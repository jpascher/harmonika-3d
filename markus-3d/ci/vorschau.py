# Vorschau aus einem STEP-Modell: grobe GLB mit Farben (fuer den Browser / 3D-Viewer) und ein PNG-Standbild.
#   python3 vorschau.py modell.step vorschau.glb vorschau.png
import sys, os
os.environ.setdefault("PYVISTA_OFF_SCREEN", "true")
import cadquery as cq, trimesh, numpy as np, pyvista as pv

step, glb, png = sys.argv[1:4]
assy = cq.Assembly.importStep(step)
assy.export(glb, tolerance=0.8, angularTolerance=0.6)
print(f"GLB {os.path.getsize(glb) / 1e6:.1f} MB")
szene = trimesh.load(glb, force="scene")
import re
netze = []                                                # (Teilname, Netz in Weltlage)
for knoten in szene.graph.nodes_geometry:
    T_, g_ = szene.graph[knoten]
    m0 = szene.geometry[g_]
    if len(m0.faces) == 0: continue
    m = m0.copy(); m.apply_transform(T_)
    netze.append((re.sub(r"_[0-9a-f]{6}$", "", str(knoten)), m))
VERDECK = re.compile(r"^(Verdeck|Deckplatte|Front|Seite_|Blume)")
def gruppiere(auswahl):
  gruppen = {}                                            # nach Farbe zusammenfassen: wenige grosse Netze rendern schnell
  for nm, m in auswahl:
    farbe = (179, 179, 179)
    try:
        f_ = np.asarray(m.visual.material.baseColorFactor[:3], float)
        farbe = tuple(int(round(v)) for v in (f_ if f_.max() > 1 else f_ * 255))
    except Exception:
        try: farbe = tuple(int(v) for v in m.visual.main_color[:3])
        except Exception: pass
    gruppen.setdefault(farbe, []).append(trimesh.Trimesh(m.vertices, m.faces, process=False))
  return gruppen

def bild(auswahl, datei, ansicht=None):
    gruppen = gruppiere(auswahl)
    pl = pv.Plotter(off_screen=True, window_size=(1600, 1000))
    pl.set_background("white")
    for farbe, teile in gruppen.items():
        pl.add_mesh(pv.wrap(trimesh.util.concatenate(teile)), color=tuple(v / 255 for v in farbe))
    if ansicht is None:
        pl.view_isometric(); pl.camera.zoom(1.3)
    else:                                                 # Blickrichtung und Oben in Modellkoordinaten (GLB: X, Z, -Y)
        (bx, by, bz), (ox, oy, oz) = ansicht
        pl.reset_camera()
        c = np.asarray(pl.camera.focal_point); d = pl.camera.distance
        v = np.array([bx, bz, -by], float); v /= np.linalg.norm(v)
        pl.camera.position = tuple(c - v * d); pl.camera.up = (ox, oz, -oy)
        pl.reset_camera(); pl.camera.zoom(1.35)
    pl.screenshot(datei)
    print(f"PNG {datei} ({len(gruppen)} Farben)")

bild(netze, png)
# 28.11. (Johann): zusaetzlich Blick auf den Griffstock ohne Verdeck und von der Balgseite ins Gehaeuse
ohne = [(n, m) for n, m in netze if not VERDECK.search(n)]
stamm = png[:-4] if png.lower().endswith(".png") else png
bild(ohne, stamm + "_griffstock.png", ((0.25, -0.9, 0.7), (0.0, 0.0, -1.0)))      # Knoepfe und Hebel (Verdeckseite)
bild(ohne, stamm + "_deckel.png", ((0.3, 1.0, -0.35), (0.0, 0.0, 1.0)))         # Griffstockdeckel (Daumenseite)
bild(ohne, stamm + "_innen.png", ((0.0, 0.25, -1.0), (0.0, 1.0, 0.0)))
