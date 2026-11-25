"""Sound for YA DONYA (v6). Every event is derived from edl3, so sound and picture share one clock."""
import sys, os, json, subprocess, numpy as np, soundfile as sf, scipy.signal as sg
sys.path.insert(0, os.path.dirname(__file__))
from edl6 import *
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

# ---------------- soundtrack: the recitation, untouched ----------------
song, _ = sf.read(f'{ROOT}/s6/song48.wav')
M = np.zeros((n, 2)); i0 = int(P * SR); L = min(len(song), n - i0); M[i0:i0 + L] = song[:L]

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
lvl = np.full(n, -12.0)
intro = np.where(T < SLAM + 0.06, 1.0, np.clip(1 - (T - (SLAM + 0.06)) / 0.8, 0, 1) ** 1.5)
lvl += 15 * intro                                   # the opening collage settles under the first words
for k in range(1, 35):                              # the city breathes in the speaker's pauses
    a_, b_ = LE[k - 1], LS[k]
    if b_ - a_ > 0.35: lvl += 4 * bump(V(a_ + 0.08), V(b_ - 0.08), 0.12)
lvl -= 30 * np.clip((T - (V(AUDIO_END) + 0.3)) / 1.2, 0, 1)
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
os.makedirs(f'{ROOT}/out7', exist_ok=True)
for nm, arr in [('mix_pre', mix), ('stem_music', M), ('stem_city', A), ('stem_fx', X)]:
    sf.write(f'{ROOT}/out7/{nm}.wav', arr.astype(np.float32), SR, subtype='FLOAT')
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', f'{ROOT}/out7/mix_pre.wav', '-af', 'loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json',
                    '-f', 'null', '-'], capture_output=True, text=True).stderr
m = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
af = (f"loudnorm=I=-14:TP=-1.0:LRA=11:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
      f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']},aresample=48000")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{ROOT}/out7/mix_pre.wav', '-af', af, '-ar', '48000', f'{ROOT}/out7/mix.wav'], check=True)
print('measured', m['input_i'], m['input_tp'], '-> out7/mix.wav')
