from common import *

def ice_land(d, t, y0=130):
    grad(d, 0, y0, (176, 190, 200), (214, 222, 228))
    r = random.Random(20)
    for k in range(14):                          # frozen clouds hanging in the sky
        x = r.randrange(-40, W); y = r.randrange(10, 80); w = r.randint(40, 110)
        d.ellipse([x, y, x + w, y + r.randint(14, 30)], fill=(236, 240, 244)); d.ellipse([x + 6, y + 10, x + w - 6, y + 30], fill=(200, 210, 218))
    grad(d, y0, H, (230, 236, 240), (200, 210, 220))
    for k in range(6):
        x = r.randrange(W); d.polygon([(x - 50, y0 + 4), (x, y0 - 18), (x + 50, y0 + 4)], fill=(214, 222, 230))

def s20_ice(t):                       # Mann's frozen world
    im, d = canvas(); ice_land(d, t)
    k = clamp(t / 8)
    ranger(d, lerp(300, 170, k), lerp(60, 150, k ** 0.7), 1.2, -1, flame=k < 1, f=int(t * 24))
    return im

def s21_mann(t):                      # the hero wakes from cryosleep
    im, d = zcanvas()
    grad(d, 0, ZH, (180, 190, 200), (140, 150, 160), 0, ZW)
    R(d, 20, 50, 110, 80, (220, 226, 232)); R(d, 22, 52, 108, 66, (150, 200, 230))
    portrait(d, 66, 72, 'mann', 1.4, cry=t > 2, beard=(140, 110, 80))
    for k in range(int(t * 8) % 20): d.point((24 + (k * 13) % 84, 54 + (k * 7) % 12), fill=(240, 250, 255))
    person(d, 140, 100, 'cooperS', -1); person(d, 160, 100, 'brand', -1)
    return up(im)

def s22_betrayal(t):                  # on the ridge: Mann turns on Cooper
    im, d = zcanvas()
    grad(d, 0, 60, (176, 190, 200), (214, 222, 228), 0, ZW)
    d.polygon([(0, 70), (60, 64), (120, 72), (192, 60), (192, 108), (0, 108)], fill=(226, 232, 238))
    d.polygon([(0, 80), (192, 86), (192, 108), (0, 108)], fill=(206, 214, 222))
    shove = clamp((t - 3) / 1.5)
    astro(d, 90 - shove * 6, 88, 1, 'reach' if t < 6 else 'stand', visor=(80, 110, 140), s=1.3)
    astro(d, 116 + shove * 14, 88 + shove * 6, -1, 'stand', visor=(70, 100, 130), crack=t > 5, s=1.3)
    if t > 5:
        for k in range(14): d.point((112 + shove * 14 + (k * 5) % 16 - 8, 40 + (k * 3) % 12), fill=(240, 250, 255))
        bubble(d, 112 + shove * 14, 30, '!')
    return up(im)

def boom(d, cx, cy, k, seed=1):
    r = random.Random(seed)
    for n in range(80):
        a = r.uniform(0, 6.28); rr = r.uniform(0, 50) * k
        col = mix((255, 250, 220), (230, 100, 40), rr / 50)
        R(d, cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.8, cx + math.cos(a) * rr + 2, cy + math.sin(a) * rr * 0.8 + 2, col)

def s23_explosion(t):                 # Mann forces the airlock
    im, d = canvas((3, 4, 10)); stars(d, 23, 160)
    R(d, 0, 170, W, H, (230, 236, 240)); d.ellipse([-200, 150, 584, 400], fill=(220, 228, 236))
    endurance(d, 192, 90, 70, ang=t * (0.15 if t < 4 else 1.4), tilt=0.38, dmg=t > 4)
    if t > 3.5: boom(d, 192 + 70 * math.cos(0.15 * 3.5 + 3 * math.pi / 6), 90 + 70 * 0.38 * math.sin(0.15 * 3.5 + 3 * math.pi / 6), clamp((t - 3.5) / 1.5))
    return im

def s24_docking(t):                   # matching the spin
    im, d = canvas((2, 3, 8)); stars(d, 24, 160)
    R(d, 0, 186, W, H, (230, 236, 240))
    spin = 2.6
    endurance(d, 192, 100, 72, ang=t * spin, tilt=0.9, dmg=True)
    for k in range(3):                           # motion arcs
        d.arc([192 - 82 - k * 4, 100 - 70 - k * 4, 192 + 82 + k * 4, 100 + 70 + k * 4], int(t * spin * 57) % 360, int(t * spin * 57) % 360 + 40, fill=(90, 90, 110))
    k = clamp(t / 9)
    rx, ry = lerp(40, 192, k), lerp(30, 100, k)
    ranger(d, rx - 26, ry, 1.0, 1, flame=True, f=int(t * 24))
    for n in range(3): d.line([rx - 40 - n * 8, ry - 4 + n, rx - 34 - n * 8, ry - 4 + n], fill=(150, 200, 255))
    return im

def s25_gargantua(t):                 # Gargantua
    im, d = canvas((0, 0, 0)); stars(d, 25, 200)
    gargantua(d, 192, 100, 46, t)
    k = clamp(t / 12)
    endurance(d, lerp(330, 270, k), lerp(170, 150, k), 7, ang=t * 0.2, tilt=0.5, dmg=True)
    return im

def s26_detach(t):                    # Cooper lets go so she can make it
    im, d = canvas((0, 0, 0)); stars(d, 26, 160)
    gargantua(d, 120, 110, 70, t)
    k = clamp(t / 10)
    endurance(d, 300 + k * 30, 50 - k * 20, 14, ang=t * 0.2, tilt=0.5, dmg=True)
    ranger(d, lerp(286, 200, k), lerp(64, 110, k), 0.5, -1)
    if t > 4:
        R(d, 300, 150, 380, 210, (40, 40, 50))
        portrait(d, 340, 210, 'brand', 1.8, cry=True)
    return im

def s27_fall(t):                      # into the dark
    im, d = canvas((0, 0, 0))
    r = random.Random(27)
    for k in range(220):                         # light streaks rushing past
        a = r.uniform(0, 6.28); q = (r.random() + t * 0.25) % 1
        rr = q * q * 260
        x = 192 + math.cos(a) * rr; y = 108 + math.sin(a) * rr
        d.line([x, y, 192 + math.cos(a) * rr * 0.86, 108 + math.sin(a) * rr * 0.86], fill=mix((60, 40, 20), (255, 230, 180), q))
    R(d, 0, 150, W, H, (30, 30, 34)); R(d, 0, 150, W, 152, (70, 70, 76))
    R(d, 60, 160, 324, 200, (44, 44, 50))
    for k in range(10): R(d, 80 + k * 24, 170, 90 + k * 24, 176, (200, 60, 40) if (k + int(t * 6)) % 3 == 0 else (60, 140, 90))
    if t > 8:
        boom(d, 192, 108, clamp((t - 8) / 2), 3)
    return im

SCENES = [
    ('氷の惑星', s20_ice, 6), ('英雄マン博士の目覚め', s21_mann, 4), ('裏切り', s22_betrayal, 6),
    ('ドッキングの暴走、爆発', s23_explosion, 4.5), ('回転に合わせてドッキング', s24_docking, 6),
    ('ブラックホール「ガルガンチュア」', s25_gargantua, 6), ('ひとり切り離す', s26_detach, 6), ('ブラックホールの中へ', s27_fall, 6),
]
