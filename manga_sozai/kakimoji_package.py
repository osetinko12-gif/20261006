"""成人向け描き文字集：zip（色ごと）・一覧表・表紙・サンプル画像."""
import csv
import os
import shutil
import zipfile

from PIL import Image, ImageDraw

from kakimoji import STYLES
from kakimoji_build import FONT_SET, OUT, fname
from kakimoji_words import WORDS
from package import (APPS_TXT, DIST, FONT_BLACK, FONT_BOLD, FONT_DELA, IMG, INK, TERMS_TXT, checker, fit_render,
                     font, text_center, to_la, watermark)

TITLE = "成人向け描き文字集"
ZIP_BASE = "kakimoji_R18"
PINK = (255, 79, 147)


def manifest():
    with open(os.path.join(OUT, "manifest.csv"), encoding="utf-8") as f:
        return [tuple(r) for r in csv.reader(f)]


def svg_path(style, fdir, cat, w):
    return os.path.join(OUT, style, fdir, cat, fname(w) + ".svg")


def catalog(cat, rows, fdir, out_path, cols=10, cell=210):
    lab_h = 40
    head = 100
    n = len(rows)
    rws = (n + cols - 1) // cols
    W, H = cols * cell, head + rws * (cell + lab_h) + 10
    im = checker(W, H)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, head], fill=INK)
    d.text((24, 20), "{}  {}（{}）".format(WORDS[cat][0], fdir[2:], n), font=font(FONT_BLACK, 40), fill=(255, 255, 255))
    f = font(FONT_BOLD, 20)
    for i, (c, w) in enumerate(rows):
        r_, c_ = divmod(i, cols)
        x0, y0 = c_ * cell, head + r_ * (cell + lab_h)
        art = fit_render(svg_path("1_黒文字", fdir, cat, w), cell - 30, cell - 20)
        im.paste(art, (x0 + (cell - art.width) // 2, y0 + (cell - art.height) // 2), art)
        d.text((x0 + 8, y0 + cell + 6), fname(w), font=f, fill=(40, 40, 40))
    im.save(out_path, optimize=True)


def make_zips():
    rows = manifest()
    total_words = len(rows)
    cats = list(WORDS.keys())
    os.makedirs(DIST, exist_ok=True)
    # 共通：一覧表・説明書
    common = os.path.join(DIST, "_kaki_common")
    if os.path.isdir(common):
        shutil.rmtree(common)
    os.makedirs(os.path.join(common, "一覧表"))
    for c in cats:
        catalog(c, [r for r in rows if r[0] == c], FONT_SET[0][0], os.path.join(common, "一覧表", "{}_{}.png".format(c, WORDS[c][0].split("（")[0])))
    with open(os.path.join(common, "言葉一覧.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["分類フォルダ", "分類", "言葉（ファイル名）"])
        for c, wd in rows:
            w.writerow([c, WORDS[c][0], fname(wd)])
    n_items = total_words * len(FONT_SET) * len(STYLES)
    desc = ["{}　{}語 × {}書体 × {}色 ＝ 全{:,}点".format(TITLE, total_words, len(FONT_SET), len(STYLES), n_items), "",
            "このたびはお買い上げありがとうございます。", "",
            "■ 内容",
            "・喘ぎ声・水音を中心に、成人向け漫画やCG集で使う描き文字を{}語収録".format(total_words),
            "・分類：" + "／".join(WORDS[c][0] for c in cats),
            "・書体：" + "／".join(f[0][2:] for f in FONT_SET),
            "・色：" + "／".join(v[0] for v in STYLES.values()),
            "・PNG（透過・600dpi）とSVG（ベクター）の両方を同梱",
            "・ファイル名が言葉そのものなので、Finder／エクスプローラーの検索ですぐ見つかります（例：じゅぷっ.png）",
            "・縦書き。等倍で1文字およそ12mm（B5原稿でそのまま使える大きさ）", "",
            "■ zipの分け方",
            "容量が大きいため、色ごとにzipを分けています。必要な色だけダウンロードしてもOKです。"]
    for st, (ja, *_r) in STYLES.items():
        desc.append("  {}_{}.zip … {}".format(ZIP_BASE, st, ja))
    desc += ["", "■ フォルダ構成（各zip共通）",
             "  PNG/<書体>/<分類>/<言葉>.png", "  SVG/<書体>/<分類>/<言葉>.svg",
             "  一覧表/ … 分類ごとに全部の言葉を並べた見本（ファイル名つき）", "  言葉一覧.csv", "",
             "■ 使い方のヒント",
             "・SVGは色を自由に変えられます（Illustrator・Affinity・Inkscapeなどで塗りの色を変更）",
             "・白フチ版は、絵の上に置いても文字が埋もれません",
             "・左右反転・回転・変形してもOKです", "",
             "■ おまけ：修正素材", "・黒棒・白棒・ハート隠し・星隠し・光修正・湯気隠し（おまけ_修正素材フォルダ）",
             "・修正の程度は、販売先の規約と法令に合わせてご判断ください", "", APPS_TXT, TERMS_TXT,
             "■ ご注意", "・成人向け作品での使用を想定した素材です。18歳未満の方はご購入いただけません。"]
    with open(os.path.join(common, "商品説明.txt"), "w", encoding="utf-8-sig") as f:
        f.write("\n".join(desc))

    paths = []
    for st in STYLES:
        zname = "{}_{}.zip".format(ZIP_BASE, st)
        zpath = os.path.join(DIST, zname)
        if os.path.exists(zpath):
            os.remove(zpath)
        root = zname[:-4]
        tmp = os.path.join(DIST, "_kaki_tmp.png")
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for fn in sorted(os.listdir(common)):
                full = os.path.join(common, fn)
                if os.path.isdir(full):
                    for g in sorted(os.listdir(full)):
                        z.write(os.path.join(full, g), os.path.join(root, fn, g))
                else:
                    z.write(full, os.path.join(root, fn))
            sh = os.path.join(os.path.dirname(OUT), "seijin", "07_shusei")
            for fn in sorted(os.listdir(sh)):
                if fn.endswith(".png"):
                    to_la(os.path.join(sh, fn), tmp)
                    z.write(tmp, os.path.join(root, "おまけ_修正素材", "PNG", fn))
                elif fn.endswith(".svg"):
                    z.write(os.path.join(sh, fn), os.path.join(root, "おまけ_修正素材", "SVG", fn))
            for fdir, _, _ in FONT_SET:
                for c in cats:
                    for cc, w in rows:
                        if cc != c:
                            continue
                        base = os.path.join(OUT, st, fdir, c, fname(w))
                        if st.startswith("4_"):
                            z.write(base + ".png", os.path.join(root, "PNG", fdir, c, fname(w) + ".png"))
                        else:
                            to_la(base + ".png", tmp)
                            z.write(tmp, os.path.join(root, "PNG", fdir, c, fname(w) + ".png"))
                        z.write(base + ".svg", os.path.join(root, "SVG", fdir, c, fname(w) + ".svg"))
        if os.path.exists(tmp):
            os.remove(tmp)
        print("zip", zname, os.path.getsize(zpath) // 1024 // 1024, "MB", flush=True)
        paths.append(zpath)
    shutil.rmtree(common)
    return total_words, n_items


TRIAL = ["あっ♡", "んぅ", "はぁはぁ", "ひぅっ", "らめぇ", "きもちいぃ♡", "くちゅくちゅ", "じゅぷっ", "ぬちゅ",
         "とろぉ", "びゅるっ", "どくどく", "ぱんぱん", "ずぷっ", "ちゅっ", "れろれろ", "むにゅ", "ぷるん", "ビクビク", "ゾクゾク"]


def make_trial():
    """無料お試し版：20語×4書体×4色."""
    rows = [r for r in manifest() if r[1] in TRIAL]
    zname = "{}_お試し版_無料.zip".format(ZIP_BASE)
    zpath = os.path.join(DIST, zname)
    root = zname[:-4]
    tmp = os.path.join(DIST, "_kaki_tmp.png")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr(os.path.join(root, "はじめにお読みください.txt"), "\ufeff" + "\n".join([
            "{}【お試し版】".format(TITLE), "",
            "製品版593語のうち{}語を、4書体×4色すべて収録した無料お試し版です。".format(len(rows)),
            "製品版には、喘ぎ声・セリフ・水音・射精音・挿入音・キス・体・反応の全593語（9,488点）と、おまけの修正素材が入っています。", "",
            TERMS_TXT, "■ ご注意", "・成人向け作品での使用を想定した素材です。18歳未満の方はご利用いただけません。"]))
        for st in STYLES:
            for fdir, _, _ in FONT_SET:
                for c, w in rows:
                    base = os.path.join(OUT, st, fdir, c, fname(w))
                    if st.startswith("4_"):
                        z.write(base + ".png", os.path.join(root, st, "PNG", fdir, fname(w) + ".png"))
                    else:
                        to_la(base + ".png", tmp)
                        z.write(tmp, os.path.join(root, st, "PNG", fdir, fname(w) + ".png"))
                    z.write(base + ".svg", os.path.join(root, st, "SVG", fdir, fname(w) + ".svg"))
    if os.path.exists(tmp):
        os.remove(tmp)
    print("zip", zname, os.path.getsize(zpath) // 1024 // 1024, "MB")
    return zpath


# ---------------------------------------------------------------- images
def put_word(im, st, fdir, cat, w, box):
    x0, y0, bw, bh = box
    art = fit_render(svg_path(st, fdir, cat, w), bw, bh)
    im.paste(art, (int(x0 + (bw - art.width) / 2), int(y0 + (bh - art.height) / 2)), art)


def cover(total_words, n_items, lang="ja"):
    W = H = 1600
    im = Image.new("RGB", (W, H), (24, 18, 24))
    d = ImageDraw.Draw(im)
    if lang == "ja":
        text_center(d, W / 2, 60, "成人向け描き文字集", font(FONT_BLACK, 112), (255, 255, 255), spacing=8)
        text_center(d, W / 2, 210, "喘ぎ声・水音・擬音を全部まとめて", font(FONT_BOLD, 40), (255, 190, 215))
    else:
        text_center(d, W / 2, 70, "ADULT MANGA SFX LETTERING", font(FONT_BLACK, 84), (255, 255, 255))
        text_center(d, W / 2, 210, "Japanese moans & wet sounds, hand-lettered style", font(FONT_BOLD, 38), (255, 190, 215))
    num = "{:,}".format(n_items)
    fn = font(FONT_DELA, 250)
    nw = d.textlength(num, font=fn)
    fu = font(FONT_BLACK, 90)
    unit = "点" if lang == "ja" else ""
    uw = d.textlength(unit, font=fu)
    x0 = W / 2 - (nw + 20 + uw) / 2
    d.text((x0, 270), num, font=fn, fill=PINK)
    if unit:
        d.text((x0 + nw + 20, 440), unit, font=fu, fill=PINK)
    sub = "{}語 × {}書体 × {}色".format(total_words, len(FONT_SET), len(STYLES)) if lang == "ja" else \
        "{} WORDS x {} STYLES x {} COLORS".format(total_words, len(FONT_SET), len(STYLES))
    text_center(d, W / 2, 590, sub, font(FONT_BLACK, 58), (255, 255, 255))
    # 白いパネルに見本
    d.rounded_rectangle([60, 700, W - 60, 1380], radius=28, fill=(255, 255, 255))
    picks = [("4_ピンク_白フチ", "A_筆", "01_aegi", "あっ♡"), ("1_黒文字", "C_極太", "03_mizu", "じゅぷっ"),
             ("1_黒文字", "A_筆", "05_sounyu", "ぱんっ"), ("4_ピンク_白フチ", "D_丸文字", "02_serifu", "らめぇ"),
             ("1_黒文字", "B_細筆", "04_shasei", "びゅるるっ"), ("4_ピンク_白フチ", "C_極太", "03_mizu", "ぐちゅぐちゅ♡"),
             ("1_黒文字", "D_丸文字", "08_hannou", "ビクビク"), ("4_ピンク_白フチ", "B_細筆", "01_aegi", "はぁはぁ♡")]
    cw = (W - 160) / len(picks)
    for i, (st, fd, c, w) in enumerate(picks):
        put_word(im, st, fd, c, w, (80 + i * cw, 730, cw - 10, 620))
    d.rectangle([0, H - 170, W, H], fill=PINK)
    tag = "R18　｜　PNG＋SVG　｜　黒・白・ピンク" if lang == "ja" else "18+  |  PNG + SVG  |  BLACK / WHITE / PINK"
    text_center(d, W / 2, H - 125, tag, font(FONT_BLACK, 60), (255, 255, 255))
    out = os.path.join(IMG, "kakimoji_cover{}.png".format("" if lang == "ja" else "_EN"))
    im.save(out, optimize=True)
    return out


def sample(title, items, out_name, color, cols=6, cell=250, cell_h=None):
    cell_h = cell_h or cell
    W = cols * cell + 60
    head = 140
    rws = (len(items) + cols - 1) // cols
    H = head + rws * cell_h + 40
    im = checker(W, H, s=20)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, head], fill=color)
    d.text((40, 30), title, font=font(FONT_BLACK, 60), fill=(255, 255, 255))
    d.text((W - 40 - d.textlength(TITLE, font=font(FONT_BOLD, 32)), 50), TITLE, font=font(FONT_BOLD, 32), fill=(255, 255, 255))
    for i, (st, fd, c, w) in enumerate(items):
        r_, c_ = divmod(i, cols)
        put_word(im, st, fd, c, w, (30 + c_ * cell + 10, head + 20 + r_ * cell_h + 10, cell - 20, cell_h - 20))
    im = watermark(im)
    out = os.path.join(IMG, out_name)
    im.save(out, optimize=True)
    return out


def samples(rows):
    by = {}
    for c, w in rows:
        by.setdefault(c, []).append(w)
    fonts = [f[0] for f in FONT_SET]
    outs = []
    # 1. 書体×色の見本
    words4 = [("01_aegi", "あっ♡"), ("03_mizu", "くちゅくちゅ"), ("05_sounyu", "ずぷっ"), ("02_serifu", "イクッ")]
    items = []
    for st in STYLES:
        for fd in fonts:
            c, w = words4[fonts.index(fd)]
            items.append((st, fd, c, w))
    outs.append(sample("4書体 × 4色", items, "kakimoji_sample_1_styles.png", (40, 30, 40), cols=4, cell=300))
    # 2-5. 分類ごと
    plans = [("喘ぎ声・セリフ", ["01_aegi", "02_serifu"], (230, 70, 130)),
             ("水音・射精音", ["03_mizu", "04_shasei"], (60, 120, 210)),
             ("挿入音・キス・体", ["05_sounyu", "06_kiss", "07_karada"], (130, 90, 190)),
             ("反応・ふるえ", ["08_hannou"], (40, 160, 120))]
    for k, (title, cs, color) in enumerate(plans):
        items = []
        j = 0
        for c in cs:
            ws = by[c]
            step = max(1, len(ws) // (18 // len(cs) + 1))
            for w in ws[::step][: 18 // len(cs)]:
                st = list(STYLES)[j % 4] if j % 3 == 0 else "1_黒文字"
                items.append((st, fonts[j % 4], c, w))
                j += 1
        outs.append(sample(title, items, "kakimoji_sample_{}.png".format(k + 2), color, cols=9, cell=170, cell_h=520))
    return outs


if __name__ == "__main__":
    import sys
    rows = manifest()
    if "--trial" in sys.argv:
        make_trial()
        raise SystemExit
    if "--no-zip" in sys.argv:
        tw, ni = len(rows), len(rows) * len(FONT_SET) * len(STYLES)
    else:
        tw, ni = make_zips()
    cover(tw, ni, "ja")
    cover(tw, ni, "en")
    samples(rows)
    print(tw, ni)
