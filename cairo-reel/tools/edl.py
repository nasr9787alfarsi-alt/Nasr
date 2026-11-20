# Edit decision list for the Cairo reel. All times in seconds (output timeline, 30 fps).
# Music anchors (measured): hook-out onset 0.773 | phrase gap/onset 2.644 | onset 4.106 | gap 5.10
# onset 6.231 | silence 9.60-10.30 | vocal re-entry 10.302 | 10.711 | 11.030 | peak 12.26 | 12.926
# 13.569 | 14.30 | peak 14.75 | bass hit 15.52 | 16.46 | climax note 17.10-20.094 | silence | HIT 20.513

FPS = 30
DUR = 23.00

# seg: (name, clip, out_start, out_end, src_start, src_end or None(=1x), opts)
# opts: zoom=(z0,z1) push-in, ramp='decel'|'accel' speed profile, cx/cy zoom centre (0..1)
F = 1/30
BURST = ['IMG_6227', 'IMG_5966', 'IMG_6211', 'IMG_5970', 'IMG_6220',
         'IMG_5976', 'IMG_6204', 'IMG_5960', 'IMG_6228']
BURST_IN = [0.2, 1.5, 0.6, 1.0, 3.0, 0.3, 0.6, 2.0, 0.4]

SEGS = []
def seg(name, clip, a, b, s0, s1=None, **o):
    SEGS.append(dict(name=name, clip=clip, a=a, b=b, s0=s0, s1=s1, o=o))

# 1. HOOK - the mural as our "CAIRO poster" (reference: CAIRO sign 0-0.67)
seg('hook', 'IMG_6221', 0.0, 0.767, 0.25, zoom=(1.10, 1.06), cy=0.42)
# 2. FLASH BURST - 9 x 3-frame previews of what's coming (reference 0.67-1.57)
for i, (c, s) in enumerate(zip(BURST, BURST_IN)):
    a = 0.767 + i * 3 * F
    seg(f'flash{i}', c, a, a + 3 * F, s, zoom=(1.08, 1.08))
# 3. HOLD then dissolve into the title shot (reference: records 1.57-2.27 + dissolve)
seg('hold', 'IMG_6226', 1.667, 2.644, 0.3, zoom=(1.04, 1.09))
# 4. TITLE - "VISUAL DIARY from Cairo" typed on (reference: coffee 2.27-4.17)
seg('title', 'IMG_5736', 2.30, 4.25, 0.02, 1.68, zoom=(1.02, 1.08), cy=0.35)
# 5. light leak 4.106-4.45, hidden cut at 4.25
seg('enter', 'IMG_5724', 4.25, 5.10, 0.35, zoom=(1.06, 1.03))
# DEVELOPMENT - calm, phrase-length holds
seg('balcony', 'IMG_6211', 5.10, 6.233, 0.0, zoom=(1.02, 1.05))
seg('shutter', 'IMG_5960', 6.233, 7.333, 2.0, zoom=(1.03, 1.08), cx=0.6, cy=0.62)
seg('books', 'IMG_5966', 7.333, 8.50, 0.4, zoom=(1.02, 1.07))
seg('bread', 'IMG_5970', 8.50, 9.60, 0.3, zoom=(1.02, 1.06))
# BREATH - arch-mask reveal in the musical silence (reference: arch window near the end)
seg('arch', 'IMG_6227', 9.60, 10.30, 0.0, 0.50)
# BUILD - vocal re-entry: tilt-down speed ramp from minaret to street
seg('tilt', 'IMG_6227', 10.30, 11.033, 0.50, 2.75, ramp='decel')
seg('wood', 'IMG_5976', 11.033, 11.75, 0.0, zoom=(1.04, 1.04))
seg('flowers', 'IMG_6204', 11.75, 12.267, 1.93 - 0.517)        # exits on motorbike wipe
seg('riders', 'IMG_5968', 12.267, 12.933, 1.0, zoom=(1.03, 1.05))
seg('square', 'IMG_6220', 12.933, 13.567, 0.4, zoom=(1.04, 1.04))
seg('flyover', 'IMG_5965', 13.567, 14.30, 0.5, zoom=(1.03, 1.05))
seg('facade', 'IMG_6212', 14.30, 14.75, 1.50 - 0.45)           # exits on SUV wipe
seg('crowd', 'IMG_6182', 14.75, 15.533, 1.55, zoom=(1.03, 1.05))
seg('avenue', 'IMG_6219', 15.533, 16.467, 1.9, zoom=(1.04, 1.07), cy=0.55)
seg('pass', 'IMG_6208', 16.467, 17.10, 0.86 - 0.633)           # exits on motorbike wipe
# CLIMAX - the long held note: strongest footage, day -> golden hour
seg('minarets', 'IMG_6222', 17.10, 18.10, 0.35, 2.35, ramp='decel')
seg('golden', 'IMG_6228', 18.10, 19.10, 0.0, zoom=(1.03, 1.06))
seg('station', 'IMG_6181', 19.10, 20.513, 0.4, zoom=(1.02, 1.09), cy=0.45)
# FINALE - on the hit: bookend to the mural (reference ends on its opening CAIRO sign)
seg('final', 'IMG_6221', 20.513, DUR, 0.10, 1.85, zoom=(1.10, 1.05), cy=0.42)

# transitions
DISSOLVE = ('hold', 'title', 2.30, 2.644)
LEAK = (4.106, 4.25, 4.47)          # start, peak(cut), end
ARCH = (9.60, 10.02, 10.30)         # appear, start opening, fully open
TITLE_T = (2.72, 4.10)
END_T = 20.513
TO_BLACK = (21.10, 21.55)       # mural fades to black under the ring-out
CARD = (21.40, 22.45, DUR)       # end card: in, start out, gone
WIPES = [12.267, 14.75, 17.10]      # 2-frame blur-blend on these cuts
