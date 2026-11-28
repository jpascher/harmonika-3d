# Betaetigung der Registerschieber mit EINEM Daumenhebel (28.11.2026, Johann)
#
# Aussen: Hebel auf einer Welle durch die hintere Gehaeusewand (Griffstockseite, Rahmen_hinten), in der Mitte;
#         der Hebel reicht ueber den Griffstockdeckel nach unten zum Daumen, ein Rastblech mit 6 Kerben sitzt
#         aussen am Deckel, ein Stift am Hebel rastet ein (Hebel aus Federstahl).
# Innen:  Kegelrad auf der Welle treibt ein Ritzel 1:5 auf einer Walze (Achse in X, im Spalt zwischen Rueckwand und
#         Stimmstock 4). Die Walze hat zwei Kurvennuten; je ein Stift an einer Schubstange laeuft darin, die Stangen
#         bewegen sich direkt in X:  Stange B nach links zur B-Koppelstange, Stange A nach rechts zur A-Koppelstange.
#         Jede Koppelstange laeuft quer (Y) ueber alle vier Stimmstoecke und greift mit 4 Stiften in die Rastschlitze.
# Rastfolge (in jedem Schritt bewegt sich nur ein Schieber): LMR, L-R, L--, LM-, -MR, --R.
# Die Uebersetzung 1:5 ist noetig, weil innen nur ~40 mm Hoehe frei sind: so dreht die Walze je Rast 50 Grad und
# die Nuten bleiben flach genug (Steigung wird ausgegeben).
import math
from shapely.geometry import Point, Polygon, box as sbox
from shapely.ops import unary_union
from shapely.affinity import rotate as srot
import registerschieber as rs

FOLGE = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 2), (1, 2)]      # (A-Index, B-Index) je Rast
TH0, DTH, UEBER = -25.0, 10.0, 5.0                              # Hebelwinkel der ersten Rast, Rastabstand, Ueberweg
I_KR = 5.0                                                      # Kegelrad : Ritzel
Z_W, Y_W = 31.5, 23.5                                           # Wellenhoehe, Walzenachse (Y)
R_KR, R_RZ = 18.0, 3.6                                          # Teilkreise Kegelrad / Ritzel
R_WZ, R_NUT, R_NUTB = 16.0, 15.5, 2.0                           # Walze, Nut-Mittellinie (Rohr), Rohrradius
L_HEB, R_RAST = 80.0, 72.0                                      # Hebellaenge (Daumen), Radius der Rastkerben
Y_HEB = (-22.5, -20.5); Y_RB = (-19.5, -17.4); Y_NABE = (-20.5, -1.2)
STANGE_Y, STANGE_Z = (22.0, 25.0), (11.5, 14.5)                 # Schubstangen (auf der Verstaerkungsleiste)
KOPP_Z, KOPP_B = (11.5, 15.0), 4.0                              # Koppelstangen
D_WELLE, D_ACHSE, D_STIFT = 5.0, 4.0, 2.4


def _glatt(t):
    return 0.5 - 0.5 * math.cos(math.pi * min(1.0, max(0.0, t)))


def verlauf(G, th):
    """Schieberlagen (a, b) beim Hebelwinkel th (Grad); zwischen den Rasten weich (Kosinus) uebergeblendet."""
    RA, RB = G["RA"], G["RB"]
    k = (th - TH0) / DTH
    if k <= 0: i0, t = 0, 0.0
    elif k >= len(FOLGE) - 1: i0, t = len(FOLGE) - 2, 1.0
    else: i0 = int(k); t = k - i0
    (a0, b0), (a1, b1) = FOLGE[i0], FOLGE[i0 + 1]
    g = _glatt(t)
    return RA[a0] + (RA[a1] - RA[a0]) * g, RB[b0] + (RB[b1] - RB[b0]) * g


def teile(INSTR, L, RI, B, box):
    import cadquery as cq
    V = cq.Vector
    G = rs.mass(INSTR); RA, RB = G["RA"], G["RB"]
    U = rs.umrisse(INSTR)
    sa, sb = U[0][3], U[0][4]                                   # Schlitzmitten (Zeichnungslage), gleich fuer alle Stoecke
    kA0, kB0 = sa + RA[0], sb + RB[0]                           # Koppelstangen in der Ruhelage (Rast 1 = LMR)
    hubA, hubB = RA[0] - RA[1], RB[0] - RB[2]
    XM = L / 2.0
    out, schnitte = [], []

    def zyl(r, p, d, h): return cq.Solid.makeCylinder(r, h, V(*p), V(*d))
    def xz(poly, y0, y1):
        pts = list(poly.exterior.coords)[:-1]
        s_ = cq.Workplane("XZ").polyline(pts).close().extrude(-(y1 - y0)).translate((0, y0, 0)).val()
        for h_ in poly.interiors:
            s_ = s_.cut(cq.Workplane("XZ").polyline(list(h_.coords)[:-1]).close().extrude(-(y1 - y0) - 2).translate((0, y0 - 1, 0)).val())
        return s_
    def richt(th, r): return (XM + r * math.sin(math.radians(th)), Z_W - r * math.cos(math.radians(th)))

    # ---- Rasten pruefen und ausgeben
    namen = {v: k for k, v in G["REGISTER"].items()}
    rast = []
    for k, (ia, ib) in enumerate(FOLGE):
        th = TH0 + k * DTH; rast.append(th)
        print(f"   Registerhebel Rast {k+1}: {th:+.0f} Grad  A {RA[ia]:+.2f} B {RB[ib]:+.2f}  -> {namen[(RA[ia], RB[ib])]}")
    assert len({namen[(RA[ia], RB[ib])] for ia, ib in FOLGE}) == 6

    # ---- aussen: Hebel, Nabe, Rastblech
    th0 = rast[0]
    heb = unary_union([Point(XM, Z_W).buffer(8.0), sbox(XM - 4.5, Z_W - L_HEB, XM + 4.5, Z_W), Point(XM, Z_W - L_HEB).buffer(9.0)])
    heb = srot(heb, th0, origin=(XM, Z_W)).difference(Point(XM, Z_W).buffer(D_WELLE / 2 + 0.01))
    s_heb = xz(heb, *Y_HEB)
    px, pz = richt(th0, R_RAST)
    s_heb = s_heb.fuse(zyl(1.5, (px, Y_HEB[1] - 0.01, pz), (0, 1, 0), Y_RB[1] - 0.4 - Y_HEB[1]))     # Raststift
    out.append(("Registerhebel", s_heb, "Stahl"))
    out.append(("Registerhebel_Nabe", zyl(7.0, (XM, Y_NABE[0], Z_W), (0, 1, 0), Y_NABE[1] - Y_NABE[0])
                .cut(zyl(D_WELLE / 2 + 0.01, (XM, Y_NABE[0] - 1, Z_W), (0, 1, 0), 30)), "Messing"))
    w0, w1 = rast[0] - 6.0, rast[-1] + 6.0
    ring = Polygon([richt(w0 + (w1 - w0) * i / 60, R_RAST) for i in range(61)] +
                   [richt(w1 - (w1 - w0) * i / 60, R_RAST - 9.0) for i in range(61)])
    for th in rast: ring = ring.difference(Point(*richt(th, R_RAST)).buffer(1.7))
    out.append(("Registerhebel_Rastblech", xz(ring, *Y_RB), "Stahl"))

    # ---- Welle mit Buchse durch die Rueckwand
    out.append(("Registerhebel_Welle", zyl(D_WELLE / 2, (XM, Y_HEB[0], Z_W), (0, 1, 0), Y_W + R_RZ + 2.6 - Y_HEB[0]), "Stahl"))
    out.append(("Registerhebel_Buchse", zyl(4.49, (XM, -1.0, Z_W), (0, 1, 0), RI + 1.0)
                .cut(zyl(D_WELLE / 2 + 0.05, (XM, -2, Z_W), (0, 1, 0), 10)), "Messing"))
    schnitte.append(("Rahmen_hinten", zyl(4.5, (XM, -3.0, Z_W), (0, 1, 0), RI + 4.0)))

    # ---- innen: Kegelrad 1:5, Ritzel, Walze
    y_kr = Y_W + R_RZ + 0.05
    out.append(("Register_Kegelrad", zyl(R_KR, (XM, y_kr, Z_W), (0, 1, 0), 2.5)
                .cut(zyl(D_WELLE / 2 + 0.01, (XM, y_kr - 1, Z_W), (0, 1, 0), 5)), "Messing"))
    x_rz = XM + R_KR + 0.05
    out.append(("Register_Ritzel", zyl(R_RZ, (x_rz, Y_W, Z_W), (1, 0, 0), 2.5)
                .cut(zyl(D_ACHSE / 2 + 0.01, (x_rz - 1, Y_W, Z_W), (1, 0, 0), 5)), "Messing"))
    XD0 = XM + 23.0
    xfB0 = XD0 + 2.0 + R_NUTB + hubB                               # Nutstift B in der Ruhelage (B wandert nach -X)
    xfA0 = xfB0 + R_NUTB + 3.0 + R_NUTB + hubA
    XD1 = xfA0 + R_NUTB + 2.0
    walze = zyl(R_WZ, (XD0, Y_W, Z_W), (1, 0, 0), XD1 - XD0).cut(zyl(D_ACHSE / 2 + 0.01, (XD0 - 1, Y_W, Z_W), (1, 0, 0), XD1 - XD0 + 2))
    steig = 0.0
    for nm, x0_, idx in (("B", xfB0, 1), ("A", xfA0, 0)):
        pts, n = [], 90
        for i in range(n + 1):
            th = rast[0] - UEBER + (rast[-1] - rast[0] + 2 * UEBER) * i / n
            ab = verlauf(G, th)
            x = x0_ + ab[idx] - (RB[0] if idx else RA[0])
            beta = math.radians(-90.0 - I_KR * (th - rast[0]))
            pts.append(V(x, Y_W + R_NUT * math.cos(beta), Z_W + R_NUT * math.sin(beta)))
            if i:
                ds = R_NUT * math.radians(I_KR * (rast[-1] - rast[0] + 2 * UEBER) / n)
                steig = max(steig, math.degrees(math.atan(abs(pts[-1].x - pts[-2].x) / ds)))
        pfad = cq.Wire.assembleEdges([cq.Edge.makeSpline(pts)])
        t0 = (pts[1] - pts[0]).normalized()
        prof = cq.Wire.assembleEdges([cq.Edge.makeCircle(R_NUTB, pts[0], t0)])
        rohr = cq.Solid.sweep(prof, [], pfad, True, True)
        walze = walze.cut(rohr)
    out.append(("Register_Walze", walze, "POM"))
    out.append(("Register_Walzenachse", zyl(D_ACHSE / 2, (XM + 10.0, Y_W, Z_W), (1, 0, 0), XD1 + 5.0 - XM - 10.0), "Stahl"))
    for nm, x0_ in (("links", XM + 11.0), ("rechts", XD1 + 1.0)):
        out.append((f"Register_Lagerwinkel_{nm}", box(x0_, x0_ + 3.0, RI, Y_W + 3.4, Z_W - 6.5, Z_W + 6.5)
                    .cut(zyl(D_ACHSE / 2 + 0.1, (x0_ - 1, Y_W, Z_W), (1, 0, 0), 5)), "Stahl"))

    # ---- Schubstangen mit Nutstiften, Fuehrungen auf der Verstaerkungsleiste
    zst = Z_W - R_NUT + 1.3                                         # Stiftende in der Nut (1,8 tief)
    for nm, xa, xb, xf in (("B", kB0 + KOPP_B / 2, xfB0 + 1.5, xfB0), ("A", xfA0 - 1.5, kA0 - KOPP_B / 2, xfA0)):
        s_ = box(xa, xb, STANGE_Y[0], STANGE_Y[1], STANGE_Z[0], STANGE_Z[1])
        s_ = s_.fuse(zyl(1.5, (xf, Y_W, STANGE_Z[1] - 0.1), (0, 0, 1), zst - STANGE_Z[1] + 0.1))
        out.append((f"Register_Schubstange_{nm}", s_, "Stahl"))
    fx = {"B": (kB0 + 30.0, XM - 30.0), "A": (XD1 + 20.0, kA0 - 25.0)}
    for nm, xs in fx.items():
        for i, x in enumerate(xs):
            f_ = box(x - 3, x + 3, STANGE_Y[0] - 2, STANGE_Y[1] + 2, 9.0, STANGE_Z[1] + 2.5)
            f_ = f_.cut(box(x - 4, x + 4, STANGE_Y[0] - 0.2, STANGE_Y[1] + 0.2, STANGE_Z[0] - 0.2, STANGE_Z[1] + 0.2))
            out.append((f"Register_Fuehrung_{nm}{i+1}", f_, "POM"))

    # ---- Koppelstangen ueber alle Stimmstoecke, Stifte in den Rastschlitzen, Fuehrung an der Vorderwand
    y_v = B - RI
    for nm, kx, hub in (("B", kB0, hubB), ("A", kA0, hubA)):
        s_ = box(kx - KOPP_B / 2, kx + KOPP_B / 2, STANGE_Y[0] - 2.0, y_v - 2.5, *KOPP_Z)
        for s, Ap, Bp, _, _ in U:
            ys = s["ylo"] - 2.0 if nm == "B" else s["yhi"] + 3.7
            s_ = s_.fuse(zyl(D_STIFT / 2, (kx, ys, 5.1), (0, 0, 1), KOPP_Z[0] - 5.1 + 0.1))
        out.append((f"Register_Koppelstange_{nm}", s_, "Stahl"))
        f_ = box(max(RI, kx - hub - KOPP_B / 2 - 4), min(L - RI, kx + KOPP_B / 2 + 4), y_v - 6.0, y_v, 9.0, KOPP_Z[1] + 2.5)
        f_ = f_.cut(box(kx - hub - KOPP_B / 2 - 0.3, kx + KOPP_B / 2 + 0.3, y_v - 7.0, y_v - 1.0, KOPP_Z[0] - 0.2, KOPP_Z[1] + 0.2))
        out.append((f"Register_Fuehrung_Koppel_{nm}", f_, "POM"))

    print(f"   Registerhebel: Welle X {XM:.1f} Z {Z_W:.1f} durch die Rueckwand, Hebel {L_HEB:.0f} mm, Rasten alle {DTH:.0f} Grad "
          f"(Daumenweg je Rast {L_HEB * math.radians(DTH):.1f} mm); Kegelrad 1:{I_KR:g}, Walze D{2*R_WZ:.0f} X {XD0:.1f}..{XD1:.1f}, "
          f"Nutsteigung max {steig:.0f} Grad; Koppelstange B X {kB0 - hubB:.1f}..{kB0:.1f}, A X {kA0 - hubA:.1f}..{kA0:.1f}")
    return out, schnitte


def wege(INSTR, L, teile, schritt=2.0):
    """Bewegte Teile ueber den ganzen Weg (Schubstangen und Koppelstangen in X, Hebel um die Welle) gegen alle
    festen Teile (nicht 'Register...'). Liefert Kollisionen wie die Kollisionspruefung: (Teil, Teil, mm3)."""
    import cadquery as cq
    V = cq.Vector
    G = rs.mass(INSTR); RA, RB = G["RA"], G["RB"]
    XM = L / 2.0
    feste = [(n_, s_, s_.BoundingBox()) for n_, s_, f_ in teile if not n_.startswith("Register")]
    def trifft(a, b):
        return not (a.xmax < b.xmin or b.xmax < a.xmin or a.ymax < b.ymin or b.ymax < a.ymin or a.zmax < b.zmin or b.zmax < a.zmin)
    koll, n_bew = [], 0
    for n_, s_, f_ in teile:
        if n_ in ("Register_Koppelstange_A", "Register_Schubstange_A"): hub = RA[0] - RA[1]
        elif n_ in ("Register_Koppelstange_B", "Register_Schubstange_B"): hub = RB[0] - RB[2]
        elif n_ != "Registerhebel": continue
        if n_ == "Registerhebel":
            w = DTH * (len(FOLGE) - 1); n = int(w / 2.5)
            kop = [s_.rotate(V(XM, 0, Z_W), V(XM, 1, Z_W), -w * i / n) for i in range(n + 1)]
        else:
            n = max(1, int(math.ceil(hub / schritt)))
            kop = [s_.translate(V(-hub * i / n, 0, 0)) for i in range(n + 1)]
        n_bew += 1
        kb = [(k_, k_.BoundingBox()) for k_ in kop]
        for nb, sb, bb in feste:
            vmax = 0.0
            for k_, b_ in kb:
                if not trifft(b_, bb): continue
                try: v_ = k_.intersect(sb).Volume()
                except Exception: v_ = -1.0
                if v_ < 0 or v_ > vmax: vmax = v_
                if v_ < 0: break
            if vmax > 0.5 or vmax < 0: koll.append((n_ + " (Weg)", nb, round(vmax, 1)))
    print(f"   Registermechanik Wege: {n_bew} bewegte Teile geprueft, {len(koll)} Kollisionen")
    return koll
