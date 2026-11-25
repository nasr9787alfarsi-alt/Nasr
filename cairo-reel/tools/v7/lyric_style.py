"""Lyric style v7: small Ruqʿah line near the bottom, one phrase at a time.
size 58 px (1080 wide) ~ 21 pt on iPhone; baseline 0.79 H (inside Instagram's safe area, above the caption zone);
max width 0.70 W centred (clear of the right-hand Reels buttons); ivory with a gold hairline ornament;
readability from a soft graded bottom shade (max 22 %), not boxes or outlines; per-word fade + 6 px rise."""
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
FONT = '/tmp/claude-0/-home-user-Nasr/6cbdd08a-b868-51ac-a2ff-4cbd15ee33a7/scratchpad/fonts/ArefRuqaa-400.ttf'
SZ = 60; IVORY = np.float32([250, 244, 232]); GOLD = np.float32([226, 192, 128])
W, H = 1080, 1920
YY = np.arange(H, dtype=np.float32)[:, None]
def ss(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def shade(strength):
    g = np.clip((YY - 0.62 * H) / (0.38 * H), 0, 1) ** 1.6
    return 1 - 0.22 * strength * g
def layout(words, y=0.79):
    f = ImageFont.truetype(FONT, SZ, layout_engine=ImageFont.Layout.RAQM)
    out = []; gap = int(SZ * 0.30)
    ws = [(w, t, f.getlength(w, direction='rtl', language='ar')) for w, t in words]
    total = sum(x[2] for x in ws) + gap * (len(ws) - 1); xr = W / 2 + total / 2
    for w, t, ln in ws:
        im = Image.new('L', (int(ln) + 40, SZ * 2), 0); d = ImageDraw.Draw(im)
        d.text((int(ln) + 20, int(SZ * 1.35)), w, font=f, fill=255, anchor='rs', direction='rtl', language='ar')
        out.append(dict(m=np.asarray(im).astype(np.float32) / 255, x=int(xr - ln) - 20, y=int(y * H - SZ * 1.35), t=t))
        xr -= ln + gap
    return out, int(y * H), total
def draw(img, words, t, start, end, y=0.79, fade_out=0.5):
    items, by, total = layout(words, y)
    out = 1 - ss((t - end) / fade_out) if t > end else 1.0
    k = ss((t - start) / 0.5) * out
    img = img * shade(k)[..., None]
    a = np.zeros((H, W), np.float32); col = np.zeros((H, W, 3), np.float32)
    for it in items:
        p = ss((t - it['t']) / 0.40)
        if p <= 0: continue
        m = it['m'] * p * out; h, w = m.shape; yy = it['y'] + int(6 * (1 - p))
        a[yy:yy + h, it['x']:it['x'] + w] = np.maximum(a[yy:yy + h, it['x']:it['x'] + w], m)
    sh = cv2.GaussianBlur(a, (0, 0), 3) * 0.30
    img = img * (1 - sh[..., None]) * 1.0
    img = img * (1 - a[..., None]) + IVORY * a[..., None]
    lw = int(22 * k); yl = by - int(SZ * 1.05)          # gold hairline above the phrase
    if lw > 1: img[yl:yl + 2, W // 2 - lw:W // 2 + lw] = img[yl:yl + 2, W // 2 - lw:W // 2 + lw] * (1 - 0.85 * k) + GOLD * 0.85 * k
    return img
