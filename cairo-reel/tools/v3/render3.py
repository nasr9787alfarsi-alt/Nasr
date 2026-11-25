import sys, os, subprocess, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.interpolate import PchipInterpolator
sys.path.insert(0, os.path.dirname(__file__))
from edl3 import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTER = f'{ROOT}/inter2'; FONTS = f'{ROOT}/fonts'
W, H = 1080, 1920
args = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = args[0] if args else f'{ROOT}/out3/master.mkv'
PREVIEW = '--preview' in sys.argv
STILLS = [float(x) for x in os.environ.get('STILLS', '').split(',') if x]
N = int(round(DUR * FPS))
def ss(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def eo(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3

class Map:
    def __init__(self, pts):
        self.pts = pts; self.lo, self.hi = pts[0][0], pts[-1][0]
        self.f = PchipInterpolator([p[0] for p in pts], [p[1] for p in pts]) if len(pts) > 2 else None
    def __call__(self, t):
        t = min(max(t, self.lo), self.hi)
        if self.f is not None: return float(self.f(t))
        (x0, y0), (x1, y1) = self.pts
        return y0 + (y1 - y0) * (t - x0) / (x1 - x0) if x1 > x0 else y0
for s in SEGS:
    if s['keys'] is None: s['keys'] = [(s['a'], s['s0']), (s['b'], s['s0'] + (s['b'] - s['a']))]
    s['tmap'] = Map(s['keys']); s['zmap'] = Map(s['zoom']); s['rmap'] = Map(s['roll']) if s['roll'] else None

_fps = {}
def clip_fps(c):
    if c not in _fps:
        r = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate',
                                     '-of', 'default=nw=1:nk=1', f'{INTER}/{c}.mkv']).decode().split()[0]
        a, b = r.split('/'); _fps[c] = float(a) / float(b)
    return _fps[c]
def load(c, t0, t1):
    fps = clip_fps(c); i0 = max(0, int(math.floor(t0 * fps)) - 1); n = int(math.ceil((t1 - t0) * fps)) + 5
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f'{i0 / fps:.5f}', '-i', f'{INTER}/{c}.mkv', '-frames:v', str(n),
                                   '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    return i0, fps, np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)

def matrix(z, cx, cy, vp=None, roll=0.0):
    if roll:
        M = cv2.getRotationMatrix2D((cx * W, cy * H), roll, z); M[0, 2] += W / 2 - cx * W; M[1, 2] += H / 2 - cy * H
        return M.astype(np.float32)
    if vp is not None: tx = VP_TARGET[0] * W - z * vp[0] * W; ty = VP_TARGET[1] * H - z * vp[1] * H
    else: tx = W / 2 - z * cx * W; ty = H / 2 - z * cy * H
    tx = min(0.0, max(W * (1 - z), tx)); ty = min(0.0, max(H * (1 - z), ty))
    return np.float32([[z, 0, tx], [0, z, ty]])

class Seg:
    def __init__(self, s): self.s = s; self.data = None; self.gain = None
    def ensure(self):
        if self.data is None:
            s = self.s; ts = [s['tmap'](s['a'] + k * (s['b'] - s['a']) / 24) for k in range(25)]
            self.data = load(s['clip'], min(ts) - 0.02, max(ts) + 0.08)
    def free(self): self.data = None
    def raw_at(self, st):
        i0, fps, fr = self.data; f = min(max(st * fps - i0, 0), len(fr) - 1)
        a = int(math.floor(f)); b = min(a + 1, len(fr) - 1); w = f - a
        if w < 0.12 or a == b: return fr[a].astype(np.float32)
        if w > 0.88: return fr[b].astype(np.float32)
        return fr[a].astype(np.float32) * (1 - w) + fr[b].astype(np.float32) * w
    def frame(self, t):
        self.ensure(); s = self.s
        if self.gain is None: self.gain = colour_gain(self)
        st = s['tmap'](t); st2 = s['tmap'](t + 1 / FPS); speed = abs(st2 - st) * FPS; fps = self.data[1]
        if speed > 1.5:
            k = max(2, int(round(speed * fps / FPS * 0.5)))
            img = sum(self.raw_at(st + j * (st2 - st) * 0.5 / k) for j in range(k)) / k
        else: img = self.raw_at(st)
        img = img * self.gain
        z = s['zmap'](t); r = s['rmap'](t) if s['rmap'] else 0.0
        z2 = s['zmap'](t + 1 / FPS)
        if abs(z2 - z) / z > 0.012:            # fast zoom: zoom blur
            acc = 0
            for j in range(4): acc = acc + cv2.warpAffine(img, matrix(z + (z2 - z) * j / 8, s['cx'], s['cy'], s['vp'], r), (W, H),
                                                          flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
            return acc / 4
        if abs(z - 1) < 1e-4 and s['vp'] is None and not r: return img
        return cv2.warpAffine(img, matrix(z, s['cx'], s['cy'], s['vp'], r), (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

# ---- per-shot exposure / white balance matching ----
STATS = {}
def shot_stats(o):
    s = o.s; img = o.raw_at(s['tmap']((s['a'] + s['b']) / 2)); small = cv2.resize(img, (108, 192), interpolation=cv2.INTER_AREA)
    y = small @ np.float32([0.2126, 0.7152, 0.0722]); m = (y > 30) & (y < 225)
    return float(y[m].mean()), small[m].mean(0)
KEEP_WARM = {'golden', 'station'}
def colour_gain(o):
    luma, rgb = STATS[o.s['clip']]; g = np.ones(3, np.float32) * np.clip((TARGET_LUMA / luma) ** 0.5, 0.90, 1.12)
    if o.s['name'] not in KEEP_WARM: g *= np.clip(((TARGET_RGB / TARGET_RGB[1]) / (rgb / rgb[1])) ** 0.4, 0.95, 1.05)
    return g.astype(np.float32)
SEGOBJ = [Seg(s) for s in SEGS]; BY = {o.s['name']: o for o in SEGOBJ}
for o in SEGOBJ:
    if o.s['clip'] in STATS or o.s['name'].startswith('flash') or o.s['name'] == 'hook': continue
    o.ensure(); STATS[o.s['clip']] = shot_stats(o); o.free()
for o in SEGOBJ:
    if o.s['clip'] not in STATS: o.ensure(); STATS[o.s['clip']] = shot_stats(o); o.free()
_main = [v for k, v in STATS.items()]
TARGET_LUMA = float(np.median([l for l, c in _main])); TARGET_RGB = np.median(np.array([c for l, c in _main]), 0).astype(np.float32)

def seg_at(t):
    for o in SEGOBJ:
        if o.s['a'] - 1e-6 <= t < o.s['b'] - 1e-6: return o
    return SEGOBJ[-1]

# ---- transitions ----
def dir_blur(img, L, horizontal=True):
    L = int(L)
    if L < 3: return img
    k = np.ones((1, L) if horizontal else (L, 1), np.float32) / L
    return cv2.filter2D(img, -1, k, borderType=cv2.BORDER_REFLECT)
def shift(img, dx):
    return cv2.warpAffine(img, np.float32([[1, 0, dx], [0, 1, 0]]), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
def whip(img, t):
    for tc, d in WHIPS:
        k = round((t - tc) * FPS)
        if -2 <= k <= 1:
            sh = {-2: 70, -1: 210, 0: -230, 1: -80}[k] * d; bl = {-2: 90, -1: 240, 0: 260, 1: 100}[k]
            return dir_blur(shift(img, sh), bl)
    return img
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rr = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
VIGNETTE = (1 - 0.09 * np.clip(rr - 0.3, 0, None) ** 1.2)[..., None].astype(np.float32)
def flare(img, t):
    a, p, e = FLARE
    if not (a <= t <= e): return img
    k = ss((t - a) / (p - a)) if t <= p else (1 - ss((t - p) / (e - p))) ** 1.5
    g = np.exp(-(((xx - 0.62 * W) / (0.55 * W)) ** 2 + ((yy - 0.38 * H) / (0.40 * H)) ** 2))[..., None] * np.float32([255, 214, 160])
    return 255 - (255 - img) * (1 - np.clip(g * k * 1.1, 0, 255) / 255)

# ---- typography ----
RUQ = f'{FONTS}/ArefRuqaa-700.ttf'
def font(sz, path=RUQ): return ImageFont.truetype(path, sz, layout_engine=ImageFont.Layout.RAQM)
INK = (255, 247, 234)
def word_sprite(txt, sz):
    f = font(sz); bb = f.getbbox(txt, direction='rtl', language='ar', anchor='ls')
    pad = 40; w = bb[2] - bb[0] + 2 * pad; h = int(sz * 1.9) + 2 * pad
    im = Image.new('L', (w, h), 0); d = ImageDraw.Draw(im)
    base = pad + int(sz * 1.25)
    d.text((pad - bb[0], base), txt, font=f, fill=255, direction='rtl', language='ar', anchor='ls')
    return np.asarray(im).astype(np.float32) / 255, base, bb[2] - bb[0]
SIZES = {'line': 130, 'big': 178, 'pen': 138, 'final': 215}
LAY = []   # per line: list of (sprite, x_left, baseline_y, onset_video, dur)
for L in LYRICS:
    sz = SIZES[L.get('style', 'line')]
    sprites = [word_sprite(w, sz) for w, _ in L['words']]
    gap = int(sz * 0.30); total = sum(sp[2] for sp in sprites) + gap * (len(sprites) - 1)
    if total > 0.86 * W:
        sz = int(sz * 0.86 * W / total); sprites = [word_sprite(w, sz) for w, _ in L['words']]
        gap = int(sz * 0.30); total = sum(sp[2] for sp in sprites) + gap * (len(sprites) - 1)
    x = (W + total) / 2; by = L['y'] * H; items = []
    for i, ((w, on), (mask, base, ww)) in enumerate(zip(L['words'], sprites)):
        x -= ww; dur = L.get('durs', [None] * 9)[i]
        items.append(dict(mask=mask, base=base, x=int(x) - 40, y=int(by - base), on=V(on), dur=dur)); x -= gap
    LAY.append(dict(items=items, end=V(L['end']), style=L.get('style', 'line'), start=V(L['words'][0][1])))

def paste_alpha(acc, mask, x, y):
    h, w = mask.shape; x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0: return
    acc[y0:y1, x0:x1] = np.maximum(acc[y0:y1, x0:x1], mask[y0 - y:y1 - y, x0 - x:x1 - x])

def lyric_alpha(t):
    acc = np.zeros((H, W), np.float32); used = False
    for Lz in LAY:
        if t < Lz['start'] - 0.05 or t > Lz['end'] + 0.35: continue
        out = 1 - ss((t - Lz['end']) / 0.30) if t > Lz['end'] else 1.0
        lift = -14 * ss((t - Lz['end']) / 0.30) if t > Lz['end'] else 0
        for it in Lz['items']:
            p = (t - (it['on'] - 0.04)) / (0.32 if Lz['style'] != 'final' else 0.55)
            if p <= 0: continue
            pe = eo(p); m = it['mask']
            if Lz['style'] == 'pen':     # the word is written right-to-left with the singer
                d = max(0.35, min(1.1, it['dur'] or 0.6)); q = min(1, (t - it['on'] + 0.04) / d)
                hh, ww = m.shape; edge = (1 - q) * ww
                ramp = np.clip((np.arange(ww) - edge + 30) / 60, 0, 1)[None, :]
                m = m * ramp; pe = min(1, p * 2)
            if Lz['style'] in ('big', 'final') and pe < 1:
                sc = 1 + 0.10 * (1 - pe); hh, ww = m.shape
                mm = cv2.resize(m, (int(ww * sc), int(hh * sc)), interpolation=cv2.INTER_LINEAR)
                ox = (mm.shape[1] - ww) // 2; oy = (mm.shape[0] - hh) // 2
                paste_alpha(acc, mm * pe * out, it['x'] - ox, int(it['y'] + 16 * (1 - pe) + lift) - oy)
            else:
                if pe < 1: m = cv2.GaussianBlur(m, (0, 0), 0.1 + 5 * (1 - pe))
                paste_alpha(acc, m * pe * out, it['x'], int(it['y'] + 18 * (1 - pe) + lift))
            used = True
    return acc if used else None

def text_over(img, a):
    if a is None: return img
    small = cv2.resize(a, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    scrim = cv2.resize(cv2.GaussianBlur(small, (0, 0), 16), (W, H)) ; scrim = np.clip(scrim * 2.2, 0, 1) * 0.30
    sh1 = cv2.GaussianBlur(a, (0, 0), 12) * 0.62; sh2 = cv2.GaussianBlur(a, (0, 0), 2.5) * 0.40
    img = img * (1 - scrim[..., None]); img = img * (1 - sh1[..., None]); img = img * (1 - sh2[..., None])
    return img * (1 - a[..., None]) + np.float32(INK) * a[..., None]

_title_cache = {}
def title_alpha(t):
    if t < SLAM - 0.01 or t > TITLE_OUT + 0.3: return None
    k = eo((t - SLAM) / 0.14); out = 1 - ss((t - TITLE_OUT) / 0.3) if t > TITLE_OUT else 1
    if 'm' not in _title_cache:
        a = np.zeros((H, W), np.float32)
        f = font(250); txt = 'القاهرة'
        bb = f.getbbox(txt, direction='rtl', language='ar', anchor='ms')
        im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
        d.text((W / 2, 0.44 * H), txt, font=f, fill=255, direction='rtl', language='ar', anchor='ms')
        fl = ImageFont.truetype(f'{FONTS}/Cormorant-500.ttf', 54); s = 'C   A   I   R   O'
        d.text((W / 2, 0.44 * H + 95), s, font=fl, fill=230, anchor='ms')
        _title_cache['m'] = np.asarray(im).astype(np.float32) / 255
    m = _title_cache['m']; sc = 1 + 0.18 * (1 - k) + 0.04 * ss((t - SLAM) / 0.9)
    mm = cv2.warpAffine(m, cv2.getRotationMatrix2D((W / 2, 0.42 * H), 0, sc), (W, H))
    return mm * k * out

def end_alpha(t):
    t0 = V(SONG_FREEZE) + 1.0
    if t < t0: return None
    k = ss((t - t0) / 0.6)
    if 'e' not in _title_cache:
        im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
        fl = ImageFont.truetype(f'{FONTS}/Cormorant-600.ttf', 64)
        d.text((W / 2, 0.30 * H + 135), 'C   A   I   R   O', font=fl, fill=255, anchor='ms')
        _title_cache['e'] = np.asarray(im).astype(np.float32) / 255
    return _title_cache['e'] * k

def pulse_zoom(t):
    z = 1.0
    for tp in PULSES:
        if 0 <= t - tp < 0.6: z += 0.065 * math.exp(-(t - tp) / 0.11)
    return z

def compose(t):
    o = seg_at(t); img = o.frame(t)
    for wt in WIPES:
        if abs(t - wt) < 0.5 / FPS:
            prev = [x for x in SEGOBJ if abs(x.s['b'] - wt) < 1e-3]
            if prev: img = img * 0.55 + prev[0].frame(wt - 1e-4) * 0.45
    img = whip(img, t)
    pz = pulse_zoom(t)
    if pz > 1.0005: img = cv2.warpAffine(img, cv2.getRotationMatrix2D((W / 2, H / 2), 0, pz), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    img = flare(img, t)
    lum = img @ np.float32([0.2126, 0.7152, 0.0722]); img = lum[..., None] + (img - lum[..., None]) * 1.06   # gentle vibrance
    img = img * VIGNETTE
    ta = title_alpha(t); la = lyric_alpha(t); ea = end_alpha(t)
    a = None
    for x in (ta, la, ea):
        if x is not None: a = x if a is None else np.maximum(a, x)
    img = text_over(img, a)
    if t > DUR - 0.7: img = img * (1 - ss((t - (DUR - 0.7)) / 0.66))
    return img

rng = np.random.default_rng(5)
def grain(img):
    g = cv2.resize(rng.normal(0, 2.0, (H // 2, W // 2)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    return np.clip(img + g[..., None], 0, 255).astype(np.uint8)

if STILLS:
    os.makedirs(f'{ROOT}/out3/stills', exist_ok=True)
    for t in STILLS:
        Image.fromarray(grain(compose(t))).resize((360, 640)).save(f'{ROOT}/out3/stills/s_{t:06.2f}.png')
        for x in SEGOBJ: x.free()
    print('stills done'); sys.exit()

os.makedirs(os.path.dirname(OUT), exist_ok=True)
enc = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
enc += (['-vf', 'scale=540:960', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20'] if PREVIEW else ['-c:v', 'libx264', '-preset', 'slow', '-crf', '8'])
enc += ['-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', OUT]
p = subprocess.Popen(enc, stdin=subprocess.PIPE)
for n in range(N):
    t = n / FPS
    p.stdin.write(grain(compose(t)).tobytes())
    for x in SEGOBJ:
        if x.data is not None and x.s['b'] < t - 0.6: x.free()
    if n % 150 == 0: print(f'{n}/{N}', flush=True)
p.stdin.close(); p.wait(); print('done', OUT)
