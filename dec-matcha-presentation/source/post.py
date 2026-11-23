"""Inject Morph transitions, choreographed animations and 3-D effects into the pptxgenjs deck."""
import json, os, re, shutil, sys, zipfile, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sounds
from lxml import etree

SRC, DST, SPEC = sys.argv[1], sys.argv[2], sys.argv[3]
spec = json.load(open(SPEC))
NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
A = "{%s}" % NS["a"]

work = DST + ".dir"
shutil.rmtree(work, ignore_errors=True)
zipfile.ZipFile(SRC).extractall(work)


class T:
    """Timing XML builder."""

    def __init__(self, shapes, snd=None):
        self.snd = snd
        self.id = 3
        self.shapes = shapes      # name -> (spid, kind)
        self.grp = {}             # spid -> next grpId
        self.bld = []             # (spid, grpId)
        self.items = []           # (delay, xml)

    def nid(self):
        self.id += 1
        return self.id

    def tgt(self, s):
        return f'<p:tgtEl><p:spTgt spid="{s}"/></p:tgtEl>'

    def setvis(self, s, val="visible"):
        return (f'<p:set><p:cBhvr><p:cTn id="{self.nid()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
                f'{self.tgt(s)}<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
                f'<p:to><p:strVal val="{val}"/></p:to></p:set>')

    def filt(self, s, f, d, tr="in"):
        return f'<p:animEffect transition="{tr}" filter="{f}"><p:cBhvr><p:cTn id="{self.nid()}" dur="{d}"/>{self.tgt(s)}</p:cBhvr></p:animEffect>'

    def anim(self, s, attr, frm, to, d, decel=True):
        dc = ' decel="100000"' if decel else ""
        return (f'<p:anim calcmode="lin" valueType="num"><p:cBhvr additive="base"><p:cTn id="{self.nid()}" dur="{d}" fill="hold"{dc}/>'
                f'{self.tgt(s)}<p:attrNameLst><p:attrName>{attr}</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst>'
                f'<p:tav tm="0"><p:val><p:strVal val="{frm}"/></p:val></p:tav>'
                f'<p:tav tm="100000"><p:val><p:strVal val="{to}"/></p:val></p:tav></p:tavLst></p:anim>')

    def rot(self, s, by, d, decel=False):
        dc = ' decel="100000"' if decel else ""
        return (f'<p:animRot by="{int(by)}"><p:cBhvr><p:cTn id="{self.nid()}" dur="{d}" fill="hold"{dc}/>{self.tgt(s)}'
                f'<p:attrNameLst><p:attrName>r</p:attrName></p:attrNameLst></p:cBhvr></p:animRot>')

    def motion(self, s, dy, d):
        return (f'<p:animMotion origin="layout" path="M 0 0 L 0 {dy} E" pathEditMode="relative" ptsTypes="">'
                f'<p:cBhvr><p:cTn id="{self.nid()}" dur="{d}" fill="hold"/>{self.tgt(s)}'
                f'<p:attrNameLst><p:attrName>ppt_x</p:attrName><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr></p:animMotion>')

    def audio(self, sound):
        if not sound:
            return ""
        rid, fname = self.snd(sound)
        vol = int(sound.get("vol", 1.0) * 100000)
        return (f'<p:subTnLst><p:audio><p:cMediaNode vol="{vol}" showWhenStopped="0"><p:cTn id="{self.nid()}" display="0" masterRel="sameClick">'
                '<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:endCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:endCondLst></p:cTn>'
                f'<p:tgtEl><p:sndTgt r:embed="{rid}" name="{fname}"/></p:tgtEl></p:cMediaNode></p:audio></p:subTnLst>')

    def effect(self, name, at, cls, pid, sub, body_fn, extra="", iterate="", sound=None):
        if name not in self.shapes:
            raise SystemExit(f"unknown shape name {name!r}")
        s, kind = self.shapes[name]
        g = self.grp.get(s, 0)
        self.grp[s] = g + 1
        if kind == "sp":
            self.bld.append((s, g))
        eid = self.nid()
        body = body_fn(s)
        xml = (f'<p:par><p:cTn id="{eid}" presetID="{pid}" presetClass="{cls}" presetSubtype="{sub}"{extra} fill="hold" '
               f'grpId="{g}" nodeType="withEffect"><p:stCondLst><p:cond delay="{int(at)}"/></p:stCondLst>{iterate}'
               f'<p:childTnLst>{body}</p:childTnLst>{self.audio(sound)}</p:cTn></p:par>')
        self.items.append((at, xml))

    # ---------------------------------------------------------------- effect vocabulary
    def add(self, e):
        t, at = e["type"], e.get("at", 0)
        d = e.get("dur", 600)
        WIPE = {"top": ("down", 1), "bottom": ("up", 4), "left": ("right", 8), "right": ("left", 2)}
        if t == "counter":
            fr, step = e["frames"], e["step"]
            for i, n in enumerate(fr):
                snd = dict(e["sound"], kind="roll", step=step, n=len(fr)) if (i == 0 and e.get("sound")) else None
                self.effect(n, at + i * step, "entr", 1, 0, lambda s: self.setvis(s), sound=snd)
                self.effect(n, at + (i + 1) * step, "exit", 1, 0, lambda s: self.setvis(s, "hidden"))
            self.effect(e["final"], at + len(fr) * step, "entr", 1, 0, lambda s: self.setvis(s))
            return
        if t == "assemble":                       # digits fly in from the camera and lock into place
            dg, step = e["digits"], e["step"]
            end = at + (len(dg) - 1) * step + d + 60
            land = [i * step + d for i in range(len(dg))]
            for i, n in enumerate(dg):
                snd = dict(e["sound"], kind="assemble", times=land, final=end - at) if (i == 0 and e.get("sound")) else None
                self.effect(n, at + i * step, "entr", 53, 16, lambda s: self.setvis(s) + self.filt(s, "fade", int(d * 0.6))
                            + self.anim(s, "ppt_w", "#ppt_w*2.6", "#ppt_w", d) + self.anim(s, "ppt_h", "#ppt_h*2.6", "#ppt_h", d)
                            + self.anim(s, "ppt_y", "#ppt_y-0.05", "#ppt_y", d), sound=snd)
                self.effect(n, end, "exit", 1, 0, lambda s: self.setvis(s, "hidden"))
            self.effect(e["final"], end, "entr", 1, 0, lambda s: self.setvis(s))
            return
        orig_effect = self.effect
        first = [True]

        def effect_with_sound(*a, **k):
            if first[0] and e.get("sound"):
                k["sound"] = e["sound"]
            first[0] = False
            return orig_effect(*a, **k)
        self.effect = effect_with_sound
        try:
            self._names(e, t, at, d, WIPE)
        finally:
            self.effect = orig_effect

    def _names(self, e, t, at, d, WIPE):
        for n in e["names"]:
            if t == "fade":
                self.effect(n, at, "entr", 10, 0, lambda s: self.setvis(s) + self.filt(s, "fade", d))
            elif t in ("rise", "drop"):
                off = "+0.05" if t == "rise" else "-0.06"
                self.effect(n, at, "entr", 42, 0, lambda s: self.setvis(s) + self.filt(s, "fade", d)
                            + self.anim(s, "ppt_y", f"#ppt_y{off}", "#ppt_y", d))
            elif t in ("zoom", "pop"):
                k = e.get("from", 0.0 if t == "pop" else 0.7)
                nf = e.get("noFade")
                self.effect(n, at, "entr", 53, 16, lambda s: self.setvis(s) + ("" if nf else self.filt(s, "fade", d))
                            + self.anim(s, "ppt_w", f"#ppt_w*{k}", "#ppt_w", d) + self.anim(s, "ppt_h", f"#ppt_h*{k}", "#ppt_h", d))
            elif t == "emerge":
                fx, fy = e["fx"], e["fy"]
                self.effect(n, at, "entr", 53, 16, lambda s: self.setvis(s) + self.filt(s, "fade", int(d * 0.7))
                            + self.anim(s, "ppt_x", f"{fx}", "#ppt_x", d) + self.anim(s, "ppt_y", f"{fy}", "#ppt_y", d)
                            + self.anim(s, "ppt_w", "#ppt_w*0.2", "#ppt_w", d) + self.anim(s, "ppt_h", "#ppt_h*0.2", "#ppt_h", d))
            elif t == "emergeX":
                dx = e["dx"]
                sgn = "+" if dx >= 0 else "-"
                self.effect(n, at, "entr", 2, 2 if dx >= 0 else 8, lambda s: self.setvis(s) + self.filt(s, "fade", d)
                            + self.anim(s, "ppt_x", f"#ppt_x{sgn}{abs(dx)}", "#ppt_x", d))
            elif t == "converge":               # particles gather inward from a larger cloud
                k = e.get("from", 2.2)
                self.effect(n, at, "entr", 53, 16, lambda s: self.setvis(s) + self.filt(s, "fade", int(d * 0.4))
                            + self.anim(s, "ppt_w", f"#ppt_w*{k}", "#ppt_w", d) + self.anim(s, "ppt_h", f"#ppt_h*{k}", "#ppt_h", d))
            elif t == "fadeOut":
                self.effect(n, at, "exit", 10, 0, lambda s: self.filt(s, "fade", d, "out")
                            + (f'<p:set><p:cBhvr><p:cTn id="{self.nid()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="{d - 1}"/></p:stCondLst></p:cTn>'
                               f'{self.tgt(s)}<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="hidden"/></p:to></p:set>'))
            elif t == "push":                   # slow camera push-in (emphasis grow)
                k = int(e.get("scale", 1.08) * 100000)
                self.effect(n, at, "emph", 6, 0, lambda s: f'<p:animScale><p:cBhvr><p:cTn id="{self.nid()}" dur="{d}" fill="hold" decel="60000"/>{self.tgt(s)}</p:cBhvr><p:by x="{k}" y="{k}"/></p:animScale>')
            elif t == "flip":
                self.effect(n, at, "entr", 53, 16, lambda s: self.setvis(s) + self.filt(s, "fade", int(d * 0.5))
                            + self.anim(s, "ppt_w", "#ppt_w*0.02", "#ppt_w", d) + self.anim(s, "ppt_y", "#ppt_y+0.03", "#ppt_y", d))
            elif t == "wipe":
                f, sub = WIPE[e["dir"]]
                self.effect(n, at, "entr", 22, sub, lambda s: self.setvis(s) + self.filt(s, f"wipe({f})", d))
            elif t == "barn":
                self.effect(n, at, "entr", 16, 42, lambda s: self.setvis(s) + self.filt(s, "barn(outVertical)", d))
            elif t == "wheel":
                self.effect(n, at, "entr", 21, 1, lambda s: self.setvis(s) + self.filt(s, "wheel(1)", d))
            elif t == "letters":
                it = f'<p:iterate type="lt"><p:tmAbs val="{e.get("step", 60)}"/></p:iterate>'
                self.effect(n, at, "entr", 42, 0, lambda s: self.setvis(s) + self.filt(s, "fade", d)
                            + self.anim(s, "ppt_y", "#ppt_y+0.04", "#ppt_y", d), iterate=it)
            elif t == "spin":
                by = -21600000 if e.get("rev") else 21600000
                self.effect(n, at, "emph", 8, 0, lambda s: self.rot(s, by, d), extra=' repeatCount="indefinite"')
            elif t == "rotby":
                self.effect(n, at, "emph", 8, 0, lambda s: self.rot(s, e["by"] * 60000, max(d, 1), e.get("decel", False)))
            elif t == "float":
                self.effect(n, at, "path", 0, 0, lambda s: self.motion(s, e.get("dy", -0.01), d),
                            extra=' repeatCount="indefinite" accel="50000" decel="50000" autoRev="1"')
            else:
                raise SystemExit("unknown effect " + t)

    def xml(self):
        self.items.sort(key=lambda x: x[0])
        inner = "".join(x for _, x in self.items)
        bld = "".join(f'<p:bldP spid="{s}" grpId="{g}" animBg="1"/>' for s, g in self.bld)
        return ('<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
                '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
                '<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
                f'<p:par><p:cTn id="{self.nid()}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>{inner}</p:childTnLst></p:cTn></p:par>'
                '</p:childTnLst></p:cTn></p:par>'
                '</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
                '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
                f'</p:childTnLst></p:cTn></p:par></p:tnLst><p:bldLst>{bld}</p:bldLst></p:timing>')


MORPH = ('<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
         '<mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159">'
         '<p:transition xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" spd="slow" p14:dur="1600"><p159:morph option="byObject"/></p:transition>'
         '</mc:Choice><mc:Fallback><p:transition spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>')
FADE = '<p:transition spd="slow"><p:fade thruBlk="1"/></p:transition>'


def alt(req, ns, body, dur):
    return ('<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
            f'<mc:Choice xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" {ns} Requires="{req}">'
            f'<p:transition spd="slow" p14:dur="{dur}">{body}</p:transition>'
            '</mc:Choice><mc:Fallback><p:transition spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>')


TRANS = {
    "fade": FADE,
    "morph": MORPH,
    "ripple": alt("p14", "", '<p14:ripple dir="center"/>', 1600),
    "vortex": alt("p14", "", '<p14:vortex dir="r"/>', 2600),
    "wind": alt("p15", 'xmlns:p15="http://schemas.microsoft.com/office/powerpoint/2012/main"', '<p15:prstTrans prst="wind"/>', 2000),
}

BEVEL = ('<a:scene3d><a:camera prst="orthographicFront"/><a:lightRig rig="threePt" dir="t"/></a:scene3d>'
         '<a:sp3d><a:bevelT w="57150" h="25400" prst="circle"/></a:sp3d>')
TEXT3D = ('<a:scene3d><a:camera prst="orthographicFront"/><a:lightRig rig="balanced" dir="t"/></a:scene3d>'
          '<a:sp3d extrusionH="19050" prstMaterial="warmMatte"><a:bevelT w="12700" h="12700"/>'
          '<a:extrusionClr><a:srgbClr val="1C3016"/></a:extrusionClr></a:sp3d>')


def tilt(deg):
    lat = int((360 - deg) * 60000)
    return (f'<a:scene3d><a:camera prst="perspectiveFront" fov="3000000"><a:rot lat="{lat}" lon="0" rev="0"/></a:camera>'
            '<a:lightRig rig="threePt" dir="t"/></a:scene3d>')


def frag(x):
    return etree.fromstring(f'<r xmlns:a="{NS["a"]}">{x}</r>')


for sl in spec["slides"]:
    p = os.path.join(work, "ppt", "slides", f"slide{sl['n']}.xml")
    tree = etree.parse(p)
    root = tree.getroot()
    shapes = {}
    for el in root.iter("{%s}sp" % NS["p"], "{%s}pic" % NS["p"], "{%s}cxnSp" % NS["p"]):
        c = el.find(".//p:cNvPr", NS)
        kind = etree.QName(el).localname
        if c.get("name") in shapes:
            raise SystemExit(f"duplicate name {c.get('name')} on slide {sl['n']}")
        shapes[c.get("name")] = (c.get("id"), kind, el)

    # 3-D: bevelled medallions, dimensional hero numerals, perspective-tilted bowl
    for name, (sid, kind, el) in shapes.items():
        if name.startswith("medal ") or name.startswith("Node ") and not name.startswith("Node num"):
            sp = el.find("p:spPr", NS)
            for ch in frag(BEVEL):
                sp.append(ch)
    for base in sl.get("text3d", []):
        for name, (sid, kind, el) in shapes.items():
            if name == base or name.startswith(base + " counter frame"):
                bp = el.find(".//a:bodyPr", NS)
                for ch in frag(TEXT3D):
                    bp.append(ch)
    for name, deg in sl.get("tilt", {}).items():
        sp = shapes[name][2].find("p:spPr", NS)
        for ch in frag(tilt(deg)):
            sp.append(ch)

    relp = os.path.join(work, "ppt", "slides", "_rels", f"slide{sl['n']}.xml.rels")
    rels = open(relp, encoding="utf-8").read()
    added = {}

    def snd(sd):
        key = json.dumps({k: v for k, v in sd.items() if k != "vol"}, sort_keys=True)
        if key in added:
            return added[key]
        fname = "snd_" + sd["kind"] + "_" + hashlib.sha1(key.encode()).hexdigest()[:8] + ".wav"
        sounds.make(sd["kind"], sd, os.path.join(work, "ppt", "media", fname))
        rid = f"rIdSnd{len(added) + 1}"
        added[key] = (rid, fname)
        return added[key]

    t = T({k: (v[0], v[1]) for k, v in shapes.items()}, snd)
    for e in sl["effects"]:
        t.add(e)
    xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True).decode()
    trans = TRANS[sl["transition"]]
    if sl.get("tsound"):
        rid, fname = snd(sl["tsound"])
        sa = f'<p:sndAc><p:stSnd><p:snd r:embed="{rid}" name="{fname}"/></p:stSnd></p:sndAc>'
        trans = trans.replace("</p:transition>", sa + "</p:transition>")
    if added:
        extra = "".join(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/audio" Target="../media/{fn}"/>' for rid, fn in added.values())
        open(relp, "w", encoding="utf-8").write(rels.replace("</Relationships>", extra + "</Relationships>"))
    assert "<p:timing" not in xml and "<p:transition" not in xml
    xml = xml.replace("</p:clrMapOvr>", "</p:clrMapOvr>" + trans + t.xml(), 1)
    assert trans in xml
    open(p, "w", encoding="utf-8").write(xml)

ctp = os.path.join(work, "[Content_Types].xml")
ct = open(ctp, encoding="utf-8").read()
if 'Extension="wav"' not in ct:
    ct = ct.replace("<Default ", '<Default Extension="wav" ContentType="audio/wav"/><Default ', 1)
    open(ctp, "w", encoding="utf-8").write(ct)

# dedupe identical media (pptxgenjs embeds one copy per use)
import hashlib, glob
media = sorted(glob.glob(os.path.join(work, "ppt", "media", "*")))
seen, remap = {}, {}
for m in media:
    h = hashlib.sha1(open(m, "rb").read()).hexdigest()
    if h in seen:
        remap[os.path.basename(m)] = os.path.basename(seen[h]); os.remove(m)
    else:
        seen[h] = m
for rel in glob.glob(os.path.join(work, "ppt", "**", "_rels", "*.rels"), recursive=True):
    txt = open(rel, encoding="utf-8").read()
    new = re.sub(r'(Target="\.\./media/)([^"]+)"', lambda mm: mm.group(1) + remap.get(mm.group(2), mm.group(2)) + '"', txt)
    if new != txt:
        open(rel, "w", encoding="utf-8").write(new)
print("deduped", len(remap), "media files")

# pack
if os.path.exists(DST):
    os.remove(DST)
with zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as z:
    names = []
    for dp, _, fs in os.walk(work):
        for f in fs:
            full = os.path.join(dp, f)
            names.append(os.path.relpath(full, work))
    names.sort(key=lambda n: (n != "[Content_Types].xml", n))
    for n in names:
        z.write(os.path.join(work, n), n)
shutil.rmtree(work)
print("wrote", DST)
