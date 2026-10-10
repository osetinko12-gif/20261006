"""吹き出し集ジェネレーター.

基本サイズ：縦長の楕円でおよそ 28×40mm（B5原稿で等倍）。線幅 0.45mm。
日本語の縦書きセリフが入る縦長を基本に、横長・円も用意する。
"""
import math
import os
import sys

from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
from shapely import affinity

from sozai import (BLACK, WHITE, bezier, closing, dashed_outline, ellipse, fit_canvas, heart,
                   outline_ring, radial, ray_hit, rng, rounded_rect, wedge_along)

LW = 0.45
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "fukidashi")

# 向き（画面座標・y下向き）
DIRS = {
    "LD": (125, "左下"), "RD": (55, "右下"), "L": (170, "左"), "R": (10, "右"),
    "D": (92, "下"), "LU": (215, "左上"), "RU": (325, "右上"),
}
# 縦横比
ASPECT = {
    "tate": (13.0, 20.0, "縦長"), "tate2": (13.5, 17.0, "やや縦長"),
    "maru": (15.0, 15.0, "円"), "yoko": (21.0, 13.0, "横長"),
}


# ---------------------------------------------------------------- tails
def tail(S, deg, L=9.0, bw=6.0, bend=0.35, kind="curve"):
    """形Sに尻尾をつける. bend: 先端の横ずれ（Lに対する比）."""
    phi = math.radians(deg)
    ex, ey = ray_hit(S, phi)
    ux, uy = math.cos(phi), math.sin(phi)
    px, py = -uy, ux
    start = (ex - ux * 3, ey - uy * 3)
    tip = (ex + ux * L + px * bend * L, ey + uy * L + py * bend * L)
    if kind == "straight":
        coords = [start, tip]
        T = wedge_along(coords, bw, 0.0, 1.0)
    elif kind == "curve":
        ctrl = (ex + ux * L * 0.6, ey + uy * L * 0.6)
        T = wedge_along(bezier(start, ctrl, tip, 30), bw, 0.0, 0.85)
    elif kind == "thin":  # 細長い尻尾
        ctrl = (ex + ux * L * 0.5 - px * bend * L * 0.4, ey + uy * L * 0.5 - py * bend * L * 0.4)
        T = wedge_along(bezier(start, ctrl, tip, 30), bw * 0.65, 0.0, 1.2)
    elif kind == "zigzag":  # 稲妻（電話・機械）: 太い根元から鋭く折れる
        P = lambda t, side: (ex + ux * L * t + px * side, ey + uy * L * t + py * side)
        w = bw * 0.9
        left = [P(-0.35, w / 2), P(0.0, w / 2), P(0.42, 3.4), P(0.38, -0.2), P(0.78, 1.6), P(0.72, -1.6), P(1.0, -0.6)]
        right = [P(-0.35, -w / 2), P(0.0, -w / 2), P(0.30, 0.4), P(0.26, -3.0), P(0.62, -1.2)]
        T = Polygon(left + right[::-1]).buffer(0)
        return closing(S.union(T), 0.5)
    else:
        raise ValueError(kind)
    return closing(S.union(T), 1.2)


def spike_tail(S, deg, L=10.0, bw=5.0):
    phi = math.radians(deg)
    ex, ey = ray_hit(S, phi)
    ux, uy = math.cos(phi), math.sin(phi)
    px, py = -uy, ux
    T = Polygon([(ex - ux * 4 + px * bw / 2, ey - uy * 4 + py * bw / 2),
                 (ex + ux * L, ey + uy * L),
                 (ex - ux * 4 - px * bw / 2, ey - uy * 4 - py * bw / 2)])
    return S.union(T).buffer(0)


def thought_tail(deg, S, n=3, r0=2.6, gap=1.6):
    phi = math.radians(deg)
    ex, ey = ray_hit(S, phi)
    ux, uy = math.cos(phi), math.sin(phi)
    out = []
    d = gap + r0
    r = r0
    for i in range(n):
        out.append(Point(ex + ux * d, ey + uy * d).buffer(r, quad_segs=24))
        d += r + gap + r * 0.6
        r *= 0.62
    return out


# ---------------------------------------------------------------- bodies
def body_ellipse(a, b):
    return ellipse(a, b)


def body_spiky(a, b, k, depth, r, irregular=0.0, inner=1.0, curved=True, tail_deg=None, tail_len=0.0):
    """叫びフキダシ. curved=True でトゲの間が内側に反る（漫画らしい形）.
    tail_deg を指定すると、その向きのトゲ1本を長く伸ばして尻尾にする."""
    tips = []
    for i in range(k):
        t = (i + r.uniform(-0.25, 0.25) * irregular) / k
        th = 2 * math.pi * t
        m = 1 + depth * (1 + r.uniform(-irregular, irregular) * 0.8)
        tips.append([th, m])
    if tail_deg is not None:
        want = math.radians(tail_deg) % (2 * math.pi)
        j = min(range(k), key=lambda q: abs((tips[q][0] - want + math.pi) % (2 * math.pi) - math.pi))
        tips[j][0] = want
        tips[j][1] += tail_len / ((a + b) / 2)
    pts = []
    for i in range(k):
        th0, m0 = tips[i]
        th1, m1 = tips[(i + 1) % k]
        if th1 < th0:
            th1 += 2 * math.pi
        p0 = (a * m0 * math.cos(th0), b * m0 * math.sin(th0))
        p1 = (a * m1 * math.cos(th1), b * m1 * math.sin(th1))
        mid = (th0 + th1) / 2
        mi = inner * (1 + r.uniform(-0.04, 0.04) * irregular)
        if curved:
            c = (a * mi * 0.86 * math.cos(mid), b * mi * 0.86 * math.sin(mid))
            pts += bezier(p0, c, p1, 18)[:-1]
        else:
            pts += [p0, (a * mi * math.cos(mid), b * mi * math.sin(mid))]
    return Polygon(pts).buffer(0)


def body_cloud(a, b, k, bump, r, irregular=0.25):
    """もこもこ雲. kはこぶの数."""
    base = ellipse(a, b)
    ring = base.exterior
    L = ring.length
    parts = [base]
    for i in range(k):
        p = ring.interpolate(L * (i + r.uniform(-0.15, 0.15) * irregular) / k)
        rr = bump * (1 + r.uniform(-irregular, irregular))
        parts.append(Point(p.x, p.y).buffer(rr, quad_segs=24))
    return unary_union(parts).buffer(0)


def body_scallop(a, b, k, bump):
    """ふんわり（こぶが均一）."""
    base = ellipse(a, b)
    ring = base.exterior
    L = ring.length
    parts = [base] + [Point(ring.interpolate(L * i / k).coords[0]).buffer(bump, quad_segs=24)
                      for i in range(k)]
    return unary_union(parts).buffer(0)


def body_wave(a, b, k, amp, phase=0.0):
    return radial(a, b, lambda t: 1 + amp * math.sin(2 * math.pi * (k * t + phase)), n=1440)


def body_jitter(a, b, k, amp, r):
    """ガタガタ（震え）."""
    pts = []
    for i in range(2 * k):
        th = 2 * math.pi * i / (2 * k)
        m = 1 + (amp if i % 2 == 0 else -amp) * r.uniform(0.6, 1.0)
        pts.append((a * m * math.cos(th), b * m * math.sin(th)))
    return Polygon(pts).buffer(0)


def body_wobble(a, b, r, amp=0.06, k=5):
    """へにょっとした手描きっぽいゆがみ."""
    ph = [r.uniform(0, 1) for _ in range(3)]
    am = [amp * r.uniform(0.5, 1.0) for _ in range(3)]
    return radial(a, b, lambda t: 1 + am[0] * math.sin(2 * math.pi * (2 * t + ph[0]))
                  + am[1] * math.sin(2 * math.pi * (3 * t + ph[1]))
                  + am[2] * 0.5 * math.sin(2 * math.pi * (k * t + ph[2])))


def body_octagon(a, b, cut=0.32):
    """角ばった機械的なフキダシ."""
    ca, cb = a * cut, b * cut
    return Polygon([(-a + ca, -b), (a - ca, -b), (a, -b + cb), (a, b - cb),
                    (a - ca, b), (-a + ca, b), (-a, b - cb), (-a, -b + cb)])


def body_flower(a, b, k, depth):
    return radial(a, b, lambda t: 1 - depth + depth * abs(math.sin(math.pi * k * t)) ** 0.6, n=1440)


# ---------------------------------------------------------------- render
class Item:
    def __init__(self, cat, name, ja):
        self.cat, self.name, self.ja = cat, name, ja
        self.layers = []  # (geom, color)

    def white_lined(self, S, lw=LW, extra=()):
        self.layers.append((S, WHITE))
        self.layers.append((outline_ring(S, lw), BLACK))
        for g in extra:
            self.layers.append((g, WHITE))
            self.layers.append((outline_ring(g, lw), BLACK))
        return self

    def save(self):
        geoms = [g for g, _ in self.layers]
        cv = fit_canvas(geoms, margin=1.5)
        for g, c in self.layers:
            cv.add(g, c)
        base = os.path.join(OUT, self.cat, self.name)
        cv.save(base)
        return base + ".svg"


ITEMS = []


def add(cat, name, ja):
    it = Item(cat, name, ja)
    ITEMS.append(it)
    return it


def build():
    n = 0

    # 01 通常（楕円）
    cat = "01_normal"
    i = 0
    for ak, (a, b, aj) in ASPECT.items():
        variants = [(None, None)] + [("LD", "curve"), ("RD", "curve"), ("L", "curve"), ("R", "curve"),
                                     ("D", "straight"), ("LD", "thin"), ("RD", "thin")]
        for dk, kind in variants:
            i += 1
            S = body_ellipse(a, b)
            if dk:
                deg, dj = DIRS[dk]
                bend = {"LD": 0.35, "RD": -0.35, "L": -0.3, "R": 0.3}.get(dk, 0)
                if kind == "straight":
                    bend = 0
                S = tail(S, deg, L=10 if kind != "thin" else 13, bw=6.5, bend=bend, kind=kind)
                ja = "楕円_{}_尻尾{}{}".format(aj, dj, "（細）" if kind == "thin" else "")
            else:
                ja = "楕円_{}_尻尾なし".format(aj)
            add(cat, "fk_normal_{:03d}".format(i), ja).white_lined(S)
    # 手描き風ゆがみ楕円
    for j in range(6):
        i += 1
        r = rng("wob", j)
        a, b = (13.5, 19.5) if j % 3 != 2 else (19, 13)
        S = body_wobble(a, b, r, amp=0.035)
        dk = ["LD", "RD", None, "L", "R", None][j]
        if dk:
            S = tail(S, DIRS[dk][0], L=10, bw=6, bend={"LD": 0.35, "RD": -0.35, "L": -0.3, "R": 0.3}[dk])
        add(cat, "fk_normal_{:03d}".format(i), "手描き風ゆがみ楕円_{}".format(DIRS[dk][1] if dk else "尻尾なし")).white_lined(S)

    # 02 ナレーション・角型
    cat = "02_box"
    i = 0
    boxes = [(24, 44, 0, "縦長_角"), (24, 44, 3, "縦長_角丸"), (30, 30, 0, "正方_角"), (30, 30, 4, "正方_角丸"),
             (44, 20, 0, "横長_角"), (44, 20, 3, "横長_角丸"), (18, 54, 0, "細長_角"), (18, 54, 9, "細長_丸端")]
    for w, h, rr, ja in boxes:
        i += 1
        S = rounded_rect(w, h, rr)
        add(cat, "fk_box_{:03d}".format(i), "ナレーション_" + ja).white_lined(S)
    for w, h, rr, ja in boxes[:6]:  # 二重枠
        i += 1
        S = rounded_rect(w, h, rr)
        inner = rounded_rect(w - 2.4, h - 2.4, max(0, rr - 1.2))
        it = add(cat, "fk_box_{:03d}".format(i), "二重枠_" + ja)
        it.layers += [(S, WHITE), (outline_ring(S, LW), BLACK), (outline_ring(inner, LW * 0.7), BLACK)]
    for w, h, rr, ja, dk in [(24, 40, 3, "縦長角丸", "LD"), (24, 40, 3, "縦長角丸", "RD"),
                             (40, 22, 2, "横長角丸", "D"), (26, 40, 0, "縦長角", "L")]:
        i += 1
        S = tail(rounded_rect(w, h, rr), DIRS[dk][0], L=9, bw=6, bend={"LD": 0.3, "RD": -0.3, "L": -0.3, "D": 0}[dk])
        add(cat, "fk_box_{:03d}".format(i), "尻尾つき_{}_{}".format(ja, DIRS[dk][1])).white_lined(S)
    # 斜めに傾いた箱（モノローグ演出）
    for j, ang in enumerate([-6, 5]):
        i += 1
        S = affinity.rotate(rounded_rect(24, 44, 0), ang, origin=(0, 0))
        add(cat, "fk_box_{:03d}".format(i), "傾き箱_{}度".format(ang)).white_lined(S)

    # 03 叫び（トゲ）
    cat = "03_shout"
    i = 0
    shout_specs = [
        (16, 0.22, 0.0, True, "トゲ_細かめ"), (11, 0.32, 0.0, True, "トゲ_大きめ"),
        (14, 0.30, 0.6, True, "不規則トゲ"), (18, 0.38, 0.9, True, "爆発"),
        (9, 0.42, 0.5, True, "大トゲ"), (22, 0.12, 0.0, False, "ギザギザ"),
    ]
    for si, (k, dep, irr, cv, ja) in enumerate(shout_specs):
        for ak in ["tate", "maru", "yoko"]:
            a, b, aj = ASPECT[ak]
            r = rng("shout", si, ak)
            S = body_spiky(a, b, k + (3 if ak == "yoko" else 0), dep, r, irregular=irr, curved=cv)
            i += 1
            add(cat, "fk_shout_{:03d}".format(i), "叫び_{}_{}".format(ja, aj)).white_lined(S)
        a, b, aj = ASPECT["tate"]
        for dk in ["LD", "RD"]:
            r = rng("shoutT", si, dk)
            S = body_spiky(a, b, k, dep, r, irregular=irr, curved=cv, tail_deg=DIRS[dk][0], tail_len=11)
            i += 1
            add(cat, "fk_shout_{:03d}".format(i), "叫び_{}_尻尾{}".format(ja, DIRS[dk][1])).white_lined(S)

    # 04 思考（雲）
    cat = "04_thought"
    i = 0
    for si, (k, bump, irr, ja) in enumerate([(11, 4.2, 0.25, "もこもこ"), (8, 5.5, 0.35, "大きなこぶ"),
                                             (16, 3.0, 0.15, "細かいこぶ"), (10, 4.8, 0.5, "ふぞろい")]):
        for ak in ["tate", "maru", "yoko"]:
            a, b, aj = ASPECT[ak]
            r = rng("cloud", si, ak)
            S = body_cloud(a - 2.5, b - 2.5, k + (3 if ak == "yoko" else 0), bump, r, irr)
            for dk in [None, "LD", "RD"]:
                i += 1
                extra = thought_tail(DIRS[dk][0], S) if dk else []
                add(cat, "fk_thought_{:03d}".format(i),
                    "思考_{}_{}_{}".format(ja, aj, ("あぶく" + DIRS[dk][1]) if dk else "あぶくなし")).white_lined(S, extra=extra)
    # 楕円＋あぶく
    for ak in ["tate", "yoko"]:
        a, b, aj = ASPECT[ak]
        for dk in ["LD", "RD"]:
            i += 1
            S = body_ellipse(a, b)
            add(cat, "fk_thought_{:03d}".format(i), "思考_楕円_{}_あぶく{}".format(aj, DIRS[dk][1])).white_lined(
                S, extra=thought_tail(DIRS[dk][0], S))

    # 05 震え・波
    cat = "05_shaky"
    i = 0
    for ak in ["tate", "maru", "yoko"]:
        a, b, aj = ASPECT[ak]
        for (k, amp, ja) in [(26, 0.025, "細かい波"), (14, 0.04, "大きい波")]:
            for dk in [None, "LD"]:
                i += 1
                S = body_wave(a, b, k, amp)
                if dk:
                    S = tail(S, DIRS[dk][0], L=10, bw=6, bend=0.35)
                add(cat, "fk_shaky_{:03d}".format(i), "震え_{}_{}_{}".format(ja, aj, "尻尾" + DIRS[dk][1] if dk else "尻尾なし")).white_lined(S)
        for (k, amp, ja) in [(40, 0.03, "ガタガタ"), (60, 0.018, "ブルブル")]:
            for dk in [None, "RD"]:
                i += 1
                r = rng("jit", ak, k, dk)
                S = body_jitter(a, b, k, amp, r)
                if dk:
                    S = tail(S, DIRS[dk][0], L=10, bw=6, bend=-0.35)
                add(cat, "fk_shaky_{:03d}".format(i), "震え_{}_{}_{}".format(ja, aj, "尻尾" + DIRS[dk][1] if dk else "尻尾なし")).white_lined(S)

    # 06 電話・機械
    cat = "06_electric"
    i = 0
    for ak in ["tate", "yoko"]:
        a, b, aj = ASPECT[ak]
        for dk in ["LD", "RD", "D"]:
            i += 1
            S = tail(body_ellipse(a, b), DIRS[dk][0], L=12, bw=6, kind="zigzag")
            add(cat, "fk_elec_{:03d}".format(i), "電話_楕円_{}_稲妻{}".format(aj, DIRS[dk][1])).white_lined(S)
        for dk in [None, "LD", "RD"]:
            i += 1
            S = body_octagon(a, b)
            if dk:
                S = tail(S, DIRS[dk][0], L=12, bw=6, kind="zigzag")
            add(cat, "fk_elec_{:03d}".format(i), "機械_八角_{}_{}".format(aj, "稲妻" + DIRS[dk][1] if dk else "尻尾なし")).white_lined(S)
        for dk in [None, "LD"]:
            i += 1
            r = rng("elecJ", ak, dk)
            S = body_spiky(a, b, 30, 0.07, r, irregular=0.0)
            if dk:
                S = tail(S, DIRS[dk][0], L=12, bw=6, kind="zigzag")
            add(cat, "fk_elec_{:03d}".format(i), "電子音_ギザ縁_{}_{}".format(aj, "稲妻" + DIRS[dk][1] if dk else "尻尾なし")).white_lined(S)

    # 07 ささやき（点線・破線）
    cat = "07_whisper"
    i = 0
    for ak in ["tate", "maru", "yoko"]:
        a, b, aj = ASPECT[ak]
        for (dash, gap, ja) in [(LW, 1.0, "点線"), (2.2, 1.3, "破線"), (5.0, 1.6, "長破線")]:
            for dk in [None, "LD"] if ak != "maru" else [None]:
                i += 1
                S = body_ellipse(a, b)
                if dk:
                    S = tail(S, DIRS[dk][0], L=10, bw=6, bend=0.35)
                it = add(cat, "fk_whisper_{:03d}".format(i), "ささやき_{}_{}_{}".format(ja, aj, "尻尾" + DIRS[dk][1] if dk else "尻尾なし"))
                it.layers += [(S, WHITE), (dashed_outline(S, LW, dash, gap), BLACK)]
    for (dash, gap, ja) in [(LW, 1.0, "点線"), (2.2, 1.3, "破線")]:
        i += 1
        S = rounded_rect(24, 42, 3)
        it = add(cat, "fk_whisper_{:03d}".format(i), "ささやき_箱_{}".format(ja))
        it.layers += [(S, WHITE), (dashed_outline(S, LW, dash, gap), BLACK)]
        i += 1
        r = rng("wcloud", ja)
        S = body_cloud(11, 17, 11, 4.0, r)
        it = add(cat, "fk_whisper_{:03d}".format(i), "ささやき_雲_{}".format(ja))
        it.layers += [(S, WHITE), (dashed_outline(S, LW, dash, gap), BLACK)]

    # 08 ベタ（黒）フキダシ
    cat = "08_black"
    i = 0
    for ak in ["tate", "yoko"]:
        a, b, aj = ASPECT[ak]
        shapes = [
            ("楕円", body_ellipse(a, b)),
            ("楕円_尻尾左下", tail(body_ellipse(a, b), DIRS["LD"][0], L=10, bw=6, bend=0.35)),
            ("トゲ", body_spiky(a, b, 14, 0.28, rng("bs", ak), irregular=0.6)),
            ("爆発", body_spiky(a, b, 18, 0.35, rng("bx", ak), irregular=0.9)),
            ("雲", body_cloud(a - 2.5, b - 2.5, 11, 4.4, rng("bc", ak))),
            ("震え", body_wave(a, b, 22, 0.03)),
            ("ガタガタ", body_jitter(a, b, 40, 0.03, rng("bj", ak))),
            ("角", rounded_rect(2 * a, 2 * b, 0)),
        ]
        for ja, S in shapes:
            i += 1
            it = add(cat, "fk_black_{:03d}".format(i), "ベタ_{}_{}".format(ja, aj))
            it.layers.append((S, BLACK))

    # 09 連結（すき間をあけて細い首でつなぐ）
    cat = "09_linked"
    i = 0
    from shapely.geometry import LineString

    def er(a_, b_, th):
        return a_ * b_ / math.hypot(b_ * math.cos(th), a_ * math.sin(th))

    link_specs = [
        ([(12, 18, None), (11, 16, 60)], "2連_右下へ"),
        ([(12, 18, None), (11, 16, 120)], "2連_左下へ"),
        ([(12, 18, None), (12, 18, 8)], "2連_横並び"),
        ([(12, 17, None), (11, 15, 60), (10, 14, 120)], "3連_ジグザグ"),
        ([(11, 16, None), (11, 16, 10), (11, 16, 10)], "3連_横並び"),
        ([(17, 11, None), (15, 10, 75)], "2連_横長_縦つなぎ"),
    ]
    for li, (cs, ja) in enumerate(link_specs):
        centers = []
        for k_, (a_, b_, d_) in enumerate(cs):
            if d_ is None:
                centers.append((0.0, 0.0))
                continue
            th = math.radians(d_)
            pa, pb, _ = cs[k_ - 1]
            dist = er(pa, pb, th) + er(a_, b_, th) + 3.5
            px_, py_ = centers[-1]
            centers.append((px_ + dist * math.cos(th), py_ + dist * math.sin(th)))
        for style in ["normal", "cloud"]:
            parts = []
            for (cx, cy), (a_, b_, _) in zip(centers, cs):
                if style == "normal":
                    parts.append(ellipse(a_, b_, cx, cy))
                else:
                    parts.append(affinity.translate(body_cloud(a_ - 2.4, b_ - 2.4, 10, 3.6, rng("lk", li, cx)), cx, cy))
            bridges = [LineString([p, q]).buffer(1.6) for p, q in zip(centers, centers[1:])]
            S = closing(unary_union(parts + bridges), 1.0)
            variants = [None, "LD"] if style == "normal" else [None]
            for tdk in variants:
                i += 1
                SS = tail(S, DIRS[tdk][0], L=10, bw=6, bend=0.35) if tdk else S
                add(cat, "fk_linked_{:03d}".format(i), "連結_{}_{}{}".format(
                    ja, "楕円" if style == "normal" else "雲", "_尻尾左下" if tdk else "")).white_lined(SS)

    # 10 恋愛・ふんわり
    cat = "10_love"
    i = 0
    for hk, (fat, h_, ja) in enumerate([(1.0, 40, "ハート"), (1.25, 36, "ぽってりハート"), (0.85, 44, "縦長ハート")]):
        for rot in [0, -12]:
            i += 1
            S = affinity.rotate(heart(h_, fat=fat), rot, origin=(0, 0))
            add(cat, "fk_love_{:03d}".format(i), "{}_{}".format(ja, "傾き" if rot else "まっすぐ")).white_lined(S)
    for ak in ["tate", "maru", "yoko"]:
        a, b, aj = ASPECT[ak]
        for dk in [None, "LD"]:
            i += 1
            S = body_scallop(a - 1.6, b - 1.6, 26 if ak != "maru" else 22, 2.0)
            if dk:
                S = tail(S, DIRS[dk][0], L=10, bw=6, bend=0.35)
            add(cat, "fk_love_{:03d}".format(i), "ふんわり_{}_{}".format(aj, "尻尾" + DIRS[dk][1] if dk else "尻尾なし")).white_lined(S)
        i += 1
        S = body_flower(a + 1.5, b + 1.5, 6 if ak == "maru" else 7, 0.16)
        add(cat, "fk_love_{:03d}".format(i), "花_{}".format(aj)).white_lined(S)
    # 小さなハートを散らした楕円
    from sozai import heart as _h
    for ak in ["tate", "yoko"]:
        a, b, aj = ASPECT[ak]
        S = body_ellipse(a, b)
        hs = []
        for ang, sz in [(-40, 7), (-62, 4.5), (205, 5.5)]:
            th = math.radians(ang)
            hs.append(_h(sz, a * 1.02 * math.cos(th), b * 1.02 * math.sin(th)))
        i += 1
        it = add(cat, "fk_love_{:03d}".format(i), "ハート添え楕円_{}".format(aj))
        it.white_lined(S)
        for hh in hs:
            it.layers += [(hh, WHITE), (outline_ring(hh, LW), BLACK)]

    # 11 二重線・テレパシー・回想
    cat = "11_double"
    i = 0
    for ak in ["tate", "maru", "yoko"]:
        a, b, aj = ASPECT[ak]
        for gap, ja in [(1.2, "二重線"), (2.4, "二重線_広")]:
            for dk in [None, "LD"]:
                i += 1
                S = body_ellipse(a, b)
                if dk:
                    S = tail(S, DIRS[dk][0], L=10, bw=6, bend=0.35)
                inner = S.buffer(-gap)
                it = add(cat, "fk_double_{:03d}".format(i), "{}_{}_{}".format(ja, aj, "尻尾" + DIRS[dk][1] if dk else "尻尾なし"))
                it.layers += [(S, WHITE), (outline_ring(S, LW), BLACK), (outline_ring(inner, LW * 0.7), BLACK)]
        i += 1
        S = body_ellipse(a, b)
        it = add(cat, "fk_double_{:03d}".format(i), "回想_点線内枠_{}".format(aj))
        it.layers += [(S, WHITE), (outline_ring(S, LW), BLACK), (dashed_outline(S.buffer(-1.6), LW * 0.7, LW * 0.7, 0.9), BLACK)]
        i += 1
        S = body_ellipse(a, b)
        it = add(cat, "fk_double_{:03d}".format(i), "ベタ縁_{}".format(aj))
        it.layers += [(S.buffer(1.6), BLACK), (S, WHITE)]

    # 12 心の声・モノローグ（線なしの白＋ぼかし代わりのギザ縁はなし→細線のみ）
    cat = "12_monologue"
    i = 0
    for ak in ["tate", "maru", "yoko"]:
        a, b, aj = ASPECT[ak]
        for lw, ja in [(LW * 0.5, "極細線"), (LW * 1.8, "太線")]:
            i += 1
            add(cat, "fk_mono_{:03d}".format(i), "モノローグ_楕円_{}_{}".format(ja, aj)).white_lined(body_ellipse(a, b), lw=lw)
        i += 1
        r = rng("mono", ak)
        add(cat, "fk_mono_{:03d}".format(i), "モノローグ_ゆがみ_{}".format(aj)).white_lined(body_wobble(a, b, r, amp=0.05), lw=LW * 0.6)
        i += 1
        S = body_ellipse(a, b)
        it = add(cat, "fk_mono_{:03d}".format(i), "モノローグ_切れ線_{}".format(aj))
        it.layers += [(S, WHITE), (dashed_outline(S, LW, 9, 2.2), BLACK)]
    for j, (w, h) in enumerate([(22, 46), (40, 20)]):
        i += 1
        S = rounded_rect(w, h, 0)
        it = add(cat, "fk_mono_{:03d}".format(i), "モノローグ_かぎ枠_{}".format("縦" if h > w else "横"))
        # 左上と右下だけのカギ括弧型
        from shapely.geometry import LineString
        k = 8
        c1 = LineString([(-w / 2, -h / 2 + k), (-w / 2, -h / 2), (-w / 2 + k, -h / 2)]).buffer(LW / 2, cap_style="flat", join_style="mitre")
        c2 = LineString([(w / 2, h / 2 - k), (w / 2, h / 2), (w / 2 - k, h / 2)]).buffer(LW / 2, cap_style="flat", join_style="mitre")
        it.layers += [(S, WHITE), (unary_union([c1, c2]), BLACK)]

    for it in ITEMS:
        it.path = it.save()
        n += 1
    return ITEMS


if __name__ == "__main__":
    items = build()
    print(len(items), "items")
    from collections import Counter
    print(Counter(it.cat for it in items))
