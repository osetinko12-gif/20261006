# 収益化 再審査請求用動画の生成スクリプト
# 使い方: python3 make_appeal.py  (Azure TTS + ffmpeg + Pillow が必要)
import os, subprocess, wave, json, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ROOT, 'build')
THUMBS = os.path.join(ROOT, 'assets', 'thumbs')
os.makedirs(BUILD, exist_ok=True)
W, H = 1920, 1080
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
VOICE = 'ja-JP-NaokiNeural'
TTS_URL = 'https://japaneast.tts.speech.microsoft.com/cognitiveservices/v1'
BG, FG, SUB, ACC = (16, 20, 30), (238, 240, 245), (150, 160, 180), (230, 80, 70)

def f(size): return ImageFont.truetype(FONT, size)

VIDEOS = [  # (id, タイトル)
    ('3I5L4VdPqFk', '崩壊した日本。地下シェルターの食品広告'),
    ('Q2M1HjWt5hg', '崩壊した日本のクリスマス'),
    ('gPELIs9SCO0', '崩壊した日本のお正月'),
    ('ej2vgSxh0CM', '崩壊した日本の大阪'),
    ('fuv9R702wSA', '昭和風の不気味で怖い架空CM映像集'),
    ('FqdXHoacRvU', '平成風の不気味で怖い架空CM映像集'),
    ('lRXy4Ak3TiY', '本当にありそうな架空CM映像集'),
    ('7oLFg5G9GrM', 'お盆の深夜に放送される料理アニメ'),
    ('BUFSipn_JyQ', '旧東京電力からのお知らせ'),
]

# 各セクション: スライド定義 と ナレーション(1文ずつ)
URL = 'youtube.com/@期限が迫っています'

SECTIONS = [
    dict(kind='title', title='収益化 再審査のお願い',
         sub='チャンネル「期限が迫っています。」', url=URL,
         lines=['YouTube ご担当者様。',
                'チャンネル「期限が迫っています。」を運営している者です。',
                'チャンネルのURLは、画面に表示している、ユーチューブドットコム、スラッシュ、アット、期限が迫っています、です。',
                '「満足度の低い、または不快なコンテンツ」との判定について、制作の意図と工程をご説明させていただきたく、この動画をお送りします。']),
    dict(kind='grid', title='チャンネルについて',
         lines=['本チャンネルでは、アナログホラー、フェイクドキュメンタリーと呼ばれる創作ジャンルの映像作品を制作しています。',
                'もしも日本が崩壊し、人々が地下シェルターで暮らしていたら、どんなテレビCMが流れているのか。',
                'そんな架空の世界を、昭和や平成のテレビ広告の様式を借りて描いています。']),
    dict(kind='series', title='一つの世界観で続くシリーズ',
         lines=['各作品は単発の映像ではなく、一つの世界設定の上に積み重ねたシリーズです。',
                '最初の「地下シェルターの食品広告」から、クリスマス編、お正月編、大阪編と、季節や地域ごとに、崩壊後の社会で人々が何を食べ、どんな宣伝を目にしているのかを描き分けています。']),
    dict(kind='steps', title='制作工程（企画・脚本・編集はすべて本人）',
         items=['① 企画・世界設定・年表を考える', '② 商品名・キャッチコピー・ナレーション原稿を書く',
                '③ 一場面ずつプロンプトを設計し、生成・選別を繰り返す', '④ 一部の作品はアナログ（手作業）で制作',
                '⑤ 構成・テロップ・音声・放送風の画質加工を編集'],
         lines=['企画、脚本、編集は、すべて私自身が行っています。',
                'まず世界設定を考え、各CMの商品名、キャッチコピー、ナレーション原稿を書きます。',
                '映像素材の多くはAI生成ツールを使っていますが、一場面ごとに自分でプロンプトを設計し、狙った演出になるまで生成と選別を繰り返しています。',
                'また、一部の作品はAIを使わず、アナログの手作業で制作しています。',
                '最後に、編集ソフトで構成、テロップ、音声、当時のテレビ放送を再現する画質加工を加えて、一本の作品に仕上げています。']),
    dict(kind='placeholder', title='実際の制作画面',
         note='※ ここに画面録画を差し込む（合計40〜60秒）\n　 ・企画メモ／脚本　・プロンプトと没になった生成結果\n　 ・編集ソフトのタイムライン　・アナログ制作の様子',
         lines=['こちらが、実際の企画メモ、プロンプト、編集の画面です。']),
    dict(kind='bullets', title='「満足度の低いコンテンツ」ではないと考える理由',
         items=['驚かせること自体が目的ではなく、世界観を伝える物語', '明るい広告の語り口 × 崩壊した世界 というずれで風刺',
                '視聴者がコメント欄で設定を考察・議論している'],
         lines=['これらの作品は、ただ視聴者を驚かせるためのものではありません。',
                '明るく親しみやすい広告の語り口と、崩壊した世界の現実とのずれを通して、災害への備えや、消費社会、メディアの在り方を風刺する創作です。',
                '実際に、コメント欄では、多くの視聴者の方が世界観の設定を考察したり、次回作への感想を書き込んだりしてくださっています。']),
    dict(kind='placeholder', title='視聴者の反応',
         note='※ ここにコメント欄のスクリーンショットを差し込む（5〜10秒）\n　 考察・感想系のコメントが分かるもの',
         lines=['こうした反応は、作品が創作として楽しまれている証だと考えています。']),
    dict(kind='bullets', title='視聴者への配慮',
         items=['すべての作品はフィクションであることを明記', '実在の人物・団体・製品とは無関係',
                'AI生成ツールの使用もチャンネル概要で開示'],
         lines=['また、すべての作品がフィクションであり、実在の人物、団体、製品とは関係がないこと、そしてAI生成ツールを使用していることを、チャンネルの概要で明記しています。']),
    dict(kind='bullets', title='今後の改善',
         items=['各動画の概要欄に、設定と制作意図の解説を追加', '内容と関係なく驚きだけを狙ったタイトル・サムネイルは使わない',
                '冒頭に「フィクション・ホラー表現あり」の注意書きを入れる'],
         lines=['今回のご指摘を受け、今後は次の点を改善いたします。',
                '各動画の概要欄に、作品の設定や制作意図の解説を加えること。',
                '内容と関係なく、驚きだけを狙ったタイトルやサムネイルは使用しないこと。',
                'そして、動画の冒頭に、フィクションであることと、ホラー表現を含むことの注意書きを入れることです。']),
    dict(kind='title', title='ご覧いただき、ありがとうございました',
         sub='チャンネル「期限が迫っています。」', url=URL,
         lines=['お忙しいところ恐縮ですが、改めてご審査いただけますと幸いです。',
                'ご覧いただき、ありがとうございました。']),
]

def wrap(text, font, maxw):
    out, cur = [], ''
    for ch in text:
        if font.getlength(cur + ch) > maxw and ch not in '、。」）':
            out.append(cur); cur = ch
        else:
            cur += ch
    return out + ([cur] if cur else [])

def header(d, title):
    d.rectangle([120, 110, 132, 180], fill=ACC)
    d.text((160, 108), title, font=f(64), fill=FG)

def thumb(vid, size):
    return Image.open(os.path.join(THUMBS, vid + '.jpg')).convert('RGB').resize(size, Image.LANCZOS)

def base_slide(s):
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    k = s['kind']
    if k == 'title':
        bg = Image.new('RGB', (W, H))
        for i, (vid, _) in enumerate(VIDEOS[:8]):
            bg.paste(thumb(vid, (480, 270)), ((i % 4) * 480, (i // 4) * 270 + 270))
        bg = bg.filter(ImageFilter.GaussianBlur(14))
        im = Image.blend(im, bg, 0.25); d = ImageDraw.Draw(im)
        tf = f(96); tw = tf.getlength(s['title'])
        d.text(((W - tw) / 2, 380), s['title'], font=tf, fill=FG)
        sf = f(48); sw = sf.getlength(s['sub'])
        d.text(((W - sw) / 2, 530), s['sub'], font=sf, fill=SUB)
        d.rectangle([(W - 200) / 2, 500, (W + 200) / 2, 506], fill=ACC)
        uf = f(44); uw = uf.getlength(s['url'])
        d.text(((W - uw) / 2, 620), s['url'], font=uf, fill=ACC)
    elif k == 'grid':
        header(d, s['title'])
        tw, th, gap = 400, 225, 30
        x0 = (W - (tw * 4 + gap * 3)) / 2
        for i, (vid, t) in enumerate(VIDEOS[:8]):
            x, y = int(x0 + (i % 4) * (tw + gap)), 230 + (i // 4) * (th + 70)
            im.paste(thumb(vid, (tw, th)), (x, y))
            d.text((x, y + th + 10), wrap(t, f(24), tw)[0], font=f(24), fill=SUB)
    elif k == 'series':
        header(d, s['title'])
        tw, th = 380, 214
        for i, (vid, t) in enumerate(VIDEOS[:4]):
            x, y = 130 + i * 430, 330
            im.paste(thumb(vid, (tw, th)), (x, y))
            for j, ln in enumerate(wrap(t, f(28), tw)):
                d.text((x, y + th + 14 + j * 36), ln, font=f(28), fill=FG)
            if i < 3:
                d.polygon([(x + tw + 12, y + 95), (x + tw + 36, y + 107), (x + tw + 12, y + 119)], fill=ACC)
        d.text((130, 250), '「崩壊した日本」シリーズ', font=f(40), fill=SUB)
    elif k in ('steps', 'bullets'):
        header(d, s['title'])
        for i, it in enumerate(s['items']):
            y = 260 + i * 105
            if k == 'bullets': d.ellipse([160, y + 16, 184, y + 40], fill=ACC)
            d.text((210 if k == 'bullets' else 160, y), it, font=f(50), fill=FG)
    elif k == 'placeholder':
        header(d, s['title'])
        d.rectangle([160, 230, W - 160, 800], outline=SUB, width=4)
        for j, ln in enumerate(s['note'].split('\n')):
            d.text((220, 360 + j * 80), ln, font=f(46), fill=ACC)
    return im

def subtitle(im, text):
    im = im.copy(); d = ImageDraw.Draw(im, 'RGBA')
    sf = f(44); lines = wrap(text, sf, W - 300)
    top = H - 60 - len(lines) * 62
    d.rectangle([0, top - 24, W, H], fill=(0, 0, 0, 190))
    for j, ln in enumerate(lines):
        d.text(((W - sf.getlength(ln)) / 2, top + j * 62), ln, font=sf, fill=(255, 255, 255))
    return im

def tts(text, path):
    if os.path.exists(path): return
    ssml = (f'<speak version="1.0" xml:lang="ja-JP"><voice name="{VOICE}">'
            f'<prosody rate="-5%">{text}</prosody></voice></speak>')
    req = urllib.request.Request(TTS_URL, data=ssml.encode('utf-8'), headers={
        'Content-Type': 'application/ssml+xml', 'User-Agent': 'appeal',
        'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm'})
    with urllib.request.urlopen(req) as r, open(path, 'wb') as o:
        o.write(r.read())

def dur(path):
    with wave.open(path) as w: return w.getnframes() / w.getframerate()

def ts(t):
    ms = int(round(t * 1000)); return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'

PAD = 0.45
clips, srt, t, n = [], [], 0.0, 0
for si, s in enumerate(SECTIONS):
    slide = base_slide(s)
    slide.save(os.path.join(BUILD, f'slide{si:02d}.png'))
    for li, line in enumerate(s['lines']):
        n += 1
        wav = os.path.join(BUILD, f'n{si:02d}_{li:02d}.wav'); tts(line, wav)
        png = os.path.join(BUILD, f'f{si:02d}_{li:02d}.png'); subtitle(slide, line).save(png)
        mp4 = os.path.join(BUILD, f'c{si:02d}_{li:02d}.mp4')
        d = dur(wav) + PAD + (0.6 if li == len(s['lines']) - 1 else 0)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-i', png, '-i', wav,
                        '-af', f'apad=whole_dur={d}', '-t', f'{d}', '-r', '30', '-c:v', 'libx264',
                        '-tune', 'stillimage', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '48000',
                        '-b:a', '192k', mp4], check=True)
        clips.append(mp4)
        srt.append(f'{n}\n{ts(t)} --> {ts(t + dur(wav))}\n{line}\n')
        t += d

with open(os.path.join(BUILD, 'list.txt'), 'w') as o:
    o.writelines(f"file '{c}'\n" for c in clips)
out = os.path.join(ROOT, 'appeal_draft.mp4')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
                '-i', os.path.join(BUILD, 'list.txt'), '-c', 'copy', out], check=True)
open(os.path.join(ROOT, 'appeal_draft.srt'), 'w', encoding='utf-8').write('\n'.join(srt))
print(f'{out}  {t:.1f}s')
