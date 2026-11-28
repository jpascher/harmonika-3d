exec(open("neu.py").read())
RR=-1260.0; LL=-1653.0; RAHMEN5=(LL,RR)
XAe=RR+VOR+11.1; XBe=RR+VOR+31.0   # Laschenenden: in der innersten Raste 15 mm ueberstehend
XBu=-1283.08+31.0+1.0              # unterer Teil der B-Lasche erst rechts davon (darf beim Verschieben kein Loch ueberstreichen)
# A: Bruecke nach links, rechts offen; Lasche oben (ueber dem B-Steg) mit Schlitz von oben
A5=unary_union([A2.difference(box(-1275.83,-850,-1200,-810)),
    box(-1640.5,-845.08,-1631.5,-817.68), box(-1640.5,-819.18,-1630.0,-817.68), box(-1640.5,-845.08,-1630.0,-842.58),
    box(-1286.2,-819.18,XAe,-817.68), box(-1286.2,-845.08,-1275.83,-842.58),
    box(-1275.9,-828.9,XAe,-817.68)]).difference(box(XAe-SA-SW/2,-823.68,XAe-SA+SW/2,-817.0))
# B: links gekuerzt (der linke untere Zahn deckt nie ein Loch); Steg nach rechts, Lasche unten mit Schlitz von unten
B5=unary_union([B2.difference(box(-1700,-850,-1600.43,-810))]+[box(-1624.68+50.5*k,-842.43,-1624.68+50.5*k+10.3,-841.0) for k in range(1,8)]
    +[box(-1261.0,-831.95,XBe,-829.28), box(XBu,-842.43,XBe,-829.28)]).difference(box(XBe-SA-SW/2,-843.0,XBe-SA+SW/2,-836.43))
print("A5",A5.geom_type,[round(v,2) for v in A5.bounds],"B5",B5.geom_type,[round(v,2) for v in B5.bounds])
