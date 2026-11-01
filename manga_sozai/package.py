"""3セットを生成→商品zip・表紙・サンプル画像・説明文までまとめて作る.

python3 package.py            # 全部
python3 package.py --no-build # 生成済みの out/ を使ってパッケージだけ
"""
import csv
import io
import math
import os
import shutil
import sys
import zipfile

import cairosvg
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
DIST = os.path.join(HERE, "dist")
IMG = os.path.join(HERE, "product_images")
FONT_BLACK = os.path.join(HERE, "fonts", "NotoSansJP_900Black.ttf")
FONT_BOLD = os.path.join(HERE, "fonts", "NotoSansJP_700Bold.ttf")
FONT_DELA = os.path.join(HERE, "fonts", "DelaGothicOne_400Regular.ttf")
YELLOW = (247, 201, 30)
INK = (20, 20, 22)

SETS = {
    "fukidashi": {
        "ja": "吹き出し集", "en": "SPEECH BUBBLE LIBRARY", "en_title": "Speech Bubbles", "unit": "種", "unit_en": "BUBBLES",
        "zip": "fukidashi_完成版.zip",
        "cats": {
            "01_normal": ("通常（楕円）", "Normal (oval)"), "02_box": ("ナレーション・角型", "Narration boxes"),
            "03_shout": ("叫び・トゲ", "Shout / spiky"), "04_thought": ("思考・雲", "Thought clouds"),
            "05_shaky": ("震え・波", "Shaky / wavy"), "06_electric": ("電話・機械", "Phone / machine"),
            "07_whisper": ("ささやき（点線・破線）", "Whisper (dotted)"), "08_black": ("ベタ（黒）", "Black fill"),
            "09_linked": ("連結（2連・3連）", "Linked"), "10_love": ("恋愛・ハート・ふんわり", "Love / soft"),
            "11_double": ("二重線・回想", "Double line / flashback"), "12_monologue": ("モノローグ", "Monologue"),
            "13_special": ("特殊・演出（ドロドロ・つらら・爆発二重など）", "Special"),
        },
        "size_note": "等倍で、縦長の楕円がおよそ 26×40mm（B5原稿に置いてちょうどよい大きさ）。線幅0.45mm。",
        "size_note_en": "At 100%, a tall oval is about 26x40 mm (fits a B5 manga page). Line width 0.45 mm.",
        "points": ["日本語の縦書きセリフが入る『縦長』を基本に、円・横長も収録",
                   "尻尾は左下・右下・左・右・下＋尻尾なし。左右反転すれば向きはさらに増やせます",
                   "白い塗り＋黒線なので、絵の上に置くだけで下が隠れます"],
    },
    "kouka": {
        "ja": "効果線集", "en": "MANGA EFFECT LINES", "en_title": "Effect Lines", "unit": "種", "unit_en": "EFFECTS",
        "zip": "kouka_完成版.zip",
        "cats": {
            "01_shuchu": ("集中線", "Focus lines"), "02_ryusen": ("流線（スピード線）", "Speed lines"),
            "03_uniflash": ("ウニフラッシュ", "Uni-flash"), "04_betaflash": ("ベタフラッシュ", "Beta-flash"),
            "05_shogeki": ("衝撃・爆発", "Impact / burst"), "06_tatesen": ("縦線（ガーン・どよーん）", "Gloom lines"),
            "07_hamon": ("波紋・同心円", "Ripples"), "08_ame": ("雨", "Rain"),
            "09_kirakira": ("キラキラ背景", "Sparkle backgrounds"), "10_kakeami": ("カケアミ・斜線", "Cross-hatching"),
            "11_guruguru": ("ぐるぐる（渦）", "Swirl"), "12_sunburst": ("放射帯（サンバースト）", "Sunburst"),
            "13_chirashi": ("散らし背景（花・ハート・シャボン玉）", "Scatter backgrounds"),
            "14_tone": ("網点・グラデ・砂目トーン", "Halftone screens"), "15_inazuma": ("稲妻", "Lightning"),
            "16_namisen": ("波線（ゆらゆら・寒気）", "Wavy lines"),
        },
        "parts": [("_1_線・フラッシュ", ["01_shuchu", "02_ryusen", "03_uniflash", "04_betaflash", "05_shogeki",
                                     "06_tatesen", "07_hamon", "08_ame", "10_kakeami"]),
                  ("_2_背景・トーン", ["09_kirakira", "11_guruguru", "12_sunburst", "13_chirashi", "14_tone",
                                    "15_inazuma", "16_namisen"])],
        "size_note": "縦150×220mm（B5の基本枠）／横150×100mm／正方120×120mm の3サイズ。コマに合わせて拡大・切り抜きして使えます。",
        "size_note_en": "Three canvas sizes: 150x220 mm (B5 inner frame), 150x100 mm, 120x120 mm.",
        "points": ["線は1本ずつ『入り抜き』のある手描き風の形",
                   "黒線版に加えて、ベタやトーンの上に乗せる『白線版』も収録",
                   "クリスタ以外（Procreate・ibisPaint・MediBangなど）で効果線を引く手間がなくなります"],
    },
    "manpu": {
        "ja": "漫符集", "en": "MANGA SYMBOLS", "en_title": "Manga Symbols", "unit": "種", "unit_en": "SYMBOLS",
        "zip": "manpu_完成版.zip",
        "cats": {
            "01_ase": ("汗・涙", "Sweat / tears"), "02_ikari": ("怒り", "Anger"),
            "03_odoroki": ("驚き・ショック・！？", "Surprise / shock"), "04_konran": ("混乱・眠り・ため息", "Dizzy / sleep / sigh"),
            "05_hirameki": ("ひらめき・音符", "Idea / music"), "06_kira": ("キラキラ・星・花", "Sparkles / stars / flowers"),
            "07_heart": ("ハート・照れ", "Hearts / blush"), "08_sonota": ("その他（天使の輪・湯気・雨雲など）", "Misc"),
        },
        "size_note": "等倍でおよそ10〜30mm。キャラの頭や顔のまわりにそのまま置けるサイズ。",
        "size_note_en": "About 10-30 mm at 100%, ready to place around a character's head.",
        "points": ["多くの記号を『線画（白抜き）』と『ベタ（黒塗り）』の2種類で収録",
                   "汗・怒りマーク・！？・ハート・Zzz・キラキラなど定番を網羅",
                   "白抜き版は絵の上に置いても下の線が透けません"],
    },
    "seijin": {
        "ja": "成人向けエフェクト集", "en": "ADULT MANGA EFFECTS", "en_title": "Adult Effects", "unit": "種", "unit_en": "EFFECTS",
        "zip": "seijin_完成版.zip",
        "cats": {
            "01_heart_fuki": ("ハート吹き出し", "Heart bubbles"), "02_heart_mark": ("ハート記号", "Heart marks"),
            "03_toiki": ("吐息・湯気", "Breath / steam"), "04_shizuku": ("汗・しずく・糸引き", "Sweat / drops"),
            "05_furue": ("震え・ビクビク", "Trembling marks"), "06_haikei": ("背景（ハート集中線など）", "Backgrounds"),
            "07_shusei": ("修正素材（黒棒・ハート隠し・光）", "Censor shapes"),
        },
        "size_note": "記号・吹き出しは等倍でおよそ10〜40mm。背景は 縦150×220mm／横150×100mm／正方120×120mm。",
        "size_note_en": "Symbols about 10-40 mm; backgrounds 150x220 / 150x100 / 120x120 mm.",
        "points": ["成人向け漫画の『演出』に使う効果素材（描写そのものは含みません）",
                   "ハート吹き出し・吐息・汗・しずく・震え線・ハート集中線をまとめて収録",
                   "修正用の黒棒・ハート隠し・光修正も同梱（修正の程度は販売先の規約・法令に合わせてご判断ください）"],
    },
}

APPS_TXT = """■ 対応ソフト
・PNG（透過・600dpi）… ほぼすべてのお絵かきソフトで使えます
  CLIP STUDIO PAINT／Photoshop／Procreate／Krita／MediBang Paint／ibisPaint／Canva／Affinity Photo／GIMP／Photopea など
・SVG（ベクター）… 拡大しても荒れません。形の変形・色の変更ができます（線は「塗りのパス」なので、どのソフトでも見た目が同じです）
  CLIP STUDIO PAINT（ファイル→読み込み）／Illustrator／Affinity Designer／Inkscape／Figma など
  ※PhotoshopでSVGを開くとラスタライズ（画像化）されるので、PhotoshopではPNGがおすすめです
"""

TERMS_TXT = """■ 利用規約
・商用・非商用どちらでも使えます（同人誌・商業誌・Web漫画・イラスト・動画・グッズなど）
・クレジット表記は不要です
・加工・改変OKです（色を変える、変形する、一部だけ使う など）
・素材そのものの再配布・再販売（素材集として配る、素材として売る、AI学習用データとして配布する など）は禁止です
"""


# ---------------------------------------------------------------- helpers
def font(path, size):
    return ImageFont.truetype(path, size)


def render_svg(path, width=None, height=None, dpi=None):
    kw = {}
    if width:
        kw["output_width"] = int(width)
    if height:
        kw["output_height"] = int(height)
    if dpi:
        kw["dpi"] = dpi
    png = cairosvg.svg2png(url=path, **kw)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def fit_render(path, box_w, box_h):
    im = render_svg(path, dpi=96)
    k = min(box_w / im.width, box_h / im.height)
    return render_svg(path, width=max(1, im.width * k))


def checker(w, h, s=14, c1=(255, 255, 255), c2=(232, 232, 232)):
    im = Image.new("RGB", (w, h), c1)
    d = ImageDraw.Draw(im)
    for y in range(0, h, s):
        for x in range(0, w, s):
            if (x // s + y // s) % 2:
                d.rectangle([x, y, x + s - 1, y + s - 1], fill=c2)
    return im


def text_center(draw, cx, y, s, fnt, fill, spacing=0):
    if spacing:
        widths = [draw.textlength(ch, font=fnt) for ch in s]
        total = sum(widths) + spacing * (len(s) - 1)
        x = cx - total / 2
        for ch, w in zip(s, widths):
            draw.text((x, y), ch, font=fnt, fill=fill)
            x += w + spacing
        return total
    w = draw.textlength(s, font=fnt)
    draw.text((cx - w / 2, y), s, font=fnt, fill=fill)
    return w


def watermark(im, text="SAMPLE"):
    W, H = im.size
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(FONT_BLACK, int(W * 0.06))
    step_y = int(H * 0.2)
    for row, y in enumerate(range(-H, 2 * H, step_y)):
        for x in range(-W, 2 * W, int(W * 0.42)):
            d.text((x + (row % 2) * W * 0.21, y), text, font=f, fill=(120, 120, 120, 60))
    layer = layer.rotate(28, resample=Image.BICUBIC, center=(W / 2, H / 2))
    out = im.convert("RGBA")
    out.alpha_composite(layer)
    return out.convert("RGB")


def to_la(src, dst):
    """RGBA → グレースケール＋透過（白黒素材なので見た目は同じでファイルが小さい）."""
    im = Image.open(src)
    im.convert("LA").save(dst, optimize=True)


# ---------------------------------------------------------------- build
def build_all():
    sys.path.insert(0, HERE)
    import fukidashi, kouka, manpu, seijin
    res = {}
    for key, mod in [("fukidashi", fukidashi), ("kouka", kouka), ("manpu", manpu), ("seijin", seijin)]:
        out_dir = os.path.join(OUT, key)
        if os.path.isdir(out_dir):
            shutil.rmtree(out_dir)
        items = mod.build()
        res[key] = [(it.cat, it.name, it.ja) for it in items]
        print(key, len(items))
    return res


def manifest_from_disk():
    sys.path.insert(0, HERE)
    import fukidashi, kouka, manpu
    # build() を走らせずに名前だけ欲しいので、各モジュールのカタログを保存しないで再構築する
    raise SystemExit("--no-build は manifest.csv が out/ にあるときだけ使えます")


def write_manifest(res):
    for key, rows in res.items():
        with open(os.path.join(OUT, key, "manifest.csv"), "w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(rows)


def read_manifest(key):
    with open(os.path.join(OUT, key, "manifest.csv"), encoding="utf-8") as f:
        return [tuple(r) for r in csv.reader(f)]


# ---------------------------------------------------------------- catalog / zip
def catalog_sheet(key, cat, rows, out_path, cols=6, cell=300):
    lab_h = 54
    n = len(rows)
    rws = (n + cols - 1) // cols
    head = 110
    W, H = cols * cell, head + rws * (cell + lab_h) + 20
    sheet = checker(W, H)
    d = ImageDraw.Draw(sheet)
    d.rectangle([0, 0, W, head], fill=INK)
    ja, en = SETS[key]["cats"][cat]
    d.text((30, 22), "{}  {}".format(SETS[key]["ja"], ja), font=font(FONT_BLACK, 44), fill=(255, 255, 255))
    d.text((W - 30 - d.textlength("{} files".format(n), font=font(FONT_BOLD, 28)), 40), "{} files".format(n),
           font=font(FONT_BOLD, 28), fill=YELLOW)
    f1 = font(FONT_BOLD, 19)
    f2 = font(FONT_BOLD, 15)
    for i, (c, name, label) in enumerate(rows):
        r, cc = divmod(i, cols)
        x0, y0 = cc * cell, head + r * (cell + lab_h)
        svg = os.path.join(OUT, key, c, name + ".svg")
        im = fit_render(svg, cell - 30, cell - 30)
        sheet.paste(im, (x0 + (cell - im.width) // 2, y0 + (cell - im.height) // 2 + 6), im)
        d.text((x0 + 10, y0 + cell + 2), name, font=f1, fill=(30, 30, 30))
        lab = label if d.textlength(label, font=f2) < cell - 14 else label[:18] + "…"
        d.text((x0 + 10, y0 + cell + 26), lab, font=f2, fill=(110, 110, 110))
    sheet.save(out_path, optimize=True)
    return sheet


def make_zip(key):
    S = SETS[key]
    rows = read_manifest(key)
    cats = list(S["cats"].keys())
    stage = os.path.join(DIST, "_stage_" + key)
    if os.path.isdir(stage):
        shutil.rmtree(stage)
    os.makedirs(stage)
    for c in cats:
        os.makedirs(os.path.join(stage, "PNG", c))
        os.makedirs(os.path.join(stage, "SVG", c))
    os.makedirs(os.path.join(stage, "一覧表"))
    for c, name, ja in rows:
        to_la(os.path.join(OUT, key, c, name + ".png"), os.path.join(stage, "PNG", c, name + ".png"))
        shutil.copy(os.path.join(OUT, key, c, name + ".svg"), os.path.join(stage, "SVG", c, name + ".svg"))
    for k, c in enumerate(cats):
        catalog_sheet(key, c, [r for r in rows if r[0] == c], os.path.join(stage, "一覧表", "{}.png".format(c)))

    total = len(rows)
    # README_フォルダ対応表
    lines = ["{}（全{}{}）フォルダ対応表".format(S["ja"], total, S["unit"]), "",
             "PNG/ … 透過PNG（600dpi）", "SVG/ … ベクター（拡大しても荒れない・編集できる）",
             "一覧表/ … どのファイルがどんな形かを一目で確認できる画像", "",
             "■ フォルダ一覧"]
    for c in cats:
        n = sum(1 for r in rows if r[0] == c)
        lines.append("  {:<14} {}（{}種）".format(c, S["cats"][c][0], n))
    if S.get("parts"):
        lines += ["", "■ ファイルサイズが大きいため、zipを{}つに分けています（どちらも同じ説明書つき）".format(len(S["parts"]))]
        for suffix, pcats in S["parts"]:
            lines.append("  {} … {}".format(S["zip"].replace(".zip", suffix + ".zip"), "・".join(S["cats"][c][0].split("（")[0] for c in pcats)))
    lines += ["", "■ ファイルの中身は『ファイル一覧.csv』（Excel・Numbers・Googleスプレッドシートで開けます）にも書いてあります。"]
    with open(os.path.join(stage, "README_フォルダ対応表.txt"), "w", encoding="utf-8-sig") as f:
        f.write("\n".join(lines) + "\n")
    with open(os.path.join(stage, "ファイル一覧.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["フォルダ", "分類", "ファイル名", "内容"])
        for c, name, ja in rows:
            w.writerow([c, S["cats"][c][0], name, ja])
    desc = ["{}　全{}{}　PNG＋SVG両対応".format(S["ja"], total, S["unit"]), "",
            "このたびはお買い上げありがとうございます。", "",
            "■ 内容", "・全{}{}／{}分類".format(total, S["unit"], len(cats)),
            "・PNG（透過・600dpi・アンチエイリアス済）とSVG（ベクター）の両方を同梱",
            "・" + S["size_note"], ""]
    desc += ["■ 特長"] + ["・" + p for p in S["points"]] + [""]
    desc += [APPS_TXT, "■ 使い方（CLIP STUDIO PAINTの例）",
             "・PNG：ファイル→読み込み→画像 で配置。拡大縮小・回転・左右反転して使えます",
             "・SVG：ファイル→読み込み からベクターとして読み込めます（バージョンにより手順が異なります）", "",
             "■ 使い方（Procreate／ibisPaintの例）",
             "・写真やファイルから『画像を挿入／読み込み』でPNGを配置してください", "", TERMS_TXT]
    with open(os.path.join(stage, "商品説明.txt"), "w", encoding="utf-8-sig") as f:
        f.write("\n".join(desc))

    parts = S.get("parts") or [("", cats)]
    for suffix, pcats in parts:
        zname = S["zip"].replace(".zip", suffix + ".zip")
        zpath = os.path.join(DIST, zname)
        if os.path.exists(zpath):
            os.remove(zpath)
        root = zname.replace(".zip", "")
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for dp, dn, fn in os.walk(stage):
                dn.sort()
                for f in sorted(fn):
                    full = os.path.join(dp, f)
                    rel = os.path.relpath(full, stage)
                    top = rel.split(os.sep)[0]
                    if top in ("PNG", "SVG") and rel.split(os.sep)[1] not in pcats:
                        continue
                    if top == "一覧表" and f[:-4] not in pcats:
                        continue
                    z.write(full, os.path.join(root, rel))
        print("zip", zpath, os.path.getsize(zpath) // 1024 // 1024, "MB")
    shutil.rmtree(stage)
    return total


# ---------------------------------------------------------------- product images
def pick(key, names):
    rows = {r[1]: r for r in read_manifest(key)}
    return [os.path.join(OUT, key, rows[n][0], n + ".svg") for n in names]


COVER_PICKS = {
    "fukidashi": ["fk_normal_002", "fk_shout_004", "fk_thought_002", "fk_love_001", "fk_elec_001", "fk_linked_001"],
    "kouka": ["kk_shuchu_025", "kk_beta_001", "kk_shuchu_010", "kk_shogeki_002", "kk_uni_011"],
    "manpu": ["mp_ase_002", "mp_ikari_002", "mp_odoroki_018", "mp_heart_002", "mp_kira_006", "mp_konran_006",
              "mp_hirameki_007", "mp_ase_008"],
    "seijin": ["sj_hfuki_007", "sj_hmark_002", "sj_toiki_003", "sj_hmark_017", "sj_shizuku_008", "sj_hfuki_016"],
}


def cover(key, total, lang="ja"):
    S = SETS[key]
    W = H = 1600
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    if lang == "ja":
        text_center(d, W / 2, 70, S["ja"], font(FONT_BLACK, 130), (255, 255, 255), spacing=14)
        text_center(d, W / 2, 245, S["en"], font(FONT_BOLD, 34), (210, 210, 210), spacing=10)
    else:
        text_center(d, W / 2, 80, S["en_title"].upper(), font(FONT_BLACK, 116), (255, 255, 255), spacing=8)
        text_center(d, W / 2, 245, "FOR MANGA & COMICS", font(FONT_BOLD, 34), (210, 210, 210), spacing=10)
    d.rectangle([W / 2 - 170, 310, W / 2 + 170, 316], fill=YELLOW)
    # 大きな数字
    num = str(total)
    fn = font(FONT_DELA, 400)
    nw = d.textlength(num, font=fn)
    unit = S["unit"] if lang == "ja" else S["unit_en"]
    fu = font(FONT_BLACK, 110 if lang == "ja" else 70)
    uw = d.textlength(unit, font=fu)
    x0 = W / 2 - (nw + 30 + uw) / 2
    d.text((x0, 330), num, font=fn, fill=YELLOW)
    d.text((x0 + nw + 30, 330 + (470 if lang == "ja" else 500) - (110 if lang == "ja" else 70) - 40), unit, font=fu, fill=YELLOW)
    # 素材の並び
    picks = pick(key, COVER_PICKS[key])
    n = len(picks)
    band_y, band_h = 900, 440
    if key == "kouka":
        # 効果線は白いパネルに入れて見せる
        pw = (W - 120 - 30 * (n - 1)) / n
        for i, p in enumerate(picks):
            x = 60 + i * (pw + 30)
            panel = Image.new("RGBA", (int(pw), band_h), (255, 255, 255, 255))
            art = render_svg(p, width=pw * 1.12)
            art = art.crop((int((art.width - pw) / 2), int((art.height - band_h) / 2),
                            int((art.width - pw) / 2) + int(pw), int((art.height - band_h) / 2) + band_h))
            panel.alpha_composite(art)
            im.paste(panel.convert("RGB"), (int(x), band_y))
            d.rectangle([x, band_y, x + pw - 1, band_y + band_h - 1], outline=(255, 255, 255), width=4)
    else:
        cell = (W - 120) / n
        for i, p in enumerate(picks):
            art = fit_render(p, cell - 24, band_h - 40)
            if key in ("manpu", "seijin"):
                # 黒地で見えるよう白いフチをつける
                bg = Image.new("RGBA", (art.width + 24, art.height + 24), (0, 0, 0, 0))
                a = art.split()[3].point(lambda v: 255 if v > 10 else 0)
                from PIL import ImageFilter
                a = a.filter(ImageFilter.MaxFilter(9))
                halo = Image.new("RGBA", art.size, (255, 255, 255, 255))
                halo.putalpha(a)
                bg.alpha_composite(halo.resize(art.size), (12, 12))
                bg.alpha_composite(art, (12, 12))
                art = bg
            x = 60 + i * cell + (cell - art.width) / 2
            y = band_y + (band_h - art.height) / 2
            im.paste(art, (int(x), int(y)), art)
    # 下の黄色い帯
    d.rectangle([0, H - 180, W, H], fill=YELLOW)
    ncat = len(S["cats"])
    if lang == "ja":
        tag = "全{}分類　｜　PNG＋SVG両対応　｜　クリスタ対応".format(ncat)
    else:
        tag = "{} CATEGORIES  |  PNG + SVG  |  600 DPI".format(ncat)
    text_center(d, W / 2, H - 132, tag, font(FONT_BLACK, 56 if lang == "ja" else 54), INK)
    os.makedirs(IMG, exist_ok=True)
    out = os.path.join(IMG, "{}_cover{}.png".format(key, "" if lang == "ja" else "_EN"))
    im.save(out, optimize=True)
    return out


SAMPLE_COLORS = [(228, 72, 72), (64, 120, 210), (130, 90, 190), (40, 160, 120)]


def sample_sheet(key, title, names, out_name, color, cols=4, cell=None, crop_panels=False):
    W = 1600
    head = 150
    rows_n = (len(names) + cols - 1) // cols
    cell = cell or (W - 80) // cols
    H = head + rows_n * cell + 60
    im = checker(W, H, s=20)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, head], fill=color)
    d.text((50, 30), title, font=font(FONT_BLACK, 64), fill=(255, 255, 255))
    d.text((W - 50 - d.textlength(SETS[key]["ja"], font=font(FONT_BOLD, 36)), 52), SETS[key]["ja"],
           font=font(FONT_BOLD, 36), fill=(255, 255, 255))
    for i, p in enumerate(pick(key, names)):
        r, c = divmod(i, cols)
        x0, y0 = 40 + c * cell, head + 30 + r * cell
        if crop_panels:
            art = fit_render(p, cell - 30, cell - 30)
            panel = Image.new("RGBA", art.size, (255, 255, 255, 255))
            panel.alpha_composite(art)
            px_, py_ = x0 + (cell - art.width) // 2, y0 + (cell - art.height) // 2
            im.paste(panel.convert("RGB"), (px_, py_))
            d.rectangle([px_, py_, px_ + art.width - 1, py_ + art.height - 1], outline=INK, width=3)
        else:
            art = fit_render(p, cell - 40, cell - 40)
            im.paste(art, (x0 + (cell - art.width) // 2, y0 + (cell - art.height) // 2), art)
    im = watermark(im)
    out = os.path.join(IMG, out_name)
    im.save(out, optimize=True)
    return out


def overview(key, total):
    """全分類を1枚に（各分類から2つずつ）."""
    rows = read_manifest(key)
    cats = list(SETS[key]["cats"].keys())
    W = 1600
    cols = 4 if len(cats) != 10 else 5
    per = 2
    cellw = (W - 60) // cols
    cellh = 300
    head = 150
    rws = (len(cats) + cols - 1) // cols
    H = head + rws * (cellh + 70) + 40
    im = checker(W, H, s=20)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, head], fill=INK)
    d.text((50, 30), "全{}分類・{}種".format(len(cats), total), font=font(FONT_BLACK, 64), fill=YELLOW)
    d.text((W - 50 - d.textlength(SETS[key]["ja"], font=font(FONT_BOLD, 36)), 52), SETS[key]["ja"],
           font=font(FONT_BOLD, 36), fill=(255, 255, 255))
    for k, c in enumerate(cats):
        r, cc = divmod(k, cols)
        x0, y0 = 30 + cc * cellw, head + 20 + r * (cellh + 70)
        crs = [rr for rr in rows if rr[0] == c]
        sel = [crs[0], crs[len(crs) // 2]] if len(crs) > 1 else crs
        sub = (cellw - 20) // per
        for j, (cat_, name, _) in enumerate(sel):
            p = os.path.join(OUT, key, cat_, name + ".svg")
            if key == "kouka":
                art = fit_render(p, sub - 16, cellh - 20)
                panel = Image.new("RGBA", art.size, (255, 255, 255, 255))
                panel.alpha_composite(art)
                px_, py_ = x0 + 10 + j * sub + (sub - art.width) // 2, y0 + (cellh - art.height) // 2
                im.paste(panel.convert("RGB"), (px_, py_))
                d.rectangle([px_, py_, px_ + art.width - 1, py_ + art.height - 1], outline=INK, width=2)
            else:
                art = fit_render(p, sub - 20, cellh - 30)
                im.paste(art, (x0 + 10 + j * sub + (sub - art.width) // 2, y0 + (cellh - art.height) // 2), art)
        text_center(d, x0 + cellw / 2, y0 + cellh + 6, SETS[key]["cats"][c][0].split("（")[0], font(FONT_BOLD, 30), INK)
    im = watermark(im)
    out = os.path.join(IMG, "{}_sample_1_overview.png".format(key))
    im.save(out, optimize=True)
    return out


SAMPLES = {
    "fukidashi": [
        ("叫び・思考・震え", ["fk_shout_001", "fk_shout_011", "fk_shout_019", "fk_shout_005",
                          "fk_thought_002", "fk_thought_014", "fk_thought_026", "fk_thought_039",
                          "fk_shaky_002", "fk_shaky_012", "fk_shaky_006", "fk_shaky_022"]),
        ("ベタ・連結・恋愛・ささやき", ["fk_black_002", "fk_black_004", "fk_black_005", "fk_black_010",
                                "fk_linked_001", "fk_linked_010", "fk_love_001", "fk_love_008",
                                "fk_whisper_004", "fk_whisper_013", "fk_double_002", "fk_elec_002"]),
        ("特殊・演出（新規追加）", ["fk_special_001", "fk_special_002", "fk_special_003", "fk_special_007",
                              "fk_special_010", "fk_special_012", "fk_special_014", "fk_special_016",
                              "fk_special_017", "fk_special_018", "fk_special_024", "fk_special_027"]),
    ],
    "kouka": [
        ("集中線・ベタ集中線", ["kk_shuchu_001", "kk_shuchu_005", "kk_shuchu_010", "kk_shuchu_025",
                           "kk_shuchu_013", "kk_shuchu_016", "kk_shuchu_019", "kk_shuchu_022"]),
        ("フラッシュ・流線・縦線", ["kk_uni_001", "kk_beta_002", "kk_shogeki_004", "kk_ryusen_001",
                              "kk_ryusen_011", "kk_tatesen_001", "kk_hamon_001", "kk_kake_005"]),
        ("背景・トーン（新規追加）", ["kk_guru_001", "kk_sun_001", "kk_chirashi_001", "kk_chirashi_004", "kk_tone_003",
                                "kk_tone_006", "kk_inazuma_003", "kk_nami_001"]),
    ],
    "manpu": [
        ("汗・怒り・驚き", ["mp_ase_001", "mp_ase_002", "mp_ase_008", "mp_ase_013", "mp_ase_021",
                        "mp_ikari_001", "mp_ikari_002", "mp_ikari_010", "mp_ikari_013", "mp_ikari_015",
                        "mp_odoroki_001", "mp_odoroki_004", "mp_odoroki_018", "mp_odoroki_019", "mp_odoroki_022"]),
        ("キラキラ・ハート・ねむり", ["mp_kira_002", "mp_kira_005", "mp_kira_010", "mp_kira_015", "mp_kira_018",
                                "mp_heart_002", "mp_heart_005", "mp_heart_008", "mp_heart_011", "mp_heart_013",
                                "mp_konran_001", "mp_konran_003", "mp_konran_006", "mp_hirameki_001", "mp_hirameki_007"]),
        ("その他（新規追加）", ["mp_sonota_001", "mp_sonota_003", "mp_sonota_006", "mp_sonota_007", "mp_sonota_010",
                          "mp_sonota_012", "mp_sonota_013", "mp_sonota_018", "mp_sonota_020", "mp_sonota_021",
                          "mp_sonota_023", "mp_sonota_026", "mp_sonota_027", "mp_sonota_028", "mp_sonota_029"]),
    ],
    "seijin": [
        ("ハート吹き出し・ハート記号", ["sj_hfuki_001", "sj_hfuki_003", "sj_hfuki_007", "sj_hfuki_009", "sj_hfuki_012",
                                 "sj_hfuki_015", "sj_hfuki_017", "sj_hfuki_019", "sj_hmark_007", "sj_hmark_011",
                                 "sj_hmark_015", "sj_hmark_017", "sj_hmark_019", "sj_hmark_021", "sj_hmark_023"]),
        ("吐息・しずく・震え・修正", ["sj_toiki_001", "sj_toiki_003", "sj_toiki_006", "sj_toiki_011", "sj_shizuku_002",
                                "sj_shizuku_007", "sj_shizuku_010", "sj_shizuku_014", "sj_shizuku_018", "sj_shizuku_021",
                                "sj_furue_003", "sj_furue_008", "sj_shusei_001", "sj_shusei_009", "sj_shusei_012"]),
        ("背景", ["sj_haikei_001", "sj_haikei_005", "sj_haikei_007", "sj_haikei_008", "sj_haikei_011", "sj_haikei_014"]),
    ],
}


def usage_page():
    """3セットを組み合わせた使用例ページ（コマ枠＋効果線＋吹き出し＋漫符）."""
    dpi = 150
    mm = dpi / 25.4
    W, H = int(182 * mm), int(257 * mm)
    page = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    d = ImageDraw.Draw(page)
    m = 16 * mm
    g = 2.5 * mm
    lw = int(0.7 * mm)
    x0, y0, x1, y1 = m, m, W - m, H - m
    mid = y0 + (y1 - y0) * 0.36
    mid2 = y0 + (y1 - y0) * 0.66
    xm = x0 + (x1 - x0) * 0.55
    panels = [(x0, y0, x1, mid), (x0, mid + g, xm, mid2), (xm + g, mid + g, x1, mid2), (x0, mid2 + g, x1, y1)]

    import json
    with open(os.path.join(OUT, "fukidashi", "anchors.json"), encoding="utf-8") as f:
        anchors = json.load(f)

    def put(svg_key, name, box, scale=1.0, at=None, flip=False):
        """素材を置く. 吹き出しは『本体の中心』が at に来るように置き、その座標を返す."""
        p = pick(svg_key, [name])[0]
        art = render_svg(p, dpi=dpi * scale)
        if flip:
            art = art.transpose(Image.FLIP_LEFT_RIGHT)
        bx0, by0, bx1, by1 = [int(v) for v in box]
        cx, cy = ((bx0 + bx1) / 2, (by0 + by1) / 2) if at is None else at
        k = dpi * scale / 25.4
        if name in anchors:
            ax, ay = anchors[name][0] * k, anchors[name][1] * k
            if flip:
                ax = art.width - ax
        else:
            ax, ay = art.width / 2, art.height / 2
        layer = Image.new("RGBA", page.size, (0, 0, 0, 0))
        layer.alpha_composite(art, (int(round(cx - ax)), int(round(cy - ay))))
        mask = Image.new("L", page.size, 0)
        ImageDraw.Draw(mask).rectangle([bx0, by0, bx1, by1], fill=255)
        layer.putalpha(Image.composite(layer.split()[3], Image.new("L", page.size, 0), mask))
        page.alpha_composite(layer)
        return cx, cy

    def vtext(center, s, size):
        """縦書き. 1文字ずつマスの中心に置く. !? !! は横に並べて1マス（縦中横）."""
        cx, cy = center
        f = font(FONT_BOLD, int(size))
        toks = []
        i = 0
        while i < len(s):
            if s[i] in "!?！？" and i + 1 < len(s) and s[i + 1] in "!?！？":
                toks.append(s[i:i + 2])
                i += 2
            else:
                toks.append(s[i])
                i += 1
        step = size * 1.08
        y = cy - step * len(toks) / 2 + step / 2
        for t in toks:
            if t in "ー…―〜":
                im_ = Image.new("RGBA", (int(size * 2), int(size * 2)), (0, 0, 0, 0))
                ImageDraw.Draw(im_).text((size, size), t, font=f, fill=(0, 0, 0), anchor="mm")
                im_ = im_.rotate(-90)
                page.alpha_composite(im_, (int(cx - size), int(y - size)))
            elif t in "っゃゅょぁぃぅぇぉッャュョァィゥェォ":
                d.text((cx + size * 0.12, y - size * 0.1), t, font=f, fill=(0, 0, 0), anchor="mm")
            elif t in "、。":
                d.text((cx + size * 0.3, y - size * 0.3), t, font=f, fill=(0, 0, 0), anchor="mm")
            elif len(t) == 2:
                f2 = font(FONT_BOLD, int(size * 0.8))
                d.text((cx, y), t, font=f2, fill=(0, 0, 0), anchor="mm")
            else:
                d.text((cx, y), t, font=f, fill=(0, 0, 0), anchor="mm")
            y += step

    def rel(p, fx, fy):
        return (p[0] + (p[2] - p[0]) * fx, p[1] + (p[3] - p[1]) * fy)

    p1, p2, p3, p4 = panels
    put("kouka", "kk_shuchu_013", p1, scale=1.0)
    vtext(put("fukidashi", "fk_shout_001", p1, at=rel(p1, 0.5, 0.5), scale=1.15), "なんだと!?", 6.6 * mm)
    put("kouka", "kk_ryusen_001", p2, scale=1.0)
    vtext(put("fukidashi", "fk_normal_003", p2, at=rel(p2, 0.36, 0.42)), "待って", 5 * mm)
    put("manpu", "mp_ase_007", p2, at=rel(p2, 0.78, 0.3), scale=1.1)
    put("kouka", "kk_kira_001", p3, scale=1.0)
    vtext(put("fukidashi", "fk_love_008", p3, at=rel(p3, 0.5, 0.45), scale=0.95), "好き…", 5 * mm)
    put("manpu", "mp_heart_007", p3, at=rel(p3, 0.82, 0.2))
    put("kouka", "kk_tatesen_007", p4, at=((p4[0] + p4[2]) / 2, p4[1] + 70 * mm), scale=1.0)
    vtext(put("fukidashi", "fk_thought_002", p4, at=rel(p4, 0.72, 0.42)), "どうしよう", 4.6 * mm)
    vtext(put("fukidashi", "fk_shaky_006", p4, at=rel(p4, 0.28, 0.5), scale=0.9), "うそ…", 4.6 * mm)
    put("manpu", "mp_odoroki_019", p4, at=rel(p4, 0.5, 0.25), scale=1.3)
    for (a, b, c, e) in panels:
        d.rectangle([a, b, c, e], outline=(0, 0, 0), width=lw)
    # 外側の白い帯にラベル
    canvas = Image.new("RGB", (W + 2 * int(10 * mm), H + int(26 * mm)), (240, 240, 240))
    canvas.paste(page.convert("RGB"), (int(10 * mm), int(20 * mm)))
    dd = ImageDraw.Draw(canvas)
    dd.text((int(10 * mm), int(5 * mm)), "使用例：吹き出し集＋効果線集＋漫符集", font=font(FONT_BLACK, int(7 * mm)), fill=INK)
    out = os.path.join(IMG, "set_usage_example.png")
    canvas.save(out, optimize=True)
    return out


def bundle_cover(totals):
    W = H = 1600
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    text_center(d, W / 2, 80, "漫画素材セット", font(FONT_BLACK, 130), (255, 255, 255), spacing=12)
    text_center(d, W / 2, 255, "MANGA ASSET BUNDLE", font(FONT_BOLD, 34), (210, 210, 210), spacing=10)
    d.rectangle([W / 2 - 170, 320, W / 2 + 170, 326], fill=YELLOW)
    s = totals["fukidashi"] + totals["kouka"] + totals["manpu"]
    fn = font(FONT_DELA, 330)
    num = str(s)
    nw = d.textlength(num, font=fn)
    fu = font(FONT_BLACK, 100)
    x0 = W / 2 - (nw + 24 + d.textlength("種", font=fu)) / 2
    d.text((x0, 340), num, font=fn, fill=YELLOW)
    d.text((x0 + nw + 24, 640), "種", font=fu, fill=YELLOW)
    boxes = [("吹き出し集", totals["fukidashi"], "fk_shout_001"), ("効果線集", totals["kouka"], "kk_shuchu_025"),
             ("漫符集", totals["manpu"], "mp_ikari_002")]
    bw = 440
    for i, (ja, n, nm) in enumerate(boxes):
        x = 90 + i * (bw + 45)
        y = 860
        d.rounded_rectangle([x, y, x + bw, y + 500], radius=24, fill=(255, 255, 255))
        key = {"fk": "fukidashi", "kk": "kouka", "mp": "manpu"}[nm[:2]]
        p = pick(key, [nm])[0]
        if key == "kouka":
            art = render_svg(p, width=bw * 1.3)
            ox, oy = (art.width - (bw - 40)) // 2, (art.height - 300) // 2
            art = art.crop((ox, oy, ox + bw - 40, oy + 300))
        else:
            art = fit_render(p, bw - 120, 260)
        im.paste(art, (int(x + (bw - art.width) / 2), int(y + 30 + (300 - art.height) / 2)), art)
        text_center(d, x + bw / 2, y + 350, ja, font(FONT_BLACK, 56), INK)
        text_center(d, x + bw / 2, y + 425, "{}種".format(n), font(FONT_DELA, 44), (200, 150, 0))
    d.rectangle([0, H - 150, W, H], fill=YELLOW)
    text_center(d, W / 2, H - 112, "3点セット　｜　PNG＋SVG両対応　｜　クリスタ対応", font(FONT_BLACK, 54), INK)
    out = os.path.join(IMG, "bundle_cover.png")
    im.save(out, optimize=True)
    return out


def main():
    os.makedirs(DIST, exist_ok=True)
    os.makedirs(IMG, exist_ok=True)
    if "--no-build" not in sys.argv:
        res = build_all()
        write_manifest(res)
    totals = {}
    for key in SETS:
        if "--no-zip" not in sys.argv:
            totals[key] = make_zip(key)
        else:
            totals[key] = len(read_manifest(key))
        cover(key, totals[key], "ja")
        cover(key, totals[key], "en")
        overview(key, totals[key])
        for k, (title, names) in enumerate(SAMPLES[key]):
            sample_sheet(key, title, names, "{}_sample_{}.png".format(key, k + 2), SAMPLE_COLORS[k % 4],
                         cols=4 if key == "kouka" else (5 if key in ("manpu", "seijin") and len(names) > 8 else 4),
                         crop_panels=(key == "kouka" or names[0].startswith("sj_haikei")))
        print("images", key)
    bundle_cover(totals)
    usage_page()
    print(totals)


if __name__ == "__main__":
    main()
