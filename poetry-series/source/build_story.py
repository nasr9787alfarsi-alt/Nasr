#!/usr/bin/env python3
"""Instagram Story (9:16, 1080x1920 css) variant of the series.
Text kept inside the safe zone (~y 250..1670) away from the story UI."""
import os, build
from build import INK, PAPER, GOLD

S = build.S
PLUM = "#2b2230"

SLIDES = [
  dict(n=1, img="a_street.jpg", pos="10% 50%",
       grade="contrast(1.06) saturate(0.88) brightness(0.98)",
       overlays=["linear-gradient(180deg, rgba(24,34,58,.30) 0%, rgba(24,34,58,0) 30%)",
                 "linear-gradient(0deg, rgba(10,8,6,.40) 0%, rgba(10,8,6,0) 25%)"],
       blocks=[
         dict(css="top:285px; left:200px; width:640px;", color=PAPER, align="center",
              lines=[("كم الحياةُ الآن يا صاحِبي؟", "l")]),
         dict(css="top:655px; left:466px; width:360px;", color=INK, align="center",
              lines=[("اثنان..", "xl")]),
         dict(css="top:875px; left:520px; width:320px;", color=INK, align="center",
              lines=[("إلا ضحكة غائبه", "s fade")]),
       ], folio_color=PAPER),
  dict(n=2, img="c_road.jpg", pos="50% 50%",
       grade="contrast(1.08) saturate(0.85) brightness(0.96)",
       overlays=["linear-gradient(0deg, rgba(12,12,14,.62) 0%, rgba(12,12,14,.30) 30%, rgba(12,12,14,0) 48%)"],
       blocks=[
         dict(css="top:1240px; right:72px; width:600px;", color=PAPER, align="right",
              lines=[("أيُّ دروبٍ سوف نمشي بها؟", "l"), ("gap", ""),
                     ("تلك التي", "m"), ("عكس الخُطى ذاهبه", "m")]),
       ], folio_color=PAPER),
  dict(n=3, img="b_tree.jpg", pos="0% 50%",
       grade="contrast(1.07) saturate(0.72) brightness(0.95)",
       overlays=["radial-gradient(ellipse 75% 32% at 18% 90%, rgba(10,9,8,.68) 0%, rgba(10,9,8,.30) 55%, rgba(10,9,8,0) 100%)",
                 "linear-gradient(0deg, rgba(10,8,6,.35) 0%, rgba(10,8,6,0) 20%)"],
       blocks=[
         dict(css="top:1430px; left:36px; width:470px; font-size:42px;", color=PAPER, align="center",
              lines=[("نحن -الرماديين- لم تكتَرث", ""), ("بحزننا أيّامُنا الصاخبه", "")]),
       ], folio_color=PAPER),
  dict(n=4, img="d_books.jpg", pos="60% 50%",
       grade="contrast(1.06) saturate(0.80) brightness(0.94)",
       overlays=["linear-gradient(0deg, rgba(14,11,8,.78) 0%, rgba(14,11,8,.45) 18%, rgba(14,11,8,0) 34%)"],
       blocks=[
         dict(css="top:1480px; right:230px; width:400px;", color=PAPER, align="right",
              lines=[("عشنا..", "xl")]),
         dict(css="top:1565px; right:420px; width:400px;", color=PAPER, align="right",
              lines=[("ومتنا..", "xl")]),
       ], folio_color=PAPER),
  dict(n=5, img="f_grey.jpg", pos="50% 50%",
       grade="contrast(1.05) saturate(0.80) brightness(0.99)",
       overlays=["linear-gradient(0deg, rgba(10,8,6,.30) 0%, rgba(10,8,6,0) 25%)"],
       blocks=[
         dict(css="top:330px; left:140px; width:800px;", color=INK, align="center",
              lines=[("لم يكنْ عُمرُنا في الأرض", "l"), ("إلا حكمةً كاذبه", "l")]),
       ], folio_color=INK),
  dict(n=6, img="e_sunset.jpg", pos="50% 50%",
       grade="contrast(1.05) saturate(0.90) brightness(0.98)",
       overlays=["linear-gradient(0deg, rgba(10,8,6,.30) 0%, rgba(10,8,6,0) 25%)"],
       blocks=[
         dict(css="top:330px; left:190px; width:700px;", color=PLUM, align="center",
              lines=[("وما اسْمُنا؟", "xl"), ("ليس لنا أوجه", "m")]),
       ], folio_color=PLUM),
  dict(n=7, img="g_night.jpg", pos="15% 50%",
       grade="contrast(1.04) saturate(0.95) brightness(0.97)",
       overlays=[],
       blocks=[
         dict(css="top:300px; right:22px; width:470px; font-size:45px;", color=GOLD, align="center",
              lines=[("فهل ستُجْدي الأحرُفُ الشاحبه؟", "")]),
       ], folio_color=GOLD),
]

def main():
    build.SLIDES = SLIDES
    build.TPL = (build.TPL.replace("width:1080px;height:1350px", "width:1080px;height:1920px")
                 .replace(".folio{position:absolute;bottom:44px", ".folio{position:absolute;bottom:270px"))
    os.makedirs(os.path.join(S, "html"), exist_ok=True)
    build.build()

if __name__ == "__main__":
    main()
