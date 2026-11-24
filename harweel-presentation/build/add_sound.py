"""Add native PowerPoint effect sounds to a COPY of the Harweel deck.

Nothing visual is touched: each sound is attached to an animation effect that
already exists (PowerPoint's "Effect Options > Sound"), so it fires exactly when
that animation starts. One transition sound is added to the Morph zoom (slide 11).
Usage: python3 add_sound.py <original.pptx> <sfx_dir> <out.pptx> [cues.json]
"""
import os
import re
import shutil
import sys
import tempfile
import wave
import zipfile

from lxml import etree

SRC, SFX, OUT = sys.argv[1:4]
NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006"}
P = "{%s}" % NS["p"]
R_AUDIO = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/audio"

# slide: [(shape name, animation class, sound)]  — sparse by design
CUES = {
    1: [("cov_top", "entr", "rumble_build"), ("cov_well", "entr", "drill_descend")],
    2: [("!!pin", "entr", "sonar_ping")],
    3: [("!!blk_top", "entr", "rumble_build")],
    4: [("!!bignum", "entr", "deep_time_swell"), ("s4_bar", "entr", "time_sweep")],
    5: [("!!tile0_l", "entr", "stone_settle"), ("!!bignum", "entr", "data_blip")],
    6: [("s6a_lens", "entr", "lens_focus"), ("s6a_o0", "entr", "oil_trickle")],
    7: [("s7_needle", "emph", "gauge_ticks")],
    8: [("s8_S", "entr", "gas_hiss")],
    9: [("s9_dim9", "entr", "power_down")],
    10: [("s10_fp_0", "entr", "gas_pipe_flow"), ("s10_front", "entr", "reservoir_sweep"),
         ("s10_fo_0", "entr", "oil_rise")],
    11: [("s11_gas0", "entr", "dissolve_fizz"), ("s11_o0", "entr", "oil_trickle")],
    12: [("s12_v2", "entr", "data_blip_up")],
    13: [("s13_sep1_b", "entr", "plant_startup"), ("s13_out0", "entr", "gas_pipe_flow")],
    14: [("!!bignum", "entr", "data_blip"), ("s14_new", "entr", "pipeline_sweep")],
    15: [("s15_i4", "entr", "spark_shimmer")],
}
TRANSITION_SOUNDS = {11: "zoom_in_whoosh"}
if len(sys.argv) > 4:  # optional JSON cue list (used by later stages); no transition sounds then
    import json
    CUES = {int(k): [tuple(c) for c in v] for k, v in json.load(open(sys.argv[4])).items()}
    TRANSITION_SOUNDS = {}


def wav_len(name):
    with wave.open(os.path.join(SFX, name + ".wav")) as w:
        return w.getnframes() / w.getframerate()


tmp = tempfile.mkdtemp()
with zipfile.ZipFile(SRC) as z:
    z.extractall(tmp)
    order = z.namelist()

used = sorted({s for c in CUES.values() for _, _, s in c} | set(TRANSITION_SOUNDS.values()))
for s in used:
    shutil.copy(os.path.join(SFX, s + ".wav"), os.path.join(tmp, "ppt/media", f"sfx_{s}.wav"))

ct_path = os.path.join(tmp, "[Content_Types].xml")
ct = open(ct_path, encoding="utf-8").read()
if 'Extension="wav"' not in ct:
    ct = ct.replace("<Default ", '<Default Extension="wav" ContentType="audio/wav"/><Default ', 1)
    open(ct_path, "w", encoding="utf-8").write(ct)

report = []
problems = []
for n in range(1, 17):
    cues = CUES.get(n, [])
    tsnd = TRANSITION_SOUNDS.get(n)
    if not cues and not tsnd:
        continue
    sp = os.path.join(tmp, f"ppt/slides/slide{n}.xml")
    rp = os.path.join(tmp, f"ppt/slides/_rels/slide{n}.xml.rels")
    tree = etree.parse(sp)
    root = tree.getroot()
    rels = etree.parse(rp)
    rroot = rels.getroot()
    existing = [int(m) for m in re.findall(r'Id="rId(\d+)"', etree.tostring(rroot).decode())]
    next_rid = [max(existing + [0]) + 1]
    rid_for = {}

    def rel(sound):
        if sound not in rid_for:
            rid = f"rId{next_rid[0]}"
            next_rid[0] += 1
            el = etree.SubElement(rroot, "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship")
            el.set("Id", rid), el.set("Type", R_AUDIO), el.set("Target", f"../media/sfx_{sound}.wav")
            rid_for[sound] = rid
        return rid_for[sound]

    ids = {e.get("name"): e.get("id") for e in root.iter(P + "cNvPr")}
    max_ctn = max(int(c.get("id")) for c in root.iter(P + "cTn") if c.get("id"))
    timeline = []
    for shape, cls, sound in cues:
        sid = ids[shape]
        hit = None
        for ctn in root.iter(P + "cTn"):
            if ctn.get("presetClass") != cls:
                continue
            if ctn.find(f"{P}childTnLst//{P}spTgt[@spid='{sid}']") is not None:
                hit = ctn
                break
        assert hit is not None, (n, shape, cls)
        assert hit.find(P + "subTnLst") is None, (n, shape, "already has a sound")
        start = int(hit.find(f"{P}stCondLst/{P}cond").get("delay"))
        max_ctn += 1
        sub = etree.fromstring(
            f'<p:subTnLst xmlns:p="{NS["p"]}" xmlns:r="{NS["r"]}"><p:audio><p:cMediaNode>'
            f'<p:cTn id="{max_ctn}" display="0" masterRel="sameClick"><p:stCondLst>'
            f'<p:cond evt="begin" delay="0"><p:tn val="{hit.get("id")}"/></p:cond></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:sndTgt r:embed="{rel(sound)}" name="{sound}.wav"/></p:tgtEl>'
            f'</p:cMediaNode></p:audio></p:subTnLst>')
        hit.find(P + "childTnLst").addnext(sub)
        timeline.append((start, start + int(wav_len(sound) * 1000), sound, shape))
    if tsnd:
        trs = root.findall(f".//{P}transition")
        assert trs, n
        for tr in trs:  # both the Morph <mc:Choice> and the fade <mc:Fallback>
            snd = etree.fromstring(
                f'<p:sndAc xmlns:p="{NS["p"]}" xmlns:r="{NS["r"]}"><p:stSnd>'
                f'<p:snd r:embed="{rel(tsnd)}" name="{tsnd}.wav"/></p:stSnd></p:sndAc>')
            tr.append(snd)
        report.append(f"slide {n:2d}  transition      {tsnd} ({wav_len(tsnd):.2f}s, during the Morph)")
    timeline.sort()
    for i, (a, b, s, sh) in enumerate(timeline):
        report.append(f"slide {n:2d}  {a / 1000:5.2f}-{b / 1000:5.2f}s  {s:16s} on '{sh}'")
        if i + 1 < len(timeline) and timeline[i + 1][0] < b:
            problems.append(f"slide {n}: {s} overlaps {timeline[i + 1][2]}")
    tree.write(sp, xml_declaration=True, encoding="UTF-8", standalone=True)
    rels.write(rp, xml_declaration=True, encoding="UTF-8", standalone=True)

if os.path.exists(OUT):
    os.remove(OUT)
names = order + [f"ppt/media/sfx_{s}.wav" for s in used]
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for nm in names:
        z.write(os.path.join(tmp, nm), nm)
shutil.rmtree(tmp)
print("\n".join(report))
print("OVERLAPS:", problems or "none")
print("saved", OUT, round(os.path.getsize(OUT) / 1e6, 2), "MB")
