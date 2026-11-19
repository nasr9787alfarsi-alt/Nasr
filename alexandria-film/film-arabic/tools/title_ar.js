// Renders the Arabic title "الإسكندرية" as a transparent 1080x1920 PNG with the browser's Arabic shaping (RTL, joined letters).
const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
const W=process.argv[2];
(async()=>{
 const b=await chromium.launch({args:['--allow-file-access-from-files']}); const p=await b.newPage({viewport:{width:1080,height:1920}});
 const html=`<html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>
 @font-face{font-family:Ruqaa;src:url('../fonts_ar/aref-ruqaa-arabic-400-normal.woff2') format('woff2')}
 html,body{margin:0;width:1080px;height:1920px;background:transparent}
 .t{position:absolute;left:0;right:0;top:1742px;height:60px;direction:rtl;font-family:Ruqaa;font-size:50px;line-height:60px;
    color:rgba(255,255,255,.94);text-shadow:0 0 12px rgba(0,0,0,.38),0 1px 2px rgba(0,0,0,.30);
    display:flex;justify-content:center;align-items:center;gap:20px}
 .l{width:40px;height:1.5px;background:rgba(255,255,255,.72);box-shadow:0 0 6px rgba(0,0,0,.3)}
 </style></head><body><div class="t"><span class="l"></span><span>الإسكندرية</span><span class="l"></span></div></body></html>`;
 fs.writeFileSync(path.join(W,'ttl','title.html'),html);
 await p.goto('file://'+path.join(W,'ttl','title.html')); await p.evaluate(()=>document.fonts.ready);
 if(!(await p.evaluate(()=>document.fonts.check('50px Ruqaa')))) throw new Error('font not loaded');
 await p.screenshot({path:path.join(W,'ttl','title_ar.png'),omitBackground:true});
 await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
