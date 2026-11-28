# Auswahl fuer "Harmonika erzeugen" einlesen und pruefen (Johann 26.11.2026)
# Quelle: Formular "Run workflow" (Umgebungsvariablen IN_<feld>) oder eine Modell-Anfrage als Issue (ISSUE_BODY).
# Nur gepruefte Werte aus festen Listen bzw. streng gepruefte Zahlen-/Kurzform-Texte werden weitergegeben.
# Ausgabe: Zeilen "name=wert" nach $GITHUB_OUTPUT; bei Fehlern ok=nein und grund=<Meldung>.
import os, re, sys, json, glob

HIER = os.path.dirname(os.path.abspath(__file__))
M3D = os.path.dirname(HIER)
LISTEN = {"teil": ["bass", "diskant"], "bass_variante": ["markus", "marie38", "eduard", "gerhard", "andreas", "v340", "v3", "helikon44", "helikon45"],
          "teilung": ["standard", "18", "19", "20"], "instrument": ["markus", "marie"],
          "griffstock": ["standard", "traditionell", "kugellager", "kolben", "kolben12", "winkel", "winkel_ital"],
          "knoepfe": ["50", "44", "46", "48", "52", "54"], "abstand": ["20", "19", "18"]}
STANDARD = {"teil": "bass", "bass_variante": "markus", "teilung": "standard", "laenge": "", "breite": "", "instrument": "markus",
            "griffstock": "standard", "knoepfe": "50", "abstand": "", "hebel": "", "platten": "", "belegung": "", "vorschau": "ja", "registerschieber": "", "klappenteilung": ""}
# Feldtitel im Issue-Formular (.github/ISSUE_TEMPLATE/modell_anfrage.yml) -> Feld
TITEL = {"Teil": "teil", "Bass: Bassteil": "bass_variante", "Bass: Knopfteilung": "teilung",
         "Bass: Gehäuselänge (nur Markus-Bass, mm)": "laenge", "Gehäuselänge (mm)": "laenge", "Gehäusebreite (mm)": "breite", "Bass: Belegung (nur v340)": "belegung", "Bass: Belegung (nicht beim Markus-Bass)": "belegung", "Bass: Belegung": "belegung",
         "Diskant: Instrument": "instrument", "Diskant: Griffstock": "griffstock", "Diskant: Knopfzahl": "knoepfe",
         "Diskant: Knopfabstand (mm)": "abstand", "Diskant: Hebelteilung (mm)": "hebel", "Diskant: Stimmplattenlängen": "platten", "Vorschau erzeugen": "vorschau"}

def aus_issue(text):
    werte, feld = {}, None
    for z in (text or "").splitlines():
        m = re.match(r"^###\s+(.+?)\s*$", z)
        if m: feld = TITEL.get(m.group(1).strip()); continue
        # nicht ausgefüllt: Textfelder liefern "_No response_", nicht gewählte Auswahllisten "None" -> Standardwert
        if feld and z.strip() and z.strip() not in ("_No response_", "None"):
            werte[feld] = (werte.get(feld, "") + " " + z.strip()).strip()
    return werte

def pruefe(w):
    a = dict(STANDARD); a.update({k: v.strip() for k, v in w.items() if v is not None and v.strip() != ""})
    if not a["abstand"]:                    # alte Angabe Hebelteilung 9 / 10 -> Knopfabstand 18 / 20; sonst Markus 20, Marie 19
        a["abstand"] = {"9": "18", "10": "20"}.get(a["hebel"], "") if a["hebel"] else ("19" if a["instrument"] == "marie" and a["griffstock"] != "winkel" else "20")
        if not a["abstand"]: raise ValueError(f"Hebelteilung {a['hebel']} mm gibt es nicht mehr - Knopfabstand 18, 19 oder 20 mm wählen")
    for k, erlaubt in LISTEN.items():
        if a[k] not in erlaubt: raise ValueError(f"{k}: '{a[k]}' ist nicht erlaubt ({', '.join(erlaubt)})")
    a["vorschau"] = "true" if a["vorschau"].lower() in ("ja", "true", "1") else "false"
    if a["laenge"]:
      try: l = float(a["laenge"].replace(",", "."))
      except ValueError: raise ValueError(f"Gehäuselänge '{a['laenge']}' ist keine Zahl")
      if not 300 <= l <= 560: raise ValueError(f"Gehäuselänge {l:g} mm außerhalb 300–560 mm")
      a["laenge"] = f"{l:g}"
    if a["breite"]:
      try: b = float(a["breite"].replace(",", "."))
      except ValueError: raise ValueError(f"Gehäusebreite '{a['breite']}' ist keine Zahl")
      if not 200 <= b <= 215: raise ValueError(f"Gehäusebreite {b:g} mm außerhalb 200–215 mm")
      a["breite"] = f"{b:g}"
    L0 = {"markus": 380, "marie38": 380, "eduard": 380, "gerhard": 380, "andreas": 400, "v340": 340, "v3": 380, "helikon44": 380, "helikon45": 380}   # gezeichnet (fertig)
    if a["teil"] == "bass" and a["bass_variante"] == "v3" and a["teilung"] not in ("", "standard", "20"):
      raise ValueError("Variante 3 traditionell gibt es nur mit 20 mm Knopfteilung")
    if a["teil"] == "bass" and a["laenge"]:
      l0 = L0[a["bass_variante"]]
      if float(a["laenge"]) < l0 - 0.05: raise ValueError(f"Gehäuselänge {a['laenge']} mm: der Bass {a['bass_variante']} ist mindestens {l0} mm lang (kürzer geht nicht)")
      if float(a["laenge"]) > l0 + 150: raise ValueError(f"Gehäuselänge {a['laenge']} mm: höchstens {l0 + 150} mm")
    BMIN = {"markus": 203.5, "marie38": 200, "eduard": 200.5, "gerhard": 202, "andreas": 202.5, "v340": 203, "v3": 203.5, "helikon44": 205, "helikon45": 205}   # gerechnet 27.11.
    if a["teil"] == "bass" and a["breite"] and float(a["breite"]) < BMIN[a["bass_variante"]] - 0.01:
      raise ValueError(f"Gehäusebreite {a['breite']} mm: beim Bass {a['bass_variante']} geht schmäler nur bis {BMIN[a['bass_variante']]:g} mm, "
                       "ohne Stimmplatten, Kammern oder Mechanik zu beschneiden")
    if not re.fullmatch(r"[Rr0-9:;,.\s]{0,600}", a["platten"]): raise ValueError("Stimmplattenlängen: nur R, Ziffern, Doppelpunkt, Strichpunkt, Komma, Punkt")
    if not re.fullmatch(r"[0-9.=A-Za-z,;\s]{0,800}", a["belegung"]): raise ValueError("Belegung: nur die Kurzform '1.1=V077, 1.2=BL152, ...'")
    a["platten"] = " ".join(a["platten"].split()); a["belegung"] = " ".join(a["belegung"].split())
    sys.path.insert(0, HIER); sys.path.insert(0, os.path.join(M3D, "bass"))
    if a["teil"] == "diskant":
        import tastenliste_bauen as tb
        if a["griffstock"].startswith("winkel") and a["abstand"] == "18":   # 28.11.2026 (Johann): Lager fest, Kroepfung ca. 58 Grad
            raise ValueError("Winkel-Griffstock mit 18 mm Knopfabstand geht nicht (Lager fest: 50 Schlitze, 4,8 mm Teilung; Kröpfung Lager → Knopf etwa 58°)")
        tb.pruefe(a["instrument"], a["griffstock"], int(a["knoepfe"]), int(a["abstand"]))
        if a["platten"]: tb.lies_platten(a["platten"])
        if a["laenge"]:                                       # reicht die Laenge fuer Knopfzahl und Knopfabstand?
            import tempfile
            with tempfile.TemporaryDirectory() as td:
                tb.baue(a["instrument"], a["griffstock"], int(a["knoepfe"]), int(a["abstand"]), os.path.join(td, "t.txt"), "", a["laenge"])
        a["variante"] = f'{a["instrument"]}:{a["griffstock"]}:{a["knoepfe"]}:{a["abstand"]}'
        a["titel"] = f'Diskant {a["instrument"]}, {a["griffstock"]}, {a["knoepfe"]} Knoepfe, Knopfabstand {a["abstand"]} mm'
    else:
        a["variante"] = a["bass_variante"]
        if a["belegung"]:
            ord_ = {"markus": os.path.join(M3D, "bass"), "v3": os.path.join(M3D, "bass", "variante3"), "helikon44": os.path.join(M3D, "bass", "kugellager"),
                    "helikon45": os.path.join(M3D, "bass", "kugellager")}.get(a["bass_variante"], os.path.join(M3D, "bass", a["bass_variante"]))
            mj = glob.glob(os.path.join(ord_, f"belegung_modell_{a['bass_variante']}.json")) or glob.glob(os.path.join(ord_, "belegung_modell_*.json"))
            if not mj: raise ValueError(f"Freie Belegung gibt es für {a['bass_variante']} noch nicht")
            import belegung
            belegung.pruefe_alles(mj[0], a["belegung"], a["teilung"])   # Knopfzahl je Reihe (R1=..), Teilung, Gassen
        a["titel"] = f'Bass {a["bass_variante"]}, Teilung {a["teilung"]}' + (", eigene Belegung" if a["belegung"] else "")
    if a["laenge"] or a["breite"]:
        a["titel"] += ", Gehaeuse" + (f' L {a["laenge"]}' if a["laenge"] else "") + (f' B {a["breite"]}' if a["breite"] else "")
    # 28.11.2026: Registerschieber (nur Diskant Markus 3-choerig); Laenge ergibt sich dann aus dem kuerzesten Einbau
    a["schieber"] = "1" if a.get("registerschieber", "").lower() in ("1", "ja", "true", "yes") else ""
    if a["schieber"]:
        if a["teil"] != "diskant" or a["instrument"] != "markus": raise ValueError("Registerschieber gibt es nur beim Diskant Markus (3-choerig)")
        a["titel"] += ", Registerschieber"
        if a.get("klappenteilung"):
            try: kt_ = float(a["klappenteilung"].replace(",", "."))
            except ValueError: raise ValueError(f"Klappenteilung '{a['klappenteilung']}' ist keine Zahl")
            if not 20.0 <= kt_ <= 26.25: raise ValueError(f"Klappenteilung {kt_:g} mm ausserhalb 20-26,25 mm")
            a["klappenteilung"] = f"{kt_:g}"; a["titel"] += f", Klappenteilung {kt_:g}"
    else:
        a["klappenteilung"] = ""
    # 28.11.2026: Name im Sammel-Release "modelle", falls genau diese Ausfuehrung dort schon liegt (dann nicht neu rechnen)
    a["sammel"] = ""
    if a["teil"] == "diskant" and not (a["platten"] or a["laenge"] or a["breite"] or a["schieber"]):
        a["sammel"] = f'Diskant_{a["instrument"].capitalize()}_{a["griffstock"]}_{a["knoepfe"]}K_{a["abstand"]}mm'
    elif a["teil"] == "bass" and not (a["belegung"] or a["breite"]):
        t_ = a["teilung"] if a["teilung"] not in ("", "standard") else ""
        if a["bass_variante"] == "markus":
            a["sammel"] = f'Bass_Markus_T{t_ or "20"}_L{a["laenge"] or "380"}'
        elif not t_ and not a["laenge"]:
            a["sammel"] = f'Bass_{a["bass_variante"].capitalize()}'
    return a

def main():
    out = open(os.environ.get("GITHUB_OUTPUT", "/dev/stdout"), "a", encoding="utf-8")
    if os.environ.get("QUELLE") == "issue": w = aus_issue(os.environ.get("ISSUE_BODY", ""))
    else: w = {k: os.environ.get("IN_" + k.upper(), "") for k in STANDARD}
    try:
        a = pruefe(w)
    except (ValueError, SystemExit) as e:
        grund = " ".join(str(e).split())
        print("Auswahl ungueltig:", grund)
        out.write("ok=nein\n"); out.write(f"grund={grund}\n"); return
    for k in ("teil", "variante", "teilung", "laenge", "breite", "vorschau", "platten", "belegung", "titel", "sammel", "schieber", "klappenteilung"):
        out.write(f"{k}={a[k]}\n")
    out.write("ok=ja\n")
    print("Auswahl:", json.dumps({k: a[k] for k in ("teil", "variante", "teilung", "laenge", "breite", "vorschau", "platten", "belegung")}, ensure_ascii=False))

if __name__ == "__main__":
    main()
