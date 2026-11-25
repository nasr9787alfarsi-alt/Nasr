#!/usr/bin/env python3
"""WHO PULLS THE STRINGS? - A2 landscape poster (594 x 420 mm), Chapter 2 Economic Systems."""
import pathlib
HERE = pathlib.Path(__file__).parent
exec((HERE / 'lib' / 'islands_symbols.py').read_text().split('# ------------------------------------------------------------------ ISLANDS SCENE')[0])

AM, AMD, AMS = '#E0802A', '#A85A14', '#FCEBD6'      # capitalist: amber
TL, TLD, TLS = '#24877D', '#17625A', '#DBEFEC'      # mixed: teal
NV, NVD, NVS = '#2D4A8C', '#1F356A', '#DFE6F4'      # command: navy
GOLD, VEL, VELD = '#E8B84B', '#8A1E33', '#5E1222'   # theatre gold, velvet
NIGHT = '#241A2B'; CREAM = '#FBF3E4'; WOOD = '#B7814F'

EXTRA = f'''
<g id="hand">
  <rect x="-5.6" y="-46" width="11.2" height="28" style="fill:var(--sleeve,{NV});stroke-dasharray:var(--dash,none)" {SW}/>
  <rect x="-7.2" y="-20.6" width="14.4" height="4.6" rx="1.4" style="fill:var(--cuff,#fff);stroke-dasharray:var(--dash,none)" {SW}/>
  <path d="M-7 -16.4 H7 V-5.6 Q7 -1.6 3 -1.6 H-3 Q-7 -1.6 -7 -5.6Z" style="fill:var(--skin,#E8B48C);stroke-dasharray:var(--dash,none)" {SW}/>
  <ellipse cx="-7.4" cy="-8.4" rx="2" ry="3.8" transform="rotate(-18 -7.4 -8.4)" style="fill:var(--skin,#E8B48C);stroke-dasharray:var(--dash,none)" {SW}/>
  {''.join(f'<rect x="{x}" y="-3.6" width="3.3" height="6" rx="1.5" style="fill:var(--skin,#E8B48C);stroke-dasharray:var(--dash,none)" {SW}/>' for x in (-6.8, -3.4, 0, 3.4))}
</g>
<g id="dallah">
  <path d="M-4.4 -7 Q-11 -9 -7.6 -17" fill="none" stroke="{INK}" stroke-width="1.1" stroke-linecap="round"/>
  <path d="M4.2 -8.6 Q10.6 -11 11.6 -21.4 Q10.2 -20.6 9.6 -14.6 Q8.2 -10 4 -6.8Z" fill="#E0AE4A" {SW}/>
  <path d="M-6.6 0 Q-9.6 -6.2 -4.8 -10.4 L-2.8 -16.6 Q-4 -18.4 -2 -19.2 H2 Q4 -18.4 2.8 -16.6 L4.8 -10.4 Q9.6 -6.2 6.6 0Z" fill="#E0AE4A" {SW}/>
  <path d="M-2.6 -19.2 Q0 -24.4 2.6 -19.2Z" fill="#E0AE4A" {SW}/><circle cx="0" cy="-24.6" r=".9" fill="#E0AE4A" {SW}/>
  <rect x="-7.2" y="-.6" width="14.4" height="1.6" rx=".6" fill="#C9963A" {SW}/>
</g>
<g id="scroll"><rect x="-6" y="-4" width="12" height="8" fill="#FFF8EC" {SW}/><circle cx="-6" cy="0" r="4" fill="#E9D9BF" {SW}/><circle cx="6" cy="0" r="4" fill="#E9D9BF" {SW}/><path d="M-3 -1.6 H3 M-3 .4 H3 M-3 2.2 H1.6" stroke="{INK}" stroke-width=".35"/></g>
'''

def T(x, y, txt, size=5, w=700, col=INK, anchor='middle', extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" text-anchor="{anchor}" fill="{col}"{extra}>{txt}</text>'

def tagpill(x, y, txt, size=4.4, col=INK, fill='#fff', icon=None):
    w = len(txt)*size*.5 + 4.6 + (6 if icon else 0); h = size*1.55
    x0 = x - w/2
    ic = use(icon, x0+3.8, y, .5) if icon else ''
    return (f'<rect x="{x0:.1f}" y="{y-h/2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h/2:.1f}" fill="{fill}" {SW}/>' + ic +
            T(f'{x + (2.9 if icon else 0):.1f}', f'{y+size*.36:.2f}', txt, size, 700, col))

def string(x1, y1, x2, y2):
    return f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{INK}" stroke-width=".28" opacity=".85"/>'

def bar(x1, x2, y):
    return f'<rect x="{x1}" y="{y-1.5}" width="{x2-x1}" height="3" rx="1.5" fill="{WOOD}" {SW}/>'

def stage_base(tint, W=140, H=66):
    o = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="{tint}"/>',
         f'<path d="M{W/2-26} 0 L{W/2+26} 0 L{W/2+58} {H-10} L{W/2-58} {H-10}Z" fill="#FFFFFF" opacity=".38"/>',
         f'<rect x="0" y="{H-10}" width="{W}" height="10" fill="{WOOD}"/>']
    o += [f'<path d="M{x} {H-10} L{x-3} {H}" stroke="#94643A" stroke-width=".4"/>' for x in range(8, W, 14)]
    o.append(f'<path d="M0 {H-10} H{W}" stroke="{INK}" stroke-width=".6"/>')
    o += [f'<path d="M{x-2.4} {H} A2.4 2.4 0 0 1 {x+2.4} {H}Z" fill="{GOLD}" {SW}/>' for x in range(10, W, 20)]
    return ''.join(o)

GHOST = '--sleeve:rgba(255,255,255,.55);--cuff:rgba(255,255,255,.55);--skin:rgba(255,255,255,.55);--dash:1.3 .9'
GOVH = f'--sleeve:{NV};--skin:#E8B48C'
FL = 56  # stage floor line

# ---------------- CAPITALIST stage
c = [stage_base(AMS), use('hand', 70, 12, .95, GHOST), bar(14, 126, 12)]
c.append(tagpill(104, 4.6, 'invisible hand: PRICES', 4.0, AMD))
# shops on strings (competition)
for x, awn, name in [(25, AM, 'SHOP A'), (51, TL, 'SHOP B')]:
    top = FL - 21.6*.82
    c.append(string(x-7, 12, x-7, top+4)); c.append(string(x+7, 12, x+7, top+4))
    c.append(use('shop', x, FL, .82, f'--awn:{awn}'))
    c.append(T(x, FL-21.6*.82+2.6, name, 2.5, 800, '#fff'))
c.append(use('tag', 30.6, 26, .9)); c.append(use('tag', 56.6, 30, .9))
c.append(tagpill(38, 21, 'competition', 4.0, AMD))
# consumer puppet (freedom of choice)
c.append(string(80, 12, 84, FL-13.6)); c.append(string(76, 12, 80.7, FL-6.2)); c.append(string(92, 12, 87.3, FL-6.2))
c.append(use('person', 84, FL, 1.0, f'--shirt:{NV};--skin:{C["skin3"]}')); c.append(use('bag', 84, FL, 1.0))
c.append(tagpill(84, 30, 'free choice', 4.0, AMD))
# private property
c.append(string(108, 12, 108, FL-17*.85)); c.append(use('house', 108, FL, .85, f'--roof:{AM}'))
c.append(use('i-key', 117.5, FL-12, .62))
c.append(tagpill(110, 24, 'private property', 4.0, AMD))
# government off-strings
c.append(use('gov', 131, FL, .32)); c.append(f'<circle cx="131" cy="{FL-3.4}" r="5.4" fill="none" stroke="{NV}" stroke-width=".45" stroke-dasharray="1.1 .8"/>')
c.append(T(130, FL-11, 'little gov&#8217;t', 3.4, 800, NVD))
CAP = ''.join(c)

# ---------------- COMMAND stage
m = [stage_base(NVS), use('hand', 70, 12, 1.15, GOVH), bar(8, 132, 12)]
m.append(tagpill(34, 4.6, 'one hand: CENTRAL PLAN', 4.0, NVD))
m.append(string(18, 12, 18, FL-12.5*.9)); m.append(string(30, 12, 30, FL-12.5*.9))
m.append(use('factory', 24, FL, .9, f'--fac:#8FA3C7'))
m.append(tagpill(24, 33, 'state-owned', 4.0, NVD))
# fixed price tag hanging
m.append(string(50, 12, 50, 26.6))
m.append(f'<g transform="translate(41.6 26.6) scale(2.3)"><use href="#tag"/></g>')
m.append(T(48.4, 33.4, 'FIXED', 3.0, 800, INK))
m.append(T(51, 42, 'reasonable', 3.3, 700, NVD) + T(51, 45.8, 'prices', 3.3, 700, NVD))
# identical worker puppets: equal jobs for all
for i, x in enumerate([74, 86, 98, 110, 122]):
    m.append(string(x, 12, x, FL-15.2*.88))
    m.append(use('person', x, FL, .88, f'--shirt:#8FA3C7;--skin:{C["skin1"] if i % 2 else C["skin2"]}'))
    m.append(use('hardhat', x, FL, .88))
m.append(tagpill(98, 28, 'jobs for all', 4.0, NVD))
COM = ''.join(m)

# ---------------- MIXED stage
x_ = [stage_base(TLS), use('hand', 35, 12, .9, GOVH), bar(6, 64, 12), use('hand', 105, 12, .9, GHOST), bar(76, 134, 12)]
x_.append(tagpill(35, 4.4, 'gov&#8217;t: planning', 3.8, NVD))
x_.append(tagpill(105, 4.4, 'market: prices', 3.8, AMD))
x_.append(string(14, 12, 14, FL-18.5*.85)); x_.append(string(28, 12, 28, FL-18.5*.85))
x_.append(use('gov', 21, FL, .85, f'--groof:{NV}'))
x_.append(T(21, FL-20, 'PUBLIC', 3.2, 800, NVD))
x_.append(string(46, 12, 46, 29)); x_.append(f'<circle cx="46" cy="34.6" r="5.4" fill="#fff" {SW}/>' + use('i-shield', 46, 34.6, .78))
x_.append(string(58, 12, 58, 37)); x_.append(f'<circle cx="58" cy="42.6" r="5.4" fill="#fff" {SW}/>' + use('i-hat', 58, 42.6, .78))
x_.append(T(46, 25, 'consumer', 3.2, 800, TLD) + T(60, 53, 'labour', 3.2, 800, TLD))
x_.append(T(45.5, 28.2, 'rights', 3.2, 800, TLD) if False else '')
x_.append(string(84, 12, 84, FL-21.6*.82+4)); x_.append(string(98, 12, 98, FL-21.6*.82+4))
x_.append(use('shop', 91, FL, .82, f'--awn:{AM}')); x_.append(T(91, FL-21.6*.82+2.6, 'PRIVATE', 2.4, 800, '#fff'))
x_.append(string(118, 12, 122, FL-13.6)); x_.append(use('person', 122, FL, .95, f'--shirt:{AM};--skin:{C["skin2"]}')); x_.append(use('bag', 122, FL, .95))
x_.append(f'<path d="M67 44 Q72 40 77 44" fill="none" stroke="{TLD}" stroke-width=".9"/>' + T(72, 50.6, 'co-exist', 3.6, 800, TLD))
MIX = ''.join(x_)

# ---------------- flowcharts (130 x 30)
def node(x, y, ic, lab, col):
    lines = lab.split('|')
    t = ''.join(T(x, y+11.2+i*4.9, ln, 4.7, 700, INK) for i, ln in enumerate(lines))
    return f'<circle cx="{x}" cy="{y}" r="6.6" fill="#fff" stroke="{col}" stroke-width=".9"/>' + use(ic, x, y, .9) + t
def arr(x1, x2, y, col, lab=''):
    t = T((x1+x2)/2, y-2.2, lab, 3.9, 700, col) if lab else ''
    return f'<path d="M{x1} {y} H{x2-1.8}" stroke="{col}" stroke-width=".9"/><path d="M{x2-2.8} {y-1.8} L{x2} {y} L{x2-2.8} {y+1.8}Z" fill="{col}"/>' + t
F_CAP = (node(16, 9, 'i-whom', 'Consumers', AM) + arr(24, 56, 9, AMD, 'demand') + node(65, 9, 'i-tag', 'Market price', AM) +
         arr(73, 105, 9, AMD, 'profit signal') + node(114, 9, 'i-how', 'Producers', AM) +
         f'<path d="M114 25.6 V28.6 H16 V25.6" fill="none" stroke="{AMD}" stroke-width=".7" stroke-dasharray="1.4 .9"/>' +
         f'<rect x="42" y="26.2" width="46" height="4.8" fill="#FFFBF3"/>' + T(65, 29.6, 'goods for buyers who can pay', 3.7, 700, AMD))
F_COM = (node(16, 9, 'i-plan', 'Central|authority', NV) + arr(24, 56, 9, NVD, 'plans &amp; fixes prices') + node(65, 9, 'i-how', 'State-owned|firms', NV) +
         arr(73, 105, 9, NVD, 'allocates') + node(114, 9, 'i-whom', 'Citizens', NV))
F_MIX = (node(16, 9, 'i-gov', 'Public|sector', TL) + T(40.5, 12, '+', 8, 800, TLD) + node(65, 9, 'i-tag', 'Private|sector', TL) +
         arr(73, 105, 9, TLD, 'plan + prices') + node(114, 9, 'i-what', 'Goods &amp;|services', TL))

FLBL = T(0, 0, 'FLOWCHART', 3.7, 400, '{c}', anchor='start', extra=' font-family="Limelight" letter-spacing=".2" transform="translate(3.4 30.4) rotate(-90)"')
def svg(inner, w, h, cls='', style='', vb=None):
    vb = vb or f'0 0 {w} {h}'
    return f'<svg class="{cls}" viewBox="{vb}" width="{w}mm" height="{h}mm" style="display:block;{style}">{inner}</svg>'
def ic(i, s=1.0):
    return f'<svg class="ic" viewBox="-6 -6 12 12"><use href="#{i}" transform="scale({s})"/></svg>'

# ---------------- marquee frame with bulbs (574 x 50)
MW, MH = 574, 46
bulbs = []
for i in range(int(MW/6.2)+1):
    x = 3 + i*(MW-6)/int(MW/6.2)
    for y in (2.6, MH-2.6):
        bulbs.append(f'<circle cx="{x:.1f}" cy="{y}" r="1.25" fill="#FFE7A3" stroke="#B9862C" stroke-width=".3"/>')
for j in range(1, int(MH/6.2)):
    y = 2.6 + j*(MH-5.2)/int(MH/6.2)
    for x in (2.6, MW-2.6):
        bulbs.append(f'<circle cx="{x}" cy="{y:.1f}" r="1.25" fill="#FFE7A3" stroke="#B9862C" stroke-width=".3"/>')
MARQ = (f'<rect x="0" y="0" width="{MW}" height="{MH}" rx="4" fill="{VELD}" stroke="{GOLD}" stroke-width="1.2"/>'
        f'<rect x="5.4" y="5.4" width="{MW-10.8}" height="{MH-10.8}" rx="2.4" fill="#1B1320" stroke="{GOLD}" stroke-width=".5"/>' + ''.join(bulbs) +
        # strings from a control bar to the title
        f'<rect x="52" y="6.8" width="150" height="2.2" rx="1.1" fill="{WOOD}" {SW}/>' +
        ''.join(f'<path d="M{x} 9 L{x} 15.6" stroke="#E9DFC9" stroke-width=".3"/>' for x in (60, 100, 150, 194)))

OMAN_ART = (f'<rect x="0" y="0" width="172" height="40" rx="2.4" fill="#F6DDB0"/>'
            f'<circle cx="150" cy="10" r="6" fill="#F4A94A" opacity=".85"/>'
            f'<path d="M0 30 H172 V37.6 Q172 40 169.6 40 H2.4 Q0 40 0 37.6Z" fill="#3C93A0"/>' + waves(32.4, 2, 170, step=7, amp=.7, op=.5) +
            f'<path d="M4 30 Q24 23 52 24 Q70 25 84 30Z" fill="#EFD9AE" {SW}/>' +
            use('fort', 34, 28, .72) + use('palm', 12, 29, .6) + use('palm', 74, 30, .5) + use('dallah', 98, 30, .5) +
            use('dhow', 136, 37, .62) + use('shop', 118, 30, .5, f'--awn:{AM}') +
            use('hand', 34, 5.4, .42, GOVH) + bar(20, 48, 5.4) + string(30, 5.4, 30, 9.6) +
            use('hand', 128, 5.4, .42, GHOST) + bar(114, 142, 5.4) + string(118, 5.4, 118, 19.4) + string(136, 5.4, 136, 15))

HTML = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Who Pulls the Strings?</title>
<link rel="stylesheet" href="fonts/fonts.css">
<style>
@page {{ size: 594mm 420mm; margin: 0; }}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:594mm;height:420mm}}
body{{font-family:'Bricolage Grotesque',sans-serif;font-stretch:semi-condensed;color:{INK};font-size:24pt;line-height:1.12;background:{NIGHT};
  -webkit-print-color-adjust:exact;print-color-adjust:exact}}
svg text{{font-family:'Bricolage Grotesque';font-stretch:semi-condensed}}
b{{font-weight:700}}
.page{{position:relative;width:594mm;height:420mm;overflow:hidden;display:flex;flex-direction:column;gap:2.6mm;padding:0 10mm 3.4mm}}
.page > *{{flex-shrink:0;position:relative;z-index:1}}
.curtains{{position:absolute !important;inset:0;z-index:0 !important;pointer-events:none}}
.ic{{width:9mm;height:9mm;flex:none;overflow:visible}}
.src{{font-size:15pt;color:#6a6474;font-weight:500;white-space:nowrap}}
.lime{{font-family:'Limelight';font-weight:400}}
.act{{font-family:'Limelight';font-size:17pt;color:{GOLD};letter-spacing:.06em;line-height:1}}
.card{{background:{CREAM};border:.6mm solid {INK};border-radius:3.6mm;box-shadow:0 0 0 1mm {GOLD}, 1.6mm 1.6mm 0 1mm #120C16}}

/* student names band */
.band{{margin:0 -10mm;background:#120C16;color:{CREAM};display:flex;align-items:center;justify-content:space-between;padding:1.5mm 12mm 1.7mm;border-bottom:.6mm solid {GOLD}}}
.band .who{{font-family:'Limelight';color:{GOLD};font-size:20pt;padding:.4mm 3.4mm .8mm;border:.45mm solid {GOLD};border-radius:8mm;line-height:1.1;white-space:nowrap}}
.band .m{{display:flex;gap:1.8mm;align-items:baseline;font-size:22pt;padding-left:4mm;border-left:.5mm solid rgba(232,184,75,.45)}}
.band .m b{{font-weight:700}}
.band .m i{{font-style:normal;font-stretch:condensed;color:#F3D58C;font-weight:600}}

/* marquee */
.marquee{{height:46mm}}
.marquee > svg{{position:absolute;inset:0}}
.mq{{position:absolute;inset:0;display:grid;grid-template-columns:262mm 1fr;align-items:center;padding:0 12mm 0 14mm}}
.title{{font-family:'Limelight';font-size:47pt;line-height:1;color:{GOLD};text-shadow:.9mm .9mm 0 {VEL};white-space:nowrap;margin-top:3mm}}
.mq .right{{color:{CREAM}}}
.summary{{font-size:24pt;line-height:1.12}}
.summary b{{color:{GOLD};font-weight:700}}
.chips{{display:flex;gap:3mm;margin-top:2.2mm}}
.chip{{font-size:21pt;font-weight:700;padding:.6mm 4mm 1mm;border-radius:10mm;border:.5mm solid {GOLD};color:{GOLD};line-height:1.1;white-space:nowrap}}
.chip.solid{{background:{GOLD};color:#1B1320}}

/* middle */
.middle{{display:grid;grid-template-columns:134mm repeat(3,1fr);column-gap:6mm}}
.script{{padding:2.6mm 4.4mm 3mm;display:flex;flex-direction:column;gap:1.6mm}}
.script h2{{font-weight:800;font-size:25pt;line-height:1.02}}
.qrow{{display:flex;gap:1.8mm;margin-top:.6mm}}
.q{{flex:1;display:flex;gap:1.2mm;justify-content:center;align-items:center;white-space:nowrap;background:#fff;border:.45mm solid {INK};border-radius:3mm;padding:1mm .6mm;font-weight:800;font-size:20pt}}
.q .ic{{width:7.6mm;height:7.6mm}}
.stage{{overflow:hidden;display:flex;flex-direction:column}}
.stage .sign{{display:flex;justify-content:space-between;align-items:baseline;padding:1.8mm 4mm 1.8mm;background:var(--s);color:#fff;border-bottom:.6mm solid {INK};white-space:nowrap}}
.stage .sign b{{font-family:'Limelight';font-weight:400;font-size:21pt;line-height:1}}
.stage .sign span{{font-size:17pt;font-weight:700}}
.stage .art{{border-bottom:.6mm solid {INK}}}
.stage ul{{list-style:none;padding:1.8mm 4mm 0;white-space:nowrap}}
.stage li{{padding-left:5.4mm;position:relative;line-height:1.08;margin-bottom:.15mm}}
.stage li::before{{content:"";position:absolute;left:.4mm;top:2.5mm;width:2.8mm;height:2.8mm;transform:rotate(45deg);background:var(--s);border:.3mm solid {INK}}}
.stage .flowlbl{{margin:1.2mm 4mm 0;font-family:'Limelight';font-size:14pt;color:var(--sd);letter-spacing:.06em}}
.stage .flow{{margin:2.4mm auto 1.6mm}}

/* bottom */
.bottom{{display:grid;grid-template-columns:1fr 186mm;column-gap:6mm}}
.review{{overflow:hidden}}
.review .ttl{{display:flex;align-items:center;gap:3mm;padding:1.6mm 4mm 1.6mm;background:#1B1320;color:{CREAM}}}
.review .ttl h2{{font-family:'Limelight';font-weight:400;font-size:21pt;color:{GOLD};white-space:nowrap}}
.review .ttl .src{{margin-left:auto;color:#CFC6D6}}
.tg{{display:grid;grid-template-columns:80mm repeat(3,minmax(0,1fr))}}
.tg > div{{padding:.55mm 3mm;border-top:.35mm solid #DCCDB3;display:flex;align-items:center;white-space:nowrap;font-stretch:condensed}}
.tg .lab{{gap:2mm;font-weight:800;line-height:1;font-size:20.5pt;font-stretch:semi-condensed;padding-left:2.4mm;white-space:normal !important}}
.tg .lab .ic{{width:8.6mm;height:8.6mm}}
.tg .h{{font-family:'Limelight';font-size:19pt;justify-content:center;color:#fff;border-top:none;padding:1.4mm 2mm 1.5mm}}
.tg .div{{grid-column:1 / -1;background:#EADCC3;font-family:'Limelight';font-size:15pt;letter-spacing:.08em;padding:.5mm 3mm .7mm 3.6mm;color:#4a3d52;border-top:.5mm solid {INK}}}
.c1{{background:{AMS}}} .c2{{background:{TLS}}} .c3{{background:{NVS}}}
.c1 b{{color:{AMD}}} .c2 b{{color:{TLD}}} .c3 b{{color:{NVD}}}
.tg ul{{list-style:none}}
.tg li{{padding-left:4.4mm;position:relative;line-height:1.04}}
.tg li::before{{position:absolute;left:0;top:0;font-weight:800}}
.adv li::before{{content:"+";color:#2E8A50}} .dis li::before{{content:"\\2013";color:#C0392B}}

.oman{{padding:2mm 4mm 2mm;display:flex;flex-direction:column;gap:.8mm;box-shadow:0 0 0 1mm {TL}, 1.6mm 1.6mm 0 1mm #120C16}}
.oman h2{{font-family:'Limelight';font-weight:400;font-size:19.5pt;color:{TLD};line-height:1.05;white-space:nowrap}}
.oman h4{{font-size:22pt;font-weight:800;display:flex;align-items:center;gap:1.6mm;line-height:1;margin-top:.6mm}}
.oman .it{{display:flex;gap:2mm;align-items:center;line-height:1.04;white-space:nowrap}}
.oman .it .ic{{width:7.6mm;height:7.6mm}}

/* footer */
.footer{{display:grid;grid-template-columns:182mm 1fr;column-gap:6mm;margin-top:auto;align-items:stretch}}
.call{{background:{GOLD};border:.6mm solid {INK};border-radius:3.6mm;padding:1.4mm 4mm 1.6mm;line-height:1.06;display:flex;align-items:center}}
.call > span{{display:block}}
.call b{{font-family:'Limelight';font-weight:400;font-size:19pt;margin-right:2mm}}
.refs{{background:{CREAM};border:.6mm solid {INK};border-radius:3.6mm;padding:1.4mm 3.6mm 1.4mm;display:grid;grid-template-columns:40mm 1fr;column-gap:3mm}}
.refs h3{{font-family:'Limelight';font-weight:400;font-size:18pt;line-height:1.05;color:{VEL}}}
.refs h3 small{{display:block;font-family:'Bricolage Grotesque';font-weight:600;font-size:10.5pt;color:#6a6474;margin-top:.6mm}}
.refs ul{{columns:3;column-gap:4mm;list-style:none;font-size:10pt;line-height:1.13}}
.refs li{{break-inside:avoid;padding-left:3.6mm;text-indent:-3.6mm;margin-bottom:.4mm}}
</style></head>
<body><div class="page">
<svg width="0" height="0" style="position:absolute"><defs>{DEFS}{EXTRA}</defs></svg>

<svg class="curtains" viewBox="0 0 594 420" width="594mm" height="420mm">
  {''.join(f'<path d="M{x} 0 Q{x+2.5} 210 {x} 420" stroke="{VELD}" stroke-width="2.2" fill="none"/>' for x in (1.4, 5.2, 8.6))}
  <rect x="0" y="0" width="10" height="420" fill="{VEL}" opacity=".85"/>
  <rect x="584" y="0" width="10" height="420" fill="{VEL}" opacity=".85"/>
  {''.join(f'<path d="M{x} 0 Q{x-2.5} 210 {x} 420" stroke="{VELD}" stroke-width="2.2" fill="none"/>' for x in (585.4, 589, 592.6))}
  <path d="M0 0 H10 V420 H0Z M584 0 H594 V420 H584Z" fill="none" stroke="{GOLD}" stroke-width=".4"/>
</svg>

<div class="band">
  <span class="who">Student Names</span>
  <span class="m"><b>Mais altoubi</b><i>31j2573</i></span>
  <span class="m"><b>Alshima Almahrooqi</b><i>21S252540139</i></span>
  <span class="m"><b>Nardeen alfarsi</b><i>21J2583</i></span>
  <span class="m"><b>shatha al_umeiri</b><i>21J25157</i></span>
</div>

<div class="marquee">
  {svg(MARQ, MW, MH)}
  <div class="mq">
    <div class="title">Who Pulls the Strings?</div>
    <div class="right">
      <p class="summary">Every society must decide <b>what</b>, <b>how</b> and <b>for whom</b> to produce. An economic system is the answer to: <b>who decides?</b></p>
      <div class="chips"><span class="chip solid">BSEC1103 &middot; Principles of Economics</span><span class="chip">Chapter 2 &middot; Economic Systems</span></div>
    </div>
  </div>
</div>

<section class="middle">
  <div class="card script">
    <div class="act">ACT I &middot; THE SCRIPT</div>
    <h2>What is an economic system?</h2>
    <p>The <b>means by which a society or government organises and distributes</b> its resources, goods and services: its <b>mode of production and distribution</b>. <span class="src">(Fernando, 2026)</span></p>
    <h2 style="margin-top:.8mm">Why does a society need one?</h2>
    <p>Resources are <b>scarce</b> but wants are <b>unlimited</b>, so every society must choose. Its system answers <b>3 central questions</b>: <span class="src">(Mankiw, 2021)</span></p>
    <div class="qrow"><div class="q">{ic('i-what')}WHAT?</div><div class="q">{ic('i-how')}HOW?</div><div class="q" style="flex:1.5">{ic('i-whom')}FOR WHOM?</div></div>
  </div>

  <div class="card stage" style="--s:{AM};--sd:{AMD}">
    <div class="sign"><b>Capitalist Economy</b><span>market &middot; free</span></div>
    <div class="art">{svg(CAP, 140, 66, style='width:100%;height:auto')}</div>
    <ul><li>Resources <b>privately owned</b></li><li><b>Freedom</b> to start any business</li><li>Buyers choose, <b>by their income</b></li><li>Guided by <b>profit &amp; competition</b></li></ul>
    {svg(FLBL.replace('{c}', AMD) + F_CAP, 130, 31, 'flow')}
  </div>
  <div class="card stage" style="--s:{TL};--sd:{TLD}">
    <div class="sign"><b>Mixed Economy</b><span>public + private</span></div>
    <div class="art">{svg(MIX, 140, 66, style='width:100%;height:auto')}</div>
    <ul><li><b>Public &amp; private</b> sectors co-exist</li><li><b>Both</b> decide output &amp; distribution</li><li><b>Planning</b> controls the economy</li><li>Protects <b>consumer &amp; labour rights</b></li></ul>
    {svg(FLBL.replace('{c}', TLD) + F_MIX, 130, 31, 'flow')}
  </div>
  <div class="card stage" style="--s:{NV};--sd:{NVD}">
    <div class="sign"><b>Socialist Economy</b><span>command</span></div>
    <div class="art">{svg(COM, 140, 66, style='width:100%;height:auto')}</div>
    <ul><li><b>State owns</b> banks &amp; industry</li><li><b>Central authority</b> decides all</li><li><b>Fixed</b>, reasonable prices</li><li><b>Equal jobs</b> for all; social welfare</li></ul>
    {svg(FLBL.replace('{c}', NVD) + F_COM, 130, 31, 'flow')}
  </div>
</section>

<section class="bottom">
  <div class="card review">
    <div class="ttl"><span class="act">ACT III</span><h2>The Review: 3 central questions &amp; comparison table</h2><span class="src">(Fernando, 2026)</span></div>
    <div class="tg">
      <div class="h" style="background:#3A2C44;justify-content:flex-start;font-family:'Bricolage Grotesque';font-weight:800;font-size:19pt">Criteria</div>
      <div class="h" style="background:{AM}">Capitalist</div><div class="h" style="background:{TL}">Mixed</div><div class="h" style="background:{NV}">Socialist (Command)</div>
      <div class="div">THE 3 CENTRAL QUESTIONS: WHO ANSWERS THEM?</div>
      <div class="lab">{ic('i-what')}What to produce?</div><div class="c1">Whatever consumers demand</div><div class="c2">Demand + national plans</div><div class="c3">Central authority&rsquo;s plan</div>
      <div class="lab">{ic('i-how')}How to produce?</div><div class="c1">Producers choose, for profit</div><div class="c2">Private firms + public sector</div><div class="c3">State organises production</div>
      <div class="lab">{ic('i-whom')}For whom?</div><div class="c1">Buyers, by their income</div><div class="c2">Market + social welfare</div><div class="c3">State allocates to citizens</div>
      <div class="div">COMPARISON TABLE</div>
      <div class="lab">{ic('i-key')}Ownership of resources</div><div class="c1"><span><b>Private</b> individuals</span></div><div class="c2"><span><b>Public + private</b></span></div><div class="c3"><span><b>Government</b></span></div>
      <div class="lab">{ic('i-gov')}Role of government</div><div class="c1"><span><b>Little</b>: no interference</span></div><div class="c2"><span><b>Plans</b> &amp; controls</span></div><div class="c3"><span><b>Total</b>: decides all</span></div>
      <div class="lab">{ic('i-tag')}Price mechanism</div><div class="c1"><span><b>Free</b> market prices</span></div><div class="c2"><span><b>Prices</b> + planning</span></div><div class="c3"><span><b>Fixed</b> by the authority</span></div>
      <div class="lab">{ic('i-motive')}Motive</div><div class="c1"><span><b>Profit</b></span></div><div class="c2"><span><b>Profit + social interest</b></span></div><div class="c3"><span><b>Social welfare</b></span></div>
      <div class="lab">{ic('i-up')}Advantages</div>
      <div class="c1"><ul class="adv"><li>Equal opportunities</li><li>Innovation &amp; fast growth</li></ul></div>
      <div class="c2"><ul class="adv"><li>Best allocation of resources</li><li>Via prices, profit &amp; liberty</li></ul></div>
      <div class="c3"><ul class="adv"><li>Efficient use; stability</li><li>Max welfare; no monopoly</li></ul></div>
      <div class="lab">{ic('i-down')}Disadvantages</div>
      <div class="c1"><ul class="dis"><li>Rich richer, poor poorer</li><li>No welfare &rarr; poverty</li></ul></div>
      <div class="c2"><ul class="dis"><li>Sectors may not cooperate</li><li>Inefficient public sector</li></ul></div>
      <div class="c3"><ul class="dis"><li>Bureaucracy; no freedom</li><li>No tech or competition</li></ul></div>
    </div>
  </div>

  <div class="card oman">
    <div class="act" style="color:{TLD}">ACT IV &middot; THE FINALE</div>
    <h2>Oman&rsquo;s stage: a mixed economy</h2>
    {svg(OMAN_ART, 172, 40, style='width:100%;height:auto;border:.45mm solid #1C2433;border-radius:2.4mm')}
    <h4 style="color:{NVD}">{ic('i-gov')}Government sector</h4>
    <div class="it">{ic('i-compass')}<span>Plans the economy: <b>Oman Vision 2040</b></span></div>
    <div class="it">{ic('i-key')}<span>Owns state firms: <b>Oman Investment Authority</b></span></div>
    <div class="it">{ic('i-shield')}<span>Protects consumers &amp; workers by law</span></div>
    <h4 style="color:{AMD}">{ic('i-tag')}Private sector</h4>
    <div class="it">{ic('i-branch')}<span>Leads diversification beyond oil</span></div>
    <div class="it">{ic('i-bridge')}<span>Partners the state in <b>PPP</b> projects</span></div>
    <div class="it">{ic('i-how')}<span>Takes over state firms via <b>privatisation</b></span></div>
    <span class="src" style="font-size:13pt;white-space:normal">(Oman Vision 2040 Main Committee, 2019; Royal Decrees 66/2014, 51/2019, 52/2019, 61/2020, 53/2023)</span>
  </div>
</section>

<section class="footer">
  <div class="call"><span><b>Curtain call:</b>The mixed economy blends market freedom with social welfare: the model Oman follows.</span></div>
  <div class="refs">
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
