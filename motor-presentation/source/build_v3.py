"""Inside the Motor - v3 builder.
No video, no GIF, no hand-authored 3D-model markup: realistic 3D renders as pictures moved by Morph, and
PowerPoint-native animations (spin, fade, motion paths) for the working principle. Images are sized to their
on-screen size and palette-compressed (libimagequant) to keep the file small enough for e-mail.
usage: python3 build_v3.py out.pptx
"""
import os, sys, io, json, math, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'v3_head.py'), encoding='utf-8').read())
sys.path.insert(0, HERE)
from PIL import Image, ImageChops
import imagequant
import native_layout2 as NL
from cfg_v3 import CFG3
exec(open(os.path.join(HERE, 'anim_native.py'), encoding='utf-8').read())
ND3 = D3
OPT = os.path.join(D3, 'opt'); os.makedirs(OPT, exist_ok=True)
DPI = 165                                       # ~1.15x a 1920-px projector (144 px/in): sharp, not wasteful

# ---------------------------------------------------------------- image optimisation
def _quant(im, out):
    q = imagequant.quantize_pil_image(im, dithering_level=1.0, max_colors=256, min_quality=78, max_quality=98)
    q.save(out, optimize=True)

def opt_png(src, width_in=None, crop=True):
    """crop transparent margins, resize to the displayed size at DPI, palette-compress. Returns path, crop fractions."""
    im = Image.open(src).convert('RGBA'); W, H = im.size; bb = (0, 0, W, H)
    if crop:
        b = im.getchannel('A').point(lambda a: 255 if a > 3 else 0).getbbox()
        if b: bb = (max(0, b[0] - 2), max(0, b[1] - 2), min(W, b[2] + 2), min(H, b[3] + 2))
    frac = (bb[0] / W, bb[1] / H, bb[2] / W, bb[3] / H)
    key = hashlib.md5(f'{src}|{os.path.getmtime(src)}|{width_in}|{crop}'.encode()).hexdigest()[:14]
    out = os.path.join(OPT, key + '.png')
    if not os.path.exists(out):
        c = im.crop(bb)
        if width_in:
            px = int(width_in * (frac[2] - frac[0]) * DPI)
            if c.width > px: c = c.resize((px, max(1, round(c.height * px / c.width))), Image.LANCZOS)
        _quant(c, out)
    return out, frac

def pic(s, name, x, y, w=None, h=None):           # optimised replacement for the renders helper
    a = ASP.get(name)
    if w is not None and h is None: h = w / a
    if h is not None and w is None: w = h * a
    path, (f0, f1, f2, f3) = opt_png(IMG(name + '.png'), w)
    return s.shapes.add_picture(path, Inches(x + f0 * w), Inches(y + f1 * h), Inches((f2 - f0) * w), Inches((f3 - f1) * h))

def photo(s, f, x, y, w, h):                       # optimised replacement: cropped + resized JPEG
    out = os.path.join(OPT, 'ph_' + f.replace('.jpg', '') + f'_{w:.2f}x{h:.2f}.jpg')
    if not os.path.exists(out):
        im = Image.open(PH(f)).convert('RGB'); iw, ih = im.size; ar = w / h
        if iw / ih > ar: nw = ih * ar; im = im.crop((int((iw - nw) / 2), 0, int((iw + nw) / 2), ih))
        else: nh = iw / ar; im = im.crop((0, int((ih - nh) / 2), iw, int((ih + nh) / 2)))
        im = im.resize((int(w * DPI), int(h * DPI)), Image.LANCZOS); im.save(out, quality=84, optimize=True, progressive=True)
    return s.shapes.add_picture(out, Inches(x), Inches(y), Inches(w), Inches(h))

# ---------------------------------------------------------------- transitions
TRANS = {}   # slide_id -> (kind, dur_ms, advance_after_ms or None)
def set_trans(s, kind='fade', dur=700, adv=None): TRANS[s.slide_id] = (kind, dur, adv)

def write_transitions():
    for s in prs.slides:
        kind, dur, adv = TRANS.get(s.slide_id, ('fade', 700, None))
        a = f' advTm="{adv}"' if adv is not None else ''
        if kind == 'morph':
            xml = ('<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
                   '<mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159">'
                   f'<p:transition xmlns:p="{P_NS}" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" spd="slow" p14:dur="{dur}"{a}><p159:morph option="byObject"/></p:transition>'
                   f'</mc:Choice><mc:Fallback><p:transition xmlns:p="{P_NS}" spd="med"{a}><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>')
        else:
            xml = f'<p:transition xmlns:p="{P_NS}" spd="med"{a}><p:fade/></p:transition>'
        el = etree.fromstring(xml); sld = s._element; cmo = sld.find(qn('p:clrMapOvr'))
        (cmo if cmo is not None else sld.find(qn('p:cSld'))).addnext(el)

# ====================================================================== 1 COVER
s = new('Cover 3', 'cover')
set_ph(s, 0, 'Inside the Motor', size=40, bold=True)
set_ph(s, 10, 'Understanding Induction vs. Synchronous Technology', size=20)
set_ph(s, 11, 'Technical Induction Session')
set_ph(s, 12, 'Engineering Fundamentals')
for idx, y in [(0, 1.85), (10, 2.75), (11, 3.85), (12, 4.22)]:
    p = ph(s, idx); p.left = Inches(2.85); p.top = Inches(y); p.width = Inches(5.0); p.height = Inches(0.9 if idx == 0 else (0.85 if idx == 10 else 0.4))
pic(s, 'ind_cut_l', 6.75, 4.05, w=3.1)
pic(s, 'syn_cut_l', 9.55, 3.15, h=4.0)

# ====================================================================== 2 WHAT DOES A MOTOR DO
s = new('Title & Subtitle Only', 'motor')
title(s, 'What does an electric motor do?', 'It turns electricity into rotation – the turning force that drives machines')
tl = Timeline()
cy0 = 3.35
c1 = shape(s.shapes, MSO_SHAPE.OVAL, 2.1, cy0, 1.75, 1.75, fill=GREEN)
bolt = shape(s.shapes, MSO_SHAPE.LIGHTNING_BOLT, 2.1, cy0, 0.85, 1.15, fill=WHITE)
mot = pic(s, 'ind_hero_l', 5.27, 2.0, w=2.8)
fan = s.shapes.add_group_shape(); ghost_circle(fan.shapes, 11.1, cy0, 0.95)
shape(fan.shapes, MSO_SHAPE.OVAL, 11.1, cy0, 1.9, 1.9, fill=None, line=STEEL_D, lw=2.25)
for a in (0, 90, 180, 270):
    x, y = polar(11.1, cy0, 0.45, a); shape(fan.shapes, MSO_SHAPE.OVAL, x, y, 0.42 if a in (90, 270) else 0.78, 0.78 if a in (90, 270) else 0.42, fill=TEAL)
shape(fan.shapes, MSO_SHAPE.OVAL, 11.1, cy0, 0.3, 0.3, fill=DARK)
ar1 = shape(s.shapes, MSO_SHAPE.RIGHT_ARROW, 3.9, cy0, 1.25, 0.42, fill=LINE)
ar2 = shape(s.shapes, MSO_SHAPE.RIGHT_ARROW, 9.25, cy0, 1.25, 0.42, fill=LINE)
d1 = shape(s.shapes, MSO_SHAPE.OVAL, 3.38, cy0, 0.2, 0.2, fill=GREEN)
d2 = shape(s.shapes, MSO_SHAPE.OVAL, 8.73, cy0, 0.2, 0.2, fill=TEAL)
caps = [(2.1, 'Electricity in', 'from the power supply', GREEN), (6.67, 'Magnetism inside', 'copper coils create a turning magnetic field', DARK), (11.1, 'Rotation out', 'the shaft turns pumps, fans, compressors…', TEAL)]
cap_sh = []
for x, h, d, c in caps:
    t1 = text(s, x - 1.6, 4.65, 3.2, 0.4, h, size=18, bold=True, color=c, align=PP_ALIGN.CENTER)
    t2 = text(s, x - 1.6, 5.08, 3.2, 0.7, d, size=13.5, color=TXT, align=PP_ALIGN.CENTER, line=1.05)
    cap_sh.append((t1, t2))
hline(s, 0.6, 6.0, 12.1)
foot = text(s, 0.6, 6.18, 12.1, 0.6, [[('Motors use about 45 % of all the electricity in the world. ', {'bold': True, 'color': DARK}), ('Most of them are induction motors; the very largest are often synchronous motors.', {})]], size=14, line=1.05)
for shp_, t in ((c1, 200), (bolt, 200), (cap_sh[0][0], 300), (cap_sh[0][1], 300), (ar1, 900), (mot, 1300), (cap_sh[1][0], 1400), (cap_sh[1][1], 1400), (ar2, 2100), (fan, 2600), (cap_sh[2][0], 2700), (cap_sh[2][1], 2700), (foot, 3600)):
    tl.fade_in(shp_, t, 500)
tl.fade_in(d1, 900, 200).path(d1, 900, 1100, 1.0 / 13.333, 0, repeat='indefinite')
tl.fade_in(d2, 2100, 200).path(d2, 2100, 1100, 1.0 / 13.333, 0, repeat='indefinite')
tl.spin(fan, 2600, 1500, repeat='indefinite')
tl.write(s)

# ====================================================================== 3 TWO FAMILIES (native speed dials)
s = new('Title & Subtitle Only', 'families')
title(s, 'Two motor families, one key difference', 'Together they drive most of the machines in an industrial plant')
pic(s, 'ind_hero_l', 0.6, 1.6, w=3.45)
pic(s, 'syn_hero_l', 9.85, 1.5, h=3.3)
tl = Timeline()
for cx, lab, sub, lag, rper in ((5.45, 'Induction', 'rotor slightly slower', 0, 4700), (7.95, 'Synchronous', 'rotor exactly in step', -14, 4000)):
    cy = 2.85; R = 0.78
    shape(s.shapes, MSO_SHAPE.OVAL, cx, cy, 2 * R, 2 * R, fill=WHITE, line=LINE, lw=1.5)
    for k in range(12):
        x, y = polar(cx, cy, R - 0.1, k * 30); shape(s.shapes, MSO_SHAPE.OVAL, x, y, 0.05, 0.05, fill=GREY)
    hf = s.shapes.add_group_shape(); ghost_circle(hf.shapes, cx, cy, R - 0.08); shape(hf.shapes, MSO_SHAPE.ROUNDED_RECTANGLE, cx, cy - (R - 0.12) / 2, 0.07, R - 0.12, fill=GREEN)
    hr = s.shapes.add_group_shape(); ghost_circle(hr.shapes, cx, cy, R - 0.08); shape(hr.shapes, MSO_SHAPE.ROUNDED_RECTANGLE, cx, cy - (R - 0.3) / 2, 0.1, R - 0.3, fill=COPPER)
    hr.rotation = lag
    shape(s.shapes, MSO_SHAPE.OVAL, cx, cy, 0.14, 0.14, fill=DARK)
    text(s, cx - 1.2, cy - R - 0.42, 2.4, 0.3, [[(lab, {'caps': True, 'bold': True, 'size': 10.5, 'spc': 140, 'color': DARK})]], align=PP_ALIGN.CENTER)
    text(s, cx - 1.2, cy + R + 0.08, 2.4, 0.3, sub, size=11, color=COPPER, align=PP_ALIGN.CENTER, italic=True)
    tl.spin(hf, 300, 4000, repeat='indefinite').spin(hr, 300, rper, repeat='indefinite')
text(s, 4.25, 4.25, 4.85, 0.3, [[('green hand: ', {'bold': True, 'color': GREEN}), ('magnetic field  ·  ', {}), ('copper hand: ', {'bold': True, 'color': COPPER}), ('rotor (difference exaggerated)', {})]], size=10.5, color=GREY, align=PP_ALIGN.CENTER)
tl.write(s)
hline(s, 0.6, 5.15, 12.1)
label(s, 0.6, 5.35, 5.6, 'Induction motor · the workhorse')
text(s, 0.6, 5.68, 5.6, 1.0, [[('Its rotor is pushed round by the magnetic field and always turns ', {}), ('slightly slower', {'bold': True, 'color': DARK}), (' than the field.', {})]], size=15, line=1.1)
label(s, 7.1, 5.35, 5.6, 'Synchronous motor · the specialist', color=TEAL)
text(s, 7.1, 5.68, 5.6, 1.0, [[('Its rotor is a magnet of its own and turns ', {}), ('exactly in step', {'bold': True, 'color': DARK}), (' with the field – the same speed.', {})]], size=15, line=1.1)

# ====================================================================== 4 SECTION: CONSTRUCTION
s = new('Section', 'sec1')
set_ph(s, 0, 'Construction', size=34, bold=True)
p = ph(s, 0); p.left = Inches(2.85); p.top = Inches(3.3); p.width = Inches(4.6); p.height = Inches(1.0); p.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
text(s, 2.95, 4.45, 4.4, 0.4, 'What is inside each motor', size=16, color=WHITE)
label(s, 2.95, 2.95, 3, '01  ·  Section', color=WHITE)
pic(s, 'ind_cut_l', 7.25, 2.25, w=5.6)

# ====================================================================== 5 STATOR & ROTOR
s = new('Title & Subtitle Only', 'sr')
title(s, 'Two main parts: stator and rotor', 'Every motor has a fixed outer part and a turning inner part')
pic(s, 'ind_statorrotor_l', 1.87, 1.85, w=9.6)
leader(s, 3.75, 2.75, 3.75, 1.65); label(s, 3.9, 1.53, 3, 'Rotor · turns', color=COPPER)
leader(s, 9.36, 2.07, 9.36, 1.65); label(s, 9.51, 1.53, 3, 'Stator · fixed')
for i, (h, d, c) in enumerate([('Stator', 'The fixed outer part: copper coils in a stack of thin steel sheets. It creates the magnetic field.', GREEN),
                               ('Rotor', 'The turning part on the shaft. The magnetic field pushes it round, and it drives the machine.', COPPER),
                               ('Air gap', 'A tiny gap between them – often 1–2 mm. The magnetic field crosses it with no contact.', TEAL)]):
    x = 0.6 + i * 4.15
    hline(s, x, 5.55, 3.75, color=c, weight=1.5)
    text(s, x, 5.7, 3.75, 0.35, h, size=16, bold=True, color=DARK)
    text(s, x, 6.08, 3.75, 0.9, d, size=13, line=1.1)

# ====================================================================== CONSTRUCTION: native 3D-render motion
def badge(s, n, x, y, d, name=None, size=None, ring=True):
    o = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x - d / 2), Inches(y - d / 2), Inches(d), Inches(d))
    o.fill.solid(); o.fill.fore_color.rgb = GREEN
    if ring: o.line.color.rgb = WHITE; o.line.width = Pt(2 if d < 0.6 else 3)
    else: o.line.fill.background()
    o.shadow.inherit = False; shadow(o, blur=8, dist=2, alpha=22)
    tf = o.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = MSO_ANCHOR.MIDDLE; tf.word_wrap = False
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; r = p.add_run(); r.text = str(n)
    r.font.size = Pt(size or (14 if d < 0.6 else 40)); r.font.bold = True; r.font.color.rgb = WHITE
    if name: o.name = name
    return o

def chip(s, x, y, t, color):
    w = 0.3 + 0.1 * len(t)
    r = rect(s, x, y, w, 0.27, fill=None, line=color, radius=0.5)
    tf = r.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = MSO_ANCHOR.MIDDLE; tf.word_wrap = False
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; rr = p.add_run(); rr.text = t
    rr.font.size = Pt(9); rr.font.bold = True; rr.font.color.rgb = color
    rPr = rr._r.get_or_add_rPr(); rPr.set('cap', 'all'); rPr.set('spc', '120')
    return r

def place(s, kind, p, label_txt):
    src = os.path.join(ND3, 'img', NL.img_name(kind, p['obj'], p['yaw']))
    path, (f0, f1, f2, f3) = opt_png(src, None)
    side = p['side']; x0, y0 = p['x'] - side / 2, p['y'] - side / 2
    pc = s.shapes.add_picture(path, Inches(x0 + f0 * side), Inches(y0 + f1 * side), Inches((f2 - f0) * side), Inches((f3 - f1) * side))
    pc.name = f"!!{kind}_{p['obj']}"; pc._element.nvPicPr.cNvPr.set('descr', label_txt)
    return pc

def minimap(kind, ov):
    """'where it sits' locator composed from the same part renders as the overview"""
    dpi = 60; xs = [p['x'] - p['side'] / 2 for p in ov]; ys = [p['y'] - p['side'] / 2 for p in ov]
    X0, Y0 = min(xs), min(ys); X1 = max(p['x'] + p['side'] / 2 for p in ov); Y1 = max(p['y'] + p['side'] / 2 for p in ov)
    canvas = Image.new('RGBA', (int((X1 - X0) * dpi), int((Y1 - Y0) * dpi)), (255, 255, 255, 0))
    for p in ov:
        im = Image.open(os.path.join(ND3, 'img', NL.img_name(kind, p['obj'], p['yaw']))).convert('RGBA').resize((int(p['side'] * dpi),) * 2, Image.LANCZOS)
        canvas.alpha_composite(im, (int((p['x'] - p['side'] / 2 - X0) * dpi), int((p['y'] - p['side'] / 2 - Y0) * dpi)))
    bb = canvas.getchannel('A').point(lambda a: 255 if a > 3 else 0).getbbox(); canvas = canvas.crop(bb)
    out = os.path.join(OPT, f'{kind}_map.png'); _quant(canvas, out)
    to_map = lambda x, y: (((x - X0) * dpi - bb[0]) / canvas.width, ((y - Y0) * dpi - bb[1]) / canvas.height)
    return out, canvas.width / canvas.height, to_map

def construction(kind, motor, items, key, hero_sub, hero_cap):
    L_ = NL.layout(ND3, kind, CFG3[kind]); N = len(items)
    names = {}
    for n, comp in enumerate(CFG3[kind]['components'], 1):
        for o in comp['show']: names.setdefault(o, items[n - 1]['name'])
    EXTRA = dict(hero=f'Complete {motor.lower()}', bearingNDE='Bearing', endShieldDE='End shield', endShieldNDE='End shield', fanCover='Fan cover', shaftFan='Shaft fan', rotorAsm='Rotor', statorAsm='Stator', cooling='Cooling system')
    lab = lambda o: names.get(o) or EXTRA.get(o, o)
    head = f'{motor}: the main components'; sub = f'{N} parts, one at a time – each keeps its number on the slides that follow'
    # hero 1 -> hero 2: the complete motor turns slowly (Morph between two renders, 16 deg apart)
    s = new('Title & Subtitle Only', key + 'h1'); title(s, f'{motor}: the complete machine', hero_sub)
    for p in L_['hero1']['objects']: place(s, kind, p, lab(p['obj']))
    set_trans(s, 'fade', 700, adv=600)
    s = new('Title & Subtitle Only', key + 'h2'); title(s, f'{motor}: the complete machine', hero_sub)
    for p in L_['hero2']['objects']: place(s, kind, p, lab(p['obj']))
    cap = text(s, 0.6, 6.75, 8, 0.35, hero_cap, size=12, color=GREY, italic=True)
    set_trans(s, 'morph', 2400)
    # stage 1 (automatic): covers lift away; then the inside slides apart into the full exploded view
    s = new('Title & Subtitle Only', key + 's1'); title(s, head, sub)
    for p in L_['stage1']['objects']: place(s, kind, p, lab(p['obj']))
    set_trans(s, 'morph', 1500, adv=150)
    # overview: exploded and numbered
    s = new('Title & Subtitle Only', key + 'o'); title(s, head, sub)
    OV = L_['overview']
    for p in OV['objects']: place(s, kind, p, lab(p['obj']))
    set_trans(s, 'morph', 1600)
    anc = OV['anchors']
    pos = {n: [anc[n][0], anc[n][1] - 0.45] for n in anc}
    for _ in range(400):
        for a in pos:
            for b in pos:
                if a >= b: continue
                dx, dy = pos[b][0] - pos[a][0], pos[b][1] - pos[a][1]; d = (dx * dx + dy * dy) ** 0.5 or 1e-3
                if d < 0.6: f = (0.6 - d) / 2 / d; pos[a][0] -= dx * f; pos[a][1] -= dy * f; pos[b][0] += dx * f; pos[b][1] += dy * f
            for c in anc:
                dx, dy = pos[a][0] - anc[c][0], pos[a][1] - anc[c][1]; d = (dx * dx + dy * dy) ** 0.5 or 1e-3
                if d < 0.34: f = (0.34 - d) / d; pos[a][0] += dx * f; pos[a][1] += dy * f
            pos[a][1] += (anc[a][1] - 0.45 - pos[a][1]) * 0.02
            pos[a][0] = min(max(pos[a][0], 0.6), 8.8); pos[a][1] = min(max(pos[a][1], 1.6), 7.0)
    tl = Timeline(); lx = 9.45
    tl.fade_in(label(s, lx, 1.5, 3.3, 'Main components'), 0)
    for n in range(1, N + 1):
        (ax, ay), (bx, by) = anc[n], pos[n]
        ln = s.shapes.add_connector(1, Inches(ax), Inches(ay), Inches(bx), Inches(by)); ln.line.color.rgb = GREEN; ln.line.width = Pt(1.25)
        dot = shape(s.shapes, MSO_SHAPE.OVAL, ax, ay, 0.09, 0.09, fill=GREEN, line=WHITE)
        bd = badge(s, n, bx, by, 0.46, name=f'!!n{n}')
        for shp_ in (dot, ln, bd): tl.fade_in(shp_, 150 + 90 * n, 400)
        y = 1.95 + (n - 1) * 0.62
        b2 = badge(s, n, lx + 0.17, y + 0.17, 0.36, size=12, ring=False)
        t2 = text(s, lx + 0.55, y + 0.01, 3.0, 0.34, items[n - 1]['name'], size=15, bold=True, color=DARK, anchor=MSO_ANCHOR.MIDDLE)
        tl.fade_in(b2, 150 + 90 * n, 400).fade_in(t2, 150 + 90 * n, 400)
    tl.write(s)
    # components: the camera moves in on each part
    mm_img, mm_ar, to_map = minimap(kind, OV['objects'])
    MH = 1.7; MW = MH * mm_ar
    if MW > 3.5: MW = 3.5; MH = MW / mm_ar
    for n, it in enumerate(items, 1):
        s = new('Title & Subtitle Only', f'{key}{n}'); title(s, head, sub)
        set_trans(s, 'morph', 1400)
        C = L_['comps'][n - 1]
        for p in C['objects']: place(s, kind, p, lab(p['obj']))
        if it.get('note'): text(s, 0.6, 6.85, 6, 0.25, it['note'], size=10.5, color=GREY, italic=True)
        badge(s, n, 9.55, 2.0, 1.1, name=f'!!n{n}')
        label(s, 10.3, 1.62, 2.6, f'Component {n} of {N}', color=GREY)
        if it.get('chip'): chip(s, 10.3, 2.0, it['chip'], COPPER if it['chip'] == 'Rotating' else GREEN)
        body = text(s, 9.0, 2.8, 3.95, 2.3, [[(it['name'], {'size': 28, 'bold': True, 'color': DARK})], [(it['desc'], {'size': 16})]], spacing=8, line=1.05)
        ax, ay = C['anchor']
        ln = s.shapes.add_connector(1, Inches(ax), Inches(ay), Inches(8.95), Inches(2.0)); ln.line.color.rgb = GREEN; ln.line.width = Pt(1.5)
        dot = shape(s.shapes, MSO_SHAPE.OVAL, ax, ay, 0.12, 0.12, fill=GREEN, line=WHITE, lw=1.25)
        MX, MY = 9.0, 7.2 - MH
        label(s, 9.0, MY - 0.3, 3.5, 'Where it sits', color=GREY, size=10)
        mm = s.shapes.add_picture(mm_img, Inches(MX), Inches(MY), Inches(MW), Inches(MH)); mm.name = '!!map'
        mu, mv = to_map(*anc[n]); rd = 0.34
        ring = shape(s.shapes, MSO_SHAPE.OVAL, MX + mu * MW, MY + mv * MH, rd, rd, fill=None, line=GREEN, lw=2.5, name='!!ring')
        Timeline().fade_in(dot, 0, 300).wipe_in(ln, 0, 600).fade_in(body, 350, 450).write(s)

IND_ITEMS = [
    dict(name='Stator', chip='Stationary', desc='The fixed outer part. Copper coils in a stack of thin steel sheets create the turning magnetic field.'),
    dict(name='Rotor', chip='Rotating', desc='The turning part inside the stator. The magnetic field pushes it round, and it turns the shaft.'),
    dict(name='Rotor bars and end rings', chip='Rotating', desc='Metal bars joined by a ring at each end – the “squirrel cage”. Current is created in it without any wires.', note='Steel core removed to show the cage'),
    dict(name='Shaft', chip='Rotating', desc='A strong steel bar through the rotor. It carries the turning force out to the pump, fan or compressor.'),
    dict(name='Bearings', desc='One at each end. Steel balls roll between two rings, so the shaft spins smoothly.'),
    dict(name='Frame / housing', chip='Stationary', desc='The cast-iron body with its end covers. It holds and protects everything; its fins carry heat away.'),
    dict(name='Cooling fan', chip='Rotating', desc='Fixed to the back of the shaft. It blows air along the fins to keep the motor cool.'),
]
SYN_ITEMS = [
    dict(name='Stator', chip='Stationary', desc='Just like the induction motor’s stator: its coils create the turning magnetic field.'),
    dict(name='Rotor with poles', chip='Rotating', desc='Its poles stick out like spokes. Each one becomes a fixed North or South magnet.'),
    dict(name='Field coils', chip='Rotating', desc='Copper coils round each pole. A DC current through them turns the poles into magnets.', note='Pole steel removed to show the coils'),
    dict(name='Damper bars', chip='Rotating', desc='Copper bars in the pole faces – a small cage that gets the motor started.', note='Pole steel removed to show the bars'),
    dict(name='Slip rings and brushes', desc='Carbon brushes press on rings on the shaft. They carry the DC into the spinning rotor.'),
    dict(name='Excitation system', chip='Stationary', desc='This cabinet makes the DC current for the rotor coils – it sets how strong the rotor magnets are.'),
    dict(name='Frame and cooling', chip='Stationary', desc='A welded steel housing with a cooler on top. The shaft and bearings do the same job as before.'),
]
construction('induction', 'Induction motor', IND_ITEMS, 'i', 'The most common motor in industry: simple, rugged and low-cost', 'A complete squirrel-cage induction motor – next, we open it up.')
construction('sync', 'Synchronous motor', SYN_ITEMS, 's', 'Used for very large drives that must run at an exact speed', 'A complete large synchronous motor – next, we open it up.')

# ====================================================================== SECTION: HOW THEY WORK
s = new('Section', 'sec2')
set_ph(s, 0, 'How they work', size=34, bold=True)
p = ph(s, 0); p.left = Inches(2.85); p.top = Inches(3.3); p.width = Inches(4.6); p.height = Inches(1.0); p.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
text(s, 2.95, 4.45, 4.4, 0.4, 'Making the invisible visible', size=16, color=WHITE)
label(s, 2.95, 2.95, 3, '02  ·  Section', color=WHITE)
pic(s, 'syn_cut_l', 7.6, 1.9, h=4.9)

# ====================================================================== NATIVE WORKING-PRINCIPLE ANIMATIONS
CX, CY, RS, RB = 3.55, 4.35, 2.45, 1.62
T = 4000    # one field revolution in the animation (ms), slowed down so the eye can follow

def principle_frame(s, ttl, sub, steps, note):
    title(s, ttl, sub)
    st = steps_panel(s, 7.0, 1.55, 5.8, steps, size=15, gap=1.02)
    text(s, 0.6, 6.95, 6.2, 0.3, note, size=10.5, color=GREY, italic=True)
    return st

# ---- the rotating magnetic field
s = new('Title & Subtitle Only', 'rmf')
st = principle_frame(s, 'The rotating magnetic field', 'Both motors start here: three coils make one magnetic field that turns',
    [('Three coils', 'Three pairs of coils sit around the stator, each fed by one of the three supply phases.'),
     ('Currents take turns', 'The current in each coil rises and falls a moment after the one before.'),
     ('One field that turns', 'Together they make one magnetic field – a North and a South pole – that turns round.'),
     ('A magnet follows it', 'A magnet placed in the middle is dragged round by the turning field. Nothing touches it.'),
     ('The speed is fixed', 'The supply frequency sets it: 1500 rpm for a typical 4-pole motor on 50 Hz.')],
    'Animation slowed down: in a real motor the field turns about 25 times a second.')
ring, coils = draw_stator(s, CX, CY, RS, RB)
tl = Timeline()
over = []
for i, k, a, c in coils:
    x, y = polar(CX, CY, (RS + RB) / 2, a)
    g = shape(s.shapes, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, 0.74, 0.46, fill=PHASE[i], line=WHITE, lw=2, rot=90 - a)
    shadow(g, blur=14, dist=0, alpha=60); over.append((i, g))
for cyc in range(2):
    for i in range(3):
        t0 = 1300 + cyc * 3600 + i * 1200
        for j, g in over:
            if j == i: tl.fade_in(g, t0, 350).fade_out(g, t0 + 800, 350)
fg = field_group(s, CX, CY, RB, arrow=True)
tl.fade_in(fg, 9000, 700).spin(fg, 9000, T, repeat='indefinite', ccw=True)
nd = s.shapes.add_group_shape(); ghost_circle(nd.shapes, CX, CY, 0.85)
shape(nd.shapes, MSO_SHAPE.ISOSCELES_TRIANGLE, CX, CY - 0.42, 0.34, 0.84, fill=NCOL)
shape(nd.shapes, MSO_SHAPE.ISOSCELES_TRIANGLE, CX, CY + 0.42, 0.34, 0.84, fill=STEEL_D, rot=180)
shape(nd.shapes, MSO_SHAPE.OVAL, CX, CY, 0.16, 0.16, fill=DARK)
tl.fade_in(nd, 17000, 600).spin(nd, 17000, T, repeat='indefinite', ccw=True)       # 17 s = field start + 2T -> aligned
for (b, t_), at in zip(st, (0, 1300, 9000, 17000, 24000)): tl.fade_in(b, at, 400).fade_in(t_, at, 400)
tl.write(s)

# ---- induction motor: how it turns
s = new('Title & Subtitle Only', 'ianim')
st = principle_frame(s, 'Induction motor: how it turns', 'The turning field drags the rotor along – always a little slower',
    [('The field turns', 'The stator coils create the turning magnetic field.'),
     ('Currents appear in the rotor', 'As the field sweeps over the rotor bars, it creates currents in them – no wires needed.'),
     ('Current + field = force', 'The rotor currents and the field push on each other. This turning force is called torque.'),
     ('The rotor turns', 'The rotor speeds up and chases the field…'),
     ('…but never catches it', 'It always runs a little slower (about 2 %): this lag is the slip. No slip – no current – no force.')],
    'Slip exaggerated in the animation so you can see it.')
draw_stator(s, CX, CY, RS, RB)
tl = Timeline()
fg = field_group(s, CX, CY, RB, arrow=False)
tl.fade_in(fg, 400, 600).spin(fg, 400, T, repeat='indefinite', ccw=True)
rot = s.shapes.add_group_shape(); ghost_circle(rot.shapes, CX, CY, 1.32)
shape(rot.shapes, MSO_SHAPE.OVAL, CX, CY, 2.5, 2.5, fill=STEEL, line=STEEL_D, lw=1)
for k in range(18):
    a = k * 20; x, y = polar(CX, CY, 1.04, a)
    shape(rot.shapes, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, 0.13, 0.36, fill=ALU, line=STEEL_D, lw=0.5, rot=90 - a)
shape(rot.shapes, MSO_SHAPE.ROUNDED_RECTANGLE, CX, CY - 0.55, 0.14, 0.72, fill=COPPER)
shape(rot.shapes, MSO_SHAPE.OVAL, CX, CY, 0.5, 0.5, fill=DARK)
cur = s.shapes.add_group_shape(); ghost_circle(cur.shapes, CX, CY, 1.32)
for a in (90, 270):
    x, y = polar(CX, CY, 1.04, a); shape(cur.shapes, MSO_SHAPE.OVAL, x, y, 1.2, 0.5, fill=RGBColor(0xF5, 0x9E, 0x1B), transp=0.25)
tl.fade_in(cur, 8400, 600).spin(cur, 8400, T, repeat='indefinite', ccw=True)       # field start + 2T -> aligned under the poles
arrs = []
for a, rot_ in ((0, 270), (180, 90)):
    x, y = polar(CX, CY, 1.47, a); arrs.append(shape(s.shapes, MSO_SHAPE.RIGHT_ARROW, x, y, 0.7, 0.26, fill=GREEN, rot=rot_))
for ar in arrs: tl.fade_in(ar, 13500, 500)
tl.spin(rot, 17000, 7000, accel=0.6, ccw=True)                                     # speeds up over 7 s...
tl.spin(rot, 24000, 4900, repeat='indefinite', ccw=True)                           # ...then runs ~18 % slower than the field (slip exaggerated)
for (b, t_), at in zip(st, (0, 8400, 13500, 17000, 26000)): tl.fade_in(b, at, 400).fade_in(t_, at, 400)
tl.write(s)

# ---- synchronous motor: how it locks in step
s = new('Title & Subtitle Only', 'sanim')
st = principle_frame(s, 'Synchronous motor: how it locks in step', 'The rotor becomes a magnet and turns exactly with the field',
    [('The same turning field', 'The stator makes the same turning magnetic field.'),
     ('Getting started', 'A rotor at rest cannot follow such a fast field. The damper bars spin it up, like an induction motor.'),
     ('DC on: the rotor becomes a magnet', 'Its North and South poles are pulled towards the opposite poles of the field.'),
     ('Locked in step', 'Rotor and field now turn together at exactly the same speed: 1500 rpm, zero slip.'),
     ('Under load', 'The rotor trails the field by a small angle – but it never slows down.')],
    'Pole colours show the magnet the rotor becomes once its DC is switched on.')
draw_stator(s, CX, CY, RS, RB)
tl = Timeline()
fg = field_group(s, CX, CY, RB, arrow=False)
tl.fade_in(fg, 400, 600).spin(fg, 400, T, repeat='indefinite', ccw=True)
halo = shape(s.shapes, MSO_SHAPE.DONUT, CX, CY, 2.95, 2.95, fill=RGBColor(0xF5, 0xB0, 0x1B), transp=0.55); halo.adjustments[0] = 0.06
rot = s.shapes.add_group_shape(); ghost_circle(rot.shapes, CX, CY, 1.32)
shape(rot.shapes, MSO_SHAPE.ROUNDED_RECTANGLE, CX, CY, 0.78, 2.3, fill=STEEL, line=STEEL_D, lw=1)
for sgn, col, t_ in ((-1, SCOL, 'S'), (1, NCOL, 'N')):
    shape(rot.shapes, MSO_SHAPE.ROUNDED_RECTANGLE, CX, CY + sgn * 1.12, 1.65, 0.36, fill=col)
    shape(rot.shapes, MSO_SHAPE.ROUNDED_RECTANGLE, CX, CY + sgn * 0.62, 1.05, 0.42, fill=CU)
    label_in(rot.shapes, CX, CY + sgn * 1.12, t_, size=14, color=WHITE)
shape(rot.shapes, MSO_SHAPE.OVAL, CX, CY, 0.44, 0.44, fill=DARK)
rot.rotation = 20                                                                  # trails the field (load angle)
tl.spin(rot, 400 + T, 2 * T, accel=1.0, ccw=True)                                  # damper start: 0 -> field speed in 2T (one turn)
tl.fade_in(halo, 400 + 3 * T, 500)                                                 # DC on
tl.spin(rot, 400 + 3 * T, T, repeat='indefinite', ccw=True)                        # locked: same period, same phase as the field
for (b, t_), at in zip(st, (0, 400 + T, 400 + 3 * T, 18000, 24000)): tl.fade_in(b, at, 400).fade_in(t_, at, 400)
tl.write(s)

# ====================================================================== THE FUNDAMENTAL DIFFERENCE
s = new('Title & Subtitle Only', 'fund')
title(s, 'The fundamental difference', 'Three things separate the two motors')
text(s, 3.55, 1.5, 4.3, 0.35, 'Induction motor', size=17, bold=True, color=GREEN)
text(s, 8.45, 1.5, 4.3, 0.35, 'Synchronous motor', size=17, bold=True, color=TEAL)
rowsF = [
  ('Rotor magnetism', 'Where does the rotor’s magnetism come from?',
   ('ind_cage_l', 'Created by the field', 'The turning field creates current in the cage – nothing is connected to it.'),
   ('rot_salient_l', 'Own DC magnet', 'A DC current in the rotor coils makes fixed North and South poles.')),
  ('Slip', 'Does the rotor lag behind the field?', (None, '≈ 2 %', 'It must lag a little – without slip there is no current and no force.'), (None, '0 %', 'Locked in step with the field – no lag at all.')),
  ('Speed', '4-pole motor on 50 Hz (field: 1500 rpm)', (None, '≈ 1470 rpm', 'Slightly below the field, and drops a little as the load rises.'), (None, '1500 rpm', 'Exactly the field speed, whatever the load.')),
]
for i, (h, q, a, b) in enumerate(rowsF):
    y = 2.0 + i * 1.62
    rect(s, 0.6, y, 12.1, 1.45, fill=LIGHT if i % 2 == 0 else WHITE, radius=0.05)
    text(s, 0.85, y + 0.3, 2.5, 0.4, h, size=17, bold=True, color=DARK)
    text(s, 0.85, y + 0.72, 2.45, 0.6, q, size=11.5, color=GREY, line=1.05)
    for x, (img, big, d), c in ((3.55, a, GREEN), (8.45, b, TEAL)):
        xx = x
        if img: pic(s, img, x, y + 0.2, h=1.05); xx = x + 1.05 * ASP[img] + 0.15
        cw = (8.2 if x < 8 else 12.5) - xx
        text(s, xx, y + 0.22, cw, 0.5, big, size=24 if not img else 18, bold=True, color=c)
        text(s, xx, y + (0.78 if not img else 0.68), cw, 0.7, d, size=12.5, color=TXT, line=1.05)

# ====================================================================== STRENGTHS & LIMITATIONS
s = new('Title & Subtitle Only', 'pros')
title(s, 'Strengths and limitations', 'Neither is “better” – each is the right tool for different jobs')
cols = [(0.6, 'Induction motor', GREEN, ['Simple and rugged', 'Little maintenance', 'Starts by itself', 'Lower cost', 'Available in every size'],
         ['Speed drops slightly with load', 'Draws extra “magnetising” current', 'Changing speed needs a drive (VFD)']),
        (6.85, 'Synchronous motor', TEAL, ['Exact, constant speed', 'Very efficient in large sizes', 'Can help the plant’s power supply', 'Ideal for very large machines'],
         ['More complex and costly', 'Needs a DC supply for the rotor', 'Needs help to start'])]
for x, h, c, pros_, cons in cols:
    rect(s, x, 1.5, 5.9, 4.6, fill=LIGHT, radius=0.04)
    text(s, x + 0.35, 1.72, 5, 0.4, h, size=19, bold=True, color=c)
    label(s, x + 0.35, 2.3, 2.6, 'Strengths', color=DARK, size=10)
    label(s, x + 3.1, 2.3, 2.6, 'Limitations', color=COPPER, size=10)
    for i, t_ in enumerate(pros_):
        y = 2.7 + i * 0.7
        shape(s.shapes, MSO_SHAPE.OVAL, x + 0.41, y + 0.14, 0.12, 0.12, fill=c)
        text(s, x + 0.6, y, 2.4, 0.6, t_, size=14, color=DARK, line=1.02)
    for i, t_ in enumerate(cons):
        y = 2.7 + i * 0.7
        shape(s.shapes, MSO_SHAPE.OVAL, x + 3.16, y + 0.14, 0.12, 0.12, fill=None, line=COPPER, lw=1.25)
        text(s, x + 3.35, y, 2.45, 0.66, t_, size=14, color=TXT, line=1.02)
text(s, 0.6, 6.3, 12.1, 0.6, [[('In one line: ', {'bold': True, 'color': DARK}), ('choose an induction motor by default; choose a synchronous motor when the machine is very large or the speed must be exact.', {})]], size=14, line=1.08)

# ====================================================================== APPLICATIONS
s = new('Title & Subtitle Only', 'apps')
title(s, 'Where we use each motor', 'Induction for everyday machines – synchronous for the very large ones')
label(s, 0.6, 1.45, 6, 'Induction motor · everyday machines')
apps = [('ph_pump.jpg', 'Pumps', 'B. S. Janse, CC BY 2.5'), ('ph_fan.jpg', 'Fans & ventilation', 'Kecko, CC BY 2.0'), ('ph_compressor.jpg', 'Compressors', 'Asurnipal, CC BY-SA 4.0'), ('ph_conveyor.jpg', 'Conveyors', 'L. Lenz, CC BY-SA 4.0'), ('ph_hvac.jpg', 'Air conditioning', 'A. van Beem, CC0')]
for i, (f, t_, c) in enumerate(apps):
    x = 0.6 + i * 2.45; photo(s, f, x, 1.8, 2.3, 1.55)
    text(s, x, 3.42, 2.3, 0.3, t_, size=13.5, bold=True, color=DARK)
    text(s, x, 3.7, 2.3, 0.2, c, size=7, color=GREY)
label(s, 0.6, 4.05, 6, 'Synchronous motor · very large machines', color=TEAL)
apps2 = [('ph_mill.jpg', 'Grinding mills', 'V. Bukharov, CC BY-SA 4.0'), ('ph_cement.jpg', 'Cement plants', 'Jb957, CC0'), ('ph_steel.jpg', 'Steel mills', 'J. Knauer, CC BY 3.0')]
for i, (f, t_, c) in enumerate(apps2):
    x = 0.6 + i * 2.45; photo(s, f, x, 4.4, 2.3, 1.55)
    text(s, x, 6.02, 2.3, 0.3, t_, size=13.5, bold=True, color=DARK)
    text(s, x, 6.3, 2.3, 0.2, c, size=7, color=GREY)
rect(s, 7.95, 4.4, 4.75, 2.3, fill=LIGHT, radius=0.05)
photo(s, 'ph_condenser.jpg', 8.1, 4.55, 1.95, 1.95)
label(s, 10.2, 4.6, 2.4, 'Also', color=TEAL, size=9.5)
text(s, 10.2, 4.88, 2.4, 0.35, 'Large compressors and pumps', size=13, bold=True, color=DARK)
text(s, 10.2, 5.5, 2.4, 1.0, 'Some even run with no load at all, just to support the power grid.', size=11.5, line=1.05)
text(s, 8.1, 6.52, 2.2, 0.2, 'Mriya, CC BY-SA 3.0', size=7, color=GREY)
text(s, 0.6, 6.72, 12, 0.25, 'Photos: Wikimedia Commons.', size=9.5, color=GREY)

# ====================================================================== WHAT TO REMEMBER
s = new('Title & Subtitle Only', 'remember')
title(s, 'What should we remember?', 'Same turning field – two different ways for the rotor to follow it')
pic(s, 'ind_hero_l', 0.7, 1.65, w=3.6)
pic(s, 'syn_hero_l', 7.05, 1.55, h=3.55)
text(s, 4.45, 2.4, 2.5, 0.3, [[('Induction', {'caps': True, 'bold': True, 'color': GREEN, 'size': 11, 'spc': 160})]])
text(s, 4.45, 2.75, 2.4, 1.6, 'The field drags the rotor round – a little slower', size=20, bold=True, color=DARK, line=1.0)
text(s, 10.3, 2.4, 2.5, 0.3, [[('Synchronous', {'caps': True, 'bold': True, 'color': TEAL, 'size': 11, 'spc': 160})]])
text(s, 10.3, 2.75, 2.45, 1.8, 'The rotor is a magnet that locks onto the field', size=20, bold=True, color=DARK, line=1.0)
hline(s, 0.6, 5.5, 12.1)
for i, (n, t_) in enumerate([('1', 'A motor turns electricity into rotation, using a turning magnetic field.'), ('2', 'Induction: no rotor supply, always a little slower. Simple, the default choice.'), ('3', 'Synchronous: DC magnet rotor, exact speed. For very large machines.')]):
    x = 0.6 + i * 4.1; num(s, n, x, 5.8, 0.38)
    text(s, x + 0.55, 5.77, 3.4, 1.1, t_, size=14.5, color=DARK, line=1.08)

# ====================================================================== THANK YOU
s = new('Thank You!', 'thanks')
for p in s.placeholders:
    if p.placeholder_format.type == 1 or p.placeholder_format.idx == 0: p.text_frame.text = 'Thank You!'
text(s, 1.45, 6.55, 6.5, 0.6, [[('Understanding the difference is the first step toward understanding industrial motor applications.', {'italic': True})]], size=14, color=TXT)

write_transitions()
exec(open(os.path.join(HERE, 'notes_v3.py'), encoding='utf-8').read())
prs.save(OUT); print('saved', OUT, len(prs.slides._sldIdLst), 'slides')
