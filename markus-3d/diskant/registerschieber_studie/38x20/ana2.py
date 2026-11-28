import json, collections
d=json.load(open("res.json")); tri=d["tri"]; cx=d["cx"]; cy=d["cy"]
R={tuple(map(float,k.split(","))):v for k,v in d["res"].items()}
st=0.25; start=(0.0,0.0); seen={start}; q=[start]
while q:
    a,b=q.pop()
    for da,db in((st,0),(-st,0),(0,st),(0,-st)):
        n=(round(a+da,2),round(b+db,2))
        if n in R and n not in seen: seen.add(n); q.append(n)
# Chor-Zuordnung: Einzelloch = M; Paar: bei Paar oben links=L,rechts=R; bei Paar unten (um 180 Grad gedreht) links=R, rechts=L
kan=[]
for t in tri:
    ob=sorted([i for i in t if cy[i]>-831],key=lambda i:cx[i]); un=sorted([i for i in t if cy[i]<-831],key=lambda i:cx[i])
    if len(ob)==1: kan.append({"M":ob[0],"L":un[1],"R":un[0]})
    else: kan.append({"M":un[0],"L":ob[0],"R":ob[1]})
def mus(v,k): return "".join(c if v[k[c]]>0.9 else "-" if v[k[c]]<0.1 else "?" for c in "LMR")
def auswert(menge,titel):
    print("\n==",titel,"Stellungen:",len(menge))
    glob=collections.defaultdict(list)
    for k in menge:
        glob[tuple(mus(R[k],kk) for kk in kan)].append(k)
    einheit=collections.defaultdict(list)
    for p,ks in glob.items():
        if len(set(p[:12]))==1 and "?" not in p[0]: einheit[p[0]].append((p[12],ks))
    for m,l in sorted(einheit.items()):
        alle=[k for _,ks in l for k in ks]
        aa=[k[0] for k in alle]; bb=[k[1] for k in alle]
        print(f"  Register {m}: A {min(aa):+.2f}..{max(aa):+.2f}, B {min(bb):+.2f}..{max(bb):+.2f}  ({len(alle)} Rasterpunkte); Tripel 13 dabei:",sorted({x for x,_ in l}))
    return einheit
auswert(seen,"ohne Grenze fuer B (nur Zaehne + A im Rahmen)")
BX=(-20.25,11.2)
auswert({k for k in seen if BX[0]-1e-9<=k[1]<=BX[1]+1e-9},"B ebenfalls im Rahmen Schieber-max")
json.dump(kan,open("kan.json","w"))
