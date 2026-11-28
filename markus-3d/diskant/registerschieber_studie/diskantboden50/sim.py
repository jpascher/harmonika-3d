from geo import *
from shapely.affinity import translate
from shapely.prepared import prep
import numpy as np, sys, pickle
REG=["LMR","LM-","-MR","L-R","L--","--R"]
bruecke=sys.argv[1] if len(sys.argv)>1 else "links"
ok={m:None for m in REG}; koll=set()
for k,s in enumerate(STOCK):
    A,B=schieber(s,bruecke); H=loecher(s)
    pts={m:set() for m in REG}
    for a in np.round(np.arange(-13,1.01,0.25),2):
        Aa=translate(A,a)
        HA=[h.intersection(Aa) for _,_,h in H]
        for b in np.round(np.arange(-33,-7.99,0.25),2):
            Bb=translate(B,b)
            if Aa.intersection(Bb).area>1e-6: koll.add((a,b)); continue
            zu=[ (ha.union(h.intersection(Bb))).area/h.area for ha,(_,_,h) in zip(HA,H)]
            for m in REG:
                if all((z<=0.001) if c in m else (z>=0.999) for z,(_,c,_) in zip(zu,H)): pts[m].add((a,b))
    for m in REG: ok[m]=pts[m] if ok[m] is None else ok[m]&pts[m]
    print("Stimmstock",4-k,"fertig",flush=True)
for m in REG:
    p=ok[m]
    if not p: print(m,"KEINE gemeinsame Stellung"); continue
    aa=[x for x,_ in p]; bb=[y for _,y in p]
    print(f"{m}: A {min(aa)}..{max(aa)}  B {min(bb)}..{max(bb)}  ({len(p)})")
pickle.dump((ok,koll),open(f"ok_{bruecke}.pkl","wb"))
