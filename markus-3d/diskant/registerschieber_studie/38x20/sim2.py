import ezdxf, json, numpy as np
from shapely.geometry import Polygon, box
from shapely.affinity import translate
from shapely.ops import unary_union
exec(open("sim.py").read().split("MAXX")[0])
kan=json.load(open("kan.json"))
# Variante: Zahnteilung am rechten Ende fortsetzen
A2=unary_union([A.difference(box(-1286.2,-850,-1200,-810)),
   box(-1286.2,-819.18,-1252.83,-817.68), box(-1286.2,-845.08,-1252.83,-842.58),
   box(-1260.88,-845.08,-1252.83,-817.68), box(-1286.13,-829.28,-1275.83,-819.0)])
B2=unary_union([B, box(-1286.2,-831.95,-1260.88,-829.28), box(-1271.18,-841.98,-1260.88,-831.9)])
print("A2",A2.geom_type,round(A2.area,1),"B2",B2.geom_type,"Ueberlappung",round(A2.intersection(B2).area,3), "A2 x",[round(v,2) for v in A2.bounds], "B2 x",[round(v,2) for v in B2.bounds])
def mus(v,k): return "".join(c if v[k[c]]>0.9 else "-" if v[k[c]]<0.1 else "?" for c in "LMR")
import sys
VAR={"orig":(A,B),"neu":(A2,B2)}
for name,(PA,PB) in VAR.items():
    st=0.25; res={}
    for a in np.arange(-14,1.01,st):
        Aa=translate(PA,a)
        for b in np.arange(a-31,a+1.01,st):
            Bb=translate(PB,b)
            if Aa.intersection(Bb).area>1e-6: continue
            U=unary_union([Aa,Bb]); v=[1-p.intersection(U).area/p.area for p in L]
            p=[mus(v,k) for k in kan]
            if len(set(p))==1 and "?" not in p[0]: res.setdefault(p[0],[]).append((round(a,2),round(b,2)))
    print("\n==",name)
    for m,l in sorted(res.items()):
        aa=[x for x,_ in l]; bb=[y for _,y in l]
        print(f"  {m}: A {min(aa):+.2f}..{max(aa):+.2f}  B {min(bb):+.2f}..{max(bb):+.2f}  ({len(l)} Punkte)")
