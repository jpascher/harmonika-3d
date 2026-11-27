# Freie Bassbelegung fuer alle Bassteile nach dem Baukasten (Eduard, Gerhard, Andreas, Marie 38; 27.11.2026)
# Wird von mech_<modell>.py nach dem Aufbau der Achstabelle aufgerufen:
#   ACHSEN, KNOPF_X, HEBEL_WEG = belegung_hook.anwenden("eduard", "Eduard Winkelbass", ACHSEN, kn, KNOPF_X, HEBEL_WEG, gehaeuse=(L, B))
# - BELEGUNG_EXPORT=<datei.json>: schreibt aus der gebauten Achstabelle die Modelldatei (Klappen, Gassen, Knopfreihen,
#   Belegung wie gebaut) - fuer die Webseite "Bassbelegung zuordnen" und die Pruefung in der Automatik.
# - BASS_BELEGUNG=<belegungsdatei>: ersetzt die Achstabelle durch die freie Belegung (Verteilung in belegung.py).
# Ohne beide Variablen bleibt alles wie gebaut.
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import belegung

def reihen(reihen_n):
    """Knopfzahl je Reihe aus dem Kopf der Belegung (R1 = n ...), sonst wie gebaut."""
    b = os.environ.get("BASS_BELEGUNG")
    return belegung.reihen_aus(belegung.lies(b)[0], dict(reihen_n)) if b else reihen_n

def _reihen_x(kn):
    rx = {}
    for k in kn: rx.setdefault(int(k[3]), []).append(round(k[0], 2))
    return {r: sorted(v) for r, v in rx.items()}

def _art(n, ziel, hebel_x):
    return ("schraeg" if abs(hebel_x - ziel[0]) > 1.0 else "gerade", round(ziel[1] / 8.0))

def _anzeige(n, k, klappen, gehaeuse):
    """Klappenart fuer die Webseite: Begleiter links/rechts (Name beginnt mit B), sonst Grundbass hinten/vorne."""
    if n.upper().startswith("B"):
        return "Begleiter " + ("links" if k["ziel"][0] < gehaeuse[0] / 2 else "rechts")
    gy = [v["ziel"][1] for m, v in klappen.items() if not m.upper().startswith("B")]
    return "Grundbass " + ("hinten" if k["ziel"][1] <= (min(gy) + max(gy)) / 2 else "vorne")

def exportiere(pfad, modell, name, ACHSEN, kn, KNOPF_X, gehaeuse, teilung, fest=False):
    rx = _reihen_x(kn)
    gy = sorted({round(y, 2) for _, y, _, _ in ACHSEN})
    gname = {y: f"G{i + 1}" for i, y in enumerate(gy)}
    klappen, standard, art = {}, {}, {}
    for n, y, arme, hebel in ACHSEN:
        xa, kc = hebel[0]
        klappen[n] = {"ziel": [round(kc[0], 2), round(kc[1], 2)], "hebel_x": round(xa, 2), "_gasse": gname[round(y, 2)]}
        art[n] = _art(n, kc, xa)
        for r, xs in arme:
            xk = KNOPF_X.get((n, r, xs), xs) if KNOPF_X else xs
            i = min(range(len(rx[r])), key=lambda j: abs(rx[r][j] - xk))
            standard[f"{r}.{i + 1}"] = n
    # Gassen je Klappe: die gebaute zuerst, dann alle Gassen gleicher Klappenart nach Abstand zur Klappe
    for n, k in klappen.items():
        gl = sorted({klappen[m]["_gasse"] for m in klappen if art[m] == art[n]},
                    key=lambda g: abs(gy[int(g[1:]) - 1] - k["ziel"][1]))
        k["gassen"] = [k["_gasse"]] + [g for g in gl if g != k["_gasse"]]
        k["art"] = _anzeige(n, k, klappen, gehaeuse)
    # kleinste Luecke zwischen Achsen derselben Gasse wie gebaut (darf die Verteilung nicht unterschreiten)
    ber = {}
    for n, y, arme, hebel in ACHSEN:
        xs = [(KNOPF_X.get((n, r, x), x) if KNOPF_X else x) for r, x in arme] + [hebel[0][0]]   # wie belegung.verteile: Knopf-X
        ber.setdefault(klappen[n]["_gasse"], []).append((min(xs), max(xs)))
    luecke = 12.0
    for g, bs in ber.items():
        bs.sort()
        for (a0, a1), (b0, b1) in zip(bs, bs[1:]): luecke = min(luecke, b0 - a1 - 0.5)
    for k in klappen.values(): del k["_gasse"]
    L, B = gehaeuse
    alle_x = [x for v in rx.values() for x in v]
    m = {"modell": modell, "name": name, "gehaeuse": [round(L, 1), round(B, 1)],
         "reihen": {str(r): len(v) for r, v in rx.items()},
         "reihen_mitte": {str(r): round((v[0] + v[-1]) / 2, 2) for r, v in rx.items()},
         "reihen_zentriert": not fest, "reihen_fest": fest, "teilung": float(teilung),
         "knopf_x": {str(r): v for r, v in rx.items()},
         "knopf_bereich": [round(min(alle_x) - 2 * teilung, 1), round(max(alle_x) + 2 * teilung, 1)],
         "reihen_hinweis": "Knopfzahl je Reihe frei (R1 = n), jede Reihe mittig mit der Knopfteilung",
         "knopf_y": {str(r): round(B - 9 - 14 * (i), 1) for i, r in enumerate(sorted(rx))},
         "gassen": {gname[y]: y for y in gy}, "min_luecke": round(max(4.0, luecke), 1), "gassen_abstand_min": 3.0,
         "klappen": klappen, "standard": dict(sorted(standard.items(), key=lambda kv: [int(t) for t in kv[0].split(".")]))}
    json.dump(m, open(pfad, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Belegungsmodell geschrieben: {pfad} ({len(klappen)} Klappen, {len(gy)} Gassen, {len(standard)} Knoepfe)")

def anwenden(modell, name, ACHSEN, kn, KNOPF_X=None, HEBEL_WEG=None, gehaeuse=(0, 0), teilung=20.0, km=None, fest=False):
    KNOPF_X = {} if KNOPF_X is None else KNOPF_X
    HEBEL_WEG = {} if HEBEL_WEG is None else HEBEL_WEG
    ex = os.environ.get("BELEGUNG_EXPORT")
    if ex:
        exportiere(ex, modell, name, ACHSEN, kn, KNOPF_X, gehaeuse, teilung, fest)
        if os.environ.get("BELEGUNG_NUR_EXPORT"): raise SystemExit(0)
    b = os.environ.get("BASS_BELEGUNG")
    if not b: return ACHSEN, KNOPF_X, HEBEL_WEG
    mj = os.path.join(os.getcwd(), f"belegung_modell_{modell}.json")
    m = json.load(open(mj, encoding="utf-8"))
    katalog = {k: {"ziel": tuple(v["ziel"]), "hebel_x": v["hebel_x"], "gassen": v["gassen"]} for k, v in m["klappen"].items()}
    rx = _reihen_x(kn)
    knopf_x = lambda r, i: rx[r][i]
    _A = belegung.baue_tabelle(b, katalog, m["gassen"], knopf_x, {r: len(v) for r, v in rx.items()}, m.get("min_luecke", 12.0),
                               m.get("gassen_abstand_min", 0.0))
    # Regel 5: Schenkel seitlich versetzen, wo zwei Stangen in derselben X-Lage stehen - wie gebaut, sonst 4 mm
    off = {}
    for n0, y0, arme0, _ in ACHSEN:
        for r0, xs0 in arme0:
            xk0 = KNOPF_X.get((n0, r0, xs0), xs0)
            if abs(xs0 - xk0) > 0.05: off[(r0, round(xk0, 1))] = xs0 - xk0
    alle_k = [(r, xk) for _, _, ks, _, _ in _A for r, xk, _ in ks]
    def versatz(r, xk):
        if (r, round(xk, 1)) in off: return off[(r, round(xk, 1))]
        andere = [r2 for r2, x2 in alle_k if r2 != r and abs(x2 - xk) < 3.0]
        return -4.0 if andere and r > min(andere) else 0.0
    # unveraenderte Achsen (gleiche Klappe, Gasse und Knoepfe) genau wie gebaut uebernehmen - so bleibt die
    # Standardbelegung bitgleich zum gepruefen Modell, nur geaenderte Achsen werden neu gerechnet
    orig = {}
    for e0 in ACHSEN:
        n0, y0, arme0 = e0[0], e0[1], e0[2]
        orig[n0] = (y0, sorted((r0, round(KNOPF_X.get((n0, r0, xs0), xs0), 1)) for r0, xs0 in arme0), e0)
    neu, kx, weg = [], {}, {}
    for kl, y, ks, hs, _ in _A:
        o = orig.get(kl)
        if o and abs(o[0] - y) < 0.01 and o[1] == sorted((r, round(xk, 1)) for r, xk, _ in ks):
            neu.append(o[2])
            for r0, xs0 in o[2][2]:
                if (kl, r0, xs0) in KNOPF_X: kx[(kl, r0, xs0)] = KNOPF_X[(kl, r0, xs0)]
            if kl in HEBEL_WEG: weg[kl] = HEBEL_WEG[kl]
            continue
        hebel = [(xa, (km(*z) if km else tuple(z))) for xa, z in hs]
        arme = [(r, round(xk + versatz(r, xk), 2), xk) for r, xk, _ in ks]
        neu.append((kl, y, [(r, xs) for r, xs, xk in arme], hebel))
        for r, xs, xk in arme: kx[(kl, r, xs)] = xk
        if kl in HEBEL_WEG and any(abs(y - y0) < 0.01 for n0, y0, _, _ in ACHSEN if n0 == kl): weg[kl] = HEBEL_WEG[kl]
    return neu, kx, weg
