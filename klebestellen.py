#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wo verschluckt PHP ein Leerzeichen? Ueber den ganzen Bestand.

Gesucht wird das Muster aus Regeln/03: eine Zeile, die etwas AUSGIBT und mit
`?>` endet, gefolgt von einer Zeile, die ohne Leerraum mit sichtbarer Ausgabe
beginnt. PHP verschluckt genau einen Zeilenumbruch nach `?>` - die beiden
Woerter kleben.

Nicht gemeldet wird:
  * eine Folgezeile, die mit Leerraum beginnt (das Leerzeichen ueberlebt),
  * ein Block- oder Zellenelement (<div>, <p>, <td>, <tr>, <br>, <li>, <h1>...)
    - dort trennt die Darstellung ohnehin,
  * eine reine Steuerzeile (`<?php } ?>`, `<?php if ... ?>`), die nichts ausgibt.
"""
import glob
import os
import re
import sys

AUSGABE = re.compile(r'<\?=|<\?php\s+(echo|print)\b')
BLOCK = re.compile(r'^<(/?)(div|p|td|tr|th|table|br|li|ul|ol|h[1-6]|form|option|select|input|button|textarea|script|style|!--)\b', re.I)
INLINE = re.compile(r'^(<(b|i|em|strong|span|a|code|small|sup|sub)\b|&[a-z#0-9]+;|[0-9A-Za-zÄÖÜäöüß(])')


def messen(pfad):
    with open(pfad, 'rb') as f:
        z = f.read().decode('utf-8', 'replace').replace('\r\n', '\n').split('\n')
    treffer = []
    for i in range(len(z) - 1):
        a = z[i].rstrip()
        if not a.endswith('?>') or not AUSGABE.search(a):
            continue
        b = z[i + 1]
        if b[:1] in (' ', '\t', ''):
            continue
        if BLOCK.match(b) or b.startswith('<?php'):
            continue
        if not INLINE.match(b):
            continue
        treffer.append((i + 1, a.strip()[-52:], b.strip()[:42]))
    return treffer


ziel = sys.argv[1] if len(sys.argv) > 1 else 'LoxBerry-Plugin-*'
linien = sorted(d for d in glob.glob(ziel) if os.path.isdir(d))
gesamt = 0
betroffen = []
for d in linien:
    n = 0
    for r, _, fs in os.walk(d):
        for f in fs:
            if not f.endswith('.php'):
                continue
            t = messen(os.path.join(r, f))
            if t:
                n += len(t)
                if len(sys.argv) > 1:
                    for zeile, a, b in t:
                        print('  %s:%d\n      %s\n   -> %s' % (
                            os.path.join(r, f).replace(os.sep, '/'), zeile, a, b))
    if n:
        betroffen.append((d, n))
        gesamt += n

print('\n%d Linien geprueft, %d mit Klebestelle, %d Stellen insgesamt.'
      % (len(linien), len(betroffen), gesamt))
for d, n in sorted(betroffen, key=lambda x: -x[1])[:15]:
    print('  %-46s %3d' % (d, n))
