"""The 'matcha world' renders: powder-dune landscape, macro powder panel, particle convergence cloud, side-view chawan."""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
rng = np.random.default_rng(23)


def smooth_noise(n, cutoff, seed):
    r = np.random.default_rng(seed)
    X = np.fft.fft2(r.normal(0, 1, (n, n)))
    fy = np.fft.fftfreq(n)[:, None]
    fx = np.fft.fftfreq(n)[None, :]
    f = np.sqrt(fx * fx + fy * fy)
    X *= np.exp(-(f / cutoff) ** 2)
    z = np.real(np.fft.ifft2(X))
    return (z - z.min()) / (z.max() - z.min())


def feather(img, frac=0.1):
    a = np.array(img, np.float32)
    h, w = a.shape[:2]
    fy = np.clip(np.minimum(np.arange(h), np.arange(h)[::-1]) / (h * frac), 0, 1)
    fx = np.clip(np.minimum(np.arange(w), np.arange(w)[::-1]) / (w * frac), 0, 1)
    m = np.outer(fy, fx)
    a[..., 3] *= m * m * (3 - 2 * m)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


# ------------------------------------------------------------------ 1. powder-dune landscape (voxel-space renderer)
def landscape(name, W=2560, H=1440, horizon=0.40, cam_h=0.55, sun=(-0.75, 0.35, 0.55), seed=3):
    N = 1024
    low = smooth_noise(N, 0.006, seed)
    mid = smooth_noise(N, 0.02, seed + 1)
    yy, xx = np.mgrid[0:N, 0:N] / N
    ridge = 0.5 + 0.5 * np.sin(2 * np.pi * (xx * 3.0 + yy * 1.2 + 0.8 * low))
    hmap = 0.62 * low + 0.22 * ridge ** 3 * (0.4 + 0.6 * mid) + 0.16 * mid
    # lighting from the height gradient (low, warm sun raking across the dunes)
    gy, gx = np.gradient(hmap * 60)
    nrm = np.stack([-gx, -gy, np.ones_like(gx)], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    L = np.array(sun); L /= np.linalg.norm(L)
    shade = np.clip(nrm @ L, 0, 1)
    grain = smooth_noise(N, 0.35, seed + 7)
    dark, light = np.array([58, 84, 40.]), np.array([196, 210, 146.])
    cmap = dark + (light - dark) * (shade ** 1.3)[..., None]
    cmap *= (0.94 + 0.12 * grain)[..., None]

    sky_top, sky_hor = np.array([236, 233, 222.]), np.array([250, 247, 238.])
    img = np.zeros((H, W, 3))
    rows = np.arange(H)[:, None]
    t = np.clip(rows / (H * horizon), 0, 1)
    img[:] = sky_top + (sky_hor - sky_top) * t[..., None]
    # sun glow
    yy2, xx2 = np.mgrid[0:H, 0:W]
    glow = np.exp(-(((xx2 - W * 0.22) / (W * 0.35)) ** 2 + ((yy2 - H * horizon) / (H * 0.25)) ** 2))
    img += glow[..., None] * np.array([10, 8, 2.])

    ybuf = np.full(W, H, float)
    cols = np.arange(W)
    fov = 1.1
    ang = (cols / W - 0.5) * fov
    px, py = 0.5, 0.95
    zs = np.concatenate([np.linspace(0.004, 0.08, 260), np.geomspace(0.08, 1.6, 900)])
    focal = W * 0.9
    for z in zs:
        wx = (px + np.sin(ang) * z) % 1.0
        wy = (py - np.cos(ang) * z) % 1.0
        fx_, fy_ = wx * N, wy * N
        ix, iy = fx_.astype(int) % N, fy_.astype(int) % N
        ix1, iy1 = (ix + 1) % N, (iy + 1) % N
        ax, ay = fx_ - np.floor(fx_), fy_ - np.floor(fy_)
        hgt = ((hmap[iy, ix] * (1 - ax) + hmap[iy, ix1] * ax) * (1 - ay) + (hmap[iy1, ix] * (1 - ax) + hmap[iy1, ix1] * ax) * ay) * 0.42
        ys = H * horizon + (cam_h - hgt) / z * focal * 0.18
        col = cmap[iy, ix]
        fog = np.clip((z - 0.15) / 1.45, 0, 1) ** 0.8
        col = col * (1 - fog[..., None] if np.ndim(fog) else 1 - fog) + sky_hor * fog
        top = np.clip(ys, 0, H)
        mask = (rows >= top[None, :]) & (rows < ybuf[None, :])
        if mask.any():
            img[mask] = np.broadcast_to(col[None, :, :], (H, W, 3))[mask]
        ybuf = np.minimum(ybuf, top)
    # airborne dust with depth of field
    dust = Image.new("RGBA", (W, H), (150, 172, 98, 0))
    d = ImageDraw.Draw(dust)
    for i in range(260):
        x, y = rng.uniform(0, W), rng.uniform(H * 0.2, H * 0.7)
        r = rng.uniform(1.5, 4.5)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(141, 166, 91, int(rng.uniform(25, 80))))
    base = Image.fromarray(np.clip(img + rng.normal(0, 1.2, img.shape), 0, 255).astype(np.uint8)).convert("RGBA")
    base = Image.alpha_composite(base, dust.filter(ImageFilter.GaussianBlur(1.6)))
    big = Image.new("RGBA", (W, H), (150, 172, 98, 0))
    d = ImageDraw.Draw(big)
    for i in range(40):
        x, y = rng.uniform(0, W), rng.uniform(H * 0.3, H)
        r = rng.uniform(12, 30)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(120, 150, 75, int(rng.uniform(20, 50))))
    base = Image.alpha_composite(base, big.filter(ImageFilter.GaussianBlur(14)))
    base.convert("RGB").resize((1600, 900), Image.LANCZOS).save(os.path.join(OUT, name), quality=88)


# ------------------------------------------------------------------ 2. macro powder (dark, raking light) for the cover panel
def macro(name, W=900, H=1002):
    n = rng.normal(0, 1, (H, W))
    g1 = np.array(Image.fromarray(((n * 40) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6)), float)
    g2 = np.array(Image.fromarray(((rng.normal(0, 1, (H, W)) * 40) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)), float)
    hm = g1 * 0.6 + g2 * 0.4
    gy, gx = np.gradient(hm)
    nrm = np.stack([-gx, -gy, np.full_like(gx, 3.0)], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    L = np.array([-0.8, -0.5, 0.35]); L /= np.linalg.norm(L)
    sh = np.clip(nrm @ L, 0, 1)
    base = np.array([31, 58, 43.])
    img = base * (0.80 + 0.38 * sh)[..., None]
    yy, xx = np.mgrid[0:H, 0:W] / np.array([H, W])[:, None, None]
    light = np.exp(-(((xx - 0.1) / 0.6) ** 2 + ((yy - 0.05) / 0.5) ** 2))
    img *= (0.72 + 0.45 * light)[..., None]
    img *= (1 - 0.35 * np.clip(((xx - 0.5) ** 2 + (yy - 0.6) ** 2) * 1.4, 0, 1))[..., None]
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(os.path.join(OUT, name), quality=88)


# ------------------------------------------------------------------ 3. particle convergence cloud (numbers form from powder)
def dustburst(name, W=1400, H=800, n=5000, tint=(141, 166, 91), cols=((112, 140, 66), (141, 166, 91), (171, 190, 124), (217, 199, 159))):
    out = Image.new("RGBA", (W, H), tint + (0,))
    ang = rng.uniform(0, 2 * np.pi, n)
    rad = np.abs(rng.normal(0.0, 0.30, n)) * np.sqrt(rng.random(n))
    xs = W / 2 + np.cos(ang) * rad * W * 0.55
    ys = H / 2 + np.sin(ang) * rad * H * 0.55
    dep = rng.random(n)
    for lo, hi, blur, amax in [(0, .6, .5, 230), (.6, .9, 2, 160), (.9, 1, 5, 110)]:
        lay = Image.new("RGBA", (W, H), tint + (0,))
        d = ImageDraw.Draw(lay)
        sel = (dep >= lo) & (dep < hi)
        for x, y, dp in zip(xs[sel], ys[sel], dep[sel]):
            r = 0.8 + dp * 4 * rng.random()
            c = cols[int(rng.integers(0, len(cols)))]
            d.ellipse([x - r, y - r, x + r, y + r], fill=c + (int(amax * rng.uniform(.35, 1)),))
        out = Image.alpha_composite(out, lay.filter(ImageFilter.GaussianBlur(blur)))
    feather(out, 0.12).save(os.path.join(OUT, name), optimize=True)


# ------------------------------------------------------------------ 4. side-view chawan (glazed ceramic tea bowl with whisked matcha)
def chawan(name, orb_path, W=1200, H=1000):
    cx, rim_y, a = W / 2, 330, 430          # rim centre-line and half-width
    persp = 0.30                            # ellipse squash for a ~17deg camera elevation
    depth = 470                             # rim to foot
    y, x = np.mgrid[0:H, 0:W].astype(float)
    t = (y - rim_y) / depth                 # 0 at rim, 1 at foot
    half = a * np.sqrt(np.clip(1 - np.clip(t, 0, 1) ** 2.1 * 0.72, 0, 1))
    half = np.where(t > 0.9, a * 0.36, half)  # foot ring
    # body is everything between the front rim curve and the foot
    front_rim = rim_y + persp * a * np.sqrt(np.clip(1 - ((x - cx) / a) ** 2, 0, 1))
    body = (np.abs(x - cx) < half) & (y >= front_rim - 1) & (t <= 1.02)
    u = np.clip((x - cx) / np.maximum(half, 1), -1, 1)
    slope = np.clip(np.gradient(half, axis=0) / 3, -1.5, 1.5)
    n = np.stack([u, np.full_like(u, 0.15) - slope * 0.0, np.sqrt(np.clip(1 - u * u, 0, 1)) + 0.05], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    L = np.array([-0.55, -0.35, 0.76]); L /= np.linalg.norm(L)
    Hh = L + np.array([0, 0, 1.]); Hh /= np.linalg.norm(Hh)
    diff = np.clip(n @ L, 0, 1)
    spec = np.clip(n @ Hh, 0, 1) ** 60
    glaze_top, glaze_low = np.array([244, 238, 222.]), np.array([222, 210, 186.])
    tt = np.clip(t, 0, 1)[..., None]
    glaze = glaze_top * (1 - tt) + glaze_low * tt
    # glaze drip line and unglazed clay foot
    drip = 0.74 + 0.04 * np.sin(u * 9 + 1.3) + 0.02 * np.sin(u * 23)
    clay = np.array([170, 142, 108.])
    col = np.where((t > drip)[..., None], clay, glaze)
    col = col * (0.52 + 0.58 * diff)[..., None] + (spec * 110)[..., None] * (t < drip)[..., None]
    speck = (rng.random((H, W)) > 0.993) * rng.uniform(20, 60, (H, W))
    col -= speck[..., None] * 0.6
    img = np.zeros((H, W, 4))
    img[..., :3] = col
    img[..., 3] = body * 255

    # rim + interior: outer ellipse, inner wall (back), liquid surface
    def ell(ax, ay, cyy):
        return ((x - cx) / ax) ** 2 + ((y - cyy) / ay) ** 2 <= 1
    outer = ell(a, a * persp, rim_y)
    inner = ell(a - 16, (a - 16) * persp, rim_y)
    liquid_cy, la = rim_y + 26, a - 44
    liquid = ell(la, la * persp, liquid_cy) & inner
    rimband = outer & ~inner
    img[rimband, :3] = np.array([246, 242, 232.]) * (0.85 + 0.15 * np.clip((cx - x[rimband]) / a, -1, 1))[:, None]
    img[rimband, 3] = 255
    wall = inner & ~liquid
    img[wall, :3] = np.array([214, 206, 186.]) * (0.75 + 0.25 * np.clip((y[wall] - rim_y) / (a * persp), 0, 1))[:, None]
    img[wall, 3] = 255
    orb = Image.open(orb_path).convert("RGBA")
    s = orb.width
    crop = orb.crop((int(s * 0.5 - s * 0.44 * 0.8), int(s * 0.5 - s * 0.44 * 0.8), int(s * 0.5 + s * 0.44 * 0.8), int(s * 0.5 + s * 0.44 * 0.8)))
    surf = np.array(crop.resize((int(2 * la), int(2 * la * persp)), Image.LANCZOS), float)
    y0, x0 = int(liquid_cy - la * persp), int(cx - la)
    hs, ws = surf.shape[:2]
    reg = liquid[y0:y0 + hs, x0:x0 + ws]
    img[y0:y0 + hs, x0:x0 + ws][reg, :3] = surf[reg][:, :3]
    img[y0:y0 + hs, x0:x0 + ws][reg, 3] = 255
    # rim highlight
    hl = outer & ~ell(a - 5, (a - 5) * persp, rim_y - 2) & (y < rim_y)
    img[hl, :3] = np.minimum(255, img[hl, :3] + 25)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGBA").filter(ImageFilter.SMOOTH)
    # contact shadow
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).ellipse([cx - a * 0.75, rim_y + depth - 18, cx + a * 0.75, rim_y + depth + 40], fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(26))
    shadow = Image.new("RGBA", (W, H), (20, 35, 25, 0)); shadow.putalpha(sh)
    out = Image.alpha_composite(shadow, im)
    feather(out, 0.04).save(os.path.join(OUT, name), optimize=True)


if __name__ == "__main__":
    which = sys.argv[1:] or ["landscape", "macro", "dust", "chawan"]
    if "landscape" in which:
        landscape("dunes.jpg")
    if "macro" in which:
        macro("panel.jpg")
    if "dust" in which:
        dustburst("dust_light.png", tint=(240, 236, 220), cols=((250, 247, 240), (217, 199, 159), (220, 230, 205), (190, 210, 160)))
    if "closing" in which:
        landscape("dunes_low.jpg", horizon=0.62, cam_h=0.5, seed=5)
    if "chawan" in which:
        chawan("chawan.png", os.path.join(OUT, "orb.png"))
    print("done", which)
