"""Giza cinematic edit v2 - refined cut + synced lyrics.

Editing language (deliberately restrained):
  * intro: fade from black + two slow dissolves
  * build / body: clean cuts on the beat, gentle drift only where a shot is static
  * ONE signature transition: speed-ramp into the pyramid apex -> soft light -> GEM facade (triangle match cut)
  * soft light bloom only on the three structural hits (drop 9.38, 14.95, 18.95)
  * ending: slow push on the mask, title, fade to black with the echo tail
"""
import subprocess, sys, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = sys.argv[1]
OUT = sys.argv[2]
PREVIEW = len(sys.argv) > 3 and sys.argv[3] == 'preview'
FPS = 30
W, H = (540, 960) if PREVIEW else (1080, 1920)
RAW = S + '/raw'
FONTS = S + '/fonts'
TM = ('zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,'
      'tonemap=mobius:param=0.5:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p')
DROP = 9.38
END = 25.2
TITLE_IN = 23.35


def sh(clip, src, t0, t1, **o):
    return dict(clip=clip, src=src, t0=t0, t1=t1, **o)


# lyric map in comments: what is heard over each block
SHOTS = [
    # ---- "Wait, what's that song that goes like..." : slow, monumental
    sh('IMG_5871.MOV', 2.0, 0.00, 1.79, sp=1.5, z=(1.0, 1.06), c=((0.5, 0.45), (0.5, 0.42)), fadein=0.45),
    sh('IMG_5894.MOV', 1.0, 1.79, 3.55, z=(1.12, 1.26), c=((0.52, 0.45), (0.55, 0.41)), tin=10, hires=True),
    # ---- instrumental build: clean cuts every two beats, motion carried shot to shot
    sh('IMG_5914.MOV', 0.4, 3.55, 4.44, z=(1.36, 1.40), c=((0.54, 0.44), (0.47, 0.44)), tin=8),
    sh('IMG_5921.MOV', 0.3, 4.44, 5.29, sp=1.3, z=(1.03, 1.03)),
    sh('IMG_5888.MOV', 0.1, 5.29, 6.13, z=(1.0, 1.03)),
    sh('IMG_5852.MOV', 1.4, 6.13, 6.99, sp=1.6),
    sh('IMG_5913.MOV', 0.25, 6.99, 7.87, sp=1.2, z=(1.04, 1.07)),
    sh('IMG_5886.MOV', 1.0, 7.87, 8.78, z=(1.30, 1.36), c=((0.62, 0.47), (0.62, 0.46))),
    # signature: speed-ramp into the apex, dissolving through soft light
    sh('IMG_5872.MOV', 0.5, 8.78, DROP, z=(1.0, 2.1), c=((0.5, 0.40), (0.5, 0.335)), ease='in', bloomout=0.6,
       hires=True),
    # ---- DROP  "I used to rule the world" : the pharaohs' hall
    sh('IMG_6051.MOV', 0.3, DROP, 10.52, z=(1.0, 1.05), c=((0.42, 0.5), (0.42, 0.48)), bloomin=0.6),
    sh('IMG_5982.MOV', 0.15, 10.52, 11.40, z=(1.0, 1.04)),
    sh('IMG_5990.MOV', 0.5, 11.40, 12.31, z=(1.0, 1.03)),
    sh('IMG_5986.MOV', 4.6, 12.31, 13.19, sp=1.5),
    # ---- "Seas would rise" : the solar boat, two angles, continuous motion
    sh('IMG_6050.MOV', 1.0, 13.19, 14.07, sp=2.2),
    sh('IMG_6046.MOV', 2.0, 14.07, 14.95, sp=1.5),
    # ---- "when I gave the word" (strongest hit) : the pyramids seen from the museum
    sh('IMG_6044.MOV', 0.4, 14.95, 15.84, z=(1.75, 1.84), c=((0.52, 0.35), (0.52, 0.35)), dehaze=0.7, bloomin=0.3),
    # ---- "Now in the morning" : out under the real thing
    sh('IMG_5853.MOV', 0.8, 15.84, 16.74, z=(1.08, 1.12), c=((0.45, 0.42), (0.45, 0.41))),
    sh('IMG_5855.MOV', 4.0, 16.74, 17.18, sp=1.4),
    # ---- "I sleep alone" : the tomb
    sh('IMG_6013.MOV', 0.0, 17.18, 18.07, sp=0.92, z=(1.08, 1.14), c=((0.5, 0.42), (0.5, 0.40))),
    sh('IMG_6004.MOV', 0.3, 18.07, 18.95, z=(1.0, 1.04)),
    sh('IMG_6010.MOV', 3.8, 18.95, 19.83, sp=4.0, z=(1.05, 1.10), c=((0.5, 0.52), (0.5, 0.48)), bloomin=0.3),
    # ---- "Sweep the streets" : the crowds
    sh('IMG_5983.MOV', 0.3, 19.83, 20.71, z=(1.0, 1.04)),
    sh('IMG_5998.MOV', 1.2, 20.71, 21.15, z=(1.04, 1.06)),
    # ---- "I used to own" : the treasures, the kingdom, the king
    sh('IMG_6007.MOV', 0.5, 21.15, 21.59, z=(1.0, 1.03)),
    sh('IMG_6002.MOV', 0.3, 21.59, 22.04, z=(1.06, 1.08)),
    sh('IMG_5873.MOV', 0.5, 22.04, 22.48, z=(1.15, 1.19), c=((0.5, 0.42), (0.5, 0.41)), hires=True),
    sh('IMG_6008.MOV', 0.2, 22.48, END, sp=0.9, z=(1.30, 1.55), c=((0.42, 0.62), (0.42, 0.635)), bloomin=0.2,
       ease='out', fadeout=1.2, title=True),
]

# Lyrics as displayed in the provided reference video (word onset times read from it at 10 fps).
# 13.3s: the reference renders "SEASON"; the sung words are "seas would", shown together at that onset.
LINES = [
    ([("Wait,", 0.00), ("what's", 0.90), ("that", 1.10), ("song", 1.30)], 1.65),
    ([("that", 1.70), ("goes", 1.90), ("like…", 2.30)], 3.20),
    ([("I", 9.40), ("used", 9.60), ("to", 10.00), ("rule", 10.50), ("the", 11.70), ("world", 12.00)], 13.25),
    ([("Seas would", 13.30), ("rise", 14.00)], 14.45),
    ([("when", 14.50), ("I", 14.70), ("gave", 14.90), ("the", 15.30), ("word", 15.50)], 15.95),
    ([("Now", 16.00), ("in", 16.20), ("the", 16.40), ("morning", 16.60)], 17.05),
    ([("I sleep", 17.10), ("alone", 18.40)], 19.75),
    ([("Sweep", 19.80), ("the", 20.40), ("streets", 20.70)], 21.15),
    ([("I", 21.20), ("used", 21.40), ("to", 21.90), ("own", 22.20)], 23.30),
]


def fr(t):
    return int(round(t * FPS))


def ease(x, kind='smooth'):
    x = min(max(x, 0.0), 1.0)
    if kind == 'in':
        return x ** 2.6
    if kind == 'out':
        return 1 - (1 - x) ** 2
    return x * x * (3 - 2 * x)


def decode(shot, n):
    sp = shot.get('sp', 1.0)
    lead = 12
    start = max(0.0, shot['src'] - lead / FPS * sp)
    shot['_pre'] = (shot['src'] - start) * FPS / sp
    span = (n + 2 * lead) / FPS * sp + 0.2
    if PREVIEW:
        sw, shh = 540, 960
    elif shot.get('hires'):
        sw, shh = 2160, 3840
    else:
        sw, shh = 1080, 1920
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{start:.3f}', '-t', f'{span:.3f}', '-i', f"{RAW}/{shot['clip']}",
           '-vf', f'{TM},scale={sw}:{shh}:flags=lanczos,fps={FPS}', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-']
    data = subprocess.run(cmd, capture_output=True).stdout
    k = len(data) // (sw * shh * 3)
    return np.frombuffer(data[:k * sw * shh * 3], np.uint8).reshape(k, shh, sw, 3)


def auto_gain(frames):
    m = frames[len(frames) // 2][::4, ::4].astype(np.float32).mean() / 255.0
    return min(0.30 / max(m, 0.05), 1.22) if m < 0.26 else 1.0


def grade(img, gain):
    f = img.astype(np.float32) / 255.0 * gain
    f = np.clip(f, 0, 1)
    f = f + 0.05 * (f - 0.5) * (1 - np.abs(2 * f - 1))  # gentle S
    y = (0.2126 * f[..., 0] + 0.7152 * f[..., 1] + 0.0722 * f[..., 2])[..., None]
    sat = np.abs(f - y).max(-1, keepdims=True)
    f = y + (f - y) * (1.0 + 0.08 * (1 - np.clip(sat * 2.5, 0, 1)))  # light vibrance
    return np.clip(f, 0, 1)


def camera(src, z, cx, cy):
    sh_, sw = src.shape[:2]
    z = max(z, 1.0)
    hw = 0.5 / z
    cx = min(max(cx, hw), 1 - hw)
    cy = min(max(cy, hw), 1 - hw)
    s = z * W / sw
    M = np.array([[s, 0, W / 2 - s * cx * sw], [0, s, H / 2 - s * cy * sh_]], np.float32)
    interp = cv2.INTER_AREA if s < 0.75 else cv2.INTER_CUBIC
    return cv2.warpAffine(src, M, (W, H), flags=interp, borderMode=cv2.BORDER_REFLECT)


def shot_frame(shot, frames, i):
    n = fr(shot['t1']) - fr(shot['t0'])
    sp = shot.get('sp', 1.0)
    si = int(min(max(round(shot['_pre'] + i * sp), 0), len(frames) - 1))
    p = min(max(i / max(n - 1, 1), 0), 1)
    e = ease(p, shot['ease']) if shot.get('ease') else p
    z0, z1 = shot.get('z', (1.0, 1.0))
    (cx0, cy0), (cx1, cy1) = shot.get('c', ((0.5, 0.5), (0.5, 0.5)))
    img = camera(frames[si], z0 + (z1 - z0) * e, cx0 + (cx1 - cx0) * e, cy0 + (cy1 - cy0) * e)
    f = grade(img, shot.setdefault('_gain', auto_gain(frames)))
    dh = shot.get('dehaze', 0.0)
    if dh:
        f = f ** (1 + dh)
        y = f.mean(-1, keepdims=True)
        f = np.clip(y + (f - y) * (1 + 0.5 * dh), 0, 1)
    # soft light bloom (a lifted, slightly softened exposure, not a hard white flash)
    b = 0.0
    if shot.get('bloomin') and i < 8:
        b = shot['bloomin'] * (1 - ease(i / 8, 'out'))
    if shot.get('bloomout') and i >= n - 6:
        b = shot['bloomout'] * ease((i - (n - 6) + 1) / 6, 'in')
    if b > 0:
        soft = cv2.GaussianBlur(f, (0, 0), 6 * W / 1080)
        f = f * (1 - b) + (1 - (1 - soft) * (1 - soft * 0.6)) * b
        f = f + (1 - f) * b * 0.55
    return f


# ---------------- typography ----------------
SC = W / 1080


def font(name, size):
    return ImageFont.truetype(name, max(8, int(size * SC)))


LYR_FONT = font(f'{FONTS}/CG-SemiBold.ttf', 60)
LYR_Y = int(1605 * SC)  # baseline area near the bottom, above the platform UI zone


def build_lines():
    out = []
    space = LYR_FONT.getlength(' ')
    for words, t_end in LINES:
        widths = [LYR_FONT.getlength(w) for w, _ in words]
        total = sum(widths) + space * (len(words) - 1)
        x = (W - total) / 2
        items = []
        for (w, t), wd in zip(words, widths):
            pad = int(24 * SC)
            ww, hh = int(wd) + 2 * pad, int(90 * SC)
            m = Image.new('L', (ww, hh), 0)
            ImageDraw.Draw(m).text((pad, int(12 * SC)), w, font=LYR_FONT, fill=255)
            glyph = np.asarray(m).astype(np.float32)[..., None] / 255.0
            tight = np.asarray(m.filter(ImageFilter.GaussianBlur(2.5 * SC))).astype(np.float32)[..., None] / 255.0
            wide = np.asarray(m.filter(ImageFilter.GaussianBlur(16 * SC))).astype(np.float32)[..., None] / 255.0
            shadow = np.clip(tight * 0.75 + wide * 2.2, 0, 1)
            items.append(dict(t=t, x=int(x) - pad, glyph=glyph, shadow=shadow))
            x += wd + space
        # feathered elliptical scrim behind the full line (local contrast, no visible box)
        x0l, x1l = int((W - total) / 2), int((W + total) / 2)
        sm = np.zeros((H, W), np.float32)
        cy_ = LYR_Y + int(26 * SC)
        cv2.ellipse(sm, (W // 2, cy_), (int((x1l - x0l) / 2 + 40 * SC), int(34 * SC)), 0, 0, 360, 1.0, -1)
        sm = cv2.GaussianBlur(sm, (0, 0), 30 * SC)
        sm = sm / max(sm.max(), 1e-6)
        ys = slice(max(cy_ - int(150 * SC), 0), min(cy_ + int(150 * SC), H))
        out.append(dict(t0=words[0][1], t1=t_end, items=items, scrim=sm[ys][..., None], ys=ys))
    return out


INK = np.array([247, 241, 229], np.float32) / 255.0


def draw_lyrics(f, tt, lines):
    for ln in lines:
        if not (ln['t0'] - 0.01 <= tt <= ln['t1'] + 0.01):
            continue
        out_a = 1.0 - ease((tt - (ln['t1'] - 0.20)) / 0.20) if tt > ln['t1'] - 0.20 else 1.0
        in_a = ease((tt - ln['t0']) / 0.2, 'out')
        reg = f[ln['ys']]
        lum = float(reg.mean())
        strength = 0.18 + 0.30 * min(max((lum - 0.25) / 0.45, 0), 1)  # adapt: more on bright scenes
        reg *= 1 - strength * ln['scrim'] * in_a * out_a
        for it in ln['items']:
            if tt < it['t']:
                continue
            k = ease((tt - it['t']) / 0.16, 'out')  # each word eases in with the sung syllable
            a = k * out_a
            if a <= 0:
                continue
            rise = int((1 - k) * 10 * SC)
            gh, gw = it['glyph'].shape[:2]
            y0 = LYR_Y - int(12 * SC) + rise
            x0 = it['x']
            xa, xb = max(x0, 0), min(x0 + gw, W)
            reg = f[y0:y0 + gh, xa:xb]
            g = it['glyph'][:, xa - x0:xb - x0]
            s = it['shadow'][:, xa - x0:xb - x0]
            reg *= (1 - 0.55 * s * a)  # soft legibility shadow
            reg[:] = reg * (1 - g * a * 0.95) + INK * g * a * 0.95
    return f


def title_layer():
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    big = font('/usr/share/fonts/opentype/inter/Inter-Thin.otf', 150)
    small = font(f'{FONTS}/CG-MediumItalic.ttf', 44)

    def spaced(text, fnt, y, track, fill):
        widths = [d.textlength(ch, font=fnt) for ch in text]
        total = sum(widths) + track * (len(text) - 1)
        x = (W - total) / 2
        for ch, w in zip(text, widths):
            d.text((x, y), ch, font=fnt, fill=fill)
            x += w + track

    spaced('GIZA', big, int(1400 * SC), 60 * SC, (255, 255, 255, 240))
    d.line([(int(475 * SC), int(1612 * SC)), (int(605 * SC), int(1612 * SC))], fill=(231, 196, 120, 230),
           width=max(1, int(2 * SC)))
    spaced('the Pyramids & the Grand Egyptian Museum', small, int(1640 * SC), 1 * SC, (245, 236, 218, 230))
    a = np.asarray(img).astype(np.float32) / 255.0
    return a[..., :3], a[..., 3:4]


def vignette():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    return (1 - 0.08 * np.clip((r - 0.5) / 0.5, 0, 1) ** 2)[..., None].astype(np.float32)


def main():
    total = fr(END)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264',
                            '-preset', 'veryfast' if PREVIEW else 'slow', '-crf', '23' if PREVIEW else '15',
                            '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709',
                            '-color_trc', 'bt709', '-color_range', 'tv', OUT], stdin=subprocess.PIPE)
    trgb, ta = title_layer()
    vig = vignette()
    lines = build_lines()
    cache = {}

    def get(k):
        if k not in cache:
            s = SHOTS[k]
            cache[k] = decode(s, fr(s['t1']) - fr(s['t0']))
            for old in list(cache):
                if old < k - 1:
                    del cache[old]
        return cache[k]

    k = 0
    for t in range(total):
        while k + 1 < len(SHOTS) and t >= fr(SHOTS[k + 1]['t0']):
            k += 1
        s = SHOTS[k]
        i = t - fr(s['t0'])
        f = shot_frame(s, get(k), i)
        # dissolves centred on the cut
        if s.get('tin') and i < s['tin'] // 2:
            d = s['tin']
            a = 0.5 + 0.5 * (i + 0.5) / (d / 2)
            pv = SHOTS[k - 1]
            f = shot_frame(pv, get(k - 1), t - fr(pv['t0'])) * (1 - a) + f * a
        if k + 1 < len(SHOTS) and SHOTS[k + 1].get('tin'):
            d = SHOTS[k + 1]['tin']
            j = t - fr(SHOTS[k + 1]['t0'])
            if -(d // 2) <= j < 0:
                a = 0.5 * (j + d / 2 + 0.5) / (d / 2)
                f = f * (1 - a) + shot_frame(SHOTS[k + 1], get(k + 1), j) * a
        f = f * vig
        tt = t / FPS
        if s.get('fadein'):
            f = f * ease(tt / s['fadein'], 'out')
        f = draw_lyrics(f, tt, lines)
        if s.get('title') and tt > TITLE_IN:
            a = ta * ease((tt - TITLE_IN) / 0.8)
            f = f * (1 - a) + trgb * a
        if s.get('fadeout'):
            fo = (END - tt) / s['fadeout']
            if fo < 1:
                f = f * ease(max(fo, 0))
        enc.stdin.write((np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        if t % 90 == 0:
            print(f'frame {t}/{total} shot {k} {s["clip"]}', flush=True)
    enc.stdin.close()
    enc.wait()


if __name__ == '__main__':
    main()
