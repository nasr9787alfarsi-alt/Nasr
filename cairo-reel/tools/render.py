import sys, os, subprocess, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from edl import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTER = f'{ROOT}/inter'; FONTS = f'{ROOT}/fonts'
W, H = 1080, 1920
OUT = sys.argv[1] if len(sys.argv) > 1 else f'{ROOT}/out/video_noaudio.mkv'
PREVIEW = '--preview' in sys.argv
N = int(round(DUR * FPS))

def ss(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def eo(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3

# ---------------- source access ----------------
_fps = {}
def clip_fps(c):
    if c not in _fps:
        r = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries',
                                     'stream=r_frame_rate', '-of', 'csv=p=0', f'{INTER}/{c}.mkv']).decode().strip().strip(',').split('\n')[0].strip(',')
        a, b = r.split('/'); _fps[c] = float(a) / float(b)
    return _fps[c]

def load(c, t0, t1):
    fps = clip_fps(c)
    i0 = max(0, int(math.floor(t0 * fps)) - 1); n = int(math.ceil((t1 - t0) * fps)) + 4
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{i0 / fps:.5f}', '-i', f'{INTER}/{c}.mkv', '-frames:v', str(n),
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.check_output(cmd)
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    return i0, fps, fr

def src_time(s, u):
    """output-relative time u -> source time."""
    T = s['b'] - s['a']
    if s['s1'] is None: return s['s0'] + u
    span = s['s1'] - s['s0']; x = u / T
    r = s['o'].get('ramp')
    if r == 'decel':   # fast -> slow : speed profile p = 1 - 0.75 x  (integral normalised)
        g = (x - 0.375 * x * x) / 0.625
    elif r == 'accel':
        g = (0.25 * x + 0.375 * x * x) / 0.625
    else: g = x
    return s['s0'] + span * g

class Seg:
    def __init__(self, s):
        self.s = s; self.data = None
    def ensure(self):
        if self.data is None:
            s = self.s; T = s['b'] - s['a']
            t0 = src_time(s, 0); t1 = src_time(s, T + 1 / FPS)
            self.data = load(s['clip'], t0, t1)
    def free(self): self.data = None
    def frame(self, t):
        self.ensure(); s = self.s; i0, fps, fr = self.data
        u = t - s['a']; T = s['b'] - s['a']
        st = src_time(s, u); st2 = src_time(s, u + 1 / FPS)
        speed = (st2 - st) * FPS
        def at(x):
            f = x * fps - i0; f = min(max(f, 0), len(fr) - 1)
            a = int(math.floor(f)); b = min(a + 1, len(fr) - 1); w = f - a
            if w < 0.08 or a == b: return fr[a].astype(np.float32)
            if w > 0.92: return fr[b].astype(np.float32)
            return fr[a].astype(np.float32) * (1 - w) + fr[b].astype(np.float32) * w
        if speed > 1.6:   # fast part of a ramp: 180deg-shutter motion blur from real frames
            k = max(2, int(round(speed * fps / FPS * 0.5)))
            img = sum(at(st + j * (st2 - st) * 0.5 / k) for j in range(k)) / k
        else:
            img = at(st)
        z = s['o'].get('zoom', (1.0, 1.0))
        zz = z[0] + (z[1] - z[0]) * ss(u / T) if T > 0 else z[0]
        return zoom(img, zz, s['o'].get('cx', 0.5), s['o'].get('cy', 0.5))

def zoom(img, z, cx=0.5, cy=0.5):
    if abs(z - 1) < 1e-4: return img
    # keep the zoomed window inside the frame
    px = cx * W; py = cy * H
    hw, hh = W / (2 * z), H / (2 * z)
    px = min(max(px, hw), W - hw); py = min(max(py, hh), H - hh)
    M = np.float32([[z, 0, W / 2 - z * px], [0, z, H / 2 - z * py]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

SEGOBJ = [Seg(s) for s in SEGS]
BYNAME = {s.s['name']: s for s in SEGOBJ}
def seg_at(t):
    for s in SEGOBJ:
        if s.s['a'] - 1e-6 <= t < s.s['b'] - 1e-6: return s
    return SEGOBJ[-1]

# ---------------- graphics ----------------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rr = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
VIGNETTE = (1 - 0.16 * np.clip(rr - 0.25, 0, None) ** 1.2)[..., None].astype(np.float32)

def arch_mask(scale):
    """Islamic arch window (rect + pointed/round top) centred, soft edge."""
    m = np.zeros((H, W), np.uint8)
    w = int(W * 0.46 * scale); h = int(H * 0.36 * scale)
    cx, cy = W // 2, int(H * 0.47)
    x0, x1 = cx - w // 2, cx + w // 2; ytop = cy - h // 2; ybot = cy + h // 2
    r = w // 2
    cv2.rectangle(m, (x0, ytop + r), (x1, ybot), 255, -1)
    cv2.ellipse(m, (cx, ytop + r), (r, int(r * 1.15)), 0, 180, 360, 255, -1)
    return cv2.GaussianBlur(m, (0, 0), 1.6).astype(np.float32)[..., None] / 255

def leak(t):
    a, p, e = LEAK
    if t < a or t > e: return None, 0
    k = ss((t - a) / (p - a)) if t <= p else 1 - ss((t - p) / (e - p))
    ph = (t - a) / (e - a)
    g = np.zeros((H, W, 3), np.float32)
    for (x0, y0, dx, dy, rad, col) in [(-0.2, 0.25, 1.3, 0.25, 0.75, (255, 150, 60)),
                                        (1.1, 0.75, -1.0, -0.3, 0.65, (255, 90, 70)),
                                        (0.5, 0.5, 0.2, -0.2, 0.9, (255, 225, 170))]:
        cx = (x0 + dx * ph) * W; cy = (y0 + dy * ph) * H; R = rad * W
        d = ((xx - cx) ** 2 + (yy - cy) ** 2) / (R * R)
        g += np.exp(-d * 2.2)[..., None] * np.array(col, np.float32)
    return g, k

# fonts
def F_(n, s): return ImageFont.truetype(f'{FONTS}/{n}.ttf', s)

def text_layer_title(t):
    """Typewriter title over the balcony shot (sky, upper left)."""
    t0, t1 = TITLE_T
    if t < t0 - 0.01 or t > LEAK[2]: return None
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    out_k = 1 - ss((t - LEAK[0]) / (LEAK[1] - LEAK[0] + 0.05)) if t > LEAK[0] else 1
    lines = [  # text, font, x, y, colour, start time, per-char interval, tracking
        ('VISUAL DIARY', F_('Cormorant-600', 66), 74, 222, (252, 248, 240), t0, 0.045, 5),
        ('from', F_('Cormorant-400i', 48), 78, 300, (252, 248, 240), t0 + 0.62, 0.05, 1),
        ('Cairo', F_('Playfair-400', 150), 66, 330, (238, 198, 122), t0 + 0.80, 0.07, 2),
        ('30.0444° N  ·  31.2357° E', F_('Inter-300', 24), 80, 526, (248, 244, 236), t0 + 1.05, 0.012, 2),
    ]
    for txt, font, x, y, col, ts, dt, track in lines:
        cx = x
        for i, ch in enumerate(txt):
            ct = ts + i * dt; a = ss((t - ct) / 0.10)
            if a > 0:
                d.text((cx, y), ch, font=font, fill=col + (int(255 * a * out_k),))
            cx += font.getlength(ch) + track
    sh = L.split()[3].filter(ImageFilter.GaussianBlur(10))
    shadow = Image.new('RGBA', (W, H), (20, 12, 5, 0)); shadow.putalpha(sh.point(lambda v: int(v * 0.7)))
    return Image.alpha_composite(shadow, L)

_end_cache = {}
def text_layer_end(t):
    if t < CARD[0]: return None
    k = ss((t - CARD[0]) / 0.45) * (1 - ss((t - CARD[1]) / (CARD[2] - CARD[1] - 2 / FPS)))
    key = int(k * 40)
    if key not in _end_cache:
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        fa = ImageFont.truetype(f'{FONTS}/Amiri-700.ttf', 170, layout_engine=ImageFont.Layout.RAQM)
        txt = 'القاهرة'
        bb = d.textbbox((0, 0), txt, font=fa, direction='rtl', language='ar')
        d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], 700), txt, font=fa, fill=(250, 246, 238, int(255 * k)),
               direction='rtl', language='ar')
        fl = F_('Cormorant-500', 50); s = 'C A I R O'
        tw = fl.getlength(s); d.text(((W - tw) / 2, 985), s, font=fl, fill=(236, 196, 120, int(255 * k)))
        fs = F_('Inter-300', 26); s2 = 'VISUAL DIARY'
        s2 = '   '.join(s2.split(' ')); tw = fs.getlength(s2)
        d.text(((W - tw) / 2, 1062), s2, font=fs, fill=(245, 240, 230, int(200 * k)))
        sh = L.split()[3].filter(ImageFilter.GaussianBlur(14))
        shadow = Image.new('RGBA', (W, H), (10, 6, 2, 0)); shadow.putalpha(sh.point(lambda v: int(v * 0.6)))
        _end_cache[key] = np.asarray(Image.alpha_composite(shadow, L)).astype(np.float32)
    return _end_cache[key]

def over(img, layer):
    if layer is None: return img
    if isinstance(layer, Image.Image): layer = np.asarray(layer).astype(np.float32)
    a = layer[..., 3:4] / 255
    return img * (1 - a) + layer[..., :3] * a

# ---------------- main loop ----------------
os.makedirs(os.path.dirname(OUT), exist_ok=True)
enc = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
       '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast' if PREVIEW else 'slow', '-crf', '20' if PREVIEW else '8',
       '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', OUT]
if PREVIEW: enc[enc.index('-i') + 2:enc.index('-i') + 2] = ['-vf', 'scale=540:960']
p = subprocess.Popen(enc, stdin=subprocess.PIPE)
rng = np.random.default_rng(7)
for n in range(N):
    t = n / FPS
    s = seg_at(t)
    img = s.frame(t)
    # dissolve hold -> title
    a, b, d0, d1 = DISSOLVE
    if d0 <= t < d1:
        w = ss((t - d0) / (d1 - d0))
        img = BYNAME[a].frame(t) * (1 - w) + BYNAME[b].frame(t) * w
    # 2-frame blend across motion wipes (makes the cut ride the passing object)
    for wt in WIPES:
        if abs(t - wt) < 0.5 / FPS:
            prev = [x for x in SEGOBJ if abs(x.s['b'] - wt) < 1e-3][0]
            img = img * 0.55 + prev.frame(wt - 1e-4) * 0.45
    # arch reveal in the silence
    if ARCH[0] <= t < ARCH[2]:
        if t < ARCH[1]: sc = 0.92 + 0.08 * ss((t - ARCH[0]) / (ARCH[1] - ARCH[0]))
        else: sc = 1.0 + 2.6 * ss((t - ARCH[1]) / (ARCH[2] - ARCH[1])) ** 1.6
        fade = ss((t - ARCH[0]) / 0.12)
        img = img * arch_mask(sc) * fade
    # light leak transition
    g, k = leak(t)
    if g is not None:
        img = 255 - (255 - img) * (1 - np.clip(g * k * 1.05, 0, 255) / 255)   # screen
        img = img * (1 + 0.35 * k)
    # titles
    img = over(img, text_layer_title(t))
    # finale: slight punch on the hit
    if t >= END_T and t < END_T + 0.12:
        img = img * (1 + 0.25 * (1 - (t - END_T) / 0.12))
    if t >= TO_BLACK[0]: img = img * (1 - ss((t - TO_BLACK[0]) / (TO_BLACK[1] - TO_BLACK[0])))
    img = over(img, text_layer_end(t))
    # finishing: vignette + fine monochrome grain
    img = img * VIGNETTE
    gr = cv2.resize(rng.normal(0, 3.2, (H // 2, W // 2)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    img = img + gr[..., None]
    p.stdin.write(np.clip(img, 0, 255).astype(np.uint8).tobytes())
    for o in SEGOBJ:   # free memory of finished segments
        if o.data is not None and o.s['b'] < t - 0.6: o.free()
    if n % 60 == 0: print(f'{n}/{N}', flush=True)
p.stdin.close(); p.wait(); print('done', OUT)
