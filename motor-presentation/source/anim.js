/* 2D working-principle animations (Canvas2D), deterministic frame(t). */
(function () {
  const TAU = Math.PI * 2, D = Math.PI / 180;
  const C = {
    bg0: '#16314f', bg1: '#050b14', steel: '#5d6873', steelHi: '#8a96a3', steelLo: '#2f3943',
    copper: '#c46a38', white: '#ffffff', text: '#c9d6e3', muted: '#6f8aa6', accent: '#38b6ff',
    N: '#ff4f4f', S: '#2f8bff', A: '#ff7a59', B: '#ffd166', Cc: '#5ee0c8', amber: '#ffb347', green: '#3ddc97'
  };
  const PH = [C.A, C.B, C.Cc];
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const ease = t => { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); };
  const wrap = a => { a = (a + Math.PI) % TAU; if (a < 0) a += TAU; return a - Math.PI; };
  let cv, g, W = 1920, H = 1080;

  function init(w, h) {
    W = w || 1920; H = h || 1080; cv = document.getElementById('cv'); cv.width = W; cv.height = H; g = cv.getContext('2d');
  }
  function bg() {
    const gr = g.createRadialGradient(W * 0.5, H * 0.42, 50, W * 0.5, H * 0.45, W * 0.75);
    gr.addColorStop(0, C.bg0); gr.addColorStop(0.45, '#0b1a2c'); gr.addColorStop(1, C.bg1);
    g.fillStyle = gr; g.fillRect(0, 0, W, H);
    g.strokeStyle = 'rgba(56,182,255,0.05)'; g.lineWidth = 1;
    for (let x = 0; x < W; x += 48) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, H); g.stroke(); }
    for (let y = 0; y < H; y += 48) { g.beginPath(); g.moveTo(0, y); g.lineTo(W, y); g.stroke(); }
  }
  const P = (cx, cy, r, a) => [cx + r * Math.cos(a), cy - r * Math.sin(a)];
  function txt(s, x, y, size, color, weight, align, alpha) {
    g.save(); g.globalAlpha = alpha === undefined ? 1 : alpha; g.fillStyle = color || C.white; g.font = `${weight || 500} ${size}px Inter`; g.textAlign = align || 'left'; g.textBaseline = 'alphabetic'; g.fillText(s, x, y); g.restore();
  }
  function wrapText(s, x, y, maxW, size, lh, color, weight, alpha) {
    g.save(); g.font = `${weight || 400} ${size}px Inter`; const words = s.split(' '); let line = '', yy = y;
    g.globalAlpha = alpha === undefined ? 1 : alpha; g.fillStyle = color || C.text;
    for (const w of words) { const t = line ? line + ' ' + w : w; if (g.measureText(t).width > maxW && line) { g.fillText(line, x, yy); line = w; yy += lh; } else line = t; }
    if (line) g.fillText(line, x, yy); g.restore(); return yy;
  }
  function rrect(x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
  function panel(x, y, w, h, alpha) { g.save(); g.globalAlpha = alpha === undefined ? 1 : alpha; rrect(x, y, w, h, 18); g.fillStyle = 'rgba(8,18,32,0.78)'; g.fill(); g.strokeStyle = 'rgba(56,182,255,0.35)'; g.lineWidth = 1.5; g.stroke(); g.restore(); }
  function arrow(x1, y1, x2, y2, color, w, head, alpha) {
    const a = Math.atan2(y2 - y1, x2 - x1), L = Math.hypot(x2 - x1, y2 - y1); if (L < 1) return; head = Math.min(head || 16, L * 0.6);
    g.save(); g.globalAlpha = alpha === undefined ? 1 : alpha; g.strokeStyle = color; g.fillStyle = color; g.lineWidth = w || 4; g.lineCap = 'round';
    g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2 - Math.cos(a) * head * 0.8, y2 - Math.sin(a) * head * 0.8); g.stroke();
    g.beginPath(); g.moveTo(x2, y2); g.lineTo(x2 - head * Math.cos(a - 0.45), y2 - head * Math.sin(a - 0.45)); g.lineTo(x2 - head * Math.cos(a + 0.45), y2 - head * Math.sin(a + 0.45)); g.closePath(); g.fill(); g.restore();
  }
  function curSym(x, y, r, i, color, alpha) { // ⊙ (i>0, toward viewer) / ⊗ (i<0)
    const m = Math.abs(i); if (m < 0.04) return; g.save(); g.globalAlpha = (alpha === undefined ? 1 : alpha) * clamp(0.25 + m, 0, 1);
    g.beginPath(); g.arc(x, y, r, 0, TAU); g.fillStyle = 'rgba(5,11,20,0.85)'; g.fill(); g.lineWidth = 2.5; g.strokeStyle = color; g.stroke();
    g.fillStyle = color; g.strokeStyle = color;
    if (i > 0) { g.beginPath(); g.arc(x, y, r * 0.3, 0, TAU); g.fill(); }
    else { const k = r * 0.5; g.lineWidth = 3; g.beginPath(); g.moveTo(x - k, y - k); g.lineTo(x + k, y + k); g.moveTo(x + k, y - k); g.lineTo(x - k, y + k); g.stroke(); }
    g.restore();
  }
  function glowCircle(x, y, r, color, a) { g.save(); const gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, color); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.globalAlpha = a; g.fillStyle = gr; g.beginPath(); g.arc(x, y, r, 0, TAU); g.fill(); g.restore(); }

  // ----------------- stator cross-section -----------------
  // belts: phase k positive side centred at electrical angle thk+90°, negative at thk-90°, thk = k*120°
  function slotCurrent(phiE, ia) { // returns [phase, signedCurrent]
    let best = null;
    for (let k = 0; k < 3; k++) for (const sg of [1, -1]) {
      const c = k * 120 * D + sg * 90 * D; const d = Math.abs(wrap(phiE - c));
      if (d <= 30 * D + 1e-6 && !best) best = [k, sg * ia[k]];
    }
    return best;
  }
  function drawStator(cx, cy, Ro, Ri, nSlots, p, ia, opt) {
    opt = opt || {};
    // yoke
    g.save();
    const gr = g.createRadialGradient(cx, cy, Ri, cx, cy, Ro); gr.addColorStop(0, '#6b7782'); gr.addColorStop(0.5, '#56616c'); gr.addColorStop(1, '#3a444e');
    g.beginPath(); g.arc(cx, cy, Ro, 0, TAU); g.arc(cx, cy, Ri, 0, TAU, true); g.fillStyle = gr; g.fill('evenodd');
    // lamination hint rings
    g.strokeStyle = 'rgba(255,255,255,0.05)'; g.lineWidth = 1; for (let r = Ri + 120; r < Ro; r += 9) { g.beginPath(); g.arc(cx, cy, r, 0, TAU); g.stroke(); }
    g.strokeStyle = 'rgba(160,190,220,0.6)'; g.lineWidth = 2; g.beginPath(); g.arc(cx, cy, Ro, 0, TAU); g.stroke();
    // slots
    const sd = opt.slotDepth || 70, sw = opt.slotW || 26;
    for (let k = 0; k < nSlots; k++) {
      const a = (k + 0.5) / nSlots * TAU; const [k3, cur] = slotCurrent(wrap(p * a), ia);
      g.save(); g.translate(...P(cx, cy, Ri + sd / 2 + 4, a)); g.rotate(-a);
      rrect(-sd / 2, -sw / 2, sd, sw, 5); g.fillStyle = '#0b141e'; g.fill();
      rrect(-sd / 2 + 6, -sw / 2 + 3, sd - 12, sw - 6, 4); g.fillStyle = opt.copperA ? `rgba(196,106,56,${opt.copperA})` : '#8a4a28'; g.fill();
      g.restore();
      if (!opt.noSym) { const [x, y] = P(cx, cy, Ri + sd / 2 + 4, a); curSym(x, y, Math.min(13, sw * 0.5), cur, PH[k3], opt.symA); }
    }
    g.restore();
  }
  // airgap field glow on the stator bore
  function boreGlow(cx, cy, Ri, p, thE, amp, labels) {
    if (amp <= 0.01) return;
    const n = 180; g.save(); g.lineWidth = 16; g.lineCap = 'butt';
    for (let i = 0; i < n; i++) {
      const a0 = i / n * TAU, a1 = (i + 1.1) / n * TAU, br = Math.cos(p * (a0 + a1) / 2 - thE);
      g.globalAlpha = amp * Math.abs(br) * 0.9; g.strokeStyle = br > 0 ? C.S : C.N;
      g.beginPath(); g.arc(cx, cy, Ri + 8, -a1, -a0); g.stroke();
    }
    g.restore();
    if (labels) for (let k = 0; k < 2 * p; k++) {
      const a = (thE + k * Math.PI) / p; const isS = k % 2 === 0; const [x, y] = P(cx, cy, Ri + 46, a);
      g.save(); g.globalAlpha = amp; g.beginPath(); g.arc(x, y, 24, 0, TAU); g.fillStyle = isS ? C.S : C.N; g.fill();
      g.fillStyle = '#fff'; g.font = '800 26px Inter'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(isS ? 'S' : 'N', x, y + 1); g.restore();
    }
  }
  // flux lines inside the bore: stream function psi = (r/R)^p sin(p*phi - thE)
  function fluxLines(cx, cy, R, p, thE, amp, t, color) {
    if (amp <= 0.01) return;
    const levels = [0.1, 0.32, 0.56, 0.8]; g.save(); g.lineWidth = 2.6; g.lineCap = 'round';
    for (const c0 of levels) for (const sg of [1, -1]) {
      const c = c0 * sg; let seg = [];
      const segs = [];
      for (let i = 0; i <= 720; i++) {
        const phi = i / 720 * TAU; const s = Math.sin(p * phi - thE);
        const q = c / s; if (q > 0 && q <= 1) { const r = R * Math.pow(q, 1 / p); seg.push([phi, r]); } else { if (seg.length > 2) segs.push(seg); seg = []; }
      }
      if (seg.length > 2) segs.push(seg);
      for (const s of segs) {
        // orient from N (Br<0) to S (Br>0)
        const brStart = Math.cos(p * s[0][0] - thE); const pts = brStart < 0 ? s : s.slice().reverse();
        g.beginPath(); pts.forEach(([phi, r], i) => { const [x, y] = P(cx, cy, r, phi); i ? g.lineTo(x, y) : g.moveTo(x, y); });
        g.globalAlpha = amp * 0.55; g.strokeStyle = color || 'rgba(140,210,255,1)'; g.setLineDash([]); g.stroke();
        g.globalAlpha = amp * 0.95; g.strokeStyle = '#d9f1ff'; g.setLineDash([10, 26]); g.lineDashOffset = -t * 60; g.stroke();
      }
    }
    g.setLineDash([]); g.restore();
  }
  // squirrel cage rotor (cross-section)
  function drawCageRotor(cx, cy, R, nBars, th, barI, forceA, mark) {
    g.save();
    const gr = g.createRadialGradient(cx - R * 0.3, cy - R * 0.3, 10, cx, cy, R); gr.addColorStop(0, '#7d8994'); gr.addColorStop(1, '#46515b');
    g.beginPath(); g.arc(cx, cy, R, 0, TAU); g.fillStyle = gr; g.fill(); g.strokeStyle = 'rgba(190,210,230,0.7)'; g.lineWidth = 2; g.stroke();
    // shaft
    g.beginPath(); g.arc(cx, cy, R * 0.26, 0, TAU); g.fillStyle = '#c3c9d0'; g.fill(); g.strokeStyle = '#2b333b'; g.lineWidth = 3; g.stroke();
    // reference mark (key) so rotation is visible
    if (mark !== false) { g.save(); g.translate(cx, cy); g.rotate(-th); g.fillStyle = '#ffffff'; g.fillRect(R * 0.05, -6, R * 0.21, 12); g.fillStyle = C.amber; g.beginPath(); g.arc(R * 0.62, 0, 9, 0, TAU); g.fill(); g.restore(); }
    for (let k = 0; k < nBars; k++) {
      const a = th + k / nBars * TAU; const [x, y] = P(cx, cy, R - 24, a); const i = barI ? barI(a) : 0;
      g.beginPath(); g.arc(x, y, 15, 0, TAU); g.fillStyle = '#c9ced4'; g.fill(); g.strokeStyle = '#2b333b'; g.lineWidth = 2; g.stroke();
      if (Math.abs(i) > 0.04) { glowCircle(x, y, 34, i > 0 ? 'rgba(255,170,80,0.9)' : 'rgba(255,170,80,0.9)', Math.min(0.8, Math.abs(i) * 0.8)); curSym(x, y, 12, i, C.amber); }
      if (forceA && Math.abs(i) > 0.06) { // tangential force (CCW)
        const f = forceA(a); if (f > 0.03) { const tx = -Math.sin(a), ty = -Math.cos(a); const L = 18 + 55 * f; const [x0, y0] = P(cx, cy, R + 2, a); arrow(x0, y0, x0 + tx * L, y0 + ty * L, C.green, 4, 13); }
      }
    }
    g.restore();
  }
  // salient-pole rotor (4 poles)
  function drawSalientRotor(cx, cy, R, th, exc, damperI, polesGlow) {
    g.save();
    for (let k = 0; k < 4; k++) {
      const a = th + k * Math.PI / 2; const isN = k % 2 === 0;
      g.save(); g.translate(cx, cy); g.rotate(-a);
      // pole body
      const bodyW = 96, r0 = 70, r1 = R - 52;
      g.fillStyle = '#6c7884'; g.fillRect(r0, -bodyW / 2, r1 - r0, bodyW);
      // field coils (copper) on both sides
      g.fillStyle = '#b8642f'; g.fillRect(r0 + 10, -bodyW / 2 - 30, r1 - r0 - 18, 28); g.fillRect(r0 + 10, bodyW / 2 + 2, r1 - r0 - 18, 28);
      g.strokeStyle = 'rgba(0,0,0,0.35)'; g.lineWidth = 1; for (let i = 1; i < 6; i++) { const x = r0 + 10 + i * (r1 - r0 - 18) / 6; g.beginPath(); g.moveTo(x, -bodyW / 2 - 30); g.lineTo(x, -bodyW / 2 - 2); g.moveTo(x, bodyW / 2 + 2); g.lineTo(x, bodyW / 2 + 30); g.stroke(); }
      // pole shoe
      const half = 34 * D; g.beginPath(); g.arc(0, 0, R, -half, half); g.arc(0, 0, r1 - 2, half * 0.8, -half * 0.8, true); g.closePath();
      const gr = g.createLinearGradient(r1, 0, R, 0); gr.addColorStop(0, '#5f6b77'); gr.addColorStop(1, '#8996a3'); g.fillStyle = gr; g.fill(); g.strokeStyle = 'rgba(190,210,230,0.7)'; g.lineWidth = 2; g.stroke();
      g.restore();
      // coil current symbols (DC): one side out, other side in; N poles vs S poles reversed
      if (exc > 0.02) {
        const sgn = isN ? 1 : -1; const rm = (70 + R - 52) / 2 + 4;
        const off = (96 / 2 + 16) / rm; // angular offset of coil sides
        const [x1, y1] = P(cx, cy, rm, a + off), [x2, y2] = P(cx, cy, rm, a - off);
        curSym(x1, y1, 11, sgn * exc, C.amber); curSym(x2, y2, 11, -sgn * exc, C.amber);
      }
      // damper bars
      for (let j = -2; j <= 2; j++) {
        const ab = a + j * 12 * D; const [x, y] = P(cx, cy, R - 14, ab); const i = damperI ? damperI(ab) : 0;
        g.beginPath(); g.arc(x, y, 8, 0, TAU); g.fillStyle = '#d0874f'; g.fill(); g.strokeStyle = '#2b333b'; g.lineWidth = 1.5; g.stroke();
        if (Math.abs(i) > 0.05) { glowCircle(x, y, 26, 'rgba(255,170,80,0.9)', Math.min(0.85, Math.abs(i))); }
      }
      // pole polarity
      if (exc > 0.02) {
        const [x, y] = P(cx, cy, R - 42, a); glowCircle(x, y, 90, isN ? 'rgba(255,79,79,0.9)' : 'rgba(47,139,255,0.9)', 0.45 * exc * (polesGlow === undefined ? 1 : polesGlow));
        g.save(); g.globalAlpha = exc; g.beginPath(); g.arc(x, y, 21, 0, TAU); g.fillStyle = isN ? C.N : C.S; g.fill(); g.fillStyle = '#fff'; g.font = '800 23px Inter'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(isN ? 'N' : 'S', x, y + 1); g.restore();
      }
    }
    // hub + shaft + mark
    g.beginPath(); g.arc(cx, cy, 78, 0, TAU); g.fillStyle = '#56616c'; g.fill();
    g.beginPath(); g.arc(cx, cy, 46, 0, TAU); g.fillStyle = '#c3c9d0'; g.fill(); g.strokeStyle = '#2b333b'; g.lineWidth = 3; g.stroke();
    g.save(); g.translate(cx, cy); g.rotate(-th - Math.PI / 4); g.fillStyle = '#fff'; g.fillRect(4, -5, 38, 10); g.restore();
    g.restore();
  }

  // ----------------- gauges / plots -----------------
  function dial(x, y, r, ang, label, color, value, sub) {
    g.save();
    g.beginPath(); g.arc(x, y, r, 0, TAU); g.fillStyle = 'rgba(8,18,32,0.9)'; g.fill(); g.strokeStyle = 'rgba(56,182,255,0.35)'; g.lineWidth = 2; g.stroke();
    for (let i = 0; i < 24; i++) { const a = i / 24 * TAU; const [x1, y1] = P(x, y, r - 6, a), [x2, y2] = P(x, y, r - (i % 6 === 0 ? 20 : 12), a); g.strokeStyle = 'rgba(160,190,220,0.5)'; g.lineWidth = i % 6 === 0 ? 3 : 1.5; g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2, y2); g.stroke(); }
    const [nx, ny] = P(x, y, r - 26, ang); g.strokeStyle = color; g.lineWidth = 7; g.lineCap = 'round'; g.beginPath(); g.moveTo(x, y); g.lineTo(nx, ny); g.stroke();
    g.beginPath(); g.arc(nx, ny, 9, 0, TAU); g.fillStyle = color; g.fill(); g.beginPath(); g.arc(x, y, 9, 0, TAU); g.fillStyle = '#d8e3ee'; g.fill();
    g.restore();
    txt(label, x, y + r + 40, 22, C.text, 600, 'center');
    if (value) txt(value, x, y + r + 74, 30, color, 800, 'center');
    if (sub) txt(sub, x, y + r + 104, 18, C.muted, 500, 'center');
  }
  function waves(x, y, w, h, thE, alphaK, title) {
    panel(x, y, w, h);
    if (title) txt(title, x + 22, y + 34, 18, C.muted, 700);
    const x0 = x + 22, x1 = x + w - 22, ym = y + h / 2 + 12, A = h / 2 - 38;
    g.strokeStyle = 'rgba(160,190,220,0.25)'; g.lineWidth = 1; g.beginPath(); g.moveTo(x0, ym); g.lineTo(x1, ym); g.stroke();
    const span = 2 * TAU; const cur = (thE % span + span) % span;
    for (let k = 0; k < 3; k++) {
      g.save(); g.globalAlpha = alphaK ? alphaK[k] : 1; g.strokeStyle = PH[k]; g.lineWidth = 3.5; g.beginPath();
      for (let i = 0; i <= 300; i++) { const e = i / 300 * span; const v = Math.cos(e - k * 120 * D); const px = x0 + (x1 - x0) * i / 300, py = ym - v * A; i ? g.lineTo(px, py) : g.moveTo(px, py); }
      g.stroke();
      const v = Math.cos(cur - k * 120 * D); const px = x0 + (x1 - x0) * cur / span; g.beginPath(); g.arc(px, ym - v * A, 7, 0, TAU); g.fillStyle = PH[k]; g.fill(); g.restore();
    }
    const px = x0 + (x1 - x0) * cur / span; g.strokeStyle = 'rgba(255,255,255,0.6)'; g.lineWidth = 2; g.beginPath(); g.moveTo(px, y + 46); g.lineTo(px, y + h - 12); g.stroke();
    ['L1', 'L2', 'L3'].forEach((l, k) => txt(l, x + w - 150 + k * 46, y + 34, 18, PH[k], 800, 'left', alphaK ? Math.max(0.3, alphaK[k]) : 1));
  }
  function stepPanel(x, y, w, steps, idx, u, title) {
    // header
    txt(title, x, y, 20, C.accent, 800);
    const st = steps[idx]; const a = ease(u / 0.5);
    txt(`STEP ${idx + 1} / ${steps.length}`, x, y + 56, 20, C.muted, 700, 'left', a);
    let yy = wrapText(st.t, x, y + 112, w, 44, 52, '#fff', 800, a);
    wrapText(st.d, x, yy + 54, w, 27, 38, C.text, 400, a);
    // progress pips
    for (let i = 0; i < steps.length; i++) { g.beginPath(); g.arc(x + 9 + i * 30, y + 26 + 0, 0, 0, 0); g.fillStyle = i <= idx ? C.accent : 'rgba(111,138,166,0.4)'; rrect(x + i * 34, y + 18, 26, 6, 3); g.fill(); }
  }
  function legend(x, y, items) {
    let xx = x;
    items.forEach(it => {
      if (it.sym !== undefined) { curSym(xx + 12, y - 8, 12, it.sym, it.color); xx += 34; }
      else { g.beginPath(); g.arc(xx + 12, y - 8, 11, 0, TAU); g.fillStyle = it.color; g.fill(); xx += 32; }
      txt(it.label, xx, y, 19, C.text, 500); g.font = '500 19px Inter'; xx += g.measureText(it.label).width + 34;
    });
  }
  function scheduleIdx(steps, t) { let acc = 0; for (let i = 0; i < steps.length; i++) { if (t < acc + steps[i].dur) return [i, t - acc]; acc += steps[i].dur; } return [steps.length - 1, steps[steps.length - 1].dur]; }
  const total = steps => steps.reduce((a, s) => a + s.dur, 0);

  // =====================================================================
  //  SCENE 1: ROTATING MAGNETIC FIELD (2-pole, three concentrated coils)
  // =====================================================================
  function sceneRMF() {
    const steps = [
      { dur: 6.5, t: 'One coil, one AC current', d: 'Alternating current flows back and forth. Coil L1 makes a magnetic field that grows, shrinks and flips – but it does not rotate.' },
      { dur: 6.5, t: 'Add two more coils', d: 'Coils L2 and L3 sit 120° apart. Their currents peak one-third of a cycle later, then two-thirds later.' },
      { dur: 9, t: 'The fields add up and ROTATE', d: 'Added together, the three pulsing fields form ONE field of constant strength that turns smoothly around the stator.' },
      { dur: 8, t: 'A magnet inside follows it', d: 'Place a magnet (or a rotor) in the middle and the rotating field drags it round – with no moving contacts at all.' },
    ];
    const cx = 600, cy = 560, Ro = 400, Ri = 250; const fE = 0.33; // visual electrical Hz
    return {
      duration: total(steps), frame(t) {
        bg(); const [idx, u] = scheduleIdx(steps, t); const thE = TAU * fE * t;
        const on = [1, idx >= 1 ? ease((t - steps[0].dur) / 1.2) : 0, idx >= 1 ? ease((t - steps[0].dur - 0.6) / 1.2) : 0];
        const ia = [0, 1, 2].map(k => on[k] * Math.cos(thE - k * 120 * D));
        // stator ring
        const gr = g.createRadialGradient(cx, cy, Ri, cx, cy, Ro); gr.addColorStop(0, '#6b7782'); gr.addColorStop(1, '#3a444e');
        g.beginPath(); g.arc(cx, cy, Ro, 0, TAU); g.arc(cx, cy, Ri, 0, TAU, true); g.fillStyle = gr; g.fill('evenodd');
        g.strokeStyle = 'rgba(160,190,220,0.6)'; g.lineWidth = 2; g.beginPath(); g.arc(cx, cy, Ro, 0, TAU); g.stroke();
        // coils: phase k axis at k*120°, coil sides at axis±90°
        for (let k = 0; k < 3; k++) {
          const ax = k * 120 * D; const alpha = 0.25 + 0.75 * on[k];
          for (const sg of [1, -1]) {
            const a = ax + sg * 90 * D; const [x, y] = P(cx, cy, Ri + 40, a);
            g.save(); g.globalAlpha = alpha; g.translate(x, y); g.rotate(-a); rrect(-34, -26, 68, 52, 10); g.fillStyle = '#0b141e'; g.fill(); rrect(-28, -20, 56, 40, 8); g.fillStyle = PH[k]; g.globalAlpha = alpha * 0.35; g.fill(); g.restore();
            curSym(x, y, 17, sg * ia[k], PH[k], 0.3 + 0.7 * on[k]);
            const [lx, ly] = P(cx, cy, Ro + 34, a); txt(`L${k + 1}${sg > 0 ? '' : '′'}`, lx, ly + 8, 22, PH[k], 800, 'center', alpha);
          }
        }
        // individual phase field arrows + resultant
        const sc = 150; let bx = 0, by = 0;
        for (let k = 0; k < 3; k++) { const ax = k * 120 * D; const m = ia[k]; bx += m * Math.cos(ax); by += m * Math.sin(ax); if (on[k] > 0.02) arrow(cx, cy, cx + sc * m * Math.cos(ax), cy - sc * m * Math.sin(ax), PH[k], 6, 18, 0.9 * on[k]); }
        const showRes = idx >= 2 ? ease((t - steps[0].dur - steps[1].dur) / 1.0) : 0;
        if (showRes > 0) {
          // trace circle
          g.save(); g.globalAlpha = 0.35 * showRes; g.setLineDash([8, 10]); g.strokeStyle = '#fff'; g.lineWidth = 2; g.beginPath(); g.arc(cx, cy, sc * 1.5, 0, TAU); g.stroke(); g.restore();
          arrow(cx, cy, cx + sc * bx, cy - sc * by, '#ffffff', 11, 30, showRes * (idx >= 3 ? 1 - 0.6 * ease(u / 1.0) : 1));
          const [lx, ly] = [cx + sc * bx * 1.18, cy - sc * by * 1.18]; txt('Resultant field', lx, ly, 20, '#fff', 700, 'center', showRes * 0.9);
        }
        // compass magnet following the field in step 4
        if (idx >= 3) {
          const a = ease((u) / 1.0); const ang = Math.atan2(by, bx);
          g.save(); g.globalAlpha = a; g.translate(cx, cy); g.rotate(-ang);
          g.fillStyle = C.N; g.beginPath(); g.moveTo(110, 0); g.lineTo(0, -20); g.lineTo(0, 20); g.fill();
          g.fillStyle = C.S; g.beginPath(); g.moveTo(-110, 0); g.lineTo(0, -20); g.lineTo(0, 20); g.fill();
          g.fillStyle = '#fff'; g.font = '800 22px Inter'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('N', 55, 1); g.fillText('S', -55, 1);
          g.beginPath(); g.arc(0, 0, 8, 0, TAU); g.fillStyle = '#d8e3ee'; g.fill(); g.restore();
        }
        // right panel
        stepPanel(1150, 120, 680, steps, idx, u, 'THE ROTATING MAGNETIC FIELD');
        waves(1150, 600, 680, 250, thE, on, 'THREE-PHASE CURRENTS');
        legend(1150, 935, [{ sym: 1, color: '#d8e3ee', label: 'current toward you' }, { sym: -1, color: '#d8e3ee', label: 'current away from you' }]);
        txt('The field turns at SYNCHRONOUS SPEED:', 1150, 985, 20, C.muted, 700); txt('50 Hz supply → 3000 rpm (2 poles) · 1500 rpm (4 poles)', 1150, 1015, 20, C.muted, 500);
      }
    };
  }

  // =====================================================================
  //  SCENE 2: INDUCTION MOTOR (4-pole field, squirrel cage)
  // =====================================================================
  function sceneInduction() {
    const steps = [
      { dur: 5, t: 'Three-phase AC enters the stator', d: 'The supply feeds the three groups of stator coils. Each current rises and falls a little after the previous one.' },
      { dur: 6, t: 'A rotating magnetic field appears', d: 'Together the coils create North and South poles that travel around the stator – the rotor is still standing still.' },
      { dur: 6, t: 'The field sweeps across the rotor bars', d: 'As the moving field cuts through the bars it INDUCES a voltage, and current flows round the closed cage – no wires connected.' },
      { dur: 5, t: 'The rotor becomes a magnet', d: 'These induced currents create the rotor’s own magnetic poles, sitting just behind the stator poles.' },
      { dur: 5, t: 'Magnetic pull creates torque', d: 'The stator poles drag the rotor poles along. Every bar feels a force in the direction the field is turning.' },
      { dur: 7, t: 'The rotor accelerates', d: 'The rotor speeds up and chases the rotating field. (In a real motor this whole start takes only seconds.)' },
      { dur: 8, t: 'Running: always slightly slower', d: 'At normal running the rotor turns a little slower than the field. This small difference is called SLIP.' },
      { dur: 9, t: 'Why can’t it catch up?', d: 'If the rotor matched the field speed, the field would no longer cut the bars: no induced current, no torque – so it falls back again.' },
    ];
    const cx = 600, cy = 560, Ro = 420, Ri = 262, Rr = 254, p = 2, nBars = 28;
    const ws = TAU * 0.2; // field mechanical rad/s (visual)
    const sm = 0.5, Tm = 1.6, J = 1.2; const kloss = s => s <= 0 ? -2 * Tm / (Math.abs(s) / sm + sm / Math.max(1e-6, Math.abs(s))) * (s < 0 ? 1 : 0) : 2 * Tm / (s / sm + sm / s);
    const sRun = 0.08; const TL = kloss(sRun);
    const T0 = steps.slice(0, 5).reduce((a, s) => a + s.dur, 0); // rotor released
    const T7 = steps.slice(0, 7).reduce((a, s) => a + s.dur, 0);
    let sim = { t: 0, th: 0, w: 0 };
    function simulate(tt) {
      if (tt < sim.t) sim = { t: 0, th: 0, w: 0 };
      const dt = 1 / 400;
      while (sim.t < tt) {
        const t = sim.t; let w = sim.w;
        if (t >= T0) {
          const s = 1 - w / ws; const Te = kloss(Math.max(1e-4, s)) * (s > 0 ? 1 : -1);
          const load = TL * ease((t - T0) / 2);
          if (t > T7 + 1.2 && t < T7 + 4.8) { // hypothetical: rotor pushed up to field speed
            const target = ws; w += (target - w) * Math.min(1, dt * 3.0);
          } else w += (Te - load) / J * dt;
        }
        sim.th += w * dt; sim.w = w; sim.t += dt;
      }
      return sim;
    }
    return {
      duration: total(steps), frame(t) {
        bg(); const [idx, u] = scheduleIdx(steps, t); const st = simulate(t);
        const supply = ease(t / 1.5);
        const thM = ws * t; const thE = p * thM; // electrical field angle
        const ia = [0, 1, 2].map(k => supply * Math.cos(thE - k * 120 * D));
        const fieldA = idx >= 1 ? ease((t - steps[0].dur) / 1.5) : 0;
        const s = 1 - st.w / ws;
        const lag = Math.atan(2.2 * Math.max(0, s));
        const induced = idx >= 2 ? ease((t - steps[0].dur - steps[1].dur) / 1.5) : 0;
        const barScale = clamp(s / 0.25, 0, 1) * 0.85 + (s > 0.02 ? 0.15 : s / 0.02 * 0.15);
        const barI = a => induced * barScale * Math.cos(p * a - thE + lag) * (s > 0 ? 1 : 0);
        const forceOn = idx >= 4 ? ease((t - T0 + steps[4].dur) / 1.2) : 0;
        const forceA = a => forceOn * barScale * Math.max(0, Math.cos(p * a - thE + lag) * Math.cos(p * a - thE)) * 1.2;

        drawStator(cx, cy, Ro, Ri, 36, p, ia, { slotDepth: 74, slotW: 24, symA: 0.4 + 0.6 * supply });
        boreGlow(cx, cy, Ri, p, thE, fieldA, true);
        drawCageRotor(cx, cy, Rr, nBars, st.th, barI, forceA);
        fluxLines(cx, cy, Rr - 6, p, thE, fieldA * 0.85, t);
        // rotor poles (from induced currents): rotor N at stator-S angle - (90°-lag)/p ... shown from step 4
        const rp = idx >= 3 ? ease((t - steps.slice(0, 3).reduce((a, s) => a + s.dur, 0)) / 1.2) * clamp(barScale * 1.3, 0, 1) : 0;
        if (rp > 0.02) for (let k = 0; k < 2 * p; k++) {
          const aS = (thE + k * Math.PI) / p; const isRotorN = k % 2 === 0; // rotor N trails stator S
          const a = aS - (Math.PI / 2 + lag) / p; const [x, y] = P(cx, cy, Rr - 80, a);
          glowCircle(x, y, 70, isRotorN ? 'rgba(255,79,79,0.9)' : 'rgba(47,139,255,0.9)', 0.35 * rp);
          g.save(); g.globalAlpha = rp; g.beginPath(); g.arc(x, y, 17, 0, TAU); g.strokeStyle = isRotorN ? C.N : C.S; g.lineWidth = 3; g.fillStyle = 'rgba(5,11,20,0.8)'; g.fill(); g.stroke(); g.fillStyle = isRotorN ? '#ff9a9a' : '#9cc8ff'; g.font = '800 19px Inter'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(isRotorN ? 'n' : 's', x, y + 1); g.restore();
        }
        // field direction arrow around stator
        if (fieldA > 0.05) { g.save(); g.globalAlpha = fieldA * 0.8; g.strokeStyle = C.accent; g.lineWidth = 4; const a0 = 25 * D; g.beginPath(); g.arc(cx, cy, Ro + 30, -(a0 + 0.9), -a0, false); g.stroke(); const [hx, hy] = P(cx, cy, Ro + 30, a0 + 0.9); const tx = -Math.sin(a0 + 0.9), ty = -Math.cos(a0 + 0.9); arrow(hx - tx * 2, hy - ty * 2, hx + tx * 16, hy + ty * 16, C.accent, 4, 18); g.restore(); txt('field rotation', ...P(cx, cy, Ro + 64, a0 + 0.45), 18, C.accent, 700, 'center', fieldA); }

        stepPanel(1150, 110, 690, steps, idx, u, 'INDUCTION MOTOR · HOW IT WORKS');
        // dials
        const dy = 720; const showD = idx >= 1 ? 1 : 0.35;
        dial(1290, dy, 105, thM, 'Magnetic field', C.accent, '100 %', 'synchronous speed');
        const pct = Math.round(100 * st.w / ws);
        dial(1590, dy, 105, st.th, 'Rotor', C.amber, `${pct} %`, idx >= 6 ? `slip ≈ ${Math.max(0, 100 - pct)} %` : 'of field speed');
        if (idx >= 6) txt('Slip exaggerated for visibility – real motors: about 1–5 %', 1150, 1035, 19, C.muted, 500);
        legend(60, 1040, [{ color: C.N, label: 'N pole' }, { color: C.S, label: 'S pole' }, { sym: 1, color: C.amber, label: 'induced current toward you' }, { sym: -1, color: C.amber, label: 'away' }, { color: C.green, label: 'force on bar' }]);
        if (idx === 7 && t > T7 + 1.2 && t < T7 + 5.2) { panel(330, 70, 560, 70, 0.95); txt('Imagine: rotor at field speed → current = 0', 610, 115, 24, '#fff', 700, 'center'); }
      }
    };
  }

  // =====================================================================
  //  SCENE 3: SYNCHRONOUS MOTOR (4-pole salient, damper start, DC excitation)
  // =====================================================================
  function sceneSync() {
    const steps = [
      { dur: 5.5, t: 'Three-phase AC → rotating field', d: 'Exactly as in the induction motor, the stator creates a magnetic field that rotates at synchronous speed.' },
      { dur: 7.5, t: 'Why it cannot start by itself', d: 'Give the stationary rotor DC poles: the field races past so fast that each pole is pulled forward, then backward. The rotor only shakes.' },
      { dur: 8, t: 'Starting: the damper bars', d: 'With the DC switched off, the damper bars work like an induction cage. The rotor accelerates to just below synchronous speed.' },
      { dur: 6, t: 'DC excitation switched on', d: 'Now DC flows into the field winding: each rotor pole becomes a fixed North or South electromagnet.' },
      { dur: 7, t: 'Magnetic locking – pull-in', d: 'Each rotor pole is attracted to an opposite stator pole and is pulled into step with the rotating field.' },
      { dur: 7, t: 'Locked: exactly the same speed', d: 'Rotor and field now turn together at synchronous speed. Slip = 0, so the damper bars carry no current.' },
      { dur: 8, t: 'Under load: same speed, small angle', d: 'More load makes the rotor poles trail a little further behind (the load angle) – but the speed stays exactly synchronous.' },
    ];
    const cx = 600, cy = 560, Ro = 420, Ri = 262, Rr = 256, p = 2;
    const ws = TAU * 0.2; const Ts = 1.0, Kd = 0.9, J = 0.32;
    const tA = steps[0].dur, tB = tA + steps[1].dur, tC = tB + steps[2].dur, tD = tC + steps[3].dur, tE = tD + steps[4].dur, tF = tE + steps[5].dur;
    let sim = { t: 0, th: 0, w: 0 };
    const stDir = thE => thE / p; // angle of stator S pole (k=0)
    function exc(t) { if (t >= tA + 0.6 && t < tB - 0.6) return ease((t - tA - 0.6) / 0.6) * (1 - ease((t - tB + 1.4) / 0.6)); if (t >= tC + 0.8) return ease((t - tC - 0.8) / 1.0); return 0; }
    function load(t) { return t < tF ? 0.12 : 0.12 + 0.48 * ease((t - tF - 0.8) / 2.5); }
    function simulate(tt) {
      if (tt < sim.t) sim = { t: 0, th: 0, w: 0 };
      const dt = 1 / 500;
      while (sim.t < tt) {
        const t = sim.t; const thE = p * ws * t; const e = exc(t);
        if (t < tB) { // rotor held by heavy coupled load: show small jiggle only
          const dE = wrap(thE + 0 - p * (sim.th0 || 0)); const Jb = 6.0;
          const Tq = Ts * e * Math.sin(wrap(p * (stDir(thE) + Math.PI / 2 * 0) - p * sim.th));
          sim.w += (Tq - 0.6 * sim.w * Jb) / Jb * dt;
        } else {
          const dE = wrap(thE - p * sim.th); // electrical angle by which stator S leads rotor N
          const Tsync = Ts * e * Math.sin(dE);
          const Tdamp = Math.min(Kd * (ws - sim.w), 0.2);
          sim.w += (Tsync + Tdamp - load(t)) / J * dt;
        }
        sim.th += sim.w * dt; sim.t += dt;
      }
      return sim;
    }
    return {
      duration: total(steps), frame(t) {
        bg(); const [idx, u] = scheduleIdx(steps, t); const st = simulate(t);
        const supply = ease(t / 1.5); const thM = ws * t, thE = p * thM;
        const ia = [0, 1, 2].map(k => supply * Math.cos(thE - k * 120 * D));
        const e = exc(t); const s = 1 - st.w / ws; const dE = wrap(thE - p * st.th);
        drawStator(cx, cy, Ro, Ri, 36, p, ia, { slotDepth: 74, slotW: 24, symA: 0.4 + 0.6 * supply });
        boreGlow(cx, cy, Ri, p, thE, ease(t / 2), true);
        const dampOn = (t >= tB) ? clamp(Math.abs(s) / 0.15, 0, 1) : 0;
        const damperI = a => dampOn * Math.cos(p * a - thE);
        drawSalientRotor(cx, cy, Rr, st.th, e, damperI, 1);
        fluxLines(cx, cy, Rr - 8, p, thE, 0.55 * ease(t / 2), t);
        // torque arrows in step 2 (alternating)
        if (idx === 1 && e > 0.1) {
          const Tq = Math.sin(wrap(thE - p * st.th)); const a = st.th; const dir = Tq > 0 ? 1 : -1;
          for (let k = 0; k < 4; k++) { const ak = a + k * Math.PI / 2; const [x0, y0] = P(cx, cy, Rr + 0, ak); const tx = -Math.sin(ak) * dir, ty = -Math.cos(ak) * dir; arrow(x0, y0, x0 + tx * 60 * Math.abs(Tq), y0 + ty * 60 * Math.abs(Tq), Tq > 0 ? C.green : '#ff7b7b', 5, 14, e); }
          panel(360, 70, 480, 66, 0.95); txt(Tq > 0 ? 'pulled forward…' : '…pulled backward', 600, 113, 26, Tq > 0 ? C.green : '#ff9b9b', 800, 'center');
        }
        // magnetic lock "springs" + load angle
        if (t >= tD - 1.5 && e > 0.5) {
          const a = ease((t - tD + 1.5) / 1.5);
          for (let k = 0; k < 2; k++) {
            const aS = (thE + k * TAU) / p; const aN = st.th + k * Math.PI;
            const [x1, y1] = P(cx, cy, Ri + 10, aS), [x2, y2] = P(cx, cy, Rr - 30, aN);
            g.save(); g.globalAlpha = 0.85 * a; g.strokeStyle = '#ffffff'; g.lineWidth = 3; g.setLineDash([6, 8]); g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2, y2); g.stroke(); g.restore();
          }
          if (idx >= 6) { // load angle arc on k=0
            const aS = thE / p, aN = st.th; const al = ease((t - tF) / 1.5);
            g.save(); g.globalAlpha = al; g.strokeStyle = C.amber; g.lineWidth = 6; g.beginPath(); g.arc(cx, cy, Rr + 20, -aS, -aN); g.stroke(); g.restore();
            const [lx, ly] = P(cx, cy, Rr + 120, (aS + aN) / 2); txt(`load angle δ = ${Math.round(Math.abs(dE) / D)}° el.`, lx, ly, 24, C.amber, 800, 'center', al);
          }
        }
        stepPanel(1150, 110, 690, steps, idx, u, 'SYNCHRONOUS MOTOR · HOW IT WORKS');
        const dy = 720; const pct = Math.round(100 * st.w / ws);
        dial(1290, dy, 105, thM, 'Magnetic field', C.accent, '100 %', 'synchronous speed');
        const locked = t > tE - 1 && Math.abs(s) < 0.004;
        dial(1590, dy, 105, st.th, 'Rotor', locked ? C.green : C.amber, `${clamp(pct, 0, 100)} %`, locked ? 'LOCKED · slip = 0' : (idx >= 2 ? `slip ≈ ${Math.max(0, 100 - pct)} %` : 'of field speed'));
        // excitation indicator
        panel(1150, 945, 330, 60); g.beginPath(); g.arc(1180, 975, 11, 0, TAU); g.fillStyle = e > 0.5 ? C.amber : '#33414f'; g.fill(); txt(`DC excitation: ${e > 0.5 ? 'ON' : 'OFF'}`, 1202, 983, 22, e > 0.5 ? C.amber : C.muted, 700);
        if (idx >= 2 && idx <= 4) txt('Slip exaggerated for visibility', 1510, 983, 19, C.muted, 500);
        legend(60, 1040, [{ color: C.N, label: 'N pole' }, { color: C.S, label: 'S pole' }, { sym: 1, color: C.amber, label: 'DC field current' }, { color: '#d0874f', label: 'damper bar' }]);
      }
    };
  }

  // =====================================================================
  //  SCENE 4: SPEED COMPARISON LOOP (for GIF) – induction vs synchronous
  // =====================================================================
  function sceneDials(opts) {
    const dur = 20; const wF = TAU * 0.25, wI = TAU * 0.2; // 5 vs 4 turns in 20 s => seamless loop
    return {
      duration: dur, frame(t) {
        g.clearRect(0, 0, W, H); if (!opts.transparent) { g.fillStyle = '#0b1a2c'; g.fillRect(0, 0, W, H); }
        const cols = [[W * 0.25, 'INDUCTION', wI, C.amber, 'rotor slightly slower'], [W * 0.75, 'SYNCHRONOUS', wF, C.green, 'rotor exactly in step']];
        cols.forEach(([x, name, wr, col, sub]) => {
          const y = H * 0.48, r = H * 0.3;
          g.beginPath(); g.arc(x, y, r, 0, TAU); g.fillStyle = 'rgba(8,18,32,0.95)'; g.fill(); g.strokeStyle = 'rgba(56,182,255,0.45)'; g.lineWidth = 3; g.stroke();
          for (let i = 0; i < 24; i++) { const a = i / 24 * TAU; const [x1, y1] = P(x, y, r - 6, a), [x2, y2] = P(x, y, r - (i % 6 === 0 ? 22 : 12), a); g.strokeStyle = 'rgba(160,190,220,0.5)'; g.lineWidth = i % 6 ? 1.5 : 3; g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2, y2); g.stroke(); }
          const af = wF * t, ar = wr * t;
          const [fx, fy] = P(x, y, r - 30, af); g.strokeStyle = C.accent; g.lineWidth = 9; g.lineCap = 'round'; g.beginPath(); g.moveTo(x, y); g.lineTo(fx, fy); g.stroke(); g.beginPath(); g.arc(fx, fy, 11, 0, TAU); g.fillStyle = C.accent; g.fill();
          const [rx, ry] = P(x, y, r - 62, ar); g.strokeStyle = col; g.lineWidth = 9; g.beginPath(); g.moveTo(x, y); g.lineTo(rx, ry); g.stroke(); g.beginPath(); g.arc(rx, ry, 11, 0, TAU); g.fillStyle = col; g.fill();
          g.beginPath(); g.arc(x, y, 10, 0, TAU); g.fillStyle = '#d8e3ee'; g.fill();
          txt(name, x, H * 0.08 + 10, H * 0.06, '#fff', 800, 'center');
          txt(sub, x, H * 0.93, H * 0.045, col, 700, 'center');
        });
        // legend centre
        const lx = W * 0.5, ly = H * 0.42;
        g.strokeStyle = C.accent; g.lineWidth = 8; g.beginPath(); g.moveTo(lx - 60, ly); g.lineTo(lx - 20, ly); g.stroke(); txt('field', lx - 10, ly + 9, H * 0.04, C.text, 600);
        g.strokeStyle = C.amber; g.beginPath(); g.moveTo(lx - 60, ly + 60); g.lineTo(lx - 40, ly + 60); g.stroke(); g.strokeStyle = C.green; g.beginPath(); g.moveTo(lx - 40, ly + 60); g.lineTo(lx - 20, ly + 60); g.stroke(); txt('(slip exaggerated)', lx + 40, ly + 140, H * 0.03, C.muted, 500, 'center'); txt('rotor', lx - 10, ly + 69, H * 0.04, C.text, 600);
      }
    };
  }

  window.ANIM = {
    init, make(kind, opts) {
      return { rmf: sceneRMF, induction: sceneInduction, sync: sceneSync, dials: () => sceneDials(opts || {}) }[kind]();
    }
  };
})();
