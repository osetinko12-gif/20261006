# 台本 script.json を Azure Speech で合成し、build/ に各行の wav と timeline.json を作る
# 使い方: python3 tts.py [--force]
import json, os, sys, subprocess, hashlib, urllib.request
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, 'build'); os.makedirs(B, exist_ok=True)
REGION = os.environ.get('AZURE_SPEECH_REGION', 'japaneast')
sc = json.load(open(os.path.join(HERE, 'script.json')))

def synth(text, out):
    ssml = (f'<speak version="1.0" xml:lang="ja-JP"><voice name="{sc["voice"]}">'
            f'<prosody rate="{sc["rate"]}">{escape(text)}</prosody></voice></speak>')
    req = urllib.request.Request(f'https://{REGION}.tts.speech.microsoft.com/cognitiveservices/v1', data=ssml.encode(),
        headers={'Content-Type': 'application/ssml+xml', 'X-Microsoft-OutputFormat': 'riff-48khz-16bit-mono-pcm', 'User-Agent': 'artvid'})
    open(out, 'wb').write(urllib.request.urlopen(req).read())

def dur(f):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))

t = sc['lead']; lines = []; scenes = []
for it in sc['items']:
    if not scenes or scenes[-1]['name'] != it['scene']:
        if scenes: scenes[-1]['t1'] = t
        scenes.append({'name': it['scene'], 't0': t})
    if 'gap' in it:
        t += it['gap']; continue
    h = hashlib.md5((sc['voice'] + sc['rate'] + it['text']).encode()).hexdigest()[:8]
    f = os.path.join(B, f'{it["id"]}_{h}.wav')
    if not os.path.exists(f) or '--force' in sys.argv:
        synth(it['text'], f); print('synth', it['id'])
    d = dur(f)
    lines.append({'id': it['id'], 'text': it['text'], 't0': round(t, 3), 't1': round(t + d, 3), 'file': os.path.basename(f)})
    t += d + it['pause']
scenes[-1]['t1'] = t
json.dump({'duration': round(t, 3), 'lines': lines, 'scenes': scenes}, open(os.path.join(HERE, 'timeline.json'), 'w'), ensure_ascii=False, indent=1)
print('total', round(t, 1), 's')
for s in scenes: print(f'{s["name"]:10s} {s["t0"]:7.1f} {s["t1"]-s["t0"]:6.1f}')
