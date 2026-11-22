# Construction section, PowerPoint-native 3D (exec'd from build_brand.py, shares its globals). No video.
# Each slide is a view of one virtual camera on the exploded motor (native_layout.py). Every part is its own
# object with the same name on every slide ('!!<kind>_<object>'), so Morph moves it exactly as the camera
# would: from the overview the selected part grows to the centre while the others fly out past the edges;
# between components the scene pans, with a gentle turntable swing.
# NATIVE_MODE=3d  -> each object is a genuine PowerPoint 3D model (.glb, am3d:model3d) with a picture fallback
# NATIVE_MODE=img -> each object is a high-quality transparent picture (backup deck, same layout and Morph)
import math, itertools
from PIL import Image
from pptx.opc.package import Part
from pptx.opc.packuri import PackURI
sys.path.insert(0, HERE)
import native_layout as NL
ND = os.path.join(D2, 'native'); FD = lambda f: os.path.join(D2, 'film', f)
MODE = os.environ.get('NATIVE_MODE', '3d')
MORPH = set()
EMU = 914400
RT_MODEL3D = 'http://schemas.microsoft.com/office/2017/06/relationships/model3d'
A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'; R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
P_NS = 'http://schemas.openxmlformats.org/presentationml/2006/main'
_glb_parts = {}

def badge(s, n, x, y, d, name=None, size=None, ring=True):
    o = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x - d / 2), Inches(y - d / 2), Inches(d), Inches(d))
    o.fill.solid(); o.fill.fore_color.rgb = GREEN
    if ring: o.line.color.rgb = WHITE; o.line.width = Pt(2 if d < 0.6 else 3)
    else: o.line.fill.background()
    o.shadow.inherit = False; shadow(o, blur=8, dist=2, alpha=22)
    tf = o.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = MSO_ANCHOR.MIDDLE; tf.word_wrap = False
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; r = p.add_run(); r.text = str(n)
    r.font.size = Pt(size or (14 if d < 0.6 else 40)); r.font.bold = True; r.font.color.rgb = WHITE
    if name: o.name = name
    return o

def chip(s, x, y, t, color):
    w = 0.3 + 0.1 * len(t)
    r = rect(s, x, y, w, 0.27, fill=None, line=color, radius=0.5)
    tf = r.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = MSO_ANCHOR.MIDDLE; tf.word_wrap = False
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; rr = p.add_run(); rr.text = t
    rr.font.size = Pt(9); rr.font.bold = True; rr.font.color.rgb = color
    rPr = rr._r.get_or_add_rPr(); rPr.set('cap', 'all'); rPr.set('spc', '120')
    return r

def glb_part(kind, obj):
    key = (kind, obj)
    if key not in _glb_parts:
        blob = open(os.path.join(ND, f'{kind}_{obj}.glb'), 'rb').read()
        pn = PackURI(f'/ppt/media/model3d_{kind}_{obj}.glb')
        _glb_parts[key] = Part(pn, 'model/gltf-binary', prs.part.package, blob)
    return _glb_parts[key]

def _next_id(s):
    return max([int(e.get('id')) for e in s._element.iter(qn('p:cNvPr'))] + [1]) + 1

def add_object(s, kind, p, scene_obj, label_txt):
    """one part: a PowerPoint 3D model (with picture fallback) or, in the backup deck, a picture"""
    img = os.path.join(ND, 'img', NL.img_name(kind, p['obj'], p['yaw']))
    side = int(round(p['side'] * EMU)); x = int(round((p['x'] - p['side'] / 2) * EMU)); y = int(round((p['y'] - p['side'] / 2) * EMU))
    name = f"!!{kind}_{p['obj']}"; descr = f'{label_txt} (3D model)' if MODE == '3d' else label_txt
    if MODE != '3d':
        pic = s.shapes.add_picture(img, x, y, side, side); pic.name = name
        pic._element.nvPicPr.cNvPr.set('descr', descr); return pic
    _, rid_img = s.part.get_or_add_image_part(img)
    rid_glb = s.part.relate_to(glb_part(kind, p['obj']), RT_MODEL3D)
    sid = _next_id(s)
    fov = NL_FOV = 15.0
    r_ref = 0.7                                              # model normalised to a 0.7 m bounding sphere
    mpu = r_ref / scene_obj['r']                             # metres per model unit
    dist = int(r_ref / math.sin(math.radians(fov / 2)) * 36000000)   # camera distance in EMU (1 m = 36,000,000 EMU)
    yaw = int(round(math.degrees(p['yaw']) * 60000))
    L = lambda lx, ly, lz: f'<am3d:pos x="{int(lx * 36000000)}" y="{int(ly * 36000000)}" z="{int(lz * 36000000)}"/>'
    xml = f'''<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:p="{P_NS}" xmlns:a="{A_NS}" xmlns:r="{R_NS}">
<mc:Choice xmlns:am3d="http://schemas.microsoft.com/office/drawing/2017/model3d" Requires="am3d">
<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="{sid}" name="{name}" descr="{descr}"/><p:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></p:cNvGraphicFramePr><p:nvPr/></p:nvGraphicFramePr>
<p:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{side}" cy="{side}"/></p:xfrm>
<a:graphic><a:graphicData uri="http://schemas.microsoft.com/office/drawing/2017/model3d"><am3d:model3d r:embed="{rid_glb}">
<am3d:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{side}" cy="{side}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></am3d:spPr>
<am3d:camera><am3d:pos x="0" y="0" z="{dist}"/><am3d:up dx="0" dy="36000000" dz="0"/><am3d:lookAt x="0" y="0" z="0"/><am3d:perspective fov="{int(fov * 60000)}"/></am3d:camera>
<am3d:trans><am3d:meterPerModelUnit n="{int(round(mpu * 1000000))}" d="1000000"/><am3d:preTrans dx="0" dy="0" dz="0"/><am3d:scale><am3d:sx n="1000000" d="1000000"/><am3d:sy n="1000000" d="1000000"/><am3d:sz n="1000000" d="1000000"/></am3d:scale><am3d:rot ax="0" ay="{yaw}" az="0"/><am3d:postTrans dx="0" dy="0" dz="0"/></am3d:trans>
<am3d:raster rName="Office3DRenderer" rVer="16.0.8326"><am3d:blip r:embed="{rid_img}"/></am3d:raster>
<am3d:objViewport viewportSz="{side}"/>
<am3d:ambientLight><am3d:clr><a:scrgbClr r="50000" g="50000" b="50000"/></am3d:clr><am3d:illuminance n="500000" d="1000000"/></am3d:ambientLight>
<am3d:ptLight rad="0"><am3d:clr><a:scrgbClr r="100000" g="75000" b="50000"/></am3d:clr><am3d:intensity n="9765625" d="1000000"/>{L(0.6, 1.97, 0.45)}</am3d:ptLight>
<am3d:ptLight rad="0"><am3d:clr><a:scrgbClr r="40000" g="60000" b="95000"/></am3d:clr><am3d:intensity n="9765625" d="1000000"/>{L(-1.5, 0.3, 1.6)}</am3d:ptLight>
<am3d:ptLight rad="0"><am3d:clr><a:scrgbClr r="86000" g="74000" b="56000"/></am3d:clr><am3d:intensity n="9765625" d="1000000"/>{L(-0.4, -1.2, -2.0)}</am3d:ptLight>
</am3d:model3d></a:graphicData></a:graphic></p:graphicFrame>
</mc:Choice>
<mc:Fallback><p:pic><p:nvPicPr><p:cNvPr id="{sid}" name="{name}" descr="{descr}"/><p:cNvPicPr><a:picLocks noGrp="1" noRot="1" noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>
<p:blipFill><a:blip r:embed="{rid_img}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{side}" cy="{side}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic></mc:Fallback>
</mc:AlternateContent>'''
    el = etree.fromstring(xml)
    s.shapes._spTree.append(el)
    return el

def reveal_timing(s, items):
    """after the Morph: leader line wipes from the part to the number, then the text fades in. items: (shape, kind, delay_ms)"""
    ids = itertools.count(1)
    root, seq, outer = next(ids), next(ids), next(ids)
    def eff(kind, spid, node, dur):
        i, j, k = next(ids), next(ids), next(ids)
        vis = (f'<p:set><p:cBhvr><p:cTn id="{k}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
               f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>')
        filt, pid, sub = {'fade': ('fade', 10, 0), 'wipe': ('wipe(left)', 22, 8)}[kind]
        body = vis + f'<p:animEffect transition="in" filter="{filt}"><p:cBhvr><p:cTn id="{j}" dur="{dur}"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>'
        return (f'<p:par><p:cTn id="{i}" presetID="{pid}" presetClass="entr" presetSubtype="{sub}" fill="hold" grpId="0" nodeType="{node}">'
                f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>{body}</p:childTnLst></p:cTn></p:par>')
    groups = {}
    for shp, kind, d in items: groups.setdefault(d, []).append((shp, kind))
    pars = ''
    for d in sorted(groups):
        gid = next(ids)
        effs = ''.join(eff(kind, shp.shape_id, 'afterEffect' if n == 0 else 'withEffect', 600 if kind == 'wipe' else 450) for n, (shp, kind) in enumerate(groups[d]))
        pars += f'<p:par><p:cTn id="{gid}" fill="hold"><p:stCondLst><p:cond delay="{d}"/></p:stCondLst><p:childTnLst>{effs}</p:childTnLst></p:cTn></p:par>'
    def bld(shp):
        el = shp._element
        if el.tag != qn('p:sp'): return ''
        tb = el.find(qn('p:nvSpPr')).find(qn('p:cNvSpPr')).get('txBox') == '1'
        return f'<p:bldP spid="{shp.shape_id}" grpId="0"' + ('' if tb else ' animBg="1"') + '/>'
    b = ''.join(bld(shp) for shp, _, _ in items)
    xml = (f'<p:timing xmlns:p="{P_NS}"><p:tnLst><p:par><p:cTn id="{root}" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
           f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="{seq}" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
           f'<p:par><p:cTn id="{outer}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="{seq}"/></p:cond></p:stCondLst>'
           f'<p:childTnLst>{pars}</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
           f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
           f'</p:childTnLst></p:cTn></p:par></p:tnLst>' + (f'<p:bldLst>{b}</p:bldLst>' if b else '') + '</p:timing>')
    sld = s._element; old = sld.find(qn('p:timing'))
    if old is not None: sld.remove(old)
    el = etree.fromstring(xml); ext = sld.find(qn('p:extLst'))
    (ext.addprevious(el) if ext is not None else sld.append(el))

def minimap(kind):
    """small locator: the overview frame of the 3D model, with label anchors (from film.js stills/plan)"""
    plan = json.load(open(FD(kind + '_plan.json'))); an = plan['segments'][0]['anchors']
    im = Image.open(FD(f'{kind}_end0.png')).convert('RGB'); W, H = im.size
    from PIL import ImageChops
    x0, y0, x1, y1 = ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).point(lambda v: 255 if v > 10 else 0).convert('L').getbbox()
    pad = int(0.02 * W); x0, y0, x1, y1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
    out = os.path.join(ND, f'{kind}_map.jpg'); im.crop((x0, y0, x1, y1)).resize(((x1 - x0) // 2, (y1 - y0) // 2), Image.LANCZOS).save(out, quality=90)
    return out, (x1 - x0) / (y1 - y0), {int(k): ((u * W - x0) / (x1 - x0), (v * H - y0) / (y1 - y0)) for k, (u, v) in an.items()}

def component_section(kind, motor, items, offsets, ov_note, key):
    slides = NL.layout(ND, kind); scene = json.load(open(os.path.join(ND, f'{kind}_scene.json')))['objects']
    cfg = NL.Scene(ND, kind).cfg
    N = len(items); head = f'{motor}: the main components'
    sub = f'{N} parts, one at a time – each keeps its number on the slides that follow'
    names = {}
    for n, comp in enumerate(cfg['components'], 1):
        for o in comp['show']: names.setdefault(o, items[n - 1]['name'])
    EXTRA = dict(bearingNDE='Bearing (non-drive end)', endShieldDE='End shield (drive end)', endShieldNDE='End shield (non-drive end)', fanCover='Fan cover', shaftFan='Shaft fan', cooling='Cooling system', rotorAsm='Rotor', statorAsm='Stator')
    label_of = lambda o: names.get(o) or EXTRA.get(o, o)
    # ---------- overview: the exploded motor, every part a separate 3D object ----------
    s = new('Title & Subtitle Only', key=key + 'o'); title(s, head, sub)
    SL = slides[0]
    for p in SL['objects']: add_object(s, kind, p, scene[p['obj']], label_of(p['obj']))
    anc = {n: SL['anchors'][n] for n in range(1, N + 1)}
    pos = {n: [anc[n][0] + offsets.get(n, (0, -0.45))[0], anc[n][1] + offsets.get(n, (0, -0.45))[1]] for n in anc}
    for _ in range(400):
        for a in pos:
            for b in pos:
                if a >= b: continue
                dx, dy = pos[b][0] - pos[a][0], pos[b][1] - pos[a][1]; d = (dx * dx + dy * dy) ** 0.5 or 1e-3
                if d < 0.58: f = (0.58 - d) / 2 / d; pos[a][0] -= dx * f; pos[a][1] -= dy * f; pos[b][0] += dx * f; pos[b][1] += dy * f
            for c in anc:
                dx, dy = pos[a][0] - anc[c][0], pos[a][1] - anc[c][1]; d = (dx * dx + dy * dy) ** 0.5 or 1e-3
                if d < 0.34: f = (0.34 - d) / d; pos[a][0] += dx * f; pos[a][1] += dy * f
            pos[a][1] += (anc[a][1] - 0.45 - pos[a][1]) * 0.02
            pos[a][0] = min(max(pos[a][0], 0.6), 8.8); pos[a][1] = min(max(pos[a][1], 1.55), 7.0)
    reveal = []
    for n in range(1, N + 1):
        (ax, ay), (bx, by) = anc[n], pos[n]
        ln = s.shapes.add_connector(1, Inches(ax), Inches(ay), Inches(bx), Inches(by)); ln.line.color.rgb = GREEN; ln.line.width = Pt(1.25)
        dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(ax - 0.045), Inches(ay - 0.045), Inches(0.09), Inches(0.09))
        dot.fill.solid(); dot.fill.fore_color.rgb = GREEN; dot.line.color.rgb = WHITE; dot.line.width = Pt(1); dot.shadow.inherit = False
        bd = badge(s, n, bx, by, 0.44, name=f'!!n{n}')
        reveal += [(dot, 'fade', 60 * n), (ln, 'fade', 60 * n), (bd, 'fade', 60 * n)]
    lx = 9.45; lab = label(s, lx, 1.5, 3.3, 'Main components'); reveal.append((lab, 'fade', 0))
    step = min(0.56, 5.0 / N); y0 = 1.95
    for n, it in enumerate(items, 1):
        y = y0 + (n - 1) * step
        b2 = badge(s, n, lx + 0.17, y + 0.17, 0.34, size=11, ring=False)
        t2 = text(s, lx + 0.5, y + 0.02, 3.0, 0.32, it['name'], size=14.5 if N <= 7 else 13.5, bold=True, color=DARK, anchor=MSO_ANCHOR.MIDDLE)
        reveal += [(b2, 'fade', 60 * n), (t2, 'fade', 60 * n)]
    if MODE == '3d':
        t3 = text(s, lx, y0 + N * step + 0.12, 3.4, 0.5, 'Every part is a real 3D model – select one and drag to turn it.', size=10.5, color=GREY, italic=True); reveal.append((t3, 'fade', 60 * N))
    reveal_timing(s, reveal)
    # ---------- one slide per component: the camera moves in on the part ----------
    mm_img, mm_ar, mm_an = minimap(kind)
    MH = 1.75; MW = MH * mm_ar
    if MW > 3.4: MW = 3.4; MH = MW / mm_ar
    for n, it in enumerate(items, 1):
        s = new('Title & Subtitle Only', key=f'{key}{n}'); title(s, head, sub)
        MORPH.add(s.slide_id)
        SL = slides[n]
        for p in SL['objects']: add_object(s, kind, p, scene[p['obj']], label_of(p['obj']))
        if it.get('note'): text(s, 0.6, 6.85, 6, 0.25, it['note'], size=10, color=GREY, italic=True)
        badge(s, n, 9.55, 2.0, 1.1, name=f'!!n{n}')
        label(s, 10.3, 1.62, 2.6, f'Component {n} of {N}', color=GREY)
        if it.get('chip'): chip(s, 10.3, 2.0, it['chip'], COPPER if it['chip'] == 'Rotating' else GREEN)
        body = text(s, 9.0, 2.8, 3.95, 2.25, [[(it['name'], {'size': 28, 'bold': True, 'color': DARK})], [(it['desc'], {'size': 15.5})]], spacing=8, line=1.05)
        ax, ay = SL['anchors'][n]
        ln = s.shapes.add_connector(1, Inches(ax), Inches(ay), Inches(8.95), Inches(2.0)); ln.line.color.rgb = GREEN; ln.line.width = Pt(1.5)
        dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(ax - 0.06), Inches(ay - 0.06), Inches(0.12), Inches(0.12))
        dot.fill.solid(); dot.fill.fore_color.rgb = GREEN; dot.line.color.rgb = WHITE; dot.line.width = Pt(1.25); dot.shadow.inherit = False
        MX, MY = 9.0, 7.2 - MH
        label(s, 9.0, MY - 0.3, 3.5, 'Where it sits', color=GREY, size=9.5)
        mm = s.shapes.add_picture(mm_img, Inches(MX), Inches(MY), Inches(MW), Inches(MH)); mm.name = '!!map'
        mu, mv = mm_an[n]; rd = 0.34
        ring = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(MX + mu * MW - rd / 2), Inches(MY + mv * MH - rd / 2), Inches(rd), Inches(rd))
        ring.fill.background(); ring.line.color.rgb = GREEN; ring.line.width = Pt(2.5); ring.shadow.inherit = False; ring.name = '!!ring'
        reveal_timing(s, [(dot, 'fade', 0), (ln, 'wipe', 0), (body, 'fade', 350)])

IND_ITEMS = [
    dict(name='Stator', chip='Stationary', desc='The fixed outer part. Copper coils in a stack of thin steel sheets create the rotating magnetic field.'),
    dict(name='Rotor', chip='Rotating', desc='The turning part inside the stator. The magnetic field pushes it round, and it turns the shaft.'),
    dict(name='Rotor bars and end rings', chip='Rotating', desc='Bars joined by a ring at each end form a closed “squirrel cage”. Current is induced in it – no wires needed.', note='Steel core removed to show the cage'),
    dict(name='Shaft', chip='Rotating', desc='A strong steel bar through the rotor. It carries the turning force out to the pump, fan or compressor.'),
    dict(name='Bearings', desc='One at each end. Steel balls roll between two rings, so the shaft spins smoothly with little friction.'),
    dict(name='Frame / housing', chip='Stationary', desc='The cast-iron body and end covers. It holds and protects everything; its fins carry heat away.'),
    dict(name='Cooling fan', chip='Rotating', desc='Fixed to the back of the shaft. It blows air along the fins to keep the motor cool.'),
]
SYN_ITEMS = [
    dict(name='Stator', chip='Stationary', desc='Built just like the induction motor’s stator. Its three-phase coils create the rotating magnetic field.'),
    dict(name='Salient-pole rotor', chip='Rotating', desc='Its poles stick out like spokes. With DC current, each pole becomes a fixed North or South magnet.'),
    dict(name='Field winding', chip='Rotating', desc='Copper coils wound round each pole. DC current through them turns the poles into electromagnets.', note='Pole steel removed to show the coils'),
    dict(name='Damper (starting) bars', chip='Rotating', desc='Copper bars in the pole faces form a small cage. They start the motor and calm any swinging.', note='Pole steel removed to show the bars'),
    dict(name='Slip rings and brushes', desc='Rings on the shaft with carbon brushes pressing on them. They carry the DC into the spinning rotor.'),
    dict(name='DC excitation system', chip='Stationary', desc='This cabinet turns AC into controlled DC for the field winding. It sets how strong the rotor magnets are.'),
    dict(name='Shaft', chip='Rotating', desc='A forged steel shaft. It carries the heavy rotor and delivers the turning force to the machine.'),
    dict(name='Bearings', desc='Oil-lubricated sleeve bearings. A thin film of oil carries the heavy rotor, so the metal never touches.'),
    dict(name='Frame / housing', chip='Stationary', desc='A welded steel box. It holds the stator, bearings and cooler, and is bolted to the foundation.'),
    dict(name='Cooling system', desc='A shaft fan pushes warm air from inside through the cooler on top, where outside air carries the heat away.'),
]
