"""Giza cinematic edit renderer.
Decodes each shot (HLG -> SDR mobius tonemap), applies subpixel camera moves,
beat-synced punches/flashes/whips, gentle grade, and pipes to x264."""
import subprocess, sys, os, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

S = sys.argv[1]
OUT = sys.argv[2]
PREVIEW = len(sys.argv) > 3 and sys.argv[3] == 'preview'
FPS = 30
W, H = 1080, 1920
if PREVIEW:
    W, H = 540, 960
RAW = S + '/raw'
TM = ('zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,'
      'tonemap=mobius:param=0.5:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p')

# beat grid from librosa analysis (136 BPM)
B = [0.07, 0.51, 0.95, 1.37, 1.79, 2.23, 2.67, 3.11, 3.55, 3.99, 4.44, 4.88, 5.29, 5.71, 6.13, 6.55,
     6.99, 7.43, 7.87, 8.31, 8.78, 9.22, 9.66, 10.08, 10.52, 10.96, 11.40, 11.84, 12.31, 12.75, 13.19,
     13.63, 14.07, 14.51, 14.95, 15.39, 15.84, 16.28, 16.74, 17.18, 17.62, 18.07, 18.51, 18.95, 19.39,
     19.83, 20.27, 20.71, 21.15, 21.59, 22.04, 22.48, 22.92]
DROP = 9.38
END = 25.2
H8 = lambda a, b: (a + b) / 2  # half-beat helper

# shot: clip, src_in, t0, t1, options
# z: (z0,z1) zoom; c: ((cx0,cy0),(cx1,cy1)) normalized centre; sp: speed
# punch: initial extra zoom that settles; flash: white flash strength; tin: transition in
def sh(clip, src, t0, t1, **o):
    return dict(clip=clip, src=src, t0=t0, t1=t1, **o)

SHOTS = [
    # ---- ACT I : THE DESERT (quiet intro -> build)
    sh('IMG_5871.MOV', 2.0, 0.00, 1.79, sp=1.5, z=(1.0, 1.10), c=((0.5, 0.45), (0.5, 0.40)), fadein=0.45),
    sh('IMG_5894.MOV', 1.0, 1.79, 3.55, z=(1.18, 1.38), c=((0.52, 0.45), (0.55, 0.40)), tin=('dissolve', 8)),
    sh('IMG_5914.MOV', 0.4, 3.55, 4.44, z=(1.40, 1.48), c=((0.44, 0.44), (0.56, 0.44)), tin=('dissolve', 6)),
    sh('IMG_5888.MOV', 0.1, 4.44, 5.29, z=(1.0, 1.06), c=((0.5, 0.5), (0.5, 0.5))),
    sh('IMG_5921.MOV', 0.3, 5.29, 6.13, sp=1.5, z=(1.05, 1.08)),
    sh('IMG_5852.MOV', 1.4, 6.13, 6.99, sp=1.6, z=(1.0, 1.05)),
    sh('IMG_5913.MOV', 0.25, 6.99, 7.87, sp=1.3, z=(1.04, 1.10)),
    sh('IMG_5853.MOV', 1.0, 7.87, 8.31, z=(1.10, 1.14), c=((0.45, 0.42), (0.45, 0.40)), punch=0.04),
    sh('IMG_5855.MOV', 4.0, 8.31, 8.78, sp=1.5, z=(1.0, 1.04), punch=0.04),
    sh('IMG_5886.MOV', 1.0, 8.78, 9.22, z=(1.30, 1.38), c=((0.62, 0.47), (0.62, 0.46)), punch=0.05),
    # accelerating zoom into the apex -> white-out into drop
    sh('IMG_5872.MOV', 0.5, 9.22, DROP, z=(1.0, 1.9), c=((0.5, 0.40), (0.5, 0.31)), ease='in', whiteout=0.85),
    # ---- ACT II : THE MUSEUM (drop) -- triangle match cut
    sh('IMG_6051.MOV', 0.3, DROP, 10.08, z=(1.0, 1.06), c=((0.42, 0.5), (0.42, 0.5)), punch=0.14, flash=0.9),
    sh('IMG_5983.MOV', 0.5, 10.08, 10.52, z=(1.0, 1.04), punch=0.06),
    sh('IMG_5982.MOV', 0.2, 10.52, 10.96, z=(1.0, 1.05), punch=0.06, whipout=True),
    sh('IMG_5986.MOV', 4.6, 10.96, 11.40, sp=2.0, z=(1.0, 1.04), whipin=True),
    sh('IMG_5990.MOV', 0.2, 11.40, 11.84, z=(1.0, 1.05), punch=0.06),
    # sphinx <-> sphinx match cut (museum / desert)
    sh('IMG_5987.MOV', 0.3, 11.84, 12.31, z=(1.12, 1.18), c=((0.52, 0.40), (0.52, 0.38)), punch=0.06),
    sh('IMG_5897.MOV', 1.0, 12.31, 12.75, z=(1.55, 1.62), c=((0.42, 0.40), (0.42, 0.39)), punch=0.06),
    # half-beat burst
    sh('IMG_5993.MOV', 0.3, 12.75, H8(12.75, 13.19), z=(1.05, 1.08)),
    sh('IMG_5991.MOV', 1.0, H8(12.75, 13.19), 13.19, z=(1.05, 1.08)),
    sh('IMG_5988.MOV', 0.1, 13.19, H8(13.19, 13.63), z=(1.05, 1.08), flash=0.3),
    sh('IMG_5992.MOV', 0.6, H8(13.19, 13.63), 13.63, z=(1.05, 1.08)),
    sh('IMG_6038.MOV', 0.3, 13.63, 14.07, z=(1.05, 1.10), c=((0.55, 0.42), (0.55, 0.42)), punch=0.06),
    sh('IMG_6050.MOV', 2.0, 14.07, 14.95, sp=2.6, z=(1.0, 1.06)),
    # strongest hit -> the pyramids seen from inside the museum
    sh('IMG_6044.MOV', 0.4, 14.95, 15.84, z=(1.75, 1.90), c=((0.52, 0.35), (0.52, 0.35)), flash=0.7, punch=0.10, dehaze=0.7,
       whipout=True),
    sh('IMG_6046.MOV', 3.3, 15.84, 16.28, sp=1.5, z=(1.0, 1.04), whipin=True),
    # gallery burst
    sh('IMG_5995.MOV', 0.4, 16.28, H8(16.28, 16.74), z=(1.05, 1.08)),
    sh('IMG_6021.MOV', 0.4, H8(16.28, 16.74), 16.74, z=(1.08, 1.10)),
    sh('IMG_6040.MOV', 0.5, 16.74, H8(16.74, 17.18), z=(1.12, 1.15)),
    sh('IMG_6025.MOV', 0.6, H8(16.74, 17.18), 17.18, z=(1.05, 1.08)),
    sh('IMG_6037.MOV', 0.5, 17.18, 17.62, z=(1.0, 1.05), punch=0.05),
    sh('IMG_6013.MOV', 0.0, 17.62, 18.07, z=(1.10, 1.16), c=((0.5, 0.42), (0.5, 0.40))),
    sh('IMG_6004.MOV', 0.5, 18.07, 18.51, z=(1.0, 1.05), punch=0.05),
    sh('IMG_6005.MOV', 1.0, 18.51, 18.95, z=(1.0, 1.05), punch=0.05),
    # big hit -> the mummy hologram scan (skeleton -> mummy)
    sh('IMG_6010.MOV', 3.8, 18.95, 19.83, sp=4.0, z=(1.05, 1.12), c=((0.5, 0.52), (0.5, 0.48)), flash=0.6,
       punch=0.10),
    sh('IMG_6007.MOV', 0.5, 19.83, 20.27, z=(1.0, 1.06), punch=0.05),
    # treasure burst
    sh('IMG_6006.MOV', 0.5, 20.27, H8(20.27, 20.71), z=(1.05, 1.08)),
    sh('IMG_6002.MOV', 0.3, H8(20.27, 20.71), 20.71, z=(1.10, 1.12)),
    sh('IMG_6027.MOV', 0.5, 20.71, H8(20.71, 21.15), z=(1.05, 1.08)),
    sh('IMG_6043.MOV', 0.3, H8(20.71, 21.15), 21.15, z=(1.05, 1.08)),
    sh('IMG_6024.MOV', 2.0, 21.15, 21.59, z=(1.05, 1.10), punch=0.05),
    sh('IMG_6041.MOV', 0.3, 21.59, 22.04, z=(1.0, 1.05), punch=0.05),
    # bookend: back to the pyramid
    sh('IMG_5873.MOV', 0.5, 22.04, 22.48, z=(1.15, 1.25), c=((0.5, 0.42), (0.5, 0.40)), punch=0.05),
    # finale: the golden mask emerges from darkness
    sh('IMG_6008.MOV', 0.2, 22.48, END, sp=0.9, z=(1.30, 1.62), c=((0.42, 0.62), (0.42, 0.64)), flash=0.35,
       punch=0.06, ease='out', fadeout=1.2, title=True),
]

LEAD = 10  # extra frames decoded before/after each shot for transitions


def fr(t):
    return int(round(t * FPS))


def decode(shot, nframes_needed):
    """Return list of source frames (float32 0-1, HxW at output res*1.0 of source portrait)."""
    sp = shot.get('sp', 1.0)
    start = max(0.0, shot['src'] - LEAD / FPS * sp)
    shot['_pre'] = (shot['src'] - start) * FPS / sp  # output frames available before t0
    span = (nframes_needed + 2 * LEAD) / FPS * sp + 0.2
    sw, shh = (1080, 1920) if not PREVIEW else (540, 960)
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{start:.3f}', '-t', f'{span:.3f}', '-i', f"{RAW}/{shot['clip']}",
           '-vf', f'{TM},scale={sw}:{shh}:flags=lanczos,fps={FPS}', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-']
    data = subprocess.run(cmd, capture_output=True).stdout
    n = len(data) // (sw * shh * 3)
    arr = np.frombuffer(data[:n * sw * shh * 3], np.uint8).reshape(n, shh, sw, 3)
    return arr


def ease(x, kind):
    x = min(max(x, 0.0), 1.0)
    if kind == 'in':
        return x ** 2.6
    if kind == 'out':
        return 1 - (1 - x) ** 2
    return x * x * (3 - 2 * x)  # smoothstep


def grade(img, gain):
    """Subtle, natural grade: exposure gain, gentle S-curve, light vibrance."""
    f = img.astype(np.float32) / 255.0
    f *= gain
    # gentle filmic S-curve around mid-grey (strength small)
    f = np.clip(f, 0, 1)
    f = f + 0.06 * (f - 0.5) * (1 - np.abs(2 * f - 1))
    y = (0.2126 * f[..., 0] + 0.7152 * f[..., 1] + 0.0722 * f[..., 2])[..., None]
    sat = np.abs(f - y).max(-1, keepdims=True)
    f = y + (f - y) * (1.0 + 0.10 * (1 - np.clip(sat * 2.5, 0, 1)))  # vibrance: boost low-sat only
    return np.clip(f, 0, 1)


VIG = None


def vignette():
    global VIG
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
        VIG = (1 - 0.10 * np.clip((r - 0.45) / 0.55, 0, 1) ** 2)[..., None].astype(np.float32)
    return VIG


def camera(src, z, cx, cy, shift_x=0.0, blur=0):
    sh_, sw = src.shape[:2]
    z = max(z, 1.0)
    # clamp centre so crop stays inside frame
    hw, hh = 0.5 / z, 0.5 / z
    cx = min(max(cx, hw), 1 - hw)
    cy = min(max(cy, hh), 1 - hh)
    s = z * W / sw
    M = np.array([[s, 0, W / 2 - s * cx * sw + shift_x * W], [0, s, H / 2 - s * cy * sh_]], np.float32)
    out = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    if blur > 1:
        k = np.zeros((1, blur), np.float32)
        k[:] = 1.0 / blur
        out = cv2.filter2D(out, -1, k)
    return out


def shot_frame(shot, frames, i):
    """i = output frame index relative to shot t0 (may be negative / beyond end for transitions)."""
    n = fr(shot['t1']) - fr(shot['t0'])
    sp = shot.get('sp', 1.0)
    si = shot['_pre'] + i * sp
    si = int(min(max(round(si), 0), len(frames) - 1))
    src = frames[si]
    p = (i / max(n - 1, 1))
    z0, z1 = shot.get('z', (1.0, 1.0))
    (cx0, cy0), (cx1, cy1) = shot.get('c', ((0.5, 0.5), (0.5, 0.5)))
    e = ease(p, shot.get('ease', 'linear')) if shot.get('ease') else min(max(p, 0), 1)
    z = z0 + (z1 - z0) * e
    cx = cx0 + (cx1 - cx0) * e
    cy = cy0 + (cy1 - cy0) * e
    pn = shot.get('punch', 0.0)
    if pn and 0 <= i < 7:
        z *= 1 + pn * (1 - ease(i / 7, 'out'))
    shift, blur = 0.0, 0
    if shot.get('whipout') and i >= n - 4:
        k = i - (n - 4) + 1
        shift, blur = -0.10 * k * k / 4, 12 * k + 1
    if shot.get('whipin') and i < 4:
        k = 4 - i
        shift, blur = 0.10 * k * k / 4, 12 * k + 1
    img = camera(src, z, cx, cy, shift, blur)
    g = shot.setdefault('_gain', auto_gain(frames))
    f = grade(img, g)
    dh = shot.get('dehaze', 0.0)
    if dh:
        f = f ** (1 + dh)
        y = f.mean(-1, keepdims=True)
        f = np.clip(y + (f - y) * (1 + 0.5 * dh), 0, 1)
    fl = shot.get('flash', 0.0)
    if fl and 0 <= i < 6:
        a = fl * (1 - i / 6) ** 1.5
        f = f + (1 - f) * a
    wo = shot.get('whiteout', 0.0)
    if wo and i >= n - 4:
        a = wo * ((i - (n - 4) + 1) / 4) ** 1.5
        f = f + (1 - f) * a
    return f


def auto_gain(frames):
    m = frames[len(frames) // 2].astype(np.float32).mean() / 255.0
    if m < 0.26:
        return min(0.30 / max(m, 0.05), 1.22)
    return 1.0


def title_layer():
    """Pre-render the end title as RGBA (premultiplied later)."""
    img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Thin.otf', 150)
    small = ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf', 30)
    def spaced(text, font, y, track, fill):
        widths = [d.textlength(ch, font=font) for ch in text]
        total = sum(widths) + track * (len(text) - 1)
        x = (1080 - total) / 2
        for ch, w in zip(text, widths):
            d.text((x, y), ch, font=font, fill=fill)
            x += w + track
    spaced('GIZA', big, 1420, 60, (255, 255, 255, 240))
    d.line([(470, 1630), (610, 1630)], fill=(231, 196, 120, 230), width=2)
    spaced('PYRAMIDS  ·  GRAND EGYPTIAN MUSEUM', small, 1665, 7, (245, 236, 218, 225))
    if PREVIEW:
        img = img.resize((W, H), Image.LANCZOS)
    a = np.asarray(img).astype(np.float32) / 255.0
    return a[..., :3], a[..., 3:4]


def main():
    total = fr(END)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow' if not PREVIEW else 'veryfast',
                            '-crf', '15' if not PREVIEW else '23', '-pix_fmt', 'yuv420p',
                            '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
                            '-color_range', 'tv', OUT], stdin=subprocess.PIPE)
    trgb, ta = title_layer()
    vig = vignette()
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
        # handle dissolve centred on cut: blend prev shot over first d/2 and next over last d/2
        if 'tin' in s and s['tin'][0] == 'dissolve':
            d = s['tin'][1]
            if i < d // 2:
                a = 0.5 + 0.5 * (i + 0.5) / (d / 2)
                prev = SHOTS[k - 1]
                fp = shot_frame(prev, get(k - 1), t - fr(prev['t0']))
                f = fp * (1 - a) + f * a
        if k + 1 < len(SHOTS) and 'tin' in SHOTS[k + 1] and SHOTS[k + 1]['tin'][0] == 'dissolve':
            d = SHOTS[k + 1]['tin'][1]
            j = t - fr(SHOTS[k + 1]['t0'])
            if -(d // 2) <= j < 0:
                a = 0.5 * (j + d / 2 + 0.5) / (d / 2)
                nx = SHOTS[k + 1]
                fn = shot_frame(nx, get(k + 1), j)
                f = f * (1 - a) + fn * a
        f = f * vig
        tt = t / FPS
        if s.get('fadein'):
            f = f * min(1.0, ease(tt / s['fadein'], 'out'))
        if s.get('title'):
            ta_t = ease((tt - 23.0) / 0.9, 'smooth') if tt > 23.0 else 0.0
            if ta_t > 0:
                a = ta * ta_t
                f = f * (1 - a) + trgb * a
        if s.get('fadeout'):
            fo = (END - tt) / s['fadeout']
            if fo < 1:
                f = f * ease(max(fo, 0), 'smooth')
        enc.stdin.write((np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        if t % 60 == 0:
            print(f'frame {t}/{total} shot {k} {s["clip"]}', flush=True)
    enc.stdin.close()
    enc.wait()


if __name__ == '__main__':
    main()
