"""Build 'Inside the Motor' on the PDO corporate template (python-pptx)."""
import copy, json, os, sys
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
D2 = os.path.join(HERE, '..', 'deliver2')
IMG = lambda f: os.path.join(D2, 'img', f)
VID = lambda f: os.path.join(D2, 'video', f)
PH = lambda f: os.path.join(D2, 'photos', f)
TEMPLATE = os.path.join(HERE, '..', 'tpl', 'template.pptx')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(D2, 'Inside_the_Motor_Induction_vs_Synchronous.pptx')
ASP = json.load(open(IMG('aspects.json')))

GREEN = RGBColor(0x00, 0xB4, 0x77); TEAL = RGBColor(0x08, 0x9A, 0xA2); DARK = RGBColor(0x2E, 0x36, 0x3A)
TXT = RGBColor(0x4F, 0x5A, 0x60); GREY = RGBColor(0x8A, 0x95, 0x9B); LIGHT = RGBColor(0xF2, 0xF4, 0xF5)
LINE = RGBColor(0xDD, 0xE3, 0xE6); COPPER = RGBColor(0xC8, 0x6B, 0x32); WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SKY = RGBColor(0x2F, 0x7F, 0xE0)

prs = Presentation(TEMPLATE)
# ---- remove all sample slides ----
sldIdLst = prs.slides._sldIdLst
for sldId in list(sldIdLst):
    prs.part.drop_rel(sldId.rId); sldIdLst.remove(sldId)
L = {l.name.strip(): l for l in prs.slide_layouts}

KEYS = []                      # notes key per slide, in deck order
_OLD = iter([1, 2, 3, 4, 8] + list(range(9, 19)))
def new(layout, key=None):
    s = prs.slides.add_slide(L[layout]); KEYS.append(key if key is not None else next(_OLD)); return s

def ph(s, idx):
    for p in s.placeholders:
        if p.placeholder_format.idx == idx: return p
    return None

def kill_ph(s, idx):
    p = ph(s, idx)
    if p is not None: p._element.getparent().remove(p._element)

def set_ph(s, idx, text, size=None, color=None, bold=None):
    p = ph(s, idx); tf = p.text_frame; tf.text = text
    r = tf.paragraphs[0].runs[0]
    if size: r.font.size = Pt(size)
    if color is not None: r.font.color.rgb = color
    if bold is not None: r.font.bold = bold
    return p

def text(s, x, y, w, h, runs, size=14, color=TXT, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=None, line=None, italic=False):
    """runs: str | list of paragraphs; paragraph = str | list of (text, {opts})"""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = anchor
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.alignment = align
        if line: p.line_spacing = line
        if spacing is not None and i > 0: p.space_before = Pt(spacing)
        segs = para if isinstance(para, list) else [(para, {})]
        for t, o in segs:
            r = p.add_run(); r.text = t; f = r.font
            f.size = Pt(o.get('size', size)); f.bold = o.get('bold', bold); f.italic = o.get('italic', italic)
            f.color.rgb = o.get('color', color)
            if o.get('caps'):
                rPr = r._r.get_or_add_rPr(); rPr.set('cap', 'all'); rPr.set('spc', str(o.get('spc', 150)))
    return tb

def label(s, x, y, w, t, color=GREEN, size=10.5, align=PP_ALIGN.LEFT):
    return text(s, x, y, w, 0.25, [[(t, {'caps': True, 'bold': True, 'color': color, 'size': size, 'spc': 160})]], align=align)

def shadow(shape, blur=18, dist=4, alpha=14):
    spPr = shape._element.spPr
    eff = etree.SubElement(spPr, qn('a:effectLst'))
    sh = etree.SubElement(eff, qn('a:outerShdw'), blurRad=str(int(blur * 12700)), dist=str(int(dist * 12700)), dir='5400000', algn='t', rotWithShape='0')
    c = etree.SubElement(sh, qn('a:srgbClr'), val='1C2B33'); etree.SubElement(c, qn('a:alpha'), val=str(alpha * 1000))

def rect(s, x, y, w, h, fill=LIGHT, line=None, radius=0.06, shape=MSO_SHAPE.ROUNDED_RECTANGLE, shd=False):
    r = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE: r.adjustments[0] = radius
    if fill is None: r.fill.background()
    else: r.fill.solid(); r.fill.fore_color.rgb = fill
    if line is None: r.line.fill.background()
    else: r.line.color.rgb = line; r.line.width = Pt(0.75)
    r.shadow.inherit = False
    if shd: shadow(r)
    r.text_frame.text = ''
    return r

def hline(s, x, y, w, color=LINE, weight=0.75):
    c = s.shapes.add_connector(1, Inches(x), Inches(y), Inches(x + w), Inches(y)); c.line.color.rgb = color; c.line.width = Pt(weight); return c

def leader(s, x1, y1, x2, y2, color=GREEN):
    c = s.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2)); c.line.color.rgb = color; c.line.width = Pt(1)
    d = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x1 - 0.05), Inches(y1 - 0.05), Inches(0.1), Inches(0.1)); d.fill.solid(); d.fill.fore_color.rgb = color; d.line.color.rgb = WHITE; d.line.width = Pt(1.25); d.shadow.inherit = False

def pic(s, name, x, y, w=None, h=None):
    a = ASP.get(name)
    if w is not None and h is None: h = w / a
    if h is not None and w is None: w = h * a
    return s.shapes.add_picture(IMG(name + '.png'), Inches(x), Inches(y), Inches(w), Inches(h))

def photo(s, f, x, y, w, h):
    from PIL import Image
    im = Image.open(PH(f)); iw, ih = im.size; ar = w / h
    p = s.shapes.add_picture(PH(f), Inches(x), Inches(y), Inches(w), Inches(h))
    if iw / ih > ar:
        c = (1 - (ih * ar) / iw) / 2; p.crop_left = c; p.crop_right = c
    else:
        c = (1 - (iw / ar) / ih) / 2; p.crop_top = c; p.crop_bottom = c
    return p

def video(s, f, poster, x, y, w, h):
    m = s.shapes.add_movie(VID(f), Inches(x), Inches(y), Inches(w), Inches(h), poster_frame_image=poster, mime_type='video/mp4')
    shadow(m, blur=22, dist=6, alpha=16)
    return m

def num(s, n, x, y, d=0.34, fill=GREEN):
    o = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d)); o.fill.solid(); o.fill.fore_color.rgb = fill; o.line.fill.background(); o.shadow.inherit = False
    tf = o.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; r = p.add_run(); r.text = str(n); r.font.size = Pt(11 if d < 0.4 else 13); r.font.bold = True; r.font.color.rgb = WHITE

def title(s, t, sub=None):
    set_ph(s, 11, t, size=26, color=GREEN, bold=True)
    if sub: set_ph(s, 10, sub, size=16, color=GREY, bold=False)
    else: kill_ph(s, 10)

def notes(s, t): s.notes_slide.notes_text_frame.text = t

def transition(s, kind='fade'):
    sld = s._element
    tr = etree.Element(qn('p:transition'), spd='med')
    etree.SubElement(tr, qn('p:fade'))
    cmo = sld.find(qn('p:clrMapOvr'))
    if cmo is not None: cmo.addnext(tr)
    else: sld.find(qn('p:cSld')).addnext(tr)

# ======================================================================
# 1 COVER
s = new('Cover 3')
set_ph(s, 0, 'Inside the Motor', size=40, bold=True)
set_ph(s, 10, 'Understanding Induction vs. Synchronous Technology', size=20)
set_ph(s, 11, 'Technical Induction Session')
set_ph(s, 12, 'Engineering Fundamentals')
for i, (idx, y) in enumerate([(0, 1.85), (10, 2.75), (11, 3.85), (12, 4.22)]):
    p = ph(s, idx); p.left = Inches(2.85); p.top = Inches(y); p.width = Inches(5.0); p.height = Inches(0.9 if idx == 0 else (0.85 if idx == 10 else 0.4))
pic(s, 'ind_cut_l', 6.75, 4.05, w=3.1)
pic(s, 'syn_cut_l', 9.55, 3.15, h=4.0)
notes(s, """Welcome. In the next fifteen minutes we are going to open up two of the most important machines in any industrial facility: the induction motor and the synchronous motor.

From the outside they look similar – a steel body with a shaft. Inside, they work in two clearly different ways, and that difference decides where each one is used.

No electrical background is needed. We will take each motor apart, then switch it on and watch the invisible magnetic forces that make it turn.""")

# 2 TWO MOTORS, ONE DIFFERENCE
s = new('Title & Subtitle Only')
title(s, 'Two motor families, one key difference', 'Together they drive most of the machines in an industrial plant')
pic(s, 'ind_hero_l', 0.6, 1.6, w=3.45)
pic(s, 'syn_hero_l', 9.85, 1.5, h=3.3)
s.shapes.add_picture(IMG('speed_dials.gif'), Inches(4.25), Inches(2.0), Inches(4.85), Inches(4.85 * 540 / 1600))
text(s, 4.25, 3.7, 4.85, 0.3, 'Blue-green hand: magnetic field · coloured hand: rotor (slip exaggerated)', size=10, color=GREY, align=PP_ALIGN.CENTER)
hline(s, 0.6, 5.15, 12.1)
label(s, 0.6, 5.35, 5.6, 'Induction motor · the workhorse')
text(s, 0.6, 5.68, 5.6, 1.0, [[('The rotor gets its motion through ', {}), ('electromagnetic induction', {'bold': True, 'color': DARK}), (' – it always turns slightly slower than the magnetic field.', {})]], size=15, line=1.1)
label(s, 7.1, 5.35, 5.6, 'Synchronous motor · the specialist', color=TEAL)
text(s, 7.1, 5.68, 5.6, 1.0, [[('The rotor is its own magnet and turns ', {}), ('in step', {'bold': True, 'color': DARK}), (' with the rotating magnetic field – at exactly the same speed.', {})]], size=15, line=1.1)
text(s, 0.6, 6.72, 11, 0.25, 'Electric-motor systems use about 45 % of the world’s electricity – IEA (2011), Energy-Efficiency Policy Opportunities for Electric Motor-Driven Systems (43–46 %).', size=9, color=GREY)
notes(s, """Electric-motor-driven systems use roughly 43 to 46 percent of all electricity in the world, according to the International Energy Agency. Two families of AC motor do most of that work.

• The induction motor is the workhorse – simple, rugged and affordable. Its rotor gets its motion through electromagnetic induction, and it always turns slightly slower than the magnetic field.
• The synchronous motor is the specialist. Its rotor is made into a magnet of its own, so it locks onto the rotating field and turns exactly in step with it. "Synchronous" simply means "at the same speed".

The two dials in the middle show it: on the left the rotor hand keeps falling behind the field hand; on the right they move together. (The slip on the left is exaggerated so you can see it.)

If you remember one thing today, remember this sentence.""")

# 3 SECTION: CONSTRUCTION
s = new('Section')
set_ph(s, 0, 'Construction', size=34, bold=True)
p = ph(s, 0); p.left = Inches(2.85); p.top = Inches(3.3); p.width = Inches(4.6); p.height = Inches(1.0); p.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
text(s, 2.95, 4.45, 4.4, 0.4, 'What is inside each motor', size=16, color=WHITE)
label(s, 2.95, 2.95, 3, '01  ·  Section', color=WHITE)
pic(s, 'ind_cut_l', 7.25, 2.25, w=5.6)
notes(s, "Let's start by looking inside. First the parts both motors share, then each motor taken apart.")

# 4 STATOR & ROTOR
s = new('Title & Subtitle Only')
title(s, 'Two main parts: stator and rotor', 'Every AC motor is built around a fixed outer part and a turning inner part')
pic(s, 'ind_statorrotor_l', 1.87, 1.85, w=9.6)
leader(s, 3.75, 2.75, 3.75, 1.65); label(s, 3.9, 1.53, 3, 'Rotor · turns', color=COPPER)
leader(s, 9.36, 2.07, 9.36, 1.65); label(s, 9.51, 1.53, 3, 'Stator · fixed')
cols = [('Stator', 'The fixed outer part: a laminated steel core with copper windings, bolted inside the frame. It creates the magnetic field.', GREEN),
        ('Rotor', 'The turning inner part on the shaft. The magnetic field pushes it round and it drives the pump, fan or compressor.', COPPER),
        ('Air gap', 'The tiny clearance between them – often only 0.5–2 mm. The magnetic field crosses it without any contact.', TEAL)]
for i, (h, d, c) in enumerate(cols):
    x = 0.6 + i * 4.15
    hline(s, x, 5.55, 3.75, color=c, weight=1.5)
    text(s, x, 5.7, 3.75, 0.35, h, size=16, bold=True, color=DARK)
    text(s, x, 6.08, 3.75, 0.9, d, size=12.5, line=1.1)
notes(s, """Every AC motor – induction or synchronous – is built from two main parts.

The STATOR is the stationary part: a hollow stack of thin steel sheets with copper windings in slots, fixed inside the frame. Its job is to create the magnetic field. It never moves.

The ROTOR is the rotating part. It sits inside the stator on the shaft and turns the machine.

Between them is the AIR GAP – often only half a millimetre to two millimetres. There is no contact: the magnetic field reaches across this gap.

Here the induction motor has been taken apart: the rotor, pulled out on the left, normally sits inside the stator on the right.""")

IND_OFFS = {}
SYN_OFFS = {2: (-0.5, -0.45), 3: (-0.1, 0.62), 4: (0.4, -0.55), 5: (0.55, 0.05), 6: (0.05, -0.5)}
# 5-22 COMPONENTS, ONE SLIDE EACH (overview + parts, induction then synchronous)
exec(open(os.path.join(HERE, 'components_section.py'), encoding='utf-8').read())
component_section('induction', 'Induction motor', IND_ITEMS, IND_OFFS, None, 'i')
component_section('sync', 'Synchronous motor', SYN_ITEMS, SYN_OFFS, None, 's')

# 8 ROTOR DESIGNS & EXCITATION
s = new('Title & Subtitle Only')
title(s, 'The synchronous rotor: design and excitation', 'Its rotor carries a DC field winding – so it has its own fixed North and South poles')
label(s, 0.6, 1.5, 6, 'Two rotor designs')
label(s, 6.95, 1.5, 6, 'Two ways to feed DC into a spinning rotor', color=TEAL)
v = s.shapes.add_connector(1, Inches(6.67), Inches(1.55), Inches(6.67), Inches(6.3)); v.line.color.rgb = LINE; v.line.width = Pt(0.75)
cells = [(0.6, 'rot_salient_l', 'Salient-pole', 'Poles project like spokes. Many poles → lower speeds. Typical for large industrial motors and mills.'),
         (3.6, 'rot_cyl_l', 'Cylindrical (round)', 'Smooth solid drum, winding in slots. Very strong → high speeds (2 or 4 poles).'),
         (6.95, 'rot_salient_l', 'Slip rings & brushes', 'Carbon brushes slide on rotating bronze rings. Simple to control; brushes need inspection.'),
         (9.95, 'rot_brushless_l', 'Brushless exciter', 'A small AC exciter and rotating diodes on the shaft produce DC – no sliding contacts.')]
for x, im, h, d in cells:
    a = ASP[im]; w = 2.8; hh = w / a
    pic(s, im, x, 1.95 + (2.25 - hh) / 2, w=w)
    text(s, x, 4.45, 2.8, 0.35, h, size=15, bold=True, color=DARK)
    text(s, x, 4.85, 2.75, 1.4, d, size=12, line=1.08)
text(s, 0.6, 6.55, 12, 0.3, 'Permanent-magnet synchronous motors need no excitation at all – magnets in the rotor provide the field.', size=11, color=GREY, italic=True)
notes(s, """Two things define a synchronous rotor: its shape and how it gets its DC.

Shape. The salient-pole rotor has poles that stick out like spokes – easy to fit many poles, so it suits lower speeds: large industrial motors, mills, hydro generators. The cylindrical rotor is a smooth, solid drum with the winding buried in slots – strong and compact, for high speeds with two or four poles.

Excitation. The rotor spins, so how does the DC get in?
• Slip rings and brushes: bronze rings on the shaft, with fixed carbon brushes sliding on them. Simple and easy to control, but brushes wear and need inspection.
• Brushless: a small AC exciter on the same shaft, plus a ring of rotating diodes that turns its AC into DC. Nothing slides, so less maintenance.

Permanent-magnet synchronous motors use magnets instead and need no excitation – usually fed from a variable-frequency drive.""")

# 9 SECTION: WORKING PRINCIPLE
s = new('Section')
set_ph(s, 0, 'How they work', size=34, bold=True)
p = ph(s, 0); p.left = Inches(2.85); p.top = Inches(3.3); p.width = Inches(4.6); p.height = Inches(1.0); p.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
text(s, 2.95, 4.45, 4.4, 0.4, 'Making the invisible visible', size=16, color=WHITE)
label(s, 2.95, 2.95, 3, '02  ·  Section', color=WHITE)
pic(s, 'syn_cut_l', 8.15, 1.9, h=5.0)
notes(s, "Now we switch the motors on and watch the magnetic forces that we normally cannot see.")

def side_video_slide(t, sub, vid, poster, side_title, side_items, note, foot=None):
    s = new('Title & Subtitle Only'); title(s, t, sub)
    vw = 9.0; vh = vw * 9 / 16
    video(s, vid, poster, 0.6, 1.45, vw, vh)
    x = 9.95
    label(s, x, 1.5, 2.9, side_title)
    y = 1.9
    for h, d in side_items:
        hline(s, x, y, 2.85)
        text(s, x, y + 0.12, 2.85, 0.45, h, size=20, bold=True, color=DARK)
        text(s, x, y + 0.58, 2.85, 0.7, d, size=11.5, line=1.05)
        y += 1.3
    if foot: text(s, 0.6, 1.45 + vh + 0.12, vw, 0.3, foot, size=10, color=GREY)
    notes(s, note); return s

# 10 RMF
side_video_slide('The rotating magnetic field', 'Common to both motors: three AC currents create one field that turns', 'anim_rmf.mp4', IMG('poster_rmf.png'),
    'Synchronous speed', [('1500 rpm', '4 poles at 50 Hz – the speed of the field'), ('3000 rpm', '2 poles at 50 Hz'), ('120 × f ÷ p', 'Field speed in rpm: f = supply frequency, p = number of poles')],
    """[Click to play – 30 seconds.]

Both motors use the same trick: a magnetic field that rotates without anything moving mechanically.

1 – One coil with alternating current: its field grows, shrinks and flips – it pulses but does not rotate.
2 – Add two more coils 120 degrees apart, each fed from a different phase. Each phase peaks one-third of a cycle after the previous one.
3 – The three pulsing fields add up to ONE field of constant strength that turns smoothly round the stator.
4 – A magnet in the middle is dragged round by it.

The speed of this field is the SYNCHRONOUS SPEED: 120 times frequency divided by the number of poles. At 50 Hz: 3000 rpm with 2 poles, 1500 rpm with 4 poles.""", 'Click to play  ·  30 s')

# 11 INDUCTION WORKING
side_video_slide('Induction motor: how it turns', 'The field induces currents in the cage – and the rotor chases the field', 'anim_induction.mp4', IMG('poster_ind_anim.png'),
    'Slip – the key number', [('1500', 'rpm  ·  magnetic field (4-pole, 50 Hz)'), ('1470', 'rpm  ·  rotor at full load'), ('2 %', 'slip = (field − rotor) ÷ field. Typically 1–5 %. Zero slip would mean zero torque.')],
    """[Click to play – 50 seconds, 8 steps.]

1 Three-phase AC enters the stator.  2 It creates North and South poles that travel round – the rotating field.
3 The moving field sweeps across the rotor bars and induces a voltage; because the cage is closed, current flows. No wires are connected to the rotor.
4 These currents make the rotor a magnet, with poles just behind the stator poles.  5 The stator poles drag them along – a force on every bar (green arrows): torque.
6 The rotor accelerates.  7 It runs slightly slower than the field – that difference is SLIP (exaggerated in the animation; real motors 1–5 %).
8 If it ever caught up, the field would stop cutting the bars: no current, no torque – so it falls back. Slip is what makes it work.

Analogy: you can only push a playground roundabout while your hand moves faster than it. Load increases → slip increases slightly → more torque. The motor adjusts itself.""", 'Click to play  ·  50 s  ·  slip exaggerated in the animation for visibility')

# 12 SYNCHRONOUS WORKING
side_video_slide('Synchronous motor: how it locks in step', 'DC poles on the rotor lock onto the rotating field – exactly the same speed', 'anim_sync.mp4', IMG('poster_sync_anim.png'),
    'It needs help to start', [('Damper bars', 'Start it like an induction motor; DC is switched on at ~95–98 % speed and the rotor pulls into step.'), ('VFD start', 'A drive starts the field slowly and both speed up together.'), ('Pony motor', 'A small auxiliary motor spins it up first – rare today.')],
    """[Click to play – 50 seconds, 7 steps.]

1 The stator creates the same rotating field – here 1500 rpm.
2 Why it cannot start by itself: give the standing rotor DC poles and they are pulled forward, then backward, as the fast field races past. The average is zero – the rotor only shakes.
3 Starting: with the DC off, the damper bars act like an induction cage and the rotor accelerates to just below synchronous speed.
4 DC excitation is switched on – each pole becomes a fixed North or South electromagnet.
5 Pull-in: each rotor pole is attracted to an opposite stator pole and is pulled into step.
6 Locked: exactly synchronous speed, zero slip – the damper bars carry no current.
7 With load the rotor poles trail slightly further behind (the load angle), but the speed stays exactly the same. Too much load and it "pulls out" of step – protection trips it.

Starting methods: damper-winding start (most common), variable-frequency drive (gentle, also gives speed control), or a small pony motor (rare).""", 'Click to play  ·  50 s')

# 13 ADVANTAGES & LIMITATIONS
s = new('Title & Subtitle Only')
title(s, 'Strengths and limitations', 'Neither is “better” – each is the right tool for different jobs')
cols = [(0.6, 'Induction motor', GREEN, ['Simple, robust construction', 'Relatively low maintenance', 'No rotor excitation needed', 'Generally lower initial cost', 'Available everywhere, every size'],
         ['Needs reactive power (lagging power factor)', 'Runs slightly below synchronous speed', 'Variable speed needs a VFD', 'Efficiency & PF drop at light load']),
        (6.85, 'Synchronous motor', TEAL, ['Constant, exact speed', 'Can improve the plant’s power factor', 'Ideal for very large drives', 'High efficiency at large sizes'],
         ['More complex construction', 'Often higher initial cost', 'Starting is more involved', 'Needs excitation & control system'])]
for x, h, c, pros, cons in cols:
    rect(s, x, 1.5, 5.9, 4.6, fill=LIGHT, radius=0.04)
    text(s, x + 0.35, 1.72, 5, 0.4, h, size=18, bold=True, color=c)
    label(s, x + 0.35, 2.3, 2.6, 'Strengths', color=DARK, size=9.5)
    label(s, x + 3.1, 2.3, 2.6, 'Limitations', color=COPPER, size=9.5)
    for i, t in enumerate(pros):
        y = 2.7 + i * 0.66
        o = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 0.35), Inches(y + 0.07), Inches(0.12), Inches(0.12)); o.fill.solid(); o.fill.fore_color.rgb = c; o.line.fill.background(); o.shadow.inherit = False
        text(s, x + 0.6, y, 2.35, 0.6, t, size=12.5, color=DARK, line=1.02)
    for i, t in enumerate(cons):
        y = 2.7 + i * 0.66
        o = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 3.1), Inches(y + 0.07), Inches(0.12), Inches(0.12)); o.fill.background(); o.line.color.rgb = COPPER; o.line.width = Pt(1.25); o.shadow.inherit = False
        text(s, x + 3.35, y, 2.35, 0.6, t, size=12.5, color=TXT, line=1.02)
text(s, 0.6, 6.3, 12.1, 0.6, [[('Power factor in one line: ', {'bold': True, 'color': DARK}), ('think of a glass of beer – the beer is the useful power, the foam is the reactive power needed to magnetise the motor. Induction motors always “order foam”; an over-excited synchronous motor can supply it to the rest of the plant.', {})]], size=12, line=1.08)
notes(s, """A fair comparison.

Induction motor – strengths: simple and robust (no windings or contacts on the rotor), low maintenance, no excitation, lower cost, available in every size. Limitations: it needs reactive power to build its field, so its power factor is lagging; it runs slightly below synchronous speed; variable speed needs a drive; efficiency and power factor drop when it is lightly loaded.

Synchronous motor – strengths: exact constant speed; it can improve the plant's power factor; it is ideal for very large drives; and high efficiency is achievable at large sizes. Limitations: more complex construction, often higher cost, more involved starting, and it needs an excitation and control system.

Power factor in one line – the beer glass: real power is the beer, reactive power is the foam. The glass – cables and transformers – must carry both. Induction motors always need some foam; an over-excited synchronous motor can supply foam to the rest of the plant.""")

# 14 APPLICATIONS
s = new('Title & Subtitle Only')
title(s, 'Where we use each motor', 'Induction by default – synchronous for very large, constant-speed drives')
label(s, 0.6, 1.45, 6, 'Induction motor · general-purpose drives')
apps = [('ph_pump.jpg', 'Pumps', 'B. S. Janse, CC BY 2.5'), ('ph_fan.jpg', 'Fans & ventilation', 'Kecko, CC BY 2.0'), ('ph_compressor.jpg', 'Compressors', 'Asurnipal, CC BY-SA 4.0'), ('ph_conveyor.jpg', 'Conveyors', 'L. Lenz, CC BY-SA 4.0'), ('ph_hvac.jpg', 'HVAC systems', 'A. van Beem, CC0')]
for i, (f, t, c) in enumerate(apps):
    x = 0.6 + i * 2.45; photo(s, f, x, 1.8, 2.3, 1.55)
    text(s, x, 3.42, 2.3, 0.3, t, size=12.5, bold=True, color=DARK)
    text(s, x, 3.68, 2.3, 0.2, c, size=7, color=GREY)
label(s, 0.6, 4.05, 6, 'Synchronous motor · large constant-speed drives', color=TEAL)
apps2 = [('ph_mill.jpg', 'Ball & grinding mills', 'V. Bukharov, CC BY-SA 4.0'), ('ph_cement.jpg', 'Cement plants', 'Jb957, CC0'), ('ph_steel.jpg', 'Steel industry', 'J. Knauer, CC BY 3.0')]
for i, (f, t, c) in enumerate(apps2):
    x = 0.6 + i * 2.45; photo(s, f, x, 4.4, 2.3, 1.55)
    text(s, x, 6.02, 2.3, 0.3, t, size=12.5, bold=True, color=DARK)
    text(s, x, 6.28, 2.3, 0.2, c, size=7, color=GREY)
rect(s, 7.95, 4.4, 4.75, 2.3, fill=LIGHT, radius=0.05)
photo(s, 'ph_condenser.jpg', 8.1, 4.55, 1.95, 1.95)
label(s, 10.2, 4.6, 2.4, 'Special case', color=TEAL, size=9)
text(s, 10.2, 4.88, 2.4, 0.35, 'Synchronous condenser', size=13, bold=True, color=DARK)
text(s, 10.2, 5.25, 2.4, 1.3, 'Spins with no load, over-excited, only to supply reactive power and support grid voltage.', size=10.5, line=1.05)
text(s, 8.1, 6.52, 2.2, 0.2, 'Mriya, CC BY-SA 3.0', size=7, color=GREY)
text(s, 0.6, 6.72, 12, 0.25, 'Also: large compressors and pumps of several MW. Photos: Wikimedia Commons.', size=9.5, color=GREY)
notes(s, """Where do we find them?

Induction motors are the default almost everywhere: pumps, fans and ventilation, compressors, conveyors, HVAC – and general machinery. They are simple, rugged, cheap and available off the shelf; a slight speed change with load does not matter here, and a variable-frequency drive adds speed control when needed.

Synchronous motors appear where drives are very large and speed must be constant: ball and grinding mills in mining and cement, steel rolling mills and blowers, and large compressors and pumps of several megawatts. At that size the extra cost of excitation pays off in efficiency, exact speed and power-factor correction.

A special case: the synchronous condenser – a synchronous machine spinning with no mechanical load, over-excited purely to supply reactive power and support grid voltage. Utilities use them, for example this one in Melbourne, and they are returning to stabilise grids with high shares of wind and solar.""")

# 14b FUNDAMENTAL DIFFERENCE
s = new('Title & Subtitle Only')
title(s, 'The fundamental difference', 'Three things separate the two motors: rotor excitation, slip and operating speed')
text(s, 3.55, 1.5, 4.3, 0.35, 'Induction motor', size=17, bold=True, color=GREEN)
text(s, 8.45, 1.5, 4.3, 0.35, 'Synchronous motor', size=17, bold=True, color=TEAL)
rowsF = [
  ('Rotor excitation', 'Where does the rotor’s magnetism come from?',
   ('ind_cage_l', 'None needed', 'Current is induced in the cage by the rotating field.'),
   ('rot_salient_l', 'DC supply', 'A DC field winding (or permanent magnets) makes fixed N and S poles.')),
  ('Slip', 'Does the rotor lag behind the field?', (None, '≈ 1–5 %', 'Must lag: without slip there is no induced current and no torque.'), (None, '0 %', 'Locked in step – no slip at all in steady operation.')),
  ('Operating speed', '4-pole motor on a 50 Hz supply (field: 1500 rpm)', (None, '≈ 1470 rpm', 'Slightly below synchronous; drops a little as load increases.'), (None, '1500 rpm', 'Exactly synchronous, whatever the load – until it is overloaded.')),
]
for i, (h, q, a, b) in enumerate(rowsF):
    y = 2.0 + i * 1.62
    rect(s, 0.6, y, 12.1, 1.45, fill=LIGHT if i % 2 == 0 else WHITE, radius=0.05)
    text(s, 0.85, y + 0.3, 2.5, 0.4, h, size=16, bold=True, color=DARK)
    text(s, 0.85, y + 0.72, 2.45, 0.6, q, size=11, color=GREY, line=1.05)
    for x, (img, big, d), c in ((3.55, a, GREEN), (8.45, b, TEAL)):
        xx = x
        if img:
            pic(s, img, x, y + 0.2, h=1.05); xx = x + 1.05 * ASP[img] + 0.15
        cw = (8.2 if x < 8 else 12.5) - xx
        text(s, xx, y + 0.22, cw, 0.5, big, size=24 if not img else 18, bold=True, color=c)
        text(s, xx, y + (0.78 if not img else 0.68), cw, 0.7, d, size=12, color=TXT, line=1.05)
notes(s, """This is the heart of the comparison – three differences.

Rotor excitation: the induction motor needs none – the rotating field induces the current in the cage. The synchronous motor needs a DC supply to its field winding (or permanent magnets) so that its rotor has fixed North and South poles.

Slip: the induction rotor must lag behind the field, typically 1 to 5 percent – without that lag no current would be induced and there would be no torque. The synchronous rotor is locked in step: zero slip.

Operating speed: take a 4-pole motor on 50 Hz; the field turns at 1500 rpm. The induction motor runs at about 1470 rpm and slows slightly with load. The synchronous motor runs at exactly 1500 rpm whatever the load – until it is overloaded and pulls out of step.""")

# 15 COMPARISON TABLE
s = new('Title & Subtitle Only')
title(s, 'Induction vs. synchronous at a glance', 'Eleven questions, two answers')
rows = [('Construction', 'Simple, rugged', 'More complex'), ('Rotor design', 'Squirrel cage: bars + end rings', 'Salient poles or round rotor + field winding'),
        ('Working principle', 'Induced rotor currents', 'Rotor magnet locks onto the field'), ('Rotor excitation', 'None – induced', 'DC via slip rings or brushless; or magnets'),
        ('Starting', 'Self-starting', 'Damper winding, VFD or auxiliary motor'), ('Operating speed', 'Slightly below synchronous', 'Exactly synchronous'),
        ('Slip', 'About 1–5 %', 'Zero'), ('Maintenance', 'Low', 'Higher (exciter, brushes if fitted)'), ('Initial cost', 'Lower', 'Higher – pays off on large drives'),
        ('Power factor', 'Lagging, varies with load', 'Adjustable: 1.0 or leading'), ('Typical uses', 'Pumps, fans, compressors, conveyors, HVAC', 'Mills, large compressors & pumps, PF correction')]
tbl = s.shapes.add_table(len(rows) + 1, 3, Inches(0.6), Inches(1.45), Inches(12.1), Inches(0.42 * (len(rows) + 1))).table
tbl.columns[0].width = Inches(2.6); tbl.columns[1].width = Inches(4.5); tbl.columns[2].width = Inches(5.0)
tblPr = tbl._tbl.tblPr
for a in ('bandRow', 'firstRow'): tblPr.set(a, '0')
hdr = ['', 'Induction motor', 'Synchronous motor']
for r in range(len(rows) + 1):
    tbl.rows[r].height = Inches(0.42)
    for c in range(3):
        cell = tbl.cell(r, c); cell.margin_left = Inches(0.14); cell.margin_right = Inches(0.08); cell.margin_top = cell.margin_bottom = Inches(0.02)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        t = hdr[c] if r == 0 else rows[r - 1][c]
        tf = cell.text_frame; tf.text = t; run = tf.paragraphs[0].runs[0] if tf.paragraphs[0].runs else None
        cell.fill.solid()
        if r == 0: cell.fill.fore_color.rgb = GREEN if c != 2 else TEAL
        else: cell.fill.fore_color.rgb = LIGHT if r % 2 else WHITE
        if run:
            run.font.size = Pt(12.5 if r else 13); run.font.bold = (r == 0 or c == 0)
            run.font.color.rgb = WHITE if r == 0 else (DARK if c == 0 else TXT)
notes(s, """Everything side by side – about thirty seconds to read.
Construction: simple versus more complex. Rotor: squirrel cage versus poles with a field winding. Principle: induced currents versus a rotor magnet locking onto the field. Excitation: none versus DC (or magnets). Starting: self-starting versus damper winding, drive or auxiliary motor. Speed: slightly below synchronous versus exactly synchronous. Slip: a few percent versus zero. Maintenance: low versus higher. Cost: lower versus higher. Power factor: lagging versus adjustable. Uses: general-purpose drives versus large constant-speed drives and power-factor correction.""")

# 16 WHAT TO REMEMBER
s = new('Title & Subtitle Only')
title(s, 'What should we remember?', 'Same rotating field – two different ways for the rotor to follow it')
pic(s, 'ind_hero_l', 0.7, 1.65, w=3.6)
pic(s, 'syn_hero_l', 7.05, 1.55, h=3.55)
text(s, 4.45, 2.4, 2.5, 0.3, [[('Induction', {'caps': True, 'bold': True, 'color': GREEN, 'size': 11, 'spc': 160})]])
text(s, 4.45, 2.75, 2.4, 1.6, 'Motion through electromagnetic induction', size=20, bold=True, color=DARK, line=1.0)
text(s, 10.3, 2.4, 2.5, 0.3, [[('Synchronous', {'caps': True, 'bold': True, 'color': TEAL, 'size': 11, 'spc': 160})]])
text(s, 10.3, 2.75, 2.45, 1.8, 'Motion through magnetic locking and synchronized rotation', size=20, bold=True, color=DARK, line=1.0)
hline(s, 0.6, 5.5, 12.1)
take = [('1', 'Both stators create a magnetic field rotating at synchronous speed.'), ('2', 'The rotor is the difference: induced currents (slip) or its own DC magnet (no slip).'), ('3', 'Choose induction by default; synchronous when size, exact speed or power factor justify it.')]
for i, (n, t) in enumerate(take):
    x = 0.6 + i * 4.1; num(s, n, x, 5.8, 0.38)
    text(s, x + 0.55, 5.77, 3.4, 1.1, t, size=13.5, color=DARK, line=1.08)
notes(s, """To wrap up:

Both motors start from the same idea – a stator that creates a magnetic field rotating at synchronous speed.

The difference is how the rotor follows it:
• Induction motor – motion through electromagnetic induction. The field induces currents in the cage, so the rotor always runs slightly slower: slip. Simple, rugged, the default choice.
• Synchronous motor – motion through magnetic locking. The rotor is its own magnet and turns exactly in step: no slip. It needs excitation and a starting method, and is chosen for large drives, exact speed and power-factor control.

Understanding the difference is the first step toward understanding industrial motor applications.""")

# 17 THANK YOU
s = new('Thank You!')
for p in s.placeholders:
    if p.placeholder_format.type == 1 or p.placeholder_format.idx == 0: p.text_frame.text = 'Thank You!'
text(s, 1.45, 6.55, 6.5, 0.6, [[('Understanding the difference is the first step toward understanding industrial motor applications.', {'italic': True})]], size=14, color=TXT)
notes(s, """Thank you – questions?

Possible questions:
• Can an induction motor run exactly at synchronous speed? Not as a motor – above synchronous speed it becomes a generator.
• Why not use synchronous motors everywhere? Higher cost and complexity; for small and medium drives the induction motor is the better buy.
• What if a synchronous motor is overloaded? It pulls out of step and protection trips it.
• Electric cars? Many use permanent-magnet synchronous motors, some use induction motors – both fed from an inverter.

For Q&A, open viewer/motor_explorer_offline.html to rotate and take apart either motor live.""")

# BACKUP (hidden): the full exploded-view videos, for Q&A
# 5 INDUCTION EXPLODED
s = new('Title & Subtitle Only', key='b5')
title(s, 'Induction motor: taking it apart', 'Squirrel-cage, totally enclosed fan-cooled motor – 12 components in 50 seconds')
video(s, 'induction_motor_exploded.mp4', IMG('poster_ind.png'), 1.2, 1.38, 10.93, 6.15 * 0.9)
text(s, 1.2, 6.97, 10.9, 0.25, 'Click to play  ·  pause on any component to discuss it', size=10, color=GREY, align=PP_ALIGN.CENTER)
notes(s, """[Click the video to play – 50 seconds. Pause on any part.]

A typical industrial induction motor – the kind on thousands of pumps and fans.

The motor opens up in a logical sequence: the frame lifts off, the rotor slides out of the stator, and the end shields, bearings, fan and cover move away along the shaft line. Then each component is highlighted:
1 Stator – the fixed outer part.  2 Stator core – thin insulated steel sheets that guide the magnetic field with low losses.  3 Stator windings – copper coils in three groups, one per phase (shown in three colours).
4 Rotor – the turning part.  5 Rotor core – laminated steel on the shaft.  6 Rotor bars – aluminium bars cast into the rotor; nothing is wired to them.  7 End rings – short-circuit the bars, forming the "squirrel cage".
8 Air gap – the small space the field must cross.  9 Shaft.  10 Bearings.  11 Frame and end shields – hold everything and shed heat through the fins.  12 Cooling fan and cover.

Interactive model for Q&A: viewer/motor_explorer_offline.html (open in any browser).""")

# 7 SYNCHRONOUS EXPLODED
s = new('Title & Subtitle Only', key='b7')
title(s, 'Synchronous motor: taking it apart', 'Large salient-pole motor with DC excitation, slip rings and top-mounted cooler')
video(s, 'synchronous_motor_exploded.mp4', IMG('poster_syn.png'), 1.2, 1.38, 10.93, 6.15 * 0.9)
text(s, 1.2, 6.97, 10.9, 0.25, 'Click to play  ·  pause on any component to discuss it', size=10, color=GREY, align=PP_ALIGN.CENTER)
notes(s, """[Click the video to play – 50 seconds.]

A large industrial synchronous motor, the kind used on big compressors or mills.

1–3 The stator is built exactly like the induction-motor stator: laminated core and a three-phase winding that creates the rotating field.
4–6 The rotor is different: salient (projecting) poles, each wound with a copper field coil. With DC current each pole becomes a fixed North or South electromagnet. Damper bars in the pole faces form a small cage used for starting.
7 The DC excitation system – an exciter cubicle supplying controlled DC.  8 Slip rings and brushes – the sliding contact that carries DC into the spinning rotor.
9–12 Shaft, oil-lubricated sleeve bearings, the welded frame, and the cooling system: a shaft fan pushes internal air through a top-mounted heat exchanger.""")

for s in list(prs.slides)[-2:]: s._element.set('show', '0')

MORPH_XML = ('<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
  '<mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159">'
  '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" spd="slow" p14:dur="1000"><p159:morph option="byObject"/></p:transition>'
  '</mc:Choice><mc:Fallback><p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>')
for s in prs.slides:
    if s.slide_id in MORPH:
        el = etree.fromstring(MORPH_XML); cmo = s._element.find(qn('p:clrMapOvr'))
        (cmo if cmo is not None else s._element.find(qn('p:cSld'))).addnext(el)
    else: transition(s)
prs.save(OUT); print('saved', OUT, len(prs.slides._sldIdLst))

# ---------------- timed speaker script (overrides notes; target ≈ 13 min) ----------------
NOTES = {
1: ("0:30", """Good morning. In the next fifteen minutes we will open up the two most important motors in industry – the induction motor and the synchronous motor.
From outside they look similar. Inside, they work differently – and that difference decides where each one is used. No electrical background is needed."""),
2: ("0:55", """Electric motors use about 45 percent of the world's electricity, and two families do most of that work.
The induction motor is the workhorse: simple, rugged and affordable. Its rotor is pushed round by induction and always turns slightly slower than the magnetic field.
The synchronous motor is the specialist. Its rotor is a magnet of its own and turns exactly in step with the field.
Look at the dials: on the left the rotor hand keeps falling behind; on the right both hands move together. Remember this picture – everything else explains it."""),
3: ("0:10", """First: what is inside?"""),
4: ("0:30", """Every AC motor has two main parts.
The stator is the fixed outer part. It creates the magnetic field and never moves.
The rotor is the turning part on the shaft. Between them is a tiny air gap, often only one or two millimetres – the field crosses it without any contact."""),
"io": ("0:25", """Here is the induction motor taken apart. Seven main parts, numbered one to seven.
We will look at each one on its own. Keep an eye on the number, and on the small map in the corner that shows where the part sits."""),
"i1": ("0:15", """Number one, the stator. The fixed outer part: a stack of thin steel sheets with copper coils in the slots. Fed with three-phase power, these coils create the rotating magnetic field."""),
"i2": ("0:15", """Number two, the rotor. The turning part, inside the stator. The magnetic field pushes it round, and it turns the shaft."""),
"i3": ("0:20", """Number three is the heart of this motor: the rotor bars and end rings. Here we have removed the steel so you can see them.
Bars run along the rotor and a ring at each end joins them into a closed cage – the "squirrel cage". Nothing is wired to it: the current is induced by the field. That is why it is so simple and reliable."""),
"i4": ("0:10", """Number four, the shaft. It carries the rotor and takes the turning force out to the machine."""),
"i5": ("0:12", """Number five, the bearings – one at each end. Steel balls roll between two rings, so the shaft turns smoothly with very little friction. They are the main wear part of the motor."""),
"i6": ("0:12", """Number six, the frame or housing, with its end covers. It holds everything in line and protects it, and the fins carry the heat away."""),
"i7": ("0:12", """And number seven, the cooling fan on the back of the shaft. It blows air along those fins. Seven parts – that is the whole induction motor."""),
"so": ("0:25", """Now the large synchronous motor, with ten main parts. Several are the same as before; the new ones are in the rotor and in how it gets its DC supply."""),
"s1": ("0:08", """Number one, the stator – built just like the induction motor's, and it makes the same rotating field."""),
"s2": ("0:15", """Number two, the rotor – and this is where the motors differ. Its poles stick out like spokes. With DC current, each pole becomes a fixed North or South magnet."""),
"s3": ("0:15", """Number three, the field winding: copper coils wound round each pole. The DC current flows through these coils and turns the poles into electromagnets."""),
"s4": ("0:15", """Number four, the damper bars – copper bars in the pole faces forming a small cage. They let the motor start like an induction motor, and they calm any swinging once it runs."""),
"s5": ("0:15", """Number five, the slip rings and brushes. The rotor spins, so how does the DC get in? Carbon brushes press on rings on the shaft – a sliding contact."""),
"s6": ("0:15", """Number six, the DC excitation system. This cabinet turns AC into controlled DC for the field winding. It sets how strong the rotor magnets are – and with that, the plant's power factor."""),
"s7": ("0:07", """Number seven, the shaft – forged steel, carrying the heavy rotor."""),
"s8": ("0:10", """Number eight, the bearings. In big machines these are sleeve bearings: the shaft floats on a thin film of oil, so metal never touches metal."""),
"s9": ("0:08", """Number nine, the frame – a welded steel box bolted to the foundation."""),
"s10": ("0:12", """And number ten, the cooling system: a fan on the shaft pushes warm air from inside through the cooler on top, where outside air takes the heat away."""),
8: ("0:35", """Two more points about the synchronous rotor.
Shape: salient poles suit large, slower machines; a smooth cylindrical rotor suits high speeds.
DC supply: through slip rings and brushes, as we just saw – or brushless, with a small exciter and rotating diodes on the shaft, so nothing slides. Permanent-magnet motors need no excitation at all."""),
"b5": (None, """[Click to play – 49 s.] The complete exploded-view animation of the induction motor, for questions.
A typical industrial induction motor. Watch it open in sequence: the frame lifts off, the rotor slides out of the stator, and the end shields, bearings and fan move away along the shaft line.
Now each part: the stator with its laminated core and three-phase copper windings; the rotor with its core, aluminium bars and end rings – the squirrel cage; the air gap; the shaft; the bearings; the frame with cooling fins; and the shaft-mounted fan. Then it closes up again."""),
"b7": (None, """[Click to play – 49 s.] The complete exploded-view animation of the synchronous motor, for questions.
Now a large synchronous motor, the kind used on big compressors and mills.
The stator is built just like the induction motor's. The rotor is different: projecting poles, each wound with a copper field coil. With DC current every pole becomes a fixed North or South electromagnet. Damper bars in the pole faces help it start.
The DC comes from an exciter cubicle, through slip rings and carbon brushes. Then shaft, sleeve bearings, frame and the cooling system on top."""),
9: ("0:10", """Now we switch them on and make the invisible magnetic forces visible."""),
10: ("0:40", """[Click to play – 30 s.]
Both motors use the same trick. One coil with AC makes a field that only pulses. Add two more coils, 120 degrees apart, fed a third of a cycle later – and the three pulsing fields add up to one field that rotates.
Its speed is the synchronous speed: 1500 rpm for a 4-pole motor on 50 Hz."""),
11: ("1:00", """[Click to play – 51 s. Speak over the video.]
The rotating field sweeps across the rotor bars. A moving magnetic field crossing a conductor induces a voltage, and because the cage is closed, current flows.
That current turns the rotor into a magnet, and the stator's poles drag it along – that is torque. The rotor speeds up and chases the field.
But it never catches it: if it did, nothing would cross the bars, the current and the torque would disappear. So it always runs a little slower – that gap is slip, typically 1 to 5 percent."""),
12: ("1:00", """[Click to play – 49 s. Speak over the video.]
Same rotating field. But a standing rotor with DC poles cannot follow it: it is pulled forward, then backward, and only shakes.
So it starts with its damper bars, like an induction motor, up to almost full speed. Then the DC is switched on, the rotor poles lock onto the opposite stator poles and are pulled into step.
Now it turns at exactly synchronous speed. Under load the poles trail by a small angle – but the speed does not change."""),
13: ("0:55", """Neither motor is better – each fits different jobs.
The induction motor is simple, low-maintenance and cheaper; its limits are a lagging power factor, slightly load-dependent speed, and the need for a drive to vary speed.
The synchronous motor gives exact speed, high efficiency at large sizes and can correct the plant's power factor; but it is more complex, costs more and needs excitation and a starting method.
Power factor in one line: the foam on a beer – needed to magnetise motors but doing no work. A synchronous motor can supply that foam."""),
14: ("0:50", """Induction motors are the default: pumps, fans, compressors, conveyors, HVAC – simple, rugged and available everywhere.
Synchronous motors are chosen for very large, constant-speed drives: grinding mills, cement plants, steel mills and big compressors, where efficiency and power-factor correction pay back the extra cost.
A special case: the synchronous condenser – it spins with no load at all, purely to support the grid voltage."""),
15: ("0:55", """This is the heart of the comparison.
Excitation: the induction rotor needs none – its current is induced. The synchronous rotor needs DC, or magnets, to be a magnet.
Slip: the induction rotor must lag, about 1 to 5 percent, or there would be no torque. The synchronous rotor has zero slip.
Speed: with a 4-pole motor on 50 Hz, about 1470 rpm versus exactly 1500 rpm."""),
16: ("0:25", """Everything side by side. I won't read every row – the key lines are rotor excitation, starting, speed and slip, which we have just seen. This slide is your one-page reference."""),
17: ("0:35", """To remember: both stators create the same rotating field.
The induction motor follows it through electromagnetic induction – always slightly slower.
The synchronous motor follows it through magnetic locking – exactly in step.
Understanding that difference is the first step toward understanding industrial motor applications."""),
18: ("0:05", """Thank you – I am happy to take questions.

Backup answers:
• Can an induction motor reach synchronous speed? Not as a motor – above it, it becomes a generator.
• Why not use synchronous motors everywhere? Cost and complexity; for small and medium drives induction wins.
• What if a synchronous motor is overloaded? It pulls out of step and protection trips it.
• Q&A model: viewer/motor_explorer_offline.html."""),
}
elapsed = 0
assert len(KEYS) == len(prs.slides._sldIdLst), (len(KEYS), len(prs.slides._sldIdLst))
for k, s in zip(KEYS, prs.slides):
    cue, body = NOTES[k]
    if cue is None:
        s.notes_slide.notes_text_frame.text = "[Backup slide – hidden, not part of the timed talk]\n\n" + body; continue
    m, sec = cue.split(':'); elapsed += int(m) * 60 + int(sec)
    s.notes_slide.notes_text_frame.text = f"[Time: {cue}  ·  running total {elapsed // 60}:{elapsed % 60:02d}]\n\n" + body
print('scripted total', elapsed // 60, 'min', elapsed % 60, 's')
prs.save(OUT)
