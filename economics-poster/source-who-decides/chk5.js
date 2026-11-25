const { chromium } = require('playwright'); const path=require('path');
(async()=>{const b=await chromium.launch(); const p=await b.newPage({viewport:{width:2245,height:1588}});
await p.goto('file://'+path.resolve('poster.html')); await p.waitForFunction(()=>document.body.dataset.ready==='1');
const r=await p.evaluate(()=>{const mm=v=>(v/3.7795).toFixed(1); const o=[];
document.querySelectorAll('.tg > div,.card li,.card .ttl,.names .m,.hook,.script,.oman .it,.pill p,.concl p,h2').forEach(e=>{
 const dw=e.scrollWidth-e.clientWidth, dh=e.scrollHeight-e.clientHeight;
 if(dw>1||dh>3) o.push((e.className||e.tagName)+' "'+e.textContent.trim().slice(0,30)+'" dw='+mm(dw)+' dh='+mm(dh));});
// also check text runs right edge vs parent box
return o;}); console.log(r.join('\n')||'no overflow'); await b.close();})();
