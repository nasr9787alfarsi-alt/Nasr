# -*- coding: utf-8 -*-
"""Stage 3: animated number experiences on top of the approved sound-design deck.

Usage: python3 add_counters.py <sound_design.pptx> <stage_out.pptx> <sfx_dir> <cues.json>
Then:  python3 add_sound.py <stage_out.pptx> <sfx_dir> <final.pptx> <cues.json>

Native technique (no video, no add-ins): a counter is a stack of editable text boxes,
one per value, revealed in sequence by 'Appear' effects whose times follow the SAME
accelerate/decelerate curve PowerPoint uses for the matching needle / motion path,
so digits, needle, playheads and sounds stay in sync. Every frame is opaque (panel
colour, or PowerPoint's 'slide background fill'), with the final value on top, so
the slide still reads correctly in Normal view, print and PDF.
Only slides 4, 7, 12 and 14 are touched.
"""
import copy
import json
import math
import os
import sys
import types
import wave

import numpy as np
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pptlib import E, Anim, _frag, grad, oval, poly, rect, style, text  # noqa: E402

SRC, OUT, SFX, CUES = sys.argv[1:5]
os.makedirs(SFX, exist_ok=True)

INK, MUTED, DIM = "F3F8F7", "A7C2BE", "5F827D"
GREEN, TEAL, LGREEN, LTEAL, RULE = "00B477", "089AA2", "76DFA5", "59BDC2", "2B5A57"
OIL, OIL_HI = "F2A93B", "FFD27A"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
R_EMBED = qn("r:embed")


# ------------------------------------------------------------------ easing (PowerPoint/SMIL accel-decel)
def ease(t, a=0.0, d=0.0):
    """Progress 0..1 of a PowerPoint effect with accel=a, decel=d (fractions): linear speed ramps."""
    t = min(max(t, 0.0), 1.0)
    v = 1.0 / (1.0 - a / 2 - d / 2)
    if a and t < a:
        return v * t * t / (2 * a)
    pa = v * a / 2
    if t <= 1 - d:
        return pa + v * (t - a)
    pb = pa + v * (1 - d - a)
    u = t - (1 - d)
    return pb + v * u - v * u * u / (2 * d)


def inv(f, a=0.0, d=0.0):
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if ease(mid, a, d) < f else (lo, mid)
    return (lo + hi) / 2


def frames(start, dur, final, a, d, step):
    """[(time_ms, value)] — value changes only, last = exact final at start+dur."""
    out = [(start, 0)]
    k = 1
    while start + k * step < start + dur:
        v = int(round(final * ease(k * step / dur, a, d)))
        if v != out[-1][1] and v < final:
            out.append((start + k * step, v))
        k += 1
    out.append((start + dur, final))
    return out


# ------------------------------------------------------------------ XML helpers
def find(slide, name):
    for sh in slide.shapes:
        if sh.name == name:
            return sh
    raise KeyError(name)


def group(slide):
    for c in slide._element.iter(P + "cTn"):
        if c.get("id") == "4":
            return c.find(P + "childTnLst")
    raise RuntimeError("no timing group")


def effect(slide, spid, cls):
    for c in slide._element.iter(P + "cTn"):
        if c.get("presetClass") == cls and c.find(f"{P}childTnLst//{P}spTgt[@spid='{spid}']") is not None:
            return c
    raise KeyError((spid, cls))


def set_delay(ctn, ms):
    ctn.find(f"{P}stCondLst/{P}cond").set("delay", str(int(ms)))


def drop_sound(slide, ctn):
    sub = ctn.find(P + "subTnLst")
    if sub is None:
        return
    rids = [e.get(R_EMBED) for e in sub.iter(P + "sndTgt")]
    ctn.remove(sub)
    for rid in rids:
        slide.part.drop_rel(rid)


def to_appear(ctn, ms):
    """Turn an entrance into an instant 'Appear' (keeps its node, so ids stay valid)."""
    ctn.set("presetID", "1"), ctn.set("presetSubtype", "0")
    kids = ctn.find(P + "childTnLst")
    for ch in list(kids):
        if ch.tag != P + "set":
            kids.remove(ch)
    set_delay(ctn, ms)


def to_fade(ctn):
    ctn.set("presetID", "10"), ctn.set("presetSubtype", "0")
    kids = ctn.find(P + "childTnLst")
    for ch in list(kids):
        if ch.tag == P + "anim":
            kids.remove(ch)


def remove_shape_and_effects(slide, sh):
    sid = str(sh.shape_id)
    for par in list(group(slide)):
        if par.find(f".//{P}spTgt[@spid='{sid}']") is not None:
            for ctn in par.iter(P + "cTn"):
                drop_sound(slide, ctn)
            group(slide).remove(par)
    for b in slide._element.iter(P + "bldP"):
        if b.get("spid") == sid:
            b.getparent().remove(b)
    sh._element.getparent().remove(sh._element)


def merge(slide, A):
    """Append an Anim's effects into the slide's existing (auto-start) timing group."""
    root = _frag(A.xml())[0]
    ids = [int(c.get("id")) for c in slide._element.iter(P + "cTn") if c.get("id")]
    off = max(ids) - 4
    new4 = [c for c in root.iter(P + "cTn") if c.get("id") == "4"][0].find(P + "childTnLst")
    for c in new4.iter(P + "cTn"):
        if c.get("id"):
            c.set("id", str(int(c.get("id")) + off))
    g = group(slide)
    for par in list(new4):
        g.append(par)
    bl = root.find(P + "bldLst")
    if bl is not None:
        timing = slide._element.find(P + "timing")
        tbl = timing.find(P + "bldLst")
        if tbl is None:
            tbl = _frag("<p:bldLst/>")[0]
            timing.append(tbl)
        have = {b.get("spid") for b in tbl}
        for b in list(bl):
            if b.get("spid") not in have:
                tbl.append(b)


def next_id(slide):
    return max(int(e.get("id")) for e in slide._element.iter(P + "cNvPr")) + 1


def bgfill(el):
    """PowerPoint 'Slide background fill': opaque, yet visually identical to the background."""
    el.set("useBgFill", "1")
    spPr = el.find(P + "spPr")
    for t in ("a:noFill", "a:solidFill", "a:gradFill", "a:pattFill", "a:blipFill"):
        for f in spPr.findall(qn(t)):
            spPr.remove(f)


def clone(slide, src_el, name, texts):
    el = copy.deepcopy(src_el)
    nv = el.find(f"{P}nvSpPr/{P}cNvPr")
    nv.set("id", str(next_id(slide))), nv.set("name", name)
    for ext in nv.findall(qn("a:extLst")):
        nv.remove(ext)
    ts = list(el.iter(qn("a:t")))
    for t_el, s in zip(ts, texts):
        t_el.text = s
    src_el.addprevious(el)  # below the final value in z-order
    return types.SimpleNamespace(shape_id=int(nv.get("id")), _element=el)


def to_back_of(el, ref_el):
    el.getparent().remove(el)
    ref_el.addprevious(el)


def add_note(slide, txt):
    tf = slide.notes_slide.notes_text_frame
    tf.text = tf.text + "\n\n" + txt


# ------------------------------------------------------------------ audio helpers
SR = 32000
rng = np.random.default_rng(7)


def lp(x, f, o=4):
    return signal.sosfilt(signal.butter(o, f, "lowpass", fs=SR, output="sos"), x)


def bp(x, lo, hi, o=4):
    return signal.sosfilt(signal.butter(o, [lo, hi], "bandpass", fs=SR, output="sos"), x)


def place(buf, snd, t, g=1.0):
    i = int(t * SR)
    n = min(len(snd), len(buf) - i)
    if n > 0:
        buf[i:i + n] += snd[:n] * g


def tick(f=2500, dec=0.0016, m=0.014):
    tt = np.arange(int(m * SR)) / SR
    x = np.sin(2 * np.pi * f * tt) * np.exp(-tt / dec) + 0.5 * rng.standard_normal(len(tt)) * np.exp(-tt / 0.0005)
    return bp(x, 800, 7500)


def flap(m=0.03):
    """soft mechanical number-flip (split-flap leaf): short band-limited noise transient."""
    tt = np.arange(int(m * SR)) / SR
    x = rng.standard_normal(len(tt)) * (np.exp(-tt / 0.004) + 0.3 * np.exp(-(tt - 0.009).clip(0) / 0.003) *
                                        (tt > 0.009))
    return bp(x, 1200, 5200, 2)


def impact(dur=1.0, f0=62, bright=0.15):
    """soft cinematic 'arrival': low sine thump + filtered air, no hard transient."""
    tt = np.arange(int(dur * SR)) / SR
    th = np.sin(2 * np.pi * f0 * tt * (1 - 0.15 * tt)) * np.exp(-tt / 0.28) * (1 - np.exp(-tt / 0.006))
    air = lp(rng.standard_normal(len(tt)), 1400) * np.exp(-tt / 0.35) * bright * (1 - np.exp(-tt / 0.02))
    return th + air


def reverb(x, tail=0.5, mix=0.16, tone=4000):
    n = int(tail * SR)
    ir = lp(rng.standard_normal(n), tone, 2) * np.exp(-np.linspace(0, 7, n))
    wet = signal.fftconvolve(x, ir)[: len(x)]
    wet *= np.sqrt(np.mean(x ** 2) / (np.mean(wet ** 2) + 1e-12))
    return (1 - mix) * x + mix * wet


def write(name, x, rms_db, peak_db=-6.0):
    x = x - np.mean(x)
    n = len(x)
    e = np.ones(n)
    e[:80] = np.linspace(0, 1, 80)
    e[-int(0.08 * SR):] = np.linspace(1, 0, int(0.08 * SR))
    x = x * e
    x *= 10 ** (rms_db / 20) / (np.sqrt(np.mean(x ** 2)) + 1e-12)
    pk = np.abs(x).max()
    if pk > 10 ** (peak_db / 20):
        x *= 10 ** (peak_db / 20) / pk
    with wave.open(os.path.join(SFX, name + ".wav"), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(SR)
        w.writeframes(np.clip(x * 32767, -32768, 32767).astype("<i2").tobytes())
    return n / SR


prs = Presentation(SRC)
S = list(prs.slides)
cues = {}
summary = []

# =================================================================== SLIDE 7 — hybrid pressure instrument
s = S[6]
A = Anim()
GX, GY, GR = 3.55, 4.25, 1.95
T7, D7, DEC7 = 1400, 3000, 0.8           # needle: start, duration, decelerate fraction
dial = find(s, "s7_dial")
bezel = oval(s, GX, GY, GR + 0.38, fill=grad((0, "F4F7F8"), (30, "A3AFB4"), (52, "56646A"), (75, "CDD5D8"),
                                              (100, "6A787E"), ang=45),
             line=("2E3B40", 0.75), shadow=(22, 6, 90, "000000", 55), name="s7_bezel")
to_back_of(bezel._element, dial._element)
A.zoom(bezel, 100, 500)
panel = rect(s, GX - 0.95, 5.3, 1.9, 0.6, fill="041413", line=(LTEAL, 0.75, 60), kind=MSO_SHAPE.ROUNDED_RECTANGLE,
             adj=[0.2], name="s7_lcd")
A.fade(panel, 900, 400)
fr7 = frames(T7, D7, 14000, 0.0, DEC7, 60)
for i, (t_, v) in enumerate(fr7):
    last = i == len(fr7) - 1
    tb = text(s, GX - 0.85, 5.34, 1.7, 0.52, f"{v:,}", size=24, color=LGREEN, bold=True, align="c", anchor="m",
              spc=1, name="s7_lcd_final" if last else f"s7_lcd_{i:02d}")
    style(tb, fill="041413", line=None)
    if i == 0:
        A.fade(tb, 900, 400)
    else:
        A.appear(tb, t_)
glass = oval(s, GX, GY, GR + 0.24, fill=grad((0, "FFFFFF", 17), (38, "FFFFFF", 4), (60, "FFFFFF", 0),
                                              (100, "FFFFFF", 0), ang=90), name="s7_glass")
A.zoom(glass, 100, 500)
needle = find(s, "s7_needle")
nc = effect(s, needle.shape_id, "emph")
nc.set("decel", str(int(DEC7 * 100000)))
nc.find(f"{P}childTnLst/{P}animRot/{P}cBhvr/{P}cTn").set("dur", str(D7))
drop_sound(s, nc)
for nm, ms in (("!!bignum", T7 + D7 + 150), ("s7_t1", T7 + D7 + 550), ("s7_card", T7 + D7 + 950),
               ("s7_ct", T7 + D7 + 950)):
    set_delay(effect(s, find(s, nm).shape_id, "entr"), ms)
merge(s, A)
# sound: one mechanical tick per 500 psi, timed on the needle's real deceleration curve, then the settle + soft arrival
L = D7 / 1000 + 1.1
buf = np.zeros(int(L * SR))
for k in range(1, 29):
    tk = inv(k * 500 / 14000, 0.0, DEC7) * D7 / 1000
    place(buf, tick(rng.uniform(2300, 2800)), tk, 0.55 + 0.08 * rng.standard_normal())
place(buf, lp(tick(1100, 0.006, 0.05), 3000), D7 / 1000 - 0.01, 1.2)  # needle settles
place(buf, impact(1.0, 58, 0.12), D7 / 1000, 1.1)
buf += 0.035 * bp(rng.standard_normal(len(buf)), 2500, 8000) * np.clip(1 - np.arange(len(buf)) / (D7 / 1000 * SR), 0, 1)
d = write("gauge_counter", reverb(buf, 0.35, 0.12), -31)
cues[7] = [["s7_needle", "emph", "gauge_counter"]]
summary.append(f"S7 needle+LCD 0 -> 14,000 psi over {D7} ms ({len(fr7)} readings), sound {d:.2f}s")
add_note(s, "NUMBER ANIMATION: hybrid instrument. The needle and the digital readout run together from 0 to "
            "14,000 psi on the same slowing curve (3 s), with mechanical ticks every 500 psi. Both settle exactly "
            "on 14,000, then a soft arrival sound plays and the headline appears. Let the needle land, pause, then say "
            "'fourteen thousand P-S-I'.")

# =================================================================== SLIDE 4 — journey through geological time
s = S[3]
A = Anim()
T4, D4, AC4, DE4 = 600, 3500, 0.35, 0.5
X0, X1, YB = 6.6, 12.6, 5.55


def xm(ma):
    return X1 - ma / 540 * (X1 - X0)


# counter: the existing '540' becomes the final reading; frames sit below it
big = find(s, "!!bignum")
big_el = big._element
big.width = E(3.05)
big_el.find(f"{P}txBody/{qn('a:bodyPr')}").set("wrap", "none")
bgfill(big_el)
big_el.find(f"{P}nvSpPr/{P}cNvPr").set("name", "s4_count_final")  # avoid Morph ghosting of the frames
bc = effect(s, big.shape_id, "entr")
drop_sound(s, bc)
to_appear(bc, T4 + D4)
fr4 = frames(T4, D4, 540, AC4, DE4, 70)
for i, (t_, v) in enumerate(fr4[:-1]):
    f = clone(s, big_el, f"s4_count_{i:02d}", [str(v)])
    if i == 0:
        A.fade(f, 300, 400)
    else:
        A.appear(f, t_)
lab = text(s, 9.75, 1.95, 2.95, 0.3, "MILLION YEARS AGO", size=12, color=GREEN, bold=True, spc=2, name="s4_unit")
A.fade(lab, 300, 400)
# period readout, switched exactly when the counter crosses each ICS boundary (Ma)
PERIODS = [(0, "CENOZOIC ERA", "Quaternary"), (2.58, "CENOZOIC ERA", "Neogene"), (23.03, "CENOZOIC ERA", "Paleogene"),
           (66.0, "MESOZOIC ERA", "Cretaceous"), (145.0, "MESOZOIC ERA", "Jurassic"),
           (201.4, "MESOZOIC ERA", "Triassic"), (251.902, "PALEOZOIC ERA", "Permian"),
           (298.9, "PALEOZOIC ERA", "Carboniferous"), (358.9, "PALEOZOIC ERA", "Devonian"),
           (419.2, "PALEOZOIC ERA", "Silurian"), (443.8, "PALEOZOIC ERA", "Ordovician"),
           (485.4, "PALEOZOIC ERA", "Cambrian")]
cross = []
for i, (ma, era, per) in enumerate(PERIODS):
    t_ = 300 if i == 0 else T4 + D4 * inv(ma / 540, AC4, DE4)
    cross.append(t_)
    pf = text(s, 9.75, 2.3, 2.95, 0.95, [[(era, {"size": 11, "bold": True, "color": MUTED, "spc": 1.5})],
                                       [(per, {"size": 22, "bold": True, "color": INK})]], name=f"s4_period_{i:02d}")
    bgfill(pf._element)
    A.fade(pf, 300, 400) if i == 0 else A.appear(pf, t_)
pf = text(s, 9.75, 2.3, 2.95, 0.95, [[("END OF THE PRECAMBRIAN", {"size": 11, "bold": True, "color": OIL, "spc": 1.5})],
                                   [("Ediacaran–Cambrian boundary", {"size": 20, "bold": True, "color": OIL_HI})]],
          name="s4_period_final")
bgfill(pf._element)
A.fade(pf, T4 + D4 + 80, 500)
# geological time ribbon (ICS colours) replaces the plain gradient bar, same place & z-order
bar = find(s, "s4_bar")
bar_el = bar._element
BANDS = [(540, 538.8, "FED96A"), (538.8, 485.4, "7FA056"), (485.4, 443.8, "009270"), (443.8, 419.2, "B3E1B6"),
         (419.2, 358.9, "CB8C37"), (358.9, 298.9, "67A599"), (298.9, 251.902, "F04028"), (251.902, 201.4, "812B92"),
         (201.4, 145.0, "34B2C9"), (145.0, 66.0, "7FC64E"), (66.0, 23.03, "FD9A52"), (23.03, 2.58, "FFE619"),
         (2.58, 0, "F9F97F")]
for j, (a_, b_, col) in enumerate(BANDS):
    band = rect(s, xm(a_), YB - 0.06, xm(b_) - xm(a_), 0.12, fill=(col, 82), name=f"s4_band{j:02d}")
    to_back_of(band._element, bar_el)
    A.fade(band, 300, 500)
remove_shape_and_effects(s, bar)
# markers follow the playhead
t230 = T4 + D4 * inv(230 / 540, AC4, DE4)
for nm, ms in (("s4_m0", 300), ("s4_t0", 300), ("s4_m230", t230), ("s4_t230", t230 + 60),
               ("s4_m540", T4 + D4), ("s4_t540", T4 + D4 + 60), ("s4_sub", T4 + D4 + 300),
               ("s4_body", T4 + D4 + 700)):
    set_delay(effect(s, find(s, nm).shape_id, "entr"), ms)
# rock layers change in step with the journey: a scan line descends from the surface (today) to the
# oil-bearing salt section (~540 Ma), dimming each layer it has passed
BX, BY, BW, DX, DY, SC = 0.95, 2.95, 3.9, 1.0, 0.5, 0.82
STR = [("sand", 0.22), ("rock1", 0.52), ("rock2", 0.48), ("rock3", 0.44), ("salt1", 0.38), ("oil1", 0.30),
       ("salt2", 0.38), ("oil2", 0.30), ("salt3", 0.42)]
yb, y = {}, BY
for k, th in STR:
    yb[k] = (y, y + th * SC)
    y += th * SC
Y_END = yb["oil2"][1]


def slab(y0, y1, top=False):
    pts = [(BX, y0)] + ([(BX + DX, y0 - DY), (BX + BW + DX, y0 - DY)] if top else [(BX + BW, y0),
                                                                                   (BX + BW + DX, y0 - DY)])
    return pts + [(BX + BW + DX, y1 - DY), (BX + BW, y1), (BX, y1)]


for k in ("sand", "rock1", "rock2", "rock3", "salt1"):
    y0, y1 = yb[k]
    tc = T4 + D4 * inv((y1 - BY) / (Y_END - BY), AC4, DE4)
    vl = poly(s, slab(y0, y1, k == "sand"), fill=("031312", 48), name=f"s4_veil_{k}")
    A.fade(vl, tc - 120, 380)
oz = poly(s, slab(yb["oil1"][0], yb["oil2"][1]), fill=(OIL, 20), glow=(OIL, 8, 45), name="s4_oilzone")
A.fade(oz, T4 + D4, 600)
scan = poly(s, [(BX, BY), (BX + BW, BY), (BX + BW + DX, BY - DY)], fill=None, line=(LGREEN, 2.25), closed=False,
            glow=(GREEN, 7, 70), name="s4_scan")
A.fade(scan, 300, 300)
A.move(scan, T4, 0, Y_END - BY, dur=D4, repeat=False, accel=int(AC4 * 1e5), decel=int(DE4 * 1e5))
A.out(scan, T4 + D4 + 250, 500)
ph = oval(s, X1, YB, 0.15, fill=None, line=(OIL_HI, 1.75), glow=(OIL, 8, 60), name="s4_playhead")
A.fade(ph, 300, 300)
A.move(ph, T4, -(X1 - X0), 0, dur=D4, repeat=False, accel=int(AC4 * 1e5), decel=int(DE4 * 1e5))
A.pulse(find(s, "!!ruler_oil"), T4 + D4, 1.25, 450, repeat=False)
merge(s, A)
# sound: split-flap leaves on every counter change, accents at period boundaries, a low descending
# 'deep-time' bed, and a soft arrival at 540
L = D4 / 1000 + 1.3
buf = np.zeros(int(L * SR))
for t_, _ in fr4[1:]:
    place(buf, flap(), (t_ - T4) / 1000, 0.5 + 0.1 * rng.standard_normal())
for t_ in cross[1:]:
    place(buf, flap(0.04), (t_ - T4) / 1000 + 0.004, 0.9)
tt = np.arange(len(buf)) / SR
bed = (np.sin(2 * np.pi * (70 - 18 * np.clip(tt / (D4 / 1000), 0, 1)) * tt) * 0.5 +
       lp(rng.standard_normal(len(buf)), 260) * 0.8)
bed *= np.clip(tt / 0.6, 0, 1) * np.clip((D4 / 1000 + 0.1 - tt) / 0.5, 0, 1)
buf += bed * 0.22
place(buf, impact(1.2, 52, 0.2), D4 / 1000, 1.25)
d = write("deep_time_counter", reverb(buf, 0.6, 0.18, 3000), -30)
cues[4] = [["s4_playhead", "path", "deep_time_counter"]]
summary.append(f"S4 counter 0 -> 540 Ma over {D4} ms ({len(fr4)} readings), {len(PERIODS)} period changes, "
               f"sound {d:.2f}s")
add_note(s, "NUMBER ANIMATION: a journey back through geological time. The counter runs from today (0) back to "
            "540 million years, speeding up and then slowing down. The period name changes exactly as the counter "
            "crosses each official boundary of the International Chronostratigraphic Chart: Quaternary, Neogene, "
            "Paleogene, Cretaceous, Jurassic, Triassic, Permian, Carboniferous, Devonian, Silurian, Ordovician, "
            "Cambrian. Meanwhile a playhead travels the colour-coded time ribbon and a scan line descends through the "
            "rock layers. It lands on 'Ediacaran–Cambrian boundary', the end of the Precambrian (the base of the "
            "Cambrian is 538.8 million years ago, so about 540 sits on that boundary). Suggested line: 'Let's travel "
            "back in time… past the dinosaurs… all the way to the very start of the Cambrian.'\n"
            "ACCURACY: the period dates and colours follow the ICS chart. The scan line through the layers is "
            "schematic: it does not assign ages to the individual rock layers above the salt.")

# =================================================================== SLIDE 14 — production & distance counters
s = S[13]
A = Anim()
big = find(s, "!!bignum")
bgfill(big._element)
bc = effect(s, big.shape_id, "entr")
drop_sound(s, bc)
T14, D14 = 300, 1200
to_appear(bc, T14 + D14)
fr14 = frames(T14, D14, 54, 0.0, 0.6, 50)
first = None
for i, (t_, v) in enumerate(fr14[:-1]):
    f = clone(s, big._element, f"s14_count_{i:02d}", [f"≈ {v}", " million"])
    if i == 0:
        A.fade(f, T14, 150)
        first = f"s14_count_{i:02d}"
    else:
        A.appear(f, t_)
k176 = find(s, "s14_176")
bgfill(k176._element)
T176, D176 = 2000, 1400  # same start and length as the new pipeline drawing on the map
to_appear(effect(s, k176.shape_id, "entr"), T176 + D176)
fr176 = frames(T176, D176, 176, 0.0, 0.25, 60)
for i, (t_, v) in enumerate(fr176[:-1]):
    f = clone(s, k176._element, f"s14_km_{i:02d}", [str(v), " km"])
    A.fade(f, T176, 150) if i == 0 else A.appear(f, t_)
merge(s, A)
L = D14 / 1000 + 0.42
buf = np.zeros(int(L * SR))
for t_, _ in fr14[1:]:
    place(buf, tick(rng.uniform(1900, 2200), 0.001, 0.01), (t_ - T14) / 1000, 0.45)
place(buf, impact(0.4, 70, 0.1), D14 / 1000, 0.9)
d = write("digit_counter", reverb(buf, 0.3, 0.12), -34)
cues[14] = [[first, "entr", "digit_counter"]]
summary.append(f"S14 counters: 0 -> 54 million ({len(fr14)} readings, sound {d:.2f}s); 0 -> 176 km synced to the "
               f"pipeline drawing ({len(fr176)} readings, uses the existing pipeline sound)")
add_note(s, "NUMBER ANIMATION: '≈ 54 million' counts up from zero with soft digital clicks and a gentle arrival. "
            "'176 km' counts up at the same time as the new pipeline draws itself on the map, so the distance grows "
            "with the line.")

# =================================================================== SLIDE 12 — recovery counter rises with the bar
s = S[11]
A = Anim()
v2 = find(s, "s12_v2")
v2.height = E(0.4)  # clear of the bar's top face (frames are opaque)
bgfill(v2._element)
to_fade(effect(s, v2.shape_id, "entr"))  # keeps its existing soft blip; fades over the last frame
T12, D12 = 2300, 1200  # = the 3-D bar's wipe
fr12 = frames(T12, D12, 30, 0.0, 0.0, 60)
for i, (t_, v) in enumerate(fr12[:-1] + [(T12 + D12 - 40, 30)]):
    f = clone(s, v2._element, f"s12_count_{i:02d}", [f"{v}%"])
    A.fade(f, T12, 150) if i == 0 else A.appear(f, t_)
merge(s, A)
summary.append(f"S12 recovery counter 0% -> 30% rising with the bar ({len(fr12)} readings), then '> 30%'")
add_note(s, "NUMBER ANIMATION: the percentage counts up while the bar rises, then settles on '> 30%' (expected).")

prs.save(OUT)
json.dump({str(k): v for k, v in cues.items()}, open(CUES, "w"))
print("\n".join(summary))
print("saved", OUT)
