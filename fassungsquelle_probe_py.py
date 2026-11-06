# -*- coding: utf-8 -*-
"""Misst FASSUNG einer Python-Linie in zwei Lagen - Gegenstueck zu fassungsquelle_probe.py.

Aufruf:
    python3 Werkzeuge/fassungsquelle_probe_python.py PLUGINORDNER

Erwartet zwei Dateien unter bin/ mit einer Modulvariablen FASSUNG.
Gebaut fuer die Sprachsteuerung (07.09.2026); dort meldeten beide Dateien am
Geraet FASSUNG=0, waehrend die Datenbank 0.11.3 fuehrte.

L1 installiert: bin/ unter bin/plugins/<ordner>, keine plugin.cfg, dafuer
eine plugindatabase.json mit 9.9.9.  L2 Auspackordner: plugin.cfg 7.7.7,
keine Datenbank.  Rueckgabe 0 nur, wenn beide Lagen stimmen.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DB_NUMMER = '9.9.9'
CFG_NUMMER = '7.7.7'
ORDNER = 'pruefling'

plugin = Path(sys.argv[1]).resolve()
wurzel = Path(tempfile.gettempdir()) / 'sp_fassungsprobe'
ergebnis = []


def lage(art):
    if wurzel.exists():
        shutil.rmtree(wurzel, ignore_errors=True)
    lb = wurzel / 'lb'
    for t in ('config/plugins/' + ORDNER, 'data/plugins/' + ORDNER,
              'log/plugins/' + ORDNER, 'data/system', 'templates/plugins/' + ORDNER):
        (lb / t).mkdir(parents=True, exist_ok=True)
    if art == 'installiert':
        zt = lb / 'bin' / 'plugins' / ORDNER
        shutil.copytree(plugin / 'bin', zt)
        (lb / 'data/system/plugindatabase.json').write_text(json.dumps({'plugins': {
            'aa': {'name': ORDNER, 'folder': ORDNER, 'title': 'Probe',
                   'version': DB_NUMMER}}}), encoding='utf-8')
    else:
        zt = lb / 'auspack' / ORDNER
        shutil.copytree(plugin, zt)
        (zt / 'plugin.cfg').write_text('[PLUGIN]\nVERSION=' + CFG_NUMMER + '\n',
                                       encoding='utf-8')
        zt = zt / 'bin'
    umg = dict(os.environ)
    umg['LBHOMEDIR'] = str(lb)
    umg['LBPPLUGINDIR'] = ORDNER
    umg['PYTHONDONTWRITEBYTECODE'] = '1'
    return zt, umg


TREIBER = (
    'import importlib.util, sys\n'
    'sys.argv = ["x"]\n'
    'spec = importlib.util.spec_from_file_location("m", sys.argv[0] if False else PFAD)\n'
    'm = importlib.util.module_from_spec(spec)\n'
    'try:\n'
    '    spec.loader.exec_module(m)\n'
    'except SystemExit:\n'
    '    pass\n'
    'except Exception as e:\n'
    '    print("(Laden gescheitert: %s)" % type(e).__name__)\n'
    '    raise SystemExit\n'
    'print(getattr(m, "FASSUNG", "(kein FASSUNG)"))\n')

print('== %s' % plugin.name)
for art, erwartet in (('installiert', DB_NUMMER), ('archiv', CFG_NUMMER)):
    bin_dir, umg = lage(art)
    for datei in ('hardware.py', 'sprachsteuerung_dienst.py'):
        p = bin_dir / datei
        if not p.is_file():
            print('   %-12s %-26s (fehlt)' % (art, datei))
            continue
        t = wurzel / 'treiber.py'
        t.write_text('PFAD = r"' + str(p) + '"\n' + TREIBER, encoding='utf-8')
        r = subprocess.run([sys.executable, str(t)], capture_output=True, text=True,
                           encoding='utf-8', errors='replace', env=umg,
                           cwd=str(bin_dir), timeout=90)
        ist = (r.stdout or '').strip().splitlines()[-1] if (r.stdout or '').strip() else ''
        ok = (ist == erwartet)
        ergebnis.append(ok)
        print('   %-12s %-26s [%s]  %s'
              % (art, datei, ist, 'in Ordnung' if ok else 'BEFUND - erwartet ' + erwartet))

shutil.rmtree(wurzel, ignore_errors=True)
sys.exit(0 if all(ergebnis) and ergebnis else 1)
