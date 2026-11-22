/* Rendering stage: scene, lights, camera, labels, timelines. Global THREE + MOTORS. */
(function () {
  const T = THREE; const S = {}; window.STAGE = S;
  const ease = t => t < 0 ? 0 : t > 1 ? 1 : t * t * (3 - 2 * t);
  const easeIO = t => t < 0 ? 0 : t > 1 ? 1 : (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const lerp = (a, b, t) => a + (b - a) * t;
  const lerpV = (a, b, t) => new T.Vector3(lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t));
  S.ease = ease; S.easeIO = easeIO;

  S.init = function (opts) {
    const W = opts.w || 1920, H = opts.h || 1080; S.W = W; S.H = H; S.opts = opts;
    const root = document.getElementById('root'); root.style.width = W + 'px'; root.style.height = H + 'px';
    if (opts.transparent) { root.style.background = 'transparent'; document.body.style.background = 'transparent'; document.documentElement.style.background = 'transparent'; opts.grid = false; }
    const r = new T.WebGLRenderer({ antialias: opts.aa !== false, alpha: true, preserveDrawingBuffer: true });
    r.setPixelRatio(opts.pr || 1); r.setSize(W, H); r.outputEncoding = T.sRGBEncoding; r.toneMapping = T.ACESFilmicToneMapping; r.toneMappingExposure = opts.exposure || 1.05;
    r.shadowMap.enabled = true; r.shadowMap.type = T.PCFSoftShadowMap; r.localClippingEnabled = true; r.physicallyCorrectLights = true;
    root.appendChild(r.domElement); S.renderer = r;
    const scene = new T.Scene(); S.scene = scene;
    const pm = new T.PMREMGenerator(r); scene.environment = pm.fromScene(new T.RoomEnvironment(), 0.04).texture;
    const cam = new T.PerspectiveCamera(opts.fov || 26, W / H, 0.05, 100); S.camera = cam;
    // key light with shadows
    const key = new T.DirectionalLight(0xfff4e6, 2.6); key.position.set(-3, 6, 4); key.castShadow = true;
    key.shadow.mapSize.set(opts.shadow || 2048, opts.shadow || 2048); const sc = key.shadow.camera; sc.left = -4; sc.right = 4; sc.top = 4; sc.bottom = -4; sc.near = 0.5; sc.far = 20; key.shadow.bias = -0.0004; key.shadow.normalBias = 0.01; key.shadow.radius = 4;
    scene.add(key); S.key = key;
    const rim = new T.DirectionalLight(0x5fb4ff, 1.6); rim.position.set(4, 2.5, -5); scene.add(rim);
    const fill = new T.HemisphereLight(0xbcd6ff, 0x0a0f18, 0.35); scene.add(fill);
    // floor shadow catcher + faint grid
    const floorY = opts.floorY !== undefined ? opts.floorY : -0.565;
    const fl = new T.Mesh(new T.PlaneGeometry(40, 40), new T.ShadowMaterial({ opacity: 0.55 })); fl.rotation.x = -Math.PI / 2; fl.position.y = floorY; fl.receiveShadow = true; scene.add(fl); S.floor = fl;
    if (opts.grid !== false) {
      const grid = new T.GridHelper(24, 96, 0x2b6ca3, 0x16324d); grid.position.y = floorY + 0.001;
      grid.material.transparent = true; grid.material.opacity = 0.35; grid.material.depthWrite = false; scene.add(grid); S.grid = grid;
    }
    // model
    S.model = null;
    if (opts.model === 'induction') S.model = MOTORS.buildInduction();
    if (opts.model === 'sync') S.model = MOTORS.buildSynchronous();
    if (S.model) scene.add(S.model.group);
    const envI = opts.env || 0.5;
    scene.traverse(o => { if (o.material && o.material.isMeshStandardMaterial) { o.material.envMapIntensity = o.material.metalness > 0.8 ? envI * 1.6 : envI; } });
    if (opts.model === 'cyl') { S.obj = MOTORS.buildCylindricalRotor(); scene.add(S.obj); }
    if (opts.model === 'salient') { S.obj = MOTORS.buildSalientRotor(false); scene.add(S.obj); }
    if (opts.model === 'brushless') { S.obj = MOTORS.buildSalientRotor(true); scene.add(S.obj); }
    S.svg = document.getElementById('ov'); S.svg.setAttribute('width', W); S.svg.setAttribute('height', H); S.svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    S.cap = document.getElementById('cap');
    S.rotorKeys = opts.model === 'sync' ? ['rotorPoles', 'fieldWinding', 'damper', 'shaft'] : ['rotorCore', 'rotorBars', 'endRings', 'shaft'];
    S.spinKeys = opts.model === 'sync' ? S.rotorKeys.concat(['shaftFan', 'sliprings_rot']) : S.rotorKeys.concat(['fan']);
    return true;
  };

  // ---------- part state helpers ----------
  function setPartAlpha(p, a, glow) {
    p.materials().forEach(m => {
      const base = m.userData.baseOpacity ?? 1;
      if (a >= 0.999 && !m.userData.baseTransparent) { m.transparent = false; m.opacity = base; m.depthWrite = true; }
      else { m.transparent = true; m.opacity = base * a; m.depthWrite = a > 0.6; }
      if (m.emissive) { const g = glow || 0; m.emissive.setRGB(0.02 * g, 0.12 * g, 0.24 * g); }
      m.needsUpdate = true;
    });
    p.group.traverse(o => { if (o.isMesh) o.castShadow = a > 0.6; });
  }
  S.setPartAlpha = setPartAlpha;
  function setPhaseColors(part, k) { // k: 0..1 blend copper -> phase colours
    if (!part.phaseMeshes) return; const cols = [new T.Color(0xe0453a), new T.Color(0xf2c230), new T.Color(0x2f8fff)];
    part.phaseMeshes.forEach((o, i) => { const c = new T.Color(0xc46a38).lerp(cols[i], k); o.material.color.copy(c); });
  }
  S.setPhaseColors = setPhaseColors;

  S.applyExplode = function (e, overrides) {
    const M = S.model; if (!M) return;
    M.order.forEach(k => {
      const p = M.parts[k]; const span = 0.55; const t = easeIO((e - p.delay * (1 - span)) / span);
      const ov = overrides && overrides[k]; const f = ov !== undefined ? ov : t;
      p.group.position.copy(p.offset).multiplyScalar(f);
    });
  };
  S.spin = function (angle) { const M = S.model; if (!M) return; S.spinKeys.forEach(k => { if (M.parts[k]) M.parts[k].group.rotation.x = angle; });  };

  S.setCamera = function (pos, target, fov) { S.camera.position.copy(pos); S.camera.lookAt(target); if (fov) { S.camera.fov = fov; S.camera.updateProjectionMatrix(); } S.camTarget = target; };

  S.project = function (v) { const p = v.clone().project(S.camera); return [(p.x + 1) / 2 * S.W, (1 - p.y) / 2 * S.H, p.z]; };
  S.anchorWorld = function (k) { const p = S.model.parts[k]; return p.anchor.clone().add(p.group.position); };

  // ---------- overlay drawing ----------
  const NS = 'http://www.w3.org/2000/svg';
  function el(tag, attrs, parent) { const e = document.createElementNS(NS, tag); for (const a in attrs) e.setAttribute(a, attrs[a]); (parent || S.svg).appendChild(e); return e; }
  S.clearOverlay = function () { while (S.svg.firstChild) S.svg.removeChild(S.svg.firstChild); S.cap.style.opacity = 0; };
  S.tag = function (k, num, text, alpha, dir) {
    const [x, y] = S.project(S.anchorWorld(k)); const [dx, dy] = dir || [0, -90];
    const g = el('g', { opacity: alpha });
    const abs = dir && dir[2]==='abs'; const lx = abs ? dx : x + dx, ly = abs ? dy : y + dy;
    el('circle', { cx: x, cy: y, r: 6, fill: '#38b6ff', stroke: '#0b1626', 'stroke-width': 2 }, g);
    el('polyline', { points: `${x},${y} ${lx},${abs ? (ly + (y > ly ? 22 : -22)) : ly}`, stroke: '#9fd8ff', 'stroke-width': 2, fill: 'none' }, g);
    const t = el('text', { x: 0, y: 0, 'font-family': 'Inter', 'font-weight': 600, 'font-size': 25, fill: '#ffffff' }, g); t.textContent = text;
    const w = t.getComputedTextLength() + 62; const bx = abs ? lx - w / 2 : (dx < 0 ? lx - w : (dx > 0 ? lx : lx - w / 2)); const by = ly - 22;
    const rect = el('rect', { x: bx, y: by, width: w, height: 44, rx: 8, fill: 'rgba(9,20,36,0.86)', stroke: 'rgba(56,182,255,0.75)', 'stroke-width': 1.5 }, g);
    g.insertBefore(rect, t);
    const c = el('circle', { cx: bx + 22, cy: ly, r: 14, fill: '#38b6ff' }, g); const n = el('text', { x: bx + 22, y: ly + 7, 'text-anchor': 'middle', 'font-family': 'Inter', 'font-weight': 700, 'font-size': 18, fill: '#071220' }, g); n.textContent = num;
    t.setAttribute('x', bx + 44); t.setAttribute('y', ly + 9);
  };
  S.caption = function (num, total, title, desc, chip, alpha) {
    const c = S.cap; c.style.opacity = alpha;
    c.innerHTML = `<div class="n">${String(num).padStart(2, '0')}<span>/ ${String(total).padStart(2, '0')}</span></div><div class="t">${title}</div><div class="d">${desc}</div>` + (chip ? `<div class="chip ${chip.toLowerCase()}">${chip}</div>` : '');
  };
  S.title = function (txt, sub, alpha) { const h = document.getElementById('hd'); h.style.opacity = alpha; h.innerHTML = `<div class="k">${sub || ''}</div><div class="h">${txt}</div>`; };

  S.render = function () { S.renderer.render(S.scene, S.camera); };
})();
(function(){ const T=THREE, S=STAGE;
  S.cutaway = function(keys, on){ // remove front-top quadrant (y>0,z>0) of listed parts
    const planes = on ? [new T.Plane(new T.Vector3(0,-1,0),0), new T.Plane(new T.Vector3(0,0,-1),0)] : [];
    keys.forEach(k=>{ const p=S.model.parts[k]; if(!p) return; p.materials().forEach(m=>{ m.clippingPlanes=planes; m.clipIntersection=true; m.clipShadows=true; m.needsUpdate=true; }); });
  };
})();
