import json, subprocess, sys, os
S=sys.argv[1]; MODE=sys.argv[2]
shots=json.load(open(f'{S}/shots_{MODE}/shots.json'))
END=39.8; NF=round(END*30)
inputs=[]; fc=[]
for s in shots: inputs+=['-i',s['file']]
# chain: hard cuts via concat, dissolves via xfade
acc=None; acc_frames=0; pending=[]
def flush():
    global acc
    if len(pending)>1:
        fc.append(''.join(pending)+f'concat=n={len(pending)}:v=1:a=0,settb=1/30,setpts=N[g{len(fc)}]'); acc=f'[g{len(fc)-1}]'
    elif pending: acc=pending[0]
for k,s in enumerate(shots):
    lab=f'[{k}:v]'
    fc.append(f'{lab}settb=1/30,setpts=N,format=yuv422p10le[s{k}]'); lab=f'[s{k}]'
    if s.get('hin_f',0)>0:
        flush(); pending.clear()
        d=s['hin_f']*2; off=(acc_frames-d)/30
        fc.append(f'{acc}{lab}xfade=transition=fade:duration={d/30:.4f}:offset={off:.4f}[x{k}]')
        acc=f'[x{k}]'; pending.append(acc); acc_frames+=s['n']-d
    else:
        if not pending and acc: pending.append(acc)
        pending.append(lab); acc_frames+=s['n']
flush()
print('timeline frames',acc_frames,'expected',round(shots[-1]['t1']*30)+shots[-1].get('hout_f',0))
last=acc
# titles
I3=[s['clip'] for s in shots].index('6103'); T0=round(shots[I3+1]['t0']*30)-114   # title ends 2 frames before the cut
E0=round((shots[-1]['t0']+1.4)*30)
ti=len(shots); inputs+=['-framerate','30','-i',f'{S}/ttl/{MODE}_title/%04d.png','-framerate','30','-i',f'{S}/ttl/{MODE}_end/%04d.png','-i',f'{S}/audio/mix_final.wav']
fc.append(f'[{ti}:v]format=yuva444p10le,setpts=PTS+{T0}/30/TB[t1];[{ti+1}:v]format=yuva444p10le,setpts=PTS+{E0}/30/TB[t2]')
fc.append(f'{last}tpad=stop_mode=add:stop_duration={END:.2f}:color=black,trim=end_frame={NF},format=yuv444p10le[base]')
fc.append(f'[base][t1]overlay=eof_action=pass:format=yuv444p10[o1];[o1][t2]overlay=eof_action=pass:format=yuv444p10[o2]')
fend=shots[-1]['t1']
fc.append(f'[o2]fade=t=in:st=0:d=0.6,fade=t=out:st={fend-1.15:.3f}:d=1.15,format=yuv422p10le[v]')
tags=(['-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709'] if MODE=='sdr' else
      ['-color_primaries','bt2020','-color_trc','arib-std-b67','-colorspace','bt2020nc'])
open(f'{S}/fc_{MODE}.txt','w').write(';\n'.join(fc))
cmd=['ffmpeg','-v','error','-stats','-y',*inputs,'-filter_complex_script',f'{S}/fc_{MODE}.txt','-map','[v]','-map',f'{ti+2}:a',
     '-t',f'{END}','-c:v','prores_ks','-profile:v','3','-vendor','apl0',*tags,'-c:a','pcm_s24le',f'{S}/master_{MODE}.mov']
subprocess.run(cmd,check=True)
