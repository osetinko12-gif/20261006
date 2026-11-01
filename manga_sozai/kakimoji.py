"""描き文字ジェネレーター（試作）.

フォント（SIL OFL）のグリフを輪郭として取り出し、1文字ずつ傾け・大きさ・位置をずらし、
輪郭をゆらがせて太らせることで手描き風にする. 縦書き.
「ー」「〜」「♡」「…」「っ」などは描き文字らしく別処理.
"""
import math
import os

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from shapely import affinity

from sozai import BLACK, WHITE, fit_canvas, heart, outline_ring, rng, tapered_curve

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = {
    "brush": ("PottaOne_400Regular.ttf", "筆"),
    "kurenaido": ("ZenKurenaido_400Regular.ttf", "細筆"),
    "maru": ("HachiMaruPop_400Regular.ttf", "丸文字"),
    "magic": ("YuseiMagic_400Regular.ttf", "マジック"),
    "reggae": ("ReggaeOne_400Regular.ttf", "極太"),
}
SMALL = set("っゃゅょぁぃぅぇぉッャュョァィゥェォ")


class FlatPen(BasePen):
    def __init__(self, glyphset, step=24):
        super().__init__(glyphset)
        self.rings, self.cur, self.step = [], [], step

    def _moveTo(self, p):
        self.cur = [p]

    def _lineTo(self, p):
        self.cur.append(p)

    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, self.step + 1):
            t = i / self.step
            mt = 1 - t
            self.cur.append((mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
                             mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]))

    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for i in range(1, self.step + 1):
            t = i / self.step
            mt = 1 - t
            self.cur.append((mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0],
                             mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]))

    def _closePath(self):
        if len(self.cur) > 2:
            self.rings.append(self.cur)
        self.cur = []

    _endPath = _closePath


_font_cache = {}


def glyph(fontkey, ch):
    """1文字の輪郭を shapely 図形で返す（1em = 1.0、中心が原点、y下向き）."""
    if fontkey not in _font_cache:
        f = TTFont(os.path.join(HERE, "fonts", FONTS[fontkey][0]))
        _font_cache[fontkey] = (f, f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm)
    f, gs, cmap, upm = _font_cache[fontkey]
    name = cmap.get(ord(ch))
    if name is None:
        return None
    pen = FlatPen(gs)
    gs[name].draw(pen)
    g = Polygon()
    for ring in pen.rings:
        p = Polygon(ring).buffer(0)
        g = g.symmetric_difference(p)
    g = affinity.scale(g, 1 / upm, -1 / upm, origin=(0, 0))
    adv = gs[name].width / upm
    return affinity.translate(g, -adv / 2, 0.88 - 0.5)  # だいたい em の中心へ


def wobble(g, amp, r, freq=2.2):
    """全体をなめらかにゆがませる（手のゆらぎ）."""
    ph = [r.uniform(0, 6.3) for _ in range(4)]

    def warp(x, y):
        return (x + amp * math.sin(freq * y * 6.28 + ph[0]) + amp * 0.5 * math.sin(freq * 2.3 * y * 6.28 + ph[1]),
                y + amp * math.sin(freq * x * 6.28 + ph[2]) + amp * 0.5 * math.sin(freq * 1.7 * x * 6.28 + ph[3]))

    def ring(coords):
        out = []
        cs = list(coords)
        for (x0, y0), (x1, y1) in zip(cs, cs[1:]):
            n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 0.02))
            for k in range(n):
                t = k / n
                out.append(warp(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
        return out

    polys = [g] if g.geom_type == "Polygon" else list(getattr(g, "geoms", []))
    res = []
    for p in polys:
        if p.geom_type != "Polygon" or p.is_empty:
            continue
        res.append(Polygon(ring(p.exterior.coords), [ring(h.coords) for h in p.interiors]).buffer(0))
    return unary_union(res)


def long_bar(L, r, wavy=False):
    """縦書きの「ー」「〜」を手で引いた線にする（長さLは em 単位）."""
    pts = []
    for i in range(60):
        t = i / 59
        x = (0.09 * math.sin(t * 6.28 * 1.5) if wavy else 0.03 * math.sin(t * 3.1))
        pts.append((x, -0.35 + L * t))
    return tapered_curve(pts, 0.16, 0.15, 0.55)


def dots(n=3):
    return unary_union([Point(0, -0.3 + i * 0.32).buffer(0.07, quad_segs=12) for i in range(n)])


def word(text, fontkey, size, seed, bold=0.0, wob=0.007, tilt=8, jitter=0.06, step=0.9):
    """縦書きの描き文字を1つ作る. size は1文字の大きさ(mm)."""
    r = rng("kaki", text, fontkey, seed)
    parts = []
    y = 0.0
    sway = r.uniform(-0.1, 0.1)
    for i, ch in enumerate(text):
        if ch in "ー―〜～":
            L = r.uniform(0.9, 1.6)
            g = long_bar(L, r, wavy=ch in "〜～")
            parts.append(affinity.translate(g, sway * i * 0.5, y + 0.35))
            y += L + 0.15
            continue
        if ch == "…":
            parts.append(affinity.translate(dots(), 0, y + 0.4))
            y += 1.0
            continue
        if ch in "♡♥":
            hs = r.uniform(0.6, 0.85)
            hh = heart(hs, 0, 0)
            hh = affinity.rotate(hh, r.uniform(-20, 20), origin=(0, 0))
            if ch == "♡":
                hh = hh.difference(hh.buffer(-0.075))
            parts.append(affinity.translate(hh, r.uniform(-0.1, 0.1), y + hs * 0.55))
            y += hs + 0.1
            continue
        g = glyph(fontkey, ch)
        if g is None or g.is_empty:
            y += 0.5
            continue
        sc = r.uniform(0.88, 1.12)
        dx = r.uniform(-jitter, jitter) + sway * i * 0.5
        if ch in SMALL:
            sc *= 0.62
            dx += 0.18
            g = affinity.translate(g, 0, -0.05)
        if ch in "!！?？":
            sc *= 1.05
        g = affinity.rotate(g, r.uniform(-tilt, tilt), origin=(0, 0))
        g = affinity.scale(g, sc, sc, origin=(0, 0))
        h = sc * (0.62 if ch in SMALL else 1.0)
        parts.append(affinity.translate(g, dx, y + h / 2))
        y += h * step
    G = unary_union(parts)
    G = wobble(G, wob, r)
    if bold:
        G = G.buffer(bold, quad_segs=6).buffer(-bold * 0.3, quad_segs=6)
    G = affinity.rotate(G, r.uniform(-6, 6), origin=(0, 0))
    return affinity.scale(G, size, size, origin=(0, 0))


def save(g, path, style="black", fringe=0.9):
    """style: black=黒文字 / white=白文字（黒フチ）/ black_w=黒文字＋白フチ."""
    layers = []
    if style == "black":
        layers = [(g, BLACK)]
    elif style == "white":
        layers = [(g.buffer(fringe * 0.55, quad_segs=6), BLACK), (g, WHITE)]
    elif style == "black_w":
        layers = [(g.buffer(fringe, quad_segs=6), WHITE), (g, BLACK)]
    cv = fit_canvas([l for l, _ in layers], margin=1.0)
    for l, c in layers:
        cv.add(l, c)
    cv.save(path)
    return path + ".svg"


if __name__ == "__main__":
    from sozai import contact_sheet
    out = os.path.join(HERE, "out", "kakimoji_test")
    words = ["あっ♡", "んぅ…", "はぁはぁ", "ぱんっ", "じゅぷっ", "びゅるっ", "らめぇ♡", "ビクビクッ", "とろぉ〜", "ぐちゅ", "きもちぃ♡", "どぷっ"]
    items = []
    for fk, bold in [("brush", 0.015), ("kurenaido", 0.03), ("reggae", 0.0)]:
        for k, w in enumerate(words):
            st = "white" if k in (2, 8) else "black"
            p = save(word(w, fk, 12, k, bold=bold), os.path.join(out, "{}_{:02d}".format(fk, k)), st)
            items.append((p, "{} {}".format(FONTS[fk][1], w)))
    contact_sheet(items, os.path.join(HERE, "out", "review", "kaki_test.png"), cols=12, cell=200,
                  font=os.path.join(HERE, "fonts", "NotoSansJP_700Bold.ttf"))
    print(len(items))
