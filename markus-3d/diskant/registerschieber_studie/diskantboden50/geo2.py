from geo import *
AUSSEN_L, AUSSEN_R = -380.0, 0.0          # Aussenflaechen Rahmen (Boden-Zeichnung)
VOR=15.0; SW,ST,SA=3.2,6.0,7.0
RA=(-0.5,-11.1); RB=(-10.4,-20.9,-31.1)    # Raststellungen (gemeinsam fuer alle vier Stimmstoecke)
C_MAX=1.0                                  # B gegen A hoechstens +1.0 (dann stossen die Zaehne aneinander)
XA_L = AUSSEN_L - VOR - max(RA)            # A-Lasche links: Ende bei a=0 (innerste Raste -0.5 -> 15 ueber)
XB_L = AUSSEN_L - VOR - max(RB)            # B-Lasche links
def schieber_links(s):
    """Betaetigung links: A-Lasche oben, B-Lasche unten; A-Bruecke rechts ausserhalb (laeuft durch die rechte Wand)."""
    ylo,yhi=s["ylo"],s["yhi"]; tri=s["tri"]; x0=tri[0][0]; xl=tri[-1][0]
    A=[]; B=[]
    for x,er in tri:
        y0,y1=band(s,er,"A"); A.append(box(x+5.95,y0,x+16.25,y1))
        pr="hi" if er=="lo" else "lo"; y0,y1=band(s,pr,"B"); B.append(box(x+20.9,y0,x+31.2,y1))
    # erstes Loch je Reihe (links)
    def erstes(reihe):
        x,er=tri[0]
        return x-4 if er==reihe else x-9
    xb=xl+31.2+C_MAX+0.3                                   # Bruecke rechts
    A.append(box(xb,ylo-7.7,xb+5.0,yhi+6.7))
    a_rechts_tab=erstes("hi")-0.5-1.0                      # A-Lasche ueberstreicht beim Verschieben keine Loecher der oberen Reihe
    A.append(box(XA_L,yhi+5.2,xb+5.0,yhi+6.7)); A.append(box(x0-15.0,ylo-7.7,xb+5.0,ylo-5.2))
    A.append(box(XA_L,ylo+8.1+0.38,a_rechts_tab,yhi+6.7))
    Ap=unary_union(A).difference(box(XA_L+SA-SW/2,yhi+6.7-ST,XA_L+SA+SW/2,yhi+7.5))
    b_rechts_tab=erstes("lo")-0.5+9.0            # Lasche liegt bei b<=-9 links der unteren Loecher
    B.append(box(XB_L,ylo+5.43,xl+31.2,ylo+8.1))          # Steg
    B.append(box(XB_L,ylo-5.05,min(b_rechts_tab,x0+20.9),ylo+8.1))
    Bp=unary_union(B).difference(box(XB_L+SA-SW/2,ylo-6.0,XB_L+SA+SW/2,ylo-5.05+ST))
    return Ap,Bp
