"""Sound for YA DONYA (v4). Every event is derived from edl3, so sound and picture share one clock."""
import sys, os, json, subprocess, numpy as np, soundfile as sf, scipy.signal as sg
sys.path.insert(0, os.path.dirname(__file__))
from edl4 import *
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000; n = int(DUR * SR); T = np.arange(n) / SR
db = lambda x: 10 ** (x / 20)
rng = np.random.default_rng(9)
def place(buf, x, t, g=0.0):
    i = int(round(t * SR))
    if i < 0: x = x[-i:]; i = 0
    L = min(len(x), n - i)
    if L > 0: buf[i:i + L] += x[:L] * db(g)
def fades(x, a=0.004, b=0.004):
    x = x.copy(); ia, ib = int(a * SR), int(b * SR)
    if ia: x[:ia] *= np.linspace(0, 1, ia)[:, None]
    if ib: x[-ib:] *= np.linspace(1, 0, ib)[:, None]
    return x
AMB = {}
def amb(c):
    if c not in AMB: AMB[c], _ = sf.read(f'{ROOT}/amb/{c}.wav')
    return AMB[c]
def rms_db(y): return 20 * np.log10(np.sqrt((y ** 2).mean()) + 1e-9)
FILL = {'IMG_5736': 'IMG_5724'}          # same street from a balcony: continues the bed when a slowed shot outlasts its sound
def clip_audio(c, s0, dur):
    y = amb(c); a = int(max(0, s0) * SR); need = int(dur * SR); x = y[a:a + need] * db(-24 - rms_db(y))
    if len(x) < need:
        src = FILL.get(c, c); z = amb(src); z = z * db(-24 - rms_db(z)); xf = int(0.25 * SR)
        fill = np.concatenate([z] * (1 + need // len(z)))[:need - len(x) + xf]
        if len(x) > xf:
            r = np.linspace(0, 1, xf)[:, None]
            x = np.concatenate([x[:-xf], x[-xf:] * np.cos(r * np.pi / 2) + fill[:xf] * np.sin(r * np.pi / 2), fill[xf:]])
        else: x = np.concatenate([x, fill[xf:]])
    return x[:need]

def ir(t60=2.6, pre=0.025, seed=0):
    r = np.random.default_rng(seed); L = int((t60 + pre) * SR); t = np.arange(L) / SR
    x = r.normal(0, 1, (L, 2)) * np.exp(-6.9 * t / t60)[:, None]
    b, a = sg.butter(1, 4500, 'lp', fs=SR); x = sg.lfilter(b, a, x, axis=0)
    x[:int(pre * SR)] = 0; return x / np.sqrt((x ** 2).sum(0))

# ---------------- music ----------------
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{ROOT}/drive2/audio/new.mp4', '-vn', '-ac', '2', '-ar', str(SR),
                f'{ROOT}/out4/song48.wav'], check=True)
song, _ = sf.read(f'{ROOT}/out4/song48.wav')
M = np.zeros((n, 2)); i0 = int(P * SR); L = min(len(song), n - i0); M[i0:i0 + L] = song[:L]
# ending: the last held note blooms into a hall instead of the file's abrupt cut
s_a, s_b = 43.6, 46.0
seg_ = song[int(s_a * SR):int(s_b * SR)]
wet = np.stack([sg.fftconvolve(seg_[:, c], ir(3.2, 0.03, 1)[:, c]) for c in range(2)], 1) * 0.9
wenv = np.clip((np.arange(len(wet)) / SR - (44.9 - s_a)) / 0.7, 0, 1)
place_t = V(s_a); Wt = np.zeros((n, 2)); place(Wt, wet * wenv[:, None], place_t)
dry_env = np.clip((V(45.95) - T) / 0.45, 0, 1); M *= dry_env[:, None]
M += Wt * np.clip((V(47.45) - T) / 0.6, 0, 1)[:, None] ** 0.5
# intro handoff: reverse-reverb swell of the first syllable rising into the first note
first = song[int(0.10 * SR):int(0.75 * SR)]
rv = np.stack([sg.fftconvolve(first[:, c], ir(2.2, 0.02, 2)[:, c]) for c in range(2)], 1)[::-1]
rv = rv / np.abs(rv).max() * 0.35
ON = V(0.13); swell_len = 0.62; seg_r = rv[-int(swell_len * SR):]
env = np.linspace(0, 1, len(seg_r)) ** 2.2
place(M, seg_r * env[:, None], ON - swell_len)

# ---------------- city ----------------
A = np.zeros((n, 2))
XF = int(0.03 * SR)
for s in SEGS:
    a, b = s['a'], s['b']; s0 = s['keys'][0][1] if s['keys'] else s['s0']
    sp = ((s['keys'][-1][1] - s['keys'][0][1]) / max(1e-6, s['keys'][-1][0] - s['keys'][0][0])) if s['keys'] else 1.0
    kind = s['tin'][0]; xin = s['tin'][1] / FPS if kind in ('dissolve', 'carry') else 0.03
    xin = max(xin, 0.03 if kind != 'dissolve' else 0.18)                                        # dissolves breathe in sound too
    nxt = SEGS[SEGS.index(s) + 1] if SEGS.index(s) + 1 < len(SEGS) else None
    xout = 0.03
    if nxt is not None and nxt['tin'][0] in ('dissolve', 'carry'): xout = max(0.03 if nxt['tin'][0] == 'carry' else 0.18, nxt['tin'][1] / FPS)
    pre = xin / 2; post = xout / 2
    dur = b - a + pre + post
    x = clip_audio(s['clip'], s0 - pre * min(1, sp), dur)
    if s['name'].startswith('flash') or s['name'] == 'hook':
        x = x * db(4); x[:int(0.03 * SR)] *= db(3)
        x = fades(x, 0.003, 0.012 if s['name'] != 'flash11' else 0.03)
    else:
        L = len(x); e = np.ones(L); i1 = max(1, int(xin * SR)); i2 = max(1, int(xout * SR))
        e[:i1] = np.sin(np.linspace(0, np.pi / 2, i1)) ** 2; e[-i2:] = np.cos(np.linspace(0, np.pi / 2, i2)) ** 2
        x = x * e[:, None]
    place(A, x, a - pre)
def bump(a, b, ramp): return np.minimum(np.clip((T - (a - ramp)) / ramp, 0, 1), np.clip(((b + ramp) - T) / ramp, 0, 1))
lvl = np.full(n, -10.0)
intro = np.where(T < SLAM + 0.06, 1.0, np.clip(1 - (T - (SLAM + 0.06)) / 0.6, 0, 1) ** 1.5)
lvl += 13 * intro                                                 # the collage settles into the balcony's street
lvl -= 5 * bump(V(0.10), V(1.60), 0.35)                           # make room as the voice enters - never silence
for a_, b_ in [(9.00, 9.28), (16.65, 17.60), (27.20, 27.95), (36.75, 37.55), (40.94, 41.55)]:
    lvl += 6 * bump(V(a_), V(b_), 0.12)
for tp, g in [(V(12.60), 7), (V(17.60), 6), (V(32.75), 7), (V(37.10), 7)]:   # riders, car, motorbike, SUV - the objects that carry the cuts
    lvl += g * np.exp(-((T - tp) / 0.30) ** 2)
lvl += 3 * bump(JOY[0], JOY[-1], 0.05)
lvl -= 4 * bump(V(37.59), V(44.0), 0.3)
lvl -= 45 * np.clip((T - V(SONG_FREEZE)) / 0.25, 0, 1)
A *= db(lvl)[:, None]

# ---------------- accents ----------------
X = np.zeros((n, 2))
y5968 = amb('IMG_5968')
horn1 = fades(y5968[int(0.60 * SR):int(0.99 * SR)], 0.003, 0.03); horn2 = fades(y5968[int(2.04 * SR):int(2.41 * SR)], 0.003, 0.03)
hp = sg.butter(2, 250, 'hp', fs=SR, output='sos')
horn1 = sg.sosfiltfilt(hp, horn1, axis=0); horn2 = sg.sosfiltfilt(hp, horn2, axis=0)
place(X, horn1 / np.abs(horn1).max(), 0.0, -9)                  # Cairo opens with a horn
place(X, horn2 / np.abs(horn2).max(), SLAM - 0.01, -10)         # ...and answers on the title
def noise_sweep(t_peak, rise, fall, f0, f1, g, seed=4):
    r = np.random.default_rng(seed); L = int((rise + fall) * SR); w = r.normal(0, 1, (L, 2))
    out = np.zeros_like(w); hop = 2400
    for k in range(0, L, hop):           # moving band-pass
        tt = k / L; fc = f0 * (f1 / f0) ** min(1, tt * (rise + fall) / rise)
        sos = sg.butter(2, [fc * 0.6, min(fc * 1.6, 20000)], 'bp', fs=SR, output='sos')
        out[k:k + hop] = sg.sosfilt(sos, w[k:k + hop + 2000], axis=0)[:min(hop, L - k)]
    x = np.arange(L) / SR; e = np.where(x < rise, (x / rise) ** 2.4, np.exp(-(x - rise) / (fall / 3)))
    out = out / np.abs(out).max() * e[:, None]
    B = np.zeros((n, 2)); place(B, out, t_peak - rise, g); return B
X += noise_sweep(SLAM, 1.45, 0.10, 300, 6000, -19)              # riser into the title
mech, _ = sf.read(f'{ROOT}/ana2/mech.wav')
clunk = fades(mech[int(0.1058 * SR):int(0.50 * SR)], 0.002, 0.15); clunk /= np.abs(clunk).max()
place(X, clunk, SLAM - 0.004, -14)                              # weight under the title slam
def thump(t, g):
    L = int(0.35 * SR); tt = np.arange(L) / SR; x = np.sin(2 * np.pi * (58 - 18 * tt) * tt) * np.exp(-tt / 0.09)
    B = np.zeros((n, 2)); place(B, np.stack([x, x], 1), t, g); return B

mix = M + A + X
os.makedirs(f'{ROOT}/out4', exist_ok=True)
for nm, arr in [('mix_pre', mix), ('stem_music', M), ('stem_city', A), ('stem_fx', X)]:
    sf.write(f'{ROOT}/out4/{nm}.wav', arr.astype(np.float32), SR, subtype='FLOAT')
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', f'{ROOT}/out4/mix_pre.wav', '-af', 'loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json',
                    '-f', 'null', '-'], capture_output=True, text=True).stderr
m = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
af = (f"loudnorm=I=-14:TP=-1.0:LRA=11:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
      f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']},aresample=48000")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{ROOT}/out4/mix_pre.wav', '-af', af, '-ar', '48000', f'{ROOT}/out4/mix.wav'], check=True)
print('measured', m['input_i'], m['input_tp'], '-> out4/mix.wav')
