# Bassteil Standardmechanik mit 4/5 Helikon erzeugen (27.11.2026) - Aufruf: python3 helikon45.py <ausgabe.step> [teilung]
import sys, os, subprocess
H = os.path.dirname(os.path.abspath(__file__))
t = sys.argv[2] if len(sys.argv) > 2 else "20"
env = dict(os.environ, KB_VAR="4-5")
sys.exit(subprocess.run([sys.executable, os.path.join(H, "kugel_bass2.py"), t, "380", os.path.abspath(sys.argv[1])], cwd=H, env=env).returncode)
