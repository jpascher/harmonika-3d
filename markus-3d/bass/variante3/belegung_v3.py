# Freie Bassbelegung fuer Bassteil Variante 3 "traditionell, flacher Einbau" (27.11.2026)
# Die Mechanik dieser Variante wird aus einer Tabelle Knopf -> Klappe gebaut (BASS_T/BEGL_T in mechanik.py); die Achsen
# werden danach automatisch in Reihen hinter den Klappen gelegt. Eine freie Belegung ersetzt diese Tabelle; die Reihen
# legt dann die automatische Verteilung (layout) fest. Wie gebaut bleibt alles unveraendert (gesuchte feste Reihen).
# Klappennamen: H1-H8 Bassklappen (von links), B1-B8 Begleiterklappen, Z Zusatzklappe (bleibt auf ihrem Knopf).
# Knoepfe von links gezaehlt in der Modellansicht (X = L - x), Reihe 1 = A (Front), Reihe 2 = B (Blende).
import os, json
REIHE_NR = {"A": 1, "B": 2}
ART = {"Bass": "Grundbass", "Begleiter": "Begleiter", "Zusatz": "Zusatz"}

NAMEN = {}
def _namen(kl_c, L):
    """Klappennamen von links in der Modellansicht: H1-H8 Bass, B1-B8 Begleiter, Z Zusatzklappe"""
    NAMEN.clear()
    for pre, art in (("H", "Bassklappe_"), ("B", "Begleiterklappe_")):
        ks = sorted((k for k in kl_c if k.startswith(art)), key=lambda k: L - kl_c[k][0])
        for i, k in enumerate(ks, 1): NAMEN[k] = f"{pre}{i}"
def _kid(kl):
    return NAMEN.get(kl, "Z")

def _index(knoepfe, L):
    idx, rueck = {}, {}
    for r in REIHE_NR:
        xs = sorted((x for x, rr in knoepfe if rr == r), key=lambda x: L - x)
        for i, x in enumerate(xs, 1): idx[(r, round(x, 1))] = (REIHE_NR[r], i); rueck[(REIHE_NR[r], i)] = (r, x)
    return idx, rueck

def _naechster(idx, r, x):
    return min(((rr, xx) for rr, xx in idx if rr == r), key=lambda q: abs(q[1] - x))

def anwenden(ach, knoepfe, kl_c, L):
    _namen(kl_c, L)
    idx, rueck = _index(knoepfe, L)
    standard = {}
    for a in ach:
        for r, x in a["kn"]:
            k = idx[_naechster(idx, r, x)]; standard[f"{k[0]}.{k[1]}"] = _kid(a["kl"])
    ex = os.environ.get("BELEGUNG_EXPORT")
    if ex: _exportiere(ex, ach, knoepfe, kl_c, L, idx, standard)
    b = os.environ.get("BASS_BELEGUNG")
    if not b: return ach, False
    import belegung
    m = json.load(open("belegung_modell_v3.json", encoding="utf-8"))
    kopf, zuo = belegung.lies(b)
    canon = {k.upper(): k for k in m["klappen"]}
    zuo = {k: canon.get(v.upper(), v) for k, v in zuo.items()}
    reihen = {int(r): len(v) for r, v in m["knopf_x"].items()}
    if belegung.reihen_aus(kopf, reihen) != reihen:
        raise belegung.BelegungsFehler("Bei Variante 3 ist die Knopfzahl je Reihe fest: " + ", ".join(f"R{r} = {n}" for r, n in sorted(reihen.items())))
    belegung.pruefe(zuo, m["klappen"], reihen)
    if {f"{r}.{i}": v for (r, i), v in zuo.items()} == standard:
        print("Belegung Variante 3: wie gebaut"); return ach, False
    neu = []
    for a in ach:
        kid = _kid(a["kl"])
        kn = [rueck[k] for k, v in sorted(zuo.items()) if v == kid]
        neu.append(dict(art=a["art"], kn=kn, kl=a["kl"]))
    print("Belegung Variante 3:", "; ".join(f"{_kid(a['kl'])}: " + " ".join(f"{REIHE_NR[r]}.{idx[(r, round(x, 1))][1]}" for r, x in a["kn"]) for a in neu))
    return neu, True

def _exportiere(ex, ach, knoepfe, kl_c, L, idx, standard):
    knopf_x = {str(REIHE_NR[r]): sorted(round(L - x, 2) for x, rr in knoepfe if rr == r) for r in REIHE_NR}
    bass = sorted([a for a in ach if a["art"] == "Bass"], key=lambda a: kl_c[a["kl"]][0])
    schraeg = {a["kl"] for a in bass[5:]}                       # Bassklappen 6-8: Schraegachsen, eigene Lage
    gassen = {"HB0": 44.0 + 9.6, "HB1": 44.0 + 6.4, "HB2": 44.0 + 3.2, "HB3": 44.0,
              "BG0": 104.0 + 9.6, "BG1": 104.0 + 6.4, "BG2": 104.0 + 3.2, "BG3": 104.0}
    klappen = {}
    for a in ach:
        kid = _kid(a["kl"]); cx, cy = kl_c[a["kl"]][0], kl_c[a["kl"]][1]
        if a["art"] == "Bass" and a["kl"] in schraeg: gs = ["S" + kid]; gassen["S" + kid] = 20.0 + 2.0 * len([g for g in gassen if g.startswith("S")])
        elif a["art"] == "Bass": gs = ["HB0", "HB1", "HB2", "HB3"]
        elif a["art"] == "Begleiter": gs = ["BG0", "BG1", "BG2", "BG3"]
        else: gs = ["Z0"]; gassen["Z0"] = 140.0
        k = {"ziel": [round(L - cx, 2), round(cy, 2)], "hebel_x": round(L - cx, 2), "gassen": gs,
             "art": ("Grundbass hinten" if a["art"] == "Bass" else "Begleiter " + ("links" if L - cx < L / 2 else "rechts") if a["art"] == "Begleiter" else "Grundbass vorne")}
        if a["art"] == "Zusatz":                                 # Zusatzklappe: Stange im U ueber die Lufttaste, nur ihr Knopf
            xz = [knopf_x[s.split(".")[0]][int(s.split(".")[1]) - 1] for s, v in standard.items() if v == kid]
            k["x_bereich"] = [min(xz + [k["hebel_x"]]) - 1.0, max(xz + [k["hebel_x"]]) + 1.0]
        klappen[kid] = k
    mod = {"modell": "v3", "name": "Variante 3 traditionell", "gehaeuse": [L, 207.0],
           "reihen": {r: len(v) for r, v in knopf_x.items()},
           "reihen_mitte": {r: round(sum(v) / len(v), 2) for r, v in knopf_x.items()},
           "reihen_zentriert": False, "reihen_fest": True, "teilung": 20.0, "knopf_x": knopf_x,
           "knopf_bereich": [min(min(v) for v in knopf_x.values()), max(max(v) for v in knopf_x.values())],
           "reihen_hinweis": "Variante 3: Knopfzahl je Reihe fest (9 / 8); die Achsen werden automatisch in Reihen hinter den Klappen gelegt",
           "knopf_y": {"1": 198.0, "2": 184.0}, "gassen": gassen, "min_luecke": 15.0, "gassen_abstand_min": 0.0,
           "klappen": klappen, "standard": standard}
    json.dump(mod, open(ex, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"Belegungsmodell geschrieben: {ex} ({len(klappen)} Klappen, {len(standard)} Knoepfe)")
    if os.environ.get("BELEGUNG_NUR_EXPORT"): raise SystemExit(0)
