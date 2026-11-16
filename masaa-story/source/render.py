#!/usr/bin/env python3
"""
مساء — Instagram Story (1080x1920, 30 fps)

Frame-accurate compositor:
  * iPhone HLG footage -> Rec.709 SDR, per-shot exposure balance
  * sub-pixel slow push-ins (Ken Burns) with cv2.warpAffine
  * "lights-first" luminance dissolves: bright points of the incoming shot
    arrive before its shadows, like city lights switching on
  * a unified night grade: soft highlight shoulder, warm halation around
    the lights, cool deep shadows, gentle vignette, fine grain
  * Arabic typography rendered with Raqm (HarfBuzz + FriBiDi), revealed
    word by word on the voice, with soft glow for legibility
Output video is piped as raw RGB into ffmpeg, which muxes the audio.

Usage: render.py <clips_dir> <fonts_dir> <audio_wav> <out.mp4> [--preview N] [--still t1,t2,...]
"""
import os, sys, subprocess, math, argparse
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
DUR = 20.2
NF = int(round(DUR * FPS))

ap = argparse.ArgumentParser()
ap.add_argument("clips"); ap.add_argument("fonts"); ap.add_argument("audio"); ap.add_argument("out")
ap.add_argument("--still", default="")
ap.add_argument("--notext", action="store_true")
args = ap.parse_args()

# ---------------------------------------------------------------- shots
# clip, source in-point, timeline start, timeline end, speed, zoom a->b, focal point, exposure gain
SHOTS = [
    dict(c="IMG_5945", src=0.40, t0=0.00,  t1=2.40,  sp=1.00, z=(1.000, 1.035), f=(560, 900),  g=1.00),  # golden shoreline — وستعرف
    dict(c="IMG_5936", src=0.15, t0=2.00,  t1=4.65,  sp=1.00, z=(1.045, 1.010), f=(560, 980),  g=0.90),  # headlights pass — بعد رحيل العمر
    dict(c="IMG_5941", src=0.00, t0=4.35,  t1=7.42,  sp=0.88, z=(1.000, 1.045), f=(760, 640),  g=0.92),  # people on the curving path — تطارد
    dict(c="IMG_5944", src=1.30, t0=7.10,  t1=9.60,  sp=1.00, z=(1.040, 1.005), f=(700, 1000), g=1.02),  # pink light on water — خيط دخان
    dict(c="IMG_5949", src=0.00, t0=9.05,  t1=13.20, sp=1.00, z=(1.040, 1.090), f=(640, 1180), g=1.10),  # looking across the river — فحبيبة قلبك
    dict(c="IMG_5937", src=5.40, t0=13.02, t1=14.66, sp=1.00, z=(1.020, 1.050), f=(560, 900),  g=0.88),  # the corniche — أرض
    dict(c="IMG_5945", src=2.78, t0=14.45, t1=16.08, sp=0.87, z=(1.060, 1.090), f=(420, 1000), g=1.00),  # the opening shore returns — أو وطن
    dict(c="IMG_5935", src=0.40, t0=15.88, t1=DUR,   sp=1.00, z=(1.000, 1.060), f=(620, 900),  g=1.10),  # distant shore, fade — أو عنوان
]
FADE_IN = (0.0, 0.95)
FADE_OUT = (18.55, 20.15)


def tonemap_chain(sp):
    vf = "zscale=t=bt709:p=bt709:m=bt709:r=tv"
    if sp != 1.0:
        vf += f",format=yuv444p,setpts={1/sp:.6f}*PTS,minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
    return vf + ",format=rgb48le"


class Reader:
    def __init__(self, s):
        self.s = s
        n = int(math.ceil((s["t1"] - s["t0"]) * FPS)) + 2
        src_len = (s["t1"] - s["t0"]) * s["sp"] + 0.2
        cmd = ["ffmpeg", "-v", "error", "-ss", f"{s['src']:.3f}", "-t", f"{src_len:.3f}",
               "-i", os.path.join(args.clips, s["c"] + ".MOV"),
               "-vf", tonemap_chain(s["sp"]), "-r", str(FPS), "-frames:v", str(n),
               "-f", "rawvideo", "-pix_fmt", "rgb48le", "-"]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        self.last = None
        self.idx = -1

    def frame(self, k):
        while self.idx < k:
            buf = self.p.stdout.read(W * H * 6)
            if len(buf) == W * H * 6:
                self.last = np.frombuffer(buf, np.uint16).reshape(H, W, 3).astype(np.float32) / 65535.0
            self.idx += 1
        return self.last


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def luma(img):
    return img[..., 0] * 0.2126 + img[..., 1] * 0.7152 + img[..., 2] * 0.0722


def push(img, s, t):
    """sub-pixel slow push toward the focal point"""
    u = (t - s["t0"]) / (s["t1"] - s["t0"])
    u = min(max(u, 0), 1)  # linear: the camera never stops moving across a cut
    z = s["z"][0] + (s["z"][1] - s["z"][0]) * u
    fx, fy = s["f"]
    # keep the focal point fixed on screen while scaling
    M = np.array([[z, 0, fx - z * fx], [0, z, fy - z * fy]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


# ---------------------------------------------------------------- grade
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rx = (xx - W / 2) / (W * 0.62)
ry = (yy - H * 0.47) / (H * 0.60)
VIGNETTE = (1.0 - 0.26 * np.clip(rx * rx + ry * ry, 0, 1.6) ** 1.25)[..., None].astype(np.float32)
SHADOW_TINT = np.array([-0.004, 0.004, 0.016], np.float32)
HILITE_TINT = np.array([0.016, 0.006, -0.014], np.float32)
HALO_TINT = np.array([1.0, 0.80, 0.62], np.float32)
rng = np.random.default_rng(7)


def shoulder(x, knee=0.78):
    # smooth highlight roll-off above the knee
    over = np.maximum(x - knee, 0)
    return np.where(x > knee, knee + (1 - knee) * (1 - np.exp(-over / (1 - knee) * 1.25)) / (1 - math.exp(-1.25)), x)


def grade(img, gain):
    x = img * gain
    x = shoulder(x)
    # halation: a warm bloom around the brightest lights
    small = cv2.resize(x, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    hi = np.clip(luma(small) - 0.62, 0, None)[..., None] * small
    halo = cv2.GaussianBlur(hi, (0, 0), 7) * 0.55 + cv2.GaussianBlur(hi, (0, 0), 22) * 0.45
    halo = cv2.resize(halo, (W, H), interpolation=cv2.INTER_LINEAR) * HALO_TINT
    x = x + halo * 0.55
    # gentle saturation trim (keep the pinks and sodium golds, calm the noise)
    l = luma(x)[..., None]
    x = l + (x - l) * 0.90
    # split tone: cool deep shadows, warm highlights
    x = x + (1 - np.clip(l * 3.0, 0, 1)) ** 2 * SHADOW_TINT + np.clip(l, 0, 1) ** 2 * HILITE_TINT
    # soft contrast curve, lifted (not crushed) blacks
    x = np.clip(x, 0, 1)
    x = x + 0.10 * x * (1 - x) * (x - 0.35) * 2.2
    x = 0.010 + x * 0.985
    return x


def finish(x):
    x = x * VIGNETTE
    g = rng.standard_normal((H // 2, W // 2)).astype(np.float32)
    g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
    l = luma(x)
    amp = 0.012 * (0.35 + 1.4 * l * (1 - l) * 2.0)
    x = x + (g * amp)[..., None]
    return np.clip(x, 0, 1)


def lights_first(p, lum, k=0.65):
    """weight of the incoming image: bright pixels arrive first"""
    a = np.clip(p * (1 + k) - k * (1 - lum), 0, 1)
    return a * a * (3 - 2 * a)


# ---------------------------------------------------------------- typography
AMIRI = os.path.join(args.fonts, "amiri-arabic-400-normal.ttf")
IVORY = np.array([244, 238, 226], np.float32) / 255
CHAMPAGNE = np.array([234, 214, 172], np.float32) / 255


class Line:
    """one shaped RTL line, sliced into word sprites at their true positions"""

    def __init__(self, words, cx, cy, size, color=IVORY, anchor="m"):
        font = ImageFont.truetype(AMIRI, size, layout_engine=ImageFont.Layout.RAQM)
        text = " ".join(words)
        kw = dict(direction="rtl", language="ar")
        full = font.getlength(text, **kw)
        pad = int(size * 0.9)
        cw, ch = int(full + 2 * pad), int(size * 2.4)
        im = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(im).text((pad, ch // 2), text, font=font, fill=255, anchor="lm", **kw)
        a = np.asarray(im, np.float32) / 255
        if anchor == "r":
            left = cx - full - pad
        elif anchor == "l":
            left = cx - pad
        else:
            left = cx - full / 2 - pad
        self.x0, self.y0 = int(round(left)), int(round(cy - ch / 2))
        self.color = color
        # word extents: RTL, word i spans [R - len(prefix_i), R - len(prefix_{i-1})]
        R = pad + full
        self.words = []
        prev = 0.0
        sp = font.getlength(" ", **kw)
        for i, w in enumerate(words):
            pre = " ".join(words[: i + 1])
            L = font.getlength(pre, **kw)
            xa = int(math.floor(R - L - (sp / 2 if i < len(words) - 1 else pad)))
            xb = int(math.ceil(R - prev + (sp / 2 if i > 0 else pad)))
            xa, xb = max(xa, 0), min(xb, cw)
            spr = np.zeros_like(a)
            spr[:, xa:xb] = a[:, xa:xb]
            self.words.append(spr)
            prev = L + sp


def place(canvas_rgb, alpha, color, x0, y0, dy=0.0, blur=0.0, glow=0.5):
    """composite a text alpha sprite with a soft dark glow"""
    if blur > 0.05:
        alpha = cv2.GaussianBlur(alpha, (0, 0), blur)
    h, w = alpha.shape
    if abs(dy) > 0.01:
        M = np.array([[1, 0, 0], [0, 1, dy]], np.float32)
        alpha = cv2.warpAffine(alpha, M, (w, h), flags=cv2.INTER_LINEAR)
    X0, Y0 = max(x0, 0), max(y0, 0)
    X1, Y1 = min(x0 + w, W), min(y0 + h, H)
    a = alpha[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    if a.max() <= 0.001:
        return
    region = canvas_rgb[Y0:Y1, X0:X1]
    sh = cv2.GaussianBlur(a, (0, 0), 9)[..., None] * glow
    region *= (1 - sh)
    a3 = a[..., None]
    region[:] = region * (1 - a3 * 0.94) + color * (a3 * 0.94)


class Stanza:
    """
    words revealed on their spoken onsets; whole stanza leaves together
    (or each word separately with `outs`). style 'smoke' disperses upward.
    """

    def __init__(self, line, ins, out, outs=None, out_dur=0.45, in_dur=0.6, style="fade", glow=0.5):
        self.line, self.ins, self.out, self.outs, self.glow = line, ins, out, outs, glow
        self.out_dur, self.in_dur, self.style = out_dur, in_dur, style

    def draw(self, canvas, t):
        L = self.line
        for i, spr in enumerate(L.words):
            ti = self.ins[i]
            if t < ti:
                continue
            pin = ease_out((t - ti) / self.in_dur)
            to = self.outs[i] if self.outs else self.out
            pout = ease((t - to) / self.out_dur) if t >= to else 0.0
            a = pin * (1 - pout)
            if a <= 0.002:
                continue
            blur = (1 - pin) * 5.0
            dy = (1 - pin) * 10.0
            if self.style == "smoke" and pout > 0:
                blur += pout * 13.0
                dy -= pout * 34.0
            else:
                blur += pout * 2.5
            place(canvas, spr * a, L.color, L.x0, L.y0, dy=dy, blur=blur, glow=self.glow)


S = 50  # base size (px on a 1080-wide canvas): small, refined
STANZAS = [
    # «وستعرف» — alone, in the dark water below the golden shore
    Stanza(Line(["وستعرف"], 540, 1455, S), ins=[0.58], out=1.95, out_dur=0.5),
    # «بعد رحيل العمر» — over the passing headlights
    Stanza(Line(["بعد", "رحيل", "العمر"], 380, 470, S), ins=[2.33, 2.80, 3.25], out=4.12, out_dur=0.45, glow=0.7),
    # «بأنك كنت تطارد» — in the night sky, where the path leads the eye
    Stanza(Line(["بأنك", "كنت", "تطارد"], 540, 430, S), ins=[4.70, 5.60, 6.12], out=7.02, out_dur=0.38),
    # «خيط دخان» — champagne, slightly larger; dissolves like smoke
    Stanza(Line(["خيط", "دخان"], 540, 1440, S + 6, color=CHAMPAGNE), ins=[7.40, 7.82], out=None,
           outs=[8.45, 8.70], out_dur=1.0, style="smoke"),
    # «فحبيبة قلبك / ليس لها» — over the dark water of the river view
    Stanza(Line(["فحبيبة", "قلبك"], 620, 1395, S), ins=[9.62, 10.55], out=12.72, out_dur=0.42),
    Stanza(Line(["ليس", "لها"], 620, 1470, S), ins=[11.70, 12.12], out=12.72, out_dur=0.42),
    # «أرض · أو وطن · أو عنوان» — one line in the night sky, each on its own cut,
    # then they leave one by one: no land, no homeland, no address.
    Stanza(Line(["أرض", "أو", "وطن", "أو", "عنوان"], 540, 455, S),
           ins=[13.22, 14.58, 14.80, 15.98, 16.20], out=None,
           outs=[17.45, 17.85, 17.95, 18.35, 18.45], out_dur=0.95, style="smoke"),
]


# ---------------------------------------------------------------- render
def render_frame(t, readers):
    k = int(round(t * FPS))
    active = [i for i, s in enumerate(SHOTS) if s["t0"] - 1e-6 <= t < s["t1"] + 1e-6]
    out = None
    for i in active:
        s = SHOTS[i]
        r = readers[i]
        img = r.frame(int(round((t - s["t0"]) * FPS)))
        img = grade(push(img, s, t), s["g"])
        if out is None:
            out = img
        else:
            p = (t - s["t0"]) / (SHOTS[i - 1]["t1"] - s["t0"])
            a = lights_first(p, np.clip(luma(img) * 1.6, 0, 1))[..., None]
            out = out * (1 - a) + img * a
    # open: lights emerge first from black / close: lights are the last to leave
    lum = np.clip(luma(out) * 1.6, 0, 1)
    if t < FADE_IN[1]:
        p = (t - FADE_IN[0]) / (FADE_IN[1] - FADE_IN[0])
        out = out * lights_first(p, lum, 0.8)[..., None]
    if t > FADE_OUT[0]:
        p = 1 - (t - FADE_OUT[0]) / (FADE_OUT[1] - FADE_OUT[0])
        out = out * lights_first(max(p, 0), lum, 0.8)[..., None]
    out = np.ascontiguousarray(out, dtype=np.float32)
    if not args.notext:
        for st in STANZAS:
            st.draw(out, t)
    return finish(out)


def to8(x):
    return (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)


if args.still:
    times = [float(v) for v in args.still.split(",")]
    for t in times:
        readers = {}
        for i, s in enumerate(SHOTS):
            if s["t0"] - 1e-6 <= t < s["t1"] + 1e-6:
                s2 = dict(s)
                off = t - s["t0"]
                readers[i] = Reader(dict(s2, src=s["src"] + off * s["sp"], t0=s["t0"]))
                readers[i].idx = int(round(off * FPS)) - 1
        img = render_frame(t, readers)
        for r in readers.values():
            r.p.kill()
        Image.fromarray(to8(img)).save(f"{args.out}_{t:05.2f}.png")
    sys.exit(0)

readers = {}
enc = subprocess.Popen([
    "ffmpeg", "-v", "error", "-y",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-i", args.audio,
    "-map", "0:v", "-map", "1:a",
    "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-maxrate", "16M", "-bufsize", "32M", "-profile:v", "high", "-level", "4.2",
    "-x264-params", "aq-mode=3:deblock=-1,-1",
    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
    "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
    "-t", f"{DUR:.3f}", "-movflags", "+faststart", args.out], stdin=subprocess.PIPE)

for k in range(NF):
    t = k / FPS
    for i, s in enumerate(SHOTS):
        if i not in readers and t >= s["t0"] - 1e-6:
            readers[i] = Reader(s)
        if i in readers and t > s["t1"] + 0.1 and readers[i].p:
            readers[i].p.kill(); readers[i].p = None
    enc.stdin.write(to8(render_frame(t, readers)).tobytes())
    if k % 60 == 0:
        print(f"frame {k}/{NF}", flush=True)
enc.stdin.close()
enc.wait()
print("done", args.out)
