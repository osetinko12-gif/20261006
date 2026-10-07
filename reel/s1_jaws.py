"""JAWS — calm beach, the view from below, the fin. ~18s"""
import math, random, sys
import numpy as np
from PIL import Image, ImageDraw
from engine import *

SEC = 18
random.seed(7)
SKY = [(140, 205, 245), (120, 190, 240), (100, 175, 235)]
SEA1, SEA2, FOAM = (30, 110, 185), (22, 85, 160), (220, 240, 250)
SAND, SAND2 = (240, 222, 165), (225, 200, 140)
SKIN, FIN, FIN2 = (240, 190, 150), (70, 80, 95), (110, 120, 135)
swimmers = [(60, 98, (230, 60, 60)), (110, 112, (250, 210, 60)), (170, 92, (60, 200, 120)),
            (230, 105, (240, 120, 200)), (275, 95, (80, 140, 240))]

def beach(d, t, panic=0.0):
    for i, c in enumerate(SKY): d.rectangle([0, i * 20, W, i * 20 + 20], fill=c)
    for cx in (40, 200):                         # clouds
        x = (cx + t * 3) % (W + 60) - 30
        d.rectangle([x, 14, x + 34, 20], fill=(250, 250, 255)); d.rectangle([x + 6, 10, x + 26, 14], fill=(250, 250, 255))
    for k in range(3):                           # gulls
        gx = (k * 110 + t * 14) % (W + 20) - 10; gy = 30 + k * 7
        wing = 1 if int(t * 6 + k) % 2 else 0
        d.line([gx - 3, gy - wing, gx, gy, gx + 3, gy - wing], fill=(60, 60, 70))
    d.rectangle([0, 60, W, 140], fill=SEA1)
    d.rectangle([0, 60, W, 66], fill=SEA2)
    for y in range(68, 138, 6):
        off = int(t * 10 + y * 3) % 24
        for x in range(-off, W, 24): d.line([x, y, x + 6, y], fill=(60, 140, 205))
    for x in range(0, W, 2):                     # shoreline foam
        fy = 138 + int(2 * math.sin(x / 9 + t * 2))
        d.point((x, fy), fill=FOAM); d.point((x, fy + 1), fill=FOAM)
    d.rectangle([0, 141, W, H], fill=SAND)
    for i in range(80): d.point(((i * 53) % W, 145 + (i * 29) % 34), fill=SAND2)
    for ux, col in ((40, (220, 50, 50)), (150, (40, 120, 220)), (260, (240, 170, 40))):  # umbrellas
        d.line([ux, 152, ux, 172], fill=(120, 90, 60))
        for s in range(7):
            c = col if s % 2 == 0 else (250, 250, 250)
            d.polygon([(ux - 14 + s * 4, 156), (ux, 146), (ux - 10 + s * 4, 156)], fill=c)
        d.rectangle([ux + 4, 168, ux + 16, 171], fill=(250, 250, 250))
        d.rectangle([ux + 6, 166, ux + 9, 168], fill=SKIN)
    for k, (sx, sy, cap) in enumerate(swimmers):
        bob = int(math.sin(t * 3 + k) * 1)
        x = sx - panic * (sx - 160) * 0.0
        y = sy + bob + panic * (140 - sy)
        if panic > 0:                            # running out of the water
            x = sx + math.sin(t * 20 + k) * 1
            y = sy + panic * (150 - sy)
            if y > 138:
                d.rectangle([x - 1, y - 6, x + 1, y], fill=SKIN)
                d.rectangle([x - 1, y - 8, x + 1, y - 7], fill=cap)
                leg = int(t * 12 + k) % 2
                d.line([x - 1, y, x - 2 + leg * 2, y + 3], fill=SKIN)
                continue
        d.rectangle([x - 2, y - 2, x + 2, y + 1], fill=SKIN); d.rectangle([x - 2, y - 3, x + 2, y - 2], fill=cap)
        d.line([x - 4, y + 2, x + 4, y + 2], fill=FOAM)
    # kid on yellow raft
    rx, ry = 130, 80 + int(math.sin(t * 2.5) * 1)
    d.rectangle([rx, ry, rx + 14, ry + 3], fill=(250, 215, 40)); d.rectangle([rx + 4, ry - 2, rx + 9, ry], fill=SKIN)

def fin(d, x, y, s=1.0):
    h = int(12 * s); w = int(10 * s)
    d.polygon([(x, y), (x + w // 2, y - h), (x + w, y)], fill=FIN)
    d.line([x + w // 2, y - h, x + w, y], fill=FIN2)
    for k in range(4): d.point((x + w + 2 + k * 3, y + (k % 2)), fill=FOAM)
    d.line([x - 2, y + 1, x + w + 2, y + 1], fill=FOAM)

def underwater(d, t, lt):
    for y in range(H):
        d.line([0, y, W, y], fill=mix((60, 150, 200), (4, 14, 34), y / H))
    for k in range(6):                           # light shafts
        x0 = 30 + k * 55 + int(math.sin(t + k) * 6)
        for y in range(0, 120, 2):
            if (y // 2 + k) % 3: d.point((x0 + y // 5, y), fill=(110, 185, 225))
    d.rectangle([0, 0, W, 10], fill=(150, 210, 240))
    for x in range(0, W, 2): d.point((x, 10 + int(math.sin(x / 7 + t * 3))), fill=(200, 235, 250))
    # swimmers seen from below: body at the surface, legs dangling
    SIL = (18, 48, 78)
    for k, lx in enumerate((70, 150, 235)):
        kick = math.sin(t * 5 + k * 2) * 2
        d.rectangle([lx - 9, 9, lx + 9, 14], fill=SIL)          # torso flat on the surface
        d.rectangle([lx - 14, 10, lx - 9, 12], fill=SIL); d.rectangle([lx + 9, 10, lx + 14, 12], fill=SIL)
        d.rectangle([lx - 4, 14, lx - 1, 24 + kick], fill=SIL)    # thighs
        d.rectangle([lx + 1, 14, lx + 4, 24 - kick], fill=SIL)
        d.rectangle([lx - 4 + int(kick), 24 + kick, lx - 2 + int(kick), 34 + kick], fill=SIL)
        d.rectangle([lx + 2 - int(kick), 24 - kick, lx + 4 - int(kick), 34 - kick], fill=SIL)
    # the shape rising from the deep
    s = 0.4 + lt * 1.3
    cx = 150 + math.sin(t * 0.8) * 8; cy = 190 - lt * 110
    L = 70 * s; Wd = 14 * s
    d.ellipse([cx - Wd, cy - L * 0.5, cx + Wd, cy + L * 0.5], fill=(10, 22, 40))
    d.polygon([(cx - Wd, cy), (cx - Wd * 3.2, cy + L * 0.22), (cx - Wd * 0.6, cy + L * 0.12)], fill=(10, 22, 40))
    d.polygon([(cx + Wd, cy), (cx + Wd * 3.2, cy + L * 0.22), (cx + Wd * 0.6, cy + L * 0.12)], fill=(10, 22, 40))
    tail = math.sin(t * 5) * Wd
    d.polygon([(cx, cy + L * 0.45), (cx - Wd * 1.4 + tail, cy + L * 0.8), (cx + Wd * 1.4 + tail, cy + L * 0.8)], fill=(10, 22, 40))
    for k in range(5):                           # bubbles
        by = (cy - 20 - ((t * 40 + k * 23) % 60)); bx = cx + (k - 2) * 6
        d.point((bx, by), fill=(160, 210, 235))

def surface(d, t, lt):
    for y in range(H): d.line([0, y, W, y], fill=mix((40, 125, 195), (18, 70, 140), y / H))
    for y in range(4, H, 7):
        off = int(t * 14 + y * 5) % 30
        for x in range(-off, W, 30): d.line([x, y, x + 8, y], fill=(70, 150, 210))
    # swimmer (close)
    sx, sy = 96, 96 + int(math.sin(t * 3) * 1)
    d.rectangle([sx - 6, sy - 7, sx + 6, sy + 2], fill=SKIN)
    d.rectangle([sx - 6, sy - 9, sx + 6, sy - 6], fill=(230, 60, 60))
    d.point((sx - 3, sy - 3), fill=(30, 30, 30)); d.point((sx + 2, sy - 3), fill=(30, 30, 30))
    d.line([sx - 9, sy + 3, sx + 9, sy + 3], fill=FOAM)
    fx = int(lerp(330, 130, clamp(lt / 0.75)))
    fin(d, fx, 104, 2.2)
    if lt > 0.25:                                # "!"
        bx, by = sx - 4, sy - 30
        d.rectangle([bx, by, bx + 9, by + 13], fill=(250, 250, 250)); d.rectangle([bx + 1, by + 1, bx + 8, by + 12], fill=(250, 250, 250))
        d.rectangle([bx + 4, by + 2, bx + 5, by + 8], fill=(220, 30, 30)); d.rectangle([bx + 4, by + 10, bx + 5, by + 11], fill=(220, 30, 30))
        d.polygon([(bx + 3, by + 13), (bx + 6, by + 13), (bx + 4, by + 16)], fill=(250, 250, 250))

def frame(t, i):
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    if t < 6:
        beach(d, t)
        if t > 3.5: fin(d, int(lerp(330, 250, (t - 3.5) / 2.5)), 70, 0.6)
    elif t < 12:
        underwater(d, t, (t - 6) / 6)
    elif t < 15:
        surface(d, t, (t - 12) / 3)
    elif t < 15.5:                               # splash
        surface(d, t, 1)
        random.seed(i)
        for k in range(160):
            a = random.uniform(0, math.pi); r = random.uniform(0, 70) * (t - 15 + 0.2) * 3
            d.rectangle([110 + math.cos(a) * r * 1.4, 100 - math.sin(a) * r, 112 + math.cos(a) * r * 1.4, 102 - math.sin(a) * r], fill=FOAM)
    else:
        lt = (t - 15.5) / 2.5
        beach(d, t, panic=clamp(lt * 1.6))
        fin(d, int(170 + math.sin(t * 1.5) * 50), 86, 0.8)
    if 5.8 < t < 6.0 or 11.9 < t < 12.0: d.rectangle([0, 0, W, H], fill=(0, 0, 0))
    if t > 17.4: im = Image.blend(im, Image.new('RGB', (W, H)), clamp((t - 17.4) / 0.6))
    return im

def music(path):
    tr = Track(SEC)
    for k in range(240):                          # soft surf
        tr.add(k * 0.075, osc('noise', 1, 0.075, 0.012 * (1 + math.sin(k / 9)), adsr=(0.03, 0.02, 1, 0.03)))
    # accelerating low pulse (alternating minor third, not the famous semitone)
    t, gap, k = 0.6, 0.9, 0
    while t < 15:
        nt = 'A2' if k % 2 == 0 else 'C3'
        tr.add(t, osc('sq', freq(nt), min(0.22, gap * 0.8), 0.20, duty=0.125, adsr=(0.003, 0.08, 0.5, 0.05)))
        tr.add(t, osc('tri', freq(nt) / 2, min(0.25, gap * 0.8), 0.30, adsr=(0.003, 0.1, 0.6, 0.05)))
        k += 1; t += gap; gap = max(0.13, gap * 0.94)
    # string tremolo underwater
    for k in range(int(6 / 0.08)):
        tt = 6 + k * 0.08
        tr.add(tt, osc('sq', freq('E5') if k % 2 else freq('F5'), 0.07, 0.035 * (k / 75), duty=0.25))
    tr.seq(9, 120, 'D4+G#4:4 C#4+G4:2', 'saw', 0.05, gate=1, adsr=(0.6, 0.2, 0.8, 0.4))
    # stab at "!" and splash
    for nt in ('C5', 'C#5', 'F#5', 'G5'): tr.add(12.8, osc('sq', freq(nt), 0.6, 0.07, duty=0.25, adsr=(0.002, 0.2, 0.4, 0.2)))
    tr.boom(15.0, 0.5, 2.0)
    for nt in ('A2', 'Eb3', 'A3', 'Bb3', 'E4'): tr.add(15.0, osc('saw', freq(nt), 2.4, 0.06, adsr=(0.002, 0.5, 0.5, 0.8)))
    t = 15.6                                     # fading pulse while the fin circles
    while t < 18: tr.add(t, osc('tri', freq('A1'), 0.25, 0.35, adsr=(0.003, 0.1, 0.6, 0.05))); t += 0.45
    tr.write(path, SEC)

if __name__ == '__main__':
    music('out/s1.wav')
    if 'stills' in sys.argv:
        for tt in (2, 9, 13.5, 15.2, 16.8): still(frame, tt, f'out/s1_{tt}.png')
    else:
        render(frame, SEC, 'out/s1.wav', 'out/s1_jaws.mp4')
