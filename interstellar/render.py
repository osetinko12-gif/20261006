"""Render every shot in parallel, concat, mux with the score."""
import subprocess, sys, os
from multiprocessing import Pool
from PIL import Image
from common import W, H, FPS, clamp
from timeline import SHOTS, FADE_IN

FADE = 0.6
def render_shot(k):
    fn, a, b, _ = SHOTS[k]
    out = f'out/seg_{k:03d}.mp4'
    n = int(round((b - a) * FPS))
    fin = k in FADE_IN; fout = (k + 1) in FADE_IN or k == len(SHOTS) - 1
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-vf', 'scale=1920:1080:flags=neighbor', '-c:v', 'libx264',
                          '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    black = Image.new('RGB', (W, H))
    for i in range(n):
        lt = i / FPS; im = fn(a + lt).convert('RGB')
        if im.size != (W, H): im = im.resize((W, H), Image.NEAREST)
        if fin and lt < FADE: im = Image.blend(black, im, lt / FADE)
        if fout and lt > (b - a) - FADE: im = Image.blend(im, black, clamp((lt - ((b - a) - FADE)) / FADE))
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    return k

if __name__ == '__main__':
    ks = list(range(len(SHOTS))) if len(sys.argv) < 2 else [int(x) for x in sys.argv[1:]]
    with Pool(4) as pool:
        for k in pool.imap_unordered(render_shot, ks): print('done', k, flush=True)
    with open('out/segs.txt', 'w') as f:
        for k in range(len(SHOTS)): f.write(f"file 'seg_{k:03d}.mp4'\n")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'out/segs.txt', '-i', 'out/score_n.wav',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', 'out/interstellar_8bit.mp4'], check=True)
    print('final written')
