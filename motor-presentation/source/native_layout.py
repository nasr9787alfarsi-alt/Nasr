"""Layout engine for the PowerPoint-native 3D construction section.

Every slide is a view of one virtual camera on the exploded motor: all objects share the same projection,
scale and turn, so Morph between slides moves the parts exactly as a camera move would (zoom, pan, separation).
Positions in inches on a 13.333 x 7.5 slide. Distances in metres. View direction D0 from native_cfg.js.
"""
import json, math, os

SLIDE_W, SLIDE_H = 13.333, 7.5
OV_AREA = (0.45, 1.4, 8.95, 7.15)     # overview: whole exploded motor
CP_AREA = (0.55, 1.45, 8.65, 7.1)     # component close-up
YAW_DEG = 9.0                          # gentle alternating turntable swing on component slides

def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def add(a, b): return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]

class Scene:
    def __init__(self, native_dir, kind):
        cfg = json.load(open(os.path.join(native_dir, 'cfg.json')))
        self.cfg = cfg['CFG'][kind]; self.B = cfg['basis']; self.fov = cfg['FOV_DEG']
        self.sc = json.load(open(os.path.join(native_dir, f'{kind}_scene.json')))
        self.kind = kind

    def cam(self, p):                       # world -> camera coords (x right, y up, z towards camera)
        return [dot(p, self.B['x']), dot(p, self.B['y']), dot(p, self.B['z'])]

    def offset(self, obj, join):
        keys = self.sc['objects'][obj]['keys']; k = keys[0]
        if join and obj in join: k = self.sc['objects'][join[obj]]['keys'][0]
        return self.sc['parts'][k]['offset']

    def obj_center(self, obj, join=None):
        return add(self.sc['objects'][obj]['center'], self.offset(obj, join))

    def corners(self, obj, join=None):
        o = self.sc['objects'][obj]; c = self.obj_center(obj, join); h = [s / 2 for s in o['size']]
        return [[c[0] + sx * h[0], c[1] + sy * h[1], c[2] + sz * h[2]] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]

    def anchor_world(self, tag, join=None, obj=None):
        P = self.sc['parts'][tag]; off = P['offset']
        if join and obj and obj in join: off = self.offset(obj, join)
        return add(P['anchor'], off)

def rot_y(v, pivot, yaw):                   # rotate camera-space point about the camera's up axis through pivot
    c, s = math.cos(yaw), math.sin(yaw); x, z = v[0] - pivot[0], v[2] - pivot[2]
    return [pivot[0] + x * c + z * s, v[1], pivot[2] - x * s + z * c]

def fit(points2d, area, fill):
    xs = [p[0] for p in points2d]; ys = [p[1] for p in points2d]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    ax0, ay0, ax1, ay1 = area; s = min((ax1 - ax0) * fill / w, (ay1 - ay0) * fill / h)
    return s, ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2), ((ax0 + ax1) / 2, (ay0 + ay1) / 2)

def view(S, objs, targets, join, yaw, area, fill):
    """place objs for a camera framing `targets` (all objects share one projection)"""
    pivot = None
    tc = [S.cam(S.obj_center(o, join)) for o in targets]
    pivot = [sum(p[i] for p in tc) / len(tc) for i in range(3)]
    proj = lambda w: rot_y(S.cam(w), pivot, yaw)
    pts = [proj(c) for o in targets for c in S.corners(o, join)]
    s, (mx, my), (cx, cy) = fit([(p[0], p[1]) for p in pts], area, fill)
    to_slide = lambda q: (cx + (q[0] - mx) * s, cy - (q[1] - my) * s)
    placed = []
    for o in objs:
        q = proj(S.obj_center(o, join)); x, y = to_slide(q); side = 2 * S.sc['objects'][o]['r'] * s
        placed.append(dict(obj=o, x=x, y=y, side=side, depth=q[2], target=o in targets, yaw=yaw))
    return placed, proj, to_slide, s

def push_off(placed, centre):
    """non-target objects leave the slide along the line from the focus outwards (camera passes them)"""
    for p in placed:
        if p['target']: continue
        dx, dy = p['x'] - centre[0], p['y'] - centre[1]; d = math.hypot(dx, dy)
        if d < 1e-3: dx, dy, d = -1.0, 0.0, 1.0
        ux, uy = dx / d, dy / d
        p['side'] = min(p['side'], 3.0)                 # parked parts stay modest so fly-bys never fill the slide
        h = p['side'] / 2
        def inside(x, y): return x + h > 0 and x - h < SLIDE_W and y + h > 0 and y - h < SLIDE_H
        t = 0.0
        while inside(p['x'] + ux * t, p['y'] + uy * t) and t < 200: t += 0.25
        p['x'] += ux * (t + 0.15); p['y'] += uy * (t + 0.15); p['off'] = True

def layout(native_dir, kind):
    S = Scene(native_dir, kind); C = S.cfg
    slides = []
    # overview
    objs = list(C['overview'])
    placed, proj, to_slide, s = view(S, objs, objs, None, 0.0, OV_AREA, 0.94)
    anchors = {}
    for n, comp in enumerate(C['components'], 1):
        tag = comp['tag']; anchors[n] = to_slide(proj(S.anchor_world(tag)))
    slides.append(dict(k=0, objects=placed, anchors=anchors, scale=s))
    for n, comp in enumerate(C['components'], 1):
        rep = comp.get('replace', {}); join = comp.get('join')
        objs = [rep.get(o, o) for o in C['overview']]
        for o in comp['show']:
            if o not in objs: objs.append(o)
        yaw = math.radians(YAW_DEG if n % 2 else -YAW_DEG)
        placed, proj, to_slide, s = view(S, objs, comp['show'], join, yaw, CP_AREA, 0.86)
        tgt = [p for p in placed if p['target']]
        centre = (sum(p['x'] for p in tgt) / len(tgt), sum(p['y'] for p in tgt) / len(tgt))
        push_off(placed, centre)
        tag_obj = next((o for o in comp['show'] if comp['tag'] in S.sc['objects'][o]['keys']), comp['show'][0])
        a = to_slide(proj(S.anchor_world(comp['tag'], join, tag_obj)))
        slides.append(dict(k=n, objects=placed, anchors={n: a}, scale=s))
    for sl in slides: sl['objects'].sort(key=lambda p: p['depth'])   # far -> near = bottom -> top
    return slides

def image_jobs(native_dir, kinds, dpi=230, off_px=192, max_px=1700):
    jobs = {}
    for kind in kinds:
        for sl in layout(native_dir, kind):
            for p in sl['objects']:
                key = (kind, p['obj'], round(math.degrees(p['yaw'])))
                px = off_px if p.get('off') else int(min(max_px, max(off_px, p['side'] * dpi)))
                jobs[key] = max(jobs.get(key, 0), px)
    return jobs

def img_name(kind, obj, yaw_rad):
    return f'{kind}_{obj}_y{round(math.degrees(yaw_rad)):+d}.png'

if __name__ == '__main__':
    import sys
    nd = sys.argv[1]
    jobs = image_jobs(nd, ['induction', 'sync'])
    S = {k: Scene(nd, k) for k in ('induction', 'sync')}
    out = [dict(kind=k, obj=o, keys=S[k].sc['objects'][o]['keys'], center=S[k].sc['objects'][o]['center'], r=S[k].sc['objects'][o]['r'],
                yaw=y, px=px, out=img_name(k, o, math.radians(y))) for (k, o, y), px in sorted(jobs.items())]
    json.dump(out, open(os.path.join(nd, 'jobs.json'), 'w'), indent=1)
    print(len(out), 'images;', sum(j['px'] ** 2 for j in out) / 1e6, 'Mpx')
    for k in ('induction', 'sync'):
        for sl in layout(nd, k):
            on = [p['obj'] for p in sl['objects'] if not p.get('off')]
            print(k, sl['k'], 'scale %.2f' % sl['scale'], 'on-slide:', on)
