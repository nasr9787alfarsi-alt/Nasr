#!/usr/bin/env python3
"""Generates ECONOLAND poster (A2 portrait 420x594 mm) as HTML with inline SVG art."""
import math, random, pathlib
random.seed(7)
OUT = pathlib.Path(__file__).with_name('poster.html')

INK = '#1C2433'
C = dict(cream='#FFF8EC', coral='#E5674A', coralD='#B9472F', mustard='#F2B33D', mustD='#C98E1E',
         jade='#2F9C83', jadeD='#1F7563', indigo='#3B4E92', indigoD='#2A386B', steel='#9AAAD0',
         sand='#EFD9AE', sandD='#D6B57A', grass='#8CC084', grassD='#5E9B66', sky='#BFE3EA',
         skin1='#E8B48C', skin2='#C98B5E', skin3='#F1C9A5', hair='#2B2230')

def gear(r1, r2, n):
    pts = []
    for i in range(n*4):
        a = i/(n*4)*2*math.pi
        r = r2 if (i % 4) in (1, 2) else r1
        pts.append((r*math.cos(a), r*math.sin(a)))
    return 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in pts) + 'Z'

SW = 'stroke="%s" stroke-width=".45" stroke-linejoin="round" stroke-linecap="round"' % INK

# ------------------------------------------------------------------ symbol library
DEFS = f'''
<linearGradient id="gSea" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#3C93A0"/><stop offset=".25" stop-color="#21677A"/><stop offset="1" stop-color="#123846"/></linearGradient>
<linearGradient id="gSky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#FBE3C4"/><stop offset="1" stop-color="#F6CFA6"/></linearGradient>
<linearGradient id="gRock" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#2B6E7C"/><stop offset="1" stop-color="#21677A" stop-opacity="0"/></linearGradient>
<linearGradient id="gTitle" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{C['coral']}"/><stop offset=".5" stop-color="{C['jade']}"/><stop offset="1" stop-color="{C['indigo']}"/></linearGradient>

<g id="person">
  <path d="M-3.3 0 V-5.3 Q-3.3 -8.5 0 -8.5 Q3.3 -8.5 3.3 -5.3 V0 Z" style="fill:var(--shirt,{C['coral']})" {SW}/>
  <circle cx="0" cy="-10.9" r="2.45" style="fill:var(--skin,{C['skin1']})" {SW}/>
  <path d="M-2.45 -11.2 Q-2.5 -13.7 0 -13.65 Q2.6 -13.7 2.45 -11 Q0.6 -12.4 -2.45 -11.2Z" style="fill:var(--hair,{C['hair']})"/>
  <circle cx="-.85" cy="-10.6" r=".28" fill="{INK}"/><circle cx=".85" cy="-10.6" r=".28" fill="{INK}"/>
</g>
<g id="hardhat"><path d="M-2.9 -12.2 Q-2.9 -15.2 0 -15.2 Q2.9 -15.2 2.9 -12.2 Z" fill="{C['mustard']}" {SW}/><rect x="-3.5" y="-12.6" width="7" height="1" rx=".4" fill="{C['mustard']}" {SW}/></g>
<g id="bag"><rect x="2.4" y="-5.6" width="3.6" height="4" rx=".6" fill="{C['mustard']}" {SW}/><path d="M3.3 -5.6 Q4.2 -7.4 5.1 -5.6" fill="none" {SW}/></g>

<g id="house">
  <rect x="-7" y="-10" width="14" height="10" style="fill:var(--wall,#FFF1DC)" {SW}/>
  <path d="M-8.8 -9.6 L0 -17 L8.8 -9.6Z" style="fill:var(--roof,{C['coral']})" {SW}/>
  <rect x="1.2" y="-6" width="3.6" height="6" fill="{C['coralD']}" {SW}/>
  <rect x="-5" y="-7" width="4.2" height="3.6" fill="{C['sky']}" {SW}/>
  <rect x="3.4" y="-16" width="2.2" height="4" fill="#B9A08A" {SW}/>
</g>
<g id="shop">
  <rect x="-10" y="-13" width="20" height="13" fill="#FFF1DC" {SW}/>
  <rect x="-7.6" y="-8.6" width="7.4" height="5.4" fill="{C['sky']}" {SW}/>
  <rect x="2" y="-7.4" width="5" height="7.4" style="fill:var(--awn,{C['coral']})" {SW}/>
  <rect x="-11" y="-17.6" width="22" height="4" fill="#FFFFFF" {SW}/>
  <rect x="-7.33" y="-17.6" width="3.67" height="4" style="fill:var(--awn,{C['coral']})"/>
  <rect x="0" y="-17.6" width="3.67" height="4" style="fill:var(--awn,{C['coral']})"/>
  <rect x="7.33" y="-17.6" width="3.67" height="4" style="fill:var(--awn,{C['coral']})"/>
  <path d="M-11 -13.6 a1.833 1.6 0 0 0 3.667 0 a1.833 1.6 0 0 0 3.667 0 a1.833 1.6 0 0 0 3.667 0 a1.833 1.6 0 0 0 3.667 0 a1.833 1.6 0 0 0 3.667 0 a1.833 1.6 0 0 0 3.667 0" style="fill:var(--awn,{C['coral']})" {SW}/>
  <rect x="-11" y="-17.6" width="22" height="4" fill="none" {SW}/>
  <rect x="-6" y="-21.6" width="12" height="4" rx="1" fill="{INK}"/>
</g>
<g id="tag"><path d="M0 0 L5.2 0 L7.4 2 L5.2 4 L0 4Z" fill="{C['mustard']}" {SW}/><circle cx="5.3" cy="2" r=".55" fill="#fff" {SW}/></g>
<g id="factory">
  <rect x="7" y="-19" width="3.6" height="19" style="fill:var(--fac,{C['steel']})" {SW}/>
  <rect x="7" y="-19" width="3.6" height="2" fill="{C['indigoD']}"/>
  <path d="M-12 0 V-8 L-6 -12.5 V-8 L0 -12.5 V-8 L6 -12.5 V-8 L12 -12.5 V0Z" style="fill:var(--fac,{C['steel']})" {SW}/>
  <rect x="-9.5" y="-5.6" width="3" height="2.6" fill="#E9EEF8" {SW}/><rect x="-3.5" y="-5.6" width="3" height="2.6" fill="#E9EEF8" {SW}/>
  <rect x="2.5" y="-5.6" width="3" height="2.6" fill="#E9EEF8" {SW}/>
  <rect x="7.6" y="-5" width="3.2" height="5" fill="{C['indigoD']}" {SW}/>
</g>
<g id="smoke"><circle cx="0" cy="0" r="2.2" fill="#E7E3EA" {SW}/><circle cx="2.8" cy="-2.6" r="2.8" fill="#EFECF1" {SW}/><circle cx="6.4" cy="-4.4" r="2.2" fill="#F4F2F5" {SW}/></g>
<g id="gov">
  <rect x="-12" y="-2.2" width="24" height="2.2" fill="#E9DDC4" {SW}/>
  <rect x="-10.5" y="-12" width="21" height="9.8" style="fill:var(--gwall,#F7EEDC)" {SW}/>
  <rect x="-8.6" y="-11.5" width="2.2" height="9.3" fill="#fff" {SW}/><rect x="-3.6" y="-11.5" width="2.2" height="9.3" fill="#fff" {SW}/>
  <rect x="1.4" y="-11.5" width="2.2" height="9.3" fill="#fff" {SW}/><rect x="6.4" y="-11.5" width="2.2" height="9.3" fill="#fff" {SW}/>
  <path d="M-12 -12 L0 -18.5 L12 -12Z" style="fill:var(--groof,{C['indigo']})" {SW}/>
  <circle cx="0" cy="-14.4" r="1.4" fill="{C['mustard']}" {SW}/>
</g>
<g id="hospital">
  <rect x="-9" y="-16" width="18" height="16" fill="#FFFFFF" {SW}/>
  <rect x="-9" y="-16" width="18" height="3" fill="{C['jade']}" {SW}/>
  <rect x="-2.6" y="-11.4" width="5.2" height="5.2" rx=".8" fill="{C['coral']}"/>
  <rect x="-.75" y="-10.6" width="1.5" height="3.6" fill="#fff"/><rect x="-1.8" y="-9.55" width="3.6" height="1.5" fill="#fff"/>
  <rect x="-2" y="-4.4" width="4" height="4.4" fill="{C['sky']}" {SW}/>
  <rect x="-7.4" y="-4.4" width="3" height="2.6" fill="{C['sky']}" {SW}/><rect x="4.4" y="-4.4" width="3" height="2.6" fill="{C['sky']}" {SW}/>
</g>
<g id="office">
  <rect x="-7" y="-30" width="14" height="30" fill="#CFE6EA" {SW}/>
  <path d="M-7 -30 L7 -30 L7 -27 L-7 -27Z" fill="{C['coral']}" {SW}/>
  {''.join(f'<rect x="{-5+c*3.6:.1f}" y="{-25+r*4.2:.1f}" width="2.6" height="2.8" fill="#FFFFFF" {SW}/>' for r in range(5) for c in range(3))}
</g>
<g id="tower">
  <rect x="-6.5" y="-36" width="13" height="36" fill="{C['indigo']}" {SW}/>
  <rect x="-9" y="-43" width="18" height="8" rx="1.2" fill="{C['indigoD']}" {SW}/>
  {''.join(f'<rect x="{-7+c*3.5:.1f}" y="-41" width="2.4" height="4" fill="#F4D67A"/>' for c in range(5))}
  <path d="M0 -43 V-50" {SW}/><circle cx="0" cy="-50.8" r="1.2" fill="{C['coral']}" {SW}/>
  {''.join(f'<rect x="{-4.6+c*3.6:.1f}" y="{-32+r*5.4:.1f}" width="2.2" height="3" fill="#C8D3EE"/>' for r in range(5) for c in range(3))}
  <rect x="-2.4" y="-5" width="4.8" height="5" fill="{C['indigoD']}" {SW}/>
</g>
<g id="tree"><rect x="-.9" y="-6" width="1.8" height="6" fill="#8B5E3C" {SW}/><circle cx="0" cy="-9" r="4.6" fill="{C['grass']}" {SW}/><circle cx="-1.4" cy="-10.4" r="1.4" fill="#A9D29B"/></g>
<g id="palm">
  <path d="M0 0 Q-.6 -8 1.4 -15" fill="none" stroke="#8B5E3C" stroke-width="1.6" stroke-linecap="round"/>
  <path d="M1.4 -15 Q-4 -18 -8 -14 Q-3.6 -16 1.4 -15Z M1.4 -15 Q6.4 -18.6 10 -14 Q5.6 -16.4 1.4 -15Z M1.4 -15 Q-2 -21 -6 -21 Q-1 -19.4 1.4 -15Z M1.4 -15 Q4.4 -21.4 8.4 -20.4 Q3.6 -19.6 1.4 -15Z" fill="{C['grassD']}" {SW}/>
</g>
<g id="podium">
  <rect x="-11" y="-6" width="7" height="6" fill="{C['steel']}" {SW}/><rect x="-4" y="-10" width="8" height="10" fill="{C['mustard']}" {SW}/>
  <rect x="4" y="-4.4" width="7" height="4.4" fill="{C['coral']}" {SW}/>
  <text x="-7.5" y="-1.6" font-size="3.6" font-weight="800" text-anchor="middle" fill="{INK}">2</text>
  <text x="0" y="-4" font-size="4.2" font-weight="800" text-anchor="middle" fill="{INK}">1</text>
  <text x="7.5" y="-1" font-size="3.2" font-weight="800" text-anchor="middle" fill="#fff">3</text>
  <path d="M-2.6 -18 H2.6 V-16 Q2.6 -13 0 -13 Q-2.6 -13 -2.6 -16Z" fill="{C['mustard']}" {SW}/>
  <path d="M-2.6 -17 Q-4.4 -17 -4 -15.4 Q-3.6 -14.4 -2.4 -14.6 M2.6 -17 Q4.4 -17 4 -15.4 Q3.6 -14.4 2.4 -14.6" fill="none" {SW}/>
  <rect x="-.6" y="-13" width="1.2" height="1.8" fill="{C['mustD']}"/><rect x="-2" y="-11.4" width="4" height="1.4" fill="{C['mustD']}" {SW}/>
</g>
<g id="crate"><rect x="-2.4" y="-4.4" width="4.8" height="4.4" fill="#C98E5A" {SW}/><path d="M-2.4 -4.4 L2.4 0 M2.4 -4.4 L-2.4 0" stroke="#8B5E3C" stroke-width=".35"/></g>
<g id="pkg"><rect x="-2.6" y="-4.6" width="5.2" height="4.6" fill="#D9A866" {SW}/><rect x="-.5" y="-4.6" width="1" height="4.6" fill="#F4E2BF"/></g>
<g id="boat">
  <path d="M-11 -3 L11 -3 L8 2 L-8 2Z" fill="{C['coral']}" {SW}/>
  <rect x="-7" y="-7" width="5" height="4" fill="#C98E5A" {SW}/><rect x="-1.6" y="-7" width="5" height="4" fill="#D9A866" {SW}/>
  <rect x="3.6" y="-9.2" width="4.6" height="6.2" fill="#FFF8EC" {SW}/><rect x="4.6" y="-8" width="2.6" height="1.8" fill="{C['sky']}"/>
</g>
<g id="dhow">
  <path d="M-15 -4 Q-1 1 16 -6 L13 1.6 Q0 4.6 -11 1.6Z" fill="#9C6B3F" {SW}/>
  <path d="M-10 -2.6 Q0 0 12 -4.6" fill="none" stroke="#7A5030" stroke-width=".5"/>
  <path d="M0 -2 V-24" stroke="#6B4528" stroke-width=".9"/>
  <path d="M-12 -21 Q2 -30 13 -9 Q2 -9 -5 -5 Z" fill="#FFF8EC" {SW}/>
  <path d="M-12 -21 L13 -9" stroke="#C9B89A" stroke-width=".4"/>
  <path d="M0 -24 L5 -22.5 L0 -21Z" fill="{C['coral']}" {SW}/>
</g>
<g id="fort">
  <path d="M-11 0 V-20 H-12.4 V-23.4 H-10 V-21.8 H-7.6 V-23.4 H-5.2 V-21.8 H-2.8 V-23.4 H-.4 V-21.8 H2 V-23.4 H4.4 V-21.8 H6.8 V-23.4 H9.2 V-21.8 H11.6 V-23.4 H12.4 V-20 H11 V0Z" fill="#E4BF86" {SW}/>
  <path d="M-11 -14 H11" stroke="#C9A066" stroke-width=".4"/>
  <path d="M-3 0 V-6 Q0 -9.4 3 -6 V0Z" fill="#8B5E3C" {SW}/>
  <path d="M-8 -16 V-18.6 Q-6.8 -20 -5.6 -18.6 V-16Z M5.6 -16 V-18.6 Q6.8 -20 8 -18.6 V-16Z" fill="#8B5E3C"/>
  <path d="M18 0 V-14 H16.6 V-16.6 H18.8 V-15.4 H21 V-16.6 H23.2 V-15.4 H25.4 V-16.6 H27.6 V-14 H26.2 V0Z" fill="#DDB37A" {SW}/>
  <path d="M11 -10 H18 V0 H11Z" fill="#E9CB98" {SW}/>
</g>
<g id="cloud"><path d="M-14 0 Q-15 -5 -9 -5 Q-8 -11 -1 -10 Q3 -15 9 -10 Q15 -10 14 -4 Q17 -1 13 0Z" fill="#FFFBF4" {SW}/></g>
<g id="fish"><path d="M0 0 Q5 -3.4 10 0 Q5 3.4 0 0Z M10 0 L13 -2.4 L13 2.4Z" style="fill:var(--fish,{C['mustard']})" {SW}/><circle cx="2.6" cy="-.4" r=".45" fill="{INK}"/></g>
<g id="bubble"><circle r="1" fill="none" stroke="#BFE3EA" stroke-width=".35" opacity=".8"/></g>

<!-- concept icons (centered, ~10mm) -->
<g id="i-what"><path d="M-4.6 -1.4 L0 -4 L4.6 -1.4 L0 1.2Z" fill="#F4D49B" {SW}/><path d="M-4.6 -1.4 V3.6 L0 6.2 V1.2Z" fill="#D9A866" {SW}/><path d="M4.6 -1.4 V3.6 L0 6.2 V1.2Z" fill="#C98E5A" {SW}/><path d="M-2.3 -2.7 L2.3 -.1 V1.6" fill="none" stroke="#fff" stroke-width=".6"/></g>
<g id="i-how"><path d="{gear(3.4,4.7,8)}" fill="{C['steel']}" {SW}/><circle r="1.5" fill="#FFF8EC" {SW}/></g>
<g id="i-whom"><use href="#person" transform="translate(-2.4 5.2) scale(.56)" style="--shirt:{C['coral']}"/><use href="#person" transform="translate(2.6 5.6) scale(.6)" style="--shirt:{C['jade']};--skin:{C['skin2']}"/></g>
<g id="i-key"><circle cx="-2.6" cy="0" r="2.6" fill="{C['mustard']}" {SW}/><circle cx="-2.6" cy="0" r=".9" fill="#FFF8EC" {SW}/><path d="M0 -.8 H5.6 V.8 H0Z" fill="{C['mustard']}" {SW}/><path d="M3.4 .8 V2.6 H4.6 V.8 M5 .8 V2 H5.6 V.8" fill="{C['mustard']}" {SW}/></g>
<g id="i-gov"><use href="#gov" transform="translate(0 4.6) scale(.42)"/></g>
<g id="i-tag"><g transform="rotate(-20) translate(-4 -2.4) scale(1.15)"><use href="#tag"/></g></g>
<g id="i-motive"><circle r="4.6" fill="#fff" {SW}/><circle r="3" fill="{C['coral']}" {SW}/><circle r="1.4" fill="#fff" {SW}/><path d="M0 0 L5.6 -5.6" {SW}/><path d="M5.6 -5.6 L4 -5.8 M5.6 -5.6 L5.4 -4" {SW}/></g>
<g id="i-up"><circle r="4.6" fill="#3E9B5F" {SW}/><path d="M-2.2 .2 L-.6 1.9 L2.4 -1.6" fill="none" stroke="#fff" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/></g>
<g id="i-down"><circle r="4.6" fill="#C8463C" {SW}/><path d="M-1.8 -1.8 L1.8 1.8 M1.8 -1.8 L-1.8 1.8" stroke="#fff" stroke-width="1.1" stroke-linecap="round"/></g>
<g id="i-shield"><path d="M0 -5 L4.4 -3.4 V.4 Q4.4 3.8 0 5.6 Q-4.4 3.8 -4.4 .4 V-3.4Z" fill="{C['jade']}" {SW}/><path d="M-1.8 .2 L-.4 1.6 L2 -1.2" fill="none" stroke="#fff" stroke-width=".9" stroke-linecap="round"/></g>
<g id="i-hat"><path d="M-4.6 1.4 Q-4.6 -4.4 0 -4.4 Q4.6 -4.4 4.6 1.4Z" fill="{C['mustard']}" {SW}/><rect x="-5.6" y="1" width="11.2" height="1.8" rx=".7" fill="{C['mustard']}" {SW}/><path d="M0 -4.4 V1" stroke="{C['mustD']}" stroke-width=".7"/></g>
<g id="i-plan"><rect x="-4" y="-5" width="8" height="10.4" rx="1" fill="#fff" {SW}/><rect x="-2" y="-6" width="4" height="2" rx=".6" fill="{C['steel']}" {SW}/><path d="M-2.4 -1.6 H2.4 M-2.4 .8 H2.4 M-2.4 3.2 H1" stroke="{INK}" stroke-width=".45"/></g>
<g id="i-wheat"><path d="M0 5 V-4" stroke="{C['mustD']}" stroke-width=".7"/>{''.join(f'<ellipse cx="{s*1.3:.1f}" cy="{y}" rx="1.1" ry="1.9" transform="rotate({s*-28} {s*1.3:.1f} {y})" fill="{C["mustard"]}" {SW}/>' for y in (-3.2,-.4,2.2) for s in (-1,1))}<ellipse cx="0" cy="-5" rx="1" ry="1.8" fill="{C['mustard']}" {SW}/></g>
<g id="i-bulb"><path d="M-3.4 -1.2 A3.8 3.8 0 1 1 3.4 -1.2 Q2 1 2 2.6 H-2 Q-2 1 -3.4 -1.2Z" fill="#F7D774" {SW}/><rect x="-2" y="2.6" width="4" height="2.2" rx=".5" fill="{C['steel']}" {SW}/></g>
<g id="i-compass"><circle r="4.8" fill="#FFF8EC" {SW}/><path d="M0 -3.8 L1.1 0 L0 3.8 L-1.1 0Z" fill="{C['coral']}" {SW}/><circle r=".7" fill="{INK}"/></g>
<g id="i-branch"><path d="M-4.4 4 V0 Q-4.4 -2.2 -2 -2.2 H4.4 M-4.4 0 Q-4.4 -4.6 0 -4.6 H4.4 M-4.4 2.2 H4.4" fill="none" stroke="{C['coral']}" stroke-width="1.1" stroke-linecap="round"/><path d="M3.2 -5.8 L4.8 -4.6 L3.2 -3.4 M3.2 -3.4 L4.8 -2.2 L3.2 -1 M3.2 1 L4.8 2.2 L3.2 3.4" fill="none" stroke="{C['coral']}" stroke-width=".8" stroke-linecap="round" stroke-linejoin="round"/></g>
<g id="i-bridge"><path d="M-5.4 3 V-.6 Q0 -5.6 5.4 -.6 V3" fill="none" stroke="{C['jadeD']}" stroke-width="1.1"/><path d="M-5.6 1 H5.6" stroke="{INK}" stroke-width=".9"/><path d="M-2.6 1 V-2.4 M0 1 V-3.2 M2.6 1 V-2.4" stroke="{C['jadeD']}" stroke-width=".5"/></g>
'''

# ------------------------------------------------------------------ helpers
def use(i, x, y, s=1.0, style='', rot=0):
    st = f' style="{style}"' if style else ''
    r = f' rotate({rot})' if rot else ''
    return f'<use href="#{i}" transform="translate({x:.2f} {y:.2f}){r} scale({s})"{st}/>'

def pill(x, y, text, size=6.0, color=INK, fill='#FFFFFF', anchor='middle', w=None, icon=None):
    w = w or len(text)*size*0.47 + 5 + (7 if icon else 0)
    x0 = x - w/2 if anchor == 'middle' else x
    ico = use(icon, x0+4.6, y, .62) if icon else ''
    tx = x0 + w/2 + (3.3 if icon else 0)
    return (f'<rect x="{x0:.1f}" y="{y-size*.72:.1f}" width="{w:.1f}" height="{size*1.44:.1f}" rx="{size*.72:.1f}" fill="{fill}" {SW}/>'
            f'{ico}<text x="{tx:.1f}" y="{y+size*.36:.1f}" font-size="{size}" font-weight="700" text-anchor="middle" fill="{color}" class="lbl">{text}</text>')

def leader(x1, y1, x2, y2):
    return f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{INK}" stroke-width=".35" stroke-dasharray="1 .8"/>'

def island(cx, w, top, water, accent):
    l, r = cx-w/2, cx+w/2
    land = (f'<path d="M{l} {water} C{l+5} {top+3} {l+12} {top} {l+22} {top} L{r-22} {top} C{r-12} {top} {r-5} {top+3} {r} {water}Z" fill="{C["sand"]}" {SW}/>')
    grass = (f'<path d="M{l+9} {top+2.6} C{l+13} {top-.2} {l+17} {top-.6} {l+24} {top-.6} L{r-24} {top-.6} C{r-17} {top-.6} {r-13} {top-.2} {r-9} {top+2.6} Q{cx} {top+4.6} {l+9} {top+2.6}Z" fill="{C["grass"]}" {SW}/>')
    under = (f'<path d="M{l+2} {water} C{l+14} {water+10} {cx-24} {water+17} {cx} {water+19} C{cx+24} {water+17} {r-14} {water+10} {r-2} {water}Z" fill="url(#gRock)"/>')
    pebbles = ''.join(f'<ellipse cx="{l+16+i*(w-32)/5:.1f}" cy="{top+6.4+(i%2)*1.8:.1f}" rx="1.4" ry=".7" fill="{C["sandD"]}"/>' for i in range(6))
    return under + land + grass + pebbles

def waves(y, x0, x1, step=9, amp=1.3, color='#FFFFFF', op=.55, sw=.5):
    d = f'M{x0} {y}'
    x = x0
    while x < x1:
        d += f' q{step/4} {-amp} {step/2} 0 q{step/4} {amp} {step/2} 0'
        x += step
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="{sw}" stroke-linecap="round"/>'

# ------------------------------------------------------------------ ISLANDS SCENE (full bleed 420 x 104, page y=160)
SCENE_Y = 140
WATER = 82           # waterline inside scene -> page 222
TOP = 69
s = []
# distant sea band
s.append(f'<rect x="0" y="{WATER}" width="420" height="{96-WATER}" fill="#3C93A0"/>')
for i, yy in enumerate([WATER+2.5, WATER+6.5, WATER+11, WATER+16]):
    s.append(waves(yy, -4+(i % 2)*4.5, 424, step=11, amp=1.1, op=.35 - i*.06))
# --- Market island
MX, MID, CX = 72, 210, 348
s.append(island(MX, 132, TOP, WATER, C['coral']))
s.append(island(MID, 132, TOP, WATER, C['jade']))
s.append(island(CX, 132, TOP, WATER, C['indigo']))

g = TOP + 1.4   # ground line on islands
# Market: private houses + fence
s.append(use('tree', MX-56, g, .9))
s.append(use('house', MX-44, g, 1.0, f'--roof:{C["coral"]}'))
s.append(use('house', MX-28, g, .86, f'--roof:{C["mustard"]};--wall:#FFE9D6'))
s.append(''.join(f'<rect x="{MX-54+i*2.6:.1f}" y="{g-3.2}" width="1.1" height="3.2" fill="#fff" {SW}/>' for i in range(14) if not (5 <= i <= 6)))
s.append(f'<path d="M{MX-54} {g-2.2} H{MX-18}" {SW}/>')
s.append(use('person', MX-36.5, g, .78, f'--shirt:{C["jade"]};--skin:{C["skin2"]}'))
# shops (freedom of choice) with varied awnings
s.append(use('shop', MX-6, g, .95, f'--awn:{C["coral"]}'))
s.append(use('shop', MX+16, g, .95, f'--awn:{C["jade"]}'))
s.append(use('tag', MX-14, g-13.6, .9))
s.append(use('tag', MX+9, g-13.6, .9))
s.append(f'<text x="{MX-6}" y="{g-18.6}" font-size="2.6" font-weight="800" text-anchor="middle" fill="#fff">BAZAAR</text>')
s.append(f'<text x="{MX+16}" y="{g-18.6}" font-size="2.6" font-weight="800" text-anchor="middle" fill="#fff">SHOP</text>')
s.append(use('person', MX+5, g, .9, f'--shirt:{C["indigo"]};--skin:{C["skin3"]}'))
s.append(use('bag', MX+5, g, .9))
s.append(use('person', MX-17.5, g, .82, f'--shirt:{C["mustard"]}'))
s.append(use('bag', MX-17.5, g, .82))
# competition podium
s.append(use('podium', MX+42, g, 1.0))
s.append(use('person', MX+42, g-10, .62, f'--shirt:{C["coral"]}'))
# tiny government (limited)
s.append(use('gov', MX+57, g, .38))
s.append(f'<circle cx="{MX+57}" cy="{g-3.8}" r="5.8" fill="none" stroke="{C["indigo"]}" stroke-width=".45" stroke-dasharray="1.1 .8"/>')
# labels
s.append(pill(MX-38, 35, 'Private property', 6.2, icon='i-key'))
s.append(pill(MX-34, 77.2, 'Profit motive', 5.2, color=C['coralD'], icon='i-motive'))
s.append(leader(MX-38, 39.6, MX-38, 49))
s.append(pill(MX+2, 22, 'Freedom of choice', 6.2, icon='i-what'))
s.append(leader(MX+2, 26.6, MX+2, 47))
s.append(pill(MX+42, 35, 'Competition', 6.2))
s.append(leader(MX+42, 39.6, MX+42, 51))
s.append(pill(MX+42, 46.5, '', 0.1, fill='none') if False else '')
s.append(pill(MX+32, 77.2, 'Limited government', 5.2, color=C['indigoD'], icon='i-gov'))

# Mixed island: public (left) + private (right) + plan + rights
s.append(use('palm', MID-60, g, .9))
s.append(use('gov', MID-43, g, 1.05))
s.append(use('hospital', MID-22, g, 1.0))
s.append(use('office', MID+44, g, .92))
s.append(use('shop', MID+26, g, .92, f'--awn:{C["mustard"]}'))
s.append(use('palm', MID+59, g, .85))
# plan flag in middle
s.append(f'<path d="M{MID} {g} V{g-30}" stroke="{INK}" stroke-width=".7"/>')
s.append(f'<path d="M{MID} {g-30} H{MID+11} L{MID+8.6} {g-26} L{MID+11} {g-22} H{MID}Z" fill="{C["jade"]}" {SW}/>')
s.append(f'<text x="{MID+4.6}" y="{g-24.6}" font-size="2.9" font-weight="800" text-anchor="middle" fill="#fff">PLAN</text>')
# handshake: two people
s.append(use('person', MID-5.2, g, .9, f'--shirt:{C["indigo"]}'))
s.append(use('person', MID+5.2, g, .9, f'--shirt:{C["coral"]};--skin:{C["skin2"]}'))
s.append(f'<path d="M{MID-2.4} {g-4.6} Q{MID} {g-6.2} {MID+2.4} {g-4.6}" fill="none" stroke="{INK}" stroke-width=".9" stroke-linecap="round"/>')
s.append(f'<circle cx="{MID}" cy="{g-5.4}" r="1.1" fill="{C["skin1"]}" {SW}/>')
s.append(pill(MID-36, 35, 'Public sector', 6.2, color=C['indigoD'], icon='i-gov'))
s.append(leader(MID-38, 39.6, MID-38, 50))
s.append(pill(MID+36, 35, 'Private sector', 6.2, color=C['coralD'], icon='i-tag'))
s.append(leader(MID+40, 39.6, MID+42, 41))
s.append(pill(MID, 22, 'Economic planning', 6.2, color=C['jadeD'], icon='i-plan'))
s.append(leader(MID, 26.6, MID, 40))
s.append(pill(MID-28, 77.2, 'Consumer rights', 5.2, color=C['jadeD'], icon='i-shield'))
s.append(pill(MID+28, 77.2, 'Labour rights', 5.2, color=C['jadeD'], icon='i-hat'))

# Command island: tower + identical factories + queue + fixed price
s.append(use('factory', CX-44, g, .95))
s.append(use('smoke', CX-34, g-21, .7))
s.append(use('factory', CX+38, g, .95))
s.append(use('smoke', CX+48, g-21, .7))
s.append(use('tower', CX, g, 1.0))
# plan board on tower
s.append(f'<rect x="{CX-22}" y="{g-25}" width="13" height="9" rx="1" fill="#FFF8EC" {SW}/>')
s.append(f'<text x="{CX-15.5}" y="{g-19.6}" font-size="3.4" font-weight="800" text-anchor="middle" fill="{C["indigoD"]}">PLAN</text>')
s.append(f'<path d="M{CX-9} {g-20.5} H{CX-6.5}" {SW}/>')
# conveyor with identical boxes
s.append(f'<rect x="{CX-31}" y="{g-3.2}" width="22" height="2.4" rx="1.2" fill="{C["steel"]}" {SW}/>')
s.append(''.join(use('pkg', CX-27+i*6.2, g-3.2, .8) for i in range(3)))
# identical citizens in a queue (with hard hats = jobs for all)
for i in range(4):
    s.append(use('person', CX+12+i*6.2, g, .74, f'--shirt:{C["steel"]};--skin:{C["skin1"] if i%2 else C["skin2"]}'))
    s.append(use('hardhat', CX+12+i*6.2, g, .74))
# fixed price sign
s.append(f'<path d="M{CX+59} {g} V{g-12}" stroke="{INK}" stroke-width=".7"/>')
s.append(f'<rect x="{CX+51}" y="{g-21}" width="16" height="10" rx="1" fill="#FFF8EC" {SW}/>')
s.append(f'<text x="{CX+59}" y="{g-16.8}" font-size="2.8" font-weight="800" text-anchor="middle" fill="{C["indigoD"]}">PRICE</text>')
s.append(f'<text x="{CX+59}" y="{g-12.9}" font-size="2.8" font-weight="800" text-anchor="middle" fill="{C["coral"]}">FIXED</text>')
s.append(pill(CX+22, 22, 'Central authority', 6.2, color=C['indigoD'], icon='i-gov'))
s.append(leader(CX+6, 26.6, CX+2.5, 30))
s.append(pill(CX-36, 35, 'State-owned firms', 6.2, color=C['indigoD'], icon='i-key'))
s.append(leader(CX-44, 39.6, CX-44, 56))
s.append(pill(CX+44, 35, 'Fixed prices', 6.2, color=C['indigoD'], icon='i-tag'))
s.append(leader(CX+57, 39.6, CX+59, 48.4))
s.append(pill(CX+24, 77.2, 'Jobs for all', 5.2, color=C['indigoD'], icon='i-hat'))

# boats carrying resources between islands
s.append(use('dhow', 140, WATER+8.4, .62))
s.append(use('boat', 279, WATER+3.4, .9, rot=0))

# island name banners (map labels)
def banner(cx, text, sub, col):
    w = len(text)*4.3 + 16
    return (f'<path d="M{cx-w/2-5} {-.5} L{cx-w/2} {4.5} L{cx-w/2-5} {9.5} H{cx-w/2+3}Z" fill="{col}" opacity=".0"/>')
for cx, name, col in [(MX, 'Market Island', C['coralD']), (MID, 'Mixed Island', C['jadeD']), (CX, 'Command Island', C['indigoD'])]:
    s.insert(0, f'<text x="{cx}" y="9" font-family="Fraunces" font-weight="900" font-size="10.4" text-anchor="middle" fill="{col}" stroke="#FBE3C4" stroke-width="1.6" paint-order="stroke">{name}</text>')
SCENE = '\n'.join(s)

# ------------------------------------------------------------------ MOUNTAIN (intro centre, 118 x 92)
m = []
m.append('<ellipse cx="59" cy="84" rx="54" ry="5.5" fill="#BFE3EA" stroke="#1C2433" stroke-width=".45"/>')
m.append(waves(84, 10, 108, step=8, amp=.9, color='#3C93A0', op=.6, sw=.45))
m.append(f'<path d="M12 82 L40 36 L50 48 L62 24 L80 52 L88 44 L106 82Z" fill="#9C8A78" {SW}/>')
m.append(f'<path d="M62 24 L70 37 L66 35 L62 40 L58 35 L54 37Z" fill="#FFF8EC" {SW}/>')
m.append(f'<path d="M40 36 L45 44 L41 43 L37 45 L35 44Z" fill="#FFF8EC" {SW}/>')
m.append(f'<path d="M62 24 L80 52 L88 44 L106 82 L70 82 Q74 60 62 40Z" fill="#000" opacity=".10"/>')
m.append(f'<path d="M14 82 Q30 74 46 78 Q60 82 74 76 Q90 72 104 82Z" fill="{C["grass"]}" {SW}/>')
m.append(use('tree', 28, 80, .8) + use('tree', 92, 80, .7))
# factor badges
for (x, y, ic, lab) in [(20, 30, 'i-wheat', 'Land'), (59, 8, 'i-hat', 'Labour'), (98, 30, 'i-how', 'Capital')]:
    m.append(f'<circle cx="{x}" cy="{y}" r="7.4" fill="#FFF8EC" {SW}/>' + use(ic, x, y, 1.05))
    m.append(f'<text x="{x}" y="{y+13.4}" font-size="5.6" font-weight="700" text-anchor="middle" fill="{INK}" class="lbl">{lab}</text>')
m.append(f'<rect x="31" y="58" width="56" height="10.6" rx="5.3" fill="{C["coral"]}" {SW}/>')
m.append(f'<text x="59" y="65.4" font-size="6" font-weight="800" text-anchor="middle" fill="#fff" letter-spacing=".2" class="lbl">SCARCE RESOURCES</text>')
MOUNTAIN = '\n'.join(m)

# ------------------------------------------------------------------ SEA BACKGROUND DECOR (page coords)
d = []
# light rays
for x, wv in [(40, 30), (150, 22), (260, 34), (360, 24)]:
    d.append(f'<path d="M{x} 222 L{x+wv} 222 L{x+wv+60} 545 L{x+30} 545Z" fill="#FFFFFF" opacity=".035"/>')
# bubbles
for _ in range(38):
    x = random.uniform(6, 414); y = random.uniform(236, 540); r = random.uniform(.5, 1.6)
    d.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="none" stroke="#BFE3EA" stroke-opacity=".45" stroke-width=".3"/>')
# anchor ropes from islands down to cards
for x in (72, 210, 348):
    d.append(f'<path d="M{x} 234 V238" stroke="#E9D6B0" stroke-width=".8" stroke-dasharray="1.4 1"/>')
# seabed
d.append(f'<path d="M0 551 Q40 543 90 548 T190 547 T300 545 T420 547 V594 H0Z" fill="{C["sand"]}" {SW}/>')
d.append(f'<path d="M0 556 Q60 551 120 555 T260 553 T420 555" fill="none" stroke="{C["sandD"]}" stroke-width=".5"/>')
# seaweed & corals at edges
def weed(x, h, col):
    return f'<path d="M{x} 551 q-3 -{h/3} 0 -{h/2} t0 -{h/2}" fill="none" stroke="{col}" stroke-width="1.6" stroke-linecap="round"/>'
for x, h in [(6, 22), (10, 16), (410, 20), (415, 14)]:
    d.append(weed(x, h, '#3E9B6B'))
SEA = '\n'.join(d)

# ------------------------------------------------------------------ flow charts per system (inside cards, 114 x 30)
def node(x, y, ic, lab, col):
    return (f'<circle cx="{x}" cy="{y}" r="7.6" fill="#fff" stroke="{col}" stroke-width=".8"/>' + use(ic, x, y, 1.0) +
            f'<text x="{x}" y="{y+13.6}" font-size="5.6" font-weight="700" text-anchor="middle" fill="{INK}" class="lbl">{lab}</text>')
def arrow(x1, x2, y, col, lab=''):
    t = f'<text x="{(x1+x2)/2}" y="{y-2.4}" font-size="4.4" text-anchor="middle" fill="{col}" font-weight="600" class="lbl">{lab}</text>' if lab else ''
    return (f'<path d="M{x1} {y} H{x2-1.6}" stroke="{col}" stroke-width=".9"/><path d="M{x2-2.6} {y-1.8} L{x2} {y} L{x2-2.6} {y+1.8}Z" fill="{col}"/>' + t)

FLOW_M = (node(15, 10, 'i-whom', 'Consumers', C['coral']) + arrow(24, 47, 10, C['coralD'], 'demand') +
          node(57, 10, 'i-tag', 'Market prices', C['coral']) + arrow(66, 89, 10, C['coralD'], 'profit') +
          node(99, 10, 'i-how', 'Producers', C['coral']) +
          f'<path d="M99 -0.6 Q99 -4.6 57 -4.6 Q15 -4.6 15 -0.6" fill="none" stroke="{C["coralD"]}" stroke-width=".7" stroke-dasharray="1.6 1"/>'
          f'<path d="M13.4 -2.4 L15 0 L16.6 -2.4Z" fill="{C["coralD"]}"/>'
          f'<rect x="38" y="-7.4" width="38" height="5.4" rx="2.7" fill="#FFF8EC"/>'
          f'<text x="57" y="-3.2" font-size="4.4" text-anchor="middle" fill="{C["coralD"]}" font-weight="600" class="lbl">variety of goods</text>')
FLOW_X = (node(12, 10, 'i-gov', 'Public', C['jade']) +
          f'<text x="32.5" y="13" font-size="10" font-weight="800" text-anchor="middle" fill="{C["jadeD"]}">+</text>' +
          node(53, 10, 'i-tag', 'Private', C['jade']) + arrow(62, 86, 10, C['jadeD'], 'together') +
          node(95, 10, 'i-what', 'Goods &amp; services', C['jade']) +
          f'<rect x="6.5" y="-7.4" width="52" height="5.4" rx="2.7" fill="{C["jade"]}"/>'
          f'<text x="32.5" y="-3.3" font-size="4.4" text-anchor="middle" fill="#fff" font-weight="700" class="lbl">guided by planning</text>')
FLOW_C = (node(15, 10, 'i-plan', 'Central plan', C['indigo']) + arrow(24, 47, 10, C['indigoD'], 'orders') +
          node(57, 10, 'i-how', 'State firms', C['indigo']) + arrow(66, 89, 10, C['indigoD'], 'allocates') +
          node(99, 10, 'i-whom', 'Citizens', C['indigo']) +
          f'<rect x="38" y="-7.4" width="38" height="5.4" rx="2.7" fill="{C["indigo"]}"/>'
          f'<text x="57" y="-3.3" font-size="4.4" text-anchor="middle" fill="#fff" font-weight="700" class="lbl">prices fixed</text>')

def flow_svg(inner):
    return f'<svg class="flow" viewBox="0 -8.6 114 34" width="114mm" height="34mm">{inner}</svg>'

def ic(i, s=1.0):  # inline icon
    return f'<svg class="ic" viewBox="-6 -6 12 12"><use href="#{i}" transform="scale({s})"/></svg>'

# ------------------------------------------------------------------ HTML
HTML = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Econoland: Economic Systems</title>
<link rel="stylesheet" href="fonts/fonts.css">
<style>
@page {{ size: 420mm 594mm; margin: 0; }}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:420mm;height:594mm}}
body{{font-family:'Bricolage Grotesque',sans-serif;font-stretch:semi-condensed;color:{INK};font-size:24pt;line-height:1.13;
  -webkit-print-color-adjust:exact;print-color-adjust:exact;
  background:linear-gradient(180deg,#FBE3C4 0mm,#F7D2AA 222mm,#3C93A0 222mm,#21677A 300mm,#163F4E 450mm,#112F3B 594mm);}}
.page{{position:relative;width:420mm;height:594mm;overflow:hidden}}
.abs{{position:absolute}}
svg text{{font-family:'Bricolage Grotesque';font-stretch:semi-condensed}}
.lbl{{letter-spacing:.05px}}
b{{font-weight:700}}
.ic{{width:9mm;height:9mm;flex:none;overflow:visible}}

/* header */
.titlewrap{{left:11mm;top:6.5mm;width:255mm}}
.chips{{display:flex;gap:3mm;margin-bottom:1.4mm}}
.chip{{font-size:22pt;font-weight:700;padding:.8mm 4mm 1.1mm;border-radius:10mm;border:.5mm solid {INK};background:#FFF8EC;line-height:1.1}}
.chip.dark{{background:{INK};color:#FFF8EC}}
.crew{{right:11mm;top:7mm;width:141mm;background:#FFF8EC;border:.6mm solid {INK};border-radius:4mm;padding:3mm 4.5mm 3mm 5mm;box-shadow:1.4mm 1.4mm 0 {INK}}}
.crew h3{{font-size:20pt;font-weight:800;letter-spacing:.12em;color:{C['coralD']};display:flex;justify-content:space-between;align-items:center;border-bottom:.45mm dashed {INK};padding-bottom:1.2mm;margin-bottom:.8mm}}
.crew h3 span{{color:{INK};opacity:.6}}
.crew .m{{display:flex;justify-content:space-between;align-items:baseline;line-height:1.28}}
.crew .m .nm{{font-weight:700}}
.crew .m .id{{font-weight:600;font-stretch:condensed;color:{C['indigoD']};letter-spacing:.03em}}

/* intro cards */
.card{{background:#FFF8EC;border:.6mm solid {INK};border-radius:5mm;box-shadow:1.4mm 1.4mm 0 rgba(28,36,51,.9)}}
.intro{{top:67mm;width:140mm;padding:3.2mm 5mm 3.4mm}}
.pinh{{display:flex;align-items:center;gap:3mm;font-weight:800;font-size:25.5pt;line-height:1.02;margin-bottom:1.6mm;white-space:nowrap}}
.pin{{width:11mm;height:11mm;border-radius:50% 50% 50% 0;transform:rotate(-45deg);background:{C['coral']};border:.5mm solid {INK};display:flex;align-items:center;justify-content:center;flex:none}}
.pin span{{transform:rotate(45deg);color:#fff;font-weight:800;font-size:22pt;font-stretch:normal}}
.src{{font-size:15pt;font-style:normal;color:#5d6475;font-weight:500}}
.qrow{{display:flex;gap:2.5mm;margin-top:2.4mm}}
.q{{flex:1;display:flex;flex-direction:row;gap:1.6mm;justify-content:center;align-items:center;white-space:nowrap;background:#fff;border:.45mm solid {INK};border-radius:3mm;padding:1.6mm 1mm 1.4mm;font-weight:800;font-size:22pt}}
.q .ic{{width:9mm;height:9mm}}

/* island names over scene */
.iname{{top:160mm;width:132mm;text-align:center;font-family:'Fraunces';font-weight:900;font-size:30pt;line-height:1;letter-spacing:-.01em}}

/* underwater cards */
.syscard{{top:238mm;width:128mm;padding:0 0 2.6mm;overflow:hidden}}
.syscard .hd{{padding:2.4mm 5mm 2.4mm;color:#fff;display:flex;justify-content:space-between;align-items:baseline;border-bottom:.6mm solid {INK}}}
.syscard .hd b{{font-family:'Fraunces';font-weight:800;font-size:28pt;font-stretch:normal}}
.syscard .hd span{{font-size:19pt;font-weight:600;opacity:.92}}
.syscard .body{{padding:2.4mm 5mm 0}}
.syscard .def{{margin:0 0 1.8mm}}
.flow{{display:block;margin:0 auto 1mm;overflow:visible}}
.ql{{display:flex;align-items:center;gap:2.4mm;line-height:1.12;margin-top:1mm}}
.ql .ic{{width:8mm;height:8mm}}
.ql .k{{font-weight:800;font-size:18pt;width:19mm;flex:none;letter-spacing:.02em}}

/* logbook table */
.log{{left:11mm;width:398mm;padding:0 0 1mm;overflow:hidden}}
.log .ttl{{display:flex;align-items:center;gap:3.5mm;padding:2.6mm 5mm;background:{INK};color:#FFF8EC}}
.log .ttl h2{{font-family:'Fraunces';font-weight:800;font-size:30pt;font-stretch:normal}}
.log .ttl .sub{{font-size:20pt;opacity:.8;margin-left:auto}}
.grid{{display:grid;grid-template-columns:78mm repeat(3,1fr)}}
.grid > div{{padding:1.3mm 3.5mm;border-top:.35mm solid #D8CCB4;display:flex;align-items:center}}
.grid .lab{{gap:2.4mm;font-weight:800;line-height:1.0;font-size:23pt}}
.grid .lab .ic{{width:9.5mm;height:9.5mm}}
.grid .h{{font-family:'Fraunces';font-weight:800;font-size:25pt;justify-content:center;border-top:none;padding:1.8mm 2mm;font-stretch:normal}}
.cm{{background:#FCE6DC}} .cx{{background:#DDF0E9}} .cc{{background:#E2E7F5}}
.cm b{{color:{C['coralD']}}} .cx b{{color:{C['jadeD']}}} .cc b{{color:{C['indigoD']}}}
.grid ul{{list-style:none}}
.grid li{{padding-left:4.6mm;position:relative;line-height:1.06}}
.grid li::before{{content:"";position:absolute;left:.4mm;top:2.7mm;width:2.2mm;height:2.2mm;border-radius:50%}}
.adv li::before{{background:#3E9B5F}} .dis li::before{{background:#C8463C}}

/* oman */
.oman{{left:11mm;width:398mm;background:#FBEBD0;display:grid;grid-template-columns:84mm 1fr 1fr;grid-template-rows:auto 1fr;column-gap:5mm;padding:3mm 5mm 3mm 3mm;overflow:hidden}}
.oman .top{{grid-column:2 / 4;display:flex;align-items:center;gap:3mm;white-space:nowrap}}
.oman h2{{font-family:'Fraunces';font-weight:900;font-size:30pt;line-height:1;font-stretch:normal;color:{C['jadeD']}}}
.oman .role h4{{font-size:25pt;font-weight:800;margin:1.4mm 0 0}}
.oman .it{{display:flex;gap:2.2mm;align-items:center;line-height:1.08;margin-top:1.1mm}}
.oman .it .ic{{width:9mm;height:9mm}}

/* footer */
.refs{{left:11mm;width:398mm;bottom:3.5mm;display:grid;grid-template-columns:40mm 1fr;column-gap:4mm;align-items:start}}
.refs h3{{font-family:'Fraunces';font-weight:900;font-size:20pt;font-stretch:normal;line-height:1}}
.refs h3 small{{display:block;font-family:'Bricolage Grotesque';font-weight:600;font-size:11pt;color:#6b5a3c;margin-top:1mm}}
.refs ul{{columns:3;column-gap:5mm;list-style:none;font-size:11.5pt;line-height:1.18}}
.refs li{{break-inside:avoid;padding-left:4mm;text-indent:-4mm;margin-bottom:.6mm}}
</style></head>
<body><div class="page">

<svg width="0" height="0" style="position:absolute"><defs>{DEFS}</defs></svg>

<!-- sky decor -->
<svg class="abs" style="left:0;top:0" width="420mm" height="250mm" viewBox="0 0 420 250">
  <circle cx="210" cy="104" r="40" fill="#F6B860" opacity=".28"/>
  <circle cx="210" cy="104" r="27" fill="#F4A94A" opacity=".35"/>
  {use('cloud', 150, 150, .5)}{use('cloud', 282, 150, .5)}{use('cloud', 20, 152, .45)}{use('cloud', 404, 146, .45)}
  <path d="M0 210 Q60 203 120 208 T240 206 T420 208 V222 H0Z" fill="#E9C9A0" opacity=".5"/>
</svg>

<!-- sea decor -->
<svg class="abs" style="left:0;top:0" width="420mm" height="594mm" viewBox="0 0 420 594">{SEA}
  {use('fish', 52, 232, .7, f'--fish:{C["mustard"]}')}{use('fish', 366, 231, .6, f'--fish:{C["coral"]}')}{use('fish', 300, 234, .45, f'--fish:{C["steel"]}')}
</svg>

<!-- islands scene -->
<svg class="abs" style="left:0;top:{SCENE_Y}mm" width="420mm" height="96mm" viewBox="0 0 420 96">{SCENE}</svg>

<!-- ===== HEADER ===== -->
<div class="abs titlewrap">
  <div class="chips"><span class="chip dark">BSEC1103 &middot; Principles of Economics</span><span class="chip">Chapter 2 &middot; Economic Systems</span></div>
  <svg width="255mm" height="37mm" viewBox="0 0 255 37" style="display:block;overflow:visible">
    <text x="1.5" y="34.4" font-family="Fraunces" font-weight="900" font-size="41" letter-spacing="-.8" fill="{INK}">ECONOLAND</text>
    <text x="0" y="33" font-family="Fraunces" font-weight="900" font-size="41" letter-spacing="-.8" fill="url(#gTitle)" stroke="{INK}" stroke-width=".55">ECONOLAND</text>
  </svg>
  <div style="font-family:'Fraunces';font-style:italic;font-weight:600;font-size:27pt;line-height:1.05;margin:.4mm 0 0 .6mm">An explorer&rsquo;s map of economic systems</div>
</div>

<div class="abs crew">
  <h3>EXPEDITION CREW <span>ID</span></h3>
  <div class="m"><span class="nm">Mais altoubi</span><span class="id">31j2573</span></div>
  <div class="m"><span class="nm">Alshima Almahrooqi</span><span class="id">21S252540139</span></div>
  <div class="m"><span class="nm">Nardeen alfarsi</span><span class="id">21J2583</span></div>
  <div class="m"><span class="nm">shatha al_umeiri</span><span class="id">21J25157</span></div>
</div>

<!-- ===== INTRO ===== -->
<div class="abs card intro" style="left:11mm">
  <div class="pinh"><div class="pin"><span>1</span></div>What is an economic system?</div>
  <p>The <b>means by which a society or government organises and distributes</b> its resources, goods and services: its <b>mode of production and distribution</b>. <span class="src">(Fernando, 2026)</span></p>
</div>

<svg class="abs" style="left:161.5mm;top:64mm" width="97mm" height="75.6mm" viewBox="0 0 118 92">{MOUNTAIN}</svg>

<div class="abs card intro" style="right:11mm">
  <div class="pinh"><div class="pin"><span>2</span></div>Why societies need one</div>
  <p>Resources are <b>scarce</b> but wants are <b>unlimited</b>, so every society must choose. Its system answers: <span class="src">(Mankiw, 2021)</span></p>
  <div class="qrow">
    <div class="q">{ic('i-what',1.05)}WHAT?</div><div class="q">{ic('i-how',1.05)}HOW?</div><div class="q" style="flex:1.5">{ic('i-whom',1.05)}FOR WHOM?</div>
  </div>
</div>


<!-- ===== UNDERWATER: HOW EACH SYSTEM WORKS ===== -->
<div class="abs card syscard" style="left:8mm">
  <div class="hd" style="background:{C['coral']}"><b>Capitalist</b><span>market &middot; free economy</span></div>
  <div class="body">
    
    {flow_svg(FLOW_M)}
    <div class="ql">{ic('i-what')}<span class="k" style="color:{C['coralD']}">WHAT</span><span>consumer demand</span></div>
    <div class="ql">{ic('i-how')}<span class="k" style="color:{C['coralD']}">HOW</span><span>firms decide, for profit</span></div>
    <div class="ql">{ic('i-whom')}<span class="k" style="color:{C['coralD']}">WHOM</span><span>buyers, by their income</span></div>
  </div>
</div>
<div class="abs card syscard" style="left:146mm">
  <div class="hd" style="background:{C['jade']}"><b>Mixed</b><span>public + private</span></div>
  <div class="body">
    
    {flow_svg(FLOW_X)}
    <div class="ql">{ic('i-what')}<span class="k" style="color:{C['jadeD']}">WHAT</span><span>demand + state plan</span></div>
    <div class="ql">{ic('i-how')}<span class="k" style="color:{C['jadeD']}">HOW</span><span>private + public sectors</span></div>
    <div class="ql">{ic('i-whom')}<span class="k" style="color:{C['jadeD']}">WHOM</span><span>market + social interest</span></div>
  </div>
</div>
<div class="abs card syscard" style="left:284mm">
  <div class="hd" style="background:{C['indigo']}"><b>Command</b><span>socialist economy</span></div>
  <div class="body">
    
    {flow_svg(FLOW_C)}
    <div class="ql">{ic('i-what')}<span class="k" style="color:{C['indigoD']}">WHAT</span><span>set by the central plan</span></div>
    <div class="ql">{ic('i-how')}<span class="k" style="color:{C['indigoD']}">HOW</span><span>organised by the state</span></div>
    <div class="ql">{ic('i-whom')}<span class="k" style="color:{C['indigoD']}">WHOM</span><span>allocated by the state</span></div>
  </div>
</div>

<!-- ===== LOGBOOK ===== -->
<div class="abs card log" id="log">
  <div class="ttl"><div class="pin" style="background:{C['mustard']}"><span style="color:{INK}">4</span></div><h2>Explorer&rsquo;s logbook: the three islands compared</h2><span class="sub">(Fernando, 2026)</span></div>
  <div class="grid">
    <div class="h" style="justify-content:flex-start;padding-left:5mm;font-family:'Bricolage Grotesque';font-weight:700;font-size:20pt;color:#6b6f7c">Feature</div>
    <div class="h cm" style="color:{C['coralD']}">Capitalist</div><div class="h cx" style="color:{C['jadeD']}">Mixed</div><div class="h cc" style="color:{C['indigoD']}">Command</div>

    <div class="lab">{ic('i-key')}Ownership</div>
    <div class="cm"><span><b>Private</b> individuals</span></div>
    <div class="cx"><span><b>Both</b>: public + private</span></div>
    <div class="cc"><span><b>Government</b> (the state)</span></div>

    <div class="lab">{ic('i-gov')}Government role</div>
    <div class="cm"><span><b>Little</b>: no interference</span></div>
    <div class="cx"><span><b>Plans</b> &amp; regulates</span></div>
    <div class="cc"><span><b>Total</b>: takes all decisions</span></div>

    <div class="lab">{ic('i-tag')}Price mechanism</div>
    <div class="cm"><span><b>Free</b>: set in the market</span></div>
    <div class="cx"><span><b>Works</b>, guided by planning</span></div>
    <div class="cc"><span><b>Fixed</b> by central authority</span></div>

    <div class="lab">{ic('i-motive')}Motive</div>
    <div class="cm"><span><b>Profit</b></span></div>
    <div class="cx"><span><b>Profit + social interest</b></span></div>
    <div class="cc"><span><b>Social welfare</b></span></div>

    <div class="lab">{ic('i-up')}Advantages</div>
    <div class="cm"><ul class="adv"><li>Equal opportunity</li><li>Innovation &amp; high growth</li></ul></div>
    <div class="cx"><ul class="adv"><li>Best of both systems</li><li>Efficient allocation (prices, profit, freedom)</li></ul></div>
    <div class="cc"><ul class="adv"><li>Efficient resource use</li><li>Stability, welfare, no monopoly</li></ul></div>

    <div class="lab">{ic('i-down')}Disadvantages</div>
    <div class="cm"><ul class="dis"><li>Inequality: rich get richer</li><li>No welfare &rarr; poverty</li></ul></div>
    <div class="cx"><ul class="dis"><li>Sectors may not cooperate</li><li>Inefficient public sector</li></ul></div>
    <div class="cc"><ul class="dis"><li>Bureaucracy; no freedom</li><li>Little tech or competition</li></ul></div>
  </div>
</div>

<!-- ===== OMAN ===== -->
<div class="abs card oman" id="oman">
  <svg viewBox="0 0 92 56" width="84mm" height="51mm" style="align-self:center;grid-row:1 / 3">
    <rect x="0" y="0" width="92" height="56" rx="4" fill="#BFE3EA"/>
    <circle cx="72" cy="14" r="8" fill="#F4A94A" opacity=".8"/>
    <path d="M0 40 H92 V52 Q92 56 88 56 H4 Q0 56 0 52Z" fill="#3C93A0"/>
    {waves(43, 2, 90, step=8, amp=.8, op=.5)}
    <path d="M4 40 Q20 30 46 31 Q62 32 74 40Z" fill="{C['sand']}" {SW}/>
    {use('fort', 30, 36, .95)}{use('palm', 12, 37, .85)}{use('palm', 66, 39, .7)}
    {use('dhow', 70, 49, .85)}
  </svg>
  <div class="top"><div class="pin" style="background:{C['jade']}"><span>5</span></div><h2>Oman: a mixed economy</h2><span>where public &amp; private sectors <b>co-exist</b></span></div>
  <div>
    <div class="role">
      <h4 style="color:{C['indigoD']}">Government roles</h4>
      <div class="it">{ic('i-compass')}<span>Plans the economy: <b>Oman Vision 2040</b></span></div>
      <div class="it">{ic('i-gov')}<span>Owns state firms: <b>Oman Investment Authority</b></span></div>
      <div class="it">{ic('i-shield')}<span>Protects consumers &amp; workers by law</span></div>
    </div>
  </div>
  <div>
    <div class="role">
      <h4 style="color:{C['coralD']}">Private sector roles</h4>
      <div class="it">{ic('i-branch')}<span>Leads diversification away from oil</span></div>
      <div class="it">{ic('i-bridge')}<span>Partners the state in <b>PPP</b> projects</span></div>
    </div>
    <p class="src" style="margin-top:1.4mm">(Oman Vision 2040 Main Committee, 2019; Royal Decree No. 66/2014, 52/2019, 61/2020, 53/2023)</p>
  </div>
</div>

<!-- ===== REFERENCES (seabed) ===== -->
<div class="abs refs">
  <h3>References<small>APA 7th ed.</small></h3>
  <ul>
    <li>Fernando, G. A. (2026). <i>Chapter 2: Economic systems</i> [PowerPoint slides]. BSEC1103 Principles of Economics, University of Technology and Applied Sciences.</li>
    <li>Mankiw, N. G. (2021). <i>Principles of economics</i> (9th ed.). Cengage Learning.</li>
    <li>Oman Vision 2040 Main Committee. (2019). <i>Oman Vision 2040: Vision document</i>. Sultanate of Oman. https://www.oman2040.om</li>
    <li>Royal Decree No. 52/2019 promulgating the Public-Private Partnership Law. (2019). <i>Official Gazette of the Sultanate of Oman</i>. https://decree.om/2019/rd20190052/</li>
    <li>Royal Decree No. 53/2023 promulgating the Labour Law. (2023). <i>Official Gazette of the Sultanate of Oman</i>.</li>
    <li>Royal Decree No. 61/2020 establishing the Oman Investment Authority. (2020). <i>Official Gazette of the Sultanate of Oman</i>. https://decree.om/2020/rd20200061/</li>
    <li>Royal Decree No. 66/2014 promulgating the Consumer Protection Law. (2014). <i>Official Gazette of the Sultanate of Oman</i>.</li>
  </ul>
</div>

</div>
<script>
// stack the lower sections: logbook under the tallest system card, oman under logbook
document.fonts.ready.then(function(){{
  const mm=v=>v/3.7795;
  const cards=[...document.querySelectorAll('.syscard')];
  const bottom=Math.max(...cards.map(c=>c.getBoundingClientRect().bottom));
  const log=document.getElementById('log'); log.style.top=(mm(bottom)+5)+'mm';
  const lb=log.getBoundingClientRect().bottom;
  const om=document.getElementById('oman'); om.style.top=(mm(lb)+5)+'mm';
  // equalise system card heights
  const h=Math.max(...cards.map(c=>c.getBoundingClientRect().height)); cards.forEach(c=>c.style.height=mm(h)+'mm');
  document.body.dataset.ready='1';
}});
</script>
</body></html>
'''
OUT.write_text(HTML)
print('written', OUT)
