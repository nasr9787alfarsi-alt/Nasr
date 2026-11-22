// usage: node still.js out.png '<js to run after init>' '{"model":"induction"}'
const { chromium } = require('playwright');
(async()=>{
  const [out, code, optsJson] = process.argv.slice(2);
  const opts = JSON.parse(optsJson||'{}'); const W=opts.w||1920,H=opts.h||1080;
  const b = await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const p = await b.newPage({viewport:{width:W,height:H}});
  p.on('console', m=>{ if(m.type()==='error'||m.type()==='warning') console.log('PAGE', m.text()); });
  p.on('pageerror', e=>console.log('PAGEERR', e.message));
  await p.goto('file://'+__dirname+'/stage.html');
  const t0=Date.now();
  await p.evaluate(o=>STAGE.init(o), opts);
  await p.evaluate(code);
  console.log('render ms', Date.now()-t0);
  await p.locator('#root').screenshot({path: out, type: out.endsWith('.jpg')?'jpeg':'png', ...(out.endsWith('.jpg')?{quality:92}:{}) , omitBackground: !!opts.transparent, timeout: 240000});
  await b.close();
})();
