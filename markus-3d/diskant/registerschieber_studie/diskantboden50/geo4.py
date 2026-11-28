from geo import *
OL, OR = -396.0, 16.0; WAND=5.5; LI, RI = OL+WAND, OR-WAND      # 410er-Gehaeuse, Einbau mittig (+15 je Ende)
SW,ST=3.2,6.0
RA=(-0.5,-11.1); RB=(-10.4,-20.9,-31.1); C_MAX=1.0; TOL=1.0; BR_R=5.0
def erstes(s,r): x,er=s["tri"][0]; return x-4 if er==r else x-9
A_TAB_R=min(erstes(s,"hi")-0.5-TOL for s in STOCK); XA_L=A_TAB_R-12.0; SA_A=7.0
B_LUG_R=min(min(erstes(s,"lo")-0.5+9.0, s["tri"][0][0]+20.9) for s in STOCK); XB_L=B_LUG_R-10.3; SA_B=5.0
def schieber4(s):
    ylo,yhi=s["ylo"],s["yhi"]; tri=s["tri"]; x0=tri[0][0]; xl=tri[-1][0]
    A=[]; B=[]
    for x,er in tri:
        y0,y1=band(s,er,"A"); A.append(box(x+5.95,y0,x+16.25,y1))
        pr="hi" if er=="lo" else "lo"; y0,y1=band(s,pr,"B"); B.append(box(x+20.9,y0,x+31.2,y1))
    xb=xl+31.2+C_MAX+0.3
    A+=[box(xb,ylo-7.7,xb+BR_R,yhi+6.7), box(XA_L,yhi+5.2,xb+BR_R,yhi+6.7), box(x0-15.0,ylo-7.7,xb+BR_R,ylo-5.2),
        box(XA_L,ylo+8.1+0.38,erstes(s,"hi")-0.5-TOL,yhi+6.7)]
    Ap=unary_union(A).difference(box(XA_L+SA_A-SW/2,yhi+6.7-ST,XA_L+SA_A+SW/2,yhi+7.5))
    B+=[box(XB_L,ylo+5.43,xl+31.2,ylo+8.1), box(XB_L,ylo-5.05,min(erstes(s,"lo")-0.5+9.0,x0+20.9),ylo+8.1)]
    Bp=unary_union(B).difference(box(XB_L+SA_B-SW/2,ylo-6.0,XB_L+SA_B+SW/2,ylo-5.05+ST))
    return Ap,Bp
if __name__=="__main__":
    print("XA_L",round(XA_L,1),"XB_L",round(XB_L,1))
    for k,s in enumerate(STOCK):
        A,B=schieber4(s)
        aL=A.bounds[0]+min(RA); aR=A.bounds[2]+max(RA); bL=B.bounds[0]+min(RB); bR=B.bounds[2]+max(RB)
        print(f"St{4-k}: A {aL:.1f}..{aR:.1f}  B {bL:.1f}..{bR:.1f}   Luft links {min(aL,bL)-LI:.1f} rechts {RI-max(aR,bR):.1f}")
