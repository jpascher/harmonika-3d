# Achsen (meist ein "H": Achse mit angeschweisstem Knopf-Schenkel und Klappenhebel) fuer das Schweissen vorbereiten
# (Johann 27.11.2026): alle Draehte gestreckt, d. h. ohne Biegungen, mit Biegeradius auf die Zuschnittlaenge
# abgewickelt; dazu eine Fraesschablone - Nuten in einer Unterlage, in die die gestreckten Teile in der richtigen
# Lage eingelegt und verschweisst werden, mit gravierter Nummer daneben. Gebogen wird nach dem Schweissen.
#
#   python3 achsen_lehre.py modell.step zielordner [--ri 2.4] [--tafel 600x300]
#
# Erkennt Drahtteile im Modell (nur Zylinder/Kugeln/Endflaechen mit Draht-Durchmesser), ihre Mittellinien und welche
# Draehte an welcher Achse sitzen (Abstand < 0,5 mm). Ergebnis:
#   Schweisslehre_Tafel<n>.dxf  Layer Nut_Kontur_B<b>_T<t> (Taschen), Nut_Mitte (Mittellinien, z. B. Nutfraeser = Breite),
#                               Biegemarke (Striche quer zur Nut = Biegebeginn), Gravur_Nummer, Platte
#   Zuschnitt_Biegen.csv        je Draht: Nummer, Zuschnittlaenge, Biegungen (Lage ab Anfang, Winkel, Radius)
import sys, os, re, math, argparse, csv
import cadquery as cq, ezdxf
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "diskant", "disk"))
import gravur                                                    # Einstrich-Schrift

AUS = re.compile(r"schraube|feder|schubstange|bolzen|stift|niete|gabel|gelenk", re.I)

def blaetter(a, loc=None, pfad=""):
    loc = (loc * a.loc) if loc is not None else a.loc
    p = (pfad + "/" + a.name) if pfad else a.name
    out = []
    if a.obj is not None:
        objs = a.obj.vals() if isinstance(a.obj, cq.Workplane) else [a.obj]
        for o in objs:
            if isinstance(o, cq.Shape):
                for s in o.moved(loc).Solids(): out.append((p.split("/")[-1], s))
    for c in a.children: out += blaetter(c, loc, p)
    return out

def mittellinie(s, rdraht):
    """Mittellinie eines Drahts aus seinen Zylinderflaechen (scharfe Ecken wie im Modell) oder None."""
    segs = []
    for f in s.Faces():
        g = f.geomType()
        if g == "PLANE": continue
        if g == "SPHERE":
            if abs(f._geomAdaptor().Sphere().Radius() - rdraht) > 0.05: return None
            continue
        if g != "CYLINDER": return None
        cy = f._geomAdaptor().Cylinder()
        if abs(cy.Radius() - rdraht) > 0.05: return None
        ax = cy.Axis(); o = ax.Location(); d = ax.Direction()
        O = cq.Vector(o.X(), o.Y(), o.Z()); D = cq.Vector(d.X(), d.Y(), d.Z())
        ts = [(cq.Vector(*v.toTuple()) - O).dot(D) for v in f.Vertices()]
        if not ts:
            bb = f.BoundingBox(); ts = [(cq.Vector(bb.xmin, bb.ymin, bb.zmin) - O).dot(D), (cq.Vector(bb.xmax, bb.ymax, bb.zmax) - O).dot(D)]
        a, b = min(ts), max(ts)
        if b - a < 0.05: continue
        segs.append((O + D * a, O + D * b))
    if not segs: return None
    # gleiche Gerade (z. B. geteilte Zylinderflaeche) zusammenfassen
    zus = []
    for p, q in segs:
        d = (q - p).normalized()
        for k, (a, b) in enumerate(zus):
            e = (b - a).normalized()
            if abs(abs(d.dot(e)) - 1) < 1e-4 and ((p - a) - e * (p - a).dot(e)).Length < 0.05:
                ts = [0.0, (b - a).Length, (p - a).dot(e), (q - a).dot(e)]
                zus[k] = (a + e * min(ts), a + e * max(ts)); break
        else: zus.append((p, q))
    # Splitter kuerzer als der Drahtdurchmesser (Reste vom Verschneiden mit der Achse) weglassen, wenn mehr da ist
    lang = [sg for sg in zus if (sg[1] - sg[0]).Length >= 2 * rdraht]
    segs = lang if lang else zus
    # Segmente zu einem Zug verketten (Ecken liegen in Kugelmitten bzw. an gemeinsamen Enden)
    rest = segs[1:]; zug = [segs[0][0], segs[0][1]]
    while rest:
        best = None
        for i, (p, q) in enumerate(rest):
            for ende, (u, v) in (("hinten", (p, q)), ("hinten", (q, p)), ("vorne", (q, p)), ("vorne", (p, q))):
                ref = zug[-1] if ende == "hinten" else zug[0]
                dd = (u - ref).Length if ende == "hinten" else (v - ref).Length
                if best is None or dd < best[0]: best = (dd, i, ende, u, v)
        dd, i, ende, u, v = best
        if dd > 3 * rdraht + 0.5: return None                     # nicht zusammenhaengend
        if ende == "hinten":
            zug[-1] = (zug[-1] + u) * 0.5; zug.append(v)
        else:
            zug[0] = (zug[0] + v) * 0.5; zug.insert(0, u)
        rest.pop(i)
    return zug

def _ecken(zug, R):
    """Ablenkwinkel und Biegeradius (Mittellinie) je Ecke; bei kurzen Schenkeln wird der Radius kleiner."""
    l = [(zug[i + 1] - zug[i]).Length for i in range(len(zug) - 1)]
    out = []
    for i in range(1, len(zug) - 1):
        a = (zug[i] - zug[i - 1]).normalized(); b = (zug[i + 1] - zug[i]).normalized()
        t = math.acos(max(-1.0, min(1.0, a.dot(b))))
        if t < 1e-3: out.append((0.0, R)); continue
        platz = min(l[i - 1] if i - 1 == 0 else l[i - 1] / 2, l[i] if i == len(zug) - 2 else l[i] / 2)
        r = min(R, max(0.3, platz) / math.tan(min(t, math.radians(179)) / 2))
        out.append((t, r))
    return l, out

def abwicklung(zug, R):
    """Zuschnittlaenge mit Biegeradius R (Mittellinie) und Lage jeder Biegung (Beginn, Winkel, Radius)."""
    l, ecken = _ecken(zug, R)
    kuerz = [r * math.tan(t / 2) for t, r in ecken]
    pos = []; s = 0.0
    for i, (t, r) in enumerate(ecken):
        s += l[i] - (kuerz[i - 1] if i > 0 else 0) - kuerz[i]
        if t > 1e-3: pos.append((s, math.degrees(t), r))
        s += r * t
    L = sum(l) - 2 * sum(kuerz) + sum(r * t for t, r in ecken)
    return L, pos

def dev_param(zug, R, P):
    """Abgewickelte Lage (mm ab Anfang) des Mittellinienpunkts, der P am naechsten liegt."""
    best = None
    for i in range(len(zug) - 1):
        a, b = zug[i], zug[i + 1]; ab = b - a; L = ab.Length
        t = max(0.0, min(1.0, (P - a).dot(ab) / (L * L))) if L > 0 else 0.0
        d = (a + ab * t - P).Length
        if best is None or d < best[0]: best = (d, i, t * L)
    _, i, tl = best
    l, ecken = _ecken(zug, R)
    s = 0.0
    for j in range(i):
        t, r = ecken[j]; k = r * math.tan(t / 2)
        s += l[j] - (ecken[j - 1][1] * math.tan(ecken[j - 1][0] / 2) if j > 0 else 0) - k + r * t
    k_vor = ecken[i - 1][1] * math.tan(ecken[i - 1][0] / 2) if i > 0 else 0.0
    return s + max(0.0, tl - k_vor)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step"); ap.add_argument("ordner")
    ap.add_argument("--d", type=float, default=2.4, help="Drahtdurchmesser")
    ap.add_argument("--ri", type=float, default=2.4, help="Biege-Innenradius")
    ap.add_argument("--tafel", default="600x300"); ap.add_argument("--spiel", type=float, default=0.2)
    ap.add_argument("--tiefe", type=float, default=1.5)
    ap.add_argument("--uebermass", type=float, default=10.0, help="Klappenhebel ueber die Klappenmitte hinaus (Johann 27.11.)")
    a = ap.parse_args()
    os.makedirs(a.ordner, exist_ok=True)
    R = a.ri + a.d / 2; rd = a.d / 2
    teile = blaetter(cq.Assembly.importStep(a.step))
    draht = {}
    for n, s in teile:
        if AUS.search(n): continue
        z = mittellinie(s, rd)
        if z: draht[n] = (s, z)
    achsen = sorted([n for n in draht if re.search(r"(^|_)Achse(_|$)", n) and not n.lower().startswith("feder")],
                    key=lambda n: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", n)])
    gruppen = []; vergeben = set(achsen)
    for an in achsen:
        s_a, z_a = draht[an]; arme = []
        for n, (s, z) in draht.items():
            if n in vergeben: continue
            if s_a.distance(s) < 0.5:
                arme.append(n); vergeben.add(n)
        gruppen.append((an, arme))
    # --- Lehren je Achse in Ebenen-Koordinaten (Achse = x-Achse, Arme senkrecht) ---
    zeilen = [["Nummer", "Teil im Modell", "Achse", "Zuschnitt_mm", "Biegungen (Beginn ab Anfang mm / Winkel Grad / Innenradius mm)", "Lage an der Achse mm"]]
    lehren = []
    for gi, (an, arme) in enumerate(gruppen, 1):
        nr = f"A{gi}"
        s_a, z_a = draht[an]; La, pa = abwicklung(z_a, R)
        linien = [LineString([(0, 0), (La, 0)])]; marken = []
        for s0, w, b in pa: marken.append(((s0, 0), "x"))
        zeilen.append([nr, an, nr, f"{La:.1f}", " ".join(f"{p:.1f}/{w:.0f}/R{r - rd:.1f}" for p, w, r in pa) or "gerade", "-"])
        ref = None
        for k, wn in enumerate(arme, 1):
            s_w, z_w = draht[wn]
            def _d(P):                                            # Abstand zur Achs-Mittellinie
                return min(((P - (z_a[i] + (z_a[i + 1] - z_a[i]) * max(0, min(1, (P - z_a[i]).dot(z_a[i + 1] - z_a[i]) / max(1e-9, (z_a[i + 1] - z_a[i]).Length ** 2))))).Length)
                           for i in range(len(z_a) - 1))
            # Stuecke des Arms, die ganz in der Achse stecken (Verschneidungsreste), abschneiden
            while len(z_w) > 2 and _d(z_w[0]) < 1.4 * rd and _d(z_w[1]) < 1.4 * rd: z_w = z_w[1:]
            while len(z_w) > 2 and _d(z_w[-1]) < 1.4 * rd and _d(z_w[-2]) < 1.4 * rd: z_w = z_w[:-1]
            Lw, pw = abwicklung(z_w, R)
            # Beruehrpunkt: naechste Punkte der Mittellinien
            # 3D-naechster Punkt: auf dem Arm abtasten
            pts = []
            for i in range(len(z_w) - 1):
                for t in range(0, 21):
                    pts.append(z_w[i] + (z_w[i + 1] - z_w[i]) * (t / 20))
            def dist_achse(P):
                return min((((P - (z_a[i] + (z_a[i + 1] - z_a[i]) * max(0, min(1, (P - z_a[i]).dot(z_a[i + 1] - z_a[i]) / max(1e-9, (z_a[i + 1] - z_a[i]).Length ** 2))))).Length, i)
                            for i in range(len(z_a) - 1)))
            Pw = min(pts, key=lambda P: dist_achse(P)[0])
            sa = dev_param(z_a, R, Pw); uw = dev_param(z_w, R, Pw)
            # Seite: Richtung vom Beruehrpunkt zum laengeren Armteil, quer zur Achse
            ia = dist_achse(Pw)[1]; t_a = (z_a[ia + 1] - z_a[ia]).normalized()
            fern = z_w[-1] if (Lw - uw) >= uw else z_w[0]
            q = fern - Pw; q = q - t_a * q.dot(t_a)
            if ref is None: ref = q.normalized() if q.Length > 1e-6 else cq.Vector(0, 0, 1)
            seite = 1 if q.dot(ref) >= 0 else -1
            lang, kurz = (Lw - uw, uw) if (Lw - uw) >= uw else (uw, Lw - uw)
            ue = a.uebermass if re.search(r"klappenhebel", wn, re.I) else 0.0   # freies Ende = Klappenmitte, dort Uebermass
            lang += ue; Lw += ue
            linien.append(LineString([(sa, -seite * kurz), (sa, seite * lang)]))
            # Biegemarken auf dem Arm (abgewickelte Lage ab dem Anfang, der hier am Ende 'kurz' liegt)
            for p0, w, b in pw:
                y = (p0 - uw) if (Lw - uw) >= uw else (uw - p0)
                marken.append(((sa, seite * y), "y"))
            zeilen.append([f"{nr}-{k}", wn + (f" (inkl. {ue:g} mm Uebermass ueber die Klappenmitte)" if ue else ""), nr, f"{Lw:.1f}",
                           " ".join(f"{p:.1f}/{w:.0f}/R{r - rd:.1f}" for p, w, r in pw) or "gerade", f"{sa:.1f}"])
        lehren.append((nr, linien, marken))
    with open(os.path.join(a.ordner, "Zuschnitt_Biegen.csv"), "w", newline="", encoding="utf-8") as f:
        csv.writer(f, delimiter=";").writerows(zeilen)
    # --- auf Tafeln setzen (Regale) ---
    TW, TH = (float(x) for x in a.tafel.lower().split("x")); rand = 8.0; luft = 8.0
    b_nut = a.d + a.spiel
    stuecke = []
    for nr, linien, marken in lehren:
        nut = unary_union([l.buffer(b_nut / 2 + 0.0, cap_style=1) for l in linien])
        zuege, h = gravur.text_linien(nr, 4.0)
        bx = nut.bounds
        # Nummer links vor der Achse
        tx, ty = bx[0] - h - 4.0, -2.0
        zuege = [[(x + tx, y + ty) for x, y in z] for z in zuege]
        alles = unary_union([nut, box(tx, ty, tx + h, ty + 4.0)])
        stuecke.append({"nr": nr, "linien": linien, "marken": marken, "nut": nut, "text": zuege, "bounds": alles.bounds})
    stuecke.sort(key=lambda s: -(s["bounds"][2] - s["bounds"][0]))
    tafeln = [[]]; x = rand; y = rand; zeile_h = 0.0
    for st in stuecke:
        b = st["bounds"]; w, h = b[2] - b[0], b[3] - b[1]
        if w > TW - 2 * rand: raise SystemExit(f"{st['nr']} ({w:.0f} mm) ist laenger als die Tafel")
        if x + w > TW - rand: x = rand; y += zeile_h + luft; zeile_h = 0.0
        if y + h > TH - rand:
            tafeln.append([]); x = rand; y = rand; zeile_h = 0.0
        st["dx"], st["dy"] = x - b[0], y - b[1]
        tafeln[-1].append(st); x += w + luft; zeile_h = max(zeile_h, h)
    for ti, taf in enumerate(tafeln, 1):
        doc = ezdxf.new(setup=True); doc.units = ezdxf.units.MM; m = doc.modelspace()
        lay_nut = f"Nut_Kontur_B{b_nut:.1f}_T{a.tiefe:.1f}".replace(".", ",")
        for ln, c in ((lay_nut, 7), ("Nut_Mitte", 5), ("Biegemarke", 3), ("Gravur_Nummer", 6), ("Platte", 8), ("Text", 2)): doc.layers.add(ln, color=c)
        m.add_lwpolyline([(0, 0), (TW, 0), (TW, TH), (0, TH)], close=True, dxfattribs={"layer": "Platte"})
        for st in taf:
            tr = lambda g: affinity.translate(g, st["dx"], st["dy"])
            for p in (st["nut"].geoms if hasattr(st["nut"], "geoms") else [st["nut"]]):
                p = tr(p); m.add_lwpolyline(list(p.exterior.coords), close=True, dxfattribs={"layer": lay_nut})
                for i in p.interiors: m.add_lwpolyline(list(i.coords), close=True, dxfattribs={"layer": lay_nut})
            for l in st["linien"]:
                l = tr(l); m.add_line(l.coords[0], l.coords[-1], dxfattribs={"layer": "Nut_Mitte"})
            for (mx, my), r in st["marken"]:
                mx += st["dx"]; my += st["dy"]; e = b_nut / 2 + 2.0
                if r == "x": m.add_line((mx, my - e), (mx, my + e), dxfattribs={"layer": "Biegemarke"})
                else: m.add_line((mx - e, my), (mx + e, my), dxfattribs={"layer": "Biegemarke"})
            for z in st["text"]:
                m.add_lwpolyline([(x_ + st["dx"], y_ + st["dy"]) for x_, y_ in z], dxfattribs={"layer": "Gravur_Nummer"})
        m.add_text(f"Schweisslehre Achsen, Tafel {ti}/{len(tafeln)}: Nuten {b_nut:g} mm breit, {a.tiefe:g} mm tief; Draht {a.d:g} mm "
                   f"gestreckt (Biege-Innenradius {a.ri:g} mm), Striche = Biegebeginn; Zuschnitt siehe Zuschnitt_Biegen.csv",
                   height=3.0, dxfattribs={"layer": "Text"}).set_placement((0, TH + 4))
        doc.saveas(os.path.join(a.ordner, f"Schweisslehre_Tafel{ti}.dxf"))
    print(f"Achsen-Schweisslehre: {len(lehren)} Achsen mit {sum(len(g[1]) for g in gruppen)} Armen auf {len(tafeln)} Tafel(n) "
          f"{TW:g} x {TH:g} mm; Draehte gesamt {len(draht)}")

if __name__ == "__main__":
    main()
