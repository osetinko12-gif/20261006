"""漫符（まんぷ）集ジェネレーター.

キャラの頭や顔のまわりに置く記号. 大きさはB5原稿で等倍 10〜30mm 程度.
「線画（白抜き＋黒線）」と「ベタ（黒塗り）」の2スタイルを基本に用意する.
"""
import math
import os
from collections import Counter

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from shapely import affinity

from sozai import (BLACK, WHITE, bezier, ellipse, fit_canvas, heart, outline_ring, rng, sparkle, star,
                   stroke_line, tapered, tapered_curve, wedge_along)
from fukidashi import body_cloud

LW = 0.4
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "manpu")
ITEMS = []


class Mark:
    def __init__(self, cat, name, ja):
        self.cat, self.name, self.ja = cat, name, ja
        self.layers = []

    def line(self, g, lw=LW):
        """白抜き＋黒線."""
        self.layers += [(g, WHITE), (outline_ring(g, lw), BLACK)]
        return self

    def solid(self, g, color=BLACK):
        self.layers.append((g, color))
        return self

    def save(self):
        cv = fit_canvas([g for g, _ in self.layers], margin=1.0)
        for g, c in self.layers:
            cv.add(g, c)
        base = os.path.join(OUT, self.cat, self.name)
        cv.save(base)
        return base + ".svg"


def mk(cat, prefix, ja):
    n = sum(1 for it in ITEMS if it.cat == cat) + 1
    it = Mark(cat, "{}_{:03d}".format(prefix, n), ja)
    ITEMS.append(it)
    return it


def both(cat, prefix, ja, g, lw=LW):
    """同じ形を線画版とベタ版の2つ作る."""
    mk(cat, prefix, ja + "_線画").line(g, lw)
    mk(cat, prefix, ja + "_ベタ").solid(g)


# ---------------------------------------------------------------- shapes
def drop(h, cx=0, cy=0, rot=0, fat=1.0):
    """しずく（先が上）."""
    pts = []
    for i in range(240):
        t = 2 * math.pi * i / 240
        x = math.sin(t) * math.sin(t / 2) ** 1.3 * fat
        y = -math.cos(t)
        pts.append((x, y))
    g = Polygon(pts).buffer(0)
    minx, miny, maxx, maxy = g.bounds
    s = h / (maxy - miny)
    g = affinity.scale(g, s, s, origin=(0, 0))
    g = affinity.translate(g, cx - g.centroid.x, cy - (g.bounds[1] + g.bounds[3]) / 2)
    return affinity.rotate(g, rot, origin=(cx, cy))


def drop_shine(h, cx=0, cy=0, rot=0):
    """しずくのハイライト（白い線）."""
    r = h * 0.22
    arc = [(cx + r * math.cos(a), cy + h * 0.12 + r * math.sin(a))
           for a in [math.radians(d) for d in range(200, 260, 4)]]
    g = tapered_curve(arc, h * 0.07, 0.3, 0.3)
    return affinity.rotate(g, rot, origin=(cx, cy))


def anger(size, w=None, rot=0):
    """怒りマーク（4つの曲がった線が十字に向き合う形）."""
    s = size / 2
    g = size * 0.11
    w = w or size * 0.13
    parts = []
    for k in range(4):
        a = math.radians(90 * k)
        R = lambda x, y: (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))
        A, B, C = R(g, s), R(g * 1.1, g * 1.1), R(s, g)
        curve = bezier(A, B, C, 30)
        parts.append(tapered_curve(curve, w, 0.12, 0.12, min_w=w * 0.35))
    return affinity.rotate(unary_union(parts), rot, origin=(0, 0))


def exclam(h, w=None, cx=0, cy=0, slant=0):
    w = w or h * 0.28
    body = Polygon([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w * 0.12, cy + h * 0.22),
                    (cx - w * 0.12, cy + h * 0.22)]).buffer(w * 0.08)
    dot = Point(cx, cy + h / 2 - w * 0.22).buffer(w * 0.24, quad_segs=16)
    g = unary_union([body, dot])
    return affinity.skew(g, xs=slant, origin=(cx, cy))


def question(h, cx=0, cy=0, slant=0):
    r = h * 0.26
    top = cy - h / 2 + r
    pts = [(cx - r * 1.0, top + r * 0.1)]
    for d in range(190, 360 + 80, 6):
        a = math.radians(d)
        pts.append((cx + r * math.cos(a), top + r * math.sin(a)))
    pts += bezier(pts[-1], (cx, top + r * 1.2), (cx, cy + h * 0.2), 10)[1:]
    hook = tapered_curve(pts, h * 0.15, 0.05, 0.05, min_w=h * 0.09)
    dot = Point(cx, cy + h / 2 - h * 0.06).buffer(h * 0.075, quad_segs=16)
    return affinity.skew(unary_union([hook, dot]), xs=slant, origin=(cx, cy))


def note(h, cx=0, cy=0, double=False):
    hr = h * 0.17
    head = affinity.rotate(ellipse(hr * 1.25, hr * 0.85, cx, cy + h / 2 - hr), -25, origin=(cx, cy + h / 2 - hr))
    sx = cx + hr * 1.05
    stem = Polygon([(sx - h * 0.06, cy - h / 2), (sx, cy - h / 2), (sx, cy + h / 2 - hr), (sx - h * 0.06, cy + h / 2 - hr)])
    parts = [head, stem]
    if double:
        dx = h * 0.62
        head2 = affinity.translate(head, dx, -h * 0.12)
        stem2 = affinity.translate(stem, dx, -h * 0.12)
        beam = Polygon([(sx - h * 0.06, cy - h / 2), (sx + dx, cy - h / 2 - h * 0.12),
                        (sx + dx, cy - h / 2 - h * 0.12 + h * 0.16), (sx - h * 0.06, cy - h / 2 + h * 0.16)])
        parts += [head2, stem2, beam]
    else:
        flag = tapered_curve(bezier((sx - 0.1, cy - h / 2 + 0.3), (sx + h * 0.45, cy - h * 0.15), (sx + h * 0.22, cy + h * 0.1), 20),
                             h * 0.12, 0.0, 0.7)
        parts.append(flag)
    return unary_union(parts)


def spiral(R, turns, lw, cx=0, cy=0):
    pts = []
    n = int(turns * 90)
    for i in range(n + 1):
        t = i / n
        a = 2 * math.pi * turns * t
        r = R * t
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return tapered_curve(pts, lw, 0.15, 0.08)


def zzz(h, n=3, lw=None):
    parts = []
    x, y, s = 0.0, 0.0, h
    lw = lw or h * 0.12
    for i in range(n):
        Z = [(x, y), (x + s, y), (x, y + s), (x + s, y + s)]
        parts.append(stroke_line(Z, lw * (s / h) ** 0.5, cap="round"))
        ns = s * 0.68
        x, y = x + s * 0.9, y - ns - s * 0.22
        s = ns
    return unary_union(parts)


def surprise(n, L, spread, w, gap=0):
    """驚き線（ハッ）: 扇形に並ぶ短い線."""
    parts = []
    for i in range(n):
        a = math.radians(-90 - spread / 2 + spread * i / max(1, n - 1))
        p0 = (gap * math.cos(a), gap * math.sin(a))
        p1 = ((gap + L) * math.cos(a), (gap + L) * math.sin(a))
        parts.append(tapered(p1, p0, w, 0.0))
    return unary_union(parts)


def blush(n, L, w, ang=60, spacing=None):
    spacing = spacing or L * 0.28
    a = math.radians(ang)
    parts = []
    for i in range(n):
        x = i * spacing
        parts.append(tapered_curve([(x, 0), (x + L * math.cos(a), -L * math.sin(a))], w, 0.35, 0.35))
    return unary_union(parts)


def bolt(h, w=None):
    w = w or h * 0.45
    pts = [(0.15 * w, -h / 2), (0.55 * w, -h / 2), (0.25 * w, -h * 0.05), (0.6 * w, -h * 0.05),
           (-0.25 * w, h / 2), (0.02 * w, h * 0.06), (-0.35 * w, h * 0.06)]
    return Polygon(pts)


def flower(R, k=5, cx=0, cy=0):
    parts = [Point(cx + R * 0.55 * math.cos(2 * math.pi * i / k - math.pi / 2),
                   cy + R * 0.55 * math.sin(2 * math.pi * i / k - math.pi / 2)).buffer(R * 0.45, quad_segs=24) for i in range(k)]
    return unary_union(parts)


def scribble(R, r, turns=7, lw=0.35):
    pts = []
    n = turns * 60
    cx = cy = 0
    for i in range(n):
        t = i / n
        a = 2 * math.pi * turns * t * 1.03
        rr = R * (0.55 + 0.45 * math.sin(2 * math.pi * t * 2.3 + r.uniform(0, 0.02)))
        cx += r.uniform(-0.05, 0.05)
        cy += r.uniform(-0.05, 0.05)
        pts.append((cx + rr * math.cos(a), cy + rr * 0.8 * math.sin(a)))
    return tapered_curve(pts, lw, 0.05, 0.05)


def soul(h):
    """魂（口から抜けるやつ）."""
    head = Point(0, 0).buffer(h * 0.3, quad_segs=32)
    tail = wedge_along(bezier((0, h * 0.05), (h * 0.55, h * 0.35), (h * 0.1, h * 0.75), 30), h * 0.55, 0.0, 0.9)
    return unary_union([head, tail]).buffer(0.01)


def bulb(h):
    r = h * 0.32
    glass = unary_union([Point(0, 0).buffer(r, quad_segs=32),
                         Polygon([(-r * 0.6, r * 0.6), (r * 0.6, r * 0.6), (r * 0.45, r * 1.25), (-r * 0.45, r * 1.25)])])
    base = Polygon([(-r * 0.45, r * 1.3), (r * 0.45, r * 1.3), (r * 0.42, r * 1.75), (-r * 0.42, r * 1.75)])
    return glass, base


def rays(R0, R1, n, w, start=-160, end=-20):
    parts = []
    for i in range(n):
        a = math.radians(start + (end - start) * i / max(1, n - 1))
        parts.append(tapered((R1 * math.cos(a), R1 * math.sin(a)), (R0 * math.cos(a), R0 * math.sin(a)), w, 0.0))
    return unary_union(parts)


def shake_marks(h, w=LW * 1.6, pairs=2):
    """ぷるぷる（左右の小さなカッコ線）."""
    parts = []
    for side in [-1, 1]:
        for k in range(pairs):
            x = side * (h * 0.5 + k * h * 0.22)
            arc = [(x + side * h * 0.08 * math.sin(math.pi * t), -h * 0.25 + h * 0.5 * t) for t in [i / 20 for i in range(21)]]
            parts.append(tapered_curve(arc, w, 0.3, 0.3))
    return unary_union(parts)


def broken_heart(h, r):
    hh = heart(h)
    zz = [(0.0, -h * 0.6)]
    y = -h * 0.35
    s = 1
    while y < h * 0.6:
        zz.append((s * h * 0.08, y))
        y += h * 0.15
        s *= -1
    crack = LineString(zz).buffer(h * 0.03)
    left = hh.difference(crack)
    pieces = list(left.geoms) if left.geom_type == "MultiPolygon" else [left]
    pieces.sort(key=lambda p: p.centroid.x)
    if len(pieces) >= 2:
        pieces[0] = affinity.rotate(affinity.translate(pieces[0], -h * 0.05, 0), 6, origin=(0, h * 0.4))
        pieces[-1] = affinity.rotate(affinity.translate(pieces[-1], h * 0.05, 0), -6, origin=(0, h * 0.4))
    return unary_union(pieces)


# ---------------------------------------------------------------- catalog
def build():
    # 01 汗
    cat = "01_ase"
    for rot, ja in [(0, "まっすぐ"), (-25, "傾き左"), (25, "傾き右")]:
        g = drop(12, rot=rot)
        it = mk(cat, "mp_ase", "汗_1滴_{}_線画".format(ja)).line(g)
        mk(cat, "mp_ase", "汗_1滴_{}_ベタ".format(ja)).solid(g).solid(drop_shine(12, rot=rot), WHITE)
    g2 = [drop(12, 0, 0, -15), drop(8, 9, 6, 15)]
    mk(cat, "mp_ase", "汗_2滴_線画").line(g2[0]).line(g2[1])
    mk(cat, "mp_ase", "汗_2滴_ベタ").solid(unary_union(g2))
    g3 = [drop(11, 0, 0, -20), drop(8, 9, -4, 10), drop(6, 5, 9, 30)]
    mk(cat, "mp_ase", "汗_3滴_線画").line(g3[0]).line(g3[1]).line(g3[2])
    mk(cat, "mp_ase", "汗_3滴_ベタ").solid(unary_union(g3))
    # 冷や汗（小さなしずくのかたまり）
    r = rng("hiyaase")
    small = [drop(r.uniform(2.5, 4.5), r.uniform(-8, 8), r.uniform(-8, 8), r.uniform(-20, 20)) for _ in range(9)]
    small = [s for k, s in enumerate(small) if not any(s.distance(t) < 0.8 for t in small[:k])]
    it = mk(cat, "mp_ase", "冷や汗_小粒_線画")
    for s in small:
        it.line(s, LW * 0.7)
    mk(cat, "mp_ase", "冷や汗_小粒_ベタ").solid(unary_union(small))
    # 汗飛び（あせあせ）
    for k, ja in [(5, "あせあせ"), (3, "あせ")]:
        parts = []
        for i in range(k):
            a = math.radians(-150 + 120 * i / (k - 1))
            d = 12
            parts.append(drop(6, d * math.cos(a), d * math.sin(a), math.degrees(a) - 90))
        mk(cat, "mp_ase", "汗飛び_{}_線画".format(ja)).line(unary_union(parts))
        mk(cat, "mp_ase", "汗飛び_{}_ベタ".format(ja)).solid(unary_union(parts))
    # 汗＋流れ線
    g = drop(13)
    lines = unary_union([tapered((-6.5 + 2.2 * i, -10), (-6.5 + 2.2 * i, -4), 0.45, 0) for i in range(0)] +
                        [tapered((x, -9), (x, -14), 0.5, 0.0) for x in (-3, 0, 3)])
    mk(cat, "mp_ase", "汗_たらり_線画").line(g).solid(lines)
    # 涙
    for rot, ja in [(0, "ぽろり"), (-15, "ぽろり傾き")]:
        g = drop(9, rot=rot, fat=0.85)
        mk(cat, "mp_ase", "涙_{}_線画".format(ja)).line(g)
    for k, ja in [(1, "滝涙_1本"), (2, "滝涙_2本")]:
        parts = []
        for j in range(k):
            pts = [(j * 4 + 0.8 * math.sin(t * 7), t * 30) for t in [i / 40 for i in range(41)]]
            parts.append(tapered_curve(pts, 2.2, 0.05, 0.25))
        g = unary_union(parts)
        mk(cat, "mp_ase", "{}_線画".format(ja)).line(g, LW * 0.8)

    # 02 怒り
    cat = "02_ikari"
    for size, rot, ja in [(14, 0, "標準"), (14, 20, "傾き"), (20, 0, "大")]:
        both(cat, "mp_ikari", "怒りマーク_" + ja, anger(size, rot=rot))
    g = unary_union([anger(14), affinity.translate(anger(9, rot=25), 13, -8)])
    both(cat, "mp_ikari", "怒りマーク_2つ", g)
    # 怒りの湯気（ぷんすか）
    for k, ja in [(2, "湯気2つ"), (3, "湯気3つ")]:
        puffs = []
        for i in range(k):
            a = math.radians(-130 + 80 * i / max(1, k - 1))
            c = body_cloud(4.5 - i * 0.3, 3.5, 6, 1.8, rng("puff", k, i), 0.2)
            puffs.append(affinity.translate(c, 14 * math.cos(a), 14 * math.sin(a)))
        it = mk(cat, "mp_ikari", "怒り_{}_線画".format(ja))
        for p in puffs:
            it.line(p)
        mk(cat, "mp_ikari", "怒り_{}_ベタ".format(ja)).solid(unary_union(puffs))
    # ピキッ（ひび）
    for ja, pts in [("ピキッ", [(0, 0), (3, 2), (1.5, 4), (5, 6.5), (3.5, 8.5), (7, 11)])]:
        g = tapered_curve(pts, 1.1, 0.0, 0.6)
        branch = tapered_curve([(3, 2), (6, 1.2)], 0.7, 0.0, 0.8)
        branch2 = tapered_curve([(5, 6.5), (8, 5.8)], 0.6, 0.0, 0.8)
        mk(cat, "mp_ikari", ja + "_ひび").solid(unary_union([g, branch, branch2]))
    # もやもや（いらいら）
    for i, (R, turns) in enumerate([(7, 8), (10, 12)]):
        mk(cat, "mp_ikari", "もやもや_{}".format("小" if i == 0 else "大")).solid(scribble(R, rng("scr", i), turns, 0.35))
    # 03 驚き・ショック
    cat = "03_odoroki"
    for n, L, sp, ja in [(3, 7, 70, "3本"), (5, 7, 110, "5本"), (3, 11, 50, "3本_長")]:
        mk(cat, "mp_odoroki", "驚き線_" + ja).solid(surprise(n, L, sp, 1.0, gap=4))
    # 頭のまわりの驚き線（左右）
    g = unary_union([surprise(3, 6, 60, 0.9, gap=3).buffer(0), affinity.translate(affinity.scale(surprise(3, 6, 60, 0.9, gap=3), -1, 1), 0, 0)])
    parts = []
    for side in [-1, 1]:
        for k in range(3):
            a = math.radians((-90 + side * (35 + 22 * k)))
            p0 = (14 * math.cos(a), 14 * math.sin(a))
            p1 = (21 * math.cos(a), 21 * math.sin(a))
            parts.append(tapered(p1, p0, 1.0, 0))
    mk(cat, "mp_odoroki", "驚き線_左右").solid(unary_union(parts))
    for h, sl, ja in [(16, 0, "まっすぐ"), (16, -0.2, "傾き")]:
        both(cat, "mp_odoroki", "ビックリ_" + ja, exclam(h, slant=sl))
    both(cat, "mp_odoroki", "ビックリ2つ", unary_union([exclam(16, slant=-0.15), exclam(13, cx=6.5, cy=1.5, slant=-0.15)]))
    for sl, ja in [(0, "まっすぐ"), (-0.2, "傾き")]:
        both(cat, "mp_odoroki", "はてな_" + ja, question(16, slant=sl))
    both(cat, "mp_odoroki", "はてな2つ", unary_union([question(16), affinity.translate(question(11), 11, 3)]))
    both(cat, "mp_odoroki", "ビックリはてな", unary_union([exclam(16, slant=-0.15), question(15, cx=8.5, cy=0.5, slant=-0.15)]))
    # ガーン縦線（顔の上に乗せる小さいもの）
    for n, ja in [(5, "5本"), (8, "8本")]:
        r = rng("gaan", n)
        parts = [tapered((i * 1.6, 0), (i * 1.6, r.uniform(8, 14)), 0.55, 0.0, round_tip=False) for i in range(n)]
        mk(cat, "mp_odoroki", "ガーン縦線_" + ja).solid(unary_union(parts))
    # 稲妻（ショック）
    both(cat, "mp_odoroki", "稲妻", bolt(16))
    both(cat, "mp_odoroki", "稲妻2つ", unary_union([bolt(16), affinity.translate(affinity.rotate(bolt(11), 15), 9, 4)]))
    # 魂が抜ける
    mk(cat, "mp_odoroki", "魂が抜ける_線画").line(soul(18))
    mk(cat, "mp_odoroki", "魂が抜ける_反転_線画").line(affinity.scale(soul(18), -1, 1, origin=(0, 0)))

    # 04 混乱・眠り
    cat = "04_konran"
    for R, t, ja in [(6, 3.2, "小"), (9, 4.2, "大")]:
        mk(cat, "mp_konran", "ぐるぐる_" + ja).solid(spiral(R, t, 0.7))
    # 目が回る（星がまわる）
    orbit = ellipse(14, 5)
    ring = outline_ring(orbit, 0.35)
    stars = []
    for a in [200, 300, 30]:
        th = math.radians(a)
        stars.append(star(3.2, 1.4, 5, 14 * math.cos(th), 5 * math.sin(th)))
    cut = unary_union([s.buffer(0.8) for s in stars])
    it = mk(cat, "mp_konran", "ピヨピヨ星_線画")
    it.solid(ring.difference(cut))
    for s in stars:
        it.line(s)
    mk(cat, "mp_konran", "ピヨピヨ星_ベタ").solid(ring.difference(cut)).solid(unary_union(stars))
    both(cat, "mp_konran", "Zzz", zzz(9))
    both(cat, "mp_konran", "Zz", zzz(9, n=2))
    # 鼻ちょうちん
    bub = Point(0, 0).buffer(7, quad_segs=48)
    shine = tapered_curve([(4.6 * math.cos(math.radians(200 + 5 * k)), 4.6 * math.sin(math.radians(200 + 5 * k)))
                           for k in range(11)], 0.9, 0.3, 0.3)
    mk(cat, "mp_konran", "鼻ちょうちん").line(bub).solid(shine)
    # ため息
    for i in range(2):
        c = body_cloud(6, 4, 7, 2.0, rng("sigh", i), 0.2)
        tail = tapered_curve(bezier((-6, 2), (-10, 5), (-13, 2), 20), 1.2, 0.0, 0.8)
        g = unary_union([c, affinity.translate(body_cloud(2.5, 2, 5, 1.0, rng("sigh2", i), 0.2), -10, 4)])
        mk(cat, "mp_konran", "ため息_{}".format(i + 1)).line(g)
    # ぷるぷる
    mk(cat, "mp_konran", "ぷるぷる_1重").solid(shake_marks(16, pairs=1))
    mk(cat, "mp_konran", "ぷるぷる_2重").solid(shake_marks(16, pairs=2))

    # 05 ひらめき・音符
    cat = "05_hirameki"
    glass, base = bulb(18)
    hatch = unary_union([LineString([(-3, 18 * 0.32 * (1.38 + 0.13 * k)), (3, 18 * 0.32 * (1.38 + 0.13 * k))]).buffer(0.2) for k in range(3)])
    mk(cat, "mp_hirameki", "電球").line(glass).line(base).solid(hatch.intersection(base)).solid(rays(8, 12, 5, 0.9, -170, -10))
    mk(cat, "mp_hirameki", "電球_光線なし").line(glass).line(base).solid(hatch.intersection(base))
    mk(cat, "mp_hirameki", "ピコーン線").solid(rays(3, 10, 5, 1.1, -160, -20))
    both(cat, "mp_hirameki", "音符_八分", note(14))
    both(cat, "mp_hirameki", "音符_連桁", note(14, double=True))
    g = unary_union([note(12), affinity.translate(note(9), 11, -6), affinity.translate(note(10, double=True), 16, 6)])
    mk(cat, "mp_hirameki", "音符_3つ散らし").solid(g)

    # 06 キラキラ・星
    cat = "06_kira"
    for thin, ja in [(0.12, "細"), (0.22, "太")]:
        both(cat, "mp_kira", "キラ_1つ_" + ja, sparkle(8, thin=thin))
    g = unary_union([sparkle(8), sparkle(4.5, 9, -6), sparkle(3, 6, 8)])
    both(cat, "mp_kira", "キラ_3つ", g)
    g = unary_union([sparkle(9), sparkle(5.5, 0, 0, thin=0.12, rot=math.pi / 4)])
    both(cat, "mp_kira", "キラ_8方向", g)
    for k, ja in [(5, "五芒星"), (6, "六芒星")]:
        both(cat, "mp_kira", "星_" + ja, star(8, 3.6 if k == 5 else 4.6, k))
    g = unary_union([star(8, 3.6, 5), star(5, 2.2, 5, 11, -6), star(3.5, 1.5, 5, 9, 7)])
    both(cat, "mp_kira", "星_3つ", g)
    # 輝き（丸＋光線）
    g = unary_union([Point(0, 0).buffer(2.2), rays(3.5, 8, 8, 0.9, 0, 315)])
    mk(cat, "mp_kira", "ピカッ").solid(g)
    # 花
    for k, ja in [(5, "5弁"), (6, "6弁")]:
        f = flower(7, k)
        c = Point(0, 0).buffer(1.8, quad_segs=24)
        mk(cat, "mp_kira", "花_{}_線画".format(ja)).line(f).line(c)
    fl = [affinity.translate(flower(6, 5), 0, 0), affinity.translate(flower(4.5, 5), 11, -5), affinity.translate(flower(3.5, 5), 8, 7)]
    it = mk(cat, "mp_kira", "花_3つ_線画")
    for f in fl:
        it.line(f)
        it.line(Point(f.centroid).buffer(f.bounds[2] - f.centroid.x - (f.bounds[2] - f.bounds[0]) * 0.36))

    # 07 ハート・恋愛
    cat = "07_heart"
    both(cat, "mp_heart", "ハート", heart(12))
    g = unary_union([heart(12), affinity.rotate(heart(7), 15, origin=(0, 0)).buffer(0) if False else heart(7, 11, -7), heart(5, 8, 8)])
    both(cat, "mp_heart", "ハート_3つ", g)
    both(cat, "mp_heart", "ハートブレイク", broken_heart(14, rng("bh")))
    # ドキドキ（ハート＋まわりの線）
    lines = unary_union([tapered((10 * math.cos(math.radians(a)), 10 * math.sin(math.radians(a))),
                                 (7 * math.cos(math.radians(a)), 7 * math.sin(math.radians(a))), 0.9, 0) for a in [-150, -120, -60, -30, 160, 20]])
    mk(cat, "mp_heart", "ドキドキ_線画").line(heart(10)).solid(lines)
    mk(cat, "mp_heart", "ドキドキ_ベタ").solid(heart(10)).solid(lines)
    # ハートが飛ぶ
    hs = [heart(4.5 + i * 1.3, i * 6.5, -i * 5.5 + (i % 2) * 2) for i in range(4)]
    mk(cat, "mp_heart", "ハート連なり_線画").line(unary_union(hs))
    mk(cat, "mp_heart", "ハート連なり_ベタ").solid(unary_union(hs))
    # 照れ（斜線）
    mk(cat, "mp_heart", "照れ斜線_5本").solid(blush(5, 6, 0.6))
    mk(cat, "mp_heart", "照れ斜線_7本").solid(blush(7, 5, 0.5))
    oval = ellipse(7, 4)
    hatch = unary_union([LineString([(-8 + i * 1.6, 5), (-4 + i * 1.6, -5)]).buffer(0.22) for i in range(12)]).intersection(oval.buffer(-0.6))
    mk(cat, "mp_heart", "ほっぺ_斜線入り楕円").solid(hatch)
    mk(cat, "mp_heart", "ほっぺ_斜線入り楕円_ペア").solid(unary_union([hatch, affinity.translate(hatch, 26, 0)]))
    # ハートの吐息
    c = body_cloud(5, 3.5, 6, 1.8, rng("hb"), 0.2)
    mk(cat, "mp_heart", "ハート吐息").line(unary_union([c])).line(heart(5, -8, 3)).solid(heart(3.5, 6, -5))
    # ハート目（目の上に乗せる）
    both(cat, "mp_heart", "ハート目_ペア", unary_union([heart(8, 0, 0), heart(8, 16, 0)]))

    # 08 その他
    cat = "08_sonota"
    # 天使の輪
    halo = ellipse(9, 2.6).difference(ellipse(6.6, 1.4))
    both(cat, "mp_sonota", "天使の輪", halo)
    # ゾクッ（寒気の波線）
    for n, ja in [(3, "3本"), (5, "5本")]:
        parts = []
        for k in range(n):
            pts = [(k * 2.6 + 0.7 * math.sin(t * 2 * math.pi * 2.5), t * 14) for t in [i / 60 for i in range(61)]]
            parts.append(tapered_curve(pts, 0.6, 0.3, 0.3))
        mk(cat, "mp_sonota", "ゾクッ_寒気_" + ja).solid(unary_union(parts))
    # ビクッ（肩のまわりの短い線）
    parts = []
    for side in [-1, 1]:
        for k, (ang, L) in enumerate([(-35, 5), (-10, 6), (15, 5)]):
            a = math.radians(ang)
            x0 = side * 12
            p0 = (x0 + side * 1.5 * math.cos(a), 1.5 * math.sin(a))
            p1 = (x0 + side * (1.5 + L) * math.cos(a), (1.5 + L) * math.sin(a))
            parts.append(tapered(p1, p0, 0.9, 0.0))
    mk(cat, "mp_sonota", "ビクッ_左右").solid(unary_union(parts))
    # ドキッ（トゲの中のハート）
    from fukidashi import body_spiky
    sp = body_spiky(9, 9, 12, 0.3, rng("doki"), irregular=0.3)
    mk(cat, "mp_sonota", "ドキッ_トゲハート_線画").line(sp).solid(heart(7))
    mk(cat, "mp_sonota", "ドキッ_トゲハート_ベタ").solid(sp.difference(heart(7.8))).solid(heart(6.2))
    # ほかほか湯気
    for n, ja in [(3, "3本"), (2, "2本")]:
        parts = []
        for k in range(n):
            pts = [(k * 4.5 + 1.2 * math.sin(t * 2 * math.pi * 1.3 + k), -t * 13) for t in [i / 50 for i in range(51)]]
            parts.append(tapered_curve(pts, 0.9, 0.25, 0.5))
        mk(cat, "mp_sonota", "湯気_ほかほか_" + ja).solid(unary_union(parts))
    # ズキュン（矢が刺さったハート）
    hh = heart(13)
    arrow = unary_union([LineString([(-12, 7), (12, -7)]).buffer(0.45),
                         Polygon([(12, -7), (8.2, -7.3), (10.3, -3.9)]).buffer(0),
                         Polygon([(-12, 7), (-14.5, 6.0), (-13.6, 8.6)]).buffer(0),
                         Polygon([(-11, 6.4), (-13.5, 5.4), (-12.6, 8.0)]).buffer(0)])
    mk(cat, "mp_sonota", "ズキュン_矢ハート_線画").line(hh).solid(arrow.difference(hh.buffer(-0.01)).union(arrow.intersection(hh).difference(hh.buffer(-6))))
    mk(cat, "mp_sonota", "ズキュン_矢ハート_ベタ").solid(hh).solid(arrow.difference(hh))
    # ぷしゅー（頭から出る煙）
    puffs = [body_cloud(3.8, 3, 6, 1.5, rng("pshu", i), 0.2) for i in range(3)]
    puffs = [affinity.translate(p, dx, dy) for p, (dx, dy) in zip(puffs, [(0, 0), (5, -7), (-3, -13)])]
    it = mk(cat, "mp_sonota", "ぷしゅー_煙_線画")
    for p in puffs:
        it.line(p)
    mk(cat, "mp_sonota", "ぷしゅー_煙_ベタ").solid(unary_union(puffs))
    # 三点リーダ
    mk(cat, "mp_sonota", "三点リーダ_横").solid(unary_union([Point(i * 4, 0).buffer(0.9) for i in range(3)]))
    mk(cat, "mp_sonota", "三点リーダ_縦").solid(unary_union([Point(0, i * 4).buffer(0.9) for i in range(3)]))
    # ビックリ3つ
    both(cat, "mp_sonota", "ビックリ3つ", unary_union([exclam(15, cx=0, slant=-0.15), exclam(15, cx=6, slant=-0.15), exclam(15, cx=12, slant=-0.15)]))
    # 怒りマーク散らし
    g = unary_union([anger(10), affinity.translate(anger(7, rot=20), 11, -7), affinity.translate(anger(6, rot=-15), -9, -8),
                     affinity.translate(anger(5, rot=30), 9, 8)])
    both(cat, "mp_sonota", "怒りマーク散らし", g)
    # 雨雲（どんより）
    cloud = body_cloud(9, 4.5, 9, 2.6, rng("rainc"), 0.25)
    rain = unary_union([tapered((x, 7), (x - 1.2, 13 + (x % 3)), 0.6, 0.0) for x in (-6, -3, 0, 3, 6)])
    mk(cat, "mp_sonota", "雨雲_どんより_線画").line(cloud).solid(rain)
    mk(cat, "mp_sonota", "雨雲_どんより_ベタ").solid(cloud).solid(rain)
    # 晴れ（太陽）
    sun = Point(0, 0).buffer(4.5, quad_segs=32)
    mk(cat, "mp_sonota", "太陽_線画").line(sun).solid(rays(6.2, 10, 12, 1.0, 0, 330))
    # 汗しぶき（大）
    r = rng("splash")
    parts = []
    for k in range(9):
        a = math.radians(-170 + 160 * k / 8 + r.uniform(-6, 6))
        d = r.uniform(8, 13)
        parts.append(drop(r.uniform(3, 5.5), d * math.cos(a), d * math.sin(a), math.degrees(a) - 90))
    both(cat, "mp_sonota", "汗しぶき_大", unary_union(parts))
    # 十字キラ（丸つき）
    g = unary_union([sparkle(8, thin=0.1), Point(0, 0).buffer(1.6)])
    mk(cat, "mp_sonota", "十字キラ_光点").solid(g)
    g = unary_union([sparkle(8, thin=0.1), sparkle(5, thin=0.1, rot=math.pi / 4), Point(0, 0).buffer(1.4)])
    mk(cat, "mp_sonota", "キラッ_八方光").solid(g)
    # 冷や汗の縦線（ほほ）
    mk(cat, "mp_sonota", "冷や汗_縦線").solid(unary_union([tapered((i * 1.5, 0), (i * 1.5, 7 + (i % 2) * 2), 0.5, 0.0, round_tip=False) for i in range(4)]))
    # 汗ぽたぽた（しずく＋落ちる跡）
    g = unary_union([drop(8), drop(5, 0, 11), drop(3, 0, 18)])
    both(cat, "mp_sonota", "汗ぽたぽた", g)

    for it in ITEMS:
        it.path = it.save()
    return ITEMS


if __name__ == "__main__":
    items = build()
    print(len(items), "items")
    print(Counter(it.cat for it in items))
