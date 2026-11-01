"""成人向け描き文字集を量産する.

out/kakimoji/<色>/<書体>/<分類>/<言葉>.svg / .png
"""
import csv
import os
import sys
from multiprocessing import Pool

from kakimoji import STYLES, save_styled, word
from kakimoji_words import WORDS, words

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "kakimoji")
FONT_SET = [  # (フォルダ名, フォントキー, 太らせ量)
    ("A_筆", "brush", 0.015),
    ("B_細筆", "kurenaido", 0.03),
    ("C_極太", "reggae", 0.0),
    ("D_丸文字", "maru", 0.022),
]
SIZE = 12.0  # 1文字の大きさ(mm)


def fname(w):
    return w.replace("/", "／").replace("?", "？").replace(":", "：").replace("*", "＊")


def job(args):
    cat, w, fdir, fkey, bold, idx = args
    # 分類ごとの勢い：擬音系は傾き強め、喘ぎ・セリフは控えめ
    tilt = {"05_sounyu": 12, "04_shasei": 11, "03_mizu": 10}.get(cat, 8)
    g = word(w, fkey, SIZE, idx, bold=bold, tilt=tilt)
    for st in STYLES:
        base = os.path.join(OUT, st, fdir, cat, fname(w))
        os.makedirs(os.path.dirname(base), exist_ok=True)
        save_styled(g, base, st, fringe=SIZE * 0.075)
    return cat, w, fdir


def build(limit=None):
    tasks = []
    ws = words()
    if limit:
        ws = ws[::max(1, len(ws) // limit)][:limit]
    for i, (cat, w) in enumerate(ws):
        for fdir, fkey, bold in FONT_SET:
            tasks.append((cat, w, fdir, fkey, bold, i))
    with Pool(4) as p:
        for k, _ in enumerate(p.imap_unordered(job, tasks, chunksize=4)):
            if k % 200 == 0:
                print(k, "/", len(tasks), flush=True)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "manifest.csv"), "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(ws)
    return ws


if __name__ == "__main__":
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else None
    ws = build(lim)
    print(len(ws), "words")
