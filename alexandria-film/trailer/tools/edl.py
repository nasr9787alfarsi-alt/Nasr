# Edit decision list. Shots: (clip, start_beat, end_beat, src_in, note). Film beat index -> time from beatmap.
import json, os
S=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BT={}
for l in open(S+'/audio/beatmap.txt'):
    p=l.split(); BT[int(p[0])]=float(p[1])
def T(b): return 0.0 if b=='start' else BT[b]
SHOTS=[
 # DEPARTURE - free intro (unchanged from the full film)
 ('6094','start',6,  0.40,'platform at dawn, fade in'),
 ('6093',6,9,        0.00,'train nose, sun flare'),
 ('6178',9,19,       0.40,'the traveller watches the train'),
 ('6177',19,26,      0.25,'headlight approaching in the hush'),
 # JOURNEY - band drop
 ('6173',26,30,      0.00,'DROP: train blasts past'),
 ('6096',30,36,      0.50,'window, golden fields'),
 ('6095',36,42,      0.70,'fields and viaduct'),
 ('6176',42,51,      0.20,'train pulls into Alexandria (verse splice on the cut)'),
 # ARRIVAL
 ('6098',51,55,      0.30,'station square'),
 ('6099',55,59,      0.20,'black-and-yellow taxi'),
 ('6101',59,64,      0.50,'alley, breath before the hit'),
 # REVEAL + TITLE
 ('6103',64,72,      0.00,'HIT: sea reveal, TITLE'),
 # TREASURES - accent (song splice on the cut)
 ('6128',72,76,      0.00,'ACCENT: palace with flags'),
 ('6112',76,81,      0.50,'red carpet staircase'),
 ('6143',81,87,      1.00,'night, light beams'),
 # PEAK - Stanley Bridge and the Corniche
 ('6170',87,91,      0.50,'bridge towers'),
 ('6167',91,96,      1.50,'Stanley tower'),
 ('6168',96,100,     1.00,'cars along the sea railing'),
 ('6152',100,105,    0.30,'the sea and the pier from above'),
 ('6153',105,111,    0.20,'Corniche from above'),
 # OUTRO
 ('6164',111,119,    0.30,'turquoise bay'),
 ('6179',119,126,    0.35,'golden locomotive'),
 ('6162',126,None,   0.35,'the sea - END CARD'),
]
DISSOLVE={2:0.5, 3:0.5, 21:0.7, 22:0.7}  # index of incoming shot -> duration
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
