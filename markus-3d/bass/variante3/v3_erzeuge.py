# Bassteil Variante 3 "traditionell, flacher Einbau" erzeugen (27.11.2026)
# Aufruf im Ordner bass/variante3:  python3 v3_erzeuge.py <ausgabe.step>
# Legt eine Arbeitskopie an (Markus-Quellen aus bass/, darueber die Dateien dieser Variante), baut Front, Rueckteil und
# Seitenteile aus rahmen.dxf und rechnet dann kammern.py (Gehaeuse, Kammern, Mechanik mit Kollisionspruefung).
# Freie Belegung: Umgebungsvariable BASS_BELEGUNG (Datei wie bei den anderen Bassteilen, siehe belegung_modell_v3.json).
import sys, os, shutil, subprocess
HIER = os.path.dirname(os.path.abspath(__file__)); BASS = os.path.dirname(HIER)
OUT = os.path.abspath(sys.argv[1])
Z = os.path.join(BASS, "varianten", "variante3")
if os.path.exists(Z): shutil.rmtree(Z)
os.makedirs(Z)
for f in os.listdir(BASS):                                   # Markus-Quellen (nur Dateien, keine Unterordner)
    p = os.path.join(BASS, f)
    if os.path.isfile(p) and not f.endswith(".step"): shutil.copy2(p, Z)
for f in os.listdir(HIER):                                   # Variante 3 darueber
    p = os.path.join(HIER, f)
    if os.path.isfile(p): shutil.copy2(p, Z)
for t in ("front", "rueck", "seite"):
    subprocess.run([sys.executable, "teile.py", "rahmen.dxf", f"Markus_{t}_v4.step", t], cwd=Z, check=True, stdout=subprocess.DEVNULL)
r = subprocess.run([sys.executable, "kammern.py", "boden2.dxf", OUT], cwd=Z)
sys.exit(r.returncode)
