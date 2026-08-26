#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Liegt JEDER handelnde POST-Zweig hinter dem Wachposten?

Ein Merkmal, das erzeugt und in die Formulare geschrieben, aber nie geprueft
wird, ist kein Schutz - nur die Behauptung eines Schutzes. Umgekehrt taeuscht
eine Pruefung Sicherheit vor, wenn ein einzelner Zweig an ihr vorbeilaeuft.

Gemessen wird nicht am Namen einer Funktion: die Pruefung kann inline in
index.php stehen. Gesucht wird der VERGLEICH (hash_equals) und danach, ob
jeder Zweig, der $_POST auswertet, entweder

    - an der Wache haengt ($<prae>_post, das die Wache auf false setzt), oder
    - innerhalb eines Blocks steht, der daran haengt, oder
    - gar nicht handelt (er liest nur den aktiven Reiter).
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ARBEIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARMLOS = re.compile(r"_POST\['(activetab|tab|form)'\]")


def tiefe_bis(z, bis):
    """Klammertiefe am Anfang der Zeile - Zeichenketten und Kommentare
    uebersprungen. Ohne das zaehlt eine Klammer in einem Text mit, und der
    Wachposten meldet ein rotes Kreuz, das nichts bedeutet. Ein falscher
    Befund kostet mehr Vertrauen, als ein richtiger einbringt."""
    t = 0
    j = 0
    s = chr(10).join(z[:bis])
    while j < len(s):
        c = s[j]
        if c in chr(34) + chr(39):
            q = c
            j += 1
            while j < len(s) and s[j] != q:
                j += 2 if s[j] == chr(92) else 1
        elif s.startswith("//", j) or s.startswith("#", j):
            j = s.find(chr(10), j)
            if j < 0:
                break
        elif s.startswith("/*", j):
            k = s.find("*/", j)
            if k < 0:
                break
            j = k + 1
        elif c == "{":
            t += 1
        elif c == "}":
            t -= 1
        j += 1
    return t

def pruefe(o):
    idx = os.path.join(o, 'webfrontend', 'htmlauth', 'index.php')
    if not os.path.isfile(idx):
        return None
    z = io.open(idx, encoding='utf-8', errors='replace').read().split('\n')
    ganz = '\n'.join(z)
    # Der VERGLEICH muss nicht in index.php stehen.
    #
    # Bis zum 26.08.2026 suchte diese Zeile hash_equals ausschliesslich in
    # index.php. Ein Plugin, das die Pruefung in seine Bibliothek zieht -
    #     if (!ro_formtoken_ok($cfg)) { ... }
    # mit hash_equals in robo_lib.php - fiel damit auf 'kein Vergleich' und
    # wurde stillschweigend UEBERSPRUNGEN. Es erschien gar nicht in der
    # Tabelle. Ein Werkzeug, das den Prueflieferanten ueberspringt, entlastet
    # nicht; genau davor warnt der eigene Kopf dieser Datei.
    #
    # Gesucht wird deshalb in beiden Richtungen, und BEIDES muss zutreffen:
    #   a) irgendwo im Plugin steht der Vergleich
    #   b) index.php laesst ihn auch anlaufen - direkt oder ueber einen
    #      Aufruf, dessen Name auf _formtoken_ok / _fmt_ok endet.
    # Ohne b) waere ein Vergleich, den niemand ruft, ein gruener Haken.
    zeile_wache = next((i for i, y in enumerate(z) if 'hash_equals' in y), None)
    if zeile_wache is None:
        ruf = re.compile(r'\b\w+_(?:formtoken_ok|fmt_ok|merkmal_ok)\s*\(')
        zeile_wache = next((i for i, y in enumerate(z) if ruf.search(y)), None)
        vergleich_da = False
        if zeile_wache is not None:
            for wurzel, _, ds in os.walk(o):
                for f in ds:
                    if not f.endswith('.php'):
                        continue
                    try:
                        if 'hash_equals' in io.open(os.path.join(wurzel, f),
                                                    encoding='utf-8',
                                                    errors='replace').read():
                            vergleich_da = True
                    except Exception:
                        pass
        if zeile_wache is None or not vergleich_da:
            return ('kein Vergleich', [])
    wache = zeile_wache
    m = re.search(r'\$(\w+_post)\s*=\s*false', ganz)
    postvar = '$' + m.group(1) if m else None
    leert = '$_POST = array()' in ganz
    if leert:
        return ('geprueft, $_POST geleert', [])
    if not postvar:
        return ('geprueft, aber keine Wache erkennbar', [])
    offen = []
    for i, y in enumerate(z):
        if i <= wache or "isset($_POST[" not in y or not y.lstrip().startswith('if'):
            continue
        if postvar in y or HARMLOS.search(y):
            continue
        # haengt ein umschliessender Block daran?
        if tiefe_bis(z, i) > 0:
            continue
        offen.append((i + 1, y.strip()[:70]))
    return ('geprueft ueber %s' % postvar, offen)


ordner = sys.argv[1:] or [e for e in sorted(os.listdir(ARBEIT))
                          if e.startswith('LoxBerry-Plugin-')
                          and os.path.isdir(os.path.join(ARBEIT, e))]
print('%-30s %-34s %s' % ('Plugin', 'Wachposten', 'ungedeckte Zweige'))
print('-' * 86)
n = 0
for e in ordner:
    o = e if os.path.isdir(e) else os.path.join(ARBEIT, e)
    r = pruefe(o)
    if r is None:
        continue
    art, offen = r
    if art == 'kein Vergleich':
        continue
    if offen:
        n += 1
    print('%-30s %-34s %s' % (os.path.basename(o)[16:45], art,
                              ('ROT ' + ', '.join('Z.%d' % x[0] for x in offen))
                              if offen else 'keine'))
print('-' * 86)
print('%d Linie(n) mit ungedeckten Zweigen' % n)
