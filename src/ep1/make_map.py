# Natural Earth（パブリックドメイン）からヨーロッパ地図を投影・簡略化して map.json を作る
# 使い方: python3 make_map.py <natural-earth geojson のフォルダ>
import json, math, sys, os
from shapely.geometry import shape, box, mapping, Polygon
from shapely.ops import unary_union
D = sys.argv[1]
L0, P0 = math.radians(12), math.radians(52)
def proj(lon, lat):  # Lambert 正積方位図法
    l, p = math.radians(lon), math.radians(lat)
    k = math.sqrt(2 / (1 + math.sin(P0) * math.sin(p) + math.cos(P0) * math.cos(p) * math.cos(l - L0)))
    return k * math.cos(p) * math.sin(l - L0), -k * (math.cos(P0) * math.sin(p) - math.sin(P0) * math.cos(p) * math.cos(l - L0))
# 画面 1920x1080 に合わせる
corners = [proj(-13, 37), proj(45, 37), proj(-13, 70), proj(45, 70), proj(12, 31), proj(12, 71.5)]
xs, ys = [c[0] for c in corners], [c[1] for c in corners]
cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
S = min(1920 / (max(xs) - min(xs)), 1080 / (max(ys) - min(ys))) * 1.0
def P(lon, lat):
    x, y = proj(lon, lat); return (round(960 + (x - cx) * S, 1), round(540 + (y - cy) * S, 1))
def projgeom(g):
    if g.geom_type == 'Polygon':
        return [Polygon([P(*c[:2]) for c in g.exterior.coords], [[P(*c[:2]) for c in r.coords] for r in g.interiors]).buffer(0)]
    if hasattr(g, 'geoms'): return [q for p in g.geoms for q in projgeom(p)]
    return []
view = box(-400, -300, 2320, 1380)
def load(name, tol=1.2, drop_holes=False):
    fs = json.load(open(os.path.join(D, name + '.json')))['features']
    out = []
    clip = box(-75, 5, 120, 88)
    for f in fs:
        g = shape(f['geometry']).buffer(0).intersection(clip)
        if g.is_empty: continue
        for p in [q for g2 in projgeom(g) for q in getattr(g2.intersection(view).simplify(tol), 'geoms', [g2.intersection(view).simplify(tol)])]:
            if p.geom_type != 'Polygon' or p.area < 6: continue
            holes = [r for r in p.interiors if not drop_holes or Polygon(r).area > 4000 and Polygon(r).centroid.x > 450]
            out.append([[list(c) for c in p.exterior.coords]] + [[list(c) for c in r.coords] for r in holes])
    return out
land = load('ne_50m_land')
deep = load('ne_10m_bathymetry_K_200', 1.5, True)
ICE = [(-11, 54), (-10.5, 51.6), (-6, 51.3), (-4, 51.7), (-2, 52.4), (0.5, 52.9), (3, 53.4), (6, 53.6), (9, 53.3), (12, 52.6), (14.5, 52.4), (17, 52.3), (20, 52.7), (23, 53.1), (25.5, 53.8), (28, 54.7), (31, 55.6), (33.5, 57.2), (36, 59.2), (39, 61.2), (42, 63), (46, 64.6), (50, 66), (56, 68), (62, 70), (64, 77), (40, 80), (15, 79), (0, 73), (-8, 66), (-12, 60), (-13, 56.5)]
ALPS = [(5.8, 45.3), (7, 44.6), (8.5, 45.5), (10.5, 45.8), (12.5, 46.0), (14, 46.3), (15.6, 46.8), (14, 47.6), (12, 47.9), (10, 47.85), (8, 47.7), (6.5, 47.1), (6.0, 46.2)]
PYR = [(-1.5, 43.0), (0.5, 42.5), (2.3, 42.5), (2.0, 42.85), (0.5, 42.95), (-1.0, 43.15)]
sites = {k: P(*v) for k, v in {'lascaux': (1.17, 45.05), 'chauvet': (4.42, 44.39), 'altamira': (-4.12, 43.38),
        'refuge': (-1.5, 44.2), 'levant': (35.5, 32.5), 'anatolia': (30, 39.5), 'balkans': (23, 43.2), 'danube': (14, 48.2), 'france': (2.5, 46.3),
        'alps': (10, 46.6), 'britain': (-2, 53.5), 'doggerland': (3.5, 54.6), 'scand': (16, 63)}.items()}
json.dump({'land': land, 'deep': deep, 'ice': [P(*c) for c in ICE], 'alps': [P(*c) for c in ALPS], 'pyr': [P(*c) for c in PYR], 'sites': sites},
          open('map.json', 'w'), separators=(',', ':'))
print('land', len(land), 'deep', len(deep), os.path.getsize('map.json') // 1024, 'KB', sites)
