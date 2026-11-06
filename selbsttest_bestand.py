#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Grundlinie: welche Datei waehlt _selbsttest_suchen() je Plugin?

Laeuft ueber den GANZEN Bestand. Die Funktion wird aus der angegebenen
Werkzeugdatei herausgeloest und in einem eigenen Namensraum ausgefuehrt -
freigabe_pruefen.py laesst sich nicht importieren, es fuehrt beim Laden
seine Pruefungen aus.

Aufruf:  python selbsttest_bestand.py <freigabe_pruefen.py> <arbeitsordner>
Ausgabe: eine Zeile je Plugin mit bin/, sortiert.
"""

import os
import re
import sys

werkzeug = sys.argv[1]
arbeit = sys.argv[2]

quelle = open(werkzeug, encoding='utf-8').read()
m = re.search(r'^def _selbsttest_suchen\(wurzel\):\n(?:(?:[ \t].*)?\n)+', quelle, re.M)
if not m:
    raise SystemExit("ABBRUCH: _selbsttest_suchen nicht gefunden in " + werkzeug)
funktionstext = m.group(0)

# Die Umgebung, die die Funktion braucht - dieselben Namen wie im Werkzeug.
raum = {'os': os, 're': re, 'PY': 'PYTHON',
        'PHP_FASSNAME': None,
        'PHP_FASSUNGEN': [('7.4', 'PHP74')]}
exec(compile(funktionstext, werkzeug, 'exec'), raum)
suchen = raum['_selbsttest_suchen']

ordner = sorted(d for d in os.listdir(arbeit)
                if d.startswith('LoxBerry-Plugin-')
                and os.path.isdir(os.path.join(arbeit, d))
                and os.path.isdir(os.path.join(arbeit, d, 'bin')))

for d in ordner:
    p = os.path.join(arbeit, d)
    try:
        erg = suchen(p)
    except Exception as e:                      # noqa: BLE001
        print('%-52s AUSNAHME %s' % (d, e))
        continue
    if erg is None:
        print('%-52s -' % d)
    else:
        wie = os.path.basename(erg[0])
        was = os.path.relpath(erg[-1], p).replace('\\', '/')
        print('%-52s %s %s' % (d, wie, was))
