# Edit decision list. Shots: (clip, start_beat, end_beat, src_in, note). Film beat index -> time from beatmap.
import json, os
S=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BT={}
for l in open(S+'/audio/beatmap.txt'):
    p=l.split(); BT[int(p[0])]=float(p[1])
def T(b): return 0.0 if b=='start' else BT[b]
SHOTS=[
 # HUSH - the intro melody, the traveller and the approaching train
 ('6178','start',3,  2.50,'the traveller watches the train'),
 ('6177',3,7,        1.70,'headlight approaching'),
 # HIT - accent replaces the band drop: the journey
 ('6173',7,10,       0.00,'HIT: train blasts past'),
 ('6096',10,12,      0.80,'golden fields from the window'),
 ('6095',12,14,      0.70,'fields and viaduct'),
 ('6176',14,16,      1.60,'train pulls into Alexandria'),
 # REVEAL + TITLE
 ('6103',16,24,      0.00,'sea reveal, TITLE'),
 # ALEXANDRIA - loudest block of the song: one- and two-beat cuts
 ('6099',24,25,      0.20,'yellow taxi'),
 ('6100',25,26,      0.50,'downtown street'),
 ('6105',26,27,      0.50,'street corner'),
 ('6128',27,29,      0.00,'palace with flags'),
 ('6112',29,31,      0.50,'red carpet staircase'),
 ('6113',31,32,      0.60,'stained glass, portrait'),
 ('6119',32,33,      0.80,'glowing doorway'),
 ('6135',33,35,      0.30,'night facade'),
 ('6143',35,37,      1.00,'night, light beams'),
 ('6170',37,39,      0.50,'Stanley Bridge towers'),
 ('6160',39,40,      2.00,'Stanley tower, bus'),
 ('6167',40,42,      1.50,'Stanley tower (strongest accent)'),
 ('6168',42,44,      1.00,'cars along the sea railing'),
 ('6152',44,46,      0.30,'the sea and the pier from above'),
 # OUTRO - longer shots as the song resolves
 ('6153',46,50,      0.20,'Corniche from above'),
 ('6164',50,55,      0.30,'turquoise bay'),
 ('6179',55,61,      0.35,'golden locomotive'),
 ('6162',61,None,    0.00,'the sea - END CARD, hard cut on the final accent'),
]
DISSOLVE={1:0.5, 23:0.7}  # index of incoming shot -> duration
FPS=30
def build():
    out=[]
    for i,(c,a,b,si,n) in enumerate(SHOTS):
        t0=T(a); t1=T(b) if b is not None else t0+6.32-si
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
