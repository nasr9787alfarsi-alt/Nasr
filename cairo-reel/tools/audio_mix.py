import sys, os, subprocess, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(__file__))
from edl import *
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
OUT = f'{ROOT}/out/mix.wav'
n = int(DUR * SR)

def wav(clip):
    y, sr = sf.read(f'{ROOT}/amb/{clip}.wav'); assert sr == SR
    return y
def rms_db(y): return 20 * np.log10(np.sqrt((y ** 2).mean()) + 1e-9)

# ---- music ----
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{ROOT}/drive/audio/7001672f5d184c6ba650e6e09e0641b3.mp4', '-vn',
                '-ac', '2', '-ar', str(SR), f'{ROOT}/out/music.wav'], check=True)
music, _ = sf.read(f'{ROOT}/out/music.wav')
M = np.zeros((n, 2)); M[:min(n, len(music))] = music[:n]

# ---- diegetic ambience: each shot's own sound, loudness matched, 40 ms crossfades ----
A = np.zeros((n, 2)); XF = int(0.04 * SR)
regions = []
for s in SEGS:
    if s['name'].startswith('flash'): continue
    regions.append((s['clip'], s['a'], s['b'], s['s0']))
regions.append(('IMG_6220', 0.767, 1.667, 3.0))       # one continuous traffic bed under the flash burst
for clip, a, b, s0 in regions:
    y = wav(clip); g = 10 ** ((-26 - rms_db(y)) / 20); g = min(g, 4.0)
    i0 = int(a * SR) - XF; i1 = int(b * SR) + XF; L = i1 - i0
    j0 = int(s0 * SR) - XF
    seg = np.zeros((L, 2))
    src = y[max(0, j0): max(0, j0) + L]
    if len(src) < L:          # loop the tail if the clip is short (e.g. slow-motion segments)
        src = np.concatenate([src, y[:L - len(src)]]) if len(y) else src
    seg[:len(src)] = src[:L] * g
    env = np.ones(L); r = np.linspace(0, 1, 2 * XF)
    env[:2 * XF] = np.sin(r * np.pi / 2) ** 2; env[-2 * XF:] = np.cos(r * np.pi / 2) ** 2
    seg *= env[:, None]
    lo, hi = max(0, i0), min(n, i1)
    A[lo:hi] += seg[lo - i0: hi - i0]

# ambience level automation: low under vocals, swells in the musical silences, fades with the end card
t = np.arange(n) / SR
def bump(t, a, b, ramp):
    up = np.clip((t - (a - ramp)) / ramp, 0, 1); dn = np.clip(((b + ramp) - t) / ramp, 0, 1)
    return np.minimum(up, dn)
lvl_db = -9.0 + 8.0 * bump(t, 9.60, 10.25, 0.18) + 9.0 * bump(t, 20.10, 20.48, 0.08)
lvl_db += 4.0 * bump(t, 0.0, 0.70, 0.1)          # let the street be heard a touch in the hook
tail = np.clip((t - 21.0) / 1.6, 0, 1); lvl_db -= 30 * tail ** 1.5
A *= (10 ** (lvl_db / 20))[:, None]

# ---- whooshes (filtered noise, very low) ----
def whoosh(center, dur, peak_db, lo=300, hi=7000, seed=1):
    rng = np.random.default_rng(seed); L = int(dur * SR)
    w = rng.normal(0, 1, (L, 2))
    # spectral band-limit
    Fw = np.fft.rfft(w, axis=0); f = np.fft.rfftfreq(L, 1 / SR)
    band = ((f > lo) & (f < hi)).astype(float) / np.sqrt(np.maximum(f, 50) / 300)   # pinkish
    w = np.fft.irfft(Fw * band[:, None], n=L, axis=0); w /= np.abs(w).max()
    x = np.linspace(0, 1, L); env = np.where(x < 0.6, (x / 0.6) ** 2.2, ((1 - x) / 0.4) ** 1.4)
    w *= env[:, None] * 10 ** (peak_db / 20)
    i0 = int((center - dur * 0.6) * SR); W = np.zeros((n, 2)); W[i0:i0 + L] = w[:n - i0]; return W
FX = whoosh(4.25, 0.55, -24) + whoosh(10.42, 0.45, -30, 500, 9000, 2)

mix = M * 1.0 + A + FX
sf.write(f'{ROOT}/out/mix_pre.wav', mix.astype(np.float32), SR, subtype='FLOAT')
# loudness: -14 LUFS integrated, -1 dBTP (Instagram)
import json, re
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', f'{ROOT}/out/mix_pre.wav', '-af',
                    'loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
m = json.loads(r[r.rindex('{'):r.rindex('}') + 1]); print('measured', m['input_i'], m['input_tp'], m['input_lra'])
af = (f"loudnorm=I=-14:TP=-1.0:LRA=11:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
      f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']},aresample=48000")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{ROOT}/out/mix_pre.wav', '-af', af, '-ar', '48000', OUT], check=True)
print('ok', OUT)
