# Freie Bassbelegung fuer das Bassteil Standardmechanik mit 4/4 bzw. 4/5 Helikon (27.11.2026)
# Die Mechanik wird aus den Tabellen BASS / BEGL (Knoepfe -> Klappe) in kugel_bass2.py gebaut; Hebellage und Ebenen
# (Bass 3, Begleiter 2) verteilt das Programm danach selbst. Eine freie Belegung ersetzt nur die Knopflisten dieser
# Tabellen. Klappennamen: H1-H8 Bassklappen, B1-B8 Begleiterklappen (von links in der Grundrisszeichnung);
# bei 4/5 bedient Knopf 1.9 die Zusatzkammer (Z5) mit eigener Mechanik - dieser Knopf bleibt fest.
# Knoepfe von links gezaehlt, Reihe 1 = vordere Reihe (9 Knoepfe), Reihe 2 = 8 Knoepfe.
import os, json

def _namen(BASS, BEGL):
    return [("H", i + 1, t) for i, t in enumerate(BASS)] + [("B", i + 1, t) for i, t in enumerate(BEGL)]

def anwenden(BASS, BEGL, KN_PX, XK, X, var45, Z_BASS, Z_BEGL, L):
    std = {}
    for pre, i, (knl, pxk, pyl) in _namen(BASS, BEGL):
        for rr, px in knl: std[f"{rr}.{KN_PX[rr].index(px) + 1}"] = f"{pre}{i}"
    if var45: std[f"1.{KN_PX[1].index(261.5) + 1}"] = "Z5"
    ex = os.environ.get("BELEGUNG_EXPORT")
    if ex: _exportiere(ex, BASS, BEGL, KN_PX, XK, X, var45, Z_BASS, Z_BEGL, L, std)
    b = os.environ.get("BASS_BELEGUNG")
    if not b: return BASS, BEGL
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import belegung
    m = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"belegung_modell_helikon{'45' if var45 else '44'}.json"), encoding="utf-8"))
    kopf, zuo = belegung.lies(b)
    canon = {k.upper(): k for k in m["klappen"]}
    zuo = {k: canon.get(v.upper(), v) for k, v in zuo.items()}
    reihen = {int(r): len(v) for r, v in m["knopf_x"].items()}
    if belegung.reihen_aus(kopf, reihen) != reihen:
        raise belegung.BelegungsFehler("Beim Standard-Helikon ist die Knopfzahl je Reihe fest: R1 = 9, R2 = 8")
    belegung.pruefe(zuo, m["klappen"], reihen)
    if {f"{r}.{i}": v for (r, i), v in zuo.items()} == std:
        print("Belegung Helikon: wie gebaut"); return BASS, BEGL
    if var45 and zuo.get((1, KN_PX[1].index(261.5) + 1)) != "Z5":
        raise belegung.BelegungsFehler("Bei 4/5 bleibt Knopf 1.9 auf der Zusatzkammer (Z5)")
    def knl(name): return [(r, KN_PX[r][i - 1]) for (r, i), v in sorted(zuo.items()) if v == name]
    nb = [(knl(f"H{i + 1}"), pxk, pyl) for i, (_, pxk, pyl) in enumerate(BASS)]
    ng = [(knl(f"B{i + 1}"), pxk, pyl) for i, (_, pxk, pyl) in enumerate(BEGL)]
    print("Belegung Helikon:", "; ".join(f"{p}{i}: " + " ".join(f"{r}.{KN_PX[r].index(px) + 1}" for r, px in t[0]) for p, i, t in _namen(nb, ng)))
    return nb, ng

def _exportiere(ex, BASS, BEGL, KN_PX, XK, X, var45, Z_BASS, Z_BEGL, L, std):
    knopf_x = {str(r): [round(XK(px), 2) for px in KN_PX[r]] for r in (1, 2)}
    gassen = {f"HB{j}": 40.0 + 6.0 * j for j in range(len(Z_BASS))}
    gassen.update({f"BG{j}": 110.0 + 6.0 * j for j in range(len(Z_BEGL))})
    klappen = {}
    for pre, i, (knl, pxk, pyl) in _namen(BASS, BEGL):
        klappen[f"{pre}{i}"] = {"ziel": [round(X(pxk), 2), 60.0 if pre == "H" else 130.0], "hebel_x": round(X(pxk), 2),
                                "gassen": [g for g in gassen if g.startswith("HB" if pre == "H" else "BG")],
                                "art": "Grundbass hinten" if pre == "H" else ("Begleiter links" if X(pxk) < L / 2 else "Begleiter rechts")}
    if var45:
        x5 = round(XK(261.5), 2)
        gassen["Z5"] = 170.0
        klappen["Z5"] = {"ziel": [x5, 160.0], "hebel_x": x5, "gassen": ["Z5"], "art": "Grundbass vorne", "x_bereich": [x5 - 1, x5 + 1]}
    mod = {"modell": "helikon45" if var45 else "helikon44", "name": f"Standard Helikon {'4/5' if var45 else '4/4'}", "gehaeuse": [L, 207.0],
           "reihen": {r: len(v) for r, v in knopf_x.items()}, "reihen_mitte": {r: round(sum(v) / len(v), 2) for r, v in knopf_x.items()},
           "reihen_zentriert": False, "reihen_fest": True, "teilung": round(XK(128.5) - XK(109.5), 2), "knopf_x": knopf_x,
           "knopf_bereich": [min(min(v) for v in knopf_x.values()), max(max(v) for v in knopf_x.values())],
           "reihen_hinweis": "Standard Helikon: Knopfzahl je Reihe fest (9 / 8); Hebellage und Ebenen verteilt das Programm",
           "knopf_y": {"1": 198.0, "2": 184.0}, "gassen": gassen, "min_luecke": 3.0, "gassen_abstand_min": 0.0,
           "klappen": klappen, "standard": std}
    json.dump(mod, open(ex, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"Belegungsmodell geschrieben: {ex} ({len(klappen)} Klappen, {len(std)} Knoepfe)")
    if os.environ.get("BELEGUNG_NUR_EXPORT"): raise SystemExit(0)
