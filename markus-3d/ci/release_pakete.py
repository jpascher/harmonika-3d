# Ergebnis eines Laufs von erzeuge_ci.py fuer das Sammel-Release "modelle" umpacken (27.11.2026)
#   python3 release_pakete.py <ergebnisordner> <Name> <zielordner>
# Erzeugt <Name>_step.zip (nur das STEP-Modell), <Name>_Fraesdaten.zip (alle Fertigungsdaten: DXF fuer CamBam,
# beim Diskant auch Fusion-Daten fuer Stimmstoecke/Griffstock, Alu-Tafeln, Holzteile) und <Name>_vorschau.png.
import sys, os, glob, zipfile, shutil

def main(erg, name, ziel):
    os.makedirs(ziel, exist_ok=True)
    quelle = (glob.glob(os.path.join(erg, "*_mit_Fraesdaten.zip")) + glob.glob(os.path.join(erg, "*_step.zip")))[0]
    with zipfile.ZipFile(quelle) as z, \
         zipfile.ZipFile(os.path.join(ziel, f"{name}_step.zip"), "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zs, \
         zipfile.ZipFile(os.path.join(ziel, f"{name}_Fraesdaten.zip"), "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for i in z.infolist():
            if i.is_dir(): continue
            daten = z.read(i.filename)
            if i.filename.lower().endswith(".step") and "/" not in i.filename.strip("/"):
                zs.writestr(f"{name}.step", daten)                      # Hauptmodell
            elif i.filename.lower().endswith((".kollision.json",)):
                continue
            else:
                zf.writestr(i.filename, daten)
        for extra in ("notizen.md", "belegung.txt", "masse.json"):
            p = os.path.join(erg, extra)
            if os.path.exists(p): zf.write(p, extra)
    png = os.path.join(erg, "vorschau.png")
    if os.path.exists(png): shutil.copy(png, os.path.join(ziel, f"{name}_vorschau.png"))
    for f in sorted(os.listdir(ziel)): print(f, os.path.getsize(os.path.join(ziel, f)))

if __name__ == "__main__":
    main(*sys.argv[1:4])
