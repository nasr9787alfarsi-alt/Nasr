import numpy as np, json, sys
S=sys.argv[1]
X=np.load(S+'/short/X.npy'); bt=np.array(json.load(open(S+'/audio/beats.json'))['beats'])
A=[l.split() for l in open(S+'/audio/beatmap.txt')]
def sim(i,j,W):
    a=X[:,i-W:i+W]; b=X[:,j-W:j+W]
    return float(((a*b).sum(0)/(np.linalg.norm(a,axis=0)*np.linalg.norm(b,axis=0))).mean())
pre=13.375+(26.099-13.375)+(48.994-42.400)   # film time of chorus hit after verse cut b51->b83
print('hit at film',round(pre,3))
END=311.2
r=[]
for i in range(100,129):
    for j in range(536,590):
        if (j-i)%4: continue
        tot=pre+(bt[i]-48.994)+(END-bt[j])
        if 60<=tot<=75: r.append((round(sim(i,j,4),3),round(sim(i,j,8),3),i,j,round(bt[i],2),round(bt[j],2),round(tot,1)))
r.sort(reverse=True)
for x in r[:20]: print(x)
