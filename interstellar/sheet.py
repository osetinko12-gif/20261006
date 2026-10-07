"""Render a numbered storyboard contact sheet (like the Odyssey one)."""
import importlib, sys
from PIL import Image, ImageDraw, ImageFont
from common import W, H
acts = sys.argv[1:] or ['act1']
FONT = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 22)
items = []
for a in acts:
    items += importlib.import_module(a).SCENES
cols = 5; tw, th = W * 2 // 2 * 2 // 2 * 1, H
tw, th = 384, 216
cap = 34
rows = (len(items) + cols - 1) // cols
sheet = Image.new('RGB', (cols * (tw + 12) + 12, rows * (th + cap + 12) + 12), (28, 28, 34))
dr = ImageDraw.Draw(sheet)
start = int(sys.argv[0] and 0)
num0 = {'act1': 1, 'act2': 10, 'act3': 20, 'act4': 28}
n = num0.get(acts[0], 1)
for k, (title, fn, ts) in enumerate(items):
    x = 12 + (k % cols) * (tw + 12); y = 12 + (k // cols) * (th + cap + 12)
    sheet.paste(fn(ts), (x, y))
    dr.text((x + 2, y + th + 6), f'{n + k:02d}  {title}', font=FONT, fill=(230, 230, 230))
out = f"out/sheet_{'_'.join(acts)}.png"
sheet.save(out); print(out, sheet.size)
