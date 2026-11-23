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


# ------------------------------------------------------------------ compositions used by the deck
def make(kind, p, path):
    if kind == "whoosh":
        x = whoosh(p.get("sec", 1.4))
    elif kind == "boom":
        x = boom()
    elif kind == "roll":                       # count-up: soft ticks per frame + a lock chime on the final value
        step, n = p["step"] / 1000, p["n"]
        parts = [(i * step, click(amp=0.55 + 0.45 * i / n, freq=2400 + 40 * i), 1) for i in range(n)]
        parts.append((n * step, chime(), 0.55))
        parts.append((n * step, click(freq=3200), 0.8))
        x = norm(mix(n * step + 1.0, parts), 0.42)
    elif kind == "assemble":                   # digits landing: metallic clacks, then chime
        parts = [(ms / 1000, clack(), 1) for ms in p["times"]]
        parts.append((p["final"] / 1000, chime(), 0.7))
        x = norm(mix(p["final"] / 1000 + 1.0, parts), 0.45)
    elif kind == "servo":
        parts = [(0, servo(p["sec"]), 1), (p["sec"] - 0.05, clack(), 0.6)]
        x = norm(mix(p["sec"] + 0.35, parts), 0.4)
    elif kind == "ping":
        x = norm(ping(), 0.3)
    elif kind == "clack":
        x = norm(clack(), 0.38)
    else:
        raise ValueError(kind)
    write(path, fade(x, 0.001, 0.02))
