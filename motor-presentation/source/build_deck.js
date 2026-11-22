/* Builds: Inside the Motor — Induction vs Synchronous (pptx) */
const pptxgen = require('pptxgenjs');
const fs = require('fs'); const path = require('path');
const React = require('react'); const RDS = require('react-dom/server'); const sharp = require('sharp');
const FA = require('react-icons/fa6');
const { applyTheme } = require(process.env.SKILL + '/scripts/apply_theme.js');

const ROOT = path.resolve(__dirname, '..', 'deliver'); const IMG = p => path.join(ROOT, 'img', p); const VID = p => path.join(ROOT, 'video', p);
const ASP = JSON.parse(fs.readFileSync(IMG('aspects.json')));
const OUT = process.argv[2] || path.join(ROOT, 'Inside_the_Motor_Induction_vs_Synchronous.pptx');

const COL = { navy: '0A1422', card: '0F2236', card2: '132B45', line: '24486B', accent: '38B6FF', copper: 'D9824A', green: '3DDC97', amber: 'FFB347', red: 'FF6B6B', white: 'FFFFFF', txt: 'C9D6E3', muted: '8AA3BC', ind: '5AA9E6', syn: 'E3A15C' };
const THEME = { name: 'Inside the Motor', headFontFace: 'Arial', bodyFontFace: 'Calibri',
  colors: { dk1: '0A1422', lt1: 'FFFFFF', dk2: '13263D', lt2: 'C9D6E3', accent1: '38B6FF', accent2: 'D9824A', accent3: '3DDC97', accent4: 'FFB347', accent5: 'FF6B6B', accent6: '8AA3BC', hlink: '38B6FF', folHlink: '8AA3BC' } };

async function icon(name, color, size = 256) {
  const svg = RDS.renderToStaticMarkup(React.createElement(FA[name], { color: '#' + color, size: String(size) }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer(); return 'image/png;base64,' + buf.toString('base64');
}
async function pngData(file, w) { const buf = await sharp(file).resize({ width: w || 1280 }).png().toBuffer(); return 'data:image/png;base64,' + buf.toString('base64'); }

(async () => {
  const pres = new pptxgen(); pres.layout = 'LAYOUT_WIDE'; pres.title = 'Inside the Motor: Induction vs. Synchronous'; pres.subject = 'Induction and synchronous motors explained for non-electrical audiences'; pres.author = 'Technical Induction Session';
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const W = 13.333, H = 7.5;

  pres.defineSlideMaster({ title: 'TITLE', background: { path: IMG('bg_center.png') }, objects: [] });
  const footer = [
    { text: { text: 'INSIDE THE MOTOR  ·  INDUCTION vs. SYNCHRONOUS', options: { x: 0.6, y: 7.02, w: 6, h: 0.3, fontSize: 9, color: '5F7A96', bold: true, charSpacing: 2, fontFace: 'Calibri' } } },
  ];
  pres.defineSlideMaster({ title: 'CONTENT', background: { path: IMG('bg_dim.png') }, objects: [...footer,
    { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.62, w: 12.1, h: 0.72, fontSize: 30, bold: true, color: 'FFFFFF', fontFace: 'Arial', valign: 'top', align: 'left', margin: 0 }, text: '' } }],
    slideNumber: { x: 12.25, y: 6.98, w: 0.5, h: 0.3, fontSize: 9, color: '5F7A96', fontFace: 'Calibri', align: 'right' } });
  pres.defineSlideMaster({ title: 'MEDIA', background: { path: IMG('bg_dim.png') }, objects: [...footer,
    { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.5, w: 12.1, h: 0.6, fontSize: 26, bold: true, color: 'FFFFFF', fontFace: 'Arial', valign: 'top', align: 'left', margin: 0 }, text: '' } }],
    slideNumber: { x: 12.25, y: 6.98, w: 0.5, h: 0.3, fontSize: 9, color: '5F7A96', fontFace: 'Calibri', align: 'right' } });

  // ---------- helpers ----------
  const T = (s, t, o) => s.addText(t, Object.assign({ isTextBox: true, fontFace: 'Calibri', color: COL.txt, fontSize: 15, margin: 0, valign: 'top' }, o));
  const kicker = (s, t, y) => T(s, t, { x: 0.6, y: y || 0.3, w: 9, h: 0.28, fontSize: 12, bold: true, color: COL.accent, charSpacing: 3 });
  const card = (s, x, y, w, h, o) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, Object.assign({ x, y, w, h, rectRadius: 0.12, fill: { color: COL.card, transparency: 8 }, line: { color: COL.line, width: 1 } }, o || {}));
  const img = (s, f, x, y, w, o) => { const a = ASP[f]; s.addImage(Object.assign({ path: IMG(f + '_t.png'), x, y, w, h: w / a }, o || {})); return w / a; };
  const imgH = (s, f, x, y, h, o) => { const a = ASP[f]; s.addImage(Object.assign({ path: IMG(f + '_t.png'), x, y, w: h * a, h }, o || {})); return h * a; };
  const ic = {}; const ICN = async (n, c) => (ic[n + c] = ic[n + c] || await icon(n, c));
  const iconCircle = async (s, n, c, x, y, d, bg) => { s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: bg || COL.card2 }, line: { color: c, width: 1.25 } }); s.addImage({ data: await ICN(n, c), x: x + d * 0.25, y: y + d * 0.25, w: d * 0.5, h: d * 0.5 }); };
  const numDot = (s, n, x, y, d, c) => { s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: c || COL.accent }, line: { type: 'none' } }); T(s, String(n), { x, y, w: d, h: d, fontSize: d > 0.35 ? 13 : 10, bold: true, color: '071220', align: 'center', valign: 'middle' }); };
  const chip = (s, t, x, y, c, w) => { s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: w || 1.5, h: 0.32, rectRadius: 0.16, fill: { color: c, transparency: 82 }, line: { color: c, width: 1 } }); T(s, t, { x, y, w: w || 1.5, h: 0.32, fontSize: 10.5, bold: true, color: c, align: 'center', valign: 'middle', charSpacing: 2 }); };
  const photo = (s, f, x, y, w, h, credit) => { s.addImage({ path: IMG(f), x, y, w, h, sizing: { type: 'cover', w, h } }); if (credit) T(s, credit, { x, y: y + h + 0.04, w, h: 0.2, fontSize: 7.5, color: '5F7A96' }); };
  const video = async (s, file, poster, x, y, w, h, name) => {
    if (process.env.DRAFT && file.includes('exploded')) file = 'anim_rmf.mp4';
    s.addMedia({ type: 'video', path: VID(file), x, y, w, h, cover: await pngData(poster, 1280), objectName: name });
  };
  const content = (sec) => pres.addSlide({ masterName: 'CONTENT', sectionTitle: sec });
  const media = (sec) => pres.addSlide({ masterName: 'MEDIA', sectionTitle: sec });

  // =====================================================================
  pres.addSection({ title: 'A · Introduction' });
  // 1 — TITLE
  { const s = pres.addSlide({ masterName: 'TITLE', sectionTitle: 'A · Introduction' });
    T(s, 'TECHNICAL INDUCTION SESSION', { x: 0.6, y: 0.62, w: 12.1, h: 0.3, fontSize: 13, bold: true, color: COL.accent, charSpacing: 5, align: 'center' });
    T(s, 'Inside the Motor', { x: 0.6, y: 0.98, w: 12.1, h: 0.95, fontSize: 54, bold: true, color: COL.white, fontFace: 'Arial', align: 'center' });
    T(s, 'Understanding Induction vs. Synchronous Technology', { x: 0.6, y: 1.95, w: 12.1, h: 0.5, fontSize: 22, color: COL.txt, align: 'center' });
    img(s, 'ind_hero', 1.0, 2.7, 4.3);
    imgH(s, 'syn_hero', 8.35, 2.6, 4.05);
    T(s, 'INDUCTION MOTOR', { x: 1.0, y: 6.82, w: 4.3, h: 0.3, fontSize: 12, bold: true, color: COL.ind, align: 'center', charSpacing: 3 });
    T(s, 'SYNCHRONOUS MOTOR', { x: 7.75, y: 6.82, w: 4.6, h: 0.3, fontSize: 12, bold: true, color: COL.syn, align: 'center', charSpacing: 3 });
    T(s, 'vs.', { x: 5.9, y: 4.25, w: 1.5, h: 0.7, fontSize: 34, bold: true, color: '5F7A96', align: 'center', fontFace: 'Arial' });
    s.addNotes(`Welcome everyone. Today we are going to open up two of the most important machines in any industrial plant: the induction motor and the synchronous motor.

From the outside they can look very similar – both are big steel machines with a shaft sticking out. But inside, they work in two clearly different ways, and that difference decides where each one is used.

You do not need any electrical background for this session. We will take each motor apart, look at every important part, then "switch it on" and watch the invisible magnetic forces that make it turn.

By the end you should be able to explain, in one sentence, what makes an induction motor different from a synchronous motor.`); }

  // 2 — WHY IT MATTERS
  { const s = content('A · Introduction'); kicker(s, 'WHY THIS MATTERS');
    s.addText('Electric motors keep industry moving', { placeholder: 'title' });
    card(s, 0.6, 1.65, 5.2, 4.95);
    T(s, '≈ 45 %', { x: 0.9, y: 1.95, w: 4.6, h: 1.4, fontSize: 80, bold: true, color: COL.accent, fontFace: 'Arial' });
    T(s, 'of all the electricity used in the world goes into electric-motor-driven systems.', { x: 0.9, y: 3.45, w: 4.6, h: 1.0, fontSize: 18, color: COL.white });
    T(s, 'Pumps, fans, compressors, conveyors, mills – almost everything that moves in a plant is turned by a motor.', { x: 0.9, y: 4.5, w: 4.6, h: 1.0, fontSize: 14, color: COL.txt });
    T(s, 'Source: IEA (2011), Energy-Efficiency Policy Opportunities for Electric Motor-Driven Systems – estimate 43–46 %.', { x: 0.9, y: 5.85, w: 4.6, h: 0.55, fontSize: 9.5, color: COL.muted });
    T(s, 'Two motor families do most of the heavy work:', { x: 6.25, y: 1.65, w: 6.5, h: 0.4, fontSize: 17, bold: true, color: COL.white });
    // induction card
    card(s, 6.25, 2.2, 6.5, 2.05, { fill: { color: COL.card, transparency: 8 } });
    img(s, 'ind_hero', 6.45, 2.35, 1.95);
    T(s, 'INDUCTION MOTOR', { x: 8.6, y: 2.4, w: 4, h: 0.3, fontSize: 12, bold: true, color: COL.ind, charSpacing: 3 });
    T(s, 'The workhorse', { x: 8.6, y: 2.7, w: 4, h: 0.45, fontSize: 22, bold: true, color: COL.white, fontFace: 'Arial' });
    T(s, 'Simple, rugged and affordable. By far the most common motor in industry.', { x: 8.6, y: 3.2, w: 3.95, h: 0.85, fontSize: 14 });
    // sync card
    card(s, 6.25, 4.55, 6.5, 2.05);
    imgH(s, 'syn_hero', 6.75, 4.68, 1.8);
    T(s, 'SYNCHRONOUS MOTOR', { x: 8.6, y: 4.75, w: 4, h: 0.3, fontSize: 12, bold: true, color: COL.syn, charSpacing: 3 });
    T(s, 'The specialist', { x: 8.6, y: 5.05, w: 4, h: 0.45, fontSize: 22, bold: true, color: COL.white, fontFace: 'Arial' });
    T(s, 'Exact, constant speed and power-factor control. Chosen for very large drives.', { x: 8.6, y: 5.55, w: 3.95, h: 0.85, fontSize: 14 });
    s.addNotes(`Why should we care about motors? Because they are everywhere. The International Energy Agency estimated that electric-motor-driven systems use roughly 43 to 46 percent of all the electricity consumed in the world. In a typical industrial plant the share is even higher.

Almost everything that moves – pumps, fans, compressors, conveyors, crushers, mills – is driven by a motor.

Two families of AC motor do most of this work:
• The induction motor is the workhorse. It is simple, tough, cheap and available everywhere, so it is by far the most common motor you will see.
• The synchronous motor is the specialist. It runs at an exact, constant speed and can even help the plant's power factor. It is usually chosen for very large drives.

Let's see what really separates them.`); }

  // 3 — THE KEY DIFFERENCE
  { const s = content('A · Introduction'); kicker(s, 'THE ONE-SENTENCE DIFFERENCE');
    s.addText('Same stator idea – a very different rotor', { placeholder: 'title' });
    const gx = 2.47, gw = 8.4, c1 = gx + gw * 0.25, c2 = gx + gw * 0.75;
    img(s, 'ind_hero', c1 - 1.45, 1.45, 2.9);
    imgH(s, 'syn_hero', c2 - 1.17, 1.4, 2.65);
    card(s, 0.6, 4.15, 5.85, 0.95, { fill: { color: COL.card2, transparency: 10 }, line: { color: COL.ind, width: 1.25 } });
    T(s, [{ text: 'Induction motor: ', options: { bold: true, color: COL.ind } }, { text: 'the rotor gets its motion through ', options: { color: COL.white } }, { text: 'electromagnetic induction', options: { bold: true, color: COL.white } }, { text: ' – it is always slightly slower than the magnetic field.', options: { color: COL.white } }], { x: 0.8, y: 4.22, w: 5.5, h: 0.82, fontSize: 15, valign: 'middle' });
    card(s, 6.88, 4.15, 5.85, 0.95, { fill: { color: COL.card2, transparency: 10 }, line: { color: COL.syn, width: 1.25 } });
    T(s, [{ text: 'Synchronous motor: ', options: { bold: true, color: COL.syn } }, { text: 'the rotor is its own magnet and turns ', options: { color: COL.white } }, { text: 'in step', options: { bold: true, color: COL.white } }, { text: ' with the rotating magnetic field – exactly the same speed.', options: { color: COL.white } }], { x: 7.08, y: 4.22, w: 5.5, h: 0.82, fontSize: 15, valign: 'middle' });
    s.addImage({ path: IMG('speed_dials.gif'), x: gx, y: 5.2, w: gw * 0.62, h: gw * 0.62 * 540 / 1600, });
    T(s, 'Speed check (loops automatically): the blue hand is the magnetic field, the coloured hand is the rotor.', { x: gx + gw * 0.64, y: 5.45, w: 3.0, h: 1.2, fontSize: 12, color: COL.muted });
    s.addNotes(`If you remember only one slide today, make it this one.

Both motors have a very similar stationary outer part – the stator – which creates a magnetic field that rotates. The big difference is the rotor, the part that spins.

• In the induction motor, nobody connects any electricity to the rotor. The rotating field induces currents in the rotor – that is where the name "induction" comes from – and those currents make it turn. For this to work, the rotor must always run a little slower than the field.

• In the synchronous motor, the rotor is made into a magnet of its own, normally with DC current. That magnet locks onto the rotating field and turns exactly in step with it – "synchronous" simply means "at the same time, at the same speed".

Look at the small dials at the bottom: on the left, the rotor hand keeps falling behind the field hand; on the right, the two hands move together. (The slip on the left is exaggerated so you can see it.)`); }

  // =====================================================================
  pres.addSection({ title: 'B · Construction' });
  // 4 — STATOR vs ROTOR
  { const s = content('B · Construction'); kicker(s, 'SECTION B · CONSTRUCTION');
    s.addText('Two main parts: the stator and the rotor', { placeholder: 'title' });
    img(s, 'ind_statorrotor', 0.45, 2.0, 8.0);
    chip(s, 'ROTOR · TURNS', 1.25, 1.7, COL.copper, 1.9);
    chip(s, 'STATOR · FIXED', 5.75, 1.7, COL.accent, 1.9);
    const rows = [
      ['FaLock', COL.accent, 'Stator – the fixed part', 'Outer steel core with copper windings, bolted inside the frame. It creates the magnetic field. It never moves.'],
      ['FaArrowsRotate', COL.copper, 'Rotor – the turning part', 'Sits inside the stator on the shaft. It is pushed round by the magnetic field and drives the machine.'],
      ['FaMagnet', COL.green, 'Air gap – the tiny space between', 'Often only 0.5–2 mm. The magnetic field jumps across it from stator to rotor, without any contact.'],
    ];
    for (let i = 0; i < rows.length; i++) { const y = 1.75 + i * 1.62; card(s, 8.75, y, 4.0, 1.45);
      await iconCircle(s, rows[i][0], rows[i][1], 8.95, y + 0.2, 0.55);
      T(s, rows[i][2], { x: 9.65, y: y + 0.15, w: 3.0, h: 0.35, fontSize: 15, bold: true, color: COL.white });
      T(s, rows[i][3], { x: 9.65, y: y + 0.5, w: 2.95, h: 0.9, fontSize: 12.5 }); }
    T(s, 'Think of it as a stage and a dancer: the stator is the stage that sets the rhythm, the rotor is the dancer that moves.', { x: 0.6, y: 6.35, w: 8.0, h: 0.55, fontSize: 14, italic: true, color: COL.txt });
    s.addNotes(`Every AC motor – induction or synchronous – is built from two main parts.

The STATOR is the stationary part. "Stat" as in static. It is a hollow steel cylinder with copper windings in slots, fixed inside the frame. Its job is to create the magnetic field. It never moves.

The ROTOR is the rotating part. It sits inside the stator, mounted on the shaft, and it is the rotor that turns the pump, the fan or the compressor.

Between them is the AIR GAP – a very small clearance, often only half a millimetre to a couple of millimetres. There is no contact: the magnetic field simply reaches across this gap.

An easy way to picture it: the stator is the stage that sets the rhythm, and the rotor is the dancer that moves to it.

On this picture the induction motor has been taken apart: the rotor on the left has been pulled out of the stator on the right.`); }

  // 5 — INDUCTION EXPLODED VIDEO
  { const s = media('B · Construction'); kicker(s, 'SECTION B · CONSTRUCTION', 0.22);
    s.addText('Induction motor: taking it apart', { placeholder: 'title' });
    await video(s, 'induction_motor_exploded.mp4', IMG('poster_ind_exploded.jpg'), 0.6, 1.3, 8.85, 4.98, 'Induction motor exploded view');
    T(s, '▶  Click the video to play – 50-second exploded-view tour of all 12 components. Pause on any part to discuss it.', { x: 0.6, y: 6.4, w: 8.85, h: 0.4, fontSize: 12, color: COL.muted });
    const parts = ['Stator', 'Stator core', 'Stator windings', 'Rotor', 'Rotor core', 'Rotor bars', 'End rings', 'Air gap', 'Shaft', 'Bearings', 'Frame / housing', 'Cooling fan'];
    card(s, 9.75, 1.3, 3.0, 4.98);
    T(s, 'COMPONENTS', { x: 9.95, y: 1.45, w: 2.6, h: 0.28, fontSize: 11, bold: true, color: COL.accent, charSpacing: 3 });
    parts.forEach((p, i) => { const y = 1.85 + i * 0.365; numDot(s, i + 1, 9.95, y, 0.27, [3, 4, 5, 6, 8].includes(i) ? COL.copper : COL.accent); T(s, p, { x: 10.35, y: y - 0.02, w: 2.3, h: 0.3, fontSize: 13, color: COL.white, valign: 'middle' }); });
    s.addNotes(`[Click the video to start it. It runs about 50 seconds; pause it whenever you want to talk about a part.]

This is a typical industrial induction motor – a "totally enclosed, fan-cooled" squirrel-cage motor, the kind you will find on thousands of pumps and fans.

Watch it come apart: the frame lifts off, the rotor slides out of the stator, and the end shields, bearings, fan and fan cover move away.

Then we visit each component in turn:
1. Stator – the fixed outer part.
2. Stator core – hundreds of thin steel sheets stacked together. Thin sheets instead of solid steel reduce energy losses.
3. Stator windings – insulated copper coils in three groups, one per phase of the supply. In the video they light up in three colours.
4. Rotor – the part that turns (copper-coloured numbers in the list on the right are rotating parts).
5. Rotor core – also laminated steel, pressed onto the shaft.
6. Rotor bars – aluminium bars cast into the rotor. Nothing is wired to them.
7. End rings – short-circuit all the bars at both ends.
8. Air gap – the tiny space the magnetic field must cross.
9. Shaft – delivers the torque.
10. Bearings – let the shaft spin smoothly.
11. Frame and end shields – hold everything, protect it and carry heat away through the fins.
12. Cooling fan and cover – blow air along the fins.\n\nTIP – interactive model: for questions, open viewer/motor_explorer_offline.html (in the presentation folder) in any web browser. You can rotate, zoom, explode and cut away the motor and click on any part.`); }

  // 6 — SQUIRREL CAGE
  { const s = content('B · Construction'); kicker(s, 'INDUCTION MOTOR · THE ROTOR');
    s.addText('The squirrel-cage rotor: simple and almost indestructible', { placeholder: 'title' });
    img(s, 'ind_cage', 0.4, 1.75, 7.4);
    T(s, 'Steel core shown see-through', { x: 0.6, y: 6.55, w: 5, h: 0.3, fontSize: 11, color: COL.muted, italic: true });
    const pts = [
      ['FaBolt', COL.copper, 'Bars + end rings = a closed cage', 'Aluminium (or copper) bars run along the rotor. End rings join them, so current can flow round in loops.'],
      ['FaPlug', COL.green, 'No wires, no brushes, no contacts', 'Nothing is connected to the rotor. Its current is induced by the stator’s moving magnetic field.'],
      ['FaGears', COL.accent, 'Why "squirrel cage"?', 'Without the steel core, the bars and rings look just like a pet’s exercise wheel.'],
      ['FaWind', COL.amber, 'Small details that matter', 'Bars are slightly skewed for smooth, quiet running; fins on the end rings stir cooling air.'],
    ];
    for (let i = 0; i < pts.length; i++) { const y = 1.6 + i * 1.3; await iconCircle(s, pts[i][0], pts[i][1], 8.1, y + 0.05, 0.6);
      T(s, pts[i][2], { x: 8.9, y, w: 3.9, h: 0.35, fontSize: 15.5, bold: true, color: COL.white });
      T(s, pts[i][3], { x: 8.9, y: y + 0.38, w: 3.85, h: 0.85, fontSize: 13 }); }
    s.addNotes(`Let's look closer at the heart of the induction motor: the squirrel-cage rotor. Here the steel core has been made see-through so you can see what is inside.

There are metal bars – usually die-cast aluminium, in big motors often copper – running the full length of the rotor. At each end, a ring connects all the bars together. So the bars and rings form a closed cage in which current can flow round and round.

The key point: nothing is connected to the rotor. No wires, no brushes, no sliding contacts. The current in the bars is produced purely by induction, by the moving magnetic field of the stator. That is why this rotor is so simple and so reliable.

The name comes from its shape – take away the steel and the cage looks like the exercise wheel of a pet squirrel or hamster.

Two small details: the bars are slightly twisted (skewed) to make the motor run smoothly and quietly, and the small fins cast on the end rings help circulate air inside the motor.`); }

  // 7 — SYNC EXPLODED VIDEO
  { const s = media('B · Construction'); kicker(s, 'SECTION B · CONSTRUCTION', 0.22);
    s.addText('Synchronous motor: taking it apart', { placeholder: 'title' });
    await video(s, 'synchronous_motor_exploded.mp4', IMG('poster_syn_exploded.jpg'), 0.6, 1.3, 8.85, 4.98, 'Synchronous motor exploded view');
    T(s, '▶  Click the video to play – 50-second exploded-view tour. Large salient-pole motor with slip rings and a top-mounted cooler.', { x: 0.6, y: 6.4, w: 8.85, h: 0.4, fontSize: 12, color: COL.muted });
    const parts = ['Stator', 'Stator core', '3-phase stator windings', 'Rotor (salient-pole)', 'Rotor poles & field winding', 'Damper (starting) bars', 'DC excitation system', 'Slip rings & brushes', 'Shaft', 'Bearings', 'Frame / housing', 'Cooling system'];
    card(s, 9.75, 1.3, 3.0, 4.98);
    T(s, 'COMPONENTS', { x: 9.95, y: 1.45, w: 2.6, h: 0.28, fontSize: 11, bold: true, color: COL.accent, charSpacing: 3 });
    parts.forEach((p, i) => { const y = 1.85 + i * 0.365; numDot(s, i + 1, 9.95, y, 0.27, [3, 4, 5, 8].includes(i) ? COL.copper : (i === 6 ? COL.amber : COL.accent)); T(s, p, { x: 10.35, y: y - 0.02, w: 2.35, h: 0.3, fontSize: 12.5, color: COL.white, valign: 'middle' }); });
    s.addNotes(`[Click the video to start it.]

Now the synchronous motor. This one represents a large industrial machine, the kind used on big compressors or mills.

The stator (1–3) is built exactly like the induction-motor stator: a laminated steel core and a three-phase copper winding that creates a rotating magnetic field.

The big difference is the rotor (4–6):
• It has salient – projecting – poles, like spokes.
• Copper field coils are wound around each pole. When DC current flows through them, each pole becomes a strong North or South electromagnet.
• In the faces of the poles there are damper bars – a small squirrel cage – used for starting and for calming oscillations.

7 – The DC excitation system: an exciter cubicle that supplies controlled DC current to the field winding.
8 – Slip rings and brushes: because the rotor spins, the DC has to be passed through sliding contacts – carbon brushes pressing on rotating bronze rings. (We will see the brushless alternative shortly.)

9–12 – Shaft, bearings, frame and the cooling system: here a fan on the shaft pushes inside air through a heat exchanger on top, where outside air carries the heat away.\n\nTIP – interactive model: for questions, open viewer/motor_explorer_offline.html (in the presentation folder) in any web browser. You can rotate, zoom, explode and cut away the motor and click on any part.`); }

  // 8 — ROTOR DESIGNS
  { const s = content('B · Construction'); kicker(s, 'SYNCHRONOUS MOTOR · ROTOR DESIGNS');
    s.addText('Two ways to build a synchronous rotor', { placeholder: 'title' });
    card(s, 0.6, 1.6, 5.95, 5.15); card(s, 6.8, 1.6, 5.95, 5.15);
    img(s, 'rot_salient', 1.1, 1.75, 4.95);
    img(s, 'rot_cyl', 7.25, 1.95, 5.05);
    T(s, 'SALIENT-POLE ROTOR', { x: 0.9, y: 4.6, w: 5.4, h: 0.3, fontSize: 12, bold: true, color: COL.syn, charSpacing: 3 });
    T(s, 'Poles stick out like spokes', { x: 0.9, y: 4.9, w: 5.4, h: 0.45, fontSize: 20, bold: true, color: COL.white, fontFace: 'Arial' });
    T(s, [{ text: 'Many poles fit easily → suited to lower speeds', options: { bullet: true, breakLine: true } }, { text: 'Typical for large industrial motors: mills, compressors, pumps (and hydro generators)', options: { bullet: true, breakLine: true } }, { text: 'Damper bars in the pole faces help it start', options: { bullet: true } }], { x: 0.9, y: 5.4, w: 5.4, h: 1.3, fontSize: 13, paraSpaceAfter: 4 });
    T(s, 'CYLINDRICAL (ROUND) ROTOR', { x: 7.1, y: 4.6, w: 5.4, h: 0.3, fontSize: 12, bold: true, color: COL.syn, charSpacing: 3 });
    T(s, 'A smooth, solid steel drum', { x: 7.1, y: 4.9, w: 5.4, h: 0.45, fontSize: 20, bold: true, color: COL.white, fontFace: 'Arial' });
    T(s, [{ text: 'Field winding sits in slots, held by steel retaining rings', options: { bullet: true, breakLine: true } }, { text: 'Very strong → suited to high speeds (2 or 4 poles: 3000 / 1500 rpm at 50 Hz)', options: { bullet: true, breakLine: true } }, { text: 'Typical for high-speed drives and turbo-generators', options: { bullet: true } }], { x: 7.1, y: 5.4, w: 5.4, h: 1.3, fontSize: 13, paraSpaceAfter: 4 });
    s.addNotes(`Synchronous rotors come in two main designs, and you can tell them apart at a glance.

On the left, the SALIENT-POLE rotor. "Salient" just means "sticking out": the poles project from the hub like spokes, each with its own field coil. It is easy to fit many poles this way, and more poles means lower speed. That is why salient-pole rotors are typical for large, slower industrial motors – mills, compressors, big pumps – and for hydro-power generators. The damper bars in the pole faces help it start.

On the right, the CYLINDRICAL or round rotor. It is a smooth, solid steel drum; the field winding is buried in slots along it and held at the ends by strong retaining rings. Because it is so compact and strong, it is used at high speed – typically two or four poles, so 3000 or 1500 rpm on a 50 Hz supply. Turbo-generators in power stations use this design.

Whichever design: the rotor carries a DC field winding, so it has its OWN fixed North and South poles. That is the essential difference from the squirrel-cage rotor.`); }

  // 9 — EXCITATION
  { const s = content('B · Construction'); kicker(s, 'SYNCHRONOUS MOTOR · EXCITATION');
    s.addText('How does DC current reach a spinning rotor?', { placeholder: 'title' });
    card(s, 0.6, 1.6, 5.95, 5.15); card(s, 6.8, 1.6, 5.95, 5.15);
    img(s, 'rot_salient', 1.4, 1.7, 4.4);
    img(s, 'rot_brushless', 7.45, 1.75, 4.6);
    chip(s, 'OPTION 1', 0.9, 4.1, COL.syn, 1.2); chip(s, 'OPTION 2', 7.1, 4.1, COL.syn, 1.2);
    T(s, 'Slip rings & brushes', { x: 0.9, y: 4.5, w: 5.4, h: 0.45, fontSize: 20, bold: true, color: COL.white, fontFace: 'Arial' });
    T(s, 'Brushless excitation', { x: 7.1, y: 4.5, w: 5.4, h: 0.45, fontSize: 20, bold: true, color: COL.white, fontFace: 'Arial' });
    const flow = (x, y, items, c) => { items.forEach((t, i) => { const bx = x + i * 1.82; s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx, y, w: 1.6, h: 0.72, rectRadius: 0.08, fill: { color: COL.card2 }, line: { color: c, width: 1 } }); T(s, t, { x: bx + 0.05, y, w: 1.5, h: 0.72, fontSize: 11.5, color: COL.white, align: 'center', valign: 'middle', bold: true }); if (i < items.length - 1) s.addShape(pres.shapes.RIGHT_ARROW, { x: bx + 1.63, y: y + 0.25, w: 0.17, h: 0.22, fill: { color: c }, line: { type: 'none' } }); }); };
    flow(0.9, 5.05, ['DC exciter (cubicle)', 'Carbon brushes (fixed)', 'Slip rings → field coils'], COL.amber);
    flow(7.1, 5.05, ['AC exciter on the shaft', 'Rotating diodes (AC→DC)', 'Field coils'], COL.amber);
    T(s, 'Simple and easy to control; brushes wear and need regular inspection.', { x: 0.9, y: 5.95, w: 5.4, h: 0.6, fontSize: 13 });
    T(s, 'No sliding contacts: everything turns together on the shaft. Less maintenance, common on modern motors.', { x: 7.1, y: 5.95, w: 5.45, h: 0.6, fontSize: 13 });
    T(s, 'Note: permanent-magnet synchronous motors need no excitation at all – magnets in the rotor provide the field.', { x: 0.6, y: 6.8, w: 12, h: 0.25, fontSize: 10.5, color: COL.muted, italic: true });
    s.addNotes(`The synchronous rotor needs DC current in its field winding. But the rotor is spinning – so how do we get electricity into it? There are two common answers.

OPTION 1 – Slip rings and brushes. Two smooth bronze rings are mounted on the shaft and turn with it. Stationary carbon brushes press against them and slide on them. DC from an exciter cubicle flows through the brushes, into the rings, and on to the field coils. It is simple and the field current is easy to control, but brushes wear out and create carbon dust, so they need regular inspection.

OPTION 2 – Brushless excitation. A small AC generator, the exciter, is built onto the same shaft. Its AC output is turned into DC by a ring of diodes that rotate with the shaft, and that DC goes straight to the field coils. Nothing slides, so there is much less maintenance. This is very common on modern synchronous motors.

A third family worth knowing: permanent-magnet synchronous motors. There the rotor field comes from magnets, so no excitation is needed at all – but they are normally fed from a variable-frequency drive.`); }

  // =====================================================================
  pres.addSection({ title: 'C · Working Principle' });
  // 10 — RMF
  { const s = media('C · Working Principle'); kicker(s, 'SECTION C · HOW THEY WORK · STEP 0 (BOTH MOTORS)', 0.22);
    s.addText('First, the magic trick: a magnetic field that rotates', { placeholder: 'title' });
    await video(s, 'anim_rmf.mp4', IMG('poster_anim_rmf.jpg'), 1.69, 1.28, 9.956, 5.6, 'Rotating magnetic field animation');
    s.addNotes(`[Click to play – 30 seconds.]

Before we look at either motor, we need one idea that both of them use: the rotating magnetic field.

Step 1 – one coil with alternating current. The current flows one way, then the other, 50 times a second. The coil's magnetic field grows, shrinks and flips – it pulses, but it does not rotate.

Step 2 – we add two more coils, placed 120 degrees apart around the stator, and feed each from a different phase of the three-phase supply. Look at the waves on the right: each phase peaks one-third of a cycle after the previous one.

Step 3 – the three pulsing fields add together into ONE field of constant strength that turns smoothly round the stator. Nothing is moving mechanically – the rotation is created purely by the timing of the three currents.

Step 4 – put a magnet in the middle and it is dragged round by this field. That is the basic idea of every three-phase motor.

The speed of this field is called the SYNCHRONOUS SPEED. It depends only on the supply frequency and the number of poles: on a 50 Hz supply it is 3000 rpm for a 2-pole motor and 1500 rpm for a 4-pole motor.`); }

  // 11 — INDUCTION WORKING
  { const s = media('C · Working Principle'); kicker(s, 'SECTION C · HOW THEY WORK', 0.22);
    s.addText('Induction motor: how it turns', { placeholder: 'title' });
    await video(s, 'anim_induction.mp4', IMG('poster_anim_induction.jpg'), 1.69, 1.28, 9.956, 5.6, 'Induction motor working principle animation');
    s.addNotes(`[Click to play – about 50 seconds, 8 steps. Pause between steps if you want.]

This is a slice through a 4-pole induction motor.

1. Three-phase AC is fed into the stator coils. The symbols show the current coming toward you or going away from you.
2. Together these currents create North and South poles that travel round the stator – the rotating magnetic field. The rotor is still standing still.
3. The moving field sweeps across the rotor bars. A conductor that is cut by a moving magnetic field gets a voltage induced in it – just like in a generator – and because the cage is closed, current flows in the bars. No wires are connected to the rotor.
4. Those induced currents turn the rotor into a magnet with its own poles – shown with small n and s – sitting just behind the stator poles.
5. The stator poles pull the rotor poles along. You can also see it as a force on each bar – the green arrows – always in the direction the field is turning. That is torque.
6. The rotor accelerates and chases the field.
7. At normal running the rotor turns slightly slower than the field. The difference is called SLIP. In this animation it is exaggerated; in a real motor it is only a few percent.
8. Why can't it catch up? Imagine it did: the field would no longer move relative to the bars, so no voltage would be induced, no current would flow and there would be no torque. The rotor would immediately slow down again. So an induction motor ALWAYS runs a little slower than its field – the slip is what makes it work.`); }

  // 12 — SLIP
  { const s = content('C · Working Principle'); kicker(s, 'INDUCTION MOTOR · SLIP');
    s.addText('Slip: the small speed difference that makes it work', { placeholder: 'title' });
    // numbers
    card(s, 0.6, 1.6, 6.3, 2.45);
    const stat = (x, big, small, c) => { T(s, big, { x, y: 1.85, w: 1.95, h: 0.8, fontSize: 36, bold: true, color: c, fontFace: 'Arial', align: 'center' }); T(s, small, { x, y: 2.7, w: 1.95, h: 0.6, fontSize: 12, align: 'center' }); };
    stat(0.75, '1500', 'rpm\nmagnetic field', COL.accent); stat(2.75, '1470', 'rpm\nrotor (full load)', COL.amber); stat(4.75, '2 %', 'slip', COL.white);
    T(s, 'Typical 4-pole motor on a 50 Hz supply', { x: 0.85, y: 3.5, w: 5.8, h: 0.3, fontSize: 11, color: COL.muted, align: 'center' });
    card(s, 0.6, 4.25, 6.3, 2.5);
    T(s, 'In plain words', { x: 0.85, y: 4.4, w: 5.8, h: 0.35, fontSize: 15, bold: true, color: COL.white });
    T(s, [{ text: 'Slip = (field speed − rotor speed) ÷ field speed', options: { bold: true, color: COL.white, breakLine: true } },
      { text: 'Typically about 1–5 % at full load (smaller in big motors).', options: { bullet: true, breakLine: true } },
      { text: 'More load → a bit more slip → more induced current → more torque. The motor adjusts itself automatically.', options: { bullet: true, breakLine: true } },
      { text: 'Zero slip would mean zero torque.', options: { bullet: true } }], { x: 0.85, y: 4.8, w: 5.85, h: 1.9, fontSize: 13.5, paraSpaceAfter: 5 });
    // analogy
    card(s, 7.15, 1.6, 5.6, 5.15, { fill: { color: COL.card2, transparency: 10 } });
    await iconCircle(s, 'FaHandPointer', COL.amber, 7.45, 1.85, 0.75);
    T(s, 'AN EVERYDAY ANALOGY', { x: 8.4, y: 1.95, w: 4.2, h: 0.3, fontSize: 11, bold: true, color: COL.amber, charSpacing: 3 });
    T(s, 'Pushing a playground roundabout', { x: 8.4, y: 2.25, w: 4.2, h: 0.4, fontSize: 18, bold: true, color: COL.white, fontFace: 'Arial' });
    T(s, 'You run alongside a spinning roundabout and push it with your hand.', { x: 7.45, y: 2.95, w: 5.0, h: 0.6, fontSize: 14 });
    T(s, [{ text: 'Your hand moves a little faster than the roundabout → you can push it.', options: { bullet: { code: '2714' }, breakLine: true } },
      { text: 'If the roundabout moves exactly as fast as your hand → your hand just rests on it. No push.', options: { bullet: { code: '2716' }, breakLine: true } },
      { text: 'Heavier children on board (more load) → it falls back a little more, and you push harder.', options: { bullet: { code: '2714' } } }], { x: 7.45, y: 3.65, w: 5.05, h: 2.2, fontSize: 14, paraSpaceAfter: 8 });
    T(s, 'Hand = rotating magnetic field  ·  Roundabout = rotor', { x: 7.45, y: 6.1, w: 5.05, h: 0.4, fontSize: 13, bold: true, color: COL.accent });
    s.addNotes(`Let's put real numbers on slip.

Take a common 4-pole motor on a 50 Hz supply. Its magnetic field turns at 1500 rpm – the synchronous speed. At full load the rotor turns at about 1470 rpm. The difference, 30 rpm, divided by 1500, is 2 percent. That is the slip.

Typical values are about 1 to 5 percent at full load; large motors have smaller slip.

Here is the clever part: the motor adjusts itself. If the load increases, the rotor slows down a tiny bit, the slip increases, the field cuts the bars faster, more current is induced and more torque is produced – until it balances the load again.

An everyday analogy: pushing a playground roundabout. You can only push it while your hand moves a little faster than the roundabout. If it moves exactly as fast as your hand, your hand is just resting on it – there is no push. And if more children climb on, the roundabout falls back a little and you push harder.

The hand is the rotating magnetic field, the roundabout is the rotor. Zero slip means zero torque.`); }

  // 13 — SYNC WORKING
  { const s = media('C · Working Principle'); kicker(s, 'SECTION C · HOW THEY WORK', 0.22);
    s.addText('Synchronous motor: how it locks in step', { placeholder: 'title' });
    await video(s, 'anim_sync.mp4', IMG('poster_anim_sync.jpg'), 1.69, 1.28, 9.956, 5.6, 'Synchronous motor working principle animation');
    s.addNotes(`[Click to play – about 50 seconds, 7 steps.]

A slice through a 4-pole synchronous motor with a salient-pole rotor.

1. The stator works exactly as before: three-phase AC creates a magnetic field rotating at synchronous speed – here 1500 rpm.
2. Why can't it simply start? If we switch on the DC while the heavy rotor is standing still, its poles are pulled forward by one stator pole and, a split second later, pulled backward by the next one. The field is far too fast for the rotor to follow – the rotor only shakes. So a conventional synchronous motor does NOT start by itself at synchronous speed.
3. Starting: with the DC switched off, the damper bars in the pole faces behave like an induction-motor cage. The rotor accelerates – as an induction motor – to just below synchronous speed.
4. Now DC excitation is switched on: each pole becomes a fixed North or South electromagnet.
5. Magnetic locking: each rotor pole is attracted to an opposite stator pole and is pulled into step. This is called pull-in.
6. Locked: rotor and field turn together at exactly the same speed. Slip is zero, so the damper bars carry no current any more.
7. When we add load, the rotor poles trail a little further behind the stator poles – this is the load angle – but the speed stays exactly synchronous. Only if the load becomes too large does the motor "pull out" of step, and protection trips it.`); }

  // 14 — STARTING
  { const s = content('C · Working Principle'); kicker(s, 'SYNCHRONOUS MOTOR · STARTING');
    s.addText('A synchronous motor needs help to start', { placeholder: 'title' });
    card(s, 0.6, 1.55, 12.15, 1.0, { fill: { color: COL.card2, transparency: 5 }, line: { color: COL.amber, width: 1.25 } });
    await iconCircle(s, 'FaTriangleExclamation', COL.amber, 0.85, 1.72, 0.65);
    T(s, 'On a fixed 50 Hz supply the field turns at full speed at once – far too fast for a heavy rotor to lock on from standstill. The average pull is zero, so the rotor just vibrates. It must first be brought close to synchronous speed.', { x: 1.7, y: 1.67, w: 10.85, h: 0.78, fontSize: 14, color: COL.white, valign: 'middle' });
    const m = [
      ['FaGears', 'MOST COMMON', 'Damper-winding start', 'The damper bars make the rotor start like an induction motor. Near full speed (about 95–98 %), DC is switched on and the rotor pulls into step.', 'Field winding is shorted through a resistor during the run-up for protection.'],
      ['FaGaugeHigh', 'MODERN & GENTLE', 'Variable-frequency drive (VFD)', 'The drive starts at a very low frequency, so the field turns slowly and the rotor follows it, then both speed up together.', 'Also allows speed control and limits starting current.'],
      ['FaArrowsRotate', 'SPECIAL CASES', 'Auxiliary ("pony") motor', 'A smaller motor on the same shaft spins the rotor up to speed before the synchronous motor is connected.', 'Rare today – mostly replaced by VFD starting.'],
    ];
    for (let i = 0; i < 3; i++) { const x = 0.6 + i * 4.1; card(s, x, 2.8, 3.95, 3.95);
      await iconCircle(s, m[i][0], COL.syn, x + 0.25, 3.05, 0.7);
      T(s, m[i][1], { x: x + 1.1, y: 3.12, w: 2.7, h: 0.3, fontSize: 10, bold: true, color: COL.syn, charSpacing: 2 });
      T(s, m[i][2], { x: x + 1.1, y: 3.4, w: 2.75, h: 0.4, fontSize: 16, bold: true, color: COL.white });
      T(s, m[i][3], { x: x + 0.25, y: 4.0, w: 3.5, h: 1.6, fontSize: 13.5 });
      T(s, m[i][4], { x: x + 0.25, y: 5.75, w: 3.5, h: 0.8, fontSize: 11.5, color: COL.muted, italic: true }); }
    s.addNotes(`This is an important technical point that is often misunderstood: a conventional synchronous motor cannot start by itself on the normal supply.

The moment it is connected, its stator field is already rotating at full synchronous speed – 25 revolutions per second for a 4-pole motor at 50 Hz. A heavy rotor standing still cannot jump to that speed. Its poles are pulled forward, then backward, many times a second; the average pull is zero, so it only vibrates.

So it needs a starting method:

1. Damper-winding start – the most common for motors connected directly to the supply. The damper bars in the pole faces act like a squirrel cage, so the motor starts as an induction motor. When it reaches about 95 to 98 percent of synchronous speed, the DC field is switched on and the rotor pulls into step. During the run-up the field winding is shorted through a resistor to protect it from high induced voltages.

2. Variable-frequency drive. The drive starts at a very low frequency, so the field turns slowly and the rotor can follow it from the very beginning; then the drive raises the frequency and both speed up together. This is gentle on the motor and the network, and also allows speed control.

3. A small auxiliary or "pony" motor brings the rotor up to speed first. This is rare today.`); }

  // 15 — POWER FACTOR
  { const s = content('C · Working Principle'); kicker(s, 'A BONUS OF THE SYNCHRONOUS MOTOR');
    s.addText('Power factor, explained with a glass of beer', { placeholder: 'title' });
    // glass graphic
    const gx = 0.95, gy = 1.75, gw = 2.3, gh = 4.3;
    s.addShape(pres.shapes.RECTANGLE, { x: gx, y: gy + 1.2, w: gw, h: gh - 1.2, fill: { color: 'E8A33D' }, line: { type: 'none' } });
    s.addShape(pres.shapes.RECTANGLE, { x: gx, y: gy, w: gw, h: 1.2, fill: { color: 'F4F1E8' }, line: { type: 'none' } });
    s.addShape(pres.shapes.RECTANGLE, { x: gx - 0.06, y: gy - 0.1, w: gw + 0.12, h: gh + 0.16, fill: { type: 'none' }, line: { color: 'D8E6F2', width: 2.5 } });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: gx + gw + 0.03, y: gy + 0.9, w: 0.6, h: 2.0, rectRadius: 0.25, fill: { type: 'none' }, line: { color: 'D8E6F2', width: 2.5 } });
    for (let i = 0; i < 9; i++) s.addShape(pres.shapes.OVAL, { x: gx + 0.2 + (i * 0.37) % 1.9, y: gy + 1.6 + (i * 0.53) % 2.4, w: 0.08, h: 0.08, fill: { color: 'FFE2A6' }, line: { type: 'none' } });
    T(s, 'FOAM', { x: gx, y: gy + 0.38, w: gw, h: 0.4, fontSize: 16, bold: true, color: '5B4A2A', align: 'center' });
    T(s, 'BEER', { x: gx, y: gy + 2.5, w: gw, h: 0.4, fontSize: 16, bold: true, color: '5B3A0A', align: 'center' });
    const lab = (y, t1, c, t2) => { T(s, t1, { x: 4.05, y, w: 3.4, h: 0.32, fontSize: 14, bold: true, color: c }); T(s, t2, { x: 4.05, y: y + 0.32, w: 3.4, h: 0.85, fontSize: 12.5 }); };
    lab(1.75, 'Reactive power (kvar) = foam', 'F4F1E8', 'Needed to build the magnetic fields, but does no useful work. Still has to be carried by cables and transformers.');
    lab(3.25, 'Real power (kW) = beer', 'E8A33D', 'Does the useful work: turns the pump, the fan, the mill.');
    lab(4.6, 'Power factor = beer ÷ full glass', COL.white, 'Closer to 1.0 means less "foam" – less current for the same work, lower losses, smaller cables.');
    // motor cards
    card(s, 7.75, 1.6, 5.0, 2.45, { line: { color: COL.ind, width: 1.25 } });
    T(s, 'INDUCTION MOTOR', { x: 8.0, y: 1.78, w: 4.5, h: 0.3, fontSize: 12, bold: true, color: COL.ind, charSpacing: 3 });
    T(s, 'Always orders some foam', { x: 8.0, y: 2.08, w: 4.5, h: 0.4, fontSize: 18, bold: true, color: COL.white, fontFace: 'Arial' });
    T(s, 'It must draw magnetizing current from the supply to create its field, so its power factor is lagging – often around 0.8–0.9 at full load, and lower at light load.', { x: 8.0, y: 2.55, w: 4.55, h: 1.4, fontSize: 13 });
    card(s, 7.75, 4.3, 5.0, 2.45, { line: { color: COL.syn, width: 1.25 } });
    T(s, 'SYNCHRONOUS MOTOR', { x: 8.0, y: 4.48, w: 4.5, h: 0.3, fontSize: 12, bold: true, color: COL.syn, charSpacing: 3 });
    T(s, 'Can even supply foam to others', { x: 8.0, y: 4.78, w: 4.6, h: 0.4, fontSize: 18, bold: true, color: COL.white, fontFace: 'Arial' });
    T(s, 'Its DC excitation builds the rotor field. Turning the DC up ("over-excitation") gives power factor 1.0 or even leading – it supplies reactive power to the rest of the plant.', { x: 8.0, y: 5.25, w: 4.55, h: 1.4, fontSize: 13 });
    s.addNotes(`One term appears in every motor comparison: power factor. Here is the classic way to explain it.

Think of a glass of beer. The beer is the real power, measured in kilowatts – it does the useful work. The foam is the reactive power – it is needed to build the magnetic fields inside motors and transformers, but it does no useful work. Yet the glass – the cables, transformers and generators – has to carry both. Power factor is the beer divided by the whole glass. Closer to 1 means less foam: less current for the same work, lower losses and smaller cables, and often lower electricity bills because utilities penalize poor power factor.

The induction motor always "orders some foam": it has to draw magnetizing current from the supply to create its field. Its power factor is lagging – typically around 0.8 to 0.9 at full load, and noticeably worse when lightly loaded.

The synchronous motor creates its rotor field with its own DC excitation. If we increase the DC – called over-excitation – its power factor becomes 1 or even leading: it then supplies reactive power to the rest of the plant, cancelling some of the "foam" drawn by all the induction motors. This is a real economic advantage of large synchronous motors.`); }

  // =====================================================================
  pres.addSection({ title: 'D · Advantages & Limitations' });
  const prosCons = async (s, hero, color, pros, cons) => {
    card(s, 0.6, 1.6, 6.05, 5.15, { line: { color: COL.green, width: 1 } }); card(s, 6.85, 1.6, 5.9, 5.15, { line: { color: COL.amber, width: 1 } });
    T(s, 'ADVANTAGES', { x: 0.9, y: 1.78, w: 3, h: 0.3, fontSize: 12, bold: true, color: COL.green, charSpacing: 3 });
    T(s, 'LIMITATIONS', { x: 7.15, y: 1.78, w: 3, h: 0.3, fontSize: 12, bold: true, color: COL.amber, charSpacing: 3 });
    const rowH = 4.45 / Math.max(pros.length, cons.length);
    for (let i = 0; i < pros.length; i++) { const y = 2.2 + i * rowH; s.addImage({ data: await ICN('FaCircleCheck', COL.green), x: 0.9, y: y + 0.04, w: 0.32, h: 0.32 }); T(s, pros[i][0], { x: 1.4, y, w: 5.05, h: 0.32, fontSize: 15, bold: true, color: COL.white }); T(s, pros[i][1], { x: 1.4, y: y + 0.33, w: 5.05, h: rowH - 0.38, fontSize: 12.5 }); }
    for (let i = 0; i < cons.length; i++) { const y = 2.2 + i * rowH; s.addImage({ data: await ICN('FaTriangleExclamation', COL.amber), x: 7.15, y: y + 0.04, w: 0.32, h: 0.32 }); T(s, cons[i][0], { x: 7.65, y, w: 4.9, h: 0.32, fontSize: 15, bold: true, color: COL.white }); T(s, cons[i][1], { x: 7.65, y: y + 0.33, w: 4.9, h: rowH - 0.38, fontSize: 12.5 }); }
  };
  // 16 — INDUCTION PROS/CONS
  { const s = content('D · Advantages & Limitations'); kicker(s, 'SECTION D · INDUCTION MOTOR');
    s.addText('Induction motor: strengths and limitations', { placeholder: 'title' });
    await prosCons(s, 'ind_hero', COL.ind,
      [['Simple, robust construction', 'Squirrel-cage rotor: no windings, brushes or slip rings on the rotor.'], ['Relatively low maintenance', 'Mainly bearings and cooling to look after.'], ['No rotor excitation needed', 'Standard cage motors connect straight to the supply (or a drive).'], ['Generally lower initial cost', 'Built in huge numbers, in standard frame sizes.'], ['Available everywhere', 'Suits most pumps, fans, compressors and conveyors.']],
      [['Needs reactive power', 'Draws magnetizing current, so power factor is lagging.'], ['Runs below synchronous speed', 'Speed drops slightly with load (slip).'], ['Speed control needs a VFD', 'On a fixed supply it runs at one (nearly) fixed speed.'], ['Efficiency & PF depend on load', 'Both are poorer when the motor runs lightly loaded or is oversized.']]);
    s.addNotes(`Let's weigh up the induction motor fairly.

Strengths:
• Simple, robust construction – the squirrel-cage rotor has no windings, no brushes and no slip rings. There is very little that can go wrong.
• Relatively low maintenance – mainly bearings and keeping the cooling clean.
• No separate rotor excitation – a standard cage motor is simply connected to the supply or to a drive.
• Generally lower purchase cost – they are made in huge numbers in standard sizes.
• Widely available and suitable for most industrial jobs.

Limitations:
• It needs reactive power to build its magnetic field, so its power factor is lagging.
• The rotor runs below synchronous speed, and the speed changes slightly with load.
• On a fixed-frequency supply it runs at essentially one speed; for variable speed you need a variable-frequency drive.
• Efficiency and power factor depend on the load and design – both drop when a motor is lightly loaded, for example when it is oversized for the job.

None of these limitations is dramatic, which is exactly why induction motors are the default choice.`); }

  // 17 — SYNC PROS/CONS
  { const s = content('D · Advantages & Limitations'); kicker(s, 'SECTION D · SYNCHRONOUS MOTOR');
    s.addText('Synchronous motor: strengths and limitations', { placeholder: 'title' });
    await prosCons(s, 'syn_hero', COL.syn,
      [['Constant, exact speed', 'Runs at synchronous speed regardless of load (within its rating).'], ['Can improve power factor', 'Over-excited, it supplies reactive power to the plant.'], ['Ideal for very large drives', 'Economical at high power and low speed.'], ['High efficiency possible', 'Especially in large machines running near rated load.']],
      [['More complex construction', 'Field winding, excitation system, slip rings or brushless exciter.'], ['Often higher initial cost', 'Especially in smaller sizes, where induction motors win.'], ['Starting is more involved', 'Needs damper winding, a VFD or another starting method.'], ['Needs excitation & control', 'DC supply, field control and protection against pull-out.']]);
    s.addNotes(`Now the synchronous motor.

Strengths:
• Constant, exact speed: it runs at synchronous speed whatever the load, as long as it stays within its rating. That matters for processes that need precise timing or speed.
• It can improve the plant's power factor when over-excited, as we saw with the beer glass.
• It is well suited to very large drives – thousands of kilowatts – especially at low speed, where it is often more economical than an equivalent induction motor.
• High efficiency can be achieved in suitable designs, particularly in large machines running near their rated load.

Limitations:
• More complex construction: a field winding, an excitation system, slip rings or a brushless exciter.
• Often a higher purchase cost, especially in smaller sizes, where an induction motor is usually the better buy.
• Starting is more complicated: it needs a damper winding, a drive or another starting arrangement.
• It needs an excitation supply and control system, and protection in case it is overloaded and falls out of step.

So it is a specialist: excellent where its strengths are needed, unnecessary elsewhere.`); }

  // =====================================================================
  pres.addSection({ title: 'E · Applications' });
  // 18 — INDUCTION APPLICATIONS
  { const s = content('E · Applications'); kicker(s, 'SECTION E · WHERE WE USE THEM');
    s.addText('Induction motors: the default choice almost everywhere', { placeholder: 'title' });
    const apps = [['ph_pump.jpg', 'Pumps', 'Water, slurry, process liquids', 'B. S. Janse, CC BY 2.5'], ['ph_fan.jpg', 'Fans & ventilation', 'Tunnels, mines, process air', 'Kecko, CC BY 2.0'], ['ph_compressor.jpg', 'Compressors', 'Plant air, refrigeration', 'Asurnipal, CC BY-SA 4.0'], ['ph_conveyor.jpg', 'Conveyors', 'Mining, bulk handling', 'L. Lenz, CC BY-SA 4.0'], ['ph_hvac.jpg', 'HVAC systems', 'Air-handling units, chillers', 'Alf van Beem, CC0']];
    apps.forEach((a, i) => { const x = 0.6 + i * 2.47, w = 2.27; photo(s, a[0], x, 1.6, w, w, 'Photo: ' + a[3] + ' · Wikimedia Commons');
      T(s, a[1], { x, y: 1.6 + w + 0.3, w, h: 0.35, fontSize: 16, bold: true, color: COL.white }); T(s, a[2], { x, y: 1.6 + w + 0.65, w, h: 0.35, fontSize: 12.5 }); });
    card(s, 0.6, 5.45, 12.15, 1.3, { fill: { color: COL.card2, transparency: 5 }, line: { color: COL.ind, width: 1.25 } });
    await iconCircle(s, 'FaLightbulb', COL.ind, 0.85, 5.68, 0.8);
    T(s, 'WHY AN ENGINEER CHOOSES IT', { x: 1.9, y: 5.6, w: 6, h: 0.3, fontSize: 11, bold: true, color: COL.ind, charSpacing: 3 });
    T(s, 'Simple, rugged and low-cost, available off the shelf in every size. A small change in speed with load does not matter for these machines – and when speed control is needed, a VFD provides it.', { x: 1.9, y: 5.9, w: 10.65, h: 0.8, fontSize: 14, color: COL.white });
    T(s, 'Also: general industrial machinery – mixers, crushers, machine tools, hoists and more.', { x: 0.6, y: 5.12, w: 12, h: 0.28, fontSize: 11.5, color: COL.muted, italic: true });
    s.addNotes(`Where do we find induction motors? Practically everywhere.

• Pumps – water supply, cooling water, slurry, chemicals.
• Fans and ventilation – from small cooling fans to huge tunnel and mine ventilation fans like this one.
• Compressors – plant air and refrigeration.
• Conveyors – in mining and bulk-material handling.
• HVAC – air-handling units, chillers and cooling towers in every large building.
• And general machinery: mixers, crushers, machine tools, hoists.

Why do engineers choose it for these jobs? Because it is simple, rugged, cheap and available off the shelf in every size. For a pump or a fan, it does not matter if the speed drops by a couple of percent under load. And if the process does need speed control – for example to save energy on a fan – a variable-frequency drive provides it.

The induction motor is the default. An engineer usually needs a specific reason to choose something else.`); }

  // 19 — SYNC APPLICATIONS
  { const s = content('E · Applications'); kicker(s, 'SECTION E · WHERE WE USE THEM');
    s.addText('Synchronous motors: big, constant-speed drives', { placeholder: 'title' });
    const apps = [['ph_mill.jpg', 'Ball & grinding mills', 'Mining and cement', 'V. Bukharov, CC BY-SA 4.0'], ['ph_cement.jpg', 'Cement plants', 'Mills, kiln & ID fans', 'Jb957, CC0'], ['ph_steel.jpg', 'Steel industry', 'Rolling mills, blowers', 'J. Knauer, CC BY 3.0']];
    apps.forEach((a, i) => { const x = 0.6 + i * 2.62, w = 2.45, h = w * 0.75; photo(s, a[0], x, 1.6, w, h, 'Photo: ' + a[3]);
      T(s, a[1], { x, y: 1.6 + h + 0.3, w, h: 0.35, fontSize: 15, bold: true, color: COL.white }); T(s, a[2], { x, y: 1.6 + h + 0.63, w, h: 0.3, fontSize: 12 }); });
    T(s, [{ text: 'Also: ', options: { bold: true, color: COL.white } }, { text: 'large compressors (air separation, refineries, pipelines) and large pumps – typically thousands of kW at constant speed.' }], { x: 0.6, y: 4.65, w: 7.6, h: 0.6, fontSize: 13 });
    // condenser panel
    card(s, 8.45, 1.6, 4.3, 3.65, { line: { color: COL.syn, width: 1.25 } });
    photo(s, 'ph_condenser.jpg', 8.6, 1.75, 4.0, 2.25, null);
    T(s, 'Photo: Mriya, CC BY-SA 3.0 · Wikimedia Commons', { x: 8.6, y: 4.02, w: 4, h: 0.2, fontSize: 7.5, color: '5F7A96' });
    T(s, 'SPECIAL CASE · SYNCHRONOUS CONDENSER', { x: 8.6, y: 4.27, w: 4.1, h: 0.28, fontSize: 10, bold: true, color: COL.syn, charSpacing: 2 });
    T(s, 'An over-excited synchronous machine spinning with NO mechanical load – only to supply reactive power and support grid voltage.', { x: 8.6, y: 4.55, w: 4.0, h: 0.7, fontSize: 11.5, color: COL.white });
    card(s, 0.6, 5.45, 12.15, 1.3, { fill: { color: COL.card2, transparency: 5 }, line: { color: COL.syn, width: 1.25 } });
    await iconCircle(s, 'FaLightbulb', COL.syn, 0.85, 5.68, 0.8);
    T(s, 'WHY AN ENGINEER CHOOSES IT', { x: 1.9, y: 5.6, w: 6, h: 0.3, fontSize: 11, bold: true, color: COL.syn, charSpacing: 3 });
    T(s, 'Very high power at constant (often low) speed, high efficiency at that size – plus the ability to correct the plant’s power factor. The extra cost and complexity pay off only on large drives.', { x: 1.9, y: 5.9, w: 10.65, h: 0.8, fontSize: 14, color: COL.white });
    s.addNotes(`Synchronous motors appear where drives are very large and the speed should stay constant.

• Ball and grinding mills in mining and cement plants – huge rotating drums, often driven by low-speed synchronous motors of several megawatts.
• Cement plants – mills and large fans.
• The steel industry – rolling mills and large blowers.
• Large compressors – in air-separation plants, refineries and gas pipelines – and large pumps.

Why choose a synchronous motor here? At thousands of kilowatts the extra cost of the excitation system is small compared with the benefits: high efficiency, exact constant speed, and the possibility to run at leading power factor and correct the power factor of the whole plant.

A special case on the right: the synchronous condenser. This is a synchronous machine that spins with no mechanical load at all. It is over-excited purely to supply reactive power – the "foam" – and to support the grid voltage. Utilities use them, for example the one in this photo near Melbourne, and they are becoming popular again to stabilize grids with lots of wind and solar power.`); }

  // =====================================================================
  pres.addSection({ title: 'F · Comparison & Summary' });
  // 20 — ULTIMATE COMPARISON
  { const s = content('F · Comparison & Summary'); kicker(s, 'SECTION F · THE ULTIMATE COMPARISON');
    s.addText('Induction vs. synchronous at a glance', { placeholder: 'title' });
    const hdr = (t, c) => ({ text: t, options: { bold: true, color: c, fontSize: 13, fill: { color: '0E2034' }, charSpacing: 2 } });
    const rows = [
      ['Construction', 'Simple, rugged', 'More complex'],
      ['Rotor design', 'Squirrel cage (bars + end rings)', 'Salient poles or round rotor + field winding'],
      ['Working principle', 'Induced rotor currents', 'Rotor magnet locks to the field'],
      ['Rotor excitation', 'None – induced', 'DC (slip rings/brushless) or permanent magnets'],
      ['Starting', 'Self-starting', 'Needs damper winding, VFD or aux. motor'],
      ['Operating speed', 'Slightly below synchronous', 'Exactly synchronous'],
      ['Slip', 'Yes – about 1–5 %', 'Zero'],
      ['Maintenance', 'Low', 'Higher (exciter, brushes if fitted)'],
      ['Initial cost', 'Lower', 'Higher – pays off on large drives'],
      ['Power factor', 'Lagging, varies with load', 'Adjustable – 1.0 or leading'],
      ['Typical uses', 'Pumps, fans, compressors, conveyors, HVAC', 'Mills, big compressors, large pumps, PF correction'],
    ];
    const tbl = [[hdr('', COL.white), hdr('INDUCTION MOTOR', COL.ind), hdr('SYNCHRONOUS MOTOR', COL.syn)]].concat(rows.map((r, i) => [
      { text: r[0], options: { bold: true, color: COL.white, fill: { color: i % 2 ? '0F2236' : '122A43' } } },
      { text: r[1], options: { color: COL.txt, fill: { color: i % 2 ? '0F2236' : '122A43' } } },
      { text: r[2], options: { color: COL.txt, fill: { color: i % 2 ? '0F2236' : '122A43' } } }]));
    s.addTable(tbl, { x: 0.6, y: 1.5, w: 12.15, colW: [2.35, 4.75, 5.05], rowH: 0.43, fontFace: 'Calibri', fontSize: 13, valign: 'middle', margin: [0.03, 0.08, 0.03, 0.12], border: { type: 'solid', pt: 0.75, color: '1E3A57' } });
    s.addNotes(`Here is everything side by side. Read it row by row – it should take about 30 seconds.

• Construction: induction is simple and rugged; synchronous is more complex.
• Rotor: a squirrel cage versus poles with a field winding.
• Principle: induced currents versus a rotor magnet locking onto the field.
• Rotor excitation: none for the induction motor; DC through slip rings or a brushless exciter – or permanent magnets – for the synchronous motor.
• Starting: the induction motor starts by itself; the synchronous motor needs a damper winding, a drive or an auxiliary motor.
• Speed: slightly below synchronous versus exactly synchronous.
• Slip: a few percent versus zero.
• Maintenance: low versus somewhat higher.
• Cost: lower versus higher, which pays off on large drives.
• Power factor: lagging versus adjustable, even leading.
• Uses: general-purpose drives versus large, constant-speed drives and power-factor correction.`); }

  // 21 — WHAT TO REMEMBER
  { const s = content('F · Comparison & Summary'); kicker(s, 'WHAT SHOULD WE REMEMBER?');
    s.addText('Two motors, one rotating field, two ways to follow it', { placeholder: 'title' });
    card(s, 0.6, 1.6, 5.95, 3.55, { line: { color: COL.ind, width: 1.5 } }); card(s, 6.8, 1.6, 5.95, 3.55, { line: { color: COL.syn, width: 1.5 } });
    img(s, 'ind_hero', 0.85, 1.75, 2.35); imgH(s, 'syn_hero', 7.15, 1.72, 2.4);
    T(s, 'INDUCTION', { x: 3.35, y: 1.95, w: 3.0, h: 0.3, fontSize: 12, bold: true, color: COL.ind, charSpacing: 3 });
    T(s, 'Motion through electromagnetic induction', { x: 3.35, y: 2.25, w: 3.05, h: 1.2, fontSize: 19, bold: true, color: COL.white, fontFace: 'Arial' });
    T(s, 'SYNCHRONOUS', { x: 9.4, y: 1.95, w: 3.2, h: 0.3, fontSize: 12, bold: true, color: COL.syn, charSpacing: 3 });
    T(s, 'Motion through magnetic locking and synchronized rotation', { x: 9.4, y: 2.25, w: 3.2, h: 1.4, fontSize: 19, bold: true, color: COL.white, fontFace: 'Arial' });
    T(s, 'Rotor slightly slower than the field (slip). Simple, rugged, low cost – the default choice.', { x: 0.85, y: 4.2, w: 5.5, h: 0.8, fontSize: 13.5 });
    T(s, 'Rotor exactly in step (no slip). Needs excitation and a starting method – chosen for large drives and power-factor control.', { x: 7.05, y: 4.2, w: 5.5, h: 0.8, fontSize: 13.5 });
    const k = [['FaArrowsRotate', 'The stator of both creates a rotating magnetic field at synchronous speed.'], ['FaMagnet', 'What differs is the rotor: induced currents (induction) or its own DC magnet (synchronous).'], ['FaScaleBalanced', 'Choose induction by default; choose synchronous when size, constant speed or power factor justify it.']];
    for (let i = 0; i < 3; i++) { const x = 0.6 + i * 4.1; card(s, x, 5.4, 3.95, 1.35, { fill: { color: COL.card2, transparency: 10 } }); await iconCircle(s, k[i][0], COL.accent, x + 0.2, 5.62, 0.6); T(s, k[i][1], { x: x + 0.95, y: 5.5, w: 2.85, h: 1.15, fontSize: 12.5, color: COL.white, valign: 'middle' }); }
    s.addNotes(`Let's wrap up with what you should take away.

Both motors share the same starting point: a stator that creates a magnetic field rotating at synchronous speed.

The difference is in how the rotor follows that field:
• The induction motor gets its motion through electromagnetic induction. The field induces currents in the cage, so the rotor must always be slightly slower than the field – that is the slip. It is simple, rugged and cheap – the default choice.
• The synchronous motor gets its motion through magnetic locking. Its rotor is its own magnet, locked in step with the field – exactly the same speed, no slip. It needs excitation and a starting method, and it is chosen for large drives, constant speed and power-factor control.

If someone asks you tomorrow, "What's the difference?", you can answer: "In an induction motor the rotor is dragged along by induced currents and always lags a little; in a synchronous motor the rotor is a magnet that locks onto the rotating field and turns exactly in step."`); }

  // 22 — CLOSING
  { const s = pres.addSlide({ masterName: 'TITLE', sectionTitle: 'F · Comparison & Summary' });
    T(s, 'Understanding the difference', { x: 0.6, y: 0.8, w: 12.1, h: 0.75, fontSize: 40, bold: true, color: COL.white, fontFace: 'Arial', align: 'center' });
    T(s, 'is the first step toward understanding industrial motor applications.', { x: 0.6, y: 1.6, w: 12.1, h: 0.5, fontSize: 22, color: COL.txt, align: 'center' });
    img(s, 'ind_cut', 1.2, 2.45, 4.1);
    imgH(s, 'syn_cut', 8.2, 2.35, 4.2);
    T(s, 'THANK YOU', { x: 5.2, y: 4.0, w: 3.0, h: 0.5, fontSize: 20, bold: true, color: COL.white, align: 'center', charSpacing: 4, fontFace: 'Arial' });
    T(s, 'QUESTIONS?', { x: 5.2, y: 4.5, w: 3.0, h: 0.4, fontSize: 14, bold: true, color: COL.accent, align: 'center', charSpacing: 4 });
    T(s, '3D models and animations created for this session. Photographs: Wikimedia Commons contributors under the licences stated on each slide.', { x: 0.6, y: 6.85, w: 12.1, h: 0.3, fontSize: 9, color: '5F7A96', align: 'center' });
    s.addNotes(`Understanding the difference between these two motors is the first step toward understanding industrial motor applications – why a particular motor was chosen, how it is started, how it is maintained and how it affects the plant's power system.

Thank you. I am happy to take questions.

Possible questions to prepare for:
• "Can an induction motor run at exactly synchronous speed?" – Not as a motor. Above synchronous speed it actually becomes a generator.
• "Why not use synchronous motors everywhere?" – Higher cost and complexity; for small and medium drives the induction motor is the better buy.
• "What happens if a synchronous motor is overloaded?" – It pulls out of step and must be tripped by protection.
• "What about electric cars?" – Many use permanent-magnet synchronous motors, some use induction motors; both are fed from a variable-frequency inverter.`); }

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log('wrote', OUT);
})().catch(e => { console.error(e); process.exit(1); });
