"""PowerPoint-native animation toolkit (exec'd into the deck builder's globals).

Only standard PowerPoint effects are used: Fade/Appear entrance, Fade exit, Spin (with repeat), custom
motion paths. Everything on a slide runs on one timeline from the moment the slide appears ("With previous"
+ delay), so effects that must stay in step - a rotor locked onto the rotating field - start on exact
multiples of the field period.
"""
import itertools, math

P_NS = 'http://schemas.openxmlformats.org/presentationml/2006/main'

class Timeline:
    def __init__(self): self.fx = []
    def fade_in(self, shp, t, dur=500): self.fx.append(('in', shp, t, dur, {})); return self
    def appear(self, shp, t): self.fx.append(('appear', shp, t, 1, {})); return self
    def fade_out(self, shp, t, dur=500): self.fx.append(('out', shp, t, dur, {})); return self
    def wipe_in(self, shp, t, dur=600): self.fx.append(('wipe', shp, t, dur, {})); return self
    def spin(self, shp, t, period, turns=1.0, repeat=None, accel=0, decel=0, ccw=False):
        self.fx.append(('spin', shp, t, int(period * turns), dict(by=int(round((-1 if ccw else 1) * 21600000 * turns)), repeat=repeat, accel=accel, decel=decel))); return self
    def path(self, shp, t, dur, dx, dy, repeat=None):
        self.fx.append(('path', shp, t, dur, dict(dx=dx, dy=dy, repeat=repeat))); return self

    def write(self, slide):
        ids = itertools.count(1)
        root, seq, outer, grp = next(ids), next(ids), next(ids), next(ids)
        body = ''
        for n, (kind, shp, t, dur, o) in enumerate(sorted(self.fx, key=lambda f: f[2])):
            spid = shp.shape_id; node = 'afterEffect' if n == 0 else 'withEffect'
            eid = next(ids)
            tgt = f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
            vis = lambda v, d=0: (f'<p:set><p:cBhvr><p:cTn id="{next(ids)}" dur="1" fill="hold"><p:stCondLst><p:cond delay="{d}"/></p:stCondLst></p:cTn>{tgt}'
                                  f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="{v}"/></p:to></p:set>')
            extra = ''
            if kind == 'appear':
                head = 'presetID="1" presetClass="entr" presetSubtype="0" grpId="0"'; inner = vis('visible')
            elif kind == 'in':
                head = 'presetID="10" presetClass="entr" presetSubtype="0" grpId="0"'
                inner = vis('visible') + f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{next(ids)}" dur="{dur}"/>{tgt}</p:cBhvr></p:animEffect>'
            elif kind == 'wipe':
                head = 'presetID="22" presetClass="entr" presetSubtype="8" grpId="0"'
                inner = vis('visible') + f'<p:animEffect transition="in" filter="wipe(left)"><p:cBhvr><p:cTn id="{next(ids)}" dur="{dur}"/>{tgt}</p:cBhvr></p:animEffect>'
            elif kind == 'out':
                head = 'presetID="10" presetClass="exit" presetSubtype="0" grpId="1"'
                inner = f'<p:animEffect transition="out" filter="fade"><p:cBhvr><p:cTn id="{next(ids)}" dur="{dur}"/>{tgt}</p:cBhvr></p:animEffect>' + vis('hidden', dur - 1)
            elif kind == 'spin':
                head = 'presetID="8" presetClass="emph" presetSubtype="0" grpId="2"'
                if o['repeat']: extra += f' repeatCount="{o["repeat"]}"'
                if o['accel']: extra += f' accel="{int(o["accel"] * 100000)}"'
                if o['decel']: extra += f' decel="{int(o["decel"] * 100000)}"'
                inner = (f'<p:animRot by="{o["by"]}"><p:cBhvr><p:cTn id="{next(ids)}" dur="{dur}" fill="hold"/>{tgt}'
                         f'<p:attrNameLst><p:attrName>r</p:attrName></p:attrNameLst></p:cBhvr></p:animRot>')
            elif kind == 'path':
                head = 'presetID="0" presetClass="path" presetSubtype="0" grpId="3"'
                if o['repeat']: extra += f' repeatCount="{o["repeat"]}"'
                inner = (f'<p:animMotion origin="layout" path="M 0 0 L {o["dx"]:.5f} {o["dy"]:.5f} E" pathEditMode="relative" ptsTypes="AA">'
                         f'<p:cBhvr><p:cTn id="{next(ids)}" dur="{dur}" fill="hold"/>{tgt}'
                         f'<p:attrNameLst><p:attrName>ppt_x</p:attrName><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr></p:animMotion>')
            body += (f'<p:par><p:cTn id="{eid}" {head} fill="hold" nodeType="{node}"{extra}><p:stCondLst><p:cond delay="{int(t)}"/></p:stCondLst>'
                     f'<p:childTnLst>{inner}</p:childTnLst></p:cTn></p:par>')
        bld = ''
        seen = set()
        for kind, shp, t, dur, o in self.fx:
            el = shp._element
            if el.tag != qn('p:sp'): continue
            gid = {'in': '0', 'appear': '0', 'wipe': '0', 'out': '1', 'spin': '2', 'path': '3'}[kind]
            if (shp.shape_id, gid) in seen: continue
            seen.add((shp.shape_id, gid))
            tb = el.find(qn('p:nvSpPr')).find(qn('p:cNvSpPr')).get('txBox') == '1'
            bld += f'<p:bldP spid="{shp.shape_id}" grpId="{gid}"' + ('' if tb else ' animBg="1"') + '/>'
        xml = (f'<p:timing xmlns:p="{P_NS}"><p:tnLst><p:par><p:cTn id="{root}" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
               f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="{seq}" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
               f'<p:par><p:cTn id="{outer}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="{seq}"/></p:cond></p:stCondLst><p:childTnLst>'
               f'<p:par><p:cTn id="{grp}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>{body}</p:childTnLst></p:cTn></p:par>'
               f'</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
               f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
               f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
               f'</p:childTnLst></p:cTn></p:par></p:tnLst>' + (f'<p:bldLst>{bld}</p:bldLst>' if bld else '') + '</p:timing>')
        sld = slide._element; old = sld.find(qn('p:timing'))
        if old is not None: sld.remove(old)
        el = etree.fromstring(xml); ext = sld.find(qn('p:extLst'))
        (ext.addprevious(el) if ext is not None else sld.append(el))

# ---------------- drawing helpers ----------------
def _fill(shp, color, transp=0):
    if color is None: shp.fill.background()
    else:
        shp.fill.solid(); shp.fill.fore_color.rgb = color
        if transp:
            sf = shp.fill._xPr.find(qn('a:solidFill'))[0]
            a = etree.SubElement(sf, qn('a:alpha')); a.set('val', str(int((1 - transp) * 100000)))
def _line(shp, color=None, w=1.0):
    if color is None: shp.line.fill.background()
    else: shp.line.color.rgb = color; shp.line.width = Pt(w)
def shape(container, kind, cx, cy, w, h, fill=None, line=None, lw=1.0, rot=0, transp=0, name=None):
    s_ = container.add_shape(kind, Inches(cx - w / 2), Inches(cy - h / 2), Inches(w), Inches(h))
    _fill(s_, fill, transp); _line(s_, line, lw); s_.shadow.inherit = False; s_.rotation = rot
    if s_.has_text_frame: s_.text_frame.text = ''
    if name: s_.name = name
    return s_
def ghost_circle(container, cx, cy, r):
    """invisible circle that makes a group's bounding box symmetric about (cx, cy) so Spin turns it about that point"""
    return shape(container, MSO_SHAPE.OVAL, cx, cy, 2 * r, 2 * r)
def label_in(container, cx, cy, txt, size=14, color=None, bold=True, w=0.6, h=0.4):
    tb = container.add_textbox(Inches(cx - w / 2), Inches(cy - h / 2), Inches(w), Inches(h)); tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = MSO_ANCHOR.MIDDLE; tf.word_wrap = False
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; r = p.add_run(); r.text = txt
    r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color or DARK
    return tb
def polar(cx, cy, r, deg): return cx + r * math.cos(math.radians(deg)), cy - r * math.sin(math.radians(deg))

PHASE = [RGBColor(0xE0, 0x45, 0x3A), RGBColor(0xE0, 0xA1, 0x10), RGBColor(0x2F, 0x7F, 0xE0)]   # L1 red, L2 amber, L3 blue
NCOL, SCOL = RGBColor(0xD9, 0x3B, 0x30), RGBColor(0x2F, 0x6F, 0xD8)
STEEL, STEEL_D = RGBColor(0xC9, 0xD0, 0xD5), RGBColor(0x8F, 0x9A, 0xA1)
CU = RGBColor(0xC8, 0x6B, 0x32); ALU = RGBColor(0xB9, 0xC2, 0xC8)

def draw_stator(s, cx, cy, R, Rb, labels=True):
    """stator ring with three coil pairs (L1 at 90 deg, L2 at 210 deg, L3 at 330 deg; returns opposite)"""
    ring = shape(s.shapes, MSO_SHAPE.DONUT, cx, cy, 2 * R, 2 * R, fill=STEEL, line=STEEL_D, lw=1.25)
    ring.adjustments[0] = (R - Rb) / (2 * R)
    coils = []
    rc = (R + Rb) / 2
    for i, ang in enumerate((90, 210, 330)):
        for k, a in enumerate((ang, ang + 180)):
            x, y = polar(cx, cy, rc, a)
            c = shape(s.shapes, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, 0.62, 0.36, fill=PHASE[i], line=None, rot=90 - a, transp=0 if k == 0 else 0.45)
            coils.append((i, k, a, c))
        if labels:
            x, y = polar(cx, cy, R + 0.32, ang)
            label_in(s.shapes, x, y, f'L{i + 1}', size=12, color=PHASE[i])
    return ring, coils

def field_group(s, cx, cy, Rb, arrow=True):
    """rotating magnetic field: N and S pole glows on the bore rim + field arrow through the centre (spins as one)"""
    g = s.shapes.add_group_shape()
    ghost_circle(g.shapes, cx, cy, Rb)
    for a, col, t in ((90, NCOL, 'N'), (270, SCOL, 'S')):
        x, y = polar(cx, cy, Rb - 0.2, a)
        shape(g.shapes, MSO_SHAPE.OVAL, x, y, 1.25, 0.5, fill=col, transp=0.35)
        label_in(g.shapes, x, y, t, size=16, color=WHITE)
    if arrow:
        shape(g.shapes, MSO_SHAPE.UP_ARROW, cx, cy, 0.42, 2 * Rb - 1.5, fill=GREEN, transp=0.25)
    return g

def steps_panel(s, x, y, w, steps, size=15, gap=0.98):
    """numbered steps; returns list of (badge, text) shapes to fade in on the timeline"""
    out = []
    for i, st in enumerate(steps):
        yy = y + i * gap
        b = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(yy + 0.02), Inches(0.36), Inches(0.36)); _fill(b, GREEN); _line(b); b.shadow.inherit = False
        tf = b.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; r = p.add_run(); r.text = str(i + 1); r.font.size = Pt(12); r.font.bold = True; r.font.color.rgb = WHITE
        if isinstance(st, tuple): head, body = st; runs = [[(head, {'bold': True, 'color': DARK, 'size': size + 1})], [(body, {'size': size - 1.5})]]
        else: runs = st
        t = text(s, x + 0.55, yy - 0.02, w - 0.55, gap, runs, size=size, color=TXT, line=1.04, spacing=2)
        out.append((b, t))
    return out
