# Einstrich-Schrift fuer Gravuren (Hebelnummern) und Platzsuche im Teil (Johann 27.11.2026)
# Ziffern, Bindestrich und Buchstaben R/S/T als offene Polylinien in einem Feld 0,6 x 1 (Hoehe 1). CamBam graviert
# sie direkt (Gravieren auf der Linie), ohne Schriftart.
import math
from shapely.geometry import Polygon, LineString, Point, box
from shapely import affinity

ZEICHEN = {
    "0": [[(0, 0), (0.6, 0), (0.6, 1), (0, 1), (0, 0)]],
    "1": [[(0.15, 0.8), (0.35, 1), (0.35, 0)], [(0.1, 0), (0.6, 0)]],
    "2": [[(0, 1), (0.6, 1), (0.6, 0.5), (0, 0.5), (0, 0), (0.6, 0)]],
    "3": [[(0, 1), (0.6, 1), (0.6, 0), (0, 0)], [(0.1, 0.5), (0.6, 0.5)]],
    "4": [[(0, 1), (0, 0.45), (0.6, 0.45)], [(0.45, 0.7), (0.45, 0)]],
    "5": [[(0.6, 1), (0, 1), (0, 0.5), (0.6, 0.5), (0.6, 0), (0, 0)]],
    "6": [[(0.6, 1), (0, 1), (0, 0), (0.6, 0), (0.6, 0.5), (0, 0.5)]],
    "7": [[(0, 1), (0.6, 1), (0.2, 0)]],
    "8": [[(0, 0), (0.6, 0), (0.6, 1), (0, 1), (0, 0)], [(0, 0.5), (0.6, 0.5)]],
    "9": [[(0, 0), (0.6, 0), (0.6, 1), (0, 1), (0, 0.5), (0.6, 0.5)]],
    "-": [[(0.1, 0.5), (0.5, 0.5)]],
    "R": [[(0, 0), (0, 1), (0.6, 1), (0.6, 0.5), (0, 0.5), (0.6, 0)]],
}
ABSTAND = 0.35          # Zeichenabstand (in Schrifthoehen)

def text_linien(text, hoehe):
    """Liste offener Polylinien (Punktlisten), Text links unten bei (0, 0), Hoehe = hoehe."""
    out = []; x = 0.0
    for ch in text:
        for zug in ZEICHEN.get(ch, []):
            out.append([((x + px) * hoehe, py * hoehe) for px, py in zug])
        x += 0.6 + ABSTAND
    return out, (x - ABSTAND) * hoehe

def platziere(teil, text, hoehe=2.5, frei=0.8, sperr=None):
    """Text so ins Teil legen, dass er mit 'frei' mm Abstand ganz im Material liegt und 'sperr' (Bohrungen,
    Biegelinien) nicht beruehrt. Sucht Lage und Drehung (laengs der laengsten Teilkanten); gibt Polylinien
    oder None zurueck (dann kleinere Schrift versuchen)."""
    for h in (hoehe, hoehe * 0.8, hoehe * 0.6):
        linien, breite = text_linien(text, h)
        feld = teil.buffer(-frei)
        if sperr is not None and not sperr.is_empty: feld = feld.difference(sperr)
        if feld.is_empty: continue
        # Richtungen: Kanten des Umrisses, nach Laenge sortiert
        co = list(teil.exterior.coords)
        kanten = sorted(((math.dist(co[i], co[i + 1]), math.degrees(math.atan2(co[i + 1][1] - co[i][1], co[i + 1][0] - co[i][0])))
                         for i in range(len(co) - 1)), reverse=True)
        winkel = []
        for _, w in kanten[:6] + [(0, 0.0), (0, 90.0)]:
            w = (w + 90) % 180 - 90                              # Text nie auf dem Kopf
            if all(abs(w - v) > 2 for v in winkel): winkel.append(w)
        rahmen = box(0, 0, breite, h)
        best = None
        for w in winkel:
            r = affinity.rotate(rahmen, w, origin=(0, 0))
            bx = r.bounds
            minx, miny, maxx, maxy = feld.bounds
            schritt = 0.5
            y = miny - bx[1]
            while y + bx[3] <= maxy + 1e-9:
                x = minx - bx[0]
                while x + bx[2] <= maxx + 1e-9:
                    rr = affinity.translate(r, x, y)
                    if feld.contains(rr):
                        # moeglichst weit innen: Abstand der Mitte zum Rand
                        wert = teil.exterior.distance(rr.centroid)
                        if best is None or wert > best[0]: best = (wert, w, x, y)
                    x += schritt
                y += schritt
        if best:
            _, w, x, y = best
            return [[(lambda p: (p.x, p.y))(affinity.translate(affinity.rotate(Point(px, py), w, origin=(0, 0)), x, y))
                     for px, py in zug] for zug in linien], h
    return None, None

def biegemarken(teil, linien, d=1.0, rand=1.5):
    """Je Biegelinie zwei Bohrungen d (Mitte), 'rand' mm innerhalb der Kontur an beiden Enden der Linie im Teil."""
    out = []
    for L in linien:
        s = L.intersection(teil)
        stuecke = [g for g in (s.geoms if hasattr(s, "geoms") else [s]) if g.geom_type == "LineString" and g.length > 2 * rand + d]
        for g in stuecke:
            for t in (rand + d / 2, g.length - rand - d / 2):
                p = g.interpolate(t)
                if teil.buffer(-d / 2 - 0.3).contains(p): out.append((p.x, p.y))
    return out
