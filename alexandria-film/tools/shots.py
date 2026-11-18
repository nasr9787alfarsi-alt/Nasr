import sys, os, subprocess, json
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__)); import edl
S=edl.S; MODE=sys.argv[1]  # sdr | hdr
OUT=f'{S}/shots_{MODE}'; os.makedirs(OUT,exist_ok=True)
TM=("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
    "zscale=t=bt709:m=bt709:r=tv,format=yuv444p10le,eq=contrast=1.03:saturation=1.04")
def job(s):
    f0=round(s['t0']*30); f1=round(s['t1']*30)
    hin=round(s.get('hin',0)*30); hout=round(s.get('hout',0)*30)
    n=f1-f0+hin+hout; ss=s['src']-hin/30
    s.update(f0=f0,f1=f1,hin_f=hin,hout_f=hout,n=n)
    vf=f"fps=30,{TM}" if MODE=='sdr' else "fps=30,format=yuv444p10le"
    vf+=",format=yuv422p10le"
    tags=(['-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709'] if MODE=='sdr' else
          ['-color_primaries','bt2020','-color_trc','arib-std-b67','-colorspace','bt2020nc'])
    out=f"{OUT}/{s['i']:02d}_{s['clip']}.mov"
    cmd=['ffmpeg','-v','error','-y','-ss',f'{max(ss,0):.4f}','-i',f"{S}/src/vid/IMG_{s['clip']}.MOV",'-an','-vf',vf,
         '-frames:v',str(n),'-c:v','prores_ks','-profile:v','3','-vendor','apl0',*tags,out]
    subprocess.run(cmd,check=True)
    got=int(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v','-show_entries','stream=nb_read_frames','-of','csv=p=0',out]))
    s['file']=out; s['got']=got
    return s
shots=edl.build()
with ThreadPoolExecutor(4) as ex: res=list(ex.map(job,shots))
bad=[(r['i'],r['n'],r['got']) for r in res if r['n']!=r['got']]
print('frame mismatches:',bad)
json.dump(res,open(f'{OUT}/shots.json','w'),indent=1)
