"""RAIDERS OF THE LOST ARK — the idol swap, the rumble, the boulder. ~18s"""
import math, random, sys
from PIL import Image, ImageDraw
from engine import *

SEC = 18
HAT, SKIN, JACK, SHIRT, PANTS, BOOT = (105, 68, 38), (230, 180, 135), (125, 82, 45), (215, 190, 140), (150, 125, 85), (55, 38, 25)
GOLD, GOLD2 = (250, 200, 50), (200, 140, 30)
STONE, STONE2, STONE3 = (92, 78, 62), (70, 58, 46), (50, 41, 33)

def hero(d, x, y, face=1, pose='stand', f=0, item=None):
    """x = centre, y = feet. face 1 = right, -1 = left."""
    X = lambda dx: x + dx * face
    def R(a, b, c, e, col):
        x0, x1 = sorted((X(a), X(c))); d.rectangle([x0, y + b, x1, y + e], fill=col)
    if pose == 'run':
        ph = int(f) % 4; sw = [3, 1, -3, -1][ph]
        R(-1, -9, 1, -6, PANTS); R(-1 + sw, -6, 1 + sw, -1, PANTS); R(-1 - sw, -6, 1 - sw, -1, PANTS)
        R(-1 + sw, -1, 2 + sw, 0, BOOT); R(-1 - sw, -1, 2 - sw, 0, BOOT)
        R(-3, -17, 3, -9, JACK); R(-1, -17, 1, -10, SHIRT)
        R(2, -16, 6, -14, JACK) if ph % 2 else R(-5, -16, -2, -14, JACK)
        R(-1, -21, 3, -18, SKIN); R(-4, -23, 5, -22, HAT); R(-2, -25, 3, -23, HAT)
        R(-4, -11, -3, -9, (80, 50, 30))
    elif pose == 'dive':
        R(-8, -6, 6, -3, JACK); R(-12, -6, -8, -4, PANTS); R(-14, -6, -12, -4, BOOT)
        R(6, -7, 10, -4, SKIN); R(6, -9, 11, -8, HAT); R(10, -5, 14, -4, JACK)
    else:
        R(-2, -9, -1, -1, PANTS); R(1, -9, 2, -1, PANTS); R(-2, -1, -1, 0, BOOT); R(1, -1, 3, 0, BOOT)
        R(-3, -17, 3, -9, JACK); R(-1, -17, 1, -10, SHIRT)
        reach = pose == 'reach'
        R(2, -15, 8 if reach else 4, -14, JACK); R(8 if reach else 4, -15, 9 if reach else 5, -13, SKIN)
        R(-1, -21, 3, -18, SKIN); d.point((X(2), y - 20), fill=(30, 20, 10))
        R(-4, -23, 5, -22, HAT); R(-2, -25, 3, -23, HAT)
        R(-4, -11, -3, -8, (80, 50, 30)); R(-5, -10, -4, -9, (80, 50, 30))     # coiled whip
        if item == 'idol': R(8, -19, 10, -14, GOLD)
        if item == 'bag': R(8, -16, 11, -13, (190, 170, 120))

def bricks(d, scroll, y0, y1):
    d.rectangle([0, y0, W, y1], fill=STONE)
    off = -scroll % 32
    for row, y in enumerate(range(y0, y1, 8)):
        d.line([0, y, W, y], fill=STONE3)
        sh = 16 if row % 2 else 0
        for x in range(int(off) - 32 + sh, W + 32, 32): d.line([x, y, x, y + 7], fill=STONE3)
        for x in range(int(off) - 32 + sh, W + 32, 32): d.line([x + 1, y + 1, x + 30, y + 1], fill=(108, 92, 74))

def chamber(d, t, i):
    shake = 0
    if t > 4.0: shake = random.Random(i).randint(-2, 2)
    bricks(d, shake, 0, 140)
    d.rectangle([0, 140, W, H], fill=STONE2)
    for x in range(0, W, 12): d.line([x + shake, 140, x - 6 + shake, H], fill=STONE3)
    for k, lx in enumerate((60, 110, 230)):      # light shafts
        for y in range(0, 140, 2):
            for w in range(0, 14, 3):
                if (y + w + k) % 4 == 0: d.point((lx + y // 4 + w + shake, y), fill=(170, 150, 110))
    px = 110 + shake; sink = 2 if t > 3.4 else 0
    d.rectangle([px - 12, 112 + sink, px + 12, 140], fill=(120, 105, 85)); d.rectangle([px - 14, 108 + sink, px + 14, 113 + sink], fill=(140, 122, 98))
    if t < 2.9:                                  # the idol, glowing
        g = 3 + int(math.sin(t * 6) * 1.5)
        d.ellipse([px - 7 - g, 92 - g, px + 7 + g, 108 + g], fill=(150, 110, 50))
        d.rectangle([px - 4, 96, px + 4, 108], fill=GOLD); d.ellipse([px - 4, 90, px + 4, 98], fill=GOLD)
        d.rectangle([px - 4, 102, px + 4, 103], fill=GOLD2); d.point((px - 2, 94), fill=GOLD2); d.point((px + 1, 94), fill=GOLD2)
    else:
        d.rectangle([px - 4, 101 + sink, px + 4, 108 + sink], fill=(190, 170, 120))
    if t < 2.9: hero(d, 132 + shake, 140, -1, 'reach' if t > 1.6 else 'stand', item='bag')
    elif t < 4.4: hero(d, 132 + shake, 140, -1, 'stand', item='idol')
    else:
        hx = 132 + (t - 4.9) * 150 if t > 4.9 else 132
        if t < 4.9: hero(d, 132 + shake, 140, 1, 'stand', item='idol')
        else: hero(d, hx + shake, 140, 1, 'run', f=t * 12)
    if 4.1 < t < 5.4:                            # "!"
        bx, by = 126, 92
        d.rectangle([bx, by, bx + 9, by + 13], fill=(250, 250, 250)); d.rectangle([bx + 4, by + 2, bx + 5, by + 8], fill=(220, 30, 30))
        d.rectangle([bx + 4, by + 10, bx + 5, by + 11], fill=(220, 30, 30))
    if t > 4.0:                                  # falling dust
        random.seed(i // 2)
        for k in range(int((t - 4) * 30)):
            d.point((random.randrange(W), random.randrange(140)), fill=(160, 140, 110))

def boulder(d, cx, cy, r, ang):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(118, 100, 80))
    d.ellipse([cx - r + 4, cy - r + 3, cx + r - 10, cy + r - 12], fill=(136, 118, 94))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(60, 50, 40))
    for k in range(5):                           # rolling cracks
        a = ang + k * 1.256
        x1, y1 = cx + math.cos(a) * r * 0.25, cy + math.sin(a) * r * 0.25
        x2, y2 = cx + math.cos(a + 0.3) * r * 0.85, cy + math.sin(a + 0.3) * r * 0.85
        d.line([x1, y1, x2, y2], fill=(80, 66, 52))

def corridor(d, t, i):
    lt = t - 6.5
    stop = 13.5 - 6.5
    scroll = 160 * min(lt, stop)
    shake = random.Random(i).randint(-1, 1)
    bricks(d, scroll, 0, 132)
    for k in range(-1, 4):                       # torches
        tx = int(-scroll % 140 + k * 140)
        d.rectangle([tx, 60, tx + 2, 72], fill=(90, 60, 30))
        fl = (255, 200, 60) if (i // 3 + k) % 2 else (255, 140, 40)
        d.polygon([(tx - 2, 60), (tx + 1, 50 + (i % 3)), (tx + 4, 60)], fill=fl)
    d.rectangle([0, 132, W, H], fill=STONE2)
    for x in range(int(-scroll % 16) - 16, W, 16): d.line([x, 132, x - 4, H], fill=STONE3)
    ex = int(W + 20 - max(0, 160 * min(lt, stop) - 160 * (stop - 0.5)))     # exit doorway slides in
    if ex < W + 20:
        d.rectangle([ex, 50, ex + 60, 140], fill=(150, 200, 110)); d.rectangle([ex, 50, ex + 60, 58], fill=(230, 240, 200))
        for k in range(8): d.polygon([(ex + k * 8, 140), (ex + 4 + k * 8, 120 + (k * 7) % 12), (ex + 8 + k * 8, 140)], fill=(70, 140, 60))
        d.rectangle([ex - 6, 44, ex, 140], fill=STONE3)
    # hero
    if lt < stop: hero(d, 210 + shake, 150, 1, 'run', f=t * 14, item=None)
    elif lt < stop + 1.0:
        k = (lt - stop) / 1.0
        hx = 210 + k * 160; hy = 150 - math.sin(k * math.pi) * 14
        hero(d, hx, hy, 1, 'dive' if k > 0.25 else 'run', f=t * 14)
    # boulder
    if lt < stop: bx = lerp(-60, 150, (lt / stop) ** 0.8)
    else: bx = min(lerp(150, ex + 30, (lt - stop) / 1.4), ex + 30)
    rolled = bx + scroll
    boulder(d, int(bx) + shake, 98, 42, rolled / 42)
    random.seed(i)
    for k in range(18):                          # dust kicked up
        dx = bx - 40 - random.randint(0, 30); dy = 132 + random.randint(0, 20)
        d.rectangle([dx, dy, dx + 2, dy + 2], fill=(140, 120, 95))
    if lt > stop + 1.4:                          # impact dust cloud
        k = clamp((lt - stop - 1.4) / 2.0)
        random.seed(99)
        for n in range(60):
            a = random.uniform(-math.pi, 0); r = random.uniform(10, 60) * (0.3 + k)
            if random.random() > k * 0.9:
                d.rectangle([ex + math.cos(a) * r - 10, 132 + math.sin(a) * r * 0.6, ex + math.cos(a) * r - 7, 135 + math.sin(a) * r * 0.6], fill=(170, 150, 120))

def frame(t, i):
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    if t < 6.3: chamber(d, t, i)
    elif t < 6.5: pass
    else: corridor(d, t, i)
    if t < 0.4: im = Image.blend(Image.new('RGB', (W, H)), im, clamp(t / 0.4))
    if t > 17.3: im = Image.blend(im, Image.new('RGB', (W, H)), clamp((t - 17.3) / 0.7))
    return im

def music(path):
    tr = Track(SEC)
    # 0-4: mysterious temple — low drone + phrygian bells
    tr.add(0, osc('sq', freq('D2'), 4.0, 0.06, duty=0.125, adsr=(0.8, 0.2, 0.9, 0.3)))
    tr.add(0, osc('tri', freq('D3'), 4.0, 0.12, adsr=(0.8, 0.2, 0.9, 0.3)))
    tr.seq(0.3, 90, 'D5:1 Eb5:1 F5:.5 Eb5:1.5 -:.6', 'tri', 0.10, adsr=(0.002, 0.3, 0.2, 0.3))
    tr.add(2.95, osc('tri', freq('A5'), 0.4, 0.08, adsr=(0.002, 0.2, 0.1, 0.2)))    # the swap...
    tr.add(3.45, osc('noise', 3, 0.05, 0.25, adsr=(0.001, 0.02, 0.2, 0.02)))        # click
    tr.boom(4.0, 0.6, 2.4)
    for nt in ('D2', 'Eb2', 'A2'): tr.add(4.0, osc('saw', freq(nt), 2.4, 0.06, adsr=(0.01, 0.5, 0.6, 0.5)))
    # 6.5-15: chase march (original melody), driving eighths
    bpm = 160; b = 60 / bpm; t0 = 6.5
    mel = ('A4:.75 D5:.25 F#5:1.5 E5:.5 D5:.75 E5:.25 A4:2 '
           'B4:.75 C#5:.25 D5:1 G5:1 F#5:.75 E5:.25 D5:1 E5:2 '
           'A4:.75 D5:.25 F#5:1.5 A5:.5 B5:.75 A5:.25 G5:1 F#5:1 '
           'E5:.75 F#5:.25 G5:1 E5:1 A5:4')
    tr.seq(t0, bpm, mel, 'sq', 0.12, duty=0.25, vib=0.004)
    bass = ' '.join(['D3:.5 A2:.5'] * 8 + ['G2:.5 D3:.5'] * 4 + ['A2:.5 E3:.5'] * 4 + ['D3:.5 A2:.5'] * 4 + ['G2:.5 D3:.5'] * 4 + ['A2:.5 E3:.5'] * 6)
    tr.seq(t0, bpm, bass, 'tri', 0.32)
    nb = int((15.0 - t0) / b)
    for k in range(nb):
        tt = t0 + k * b
        tr.snare(tt + b * 0.75, 0.08, dec=45); tr.hat(tt + b / 2)
        if k % 2 == 0: tr.kick(tt, 0.4)
        else: tr.snare(tt, 0.2)
    for k in range(int(8.5 / 0.05)):             # the boulder's rumble
        tr.add(t0 + k * 0.05, osc('noise', k, 0.05, 0.03 + 0.03 * k / 170, adsr=(0.01, 0.01, 1, 0.01)) * 0.6)
    # 15: impact + resolving chord
    tr.boom(15.0, 0.8, 2.5)
    for nt in ('D3', 'A3', 'D4', 'F#4', 'A4', 'D5'): tr.add(15.0, osc('sq', freq(nt), 2.8, 0.045, duty=0.25, vib=0.004, adsr=(0.01, 0.3, 0.7, 1.2)))
    tr.add(15.0, osc('tri', freq('D2'), 2.8, 0.4, adsr=(0.005, 0.3, 0.6, 1.2)))
    tr.write(path, SEC)

if __name__ == '__main__':
    music('out/s4.wav')
    if 'stills' in sys.argv:
        for tt in (1, 2.0, 4.5, 9, 13.9, 16): still(frame, tt, f'out/s4_{tt}.png')
    else:
        render(frame, SEC, 'out/s4.wav', 'out/s4_raiders.mp4')
