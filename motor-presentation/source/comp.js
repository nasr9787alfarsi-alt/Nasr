// Component close-up renders for the one-slide-per-component Construction section.
// usage: node comp.js <induction|sync> <outdir> [all|overview|N] [scale]
// Writes <outdir>/<model>_overview.png + <model>_overview.json (label anchors as 0..1 of the image)
// and <outdir>/<model>_c<N>.png for every component in COMPONENTS (transparent PNG, 4:3).
const { chromium } = require('playwright');
const fs = require('fs');

// keys: parts rendered; ghost: parts shown faintly for context (included in framing when ghostFit);
// dir: camera direction from the part; tag: part whose anchor carries the overview number;
// assembled: render in assembled position (else exploded); fill: fraction of frame to fill
const COMPONENTS = {
  induction: [
    { n: 1, keys: ['statorCore', 'statorWinding'], dir: [-1.0, 0.55, 1.25], tag: 'statorCore' },
    { n: 2, keys: ['rotorCore', 'rotorBars', 'endRings', 'shaft'], dir: [-0.8, 0.5, 1.3], tag: 'rotorCore' },
    { n: 3, keys: ['rotorBars', 'endRings'], dir: [-1.0, 0.5, 1.2], tag: 'endRings' },
    { n: 4, keys: ['shaft'], dir: [-0.35, 0.45, 1.3], tag: 'shaft' },
    { n: 5, keys: ['bearingDE'], dir: [-1.0, 0.55, 0.9], tag: 'bearingNDE' },
    { n: 6, keys: ['frame', 'endShieldDE', 'endShieldNDE'], dir: [-1.0, 0.6, 1.25], tag: 'frame', assembled: true },
    { n: 7, keys: ['fan'], dir: [1.0, 0.45, 1.0], tag: 'fan' },
  ],
  sync: [
    { n: 1, keys: ['statorCore', 'statorWinding'], dir: [-1.0, 0.55, 1.25], tag: 'statorCore' },
    { n: 2, keys: ['rotorPoles', 'fieldWinding', 'damper', 'shaft'], dir: [-0.8, 0.5, 1.3], tag: 'rotorPoles' },
    { n: 3, keys: ['fieldWinding'], ghost: ['rotorPoles'], dir: [-1.0, 0.6, 1.2], tag: 'fieldWinding' },
    { n: 4, keys: ['damper'], ghost: ['rotorPoles'], dir: [-1.0, 0.6, 1.2], tag: 'damper' },
    { n: 5, keys: ['sliprings'], dir: [-1.0, 0.5, 1.25], tag: 'sliprings' },
    { n: 6, keys: ['exciter'], dir: [-1.0, 0.45, 1.3], tag: 'exciter', fill: 0.95 },
    { n: 7, keys: ['shaft'], dir: [-0.35, 0.45, 1.3], tag: 'shaft' },
    { n: 8, keys: ['bearingDE'], dir: [-1.0, 0.55, 1.0], tag: 'bearingNDE' },
    { n: 9, keys: ['frame', 'endShieldDE', 'endShieldNDE'], dir: [-1.0, 0.55, 1.25], tag: 'frame', assembled: true },
    { n: 10, keys: ['cooling', 'shaftFan'], ghost: ['frame'], ghostFit: true, dir: [-1.0, 0.6, 1.25], tag: 'cooling', assembled: true, fill: 0.9 },
  ],
};
const OVERVIEW_DIR = { induction: [-0.62, 0.42, 1.0], sync: [-0.62, 0.42, 1.0] };

// Runs in the page: frame a Box3 so its projected extent fills `fill` of the narrower half-extent.
const FIT = `window.FIT = function (box, dir, fill) {
  const S = STAGE, V = THREE.Vector3; const c = box.getCenter(new V()); const r = box.getSize(new V()).length() / 2;
  const D = new V(...dir).normalize(); let d = r * 3.2;
  const pts = []; for (let i = 0; i < 8; i++) pts.push(new V(i & 1 ? box.max.x : box.min.x, i & 2 ? box.max.y : box.min.y, i & 4 ? box.max.z : box.min.z));
  let off = new V(0, 0, 0);
  for (let it = 0; it < 14; it++) {
    const tgt = c.clone().add(off);
    S.setCamera(tgt.clone().add(D.clone().multiplyScalar(d)), tgt); S.camera.updateMatrixWorld();
    let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
    pts.forEach(p => { const q = p.clone().project(S.camera); x0 = Math.min(x0, q.x); x1 = Math.max(x1, q.x); y0 = Math.min(y0, q.y); y1 = Math.max(y1, q.y); });
    // recentre the projected box, then scale distance so the larger extent equals fill
    const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
    const right = new V().setFromMatrixColumn(S.camera.matrixWorld, 0), up = new V().setFromMatrixColumn(S.camera.matrixWorld, 1);
    const h = Math.tan(S.camera.fov * Math.PI / 360) * d, w = h * S.camera.aspect;
    off.add(right.multiplyScalar(cx * w)).add(up.multiplyScalar(cy * h));
    const m = Math.max((x1 - x0) / 2, (y1 - y0) / 2);
    d *= 0.35 + 0.65 * (m / fill);
  }
  return d;
};`;

(async () => {
  let [kind, outdir, only, scaleArg] = process.argv.slice(2); if (!only || only === 'all') only = '';
  const sc = parseFloat(scaleArg || '1');
  fs.mkdirSync(outdir, { recursive: true });
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const job = async (name, W, H, fn, arg) => {
    const p = await b.newPage({ viewport: { width: W, height: H } });
    p.on('pageerror', e => console.log('PAGEERR', e.message));
    await p.goto('file://' + __dirname + '/stage.html');
    await p.evaluate(o => STAGE.init(o), { model: kind, transparent: true, light: true, w: W, h: H, shadow: 4096 });
    await p.evaluate(FIT);
    const res = await p.evaluate(fn, arg);
    await p.locator('#root').screenshot({ path: outdir + '/' + name + '.png', omitBackground: true, timeout: 900000 });
    await p.close(); return res;
  };
  // keep the key light's shadow camera tight around the subject (crisper contact shadows)
  const comps = COMPONENTS[kind];
  if (!only || only === 'overview') {
    const t0 = Date.now();
    const anchors = await job(kind + '_overview', Math.round(2400 * sc), Math.round(1500 * sc), ([dir, comps]) => {
      const S = STAGE, T = THREE, M = S.model; S.applyExplode(1); M.group.updateMatrixWorld(true);
      const box = new T.Box3(); M.order.forEach(k => { if (M.parts[k].group.visible) box.expandByObject(M.parts[k].group); });
      FIT(box, dir, 0.93); S.render();
      const out = {}; comps.forEach(c => { const [x, y] = S.project(S.anchorWorld(c.tag)); out[c.n] = [x / S.W, y / S.H]; });
      return out;
    }, [OVERVIEW_DIR[kind], comps]);
    fs.writeFileSync(outdir + '/' + kind + '_overview.json', JSON.stringify(anchors, null, 1));
    console.log(kind, 'overview', ((Date.now() - t0) / 1000).toFixed(0) + 's');
  }
  for (const c of comps) {
    if (only && +only !== c.n) continue;
    const t0 = Date.now();
    await job(kind + '_c' + c.n, Math.round(2000 * sc), Math.round(1500 * sc), (c) => {
      const S = STAGE, T = THREE, V = T.Vector3, M = S.model;
      if (!c.assembled) S.applyExplode(1);
      const ghost = c.ghost || [];
      M.order.forEach(k => { M.parts[k].group.visible = c.keys.includes(k) || ghost.includes(k); });
      M.group.updateMatrixWorld(true);
      const box = new T.Box3(); c.keys.concat(c.ghostFit ? ghost : []).forEach(k => box.expandByObject(M.parts[k].group));
      const ctr = box.getCenter(new V()); M.group.position.sub(ctr); M.group.updateMatrixWorld(true); box.translate(ctr.clone().negate());
      ghost.forEach(k => S.setPartAlpha(M.parts[k], c.ghostFit ? 0.1 : 0.16, 0));
      S.floor.position.y = box.min.y - 0.002;
      const r = box.getSize(new V()).length() / 2;
      FIT(box, c.dir, c.fill || 0.86);
      const k = S.key, cam = k.shadow.camera, s = Math.max(r * 1.5, 0.35);
      cam.left = -s; cam.right = s; cam.top = s; cam.bottom = -s; cam.near = 0.1; cam.far = r * 12 + 4; cam.updateProjectionMatrix();
      k.position.set(-3, 6, 4).normalize().multiplyScalar(r * 5 + 1.5); k.target.position.set(0, 0, 0); k.target.updateMatrixWorld();
      S.render(); return true;
    }, c);
    console.log(kind, 'c' + c.n, ((Date.now() - t0) / 1000).toFixed(0) + 's');
  }
  await b.close();
})();
