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
 ('6172',51,55,      0.10,'headlights in the station'),
 ('6176',55,66,      0.20,'train pulls in'),
 ('6175',66,75,      0.50,'platform, light rays'),
 ('6180',75,81,      0.20,'station exterior, flags'),
 ('6098',81,90,      0.00,'station square'),
 ('6099',90,96,      0.20,'black-and-yellow taxis'),
 # REVEAL + TITLE
 ('6103',96,104,     0.00,'HIT: sea reveal, TITLE'),
 ('6102',104,112,    0.05,'bay from above'),
 # STREETS
 ('6100',112,116,    0.30,'tall street'),
 ('6101',116,120,    0.50,'alley, red awnings'),
 ('6131',120,124,    0.60,'taxi and motorbike'),
 ('6134',124,128,    0.50,'lamp post and taxi'),
 ('6133',128,132,    0.20,'carved old wall'),
 ('6107',132,135,    0.05,'walking together'),
 ('6128',135,143,    0.00,'palace with flags'),
 # MUSEUM
 ('6110',143,151,    0.30,'ACCENT: palace facade'),
 ('6109',151,154,    0.20,'bronze statue'),
 ('6112',154,163,    0.50,'red carpet staircase'),
 ('6113',163,171,    0.30,'stained glass, portrait'),
 ('6116',171,179,    0.40,'gallery corridor'),
 ('6115',179,183,    0.80,'bronze bust'),
 ('6117',183,191,    1.30,'chandelier reveal'),
 ('6120',191,195,    0.40,'painted panels'),
 ('6119',195,204,    0.00,'glowing doorway'),
 ('6150',204,207,    0.50,'harbour lights at night (dissolve)'),
 # NIGHT
 ('6135',207,211,    0.30,'HIT: night facade'),
 ('6140',211,215,    0.50,'crowds'),
 ('6143',215,219,    1.00,'lit buildings'),
 ('6136',219,223,    0.50,'light beams, crowd'),
 ('6141',223,231,    0.50,'long night street (hides audio splice)'),
 ('6142',231,235,    0.50,'monument at night'),
 # DAY 2 - CORNICHE
 ('6152',235,239,    0.30,'next morning: sea from above'),
 ('6154',239,241,    0.30,'drive'),
 ('6155',241,243,    0.20,'drive, red car'),
 ('6157',243,245,    0.50,'drive'),
 ('6160',245,250,    2.00,'Stanley tower reveal'),
 # PEAK
 ('6167',250,254,    2.60,'Stanley tower'),
 ('6170',254,258,    0.50,'bridge towers'),
 ('6164',258,264,    0.30,'turquoise bay'),
 ('6163',264,270,    0.40,'bridge tower'),
 # OUTRO
 ('6165',270,278,    0.00,'bay, wide'),
 ('6179',278,285,    0.35,'golden locomotive'),
 ('6162',285,None,   0.35,'the sea - END CARD'),
]
DISSOLVE={1:0.0, 2:0.5, 3:0.5, 32:1.0, 39:0.6, 49:0.7, 50:0.7}  # index of incoming shot -> duration
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
