// Export each display object of a motor as a binary glTF (.glb) for PowerPoint 3D models.
// usage: node glb.js <induction|sync> <outdir>
// - geometry re-centred on the object's bounding-box centre and pre-rotated so that PowerPoint's default
//   camera (on +Z, looking at the origin, +Y up) sees exactly the overview view direction D0
// - instanced laminations are baked into real geometry (thinned: every 4th sheet, 4x thick) to keep files light
// Writes <outdir>/<kind>_<object>.glb and <outdir>/<kind>_scene.json (objects: centre, half-diagonal r,
// box size, bytes; parts: exploded offset + label anchor, in metres, world axes).
const { chromium } = require('playwright');
const fs = require('fs');
const { CFG, D0, basis } = require('./native_cfg.js');

(async () => {
  const [kind, outdir] = process.argv.slice(2);
  fs.mkdirSync(outdir, { recursive: true });
  const cfg = CFG[kind], B = basis(D0);
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 400, height: 300 } });
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.goto('file://' + __dirname + '/stage.html');
  await p.addScriptTag({ path: __dirname + '/node_modules/three/examples/js/exporters/GLTFExporter.js' });
  await p.evaluate(k => { window.NO_BUMP = true; STAGE.init({ model: k, light: true, w: 400, h: 300 }); }, kind);
  const scene = { D0, basis: B, objects: {}, parts: {} };
  scene.parts = await p.evaluate(() => { const M = STAGE.model, o = {}; M.order.forEach(k => { const P = M.parts[k]; o[k] = { offset: P.offset.toArray(), anchor: P.anchor.toArray() }; }); return o; });
  for (const [obj, keys] of Object.entries(cfg.objects)) {
    const res = await p.evaluate(async ([keys, B]) => {
      const T = THREE, M = STAGE.model;
      M.order.forEach(k => M.parts[k].group.position.set(0, 0, 0)); M.group.updateMatrixWorld(true);
      const box = new T.Box3(); keys.forEach(k => box.expandByObject(M.parts[k].group));
      const c = box.getCenter(new T.Vector3()), sz = box.getSize(new T.Vector3());
      // world -> camera-basis rotation (rows x', y', z')
      const R = new T.Matrix4().set(B.x[0], B.x[1], B.x[2], 0, B.y[0], B.y[1], B.y[2], 0, B.z[0], B.z[1], B.z[2], 0, 0, 0, 0, 1);
      const pre = new T.Matrix4().multiplyMatrices(R, new T.Matrix4().makeTranslation(-c.x, -c.y, -c.z));
      const root = new T.Scene(); const g = new T.Group(); root.add(g);
      const cache = new Map();
      const conv = m => {
        if (cache.has(m)) return cache.get(m);
        const s = new T.MeshStandardMaterial({ color: m.color ? m.color.clone() : new T.Color(0xaaaaaa), metalness: m.metalness ?? 0.2, roughness: m.roughness ?? 0.6,
          map: m.map || null, side: m.side, transparent: !!m.userData.baseTransparent, opacity: m.userData.baseOpacity ?? 1 });
        s.name = m.name || ''; cache.set(m, s); return s;
      };
      let r = 0;
      const place = (geo, mw) => { const gg = geo.clone(); gg.applyMatrix4(new T.Matrix4().multiplyMatrices(pre, mw)); if (gg.attributes.uv2) gg.deleteAttribute('uv2');
        const pos = gg.attributes.position; for (let i = 0; i < pos.count; i++) r = Math.max(r, Math.hypot(pos.getX(i), pos.getY(i), pos.getZ(i))); return gg; };
      keys.forEach(k => M.parts[k].group.traverse(o => {
        if (!o.isMesh || !o.visible) return; o.updateMatrixWorld(true);
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        if (o.isInstancedMesh) {
          const step = o.count > 16 ? 5 : 1, im = new T.Matrix4(), list = [];
          for (let i = 0; i < o.count; i += step) { o.getMatrixAt(i, im); const sc = new T.Matrix4().makeScale(step, 1, 1); list.push(place(o.geometry, new T.Matrix4().multiplyMatrices(o.matrixWorld, im).multiply(sc))); }
          g.add(new T.Mesh(T.BufferGeometryUtils.mergeBufferGeometries(list.every(q => q.index) ? list : list.map(q => q.index ? q.toNonIndexed() : q)), conv(mats[0])));
        } else g.add(new T.Mesh(place(o.geometry, o.matrixWorld), Array.isArray(o.material) ? mats.map(conv) : conv(mats[0])));
      }));
      const buf = await new Promise(res => new T.GLTFExporter().parse(root, res, { binary: true, embedImages: true, maxTextureSize: 1024 }));
      let bin = ''; const u8 = new Uint8Array(buf); for (let i = 0; i < u8.length; i += 0x8000) bin += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
      return { b64: btoa(bin), center: c.toArray(), size: sz.toArray(), r };
    }, [keys, B]);
    const file = `${outdir}/${kind}_${obj}.glb`, buf = Buffer.from(res.b64, 'base64'); fs.writeFileSync(file, buf);
    scene.objects[obj] = { keys, center: res.center, size: res.size, r: res.r, bytes: buf.length };
    console.log(obj, (buf.length / 1e6).toFixed(2) + ' MB', 'r=' + res.r.toFixed(3));
  }
  fs.writeFileSync(`${outdir}/${kind}_scene.json`, JSON.stringify(scene, null, 1));
  await b.close();
})();
