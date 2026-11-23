// Dec Matcha — "Ivory, Forest & Matcha" identity. Content strings are copied verbatim from the original deck.
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

// ------------------------------------------------------------ design tokens
const C = {
  porc: "FAF7F0",   // warm ivory ground
  white: "FFFFFF",  // surfaces
  forest: "1F3A2B", // brand anchor
  sage: "7E9C68",   // secondary
  sageL: "DCE6D3",  // light text on forest
  tint: "EDF2E3",   // emphasis surface (matcha tint)
  beige: "F0E9DA",  // notes surface
  matcha: "8DA65B", // natural matcha — data accents
  gold: "B39257",   // champagne metal — graphics
  goldD: "8E7140",  // champagne — small text on light
  goldL: "D9C79F",  // champagne — small text on forest
  ink: "1F2A23", body: "4A574D", muted: "6B776E", hair: "DDE2D8",
};
const H = "Cambria", B = "Calibri";
const SPEC = { slides: [] };

async function icon(Comp, color) {
  const svg = RDS.renderToStaticMarkup(React.createElement(Comp, { color, size: 256 }));
  const buf = await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

// ------------------------------------------------------------ helpers
const shadow = (o = 0.12, blur = 16) => ({ type: "outer", color: C.forest, blur, offset: 3, angle: 90, opacity: o });

function card(s, name, x, y, w, h, o = {}) {
  s.addShape("roundRect", {
    objectName: name, x, y, w, h, rectRadius: o.r ?? 0.1,
    fill: { color: o.fill ?? C.white },
    line: o.line === null ? { type: "none" } : { color: o.line ?? C.hair, width: 0.75 },
    shadow: o.noShadow ? undefined : shadow(o.so ?? 0.12),
  });
}
function txt(s, name, text, x, y, w, h, o = {}) {
  s.addText(text, Object.assign({
    objectName: name, x, y, w, h, margin: 0, isTextBox: true, fontFace: B,
    fontSize: 12, color: C.ink, valign: "top",
  }, o));
}
function label(s, name, text, x, y, w, o = {}) {
  txt(s, name, text, x, y, w, 0.24, Object.assign({ fontSize: 8.5, bold: true, color: C.goldD, charSpacing: 2.5 }, o));
}
function medal(s, name, x, y, d, img, o = {}) {
  s.addShape("ellipse", { objectName: "medal " + name, x, y, w: d, h: d, fill: { color: o.fill ?? C.forest }, line: { type: "none" }, shadow: shadow(0.18, 8) });
  const k = d * 0.46;
  s.addImage({ objectName: "icon " + name, data: img, x: x + (d - k) / 2, y: y + (d - k) / 2, w: k, h: k, altText: "Icon " + name });
  return ["medal " + name, "icon " + name];
}
const LEAF_AR = 256 / 272;
function leaves(s, a, b) {
  s.addImage({ objectName: "!!leafB", path: A("leafB.png"), x: b[0], y: b[1], w: b[2], h: b[2] * LEAF_AR, rotate: b[3], altText: "Decorative blurred matcha leaf" });
  s.addImage({ objectName: "!!leafA", path: A("leafA.png"), x: a[0], y: a[1], w: a[2], h: a[2] * LEAF_AR, rotate: a[3], altText: "Decorative matcha leaf" });
}
function mist(s, dx, dy) {
  s.addImage({ objectName: "!!bokeh", path: A("bokeh.png"), x: -0.3 + dx, y: -0.35 + dy, w: 13.2, h: 6.6, altText: "Decorative soft light" });
}
function orb(s, x, y, w) {
  s.addImage({ objectName: "!!orb", path: A("orb.png"), x, y, w, h: w, altText: "Matcha bowl seen from above" });
}
function ring(s, x, y, w) {
  s.addShape("ellipse", { objectName: "!!ring", x, y, w, h: w, fill: { type: "none" }, line: { color: C.gold, width: 0.75, dashType: "sysDash", transparency: 25 } });
}
function header(s, num, title) {
  txt(s, "!!secnum", num, 0.5, 0.36, 0.62, 0.6, { fontFace: H, fontSize: 28, bold: true, color: C.gold, valign: "middle" });
  s.addShape("line", { objectName: "!!hair", x: 1.2, y: 0.47, w: 0, h: 0.38, line: { color: C.goldL, width: 1 } });
  s.addText(title, { placeholder: "title" });
}
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
const floatLeaf = (dur) => ({ type: "float", names: ["!!leafA"], at: 0, dur, dy: -0.01 });

(async () => {
  const P = "#FAF7F0";
  const I = {
    leaf: await icon(fa.FaLeaf, P), handshake: await icon(fa.FaHandshake, P), mug: await icon(fa.FaMugHot, P),
    users: await icon(fa.FaUsers, P), pin: await icon(fa.FaMapMarkerAlt, P), heart: await icon(fa.FaHeart, P),
    exchange: await icon(fa.FaExchangeAlt, P), plan: await icon(fa.FaClipboardCheck, P), tag: await icon(fa.FaTag, P),
    horn: await icon(fa.FaBullhorn, P), coins: await icon(fa.FaCoins, P), boxes: await icon(fa.FaBoxes, P),
    friends: await icon(fa.FaUserFriends, P), check: await icon(fa.FaCheck, P),
  };

  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.title = "Dec Matcha";
  pres.theme = { headFontFace: H, bodyFontFace: B };

  pres.defineSlideMaster({ title: "COVER", background: { color: C.porc }, objects: [] });
  pres.defineSlideMaster({
    title: "CONTENT", background: { color: C.porc },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 1.38, y: 0.36, w: 6.9, h: 0.6, fontFace: H, fontSize: 28, color: C.forest, valign: "middle", align: "left", margin: 0 }, text: "" } },
      { image: { path: A("emblem.png"), x: 0.5, y: 5.1, w: 0.27, h: 0.27 * 444 / 378, altText: "Dec Matcha emblem" } },
      { text: { text: "DEC MATCHA", options: { x: 0.86, y: 5.17, w: 2.0, h: 0.22, margin: 0, fontFace: B, fontSize: 7.5, bold: true, charSpacing: 3, color: C.muted, valign: "middle" } } },
    ],
    slideNumber: { x: 9.0, y: 5.17, w: 0.5, h: 0.22, fontFace: B, fontSize: 8, color: C.muted, align: "right", margin: 0 },
  });

  // =================================================================== 1 — cover
  {
    const s = pres.addSlide({ masterName: "COVER" });
    s.background = { path: A("bg1.jpg") };
    s.addImage({ objectName: "!!dunes", path: A("dunes.jpg"), x: 0, y: 0, w: 10, h: 5.625, altText: "Landscape of matcha powder dunes" });
    s.addImage({ objectName: "!!powder", path: A("powder.png"), x: -0.55, y: 0.05, w: 6.2, h: 6.2 * 825 / 1350, altText: "Drifting matcha powder" });
    orb(s, 1.3, 1.65, 2.3);
    s.addShape("ellipse", { objectName: "!!plate", x: 0.6, y: 0.95, w: 3.7, h: 3.7, fill: { color: C.white }, line: { color: C.hair, width: 0.75 }, shadow: { type: "outer", color: C.forest, blur: 30, offset: 8, angle: 90, opacity: 0.16 } });
    ring(s, 0.42, 0.77, 4.06);
    s.addImage({ objectName: "!!logo", path: LOGO, x: 1.0, y: 1.6, w: 2.9, h: 2.9 * 782 / 936, altText: "Dec Matcha logo: matcha bowl with a leaf" });
    s.addImage({ objectName: "Cover panel", path: A("panel.jpg"), x: 4.95, y: 0, w: 5.05, h: 5.625, altText: "Deep green panel" });
    txt(s, "Cover subtitle", "BUSINESS PLAN  |  INTRODUCTION TO BUSINESS (BSIB1101)", 5.5, 0.72, 4.1, 0.26, { fontSize: 9, bold: true, color: C.goldL, charSpacing: 0.5 });
    txt(s, "Cover title", "DEC MATCHA", 5.5, 1.0, 4.1, 0.82, { fontFace: H, fontSize: 44, bold: true, charSpacing: 2, color: C.porc, valign: "middle" });
    label(s, "Members label", "GROUP MEMBERS", 5.5, 2.1, 3, { color: C.sageL, charSpacing: 3 });
    const M = [["Deema Zaid Al Moharbi", "21J25117"], ["Taqwa Abdullah Al-Hashami", "21S2452"], ["Nardeen Mansoor Al-Farsi", "21J2583"], ["Mais Shaikhan Al-Toubi", "31J2573"], ["Dhoha Talal Al-Hinai", "21S246"]];
    const rows = [];
    M.forEach(([n, id], i) => {
      const y = 2.4 + i * 0.53;
      s.addShape("line", { objectName: `Member rule ${i + 1}`, x: 5.5, y, w: 4.0, h: 0, line: { color: C.sageL, width: 0.5, transparency: 70 } });
      txt(s, `Member name ${i + 1}`, n, 5.5, y, 2.9, 0.53, { fontSize: 14, bold: true, color: C.porc, valign: "middle" });
      txt(s, `Member ID ${i + 1}`, id, 8.3, y, 1.2, 0.53, { fontSize: 11.5, color: C.goldL, align: "right", valign: "middle", charSpacing: 1 });
      rows.push([`Member rule ${i + 1}`, `Member name ${i + 1}`, `Member ID ${i + 1}`]);
    });
    leaves(s, [4.25, 0.35, 0.55, 15], [-0.6, 4.35, 1.6, -25]);
    const fx = [
      { type: "push", names: ["!!dunes"], at: 0, dur: 16000, scale: 1.07 },
      { type: "fade", names: ["!!plate"], at: 0, dur: 900, sound: { kind: "bowl", vol: 0.7 } },
      { type: "fade", names: ["!!powder"], at: 500, dur: 1800, sound: { kind: "whisk", vol: 0.5 } },
      { type: "emergeX", names: ["!!powder"], at: 500, dur: 2400, dx: -0.03 },
      { type: "fade", names: ["!!logo"], at: 350, dur: 900 },
      { type: "fade", names: ["!!ring"], at: 700, dur: 900 },
      { type: "spin", names: ["!!ring"], at: 700, dur: 90000 },
      { type: "wipe", dir: "right", names: ["Cover panel"], at: 200, dur: 1000 },
      { type: "fade", names: ["Cover subtitle"], at: 1000, dur: 700 },
      { type: "rise", names: ["Cover title"], at: 1150, dur: 900 },
      { type: "fade", names: ["Members label"], at: 1600, dur: 600 },
      ...rows.map((g, i) => ({ type: "emergeX", names: g, at: 1750 + i * 130, dur: 700, dx: 0.04 })),
      floatLeaf(3600),
    ];
    SPEC.slides.push({ n: 1, transition: "fade", effects: fx, tilt: { "!!orb": 52 }, text3d: ["Cover title"] });
  }

  // =================================================================== 2 — business background (hub & spokes)
  {
    const s = pres.addSlide({ masterName: "CONTENT" });
    s.background = { path: A("bg2.jpg") };
    mist(s, -0.25, 0.05);
    header(s, "01", "Business Background");
    const cy = [1.25, 2.5, 3.75].map((y) => y + 0.525);
    const spokes = [];
    cy.forEach((y, i) => {
      const dy = (y - 2.9);
      const ang = Math.atan2(dy, 1.5);
      const ex = 5.0 - 1.15 * Math.cos(ang), ey = 2.9 + 1.15 * Math.sin(ang);
      const L = { color: C.gold, width: 0.75, transparency: 35 };
      s.addShape("line", { objectName: `Spoke L${i}`, x: 3.5, y: Math.min(y, ey), w: ex - 3.5, h: Math.max(Math.abs(ey - y), 0.001), line: Object.assign({}, L), flipV: ey < y });
      const ex2 = 5.0 + 1.15 * Math.cos(ang);
      s.addShape("line", { objectName: `Spoke R${i}`, x: ex2, y: Math.min(y, ey), w: 6.5 - ex2, h: Math.max(Math.abs(ey - y), 0.001), line: Object.assign({}, L), flipV: ey > y });
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
      card(s, `Card ${lab}`, x, y, 3.05, 1.05); g.push(`Card ${lab}`);
      g.push(...medal(s, lab, x + 0.18, y + 0.29, 0.46, ic));
      label(s, `Label ${lab}`, lab, x + 0.8, y + 0.13, 2.15, { fontSize: 8 }); g.push(`Label ${lab}`);
      const big = val.length < 20;
      txt(s, `Value ${lab}`, val, x + 0.8, y + 0.36, 2.15, sub ? 0.3 : 0.6, { fontSize: big ? 15 : 12, bold: true, fontFace: big ? H : B, color: big ? C.forest : C.ink }); g.push(`Value ${lab}`);
      if (sub) { txt(s, `Note ${lab}`, sub, x + 0.8, y + 0.66, 2.15, 0.34, { fontSize: 9, italic: true, color: C.muted }); g.push(`Note ${lab}`); }
      groups.push({ g, col });
    });
    leaves(s, [8.95, 0.3, 0.5, 40], [-0.75, 4.6, 1.5, 10]);
    const fx = [
      { type: "spin", names: ["!!orb"], at: 0, dur: 60000 },
      { type: "spin", names: ["!!ring"], at: 0, dur: 90000, rev: true },
      ...spokes.map((n, i) => ({ type: "wipe", dir: n.includes("L") ? "right" : "left", names: [n], at: 100 + (i >> 1) * 120, dur: 600 })),
      ...groups.map(({ g, col }, i) => ({ type: "emerge", names: g, at: 450 + (i % 3) * 170 + col * 85, dur: 850, fx: 0.5, fy: 0.52 })),
      floatLeaf(3800),
    ];
    SPEC.slides.push({ n: 2, transition: "morph", tsound: { kind: "air", vol: 0.8 }, effects: fx });
  }

  // =================================================================== 3 — target market (radar)
  {
    const s = pres.addSlide({ masterName: "CONTENT" });
    s.background = { path: A("bg3.jpg") };
    mist(s, -0.5, -0.05);
    header(s, "02", "Target Market & Competition");
    card(s, "Hero card", 0.5, 1.2, 4.4, 2.75, { fill: C.forest, line: null, so: 0.22 });
    label(s, "Main customers label", "MAIN CUSTOMERS", 0.78, 1.45, 3, { color: C.goldL });
    s.addImage({ objectName: "Age dust", path: A("dust_light.png"), x: 2.35 - 0.16, y: 2.27 - 0.09, w: 0.32, h: 0.32 * 800 / 1400, altText: "Matcha particles gathering" }); // parked behind the number; scaled up only during the show
    const k = counter(s, "Age range", "18–30", (f) => `${Math.round(18 * f)}–${Math.round(30 * f)}`, { x: 0.75, y: 1.7, w: 3.9, h: 1.15, fill: C.forest }, { fontFace: H, fontSize: 72, bold: true, color: C.porc, valign: "middle" });
    txt(s, "Customers", "University students and young adults", 0.78, 2.97, 3.95, 0.35, { fontSize: 15, bold: true, color: C.sageL });
    txt(s, "Also welcome", "We also welcome matcha lovers and café visitors.", 0.78, 3.36, 3.95, 0.4, { fontSize: 11.5, color: "B9C8B4" });

    label(s, "Competitors label", "COMPETITORS IN NIZWA", 5.4, 1.08, 3);
    ring(s, 5.675, 1.35, 2.65);
    s.addImage({ objectName: "Radar", path: A("radar.png"), x: 5.725, y: 1.4, w: 2.55, h: 2.55, altText: "Ripple rings around the bowl" });
    orb(s, 6.69, 2.365, 0.62);
    const comp = [["Drisha", 6.33, 1.98], ["Fusul Cafe", 7.82, 2.3], ["Rive", 6.72, 3.33]];
    const cg = [];
    comp.forEach(([n, x, y], i) => {
      s.addShape("ellipse", { objectName: `Comp halo ${i}`, x: x - 0.1, y: y - 0.1, w: 0.34, h: 0.34, fill: { color: C.gold, transparency: 72 }, line: { type: "none" } });
      s.addShape("ellipse", { objectName: `Comp dot ${i}`, x, y, w: 0.14, h: 0.14, fill: { color: C.gold }, line: { color: C.white, width: 1 } });
      txt(s, `Comp ${n}`, n, x + 0.25, y - 0.09, 1.25, 0.3, { fontSize: 12, bold: true, color: C.forest, valign: "middle" });
      cg.push([`Comp halo ${i}`, `Comp dot ${i}`, `Comp ${n}`]);
    });
    label(s, "Difference label", "OUR DIFFERENCE", 0.5, 4.13, 3);
    const diffs = ["More matcha choices", "Oat milk", "Student offers", "A calm place"];
    const dg = [];
    diffs.forEach((d, i) => {
      const x = 0.5 + i * 2.3;
      card(s, `Diff card ${i}`, x, 4.4, 2.1, 0.5, { r: 0.25 });
      s.addShape("ellipse", { objectName: `Check ${i}`, x: x + 0.12, y: 4.5, w: 0.3, h: 0.3, fill: { color: C.matcha }, line: { type: "none" } });
      s.addImage({ objectName: `Check icon ${i}`, data: I.check, x: x + 0.195, y: 4.575, w: 0.15, h: 0.15, altText: "Check" });
      txt(s, `Diff ${i}`, d, x + 0.52, 4.4, 1.55, 0.5, { fontSize: 12, bold: true, color: C.ink, valign: "middle" });
      dg.push([`Diff card ${i}`, `Check ${i}`, `Check icon ${i}`, `Diff ${i}`]);
    });
    leaves(s, [8.95, 0.25, 0.5, 110], [9.3, 2.75, 1.4, -40]);
    const fx = [
      { type: "spin", names: ["!!ring"], at: 0, dur: 90000 },
      { type: "zoom", names: ["Hero card"], at: 0, dur: 700, from: 0.94 },
      { type: "fade", names: ["Main customers label"], at: 300, dur: 500 },
      { type: "converge", names: ["Age dust"], at: 250, dur: 1300, from: 13, sound: { kind: "dust", vol: 0.6 } },
      { type: "fadeOut", names: ["Age dust"], at: 1450, dur: 700 },
      { type: "counter", frames: k.frames, final: k.final, at: 650, step: 80, sound: { vol: 0.55 } },
      { type: "rise", names: ["Customers"], at: 1250, dur: 600 },
      { type: "rise", names: ["Also welcome"], at: 1400, dur: 600 },
      { type: "zoom", names: ["Radar"], at: 200, dur: 1400, from: 0.4 },
      { type: "fade", names: ["Competitors label"], at: 400, dur: 600 },
      { type: "spin", names: ["!!orb"], at: 0, dur: 60000 },
      ...cg.map((g, i) => ({ type: "pop", names: g, at: 1300 + i * 350, dur: 450, sound: { kind: "drop", vol: 0.4 } })),
      { type: "fade", names: ["Difference label"], at: 2100, dur: 500 },
      ...dg.map((g, i) => ({ type: "rise", names: g, at: 2200 + i * 130, dur: 600 })),
      floatLeaf(3400),
    ];
    SPEC.slides.push({ n: 3, transition: "morph", tsound: { kind: "air", vol: 0.8 }, effects: fx, text3d: [k.final] });
  }

  // =================================================================== 4 — macro-economics (gauge)
  {
    const s = pres.addSlide({ masterName: "CONTENT" });
    s.background = { path: A("bg4.jpg") };
    mist(s, -0.75, 0.05);
    header(s, "03", "Macro-Economic Factors");
    // a single drop lands in the bowl: ripples spread from the inflation figure
    const ox = 2.425, oy = 3.05;
    orb(s, ox - 1.975, oy - 1.975, 3.95);
    const ripples = [[1.75, 25], [2.25, 45], [2.7, 62]].map(([d, tr], i) => {
      s.addShape("ellipse", { objectName: `Ripple ${i + 1}`, x: ox - d / 2, y: oy - d / 2, w: d, h: d, fill: { type: "none" }, line: { color: C.porc, width: 1.25, transparency: tr } });
      return `Ripple ${i + 1}`;
    });
    s.addShape("ellipse", { objectName: "Drop", x: ox - 0.72, y: oy - 0.72, w: 1.44, h: 1.44, fill: { color: C.forest }, line: { color: C.porc, width: 1.5, transparency: 20 }, shadow: shadow(0.3, 12) });
    const k = counter(s, "Inflation value", "2.9%", (f) => `${(2.9 * f).toFixed(1)}%`, { x: ox - 0.62, y: oy - 0.3, w: 1.24, h: 0.6, fill: C.forest }, { fontFace: H, fontSize: 32, bold: true, color: C.porc, align: "center", valign: "middle" }, 12);

    txt(s, "Inflation title", "Inflation", 5.0, 1.2, 4.4, 0.42, { fontFace: H, fontSize: 22, bold: true, color: C.forest });
    txt(s, "Inflation text", "Higher prices for matcha, milk, cups, and rent can increase our costs.", 5.0, 1.65, 4.4, 0.48, { fontSize: 12.5, color: C.body });
    txt(s, "Inflation source", "NCSI, Oman, October 2026", 5.0, 2.14, 4.4, 0.22, { fontSize: 9, italic: true, color: C.muted });
    const cards = [["Exchange rates", "Changes may make imported matcha powder cost more.", I.exchange, C.white, 2.6], ["Our plan", "Compare suppliers and avoid wasting ingredients.", I.plan, C.tint, 3.85]];
    const cg = [];
    cards.forEach(([t, b, ic, fill, y]) => {
      const g = [];
      card(s, `Card ${t}`, 5.0, y, 4.5, 1.05, { fill }); g.push(`Card ${t}`);
      g.push(...medal(s, t, 5.2, y + 0.29, 0.46, ic));
      txt(s, `Title ${t}`, t, 5.85, y + 0.17, 3.45, 0.32, { fontSize: 14.5, bold: true, color: C.forest }); g.push(`Title ${t}`);
      txt(s, `Body ${t}`, b, 5.85, y + 0.5, 3.45, 0.45, { fontSize: 11.5, color: C.body }); g.push(`Body ${t}`);
      cg.push(g);
    });
    leaves(s, [9.05, 0.3, 0.5, 160], [-0.9, 4.25, 1.5, 30]);
    const fx = [
      { type: "pop", names: ["Drop"], at: 250, dur: 500, sound: { kind: "drop", vol: 0.6 } },
      ...ripples.map((r, i) => ({ type: "zoom", names: [r], at: 450 + i * 220, dur: 1500, from: 0.45 })),
      { type: "counter", frames: k.frames, final: k.final, at: 600, step: 100 },
      { type: "spin", names: ["!!orb"], at: 0, dur: 60000 },
      { type: "rise", names: ["Inflation title"], at: 900, dur: 600 },
      { type: "rise", names: ["Inflation text"], at: 1050, dur: 600 },
      { type: "fade", names: ["Inflation source"], at: 1300, dur: 600 },
      ...cg.map((g, i) => ({ type: "emergeX", names: g, at: 1700 + i * 300, dur: 800, dx: 0.06 })),
      floatLeaf(3600),
    ];
    SPEC.slides.push({ n: 4, transition: "ripple", tsound: { kind: "air", vol: 0.8 }, effects: fx, text3d: [k.final] });
  }

  // =================================================================== 5 — 4 Ps
  {
    const s = pres.addSlide({ masterName: "CONTENT" });
    s.background = { path: A("bg5.jpg") };
    mist(s, -1.0, 0.0);
    header(s, "04", "Marketing Mix – The 4 Ps");
    const Ps = [
      ["Product", "Hot and iced matcha, strawberry matcha, vanilla matcha, and light desserts", I.mug, 0.5, 1.15, C.white],
      ["Price", "Proposed drink prices from OMR 1.500 to OMR 2.000", I.tag, 5.3, 1.15, C.tint],
      ["Place", "An accessible café in Nizwa, with takeaway and online orders", I.pin, 0.5, 3.15, C.white],
      ["Promotion", "Instagram, TikTok, student discounts, opening offers, and loyalty cards", I.horn, 5.3, 3.15, C.white],
    ];
    const pg = [];
    Ps.forEach(([t, b, ic, x, y, fill]) => {
      const g = [];
      card(s, `Card ${t}`, x, y, 4.2, 1.8, { fill, r: 0.12 }); g.push(`Card ${t}`);
      g.push(...medal(s, t, x + 0.35, y + 0.3, 0.52, ic));
      txt(s, `Title ${t}`, t, x + 1.05, y + 0.3, 2.8, 0.52, { fontFace: H, fontSize: 21, bold: true, color: C.forest, valign: "middle" }); g.push(`Title ${t}`);
      txt(s, `Body ${t}`, b, x + 0.35, y + 0.98, 3.65, 0.62, { fontSize: 12, color: C.body }); g.push(`Body ${t}`);
      pg.push(g);
    });
    ring(s, 4.35, 2.4, 1.3);
    orb(s, 4.5, 2.55, 1.0);
    leaves(s, [9.15, 0.3, 0.45, 200], [4.3, 5.0, 1.3, 0]);
    const fx = [
      { type: "spin", names: ["!!orb"], at: 0, dur: 60000 },
      { type: "spin", names: ["!!ring"], at: 0, dur: 90000, rev: true },
      ...pg.map((g, i) => ({ type: "emerge", names: g, at: 150 + i * 220, dur: 900, fx: 0.5, fy: 0.54 })),
      floatLeaf(3300),
    ];
    SPEC.slides.push({ n: 5, transition: "morph", tsound: { kind: "air", vol: 0.8 }, effects: fx });
  }

  // =================================================================== 6 — human resources
  {
    const s = pres.addSlide({ masterName: "CONTENT" });
    s.background = { path: A("bg6.jpg") };
    mist(s, -1.25, 0.1);
    header(s, "05", "Human Resources");
    orb(s, 8.78, 0.33, 0.6);
    card(s, "GM card", 3.4, 1.12, 3.2, 0.82, { fill: C.forest, line: null, r: 0.12, so: 0.22 });
    txt(s, "GM title", "GENERAL MANAGER", 3.4, 1.2, 3.2, 0.36, { fontSize: 13.5, bold: true, color: C.porc, align: "center", charSpacing: 1.5, valign: "middle" });
    txt(s, "GM text", "Overall planning and supervision", 3.4, 1.55, 3.2, 0.3, { fontSize: 10.5, color: C.sageL, align: "center", valign: "middle" });
    const L = { color: C.gold, width: 1, transparency: 25 };
    s.addShape("line", { objectName: "Trunk", x: 5.0, y: 1.94, w: 0, h: 0.31, line: Object.assign({}, L) });
    s.addShape("line", { objectName: "Branch", x: 1.575, y: 2.25, w: 6.9, h: 0, line: Object.assign({}, L) });
    const roles = [["Marketing Manager", "Advertising", I.horn], ["Finance Manager", "Budget and accounts", I.coins], ["Operations Manager", "Stock and quality", I.boxes], ["HR Manager", "Staff and training", I.friends]];
    const rg = [], drops = [];
    roles.forEach(([t, d, ic], i) => {
      const x = 0.55 + i * 2.3, cx = x + 1.025;
      s.addShape("line", { objectName: `Drop ${i}`, x: cx, y: 2.25, w: 0, h: 0.25, line: Object.assign({}, L) });
      drops.push(`Drop ${i}`);
      const g = [];
      card(s, `Card ${t}`, x, 2.5, 2.05, 1.7); g.push(`Card ${t}`);
      g.push(...medal(s, t, cx - 0.28, 2.7, 0.56, ic));
      txt(s, `Title ${t}`, t, x + 0.1, 3.36, 1.85, 0.35, { fontSize: 13, bold: true, color: C.forest, align: "center", valign: "middle" }); g.push(`Title ${t}`);
      txt(s, `Duty ${t}`, d, x + 0.1, 3.7, 1.85, 0.3, { fontSize: 11, color: C.body, align: "center", valign: "middle" }); g.push(`Duty ${t}`);
      rg.push(g);
    });
    card(s, "Staff bar", 0.55, 4.45, 8.95, 0.5, { fill: C.beige, line: "E4DCC9", r: 0.25, noShadow: true });
    txt(s, "Staff text", [
      { text: "Additional staff: ", options: { bold: true, color: C.forest } },
      { text: "baristas and a cashier/service assistant", options: { color: C.body } },
    ], 0.55, 4.45, 8.95, 0.5, { fontSize: 12, align: "center", valign: "middle" });
    leaves(s, [9.55, 2.0, 0.45, 300], [-0.85, 0.9, 1.5, 60]);
    const fx = [
      { type: "spin", names: ["!!orb"], at: 0, dur: 60000 },
      { type: "drop", names: ["GM card", "GM title", "GM text"], at: 0, dur: 800 },
      { type: "wipe", dir: "top", names: ["Trunk"], at: 700, dur: 300 },
      { type: "barn", names: ["Branch"], at: 950, dur: 600, sound: { kind: "knock", vol: 0.5 } },
      ...drops.map((d) => ({ type: "wipe", dir: "top", names: [d], at: 1450, dur: 250 })),
      ...rg.map((g, i) => ({ type: "flip", names: g, at: 1600 + i * 150, dur: 700 })),
      { type: "zoom", names: ["Staff bar", "Staff text"], at: 2400, dur: 700, from: 0.94 },
      floatLeaf(3500),
    ];
    SPEC.slides.push({ n: 6, transition: "vortex", tsound: { kind: "dust", vol: 0.7 }, effects: fx });
  }

  // =================================================================== 7 — start-up costs & finance
  {
    const s = pres.addSlide({ masterName: "CONTENT" });
    s.background = { path: A("bg7.jpg") };
    mist(s, -1.5, 0.05);
    header(s, "06", "Start-up Costs & Finance");
    card(s, "Total card", 0.5, 1.15, 4.6, 0.85, { fill: C.forest, line: null, r: 0.1, so: 0.22 });
    s.addImage({ objectName: "Total dust", path: A("dust_light.png"), x: 3.9 - 0.15, y: 1.57 - 0.085, w: 0.3, h: 0.3 * 800 / 1400, altText: "Matcha particles gathering" }); // parked behind the total
    txt(s, "Total label", "TOTAL START-UP BUDGET", 0.75, 1.15, 2.0, 0.85, { fontSize: 9, bold: true, color: C.goldL, charSpacing: 1.5, valign: "middle" });
    // digits assemble individually (Cambria Bold advances), then the editable value locks in on top
    const MET = JSON.parse(fs.readFileSync(path.join(__dirname, "metrics.json")));
    const TV = "OMR 8,500", FS = 28, right = 2.6 + 2.32;
    const adv = (str) => [...str].reduce((a, ch) => a + MET[ch] * FS / 72, 0);
    const x0 = right - adv(TV);
    const pieces = [[0, "OMR"], [4, "8"], [5, ","], [6, "5"], [7, "0"], [8, "0"]];
    const digitNames = pieces.map(([i, str], j) => {
      const nm = `Total value counter frame digit ${j + 1}`;
      txt(s, nm, str, x0 + adv(TV.slice(0, i)), 1.24, adv(str) + 0.12, 0.66, { fontFace: H, fontSize: FS, bold: true, color: C.porc, valign: "middle", wrap: false });
      return nm;
    });
    txt(s, "Total value", TV, 2.6, 1.24, 2.32, 0.66, { fontFace: H, fontSize: FS, bold: true, color: C.porc, align: "right", valign: "middle", fill: { color: C.forest } });

    const costs = [["Rent and setup", "OMR 1,500", 1500], ["Furniture and interior", "OMR 1,800", 1800], ["Equipment", "OMR 2,000", 2000], ["Ingredients and packaging", "OMR 1,000", 1000], ["Other setup costs and working capital", "OMR 2,200", 2200]];
    costs.forEach(([l, v, n], i) => {
      const y = 2.2 + i * 0.47;
      txt(s, `Cost label ${i}`, l, 0.5, y, 1.8, 0.4, { fontSize: 10, color: C.body, valign: "middle" });
      s.addShape("roundRect", { objectName: `Track ${i}`, x: 2.4, y: y + 0.13, w: 1.75, h: 0.14, rectRadius: 0.07, fill: { color: "E4EAE0" }, line: { type: "none" } });
      s.addShape("roundRect", { objectName: `Bar ${i}`, x: 2.4, y: y + 0.13, w: 1.75 * n / 2200, h: 0.14, rectRadius: 0.07, fill: { color: i === 4 ? C.gold : C.matcha }, line: { type: "none" } });
      txt(s, `Cost value ${i}`, v, 4.25, y, 0.85, 0.4, { fontSize: 10, bold: true, color: C.ink, valign: "middle" });
    });
    txt(s, "Estimate note", "These costs are estimates, not final prices.", 0.5, 4.7, 4.6, 0.28, { fontSize: 9.5, italic: true, color: C.muted });

    label(s, "Finance label", "SOURCES OF FINANCE", 5.45, 1.15, 3);
    ring(s, 5.3, 1.35, 2.8);
    const cx = 6.7, cyy = 2.75, D = 2.5;
    const partAng = 270 + 360 * 6000 / 8500;
    s.addShape("blockArc", { objectName: "Arc partners", x: cx - D / 2, y: cyy - D / 2, w: D, h: D, angleRange: [270, partAng % 360], arcThicknessRatio: 0.2, fill: { color: C.forest }, line: { type: "none" } });
    s.addShape("blockArc", { objectName: "Arc family", x: cx - D / 2, y: cyy - D / 2, w: D, h: D, angleRange: [partAng % 360, 270], arcThicknessRatio: 0.2, fill: { color: C.gold }, line: { type: "none" } });
    orb(s, 6.0, 2.05, 1.4);
    card(s, "Fin card 1", 8.2, 1.5, 1.3, 1.05);
    card(s, "Fin card 2", 8.2, 2.85, 1.3, 1.05);
    s.addShape("ellipse", { objectName: "Swatch 1", x: 8.33, y: 1.66, w: 0.1, h: 0.1, fill: { color: C.forest }, line: { type: "none" } });
    s.addShape("ellipse", { objectName: "Swatch 2", x: 8.33, y: 3.01, w: 0.1, h: 0.1, fill: { color: C.gold }, line: { type: "none" } });
    txt(s, "Fin label 1", "PARTNERS’ SAVINGS", 8.48, 1.6, 1.0, 0.36, { fontSize: 7.5, bold: true, color: C.muted, charSpacing: 1 });
    txt(s, "Fin label 2", "FAMILY INVESTMENT", 8.48, 2.95, 1.0, 0.36, { fontSize: 7.5, bold: true, color: C.muted, charSpacing: 1 });
    const f1 = counter(s, "Fin value 1", "OMR 6,000", (f) => omr(6000 * f), { x: 8.3, y: 2.0, w: 1.12, h: 0.42, fill: C.white }, { fontFace: H, fontSize: 16, bold: true, color: C.forest, valign: "middle" }, 10);
    const f2 = counter(s, "Fin value 2", "OMR 2,500", (f) => omr(2500 * f), { x: 8.3, y: 3.35, w: 1.12, h: 0.42, fill: C.white }, { fontFace: H, fontSize: 16, bold: true, color: C.goldD, valign: "middle" }, 10);
    leaves(s, [9.1, 4.35, 0.45, 20], [9.0, -0.65, 1.5, -10]);
    const fx = [
      { type: "spin", names: ["!!orb"], at: 0, dur: 60000 },
      { type: "spin", names: ["!!ring"], at: 0, dur: 90000 },
      { type: "zoom", names: ["Total card", "Total label"], at: 0, dur: 700, from: 0.94 },
      { type: "converge", names: ["Total dust"], at: 100, dur: 1000, from: 10 },
      { type: "fadeOut", names: ["Total dust"], at: 1150, dur: 600 },
      { type: "assemble", digits: digitNames, final: "Total value", at: 350, step: 110, dur: 450, sound: { vol: 0.7 } },
      ...costs.map((_, i) => ({ type: "fade", names: [`Cost label ${i}`, `Track ${i}`], at: 600 + i * 120, dur: 500 })),
      ...costs.map((_, i) => ({ type: "wipe", dir: "left", names: [`Bar ${i}`], at: 900 + i * 120, dur: 800 })),
      ...costs.map((_, i) => ({ type: "emergeX", names: [`Cost value ${i}`], at: 1450 + i * 120, dur: 500, dx: -0.02 })),
      { type: "fade", names: ["Estimate note"], at: 2300, dur: 600 },
      { type: "fade", names: ["Finance label"], at: 700, dur: 500 },
      { type: "wheel", names: ["Arc partners"], at: 1000, dur: 1100 },
      { type: "wheel", names: ["Arc family"], at: 2000, dur: 600 },
      { type: "emergeX", names: ["Fin card 1", "Swatch 1", "Fin label 1"], at: 1300, dur: 600, dx: 0.04 },
      { type: "counter", frames: f1.frames, final: f1.final, at: 1450, step: 75, sound: { vol: 0.45 } },
      { type: "emergeX", names: ["Fin card 2", "Swatch 2", "Fin label 2"], at: 2000, dur: 600, dx: 0.04 },
      { type: "counter", frames: f2.frames, final: f2.final, at: 2150, step: 75, sound: { vol: 0.45 } },
      floatLeaf(3100),
    ];
    SPEC.slides.push({ n: 7, transition: "morph", tsound: { kind: "air", vol: 0.8 }, effects: fx, text3d: ["Total value"] });
  }

  // =================================================================== 8 — references
  {
    const s = pres.addSlide({ masterName: "CONTENT" });
    s.background = { path: A("bg8.jpg") };
    mist(s, -1.75, 0.0);
    header(s, "07", "References");
    orb(s, 8.78, 0.33, 0.6);
    const refs = [
      ["National Centre for Statistics and Information (NCSI). (18 November 2026). Oman’s inflation rate reaches 2.9% in October 2026.", "https://ncsi.gov.om/newsPage/newsDetail?id=434"],
      ["Times of Oman. (17 November 2026). Oman’s inflation rate reaches 2.9 percent in October 2026.", "https://timesofoman.com/article/179291-omans-inflation-rate-reaches-29-percent-in-october-2026"],
      ["Talabat. (n.d.). Rive menu in Nizwa.", "https://www.talabat.com/oman/restaurant/1116567/rive-nizwa-suq"],
      ["Restaurant Guru. (n.d.). Drisha café listing in Nizwa.", "https://restaurantguru.com/Drisha-Nizwa"],
    ];
    s.addShape("line", { objectName: "Timeline", x: 0.83, y: 1.4, w: 0, h: 2.8, line: { color: C.gold, width: 1, transparency: 30 } });
    const rg = [];
    refs.forEach(([cite, url], i) => {
      const y = 1.15 + i * 0.8;
      s.addShape("ellipse", { objectName: `Node ${i}`, x: 0.65, y: y + 0.18, w: 0.36, h: 0.36, fill: { color: C.forest }, line: { type: "none" }, shadow: shadow(0.18, 8) });
      txt(s, `Node num ${i}`, String(i + 1), 0.65, y + 0.18, 0.36, 0.36, { fontFace: H, fontSize: 12, bold: true, color: C.porc, align: "center", valign: "middle" });
      card(s, `Ref card ${i}`, 1.3, y, 8.2, 0.72);
      txt(s, `Ref ${i}`, cite, 1.48, y + 0.07, 7.85, 0.4, { fontSize: 10.5, color: C.ink, valign: "middle" });
      txt(s, `URL ${i}`, [{ text: url, options: { hyperlink: { url } } }], 1.48, y + 0.47, 7.85, 0.2, { fontSize: 8.5, color: "4E7A55", valign: "middle" });
      rg.push({ node: [`Node ${i}`, `Node num ${i}`], card: [`Ref card ${i}`, `Ref ${i}`, `URL ${i}`] });
    });
    card(s, "Note bar", 1.3, 4.45, 8.2, 0.48, { fill: C.beige, line: "E4DCC9", r: 0.24, noShadow: true });
    txt(s, "Note", "Dec Matcha’s drink prices, start-up costs, and sources of finance are the team’s own estimates.", 1.48, 4.45, 7.85, 0.48, { fontSize: 10.5, italic: true, color: C.forest, valign: "middle" });
    leaves(s, [0.3, 4.55, 0.4, 40], [9.45, 1.0, 1.4, 120]);
    const fx = [
      { type: "spin", names: ["!!orb"], at: 0, dur: 60000 },
      { type: "wipe", dir: "top", names: ["Timeline"], at: 0, dur: 2000 },
      ...rg.map((r, i) => ({ type: "pop", names: r.node, at: 150 + i * 480, dur: 400 })),
      ...rg.map((r, i) => ({ type: "emergeX", names: r.card, at: 250 + i * 480, dur: 700, dx: 0.04 })),
      { type: "rise", names: ["Note bar", "Note"], at: 2300, dur: 700 },
      floatLeaf(3200),
    ];
    SPEC.slides.push({ n: 8, transition: "wind", tsound: { kind: "air", vol: 0.6 }, effects: fx });
  }

  // =================================================================== 9 — thank you: the finished bowl rests on the matcha dunes
  {
    const s = pres.addSlide({ masterName: "COVER" });
    s.background = { path: A("bg9.jpg") };
    s.addImage({ objectName: "!!dunes", path: A("dunes_low.jpg"), x: 0, y: 0, w: 10, h: 5.625, altText: "Landscape of matcha powder dunes" });
    s.addImage({ objectName: "!!powder", path: A("powder.png"), x: -0.95, y: -0.35, w: 5.4, h: 5.4 * 825 / 1350, altText: "Drifting matcha powder" });
    s.addShape("ellipse", { objectName: "!!plate", x: 0.75, y: 0.45, w: 2.7, h: 2.7, fill: { color: C.white }, line: { color: C.hair, width: 0.75 }, shadow: { type: "outer", color: C.forest, blur: 30, offset: 8, angle: 90, opacity: 0.16 } });
    ring(s, 0.58, 0.28, 3.04);
    s.addImage({ objectName: "!!logo", path: LOGO, x: 1.075, y: 0.94, w: 2.05, h: 2.05 * 782 / 936, altText: "Dec Matcha logo: matcha bowl with a leaf" });
    // the top-view bowl from every previous scene morphs into the finished chawan
    s.addImage({ objectName: "!!orb", path: A("chawan.png"), x: 6.05, y: 2.45, w: 3.7, h: 3.7 * 1000 / 1200, altText: "Bowl of whisked matcha" });
    txt(s, "Thanks", "Thank You!", 3.95, 0.72, 5.6, 0.85, { fontFace: H, fontSize: 46, bold: true, valign: "middle", color: C.forest });
    txt(s, "Closing", "Dec Matcha aims to bring fresh matcha, good service, and a comfortable café experience to Nizwa.", 3.95, 1.62, 4.9, 0.7, { fontSize: 14, color: C.body });
    leaves(s, [3.5, 0.3, 0.5, 30], [-0.6, 4.1, 1.6, -20]);
    const fx = [
      { type: "push", names: ["!!dunes"], at: 0, dur: 16000, scale: 1.06 },
      { type: "spin", names: ["!!ring"], at: 0, dur: 90000 },
      { type: "rise", names: ["Thanks"], at: 300, dur: 1000, sound: { kind: "bowl", vol: 0.6 } },
      { type: "rise", names: ["Closing"], at: 900, dur: 900 },
      { type: "float", names: ["!!orb"], at: 1600, dur: 4200, dy: -0.006 },
      floatLeaf(3200),
    ];
    SPEC.slides.push({ n: 9, transition: "morph", tsound: { kind: "air", vol: 0.8 }, effects: fx, text3d: ["Thanks"] });
  }

  await pres.writeFile({ fileName: OUT });
  fs.writeFileSync(path.join(path.dirname(path.resolve(OUT)), "spec.json"), JSON.stringify(SPEC, null, 1));
  console.log("wrote", OUT);
})();
