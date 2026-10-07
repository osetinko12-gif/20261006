import json, sys, urllib.request, urllib.parse
def say(text, spk, out, speed=0.95, pitch=0.0, intonation=1.1):
    q = urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:50021/audio_query?speaker={spk}&text={urllib.parse.quote(text)}", method="POST")).read()
    q = json.loads(q); q['speedScale']=speed; q['pitchScale']=pitch; q['intonationScale']=intonation; q['postPhonemeLength']=0.6; q['outputSamplingRate']=48000
    w = urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:50021/synthesis?speaker={spk}", data=json.dumps(q).encode(), headers={'Content-Type':'application/json'})).read()
    open(out,'wb').write(w)
if __name__ == '__main__':
    say(sys.argv[1], int(sys.argv[2]), sys.argv[3])
