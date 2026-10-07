# timeline.json とナレーション wav から、BGM・効果音・ナレーションを合わせた build/ep1_mix.wav を作る
import json, os
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, 'build')
TL = json.load(open(os.path.join(HERE, 'timeline.json')))
SR = 48000
DUR = TL['duration']
N = int(SR * DUR)
tt = np.arange(N) / SR
rng = np.random.default_rng(6)
LINE = {l['id']: l for l in TL['lines']}
SC = {s['name']: s for s in TL['scenes']}

def at(i, f=0.0):
    l = LINE[i]; return l['t0'] + (l['t1'] - l['t0'] - 0.3) * f
def at_str(i, s):
    l = LINE[i]; return at(i, l['text'].index(s) / len(l['text']))

def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)
def env(a, b, att, rel):
    e = np.zeros(N); i0, i1 = max(0, int(a * SR)), min(N, int(b * SR))
    if i1 <= i0: return e
    seg = np.ones(i1 - i0); na, nr = min(int(att * SR), len(seg)), min(int(rel * SR), len(seg))
    if na: seg[:na] = np.linspace(0, 1, na) ** 2
    if nr: seg[-nr:] *= np.linspace(1, 0, nr) ** 2
    e[i0:i1] = seg; return e
def scene_env(*names, att=1.5, rel=1.5):
    return sum(env(SC[n]['t0'] - 0.4, SC[n]['t1'] + 0.6, att, rel) for n in names)

music = np.zeros((N, 2)); sfx = np.zeros((N, 2))
def add(buf, sig, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR); n = min(len(sig), N - i0)
    if n <= 0 or i0 < 0: return
    buf[i0:i0 + n, 0] += sig[:n] * gain * np.sqrt((1 - pan) / 2) * 1.414
    buf[i0:i0 + n, 1] += sig[:n] * gain * np.sqrt((1 + pan) / 2) * 1.414
def mono(x): return np.stack([x, x], 1)

# ---------- 音楽：ゆっくり移ろう和音のパッド ----------
CHORDS = [[50, 57, 62, 65, 69], [46, 53, 58, 62, 65], [48, 55, 60, 64, 67], [45, 52, 57, 60, 64]]  # Dm Bb C Am
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
pad = np.zeros(N); CL = 9.0
for k in range(int(DUR / CL) + 2):
    ch = CHORDS[k % 4]; e = env(k * CL - 2.5, (k + 1) * CL + 2.5, 3.0, 3.0)
    idx = np.nonzero(e)[0]
    if not len(idx): continue
    seg = np.zeros(len(idx)); ts = tt[idx]
    for j, m in enumerate(ch):
        f = hz(m); a = 0.5 if j == 0 else 0.3
        seg += a * (np.sin(2 * np.pi * f * ts + j) + 0.6 * np.sin(2 * np.pi * f * 1.004 * ts + 2 * j)) * (1 + 0.25 * np.sin(2 * np.pi * (0.11 + 0.03 * j) * ts))
    pad[idx] += seg * e[idx]
pad = lp(pad, 1100) * 0.05
padL = pad * (1 + 0.15 * np.sin(2 * np.pi * 0.05 * tt)); padR = pad * (1 - 0.15 * np.sin(2 * np.pi * 0.05 * tt))
pad_amt = np.clip(scene_env('timeline', 'series', 'four', 'question', 'map', 'steppe', 'arrival', 'hunter', 'tools', 'reindeer') * 1.0 + 0.45 * scene_env('intro', 'panel', 'section', 'outro'), 0, 1)
music += np.stack([padL, padR], 1) * pad_amt[:, None]

# 洞窟の低いうなり
drone = sum(a * np.sin(2 * np.pi * f * tt + p) for f, a, p in [(41.2, 1.0, 0), (55, 0.6, 1), (82.4, 0.3, 2)]) * 0.07 + lp(rng.standard_normal(N), 260) * 0.12
cave_amt = np.clip(scene_env('intro', 'question', 'panel', 'section', 'outro'), 0, 1)
music += mono(drone * cave_amt)

# ピアノ風の単音（問い・章題・結び）
def bell(f, d=3.5):
    n = int(d * SR); t = np.arange(n) / SR
    return sum(a * np.sin(2 * np.pi * f * h * t) * np.exp(-t * dk) for h, a, dk in [(1, 0.5, 1.2), (2.0, 0.18, 2.0), (3.01, 0.08, 3.0), (4.2, 0.03, 4.5)])
for t0, m in [(at('n07', 0), 62), (at('n07', 0) + 0.6, 69), (at_str('n07', '絵'), 65), (at('n32', 0), 62), (at('n32', 0) + 0.8, 69), (at('n32', 0) + 1.6, 68)]:
    add(music, bell(hz(m + 12)), t0, 0.22, 0.2)

# ---------- 効果音 ----------
def drip(f0):
    n = int(0.5 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(f0 * np.exp(-t * 6) + f0 * 0.45) / SR) * np.exp(-t * 18) * 0.5
for name in ['intro', 'question', 'panel', 'section', 'outro']:
    s = SC[name]; t = s['t0'] + 1.3
    while t < s['t1'] - 0.5:
        add(sfx, drip(1200 + rng.random() * 500), t, 0.16, rng.random() * 1.2 - 0.6); t += 2.5 + rng.random() * 4

# たいまつのパチパチ
def fire(a, b, gain):
    e = env(a, b, 1.0, 1.0); bed = lp(rng.standard_normal(N), 900) * 0.05 * e
    cr = np.zeros(N); t = a
    while t < b:
        i = int(t * SR); k = int(SR * 0.01)
        if i + k < N: cr[i:i + k] += rng.standard_normal(k) * np.exp(-np.arange(k) / (SR * 0.002)) * (0.2 + rng.random() * 0.8)
        t += rng.exponential(1 / 14)
    return (bed + hp(cr, 1500) * 0.2 * e) * gain
for name, g in [('intro', 1.0), ('question', 0.6), ('panel', 0.8), ('outro', 0.9)]:
    sfx += mono(fire(SC[name]['t0'] - 0.3, SC[name]['t1'] + 0.5, g))

# 風（草原・地図）
wind = bp(rng.standard_normal(N), 250, 1600) * (0.6 + 0.4 * lp(np.abs(rng.standard_normal(N)), 0.3) * 6)
wind_amt = np.clip(scene_env('steppe', 'hunter', att=2.0, rel=2.0) * 1.0 + 0.35 * scene_env('map', att=2, rel=2), 0, 1)
sfx += np.stack([wind * 0.05 * wind_amt, np.roll(wind, 2400) * 0.05 * wind_amt], 1)

# 年表の線・カードの小さな音
def tick(f=900, g=1.0):
    n = int(0.25 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 30) + hp(rng.standard_normal(n), 3000) * np.exp(-t * 120) * 0.2) * g
for i in range(23):
    add(sfx, tick(700 + i * 14, 0.05), at('n03', 0.08) + (at('n03', 0.85) - at('n03', 0.08)) * i / 22, 1.0, -0.6 + i / 18)
for k in ['誰が', '何のため', 'どんな道具', 'そして']:
    add(sfx, tick(520, 0.12), at_str('n05', k) - 0.15)

# 章題：低い一撃
n = int(5 * SR); t = np.arange(n) / SR
boom = np.sin(2 * np.pi * 38 * t + 3 * np.exp(-t * 4)) * np.exp(-t * 1.4) * 0.8 + lp(rng.standard_normal(n), 2500) * np.exp(-t * 8) * 0.2
add(sfx, boom, SC['chapter']['t0'] + 0.75, 0.7)
add(music, bell(hz(62)) + bell(hz(69)) * 0.6, SC['chapter']['t0'] + 0.8, 0.35)

# 氷が広がる：ゴーッという低音と軋み
n = int(4 * SR); t = np.arange(n) / SR
rum = lp(rng.standard_normal(n), 140) * np.sin(np.pi * t / 4) ** 2 * 1.2
crk = np.zeros(n)
for c in rng.uniform(0.3, 3.5, 7):
    i = int(c * SR); k = int(0.08 * SR); crk[i:i + k] += hp(rng.standard_normal(k), 1800) * np.exp(-np.arange(k) / (SR * 0.015)) * 0.25
add(sfx, rum + crk, at('n14', 0), 0.7)
add(sfx, (rum + crk)[:int(2 * SR)] * 0.6, at('n15', 0), 0.6, 0.3)
# 海面が下がる：引いていく波
n = int(3.5 * SR); t = np.arange(n) / SR
add(sfx, bp(rng.standard_normal(n), 200, 2500) * np.sin(np.pi * t / 3.5) ** 2 * 0.25, at('n16', 0.15), 1.0, -0.3)
# 遺跡のピン
for i, d in enumerate([0, 0.6, 1.2]):
    add(sfx, tick(1320 + i * 180, 0.12), at('n18', 0.25) + d, 1.0, -0.3 + i * 0.3)
# 矢印の進行
n = int(3.5 * SR); t = np.arange(n) / SR
add(sfx, bp(rng.standard_normal(n), 800, 4000) * (t / 3.5) * np.exp(-np.maximum(t - 3.2, 0) * 20) * 0.08, at('n21', 0.35), 1.0)
# 道具：石を打つ音
for k in ['石', '骨', '毛皮']:
    n = int(0.4 * SR); t = np.arange(n) / SR
    knock = (np.sin(2 * np.pi * 1800 * t) * 0.3 + bp(rng.standard_normal(n), 1500, 6000)) * np.exp(-t * 40)
    add(sfx, knock * 0.18, at_str('n24', k) - 0.1)
# 最後の暗転前の余韻
add(music, bell(hz(57), 5.0) * 0.8, at('n33', 0.75), 0.3)

# ---------- 洞窟の響き（音楽と効果音に） ----------
irn = int(2.6 * SR); t = np.arange(irn) / SR
ir = rng.standard_normal((2, irn)) * np.exp(-t * 2.4); ir = np.array([lp(ir[0], 4000), lp(ir[1], 3800)])
amb = music + sfx
wet = np.stack([fftconvolve(amb[:, 0], ir[0])[:N], fftconvolve(amb[:, 1], ir[1])[:N]], 1)
wet *= np.max(np.abs(amb)) / (np.max(np.abs(wet)) + 1e-9)
amb = amb + wet * 0.3

# ---------- ナレーション ----------
nar = np.zeros(N)
for l in TL['lines']:
    sr, x = wavfile.read(os.path.join(B, l['file'])); x = x.astype(np.float64) / 32768
    if x.ndim > 1: x = x.mean(1)
    assert sr == SR
    i0 = int(l['t0'] * SR); n = min(len(x), N - i0); nar[i0:i0 + n] += x[:n]
nar = nar / (np.max(np.abs(nar)) + 1e-9) * 0.9
# ナレーション中は背景を下げる
act = np.zeros(N)
for l in TL['lines']: act += env(l['t0'] - 0.25, l['t1'] + 0.1, 0.2, 0.2)
act = np.clip(lp(np.clip(act, 0, 1), 3), 0, 1)
duck = 1 - 0.55 * act
amb = amb / (np.max(np.abs(amb)) + 1e-9) * 0.42 * duck[:, None]

out = amb + mono(nar)
fade = np.clip(tt / 1.0, 0, 1) * np.clip((DUR - tt) / 1.6, 0, 1)
out *= fade[:, None]
out = np.tanh(out * 1.05) * 0.95
wavfile.write(os.path.join(B, 'ep1_mix.wav'), SR, (out * 32767).astype(np.int16))
print('ok', round(DUR, 1), 's')
