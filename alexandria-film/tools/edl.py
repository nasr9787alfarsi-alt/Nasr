# Edit decision list. Shots: (clip, start_beat, end_beat, src_in, note). Film beat index -> time from beatmap.
import json, os
S=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BT={}
for l in open(S+'/audio/beatmap.txt'):
    p=l.split(); BT[int(p[0])]=float(p[1])
def T(b): return 0.0 if b=='start' else BT[b]
SHOTS=[
 # PROLOGUE - free intro melody
 ('6094','start',6,  0.40,'platform at dawn, fade in'),
 ('6093',6,9,        0.00,'train nose, sun flare'),
 ('6178',9,19,       0.40,'the traveller watches the train'),
 ('6177',19,26,      0.25,'headlight approaching in the hush'),
 # JOURNEY - band drop
 ('6173',26,30,      0.00,'DROP: train blasts past'),
 ('6096',30,38,      0.50,'window, golden fields'),
 ('6095',38,46,      0.70,'fields and viaduct'),
 ('6097',46,51,      0.20,'window frame'),
 ('6176',51,62,      0.20,'train pulls into Alexandria'),
 ('6175',62,71,      0.50,'platform, light rays'),
 ('6098',71,79,      0.30,'station square'),
 ('6099',79,85,      0.20,'black-and-yellow taxis'),
 ('6131',85,90,      0.30,'taxi and motorbike'),
 ('6101',90,96,      0.50,'alley, calm before the hit'),
 # REVEAL + TITLE
 ('6103',96,104,     0.00,'HIT: sea reveal, TITLE'),
 ('6134',104,108,    0.50,'lamp post and taxi'),
 ('6128',108,112,    0.00,'palace with flags'),
 # MUSEUM (song splice hidden inside 6112)
 ('6110',112,120,    0.30,'Royal Jewelry Museum facade'),
 ('6112',120,129,    0.50,'red carpet staircase (hides splice)'),
 ('6113',129,133,    0.30,'stained glass, portrait'),
 ('6116',133,137,    0.50,'gallery corridor'),
 ('6119',137,143,    0.50,'glowing doorway, musical breath'),
 # NIGHT - section hit
 ('6135',143,147,    0.30,'HIT: night facade'),
 ('6140',147,151,    0.50,'crowds'),
 ('6143',151,155,    1.00,'lit buildings'),
 ('6136',155,159,    0.50,'light beams, crowd'),
 ('6141',159,167,    0.50,'long night street'),
 # MORNING - accent
 ('6152',167,171,    0.30,'ACCENT: next morning, sea from above'),
 ('6160',171,176,    2.00,'Stanley tower reveal'),
 ('6167',176,182,    2.00,'Stanley tower'),
 # PEAK
 ('6170',182,186,    0.50,'bridge towers'),
 ('6163',186,193,    0.40,'bridge tower'),
 ('6168',193,199,    1.00,'cars stream past the sea railing'),
 ('6153',199,206,    0.20,'Corniche from above'),
 # OUTRO
 ('6164',206,214,    0.30,'turquoise bay, calm'),
 ('6179',214,221,    0.35,'golden locomotive'),
 ('6162',221,None,   0.35,'the sea - END CARD'),
]
DISSOLVE={2:0.5, 3:0.5, 35:0.7, 36:0.7}  # index of incoming shot -> duration
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
