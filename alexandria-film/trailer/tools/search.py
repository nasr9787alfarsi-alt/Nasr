import librosa, numpy as np, json, sys
S=sys.argv[1]
y,sr=librosa.load(S+'/audio/song.wav',sr=22050)
bt=np.array(json.load(open(S+'/audio/beats.json'))['beats'])
bf=librosa.time_to_frames(bt,sr=sr)
ch=librosa.feature.chroma_cqt(y=y,sr=sr); mf=librosa.feature.mfcc(y=y,sr=sr,n_mfcc=20)
X=np.vstack([librosa.util.normalize(librosa.util.sync(ch,bf),axis=0),0.5*librosa.util.normalize(librosa.util.sync(mf[1:],bf),axis=0)])
rms=librosa.util.sync(librosa.feature.rms(y=y),bf)[0]
np.save(S+'/short/X.npy',X)
def nb(t): return int(np.argmin(abs(bt-t)))
keys={'drop':13.375,'hit':48.994,'hit2':240.3,'sec':264.15,'acc':276.36,'peak':284.0,'out':296.22,'end':308.66}
K={k:nb(v) for k,v in keys.items()}; print({k:(v,round(bt[v],3)) for k,v in K.items()})
W=6
def sim(i,j):
    a=X[:,i-W:i+W]; b=X[:,j-W:j+W]
    return float(((a*b).sum(0)/(np.linalg.norm(a,axis=0)*np.linalg.norm(b,axis=0))).mean())
def top(I,J,n=8,label=''):
    r=sorted([(sim(i,j),i,j) for i in I for j in J if j-i>=8 and (j-i)%4==0],reverse=True)[:n]
    print('==',label)
    for s,i,j in r: print(f"  {s:.3f} out {bt[i]:.3f} (b{i}) -> in {bt[j]:.3f} (b{j})  skip {bt[j]-bt[i]:.1f}s  rms {rms[i-1]:.3f}/{rms[j-1]:.3f}")
# verse shortening: out after drop+8 beats, in at least 8 beats before hit
top(range(K['drop']+8,K['hit']-12),range(K['drop']+16,K['hit']-7),label='verse')
# chorus2 -> later sections
top(range(K['hit2']+8,K['sec']),range(K['sec'],K['out']),label='after hit2')
top(range(K['hit']+8,nb(65)),range(K['sec'],K['out']),label='chorus1 -> later')
