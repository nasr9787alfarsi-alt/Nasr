const { chromium } = require('playwright');
const path=require('path');
(async()=>{
  const f=process.argv[2], out=process.argv[3];
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:2245,height:1588}});
  await p.goto('file://'+path.resolve(f)); await p.waitForFunction(()=>document.body.dataset.ready==='1'); await p.waitForTimeout(200);
  const rep=await p.evaluate(()=>{
    const mm=v=>(v/3.7795).toFixed(1); const r=[];
    const pg=document.querySelector('.page'); r.push('page content '+mm(pg.scrollHeight)+' / '+mm(pg.clientHeight));
    [...pg.children].forEach(e=>{if(e.tagName==='svg')return;const b=e.getBoundingClientRect(); r.push((e.className||e.tagName)+' '+mm(b.top)+'-'+mm(b.bottom)+' h'+mm(b.height));});
    document.querySelectorAll('.card,.stage,.oman').forEach(e=>{if(e.scrollHeight>e.clientHeight+1||e.scrollWidth>e.clientWidth+1) r.push('OVERFLOW '+e.className);});
    const sizes={}; document.querySelectorAll('body *').forEach(e=>{if(e.closest('svg'))return; if([...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())){const fs=(parseFloat(getComputedStyle(e).fontSize)*0.75).toFixed(0); sizes[fs]=(sizes[fs]||0)+1;}});
    r.push('html text pt: '+JSON.stringify(sizes));
    return r;});
  console.log(rep.join('\n'));
  await p.screenshot({path:out+'.png'});
  await p.pdf({path:out+'.pdf',width:'594mm',height:'420mm',printBackground:true,preferCSSPageSize:true});
  await b.close();
})();
