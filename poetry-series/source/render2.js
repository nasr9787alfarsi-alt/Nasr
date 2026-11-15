const { chromium } = require('playwright');
const path = require('path'); const fs = require('fs');
const S = __dirname; const scale = Number(process.argv[2] || 2);
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: Number(process.argv[3]||1350) }, deviceScaleFactor: scale });
  fs.mkdirSync(path.join(S, (process.argv[4]||'out')), { recursive: true });
  for (const f of fs.readdirSync(path.join(S, 'html')).sort()) {
    await p.goto('file://' + path.join(S, 'html', f));
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(150);
    const out = path.join(S, (process.argv[4]||'out'), f.replace('.html', scale === 1 ? '_preview.png' : '.png'));
    await p.screenshot({ path: out });
  }
  await b.close();
})();
