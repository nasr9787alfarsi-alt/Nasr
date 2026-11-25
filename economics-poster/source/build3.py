#!/usr/bin/env python3
"""WHO'S COOKING THE ECONOMY? - A2 portrait poster (420 x 594 mm), Chapter 2 Economic Systems."""
import pathlib
HERE = pathlib.Path(__file__).parent
src = (HERE / 'lib' / 'islands_symbols.py').read_text()
exec(src.split('# ------------------------------------------------------------------ ISLANDS SCENE')[0])  # C, INK, SW, DEFS, use, pill, gear...

# ---------- palette for this poster
MK, MKD, MKS = '#D9503F', '#A93A2C', '#FBE3DC'      # market: tomato
MX_, MXD, MXS = '#2F8F7A', '#1F6B5B', '#DCEFE8'     # mixed: olive-teal
CM, CMD, CMS = '#2E4A86', '#22376A', '#E0E6F3'      # command: navy
MUST = '#F0B13B'
PAPER = '#FBF1E1'

EXTRA = f'''
<g id="toque"><circle cx="-2.3" cy="-16.3" r="2.1" fill="#fff" {SW}/><circle cx="2.3" cy="-16.3" r="2.1" fill="#fff" {SW}/><circle cx="0" cy="-17.6" r="2.4" fill="#fff" {SW}/>
  <rect x="-2.9" y="-15.6" width="5.8" height="3" rx=".4" fill="#fff" {SW}/></g>
<g id="tray"><rect x="-4.6" y="-6.4" width="9.2" height="1.3" rx=".5" fill="#B9BFCC" {SW}/><path d="M-2.4 -6.4 Q0 -9.6 2.4 -6.4Z" fill="{MUST}" {SW}/></g>
<g id="clip"><rect x="-1.6" y="-1" width="3.2" height="3.4" rx=".6" fill="#B9BFCC" {SW}/></g>
<g id="dallah">
  <path d="M-4.4 -7 Q-11 -9 -7.6 -17" fill="none" stroke="{INK}" stroke-width="1.1" stroke-linecap="round"/>
  <path d="M4.2 -8.6 Q10.6 -11 11.6 -21.4 Q10.2 -20.6 9.6 -14.6 Q8.2 -10 4 -6.8Z" fill="#E0AE4A" {SW}/>
  <path d="M-6.6 0 Q-9.6 -6.2 -4.8 -10.4 L-2.8 -16.6 Q-4 -18.4 -2 -19.2 H2 Q4 -18.4 2.8 -16.6 L4.8 -10.4 Q9.6 -6.2 6.6 0Z" fill="#E0AE4A" {SW}/>
  <path d="M-5.6 -6 H5.6" stroke="#B9862C" stroke-width=".6"/>
  <path d="M-2.6 -19.2 Q0 -24.4 2.6 -19.2Z" fill="#E0AE4A" {SW}/><circle cx="0" cy="-24.6" r=".9" fill="#E0AE4A" {SW}/>
  <rect x="-7.2" y="-.6" width="14.4" height="1.6" rx=".6" fill="#C9963A" {SW}/>
</g>
<g id="cup"><path d="M-2.4 -3.2 H2.4 L1.8 0 H-1.8Z" fill="#fff" {SW}/></g>
<g id="megaphone"><path d="M0 -1 L5 -3.4 V3.4 L0 1Z" fill="{MUST}" {SW}/><rect x="-1.6" y="-1.2" width="1.8" height="2.4" fill="{CMD}" {SW}/></g>
<g id="jar"><rect x="-8" y="-17" width="16" height="17" rx="3" fill="#EAF4F3" {SW}/><rect x="-6.4" y="-19.6" width="12.8" height="3" rx="1" style="fill:var(--lid,{MK})" {SW}/>
  <rect x="-7" y="-7.6" width="14" height="5" rx="1" fill="#fff" {SW}/></g>
<g id="ejar"><rect x="-8" y="-17" width="16" height="17" rx="3" fill="none" stroke="{INK}" stroke-width=".45" stroke-dasharray="1.2 1"/><rect x="-6.4" y="-19.6" width="12.8" height="3" rx="1" fill="none" stroke="{INK}" stroke-width=".45" stroke-dasharray="1.2 1"/></g>
'''

def T(x, y, txt, size=5, w=700, col=INK, anchor='middle', fam='', extra=''):
    f = f' font-family="{fam}"' if fam else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" text-anchor="{anchor}" fill="{col}"{f}{extra}>{txt}</text>'

def bubble(x, y, txt, size=4.2, col=INK, tail='down', fill='#fff'):
    w = len(txt)*size*.5 + 5; h = size*1.6
    t = f'<path d="M{x-2} {y+h/2-.2} L{x-3.4} {y+h/2+3} L{x+1.4} {y+h/2-.2}Z" fill="{fill}" {SW}/>' if tail == 'down' else ''
    return (f'<rect x="{x-w/2:.1f}" y="{y-h/2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h/2:.1f}" fill="{fill}" {SW}/>' + t +
            f'<rect x="{x-2.2}" y="{y+h/2-1.2}" width="3.8" height="1.4" fill="{fill}"/>' + T(x, y+size*.36, txt, size, 700, col))

def floor(y, w=128, h=8):
    out = [f'<rect x="0" y="{y}" width="{w}" height="{h}" fill="#fff"/>']
    for i in range(int(w/4)+1):
        for j in range(int(h/4)):
            if (i+j) % 2 == 0:
                out.append(f'<rect x="{i*4}" y="{y+j*4}" width="4" height="4" fill="{INK}" opacity=".85"/>')
    out.append(f'<path d="M0 {y} H{w}" stroke="{INK}" stroke-width=".6"/>')
    return ''.join(out)

def scene_frame(bg):
    return f'<rect x="0" y="0" width="128" height="62" fill="{bg}"/>'

# ---------- MARKET BISTRO scene (128 x 62)
FL = 54
mk = [scene_frame(MKS), floor(FL)]
for i, (x, awn, name) in enumerate([(17, MK, 'BURGERS'), (45, MUST, 'FALAFEL'), (73, MX_, 'JUICE')]):
    mk.append(use('shop', x, FL, 1.08, f'--awn:{awn}'))
    mk.append(T(x, FL-21.6*1.08+3.1, name, 2.9, 800, '#fff'))
mk.append(use('tag', 4, FL-14.6, .95)); mk.append(use('tag', 34, FL-14.6, .95)); mk.append(use('tag', 62, FL-14.6, .95))
mk.append(bubble(20, 6.2, 'Best price!', 4.4, MKD))
mk.append(bubble(56, 6.2, 'New dish!', 4.4, MKD))
# chef at stall 2 & customers choosing
mk.append(use('person', 31, FL, .95, f'--shirt:#fff;--skin:{C["skin2"]}')); mk.append(use('toque', 31, FL, .95))
for x, sh, sk in [(94, MX_, C['skin1']), (104, CM, C['skin3'])]:
    mk.append(use('person', x, FL, .95, f'--shirt:{sh};--skin:{sk}')); mk.append(use('bag', x, FL, .95))
mk.append(bubble(99, 20, 'Which one?', 4.2, INK))
# tiny limited government
mk.append(use('gov', 120, FL, .34))
mk.append(f'<circle cx="120" cy="{FL-3.6}" r="5.6" fill="none" stroke="{CM}" stroke-width=".45" stroke-dasharray="1.1 .8"/>')
mk.append(T(114, 37, 'little', 3.8, 700, CMD) + T(114, 41.4, 'gov’t', 3.8, 700, CMD))
MARKET = ''.join(mk)

# ---------- STATE CANTEEN scene
cm = [scene_frame(CMS), floor(FL)]
cm.append(f'<rect x="6" y="17" width="74" height="{FL-17}" fill="#5A6FAE" {SW}/>')
cm.append(f'<rect x="3" y="11" width="80" height="7" rx="1.2" fill="{CMD}" {SW}/>')
cm.append(T(43, 16.4, 'STATE CANTEEN No. 1', 4.4, 800, '#fff'))
for r in range(2):
    for c in range(4):
        if not (r == 1 and c in (1, 2)):
            cm.append(f'<rect x="{10+c*7.6}" y="{22+r*11}" width="5" height="7" fill="#F4D67A" {SW}/>')
cm.append(f'<rect x="16" y="{FL-10}" width="9" height="10" fill="{CMD}" {SW}/>')
# fixed menu board
cm.append(f'<rect x="44" y="21" width="32" height="24" rx="1.2" fill="#FFF8EC" {SW}/>')
cm.append(T(60, 26.6, 'TODAY’S MENU', 3.8, 800, CMD))
cm.append(f'<path d="M47 28.6 H73" stroke="{INK}" stroke-width=".35"/>')
cm.append(T(60, 33.4, 'Meal A only', 4.2, 700, INK))
cm.append(T(60, 38.6, 'Price: FIXED', 4.2, 800, MK))
cm.append(T(60, 43.2, 'by central authority', 2.9, 600, CMD))
# planner on roof with megaphone
cm.append(use('person', 30, 11, .9, f'--shirt:{CMD};--skin:{C["skin1"]}'))
cm.append(use('megaphone', 33.4, 11-6.4, 1.0))
cm.append(bubble(56, 4.2, 'The plan decides!', 4.2, CMD, tail='none'))
# identical queue with trays
for i in range(4):
    x = 89 + i*9.4
    cm.append(use('person', x, FL, .95, f'--shirt:#9AAAD0;--skin:{C["skin1"] if i % 2 else C["skin2"]}'))
    cm.append(use('tray', x, FL-1.4, .95))
cm.append(T(103, 30, 'same meal', 4, 700, CMD) + T(103, 34.6, 'for all', 4, 700, CMD))
CANTEEN = ''.join(cm)

# ---------- MIXED FOOD COURT scene
mx = [scene_frame(MXS), floor(FL)]
mx.append(f'<path d="M6 {FL} V4 M122 {FL} V4" stroke="{INK}" stroke-width=".8"/>')
mx.append(f'<path d="M6 5 Q64 12 122 5 V11 Q64 18 6 11Z" fill="{MX_}" {SW}/>')
mx.append(T(64, 12.6, 'PLANNING &amp; RULES', 4.2, 800, '#fff'))
# public kitchen (left)
mx.append(use('gov', 24, FL, 1.25, f'--groof:{CM}'))
mx.append(T(24, FL-26.4, 'PUBLIC', 3.6, 800, CMD))
# private stalls (right)
mx.append(use('shop', 92, FL, 1.0, f'--awn:{MK}')); mx.append(T(92, FL-18.6, 'PRIVATE', 2.8, 800, '#fff'))
mx.append(use('shop', 114, FL, 1.0, f'--awn:{MUST}')); mx.append(T(114, FL-18.6, 'CAFÉ', 2.8, 800, '#fff'))
# inspector with shield & diners
mx.append(use('person', 58, FL, .95, f'--shirt:{MXD};--skin:{C["skin2"]}'))
mx.append(use('i-shield', 61.6, FL-5, .55))
mx.append(bubble(56, 25, 'Fair for all!', 4.2, MXD))
mx.append(use('person', 47, FL, .9, f'--shirt:{MK};--skin:{C["skin3"]}')); mx.append(use('tray', 47, FL-1.4, .9))
mx.append(use('person', 69, FL, .9, f'--shirt:{CM};--skin:{C["skin1"]}')); mx.append(use('tray', 69, FL-1.4, .9))
MIXED = ''.join(mx)

# ---------- PANTRY (intro centre) 104 x 64
p = []
p.append(f'<rect x="8" y="9" width="88" height="48" rx="2" fill="#B98552" {SW}/>')
p.append(f'<rect x="11" y="12" width="82" height="42" fill="#F3E2C6" {SW}/>')
p.append(f'<rect x="11" y="32" width="82" height="2.6" fill="#B98552" {SW}/>')
p.append(f'<rect x="20" y="1" width="64" height="9" rx="2" fill="{MK}" {SW}/>')
p.append(T(52, 7.6, 'PANTRY: LIMITED STOCK', 4.6, 800, '#fff'))
for x, ic, lab, lid in [(27, 'i-wheat', 'LAND', MUST), (52, 'i-hat', 'LABOUR', MK), (77, 'i-how', 'CAPITAL', CM)]:
    p.append(use('jar', x, 32, 1.0, f'--lid:{lid}'))
    p.append(use(ic, x, 20.6, .95))
    p.append(T(x, 28.5, lab, 2.9, 800, INK))
p.append(use('ejar', 27, 54, 1.0)); p.append(use('ejar', 52, 54, 1.0))
p.append(T(39.5, 46, 'empty!', 4.2, 800, MKD))
# unlimited wants receipt spilling out
p.append(f'<path d="M66 37 H86 V58 Q84 60 82 58 Q80 56 78 58 Q76 60 74 58 Q72 56 70 58 Q68 60 66 58Z" fill="#fff" {SW}/>')
p.append(T(76, 41.6, 'WANTS', 3.4, 800, MKD))
for i in range(5):
    p.append(f'<path d="M68 {44.6+i*2.4} H{84-(i % 3)*3}" stroke="{INK}" stroke-width=".35"/>')
p.append(f'<path d="M80 58 Q90 62 96 58 Q100 56 101 61" fill="none" stroke="{INK}" stroke-width=".35" stroke-dasharray="1 .8"/>')
p.append(T(52, 63.6, 'scarce resources vs. unlimited wants', 4.2, 700, INK))
PANTRY = ''.join(p)

# ---------- TICKET-RAIL FLOWCHARTS (118 x 44)
def ticket(x, ic, lines, col, w=34):
    zz = ''.join(f' L{x-w/2+(k+1)*w/10:.2f} {29 + (1.4 if k % 2 == 0 else 0)}' for k in range(10))
    body = f'<path d="M{x-w/2} 5 H{x+w/2} V29{zz.replace(f"L{x+w/2:.2f}", "L"+f"{x+w/2:.2f}")} L{x-w/2} 29Z" fill="#fff" {SW}/>'
    body = f'<path d="M{x-w/2} 5 H{x+w/2} V29.7' + ''.join(f' L{x+w/2-(k+1)*w/10:.2f} {29.7 + (1.4 if k % 2 == 0 else 0)}' for k in range(10)) + f'Z" fill="#fff" {SW}/>'
    out = [body, f'<rect x="{x-w/2}" y="5" width="{w}" height="2.4" fill="{col}"/>', use('clip', x, 3.4, 1.0), use(ic, x, 13.6, .95)]
    for i, ln in enumerate(lines):
        out.append(T(x, 23.4 + i*5.2 - (2.6 if len(lines) > 1 else 0), ln, 5.0, 700, INK))
    return ''.join(out)

def arr(x1, x2, y, col, lab=''):
    o = f'<path d="M{x1} {y} H{x2-1.8}" stroke="{col}" stroke-width=".9"/><path d="M{x2-2.8} {y-1.8} L{x2} {y} L{x2-2.8} {y+1.8}Z" fill="{col}"/>'
    return o

def rail():
    return (f'<path d="M1 2.4 H117" stroke="#8C93A3" stroke-width="1.3" stroke-linecap="round"/>'
            f'<rect x="-2" y="-3.2" width="27" height="5.2" rx="2.6" fill="{INK}"/>' + T(11.5, .7, 'FLOWCHART', 3.9, 800, '#FFF6E6', extra=' letter-spacing=".35"'))

FLOW_MK = (rail() + ticket(18, 'i-whom', ['Consumers'], MK) + arr(35.4, 42.6, 17, MKD) + ticket(59, 'i-tag', ['Market', 'price'], MK) +
           arr(76.4, 83.6, 17, MKD) + ticket(100, 'i-how', ['Producers'], MK) +
           f'<path d="M100 32.6 V36.6 H18 V33.4" fill="none" stroke="{MKD}" stroke-width=".8"/><path d="M16.2 34.6 L18 31.8 L19.8 34.6Z" fill="{MKD}"/>' +
           f'<rect x="31" y="34" width="56" height="5.6" fill="{MKS}"/>' + T(59, 38.4, 'goods for buyers who can pay', 4.4, 700, MKD))
FLOW_CM = (rail() + ticket(18, 'i-plan', ['Central', 'authority'], CM) + arr(35.4, 42.6, 17, CMD) + ticket(59, 'i-how', ['State-owned', 'firms'], CM) +
           arr(76.4, 83.6, 17, CMD) + ticket(100, 'i-whom', ['Citizens'], CM) +
           f'<rect x="20" y="34" width="78" height="5.6" rx="2.8" fill="{CM}"/>' + T(59, 38.4, 'plan sets output &amp; fixed prices', 4.4, 700, '#fff'))
FLOW_MX = (rail() + ticket(18, 'i-gov', ['Public', 'sector'], MX_) + T(38.8, 20.4, '+', 9, 800, MXD) + ticket(59, 'i-tag', ['Private', 'sector'], MX_) +
           arr(76.4, 83.6, 17, MXD) + ticket(100, 'i-what', ['Goods &amp;', 'services'], MX_) +
           f'<rect x="10" y="34" width="98" height="5.6" rx="2.8" fill="{MX_}"/>' + T(59, 38.4, 'price mechanism + government planning', 4.4, 700, '#fff'))

def svg(inner, w, h, cls='', style=''):
    return f'<svg class="{cls}" viewBox="0 0 {w} {h}" width="{w}mm" height="{h}mm" style="display:block;overflow:visible;{style}">{inner}</svg>'

def ic(i, s=1.0):
    return f'<svg class="ic" viewBox="-6 -6 12 12"><use href="#{i}" transform="scale({s})"/></svg>'

def plate(n, col=INK):
    return f'<span class="plate" style="--pc:{col}"><span>{n}</span></span>'

ARCH = 'M4 54 V22 Q4 8 22 4 Q34 1.6 40 -4 Q46 1.6 58 4 Q76 8 76 22 V54Z'
OMAN_ART = (f'<clipPath id="archc"><path d="{ARCH}"/></clipPath><g clip-path="url(#archc)"><rect x="0" y="-6" width="80" height="62" fill="#F4D9A8"/>'
            f'<circle cx="62" cy="13" r="7" fill="#F4A94A" opacity=".8"/>'
            f'<path d="M0 40 H80 V51 Q80 54 77 54 H3 Q0 54 0 51Z" fill="#3C93A0"/>' + waves(43, 2, 78, step=7, amp=.7, op=.5) +
            f'<path d="M2 40 Q16 31 40 32 Q54 33 64 40Z" fill="#EFD9AE" {SW}/>' +
            use('fort', 26, 37, .9) + use('palm', 10, 38, .8) + use('dhow', 62, 50, .7) + use('dallah', 54, 37.6, .62) + use('cup', 61, 37.6, .7) + '</g>' +
            f'<path d="{ARCH}" fill="none" stroke="{INK}" stroke-width=".7"/><path d="M1 54 V21 Q1 5.6 21 1.2 Q33 -1.2 40 -7.6 Q47 -1.2 59 1.2 Q79 5.6 79 21 V54" fill="none" stroke="{MX_}" stroke-width="1.6"/>')

HTML = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Who's Cooking the Economy?</title>
<link rel="stylesheet" href="fonts/fonts.css">
<style>
@page {{ size: 420mm 594mm; margin: 0; }}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:420mm;height:594mm}}
body{{font-family:'Bricolage Grotesque',sans-serif;font-stretch:semi-condensed;color:{INK};font-size:24pt;line-height:1.13;background:{PAPER};
  -webkit-print-color-adjust:exact;print-color-adjust:exact}}
svg text{{font-family:'Bricolage Grotesque';font-stretch:semi-condensed}}
b{{font-weight:700}}
.page{{position:relative;width:420mm;height:594mm;overflow:hidden;display:flex;flex-direction:column;gap:1.9mm;padding:0 11mm 3mm}}
.page > *{{flex-shrink:0}}
.ic{{width:9mm;height:9mm;flex:none;overflow:visible}}
.plate{{width:12mm;height:12mm;border-radius:50%;background:#fff;border:.55mm solid {INK};box-shadow:inset 0 0 0 1.2mm #fff, inset 0 0 0 1.6mm var(--pc);display:inline-flex;align-items:center;justify-content:center;flex:none}}
.plate span{{font-family:'Shrikhand';font-size:22pt;color:var(--pc);line-height:1;transform:translateY(.4mm)}}
.src{{font-size:15pt;color:#6a6f7d;font-weight:500;white-space:nowrap}}
.box{{background:#FFFBF4;border:.6mm solid {INK};border-radius:4.5mm;box-shadow:1.3mm 1.3mm 0 {INK}}}
h2.sh{{display:flex;align-items:center;gap:2.6mm;font-weight:800;font-size:26pt;line-height:1;white-space:nowrap;letter-spacing:-.01em}}

/* credits band (top) */
.credits{{margin:0 -11mm;background:{INK};color:#FFF6E6;display:flex;align-items:center;justify-content:space-between;padding:2mm 11mm 2.2mm;font-size:22pt;line-height:1.1}}
.credits .who{{font-weight:800;letter-spacing:.1em;color:{MUST};font-size:18pt}}
.credits .m{{display:flex;gap:2mm;align-items:baseline}}
.credits .m b{{font-weight:700}}
.credits .m i{{font-style:normal;font-stretch:condensed;color:#BFD0F0;font-weight:600}}

/* header */
header{{display:grid;grid-template-columns:1fr 46mm;column-gap:6mm;align-items:center;margin-top:1mm}}
.title{{font-family:'Shrikhand';font-size:59pt;line-height:1;color:{MK};-webkit-text-stroke:.5mm {INK};text-shadow:1.2mm 1.2mm 0 {INK};letter-spacing:.2mm;white-space:nowrap}}
.title em{{font-style:normal;color:{MX_}}} .title u{{text-decoration:none;color:{CM}}}
.summary{{font-size:24pt;margin-top:2mm;white-space:nowrap}}
.summary b{{font-weight:800}}
.chips{{display:flex;gap:3mm;margin-top:1.8mm}}
.chip{{font-size:22pt;font-weight:700;padding:.8mm 4mm 1.1mm;border-radius:10mm;border:.5mm solid {INK};background:#fff;line-height:1.1}}
.chip.dark{{background:{INK};color:#FFF6E6}}

/* intro */
.intro{{display:grid;grid-template-columns:1fr 94mm 1fr;column-gap:5mm;align-items:stretch}}
.recipe{{padding:2.8mm 4.5mm 3mm;background-image:repeating-linear-gradient(180deg,transparent 0 9.1mm,#E9D9BF 9.1mm 9.4mm);background-position:0 15mm}}
.order{{padding:2.8mm 4.5mm 3mm}}
.qrow{{display:flex;gap:2mm;margin-top:1.8mm}}
.q{{flex:1;display:flex;gap:1.4mm;justify-content:center;align-items:center;white-space:nowrap;background:#fff;border:.45mm solid {INK};border-radius:3mm;padding:1.2mm 1mm;font-weight:800;font-size:21pt}}
.q .ic{{width:8.5mm;height:8.5mm}}

/* kitchens */
.kitchens{{display:grid;grid-template-columns:repeat(3,1fr);column-gap:7mm;position:relative}}
.vtab{{position:absolute;left:-10.4mm;top:0;bottom:0;width:9.4mm;display:flex;flex-direction:column-reverse;align-items:center;justify-content:center;gap:2mm}}
.vtab span{{writing-mode:vertical-rl;transform:rotate(180deg);font-weight:800;font-size:22pt;white-space:nowrap;line-height:1}}
.vtab .plate{{width:9mm;height:9mm}} .vtab .plate span{{writing-mode:horizontal-tb;transform:none;font-family:'Shrikhand';font-size:17pt;font-weight:400}}
.kit{{overflow:hidden;display:flex;flex-direction:column}}
.kit .sign{{display:flex;justify-content:space-between;align-items:baseline;white-space:nowrap;padding:1.8mm 4mm 2mm;color:#fff;border-bottom:.6mm solid {INK}}}
.kit .sign b{{font-family:'Shrikhand';font-weight:400;font-size:23pt;line-height:1}}
.kit .sign span{{font-size:17pt;font-weight:700;opacity:.95}}
.kit .art{{border-bottom:.6mm solid {INK}}}
.kit ul{{list-style:none;padding:1.8mm 4mm 0;white-space:nowrap}}
.kit li{{padding-left:5.6mm;position:relative;line-height:1.06;margin-bottom:.2mm}}
.kit li::before{{content:"";position:absolute;left:.6mm;top:2.6mm;width:3mm;height:3mm;border-radius:50%;background:var(--k);border:.35mm solid {INK}}}
.kit .flowlbl{{margin:1.2mm 4mm .2mm;font-size:15pt;font-weight:800;letter-spacing:.12em;color:var(--kd)}}
.kit .flow{{margin:2.4mm auto 1.6mm}}

/* chalkboard */
.chalk{{background:#26342F;color:#F3EEE2;border:2mm solid #A9754A;border-radius:4mm;box-shadow:1.3mm 1.3mm 0 {INK};padding:2mm 4mm 1.8mm;outline:.6mm solid {INK};outline-offset:0}}
.chalk h2{{display:flex;align-items:center;gap:2.6mm;font-weight:800;font-size:26pt;line-height:1;margin-bottom:.6mm}}
.chalk h2 .s{{margin-left:auto;font-size:15pt;font-weight:500;color:#C9CFC4}}
.cg{{display:grid;grid-template-columns:61mm repeat(3,1fr)}}
.cg > div{{padding:.9mm 3mm;white-space:nowrap;border-top:.35mm dashed rgba(243,238,226,.35);display:flex;align-items:center;gap:2.2mm}}
.cg .hd{{font-family:'Shrikhand';font-size:21pt;border-top:none;justify-content:center;padding-top:0;padding-bottom:.4mm}}
.cg .lab{{font-weight:800;font-size:24pt}}
.cg .lab .ic{{width:9mm;height:9mm;background:#F3EEE2;border-radius:50%;padding:.6mm}}

/* table */
.review{{overflow:hidden}}
.gingham{{height:5mm;background-color:#fff;background-image:linear-gradient(90deg,rgba(217,80,63,.55) 50%,transparent 50%),linear-gradient(0deg,rgba(217,80,63,.55) 50%,transparent 50%);background-size:6mm 6mm;border-bottom:.6mm solid {INK}}}
.review h2{{padding:1.8mm 5mm 1.4mm}}
.review h2 .s{{margin-left:auto;font-size:15pt;font-weight:500;color:#6a6f7d}}
.tg{{display:grid;grid-template-columns:80mm repeat(3,1fr)}}
.tg > div{{padding:.75mm 3.4mm;white-space:nowrap;border-top:.35mm solid #DCCDB3;display:flex;align-items:center}}
.tg .lab{{padding-right:.6mm !important;padding-left:2.4mm !important;gap:2mm;font-weight:800;line-height:1;font-size:20.5pt}}
.tg .lab .ic{{width:9.5mm;height:9.5mm}}
.tg .h{{font-family:'Shrikhand';font-size:23pt;justify-content:center;color:#fff;border-top:.6mm solid {INK};padding:1.6mm 2mm 1.8mm}}
.c1{{background:{MKS}}} .c2{{background:{MXS}}} .c3{{background:{CMS}}}
.c1 b{{color:{MKD}}} .c2 b{{color:{MXD}}} .c3 b{{color:{CMD}}}
.tg ul{{list-style:none}}
.tg li{{padding-left:5mm;position:relative;line-height:1.08}}
.tg li::before{{position:absolute;left:0;top:0;font-weight:800}}
.adv li::before{{content:"+";color:#2E8A50}} .dis li::before{{content:"\\2013";color:#C0392B}}

/* oman */
.oman{{position:relative;background:#FFF3DC;padding:2.2mm 5mm 2.4mm 3mm;display:grid;grid-template-columns:68mm 1fr 1fr;column-gap:5mm;grid-template-rows:auto 1fr;border-color:{MXD};box-shadow:1.3mm 1.3mm 0 {MXD}}}
.oman .top{{grid-column:2 / 4;display:flex;align-items:center;gap:3mm}}
.oman h2{{font-family:'Shrikhand';font-weight:400;font-size:28pt;color:{MXD};line-height:1;white-space:nowrap}}
.oman .lead{{font-size:23pt;line-height:1.08}}
.oman h4{{font-size:24pt;font-weight:800;margin:1mm 0 .4mm;display:flex;align-items:center;gap:2mm}}
.oman .it{{display:flex;gap:2.2mm;align-items:center;line-height:1.06;margin-top:1mm}}
.oman .it .ic{{width:8.5mm;height:8.5mm}}
.arch{{position:absolute;left:-.6mm;right:-.6mm;top:-5.4mm;height:5.4mm;overflow:visible}}

/* conclusion + refs */
.concl{{display:flex;align-items:center;gap:3mm;background:{MUST};border:.6mm solid {INK};border-radius:20mm;padding:.9mm 6mm .9mm 1.4mm;box-shadow:1.3mm 1.3mm 0 {INK}}}
.concl b{{font-family:'Shrikhand';font-weight:400;font-size:22pt;white-space:nowrap}}
.refs{{display:grid;grid-template-columns:35mm 1fr;column-gap:4mm;border-top:.5mm solid {INK};padding-top:1.4mm;margin-top:auto}}
.refs h3{{font-family:'Shrikhand';font-weight:400;font-size:17pt;line-height:1.05}}
.refs h3 small{{display:block;font-family:'Bricolage Grotesque';font-weight:600;font-size:11pt;color:#6a6f7d;margin-top:.6mm}}
.refs ul{{columns:4;column-gap:4.5mm;list-style:none;font-size:10.5pt;line-height:1.14}}
.refs li{{break-inside:avoid;padding-left:4mm;text-indent:-4mm;margin-bottom:.5mm}}
</style></head>
<body><div class="page">
<svg width="0" height="0" style="position:absolute"><defs>{DEFS}{EXTRA}</defs></svg>

<div class="credits">
  <span class="who">THE CHEFS</span>
  <span class="m"><b>Mais altoubi</b><i>31j2573</i></span>
  <span class="m"><b>Alshima Almahrooqi</b><i>21S252540139</i></span>
  <span class="m"><b>Nardeen alfarsi</b><i>21J2583</i></span>
  <span class="m"><b>shatha al_umeiri</b><i>21J25157</i></span>
</div>

<header>
  <div>
    <div class="title">Who&rsquo;s Cooking <em>the</em> <u>Economy?</u></div>
    <p class="summary"><b>Scarce ingredients</b>, one big question: who decides <b>what</b> to cook, <b>how</b>, and <b>for whom</b>?</p>
    <div class="chips"><span class="chip dark">BSEC1103 &middot; Principles of Economics</span><span class="chip">Chapter 2 &middot; Economic Systems</span></div>
  </div>
  {svg(use('person', 23, 46, 2.2, f'--shirt:#fff;--skin:{C["skin2"]}') + use('toque', 23, 46, 2.2) + use('i-what', 36, 30, 1.2) +
       f'<path d="M4 46 H42" stroke="{INK}" stroke-width=".8"/>' + use('tray', 9.5, 39, 1.3), 46, 48)}
</header>

<section class="intro">
  <div class="box recipe">
    <h2 class="sh">{plate(1, MK)}What is an economic system?</h2>
    <p style="margin-top:1.6mm">The <b>means by which a society organises and distributes</b> its resources, goods and services: its <b>mode of production and distribution</b>. <span class="src">(Fernando, 2026)</span></p>
  </div>
  {svg(PANTRY, 104, 65, style='width:94mm;height:58.8mm;align-self:center')}
  <div class="box order">
    <h2 class="sh">{plate(2, MX_)}Why every society needs one</h2>
    <p style="margin-top:1.6mm">Resources are <b>scarce</b>, wants are <b>unlimited</b>, so every society must choose. Its system answers: <span class="src">(Mankiw, 2021)</span></p>
    <div class="qrow"><div class="q">{ic('i-what')}WHAT?</div><div class="q">{ic('i-how')}HOW?</div><div class="q" style="flex:1.45">{ic('i-whom')}FOR WHOM?</div></div>
  </div>
</section>

<section class="kitchens"><div class="vtab">{plate(3, CM)}<span>How each system works</span></div>
  <div class="box kit" style="--k:{MK};--kd:{MKD}">
    <div class="sign" style="background:{MK}"><b>Market Bistro</b><span>capitalist</span></div>
    <div class="art">{svg(MARKET, 128, 62, style='width:100%;height:auto')}</div>
    <ul><li><b>Private</b> ownership of resources</li><li><b>No government</b> interference</li><li>Free choice, guided by <b>profit</b></li></ul>
    {svg(FLOW_MK, 118, 40, 'flow')}
  </div>
  <div class="box kit" style="--k:{MX_};--kd:{MXD}">
    <div class="sign" style="background:{MX_}"><b>Mixed Food Court</b><span>mixed</span></div>
    <div class="art">{svg(MIXED, 128, 62, style='width:100%;height:auto')}</div>
    <ul><li><b>Public &amp; private</b> co-exist</li><li><b>Both</b> decide what &amp; for whom</li><li>Planning + <b>profit &amp; welfare</b></li></ul>
    {svg(FLOW_MX, 118, 40, 'flow')}
  </div>
  <div class="box kit" style="--k:{CM};--kd:{CMD}">
    <div class="sign" style="background:{CM}"><b>State Canteen</b><span>socialist / command</span></div>
    <div class="art">{svg(CANTEEN, 128, 62, style='width:100%;height:auto')}</div>
    <ul><li><b>Government</b> owns resources</li><li><b>Central authority</b> decides all</li><li><b>Fixed prices</b>; social welfare</li></ul>
    {svg(FLOW_CM, 118, 40, 'flow')}
  </div>
</section>

<section class="chalk">
  <h2>{plate(4, MUST)}Today&rsquo;s menu: who answers the 3 central questions? <span class="s">(Fernando, 2026)</span></h2>
  <div class="cg">
    <div class="hd"></div><div class="hd" style="color:#F59A86">Capitalist / Market</div><div class="hd" style="color:#7FD3BC">Mixed</div><div class="hd" style="color:#A9BCF0">Socialist / Command</div>
    <div class="lab">{ic('i-what')}WHAT?</div><div>Whatever consumers demand</div><div>Demand + national plans</div><div>Central authority&rsquo;s plan</div>
    <div class="lab">{ic('i-how')}HOW?</div><div>Producers choose, for profit</div><div>Private firms + public sector</div><div>State organises production</div>
    <div class="lab">{ic('i-whom')}FOR WHOM?</div><div>Buyers, by their income</div><div>Market + social welfare</div><div>State allocates to citizens</div>
  </div>
</section>

<section class="box review">
  <div class="gingham"></div>
  <h2 class="sh">{plate(5, MK)}Comparison table: the three kitchens reviewed <span class="s">(Fernando, 2026)</span></h2>
  <div class="tg">
    <div class="h" style="background:{INK};justify-content:flex-start;padding-left:4mm;font-family:'Bricolage Grotesque';font-weight:800;font-size:20pt">Criteria</div>
    <div class="h" style="background:{MK}">Capitalist / Market</div><div class="h" style="background:{MX_}">Mixed</div><div class="h" style="background:{CM}">Socialist / Command</div>

    <div class="lab">{ic('i-key')}Resource ownership</div>
    <div class="c1"><span><b>Private</b> individuals</span></div><div class="c2"><span><b>Public + private</b></span></div><div class="c3"><span><b>Government</b></span></div>
    <div class="lab">{ic('i-gov')}Government role</div>
    <div class="c1"><span><b>Little</b>: no interference</span></div><div class="c2"><span><b>Plans</b> &amp; regulates</span></div><div class="c3"><span><b>Total</b>: decides all</span></div>
    <div class="lab">{ic('i-tag')}Price mechanism</div>
    <div class="c1"><span><b>Free</b> market prices</span></div><div class="c2"><span><b>Market</b> + planning</span></div><div class="c3"><span><b>Fixed</b> by the state</span></div>
    <div class="lab">{ic('i-motive')}Motive</div>
    <div class="c1"><span><b>Profit</b></span></div><div class="c2"><span><b>Profit + social interest</b></span></div><div class="c3"><span><b>Social welfare</b></span></div>
    <div class="lab">{ic('i-up')}Advantages</div>
    <div class="c1"><ul class="adv"><li>Equal opportunity for all</li><li>Innovation &amp; high growth</li></ul></div>
    <div class="c2"><ul class="adv"><li>Best of both systems</li><li>Efficient allocation</li></ul></div>
    <div class="c3"><ul class="adv"><li>Efficient use; stability</li><li>Max welfare; no monopoly</li></ul></div>
    <div class="lab">{ic('i-down')}Disadvantages</div>
    <div class="c1"><ul class="dis"><li>Rich richer, poor poorer</li><li>No welfare &rarr; poverty</li></ul></div>
    <div class="c2"><ul class="dis"><li>Sectors may not cooperate</li><li>Inefficient public sector</li></ul></div>
    <div class="c3"><ul class="dis"><li>Bureaucracy; no freedom</li><li>Weak tech; no competition</li></ul></div>
  </div>
</section>

<section class="box oman">
  <svg viewBox="0 -8.5 80 63" style="grid-row:1 / 3;align-self:center;width:66mm;height:52mm;overflow:visible">{OMAN_ART}</svg>
  <div class="top">{plate(6, MXD)}<h2>Oman&rsquo;s kitchen: a mixed economy</h2><span class="src" style="margin-left:auto">(Vision 2040, 2019; Royal Decrees)</span></div>
  <div>
    <h4 style="color:{CMD}">{ic('i-gov')}Government sector</h4>
    <div class="it">{ic('i-compass')}<span>Plans the economy: <b>Oman Vision 2040</b></span></div>
    <div class="it">{ic('i-key')}<span>Owns state firms: <b>Oman Investment Authority</b></span></div>
    <div class="it">{ic('i-shield')}<span>Protects consumers &amp; workers by law</span></div>
  </div>
  <div>
    <h4 style="color:{MKD}">{ic('i-tag')}Private sector</h4>
    <div class="it">{ic('i-branch')}<span>Leads diversification beyond oil</span></div>
    <div class="it">{ic('i-bridge')}<span>Partners the state in <b>PPP</b> projects</span></div>
    <div class="it">{ic('i-how')}<span>Runs firms sold by <b>privatisation</b></span></div>
  </div>
</section>

<div class="concl">{use('i-up', 0, 0) if False else plate('!', MKD)}<b>Chef&rsquo;s note:</b><span style="white-space:nowrap">The mixed economy blends market freedom with social welfare: Oman&rsquo;s recipe.</span></div>

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
</div>
<script>document.fonts.ready.then(()=>{{document.body.dataset.ready='1'}});</script>
</body></html>'''
(HERE / 'poster.html').write_text(HTML)
print('ok')
