"""
Scene-linear colour pipeline for the iPhone HLG night footage.

decode   : 10-bit HEVC -> temporal/spatial denoise (hqdn3d, per clip) -> HLG -> scene-linear
           Rec.709 float (1.0 = HLG reference white, highlights up to ~5x preserved)
correct  : per-clip white balance + exposure (in linear light, where it is physically right)
tone     : filmic curve on luminance (hue/ratio preserving): shadow toe that opens the
           darks without lifting black, smooth highlight shoulder that keeps lamp and
           window detail instead of clipping; gentle highlight desaturation like film
look     : per-clip contrast, vibrance (protects already-saturated pinks/golds & skin),
           a shared split tone (clean blue-black shadows, warm lights)
detail   : luma-only clarity (large-radius local contrast, midtone-masked) and fine
           sharpening with a noise threshold — no colour fringing, no halos
"""
import math
import numpy as np
import cv2

W, H = 1080, 1920

# hqdn3d: luma_spatial:chroma_spatial:luma_tmp:chroma_tmp
DENOISE = {  # spatial pre-filter only; temporal denoising is motion-compensated (mcdenoise.py)
    "IMG_5945": "1.2:2.5:0:0", "IMG_5936": "1.0:2.5:0:0", "IMG_5941": "0.8:2:0:0", "IMG_5944": "1.5:3:0:0",
    "IMG_5949": "1.5:3:0:0", "IMG_5937": "0.8:2:0:0", "IMG_5935": "1.5:3:0:0", "IMG_5932": "1:2:0:0",
}

# per-clip correction. ev: exposure in stops; wb: linear RGB gains;
# toe: shadow/midtone gamma (<1 opens); con: S-curve contrast; vib: vibrance; bp: black point
LOOK = {
    # golden shoreline: hazy orange sky -> cleaner neutral night, keep the gold lights
    "IMG_5945": dict(ev=1.56, wb=(0.93, 1.0, 1.12), toe=1.095, con=1.06, vib=0.22, bp=0.0, grad=0.38),
    # overpass + headlights: mixed sodium/LED, tame the glare, open the ceiling a touch
    "IMG_5936": dict(ev=1.21, wb=(0.95, 1.0, 1.06), toe=1.098, con=1.05, vib=0.15, bp=0.0),
    # corniche walkway from above: bright, warm path; hold highlights, keep people natural
    "IMG_5941": dict(ev=1.09, wb=(0.96, 1.0, 1.03), toe=1.098, con=1.05, vib=0.16, bp=0.0),
    # pink light on the water: open the dark river, keep the magenta pure
    "IMG_5944": dict(ev=1.71, wb=(0.98, 1.0, 1.03), toe=1.098, con=1.07, vib=0.20, bp=0.0),
    # POV across the river: the darkest shot — lift more, deep blue-black water
    "IMG_5949": dict(ev=2.08, wb=(0.96, 1.0, 1.05), toe=1.098, con=1.07, vib=0.22, bp=0.0),
    # lit corniche: very bright paving, warm cast -> neutralise slightly, recover highlights
    "IMG_5937": dict(ev=0.31, wb=(0.93, 1.0, 1.08), toe=0.927, con=1.05, vib=0.14, bp=0.0),
    # skyline with the pink reflection (replaces IMG_5949: far more real detail, same mood)
    "IMG_5942": dict(ev=1.80, wb=(0.96, 1.0, 1.05), toe=1.060, con=1.06, vib=0.20, bp=0.0),
    # distant towers: dark, fine city lights — lift and add sparkle
    "IMG_5935": dict(ev=1.83, wb=(0.96, 1.0, 1.05), toe=1.083, con=1.07, vib=0.22, bp=0.0),
}

SHADOW_TINT = np.array([-0.010, -0.002, 0.012], np.float32)   # clean blue-black
HILITE_TINT = np.array([0.018, 0.006, -0.014], np.float32)   # warm lights
HALO_TINT = np.array([1.0, 0.82, 0.64], np.float32)
REC709 = np.array([0.2126, 0.7152, 0.0722], np.float32)


def decode_filter(clip, speed=1.0, fps=30):
    vf = f"hqdn3d={DENOISE.get(clip, '3:4:6:8')}"
    if speed != 1.0:
        vf += f",format=yuv444p,setpts={1/speed:.6f}*PTS,minterpolate=fps={fps}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
    return vf + ",zscale=tin=arib-std-b67:pin=bt2020:min=bt2020nc:rin=tv:t=linear:npl=203:p=bt709,format=gbrpf32le"


def planar_to_rgb(buf):
    a = np.frombuffer(buf, np.float32).reshape(3, H, W)
    return np.ascontiguousarray(np.stack([a[2], a[0], a[1]], -1))  # gbr -> rgb


def luma(x):
    return x[..., 0] * 0.2126 + x[..., 1] * 0.7152 + x[..., 2] * 0.0722


def _oetf(x):
    # continuous display encode (sRGB-style piecewise curve, no seam)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(np.maximum(x, 0.0031308), 1 / 2.4) - 0.055)


def _hlg(E):
    a, b, c = 0.17883277, 0.28466892, 0.55991073
    return np.where(E <= 1 / 12, np.sqrt(3 * np.maximum(E, 0)), a * np.log(np.maximum(12 * E - b, 1e-6)) + c)


def tone(lin, p):
    """linear scene -> display-referred [0,1].
    Luminance is mapped through the HLG curve itself (the camera's own, natural-looking
    shadow and midtone response), then a smooth shoulder brings the >reference-white
    lights that the plain conversion clipped back into range. RGB ratios are kept, so
    hues stay true; a per-clip black point clears the milky noise floor."""
    x = np.maximum(lin, 0) * np.array(p["wb"], np.float32) * (2.0 ** p["ev"])
    L = np.maximum(luma(x), 1e-8)
    E = np.power(L * 0.203, 1 / 1.2)                 # display-referred -> scene (inverse OOTF)
    d = _hlg(E) / 0.75                               # 1.0 at reference white
    d = np.power(np.clip(d, 0, None), p["toe"])      # per-clip shadow/midtone gamma
    # shoulder: 0.72..1.333 -> 0.72..1.0, slope-continuous
    k0, k1 = 0.72, 1.333
    t = np.clip((d - k0) / (k1 - k0), 0, 1)
    d = np.where(d > k0, k0 + (1 - k0) * (1 - (1 - t) ** 2), d)
    # black point
    bp = p["bp"]
    d = np.clip((d - bp) / (1 - bp), 0, 1)
    D = np.power(d, 2.4)                              # display-linear target luminance
    y = x * (D / L)[..., None]
    # film-like highlight desaturation: channels that exceed 1 bleed toward white
    m = y.max(-1, keepdims=True)
    over = np.clip((m - 0.85) / 0.6, 0, 1)
    y = y * (1 - over) + (D[..., None] + (y - D[..., None]) * 0.35) * over
    # calm chroma noise in the deepest shadows
    sh = np.clip(d / 0.12, 0, 1)[..., None]
    y = D[..., None] + (y - D[..., None]) * (0.55 + 0.45 * sh)
    y = np.clip(y, 0, 1)
    return np.power(y, 1 / 2.4)


def _smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def look(d, p):
    # clean the veiling flare a hair, then a black- and white-preserving S-curve
    d = np.clip(d, 0, 1.05)
    amt = (p["con"] - 1.0) * 4.0
    # pivot low: mid/high tones gain contrast, the shadow end is left open
    d = d + amt * d * (1 - np.clip(d, 0, 1)) * (d - 0.14) * np.clip(d / 0.14, 0, 1)
    d = np.clip(d, 0, 1.05)
    # vibrance: boost low-chroma colours more than already-saturated ones
    l = luma(d)[..., None]
    c = d - l
    sat = np.abs(c).max(-1, keepdims=True) / (l + 0.06)
    vmask = _smooth(0.03, 0.16, l)  # never push colour into near-black noise
    d = l + c * (1 + p["vib"] * np.clip(1 - sat * 0.9, 0, 1) * vmask)
    # split tone with soft, wide masks (no visible boundaries in gradients)
    lm = np.clip(luma(d), 0, 1)[..., None]
    wsh = _smooth(0.0, 0.18, lm) * (1 - _smooth(0.12, 0.45, lm))
    d = d + wsh * SHADOW_TINT + _smooth(0.45, 1.0, lm) * HILITE_TINT
    return d


def detail(d, clarity=0.12, sharp=0.38):
    """edge-aware definition on luma only: sharpening is applied where there is a real
    edge (gradient well above the noise floor), never on flat sky/water noise"""
    l = luma(d)
    big = cv2.GaussianBlur(l, (0, 0), 24)
    mask_mid = np.clip(1 - np.abs(l - 0.42) * 2.2, 0, 1) * np.clip(l * 6, 0, 1)
    dl = (l - big) * clarity * mask_mid
    fine = cv2.GaussianBlur(l, (0, 0), 0.9)
    hf = l - fine
    gx = cv2.Sobel(fine, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(fine, cv2.CV_32F, 0, 1, ksize=3)
    g = cv2.GaussianBlur(np.sqrt(gx * gx + gy * gy), (0, 0), 1.0)
    edge = np.clip((g - 0.035) / 0.08, 0, 1)
    dl += hf * sharp * edge
    return d + dl[..., None]


def halation(d, amount=0.22):
    small = cv2.resize(d, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    hi = np.clip(luma(small) - 0.72, 0, None)[..., None] * small
    halo = cv2.GaussianBlur(hi, (0, 0), 5) * 0.5 + cv2.GaussianBlur(hi, (0, 0), 16) * 0.5
    halo = cv2.resize(halo, (W, H), interpolation=cv2.INTER_LINEAR) * HALO_TINT
    return d + halo * amount


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_rx = (xx - W / 2) / (W * 0.62)
_ry = (yy - H * 0.47) / (H * 0.62)
VIGNETTE = (1.0 - 0.16 * np.clip(_rx * _rx + _ry * _ry, 0, 1.6) ** 1.3)[..., None].astype(np.float32)
_rng = np.random.default_rng(11)


def finish(d):
    d = d * VIGNETTE
    # tiny dither only (prevents banding in the night sky after 8-bit encode)
    d = d + _rng.uniform(-0.5, 0.5, (H, W, 1)).astype(np.float32) / 255.0
    return np.clip(d, 0, 1)


GRAD_Y = None


def grade(lin, clip):
    global GRAD_Y
    p = LOOK[clip]
    d = tone(lin, p)
    d = look(d, p)
    if p.get("grad"):
        # soft graduated ND on the sky (screen-fixed, like a filter on the lens)
        if GRAD_Y is None:
            GRAD_Y = _smooth(0.0, 0.48, np.linspace(0, 1, H, dtype=np.float32))[:, None, None]
        d = d * (1 - p["grad"] * (1 - GRAD_Y))
    d = halation(d)
    d = detail(d)
    return d
