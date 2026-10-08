"""Edit decision list: (scene, local start, local end, music-section label)."""
from op import op
from act1 import *
from act2 import *
from act3 import *
from act4 import *

SHOTS = [
    # OPENING
    (op, 0, 14, 'op'),
    # ACT 1 — Earth
    (s01_farm, 0, 8, 'earth'), (s02_dust, 0, 11, 'earth'), (s03_ghost, 0, 12, 'earth'),
    (s04_drone, 0, 11, 'earth'), (s05_coords, 0, 10, 'earth'), (s06_nasa, 0, 12, 'earth'),
    (s07_goodbye, 0, 7, 'farewell'), (s07b_watches, 0, 5, 'farewell'), (s07_goodbye, 7, 11, 'farewell'),
    (s08_leave, 0, 5, 'launch'), (s09_launch, 0, 4, 'launch'), (s08_leave, 5, 11, 'launch'), (s09_launch, 4, 12, 'launch'),
    # ACT 2 — space, the water planet, lost years
    (s10_orbit, 0, 10, 'space'), (s11_saturn, 0, 9, 'space'), (s12_wormhole, 0, 10, 'space'), (s13_inside, 0, 8, 'space'),
    (s14_miller, 0, 10, 'miller'), (s15_wave, 0, 5, 'miller'), (s15b_lookup, 0, 3, 'miller'), (s15_wave, 5, 9, 'miller'),
    (s16_escape, 0, 8, 'miller'),
    (s17_23years, 0, 11, 'loss'), (s18_messages, 0, 13, 'loss'), (s19_murph, 0, 11, 'loss'),
    # ACT 3 — Mann, the spin, Gargantua
    (s20_ice, 0, 9, 'mann'), (s21_mann, 0, 9, 'mann'), (s22_betrayal, 0, 11.5, 'mann'), (s22b_trap, 0, 7, 'mann'), (s22c_mannflies, 0, 7.5, 'docking'),
    (s23_explosion, 2.5, 7, 'docking'), (s24_docking, 0, 4, 'docking'), (s24b_cockpit, 0, 3, 'docking'),
    (s24_docking, 4, 9, 'docking'), (s24b_cockpit, 3, 5, 'docking'), (s24c_cheer, 0, 6, 'docking'),
    (s25_gargantua, 0, 10, 'garg'), (s26_detach, 0, 11, 'garg'), (s27_fall, 0, 10, 'garg'),
    # ACT 4 — the tesseract and home
    (s28_tesseract, 0, 10, 'tess'), (s29_behind, 0, 10, 'tess'),
    (s30_watch, 0, 5, 'tess'), (s31_eureka, 0, 4, 'tess'), (s30_watch, 5, 8, 'tess'), (s31_eureka, 4, 10, 'tess'),
    (s32_papers, 0, 9, 'tess'),
    (s33_station, 0, 9, 'home'), (s34_family, 0, 10, 'home'), (s35_hands, 0, 6, 'home'), (s35b_hug, 0, 9, 'home'),
    (s36_depart, 0, 9, 'end'), (s37_edmunds, 0, 14, 'end'),
]
SHOTS = [(f, a, (a + (b - a) * 1.2) if (b - a) >= 8 and f is not op else b, lab) for f, a, b, lab in SHOTS]
# soft fades at the act breaks (index of shot that fades IN)
ACT_STARTS = ('op', 's01_farm', 's10_orbit', 's20_ice', 's28_tesseract', 's36_depart')
FADE_IN = {k for k, sh in enumerate(SHOTS) if sh[0].__name__ in ACT_STARTS and (k == 0 or SHOTS[k - 1][0] is not sh[0])}

def starts():
    out, t = [], 0.0
    for sh in SHOTS: out.append(t); t += sh[2] - sh[1]
    return out, t

def sections():
    st, total = starts(); sec = {}
    for (fn, a, b, lab), s in zip(SHOTS, st):
        lo, hi = sec.get(lab, (s, s))
        sec[lab] = (min(lo, s), max(hi, s + b - a))
    return sec, total

if __name__ == '__main__':
    sec, total = sections()
    print(f'{len(SHOTS)} shots, {total:.0f}s = {int(total // 60)}:{int(total % 60):02d}')
    for k, v in sec.items(): print(f'  {k:9s} {v[0]:6.1f} - {v[1]:6.1f}')
