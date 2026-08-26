#!/usr/bin/env python3
"""Sprachschluessel pruefen - statisch UND die dynamischen Familien.

Rein lesend. Zwei Pruefungen je Plugin:

1. Statisch: jeder woertlich aufgerufene Schluessel xx_t('SEC.KEY') muss in
   language_de.ini UND language_en.ini stehen.
2. Dynamisch: zusammengesetzte Aufrufe wie xx_t('EINST.L_' . $feld) kann
   keine statische Pruefung abdecken (Befund vom 13.08.2026). Dieses
   Werkzeug findet jeden solchen Praefix und zaehlt, wie viele definierte
   Schluessel darauf passen. NULL Treffer sind praktisch sicher ein Fehler
   (der Praefix zeigt ins Leere); wenige Treffer verdienen einen Blick.

Aufruf:  python3 sprachschluessel_pruefen.py <Pluginordner> [...]
Rueckgabewert 1, wenn etwas fehlt - fuer die Pruefkette.

Die Sprachfunktion wird am haeufigsten benutzten Muster erkannt
(xx_t, laengere wie abfahrt_t oder marstek_t eingeschlossen); Gardenas
gt()-Kurzform wird eigens mitgeprueft.
"""
import re
import sys
from pathlib import Path


def wurzel(p):
    if (p / 'plugin.cfg').is_file():
        return p
    treffer = [d for d in sorted(p.iterdir()) if d.is_dir() and (d / 'plugin.cfg').is_file()]
    return treffer[0] if len(treffer) == 1 else p


def schluessel_aus(ini):
    sec, aus = '', set()
    if not ini.is_file():
        return None
    for zl in ini.read_text(encoding='utf-8', errors='replace').splitlines():
        m = re.match(r'^\[([A-Z0-9_]+)\]\s*$', zl.strip())
        if m:
            sec = m.group(1)
            continue
        m = re.match(r'^([A-Za-z0-9_]+)\s*=', zl)
        if m and sec:
            aus.add(sec + '.' + m.group(1))
    return aus


def pruefe(p):
    p = wurzel(p)
    code = ''
    for f in p.glob('webfrontend/**/*.php'):
        code += f.read_text(encoding='utf-8', errors='replace')
    for f in p.glob('bin/*.php'):
        code += f.read_text(encoding='utf-8', errors='replace')
    fns = re.findall(r"\b([a-z][a-z0-9_]{0,12}_t|gt)\(\s*['\"]", code)
    if not fns:
        return ['keine Sprachfunktion gefunden - von Hand ansehen']
    fn = max(set(fns), key=fns.count)
    de = schluessel_aus(p / 'templates/lang/language_de.ini')
    en = schluessel_aus(p / 'templates/lang/language_en.ini')
    aus = []
    if de is None:
        return ['language_de.ini fehlt']
    if en is None:
        aus.append('language_en.ini fehlt')
        en = set()

    # 1. statisch
    statisch = set(re.findall(re.escape(fn) + r"\(\s*'([A-Z0-9_]+\.[A-Za-z0-9_]+)'\s*\)", code))
    for k in sorted(statisch - de):
        aus.append('fehlt in DE: ' + k)
    for k in sorted(statisch - en):
        aus.append('fehlt in EN: ' + k)

    # 2. dynamische Familien: xx_t('SEC.PREFIX' . irgendwas)
    for praefix in sorted(set(re.findall(
            re.escape(fn) + r"\(\s*'([A-Z0-9_]+\.[A-Za-z0-9_]*?)'\s*\.", code))):
        treffer_de = [k for k in de if k.startswith(praefix)]
        treffer_en = [k for k in en if k.startswith(praefix)]
        if not treffer_de:
            aus.append("dynamischer Praefix '%s' trifft KEINEN DE-Schluessel" % praefix)
        elif len(treffer_de) != len(treffer_en):
            aus.append("dynamischer Praefix '%s': DE %d, EN %d Schluessel"
                       % (praefix, len(treffer_de), len(treffer_en)))
    return aus


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    offen = 0
    for arg in sys.argv[1:]:
        p = Path(arg)
        beanstandungen = pruefe(p)
        if beanstandungen:
            offen += 1
            print(p.name if p.name else str(p))
            for b in beanstandungen:
                print('   ', b)
        else:
            print('%-34s ok' % (p.name if p.name else str(p)))
    sys.exit(1 if offen else 0)
