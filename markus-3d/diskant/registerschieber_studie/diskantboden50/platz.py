from geo import *
import pickle,sys
ok,koll=pickle.load(open("ok_links.pkl","rb"))
RA=(-0.5,-11.1); RB=(-10.4,-20.9,-31.1)
REGR={"LMR":(RA[0],RB[0]),"LM-":(RA[0],RB[1]),"-MR":(RA[0],RB[2]),"L-R":(RA[1],RB[0]),"L--":(RA[1],RB[1]),"--R":(RA[1],RB[2])}
def nah(p,S): return any(abs(p[0]-a)<0.13 and abs(p[1]-b)<0.13 for a,b in S)
for m,p in REGR.items(): print(m,p,"in Fenster:",nah(p,ok[m]))
for br in ("links","rechts"):
    print("\nBruecke",br)
    for k,s in enumerate(STOCK):
        A,B=schieber(s,br)
        al=A.bounds[0]+min(RA)-1.0; ar=A.bounds[2]+max(RA)+1.0
        bl=B.bounds[0]+min(RB)-1.0; br_=B.bounds[2]+max(RB)+1.0
        print(f"  St{4-k}: A {al:7.1f}..{ar:7.1f}  B {bl:7.1f}..{br_:7.1f}   Platz links {min(al,bl)-WI:5.1f}  rechts {WA-max(ar,br_):5.1f}")
