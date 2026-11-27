# Steirische Harmonika – 3D-Modelle

Dieses Repository enthält alles, um eine Steirische Harmonika als 3D-Modell zu rechnen: die Python-Generatoren für Diskant- und Bassteil, die Werkstattzeichnungen, aus denen sie lesen, und die Webseite mit Konfigurator. Jedes Teil – Gehäuse, Kammern, Stimmstöcke, Mechanik, Griffstock – entsteht aus diesen Zeichnungen, nicht von Hand. Zum Modell gehören die Fertigungsdaten: Fusion-CAM-Vorlagen für Diskant-Stimmstöcke und Griffstöcke und DXF-Dateien für CamBam für alle übrigen Frästeile.

Die Webseite liegt unter **https://jpascher.github.io/harmonika-3d/**. Dort lassen sich die geprüften Modelle samt Fräsdaten ohne Anmeldung herunterladen, und mit dem Konfigurator kann man ein eigenes Modell zusammenstellen und rechnen lassen; dafür braucht es ein kostenloses GitHub-Konto. Die Hilfe-Seite erklärt alle Auswahlmöglichkeiten und wie man die Dateien in Fusion, FreeCAD oder im Browser ansieht.

Die geprüften Modelle hängen als Dateien am Release [„Geprüfte Modelle“](https://github.com/jpascher/harmonika-3d/releases/tag/modelle-geprueft), die auf Anfrage gerechneten Modelle je als eigenes Release „modell-…“. Große Dateien liegen bewusst nicht im Repository selbst, damit es klein bleibt.

Die Quellen stehen im Ordner `markus-3d`: `diskant/` und `bass/` mit den Generatoren je Modell, `ci/` mit der Automatik (Workflow `.github/workflows/harmonika_erzeugen.yml`, Gehäusemaße, Fräsdaten). Beschreibungen stehen in `markus-3d/README.md` und `markus-3d/ci/LIESMICH_Automatik.md`.

Alles ist Open Source und kann von jedem geklont werden (`git clone https://github.com/jpascher/harmonika-3d`). Programme, Skripte und Webseiten stehen unter der GNU General Public License Version 3 oder neuer (`LICENSE`), Zeichnungen, Modelle, Fräsdaten und Bilder unter Creative Commons BY-SA 4.0 (`LICENSE-Modelle-CC-BY-SA-4.0.txt`). Verwenden, nachbauen, ändern und weitergeben ist erlaubt, auch gewerblich, wenn der Urheber Johann Pascher genannt wird und geänderte Fassungen wieder unter derselben Lizenz frei bleiben.
