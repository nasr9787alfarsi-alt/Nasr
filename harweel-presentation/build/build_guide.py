# -*- coding: utf-8 -*-
"""Build the bilingual Personal Presenter Guide (a separate file — the original deck is only read).

Usage: python3 build_guide.py <previews_dir with p-01.jpg..p-16.jpg> <out.pptx>
"""
import os
import sys

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guide_content import NUMBERS, PRONOUNCE, SLIDES  # noqa: E402

PREV, OUT = sys.argv[1], sys.argv[2]

GREEN, TEAL, DARK, INK, MUTED = "00A06A", "089AA2", "0E3030", "1F2A2A", "5C6B6A"
SOFT, SOFT2, LINE, AMBER, BLUE = "EEF7F3", "F3F6F7", "D5E2DE", "C9861A", "1C7FA6"
FONT = "Arial"  # ships with Windows & macOS; full Arabic support

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def box(s, x, y, w, h, fill=None, line=None, kind=MSO_SHAPE.RECTANGLE, radius=None, name=None):
    sh = s.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    st = sh._element.find(qn("p:style"))
    if st is not None:
        sh._element.remove(st)
    if radius is not None:
        sh.adjustments[0] = radius
    if fill:
        sh.fill.solid()
        sh.fill.fore_color.rgb = RGBColor.from_string(fill)
    else:
        sh.fill.background()
    if line:
        sh.line.color.rgb = RGBColor.from_string(line)
        sh.line.width = Pt(0.75)
    else:
        sh.line.fill.background()
    if name:
        sh.name = name
    return sh


def tb(s, x, y, w, h, paras, size=12, color=INK, rtl=False, anchor="t", after=3, lsp=None, name=None):
    """paras: list of paragraphs; each = str or list of (text, {bold, color, size, italic})."""
    t = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = t.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.02)
    tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE}[anchor]
    if isinstance(paras, str):
        paras = [paras]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        runs = [(para, {})] if isinstance(para, str) else para
        p.alignment = PP_ALIGN.RIGHT if rtl else PP_ALIGN.LEFT
        p.space_after = Pt(after)
        if lsp:
            p.line_spacing = lsp
        if rtl:
            p._p.get_or_add_pPr().set("rtl", "1")
        for text, o in runs:
            r = p.add_run()
            r.text = text
            f = r.font
            f.size = Pt(o.get("size", size))
            f.bold = o.get("bold", False)
            f.italic = o.get("italic", False)
            f.color.rgb = RGBColor.from_string(o.get("color", color))
            f.name = FONT
            rpr = r._r.get_or_add_rPr()
            if rtl:
                rpr.set("lang", "ar-OM")
            cs = etree.SubElement(rpr, qn("a:cs"))
            cs.set("typeface", FONT)
    if name:
        t.name = name
    return t


def chip(s, x, y, w, h, txt, fill, color="FFFFFF", size=11, bold=True):
    box(s, x, y, w, h, fill, kind=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
    tb(s, x, y, w, h, [[(txt, {"bold": bold, "color": color, "size": size})]], anchor="m", after=0).text_frame \
        .paragraphs[0].alignment = PP_ALIGN.CENTER


def section_label(s, x, y, w, en, ar, color=GREEN):
    f = 0.68 if w < 5 else 0.56
    tb(s, x, y, w * f, 0.3, [[(en, {"bold": True, "color": color, "size": 10 if w < 5 else 11})]], after=0)
    tb(s, x + w * f, y, w * (1 - f), 0.3, [[(ar, {"bold": True, "color": color, "size": 12})]], rtl=True, after=0)


def header(s, d, page, page_ar):
    box(s, 0, 0, 13.333, 0.95, DARK)
    chip(s, 0.45, 0.24, 1.75, 0.48, f"SLIDE {d['n']:02d} / 16", GREEN, size=13)
    tb(s, 2.4, 0.16, 6.9, 0.65, [[(d["title"], {"bold": True, "color": "FFFFFF", "size": 20})]], anchor="m",
       after=0)
    chip(s, 9.45, 0.24, 1.45, 0.48, f"⏱ {d['time']} sec", "FFFFFF", color=DARK, size=12)
    tb(s, 11.05, 0.2, 2.1, 0.6, [[(page, {"bold": True, "color": "A9D9C6", "size": 10})],
                                  [(page_ar, {"bold": True, "color": "A9D9C6", "size": 11})]], after=0)
    s.shapes[-1].text_frame.paragraphs[1]._p.get_or_add_pPr().set("rtl", "1")


def footer(s, txt):
    tb(s, 0.45, 7.17, 12.4, 0.25, [[(txt, {"color": "8A9897", "size": 9})]], after=0)


total = sum(d["time"] for d in SLIDES)

# ------------------------------------------------------------------ cover
s = prs.slides.add_slide(BLANK)
box(s, 0, 0, 13.333, 7.5, DARK)
box(s, 0, 5.2, 13.333, 2.3, "0A2626")
tb(s, 0.8, 1.0, 11.5, 0.4, [[("PERSONAL PRESENTER GUIDE  ·  NOT FOR THE AUDIENCE", {"bold": True, "color": "6FD3A8",
                                                                                     "size": 13})]])
tb(s, 0.8, 1.55, 11.5, 1.0, [[("Harweel Field — From Subsurface to Surface", {"bold": True, "color": "FFFFFF",
                                                                              "size": 36})]])
tb(s, 0.8, 2.6, 11.5, 0.7, [[("دليل المقدّم الشخصي — شرح ثنائي اللغة لكل شريحة", {"bold": True, "color": "CFEFE3",
                                                                                     "size": 24})]], rtl=True)
tb(s, 0.8, 3.55, 11.5, 1.2, [
    [("For each of the 16 slides: Arabic explanation · simple English script · key ideas · what moves on screen · "
      "vocabulary · transition sentence · speaking time.", {"color": "A7C2BE", "size": 15})]])
pv = s.shapes.add_picture(os.path.join(PREV, "p-01.jpg"), Inches(8.9), Inches(5.45), Inches(3.4))
tb(s, 0.8, 5.55, 7.6, 1.5, [
    [("Total speaking time: ", {"color": "FFFFFF", "size": 16}),
     (f"≈ {total // 60} min {total % 60:02d} sec", {"bold": True, "color": "6FD3A8", "size": 16})],
    [("Original file (unchanged): Harweel_Field_From_Subsurface_to_Surface.pptx", {"color": "A7C2BE", "size": 12})]])

# ------------------------------------------------------------------ how to use + timing plan
s = prs.slides.add_slide(BLANK)
box(s, 0, 0, 13.333, 0.95, DARK)
tb(s, 0.45, 0.16, 8, 0.65, [[("How to use this guide  ·  Timing plan", {"bold": True, "color": "FFFFFF",
                                                                         "size": 20})]], anchor="m")
tb(s, 6.9, 0.16, 6.0, 0.65, [[("طريقة استخدام الدليل وخطة الوقت", {"bold": True, "color": "A9D9C6", "size": 18})]],
   rtl=True, anchor="m")
box(s, 0.45, 1.2, 5.6, 5.85, SOFT, LINE, MSO_SHAPE.ROUNDED_RECTANGLE, 0.04)
tb(s, 0.7, 1.35, 5.15, 5.6, [
    [("طريقة المذاكرة", {"bold": True, "color": GREEN, "size": 15})],
    "كل شريحة في العرض الأصلي لها صفحتان هنا:",
    [("الصفحة 1 — الفهم: ", {"bold": True}), ("صورة الشريحة، الشرح بالعربي، الأفكار الرئيسية، والمفردات.", {})],
    [("الصفحة 2 — التقديم: ", {"bold": True}), ("ما تقوله بالإنجليزية، ماذا يظهر على الشاشة ومتى تتكلم، "
                                                 "وجملة الانتقال للشريحة التالية.", {})],
    [("نصيحة: ", {"bold": True}), ("اقرأ الشرح العربي أولاً حتى تفهم الفكرة. ثم اقرأ النص الإنجليزي بصوت عالٍ "
                                   "مرتين. بعد ذلك جرّب أن تشرح الفكرة بكلماتك أنت، مستعينًا فقط بقسم "
                                   "«افهم، لا تحفظ».", {})],
    [("كل شريحة تتقدّم بنقرة واحدة، ", {"bold": True}), ("وبعدها تعمل الحركات تلقائيًا. انتظر الحركة المهمة "
                                                           "ثم تكلّم.", {})],
    [("المعلومات المضافة: ", {"bold": True}), ("أي معلومة ليست من الفيديو مكتوب بجانبها «معلومة عامة».", {})],
], size=13, rtl=True, after=7, lsp=1.1)
# timing table
rows = len(SLIDES) + 2
tbl = s.shapes.add_table(rows, 3, Inches(6.35), Inches(1.2), Inches(6.55), Inches(5.85)).table
tbl.columns[0].width, tbl.columns[1].width, tbl.columns[2].width = Inches(0.75), Inches(4.4), Inches(1.4)
cum = 0


def cell(c, txt, bold=False, color=INK, size=10.5, fill=None, align=PP_ALIGN.LEFT):
    c.text = ""
    p = c.text_frame.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = txt
    r.font.size, r.font.bold, r.font.name = Pt(size), bold, FONT
    r.font.color.rgb = RGBColor.from_string(color)
    c.margin_top = c.margin_bottom = Inches(0.02)
    if fill:
        c.fill.solid()
        c.fill.fore_color.rgb = RGBColor.from_string(fill)


for j, h in enumerate(["Slide", "Topic", "Time (cum.)"]):
    cell(tbl.cell(0, j), h, True, "FFFFFF", 11, DARK)
for i, d in enumerate(SLIDES, 1):
    cum += d["time"]
    f = "FFFFFF" if i % 2 else SOFT2
    cell(tbl.cell(i, 0), f"{d['n']:02d}", True, GREEN, fill=f, align=PP_ALIGN.CENTER)
    cell(tbl.cell(i, 1), d["title"], fill=f)
    cell(tbl.cell(i, 2), f"{d['time']} s  ({cum // 60}:{cum % 60:02d})", fill=f)
cell(tbl.cell(rows - 1, 0), "", fill=SOFT)
cell(tbl.cell(rows - 1, 1), "TOTAL", True, fill=SOFT)
cell(tbl.cell(rows - 1, 2), f"≈ {total // 60} min {total % 60:02d} s", True, GREEN, fill=SOFT)
for r_ in range(rows):
    tbl.rows[r_].height = Inches(5.85 / rows)

# ------------------------------------------------------------------ per-slide pages
for d in SLIDES:
    nxt = next((x for x in SLIDES if x["n"] == d["n"] + 1), None)
    # ---- page 1: understand
    s = prs.slides.add_slide(BLANK)
    header(s, d, "PAGE 1 · UNDERSTAND", "الفهم")
    box(s, 0.43, 1.13, 4.44, 2.54, None, LINE)
    s.shapes.add_picture(os.path.join(PREV, f"p-{d['n']:02d}.jpg"), Inches(0.45), Inches(1.15), Inches(4.4))
    tb(s, 0.45, 3.7, 4.4, 0.25, [[(f"Original slide {d['n']} — preview", {"italic": True, "color": MUTED,
                                                                          "size": 9})]], after=0)
    box(s, 0.45, 4.0, 4.4, 3.1, SOFT, LINE, MSO_SHAPE.ROUNDED_RECTANGLE, 0.05)
    section_label(s, 0.6, 4.08, 4.1, "UNDERSTAND, DON'T MEMORIZE", "افهم، لا تحفظ")
    paras = []
    for en, ar in d["ideas"]:
        paras.append([("● " + en, {"bold": True, "size": 11.5})])
        paras.append([(ar, {"size": 11, "color": MUTED})])
    t = tb(s, 0.6, 4.42, 4.1, 2.65, paras, after=1)
    for k, p in enumerate(t.text_frame.paragraphs):
        if k % 2:
            p.alignment = PP_ALIGN.RIGHT
            p._p.get_or_add_pPr().set("rtl", "1")
            p.space_after = Pt(5)
    # Arabic explanation
    box(s, 5.1, 1.13, 7.78, 3.95, "FFFFFF", LINE, MSO_SHAPE.ROUNDED_RECTANGLE, 0.03)
    tb(s, 5.3, 1.2, 7.4, 0.35, [[("الشرح بالعربي", {"bold": True, "color": GREEN, "size": 14})]], rtl=True, after=0)
    tb(s, 5.3, 1.58, 7.4, 3.45, d["ar"], size=13, rtl=True, after=5, lsp=1.05)
    # vocabulary
    section_label(s, 5.1, 5.18, 7.78, "IMPORTANT VOCABULARY", "المفردات المهمة")
    n = len(d["vocab"])
    vt = s.shapes.add_table(n + 1, 3, Inches(5.1), Inches(5.5), Inches(7.78), Inches(0.3 * (n + 1))).table
    vt.columns[0].width, vt.columns[1].width, vt.columns[2].width = Inches(2.15), Inches(2.0), Inches(3.63)
    for j, h in enumerate(["English term", "المعنى بالعربي", "Simple explanation"]):
        cell(vt.cell(0, j), h, True, "FFFFFF", 10.5, TEAL, PP_ALIGN.RIGHT if j == 1 else PP_ALIGN.LEFT)
    for i, (en, ar, ex) in enumerate(d["vocab"], 1):
        f = "FFFFFF" if i % 2 else SOFT2
        cell(vt.cell(i, 0), en, True, INK, 10.5, f)
        cell(vt.cell(i, 1), ar, False, INK, 11, f, PP_ALIGN.RIGHT)
        vt.cell(i, 1).text_frame.paragraphs[0]._p.get_or_add_pPr().set("rtl", "1")
        cell(vt.cell(i, 2), ex, False, MUTED, 10, f)
    for r_ in range(n + 1):
        vt.rows[r_].height = Inches(0.3)
    footer(s, "Personal preparation only — not for the audience.")

    # ---- page 2: say it
    s = prs.slides.add_slide(BLANK)
    header(s, d, "PAGE 2 · SAY IT", "التقديم")
    box(s, 0.45, 1.13, 6.35, 4.45, "FFFFFF", GREEN, MSO_SHAPE.ROUNDED_RECTANGLE, 0.03)
    section_label(s, 0.65, 1.22, 5.95, "SIMPLE ENGLISH SCRIPT — SAY THIS", "النص الإنجليزي — قل هذا")
    tb(s, 0.65, 1.62, 5.95, 3.9, [[(line, {"size": 15})] for line in d["script"]], after=6, lsp=1.05)
    box(s, 0.45, 5.75, 6.35, 1.35, "FFF6E3", "EBC98A", MSO_SHAPE.ROUNDED_RECTANGLE, 0.06)
    section_label(s, 0.65, 5.83, 5.95, "SLIDE-TO-SLIDE TRANSITION", "جملة الانتقال", AMBER)
    nx = f"→ Next: Slide {nxt['n']} — {nxt['title']}" if nxt else "→ End — open the floor for questions"
    tb(s, 0.65, 6.15, 5.95, 0.95, [[("“" + d["transition"] + "”", {"bold": True, "italic": True, "size": 14})],
                                   [(nx, {"color": MUTED, "size": 10})]], after=2)
    # visual explanation
    box(s, 7.05, 1.13, 5.83, 5.97, SOFT2, LINE, MSO_SHAPE.ROUNDED_RECTANGLE, 0.03)
    section_label(s, 7.2, 1.22, 5.55, "ON SCREEN → WHAT TO SAY", "ماذا يظهر ومتى أتكلم", BLUE)
    paras = []
    for k, (what, ar, say) in enumerate(d["visuals"], 1):
        paras.append([(f"{k}. {what}", {"bold": True, "size": 12})])
        paras.append([(ar, {"size": 11.5, "color": MUTED})])
        paras.append([("Say: ", {"bold": True, "color": GREEN, "size": 11.5}), (say, {"italic": True,
                                                                                    "size": 11.5})])
    t = tb(s, 7.2, 1.6, 5.55, 5.4, paras, after=1)
    for k, p in enumerate(t.text_frame.paragraphs):
        if k % 3 == 1:
            p.alignment = PP_ALIGN.RIGHT
            p._p.get_or_add_pPr().set("rtl", "1")
        if k % 3 == 2:
            p.space_after = Pt(9)
    footer(s, f"Speaking time for this slide: about {d['time']} seconds. Speak slowly — pauses look confident.")

# ------------------------------------------------------------------ pronunciation & numbers
s = prs.slides.add_slide(BLANK)
box(s, 0, 0, 13.333, 0.95, DARK)
tb(s, 0.45, 0.16, 8, 0.65, [[("Pronunciation helper  ·  How to read the numbers", {"bold": True, "color": "FFFFFF",
                                                                                   "size": 20})]], anchor="m")
tb(s, 7.9, 0.16, 5.0, 0.65, [[("النطق وقراءة الأرقام", {"bold": True, "color": "A9D9C6", "size": 18})]], rtl=True,
   anchor="m")
pt = s.shapes.add_table(len(PRONOUNCE) + 1, 3, Inches(0.45), Inches(1.15), Inches(6.6), Inches(5.9)).table
pt.columns[0].width, pt.columns[1].width, pt.columns[2].width = Inches(2.3), Inches(2.4), Inches(1.9)
for j, h in enumerate(["Word", "Say it like", "بالعربي"]):
    cell(pt.cell(0, j), h, True, "FFFFFF", 11, TEAL, PP_ALIGN.RIGHT if j == 2 else PP_ALIGN.LEFT)
for i, (w, say, ar) in enumerate(PRONOUNCE, 1):
    f = "FFFFFF" if i % 2 else SOFT2
    cell(pt.cell(i, 0), w, True, INK, 11, f)
    cell(pt.cell(i, 1), say, False, GREEN, 11, f)
    cell(pt.cell(i, 2), ar, False, INK, 11, f, PP_ALIGN.RIGHT)
    pt.cell(i, 2).text_frame.paragraphs[0]._p.get_or_add_pPr().set("rtl", "1")
for r_ in range(len(PRONOUNCE) + 1):
    pt.rows[r_].height = Inches(5.9 / (len(PRONOUNCE) + 1))
tb(s, 0.45, 7.1, 6.6, 0.3, [[("Capital letters = the stressed part of the word.", {"color": MUTED, "size": 10})]])
nt = s.shapes.add_table(len(NUMBERS) + 1, 2, Inches(7.35), Inches(1.15), Inches(5.55), Inches(4.2)).table
nt.columns[0].width, nt.columns[1].width = Inches(1.6), Inches(3.95)
cell(nt.cell(0, 0), "On screen", True, "FFFFFF", 11, TEAL)
cell(nt.cell(0, 1), "Say it like", True, "FFFFFF", 11, TEAL)
for i, (a, b) in enumerate(NUMBERS, 1):
    f = "FFFFFF" if i % 2 else SOFT2
    cell(nt.cell(i, 0), a, True, INK, 11, f)
    cell(nt.cell(i, 1), b, False, INK, 11, f)
for r_ in range(len(NUMBERS) + 1):
    nt.rows[r_].height = Inches(4.2 / (len(NUMBERS) + 1))
box(s, 7.35, 5.55, 5.55, 1.5, SOFT, LINE, MSO_SHAPE.ROUNDED_RECTANGLE, 0.06)
tb(s, 7.5, 5.62, 5.25, 1.4, [
    [("نصيحة: ", {"bold": True, "color": GREEN}), ("علامة ≈ تُقرأ \"about\". والرمز psi يُقرأ حرفًا حرفًا "
                                                   "P-S-I. قل الأرقام الكبيرة ببطء وتوقف بعدها لحظة.", {})]],
   size=12.5, rtl=True, lsp=1.1)

# ------------------------------------------------------------------ final checklist
s = prs.slides.add_slide(BLANK)
box(s, 0, 0, 13.333, 0.95, DARK)
tb(s, 0.45, 0.16, 8, 0.65, [[("Before you present — checklist", {"bold": True, "color": "FFFFFF", "size": 20})]],
   anchor="m")
tb(s, 7.9, 0.16, 5.0, 0.65, [[("قائمة التحقق قبل العرض", {"bold": True, "color": "A9D9C6", "size": 18})]],
   rtl=True, anchor="m")
items_en = ["Run the original deck once in PowerPoint slideshow mode (check Morph and animations).",
            "One click per slide. Wait for the key animation, then speak.",
            "Practise aloud with a timer — aim for 8 to 9 minutes.",
            "Say “expected” for the 30% figure. Say “alone” for 54 million (Zalzala).",
            "Locations on the maps are approximate — say so if asked.",
            "Do not name the 2024 pipeline project unless you have confirmed the name.",
            "Unknown question? “I will check and come back to you.”"]
items_ar = ["شغّل العرض الأصلي مرة كاملة في PowerPoint للتأكد من الحركات.",
            "نقرة واحدة لكل شريحة. انتظر الحركة المهمة ثم تكلّم.",
            "تدرّب بصوت عالٍ مع ساعة توقيت — الهدف 8 إلى 9 دقائق.",
            "قل «متوقع» مع رقم 30%، وقل «وحده» مع رقم 54 مليون (زلزلة).",
            "المواقع على الخرائط تقريبية — قل ذلك إذا سُئلت.",
            "لا تذكر اسم مشروع خط الغاز 2024 إلا بعد التأكد منه.",
            "سؤال لا تعرف إجابته؟ «سأتأكد وأعود إليك»."]
for i, (en, ar) in enumerate(zip(items_en, items_ar)):
    y = 1.2 + i * 0.83
    box(s, 0.45, y, 12.43, 0.72, SOFT if i % 2 == 0 else "FFFFFF", LINE, MSO_SHAPE.ROUNDED_RECTANGLE, 0.15)
    box(s, 0.62, y + 0.2, 0.32, 0.32, "FFFFFF", GREEN, MSO_SHAPE.ROUNDED_RECTANGLE, 0.2)
    tb(s, 1.1, y, 6.0, 0.72, [[(en, {"size": 12.5})]], anchor="m", after=0)
    tb(s, 7.2, y, 5.5, 0.72, [[(ar, {"size": 12.5})]], rtl=True, anchor="m", after=0)

prs.core_properties.title = "Harweel Field — Personal Presenter Guide"
prs.core_properties.author = "Presenter"
prs.save(OUT)
print("saved", OUT, os.path.getsize(OUT) // 1024, "KB", "slides:", len(prs.slides), "total sec:", total)
