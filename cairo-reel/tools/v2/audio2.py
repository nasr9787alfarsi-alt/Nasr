"""Sound design for CAIRO CLOCKWORK. All events are derived from edl2 so sound and picture cannot drift."""
import sys, os, json, subprocess, numpy as np, soundfile as sf, scipy.signal as sg
sys.path.insert(0, os.path.dirname(__file__))
from edl2 import *
from scipy.interpolate import PchipInterpolator
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000; n = int(DUR * SR); T = np.arange(n) / SR
db = lambda x: 10 ** (x / 20)
rng = np.random.default_rng(3)

def place(buf, x, t, gain_db=0.0):
    i = int(round(t * SR))
    if i >= n: return
    if i < 0: x = x[-i:]; i = 0
    L = min(len(x), n - i); buf[i:i + L] += x[:L] * db(gain_db)

# ---------------- mechanical palette (from the BOOM MECHANICALS teaser) ----------------
mech, _ = sf.read(f'{ROOT}/ana2/mech.wav')
hp = lambda f: sg.butter(4, f, 'hp', fs=SR, output='sos')
def cut(t0, dur, hpf=180, fade=0.6, pre=0.004):
    a = int((t0 - pre) * SR); x = mech[a:a + int(dur * SR)].copy()
    if hpf: x = sg.sosfiltfilt(hp(hpf), x, axis=0)
    L = len(x); env = np.ones(L)
    k = int(L * fade); env[L - k:] = np.linspace(1, 0, k) ** 2          # tail fade
    env[:int(0.002 * SR)] = np.linspace(0, 1, int(0.002 * SR))
    x = x * env[:, None]; return x / (np.abs(x).max() + 1e-9)
TICKS = [cut(t, 0.10) for t in (2.5242, 2.9583, 3.4520, 3.9208)]
TYPE = [cut(t, 0.050, 250, 0.5) for t in (4.3447, 4.4019, 4.5262, 4.5710, 4.6257, 4.6984, 4.7306, 4.7927)]
RATCH = [cut(t, 0.034, 300, 0.5) for t in (18.6645, 18.7156, 18.7549, 18.8162, 18.8632, 18.8953, 18.9276,
                                            18.9740, 19.0153, 19.0547, 19.0883, 19.1220, 19.1605, 19.2180)]
POCKET = [cut(t, 0.045, 250, 0.5) for t in (12.0999, 12.1366, 12.2385, 12.2927, 12.3428, 12.4040, 12.4355, 12.5384)]
KNOB = [cut(t, 0.06, 200, 0.5) for t in (26.6342, 26.7915, 26.9767, 27.0545, 27.2104, 27.3464)]
LATCH = cut(24.4774, 0.28, 90, 0.7)
CLUNK = cut(0.1098, 0.45, 35, 0.7)

FX = np.zeros((n, 2))
place(FX, CLUNK, 0.0, -3)                                             # the machine starts
for i in range(10): place(FX, TICKS[i % 4], BURST_T0 + i * 3 * F, -9 + rng.uniform(-1, 1))  # tick per flash cut
ev = json.load(open(f'{ROOT}/out2/events.json'))
for i, t in enumerate(ev['type']): place(FX, TYPE[i % len(TYPE)], t, -10 + rng.uniform(-2, 1.5))   # title keys

def whoosh(t_peak, rise, fall, peak_db, lo=250, hi=7000, seed=1):
    r = np.random.default_rng(seed); L = int((rise + fall) * SR)
    w = r.normal(0, 1, (L, 2)); Fw = np.fft.rfft(w, axis=0); f = np.fft.rfftfreq(L, 1 / SR)
    band = ((f > lo) & (f < hi)) / np.sqrt(np.maximum(f, 50) / 300)
    w = np.fft.irfft(Fw * band[:, None], n=L, axis=0); w /= np.abs(w).max()
    x = np.arange(L) / SR; env = np.where(x < rise, (x / rise) ** 2.5, np.exp(-(x - rise) / (fall / 3)))
    out = np.zeros((n, 2)); i0 = int((t_peak - rise) * SR); out[i0:i0 + L] = (w * env[:, None])[:n - i0]
    return out * db(peak_db)
FX += whoosh(LEAK[1], 0.22, 0.30, -18)                                # light-leak burn into the 4.99 accent
FX += whoosh(ARCH[1], 0.60, 0.25, -24, 150, 5000, 2)                  # push into the doorway
place(FX, LATCH, ARCH[1] - 0.004, -5)                                 # ...the door unlatches on the B section
for k, t in enumerate(STUTTER_STEPS): place(FX, KNOB[k % len(KNOB)], t, -8)   # each held frame clicks
# wind-up during the freeze: ratchet accelerating
t = WIND[0]; gap = 0.050; k = 0
while t < WIND[1]:
    place(FX, RATCH[k % len(RATCH)], t, -10 + 4 * (t - WIND[0]) / (WIND[1] - WIND[0])); k += 1
    t += gap; gap = max(0.020, gap * 0.90)
place(FX, CLUNK, HIT - 0.003, -6)                                     # release
# wind-down: click rate follows the speed of the decelerating reverse pan
fin = [s for s in SEGS if s['name'] == 'final'][0]; keys = fin['keys']
P = PchipInterpolator([k_[0] for k_ in keys], [k_[1] for k_ in keys])
phase = 0.0; tt = WINDDOWN_CLICKS[0]; k = 0
while tt < WINDDOWN_CLICKS[1]:
    speed = abs(float(P(tt + 0.005)) - float(P(tt))) / 0.005
    phase += speed * 9.0 * 0.005
    if phase >= 1: phase -= 1; place(FX, POCKET[k % len(POCKET)], tt, -11); k += 1
    tt += 0.005
place(FX, LATCH, END_FREEZE - 0.004, -4)                              # the clock stops on the opening frame

# ---------------- music with a tape-stop wind-down ----------------
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{ROOT}/drive2/audio/new.mp4', '-vn', '-ac', '2', '-ar', str(SR),
                f'{ROOT}/out2/song48.wav'], check=True)
song, _ = sf.read(f'{ROOT}/out2/song48.wav')
M = np.zeros((n, 2)); M[:min(n, len(song))] = song[:n]
a, b = TAPESTOP; ia, ib = int(a * SR), int(b * SR)
x = (np.arange(ib - ia)) / (ib - ia); rate = (1 - x) ** 1.3
tau = a + np.cumsum(rate) / SR
for c in range(2): M[ia:ib, c] = np.interp(tau, np.arange(len(song)) / SR, song[:, c])
M[ib:] = 0
lp = np.ones(ib - ia); M[ia:ib] *= (1 - x[:, None] ** 3)                # fades as it stops

# ---------------- city: every shot's own sync sound ----------------
def amb(c):
    y, sr = sf.read(f'{ROOT}/amb/{c}.wav'); return y
def rms_db(y): return 20 * np.log10(np.sqrt((y ** 2).mean()) + 1e-9)
A = np.zeros((n, 2)); XF = int(0.035 * SR)
regions = [(s['clip'], s['a'], s['b'], (s['keys'][0][1] if s['keys'] else s['s0']), s['name']) for s in SEGS if not s['name'].startswith('flash')]
regions.append(('IMG_6220', BURST_T0, BURST_T0 + 0.9, 3.0, 'burstbed'))
for clip, a_, b_, s0, name in regions:
    y = amb(clip); g = db(-26 - rms_db(y)); g = min(g, 4.0)
    i0, i1 = int(a_ * SR) - XF, int(b_ * SR) + XF; L = i1 - i0; j0 = max(0, int(s0 * SR) - XF)
    src = y[j0:j0 + L]
    if len(src) < L: src = np.concatenate([src, y[:L - len(src)]])
    if name == 'stutter':      # audio stutters with the picture: each held frame repeats its own 100 ms
        step = int(3 * SR / FPS); base = int(s0 * SR); src = np.zeros((L, 2))
        for k in range(0, L, step):
            g_ = int(0.050 * SR); ch = y[base + k: base + k + g_]; ch = ch[:max(0, min(len(ch), L - k))]
            src[k:k + len(ch)] = ch * np.hanning(len(ch))[:, None] ** 0.4     # gated: city sound chops with the frames
    if name == 'freeze': src = src * 0                                  # time stops: the city goes silent
    seg_ = src[:L] * g; env = np.ones(L); r = np.linspace(0, 1, 2 * XF)
    env[:2 * XF] = np.sin(r * np.pi / 2) ** 2; env[-2 * XF:] = np.cos(r * np.pi / 2) ** 2
    lo, hi = max(0, i0), min(n, i1); A[lo:hi] += (seg_ * env[:, None])[lo - i0:hi - i0]

def bump(a_, b_, ramp):
    return np.minimum(np.clip((T - (a_ - ramp)) / ramp, 0, 1), np.clip(((b_ + ramp) - T) / ramp, 0, 1))
lvl = np.full(n, -7.0)
lvl += -5 * bump(0.0, 4.99, 0.05)                    # opening: let the mechanics speak
lvl += 7 * bump(9.00, 9.31, 0.10) + 7 * bump(14.06, 14.69, 0.10) + 7 * bump(22.88, 23.48, 0.12)
lvl += 6 * bump(27.52, 27.88, 0.10) + 6 * bump(37.11, 37.52, 0.10) + 6 * bump(41.20, 41.55, 0.10)
lvl += 3 * bump(14.56, 22.0, 0.3)                    # vehicles sequence: traffic is part of the story
for tp in (14.56, 16.95, 19.56, 22.10, 34.10):       # passing vehicles: their own sound swells as they pass
    lvl += 5 * np.exp(-((T - tp) / 0.25) ** 2)
lvl += -5 * bump(37.52, 41.20, 0.3)                  # climax: the music takes control
lvl += -30 * np.clip((T - (END_FREEZE + 0.05)) / 0.35, 0, 1)
A *= db(lvl)[:, None]

mix = M + A + FX
sf.write(f'{ROOT}/out2/mix_pre.wav', mix.astype(np.float32), SR, subtype='FLOAT')
sf.write(f'{ROOT}/out2/stem_music.wav', M.astype(np.float32), SR, subtype='FLOAT')
sf.write(f'{ROOT}/out2/stem_amb.wav', A.astype(np.float32), SR, subtype='FLOAT')
sf.write(f'{ROOT}/out2/stem_fx.wav', FX.astype(np.float32), SR, subtype='FLOAT')
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', f'{ROOT}/out2/mix_pre.wav', '-af',
                    'loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
m = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
af = (f"loudnorm=I=-14:TP=-1.0:LRA=11:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
      f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']},aresample=48000")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{ROOT}/out2/mix_pre.wav', '-af', af, '-ar', '48000',
                f'{ROOT}/out2/mix.wav'], check=True)
print('measured', m['input_i'], m['input_tp'], '-> out2/mix.wav')
