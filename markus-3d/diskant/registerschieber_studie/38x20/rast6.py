exec(open("neu6.py").read()); A3,B3=A6,B6
import json
from shapely.affinity import translate
kan=json.load(open("kan.json"))
def q(a,b,m):
    Aa=translate(A3,a);Bb=translate(B3,b)
    if Aa.intersection(Bb).area>1e-6: return -1
    U=unary_union([Aa,Bb]); v=[1-h.intersection(U).area/h.area for h in L]
    return min((v[k[c]] if c in m else 1-v[k[c]]) for k in kan for c in "LMR")
def spiel(a,b,m,richt):
    d=0
    while d<3 and q(a+richt[0]*(d+0.05),b+richt[1]*(d+0.05),m)>=0.999: d+=0.05
    return d
AR={"M offen":-1.3,"M zu":-11.1}
REG={("M offen",-1.5):"L-R",("M offen",-11.4):"LMR",("M offen",-21):"LM-",("M offen",-31):"-MR",
     ("M zu",-11.4):"L-R",("M zu",-21):"L--",("M zu",-31):"--R"}
for (an,b),m in REG.items():
    a=AR[an]
    print(f"A {a:+.1f} B {b:+.1f} -> {m}: Guete {q(a,b,m):.3f}  Spiel A +{spiel(a,b,m,(1,0)):.2f}/-{spiel(a,b,m,(-1,0)):.2f}  B +{spiel(a,b,m,(0,1)):.2f}/-{spiel(a,b,m,(0,-1)):.2f}")
