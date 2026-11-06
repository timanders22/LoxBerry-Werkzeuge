#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schluessel-Wert-Abbild einer `templates/lang`-Ablage festhalten und halten.

WOZU
====
Wenn ein Sprachdatei-Erzeuger nach laengerer Pause wieder laeuft, schreibt er
die `.ini` in SEINER Reihenfolge - und die kann von der gewachsenen Ordnung der
ausgelieferten Datei abweichen. Der Diff ist dann gross und inhaltsleer, und
genau darin verschwindet ein echter Befund.

Ein ZEILENVERGLEICH taugt dafuer nicht. Das richtige Mittel ist die Menge der
Schluessel mit ihren Werten:

    sprachwache.schluessel(text)  ->  {ABSCHNITT.NAME: Wert}

Dieses Werkzeug haelt dieses Abbild VOR einer Aenderung fest und danach
dagegen. Erwartet wird: gleich viele Schluessel, keiner nur auf einer Seite,
kein abweichender Wert. Nur die Zeilenfolge darf sich unterscheiden.

Anlass: APC-UPS 1.2.7 -> 1.2.8, 13.09.2026. Dort: 338 gegen 338, kein
Schluessel nur auf einer Seite, kein abweichender Wert; 55 Zeilen je Seite
verschoben.

AUFRUF
======
    python3 sprachabbild.py sichern <lang-Ordner> <ziel.json>
    python3 sprachabbild.py halten  <vorher.json> <lang-Ordner>

    --sprachen de,en    welche language_<x>.ini gemeint sind (Vorgabe de,en)

Rueckgabe 0 = kein Unterschied ausser der Zeilenfolge, 1 = Befund,
2 = Aufrufproblem oder nichts gemessen.

Rein lesend fuer die Sprachdateien; `sichern` schreibt genau die genannte
JSON-Datei und sonst nichts.
"""
import io
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import sprachwache


def _feste(argv, wertflaggen):
    """Die Argumente ohne Schalter - und ohne deren WERTE.

    Ohne diese Unterscheidung landet der Wert eines Schalters in getrennter
    Schreibweise (`--sprachen de,en`) unter den festen Argumenten, und die
    Zaehlung darunter weist einen richtigen Aufruf ab.
    """
    aus = []
    ueberspringen = False
    for a in argv:
        if ueberspringen:
            ueberspringen = False
            continue
        if a.startswith('--'):
            ueberspringen = a in wertflaggen
            continue
        aus.append(a)
    return aus


def _sprachen(argv):
    for i, a in enumerate(argv):
        if a == '--sprachen' and i + 1 < len(argv):
            return [s.strip() for s in argv[i + 1].split(',') if s.strip()]
        if a.startswith('--sprachen='):
            return [s.strip() for s in a.split('=', 1)[1].split(',') if s.strip()]
    return ['de', 'en']


def lies(ordner, sp):
    """Die Schluessel einer language_<sp>.ini. Fehlt die Datei: None."""
    pfad = os.path.join(ordner, 'language_%s.ini' % sp)
    if not os.path.isfile(pfad):
        return None
    return sprachwache.schluessel(io.open(pfad, 'rb').read().decode('utf-8'))


def sichern(ordner, ziel, sprachen):
    ab = {}
    for sp in sprachen:
        d = lies(ordner, sp)
        if d is None:
            sys.stderr.write('ABBRUCH: language_%s.ini fehlt unter %s\n' % (sp, ordner))
            return 2
        ab[sp] = d
        print('  %s: %d Schluessel' % (sp, len(d)))
    # Eine leere Menge ist kein Abbild, sondern ein Messfehler.
    if not ab or not any(ab.values()):
        sys.stderr.write('ABBRUCH: kein einziger Schluessel gelesen - nichts gemessen\n')
        return 2
    with io.open(ziel, 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(ab, ensure_ascii=False, indent=1, sort_keys=True))
    print('festgehalten in %s' % ziel)
    return 0


def halten(vorher, ordner, sprachen):
    with io.open(vorher, 'r', encoding='utf-8') as fh:
        alt = json.load(fh)
    if not alt:
        sys.stderr.write('ABBRUCH: das Abbild ist leer - nichts zu vergleichen\n')
        return 2
    fehl = 0
    gemessen = 0
    for sp in sprachen:
        if sp not in alt:
            print('  %s: im Abbild nicht enthalten - NICHT gemessen' % sp)
            fehl += 1
            continue
        a = alt[sp]
        n = lies(ordner, sp)
        if n is None:
            print('  %s: language_%s.ini fehlt jetzt - NICHT gemessen' % (sp, sp))
            fehl += 1
            continue
        gemessen += 1
        nur_a = sorted(set(a) - set(n))
        nur_n = sorted(set(n) - set(a))
        anders = sorted(k for k in set(a) & set(n) if a[k] != n[k])
        print('--- %s: vorher %d, jetzt %d' % (sp, len(a), len(n)))
        for k in nur_a:
            print('  NUR VORHER   %s = %s' % (k, a[k]))
            fehl += 1
        for k in nur_n:
            print('  NUR JETZT    %s = %s' % (k, n[k]))
            fehl += 1
        for k in anders:
            print('  ANDERER WERT %s' % k)
            print('      vorher: %s' % a[k])
            print('      jetzt : %s' % n[k])
            fehl += 1
        if not (nur_a or nur_n or anders):
            print('  kein Schluessel nur auf einer Seite, kein abweichender Wert')
    if gemessen == 0:
        print('NICHTS GEMESSEN - das ist kein sauberer Lauf.')
        return 2
    print('%d Sprache(n) gemessen, %d Befund(e)' % (gemessen, fehl))
    return 1 if fehl else 0


if __name__ == '__main__':
    argv = sys.argv[1:]
    fest = _feste(argv, ('--sprachen',))
    if len(fest) != 3 or fest[0] not in ('sichern', 'halten'):
        sys.stderr.write(__doc__.split('AUFRUF')[1].strip() + '\n')
        sys.exit(2)
    sprachen = _sprachen(argv)
    if fest[0] == 'sichern':
        sys.exit(sichern(fest[1], fest[2], sprachen))
    sys.exit(halten(fest[1], fest[2], sprachen))
