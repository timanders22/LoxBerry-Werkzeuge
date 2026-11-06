# -*- coding: utf-8 -*-
"""Misst eine Python-Funktion (z. B. version()) in zwei Lagen.

Aufruf:
    python3 Werkzeuge/fassungsquelle_probe_py_funktion.py . ORDNER BIN-DATEI FUNKTION

Gegenstueck zu fassungsquelle_probe.py (PHP) und
fassungsquelle_probe_py.py (Modulvariable FASSUNG). Gebaut am 07.09.2026 fuer
APC-UPS und Chromecast4lox - dort heisst es version() und ist eine Funktion.

L1 installiert: bin/ unter bin/plugins/<ordner>, keine plugin.cfg, dafuer eine
plugindatabase.json mit 9.9.9.  L2 Auspackordner: plugin.cfg 7.7.7, keine
Datenbank.  Der Ordnername kommt aus der plugin.cfg der Linie.

Eine leere Antwort in L2 ist NICHT zwingend ein Befund: manche Linien geben
dort bewusst nichts zurueck, weil eine geratene Nummer schlechter waere als
keine. Der Ausgang ist eine Frage, kein Urteil.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ARBEIT = Path(sys.argv[1])
PLUGIN = ARBEIT / sys.argv[2]
DATEI = sys.argv[3]
FUNK = sys.argv[4]
DB, CFG = '9.9.9', '7.7.7'

m = re.search(r'^\s*FOLDER\s*=\s*(\S+)',
              (PLUGIN / 'plugin.cfg').read_text(encoding='utf-8', errors='replace'),
              re.M | re.I)
ORDNER = m.group(1).strip().strip('"').strip("'") if m else 'pruefling'
print('== %s  (bin/%s, %s())   Ordner: %s' % (PLUGIN.name, DATEI, FUNK, ORDNER))

W = Path(tempfile.gettempdir()) / 'py_version_probe'
ergebnis = []

TREIBER = (
    'import importlib.util, sys\n'
    'sys.argv = ["x"]\n'
    'spec = importlib.util.spec_from_file_location("m", PFAD)\n'
    'm = importlib.util.module_from_spec(spec)\n'
    'try:\n'
    '    spec.loader.exec_module(m)\n'
    'except SystemExit:\n'
    '    pass\n'
    'except Exception as e:\n'
    '    print("(Laden gescheitert: %s: %s)" % (type(e).__name__, e))\n'
    '    raise SystemExit\n'
    'f = getattr(m, FUNK, None)\n'
    'print(f() if callable(f) else "(keine Funktion %s)" % FUNK)\n')

for art, erwartet in (('installiert', DB), ('archiv', CFG)):
    if W.exists():
        shutil.rmtree(W, ignore_errors=True)
    lb = W / 'lb'
    for t in ('config/plugins/' + ORDNER, 'data/plugins/' + ORDNER,
              'log/plugins/' + ORDNER, 'data/system'):
        (lb / t).mkdir(parents=True, exist_ok=True)
    if art == 'installiert':
        bin_dir = lb / 'bin' / 'plugins' / ORDNER
        shutil.copytree(PLUGIN / 'bin', bin_dir)
        (lb / 'data/system/plugindatabase.json').write_text(json.dumps({'plugins': {
            'aa': {'name': ORDNER, 'folder': ORDNER, 'title': 'Probe', 'version': DB}}}),
            encoding='utf-8')
    else:
        zt = lb / 'auspack' / ORDNER
        shutil.copytree(PLUGIN, zt)
        (zt / 'plugin.cfg').write_text('[PLUGIN]\nVERSION=' + CFG + '\nFOLDER=' + ORDNER + '\n',
                                       encoding='utf-8')
        bin_dir = zt / 'bin'
    umg = dict(os.environ)
    umg['LBHOMEDIR'] = str(lb)
    umg['LBPPLUGINDIR'] = ORDNER
    umg['LBPCONFIGDIR'] = str(lb / 'config/plugins' / ORDNER)
    umg['LBPLOGDIR'] = str(lb / 'log/plugins' / ORDNER)
    umg['LBPDATADIR'] = str(lb / 'data/plugins' / ORDNER)
    umg['PYTHONDONTWRITEBYTECODE'] = '1'
    t = W / 'treiber.py'
    t.write_text('PFAD = r"' + str(bin_dir / DATEI) + '"\nFUNK = "' + FUNK + '"\n' + TREIBER,
                 encoding='utf-8')
    r = subprocess.run([sys.executable, str(t)], capture_output=True, text=True,
                       encoding='utf-8', errors='replace', env=umg,
                       cwd=str(bin_dir), timeout=120)
    ist = (r.stdout or '').strip().splitlines()[-1] if (r.stdout or '').strip() else ''
    ok = (ist == erwartet)
    ergebnis.append(ok)
    print('   %-12s [%s]  %s' % (art, ist, 'in Ordnung' if ok else 'erwartet ' + erwartet))

shutil.rmtree(W, ignore_errors=True)
sys.exit(0 if all(ergebnis) else 1)
