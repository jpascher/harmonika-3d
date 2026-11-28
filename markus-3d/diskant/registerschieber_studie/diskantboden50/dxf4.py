from geo4 import *
import ezdxf
doc=ezdxf.readfile("boden.dxf"); msp=doc.modelspace()
for n,c in (("Sole-Oeffnung-eckig",6),("Schieber-A",5),("Schieber-B",3),("Raststellungen",1),("Wanddurchbruch",30)):
    doc.layers.add(n,color=c)
def pl(P,layer):
    P=P.simplify(0.001)
    msp.add_lwpolyline([(round(x,4),round(y,4)) for x,y in list(P.exterior.coords)[:-1]],close=True,dxfattribs={"layer":layer})
for k,s in enumerate(STOCK):
    for _,_,h in loecher(s): pl(h,"Sole-Oeffnung-eckig")
    A,B=schieber4(s); pl(A,"Schieber-A"); pl(B,"Schieber-B")
    # Wanddurchbrueche (Hoehe ueber alles was durchgeht, +0.3 Luft)
    y0,y1=s["ylo"]-7.7-0.3, s["yhi"]+6.7+0.3
    pass
    msp.add_text(f"Stimmstock {4-k}",height=3,dxfattribs={"layer":"Raststellungen"}).set_placement((-520,(s['ylo']+s['yhi'])/2))
# Rastmarken an den Laschenschlitzen (oberster Stimmstock oben bzw. unterster unten)
s1,s4=STOCK[-1],STOCK[0]
for t,a in (("A M offen",RA[0]),("A M zu",RA[1])):
    x=XA_L+SA_A+a; msp.add_line((x,s1["yhi"]+6.7),(x,s1["yhi"]+14),dxfattribs={"layer":"Raststellungen"})
    msp.add_text(f"{t} ({a:+.1f})",height=2,dxfattribs={"layer":"Raststellungen","rotation":90}).set_placement((x-0.7,s1["yhi"]+15))
for t,b in (("B LMR/L-R",RB[0]),("B LM-/L--",RB[1]),("B -MR/--R",RB[2])):
    x=XB_L+SA_B+b; msp.add_line((x,s4["ylo"]-5.05),(x,s4["ylo"]-14),dxfattribs={"layer":"Raststellungen"})
    msp.add_text(f"{t} ({b:+.1f})",height=2,dxfattribs={"layer":"Raststellungen","rotation":90}).set_placement((x-0.7,s4["ylo"]-38))
doc.layers.add("Gehaeuse-neu",color=1)
for xa,xb in ((OL,OR),(LI,RI)): msp.add_lwpolyline([(xa,0),(xb,0),(xb,205),(xa,205)],close=True,dxfattribs={"layer":"Gehaeuse-neu"})
doc.saveas("Diskantboden50_Doppelschieber_410.dxf"); print("ok")
