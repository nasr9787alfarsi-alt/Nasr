// Bilingual lesson deck: "Who's Cooking the Economy?" - Chapter 2 Economic Systems
const pptxgen = require('pptxgenjs');
const React = require('react');
const ReactDOMServer = require('react-dom/server');
const sharp = require('sharp');
const fa = require('react-icons/fa');
const fs = require('fs');
const path = require('path');

const THEME = {
  name: "Who's Cooking the Economy",
  headFontFace: 'Cambria', bodyFontFace: 'Calibri',
  colors: { dk1: '22223A', lt1: 'FFFFFF', dk2: '2E4A86', lt2: 'FBF1E1',
            accent1: 'D9503F', accent2: '2F8F7A', accent3: '2E4A86', accent4: 'F0B13B', accent5: '26342F', accent6: 'A93A2C',
            hlink: '2E4A86', folHlink: '1F6B5B' },
};
const HEX = { ink: '22223A', cream: 'FBF1E1', white: 'FFFFFF', mk: 'D9503F', mx: '2F8F7A', cm: '2E4A86', must: 'F0B13B', chalk: '26342F', muted: '6A6F7D' };
const AR = 'Arial';
const IMG = path.join(__dirname, 'img');

// ---------------------------------------------------------------- icons
const iconCache = {};
async function icon(name, hex, size = 256) {
  const key = name + hex;
  if (iconCache[key]) return iconCache[key];
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(fa[name], { color: '#' + hex, size: String(size) }));
  const buf = await sharp(Buffer.from(svg)).resize(size, size).png().toBuffer();
  return (iconCache[key] = 'image/png;base64,' + buf.toString('base64'));
}

(async () => {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE';            // 13.333 x 7.5 in
  pres.title = "Who's Cooking the Economy? - Chapter 2 Economic Systems";
  pres.author = 'Mais altoubi, Alshima Almahrooqi, Nardeen alfarsi, shatha al_umeiri';
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;
  const COL = { ink: C.text1, white: C.background1, cream: C.background2, mk: C.accent1, mx: C.accent2, cm: C.accent3, must: C.accent4, chalk: C.accent5, mkd: C.accent6, navy: C.text2 };

  // ---------------------------------------------------------------- layouts
  pres.defineSlideMaster({
    title: 'TITLE_DARK', background: { color: COL.ink },
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: 0.7, y: 1.55, w: 8.2, h: 1.9, fontSize: 48, bold: true, color: COL.must, valign: 'top', align: 'left' }, text: '' } },
      { placeholder: { options: { name: 'body', type: 'body', x: 0.7, y: 3.45, w: 8.2, h: 0.9, fontSize: 22, color: COL.white, valign: 'top' }, text: '' } },
    ],
  });
  pres.defineSlideMaster({
    title: 'SECTION_DARK', background: { color: COL.ink },
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: 0.9, y: 2.0, w: 6.8, h: 1.7, fontSize: 38, bold: true, color: COL.white, valign: 'bottom', align: 'left' }, text: '' } },
      { placeholder: { options: { name: 'body', type: 'body', x: 0.9, y: 3.9, w: 6.8, h: 1.4, fontSize: 18, color: COL.must, valign: 'top', align: 'left' }, text: '' } },
    ],
  });
  pres.defineSlideMaster({
    title: 'CONTENT', background: { color: COL.cream },
    objects: [
      { placeholder: { options: { name: 'kicker', type: 'body', x: 0.6, y: 0.22, w: 9, h: 0.32, fontSize: 12, bold: true, color: COL.mkd, charSpacing: 2 }, text: '' } },
      { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.52, w: 12.1, h: 0.75, fontSize: 30, bold: true, color: COL.ink, valign: 'top', align: 'left' }, text: '' } },
      { text: { text: "Who's Cooking the Economy?  ·  BSEC1103 Principles of Economics  ·  Chapter 2: Economic Systems", options: { x: 0.6, y: 7.05, w: 9, h: 0.3, fontSize: 10, color: C.text1, transparency: 40 } } },
    ],
    slideNumber: { x: 12.2, y: 7.03, w: 0.6, h: 0.3, fontSize: 10, color: C.text1, align: 'right' },
  });

  const ANIM = {};     // slideIndex -> array of steps (array of objectNames)
  let sIdx = 0;
  const seenSec = new Set();
  function newSlide(master, section) { if (!seenSec.has(section)) { pres.addSection({ title: section }); seenSec.add(section); } sIdx += 1; return pres.addSlide({ masterName: master, sectionTitle: section }); }
  function addStep(names) { (ANIM[sIdx] = ANIM[sIdx] || []).push(names); }
  let uid = 0; const nm = (p) => `${p}_${++uid}`;

  // ---------------------------------------------------------------- helpers
  async function iconCircle(slide, iconName, x, y, d, fillCol, iconHex = 'FFFFFF', name) {
    const n1 = name || nm('icbg');
    slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fillCol }, line: { color: fillCol }, objectName: n1 });
    const n2 = n1 + '_i';
    slide.addImage({ data: await icon(iconName, iconHex), x: x + d * 0.24, y: y + d * 0.24, w: d * 0.52, h: d * 0.52, objectName: n2, altText: iconName.replace('Fa', '') + ' icon' });
    return [n1, n2];
  }
  function card(slide, x, y, w, h, opts = {}) {
    const n = opts.name || nm('card');
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: opts.fill || COL.white }, line: { color: opts.line || 'E4D7BF', width: 0.75 },
      shadow: { type: 'outer', color: '000000', opacity: 0.12, blur: 6, offset: 2, angle: 90 }, objectName: n });
    return n;
  }
  // Arabic explanation panel
  function arBox(slide, x, y, w, h, paras, col = COL.mx, title = 'الشرح بالعربي') {
    const n = card(slide, x, y, w, h, { fill: COL.white });
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + w - 2.05, y: y + 0.18, w: 1.85, h: 0.42, rectRadius: 0.2, fill: { color: col }, line: { color: col }, objectName: n + '_pill' });
    slide.addText(title, { x: x + w - 2.05, y: y + 0.18, w: 1.85, h: 0.42, fontFace: AR, fontSize: 14, bold: true, color: COL.white, align: 'center', valign: 'middle', rtlMode: true, lang: 'ar-SA', margin: 0, isTextBox: true, objectName: n + '_pt' });
    const runs = [];
    paras.forEach((p, i) => {
      const parts = Array.isArray(p) ? p : [{ text: p }];
      parts.forEach((r, j) => runs.push({ text: r.text, options: { bold: !!r.bold, color: r.color || COL.ink, breakLine: j === parts.length - 1 && i < paras.length - 1, paraSpaceAfter: 6 } }));
    });
    slide.addText(runs, { x: x + 0.22, y: y + 0.72, w: w - 0.44, h: h - 0.85, fontFace: AR, fontSize: 15, align: 'right', valign: 'top', rtlMode: true, lang: 'ar-SA', lineSpacingMultiple: 1.12, isTextBox: true, objectName: n + '_t' });
    return [n, n + '_pill', n + '_pt', n + '_t'];
  }
  // English paragraph block with optional bold runs; items: string | [{text,bold}] ; bullets
  function enText(slide, items, x, y, w, h, opts = {}) {
    const runs = [];
    items.forEach((it, i) => {
      const parts = Array.isArray(it) ? it : [{ text: it }];
      parts.forEach((r, j) => {
        const last = j === parts.length - 1;
        const o = { bold: !!r.bold, color: r.color || COL.ink, italic: !!r.italic };
        if (j === 0 && opts.bullet) o.bullet = { indent: 18 };
        if (last && i < items.length - 1) o.breakLine = true;
        o.paraSpaceAfter = opts.gap ?? 8;
        runs.push({ text: r.text, options: o });
      });
    });
    const n = opts.name || nm('en');
    slide.addText(runs, { x, y, w, h, fontSize: opts.size || 17, valign: 'top', isTextBox: true, objectName: n, margin: opts.margin ?? 0.05 });
    return n;
  }
  function label(slide, text, x, y, w, col = COL.mkd, size = 12) {
    slide.addText(text, { x, y, w, h: 0.3, fontSize: size, bold: true, color: col, charSpacing: 2, isTextBox: true, margin: 0 });
  }
  function title(slide, kicker, t) {
    slide.addText(kicker, { placeholder: 'kicker' });
    slide.addText(t, { placeholder: 'title' });
  }
  async function stepsList(slide, steps, x, y, w, rowH, col, animate = true) {
    // numbered rows: [{en, ar}]  - EN left, AR under it
    for (let i = 0; i < steps.length; i++) {
      const yy = y + i * rowH; const g = nm('step');
      slide.addShape(pres.shapes.OVAL, { x, y: yy + 0.04, w: 0.46, h: 0.46, fill: { color: col }, line: { color: col }, objectName: g + '_c' });
      slide.addText(String(i + 1), { x, y: yy + 0.04, w: 0.46, h: 0.46, fontSize: 16, bold: true, color: COL.white, align: 'center', valign: 'middle', margin: 0, isTextBox: true, objectName: g + '_n' });
      slide.addText(steps[i].en, { x: x + 0.62, y: yy - 0.02, w: w - 0.62, h: rowH * 0.5, fontSize: 15.5, color: COL.ink, valign: 'top', margin: 0, isTextBox: true, objectName: g + '_e' });
      slide.addText(steps[i].ar, { x: x + 0.62, y: yy + rowH * 0.47, w: w - 0.62, h: rowH * 0.48, fontFace: AR, fontSize: 14, color: '4A4F5E', align: 'right', valign: 'top', rtlMode: true, lang: 'ar-SA', margin: 0, isTextBox: true, objectName: g + '_a' });
      if (animate) addStep([g + '_c', g + '_n', g + '_e', g + '_a']);
    }
  }
  // native flowchart: nodes [{icon,label}] with arrows; plus optional "+"
  async function flowchart(slide, nodes, x, y, w, col, arrows, plusAfter = -1) {
    const nw = 2.0, nh = 1.45; const gap = (w - nodes.length * nw) / (nodes.length - 1);
    const names = [];
    for (let i = 0; i < nodes.length; i++) {
      const nx = x + i * (nw + gap); const g = nm('fn');
      slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: nx, y, w: nw, h: nh, rectRadius: 0.1, fill: { color: COL.white }, line: { color: col, width: 2 }, objectName: g + '_b',
        shadow: { type: 'outer', color: '000000', opacity: 0.12, blur: 5, offset: 2, angle: 90 } });
      slide.addShape(pres.shapes.RECTANGLE, { x: nx + 0.02, y: y + 0.02, w: nw - 0.04, h: 0.14, fill: { color: col }, line: { color: col }, objectName: g + '_top' });
      slide.addImage({ data: await icon(nodes[i].icon, THEME.colors[col === COL.mk ? 'accent1' : col === COL.mx ? 'accent2' : 'accent3']), x: nx + nw / 2 - 0.27, y: y + 0.27, w: 0.54, h: 0.54, objectName: g + '_i', altText: nodes[i].label });
      slide.addText(nodes[i].label, { x: nx + 0.05, y: y + 0.85, w: nw - 0.1, h: 0.55, fontSize: 15, bold: true, color: COL.ink, align: 'center', valign: 'middle', margin: 0, isTextBox: true, objectName: g + '_l' });
      names.push([g + '_b', g + '_top', g + '_i', g + '_l']);
      if (i < nodes.length - 1) {
        const ax = nx + nw + 0.08, aw = gap - 0.16; const a = nm('fa');
        if (i === plusAfter) {
          slide.addText('+', { x: ax, y: y + 0.35, w: aw, h: 0.7, fontSize: 36, bold: true, color: col, align: 'center', valign: 'middle', isTextBox: true, objectName: a + '_p' });
          names.push([a + '_p']);
        } else {
          slide.addShape(pres.shapes.LINE, { x: ax, y: y + nh / 2, w: aw, h: 0, line: { color: col, width: 2.5, endArrowType: 'triangle' }, objectName: a + '_l' });
          if (arrows && arrows[i]) slide.addText(arrows[i], { x: ax - 0.1, y: y + nh / 2 - 0.5, w: aw + 0.2, h: 0.42, fontSize: 12, bold: true, color: col, align: 'center', valign: 'bottom', margin: 0, isTextBox: true, objectName: a + '_t' });
          names.push(arrows && arrows[i] ? [a + '_l', a + '_t'] : [a + '_l']);
        }
      }
    }
    return names; // in visual order: node, arrow, node, arrow, node
  }

  // ================================================================= SLIDES
  // ---- 1 Title
  let s = newSlide('TITLE_DARK', 'Introduction');
  s.addText("Who's Cooking the Economy?", { placeholder: 'title' });
  s.addText('Chapter 2: Economic Systems  ·  a bilingual lesson', { placeholder: 'body' });
  s.addText('الأنظمة الاقتصادية: درس ثنائي اللغة (إنجليزي وعربي)', { x: 0.7, y: 4.2, w: 8.2, h: 0.5, fontFace: AR, fontSize: 20, color: COL.white, align: 'right', rtlMode: true, lang: 'ar-SA', isTextBox: true });
  s.addText('BSEC1103 Principles of Economics', { x: 0.7, y: 1.05, w: 8, h: 0.4, fontSize: 16, bold: true, color: COL.white, charSpacing: 3, isTextBox: true });
  s.addImage({ path: path.join(IMG, 'chef.png'), x: 9.55, y: 1.0, w: 2.9, h: 3.02, altText: 'Chef character carrying a tray and a box, the poster mascot' });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 5.15, w: 11.9, h: 1.65, rectRadius: 0.12, fill: { color: '2E2E4A' }, line: { color: '3A3A5C' } });
  s.addText('Student Names', { x: 1.0, y: 5.28, w: 4, h: 0.35, fontSize: 13, bold: true, color: COL.must, charSpacing: 3, isTextBox: true, margin: 0 });
  const studs = [['Mais altoubi', '31j2573'], ['Alshima Almahrooqi', '21S252540139'], ['Nardeen alfarsi', '21J2583'], ['shatha al_umeiri', '21J25157']];
  studs.forEach(([n, id], i) => {
    s.addText([{ text: n, options: { bold: true, color: COL.white, fontSize: 18, breakLine: true } }, { text: id, options: { color: COL.must, fontSize: 15 } }],
      { x: 1.0 + i * 2.9, y: 5.7, w: 2.8, h: 0.9, valign: 'top', isTextBox: true, margin: 0 });
  });
  s.addNotes('Welcome. This lesson explains every part of our poster "Who\'s Cooking the Economy?" for Chapter 2: Economic Systems. Each slide has an English explanation and an Arabic summary. Arabic: نرحب بكم، هذا الدرس يشرح كل جزء من البوستر باللغتين.');

  // ---- 2 Lesson map + poster map
  s = newSlide('CONTENT', 'Introduction');
  title(s, 'LESSON MAP  ·  خريطة الدرس', 'How this lesson follows the poster');
  const map = [
    ['FaSeedling', 'The basic idea', 'Meaning of an economic system, scarcity, and the 3 central questions', 'المعنى، الندرة، والأسئلة الثلاثة', COL.must, 'Poster ① ②'],
    ['FaStore', 'Capitalist economy', 'Meaning, flowchart, answers, merits & demerits', 'الاقتصاد الرأسمالي', COL.mk, 'Poster ③'],
    ['FaLandmark', 'Socialist (command) economy', 'Meaning, flowchart, answers, merits & demerits', 'الاقتصاد الاشتراكي (الموجّه)', COL.cm, 'Poster ③'],
    ['FaHandshake', 'Mixed economy', 'Meaning, flowchart, answers, merits & demerits', 'الاقتصاد المختلط', COL.mx, 'Poster ③'],
    ['FaTable', 'Comparing the systems', 'The 6 criteria, the comparison table, the 3 questions', 'المقارنة والجدول والأسئلة', COL.ink, 'Poster ④ ⑤'],
    ['FaMapMarkerAlt', 'Oman', 'Why Oman is a mixed economy; government & private roles', 'عُمان: اقتصاد مختلط', COL.mx, 'Poster ⑥'],
    ['FaComments', 'Revision & questions', 'Key takeaways and model answers for the viva', 'المراجعة والأسئلة المتوقعة', COL.mkd, 'Chef’s note'],
  ];
  for (let i = 0; i < map.length; i++) {
    const col = i < 4 ? 0 : 1; const row = i < 4 ? i : i - 4;
    const x = 0.6 + col * 6.2, y = 1.55 + row * 1.33;
    card(s, x, y, 5.95, 1.15);
    await iconCircle(s, map[i][0], x + 0.2, y + 0.2, 0.75, map[i][4]);
    s.addText(map[i][1], { x: x + 1.15, y: y + 0.12, w: 3.4, h: 0.38, fontSize: 17, bold: true, color: COL.ink, margin: 0, isTextBox: true });
    s.addText(map[i][5], { x: x + 4.45, y: y + 0.12, w: 1.35, h: 0.32, fontSize: 11, bold: true, color: COL.mkd, align: 'right', margin: 0, isTextBox: true });
    s.addText(map[i][2], { x: x + 1.15, y: y + 0.5, w: 4.65, h: 0.3, fontSize: 12.5, color: '4A4F5E', margin: 0, isTextBox: true });
    s.addText(map[i][3], { x: x + 1.15, y: y + 0.78, w: 4.65, h: 0.3, fontFace: AR, fontSize: 13, color: '4A4F5E', align: 'right', rtlMode: true, lang: 'ar-SA', margin: 0, isTextBox: true });
  }
  s.addText([{ text: 'Goal: ', options: { bold: true, color: COL.mkd } }, { text: 'understand each idea well enough to explain it in your own words and answer the judges’ "why" and "what if" questions.' }],
    { x: 6.8, y: 5.6, w: 5.95, h: 0.9, fontSize: 14, color: COL.ink, isTextBox: true, margin: 0.05 });
  s.addNotes('Use this map to show the audience the route: basic idea, the three systems, the comparison, Oman, then revision. Each part matches a numbered section of the poster (1 to 6). Arabic: نتبع ترتيب البوستر من 1 إلى 6.');

  // ================= PART 1
  s = newSlide('SECTION_DARK', 'Part 1: The basic idea');
  s.addText('Part 1 · The basic idea', { placeholder: 'title' });
  s.addText('Why every society needs an economic system\nالجزء الأول: الفكرة الأساسية', { placeholder: 'body' });
  s.addImage({ path: path.join(IMG, 'pantry.png'), x: 8.7, y: 2.1, w: 3.9, h: 2.45, altText: 'Pantry with limited jars of land, labour and capital and a long list of wants' });
  s.addNotes('Part 1 builds the foundation: what an economic system is, why scarcity makes it necessary, and the three central questions every system must answer.');

  // ---- What is an economic system
  s = newSlide('CONTENT', 'Part 1: The basic idea');
  title(s, 'POSTER ①  ·  MEANING', 'What is an economic system?');
  card(s, 0.6, 1.5, 7.35, 1.75, { fill: 'FFF4E0', line: 'F0B13B' });
  label(s, 'DEFINITION (CHAPTER 2 SLIDES)', 0.85, 1.65, 6);
  enText(s, [[{ text: 'An economic system is the ' }, { text: 'means by which societies or governments organise and distribute', bold: true }, { text: ' available resources, services and goods across a region or country. It refers to the ' }, { text: 'mode of production and distribution', bold: true }, { text: ' within which economic activity takes place.' }]], 0.85, 1.98, 6.95, 1.25, { size: 16 });
  label(s, 'IN SIMPLE WORDS', 0.6, 3.5, 6, COL.mx);
  enText(s, [
    [{ text: 'It is the ' }, { text: '"way a country runs its economy"', bold: true }, { text: ': who produces, how they produce, and who receives the goods.' }],
    [{ text: 'Resources', bold: true }, { text: ' = what we produce with: land, labour and capital.' }],
    [{ text: 'Production', bold: true }, { text: ' = making goods and services. ' }, { text: 'Distribution', bold: true }, { text: ' = sharing them among people.' }],
    [{ text: 'Poster metaphor: ', bold: true, color: COL.mkd }, { text: 'the economic system is the ' }, { text: 'kitchen', bold: true }, { text: ' that decides what to cook, how, and for whom.' }],
  ], 0.6, 3.82, 7.35, 2.9, { bullet: true, size: 16 });
  arBox(s, 8.3, 1.5, 4.45, 5.25, [
    [{ text: 'النظام الاقتصادي: ', bold: true }, { text: 'هو الوسيلة التي ينظّم بها المجتمع أو الحكومة الموارد والسلع والخدمات المتاحة ويوزّعها داخل منطقة أو دولة.' }],
    [{ text: 'أي أنه ' }, { text: '«أسلوب الإنتاج والتوزيع»', bold: true }, { text: ' الذي يتم فيه النشاط الاقتصادي.' }],
    [{ text: 'الموارد: ', bold: true }, { text: 'الأرض والعمل ورأس المال.' }],
    [{ text: 'تشبيه البوستر: ', bold: true }, { text: 'النظام الاقتصادي مثل «المطبخ» الذي يقرّر ماذا نطبخ، وكيف نطبخ، ولمن نقدّم الطعام.' }],
  ], COL.must);
  s.addNotes('Read the definition from the Chapter 2 slides, then explain it simply: an economic system is the way a country organises production and distribution. On the poster, section 1 shows this definition. Arabic: النظام الاقتصادي = أسلوب الإنتاج والتوزيع.');

  // ---- Why every society needs one
  s = newSlide('CONTENT', 'Part 1: The basic idea');
  title(s, 'POSTER ②  ·  SCARCITY', 'Why does every society need an economic system?');
  s.addImage({ path: path.join(IMG, 'pantry.png'), x: 0.6, y: 1.55, w: 3.1, h: 1.94, altText: 'Pantry: limited jars of land, labour and capital; two empty jars; a long wants list' });
  enText(s, [
    [{ text: 'Resources are scarce: ', bold: true, color: COL.mkd }, { text: 'land, labour and capital are limited ("limited stock", empty jars).' }],
    [{ text: 'Wants are unlimited: ', bold: true, color: COL.mkd }, { text: 'people always want more (the long "WANTS" list).' }],
    [{ text: 'So every society must choose. ', bold: true }, { text: 'It cannot produce everything for everyone.' }],
    [{ text: 'The economic system is the method a society uses to make these choices.', bold: true }],
  ], 3.9, 1.45, 4.1, 2.7, { bullet: true, size: 14, gap: 4 });
  card(s, 0.6, 4.25, 7.35, 2.45, { fill: 'EAF5F1', line: '2F8F7A' });
  label(s, 'SIMPLE EXAMPLE', 0.85, 4.4, 6, COL.mx);
  enText(s, [
    'A country has one piece of land. Should it grow dates, build a factory, or build a hospital? It cannot do all three on the same land.',
    [{ text: 'Someone must decide. ' }, { text: 'Who decides, and how, is exactly what separates the three economic systems.', bold: true }],
  ], 0.85, 4.72, 6.9, 1.9, { size: 16 });
  arBox(s, 8.3, 1.5, 4.45, 5.25, [
    [{ text: 'الندرة (Scarcity): ', bold: true }, { text: 'الموارد مثل الأرض والعمل ورأس المال محدودة.' }],
    [{ text: 'الرغبات غير محدودة: ', bold: true }, { text: 'الناس يريدون دائمًا المزيد من السلع والخدمات.' }],
    [{ text: 'لذلك لا يستطيع أي مجتمع إنتاج كل شيء للجميع، ويجب أن يختار.' }],
    [{ text: 'النظام الاقتصادي ', bold: true }, { text: 'هو الطريقة التي يتخذ بها المجتمع هذه الاختيارات.' }],
    [{ text: 'مثال: ', bold: true }, { text: 'قطعة أرض واحدة: هل نزرعها نخيلًا أم نبني عليها مصنعًا أم مستشفى؟' }],
  ], COL.mx);
  s.addNotes('Key idea: scarcity. Limited resources and unlimited wants force choices, and an economic system is the way those choices are made (Mankiw, 2021). Point to the pantry on the poster: limited stock, empty jars, and a long wants list.');

  // ---- Three central questions
  s = newSlide('CONTENT', 'Part 1: The basic idea');
  title(s, 'POSTER ②  ·  THE CORE PROBLEM', 'The three central economic questions');
  const qs = [
    ['FaBoxOpen', 'WHAT to produce?', 'Which goods and services, and how much of each?', 'Example: more food or more cars?', 'ماذا ننتج؟', 'أي السلع والخدمات، وبأي كمية؟', COL.mk],
    ['FaCogs', 'HOW to produce?', 'Which methods and technology, and who produces?', 'Example: machines or many workers?', 'كيف ننتج؟', 'بأي طريقة وتقنية، ومن يقوم بالإنتاج؟', COL.cm],
    ['FaUsers', 'FOR WHOM to produce?', 'Who receives the goods: how is output distributed?', 'Example: everyone equally, or those who can pay?', 'لمن ننتج؟', 'كيف تُوزَّع السلع بين الناس، ومن يحصل عليها؟', COL.mx],
  ];
  for (let i = 0; i < 3; i++) {
    const x = 0.6 + i * 4.1, q = qs[i];
    const cn = card(s, x, 1.55, 3.85, 4.15);
    const ic = await iconCircle(s, q[0], x + 1.45, 1.75, 0.95, q[6]);
    s.addText(q[1], { x: x + 0.15, y: 2.8, w: 3.55, h: 0.45, fontSize: 21, bold: true, color: q[6], align: 'center', isTextBox: true, margin: 0, objectName: cn + '_h' });
    s.addText(q[2], { x: x + 0.25, y: 3.3, w: 3.35, h: 0.75, fontSize: 15.5, color: COL.ink, align: 'center', isTextBox: true, margin: 0, objectName: cn + '_d' });
    s.addText(q[3], { x: x + 0.25, y: 4.08, w: 3.35, h: 0.55, fontSize: 14, italic: true, color: '4A4F5E', align: 'center', isTextBox: true, margin: 0, objectName: cn + '_x' });
    s.addText([{ text: q[4], options: { bold: true, breakLine: true, color: q[6] } }, { text: q[5] }], { x: x + 0.25, y: 4.72, w: 3.35, h: 0.9, fontFace: AR, fontSize: 15, color: COL.ink, align: 'center', rtlMode: true, lang: 'ar-SA', isTextBox: true, margin: 0, objectName: cn + '_a' });
    addStep([cn, ...ic, cn + '_h', cn + '_d', cn + '_x', cn + '_a']);
  }
  card(s, 0.6, 5.95, 12.15, 0.85, { fill: 'FFF4E0', line: 'F0B13B' });
  s.addText([{ text: 'Every economic system must answer all three. ', options: { bold: true } }, { text: 'The difference is WHO answers them: the market, the government, or both.' }],
    { x: 0.85, y: 6.0, w: 7.2, h: 0.75, fontSize: 14.5, color: COL.ink, valign: 'middle', isTextBox: true, margin: 0 });
  s.addText('كل نظام يجيب عن الأسئلة الثلاثة؛ الفرق هو مَن يجيب.', { x: 8.2, y: 6.0, w: 4.35, h: 0.75, fontFace: AR, fontSize: 15, bold: true, color: COL.ink, align: 'right', valign: 'middle', rtlMode: true, lang: 'ar-SA', isTextBox: true, margin: 0 });
  s.addNotes('Reveal one question per click. WHAT = which goods and how much. HOW = methods, technology, who produces. FOR WHOM = distribution of output. Stress the last line: all systems answer the same questions; they differ in who decides.');

  // ---- Three kitchens overview
  s = newSlide('CONTENT', 'Part 1: The basic idea');
  title(s, 'POSTER ③  ·  THE KEY TO THE POSTER', 'Three kitchens = three economic systems');
  const kit = [
    ['kit_market.png', 'Market Bistro', 'Capitalist (market / free) economy', 'Buyers and sellers decide through prices and profit.', 'الاقتصاد الرأسمالي: السوق يقرّر', COL.mk],
    ['kit_command.png', 'State Canteen', 'Socialist (command) economy', 'A central authority (the government) decides everything.', 'الاقتصاد الاشتراكي (الموجّه): الحكومة تقرّر', COL.cm],
    ['kit_mixed.png', 'Mixed Food Court', 'Mixed economy', 'The public and private sectors decide together.', 'الاقتصاد المختلط: القطاعان العام والخاص معًا', COL.mx],
  ];
  for (let i = 0; i < 3; i++) {
    const x = 0.6 + i * 4.1, k = kit[i];
    const cn = card(s, x, 1.5, 3.85, 4.6);
    s.addImage({ path: path.join(IMG, k[0]), x: x + 0.12, y: 1.62, w: 3.61, h: 1.756, objectName: cn + '_img', altText: k[1] + ' illustration from the poster' });
    s.addText(k[1], { x: x + 0.2, y: 3.5, w: 3.45, h: 0.42, fontSize: 20, bold: true, color: k[5], isTextBox: true, margin: 0, objectName: cn + '_h' });
    s.addText(k[2], { x: x + 0.2, y: 3.92, w: 3.45, h: 0.35, fontSize: 14, bold: true, color: COL.ink, isTextBox: true, margin: 0, objectName: cn + '_s' });
    s.addText(k[3], { x: x + 0.2, y: 4.3, w: 3.45, h: 0.7, fontSize: 15, color: COL.ink, isTextBox: true, margin: 0, objectName: cn + '_d' });
    s.addText(k[4], { x: x + 0.2, y: 5.1, w: 3.45, h: 0.8, fontFace: AR, fontSize: 15, bold: true, color: k[5], align: 'right', rtlMode: true, lang: 'ar-SA', isTextBox: true, margin: 0, objectName: cn + '_a' });
    addStep([cn, cn + '_img', cn + '_h', cn + '_s', cn + '_d', cn + '_a']);
  }
  s.addText('Source: the three main types of economic system, Chapter 2 slides (Fernando, 2026).', { x: 0.6, y: 6.3, w: 12.1, h: 0.4, fontSize: 12, italic: true, color: '6A6F7D', isTextBox: true, margin: 0 });
  s.addNotes('This is the key to the whole poster. Each restaurant is one system: Market Bistro = capitalist, State Canteen = socialist (command), Mixed Food Court = mixed. The question in each kitchen is always: who decides what to cook, how, and for whom?');

  // ================= helper to build a system section (3 slides + divider)
  async function systemSection(cfg) {
    // divider
    let d = newSlide('SECTION_DARK', cfg.section);
    d.addText(cfg.divTitle, { placeholder: 'title' });
    d.addText(cfg.divSub, { placeholder: 'body' });
    d.addImage({ path: path.join(IMG, cfg.img), x: 8.05, y: 2.4, w: 4.7, h: 2.286, altText: cfg.kitchen + ' illustration' });
    d.addNotes(cfg.divNotes);

    // meaning & features
    let t = newSlide('CONTENT', cfg.section);
    title(t, cfg.kicker1, cfg.title1);
    card(t, 0.6, 1.5, 7.35, 1.4, { fill: cfg.tint, line: cfg.lineHex });
    label(t, 'MEANING (CHAPTER 2 SLIDES)', 0.85, 1.6, 6, cfg.col);
    enText(t, [cfg.meaning], 0.85, 1.9, 6.95, 1.0, { size: 15.5 });
    label(t, 'KEY FEATURES', 0.6, 3.1, 4, cfg.col);
    for (let i = 0; i < cfg.features.length; i++) {
      const f = cfg.features[i]; const y = 3.42 + i * 0.67;
      await iconCircle(t, f[0], 0.6, y, 0.5, cfg.col);
      enText(t, [[{ text: f[1], bold: true }, { text: f[2] }]], 1.25, y + 0.02, 6.7, 0.6, { size: 15 });
    }
    arBox(t, 8.3, 1.5, 4.45, 5.25, cfg.arMeaning, cfg.col);
    t.addNotes(cfg.notes1);

    // flowchart step by step
    t = newSlide('CONTENT', cfg.section);
    title(t, cfg.kicker2, cfg.title2);
    const parts = await flowchart(t, cfg.flow.nodes, 0.9, 1.55, 11.5, cfg.col, cfg.flow.arrows, cfg.flow.plusAfter);
    if (cfg.flow.returnText) {
      const r = nm('ret');
      t.addShape(pres.shapes.LINE, { x: 1.9, y: 3.3, w: 0, h: 0.25, line: { color: cfg.col, width: 2, beginArrowType: 'triangle' }, objectName: r + '_a' });
      t.addShape(pres.shapes.LINE, { x: 1.9, y: 3.55, w: 9.5, h: 0, line: { color: cfg.col, width: 2, dashType: 'dash' }, objectName: r + '_b' });
      t.addShape(pres.shapes.LINE, { x: 11.4, y: 3.0, w: 0, h: 0.55, line: { color: cfg.col, width: 2 }, objectName: r + '_c' });
      t.addText(cfg.flow.returnText, { x: 4.4, y: 3.32, w: 4.5, h: 0.45, fontSize: 13, bold: true, color: cfg.col, align: 'center', fill: { color: cfg.cream || 'FBF1E1' }, isTextBox: true, margin: 0, objectName: r + '_t' });
      parts.push([r + '_a', r + '_b', r + '_c', r + '_t']);
    }
    if (cfg.flow.banner) {
      const b = nm('ban');
      t.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 3.4, y: 3.3, w: 6.5, h: 0.45, rectRadius: 0.2, fill: { color: cfg.col }, line: { color: cfg.col }, objectName: b + '_r' });
      t.addText(cfg.flow.banner, { x: 3.4, y: 3.3, w: 6.5, h: 0.45, fontSize: 14, bold: true, color: COL.white, align: 'center', valign: 'middle', isTextBox: true, margin: 0, objectName: b + '_t' });
      parts.push([b + '_r', b + '_t']);
    }
    // group flow parts into reveal steps (node + following arrow)
    const groups = []; let cur = [];
    parts.forEach((p, i) => { cur.push(...p); if (i % 2 === 0 || i === parts.length - 1) { groups.push(cur); cur = []; } });
    groups.forEach(g => addStep(g));
    await stepsList(t, cfg.steps, 0.6, 4.05, 7.6, 0.72, cfg.col);
    card(t, 8.6, 4.05, 4.15, 2.75, { fill: cfg.tint, line: cfg.lineHex });
    label(t, 'EXAMPLE  ·  مثال', 8.85, 4.18, 3.6, cfg.col);
    t.addText(cfg.example.en, { x: 8.85, y: 4.5, w: 3.7, h: 1.25, fontSize: 14, color: COL.ink, valign: 'top', isTextBox: true, margin: 0 });
    t.addText(cfg.example.ar, { x: 8.85, y: 5.75, w: 3.7, h: 1.0, fontFace: AR, fontSize: 13.5, color: COL.ink, align: 'right', valign: 'top', rtlMode: true, lang: 'ar-SA', isTextBox: true, margin: 0 });
    t.addNotes(cfg.notes2);

    // 3 questions + merits/demerits
    t = newSlide('CONTENT', cfg.section);
    title(t, cfg.kicker3, cfg.title3);
    const qn = [['FaBoxOpen', 'WHAT?', 'ماذا؟'], ['FaCogs', 'HOW?', 'كيف؟'], ['FaUsers', 'FOR WHOM?', 'لمن؟']];
    for (let i = 0; i < 3; i++) {
      const y = 1.5 + i * 0.98; const cn = card(t, 0.6, y, 6.0, 0.86);
      await iconCircle(t, qn[i][0], 0.75, y + 0.13, 0.6, cfg.col);
      t.addText([{ text: qn[i][1] + '  ', options: { bold: true, color: cfg.col } }, { text: cfg.answers[i][0] }], { x: 1.5, y: y + 0.05, w: 5.0, h: 0.42, fontSize: 15.5, color: COL.ink, isTextBox: true, margin: 0, valign: 'middle' });
      t.addText(qn[i][2] + ' ' + cfg.answers[i][1], { x: 1.5, y: y + 0.45, w: 5.0, h: 0.36, fontFace: AR, fontSize: 13.5, color: '4A4F5E', align: 'right', rtlMode: true, lang: 'ar-SA', isTextBox: true, margin: 0 });
    }
    // merits / demerits
    const md = [['ADVANTAGES (MERITS)', 'FaCheckCircle', '2E8A50', 'EAF5EE', cfg.merits], ['DISADVANTAGES (DEMERITS)', 'FaTimesCircle', 'C0392B', 'FBEAE8', cfg.demerits]];
    for (let j = 0; j < 2; j++) {
      const x = 6.85 + j * 3.0; const cn = card(t, x, 1.5, 2.9, 4.4, { fill: md[j][3] });
      t.addImage({ data: await icon(md[j][1], md[j][2]), x: x + 0.18, y: 1.66, w: 0.36, h: 0.36, objectName: cn + '_i', altText: md[j][0] });
      t.addText(md[j][0], { x: x + 0.6, y: 1.62, w: 2.25, h: 0.45, fontSize: 11.5, bold: true, color: md[j][2], valign: 'middle', isTextBox: true, margin: 0, objectName: cn + '_h' });
      const items = md[j][4].map(m => [{ text: m[0], bold: true }, { text: m[1] ? ': ' + m[1] : '' }]);
      enText(t, items, x + 0.15, 2.15, 2.65, 2.4, { bullet: true, size: 13.5, gap: 5, name: cn + '_t' });
      t.addText(md[j][4].map((m, k) => ({ text: m[2], options: { breakLine: k < md[j][4].length - 1, paraSpaceAfter: 3 } })),
        { x: x + 0.15, y: 4.55, w: 2.65, h: 1.3, fontFace: AR, fontSize: 12.5, color: '4A4F5E', align: 'right', valign: 'top', rtlMode: true, lang: 'ar-SA', isTextBox: true, margin: 0, objectName: cn + '_a' });
      addStep([cn, cn + '_i', cn + '_h', cn + '_t', cn + '_a']);
    }
    card(t, 0.6, 4.5, 6.0, 1.4, { fill: cfg.tint, line: cfg.lineHex });
    label(t, 'DIFFICULT WORDS  ·  مصطلحات', 0.85, 4.6, 5.5, cfg.col);
    cfg.terms.forEach((tm, k) => {
      t.addText([{ text: tm[0] + ' ', options: { bold: true } }, { text: '= ' + tm[1] }], { x: 0.85, y: 4.92 + k * 0.46, w: 4.1, h: 0.44, fontSize: 12.5, color: COL.ink, valign: 'middle', isTextBox: true, margin: 0 });
      t.addText(tm[2], { x: 5.0, y: 4.92 + k * 0.46, w: 1.45, h: 0.44, fontFace: AR, fontSize: 13.5, bold: true, color: cfg.col, align: 'right', valign: 'middle', rtlMode: true, lang: 'ar-SA', isTextBox: true, margin: 0 });
    });
    card(t, 0.6, 6.05, 12.15, 0.75, { fill: COL.white });
    t.addText([{ text: 'On the poster: ', options: { bold: true, color: cfg.col } }, { text: cfg.posterLink }], { x: 0.85, y: 6.1, w: 11.7, h: 0.65, fontSize: 13.5, color: COL.ink, valign: 'middle', isTextBox: true, margin: 0 });
    t.addNotes(cfg.notes3);
  }

  // ================= PART 2-4: the three systems
  await systemSection({
    section: 'Part 2: Capitalist economy', img: 'kit_market.png', kitchen: 'Market Bistro', col: COL.mk, tint: 'FCE6DE', lineHex: 'D9503F',
    divTitle: 'Part 2 · Capitalist economy', divSub: 'The Market Bistro: also called a market or free economy\nالجزء الثاني: الاقتصاد الرأسمالي (اقتصاد السوق / الحر)',
    divNotes: 'Part 2: the capitalist economy, shown on the poster as the Market Bistro.',
    kicker1: 'CAPITALIST ECONOMY  ·  MEANING', title1: 'Capitalist economy: the market decides',
    meaning: [{ text: 'Factors of production are ' }, { text: 'privately owned by institutions and citizens', bold: true }, { text: '. There is ' }, { text: 'no interference by the government', bold: true }, { text: '. It is a ' }, { text: 'free economy', bold: true }, { text: ': consumers, businesses and resource suppliers have freedom of choice.' }],
    features: [
      ['FaKey', 'Private property: ', 'individuals own land, factories and businesses.'],
      ['FaStore', 'Freedom of choice: ', 'anyone may start a business; consumers buy what they want with their income.'],
      ['FaChartLine', 'Profit motive: ', 'all economic activities are guided by the motive of profit.'],
      ['FaTrophy', 'Competition: ', 'producers compete and offer variety to match consumers’ tastes.'],
      ['FaLandmark', 'Limited government: ', 'the government has little role in the economy.'],
    ],
    arMeaning: [
      [{ text: 'الاقتصاد الرأسمالي (اقتصاد السوق أو الاقتصاد الحر): ', bold: true }, { text: 'عوامل الإنتاج مملوكة ملكية خاصة للأفراد والمؤسسات، ولا تتدخّل الحكومة.' }],
      [{ text: 'حرية الاختيار: ', bold: true }, { text: 'للمستهلك أن يشتري ما يريد حسب دخله، وللمنتج أن ينتج سلعًا متنوعة تناسب أذواق المستهلكين.' }],
      [{ text: 'دافع الربح: ', bold: true }, { text: 'كل الأنشطة الاقتصادية يوجّهها الربح، مع وجود المنافسة.' }],
      [{ text: 'في البوستر: ', bold: true }, { text: 'محلات متنافسة («أفضل سعر!» و«طبق جديد!»)، وزبون يختار، ومبنى حكومي صغير يدل على تدخل حكومي محدود.' }],
    ],
    notes1: 'Explain the meaning using the Chapter 2 definition, then the five features (private property, freedom of choice, profit motive, competition, limited government; slides 4-6). Link each to the Market Bistro picture: competing stalls = competition, "Which one?" = freedom of choice, the tiny circled government building = limited government.',
    kicker2: 'CAPITALIST ECONOMY  ·  FLOWCHART', title2: 'How the capitalist flowchart works, step by step',
    flow: { nodes: [{ icon: 'FaUsers', label: 'Consumers' }, { icon: 'FaTag', label: 'Market price' }, { icon: 'FaIndustry', label: 'Producers' }], arrows: ['demand', 'profit signal'], returnText: 'goods for buyers who can pay' },
    steps: [
      { en: 'Consumers spend their income on what they want: this is demand.', ar: 'المستهلكون ينفقون دخلهم على ما يريدون، وهذا هو الطلب.' },
      { en: 'Demand shapes the market price, which signals where profit can be made.', ar: 'الطلب يشكّل سعر السوق الذي يوضّح أين يمكن تحقيق الربح.' },
      { en: 'Producers follow profit and competition, offering a variety of goods.', ar: 'المنتجون يتبعون الربح والمنافسة فيقدّمون سلعًا متنوعة.' },
      { en: 'Goods return to consumers who can pay (the dashed arrow).', ar: 'تعود السلع إلى المستهلكين القادرين على الدفع (السهم المتقطع).' },
    ],
    example: { en: 'Many people start buying fresh juice. Juice shops earn more profit, so new juice shops open, with no government order needed.', ar: 'إذا زاد شراء العصير، تربح محلات العصير أكثر، فتفتح محلات جديدة دون أمر من الحكومة.' },
    notes2: 'Click through the flowchart: (1) consumers create demand with their income; (2) the market price forms and signals profit; (3) producers respond for profit and compete; (4) the dashed return arrow shows goods going to buyers who can pay. Nobody gives orders: prices and profit coordinate the economy.',
    kicker3: 'CAPITALIST ECONOMY  ·  ANSWERS, MERITS & DEMERITS', title3: 'Capitalism: its answers, merits and demerits',
    answers: [['Whatever consumers demand.', 'ما يطلبه المستهلكون.'], ['Producers choose methods, for profit.', 'المنتجون يختارون طريقة الإنتاج بهدف الربح.'], ['Buyers, according to their income.', 'المشترون حسب دخلهم.']],
    merits: [['Equal opportunities', 'anyone can build wealth through effort', 'فرص متساوية لتكوين الثروة بالجهد'], ['Innovation', 'risk-taking entrepreneurs bring new technology, growth and productivity', 'الابتكار والنمو وزيادة الإنتاجية']],
    demerits: [['Economic inequality', 'resources concentrate; the rich get richer, the poor poorer', 'عدم المساواة: الغني يزداد غنى والفقير فقرًا'], ['Limited government control', 'no government welfare, so great poverty can occur', 'لا رعاية حكومية فقد ينتشر الفقر']],
    terms: [['Entrepreneur', 'a person who takes the risk of starting a business', 'رائد الأعمال'], ['Welfare', 'help that supports people’s well-being', 'الرعاية الاجتماعية']],
    posterLink: 'the Market Bistro card, the first column of the 3-questions chalkboard, and the "Capitalist / Market" column of the comparison table.',
    notes3: 'Answers to the three questions: what = consumer demand; how = producers choose, for profit; for whom = buyers by income. Merits and demerits come from Chapter 2 slide 7. Be ready to explain why inequality happens: resources concentrate in a few hands.',
  });

  await systemSection({
    section: 'Part 3: Socialist economy', img: 'kit_command.png', kitchen: 'State Canteen', col: COL.cm, tint: 'E0E6F3', lineHex: '2E4A86',
    divTitle: 'Part 3 · Socialist (command) economy', divSub: 'The State Canteen: a central authority plans everything\nالجزء الثالث: الاقتصاد الاشتراكي (الموجّه)',
    divNotes: 'Part 3: the socialist or command economy, shown on the poster as the State Canteen.',
    kicker1: 'SOCIALIST (COMMAND) ECONOMY  ·  MEANING', title1: 'Socialist economy: the central authority decides',
    meaning: [{ text: 'The ' }, { text: 'government owns the factors of production and distribution', bold: true }, { text: ', including financial institutions, industries, transport and communication. A ' }, { text: 'central authority takes all decisions', bold: true }, { text: ' and ' }, { text: 'prices are fixed', bold: true }, { text: ' by it.' }],
    features: [
      ['FaLandmark', 'Government ownership: ', 'the means of production are owned by the government.'],
      ['FaClipboardList', 'Central planning: ', 'decides what and how much, how to organise production, and to whom.'],
      ['FaTag', 'Fixed prices: ', 'prices do not move freely; products of high quality at reasonable prices.'],
      ['FaHeart', 'Social welfare: ', 'the chief motivating force behind all economic activities.'],
      ['FaHardHat', 'Jobs for all: ', 'the economy aims at equal opportunities of employment for all.'],
    ],
    arMeaning: [
      [{ text: 'الاقتصاد الاشتراكي (الموجّه): ', bold: true }, { text: 'تملك الحكومة عوامل الإنتاج والتوزيع، ومنها المؤسسات المالية والصناعات والنقل والاتصالات.' }],
      [{ text: 'السلطة المركزية ', bold: true }, { text: 'تتخذ كل القرارات: ماذا ننتج وكم، وكيف ننظّم الإنتاج، ولمن نوزّع.' }],
      [{ text: 'الأسعار ثابتة ', bold: true }, { text: 'تحددها السلطة المركزية، والهدف هو الرفاه الاجتماعي وتوفير فرص عمل متساوية للجميع.' }],
      [{ text: 'في البوستر: ', bold: true }, { text: '«الخطة تقرّر!»، وجبة واحدة فقط، وسعر ثابت، ونفس الوجبة للجميع.' }],
    ],
    notes1: 'Use slides 8-9: government ownership (including banks, industries, transport, communication), a central authority that takes all decisions, fixed prices with quality goods at reasonable prices, social welfare as the motive, and equal employment for all. Point to the State Canteen: the planner with a megaphone, one menu, fixed price, identical trays.',
    kicker2: 'SOCIALIST (COMMAND) ECONOMY  ·  FLOWCHART', title2: 'How the command flowchart works, step by step',
    flow: { nodes: [{ icon: 'FaClipboardList', label: 'Central authority' }, { icon: 'FaIndustry', label: 'State-owned firms' }, { icon: 'FaUsers', label: 'Citizens' }], arrows: ['plan & orders', 'allocates'], banner: 'the plan sets output and fixes prices' },
    steps: [
      { en: 'The central authority makes the plan: what and how much to produce.', ar: 'السلطة المركزية تضع الخطة: ماذا ننتج وبأي كمية.' },
      { en: 'It sends orders to state-owned firms and fixes the prices.', ar: 'ترسل الأوامر إلى الشركات المملوكة للدولة وتحدّد الأسعار.' },
      { en: 'State-owned firms produce exactly what the plan says.', ar: 'الشركات الحكومية تنتج ما تقوله الخطة بالضبط.' },
      { en: 'Output is allocated to citizens; the aim is social welfare.', ar: 'يُوزَّع الإنتاج على المواطنين بهدف تحقيق الرفاه الاجتماعي.' },
    ],
    example: { en: 'The plan says: make 1 million pairs of the same school shoes this year, sold at one fixed price in state shops.', ar: 'الخطة تقول: إنتاج مليون زوج من نفس الحذاء المدرسي هذا العام، ويُباع بسعر ثابت في متاجر الدولة.' },
    notes2: 'Click through: (1) the central authority plans what and how much; (2) it gives orders and fixes prices; (3) state-owned firms produce; (4) goods are allocated to citizens. Compare with capitalism: here orders flow from the top, not from prices and profit.',
    kicker3: 'SOCIALIST (COMMAND) ECONOMY  ·  ANSWERS, MERITS & DEMERITS', title3: 'Socialism: its answers, merits and demerits',
    answers: [['Set by the central authority’s plan.', 'تحدده خطة السلطة المركزية.'], ['The state organises production.', 'الدولة تنظّم الإنتاج.'], ['The state allocates goods to citizens.', 'الدولة توزّع السلع على المواطنين.']],
    merits: [['Efficient use of resources', '', 'الاستخدام الكفء للموارد'], ['Economic stability', '', 'الاستقرار الاقتصادي'], ['Maximum social welfare', '', 'أقصى رفاه اجتماعي'], ['No monopoly', '', 'غياب الاحتكار']],
    demerits: [['Bureaucratic expansion', '', 'توسّع البيروقراطية'], ['No freedom', '', 'غياب الحرية'], ['Absence of technology', '', 'ضعف التكنولوجيا'], ['No competition', '', 'غياب المنافسة']],
    terms: [['Monopoly', 'one producer controls the whole market', 'الاحتكار'], ['Bureaucracy', 'many official rules, offices and procedures', 'البيروقراطية']],
    posterLink: 'the State Canteen card, the third column of the 3-questions chalkboard, and the "Socialist / Command" column of the comparison table.',
    notes3: 'Answers: what, how and for whom are all decided by the central authority. Merits and demerits come from slide 10. Explain "no monopoly": since the state owns production, no private firm can dominate a market. Explain "absence of technology": with no competition, there is less pressure to innovate.',
  });

  await systemSection({
    section: 'Part 4: Mixed economy', img: 'kit_mixed.png', kitchen: 'Mixed Food Court', col: COL.mx, tint: 'DCEFE8', lineHex: '2F8F7A',
    divTitle: 'Part 4 · Mixed economy', divSub: 'The Mixed Food Court: public and private cook together\nالجزء الرابع: الاقتصاد المختلط',
    divNotes: 'Part 4: the mixed economy, shown on the poster as the Mixed Food Court.',
    kicker1: 'MIXED ECONOMY  ·  MEANING', title1: 'Mixed economy: both sectors decide',
    meaning: [{ text: 'An economic system that includes a ' }, { text: 'variety of private and government control', bold: true }, { text: '. The ' }, { text: 'government and private sectors take decisions together', bold: true }, { text: ' to determine which goods and services are produced and how they are distributed.' }],
    features: [
      ['FaHandshake', 'Co-existence: ', 'public and private sectors work side by side.'],
      ['FaClipboardList', 'Economic planning: ', 'planning is used to control the economy.'],
      ['FaBalanceScale', 'Blend of motives: ', 'the profit motive is combined with social interest.'],
      ['FaShieldAlt', 'Consumer rights: ', 'consumers are safeguarded by rules.'],
      ['FaHardHat', 'Labour rights: ', 'workers’ rights are protected.'],
    ],
    arMeaning: [
      [{ text: 'الاقتصاد المختلط: ', bold: true }, { text: 'نظام يجمع بين سيطرة القطاع الخاص وسيطرة الحكومة.' }],
      [{ text: 'القطاعان العام والخاص ', bold: true }, { text: 'يتخذان القرارات معًا: أي السلع والخدمات تُنتَج وكيف تُوزَّع.' }],
      [{ text: 'خصائصه: ', bold: true }, { text: 'تعايش القطاعين، والتخطيط الاقتصادي، والجمع بين دافع الربح والمصلحة الاجتماعية، وحماية حقوق المستهلك والعمال.' }],
      [{ text: 'في البوستر: ', bold: true }, { text: 'مطبخ عام بجانب محلات خاصة، تحت لافتة «التخطيط والقواعد»، ومفتش يقول «عادل للجميع!».' }],
    ],
    notes1: 'Slides 11-13: private and government control combined; both sectors decide; features: co-existence, planning, blend of profit and social interest, and protection of consumer and labour rights (from the slide 13 diagram). In the Mixed Food Court: the public kitchen and private stalls under one "Planning & rules" banner, and an inspector with a consumer-protection shield.',
    kicker2: 'MIXED ECONOMY  ·  FLOWCHART', title2: 'How the mixed flowchart works, step by step',
    flow: { nodes: [{ icon: 'FaLandmark', label: 'Public sector' }, { icon: 'FaStore', label: 'Private sector' }, { icon: 'FaBoxOpen', label: 'Goods & services' }], arrows: [null, 'together'], plusAfter: 0, banner: 'price mechanism + government planning' },
    steps: [
      { en: 'The public sector (government) produces in the social interest.', ar: 'القطاع العام (الحكومة) ينتج لتحقيق المصلحة الاجتماعية.' },
      { en: 'The private sector produces for profit, guided by prices.', ar: 'القطاع الخاص ينتج بهدف الربح مسترشدًا بالأسعار.' },
      { en: 'Together they supply the goods and services society needs.', ar: 'معًا يوفّران السلع والخدمات التي يحتاجها المجتمع.' },
      { en: 'Government planning and rules guide both (e.g. consumer and labour rights).', ar: 'التخطيط والقوانين الحكومية توجّه القطاعين، مثل حماية المستهلك والعمال.' },
    ],
    example: { en: 'Private restaurants and shops sell food for profit, while the government runs public schools and sets rules that protect consumers and workers.', ar: 'المطاعم والمتاجر الخاصة تبيع الطعام بهدف الربح، بينما تدير الحكومة المدارس العامة وتضع قوانين تحمي المستهلك والعامل.' },
    notes2: 'Click through: the public sector, the "+" showing both sectors exist together, the private sector, and goods and services for society; then the banner: price mechanism plus government planning. This is why the mixed economy sits between the other two.',
    kicker3: 'MIXED ECONOMY  ·  ANSWERS, MERITS & DEMERITS', title3: 'Mixed economy: its answers, merits and demerits',
    answers: [['Consumer demand + national plans.', 'طلب المستهلكين مع الخطط الوطنية.'], ['Private firms + the public sector.', 'الشركات الخاصة مع القطاع العام.'], ['The market + social welfare.', 'السوق مع الرعاية الاجتماعية.']],
    merits: [['Best allocation of resources', 'it combines features of capitalism and socialism', 'أفضل توزيع للموارد لأنه يجمع مزايا النظامين'], ['Efficient allocation', 'through the price mechanism, profit motive and liberty', 'توزيع كفء عبر الأسعار والربح والحرية']],
    demerits: [['Non-cooperation', 'the two sectors may not cooperate', 'عدم التعاون بين القطاعين'], ['Inefficient public sector', 'it can burden the economy and production falls', 'قطاع عام غير كفء يثقل الاقتصاد فيقل الإنتاج']],
    terms: [['Public sector', 'businesses and services owned by the government', 'القطاع العام'], ['Private sector', 'businesses owned by individuals and companies', 'القطاع الخاص']],
    posterLink: 'the Mixed Food Court card, the middle column of the 3-questions chalkboard and the comparison table, and the Oman section, because Oman is a mixed economy.',
    notes3: 'Answers: demand plus national plans; private firms plus the public sector; the market plus social welfare. Merits and demerits come from slide 14. A likely question: why is it "the best of both"? Because it keeps the efficiency and freedom of markets while government planning protects social welfare.',
  });

  // ================= PART 5: comparison
  s = newSlide('SECTION_DARK', 'Part 5: Comparing the systems');
  s.addText('Part 5 · Comparing the systems', { placeholder: 'title' });
  s.addText('The 6 criteria, the comparison table and the 3 questions\nالجزء الخامس: المقارنة بين الأنظمة', { placeholder: 'body' });
  await iconCircle(s, 'FaTable', 9.6, 2.4, 2.2, COL.mk);
  s.addNotes('Part 5 brings the three systems together: first what each comparison criterion means, then the table, then the three questions side by side.');

  // ---- six criteria explained
  s = newSlide('CONTENT', 'Part 5: Comparing the systems');
  title(s, 'POSTER ⑤  ·  BEFORE THE TABLE', 'What do the six comparison criteria mean?');
  const crit = [
    ['FaKey', 'Ownership of resources', 'Who owns land, factories, banks and other means of production?', 'ملكية الموارد: من يملك الأرض والمصانع ووسائل الإنتاج؟'],
    ['FaLandmark', 'Role of government', 'How much does the government decide and intervene in the economy?', 'دور الحكومة: إلى أي مدى تتدخّل الحكومة وتقرّر؟'],
    ['FaTag', 'Price mechanism', 'How are prices set: freely by the market, or fixed by an authority?', 'آلية الأسعار: هل يحدّدها السوق بحرية أم تثبّتها السلطة؟'],
    ['FaBullseye', 'Motive', 'What is the main goal behind economic activity: profit or social welfare?', 'الدافع: ما الهدف الأساسي: الربح أم الرفاه الاجتماعي؟'],
    ['FaThumbsUp', 'Advantages', 'The strengths (merits) of the system.', 'المزايا: نقاط القوة في النظام.'],
    ['FaThumbsDown', 'Disadvantages', 'The weaknesses (demerits) of the system.', 'العيوب: نقاط الضعف في النظام.'],
  ];
  for (let i = 0; i < 6; i++) {
    const col = i % 3, row = Math.floor(i / 3); const x = 0.6 + col * 4.1, y = 1.5 + row * 2.65;
    const cn = card(s, x, y, 3.85, 2.45);
    const ic = await iconCircle(s, crit[i][0], x + 0.2, y + 0.2, 0.62, [COL.mk, COL.cm, COL.mx][col]);
    s.addText(crit[i][1], { x: x + 0.95, y: y + 0.22, w: 2.8, h: 0.6, fontSize: 17, bold: true, color: COL.ink, valign: 'middle', isTextBox: true, margin: 0, objectName: cn + '_h' });
    s.addText(crit[i][2], { x: x + 0.2, y: y + 0.95, w: 3.45, h: 0.75, fontSize: 14.5, color: COL.ink, valign: 'top', isTextBox: true, margin: 0, objectName: cn + '_d' });
    s.addText(crit[i][3], { x: x + 0.2, y: y + 1.7, w: 3.45, h: 0.65, fontFace: AR, fontSize: 13.5, color: '4A4F5E', align: 'right', valign: 'top', rtlMode: true, lang: 'ar-SA', isTextBox: true, margin: 0, objectName: cn + '_a' });
  }
  s.addNotes('Teach the meaning of each criterion before comparing. Students often confuse "role of government" with "ownership": ownership is who owns; role of government is how much the government decides and controls.');

  // ---- table A
  const hdrCell = (t, c) => ({ text: t, options: { bold: true, color: 'FFFFFF', fill: { color: c }, align: 'center', valign: 'middle', fontSize: 15 } });
  const lab = (t) => ({ text: t, options: { bold: true, color: HEX.ink, fill: { color: 'F3E6CC' }, valign: 'middle', fontSize: 15 } });
  const cell = (t, tint) => ({ text: t, options: { color: HEX.ink, fill: { color: tint }, valign: 'middle', fontSize: 14 } });
  const TM = 'FCE6DE', TX = 'DCEFE8', TC = 'E0E6F3';
  s = newSlide('CONTENT', 'Part 5: Comparing the systems');
  title(s, 'POSTER ⑤  ·  COMPARISON TABLE (1 OF 2)', 'Ownership, government, prices and motive');
  s.addTable([
    [hdrCell('Criteria', HEX.ink), hdrCell('Capitalist / Market', HEX.mk), hdrCell('Mixed', HEX.mx), hdrCell('Socialist / Command', HEX.cm)],
    [lab('Ownership of resources'), cell('Private: individuals and institutions own the factors of production', TM), cell('Both: public and private sectors co-exist', TX), cell('Government: owns factors of production, incl. banks, industry, transport', TC)],
    [lab('Role of government'), cell('Little: no interference', TM), cell('Plans and regulates (rules, planning)', TX), cell('Total: a central authority takes all decisions', TC)],
    [lab('Price mechanism'), cell('Free market prices', TM), cell('Market prices + government planning', TX), cell('Fixed by the central authority', TC)],
    [lab('Motive'), cell('Profit', TM), cell('Profit + social interest', TX), cell('Social welfare', TC)],
  ], { x: 0.6, y: 1.5, w: 12.15, colW: [2.55, 3.2, 3.2, 3.2], rowH: [0.5, 0.85, 0.7, 0.7, 0.55], border: { type: 'solid', color: 'FFFFFF', pt: 2 }, fontSize: 14, margin: 0.08 });
  arBox(s, 0.6, 5.0, 12.15, 1.8, [
    [{ text: 'كيف نقرأ الجدول؟ ', bold: true }, { text: 'كلما انتقلنا من الرأسمالي إلى الاشتراكي زاد دور الحكومة: الملكية تنتقل من الأفراد إلى الدولة، والأسعار من حرة إلى ثابتة، والدافع من الربح إلى الرفاه الاجتماعي. الاقتصاد المختلط في الوسط يجمع بين الاثنين.' }],
  ], COL.ink);
  s.addNotes('Read the table row by row. Pattern to remember: moving from capitalist to socialist, the government\'s role grows. Ownership moves from private to state, prices from free to fixed, and the motive from profit to social welfare. Mixed sits in the middle.');

  // ---- table B
  s = newSlide('CONTENT', 'Part 5: Comparing the systems');
  title(s, 'POSTER ⑤  ·  COMPARISON TABLE (2 OF 2)', 'Advantages and disadvantages side by side');
  s.addTable([
    [hdrCell('Criteria', HEX.ink), hdrCell('Capitalist / Market', HEX.mk), hdrCell('Mixed', HEX.mx), hdrCell('Socialist / Command', HEX.cm)],
    [lab('Advantages'), cell('+ Equal opportunities to build wealth\n+ Innovation, high growth and productivity', TM), cell('+ Best allocation of resources (best of both systems)\n+ Efficient allocation via prices, profit and liberty', TX), cell('+ Efficient use of resources\n+ Economic stability\n+ Maximum social welfare\n+ No monopoly', TC)],
    [lab('Disadvantages'), cell('– Inequality: the rich get richer, the poor poorer\n– No government welfare → great poverty', TM), cell('– The two sectors may not cooperate\n– Inefficient public sector can cause production to fall', TX), cell('– Bureaucratic expansion\n– No freedom\n– Absence of technology\n– No competition', TC)],
  ], { x: 0.6, y: 1.5, w: 12.15, colW: [2.55, 3.2, 3.2, 3.2], rowH: [0.5, 1.6, 1.6], border: { type: 'solid', color: 'FFFFFF', pt: 2 }, fontSize: 14, margin: 0.08 });
  arBox(s, 0.6, 5.4, 12.15, 1.4, [
    [{ text: 'فكرة مهمة: ', bold: true }, { text: 'لكل نظام مزايا وعيوب. ميزة نظام غالبًا تقابل عيب نظام آخر؛ فالحرية والابتكار في الرأسمالية يقابلهما غياب الحرية وضعف التكنولوجيا في الاشتراكية، والاقتصاد المختلط يحاول الجمع بين المزايا.' }],
  ], COL.ink);
  s.addNotes('Notice how one system\'s strength is often another\'s weakness: capitalism has freedom and innovation but inequality; socialism has welfare and stability but no freedom and weak technology. The mixed economy tries to combine the strengths. Sources: Chapter 2 slides 7, 10 and 14.');

  // ---- three questions matrix (chalkboard)
  s = newSlide('CONTENT', 'Part 5: Comparing the systems');
  title(s, 'POSTER ④  ·  THE CHALKBOARD', 'Who answers the three central questions?');
  const ch = (t, o = {}) => ({ text: t, options: Object.assign({ color: 'F3EEE2', fill: { color: HEX.chalk }, valign: 'middle', fontSize: 15 }, o) });
  s.addTable([
    [ch(''), ch('Capitalist / Market', { bold: true, color: 'F59A86', align: 'center' }), ch('Mixed', { bold: true, color: '7FD3BC', align: 'center' }), ch('Socialist / Command', { bold: true, color: 'A9BCF0', align: 'center' })],
    [ch('WHAT to produce?', { bold: true }), ch('Whatever consumers demand'), ch('Demand + national plans'), ch('The central authority’s plan')],
    [ch('HOW to produce?', { bold: true }), ch('Producers choose, for profit'), ch('Private firms + public sector'), ch('The state organises production')],
    [ch('FOR WHOM?', { bold: true }), ch('Buyers, by their income'), ch('Market + social welfare'), ch('The state allocates to citizens')],
  ], { x: 0.6, y: 1.5, w: 12.15, colW: [2.55, 3.2, 3.2, 3.2], rowH: [0.55, 0.62, 0.62, 0.62], border: { type: 'solid', color: '3E4C46', pt: 1 }, margin: 0.1 });
  const pats = [['FaUsers', 'Capitalist: the market decides', 'Buyers and sellers, through prices and profit.', 'السوق يقرّر عبر الأسعار والربح', COL.mk],
                ['FaHandshake', 'Mixed: both decide', 'The market and the government share decisions.', 'السوق والحكومة يقرّران معًا', COL.mx],
                ['FaLandmark', 'Socialist: the state decides', 'A central authority plans all three answers.', 'السلطة المركزية تخطّط للإجابات الثلاث', COL.cm]];
  for (let i = 0; i < 3; i++) {
    const x = 0.6 + i * 4.1; const cn = card(s, x, 4.25, 3.85, 2.5);
    const ic = await iconCircle(s, pats[i][0], x + 0.2, 4.45, 0.6, pats[i][4]);
    s.addText(pats[i][1], { x: x + 0.95, y: 4.45, w: 2.8, h: 0.6, fontSize: 15.5, bold: true, color: pats[i][4], valign: 'middle', isTextBox: true, margin: 0, objectName: cn + '_h' });
    s.addText(pats[i][2], { x: x + 0.2, y: 5.2, w: 3.45, h: 0.7, fontSize: 14.5, color: COL.ink, isTextBox: true, margin: 0, objectName: cn + '_d' });
    s.addText(pats[i][3], { x: x + 0.2, y: 5.92, w: 3.45, h: 0.6, fontFace: AR, fontSize: 14, color: '4A4F5E', align: 'right', rtlMode: true, lang: 'ar-SA', isTextBox: true, margin: 0, objectName: cn + '_a' });
    addStep([cn, ...ic, cn + '_h', cn + '_d', cn + '_a']);
  }
  s.addNotes('Read across each row: the same question has three different answers. Then reveal the pattern cards: the market decides (capitalist), both decide (mixed), the state decides (socialist). This one idea, who decides, explains the whole chalkboard.');

  // ---- spectrum memory aid
  s = newSlide('CONTENT', 'Part 5: Comparing the systems');
  title(s, 'MEMORY AID  ·  أداة للحفظ', 'One question explains everything: who decides?');
  s.addShape(pres.shapes.RECTANGLE, { x: 0.9, y: 2.3, w: 3.85, h: 0.75, fill: { color: COL.mk }, line: { color: COL.mk } });
  s.addShape(pres.shapes.RECTANGLE, { x: 4.75, y: 2.3, w: 3.85, h: 0.75, fill: { color: COL.mx }, line: { color: COL.mx } });
  s.addShape(pres.shapes.RECTANGLE, { x: 8.6, y: 2.3, w: 3.85, h: 0.75, fill: { color: COL.cm }, line: { color: COL.cm } });
  [['Capitalist', 0.9], ['Mixed', 4.75], ['Socialist (command)', 8.6]].forEach(([t, x]) => s.addText(t, { x, y: 2.3, w: 3.85, h: 0.75, fontSize: 20, bold: true, color: COL.white, align: 'center', valign: 'middle', isTextBox: true, margin: 0 }));
  s.addText('◀  more private control (market)', { x: 0.9, y: 1.7, w: 5, h: 0.45, fontSize: 15, bold: true, color: COL.mkd, isTextBox: true, margin: 0 });
  s.addText('more government control (state)  ▶', { x: 7.45, y: 1.7, w: 5, h: 0.45, fontSize: 15, bold: true, color: COL.cm, align: 'right', isTextBox: true, margin: 0 });
  const pin = nm('pin');
  s.addImage({ data: await icon('FaMapMarkerAlt', HEX.must), x: 6.42, y: 3.15, w: 0.5, h: 0.5, objectName: pin + '_i', altText: 'Map pin marking Oman in the mixed zone' });
  s.addText('Oman is here: a mixed economy', { x: 4.75, y: 3.65, w: 3.85, h: 0.4, fontSize: 15, bold: true, color: COL.ink, align: 'center', isTextBox: true, margin: 0, objectName: pin + '_t' });
  addStep([pin + '_i', pin + '_t']);
  const rows = [['Ownership', 'private', 'both', 'government'], ['Prices', 'free', 'market + plan', 'fixed'], ['Motive', 'profit', 'profit + social interest', 'social welfare']];
  rows.forEach((r, i) => {
    const y = 4.35 + i * 0.62;
    s.addText(r[0], { x: 0.9, y, w: 1.6, h: 0.5, fontSize: 14, bold: true, color: COL.ink, valign: 'middle', isTextBox: true, margin: 0 });
    [[r[1], 2.5, 'FCE6DE'], [r[2], 5.3, 'DCEFE8'], [r[3], 9.1, 'E0E6F3']].forEach(([t, x, f]) => {
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 2.8, h: 0.5, rectRadius: 0.2, fill: { color: f }, line: { color: f } });
      s.addText(t, { x, y, w: 2.8, h: 0.5, fontSize: 14, color: COL.ink, align: 'center', valign: 'middle', isTextBox: true, margin: 0 });
    });
  });
  s.addText('كلما اتجهنا يمينًا زادت سيطرة الحكومة، وكلما اتجهنا يسارًا زادت سيطرة السوق. الاقتصاد المختلط (وعُمان) في الوسط.', { x: 0.9, y: 6.3, w: 11.55, h: 0.5, fontFace: AR, fontSize: 15, color: COL.ink, align: 'right', rtlMode: true, lang: 'ar-SA', isTextBox: true, margin: 0 });
  s.addNotes('A quick memory aid: think of a line from private control to government control. Capitalism is at the market end, socialism at the state end, and the mixed economy (including Oman) in the middle. Ownership, prices and motive all change along this line.');

  // ================= PART 6: Oman
  s = newSlide('SECTION_DARK', 'Part 6: Oman');
  s.addText('Part 6 · Oman’s economic system', { placeholder: 'title' });
  s.addText('Oman’s kitchen: a mixed economy\nالجزء السادس: النظام الاقتصادي في عُمان', { placeholder: 'body' });
  s.addImage({ path: path.join(IMG, 'oman.png'), x: 9.0, y: 1.9, w: 3.2, h: 2.52, altText: 'Omani scene with a fort, palm, dallah coffee pot and dhow' });
  s.addNotes('Part 6 links the chapter to Oman, as the assignment requires.');

  s = newSlide('CONTENT', 'Part 6: Oman');
  title(s, 'POSTER ⑥  ·  OMAN', 'Why is Oman a mixed economy?');
  enText(s, [[{ text: 'Oman has the main features of a mixed economy from Chapter 2. Each feature can be matched with real evidence:' }]], 0.6, 1.45, 7.4, 0.7, { size: 16 });
  const ev = [
    ['FaHandshake', 'Public and private sectors co-exist', 'State companies (Oman Investment Authority) work alongside private firms and PPP projects.'],
    ['FaCompass', 'Planning controls the economy', 'Oman Vision 2040 is the national long-term plan.'],
    ['FaShieldAlt', 'Consumer rights are safeguarded', 'Consumer Protection Law (Royal Decree 66/2014).'],
    ['FaHardHat', 'Labour rights are protected', 'Labour Law (Royal Decree 53/2023).'],
  ];
  for (let i = 0; i < ev.length; i++) {
    const y = 2.2 + i * 1.12; const cn = card(s, 0.6, y, 7.4, 1.0);
    const ic = await iconCircle(s, ev[i][0], 0.78, y + 0.18, 0.64, COL.mx);
    s.addText([{ text: 'Feature: ', options: { bold: true, color: COL.mx } }, { text: ev[i][1], options: { bold: true } }], { x: 1.6, y: y + 0.06, w: 6.25, h: 0.42, fontSize: 15, color: COL.ink, valign: 'middle', isTextBox: true, margin: 0, objectName: cn + '_h' });
    s.addText([{ text: 'Oman: ', options: { bold: true, color: COL.mkd } }, { text: ev[i][2] }], { x: 1.6, y: y + 0.48, w: 6.25, h: 0.45, fontSize: 14, color: COL.ink, valign: 'middle', isTextBox: true, margin: 0, objectName: cn + '_d' });
    addStep([cn, ...ic, cn + '_h', cn + '_d']);
  }
  arBox(s, 8.3, 1.5, 4.45, 5.25, [
    [{ text: 'عُمان تتبع الاقتصاد المختلط ', bold: true }, { text: 'لأن خصائص هذا النظام موجودة فيها:' }],
    [{ text: '١) تعايش القطاعين: ', bold: true }, { text: 'شركات حكومية (جهاز الاستثمار العُماني) إلى جانب شركات خاصة.' }],
    [{ text: '٢) التخطيط: ', bold: true }, { text: 'رؤية عُمان 2040 خطة وطنية طويلة المدى.' }],
    [{ text: '٣) حماية المستهلك: ', bold: true }, { text: 'قانون حماية المستهلك (مرسوم سلطاني 66/2014).' }],
    [{ text: '٤) حماية العمال: ', bold: true }, { text: 'قانون العمل (مرسوم سلطاني 53/2023).' }],
  ], COL.mx);
  s.addNotes('The strongest way to answer "why is Oman a mixed economy?" is to match the Chapter 2 features of a mixed economy to Omani evidence: co-existence (Oman Investment Authority alongside private firms), planning (Vision 2040), consumer protection (Royal Decree 66/2014) and labour protection (Royal Decree 53/2023).');

  s = newSlide('CONTENT', 'Part 6: Oman');
  title(s, 'POSTER ⑥  ·  OMAN', 'The roles of the government and private sectors in Oman');
  const roles = [
    ['GOVERNMENT SECTOR  ·  القطاع الحكومي', COL.cm, 'E0E6F3', [
      ['FaCompass', 'Plans the economy', 'Oman Vision 2040 sets the national direction for development.', 'يخطّط للاقتصاد عبر رؤية عُمان 2040.'],
      ['FaKey', 'Owns state companies', 'The Oman Investment Authority (Royal Decree 61/2020) owns and manages government companies.', 'يملك الشركات الحكومية عبر جهاز الاستثمار العُماني.'],
      ['FaShieldAlt', 'Protects people by law', 'Consumer Protection Law (66/2014) and Labour Law (53/2023).', 'يحمي المستهلكين والعمال بالقوانين.'],
    ]],
    ['PRIVATE SECTOR  ·  القطاع الخاص', COL.mk, 'FCE6DE', [
      ['FaChartLine', 'Leads diversification', 'Vision 2040 makes the private sector a main driver of growth beyond oil.', 'يقود التنويع الاقتصادي بعيدًا عن النفط.'],
      ['FaHandshake', 'Partners the state (PPP)', 'Public-Private Partnership Law (52/2019): firms build and run projects with the government.', 'يشارك الحكومة في مشاريع الشراكة (PPP).'],
      ['FaExchangeAlt', 'Runs privatised firms', 'Privatisation Law (51/2019): state-owned assets can be transferred to private owners.', 'يدير شركات تنتقل ملكيتها إليه عبر التخصيص.'],
    ]],
  ];
  for (let j = 0; j < 2; j++) {
    const x = 0.6 + j * 6.15; const R = roles[j];
    card(s, x, 1.5, 5.95, 5.3, { fill: R[2] });
    s.addText(R[0], { x: x + 0.25, y: 1.62, w: 5.5, h: 0.4, fontSize: 14, bold: true, color: R[1], charSpacing: 1, isTextBox: true, margin: 0 });
    for (let i = 0; i < 3; i++) {
      const y = 2.15 + i * 1.53; const g = nm('role');
      const ic = await iconCircle(s, R[3][i][0], x + 0.25, y + 0.05, 0.62, R[1], 'FFFFFF', g + '_c');
      s.addText(R[3][i][1], { x: x + 1.05, y, w: 4.7, h: 0.38, fontSize: 16, bold: true, color: COL.ink, isTextBox: true, margin: 0, objectName: g + '_h' });
      s.addText(R[3][i][2], { x: x + 1.05, y: y + 0.38, w: 4.7, h: 0.66, fontSize: 13.5, color: COL.ink, valign: 'top', isTextBox: true, margin: 0, objectName: g + '_d' });
      s.addText(R[3][i][3], { x: x + 1.05, y: y + 1.04, w: 4.7, h: 0.36, fontFace: AR, fontSize: 13.5, color: '4A4F5E', align: 'right', rtlMode: true, lang: 'ar-SA', isTextBox: true, margin: 0, objectName: g + '_a' });
      addStep([...ic, g + '_h', g + '_d', g + '_a']);
    }
  }
  s.addNotes('Government: plans (Vision 2040), owns state companies (Oman Investment Authority, Royal Decree 61/2020), protects consumers and workers (66/2014, 53/2023). Private sector: leads diversification beyond oil (Vision 2040), partners the government in PPP projects (52/2019), and runs firms transferred by privatisation (51/2019). Explain PPP: the government and a private company share a project, for example building and running infrastructure. Explain privatisation: moving ownership from the state to private owners.');

  // ================= PART 7: Revision & Q&A
  s = newSlide('SECTION_DARK', 'Part 7: Revision and questions');
  s.addText('Part 7 · Revision & questions', { placeholder: 'title' });
  s.addText('Key takeaways, presenting the poster, and model answers\nالجزء السابع: المراجعة والأسئلة المتوقعة', { placeholder: 'body' });
  await iconCircle(s, 'FaGraduationCap', 9.6, 2.4, 2.2, COL.must, HEX.ink);
  s.addNotes('Final part: revise the key ideas, plan the viva, and practise answering questions.');

  s = newSlide('CONTENT', 'Part 7: Revision and questions');
  title(s, 'REVISION  ·  المراجعة', 'Six things to remember');
  const keys = [
    ['FaSeedling', 'An economic system organises production and distribution of scarce resources.', 'النظام الاقتصادي ينظّم إنتاج الموارد النادرة وتوزيعها.'],
    ['FaQuestionCircle', 'Every system answers WHAT, HOW and FOR WHOM to produce.', 'كل نظام يجيب: ماذا وكيف ولمن ننتج.'],
    ['FaStore', 'Capitalist: private ownership, free prices, profit; the market decides.', 'الرأسمالي: ملكية خاصة وأسعار حرة وربح.'],
    ['FaLandmark', 'Socialist: government ownership, fixed prices, social welfare; the state decides.', 'الاشتراكي: ملكية حكومية وأسعار ثابتة ورفاه.'],
    ['FaHandshake', 'Mixed: both sectors, planning + prices, profit + social interest.', 'المختلط: القطاعان معًا مع التخطيط والأسعار.'],
    ['FaMapMarkerAlt', 'Oman is a mixed economy: Vision 2040, state firms, private sector, PPP.', 'عُمان اقتصاد مختلط.'],
  ];
  for (let i = 0; i < 6; i++) {
    const col = i % 2, row = Math.floor(i / 2); const x = 0.6 + col * 6.15, y = 1.5 + row * 1.32;
    const cn = card(s, x, y, 5.95, 1.15);
    const ic = await iconCircle(s, keys[i][0], x + 0.2, y + 0.24, 0.66, [COL.must, COL.ink, COL.mk, COL.cm, COL.mx, COL.mx][i]);
    s.addText(keys[i][1], { x: x + 1.05, y: y + 0.1, w: 4.75, h: 0.6, fontSize: 14.5, bold: true, color: COL.ink, valign: 'middle', isTextBox: true, margin: 0, objectName: cn + '_e' });
    s.addText(keys[i][2], { x: x + 1.05, y: y + 0.72, w: 4.75, h: 0.36, fontFace: AR, fontSize: 13.5, color: '4A4F5E', align: 'right', rtlMode: true, lang: 'ar-SA', isTextBox: true, margin: 0, objectName: cn + '_a' });
    addStep([cn, ...ic, cn + '_e', cn + '_a']);
  }
  card(s, 0.6, 5.55, 12.15, 1.25, { fill: 'FFF4E0', line: 'F0B13B' });
  s.addText([{ text: 'Chef’s note (poster conclusion): ', options: { bold: true, color: COL.mkd } }, { text: 'The mixed economy blends market freedom with social welfare: Oman’s recipe.', options: { bold: true } }],
    { x: 0.85, y: 5.62, w: 11.7, h: 0.55, fontSize: 16, color: COL.ink, valign: 'middle', isTextBox: true, margin: 0 });
  s.addText('ملاحظة الطاهي: الاقتصاد المختلط يجمع بين حرية السوق والرفاه الاجتماعي، وهذه «وصفة» عُمان.', { x: 0.85, y: 6.18, w: 11.7, h: 0.5, fontFace: AR, fontSize: 15, color: COL.ink, align: 'right', rtlMode: true, lang: 'ar-SA', isTextBox: true, margin: 0 });
  s.addNotes('Reveal one takeaway per click, then finish with the poster\'s conclusion (the Chef\'s note).');

  // ---- presenting in the viva
  s = newSlide('CONTENT', 'Part 7: Revision and questions');
  title(s, 'VIVA PLAN  ·  خطة العرض الشفهي', 'Presenting the poster as a team (3 to 5 minutes)');
  const plan = [
    ['FaSeedling', 'Speaker 1', 'Sections ① ②', 'Meaning of an economic system, scarcity, and the 3 questions.', 'المعنى والندرة والأسئلة الثلاثة', COL.must],
    ['FaUtensils', 'Speaker 2', 'Section ③', 'The three kitchens and how each flowchart works.', 'المطابخ الثلاثة والمخططات', COL.mk],
    ['FaTable', 'Speaker 3', 'Sections ④ ⑤', 'The 3-questions chalkboard and the comparison table.', 'السبورة وجدول المقارنة', COL.cm],
    ['FaMapMarkerAlt', 'Speaker 4', 'Section ⑥ + conclusion', 'Oman’s mixed economy, the Chef’s note, and the references.', 'عُمان والخلاصة والمراجع', COL.mx],
  ];
  for (let i = 0; i < 4; i++) {
    const x = 0.6 + i * 3.08; const cn = card(s, x, 1.5, 2.9, 3.6);
    const ic = await iconCircle(s, plan[i][0], x + 1.05, 1.7, 0.8, plan[i][5]);
    s.addText(plan[i][1], { x: x + 0.15, y: 2.6, w: 2.6, h: 0.4, fontSize: 18, bold: true, color: plan[i][5], align: 'center', isTextBox: true, margin: 0, objectName: cn + '_h' });
    s.addText(plan[i][2], { x: x + 0.15, y: 3.0, w: 2.6, h: 0.35, fontSize: 13, bold: true, color: COL.ink, align: 'center', isTextBox: true, margin: 0, objectName: cn + '_s' });
    s.addText(plan[i][3], { x: x + 0.2, y: 3.4, w: 2.5, h: 0.95, fontSize: 13.5, color: COL.ink, align: 'center', valign: 'top', isTextBox: true, margin: 0, objectName: cn + '_d' });
    s.addText(plan[i][4], { x: x + 0.2, y: 4.4, w: 2.5, h: 0.55, fontFace: AR, fontSize: 13.5, color: '4A4F5E', align: 'center', rtlMode: true, lang: 'ar-SA', isTextBox: true, margin: 0, objectName: cn + '_a' });
  }
  enText(s, [
    [{ text: 'Format (Word brief): ', bold: true }, { text: '3 to 5 minutes of presentation, then 2 to 3 minutes of questions. Every member must take part.' }],
    [{ text: 'Viva marks: ', bold: true }, { text: 'understanding and explaining (2), quality of answers (2), communication, confidence and time (1).' }],
    [{ text: 'Tip: ', bold: true }, { text: 'point to the poster while you speak, and answer "why" and "what if" questions with an example.' }],
  ], 0.6, 5.3, 12.15, 1.5, { bullet: true, size: 14.5, gap: 4 });
  s.addNotes('This is a suggested split so that every member speaks, as the brief requires. The order follows the poster: sections 1-2, section 3, sections 4-5, section 6 and the conclusion. Rehearse to stay within 3 to 5 minutes.');

  // ---- Q&A slides
  const QA = [
    ['Explain what an economic system is and why a society needs one.', 'An economic system is the way a society or government organises production and distributes resources, goods and services. Because resources are scarce and wants are unlimited, every society must choose, and the system is how it makes those choices.', 'هو أسلوب الإنتاج والتوزيع. نحتاجه لأن الموارد نادرة والرغبات غير محدودة، فلا بد من الاختيار.'],
    ['What are the three central questions? Give an example of each.', 'WHAT to produce (e.g. food or cars); HOW to produce (e.g. machines or many workers); FOR WHOM to produce (e.g. everyone equally, or those who can pay). Every system must answer all three.', 'ماذا ننتج؟ كيف ننتج؟ لمن ننتج؟ وكل نظام يجيب عنها بطريقته.'],
    ['Explain the capitalist flowchart in your own words.', 'Consumers spend their income: that is demand. Demand forms the market price, which signals where profit can be made. Producers follow profit and compete, producing a variety of goods, and the goods go to buyers who can pay. No central order is needed.', 'المستهلكون يطلبون، فيتكون السعر، فيستجيب المنتجون بدافع الربح، وتذهب السلع لمن يستطيع الدفع.'],
    ['In a command economy, who decides prices, and what is one weakness of this system?', 'The central authority fixes prices. One weakness: there is no competition, so there is less pressure to innovate, which leads to an "absence of technology". Others: no freedom and bureaucratic expansion.', 'السلطة المركزية تثبّت الأسعار. من العيوب غياب المنافسة وضعف التكنولوجيا وغياب الحرية.'],
    ['What is the difference between the profit motive and social welfare?', 'Profit motive means producing to earn the highest profit (capitalism). Social welfare means producing to improve the well-being of all citizens (socialism). A mixed economy blends both.', 'دافع الربح: الإنتاج لتحقيق الربح. الرفاه الاجتماعي: الإنتاج لتحسين حياة الجميع. والمختلط يجمع بينهما.'],
    ['Give one advantage and one disadvantage of capitalism, and explain why it happens.', 'Advantage: innovation and growth, because entrepreneurs take risks to earn profit. Disadvantage: inequality, because resources concentrate in a few hands and there is little government welfare.', 'ميزة: الابتكار والنمو بسبب المنافسة والربح. عيب: عدم المساواة لتركّز الموارد وقلة الرعاية الحكومية.'],
    ['Why is the mixed economy described as "the best of both systems"?', 'It combines the market’s efficiency and freedom (price mechanism, profit motive, liberty of production and consumption) with government planning that protects social welfare, consumers and workers.', 'لأنه يجمع كفاءة السوق وحريته مع تخطيط الحكومة الذي يحمي الرفاه الاجتماعي.'],
    ['What can go wrong in a mixed economy?', 'The public and private sectors may not cooperate, and the public sector can be inefficient, burdening the economy so that production falls.', 'قد لا يتعاون القطاعان، وقد يكون القطاع العام غير كفء فيقل الإنتاج.'],
    ['Why is Oman classified as a mixed economy?', 'Because it shows the features of a mixed economy: public and private sectors co-exist (state companies under the Oman Investment Authority alongside private firms), the government plans (Vision 2040), and laws protect consumers and workers.', 'لأن القطاعين يتعايشان، والحكومة تخطط عبر رؤية 2040، والقوانين تحمي المستهلكين والعمال.'],
    ['Give one example of the government’s role and one of the private sector’s role in Oman.', 'Government: owns and manages state companies through the Oman Investment Authority, or plans through Vision 2040. Private sector: leads diversification beyond oil, or partners the government in PPP projects.', 'الحكومة: جهاز الاستثمار العُماني أو رؤية 2040. القطاع الخاص: التنويع بعيدًا عن النفط أو مشاريع الشراكة.'],
    ['What if a country needs more hospitals? How would each system decide?', 'Capitalist: private firms build hospitals if they can earn profit, and patients pay. Socialist: the central authority plans and builds them for everyone. Mixed: the government builds public hospitals for social welfare while private hospitals also operate.', 'الرأسمالي: يبنيها القطاع الخاص إذا كانت مربحة. الاشتراكي: تخطط الدولة وتبنيها للجميع. المختلط: الاثنان معًا.'],
    ['What do "PPP" and "privatisation" mean?', 'PPP (public-private partnership): the government and a private company work together on a project. Privatisation: transferring ownership of state-owned assets or companies to the private sector.', 'الشراكة: تعاون الحكومة والقطاع الخاص في مشروع. التخصيص: نقل ملكية أصول الدولة إلى القطاع الخاص.'],
  ];
  for (let p = 0; p < QA.length; p += 3) {
    s = newSlide('CONTENT', 'Part 7: Revision and questions');
    title(s, `POTENTIAL QUESTIONS AND MODEL ANSWERS  ·  ${p / 3 + 1} OF 4`, 'Potential Questions and Model Answers');
    for (let k = 0; k < 3 && p + k < QA.length; k++) {
      const q = QA[p + k]; const y = 1.45 + k * 1.82; const g = nm('qa');
      card(s, 0.6, y, 12.15, 1.68);
      s.addShape(pres.shapes.OVAL, { x: 0.78, y: y + 0.17, w: 0.5, h: 0.5, fill: { color: COL.mkd }, line: { color: COL.mkd } });
      s.addText('Q' + (p + k + 1), { x: 0.78, y: y + 0.17, w: 0.5, h: 0.5, fontSize: 12.5, bold: true, color: COL.white, align: 'center', valign: 'middle', isTextBox: true, margin: 0 });
      s.addText(q[0], { x: 1.45, y: y + 0.12, w: 11.1, h: 0.45, fontSize: 16, bold: true, color: COL.ink, valign: 'middle', isTextBox: true, margin: 0 });
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 1.45, y: y + 0.62, w: 11.1, h: 0.98, rectRadius: 0.08, fill: { color: 'F4F8F6' }, line: { color: 'CFE6DD' }, objectName: g + '_bg' });
      s.addText([{ text: 'Model answer: ', options: { bold: true, color: COL.mx } }, { text: q[1] }], { x: 1.6, y: y + 0.65, w: 10.8, h: 0.6, fontSize: 13, color: COL.ink, valign: 'top', isTextBox: true, margin: 0, objectName: g + '_e' });
      s.addText(q[2], { x: 1.6, y: y + 1.24, w: 10.8, h: 0.34, fontFace: AR, fontSize: 13, color: '4A4F5E', align: 'right', valign: 'top', rtlMode: true, lang: 'ar-SA', isTextBox: true, margin: 0, objectName: g + '_a' });
      addStep([g + '_bg', g + '_e', g + '_a']);
    }
    s.addNotes('Practice mode: read the question, let students answer in their own words, then click to reveal the model answer (English, with the Arabic summary).');
  }

  // ---- References
  s = newSlide('CONTENT', 'Part 7: Revision and questions');
  title(s, 'SOURCES  ·  المراجع', 'References');
  enText(s, [
    [{ text: 'Fernando, G. A. (2026). ' }, { text: 'Chapter 2: Economic systems', italic: true }, { text: ' [PowerPoint slides]. BSEC1103 Principles of Economics, University of Technology and Applied Sciences.' }],
    [{ text: 'Mankiw, N. G. (2021). ' }, { text: 'Principles of economics', italic: true }, { text: ' (9th ed.). Cengage Learning.' }],
    [{ text: 'Oman Vision 2040 Main Committee. (2019). ' }, { text: 'Oman Vision 2040: Vision document', italic: true }, { text: '. Sultanate of Oman. https://www.oman2040.om' }],
    [{ text: 'Royal Decree No. 51/2019 issuing the Privatization Law. (2019). ' }, { text: 'Official Gazette of the Sultanate of Oman', italic: true }, { text: '.' }],
    [{ text: 'Royal Decree No. 52/2019 promulgating the Public-Private Partnership Law. (2019). ' }, { text: 'Official Gazette of the Sultanate of Oman', italic: true }, { text: '. https://decree.om/2019/rd20190052/' }],
    [{ text: 'Royal Decree No. 53/2023 promulgating the Labour Law. (2023). ' }, { text: 'Official Gazette of the Sultanate of Oman', italic: true }, { text: '.' }],
    [{ text: 'Royal Decree No. 61/2020 establishing the Oman Investment Authority. (2020). ' }, { text: 'Official Gazette of the Sultanate of Oman', italic: true }, { text: '. https://decree.om/2020/rd20200061/' }],
    [{ text: 'Royal Decree No. 66/2014 promulgating the Consumer Protection Law. (2014). ' }, { text: 'Official Gazette of the Sultanate of Oman', italic: true }, { text: '.' }],
  ], 0.6, 1.5, 12.15, 5.0, { size: 14, gap: 7 });
  s.addText('APA 7th edition  ·  the same sources as the poster', { x: 0.6, y: 6.55, w: 8, h: 0.35, fontSize: 12, italic: true, color: '6A6F7D', isTextBox: true, margin: 0 });
  s.addNotes('These are the same references as on the poster, in APA 7th style, as the Word brief requires.');

  // ---- Closing
  s = newSlide('TITLE_DARK', 'Part 7: Revision and questions');
  s.addText('Thank you  ·  شكرًا لكم', { placeholder: 'title' });
  s.addText('Questions are welcome. We are ready to explain every part of the poster.', { placeholder: 'body' });
  s.addImage({ path: path.join(IMG, 'chef.png'), x: 9.55, y: 1.0, w: 2.9, h: 3.02, altText: 'Chef character, the poster mascot' });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 5.15, w: 11.9, h: 1.65, rectRadius: 0.12, fill: { color: '2E2E4A' }, line: { color: '3A3A5C' } });
  s.addText('Student Names', { x: 1.0, y: 5.28, w: 4, h: 0.35, fontSize: 13, bold: true, color: COL.must, charSpacing: 3, isTextBox: true, margin: 0 });
  studs.forEach(([n, id], i) => {
    s.addText([{ text: n, options: { bold: true, color: COL.white, fontSize: 18, breakLine: true } }, { text: id, options: { color: COL.must, fontSize: 15 } }],
      { x: 1.0 + i * 2.9, y: 5.7, w: 2.8, h: 0.9, valign: 'top', isTextBox: true, margin: 0 });
  });
  s.addNotes('Close by inviting questions. Arabic: شكرًا لكم، يسعدنا الإجابة عن أسئلتكم.');

  const out = path.join(__dirname, 'Economic_Systems_Bilingual_Lesson.pptx');
  await pres.writeFile({ fileName: out });
  fs.writeFileSync(path.join(__dirname, 'anim.json'), JSON.stringify(ANIM));
  const { applyTheme } = require('/root/.claude/skills/synced/08b08bca-ae16-4991-94fe-78d4fad40ef2_bf56dd94-1b8e-4016-aaf9-bd4f64d1b9f6/pptx/scripts/apply_theme.js');
  await applyTheme(out, THEME);
  console.log('written', out, 'slides', sIdx);
})().catch(e => { console.error(e); process.exit(1); });
