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
         lines=['YouTube ご担当者様。チャンネル「期限が迫っています。」を運営している者です。',
                'チャンネルのURLは、画面に表示している、ユーチューブドットコム、スラッシュ、アット、期限が迫っています、です。',
                '「満足度の低い、または不快なコンテンツ」との判定について、創作の意図と工程をご説明させていただきたく、この動画をお送りします。']),
    dict(kind='grid', title='チャンネルについて',
         lines=['本チャンネルでは、アナログホラー、フェイクドキュメンタリーと呼ばれる創作ジャンルの映像作品を制作しています。',
                'もしも日本が崩壊し、人々が地下シェルターで暮らしていたら、どんなテレビCMが流れているのか。そんな架空の世界を、昭和や平成のテレビ広告の様式で描いています。']),
    dict(kind='series', title='一つの世界観で続くシリーズ',
         lines=['各作品は単発の映像ではなく、一つの世界設定の上に積み重ねたシリーズです。',
                'クリスマス編、お正月編、大阪編と、季節や地域ごとに、崩壊後の人々の暮らしを描き分けています。']),
    dict(kind='steps', title='制作工程（企画・脚本・編集はすべて本人）',
         items=['① 企画・世界設定を考える', '② 商品名・キャッチコピー・ナレーション原稿を書く',
                '③ 一場面ずつプロンプトを書き、生成・選別を繰り返す', '④ 一部の作品はアナログ（手作業）で制作',
                '⑤ 構成・テロップ・音声・放送風の画質加工を編集'],
         lines=['企画、脚本、編集は、すべて私自身が行っています。',
                '映像素材の多くはAI生成ツールを使っていますが、一場面ごとに自分でプロンプトを書き、狙った演出になるまで生成と選別を繰り返しています。また、一部の作品はアナログの手作業で制作しています。']),
    dict(kind='shots', title='実際の制作画面',
         shots=[('prompt_memo.png', '自分で書いたプロンプトのメモ'),
                ('prompt_list.png', '作品ごとに書きためたプロンプト'),
                ('material_folder.png', '生成素材を世界観の地域ごとに管理・選別'),
                ('fcp_timeline.png', 'Final Cut Pro：映像・テロップ・ナレーション・効果音を配置'),
                ('fcp_blockmeat.png', '商品名のロゴやテロップも自作'),
                ('fcp_effects.png', 'スーパー8mm・古いフィルム等のエフェクトを手動で調整')],
         lines=['こちらは、私が書いたプロンプトのメモです。商品名とコンセプト、カットごとの展開、登場人物の衣装まで、一本のCMを自分で設計しています。',
                '使っていた生成サービスの一つは提供が終了したため生成画面は残っていませんが、作品ごとのメモが数多く残っています。',
                '生成した素材は、旧東京、旧北海道といった世界観の地域ごとに整理し、使えるカットを選別しています。',
                'そしてFinal Cut Proで、映像、テロップ、ナレーション、効果音を、カットごとに一つずつ配置しています。',
                '商品名のロゴやテロップも、作品ごとに作っています。',
                'さらに、古いフィルムや画質の悪いテレビといったエフェクトを自分で調整し、当時の放送の質感を作り込んでいます。']),
    dict(kind='quotes', title='視聴者の反応',
         pages=[('「崩壊した日本。地下シェルターの食品広告」　22万回視聴・コメント353件',
                 ['絶望的な状況なのにやたら陽気なのは昭和の力。', '重金属たっぷりはアカンやろｗ',
                  'ヌカラムネ出だ瞬間ビビッと来たわ、これFalloutや', '最後の特殊復興隊のCM、なんかかっこいいですね。']),
                ('「崩壊した日本。地下シェルターの食品広告」　コメント欄より',
                 ['世界が崩壊したらみんなディストピアな昭和になってた。', 'コオロギふりかけはせめて加工してくれ…',
                  'まさかの日本版Fallout…', '199X年。地球は核の炎に包まれた…!!']),
                ('「お盆の深夜に放送される料理アニメ」　コメント欄より',
                 ['わー！おかえりなさい！新作ありがとうございます！', 'お久しぶりです',
                  '崩壊した日本シリーズの新作楽しみにしてます！'])],
         lines=['シリーズ第一作は22万回以上視聴され、350件以上のコメントをいただいています。',
                'コメント欄では、架空の商品や世界の設定について、視聴者同士で盛り上がっています。',
                '久しぶりに投稿した際には、待っていたという声や、崩壊した日本シリーズの新作を楽しみにしているという声もいただきました。']),
    dict(kind='bullets', title='「満足度の低いコンテンツ」ではないと考える理由',
         items=['驚かせること自体が目的ではなく、世界観を伝える物語', '明るい広告の語り口 × 崩壊した世界 というずれで風刺',
                '視聴者が設定を楽しみ、シリーズの続きを待っている'],
         lines=['これらの作品は、ただ視聴者を驚かせるためのものではありません。',
                '明るい広告の語り口と、崩壊した世界とのずれを通して、災害への備えや消費社会を風刺する創作であり、視聴者の方にも、一つの物語として楽しんでいただいています。']),
    dict(kind='bullets', title='視聴者への配慮と今後の改善',
         items=['フィクションであること・AI使用をチャンネル概要で明記', '各動画の概要欄に設定と制作意図の解説を追加',
                '驚きだけを狙ったタイトル・サムネイルは使わない', '冒頭に「フィクション・ホラー表現あり」の注意書き'],
         lines=['すべての作品がフィクションであることと、AI生成ツールの使用は、チャンネルの概要で明記しています。',
                '今後はさらに、各動画の概要欄に設定や制作意図の解説を加え、驚きだけを狙ったタイトルやサムネイルは使わず、冒頭にフィクションとホラー表現の注意書きを入れます。']),
    dict(kind='title', title='ご覧いただき、ありがとうございました',
         sub='チャンネル「期限が迫っています。」', url=URL,
         lines=['お忙しいところ恐縮ですが、改めてご審査いただけますと幸いです。ご覧いただき、ありがとうございました。']),
]

EN = [  # 英語字幕（YouTubeに字幕トラックとして追加する用）
    'Dear YouTube team, I run the channel "Kigen ga Sematteimasu" (The Deadline Is Approaching).',
    'The channel URL, shown on screen, is youtube.com/@期限が迫っています',
    'I am sending this video to explain the creative intent and production process behind my content, regarding the "low-satisfaction or disturbing content" decision.',
    'This channel produces original fiction in the genres known as analog horror and fake documentary (mockumentary).',
    'What TV commercials would air if Japan had collapsed and people lived in underground shelters? I depict this fictional world in the style of Showa- and Heisei-era Japanese TV ads.',
    'Each video is not a standalone clip but part of a series built on a single shared world setting.',
    'Christmas, New Year, Osaka: each episode portrays life after the collapse in a different season or region.',
    'I do all of the planning, scriptwriting and editing myself.',
    'Much of the footage is made with AI generation tools, but I write the prompts for every scene myself and repeat generation and selection until I get the direction I want. Some works are also made by hand, without AI.',
    'These are prompt notes I wrote myself. Product names, concepts, cut-by-cut structure and even costumes: I design each commercial myself.',
    'One of the generation services I used has shut down, so its screens no longer exist, but many notes for each work remain.',
    'Generated footage is organized by region of the fictional world, such as "Former Tokyo" and "Former Hokkaido", and I select the usable cuts.',
    'Then in Final Cut Pro, I place the footage, captions, narration and sound effects cut by cut.',
    'I also create product logos and captions for each work.',
    'I adjust effects such as old film and bad-TV signal myself to recreate the texture of broadcasts from that era.',
    'The first video in the series has over 220,000 views and more than 350 comments.',
    'In the comments, viewers enjoy discussing the fictional products and the world setting with each other.',
    'When I posted after a long break, viewers said they had been waiting and that they look forward to new episodes of the Collapsed Japan series.',
    'These works are not made simply to shock viewers.',
    'Through the gap between cheerful advertising and a collapsed world, they satirize disaster preparedness and consumer society, and viewers enjoy them as a single continuing story.',
    'The channel description clearly states that all works are fiction and that AI generation tools are used.',
    'Going forward, I will add explanations of the setting and intent to each video description, avoid shock-only titles and thumbnails, and add a fiction / horror notice at the start of videos.',
    'Thank you for your time. I would appreciate it if you could review my channel again. Thank you for watching.',
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
    elif k in ('shots', 'quotes'):
        header(d, s['title'])
    elif k == 'placeholder':
        header(d, s['title'])
        d.rectangle([160, 230, W - 160, 800], outline=SUB, width=4)
        for j, ln in enumerate(s['note'].split('\n')):
            d.text((220, 360 + j * 80), ln, font=f(46), fill=ACC)
    return im

def shot_slide(base, s, li):
    name, cap = s['shots'][li]
    im = base.copy(); d = ImageDraw.Draw(im)
    sh = Image.open(os.path.join(ROOT, 'assets', 'process', name)).convert('RGB')
    bw, bh = W - 240, 660
    r = min(bw / sh.width, bh / sh.height)
    sh = sh.resize((int(sh.width * r), int(sh.height * r)), Image.LANCZOS)
    x, y = (W - sh.width) // 2, 215 + (bh - sh.height) // 2
    d.rectangle([x - 4, y - 4, x + sh.width + 3, y + sh.height + 3], fill=SUB)
    im.paste(sh, (x, y))
    cf = f(36); d.text((W - 120 - cf.getlength(cap), 130), cap, font=cf, fill=ACC)
    return im

def quote_slide(base, s, li):
    stat, qs = s['pages'][li]
    im = base.copy(); d = ImageDraw.Draw(im)
    d.text((160, 215), stat, font=f(38), fill=ACC)
    for i, q in enumerate(qs):
        y = 300 + i * 135
        d.rounded_rectangle([160, y, W - 160, y + 105], radius=18, fill=(32, 38, 54))
        d.text((200, y + 26), q, font=f(48), fill=FG)
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
        cur = shot_slide(slide, s, li) if s['kind'] == 'shots' else quote_slide(slide, s, li) if s['kind'] == 'quotes' else slide
        png = os.path.join(BUILD, f'f{si:02d}_{li:02d}.png'); subtitle(cur, line).save(png)
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
out = os.path.join(ROOT, 'appeal_final.mp4')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
                '-i', os.path.join(BUILD, 'list.txt'), '-c', 'copy', out], check=True)
open(os.path.join(ROOT, 'appeal_ja.srt'), 'w', encoding='utf-8').write('\n'.join(srt))
en = [b.split('\n')[:2] + [EN[i]] for i, b in enumerate(srt)]
open(os.path.join(ROOT, 'appeal_en.srt'), 'w', encoding='utf-8').write('\n'.join('\n'.join(x) + '\n' for x in en))
print(f'{out}  {t:.1f}s')
