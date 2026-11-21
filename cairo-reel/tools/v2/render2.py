import sys, os, subprocess, math, json, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.interpolate import PchipInterpolator
sys.path.insert(0, os.path.dirname(__file__))
from edl2 import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTER = f'{ROOT}/inter2'; FONTS = f'{ROOT}/fonts'
W, H = 1080, 1920
args = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = args[0] if args else f'{ROOT}/out2/master.mkv'
PREVIEW = '--preview' in sys.argv
T_FROM = float(os.environ.get('T_FROM', 0)); T_TO = float(os.environ.get('T_TO', DUR))
N = int(round(DUR * FPS))

def ss(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)

# ---------------- time / zoom maps ----------------
class Map:
    def __init__(self, pts):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        self.lo, self.hi = xs[0], xs[-1]
        self.f = PchipInterpolator(xs, ys) if len(pts) > 2 else None
        self.pts = pts
    def __call__(self, t):
        t = min(max(t, self.lo), self.hi)
        if self.f is not None: return float(self.f(t))
        (x0, y0), (x1, y1) = self.pts
        return y0 + (y1 - y0) * (t - x0) / (x1 - x0) if x1 > x0 else y0

for s in SEGS:
    if s['keys'] is None: s['keys'] = [(s['a'], s['s0']), (s['b'], s['s0'] + (s['b'] - s['a']))]
    s['tmap'] = Map(s['keys']); s['zmap'] = Map(s['zoom'])

_fps = {}
def clip_fps(c):
    if c not in _fps:
        r = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                     'stream=r_frame_rate', '-of', 'default=nw=1:nk=1', f'{INTER}/{c}.mkv']).decode().split()[0]
        a, b = r.split('/'); _fps[c] = float(a) / float(b)
    return _fps[c]

def load(c, t0, t1):
    fps = clip_fps(c)
    i0 = max(0, int(math.floor(min(t0, t1) * fps)) - 1); n = int(math.ceil(abs(t1 - t0) * fps)) + 5
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f'{i0 / fps:.5f}', '-i', f'{INTER}/{c}.mkv',
                                   '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    return i0, fps, np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)

def transform(z, cx, cy, vp=None):
    if vp is not None:
        tx = VP_TARGET[0] * W - z * vp[0] * W; ty = VP_TARGET[1] * H - z * vp[1] * H
    else:
        tx = W / 2 - z * cx * W; ty = H / 2 - z * cy * H
    tx = min(0.0, max(W * (1 - z), tx)); ty = min(0.0, max(H * (1 - z), ty))
    return np.float32([[z, 0, tx], [0, z, ty]])

class Seg:
    def __init__(self, s): self.s = s; self.data = None; self.gain = None
    def ensure(self):
        if self.data is None:
            s = self.s; ts = [s['tmap'](s['a'] + k * (s['b'] - s['a']) / 20) for k in range(21)]
            self.data = load(s['clip'], min(ts) - 0.02, max(ts) + 0.06)
    def free(self): self.data = None
    def raw_at(self, st):
        i0, fps, fr = self.data
        f = st * fps - i0; f = min(max(f, 0), len(fr) - 1)
        a = int(math.floor(f)); b = min(a + 1, len(fr) - 1); w = f - a
        if w < 0.1 or a == b: return fr[a].astype(np.float32)
        if w > 0.9: return fr[b].astype(np.float32)
        return fr[a].astype(np.float32) * (1 - w) + fr[b].astype(np.float32) * w
    def frame(self, t):
        self.ensure(); s = self.s
        if self.gain is None: self.gain = colour_gain(self)
        tq = t
        if s['step']: tq = s['a'] + math.floor((t - s['a']) * FPS / s['step'] + 1e-6) * s['step'] / FPS
        st = s['tmap'](tq); st2 = s['tmap'](tq + 1 / FPS)
        speed = abs(st2 - st) * FPS
        fps = self.data[1]
        if speed > 1.6 and not s['step']:           # real-frame motion blur (180 deg shutter)
            k = max(2, int(round(speed * fps / FPS * 0.5)))
            img = sum(self.raw_at(st + j * (st2 - st) * 0.5 / k) for j in range(k)) / k
        else:
            img = self.raw_at(st)
        img = img * self.gain
        z = s['zmap'](t); z2 = s['zmap'](t + 1 / FPS)
        if abs(z2 - z) / z > 0.012:                 # fast push: zoom motion blur
            acc = 0
            for j in range(4):
                zz = z + (z2 - z) * j / 8
                acc = acc + cv2.warpAffine(img, transform(zz, s['cx'], s['cy'], s['vp']), (W, H), flags=cv2.INTER_CUBIC)
            return acc / 4
        if abs(z - 1) < 1e-4 and s['vp'] is None: return img
        return cv2.warpAffine(img, transform(z, s['cx'], s['cy'], s['vp']), (W, H), flags=cv2.INTER_CUBIC,
                              borderMode=cv2.BORDER_REFLECT)

# ---------------- per-shot colour matching ----------------
STATS = {}
def shot_stats(o):
    s = o.s; st = s['tmap']((s['a'] + s['b']) / 2); img = o.raw_at(st)
    small = cv2.resize(img, (108, 192), interpolation=cv2.INTER_AREA)
    y = small @ np.float32([0.2126, 0.7152, 0.0722])
    m = (y > 30) & (y < 225)
    return float(y[m].mean()), small[m].mean(0)
KEEP_WARM = {'golden', 'station', 'vista'}
def colour_gain(o):
    s = o.s
    if s['clip'] not in STATS: STATS[s['clip']] = shot_stats(o)
    luma, rgb = STATS[s['clip']]
    g = np.ones(3, np.float32)
    g *= np.clip((TARGET_LUMA / luma) ** 0.5, 0.90, 1.12)          # half-way exposure match
    if s['name'] not in KEEP_WARM:
        ratio = rgb / rgb[1]; tr = TARGET_RGB / TARGET_RGB[1]
        g *= np.clip((tr / ratio) ** 0.4, 0.95, 1.05)               # gentle white-balance match
    return g.astype(np.float32)

SEGOBJ = [Seg(s) for s in SEGS]
BY = {o.s['name']: o for o in SEGOBJ}
# global targets from all shots (medians)
_l, _c = [], []
for o in SEGOBJ:
    if o.s['clip'] in STATS: continue
    if o.s['name'].startswith('flash'): continue
    o.ensure(); STATS[o.s['clip']] = shot_stats(o); o.free()
for k, (l, c) in STATS.items(): _l.append(l); _c.append(c)
TARGET_LUMA = float(np.median(_l)); TARGET_RGB = np.median(np.array(_c), 0).astype(np.float32)
print('colour targets', TARGET_LUMA, TARGET_RGB)

def seg_at(t):
    for o in SEGOBJ:
        if o.s['a'] - 1e-6 <= t < o.s['b'] - 1e-6: return o
    return SEGOBJ[-1]

# ---------------- graphics ----------------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rr = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
VIGNETTE = (1 - 0.10 * np.clip(rr - 0.3, 0, None) ** 1.2)[..., None].astype(np.float32)

def door_mask(t, expand):
    """doorway opening of IMG_6212, tracked through the live push-in, optionally expanded."""
    o = BY['door']; s = o.s; z = s['zmap'](t); M = transform(z, s['cx'], s['cy'])
    def P(x, y): return M[0, 0] * x * W + M[0, 2], M[1, 1] * y * H + M[1, 2]
    cx, apex = P(DOOR['cx'], DOOR['apex']); _, spring = P(DOOR['cx'], DOOR['spring'])
    _, sill = P(DOOR['cx'], DOOR['sill']); hw = DOOR['half_w'] * W * z
    # expand about the opening's centre
    mcx, mcy = cx, (apex + sill) / 2
    E = lambda x, y: (mcx + (x - mcx) * expand, mcy + (y - mcy) * expand)
    m = np.zeros((H, W), np.uint8)
    arc = [(cx + hw * math.cos(a), spring + (spring - apex) * math.sin(a))
           for a in np.linspace(math.pi, 2 * math.pi, 48)]
    poly = [E(cx - hw, sill)] + [E(*q) for q in arc] + [E(cx + hw, sill)]
    pts = np.array(poly, np.int32)
    cv2.fillPoly(m, [pts], 255, lineType=cv2.LINE_AA)
    return cv2.GaussianBlur(m, (0, 0), 1.2).astype(np.float32)[..., None] / 255

def leak(t):
    a, p, e = LEAK
    if t < a or t > e: return None, 0
    k = ss((t - a) / (p - a)) if t <= p else 1 - ss((t - p) / (e - p))
    ph = (t - a) / (e - a)
    g = np.zeros((H, W, 3), np.float32)
    for (x0, y0, dx, dy, rad, col) in [(-0.2, 0.30, 1.3, 0.20, 0.75, (255, 160, 80)),
                                        (1.1, 0.70, -1.0, -0.3, 0.60, (255, 110, 80)),
                                        (0.5, 0.5, 0.2, -0.2, 0.90, (255, 230, 190))]:
        cx = (x0 + dx * ph) * W; cy = (y0 + dy * ph) * H; R = rad * W
        g += np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (R * R) * 2.2)[..., None] * np.array(col, np.float32)
    return g, k

def F_(n, s): return ImageFont.truetype(f'{FONTS}/{n}.ttf', s)
TITLE_EVENTS = []      # (time, char) -> used by audio for typewriter strikes
for txt, font, size, x, y, col, t0, dt, track in TITLE:
    for i, ch in enumerate(txt):
        if ch != ' ': TITLE_EVENTS.append(round(t0 + i * dt, 4))
os.makedirs(f'{ROOT}/out2', exist_ok=True); json.dump({'type': TITLE_EVENTS}, open(f'{ROOT}/out2/events.json', 'w'))

def title_layer(t):
    if t < TITLE[0][6] - 0.01 or t > LEAK[2]: return None
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    out_k = 1 - ss((t - LEAK[0]) / (LEAK[1] - LEAK[0])) if t > LEAK[0] else 1
    for txt, font, size, x, y, col, t0, dt, track in TITLE:
        fnt = F_(font, size); cx = x
        for i, ch in enumerate(txt):
            ct = t0 + i * dt
            if t >= ct:   # typewriter: the glyph lands, with a 1-frame strike flash
                a = 1.0 if t - ct > 1 / FPS else 0.85
                d.text((cx, y + (2 if t - ct < 1 / FPS else 0)), ch, font=fnt, fill=col + (int(255 * a * out_k),))
            cx += fnt.getlength(ch) + track
    sh = L.split()[3].filter(ImageFilter.GaussianBlur(10))
    shadow = Image.new('RGBA', (W, H), (20, 12, 5, 0)); shadow.putalpha(sh.point(lambda v: int(v * 0.7)))
    return np.asarray(Image.alpha_composite(shadow, L)).astype(np.float32)

def over(img, layer):
    if layer is None: return img
    a = layer[..., 3:4] / 255
    return img * (1 - a) + layer[..., :3] * a

# ---------------- main loop ----------------
os.makedirs(os.path.dirname(OUT), exist_ok=True)
n0, n1 = int(round(T_FROM * FPS)), int(round(T_TO * FPS))
enc = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
if PREVIEW: enc += ['-vf', 'scale=540:960', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20']
else: enc += ['-c:v', 'libx264', '-preset', 'slow', '-crf', '8']
enc += ['-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', OUT]
p = subprocess.Popen(enc, stdin=subprocess.PIPE)
rng = np.random.default_rng(11)
for n in range(n0, n1):
    t = n / FPS
    o = seg_at(t); img = o.frame(t)
    for a, b, d0, d1 in DISSOLVE:
        if d0 <= t < d1:
            w = ss((t - d0) / (d1 - d0)); img = BY[a].frame(t) * (1 - w) + BY[b].frame(t) * w
    # through the doorway into Old Cairo
    if ARCH[0] <= t < ARCH[2] and t < BY['door'].s['b']:
        e = 1.0 if t < ARCH[1] else 1.0 + 7.0 * ss((t - ARCH[1]) / (ARCH[2] - ARCH[1])) ** 1.5
        m = door_mask(t, e) * ss((t - ARCH[0]) / 0.08)
        img = BY['door'].frame(t) * (1 - m) + BY['tilt'].frame(t) * m
    g, k = leak(t)
    if g is not None:
        img = 255 - (255 - img) * (1 - np.clip(g * k * 1.05, 0, 255) / 255)
        img = img * (1 + 0.30 * k)
    img = over(img, title_layer(t))
    if abs(t - HIT) < 0.5 / FPS: img = img * 1.12          # the release lands
    img = img * VIGNETTE
    gr = cv2.resize(rng.normal(0, 2.2, (H // 2, W // 2)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    img = img + gr[..., None]
    p.stdin.write(np.clip(img, 0, 255).astype(np.uint8).tobytes())
    for x in SEGOBJ:
        if x.data is not None and x.s['b'] < t - 0.6: x.free()
    if n % 90 == 0: print(f'{n}/{N}', flush=True)
p.stdin.close(); p.wait(); print('done', OUT)
