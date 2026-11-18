import numpy as np, json, sys
S=sys.argv[1]
X=np.load(S+'/short/X.npy'); bt=np.array(json.load(open(S+'/audio/beats.json'))['beats'])
def sim(i,j,W):
    a=X[:,i-W:i+W]; b=X[:,j-W:j+W]
    return float(((a*b).sum(0)/(np.linalg.norm(a,axis=0)*np.linalg.norm(b,axis=0))).mean())
def pre_sim(i,j,W=4):  # how well the material before the out-point predicts what follows the in-point
    a=X[:,i-W:i]; b=X[:,j-W:j]
    return float(((a*b).sum(0)/(np.linalg.norm(a,axis=0)*np.linalg.norm(b,axis=0))).mean())
pre=32.693
for i in (104,108,112,116,120,128):
    for j in (543,547,551,558,562,566):
        tot=pre+(bt[i]-48.994)+(311.2-bt[j])
        if 58<tot<77: print(f"out b{i} {bt[i]:.2f} -> in b{j} {bt[j]:.2f}  sim4 {sim(i,j,4):.3f} sim8 {sim(i,j,8):.3f} pre {pre_sim(i,j):.3f}  total {tot:.1f}")
