from geo2 import *
from shapely.affinity import translate
import numpy as np
REGR={"LMR":(RA[0],RB[0]),"LM-":(RA[0],RB[1]),"-MR":(RA[0],RB[2]),"L-R":(RA[1],RB[0]),"L--":(RA[1],RB[1]),"--R":(RA[1],RB[2])}
def zust(A,B,H,a,b):
    Aa=translate(A,a);Bb=translate(B,b)
    if Aa.intersection(Bb).area>1e-6: return None
    U=unary_union([Aa,Bb]); return [h.intersection(U).area/h.area for _,_,h in H]
def ok(z,H,m): return z is not None and all((v<=0.001) if c in m else (v>=0.999) for v,(_,c,_) in zip(z,H))
for k,s in enumerate(STOCK):
    A,B=schieber_links(s); H=loecher(s); erg=[]
    for m,(a,b) in REGR.items():
        z=zust(A,B,H,a,b); sp=[]
        for da,db in ((1,0),(-1,0),(0,1),(0,-1)):
            d=0
            while d<2 and ok(zust(A,B,H,a+da*(d+0.1),b+db*(d+0.1)),H,m): d+=0.1
            sp.append(d)
        erg.append(f"{m}:{'ok' if ok(z,H,m) else 'FEHLER'}(A+{sp[0]:.1f}/-{sp[1]:.1f} B+{sp[2]:.1f}/-{sp[3]:.1f})")
    # Wege zwischen den Rasten
    koll=[ (a,round(b,1)) for a in RA for b in np.arange(min(RB),max(RB)+0.01,0.1) if zust(A,B,H,a,b) is None]
    koll+=[(round(a,1),b) for b in RB for a in np.arange(min(RA),max(RA)+0.01,0.1) if zust(A,B,H,a,b) is None]
    print(f"Stimmstock {4-k}:", " ".join(erg), " Kollisionen auf den Wegen:",koll[:3])
