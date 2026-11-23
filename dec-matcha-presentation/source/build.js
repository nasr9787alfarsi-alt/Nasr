// Dec Matcha — cinematic rebuild. Content strings are copied verbatim from the original deck.
const pptxgen = require("pptxgenjs");
const React = require("react");
const RDS = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const fs = require("fs");
const path = require("path");

const A = (f) => path.join(__dirname, "assets", f);
const LOGO = process.argv[2];
const OUT = process.argv[3] || "deck.pptx";

const C = {
  ink: "0B1610", panel: "132519", panel2: "1A3022", line: "2E4A33",
  matcha: "9DBF5E", matchaL: "C9DE8F", cream: "F2EEE3", muted: "A9B8A2",
  gold: "D8B56A", deep: "2F4A26", face: "0F1E14",
};
const H = "Cambria", B = "Calibri";
const SPEC = { slides: [] };

async function icon(Comp, color = "#0B1610") {
  const svg = RDS.renderToStaticMarkup(React.createElement(Comp, { color, size: 256 }));
  const buf = await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

// ------------------------------------------------------------ helpers
const shadow = () => ({ type: "outer", color: "000000", blur: 12, offset: 4, angle: 90, opacity: 0.45 });

function card(s, name, x, y, w, h, o = {}) {
  s.addShape("roundRect", {
    objectName: name, x, y, w, h, rectRadius: o.r ?? 0.1,
    fill: { color: o.fill ?? C.panel, transparency: o.tr ?? 0 },
    line: { color: o.line ?? C.line, width: o.lw ?? 0.75 },
    shadow: o.noShadow ? undefined : shadow(),
  });
}
function txt(s, name, text, x, y, w, h, o = {}) {
  s.addText(text, Object.assign({
    objectName: name, x, y, w, h, margin: 0, isTextBox: true, fontFace: B,
    fontSize: 11, color: C.cream, valign: "top",
  }, o));
}
function label(s, name, text, x, y, w, o = {}) {
  txt(s, name, text, x, y, w, 0.22, Object.assign({ fontSize: 7.5, bold: true, color: C.gold, charSpacing: 2.5 }, o));
}
function medal(s, name, x, y, d, img, o = {}) {
  s.addShape("ellipse", { objectName: "medal " + name, x, y, w: d, h: d, fill: { color: o.fill ?? C.matcha }, line: { color: o.line ?? C.matchaL, width: 0.75 }, shadow: shadow() });
  const k = d * 0.5;
  s.addImage({ objectName: "icon " + name, data: img, x: x + (d - k) / 2, y: y + (d - k) / 2, w: k, h: k, altText: "Icon " + name });
  return ["medal " + name, "icon " + name];
}
const LEAF_AR = 256 / 272; // h / w of leafA
function leaves(s, a, b) {
  s.addImage({ objectName: "!!leafB", path: A("leafB.png"), x: b[0], y: b[1], w: b[2], h: b[2] * LEAF_AR, rotate: b[3], altText: "Decorative blurred matcha leaf" });
  s.addImage({ objectName: "!!leafA", path: A("leafA.png"), x: a[0], y: a[1], w: a[2], h: a[2] * LEAF_AR, rotate: a[3], altText: "Decorative matcha leaf" });
}
function bokeh(s, dx, dy) {
  s.addImage({ objectName: "!!bokeh", path: A("bokeh.png"), x: -0.3 + dx, y: -0.35 + dy, w: 11.5, h: 6.5, altText: "Decorative light particles" });
}
function orb(s, x, y, w) {
  s.addImage({ objectName: "!!orb", path: A("orb.png"), x, y, w, h: w, altText: "Matcha bowl seen from above" });
}
function ring(s, x, y, w) {
  s.addShape("ellipse", { objectName: "!!ring", x, y, w, h: w, fill: { type: "none" }, line: { color: C.gold, width: 1, dashType: "sysDash", transparency: 30 } });
}
function header(s, num, title) {
  txt(s, "!!secnum", num, 0.5, 0.33, 0.8, 0.62, { fontFace: H, fontSize: 30, bold: true, color: C.gold, valign: "middle" });
  s.addText(title, { placeholder: "title" });
}
// count-up frames: values from 0 → target, ease-out; final frame carries the real text.
function easeVals(n) { const a = []; for (let i = 0; i < n; i++) { const t = i / n; a.push(1 - Math.pow(1 - t, 3)); } return a; }
function counter(s, base, finalText, fmt, box, style, n = 10) {
  const names = [];
  easeVals(n).forEach((f, i) => {
    const nm = `${base} counter frame ${i + 1}`;
    txt(s, nm, fmt(f), box.x, box.y, box.w, box.h, Object.assign({}, style));
    names.push(nm);
  });
  txt(s, base, finalText, box.x, box.y, box.w, box.h, Object.assign({}, style, { fill: { color: box.fill } }));
  return { frames: names, final: base };
}
const omr = (v) => "OMR " + Math.round(v).toLocaleString("en-US");

(async () => {
  const I = {
    leaf: await icon(fa.FaLeaf), handshake: await icon(fa.FaHandshake), mug: await icon(fa.FaMugHot),
    users: await icon(fa.FaUsers), pin: await icon(fa.FaMapMarkerAlt), heart: await icon(fa.FaHeart),
    exchange: await icon(fa.FaExchangeAlt), plan: await icon(fa.FaClipboardCheck), tag: await icon(fa.FaTag),
    horn: await icon(fa.FaBullhorn), coins: await icon(fa.FaCoins), boxes: await icon(fa.FaBoxes),
    friends: await icon(fa.FaUserFriends), check: await icon(fa.FaCheck), crown: await icon(fa.FaChessKing),
  };

  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.title = "Dec Matcha";
  pres.theme = { headFontFace: H, bodyFontFace: B };

  pres.defineSlideMaster({ title: "COVER", background: { color: C.ink }, objects: [] });
  pres.defineSlideMaster({
    title: "CONTENT", background: { color: C.ink },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 1.3, y: 0.33, w: 6.9, h: 0.62, fontFace: H, fontSize: 26, color: C.cream, valign: "middle", align: "left", margin: 0 }, text: "" } },
      { text: { text: "DEC MATCHA", options: { x: 0.5, y: 5.2, w: 2.0, h: 0.25, margin: 0, fontFace: B, fontSize: 7.5, bold: true, charSpacing: 3, color: C.muted } } },
    ],
    slideNumber: { x: 9.0, y: 5.2, w: 0.5, h: 0.25, fontFace: B, fontSize: 8, color: C.muted, align: "right", margin: 0 },
  });

  // =================================================================== 1 — cover
  {
    const s = pres.addSlide({ masterName: "COVER" });
    s.background = { path: A("bg1.jpg") };
    bokeh(s, 0, 0);
    orb(s, 1.35, 1.5, 2.6);
    s.addShape("ellipse", { objectName: "!!plate", x: 0.65, y: 0.8, w: 4.0, h: 4.0, fill: { color: C.cream }, line: { color: "FFFFFF", width: 1.5, transparency: 40 }, shadow: { type: "outer", color: "000000", blur: 30, offset: 8, angle: 90, opacity: 0.6 } });
    ring(s, 0.45, 0.6, 4.4);
    s.addImage({ objectName: "!!logo", path: LOGO, x: 1.1, y: 1.5, w: 3.1, h: 3.1 * 782 / 936, altText: "Dec Matcha logo: matcha bowl with a leaf" });
    txt(s, "Cover title", "DEC MATCHA", 5.2, 0.7, 4.4, 0.8, { fontFace: H, fontSize: 40, bold: true, charSpacing: 4, color: C.cream, valign: "middle" });
    txt(s, "Cover subtitle", "BUSINESS PLAN  |  INTRODUCTION TO BUSINESS (BSIB1101)", 5.2, 1.5, 4.4, 0.3, { fontSize: 9, bold: true, color: C.gold, charSpacing: 1 });
    label(s, "Members label", "GROUP MEMBERS", 5.2, 2.05, 3, { color: C.muted, charSpacing: 3 });
    const M = [["Deema Zaid Al Moharbi", "21J25117"], ["Taqwa Abdullah Al-Hashami", "21S2452"], ["Nardeen Mansoor Al-Farsi", "21J2583"], ["Mais Shaikhan Al-Toubi", "31J2573"], ["Dhoha Talal Al-Hinai", "21S246"]];
    const mem = [];
    M.forEach(([n, id], i) => {
      const y = 2.35 + i * 0.56;
      card(s, `Member card ${i + 1}`, 5.2, y, 4.3, 0.46, { tr: 15, r: 0.08 });
      s.addShape("ellipse", { objectName: `Member dot ${i + 1}`, x: 5.38, y: y + 0.18, w: 0.1, h: 0.1, fill: { color: C.matcha }, line: { type: "none" } });
      txt(s, `Member name ${i + 1}`, n, 5.62, y, 2.6, 0.46, { fontSize: 11.5, bold: true, valign: "middle" });
      txt(s, `Member ID ${i + 1}`, id, 8.15, y, 1.15, 0.46, { fontSize: 9, color: C.muted, align: "right", valign: "middle", charSpacing: 1 });
      mem.push([`Member card ${i + 1}`, `Member dot ${i + 1}`, `Member name ${i + 1}`, `Member ID ${i + 1}`]);
    });
    leaves(s, [4.45, 0.25, 0.6, 15], [-0.55, 4.3, 1.7, -25]);
    const fx = [
      { type: "zoom", names: ["!!plate"], at: 0, dur: 1100, from: 0.6, sound: { kind: "boom", vol: 0.9 } },
      { type: "fade", names: ["!!logo"], at: 500, dur: 900 },
      { type: "zoom", names: ["!!logo"], at: 500, dur: 900, from: 0.85, noFade: true },
      { type: "fade", names: ["!!ring"], at: 900, dur: 900 },
      { type: "spin", names: ["!!ring"], at: 900, dur: 60000 },
      { type: "letters", names: ["Cover title"], at: 900, dur: 500, step: 70 },
      { type: "rise", names: ["Cover subtitle"], at: 1500, dur: 700 },
      { type: "fade", names: ["Members label"], at: 1800, dur: 600 },
      ...mem.map((g, i) => ({ type: "emergeX", names: g, at: 1950 + i * 130, dur: 700, dx: 0.06 })),
      { type: "float", names: ["!!leafA"], at: 0, dur: 3200, dy: -0.012 },
    ];
    SPEC.slides.push({ n: 1, transition: "fade", effects: fx, tilt: { "!!orb": 52 } });
  }

  // =================================================================== 2 — business background (hub & spokes)
  {
    const s = pres.addSlide({ masterName: "CONTENT" });
    s.background = { path: A("bg2.jpg") };
    bokeh(s, -0.25, 0.05);
    header(s, "01", "Business Background");
    // spokes
    const cy = [1.25, 2.5, 3.75].map((y) => y + 0.525);
    const spokes = [];
    cy.forEach((y, i) => {
      const dy = (y - 2.9);
      const ang = Math.atan2(dy, 1.5);
      const ex = 5.0 - 1.15 * Math.cos(ang), ey = 2.9 + 1.15 * Math.sin(ang);
      s.addShape("line", { objectName: `Spoke L${i}`, x: 3.5, y: Math.min(y, ey), w: ex - 3.5, h: Math.max(Math.abs(ey - y), 0.001), line: { color: C.gold, width: 0.75, transparency: 45 }, flipV: ey < y });
      const ex2 = 5.0 + 1.15 * Math.cos(ang);
      s.addShape("line", { objectName: `Spoke R${i}`, x: ex2, y: Math.min(y, ey), w: 6.5 - ex2, h: Math.max(Math.abs(ey - y), 0.001), line: { color: C.gold, width: 0.75, transparency: 45 }, flipV: ey > y });
      spokes.push(`Spoke L${i}`, `Spoke R${i}`);
    });
    ring(s, 3.65, 1.55, 2.7);
    orb(s, 3.85, 1.75, 2.3);
    const items = [
      ["BUSINESS NAME", "Dec Matcha", "Named after December, the month the café opened", I.leaf],
      ["FORM OF BUSINESS", "Partnership", null, I.handshake],
      ["ACTIVITY", "A café that sells matcha drinks and small desserts", null, I.mug],
      ["OWNERSHIP", "Five partners will run the café together", null, I.users],
      ["LOCATION", "Nizwa, Al Dakhiliyah, Oman", null, I.pin],
      ["GOAL", "Good matcha, kind service, and fair prices", null, I.heart],
    ];
    const groups = [];
    items.forEach(([lab, val, sub, ic], i) => {
      const col = i < 3 ? 0 : 1, row = i % 3;
      const x = col ? 6.5 : 0.45, y = 1.25 + row * 1.25;
      const g = [];
      card(s, `Card ${lab}`, x, y, 3.05, 1.05, { tr: 10 }); g.push(`Card ${lab}`);
      g.push(...medal(s, lab, x + 0.18, y + 0.29, 0.46, ic));
      label(s, `Label ${lab}`, lab, x + 0.8, y + 0.14, 2.1); g.push(`Label ${lab}`);
      const big = val.length < 20;
      txt(s, `Value ${lab}`, val, x + 0.8, y + 0.36, 2.15, sub ? 0.3 : 0.58, { fontSize: big ? 14 : 11.5, bold: true, fontFace: big ? H : B }); g.push(`Value ${lab}`);
      if (sub) { txt(s, `Note ${lab}`, sub, x + 0.8, y + 0.66, 2.15, 0.34, { fontSize: 8.5, italic: true, color: C.muted }); g.push(`Note ${lab}`); }
      groups.push({ g, col });
    });
    leaves(s, [8.95, 0.3, 0.5, 40], [-0.75, 4.55, 1.6, 10]);
    const fx = [
      { type: "spin", names: ["!!orb"], at: 0, dur: 40000 },
      { type: "spin", names: ["!!ring"], at: 0, dur: 60000, rev: true },
      ...spokes.map((n, i) => ({ type: "wipe", dir: n.includes("L") ? "right" : "left", names: [n], at: 100 + (i >> 1) * 120, dur: 600 })),
      ...groups.map(({ g, col }, i) => ({ type: "emerge", names: g, at: 500 + (i % 3) * 180 + col * 90, dur: 800, fx: 0.5, fy: 0.52 })),
      { type: "float", names: ["!!leafA"], at: 0, dur: 3400, dy: -0.012 },
    ];
    SPEC.slides.push({ n: 2, transition: "morph", tsound: { kind: "whoosh", vol: 1.0 }, effects: fx });
  }

  // =================================================================== 3 — target market (radar)
  {
    const s = pres.addSlide({ masterName: "CONTENT" });
    s.background = { path: A("bg3.jpg") };
    bokeh(s, -0.5, -0.05);
    header(s, "02", "Target Market & Competition");
    card(s, "Hero card", 0.5, 1.2, 4.4, 2.75, { fill: C.panel });
    label(s, "Main customers label", "MAIN CUSTOMERS", 0.75, 1.42, 3);
    const k = counter(s, "Age range", "18–30", (f) => `${Math.round(18 * f)}–${Math.round(30 * f)}`, { x: 0.72, y: 1.66, w: 3.9, h: 1.15, fill: C.panel }, { fontFace: H, fontSize: 72, bold: true, color: C.matchaL, valign: "middle" });
    txt(s, "Customers", "University students and young adults", 0.75, 2.95, 3.95, 0.35, { fontSize: 14, bold: true });
    txt(s, "Also welcome", "We also welcome matcha lovers and café visitors.", 0.75, 3.33, 3.95, 0.4, { fontSize: 10.5, color: C.muted });

    label(s, "Competitors label", "COMPETITORS IN NIZWA", 5.4, 1.08, 3);
    ring(s, 5.675, 1.35, 2.65);
    s.addImage({ objectName: "Radar", path: A("radar.png"), x: 5.725, y: 1.4, w: 2.55, h: 2.55, altText: "Radar showing competitors" });
    s.addImage({ objectName: "Radar sweep", path: A("sweep.png"), x: 5.725, y: 1.4, w: 2.55, h: 2.55, altText: "Radar sweep" });
    orb(s, 6.69, 2.365, 0.62);
    const comp = [["Drisha", 6.33, 1.98], ["Fusul Cafe", 7.82, 2.3], ["Rive", 6.72, 3.33]];
    const cg = [];
    comp.forEach(([n, x, y], i) => {
      s.addShape("ellipse", { objectName: `Comp halo ${i}`, x: x - 0.1, y: y - 0.1, w: 0.34, h: 0.34, fill: { color: C.gold, transparency: 70 }, line: { type: "none" } });
      s.addShape("ellipse", { objectName: `Comp dot ${i}`, x: x, y: y, w: 0.14, h: 0.14, fill: { color: C.gold }, line: { color: "FFF4D6", width: 0.75 } });
      txt(s, `Comp ${n}`, n, x + 0.25, y - 0.09, 1.2, 0.3, { fontSize: 11, bold: true, valign: "middle" });
      cg.push([`Comp halo ${i}`, `Comp dot ${i}`, `Comp ${n}`]);
    });
    label(s, "Difference label", "OUR DIFFERENCE", 0.5, 4.13, 3);
    const diffs = ["More matcha choices", "Oat milk", "Student offers", "A calm place"];
    const dg = [];
    diffs.forEach((d, i) => {
      const x = 0.5 + i * 2.3;
      card(s, `Diff card ${i}`, x, 4.38, 2.1, 0.5, { tr: 10, r: 0.25 });
      s.addShape("ellipse", { objectName: `Check ${i}`, x: x + 0.12, y: 4.48, w: 0.3, h: 0.3, fill: { color: C.matcha }, line: { type: "none" } });
      s.addImage({ objectName: `Check icon ${i}`, data: I.check, x: x + 0.195, y: 4.555, w: 0.15, h: 0.15, altText: "Check" });
      txt(s, `Diff ${i}`, d, x + 0.52, 4.38, 1.5, 0.5, { fontSize: 11, bold: true, valign: "middle" });
      dg.push([`Diff card ${i}`, `Check ${i}`, `Check icon ${i}`, `Diff ${i}`]);
    });
    leaves(s, [8.95, 0.25, 0.5, 110], [9.3, 2.75, 1.5, -40]);
    const fx = [
      { type: "spin", names: ["!!ring"], at: 0, dur: 60000 },
      { type: "zoom", names: ["Hero card"], at: 0, dur: 700, from: 0.92 },
      { type: "fade", names: ["Main customers label"], at: 300, dur: 500 },
      { type: "counter", frames: k.frames, final: k.final, at: 450, step: 80, sound: { vol: 0.8 } },
      { type: "rise", names: ["Customers"], at: 1250, dur: 600 },
      { type: "rise", names: ["Also welcome"], at: 1400, dur: 600 },
      { type: "zoom", names: ["Radar"], at: 200, dur: 900, from: 0.6 },
      { type: "fade", names: ["Competitors label"], at: 400, dur: 600 },
      { type: "fade", names: ["Radar sweep"], at: 900, dur: 400 },
      { type: "spin", names: ["Radar sweep"], at: 900, dur: 4000 },
      { type: "spin", names: ["!!orb"], at: 0, dur: 30000 },
      ...cg.map((g, i) => ({ type: "pop", names: g, at: 1200 + i * 330, dur: 450, sound: { kind: "ping", vol: 0.6 } })),
      { type: "fade", names: ["Difference label"], at: 2000, dur: 500 },
      ...dg.map((g, i) => ({ type: "rise", names: g, at: 2100 + i * 140, dur: 600 })),
      { type: "float", names: ["!!leafA"], at: 0, dur: 3000, dy: -0.012 },
    ];
    SPEC.slides.push({ n: 3, transition: "morph", tsound: { kind: "whoosh", vol: 1.0 }, effects: fx, text3d: [k.final] });
  }

  // =================================================================== 4 — macro-economics (gauge)
  {
    const s = pres.addSlide({ masterName: "CONTENT" });
    s.background = { path: A("bg4.jpg") };
    bokeh(s, -0.75, 0.05);
    header(s, "03", "Macro-Economic Factors");
    s.addImage({ objectName: "Gauge", path: A("gauge.png"), x: 0.5, y: 1.15, w: 3.8, h: 3.8, altText: "Gauge dial for inflation" });
    s.addImage({ objectName: "Needle", path: A("needle.png"), x: 0.5, y: 1.15, w: 3.8, h: 3.8, rotate: 303.3, altText: "Gauge needle" });
    orb(s, 2.09, 2.74, 0.62);
    const k = counter(s, "Inflation value", "2.9%", (f) => `${(2.9 * f).toFixed(1)}%`, { x: 1.6, y: 3.38, w: 1.6, h: 0.62, fill: C.face }, { fontFace: H, fontSize: 38, bold: true, color: C.cream, align: "center", valign: "middle" }, 12);

    txt(s, "Inflation title", "Inflation", 5.0, 1.2, 4.4, 0.4, { fontFace: H, fontSize: 20, bold: true, color: C.matchaL });
    txt(s, "Inflation text", "Higher prices for matcha, milk, cups, and rent can increase our costs.", 5.0, 1.62, 4.4, 0.45, { fontSize: 11.5 });
    txt(s, "Inflation source", "NCSI, Oman, October 2026", 5.0, 2.08, 4.4, 0.22, { fontSize: 8.5, italic: true, color: C.muted });
    const cards = [["Exchange rates", "Changes may make imported matcha powder cost more.", I.exchange, C.panel, 2.55], ["Our plan", "Compare suppliers and avoid wasting ingredients.", I.plan, C.deep, 3.8]];
    const cg = [];
    cards.forEach(([t, b, ic, fill, y]) => {
      const g = [];
      card(s, `Card ${t}`, 5.0, y, 4.5, 1.05, { fill, tr: 5 }); g.push(`Card ${t}`);
      g.push(...medal(s, t, 5.2, y + 0.29, 0.46, ic));
      txt(s, `Title ${t}`, t, 5.85, y + 0.17, 3.45, 0.32, { fontSize: 14, bold: true }); g.push(`Title ${t}`);
      txt(s, `Body ${t}`, b, 5.85, y + 0.5, 3.45, 0.45, { fontSize: 11, color: C.muted }); g.push(`Body ${t}`);
      cg.push(g);
    });
    leaves(s, [9.05, 0.3, 0.5, 160], [-0.9, 4.2, 1.6, 30]);
    const fx = [
      { type: "zoom", names: ["Gauge"], at: 0, dur: 800, from: 0.8 },
      { type: "rotby", names: ["Needle"], at: 0, dur: 1, by: -78.3, hidden: true },
      { type: "fade", names: ["Needle"], at: 500, dur: 300 },
      { type: "rotby", names: ["Needle"], at: 600, dur: 1300, by: 78.3, decel: true, sound: { kind: "servo", sec: 1.3, vol: 0.8 } },
      { type: "counter", frames: k.frames, final: k.final, at: 600, step: 108 },
      { type: "spin", names: ["!!orb"], at: 0, dur: 30000 },
      { type: "rise", names: ["Inflation title"], at: 900, dur: 600 },
      { type: "rise", names: ["Inflation text"], at: 1050, dur: 600 },
      { type: "fade", names: ["Inflation source"], at: 1300, dur: 600 },
      ...cg.map((g, i) => ({ type: "emergeX", names: g, at: 1700 + i * 300, dur: 800, dx: 0.08 })),
      { type: "float", names: ["!!leafA"], at: 0, dur: 3600, dy: -0.012 },
    ];
    SPEC.slides.push({ n: 4, transition: "morph", tsound: { kind: "whoosh", vol: 1.0 }, effects: fx, text3d: [k.final] });
  }

  // =================================================================== 5 — 4 Ps (quadrants around the bowl)
  {
    const s = pres.addSlide({ masterName: "CONTENT" });
    s.background = { path: A("bg5.jpg") };
    bokeh(s, -1.0, 0.0);
    header(s, "04", "Marketing Mix – The 4 Ps");
    const P = [
      ["Product", "Hot and iced matcha, strawberry matcha, vanilla matcha, and light desserts", I.mug, 0.5, 1.15, C.panel],
      ["Price", "Proposed drink prices from OMR 1.500 to OMR 2.000", I.tag, 5.3, 1.15, C.deep],
      ["Place", "An accessible café in Nizwa, with takeaway and online orders", I.pin, 0.5, 3.15, C.panel],
      ["Promotion", "Instagram, TikTok, student discounts, opening offers, and loyalty cards", I.horn, 5.3, 3.15, C.panel],
    ];
    const pg = [];
    P.forEach(([t, b, ic, x, y, fill]) => {
      const g = [];
      card(s, `Card ${t}`, x, y, 4.2, 1.8, { fill, tr: 5, r: 0.12 }); g.push(`Card ${t}`);
      g.push(...medal(s, t, x + 0.35, y + 0.3, 0.52, ic));
      txt(s, `Title ${t}`, t, x + 1.05, y + 0.3, 2.8, 0.52, { fontFace: H, fontSize: 20, bold: true, valign: "middle" }); g.push(`Title ${t}`);
      txt(s, `Body ${t}`, b, x + 0.35, y + 0.98, 3.65, 0.62, { fontSize: 12, color: "DCE3D4" }); g.push(`Body ${t}`);
      pg.push(g);
    });
    ring(s, 4.35, 2.4, 1.3);
    orb(s, 4.5, 2.55, 1.0);
    leaves(s, [9.15, 0.3, 0.45, 200], [4.3, 4.98, 1.4, 0]);
    const fx = [
      { type: "spin", names: ["!!orb"], at: 0, dur: 30000 },
      { type: "spin", names: ["!!ring"], at: 0, dur: 60000, rev: true },
      ...pg.map((g, i) => ({ type: "emerge", names: g, at: 150 + i * 220, dur: 900, fx: 0.5, fy: 0.54 })),
      { type: "float", names: ["!!leafA"], at: 0, dur: 3300, dy: -0.012 },
    ];
    SPEC.slides.push({ n: 5, transition: "morph", tsound: { kind: "whoosh", vol: 1.0 }, effects: fx });
  }

  // =================================================================== 6 — human resources (org chart)
  {
    const s = pres.addSlide({ masterName: "CONTENT" });
    s.background = { path: A("bg6.jpg") };
    bokeh(s, -1.25, 0.1);
    header(s, "05", "Human Resources");
    orb(s, 8.75, 0.3, 0.62);
    card(s, "GM card", 3.4, 1.12, 3.2, 0.8, { fill: C.matcha, line: C.matchaL, r: 0.12 });
    txt(s, "GM title", "GENERAL MANAGER", 3.4, 1.2, 3.2, 0.35, { fontSize: 13, bold: true, color: C.ink, align: "center", charSpacing: 1.5, valign: "middle" });
    txt(s, "GM text", "Overall planning and supervision", 3.4, 1.53, 3.2, 0.3, { fontSize: 10, color: "1F3318", align: "center", valign: "middle" });
    const L = { color: C.gold, width: 1, transparency: 30 };
    s.addShape("line", { objectName: "Trunk", x: 5.0, y: 1.92, w: 0, h: 0.33, line: Object.assign({}, L) });
    s.addShape("line", { objectName: "Branch", x: 1.575, y: 2.25, w: 6.9, h: 0, line: Object.assign({}, L) });
    const roles = [["Marketing Manager", "Advertising", I.horn], ["Finance Manager", "Budget and accounts", I.coins], ["Operations Manager", "Stock and quality", I.boxes], ["HR Manager", "Staff and training", I.friends]];
    const rg = [], drops = [];
    roles.forEach(([t, d, ic], i) => {
      const x = 0.55 + i * 2.3, cx = x + 1.025;
      s.addShape("line", { objectName: `Drop ${i}`, x: cx, y: 2.25, w: 0, h: 0.25, line: Object.assign({}, L) });
      drops.push(`Drop ${i}`);
      const g = [];
      card(s, `Card ${t}`, x, 2.5, 2.05, 1.7, { tr: 5 }); g.push(`Card ${t}`);
      g.push(...medal(s, t, cx - 0.28, 2.7, 0.56, ic));
      txt(s, `Title ${t}`, t, x + 0.1, 3.36, 1.85, 0.35, { fontSize: 12.5, bold: true, align: "center", valign: "middle" }); g.push(`Title ${t}`);
      txt(s, `Duty ${t}`, d, x + 0.1, 3.7, 1.85, 0.3, { fontSize: 10.5, color: C.muted, align: "center", valign: "middle" }); g.push(`Duty ${t}`);
      rg.push(g);
    });
    card(s, "Staff bar", 0.55, 4.45, 8.95, 0.5, { fill: C.panel2, tr: 0, r: 0.25 });
    txt(s, "Staff text", [
      { text: "Additional staff: ", options: { bold: true, color: C.matchaL } },
      { text: "baristas and a cashier/service assistant", options: { color: C.cream } },
    ], 0.55, 4.45, 8.95, 0.5, { fontSize: 11.5, align: "center", valign: "middle" });
    leaves(s, [9.55, 2.0, 0.45, 300], [-0.85, 0.9, 1.6, 60]);
    const fx = [
      { type: "spin", names: ["!!orb"], at: 0, dur: 30000 },
      { type: "drop", names: ["GM card", "GM title", "GM text"], at: 0, dur: 800 },
      { type: "wipe", dir: "top", names: ["Trunk"], at: 700, dur: 300 },
      { type: "barn", names: ["Branch"], at: 950, dur: 600, sound: { kind: "clack", vol: 0.7 } },
      ...drops.map((d, i) => ({ type: "wipe", dir: "top", names: [d], at: 1450, dur: 250 })),
      ...rg.map((g, i) => ({ type: "flip", names: g, at: 1600 + i * 150, dur: 700 })),
      { type: "zoom", names: ["Staff bar", "Staff text"], at: 2400, dur: 700, from: 0.9 },
      { type: "float", names: ["!!leafA"], at: 0, dur: 3500, dy: -0.012 },
    ];
    SPEC.slides.push({ n: 6, transition: "morph", tsound: { kind: "whoosh", vol: 1.0 }, effects: fx });
  }

  // =================================================================== 7 — start-up costs & finance
  {
    const s = pres.addSlide({ masterName: "CONTENT" });
    s.background = { path: A("bg7.jpg") };
    bokeh(s, -1.5, 0.05);
    header(s, "06", "Start-up Costs & Finance");
    card(s, "Total card", 0.5, 1.15, 4.6, 0.85, { fill: C.matcha, line: C.matchaL, r: 0.1 });
    txt(s, "Total label", "TOTAL START-UP BUDGET", 0.72, 1.15, 2.0, 0.85, { fontSize: 9, bold: true, color: C.ink, charSpacing: 1.5, valign: "middle" });
    // digits assemble individually (glyph advances = Cambria Bold metrics), then the editable final value locks in on top
    const MET = JSON.parse(fs.readFileSync(path.join(__dirname, "metrics.json")));
    const TV = "OMR 8,500", FS = 28, right = 2.6 + 2.32;
    const adv = (str) => [...str].reduce((a, ch) => a + MET[ch] * FS / 72, 0);
    const x0 = right - adv(TV);
    const pieces = [[0, "OMR"], [4, "8"], [5, ","], [6, "5"], [7, "0"], [8, "0"]];
    const digitNames = pieces.map(([i, str], j) => {
      const nm = `Total value counter frame digit ${j + 1}`;
      txt(s, nm, str, x0 + adv(TV.slice(0, i)), 1.24, adv(str) + 0.12, 0.66, { fontFace: H, fontSize: FS, bold: true, color: C.ink, valign: "middle", wrap: false });
      return nm;
    });
    txt(s, "Total value", TV, 2.6, 1.24, 2.32, 0.66, { fontFace: H, fontSize: FS, bold: true, color: process.env.DEBUG_DIGITS ? "FF0000" : C.ink, align: "right", valign: "middle", ...(process.env.DEBUG_DIGITS ? {} : { fill: { color: C.matcha } }) });
    const k = { final: "Total value", digits: digitNames };
    // values for frames need scaling: rebuild text via fmt with target
    const costs = [["Rent and setup", "OMR 1,500", 1500], ["Furniture and interior", "OMR 1,800", 1800], ["Equipment", "OMR 2,000", 2000], ["Ingredients and packaging", "OMR 1,000", 1000], ["Other setup costs and working capital", "OMR 2,200", 2200]];
    const bars = [];
    costs.forEach(([l, v, n], i) => {
      const y = 2.2 + i * 0.47;
      txt(s, `Cost label ${i}`, l, 0.5, y, 1.8, 0.4, { fontSize: 9.5, color: "DCE3D4", valign: "middle" });
      s.addShape("roundRect", { objectName: `Track ${i}`, x: 2.4, y: y + 0.12, w: 1.75, h: 0.16, rectRadius: 0.08, fill: { color: "1E3324" }, line: { type: "none" } });
      const w = 1.75 * n / 2200;
      s.addShape("roundRect", { objectName: `Bar ${i}`, x: 2.4, y: y + 0.12, w, h: 0.16, rectRadius: 0.08, fill: { color: i === 4 ? C.gold : C.matcha }, line: { type: "none" } });
      txt(s, `Cost value ${i}`, v, 4.25, y, 0.85, 0.4, { fontSize: 9.5, bold: true, valign: "middle" });
      bars.push(i);
    });
    txt(s, "Estimate note", "These costs are estimates, not final prices.", 0.5, 4.68, 4.6, 0.28, { fontSize: 9, italic: true, color: C.muted });

    label(s, "Finance label", "SOURCES OF FINANCE", 5.45, 1.15, 3);
    ring(s, 5.3, 1.35, 2.8);
    const cx = 6.7, cyy = 2.75, D = 2.5;
    const partAng = 270 + 360 * 6000 / 8500;
    s.addShape("blockArc", { objectName: "Arc partners", x: cx - D / 2, y: cyy - D / 2, w: D, h: D, angleRange: [270, partAng % 360], arcThicknessRatio: 0.22, fill: { color: C.matcha }, line: { type: "none" } });
    s.addShape("blockArc", { objectName: "Arc family", x: cx - D / 2, y: cyy - D / 2, w: D, h: D, angleRange: [partAng % 360, 270], arcThicknessRatio: 0.22, fill: { color: C.gold }, line: { type: "none" } });
    orb(s, 6.0, 2.05, 1.4);
    card(s, "Fin card 1", 8.2, 1.5, 1.3, 1.05, { fill: C.panel });
    card(s, "Fin card 2", 8.2, 2.85, 1.3, 1.05, { fill: C.panel });
    s.addShape("ellipse", { objectName: "Swatch 1", x: 8.33, y: 1.66, w: 0.1, h: 0.1, fill: { color: C.matcha }, line: { type: "none" } });
    s.addShape("ellipse", { objectName: "Swatch 2", x: 8.33, y: 3.01, w: 0.1, h: 0.1, fill: { color: C.gold }, line: { type: "none" } });
    txt(s, "Fin label 1", "PARTNERS’ SAVINGS", 8.48, 1.6, 1.0, 0.36, { fontSize: 7, bold: true, color: C.muted, charSpacing: 1 });
    txt(s, "Fin label 2", "FAMILY INVESTMENT", 8.48, 2.95, 1.0, 0.36, { fontSize: 7, bold: true, color: C.muted, charSpacing: 1 });
    const f1 = counter(s, "Fin value 1", "OMR 6,000", (f) => omr(6000 * f), { x: 8.3, y: 2.0, w: 1.12, h: 0.42, fill: C.panel }, { fontFace: H, fontSize: 16, bold: true, color: C.matchaL, valign: "middle" }, 10);
    const f2 = counter(s, "Fin value 2", "OMR 2,500", (f) => omr(2500 * f), { x: 8.3, y: 3.35, w: 1.12, h: 0.42, fill: C.panel }, { fontFace: H, fontSize: 16, bold: true, color: C.gold, valign: "middle" }, 10);
    leaves(s, [9.1, 4.35, 0.45, 20], [9.0, -0.65, 1.6, -10]);
    const fx = [
      { type: "spin", names: ["!!orb"], at: 0, dur: 30000 },
      { type: "spin", names: ["!!ring"], at: 0, dur: 60000 },
      { type: "zoom", names: ["Total card", "Total label"], at: 0, dur: 700, from: 0.9 },
      { type: "assemble", digits: k.digits, final: k.final, at: 250, step: 110, dur: 450, sound: { vol: 0.85 } },
      ...bars.map((i) => ({ type: "fade", names: [`Cost label ${i}`, `Track ${i}`], at: 600 + i * 120, dur: 500 })),
      ...bars.map((i) => ({ type: "wipe", dir: "left", names: [`Bar ${i}`], at: 900 + i * 120, dur: 800 })),
      ...bars.map((i) => ({ type: "emergeX", names: [`Cost value ${i}`], at: 1450 + i * 120, dur: 500, dx: -0.02 })),
      { type: "fade", names: ["Estimate note"], at: 2300, dur: 600 },
      { type: "fade", names: ["Finance label"], at: 700, dur: 500 },
      { type: "wheel", names: ["Arc partners"], at: 1000, dur: 1100 },
      { type: "wheel", names: ["Arc family"], at: 2000, dur: 600 },
      { type: "emergeX", names: ["Fin card 1", "Swatch 1", "Fin label 1"], at: 1300, dur: 600, dx: 0.04 },
      { type: "counter", frames: f1.frames, final: f1.final, at: 1450, step: 75, sound: { vol: 0.55 } },
      { type: "emergeX", names: ["Fin card 2", "Swatch 2", "Fin label 2"], at: 2000, dur: 600, dx: 0.04 },
      { type: "counter", frames: f2.frames, final: f2.final, at: 2150, step: 75, sound: { vol: 0.55 } },
      { type: "float", names: ["!!leafA"], at: 0, dur: 3100, dy: -0.012 },
    ];
    SPEC.slides.push({ n: 7, transition: "morph", tsound: { kind: "whoosh", vol: 1.0 }, effects: fx, text3d: [k.final] });
  }

  // =================================================================== 8 — references (timeline)
  {
    const s = pres.addSlide({ masterName: "CONTENT" });
    s.background = { path: A("bg8.jpg") };
    bokeh(s, -1.75, 0.0);
    header(s, "07", "References");
    orb(s, 8.75, 0.3, 0.62);
    const refs = [
      ["National Centre for Statistics and Information (NCSI). (18 November 2026). Oman’s inflation rate reaches 2.9% in October 2026.", "https://ncsi.gov.om/newsPage/newsDetail?id=434"],
      ["Times of Oman. (17 November 2026). Oman’s inflation rate reaches 2.9 percent in October 2026.", "https://timesofoman.com/article/179291-omans-inflation-rate-reaches-29-percent-in-october-2026"],
      ["Talabat. (n.d.). Rive menu in Nizwa.", "https://www.talabat.com/oman/restaurant/1116567/rive-nizwa-suq"],
      ["Restaurant Guru. (n.d.). Drisha café listing in Nizwa.", "https://restaurantguru.com/Drisha-Nizwa"],
    ];
    s.addShape("line", { objectName: "Timeline", x: 0.83, y: 1.4, w: 0, h: 2.8, line: { color: C.gold, width: 1, transparency: 35 } });
    const rg = [];
    refs.forEach(([cite, url], i) => {
      const y = 1.15 + i * 0.8;
      s.addShape("ellipse", { objectName: `Node ${i}`, x: 0.65, y: y + 0.18, w: 0.36, h: 0.36, fill: { color: C.matcha }, line: { color: C.matchaL, width: 0.75 }, shadow: shadow() });
      txt(s, `Node num ${i}`, String(i + 1), 0.65, y + 0.18, 0.36, 0.36, { fontSize: 11, bold: true, color: C.ink, align: "center", valign: "middle" });
      card(s, `Ref card ${i}`, 1.3, y, 8.2, 0.72, { tr: 10 });
      txt(s, `Ref ${i}`, cite, 1.48, y + 0.07, 7.85, 0.4, { fontSize: 10, valign: "middle" });
      txt(s, `URL ${i}`, [{ text: url, options: { hyperlink: { url } } }], 1.48, y + 0.47, 7.85, 0.2, { fontSize: 8, color: C.matcha, valign: "middle" });
      rg.push({ node: [`Node ${i}`, `Node num ${i}`], card: [`Ref card ${i}`, `Ref ${i}`, `URL ${i}`] });
    });
    card(s, "Note bar", 1.3, 4.45, 8.2, 0.48, { fill: C.deep, tr: 0, r: 0.24 });
    txt(s, "Note", "Dec Matcha’s drink prices, start-up costs, and sources of finance are the team’s own estimates.", 1.48, 4.45, 7.85, 0.48, { fontSize: 10, italic: true, color: C.matchaL, valign: "middle" });
    leaves(s, [0.3, 4.55, 0.4, 40], [9.45, 1.0, 1.5, 120]);
    const fx = [
      { type: "spin", names: ["!!orb"], at: 0, dur: 30000 },
      { type: "wipe", dir: "top", names: ["Timeline"], at: 0, dur: 2000 },
      ...rg.map((r, i) => ({ type: "pop", names: r.node, at: 150 + i * 480, dur: 400 })),
      ...rg.map((r, i) => ({ type: "emergeX", names: r.card, at: 250 + i * 480, dur: 700, dx: 0.05 })),
      { type: "rise", names: ["Note bar", "Note"], at: 2300, dur: 700 },
      { type: "float", names: ["!!leafA"], at: 0, dur: 3200, dy: -0.012 },
    ];
    SPEC.slides.push({ n: 8, transition: "morph", tsound: { kind: "whoosh", vol: 0.7 }, effects: fx });
  }

  // =================================================================== 9 — thank you
  {
    const s = pres.addSlide({ masterName: "COVER" });
    s.background = { path: A("bg9.jpg") };
    bokeh(s, -2.0, 0.05);
    orb(s, 8.25, 3.25, 3.5);
    s.addShape("ellipse", { objectName: "!!plate", x: 3.55, y: 0.45, w: 2.9, h: 2.9, fill: { color: C.cream }, line: { color: "FFFFFF", width: 1.5, transparency: 40 }, shadow: { type: "outer", color: "000000", blur: 30, offset: 8, angle: 90, opacity: 0.6 } });
    ring(s, 3.35, 0.25, 3.3);
    s.addImage({ objectName: "!!logo", path: LOGO, x: 3.88, y: 0.98, w: 2.24, h: 2.24 * 782 / 936, altText: "Dec Matcha logo: matcha bowl with a leaf" });
    txt(s, "Thanks", "Thank You!", 1.5, 3.45, 7.0, 0.75, { fontFace: H, fontSize: 40, bold: true, align: "center", valign: "middle", color: C.cream });
    txt(s, "Closing", "Dec Matcha aims to bring fresh matcha, good service, and a comfortable café experience to Nizwa.", 1.8, 4.22, 6.4, 0.6, { fontSize: 13, align: "center", color: "DCE3D4" });
    leaves(s, [6.45, 0.4, 0.55, 30], [-0.6, 3.6, 1.8, -20]);
    const fx = [
      { type: "spin", names: ["!!orb"], at: 0, dur: 40000 },
      { type: "spin", names: ["!!ring"], at: 0, dur: 60000 },
      { type: "letters", names: ["Thanks"], at: 200, dur: 500, step: 80, sound: { kind: "boom", vol: 0.8 } },
      { type: "rise", names: ["Closing"], at: 1200, dur: 800 },
      { type: "float", names: ["!!leafA"], at: 0, dur: 3200, dy: -0.012 },
    ];
    SPEC.slides.push({ n: 9, transition: "morph", tsound: { kind: "whoosh", vol: 1.0 }, effects: fx, tilt: { "!!orb": 48 } });
  }

  await pres.writeFile({ fileName: OUT });
  fs.writeFileSync(path.join(path.dirname(path.resolve(OUT)), "spec.json"), JSON.stringify(SPEC, null, 1));
  console.log("wrote", OUT);
})();
