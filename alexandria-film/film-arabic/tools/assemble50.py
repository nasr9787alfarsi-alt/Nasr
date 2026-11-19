import json, subprocess, sys
S=sys.argv[1]
shots=json.load(open(f'{S}/shots_sdr/shots.json'))
END=49.4; NF=round(END*30)
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
ti=len(shots)
inputs+=['-i',f'{S}/audio/mix_final.wav','-loop','1','-framerate','30','-t',str(END),'-i',f'{S}/ttl/title_ar.png']
fc.append(f'{acc}tpad=stop_mode=add:stop_duration={END:.2f}:color=black,trim=end_frame={NF},format=yuv444p10le[base]')
fend=shots[-1]['t1']
fc.append(f'[base]fade=t=in:st=0:d=0.25,fade=t=out:st={fend-2.0:.3f}:d=2.0[pic];[{ti+1}:v]format=yuva444p10le[ar];[pic][ar]overlay=format=yuv444p10:shortest=0,format=yuv422p10le[v]')  # title sits above the fades: visible on every frame
open(f'{S}/fc.txt','w').write(';\n'.join(fc))
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex_script',f'{S}/fc.txt','-map','[v]','-map',f'{ti}:a','-t',f'{END}',
  '-c:v','prores_ks','-profile:v','3','-vendor','apl0','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:a','pcm_s24le',f'{S}/master_sdr.mov'],check=True)
