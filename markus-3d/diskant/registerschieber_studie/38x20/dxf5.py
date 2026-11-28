exec(open("neu5.py").read())
import ezdxf
doc=ezdxf.readfile("ds.dxf"); msp=doc.modelspace()
alt=doc.layers.add("Schieber-alt",color=8); alt.off()
for e in list(msp):
    if e.dxf.layer in ("Schieber","Schieber2","Schieber-max-") and not (e.dxftype()=="LWPOLYLINE" and e.dxf.layer=="Schieber" and len(e)==12):
        e.dxf.layer="Schieber-alt"
def poly(P,layer,col=None):
    P=P.simplify(0.001); a={"layer":layer}
    if col: a["color"]=col
    msp.add_lwpolyline([(round(x,4),round(y,4)) for x,y in list(P.exterior.coords)[:-1]],close=True,dxfattribs=a)
poly(A5,"Schieber2"); poly(B5,"Schieber",3)
msp.add_lwpolyline([(LL,-844.58),(RR,-844.58),(RR,-817.18),(LL,-817.18)],close=True,dxfattribs={"layer":"Schieber-max-","color":1})
doc.layers.add("Raststellungen",color=6)
for t,a in {"M offen":-1.3,"M zu":-11.1}.items():
    x=XAe-SA+a; msp.add_line((x,-817.68),(x,-811),dxfattribs={"layer":"Raststellungen"})
    msp.add_text(f"A {t} ({a:+.1f})",height=1.5,dxfattribs={"layer":"Raststellungen","rotation":90}).set_placement((x-0.5,-810.5))
for t,b in {"L-R (nur M offen)":-1.5,"LMR / L-R":-11.4,"LM- / L--":-21.0,"-MR / --R":-31.0}.items():
    x=XBe-SA+b; msp.add_line((x,-842.43),(x,-851),dxfattribs={"layer":"Raststellungen"})
    msp.add_text(f"B {t} ({b:+.1f})",height=1.5,dxfattribs={"layer":"Raststellungen","rotation":90}).set_placement((x-0.5,-872))
doc.saveas("38x20-Doppelschieber5.dxf")
