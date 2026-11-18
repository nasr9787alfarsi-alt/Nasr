// Play the file and read real decoded luma from frames as they are presented.
const { chromium } = require('playwright');
const [file, port] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }); const p = await b.newPage();
  await p.goto(`http://127.0.0.1:${port}/`);
  console.log(JSON.stringify(await p.evaluate(async (src) => {
    const v = document.createElement('video'); v.muted = true; v.src = src; document.body.appendChild(v);
    await new Promise(r => v.onloadeddata = r);
    const samples = []; let next = 0; let busy = false;
    const cb = async (now, meta) => {
      if (!busy && meta.mediaTime >= next) {
        busy = true; next += 4;
        const f = new VideoFrame(v, { timestamp: 0 });
        const buf = new Uint8Array(f.allocationSize()); await f.copyTo(buf);
        let s = 0, c = 0; const ny = f.codedWidth * f.codedHeight;
        for (let i = 0; i < ny; i += 101) { s += buf[i]; c++; }
        samples.push([+meta.mediaTime.toFixed(2), +(s / c).toFixed(1)]); f.close(); busy = false;
      }
      if (!v.ended) v.requestVideoFrameCallback(cb);
    };
    v.requestVideoFrameCallback(cb); v.playbackRate = 2; await v.play();
    await new Promise(r => { v.onended = r; setTimeout(r, 90000); });
    return { ended: v.ended, samples };
  }, '/' + file)));
  await b.close();
})().catch(e => { console.log('FAIL', e.message); process.exit(1); });
