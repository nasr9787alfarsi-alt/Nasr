const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1588,height:2245},deviceScaleFactor:4});
await p.goto('file:///home/user/Nasr/economics-poster/source/poster.html'); await p.waitForFunction(()=>document.body.dataset.ready==='1');
const names=['market','mixed','command'];
for(let i=0;i<3;i++){const k=p.locator('.kitchens .kit').nth(i);
 console.log(names[i], (await k.locator('.sign b').textContent()));
 await k.locator('.art svg').screenshot({path:`img/kit_${names[i]}.png`});
 await k.locator('svg.flow').screenshot({path:`img/flow_${names[i]}.png`,omitBackground:true});}
await b.close();})();
