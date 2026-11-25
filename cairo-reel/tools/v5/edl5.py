"""YA DONYA v5 - one rhythm for words, shots and music.
Sung phrases (pitch tracker, breath to breath) and word onsets (forced alignment) agree within 0.1 s.
Stanzas live between breaths; shot changes happen in breaths, or on the word the shot is about,
two frames ahead of the voice. The opening (hook, burst, title) is unchanged.
"""
FPS = 30
P = 2.40
def V(s): return round(P + s, 4)
SONG_FREEZE = 44.14
END = V(47.60)
DUR = END
F = 1 / FPS
LEAD = 2 / FPS                      # cuts arrive two frames before the word

SEGS = []
def seg(name, clip, a, b, s0=None, keys=None, zoom=None, cx=0.5, cy=0.5, tin=('cut',), why=''):
    SEGS.append(dict(name=name, clip=clip, a=round(a, 4), b=round(b, 4), s0=s0, keys=keys,
                     zoom=zoom or [(a, 1.0), (b, 1.0)], cx=cx, cy=cy, tin=tin, why=why, vp=None, roll=None, step=None))
def W(s): return V(s) - LEAD        # word-motivated cut time

# ---------------- OPENING (unchanged) ----------------
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
TITLE_OUT = V(0.05)
FLARE = (SLAM - 0.03, SLAM + 0.02, SLAM + 0.30)

# ---------------- STANZA 1 (0.22-8.52): «وميل وحدف منديله / كاتب على طرفه أجيله» ----------------
seg('balcony', 'IMG_5736', SLAM, V(2.28), keys=[(SLAM, 0.06), (V(2.28), 1.52)],
    zoom=[(SLAM, 1.12), (V(0.6), 1.145), (V(2.28), 1.17)], cy=0.42, tin=('land',),
    why='continues the last flash; the push never reverses')
seg('walk', 'IMG_5973', V(2.28), V(4.98) - LEAD, s0=0.40, zoom=[(V(2.28), 1.04), (V(4.98), 1.06)], tin=('dissolve', 14),
    why='a slow dissolve on «وحدف» from the balcony down into the sunlit street')
seg('books', 'IMG_5966', W(4.98), W(7.64), s0=0.30, zoom=[(W(4.98), 1.02), (W(7.64), 1.07)], cx=0.55, cy=0.55,
    why='the second line begins with «كاتب» (he wrote): the book kiosk')
seg('walk2', 'IMG_5961', W(7.64), V(9.28) - LEAD, s0=0.60, zoom=[(W(7.64), 1.04), (V(9.28), 1.07)],
    why='«أجيله» (I will come): walking on, into the breath')

# ---------------- STANZA 2 (9.28-16.65): the same words, one leftward current ----------------
seg('tilt', 'IMG_6227', W(9.28), V(11.94), s0=0.20, tin=('dissolve', 8),
    why='a new stanza: the camera leans down the minaret with «وميل»; the image drifts left')
seg('riders', 'IMG_6208', V(11.94), W(12.76), s0=0.25, tin=('carry', 3), why='the drift hands over to riders moving left')
seg('ornate', 'IMG_6211', W(12.76), V(16.65), s0=0.45, tin=('carry', 3),
    why='riders leave left on «كاتب»; one long leftward pan holds the whole second line')
seg('facade', 'IMG_6212', V(16.65), W(17.67), s0=1.78,
    why='the breath before the chorus: no words, a car crosses right')

# ---------------- STANZA 3 (17.67-22.88): «وأمانة أمانة / يا دنيا أمانة» ----------------
seg('square', 'IMG_6220', W(17.67), W(19.65), s0=1.00, zoom=[(W(17.67), 1.04), (W(19.65), 1.07)], cy=0.42, tin=('carry', 3),
    why='the car crossing right carries into traffic moving right; the hook\'s square returns')
seg('vista', 'IMG_5737', W(19.65), W(21.69), keys=[(W(19.65), 0.02), (W(21.69), 1.10)], zoom=[(W(19.65), 1.02), (W(21.69), 1.08)],
    why='«يا دنيا» (oh world): back on the balcony, the whole avenue opens')
seg('avenue', 'IMG_6219', W(21.69), W(23.33), s0=1.50, zoom=[(W(21.69), 1.04), (W(23.33), 1.08)], cy=0.55,
    why='«أمانة»: down into the avenue, its minaret on the same axis')

# ---------------- STANZA 4 (23.33-27.52): «تاخدينا للفرحة أمانة» ----------------
seg('ride', 'IMG_6223', W(23.33), W(24.71), s0=0.60, zoom=[(W(23.33), 1.05), (W(24.71), 1.10)],
    why='«تاخدينا» (take us): carried forward')
seg('friends', 'IMG_5968', W(24.71), V(27.52), s0=0.27, zoom=[(W(24.71), 1.03), (V(27.52), 1.07)],
    why='«للفرحة» (to joy): two friends on a motorbike; their horn sounds on «أمانة»')

# ---------------- STANZA 5 (27.99-32.38): «وأمانة يا دنيا أمانة» ----------------
seg('stone', 'IMG_6226', V(27.52), W(29.49), s0=0.25, zoom=[(V(27.52), 1.03), (W(29.49), 1.07)], tin=('dissolve', 12),
    why='dissolve in the breath into old Cairo')
seg('mural', 'IMG_6221', W(29.49), V(32.38), s0=0.10, zoom=[(W(29.49), 1.05), (V(32.38), 1.05)], cy=0.42,
    why='«يا دنيا»: Umm Kulthum, the voice of the world the song addresses; the pan drifts left')

# ---------------- STANZA 6 (32.81-37.11): «تاخدينا للفرحة أمانة» - one rightward journey ----------------
seg('flowers', 'IMG_6204', V(32.38), W(32.81), s0=1.37, tin=('carry', 3),
    why='in the breath, a motorbike crosses right and turns the direction')
seg('cafe', 'IMG_5969', W(32.81), W(34.29), s0=0.55, tin=('carry', 3), why='«تاخدينا»: the café pan carries the motorbike\'s direction')
seg('woodride', 'IMG_5976', W(34.29), W(35.59), s0=1.20, tin=('carry', 3), why='«للفرحة»: following the wood carrier, same direction')
seg('minarets', 'IMG_6222', W(35.59), V(37.14), s0=0.95, tin=('carry', 3), why='«أمانة»: the pan reaches the minarets; a red SUV fills the frame')

# ---------------- STANZA 7 (37.59-43.70): «وتخلّي الحزن بعيد عنّا / وتقولي للحب» ----------------
seg('elders', 'IMG_5960', V(37.14), V(38.90), s0=1.40, zoom=[(V(37.14), 1.04), (V(38.90), 1.08)], cx=0.62, cy=0.62,
    why='hidden behind the SUV, in the breath: stillness for «وتخلّي الحزن»')
seg('golden', 'IMG_6228', V(38.90), V(41.20), s0=0.42, zoom=[(V(38.90), 1.02), (V(41.20), 1.05)], tin=('dissolve', 24),
    why='a long dissolve through «الحزن» into golden hour')
seg('station', 'IMG_6181', V(41.20), END,
    keys=[(V(41.20), 0.20), (V(SONG_FREEZE), 3.14), (END, 3.14)],
    zoom=[(V(41.20), 1.02), (V(SONG_FREEZE), 1.08), (V(SONG_FREEZE) + 0.30, 1.11), (END, 1.24)], cy=0.36,
    tin=('dissolve', 12), why='dissolve in the breath; frozen on «استنّا» (wait)')

# ---------------- lyrics: stanzas ----------------
K = 'ـ'
# word: (text, onset, display-text or None, gold?)
STANZAS = [
    dict(lines=[[('وميل', 0.22), ('وحدف', 2.28), ('منديله', 3.26)],
                [('كاتب', 4.98), ('على', 6.36), ('طرفه', 6.94), ('أجيله', 7.64)]], end=8.75, y=0.60),
    dict(lines=[[('وميل', 9.28), ('وحدف', 10.44), ('منديله', 11.36)],
                [('كاتب', 12.76), ('على', 14.57), ('طرفه', 15.07), ('أجيله', 15.77)]], end=16.85, y=0.135),
    dict(lines=[[('وأمانة', 17.67), ('أمانة', 18.77)],
                [('يا', 19.65), ('دنيا', 20.55, 'دنيـ' + K * 4 + 'ـا', True), ('أمانة', 21.69)]], end=22.95, y=0.115, cx=0.38),
    dict(lines=[[('تاخدينا', 23.33), ('للفرحة', 24.71, 'للفـ' + K * 3 + 'ـرحة', True), ('أمانة', 26.29)]], end=27.45, y=0.14),
    dict(lines=[[('وأمانة', 27.99), ('يا', 29.49), ('دنيا', 30.01, 'دنيـ' + K * 4 + 'ـا', True), ('أمانة', 31.15)]], end=32.35, y=0.115),
    dict(lines=[[('تاخدينا', 32.81), ('للفرحة', 34.29, 'للفـ' + K * 3 + 'ـرحة', True), ('أمانة', 35.59)]], end=37.00, y=0.14),
    dict(lines=[[('وتخلّي', 37.59), ('الحزن', 38.69), ('بعيد', 39.53), ('عنّا', 40.46)],
                [('وتقولي', 41.60), ('للحب', 42.82)]], end=43.75, y=0.15),
    dict(lines=[[('استنّا', 44.14, 'استنّـ' + K * 4 + 'ـا', True)]], end=47.30, y=0.30, final=True),
]
