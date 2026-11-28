exec(open("neu6.py").read())
import numpy as np; from shapely.affinity import translate
def koll(a,b): return translate(A6,a).intersection(translate(B6,b)).area>1e-6
print("B-Weg bei A -1.3:", [round(b,1) for b in np.arange(-31,-1.49,0.1) if koll(-1.3,b)][:5])
print("B-Weg bei A -11.1:", [round(b,1) for b in np.arange(-31,-11.39,0.1) if koll(-11.1,b)][:5])
for b in (-11.4,-21,-31):
    print("A-Weg bei B",b, [round(a,1) for a in np.arange(-11.1,-1.29,0.1) if koll(a,b)][:5])
