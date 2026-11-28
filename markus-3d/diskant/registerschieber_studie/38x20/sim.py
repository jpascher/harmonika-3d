import ezdxf, numpy as np, json
from shapely.geometry import Polygon, box
from shapely.affinity import translate
from shapely.ops import unary_union
m=ezdxf.readfile("ds.dxf").modelspace(); pl=list(m.query("LWPOLYLINE"))
A=Polygon([(x,y) for x,y,*_ in [e for e in pl if e.dxf.layer=="Schieber2"][0].get_points()])
g=[e for e in pl if e.dxf.layer=="Schieber" and len(e)>12]
B=Polygon([(x,y) for x,y,*_ in g[0].get_points()]+[(x,y) for x,y,*_ in g[1].get_points()][1:])
L=[Polygon([(x,y) for x,y,*_ in e.get_points()]) for e in pl if e.dxf.layer=="0" and len(e)==4]
L.sort(key=lambda p:p.centroid.x)
# Tripel: je 3 Loecher nach x gruppiert
cx=[p.centroid.x for p in L]; tri=[]; cur=[0]
for i in range(1,len(L)):
    if cx[i]-cx[cur[0]]<16: cur.append(i)
    else: tri.append(cur); cur=[i]
tri.append(cur)
MAXX=(-1644.93,-1274.93); ax0,ax1=A.bounds[0],A.bounds[2]
amin,amax=MAXX[0]-ax0, MAXX[1]-ax1
print("Tripel:",len(tri),[len(t) for t in tri]," A-Weg",round(amin,2),round(amax,2))
def zust(a,b):
    U=unary_union([translate(A,a),translate(B,b)])
    return [round(1-p.intersection(U).area/p.area,3) for p in L]
res={}
step=0.25
avals=sorted(set([round(k*step,2) for k in range(int(amin/step)-1,int(amax/step)+2) if amin-1e-9<=k*step<=amax+1e-9]+[round(amin,2),round(amax,2)]))
for a in avals:
    Aa=translate(A,a)
    for b in [round(k*step,2) for k in range(-160,161)]:
        Bb=translate(B,b)
        if Aa.intersection(Bb).area>1e-6: continue
        res[(round(a,2),round(b,2))]=zust(a,b)
json.dump({"tri":tri,"cx":cx,"cy":[p.centroid.y for p in L],"res":{f"{k[0]},{k[1]}":v for k,v in res.items()}},open("res.json","w"))
print("zulaessige Stellungen",len(res))
