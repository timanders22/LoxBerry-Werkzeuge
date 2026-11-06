#!/usr/bin/env python3
"""Eichung fuer cfg_abweichung.erklaerbar() - in BEIDE Richtungen.

Zu jedem Fall, der gruen werden soll, gehoert ein Beinahefall, der rot
bleiben muss. Sonst ist die Ausnahme ein ungemessenes Loch: sie erklaert
vielleicht auch das weg, wofuer es den Waechter gibt.

Aufruf:  python3 cfg_abweichung_eichung.py
Rueckgabe 0 nur, wenn JEDER Fall so ausgeht wie vorgesehen.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfg_abweichung import erklaerbar                      # noqa: E402

REPO = 'https://github.com/timanders22/LoxBerry-Plugin-Beschattungswaechter'


def cfg(version, kommentar='', repo=REPO, zusatz='', kopf='[AUTOUPDATE]'):
    """Eine release.cfg bauen - so, wie sie im Bestand aussieht."""
    zeilen = [kopf]
    if kommentar:
        zeilen += ['# ' + z for z in kommentar.split('\n')]
    zeilen += [
        'VERSION=%s' % version,
        'ARCHIVEURL=%s/archive/refs/tags/v%s.zip' % (repo, version),
        'INFOURL=%s/releases/tag/v%s' % (repo, version),
    ]
    if zusatz:
        zeilen.append(zusatz)
    return ('\n'.join(zeilen) + '\n').encode('utf-8')


PFLEGE_ALT = 'Bei jedem Release drei Stellen gleichzeitig anfassen:\n  1. plugin.cfg\n  2. release.cfg'
PFLEGE_NEU = ('Bei jedem Release vier Stellen gleichzeitig anfassen:\n  1. plugin.cfg\n'
              '  2. release.cfg -> DIESE Datei\n  3. prerelease.cfg\n  4. das Release')

FAELLE = [
    # (Name, alt (Tag), neu (Ordner), soll_gruen)
    ('der Fall, um den es geht: Nummer hoeher UND Kommentar ergaenzt',
     cfg('0.9.12', PFLEGE_ALT), cfg('0.9.13', PFLEGE_NEU), True),
    ('der alte Fall: nur die Nummer, Kommentar unveraendert',
     cfg('0.9.12', PFLEGE_ALT), cfg('0.9.13', PFLEGE_ALT), True),
    ('Nummer hoeher, Kommentar ganz entfernt',
     cfg('1.1.2', PFLEGE_ALT), cfg('1.1.3'), True),
    ('Nummer hoeher, Kommentar neu dazugekommen',
     cfg('2.0.4'), cfg('2.1.0', PFLEGE_NEU), True),
    ('Zeilenenden verschieden, sonst wie oben',
     cfg('0.9.12', PFLEGE_ALT).replace(b'\n', b'\r\n'), cfg('0.9.13', PFLEGE_NEU), True),
    ('Nummer mit mehr Stellen (0.9.9 -> 0.9.10)',
     cfg('0.9.9'), cfg('0.9.10'), True),

    ('DIESELBE Nummer, Kommentar geaendert',
     cfg('0.9.13', PFLEGE_ALT), cfg('0.9.13', PFLEGE_NEU), False),
    ('der Ordner traegt die NIEDRIGERE Nummer',
     cfg('0.9.13'), cfg('0.9.12'), False),
    ('ARCHIVEURL zeigt auf ein FREMDES Repository',
     cfg('0.9.12'),
     cfg('0.9.13', repo='https://github.com/jemand-anders/LoxBerry-Plugin-Beschattungswaechter'),
     False),
    ('INFOURL zeigt auf einen anderen Tag als ARCHIVEURL',
     cfg('0.9.12'),
     cfg('0.9.13').replace(b'/releases/tag/v0.9.13', b'/releases/tag/v0.9.11'),
     False),
    ('ein Schluessel kommt dazu',
     cfg('0.9.12'), cfg('0.9.13', zusatz='PRERELEASE=true'), False),
    ('ein Schluessel faellt weg',
     cfg('0.9.12', zusatz='PRERELEASE=true'), cfg('0.9.13'), False),
    ('ein Schluessel wird umbenannt',
     cfg('0.9.12'), cfg('0.9.13').replace(b'INFOURL=', b'INFOADRESSE='), False),
    ('der Abschnittskopf ist ein anderer',
     cfg('0.9.12'), cfg('0.9.13', kopf='[UPDATE]'), False),
    ('VERSION ist keine Nummer',
     cfg('0.9.12'), cfg('0.9.13').replace(b'VERSION=0.9.13', b'VERSION=neuestens'), False),
    ('eine unbekannte wirksame Zeile aendert sich',
     cfg('0.9.12', zusatz='irgendwas ohne Gleichheitszeichen'),
     cfg('0.9.13', zusatz='etwas anderes ohne Gleichheitszeichen'), False),
]

print('== Eichung cfg_abweichung.erklaerbar ==\n')
fehler = 0
for name, alt, neu, soll in FAELLE:
    ist, grund = erklaerbar(alt, neu)
    gut = (ist == soll)
    if not gut:
        fehler += 1
    print('  %-6s %-58s %-5s   %s'
          % ('ok' if gut else 'FEHL',
             name,
             'gruen' if ist else 'rot',
             grund))

print('\n%d Faelle, %d gruen erwartet, %d rot erwartet, %d Abweichung(en)'
      % (len(FAELLE), sum(1 for f in FAELLE if f[3]),
         sum(1 for f in FAELLE if not f[3]), fehler))
if fehler:
    print('Die Ausnahme misst NICHT, was sie messen soll.')
sys.exit(1 if fehler else 0)
