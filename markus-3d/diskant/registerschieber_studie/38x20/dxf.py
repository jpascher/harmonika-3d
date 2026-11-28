exec(open("neu.py").read())
import ezdxf
print("Innenringe",len(A3.interiors),len(B3.interiors))
doc=ezdxf.readfile("ds.dxf"); msp=doc.modelspace()
alt=doc.layers.add("Schieber-alt",color=8); alt.off()
for e in list(msp):
    if e.dxf.layer in ("Schieber","Schieber2","Schieber-max-") and not (e.dxftype()=="LWPOLYLINE" and e.dxf.layer=="Schieber" and len(e)==12):
        e.dxf.layer="Schieber-alt"
def poly(P,layer,col=None):
    pts=[(round(x,4),round(y,4)) for x,y in list(P.exterior.coords)[:-1]]
    a={"layer":layer}; 
    if col: a["color"]=col
    msp.add_lwpolyline(pts,close=True,dxfattribs=a)
A3s=A3.simplify(0.001); B3s=B3.simplify(0.001)
poly(A3s,"Schieber2"); poly(B3s,"Schieber",3)
msp.add_lwpolyline([(RAHMEN[0],-844.58),(RAHMEN[1],-844.58),(RAHMEN[1],-817.18),(RAHMEN[0],-817.18)],close=True,dxfattribs={"layer":"Schieber-max-","color":1})
doc.layers.add("Raststellungen",color=6)
RA={"M offen":-1.3,"M zu":-11.1}
RB={"L-R (nur M offen)":-1.5,"LMR / L-R":-11.4,"LM- / L--":-21.0,"-MR / --R":-31.0}
for t,a in RA.items():
    x=xa1-SA+a; msp.add_line((x,-817.68),(x,-811),dxfattribs={"layer":"Raststellungen"})
    msp.add_text(f"A {t} ({a:+.1f})",height=1.5,dxfattribs={"layer":"Raststellungen","rotation":90}).set_placement((x-0.5,-810.5))
for t,b in RB.items():
    x=xb0+SA+b; msp.add_line((x,-841.98),(x,-851),dxfattribs={"layer":"Raststellungen"})
    msp.add_text(f"B {t} ({b:+.1f})",height=1.5,dxfattribs={"layer":"Raststellungen","rotation":90}).set_placement((x-0.5,-866))
doc.saveas("38x20-Doppelschieber4.dxf")
print("A Punkte",len(A3s.exterior.coords),"B Punkte",len(B3s.exterior.coords))
