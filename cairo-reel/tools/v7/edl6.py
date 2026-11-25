"""CAIRO - «طلبت من الله» (v6). Soundtrack: the Mohannad Abu Rizk recitation, used intact.
Video time = audio time + P. Lines/words: subtitle text burned into the source, verified by Whisper and
force-aligned word by word (s6/words.json). Cuts sit in the speaker's pauses unless noted.
"""
import json, os
FPS = 30
P = 2.45
def V(s): return round(P + s, 4)
_here = os.path.dirname(os.path.abspath(__file__))
WORDS = json.load(open(os.path.join(_here, '..', 's6', 'words.json'), encoding='utf-8'))
LINE_TXT = [l.strip() for l in open(os.path.join(_here, '..', 's6', 'lines.txt'), encoding='utf-8') if l.strip()]
LS = {}; LE = {}
for w in WORDS:
    LS.setdefault(w['line'], w['s']); LE[w['line']] = w['e']
LS[34] = 56.05; LE[34] = 57.35                     # «يا سلام»: subtitle timing (aligner low confidence)
AUDIO_END = 57.72
END = V(AUDIO_END) + 1.6
DUR = END
def gap(k):                                        # a point in the pause before line k, >=0.12 s ahead of the voice
    a, b = LE[k - 1], LS[k]
    return V(min((a + b) / 2, b - 0.12))

SEGS = []
def seg(name, clip, a, b, s0=None, keys=None, zoom=None, cx=0.5, cy=0.5, tin=('cut',), why=''):
    SEGS.append(dict(name=name, clip=clip, a=round(a, 4), b=round(b, 4), s0=s0, keys=keys,
                     zoom=zoom or [(a, 1.0), (b, 1.0)], cx=cx, cy=cy, tin=tin, why=why, vp=None, roll=None, step=None))

# ---------------- OPENING (approved, unchanged) ----------------
BEAT = 60 / 129.2; GRID16 = BEAT / 4
seg('hook', 'IMG_6220', 0.0, 0.465, s0=0.62, zoom=[(0.0, 1.16), (0.465, 1.10)], cy=0.40)
BURST = [('IMG_6211', 1.2), ('IMG_5976', 0.2), ('IMG_6227', 0.3), ('IMG_6204', 1.9), ('IMG_6221', 0.3),
         ('IMG_5968', 2.2), ('IMG_6226', 0.4), ('IMG_6182', 2.3), ('IMG_6222', 1.6), ('IMG_6228', 0.6),
         ('IMG_5960', 2.0), ('IMG_5736', 0.0)]
_t = [0.465, 0.465 + 2 * GRID16]
while len(_t) < len(BURST) + 1: _t.append(_t[-1] + GRID16)
BURST_TIMES = [round(round(x * FPS) / FPS, 4) for x in _t]
for i, (c, s) in enumerate(BURST):
    seg(f'flash{i}', c, BURST_TIMES[i], BURST_TIMES[i + 1], s0=s, zoom=[(BURST_TIMES[i], 1.08), (BURST_TIMES[i + 1], 1.12)])
SLAM = BURST_TIMES[-1]
TITLE_OUT = P - 0.25
FLARE = (SLAM - 0.03, SLAM + 0.02, SLAM + 0.30)

# ---------------- the film ----------------
# «طلبت من الله / أن يرزقني فأرزقني» - the balcony continues out of the last flash; the push never reverses
seg('balcony', 'IMG_5736', SLAM, gap(2), keys=[(SLAM, 0.06), (gap(2), 1.45)],
    zoom=[(SLAM, 1.12), (V(1.0), 1.15), (gap(2), 1.18)], cy=0.42, tin=('land',), why='same shot as the last flash')
# «فوضع في رأسي / عقلاً وفكراً ألهمني» - reason and thought: the book kiosk
seg('books', 'IMG_5966', gap(2), gap(4), keys=[(gap(2), 0.15), (gap(4), 3.00)], zoom=[(gap(2), 1.03), (gap(4), 1.10)], cx=0.55, cy=0.55, tin=('dissolve', 14),
    why='a slow dissolve: from the sky over the city into the books')
# «وبيّن لي طريق الحلال / من الحرام وزوّدني» - the path: walking forward
seg('path', 'IMG_5973', gap(4), gap(6), s0=0.30, zoom=[(gap(4), 1.04), (gap(6), 1.08)], why='the path, walked')
# «وبصفتي إنسانٌ خلقني» - a man steps into the street
seg('human', 'IMG_6182', gap(6), gap(7), s0=0.90, zoom=[(gap(6), 1.03), (gap(7), 1.06)], why='a human being')
# «فخلق جميع المخلوقات / وعنها ميّزني» - all creation: the whole avenue from above
seg('creation', 'IMG_5965', gap(7), gap(9), s0=0.40, zoom=[(gap(7), 1.02), (gap(9), 1.07)],
    why='the widest view of the city')
# «عقلاً وفكراً / وبكتابه سطّرني» - made with thought: ornate architecture, its pan drifting left
seg('ornate', 'IMG_6211', gap(9), gap(11), s0=1.30, zoom=[(gap(9), 1.02), (gap(11), 1.04)], why='a city built by reason')
# «فخلق لي لساناً / لأكلّمك فكلمتني» - the tongue that speaks: Umm Kulthum, Egypt's voice; the pan keeps drifting left
seg('voice', 'IMG_6221', gap(11), gap(13), s0=0.20, zoom=[(gap(11), 1.05), (gap(13), 1.05)], cy=0.42, tin=('carry', 3),
    why='leftward pan into leftward pan; the voice of Egypt for «لسان»')
# «أذكر اسمه دائماً عليه / حتى يعلّمني» - remembrance: the camera rises up the minaret
seg('remember', 'IMG_6227', gap(13), gap(15), s0=0.40, tin=('carry', 3), why='the pan turns upward into the minaret')
# «أول وصية أوصاني بها / ونصحني / عبادته» - worship: minarets across the square, pan to the right
seg('worship', 'IMG_6222', gap(15), gap(17), s0=0.20, why='the minarets')
seg('worship2', 'IMG_6219', gap(17), gap(18), s0=1.70, zoom=[(gap(17), 1.05), (gap(18), 1.10)], cy=0.55,
    why='«عبادته»: a minaret at the end of the avenue')
# «وبالوالدين ذكّرني» - the parents: the old men through the shutter
seg('parents', 'IMG_5960', gap(18), gap(19), s0=1.30, zoom=[(gap(18), 1.04), (gap(19), 1.10)], cx=0.62, cy=0.62,
    tin=('dissolve', 10), why='a soft dissolve into the elders')
# «وثانيها على حلف اليمين / فلا أحد يجبرني / على بيع سلعة / حتى أحصل على ما أتمكّن» - honest trade
seg('trade1', 'IMG_6204', gap(19), gap(21), s0=0.10, why='the flower seller')
seg('trade2', 'IMG_5970', gap(21), gap(23), s0=0.30, tin=('carry', 3), why='the bread stand; its pan moves right')
seg('trade3', 'IMG_5976', gap(23), gap(24), keys=[(gap(23), 0.90), (gap(24), 2.50)], tin=('carry', 3), why='earning: the wood carrier, same direction')
# «الصلاة والصوم والزكاة / على طريقها أرشدني» - the red minaret on the square, then the way forward
seg('prayer', 'IMG_6220', gap(24), gap(25), s0=1.20, zoom=[(gap(24), 1.06), (gap(25), 1.10)], cy=0.40, why='prayer')
seg('guided', 'IMG_6225', gap(25), gap(26), keys=[(gap(25), 0.15), (gap(26), 1.65)], zoom=[(gap(25), 1.05), (gap(26), 1.10)], why='guided along its path')
# «فإذا تركتها / فمن الجنة حرمني» - the gravest line: a still, shaded old street
seg('grave', 'IMG_6224', gap(26), gap(28), keys=[(gap(26), 0.12), (gap(28), 2.00)], zoom=[(gap(26), 1.02), (gap(28), 1.07)], tin=('dissolve', 10),
    why='the film slows and darkens for the warning')
# «كم أعطاني من الأثمار / حتى يُشبعني» - blessings: green trees, the light turns golden
seg('blessings', 'IMG_5972', gap(28), gap(29), keys=[(gap(28), 0.15), (gap(29), 1.55)], zoom=[(gap(28), 1.03), (gap(29), 1.06)], tin=('dissolve', 12),
    why='green, living streets')
seg('golden', 'IMG_6228', gap(29), gap(31), keys=[(gap(29), 0.28), (gap(31), 2.40)], zoom=[(gap(29), 1.02), (gap(31), 1.06)], tin=('dissolve', 14),
    why='«لأشكره دائماً»: golden hour')
# «في البرّ / والبحر والجو» - land, then sky
seg('land', 'IMG_5968', gap(31), gap(32), s0=0.30, zoom=[(gap(31), 1.03), (gap(32), 1.06)], why='on land')
seg('sky', 'IMG_5971', gap(32), gap(33), s0=0.40, zoom=[(gap(32), 1.04), (gap(33), 1.08)], why='and sky')
# «حتى في مسكني ... يا سلام» - home: the station at sunset with the flag, held to the end
seg('home', 'IMG_6181', gap(33), END, keys=[(gap(33), 0.30), (V(AUDIO_END), 3.05), (END, 3.18)],
    zoom=[(gap(33), 1.02), (V(AUDIO_END), 1.10), (END, 1.13)], cy=0.38, tin=('dissolve', 14),
    why='home: Cairo at sunset; it holds after the last words')

# ---------------- text ----------------
EN = ['I asked God', 'to provide for me, and He did.', 'He placed in my mind', 'reason and thought. He inspired me,',
      "showed me what's right", 'and wrong, and gave me more.', 'He created me as a human being.', 'He created all creation',
      'and set me apart from it', 'with reason and thought.', 'And in His Book, He wrote my story.', 'He gave me a tongue',
      'to speak to You, and You answered.', 'I always remember His name,', 'so He may teach me.', 'The first thing He commanded me,',
      'and advised me with,', 'was His worship.', 'And He reminded me of my parents.', 'And the second:', 'an oath is sacred.',
      'No one can force me', 'to sell what is mine', 'until I earn what I am able to.', 'Prayer, fasting and zakat:',
      'He guided me to their path.', 'And if I leave them,', 'I deprive myself of Paradise.', 'How many blessings has He given me',
      'to satisfy me?', 'So I may always thank Him,', 'on land,', 'at sea, and in the sky,', 'even in my own home.', 'Beautiful.']
# display groups: lists of line indices shown together; layout y (baseline of the first Arabic line) chosen per shot
GROUPS = [([0, 1], 0.62), ([2, 3], 0.15), ([4, 5], 0.14), ([6], 0.15), ([7, 8], 0.13), ([9, 10], 0.14), ([11, 12], 0.13),
          ([13, 14], 0.70), ([15, 16, 17], 0.13), ([18], 0.13), ([19, 20], 0.14), ([21, 22], 0.13), ([23], 0.14),
          ([24, 25], 0.13), ([26, 27], 0.15), ([28, 29], 0.14), ([30], 0.13), ([31, 32], 0.15), ([33], 0.13), ([34], 0.30)]
