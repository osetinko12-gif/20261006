"""Shared drawing kit for the Interstellar 8-min piece. 384x216 canvas (SNES-ish), x5 -> 1080p."""
import math, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'reel'))
from PIL import Image, ImageDraw
from engine import lerp, clamp, mix, osc, freq, Track, SR

W, H, FPS = 384, 216, 24

def canvas(col=(0, 0, 0)):
    im = Image.new('RGB', (W, H), col); return im, ImageDraw.Draw(im)

def grad(d, y0, y1, c0, c1, x0=0, x1=W):
    for y in range(int(y0), int(y1)):
        d.line([x0, y, x1, y], fill=mix(c0, c1, (y - y0) / max(1, y1 - y0)))

def stars(d, seed, n, y1=H, tw=0, col=(230, 230, 255)):
    r = random.Random(seed)
    for k in range(n):
        x, y = r.randrange(W), r.randrange(int(y1)); b = r.random()
        if tw and (k + tw) % 9 == 0: continue
        c = mix((60, 60, 90), col, b)
        d.point((x, y), fill=c)
        if b > 0.93: d.point((x + 1, y), fill=c); d.point((x - 1, y), fill=c); d.point((x, y + 1), fill=c); d.point((x, y - 1), fill=c)

def R(d, x0, y0, x1, y1, c):
    d.rectangle([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], fill=c)

def shade(c, k): return tuple(max(0, min(255, int(v * k))) for v in c)

# ------------------------------------------------------------------ people
SKIN = (236, 188, 150)
CAST = {
    # Cooper: wavy brown hair swept back, stubble, brown canvas jacket over a chambray shirt, jeans
    'cooper':  dict(hair=(104, 74, 46), top=(146, 112, 72), inner=(132, 162, 192), bot=(62, 74, 104), h=30, stubble=True),
    'cooperS': dict(hair=(104, 74, 46), top=(178, 166, 132), inner=(150, 140, 110), bot=(150, 140, 110), h=30, stubble=True),   # crew uniform
    # young Murph: long straight brown hair
    'murph':   dict(hair=(96, 58, 34), top=(116, 128, 84), bot=(70, 70, 90), h=20, long=True),
    # adult Murph: long auburn-red hair
    'murphA':  dict(hair=(172, 72, 40), top=(70, 80, 100), bot=(50, 50, 64), h=29, long=True),
    'murphO':  dict(hair=(232, 232, 232), top=(236, 236, 240), bot=(236, 236, 240), h=29, long=True),
    'tom':     dict(hair=(118, 84, 52), top=(176, 64, 52), bot=(70, 74, 92), h=24),
    # adult Tom: dark brown hair and beard
    'tomA':    dict(hair=(70, 50, 34), top=(120, 96, 66), bot=(70, 74, 92), h=30, beard=(70, 50, 34)),
    # Professor Brand: white hair, glasses, dark suit
    'prof':    dict(hair=(226, 226, 226), top=(58, 58, 68), inner=(220, 220, 220), bot=(54, 54, 62), h=29, glasses=True),
    # Amelia Brand: dark brown hair pulled back into a ponytail, crew uniform
    'brand':   dict(hair=(64, 42, 28), top=(178, 166, 132), bot=(150, 140, 110), h=28, ponytail=True),
    # Romilly: Black, short black hair, crew uniform
    'romilly': dict(hair=(26, 22, 20), skin=(122, 80, 54), top=(178, 166, 132), bot=(150, 140, 110), h=29),
    # Romilly after 23 years: grey hair, full grey beard
    'romillyO': dict(hair=(190, 190, 186), skin=(122, 80, 54), top=(178, 166, 132), bot=(150, 140, 110), h=29, beard=(196, 196, 192)),
    'doyle':   dict(hair=(120, 90, 60), top=(178, 166, 132), bot=(150, 140, 110), h=30),
    # Mann: short brown hair, scruffy beard
    'mann':    dict(hair=(116, 86, 58), top=(178, 166, 132), bot=(150, 140, 110), h=30, beard=(120, 92, 64)),
    # Donald (grandfather): white hair, glasses, plaid shirt
    'donald':  dict(hair=(230, 230, 230), top=(150, 70, 60), bot=(80, 70, 60), h=28, glasses=True),
}

def person(d, x, y, who='cooper', face=1, pose='stand', f=0, beard=None, cry=False, tilt=0):
    """x = centre, y = feet."""
    c = CAST[who]; h = c['h']; s = h / 30
    sk = c.get('skin', SKIN); beard = beard or c.get('beard')
    X = lambda dx: x + dx * face * s
    Y = lambda dy: y - dy * s
    def B(a, b, cc, e, col): R(d, X(a), Y(b), X(cc), Y(e), col)
    top, bot, hair = c['top'], c['bot'], c['hair']
    # legs
    if pose == 'walk' or pose == 'run':
        ph = [2, 0, -2, 0][int(f) % 4] * (1.6 if pose == 'run' else 1)
        B(-2 + ph, 0, -0.5 + ph, 11, bot); B(0.5 - ph, 0, 2 - ph, 11, shade(bot, .8))
        B(-2 + ph, 0, 0 + ph, 1, (40, 34, 30)); B(0.5 - ph, 0, 2.5 - ph, 1, (40, 34, 30))
    elif pose == 'sit':
        B(-2, 6, 6, 9, bot); B(4, 0, 6, 6, bot); B(4, 0, 7, 1, (40, 34, 30))
    elif pose == 'lie':
        return lie(d, x, y, who, face)
    else:
        B(-2.5, 0, -0.5, 11, bot); B(0.5, 0, 2.5, 11, shade(bot, .8))
        B(-2.5, 0, -0.5, 1, (40, 34, 30)); B(0.5, 0, 3, 1, (40, 34, 30))
    # torso
    B(-3.5, 10, 3.5, 21, top); B(-3.5, 10, -1.5, 21, shade(top, .82))
    if c.get('inner'): B(0, 20.5, 2.5, 11, c['inner'])
    # arms
    if pose in ('reach', 'give'):
        B(2.5, 19, 9, 17, top); B(9, 19, 10.5, 17, sk)
    elif pose == 'wave':
        B(2.5, 20, 4.5, 28, top); B(3, 28, 4.5, 30, sk)
    elif pose == 'arms_up':
        B(-5, 20, -3.5, 28, top); B(3.5, 20, 5, 28, top); B(-5, 28, -3.5, 30, sk); B(3.5, 28, 5, 30, sk)
    elif pose == 'run':
        sw = [3, 0, -3, 0][int(f) % 4]
        B(1 + sw, 19, 3 + sw, 13, top); B(-3 - sw, 19, -1 - sw, 13, shade(top, .8))
    else:
        B(2.5, 20, 4, 12, top); B(2.5, 12, 4, 11, sk)
    # head
    hy = 21
    B(-3, hy, 3, hy + 7, sk)
    B(-3.5, hy + 5, 3.5, hy + 8, hair); B(-3.5, hy + 2, -2, hy + 7, hair)
    if c.get('long'): B(-3.5, hy - 3, -1.5, hy + 6, hair); B(-2, hy - 2, -1, hy + 1, hair)
    if c.get('ponytail'): B(-5, hy + 1, -3.5, hy + 6, hair); B(-5.5, hy - 2, -4.5, hy + 2, hair)
    d.point((X(1.6), Y(hy + 3.6)), fill=(30, 24, 20))
    if c.get('glasses'): B(0.5, hy + 4.2, 3, hy + 4.2, (40, 40, 40))
    if c.get('stubble') and not beard: B(-1, hy, 3, hy + 1, shade(sk, .82))
    if beard: B(-1.5, hy - 0.5, 3, hy + 2.5, beard)
    if cry: d.point((X(1.6), Y(hy + 2.2)), fill=(120, 190, 255)); d.point((X(1.6), Y(hy + 1.2)), fill=(120, 190, 255))

def lie(d, x, y, who, face=1):
    c = CAST[who]
    R(d, x - 14, y - 4, x + 10, y, c['top']); R(d, x + 10, y - 6, x + 16, y, SKIN)
    R(d, x + 14, y - 7, x + 17, y, c['hair'])

def astro(d, x, y, face=1, pose='stand', f=0, visor=(70, 100, 130), flag=True, crack=False, s=1.0):
    SU, SU2, SU3 = (232, 232, 226), (190, 192, 186), (150, 150, 146)
    X = lambda dx: x + dx * face * s
    Y = lambda dy: y - dy * s
    def B(a, b, cc, e, col): R(d, X(a), Y(b), X(cc), Y(e), col)
    ph = [2, 0, -2, 0][int(f) % 4] if pose in ('walk', 'run') else 0
    B(-3 + ph, 0, -0.5 + ph, 11, SU); B(0.5 - ph, 0, 3 - ph, 11, SU2)
    B(-3 + ph, 0, 0 + ph, 2, SU3); B(0.5 - ph, 0, 3.5 - ph, 2, SU3)
    B(-4.5, 10, 4.5, 22, SU); B(-4.5, 10, -2, 22, SU2)
    B(-7, 12, -4.5, 21, (120, 120, 116))                       # backpack
    if flag: B(1.5, 19, 3.5, 17.5, (60, 80, 160)); B(1.5, 17.5, 3.5, 16.5, (200, 50, 50))
    if pose == 'reach': B(3.5, 20, 10, 18, SU); B(10, 20, 11.5, 18, SU3)
    else: B(3.5, 20, 5.5, 12, SU); B(3.5, 12, 5.5, 10.5, SU3)
    B(-4.5, 22, 4.5, 31, SU); B(-3, 23.5, 4.5, 29.5, visor)
    d.point((X(3), Y(28.5)), fill=(220, 240, 255))
    if crack:
        d.line([X(0), Y(25), X(2), Y(27), X(1), Y(29), X(3.5), Y(28)], fill=(255, 255, 255))

def tars(d, x, y, f=0, walk=False):
    """The slab robot. x = left, y = feet."""
    for k in range(4):
        off = (math.sin(f * 0.6 + k * 1.6) * 2) if walk else 0
        R(d, x + k * 5, y - 28 + off, x + k * 5 + 4, y + off, (150, 152, 156) if k % 2 else (172, 174, 178))
        R(d, x + k * 5, y - 28 + off, x + k * 5 + 4, y - 27 + off, (210, 212, 216))
    R(d, x + 2, y - 23, x + 17, y - 19, (30, 34, 38)); R(d, x + 3, y - 22, x + 8, y - 20, (120, 220, 255))

# ------------------------------------------------------------------ machines
def truck(d, x, y, face=1, col=(120, 90, 60), f=0):
    X = lambda dx: x + dx * face
    def B(a, b, cc, e, cl): R(d, X(a), y - b, X(cc), y - e, cl)
    B(0, 4, 40, 12, col); B(22, 12, 36, 20, col); B(25, 13, 34, 18, (110, 150, 170))
    B(0, 12, 21, 13, shade(col, .8)); B(36, 10, 42, 6, (210, 210, 200)); B(-1, 6, 1, 9, (200, 40, 40))
    for wx in (8, 33):
        d.ellipse([X(wx) - 5, y - 9, X(wx) + 5, y + 1], fill=(30, 30, 30)); d.ellipse([X(wx) - 2, y - 6, X(wx) + 2, y - 2], fill=(140, 140, 140))

def ranger(d, x, y, s=1.0, face=1, flame=False, f=0):
    X = lambda dx: x + dx * face * s
    Y = lambda dy: y - dy * s
    body = [(X(0), Y(2)), (X(10), Y(9)), (X(40), Y(10)), (X(52), Y(5)), (X(56), Y(2)), (X(50), Y(0)), (X(4), Y(-1))]
    d.polygon(body, fill=(205, 205, 200))
    d.polygon([(X(14), Y(3)), (X(34), Y(3)), (X(30), Y(-4)), (X(18), Y(-4))], fill=(160, 160, 156))
    d.polygon([(X(40), Y(9)), (X(50), Y(5)), (X(44), Y(5))], fill=(40, 50, 70))
    d.line([(X(2), Y(5)), (X(40), Y(8))], fill=(240, 240, 236))
    R(d, X(-2), Y(5), X(1), Y(-1), (90, 90, 90))
    if flame:
        fl = 6 + (f % 3) * 2
        d.polygon([(X(-2), Y(4)), (X(-2 - fl), Y(2)), (X(-2), Y(0))], fill=(150, 200, 255))

def endurance(d, cx, cy, r=40, ang=0.0, tilt=0.35, dmg=False):
    """Ring of 12 modules seen at an angle."""
    pts = []
    for k in range(12):
        a = ang + k * math.pi / 6
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r * tilt, math.sin(a)))
    order = sorted(range(12), key=lambda k: pts[k][2])
    d.ellipse([cx - r, cy - r * tilt, cx + r, cy + r * tilt], outline=(110, 110, 110))
    for k in range(12):                              # spokes
        if k % 3 == 0: d.line([cx, cy, pts[k][0], pts[k][1]], fill=(130, 130, 130))
    R(d, cx - 4, cy - 3, cx + 4, cy + 3, (200, 200, 196))
    for k in order:
        if dmg and k in (3, 4): continue
        px, py, z = pts[k]; sz = 4 + z * 1.2
        col = mix((140, 140, 136), (230, 230, 224), (z + 1) / 2)
        R(d, px - sz, py - sz * 0.7, px + sz, py + sz * 0.7, col)
        R(d, px - sz, py - sz * 0.7, px + sz, py - sz * 0.4, shade(col, 1.1))

def saturn(d, cx, cy, r):
    for y in range(-r, r + 1):
        w = int(math.sqrt(max(0, r * r - y * y)))
        band = (y // max(1, r // 7)) % 2
        c = (222, 196, 140) if band else (200, 170, 118)
        d.line([cx - w, cy + y, cx + w, cy + y], fill=shade(c, 0.7 + 0.3 * (1 - (y + r) / (2 * r))))
    for k in range(3):
        rr = r * (1.5 + k * 0.18)
        d.ellipse([cx - rr, cy - rr * 0.18, cx + rr, cy + rr * 0.18], outline=[(230, 210, 170), (200, 180, 140), (170, 150, 120)][k])
    # front of rings over planet
    rr = r * 1.6
    d.arc([cx - rr, cy - rr * 0.18, cx + rr, cy + rr * 0.18], 0, 180, fill=(240, 220, 180))

def gargantua(d, cx, cy, r, t=0.0):
    """Black hole: warm glow, thick lensed ring wrapping over the top/bottom, bright disk in front."""
    R2 = int(r * 2.3)
    for y in range(-R2, R2 + 1):
        for x in range(-int(R2 * 1.5), int(R2 * 1.5) + 1, 1):
            q = math.hypot(x, y) / r
            qe = math.hypot(x / 1.3, y) / r
            if qe > 2.3 or q < 1.0: continue
            ang = math.atan2(y, x)
            if q < 1.45:                             # lensed disk light hugging the shadow
                b = 1 - (q - 1.0) / 0.45
                b = (b ** 0.8) * (0.7 + 0.3 * -math.sin(ang))   # brighter over the top
                col = mix((90, 36, 10), (255, 244, 220), b)
            else:
                col = mix((70, 30, 10), (0, 0, 0), clamp((qe - 1.2) / 1.1))
            px, py = cx + x, cy + y
            if 0 <= px < W and 0 <= py < H: d.point((px, py), fill=col)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 0, 0))
    d.ellipse([cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1], outline=(255, 246, 226))
    L = r * 3.3
    for x in range(int(-L), int(L) + 1):         # accretion disk crossing in front
        u = abs(x) / L
        th = r * 0.2 * (1 - u) ** 0.8 + 1
        for yy in range(int(-th), int(th) + 1):
            v = abs(yy) / max(1, th)
            b = (1 - u) ** 0.6 * (1 - v * 0.7)
            col = mix((170, 70, 24), (255, 250, 236), b ** 0.7)
            px, py = cx + x, cy + yy + x * 0.02
            if 0 <= px < W and 0 <= py < H: d.point((px, py), fill=col)
    random.seed(int(t * 8))
    for k in range(40):
        x = cx + random.uniform(-L, L); d.point((x, cy + random.uniform(-2, 2) + (x - cx) * 0.02), fill=(255, 255, 240))

def wormhole(d, cx, cy, r, t=0.0):
    rr = random.Random(5)
    for y in range(-r, r + 1):
        w = int(math.sqrt(max(0, r * r - y * y)))
        for x in range(-w, w + 1):
            q = math.hypot(x, y) / r
            col = mix((30, 40, 70), (180, 190, 220), (1 - q) ** 0.6)
            d.point((cx + x, cy + y), fill=col)
    for k in range(120):                             # swirled lensed stars
        a = rr.uniform(0, 6.28) + t * 0.3; q = rr.uniform(0.1, 0.98)
        a2 = a + (1 - q) * 3
        d.point((cx + math.cos(a2) * q * r, cy + math.sin(a2) * q * r), fill=(255, 255, 255))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(220, 230, 255))

def watch(d, cx, cy, r, ang=0.0):
    d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], fill=(150, 150, 150))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(245, 245, 235))
    for k in range(12):
        a = k * math.pi / 6; d.point((cx + math.cos(a) * (r - 2), cy + math.sin(a) * (r - 2)), fill=(40, 40, 40))
    d.line([cx, cy, cx + math.cos(ang - math.pi / 2) * (r - 3), cy + math.sin(ang - math.pi / 2) * (r - 3)], fill=(200, 40, 40))
    d.line([cx, cy, cx + 3, cy - 2], fill=(30, 30, 30))
    sl = max(2, int(r * 1.6)); R(d, cx - r * 0.6, cy - r - 1 - sl, cx + r * 0.6, cy - r - 1, (90, 70, 50)); R(d, cx - r * 0.6, cy + r + 1, cx + r * 0.6, cy + r + 1 + sl, (90, 70, 50))

def bubble(d, x, y, kind='!'):
    R(d, x, y, x + 13, y + 12, (250, 250, 250)); d.polygon([(x + 4, y + 12), (x + 8, y + 12), (x + 5, y + 16)], fill=(250, 250, 250))
    if kind == '!':
        R(d, x + 6, y + 2, x + 7, y + 7, (220, 40, 40)); R(d, x + 6, y + 9, x + 7, y + 10, (220, 40, 40))
    elif kind == '?':
        d.line([x + 4, y + 3, x + 6, y + 2, x + 9, y + 3, x + 9, y + 5, x + 7, y + 7], fill=(40, 80, 200)); R(d, x + 6, y + 9, x + 7, y + 10, (40, 80, 200))
    elif kind == 'heart':
        d.polygon([(x + 3, y + 5), (x + 5, y + 3), (x + 7, y + 5), (x + 9, y + 3), (x + 11, y + 5), (x + 7, y + 10)], fill=(230, 60, 90))
    elif kind == '...':
        for k in range(3): R(d, x + 3 + k * 3, y + 6, x + 4 + k * 3, y + 7, (60, 60, 60))
    elif kind == 'anger':
        d.line([x + 3, y + 3, x + 10, y + 9], fill=(220, 40, 40)); d.line([x + 10, y + 3, x + 3, y + 9], fill=(220, 40, 40))

def corn(d, y0, y1, t=0.0, scroll=0.0, dark=1.0):
    for row, y in enumerate(range(int(y0), int(y1), 3)):
        k = (y - y0) / max(1, y1 - y0)
        g = shade(mix((150, 140, 60), (70, 100, 40), k), dark)
        R(d, 0, y, W, y + 3, g)
        sp = 3 + int(k * 4)
        off = int(scroll * (0.3 + k)) % sp
        for x in range(-off, W, sp):
            sw = int(math.sin(t * 2 + x * 0.1 + row) * (1 + k))
            d.line([x, y + 3, x + sw, y - 1 - int(k * 3)], fill=shade((210, 190, 90), dark * (0.8 + 0.2 * k)))

def farmhouse(d, x, y, s=1.0):
    def B(a, b, c, e, col): R(d, x + a * s, y - b * s, x + c * s, y - e * s, col)
    B(0, 0, 50, 26, (225, 220, 205)); B(0, 0, 18, 26, (200, 196, 182))
    d.polygon([(x - 4 * s, y - 26 * s), (x + 25 * s, y - 44 * s), (x + 54 * s, y - 26 * s)], fill=(110, 70, 60))
    B(30, 14, 38, 22, (70, 90, 110)); B(8, 14, 14, 22, (70, 90, 110)); B(20, 0, 27, 12, (120, 90, 70))
    B(-10, 0, 62, 2, (140, 120, 90))
    B(-6, 0, -4, 18, (230, 225, 210)); B(56, 0, 58, 18, (230, 225, 210)); B(-6, 18, 58, 20, (230, 225, 210))

def bookshelf(d, x, y, w, h, seed=0, gap=None):
    R(d, x, y, x + w, y + h, (90, 60, 40))
    r = random.Random(seed)
    for sy in range(int(y) + 2, int(y + h) - 6, 12):
        R(d, x, sy + 9, x + w, sy + 10, (70, 46, 30))
        bx = x + 2
        while bx < x + w - 3:
            bw = r.randint(2, 4); bh = r.randint(6, 9)
            if gap and abs(bx - gap[0]) < 4 and abs(sy - gap[1]) < 6: bx += bw + 1; continue
            R(d, bx, sy + 9 - bh, bx + bw - 1, sy + 8, r.choice([(170, 50, 40), (60, 90, 140), (200, 170, 90), (70, 120, 70), (140, 80, 140), (220, 210, 190)]))
            bx += bw

def fade(im, t, t_in=0.0, t_out=None, dur=0.5):
    if t < t_in + dur: im = Image.blend(Image.new('RGB', (W, H)), im, clamp((t - t_in) / dur))
    if t_out is not None and t > t_out - dur: im = Image.blend(im, Image.new('RGB', (W, H)), clamp((t - (t_out - dur)) / dur))
    return im

# ---- close-up canvas: draw at 192x108, upscale 2x so pixel size stays consistent
ZW, ZH = 192, 108
def zcanvas(col=(0, 0, 0)):
    im = Image.new('RGB', (ZW, ZH), col); return im, ImageDraw.Draw(im)
def up(im): return im.resize((W, H), Image.NEAREST)

def zroom(d, light=(240, 210, 150), dark=False, dust=0.0, t=0.0):
    k = 0.6 if dark else 1.0
    grad(d, 0, 76, shade((156, 124, 98), k), shade((132, 104, 84), k), 0, ZW)
    R(d, 0, 76, ZW, ZH, shade((150, 110, 74), k))
    for x in range(-20, ZW + 30, 14): d.line([x, 76, x - 16, ZH], fill=shade((132, 96, 64), k))
    R(d, 0, 74, ZW, 76, shade((110, 80, 56), k))
    R(d, 118, 16, 156, 54, (90, 70, 56)); R(d, 120, 18, 154, 52, light)
    d.line([137, 18, 137, 52], fill=(90, 70, 56)); d.line([120, 35, 154, 35], fill=(90, 70, 56))
    R(d, 160, 56, ZW, 76, (180, 80, 70)); R(d, 160, 52, ZW, 57, (232, 232, 222))
    bookshelf(d, 8, 18, 40, 58, seed=3, gap=(27, 42))
    R(d, 60, 30, 76, 44, (200, 190, 150)); R(d, 62, 32, 74, 42, (90, 140, 200))           # rocket poster
    d.polygon([(66, 41), (68, 33), (70, 41)], fill=(240, 240, 240))
    if dust > 0:
        r = random.Random(1)
        for n in range(int(40 * dust)):
            x = 120 + r.randrange(34); y = 18 + (r.randrange(34) + t * 10 * r.random()) % 34
            d.point((x, y), fill=(220, 190, 140))

def portrait(d, cx, by, who='cooper', s=1, cry=False, beard=None, grey=False, smile=False):
    """Head-and-shoulders bust. cx = centre, by = bottom edge. ~ 26*s tall."""
    c = CAST[who]; hair = (210, 210, 210) if grey else c['hair']
    sk = c.get('skin', SKIN); beard = beard or c.get('beard')
    def B(a, b, cc, e, col): R(d, cx + a * s, by - b * s, cx + cc * s, by - e * s, col)
    B(-12, 0, 12, 8, c['top']); B(-12, 0, -6, 8, shade(c['top'], .8)); B(-3, 8, 3, 11, sk)
    if c.get('inner'): B(-3, 0, 3, 7, c['inner'])
    if c.get('ponytail'): B(-10, 8, -7, 22, hair)
    B(-7, 10, 7, 25, sk); B(-7, 10, -5, 25, shade(sk, .92))
    B(-8, 21, 8, 27, hair); B(-8, 13, -6, 24, hair); B(6, 15, 8, 24, hair)
    if c.get('long'): B(-9, 4, -6, 22, hair); B(6, 4, 9, 22, hair)
    if c.get('ponytail'): B(-8, 22, 8, 27, hair); B(-2, 25, 2, 26, shade(hair, 1.25))
    B(-4, 18, -2, 17, (30, 24, 20)); B(2, 18, 4, 17, (30, 24, 20))
    B(-4, 20, -1, 19.5, shade(hair, .8)); B(1, 20, 4, 19.5, shade(hair, .8))
    if c.get('glasses'): B(-5, 19, -1, 16, (40, 40, 40)); B(1, 19, 5, 16, (40, 40, 40)); B(-4, 18.5, -2, 16.5, (200, 220, 230)); B(2, 18.5, 4, 16.5, (200, 220, 230)); B(-1, 18, 1, 17.5, (40, 40, 40))
    if c.get('stubble') and not beard: B(-6, 10, 6, 13, shade(sk, .85))
    if smile: B(-2, 13, 2, 12.5, (150, 70, 60))
    else: B(-2, 13, 2, 12.5, (170, 110, 90))
    if beard: B(-7, 10, 7, 14, beard); B(-3, 13, 3, 12, (150, 70, 60))
    if cry: B(-4, 16.5, -3, 13, (130, 190, 255)); B(3, 16.5, 4, 14, (130, 190, 255))
