import librosa, numpy as np, json, sys
S=sys.argv[1]
y,sr=librosa.load(S+'/audio/song.wav',sr=22050,mono=True)
tempo,beats=librosa.beat.beat_track(y=y,sr=sr,units='time')
print('tempo',tempo,'nbeats',len(beats))
onset_env=librosa.onset.onset_strength(y=y,sr=sr)
# RMS per second
hop=512
rms=librosa.feature.rms(y=y,hop_length=hop)[0]; t=librosa.frames_to_time(np.arange(len(rms)),sr=sr,hop_length=hop)
for s in range(0,int(t[-1]),2):
    m=(t>=s)&(t<s+2); v=rms[m].mean()
    print(f"{s:4d}s {v:.3f} "+'#'*int(v*150))
# segment boundaries
chroma=librosa.feature.chroma_cqt(y=y,sr=sr)
mfcc=librosa.feature.mfcc(y=y,sr=sr,n_mfcc=13)
feat=np.vstack([librosa.util.normalize(chroma,axis=1),librosa.util.normalize(mfcc,axis=1)])
bounds=librosa.segment.agglomerative(feat,14)
print('segments',[round(float(x),1) for x in librosa.frames_to_time(bounds,sr=sr)])
json.dump({'tempo':float(np.atleast_1d(tempo)[0]),'beats':[float(b) for b in beats]},open(S+'/audio/beats.json','w'))
