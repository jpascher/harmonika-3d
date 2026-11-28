from geo2 import *
from shapely.affinity import translate
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import ezdxf
bm=ezdxf.readfile("boden.dxf").modelspace()
REGR=[("LMR",RA[0],RB[0]),("LM-",RA[0],RB[1]),("-MR",RA[0],RB[2]),("L-R",RA[1],RB[0]),("L--",RA[1],RB[1]),("--R",RA[1],RB[2])]
fig,axs=plt.subplots(3,2,figsize=(18,15))
for ax,(m,a,b) in zip(axs.T.flat,REGR):
    ax.add_patch(plt.Rectangle((-380,0),380,205,fill=False,ec="#8b6a46",lw=2))
    ax.add_patch(plt.Rectangle((-376,4),372,197,fill=False,ec="#8b6a46",lw=.8,ls=":"))
    for s in STOCK:
        A,B=schieber_links(s)
        for P,c in ((translate(A,a),"#4b6a8a"),(translate(B,b),"#3f8a3a")):
            for g in getattr(P,"geoms",[P]):
                x,y=g.exterior.xy; ax.fill(x,y,c,alpha=.5,lw=.5,ec=c)
        U=unary_union([translate(A,a),translate(B,b)])
        for _,_,h in loecher(s):
            f=1-h.intersection(U).area/h.area; x,y=h.exterior.xy
            ax.fill(x,y,"white" if f>0.99 else "#c0392b" if f<0.01 else "#f3b01b",ec="k",lw=.4,zorder=5)
    ax.set_title(f"{m}:  A {a:+.1f} / B {b:+.1f}",loc="left",fontsize=12)
    ax.set_aspect("equal"); ax.set_xlim(-425,15); ax.set_ylim(35,200); ax.axis("off")
plt.tight_layout(); plt.savefig("Diskantboden50_Register.png",dpi=80)
