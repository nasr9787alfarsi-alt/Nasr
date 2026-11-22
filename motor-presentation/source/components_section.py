# Construction section: one slide per component (exec'd from build_brand.py, shares its globals).
# Overview slide with numbered callouts -> one slide per component with a large isolated 3D render,
# the matching number, name, one-line function and a locator mini-map. Morph transitions carry the
# overview image into the mini-map and the overview number into the big badge.
CI = lambda f: os.path.join(D2, 'comp', f)
MORPH = set()   # slides that get a Morph transition (with fade fallback)

def badge(s, n, x, y, d, name=None, size=None, ring=True):
    o = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x - d / 2), Inches(y - d / 2), Inches(d), Inches(d))
    o.fill.solid(); o.fill.fore_color.rgb = GREEN
    if ring: o.line.color.rgb = WHITE; o.line.width = Pt(2 if d < 0.6 else 3)
    else: o.line.fill.background()
    o.shadow.inherit = False; shadow(o, blur=8, dist=2, alpha=22)
    tf = o.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.word_wrap = False
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

def studio_panel(s, x, y, w, h):
    r = rect(s, x, y, w, h, fill=LIGHT, radius=0.04)
    r.fill.gradient(); r.fill.gradient_angle = 90
    st = r.fill.gradient_stops; st[0].color.rgb = RGBColor(0xFA, 0xFB, 0xFC); st[0].position = 0; st[1].color.rgb = RGBColor(0xE4, 0xE9, 0xEC); st[1].position = 1.0
    return r

def cropped_overview(kind):
    from PIL import Image
    src = CI(kind + '_overview.png'); out = CI(kind + '_overview_crop.png')
    im = Image.open(src); W, H = im.size; x0, y0, x1, y1 = im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
    pad = int(0.02 * W); x0, y0, x1, y1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
    im.crop((x0, y0, x1, y1)).save(out)
    an = json.load(open(CI(kind + '_overview.json')))
    an = {k: [(u * W - x0) / (x1 - x0), (v * H - y0) / (y1 - y0)] for k, (u, v) in an.items()}
    return out, (x1 - x0) / (y1 - y0), an

def component_section(kind, motor, items, offsets, ov_note, key):
    ov_png, ov_ar, anchors = cropped_overview(kind)
    N = len(items)
    head = f'{motor}: the main components'
    # ---------- overview ----------
    s = new('Title & Subtitle Only', key=key + 'o')
    title(s, head, f'{N} parts, one at a time – each keeps its number on the slides that follow')
    AW, AH = 8.6, 5.55; OW = min(AW, AH * ov_ar); OH = OW / ov_ar; OX = 0.45 + (AW - OW) / 2; OY = 1.35 + (AH - OH) / 2
    m = s.shapes.add_picture(ov_png, Inches(OX), Inches(OY), Inches(OW), Inches(OH)); m.name = '!!motor'
    for n in range(1, N + 1):
        u, v = anchors[str(n)]; ax, ay = OX + u * OW, OY + v * OH
        dx, dy = offsets.get(n, (0, -0.42)); bx, by = ax + dx, ay + dy
        leader_line = s.shapes.add_connector(1, Inches(ax), Inches(ay), Inches(bx), Inches(by)); leader_line.line.color.rgb = GREEN; leader_line.line.width = Pt(1.25)
        dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(ax - 0.045), Inches(ay - 0.045), Inches(0.09), Inches(0.09))
        dot.fill.solid(); dot.fill.fore_color.rgb = GREEN; dot.line.color.rgb = WHITE; dot.line.width = Pt(1); dot.shadow.inherit = False
        badge(s, n, bx, by, 0.44, name=f'!!n{n}')
    lx = 9.55; label(s, lx, 1.5, 3.3, 'Main components')
    step = min(0.56, 5.0 / N); y0 = 1.95
    for n, it in enumerate(items, 1):
        y = y0 + (n - 1) * step
        badge(s, n, lx + 0.17, y + 0.17, 0.34, size=11, ring=False)
        text(s, lx + 0.5, y + 0.02, 3.0, 0.32, it['name'], size=14.5 if N <= 7 else 13.5, bold=True, color=DARK, anchor=MSO_ANCHOR.MIDDLE)
    text(s, lx, y0 + N * step + 0.15, 3.3, 0.5, 'Next: each part on its own, enlarged.', size=11, color=GREY, italic=True)
    # ---------- one slide per component ----------
    for n, it in enumerate(items, 1):
        s = new('Title & Subtitle Only', key=f'{key}{n}')
        title(s, head, f'{N} parts, one at a time – each keeps its number on the slides that follow')
        MORPH.add(s.slide_id)
        studio_panel(s, 0.4, 1.35, 8.3, 5.85)
        ph_ = s.shapes.add_picture(CI(f'{kind}_c{n}.png'), Inches(0.4 + (8.3 - 7.6) / 2), Inches(1.37), Inches(7.6), Inches(5.7)); ph_.name = '!!comp'
        if it.get('note'): text(s, 0.65, 6.85, 6, 0.25, it['note'], size=10, color=GREY, italic=True)
        # number, name, function
        badge(s, n, 9.55, 2.0, 1.1, name=f'!!n{n}')
        label(s, 10.3, 1.62, 2.6, f'Component {n} of {N}', color=GREY)
        if it.get('chip'): chip(s, 10.3, 2.0, it['chip'], COPPER if it['chip'] == 'Rotating' else GREEN)
        text(s, 9.0, 2.8, 3.95, 2.25, [[(it['name'], {'size': 28, 'bold': True, 'color': DARK})], [(it['desc'], {'size': 15.5})]], spacing=8, line=1.05)
        # locator mini-map: same overview image (morphs from the overview slide), ring on this part
        MW = 3.3; MH = MW / ov_ar
        if MH > 1.8: MH = 1.8; MW = MH * ov_ar
        MX, MY = 9.0, 7.2 - MH
        label(s, 9.0, MY - 0.3, 3.5, 'Where it sits', color=GREY, size=9.5)
        mm = s.shapes.add_picture(ov_png, Inches(MX), Inches(MY), Inches(MW), Inches(MH)); mm.name = '!!motor'
        u, v = anchors[str(n)]; rd = 0.36
        ring = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(MX + u * MW - rd / 2), Inches(MY + v * MH - rd / 2), Inches(rd), Inches(rd))
        ring.fill.background(); ring.line.color.rgb = GREEN; ring.line.width = Pt(2.5); ring.shadow.inherit = False; ring.name = '!!ring'

IND_ITEMS = [
    dict(name='Stator', chip='Stationary', desc='The fixed outer part. Copper coils in a stack of thin steel sheets create the rotating magnetic field.'),
    dict(name='Rotor', chip='Rotating', desc='The turning part inside the stator. The magnetic field pushes it round, and it turns the shaft.'),
    dict(name='Rotor bars and end rings', chip='Rotating', desc='Bars joined by a ring at each end form a closed “squirrel cage”. Current is induced in it – no wires needed.', note='Steel core removed to show the cage'),
    dict(name='Shaft', chip='Rotating', desc='A strong steel bar through the rotor. It carries the turning force out to the pump, fan or compressor.'),
    dict(name='Bearings', desc='One at each end. Steel balls roll between two rings, so the shaft spins smoothly with little friction.'),
    dict(name='Frame / housing', chip='Stationary', desc='The cast-iron body and end covers. It holds and protects everything; its fins carry heat away.'),
    dict(name='Cooling fan', chip='Rotating', desc='Fixed to the back of the shaft. It blows air along the fins to keep the motor cool.'),
]
SYN_ITEMS = [
    dict(name='Stator', chip='Stationary', desc='Built just like the induction motor’s stator. Its three-phase coils create the rotating magnetic field.'),
    dict(name='Salient-pole rotor', chip='Rotating', desc='Its poles stick out like spokes. With DC current, each pole becomes a fixed North or South magnet.'),
    dict(name='Field winding', chip='Rotating', desc='Copper coils wound round each pole. DC current through them turns the poles into electromagnets.', note='Pole steel shown transparent'),
    dict(name='Damper (starting) bars', chip='Rotating', desc='Copper bars in the pole faces form a small cage. They start the motor and calm any swinging.', note='Pole steel shown transparent'),
    dict(name='Slip rings and brushes', desc='Rings on the shaft with carbon brushes pressing on them. They carry the DC into the spinning rotor.'),
    dict(name='DC excitation system', chip='Stationary', desc='This cabinet turns AC into controlled DC for the field winding. It sets how strong the rotor magnets are.'),
    dict(name='Shaft', chip='Rotating', desc='A forged steel shaft. It carries the heavy rotor and delivers the turning force to the machine.'),
    dict(name='Bearings', desc='Oil-lubricated sleeve bearings. A thin film of oil carries the heavy rotor, so the metal never touches.'),
    dict(name='Frame / housing', chip='Stationary', desc='A welded steel box. It holds the stator, bearings and cooler, and is bolted to the foundation.'),
    dict(name='Cooling system', desc='A shaft fan pushes warm air from inside through the cooler on top, where outside air carries the heat away.', note='Frame shown transparent'),
]
