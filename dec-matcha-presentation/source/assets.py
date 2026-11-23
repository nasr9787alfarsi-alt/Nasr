"""Render the image assets for the Dec Matcha cinematic deck."""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
LOGO = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)


def save_rgba(arr, name):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA").save(os.path.join(OUT, name), optimize=True)


# ---------------------------------------------------------------- backgrounds
def background(name, glows, W=1600, H=900):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    nx, ny = x / W, y / H
    base = np.array([9, 19, 13], np.float32)
    img = np.ones((H, W, 3), np.float32) * base
    for gx, gy, rad, col, k in glows:
        d2 = ((nx - gx) * 16 / 9) ** 2 + (ny - gy) ** 2
        img += np.exp(-d2 / (2 * rad * rad))[..., None] * np.array(col, np.float32) * k
    # vignette
    v = ((nx - 0.5) * 1.2) ** 2 + ((ny - 0.5) * 1.4) ** 2
    img *= (1 - 0.55 * np.clip(v, 0, 1))[..., None]
    img += rng.normal(0, 2.2, (H, W, 1))  # film grain / dithering
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(os.path.join(OUT, name), quality=90)


GREEN, GOLD = (52, 88, 40), (70, 58, 26)
bgs = {
    1: [(0.27, 0.5, 0.33, GREEN, 1.0), (0.85, 0.15, 0.30, GOLD, 0.5)],
    2: [(0.5, 0.52, 0.30, GREEN, 1.0), (0.1, 0.9, 0.3, GOLD, 0.35)],
    3: [(0.72, 0.45, 0.30, GREEN, 0.9), (0.2, 0.4, 0.3, GOLD, 0.35)],
    4: [(0.24, 0.55, 0.30, GREEN, 1.0), (0.85, 0.85, 0.30, GOLD, 0.4)],
    5: [(0.5, 0.55, 0.32, GREEN, 0.9), (0.9, 0.1, 0.3, GOLD, 0.35)],
    6: [(0.5, 0.25, 0.32, GREEN, 0.85), (0.1, 0.95, 0.3, GOLD, 0.35)],
    7: [(0.68, 0.5, 0.30, GREEN, 0.9), (0.15, 0.2, 0.3, GOLD, 0.4)],
    8: [(0.1, 0.5, 0.30, GREEN, 0.8), (0.9, 0.9, 0.3, GOLD, 0.35)],
    9: [(0.5, 0.35, 0.33, GREEN, 1.1), (0.85, 0.85, 0.3, GOLD, 0.5)],
}
for k, g in bgs.items():
    background(f"bg{k}.jpg", g)


# ---------------------------------------------------------------- the matcha bowl (top view, 3D shaded)
def orb(N=1000):
    c = N / 2
    R = N * 0.44
    y, x = np.mgrid[0:N, 0:N].astype(np.float32)
    dx, dy = x - c, y - c
    r = np.sqrt(dx * dx + dy * dy) / R
    th = np.arctan2(dy, dx)
    L = np.array([-0.5, -0.6, 0.62]); L /= np.linalg.norm(L)
    H = L + np.array([0, 0, 1.0]); H /= np.linalg.norm(H)
    col = np.zeros((N, N, 3), np.float32)

    # ceramic rim (torus cross-section)
    t = np.clip((r - 0.93) / 0.07, -1, 1)
    nz = np.sqrt(np.clip(1 - t * t, 0, 1))
    n = np.stack([t * np.cos(th), t * np.sin(th), nz], -1)
    diff = np.clip(n @ L, 0, 1)
    spec = np.clip(n @ H, 0, 1) ** 40
    cream = np.array([238, 231, 214], np.float32)
    speck = (rng.random((N, N)) > 0.996).astype(np.float32)
    speck = np.array(Image.fromarray((speck * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))) / 255.0
    rim = cream * (0.42 + 0.68 * diff)[..., None] + (spec * 120)[..., None] - (speck * 60)[..., None]

    # inner wall slopes toward the centre
    k = 0.65
    nw = np.stack([-np.cos(th) * k, -np.sin(th) * k, np.full_like(th, 0.76)], -1)
    dw = np.clip(nw @ L, 0, 1)
    wall = cream * 0.86 * (0.35 + 0.75 * dw)[..., None] - (speck * 40)[..., None]

    # matcha surface: foam + one-armed spiral (whisked swirl)
    rho = np.clip(r / 0.80, 0, 1)
    fine = rng.normal(0, 1, (N, N)).astype(np.float32)
    fine = np.array(Image.fromarray(((fine * 40) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.4)), np.float32) / 128 - 1
    coarse = rng.normal(0, 1, (N // 8, N // 8)).astype(np.float32)
    coarse = np.array(Image.fromarray(((coarse * 40) + 128).clip(0, 255).astype(np.uint8)).resize((N, N), Image.BICUBIC).filter(ImageFilter.GaussianBlur(6)), np.float32) / 128 - 1
    spiral = np.sin(th - 13.0 * rho + 0.6 * coarse)
    froth = np.clip((spiral - 0.35) / 0.65, 0, 1) ** 1.5 * np.clip(rho / 0.15, 0, 1) * np.clip((0.95 - rho) / 0.2, 0, 1)
    base = np.array([112, 146, 52], np.float32)
    foam = np.array([200, 218, 140], np.float32)
    liquid = base * (1 - froth[..., None] * 0.85) + foam * froth[..., None] * 0.85
    liquid *= (1 + 0.10 * fine + 0.06 * coarse)[..., None]
    shade = 1 + 0.16 * (-(dx + dy) / (R * 1.4))
    liquid *= shade[..., None]
    liquid *= (1 - 0.35 * np.clip((rho - 0.93) / 0.07, 0, 1))[..., None]  # meniscus
    hx, hy = c - 0.33 * R, c - 0.38 * R
    hl = np.exp(-(((x - hx) ** 2) / (2 * (0.16 * R) ** 2) + ((y - hy) ** 2) / (2 * (0.09 * R) ** 2)))
    liquid += (hl * 70)[..., None]

    col = np.where((r < 0.80)[..., None], liquid, np.where((r < 0.86)[..., None], wall, rim))
    # soft anti-aliased band transitions
    alpha = np.clip((1.0 - r) * R / 1.5 + 0.5, 0, 1)

    # drop shadow
    sh = Image.new("L", (N, N), 0)
    ImageDraw.Draw(sh).ellipse([c - R, c - R + 0.05 * R, c + R, c + R + 0.05 * R], fill=170)
    sh = np.array(sh.filter(ImageFilter.GaussianBlur(0.06 * R)), np.float32) / 255
    out = np.zeros((N, N, 4), np.float32)
    out[..., :3] = col * alpha[..., None]
    a = alpha + sh * (1 - alpha)
    out[..., :3] = np.where(a[..., None] > 0, out[..., :3] / np.maximum(a, 1e-6)[..., None], 0)
    out[..., :3] *= np.where(alpha > 0, 1, 0)[..., None] + 0  # shadow colour is black
    out[..., 3] = a * 255
    save_rgba(out, "orb.png")


orb()


# ---------------------------------------------------------------- leaves (from the brand logo)
logo = Image.open(LOGO).convert("RGBA")
leaf = logo.crop((380, 10, 572, 186))
arr = np.array(leaf, np.float32)
arr[..., :3] = np.clip(arr[..., :3] * np.array([1.55, 1.6, 1.35]), 0, 255)
leaf = Image.fromarray(arr.astype(np.uint8), "RGBA")
pad = Image.new("RGBA", (leaf.width + 80, leaf.height + 80), (0, 0, 0, 0))
pad.paste(leaf, (40, 40))
pad.save(os.path.join(OUT, "leafA.png"), optimize=True)
big = pad.resize((pad.width * 2, pad.height * 2), Image.LANCZOS).filter(ImageFilter.GaussianBlur(9))
b = np.array(big, np.float32); b[..., 3] *= 0.75
save_rgba(b, "leafB.png")


# ---------------------------------------------------------------- bokeh layer
W, H = 2300, 1300
bok = np.zeros((H, W, 4), np.float32)
layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(layer)
for i in range(46):
    rr = rng.uniform(12, 70)
    cx, cy = rng.uniform(0, W), rng.uniform(0, H)
    colr = [(186, 214, 120), (226, 200, 130), (150, 190, 100)][i % 3]
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=colr + (int(rng.uniform(10, 34)),))
layer = layer.filter(ImageFilter.GaussianBlur(5))
layer.save(os.path.join(OUT, "bokeh.png"), optimize=True)


# ---------------------------------------------------------------- gauge + needle
def gauge(N=1000, S=2):
    M = N * S
    im = Image.new("RGBA", (M, M), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = M / 2
    # bezel
    for i in range(60):
        rr = M * (0.445 - i * 0.0007)
        g = int(40 + 50 * (i / 60))
        d.ellipse([c - rr, c - rr, c + rr, c + rr], outline=(g, g + 18, g + 4, 255), width=2)
    rr = M * 0.40
    d.ellipse([c - rr, c - rr, c + rr, c + rr], fill=(15, 30, 20, 255))
    # glowing arc band
    for j in range(271):
        a0 = 135 + j
        f = j / 270
        col = (int(157 + (216 - 157) * f), int(191 + (181 - 191) * f), int(94 + (106 - 94) * f), 255)
        r1 = M * 0.385
        d.arc([c - r1, c - r1, c + r1, c + r1], a0, a0 + 1.5, fill=col, width=int(M * 0.012))
    # ticks
    for i in range(51):
        ang = math.radians(135 + i * 270 / 50)
        major = i % 5 == 0
        r_in = M * (0.325 if major else 0.345)
        r_out = M * 0.368
        w = 7 if major else 3
        colr = (242, 238, 227, 255) if major else (160, 180, 150, 200)
        d.line([c + r_in * math.cos(ang), c + r_in * math.sin(ang), c + r_out * math.cos(ang), c + r_out * math.sin(ang)], fill=colr, width=w)
    im = im.resize((N, N), Image.LANCZOS)
    glow = im.filter(ImageFilter.GaussianBlur(10))
    out = Image.alpha_composite(glow, im)
    out.save(os.path.join(OUT, "gauge.png"), optimize=True)

    nd = Image.new("RGBA", (M, M), (0, 0, 0, 0))
    d = ImageDraw.Draw(nd)
    tip, base_w = M * 0.33, M * 0.018
    d.polygon([(c - base_w, c), (c, c - tip), (c + base_w, c), (c, c + M * 0.05)], fill=(216, 181, 106, 255))
    d.polygon([(c, c), (c, c - tip), (c + base_w, c)], fill=(240, 214, 150, 255))
    nd = nd.resize((N, N), Image.LANCZOS)
    g2 = nd.filter(ImageFilter.GaussianBlur(8))
    Image.alpha_composite(g2, nd).save(os.path.join(OUT, "needle.png"), optimize=True)


gauge()


# ---------------------------------------------------------------- radar + sweep
def radar(N=1000, S=2):
    M = N * S
    im = Image.new("RGBA", (M, M), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = M / 2
    d.ellipse([c - M * 0.48, c - M * 0.48, c + M * 0.48, c + M * 0.48], fill=(16, 32, 21, 170))
    for f, w, a in [(0.16, 3, 90), (0.29, 3, 90), (0.42, 3, 110), (0.48, 5, 160)]:
        rr = M * f
        d.ellipse([c - rr, c - rr, c + rr, c + rr], outline=(157, 191, 94, a), width=w)
    for k in range(0, 360, 45):
        a = math.radians(k)
        for s in np.arange(0.05, 0.47, 0.025):
            p1 = (c + M * s * math.cos(a), c + M * s * math.sin(a))
            p2 = (c + M * (s + 0.012) * math.cos(a), c + M * (s + 0.012) * math.sin(a))
            d.line([p1, p2], fill=(157, 191, 94, 70), width=2)
    for k in range(0, 360, 5):
        a = math.radians(k)
        r1 = M * (0.455 if k % 30 else 0.44)
        d.line([c + r1 * math.cos(a), c + r1 * math.sin(a), c + M * 0.47 * math.cos(a), c + M * 0.47 * math.sin(a)], fill=(200, 220, 160, 120), width=3)
    im.resize((N, N), Image.LANCZOS).save(os.path.join(OUT, "radar.png"), optimize=True)

    y, x = np.mgrid[0:N, 0:N].astype(np.float32)
    dx, dy = x - N / 2, y - N / 2
    r = np.sqrt(dx * dx + dy * dy) / N
    th = (np.degrees(np.arctan2(dy, dx)) + 360) % 360  # 0 = east, clockwise (y down)
    lag = (0 - th) % 360  # degrees behind the leading edge at 0deg
    a = np.where(lag < 70, (1 - lag / 70) ** 2, 0) * (r < 0.47) * 120
    a += np.where(lag < 1.2, 1, 0) * (r < 0.47) * 120
    out = np.zeros((N, N, 4), np.float32)
    out[..., 0], out[..., 1], out[..., 2] = 180, 220, 110
    out[..., 3] = a
    save_rgba(out, "sweep.png")


radar()
print("assets written to", OUT)
