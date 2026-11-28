# Registerschieber fuer den 3-choerigen Diskant (28.11.2026, Johann)
# Je Stimmstock zwei Schieber (Epoxy 0,5 mm) in einer Tasche unter der Sohle:
#   A (aussen): ein Zahn rechts neben jedem Einzelloch -> schaltet den Mittelchor M
#   B (innen, Steg zwischen den Lochreihen): ein Zahn rechts neben jedem Lochpaar -> waehlt L, R oder beide
# Raststellungen (gleich fuer alle Stimmstoecke, mm ab Zeichnungslage, minus = Richtung kleines X):
#   A -0,5 = M offen, -11,1 = M zu;  B -10,4 = L+R, -20,9 = R zu, -31,1 = L zu  -> 6 Register
# Betaetigung (Johann): B am Ende mit kleinem X (Lasche unten, Schlitz von unten), A am Ende mit grossem X
# (geschlossene Bruecke mit Schlitz von oben). Alles innerhalb des Rahmens; die Schlitze liegen in allen Rasten
# ausserhalb der Stimmstoecke (Hebel von oben). Die Klappen werden so in das Gehaeuse gesetzt, dass der Einbau
# moeglichst kurz wird (instrument.py: einbau()).
from shapely.geometry import box as sbox, Polygon
from shapely.ops import unary_union
from shapely.affinity import translate

T_SCH = 0.5                       # Schieberstaerke (Epoxy)
SW, ST = 3.2, 6.0                 # Rastschlitz Breite/Tiefe
RA = (-0.5, -11.1)                # A: M offen / M zu
RB = (-10.4, -20.9, -31.1)        # B: LMR / LM- / -MR
RUHE = (RA[0], RB[0])             # im Modell gezeichnet: Register LMR
REGISTER = {"LMR": (RA[0], RB[0]), "LM-": (RA[0], RB[1]), "-MR": (RA[0], RB[2]),
            "L-R": (RA[1], RB[0]), "L--": (RA[1], RB[1]), "--R": (RA[1], RB[2])}
C_MAX, TOL = 1.0, 1.0             # B gegen A hoechstens +1 (Zahnanschlag); Fenster um die Rasten
STOCK_ENDE = 8.75 + 7.5 + 2.5     # Stimmstock endet so weit vor/hinter dem aeussersten Tripel (Kammer + Trennwand)
FREI = 1.6 + 1.0                  # halbe Schlitzbreite + Luft zum Stimmstockende (Hebel von oben)
A_BLOCK, A_SCHLITZ = 8.5, 4.25    # A: Endblock rechts (Bruecke) und Lage der Schlitzmitte darin
B_SCHLITZ = 5.0                   # B: Schlitzmitte ab Laschenende


def stoecke(INSTR):
    out = []
    for r, R in sorted(INSTR["reihen"].items()):
        kl = R["klappen"]
        ym = sum(k["y"] + (2.0 if k["lage"] == "unten" else -2.0) for k in kl) / len(kl)
        tri = sorted((k["x"], "hi" if k["lage"] == "unten" else "lo") for k in kl)
        out.append(dict(reihe=r, ylo=ym - 6.5, yhi=ym + 6.5, tri=tri))
    return out


def _band(s, reihe, teil):
    y = s["yhi"] if reihe == "hi" else s["ylo"]
    if teil == "A": return (y - 4.9, y + 5.2) if reihe == "hi" else (y - 5.2, y + 4.9)
    return (y - 4.9, y + 5.2) if reihe == "hi" else (y - 5.05, y + 5.48)


def _erstes(s, r):
    x, er = s["tri"][0]
    return x - 4 if er == r else x - 9


def loecher(s):
    out = []
    for i, (x, er) in enumerate(s["tri"]):
        ye = s["ylo"] if er == "lo" else s["yhi"]; yp = s["yhi"] if er == "lo" else s["ylo"]
        out += [(i, "M", sbox(x - 4, ye - 4.9, x + 4, ye + 4.9)), (i, "L", sbox(x - 9, yp - 4.9, x - 1, yp + 4.9)),
                (i, "R", sbox(x + 1, yp - 4.9, x + 9, yp + 4.9))]
    return out


def umrisse(INSTR):
    S = stoecke(INSTR)
    # B-Lasche (alle Stoecke gleiches X): Schlitz in der rechtesten Raste noch links vom Stimmstockende
    xb_l = min(min(s["tri"][0][0] for s in S) - STOCK_ENDE - FREI - B_SCHLITZ - (max(RB) + TOL),
               min(min(_erstes(s, "lo") - 0.5 + 9.0, s["tri"][0][0] + 20.9) for s in S) - 10.3)
    # A-Endblock rechts (alle Stoecke gleiches X): hinter dem letzten B-Zahn beim groessten c
    xr = max(s["tri"][-1][0] for s in S) + 31.2 + C_MAX + 0.3
    erg = []
    for s in S:
        ylo, yhi, tri = s["ylo"], s["yhi"], s["tri"]; x0, xl = tri[0][0], tri[-1][0]
        A, B = [], []
        for x, er in tri:
            y0, y1 = _band(s, er, "A"); A.append(sbox(x + 5.95, y0, x + 16.25, y1))
            pr = "hi" if er == "lo" else "lo"; y0, y1 = _band(s, pr, "B"); B.append(sbox(x + 20.9, y0, x + 31.2, y1))
        A += [sbox(xr, ylo - 7.7, xr + A_BLOCK, yhi + 6.7),                                   # Bruecke/Endblock
              sbox(x0 - 2.0, yhi + 5.2, xr, yhi + 6.7), sbox(x0 - 2.0, ylo - 7.7, xr, ylo - 5.2)]  # Leisten
        Ap = unary_union(A).difference(sbox(xr + A_SCHLITZ - SW / 2, yhi + 6.7 - ST, xr + A_SCHLITZ + SW / 2, yhi + 7.5))
        B += [sbox(xb_l, ylo + 5.43, xl + 31.2, ylo + 8.1),
              sbox(xb_l, ylo - 5.05, min(_erstes(s, "lo") - 0.5 + 9.0, x0 + 20.9), ylo + 8.1)]
        Bp = unary_union(B).difference(sbox(xb_l + B_SCHLITZ - SW / 2, ylo - 6.0, xb_l + B_SCHLITZ + SW / 2, ylo - 5.05 + ST))
        erg.append((s, Ap, Bp, xr + A_SCHLITZ, xb_l + B_SCHLITZ))
    return erg


def bedarf(INSTR):
    """Ueberstrichener Bereich in X (alle Rasten samt Fenster): (xmin, xmax)."""
    xs0, xs1 = [], []
    for s, Ap, Bp, sa, sb in umrisse(INSTR):
        xs0 += [Ap.bounds[0] + min(RA) - TOL, Bp.bounds[0] + min(RB) - TOL]
        xs1 += [Ap.bounds[2] + max(RA) + TOL, Bp.bounds[2] + max(RB) + TOL]
    return min(xs0), max(xs1)


def pruefe(INSTR, schritt=0.5):
    """Alle 6 Register in jedem Stimmstock sauber offen/zu, Wege zwischen den Rasten ohne Anstossen."""
    fehler = []
    for s, Ap, Bp, sa, sb in umrisse(INSTR):
        H = loecher(s)
        def zust(a, b):
            Aa, Bb = translate(Ap, a), translate(Bp, b)
            if Aa.intersection(Bb).area > 1e-6: return None
            U = unary_union([Aa, Bb]); return [h.intersection(U).area / h.area for _, _, h in H]
        for m, (a, b) in REGISTER.items():
            z = zust(a, b)
            if z is None or not all((v <= 0.001) if c in m else (v >= 0.999) for v, (_, c, _) in zip(z, H)):
                fehler.append(f"Reihe {s['reihe']} Register {m}")
        n = int(round((max(RB) - min(RB)) / schritt))
        for a in RA:
            for k in range(n + 1):
                if zust(a, min(RB) + k * schritt) is None: fehler.append(f"Reihe {s['reihe']} Weg B bei A {a}"); break
        n = int(round((max(RA) - min(RA)) / schritt))
        for b in RB:
            for k in range(n + 1):
                if zust(min(RA) + k * schritt, b) is None: fehler.append(f"Reihe {s['reihe']} Weg A bei B {b}"); break
    return fehler


def teile(INSTR, z0, xw0, xw1, _box=None):
    import cadquery as cq
    out = []
    for s, Ap, Bp, sa, sb in umrisse(INSTR):
        for nm, P, d in (("A", Ap, RUHE[0]), ("B", Bp, RUHE[1])):
            P = translate(P.simplify(0.001), d, 0)
            assert isinstance(P, Polygon) and not P.interiors, f"Registerschieber {nm}: Umriss nicht einfach"
            sol = cq.Workplane("XY").polyline(list(P.exterior.coords)[:-1]).close().extrude(T_SCH).translate((0, 0, z0)).val()
            out.append((f"Registerschieber_{nm}_{s['reihe']}.reihe", sol))
        x0, xl = s["tri"][0][0], s["tri"][-1][0]
        print(f"   Registerschieber Reihe {s['reihe']}: {len(s['tri'])} Tripel; Stimmstock X {x0 - STOCK_ENDE:.1f}..{xl + STOCK_ENDE:.1f}; "
              f"Schlitz B (unten) X {sb + min(RB):.1f}..{sb + max(RB):.1f}, Schlitz A (oben) X {sa + min(RA):.1f}..{sa + max(RA):.1f}")
    x0_, x1_ = bedarf(INSTR)
    print(f"   Registerschieber: Weg X {x0_:.1f}..{x1_:.1f}, Rahmen innen {xw0:.1f}..{xw1:.1f}")
    if x0_ < xw0 - 0.01 or x1_ > xw1 + 0.01: print("   ACHTUNG Registerschieber reichen in die Rahmenwand")
    f = pruefe(INSTR)
    print("   Registerschieber Pruefung:", "alle 6 Register in allen Stimmstoecken sauber, Wege frei" if not f else "FEHLER " + "; ".join(f))
    return out
