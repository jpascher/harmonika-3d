from geo3 import *
from shapely.affinity import translate
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import ezdxf
from matplotlib.path import Path
from matplotlib.patches import PathPatch
def flaeche(ax,g,c):
    ringe=[g.exterior]+list(g.interiors); v=[];k=[]
    for r in ringe:
        p=list(r.coords); v+=p; k+=[Path.MOVETO]+[Path.LINETO]*(len(p)-2)+[Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(v,k),fc=c,ec=c,alpha=.5,lw=.5))
bm=ezdxf.readfile("boden.dxf").modelspace()
REGR=[("LMR",RA[0],RB[0]),("LM-",RA[0],RB[1]),("-MR",RA[0],RB[2]),("L-R",RA[1],RB[0]),("L--",RA[1],RB[1]),("--R",RA[1],RB[2])]
fig,axs=plt.subplots(3,2,figsize=(18,15))
for ax,(m,a,b) in zip(axs.T.flat,REGR):
    ax.add_patch(plt.Rectangle((OL,0),OR-OL,205,fill=False,ec="#8b6a46",lw=2))
    ax.add_patch(plt.Rectangle((LI,5),RI-LI,195,fill=False,ec="#8b6a46",lw=.8,ls=":"))
    for s in STOCK:
        A,B=schieber3(s)
        for P,c in ((translate(A,a),"#4b6a8a"),(translate(B,b),"#3f8a3a")):
            for g in getattr(P,"geoms",[P]):
                flaeche(ax,g,c)
        U=unary_union([translate(A,a),translate(B,b)])
        for _,_,h in loecher(s):
            f=1-h.intersection(U).area/h.area; x,y=h.exterior.xy
            ax.fill(x,y,"white" if f>0.99 else "#c0392b" if f<0.01 else "#f3b01b",ec="k",lw=.4,zorder=5)
    ax.set_title(f"{m}:  A {a:+.1f} / B {b:+.1f}",loc="left",fontsize=12)
    ax.set_aspect("equal"); ax.set_xlim(-420,20); ax.set_ylim(35,200); ax.axis("off")
plt.tight_layout(); plt.savefig("Diskantboden50_Register_v2.png",dpi=80)
