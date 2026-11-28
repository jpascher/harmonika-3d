exec(open("sim2.py").read().split("def mus")[0])
from shapely.geometry import box
from shapely.ops import unary_union
RAHMEN=(-1644.93,-1251.93)          # Schieber-max neu (rechts fuer die Verlaengerung)
VOR=15.0                             # Ueberstand eingeschoben
SW,ST,SA=3.2,6.0,7.0                 # Schlitzbreite, -tiefe, Abstand Schlitzmitte vom Laschenende
A_IN, B_IN = -11.1, -1.3             # weitester eingeschobener Zustand (A nach links, B nach rechts)
# Schieber A: Lasche rechts an der Endleiste, volle Hoehe, Schlitz von oben
xa1=RAHMEN[1]+VOR-A_IN
A3=unary_union([A2, box(-1252.83,-831.68,xa1,-817.68)]).difference(box(xa1-SA-SW/2,-823.68,xa1-SA+SW/2,-817.0))
# Schieber B: Lasche links, zwischen den Leisten von A, Schlitz von unten
xb0=RAHMEN[0]-VOR-B_IN
B3=unary_union([B2, box(xb0,-842.43,-1624.68,-828.43)]).difference(box(xb0+SA-SW/2,-843.0,xb0+SA+SW/2,-836.43))
# untere Zaehne von B bis 0.15 mm an die Leiste von A verlaengern (Loecher reichen bis -842.28, Zaehne endeten bei -841.98)
B3=unary_union([B3]+[box(-1624.68+50.5*k,-842.43,-1624.68+50.5*k+10.3,-841.0) for k in range(8)])
print("A3",A3.geom_type,[round(v,2) for v in A3.bounds]," B3",B3.geom_type,[round(v,2) for v in B3.bounds])
print("Laschen: A bis",round(xa1,2),"Schlitzmitte",round(xa1-SA,2),"| B ab",round(xb0,2),"Schlitzmitte",round(xb0+SA,2))
