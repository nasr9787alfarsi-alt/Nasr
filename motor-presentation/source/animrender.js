// node animrender.js kind out(.mp4|prefix) fps [qaEvery] [w h transparent]
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const fs=require('fs');
(async()=>{
  const [kind,out,fpsA,every,wA,hA,tr]=process.argv.slice(2); const fps=+(fpsA||30); const W=+(wA||1920),H=+(hA||1080);
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:W,height:H}});
  p.on('pageerror',e=>console.log('PAGEERR',e.message));
  await p.goto('file://'+__dirname+'/anim.html');
  await p.evaluate(([k,w,h,tr])=>{ANIM.init(w,h); window.__A=ANIM.make(k,{transparent:tr==='1'});},[kind,W,H,tr]);
  await p.evaluate(()=>document.fonts.ready);
  const dur=await p.evaluate(()=>__A.duration); console.log(kind,'dur',dur);
  const grab=async(t)=>{ return await p.evaluate(t=>{__A.frame(t); return document.getElementById('cv').toDataURL('image/png');},t); };
  if(+every){ for(let t=0.01;t<dur;t+=+every){ const d=await grab(t); fs.writeFileSync(`${out}_${t.toFixed(1)}.png`,Buffer.from(d.split(',')[1],'base64')); } await b.close(); return; }
  if(out.endsWith('/')){ fs.mkdirSync(out,{recursive:true}); const N=Math.round(dur*fps); for(let f=0;f<N;f++){ const d=await grab(f/fps); fs.writeFileSync(`${out}f${String(f).padStart(5,'0')}.png`,Buffer.from(d.split(',')[1],'base64')); } await b.close(); return; }
  const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',String(fps),'-c:v','png','-i','-','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-level','4.1','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
  const N=Math.round(dur*fps);
  for(let f=0;f<N;f++){ const d=await grab(f/fps); const buf=Buffer.from(d.split(',')[1],'base64'); if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('done',out);
})();
