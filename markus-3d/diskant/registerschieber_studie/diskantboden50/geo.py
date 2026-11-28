# Diskantboden 50 (Markus BESASDES): Tripel je Stimmstock, Schieber A/B nach den Regeln aus 38x20-Doppelschieber
import ezdxf, collections
from shapely.geometry import box
from shapely.ops import unary_union
m=ezdxf.readfile("boden.dxf").modelspace()
ins=sorted({(round(e.dxf.insert[0],2),round(e.dxf.insert[1],2),e.dxf.name) for e in m.query('INSERT[layer=="2Füllung-Öffnug"]')})
ys=sorted({y for _,y,_ in ins})
STOCK=[]   # je Stimmstock: ylo, yhi, Tripel [(x, einzel_reihe 'lo'/'hi')]
for k in range(0,len(ys),2):
    ylo=ys[k]; yhi=ylo+13.0                                    # Reihenabstand 13 wie die eckigen Oeffnungen (Boden hat 12)
    tr=[(x,"lo" if (n=="*U3" and y==ylo) else "hi") for x,y,n in ins if y in (ys[k],ys[k+1])]
    tr=sorted(tr)
    STOCK.append(dict(ylo=ylo,yhi=yhi,tri=tr))
WI, WA = -376.0, -4.0     # Innenkanten Boden (GH-fuellung-innen)
def loecher(s):
    out=[]
    for i,(x,er) in enumerate(s["tri"]):
        ye=s["ylo"] if er=="lo" else s["yhi"]; yp=s["yhi"] if er=="lo" else s["ylo"]
        out+= [(i,"M",box(x-4,ye-4.9,x+4,ye+4.9)),(i,"L",box(x-9,yp-4.9,x-1,yp+4.9)),(i,"R",box(x+1,yp-4.9,x+9,yp+4.9))]
    return out
def band(s,reihe,teil):
    y=s["yhi"] if reihe=="hi" else s["ylo"]
    if teil=="A": return (y-4.9,y+5.2) if reihe=="hi" else (y-5.2,y+4.9)
    return (y-4.9,y+5.2) if reihe=="hi" else (y-5.05,y+5.48)
def schieber(s, bruecke="rechts", ra=(-12.2,0.5), rc=(-31.5,0.0)):
    """A: Zaehne vor jedem Einzelloch; B: Zaehne rechts neben jedem Paar; Steg dazwischen."""
    ylo,yhi=s["ylo"],s["yhi"]; tri=s["tri"]
    A=[]; B=[]
    for x,er in tri:
        y0,y1=band(s,er,"A"); A.append(box(x+5.95,y0,x+16.25,y1))
        pr="hi" if er=="lo" else "lo"; y0,y1=band(s,pr,"B"); B.append(box(x+20.9,y0,x+31.2,y1))
    bx0=tri[0][0]+20.9; bx1=tri[-1][0]+31.2
    B.append(box(bx0,ylo+5.43,bx1,ylo+8.1))
    ax0=tri[0][0]+5.95; ax1=tri[-1][0]+16.25
    if bruecke=="rechts":
        xb=bx1-rc[0]*0+rc[1]+0.5      # Bruecke rechts neben dem letzten B-Zahn bei groesstem c
        ax1=xb+5.0; A.append(box(xb,ylo-7.7,ax1,yhi+6.7))
    else:
        xb=bx0+rc[0]-0.5             # Bruecke links neben B bei kleinstem c
        ax0=xb-5.0; A.append(box(ax0,ylo-7.7,xb,yhi+6.7))
    A.append(box(ax0,yhi+5.2,ax1,yhi+6.7)); A.append(box(ax0,ylo-7.7,ax1,ylo-5.2))
    return unary_union(A), unary_union(B)
if __name__=="__main__":
    for k,s in enumerate(STOCK):
        print(f"Stimmstock {4-k} (y {s['ylo']}/{s['yhi']}): {len(s['tri'])} Tripel, x {s['tri'][0][0]} .. {s['tri'][-1][0]}, Teilung", sorted({round(s['tri'][i+1][0]-s['tri'][i][0],2) for i in range(len(s['tri'])-1)}), "Einzel:", "".join("u" if e=="lo" else "o" for _,e in s["tri"]))
