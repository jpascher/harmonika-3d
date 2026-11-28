exec(open("neu.py").read())
import json
from shapely.affinity import translate
kan=json.load(open("kan.json"))
def detail(a,b,ziel):
    Aa=translate(A3,a);Bb=translate(B3,b); U=unary_union([Aa,Bb])
    for ti,k in enumerate(kan):
        for c in "LMR":
            q=L[k[c]]; v=1-q.intersection(U).area/q.area; soll=c in ziel
            if (soll and v<0.999) or (not soll and v>0.001):
                # wer deckt? Lage der Deckung
                ia=q.intersection(Aa).area/q.area; ib=q.intersection(Bb).area/q.area
                print(f"  T{ti+1} {c} {'oben' if q.centroid.y>-831 else 'unten'} x {q.bounds[0]:.2f}: offen {v:.3f} (A {ia:.3f} B {ib:.3f})")
for z,(a,b) in {"LM-":(-2,-22),"-MR":(-2,-31.8),"L--":(-12.4,-22)}.items():
    print(z,a,b); detail(a,b,z)
