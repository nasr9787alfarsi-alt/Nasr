/* Procedural industrial motor models (three.js r128, global THREE).
   Shaft axis = X. Drive end (DE) = -X, non-drive end (NDE) = +X.
   Each model returns { group, parts:{key:Part}, order:[keys] }.            */
(function () {
  const T = THREE;
  const D = Math.PI / 180;

  // ---------- materials ----------
  function std(o) { const m = new T.MeshStandardMaterial(Object.assign({ side: T.DoubleSide }, o)); return m; }
  function phys(o) { if (window.NO_PHYS) { delete o.clearcoat; delete o.clearcoatRoughness; return std(o); } const m = new T.MeshPhysicalMaterial(Object.assign({ side: T.DoubleSide }, o)); return m; }
  let _noise = null;
  function castNoise() { // fine cast-iron / paint orange-peel texture
    if (_noise) return _noise; const c = document.createElement('canvas'); c.width = c.height = 512; const g = c.getContext('2d');
    const id = g.createImageData(512, 512); let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    for (let i = 0; i < id.data.length; i += 4) { const v = 118 + rnd() * 30; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
    g.putImageData(id, 0, 0); g.globalAlpha = 0.5; g.filter = 'blur(1.2px)'; g.drawImage(c, 0, 0);
    const t = new T.CanvasTexture(c); t.wrapS = t.wrapT = T.RepeatWrapping; t.repeat.set(6, 6); _noise = t; return t;
  }
  const paintM = (color, cc) => { const m = phys({ color, metalness: 0.25, roughness: 0.48, clearcoat: cc, clearcoatRoughness: 0.45 }); if (!window.NO_BUMP) { m.bumpMap = castNoise(); m.bumpScale = 0.0018; m.roughnessMap = castNoise(); } return m; };
  const MAT = {
    paintBlue: () => paintM(0x2b4a66, 0.35),
    paintGraphite: () => paintM(0x59626a, 0.3),
    paintLight: () => paintM(0x3f474e, 0.25),
    steel: () => std({ color: 0xc3c9d0, metalness: 1.0, roughness: 0.28 }),
    darkSteel: () => std({ color: 0x6b7178, metalness: 0.9, roughness: 0.42 }),
    lamination: () => std({ color: 0x8a9098, metalness: 0.92, roughness: 0.34 }),
    copper: () => phys({ color: 0xc46a38, metalness: 1.0, roughness: 0.3, clearcoat: 0.6, clearcoatRoughness: 0.2 }),
    copperDark: () => phys({ color: 0x9a4a25, metalness: 1.0, roughness: 0.34, clearcoat: 0.7, clearcoatRoughness: 0.2 }),
    aluminium: () => std({ color: 0xd6dadf, metalness: 1.0, roughness: 0.34 }),
    castAl: () => std({ color: 0xb9bec4, metalness: 0.95, roughness: 0.5 }),
    bronze: () => std({ color: 0xc89b55, metalness: 1.0, roughness: 0.25 }),
    polymer: () => std({ color: 0x23282e, metalness: 0.05, roughness: 0.55 }),
    carbon: () => std({ color: 0x1a1b1d, metalness: 0.1, roughness: 0.85 }),
    insulation: () => std({ color: 0xd9c9a0, metalness: 0.0, roughness: 0.7 }),
    brass: () => std({ color: 0xd4b05a, metalness: 1.0, roughness: 0.3 }),
    cable: () => std({ color: 0x15171a, metalness: 0.0, roughness: 0.6 }),
    glow: () => new T.MeshBasicMaterial({ color: 0x6fd0ff, transparent: true, opacity: 0.75, side: T.DoubleSide, depthWrite: false }),
  };

  // ---------- geometry helpers ----------
  function lathe(pts, seg) { // pts: [[r,x],...]
    const g = new T.LatheGeometry(pts.map(p => new T.Vector2(p[0], p[1])), seg || 96);
    g.rotateZ(-Math.PI / 2); return g;
  }
  function tubeRing(rIn, rOut, x0, x1, seg) { // hollow cylinder along x
    return lathe([[rIn, x0], [rOut, x0], [rOut, x1], [rIn, x1], [rIn, x0]], seg);
  }
  function extrudeX(shape, depth, x0, opts) { // shape in (z?,y) -> along +X
    const g = new T.ExtrudeGeometry(shape, Object.assign({ depth, bevelEnabled: false, curveSegments: 48 }, opts || {}));
    g.rotateY(Math.PI / 2); g.translate(x0, 0, 0); return g;
  }
  function polar(r, a, off) { // radial r at angle a (in y-z plane, a from +y), tangential offset
    const u = [Math.sin(a), Math.cos(a)], v = [Math.cos(a), -Math.sin(a)];
    return new T.Vector2(r * u[0] + (off || 0) * v[0], r * u[1] + (off || 0) * v[1]);
  }
  // NB: extrudeX maps shape.x -> -z, shape.y -> y.  polar() uses (x=sin,y=cos) => angle measured from +y.
  function circlePath(r, n, holeDir) {
    const p = new T.Path(); const N = n || 128;
    for (let i = 0; i <= N; i++) { const a = (holeDir ? -1 : 1) * i / N * Math.PI * 2; const v = polar(r, a); i ? p.lineTo(v.x, v.y) : p.moveTo(v.x, v.y); }
    return p;
  }
  function mesh(g, m, cast = true, recv = true) { const o = new T.Mesh(g, m); o.castShadow = cast; o.receiveShadow = recv; return o; }
  function merge(geos) { return T.BufferGeometryUtils.mergeBufferGeometries(geos.map(g => g.index ? g.toNonIndexed() : g)); }
  function boxAt(sx, sy, sz, x, y, z) { const g = new T.BoxGeometry(sx, sy, sz); g.translate(x, y, z); return g; }
  function cylX(r, len, x, y, z, seg) { const g = new T.CylinderGeometry(r, r, len, seg || 24); g.rotateZ(Math.PI / 2); g.translate(x, y, z); return g; }
  function cylY(r, len, x, y, z, seg) { const g = new T.CylinderGeometry(r, r, len, seg || 24); g.translate(x, y, z); return g; }
  function cylZ(r, len, x, y, z, seg) { const g = new T.CylinderGeometry(r, r, len, seg || 24); g.rotateX(Math.PI / 2); g.translate(x, y, z); return g; }
  function rotX(g, a) { g.rotateX(a); return g; }
  function roundedRectShape(w, h, r, cx, cy) {
    const s = new T.Shape(); const x = cx - w / 2, y = cy - h / 2;
    s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r);
    s.lineTo(x + w, y + h - r); s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r); s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y); return s;
  }
  function roundedRectPath(w, h, r, cx, cy) {
    const s = new T.Path(); const x = cx - w / 2, y = cy - h / 2;
    s.moveTo(x + r, y); s.quadraticCurveTo(x, y, x, y + r); s.lineTo(x, y + h - r); s.quadraticCurveTo(x, y + h, x + r, y + h);
    s.lineTo(x + w - r, y + h); s.quadraticCurveTo(x + w, y + h, x + w, y + h - r); s.lineTo(x + w, y + r); s.quadraticCurveTo(x + w, y, x + w - r, y); s.lineTo(x + r, y); return s;
  }

  // nameplate texture
  function nameplateTex(lines) {
    const c = document.createElement('canvas'); c.width = 512; c.height = 300; const g = c.getContext('2d');
    g.fillStyle = '#c9cdd2'; g.fillRect(0, 0, 512, 300); g.strokeStyle = '#555'; g.lineWidth = 6; g.strokeRect(8, 8, 496, 284);
    g.fillStyle = '#20252b'; g.font = 'bold 34px Inter, Arial'; g.fillText(lines[0], 30, 58);
    g.font = '24px Inter, Arial'; for (let i = 1; i < lines.length; i++) g.fillText(lines[i], 30, 58 + i * 46);
    for (let i = 0; i < 4; i++) { g.beginPath(); g.arc(i % 2 ? 490 : 22, i < 2 ? 22 : 278, 7, 0, 7); g.fillStyle = '#777'; g.fill(); }
    const t = new T.CanvasTexture(c); t.encoding = T.sRGBEncoding; t.anisotropy = 8; return t;
  }

  // ---------- part container ----------
  function Part(key, label, desc, opts) {
    this.key = key; this.label = label; this.desc = desc; this.group = new T.Group(); this.group.name = key;
    this.offset = (opts && opts.offset) || new T.Vector3(); this.delay = (opts && opts.delay) || 0;
    this.anchor = (opts && opts.anchor) || new T.Vector3(); this.hiddenUntilFocus = !!(opts && opts.hidden);
    this.labelSide = (opts && opts.side) || 'up'; this.num = (opts && opts.num) || 0;
  }
  Part.prototype.add = function (o) { this.group.add(o); return o; };
  Part.prototype.materials = function () {
    const ms = new Set(); this.group.traverse(o => { if (o.material) (Array.isArray(o.material) ? o.material : [o.material]).forEach(m => ms.add(m)); }); return [...ms];
  };

  function finish(parts, order) {
    const group = new T.Group();
    order.forEach(k => { const p = parts[k]; group.add(p.group); if (p.hiddenUntilFocus) p.group.visible = false;
      p.materials().forEach(m => { m.userData.baseOpacity = m.opacity; m.userData.baseTransparent = m.transparent; m.userData.baseEmissive = m.emissive ? m.emissive.clone() : null; });
    });
    return { group, parts, order };
  }

  // ---------- shared sub-builders ----------
  function statorCore(part, rO, rB, len, nSlots, slotDepth, slotW, nPlates) {
    const shape = new T.Shape(); const N = 160;
    for (let i = 0; i <= N; i++) { const v = polar(rO, i / N * Math.PI * 2); i ? shape.lineTo(v.x, v.y) : shape.moveTo(v.x, v.y); }
    const hole = new T.Path(); const pts = []; const ao = 0.006, lip = 0.012;
    for (let k = 0; k < nSlots; k++) {
      const a = k / nSlots * Math.PI * 2, a2 = (k + 1) / nSlots * Math.PI * 2;
      pts.push(polar(rB, a, -ao), polar(rB + lip, a, -ao), polar(rB + lip + 0.004, a, -slotW / 2), polar(rB + slotDepth, a, -slotW / 2),
        polar(rB + slotDepth + slotW / 2, a, 0), polar(rB + slotDepth, a, slotW / 2), polar(rB + lip + 0.004, a, slotW / 2), polar(rB + lip, a, ao), polar(rB, a, ao));
      for (let j = 1; j < 6; j++) pts.push(polar(rB, a + (a2 - a) * j / 6));
    }
    pts.forEach((p, i) => i ? hole.lineTo(p.x, p.y) : hole.moveTo(p.x, p.y)); hole.closePath();
    shape.holes.push(hole);
    const pitch = len / nPlates, th = pitch * 0.9;
    const g = extrudeX(shape, th, 0);
    const m = MAT.lamination(); const inst = new T.InstancedMesh(g, m, nPlates); inst.castShadow = inst.receiveShadow = true;
    const mx = new T.Matrix4(); for (let i = 0; i < nPlates; i++) { mx.makeTranslation(-len / 2 + i * pitch, 0, 0); inst.setMatrixAt(i, mx); }
    part.add(inst);
    // a few key bars / weld seams on the outside
    const seams = []; for (let k = 0; k < 6; k++) { const a = (k / 6 + 1 / 12) * Math.PI * 2; const p = polar(rO - 0.004, a); seams.push(boxAt(len, 0.012, 0.012, 0, p.y, -p.x)); }
    part.add(mesh(merge(seams), MAT.darkSteel()));
  }

  function statorWinding(part, rB, len, nSlots, slotDepth, slotW, span, tubeR, phaseColors) {
    const copper = MAT.copper();
    const slotGeos = [], ends = [[], [], []];
    const rMid = rB + 0.016 + (slotDepth - 0.016) / 2;
    for (let k = 0; k < nSlots; k++) {
      const a = k / nSlots * Math.PI * 2; const p = polar(rMid, a);
      const g = new T.BoxGeometry(len + 0.04, slotDepth - 0.022, slotW * 0.82); g.rotateX(-a); g.translate(0, p.y, -p.x); slotGeos.push(g);
      // wedge (insulation strip at slot mouth)
    }
    part.add(mesh(merge(slotGeos), copper));
    for (const side of [-1, 1]) {
      for (let k = 0; k < nSlots; k++) {
        const a1 = k / nSlots * Math.PI * 2, a2 = (k + span) / nSlots * Math.PI * 2; const ph = Math.floor(k / (nSlots / (3 * 4))) % 3;
        const layer = (k % 2) * 0.014; const pts = [];
        const x0 = side * (len / 2 + 0.01), reach = 0.035 + span * 0.0045;
        const r0 = rMid + layer;
        const S = 14; for (let i = 0; i <= S; i++) {
          const t = i / S; const a = a1 + (a2 - a1) * t; const bulge = Math.sin(Math.PI * t);
          const x = x0 + side * (0.015 + reach * Math.pow(bulge, 0.6)); const r = r0 + 0.022 * bulge + layer;
          const p = polar(r, a); pts.push(new T.Vector3(x, p.y, -p.x));
        }
        pts.unshift(new T.Vector3(x0 - side * 0.02, pts[0].y, pts[0].z)); const lp = pts[pts.length - 1]; pts.push(new T.Vector3(x0 - side * 0.02, lp.y, lp.z));
        const curve = new T.CatmullRomCurve3(pts); ends[ph].push(new T.TubeGeometry(curve, 36, tubeR, 7, false));
      }
    }
    const phaseMeshes = ends.map((gs, i) => { const m = phaseColors ? MAT.copper() : copper; const o = mesh(merge(gs), m); o.userData.phase = i; return o; });
    phaseMeshes.forEach(o => part.add(o));
    // lacing cords
    const lace = MAT.insulation(); const lg = [];
    for (const side of [-1, 1]) { const t = new T.TorusGeometry(rMid + 0.05, 0.006, 6, 120); t.rotateY(Math.PI / 2); t.translate(side * (len / 2 + 0.06), 0, 0); lg.push(t); }
    part.add(mesh(merge(lg), lace));
    part.phaseMeshes = phaseMeshes;
  }

  function bearing(part, x, rIn, rOut, w) {
    const st = MAT.steel();
    const ringT = (rOut - rIn) * 0.32;
    part.add(mesh(tubeRing(rOut - ringT, rOut, x - w / 2, x + w / 2), st));
    part.add(mesh(tubeRing(rIn, rIn + ringT, x - w / 2, x + w / 2), st));
    const rb = (rOut - rIn) * 0.2, rc = (rIn + rOut) / 2; const n = 11; const balls = [];
    for (let i = 0; i < n; i++) { const g = new T.SphereGeometry(rb, 16, 12); const p = polar(rc, i / n * Math.PI * 2); g.translate(x, p.y, -p.x); balls.push(g); }
    part.add(mesh(merge(balls), MAT.steel()));
    // seal shields
    part.add(mesh(tubeRing(rIn + ringT, rOut - ringT, x + w / 2 - 0.003, x + w / 2 - 0.001), MAT.polymer()));
  }

  function sleeveBearing(part, x, rIn, rOut, w) { // split babbitt-lined sleeve bearing shells
    const babbitt = std({ color: 0xd9dde0, metalness: 1, roughness: 0.22 }), steelM = MAT.steel();
    for (const half of [0, 1]) {
      const g = new T.CylinderGeometry(rOut, rOut, w, 48, 1, true, half * Math.PI + 0.03, Math.PI - 0.06); g.rotateZ(Math.PI / 2); g.translate(x, 0, 0);
      const gi = new T.CylinderGeometry(rIn, rIn, w, 48, 1, true, half * Math.PI + 0.03, Math.PI - 0.06); gi.rotateZ(Math.PI / 2); gi.translate(x, 0, 0);
      part.add(mesh(g, steelM)); part.add(mesh(gi, babbitt));
    }
    part.add(mesh(merge([tubeRing(rIn, rOut + 0.012, x - w / 2 - 0.01, x - w / 2, 48), tubeRing(rIn, rOut + 0.012, x + w / 2, x + w / 2 + 0.01, 48)]), steelM));
  }
  function shaft(part, profile, keyX0, keyX1, keyR) {
    part.add(mesh(lathe(profile, 64), MAT.steel()));
    if (keyX0 !== undefined) part.add(mesh(boxAt(keyX1 - keyX0, 0.012, keyR * 0.55, (keyX0 + keyX1) / 2, keyR - 0.004, 0), MAT.darkSteel()));
  }

  // ======================================================================
  //  INDUCTION MOTOR  (TEFC squirrel-cage)
  // ======================================================================
  function buildInduction() {
    const P = {}; const V = (x, y, z) => new T.Vector3(x, y, z);
    const L = 0.70, rO = 0.40, rB = 0.235, rR = 0.2312;

    P.frame = new Part('frame', 'Frame / Housing', 'Strong cast-iron body. Holds everything in place, protects the inside and its fins carry heat away.', { offset: V(0, 1.05, 0), anchor: V(0.15, 0.50, 0.25), delay: 0.0, side: 'up' });
    P.statorCore = new Part('statorCore', 'Stator Core', 'Stack of thin steel sheets (laminations). Guides the magnetic field and keeps energy losses low.', { anchor: V(-0.2, 0.30, 0.28), delay: 0.25 });
    P.statorWinding = new Part('statorWinding', 'Stator Windings', 'Insulated copper coils in the slots. Three-phase AC current here creates the rotating magnetic field.', { anchor: V(0.42, 0.24, 0.18), delay: 0.25 });
    P.stator = new Part('stator', 'Stator', 'The part that never moves: core + windings fixed inside the frame.', { anchor: V(0, 0.42, 0.2), hidden: true });
    P.rotorCore = new Part('rotorCore', 'Rotor Core', 'Laminated steel cylinder fixed to the shaft. Carries the magnetic field through the rotor.', { offset: V(-1.3, 0, 0), anchor: V(-0.1, 0.23, 0.08), delay: 0.45 });
    P.rotorBars = new Part('rotorBars', 'Rotor Bars', 'Aluminium bars cast into the core. The rotating field induces current in them, with no wires connected.', { offset: V(-1.3, 0, 0), anchor: V(0.1, 0.16, 0.16), delay: 0.45 });
    P.endRings = new Part('endRings', 'End Rings', 'Short-circuit every bar at both ends, forming the closed "squirrel cage".', { offset: V(-1.3, 0, 0), anchor: V(0.37, 0.2, 0.1), delay: 0.45 });
    P.shaft = new Part('shaft', 'Shaft', 'Steel shaft that carries the rotor and delivers the turning force (torque) to the machine.', { offset: V(-1.3, 0, 0), anchor: V(-0.72, 0.04, 0), delay: 0.45 });
    P.airGap = new Part('airGap', 'Air Gap', 'Very small gap (often < 1–2 mm) between stator and rotor. The magnetic field crosses it to reach the rotor.', { anchor: V(-0.3, 0.233, 0.0), hidden: true });
    P.bearingDE = new Part('bearingDE', 'Bearings', 'Ball bearings support the shaft and let it spin smoothly with little friction.', { offset: V(-1.62, 0, 0), anchor: V(-0.49, 0.1, 0), delay: 0.6 });
    P.bearingNDE = new Part('bearingNDE', 'Bearings', '', { offset: V(0.42, 0, 0), anchor: V(0.49, 0.1, 0), delay: 0.6 });
    P.endShieldDE = new Part('endShieldDE', 'End Shield (DE)', 'End covers that hold the bearings and centre the rotor exactly inside the stator.', { offset: V(-1.92, 0, 0), anchor: V(-0.5, 0.3, 0.1), delay: 0.65 });
    P.endShieldNDE = new Part('endShieldNDE', 'End Shield (NDE)', '', { offset: V(0.62, 0, 0), anchor: V(0.5, 0.3, 0.1), delay: 0.65 });
    P.fan = new Part('fan', 'Cooling Fan', 'Mounted on the shaft. Blows air over the outside fins to keep the motor cool.', { offset: V(0.95, 0, 0), anchor: V(0.63, 0.33, 0), delay: 0.8 });
    P.fanCover = new Part('fanCover', 'Fan Cover', 'Guards the fan and directs the cooling air along the frame.', { offset: V(1.35, 0, 0), anchor: V(0.76, 0.3, 0), delay: 0.85 });

    // ---- frame ----
    const paint = MAT.paintBlue();
    P.frame.add(mesh(lathe([[rO, -0.43], [0.43, -0.43], [0.43, 0.43], [rO, 0.43], [rO, -0.43]], 128), paint));
    // spigot flanges
    P.frame.add(mesh(lathe([[0.425, -0.43], [0.452, -0.43], [0.452, -0.40], [0.425, -0.40]], 128), paint));
    P.frame.add(mesh(lathe([[0.425, 0.40], [0.452, 0.40], [0.452, 0.43], [0.425, 0.43]], 128), paint));
    const fins = []; const nF = 44;
    for (let i = 0; i < nF; i++) {
      const a = (i + 0.5) / nF * Math.PI * 2; const ad = ((a / D) + 360) % 360;
      if (ad > 332 || ad < 28) continue; // under the terminal box
      if (ad > 150 && ad < 210) continue; // between the feet
      const side = Math.abs(Math.sin(a)); const h = 0.045 + 0.03 * side;
      const g = new T.BoxGeometry(0.80, h, 0.013, 1, 1, 1);
      const pos = g.attributes.position; for (let j = 0; j < pos.count; j++) { if (pos.getY(j) > 0) { pos.setZ(j, pos.getZ(j) * 0.45); pos.setX(j, pos.getX(j) * 0.985); } }
      g.computeVertexNormals(); g.translate(0, 0.43 + h / 2 - 0.006, 0); g.rotateX(-a); fins.push(g);
    }
    P.frame.add(mesh(merge(fins), paint));
    // feet
    const feet = [];
    for (const zs of [-1, 1]) {
      // cast foot web: profile in (z,y), extruded along x
      const sh = new T.Shape(); const pts = [[0.20, -0.375], [0.30, -0.30], [0.37, -0.25], [0.40, -0.33], [0.43, -0.47], [0.475, -0.525], [0.475, -0.565], [0.24, -0.565], [0.24, -0.5]];
      pts.forEach((q, i) => { const zz = q[0] * zs; i ? sh.lineTo(zz, q[1]) : sh.moveTo(zz, q[1]); });
      for (const x of [-0.30, 0.30]) {
        const g = new T.ExtrudeGeometry(sh, { depth: 0.2, bevelEnabled: true, bevelSize: 0.008, bevelThickness: 0.008, bevelSegments: 2, curveSegments: 4 });
        g.rotateY(-Math.PI / 2); g.scale(1, 1, -1); g.translate(x + 0.1, 0, 0); feet.push(g);
      }
    }
    feet.push(boxAt(0.62, 0.06, 0.26, 0, -0.40, 0));
    P.frame.add(mesh(merge(feet), paint));
    const footBolts = []; for (const x of [-0.36, -0.24, 0.24, 0.36]) for (const z of [-0.43, 0.43]) { footBolts.push(cylY(0.017, 0.025, x, -0.517, z, 6)); footBolts.push(cylY(0.026, 0.006, x, -0.527, z, 16)); }
    // terminal box
    const tbg = new T.ExtrudeGeometry(roundedRectShape(0.29, 0.29, 0.03, 0, 0), { depth: 0.11, bevelEnabled: true, bevelSize: 0.006, bevelThickness: 0.006, bevelSegments: 2 });
    tbg.rotateX(-Math.PI / 2); tbg.translate(0, 0.43, 0);
    P.frame.add(mesh(merge([tbg, boxAt(0.22, 0.03, 0.22, 0, 0.43, 0)]), paint));
    const tbl = new T.Mesh(new T.ExtrudeGeometry(roundedRectShape(0.30, 0.30, 0.025, 0, 0), { depth: 0.03, bevelEnabled: true, bevelSize: 0.008, bevelThickness: 0.008, bevelSegments: 2 }), paint);
    tbl.geometry.rotateX(-Math.PI / 2); tbl.position.y = 0.55; tbl.castShadow = tbl.receiveShadow = true; P.frame.add(tbl);
    const lidBolts = []; for (const sx of [-1, 1]) for (const sz of [-1, 1]) lidBolts.push(cylY(0.012, 0.016, sx * 0.125, 0.595, sz * 0.125, 12));
    P.frame.add(mesh(merge(lidBolts.concat(footBolts)), MAT.steel()));
    P.frame.add(mesh(merge([cylZ(0.03, 0.04, -0.06, 0.49, 0.165, 24), cylZ(0.03, 0.04, 0.06, 0.49, 0.165, 24)]), MAT.polymer()));
    P.frame.add(mesh(merge([cylZ(0.024, 0.025, -0.06, 0.49, 0.19, 6), cylZ(0.024, 0.025, 0.06, 0.49, 0.19, 6)]), MAT.darkSteel()));
    // lifting eye
    const eyes = []; for (const ex of [-0.3, 0.3]) { const e = new T.TorusGeometry(0.038, 0.011, 10, 28); e.translate(ex, 0.5, 0); eyes.push(e, cylY(0.018, 0.05, ex, 0.445, 0, 12)); }
    P.frame.add(mesh(merge(eyes), MAT.darkSteel()));
    // nameplate
    const np = new T.Mesh(new T.PlaneGeometry(0.24, 0.14), std({ map: nameplateTex(['3~ INDUCTION MOTOR', '400 V Δ   50 Hz   IP55', '45 kW   1475 min⁻¹', 'cos φ 0.86   IE3']), metalness: 0.5, roughness: 0.45 }));
    np.position.set(0.05, -0.06, 0.437 + 0.001); P.frame.add(np);

    // ---- stator ----
    statorCore(P.statorCore, rO, rB, L, 36, 0.085, 0.022, 44);
    statorWinding(P.statorWinding, rB, L, 36, 0.085, 0.022, 8, 0.016, true);

    // ---- rotor core (laminated, skewed slots with narrow openings) ----
    const nBars = 28, rBar = 0.205, skew = 360 / 36 * D; // one stator slot pitch skew
    const rs = new T.Shape(); for (let i = 0; i <= 160; i++) { const v = polar(rR, i / 160 * Math.PI * 2); i ? rs.lineTo(v.x, v.y) : rs.moveTo(v.x, v.y); }
    rs.holes.push(circlePath(0.066, 48, true));
    const nPl = 40, pitch = L / nPl;
    const rotorPlate = extrudeX(rs, pitch * 0.9, 0);
    const rcMat = MAT.lamination(); const rc = new T.InstancedMesh(rotorPlate, rcMat, nPl); rc.castShadow = rc.receiveShadow = true;
    const mx = new T.Matrix4(); for (let i = 0; i < nPl; i++) { mx.makeTranslation(-L / 2 + i * pitch, 0, 0); rc.setMatrixAt(i, mx); }
    P.rotorCore.add(rc);
    // ---- rotor bars: skewed, flush with surface (visible as stripes) ----
    const bars = [];
    for (let k = 0; k < nBars; k++) {
      const g = new T.BoxGeometry(L + 0.02, 0.05, 0.016, 12, 1, 1); g.translate(0, rR - 0.024, 0);
      const pos = g.attributes.position; const v = new T.Vector3();
      for (let i = 0; i < pos.count; i++) { v.fromBufferAttribute(pos, i); const ang = k / nBars * Math.PI * 2 + skew * (v.x / L); const c = Math.cos(ang), s = Math.sin(ang); const y = v.y * c - v.z * s, z = v.y * s + v.z * c; pos.setXYZ(i, v.x, y + 0.0, z); }
      g.computeVertexNormals(); bars.push(g);
    }
    P.rotorBars.add(mesh(merge(bars), MAT.aluminium()));
    // ---- end rings with cast cooling vanes ----
    const er = [];
    for (const s of [-1, 1]) {
      er.push(lathe([[0.135, s * (L / 2)], [rR - 0.004, s * (L / 2)], [rR - 0.004, s * (L / 2 + 0.035)], [0.135, s * (L / 2 + 0.035)], [0.135, s * (L / 2)]], 96));
      for (let k = 0; k < 10; k++) { const g = new T.BoxGeometry(0.045, 0.07, 0.012); g.translate(s * (L / 2 + 0.055), 0.185, 0); g.rotateX(k / 10 * Math.PI * 2); er.push(g); }
    }
    P.endRings.add(mesh(merge(er), MAT.castAl()));
    // ---- shaft ----
    shaft(P.shaft, [[0, -0.84], [0.036, -0.84], [0.040, -0.836], [0.040, -0.58], [0.046, -0.575], [0.046, -0.455], [0.054, -0.45], [0.054, -0.40], [0.066, -0.395], [0.066, 0.395], [0.054, 0.40], [0.054, 0.45], [0.046, 0.455], [0.046, 0.575], [0.038, 0.58], [0.038, 0.70], [0, 0.70]], -0.82, -0.62, 0.040);
    // ---- air gap highlight ----
    const ag = mesh(tubeRing(rR + 0.0005, rB - 0.0005, -L / 2 - 0.03, L / 2 + 0.03, 128), MAT.glow(), false, false); P.airGap.add(ag);
    // ---- bearings ----
    bearing(P.bearingDE, -0.49, 0.046, 0.10, 0.052);
    bearing(P.bearingNDE, 0.49, 0.046, 0.10, 0.052);
    // ---- end shields ----
    for (const s of [-1, 1]) {
      const part = s < 0 ? P.endShieldDE : P.endShieldNDE; const pm = MAT.paintBlue();
      const prof = [[0.10, 0.462], [0.10, 0.522], [0.135, 0.532], [0.22, 0.518], [0.36, 0.488], [0.425, 0.462], [0.452, 0.455], [0.452, 0.43], [0.402, 0.43], [0.402, 0.442], [0.36, 0.462], [0.22, 0.494], [0.135, 0.505], [0.115, 0.49], [0.10, 0.462]].map(p => [p[0], s * p[1]]);
      part.add(mesh(lathe(prof, 128), pm));
      part.add(mesh(lathe([[0.125, s * 0.531], [0.16, s * 0.531], [0.165, s * 0.545], [0.135, s * 0.548], [0.125, s * 0.531]], 64), pm));
      const ribs = []; const outer = [[0.15, 0.53], [0.22, 0.518], [0.36, 0.488], [0.41, 0.468]];
      for (let k = 0; k < 8; k++) {
        const sh = new T.Shape(); outer.forEach((q, i) => i ? sh.lineTo(q[0], q[1] + 0.018) : sh.moveTo(q[0], q[1] + 0.018)); for (let i = outer.length - 1; i >= 0; i--) sh.lineTo(outer[i][0], outer[i][1] - 0.01);
        const g = new T.ExtrudeGeometry(sh, { depth: 0.014, bevelEnabled: false }); g.translate(0, 0, -0.007);
        const pos = g.attributes.position; for (let j = 0; j < pos.count; j++) { const r = pos.getX(j), ax = pos.getY(j); pos.setXYZ(j, s * ax, r, pos.getZ(j)); }
        g.computeVertexNormals(); g.rotateX(k / 8 * Math.PI * 2 + 0.39); ribs.push(g);
      }
      part.add(mesh(merge(ribs), pm));
      const bolts = []; for (let k = 0; k < 4; k++) { const p = polar(0.145, k / 4 * Math.PI * 2 + 0.78); bolts.push(cylX(0.009, 0.014, s * 0.55, p.y, -p.x, 6)); }
      for (let k = 0; k < 8; k++) { const p = polar(0.44, k / 8 * Math.PI * 2 + 0.39); bolts.push(cylX(0.014, 0.02, s * 0.462, p.y, -p.x, 6)); }
      if (s < 0) bolts.push(cylX(0.008, 0.03, s * 0.53, 0.115, 0, 6));
      part.add(mesh(merge(bolts), MAT.steel()));
      if (s < 0) { part.add(mesh(tubeRing(0.047, 0.07, -0.535, -0.522, 48), MAT.polymer())); } // V-ring seal
    }
    // ---- fan ----
    const fanM = MAT.polymer(); const fg = [lathe([[0.039, 0.585], [0.075, 0.585], [0.075, 0.665], [0.039, 0.665], [0.039, 0.585]], 48), lathe([[0.07, 0.655], [0.20, 0.655], [0.20, 0.665], [0.07, 0.665]], 64)];
    for (let k = 0; k < 11; k++) { const g = new T.BoxGeometry(0.075, 0.33, 0.012); g.translate(0.62, 0.075 + 0.165, 0); g.rotateX(k / 11 * Math.PI * 2); fg.push(g); }
    P.fan.add(mesh(merge(fg), fanM));
    // ---- fan cover (cowl with grille) ----
    const cm = MAT.paintBlue(); const cg = [lathe([[0.452, 0.53], [0.458, 0.53], [0.458, 0.73], [0.44, 0.755], [0.425, 0.762], [0.42, 0.757], [0.452, 0.73], [0.452, 0.53]], 128)];
    P.fanCover.add(mesh(merge(cg), cm));
    const grille = [];
    for (let r = 0.07; r < 0.42; r += 0.032) { const t = new T.TorusGeometry(r, 0.0065, 6, 96); t.rotateY(Math.PI / 2); t.translate(0.758, 0, 0); grille.push(t); }
    for (let k = 0; k < 6; k++) { const g = new T.BoxGeometry(0.012, 0.37, 0.016); g.translate(0.758, 0.235, 0); g.rotateX(k / 6 * Math.PI * 2); grille.push(g); }
    grille.push(lathe([[0, 0.752], [0.06, 0.752], [0.06, 0.762], [0, 0.762]], 48));
    P.fanCover.add(mesh(merge(grille), cm));
    const cb = []; for (let k = 0; k < 4; k++) { const p = polar(0.455, k / 4 * Math.PI * 2 + 0.6); cb.push(cylX(0.011, 0.02, 0.56, p.y * 1.01, -p.x * 1.01, 6)); }
    P.fanCover.add(mesh(merge(cb), MAT.steel()));

    const order = ['frame', 'statorCore', 'statorWinding', 'stator', 'airGap', 'rotorCore', 'rotorBars', 'endRings', 'shaft', 'bearingDE', 'bearingNDE', 'endShieldDE', 'endShieldNDE', 'fan', 'fanCover'];
    return finish(P, order);
  }

  // ======================================================================
  //  SYNCHRONOUS MOTOR (salient-pole rotor, slip rings & brushes, top cooler)
  // ======================================================================
  function salientRotor(partCore, partCoils, partDamper, opts) {
    const L = opts.L, nP = opts.poles, rHub = opts.rHub, rBody = opts.rBody, rShoe = opts.rShoe, bodyW = opts.bodyW;
    const lam = MAT.lamination();
    // hub / spider
    partCore.add(mesh(tubeRing(0.07, rHub, -L / 2 - 0.02, L / 2 + 0.02, 96), MAT.darkSteel()));
    const coreG = [], shoeG = [];
    for (let k = 0; k < nP; k++) {
      const a = k / nP * Math.PI * 2;
      const body = new T.BoxGeometry(L, rBody - rHub + 0.02, bodyW); body.translate(0, (rHub + rBody) / 2 - 0.01, 0); body.rotateX(-a); coreG.push(body);
      // pole shoe = annular sector
      const half = (360 / nP) * 0.36 * D; const s = new T.Shape();
      const N = 24; for (let i = 0; i <= N; i++) { const v = polar(rShoe, a - half + 2 * half * i / N); i ? s.lineTo(v.x, v.y) : s.moveTo(v.x, v.y); }
      for (let i = N; i >= 0; i--) { const v = polar(rBody, a - half * 0.82 + 2 * half * 0.82 * i / N); s.lineTo(v.x, v.y); }
      shoeG.push(extrudeX(s, L, -L / 2));
    }
    partCore.add(mesh(merge(coreG.concat(shoeG)), lam));
    // field coils: layered rounded-rect rings around each pole body
    const coilG = [], insG = [];
    const nLay = 9, r0 = rHub + 0.012, r1 = rBody - 0.012, step = (r1 - r0) / nLay;
    for (let k = 0; k < nP; k++) {
      const a = k / nP * Math.PI * 2;
      for (let j = 0; j < nLay; j++) {
        const grow = 0.004 * Math.sin(Math.PI * (j + 0.5) / nLay);
        const sh = roundedRectShape(bodyW + 0.075 + grow, L + 0.075 + grow, 0.03, 0, 0);
        sh.holes.push(roundedRectPath(bodyW + 0.01, L + 0.01, 0.006, 0, 0));
        const g = new T.ExtrudeGeometry(sh, { depth: step * 0.86, bevelEnabled: false, curveSegments: 6 });
        // shape plane (x=tangential, y=axial) -> extrude along +z = radial
        g.rotateX(-Math.PI / 2); // z->y (radial up), y->-z
        g.rotateY(Math.PI / 2);  // fix axes: axial -> x
        g.translate(0, r0 + j * step, 0); g.rotateX(-a);
        coilG.push(g);
      }
      const ins = new T.ExtrudeGeometry((() => { const s = roundedRectShape(bodyW + 0.09, L + 0.09, 0.035, 0, 0); s.holes.push(roundedRectPath(bodyW + 0.01, L + 0.01, 0.006, 0, 0)); return s; })(), { depth: 0.008, bevelEnabled: false, curveSegments: 6 });
      ins.rotateX(-Math.PI / 2); ins.rotateY(Math.PI / 2); ins.translate(0, r1 - 0.002, 0); ins.rotateX(-a); insG.push(ins);
    }
    partCoils.add(mesh(merge(coilG), MAT.copper()));
    partCoils.add(mesh(merge(insG), MAT.insulation()));
    // damper (amortisseur) bars + end segments
    if (partDamper) {
      const dg = [];
      for (let k = 0; k < nP; k++) {
        const a = k / nP * Math.PI * 2; const half = (360 / nP) * 0.3 * D;
        for (let i = 0; i < 6; i++) { const aa = a - half + 2 * half * i / 5; const p = polar(rShoe - 0.012, aa); dg.push(cylX(0.0075, L + 0.05, 0, p.y, -p.x, 10)); }
        for (const s of [-1, 1]) {
          const sh = new T.Shape(); const N = 16;
          for (let i = 0; i <= N; i++) { const v = polar(rShoe - 0.003, a - half - 0.02 + (2 * half + 0.04) * i / N); i ? sh.lineTo(v.x, v.y) : sh.moveTo(v.x, v.y); }
          for (let i = N; i >= 0; i--) { const v = polar(rShoe - 0.024, a - half - 0.02 + (2 * half + 0.04) * i / N); sh.lineTo(v.x, v.y); }
          dg.push(extrudeX(sh, 0.012, s > 0 ? L / 2 + 0.008 : -L / 2 - 0.02));
        }
      }
      partDamper.add(mesh(merge(dg), MAT.copperDark()));
    }
  }

  function buildSynchronous() {
    const P = {}; const V = (x, y, z) => new T.Vector3(x, y, z);
    const L = 0.80, rO = 0.52, rB = 0.36;
    P.frame = new Part('frame', 'Frame / Housing', 'Welded steel frame that carries the stator, bearings and cooler, and bolts to the foundation.', { offset: V(0, 1.3, 0), anchor: V(-0.25, 0.56, 0.4) , delay: 0.0 });
    P.cooling = new Part('cooling', 'Cooling System', 'Top-mounted air-to-air heat exchanger plus a shaft fan: inside air is cooled by outside air.', { offset: V(0, 1.75, 0), anchor: V(0.35, 0.92, 0.2), delay: 0.0 });
    P.shaftFan = new Part('shaftFan', 'Cooling System', '', { offset: V(-1.55, 0, 0), anchor: V(0.5, 0.3, 0), delay: 0.45 });
    P.statorCore = new Part('statorCore', 'Stator Core', 'Laminated steel stack. Guides the magnetic flux with low losses (same idea as in the induction motor).', { anchor: V(-0.25, 0.42, 0.3), delay: 0.25 });
    P.statorWinding = new Part('statorWinding', 'Three-Phase Stator Windings', 'Three groups of copper coils (phases). Fed with three-phase AC, they create the rotating magnetic field.', { anchor: V(0.5, 0.36, 0.2), delay: 0.25 });
    P.stator = new Part('stator', 'Stator', 'The stationary outer part: laminated core + three-phase windings.', { hidden: true, anchor: V(0, 0.55, 0.2) });
    P.rotorPoles = new Part('rotorPoles', 'Rotor Poles', 'Salient (projecting) steel poles on a hub. Each becomes a strong N or S electromagnet.', { offset: V(-1.55, 0, 0), anchor: V(-0.1, 0.34, 0.12), delay: 0.45 });
    P.fieldWinding = new Part('fieldWinding', 'Field Winding', 'Copper coils around each pole. DC current here turns the poles into fixed electromagnets.', { offset: V(-1.55, 0, 0), anchor: V(0.2, 0.25, 0.14), delay: 0.45 });
    P.damper = new Part('damper', 'Damper (Starting) Bars', 'Copper bars in the pole faces. They act like a squirrel cage to help the motor start and damp oscillations.', { offset: V(-1.55, 0, 0), anchor: V(0.42, 0.34, 0.0), delay: 0.45 });
    P.shaft = new Part('shaft', 'Shaft', 'Forged steel shaft that carries the rotor and transmits torque to the load.', { offset: V(-1.55, 0, 0), anchor: V(-0.95, 0.05, 0), delay: 0.45 });
    P.sliprings = new Part('sliprings', 'Slip Rings & Brushes', 'Rotating bronze rings with stationary carbon brushes: the sliding contact that feeds DC into the spinning rotor.', { offset: V(1.25, 0, 0), anchor: V(0.98, 0.16, 0), delay: 0.75 });
    P.exciter = new Part('exciter', 'DC Excitation System', 'Exciter cubicle: converts AC to controlled DC for the field winding. Adjusting it controls the power factor.', { offset: V(1.25, 0, 0), anchor: V(1.55, 0.36, -1.0), delay: 0.75 });
    P.bearingDE = new Part('bearingDE', 'Bearings', 'Oil-lubricated sleeve bearings support the heavy rotor and keep it centred in the stator bore.', { offset: V(-2.05, 0, 0), anchor: V(-0.68, 0.1, 0), delay: 0.6 });
    P.bearingNDE = new Part('bearingNDE', 'Bearings', '', { offset: V(0.6, 0, 0), anchor: V(0.68, 0.1, 0), delay: 0.6 });
    P.endShieldDE = new Part('endShieldDE', 'End Shield (DE)', 'Bearing housings closing each end of the frame.', { offset: V(-2.4, 0, 0), anchor: V(-0.6, 0.4, 0), delay: 0.65 });
    P.endShieldNDE = new Part('endShieldNDE', 'End Shield (NDE)', '', { offset: V(0.85, 0, 0), anchor: V(0.6, 0.4, 0), delay: 0.65 });

    const paint = MAT.paintGraphite();
    // ---- welded box frame ----
    const fr = [];
    const sh = roundedRectShape(1.22, 1.18, 0.12, 0, 0.02); sh.holes.push(circlePath(rO + 0.005, 128, true));
    fr.push(extrudeX(sh, 0.06, -0.56)); fr.push(extrudeX(sh, 0.06, 0.50));
    // side skins
    fr.push(boxAt(1.06, 1.10, 0.02, 0, 0.04, 0.60)); fr.push(boxAt(1.06, 1.10, 0.02, 0, 0.04, -0.60));
    fr.push(boxAt(1.06, 0.02, 1.0, 0, 0.60, 0));
    for (const x of [-0.53, 0.53]) for (const z of [-0.6, 0.6]) fr.push(cylY(0.03, 1.12, x, 0.03, z, 16));
    for (const y of [-0.28, 0.3]) { fr.push(boxAt(1.06, 0.035, 0.04, 0, y, 0.62)); fr.push(boxAt(1.06, 0.035, 0.04, 0, y, -0.62)); }
    // stiffener ribs
    for (const x of [-0.25, 0.0, 0.25]) { fr.push(boxAt(0.025, 0.9, 0.05, x, 0.0, 0.62)); fr.push(boxAt(0.025, 0.9, 0.05, x, 0.0, -0.62)); }
    // base feet
    fr.push(boxAt(1.3, 0.07, 0.24, 0, -0.59, 0.55)); fr.push(boxAt(1.3, 0.07, 0.24, 0, -0.59, -0.55));
    fr.push(boxAt(1.12, 0.10, 1.22, 0, -0.52, 0));
    P.frame.add(mesh(merge(fr), paint));
    const fb = []; for (const x of [-0.58, -0.2, 0.2, 0.58]) for (const z of [-0.62, 0.62]) fb.push(cylY(0.022, 0.03, x, -0.545, z, 6));
    P.frame.add(mesh(merge(fb), MAT.steel()));
    // main terminal box on the side
    const tbm = MAT.paintGraphite();
    P.frame.add(mesh(merge([boxAt(0.36, 0.34, 0.16, 0.12, 0.05, 0.69), boxAt(0.38, 0.36, 0.02, 0.12, 0.05, 0.77)]), tbm));
    P.frame.add(mesh(merge([cylY(0.045, 0.09, 0.04, -0.17, 0.69), cylY(0.045, 0.09, 0.2, -0.17, 0.69)]), MAT.polymer()));
    const np = new T.Mesh(new T.PlaneGeometry(0.3, 0.17), std({ map: nameplateTex(['3~ SYNCHRONOUS MOTOR', '6.6 kV   50 Hz   1500 min⁻¹', 'Excitation: DC 120 V', 'cos φ 0.9 (leading) IP54']), metalness: 0.5, roughness: 0.45 }));
    np.position.set(-0.3, 0.2, 0.611); P.frame.add(np);
    // ---- cooler (air-to-air heat exchanger) ----
    const cm = MAT.paintLight(); const cg = [];
    cg.push(boxAt(1.0, 0.36, 1.12, 0, 0.80, 0));
    cg.push(boxAt(1.04, 0.03, 1.16, 0, 0.995, 0));
    P.cooling.add(mesh(merge(cg), cm));
    // tube ends grid on front face (x=-0.5) and back
    const tubes = []; for (let i = 0; i < 7; i++) for (let j = 0; j < 14; j++) { tubes.push(cylX(0.014, 1.02, 0, 0.66 + i * 0.04, -0.52 + j * 0.08, 10)); }
    P.cooling.add(mesh(merge(tubes), MAT.aluminium()));
    // external cooler fan housing at NDE of cooler
    P.cooling.add(mesh(merge([cylX(0.17, 0.16, 0.58, 0.80, 0, 48)]), cm));
    const cgr = []; for (let r = 0.04; r < 0.17; r += 0.03) { const t = new T.TorusGeometry(r, 0.005, 6, 64); t.rotateY(Math.PI / 2); t.translate(0.665, 0.80, 0); cgr.push(t); }
    P.cooling.add(mesh(merge(cgr), MAT.darkSteel()));
    // internal shaft-mounted radial fan (part of cooling system)
    const ifan = [lathe([[0.075, 0.48], [0.11, 0.48], [0.11, 0.53], [0.075, 0.53], [0.075, 0.48]], 48), lathe([[0.1, 0.525], [0.34, 0.525], [0.34, 0.535], [0.1, 0.535]], 96)];
    for (let k = 0; k < 12; k++) { const g = new T.BoxGeometry(0.045, 0.22, 0.01); g.translate(0.505, 0.21, 0); g.rotateX(k / 12 * Math.PI * 2); ifan.push(g); }
    const ifm = mesh(merge(ifan), MAT.castAl()); P.shaftFan.add(ifm);

    // ---- stator ----
    statorCore(P.statorCore, rO, rB, L, 48, 0.10, 0.024, 50);
    statorWinding(P.statorWinding, rB, L, 48, 0.10, 0.024, 10, 0.019, true);

    // ---- rotor ----
    salientRotor(P.rotorPoles, P.fieldWinding, P.damper, { L: L - 0.02, poles: 4, rHub: 0.15, rBody: 0.30, rShoe: rB - 0.006, bodyW: 0.17 });
    shaft(P.shaft, [[0, -1.05], [0.05, -1.05], [0.055, -1.045], [0.055, -0.74], [0.062, -0.735], [0.062, -0.63], [0.07, -0.625], [0.07, -0.45], [0.075, -0.445], [0.075, 0.445], [0.07, 0.45], [0.07, 0.565], [0.062, 0.57], [0.062, 0.66], [0.055, 0.665], [0.055, 1.08], [0, 1.08]], -1.03, -0.78, 0.055);
    // ---- slip rings + brush gear ----
    const srm = MAT.bronze();
    P.sliprings.add(mesh(tubeRing(0.056, 0.075, 0.86, 1.04, 48), MAT.insulation()));
    for (const x of [0.90, 0.99]) P.sliprings.add(mesh(lathe([[0.075, x - 0.028], [0.098, x - 0.028], [0.1, x - 0.025], [0.1, x + 0.025], [0.098, x + 0.028], [0.075, x + 0.028]], 64), srm));
    // insulating barriers between and beside the rings
    for (const x of [0.857, 0.945, 1.033]) P.sliprings.add(mesh(lathe([[0.075, x - 0.006], [0.108, x - 0.006], [0.108, x + 0.006], [0.075, x + 0.006]], 64), MAT.insulation()));
    // brush gear: box-type holders on an insulated rocker ring, carbon brushes pressed on by springs, copper pigtails
    const bg = [], brushes = [], cu = [], ins = [];
    const radial = (geo, a, x) => { geo.rotateX(-a); geo.translate(x, 0, 0); return geo; };
    for (const x of [0.90, 0.99]) {
      // rocker arc (in the YZ plane, centred on top, ±75°)
      const arc = new T.TorusGeometry(0.218, 0.011, 10, 64, 150 * D); arc.rotateZ(15 * D); arc.rotateY(Math.PI / 2); arc.translate(x, 0, 0); bg.push(arc);
      for (const ang of [-35, 35]) {
        const a = ang * D;
        const br = new T.BoxGeometry(0.022, 0.05, 0.03); br.translate(0, 0.125, 0); brushes.push(radial(br, a, x));            // carbon brush (r 0.100–0.150)
        const hold = []; const wall = 0.004;                                                                                   // open-bottom holder box (r 0.118–0.166)
        hold.push(boxAt(0.032, 0.048, wall, 0, 0.142, 0.017), boxAt(0.032, 0.048, wall, 0, 0.142, -0.017), boxAt(wall, 0.048, 0.038, 0.0145, 0.142, 0), boxAt(wall, 0.048, 0.038, -0.0145, 0.142, 0));
        hold.forEach(g => bg.push(radial(g, a, x)));
        bg.push(radial(cylY(0.006, 0.05, 0, 0.19, 0, 10), a, x));                                                              // clamp stud to the rocker
        const spr = new T.TorusGeometry(0.014, 0.0025, 6, 20, Math.PI); spr.rotateY(Math.PI / 2); spr.translate(0, 0.152, 0); bg.push(radial(spr, a, x)); // spring finger
        const pt = new T.CatmullRomCurve3([V(0.006, 0.151, 0.01), V(0.02, 0.17, 0.022), V(0.012, 0.2, 0.02), V(0, 0.212, 0.012)]);
        cu.push(radial(new T.TubeGeometry(pt, 16, 0.0028, 6, false), a, x));                                                   // copper pigtail
      }
      bg.push(boxAt(0.028, 0.012, 0.05, x, 0.236, 0)); cu.push(boxAt(0.02, 0.016, 0.035, x, 0.248, 0));                     // terminal lug
    }
    // pedestal: base plate, two posts with insulators, cross ties joining both rockers
    for (const z of [-1, 1]) {
      const yz = polar(0.218, 75 * D); const pz = z * Math.abs(yz.x || yz.y);
      const py = 0.218 * Math.cos(75 * D), pz2 = z * 0.218 * Math.sin(75 * D);
      bg.push(boxAt(0.12, 0.022, 0.022, 0.945, py, pz2));
      bg.push(cylY(0.016, 0.2, 0.945, -0.15, pz2, 16)); ins.push(cylY(0.022, 0.09, 0.945, py - 0.06, pz2, 16));
    }
    bg.push(boxAt(0.2, 0.03, 0.52, 0.945, -0.255, 0));
    P.sliprings.add(mesh(merge(bg), MAT.darkSteel()));
    P.sliprings.add(mesh(merge(brushes), MAT.carbon()));
    P.sliprings.add(mesh(merge(cu), MAT.copper()));
    P.sliprings.add(mesh(merge(ins), MAT.insulation()));
    // ---- exciter cubicle + DC cables ----
    const ex = MAT.paintLight();
    P.exciter.add(mesh(merge([boxAt(0.36, 0.95, 0.30, 1.55, -0.145, -1.05), boxAt(0.38, 0.02, 0.32, 1.55, 0.34, -1.05)]), ex));
    const exd = new T.Mesh(new T.PlaneGeometry(0.30, 0.86), std({ map: (() => { const c = document.createElement('canvas'); c.width = 256; c.height = 720; const g = c.getContext('2d'); g.fillStyle = '#7f8a93'; g.fillRect(0, 0, 256, 720); g.fillStyle = '#0f1a24'; g.fillRect(40, 60, 176, 110); g.fillStyle = '#38b6ff'; g.font = 'bold 44px Inter, Arial'; g.fillText('DC', 95, 120); g.font = '22px Inter, Arial'; g.fillText('120 V  85 A', 65, 155); for (let i = 0; i < 3; i++) { g.beginPath(); g.arc(70 + i * 58, 230, 16, 0, 7); g.fillStyle = ['#2ecc71', '#f1c40f', '#e74c3c'][i]; g.fill(); } g.fillStyle = '#5f6a73'; for (let i = 0; i < 12; i++) g.fillRect(40, 300 + i * 18, 176, 8); g.fillStyle = '#ccc'; g.fillRect(215, 420, 14, 80); g.fillStyle = '#20252b'; g.font = 'bold 22px Inter, Arial'; g.fillText('EXCITER', 80, 660); const t = new T.CanvasTexture(c); t.encoding = T.sRGBEncoding; return t; })(), metalness: 0.3, roughness: 0.5 }));
    exd.position.set(1.55, -0.145, -0.899); exd.rotation.y = 0; P.exciter.add(exd);
    // cables from cubicle to brush gear
    const cab = [];
    for (const dz of [-0.03, 0.03]) {
      const c = new T.CatmullRomCurve3([V(1.55, 0.34, -1.05 + dz), V(1.5, 0.55, -0.85 + dz), V(1.15, 0.5, -0.4 + dz), V(0.97, 0.32, -0.12 + dz * 0.5), V(0.945, 0.23, -0.05 + dz)]);
      cab.push(new T.TubeGeometry(c, 40, 0.014, 8, false));
    }
    P.exciter.add(mesh(merge(cab), MAT.cable()));
    // ---- bearings & end shields ----
    sleeveBearing(P.bearingDE, -0.682, 0.0625, 0.085, 0.095);
    sleeveBearing(P.bearingNDE, 0.615, 0.0625, 0.085, 0.095);
    for (const s of [-1, 1]) {
      const part = s < 0 ? P.endShieldDE : P.endShieldNDE; const pm = MAT.paintGraphite();
      const prof = [[0.14, 0.565], [0.14, 0.64], [0.19, 0.655], [0.32, 0.64], [0.50, 0.62], [0.55, 0.61], [0.55, 0.56], [0.53, 0.56], [0.50, 0.585], [0.32, 0.605], [0.19, 0.62], [0.16, 0.6], [0.14, 0.565]].map(p => [p[0], s * p[1]]);
      part.add(mesh(lathe(prof, 128), pm));
      const bx0 = s < 0 ? 0.625 : 0.56, bx1 = s < 0 ? 0.74 : 0.675;
      part.add(mesh(lathe([[0.095, s * bx0], [0.2, s * bx0], [0.215, s * (bx0 + 0.02)], [0.215, s * (bx1 - 0.02)], [0.2, s * bx1], [0.095, s * bx1], [0.095, s * bx0]], 64), pm));
      part.add(mesh(cylZ(0.028, 0.03, s * (bx0 + bx1) / 2, -0.08, 0.215, 24), std({ color: 0xb8e2ff, metalness: 0.1, roughness: 0.05, transparent: true, opacity: 0.6 })));
      part.add(mesh(merge([cylY(0.018, 0.06, s * (bx0 + bx1) / 2, 0.24, 0, 12), boxAt(0.04, 0.012, 0.44, s * (bx0 + bx1) / 2, 0, 0)]), MAT.darkSteel()));
      const bolts = []; for (let k = 0; k < 12; k++) { const p = polar(0.535, k / 12 * Math.PI * 2 + 0.26); bolts.push(cylX(0.016, 0.025, s * 0.62, p.y, -p.x, 6)); }
      part.add(mesh(merge(bolts), MAT.steel()));
    }

    const order = ['frame', 'cooling', 'shaftFan', 'statorCore', 'statorWinding', 'stator', 'rotorPoles', 'fieldWinding', 'damper', 'shaft', 'sliprings', 'exciter', 'bearingDE', 'bearingNDE', 'endShieldDE', 'endShieldNDE'];
    return finish(P, order);
  }

  // ======================================================================
  //  Stand-alone rotor variants for the "rotor designs" slide
  // ======================================================================
  function buildCylindricalRotor() {
    const g = new T.Group(); const L = 1.3, r = 0.3;
    const s = new T.Shape(); for (let i = 0; i <= 200; i++) { const v = polar(r, i / 200 * Math.PI * 2); i ? s.lineTo(v.x, v.y) : s.moveTo(v.x, v.y); }
    const forging = mesh(extrudeX(s, L, -L / 2), std({ color: 0x9aa0a7, metalness: 1, roughness: 0.3 })); g.add(forging);
    // slots with wedges over 2/3 of circumference (two pole faces left unslotted)
    const wedges = [];
    for (let k = 0; k < 32; k++) {
      const a = k / 32 * Math.PI * 2; const ad = (a / D) % 180; if (ad < 32 || ad > 148) continue;
      const w = new T.BoxGeometry(L - 0.002, 0.012, 0.03); w.translate(0, r - 0.004, 0); w.rotateX(-a); wedges.push(w);
    }
    g.add(mesh(merge(wedges), MAT.bronze()));
    // end windings under retaining rings
    for (const sd of [-1, 1]) {
      g.add(mesh(lathe([[0.31, sd * 0.65], [0.315, sd * 0.65], [0.315, sd * 0.88], [0.305, sd * 0.89], [0.2, sd * 0.89], [0.2, sd * 0.875], [0.3, sd * 0.875], [0.3, sd * 0.65]], 128), std({ color: 0xd8dde2, metalness: 1, roughness: 0.18 })));
    }
    g.add(mesh(lathe([[0, -1.6], [0.1, -1.6], [0.1, -0.9], [0.14, -0.9], [0.14, 0.9], [0.1, 0.9], [0.1, 1.5], [0, 1.5]], 64), MAT.steel()));
    for (const x of [1.15, 1.25]) g.add(mesh(lathe([[0.1, x - 0.035], [0.13, x - 0.035], [0.13, x + 0.035], [0.1, x + 0.035]], 64), MAT.bronze()));
    return g;
  }
  function buildSalientRotor(withExciter) {
    const g = new T.Group(); const pc = new Part('c'), pw = new Part('w'), pd = new Part('d'), ps = new Part('s');
    salientRotor(pc, pw, pd, { L: 0.78, poles: 4, rHub: 0.15, rBody: 0.30, rShoe: 0.354, bodyW: 0.17 });
    shaft(ps, [[0, -1.0], [0.05, -1.0], [0.055, -0.995], [0.055, -0.6], [0.07, -0.6], [0.07, -0.45], [0.075, -0.445], [0.075, 0.445], [0.07, 0.45], [0.07, 1.25], [0, 1.25]], -0.98, -0.7, 0.055);
    [pc, pw, pd, ps].forEach(p => g.add(p.group));
    if (withExciter) {
      // brushless exciter armature (laminated, with copper end turns) + rotating diode wheel
      const ea = new T.Group();
      const s = new T.Shape(); for (let i = 0; i <= 120; i++) { const v = polar(0.17, i / 120 * Math.PI * 2); i ? s.lineTo(v.x, v.y) : s.moveTo(v.x, v.y); } s.holes.push(circlePath(0.07, 32, true));
      ea.add(mesh(extrudeX(s, 0.14, 0.78), MAT.lamination()));
      for (const x of [0.77, 0.93]) ea.add(mesh(tubeRing(0.12, 0.165, x - 0.015, x + 0.015, 64), MAT.copper()));
      const dw = []; dw.push(lathe([[0.07, 1.02], [0.21, 1.02], [0.21, 1.045], [0.07, 1.045]], 96));
      ea.add(mesh(merge(dw), MAT.castAl()));
      const diodes = []; for (let k = 0; k < 6; k++) { const p = polar(0.16, k / 6 * Math.PI * 2); diodes.push(cylX(0.025, 0.04, 1.065, p.y, -p.x, 20)); }
      ea.add(mesh(merge(diodes), MAT.brass()));
      const sinks = []; for (let k = 0; k < 6; k++) { const p = polar(0.16, k / 6 * Math.PI * 2 + 0.26); sinks.push(boxAt(0.05, 0.05, 0.05, 1.07, p.y, -p.x)); }
      ea.add(mesh(merge(sinks), MAT.aluminium()));
      g.add(ea);
      // stationary exciter field (ghosted ring)
      const st = mesh(tubeRing(0.18, 0.26, 0.76, 0.94, 96), std({ color: 0x6f86a0, metalness: 0.6, roughness: 0.4, transparent: true, opacity: 0.25, depthWrite: false }));
      st.castShadow = false; g.add(st); g.userData.exciterStator = st;
    } else {
      for (const x of [0.95, 1.05]) g.add(mesh(lathe([[0.07, x - 0.03], [0.1, x - 0.03], [0.1, x + 0.03], [0.07, x + 0.03]], 64), MAT.bronze()));
    }
    return g;
  }

  window.MOTORS = { buildInduction, buildSynchronous, buildCylindricalRotor, buildSalientRotor, MAT };
})();
