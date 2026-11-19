# "Alexandria" in Pinyon Script (opening hero + final shot) above a small tracked line that stays on screen for the whole film.
import sys, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S=sys.argv[1]; W,H=1080,1920
SCRIPT=ImageFont.truetype(S+'/fonts_extra/pinyon-script-latin-400-normal.woff',118)
SANS=ImageFont.truetype(subprocess.check_output(['fc-match','-f','%{file}','Inter:style=Light']).decode(),21)
YW, YS = 1745, 1805          # wordmark baseline, subtitle centre
def ease(x): x=min(max(x,0),1); return x*x*(3-2*x)
def shadowed(img,k=0.42):
    a=img.split()[3]; sh=Image.new('RGBA',(W,H),(0,0,0,0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(9)).point(lambda v:int(v*k)))
    return Image.alpha_composite(sh,img)
def subtitle():
    img=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(img); t='THE MEDITERRANEAN EXPERIENCE'
    ws=[SANS.getlength(c) for c in t]; tot=sum(ws)+7*(len(t)-1); x=W/2-tot/2
    for c,w in zip(t,ws): d.text((x,YS),c,font=SANS,fill=(255,255,255,235),anchor='lm'); x+=w+7
    return shadowed(img)
def wordmark(t,dur,fin=1.0,fout=0.45):
    a=ease(t/fin)*((1-ease((t-(dur-fout))/fout)) if fout else 1)
    img=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    d.text((W/2,YW+8*(1-ease(t/fin))),'Alexandria',font=SCRIPT,fill=(255,255,255,int(255*a)),anchor='ms')
    return shadowed(img)
def render(name,dur,fout):
    out=f'{S}/ttl/{name}'; os.makedirs(out,exist_ok=True)
    for k in range(round(dur*30)): wordmark(k/30,dur,fout=fout).save(f'{out}/{k:04d}.png')
if __name__=='__main__':
    os.makedirs(f'{S}/ttl',exist_ok=True); subtitle().save(f'{S}/ttl/subtitle.png')
    render('open',2.25,0.45); render('end',5.30,0)
