#!/usr/bin/env python3
"""Zwei Plugin-Archive byteweise vergleichen - je Eintrag ueber eine Pruefsumme.

Der Beleg dafuer, dass nur geaendert wurde, was geaendert werden sollte.

Der Anlass, 20.08.2026: an einem Nachmittag wurden vier fremde Plugins
korrigiert. Die Frage ist dabei nicht "laeuft es noch", sondern "was habe ich
sonst noch angefasst". Ein Blick in den Ordner beantwortet das nicht -
Zeitstempel aendern sich beim Kopieren, und eine versehentlich mitgeschleppte
Datei sieht aus wie jede andere.

Der Vergleich hat in jenem Lauf zwei Dinge gefunden, die sonst mitgegangen
waeren: die Laufzeitdateien, die der Selbsttest des Plugins im Arbeitsordner
hinterlaesst (Merker und Protokoll), und eine plugin.cfg mit gemischten
Zeilenenden.

Rein lesend. Aufruf:

    python3 archivdiff.py ALT.zip NEU.zip

Erwartet wird eine kurze, vollstaendig erklaerbare Liste. Jede Zeile mehr ist
eine Frage - besonders dann, wenn die Aenderung klein war. Bei einer kleinen
Aenderung sieht man am wenigsten hin.

Rueckgabewert 1, sobald es einen Unterschied gibt - auch den erwarteten.
Dieses Werkzeug urteilt nicht, es zaehlt auf.
"""
import hashlib
import sys
import zipfile
from pathlib import Path


def inhalt(pfad):
    z = zipfile.ZipFile(pfad)
    return {n: hashlib.sha256(z.read(n)).hexdigest()
            for n in z.namelist() if not n.endswith('/')}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 2:
        print('Aufruf: python3 archivdiff.py ALT.zip NEU.zip')
        return 2
    alt, neu = Path(args[0]), Path(args[1])
    for p in (alt, neu):
        if not p.is_file():
            print('Kein Archiv: %s' % p)
            return 2

    a, b = inhalt(alt), inhalt(neu)
    print('== %s  ->  %s' % (alt.name, neu.name))
    zeilen = []
    for n in sorted(set(a) | set(b)):
        if n not in a:
            zeilen.append(('NEU      ', n))
        elif n not in b:
            zeilen.append(('WEG      ', n))
        elif a[n] != b[n]:
            zeilen.append(('GEAENDERT', n))
    for art, n in zeilen:
        print('   %s  %s' % (art, n))
    if not zeilen:
        print('   kein Unterschied - dieselbe Nummer waere also richtig')
    else:
        print('   %d Eintrag/Eintraege. Jeder gehoert erklaert.' % len(zeilen))
    print('   Dateien: %d -> %d, Byte: %d -> %d'
          % (len(a), len(b), alt.stat().st_size, neu.stat().st_size))
    return 1 if zeilen else 0


if __name__ == '__main__':
    sys.exit(main())
