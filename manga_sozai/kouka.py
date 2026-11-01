"""効果線集ジェネレーター.

サイズ: 縦（150×220mm＝B5の基本枠）、横（150×100mm＝半ページ横長ゴマ）、正方（120×120mm）。
線はすべて入り抜きのある塗りパス。黒線版のほか、ベタの上に乗せる白線版も用意する。
"""
import math
import os
from collections import Counter

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from sozai import (BLACK, WHITE, Canvas, clip_rect, ellipse, heart, rng, sparkle, tapered, tapered_curve,
                   wedge_along)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "kouka")
SIZES = {"tate": (150, 220, "縦"), "yoko": (150, 100, "横"), "sq": (120, 120, "正方")}

ITEMS = []


class FX:
    def __init__(self, cat, name, ja, size):
        self.cat, self.name, self.ja = cat, name, ja
        self.w, self.h, self.sj = SIZES[size]
        self.layers = []

    def add(self, g, color=BLACK):
        self.layers.append((g, color))
        return self

    def save(self):
        cv = Canvas(self.w, self.h)
        box = clip_rect(self.w, self.h)
        for g, c in self.layers:
            if isinstance(g, str):  # 生のSVGパス（網点など数が多いもの）
                cv.raw('<path fill="{}" d="{}"/>'.format(c, g))
            else:
                cv.add(g.intersection(box), c)
        base = os.path.join(OUT, self.cat, self.name)
        cv.save(base)
        return base + ".svg"


def item(cat, prefix, ja, size):
    n = sum(1 for it in ITEMS if it.cat == cat) + 1
    it = FX(cat, "{}_{:03d}".format(prefix, n), ja + "_" + SIZES[size][2], size)
    ITEMS.append(it)
    return it


# ---------------------------------------------------------------- generators
def focus_lines(w, h, cx, cy, rx, ry, n, wmax, spread, r, bundles=True):
    """集中線. (cx,cy)中心、(rx,ry)の楕円の内側は空ける."""
    R = math.hypot(w, h)
    lines = []
    th = 0.0
    while len(lines) < n:
        # 束（数本ずつまとまる）で角度を進める
        k = r.randint(2, 6) if bundles else 1
        base = th
        for j in range(k):
            a = base + r.gauss(0, 0.004)
            end_m = 1 + spread * r.random() ** 1.6
            ex, ey = cx + rx * end_m * math.cos(a), cy + ry * end_m * math.sin(a)
            sx, sy = cx + R * math.cos(a), cy + R * math.sin(a)
            lines.append(tapered((sx, sy), (ex, ey), wmax * r.uniform(0.35, 1.0) * 2.2, 0.0, round_tip=False))
            base += 2 * math.pi / n * r.uniform(0.6, 1.0)
        th = base + 2 * math.pi / n * r.uniform(0.4, 2.2)
        if th > 2 * math.pi:
            break
    return unary_union(lines)


def speed_lines(w, h, ang_deg, n, wmax, r, gap_band=None, taper="both", length=(0.4, 1.0)):
    """流線. ang_deg の向きに平行な線. gap_band=(位置0..1, 幅0..1) で線を薄くする帯."""
    a = math.radians(ang_deg)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    D = math.hypot(w, h)
    cx, cy = w / 2, h / 2
    parts = []
    for i in range(n):
        off = (i / n - 0.5) * D + r.uniform(-0.5, 0.5) * D / n
        t_pos = i / n
        dens = 1.0
        if gap_band:
            c, bw = gap_band
            if abs(t_pos - c) < bw / 2:
                dens = 0.12
        if r.random() > dens:
            continue
        L = D * r.uniform(*length)
        s0 = r.uniform(-D / 2, D / 2 - L * 0.3)
        p0 = (cx + px * off + ux * s0, cy + py * off + uy * s0)
        p1 = (p0[0] + ux * L, p0[1] + uy * L)
        wi = wmax * r.uniform(0.25, 1.0)
        if taper == "both":
            parts.append(tapered_curve([p0, p1], wi, 0.45, 0.45))
        else:  # 片側（入りだけ太く）
            parts.append(tapered(p0, p1, wi, 0.0, round_tip=False))
    return unary_union(parts)


def uni_flash(cx, cy, R, n, Lmin, Lmax, wmax, r):
    """ウニフラッシュ: 円の外側へ放射する、両端の細い線."""
    parts = []
    for i in range(n):
        a = 2 * math.pi * i / n + r.gauss(0, 0.6 / n)
        r0 = R * r.uniform(0.98, 1.08)
        L = r.uniform(Lmin, Lmax) * (1 if r.random() > 0.15 else 1.4)
        p0 = (cx + r0 * math.cos(a), cy + r0 * math.sin(a))
        p1 = (cx + (r0 + L) * math.cos(a), cy + (r0 + L) * math.sin(a))
        parts.append(tapered_curve([p0, p1], wmax * r.uniform(0.4, 1.0), 0.15, 0.85))
    return unary_union(parts)


def beta_flash(cx, cy, R, n, Lmin, Lmax, r, base_w=None, ring=1.2):
    """ベタフラッシュ: 白い中心のまわりに黒いトゲが放射."""
    parts = [Point(cx, cy).buffer(R + ring, quad_segs=64).difference(Point(cx, cy).buffer(R, quad_segs=64))]
    for i in range(n):
        a = 2 * math.pi * i / n + r.gauss(0, 0.4 / n)
        L = r.uniform(Lmin, Lmax) * (1.5 if r.random() < 0.1 else 1.0)
        bw = (base_w or (2 * math.pi * R / n * 1.6)) * r.uniform(0.6, 1.3)
        p0 = (cx + R * math.cos(a), cy + R * math.sin(a))
        p1 = (cx + (R + L) * math.cos(a), cy + (R + L) * math.sin(a))
        parts.append(tapered(p0, p1, bw, 0.0, round_tip=False))
    return unary_union(parts).difference(Point(cx, cy).buffer(R, quad_segs=64))


def burst(cx, cy, R, k, depth, r, irregular=0.5):
    pts = []
    for i in range(2 * k):
        a = 2 * math.pi * (i + r.uniform(-0.3, 0.3) * irregular) / (2 * k)
        m = (1 + r.uniform(-irregular, irregular) * 0.5) if i % 2 == 0 else (1 - depth) * r.uniform(0.9, 1.1)
        pts.append((cx + R * m * math.cos(a), cy + R * m * math.sin(a)))
    return Polygon(pts).buffer(0)


def gloom_lines(w, h, n, wmax, r, top_frac=(0.35, 0.85)):
    """縦線（ガーン・どよーん）: 上から垂れ下がる線."""
    parts = []
    for i in range(n):
        x = (i + r.uniform(0.1, 0.9)) * w / n
        L = h * r.uniform(*top_frac)
        parts.append(tapered((x, -2), (x, L), wmax * r.uniform(0.5, 1.0), 0.0, round_tip=False))
    return unary_union(parts)


def rings(cx, cy, r0, step, count, lw, r, broken=True):
    parts = []
    for k in range(count):
        rad = r0 + step * k * (1 + 0.1 * k)
        circ = Point(cx, cy).buffer(rad, quad_segs=96).exterior
        if broken:
            L = circ.length
            s = r.uniform(0, L)
            segs = []
            pos = 0
            while pos < L:
                seg_len = r.uniform(0.15, 0.4) * L
                from shapely.ops import substring
                a0 = (s + pos) % L
                a1 = a0 + seg_len
                if a1 <= L:
                    segs.append(substring(circ, a0, a1))
                else:
                    segs.append(substring(circ, a0, L))
                pos += seg_len + r.uniform(0.03, 0.08) * L
            for sg in segs:
                if sg.length > 0.5:
                    parts.append(tapered_curve(list(sg.coords), lw * (1 - k / (count + 1) * 0.6), 0.2, 0.2))
        else:
            parts.append(Point(cx, cy).buffer(rad + lw / 2, quad_segs=96).difference(
                Point(cx, cy).buffer(rad - lw / 2, quad_segs=96)))
    return unary_union(parts)


def rain(w, h, n, ang, Lr, wmax, r):
    a = math.radians(ang)
    parts = []
    for i in range(n):
        x, y = r.uniform(-10, w + 10), r.uniform(-10, h + 10)
        L = r.uniform(*Lr)
        parts.append(tapered_curve([(x, y), (x + L * math.cos(a), y + L * math.sin(a))], wmax * r.uniform(0.5, 1), 0.3, 0.5))
    return unary_union(parts)


def sparkle_field(w, h, mind, rmin, rmax, r):
    parts = []
    for (x, y) in poisson(w, h, mind, r):
        u = r.random()
        rad = rmin + (rmax - rmin) * u ** 3
        if u < 0.35:
            parts.append(Point(x, y).buffer(rmin * 0.28, quad_segs=12))
        else:
            parts.append(sparkle(rad, x, y, thin=0.12, rot=(math.pi / 4 if r.random() < 0.2 else 0)))
    return unary_union(parts)


def hatch_block(w, h, ang, spacing, lw, r, layers=1):
    """斜線のカケアミ風かげ（全面）."""
    parts = []
    D = math.hypot(w, h)
    for li in range(layers):
        a = math.radians(ang + li * 50)
        ux, uy = math.cos(a), math.sin(a)
        px, py = -uy, ux
        k = int(D / spacing)
        for i in range(-k, k):
            off = i * spacing + r.uniform(-0.15, 0.15) * spacing
            # 短いストロークを並べる（手描きっぽく途切れる）
            s = -D
            while s < D:
                L = r.uniform(4, 12)
                p0 = (w / 2 + px * off + ux * s, h / 2 + py * off + uy * s)
                p1 = (p0[0] + ux * L, p0[1] + uy * L)
                if -5 < p0[0] < w + 5 and -5 < p0[1] < h + 5 or -5 < p1[0] < w + 5 and -5 < p1[1] < h + 5:
                    parts.append(tapered_curve([p0, p1], lw, 0.3, 0.3))
                s += L + r.uniform(0.3, 1.2)
    return unary_union(parts)


def kakeami(w, h, cell, spacing, lw, layers, r, base_ang=30):
    """カケアミ: 短い線の束（数本の平行線）を、向きを変えながらマス目状に重ねる."""
    parts = []
    for li in range(layers):
        off = cell * 0.5 * li
        rot = base_ang + li * 45
        nx, ny = int(w / cell) + 2, int(h / cell) + 2
        for i in range(-1, nx):
            for j in range(-1, ny):
                cx = i * cell + off + cell / 2 + r.uniform(-0.15, 0.15) * cell
                cy = j * cell + off + cell / 2 + r.uniform(-0.15, 0.15) * cell
                a = math.radians(rot + (90 if (i + j) % 2 else 0) + r.uniform(-8, 8))
                ux, uy = math.cos(a), math.sin(a)
                px, py = -uy, ux
                k = max(2, int(cell / spacing))
                for q in range(k):
                    o = (q - (k - 1) / 2) * spacing
                    L = cell * r.uniform(0.95, 1.25)
                    p0 = (cx + px * o - ux * L / 2, cy + py * o - uy * L / 2)
                    p1 = (cx + px * o + ux * L / 2, cy + py * o + uy * L / 2)
                    parts.append(tapered_curve([p0, p1], lw * r.uniform(0.8, 1.1), 0.3, 0.3))
    return unary_union(parts)


def poisson(w, h, mind, r, margin=4, k=30):
    """だいたい均一にばらまく点（簡易ポアソンディスク）."""
    pts = []
    cs = mind / math.sqrt(2)
    grid = {}
    tries = int(w * h / (mind * mind) * 6)
    for _ in range(tries):
        x, y = r.uniform(margin, w - margin), r.uniform(margin, h - margin)
        gx, gy = int(x / cs), int(y / cs)
        ok = True
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                p = grid.get((gx + dx, gy + dy))
                if p and math.hypot(p[0] - x, p[1] - y) < mind:
                    ok = False
        if ok:
            grid[(gx, gy)] = (x, y)
            pts.append((x, y))
    return pts


def dot_tone(w, h, frac, lpi=60, ang=45, r_jit=None):
    """網点トーン. frac(x,y) は 0..1 の濃度（面積率）. 円をSVGの弧で直接書く."""
    p = 25.4 / lpi
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    D = math.hypot(w, h)
    n = int(D / p) + 2
    out = []
    for i in range(-n, n):
        for j in range(-n, n):
            x = w / 2 + (i * ca - j * sa) * p
            y = h / 2 + (i * sa + j * ca) * p
            if x < -p or y < -p or x > w + p or y > h + p:
                continue
            f = frac(min(max(x, 0), w), min(max(y, 0), h))
            if f <= 0.004:
                continue
            r = p * math.sqrt(min(f, 0.78) / math.pi)
            out.append("M{:.3f} {:.3f}m-{r:.3f} 0a{r:.3f} {r:.3f} 0 1 0 {d:.3f} 0a{r:.3f} {r:.3f} 0 1 0 -{d:.3f} 0".format(
                x, y, r=r, d=2 * r))
    return "".join(out)


def sand_tone(w, h, density, rad, r, frac=None):
    """砂目トーン（ランダムな細かい点）."""
    out = []
    n = int(w * h * density)
    for _ in range(n):
        x, y = r.uniform(0, w), r.uniform(0, h)
        if frac and r.random() > frac(x, y):
            continue
        rr = rad * r.uniform(0.7, 1.2)
        out.append("M{:.2f} {:.2f}m-{r:.3f} 0a{r:.3f} {r:.3f} 0 1 0 {d:.3f} 0a{r:.3f} {r:.3f} 0 1 0 -{d:.3f} 0".format(
            x, y, r=rr, d=2 * rr))
    return "".join(out)


def swirl(w, h, arms, wmax, r, tight=2.2):
    """ぐるぐる背景（中心から渦を巻く線）."""
    cx, cy = w / 2, h / 2
    R = math.hypot(w, h) * 0.6
    parts = []
    for k in range(arms):
        a0 = 2 * math.pi * k / arms + r.uniform(-0.05, 0.05)
        pts = []
        for i in range(200):
            t = i / 199
            rad = 4 + R * t
            a = a0 + tight * math.log(1 + 6 * t)
            pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
        parts.append(tapered_curve(pts, wmax * r.uniform(0.6, 1.0), 0.6, 0.02))
    return unary_union(parts)


def sunburst(w, h, k, cx=None, cy=None, hole=0.0):
    """放射状の太い帯（サンバースト）."""
    cx = w / 2 if cx is None else cx
    cy = h / 2 if cy is None else cy
    R = math.hypot(w, h) * 1.2
    parts = []
    for i in range(k):
        a0 = 2 * math.pi * i / k
        a1 = a0 + math.pi / k
        parts.append(Polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                              (cx + R * math.cos(a1), cy + R * math.sin(a1))]))
    g = unary_union(parts)
    if hole:
        g = g.difference(Point(cx, cy).buffer(hole, quad_segs=48))
    return g


def scatter(w, h, mind, maker, r):
    return unary_union([maker(x, y, r) for (x, y) in poisson(w, h, mind, r, margin=-2)])


def lightning(p0, p1, w0, r, depth=0):
    """稲妻（枝分かれあり）."""
    segs = 9
    pts = [p0]
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    for i in range(1, segs):
        t = i / segs
        o = r.uniform(-1, 1) * L * 0.09
        pts.append((p0[0] + dx * t + nx * o, p0[1] + dy * t + ny * o))
    pts.append(p1)
    parts = [wedge_along(pts, w0, 0.0, 0.8)]
    if depth < 1:
        for j in (3, 6):
            if r.random() < 0.8:
                q = pts[j]
                ang = math.atan2(dy, dx) + r.choice([-1, 1]) * r.uniform(0.4, 0.8)
                q1 = (q[0] + L * 0.3 * math.cos(ang), q[1] + L * 0.3 * math.sin(ang))
                parts.append(lightning(q, q1, w0 * 0.5, r, depth + 1))
    return unary_union(parts)


def wavy_lines(w, h, n, amp, wl, lw, r, vertical=False):
    parts = []
    for i in range(n):
        o = (i + 0.5) * (w if vertical else h) / n + r.uniform(-0.2, 0.2) * (h / n)
        ph = r.uniform(0, 2 * math.pi)
        L = h if vertical else w
        s0 = r.uniform(-0.1, 0.3) * L
        s1 = s0 + r.uniform(0.5, 0.9) * L
        pts = []
        for k in range(160):
            s = s0 + (s1 - s0) * k / 159
            d = amp * math.sin(2 * math.pi * s / wl + ph)
            pts.append((o + d, s) if vertical else (s, o + d))
        parts.append(tapered_curve(pts, lw * r.uniform(0.7, 1.0), 0.3, 0.3))
    return unary_union(parts)


# ---------------------------------------------------------------- catalog
def build():
    # 01 集中線
    cat = "01_shuchu"
    specs = [  # (中心x比, 中心y比, 穴の大きさ, 本数, 太さ, ばらつき, 名前)
        (0.5, 0.5, 0.22, 260, 0.5, 0.5, "標準"),
        (0.5, 0.5, 0.15, 380, 0.4, 0.4, "高密度_穴小"),
        (0.5, 0.5, 0.32, 200, 0.6, 0.6, "穴大"),
        (0.5, 0.5, 0.22, 140, 0.9, 0.6, "まばら_太め"),
        (0.5, 0.38, 0.22, 260, 0.5, 0.5, "中心やや上"),
        (0.35, 0.45, 0.2, 260, 0.5, 0.5, "中心左寄り"),
        (0.65, 0.45, 0.2, 260, 0.5, 0.5, "中心右寄り"),
        (0.5, 0.5, 0.22, 300, 0.35, 1.2, "長短ばらばら"),
    ]
    for si, (fx, fy, hole, n, wm, sp, ja) in enumerate(specs):
        for sk in ["tate", "yoko", "sq"]:
            w, h, _ = SIZES[sk]
            r = rng("focus", si, sk)
            rr = hole * min(w, h)
            g = focus_lines(w, h, w * fx, h * fy, rr * (1.15 if sk == "yoko" else 1), rr * (1.15 if sk == "tate" else 1),
                            n, wm, sp, r)
            item(cat, "kk_shuchu", "集中線_" + ja, sk).add(g)
    # ベタ集中線（外周が黒に溶け込む）
    for sk in ["tate", "yoko", "sq"]:
        w, h, _ = SIZES[sk]
        r = rng("focusB", sk)
        rr = 0.22 * min(w, h)
        lines = focus_lines(w, h, w / 2, h / 2, rr, rr, 300, 0.55, 0.5, r)
        heavy = focus_lines(w, h, w / 2, h / 2, rr * 2.1, rr * 2.1 * (h / w if sk == "tate" else 1),
                            420, 2.6, 0.7, rng("focusB2", sk), bundles=False)
        item(cat, "kk_shuchu", "集中線_外周ベタ", sk).add(unary_union([lines, heavy]))
    # 白線版（ベタの上に重ねる用）
    for si in [0, 1, 3]:
        fx, fy, hole, n, wm, sp, ja = specs[si]
        for sk in ["tate", "sq"]:
            w, h, _ = SIZES[sk]
            r = rng("focusW", si, sk)
            rr = hole * min(w, h)
            g = focus_lines(w, h, w * fx, h * fy, rr, rr * (1.15 if sk == "tate" else 1), n, wm, sp, r)
            item(cat, "kk_shuchu", "集中線_白線_" + ja, sk).add(g, WHITE)

    # 02 流線
    cat = "02_ryusen"
    specs = [(0, 120, 0.5, None, "both", "横"), (90, 120, 0.5, None, "both", "縦"),
             (-30, 140, 0.5, None, "both", "斜め右上"), (30, 140, 0.5, None, "both", "斜め右下"),
             (0, 180, 0.35, None, "both", "横_高密度"), (0, 120, 0.6, (0.5, 0.35), "both", "横_中央抜き"),
             (0, 110, 0.6, None, "one", "横_片側入り"), (90, 110, 0.6, None, "one", "縦_落下")]
    for si, (ang, n, wm, band, tp, ja) in enumerate(specs):
        for sk in ["tate", "yoko"]:
            w, h, _ = SIZES[sk]
            r = rng("speed", si, sk)
            nn = int(n * (h if ang in (0,) else w) / 150) if ang in (0, 90) else n
            g = speed_lines(w, h, ang, max(60, nn), wm, r, gap_band=band, taper=tp)
            item(cat, "kk_ryusen", "流線_" + ja, sk).add(g)
    for si in [0, 1, 2]:
        ang, n, wm, band, tp, ja = specs[si]
        w, h, _ = SIZES["yoko"]
        r = rng("speedW", si)
        item(cat, "kk_ryusen", "流線_白線_" + ja, "yoko").add(speed_lines(w, h, ang, n, wm, r, taper=tp), WHITE)

    # 03 ウニフラッシュ
    cat = "03_uniflash"
    for si, (Rf, n, lo, hi, wm, ja) in enumerate([(0.22, 160, 0.10, 0.22, 0.45, "標準"), (0.16, 220, 0.12, 0.30, 0.4, "密_長め"),
                                                  (0.28, 120, 0.06, 0.14, 0.5, "大円_短め"), (0.2, 90, 0.10, 0.25, 0.8, "まばら_太め")]):
        for sk in ["tate", "sq", "yoko"]:
            w, h, _ = SIZES[sk]
            m = min(w, h)
            r = rng("uni", si, sk)
            item(cat, "kk_uni", "ウニフラ_" + ja, sk).add(uni_flash(w / 2, h / 2, Rf * m, n, lo * m, hi * m, wm, r))

    # 04 ベタフラッシュ
    cat = "04_betaflash"
    for si, (Rf, n, lo, hi, ja) in enumerate([(0.2, 70, 0.12, 0.3, "標準"), (0.15, 110, 0.15, 0.38, "細かく長い"),
                                              (0.26, 48, 0.08, 0.2, "太く短い")]):
        for sk in ["tate", "sq", "yoko"]:
            w, h, _ = SIZES[sk]
            m = min(w, h)
            r = rng("beta", si, sk)
            item(cat, "kk_beta", "ベタフラ_" + ja, sk).add(beta_flash(w / 2, h / 2, Rf * m, n, lo * m, hi * m, r))

    # 05 衝撃・爆発
    cat = "05_shogeki"
    for si, (k, dep, irr, ja) in enumerate([(14, 0.45, 0.5, "爆発"), (22, 0.3, 0.3, "衝撃"), (11, 0.5, 0.4, "大爆発")]):
        for sk in ["sq", "yoko"]:
            w, h, _ = SIZES[sk]
            m = min(w, h)
            r = rng("burst", si, sk)
            outer = burst(w / 2, h / 2, m * 0.46, k, dep, r, irr)
            inner = burst(w / 2, h / 2, m * 0.30, k, dep * 0.8, r, irr)
            item(cat, "kk_shogeki", ja + "_ベタ", sk).add(outer)
            item(cat, "kk_shogeki", ja + "_白抜き二重", sk).add(outer.difference(inner))
    # 06 縦線（ガーン・どよーん）
    cat = "06_tatesen"
    for si, (n, wm, fr, ja) in enumerate([(60, 0.9, (0.35, 0.8), "ガーン"), (110, 0.5, (0.25, 0.6), "どよーん_細"),
                                          (35, 1.4, (0.4, 0.95), "ずーん_太")]):
        for sk in ["tate", "yoko", "sq"]:
            w, h, _ = SIZES[sk]
            r = rng("gloom", si, sk)
            item(cat, "kk_tatesen", "縦線_" + ja, sk).add(gloom_lines(w, h, int(n * w / 150), wm, r, fr))

    # 07 波紋・衝撃波
    cat = "07_hamon"
    for si, (r0, st, cnt, lw, br, ja) in enumerate([(10, 9, 7, 1.0, True, "途切れ波紋"), (6, 6, 10, 0.6, True, "細かい波紋"),
                                                    (14, 12, 5, 1.6, False, "同心円")]):
        for sk in ["sq", "yoko"]:
            w, h, _ = SIZES[sk]
            r = rng("ring", si, sk)
            item(cat, "kk_hamon", ja, sk).add(rings(w / 2, h / 2, r0, st, cnt, lw, r, broken=br))

    # 08 雨・斜線
    cat = "08_ame"
    for si, (n, ang, Lr, wm, ja) in enumerate([(500, 100, (6, 16), 0.3, "小雨"), (900, 105, (10, 28), 0.4, "大雨"),
                                               (700, 70, (8, 20), 0.35, "横なぐり")]):
        for sk in ["tate", "yoko"]:
            w, h, _ = SIZES[sk]
            r = rng("rain", si, sk)
            item(cat, "kk_ame", "雨_" + ja, sk).add(rain(w, h, int(n * w * h / 33000), ang, Lr, wm, r))

    # 09 キラキラ背景
    cat = "09_kirakira"
    for si, (md, lo, hi, ja) in enumerate([(13, 1.2, 8, "標準"), (8, 0.9, 4.5, "細かい"), (24, 2, 15, "大きめ")]):
        for sk in ["tate", "yoko", "sq"]:
            w, h, _ = SIZES[sk]
            r = rng("spark", si, sk)
            g = sparkle_field(w, h, md, lo, hi, r)
            item(cat, "kk_kira", "キラキラ_" + ja, sk).add(g)
            if si == 0:
                item(cat, "kk_kira", "キラキラ_白_" + ja, sk).add(g, WHITE)

    # 10 カケアミ・斜線かげ（正方120mm、タイルとして並べて使える密度）
    cat = "10_kakeami"
    for si, (ang, sp, lw, ja) in enumerate([(45, 1.0, 0.18, "斜線_細"), (45, 1.8, 0.3, "斜線_粗め")]):
        r = rng("hatch", si)
        item(cat, "kk_kake", ja, "sq").add(hatch_block(120, 120, ang, sp, lw, r, 1))
    for si, (cell, sp, lw, layers, ja) in enumerate([(3.2, 0.55, 0.14, 1, "カケアミ_1重_淡"), (3.2, 0.55, 0.14, 2, "カケアミ_2重_中"),
                                                    (3.2, 0.55, 0.14, 3, "カケアミ_3重_濃"), (4.5, 0.8, 0.2, 2, "カケアミ_粗め")]):
        r = rng("kake", si)
        item(cat, "kk_kake", ja, "sq").add(kakeami(120, 120, cell, sp, lw, layers, r))

    # 01 追加: 中心がコマの外（斜めから迫る集中線）
    cat = "01_shuchu"
    for si, (fx, fy, ja) in enumerate([(-0.15, -0.1, "左上から"), (1.15, -0.1, "右上から"), (0.5, 1.2, "下から")]):
        for sk in ["tate", "yoko"]:
            w, h, _ = SIZES[sk]
            r = rng("focusEdge", si, sk)
            g = focus_lines(w, h, w * fx, h * fy, 0.35 * min(w, h), 0.35 * min(w, h), 300, 0.55, 0.9, r)
            item(cat, "kk_shuchu", "集中線_中心が外_" + ja, sk).add(g)

    # 11 ぐるぐる
    cat = "11_guruguru"
    for si, (arms, wm, tight, ja) in enumerate([(36, 1.0, 2.0, "標準"), (70, 0.6, 2.6, "細かい"), (18, 1.8, 1.6, "太い")]):
        for sk in ["tate", "sq"]:
            w, h, _ = SIZES[sk]
            item(cat, "kk_guru", "ぐるぐる_" + ja, sk).add(swirl(w, h, arms, wm, rng("swirl", si, sk), tight))

    # 12 サンバースト
    cat = "12_sunburst"
    for k, ja in [(16, "太帯16"), (28, "細帯28")]:
        for sk in ["tate", "yoko", "sq"]:
            w, h, _ = SIZES[sk]
            item(cat, "kk_sun", "放射帯_" + ja, sk).add(sunburst(w, h, k))
        w, h, _ = SIZES["sq"]
        item(cat, "kk_sun", "放射帯_{}_中心抜き".format(ja), "sq").add(sunburst(w, h, k, hole=22))
    w, h, _ = SIZES["yoko"]
    item(cat, "kk_sun", "放射帯_下から", "yoko").add(sunburst(w, h, 20, cy=h * 1.05))

    # 13 散らし背景（花・ハート・シャボン玉）
    cat = "13_chirashi"
    from manpu import flower as _flower
    from sozai import outline_ring as _ring

    def mk_flower(x, y, r):
        f = _flower(r.uniform(3, 7), r.choice([5, 5, 6]), x, y)
        c = Point(x, y).buffer(f.bounds[2] - x - (f.bounds[2] - f.bounds[0]) * 0.36)
        return unary_union([_ring(f, 0.35), _ring(c, 0.3)])

    def mk_heart(x, y, r):
        hh = heart(r.uniform(3, 8), x, y)
        return hh if r.random() < 0.35 else _ring(hh, 0.35)

    def mk_bubble(x, y, r):
        rad = r.uniform(1.5, 6)
        c = _ring(Point(x, y).buffer(rad, quad_segs=32), 0.3)
        shine = tapered_curve([(x + rad * 0.62 * math.cos(math.radians(d)), y + rad * 0.62 * math.sin(math.radians(d)))
                               for d in range(200, 255, 5)], rad * 0.14, 0.3, 0.3)
        return c.union(shine)

    for mk_, md, ja in [(mk_flower, 15, "花"), (mk_heart, 13, "ハート"), (mk_bubble, 12, "シャボン玉")]:
        for sk in ["tate", "yoko", "sq"]:
            w, h, _ = SIZES[sk]
            item(cat, "kk_chirashi", "散らし_" + ja, sk).add(scatter(w, h, md, mk_, rng("sc", ja, sk)))

    # 14 網点トーン（60線・45度）
    cat = "14_tone"
    for pct in [10, 20, 30, 40, 50]:
        item(cat, "kk_tone", "網点_{}％".format(pct), "sq").add(dot_tone(120, 120, lambda x, y, p=pct: p / 100))
    for sk, ja, fn in [("tate", "グラデ_上濃い", lambda x, y: 0.55 * (1 - y / 220) ** 1.2),
                       ("tate", "グラデ_下濃い", lambda x, y: 0.55 * (y / 220) ** 1.2),
                       ("yoko", "グラデ_左濃い", lambda x, y: 0.55 * (1 - x / 150) ** 1.2),
                       ("sq", "グラデ_円形", lambda x, y: 0.5 * min(1, math.hypot(x - 60, y - 60) / 70) ** 1.3)]:
        item(cat, "kk_tone", "網点" + ja, sk).add(dot_tone(SIZES[sk][0], SIZES[sk][1], fn))
    item(cat, "kk_tone", "砂目_淡", "sq").add(sand_tone(120, 120, 9, 0.075, rng("sand1")))
    item(cat, "kk_tone", "砂目_濃", "sq").add(sand_tone(120, 120, 20, 0.085, rng("sand2")))
    item(cat, "kk_tone", "砂目_グラデ", "tate").add(sand_tone(150, 220, 20, 0.085, rng("sand3"), frac=lambda x, y: (1 - y / 220) ** 1.5))

    # 15 稲妻
    cat = "15_inazuma"
    for si, ja in enumerate(["1本", "2本", "3本"]):
        for sk in ["tate", "yoko"]:
            w, h, _ = SIZES[sk]
            r = rng("bolt", si, sk)
            parts = []
            for k in range(si + 1):
                x0 = w * (0.2 + 0.6 * (k + 0.5) / (si + 1)) + r.uniform(-10, 10)
                parts.append(lightning((x0, -3), (x0 + r.uniform(-25, 25), h * r.uniform(0.75, 1.0)), 6.0 if si == 0 else 4.8, r))
            item(cat, "kk_inazuma", "稲妻_" + ja, sk).add(unary_union(parts))

    # 16 波線（ゆらゆら・寒気・恐怖）
    cat = "16_namisen"
    for si, (n, amp, wl, lw, vert, ja) in enumerate([(26, 1.4, 14, 0.5, False, "横ゆらゆら"), (40, 0.8, 8, 0.35, False, "横こまかい"),
                                                    (24, 1.6, 16, 0.55, True, "縦ゆらゆら_寒気")]):
        for sk in ["tate", "yoko"]:
            w, h, _ = SIZES[sk]
            nn = int(n * (w if vert else h) / 150)
            item(cat, "kk_nami", "波線_" + ja, sk).add(wavy_lines(w, h, max(10, nn), amp, wl, lw, rng("wave", si, sk), vert))

    for it in ITEMS:
        it.path = it.save()
    return ITEMS


if __name__ == "__main__":
    items = build()
    print(len(items), "items")
    print(Counter(it.cat for it in items))
