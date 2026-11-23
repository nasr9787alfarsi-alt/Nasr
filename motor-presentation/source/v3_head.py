"""Build 'Inside the Motor' v3 on the PDO corporate template: no video, native PowerPoint motion, optimized size."""
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
D3 = os.path.join(HERE, '..', 'deliver3')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(D3, 'raw.pptx')
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
def new(layout, key):
    s = prs.slides.add_slide(L[layout]); KEYS.append(key); return s

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
