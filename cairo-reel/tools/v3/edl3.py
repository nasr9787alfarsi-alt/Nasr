"""YA DONYA - Cairo reel v3. Edit decision list.
Video time = song time + P (a 2.4 s sound-led intro built from Cairo's own street sounds precedes the song).
Lyric word onsets come from CTC forced alignment of the verified lyric text (lyr/align.json).
"""
FPS = 30
P = 2.40                     # song starts here (video time)
def V(s): return round(P + s, 4)

SONG_FREEZE = 44.14          # "استنّا" (wait!) - the image stops
END = V(47.60)
DUR = END

SEGS = []
def seg(name, clip, a, b, s0=None, keys=None, zoom=None, cx=0.5, cy=0.5, roll=None, vp=None):
    SEGS.append(dict(name=name, clip=clip, a=round(a, 4), b=round(b, 4), s0=s0, keys=keys,
                     zoom=zoom or [(a, 1.0), (b, 1.0)], cx=cx, cy=cy, roll=roll, vp=vp, step=None))
F = 1 / FPS

# ---------------- INTRO: the city counts us in (on the song's 16th-note grid, 129 bpm) ----------------
BEAT = 60 / 129.2
GRID16 = BEAT / 4
DOWNBEAT = V(0.065)                                   # first downbeat of the song
seg('hook', 'IMG_6220', 0.0, 0.465, s0=0.62, zoom=[(0.0, 1.16), (0.465, 1.10)], cy=0.40)
BURST = [('IMG_6211', 1.2), ('IMG_5976', 0.2), ('IMG_6227', 0.3), ('IMG_6204', 1.9), ('IMG_6221', 0.3),
         ('IMG_5968', 2.2), ('IMG_6226', 0.4), ('IMG_6182', 2.3), ('IMG_6222', 1.6), ('IMG_6228', 0.6),
         ('IMG_5960', 2.0), ('IMG_6181', 0.8)]
# accelerating: two 8ths, then 16ths
_t = [0.465, 0.465 + 2 * GRID16]
while len(_t) < len(BURST) + 1: _t.append(_t[-1] + GRID16)
BURST_TIMES = [round(round(x * FPS) / FPS, 4) for x in _t]
for i, (c, s) in enumerate(BURST):
    seg(f'flash{i}', c, BURST_TIMES[i], BURST_TIMES[i + 1], s0=s, zoom=[(BURST_TIMES[i], 1.08), (BURST_TIMES[i + 1], 1.12)])
SLAM = BURST_TIMES[-1]                                # title lands
TITLE_OUT = V(0.05)
FLARE = (SLAM - 0.03, SLAM + 0.02, SLAM + 0.30)

# ---------------- A1 : "he leaned, tossed his handkerchief, wrote on its edge: I'll come" ----------------
seg('title', 'IMG_5736', SLAM, V(2.28), keys=[(SLAM, 0.0), (V(2.28), 1.66)],
    zoom=[(SLAM, 1.20), (V(0.2), 1.13), (V(2.28), 1.15)], cy=0.40,
    roll=[(SLAM, 0.0), (V(0.22), 0.0), (V(2.02), -2.6), (V(2.28), -3.0)])          # the frame leans with "وميل"
seg('flowers', 'IMG_6204', V(2.28), V(3.26), s0=1.93 - 0.98)                        # motorbike fills the lens on "منديله"
seg('wood', 'IMG_5976', V(3.26), V(4.98), s0=0.0, zoom=[(V(3.26), 1.06), (V(4.98), 1.03)])
seg('books', 'IMG_5966', V(4.98), V(7.64), s0=0.3, zoom=[(V(4.98), 1.02), (V(7.64), 1.12)], cx=0.55, cy=0.55)
VP_TARGET = (0.46, 0.55)
seg('walk1', 'IMG_5961', V(7.64), V(8.52), s0=0.6, vp=(0.50, 0.47), zoom=[(V(7.64), 1.14), (V(8.52), 1.19)])
seg('walk2', 'IMG_6225', V(8.52), V(9.28), s0=0.5, vp=(0.45, 0.58), zoom=[(V(8.52), 1.15), (V(9.28), 1.20)])

# ---------------- A2 : the same words, now the city moves faster ----------------
seg('tilt', 'IMG_6227', V(9.28), V(10.44), keys=[(V(9.28), 0.0), (V(10.44), 2.70)])   # leans down from the minaret (ramp)
seg('pass', 'IMG_6208', V(10.44), V(11.36), s0=0.0)                                   # motorbike fills the lens on "منديله"
seg('riders', 'IMG_5968', V(11.36), V(12.76), s0=1.05, zoom=[(V(11.36), 1.03), (V(12.76), 1.07)])  # real horn at 2.07
seg('facade', 'IMG_6212', V(12.76), V(14.57), s0=1.30, zoom=[(V(12.76), 1.0), (V(14.57), 1.06)])  # SUV wipes in, clears
seg('minarets', 'IMG_6222', V(14.57), V(15.77), keys=[(V(14.57), 0.55), (V(15.77), 1.95)])
seg('cafe', 'IMG_5969', V(15.77), V(16.65), s0=0.8, zoom=[(V(15.77), 1.04), (V(16.65), 1.04)])
seg('riderspov', 'IMG_6223', V(16.65), V(17.67), s0=1.25, zoom=[(V(16.65), 1.05), (V(17.67), 1.12)])

# ---------------- CHORUS 1 : "I beg you, world" - the city opens up ----------------
seg('tall', 'IMG_6184', V(17.67), V(18.77), s0=1.2, zoom=[(V(17.67), 1.10), (V(17.95), 1.03), (V(18.77), 1.05)])
seg('above', 'IMG_5957', V(18.77), V(19.65), s0=1.15, zoom=[(V(18.77), 1.03), (V(19.65), 1.06)])
seg('world', 'IMG_6220', V(19.65), V(21.69), s0=2.10, zoom=[(V(19.65), 1.30), (V(20.35), 1.03), (V(21.69), 1.00)], cy=0.42)
seg('avenue', 'IMG_6219', V(21.69), V(23.33), s0=1.3, zoom=[(V(21.69), 1.04), (V(23.33), 1.10)], cy=0.55)
seg('sweep', 'IMG_6211', V(23.33), V(24.71), keys=[(V(23.33), 0.6), (V(24.71), 2.6)])
seg('people', 'IMG_6182', V(24.71), V(26.29), s0=1.35, zoom=[(V(24.71), 1.03), (V(26.29), 1.06)])
seg('stroll', 'IMG_5956', V(26.29), V(27.99), s0=0.86, zoom=[(V(26.29), 1.03), (V(27.99), 1.05)])  # red jacket wipes out

# ---------------- CHORUS 2 : the voice of Egypt, then "take us to joy" at full speed ----------------
seg('stone', 'IMG_6226', V(27.99), V(29.49), s0=0.2, zoom=[(V(27.99), 1.03), (V(29.49), 1.08)])
seg('mural', 'IMG_6221', V(29.49), V(31.15), s0=0.0, zoom=[(V(29.49), 1.06), (V(31.15), 1.06)], cy=0.42)
seg('crossing', 'IMG_5953', V(31.15), V(32.81), s0=0.0, zoom=[(V(31.15), 1.04), (V(32.81), 1.06)])
JOY = [V(32.81), V(33.30), V(33.79), V(34.27), V(34.78), V(35.27), V(35.59)]
seg('j_cyclist', 'IMG_5967', JOY[0], JOY[1], s0=2.45, zoom=[(JOY[0], 1.06), (JOY[1], 1.10)])
seg('j_flyover', 'IMG_5965', JOY[1], JOY[2], keys=[(JOY[1], 0.4), (JOY[2], 1.6)])            # 2.4x
seg('j_redcar', 'IMG_5973', JOY[2], JOY[3], s0=2.30, zoom=[(JOY[2], 1.04), (JOY[3], 1.08)])
seg('j_bread', 'IMG_5970', JOY[3], JOY[4], keys=[(JOY[3], 0.45), (JOY[4], 1.25)])           # fast pan
seg('j_bike', 'IMG_5964', JOY[4], JOY[5], s0=2.3, zoom=[(JOY[4], 1.08), (JOY[5], 1.14)])
seg('j_street', 'IMG_5962', JOY[5], JOY[6], s0=0.05, zoom=[(JOY[5], 1.05), (JOY[6], 1.08)])
seg('elders', 'IMG_5960', V(35.59), V(37.59), s0=1.6,
    zoom=[(V(35.59), 1.03), (V(37.59), 1.10)], cx=0.62, cy=0.62)                             # lands: warmth

# ---------------- OUTRO : "keep sadness far from us, and tell love: wait!" ----------------
seg('golden', 'IMG_6228', V(37.59), V(40.46), keys=[(V(37.59), 0.0), (V(40.46), 2.70)], zoom=[(V(37.59), 1.02), (V(40.46), 1.08)])
seg('station', 'IMG_6181', V(40.46), END,
    keys=[(V(40.46), 0.0), (V(SONG_FREEZE), 3.20), (END, 3.20)],
    zoom=[(V(40.46), 1.02), (V(SONG_FREEZE), 1.10), (V(SONG_FREEZE) + 0.30, 1.14), (END, 1.30)], cy=0.36)

# ---------------- transitions ----------------
WHIPS = [(V(2.28), -1), (V(15.77), +1), (V(23.33), -1), (V(34.27), +1)]    # (cut, direction of image motion)
WIPES = [V(3.26), V(11.36), V(12.76), V(27.99)]                             # blend across object wipes
PULSES = [V(17.67), V(32.81)]                                               # chorus entry / joy downbeat
VP_CUTS = [V(8.52)]

# ---------------- lyrics (song time onsets from forced alignment) ----------------
# style: 'line' default | 'pen' (written stroke reveal) | 'big' (wide moment) | 'final'
# y = vertical anchor (fraction of height) chosen per shot to keep clear of faces and key detail
LYRICS = [
    dict(words=[('وميل', 0.22)], end=2.10, y=0.74, style='big'),
    dict(words=[('وحدف', 2.28), ('منديله', 3.26)], end=4.70, y=0.20),
    dict(words=[('كاتب', 4.98), ('على', 6.36), ('طرفه', 6.94)], end=7.55, y=0.17, style='pen',
         durs=[1.26, 0.42, 0.54]),
    dict(words=[('أجيله', 7.64)], end=9.05, y=0.18),
    dict(words=[('وميل', 9.28)], end=10.30, y=0.80, style='big'),
    dict(words=[('وحدف', 10.44), ('منديله', 11.36)], end=12.60, y=0.20),
    dict(words=[('كاتب', 12.76), ('على', 14.57), ('طرفه', 15.07)], end=15.65, y=0.17, style='pen',
         durs=[1.27, 0.34, 0.50]),
    dict(words=[('أجيله', 15.77)], end=17.40, y=0.18),
    dict(words=[('وأمانة', 17.67), ('أمانة', 18.77)], end=19.55, y=0.17),
    dict(words=[('يا', 19.65), ('دنيا', 20.55), ('أمانة', 21.69)], end=23.15, y=0.16, style='big'),
    dict(words=[('تاخدينا', 23.33), ('للفرحة', 24.71), ('أمانة', 26.29)], end=27.80, y=0.18),
    dict(words=[('وأمانة', 27.99), ('يا', 29.49), ('دنيا', 30.01), ('أمانة', 31.15)], end=32.60, y=0.16),
    dict(words=[('تاخدينا', 32.81), ('للفرحة', 34.29), ('أمانة', 35.59)], end=37.35, y=0.18, style='big'),
    dict(words=[('وتخلّي', 37.59), ('الحزن', 38.69), ('بعيد', 39.53), ('عنّا', 40.46)], end=41.40, y=0.17),
    dict(words=[('وتقولي', 41.60), ('للحب', 42.82)], end=44.00, y=0.17),
    dict(words=[('استنّا', 44.14)], end=47.30, y=0.30, style='final'),
]
