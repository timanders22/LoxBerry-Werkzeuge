#!/usr/bin/env python3
"""Zeilenenden je Datei melden - binaer gelesen, nie ueber read_text().

Grund steht in REGELN_1: read_text() uebersetzt unter Windows still, und
eine Zaehlung darueber misst die Uebersetzung, nicht die Datei.
"""
import os
import sys


def art(pfad):
    b = open(pfad, 'rb').read()
    if b'\x00' in b[:8000]:
        return 'BINAER', 0, 0
    crlf = b.count(b'\r\n')
    lf = b.count(b'\n') - crlf
    if crlf and not lf:
        return 'CRLF', crlf, lf
    if lf and not crlf:
        return 'LF', crlf, lf
    if not crlf and not lf:
        return 'leer', 0, 0
    return 'GEMISCHT', crlf, lf


def lage(basis):
    aus = {}
    for w, _, fs in os.walk(basis):
        for f in sorted(fs):
            p = os.path.join(w, f)
            rel = os.path.relpath(p, basis).replace(os.sep, '/')
            aus[rel] = art(p)
    return aus


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Aufruf: zeilenenden_lage.py <ordner> [<vergleichsordner>]')
        print('        Meldet je Datei CRLF, LF, GEMISCHT oder BINAER.')
        print('        GEMISCHT ist ein Befund (Rueckgabe 1); ohne Ordner')
        print('        wurde nichts angesehen (Rueckgabe 2).')
        sys.exit(2)
    basis = sys.argv[1]
    if not os.path.isdir(basis):
        print('Kein Verzeichnis: %s - es wurde nichts angesehen.' % basis)
        sys.exit(2)
    if len(sys.argv) > 2 and not os.path.isdir(sys.argv[2]):
        print('Vergleichsordner ist kein Verzeichnis: %s' % sys.argv[2])
        sys.exit(2)
    vergleich = lage(sys.argv[2]) if len(sys.argv) > 2 else None
    ist = lage(basis)
    befunde = 0
    for rel in sorted(ist):
        a, crlf, lf = ist[rel]
        zusatz = ''
        if vergleich is not None:
            if rel not in vergleich:
                zusatz = '   (neu)'
            elif vergleich[rel][0] != a:
                zusatz = '   ABWEICHUNG, vorher %s' % vergleich[rel][0]
                befunde += 1
        if a == 'GEMISCHT':
            zusatz += '   BEFUND: %d CRLF, %d LF' % (crlf, lf)
            befunde += 1
        print('  %-8s %s%s' % (a, rel, zusatz))
    if vergleich is not None:
        for rel in sorted(set(vergleich) - set(ist)):
            print('  ENTFALLEN %s' % rel)
    print('%d Dateien angesehen, %d Befund(e).' % (len(ist), befunde))
    if not ist:
        print('ACHTUNG: es wurde keine einzige Datei angesehen.')
        sys.exit(2)
    sys.exit(1 if befunde else 0)
