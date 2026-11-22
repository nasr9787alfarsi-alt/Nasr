// Render each display object alone, through the same camera the PowerPoint 3D model uses:
// view direction D0 turned by `yaw` about the camera's up axis, FOV_DEG field of view, distance r / sin(fov/2)
// so the object's bounding sphere exactly fills a square image. Transparent background, no floor.
// usage: node partimg.js <native_dir> [kind]
const { chromium } = require('playwright');
const fs = require('fs');
const { D0, FOV_DEG, basis } = require('./native_cfg.js');

(async () => {
  const [nd, only] = process.argv.slice(2);
  const jobs = JSON.parse(fs.readFileSync(nd + '/jobs.json')).filter(j => !only || j.kind === only);
  fs.mkdirSync(nd + '/img', { recursive: true });
  const B = basis(D0);
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pages = {};
  for (const j of jobs) {
    const out = `${nd}/img/${j.out}`;
    if (fs.existsSync(out)) continue;
    const t0 = Date.now();
    const p = await b.newPage({ viewport: { width: j.px, height: j.px } });
    p.on('pageerror', e => console.log('PAGEERR', e.message));
    await p.goto('file://' + __dirname + '/stage.html');
    await p.evaluate(([j, B, D0, fov]) => {
      window.NO_BUMP = true;
      STAGE.init({ model: j.kind, light: true, transparent: true, w: j.px, h: j.px, shadow: 2048, fov });
      const S = STAGE, T = THREE, M = S.model;
      M.order.forEach(k => { const P = M.parts[k]; P.group.position.set(0, 0, 0); P.group.visible = j.keys.includes(k); });
      M.group.updateMatrixWorld(true); S.floor.visible = false;
      const up = new T.Vector3(...B.y), c = new T.Vector3(...j.center);
      const dir = new T.Vector3(...D0).normalize().applyAxisAngle(up, -j.yaw * Math.PI / 180);
      const d = j.r / Math.sin(fov * Math.PI / 360);
      S.camera.up.copy(up); S.setCamera(c.clone().add(dir.multiplyScalar(d)), c); S.camera.updateMatrixWorld();
      // key light follows the camera turn so every part is lit the same way on every slide
      S.key.position.set(-3, 6, 4).applyAxisAngle(up, -j.yaw * Math.PI / 180).add(c); S.key.target.position.copy(c); S.key.target.updateMatrixWorld();
      S.render();
    }, [j, B, D0, FOV_DEG]);
    await p.locator('#root').screenshot({ path: out, omitBackground: true, timeout: 600000 });
    await p.close();
    console.log(j.out, j.px + 'px', ((Date.now() - t0) / 1000).toFixed(0) + 's');
  }
  await b.close();
})();
