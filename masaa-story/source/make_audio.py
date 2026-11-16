#!/usr/bin/env python3
"""Audio master: the reflection (0-17.45s) untouched in timing, the abrupt source
cut softened with a fade, a quiet reverb bloom of the last phrase carrying into the
picture's fade-out, limited to -1 dBTP. Usage: make_audio.py <ref_audio.wav> <out.wav>"""
import sys, subprocess, numpy as np, wave
src, out = sys.argv[1], sys.argv[2]
SR, END, TOTAL = 48000, 17.45, 20.2
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-t", str(END), "-ar", str(SR), "-ac", "2",
                      "-f", "f32le", "-"], capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
n_tot = int(TOTAL * SR)
dry = np.zeros((n_tot, 2), np.float32); dry[:len(x)] = x
# soften the hard cut in the source: equal-power fade 16.95 -> 17.45 (voice ends ~16.9)
a, b = int(16.95 * SR), int(END * SR)
dry[a:b] *= np.cos(np.linspace(0, np.pi / 2, b - a))[:, None]
dry[b:] = 0
# reverb bloom: send of the final phrase «أو عنوان» (15.95-17.45) into a warm, decaying IR
rng = np.random.default_rng(3)
L = int(3.2 * SR); t = np.arange(L) / SR
ir = rng.standard_normal((L, 2)).astype(np.float32) * np.exp(-t / 0.75)[:, None]
ir[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))[:, None]
# darken the tail (one-pole lowpass ~3.5 kHz)
alpha = np.exp(-2 * np.pi * 3500 / SR)
for c in range(2):
    y = np.zeros(L, np.float32); acc = 0.0
    col = ir[:, c]
    for i in range(L):
        acc = (1 - alpha) * col[i] + alpha * acc; y[i] = acc
    ir[:, c] = y
ir /= np.sqrt((ir ** 2).sum(0, keepdims=True))
s0 = int(15.95 * SR)
send = np.zeros((n_tot, 2), np.float32); send[s0:b] = x[s0:b]
send[s0:s0 + 2400] *= np.linspace(0, 1, 2400)[:, None]
wet = np.zeros_like(send)
for c in range(2):
    wet[:, c] = np.fft.irfft(np.fft.rfft(send[:, c], 2 * n_tot) * np.fft.rfft(ir[:, c], 2 * n_tot))[:n_tot]
wet *= 0.32
mix = dry + wet
# fade everything to silence with the picture
f0, f1 = int(18.6 * SR), int(20.1 * SR)
mix[f0:f1] *= np.linspace(1, 0, f1 - f0)[:, None] ** 2; mix[f1:] = 0
mix *= 10 ** (0.8 / 20)
tmp = out + ".tmp.wav"
with wave.open(tmp, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af",
                "alimiter=limit=0.89:attack=1:release=60:level=false,aresample=192000,alimiter=limit=0.89:level=false,aresample=48000",
                "-c:a", "pcm_s16le", out], check=True)
import os; os.remove(tmp)
print("ok", out)
