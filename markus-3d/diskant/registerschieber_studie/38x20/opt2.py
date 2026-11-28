exec(open("neu.py").read())
import json, numpy as np
from shapely.affinity import translate
from shapely.prepared import prep
kan=json.load(open("kan.json"))
ZIEL={"LMR":"LMR","L-R":"L-R","LM-":"LM-","-MR":"-MR","L--":"L--","--R":"--R"}
Q={m:{} for m in ZIEL}
for a in np.round(np.arange(-14,1.01,0.2),2):
    Aa=translate(A3,a)
    for b in np.round(np.arange(a-31,a+0.01,0.2),2):
        Bb=translate(B3,b)
        if Aa.intersection(Bb).area>1e-6: continue
        U=unary_union([Aa,Bb]); v=[1-q.intersection(U).area/q.area for q in L]
        for m in ZIEL:
            Q[m][(a,b)]=min((v[k[c]] if c in m else 1-v[k[c]]) for k in kan for c in "LMR")
json.dump({m:{f"{k[0]},{k[1]}":x for k,x in d.items()} for m,d in Q.items()},open("q.json","w"))
for m,d in Q.items():
    best=max(d.values()); gut=[k for k,x in d.items() if x>=0.999]
    if gut:
        aa=[k[0] for k in gut]; bb=[k[1] for k in gut]
        print(f"{m}: voll sauber bei A {min(aa)}..{max(aa)}, B {min(bb)}..{max(bb)} ({len(gut)} Punkte)")
    else:
        k=max(d,key=d.get); print(f"{m}: bestes {best:.3f} bei {k}")
