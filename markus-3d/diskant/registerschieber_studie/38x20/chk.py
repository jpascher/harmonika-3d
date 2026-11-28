exec(open("neu.py").read())
import json
from shapely.affinity import translate
kan=json.load(open("kan.json"))
def mus(v,k): return "".join(c if v[k[c]]>0.99 else "-" if v[k[c]]<0.01 else "?" for c in "LMR")
for a in (-1.5,-11):
    for b in (-2,-11,-21,-30.5):
        if b>a: continue
        Aa=translate(A3,a);Bb=translate(B3,b)
        # Spiel: wie weit beide einzeln verschiebbar ohne Zustandswechsel
        def p(a_,b_):
            Aa_=translate(A3,a_);Bb_=translate(B3,b_)
            if Aa_.intersection(Bb_).area>1e-6: return None
            U=unary_union([Aa_,Bb_]); v=[1-q.intersection(U).area/q.area for q in L]; s={mus(v,k) for k in kan}
            return s.pop() if len(s)==1 else "gemischt"
        z=p(a,b); sp=[]
        for da,db in((1,0),(-1,0),(0,1),(0,-1)):
            d=0
            while d<3 and p(a+da*(d+0.1),b+db*(d+0.1))==z: d+=0.1
            sp.append(round(d,1))
        print(f"A {a:+5.1f} B {b:+5.1f}: {z:4s} Spiel A +{sp[0]}/-{sp[1]}  B +{sp[2]}/-{sp[3]}")
