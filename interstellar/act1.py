from common import *

def s01_farm(t):                      # dusty dawn on the farm
    im, d = canvas(); grad(d, 0, 110, (200, 170, 130), (236, 206, 150))
    R(d, 250, 40, 266, 56, (255, 236, 190))
    for k in range(5): R(d, (k * 90 + t * 4) % 420 - 30, 30 + k * 12, (k * 90 + t * 4) % 420 + 30, 33 + k * 12, (214, 184, 140))
    d.polygon([(0, 112), (80, 100), (180, 106), (300, 98), (384, 108), (384, 116), (0, 116)], fill=(170, 150, 110))
    corn(d, 114, 216, t)
    farmhouse(d, 40, 140, 1.0)
    R(d, 26, 100, 30, 140, (80, 70, 60)); R(d, 20, 96, 36, 100, (90, 80, 70))  # windmill pole
    a = t * 2
    for k in range(4): d.line([28, 96, 28 + math.cos(a + k * 1.57) * 12, 96 + math.sin(a + k * 1.57) * 12], fill=(90, 80, 70))
    R(d, 110, 138, 200, 142, (150, 120, 80))
    truck(d, 120, 142, 1, f=t)
    person(d, 186, 142, 'cooper', -1)
    r = random.Random(int(t * 6))
    for k in range(60): d.point((r.randrange(W), r.randrange(H)), fill=(220, 200, 160))
    return im

def s02_dust(t):                      # the dust wall over the ball game
    im, d = canvas(); grad(d, 0, 120, (150, 170, 190), (210, 200, 180))
    R(d, 0, 120, W, H, (110, 140, 70)); d.polygon([(130, 216), (192, 150), (254, 216)], fill=(190, 150, 100))
    for k in range(4): R(d, 60 + k * 8, 100 + k * 6, 160, 104 + k * 6, (170, 170, 170))
    for k in range(4): R(d, 60 + k * 8, 104 + k * 6, 160 + k * 0, 106 + k * 6, (120, 120, 120))
    for k in range(6): person(d, 70 + k * 14, 100 + (k % 4) * 6, ['cooper', 'tom', 'murph', 'donald', 'tom', 'murph'][k], 1)
    wx = 384 - t * 22
    for y in range(0, 216, 2):
        edge = wx + math.sin(y * 0.08 + t * 2) * 10 + math.sin(y * 0.21) * 5
        d.line([edge, y, W, y], fill=mix((150, 110, 70), (110, 80, 50), y / 216))
        for k in range(3): d.point((edge - k * 3 - (y * 7) % 5, y), fill=(170, 130, 90))
    for k in range(6):
        px = 200 + k * 16 - t * 18 * (k % 2 + 1)
        person(d, px, 190 + (k % 3) * 8, ['tom', 'murph', 'cooper', 'donald', 'tom', 'cooper'][k], -1, 'run', f=t * 8 + k)
    return im

def s03_ghost(t):                     # Murph's room: fallen book, dust lines
    im, d = zcanvas(); zroom(d, dust=1.0, t=t)
    for k in range(int(clamp(t / 4) * 9)):       # dust stripes appear on the floor
        x0 = 70 + k * 9
        d.line([x0, 78, x0 - 14, 107], fill=(212, 178, 128))
    by = min(86, 42 + t * 60) if t < 0.9 else 86
    R(d, 24, by, 30, by + 3, (170, 50, 40))
    person(d, 96, 100, 'murph', -1); person(d, 118, 102, 'cooper', -1)
    if t > 3: bubble(d, 88, 64, '?')
    return up(im)

def s04_drone(t):                     # chasing the drone through the corn
    im, d = canvas(); grad(d, 0, 110, (150, 190, 220), (220, 220, 200))
    for k in range(3): R(d, (k * 140 - t * 6) % 440 - 40, 20 + k * 10, (k * 140 - t * 6) % 440 + 20, 24 + k * 10, (240, 240, 240))
    d.polygon([(0, 104), (120, 96), (260, 102), (384, 94), (384, 112), (0, 112)], fill=(120, 140, 110))
    corn(d, 110, 216, t, scroll=t * 120)
    dx, dy = 230 + math.sin(t * 0.8) * 20, 40 + math.sin(t * 1.3) * 6
    R(d, dx - 40, dy, dx + 40, dy + 2, (40, 50, 80))
    for k in range(-40, 40, 6): d.line([dx + k, dy, dx + k, dy + 2], fill=(80, 100, 140))
    R(d, dx - 6, dy - 3, dx + 6, dy + 4, (180, 180, 176)); R(d, dx - 2, dy + 4, dx + 2, dy + 6, (60, 60, 60))
    R(d, 0, 158, W, 166, (170, 140, 100))
    tx = 150 + math.sin(t * 3) * 4
    truck(d, tx, 168, 1, col=(90, 110, 130), f=t)
    person(d, tx + 28, 158, 'tom', 1); person(d, tx + 10, 154, 'murph', 1, 'wave')
    r = random.Random(int(t * 10))
    for k in range(40): R(d, tx - r.randint(0, 120), 160 + r.randint(-6, 6), tx - r.randint(0, 120) + 2, 162 + r.randint(-6, 6), (200, 180, 140))
    return im

def s05_coords(t):                    # following the dust coordinates to a secret base
    im, d = canvas(); grad(d, 0, 140, (10, 12, 30), (40, 40, 70)); stars(d, 1, 120, 120, tw=int(t * 4))
    R(d, 0, 140, W, H, (30, 30, 34))
    for k in range(2):
        a = math.sin(t * 0.8 + k * 2) * 0.5
        sx = 250 + k * 80
        d.polygon([(sx, 132), (sx + math.sin(a) * 200 - 14, 0), (sx + math.sin(a) * 200 + 14, 0)], fill=(70, 70, 90))
    R(d, 200, 100, 384, 140, (60, 60, 70))
    for x in range(200, 384, 10): d.line([x, 120, x, 140], fill=(140, 140, 150))
    d.line([200, 122, 384, 122], fill=(140, 140, 150)); d.line([200, 130, 384, 130], fill=(140, 140, 150))
    for k in range(5): R(d, 210 + k * 34, 104, 222 + k * 34, 110, (230, 220, 150))
    tx = 40 + t * 8
    truck(d, tx, 170, 1, col=(90, 110, 130), f=t)
    d.polygon([(tx + 42, 166), (tx + 140, 156), (tx + 140, 176)], fill=(80, 78, 64))
    if t > 6:                                    # caught in a searchlight
        d.polygon([(250, 0), (tx - 10, 176), (tx + 60, 176), (290, 0)], fill=(150, 150, 130))
        truck(d, tx, 170, 1, col=(150, 170, 190), f=t)
    return im

def s06_nasa(t):                      # NASA hidden in a silo; the professor's plan
    im, d = canvas((30, 34, 40)); grad(d, 0, H, (40, 46, 56), (20, 22, 28))
    for x in (60, 324):
        for y in range(0, 216, 12): R(d, x - 2, y, x + 2, y + 6, (80, 86, 96))
    R(d, 150, 10, 234, 216, (24, 26, 32))
    k = clamp(t / 10)
    ry = 20 - k * 10
    R(d, 176, ry + 20, 208, 200, (220, 220, 214)); R(d, 176, ry + 20, 186, 200, (190, 190, 184))
    d.polygon([(176, ry + 20), (192, ry), (208, ry + 20)], fill=(230, 230, 224))
    R(d, 168, 160, 176, 200, (200, 200, 194)); R(d, 208, 160, 216, 200, (200, 200, 194))
    R(d, 182, 60, 202, 64, (60, 80, 160))
    R(d, 0, 196, W, H, (60, 64, 70))
    R(d, 250, 120, 370, 180, (34, 50, 40)); R(d, 250, 120, 370, 122, (120, 100, 70))
    r = random.Random(4)
    for k in range(int(clamp(t / 6) * 9)):
        y = 128 + k * 5; x = 256; pts = [(x, y)]
        for _ in range(12): x += r.randint(3, 8); pts.append((x, y + r.randint(-2, 2)))
        d.line(pts, fill=(230, 230, 220))
    person(d, 300, 200, 'prof', -1, 'reach'); person(d, 120, 200, 'cooper', 1); person(d, 90, 200, 'brand', 1)
    tars(d, 40, 200)
    return im

def s07_goodbye(t):                   # the watch, the turned back
    im, d = zcanvas(); zroom(d, light=(250, 196, 136))
    person(d, 86, 100, 'murph', -1, cry=True)
    person(d, 116, 102, 'cooper', -1, 'give' if t < 7 else 'stand')
    if t < 7: watch(d, 104, 84, 2)
    else: watch(d, 176, 54, 2, ang=t)            # left on the bed
    return up(im)

def s08_leave(t):                     # driving off; she runs out too late
    im, d = canvas(); grad(d, 0, 120, (210, 180, 140), (230, 200, 150))
    corn(d, 120, 216, t)
    R(d, 0, 158, W, 170, (170, 140, 100))
    farmhouse(d, 260, 158, 1.1)
    tx = 210 - t * 16
    truck(d, tx, 170, -1, col=(120, 90, 60), f=t)
    r = random.Random(int(t * 10))
    for k in range(50): R(d, tx + r.randint(0, 160), 158 + r.randint(-14, 8), tx + r.randint(0, 160) + 3, 161 + r.randint(-14, 8), (210, 190, 150))
    if t > 6: person(d, 276 - (t - 6) * 14, 170, 'murph', -1, 'run', f=t * 8, cry=True)
    person(d, 340, 170, 'donald', -1); person(d, 320, 170, 'tom', -1, 'wave')
    return im

def s09_launch(t):                    # liftoff
    im, d = canvas(); grad(d, 0, H, (90, 130, 190), (230, 190, 150))
    k = clamp((t - 2) / 10) ** 1.6
    ry = 80 - k * 260
    r = random.Random(int(t * 12))
    for n in range(160):                         # smoke billows
        a = r.uniform(math.pi, 2 * math.pi); rr = r.uniform(0, 90) * clamp((t - 1.5) / 3)
        cx = 192 + math.cos(a) * rr * 1.6; cy = 190 + math.sin(a) * rr * 0.4
        R(d, cx - 6, cy - 4, cx + 6, cy + 4, mix((240, 240, 236), (180, 180, 176), r.random()))
    R(d, 120, 186, 264, 216, (90, 90, 96))
    R(d, 214, 60, 222, 186, (130, 60, 50))
    if t > 1.8:
        fl = 30 + (int(t * 24) % 3) * 6
        d.polygon([(182, ry + 106), (192, ry + 106 + fl * 2), (202, ry + 106)], fill=(255, 200, 80))
        d.polygon([(186, ry + 106), (192, ry + 106 + fl), (198, ry + 106)], fill=(255, 250, 220))
    R(d, 182, ry + 20, 202, ry + 106, (230, 230, 226)); R(d, 182, ry + 20, 188, ry + 106, (196, 196, 190))
    d.polygon([(182, ry + 20), (192, ry), (202, ry + 20)], fill=(236, 236, 230))
    R(d, 176, ry + 80, 182, ry + 106, (200, 200, 196)); R(d, 202, ry + 80, 208, ry + 106, (200, 200, 196))
    return im

SCENES = [
    ('砂ぼこりの農場', s01_farm, 4), ('砂嵐が来る', s02_dust, 5), ('娘の部屋の「幽霊」', s03_ghost, 6),
    ('ドローンを追う', s04_drone, 5), ('砂の座標が示す場所へ', s05_coords, 8), ('隠されたNASA', s06_nasa, 8),
    ('時計を渡す別れ', s07_goodbye, 4), ('間に合わなかった娘', s08_leave, 8), ('打ち上げ', s09_launch, 7),
]
