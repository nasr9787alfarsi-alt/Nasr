"""CAIRO CLOCKWORK - edit decision list (v2, new soundtrack).
Times in seconds on the output timeline (30 fps). Song starts at t=0.
Song map (measured): vocal lines 0.13-4.72 | 4.98-9.00 | 9.31-14.06 | 14.69-22.88 | 23.48-27.52 (B, higher)
| 27.88-32.38 | 32.82-37.11 | 37.52-41.20 (peak pitch) | 41.55-46.00 (file cuts off mid-note)
Strong accents: 4.99, 9.37, 10.94, 12.77, 14.56, 23.36, 32.86, 33.27.  Tempo ~129 bpm (beat ~0.465 s).
"""
FPS = 30
SONG_END = 46.0
DUR = 46.40
F = 1 / FPS

# Each segment: clip, a, b (output), and either
#   s0 (1x from s0) | keys=[(t_out, src), ...] piecewise time map (monotone, smoothstep between keys)
#   zoom=[(t_out, z), ...]  cx/cy = zoom centre (0..1)  vp=(x,y) vanishing point to lock to VP_TARGET
#   step=n  -> stop-motion: hold each source frame n output frames
SEGS = []
def seg(name, clip, a, b, s0=None, keys=None, zoom=None, cx=0.5, cy=0.5, vp=None, step=None, rev=False):
    SEGS.append(dict(name=name, clip=clip, a=a, b=b, s0=s0, keys=keys, zoom=zoom or [(a, 1.0), (b, 1.0)],
                     cx=cx, cy=cy, vp=vp, step=step))

# ---------------- OPENING (IMPORTANT recreation) ----------------
HOOK_SRC = 0.30
seg('hook', 'IMG_6221', 0.0, 0.70, s0=HOOK_SRC, zoom=[(0.0, 1.10), (0.70, 1.10)], cy=0.42)
BURST = [('IMG_6227', 0.2), ('IMG_5976', 0.3), ('IMG_6211', 1.2), ('IMG_6220', 0.9), ('IMG_5960', 2.0),
         ('IMG_6228', 0.4), ('IMG_6212', 2.3), ('IMG_6181', 0.8), ('IMG_6222', 1.0)]
BURST_T0 = 0.70
for i, (c, s) in enumerate(BURST):
    a = BURST_T0 + i * 3 * F
    seg(f'flash{i}', c, a, a + 3 * F, s0=s, zoom=[(a, 1.06), (a + 3 * F, 1.06)])
seg('hold', 'IMG_5966', 1.60, 2.50, s0=0.6, zoom=[(1.60, 1.03), (2.50, 1.08)])
seg('title', 'IMG_5736', 2.20, 4.99, keys=[(2.20, 0.03), (4.99, 1.70)], zoom=[(2.20, 1.02), (4.99, 1.09)], cy=0.35)
DISSOLVE = [('hold', 'title', 2.20, 2.50)]
LEAK = (4.78, 4.99, 5.24)                 # start, peak (= hidden cut), end
TITLE = [  # text, font, size, x, y, colour, first-char time, per-char interval, tracking
    ('VISUAL DIARY', 'Cormorant-600', 66, 74, 222, (252, 248, 240), 2.62, 0.062, 5),
    ('from', 'Cormorant-400i', 48, 78, 300, (252, 248, 240), 3.48, 0.070, 1),
    ('Cairo', 'Playfair-400', 150, 66, 330, (236, 200, 128), 3.82, 0.085, 2),
]

# ---------------- THE WALK : vanishing-point-locked forward walks, cut on beats ----------------
VP_TARGET = (0.46, 0.55)
seg('walk1', 'IMG_5961', 4.99, 6.04, s0=0.70, vp=(0.50, 0.47), zoom=[(4.99, 1.14), (6.04, 1.18)])
seg('walk2', 'IMG_6225', 6.04, 6.99, s0=0.25, vp=(0.45, 0.58), zoom=[(6.04, 1.14), (6.99, 1.16)])
seg('walk3', 'IMG_5973', 6.99, 7.94, s0=4.20, vp=(0.40, 0.54), zoom=[(6.99, 1.14), (7.94, 1.18)])
seg('walk4', 'IMG_6223', 7.94, 9.31, s0=0.55, vp=(0.47, 0.62), zoom=[(7.94, 1.14), (9.31, 1.22)])

# ---------------- STREET LIFE : breathing, no effects ----------------
seg('shutter', 'IMG_5960', 9.31, 11.20, s0=1.40, zoom=[(9.31, 1.02), (11.20, 1.07)], cx=0.62, cy=0.62)
seg('cafe', 'IMG_5969', 11.20, 12.77, s0=0.55, zoom=[(11.20, 1.03), (12.77, 1.03)])
seg('bread', 'IMG_5970', 12.77, 14.06, s0=0.40, zoom=[(12.77, 1.03), (14.06, 1.05)])   # same pan direction as cafe

# ---------------- VEHICLES CARRY US : object wipes ----------------
seg('flowers', 'IMG_6204', 14.06, 14.56, s0=1.93 - 0.50)                 # motorbike fills lens at 14.56
seg('wood', 'IMG_5976', 14.56, 15.55, s0=0.0, zoom=[(14.56, 1.04), (15.55, 1.04)])   # ...motorbike continues
seg('riders', 'IMG_5968', 15.55, 16.54, s0=1.20, zoom=[(15.55, 1.03), (16.54, 1.06)])
seg('square', 'IMG_6220', 16.54, 17.55, s0=0.35, zoom=[(16.54, 1.04), (17.55, 1.04)])
seg('flyover', 'IMG_5965', 17.55, 18.69, s0=0.30, zoom=[(17.55, 1.03), (18.69, 1.06)])
seg('pass', 'IMG_6208', 18.69, 19.56, s0=0.86 - 0.87)                    # motorbike fills lens at 19.56
seg('above', 'IMG_5957', 19.56, 20.58, s0=1.20, zoom=[(19.56, 1.04), (20.58, 1.04)])
seg('cyclist', 'IMG_5967', 20.58, 21.99, s0=2.20, zoom=[(20.58, 1.03), (21.99, 1.06)])
# SUV wipes in, clears, then we push into the arched doorway
DOOR = dict(cx=0.545, apex=0.385, spring=0.43, sill=0.62, half_w=0.072)   # doorway opening in source coords
seg('door', 'IMG_6212', 21.99, 23.75, s0=1.40,
    zoom=[(21.99, 1.0), (22.80, 1.0), (23.30, 1.55), (23.75, 3.2)], cx=0.545, cy=0.52)
ARCH = (23.20, 23.48, 23.80)   # mask appears inside the door, B-section entry (latch), fully open

# ---------------- OLD CAIRO ----------------
seg('tilt', 'IMG_6227', 23.20, 25.18, keys=[(23.20, 0.0), (23.80, 0.45), (25.18, 3.10)],
    zoom=[(23.20, 1.0), (25.18, 1.03)])
seg('stone', 'IMG_6226', 25.18, 26.63, s0=0.30, zoom=[(25.18, 1.03), (26.63, 1.08)])
seg('crossing', 'IMG_5953', 26.63, 27.88, s0=0.00, zoom=[(26.63, 1.04), (27.88, 1.06)])   # walks right -> next pan moves right

# ---------------- GRANDEUR -> THE CLOCK SKIPS ----------------
seg('balcony', 'IMG_6211', 27.88, 29.56, s0=0.80, zoom=[(27.88, 1.02), (29.56, 1.04)])
seg('tall', 'IMG_6184', 29.56, 30.55, s0=1.00, zoom=[(29.56, 1.03), (30.55, 1.06)])
# young man walks into frame; time starts to tick (stop-motion), freezes in the musical pause, winds up
seg('walkin', 'IMG_6182', 30.55, 31.96, s0=0.27, zoom=[(30.55, 1.03), (31.96, 1.05)])
seg('stutter', 'IMG_6182', 31.96, 32.38, keys=[(31.96, 1.68), (32.38, 2.10)], step=3,
    zoom=[(31.96, 1.05), (32.38, 1.06)])
seg('freeze', 'IMG_6182', 32.38, 32.86, keys=[(32.38, 2.10), (32.86, 2.10)],
    zoom=[(32.38, 1.06), (32.86, 1.14)])
STUTTER_STEPS = [31.96 + i * 3 * F for i in range(5)]      # a ratchet click on every held frame
WIND = (32.40, 32.84)                                       # ratchet wind-up during the freeze
HIT = 32.86

# ---------------- RELEASE ----------------
seg('minarets', 'IMG_6222', 32.86, 34.27, keys=[(32.86, 0.10), (33.30, 1.20), (34.27, 2.30)],
    zoom=[(32.86, 1.06), (34.27, 1.02)])
seg('avenue', 'IMG_6219', 34.27, 35.67, s0=1.50, zoom=[(34.27, 1.04), (35.67, 1.08)], cy=0.55)
seg('stroll', 'IMG_5956', 35.67, 37.52, s0=0.70, zoom=[(35.67, 1.03), (37.52, 1.06)])

# ---------------- CLIMAX : the music takes control ----------------
seg('golden', 'IMG_6228', 37.52, 40.05, s0=0.0, zoom=[(37.52, 1.02), (40.05, 1.08)])
seg('station', 'IMG_6181', 40.05, 41.55, s0=0.40, zoom=[(40.05, 1.02), (41.55, 1.08)], cy=0.45)

# ---------------- WIND-DOWN : reverse pan decelerates onto the opening frame -> loop ----------------
END_FREEZE = 45.95
seg('final', 'IMG_6221', 41.55, DUR,
    keys=[(41.55, 4.55), (44.90, 0.95), (45.45, 0.50), (END_FREEZE, HOOK_SRC), (DUR, HOOK_SRC)],
    zoom=[(41.55, 1.04), (44.90, 1.08), (END_FREEZE, 1.10), (DUR, 1.10)], cy=0.42)
TAPESTOP = (45.05, SONG_END)
WINDDOWN_CLICKS = (44.90, END_FREEZE)
