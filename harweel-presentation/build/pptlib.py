"""Small helper layer over python-pptx for native, editable, animated slides.

- Shapes get explicit fills / lines / glows (no theme p:style), so they render
  identically everywhere.
- Animations are written as native PowerPoint timing XML (entrance, emphasis,
  looping motion paths), and slides get a native Morph transition.
"""
import math
from lxml import etree
from pptx.util import Emu
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
SW, SH = 13.333, 7.5  # slide size in inches


def E(v):
    return int(round(v * 914400))


def _frag(xml):
    root = etree.fromstring(f'<x xmlns:a="{NS_A}" xmlns:p="{NS_P}" xmlns:r="{NS_R}">{xml}</x>')
    return list(root)


# ---------------------------------------------------------------- colour xml
def clr(hexv, op=None, extra=""):
    a = f'<a:alpha val="{int(op * 1000)}"/>' if op is not None and op < 100 else ""
    return f'<a:srgbClr val="{hexv}">{a}{extra}</a:srgbClr>'


def fill_xml(f):
    if f is None:
        return "<a:noFill/>"
    if isinstance(f, str):
        return f"<a:solidFill>{clr(f)}</a:solidFill>"
    if isinstance(f, tuple):
        return f"<a:solidFill>{clr(f[0], f[1])}</a:solidFill>"
    # gradient dict
    gs = ""
    for st in f["stops"]:
        o = st[2] if len(st) > 2 else None
        gs += f'<a:gs pos="{int(st[0] * 1000)}">{clr(st[1], o)}</a:gs>'
    if f.get("path"):
        l, t, r, b = f.get("ftr", (50, 50, 50, 50))
        shade = (f'<a:path path="{f["path"]}"><a:fillToRect l="{l*1000}" t="{t*1000}" '
                 f'r="{r*1000}" b="{b*1000}"/></a:path>')
    else:
        shade = f'<a:lin ang="{int(f.get("ang", 90) * 60000)}" scaled="0"/>'
    return f'<a:gradFill flip="none" rotWithShape="1"><a:gsLst>{gs}</a:gsLst>{shade}</a:gradFill>'


def grad(*stops, ang=90, path=None, ftr=None):
    d = {"stops": stops, "ang": ang}
    if path:
        d["path"] = path
        d["ftr"] = ftr or (50, 50, 50, 50)
    return d


def ln_xml(line):
    if line is None:
        return "<a:ln><a:noFill/></a:ln>"
    hexv, w = line[0], line[1]
    op = line[2] if len(line) > 2 else None
    dash = line[3] if len(line) > 3 else None
    head = line[4] if len(line) > 4 else None
    tail = line[5] if len(line) > 5 else None
    x = f'<a:ln w="{int(w * 12700)}" cap="rnd"><a:solidFill>{clr(hexv, op)}</a:solidFill>'
    if dash:
        x += f'<a:prstDash val="{dash}"/>'
    x += "<a:round/>"
    if head:
        x += f'<a:headEnd type="{head}" w="med" len="med"/>'
    if tail:
        x += f'<a:tailEnd type="{tail}" w="med" len="med"/>'
    return x + "</a:ln>"


def style(shape, fill=None, line=None, glow=None, shadow=None, soft=None, bevel=None):
    sp = shape._element
    st = sp.find(qn("p:style"))
    if st is not None:
        sp.remove(st)
    spPr = sp.find(qn("p:spPr"))
    for tag in ("a:noFill", "a:solidFill", "a:gradFill", "a:blipFill", "a:pattFill",
                "a:grpFill", "a:ln", "a:effectLst", "a:scene3d", "a:sp3d"):
        for el in spPr.findall(qn(tag)):
            spPr.remove(el)
    xml = ""
    xml += fill_xml(fill)
    xml += ln_xml(line)
    eff = ""
    if glow:
        c, rad, op = glow
        eff += f'<a:glow rad="{int(rad * 12700)}">{clr(c, op)}</a:glow>'
    if shadow:
        blur, dist, ang, c, op = shadow
        eff += (f'<a:outerShdw blurRad="{int(blur * 12700)}" dist="{int(dist * 12700)}" '
                f'dir="{int(ang * 60000)}" algn="ctr" rotWithShape="0">{clr(c, op)}</a:outerShdw>')
    if soft:
        eff += f'<a:softEdge rad="{int(soft * 12700)}"/>'
    if eff:
        xml += f"<a:effectLst>{eff}</a:effectLst>"
    if bevel:
        xml += ('<a:scene3d><a:camera prst="orthographicFront"/><a:lightRig rig="threePt" dir="t"/>'
                f'</a:scene3d><a:sp3d><a:bevelT w="{int(bevel * 12700)}" h="{int(bevel * 12700 * 0.6)}"/></a:sp3d>')
    for el in _frag(xml):
        spPr.append(el)
    return shape


# ---------------------------------------------------------------- shapes
def _name(shape, name):
    if name:
        shape.name = name
    return shape


def rect(s, x, y, w, h, fill=None, line=None, name=None, kind=MSO_SHAPE.RECTANGLE, rot=0, adj=None, **kw):
    sh = s.shapes.add_shape(kind, E(x), E(y), E(w), E(h))
    if adj:
        for i, v in enumerate(adj):
            sh.adjustments[i] = v
    if rot:
        sh.rotation = rot
    style(sh, fill, line, **kw)
    return _name(sh, name)


def oval(s, cx, cy, rx, ry=None, fill=None, line=None, name=None, **kw):
    ry = rx if ry is None else ry
    return rect(s, cx - rx, cy - ry, 2 * rx, 2 * ry, fill, line, name, kind=MSO_SHAPE.OVAL, **kw)


def poly(s, pts, fill=None, line=None, name=None, closed=True, **kw):
    fb = s.shapes.build_freeform(E(pts[0][0]), E(pts[0][1]), scale=1.0)
    fb.add_line_segments([(E(x), E(y)) for x, y in pts[1:]], close=closed)
    sh = fb.convert_to_shape()
    style(sh, fill, line, **kw)
    return _name(sh, name)


def line(s, x1, y1, x2, y2, color, w=1.5, op=None, dash=None, head=None, tail=None, name=None, glow=None):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(x1), E(y1), E(x2), E(y2))
    style(c, None, (color, w, op, dash, head, tail), glow=glow)
    return _name(c, name)


def text(s, x, y, w, h, paras, size=14, color="FFFFFF", bold=False, align="l", anchor="t",
         name=None, spc=None, italic=False, lsp=None, wrap=True, after=0):
    """paras: str | list of paragraphs; paragraph = str | list of runs; run = str | (str, dict)."""
    tb = s.shapes.add_textbox(E(x), E(y), E(w), E(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    if isinstance(paras, str):
        paras = [paras]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
        if lsp:
            p.line_spacing = lsp
        if after:
            p.space_after = Emu(int(after * 12700))
        runs = [para] if isinstance(para, (str, tuple)) else para
        for r in runs:
            t, o = (r, {}) if isinstance(r, str) else r
            run = p.add_run()
            run.text = t
            f = run.font
            f.size = Emu(int(o.get("size", size) * 12700))
            f.bold = o.get("bold", bold)
            f.italic = o.get("italic", italic)
            f.color.rgb = RGBColor.from_string(o.get("color", color))
            sp = o.get("spc", spc)
            if sp:
                run._r.get_or_add_rPr().set("spc", str(int(sp * 100)))
            if o.get("baseline"):
                run._r.get_or_add_rPr().set("baseline", str(o["baseline"]))
    return _name(tb, name)


# ---------------------------------------------------------------- animation
class Anim:
    """Collects effects for one slide and writes native <p:timing>."""

    def __init__(self):
        self.fx = []

    def add(self, shape, kind, t=0, dur=600, **kw):
        self.fx.append(dict(sid=shape.shape_id, is_sp=shape._element.tag == qn("p:sp"),
                            kind=kind, t=int(t), dur=int(dur), **kw))
        return shape

    # convenience
    def fade(self, sh, t, dur=600):
        return self.add(sh, "fade", t, dur)

    def wipe(self, sh, t, dur=800, d="l"):
        return self.add(sh, "wipe", t, dur, d=d)

    def float(self, sh, t, dur=700):
        return self.add(sh, "float", t, dur)

    def zoom(self, sh, t, dur=500):
        return self.add(sh, "zoom", t, dur)

    def move(self, sh, t, dx, dy, dur=1500, repeat=True, rev=False, accel=0):
        """Motion path by (dx, dy) inches relative to the shape."""
        return self.add(sh, "path", t, dur, dx=dx / SW, dy=dy / SH, repeat=repeat, rev=rev, accel=accel)

    def spin(self, sh, t, deg, dur=2000):
        return self.add(sh, "spin", t, dur, deg=deg)

    def pulse(self, sh, t, scale=1.35, dur=900, repeat=True):
        return self.add(sh, "pulse", t, dur, scale=scale, repeat=repeat)

    def out(self, sh, t, dur=500):
        return self.add(sh, "out", t, dur)

    # ---- xml
    def xml(self):
        if not self.fx:
            return None
        n = [4]

        def nid():
            n[0] += 1
            return n[0]

        def tgt(sid):
            return f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl>'

        def setv(sid, val, delay=0):
            return (f'<p:set><p:cBhvr><p:cTn id="{nid()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="{delay}"/>'
                    f'</p:stCondLst></p:cTn>{tgt(sid)}<p:attrNameLst><p:attrName>style.visibility</p:attrName>'
                    f'</p:attrNameLst></p:cBhvr><p:to><p:strVal val="{val}"/></p:to></p:set>')

        def anim(sid, attr, v0, v1, dur, flt0=False):
            a = f'<p:fltVal val="{v0}"/>' if flt0 else f'<p:strVal val="{v0}"/>'
            return (f'<p:anim calcmode="lin" valueType="num"><p:cBhvr><p:cTn id="{nid()}" dur="{dur}" fill="hold"/>'
                    f'{tgt(sid)}<p:attrNameLst><p:attrName>{attr}</p:attrName></p:attrNameLst></p:cBhvr>'
                    f'<p:tavLst><p:tav tm="0"><p:val>{a}</p:val></p:tav><p:tav tm="100000"><p:val>'
                    f'<p:strVal val="{v1}"/></p:val></p:tav></p:tavLst></p:anim>')

        def effect(sid, flt, dur, transition="in"):
            return (f'<p:animEffect transition="{transition}" filter="{flt}"><p:cBhvr><p:cTn id="{nid()}" dur="{dur}"/>'
                    f'{tgt(sid)}</p:cBhvr></p:animEffect>')

        pars = []
        bld = []
        first = True
        for e in sorted(self.fx, key=lambda e: e["t"]):
            sid, k, d = e["sid"], e["kind"], e["dur"]
            node = "afterEffect" if first else "withEffect"
            first = False
            oid = nid()
            extra = ""
            if k in ("fade", "wipe", "float", "zoom"):
                cls = "entr"
                if k == "fade":
                    pid, sub = 10, 0
                    body = setv(sid, "visible") + effect(sid, "fade", d)
                elif k == "wipe":
                    pid = 22
                    sub, flt = {"l": (8, "wipe(left)"), "r": (2, "wipe(right)"),
                                "u": (4, "wipe(up)"), "d": (1, "wipe(down)")}[e["d"]]
                    body = setv(sid, "visible") + effect(sid, flt, d)
                elif k == "float":
                    pid, sub = 42, 0
                    body = (setv(sid, "visible") + effect(sid, "fade", d)
                            + anim(sid, "ppt_x", "#ppt_x", "#ppt_x", d)
                            + anim(sid, "ppt_y", "#ppt_y+0.05", "#ppt_y", d))
                else:
                    pid, sub = 53, 16
                    body = (setv(sid, "visible") + anim(sid, "ppt_w", 0, "#ppt_w", d, True)
                            + anim(sid, "ppt_h", 0, "#ppt_h", d, True) + effect(sid, "fade", d))
                if e["is_sp"]:
                    bld.append(sid)
            elif k == "out":
                cls, pid, sub = "exit", 10, 0
                body = effect(sid, "fade", d, "out") + setv(sid, "hidden", d - 1)
                if e["is_sp"]:
                    bld.append(sid)
            elif k == "path":
                cls, pid, sub = "path", 0, 0
                if e["repeat"]:
                    extra += ' repeatCount="indefinite"'
                if e["rev"]:
                    extra += ' autoRev="1"'
                if e["accel"]:
                    extra += f' accel="{e["accel"]}" decel="{e["accel"]}"'
                body = (f'<p:animMotion origin="layout" path="M 0 0 L {e["dx"]:.5f} {e["dy"]:.5f} E" '
                        f'pathEditMode="relative" ptsTypes="AA"><p:cBhvr><p:cTn id="{nid()}" dur="{d}" fill="hold"/>'
                        f'{tgt(sid)}<p:attrNameLst><p:attrName>ppt_x</p:attrName><p:attrName>ppt_y</p:attrName>'
                        f'</p:attrNameLst></p:cBhvr><p:rCtr x="0" y="0"/></p:animMotion>')
            elif k == "spin":
                cls, pid, sub = "emph", 8, 0
                extra += ' decel="60000"'
                body = (f'<p:animRot by="{int(e["deg"] * 60000)}"><p:cBhvr><p:cTn id="{nid()}" dur="{d}" fill="hold"/>'
                        f'{tgt(sid)}<p:attrNameLst><p:attrName>r</p:attrName></p:attrNameLst></p:cBhvr></p:animRot>')
            elif k == "pulse":
                cls, pid, sub = "emph", 6, 0
                if e["repeat"]:
                    extra += ' repeatCount="indefinite"'
                sc = int(e["scale"] * 100000)
                body = (f'<p:animScale><p:cBhvr><p:cTn id="{nid()}" dur="{d}" autoRev="1" fill="hold"/>'
                        f'{tgt(sid)}</p:cBhvr><p:by x="{sc}" y="{sc}"/></p:animScale>')
            else:
                raise ValueError(k)
            grp = ' grpId="0"' if k not in ("path", "spin", "pulse") else ' grpId="1"'
            pars.append(
                f'<p:par><p:cTn id="{oid}" presetID="{pid}" presetClass="{cls}" presetSubtype="{sub}" fill="hold"'
                f'{grp} nodeType="{node}"{extra}><p:stCondLst><p:cond delay="{e["t"]}"/></p:stCondLst>'
                f'<p:childTnLst>{body}</p:childTnLst></p:cTn></p:par>')
        seen = []
        for b in bld:
            if b not in seen:
                seen.append(b)
        bldx = "".join(f'<p:bldP spid="{b}" grpId="0" animBg="1"/>' for b in seen)
        return (
            '<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
            '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
            '<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0">'
            '<p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst><p:par><p:cTn id="4" fill="hold"><p:stCondLst>'
            '<p:cond delay="0"/></p:stCondLst><p:childTnLst>' + "".join(pars) +
            '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
            '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
            '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
            '</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>'
            + (f"<p:bldLst>{bldx}</p:bldLst>" if bldx else "") + "</p:timing>")


def finish_slide(slide, anim=None, transition="morph", dur=1600):
    sld = slide._element
    for tag in ("p:transition", "p:timing"):
        for el in sld.findall(qn(tag)):
            sld.remove(el)
    if transition == "morph":
        tx = ('<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
              '<mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159">'
              f'<p:transition xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" spd="slow" p14:dur="{dur}">'
              '<p159:morph option="byObject"/></p:transition></mc:Choice><mc:Fallback>'
              '<p:transition spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>')
    else:
        tx = ('<p:transition xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" '
              f'spd="slow" p14:dur="{dur}"><p:fade/></p:transition>')
    clr_map = sld.find(qn("p:clrMapOvr"))
    idx = list(sld).index(clr_map) + 1
    for el in reversed(_frag(tx)):
        sld.insert(idx, el)
    if anim is not None:
        x = anim.xml()
        if x:
            sld.append(_frag(x)[0])
