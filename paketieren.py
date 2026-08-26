#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Packt einen Plugin-Ordner zu einem ZIP - und weist ab, was nicht hineingehoert.

Aufruf:
    python paketieren.py <Ordner> [<Ziel.zip>]
    python paketieren.py <Ordner> --pruefen      nur pruefen, nichts schreiben

Warum es dieses Werkzeug gibt: dreimal in einer Sitzung ist ein __pycache__ in
einen Plugin-Ordner geraten, weil Sonden Plugin-Code importiert haben. Gefunden
hat es jedes Mal erst der Zufall beim Packen. Hier bricht es ab.

Das Werkzeug schreibt NICHT in den Quellordner. Es raeumt auch nicht auf - es
sagt, was wegmuss, und ueberlaesst das Entfernen dem Menschen. Ein Packwerkzeug,
das loescht, ist ein Loeschwerkzeug mit Nebenwirkung.

Nach dem Schreiben liest es das Archiv zurueck und vergleicht jede Datei
byteweise mit dem Ordner. Ohne diese Gegenprobe ist "gepackt" nur eine
Behauptung.
"""

import os
import sys
import zipfile

# Was nie ins Archiv gehoert. Ordnernamen und Dateiendungen getrennt, damit
# eine Datei namens "cache.py" nicht faelschlich anspringt.
VERBOTENE_ORDNER = ('__pycache__', '.git', '.idea', '.vscode', 'node_modules')
VERBOTENE_ENDUNGEN = ('.pyc', '.pyo', '.orig', '.rej', '.bak', '.swp')
VERBOTENE_NAMEN = ('.DS_Store', 'Thumbs.db', 'desktop.ini')


def sammeln(wurzel):
    """Alle Dateien relativ zur Wurzel, mit Schrägstrich als Trenner."""
    treffer = []
    for verzeichnis, _unter, dateien in os.walk(wurzel):
        for datei in dateien:
            voll = os.path.join(verzeichnis, datei)
            rel = os.path.relpath(voll, wurzel).replace(os.sep, '/')
            treffer.append((rel, voll))
    treffer.sort()
    return treffer


def beanstanden(dateien):
    """Liefert die Liste der Eintraege, die nicht ins Archiv duerfen."""
    schlecht = []
    for rel, _voll in dateien:
        teile = rel.split('/')
        name = teile[-1]
        if any(t in VERBOTENE_ORDNER for t in teile[:-1]):
            schlecht.append((rel, 'liegt in einem Ordner, der nicht mitgeht'))
        elif name.endswith(VERBOTENE_ENDUNGEN):
            schlecht.append((rel, 'Endung gehoert nicht ins Archiv'))
        elif name in VERBOTENE_NAMEN:
            schlecht.append((rel, 'Beiwerk des Betriebssystems'))
    return schlecht


def packen(wurzel, ziel, dateien):
    """Schreibt das Archiv - mit Ordnereintraegen, wie LoxBerry sie erwartet."""
    ordner = set()
    for rel, _voll in dateien:
        teile = rel.split('/')[:-1]
        for i in range(len(teile)):
            ordner.add('/'.join(teile[:i + 1]) + '/')
    with zipfile.ZipFile(ziel, 'w', zipfile.ZIP_DEFLATED) as archiv:
        for eintrag in sorted(ordner):
            archiv.writestr(eintrag, b'')
        for rel, voll in dateien:
            archiv.write(voll, rel)


def gegenprobe(wurzel, ziel):
    """Liest das Archiv zurueck und vergleicht byteweise. Liefert (gleich, gesamt)."""
    gleich = 0
    with zipfile.ZipFile(ziel) as archiv:
        namen = [n for n in archiv.namelist() if not n.endswith('/')]
        for name in namen:
            pfad = os.path.join(wurzel, name.replace('/', os.sep))
            with open(pfad, 'rb') as datei:
                if datei.read() == archiv.read(name):
                    gleich += 1
                else:
                    print('  [FEHL] weicht ab: %s' % name)
    return gleich, len(namen)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    wurzel = os.path.abspath(argv[1].rstrip('/\\'))
    if not os.path.isdir(wurzel):
        print('[FEHL] kein Ordner: %s' % wurzel)
        return 1

    nur_pruefen = '--pruefen' in argv[2:]
    ziel = None
    for wert in argv[2:]:
        if not wert.startswith('--'):
            ziel = os.path.abspath(wert)
    if ziel is None:
        ziel = wurzel + '.zip'

    dateien = sammeln(wurzel)
    if not dateien:
        print('[FEHL] der Ordner ist leer')
        return 1

    schlecht = beanstanden(dateien)
    if schlecht:
        print('[FEHL] %d Eintrag/Eintraege gehoeren nicht ins Archiv:' % len(schlecht))
        for rel, grund in schlecht:
            print('       %s  --  %s' % (rel, grund))
        print('')
        print('       Nichts geschrieben. Entfernen Sie die Eintraege und rufen Sie')
        print('       erneut auf. Bei __pycache__ hilft dauerhaft:')
        print('           PYTHONDONTWRITEBYTECODE=1 vor jedem Lauf, der Plugin-')
        print('           Code importiert.')
        return 1

    print('[OK]   %d Dateien, nichts Verbotenes darunter' % len(dateien))
    if nur_pruefen:
        return 0

    if os.path.exists(ziel):
        os.remove(ziel)
    packen(wurzel, ziel, dateien)
    gleich, gesamt = gegenprobe(wurzel, ziel)
    if gleich != gesamt:
        print('[FEHL] Gegenprobe: nur %d von %d Dateien stimmen ueberein' % (gleich, gesamt))
        return 1
    print('[OK]   Gegenprobe: %d von %d Dateien byteweise gleich' % (gleich, gesamt))
    print('[OK]   geschrieben: %s (%d Bytes)' % (ziel, os.path.getsize(ziel)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
