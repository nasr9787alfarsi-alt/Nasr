#!/usr/bin/env python3
"""WHO DECIDES? Economic Systems - A2 landscape (594 x 420 mm). Glossy night-sky style."""
import pathlib, random, math
HERE = pathlib.Path(__file__).parent
exec((HERE / 'lib' / 'islands_symbols.py').read_text().split('# ------------------------------------------------------------------ ISLANDS SCENE')[0])
random.seed(11)

GOLD, GOLDD, GOLDS = '#F2B53A', '#B7801A', '#FFF1D2'
CORAL, CORALD, CORALS = '#EE6A55', '#B9412F', '#FFE3DC'
TEAL, TEALD, TEALS = '#22A98C', '#147560', '#DCF4EC'
CREAM = '#FFF8EE'; NIGHT = '#1D1846'; VIO = '#4B3A9E'

def lg(id_, a, b, x2=0, y2=1):
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'
def rg(id_, a, b, cx=.35, cy=.3):
    return f'<radialGradient id="{id_}" cx="{cx}" cy="{cy}" r=".75"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></radialGradient>'

GRAD = ''.join([
    lg('gGold', '#FFE49C', '#E9A222'), rg('gCoin', '#FFF0B8', '#E39C17'), lg('gCoral', '#FFA592', '#E5523C'),
    lg('gTeal', '#7DE6CD', '#1E9F83'), lg('gCreamV', '#FFFFFF', '#EFE2CC'), lg('gLav', '#D6D0FA', '#8E84D8'),
    lg('gPanelGold', '#FFEFC4', '#F6C25E'), lg('gPanelCoral', '#FFD4C9', '#F2866E'), lg('gPanelTeal', '#CFF5EA', '#58C9AC'),
    rg('gOrbV', '#D8CCFF', '#5B43C9'), rg('gOrbT', '#A6F5E0', '#17977B'), rg('gOrbG', '#FFF0B0', '#E19A12'), rg('gOrbC', '#FFC4B6', '#D9452F'),
    lg('gSand', '#F6DDAE', '#D9AE6C'), lg('gWood', '#C98E5A', '#8B5A30'), lg('gSea', '#5CC3D0', '#2A8C9C'),
    lg('gTitleGold', '#FFE7A0', '#EFA52A'), lg('gTitleCream', '#FFFFFF', '#F3E6CF'),
])

def gear_path(r1, r2, n):
    pts = []
    for i in range(n*4):
        a = i/(n*4)*2*math.pi
        r = r2 if (i % 4) in (1, 2) else r1
        pts.append((r*math.cos(a), r*math.sin(a)))
    return 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in pts) + 'Z'

GLOSS = f'''
<g id="spark"><path d="M0 -3 Q.5 -.5 3 0 Q.5 .5 0 3 Q-.5 .5 -3 0 Q-.5 -.5 0 -3Z" fill="#FFF3C4"/></g>
<g id="shadow"><ellipse cx="0" cy="0" rx="10" ry="1.4" fill="#000" opacity=".14"/></g>
<g id="coin"><circle r="5" fill="url(#gCoin)"/><circle r="3.7" fill="none" stroke="#C98A16" stroke-width=".55"/>
  <path d="M0 -2.2 L.6 -.7 L2.2 -.7 L.9 .3 L1.4 1.9 L0 .9 L-1.4 1.9 L-.9 .3 L-2.2 -.7 L-.6 -.7Z" fill="#D8941A"/>
  <ellipse cx="-1.8" cy="-2.4" rx="1.6" ry=".9" fill="#fff" opacity=".65"/></g>
<g id="cstack">{''.join(f'<ellipse cx="0" cy="{-i*1.7:.1f}" rx="5" ry="1.6" fill="#C9850F"/><ellipse cx="0" cy="{-i*1.7-.7:.1f}" rx="5" ry="1.6" fill="url(#gGold)"/>' for i in range(5))}
  <ellipse cx="0" cy="-7.5" rx="3.4" ry=".9" fill="none" stroke="#C98A16" stroke-width=".4"/><ellipse cx="-1.8" cy="-7.9" rx="1.4" ry=".5" fill="#fff" opacity=".6"/></g>
<g id="gshop">
  <rect x="-9" y="-12" width="18" height="12" rx=".8" fill="url(#gCreamV)"/>
  <rect x="-6.6" y="-8.6" width="6.2" height="5" rx=".5" fill="#BFE6F2"/><path d="M-6.6 -8.6 L-3 -8.6 L-6.6 -5.4Z" fill="#fff" opacity=".7"/>
  <rect x="1.6" y="-7.6" width="4.6" height="7.6" rx=".5" style="fill:var(--c2,{CORALD})"/>
  <rect x="-10.5" y="-16.6" width="21" height="4.6" rx="1" fill="#fff"/>
  {''.join(f'<rect x="{-10.5+k*4.2:.1f}" y="-16.6" width="2.1" height="4.6" style="fill:var(--c,{CORAL})"/>' for k in range(5))}
  <path d="M-10.5 -12 {''.join('a1.05 1.2 0 0 0 2.1 0 ' for _ in range(10))}Z" style="fill:var(--c,{CORAL})"/>
  <rect x="-5" y="-20.6" width="10" height="3.4" rx="1" style="fill:var(--c2,{CORALD})"/>
</g>
<g id="ggov">
  <rect x="-12.5" y="-2.2" width="25" height="2.2" rx=".6" fill="#E3D3B8"/>
  <rect x="-11" y="-12" width="22" height="9.8" fill="url(#gCreamV)"/>
  {''.join(f'<rect x="{x}" y="-11.4" width="2.4" height="9.2" fill="#fff"/><rect x="{x+1.6}" y="-11.4" width=".8" height="9.2" fill="#E2D5C0"/>' for x in (-9.4, -4.4, .6, 5.6))}
  <rect x="-12" y="-13.6" width="24" height="1.8" rx=".5" fill="#F1E5D1"/>
  <path d="M-12.6 -13.6 L0 -20.4 L12.6 -13.6Z" style="fill:var(--roof,{CORAL})"/>
  <circle cx="0" cy="-16" r="1.5" fill="url(#gGold)"/>
  <path d="M0 -20.4 V-25" stroke="#8C7A66" stroke-width=".5"/><path d="M0 -25 L3.6 -24 L0 -23Z" style="fill:var(--roof,{CORAL})"/>
</g>
<g id="gfac">
  <rect x="6.4" y="-17" width="3.4" height="17" fill="#7E74C8"/><rect x="6.4" y="-17" width="3.4" height="1.6" fill="#5C52A6"/>
  <path d="M-11 0 V-8 L-5.5 -12 V-8 L0 -12 V-8 L5.5 -12 V0Z" fill="url(#gLav)"/>
  {''.join(f'<rect x="{x}" y="-5.4" width="2.6" height="2.4" rx=".3" fill="#FFF1C9"/>' for x in (-8.6, -3.3, 2))}
  <circle cx="8.6" cy="-20" r="1.8" fill="#fff" opacity=".85"/><circle cx="10.6" cy="-22.6" r="2.3" fill="#fff" opacity=".7"/>
</g>
<g id="gtag"><path d="M0 -3 H6 L8.6 0 L6 3 H0 Q-1 3 -1 2 V-2 Q-1 -3 0 -3Z" fill="url(#gGold)"/><circle cx="5.8" cy="0" r=".8" fill="#fff"/><path d="M.2 -2.2 H5" stroke="#fff" stroke-width=".5" opacity=".6"/></g>
<g id="ggear"><path d="{gear_path(5.2, 7, 9)}" style="fill:var(--g,url(#gCoral))"/><circle r="3.4" fill="#fff" opacity=".9"/><circle r="1.6" style="fill:var(--gc,{CORALD})"/>
  <path d="M-4 -4.6 A6 6 0 0 1 2 -6" stroke="#fff" stroke-width=".8" fill="none" opacity=".55"/></g>
<g id="gbag"><path d="M-5 -10 H5 L6 0 H-6Z" fill="url(#gCoral)"/><path d="M-2.4 -10 Q-2.4 -14 0 -14 Q2.4 -14 2.4 -10" fill="none" stroke="{CORALD}" stroke-width=".8"/><rect x="-4.6" y="-9.4" width="1.4" height="8.4" fill="#fff" opacity=".35"/></g>
<g id="gclip"><rect x="-6" y="-9" width="12" height="16" rx="1.4" fill="url(#gWood)"/><rect x="-4.8" y="-7" width="9.6" height="12.6" rx=".6" fill="#fff"/>
  <rect x="-2.6" y="-10" width="5.2" height="2.6" rx=".8" fill="#9AA3B8"/>{''.join(f'<rect x="-3.4" y="{y}" width="{w}" height=".8" rx=".4" fill="#C9CEDB"/>' for y, w in ((-4.6, 6.8), (-2.2, 6.8), (.2, 5), (2.6, 6)))}</g>
<g id="glock"><path d="M-2.6 -4 V-6 Q-2.6 -9 0 -9 Q2.6 -9 2.6 -6 V-4" fill="none" stroke="#A9B0C0" stroke-width="1.2"/><rect x="-4" y="-4.4" width="8" height="6.6" rx="1.2" fill="url(#gGold)"/><circle cx="0" cy="-1.6" r=".9" fill="{GOLDD}"/><rect x="-.35" y="-1.4" width=".7" height="2" fill="{GOLDD}"/></g>
<g id="gfort">
  <path d="M-11 0 V-20 H-12.4 V-23.4 H-10 V-21.8 H-7.6 V-23.4 H-5.2 V-21.8 H-2.8 V-23.4 H-.4 V-21.8 H2 V-23.4 H4.4 V-21.8 H6.8 V-23.4 H9.2 V-21.8 H11.6 V-23.4 H12.4 V-20 H11 V0Z" fill="url(#gSand)"/>
  <path d="M-3 0 V-6 Q0 -9.4 3 -6 V0Z" fill="#8B5A30"/><path d="M-8 -16 V-18.6 Q-6.8 -20 -5.6 -18.6 V-16Z M5.6 -16 V-18.6 Q6.8 -20 8 -18.6 V-16Z" fill="#8B5A30"/>
  <path d="M18 0 V-14 H16.6 V-16.6 H18.8 V-15.4 H21 V-16.6 H23.2 V-15.4 H25.4 V-16.6 H27.6 V-14 H26.2 V0Z" fill="url(#gSand)"/><path d="M11 -10 H18 V0 H11Z" fill="#F0D3A0"/>
</g>
<g id="gdhow"><path d="M-15 -4 Q-1 1 16 -6 L13 1.6 Q0 4.6 -11 1.6Z" fill="url(#gWood)"/><path d="M0 -2 V-24" stroke="#6B4528" stroke-width=".9"/>
  <path d="M-12 -21 Q2 -30 13 -9 Q2 -9 -5 -5 Z" fill="#FFF8EC"/><path d="M-12 -21 Q2 -30 13 -9" fill="none" stroke="#E2D3B6" stroke-width=".5"/><path d="M0 -24 L5 -22.5 L0 -21Z" fill="{CORAL}"/></g>
<g id="gpalm"><path d="M0 0 Q-.6 -8 1.4 -15" fill="none" stroke="#9C6B3F" stroke-width="1.6" stroke-linecap="round"/>
  <path d="M1.4 -15 Q-4 -18 -8 -14 Q-3.6 -16 1.4 -15Z M1.4 -15 Q6.4 -18.6 10 -14 Q5.6 -16.4 1.4 -15Z M1.4 -15 Q-2 -21 -6 -21 Q-1 -19.4 1.4 -15Z M1.4 -15 Q4.4 -21.4 8.4 -20.4 Q3.6 -19.6 1.4 -15Z" fill="{TEAL}"/></g>
<g id="gperson"><path d="M-3.2 0 V-5.2 Q-3.2 -8.4 0 -8.4 Q3.2 -8.4 3.2 -5.2 V0Z" style="fill:var(--shirt,{TEAL})"/><circle cx="0" cy="-10.8" r="2.4" fill="#F0C29C"/><path d="M-2.4 -11.1 Q-2.5 -13.6 0 -13.55 Q2.6 -13.6 2.4 -10.9 Q.6 -12.3 -2.4 -11.1Z" fill="#3A2A3C"/></g>
'''

def use(i, x, y, s=1.0, style='', rot=0):
    st = f' style="{style}"' if style else ''
    r = f' rotate({rot})' if rot else ''
    return f'<use href="#{i}" transform="translate({x:.2f} {y:.2f}){r} scale({s})"{st}/>'
def T(x, y, txt, size=5, w=700, col=INK, anchor='middle', fam='Poppins', extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" text-anchor="{anchor}" fill="{col}" font-family="{fam}"{extra}>{txt}</text>'
def sparks(n, W, H, smin=.5, smax=1.2, seed=0):
    random.seed(seed)
    return ''.join(use('spark', random.uniform(2, W-2), random.uniform(2, H-2), random.uniform(smin, smax)) for _ in range(n))

# ---------- header decorations
def bubble(x, y, w, txt, grad, tail_dx=-6):
    h = 9
    return (f'<ellipse cx="{x+tail_dx+2}" cy="{y+h/2+6}" rx="{w/2.4}" ry="1.2" fill="#000" opacity=".18"/>'
            f'<path d="M{x+tail_dx-1} {y+h/2-1} L{x+tail_dx-3} {y+h/2+4.4} L{x+tail_dx+4} {y+h/2-1}Z" fill="url(#{grad})"/>'
            f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="{h/2}" fill="url(#{grad})"/>'
            f'<rect x="{x-w/2+3}" y="{y-h/2+1.1}" width="{w-6}" height="1.6" rx=".8" fill="#fff" opacity=".45"/>'
            + T(x, y+2.1, txt, 5.6, 800, '#fff'))
LEFT = (sparks(9, 118, 46, seed=1) +
        f'<circle cx="8" cy="9" r="4.2" fill="url(#gOrbT)"/><circle cx="111" cy="40" r="3" fill="url(#gOrbV)"/>' +
        bubble(28, 12, 30, 'WHAT?', 'gGold', 6) + bubble(70, 21, 26, 'HOW?', 'gCoral', -4) + bubble(44, 33, 42, 'FOR WHOM?', 'gTeal', 10) +
        use('cstack', 98, 18, 1.1) + use('coin', 107, 10, .9) + use('coin', 88, 30, .7))
RIGHT = (sparks(9, 118, 46, seed=2) + f'<circle cx="110" cy="8" r="4" fill="url(#gOrbV)"/><circle cx="8" cy="38" r="2.6" fill="url(#gOrbG)"/>' +
         f'<ellipse cx="60" cy="43" rx="22" ry="2" fill="#000" opacity=".2"/>' +
         f'<path d="M54 43 H66 L63 39 H57Z" fill="url(#gGold)"/><rect x="58.8" y="9" width="2.4" height="30" rx="1" fill="url(#gGold)"/>' +
         f'<circle cx="60" cy="8" r="2.6" fill="url(#gCoin)"/><rect x="26" y="10" width="68" height="2.2" rx="1.1" fill="url(#gGold)"/>' +
         ''.join(f'<path d="M{x} 11.2 L{x-9} 27 M{x} 11.2 L{x+9} 27" stroke="#E9C26A" stroke-width=".4"/>' for x in (29, 91)) +
         f'<path d="M17 27 H41 Q41 33 29 33 Q17 33 17 27Z" fill="url(#gGold)"/><path d="M79 27 H103 Q103 33 91 33 Q79 33 79 27Z" fill="url(#gGold)"/>' +
         use('cstack', 29, 26.4, .9) + use('coin', 35, 21.6, .6) + use('ggov', 91, 27, .62, f'--roof:{CORAL}') +
         T(29, 39, 'MARKET', 3.6, 800, '#FFE6A6') + T(91, 39, 'STATE', 3.6, 800, '#FFE6A6'))

# ---------- card header illustrations (176 x 34)
def panel(grad):
    return (f'<rect x="0" y="0" width="176" height="34" rx="3.6" fill="url(#{grad})"/>'
            f'<circle cx="150" cy="9" r="9" fill="#fff" opacity=".28"/><circle cx="150" cy="9" r="5.6" fill="#fff" opacity=".35"/>'
            f'<path d="M0 27 Q44 23 88 26 T176 25 V30.4 Q176 34 172.4 34 H3.6 Q0 34 0 30.4Z" fill="#fff" opacity=".22"/>')
def cloud(x, y, s=1):
    return f'<g transform="translate({x} {y}) scale({s})"><ellipse cx="0" cy="0" rx="6" ry="2.6" fill="#fff" opacity=".9"/><circle cx="-2" cy="-1.6" r="2.6" fill="#fff" opacity=".9"/><circle cx="1.8" cy="-2.2" r="3" fill="#fff" opacity=".9"/></g>'

CAP_ART = (panel('gPanelGold') + cloud(20, 9, .9) + cloud(118, 7, .8) + sparks(5, 176, 20, .4, .7, seed=3) +
           use('shadow', 44, 30, 1.6) + use('gshop', 30, 30, 1.0, f'--c:{CORAL};--c2:{CORALD}') + use('gshop', 54, 30, 1.0, f'--c:{TEAL};--c2:{TEALD}') +
           use('gshop', 78, 30, 1.0, f'--c:{VIO};--c2:#33286F') +
           use('gtag', 19, 16, .8, ) + use('gtag', 66, 14, .8) + use('gbag', 101, 30, 1.0) + use('gperson', 112, 30, 1.0, f'--shirt:{VIO}') +
           use('cstack', 140, 30, 1.1) + use('coin', 151, 22, .8) + use('coin', 160, 29, .6) +
           T(30, 30-20.6+2.7, 'SHOP', 2.4, 800, '#fff') + T(54, 30-20.6+2.7, 'SHOP', 2.4, 800, '#fff') + T(78, 30-20.6+2.7, 'SHOP', 2.4, 800, '#fff'))
COM_ART = (panel('gPanelCoral') + cloud(16, 8, .8) + cloud(160, 20, .7) + sparks(5, 176, 20, .4, .7, seed=4) +
           use('shadow', 88, 30, 1.8) + use('ggov', 88, 30, 1.25, f'--roof:{CORALD}') +
           use('gfac', 34, 30, .9) + use('gfac', 56, 30, .9) + use('gfac', 120, 30, .9) + use('gfac', 142, 30, .9) +
           use('gclip', 160, 18, .95) + use('glock', 16, 22, 1.0) + use('gtag', 6, 26, .8) +
           f'<path d="M88 4 V-2" stroke="none"/>')
MIX_ART = (panel('gPanelTeal') + cloud(150, 8, .8) + sparks(5, 176, 20, .4, .7, seed=5) +
           use('shadow', 40, 30, 1.4) + use('ggov', 34, 30, .95, f'--roof:{CORAL}') +
           use('ggear', 78, 16, 1.25, f'--g:url(#gCoral);--gc:{CORALD}') + use('ggear', 94, 21.6, 1.05, f'--g:url(#gGold);--gc:{GOLDD}') +
           use('shadow', 136, 30, 1.4) + use('gshop', 132, 30, 1.0, f'--c:{GOLD};--c2:{GOLDD}') + use('gperson', 152, 30, 1.0, f'--shirt:{CORAL}') +
           T(34, 33, 'PUBLIC', 2.8, 800, '#0F5A49') + T(132, 33, 'PRIVATE', 2.8, 800, '#0F5A49') + T(86, 33, 'working together', 3.0, 700, '#0F5A49'))

# ---------- flowcharts (170 x 26)
def node(x, y, ic, lab, col):
    lines = lab.split('|')
    t = ''.join(T(x, y+11.6+i*4.6, ln, 4.4, 700, INK, fam='Poppins') for i, ln in enumerate(lines))
    return (f'<circle cx="{x}" cy="{y+.6}" r="6.6" fill="#000" opacity=".1"/><circle cx="{x}" cy="{y}" r="6.6" fill="#fff" stroke="{col}" stroke-width="1"/>'
            + use(ic, x, y, .9) + t)
def arr(x1, x2, y, col, lab=''):
    t = T((x1+x2)/2, y-2.2, lab, 3.8, 700, col, fam='Poppins') if lab else ''
    return f'<path d="M{x1} {y} H{x2-2}" stroke="{col}" stroke-width="1" stroke-linecap="round"/><path d="M{x2-3} {y-1.9} L{x2} {y} L{x2-3} {y+1.9}Z" fill="{col}"/>' + t
F_CAP = (node(18, 8, 'i-whom', 'Consumers', GOLD) + arr(27, 75, 8, GOLDD, 'demand (by income)') + node(85, 8, 'i-tag', 'Market price', GOLD) +
         arr(94, 142, 8, GOLDD, 'profit signal') + node(152, 8, 'i-how', 'Producers', GOLD) +
         f'<path d="M152 24.6 V27.4 H18 V24.6" fill="none" stroke="{GOLDD}" stroke-width=".7" stroke-dasharray="1.4 .9"/><path d="M16.4 25.6 L18 23.4 L19.6 25.6Z" fill="{GOLDD}"/>'
         f'<rect x="57" y="25" width="56" height="4.6" fill="{CREAM}"/>' + T(85, 28.4, 'variety of goods to buyers', 3.6, 700, GOLDD, fam='Poppins'))
F_COM = (node(18, 8, 'i-plan', 'Central|authority', CORAL) + arr(27, 75, 8, CORALD, 'plans &amp; fixes prices') + node(85, 8, 'i-how', 'State-owned|firms', CORAL) +
         arr(94, 142, 8, CORALD, 'allocates goods') + node(152, 8, 'i-whom', 'Citizens', CORAL))
F_MIX = (node(18, 8, 'i-gov', 'Public|sector', TEAL) + T(51.5, 11.2, '+', 9, 800, TEALD, fam='Poppins') + node(85, 8, 'i-tag', 'Private|sector', TEAL) +
         arr(94, 142, 8, TEALD, 'planning + prices') + node(152, 8, 'i-what', 'Goods &amp;|services', TEAL))

def svg(inner, w, h, cls='', style=''):
    return f'<svg class="{cls}" viewBox="0 0 {w} {h}" width="{w}mm" height="{h}mm" style="display:block;overflow:visible;{style}">{inner}</svg>'
def ic(i, s=1.0):
    return f'<svg class="ic" viewBox="-6 -6 12 12"><use href="#{i}" transform="scale({s})"/></svg>'

TITLE = (''.join(T(0+d*.25, 30+d*.45, 'Who Decides?', 31, 800, VIO if d > 1 else '#2B2066', anchor='start', extra=' letter-spacing="-.6"') for d in (6, 5, 4, 3, 2)) +
         f'<text x="0" y="30" font-size="31" font-weight="800" font-family="Poppins" letter-spacing="-.6"><tspan fill="url(#gTitleCream)">Who </tspan><tspan fill="url(#gTitleGold)">Decides?</tspan></text>')

OMAN_ART = (f'<rect x="0" y="0" width="64" height="30" rx="3" fill="url(#gPanelTeal)"/><circle cx="52" cy="8" r="4.4" fill="url(#gOrbG)"/>'
            f'<path d="M0 22 H64 V27 Q64 30 61 30 H3 Q0 30 0 27Z" fill="url(#gSea)"/>' + f'<path d="M2 22 Q14 16 30 17 Q40 18 46 22Z" fill="url(#gSand)"/>' +
            use('gfort', 20, 21, .62) + use('gpalm', 6, 22, .55) + use('gdhow', 52, 28, .55))

HTML = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Who Decides? Economic Systems</title>
<link rel="stylesheet" href="fonts/fonts.css">
<style>
@page {{ size: 594mm 420mm; margin: 0; }}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:594mm;height:420mm}}
body{{font-family:'Bricolage Grotesque',sans-serif;font-stretch:semi-condensed;color:#2A2540;font-size:24pt;line-height:1.12;
  background:radial-gradient(120mm 90mm at 300mm 30mm,#4A3A9C 0%,rgba(74,58,156,0) 100%),linear-gradient(165deg,#221C55 0%,#2C2468 45%,#352A74 70%,#1F1A4A 100%);
  -webkit-print-color-adjust:exact;print-color-adjust:exact}}
b{{font-weight:700}}
.page{{position:relative;width:594mm;height:420mm;overflow:hidden;display:flex;flex-direction:column;gap:1.9mm;padding:3mm 10mm 3mm}}
.page > *{{flex-shrink:0;position:relative;z-index:1}}
.bg{{position:absolute !important;inset:0;z-index:0 !important}}
.ic{{width:9mm;height:9mm;flex:none;overflow:visible}}
.src{{font-size:14pt;color:#8A8299;font-weight:500;white-space:nowrap}}
.lbl{{font-family:'Poppins';font-weight:700;font-size:14pt;letter-spacing:.18em;text-transform:uppercase;line-height:1}}
.glass{{background:rgba(44,36,104,.94);border:.4mm solid rgba(255,255,255,.2);border-radius:6mm;color:#F4EEFF}}

/* names */
.names{{display:flex;align-items:center;justify-content:space-between;padding:1.1mm 3mm 1.1mm 1.4mm;border-radius:20mm}}
.names .who{{font-family:'Poppins';font-weight:700;color:#1F1A4A;background:linear-gradient(180deg,#FFE49C,#E9A222);font-size:19pt;padding:.6mm 4.4mm .8mm;border-radius:20mm;white-space:nowrap}}
.names .m{{display:flex;gap:1.8mm;align-items:baseline;font-size:21pt;padding-left:4mm;border-left:.4mm solid rgba(255,255,255,.2)}}
.names .m b{{font-weight:700;color:#fff}} .names .m i{{font-style:normal;color:#FFD877;font-weight:600;font-stretch:condensed}}

/* header */
header{{display:grid;grid-template-columns:112mm 1fr 112mm;align-items:center;height:47mm}}
.hc{{display:flex;flex-direction:column;align-items:center}}
.script{{font-family:'Playfair Display';font-style:italic;font-weight:500;font-size:25pt;color:#F6C766;display:flex;align-items:center;gap:4mm;white-space:nowrap;line-height:1}}
.script::before,.script::after{{content:"";width:16mm;height:.5mm;background:linear-gradient(90deg,transparent,#F6C766)}}
.script::after{{transform:scaleX(-1)}}
.hook{{font-size:24pt;color:#E9E2FF;margin-top:.4mm;white-space:nowrap;line-height:1.05}}
.hook b{{color:#FFD877}}

/* intro pills */
.intro{{display:grid;grid-template-columns:1fr 1fr;column-gap:6mm}}
.pill{{display:grid;grid-template-columns:66mm 1fr;align-items:center;padding:2.4mm 5mm;border-radius:9mm}}
.pill h2{{font-family:'Poppins';font-weight:700;font-size:21pt;line-height:1.1;color:#FFD877;padding-right:4mm;border-right:.4mm solid rgba(255,255,255,.2);margin-right:4.4mm}}
.pill p{{color:#F1ECFF;line-height:1.1}}
.pill p b{{color:#fff}}

/* cards */
.cards{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));column-gap:6mm;margin-top:2.4mm}}
.badge{{position:absolute;left:50%;top:-4.6mm;transform:translateX(-50%);z-index:3;font-family:'Poppins';font-weight:700;font-size:15pt;letter-spacing:.3em;color:#3A2A10;
  background:linear-gradient(180deg,#FFE7A0,#EFAE36);padding:1.4mm 7mm 1.6mm 8mm;border-radius:20mm;box-shadow:0 .8mm 0 #B7801A;white-space:nowrap}}
.card{{background:{CREAM};border-radius:5.4mm;padding:2.6mm 3.4mm 2mm;display:flex;flex-direction:column;border-bottom:2.2mm solid var(--c);box-shadow:0 1.6mm 0 rgba(0,0,0,.25)}}
.card .ttl{{display:flex;align-items:center;gap:2.6mm;margin:2mm 1mm .4mm;white-space:nowrap}}
.card .ttl i{{width:5mm;height:5mm;border-radius:50%;background:var(--c);box-shadow:0 0 0 1.2mm var(--cs);flex:none}}
.card .ttl b{{font-family:'Poppins';font-weight:700;font-size:24pt;color:#1F1A3A;line-height:1}}
.card .ttl span{{margin-left:auto;font-size:16pt;font-weight:700;color:var(--cd)}}
.card .lbl{{color:var(--cd);margin:1.6mm 1mm .7mm}}
.card p,.card ul{{margin:0 1mm}}
.card ul{{list-style:none;white-space:nowrap}}
.card li{{padding-left:5.2mm;position:relative;line-height:1.08}}
.card li::before{{content:"";position:absolute;left:.3mm;top:2.4mm;width:3mm;height:3mm;border-radius:50%;background:radial-gradient(circle at 35% 30%,#fff 0,var(--c) 60%)}}
.card .flow{{margin:1.2mm auto 0}}

/* bottom */
.bottom{{display:grid;grid-template-columns:1fr 190mm;column-gap:6mm}}
.cmp{{padding:2mm 3mm 2mm;border-radius:5mm}}
.tg{{display:grid;grid-template-columns:86mm repeat(3,minmax(0,1fr))}}
.tg > div{{padding:.45mm 2.6mm;display:flex;align-items:center;white-space:nowrap;font-stretch:condensed;color:#F4EEFF;border-top:.3mm solid rgba(255,255,255,.14)}}
.tg .h{{border-top:none;font-family:'Poppins';font-weight:700;font-size:18pt;gap:2mm;padding-bottom:1.2mm}}
.tg .h i{{width:4.6mm;height:4.6mm;border-radius:50%;flex:none}}
.tg .cap{{font-family:'Poppins';font-weight:800;font-size:23pt;color:#FFD877;line-height:1}}
.tg .lab{{gap:2mm;font-family:'Poppins';font-weight:600;font-size:18.5pt;line-height:1.02;font-stretch:normal;color:#FFFFFF;white-space:normal}}
.tg .lab .ic{{width:8.2mm;height:8.2mm;background:#FFF8EE;border-radius:50%;padding:.5mm}}
.tg .sec{{grid-column:1 / -1;border-top:.4mm solid rgba(255,216,119,.5)}}
.tg .sec span{{font-family:'Poppins';font-weight:700;font-size:13.5pt;letter-spacing:.22em;color:#FFD877}}
.tg b{{font-weight:700}}
.k1 b{{color:#FFD877}} .k2 b{{color:#7FE3C9}} .k3 b{{color:#FFA996}}
.tg ul{{list-style:none}}
.tg li{{display:flex;gap:1.4mm;align-items:center;line-height:1.06}}
.tg li::before{{content:"";width:3.6mm;height:3.6mm;border-radius:50%;flex:none}}
.adv li::before{{background:radial-gradient(circle at 35% 30%,#B6F5D2,#23A86A)}} .dis li::before{{background:radial-gradient(circle at 35% 30%,#FFC1B6,#E0503A)}}

.oman{{background:{CREAM};border-radius:5.4mm;border-bottom:2.2mm solid {TEAL};box-shadow:0 1.6mm 0 rgba(0,0,0,.25);padding:2.4mm 4mm 2mm;display:flex;flex-direction:column;gap:.5mm}}
.oman .top{{display:grid;grid-template-columns:64mm 1fr;column-gap:3.4mm;align-items:center;margin-bottom:.6mm}}
.oman h2{{font-family:'Poppins';font-weight:800;font-size:24pt;line-height:1.02;color:#1F1A3A}}
.oman h2 em{{font-style:normal;color:{TEALD}}}
.oman .lbl{{margin-top:1mm}}
.oman .it{{display:flex;gap:2mm;align-items:center;line-height:1.04;white-space:nowrap}}
.oman .it .ic{{width:7.4mm;height:7.4mm}}

/* footer */
.foot{{margin-top:auto}}
.concl{{margin-top:auto;background:linear-gradient(180deg,#FFE7A0,#EFAE36);border-radius:4mm;padding:1.2mm 3.4mm 1.4mm;font-size:21pt;line-height:1.08;color:#2A1E05}}
.concl b{{font-family:'Poppins';font-weight:800;font-size:17pt;display:block;letter-spacing:.12em;text-transform:uppercase}}
.concl p{{font-size:21pt;line-height:1.1}}
.concl p b{{font-family:'Poppins';color:#FFD877;font-weight:700}}
.refs{{display:grid;grid-template-columns:34mm 1fr;column-gap:3mm;padding:1.6mm 3.4mm;border-radius:5mm}}
.refs h3{{font-family:'Poppins';font-weight:700;font-size:17pt;color:#FFD877;line-height:1.1}}
.refs h3 small{{display:block;font-family:'Bricolage Grotesque';font-weight:600;font-size:10pt;color:#B8B0D0}}
.refs ul{{columns:4;column-gap:4mm;list-style:none;font-size:9.6pt;line-height:1.13;color:#E9E3FA}}
.refs li{{break-inside:avoid;padding-left:3.4mm;text-indent:-3.4mm;margin-bottom:.35mm}}
</style></head>
<body><div class="page">
<svg width="0" height="0" style="position:absolute"><defs>{GRAD}{DEFS}{GLOSS}</defs></svg>
<svg class="bg" viewBox="0 0 594 420" width="594mm" height="420mm">
  {''.join(use('spark', x, y, sc) for x, y, sc in [(5,40,1.1),(4,120,.8),(6,300,1),(5,390,.7),(589,60,1),(590,170,.8),(588,300,1.1),(589,405,.7),(300,99.5,.6),(150,396,.6),(450,396,.6)])}
  <circle cx="-6" cy="236" r="15" fill="url(#gOrbC)" opacity=".75"/><circle cx="600" cy="214" r="16" fill="url(#gOrbV)" opacity=".8"/>
  <circle cx="590" cy="350" r="5" fill="url(#gOrbT)" opacity=".8"/>
</svg>

<div class="glass names">
  <span class="who">Student Names</span>
  <span class="m"><b>Mais altoubi</b><i>31j2573</i></span>
  <span class="m"><b>Alshima Almahrooqi</b><i>21S252540139</i></span>
  <span class="m"><b>Nardeen alfarsi</b><i>21J2583</i></span>
  <span class="m"><b>shatha al_umeiri</b><i>21J25157</i></span>
</div>

<header>
  {svg(LEFT, 118, 46, style='width:106mm;height:41.4mm')}
  <div class="hc">
    <div class="script">Chapter 2: Economic Systems &middot; BSEC1103 Principles of Economics</div>
    {svg(TITLE, 238, 36, style='width:190mm;height:28.7mm')}
    <div class="hook">Scarce resources force every society to choose: who decides <b>what, how &amp; for whom</b>?</div>
  </div>
  {svg(RIGHT, 118, 46, style='width:106mm;height:41.4mm;justify-self:end')}
</header>

<section class="intro">
  <div class="glass pill"><h2>What is an economic system?</h2><p>The <b>means by which a society or government organises and distributes</b> its resources, goods and services: its <b>mode of production and distribution</b>. <span class="src">(Fernando, 2026)</span></p></div>
  <div class="glass pill"><h2>Why does every society need one?</h2><p>Resources are <b>scarce</b> but wants are <b>unlimited</b>, so a society needs a system to answer the <b>three central questions</b>: what, how and for whom to produce. <span class="src">(Mankiw, 2021)</span></p></div>
</section>

<section class="cards">
  <div class="badge">THREE ECONOMIC SYSTEMS</div>
  <div class="card" style="--c:{GOLD};--cd:{GOLDD};--cs:{GOLDS}">
    <svg viewBox="0 3 176 31" style="display:block;width:100%;height:auto;border-radius:3.6mm;overflow:hidden">{CAP_ART}</svg>
    <div class="ttl"><i></i><b>Capitalist Economy</b><span>market &middot; free</span></div>
    <div class="lbl">Core functioning</div>
    <p>Resources <b>privately owned</b> by citizens &amp; institutions; <b>no government interference</b>.</p>
    <ul style="margin-top:.6mm"><li>Freedom to start any business</li><li>Consumers buy by income; firms offer variety</li><li>Guided by <b>profit</b> and <b>competition</b></li></ul>
    <div class="lbl">Flowchart</div>
    {svg(F_CAP, 170, 30, 'flow')}
  </div>
  <div class="card" style="--c:{CORAL};--cd:{CORALD};--cs:{CORALS}">
    <svg viewBox="0 3 176 31" style="display:block;width:100%;height:auto;border-radius:3.6mm;overflow:hidden">{COM_ART}</svg>
    <div class="ttl"><i></i><b>Socialist Economy</b><span>command</span></div>
    <div class="lbl">Core functioning</div>
    <p><b>Government owns &amp; controls</b> production; a <b>central authority</b> decides all.</p>
    <ul style="margin-top:.6mm"><li>State owns banks, industry, transport</li><li>Prices <b>fixed</b>; quality goods, reasonable prices</li><li>Aim: <b>social welfare</b> &amp; equal jobs for all</li></ul>
    <div class="lbl">Flowchart</div>
    {svg(F_COM, 170, 30, 'flow')}
  </div>
  <div class="card" style="--c:{TEAL};--cd:{TEALD};--cs:{TEALS}">
    <svg viewBox="0 3 176 31" style="display:block;width:100%;height:auto;border-radius:3.6mm;overflow:hidden">{MIX_ART}</svg>
    <div class="ttl"><i></i><b>Mixed Economy</b><span>public + private</span></div>
    <div class="lbl">Core functioning</div>
    <p><b>Private + government control</b>: both decide what is made &amp; how it is shared.</p>
    <ul style="margin-top:.6mm"><li><b>Public &amp; private</b> sectors co-exist</li><li><b>Planning</b> controls the economy</li><li>Profit + social interest; consumer &amp; labour rights</li></ul>
    <div class="lbl">Flowchart</div>
    {svg(F_MIX, 170, 30, 'flow')}
  </div>
</section>

<section class="bottom">
  <div class="glass cmp">
    <div class="tg">
      <div class="h"><span class="cap">Comparison</span></div>
      <div class="h"><i style="background:{GOLD}"></i>Capitalist</div><div class="h"><i style="background:{TEAL}"></i>Mixed</div><div class="h"><i style="background:{CORAL}"></i>Socialist (command)</div>
      <div class="sec"><span>THE 3 CENTRAL QUESTIONS</span><span class="src" style="margin-left:auto;color:#B8B0D0;letter-spacing:0;font-family:Bricolage Grotesque;font-weight:500">(Fernando, 2026)</span></div>
      <div class="lab">{ic('i-what')}What to produce?</div><div class="k1">Whatever consumers demand</div><div class="k2">Demand + national plans</div><div class="k3">Central authority&rsquo;s plan</div>
      <div class="lab">{ic('i-how')}How to produce?</div><div class="k1">Producers choose, for profit</div><div class="k2">Private firms + public sector</div><div class="k3">State organises production</div>
      <div class="lab">{ic('i-whom')}For whom?</div><div class="k1">Buyers, by their income</div><div class="k2">Market + social welfare</div><div class="k3">State allocates to citizens</div>
      <div class="sec"><span>COMPARISON TABLE</span></div>
      <div class="lab">{ic('i-key')}Ownership of resources</div><div class="k1"><span><b>Private</b> individuals</span></div><div class="k2"><span><b>Public + private</b></span></div><div class="k3"><span><b>Government</b></span></div>
      <div class="lab">{ic('i-gov')}Role of government</div><div class="k1"><span><b>Little</b>: no interference</span></div><div class="k2"><span><b>Plans</b> &amp; controls</span></div><div class="k3"><span><b>Total</b>: decides all</span></div>
      <div class="lab">{ic('i-tag')}Price mechanism</div><div class="k1"><span><b>Free</b> market prices</span></div><div class="k2"><span><b>Prices</b> + planning</span></div><div class="k3"><span><b>Fixed</b> by the authority</span></div>
      <div class="lab">{ic('i-motive')}Motive</div><div class="k1"><span><b>Profit</b></span></div><div class="k2"><span><b>Profit + social interest</b></span></div><div class="k3"><span><b>Social welfare</b></span></div>
      <div class="lab">{ic('i-up')}Advantages</div>
      <div class="k1"><ul class="adv"><li>Equal opportunities</li><li>Innovation &amp; fast growth</li></ul></div>
      <div class="k2"><ul class="adv"><li>Best allocation of resources</li><li>Via prices, profit &amp; liberty</li></ul></div>
      <div class="k3"><ul class="adv"><li>Efficient use; stability</li><li>Max welfare; no monopoly</li></ul></div>
      <div class="lab">{ic('i-down')}Disadvantages</div>
      <div class="k1"><ul class="dis"><li>Rich richer, poor poorer</li><li>No welfare &rarr; poverty</li></ul></div>
      <div class="k2"><ul class="dis"><li>Sectors may not cooperate</li><li>Inefficient public sector</li></ul></div>
      <div class="k3"><ul class="dis"><li>Bureaucracy; no freedom</li><li>No tech or competition</li></ul></div>
    </div>
  </div>

  <div class="oman">
    <div class="top">{svg(OMAN_ART, 64, 30)}<h2>Oman: a <em>mixed economy</em></h2></div>
    <div class="lbl" style="color:{CORALD}">Government sector</div>
    <div class="it">{ic('i-compass')}<span>Plans the economy: <b>Oman Vision 2040</b></span></div>
    <div class="it">{ic('i-key')}<span>Owns state firms: <b>Oman Investment Authority</b></span></div>
    <div class="it">{ic('i-shield')}<span>Protects consumers &amp; workers by law</span></div>
    <div class="lbl" style="color:{GOLDD}">Private sector</div>
    <div class="it">{ic('i-branch')}<span>Leads diversification beyond oil</span></div>
    <div class="it">{ic('i-bridge')}<span>Partners the state in <b>PPP</b> projects</span></div>
    <div class="it">{ic('i-how')}<span>Takes over state firms via <b>privatisation</b></span></div>
    <span class="src" style="font-size:12pt;white-space:normal;margin-top:.2mm">(Oman Vision 2040 Main Committee, 2019; Royal Decrees 66/2014, 51/2019, 52/2019, 61/2020, 53/2023)</span>
    <div class="concl"><b>Conclusion</b>The mixed economy blends market freedom with social welfare: the model Oman follows.</div>
  </div>
</section>

<section class="foot">
  <div class="glass refs">
    <h3>References<small>APA 7th ed.</small></h3>
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
</section>
</div>
<script>document.fonts.ready.then(()=>{{document.body.dataset.ready='1'}});</script>
</body></html>'''
(HERE / 'poster.html').write_text(HTML)
print('ok')
