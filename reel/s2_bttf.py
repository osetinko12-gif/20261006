"""BACK TO THE FUTURE — night parking lot, the car hits 88, fire trails. ~18s"""
import math, random, sys
from PIL import Image, ImageDraw
from engine import *

SEC = 18
DIG = {'0': ['111', '101', '101', '101', '111'], '1': ['010', '110', '010', '010', '111'],
       '2': ['111', '001', '111', '100', '111'], '3': ['111', '001', '111', '001', '111'],
       '4': ['101', '101', '111', '001', '001'], '5': ['111', '100', '111', '001', '111'],
       '6': ['111', '100', '111', '101', '111'], '7': ['111', '001', '010', '010', '010'],
       '8': ['111', '101', '111', '101', '111'], '9': ['111', '101', '111', '001', '111']}
def digits(d, x, y, s, col, sc=2):
    for k, ch in enumerate(s):
        for j, row in enumerate(DIG[ch]):
            for i, b in enumerate(row):
                if b == '1': d.rectangle([x + k * 4 * sc + i * sc, y + j * sc, x + k * 4 * sc + i * sc + sc - 1, y + j * sc + sc - 1], fill=col)

ROAD_Y = 142
def speed_at(t):            # mph
    if t < 4: return 0
    return min(88, 88 * ((t - 4) / 9) ** 1.4)
def dist_at(t):             # integrated scroll (px)
    s, x = 0.0, 0.0
    for k in range(int(t * 48)): x += speed_at(k / 48) * 0.09 / 48 * 48 / 48; s += 0
    return x * 48 / 48

CS = 1.7
def car(d, x, y, glow=0.0, t=0.0):
    """DeLorean facing right. (x, y) = rear-bottom corner."""
    STEEL, STEEL2, DARK = (190, 195, 205), (140, 145, 158), (40, 40, 48)
    P = lambda dx, dy: (x + (48 - dx) * CS, y + dy * CS)
    R = lambda x0, y0, x1, y1, c: d.rectangle([min(P(x0, y0)[0], P(x1, y1)[0]), P(x0, y0)[1], max(P(x0, y0)[0], P(x1, y1)[0]), P(x1, y1)[1]], fill=c)
    d.polygon([P(0, -9), P(6, -12), P(20, -18), P(30, -18), P(40, -12), P(48, -11), P(48, -4), P(0, -4)], fill=STEEL)
    d.line([P(6, -12), P(20, -18), P(30, -18), P(40, -12)], fill=(235, 236, 242))
    d.polygon([P(21, -16), P(29, -16), P(36, -12), P(17, -12)], fill=(40, 60, 95))
    d.line([P(29, -16), P(29, -12)], fill=STEEL)
    for k in range(4): d.line([P(33 + k * 2, -17), P(33 + k * 2, -13)], fill=STEEL2)
    R(0, -6, 48, -4, DARK)
    R(44, -10, 50, -7, (160, 160, 170)); R(46, -14, 51, -10, (120, 120, 130))
    d.point(P(48, -15), fill=(255, 200, 80))
    R(0, -9, 2, -7, (255, 250, 210)); R(47, -9, 48, -7, (230, 40, 40))
    if glow == 0:
        hx, hy = P(0, -8); d.polygon([(hx, hy), (hx + 46, hy - 5), (hx + 46, hy + 7)], fill=(120, 112, 78)); d.polygon([(hx, hy), (hx + 30, hy - 2), (hx + 30, hy + 4)], fill=(170, 160, 105))
    for wx in (9, 38):
        cx, cy = P(wx, -4); r = 5 * CS
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(20, 20, 24)); d.ellipse([cx - 2 * CS, cy - 2 * CS, cx + 2 * CS, cy + 2 * CS], fill=STEEL2)
        a = t * 30; d.rectangle([cx + 3.4 * math.cos(a) * CS - 1, cy + 3.4 * math.sin(a) * CS - 1, cx + 3.4 * math.cos(a) * CS, cy + 3.4 * math.sin(a) * CS], fill=(200, 200, 210))
    if glow > 0:
        random.seed(int(t * 24))
        for k in range(int(4 + glow * 30)):
            sx = x + random.randint(-10, int(52 * CS)); sy = y + random.randint(int(-30 * CS), 4)
            pts = [(sx, sy)]
            for _ in range(3): sx += random.randint(-5, 5); sy += random.randint(-5, 5); pts.append((sx, sy))
            d.line(pts, fill=random.choice([(120, 200, 255), (200, 240, 255), (80, 140, 255)]))

def lot(d, t, scroll):
    for y in range(110): d.line([0, y, W, y], fill=mix((8, 10, 30), (30, 30, 70), y / 110))
    random.seed(4)
    for k in range(50):
        sx, sy = random.randrange(W), random.randrange(90)
        if (k + int(t * 3)) % 9: d.point((sx, sy), fill=(200, 200, 230))
    off = -(scroll * 0.15) % 400                 # distant mall
    for bx in (off - 400, off):
        d.rectangle([bx + 40, 72, bx + 260, 110], fill=(22, 22, 40))
        for k in range(10): d.rectangle([bx + 50 + k * 20, 86, bx + 58 + k * 20, 92], fill=(70, 70, 40))
        d.rectangle([bx + 120, 60, bx + 190, 72], fill=(30, 30, 50)); d.rectangle([bx + 124, 63, bx + 186, 69], fill=(230, 90, 60))
        for k in range(3): d.polygon([(bx + 132 + k * 18, 69), (bx + 138 + k * 18, 63), (bx + 144 + k * 18, 69)], fill=(40, 120, 60))
    d.rectangle([0, 110, W, H], fill=(48, 48, 56))
    d.rectangle([0, 110, W, 112], fill=(70, 70, 80))
    off = -(scroll) % 40
    for k in range(-1, 10):                      # parking lines
        x = off + k * 40; d.polygon([(x, 116), (x + 3, 116), (x - 8, 132), (x - 11, 132)], fill=(220, 200, 90))
    off = -(scroll * 1.0) % 120
    for k in range(-1, 4):                       # lamp posts with pools of light
        x = off + k * 120
        d.ellipse([x - 26, 118, x + 28, 134], fill=(68, 66, 66))
        d.ellipse([x - 16, 121, x + 18, 131], fill=(84, 80, 74))
        d.rectangle([x, 52, x + 1, 126], fill=(90, 90, 100))
        d.rectangle([x - 5, 49, x + 6, 52], fill=(110, 110, 120)); d.rectangle([x - 4, 52, x + 5, 53], fill=(255, 240, 180))
    off = -(scroll * 1.0) % 24
    for k in range(-1, 15): d.rectangle([off + k * 24, 158, off + k * 24 + 12, 159], fill=(200, 200, 200))

def frame(t, i):
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    # numeric integral of speed for scroll
    scroll = 0.0
    for k in range(int(min(t, 13.0) * 24)): scroll += speed_at(k / 24) * 0.11
    sp = speed_at(t)
    if t < 13.0:
        shake = int(random.Random(i).randint(-1, 1) * clamp((t - 10) / 3)) if t > 10 else 0
        lot(d, t, scroll)
        cx = int(lerp(30, 110, clamp((t - 4) / 5)))
        car(d, cx, ROAD_Y + shake, glow=clamp((t - 8.5) / 4.5), t=scroll / 30)
        if 0 < sp < 30:
            for k in range(3): d.rectangle([cx - 4 - k * 3, ROAD_Y - 10 - k, cx - 2 - k * 3, ROAD_Y - 8 - k], fill=(120, 120, 130))
        if t > 6:                                # speed lines
            random.seed(i)
            for k in range(int(sp / 6)):
                y = random.randint(100, 170); x = random.randint(0, W); d.line([x, y, x + int(sp / 3), y], fill=(150, 150, 170))
    else:
        lot(d, 13.0, scroll)
        cx = 120
        if t < 13.25:
            d.rectangle([0, 0, W, H], fill=(255, 255, 255)) if t < 13.12 else None
            d.ellipse([cx - 20, ROAD_Y - 50, cx + 100, ROAD_Y + 20], fill=(200, 230, 255))
        # twin fire trails
        random.seed(i)
        for ty in (ROAD_Y - 2, ROAD_Y + 6):
            for x in range(-4, int(cx + 48 * CS), 3):
                fh = random.randint(2, 7) * (0.6 + 0.4 * clamp(1 - (t - 13) / 6))
                col = random.choice([(255, 220, 60), (255, 150, 30), (250, 90, 20)])
                d.polygon([(x, ty), (x + 3, ty), (x + 1, ty - fh)], fill=col)
        for k in range(14):                      # smoke
            sx = (k * 23 + t * 5) % (cx + 40); sy = ROAD_Y - 10 - ((t - 13) * 8 + k * 5) % 40
            d.rectangle([sx, sy, sx + 4, sy + 3], fill=(90, 90, 100))
    # speedometer
    d.rectangle([248, 8, 312, 34], fill=(20, 20, 20)); d.rectangle([250, 10, 310, 32], fill=(50, 10, 10))
    val = 88 if t >= 13 else int(sp)
    on = not (t >= 13 and int(t * 4) % 2)
    if on: digits(d, 262, 13, f'{val:02d}', (255, 120, 40), sc=3)
    if t > 17.4: im = Image.blend(im, Image.new('RGB', (W, H)), clamp((t - 17.4) / 0.6))
    return im

def music(path):
    tr = Track(SEC); bpm = 140; b = 60 / bpm
    # 0-4s: anticipation – low pedal + soft timpani rolls
    for k in range(int(4 / (b / 2))):
        tr.add(k * b / 2, osc('tri', freq('C2'), b / 2 * 0.9, 0.35, adsr=(0.003, 0.05, 0.6, 0.02)))
    tr.seq(0, bpm, 'G3+C4:4 A3+D4:4', 'sq', 0.05, duty=0.25, gate=1, adsr=(0.3, 0.1, 0.8, 0.2))
    # 4-13s: heroic brass fanfare (original melody), driving bass
    m = ('G4:.5 C5:.5 E5:1 D5:.5 C5:.5 G5:2 '
         'F5:.5 E5:.5 D5:.5 C5:.5 A5:1.5 G5:.5 E5:2 '
         'F5:.75 G5:.25 A5:1 C6:1 B5:.5 A5:.5 G5:2 '
         'A5:.5 B5:.5 C6:1 D6:1 E6:2')
    t0 = 4.0
    tr.seq(t0, bpm, m, 'sq', 0.13, duty=0.25, vib=0.004)
    tr.seq(t0, bpm, m.replace('4:', '3:').replace('5:', '4:').replace('6:', '5:'), 'sq', 0.05, duty=0.5)  # octave double
    bass = ' '.join(['C3:.5 C4:.5'] * 4 + ['F2:.5 F3:.5'] * 4 + ['G2:.5 G3:.5'] * 4 + ['A2:.5 A3:.5'] * 2 + ['F2:.5 F3:.5'] * 2 + ['G2:.5 G3:.5'] * 4)
    tr.seq(t0, bpm, bass, 'tri', 0.3)
    nb = int((13 - t0) / b)
    for k in range(nb):
        tt = t0 + k * b; tr.hat(tt + b / 2)
        if k % 2 == 0: tr.kick(tt)
        else: tr.snare(tt, 0.18)
    for k in range(int(2.5 / (b / 4))):          # snare roll building to 88
        tr.snare(10.5 + k * b / 4, 0.05 + 0.15 * k / 23, dec=40)
    # 13s: the jump — hit + triumphant chord
    tr.boom(13.0, 0.7, 2.0)
    for nt in ('C4', 'E4', 'G4', 'C5', 'E5', 'G5'): tr.add(13.0, osc('sq', freq(nt), 4.5, 0.05, duty=0.25, vib=0.004, adsr=(0.01, 0.3, 0.7, 1.5)))
    tr.add(13.0, osc('tri', freq('C2'), 4.5, 0.4, adsr=(0.005, 0.3, 0.6, 1.5)))
    for k in range(60):                          # fire crackle
        tr.add(13.3 + k * 0.07, osc('noise', k, 0.03, 0.03, adsr=(0.001, 0.01, 0.3, 0.01)))
    tr.write(path, SEC)

if __name__ == '__main__':
    music('out/s2.wav')
    if 'stills' in sys.argv:
        for tt in (2, 7, 12.5, 13.05, 15): still(frame, tt, f'out/s2_{tt}.png')
    else:
        render(frame, SEC, 'out/s2.wav', 'out/s2_bttf.mp4')
