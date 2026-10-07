"""AKIRA — neon city at night, the red bike, the slide. ~16s"""
import math, random, sys
from PIL import Image, ImageDraw
from engine import *

SEC = 16
RED, RED2, RED3, WHITE = (220, 30, 40), (160, 15, 25), (255, 90, 90), (235, 235, 240)
ROAD_Y = 150

def bike_img(f, head_turn=False):
    im = Image.new('RGBA', (70, 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ox, oy = 6, 32
    P = lambda x, y: (ox + x, oy + y)
    for wx in (10, 47):
        cx, cy = P(wx, 0)
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(25, 25, 30)); d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(70, 70, 80))
        a = f * 0.9; d.line([cx, cy, cx + 3 * math.cos(a), cy + 3 * math.sin(a)], fill=(150, 150, 160))
    d.polygon([P(0, -8), P(6, -15), P(18, -18), P(38, -17), P(50, -12), P(56, -6), P(52, -2), P(4, -2)], fill=RED)
    d.polygon([P(4, -4), P(52, -4), P(52, -2), P(4, -2)], fill=RED2)
    d.line([P(8, -9), P(46, -9)], fill=WHITE)                          # stripe
    d.polygon([P(40, -17), P(47, -16), P(50, -12), P(42, -12)], fill=(60, 120, 160))   # windshield
    d.rectangle([P(0, -9), P(2, -6)], fill=(255, 60, 60))                # tail light
    d.rectangle([P(54, -7), P(56, -5)], fill=(255, 250, 200))            # headlight
    # rider tucked low: red jacket, dark hair
    d.polygon([P(16, -16), P(22, -24), P(34, -23), P(38, -18), P(28, -16)], fill=(200, 25, 35))
    d.line([P(22, -24), P(32, -23)], fill=RED3)
    d.rectangle([P(34, -27) if not head_turn else P(31, -28), P(39, -22) if not head_turn else P(36, -23)], fill=(40, 30, 30))
    d.rectangle([P(38, -24), P(39, -23)] if not head_turn else [P(31, -25), P(32, -24)], fill=(230, 180, 140))
    d.line([P(36, -20), P(44, -15)], fill=(200, 25, 35))
    d.line([P(18, -16), P(14, -8)], fill=(40, 40, 60))
    return im

random.seed(11)
FAR = [(random.randint(0, 640), random.randint(30, 90), random.randint(14, 36)) for _ in range(40)]
NEAR = [(k * 46 + random.randint(-8, 8), random.randint(50, 100), random.randint(24, 40), random.choice([(255, 60, 150), (60, 230, 230), (255, 210, 60), (150, 90, 255)])) for k in range(14)]

def city(d, t, scroll, i):
    for y in range(H): d.line([0, y, W, y], fill=mix((14, 6, 30), (70, 20, 70), y / 130))
    off = -(scroll * 0.15) % 640
    for bx, bh, bw in FAR:
        for base in (off - 640, off):
            x = base + bx
            if -40 < x < W + 40:
                d.rectangle([x, 130 - bh, x + bw, 130], fill=(30, 18, 50))
                for wy in range(130 - bh + 4, 128, 6):
                    for wx in range(int(x) + 3, int(x + bw) - 2, 5):
                        if (wx * 7 + wy * 3) % 5 == 0: d.point((wx, wy), fill=(200, 170, 90))
    off = -(scroll * 0.45) % 644
    for bx, bh, bw, nc in NEAR:
        for base in (off - 644, off):
            x = base + bx
            if -50 < x < W + 50:
                d.rectangle([x, 132 - bh, x + bw, 132], fill=(16, 10, 28))
                on = (int(t * 3) + bx) % 7 != 0
                d.rectangle([x + 4, 132 - bh + 8, x + 8, 132 - bh + 28], fill=nc if on else (40, 30, 50))
                d.rectangle([x + 12, 132 - bh + 6, x + bw - 4, 132 - bh + 10], fill=nc if on else (40, 30, 50))
                for wy in range(132 - bh + 14, 130, 7):
                    for wx in range(int(x) + 12, int(x + bw) - 3, 6):
                        if (wx + wy * 5) % 4 == 0: d.rectangle([wx, wy, wx + 2, wy + 2], fill=(90, 200, 220))
    d.rectangle([0, 132, W, H], fill=(22, 18, 32))
    d.rectangle([0, 132, W, 135], fill=(80, 80, 100))
    off = -(scroll * 1.0) % 20
    for x in range(int(off) - 20, W, 20): d.rectangle([x, 133, x + 1, 135], fill=(50, 50, 70))
    off = -(scroll * 1.2) % 40
    for x in range(int(off) - 40, W, 40): d.rectangle([x, 166, x + 18, 167], fill=(200, 200, 210))
    for k, (bx, _, bw, nc) in enumerate(NEAR[:8]):        # neon reflections on wet road
        x = (bx - scroll * 0.45) % 644
        if x < W: d.line([x + 6, 140, x + 6, 175], fill=mix((22, 18, 32), nc, 0.35))

TRAIL = []
def frame(t, i):
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    # speed profile: fast until 8.5, then braking to 0 at 11.2
    def v(tt): return 340 if tt < 8.5 else 340 * max(0.0, 1 - (tt - 8.5) / 2.7) ** 1.6
    scroll = sum(v(k / FPS) for k in range(int(t * FPS))) / FPS
    city(d, t, scroll, i)
    sp = v(t)
    if t < 8.5:
        bx, by, ang = 110, ROAD_Y + int(math.sin(t * 20) * 0.6), 0
    else:
        k = clamp((t - 8.5) / 2.7)
        e = 1 - (1 - k) ** 2
        bx, by, ang = 110 + e * 90, ROAD_Y, e * 14 + math.sin(min(k, 1) * math.pi) * 4
    # gang bikes behind (headlights)
    if t < 8.5:
        for k in range(2):
            gx = 20 + k * 40 + math.sin(t * 2 + k) * 10
            d.rectangle([gx, ROAD_Y - 8, gx + 22, ROAD_Y - 2], fill=(40, 40, 50))
            d.ellipse([gx, ROAD_Y - 4, gx + 6, ROAD_Y + 2], fill=(20, 20, 20)); d.ellipse([gx + 16, ROAD_Y - 4, gx + 22, ROAD_Y + 2], fill=(20, 20, 20))
            d.polygon([(gx + 22, ROAD_Y - 6), (gx + 60, ROAD_Y - 12), (gx + 60, ROAD_Y + 2)], fill=(70, 60, 80))
    # tail-light streak
    tail_x = bx + 6; tail_y = by - 6
    if t < 8.5:
        for k in range(0, int(tail_x)):
            a = k / tail_x
            d.point((k, tail_y + int(math.sin((k + scroll) / 30) * 1)), fill=mix((40, 10, 20), (255, 40, 60), a))
            d.point((k, tail_y + 1), fill=mix((30, 10, 20), (200, 20, 40), a))
    else:
        k = clamp((t - 8.5) / 2.7)
        for x in range(0, int(tail_x)):
            a = x / max(1, tail_x)
            yy = tail_y + 2 * a * k
            d.point((x, yy), fill=mix((40, 10, 20), (255, 40, 60), a * (1 - 0.3 * clamp((t - 11.2) / 3))))
            d.point((x, yy + 1), fill=mix((30, 10, 20), (200, 20, 40), a * (1 - 0.3 * clamp((t - 11.2) / 3))))
    # speed lines
    if sp > 50:
        random.seed(i)
        for k in range(int(sp / 25)):
            y = random.randint(20, 175); x = random.randint(0, W); d.line([x, y, x + int(sp / 8), y], fill=(120, 90, 150))
    bimg = bike_img(scroll / 6, head_turn=t > 12.0)
    if ang: bimg = bimg.rotate(ang, resample=Image.NEAREST, expand=True)
    bb = bimg.getbbox()
    im.paste(bimg, (int(bx - 6 - (bimg.width - 70) // 2), int(by + 7 - bb[3])), bimg)
    d = ImageDraw.Draw(im)
    if 8.5 < t < 11.4:                           # sparks + smoke from the slide
        random.seed(i)
        for k in range(40):
            sx = bx + random.randint(-2, 14); sy = by + random.randint(2, 7)
            ln = random.randint(4, 20)
            d.line([sx, sy, sx - ln, sy - random.randint(0, 6)], fill=random.choice([(255, 220, 80), (255, 150, 40), (255, 255, 200)]))
        for k in range(14):
            sx = bx - random.randint(0, 80); sy = by - random.randint(0, 10)
            d.rectangle([sx, sy, sx + 4, sy + 3], fill=(90, 80, 100))
    if t > 11.2:                                 # settling smoke
        random.seed(5)
        for k in range(20):
            sx = bx - 20 + random.randint(-30, 50); sy = by - 6 - ((t - 11.2) * 6 + k * 3) % 30
            if (k + i // 4) % 3: d.rectangle([sx, sy, sx + 3, sy + 2], fill=(110, 100, 120))
    if 8.45 < t < 8.55: d.rectangle([0, 0, W, H], fill=(255, 255, 255))
    if t < 0.4: im = Image.blend(Image.new('RGB', (W, H)), im, clamp(t / 0.4))
    if t > 15.2: im = Image.blend(im, Image.new('RGB', (W, H)), clamp((t - 15.2) / 0.8))
    return im

def taiko(tr, t, vol=0.7, pitch=70):
    n = int(SR * 0.5); tt = np.arange(n) / SR
    f = pitch * (1 + 1.5 * np.exp(-tt * 30))
    w = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7) * vol
    w += np.random.default_rng(int(t * 100)).uniform(-1, 1, n) * np.exp(-tt * 60) * vol * 0.3
    tr.add(t, w)

def music(path):
    tr = Track(SEC); bpm = 132; b = 60 / bpm; e = b / 2
    # 0-8.5: taiko 3+3+2, gamelan-like metal, chanting voice
    bars = int(8.5 / (8 * e)) + 1
    for k in range(bars):
        t0 = k * 8 * e
        for s, v in ((0, 0.8), (3, 0.6), (6, 0.7)): 
            if t0 + s * e < 8.5: taiko(tr, t0 + s * e, v)
        if t0 + 4 * e < 8.5: tr.snare(t0 + 4 * e, 0.12, dec=30)
        for s in range(8):
            if t0 + s * e < 8.5: tr.hat(t0 + s * e, 0.04)
    gam = 'D6:.5 A5:.5 C6:.5 G5:.5 D6:.5 F5:.5 G5:.5 A5:.5 '
    tr.seq(0, bpm, (gam * 4).strip(), 'sq', 0.05, duty=0.25, gate=0.5, adsr=(0.001, 0.12, 0.05, 0.05))
    tr.seq(0, bpm, ('A4:.5 F4:.5 G4:.5 D4:.5 ' * 8).strip(), 'tri', 0.06, gate=0.5, adsr=(0.001, 0.1, 0.1, 0.05))
    chant = 'D4:3 F4:1 G4:2 F4:1 D4:1 C4:3 D4:5'
    tr.seq(1.8, bpm, chant, 'sq', 0.07, duty=0.5, vib=0.012, vibrate=5, gate=0.98, adsr=(0.15, 0.1, 0.8, 0.2))
    tr.seq(1.8, bpm, chant.replace('4:', '3:'), 'saw', 0.04, vib=0.012, vibrate=5, gate=0.98, adsr=(0.15, 0.1, 0.8, 0.2))
    tr.seq(0, bpm, ('D2:1 D2:.5 D2:.5 ' * 8).strip(), 'tri', 0.3)
    # 8.5: the slide — screech + suspended chord
    n = int(SR * 2.6); tt = np.arange(n) / SR
    scr = np.sign(np.sin(2 * np.pi * np.cumsum(1800 + 300 * np.sin(tt * 60) - tt * 300) / SR)) * 0.05 * np.clip(1 - tt / 2.6, 0, 1)
    tr.add(8.5, scr)
    for k in range(int(2.6 / 0.03)): tr.add(8.5 + k * 0.03, osc('noise', k, 0.03, 0.05 * (1 - k / 87), adsr=(0.001, 0.01, 0.6, 0.01)))
    for nt in ('D3', 'A3', 'C4', 'G4', 'A4', 'D5'): tr.add(8.5, osc('sq', freq(nt), 6.5, 0.035, duty=0.5, vib=0.006, adsr=(0.4, 0.5, 0.7, 2.0)))
    taiko(tr, 11.2, 0.9, 55); taiko(tr, 11.2 + 3 * e, 0.6, 55); taiko(tr, 12.6, 1.0, 45)
    tr.add(12.6, osc('sq', freq('D6'), 2.0, 0.04, duty=0.25, adsr=(0.001, 0.6, 0.2, 1.0)))
    tr.write(path, SEC, echo=0.35, delay=0.2)

if __name__ == '__main__':
    music('out/s5.wav')
    if 'stills' in sys.argv:
        for tt in (3, 7, 9.5, 12.5): still(frame, tt, f'out/s5_{tt}.png')
    else:
        render(frame, SEC, 'out/s5.wav', 'out/s5_akira.mp4')
