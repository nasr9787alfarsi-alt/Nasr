import sys, os, subprocess, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from scipy.interpolate import PchipInterpolator
sys.path.insert(0, os.path.dirname(__file__))
from edl6 import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTER = f'{ROOT}/inter2'; FONTS = f'{ROOT}/fonts'
W, H = 1080, 1920
args = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = args[0] if args else f'{ROOT}/out7/master.mkv'
PREVIEW = '--preview' in sys.argv
STILLS = [float(x) for x in os.environ.get('STILLS', '').split(',') if x]
N = int(round(DUR * FPS))
def ss(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def eo(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3

# ---------------- time maps (extrapolate at the end slopes so transitions can overlap) ----------------
class Map:
    def __init__(self, pts):
        self.pts = pts; self.lo, self.hi = pts[0][0], pts[-1][0]
        self.f = PchipInterpolator([p[0] for p in pts], [p[1] for p in pts]) if len(pts) > 2 else None
        e = 1e-3
        self.s_lo = (self._in(self.lo + e) - self._in(self.lo)) / e if self.hi > self.lo else 0
        self.s_hi = (self._in(self.hi) - self._in(self.hi - e)) / e if self.hi > self.lo else 0
    def _in(self, t):
        if self.f is not None: return float(self.f(t))
        (x0, y0), (x1, y1) = self.pts
        return y0 + (y1 - y0) * (t - x0) / (x1 - x0) if x1 > x0 else y0
    def __call__(self, t):
        if t < self.lo: return self._in(self.lo) + (t - self.lo) * self.s_lo
        if t > self.hi: return self._in(self.hi) + (t - self.hi) * self.s_hi
        return self._in(t)
class ZMap(Map):
    def __call__(self, t): return self._in(min(max(t, self.lo), self.hi))
for s in SEGS:
    if s['keys'] is None: s['keys'] = [(s['a'], s['s0']), (s['b'], s['s0'] + (s['b'] - s['a']))]
    s['tmap'] = Map(s['keys']); s['zmap'] = ZMap(s['zoom'])

_fps = {}
def clip_fps(c):
    if c not in _fps:
        r = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate',
                                     '-of', 'default=nw=1:nk=1', f'{INTER}/{c}.mkv']).decode().split()[0]
        a, b = r.split('/'); _fps[c] = float(a) / float(b)
    return _fps[c]
def load(c, t0, t1):
    fps = clip_fps(c); t0 = max(0, t0); i0 = max(0, int(math.floor(t0 * fps)) - 1); n = int(math.ceil((t1 - t0) * fps)) + 5
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f'{i0 / fps:.5f}', '-i', f'{INTER}/{c}.mkv', '-frames:v', str(n),
                                   '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    return i0, fps, np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
def matrix(z, cx, cy):
    tx = W / 2 - z * cx * W; ty = H / 2 - z * cy * H
    tx = min(0.0, max(W * (1 - z), tx)); ty = min(0.0, max(H * (1 - z), ty))
    return np.float32([[z, 0, tx], [0, z, ty]])

class Seg:
    MARGIN = 0.40
    def __init__(self, s): self.s = s; self.data = None; self.gain = None
    def ensure(self):
        if self.data is None:
            s = self.s; ts = [s['tmap'](s['a'] - self.MARGIN + k * (s['b'] - s['a'] + 2 * self.MARGIN) / 30) for k in range(31)]
            self.data = load(s['clip'], min(ts) - 0.03, max(ts) + 0.08)
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
        st = s['tmap'](t); img = self.raw_at(st) * self.gain
        z = s['zmap'](t)
        if abs(z - 1) < 1e-4: return img
        return cv2.warpAffine(img, matrix(z, s['cx'], s['cy']), (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

STATS = {}
def shot_stats(o):
    s = o.s; img = o.raw_at(s['tmap']((s['a'] + s['b']) / 2)); small = cv2.resize(img, (108, 192), interpolation=cv2.INTER_AREA)
    y = small @ np.float32([0.2126, 0.7152, 0.0722]); m = (y > 30) & (y < 225)
    return float(y[m].mean()), small[m].mean(0)
KEEP_WARM = {'golden', 'home'}
def colour_gain(o):
    luma, rgb = STATS[o.s['clip']]; g = np.ones(3, np.float32) * np.clip((TARGET_LUMA / luma) ** 0.5, 0.90, 1.12)
    if o.s['name'] not in KEEP_WARM: g *= np.clip(((TARGET_RGB / TARGET_RGB[1]) / (rgb / rgb[1])) ** 0.4, 0.95, 1.05)
    return g.astype(np.float32)
SEGOBJ = [Seg(s) for s in SEGS]; BY = {o.s['name']: o for o in SEGOBJ}
for o in SEGOBJ:
    if o.s['clip'] not in STATS: o.ensure(); STATS[o.s['clip']] = shot_stats(o); o.free()
TARGET_LUMA = float(np.median([l for l, c in STATS.values()])); TARGET_RGB = np.median(np.array([c for l, c in STATS.values()]), 0).astype(np.float32)

def seg_index(t):
    for i, o in enumerate(SEGOBJ):
        if o.s['a'] - 1e-6 <= t < o.s['b'] - 1e-6: return i
    return len(SEGOBJ) - 1

def picture(t):
    i = seg_index(t); cur = SEGOBJ[i]
    # transition windows centred on each incoming cut
    for j in (i, i + 1):
        if j <= 0 or j >= len(SEGOBJ): continue
        inc = SEGOBJ[j]; kind = inc.s['tin']
        if kind[0] in ('dissolve', 'carry'):
            h = kind[1] / 2 / FPS; a = inc.s['a']
            if a - h <= t < a + h:
                w = ss((t - (a - h)) / (2 * h))
                if kind[0] == 'carry': w = (t - (a - h)) / (2 * h)       # linear: motion should not ease
                return SEGOBJ[j - 1].frame(t) * (1 - w) + inc.frame(t) * w
    return cur.frame(t)

# ---------------- finishing ----------------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rr = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
VIGNETTE = (1 - 0.09 * np.clip(rr - 0.3, 0, None) ** 1.2)[..., None].astype(np.float32)
def flare(img, t):
    a, p, e = FLARE
    if not (a <= t <= e): return img
    k = ss((t - a) / (p - a)) if t <= p else (1 - ss((t - p) / (e - p))) ** 1.5
    g = np.exp(-(((xx - 0.62 * W) / (0.55 * W)) ** 2 + ((yy - 0.38 * H) / (0.40 * H)) ** 2))[..., None] * np.float32([255, 214, 160])
    return 255 - (255 - img) * (1 - np.clip(g * k * 1.1, 0, 255) / 255)

# ---------------- typography ----------------
AMIRI = f'{FONTS}/Amiri-400r.ttf'; AMIRI_B = f'{FONTS}/Amiri-700.ttf'
def font(sz, path=AMIRI): return ImageFont.truetype(path, sz, layout_engine=ImageFont.Layout.RAQM)
IVORY = np.float32([255, 249, 238]); GOLD = np.float32([252, 222, 164])
def rtl_len(txt, f): return f.getlength(txt, direction='rtl', language='ar')
def sprite(txt, sz, path=AMIRI):
    f = font(sz, path); w = int(rtl_len(txt, f)) + 2; pad = 30; h = int(sz * 2.0)
    im = Image.new('L', (w + 2 * pad, h + 2 * pad), 0); d = ImageDraw.Draw(im)
    base = pad + int(sz * 1.30)
    d.text((pad + w, base), txt, font=f, fill=255, direction='rtl', language='ar', anchor='rs')
    return np.asarray(im).astype(np.float32) / 255, base, w, pad

def paste(col_acc, a_acc, mask, x, y, colour, alpha):
    h, w = mask.shape; x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0 or alpha <= 0: return
    m = mask[y0 - y:y1 - y, x0 - x:x1 - x] * alpha
    a_old = a_acc[y0:y1, x0:x1]
    a_new = m + a_old * (1 - m)
    col_acc[y0:y1, x0:x1] = (colour * m[..., None] + col_acc[y0:y1, x0:x1] * (a_old * (1 - m))[..., None]) / np.maximum(a_new, 1e-6)[..., None]
    a_acc[y0:y1, x0:x1] = a_new


SCH = f'{FONTS}/Scheherazade-400.ttf'; ENF = f'{FONTS}/Cormorant-400i.ttf'
AR_SZ = 92; AR_FINAL = 150; EN_SZ = 40; LEAD_AR = 1.22; GAP_EN = 0.62
FADE_IN = 0.45; FADE_OUT = 0.60; WORD_LEAD = 0.22
def en_sprite(txt, sz):
    f = ImageFont.truetype(ENF, sz); w = int(f.getlength(txt)) + 2; pad = 20
    im = Image.new('L', (w + 2 * pad, int(sz * 1.6) + 2 * pad), 0); d = ImageDraw.Draw(im)
    base = pad + int(sz * 1.1); d.text((pad, base), txt, font=f, fill=255, anchor='ls')
    return np.asarray(im).astype(np.float32) / 255, base, w, pad
GR = []
for lines, y in GROUPS:
    final = lines == [34]; sz = AR_FINAL if final else AR_SZ
    items = []; ens = []; yb = y * H; top = yb - sz; bottom = yb
    for li in lines:
        ws = [w for w in WORDS if w['line'] == li]
        if li == 34: ws = [dict(w='يا', s=56.05), dict(w='سلام', s=56.45)]
        sps = [(sprite(w['w'], sz, SCH), w) for w in ws]
        gap = int(sz * 0.28); total = sum(sp[0][2] for sp in sps) + gap * (len(sps) - 1)
        xr = W / 2 + total / 2
        for (mask, base, ww, pad), w in sps:
            xl = int(xr - ww)
            items.append(dict(mask=mask, x=xl - pad, y=int(yb) - base, on=V(w['s']) - WORD_LEAD, gold=final))
            xr = xl - gap
        m, base, ww, pad = en_sprite(EN[li], EN_SZ if not final else 44)
        ey = yb + sz * GAP_EN
        ens.append(dict(mask=m, x=int(W / 2 - ww / 2) - pad, y=int(ey) - base, on=V(ws[0]['s']) - 0.05))
        bottom = ey + 10; yb += sz * LEAD_AR + EN_SZ * 1.25
    start = min(it['on'] for it in items)
    GR.append(dict(items=items, ens=ens, start=start, final=final, box=(top - 40, bottom + 40),
                   last=max(LE[li] for li in lines) if not final else AUDIO_END))
for k, g in enumerate(GR):
    nxt = GR[k + 1]['start'] if k + 1 < len(GR) else 1e9
    g['end'] = min(V(g['last']) + 1.2, nxt - 0.05 - FADE_OUT) if not g['final'] else END - 0.5
    g['fade'] = FADE_OUT if not g['final'] else 0.45
    g['end'] = max(g['end'], V(g['last']) + 0.15)
    if g['end'] + g['fade'] > nxt - 0.03: g['fade'] = max(0.25, nxt - 0.03 - g['end'])
_blur = {}
def lyrics_layer(t):
    col = np.zeros((H, W, 3), np.float32); al = np.zeros((H, W), np.float32); used = False; scrim = 0.0; box = None
    for k, g in enumerate(GR):
        if t < g['start'] - 0.01 or t > g['end'] + g['fade']: continue
        out = 1 - ss((t - g['end']) / g['fade']) if t > g['end'] else 1.0
        for n_, it in enumerate(g['items']):
            age = t - it['on']
            if age <= 0: continue
            a = ss(age / (FADE_IN * (1.5 if g['final'] else 1.0))); m = it['mask']
            if a < 1:
                key = (k, n_, int(a * 8))
                if key not in _blur: _blur[key] = cv2.GaussianBlur(m, (0, 0), 0.1 + 1.5 * (1 - a))
                m = _blur[key]
            colr = GOLD if it['gold'] else IVORY
            paste(col, al, m, it['x'], it['y'], colr, a * out); used = True
        for it in g['ens']:
            age = t - it['on']
            if age <= 0: continue
            a = ss(age / 0.7) * 0.92
            paste(col, al, it['mask'], it['x'], it['y'], np.float32([246, 238, 224]), a * out); used = True
        s_ = ss((t - g['start']) / 0.5) * out; scrim = max(scrim, s_); box = g['box']
    if not used: return None
    return col, al, scrim, box

YY = np.arange(H, dtype=np.float32)[:, None]
def comp_text(img, layer, scrim=0.0, box=None):
    if layer is None: return img
    col, a = layer
    if scrim > 0 and box is not None:     # a soft horizontal band of shade behind the text block
        c = (box[0] + box[1]) / 2; h = (box[1] - box[0]) / 2 + 90
        band = np.exp(-np.maximum(np.abs(YY - c) - h * 0.55, 0) ** 2 / (2 * 70 ** 2)) * 0.30 * scrim
        img = img * (1 - band[..., None])
    sh = cv2.GaussianBlur(a, (0, 0), 14) * 0.50 + cv2.GaussianBlur(a, (0, 0), 2.5) * 0.32
    img = img * (1 - np.clip(sh, 0, 0.75)[..., None])
    return img * (1 - a[..., None]) + col * a[..., None]

_cache = {}
def title_layer(t):
    if t < SLAM - 0.01 or t > TITLE_OUT + 0.3: return None
    k = eo((t - SLAM) / 0.14); out = 1 - ss((t - TITLE_OUT) / 0.3) if t > TITLE_OUT else 1
    if 'title' not in _cache:
        im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
        d.text((W / 2, 0.44 * H), 'القاهرة', font=font(260, AMIRI_B), fill=255, direction='rtl', language='ar', anchor='ms')
        im2 = Image.new('L', (W, H), 0); d2 = ImageDraw.Draw(im2)
        d2.text((W / 2, 0.44 * H + 100), 'C   A   I   R   O', font=ImageFont.truetype(f'{FONTS}/Cormorant-500.ttf', 54), fill=235, anchor='ms')
        _cache['title'] = (np.asarray(im).astype(np.float32) / 255, np.asarray(im2).astype(np.float32) / 255)
    m1, m2 = _cache['title']; sc = 1 + 0.18 * (1 - k) + 0.04 * ss((t - SLAM) / 0.9)
    M = cv2.getRotationMatrix2D((W / 2, 0.42 * H), 0, sc)
    a1 = cv2.warpAffine(m1, M, (W, H)) * k * out; a2 = cv2.warpAffine(m2, M, (W, H)) * k * out
    a = np.maximum(a1, a2); col = np.where(a1[..., None] >= a2[..., None], IVORY, GOLD).astype(np.float32)
    return col * np.ones((H, W, 3), np.float32), a

def endcard_layer(t):
    t0 = V(AUDIO_END) + 0.35
    if t < t0: return None
    k = ss((t - t0) / 0.7)
    if 'end' not in _cache:
        im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
        d.text((W / 2, 0.30 * H + 250), 'C   A   I   R   O', font=ImageFont.truetype(f'{FONTS}/Cormorant-600.ttf', 60), fill=255, anchor='ms')
        _cache['end'] = np.asarray(im).astype(np.float32) / 255
    return np.broadcast_to(IVORY, (H, W, 3)).astype(np.float32), _cache['end'] * k

def merge(layers):
    layers = [l for l in layers if l is not None]
    if not layers: return None
    col, a = layers[0]
    for c2, a2 in layers[1:]:
        na = a2 + a * (1 - a2); col = (c2 * a2[..., None] + col * (a * (1 - a2))[..., None]) / np.maximum(na, 1e-6)[..., None]; a = na
    return col, a

import lyric_style as LS7
_raw_layout = LS7.layout; _lc = {}
def _memo_layout(words, y=0.79):
    key = (tuple(words), y)
    if key not in _lc: _lc[key] = _raw_layout(words, y)
    return _lc[key]
LS7.layout = _memo_layout
SEG_Y = {'parents': 0.88, 'human': 0.56}          # per-shot height, chosen to keep clear of faces
PH = []
for li in range(35):
    ws = [w for w in WORDS if w['line'] == li]
    if li == 34: ws = [dict(w='يا', s=56.05), dict(w='سلام', s=56.40)]
    PH.append(dict(words=[(w['w'], V(w['s']) - 0.12) for w in ws], start=V(ws[0]['s']) - 0.15,
                   last=V(LE[li]) if li < 34 else V(57.35)))
for k, ph in enumerate(PH):
    nxt = PH[k + 1]['start'] if k + 1 < len(PH) else END - 0.2
    ph['end'] = min(ph['last'] + 0.9, nxt - 0.05 - 0.35); ph['end'] = max(ph['end'], ph['last'] + 0.10)
    ph['fade'] = max(0.15, min(0.35, nxt - 0.05 - ph['end']))
    seg_name = SEGOBJ[seg_index(ph['start'] + 0.2)].s['name']
    ph['y'] = SEG_Y.get(seg_name, 0.79)
_lay = {}
def phrase(img, t):
    for k, ph in enumerate(PH):
        if ph['start'] - 0.01 <= t <= ph['end'] + ph['fade']:
            return LS7.draw(img, ph['words'], t, ph['start'], ph['end'], y=ph['y'], fade_out=ph['fade'])
    return img
def compose(t):
    img = picture(t)
    img = flare(img, t)
    lum = img @ np.float32([0.2126, 0.7152, 0.0722]); img = lum[..., None] + (img - lum[..., None]) * 1.05
    img = img * VIGNETTE
    img = comp_text(img, merge([title_layer(t), endcard_layer(t)]))
    img = phrase(img, t)
    if t > DUR - 0.7: img = img * (1 - ss((t - (DUR - 0.7)) / 0.66))
    return img

rng = np.random.default_rng(5)
def grain(img):
    g = cv2.resize(rng.normal(0, 2.0, (H // 2, W // 2)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    return np.clip(img + g[..., None], 0, 255).astype(np.uint8)

if STILLS:
    os.makedirs(f'{ROOT}/out7/stills', exist_ok=True)
    for t in STILLS:
        Image.fromarray(grain(compose(t))).save(f'{ROOT}/out7/stills/s_{t:06.2f}.png')
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
        if x.data is not None and x.s['b'] < t - 0.8: x.free()
    if n % 150 == 0: print(f'{n}/{N}', flush=True)
p.stdin.close(); p.wait(); print('done', OUT)
