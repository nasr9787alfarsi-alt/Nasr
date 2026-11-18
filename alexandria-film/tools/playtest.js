// Real playback test: serve the file over HTTP, play it end-to-end in Chromium's
// <video> element, seek to several points and check pixels, decode the full audio.
// usage: node playtest.js <dir> <file.mp4> <port>
const { chromium } = require('playwright');
const [dir, file, port] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));
  await p.goto(`http://127.0.0.1:${port}/`);
  const r = await p.evaluate(async (src) => {
    const out = {};
    const v = document.createElement('video');
    v.muted = true; v.preload = 'auto'; v.src = src;
    v.style.width='270px';v.style.height='480px';v.id='v';document.body.appendChild(v);
    out.canPlay = v.canPlayType('video/mp4; codecs="avc1.640029, mp4a.40.2"');
    await new Promise((res, rej) => { v.onloadedmetadata = res; v.onerror = () => rej(new Error('load error ' + (v.error && v.error.code))); });
    out.duration = v.duration; out.w = v.videoWidth; out.h = v.videoHeight;
    // full playback, start to end
    v.currentTime = 0; await new Promise(res => v.onseeked = res);
    v.playbackRate = 1;
    const t0 = performance.now();
    let errored = null; v.onerror = () => errored = v.error && v.error.code;
    let stalls = 0; v.onwaiting = () => stalls++;
    await v.play();
    await new Promise(res => { v.onended = res; setTimeout(res, 150000); });
    out.ended = v.ended; out.endTime = v.currentTime; out.playError = errored; out.waitingEvents = stalls;
    out.wallSec = +((performance.now() - t0) / 1000).toFixed(1);
    const q = v.getVideoPlaybackQuality();
    out.decodedFrames = q.totalVideoFrames; out.droppedFrames = q.droppedVideoFrames;
    // decode the entire audio track
    const buf = await (await fetch(src)).arrayBuffer();
    const ac = new OfflineAudioContext(2, 48000, 48000);
    const ab = await ac.decodeAudioData(buf);
    const ch = ab.getChannelData(0); let pk = 0; for (let i = 0; i < ch.length; i++) pk = Math.max(pk, Math.abs(ch[i]));
    out.audio = { sec: +ab.duration.toFixed(3), ch: ab.numberOfChannels, rate: ab.sampleRate, peak: +pk.toFixed(3) };
    return out;
  }, '/' + file);
  r.seeks = [];
  const { PNG } = (() => { try { return require('pngjs'); } catch (e) { return {}; } })();
  for (const t of [0.5, 13.5, 49.5, 75, 100, 115]) {
    await p.evaluate(async (t) => { const v = document.getElementById('v'); v.pause(); v.currentTime = t; await new Promise(r => v.onseeked = r); await new Promise(r => setTimeout(r, 300)); }, t);
    const shot = await p.locator('#v').screenshot({ path: `${dir}/../qa3/seek_${file.slice(0,12)}_${t}.png` });
    r.seeks.push([t, shot.length]);
  }
  r.pageErrors = errs;
  console.log(JSON.stringify(r));
  await b.close();
})().catch(e => { console.log('FAIL', e.message); process.exit(1); });
