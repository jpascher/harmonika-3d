exec(open("sim2.py").read().split("def mus")[0])
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from shapely.affinity import translate
from shapely.ops import unary_union
def zeichne(ax,PA,PB,a,b,titel):
    for P,c in ((translate(PA,a),"#4b6a8a"),(translate(PB,b),"#3f8a3a")):
        for g in getattr(P,"geoms",[P]):
            x,y=g.exterior.xy; ax.fill(x,y,c,alpha=.55,lw=.6,ec=c)
    U=unary_union([translate(PA,a),translate(PB,b)])
    for p in L:
        f=1-p.intersection(U).area/p.area; x,y=p.exterior.xy
        ax.fill(x,y,"white" if f>0.9 else "#c0392b" if f<0.1 else "#f3b01b",ec="k",lw=.6,zorder=5)
    ax.set_title(titel,fontsize=10,loc="left"); ax.set_aspect("equal"); ax.set_xlim(-1660,-1245); ax.set_ylim(-847,-815); ax.axis("off")
F=[("orig",A,B,0,0,"Original, gezeichnete Lage: L-R (Mittelchor zu)"),
   ("orig",A,B,-1,-21,"Original A -1 / B -21: soll LM-, Tripel 13 (rechts) bleibt offen"),
   ("neu",A2,B2,-1,-11,"Neu: A -1 / B -11 → LMR"),("neu",A2,B2,-1,-1,"Neu: A -1 / B -1 → L-R"),
   ("neu",A2,B2,-1,-21,"Neu: A -1 / B -21 → LM-"),("neu",A2,B2,-2,-31,"Neu: A -2 / B -31 → -MR"),
   ("neu",A2,B2,-11,-21,"Neu: A -11 / B -21 → L--"),("neu",A2,B2,-11,-31,"Neu: A -11 / B -31 → --R")]
fig,axs=plt.subplots(len(F),1,figsize=(16,2.1*len(F)))
for ax,(n,PA,PB,a,b,t) in zip(axs,F): zeichne(ax,PA,PB,a,b,t)
plt.tight_layout(); plt.savefig("doppelschieber_test.png",dpi=90)
