from common import *

def earth_limb(d, t):
    for y in range(150, 216):
        w = math.sqrt(max(0, 900 ** 2 - (y - 1060) ** 2))
        d.line([192 - w, y, 192 + w, y], fill=mix((70, 130, 200), (30, 70, 140), (y - 150) / 66))
    r = random.Random(3)
    for k in range(40):
        x = (r.randrange(W) + t * 3) % W; y = 156 + r.randrange(60)
        R(d, x, y, x + r.randint(6, 20), y + 1, (230, 236, 240))
    for k in range(4): d.arc([192 - 900 - k, 160 - k, 192 + 900 + k, 1960 + k], 180, 360, fill=mix((170, 210, 255), (20, 30, 60), k / 4))

def s10_orbit(t):                     # Endurance in orbit; the Ranger docks
    im, d = canvas((4, 6, 14)); stars(d, 10, 160)
    earth_limb(d, t)
    endurance(d, 230, 80, 56, ang=t * 0.15, tilt=0.38)
    k = clamp(t / 9)
    ranger(d, lerp(20, 168, k), lerp(60, 76, k), 0.6)
    return im

def s11_saturn(t):                    # two years past Saturn
    im, d = canvas((2, 2, 8)); stars(d, 11, 140)
    saturn(d, 230, 110, 70)
    k = clamp(t / 12)
    endurance(d, lerp(60, 140, k), lerp(170, 150, k), 6, ang=t * 0.2, tilt=0.4)
    return im

def s12_wormhole(t):                  # the sphere in space
    im, d = canvas((2, 2, 8)); stars(d, 12, 200)
    r = int(40 + clamp(t / 12) * 60)
    wormhole(d, 220, 100, r, t)
    k = clamp(t / 12)
    endurance(d, lerp(60, 200, k), lerp(160, 104, k), 10 * (1 - k * 0.7), ang=t * 0.2, tilt=0.4)
    return im

def s13_inside(t):                    # a hand reaches out to a ripple in space
    im, d = zcanvas((10, 10, 20))
    r = random.Random(13)
    for k in range(160):                         # streaming light
        y = r.randrange(ZH); x = (r.randrange(ZW) - t * r.uniform(20, 80)) % ZW
        d.line([x, y, x + r.randint(3, 12), y], fill=mix((60, 70, 120), (220, 230, 255), r.random()))
    R(d, 0, 0, ZW, 10, (60, 60, 64)); R(d, 0, 98, ZW, ZH, (60, 60, 64))
    astro(d, 70, 92, 1, 'reach', visor=(120, 140, 160))
    for k in range(4):                           # ripple
        rr = 4 + k * 4 + (t * 6) % 4
        d.ellipse([84 - rr, 70 - rr * 0.7, 84 + rr, 70 + rr * 0.7], outline=mix((230, 240, 255), (60, 70, 120), k / 4))
    return up(im)

def ocean(d, y0, t, col0=(150, 180, 190), col1=(90, 130, 150)):
    grad(d, y0, H, col0, col1)
    r = random.Random(1)
    for k in range(90):
        y = y0 + r.randrange(H - y0); x = (r.randrange(W) + math.sin(t + k) * 3)
        d.line([x, y, x + 2 + (y - y0) // 12, y], fill=(200, 220, 225))

def s14_miller(t):                    # the water planet: knee-deep sea to the horizon
    im, d = canvas(); grad(d, 0, 110, (150, 160, 170), (196, 200, 200))
    for k in range(5):
        x = 30 + k * 80; d.polygon([(x - 30, 110), (x, 70 + (k % 2) * 10), (x + 30, 110)], fill=(150, 160, 166))
    ocean(d, 110, t)
    ranger(d, 70, 132, 0.9, -1)                   # the ship, left behind at a distance
    ox = 170 + t * 4
    astro(d, ox + 30, 172, 1, 'walk', f=t * 4); astro(d, ox, 178, 1, 'walk', f=t * 4 + 2)
    tars(d, ox - 40, 182, f=t * 4, walk=True)
    for x, y in ((ox + 30, 170), (ox, 176), (ox - 30, 180)):   # splashes at the shins
        d.line([x - 6, y, x + 6, y], fill=(230, 240, 240))
    return im

def s15_wave(t):                      # those aren't mountains...
    im, d = canvas(); grad(d, 0, 216, (150, 160, 170), (196, 200, 200))
    k = clamp(t / 10)
    top = 90 - k * 80
    for y in range(int(top), 200):
        q = (y - top) / max(1, 200 - top)
        x0 = 0; x1 = W
        d.line([x0, y, x1, y], fill=mix((120, 150, 166), (70, 100, 120), q))
    for x in range(0, W, 3):                     # foam crest
        R(d, x, top + math.sin(x * 0.1 + t * 3) * 2, x + 2, top + 2 + math.sin(x * 0.1 + t * 3) * 2, (230, 240, 240))
    ocean(d, 160, t)
    if t < 5:
        run = t * 42
        tars(d, 250 - run, 200, f=t * 12, walk=True); astro(d, 260 - run, 178, -1, s=0.8)
        astro(d, 300 - run, 196, -1, 'run', f=t * 10)
    return im

def s15a_wavewide(t):                 # wide: the "mountain" on the horizon rises and moves
    im, d = canvas(); grad(d, 0, 216, (150, 160, 170), (196, 200, 200))
    k = clamp(t / 7) ** 1.3
    top = 104 - k * 90
    for x in range(W):                            # "mountains" on the horizon that rise into one wall of water
        ridge = 22 * abs(math.sin(x * 0.018 + 0.6)) * (1 - k)
        h = top + ridge + math.sin(x * 0.07 + t * 2) * 1.5
        if h < 140:
            for y in range(int(h), 140): d.point((x, y), fill=mix((140, 166, 178), (70, 100, 120), (y - h) / max(1, 140 - h)))
            d.point((x, int(h)), fill=(230, 240, 240)); d.point((x, int(h) + 1), fill=(210, 226, 230))
    ocean(d, 140, t)
    ranger(d, 40, 168, 0.6, -1)
    run = max(0.0, t - 4.0) * 22
    for k2, x in enumerate((300, 314)): astro(d, x - run, 180, -1, 'run' if run else 'stand', f=t * 9 + k2, s=0.6)
    tars(d, 280 - run, 184, f=t * 9, walk=bool(run))
    return shake(im, 1 if t > 4 else 0, int(t * 24))

def s15c_tarsrun(t):                  # TARS wheels through the water carrying Brand back to the ship
    im, d = zcanvas()
    for y in range(0, 46): d.line([0, y, ZW, y], fill=mix((120, 146, 160), (70, 100, 120), y / 46))   # the wave wall behind
    for x in range(0, ZW, 2): R(d, x, 3 + math.sin(x * 0.2 + t * 4), x + 1, 4 + math.sin(x * 0.2 + t * 4), (230, 240, 240))
    grad(d, 46, ZH, (150, 180, 190), (100, 136, 154), 0, ZW)
    r0 = random.Random(1)
    for n in range(50):
        y = 46 + r0.randrange(62); x = (r0.randrange(ZW) + t * 30) % ZW; d.line([x, y, x + 2, y], fill=(205, 222, 228))
    ranger(d, 52, 74, 0.8, -1)
    boarded = t > 5.0
    if not boarded: astro(d, 60, 76, 1, 'reach', s=0.8)                            # Romilly at the hatch
    R(d, 52, 66, 58, 74, (40, 44, 50) if t < 5.6 else (190, 190, 186))             # hatch: open, then shut
    if boarded: return up(im)
    k = clamp(t / 5)
    cx = lerp(186, 70, k); gy = 92
    spin = -t * 8                                 # TARS on the move, slabs whirling like a wheel
    spr = Image.new('RGBA', (34, 34), (0, 0, 0, 0)); sd = ImageDraw.Draw(spr)
    for n in range(4):
        a = spin + n * math.pi / 2
        x2, y2 = 17 + math.cos(a) * 13, 17 + math.sin(a) * 13
        sd.line([17, 17, x2, y2], fill=(170, 172, 176) if n % 2 else (196, 198, 202), width=5)
    R(sd, 13, 13, 21, 21, (30, 34, 38)); R(sd, 14, 15, 18, 17, (120, 220, 255))
    im.paste(spr, (int(cx - 17), gy - 30), spr)
    paste_rot(im, astro_img(-1, 'stand', s=0.9, visor=(80, 110, 140)), cx - 2, gy - 27, -75)   # Brand, held above him
    d = ImageDraw.Draw(im)
    astro(d, cx + 30, gy + 8, -1, 'run', f=t * 10, s=1.0)                          # Cooper splashing after them
    r = random.Random(int(t * 12))
    for n in range(36):
        x = cx + 20 + r.randint(0, 40); y = gy + r.randint(-14, 8); R(d, x, y, x + 1, y + 1, (232, 242, 244))
    return up(im)

def helmet_face(d, cx, by, who, s=2, tint=(40, 50, 64), refl=None, **kw):
    """Face seen through a round space-helmet visor."""
    im = d._image
    R(d, cx - 22 * s, by - 8 * s, cx + 22 * s, by, (232, 232, 226))                       # shoulders
    R(d, cx - 22 * s, by - 8 * s, cx - 14 * s, by, (196, 198, 192))
    d.ellipse([cx - 17 * s, by - 44 * s, cx + 17 * s, by - 4 * s], fill=(232, 232, 226))  # helmet shell
    d.ellipse([cx - 17 * s, by - 44 * s, cx - 4 * s, by - 4 * s], fill=(204, 206, 200))
    d.ellipse([cx - 13 * s, by - 39 * s, cx + 13 * s, by - 10 * s], fill=tint)          # visor
    face = Image.new('RGB', im.size, tint); fd = ImageDraw.Draw(face)
    portrait(fd, cx, by - 6 * s, who, s, **kw)
    mask = Image.new('L', im.size, 0)
    ImageDraw.Draw(mask).ellipse([cx - 12 * s, by - 38 * s, cx + 12 * s, by - 11 * s], fill=255)
    im.paste(face, (0, 0), mask)
    if refl:
        for k in range(3): R(d, cx + (5 + k * 2) * s, by - (34 - k * 3) * s, cx + (8 + k * 2) * s, by - (33 - k * 3) * s, refl)
    R(d, cx - 4 * s, by - 9 * s, cx + 4 * s, by - 7 * s, (150, 150, 146))

def s15b_lookup(t):                   # close-up: Cooper looks up at the wave
    im, d = zcanvas()
    k = clamp(t / 4)
    grad(d, 0, ZH, mix((150, 160, 170), (80, 110, 130), k), mix((120, 140, 156), (50, 80, 100), k), 0, ZW)
    for x in range(0, ZW, 2): R(d, x, 6 + k * 4 + math.sin(x * 0.2 + t * 4), x + 1, 7 + k * 4, (230, 240, 240))
    helmet_face(d, 96, 108, 'cooperS', 2, refl=(200, 220, 230), shock=True)
    return shake(up(im), 2 if t > 2 else 0, int(t * 24))

def s16_escape(t):                    # liftoff as the wave breaks
    im, d = canvas(); grad(d, 0, 216, (150, 160, 170), (196, 200, 200))
    k = t / 8
    wx = 384 - k * 260
    for y in range(10, 216):                     # wall of water arriving from the right
        q = (y - 10) / 206
        edge = wx - math.sin(q * 2.6) * 50
        d.line([edge, y, W, y], fill=mix((120, 150, 166), (60, 90, 110), q))
        R(d, edge, y, edge + 2, y, (220, 236, 240))
    ocean(d, 186, t)
    k2 = max(0.0, (t - 2) / 6) ** 1.5
    ry = 176 - k2 * 150
    ranger(d, 170 - k2 * 140, ry, 1.2, -1, flame=t > 2, f=int(t * 24))
    r = random.Random(int(t * 10))
    for n in range(70):
        y = r.randint(40, 216); x = wx - math.sin((y - 10) / 206 * 2.6) * 50 - r.randint(2, 30)
        R(d, x, y, x + 2, y + 1, (226, 238, 242))
    return im

def ship_interior(d, dark=False):
    grad(d, 0, ZH, (70, 74, 80), (46, 48, 54), 0, ZW)
    for x in range(0, ZW, 24): R(d, x, 0, x + 1, ZH, (90, 94, 100))
    R(d, 0, 86, ZW, ZH, (60, 62, 68)); R(d, 0, 86, ZW, 87, (110, 112, 118))
    R(d, 120, 14, 180, 50, (10, 10, 20)); stars_box(d, 120, 14, 180, 50)

def stars_box(d, x0, y0, x1, y1, seed=2):
    r = random.Random(seed)
    for k in range(40): d.point((r.randint(x0, x1), r.randint(y0, y1)), fill=(220, 220, 240))

def s17_23years(t):                   # back aboard: Romilly has aged 23 years
    im, d = zcanvas(); ship_interior(d)
    walk = clamp((t - 4.5) / 3.0)
    hug = t > 7.5
    cx = lerp(62, 141, walk)
    if hug:                                       # a long, gentle hug
        sway = math.sin((t - 7.5) * 1.5) * 0.6
        person(d, 141 + sway, 100, 'cooperS', 1, 'reach')
        person(d, 150 + sway, 100, 'romillyO', -1, 'reach', cry=clamp((t - 8) / 3))
    else:
        person(d, 150, 100, 'romillyO', -1, 'stand' if t < 6.5 else 'reach')
        person(d, cx if t > 4.5 else 62 - clamp((t - 2) / 1) * 4, 100, 'cooperS', 1, 'walk' if 0 < walk < 1 else 'stand', f=t * 6, shock=2 < t < 4.5)
    person(d, 40, 100, 'brand', 1, 'cover' if 2.5 < t < 8 else 'stand', shock=2 < t < 4.5)
    # hourglass
    hx, hy = 100, 30
    d.polygon([(hx - 6, hy - 8), (hx + 6, hy - 8), (hx, hy)], fill=(230, 220, 180)); d.polygon([(hx - 6, hy + 8), (hx + 6, hy + 8), (hx, hy)], fill=(230, 220, 180))
    k = clamp(t / 6)
    d.polygon([(hx - 6 * (1 - k), hy - 8 * (1 - k)), (hx + 6 * (1 - k), hy - 8 * (1 - k)), (hx, hy)], fill=(200, 160, 80))
    d.polygon([(hx - 6 * k, hy + 8 - 8 * k), (hx + 6 * k, hy + 8 - 8 * k), (hx + 6, hy + 8), (hx - 6, hy + 8)], fill=(200, 160, 80))
    R(d, hx - 7, hy - 9, hx + 7, hy - 8, (120, 90, 60)); R(d, hx - 7, hy + 8, hx + 7, hy + 9, (120, 90, 60))
    return up(im)

def s18_messages(t):                  # 23 years of messages from home, one after another
    im, d = zcanvas((20, 20, 26))
    lean = clamp((t - 1) / 3) * 6
    sx0, sx1 = 24, 140
    R(d, sx0, 10, sx1, 84, (40, 40, 46)); R(d, sx0 + 4, 14, sx1 - 4, 80, (60, 70, 80))
    CLIP = 3.2
    k = min(3, int(t / CLIP)); lt = t - k * CLIP
    grad(d, 14, 80, (130, 116, 100), (96, 84, 72), sx0 + 4, sx1 - 4)
    who, kw = [('tom', {}), ('tomA', {}), ('tomA', dict(beard=(150, 110, 60))), ('murphA', {})][k]
    talk = int(t * 7) % 3 != 0 and lt > 0.3
    bob = math.sin(t * 2.3) * 1.2
    if k == 3: kw = dict(cry=clamp((lt - 1.5) / 3), shock=False)
    portrait(d, 82 + (math.sin(t * 1.3) * 2 if k == 3 else 0), 80 + bob + (4 if k == 3 and lt > 1 else 0), who, 2 if k < 3 else 2.2, talk=talk, **kw)
    yy = 14 + int(t * 20) % 66; d.line([sx0 + 4, yy, sx1 - 4, yy], fill=(120, 126, 134))
    if lt < 0.3 and t > 0.3:                      # static between clips
        r = random.Random(int(t * 40))
        for n in range(500): d.point((r.randint(sx0 + 4, sx1 - 4), r.randint(14, 80)), fill=r.choice([(200, 200, 200), (90, 90, 90), (30, 30, 30)]))
    R(d, sx0 + 6, 16, sx0 + 9, 19, (230, 50, 50) if int(t * 2) % 2 else (90, 30, 30))       # rec light
    out = up(im)
    out = glow(out, 164, 96, 90, (120, 140, 170), 0.25)                                     # screen light on his face
    d2 = ImageDraw.Draw(out)
    pim, pd = zcanvas((0, 0, 0)); pim = pim.convert('RGBA'); pim.putalpha(0); pd = ImageDraw.Draw(pim)
    portrait(pd, 172 - lean, 108, 'cooperS', 1.6, cry=clamp((t - 4) / 7))
    if t > 11.5: R(pd, 160 - lean, 92, 172 - lean, 98, SKIN)                                 # hand to his mouth
    big = pim.resize((W, H), Image.NEAREST); out.paste(big, (0, 0), big)
    return out

def s19_murph(t):                     # Earth: Murph works the equation; the professor slips away
    im, d = zcanvas()
    grad(d, 0, ZH, (90, 96, 110), (60, 64, 74), 0, ZW)
    R(d, 10, 14, 90, 60, (34, 50, 40)); R(d, 10, 14, 90, 15, (120, 100, 70))
    r = random.Random(19)
    lines = int(clamp(t / 4) * 8) if t < 4.5 else 8
    for k in range(8):
        y = 20 + k * 5; x = 14; pts = [(x, y)]
        for _ in range(10): x += r.randint(3, 7); pts.append((x, y + r.randint(-2, 2)))
        if k < lines: d.line(pts, fill=(230, 230, 220))
        elif k == lines and t < 4.5:
            n = int((t / 4 * 8 - lines) * 10); d.line(pts[:max(2, n)], fill=(230, 230, 220))
    # bed + professor
    R(d, 110, 76, 180, 86, (220, 220, 220)); R(d, 110, 70, 180, 77, (180, 200, 220)); R(d, 112, 86, 114, 100, (150, 150, 150)); R(d, 176, 86, 178, 100, (150, 150, 150))
    R(d, 112, 66, 124, 74, (240, 240, 240)); R(d, 114, 64, 122, 70, SKIN); R(d, 113, 63, 123, 65, (220, 220, 220))
    R(d, 116, 66, 120, 67, (40, 40, 40))
    # heart monitor
    R(d, 150, 40, 182, 60, (20, 24, 26)); R(d, 151, 41, 181, 59, (10, 30, 20))
    alive = t < 7.5
    for x in range(152, 181):
        ph = (x - 152 + t * 30) % 22
        y = 50 - (8 if alive and 10 < ph < 12 else 0) + (3 if alive and 12 <= ph < 13 else 0)
        d.point((x, y), fill=(90, 255, 140) if alive else (255, 90, 90))
    # Murph: at the board, then at his side
    if t < 4.5:
        arm = 'reach' if int(t * 4) % 2 else 'stand'
        person(d, 60, 100, 'murphA', -1, arm)
    elif t < 5.8:
        k = (t - 4.5) / 1.3
        person(d, lerp(60, 128, k), 100, 'murphA', 1, 'run', f=t * 10)
    else:
        if t < 7.5: person(d, 128, 100, 'murphA', 1, 'reach')
        else:
            back = clamp((t - 8) / 1.0) * 10
            person(d, 128 - back, 100, 'murphA', 1, 'cover' if t > 8 else 'stand', cry=clamp((t - 8.5) / 4), shock=t > 8)
    if 5.8 < t < 7.5: R(d, 123, 72, 127, 75, SKIN)        # his hand lifts to hers
    return up(im)

SCENES = [
    ('宇宙船エンデュランス', s10_orbit, 6), ('土星を越えて', s11_saturn, 6), ('ワームホール', s12_wormhole, 8),
    ('ワームホールの中', s13_inside, 4), ('水の惑星', s14_miller, 4), ('「山」ではなかった', s15_wave, 6), ('波を見上げる', s15b_lookup, 3),
    ('間一髪の脱出', s16_escape, 5), ('23年が過ぎていた', s17_23years, 4), ('届いていたビデオ', s18_messages, 12),
    ('地球：大人になった娘', s19_murph, 7),
]
