# "Alexandria" in Cormorant Garamond Light Italic, with one small tracked line beneath, near the bottom.
import sys, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S=sys.argv[1]; W,H=1080,1920
SCRIPT=ImageFont.truetype(S+'/fonts/package/files/cormorant-garamond-latin-300-italic.woff',124)
SANS=ImageFont.truetype(subprocess.check_output(['fc-match','-f','%{file}','Inter:style=Light']).decode(),21)
def ease(x): x=min(max(x,0),1); return x*x*(3-2*x)
def tracked(d,text,f,cx,cy,track,alpha):
    ws=[f.getlength(c) for c in text]; total=sum(ws)+track*(len(text)-1); x=cx-total/2
    for c,w in zip(text,ws): d.text((x,cy),c,font=f,fill=(255,255,255,int(255*alpha)),anchor='lm'); x+=w+track
def frame(t,dur,Y,sub,fin=1.0,fout=0.5):
    out=(1-ease((t-(dur-fout))/fout)) if fout else 1
    a1=ease(t/fin)*out; a2=ease((t-0.45)/fin)*out
    img=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    dy=8*(1-ease(t/fin))
    d.text((W/2,Y+dy),'Alexandria',font=SCRIPT,fill=(255,255,255,int(255*a1)),anchor='ms')
    lw=int(46*ease((t-0.3)/fin))
    if lw>1: d.line([(W/2-lw/2,Y+30),(W/2+lw/2,Y+30)],fill=(255,255,255,int(170*a2)),width=1)
    tracked(d,sub,SANS,W/2,Y+62,7+3*(1-ease(t/1.6)),a2*0.92)
    a=img.split()[3]; sh=Image.new('RGBA',(W,H),(0,0,0,0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(9)).point(lambda v:int(v*0.32)))
    return Image.alpha_composite(sh,img)
def render(name,dur,Y,sub,fout):
    out=f'{S}/ttl/{name}'; os.makedirs(out,exist_ok=True)
    for k in range(round(dur*30)): frame(k/30,dur,Y,sub,fout=fout).save(f'{out}/{k:04d}.png')
if __name__=='__main__':
    render('open',2.25,1590,'THE MEDITERRANEAN EXPERIENCE',0.45)
    render('end',5.30,1420,'EGYPT  ·  NOVEMBER 2026',0)
