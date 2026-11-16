"""
Typography for «مساء».

Two voices, one hierarchy:
  * DISPLAY — Gulzar (Nastaliq). The calligraphic voice of the poem: the words that carry
    meaning (رحيل العمر، تطارد، خيط دخان، حبيبة قلبك، أرض، وطن، عنوان).
  * LIGHT   — IBM Plex Sans Arabic Light. A quiet, contemporary companion for the small
    connecting words (بعد، بأنك كنت، ليس لها، أو), set small and slightly dimmer.
Lines are set right-to-left from individually shaped words (Raqm/HarfBuzz) and aligned on a
shared baseline, so the two scripts sit together as one composed line.

Motion: each word is revealed by a feathered right-to-left wipe (the direction the hand
writes Arabic), combined with an opacity ease, a 7px rise and a focus pull. Exits are a
soft fade with a slight drift; «دخان» and the closing words disperse upward like smoke.
"""
import os, math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
SS = 2  # supersampling for glyph rendering

IVORY = np.array([247, 242, 232], np.float32) / 255
SOFT = np.array([226, 220, 208], np.float32) / 255
CHAMPAGNE = np.array([238, 214, 166], np.float32) / 255

_FONTS = {}


def font(path, size):
    key = (path, size)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(path, size * SS, layout_engine=ImageFont.Layout.RAQM)
    return _FONTS[key]


class Fonts:
    def __init__(self, d):
        self.display = os.path.join(d, "gulzar-arabic-400-normal.ttf")
        self.light = os.path.join(d, "ibm-plex-sans-arabic-arabic-300-normal.ttf")


def ease_out(x):  # easeOutQuart
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 4


def ease_io(x):  # easeInOutSine
    x = min(max(x, 0.0), 1.0)
    return 0.5 - 0.5 * math.cos(math.pi * x)


class Word:
    """a shaped word sprite (alpha, float32) with its baseline position"""

    def __init__(self, text, path, size, color, alpha=1.0, gap=1.0):
        f = font(path, size)
        kw = dict(direction="rtl", language="ar")
        bbox = f.getbbox(text, anchor="ls", **kw)  # relative to baseline-left
        pad = 34 * SS
        w = bbox[2] - bbox[0] + 2 * pad
        h = bbox[3] - bbox[1] + 2 * pad
        im = Image.new("L", (w, h), 0)
        ImageDraw.Draw(im).text((pad - bbox[0], pad - bbox[1]), text, font=f, fill=255, anchor="ls", **kw)
        a = np.asarray(im, np.float32) / 255
        a = cv2.resize(a, (w // SS, h // SS), interpolation=cv2.INTER_AREA)
        self.a = a
        self.adv = f.getlength(text, **kw) / SS
        self.space = f.getlength(" ", **kw) / SS * gap
        self.ox = (pad - bbox[0]) / SS  # sprite-x of the word's origin (left at baseline)
        self.oy = (pad - bbox[1]) / SS  # sprite-y of the baseline
        self.color = color
        self.alpha = alpha
        self.x = self.y = 0.0


class Line:
    """words set right-to-left on one baseline"""

    def __init__(self, words, x, baseline, align="center"):
        self.words = words
        total = sum(w.adv for w in words) + sum(max(words[i].space, words[i + 1].space) * 0.5 +
                                                  min(words[i].space, words[i + 1].space) * 0.5
                                                  for i in range(len(words) - 1))
        if align == "center":
            right = x + total / 2
        elif align == "right":
            right = x
        else:
            right = x + total
        cur = right
        for i, w in enumerate(words):
            left = cur - w.adv
            w.x = left - w.ox
            w.y = baseline - w.oy
            if i < len(words) - 1:
                nxt = words[i + 1]
                cur = left - (max(w.space, nxt.space) * 0.5 + min(w.space, nxt.space) * 0.5)


def _blit(canvas, a, color, x, y, glow):
    """composite sprite alpha at sub-pixel position with a soft dark glow"""
    h, w = a.shape
    ix, iy = int(math.floor(x)), int(math.floor(y))
    fx, fy = x - ix, y - iy
    if fx > 1e-3 or fy > 1e-3:
        M = np.array([[1, 0, fx], [0, 1, fy]], np.float32)
        a = cv2.warpAffine(a, M, (w + 1, h + 1), flags=cv2.INTER_LINEAR)
        h, w = a.shape
    X0, Y0, X1, Y1 = max(ix, 0), max(iy, 0), min(ix + w, W), min(iy + h, H)
    if X1 <= X0 or Y1 <= Y0:
        return
    a = a[Y0 - iy:Y1 - iy, X0 - ix:X1 - ix]
    if a.max() < 0.002:
        return
    reg = canvas[Y0:Y1, X0:X1]
    if glow > 0:
        g = cv2.GaussianBlur(a, (0, 0), 9) * glow + cv2.GaussianBlur(a, (0, 0), 2.2) * glow * 0.45
        reg *= (1 - np.clip(g, 0, 0.85))[..., None]
    a3 = a[..., None]
    reg[:] = reg * (1 - a3) + color * a3


class Reveal:
    """
    timing for one stanza. ins: onset per word (in order of `words`).
    outs: exit time per word (or one value for all). style: 'fade' | 'smoke'.
    """

    def __init__(self, lines, ins, outs, in_dur=0.85, out_dur=0.6, style="fade", glow=0.42):
        self.words = [w for l in lines for w in l.words]
        self.ins = ins
        self.outs = outs if isinstance(outs, (list, tuple)) else [outs] * len(self.words)
        self.in_dur, self.out_dur, self.style, self.glow = in_dur, out_dur, style, glow
        # feathered wipe ramps, cached per word
        self._ramps = []
        for w in self.words:
            hh, ww = w.a.shape
            self._ramps.append(np.linspace(0, 1, ww, dtype=np.float32)[None, :])

    def draw(self, canvas, t):
        for i, w in enumerate(self.words):
            t_in, t_out = self.ins[i], self.outs[i]
            if t < t_in:
                continue
            u = (t - t_in) / self.in_dur
            pin = ease_out(u)
            pout = ease_io((t - t_out) / self.out_dur) if t > t_out else 0.0
            if pout >= 0.999:
                continue
            a = w.a
            if u < 1.0:
                # right-to-left feathered wipe: column x is visible once the front passes it
                feather = 0.45
                front = 1.0 - ease_out(u * 1.15) * (1 + feather)   # 1 -> -feather
                m = np.clip((self._ramps[i] - front) / feather, 0, 1)
                a = a * (m * m * (3 - 2 * m))
            alpha = w.alpha * (0.15 + 0.85 * pin) * (1 - pout)
            if u < 1.0:
                alpha = w.alpha * min(1.0, pin * 1.25) * (1 - pout)
            blur = (1 - pin) * 2.2
            dy = (1 - pin) * 7.0
            if self.style == "smoke" and pout > 0:
                blur += pout * 9.0
                dy -= pout * 28.0
            elif pout > 0:
                blur += pout * 1.6
                dy -= pout * 6.0
            if blur > 0.15:
                a = cv2.GaussianBlur(a, (0, 0), blur)
            _blit(canvas, a * alpha, w.color, w.x, w.y + dy, self.glow * (1 - pout * 0.5))
