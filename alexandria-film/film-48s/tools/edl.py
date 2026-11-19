# Edit decision list. Shots: (clip, start_beat, end_beat, src_in, note). Film beat index -> time from beatmap.
import json, os
S=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BT={}
for l in open(S+'/audio/beatmap.txt'):
    p=l.split(); BT[int(p[0])]=float(p[1])
def T(b): return 0.0 if b=='start' else BT[b]
SHOTS=[
 # JOURNEY - opens on the section hit; one train shot, one window
 ('6178','start',4,  1.80,'HIT: the traveller watches the train'),
 ('6096',4,7,        3.00,'golden fields through the window'),
 # ALEXANDRIA - hero shot with the title
 ('6170',7,12,       1.00,'Stanley Bridge towers, TITLE'),
 ('6098',12,14,      0.30,'station square, people'),
 ('6131',14,16,      1.60,'taxi rolls in'),
 ('6128',16,18,      2.40,'palace with flags'),
 ('6109',18,20,      0.40,'palace statue'),
 ('6101',20,22,      2.20,'alley'),
 ('6110',22,24,      3.40,'palace facade'),
 # TREASURES - the big accent
 ('6112',24,27,      2.40,'ACCENT: red carpet staircase'),
 ('6123',27,29,      1.00,'chandelier hall'),
 ('6113',29,31,      1.00,'stained glass, the queen portrait'),
 ('6125',31,33,      0.80,'red jewellery display'),
 ('6119',33,36,      2.00,'glowing doorway'),
 ('6116',36,39,      1.00,'gallery corridor'),
 # NIGHT - the loudest part of the song
 ('6136',39,41,      0.70,'night, light beams, crowd'),
 ('6140',41,42,      1.40,'night crowds'),
 ('6135',42,43,      0.40,'night facade'),
 ('6141',43,45,      2.20,'long night street'),
 ('6143',45,47,      1.00,'light beams'),
 # THE CORNICHE
 ('6103',47,49,      1.00,'the sea opens up'),
 ('6160',49,51,      3.40,'Stanley tower, traffic'),
 ('6167',51,52,      1.00,'tower and lamp'),
 ('6168',52,54,      1.40,'red car along the sea railing'),
 ('6153',54,56,      0.50,'Corniche from above'),
 ('6169',56,58,      4.30,'motorbike along the railing'),
 ('6152',58,63,      0.30,'the sea and the pier'),
 # OUTRO - longer, calmer
 ('6164',63,67,      1.00,'turquoise bay'),
 ('6180',67,71,      0.60,'flags in golden light'),
 ('6179',71,78,      0.50,'golden-hour locomotive'),
 ('6162',78,None,    0.00,'the sea - final title'),
]
DISSOLVE={29:0.5}  # index of incoming shot -> duration
FPS=30
def build():
    out=[]
    for i,(c,a,b,si,n) in enumerate(SHOTS):
        t0=T(a); t1=T(b) if b is not None else t0+6.30-si
        out.append(dict(i=i,clip=c,t0=t0,t1=t1,src=si,note=n))
    for k,d in DISSOLVE.items():
        if d<=0: continue
        out[k-1]['hout']=d/2; out[k]['hin']=d/2
    return out
if __name__=='__main__':
    import subprocess
    for s in build():
        dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'{S}/src/vid/IMG_{s["clip"]}.MOV']))
        a=s['src']-s.get('hin',0); b=s['src']+(s['t1']-s['t0'])+s.get('hout',0)
        flag='' if a>=0 and b<=dur-0.02 else '  <<< OUT OF RANGE'
        print(f"{s['i']:2d} {s['clip']} {s['t0']:7.3f}-{s['t1']:7.3f} ({s['t1']-s['t0']:.2f}s) src {a:.2f}-{b:.2f}/{dur:.2f}{flag}")
