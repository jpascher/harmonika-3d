from geo import *
WAND=5.0; VOR=15.0; SW,ST,SA=3.2,6.0,7.0
RA=(-0.5,-11.1); RB=(-10.4,-20.9,-31.1)
C_MAX, C_MIN = 1.0, -30.9          # B gegen A: Zahnanschlaege
TOL=1.0                            # Fensterreserve um die Rasten
BR_R=5.0; BR_L=2.0                 # Bruecke rechts (wie bisher), neue Bruecke links 2 mm
# benoetigte Innenkanten (alle vier Stimmstoecke): links: erster B-/A-Zahn bei kleinster Stellung; rechts: A-Bruecke bei groesster
LI=min(min(s["tri"][0][0]+20.9+min(RB)-TOL, s["tri"][0][0]+5.95+min(RA)-TOL) for s in STOCK)-0.5
RI=max(s["tri"][-1][0]+31.2+C_MAX+0.3+BR_R+max(RA)+TOL for s in STOCK)+0.5
OL, OR = LI-WAND, RI+WAND
XB_L = OL - VOR - max(RB)                     # B-Laschenende (bei b=0): innerste Raste -> 15 ueber
XA_L = XB_L + C_MIN - 0.5 - BR_L              # A-Ende links: Bruecke um B herum (auch bei kleinstem c frei)
def schieber3(s):
    ylo,yhi=s["ylo"],s["yhi"]; tri=s["tri"]; x0=tri[0][0]; xl=tri[-1][0]
    A=[]; B=[]
    for x,er in tri:
        y0,y1=band(s,er,"A"); A.append(box(x+5.95,y0,x+16.25,y1))
        pr="hi" if er=="lo" else "lo"; y0,y1=band(s,pr,"B"); B.append(box(x+20.9,y0,x+31.2,y1))
    erstes=lambda r: (x0-4 if tri[0][1]==r else x0-9)
    xb=xl+31.2+C_MAX+0.3
    A+= [box(xb,ylo-7.7,xb+BR_R,yhi+6.7),                                   # Bruecke rechts
         box(XA_L,yhi+5.2,xb+BR_R,yhi+6.7), box(XA_L,ylo-7.7,xb+BR_R,ylo-5.2),   # Leisten
         box(XA_L,ylo-7.7,XA_L+BR_L,yhi+6.7),                               # neue Bruecke links (2 mm)
         box(XA_L,ylo+8.1+0.38,erstes("hi")-0.5-TOL,yhi+6.7)]               # Griffteil oben ueber dem B-Steg
    Ap=unary_union(A).difference(box(XA_L+BR_L+SA-SW/2,yhi+6.7-ST,XA_L+BR_L+SA+SW/2,yhi+7.5))
    B+= [box(XB_L,ylo+5.43,xl+31.2,ylo+8.1),
         box(XB_L,ylo-5.05,min(erstes("lo")-0.5+9.0,x0+20.9),ylo+8.1)]
    Bp=unary_union(B).difference(box(XB_L+SA-SW/2,ylo-6.0,XB_L+SA+SW/2,ylo-5.05+ST))
    return Ap,Bp
if __name__=="__main__":
    print(f"Innen {LI:.1f} .. {RI:.1f} = {RI-LI:.1f}  aussen {OL:.1f} .. {OR:.1f} = {OR-OL:.1f}")
    for k,s in enumerate(STOCK):
        A,B=schieber3(s); print(4-k,A.geom_type,len(A.interiors) if A.geom_type=="Polygon" else "",[round(v,1) for v in A.bounds],B.geom_type,[round(v,1) for v in B.bounds])
