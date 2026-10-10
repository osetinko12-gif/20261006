"""漫画素材シリーズ共通ライブラリ.

すべて mm 単位で形を作り、塗り（fill）だけのSVGパスとして書き出す。
線(stroke)は使わず「線の形をした塗り」にするので、どのソフトで開いても見た目が変わらない。
SVGを正本にして cairosvg で 600dpi の透過PNGを書き出す。
"""
import math
import os
import random

import cairosvg
from shapely.geometry import LineString, MultiPolygon, Point, Polygon
from shapely.ops import substring, unary_union
from shapely import affinity

DPI = 600
BLACK = "#000000"
WHITE = "#FFFFFF"


# ---------------------------------------------------------------- geometry
def ellipse(a, b, cx=0.0, cy=0.0, n=360):
    """横半径a・縦半径bの楕円."""
    return Polygon([(cx + a * math.cos(2 * math.pi * i / n), cy + b * math.sin(2 * math.pi * i / n))
                    for i in range(n)])


def radial(a, b, rfunc, n=720, cx=0.0, cy=0.0):
    """楕円を r(θ) 倍した形. rfunc(t) は 0..1 の位置 t を受けて倍率を返す."""
    pts = []
    for i in range(n):
        t = i / n
        th = 2 * math.pi * t
        r = rfunc(t)
        pts.append((cx + a * r * math.cos(th), cy + b * r * math.sin(th)))
    return Polygon(pts).buffer(0)


def rounded_rect(w, h, r, cx=0.0, cy=0.0):
    if r <= 0:
        return Polygon([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2),
                        (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)])
    inner = Polygon([(cx - w / 2 + r, cy - h / 2 + r), (cx + w / 2 - r, cy - h / 2 + r),
                     (cx + w / 2 - r, cy + h / 2 - r), (cx - w / 2 + r, cy + h / 2 - r)])
    return inner.buffer(r, quad_segs=24)


def bezier(p0, p1, p2, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        out.append((x, y))
    return out


def ray_hit(shape, ang, center=(0.0, 0.0)):
    """centerから角度angの方向に伸ばした線と外周の交点（いちばん遠いもの）."""
    cx, cy = center
    far = LineString([(cx, cy), (cx + 1000 * math.cos(ang), cy + 1000 * math.sin(ang))])
    hit = far.intersection(shape.exterior)
    pts = [hit] if hit.geom_type == "Point" else list(getattr(hit, "geoms", []))
    pts = [p for p in pts if p.geom_type == "Point"]
    if not pts:
        return (cx, cy)
    p = max(pts, key=lambda q: (q.x - cx) ** 2 + (q.y - cy) ** 2)
    return (p.x, p.y)


def closing(g, r):
    """凹んだ角だけを丸める（尻尾のつけ根をなめらかにする）."""
    return g.buffer(r, quad_segs=16).buffer(-r, quad_segs=16)


def tapered(p0, p1, w0, w1=0.0, round_tip=True):
    """p0で太さw0、p1で太さw1になる先細りの線（入り抜き）."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1e-9
    nx, ny = -dy / L, dx / L
    pts = [(p0[0] + nx * w0 / 2, p0[1] + ny * w0 / 2),
           (p1[0] + nx * w1 / 2, p1[1] + ny * w1 / 2),
           (p1[0] - nx * w1 / 2, p1[1] - ny * w1 / 2),
           (p0[0] - nx * w0 / 2, p0[1] - ny * w0 / 2)]
    g = Polygon(pts)
    if round_tip and w0 > 0:
        g = g.union(Point(p0).buffer(w0 / 2, quad_segs=8))
    return g


def stroke_line(coords, w, cap="round"):
    capn = {"round": "round", "flat": "flat", "square": "square"}[cap]
    return LineString(coords).buffer(w / 2, cap_style=capn, join_style="round", quad_segs=8)


def tapered_curve(coords, w_max, taper_in=0.35, taper_out=0.35, min_w=0.0):
    """折れ線に沿って両端が細くなる線（ペン入れ風）."""
    line = LineString(coords)
    L = line.length
    n = max(8, int(L / 0.25))
    left, right = [], []
    for i in range(n + 1):
        s = L * i / n
        t = i / n
        p = line.interpolate(s)
        q = line.interpolate(min(L, s + 0.05))
        r = line.interpolate(max(0, s - 0.05))
        dx, dy = q.x - r.x, q.y - r.y
        d = math.hypot(dx, dy) or 1e-9
        nx, ny = -dy / d, dx / d
        k = 1.0
        if taper_in > 0 and t < taper_in:
            k = min(k, t / taper_in)
        if taper_out > 0 and t > 1 - taper_out:
            k = min(k, (1 - t) / taper_out)
        w = max(min_w, w_max * math.sin(k * math.pi / 2))
        left.append((p.x + nx * w / 2, p.y + ny * w / 2))
        right.append((p.x - nx * w / 2, p.y - ny * w / 2))
    return Polygon(left + right[::-1]).buffer(0)


def outline_ring(shape, lw):
    """形の外周に沿った太さlwの線（塗りの帯）."""
    return shape.buffer(lw / 2, quad_segs=16, join_style="round").difference(
        shape.buffer(-lw / 2, quad_segs=16, join_style="round"))


def dashed_outline(shape, lw, dash, gap):
    """点線・破線の外周."""
    ring = LineString(shape.exterior.coords)
    L = ring.length
    period = dash + gap
    k = max(1, round(L / period))
    period = L / k
    d = period * dash / (dash + gap)
    parts = []
    for i in range(k):
        s0 = i * period
        seg = substring(ring, s0, s0 + d)
        if dash <= lw * 1.05:
            parts.append(ring.interpolate(s0 + d / 2).buffer(lw / 2, quad_segs=8))
        else:
            parts.append(seg.buffer(lw / 2, cap_style="round", quad_segs=8))
    return unary_union(parts)


def heart(size, cx=0.0, cy=0.0, n=400, fat=1.0):
    """ハート形（高さ≒size）."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((x * fat, y))
    g = Polygon(pts).buffer(0)
    minx, miny, maxx, maxy = g.bounds
    s = size / (maxy - miny)
    g = affinity.scale(g, s, s, origin=(0, 0))
    gx, gy = g.centroid.x, (g.bounds[1] + g.bounds[3]) / 2
    return affinity.translate(g, cx - gx, cy - gy)


def star(r_out, r_in, k, cx=0.0, cy=0.0, rot=-math.pi / 2):
    pts = []
    for i in range(2 * k):
        r = r_out if i % 2 == 0 else r_in
        a = rot + math.pi * i / k
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return Polygon(pts)


def sparkle(r, cx=0.0, cy=0.0, thin=0.18, rot=0.0):
    """四芒星キラキラ（辺が内側に反った形）."""
    pts = []
    n = 4
    for i in range(n):
        a0 = rot + 2 * math.pi * i / n - math.pi / 2
        a1 = a0 + 2 * math.pi / n
        tip0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
        tip1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
        mid = (a0 + a1) / 2
        ctrl = (cx + r * thin * math.cos(mid), cy + r * thin * math.sin(mid))
        pts += bezier(tip0, ctrl, tip1, 20)[:-1]
    return Polygon(pts).buffer(0)


def clip_rect(w, h):
    return Polygon([(0, 0), (w, 0), (w, h), (0, h)])


# ---------------------------------------------------------------- svg out
def _ring_d(coords):
    pts = list(coords)
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    s = "M{:.2f} {:.2f}".format(*pts[0])
    s += "".join("L{:.2f} {:.2f}".format(x, y) for x, y in pts[1:])
    return s + "Z"


def path_d(g):
    if g is None or g.is_empty:
        return ""
    polys = []
    if g.geom_type == "Polygon":
        polys = [g]
    elif g.geom_type in ("MultiPolygon", "GeometryCollection"):
        polys = [p for p in g.geoms if p.geom_type == "Polygon"]
        for p in g.geoms:
            if p.geom_type == "MultiPolygon":
                polys += list(p.geoms)
    out = []
    for p in polys:
        if p.is_empty or p.area < 1e-4:
            continue
        out.append(_ring_d(p.exterior.coords))
        for h in p.interiors:
            out.append(_ring_d(h.coords))
    return "".join(out)


class Canvas:
    """mm単位のSVGキャンバス. 描いた順に重なる."""

    def __init__(self, w, h, ox=0.0, oy=0.0):
        self.w, self.h = w, h
        self.ox, self.oy = ox, oy  # 原点のずれ（中心基準で作った形を置く用）
        self.layers = []

    def add(self, g, color=BLACK, opacity=None):
        if g is None or g.is_empty:
            return
        g = affinity.translate(g, self.ox, self.oy)
        d = path_d(g)
        if not d:
            return
        op = "" if opacity is None else ' fill-opacity="{}"'.format(opacity)
        self.layers.append('<path fill="{}" fill-rule="evenodd"{} d="{}"/>'.format(color, op, d))

    def raw(self, s):
        self.layers.append(s)

    def svg(self):
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<svg xmlns="http://www.w3.org/2000/svg" width="{w:.2f}mm" height="{h:.2f}mm" '
                'viewBox="0 0 {w:.2f} {h:.2f}">\n{body}\n</svg>\n').format(
            w=self.w, h=self.h, body="\n".join(self.layers))

    def save(self, base, png=True, dpi=DPI):
        os.makedirs(os.path.dirname(base), exist_ok=True)
        s = self.svg()
        with open(base + ".svg", "w", encoding="utf-8") as f:
            f.write(s)
        if png:
            cairosvg.svg2png(bytestring=s.encode("utf-8"), write_to=base + ".png", dpi=dpi)


def fit_canvas(geoms, margin=2.0):
    """形の外接矩形+余白でキャンバスを作る."""
    u = unary_union([g for g in geoms if g is not None and not g.is_empty])
    minx, miny, maxx, maxy = u.bounds
    w = maxx - minx + 2 * margin
    h = maxy - miny + 2 * margin
    return Canvas(w, h, ox=margin - minx, oy=margin - miny)


def rng(*key):
    return random.Random("|".join(str(k) for k in key))


def wedge_along(coords, w0, w1=0.0, power=1.0):
    """折れ線に沿って w0 から w1 へ細くなる帯（尻尾・稲妻用）."""
    line = LineString(coords)
    L = line.length
    n = max(12, int(L / 0.2))
    left, right = [], []
    for i in range(n + 1):
        s = L * i / n
        t = i / n
        p = line.interpolate(s)
        q = line.interpolate(min(L, s + 0.05))
        r = line.interpolate(max(0, s - 0.05))
        dx, dy = q.x - r.x, q.y - r.y
        d = math.hypot(dx, dy) or 1e-9
        nx, ny = -dy / d, dx / d
        w = w1 + (w0 - w1) * (1 - t) ** power
        left.append((p.x + nx * w / 2, p.y + ny * w / 2))
        right.append((p.x - nx * w / 2, p.y - ny * w / 2))
    return Polygon(left + right[::-1]).buffer(0)


# ---------------------------------------------------------------- preview
def contact_sheet(items, out, cols=6, cell=260, label=True, bg="checker", font=None):
    """items: [(svgパス, ラベル)] → 一覧画像（確認・サンプル用）."""
    import io
    from PIL import Image, ImageDraw, ImageFont
    rows = (len(items) + cols - 1) // cols
    lab_h = 26 if label else 0
    W, H = cols * cell, rows * (cell + lab_h)
    sheet = Image.new("RGB", (W, H), "white")
    if bg == "checker":
        d = ImageDraw.Draw(sheet)
        s = 12
        for y in range(0, H, s):
            for x in range(0, W, s):
                if (x // s + y // s) % 2:
                    d.rectangle([x, y, x + s - 1, y + s - 1], fill=(232, 232, 232))
    fnt = ImageFont.truetype(font, 15) if font else ImageFont.load_default()
    draw = ImageDraw.Draw(sheet)
    for i, (svg, lab) in enumerate(items):
        r, c = divmod(i, cols)
        x0, y0 = c * cell, r * (cell + lab_h)
        png = cairosvg.svg2png(url=svg, output_width=None, dpi=96)
        im = Image.open(io.BytesIO(png)).convert("RGBA")
        k = min((cell - 16) / im.width, (cell - 16) / im.height)
        im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
        sheet.paste(im, (x0 + (cell - im.width) // 2, y0 + (cell - im.height) // 2), im)
        if label:
            draw.text((x0 + 6, y0 + cell + 4), lab, fill=(60, 60, 60), font=fnt)
    sheet.save(out)
    return out
