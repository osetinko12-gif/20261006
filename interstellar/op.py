"""Opening: starfield -> teal/pink swirl with the Endurance ring -> pixel title."""
import numpy as np
from common import *

FONT5 = {
 'I': ['111', '010', '010', '010', '010', '010', '111'],
 'N': ['1001', '1101', '1101', '1011', '1011', '1001', '1001'],
 'T': ['11111', '00100', '00100', '00100', '00100', '00100', '00100'],
 'E': ['1111', '1000', '1000', '1110', '1000', '1000', '1111'],
 'R': ['1110', '1001', '1001', '1110', '1010', '1001', '1001'],
 'S': ['0111', '1000', '1000', '0110', '0001', '0001', '1110'],
 'L': ['1000', '1000', '1000', '1000', '1000', '1000', '1111'],
 'A': ['0110', '1001', '1001', '1111', '1001', '1001', '1001'],
 ' ': ['00', '00', '00', '00', '00', '00', '00'],
}
def text(d, s, cx, y, sc=2, col=(255, 255, 255), gap=2):
    widths = [len(FONT5[ch][0]) for ch in s]
    total = sum(w * sc + gap * sc for w in widths) - gap * sc
    x = cx - total // 2
    for ch, w in zip(s, widths):
        for j, row in enumerate(FONT5[ch]):
            for i, b in enumerate(row):
                if b == '1': R(d, x + i * sc, y + j * sc, x + i * sc + sc - 1, y + j * sc + sc - 1, col)
        x += w * sc + gap * sc

YY, XX = np.mgrid[0:H, 0:W]
def swirl(t, cx=240, cy=96, k=1.0):
    dx, dy = (XX - cx).astype(float), (YY - cy).astype(float) * 1.25
    r = np.hypot(dx, dy) + 1e-3; a = np.arctan2(dy, dx)
    band = np.sin(a * 2 + 18.0 / np.sqrt(r) * 6 - t * 0.6 + r * 0.02)
    teal, pink = np.array([60, 200, 210]), np.array([230, 90, 130])
    m = ((band + 1) / 2)[..., None]
    col = teal * m + pink * (1 - m)
    bright = np.clip(1.4 - r / 170, 0, 1) ** 1.3 * np.clip(r / 26, 0, 1) * k
    streak = (np.sin(a * 40 + 30 / np.sqrt(r) * 8 - t) > 0.6) * 0.25
    img = col * np.clip(bright + streak * bright, 0, 1.2)[..., None]
    img = (img // 24) * 24                       # posterise -> pixel-art banding
    return np.clip(img, 0, 255).astype(np.uint8)

def op(t):
    base = Image.new('RGB', (W, H)); d = ImageDraw.Draw(base); stars(d, 99, 220, tw=int(t * 3))
    k = clamp((t - 1.5) / 3)
    if k > 0:
        sw = Image.fromarray(swirl(t, k=k))
        from PIL import ImageChops
        base = ImageChops.add(base, sw)
    d = ImageDraw.Draw(base)
    endurance(d, 250 - 2 * t, 96 + 2 * math.sin(t * 0.7), 34, ang=t * 0.25, tilt=0.6)
    if t > 7:
        a = clamp((t - 7) / 1.5)
        R(d, 0, 176, W, 204, mix((0, 0, 0), (0, 0, 0), a)) if False else None
        text(d, 'INTERSTELLAR', 192, 178, sc=3, col=mix((20, 20, 30), (255, 255, 255), a), gap=2)
    return fade(base, t, 0, 14, 0.8)

SCENES = [('オープニング', op, 9)]
