import subprocess, json, os, sys, re
sys.path.insert(0, os.path.dirname(__file__)); import edl
S=edl.S; A=f'{S}/audio'
START=json.load(open(f'{A}/splices.json'))['start']; END=49.4
def lufs(path, af=''):
    o=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',path,'-vn','-af',(af+',' if af else '')+'ebur128','-f','null','-'],capture_output=True,text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS',o)[-1])
# one continuous section of the song, from the section hit to its natural end - no splice
CUES=[('6178',1.80,0.0,2.08,-30,0.0,0.6),('6162',0.0,39.977,6.30,-27,1.5,2.3)]
HP='highpass=f=180:poles=2,highpass=f=180:poles=2,lowpass=f=12000'
inputs=['-i',f'{A}/song.wav']; fc=[f"[0:a]atrim={START:.4f},asetpts=N/SR/TB,afade=t=in:d=0.008[mus]"]; mix=['[mus]']
for k,(c,si,fs,d,tgt,fi,fo) in enumerate(CUES):
    src=f'{S}/src/vid/IMG_{c}.MOV'; g=tgt-lufs(src,HP); j=k+1; inputs+=['-i',src]
    fc.append(f"[{j}:a]atrim={si}:{si+d},asetpts=N/SR/TB,aresample=48000,{HP},volume={g:.2f}dB,afade=t=in:d={fi},afade=t=out:st={d-fo:.3f}:d={fo},adelay={int(fs*1000)}:all=1[c{j}]")
    mix.append(f'[c{j}]')
fc.append(''.join(mix)+f"amix=inputs={len(mix)}:normalize=0:duration=first,apad=whole_dur={END},atrim=0:{END},afade=t=out:st=45.9:d={END-45.9}:curve=qsin[out]")
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',';'.join(fc),'-map','[out]','-ar','48000','-c:a','pcm_s24le',f'{A}/mix_raw.wav'],check=True)
o=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',f'{A}/mix_raw.wav','-af','loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
m=json.loads(o[o.rindex('{'):o.rindex('}')+1])
af=(f"loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
    f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(['ffmpeg','-v','error','-y','-i',f'{A}/mix_raw.wav','-af',af+',aresample=48000','-c:a','pcm_s24le',f'{A}/mix_final.wav'],check=True)
print('final',lufs(f'{A}/mix_final.wav'))
