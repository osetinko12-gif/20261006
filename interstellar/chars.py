"""Character sheet: full body (x2) + portrait for each cast member."""
from PIL import Image, ImageDraw, ImageFont
from common import *
FONT = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 20)
ROWS = [
    ('cooper', 'クーパー（農場）', '茶色のくせ毛を後ろへ・無精ひげ・茶色のジャケット＋青いシャツ・ジーンズ'),
    ('cooperS', 'クーパー（宇宙船）', '同じ髪とひげ・乗組員の制服'),
    ('brand', 'ブランド', 'こげ茶の髪を後ろで束ねる・乗組員の制服'),
    ('romilly', 'ロミリー', '黒人・短い黒髪・乗組員の制服'),
    ('romillyO', 'ロミリー（23年後）', '白髪まじり・白いひげ'),
    ('murph', 'マーフ（子ども）', '長いストレートの茶髪'),
    ('murphA', 'マーフ（大人）', '長い赤毛'),
    ('murphO', 'マーフ（老年）', '白髪'),
    ('prof', 'ブランド教授', '白髪・メガネ・ダークスーツ'),
    ('mann', 'マン博士', '短い茶髪・無精ひげ'),
    ('tom', 'トム（子ども）', '茶髪'), ('tomA', 'トム（大人）', 'こげ茶の髪とひげ'),
    ('donald', 'ドナルド（祖父）', '白髪・メガネ'),
]
cell_w, cell_h = 300, 200
cols = 3; rows = (len(ROWS) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cell_w, rows * cell_h), (34, 34, 40)); dr = ImageDraw.Draw(sheet)
for k, (who, name, note) in enumerate(ROWS):
    small = Image.new('RGB', (60, 40), (190, 196, 204)); d = ImageDraw.Draw(small)
    person(d, 16, 37, who, 1)
    p = Image.new('RGB', (34, 30), (150, 156, 166)); pd = ImageDraw.Draw(p); portrait(pd, 17, 30, who, 1)
    x, y = (k % cols) * cell_w, (k // cols) * cell_h
    sheet.paste(small.resize((180, 120), Image.NEAREST), (x + 10, y + 10))
    sheet.paste(p.resize((102, 90), Image.NEAREST), (x + 190, y + 40))
    dr.text((x + 10, y + 136), name, font=FONT, fill=(240, 240, 240))
    dr.text((x + 10, y + 162), note[:20], font=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 14), fill=(190, 190, 190))
    if len(note) > 20: dr.text((x + 10, y + 180), note[20:], font=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 14), fill=(190, 190, 190))
sheet.save('out/characters.png'); print(sheet.size)
