"""8bit scene engine: pixel canvas -> 1080p mp4, plus a tiny chiptune synth."""
import math, subprocess, wave, random
import numpy as np
from PIL import Image, ImageDraw

W, H, FPS, SR = 320, 180, 24, 44100

# ---------------------------------------------------------------- video
def sprite(d, x, y, rows, pal, flip=False):
    """Draw ASCII-art sprite. '.' = transparent."""
    for j, row in enumerate(rows):
        if flip: row = row[::-1]
        for i, ch in enumerate(row):
            if ch != '.' and ch in pal:
                d.point((x + i, y + j), fill=pal[ch])

def lerp(a, b, t): return a + (b - a) * t
def clamp(v, a=0.0, b=1.0): return max(a, min(b, v))
def mix(c1, c2, t): return tuple(int(lerp(a, b, clamp(t))) for a, b in zip(c1, c2))

def render(frame_fn, seconds, wav_path, out_path):
    n = int(seconds * FPS)
    p = subprocess.Popen(
        ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
         '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav_path,
         '-vf', 'scale=1920:1080:flags=neighbor', '-c:v', 'libx264', '-crf', '18',
         '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', out_path],
        stdin=subprocess.PIPE)
    for i in range(n):
        im = frame_fn(i / FPS, i)
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait()

def still(frame_fn, t, path):
    frame_fn(t, int(t * FPS)).resize((1280, 720), Image.NEAREST).save(path)

# ---------------------------------------------------------------- audio
NOTES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
def freq(name):
    if name in ('-', 'r', None): return 0
    n = NOTES[name[0]]; k = 1
    if len(name) > 2 or name[1] in '#b':
        n += 1 if name[1] == '#' else -1; k = 2
    octv = int(name[k:])
    return 440.0 * 2 ** ((n + 12 * (octv + 1) - 69) / 12)

def env(n, a=0.005, d=0.05, s=0.7, r=0.05):
    t = np.arange(n) / SR; dur = n / SR
    e = np.where(t < a, t / max(a, 1e-6), np.where(t < a + d, 1 - (1 - s) * (t - a) / max(d, 1e-6), s))
    rel = np.clip((dur - t) / max(r, 1e-6), 0, 1)
    return e * rel

def osc(kind, f, dur, vol=0.2, duty=0.5, vib=0.0, vibrate=5.5, adsr=None, slide=0.0):
    n = int(SR * dur); t = np.arange(n) / SR
    if f == 0 and kind != 'noise': return np.zeros(n)
    fr = f * (1 + vib * np.sin(2 * np.pi * vibrate * t)) * (1 + slide * t / max(dur, 1e-6))
    ph = np.cumsum(fr) / SR % 1.0
    if kind == 'sq':    w = np.where(ph < duty, 1.0, -1.0)
    elif kind == 'tri': w = 4 * np.abs(ph - 0.5) - 1
    elif kind == 'saw': w = 2 * ph - 1
    elif kind == 'noise':
        rng = np.random.default_rng(int(f) + n); w = rng.uniform(-1, 1, n)
    else: raise ValueError(kind)
    return w * vol * env(n, *(adsr or (0.005, 0.05, 0.7, 0.05)))

class Track:
    def __init__(self, seconds): self.buf = np.zeros(int(SR * seconds) + SR)
    def add(self, t, w):
        i = int(t * SR); j = min(len(self.buf), i + len(w))
        if i < len(self.buf): self.buf[i:j] += w[:j - i]
    def seq(self, start, bpm, pattern, kind='sq', vol=0.15, gate=0.9, **kw):
        """pattern: 'C5:1 E5:.5 -:.5' (beats). returns end time."""
        beat = 60.0 / bpm; t = start
        for tok in pattern.split():
            nm, b = tok.split(':'); b = float(b)
            for sub in nm.split('+'):            # chords: C4+E4+G4
                if sub not in '-r':
                    self.add(t, osc(kind, freq(sub), b * beat * gate, vol, **kw))
            t += b * beat
        return t
    def kick(self, t, vol=0.5):
        n = int(SR * 0.18); tt = np.arange(n) / SR
        f = 120 * np.exp(-tt * 25) + 40
        self.add(t, np.sin(2 * np.pi * np.cumsum(f) / SR) * vol * np.exp(-tt * 18))
    def snare(self, t, vol=0.25, dec=22):
        n = int(SR * 0.2); tt = np.arange(n) / SR
        self.add(t, np.random.default_rng(int(t * 999)).uniform(-1, 1, n) * vol * np.exp(-tt * dec))
    def hat(self, t, vol=0.06):
        n = int(SR * 0.04); tt = np.arange(n) / SR
        w = np.random.default_rng(int(t * 777)).uniform(-1, 1, n)
        self.add(t, np.diff(w, prepend=0) * vol * np.exp(-tt * 80))
    def boom(self, t, vol=0.6, dur=1.5):
        n = int(SR * dur); tt = np.arange(n) / SR
        w = np.random.default_rng(int(t * 31)).uniform(-1, 1, n)
        w = np.convolve(w, np.ones(60) / 60, mode='same')
        self.add(t, w * vol * 6 * np.exp(-tt * 3))
    def write(self, path, seconds, echo=0.25, delay=0.14):
        x = self.buf[:int(SR * seconds)].copy()
        d = int(delay * SR)
        for k in range(1, 4):
            x[d * k:] += self.buf[:len(x) - d * k] * (echo ** k)
        fade = int(0.4 * SR); x[-fade:] *= np.linspace(1, 0, fade)
        x = x / max(1e-6, np.max(np.abs(x))) * 0.85
        with wave.open(path, 'w') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((x * 32767).astype(np.int16).tobytes())
