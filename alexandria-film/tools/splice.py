import librosa, numpy as np, sys, json
S=sys.argv[1]
y,sr=librosa.load(S+'/audio/song.wav',sr=22050)
tempo,bf=librosa.beat.beat_track(y=y,sr=sr,tightness=400)
bt=librosa.frames_to_time(bf,sr=sr)
print('tempo',tempo, 'median IBI',np.median(np.diff(bt)))
ch=librosa.feature.chroma_cqt(y=y,sr=sr); mf=librosa.feature.mfcc(y=y,sr=sr,n_mfcc=20)
onset=librosa.onset.onset_strength(y=y,sr=sr)
X=np.vstack([librosa.util.normalize(librosa.util.sync(ch,bf),axis=0),0.5*librosa.util.normalize(librosa.util.sync(mf[1:],bf),axis=0)])
# downbeat phase: which beat mod 4 has strongest onset+low-freq energy
low=librosa.feature.rms(y=librosa.effects.hpss(y)[1])[0]
ob=np.array([onset[f] for f in bf])
for p in range(4): print('phase',p,ob[p::4].mean())
# print beats near key boundaries
for tt in [14,49,105.9,144,172.8,211.8,264]:
    k=np.argmin(abs(bt-tt)); print(tt,'-> beat',k,round(bt[k],3),'k%4=',k%4)
W=8
def sim(i,j):
    a=X[:,i-W:i+W]; b=X[:,j-W:j+W]
    return float((a*b).sum(0).mean()/ (np.linalg.norm(a,axis=0)*np.linalg.norm(b,axis=0)).mean())
res=[]
I=[k for k in range(len(bt)) if 125<bt[k]<215]
J=[k for k in range(len(bt)) if 215<bt[k]<290 and bt[k]-0>0]
for i in I:
    for j in J:
        if (i-j)%4: continue
        res.append((sim(i,j),i,j))
res.sort(reverse=True)
for s,i,j in res[:15]:
    print(f"sim {s:.3f}  cut out at {bt[i]:.3f} (beat {i}) -> in at {bt[j]:.3f} (beat {j})  total {bt[i]+ (311.5-bt[j]):.1f}s")
json.dump({'bt':bt.tolist()},open(S+'/audio/bt.json','w'))
