#!/usr/bin/env python3
"""A TALE OF THREE ECONOMIES - classic cinematic A2 landscape poster (594 x 420 mm)."""
import pathlib, random, math
HERE = pathlib.Path(__file__).parent
random.seed(42)

GOLD, GOLDL, GOLDD = '#D4A84B', '#F3D58E', '#8E6A22'
IVORY, IVORYD = '#F4E9D2', '#E6D5B3'
NAVY, NAVY2, NAVY3 = '#0C1424', '#15213A', '#1D2C4A'
BURG, BURGD = '#7A2230', '#561520'
EMER, EMERD = '#1F6352', '#123F33'
INK = '#1B1A22'
MK, MX, CM = '#B8862B', EMER, BURG          # district identity colours

def gear_path(r1, r2, n):
    pts = []
    for i in range(n*4):
        a = i/(n*4)*2*math.pi
        r = r2 if (i % 4) in (1, 2) else r1
        pts.append((r*math.cos(a), r*math.sin(a)))
    return 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in pts) + 'Z'

# ---------------------------------------------------------------- monoline icon set (stroke = currentColor)
S = 'fill="none" stroke="currentColor" stroke-width=".75" stroke-linecap="round" stroke-linejoin="round"'
ICONS = f'''
<g id="m-people" {S}><circle cx="-2.4" cy="-2.2" r="1.7"/><path d="M-5.4 3.6 Q-5.4 .2 -2.4 .2 Q.6 .2 .6 3.6"/><circle cx="2.6" cy="-1.4" r="1.5"/><path d="M.6 1.4 Q1.4 .8 2.6 .8 Q5.4 .8 5.4 3.8"/></g>
<g id="m-tag" {S}><path d="M-4.6 -2.8 H1.8 L4.8 0 L1.8 2.8 H-4.6Z"/><circle cx="1.6" cy="0" r=".7"/></g>
<g id="m-gear" {S}><path d="{gear_path(3.4, 4.6, 8)}"/><circle r="1.5"/></g>
<g id="m-gov" {S}><path d="M-5 -1.6 L0 -4.6 L5 -1.6Z M-4.4 -1.6 V3 M-1.5 -1.6 V3 M1.5 -1.6 V3 M4.4 -1.6 V3 M-5.4 3.6 H5.4"/></g>
<g id="m-plan" {S}><rect x="-3.6" y="-4" width="7.2" height="8.6" rx=".8"/><path d="M-1.6 -4.6 H1.6 M-2 -1.4 H2 M-2 .8 H2 M-2 3 H.6"/></g>
<g id="m-box" {S}><path d="M0 -4.6 L4.4 -2.2 V2.6 L0 5 L-4.4 2.6 V-2.2Z M-4.4 -2.2 L0 .2 L4.4 -2.2 M0 .2 V5"/></g>
<g id="m-key" {S}><circle cx="-2.4" cy="0" r="2.2"/><path d="M-.2 0 H5 M3.4 0 V1.8 M4.8 0 V1.4"/></g>
<g id="m-target" {S}><circle r="4.4"/><circle r="2.4"/><circle r=".6" fill="currentColor"/></g>
<g id="m-up" {S}><circle r="4.4"/><path d="M-2 .2 L-.5 1.8 L2.2 -1.4"/></g>
<g id="m-down" {S}><circle r="4.4"/><path d="M-1.7 -1.7 L1.7 1.7 M1.7 -1.7 L-1.7 1.7"/></g>
<g id="m-compass" {S}><circle r="4.4"/><path d="M0 -3 L1 0 L0 3 L-1 0Z"/></g>
<g id="m-shield" {S}><path d="M0 -4.6 L4 -3 V.4 Q4 3.6 0 5 Q-4 3.6 -4 .4 V-3Z"/><path d="M-1.6 .2 L-.4 1.4 L1.8 -1"/></g>
<g id="m-branch" {S}><path d="M-4.4 4 V-.6 Q-4.4 -3.4 -1.6 -3.4 H4.4 M-4.4 1 H4.4 M2.6 -5 L4.4 -3.4 L2.6 -1.8 M2.6 -.6 L4.4 1 L2.6 2.6"/></g>
<g id="m-bridge" {S}><path d="M-5.4 2.6 V-.4 Q0 -5 5.4 -.4 V2.6 M-5.6 1 H5.6 M-2.6 1 V-2.4 M0 1 V-3.2 M2.6 1 V-2.4"/></g>
<g id="m-what" {S}><path d="M0 -4.6 L4.4 -2.2 V2.6 L0 5 L-4.4 2.6 V-2.2Z M-4.4 -2.2 L0 .2 L4.4 -2.2 M0 .2 V5"/></g>
<g id="m-hat" {S}><path d="M-4.4 1.6 Q-4.4 -3.8 0 -3.8 Q4.4 -3.8 4.4 1.6 M-5.4 1.6 H5.4 V2.8 H-5.4Z"/></g>
'''

def use(i, x, y, s=1.0, col=None):
    c = f' style="color:{col}"' if col else ''
    return f'<use href="#{i}" transform="translate({x:.2f} {y:.2f}) scale({s})"{c}/>'
def T(x, y, txt, size=5, w=600, col=IVORY, anchor='middle', fam='Cinzel', extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" text-anchor="{anchor}" fill="{col}" font-family="{fam}"{extra}>{txt}</text>'

# ---------------------------------------------------------------- SKYLINE (576 x 100)
W, H, GY = 576, 92, 72
sk = []
sk.append(f'<rect x="0" y="0" width="{W}" height="{GY}" fill="url(#gSky)"/>')
for _ in range(90):
    sk.append(f'<circle cx="{random.uniform(0, W):.1f}" cy="{random.uniform(1, 40):.1f}" r="{random.uniform(.12, .38):.2f}" fill="{IVORY}" opacity="{random.uniform(.35, .9):.2f}"/>')
# the sun of scarce resources + deco rays
SUNX, SUNY = 290, 72
for k in range(26):
    a1 = math.pi + k*math.pi/26; a2 = a1 + math.pi/52
    sk.append(f'<path d="M{SUNX} {SUNY} L{SUNX+200*math.cos(a1):.1f} {SUNY+200*math.sin(a1):.1f} L{SUNX+200*math.cos(a2):.1f} {SUNY+200*math.sin(a2):.1f}Z" fill="{GOLD}" opacity=".055"/>')
sk.append(f'<circle cx="{SUNX}" cy="{SUNY}" r="52" fill="url(#gHalo)"/>')
sk.append(f'<circle cx="{SUNX}" cy="{SUNY}" r="36" fill="url(#gSun)"/>')
for r in (40, 44):
    sk.append(f'<circle cx="{SUNX}" cy="{SUNY}" r="{r}" fill="none" stroke="{GOLD}" stroke-width=".3" opacity=".45"/>')
sk.append(T(SUNX, 45.2, 'SCARCE RESOURCES', 3.6, 700, '#4A2E08', extra=' letter-spacing=".35"'))
sk.append(T(SUNX, 51.2, 'land &#183; labour &#183; capital', 4.4, 700, '#4A2E08', fam='Cormorant Garamond', extra=' font-style="italic"'))

def beam(x, y, ang, spread, length, grad, op=1):
    a1 = math.radians(ang - spread); a2 = math.radians(ang + spread)
    return (f'<path d="M{x} {y} L{x+length*math.sin(a1):.1f} {y-length*math.cos(a1):.1f} L{x+length*math.sin(a2):.1f} {y-length*math.cos(a2):.1f}Z" '
            f'fill="url(#{grad})" opacity="{op}"/>')

def windows(x, y, w, h, col, density=.55, cw=1.1, ch=1.5, gx=2.4, gy=3.2, uniform=False):
    out = []
    cols = int((w-1.6)/gx); rows = int((h-3)/gy)
    for r in range(rows):
        for c in range(cols):
            if uniform or random.random() < density:
                out.append(f'<rect x="{x+1.2+c*gx:.2f}" y="{y+2+r*gy:.2f}" width="{cw}" height="{ch}" fill="{col}" opacity="{.9 if uniform else random.uniform(.45, 1):.2f}"/>')
    return ''.join(out)

# --- MARKET DISTRICT (x 0-192): many owners, many beams, varied towers
mk = []
for x, ang in [(22, -18), (52, 8), (88, -6), (120, 14), (160, -10)]:
    mk.append(beam(x, 32, ang, 2.6, 56, 'gBeamGold', .9))
x = 4
shades = ['#18243F', '#1D2A47', '#222F50', '#16203A', '#26345A']
while x < 186:
    w = random.uniform(9, 17); h = random.uniform(20, 50)
    top = GY - h
    col = random.choice(shades)
    style = random.choice(['flat', 'spire', 'step', 'dome', 'flat', 'step'])
    mk.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{col}"/>')
    if style == 'spire':
        mk.append(f'<path d="M{x+w/2-1.2:.1f} {top:.1f} L{x+w/2:.1f} {top-9:.1f} L{x+w/2+1.2:.1f} {top:.1f}Z" fill="{col}"/>')
    elif style == 'step':
        mk.append(f'<rect x="{x+w*.2:.1f}" y="{top-4:.1f}" width="{w*.6:.1f}" height="4" fill="{col}"/><rect x="{x+w*.35:.1f}" y="{top-7:.1f}" width="{w*.3:.1f}" height="3" fill="{col}"/>')
    elif style == 'dome':
        mk.append(f'<path d="M{x+1:.1f} {top:.1f} A{w/2-1:.1f} {w/2-1:.1f} 0 0 1 {x+w-1:.1f} {top:.1f}Z" fill="{col}"/>')
    mk.append(windows(x, top, w, h-6, random.choice([GOLDL, '#FFE4A8', '#F7C96E']), density=random.uniform(.35, .7)))
    if random.random() < .55:   # neon / company sign: private ownership
        mk.append(f'<rect x="{x+1.5:.1f}" y="{top+3:.1f}" width="{w-3:.1f}" height="2.2" fill="{random.choice([BURG, EMER, GOLD, "#C4552F"])}" opacity=".95"/>')
    x += w + random.uniform(.6, 2.4)
# market arcade with awnings + shoppers
mk.append(f'<rect x="6" y="{GY-7}" width="180" height="7" fill="#101A30"/>')
for i in range(15):
    c = [GOLD, BURG, EMER][i % 3]
    mk.append(f'<path d="M{8+i*12} {GY-7} h10 l-1.2 3 h-7.6Z" fill="{c}"/><rect x="{9.5+i*12}" y="{GY-3.4}" width="7" height="3.4" fill="#F6CB74" opacity=".55"/>')
SIL = '#070C17'
def person(x, s=1, bag=False):
    o = f'<g transform="translate({x:.1f} {GY}) scale({s})"><circle cx="0" cy="-6.8" r="1.1" fill="{SIL}"/><path d="M-1.4 0 L-1.6 -4.8 Q-1.6 -5.8 0 -5.8 Q1.6 -5.8 1.6 -4.8 L1.4 0Z" fill="{SIL}"/>'
    if bag:
        o += f'<rect x="1.6" y="-3.4" width="1.6" height="1.9" fill="{SIL}"/>'
    return o + '</g>'
for xx in (30, 34, 61, 98, 103, 141, 170):
    mk.append(person(xx, random.uniform(.9, 1.08), bag=random.random() < .7))
MARKET = ''.join(mk)

# --- THE COMMONS (mixed, x 192-384): public dome + private towers + bridge, two beams that meet
mx = []
mx.append(beam(237, 22, 26, 3, 62, 'gBeamIvory', .95))
mx.append(beam(337, 24, -24, 3, 62, 'gBeamGold', .95))
# private towers (right)
for (x, w, h) in [(316, 13, 42), (331, 11, 50), (344, 15, 37), (361, 12, 45), (375, 9, 30)]:
    mx.append(f'<rect x="{x}" y="{GY-h}" width="{w}" height="{h}" fill="#17304A"/>')
    mx.append(f'<rect x="{x}" y="{GY-h}" width="{w*.35:.1f}" height="{h}" fill="#1E3D59" opacity=".8"/>')
    mx.append(windows(x, GY-h, w, h-6, '#9FE0C8', density=.6))
    mx.append(f'<rect x="{x+1.4}" y="{GY-h+2.6}" width="{w-2.8}" height="2" fill="{GOLD}"/>')
# public civic building with dome (left/centre)
mx.append(f'<rect x="204" y="{GY-24}" width="66" height="24" fill="#1A2440"/>')
mx.append(f'<rect x="212" y="{GY-30}" width="50" height="6" fill="#1E2A49"/>')
mx.append(f'<path d="M220 {GY-30} A17 17 0 0 1 254 {GY-30}Z" fill="#22305A"/>')
mx.append(f'<path d="M224 {GY-30} A13 13 0 0 1 250 {GY-30}" fill="none" stroke="{IVORYD}" stroke-width=".35" opacity=".6"/>')
mx.append(f'<path d="M237 {GY-47} V{GY-52}" stroke="{IVORYD}" stroke-width=".5"/>')
for i in range(9):
    mx.append(f'<rect x="{208+i*7}" y="{GY-21}" width="2.2" height="18" fill="#F1DDAE" opacity=".85"/>')
mx.append(f'<path d="M202 {GY-24} L237 {GY-33} L272 {GY-24}Z" fill="#1E2A49" opacity=".0"/>')
mx.append(f'<rect x="202" y="{GY-3}" width="70" height="3" fill="#24315A"/>')
# bridge between public and private
mx.append(f'<path d="M270 {GY-6} Q293 {GY-24} 316 {GY-6}" fill="none" stroke="#0E1526" stroke-width="1.6"/><path d="M270 {GY-6} Q293 {GY-24} 316 {GY-6}" fill="none" stroke="{GOLD}" stroke-width=".5"/>')
mx.append(f'<rect x="270" y="{GY-6.6}" width="46" height="1.6" fill="#0E1526"/>')
for xx in range(274, 314, 5):
    yy = GY-6 - (9*(1-((xx-293)/23)**2))
    mx.append(f'<path d="M{xx} {GY-6} V{yy:.1f}" stroke="#0E1526" stroke-width=".6"/>')
mx.append(f'<rect x="268" y="{GY-8}" width="3" height="8" fill="#0E1526"/><rect x="315" y="{GY-8}" width="3" height="8" fill="#0E1526"/>')
for xx, b in ((206, True), (262, False), (281, True), (300, False), (330, True)):
    mx.append(person(xx, 1.0, bag=b))
MIXED = ''.join(mx)

# --- PLAN DISTRICT (command, x 384-576): perfect symmetry, one giant beam
cm = []
CX = 481
cm.append(beam(CX, 5, 0, 6.5, 70, 'gBeamIvory', 1))
pairs = [(17, 46), (31, 39), (45, 33), (59, 27), (73, 22), (86, 18)]
for dx, h in pairs:
    for sgn in (-1, 1):
        x = CX + sgn*dx - 6
        cm.append(f'<rect x="{x}" y="{GY-h}" width="12" height="{h}" fill="#1E1A30"/>')
        cm.append(f'<rect x="{x}" y="{GY-h}" width="12" height="1.6" fill="{BURG}"/>')
        cm.append(windows(x, GY-h, 12, h-5, '#E9DDC3', uniform=True, gx=2.6, gy=3.6))
# the central authority tower
cm.append(f'<rect x="{CX-9}" y="{GY-56}" width="18" height="56" fill="#241B2E"/>')
cm.append(f'<rect x="{CX-6.5}" y="{GY-62}" width="13" height="6" fill="#241B2E"/><rect x="{CX-4}" y="{GY-66}" width="8" height="4" fill="#241B2E"/>')
cm.append(f'<path d="M{CX-1.2} {GY-66} L{CX} {GY-69} L{CX+1.2} {GY-66}Z" fill="#241B2E"/>')
cm.append(f'<rect x="{CX-9}" y="{GY-50}" width="18" height="4.4" fill="{BURG}"/>' + T(CX, GY-46.7, 'THE PLAN', 2.6, 700, GOLDL, extra=' letter-spacing=".3"'))
cm.append(windows(CX-9, GY-44, 18, 41, '#F3E3BE', uniform=True, gx=2.6, gy=3.4))
cm.append(f'<circle cx="{CX}" cy="{GY-67}" r="2.2" fill="#FFF6DA"/>')
# identical queue
for i in range(9):
    cm.append(person(CX-36+i*9, 1.0))
COMMAND = ''.join(cm)

# --- river and reflections
rv = [f'<rect x="0" y="{GY}" width="{W}" height="{H-GY}" fill="url(#gRiver)"/>',
      f'<path d="M0 {GY} H{W}" stroke="{GOLD}" stroke-width=".35" opacity=".6"/>']
for _ in range(160):
    x = random.uniform(2, W-2)
    col = GOLDL if x < 192 else ('#9FE0C8' if x < 384 and random.random() < .5 else '#F3E3BE')
    rv.append(f'<rect x="{x:.1f}" y="{GY+random.uniform(1.5, 18):.1f}" width="{random.uniform(1.4, 5):.1f}" height=".35" fill="{col}" opacity="{random.uniform(.25, .7):.2f}"/>')
rv.append(f'<path d="M{SUNX-26} {GY+2} H{SUNX+26}" stroke="{GOLDL}" stroke-width=".8" opacity=".5"/><path d="M{SUNX-18} {GY+5} H{SUNX+18}" stroke="{GOLDL}" stroke-width=".6" opacity=".4"/><path d="M{SUNX-10} {GY+8} H{SUNX+10}" stroke="{GOLDL}" stroke-width=".5" opacity=".35"/>')
RIVER = ''.join(rv)

# --- district title plaques
def plaque(cx, title, sub, col):
    w = len(title)*3.55 + 14
    return (f'<path d="M{cx-w/2} 9 L{cx-w/2+3} 4.2 H{cx+w/2-3} L{cx+w/2} 9 L{cx+w/2-3} 13.8 H{cx-w/2+3}Z" fill="{NAVY}" stroke="{GOLD}" stroke-width=".4" opacity=".95"/>'
            + T(cx, 10.7, title, 4.8, 700, GOLDL, extra=' letter-spacing=".55"')
            + T(cx, 19.6, sub, 5.2, 600, col, fam='Cormorant Garamond', extra=' font-style="italic"'))
PLAQ = (plaque(96, 'THE MARKET DISTRICT', 'capitalist economy &#183; many owners, many lights', '#F3D58E') +
        plaque(480, 'THE PLAN DISTRICT', 'socialist (command) economy &#183; one central light', '#F0C9CF'))
PLAQ_MID = plaque(288, 'THE COMMONS', '', '#A8E6D2').replace('<text x="288" y="19.6"', '<text x="288" y="-99"')
SKY = ''.join(sk) + MARKET + MIXED + COMMAND + RIVER + PLAQ + \
      (f'<path d="M248 9 L251 4.2 H325 L328 9 L325 13.8 H251Z" fill="{NAVY}" stroke="{GOLD}" stroke-width=".4"/>' +
       T(288, 10.7, 'THE COMMONS', 4.8, 700, GOLDL, extra=' letter-spacing=".55"') +
       T(288, 19.6, 'mixed economy &#183; two lights meet', 5.2, 600, '#A8E6D2', fam='Cormorant Garamond', extra=' font-style="italic"'))
# vignette edges
SKY += f'<rect x="0" y="0" width="40" height="{H}" fill="url(#gVigL)"/><rect x="{W-40}" y="0" width="40" height="{H}" fill="url(#gVigR)"/>'

GRADS = f'''
<linearGradient id="gSky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0A1222"/><stop offset=".55" stop-color="#17274A"/><stop offset="1" stop-color="#3D3452"/></linearGradient>
<linearGradient id="gRiver" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#121D33"/><stop offset="1" stop-color="#070C17"/></linearGradient>
<radialGradient id="gSun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFE9B0"/><stop offset=".6" stop-color="#E9B653"/><stop offset="1" stop-color="#B9782A"/></radialGradient>
<radialGradient id="gHalo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#F3C36A" stop-opacity=".55"/><stop offset="1" stop-color="#F3C36A" stop-opacity="0"/></radialGradient>
<linearGradient id="gBeamGold" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#F6D27A" stop-opacity=".42"/><stop offset="1" stop-color="#F6D27A" stop-opacity="0"/></linearGradient>
<linearGradient id="gBeamIvory" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#FFF4DA" stop-opacity=".55"/><stop offset="1" stop-color="#FFF4DA" stop-opacity="0"/></linearGradient>
<linearGradient id="gVigL" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#05080F" stop-opacity=".75"/><stop offset="1" stop-color="#05080F" stop-opacity="0"/></linearGradient>
<linearGradient id="gVigR" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#05080F" stop-opacity=".75"/><stop offset="1" stop-color="#05080F" stop-opacity="0"/></linearGradient>
<linearGradient id="gTitle" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF0C2"/><stop offset=".45" stop-color="#E8BE62"/><stop offset=".55" stop-color="#C9932F"/><stop offset="1" stop-color="#F2D287"/></linearGradient>
<linearGradient id="gOmanSky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2B2340"/><stop offset=".7" stop-color="#B8643A"/><stop offset="1" stop-color="#E8A65A"/></linearGradient>
'''

# ---------------------------------------------------------------- flowcharts (176 x 24): deco diamonds
def dnode(x, y, ic, lab, col):
    lines = lab.split('|')
    t = ''.join(T(x, y+10.6+i*4.5, ln, 4.4, 500, INK, fam='Oswald') for i, ln in enumerate(lines))
    return (f'<path d="M{x} {y-6.6} L{x+6.6} {y} L{x} {y+6.6} L{x-6.6} {y}Z" fill="{NAVY}" stroke="{GOLD}" stroke-width=".6"/>'
            + use(ic, x, y, .95, GOLDL) + t)
def farr(x1, x2, y, col, lab=''):
    t = T((x1+x2)/2, y-2, lab, 3.9, 500, col, fam='Oswald', extra=' letter-spacing=".15"') if lab else ''
    return (f'<path d="M{x1} {y} H{x2-2}" stroke="{col}" stroke-width=".8"/><path d="M{x2-3} {y-1.7} L{x2} {y} L{x2-3} {y+1.7}Z" fill="{col}"/>' + t)
F_MK = (dnode(18, 7.4, 'm-people', 'Consumers', MK) + farr(27, 77, 7.4, GOLDD, 'DEMAND (BY INCOME)') + dnode(88, 7.4, 'm-tag', 'Market price', MK) +
        farr(97, 147, 7.4, GOLDD, 'PROFIT SIGNAL') + dnode(158, 7.4, 'm-gear', 'Producers', MK) +
        f'<path d="M158 20.4 V23.4 H18 V20.4" fill="none" stroke="{GOLDD}" stroke-width=".55" stroke-dasharray="1.3 .9"/><rect x="62" y="21" width="52" height="4.6" fill="{IVORY}"/>' +
        T(88, 24.4, 'variety of goods back to buyers', 3.7, 400, GOLDD, fam='Oswald'))
F_CM = (dnode(18, 7.4, 'm-plan', 'Central|authority', CM) + farr(27, 77, 7.4, BURG, 'PLANS &amp; FIXES PRICES') + dnode(88, 7.4, 'm-gear', 'State-owned|firms', CM) +
        farr(97, 147, 7.4, BURG, 'ALLOCATES') + dnode(158, 7.4, 'm-people', 'Citizens', CM))
F_MX = (dnode(18, 7.4, 'm-gov', 'Public|sector', MX) + T(53, 10.6, '+', 9, 700, EMER, fam='EB Garamond') + dnode(88, 7.4, 'm-tag', 'Private|sector', MX) +
        farr(97, 147, 7.4, EMER, 'PLANNING + PRICES') + dnode(158, 7.4, 'm-box', 'Goods &amp;|services', MX))

def svg(inner, w, h, cls='', style=''):
    return f'<svg class="{cls}" viewBox="0 0 {w} {h}" width="{w}mm" height="{h}mm" style="display:block;overflow:visible;{style}">{inner}</svg>'
def ic(i, col=GOLDD):
    return f'<svg class="ic" viewBox="-6 -6 12 12" style="color:{col}"><use href="#{i}"/></svg>'

# corner deco fan
def fan(x, y, sx, sy):
    rays = ''.join(f'<path d="M0 0 L{14*math.cos(math.radians(a)):.2f} {14*math.sin(math.radians(a)):.2f}" stroke="{GOLD}" stroke-width=".35"/>' for a in range(0, 91, 15))
    return f'<g transform="translate({x} {y}) scale({sx} {sy})">{rays}<path d="M8 0 A8 8 0 0 1 0 8" fill="none" stroke="{GOLD}" stroke-width=".4"/><path d="M14 0 A14 14 0 0 1 0 14" fill="none" stroke="{GOLD}" stroke-width=".4"/></g>'

TITLE = (f'<text x="150" y="9" font-family="Cinzel" font-weight="700" font-size="8" fill="{GOLDL}" text-anchor="middle" letter-spacing="3.2">A TALE OF</text>' +
         ''.join(f'<text x="{150+d*.22:.2f}" y="{31+d*.3:.2f}" font-family="Cinzel" font-weight="900" font-size="22" fill="{BURGD if d > 2 else "#2A0E14"}" text-anchor="middle" letter-spacing=".4">THREE ECONOMIES</text>' for d in (5, 4, 3, 2)) +
         f'<text x="150" y="31" font-family="Cinzel" font-weight="900" font-size="22" fill="url(#gTitle)" stroke="#5A3A0E" stroke-width=".25" text-anchor="middle" letter-spacing=".4">THREE ECONOMIES</text>' +
         f'<path d="M40 5.6 H100 M200 5.6 H260" stroke="{GOLD}" stroke-width=".4"/><path d="M100 5.6 l2 -1.4 l2 1.4 l-2 1.4Z M196 5.6 l2 -1.4 l2 1.4 l-2 1.4Z" fill="{GOLD}"/>')

OMAN_ART = (f'<rect x="0" y="0" width="60" height="30" fill="url(#gOmanSky)"/><circle cx="44" cy="22" r="7" fill="#F6CF7E" opacity=".9"/>'
            f'<path d="M0 24 H60 V30 H0Z" fill="#0F1A2E"/>' +
            ''.join(f'<rect x="{random.uniform(2, 58):.1f}" y="{random.uniform(25, 29):.1f}" width="{random.uniform(1.4, 4):.1f}" height=".3" fill="{GOLDL}" opacity=".6"/>' for _ in range(14)) +
            f'<path d="M4 24 V13 H3 V11 H5 V12 H7 V11 H9 V12 H11 V11 H13 V12 H15 V11 H17 V13 H16 V24Z M20 24 V17 H19 V15.4 H21 V16.2 H23 V15.4 H25 V17 H24 V24Z M16 24 V18 H20 V24Z" fill="#120B14"/>'
            f'<path d="M11 24 V20.6 Q12.2 19 13.4 20.6 V24Z" fill="#E8A65A" opacity=".6"/>'
            f'<path d="M29 24 Q28.6 18 30 13" fill="none" stroke="#120B14" stroke-width=".9"/><path d="M30 13 Q26 11 23 14 M30 13 Q34 10.6 37 13.4 M30 13 Q28 9 25 9.4 M30 13 Q32.6 9 35.4 9.6" fill="none" stroke="#120B14" stroke-width=".9"/>'
            f'<path d="M38 25.4 Q46 27.4 56 23.6 L54 27.6 Q46 29 40 27.6Z" fill="#120B14"/><path d="M47 25 V12" stroke="#120B14" stroke-width=".5"/><path d="M40 13.6 Q48 9 55 22 Q48 22 44 24Z" fill="#120B14"/>')

HTML = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>A Tale of Three Economies</title>
<link rel="stylesheet" href="fonts/fonts.css">
<style>
@page {{ size: 594mm 420mm; margin: 0; }}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:594mm;height:420mm}}
body{{font-family:'EB Garamond',serif;color:{INK};font-size:24pt;line-height:1.08;
  background:radial-gradient(260mm 160mm at 297mm 120mm,#1A2846 0%,#0C1424 70%) ,{NAVY};
  -webkit-print-color-adjust:exact;print-color-adjust:exact}}
b{{font-weight:600}}
.page{{position:relative;width:594mm;height:420mm;overflow:hidden}}
.abs{{position:absolute}}
.ic{{width:8.6mm;height:8.6mm;flex:none;overflow:visible}}
.src{{font-family:'EB Garamond';font-style:italic;font-size:14pt;color:#7A6A4E;white-space:nowrap}}
.cap{{font-family:'Cinzel';font-weight:700;letter-spacing:.22em;font-size:13pt;line-height:1}}
.ivory{{background:linear-gradient(180deg,#F7EEDC,#EFE1C4);border:.45mm solid {GOLD};outline:.3mm solid {GOLD};outline-offset:.9mm}}

/* prologue panels */
.pro{{top:11mm;width:142mm;padding:2mm 4.2mm 2.2mm}}
.pro .cap{{color:{BURG};display:flex;align-items:center;gap:2mm;margin-bottom:1.4mm}}
.pro .cap::after{{content:"";flex:1;height:.3mm;background:{GOLD}}}
.pro h2{{font-family:'EB Garamond';font-weight:600;font-size:27pt;line-height:1;margin-bottom:1.4mm;color:#1F1520}}
.pro p{{line-height:1.08}}
.qrow{{display:flex;gap:2mm;margin-top:1.8mm}}
.q{{flex:1;display:flex;gap:1.2mm;align-items:center;justify-content:center;font-family:'Cinzel';font-weight:700;font-size:17pt;color:{IVORY};background:{NAVY};border:.35mm solid {GOLD};padding:1mm .6mm;white-space:nowrap}}
.q .ic{{width:7mm;height:7mm}}

/* star billing */
.billing{{left:160mm;top:9.6mm;width:274mm;text-align:center;color:{IVORY}}}
.billing .cap{{color:{GOLD};font-size:12pt;letter-spacing:.42em;display:flex;align-items:center;justify-content:center;gap:3mm}}
.billing .cap::before,.billing .cap::after{{content:"";width:22mm;height:.3mm;background:linear-gradient(90deg,transparent,{GOLD})}}
.billing .cap::after{{transform:scaleX(-1)}}
.stars{{display:grid;grid-template-columns:repeat(4,1fr);margin-top:1.4mm}}
.stars div{{display:flex;flex-direction:column;align-items:center;border-left:.3mm solid rgba(212,168,75,.45)}}
.stars div:first-child{{border-left:none}}
.stars b{{font-family:'Cormorant Garamond';font-weight:600;font-size:22pt;line-height:1.02;color:#FFF6E2;white-space:nowrap}}
.stars i{{font-family:'Oswald';font-style:normal;font-weight:400;font-size:14.5pt;letter-spacing:.2em;color:{GOLD};line-height:1.1}}
.tagline{{font-family:'Cormorant Garamond';font-style:italic;font-weight:600;font-size:24pt;color:#E9DDC4;margin-top:1.8mm;white-space:nowrap}}
.titlesvg{{margin:.4mm auto 0}}
.sub{{font-family:'Oswald';font-weight:400;font-size:16pt;letter-spacing:.32em;color:#CBBBA0;margin-top:.6mm;white-space:nowrap}}
.sub b{{color:{GOLDL};font-weight:500}}

/* skyline */
.sky{{left:9mm;top:80mm;width:576mm;height:92mm;border-top:.4mm solid {GOLD};border-bottom:.4mm solid {GOLD}}}

/* scene cards */
.scene{{top:175.6mm;width:182mm;padding:0 3.4mm 1.6mm}}
.scene .hd{{display:flex;justify-content:space-between;align-items:baseline;margin:0 -3.4mm 1.4mm;padding:1.4mm 4mm 1.6mm;background:var(--c);color:{IVORY};border-bottom:.4mm solid {GOLD}}}
.scene .hd b{{font-family:'Cinzel';font-weight:700;font-size:19pt;letter-spacing:.06em;line-height:1}}
.scene .hd span{{font-family:'Cormorant Garamond';font-style:italic;font-weight:600;font-size:19pt;line-height:1}}
.scene ul{{list-style:none;white-space:nowrap}}
.scene li{{padding-left:5mm;position:relative;line-height:1.06}}
.scene li::before{{content:"";position:absolute;left:.6mm;top:2.6mm;width:2.2mm;height:2.2mm;transform:rotate(45deg);background:var(--c);outline:.25mm solid {GOLD};outline-offset:.35mm}}
.scene .flow{{margin:2.2mm auto 0}}

/* table */
.review{{left:13.4mm;top:256mm;width:412mm;padding:1.6mm 2.6mm 1.6mm}}
.review .ttl{{display:flex;align-items:baseline;gap:3mm;margin:0 .6mm .6mm}}
.review .ttl h2{{font-family:'Cinzel';font-weight:700;font-size:21pt;color:#1F1520;letter-spacing:.04em}}
.review .ttl .src{{margin-left:auto}}
.tg{{display:grid;grid-template-columns:92mm repeat(3,minmax(0,1fr))}}
.tg > div{{padding:.15mm 2.4mm;display:flex;align-items:center;white-space:nowrap;font-family:'Oswald';font-weight:300;font-size:24pt;line-height:1.0;border-top:.25mm solid #D3BE93}}
.tg .h{{font-family:'Cinzel';font-weight:700;font-size:16.5pt;letter-spacing:.06em;color:{IVORY};justify-content:center;padding:1.2mm 1mm;border-top:none}}
.tg .lab{{gap:2mm;font-family:'EB Garamond';font-weight:600;font-size:22pt;line-height:1;white-space:nowrap;color:#1F1520}}
.tg .sec{{grid-column:1 / -1;border-top:.45mm solid {GOLD};padding:.6mm 2.4mm .2mm}}
.tg .sec span{{font-family:'Cinzel';font-weight:700;font-size:12.5pt;letter-spacing:.3em;color:{BURG}}}
.c1{{background:rgba(184,134,43,.10)}} .c2{{background:rgba(31,99,82,.09)}} .c3{{background:rgba(122,34,48,.08)}}
.c1 b{{color:#8A6114}} .c2 b{{color:{EMERD}}} .c3 b{{color:{BURGD}}}
.tg b{{font-weight:500}}
.tg ul{{list-style:none}}
.tg li{{display:flex;gap:1.6mm;align-items:center;line-height:1.0}}
.tg li::before{{content:"";width:2.3mm;height:2.3mm;transform:rotate(45deg);flex:none}}
.adv li::before{{background:#2F7A4E}} .dis li::before{{background:{BURG}}}

/* oman */
.oman{{left:432mm;top:256mm;width:148.6mm;padding:1.8mm 3.4mm 1.6mm}}
.oman .top{{display:grid;grid-template-columns:44mm 1fr;column-gap:3mm;align-items:center;margin-bottom:.8mm}}
.oman .cap{{color:{EMER}}}
.oman h2{{font-family:'Cinzel';font-weight:700;font-size:19pt;line-height:1.05;color:#1F1520}}
.oman h2 em{{font-style:normal;color:{EMER}}}
.oman h4{{font-family:'Cinzel';font-weight:700;font-size:13pt;letter-spacing:.2em;margin:.8mm 0 .2mm;display:flex;align-items:center;gap:2mm}}
.oman h4::after{{content:"";flex:1;height:.25mm;background:{GOLD}}}
.oman .it{{display:flex;gap:1.8mm;align-items:center;line-height:1.04;margin-top:.5mm}}
.oman .it .ic{{width:7mm;height:7mm}}

/* epilogue + references billing block */
.epi{{left:13mm;width:568mm;text-align:center;font-family:'Cormorant Garamond';font-style:italic;font-weight:600;font-size:24pt;color:#EADFC7;white-space:nowrap}}
.epi b{{font-family:'Cinzel';font-style:normal;font-weight:700;font-size:15pt;letter-spacing:.3em;color:{GOLD};margin-right:3mm}}
.refs{{left:21mm;width:553mm;display:grid;grid-template-columns:42mm 1fr;column-gap:3mm;color:#C9BBA0;border-top:.3mm solid rgba(212,168,75,.6);padding-top:1.2mm}}
.refs h3{{font-family:'Cinzel';font-weight:700;font-size:15pt;color:{GOLD};letter-spacing:.08em;line-height:1.1}}
.refs h3 small{{display:block;font-family:'Oswald';font-weight:300;font-size:9.5pt;letter-spacing:.2em;color:#9C8E74}}
.refs ul{{columns:4;column-gap:4mm;list-style:none;font-family:'Oswald';font-weight:300;font-size:8.6pt;line-height:1.14;letter-spacing:.01em}}
.refs li{{break-inside:avoid;padding-left:3mm;text-indent:-3mm;margin-bottom:.3mm}}
.refs i{{font-style:italic}}
</style></head>
<body><div class="page">
<svg width="0" height="0" style="position:absolute"><defs>{GRADS}{ICONS}</defs></svg>

<!-- frame -->
<svg class="abs" style="left:0;top:0" width="594mm" height="420mm" viewBox="0 0 594 420">
  <rect x="4.2" y="4.2" width="585.6" height="411.6" fill="none" stroke="{GOLD}" stroke-width=".7"/>
  <rect x="6" y="6" width="582" height="408" fill="none" stroke="{GOLD}" stroke-width=".25"/>
  {fan(6, 6, 1, 1)}{fan(588, 6, -1, 1)}{fan(6, 414, 1, -1)}{fan(588, 414, -1, -1)}
</svg>

<!-- PROLOGUE -->
<div class="abs ivory pro" style="left:13mm">
  <div class="cap">PROLOGUE</div>
  <h2>What is an economic system?</h2>
  <p>The <b>means by which a society or government organises and distributes</b> its resources, goods and services: its <b>mode of production and distribution</b>. <span class="src">(Fernando, 2026)</span></p>
</div>
<div class="abs ivory pro" style="left:439mm">
  <div class="cap">THE CONFLICT</div>
  <h2>Why every society needs one</h2>
  <p>Resources are <b>scarce</b>, wants are <b>unlimited</b>: every society must answer three central questions. <span class="src">(Mankiw, 2021)</span></p>
  <div class="qrow"><div class="q">{ic('m-what', GOLDL)}WHAT?</div><div class="q">{ic('m-gear', GOLDL)}HOW?</div><div class="q" style="flex:1.5">{ic('m-people', GOLDL)}FOR WHOM?</div></div>
</div>

<!-- STAR BILLING + TITLE -->
<div class="abs billing">
  <div class="cap">Student Names</div>
  <div class="stars">
    <div><b>Mais altoubi</b><i>31j2573</i></div>
    <div><b>Alshima Almahrooqi</b><i>21S252540139</i></div>
    <div><b>Nardeen alfarsi</b><i>21J2583</i></div>
    <div><b>shatha al_umeiri</b><i>21J25157</i></div>
  </div>
  <div class="tagline">One world. Scarce resources. Three ways to decide what, how and for whom.</div>
  <svg class="titlesvg" viewBox="0 0 300 34" width="270mm" height="30.6mm" style="display:block;overflow:visible">{TITLE}</svg>
  <div class="sub"><b>CHAPTER 2</b> &middot; ECONOMIC SYSTEMS &middot; <b>BSEC1103</b> PRINCIPLES OF ECONOMICS</div>
</div>

<!-- THE CITY -->
<svg class="abs sky" viewBox="0 0 576 92">{SKY}</svg>

<!-- SCENES -->
<div class="abs ivory scene" style="left:13mm;--c:{MK}">
  <div class="hd"><b>Capitalist Economy</b><span>market &middot; free</span></div>
  <ul><li><b>Private</b> ownership; <b>no government</b> interference</li><li>Freedom to start any business</li><li>Consumers buy by income; firms offer variety</li><li>Guided by <b>profit</b> &amp; <b>competition</b></li></ul>
  {svg(F_MK, 176, 26, 'flow')}
</div>
<div class="abs ivory scene" style="left:206mm;--c:{MX}">
  <div class="hd"><b>Mixed Economy</b><span>public + private</span></div>
  <ul><li><b>Public &amp; private</b> sectors co-exist</li><li><b>Both</b> decide output &amp; distribution</li><li>Economic <b>planning</b> controls the economy</li><li>Protects <b>consumer &amp; labour rights</b></li></ul>
  {svg(F_MX, 176, 26, 'flow')}
</div>
<div class="abs ivory scene" style="left:399mm;--c:{CM}">
  <div class="hd"><b>Socialist Economy</b><span>command</span></div>
  <ul><li><b>Government</b> owns &amp; controls resources</li><li><b>Central authority</b> decides everything</li><li><b>Fixed</b>, reasonable prices; quality goods</li><li>Aim: <b>social welfare</b> &amp; equal jobs for all</li></ul>
  {svg(F_CM, 176, 26, 'flow')}
</div>

<!-- THE REVIEW -->
<div class="abs ivory review">
  <div class="ttl"><span class="cap" style="color:{BURG}">THE REVIEW</span><h2>Three central questions &amp; comparison table</h2><span class="src">(Fernando, 2026)</span></div>
  <div class="tg">
    <div class="h" style="background:{NAVY};justify-content:flex-start;padding-left:3mm">Criteria</div>
    <div class="h" style="background:{MK}">Capitalist</div><div class="h" style="background:{MX}">Mixed</div><div class="h" style="background:{CM}">Socialist (Command)</div>
    <div class="sec"><span>THE THREE CENTRAL QUESTIONS</span></div>
    <div class="lab">{ic('m-what', BURG)}What to produce?</div><div class="c1">Whatever consumers demand</div><div class="c2">Demand + national plans</div><div class="c3">Central authority&rsquo;s plan</div>
    <div class="lab">{ic('m-gear', BURG)}How to produce?</div><div class="c1">Producers choose, for profit</div><div class="c2">Private firms + public sector</div><div class="c3">State organises production</div>
    <div class="lab">{ic('m-people', BURG)}For whom?</div><div class="c1">Buyers, by their income</div><div class="c2">Market + social welfare</div><div class="c3">State allocates to citizens</div>
    <div class="sec"><span>COMPARISON TABLE</span></div>
    <div class="lab">{ic('m-key', BURG)}Ownership of resources</div><div class="c1"><span><b>Private:</b> citizens &amp; institutions</span></div><div class="c2"><span><b>Public + private</b> sectors</span></div><div class="c3"><span><b>Government:</b> banks, industry</span></div>
    <div class="lab">{ic('m-gov', BURG)}Role of government</div><div class="c1"><span><b>Little:</b> no interference</span></div><div class="c2"><span><b>Plans</b> &amp; controls</span></div><div class="c3"><span><b>Total:</b> decides all</span></div>
    <div class="lab">{ic('m-tag', BURG)}Price mechanism</div><div class="c1"><span><b>Free</b> market prices</span></div><div class="c2"><span><b>Prices</b> + planning</span></div><div class="c3"><span><b>Fixed</b> by central authority</span></div>
    <div class="lab">{ic('m-target', BURG)}Motive</div><div class="c1"><span><b>Profit</b></span></div><div class="c2"><span><b>Profit + social interest</b></span></div><div class="c3"><span><b>Social welfare</b></span></div>
    <div class="lab">{ic('m-up', '#2F7A4E')}Advantages</div>
    <div class="c1"><ul class="adv"><li>Equal opportunities</li><li>Innovation &amp; fast growth</li></ul></div>
    <div class="c2"><ul class="adv"><li>Best allocation of resources</li><li>Via prices, profit &amp; liberty</li></ul></div>
    <div class="c3"><ul class="adv"><li>Efficient use; stability</li><li>Max welfare; no monopoly</li></ul></div>
    <div class="lab">{ic('m-down', BURG)}Disadvantages</div>
    <div class="c1"><ul class="dis"><li>Rich richer, poor poorer</li><li>No welfare &rarr; poverty</li></ul></div>
    <div class="c2"><ul class="dis"><li>Sectors may not cooperate</li><li>Inefficient public sector</li></ul></div>
    <div class="c3"><ul class="dis"><li>Bureaucracy; no freedom</li><li>No technology or competition</li></ul></div>
  </div>
</div>

<!-- OMAN -->
<div class="abs ivory oman">
  <div class="top"><svg viewBox="0 0 60 30" style="display:block;width:44mm;height:22mm;outline:.3mm solid {GOLD}">{OMAN_ART}</svg><div><div class="cap">THE SEQUEL: OMAN</div><h2>Oman: a <em>mixed economy</em></h2></div></div>
  <h4 style="color:{BURG}">GOVERNMENT SECTOR</h4>
  <div class="it">{ic('m-compass', BURG)}<span>Plans the economy: <b>Oman Vision 2040</b></span></div>
  <div class="it">{ic('m-key', BURG)}<span>Owns state firms: <b>Oman Investment Authority</b></span></div>
  <div class="it">{ic('m-shield', BURG)}<span>Protects consumers &amp; workers by law</span></div>
  <h4 style="color:{EMER}">PRIVATE SECTOR</h4>
  <div class="it">{ic('m-branch', EMER)}<span>Leads diversification beyond oil</span></div>
  <div class="it">{ic('m-bridge', EMER)}<span>Partners the state in <b>PPP</b> projects</span></div>
  <div class="it">{ic('m-gear', EMER)}<span>Takes over state firms via <b>privatisation</b></span></div>
  <span class="src" style="font-size:12pt;white-space:normal;line-height:1.1">(Oman Vision 2040 Main Committee, 2019; Royal Decrees 66/2014, 51/2019, 52/2019, 61/2020, 53/2023)</span>
</div>

<div class="abs epi" id="epi"><b>EPILOGUE</b>No system is perfect; the mixed economy blends market freedom with social welfare, the model Oman follows.</div>
<div class="abs refs" id="refs">
  <h3>References<small>APA 7TH ED.</small></h3>
  <ul>
    <li>Fernando, G. A. (2026). <i>Chapter 2: Economic systems</i> [PowerPoint slides]. BSEC1103 Principles of Economics, University of Technology and Applied Sciences.</li>
    <li>Mankiw, N. G. (2021). <i>Principles of economics</i> (9th ed.). Cengage Learning.</li>
    <li>Oman Vision 2040 Main Committee. (2019). <i>Oman Vision 2040: Vision document</i>. Sultanate of Oman. https://www.oman2040.om</li>
    <li>Royal Decree No. 51/2019 issuing the Privatization Law. (2019). <i>Official Gazette of the Sultanate of Oman</i>.</li>
    <li>Royal Decree No. 52/2019 promulgating the Public-Private Partnership Law. (2019). <i>Official Gazette of the Sultanate of Oman</i>. https://decree.om/2019/rd20190052/</li>
    <li>Royal Decree No. 53/2023 promulgating the Labour Law. (2023). <i>Official Gazette of the Sultanate of Oman</i>.</li>
    <li>Royal Decree No. 61/2020 establishing the Oman Investment Authority. (2020). <i>Official Gazette of the Sultanate of Oman</i>. https://decree.om/2020/rd20200061/</li>
    <li>Royal Decree No. 66/2014 promulgating the Consumer Protection Law. (2014). <i>Official Gazette of the Sultanate of Oman</i>.</li>
  </ul>
</div>
</div>
<script>
document.fonts.ready.then(()=>{{
  const mm=v=>v/3.7795;
  const b=Math.max(document.querySelector('.review').getBoundingClientRect().bottom, document.querySelector('.oman').getBoundingClientRect().bottom);
  const epi=document.getElementById('epi'); epi.style.top=(mm(b)+1.6)+'mm';
  const refs=document.getElementById('refs'); refs.style.top=(mm(epi.getBoundingClientRect().bottom)+.6)+'mm';
  document.body.dataset.ready='1';
}});
</script>
</body></html>'''
(HERE / 'poster.html').write_text(HTML)
print('ok')
