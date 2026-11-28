exec(open("neu5.py").read())
import json; from shapely.affinity import translate
kan=json.load(open("kan.json"))
a,b=-11.1,-31; Aa=translate(A5,a);Bb=translate(B5,b)
print("Ueberlappung",Aa.intersection(Bb).area, Aa.intersection(Bb).bounds)
U=unary_union([Aa,Bb])
for ti,k in enumerate(kan):
    for c in "LMR":
        v=1-L[k[c]].intersection(U).area/L[k[c]].area
        if (c=="R" and v<0.999) or (c!="R" and v>0.001): print(ti+1,c,round(v,3))
