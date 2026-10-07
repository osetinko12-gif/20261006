"""Original chiptune score + SFX for the Interstellar piece (no melodies taken from the film)."""
import numpy as np, wave
from common import osc, freq, Track, SR, clamp
from timeline import SHOTS, starts, sections

ST, TOTAL = starts()
SEC, _ = sections()

def at(fn_name, local):
    """Global time of a scene's local time (first shot that contains it)."""
    for (fn, a, b, _), s in zip(SHOTS, ST):
        if fn.__name__ == fn_name and a <= local < b: return s + local - a
    raise KeyError(fn_name)

tr = Track(TOTAL + 2)
N = lambda s: [freq(x) for x in s.split()]

# ------------------------------------------------------------ instruments
def organ(t, dur, notes, vol=0.05, att=0.5, rel=0.8):
    for f in N(notes):
        tr.add(t, osc('sq', f, dur, vol * 0.45, duty=0.5, vib=0.002, adsr=(att, 0.2, 0.9, rel)))
        tr.add(t, osc('saw', f * 2, dur, vol * 0.12, adsr=(att, 0.2, 0.9, rel)))
        tr.add(t, osc('tri', f / 2, dur, vol * 0.7, adsr=(att, 0.2, 0.9, rel)))

def pluck(t, note, vol=0.10, dec=0.5):
    tr.add(t, osc('tri', freq(note), dec, vol, adsr=(0.002, dec * 0.6, 0.0, 0.05)))
    tr.add(t, osc('sq', freq(note), dec * 0.5, vol * 0.15, duty=0.125, adsr=(0.002, dec * 0.3, 0.0, 0.05)))

def arp(t0, t1, bpm, chords, div=2, vol=0.05, kind='sq', duty=0.25, pattern=(0, 1, 2, 1)):
    step = 60 / bpm / div; t = t0; k = 0
    beats_per_chord = 4 * div
    while t < t1 - 1e-6:
        ch = N(chords[(k // beats_per_chord) % len(chords)])
        f = ch[pattern[k % len(pattern)] % len(ch)]
        tr.add(t, osc(kind, f, step * 0.9, vol, duty=duty, adsr=(0.003, step * 0.5, 0.4, 0.02)))
        t += step; k += 1

def pads(t0, t1, bpm, chords, vol=0.05):
    bar = 4 * 60 / bpm; t = t0; k = 0
    while t < t1 - 0.2:
        organ(t, min(bar, t1 - t) + 0.3, chords[k % len(chords)], vol, att=0.6, rel=0.9); t += bar; k += 1

def melody(t0, bpm, pattern, vol=0.07, kind='sq', duty=0.5):
    tr.seq(t0, bpm, pattern, kind, vol, duty=duty, vib=0.005, gate=0.95, adsr=(0.03, 0.1, 0.8, 0.2))

def tick(t, vol=0.10):
    n = int(SR * 0.03); tt = np.arange(n) / SR
    w = np.random.default_rng(int(t * 1000)).uniform(-1, 1, n); w = np.diff(w, prepend=0)
    tr.add(t, w * vol * np.exp(-tt * 160))
    tr.add(t, osc('sq', 2200, 0.012, vol * 0.3, duty=0.5, adsr=(0.001, 0.005, 0.0, 0.005)))

def noise_bed(t0, t1, vol, smooth=40, swell=0.0):
    n = int(SR * (t1 - t0)); w = np.random.default_rng(int(t0)).uniform(-1, 1, n)
    w = np.convolve(w, np.ones(smooth) / smooth, mode='same') * np.sqrt(smooth)
    env = np.ones(n); f = min(n // 2, int(SR * 1.0)); env[:f] = np.linspace(0, 1, f); env[-f:] = np.linspace(1, 0, f)
    if swell: env *= np.linspace(1 - swell, 1, n)
    tr.add(t0, w * vol * env)

def timpani(t, note='D2', vol=0.5):
    n = int(SR * 1.2); tt = np.arange(n) / SR
    f = freq(note) * (1 + 0.3 * np.exp(-tt * 20))
    tr.add(t, np.sin(2 * np.pi * np.cumsum(f) / SR) * vol * np.exp(-tt * 3.5))
    tr.add(t, np.random.default_rng(int(t * 7)).uniform(-1, 1, n) * vol * 0.2 * np.exp(-tt * 30))

THEME_CH = ['A2 E3 A3 C4 E4', 'F2 C3 F3 A3 C4', 'C3 G3 C4 E4 G4', 'G2 D3 G3 B3 D4']
SPACE_CH = ['D2 A2 E3 F3 A3', 'Bb1 F2 D3 F3 C4', 'F2 C3 A3 C4 G4', 'C2 G2 E3 G3 D4']

# ------------------------------------------------------------ cues
a, b = SEC['op']                                                       # OPENING
pads(a + 0.5, b, 60, ['D2 A2 E3', 'D2 A2 F3', 'Bb1 F2 D3', 'C2 G2 E3'], 0.035)
arp(a + 2, b - 1, 120, ['D5 A5 E6 F6', 'D5 A5 E6 A6'], div=2, vol=0.025, duty=0.125, pattern=(0, 1, 2, 3, 2, 1))
organ(a + 7, 6.5, 'D2 A2 D3 F3 A3 D4', 0.07, att=0.05, rel=2.0); timpani(a + 7, 'D2', 0.6)

a, b = SEC['earth']                                                    # EARTH — home theme
arp(a, b, 76, THEME_CH, div=2, vol=0.06, kind='tri', pattern=(0, 2, 3, 4, 3, 2, 1, 2))
pads(a + 8, b, 76, ['A2 E3 C4', 'F2 C3 A3', 'C3 G3 E4', 'G2 D3 B3'], 0.025)
bar = 4 * 60 / 76
m = 'E5:2 D5:1 C5:1 A4:4 C5:2 D5:1 E5:1 G4:4 E5:2 F5:1 E5:1 C5:3 A4:1 B4:2 C5:1 D5:1 B4:4'
for k in range(int((b - a - 2 * bar) / (4 * bar))):
    if k % 2 == 1: melody(a + 2 * bar + k * 4 * bar, 76, m, 0.05, 'sq', 0.5)
noise_bed(a, a + 12, 0.010, 200)                                       # farm wind
noise_bed(a + 12, a + 23, 0.05, 120, swell=0.8)                        # dust storm roar
noise_bed(at('s04_drone', 0), at('s04_drone', 0) + 11, 0.012, 20)     # truck engine rattle

a, b = SEC['farewell']                                                 # FAREWELL
pads(a, b, 60, ['A2 E3 C4 E4', 'F2 C3 A3 C4', 'D3 A3 F4', 'E2 B2 E3 G#3'], 0.045)
tr.seq(a + 2, 60, 'E5:3 C5:1 B4:2 A4:2 C5:3 A4:1 G#4:4', 'tri', 0.07, gate=0.95)
for k in range(int((b - a) / 1.0)): tick(a + k * 1.0, 0.04)

a, b = SEC['launch']                                                   # LAUNCH — the build
arp(a, b, 120, ['A2 E3 A3', 'F2 C3 F3', 'C3 G3 C4', 'E2 B2 E3'], div=4, vol=0.04, pattern=(0, 1, 2, 1))
L = at('s09_launch', 1.8)
for k, ch in enumerate(['A2 E3 A3 C4', 'F2 C3 A3 C4', 'C3 G3 C4 E4', 'E2 B2 G#3 B3']):
    organ(a + k * (L - a) / 4, (L - a) / 4 + 0.3, ch, 0.03 + k * 0.012, att=0.4)
organ(L, b - L, 'A2 E3 A3 C#4 E4 A4', 0.09, att=0.05, rel=2.5); timpani(L, 'A1', 0.8)
noise_bed(L, b, 0.10, 300)                                             # rocket rumble

a, b = SEC['space']                                                    # SPACE — wide and quiet
pads(a, b, 50, SPACE_CH, 0.045)
for k in range(int((b - a) / 2.4)):
    pluck(a + 1 + k * 2.4, ['A5', 'E6', 'F5', 'D6', 'C6', 'G5'][k % 6], 0.06, 1.2)
w0 = at('s12_wormhole', 0)
arp(w0, w0 + 12 + 9.6, 100, ['D5 F5 A5 E6', 'Bb4 D5 F5 C6'], div=4, vol=0.025, duty=0.125)

a, b = SEC['miller']                                                   # MILLER — ticking, rising
t = a
while t < b: tick(t, 0.09); t += 1.25
pads(a, b, 60, ['A2 E3 C4', 'Bb2 F3 D4', 'C3 G3 E4', 'D3 A3 F4'], 0.04)
W0 = at('s15_wave', 0)
arp(W0, b, 132, ['A2 A3', 'Bb2 Bb3', 'C3 C4', 'D3 D4'], div=4, vol=0.05, kind='saw', pattern=(0, 1))
noise_bed(W0, b, 0.10, 400, swell=0.9)                                  # the wave's roar
E = at('s16_escape', 2.0)
organ(E, b - E + 1.5, 'D2 A2 D3 F3 A3 D4', 0.10, att=0.03, rel=1.5); timpani(E, 'D2', 0.8)

a, b = SEC['loss']                                                     # LOSS — the 23 years
pads(a, b, 46, ['F2 C3 A3', 'A2 E3 C4', 'D2 A2 F3', 'C2 G2 E3'], 0.05)
tr.seq(a + 4, 46, 'A4:2 G4:1 F4:1 E4:4 F4:2 E4:1 D4:1 C4:4 A4:2 C5:2 B4:4', 'tri', 0.07, gate=0.95)
for k in range(int((b - a) / 1.3)): pluck(a + k * 1.3, ['A4', 'C5', 'F4', 'E4'][k % 4], 0.03, 0.9)

a, b = SEC['mann']                                                     # MANN — cold
pads(a, b, 56, ['E2 B2 G3', 'C2 G2 E3', 'E2 B2 G3', 'F2 C3 Ab3'], 0.04)
noise_bed(a, at('s22_betrayal', 0), 0.012, 300)                        # icy wind
B0 = at('s22_betrayal', 3.2)
arp(B0, b, 140, ['E3 F3', 'E3 Bb3'], div=4, vol=0.05, kind='saw', pattern=(0, 1))
timpani(B0, 'E2', 0.7); timpani(at('s22_betrayal', 5.0), 'E2', 0.7)

a, b = SEC['docking']                                                  # DOCKING — the big one
X = at('s23_explosion', 3.5)
tr.boom(X, 0.9, 3.0); timpani(X, 'D1', 0.9)
arp(X + 1, b, 120, ['D3 A3 D4 F4', 'Bb2 F3 Bb3 D4', 'F3 C4 F4 A4', 'C3 G3 C4 E4'], div=4, vol=0.06, pattern=(0, 1, 2, 3, 2, 1))
for k, ch in enumerate(['D2 A2 D3 F3 A3', 'Bb1 F2 Bb2 D3 F3', 'F2 C3 F3 A3 C4', 'C2 G2 C3 E3 G3'] * 3):
    tt = X + 1 + k * 2.0
    if tt < b: organ(tt, 2.1, ch, 0.08, att=0.05, rel=0.3)
for k in range(int((b - X) / 1.0)): timpani(X + 1 + k * 1.0, 'D2', 0.35)
noise_bed(at('s24_docking', 0), b, 0.05, 150)                          # thrusters
organ(b - 0.2, 4.0, 'D2 A2 D3 F#3 A3 D4', 0.10, att=0.02, rel=2.5)     # docked: major resolve

a, b = SEC['garg']                                                     # GARGANTUA — awe
organ(a, b - a, 'D1 A1 D2', 0.07, att=2.0, rel=2.0)
pads(a + 2, b, 40, ['D3 A3 E4 F4', 'Bb2 F3 D4 E4', 'G2 D3 Bb3 F4', 'A2 E3 C#4 E4'], 0.04)
noise_bed(at('s27_fall', 0), b, 0.08, 60, swell=0.95)                  # falling: rising hiss
tr.boom(at('s27_fall', 8.0), 0.9, 3.0)

a, b = SEC['tess']                                                     # TESSERACT — ticking to revelation
t = a
while t < b: tick(t, 0.08); t += 1.0
arp(a, b, 76, THEME_CH, div=2, vol=0.05, kind='tri', pattern=(0, 2, 3, 4, 3, 2, 1, 2))
R0 = at('s31_eureka', 4.0)
pads(a + 4, R0, 76, ['A2 E3 C4', 'F2 C3 A3', 'C3 G3 E4', 'G2 D3 B3'], 0.03)
arp(R0, b, 152, THEME_CH, div=4, vol=0.04, duty=0.25)
organ(R0, b - R0, 'A2 E3 A3 C4 E4', 0.06, att=1.5, rel=1.0)
melody(R0 + 1, 76, 'E5:2 D5:1 C5:1 A4:4 C5:2 D5:1 E5:1 G5:4 A5:4', 0.08)
noise_bed(at('s32_papers', 0), b, 0.03, 30)                            # fire crackle

a, b = SEC['home']                                                     # HOME — reunion
arp(a, b, 66, ['F2 C3 A3 C4 F4', 'C3 G3 E4 G4', 'A2 E3 C4 E4', 'G2 D3 B3 D4'], div=2, vol=0.05, kind='tri', pattern=(0, 2, 3, 4, 3, 2, 1, 2))
H0 = at('s35_hands', 0)
pads(H0, b, 66, ['F2 C3 A3', 'C3 G3 E4', 'A2 E3 C4', 'G2 D3 B3'], 0.04)
melody(H0 + 1, 66, 'C5:2 B4:1 A4:1 G4:4 A4:2 C5:1 E5:1 D5:4 C5:4', 0.06, 'tri')

a, b = SEC['end']                                                      # END — full theme, resolve
arp(a, b - 4, 76, THEME_CH, div=4, vol=0.04, duty=0.25)
pads(a, b - 5, 76, ['A2 E3 C4 E4', 'F2 C3 A3 C4', 'C3 G3 E4 G4', 'G2 D3 B3 D4'], 0.05)
melody(a + 2, 76, m, 0.07)
organ(b - 6, 6.5, 'F2 C3 F3 A3 C4 F4', 0.06, att=0.8, rel=3.0)
organ(b - 6, 6.5, 'C2 G2 C3 E3 G3 C4', 0.04, att=2.5, rel=3.0)

if __name__ == '__main__':
    tr.write('out/score.wav', TOTAL, echo=0.3, delay=0.22)
    print('score', TOTAL)
