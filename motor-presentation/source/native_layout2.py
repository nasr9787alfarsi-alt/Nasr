"""Single-camera layout engine for the Construction section (v3, no video, no 3D-model objects).

Every Construction slide is a view of one virtual camera on the motor. Each part is a separate transparent
render with the same name on every slide, so PowerPoint Morph moves it exactly as a camera move would.
States per motor:
  hero1    complete assembled motor (single render), turned -16 deg        -> Morph: slow turn
  hero2    complete motor, overview angle; parts hidden underneath          -> Morph: covers lift off
  stage1   frame, end covers and cooler lifted away; inside still assembled -> Morph: rotor and the rest slide out
  overview fully exploded, numbered
  comp n   camera on component n: target enlarged and centred, others parked just off-slide
Positions in inches on a 13.333 x 7.5 slide; world in metres.
"""
import json, math, os

SLIDE_W, SLIDE_H = 13.333, 7.5
OV_AREA = (0.45, 1.4, 8.95, 7.15)
HERO_AREA = (0.6, 1.35, 12.7, 7.2)
CP_AREA = (0.55, 1.45, 8.65, 7.1)
YAW_DEG = 9.0
HERO_YAW1 = -16.0
STAGE1 = {'induction': ['frame', 'endShieldDE', 'endShieldNDE', 'fanCover'],
          'sync': ['frame', 'cooling', 'endShieldDE', 'endShieldNDE']}

def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def add(a, b): return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]

class Scene:
    def __init__(self, nd, kind, cfg_override=None):
        cfg = json.load(open(os.path.join(nd, 'cfg.json')))
        self.cfg = cfg_override or cfg['CFG'][kind]; self.B = cfg['basis']
        self.sc = json.load(open(os.path.join(nd, f'{kind}_scene.json'))); self.kind = kind
        objs = self.sc['objects']
        lo = [min(objs[o]['center'][i] - objs[o]['size'][i] / 2 for o in self.cfg['overview']) for i in range(3)]
        hi = [max(objs[o]['center'][i] + objs[o]['size'][i] / 2 for o in self.cfg['overview']) for i in range(3)]
        self.hero_c = [(a + b) / 2 for a, b in zip(lo, hi)]
        self.hero_r = max(math.dist(objs[o]['center'], self.hero_c) + objs[o]['r'] for o in self.cfg['overview'])
        self.hero_keys = sorted({k for o in self.cfg['overview'] for k in objs[o]['keys']})
    def cam(self, p): return [dot(p, self.B['x']), dot(p, self.B['y']), dot(p, self.B['z'])]
    def off(self, obj, mode):
        """exploded offset of an object in a given state ('assembled' | 'stage1' | 'exploded' | join dict)"""
        if mode == 'assembled': return [0, 0, 0]
        if mode == 'stage1' and obj not in STAGE1[self.kind]: return [0, 0, 0]
        key = self.sc['objects'][obj]['keys'][0]
        if isinstance(mode, dict) and obj in mode: key = self.sc['objects'][mode[obj]]['keys'][0]
        return self.sc['parts'][key]['offset']
    def centre(self, obj, mode): return add(self.sc['objects'][obj]['center'], self.off(obj, mode))
    def corners(self, obj, mode):
        o = self.sc['objects'][obj]; c = self.centre(obj, mode); h = [s / 2 for s in o['size']]
        return [[c[0] + a * h[0], c[1] + b * h[1], c[2] + d * h[2]] for a in (-1, 1) for b in (-1, 1) for d in (-1, 1)]
    def anchor(self, tag, mode, obj=None):
        P = self.sc['parts'][tag]
        off = self.off(obj, mode) if obj else P['offset']
        return add(P['anchor'], off)

def rot_y(v, pivot, yaw):
    c, s = math.cos(yaw), math.sin(yaw); x, z = v[0] - pivot[0], v[2] - pivot[2]
    return [pivot[0] + x * c + z * s, v[1], pivot[2] - x * s + z * c]

class View:
    def __init__(self, S, frame_objs, mode, yaw, area, fill, pivot=None, fixed=None):
        self.S, self.mode, self.yaw = S, mode, yaw
        if pivot is None:
            pts = [S.cam(S.centre(o, mode)) for o in frame_objs]; pivot = [sum(p[i] for p in pts) / len(pts) for i in range(3)]
        self.pivot = pivot
        if fixed: self.s, self.m, self.c = fixed
        else:
            pp = [self.proj(c) for o in frame_objs for c in S.corners(o, mode)]
            xs = [p[0] for p in pp]; ys = [p[1] for p in pp]
            ax0, ay0, ax1, ay1 = area
            self.s = min((ax1 - ax0) * fill / (max(xs) - min(xs)), (ay1 - ay0) * fill / (max(ys) - min(ys)))
            self.m = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2); self.c = ((ax0 + ax1) / 2, (ay0 + ay1) / 2)
    def proj(self, w): return rot_y(self.S.cam(w), self.pivot, self.yaw)
    def slide(self, q): return (self.c[0] + (q[0] - self.m[0]) * self.s, self.c[1] - (q[1] - self.m[1]) * self.s)
    def place(self, obj, target=False):
        q = self.proj(self.S.centre(obj, self.mode)); x, y = self.slide(q)
        return dict(obj=obj, x=x, y=y, side=2 * self.S.sc['objects'][obj]['r'] * self.s, depth=q[2], target=target, yaw=self.yaw)
    def hero(self):
        q = self.proj(self.S.hero_c); x, y = self.slide(q)
        return dict(obj='hero', x=x, y=y, side=2 * self.S.hero_r * self.s, depth=1e9, target=True, yaw=self.yaw)
    def pt(self, w): return self.slide(self.proj(w))

def push_off(placed, centre):
    for p in placed:
        if p['target']: continue
        dx, dy = p['x'] - centre[0], p['y'] - centre[1]; d = math.hypot(dx, dy)
        if d < 1e-3: dx, dy, d = -1.0, 0.0, 1.0
        ux, uy = dx / d, dy / d; p['side'] = min(p['side'], 3.0); h = p['side'] / 2
        inside = lambda x, y: x + h > 0 and x - h < SLIDE_W and y + h > 0 and y - h < SLIDE_H
        t = 0.0
        while inside(p['x'] + ux * t, p['y'] + uy * t) and t < 200: t += 0.25
        p['x'] += ux * (t + 0.15); p['y'] += uy * (t + 0.15); p['off'] = True

def layout(nd, kind, cfg):
    S = Scene(nd, kind, cfg); C = S.cfg; ov = C['overview']; out = {}
    # overview (exploded) fixes the scale used by stage1 too, so stage1 -> overview is a pure "opening" move
    V = View(S, ov, 'exploded', 0.0, OV_AREA, 0.94)
    out['overview'] = dict(objects=[V.place(o, True) for o in ov], anchors={n: V.pt(S.anchor(c['tag'], 'exploded')) for n, c in enumerate(C['components'], 1)})
    Vs = View(S, ov, 'stage1', 0.0, None, None, pivot=V.pivot, fixed=(V.s, V.m, V.c))
    out['stage1'] = dict(objects=[Vs.place(o, True) for o in ov])
    H2 = View(S, ov, 'assembled', 0.0, HERO_AREA, 0.84)
    out['hero2'] = dict(objects=[H2.place(o, True) for o in ov] + [H2.hero()])
    H1 = View(S, ov, 'assembled', math.radians(HERO_YAW1), HERO_AREA, 0.74, pivot=H2.pivot)
    out['hero1'] = dict(objects=[H1.hero()])
    comps = []
    for n, comp in enumerate(C['components'], 1):
        rep = comp.get('replace', {}); join = comp.get('join') or 'exploded'
        objs = [rep.get(o, o) for o in ov] + [o for o in comp['show'] if o not in [rep.get(x, x) for x in ov]]
        yaw = math.radians(YAW_DEG if n % 2 else -YAW_DEG)
        Vc = View(S, comp['show'], join, yaw, CP_AREA, 0.86)
        placed = [Vc.place(o, o in comp['show']) for o in objs]
        tg = [p for p in placed if p['target']]
        push_off(placed, (sum(p['x'] for p in tg) / len(tg), sum(p['y'] for p in tg) / len(tg)))
        tag_obj = next((o for o in comp['show'] if comp['tag'] in S.sc['objects'][o]['keys']), comp['show'][0])
        comps.append(dict(objects=placed, anchor=Vc.pt(S.anchor(comp['tag'], join, tag_obj))))
    out['comps'] = comps
    for st in [out['hero1'], out['hero2'], out['stage1'], out['overview']] + comps: st['objects'].sort(key=lambda p: p['depth'])
    out['scene'] = S
    return out

def img_name(kind, obj, yaw_rad): return f'{kind}_{obj}_y{round(math.degrees(yaw_rad)):+d}.png'

def image_jobs(nd, cfgs, dpi=165, off_px=160, max_px=1500):
    jobs = {}
    for kind, cfg in cfgs.items():
        L = layout(nd, kind, cfg); S = L['scene']
        for st in [L['hero1'], L['hero2'], L['stage1'], L['overview']] + L['comps']:
            for p in st['objects']:
                key = (kind, p['obj'], round(math.degrees(p['yaw'])))
                px = off_px if p.get('off') else int(min(max_px, max(off_px, p['side'] * dpi)))
                if p['obj'] == 'hero': px = int(min(1800, p['side'] * dpi))
                jobs[key] = max(jobs.get(key, 0), px)
    out = []
    for (kind, o, y), px in sorted(jobs.items()):
        S = Scene(nd, kind, cfgs[kind])
        if o == 'hero': keys, c, r = S.hero_keys, S.hero_c, S.hero_r
        else: ob = S.sc['objects'][o]; keys, c, r = ob['keys'], ob['center'], ob['r']
        out.append(dict(kind=kind, obj=o, keys=keys, center=c, r=r, yaw=y, px=px, out=img_name(kind, o, math.radians(y))))
    return out
