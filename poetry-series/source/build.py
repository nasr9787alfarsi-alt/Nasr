#!/usr/bin/env python3
"""Generate the HTML pages for the poetry series (one per slide)."""
import json, os, sys

S = os.path.dirname(os.path.abspath(__file__))
INK = "#1f2430"
PAPER = "#f6f0e4"
GOLD = "#e3c48c"

# Each block: position (css), lines [(text, class)], color, align
SLIDES = [
  dict(n=1, img="a_street.jpg", pos="50% 0%",
       grade="contrast(1.06) saturate(0.88) brightness(0.98)",
       overlays=["linear-gradient(180deg, rgba(24,34,58,.30) 0%, rgba(24,34,58,0) 30%)",
                 "linear-gradient(0deg, rgba(10,8,6,.35) 0%, rgba(10,8,6,0) 25%)"],
       blocks=[
         dict(css="top:118px; left:170px; width:540px;", color=PAPER, align="center",
              lines=[("كم الحياةُ الآن يا صاحِبي؟", "l")]),
         dict(css="top:470px; left:330px; width:360px;", color=INK, align="center",
              lines=[("اثنان..", "xl")]),
         dict(css="top:640px; left:370px; width:340px;", color=INK, align="center",
              lines=[("إلا ضحكة غائبه", "s fade")]),
       ], folio_color=PAPER),
  dict(n=2, img="c_road.jpg", pos="50% 100%",
       grade="contrast(1.08) saturate(0.85) brightness(0.96)",
       overlays=["linear-gradient(0deg, rgba(12,12,14,.62) 0%, rgba(12,12,14,.25) 28%, rgba(12,12,14,0) 45%)"],
       blocks=[
         dict(css="top:905px; right:72px; width:560px;", color=PAPER, align="right",
              lines=[("أيُّ دروبٍ سوف نمشي بها؟", "l"), ("gap", ""),
                     ("تلك التي", "m"), ("عكس الخُطى ذاهبه", "m")]),
       ], folio_color=PAPER),
  dict(n=3, img="b_tree.jpg", pos="50% 0%",
       grade="contrast(1.07) saturate(0.72) brightness(0.95)",
       overlays=["linear-gradient(180deg, rgba(20,30,60,.28) 0%, rgba(20,30,60,0) 22%)",
                 "linear-gradient(0deg, rgba(10,8,6,.30) 0%, rgba(10,8,6,0) 25%)"],
       blocks=[
         dict(css="top:62px; left:268px; width:460px;", color=PAPER, align="center",
              lines=[("نحن -الرماديين- لم تكتَرث", "m"), ("بحزننا أيّامُنا الصاخبه", "m")]),
       ], folio_color=PAPER),
  dict(n=4, img="d_books.jpg", pos="50% 100%",
       grade="contrast(1.06) saturate(0.80) brightness(0.94)",
       overlays=["linear-gradient(0deg, rgba(14,11,8,.72) 0%, rgba(14,11,8,.35) 16%, rgba(14,11,8,0) 30%)"],
       blocks=[
         dict(css="top:1092px; right:170px; width:400px;", color=PAPER, align="right",
              lines=[("عشنا..", "xl")]),
         dict(css="top:1172px; right:370px; width:400px;", color=PAPER, align="right",
              lines=[("ومتنا..", "xl")]),
       ], folio_color=PAPER),
  dict(n=5, img="f_grey.jpg", pos="50% 0%",
       grade="contrast(1.05) saturate(0.80) brightness(0.99)",
       overlays=["linear-gradient(0deg, rgba(10,8,6,.30) 0%, rgba(10,8,6,0) 25%)"],
       blocks=[
         dict(css="top:250px; left:140px; width:800px;", color=INK, align="center",
              lines=[("لم يكنْ عُمرُنا في الأرض", "l"), ("إلا حكمةً كاذبه", "l")]),
       ], folio_color=INK),
  dict(n=6, img="e_sunset.jpg", pos="50% 0%",
       grade="contrast(1.05) saturate(0.90) brightness(0.98)",
       overlays=["linear-gradient(0deg, rgba(10,8,6,.30) 0%, rgba(10,8,6,0) 25%)"],
       blocks=[
         dict(css="top:180px; left:190px; width:700px;", color="#2b2230", align="center",
              lines=[("وما اسْمُنا؟", "xl"), ("ليس لنا أوجه", "m")]),
       ], folio_color="#2b2230"),
  dict(n=7, img="g_night.jpg", pos="50% 0%",
       grade="contrast(1.04) saturate(0.95) brightness(0.97)",
       overlays=[],
       blocks=[
         dict(css="top:150px; left:455px; width:500px; font-size:52px;", color=GOLD, align="center",
              lines=[("فهل ستُجْدي الأحرُفُ الشاحبه؟", "")]),
       ], folio_color=GOLD),
]

ARABIC_NUM = "٠١٢٣٤٥٦٧٨٩"
def an(n): return "".join(ARABIC_NUM[int(c)] for c in str(n))

GRAIN = ("data:image/svg+xml;utf8," +
  "<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'>"
  "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/>"
  "<feColorMatrix values='0 0 0 0 .5 0 0 0 0 .5 0 0 0 0 .5 0 0 0 .9 0'/></filter>"
  "<rect width='100%' height='100%' filter='url(%23n)'/></svg>")

TPL = """<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<link rel="stylesheet" href="../fonts/local.css">
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px;background:#000;overflow:hidden}
.f{position:relative;width:1080px;height:1350px;overflow:hidden}
.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:__POS__;filter:__GRADE__}
.ov{position:absolute;inset:0}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse 85% 75% at 50% 48%, rgba(0,0,0,0) 55%, rgba(0,0,0,.38) 100%)}
.grain{position:absolute;inset:0;background-image:url("__GRAIN__");opacity:.07;mix-blend-mode:overlay}
.b{position:absolute;font-family:'Amiri',serif;font-feature-settings:"kern","liga","calt";direction:rtl}
.b p{white-space:nowrap;line-height:1.55}
.xl{font-size:74px;line-height:1.3!important}
.l{font-size:54px}
.m{font-size:46px}
.s{font-size:38px}
.fade{opacity:.7}
.gap{height:14px}
.folio{position:absolute;bottom:44px;left:56px;font-family:'Reem Kufi',sans-serif;font-size:15px;
  letter-spacing:.12em;display:flex;align-items:center;gap:14px;direction:ltr;opacity:.78}
.folio i{display:block;width:34px;height:1px;background:currentColor;opacity:.7}
</style></head><body><div class="f">
<img class="bg" src="../src/__IMG__">
__OVERLAYS__
<div class="vig"></div><div class="grain"></div>
__BLOCKS__
<div class="folio" style="color:__FC__"><span>__N__</span><i></i><span>٧</span></div>
</div></body></html>"""

def shadow(color):
    # light text -> soft dark halo; dark text -> faint light halo
    if color in (INK, "#2b2230"):
        return "0 0 18px rgba(255,248,236,.35)"
    return "0 1px 2px rgba(0,0,0,.35), 0 0 22px rgba(0,0,0,.30)"

def build():
    os.makedirs(os.path.join(S, "html"), exist_ok=True)
    for sl in SLIDES:
        ov = "\n".join(f'<div class="ov" style="background:{o}"></div>' for o in sl["overlays"])
        bl = []
        for b in sl["blocks"]:
            ps = "".join('<p class="gap"></p>' if t == "gap" else f'<p class="{c}">{t}</p>' for t, c in b["lines"])
            bl.append(f'<div class="b" style="{b["css"]}color:{b["color"]};text-align:{b["align"]};'
                      f'text-shadow:{shadow(b["color"])}">{ps}</div>')
        h = (TPL.replace("__POS__", sl["pos"]).replace("__GRADE__", sl["grade"])
               .replace("__GRAIN__", GRAIN).replace("__IMG__", sl["img"])
               .replace("__OVERLAYS__", ov).replace("__BLOCKS__", "\n".join(bl))
               .replace("__FC__", sl["folio_color"]).replace("__N__", an(sl["n"])))
        open(os.path.join(S, "html", f"{sl['n']:02d}.html"), "w").write(h)

if __name__ == "__main__":
    build()
