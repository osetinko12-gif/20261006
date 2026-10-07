"""E.T. — kids racing through the forest, lift-off, across the moon. ~17s"""
import math, random, sys
from PIL import Image, ImageDraw
from engine import *

SEC = 17
SIL = (10, 12, 26)
HOOD, SKIN, BLANKET, ETSKIN = (200, 40, 40), (235, 185, 145), (240, 240, 235), (150, 120, 90)
JACKETS = [(60, 120, 200), (240, 200, 60), (90, 180, 90)]

def bmx(d, x, y, f, rider=(200, 40, 40), basket=False, sil=False):
    c = SIL if sil else None
    frame_c = c or (30, 30, 34)
    for cx in (x, x + 18):
        d.ellipse([cx - 6, y - 6, cx + 6, y + 6], outline=frame_c)
        a = f * 0.9
        d.line([cx + int(5 * math.cos(a)), y + int(5 * math.sin(a)), cx - int(5 * math.cos(a)), y - int(5 * math.sin(a))], fill=frame_c)
    d.line([x, y, x + 8, y - 7, x + 18, y], fill=c or (200, 40, 40)); d.line([x + 8, y - 7, x + 15, y - 8], fill=c or (200, 40, 40))
    d.line([x + 15, y - 8, x + 18, y], fill=frame_c); d.line([x + 15, y - 8, x + 16, y - 12], fill=frame_c)
    d.line([x + 14, y - 12, x + 18, y - 12], fill=frame_c)
    # rider: body leaning forward, hood
    d.polygon([(x + 6, y - 9), (x + 9, y - 19), (x + 13, y - 18), (x + 11, y - 9)], fill=c or rider)
    d.rectangle([x + 10, y - 24, x + 15, y - 19], fill=c or rider)
    if not sil: d.rectangle([x + 13, y - 22, x + 15, y - 20], fill=SKIN)
    d.line([x + 12, y - 16, x + 16, y - 12], fill=c or rider)
    leg = int(f) % 2
    d.line([x + 8, y - 9, x + 9 + leg * 2, y - 3, x + 8 + leg * 2, y], fill=c or (40, 50, 90))
    if basket:
        d.rectangle([x + 16, y - 15, x + 23, y - 10], fill=c or (170, 120, 60))
        d.polygon([(x + 16, y - 15), (x + 18, y - 21), (x + 23, y - 21), (x + 24, y - 15)], fill=c or BLANKET)
        d.ellipse([x + 17, y - 23, x + 23, y - 18], fill=c or ETSKIN)
        if not sil: d.point((x + 22, y - 21), fill=(20, 20, 20))

def forest(d, t, scroll, lift):
    for y in range(H): d.line([0, y, W, y], fill=mix((30, 34, 80), (120, 70, 110), y / H))
    random.seed(2)
    for k in range(40):
        d.point((random.randrange(W), random.randrange(80)), fill=(220, 220, 255))
    for layer, (spd, base, col) in enumerate([(0.2, 120, (40, 40, 80)), (0.5, 140, (25, 28, 55)), (1.0, 168, (12, 14, 30))]):
        off = -(scroll * spd) % 14
        for k in range(-1, W // 14 + 2):
            tx = off + k * 14; h = 30 + ((k * 37 + layer * 11 + int(scroll * spd) // 14 * 13) % 23) + layer * 6
            d.polygon([(tx - 2, base), (tx + 7, base - h), (tx + 16, base)], fill=col)
        d.rectangle([0, base, W, H], fill=col)
    d.rectangle([0, 150, W, 156], fill=(60, 50, 50))

def moonshot(d, t, i, lt):
    for y in range(H): d.line([0, y, W, y], fill=mix((14, 20, 52), (28, 40, 88), y / H))
    random.seed(9)
    for k in range(70):
        sx, sy = random.randrange(W), random.randrange(140)
        if (k + i // 6) % 7: d.point((sx, sy), fill=(225, 225, 255))
    mx, my, r = 196, 74, 54
    for g in range(6, 0, -1):
        d.ellipse([mx - r - g * 3, my - r - g * 3, mx + r + g * 3, my + r + g * 3], fill=mix((14, 20, 52), (70, 80, 120), (7 - g) / 10))
    d.ellipse([mx - r, my - r, mx + r, my + r], fill=(248, 244, 222))
    for cx, cy, cr in [(178, 58, 8), (214, 92, 10), (206, 52, 4), (172, 96, 5), (226, 66, 5)]:
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(230, 225, 200))
    for tx in range(-4, W, 8):
        h = 22 + ((tx * 37) % 19)
        d.polygon([(tx, H), (tx + 5, H - h), (tx + 10, H)], fill=SIL)
    d.rectangle([0, H - 10, W, H], fill=SIL)
    u = 2 * (lt - 0.5); c = u ** 3 * 0.8 + u * 0.2
    bx = int(184 + 230 * c); by = int(88 - 80 * c)
    bmx(d, bx, by, i / 3, basket=True, sil=True)

def frame(t, i):
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    if t < 6.5:
        scroll = t * 70
        lift = clamp((t - 3.5) / 3)
        forest(d, t, scroll, lift)
        for k, jc in enumerate(JACKETS):         # friends behind
            fl = clamp((t - 4.2 - k * 0.35) / 2.5)
            bmx(d, 30 + k * 34, int(150 - fl * fl * 120 + math.sin(t * 9 + k)), i / 3, rider=jc)
        ly = int(150 - lift * lift * 130)
        bmx(d, 150, ly, i / 3, rider=HOOD, basket=True)
        if lift > 0:                             # sparkles under the wheels
            random.seed(i)
            for k in range(10): d.point((150 + random.randint(-8, 26), ly + random.randint(2, 14)), fill=(255, 255, 200))
    elif t < 7.0:
        im = Image.new('RGB', (W, H), (0, 0, 0)); return im
    else:
        moonshot(d, t, i, clamp((t - 7.2) / 8.0))
    if t < 0.5: im = Image.blend(Image.new('RGB', (W, H)), im, clamp(t / 0.5))
    if t > 16.2: im = Image.blend(im, Image.new('RGB', (W, H)), clamp((t - 16.2) / 0.8))
    return im

def music(path):
    tr = Track(SEC); bpm = 168; b = 60 / bpm          # 3/4 waltz feel, felt in one
    # pulsing chase (0-3.5s)
    for k in range(int(3.6 / (b / 2))):
        tr.add(k * b / 2, osc('sq', freq('D3') if k % 4 < 2 else freq('E3'), b / 2 * 0.8, 0.08, duty=0.25))
        if k % 2 == 0: tr.kick(k * b / 2, 0.3)
    tr.seq(0, bpm, 'D5:.5 E5:.5 F#5:.5 A5:.5 D5:.5 E5:.5 F#5:.5 B5:.5', 'sq', 0.06, duty=0.5)
    # lift-off: rising run (lydian sparkle)
    run = ' '.join(f'{n}:.25' for n in ['D5', 'E5', 'F#5', 'G#5', 'A5', 'B5', 'C#6', 'D6', 'E6', 'F#6', 'G#6', 'A6'])
    tr.seq(3.6, bpm, run, 'sq', 0.07, duty=0.25)
    for k in range(40): tr.add(3.6 + k * 0.07, osc('tri', freq('A6') * (1 + k / 80), 0.06, 0.03))
    # soaring theme over the moon (original melody, waltz bass)
    t0 = 5.4
    theme = ('D5:3 A5:2 G#5:1 F#5:2 E5:1 F#5:3 '
             'D5:2 E5:1 F#5:2 A5:1 D6:4 C#6:1 B5:1 A5:6')
    tr.seq(t0, bpm, theme, 'sq', 0.12, duty=0.5, vib=0.006, gate=0.97, adsr=(0.02, 0.1, 0.8, 0.15))
    tr.seq(t0, bpm, theme.replace('5:', '4:').replace('6:', '5:'), 'tri', 0.10, gate=0.97)
    chords = [('D3', 'A3', 'F#4'), ('D3', 'A3', 'F#4'), ('E3', 'B3', 'G#4'), ('D3', 'A3', 'F#4'),
              ('D3', 'A3', 'F#4'), ('E3', 'B3', 'G#4'), ('G3', 'D4', 'B4'), ('G3', 'D4', 'B4'),
              ('A3', 'E4', 'C#5'), ('A3', 'E4', 'C#5')]
    for k, (r, f5, tn) in enumerate(chords):
        tt = t0 + k * 3 * b
        tr.add(tt, osc('tri', freq(r), b * 0.95, 0.30))
        tr.add(tt + b, osc('sq', freq(f5), b * 0.6, 0.04, duty=0.25)); tr.add(tt + b, osc('sq', freq(tn), b * 0.6, 0.04, duty=0.25))
        tr.add(tt + 2 * b, osc('sq', freq(f5), b * 0.6, 0.04, duty=0.25)); tr.add(tt + 2 * b, osc('sq', freq(tn), b * 0.6, 0.04, duty=0.25))
    end = t0 + 30 * b
    for nt in ('D3', 'A3', 'D4', 'F#4', 'A4', 'D5'):
        tr.add(end, osc('sq', freq(nt), SEC - end, 0.04, duty=0.5, vib=0.005, adsr=(0.05, 0.3, 0.7, 1.5)))
    tr.write(path, SEC, echo=0.35, delay=0.18)

if __name__ == '__main__':
    music('out/s3.wav')
    if 'stills' in sys.argv:
        for tt in (2, 5.5, 11, 14): still(frame, tt, f'out/s3_{tt}.png')
    else:
        render(frame, SEC, 'out/s3.wav', 'out/s3_et.mp4')
