import json, numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 48000
DUR = 30.0
N = int(SR * DUR)
rng = np.random.default_rng(3)
L = np.zeros(N); R = np.zeros(N)
tt = np.arange(N) / SR

def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f, order=2):
    return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, order=2):
    return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)
def env(a, b, attack, release):
    e = np.zeros(N)
    i0, i1 = int(a * SR), int(b * SR)
    seg = np.ones(i1 - i0)
    na, nr = int(attack * SR), int(release * SR)
    if na: seg[:na] = np.linspace(0, 1, na) ** 2
    if nr: seg[-nr:] *= np.linspace(1, 0, nr) ** 2
    e[i0:i1] = seg
    return e
def add(sig, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR); n = min(len(sig), N - i0)
    if n <= 0: return
    L[i0:i0 + n] += sig[:n] * gain * np.sqrt((1 - pan) / 2) * 1.414
    R[i0:i0 + n] += sig[:n] * gain * np.sqrt((1 + pan) / 2) * 1.414

# --- drips
def drip(f0=1400):
    n = int(0.5 * SR); t = np.arange(n) / SR
    f = f0 * np.exp(-t * 6) + f0 * 0.45
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 18) * 0.5
for t0, f0, p in [(0.5, 1500, -0.4), (2.3, 1250, 0.5), (7.8, 1600, -0.6), (12.4, 1350, 0.3), (26.0, 1450, 0.6)]:
    add(drip(f0), t0, 0.35, p)

# --- cave drone (whole piece, swells)
drone = np.zeros(N)
for f, a in [(41.2, 1.0), (55, 0.7), (82.4, 0.35), (110, 0.15)]:
    drone += a * np.sin(2 * np.pi * f * tt + rng.random() * 6) * (1 + 0.25 * np.sin(2 * np.pi * 0.07 * tt * f / 41))
air = lp(rng.standard_normal(N), 300) * 0.6
drone = drone * 0.12 + air * 0.25
dEnv = env(0, 21.35, 3.0, 0.02) * (0.5 + 0.5 * np.clip((tt - 4) / 2, 0, 1))
tension = np.clip((tt - 16) / 5, 0, 1) * (tt < 21.35)
tens_sig = bp(rng.standard_normal(N), 120, 600) * 0.08 * tension ** 2
rise = np.sin(2 * np.pi * np.cumsum(110 + 220 * tension ** 2) / SR) * 0.05 * tension ** 1.5
add(drone * dEnv + tens_sig + rise, 0, 1.0)

# --- torch ignition
n = int(1.4 * SR); t = np.arange(n) / SR
w = lp(rng.standard_normal(n), 2500) * (1 - np.exp(-t * 30)) * np.exp(-t * 2.8)
add(w * 0.55, 3.85, 1.0, -0.2)
thump = np.sin(2 * np.pi * 70 * t * np.exp(-t * 2)) * np.exp(-t * 7)
add(thump * 0.45, 3.9)

# --- fire bed + crackles (4 -> 21.3)
fe = env(4.0, 21.3, 0.6, 0.05)
bed = lp(rng.standard_normal(N), 900) * 0.10 + bp(rng.standard_normal(N), 1500, 5000) * 0.015
add(bed * fe * (1 + 0.3 * np.sin(2 * np.pi * 0.8 * tt)), 0)
cr = np.zeros(N)
t = 4.2
while t < 21.2:
    i = int(t * SR); k = int(SR * 0.012)
    c = rng.standard_normal(k) * np.exp(-np.arange(k) / (SR * 0.0025)) * (0.2 + rng.random() * 0.8)
    cr[i:i + k] += c
    t += rng.exponential(1 / 18)
cr = hp(cr, 1200) * 0.35
add(cr, 0, 1.0, 0.1)

# --- leg count ticks
for i in range(8):
    t0 = 13.5 + i * 0.24
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 620 * (1.06 ** i)
    s = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 22)
    s += hp(rng.standard_normal(n), 2000) * np.exp(-t * 200) * 0.3
    add(s * 0.28, t0, 1.0, -0.5 + i / 7)

# --- galloping hooves on toggles
TOG = json.load(open('toggles.json'))
for j, t0 in enumerate(TOG):
    n = int(0.3 * SR); t = np.arange(n) / SR
    g = 0.35 + 0.65 * (j / len(TOG))
    s = np.sin(2 * np.pi * (75 + 30 * np.exp(-t * 40)) * t) * np.exp(-t * 16)
    s += lp(rng.standard_normal(n), 1800) * np.exp(-t * 45) * 0.5
    add(s * 0.55 * g, t0, 1.0, (-0.25 if j % 2 else 0.25))
# heartbeat-like swell under flicker
# --- riser into flare
n = int(1.0 * SR); t = np.arange(n) / SR
rs = bp(rng.standard_normal(n), 400, 6000) * (t / 1.0) ** 3
add(rs * 0.35, 20.35)
# flare impact
n = int(3.0 * SR); t = np.arange(n) / SR
imp = np.sin(2 * np.pi * 48 * t * np.exp(-t * 0.6)) * np.exp(-t * 2.2) * 0.8 + lp(rng.standard_normal(n), 3000) * np.exp(-t * 9) * 0.35
add(imp, 21.33, 0.8)

# --- spray (blow pipe) pulses
for k, t0 in enumerate([22.0, 22.42, 22.82, 23.25, 23.65]):
    n = int(0.38 * SR); t = np.arange(n) / SR
    e = np.sin(np.pi * t / 0.38) ** 1.5
    s = bp(rng.standard_normal(n), 2500, 9000) * e * 0.22 + lp(rng.standard_normal(n), 500) * e * 0.08
    add(s, t0, 1.0, -0.15)

# --- hand lift whoosh
n = int(0.9 * SR); t = np.arange(n) / SR
add(bp(rng.standard_normal(n), 300, 2500) * np.sin(np.pi * t / 0.9) ** 2 * 0.12, 24.0)

# --- title hit + pad
n = int(5.5 * SR); t = np.arange(n) / SR
boom = np.sin(2 * np.pi * 36 * t + 3 * np.exp(-t * 4)) * np.exp(-t * 1.3) * 0.9
bell = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in [(220, 0.25, 0.9), (330.2, 0.15, 1.1), (440.5, 0.12, 1.4), (593, 0.08, 1.8), (881, 0.05, 2.4)])
add(boom, 25.35, 0.9)
add(bell, 25.35, 0.55, 0.0)
pad = np.zeros(N)
for f in [55, 110, 164.8, 220, 261.6, 329.6]:
    pad += np.sin(2 * np.pi * f * tt + rng.random() * 6) * (1 + 0.003 * np.sin(2 * np.pi * 0.3 * tt))
    pad += 0.5 * np.sin(2 * np.pi * f * 1.003 * tt)
pad = lp(pad, 1400) * 0.035 * env(24.6, 30.0, 1.8, 1.4)
add(pad, 0)
# low title-room drone
add(lp(rng.standard_normal(N), 200) * 0.18 * env(21.7, 30, 1.0, 1.5), 0)

# --- cave reverb
irn = int(3.2 * SR); t = np.arange(irn) / SR
ir = rng.standard_normal((2, irn)) * np.exp(-t * 2.1)
ir = np.array([lp(ir[0], 4000), lp(ir[1], 3800)])
ir[:, :int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
wetL = fftconvolve(L, ir[0])[:N]; wetR = fftconvolve(R, ir[1])[:N]
wetL /= np.max(np.abs(wetL)) + 1e-9; wetR /= np.max(np.abs(wetR)) + 1e-9
peak = max(np.max(np.abs(L)), np.max(np.abs(R)))
outL = L / peak + wetL * 0.32
outR = R / peak + wetR * 0.32
fade = np.clip((DUR - tt) / 1.0, 0, 1)
out = np.stack([outL, outR], 1) * fade[:, None]
out = np.tanh(out * 1.1) * 0.89
wavfile.write('audio.wav', SR, (out * 32767).astype(np.int16))
print('ok', out.shape)
