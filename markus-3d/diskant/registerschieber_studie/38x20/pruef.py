exec(open("neu.py").read())
import numpy as np, json
from shapely.affinity import translate
kan=json.load(open("kan.json"))
def mus(v,k): return "".join(c if v[k[c]]>0.9 else "-" if v[k[c]]<0.1 else "?" for c in "LMR")
res={}; frei=0
for a in np.arange(-14,1.01,0.25):
    Aa=translate(A3,a)
    for b in np.arange(a-31,a+1.01,0.25):
        Bb=translate(B3,b)
        if Aa.intersection(Bb).area>1e-6: continue
        frei+=1
        U=unary_union([Aa,Bb]); v=[1-p.intersection(U).area/p.area for p in L]
        p=[mus(v,k) for k in kan]
        if len(set(p))==1 and "?" not in p[0]: res.setdefault(p[0],[]).append((round(a,2),round(b,2)))
print("zulaessige Stellungen",frei)
RAST={"LMR":(-1,-11),"L-R":(-1,-1),"LM-":(-1,-21),"-MR":(-2,-31),"L--":(-11,-21),"--R":(-11,-31)}
for m,l in sorted(res.items()):
    aa=[x for x,_ in l]; bb=[y for _,y in l]
    print(f"  {m}: A {min(aa):+.2f}..{max(aa):+.2f}  B {min(bb):+.2f}..{max(bb):+.2f}  Rast {RAST[m]} drin: {RAST[m] in l}")
for m,(a,b) in RAST.items():
    ua=(xa1+a)-RAHMEN[1]; ub=RAHMEN[0]-(xb0+b)
    print(f"  {m}: Ueberstand A {ua:.1f} mm, B {ub:.1f} mm")
for a,b in [(-1,-1),(-1,-1.5),(-1,-2),(-0.5,-1.5),(-11,-11),(-11,-12)]:
    Aa=translate(A3,a);Bb=translate(B3,b);U=unary_union([Aa,Bb]); v=[1-p.intersection(U).area/p.area for p in L]
    print((a,b),round(Aa.intersection(Bb).area,3),[mus(v,k) for k in kan])
