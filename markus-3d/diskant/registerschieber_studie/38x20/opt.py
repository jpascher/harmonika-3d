exec(open("neu.py").read())
import json, numpy as np
from shapely.affinity import translate
kan=json.load(open("kan.json"))
def zust(a,b,o,z):
    Aa=translate(A3,a);Bb=translate(B3,b)
    if Aa.intersection(Bb).area>1e-6: return None
    U=unary_union([Aa,Bb]); v=[1-q.intersection(U).area/q.area for q in L]
    s={"".join(c if v[k[c]]>o else "-" if v[k[c]]<z else "?" for c in "LMR") for k in kan}
    return s.pop() if len(s)==1 else None
# A allein bestimmt M? A-Fenster fuer M offen/zu bei B fest
for name,b in (("LMR",-11),):
    ok=[round(a,1) for a in np.arange(-14,1,0.1) if zust(a,b,0.99,0.01)=="LMR"]
    print("A fuer M offen (B -11):",min(ok),max(ok))
for name,b in (("L-R",-21),):
    pass
ok=[round(a,1) for a in np.arange(-14,-5,0.1) if zust(a,a-10,0.99,0.01)=="L--"]
print("A fuer M zu (B=A-10):",ok[:1],ok[-1:])
for a in (-1.0,-11.0):
    print("A",a)
    for b in np.arange(a-31,a+0.01,0.1):
        z=zust(a,round(b,1),0.99,0.01)
        if z: print("  ",round(b,1),z)
