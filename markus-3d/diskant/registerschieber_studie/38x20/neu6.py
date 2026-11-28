exec(open("neu.py").read())
RR=-1253.5; LL=-1642.5; RAHMEN6=(LL,RR)
XAe=LL-VOR+1.3; XBe=LL-VOR+1.3       # Laschenenden (bei a=b=0): in der innersten (rechtesten) Raste 15 mm ueberstehend
A6=unary_union([A2, box(XAe,-828.9,-1630.64,-817.68)]).difference(box(XAe+SA-SW/2,-823.68,XAe+SA+SW/2,-817.0))
B6=unary_union([B2]+[box(-1624.68+50.5*k,-842.43,-1624.68+50.5*k+10.3,-841.0) for k in range(8)]
    +[box(XBe,-842.43,-1624.68,-832.2)]).difference(box(XBe+SA-SW/2,-843.0,XBe+SA+SW/2,-836.43))
print("A6",A6.geom_type,[round(v,2) for v in A6.bounds],"B6",B6.geom_type,[round(v,2) for v in B6.bounds])
