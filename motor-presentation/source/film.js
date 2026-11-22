// Continuous 3D camera flight for the Construction section (one timeline per motor, cut into per-slide clips).
// Camera language follows the reference: hero turntable -> pull back to an exploded overview -> push in on each
// part in turn, the camera arcing (dolly out, orbit, dolly in) between parts while the rest of the motor fades
// back in for context and away again, so the audience always sees where the part sits.
//
// usage: node film.js <induction|sync> <outdir> [fps=25] [mode=all|plan|stills|frames] [W=1600]
//   frames -> <outdir>/<kind>_frames/f00000.jpg ...  (white background, blends into the slide)
//   stills -> <outdir>/<kind>_end<K>.png (K = 0 overview, 1..N components) at 2x, white background
//   plan   -> <outdir>/<kind>_plan.json: segment frame ranges + label anchors at each segment end
const { chromium } = require('playwright');
const fs = require('fs');

const COMPONENTS = {
  induction: [
    { keys: ['statorCore', 'statorWinding'], dir: [-1.0, 0.55, 1.25], tag: 'statorCore' },
    { keys: ['rotorCore', 'rotorBars', 'endRings', 'shaft'], dir: [-0.8, 0.5, 1.3], tag: 'rotorCore' },
    { keys: ['rotorBars', 'endRings'], dir: [-1.0, 0.5, 1.2], tag: 'endRings' },
    { keys: ['shaft'], dir: [-0.35, 0.45, 1.3], tag: 'shaft', fill: 0.8 },
    { keys: ['bearingDE'], dir: [-1.0, 0.55, 0.9], tag: 'bearingDE', fill: 0.62 },
    { keys: ['frame', 'endShieldDE', 'endShieldNDE'], dir: [-1.0, 0.6, 1.25], tag: 'frame', join: { endShieldDE: 'frame', endShieldNDE: 'frame' } },
    { keys: ['fan'], dir: [1.0, 0.45, 1.0], tag: 'fan', fill: 0.68 },
  ],
  sync: [
    { keys: ['statorCore', 'statorWinding'], dir: [-1.0, 0.55, 1.25], tag: 'statorCore' },
    { keys: ['rotorPoles', 'fieldWinding', 'damper', 'shaft'], dir: [-0.8, 0.5, 1.3], tag: 'rotorPoles' },
    { keys: ['fieldWinding'], ghost: { rotorPoles: 0.16 }, dir: [-1.0, 0.6, 1.2], tag: 'fieldWinding' },
    { keys: ['damper'], ghost: { rotorPoles: 0.16 }, dir: [-1.0, 0.6, 1.2], tag: 'damper' },
    { keys: ['sliprings'], dir: [-1.0, 0.5, 1.25], tag: 'sliprings', fill: 0.7 },
    { keys: ['exciter'], dir: [-1.0, 0.45, 1.3], tag: 'exciter', fill: 0.72 },
    { keys: ['shaft'], dir: [-0.35, 0.45, 1.3], tag: 'shaft', fill: 0.8 },
    { keys: ['bearingDE'], dir: [-1.0, 0.55, 1.0], tag: 'bearingDE', fill: 0.62 },
    { keys: ['frame', 'endShieldDE', 'endShieldNDE'], dir: [-1.0, 0.55, 1.25], tag: 'frame', join: { endShieldDE: 'frame', endShieldNDE: 'frame' } },
    { keys: ['cooling', 'shaftFan'], ghost: { frame: 0.1 }, ghostFit: true, dir: [-1.0, 0.6, 1.25], tag: 'cooling', join: { cooling: 'frame', shaftFan: 'frame' } },
  ],
};
const OVERVIEW_DIR = [-0.62, 0.42, 1.0];
const HERO_DIR = { induction: [-1.0, 0.42, 1.05], sync: [-1.0, 0.45, 1.1] };
const T_INTRO = 4.6, T_SEG = 3.0;

// ---------------- in-page code ----------------
const PAGE = `
(function(){
const S = STAGE, T = THREE, V = T.Vector3, M = S.model;
const sm = x => { x = Math.min(1, Math.max(0, x)); return x * x * x * (x * (x * 6 - 15) + 10); };   // smootherstep
const lerp = (a, b, t) => a + (b - a) * t;
function FIT(box, dir, fill) {
  const c = box.getCenter(new V()); const r = box.getSize(new V()).length() / 2;
  const D = new V(...dir).normalize(); let d = r * 3.2; const off = new V();
  const pts = []; for (let i = 0; i < 8; i++) pts.push(new V(i & 1 ? box.max.x : box.min.x, i & 2 ? box.max.y : box.min.y, i & 4 ? box.max.z : box.min.z));
  for (let it = 0; it < 16; it++) {
    const tgt = c.clone().add(off); S.setCamera(tgt.clone().add(D.clone().multiplyScalar(d)), tgt); S.camera.updateMatrixWorld();
    let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
    pts.forEach(p => { const q = p.clone().project(S.camera); x0 = Math.min(x0, q.x); x1 = Math.max(x1, q.x); y0 = Math.min(y0, q.y); y1 = Math.max(y1, q.y); });
    const right = new V().setFromMatrixColumn(S.camera.matrixWorld, 0), up = new V().setFromMatrixColumn(S.camera.matrixWorld, 1);
    const h = Math.tan(S.camera.fov * Math.PI / 360) * d, w = h * S.camera.aspect;
    off.add(right.multiplyScalar((x0 + x1) / 2 * w)).add(up.multiplyScalar((y0 + y1) / 2 * h));
    d *= 0.35 + 0.65 * (Math.max((x1 - x0) / 2, (y1 - y0) / 2) / fill);
  }
  return { tgt: c.clone().add(off), dir: D, d };
}
const visibleKeys = M.order.filter(k => !M.parts[k].hiddenUntilFocus);
const EXP = {}; visibleKeys.forEach(k => EXP[k] = M.parts[k].offset.clone());
// a "state" = offsets per part, alpha per part, camera {tgt, dir, d}
function offsetsFor(c) {
  const o = {}; visibleKeys.forEach(k => o[k] = EXP[k].clone());
  if (c && c.join) Object.entries(c.join).forEach(([k, to]) => o[k] = EXP[to].clone());
  return o;
}
function applyOffsets(o) { visibleKeys.forEach(k => M.parts[k].group.position.copy(o[k])); M.group.updateMatrixWorld(true); }
function boxOf(keys) { const b = new T.Box3(); keys.forEach(k => b.expandByObject(M.parts[k].group)); return b; }
window.FILM = { states: [] };
FILM.build = function (comps, ovDir, heroDir) {
  // hero: assembled motor
  const zero = {}; visibleKeys.forEach(k => zero[k] = new V());
  applyOffsets(zero); const hero = FIT(boxOf(visibleKeys), heroDir, 0.66);
  const ovOff = offsetsFor(null); applyOffsets(ovOff); const ov = FIT(boxOf(visibleKeys), ovDir, 0.9);
  const all1 = {}; visibleKeys.forEach(k => all1[k] = 1);
  FILM.hero = { off: zero, alpha: all1, cam: hero };
  FILM.states = [{ off: ovOff, alpha: all1, cam: ov, tag: null }];
  comps.forEach(c => {
    const off = offsetsFor(c); applyOffsets(off);
    const cam = FIT(boxOf(c.keys.concat(c.ghostFit ? Object.keys(c.ghost) : [])), c.dir, c.fill || 0.78);
    const alpha = {}; visibleKeys.forEach(k => alpha[k] = c.keys.includes(k) ? 1 : (c.ghost && c.ghost[k]) || 0);
    FILM.states.push({ off, alpha, cam, keys: c.keys, tag: c.tag });
  });
};
function camLerp(A, B, e, bump, eD) {
  if (eD === undefined) eD = e;
  const tgt = A.tgt.clone().lerp(B.tgt, e);
  const qa = new T.Quaternion(), dir = A.dir.clone();
  const q = new T.Quaternion().setFromUnitVectors(A.dir, B.dir); qa.slerp(q, e); dir.applyQuaternion(qa);
  const d = Math.exp(lerp(Math.log(A.d), Math.log(B.d), eD)) * (1 + bump * Math.sin(Math.PI * e));
  return { tgt, dir, d };
}
function setCam(c) { S.setCamera(c.tgt.clone().add(c.dir.clone().multiplyScalar(c.d)), c.tgt); S.camera.updateMatrixWorld(); }
function setAlphas(al, glow) {
  visibleKeys.forEach(k => { const a = al[k], p = M.parts[k]; p.group.visible = a > 0.004; if (a > 0.004) S.setPartAlpha(p, Math.min(1, a), (glow && glow[k]) || 0); });
}
function floorOf(keys) { const b = boxOf(keys); return b.isEmpty() ? -0.565 : b.min.y - 0.002; }
// time t (s) -> scene. Segment 0: hero -> overview (explode). Segment k: state k-1 -> state k.
FILM.at = function (t, T_INTRO, T_SEG) {
  if (t <= T_INTRO) {
    const u = t / T_INTRO, H = FILM.hero, O = FILM.states[0];
    // turntable while assembled, explode as the camera pulls back to the overview
    const spin = new T.Quaternion().setFromAxisAngle(new V(0, 1, 0), -0.55 * (1 - sm(u / 0.75)));
    const hc = { tgt: H.cam.tgt, dir: H.cam.dir.clone().applyQuaternion(spin), d: H.cam.d };
    const ec = sm((u - 0.18) / 0.72);
    setCam(camLerp(hc, O.cam, ec, 0.0));
    S.applyExplode(sm((u - 0.28) / 0.62)); M.group.updateMatrixWorld(true);
    setAlphas(O.alpha); S.floor.position.y = lerp(-0.565, floorOf(visibleKeys), sm((u - 0.28) / 0.62)); return;
  }
  let k = Math.min(FILM.states.length - 1, 1 + Math.floor((t - T_INTRO) / T_SEG - 1e-9));
  const u = Math.min(1, (t - T_INTRO - (k - 1) * T_SEG) / T_SEG);
  const A = FILM.states[k - 1], B = FILM.states[k];
  const e = sm(u);
  // camera: dolly out - orbit - dolly in (less pull-back when the move is mostly a zoom)
  const ratio = Math.min(A.cam.d, B.cam.d) / Math.max(A.cam.d, B.cam.d);
  const travel = A.cam.tgt.distanceTo(B.cam.tgt) / Math.max(A.cam.d, B.cam.d);
  // wider next shot: pull back first, then travel; tighter next shot: travel first, then push in
  const zoomOut = B.cam.d > A.cam.d * 1.25, zoomIn = B.cam.d < A.cam.d / 1.25;
  const eD = zoomOut ? sm(u / 0.55) : zoomIn ? sm((u - 0.4) / 0.6) : e;
  const eT = zoomOut ? sm((u - 0.2) / 0.8) : zoomIn ? sm(u / 0.75) : e;
  setCam(camLerp(A.cam, B.cam, eT, 0.42 * ratio * Math.min(1, travel * 1.6 + 0.35), eD));
  // parts glide between layouts (e.g. end shields joining the frame)
  const off = {}; visibleKeys.forEach(kk => off[kk] = A.off[kk].clone().lerp(B.off[kk], sm((u - 0.15) / 0.7))); applyOffsets(off);
  // context: the whole motor fades back in mid-flight, then everything but the target fades away
  const ctx = 0.2, al = {}, glow = {};
  const tgtKeys = B.keys || [];
  visibleKeys.forEach(kk => {
    const a0 = A.alpha[kk], a1 = B.alpha[kk];
    if (tgtKeys.includes(kk)) { al[kk] = lerp(Math.max(a0, ctx * sm(u / 0.25)), 1, sm((u - 0.12) / 0.5)); glow[kk] = Math.sin(Math.PI * Math.min(1, Math.max(0, (u - 0.1) / 0.9))) * 0.7; }
    else { const mid = Math.max(a0 * (1 - sm(u / 0.45)), ctx * sm(u / 0.3)); al[kk] = lerp(mid, a1, sm((u - 0.55) / 0.4)); }
  });
  // fade context parts that come between the camera and the target (no huge blurred ghosts near the lens)
  const cp = S.camera.position, vd = new V(); S.camera.getWorldDirection(vd); const dT = S.camTarget.clone().sub(cp).dot(vd);
  visibleKeys.forEach(kk => {
    if (al[kk] <= 0.004) return;
    const bb = boxOf([kk]); const pc = bb.getCenter(new V()); const rad = bb.getSize(new V()).length() / 2;
    const near = pc.clone().sub(cp).dot(vd) - rad;        // closest depth of the part
    let f = sm((near - 0.3 * dT) / (0.4 * dT));
    if (tgtKeys.includes(kk)) f = Math.max(f, sm((u - 0.6) / 0.3));   // targets always arrive by the end
    al[kk] *= f;
  });
  setAlphas(al, glow);
  S.floor.position.y = lerp(floorOf(A.keys || visibleKeys), floorOf(tgtKeys.length ? tgtKeys : visibleKeys), e);
};
FILM.anchors = function (k) { // normalized screen positions of tags at the end of segment k
  const out = {};
  const B = FILM.states[k];
  const tags = k === 0 ? FILM.comps.map(c => c.tag) : [B.tag];
  tags.forEach((tag, i) => { const [x, y] = S.project(S.anchorWorld(tag)); out[k === 0 ? i + 1 : k] = [x / S.W, y / S.H]; });
  return out;
};
})();`;

(async () => {
  const [kind, outdir, fpsArg, mode = 'all', wArg] = process.argv.slice(2);
  const fps = +(fpsArg || 25), W = +(wArg || 1600), H = Math.round(W * 1110 / 1600);
  const comps = COMPONENTS[kind];
  fs.mkdirSync(outdir, { recursive: true });
  const total = T_INTRO + comps.length * T_SEG;
  const seg = [0]; for (let k = 0; k <= comps.length; k++) seg.push(Math.round((T_INTRO + k * T_SEG) * fps)); seg.shift();
  // segment k (0 = intro) spans frames [k ? bounds[k-1] : 0, bounds[k]] inclusive of the shared boundary frame
  const bounds = [0].concat(comps.map((_, i) => Math.round((T_INTRO + (i + 1) * T_SEG) * fps)));
  bounds[0] = Math.round(T_INTRO * fps);
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const open = async (w, h, transparent) => {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    p.on('pageerror', e => console.log('PAGEERR', e.message));
    await p.goto('file://' + __dirname + '/stage.html');
    await p.evaluate(o => { window.NO_BUMP = o.nobump; STAGE.init(o); const r = document.getElementById('root'); r.style.background = '#ffffff'; document.body.style.background = '#ffffff'; }, { model: kind, light: true, w, h, shadow: 2048, grid: false, nobump: process.env.NO_BUMP === '1' });
    await p.evaluate(PAGE);
    await p.evaluate(([c, o, hd]) => { FILM.comps = c; FILM.build(c, o, hd); }, [comps, OVERVIEW_DIR, HERO_DIR[kind]]);
    return p;
  };
  if (mode === 'plan' || mode === 'all' || mode === 'stills') {
    const p = await open(W, H);
    const plan = { fps, W, H, T_INTRO, T_SEG, segments: [] };
    for (let k = 0; k <= comps.length; k++) {
      const f0 = k === 0 ? 0 : bounds[k - 1], f1 = bounds[k];
      await p.evaluate(([t, a, s]) => FILM.at(t, a, s), [f1 / fps, T_INTRO, T_SEG]);
      plan.segments.push({ k, f0, f1, anchors: await p.evaluate(k => FILM.anchors(k), k) });
    }
    fs.writeFileSync(`${outdir}/${kind}_plan.json`, JSON.stringify(plan, null, 1));
    await p.close(); console.log('plan written', plan.segments.map(s => s.f0 + '-' + s.f1).join(' '));
  }
  if (mode === 'stills' || mode === 'all') {
    // end-of-segment stills at 2x for the slide (sharper than the video frame, identical framing)
    const p = await open(W * 2, H * 2);
    for (let k = 0; k <= comps.length; k++) {
      const t0 = Date.now();
      await p.evaluate(([t, a, s]) => { FILM.at(t, a, s); STAGE.render(); }, [bounds[k] / fps, T_INTRO, T_SEG]);
      await p.locator('#root').screenshot({ path: `${outdir}/${kind}_end${k}.png`, timeout: 600000 });
      console.log('still', k, ((Date.now() - t0) / 1000).toFixed(0) + 's');
    }
    await p.close();
  }
  if (mode === 'frames' || mode === 'all') {
    const dir = `${outdir}/${kind}_frames`; fs.mkdirSync(dir, { recursive: true });
    const p = await open(W, H);
    const N = bounds[bounds.length - 1]; const t0 = Date.now();
    for (let i = 0; i <= N; i++) {
      const fn = `${dir}/f${String(i).padStart(5, '0')}.jpg`;
      if (fs.existsSync(fn)) continue;
      await p.evaluate(([t, a, s]) => { FILM.at(t, a, s); STAGE.render(); }, [i / fps, T_INTRO, T_SEG]);
      await p.locator('#root').screenshot({ path: fn, type: 'jpeg', quality: 94, timeout: 600000 });
      if (i % 25 === 0) console.log(kind, i, '/', N, ((Date.now() - t0) / 1000 / (i + 1)).toFixed(2), 's/frame');
    }
    await p.close();
  }
  await b.close();
})();
