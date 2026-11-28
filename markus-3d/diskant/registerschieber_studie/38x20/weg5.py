exec(open("neu5.py").read())
import numpy as np; from shapely.affinity import translate
def koll(a,b): return translate(A5,a).intersection(translate(B5,b)).area>1e-6
print("B-Weg bei A -1.3:", [round(b,1) for b in np.arange(-31,-1.49,0.1) if koll(-1.3,b)][:5])
print("B-Weg bei A -11.1:", [round(b,1) for b in np.arange(-31,-11.39,0.1) if koll(-11.1,b)][:5])
for b in (-11.4,-21,-31):
    print("A-Weg bei B",b, [round(a,1) for a in np.arange(-11.1,-1.29,0.1) if koll(a,b)][:5])
# Gesamtlaenge
v4=(-1658.63-31)-(-1225.83-1.3); v5=LL-(XBe-1.3)
print("Rahmen v4",round(-1251.93+1644.93,1),"v5",round(RR-LL,1)," Gesamt mit Laschen (groesster Ausschlag) v4",round(-v4,1),"v5",round(-v5,1))
