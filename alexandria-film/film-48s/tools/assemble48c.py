import json, subprocess, sys
S=sys.argv[1]
shots=json.load(open(f'{S}/shots_sdr/shots.json'))
END=47.9; NF=round(END*30)
inputs=[]; fc=[]
for s in shots: inputs+=['-i',s['file']]
acc=None; acc_frames=0; pending=[]
def flush():
    global acc
    if len(pending)>1:
        fc.append(''.join(pending)+f'concat=n={len(pending)}:v=1:a=0,settb=1/30,setpts=N[g{len(fc)}]'); acc=f'[g{len(fc)-1}]'
    elif pending: acc=pending[0]
for k,s in enumerate(shots):
    fc.append(f'[{k}:v]settb=1/30,setpts=N,format=yuv422p10le[s{k}]'); lab=f'[s{k}]'
    if s.get('hin_f',0)>0:
        flush(); pending.clear(); d=s['hin_f']*2; off=(acc_frames-d)/30
        fc.append(f'{acc}{lab}xfade=transition=fade:duration={d/30:.4f}:offset={off:.4f}[x{k}]')
        acc=f'[x{k}]'; pending.append(acc); acc_frames+=s['n']-d
    else:
        if not pending and acc: pending.append(acc)
        pending.append(lab); acc_frames+=s['n']
flush()
print('timeline frames',acc_frames)
I=[s['clip'] for s in shots].index('6170'); T1=shots[I]['f0']+6
T2=shots[-1]['f0']+30
ti=len(shots)
inputs+=['-framerate','30','-i',f'{S}/ttl/open/%04d.png','-framerate','30','-i',f'{S}/ttl/end/%04d.png','-i',f'{S}/audio/mix_final.wav','-loop','1','-framerate','30','-t',str(END),'-i',f'{S}/ttl/subtitle.png']
fc.append(f'[{ti}:v]format=yuva444p10le,setpts=PTS+{T1}/30/TB[t1];[{ti+1}:v]format=yuva444p10le,setpts=PTS+{T2}/30/TB[t2]')
fc.append(f'{acc}tpad=stop_mode=add:stop_duration={END:.2f}:color=black,trim=end_frame={NF},format=yuv444p10le[base]')
fc.append(f'[base][t1]overlay=eof_action=pass:format=yuv444p10[o1];[o1][t2]overlay=eof_action=pass:format=yuv444p10[o2a];[{ti+3}:v]format=yuva444p10le,fade=t=in:st=0.35:d=0.9:alpha=1[st];[o2a][st]overlay=eof_action=pass:format=yuv444p10[o2]')
fend=shots[-1]['t1']
fc.append(f'[o2]fade=t=in:st=0:d=0.25,fade=t=out:st={fend-1.2:.3f}:d=1.2,format=yuv422p10le[v]')
open(f'{S}/fc.txt','w').write(';\n'.join(fc))
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex_script',f'{S}/fc.txt','-map','[v]','-map',f'{ti+2}:a','-t',f'{END}',
  '-c:v','prores_ks','-profile:v','3','-vendor','apl0','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:a','pcm_s24le',f'{S}/master_sdr.mov'],check=True)
