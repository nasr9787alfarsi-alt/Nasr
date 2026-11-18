import sys, os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S=sys.argv[1]; MODE=sys.argv[2]; WHITE=255 if MODE=='sdr' else 191  # HLG: diffuse white ~75% signal
F=S+'/fonts/package/files/cormorant-garamond-latin-'
def font(n,s): return ImageFont.truetype(n,s)
SERIF=F+'500-normal.woff'; ITAL=F+'400-italic.woff'
SANS='/usr/share/fonts/truetype/inter/Inter-Light.ttf' if os.path.exists('/usr/share/fonts/truetype/inter/Inter-Light.ttf') else None
if SANS is None:
    import subprocess; SANS=subprocess.check_output(['fc-match','-f','%{file}','Inter:style=Light']).decode()
W,H=1080,1920
def ease(x): x=min(max(x,0),1); return x*x*(3-2*x)
def tracked(draw,text,f,cy,track,alpha):
    widths=[f.getlength(ch) for ch in text]; total=sum(widths)+track*(len(text)-1)
    x=(W-total)/2
    for ch,w in zip(text,widths):
        draw.text((x,cy),ch,font=f,fill=(WHITE,WHITE,WHITE,int(255*alpha)),anchor='lm'); x+=w+track
    return total
def frame(layers):
    img=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    for L in layers: L(d)
    # soft shadow for legibility on bright skies (very subtle)
    a=img.split()[3]; sh=Image.new('RGBA',(W,H),(0,0,0,0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(10)).point(lambda v:int(v*0.30)))
    return Image.alpha_composite(sh,img)
def render(name,dur,layersfn):
    out=f'{S}/ttl/{MODE}_{name}'; os.makedirs(out,exist_ok=True)
    n=round(dur*30)
    for k in range(n): frame(layersfn(k/30,dur)).save(f'{out}/{k:04d}.png')
    return n
# OPENING TITLE: 3.75s on 6103
big=font(SERIF,92); small=font(SANS,25)
def title(t,dur):
    a1=ease((t-0.0)/1.1)*(1-ease((t-(dur-0.55))/0.55))
    a2=ease((t-0.55)/0.9)*(1-ease((t-(dur-0.55))/0.55))
    track=34+10*(1-ease(t/2.2))           # letters settle gently
    line=ease((t-0.35)/1.0)
    def L(d):
        tracked(d,'ALEXANDRIA',big,540,track,a1)
        lw=int(70*line); 
        if lw>1: d.line([(W/2-lw/2,598),(W/2+lw/2,598)],fill=(WHITE,WHITE,WHITE,int(200*a2)),width=2)
        tracked(d,'THE MEDITERRANEAN EXPERIENCE',small,640,9,a2*0.95)
    return [L]
# END CARD on the final sea shot
it=font(ITAL,58); mid=font(SERIF,44); tiny=font(SANS,22)
def end(t,dur):
    a1=ease((t-0.0)/1.4)*(1-ease((t-(dur-0.9))/0.9))
    a2=ease((t-0.9)/1.2)*(1-ease((t-(dur-0.9))/0.9))
    def L(d):
        tracked(d,'until we meet again',it,600,1.5,a1)
        tracked(d,'ALEXANDRIA',mid,690,20,a2)
        tracked(d,'NOVEMBER 2026',tiny,745,8,a2*0.85)
    return [L]
print(render('title',3.75,title), render('end',4.4,end))
