const { chromium } = require('playwright'); const path=require('path');
(async()=>{const f=process.argv[2], out=process.argv[3];
const b=await chromium.launch(); const p=await b.newPage({viewport:{width:2245,height:1588}});
await p.goto('file://'+path.resolve(f)); await p.waitForFunction(()=>document.body.dataset.ready==='1'); await p.waitForTimeout(150);
console.log(await p.evaluate(()=>{const mm=v=>(v/3.7795).toFixed(1); const r=[];
 document.querySelectorAll('.page > .abs').forEach(e=>{const bb=e.getBoundingClientRect(); if(e.tagName!=='svg'||e.classList.contains('sky')) r.push((e.className.baseVal!==undefined?e.className.baseVal:e.className)+' x'+mm(bb.left)+'-'+mm(bb.right)+' y'+mm(bb.top)+'-'+mm(bb.bottom));});
 document.querySelectorAll('.scene li,.tg > div,.oman .it,.stars b,.tagline,.sub,.epi,.pro h2,.q,.scene .hd').forEach(e=>{const dw=e.scrollWidth-e.clientWidth; if(dw>1) r.push('XOVER "'+e.textContent.trim().slice(0,32)+'" '+mm(dw));});
 return r.join('\n');}));
await p.screenshot({path:out+'.png'}); await p.pdf({path:out+'.pdf',width:'594mm',height:'420mm',printBackground:true,preferCSSPageSize:true}); await b.close();})();
