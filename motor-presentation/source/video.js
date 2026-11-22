// node video.js kind out.mp4 [fps] [t0] [t1]
const { chromium } = require('playwright'); const { spawn } = require('child_process');
(async()=>{
  const [kind, out, fpsA, t0A, t1A, everyA] = process.argv.slice(2); const fps=+(fpsA||25);
  const W=1920,H=1080;
  const b = await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const p = await b.newPage({viewport:{width:W,height:H}});
  p.on('pageerror', e=>console.log('PAGEERR', e.message));
  await p.goto('file://'+__dirname+'/stage.html');
  await p.evaluate(k=>{ STAGE.init({model:k}); window.__D = DIRECTOR.make(k); }, kind);
  const dur = await p.evaluate(()=>__D.duration);
  const t0=+(t0A||0), t1=t1A?+t1A:dur; const every = +(everyA||0);
  console.log(kind,'duration',dur.toFixed(2));
  if(every){ // contact frames for QA
    for(let t=t0;t<t1;t+=every){ await p.evaluate(t=>__D.frame(t), t); await p.locator('#root').screenshot({path:`${out}_${t.toFixed(1)}.jpg`,type:'jpeg',quality:80}); }
    await b.close(); return;
  }
  const ff = spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',String(fps),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','slow','-crf','19','-pix_fmt','yuv420p','-profile:v','high','-level','4.1','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
  const N=Math.round((t1-t0)*fps); const st=Date.now();
  for(let f=0;f<N;f++){
    const t=t0+f/fps; await p.evaluate(t=>__D.frame(t), t);
    const buf = await p.locator('#root').screenshot({type:'jpeg',quality:94});
    if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
    if(f%50==0) console.log(kind, f,'/',N, ((Date.now()-st)/1000/(f+1)).toFixed(2),'s/frame');
  }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('done',out);
})();
