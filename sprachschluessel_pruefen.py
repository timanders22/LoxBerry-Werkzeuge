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

ALLE Sprachhelfer werden geprueft, nicht nur der haeufigste (berichtigt am
04.09.2026). Bis dahin waehlte das Werkzeug mit max(..., key=count) genau
EINEN Helfer; ein zweiter wie xx_te() - uebersetzen UND maskieren - war
unsichtbar. Bei Midea2Lox 4.5.0 meldete es 31 fehlende Schluessel, wirklich
fehlten 60; in 4.4.0 waren 107 Schluessel nie angesehen worden.

Als Sprachhelfer gilt, wer auf _t oder _te endet (oder gt heisst) UND
mindestens einmal mit einem Schluessel in Abschnitt.NAME-Form aufgerufen
wird. Die zweite Bedingung haelt Funktionen heraus, die nur zufaellig so
heissen.
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
    # ALLE Helfer, nicht nur der haeufigste - und _te gehoert dazu.
    kandidaten = sorted(set(re.findall(
        r"\b([a-z][a-z0-9_]{0,12}_te?|gt)\(\s*['\"]", code)))
    # Nur, wer wirklich mit einem Schluessel aufgerufen wird. Ohne diese
    # Bedingung wuerde jede Funktion mitgezaehlt, die zufaellig auf _t endet.
    fns = [f for f in kandidaten
           if re.search(re.escape(f) + r"\(\s*'[A-Z0-9_]+\.[A-Za-z0-9_]+'", code)]
    if not fns:
        return ['keine Sprachfunktion gefunden - von Hand ansehen']
    de = schluessel_aus(p / 'templates/lang/language_de.ini')
    en = schluessel_aus(p / 'templates/lang/language_en.ini')
    aus = []
    if de is None:
        return ['language_de.ini fehlt']
    if en is None:
        aus.append('language_en.ini fehlt')
        en = set()

    # 1. statisch - ueber JEDEN Helfer
    statisch = set()
    for fn in fns:
        statisch |= set(re.findall(
            re.escape(fn) + r"\(\s*'([A-Z0-9_]+\.[A-Za-z0-9_]+)'\s*\)", code))
    for k in sorted(statisch - de):
        aus.append('fehlt in DE: ' + k)
    for k in sorted(statisch - en):
        aus.append('fehlt in EN: ' + k)

    # 2. dynamische Familien: xx_t('SEC.PREFIX' . irgendwas) - ueber JEDEN Helfer
    praefixe = set()
    for fn in fns:
        praefixe |= set(re.findall(
            re.escape(fn) + r"\(\s*'([A-Z0-9_]+\.[A-Za-z0-9_]*?)'\s*\.", code))
    for praefix in sorted(praefixe):
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
