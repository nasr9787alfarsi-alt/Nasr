# Small, thin bottom title: "ALEXANDRIA" in Cormorant Garamond Light, widely tracked, gentle fade and settle.
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S=sys.argv[1]; W,H=1080,1920
F=ImageFont.truetype(S+'/fonts/package/files/cormorant-garamond-latin-300-normal.woff',46)
Y=1652          # baseline area ~86% down the frame, clear of faces and subjects
def ease(x): x=min(max(x,0),1); return x*x*(3-2*x)
def frame(alpha,track,dy,Y=1652):
    img=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    text='ALEXANDRIA'; ws=[F.getlength(c) for c in text]; total=sum(ws)+track*(len(text)-1); x=(W-total)/2
    for c,w in zip(text,ws):
        d.text((x,Y+dy),c,font=F,fill=(255,255,255,int(255*alpha)),anchor='lm'); x+=w+track
    a=img.split()[3]; sh=Image.new('RGBA',(W,H),(0,0,0,0))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(8)).point(lambda v:int(v*0.35)))
    return Image.alpha_composite(sh,img)
def render(name,dur,fin,fout,Y=1652):
    out=f'{S}/ttl/{name}'; os.makedirs(out,exist_ok=True); n=round(dur*30)
    for k in range(n):
        t=k/30; a=ease(t/fin)*(1-ease((t-(dur-fout))/fout) if fout else 1)
        frame(a, 17+7*(1-ease(t/(fin*1.8))), 6*(1-ease(t/fin)),Y).save(f'{out}/{k:04d}.png')
    print(name,n)
render('open',2.25,0.8,0.45)     # on the Stanley Bridge hero shot
render('end',5.30,1.2,0,Y=1560)         # on the final sea shot; leaves with the picture fade
