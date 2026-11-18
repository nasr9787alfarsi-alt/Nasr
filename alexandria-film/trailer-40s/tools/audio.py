import subprocess, json, os, sys, re
sys.path.insert(0, os.path.dirname(__file__)); import edl
S=edl.S; A=f'{S}/audio'
J=json.load(open(f'{A}/splices.json')); T0=J['start']; (a1,b1)=J['cut']; X=0.03; END=39.8
# the intro hush runs into the accent at 276.36 s in place of the band drop; the song then plays to its natural end
def lufs(path, af=''):
    o=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',path,'-vn','-af',(af+',' if af else '')+'ebur128','-f','null','-'],capture_output=True,text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS',o)[-1])
# ambience cues: (clip, src_in, film_start, dur, target_lufs, fade_in, fade_out)
CUES=[('6178',2.50,0.0,1.51,-31,0.3,0.3),('6177',1.70,1.51,2.02,-25,0.4,0.05),('6173',0.0,3.530,1.53,-25,0.0,1.0),('6162',0.0,31.262,6.32,-27,1.8,2.2)]
HP='highpass=f=180:poles=2,highpass=f=180:poles=2,lowpass=f=12000'
inputs=['-i',f'{A}/song.wav']; fc=[]
fc.append(f"[0:a]asplit=2[m1][m2];[m1]atrim={T0}:{a1+X/2:.4f},asetpts=N/SR/TB,afade=t=in:d=0.25[a1];[m2]atrim={b1-X/2:.4f},asetpts=N/SR/TB[a2];[a1][a2]acrossfade=d={X}:c1=qsin:c2=qsin[mus]")
mix=['[mus]']
for k,(c,si,fs,d,tgt,fi,fo) in enumerate(CUES):
    src=f'{S}/src/vid/IMG_{c}.MOV'
    g=tgt-lufs(src,HP)
    inputs+=['-i',src]; j=k+1
    fc.append(f"[{j}:a]atrim={si}:{si+d},asetpts=N/SR/TB,aresample=48000,{HP},volume={g:.2f}dB,afade=t=in:d={fi},afade=t=out:st={d-fo:.3f}:d={fo},adelay={int(fs*1000)}:all=1[c{j}]")
    mix.append(f'[c{j}]')
fc.append(''.join(mix)+f"amix=inputs={len(mix)}:normalize=0:duration=first,apad=whole_dur={END},atrim=0:{END}[out]")
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',';'.join(fc),'-map','[out]','-ar','48000','-c:a','pcm_s24le',f'{A}/mix_raw.wav'],check=True)
# two-pass loudness normalisation to -14 LUFS / -1 dBTP (streaming standard)
o=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',f'{A}/mix_raw.wav','-af','loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
m=json.loads(o[o.rindex('{'):o.rindex('}')+1])
af=(f"loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
    f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(['ffmpeg','-v','error','-y','-i',f'{A}/mix_raw.wav','-af',af+',aresample=48000','-c:a','pcm_s24le',f'{A}/mix_final.wav'],check=True)
print('measured',m['input_i'],m['input_tp'],'-> final',lufs(f'{A}/mix_final.wav'))
