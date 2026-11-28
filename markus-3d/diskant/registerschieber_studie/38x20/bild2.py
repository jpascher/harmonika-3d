exec(open("neu.py").read())
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from shapely.affinity import translate
def zeichne(ax,a,b,titel):
    ax.add_patch(plt.Rectangle((RAHMEN[0],-844.58),RAHMEN[1]-RAHMEN[0],27.4,fill=False,ec="#a3332b",lw=1.2,ls="--"))
    for P,c in ((translate(A3,a),"#4b6a8a"),(translate(B3,b),"#3f8a3a")):
        x,y=P.exterior.xy; ax.fill(x,y,c,alpha=.55,lw=.6,ec=c)
    U=unary_union([translate(A3,a),translate(B3,b)])
    for p in L:
        f=1-p.intersection(U).area/p.area; x,y=p.exterior.xy
        ax.fill(x,y,"white" if f>0.99 else "#c0392b" if f<0.01 else "#f3b01b",ec="k",lw=.6,zorder=5)
    ax.set_title(titel,fontsize=10,loc="left"); ax.set_aspect("equal"); ax.set_xlim(-1695,-1215); ax.set_ylim(-847,-815); ax.axis("off")
F=[(-1.3,-1.5,"L-R"),(-1.3,-11.4,"LMR"),(-1.3,-21,"LM-"),(-1.3,-31,"-MR"),(-11.1,-11.4,"L-R"),(-11.1,-21,"L--"),(-11.1,-31,"--R")]
fig,axs=plt.subplots(len(F),1,figsize=(16,2.0*len(F)))
for ax,(a,b,m) in zip(axs,F): zeichne(ax,a,b,f"A {a:+.1f} / B {b:+.1f}  →  {m}")
plt.tight_layout(); plt.savefig("doppelschieber4_raststellungen.png",dpi=90)
