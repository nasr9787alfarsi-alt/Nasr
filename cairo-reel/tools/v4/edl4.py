"""YA DONYA v4 - motion-led re-edit. The opening (hook + burst + title) is kept from v3.
Video time = song time + P. Word onsets are the CTC-aligned vocal onsets (lyr/align.json).
Transition kinds: 'cut' (straight), 'land' (same clip continues - invisible), 'dissolve' (frames),
'carry' (direction-matched cut with a 3-frame motion-blended overlap).
Every cut lists its reason.
"""
FPS = 30
P = 2.40
def V(s): return round(P + s, 4)
SONG_FREEZE = 44.14
END = V(47.60)
DUR = END
F = 1 / FPS

SEGS = []
def seg(name, clip, a, b, s0=None, keys=None, zoom=None, cx=0.5, cy=0.5, tin=('cut',), why=''):
    SEGS.append(dict(name=name, clip=clip, a=round(a, 4), b=round(b, 4), s0=s0, keys=keys,
                     zoom=zoom or [(a, 1.0), (b, 1.0)], cx=cx, cy=cy, tin=tin, why=why, vp=None, roll=None, step=None))

# ---------------- OPENING (kept) ----------------
BEAT = 60 / 129.2; GRID16 = BEAT / 4
seg('hook', 'IMG_6220', 0.0, 0.465, s0=0.62, zoom=[(0.0, 1.16), (0.465, 1.10)], cy=0.40)
BURST = [('IMG_6211', 1.2), ('IMG_5976', 0.2), ('IMG_6227', 0.3), ('IMG_6204', 1.9), ('IMG_6221', 0.3),
         ('IMG_5968', 2.2), ('IMG_6226', 0.4), ('IMG_6182', 2.3), ('IMG_6222', 1.6), ('IMG_6228', 0.6),
         ('IMG_5960', 2.0), ('IMG_5736', 0.0)]          # last flash = the balcony itself: the burst lands on it
_t = [0.465, 0.465 + 2 * GRID16]
while len(_t) < len(BURST) + 1: _t.append(_t[-1] + GRID16)
BURST_TIMES = [round(round(x * FPS) / FPS, 4) for x in _t]
for i, (c, s) in enumerate(BURST):
    seg(f'flash{i}', c, BURST_TIMES[i], BURST_TIMES[i + 1], s0=s, zoom=[(BURST_TIMES[i], 1.08), (BURST_TIMES[i + 1], 1.12)])
SLAM = BURST_TIMES[-1]
TITLE_OUT = V(0.05)
FLARE = (SLAM - 0.03, SLAM + 0.02, SLAM + 0.30)

# ---------------- HANDOFF: the balcony continues from its own flash; the push never reverses ----------------
seg('balcony', 'IMG_5736', SLAM, V(2.28), keys=[(SLAM, 0.10), (V(2.28), 1.60)],
    zoom=[(SLAM, 1.12), (V(0.6), 1.145), (V(2.28), 1.17)], cy=0.42, tin=('land',),
    why='same shot as the last flash: the burst decelerates into it, push-in continues at a slower rate')

# ---------------- VERSE A1 : from the balcony down into the street ----------------
seg('walk', 'IMG_5973', V(2.28), V(4.98), s0=0.40, zoom=[(V(2.28), 1.04), (V(4.98), 1.06)], tin=('dissolve', 6),
    why='«وحدف»: we look down at the street, then we are walking in it - forward push carries into forward walk')
seg('books', 'IMG_5966', V(4.98), V(7.64), s0=0.30, zoom=[(V(4.98), 1.02), (V(7.64), 1.08)], cx=0.55, cy=0.55,
    why='«كاتب» (he wrote) on the song\'s strongest accent: the walk arrives at the book kiosk')
seg('walk2', 'IMG_5961', V(7.64), V(9.28), s0=0.60, zoom=[(V(7.64), 1.04), (V(9.28), 1.07)],
    why='«أجيله» (I\'ll come): walking again')

# ---------------- VERSE A2 : one leftward current ----------------
seg('tilt', 'IMG_6227', V(9.28), V(11.94), s0=0.10, tin=('dissolve', 5),
    why='«وميل» (he leaned): the camera leans down the minaret; image drifts left')
seg('riders', 'IMG_6208', V(11.94), V(12.76), s0=0.25, tin=('carry', 3),
    why='leftward drift hands over to riders moving left')
seg('ornate', 'IMG_6211', V(12.76), V(15.77), s0=0.80, tin=('carry', 3),
    why='riders exit frame-left on «كاتب»; the pan keeps moving left')
seg('facade', 'IMG_6212', V(15.77), V(17.67), s0=1.60,
    why='«أجيله»: a still frame to breathe before the chorus; a car crosses rightwards into it')

# ---------------- CHORUS 1 : the city opens ----------------
seg('square', 'IMG_6220', V(17.67), V(19.65), s0=1.00, zoom=[(V(17.67), 1.04), (V(19.65), 1.07)], cy=0.42, tin=('carry', 3),
    why='the car crossing right carries into traffic moving right; the hook\'s square returns on the downbeat')
seg('downtown', 'IMG_5737', V(19.65), V(21.69), keys=[(V(19.65), 0.02), (V(21.69), 1.10)], zoom=[(V(19.65), 1.02), (V(21.69), 1.08)],
    why='«يا دنيا» (oh world): back up on the balcony, looking the other way - the whole avenue opens')
seg('avenue', 'IMG_6219', V(21.69), V(23.33), s0=1.60, zoom=[(V(21.69), 1.04), (V(23.33), 1.08)], cy=0.55,
    why='«أمانة»: minaret at the vanishing point, same depth axis as downtown')
seg('ride', 'IMG_6223', V(23.33), V(24.71), s0=0.60, zoom=[(V(23.33), 1.05), (V(24.71), 1.10)],
    why='«تاخدينا» (take us): moving forward down the avenue axis')
seg('stroll', 'IMG_5968', V(24.71), V(26.29), s0=1.00, zoom=[(V(24.71), 1.03), (V(26.29), 1.06)],
    why='«للفرحة» (to joy): two friends on a motorbike, their horn honks on the line')
seg('stone', 'IMG_6226', V(26.29), V(27.99), s0=0.30, zoom=[(V(26.29), 1.03), (V(27.99), 1.08)], tin=('dissolve', 8),
    why='«أمانة»: dissolve into old Cairo as the chorus resolves')

# ---------------- CHORUS 2 : the voice of Egypt, then joy ----------------
seg('crowd', 'IMG_6182', V(27.99), V(29.49), s0=1.00, zoom=[(V(27.99), 1.03), (V(29.49), 1.05)],
    why='chorus downbeat: a man walks into the street')
seg('mural', 'IMG_6221', V(29.49), V(31.15), s0=0.10, zoom=[(V(29.49), 1.05), (V(31.15), 1.05)], cy=0.42,
    why='«يا دنيا»: Umm Kulthum - the pan drifts left')
seg('flowers', 'IMG_6204', V(31.15), V(32.81), s0=0.23, tin=('carry', 3),
    why='leftward drift continues; a motorbike crosses right and turns the direction for the joy run')
JOY = [V(32.81), V(33.74), V(34.67), V(35.59)]
seg('cafe', 'IMG_5969', JOY[0], JOY[1], s0=0.70, tin=('carry', 3),
    why='«تاخدينا»: the motorbike leaves right, the café pan moves right')
seg('bread', 'IMG_5970', JOY[1], JOY[2], s0=0.35, tin=('carry', 3), why='rightward pan into rightward pan, two beats each')
seg('woodride', 'IMG_5976', JOY[2], JOY[3], s0=1.45, tin=('carry', 3), why='«للفرحة»: following the wood carrier rightwards')
seg('minarets', 'IMG_6222', JOY[3], V(37.14), s0=0.95, tin=('carry', 3),
    why='«أمانة»: the pan accelerates right past the minarets; a red SUV fills the frame')
seg('elders', 'IMG_5960', V(37.14), V(38.84), s0=1.40, zoom=[(V(37.14), 1.04), (V(38.84), 1.08)], cx=0.62, cy=0.62,
    why='hidden behind the SUV: landing on stillness, «وتخلّي الحزن»')

# ---------------- OUTRO ----------------
seg('golden', 'IMG_6228', V(38.84), V(40.46), s0=0.80, zoom=[(V(38.84), 1.02), (V(40.46), 1.05)], tin=('dissolve', 14),
    why='«الحزن بعيد»: the day dissolves into golden hour')
seg('station', 'IMG_6181', V(40.46), END,
    keys=[(V(40.46), 0.15), (V(SONG_FREEZE), 3.20), (END, 3.20)],
    zoom=[(V(40.46), 1.02), (V(SONG_FREEZE), 1.10), (V(SONG_FREEZE) + 0.30, 1.14), (END, 1.30)], cy=0.36,
    tin=('dissolve', 8), why='«عنّا»: the station at sunset; frozen on «استنّا»')

# ---------------- lyrics ----------------
# Each line: words (text, onset), end, y (baseline fraction), optional 'hold' = {word_index: (start, end)} for kashida
# words draw their elongation through the held note. Kashida is written with U+0640 in the text itself.
K = 'ـ'
LYRICS = [
    dict(words=[('وميل', 0.22)], end=2.12, y=0.79),
    dict(words=[('وحدف', 2.28), ('منديله', 3.26)], end=4.80, y=0.20),
    dict(words=[('كاتب', 4.98), ('على', 6.36), ('طرفه', 6.94)], end=7.52, y=0.17, hold={0: (4.98, 6.24)},
         words_k=['ك' + K * 4 + 'اتب', None, None]),
    dict(words=[('أجيله', 7.64)], end=9.05, y=0.19),
    dict(words=[('وميل', 9.28)], end=10.35, y=0.80),
    dict(words=[('وحدف', 10.44), ('منديله', 11.36)], end=12.60, y=0.20),
    dict(words=[('كاتب', 12.76), ('على', 14.57), ('طرفه', 15.07)], end=15.62, y=0.17, hold={0: (12.76, 14.03)},
         words_k=['ك' + K * 4 + 'اتب', None, None]),
    dict(words=[('أجيله', 15.77)], end=17.45, y=0.19),
    dict(words=[('وأمانة', 17.67), ('أمانة', 18.77)], end=19.55, y=0.17),
    dict(words=[('يا', 19.65), ('دنيا', 20.55)], end=21.55, y=0.115, cx=0.34, hold={1: (20.55, 21.39)},
         words_k=[None, 'دنيـ' + K * 5 + 'ـا'], gold=[1]),
    dict(words=[('أمانة', 21.69)], end=23.15, y=0.18, hold={0: (21.69, 22.53)}, words_k=['أم' + K * 4 + 'انة'], gold=[0]),
    dict(words=[('تاخدينا', 23.33), ('للفرحة', 24.71)], end=26.15, y=0.18, hold={1: (24.71, 25.99)},
         words_k=[None, 'للف' + K * 4 + 'رحة'], gold=[1]),
    dict(words=[('أمانة', 26.29)], end=27.80, y=0.18),
    dict(words=[('وأمانة', 27.99)], end=29.35, y=0.19),
    dict(words=[('يا', 29.49), ('دنيا', 30.01)], end=31.00, y=0.115, hold={1: (30.01, 30.79)},
         words_k=[None, 'دنيـ' + K * 5 + 'ـا'], gold=[]),
    dict(words=[('أمانة', 31.15)], end=32.65, y=0.17),
    dict(words=[('تاخدينا', 32.81), ('للفرحة', 34.29)], end=35.45, y=0.17, hold={1: (34.29, 35.35)},
         words_k=[None, 'للف' + K * 4 + 'رحة'], gold=[1]),
    dict(words=[('أمانة', 35.59)], end=37.05, y=0.16, hold={0: (35.59, 36.75)}, words_k=['أم' + K * 5 + 'انة'], gold=[0]),
    dict(words=[('وتخلّي', 37.59), ('الحزن', 38.69)], end=39.40, y=0.17),
    dict(words=[('بعيد', 39.53), ('عنّا', 40.46)], end=41.40, y=0.17),
    dict(words=[('وتقولي', 41.60), ('للحب', 42.82)], end=43.70, y=0.17),
    dict(words=[('استنّا', 44.14)], end=47.25, y=0.30, hold={0: (44.14, 45.70)}, words_k=['استنّـ' + K * 6 + 'ـا'], gold=[0], final=True),
]
