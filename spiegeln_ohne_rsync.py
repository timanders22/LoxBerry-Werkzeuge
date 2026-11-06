#!/usr/bin/env python3
"""Ersatz fuer die eine rsync-Zeile in linie_veroeffentlichen.sh.

ANLASS: auf diesem Rechner gibt es kein rsync (gemessen am 13.09.2026:
`command -v rsync` leer), und damit bricht linie_veroeffentlichen.sh in
Zeile 34 ab. 1.3.13 ist schon einmal mit einem solchen Ersatz geschoben
worden; der lag im Arbeitsverzeichnis einer Sitzung und ist nicht mehr da.
Deshalb hier, im Werkzeugordner, wo er bleibt.

Nachgebildet wird GENAU diese Zeile:

    rsync -rt --delete --no-perms --no-owner --no-group --exclude=.git
      --exclude=.gitignore --exclude=.gitattributes --exclude='*.zip'
      --exclude='STAND_IN_ARBEIT.md' --exclude='FREIGABE_*' "$o/" ./

  -rt                     rekursiv, Zeitstempel mitnehmen
  --delete                im ZIEL entfernen, was in der QUELLE fehlt
  --no-perms/-owner/-group  keine Rechte, kein Eigentuemer
  --exclude=...           weder uebertragen NOCH durch --delete anfassen

Der letzte Punkt ist der wichtige und der einzige, den ein naiver Nachbau
falsch macht: eine ausgenommene Datei, die im Ziel liegt (z. B. eine
repository-eigene .gitattributes eines Fremd-Forks), darf NICHT geloescht
werden, nur weil sie in der Quelle fehlt.

Aufruf:
    python3 spiegeln_ohne_rsync.py QUELLE ZIEL [--probe]

--probe schreibt nichts und zeigt nur, was geschehen wuerde.
Rueckgabe 0, wenn die Spiegelung stimmt; sonst 1.
"""
import fnmatch
import os
import shutil
import sys

AUSNAHMEN = ('.git', '.gitignore', '.gitattributes', '*.zip',
             'STAND_IN_ARBEIT.md', 'FREIGABE_*')


def ausgenommen(name):
    """Trifft eine der Ausnahmen auf diesen BASISNAMEN zu?

    rsync vergleicht ein Muster ohne Schraegstrich gegen den Basisnamen auf
    JEDER Ebene - nicht nur in der Wurzel. '*.zip' trifft also auch
    unterordner/x.zip.
    """
    return any(fnmatch.fnmatch(name, m) for m in AUSNAHMEN)


def sammeln(wurzel):
    """Relative Pfade aller Dateien unter wurzel, Ausnahmen ausgelassen."""
    out = set()
    for weg, ordner, dateien in os.walk(wurzel):
        # Ausgenommene ORDNER gar nicht erst betreten (.git!).
        ordner[:] = [d for d in ordner if not ausgenommen(d)]
        for d in dateien:
            if ausgenommen(d):
                continue
            p = os.path.relpath(os.path.join(weg, d), wurzel)
            out.add(p.replace(os.sep, '/'))
    return out


def main(argv):
    probe = '--probe' in argv
    reste = [a for a in argv if not a.startswith('--')]
    unbekannt = [a for a in argv if a.startswith('--') and a != '--probe']
    if unbekannt:
        sys.stderr.write('ABBRUCH: unbekannte(r) Schalter %s\n'
                         % ', '.join(unbekannt))
        return 2
    if len(reste) != 2:
        sys.stderr.write(__doc__)
        return 2
    quelle, ziel = reste
    for p in (quelle, ziel):
        if not os.path.isdir(p):
            sys.stderr.write('ABBRUCH: %s ist kein Verzeichnis\n' % p)
            return 2

    q = sammeln(quelle)
    z = sammeln(ziel)
    neu = sorted(q - z)
    weg = sorted(z - q)
    gleich = sorted(q & z)

    geaendert = []
    for rel in gleich:
        a = os.path.join(quelle, rel.replace('/', os.sep))
        b = os.path.join(ziel, rel.replace('/', os.sep))
        try:
            if os.path.getsize(a) != os.path.getsize(b):
                geaendert.append(rel)
                continue
            with open(a, 'rb') as fa, open(b, 'rb') as fb:
                if fa.read() != fb.read():
                    geaendert.append(rel)
        except OSError as f:
            sys.stderr.write('ABBRUCH: %s\n' % f)
            return 1

    print('  Quelle %d Datei(en), Ziel %d Datei(en)' % (len(q), len(z)))
    print('  neu: %d   geaendert: %d   zu entfernen: %d'
          % (len(neu), len(geaendert), len(weg)))
    for rel in neu:
        print('    + %s' % rel)
    for rel in geaendert:
        print('    ~ %s' % rel)
    for rel in weg:
        print('    - %s' % rel)

    if probe:
        print('  --probe: nichts geschrieben')
        return 0

    for rel in neu + geaendert:
        a = os.path.join(quelle, rel.replace('/', os.sep))
        b = os.path.join(ziel, rel.replace('/', os.sep))
        os.makedirs(os.path.dirname(b), exist_ok=True)
        # copy2 nimmt den Zeitstempel mit (rsync -t), NICHT den Modus:
        # shutil.copy2 kopiert zwar auch die Rechte, aber im Klon entscheidet
        # ohnehin git ueber den Modus (core.fileMode), und der Zielmodus wird
        # unten nachgeprueft.
        shutil.copyfile(a, b)
        shutil.copystat(a, b)
    for rel in weg:
        os.remove(os.path.join(ziel, rel.replace('/', os.sep)))

    # Leergeraeumte Ordner entfernen, wie rsync --delete es tut.
    for weg_, ordner, dateien in os.walk(ziel, topdown=False):
        if ausgenommen(os.path.basename(weg_)):
            continue
        if not os.listdir(weg_) and os.path.abspath(weg_) != os.path.abspath(ziel):
            os.rmdir(weg_)

    # NACHPRUEFEN statt hoffen: danach muessen beide Seiten deckungsgleich
    # sein. Genau diese Zeile hat bei 1.3.13 den Unterschied gemacht.
    q2 = sammeln(quelle)
    z2 = sammeln(ziel)
    if q2 != z2:
        sys.stderr.write('ABBRUCH: nach der Spiegelung nicht deckungsgleich\n')
        sys.stderr.write('  nur in der Quelle: %s\n' % sorted(q2 - z2))
        sys.stderr.write('  nur im Ziel:       %s\n' % sorted(z2 - q2))
        return 1
    ungleich = []
    for rel in sorted(q2):
        a = os.path.join(quelle, rel.replace('/', os.sep))
        b = os.path.join(ziel, rel.replace('/', os.sep))
        with open(a, 'rb') as fa, open(b, 'rb') as fb:
            if fa.read() != fb.read():
                ungleich.append(rel)
    if ungleich:
        sys.stderr.write('ABBRUCH: byteweise verschieden: %s\n' % ungleich)
        return 1
    print('  nachgeprueft: %d Datei(en) byteweise gleich' % len(q2))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
