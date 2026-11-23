"""Procedurally synthesised, subtle cinematic sound effects (22.05 kHz mono WAV)."""
import wave
import numpy as np

SR = 22050
rng = np.random.default_rng(11)


def t_axis(sec):
    return np.arange(int(sec * SR)) / SR


def lowpass(x, cutoff):
    """FFT brick-ish low-pass with a soft knee."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def bandpass(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= (1 / (1 + (lo / np.maximum(f, 1)) ** 4)) * (1 / (1 + (f / hi) ** 4))
    return np.fft.irfft(X, len(x))


def norm(x, peak):
    m = np.max(np.abs(x)) or 1
    return x / m * peak


def fade(x, a=0.005, b=0.03):
    n = len(x)
    ia, ib = int(a * SR), int(b * SR)
    if ia:
        x[:ia] *= np.linspace(0, 1, ia)
    if ib:
        x[-ib:] *= np.linspace(1, 0, ib)
    return x


def write(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


# ------------------------------------------------------------------ primitives
def whoosh(sec=1.4, peak_at=0.55):
    t = t_axis(sec)
    n = rng.normal(0, 1, len(t))
    # sweep: blend a dark and a bright band following the envelope
    dark, bright = bandpass(n, 120, 900), bandpass(n, 700, 4200)
    env = np.exp(-((t / sec - peak_at) ** 2) / 0.045)
    sweep = np.clip(t / (sec * peak_at), 0, 1)
    x = dark * env * (1 - 0.6 * sweep) + bright * env * sweep * 0.55
    x += np.sin(2 * np.pi * (48 + 20 * env) * t) * env * 0.5   # sub swell
    return fade(norm(x, 0.32), 0.02, 0.2)


def boom(sec=2.6):
    t = t_axis(sec)
    f = 38 + 34 * np.exp(-t * 6)
    phase = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(phase) * np.exp(-t * 1.6)
    x += lowpass(rng.normal(0, 1, len(t)), 180) * np.exp(-t * 9) * 0.9
    shimmer = sum(np.sin(2 * np.pi * fr * t) * a for fr, a in [(880, 1), (1318.5, .6), (1760, .35)])
    x += shimmer * np.exp(-t * 2.2) * 0.05 * np.clip(t / 0.08, 0, 1)
    return fade(norm(x, 0.55), 0.003, 0.3)


def click(sec=0.035, freq=2600, amp=1.0):
    t = t_axis(sec)
    x = np.sin(2 * np.pi * freq * t) * np.exp(-t * 260)
    x += bandpass(rng.normal(0, 1, len(t)), 2000, 7000) * np.exp(-t * 500) * 0.6
    return x * amp


def chime(sec=0.9):
    t = t_axis(sec)
    x = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(1568, 1), (2093, .55), (3136, .2)])
    return x * np.exp(-t * 5.5) * np.clip(t / 0.004, 0, 1)


def clack(sec=0.28):
    t = t_axis(sec)
    x = sum(np.sin(2 * np.pi * f * t) * a * np.exp(-t * d) for f, a, d in [(523, .5, 22), (1410, .7, 30), (2390, .45, 40), (3710, .25, 55)])
    x += lowpass(rng.normal(0, 1, len(t)), 300) * np.exp(-t * 60) * 0.8
    return x


def ping(sec=0.9):
    t = t_axis(sec)
    x = np.sin(2 * np.pi * 1320 * t) * np.exp(-t * 7) + np.sin(2 * np.pi * 1980 * t) * np.exp(-t * 11) * 0.3
    x *= np.clip(t / 0.003, 0, 1)
    d = int(0.17 * SR)
    y = x.copy()
    y[d:] += x[:-d] * 0.28
    return y


def servo(sec=1.3):
    t = t_axis(sec)
    prog = 1 - (1 - np.clip(t / (sec * 0.92), 0, 1)) ** 3          # matches decelerating needle
    f = 90 + 150 * prog
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph))
    x = lowpass(x, 900) * (np.clip(t / 0.06, 0, 1) * np.clip((sec - t) / 0.25, 0, 1)) * 0.5
    return x


def mix(total_sec, parts):
    """parts: list of (start_sec, signal, gain)"""
    out = np.zeros(int(total_sec * SR) + 1)
    for st, sig, g in parts:
        i = int(st * SR)
        j = min(len(out), i + len(sig))
        out[i:j] += sig[: j - i] * g
    return out


# ------------------------------------------------------------------ organic palette (matcha ritual)
def air(sec=1.5):
    """soft breath of air — a camera drift, not a jet"""
    t = t_axis(sec)
    n = rng.normal(0, 1, len(t))
    x = bandpass(n, 300, 2600) * np.exp(-((t / sec - 0.5) ** 2) / 0.06)
    return fade(norm(x, 0.22), 0.05, 0.3)


def bowl(sec=2.6, f0=233.0):
    """warm ceramic tea-bowl resonance (inharmonic partials, slow decay)"""
    t = t_axis(sec)
    x = sum(np.sin(2 * np.pi * f0 * r * t + p) * a * np.exp(-t * d)
            for r, a, d, p in [(1, 1, 1.4, 0), (2.71, .45, 2.2, .3), (5.18, .18, 3.5, .7), (8.4, .06, 5, 1.1)])
    x *= np.clip(t / 0.012, 0, 1) * (1 + 0.05 * np.sin(2 * np.pi * 3.1 * t))
    x += bandpass(rng.normal(0, 1, len(t)), 1500, 6000) * np.exp(-t * 40) * 0.15   # felt-mallet contact
    return fade(norm(x, 0.42), 0.002, 0.4)


def drop(sec=0.9):
    """water droplet: fast upward chirp + small ripple tail"""
    t = t_axis(sec)
    f = 700 + 1100 * (1 - np.exp(-t * 90))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 28)
    x += np.sin(2 * np.pi * 1650 * t) * np.exp(-t * 9) * 0.18 * np.clip((t - 0.03) / 0.02, 0, 1)
    return fade(norm(x, 0.35), 0.001, 0.2)


def knock(sec=0.25, f0=520):
    """hollow bamboo knock"""
    t = t_axis(sec)
    x = np.sin(2 * np.pi * f0 * t) * np.exp(-t * 34) + np.sin(2 * np.pi * f0 * 2.4 * t) * np.exp(-t * 60) * 0.35
    x += bandpass(rng.normal(0, 1, len(t)), 400, 2500) * np.exp(-t * 120) * 0.5
    return x


def tick(sec=0.04, amp=1.0, f0=1250):
    """soft wooden tick"""
    t = t_axis(sec)
    x = np.sin(2 * np.pi * f0 * t) * np.exp(-t * 180) + bandpass(rng.normal(0, 1, len(t)), 900, 4000) * np.exp(-t * 400) * 0.4
    return x * amp


def tink(sec=1.1):
    """small ceramic tink on arrival"""
    t = t_axis(sec)
    x = sum(np.sin(2 * np.pi * f * t) * a * np.exp(-t * d) for f, a, d in [(1760, 1, 5), (2370, .5, 7), (4510, .15, 11)])
    return x * np.clip(t / 0.003, 0, 1)


def whisk(sec=1.3):
    """chasen whisking: rapid brushy strokes in the bowl"""
    t = t_axis(sec)
    n = bandpass(rng.normal(0, 1, len(t)), 1800, 7500)
    strokes = (0.5 + 0.5 * np.sin(2 * np.pi * 9.5 * t)) ** 3
    env = np.clip(t / 0.15, 0, 1) * np.clip((sec - t) / 0.4, 0, 1)
    return fade(norm(n * strokes * env, 0.2), 0.01, 0.2)


# ------------------------------------------------------------------ compositions used by the deck
# ------------------------------------------------------------------ compositions used by the deck
def make(kind, p, path):
    if kind == "air":
        x = air()
    elif kind == "bowl":
        x = bowl()
    elif kind == "drop":
        x = drop()
    elif kind == "knock":
        x = norm(knock(), 0.32)
    elif kind == "whisk":
        x = whisk()
    elif kind == "roll":                       # count-up: soft wooden ticks per frame + ceramic tink on the final value
        step, n = p["step"] / 1000, p["n"]
        parts = [(i * step, tick(amp=0.5 + 0.5 * i / n, f0=1150 + 15 * i), 1) for i in range(n)]
        parts.append((n * step, tink(), 0.5))
        x = norm(mix(n * step + 1.2, parts), 0.34)
    elif kind == "assemble":                   # digits settling: bamboo knocks, then tink
        parts = [(ms / 1000, knock(f0=480 + 25 * i), 1) for i, ms in enumerate(p["times"])]
        parts.append((p["final"] / 1000, tink(), 0.6))
        x = norm(mix(p["final"] / 1000 + 1.2, parts), 0.36)
    else:
        raise ValueError(kind)
    write(path, fade(x, 0.001, 0.02))
