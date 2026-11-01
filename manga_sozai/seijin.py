"""成人向けエフェクト集ジェネレーター.

ハート吹き出し・ハート記号・吐息/湯気・汗/しずく・震え・背景・修正素材.
いずれも描写そのものではなく「演出用の効果素材」. 白黒原稿向け.
"""
import math
import os
from collections import Counter

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from shapely import affinity

from sozai import (BLACK, WHITE, Canvas, bezier, clip_rect, closing, dashed_outline, ellipse, fit_canvas, heart,
                   outline_ring, ray_hit, rng, rounded_rect, sparkle, star, tapered, tapered_curve, wedge_along)
from fukidashi import DIRS, body_cloud, tail
from manpu import drop
from kouka import poisson, SIZES

LW = 0.45
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "seijin")
ITEMS = []


class Item:
    def __init__(self, cat, name, ja, size=None):
        self.cat, self.name, self.ja, self.size = cat, name, ja, size
        self.layers = []

    def line(self, g, lw=LW):
        self.layers += [(g, WHITE), (outline_ring(g, lw), BLACK)]
        return self

    def solid(self, g, color=BLACK):
        self.layers.append((g, color))
        return self

    def save(self):
        if self.size:
            w, h, _ = SIZES[self.size]
            cv = Canvas(w, h)
            box = clip_rect(w, h)
            for g, c in self.layers:
                cv.add(g.intersection(box), c)
        else:
            cv = fit_canvas([g for g, _ in self.layers], margin=1.2)
            for g, c in self.layers:
                cv.add(g, c)
        base = os.path.join(OUT, self.cat, self.name)
        cv.save(base)
        return base + ".svg"


def mk(cat, prefix, ja, size=None):
    n = sum(1 for it in ITEMS if it.cat == cat) + 1
    it = Item(cat, "{}_{:03d}".format(prefix, n), ja + ("_" + SIZES[size][2] if size else ""), size)
    ITEMS.append(it)
    return it


def both(cat, prefix, ja, g, lw=LW):
    mk(cat, prefix, ja + "_線画").line(g, lw)
    mk(cat, prefix, ja + "_ベタ").solid(g)


# ---------------------------------------------------------------- shapes
def perturb(P, n, off):
    """外周を n 点に分け、重心から外向きに off(i, x, y) だけ動かす."""
    ring = LineString(P.exterior.coords)
    L = ring.length
    c = P.centroid
    pts = []
    for i in range(n):
        p = ring.interpolate(L * i / n)
        dx, dy = p.x - c.x, p.y - c.y
        d = math.hypot(dx, dy) or 1
        o = off(i, p.x, p.y)
        pts.append((p.x + dx / d * o, p.y + dy / d * o))
    return Polygon(pts).buffer(0)


def spiky_heart(h, k, depth, r):
    H = heart(h)
    pts = []
    ring = LineString(H.exterior.coords)
    L = ring.length
    c = H.centroid
    for i in range(2 * k):
        p = ring.interpolate(L * (i + 0.5) / (2 * k))
        dx, dy = p.x - c.x, p.y - c.y
        d = math.hypot(dx, dy) or 1
        o = depth * r.uniform(0.7, 1.2) if i % 2 == 0 else -depth * 0.15
        pts.append((p.x + dx / d * o, p.y + dy / d * o))
    return Polygon(pts).buffer(0)


def scallop_heart(h, k, bump):
    H = heart(h)
    ring = LineString(H.exterior.coords)
    L = ring.length
    return unary_union([H] + [Point(ring.interpolate(L * i / k).coords[0]).buffer(bump, quad_segs=20) for i in range(k)])


def melting_heart(h, r, k=3):
    H = heart(h)
    minx, miny, maxx, maxy = H.bounds
    parts = [H]
    for j in range(k):
        x = minx + (maxx - minx) * (0.3 + 0.4 * (j + 0.5) / k) + r.uniform(-1, 1)
        yb = max(p[1] for p in LineString([(x, miny - 1), (x, maxy + 1)]).intersection(H).coords) if True else maxy
        L = r.uniform(h * 0.2, h * 0.45)
        w = r.uniform(h * 0.07, h * 0.1)
        parts.append(Polygon([(x - w / 2, yb - 2), (x + w / 2, yb - 2), (x + w / 2, yb + L), (x - w / 2, yb + L)]))
        parts.append(Point(x, yb + L).buffer(w * 0.62, quad_segs=16))
    return closing(unary_union(parts), h * 0.03)


def strand(p0, p1, sag, w, beads=0, r=None):
    """糸引き：たるんだ細い線（しずくの粒つき）."""
    mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + sag * 2)
    pts = bezier(p0, mid, p1, 40)
    g = tapered_curve(pts, w, 0.15, 0.15, min_w=w * 0.35)
    parts = [g]
    for b in range(beads):
        t = (b + 1) / (beads + 1) + (r.uniform(-0.08, 0.08) if r else 0)
        q = pts[int(t * 40)]
        parts.append(Point(q[0], q[1] + w * 0.3).buffer(w * 1.25, quad_segs=16))
    return unary_union(parts)


def breath(r, size=1.0):
    """吐息：小さな雲＋くるっと巻いた尾."""
    c = body_cloud(5 * size, 3.4 * size, 7, 1.7 * size, r, 0.25)
    curl = []
    for i in range(40):
        t = i / 39
        a = math.pi * 0.2 + t * math.pi * 1.6
        rad = 2.6 * size * (1 - 0.5 * t)
        curl.append((-5.5 * size - 4 * size * t + rad * math.cos(a), 1.5 * size + rad * math.sin(a)))
    return c, tapered_curve(curl, 0.8 * size, 0.0, 0.7)


def steam_group(n, h, amp, lw, r, spacing=4.0):
    parts = []
    for k in range(n):
        hh = h * r.uniform(0.7, 1.1)
        ph = r.uniform(0, 6.28)
        pts = [(k * spacing + amp * math.sin(t * 2 * math.pi * 1.4 + ph) * (0.4 + t), -t * hh) for t in [i / 60 for i in range(61)]]
        parts.append(tapered_curve(pts, lw * r.uniform(0.8, 1.1), 0.3, 0.5))
    return unary_union(parts)


def pant_lines(n, r, L=5):
    """はぁはぁ：口元から出る短い曲線."""
    parts = []
    for k in range(n):
        a = math.radians(-40 + 80 * k / max(1, n - 1)) + r.uniform(-0.1, 0.1)
        p0 = (3 * math.cos(a), 3 * math.sin(a))
        p2 = ((3 + L) * math.cos(a), (3 + L) * math.sin(a))
        p1 = ((3 + L / 2) * math.cos(a + 0.25), (3 + L / 2) * math.sin(a + 0.25))
        parts.append(tapered_curve(bezier(p0, p1, p2, 16), 0.8, 0.2, 0.6))
    return unary_union(parts)


def twitch_marks(pairs, r, size=1.0):
    """ビクビク：小さなカッコ型の線を2本ずつ."""
    parts = []
    for k in range(pairs):
        cx, cy = r.uniform(-14, 14) * size, r.uniform(-10, 10) * size
        ang = r.uniform(0, 2 * math.pi)
        for j in range(2):
            rad = (2.2 + j * 1.6) * size
            pts = [(cx + rad * math.cos(ang + t), cy + rad * math.sin(ang + t)) for t in [(-0.6 + 1.2 * i / 14) for i in range(15)]]
            parts.append(tapered_curve(pts, 0.6 * size, 0.3, 0.3))
    return unary_union(parts)


def zigzag_mark(L, amp, n, lw):
    pts = [(L * i / n, amp * (1 if i % 2 else -1)) for i in range(n + 1)]
    return tapered_curve(pts, lw, 0.15, 0.15)


def heart_focus(w, h, hs, n, wmax, spread, r):
    """ハート形の穴があいた集中線."""
    H = heart(hs, w / 2, h / 2)
    c = (w / 2, h / 2 + hs * 0.05)
    R = math.hypot(w, h)
    lines = []
    for i in range(n):
        a = 2 * math.pi * i / n + r.gauss(0, 0.6 / n)
        e = ray_hit(H, a, c)
        m = 1 + spread * r.random() ** 1.6
        ex, ey = c[0] + (e[0] - c[0]) * m, c[1] + (e[1] - c[1]) * m
        lines.append(tapered((c[0] + R * math.cos(a), c[1] + R * math.sin(a)), (ex, ey), wmax * r.uniform(0.35, 1.0) * 2.2, 0.0, round_tip=False))
    return unary_union(lines)


def heart_flash(cx, cy, hs, n, Lmin, Lmax, w, r, beta=False):
    H = heart(hs, cx, cy)
    c = (cx, cy + hs * 0.05)
    parts = []
    for i in range(n):
        a = 2 * math.pi * i / n + r.gauss(0, 0.4 / n)
        e = ray_hit(H, a, c)
        L = r.uniform(Lmin, Lmax)
        p1 = (e[0] + L * math.cos(a), e[1] + L * math.sin(a))
        if beta:
            parts.append(tapered(e, p1, w * r.uniform(0.7, 1.3), 0.0, round_tip=False))
        else:
            p0 = (e[0] + 1.5 * math.cos(a), e[1] + 1.5 * math.sin(a))
            parts.append(tapered_curve([p0, p1], w * r.uniform(0.5, 1.0), 0.15, 0.85))
    g = unary_union(parts)
    if beta:
        g = unary_union([g, outline_ring(H, 2.0)]).difference(H)
    return g


# ---------------------------------------------------------------- catalog
def build():
    # 01 ハート吹き出し
    cat = "01_heart_fuki"
    P = "sj_hfuki"
    for h_, fat, ja in [(40, 1.0, "標準"), (36, 1.25, "ぽってり")]:
        H = heart(h_, fat=fat)
        mk(cat, P, "ハート吹き出し_" + ja).line(H)
        for deg, dj in [(128, "左下"), (52, "右下")]:
            mk(cat, P, "ハート吹き出し_{}_尻尾{}".format(ja, dj)).line(tail(H, deg, L=9, bw=6, bend=0.3 if deg == 128 else -0.3))
    for k, dep, ja in [(16, 3.2, "トゲ"), (26, 2.0, "細トゲ")]:
        mk(cat, P, "ハート叫び_" + ja).line(spiky_heart(40, k, dep, rng("sph", k)))
    mk(cat, P, "ハートふわふわ").line(scallop_heart(38, 30, 2.2))
    mk(cat, P, "ハート震え").line(perturb(heart(40), 160, lambda i, x, y: 0.7 * (1 if i % 2 else -1)))
    mk(cat, P, "ハート波打ち").line(perturb(heart(40), 400, lambda i, x, y: 0.9 * math.sin(i / 400 * 2 * math.pi * 22)))
    H = heart(40)
    mk(cat, P, "ハート二重線").solid(H, WHITE).solid(outline_ring(H, LW)).solid(outline_ring(H.buffer(-1.4), LW * 0.7))
    mk(cat, P, "ハートささやき_点線").solid(H, WHITE).solid(dashed_outline(H, LW, LW, 1.0))
    mk(cat, P, "ハートベタ").solid(H)
    mk(cat, P, "ハート溶け").line(melting_heart(38, rng("melt0")))
    mk(cat, P, "ハート溶け_ベタ").solid(melting_heart(38, rng("melt1")))
    it = mk(cat, P, "ハート思考_あぶく")
    it.line(H)
    for hh in [heart(7, -15, 22), heart(4.5, -21, 28)]:
        it.line(hh)
    E = ellipse(13, 20)
    it = mk(cat, P, "楕円_ハート尻尾")
    it.line(E.union(heart(9, -11, 19)).buffer(0.01))
    it = mk(cat, P, "楕円_ハート散らし")
    it.line(E)
    for ang, sz in [(-50, 7), (-25, 5), (200, 6), (150, 4)]:
        th = math.radians(ang)
        it.line(heart(sz, 13 * 1.05 * math.cos(th), 20 * 1.05 * math.sin(th)))

    # 02 ハート記号
    cat = "02_heart_mark"
    P = "sj_hmark"
    for sz, ja in [(10, "小"), (16, "大")]:
        both(cat, P, "ハート_" + ja, heart(sz))
    H = heart(14)
    mk(cat, P, "ハート_白フチ二重").solid(H.buffer(1.4)).solid(H.buffer(0.7), WHITE).solid(H)
    hs = [affinity.rotate(heart(10 - i * 1.6, i * 9, -i * 1.5), -8 - i * 6) for i in range(4)]
    both(cat, P, "ハート連打_4つ", unary_union(hs))
    hs = [affinity.rotate(heart(8 - i * 2, i * 7.5, 0), (i % 2) * 10 - 5) for i in range(3)]
    both(cat, P, "ハート連打_3つ", unary_union(hs))
    for k, ja in [(9, "乱れ散らし"), (14, "乱れ散らし_多")]:
        r = rng("hscat", k)
        pts = poisson(40, 30, 7.5, r, margin=3)[:k]
        hs = [affinity.rotate(heart(r.uniform(3.5, 8), x, y), r.uniform(-30, 30)) for x, y in pts]
        g = unary_union(hs)
        it = mk(cat, P, ja + "_線画")
        for hh in hs:
            it.line(hh, LW * 0.8)
        mk(cat, P, ja + "_ベタ").solid(g)
    H = heart(12)
    mot = unary_union([tapered((x, 9 + abs(x) * 0.3), (x * 1.4, 15 + abs(x) * 0.3), 0.8, 0.0) for x in (-4, 0, 4)])
    mk(cat, P, "飛び出すハート_線画").line(H).solid(mot)
    mk(cat, P, "飛び出すハート_ベタ").solid(H).solid(mot)
    lines = unary_union([tapered((10 * math.cos(math.radians(a)), 10 * math.sin(math.radians(a))),
                                 (7.5 * math.cos(math.radians(a)), 7.5 * math.sin(math.radians(a))), 0.9, 0) for a in range(0, 360, 30)])
    mk(cat, P, "ハートずきずき_線画").line(heart(11)).solid(lines)
    mk(cat, P, "ハートずきずき_ベタ").solid(heart(11)).solid(lines)
    both(cat, P, "ハート目_ペア", unary_union([heart(9, 0, 0), heart(9, 18, 0)]))
    g = unary_union([heart(9, 0, 0), heart(9, 18, 0)])
    mk(cat, P, "ハート目_ハイライト付き").solid(g).solid(unary_union([Point(-1.8, -1.2).buffer(1.1), Point(16.2, -1.2).buffer(1.1)]), WHITE)
    it = mk(cat, P, "ハートの泡")
    for (x, y, rr) in [(0, 0, 6), (9, -8, 4), (-5, -11, 3)]:
        it.line(Point(x, y).buffer(rr, quad_segs=32), LW * 0.8)
        it.solid(heart(rr * 0.9, x, y))
    g = unary_union([heart(11), sparkle(4, 8, -7), sparkle(2.5, -8, -6)])
    both(cat, P, "ハート_キラ", g)

    # 03 吐息・湯気
    cat = "03_toiki"
    P = "sj_toiki"
    for i, sz in enumerate([1.0, 1.3]):
        c, curl = breath(rng("br", i), sz)
        mk(cat, P, "吐息_{}".format("小" if i == 0 else "大")).line(c).solid(curl)
    c, curl = breath(rng("brh"), 1.3)
    mk(cat, P, "吐息_ハート入り").line(c).solid(curl).solid(heart(3.6, 0.5, 0))
    for n, ja in [(4, "4本"), (6, "6本")]:
        mk(cat, P, "はぁはぁ線_" + ja).solid(pant_lines(n, rng("pant", n)))
    for si, (n, h, amp, ja) in enumerate([(3, 16, 1.3, "3本"), (5, 22, 1.6, "5本"), (8, 30, 2.0, "8本_大")]):
        mk(cat, P, "湯気_" + ja).solid(steam_group(n, h, amp, 0.9, rng("st", si), spacing=4.2))
    g = steam_group(16, 34, 2.2, 0.8, rng("stw"), spacing=4.5)
    mk(cat, P, "湯気_全身用_横長").solid(g)
    r = rng("moya")
    loops = []
    for (x, y) in poisson(50, 30, 12, r, margin=4):
        e = perturb(ellipse(r.uniform(4, 7), r.uniform(2.5, 4), x, y), 120, lambda i, a, b: 0.5 * math.sin(i / 120 * 6.28 * 5))
        loops.append(outline_ring(e, 0.4))
    mk(cat, P, "熱気もやもや").solid(unary_union(loops))
    c = body_cloud(7, 4.5, 8, 2.2, rng("hpuff"), 0.2)
    mk(cat, P, "ため息_ハート").line(c).solid(heart(3, -9.5, 4)).solid(heart(2.2, -12.5, 7))

    # 04 汗・しずく
    cat = "04_shizuku"
    P = "sj_shizuku"
    for k, md, ja in [(14, 6, "汗粒_ちらし"), (26, 4.5, "汗粒_びっしり")]:
        r = rng("asep", k)
        pts = poisson(40, 30, md, r, margin=3)[:k]
        ds = [drop(r.uniform(2, 4.2), x, y, r.uniform(-25, 25)) for x, y in pts]
        it = mk(cat, P, ja + "_線画")
        for d in ds:
            it.line(d, LW * 0.7)
        mk(cat, P, ja + "_ベタ").solid(unary_union(ds))
    # テカリ（肌のハイライト線）
    r = rng("teka")
    arcs = []
    for k in range(5):
        x0, y0 = r.uniform(-8, 8), r.uniform(-6, 6)
        L = r.uniform(3, 7)
        arcs.append(tapered_curve(bezier((x0, y0), (x0 + L / 2, y0 - L * 0.25), (x0 + L, y0), 14), 0.9, 0.4, 0.4))
    g = unary_union(arcs)
    mk(cat, P, "テカリ_黒線").solid(g)
    mk(cat, P, "テカリ_白線（黒い部分に）").solid(g.buffer(0.35), BLACK).solid(g, WHITE)
    ds = [drop(s, x, 0) for s, x in [(4, 0), (6, 6), (8, 14), (10, 24)]]
    both(cat, P, "しずく_大小4つ", unary_union(ds))
    for i in range(2):
        r = rng("dripl", i)
        parts = [Polygon([(0, -1.2), (40, -1.2), (40, 0), (0, 0)])]
        for j in range(5):
            x = 4 + j * 8 + r.uniform(-2, 2)
            L = r.uniform(3, 12)
            w = r.uniform(1.6, 2.6)
            parts.append(Polygon([(x - w / 2, -0.5), (x + w / 2, -0.5), (x + w * 0.35, L), (x - w * 0.35, L)]))
            parts.append(drop(w * 1.6, x, L + w * 0.4))
        g = closing(unary_union(parts), 0.8)
        mk(cat, P, "垂れるしずく_{}_線画".format(i + 1)).line(g)
        mk(cat, P, "垂れるしずく_{}_ベタ".format(i + 1)).solid(g)
    for i in range(2):
        r = rng("spl", i)
        parts = []
        for k in range(14):
            a = r.uniform(-math.pi, 0)
            d = r.uniform(5, 15)
            if r.random() < 0.45:
                parts.append(Point(d * math.cos(a), d * math.sin(a)).buffer(r.uniform(0.4, 1.0)))
            else:
                parts.append(drop(r.uniform(2.2, 4.2), d * math.cos(a), d * math.sin(a), math.degrees(a) - 90))
        both(cat, P, "飛沫_{}".format(i + 1), unary_union(parts))
    for i, (sag, beads, ja) in enumerate([(3, 0, "糸引き_細"), (5, 2, "糸引き_しずく付き"), (2, 1, "糸引き_短")]):
        r = rng("str", i)
        g = unary_union([strand((0, 0), (22 if i != 2 else 12, 0), sag, 0.55, beads, r),
                         strand((0, 1.2), (20 if i != 2 else 11, 2.2), sag * 1.3, 0.4, 0, r)])
        mk(cat, P, ja).solid(g)
    for i in range(2):
        r = rng("dro", i)
        L = 10 + i * 6
        pts = [(0.8 * math.sin(t * 3), t * L) for t in [k / 30 for k in range(31)]]
        g = unary_union([tapered_curve(pts, 1.0, 0.0, 0.3), drop(3.4, pts[-1][0], L + 1.4)])
        mk(cat, P, "よだれ_{}_線画".format(i + 1)).line(g, LW * 0.7)
        mk(cat, P, "よだれ_{}_ベタ".format(i + 1)).solid(g)

    # 05 震え・ビクビク
    cat = "05_furue"
    P = "sj_furue"
    for k, ja in [(4, "少"), (7, "多")]:
        mk(cat, P, "ビクビク_" + ja).solid(twitch_marks(k, rng("tw", k)))
    for n, ja in [(2, "2本"), (3, "3本")]:
        g = unary_union([affinity.translate(zigzag_mark(9, 1.2, 6, 0.6), 0, i * 4) for i in range(n)])
        mk(cat, P, "ガクガク_" + ja).solid(g)
    for pairs, ja in [(1, "1重"), (2, "2重"), (3, "3重")]:
        parts = []
        for side in [-1, 1]:
            for k in range(pairs):
                x = side * (14 + k * 2.6)
                arc = [(x + side * 1.6 * math.sin(math.pi * t), -6 + 12 * t) for t in [i / 20 for i in range(21)]]
                parts.append(tapered_curve(arc, 0.7, 0.3, 0.3))
        mk(cat, P, "小刻み震え_" + ja).solid(unary_union(parts))
    for i in range(2):
        r = rng("keir", i)
        parts = []
        for k in range(10):
            a = 2 * math.pi * k / 10 + r.uniform(-0.15, 0.15)
            pts = []
            for j in range(30):
                t = j / 29
                d = 6 + t * (5 + i * 3)
                o = 0.6 * math.sin(t * 2 * math.pi * 2)
                pts.append((d * math.cos(a) - o * math.sin(a), d * math.sin(a) + o * math.cos(a)))
            parts.append(tapered_curve(pts, 0.7, 0.2, 0.6))
        mk(cat, P, "痙攣線_{}".format("短" if i == 0 else "長")).solid(unary_union(parts))
    parts = [tapered((x, 0), (x, 6 + (x % 3)), 0.55, 0.0, round_tip=False) for x in range(0, 14, 2)]
    mk(cat, P, "ゾクッ_縦線").solid(unary_union(parts))

    # 06 背景
    cat = "06_haikei"
    P = "sj_haikei"
    for sk in ["tate", "yoko", "sq"]:
        w, h, _ = SIZES[sk]
        m = min(w, h)
        mk(cat, P, "ハート集中線", sk).solid(heart_focus(w, h, m * 0.42, 280, 0.5, 0.45, rng("hf", sk)))
    for sk in ["tate", "sq"]:
        w, h, _ = SIZES[sk]
        m = min(w, h)
        mk(cat, P, "ハートウニフラ", sk).solid(heart_flash(w / 2, h / 2, m * 0.36, 150, m * 0.08, m * 0.22, 0.45, rng("hu", sk)))
        mk(cat, P, "ハートベタフラ", sk).solid(heart_flash(w / 2, h / 2, m * 0.36, 70, m * 0.08, m * 0.26, 2.6, rng("hb", sk), beta=True))
    for sk in ["tate", "yoko", "sq"]:
        w, h, _ = SIZES[sk]
        r = rng("hbg", sk)
        parts = []
        for (x, y) in poisson(w, h, 11, r, margin=-2):
            u = r.random()
            if u < 0.55:
                hh = affinity.rotate(heart(r.uniform(2.5, 7), x, y), r.uniform(-25, 25))
                parts.append(hh if r.random() < 0.3 else outline_ring(hh, 0.35))
            elif u < 0.8:
                parts.append(sparkle(r.uniform(1.5, 4), x, y))
            else:
                parts.append(Point(x, y).buffer(0.5))
        mk(cat, P, "ハート＆キラキラ散らし", sk).solid(unary_union(parts))
    for sk in ["tate", "sq"]:
        w, h, _ = SIZES[sk]
        r = rng("moyabg", sk)
        loops = []
        for (x, y) in poisson(w, h, 22, r, margin=-6):
            e = perturb(ellipse(r.uniform(7, 13), r.uniform(4, 8), x, y), 160,
                        lambda i, a, b, ph=r.uniform(0, 6): 0.8 * math.sin(i / 160 * 6.28 * 6 + ph))
            loops.append(outline_ring(e, 0.4))
        mk(cat, P, "もやもや背景", sk).solid(unary_union(loops))
    for pitch, ja in [(9, "ハート柄_小"), (15, "ハート柄_大")]:
        parts = []
        for j in range(int(120 / pitch) + 2):
            for i in range(int(120 / pitch) + 2):
                x = i * pitch + (pitch / 2 if j % 2 else 0)
                y = j * pitch * 0.9
                parts.append(heart(pitch * 0.42, x, y))
        mk(cat, P, ja, "sq").solid(unary_union(parts))

    # 07 修正素材
    cat = "07_shusei"
    P = "sj_shusei"
    for w_, h_, ang, ja in [(30, 6, 0, "黒棒_短"), (50, 7, 0, "黒棒_長"), (30, 6, -25, "黒棒_斜め"),
                            (20, 5, 0, "黒棒_極短")]:
        mk(cat, P, ja).solid(affinity.rotate(rounded_rect(w_, h_, 0.8), ang, origin=(0, 0)))
    for w_, h_, ja in [(30, 6, "白棒_短"), (50, 7, "白棒_長")]:
        mk(cat, P, ja).line(rounded_rect(w_, h_, 0.8), LW * 0.6)
    mk(cat, P, "ハート隠し_黒").solid(heart(18))
    mk(cat, P, "ハート隠し_白").line(heart(18), LW * 0.6)
    r = rng("hcl")
    hs = [affinity.rotate(heart(r.uniform(7, 11), x, y), r.uniform(-20, 20)) for x, y in [(0, 0), (8, -5), (8, 5), (-7, 4), (-6, -5)]]
    mk(cat, P, "ハート隠し_かたまり_黒").solid(unary_union(hs))
    mk(cat, P, "星隠し_黒").solid(star(10, 4.6, 5))
    mk(cat, P, "星隠し_白").line(star(10, 4.6, 5), LW * 0.6)
    for i in range(2):
        r = rng("hika", i)
        core = perturb(ellipse(10 + i * 4, 7 + i * 3), 60, lambda k, x, y: r.uniform(-0.6, 1.4) if k % 2 else 0)
        lines = []
        for k in range(48):
            a = 2 * math.pi * k / 48 + r.uniform(-0.04, 0.04)
            e = ray_hit(core, a)
            L = r.uniform(3, 9)
            lines.append(tapered_curve([(e[0] + math.cos(a), e[1] + math.sin(a)), (e[0] + (1 + L) * math.cos(a), e[1] + (1 + L) * math.sin(a))],
                                       0.5, 0.1, 0.8))
        mk(cat, P, "光修正_{}".format("小" if i == 0 else "大")).solid(core.buffer(1.5), WHITE).solid(unary_union(lines))
    for i in range(2):
        c = body_cloud(10 + i * 4, 6 + i * 2, 10, 3.2, rng("yuge", i), 0.3)
        mk(cat, P, "湯気隠し_{}".format("小" if i == 0 else "大")).line(c, LW * 0.5)

    for it in ITEMS:
        it.path = it.save()
    return ITEMS


if __name__ == "__main__":
    items = build()
    print(len(items), "items")
    print(Counter(it.cat for it in items))
