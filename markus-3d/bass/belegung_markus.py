# Freie Bassbelegung fuer den Markus-Bassteil (27.11.2026)
# Der Markus-Bass liest Achsen, Lagerboecke, Klappenhebel und Schubstangen aus der Mechanikzeichnung (mech.dxf). Die
# Achsen bleiben deshalb wie gezeichnet: jede Klappe hat ihre feste Achse. Frei ist, welcher Knopf auf welche Achse
# (= Klappe) greift; zwei Knoepfe auf derselben Klappe sind gekoppelt. Ein Knopf, der auf seiner gezeichneten Achse
# bleibt, wird nicht veraendert - die Standardbelegung ergibt genau das gepruefte Modell.
#
# Koordinaten in belegung_modell_markus.json: X wie in der Modellansicht (L - x, Knoepfe von links gezaehlt), Y wie im Modell.
# Reihe 1 = A (vorderste, Taschenboden), 2 = B, 3 = C.
import os, json, math
REIHE_NR = {"A": 1, "B": 2, "C": 3}

def _knopf_index(knoepfe, L):
    """(Reihe-Buchstabe, Modell-X) -> (Reihennummer, Knopf von links) ; von links = aufsteigend in L - x"""
    idx = {}
    for r in REIHE_NR:
        xs = sorted((x for x, rr in knoepfe if rr == r), key=lambda x: L - x)
        for i, x in enumerate(xs, 1): idx[(r, round(x, 1))] = (REIHE_NR[r], i)
    return idx

def _klappen_id(name):
    n = name.rsplit("_", 1)[-1]
    return ("B" if name.startswith("Begleiter") else "K") + n

def _y_auf(achse, x):
    (x0, y0), (x1, y1) = achse
    if abs(x1 - x0) < 1e-9: return (y0 + y1) / 2
    t = (x - x0) / (x1 - x0); return y0 + t * (y1 - y0)

def anwenden(stangen, knoepfe, achsen, fuss, L):
    b = os.environ.get("BASS_BELEGUNG")
    if not b: return stangen
    import belegung
    m = json.load(open("belegung_modell_markus.json", encoding="utf-8"))
    kopf, zuo = belegung.lies(b)
    canon = {k.upper(): k for k in m["klappen"]}
    zuo = {k: canon.get(v.upper(), v) for k, v in zuo.items()}
    reihen = {int(r): len(v) for r, v in m["knopf_x"].items()}
    if belegung.reihen_aus(kopf, reihen) != reihen:
        raise belegung.BelegungsFehler("Beim Markus-Bass ist die Knopfzahl je Reihe fest: " + ", ".join(f"R{r} = {n}" for r, n in sorted(reihen.items())))
    belegung.pruefe(zuo, m["klappen"], reihen)
    idx = _knopf_index(knoepfe, L)
    neu, geaendert = [], []
    belegt = {}                                            # Achse -> gx der Schenkel (fuer Mindestabstand)
    plan = []
    for (P, r, Xk) in stangen:
        k = idx.get((r, round(Xk, 1)))
        if k not in zuo: geaendert.append(f"{k[0]}.{k[1]} blind"); continue
        ai = m["klappen"][zuo[k]]["achse"]
        aj = min(range(len(achsen)), key=lambda j: fuss(P, achsen[j])[1])
        plan.append((P, r, Xk, k, ai, aj))
        if ai == aj: belegt.setdefault(ai, []).append(P[0])
    for (P, r, Xk, k, ai, aj) in plan:
        if ai == aj: neu.append((P, r, Xk)); continue
        (a0, a1) = achsen[ai]; lo, hi = min(a0[0], a1[0]) + 5.0, max(a0[0], a1[0]) - 5.0
        gx = min(max(P[0], lo), hi)                        # Schenkel auf der Knopf-X wie gezeichnet, innerhalb der Achse
        for _ in range(8):                                  # nicht auf einen anderen Schenkel derselben Achse
            nah = [g for g in belegt.get(ai, []) if abs(g - gx) < 5.0]
            if not nah: break
            gx = nah[0] + (5.0 if gx >= nah[0] and nah[0] + 5.0 <= hi else -5.0)
        belegt.setdefault(ai, []).append(gx)
        neu.append(((gx, _y_auf(achsen[ai], gx)), r, Xk))
        geaendert.append(f"{k[0]}.{k[1]} -> {zuo[k]} (Achse {ai + 1}, Schenkel X {L - gx:.1f})")
    print("Belegung Markus:", "; ".join(geaendert) if geaendert else "wie gezeichnet")
    return neu

def exportiere(arm_info, zuordnung, kh_liste, kh_namen, kl_c, achsen, knoepfe, REIHEN, L, B):
    ex = os.environ.get("BELEGUNG_EXPORT")
    if not ex: return
    idx = _knopf_index(knoepfe, L)
    kc = dict(kl_c)
    pa_von = {kh_namen[i]: pa for i, (pa, pk) in enumerate(kh_liste)}
    # Gassen: waagrechte Achsen auf gleicher Hoehe teilen sich eine Linie, schraege Achsen bekommen eine eigene
    gassen, g_von = {}, {}
    for ai, (a0, a1) in enumerate(achsen):
        if ai not in zuordnung: continue
        schraeg = abs(a1[1] - a0[1]) > 1.0
        ym = round((a0[1] + a1[1]) / 2, 1)
        g = next((n for n, y in gassen.items() if not schraeg and not n.startswith("S") and abs(y - ym) < 1.0), None)
        if g is None:
            g = (f"S{ai + 1}" if schraeg else f"G{len([n for n in gassen if n.startswith('G')]) + 1}"); gassen[g] = ym
        g_von[ai] = g
    klappen, standard = {}, {}
    for ai, lst in sorted(zuordnung.items()):
        kn_, ton_, _, hn_ = lst[0]
        kid = _klappen_id(kn_)
        cx, cy = kc[kn_]
        pa = pa_von.get(hn_, (cx, cy))
        (a0, a1) = achsen[ai]
        art = ("Begleiter " + ("links" if L - cx < L / 2 else "rechts")) if kn_.startswith("Begleiter") else \
              ("Grundbass hinten" if cy < 100 else "Grundbass vorne")
        klappen[kid] = {"ziel": [round(L - cx, 2), round(cy, 2)], "hebel_x": round(L - pa[0], 2), "gassen": [g_von[ai]],
                        "art": art, "ton": ton_, "achse": ai,
                        "x_bereich": [round(L - max(a0[0], a1[0]), 1), round(L - min(a0[0], a1[0]), 1)]}
    for (ai, _n, gx, gy, r, Xk) in arm_info:
        k = idx[(r, round(Xk, 1))]
        standard[f"{k[0]}.{k[1]}"] = _klappen_id(zuordnung[ai][0][0])
    knopf_x = {str(REIHE_NR[r]): sorted(round(L - x, 2) for x, rr in knoepfe if rr == r) for r in REIHE_NR}
    # x_bereich so weit, dass die gezeichnete Belegung immer passt (Schenkel liegen teils neben der Knopf-X)
    for kid, k in klappen.items():
        xs = [knopf_x[s.split(".")[0]][int(s.split(".")[1]) - 1] for s, v in standard.items() if v == kid] + [k["hebel_x"]]
        k["x_bereich"] = [min(k["x_bereich"][0], min(xs)), max(k["x_bereich"][1], max(xs))]
    # kleinste Luecke zwischen Achsen auf derselben Linie (wie gezeichnet)
    ber = {}
    for kid, k in klappen.items():
        xs = [knopf_x[s.split(".")[0]][int(s.split(".")[1]) - 1] for s, v in standard.items() if v == kid] + [k["hebel_x"]]
        ber.setdefault(k["gassen"][0], []).append((min(xs), max(xs)))
    luecken = [b2[0] - b1[1] for v in ber.values() for b1, b2 in zip(sorted(v), sorted(v)[1:])]
    min_l = max(0.0, min([12.0] + [round(l - 0.05, 1) for l in luecken]))
    mod = {"modell": "markus", "name": "Markus", "gehaeuse": [L, B],
           "reihen": {str(REIHE_NR[r]): sum(1 for _, rr in knoepfe if rr == r) for r in REIHE_NR},
           "reihen_mitte": {r: round(sum(v) / len(v), 2) for r, v in knopf_x.items()},
           "reihen_zentriert": False, "reihen_fest": True, "teilung": 20.0, "knopf_x": knopf_x,
           "knopf_bereich": [min(min(v) for v in knopf_x.values()), max(max(v) for v in knopf_x.values())],
           "reihen_hinweis": "Markus-Bass: Achsen, Boecke und Klappenhebel wie gezeichnet - frei ist, welcher Knopf welche Klappe oeffnet; Knopfzahl je Reihe fest",
           "knopf_y": {str(REIHE_NR[r]): round(REIHEN[r][1], 2) for r in REIHE_NR},
           "gassen": gassen, "min_luecke": min_l, "gassen_abstand_min": 0.0,
           "klappen": klappen, "standard": standard}
    json.dump(mod, open(ex, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"Belegungsmodell geschrieben: {ex} ({len(klappen)} Klappen, {len(gassen)} Gassen, {len(standard)} Knoepfe)")
    if os.environ.get("BELEGUNG_NUR_EXPORT"): raise SystemExit(0)
