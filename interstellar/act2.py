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
    ranger(d, 230, 140, 1.4, -1)
    for k in range(2): R(d, 210 + k * 60, 140, 214 + k * 60, 146, (180, 180, 176))
    astro(d, 140 + t * 2, 172, 1, 'walk', f=t * 4); astro(d, 110 + t * 2, 178, 1, 'walk', f=t * 4 + 2)
    tars(d, 70 + t * 2, 182, f=t * 4, walk=True)
    for x in (140, 110, 80):                     # splashes at the shins
        d.line([x + t * 2 - 6, 170 + (x == 110) * 6, x + t * 2 + 6, 170 + (x == 110) * 6], fill=(230, 240, 240))
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
    ranger(d, 250, 170, 1.2, -1)
    astro(d, 190 + t * 3, 196, 1, 'run', f=t * 8)
    tars(d, 150 + t * 4, 200, f=t * 10, walk=True); astro(d, 160 + t * 4, 178, -1, s=0.8)
    if t > 1: bubble(d, 196, 150, '!')
    return im

def s16_escape(t):                    # liftoff as the wave breaks
    im, d = canvas(); grad(d, 0, 216, (150, 160, 170), (196, 200, 200))
    k = clamp(t / 8)
    wx = 384 - k * 260
    for y in range(10, 216):                     # wall of water arriving from the right
        q = (y - 10) / 206
        edge = wx - math.sin(q * 2.6) * 50
        d.line([edge, y, W, y], fill=mix((120, 150, 166), (60, 90, 110), q))
        R(d, edge, y, edge + 2, y, (220, 236, 240))
    ocean(d, 186, t)
    ry = 176 - clamp((t - 2) / 6) ** 1.5 * 160
    ranger(d, 130, ry, 1.2, 1, flame=t > 2, f=int(t * 24))
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
    portrait(d, 150, 100, 'romillyO', 2)
    person(d, 62, 100, 'cooperS', 1); person(d, 42, 100, 'brand', 1)
    if t > 3: bubble(d, 56, 58, '!')
    # hourglass
    hx, hy = 100, 30
    d.polygon([(hx - 6, hy - 8), (hx + 6, hy - 8), (hx, hy)], fill=(230, 220, 180)); d.polygon([(hx - 6, hy + 8), (hx + 6, hy + 8), (hx, hy)], fill=(230, 220, 180))
    k = clamp(t / 6)
    d.polygon([(hx - 6 * (1 - k), hy - 8 * (1 - k)), (hx + 6 * (1 - k), hy - 8 * (1 - k)), (hx, hy)], fill=(200, 160, 80))
    d.polygon([(hx - 6 * k, hy + 8 - 8 * k), (hx + 6 * k, hy + 8 - 8 * k), (hx + 6, hy + 8), (hx - 6, hy + 8)], fill=(200, 160, 80))
    R(d, hx - 7, hy - 9, hx + 7, hy - 8, (120, 90, 60)); R(d, hx - 7, hy + 8, hx + 7, hy + 9, (120, 90, 60))
    return up(im)

def s18_messages(t):                  # 23 years of messages from home
    im, d = zcanvas((20, 20, 26))
    R(d, 24, 10, 140, 84, (40, 40, 46)); R(d, 28, 14, 136, 80, (60, 70, 80))
    k = min(3, int(t / 3.2))
    grad(d, 14, 80, (130, 116, 100), (96, 84, 72), 28, 136)
    who, kw = [('tom', {}), ('tomA', {}), ('tomA', dict(beard=(150, 110, 60))), ('murphA', dict(cry=True))][k]
    portrait(d, 82, 80, who, 2, **kw)
    for y in range(14, 80, 3): d.line([28, y, 136, y], fill=(70, 76, 84)) if (y + int(t * 30)) % 9 == 0 else None
    portrait(d, 172, 108, 'cooperS', 1.6, cry=True)
    return up(im)

def s19_murph(t):                     # on Earth: grown-up Murph at the professor's bedside
    im, d = zcanvas()
    grad(d, 0, ZH, (90, 96, 110), (60, 64, 74), 0, ZW)
    R(d, 10, 14, 90, 60, (34, 50, 40)); R(d, 10, 14, 90, 15, (120, 100, 70))
    r = random.Random(19)
    for k in range(8):
        y = 20 + k * 5; x = 14; pts = [(x, y)]
        for _ in range(10): x += r.randint(3, 7); pts.append((x, y + r.randint(-2, 2)))
        d.line(pts, fill=(230, 230, 220))
    R(d, 110, 76, 180, 86, (220, 220, 220)); R(d, 110, 70, 180, 77, (180, 200, 220)); R(d, 112, 86, 114, 100, (150, 150, 150)); R(d, 176, 86, 178, 100, (150, 150, 150))
    R(d, 112, 66, 124, 74, (240, 240, 240)); R(d, 114, 64, 122, 70, SKIN); R(d, 113, 63, 123, 65, (220, 220, 220))
    person(d, 100, 100, 'murphA', 1, cry=t > 5)
    if t > 6: bubble(d, 92, 56, '!')
    return up(im)

SCENES = [
    ('宇宙船エンデュランス', s10_orbit, 6), ('土星を越えて', s11_saturn, 6), ('ワームホール', s12_wormhole, 8),
    ('ワームホールの中', s13_inside, 4), ('水の惑星', s14_miller, 4), ('「山」ではなかった', s15_wave, 6),
    ('間一髪の脱出', s16_escape, 5), ('23年が過ぎていた', s17_23years, 4), ('届いていたビデオ', s18_messages, 12),
    ('地球：大人になった娘', s19_murph, 7),
]
