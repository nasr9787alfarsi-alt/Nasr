const { chromium } = require('playwright');
const path=require('path');
(async()=>{
  const f=process.argv[2], out=process.argv[3];
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1588,height:2245}});
  await p.goto('file://'+path.resolve(f)); await p.evaluate(()=>document.fonts.ready); await p.waitForFunction(()=>document.body.dataset.ready==='1');
  await p.evaluate(()=>{ /* rerun layout script after fonts */ });
  const rep=await p.evaluate(()=>{
    const r=[]; const mm=v=>(v/3.7795).toFixed(1);
    document.querySelectorAll('.card,.crew,.refs,.titlewrap').forEach(e=>{const b=e.getBoundingClientRect();
      r.push((e.id||e.className)+' top '+mm(b.top)+' bottom '+mm(b.bottom)+(e.scrollHeight>e.clientHeight+1?' OVERFLOW '+mm(e.scrollHeight-e.clientHeight):''));});
    return r;});
  console.log(rep.join('\n'));
  await p.screenshot({path:out+'.png'});
  await p.pdf({path:out+'.pdf',width:'420mm',height:'594mm',printBackground:true,preferCSSPageSize:true});
  await b.close();
})();
