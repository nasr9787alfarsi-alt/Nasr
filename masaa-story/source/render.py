#!/usr/bin/env python3
"""
مساء — Instagram Story (1080x1920, 30 fps)

Frame-accurate compositor:
  * 10-bit iPhone HLG footage, denoised and decoded to scene-linear light, then
    per-clip correction and a filmic night grade (grade.py)
  * sub-pixel slow push-ins (Ken Burns) on the linear image (Lanczos)
  * "lights-first" luminance dissolves: bright points of the incoming shot arrive
    before its shadows, like city lights switching on
  * Arabic typography (typo.py): Gulzar Nastaliq + IBM Plex Sans Arabic Light,
    revealed word by word on the voice
Output video is piped as raw RGB into ffmpeg, which muxes the audio.

Usage: render.py <clips_dir> <fonts_dir> <audio_wav> <out.mp4> [--still t1,t2,...] [--notext]
"""
import os, sys, subprocess, math, argparse
import numpy as np
import cv2
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grade as G
import mcdenoise as MC
import typo as T

W, H, FPS = 1080, 1920, 30
DUR = 20.2
NF = int(round(DUR * FPS))

ap = argparse.ArgumentParser()
ap.add_argument("clips"); ap.add_argument("fonts"); ap.add_argument("audio"); ap.add_argument("out")
ap.add_argument("--still", default="")
ap.add_argument("--notext", action="store_true")
args = ap.parse_args()

# ---------------------------------------------------------------- shots (unchanged edit)
# clip, source in-point, timeline start, timeline end, speed, zoom a->b, focal point
SHOTS = [
    dict(c="IMG_5945", src=0.40, t0=0.00,  t1=2.40,  sp=1.00, z=(1.000, 1.035), f=(560, 900)),   # golden shoreline — وستعرف
    dict(c="IMG_5936", src=0.15, t0=2.00,  t1=4.65,  sp=1.00, z=(1.045, 1.010), f=(560, 980)),   # headlights pass — بعد رحيل العمر
    dict(c="IMG_5941", src=0.00, t0=4.35,  t1=7.42,  sp=0.88, z=(1.000, 1.045), f=(760, 640)),   # people on the curving path — تطارد
    dict(c="IMG_5944", src=1.30, t0=7.10,  t1=9.60,  sp=1.00, z=(1.040, 1.005), f=(700, 1000)),  # pink light on water — خيط دخان
    dict(c="IMG_5942", src=0.00, t0=9.05,  t1=13.20, sp=0.90, z=(1.000, 1.050), f=(820, 760)),   # towers & pink light across the river — فحبيبة قلبك
    dict(c="IMG_5937", src=5.40, t0=13.02, t1=14.66, sp=1.00, z=(1.020, 1.050), f=(560, 900)),   # the corniche — أرض
    dict(c="IMG_5945", src=2.78, t0=14.45, t1=16.08, sp=0.87, z=(1.060, 1.090), f=(420, 1000)),  # the opening shore returns — أو وطن
    dict(c="IMG_5935", src=0.40, t0=15.88, t1=DUR,   sp=1.00, z=(1.000, 1.060), f=(620, 900)),   # distant shore, fade — أو عنوان
]
FADE_IN = (0.0, 0.95)
FADE_OUT = (18.55, 20.15)
PREROLL = 8  # frames decoded before the in-point so the temporal denoiser is settled


DN_R = 2  # temporal radius of the motion-compensated denoiser (5-frame window)


class Reader:
    """decodes a shot as scene-linear frames and returns them motion-compensated denoised"""

    def __init__(self, s, start_frame=0):
        n = int(math.ceil((s["t1"] - s["t0"]) * FPS)) + 2 - start_frame
        pre = PREROLL / FPS * s["sp"]
        src0 = s["src"] + start_frame / FPS * s["sp"]
        ss = max(src0 - pre, 0.0)
        self.skip = int(round((src0 - ss) / s["sp"] * FPS))
        src_len = (n / FPS) * s["sp"] + (src0 - ss) + 0.2
        cmd = ["ffmpeg", "-v", "error", "-ss", f"{ss:.3f}", "-t", f"{src_len:.3f}",
               "-i", os.path.join(args.clips, s["c"] + ".MOV"),
               "-vf", G.decode_filter(s["c"], s["sp"], FPS), "-r", str(FPS),
               "-frames:v", str(n + self.skip), "-f", "rawvideo", "-"]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.raw = {}           # decoded frames by shot-frame index (window cache)
        self.next = start_frame - self.skip
        self.out = {}
        self.dn = MC.MCDenoiser(DN_R)
        self.eof = False

    def _decode_until(self, k):
        while self.next <= k and not self.eof:
            buf = self.p.stdout.read(W * H * 12)
            if len(buf) < W * H * 12:
                self.eof = True
                break
            self.raw[self.next] = G.planar_to_rgb(buf)
            self.next += 1

    def frame(self, k):
        if k in self.out:
            return self.out[k]
        self._decode_until(k + DN_R)
        last = max(i for i in self.raw if i <= k) if any(i <= k for i in self.raw) else min(self.raw)
        kk = min(k, last)
        win = [self.raw.get(i) for i in range(kk - DN_R, kk + DN_R + 1)]
        lin, _ = self.dn.denoise(win, DN_R)
        lin = MC.chroma_clean(lin)
        for i in [i for i in self.raw if i < kk - DN_R]:
            del self.raw[i]
        self.out = {k: lin}
        return lin

    def close(self):
        if self.p:
            self.p.kill(); self.p = None


def push(img, s, t):
    """sub-pixel slow push toward the focal point (linear: never stops across a cut)"""
    u = min(max((t - s["t0"]) / (s["t1"] - s["t0"]), 0), 1)
    z = s["z"][0] + (s["z"][1] - s["z"][0]) * u
    fx, fy = s["f"]
    M = np.array([[z, 0, fx - z * fx], [0, z, fy - z * fy]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)


def lights_first(p, lum, k=0.65):
    """weight of the incoming image: bright pixels arrive first"""
    a = np.clip(p * (1 + k) - k * (1 - lum), 0, 1)
    return a * a * (3 - 2 * a)


# ---------------------------------------------------------------- typography
F = T.Fonts(args.fonts)
DS, LS = 52, 29   # display (Gulzar) / light (Plex) sizes on the 1080-wide canvas


def disp(t, size=DS, color=T.IVORY):
    return T.Word(t, F.display, size, color, gap=1.55)


def light(t, size=LS, color=T.SOFT, a=0.92):
    return T.Word(t, F.light, size, color, alpha=a, gap=1.25)


STANZAS = [
    # «وستعرف» — alone in the dark water below the golden shore
    T.Reveal([T.Line([disp("وستعرف", 56)], 540, 1478)], ins=[0.58], outs=1.92, in_dur=1.0, out_dur=0.55),
    # «بعد / رحيل العمر» — under the overpass ceiling, clear of the lamp
    T.Reveal([T.Line([light("بعد")], 380, 418),
              T.Line([disp("رحيل"), disp("العمر")], 380, 488)],
             ins=[2.33, 2.80, 3.25], outs=4.08, out_dur=0.5),
    # «بأنك كنت / تطارد» — in the night sky the path leads into
    T.Reveal([T.Line([light("بأنك"), light("كنت")], 540, 380),
              T.Line([disp("تطارد", 58)], 540, 452)],
             ins=[4.70, 5.60, 6.12], outs=7.00, out_dur=0.42),
    # «خيطَ دخان» — champagne, the one emphasised image; it disperses like smoke
    T.Reveal([T.Line([disp("خيط", 50, T.CHAMPAGNE), disp("دخان", 64, T.CHAMPAGNE)], 540, 1462)],
             ins=[7.40, 7.82], outs=[8.45, 8.72], out_dur=1.05, style="smoke"),
    # «فحبيبة قلبك / ليس لها» — over the dark water of the river view
    T.Reveal([T.Line([disp("فحبيبة"), disp("قلبك")], 470, 1408),
              T.Line([light("ليس"), light("لها")], 470, 1468)],
             ins=[9.62, 10.55, 11.70, 12.12], outs=12.70, out_dur=0.45),
    # «أرض أو وطن أو عنوان» — one composed line in the night sky; the nouns in Nastaliq,
    # the small «أو» in the light voice, «عنوان» in champagne. They leave one by one.
    T.Reveal([T.Line([disp("أرض"), light("أو"), disp("وطن"), light("أو"), disp("عنوان", DS + 2, T.CHAMPAGNE)], 540, 470)],
             ins=[13.22, 14.58, 14.78, 15.98, 16.20],
             outs=[17.45, 17.85, 17.95, 18.35, 18.50], in_dur=0.8, out_dur=1.0, style="smoke"),
]

# ---------------------------------------------------------------- render


def shot_image(i, t, readers):
    s = SHOTS[i]
    lin = readers[i].frame(int(round((t - s["t0"]) * FPS)))
    return G.grade(push(lin, s, t), s["c"])


def render_frame(t, readers):
    active = [i for i, s in enumerate(SHOTS) if s["t0"] - 1e-6 <= t < s["t1"] + 1e-6]
    out = None
    for i in active:
        img = shot_image(i, t, readers)
        if out is None:
            out = img
        else:
            s = SHOTS[i]
            p = (t - s["t0"]) / (SHOTS[i - 1]["t1"] - s["t0"])
            a = lights_first(p, np.clip(G.luma(img) * 1.6, 0, 1))[..., None]
            out = out * (1 - a) + img * a
    lum = np.clip(G.luma(out) * 1.6, 0, 1)
    if t < FADE_IN[1]:
        p = (t - FADE_IN[0]) / (FADE_IN[1] - FADE_IN[0])
        out = out * lights_first(p, lum, 0.8)[..., None]
    if t > FADE_OUT[0]:
        p = 1 - (t - FADE_OUT[0]) / (FADE_OUT[1] - FADE_OUT[0])
        out = out * lights_first(max(p, 0), lum, 0.8)[..., None]
    out = np.ascontiguousarray(np.clip(out, 0, 1.05), dtype=np.float32)
    if not args.notext:
        for st in STANZAS:
            st.draw(out, t)
    return G.finish(out)


def to8(x):
    return (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)


if args.still:
    for t in [float(v) for v in args.still.split(",")]:
        readers = {}
        for i, s in enumerate(SHOTS):
            if s["t0"] - 1e-6 <= t < s["t1"] + 1e-6:
                readers[i] = Reader(s, int(round((t - s["t0"]) * FPS)))
        img = render_frame(t, readers)
        for r in readers.values():
            r.close()
        Image.fromarray(to8(img)).save(f"{args.out}_{t:05.2f}.png")
    sys.exit(0)

readers = {}
enc = subprocess.Popen([
    "ffmpeg", "-v", "error", "-y",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-i", args.audio,
    "-map", "0:v", "-map", "1:a",
    "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
    "-c:v", "libx264", "-preset", "slow", "-crf", "13", "-maxrate", "25M", "-bufsize", "50M", "-x264-params", "aq-mode=3:aq-strength=0.8:deblock=-1,-1",
    "-profile:v", "high", "-level", "4.2", "-tune", "film",
    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
    "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
    "-t", f"{DUR:.3f}", "-movflags", "+faststart", args.out], stdin=subprocess.PIPE)

for k in range(NF):
    t = k / FPS
    for i, s in enumerate(SHOTS):
        if i not in readers and t >= s["t0"] - 1e-6:
            readers[i] = Reader(s)
        if i in readers and t > s["t1"] + 0.1:
            readers[i].close()
    enc.stdin.write(to8(render_frame(t, readers)).tobytes())
    if k % 60 == 0:
        print(f"frame {k}/{NF}", flush=True)
enc.stdin.close()
enc.wait()
print("done", args.out)
