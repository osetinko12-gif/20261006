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
    R(d, 0, 92, ZW, ZH, (120, 130, 140))
    R(d, 30, 78, 100, 92, (220, 226, 232)); R(d, 32, 80, 98, 84, (150, 200, 230))      # cryo pod
    d.polygon([(30, 78), (36, 58), (104, 58), (100, 78)], fill=(190, 220, 236))          # lid swung open
    d.polygon([(34, 76), (39, 61), (100, 61), (97, 76)], fill=(160, 200, 224))
    person(d, 60, 92, 'mann', 1, 'sit', cry=clamp((t - 2) / 5))
    r = random.Random(int(t * 6))
    for k in range(24): d.point((32 + r.randrange(66), 50 + r.randrange(40)), fill=(240, 250, 255))
    person(d, 140, 100, 'cooperS', -1); person(d, 160, 100, 'brand', -1)
    return up(im)

def s22_betrayal(t):                  # Mann turns on Cooper: a brawl on the ice, then the visor
    im, d = zcanvas()
    grad(d, 0, 80, (176, 190, 200), (214, 222, 228), 0, ZW)
    d.polygon([(0, 70), (60, 64), (120, 72), (192, 60), (192, 108), (0, 108)], fill=(226, 232, 238))
    d.polygon([(0, 80), (192, 86), (192, 108), (0, 108)], fill=(206, 214, 222))
    MV, CV = (90, 120, 150), (70, 100, 130)
    crack = t > 8.0
    cop = astro_img(-1, 'stand', crack=crack, visor=CV); man = astro_img(1, 'reach', visor=MV)
    gy = 90
    if t < 2.0:                                   # face to face on the ridge
        paste_rot(im, astro_img(1, 'stand', visor=MV), 78, gy - 26, 0); paste_rot(im, cop, 116, gy - 26, 0)
    elif t < 3.0:                                 # Mann lunges, Cooper goes down
        k = (t - 2) / 1
        paste_rot(im, man, 78 + k * 22, gy - 26, -k * 20); paste_rot(im, cop, 116 + k * 8, gy - 26 + k * 12, 70 * k)
    elif t < 7.0:                                 # rolling, grabbing, punching
        ph = math.sin((t - 3) * 7)
        cx = 108 + math.sin((t - 3) * 2.2) * 10
        top_is_mann = int((t - 3) * 1.6) % 2 == 0
        a1, a2 = 90 + ph * 25, -90 + ph * 30
        if top_is_mann:
            paste_rot(im, cop, cx, gy - 10, a1); paste_rot(im, man, cx + ph * 3, gy - 22, a2 * 0.4 - 20)
        else:
            paste_rot(im, man, cx, gy - 10, -a1); paste_rot(im, cop, cx - ph * 3, gy - 22, -a2 * 0.4 + 20)
        r = random.Random(int(t * 12))
        for k in range(14): x = cx + r.randint(-30, 30); y = gy - r.randint(0, 12); R(d, x, y, x + 1, y + 1, (245, 248, 252))
    elif t < 8.6:                                 # Mann pins him and slams his helmet into the visor
        bob = abs(math.sin((t - 7) * 9)) * 6
        paste_rot(im, cop, 108, gy - 10, 90); paste_rot(im, man, 110, gy - 30 + bob, -60)
    else:                                         # Mann walks away; air hisses from the cracked visor
        paste_rot(im, cop, 108, gy - 10, 90 + math.sin(t * 5) * 4)
        mx = 120 - (t - 8.6) * 36
        if mx > -30: paste_rot(im, astro_img(-1, 'walk', visor=MV, f=t * 5), mx, gy - 26, 0)
        r = random.Random(int(t * 14))
        for n in range(24): d.point((88 + r.randint(-8, 6), gy - 14 + r.randint(-12, 4)), fill=(250, 252, 255))
    out = up(im)
    hit = (2.6 < t < 3.0) or any(abs(t - (7.1 + n * 0.35)) < 0.08 for n in range(4)) or (8.0 < t < 8.3)
    return shake(out, 4 if hit else (1 if 3 < t < 7 else 0), int(t * 24))

def s22b_trap(t):                     # the station's robot was rigged — Romilly is caught in the blast
    im, d = zcanvas()
    grad(d, 0, ZH, (110, 116, 124), (70, 74, 82), 0, ZW)
    R(d, 0, 84, ZW, ZH, (60, 64, 70)); R(d, 0, 84, ZW, 85, (130, 134, 140))
    for x in range(10, ZW, 30): R(d, x, 10, x + 20, 30, (90, 96, 104)); R(d, x + 2, 12, x + 18, 28, (60, 140, 120) if (x // 30 + int(t * 2)) % 3 else (50, 60, 60))
    for k in range(4): R(d, 110 + k * 5, 56, 114 + k * 5, 84, (54, 56, 60) if k % 2 else (66, 68, 72))   # the dead robot, dark
    R(d, 112, 62, 127, 66, (20, 20, 22)); R(d, 113, 63, 116, 65, (200, 60, 50) if t > 3 and int(t * 6) % 2 else (40, 20, 20))
    person(d, 96, 92, 'romilly', 1, 'reach')
    out = up(im)
    if t > 3.6:
        k = clamp((t - 3.6) / 0.8)
        out = glow(out, 236, 130, 40 + 400 * k, (255, 230, 180), 1.0)
        if t > 4.4: out = Image.blend(out, Image.new('RGB', (W, H), (40, 30, 26)), clamp((t - 4.4) / 2.5))
        out = shake(out, 5 if t < 5.2 else 1, int(t * 24))
    return out

def s22c_mannflies(t):                # Mann takes a ship alone and forces the docking
    im, d = canvas((3, 4, 10)); stars(d, 221, 160)
    R(d, 0, 176, W, H, (230, 236, 240)); d.ellipse([-200, 160, 584, 420], fill=(220, 228, 236))
    endurance(d, 260, 80, 80, ang=0.15 * t + 0.4, tilt=0.42)
    k = clamp(t / 6)
    jitter = math.sin(t * 13) * 2 * k
    ranger(d, lerp(10, 150, k ** 0.8), lerp(150, 92, k ** 0.8) + jitter, 0.9, 1, flame=True, f=int(t * 24))
    R(d, lerp(10, 150, k ** 0.8) + 39, lerp(150, 92, k ** 0.8) + jitter - 7, lerp(10, 150, k ** 0.8) + 41, lerp(150, 92, k ** 0.8) + jitter - 5, SKIN)
    if t > 6:                                     # grinding contact sparks at the hub
        r = random.Random(int(t * 20))
        for n in range(20):
            x = 200 + r.randint(-6, 6); y = 84 + r.randint(-4, 4)
            d.line([x, y, x + r.randint(-14, 14), y + r.randint(-10, 10)], fill=r.choice([(255, 220, 120), (255, 255, 230), (255, 160, 60)]))
    return im

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

def s24b_cockpit(t):                  # close-up: Cooper fighting the spin
    im, d = zcanvas((10, 10, 16))
    a = t * 2.6
    for k in range(40):                          # stars wheeling past the window
        rr = 20 + (k * 37) % 90; aa = a + k * 0.7
        x = 96 + math.cos(aa) * rr; y = 40 + math.sin(aa) * rr * 0.6
        d.line([x, y, 96 + math.cos(aa - 0.12) * rr, 40 + math.sin(aa - 0.12) * rr * 0.6], fill=(200, 200, 230))
    R(d, 0, 66, ZW, ZH, (50, 52, 58)); d.polygon([(0, 0), (30, 0), (10, 66), (0, 66)], fill=(50, 52, 58)); d.polygon([(192, 0), (162, 0), (182, 66), (192, 66)], fill=(50, 52, 58))
    warn = int(t * 4) % 2
    for k in range(6): R(d, 20 + k * 28, 72, 30 + k * 28, 76, (230, 60, 50) if (warn + k) % 2 else (70, 70, 76))
    portrait(d, 72, 108, 'brand', 1.5, shock=True)
    portrait(d, 118, 108, 'cooperS', 1.5)
    R(d, 134, 94, 142, 100, (40, 40, 44)); R(d, 130, 92, 136, 97, SKIN)                  # hand on the stick
    tars(d, 150, 100)
    return shake(up(im), 1, int(t * 24))

def s24d_lock(t):                     # outside: the Ranger slides into the spinning hub and locks
    im = Image.new('RGB', (W, H), (2, 3, 8))
    spin = -t * 2.6
    r = random.Random(242)
    d = ImageDraw.Draw(im)
    for k in range(160):                          # the whole sky wheels around the joined ships
        rr = r.uniform(10, 260); a0 = r.uniform(0, 6.28) + spin
        x, y = 192 + math.cos(a0) * rr, 108 + math.sin(a0) * rr
        d.line([x, y, 192 + math.cos(a0 + 0.05) * rr, 108 + math.sin(a0 + 0.05) * rr], fill=(200, 200, 230))
    spr = Image.new('RGBA', (300, 300), (0, 0, 0, 0)); sd = ImageDraw.Draw(spr)
    sd.ellipse([150 - 70, 150 - 70, 150 + 70, 150 + 70], fill=(150, 150, 146))
    sd.ellipse([150 - 58, 150 - 58, 150 + 58, 150 + 58], fill=(196, 196, 190))
    for k in range(8):
        a = k * math.pi / 4; sd.line([150 + math.cos(a) * 58, 150 + math.sin(a) * 58, 150 + math.cos(a) * 70, 150 + math.sin(a) * 70], fill=(110, 110, 106), width=3)
    sd.ellipse([150 - 18, 150 - 18, 150 + 18, 150 + 18], fill=(40, 40, 46))     # docking port
    ins = clamp(t / 2.4)
    nose = 150 + 12 - (1 - ins) * 60                                             # Ranger seen from behind, sliding in
    sd.ellipse([150 - 26, 150 - 14 - (1 - ins) * 30, 150 + 26, 150 + 14 - (1 - ins) * 30], fill=(205, 205, 200))
    sd.ellipse([150 - 10, 150 - 8 - (1 - ins) * 30, 150 + 10, 150 + 8 - (1 - ins) * 30], fill=(120, 120, 120))
    if t > 2.5:                                   # clamps close
        for k in range(4):
            a = k * math.pi / 2 + math.pi / 4
            sd.polygon([(150 + math.cos(a) * 30, 150 + math.sin(a) * 30), (150 + math.cos(a + 0.3) * 20, 150 + math.sin(a + 0.3) * 20),
                        (150 + math.cos(a - 0.3) * 20, 150 + math.sin(a - 0.3) * 20)], fill=(240, 200, 80))
    rot = spr.rotate(math.degrees(spin) if t > 2.5 else math.degrees(spin) * clamp(t / 2.5), resample=Image.NEAREST)
    im.paste(rot, (192 - 150, 108 - 150), rot)
    if 2.5 < t < 2.8: im = glow(im, 192, 108, 80, (255, 240, 200), 0.8)
    return shake(im, 3 if 2.5 < t < 2.9 else 0, int(t * 24))

def s24c_cheer(t):                    # docked! relief and laughter in the cockpit
    im, d = zcanvas((14, 14, 22))
    stars_still = random.Random(3)
    for k in range(50): d.point((stars_still.randrange(30, 162), stars_still.randrange(0, 60)), fill=(220, 220, 240))
    R(d, 70, 22, 122, 50, (200, 200, 196)); R(d, 84, 30, 108, 42, (150, 150, 146))          # the docking hub, locked
    R(d, 0, 66, ZW, ZH, (50, 52, 58)); d.polygon([(0, 0), (30, 0), (10, 66), (0, 66)], fill=(50, 52, 58)); d.polygon([(192, 0), (162, 0), (182, 66), (192, 66)], fill=(50, 52, 58))
    for k in range(6): R(d, 20 + k * 28, 72, 30 + k * 28, 76, (80, 200, 110))              # all lights green
    joy = t > 1.6
    bob = abs(math.sin(t * 7)) * 2 if 1.6 < t < 4.5 else 0
    portrait(d, 118, 108 - bob, 'cooperS', 1.5, smile=joy)
    portrait(d, 72, 108 - (abs(math.sin(t * 7 + 1)) * 2 if 1.6 < t < 4.5 else 0), 'brand', 1.5, smile=joy, closed=2.0 < t < 3.4)
    if joy:                                       # her hand on his shoulder
        R(d, 90, 92, 102, 97, (178, 166, 132)); R(d, 100, 91, 106, 96, SKIN)
    from common import tars
    tars(d, 150, 100)
    return up(im)

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
    return im

def s27_fall(t):                      # into the dark: the Ranger breaks up, sparks hit Cooper, he blacks out
    im, d = zcanvas((0, 0, 0))
    r = random.Random(27)
    for k in range(110):                          # light streaks rushing past the window
        a = r.uniform(0, 6.28); q = (r.random() + t * 0.3) % 1
        rr = q * q * 130
        x = 96 + math.cos(a) * rr; y = 34 + math.sin(a) * rr * 0.6
        d.line([x, y, 96 + math.cos(a) * rr * 0.86, 34 + math.sin(a) * rr * 0.86 * 0.6], fill=mix((60, 40, 20), (255, 230, 180), q))
    R(d, 0, 62, ZW, ZH, (44, 44, 50)); d.polygon([(0, 0), (26, 0), (10, 62), (0, 62)], fill=(44, 44, 50)); d.polygon([(192, 0), (166, 0), (182, 62), (192, 62)], fill=(44, 44, 50))
    if t > 4:                                     # the window cracks
        k = clamp((t - 4) / 3)
        for n in range(5):
            a = n * 1.3 + 0.4; d.line([120, 20, 120 + math.cos(a) * 40 * k, 20 + math.sin(a) * 30 * k], fill=(230, 240, 255))
    alarm = int(t * 6) % 2 and t > 2
    for k in range(6): R(d, 20 + k * 28, 68, 30 + k * 28, 72, (230, 60, 50) if alarm else (70, 70, 76))
    out_cold = t > 8.6
    sink = clamp((t - 8.6) / 1.5) * 5
    portrait(d, 96, 108 + sink, 'cooperS', 1.6, shock=2.5 < t < 8.6, closed=out_cold)
    if 2.5 < t < 9:                               # sparks spraying from the panels into the cabin, hitting him
        rr = random.Random(int(t * 24))
        for n in range(int(10 + 30 * clamp((t - 2.5) / 5))):
            sx = rr.choice([10, 182]); sy = rr.randint(40, 70)
            ex = 96 + rr.randint(-30, 30); ey = 70 + rr.randint(-20, 20)
            q = rr.random()
            d.line([sx + (ex - sx) * q, sy + (ey - sy) * q, sx + (ex - sx) * (q + 0.08), sy + (ey - sy) * (q + 0.08)],
                   fill=rr.choice([(255, 220, 120), (255, 255, 220), (255, 150, 60)]))
        if rr.random() < 0.3:                    # debris chunks flying in
            x = rr.randint(40, 150); y = rr.randint(10, 60); R(d, x, y, x + 3, y + 2, (120, 120, 126))
    out = up(im)
    if 8.2 < t < 8.7: out = glow(out, 192, 120, 300, (255, 240, 210), 1.0)
    out = shake(out, int(1 + 4 * clamp((t - 3) / 5)) if t < 8.8 else 0, int(t * 24))
    if t > 9: out = Image.blend(out, Image.new('RGB', (W, H)), clamp((t - 9) / 2))
    return out

SCENES = [
    ('氷の惑星', s20_ice, 6), ('英雄マン博士の目覚め', s21_mann, 4), ('裏切り', s22_betrayal, 6),
    ('ドッキングの暴走、爆発', s23_explosion, 4.5), ('回転に合わせてドッキング', s24_docking, 6), ('操縦かんを握る', s24b_cockpit, 3),
    ('ブラックホール「ガルガンチュア」', s25_gargantua, 6), ('ひとり切り離す', s26_detach, 6), ('ブラックホールの中へ', s27_fall, 6),
]
