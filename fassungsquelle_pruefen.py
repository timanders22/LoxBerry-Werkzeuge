# -*- coding: utf-8 -*-
"""Woher holt sich eine Linie ihre eigene Fassungsnummer?

Aufruf:
    python3 Werkzeuge/fassungsquelle_pruefen.py [ORDNER ...]

Ohne Argument: je hoechste Fassung jeder Linie im Arbeitsordner.
Rein lesend. Rueckgabewert 1, sobald eine Linie im Ausgang BEFUND steht.

ANLASS (Intercom 2.2.9, 07.09.2026, am Geraet gemessen)
-------------------------------------------------------
`plugininstall.pl` liest die `plugin.cfg` aus dem Auspackordner und LOESCHT
sie danach - installiert wird sie nirgendwohin (Installationsprotokoll:
"removed .../LoxBerry-Plugin-Intercom-2.2.8/plugin.cfg"). Jede Linie, die
ihre Fassung nur aus Dateien liest, bekommt auf einer Installation eine leere
Zeichenkette. Bei Intercom stand deshalb im Reiter Test dauerhaft "Wird die
plugin.cfg gefunden? nein", und `?selftest=1` antwortete `"version":""`.

Die einzige Quelle, die im installierten Zustand vorliegt, ist
`data/system/plugindatabase.json` (644, lesbar). Gesucht wird dort ueber den
ORDNERNAMEN, nie ueber den MD5-Schluessel: der entsteht aus Autorenname,
E-Mail und Plugin-Name und aendert sich bei jedem Fork.

WAS DIESES WERKZEUG KANN - UND WAS NICHT
----------------------------------------
Es liest Text. Zwei Ausgaenge sind belegbar, ein dritter ist eine Frage:

  BEFUND   Die Linie fasst `plugin.cfg` an, erwaehnt `plugindatabase` aber
           NIRGENDS. Dann gibt es auf einer Installation keine Quelle - das
           ist aus dem Text sicher.
  ANSEHEN  Beides kommt vor. Ob die Datenbank wirklich als JSON gelesen wird,
           kann eine Textsuche nicht entscheiden: ein Wrapper (`rk_json_lesen()`)
           versteckt den `json_decode`, und umgekehrt beweist ein `json_decode`
           irgendwo in der Linie gar nichts. Ein erster Anlauf am 07.09.2026
           hat genau daran zweimal danebengegriffen - erst Bewaesserung
           faelschlich als heil, dann Raumklima faelschlich als kaputt.
           Deshalb: von Hand ansehen, und das Werkzeug sagt, wo.
  KEINE    Die Linie fasst `plugin.cfg` gar nicht an. Ob sie ueberhaupt eine
           Fassung anzeigt, ist eine andere Frage - die misst dieses Werkzeug
           nicht.

Von Hand nachgesehen am 07.09.2026 (Stichprobe aus der Gruppe ANSEHEN):
  Intercom 2.2.9, Robonect 1.1.10, Raumklima 0.11.6, Tibber 0.9.12  in Ordnung
  Bewaesserung 0.9.25                                               BEFUND -
      der Rueckfall greift mit /^VERSION=([0-9][0-9.]*)/m in die
      plugindatabase.json. Dort steht kein VERSION= - es ist JSON. Der
      Rueckfall sieht richtig aus und trifft nie. Das ist der gefaehrlichere
      Fall: ohne Rueckfall faellt es auf, mit einem scheinbaren nicht.
"""
import os
import re
import sys


def nummer(n):
    m = re.search(r'-(\d+)\.(\d+)\.(\d+)$', n)
    return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)


def hoechste_je_linie(wurzel):
    linien = {}
    for d in sorted(os.listdir(wurzel)):
        if d.startswith('LoxBerry-Plugin-') and os.path.isdir(os.path.join(wurzel, d)):
            linien.setdefault(re.sub(r'-\d+\.\d+\.\d+$', '', d), []).append(d)
    return [os.path.join(wurzel, max(v, key=nummer)) for v in linien.values()]


def code_ohne_kommentare(pfad):
    """Alle Programmzeilen der Linie, Kommentarzeilen entfernt."""
    aus = []
    for w, _, ds in os.walk(pfad):
        for f in ds:
            if not f.endswith(('.php', '.pl', '.py')):
                continue
            try:
                t = open(os.path.join(w, f), encoding='utf-8', errors='replace').read()
            except Exception:
                continue
            for nr, z in enumerate(t.splitlines(), 1):
                s = z.strip()
                if s.startswith(('*', '//', '#', '/*')):
                    continue
                aus.append((os.path.relpath(os.path.join(w, f), pfad).replace(os.sep, '/'),
                            nr, z))
    return aus


def beurteilen(pfad):
    zeilen = code_ohne_kommentare(pfad)
    cfg = [(f, nr) for f, nr, z in zeilen if 'plugin.cfg' in z]
    db = [(f, nr) for f, nr, z in zeilen if 'plugindatabase' in z]
    # BERICHTIGT 07.09.2026 nach der Messung am Geraet: es gibt einen DRITTEN
    # Weg, und er ist der vorgesehene - LBSystem::pluginversion() aus dem
    # LoxBerry-SDK (loxberry_system.php:403). Er liest die Plugin-Datenbank
    # selbst. Ohne ihn meldete dieses Werkzeug Pumpenwacht und
    # Smartmeter-classic als BEFUND, obwohl beide am Geraet die richtige
    # Fassung liefern (gemessen: EIGEN=[0.9.13] bzw. EIGEN=[2.8.0]).
    sdk = [(f, nr) for f, nr, z in zeilen if 'pluginversion' in z]
    if not cfg and not db and not sdk:
        return 'KEINE', []
    if sdk:
        return 'SDK', sdk
    if cfg and not db:
        return 'BEFUND', cfg
    return 'ANSEHEN', db


if __name__ == '__main__':
    argv = [a for a in sys.argv[1:] if not a.startswith('--')]
    ordner = argv if argv else hoechste_je_linie('.')
    if not ordner:
        print('Kein Plugin-Ordner gefunden.')
        sys.exit(2)
    eimer = {'BEFUND': [], 'ANSEHEN': [], 'SDK': [], 'KEINE': []}
    for d in sorted(ordner):
        art, stellen = beurteilen(d)
        eimer[art].append((os.path.basename(d.rstrip(os.sep)), stellen))

    print('%d Linie(n) angesehen\n' % len(ordner))
    print('== BEFUND (%d) - liest plugin.cfg, kennt die Datenbank nicht:'
          % len(eimer['BEFUND']))
    print('   auf einer Installation ist die Fassung dort LEER.')
    for n, st in eimer['BEFUND']:
        print('   %-46s %s' % (n, ', '.join('%s:%d' % s for s in st[:2])))
    print()
    print('== ANSEHEN (%d) - beides kommt vor, die Textsuche entscheidet es nicht:'
          % len(eimer['ANSEHEN']))
    for n, st in eimer['ANSEHEN']:
        print('   %-46s %s' % (n, ', '.join('%s:%d' % s for s in st[:2])))
    print()
    print('== SDK (%d) - ruft LBSystem::pluginversion() auf - der vorgesehene Weg'
          % len(eimer['SDK']))
    for n, st in eimer['SDK']:
        print('   %-46s %s' % (n, ', '.join('%s:%d' % s for s in st[:2])))
    print()
    print('== KEINE (%d) - fasst plugin.cfg im Code nicht an' % len(eimer['KEINE']))
    for n, _ in eimer['KEINE']:
        print('   ' + n)
    print()
    print('Die Zahl der Zeilen ist kein Urteil. Wer eine Linie berichtigt, sieht')
    print('in die genannten Stellen hinein - und prueft die Behebung an einer')
    print('nachgebauten INSTALLIERTEN Lage, nicht am Arbeitsordner: dort trifft')
    print('der Archivfall der Kandidatenliste immer, und die Pruefung misst nichts.')
    sys.exit(1 if eimer['BEFUND'] else 0)
