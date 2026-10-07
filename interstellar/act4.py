from common import *
from act1 import farmhouse, corn

def s28_tesseract(t):                 # endless bookshelves, folded in space
    im, d = canvas((10, 8, 6))
    cx, cy = 192, 108
    for k in range(9, 0, -1):                    # receding frames
        s = 0.6 ** k * (1 + (t * 0.08) % 1 * 0.4)
        w, h = 520 * s, 300 * s
        col = mix((40, 30, 20), (210, 170, 110), 1 - k / 9)
        d.rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], outline=col)
        for j in range(1, 6): d.line([cx - w / 2 + j * w / 6, cy - h / 2, cx - w / 2 + j * w / 6, cy + h / 2], fill=shade(col, 0.7))
    for k in range(30):                          # golden threads
        a = k * 0.21; d.line([cx, cy, cx + math.cos(a) * 400, cy + math.sin(a) * 260], fill=(90, 70, 40))
    for x in range(0, W, 48):
        bookshelf(d, x + 4, 0, 40, 30, seed=x); bookshelf(d, x + 4, 186, 40, 30, seed=x + 1)
    astro(d, 192 + math.sin(t) * 6, 130 + math.cos(t * 0.8) * 4, 1, 'reach', visor=(140, 120, 90))
    return im

def s29_behind(t):                    # behind the shelf: the "ghost" was him
    im, d = zcanvas((14, 10, 8))
    R(d, 0, 0, ZW, ZH, (30, 22, 16))
    R(d, 40, 10, 150, 98, (90, 60, 40))
    R(d, 76, 34, 118, 66, (200, 170, 120))       # a gap through the books -> her room
    R(d, 76, 54, 118, 66, (150, 110, 74))
    person(d, 100, 64, 'murph', -1)
    for y in range(14, 98, 12):
        for x in range(42, 148, 4):
            if 74 < x < 120 and 30 < y < 68: continue
            R(d, x, y, x + 2, y + 9, [(170, 50, 40), (60, 90, 140), (200, 170, 90), (70, 120, 70), (140, 80, 140), (220, 210, 190)][(x // 4 * 7 + y // 12 * 3) % 6])
    push = clamp((t - 2) / 1.5)
    R(d, 120 - push * 6, 26, 123 - push * 6, 35, (170, 50, 40))
    astro(d, 170, 100, -1, 'reach', visor=(70, 90, 120), s=1.4)
    if t > 4: bubble(d, 150, 40, '!')
    return up(im)

def s30_watch(t):                     # the second hand ticks in Morse
    im, d = zcanvas((24, 18, 14))
    R(d, 0, 66, ZW, ZH, (90, 60, 40)); R(d, 0, 64, ZW, 66, (120, 84, 56))
    code = [1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1]
    k = int(t * 2.5) % len(code)
    jitter = 0.18 if code[k] else 0
    watch(d, 96, 46, 22, ang=jitter)
    for n in range(len(code)):                   # glowing dots / dashes
        x = 30 + n * 10
        if n <= k: R(d, x, 92, x + (6 if code[n] else 1), 94, (255, 220, 140))
    return up(im)

def s31_eureka(t):                    # grown Murph understands
    im, d = zcanvas(); 
    from common import zroom
    zroom(d, light=(255, 150, 70), dark=True)
    r = random.Random(int(t * 8))
    for k in range(20): d.point((120 + r.randrange(34), 18 + r.randrange(34)), fill=(255, 220, 120))
    portrait(d, 92, 108, 'murphA', 2, cry=t > 3, smile=t > 6)
    watch(d, 60, 92, 5, ang=t * 4)
    if t > 4: bubble(d, 112, 30, '!')
    return up(im)

def s32_papers(t):                    # papers in the air, the corn on fire
    im, d = canvas(); grad(d, 0, 140, (60, 30, 30), (230, 120, 60))
    r = random.Random(5)
    for k in range(40):
        x = r.randrange(W); h = 20 + r.randrange(40) + math.sin(t * 6 + k) * 6
        d.polygon([(x - 8, 150), (x, 150 - h), (x + 8, 150)], fill=r.choice([(255, 200, 60), (255, 140, 40), (230, 80, 30)]))
    corn(d, 146, 216, t, dark=0.6)
    farmhouse(d, 40, 176, 1.0)
    person(d, 230, 196, 'murphA', 1, 'arms_up')
    for k in range(18):                          # papers fluttering up
        a = k * 0.7 + t
        x = 230 + math.cos(a) * (20 + k * 3); y = 160 - (t * 12 + k * 9) % 120
        R(d, x, y, x + 4, y + 5, (250, 250, 240))
    return im

def s33_station(t):                   # Cooper Station: the world curves overhead
    im, d = canvas()
    grad(d, 0, H, (150, 196, 236), (190, 220, 240))
    for y in range(0, 56):                       # the far side of the cylinder, upside down
        d.line([0, y, W, y], fill=mix((100, 140, 84), (150, 196, 236), (y / 56) ** 2))
    for k in range(5):
        x = 20 + k * 80; R(d, x, 14, x + 26, 26, (214, 208, 196)); d.polygon([(x - 2, 26), (x + 13, 34), (x + 28, 26)], fill=(120, 76, 64))
        R(d, x + 34, 10, x + 40, 22, (60, 110, 60))
    for k in range(4): d.arc([-200 - k * 40, -180 + k * 6, 584 + k * 40, 110 + k * 6], 20, 160, fill=(130, 170, 120))
    grad(d, 160, H, (120, 160, 96), (96, 136, 80))
    for k in range(4):
        x = 30 + k * 90; R(d, x, 140, x + 40, 166, (232, 228, 216)); d.polygon([(x - 4, 140), (x + 20, 124), (x + 44, 140)], fill=(130, 80, 66))
        R(d, x + 16, 152, x + 24, 166, (120, 90, 70))
    bx, by = 60 + t * 30, 150 - math.sin(t * 0.8) * 100
    R(d, bx, by, bx + 2, by + 2, (255, 255, 255))
    person(d, 300, 196, 'cooper', -1); bubble(d, 296, 152, '?')
    return im

def s34_family(t):                    # old Murph, surrounded by her family
    im, d = zcanvas()
    grad(d, 0, ZH, (200, 210, 220), (160, 170, 182), 0, ZW)
    R(d, 30, 64, 130, 76, (236, 236, 236)); R(d, 30, 58, 130, 65, (190, 206, 222))
    R(d, 34, 52, 50, 62, (240, 240, 240)); R(d, 36, 52, 48, 60, SKIN); R(d, 35, 50, 49, 53, (225, 225, 225))
    for k, who in enumerate(['tomA', 'murphA', 'brand', 'tom', 'murph', 'cooper']):
        if who == 'cooper': continue
        person(d, 40 + k * 14, 100, who, 1)
    walk = clamp(t / 6)
    person(d, 180 - walk * 30, 100, 'cooperS', -1, 'walk' if walk < 1 else 'stand', f=t * 6)
    return up(im)

def s35_hands(t):                     # father, younger than his daughter
    im, d = zcanvas((40, 44, 56))
    grad(d, 0, ZH, (210, 196, 176), (150, 136, 120), 0, ZW)
    portrait(d, 54, 108, 'murphO', 2.2, grey=True, cry=t > 2, smile=t > 6)
    portrait(d, 140, 108, 'cooperS', 2.2, cry=t > 2)
    R(d, 82, 92, 112, 98, SKIN); R(d, 96, 90, 98, 100, shade(SKIN, .85))
    if t > 7: bubble(d, 90, 22, 'heart')
    return up(im)

def s36_depart(t):                    # he takes a ship and goes to find her
    im, d = canvas((2, 3, 10)); stars(d, 36, 200)
    R(d, 0, 170, W, H, (90, 100, 110))
    d.ellipse([-60, 150, 444, 250], fill=(110, 120, 130))
    k = clamp((t - 1) / 9)
    ranger(d, lerp(80, 420, k), lerp(150, 30, k), 1.0 - k * 0.5, 1, flame=True, f=int(t * 24))
    wormhole(d, 340, 40, 18, t)
    return im

def s37_edmunds(t):                   # Brand on the new world. Sunset.
    im, d = canvas(); grad(d, 0, 130, (60, 50, 90), (240, 150, 90))
    R(d, 250, 98, 290, 132, (255, 220, 160)) if False else d.ellipse([250, 96, 300, 146], fill=(255, 210, 140))
    d.polygon([(0, 128), (90, 118), (180, 126), (300, 116), (384, 124), (384, 216), (0, 216)], fill=(150, 100, 80))
    grad(d, 140, 216, (170, 112, 86), (120, 80, 64))
    for k in range(3): R(d, 40 + k * 26, 150, 60 + k * 26, 168, (200, 200, 196))
    R(d, 120, 150, 122, 172, (120, 90, 70)); R(d, 114, 156, 128, 158, (120, 90, 70))   # a simple grave marker
    person(d, 190, 176, 'brand', 1)
    R(d, 196, 174, 204, 178, (232, 232, 226))     # helmet set down on the ground
    if t > 5:
        k = clamp((t - 5) / 6)
        x = lerp(380, 300, k); y = lerp(10, 40, k)
        d.line([x, y, x + 20, y - 6], fill=(255, 255, 255)); d.point((x, y), fill=(255, 255, 220))
    return im

SCENES = [
    ('本棚の向こう側（テサラクト）', s28_tesseract, 5), ('「幽霊」の正体', s29_behind, 5), ('時計の針でメッセージを送る', s30_watch, 4),
    ('娘が気づく', s31_eureka, 7), ('ユリイカ', s32_papers, 4), ('目覚めたら宇宙ステーション', s33_station, 3),
    ('年老いた娘と家族', s34_family, 6), ('父と娘、ふたたび', s35_hands, 8), ('彼女を探しに', s36_depart, 5),
    ('新しい星の夕焼け', s37_edmunds, 9),
]
