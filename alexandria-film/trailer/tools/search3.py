import numpy as np, json, sys, librosa
S=sys.argv[1]
X=np.load(S+'/short/X.npy'); bt=np.array(json.load(open(S+'/audio/beats.json'))['beats'])
def sim(i,j,W=4):
    a=X[:,i-W:i+W]; b=X[:,j-W:j+W]
    return float(((a*b).sum(0)/(np.linalg.norm(a,axis=0)*np.linalg.norm(b,axis=0))).mean())
rng=np.random.default_rng(0)
base=[sim(i,j) for i,j in zip(rng.integers(20,580,3000),rng.integers(20,580,3000)) if abs(i-j)>16 and (i-j)%4==0]
print('random bar-aligned pairs: median %.3f  p90 %.3f  p99 %.3f'%(np.median(base),np.percentile(base,90),np.percentile(base,99)))
# key profile per section
seg={'verse':(26,96),'chorus':(96,128),'chorus2':(472,519),'sec':(519,543),'acc':(543,558),'peak':(558,582),'outro':(582,606)}
C=X[:12]
for k,(a,b) in seg.items():
    v=C[:,a:b].mean(1); print(k, ' '.join('%.2f'%x for x in v/np.linalg.norm(v)), 'top', np.argsort(v)[-3:][::-1])
