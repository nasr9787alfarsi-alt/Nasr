"""Build 'Harweel Field — From Subsurface to Surface' on the PDO corporate template.

Usage: python3 build_deck.py <template.pptx> <out.pptx>
Everything on the slides is native, editable PowerPoint geometry; motion is
native animation XML; slide-to-slide continuity uses the Morph transition.
"""
import json
import math
import os
import random
import sys

from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from shapely.geometry import box, shape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pptlib import (E, SH, SW, Anim, _frag, fill_xml, finish_slide, grad, line, oval, poly, rect,  # noqa: E402
                    style, text)

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE, OUT = sys.argv[1], sys.argv[2]
WORK = os.path.join(os.path.dirname(os.path.abspath(OUT)), "_work")
os.makedirs(WORK, exist_ok=True)
random.seed(7)

# ------------------------------------------------------------------ palette
INK, MUTED, DIM = "F3F8F7", "A7C2BE", "5F827D"
GREEN, TEAL, LGREEN, LTEAL = "00B477", "089AA2", "76DFA5", "59BDC2"   # PDO brand
PANEL, PANEL2, RULE = "0E3030", "143B3B", "2B5A57"
OIL, OIL_HI, OIL_D = "F2A93B", "FFD27A", "9A5A17"
GAS, GAS_HI = "5FD4E6", "B9F1FA"
RABAB = "9BE8C9"
RED, H2S = "E8453C", "F5CF3E"


def dk(h, f=0.72):
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "%02X%02X%02X" % (int(r * f), int(g * f), int(b * f))


# ------------------------------------------------------------------ template
prs = Presentation(TEMPLATE)
lst = prs.slides._sldIdLst
for sid in list(lst):
    prs.part.drop_rel(sid.rId)
    lst.remove(sid)

media = {}
tz = __import__("zipfile").ZipFile(TEMPLATE)
for n in ("image47.png", "image10.png"):
    p = os.path.join(WORK, n)
    open(p, "wb").write(tz.read("ppt/media/" + n))
    media[n] = p

# faint engineering dot-grid (echoes the source video's graph-paper look)
grid_png = os.path.join(WORK, "dotgrid.png")
im = Image.new("RGBA", (1600, 900), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
for gx in range(20, 1600, 40):
    for gy in range(20, 900, 40):
        d.ellipse([gx - 1.3, gy - 1.3, gx + 1.3, gy + 1.3], fill=(150, 210, 200, 34))
im.save(grid_png, optimize=True)

BG = fill_xml(grad((0, "0F3A39"), (55, "072423"), (100, "031312"), path="circle", ftr=(20, 10, 80, 90)))


def layout_named(prefix):
    return [l for l in prs.slide_layouts if l.name.startswith(prefix)][0]


def add_pic_xml(part, sp_tree, path, x, y, w, h, name, at_back=True):
    _, rid = part.get_or_add_image_part(path)
    pic = _frag(
        f'<p:pic><p:nvPicPr><p:cNvPr id="{9000 + len(sp_tree)}" name="{name}" descr="{name}"/><p:cNvPicPr>'
        f'<a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr userDrawn="1"/></p:nvPicPr><p:blipFill>'
        f'<a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr><a:xfrm>'
        f'<a:off x="{E(x)}" y="{E(y)}"/><a:ext cx="{E(w)}" cy="{E(h)}"/></a:xfrm><a:prstGeom prst="rect">'
        f'<a:avLst/></a:prstGeom></p:spPr></p:pic>')[0]
    if at_back:
        sp_tree.insert(2, pic)
    else:
        sp_tree.append(pic)


# --- turn the template's "Short Title" layout into the dark Harweel layout
DARK = layout_named("Short Title")
DARK._element.cSld.set("name", "Harweel Dark - Title Only")
cs = DARK._element.cSld
cs.insert(0, _frag(f"<p:bg><p:bgPr>{BG}<a:effectLst/></p:bgPr></p:bg>")[0])
tree = cs.find(qn("p:spTree"))
for sp in list(tree):
    nm = sp.find(".//" + qn("p:cNvPr"))
    if nm is not None and nm.get("name") == "Freeform 41":
        tree.remove(sp)  # light corner swoosh -> not needed on dark
    if nm is not None and nm.get("name") == "Picture 7":
        _, rid = DARK.part.get_or_add_image_part(media["image47.png"])  # white "For Oman | PDO" lockup
        blip = sp.find(".//" + qn("a:blip"))
        old = blip.get(qn("r:embed"))
        blip.set(qn("r:embed"), rid)
        DARK.part.drop_rel(old)
        off = sp.find(".//" + qn("a:xfrm") + "/" + qn("a:off"))
        ext = sp.find(".//" + qn("a:xfrm") + "/" + qn("a:ext"))
        off.set("x", str(E(10.62))), off.set("y", str(E(0.22)))
        ext.set("cx", str(E(2.25))), ext.set("cy", str(E(2.25 * 886 / 2208)))
    if nm is not None and nm.get("name") == "Title 7":
        off = sp.find(".//" + qn("a:xfrm") + "/" + qn("a:off"))
        ext = sp.find(".//" + qn("a:xfrm") + "/" + qn("a:ext"))
        off.set("x", str(E(0.62))), off.set("y", str(E(0.74)))
        ext.set("cx", str(E(9.6))), ext.set("cy", str(E(0.8)))
        bp = sp.find(".//" + qn("a:bodyPr"))
        for c in list(bp):
            bp.remove(c)
        bp.set("lIns", "0"), bp.set("tIns", "0"), bp.set("rIns", "0"), bp.set("bIns", "0")
        bp.set("anchor", "t")
        for sc in sp.iter(qn("a:schemeClr")):
            sc.set("val", "bg1")
        for sc in sp.iter(qn("a:srgbClr")):
            sc.set("val", "FFFFFF")
        for el in sp.iter(qn("a:defRPr")):
            el.set("sz", "3200")
        for el in sp.iter(qn("a:rPr")):
            el.set("sz", "3200")
    if nm is not None and nm.get("name") == "Slide Number Placeholder 1":
        tree.remove(sp)
add_pic_xml(DARK.part, tree, grid_png, 0, 0, SW, SH, "Engineering dot grid")
THANKS = layout_named("Thank You")

# ------------------------------------------------------------------ helpers
YEARS = [1997, 2004, 2014, 2019, 2024]
TLX0, TLX1, TLY = 0.62, 6.0, 7.02


def tl_x(year):
    return TLX0 + YEARS.index(year) * (TLX1 - TLX0) / (len(YEARS) - 1)


def timeline(s, year):
    line(s, TLX0, TLY, TLX1, TLY, RULE, 1.5, name="!!tl_base")
    xm = tl_x(year)
    line(s, TLX0, TLY, max(xm, TLX0 + 0.01), TLY, GREEN, 2.25, name="!!tl_fill")
    for i, y in enumerate(YEARS):
        x = tl_x(y)
        done = y <= year
        oval(s, x, TLY, 0.045, fill=GREEN if done else RULE, name=f"!!tl_dot{i}")
        text(s, x - 0.4, TLY - 0.3, 0.8, 0.2, str(y), size=9 if y != year else 10,
             color=INK if y == year else DIM, bold=y == year, align="c", name=f"!!tl_lab{i}")
    oval(s, xm, TLY, 0.11, fill=None, line=(LGREEN, 1.75), glow=(GREEN, 6, 60), name="!!tl_mark")


def base(title, kicker, year=None, lead=None, lead_w=9.4):
    s = prs.slides.add_slide(DARK)
    s.shapes.title.text = title
    text(s, 0.62, 0.42, 8, 0.28, kicker.upper(), size=12, color=GREEN, bold=True, spc=2.2, name="!!kicker")
    if lead:
        text(s, 0.62, 1.48, lead_w, 0.5, lead, size=16, color=MUTED, name="!!lead")
    if year:
        timeline(s, year)
    return s, Anim()


def notes(s, dur, visual, script, flags=None):
    t = f"[≈ {dur} sec]\n\nVISUAL / ANIMATION OBJECTIVE:\n{visual}\n\nPRESENTER SCRIPT:\n{script}"
    if flags:
        t += "\n\nACCURACY NOTES:\n" + flags
    s.notes_slide.notes_text_frame.text = t


def card(s, x, y, w, h, name=None, op=88, line_c=RULE):
    return rect(s, x, y, w, h, fill=(PANEL, op), line=(line_c, 0.75), name=name,
                kind=MSO_SHAPE.ROUNDED_RECTANGLE, adj=[0.12])


def badge(s, cx, cy, n, color=GREEN, name=None, r=0.19):
    b = oval(s, cx, cy, r, fill=color, glow=(color, 5, 45), name=name)
    tb = b.text_frame
    tb.margin_left = tb.margin_right = tb.margin_top = tb.margin_bottom = 0
    p = tb.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    tb.vertical_anchor = MSO_ANCHOR.MIDDLE
    run = p.add_run()
    run.text = str(n)
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = RGBColor.from_string("06211F")
    return b


def sphere(s, cx, cy, r, hi, mid, lo, name=None, glow=None):
    return oval(s, cx, cy, r, fill=grad((0, hi), (45, mid), (100, lo), path="circle", ftr=(30, 28, 70, 72)),
                name=name, glow=glow)


def flow(s, A, p0, p1, spacing, color, r=0.045, step_ms=900, t=0, name="flow", glow=True, op=None):
    """Seamless looping particle stream from p0 to p1 (each particle travels one spacing, forever)."""
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    n = max(1, int(L / spacing))
    out = []
    for k in range(n):
        cx, cy = x0 + ux * spacing * k, y0 + uy * spacing * k
        f = color if op is None else (color, op)
        d = oval(s, cx, cy, r, fill=f, glow=(color, 4, 55) if glow else None, name=f"{name}_{k}")
        A.fade(d, t + 40 * k, 300)
        A.move(d, t + 400, ux * spacing, uy * spacing, dur=step_ms)
        out.append(d)
    return out


# ---- 3-D earth block --------------------------------------------------------
STRATA = [  # key, thickness, front top colour, front bottom colour, kind, label
    ("sand", 0.22, "EDD39F", "D2AF6E", "sand"),
    ("rock1", 0.52, "8C6C4E", "7B5D43", "rock"),
    ("rock2", 0.48, "715540", "604735", "rock"),
    ("rock3", 0.44, "5C4332", "4D3729", "rock"),
    ("salt1", 0.38, "E8EFF3", "C5D3DC", "salt"),
    ("oil1", 0.30, "5E3D21", "3F2715", "oil"),
    ("salt2", 0.38, "DFE8EE", "BCCAD4", "salt"),
    ("oil2", 0.30, "5E3D21", "3F2715", "oil"),
    ("salt3", 0.42, "D5E0E7", "B0C0CB", "salt"),
]


def earth_block(s, A, x, y, w, sc=1.0, dx=1.2, dy=0.62, pre="!!blk", t0=None, particles=True, jiggle=True):
    """Oblique 3-D cut-away of the Harweel stack. Returns layer y-ranges."""
    ys = {}
    yy = y
    top = poly(s, [(x, y), (x + w, y), (x + w + dx, y - dy), (x + dx, y - dy)],
               fill=grad((0, "F6E2B4"), (100, "D9B77A"), ang=90), line=("FFF3D6", 0.5, 60), name=pre + "_top")
    # ripples on the desert surface
    for i in range(4):
        fx = 0.18 + i * 0.2
        line(s, x + dx * fx + w * 0.08, y - dy * fx, x + dx * fx + w * 0.92, y - dy * fx, "C29A5E", 0.75, 55,
             name=f"{pre}_dune{i}")
    shapes_by_layer = [[top]]
    for key, th, c0, c1, kind in STRATA:
        th *= sc
        fr = rect(s, x, yy, w, th, fill=grad((0, c0), (100, c1), ang=90), line=(dk(c1, 0.8), 0.5, 70),
                  name=f"{pre}_{key}_f")
        sd = poly(s, [(x + w, yy), (x + w + dx, yy - dy), (x + w + dx, yy - dy + th), (x + w, yy + th)],
                  fill=grad((0, dk(c0, 0.74)), (100, dk(c1, 0.62)), ang=90), line=(dk(c1, 0.55), 0.5, 70),
                  name=f"{pre}_{key}_s")
        grp = [fr, sd]
        if kind == "rock":
            for j in range(2):
                ly = yy + th * (0.35 + 0.33 * j)
                grp.append(line(s, x + 0.05, ly, x + w - 0.05, ly + 0.02, dk(c1, 0.75), 0.75, 70,
                                name=f"{pre}_{key}_l{j}"))
        if kind == "oil":
            fr2 = rect(s, x, yy, w, th, fill=grad((0, OIL, 0), (50, OIL, 22), (100, OIL, 0), ang=90),
                       name=f"{pre}_{key}_glow")
            grp.append(fr2)
            if particles:
                k = 0
                for col in range(int(w / 0.19)):
                    for row in range(2):
                        px = x + 0.12 + col * 0.19 + (0.09 if row else 0) + random.uniform(-0.03, 0.03)
                        py = yy + th * (0.32 + 0.38 * row) + random.uniform(-0.02, 0.02)
                        if px > x + w - 0.08:
                            continue
                        rr = random.uniform(0.028, 0.045) * max(sc, 0.8)
                        dd = oval(s, px, py, rr, fill=random.choice([OIL, OIL_HI, OIL]),
                                  name=f"{pre}_{key}_p{k}")
                        grp.append(dd)
                        if jiggle and k % 2 == 0:
                            A.move(dd, (t0 or 0) + 2600, random.uniform(-0.03, 0.03), random.uniform(-0.02, 0.02),
                                   dur=random.randint(900, 1500), rev=True)
                        k += 1
        ys[key] = (yy, yy + th)
        shapes_by_layer.append(grp)
        yy += th
    if t0 is not None:
        for i, grp in enumerate(shapes_by_layer):
            for shp in grp:
                A.wipe(shp, t0 + i * 160, 450, d="d")
    ys["bottom"] = yy
    ys["x1"] = x + w
    ys["dx"], ys["dy"] = dx, dy
    return ys


# ---- isometric primitives ----------------------------------------------------
C30 = math.cos(math.radians(30))


class Iso:
    def __init__(self, ox, oy, s):
        self.ox, self.oy, self.s = ox, oy, s

    def p(self, x, y, z=0):
        return (self.ox + (x - y) * C30 * self.s, self.oy + (x + y) * 0.5 * self.s - z * self.s)

    def box(self, sl, x, y, z, w, d, h, top, side_r, side_l, name, line_c=None, glow=None):
        P = self.p
        lc = (line_c, 0.5, 60) if line_c else None
        a = poly(sl, [P(x, y + d, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x, y + d, z + h)],
                 fill=side_l, line=lc, name=name + "_l")
        b = poly(sl, [P(x + w, y, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x + w, y, z + h)],
                 fill=side_r, line=lc, name=name + "_r")
        c = poly(sl, [P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)],
                 fill=top, line=lc, name=name + "_t", glow=glow)
        return [a, b, c]

    def cyl(self, sl, x, y, z, r, h, c_hi, c_mid, c_lo, name):
        cx, cy = self.p(x, y, z)
        rx, ry = r * self.s * 1.2247, r * self.s * 0.7071
        hh = h * self.s
        a = oval(sl, cx, cy, rx, ry, fill=c_lo, name=name + "_b")
        b = rect(sl, cx - rx, cy - hh, 2 * rx, hh,
                 fill=grad((0, c_lo), (35, c_hi), (70, c_mid), (100, c_lo), ang=0), name=name + "_m")
        c = oval(sl, cx, cy - hh, rx, ry, fill=grad((0, c_hi), (100, c_mid), ang=90), line=(c_lo, 0.5),
                 name=name + "_t")
        return [a, b, c]


# ---- map helpers ---------------------------------------------------------------
GEO = json.load(open(os.path.join(HERE, "geo_region.json")))


def draw_map(s, bbox, frame, countries, styles, pre):
    lon0, lat0, lon1, lat1 = bbox
    fx, fy, fw, fh = frame
    clip = box(lon0, lat0, lon1, lat1)

    def pr(lon, lat):
        return (fx + (lon - lon0) / (lon1 - lon0) * fw, fy + (lat1 - lat) / (lat1 - lat0) * fh)

    out = []
    for c in countries:
        g = shape(GEO[c]).intersection(clip)
        if g.is_empty:
            continue
        polys = [g] if g.geom_type == "Polygon" else [q for q in getattr(g, "geoms", []) if q.geom_type == "Polygon"]
        for i, pg in enumerate(polys):
            if pg.area < 0.002:
                continue
            pts = [pr(*c2) for c2 in list(pg.exterior.coords)[:-1]]
            f, l, gl = styles[c]
            out.append(poly(s, pts, fill=f, line=l, glow=gl, name=f"{pre}_{c.replace(' ', '')}{i}"))
    return pr, out


# =================================================================== SLIDE 1 — cover
s = prs.slides.add_slide(DARK)
s._element.set("showMasterSp", "0")
A = Anim()
add_pic_xml(s.part, s.shapes._spTree, grid_png, 0, 0, SW, SH, "Engineering dot grid")
s.shapes.add_picture(media["image10.png"], E(0.62), E(0.5), E(4.1))
ys = earth_block(s, A, 7.15, 2.55, 4.15, sc=1.05, dx=1.35, dy=0.72, pre="cov", t0=300)
# a well reaching down into the oil-bearing layers
wx = 7.15 + 4.15 * 0.55
wl = line(s, wx, 2.55 - 0.36, wx, ys["oil2"][0] + 0.15, "DDE7EA", 2.25, name="cov_well")
A.wipe(wl, 2100, 900, d="d")
tip = oval(s, wx, ys["oil2"][0] + 0.15, 0.09, fill=OIL_HI, glow=(OIL, 12, 70), name="cov_tip")
A.zoom(tip, 2900, 400)
A.pulse(tip, 3400, 1.5, 900)
rig = rect(s, wx - 0.08, 1.78, 0.16, 0.42, fill=grad((0, "8E9CA3"), (50, "EEF3F5"), (100, "8E9CA3"), ang=0),
           name="cov_rig")
rig2 = rect(s, wx - 0.2, 1.95, 0.4, 0.09, fill=GREEN, name="cov_rig2")
A.fade(rig2, 2000, 500)
A.fade(rig, 2000, 500)
t = s.shapes.title
t.left, t.top, t.width, t.height = E(0.62), E(2.3), E(6.5), E(1.7)
t.text_frame.text = "HARWEEL FIELD"
r0 = t.text_frame.paragraphs[0].runs[0]
r0.font.size = Pt(54)
r0._r.get_or_add_rPr().set("spc", "200")
p2 = t.text_frame.add_paragraph()
r1 = p2.add_run()
r1.text = "From Subsurface to Surface"
r1.font.size = Pt(28)
r1.font.color.rgb = RGBColor.from_string(LGREEN)
r1.font.bold = False
tg = text(s, 0.62, 4.35, 5.6, 0.9,
          "How oil sealed in salt, three to five kilometres beneath southern Oman, became energy for the south.",
          size=16, color=MUTED, name="cov_tag")
A.fade(tg, 1200, 800)
text(s, 0.62, 6.75, 6, 0.3, "Petroleum Development Oman  ·  Technical briefing", size=11, color=DIM, name="cov_foot")
finish_slide(s, A, transition="fade", dur=1200)
notes(s, 20,
      "Cinematic opening. The 3-D earth block assembles layer by layer from the surface down; a well then drills "
      "into the deepest oil-bearing layer and its tip glows. Sets up the whole journey: subsurface -> surface.",
      "Good morning, everyone. Over the next few minutes I'd like to take you on a journey — from three to five "
      "kilometres beneath the desert of southern Oman, all the way up to the gas that reaches Salalah today. "
      "This is the story of Harweel field: what makes it unusual, why it was so hard to produce, and the idea "
      "that unlocked it.")

# =================================================================== SLIDE 2 — discovery map
s, A = base("Hidden beneath southern Oman", "Discovery · 1997", 1997)
bbox = (48.8, 16.4, 61.86, 26.6)
frame = (6.55, 1.55, 6.2, 5.0)
mapc = rect(s, *frame, fill=grad((0, "0C3437"), (100, "072325"), ang=90), line=(RULE, 0.75), name="!!map_card",
            kind=MSO_SHAPE.ROUNDED_RECTANGLE, adj=[0.03])
pr, land = draw_map(s, bbox, frame, ["Saudi Arabia", "Yemen", "United Arab Emirates", "Iran", "Qatar", "Oman"], {
    **{c: ("173F3F", ("2E5E5B", 0.5), None) for c in ["Saudi Arabia", "Yemen", "United Arab Emirates", "Iran", "Qatar"]},
    "Oman": (grad((0, "1E7A63"), (100, "0F5249"), ang=60), (LGREEN, 1.25), (GREEN, 5, 35))}, "map")
for sh in land:
    if "Oman" in sh.name:
        A.fade(sh, 200, 900)
hx, hy = pr(54.65, 17.75)
mx, my = pr(58.41, 23.59)
sx, sy = pr(54.09, 17.02)
text(s, pr(55.6, 21.0)[0], pr(55.6, 21.0)[1], 1.4, 0.35, "OMAN", size=18, color="CFEFE3", bold=True, spc=4,
     name="map_oman")
text(s, pr(57.6, 17.3)[0], pr(57.6, 17.3)[1], 1.6, 0.3, "Arabian Sea", size=11, color=LTEAL, italic=True,
     name="map_sea")
oval(s, mx, my, 0.05, fill=INK, name="map_muscat")
text(s, mx + 0.1, my - 0.12, 0.9, 0.25, "Muscat", size=10, color=INK, name="map_muscat_l")
oval(s, sx, sy, 0.04, fill=INK, name="map_salalah")
text(s, sx - 0.85, sy + 0.02, 0.8, 0.25, "Salalah", size=10, color=INK, align="r", name="map_salalah_l")
ring = oval(s, hx, hy, 0.2, fill=None, line=(RED, 1.5), name="!!pin_ring")
A.zoom(ring, 1500, 400)
A.pulse(ring, 1900, 1.6, 1000)
pin = oval(s, hx, hy, 0.09, fill=RED, glow=(RED, 8, 60), name="!!pin")
A.zoom(pin, 1300, 400)
lab = text(s, hx + 0.28, hy - 0.42, 2.0, 0.5, [[("Harweel", {"bold": True, "size": 14})],
                                               [("approximate location", {"size": 9, "color": MUTED})]],
           color=INK, name="pin_label")
A.float(lab, 1700, 600)
text(s, 0.62, 2.25, 4, 1.2, "1997", size=80, color=INK, bold=True, name="!!bignum")
body = text(s, 0.62, 3.6, 5.4, 1.4,
            [[("Petroleum Development Oman ", {"bold": True, "color": INK}),
              ("finds oil under the sands of southern Oman — hidden in a way that is genuinely unusual.", {})]],
            size=18, color=MUTED, lsp=1.1, name="s2_body")
A.float(body, 600, 700)
chips = [("Southern Oman", 0.62), ("Discovered by PDO", 2.55), ("Onshore", 4.6)]
for i, (c, x) in enumerate(chips):
    ch = rect(s, x, 5.25, 1.8 if i < 2 else 1.1, 0.42, fill=(PANEL2, 90), line=(TEAL, 0.75),
              kind=MSO_SHAPE.ROUNDED_RECTANGLE, adj=[0.5], name=f"s2_chip{i}")
    A.fade(ch, 1000 + i * 150, 400)
    tt = text(s, x, 5.25, 1.8 if i < 2 else 1.1, 0.42, c, size=12, color=LGREEN, align="c", anchor="m",
              name=f"s2_chip{i}_t")
    A.fade(tt, 1000 + i * 150, 400)
finish_slide(s, A)
notes(s, 25,
      "Morph from the cover; Oman lights up and a red pin drops on the Harweel area with a pulsing ring. "
      "Timeline at the bottom starts at 1997 — it will travel with us through the story.",
      "In 1997, beneath the sands of southern Oman, Petroleum Development Oman found oil. But this was not an "
      "ordinary discovery — the oil was hidden in a very unusual way. The field is called Harweel, and it lies in "
      "the south of the country. Keep an eye on the timeline at the bottom: it will follow us from 1997 to today.",
      "Location is approximate, as in the source video. 'Onshore' is evident from the source (desert setting).")

# =================================================================== SLIDE 3 — trapped in salt
s, A = base("Trapped between layers of salt", "The reservoir", 1997,
            "Oil sits in rock layers sealed inside salt — three to five kilometres below the desert.")
BX, BY, BW = 2.45, 2.75, 5.4
ys = earth_block(s, A, BX, BY, BW, sc=1.0, dx=1.25, dy=0.62, t0=200)
# depth ruler
rx = BX - 0.55
rl = line(s, rx, BY, rx, ys["bottom"], MUTED, 1, name="!!ruler")
A.wipe(rl, 300, 1500, d="d")
for yv, lb in [(BY, "Surface"), (ys["oil1"][0], "≈ 3 km"), (ys["oil2"][1], "≈ 5 km")]:
    tk = line(s, rx - 0.08, yv, rx + 0.08, yv, MUTED, 1, name=f"!!tick{lb}")
    tl = text(s, rx - 1.75, yv - 0.13, 1.6, 0.26, lb, size=11, color=MUTED, align="r", name=f"!!tickl{lb}")
    A.fade(tk, 1700, 400), A.fade(tl, 1700, 400)
br = rect(s, rx - 0.02, ys["oil1"][0], 0.06, ys["oil2"][1] - ys["oil1"][0], fill=OIL, glow=(OIL, 6, 60),
          name="!!ruler_oil")
A.wipe(br, 2300, 700, d="d")
# callouts
LX = BX + BW + 1.25 + 0.35
calls = [("Desert sand", "sand", INK), ("Rock layers", "rock2", INK), ("Salt — a tight seal", "salt1", "DCE8EE"),
         ("Oil-bearing rock", "oil1", OIL_HI), ("Salt", "salt2", "DCE8EE"), ("Oil-bearing rock", "oil2", OIL_HI),
         ("Salt", "salt3", "DCE8EE")]
for i, (lb, key, col) in enumerate(calls):
    y0, y1 = ys[key]
    ym = (y0 + y1) / 2 - 0.31
    ld = line(s, BX + BW + 1.25 - 0.05, ym, LX - 0.08, ym, col, 0.75, 70, name=f"call_l{i}")
    tt = text(s, LX, ym - 0.14, 3.0, 0.28, lb, size=13, color=col, bold=key.startswith("oil"), name=f"call_t{i}")
    A.fade(ld, 2600 + i * 180, 300), A.fade(tt, 2600 + i * 180, 400)
nt = text(s, LX, 6.3, 3.2, 0.25, "Schematic · not to scale", size=10, color=DIM, italic=True, name="s3_nts")
lens_hint = None
finish_slide(s, A)
notes(s, 35,
      "Camera 'cuts the earth open': the 3-D block builds from the surface down — sand, rock, salt — then the "
      "glowing oil-bearing layers appear, sealed between salt. The depth ruler highlights the 3–5 km oil zone. "
      "Oil droplets shimmer gently to show the layers hold fluid.",
      "Here is what makes Harweel unusual. Let's cut the earth open. At the top is desert sand. Below it, "
      "kilometres of ordinary rock. Then — salt. And sandwiched inside that salt are layers of rock that hold the "
      "oil, at a depth of three to five kilometres. Salt is an excellent seal: fluids can't pass through it, which "
      "is why the oil stayed locked in place for so long.",
      "'Oil trapped in rocks between salt layers, 3–5 km deep' is from the source. 'Salt acts as a seal' is "
      "general geological context added to aid understanding. Layer count and thicknesses are illustrative.")

# =================================================================== SLIDE 4 — 540 million years
s, A = base("Older than almost any oil on Earth", "Deep time", 1997)
ys = earth_block(s, A, 0.95, 2.95, 3.9, sc=0.82, dx=1.0, dy=0.5, particles=True, jiggle=False)
rl = line(s, 0.95 - 0.4, 2.95, 0.95 - 0.4, ys["bottom"], MUTED, 1, name="!!ruler")
br = rect(s, 0.95 - 0.42, ys["oil1"][0], 0.06, ys["oil2"][1] - ys["oil1"][0], fill=OIL, glow=(OIL, 6, 60),
          name="!!ruler_oil")
n540 = text(s, 6.55, 1.75, 4.2, 1.5, "540", size=110, color=OIL_HI, bold=True, name="!!bignum")
A.zoom(n540, 300, 700)
sub = text(s, 6.6, 3.3, 6.3, 0.5, "million years: the age of Harweel's source rocks", size=19, color=INK,
           name="s4_sub")
A.fade(sub, 900, 600)
b4 = text(s, 6.6, 3.85, 6.0, 0.8, "That places Harweel among the oldest commercially produced oil in the world.",
          size=16, color=MUTED, name="s4_body")
A.fade(b4, 1300, 600)
# deep-time bar (to scale: 540 Ma -> today)
X0, X1, YB = 6.6, 12.6, 5.55
tb = rect(s, X0, YB - 0.05, X1 - X0, 0.1, fill=grad((0, OIL), (60, TEAL), (100, GREEN), ang=0), name="s4_bar",
          kind=MSO_SHAPE.ROUNDED_RECTANGLE, adj=[0.5])
A.wipe(tb, 1800, 1400, d="l")
for ma, lb, col, up in [(540, "Source rocks form\n≈ 540 million years ago", OIL_HI, True),
                        (230, "First dinosaurs\n≈ 230 million years ago", MUTED, False),
                        (0, "Today", LGREEN, True)]:
    xx = X0 + (540 - ma) / 540 * (X1 - X0)
    dd = oval(s, xx, YB, 0.1, fill=col, glow=(col, 5, 50), name=f"s4_m{ma}")
    al = "l" if ma == 540 else ("r" if ma == 0 else "c")
    tx = xx if al == "l" else (xx - 2.6 if al == "r" else xx - 1.3)
    tt = text(s, tx, YB - 0.75 if up else YB + 0.2, 2.6, 0.55, lb, size=11, color=col, align=al,
              anchor="b" if up else "t", name=f"s4_t{ma}")
    A.fade(dd, 2400 + (540 - ma) * 3, 400), A.fade(tt, 2500 + (540 - ma) * 3, 400)
finish_slide(s, A)
notes(s, 25,
      "Morph: the earth block glides to the left and shrinks, keeping the visual thread. A giant '540' zooms in, "
      "then a to-scale deep-time bar runs from 540 million years ago to today, with the first dinosaurs as a "
      "reference point so the audience can feel the age.",
      "And this oil is old. The source rocks that generated it formed about 540 million years ago. To put that "
      "in perspective: the first dinosaurs appeared roughly 230 million years ago — Harweel's source rocks were "
      "already more than twice that age. It is among the oldest commercial oil anywhere in the world.",
      "540 million years and 'among the oldest commercial oil in the world' are from the source. The dinosaur "
      "reference (~230 Ma) is general context added for scale.")

# =================================================================== SLIDE 5 — cluster
s, A = base("One discovery became a cluster", "The Harweel cluster", 2004,
            "Similar fields were found nearby. Together they are known as the Harweel cluster.", lead_w=6.2)
iso = Iso(3.55, 2.75, 0.72)
plate = iso.box(s, -0.3, -0.3, -0.18, 5.0, 5.0, 0.18, grad((0, "164341"), (100, "0F3433")),
                "0B2828", "0D2E2E", "!!plate", line_c=RULE)
fields = [("Harweel", 0, 0), ("Zalzala", 2.5, 0), ("Sakhiya", 0, 2.5), ("Dafiq", 2.5, 2.5)]
for i, (nm, fx_, fy_) in enumerate(fields):
    hot = nm == "Zalzala"
    top = grad((0, "2BD397"), (100, GREEN)) if hot else grad((0, "2E6B66"), (100, "22524E"))
    faces = iso.box(s, fx_, fy_, 0, 1.9, 1.9, 0.45 if hot else 0.3, top, "0B7A55" if hot else "173F3C",
                    "0E6748" if hot else "1B4744", f"!!tile{i}", line_c="3E7C76" if not hot else LGREEN,
                    glow=(GREEN, 8, 45) if hot else None)
    for j, f in enumerate(faces):
        A.wipe(f, 300 + i * 250 + j * 60, 500, d="u")
    cx, cy = iso.p(fx_ + 0.95, fy_ + 0.95, 0.45 if hot else 0.3)
    tt = text(s, cx - 1.0, cy - 0.17, 2.0, 0.34, nm, size=15 if hot else 14, color="06211F" if hot else INK,
              bold=True, align="c", anchor="m", name=f"!!tile{i}_lab")
    A.fade(tt, 600 + i * 250, 400)
cx, cy = iso.p(3.45, 0.95, 0.45)
drop = rect(s, cx - 0.2, cy - 1.25, 0.4, 0.4, fill=grad((0, OIL_HI), (100, OIL_D), ang=45), rot=-45,
            kind=MSO_SHAPE.TEAR, glow=(OIL, 10, 60), name="s5_drop")
A.zoom(drop, 1700, 500)
A.move(drop, 2300, 0, -0.08, dur=1100, rev=True)
n2004 = text(s, 8.7, 2.3, 4, 1.4, "2004", size=80, color=INK, bold=True, name="!!bignum")
A.zoom(n2004, 1900, 600)
fb = text(s, 8.75, 3.75, 4.0, 1.0, [[("First oil from the cluster", {"bold": True, "color": LGREEN, "size": 20})],
                                    [("flowed from the Zalzala field.", {"size": 18})]], color=INK, name="s5_txt")
A.float(fb, 2300, 700)
text(s, 8.75, 5.95, 4, 0.3, "Schematic grouping · not a map", size=10, color=DIM, italic=True, name="s5_nts")
finish_slide(s, A)
notes(s, 30,
      "Four 3-D field tiles rise one after another — Harweel, Zalzala, Sakhiya and Dafiq. Zalzala glows green and "
      "an oil drop floats above it as '2004 – first oil' appears. Timeline marker moves to 2004.",
      "After that first find, similar fields were discovered around it — Zalzala, Sakhiya and Dafiq. Together "
      "they became known as the Harweel cluster. And in 2004, the first oil from the cluster came from Zalzala. "
      "So far, it sounds straightforward. It wasn't.",
      "Field names, 'Harweel cluster' and 2004 first oil from Zalzala are from the source. The 2x2 arrangement is "
      "schematic — it does not show real field positions.")

# =================================================================== SLIDE 6 — tight rock
s, A = base("Challenge 1 — the rock is tight", "Challenge 1 of 3", 2004)


def lens(s, A, cx, cy, R, grain_sp, grain_r, drop_r, flowing, pre, t0):
    ring = oval(s, cx, cy, R, fill=grad((0, "4A2E17"), (100, "26170B"), path="circle"), line=(LTEAL, 2),
                glow=(TEAL, 10, 45), name=pre + "_lens")
    A.zoom(ring, t0, 600)
    n = int(2 * R / grain_sp) + 2
    k = 0
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            gx, gy = cx + i * grain_sp, cy + j * grain_sp
            gr = grain_r * random.uniform(0.9, 1.06)
            if math.hypot(gx - cx, gy - cy) + gr > R - 0.05:
                continue
            g = sphere(s, gx, gy, gr, "F4E3C0", "C9A56C", "7E5D33", name=f"{pre}_g{k}")
            A.fade(g, t0 + 300 + k * 4, 300)
            k += 1
    # oil droplets in the pore channels
    m = 0
    for j in range(-n, n):
        ly = cy + (j + 0.5) * grain_sp
        for i in range(-n, n + 1):
            px = cx + i * grain_sp + (grain_sp / 2 if not flowing else random.uniform(0, grain_sp * 0.5))
            reach = grain_sp if flowing else 0
            if math.hypot(px - cx, ly - cy) + drop_r > R - 0.12 or math.hypot(px + reach - cx, ly - cy) > R - 0.12:
                continue
            if not flowing and random.random() < 0.45:
                continue
            dd = oval(s, px, ly, drop_r, fill=OIL_HI if flowing else OIL, glow=(OIL, 4, 60) if flowing else None,
                      name=f"{pre}_o{m}")
            A.fade(dd, t0 + 900, 400)
            if flowing:
                A.move(dd, t0 + 1300, grain_sp, 0, dur=1100)
            else:
                A.move(dd, t0 + 1300, 0.018, 0, dur=random.randint(700, 1200), rev=True)
            m += 1


lens(s, A, 3.45, 3.95, 1.75, 0.62, 0.255, 0.048, True, "s6a", 200)
lens(s, A, 9.85, 3.95, 1.75, 0.3, 0.13, 0.026, False, "s6b", 700)
vs = text(s, 6.15, 3.7, 1.0, 0.5, "vs", size=22, color=DIM, bold=True, align="c", name="s6_vs")
for (x, h1, h2, col) in [(3.45, "TYPICAL RESERVOIR ROCK", "Wide, connected pores — oil flows freely", LGREEN),
                         (9.85, "HARWEEL'S TIGHT ROCK", "Tiny, narrow pores — oil barely moves", OIL_HI)]:
    tt = text(s, x - 2.6, 5.85, 5.2, 0.7, [[(h1, {"bold": True, "color": col, "size": 13, "spc": 1.5})],
                                         [(h2, {"size": 15})]], color=INK, align="c", name=f"s6_lab{x}")
    A.fade(tt, 1800, 500)
text(s, 10.4, 6.85, 2.4, 0.25, "Illustrative · not to scale", size=9, color=DIM, italic=True, align="r",
     name="s6_nts")
finish_slide(s, A)
notes(s, 35,
      "Two 'microscope' lenses zoom in on the rock. Left: big grains with open channels — bright oil droplets "
      "stream continuously through them. Right: Harweel's tight rock — tiny grains packed closely; the oil only "
      "trembles in place. The contrast should be understood without words.",
      "The first challenge is the rock itself. Imagine looking at it under a microscope. In a typical reservoir — "
      "on the left — the grains leave wide, connected spaces, and oil can flow through them toward a well. "
      "Harweel's rock, on the right, is very tight: the spaces between the grains are tiny and poorly connected, "
      "so the oil simply does not move through it easily.",
      "'The rocks are very tight and the oil does not move through them easily' is from the source. Grain and pore "
      "sizes are illustrative only.")

# =================================================================== SLIDE 7 — pressure
s, A = base("Challenge 2 — extreme pressure", "Challenge 2 of 3", 2004)
GX, GY, GR = 3.55, 4.25, 1.95
dial = oval(s, GX, GY, GR + 0.25, fill=grad((0, "15403F"), (100, "081F1F"), path="circle"), line=(RULE, 1.25),
            name="s7_dial", shadow=(18, 4, 90, "000000", 50))
A.zoom(dial, 100, 500)
NSEG = 24
for i in range(NSEG):
    a0 = 150 + 240 * i / NSEG
    a1 = 150 + 240 * (i + 1) / NSEG - 1.6
    f = i / (NSEG - 1)
    col = GREEN if f < 0.45 else (OIL if f < 0.78 else RED)
    sg = rect(s, GX - GR, GY - GR, 2 * GR, 2 * GR, fill=col, kind=MSO_SHAPE.BLOCK_ARC,
              adj=[(a0 % 360) * 0.6, (a1 % 360) * 0.6, 0.09], name=f"s7_seg{i}")
    A.fade(sg, 500 + i * 35, 200)
for v in (0, 5000, 10000, 15000):
    ang = math.radians(150 + 240 * v / 15000)
    tx, ty = GX + (GR - 0.55) * math.cos(ang), GY + (GR - 0.55) * math.sin(ang)
    text(s, tx - 0.5, ty - 0.13, 1.0, 0.26, f"{v:,}", size=11, color=MUTED, align="c", name=f"s7_tick{v}")
text(s, GX - 0.8, GY + 0.55, 1.6, 0.3, "psi", size=14, color=MUTED, align="c", name="s7_unit")
needle = rect(s, GX - 0.09, GY - (GR - 0.3), 0.18, 2 * (GR - 0.3),
              fill=grad((0, "FFFFFF"), (48, RED), (50, RED, 0), (100, RED, 0), ang=90), kind=MSO_SHAPE.DIAMOND,
              name="s7_needle", rot=-120)
A.spin(needle, 1400, 224, dur=2600)
hub = oval(s, GX, GY, 0.2, fill=grad((0, "E7EEF0"), (100, "7C8B90"), path="circle", ftr=(30, 30, 70, 70)),
           name="s7_hub")
n14 = text(s, 6.9, 1.85, 6, 1.4, [[("14,000", {"bold": True}), (" psi", {"size": 36, "color": MUTED})]],
           size=84, color=INK, name="!!bignum")
A.fade(n14, 2800, 600)
t7 = text(s, 6.95, 3.35, 5.6, 0.5, "Pressure in most Harweel reservoirs reaches this level.", size=18,
          color=INK, name="s7_t1")
A.fade(t7, 3200, 600)
cmp_ = card(s, 6.95, 4.25, 5.6, 1.15, name="s7_card")
A.float(cmp_, 3700, 600)
ct = text(s, 7.25, 4.38, 5.1, 1.0, [[("≈ 950×", {"bold": True, "color": OIL_HI, "size": 30})],
                                   [("the air pressure at sea level (14.7 psi)", {"size": 15})]],
          color=INK, name="s7_ct")
A.float(ct, 3700, 600)
finish_slide(s, A)
notes(s, 30,
      "A segmented pressure gauge builds around the dial; the needle sweeps from zero deep into the red and stops "
      "at 14,000 psi. The headline number then appears, followed by an everyday comparison (≈950× atmospheric).",
      "The second challenge is pressure. In most of Harweel's reservoirs, pressure reaches around 14,000 psi. "
      "For comparison, the air around us at sea level presses at about 14.7 psi — so that's roughly 950 times "
      "atmospheric pressure. Everything that goes into these wells has to be engineered to contain that safely.",
      "14,000 psi in most reservoirs is from the source. The ≈950× comparison is simple arithmetic "
      "(14,000 / 14.7). The engineering remark in the last sentence is general context.")

# =================================================================== SLIDE 8 — sour gas
s, A = base("Challenge 3 — the gas is sour", "Challenge 3 of 3", 2004)
MX, MY = 3.6, 3.85
for sgn in (-1, 1):
    ang = math.radians(90 + sgn * 46)
    hx_, hy_ = MX + 1.55 * math.cos(ang), MY + 1.55 * math.sin(ang)
    bd = line(s, MX, MY, hx_, hy_, "9FB3B8", 10, name=f"s8_bond{sgn}")
    A.fade(bd, 600, 500)
    hh = sphere(s, hx_, hy_, 0.52, "FFFFFF", "DDE5E8", "8C9AA0", name=f"s8_H{sgn}")
    A.zoom(hh, 700 + (sgn + 1) * 100, 500)
    text(s, hx_ - 0.3, hy_ - 0.2, 0.6, 0.4, "H", size=20, color="3A4A50", bold=True, align="c", anchor="m",
         name=f"s8_Hl{sgn}")
S_ = sphere(s, MX, MY, 0.9, "FFF6C4", H2S, "9A7A12", name="s8_S", glow=(H2S, 18, 30))
A.zoom(S_, 300, 600)
text(s, MX - 0.4, MY - 0.3, 0.8, 0.6, "S", size=32, color="4A3A06", bold=True, align="c", anchor="m", name="s8_Sl")
text(s, MX - 2, 5.95, 4, 0.3, "Hydrogen sulphide molecule", size=11, color=DIM, italic=True, align="c",
     name="s8_cap")
hh2 = text(s, 6.95, 1.85, 5.5, 1.4, [[("H", {}), ("2", {"baseline": -25000}), ("S", {})]], size=84, color=H2S,
           bold=True, name="!!bignum")
A.fade(hh2, 1400, 600)
text(s, 6.98, 3.25, 5.5, 0.4, "Hydrogen sulphide", size=20, color=INK, name="s8_name")
rows = [("Comes up together with the oil", "It is part of the gas produced from the reservoir."),
        ("Makes the gas “sour”", "Sour gas is the industry term for gas containing H₂S."),
        ("Toxic and corrosive", "It demands special materials and careful handling.")]
for i, (a, b) in enumerate(rows):
    y = 3.95 + i * 0.85
    bg_ = badge(s, 7.17, y + 0.22, i + 1, H2S, name=f"s8_b{i}")
    tt = text(s, 7.55, y, 5.0, 0.7, [[(a, {"bold": True, "size": 16, "color": INK})], [(b, {"size": 13})]],
              color=MUTED, name=f"s8_r{i}")
    A.float(bg_, 2000 + i * 300, 500), A.float(tt, 2000 + i * 300, 500)
A.move(S_, 2600, 0, -0.06, dur=1600, rev=True)
finish_slide(s, A)
notes(s, 30,
      "A glossy 3-D H₂S molecule assembles (sulphur, then two hydrogens) and floats gently. The formula and three "
      "short facts appear beside it.",
      "And the third challenge: the gas that comes up with the oil is sour — it contains hydrogen sulphide, H2S. "
      "Hydrogen sulphide is toxic and corrosive, so it can't be treated like ordinary gas; it needs special "
      "materials and very careful handling.",
      "'The gas produced with the oil is sour, containing hydrogen sulphide' is from the source. 'Toxic and "
      "corrosive' is general, well-established context.")

# =================================================================== SLIDE 9 — the math
s, A = base("Only about one barrel in ten", "The hard math", 2004,
            "Tight rock, extreme pressure, sour gas: without a solution, only around a tenth of the oil in place "
            "would ever be recovered.", lead_w=11.5)
BW_, BH_, GAP = 0.78, 1.25, 0.32
X0 = (SW - (10 * BW_ + 9 * GAP)) / 2
for i in range(10):
    x = X0 + i * (BW_ + GAP)
    b = rect(s, x, 3.2, BW_, BH_, fill=grad((0, OIL_D), (40, OIL_HI), (100, OIL_D), ang=0), kind=MSO_SHAPE.CAN,
             adj=[0.22], line=(dk(OIL_D, 0.7), 0.75), name=f"s9_bar{i}",
             glow=(OIL, 10, 50) if i == 0 else None)
    A.float(b, 200 + i * 90, 500)
    if i:
        ov = rect(s, x - 0.02, 3.18, BW_ + 0.04, BH_ + 0.04, fill=("0B2626", 82), kind=MSO_SHAPE.CAN, adj=[0.22],
                  line=(RULE, 0.75), name=f"s9_dim{i}")
        A.fade(ov, 1700 + (10 - i) * 70, 500)
x1 = X0 + BW_ / 2
l1 = text(s, X0 - 0.4, 4.7, BW_ + 0.8, 0.9, [[("≈ 10%", {"bold": True, "size": 24, "color": OIL_HI})],
                                           [("recovered", {"size": 13})]], color=INK, align="c", name="s9_l1")
A.fade(l1, 2600, 500)
bx0, bx1 = X0 + BW_ + GAP, X0 + 10 * BW_ + 9 * GAP
brk = poly(s, [(bx0, 4.6), (bx0, 4.75), (bx1, 4.75), (bx1, 4.6)], fill=None, line=(MUTED, 1), closed=False,
           name="s9_brk")
A.fade(brk, 2800, 500)
l2 = text(s, bx0, 4.95, bx1 - bx0, 0.9, [[("≈ 90%", {"bold": True, "size": 24, "color": MUTED})],
                                         [("would stay underground", {"size": 13})]], color=INK, align="c",
          name="s9_l2")
A.fade(l2, 2900, 500)
finish_slide(s, A)
notes(s, 25,
      "Ten 3-D barrels roll in. Then nine of them dim, one by one, leaving a single glowing barrel — the audience "
      "sees '1 in 10' before it is said.",
      "Put those three challenges together and the math was hard. Without a solution, only about one tenth of "
      "the oil in the reservoir would ever come out. Nine barrels out of ten would stay in the ground. "
      "That's the problem the Harweel team had to solve.",
      "'Without a solution only about a tenth of the oil would be recovered' is from the source.")

# =================================================================== SLIDE 10 — the idea (hero)
s, A = base("The idea — put the gas back to work", "The solution", 2004)
TOP, X_L, X_R = 2.62, 0.62, 12.72
L_SAND, L_ROCK, L_SALT, L_RES, L_SALT2 = (TOP, 2.78), (2.78, 3.86), (3.86, 4.22), (4.22, 5.58), (5.58, 6.05)
poly(s, [(X_L, TOP), (X_R, TOP), (X_R - 0.25, TOP - 0.22), (X_L + 0.25, TOP - 0.22)],
     fill=grad((0, "F6E2B4"), (100, "D9B77A")), name="!!s10_surf")
for (y0, y1), c0, c1, nm in [(L_SAND, "EDD39F", "D2AF6E", "sand"), (L_ROCK, "6E523E", "4E3A2B", "rock"),
                             (L_SALT, "E3EBF0", "C3D1DA", "salt"), (L_RES, "5E3D21", "3A2413", "res"),
                             (L_SALT2, "D9E3E9", "B4C3CE", "salt2")]:
    rect(s, X_L, y0, X_R - X_L, y1 - y0, fill=grad((0, c0), (100, c1)), name=f"!!s10_{nm}")
glowres = rect(s, X_L, L_RES[0], X_R - X_L, L_RES[1] - L_RES[0],
               fill=grad((0, OIL, 0), (50, OIL, 18), (100, OIL, 0)), name="s10_resglow")
for nm, y in [("Salt", 4.04), ("Oil-bearing rock", 5.38), ("Salt", 5.82)]:
    text(s, X_R - 2.1, y - 0.11, 2.0, 0.22, nm, size=10, color="5B6B72" if nm == "Salt" else OIL_HI,
         align="r", bold=nm != "Salt", name=f"s10_lay{y}")
PX, IX = 2.35, 10.75
# gas front advancing from the injector toward the producer
front = rect(s, 4.3, L_RES[0] + 0.03, IX - 4.3 + 0.05, L_RES[1] - L_RES[0] - 0.06,
             fill=grad((0, GAS, 0), (55, GAS, 30), (100, GAS, 55), ang=0), name="s10_front")
A.wipe(front, 2600, 5200, d="r")
# wells
for xw, nm, col in [(PX, "Production well", OIL_HI), (IX, "Injection well", GAS)]:
    cs_ = rect(s, xw - 0.07, TOP - 0.05, 0.14, L_RES[1] - 0.12 - TOP, fill=grad((0, "B9C6CC"), (50, "EEF3F5"),
                                                                              (100, "8E9CA3"), ang=0),
               name=f"!!well_{nm[:3]}")
    tree_ = [rect(s, xw - 0.2, TOP - 0.62, 0.4, 0.14, fill="C6D2D7", name=f"!!tree_{nm[:3]}a", bevel=2),
             rect(s, xw - 0.1, TOP - 0.48, 0.2, 0.45, fill=grad((0, "8E9CA3"), (50, "E6ECEF"), (100, "8E9CA3"),
                                                              ang=0), name=f"!!tree_{nm[:3]}b"),
             rect(s, xw - 0.32, TOP - 0.33, 0.64, 0.1, fill=col, name=f"!!tree_{nm[:3]}c", bevel=2)]
    text(s, xw - 1.2, 1.62, 2.4, 0.26, nm.upper(), size=11, color=col, bold=True, align="c", spc=1,
         name=f"s10_wl{nm[:3]}")
# surface recycle pipe (sour gas back to the injector) + Rabab gas
PY = TOP - 0.28
pipe = line(s, PX + 0.32, PY, IX - 0.32, PY, "6F8C92", 7, name="s10_pipe")
A.wipe(pipe, 400, 900, d="l")
rp = line(s, IX + 0.32, PY, X_R, PY, "6F8C92", 7, name="s10_rpipe")
A.wipe(rp, 800, 500, d="r")
pl = text(s, 4.6, PY - 0.46, 4.2, 0.3, "Sour gas separated at surface — sent back down", size=12, color=GAS,
          align="c", name="s10_pl")
A.fade(pl, 1000, 500)
rl_ = text(s, IX + 0.42, PY - 0.52, 1.6, 0.45, [[("+ Gas from", {})], [("Rabab field", {"bold": True})]],
           size=11, color=RABAB, name="s10_rl")
A.fade(rl_, 1200, 500)
flow(s, A, (PX + 0.45, PY), (IX - 0.35, PY), 0.42, GAS, 0.05, 700, t=1300, name="s10_fp")
flow(s, A, (X_R - 0.1, PY), (IX + 0.35, PY), 0.38, RABAB, 0.05, 700, t=1300, name="s10_fr")
flow(s, A, (IX, TOP + 0.1), (IX, L_RES[1] - 0.25), 0.4, GAS, 0.045, 650, t=1700, name="s10_fi")
flow(s, A, (PX, L_RES[1] - 0.3), (PX, TOP - 0.05), 0.4, OIL_HI, 0.045, 650, t=4200, name="s10_fo")
# oil being swept toward the producer
k = 0
for row, yy in enumerate([4.48, 4.82, 5.16, 5.42]):
    sp_ = 0.62
    xx = PX + 0.35 + (row % 2) * 0.3
    while xx < IX - 0.5:
        dd = oval(s, xx, yy, 0.05, fill=OIL_HI, glow=(OIL, 4, 50), name=f"s10_oil{k}")
        A.move(dd, 4000 + row * 60, -sp_, 0, dur=1500)
        xx += sp_
        k += 1
# step cards
steps = [(1, 7.75, 2.92, "Re-inject the sour gas", "together with gas from nearby Rabab", GAS, 400),
         (2, 6.75, 6.12, "The gas dissolves into the oil", "deep inside the reservoir", GAS_HI, 3000),
         (3, 2.75, 2.92, "Oil moves to the production wells", "where it is brought to surface", OIL_HI, 4600)]
for n, x, y, h1, h2, col, t_ in steps:
    c_ = card(s, x, y, 3.55, 0.72, name=f"s10_card{n}", op=92)
    b_ = badge(s, x + 0.32, y + 0.36, n, col, name=f"s10_badge{n}")
    tt = text(s, x + 0.62, y + 0.1, 2.9, 0.55, [[(h1, {"bold": True, "size": 13, "color": INK})],
                                               [(h2, {"size": 11})]], color=MUTED, name=f"s10_ct{n}")
    for o in (c_, b_, tt):
        A.float(o, t_, 500)
lensm = oval(s, 6.6, 4.9, 0.36, fill=None, line=("FFFFFF", 1.5, None, "dash"), name="!!lens")
A.zoom(lensm, 6000, 500)
A.pulse(lensm, 6500, 1.15, 800)
finish_slide(s, A)
notes(s, 50,
      "The hero slide — the whole process at once. Sequence: (1) the surface recycle pipe draws in and cyan gas "
      "particles flow along it, joined by Rabab gas; (2) gas streams down the injection well; (3) a cyan gas front "
      "slowly sweeps through the oil layer from right to left; (4) amber oil particles drift toward the production "
      "well and rise up it. A dashed 'lens' then marks the point we zoom into next.",
      "Then came the idea. Instead of treating the sour gas as a problem, put it back to work. The gas that comes "
      "up with the oil is separated at the surface and injected back down into the reservoir — together with "
      "additional gas from the nearby Rabab field. Deep underground, that gas dissolves into the oil and helps it "
      "move toward the production wells, where it is brought back to the surface. So the challenge itself becomes "
      "part of the solution. Let's zoom in to see what 'dissolving' actually does.",
      "Re-injecting the sour gas plus gas from the Rabab field, the gas dissolving in the oil and helping it move "
      "to production wells — all from the source. The surface 'separation' wording is a simplification of how "
      "produced gas reaches the injection wells; well spacing and geometry are schematic.")

# =================================================================== SLIDE 11 — pore-scale zoom
s, A = base("Inside the rock: how gas frees the oil", "Zoom in · pore scale", 2004)
LX_, LY_, LR = 3.55, 4.15, 2.15
lens_ = oval(s, LX_, LY_, LR, fill=grad((0, "5A3A1E"), (100, "2E1D0E"), path="circle"), line=("FFFFFF", 1.75),
             glow=(TEAL, 12, 45), name="!!lens")
thin = oval(s, LX_, LY_, LR - 0.02, fill=grad((0, "B98A3E", 85), (100, "8E6A30", 85), path="circle"),
            name="s11_thin")
A.fade(thin, 3300, 1500)
k = 0
for i in range(-5, 6):
    for j in range(-5, 6):
        gx, gy = LX_ + i * 0.52 + (0.26 if j % 2 else 0), LY_ + j * 0.45
        gr = 0.2 * random.uniform(0.9, 1.08)
        if math.hypot(gx - LX_, gy - LY_) + gr > LR - 0.06:
            continue
        sphere(s, gx, gy, gr, "F4E3C0", "C9A56C", "7E5D33", name=f"s11_g{k}")
        k += 1
# gas molecules entering from the right and dissolving (fading) into the oil
for i in range(14):
    gy = LY_ + random.uniform(-1.3, 1.3)
    gx = LX_ + math.sqrt(max(LR ** 2 - (gy - LY_) ** 2, 0)) - 0.25
    g = oval(s, gx, gy, 0.055, fill=GAS_HI, glow=(GAS, 6, 70), name=f"s11_gas{i}")
    A.fade(g, 600 + i * 90, 300)
    A.move(g, 900 + i * 90, -random.uniform(0.9, 1.6), random.uniform(-0.2, 0.2), dur=2000, repeat=False)
    A.out(g, 2800 + i * 60, 600)
# then the oil starts to move
m = 0
for j in range(-4, 5):
    ly = LY_ + j * 0.45 + 0.225
    for i in range(-4, 4):
        px = LX_ + i * 0.52 + 0.13
        if math.hypot(px - LX_, ly - LY_) > LR - 0.45:
            continue
        dd = oval(s, px, ly, 0.045, fill=OIL_HI, glow=(OIL, 4, 50), name=f"s11_o{m}")
        A.fade(dd, 4200, 400)
        A.move(dd, 4600, -0.52, 0, dur=1200)
        m += 1
text(s, LX_ - 1.5, LY_ + LR + 0.1, 3, 0.25, "Pore-scale view · illustrative", size=9, color=DIM, italic=True,
     align="c", name="s11_cap")
items = [("Gas meets the oil", "Injected gas reaches oil trapped in the tiny pores.", GAS_HI, 500),
         ("The gas dissolves into it", "Gas and oil blend into a single, lighter fluid.", GAS, 2600),
         ("The oil swells and thins", "Lighter, thinner oil can squeeze through the tight rock "
                                      "toward the production wells.", OIL_HI, 4200)]
for i, (h1, h2, col, t_) in enumerate(items):
    y = 1.95 + i * 1.45
    c_ = card(s, 6.75, y, 5.95, 1.2, name=f"s11_card{i}")
    b_ = badge(s, 7.2, y + 0.6, i + 1, col, name=f"s11_b{i}", r=0.22)
    tt = text(s, 7.65, y + 0.17, 4.9, 0.95, [[(h1, {"bold": True, "size": 17, "color": INK})],
                                            [(h2, {"size": 13})]], color=MUTED, name=f"s11_t{i}")
    for o in (c_, b_, tt):
        A.float(o, t_, 500)
finish_slide(s, A)
notes(s, 35,
      "Morph zoom: the small dashed lens from the previous slide expands into a large magnified view of the "
      "reservoir rock. Cyan gas molecules drift in and fade as they dissolve; the oil-filled pores lighten "
      "(the oil becomes thinner); then oil droplets start moving through the rock toward the producer.",
      "Here's what happens at the scale of the pores. The injected gas reaches the oil trapped in the tiny spaces "
      "between the grains. Instead of pushing past it, the gas dissolves into the oil. That makes the oil swell "
      "and become thinner and lighter — and a thinner fluid can squeeze through tight rock far more easily. "
      "That's how the gas helps the oil move toward the production wells.",
      "'The gas dissolves in the oil and helps it move to the production wells' is from the source. The "
      "explanation that dissolved gas swells the oil and reduces its viscosity is standard reservoir-engineering "
      "context added for clarity.")

# =================================================================== SLIDE 12 — pilot to full field
s, A = base("Prove it first, then go full scale", "From pilot to full field", 2014)
stp = [("PILOT", "Test injection at Zalzala", "Confirm the idea works in the real reservoir"),
       ("2014", "Full-scale injection begins", "Gas injection rolled out across Zalzala"),
       ("2015", "Full capacity reached", "One year after full injection started")]
vl = line(s, 1.0, 2.15, 1.0, 5.95, RULE, 2, name="s12_vl")
A.wipe(vl, 200, 1600, d="d")
for i, (yr, h1, h2) in enumerate(stp):
    y = 2.0 + i * 1.45
    dd = oval(s, 1.0, y + 0.3, 0.16, fill=GREEN if i else TEAL, glow=(GREEN, 6, 50), name=f"s12_d{i}")
    tt = text(s, 1.4, y, 4.6, 1.1, [[(yr, {"bold": True, "size": 14, "color": LGREEN, "spc": 1.5})],
                                    [(h1, {"bold": True, "size": 18, "color": INK})], [(h2, {"size": 13})]],
              color=MUTED, name=f"s12_t{i}")
    A.zoom(dd, 400 + i * 500, 400), A.float(tt, 450 + i * 500, 500)
# 3-D bars: expected recovery
iso = Iso(8.75, 4.05, 1.0)


def bar3d(x, h, top, front, side, name, t_):
    P = iso.p
    w, d = 0.75, 0.75
    fs = [poly(s, [P(x, d, 0), P(x + w, d, 0), P(x + w, d, h), P(x, d, h)], fill=front, name=name + "_f"),
          poly(s, [P(x + w, 0, 0), P(x + w, d, 0), P(x + w, d, h), P(x + w, 0, h)], fill=side, name=name + "_s"),
          poly(s, [P(x, 0, h), P(x + w, 0, h), P(x + w, d, h), P(x, d, h)], fill=top, name=name + "_t")]
    for f in fs:
        A.wipe(f, t_, 1200, d="u")
    return P(x + w / 2, d / 2, h)


H10, H30 = 0.75, 2.6
pa = bar3d(-0.5, H10, "8FA3A6", grad((0, "6E8487"), (100, "4E6366")), "3F5154", "s12_bar10", 1800)
pb = bar3d(1.6, H30, "FFD58A", grad((0, OIL_HI), (100, OIL_D)), "8A5414", "s12_bar30", 2300)
v1 = text(s, pa[0] - 1, pa[1] - 0.75, 2, 0.5, "≈ 10%", size=24, color=INK, bold=True, align="c", name="s12_v1")
v2 = text(s, pb[0] - 1, pb[1] - 0.78, 2, 0.5, "> 30%", size=30, color=OIL_HI, bold=True, align="c", name="s12_v2")
A.fade(v1, 3000, 400), A.zoom(v2, 3500, 500)
for (pt, lb) in [(iso.p(-0.5 + 0.375, 0.75 + 0.2, 0), "Without a solution"),
                 (iso.p(1.6 + 0.375, 0.75 + 0.2, 0), "With gas injection\n(expected)")]:
    text(s, pt[0] - 1.2, pt[1] + 0.12, 2.4, 0.5, lb, size=12, color=MUTED, align="c", name=f"s12_lab{lb[:4]}")
hdr = text(s, 6.9, 1.62, 5.8, 0.35, "EXPECTED OIL RECOVERY", size=12, color=GREEN, bold=True, spc=2,
           name="s12_hdr")
text(s, 6.9, 6.72, 5.9, 0.25, "Expected recovery — Oil & Gas Journal estimate (2007), as cited in the source.",
     size=9, color=DIM, italic=True, name="s12_src")
finish_slide(s, A)
notes(s, 40,
      "Left: a vertical timeline builds — pilot, 2014 full injection, 2015 full capacity. Right: two 3-D columns "
      "rise; the 'expected' recovery column climbs to more than three times the height of the 'no solution' "
      "column. Timeline marker jumps to 2014.",
      "Of course, an idea like this has to be proven. So the team first tested gas injection in the Zalzala "
      "field, to confirm it really worked in this reservoir. The expectation was that recovery would rise from "
      "about one tenth of the oil to more than thirty percent — roughly three times as much. In 2014, full-scale "
      "injection began at Zalzala, and a year later it reached full capacity.",
      "Pilot at Zalzala, 10% -> >30% expectation (an OGJ 2007 estimate shown in the source), 2014 full "
      "injection and full capacity one year later — all from the source. The >30% is an expected figure, not a "
      "reported actual. The pilot's exact year is not given in the source, so it is shown without a date.")

# =================================================================== SLIDE 13 — RHIP surface system
s, A = base("One integrated system at the surface", "2019 · Rabab Harweel Integrated Project", 2019,
            "Production started in 2019 — the largest project in PDO's history at the time.", lead_w=8.5)
iso = Iso(6.55, 2.45, 0.6)
plate = iso.box(s, 0, 0, -0.15, 6.0, 4.2, 0.15, grad((0, "1B4A47"), (100, "123B39")), "0B2828", "0E3131",
                "!!plate", line_c=RULE)
for f in plate:
    A.fade(f, 100, 500)
for gx_ in range(1, 6):
    a_, b_ = iso.p(gx_, 0, 0), iso.p(gx_, 4.2, 0)
    line(s, a_[0], a_[1], b_[0], b_[1], "2A5E5A", 0.5, 60, name=f"s13_gx{gx_}")
for gy_ in range(1, 5):
    a_, b_ = iso.p(0, gy_, 0), iso.p(6.0, gy_, 0)
    line(s, a_[0], a_[1], b_[0], b_[1], "2A5E5A", 0.5, 60, name=f"s13_gy{gy_}")
units = []
units += iso.cyl(s, 1.0, 1.0, 0, 0.4, 0.9, "E2E9EC", "A9B7BD", "667880", "s13_sep1")
units += iso.cyl(s, 1.0, 2.3, 0, 0.4, 0.9, "E2E9EC", "A9B7BD", "667880", "s13_sep2")
units += iso.box(s, 2.6, 0.3, 0, 1.6, 1.0, 0.8, "C9D5DA", "7F9298", "9AABB1", "s13_comp", line_c="5D7076")
units += iso.cyl(s, 3.3, 2.9, 0, 0.28, 2.0, "E2E9EC", "A9B7BD", "667880", "s13_col1")
units += iso.cyl(s, 4.2, 2.9, 0, 0.28, 2.3, "E2E9EC", "A9B7BD", "667880", "s13_col2")
units += iso.cyl(s, 5.0, 1.0, 0, 0.55, 0.5, "FFE1A3", "D9A24A", "8A5A1A", "s13_tank")
for i, u in enumerate(units):
    A.float(u, 400 + i * 60, 500)
for (px_, py_, pz_, lb, dxl, dyl) in [(1.0, 1.65, 1.75, "Separation", 0, 0), (4.2, 0.3, 0.8, "Compression", 0.95, 0),
                                      (4.6, 3.3, 0, "Gas processing", 0.55, 0.12)]:
    xx, yy = iso.p(px_, py_, pz_)
    tt = text(s, xx - 0.9 + dxl, yy - 0.15 + dyl, 1.8, 0.26, lb, size=11, color=INK, bold=True, align="c",
              name=f"s13_u{lb}")
    A.fade(tt, 1600, 400)
# inflow from the wells
W0, W1 = iso.p(-2.4, 1.65, 0), iso.p(0.35, 1.65, 0)
wp = line(s, W0[0], W0[1], W1[0], W1[1], OIL, 5, name="s13_win")
A.wipe(wp, 1800, 600, d="r")
flow(s, A, W0, W1, 0.33, OIL_HI, 0.045, 600, t=2100, name="s13_fw")
for i in range(3):
    hx_, hy_ = iso.p(-2.2 + i * 0.75, 1.65, 0)
    w_ = rect(s, hx_ - 0.06, hy_ - 0.36, 0.12, 0.36, fill=grad((0, "8E9CA3"), (50, "E6ECEF"), (100, "8E9CA3"), ang=0),
              name=f"s13_wh{i}")
    A.fade(w_, 1700, 400)
wl_ = text(s, W0[0] - 2.45, W0[1] - 0.05, 2.3, 0.6, [[("From the wells", {"bold": True, "color": OIL_HI, "size": 14})],
                                                    [("oil + sour gas", {})]], size=12, color=INK,
           align="r", name="s13_wl")
A.fade(wl_, 1900, 400)
outs = [((6.0, 3.4), (8.3, 3.4), GREEN, "Sweet gas", "into the Salalah gas line", 2600, "r"),
        ((6.0, 1.5), (8.7, 1.5), OIL, "Condensate", "to the main line, via Marmul", 3000, "r"),
        ((0.6, 4.2), (0.6, 6.6), GAS, "Sour gas + Rabab gas", "back into the reservoir", 3400, "l")]
for i, (a, b, col, h1, h2, t_, side) in enumerate(outs):
    p0, p1 = iso.p(*a, 0), iso.p(*b, 0)
    pl_ = line(s, p0[0], p0[1], p1[0], p1[1], col, 5, name=f"s13_out{i}")
    A.wipe(pl_, t_, 600, d="r" if side == "r" else "l")
    flow(s, A, p0, p1, 0.33, col if i < 2 else GAS_HI, 0.045, 600, t=t_ + 300, name=f"s13_fo{i}")
    lx_, ly_ = p1
    if side == "r":
        tt = text(s, lx_ + 0.15, ly_ - 0.3, 2.7, 0.6, [[(h1, {"bold": True, "color": col, "size": 14})],
                                                      [(h2, {})]], size=12, color=INK, name=f"s13_ol{i}")
    else:
        tt = text(s, lx_ - 2.85, ly_ - 0.3, 2.7, 0.6, [[(h1, {"bold": True, "color": col, "size": 14})],
                                                      [(h2, {})]], size=12, color=INK, align="r", name=f"s13_ol{i}")
    A.fade(tt, t_ + 200, 500)
rb0, rb1 = iso.p(3.4, -2.3, 0), iso.p(3.4, 0.0, 0)
rbl = line(s, rb0[0], rb0[1], rb1[0], rb1[1], RABAB, 5, name="s13_rab")
A.wipe(rbl, 2300, 500, d="l")
flow(s, A, rb0, rb1, 0.33, RABAB, 0.045, 600, t=2500, name="s13_fr")
tr_ = text(s, rb0[0] + 0.15, rb0[1] - 0.3, 2.4, 0.6, [[("Gas from Rabab field", {"bold": True, "size": 14})],
                                                    [("joins the system", {"color": INK})]], size=12,
           color=RABAB, name="s13_rl")
A.fade(tr_, 2400, 400)
text(s, 9.2, 6.85, 3.6, 0.25, "Simplified schematic · not a plant layout", size=9, color=DIM, italic=True,
     align="r", name="s13_nts")
finish_slide(s, A)
notes(s, 40,
      "An isometric 3-D processing site assembles on its platform. Animated flows then show the whole surface "
      "loop: amber oil and sour gas arriving from the wells; Rabab gas joining from the side; sweet gas leaving "
      "for the Salalah gas line; condensate heading to the main line via Marmul; and sour gas plus Rabab gas "
      "flowing back down to the injection wells.",
      "In 2019, all of this came together in the Rabab Harweel Integrated Project — at the time, the largest "
      "project in PDO's history. Think of it as one integrated system at the surface. Oil and sour gas arrive "
      "from the wells. Gas from the Rabab field joins in. The sour gas, together with the Rabab gas, goes back "
      "down into the reservoir to keep the oil moving. Sweet gas flows into the Salalah gas line, and condensate "
      "is sent to the main line through Marmul.",
      "Project name, 2019 start, 'largest in the company's history at the time', sweet gas to the Salalah gas line "
      "and condensate to the main line via Marmul are from the source. The internal units (separation, "
      "compression, gas processing) are a simplified, generic representation — the source does not describe the "
      "plant layout. The source also does not state where the crude oil itself is exported; please confirm "
      "before presenting if asked.")

# =================================================================== SLIDE 14 — results + new pipeline
s, A = base("The results reach all the way to Salalah", "2024 · Results", 2024)
n54 = text(s, 0.62, 1.7, 5.6, 1.3, [[("≈ 54", {"bold": True}), (" million", {"size": 34, "color": MUTED})]],
           size=78, color=OIL_HI, name="!!bignum")
A.zoom(n54, 300, 600)
t1 = text(s, 0.65, 3.0, 5.4, 0.8, "extra barrels of oil — from gas injection at Zalzala alone, by 2024.",
          size=17, color=INK, name="s14_t1")
A.fade(t1, 800, 500)
dv = line(s, 0.65, 4.0, 5.9, 4.0, RULE, 1, name="s14_div")
A.wipe(dv, 1100, 600, d="l")
n176 = text(s, 0.62, 4.2, 5.6, 1.1, [[("176", {"bold": True}), (" km", {"size": 34, "color": MUTED})]], size=64,
            color=LGREEN, name="s14_176")
A.zoom(n176, 2400, 600)
t2 = text(s, 0.65, 5.3, 5.4, 0.9, "new gas pipeline from Harweel to Raysut, added in 2024 alongside the "
                                  "existing line.", size=17, color=INK, name="s14_t2")
A.fade(t2, 2800, 500)
bbox = (53.25, 16.55, 55.95, 18.55)
frame = (6.55, 1.62, 6.2, 4.9)
rect(s, *frame, fill=grad((0, "0E3A40"), (100, "082A2E"), ang=90), line=(RULE, 0.75), name="!!map_card",
     kind=MSO_SHAPE.ROUNDED_RECTANGLE, adj=[0.03])
pr, land = draw_map(s, bbox, frame, ["Oman", "Yemen"], {
    "Oman": (grad((0, "1C6E5B"), (100, "114E45"), ang=60), (LGREEN, 1.25), (GREEN, 4, 30)),
    "Yemen": ("173F3F", ("2E5E5B", 0.5), None)}, "dmap")
P_H, P_R, P_S, P_M = pr(54.65, 17.75), pr(54.01, 16.94), pr(54.09, 17.02), pr(55.18, 18.13)
old = line(s, P_H[0] - 0.13, P_H[1] - 0.04, P_S[0] - 0.08, P_S[1] - 0.04, "C9A227", 3, dash="dash", name="s14_old")
A.fade(old, 600, 500)
new = line(s, P_H[0] + 0.02, P_H[1] + 0.04, P_R[0] + 0.02, P_R[1] + 0.04, LGREEN, 4.5, glow=(GREEN, 6, 50),
           name="s14_new")
A.wipe(new, 2000, 1400, d="l")
cnd = line(s, P_H[0], P_H[1], P_M[0], P_M[1], OIL, 3, dash="sysDash", name="s14_cond")
A.fade(cnd, 900, 500)
flow(s, A, P_H, P_R, 0.3, GAS_HI, 0.04, 700, t=3400, name="s14_fg")
for (pt, lb, col, dx_, dy_, al) in [(P_H, "Harweel", RED, -1.55, -0.2, "r"), (P_R, "Raysut", INK, -1.55, 0.0, "r"),
                                    (P_S, "Salalah", INK, 0.15, 0.02, "l"), (P_M, "Marmul", INK, 0.15, -0.3, "l")]:
    oval(s, pt[0], pt[1], 0.08 if lb == "Harweel" else 0.055, fill=col, glow=(col, 6, 50) if lb == "Harweel" else None,
         name=f"s14_pt{lb}")
    text(s, pt[0] + dx_, pt[1] + dy_, 1.4, 0.3, lb, size=12 if lb == "Harweel" else 11, color=INK,
         bold=lb == "Harweel", align=al, name=f"s14_lb{lb}")
legend = [("New gas line (2024) · 176 km", LGREEN, None), ("Existing Salalah gas line", "C9A227", "dash"),
          ("Condensate → main line via Marmul", OIL, "sysDash")]
for i, (lb, col, dash) in enumerate(legend):
    y = 2.15 + i * 0.27
    line(s, 6.8, y, 7.2, y, col, 2.5, dash=dash, name=f"s14_lg{i}")
    text(s, 7.3, y - 0.12, 2.85, 0.24, lb, size=10, color=MUTED, name=f"s14_lt{i}")
text(s, pr(55.0, 16.85)[0], pr(55.0, 16.85)[1], 1.6, 0.3, "Arabian Sea", size=11, color=LTEAL, italic=True,
     name="s14_sea")
text(s, 6.75, 1.72, 3.2, 0.25, "Locations and routes approximate", size=9, color=DIM, italic=True, name="s14_nts")
finish_slide(s, A)
notes(s, 40,
      "Big '≈54 million' barrels figure zooms in on the left. On the right, a map of Dhofar: the existing "
      "Salalah gas line (dashed gold) and the condensate route to Marmul appear, then the new 176 km gas line "
      "draws itself from Harweel to Raysut, with gas particles flowing along it. Timeline reaches 2024.",
      "So, did it work? By 2024, gas injection at Zalzala alone had produced about 54 million extra barrels of "
      "oil — barrels that would otherwise have stayed underground. And the story continues at the surface: in "
      "2024, a new 176-kilometre gas line was added alongside the existing one, running from Harweel to Raysut, "
      "near Salalah.",
      "≈54 million extra barrels (Zalzala alone, by 2024) and the 176 km line Harweel→Raysut beside the old one "
      "are from the source. The source's photo caption names the inauguration as the 'Saiib' project (OQ), "
      "August 2024 — verify the official project name before quoting it. Map positions are approximate, as in "
      "the source.")

# =================================================================== SLIDE 15 — conclusion
s, A = base("From salt… to Salalah", "The Harweel journey", 2024)
nodes = [("1997", "Oil found, sealed in salt", "salt"), ("2004", "Tight rock, 14,000 psi, sour gas", "warn"),
         ("2014", "Gas put back to work", "cycle"), ("2019", "One integrated system", "gear"),
         ("2024", "Gas that reaches Salalah", "bolt")]
NX0, NX1, NY = 1.35, 11.95, 3.55
pl_ = line(s, NX0, NY, NX1, NY, RULE, 3, name="s15_path")
gl_ = line(s, NX0, NY, NX1, NY, GREEN, 3, glow=(GREEN, 6, 50), name="s15_pathg")
A.wipe(gl_, 300, 3200, d="l")
for i, (yr, lb, ic) in enumerate(nodes):
    x = NX0 + i * (NX1 - NX0) / 4
    c_ = oval(s, x, NY, 0.52, fill=grad((0, "1A4A48"), (100, "0B2A2A"), path="circle"), line=(LGREEN, 1.5),
              glow=(GREEN, 6, 35), name=f"s15_n{i}")
    t_ = 300 + i * 750
    A.zoom(c_, t_, 450)
    if ic == "salt":
        ics = [rect(s, x - 0.27, NY - 0.2 + j * 0.14, 0.54, 0.12, fill=c, name=f"s15_i{i}_{j}")
               for j, c in enumerate(["DCE6EC", OIL, "DCE6EC"])]
    elif ic == "warn":
        ics = [rect(s, x - 0.27, NY - 0.25, 0.54, 0.46, fill=H2S, kind=MSO_SHAPE.ISOSCELES_TRIANGLE,
                    name=f"s15_i{i}"),
               text(s, x - 0.2, NY - 0.12, 0.4, 0.3, "!", size=16, bold=True, color="3A2E00", align="c",
                    name=f"s15_i{i}t")]
    elif ic == "cycle":
        ics = [rect(s, x - 0.3, NY - 0.3, 0.6, 0.6, fill=GAS, kind=MSO_SHAPE.CIRCULAR_ARROW,
                    name=f"s15_i{i}")]
    elif ic == "gear":
        ics = [rect(s, x - 0.28, NY - 0.28, 0.56, 0.56, fill="C9D5DA", kind=MSO_SHAPE.GEAR_6, name=f"s15_i{i}")]
    else:
        ics = [rect(s, x - 0.22, NY - 0.3, 0.44, 0.6, fill=LGREEN, kind=MSO_SHAPE.LIGHTNING_BOLT,
                    name=f"s15_i{i}")]
    for o in ics:
        A.zoom(o, t_ + 150, 400)
    tt = text(s, x - 1.1, NY + 0.7, 2.2, 0.9, [[(yr, {"bold": True, "color": LGREEN, "size": 14})], [(lb, {})]],
              size=13, color=INK, align="c", name=f"s15_t{i}")
    A.float(tt, t_ + 200, 500)
spark = oval(s, NX0, NY, 0.07, fill="FFFFFF", glow=(LGREEN, 10, 80), name="s15_spark")
A.move(spark, 3600, NX1 - NX0, 0, dur=2600)
quote = text(s, 1.0, 5.45, 11.3, 1.0, [[("Oil once trapped in salt — ", {}),
                                       ("today, the start of gas that reaches Salalah.",
                                        {"color": LGREEN, "bold": True})]],
             size=24, color=INK, align="c", name="s15_quote")
A.fade(quote, 4200, 900)
finish_slide(s, A)
notes(s, 25,
      "The whole story collapses into one glowing path: five milestones light up in sequence, a spark travels "
      "the full journey, and the closing line appears.",
      "So that's Harweel. Oil discovered in 1997, sealed inside salt. Tight rock, extreme pressure and sour gas "
      "that made it look almost impossible to produce. An idea that turned the sour gas into the solution. One "
      "integrated system to run it all — and today, gas flowing all the way to Salalah. Oil that was once trapped "
      "in salt is now the start of gas that reaches Salalah. Thank you.")

# =================================================================== SLIDE 16 — thank you / sources
s = prs.slides.add_slide(THANKS)
q = text(s, 3.51, 4.75, 6.3, 0.4, "Questions & discussion", size=18, color="3F3F3F", align="c", name="ty_q")
src = text(s, 0.9, 6.45, 11.5, 0.75,
           [[("Source material: ", {"bold": True}),
             ("Harweel field explainer video (Shutterbuilt), which cites GeoArabia 10(4); Grosjean et al., Organic "
              "Geochemistry (2009); JPT (2014); Oil & Gas Journal (2007); Oman Observer (2018, 2019, 2025). "
              "Illustrations are simplified; locations and routes are approximate.", {})]],
           size=9, color="797979", align="c", name="ty_src")
finish_slide(s, None, transition="fade", dur=1200)
notes(s, 5, "Branded PDO closing slide from the corporate template.",
      "Thank you. I'm happy to take any questions.")

prs.core_properties.title = "Harweel Field — From Subsurface to Surface"
prs.core_properties.subject = "How Harweel field works: reservoir, challenges, gas injection and surface system"
prs.core_properties.author = "Petroleum Development Oman"
prs.save(OUT)
print("saved", OUT, os.path.getsize(OUT) // 1024, "KB")
