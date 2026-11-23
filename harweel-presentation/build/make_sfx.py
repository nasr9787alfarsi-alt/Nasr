"""Synthesise the subtle, documentary-style sound effects for the Harweel deck.

All sounds are original (procedurally generated), royalty-free, mono 16-bit WAV
(the format PowerPoint embeds for animation sounds). Levels are set by RMS so the
effects sit well under a live voice; every file has smooth fades (no clicks).
Usage: python3 make_sfx.py <out_dir>
"""
import os
import sys
import wave

import numpy as np
from scipy import signal

SR = 32000
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(42)


def t_(d):
    return np.arange(int(d * SR)) / SR


def noise(d):
    return rng.standard_normal(int(d * SR))


def brown(d):
    x = np.cumsum(noise(d))
    x = signal.sosfilt(signal.butter(1, 20, "hp", fs=SR, output="sos"), x)
    return x / (np.abs(x).max() + 1e-9)


def bp(x, lo, hi, order=4):
    return signal.sosfilt(signal.butter(order, [lo, hi], "bandpass", fs=SR, output="sos"), x)


def lp(x, f, order=4):
    return signal.sosfilt(signal.butter(order, f, "lowpass", fs=SR, output="sos"), x)


def hp(x, f, order=4):
    return signal.sosfilt(signal.butter(order, f, "highpass", fs=SR, output="sos"), x)


def env(n, a=0.02, r=0.3, shape=2.0):
    """attack/release envelope (seconds)."""
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na) ** shape
    e[-nr:] *= np.linspace(1, 0, nr) ** shape
    return e


def sweep_filter(x, f0, f1, q=1.2, curve=1.0):
    """time-varying band-pass via STFT mask (centre moves f0 -> f1)."""
    f, tt, Z = signal.stft(x, SR, nperseg=1024, noverlap=768)
    pos = (np.linspace(0, 1, Z.shape[1]) ** curve)
    fc = f0 * (f1 / f0) ** pos
    bw = fc / q
    mask = np.exp(-0.5 * ((f[:, None] - fc[None, :]) / bw[None, :]) ** 2)
    _, y = signal.istft(Z * mask, SR, nperseg=1024, noverlap=768)
    return y[: len(x)]


def reverb(x, tail=0.6, mix=0.18, tone=3500):
    n = int(tail * SR)
    ir = lp(noise(tail), tone, 2) * np.exp(-np.linspace(0, 7, n))
    wet = signal.fftconvolve(x, ir)
    wet = np.concatenate([wet, np.zeros(len(x) + n - len(wet))])[: len(x) + n]
    dry = np.concatenate([x, np.zeros(n)])
    wet *= np.sqrt(np.mean(dry ** 2) / (np.mean(wet ** 2) + 1e-12))
    return (1 - mix) * dry + mix * wet


def bubbles(d, count, f_lo, f_hi, dur=(0.015, 0.06), rise=1.6):
    """physically-inspired bubble synthesis: short rising damped sines (Minnaert-style)."""
    n = int(d * SR)
    y = np.zeros(n)
    for _ in range(count):
        st = int(rng.uniform(0, d * 0.85) * SR)
        bd = rng.uniform(*dur)
        m = int(bd * SR)
        if st + m >= n:
            continue
        tt = np.arange(m) / SR
        f0 = rng.uniform(f_lo, f_hi)
        f = f0 * (1 + (rise - 1) * tt / bd)
        ph = 2 * np.pi * np.cumsum(f) / SR
        y[st:st + m] += np.sin(ph) * np.exp(-tt / (bd / 4)) * rng.uniform(0.3, 1.0)
    return y


def click(m=0.006, f=2600, decay=0.0012):
    tt = np.arange(int(m * SR)) / SR
    return np.sin(2 * np.pi * f * tt) * np.exp(-tt / decay) + 0.4 * rng.standard_normal(len(tt)) * np.exp(-tt / 0.0004)


# hard length caps so no sound ever overlaps the next cue on its slide (seconds)
MAXLEN = {"rumble_build": 1.75, "deep_time_swell": 1.45, "stone_settle": 1.4, "lens_focus": 0.9,
          "gas_pipe_flow": 1.2, "reservoir_sweep": 1.5, "sonar_ping": 1.2, "time_sweep": 1.6,
          "dissolve_fizz": 2.0, "plant_startup": 1.9, "zoom_in_whoosh": 1.2, "spark_shimmer": 1.4}


def finish(name, x, rms_db, peak_db=-6.0, fade_in=0.005, fade_out=0.06):
    if name in MAXLEN and len(x) > MAXLEN[name] * SR:
        x = x[: int(MAXLEN[name] * SR)]
        fade_out = 0.3
    x = x - np.mean(x)
    x = x * env(len(x), fade_in, fade_out, 1.0)
    rms = np.sqrt(np.mean(x ** 2)) + 1e-12
    x = x * (10 ** (rms_db / 20) / rms)
    pk = np.abs(x).max()
    lim = 10 ** (peak_db / 20)
    if pk > lim:
        x = x * (lim / pk)
    pcm = np.clip(x * 32767, -32768, 32767).astype("<i2")
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return x


SFX = {}

# ---- geology: deep earth rumble as layers build (slides 1 & 3) ---------------
d = 2.0
r = lp(brown(d), 180) * 1.0 + bp(noise(d), 60, 260) * 0.35
grit = np.zeros(int(d * SR))
for _ in range(60):  # sparse rock grit / settling crackle
    p = int(rng.uniform(0.1, 1.7) * SR)
    c = bp(click(0.01, rng.uniform(300, 900), 0.003), 150, 1500)
    grit[p:p + len(c)] += c * rng.uniform(0.05, 0.25)
r = r * env(len(r), 0.35, 0.9, 1.6) + grit * env(len(r), 0.2, 0.8)
SFX["rumble_build"] = (reverb(r, 0.8, 0.2, 1200), -24)

# ---- well descending: soft mechanical drive (slide 1) ------------------------
d = 0.8
tt = t_(d)
f = 140 - 50 * tt / d
ph = 2 * np.pi * np.cumsum(f) / SR
m = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3.02 * ph)) * (1 + 0.3 * np.sin(2 * np.pi * 23 * tt))
m = lp(m, 900) + 0.15 * bp(noise(d), 300, 1800)
SFX["drill_descend"] = (reverb(m * env(len(m), 0.12, 0.35), 0.5, 0.15), -31)

# ---- location ping (slide 2): soft sonar-like tone -------------------------------
d = 0.9
tt = t_(d)
p = (np.sin(2 * np.pi * 740 * tt) + 0.3 * np.sin(2 * np.pi * 1480 * tt)) * np.exp(-tt / 0.18)
SFX["sonar_ping"] = (reverb(p * env(len(p), 0.008, 0.2), 0.9, 0.35, 5000), -32)

# ---- deep time: soft low swell (slide 4) -----------------------------------------
d = 1.3
tt = t_(d)
s = np.sin(2 * np.pi * 55 * tt) * 0.8 + np.sin(2 * np.pi * 82.5 * tt) * 0.3
s += sweep_filter(noise(d), 200, 900, 2.0) * 0.6
SFX["deep_time_swell"] = (reverb(s * env(len(s), 0.25, 0.8, 1.5), 1.0, 0.25, 2500), -27)

# ---- geological time bar sweep (slide 4): airy whoosh left->right -----------------
d = 1.4
w = sweep_filter(noise(d), 350, 2200, 2.5, 0.8)
SFX["time_sweep"] = (reverb(w * env(len(w), 0.4, 0.6, 1.5), 0.6, 0.15), -31)

# ---- stone settle (slide 5): tiles rising, gentle stone grind ---------------------
d = 1.1
g = bp(noise(d), 180, 900) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 3.6 * t_(d))))
for k in range(4):  # four tiles -> four soft settles, synced to 0/250/500/750 ms
    pos = int((0.12 + 0.25 * k) * SR)
    c = lp(noise(0.08), 400) * np.exp(-np.arange(int(0.08 * SR)) / SR / 0.02)
    g[pos:pos + len(c)] += c * 1.6
SFX["stone_settle"] = (reverb(g * env(len(g), 0.05, 0.4), 0.5, 0.15, 1500), -30)

# ---- data / number appears: soft interface blip (slides 5, 14) --------------------
d = 0.35
tt = t_(d)
b = np.sin(2 * np.pi * 1180 * tt) * np.exp(-tt / 0.05)
b[int(0.06 * SR):] += np.sin(2 * np.pi * 1570 * tt[: len(tt) - int(0.06 * SR)]) * np.exp(
    -tt[: len(tt) - int(0.06 * SR)] / 0.06) * 0.8
SFX["data_blip"] = (reverb(b, 0.5, 0.25, 6000), -33)

# ---- positive data (slide 12, >30%) ----------------------------------------------
d = 0.45
tt = t_(d)
u = np.zeros(len(tt))
for k, fq in enumerate((880, 1175, 1480)):
    o = int(k * 0.07 * SR)
    seg = tt[: len(tt) - o]
    u[o:] += np.sin(2 * np.pi * fq * seg) * np.exp(-seg / 0.07) * (0.7 + 0.15 * k)
SFX["data_blip_up"] = (reverb(u, 0.6, 0.25, 6000), -33)

# ---- microscope lens focus (slide 6): two soft clicks + servo ---------------------
d = 0.6
lf = 0.12 * bp(noise(d), 1500, 5000) * env(int(d * SR), 0.1, 0.2)
tt = t_(d)
lf += 0.25 * lp(np.sin(2 * np.pi * (300 + 220 * tt / d) * tt), 2000) * env(len(tt), 0.05, 0.15)
for pos in (0.02, 0.48):
    c = click(0.01, 3100, 0.0015)
    i = int(pos * SR)
    lf[i:i + len(c)] += c * 0.8
SFX["lens_focus"] = (reverb(lf, 0.4, 0.15), -32)

# ---- oil trickling through pores (slides 6, 11) -----------------------------------
d = 1.8
o = bubbles(d, 70, 280, 900, (0.02, 0.07), 1.5) + 0.15 * lp(brown(d), 500)
SFX["oil_trickle"] = (reverb(o * env(len(o), 0.3, 0.6, 1.2), 0.5, 0.2, 3000), -31)

# ---- gauge needle sweep (slide 7): mechanical ticks following the needle's ease ---
d = 2.6
y = np.zeros(int(d * SR))
# needle uses decel: fast start, slowing down; place ticks along eased progress
prog = lambda x: 1 - (1 - x) ** 2.2  # noqa: E731
ticks = 30
for k in range(ticks):
    # invert eased progress to find time of each tick
    target = (k + 1) / ticks
    lo_, hi_ = 0.0, 1.0
    for _ in range(30):
        mid = (lo_ + hi_) / 2
        lo_, hi_ = (mid, hi_) if prog(mid) < target else (lo_, mid)
    i = int(lo_ * (d - 0.25) * SR)
    c = bp(click(0.012, rng.uniform(2300, 2700), 0.0018), 900, 7000)
    y[i:i + len(c)] += c * (0.55 + 0.1 * rng.standard_normal())
c = lp(click(0.05, 900, 0.01), 2500)  # final soft "settle" of the needle
i = int((d - 0.25) * SR)
y[i:i + len(c)] += c * 0.9
y += 0.04 * bp(noise(d), 2000, 8000) * env(len(y), 0.3, 0.8)  # faint pressure hiss
SFX["gauge_ticks"] = (reverb(y, 0.35, 0.12, 6000), -32)

# ---- sour gas hiss (slide 8) -------------------------------------------------------
d = 1.2
h = hp(noise(d), 2500) * (1 + 0.25 * np.sin(2 * np.pi * 7 * t_(d)))
SFX["gas_hiss"] = (reverb(h * env(len(h), 0.15, 0.75, 1.4), 0.4, 0.12), -36)

# ---- nine barrels dim (slide 9): soft descending power-down ------------------------
d = 0.9
tt = t_(d)
f = 220 * (0.5 ** (tt / d))
ph = 2 * np.pi * np.cumsum(f) / SR
pd = (np.sin(ph) + 0.35 * np.sin(2 * ph)) * np.exp(-tt / 0.45) + 0.1 * lp(noise(d), 600)
SFX["power_down"] = (reverb(pd * env(len(pd), 0.03, 0.3), 0.6, 0.2, 2000), -30)

# ---- gas flowing in a pipe (slides 10, 13) -----------------------------------------
d = 1.2
gp = bp(noise(d), 500, 2600) * (1 + 0.2 * np.sin(2 * np.pi * 5 * t_(d))) + 0.3 * lp(brown(d), 300)
SFX["gas_pipe_flow"] = (reverb(gp * env(len(gp), 0.35, 0.55, 1.5), 0.4, 0.12), -33)

# ---- gas front sweeping through the reservoir (slide 10): low slow whoosh ----------
d = 1.5
rs = sweep_filter(noise(d) + 2 * brown(d), 1100, 160, 1.6, 1.0)
SFX["reservoir_sweep"] = (reverb(rs * env(len(rs), 0.4, 0.7, 1.5), 0.8, 0.22, 1800), -29)

# ---- oil rising up the production well (slide 10): low gurgle -----------------------
d = 1.5
orr = bubbles(d, 45, 140, 420, (0.03, 0.09), 1.35) + 0.25 * lp(brown(d), 250)
SFX["oil_rise"] = (reverb(orr * env(len(orr), 0.25, 0.6, 1.3), 0.5, 0.18, 2500), -30)

# ---- Morph zoom into the rock (slide 11 transition) ---------------------------------
d = 0.9
z = sweep_filter(noise(d), 2400, 260, 1.8, 1.3)
SFX["zoom_in_whoosh"] = (reverb(z * env(len(z), 0.3, 0.45, 1.6), 0.7, 0.2), -31)

# ---- gas dissolving into oil (slide 11): fine fizz -----------------------------------
d = 1.8
fz = bubbles(d, 260, 1500, 4200, (0.004, 0.015), 1.2) + 0.08 * hp(noise(d), 4000)
SFX["dissolve_fizz"] = (reverb(fz * env(len(fz), 0.2, 1.0, 1.3), 0.4, 0.15, 7000), -36)

# ---- plant start-up (slide 13): low motor/compressor spin-up -------------------------
d = 1.5
tt = t_(d)
fm = 28 + 32 * (1 - np.exp(-tt / 0.5))
ph = 2 * np.pi * np.cumsum(fm) / SR
mo = np.sin(ph) + 0.6 * np.sin(2 * ph) + 0.4 * np.sin(3 * ph) + 0.25 * np.sin(4 * ph)
mo = lp(mo, 700) + 0.12 * bp(noise(d), 400, 2500) + 0.2 * np.sin(2 * np.pi * 100 * tt)
SFX["plant_startup"] = (reverb(mo * env(len(mo), 0.3, 0.6, 1.4), 0.6, 0.18, 2000), -28)

# ---- new pipeline drawn on the map (slide 14) -----------------------------------------
d = 1.4
pl = sweep_filter(noise(d), 300, 1600, 2.2, 0.9) + 0.2 * lp(brown(d), 300)
SFX["pipeline_sweep"] = (reverb(pl * env(len(pl), 0.35, 0.6, 1.5), 0.6, 0.15), -32)

# ---- spark along the journey (slide 15): soft airy shimmer -----------------------------
d = 1.0
tt = t_(d)
sh = sweep_filter(noise(d), 2500, 6000, 3.0) * 0.6
for fq in (1760, 2217, 2637):
    sh += 0.12 * np.sin(2 * np.pi * fq * tt) * np.exp(-tt / 0.4)
SFX["spark_shimmer"] = (reverb(sh * env(len(sh), 0.15, 0.6, 1.4), 1.0, 0.3, 8000), -35)

for name, (x, db) in SFX.items():
    y = finish(name, x, db)
    pk = 20 * np.log10(np.abs(y).max())
    rms = 20 * np.log10(np.sqrt(np.mean(y ** 2)))
    print(f"{name:18s} {len(y) / SR:5.2f}s  rms {rms:6.1f} dBFS  peak {pk:6.1f} dBFS")
