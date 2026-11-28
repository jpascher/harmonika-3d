import json, collections
d=json.load(open("res.json")); tri=d["tri"]; cx=d["cx"]; cy=d["cy"]
R={tuple(map(float,k.split(","))):v for k,v in d["res"].items()}
# zusammenhaengend von (0,0) aus
st=0.25; start=(0.0,0.0); assert start in R
seen={start}; q=[start]
while q:
    a,b=q.pop()
    for da,db in((st,0),(-st,0),(0,st),(0,-st)):
        n=(round(a+da,2),round(b+db,2))
        if n in R and n not in seen: seen.add(n); q.append(n)
print("erreichbar",len(seen),"von",len(R))
bs=collections.defaultdict(list)
for a,b in seen: bs[a].append(b)
for a in sorted(bs)[::8]: print(f"A {a:+6.2f}: B {min(bs[a]):+6.2f} .. {max(bs[a]):+6.2f}")
def mus(v):  # je Loch: o offen, z zu, t teilweise
    return "".join("o" if x>0.95 else "z" if x<0.05 else "t" for x in v)
glob=collections.Counter(); bsp={}
for k in seen:
    v=R[k]; pats=[]
    for t in tri:
        ob=sorted([i for i in t if cy[i]>-831],key=lambda i:cx[i]); un=sorted([i for i in t if cy[i]<-831],key=lambda i:cx[i])
        pats.append(mus([v[i] for i in ob])+"/"+mus([v[i] for i in un]))
    glob[tuple(pats)]+=1; bsp.setdefault(tuple(pats),k)
print("verschiedene Gesamtzustaende",len(glob))
sauber=[p for p in glob if all("t" not in x for x in p)]
print("davon ohne Teilabdeckung",len(sauber))
for p in sorted(sauber,key=lambda p:-glob[p]):
    print(bsp[p],glob[p]," ".join(p))

print("\n--- mit Gehaeusegrenze auch fuer Schieber B (Schieber-max) ---")
BX=(-1644.93-(-1624.68), -1274.93-(-1286.13))
print("B-Grenzen aus Rahmen", BX)
ok={k for k in seen if BX[0]-1e-9<=k[1]<=BX[1]+1e-9}
print("Stellungen",len(ok))
import itertools
def guete(v,ziel): return min((v[i] if z else 1-v[i]) for i,z in zip(ziel[0],ziel[1]))
for ti,t in enumerate(tri):
    ob=sorted([i for i in t if cy[i]>-831],key=lambda i:cx[i]); un=sorted([i for i in t if cy[i]<-831],key=lambda i:cx[i])
    reih=ob+un
    zeile=[]
    for z in itertools.product([1,0],repeat=3):
        best=max(ok,key=lambda k:guete(R[k],(reih,z)))
        zeile.append(f"{''.join('o' if x else 'z' for x in z)}:{guete(R[best],(reih,z)):.2f}")
    print(f"T{ti+1:2d} ({len(ob)} oben/{len(un)} unten)", " ".join(zeile))
