(function () {
  const T = THREE;
  const TOURS = __TOURS__;
  const $ = s => document.querySelector(s);
  const view = $('#view');
  const renderer = new T.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputEncoding = T.sRGBEncoding; renderer.toneMapping = T.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = T.PCFSoftShadowMap; renderer.localClippingEnabled = true; renderer.physicallyCorrectLights = true;
  view.appendChild(renderer.domElement);
  const scene = new T.Scene();
  scene.environment = new T.PMREMGenerator(renderer).fromScene(new T.RoomEnvironment(), 0.04).texture;
  const camera = new T.PerspectiveCamera(30, 1, 0.05, 100);
  const key = new T.DirectionalLight(0xfff4e6, 2.6); key.position.set(-3, 6, 4); key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -4, right: 4, top: 4, bottom: -4, near: 0.5, far: 20 }); key.shadow.bias = -0.0004; key.shadow.normalBias = 0.01; scene.add(key);
  const rim = new T.DirectionalLight(0x5fb4ff, 1.6); rim.position.set(4, 2.5, -5); scene.add(rim);
  scene.add(new T.HemisphereLight(0xbcd6ff, 0x0a0f18, 0.35));
  const floor = new T.Mesh(new T.PlaneGeometry(40, 40), new T.ShadowMaterial({ opacity: 0.5 })); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
  const grid = new T.GridHelper(24, 96, 0x2b6ca3, 0x16324d); grid.material.transparent = true; grid.material.opacity = 0.3; grid.material.depthWrite = false; scene.add(grid);
  const controls = new T.OrbitControls(camera, renderer.domElement); controls.enableDamping = true; controls.dampingFactor = 0.08; controls.minDistance = 0.8; controls.maxDistance = 14; controls.maxPolarAngle = Math.PI * 0.49;

  const models = {}; let kind = 'induction', M = null, explode = 0, explodeTarget = 0, cut = false, spinning = true, angle = 0, selected = -1, focusT = null;
  const CFG = {
    induction: { floorY: -0.565, cam: [-2.9, 1.4, 3.4], tgt: [0, 0, 0], camE: [-1.9, 2.4, 7.0], tgtE: [-0.25, 0.25, 0], rotor: ['rotorCore', 'rotorBars', 'endRings', 'shaft'], spin: ['rotorCore', 'rotorBars', 'endRings', 'shaft', 'fan'], cut: ['frame', 'statorCore', 'statorWinding', 'endShieldDE', 'endShieldNDE', 'fanCover', 'bearingDE', 'bearingNDE'] },
    sync: { floorY: -0.625, cam: [-3.5, 1.8, 4.1], tgt: [0, 0.12, 0], camE: [-1.9, 3.2, 9.4], tgtE: [-0.1, 0.8, 0], rotor: ['rotorPoles', 'fieldWinding', 'damper', 'shaft', 'shaftFan'], spin: ['rotorPoles', 'fieldWinding', 'damper', 'shaft', 'shaftFan'], cut: ['frame', 'cooling', 'statorCore', 'statorWinding', 'endShieldDE', 'endShieldNDE', 'bearingDE', 'bearingNDE'] },
  };
  function build(k) {
    if (models[k]) return models[k];
    const m = k === 'induction' ? MOTORS.buildInduction() : MOTORS.buildSynchronous();
    m.group.traverse(o => { if (o.material && o.material.isMeshStandardMaterial) o.material.envMapIntensity = o.material.metalness > 0.8 ? 0.8 : 0.5; });
    return (models[k] = m);
  }
  function setAlpha(p, a, glow) {
    p.materials().forEach(m => {
      const base = m.userData.baseOpacity ?? 1;
      if (a >= 0.999 && !m.userData.baseTransparent) { m.transparent = false; m.opacity = base; m.depthWrite = true; }
      else { m.transparent = true; m.opacity = base * a; m.depthWrite = a > 0.6; }
      if (m.emissive) m.emissive.setRGB(0.02 * glow, 0.12 * glow, 0.24 * glow);
    });
    p.group.visible = a > 0.01;
    p.group.traverse(o => { if (o.isMesh) o.castShadow = a > 0.6; });
  }
  function setPhase(on) {
    const p = M.parts.statorWinding; if (!p.phaseMeshes) return; const cols = [0xe0453a, 0xf2c230, 0x2f8fff];
    p.phaseMeshes.forEach((o, i) => o.material.color.set(on ? cols[i] : 0xc46a38));
  }
  function applyCut() {
    const planes = cut ? [new T.Plane(new T.Vector3(0, -1, 0), 0), new T.Plane(new T.Vector3(0, 0, -1), 0)] : [];
    M.order.forEach(k => M.parts[k].materials().forEach(m => { m.clippingPlanes = CFG[kind].cut.includes(k) ? planes : []; m.clipIntersection = true; m.clipShadows = true; m.needsUpdate = true; }));
  }
  function applyAlphas() {
    const st = selected >= 0 ? TOURS[kind].steps[selected] : null;
    M.order.forEach(k => {
      const p = M.parts[k]; let a = p.hiddenUntilFocus ? 0 : 1, g = 0;
      if (st) { a = p.hiddenUntilFocus ? 0 : 0.1; if ((st.also || []).includes(k)) a = st.alsoA || 0.9; if ((st.ghost || []).includes(k)) a = 0.08; if (st.keys.includes(k)) { a = 1; g = 0.25; } }
      setAlpha(p, a, g);
    });
    if (M.parts.airGap) M.parts.airGap.materials().forEach(m => { m.opacity = st && st.keys.includes('airGap') ? 0.85 : 0; });
    setPhase(!!(st && st.phase));
  }
  function load(k) {
    if (M) scene.remove(M.group);
    kind = k; M = build(k); scene.add(M.group);
    floor.position.y = CFG[k].floorY; grid.position.y = CFG[k].floorY + 0.001;
    selected = -1; applyCut(); applyAlphas(); renderList(); showInfo(); resetView(false);
    document.querySelectorAll('.seg button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.k === k)));
  }
  function resetView(anim) {
    const c = CFG[kind], e = explodeTarget > 0.5;
    focusT = { pos: new T.Vector3(...(e ? c.camE : c.cam)), tgt: new T.Vector3(...(e ? c.tgtE : c.tgt)) };
    if (!anim) { camera.position.copy(focusT.pos); controls.target.copy(focusT.tgt); focusT = null; }
  }
  function applyExplode(e) {
    const st = selected >= 0 ? TOURS[kind].steps[selected] : null; const asm = st && st.assemble;
    M.order.forEach(k => { const p = M.parts[k]; const span = 0.55; let t = (e - p.delay * (1 - span)) / span; t = Math.max(0, Math.min(1, t)); t = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
      if (asm && CFG[kind].rotor.includes(k)) t = 0; p.group.position.copy(p.offset).multiplyScalar(t); });
  }
  // --- UI ---
  function renderList() {
    const ul = $('#parts'); ul.innerHTML = '';
    TOURS[kind].steps.forEach((st, i) => {
      const li = document.createElement('li'); const b = document.createElement('button'); b.type = 'button'; b.id = 'part-' + i;
      b.innerHTML = `<span class="n">${String(st.n).padStart(2, '0')}</span><span class="t">${st.t}</span>${st.chip ? `<span class="chip ${st.chip.toLowerCase()}">${st.chip === 'STATIONARY' ? 'fixed' : 'turns'}</span>` : ''}`;
      b.addEventListener('click', () => select(selected === i ? -1 : i)); li.appendChild(b); ul.appendChild(li);
    });
  }
  function showInfo() {
    const st = selected >= 0 ? TOURS[kind].steps[selected] : null;
    $('#info-k').textContent = st ? `Component ${String(st.n).padStart(2, '0')} of ${TOURS[kind].steps.length}` : (kind === 'induction' ? 'Squirrel-cage induction motor' : 'Salient-pole synchronous motor');
    $('#info-t').textContent = st ? st.t : (kind === 'induction' ? 'Induction motor' : 'Synchronous motor');
    $('#info-d').textContent = st ? st.d : (kind === 'induction' ? 'A totally enclosed, fan-cooled motor like the ones on most pumps and fans. Drag to rotate, scroll or pinch to zoom, and pick a component to inspect it.' : 'A large industrial synchronous motor with DC excitation through slip rings and a top-mounted cooler. Drag to rotate, scroll or pinch to zoom, and pick a component to inspect it.');
    document.querySelectorAll('#parts button').forEach((b, i) => b.setAttribute('aria-pressed', String(i === selected)));
  }
  function select(i) {
    selected = i; const st = i >= 0 ? TOURS[kind].steps[i] : null;
    if (st && explodeTarget < 0.5 && !st.assemble) { explodeTarget = 1; $('#explode').value = 100; }
    applyAlphas(); showInfo();
    if (st) {
      // aim at the selected parts
      applyExplode(explodeTarget); const box = new T.Box3();
      st.keys.forEach(k => { const p = M.parts[k]; p.group.visible = true; box.expandByObject(p.group); });
      const c = box.getCenter(new T.Vector3()), sz = box.getSize(new T.Vector3()).length();
      const dir = camera.position.clone().sub(controls.target).normalize();
      focusT = { tgt: c, pos: c.clone().add(dir.multiplyScalar(Math.max(1.6, sz * 1.6))) };
    } else resetView(true);
  }
  $('#explode').addEventListener('input', e => { explodeTarget = e.target.value / 100; });
  $('#cut').addEventListener('change', e => { cut = e.target.checked; applyCut(); });
  $('#spin').addEventListener('change', e => { spinning = e.target.checked; });
  $('#reset').addEventListener('click', () => { select(-1); explodeTarget = 0; $('#explode').value = 0; resetView(true); });
  document.querySelectorAll('.seg button').forEach(b => b.addEventListener('click', () => { explodeTarget = 0; explode = 0; $('#explode').value = 0; load(b.dataset.k); }));
  // picking
  const ray = new T.Raycaster(), ptr = new T.Vector2(); let down = null;
  function partAt(ev) {
    const r = renderer.domElement.getBoundingClientRect(); ptr.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(ptr, camera); const hits = ray.intersectObjects(M.group.children, true);
    for (const h of hits) { if (!h.object.visible || (h.object.material && h.object.material.opacity < 0.3)) continue; let o = h.object; while (o && !M.parts[o.name]) o = o.parent; if (o) return o.name; }
    return null;
  }
  renderer.domElement.addEventListener('pointerdown', e => { down = [e.clientX, e.clientY]; });
  renderer.domElement.addEventListener('pointerup', e => {
    if (!down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 5) return; const k = partAt(e); if (!k) return;
    const steps = TOURS[kind].steps; let i = steps.findIndex(s => s.keys.length === 1 && s.keys[0] === k); if (i < 0) i = steps.findIndex(s => s.keys.includes(k)); if (i >= 0) select(i);
  });
  const tip = $('#tip'); let last = 0;
  renderer.domElement.addEventListener('pointermove', e => {
    if (e.buttons || performance.now() - last < 60) return; last = performance.now(); const k = partAt(e);
    if (k) { const steps = TOURS[kind].steps; const st = steps.find(s => s.keys.length === 1 && s.keys[0] === k) || steps.find(s => s.keys.includes(k)); tip.textContent = st ? st.t : M.parts[k].label; tip.hidden = false; const r = view.getBoundingClientRect(); tip.style.left = (e.clientX - r.left + 14) + 'px'; tip.style.top = (e.clientY - r.top + 14) + 'px'; renderer.domElement.style.cursor = 'pointer'; }
    else { tip.hidden = true; renderer.domElement.style.cursor = ''; }
  });
  renderer.domElement.addEventListener('pointerleave', () => { tip.hidden = true; });
  function resize() { const w = view.clientWidth, h = view.clientHeight; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
  new ResizeObserver(resize).observe(view);
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let prev = performance.now();
  function tick(now) {
    const dt = Math.min(0.05, (now - prev) / 1000); prev = now;
    explode += (explodeTarget - explode) * Math.min(1, dt * 4); applyExplode(explode);
    if (spinning && !reduce) angle += dt * 1.6; CFG[kind].spin.forEach(k => { if (M.parts[k]) M.parts[k].group.rotation.x = angle; });
    if (focusT) { camera.position.lerp(focusT.pos, Math.min(1, dt * 3)); controls.target.lerp(focusT.tgt, Math.min(1, dt * 3)); if (camera.position.distanceTo(focusT.pos) < 0.01) focusT = null; }
    controls.update(); renderer.render(scene, camera); requestAnimationFrame(tick);
  }
  renderer.domElement.addEventListener('pointerdown', () => { focusT = null; });
  renderer.domElement.addEventListener('wheel', () => { focusT = null; }, { passive: true });
  resize(); load('induction'); requestAnimationFrame(tick);
})();
