import glob, re, numpy as np, os, sys
S=sys.argv[1]; out=[]
for f in sorted(glob.glob(S+'/stab/*.trf')):
    xs=[];ys=[]
    for line in open(f):
        if not line.startswith('Frame'): continue
        fs=re.findall(r'LM (-?\d+) (-?\d+) ',line)
        # local motions: take median shift
        if fs:
            a=np.array(fs,float); xs.append(np.median(a[:,0])); ys.append(np.median(a[:,1]))
        else: xs.append(0); ys.append(0)
    x=np.array(xs); y=np.array(ys)
    if len(x)<10: continue
    k=np.ones(15)/15
    jx=x-np.convolve(x,k,'same'); jy=y-np.convolve(y,k,'same')
    jit=np.sqrt((jx[7:-7]**2+jy[7:-7]**2).mean())
    pan=np.sqrt(x.mean()**2+y.mean()**2)
    out.append((jit,os.path.basename(f)[4:8],pan))
for j,n,p in sorted(out,reverse=True): print(f"{n} jitter={j:5.2f}px@540  pan={p:5.2f}")
