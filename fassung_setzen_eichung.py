#!/usr/bin/env python3
"""Eichung der README-Kopfzeile in `fassung_setzen.py`.

Anlass (25.08.2026): das Werkzeug fand die Kopfzeile nur, wenn sie mit
"Version" am ZEILENANFANG stand. Beim Zendure-Plugin steht sie als Zitat
(`> **Version 0.9.15 - ...**`); dort meldete es `README.md ?` und schrieb
stillschweigend nichts.

Die naheliegende Nachbesserung - ein weiteres Muster - waere GEFAEHRLICH
gewesen. Im Bestand stehen Zeilen, die genauso aussehen und NICHT angefasst
werden duerfen:

    ## Version 3.0.9 - Stoercodes im Klartext     Abschnittsueberschrift
    Version 0.2.31, Apache-Lizenz 2.0             Fassung eines FREMDEN Autors

Der erste Fall ist der teure: WOLF-ISM-NG 3.0.9 traegt eine Ueberschrift mit
GENAU der aktuellen Nummer. Ein gieriges Muster haette sie beim naechsten
Hochsetzen umgeschrieben - und damit die Geschichte gefaelscht.

    python3 fassung_setzen_eichung.py

Rueckgabe 0, wenn alle Faelle so ausgehen wie erwartet.
"""
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
KOPFZEILEN = 20


def readme_kopfzeile(d, alte_fassung):
    """Dieselbe Logik wie in fassung_setzen.py - hier zum Eichen isoliert.

    Aenderungen dort gehoeren HIER mitgezogen; laeuft die Eichung danach
    nicht mehr, ist das die Meldung, auf die es ankommt.
    """
    if not alte_fassung:
        return (None, None)
    ziel = alte_fassung.encode() if isinstance(alte_fassung, str) else alte_fassung
    zeilen = d.split(b'\n')[:KOPFZEILEN]
    muster = rb'(?<![0-9.])Version[ :]+' + re.escape(ziel) + rb'(?![0-9])'
    for i, z in enumerate(zeilen):
        nackt = z.lstrip(b' \t>*_')
        if nackt.startswith(b'#'):
            continue
        # Eine Kopfzeile steht als EIGENER ABSATZ - sonst ist es die
        # Fortsetzung eines Satzes (Ultraschall 1.1.10: "Version 0.30
        # aus dem Jahr 2015" verweist auf das Ursprungsplugin).
        if i > 0 and zeilen[i - 1].strip() != b'':
            continue
        if re.search(muster, z):
            return (i + 1, z)
    return (None, None)


def setzen(d, alt, neu):
    """Was das Werkzeug schreiben wuerde."""
    nr, zeile = readme_kopfzeile(d, alt)
    if not nr:
        return d, None
    neu_zeile = re.sub(rb'(Version[ :]+)' + re.escape(alt.encode()),
                       rb'\g<1>' + neu.encode(), zeile, count=1)
    return d.replace(zeile, neu_zeile, 1), nr


# (Name, README-Inhalt, alte Fassung, soll getroffen werden?, Erwartung)
FAELLE = [
    ('schlicht',
     b'# Plugin\n\nVersion 1.3.0\n\nText\n', '1.3.0', True,
     b'Version 1.3.1'),
    ('mit Zusatz',
     b'# Plugin\n\nVersion 0.9.10 \xc2\xb7 LoxBerry ab 3.0 \xc2\xb7 PHP 7.4 und 8.x\n',
     '0.9.10', True, b'Version 0.9.11 \xc2\xb7 LoxBerry'),
    ('als Zitat (der Ausloeser)',
     b'# Plugin\n\n> **Version 0.9.15 \xe2\x80\x94 ohne Geraet gebaut.** Aufbau,\n',
     '0.9.15', True, b'**Version 0.9.16 \xe2\x80\x94 ohne'),
    ('CRLF, als Zitat',
     b'# Plugin\r\n\r\n> **Version 2.0.0 \xe2\x80\x94 Text**\r\n', '2.0.0', True,
     b'**Version 2.0.1 \xe2\x80\x94 Text**'),

    # --- die Faelle, die NICHT getroffen werden duerfen ---
    ('Abschnittsueberschrift mit DERSELBEN Nummer',
     b'# Plugin\n\nEinleitung ohne Fassung.\n\n## Version 3.0.9 \xe2\x80\x94 Stoercodes\n',
     '3.0.9', False, None),
    ('Ueberschrift mit fuehrenden Leerzeichen',
     b'# Plugin\n\n  ## Version 3.0.9 \xe2\x80\x94 Stoercodes\n', '3.0.9', False, None),
    ('fremde Fassung, andere Nummer',
     b'# Plugin\n\nGrundlage ist das Plugin von Aleq, Version 0.2.31, Apache 2.0\n',
     '1.3.2', False, None),
    ('Fassung erst weit unten (Abschnitt)',
     b'# Plugin\n' + b'\nFuelltext\n' * 30 + b'\nVersion 1.0.0\n', '1.0.0', False, None),
    ('Teilnummer darf nicht treffen',
     b'# Plugin\n\nVersion 1.3.10\n', '1.3.1', False, None),
    # Der Fall, den der erste Anlauf falsch behandelte: dieselbe Nummer noch
    # einmal setzen. Die Kopfzeile WIRD gefunden, die Ersetzung aendert
    # nichts - und das Werkzeug brach mit "liess sich nicht setzen" ab.
    # Nichts zu tun ist kein Fehler. Aufgefallen ist es nicht hier, sondern
    # beim Probelauf am echten Ordner.
    ('dieselbe Nummer noch einmal',
     b'# Plugin\n\nVersion 2.0.0\n', '2.0.0', True, b'Version 2.0.0'),
    # Der Fall, an dem "beginnt mit Version" scheiterte: eine
    # FORTSETZUNGSZEILE. Bei Ultraschall 1.1.10 bricht der Satz um, und die
    # Folgezeile beginnt mit "Version 0.30 aus dem Jahr 2015" - die Fassung
    # des Ursprungsplugins. Erkennbar allein daran, dass die Vorzeile nicht
    # leer ist.
    ('Fortsetzungszeile eines Satzes',
     b'# Plugin\n\nGrundlage ist das Plugin von Dietmar Wimmer,\n'
     b'Version 0.30 aus dem Jahr 2015\n', '0.30', False, None),
]


def main():
    breit = max(len(f[0]) for f in FAELLE)
    fehler = 0
    for name, inhalt, alt, soll_treffer, erwartet in FAELLE:
        # Beim Fall "dieselbe Nummer" wird nicht hochgezaehlt.
        ziel = alt if name.startswith('dieselbe Nummer') else _nachfolger(alt)
        neu_d, nr = setzen(inhalt, alt, ziel)
        getroffen = nr is not None
        gut = (getroffen == soll_treffer)
        if gut and soll_treffer:
            gut = erwartet in neu_d
        if gut and not soll_treffer:
            gut = (neu_d == inhalt)          # nichts angefasst
        print('  %-4s %-*s  %s'
              % ('OK' if gut else 'ROT', breit, name,
                 ('Zeile %d getroffen' % nr) if getroffen else 'nicht getroffen'))
        if not gut:
            fehler += 1
            print('       erwartet: %s' % ('Treffer' if soll_treffer else 'KEIN Treffer'))
            if soll_treffer:
                print('       heraus  : %r' % neu_d[:120])

    # Und einmal ueber den echten Bestand: keine Ueberschrift darf getroffen
    # werden. Das ist die Zeile, die die Eichung an die Wirklichkeit bindet.
    print()
    arbeit = os.path.dirname(HIER)
    geprueft = betroffen = 0
    for eintrag in sorted(os.listdir(arbeit)):
        r = os.path.join(arbeit, eintrag, 'README.md')
        c = os.path.join(arbeit, eintrag, 'plugin.cfg')
        if not (eintrag.startswith('LoxBerry-Plugin-')
                and os.path.isfile(r) and os.path.isfile(c)):
            continue
        d = open(r, 'rb').read()
        m = re.search(rb'^VERSION=([^\r\n]*)', open(c, 'rb').read(), re.M)
        if not m:
            continue
        geprueft += 1
        nr, zeile = readme_kopfzeile(d, m.group(1).decode().strip())
        if nr and zeile.lstrip(b' \t>*_').startswith(b'#'):
            print('  ROT  %s: Ueberschrift in Zeile %d wuerde getroffen' % (eintrag, nr))
            betroffen += 1
    print('  %d README des Bestands geprueft, %d Ueberschriften betroffen'
          % (geprueft, betroffen))
    fehler += betroffen

    print('\n%d Faelle, %d Abweichungen' % (len(FAELLE), fehler))
    return 1 if fehler else 0


def _nachfolger(v):
    t = v.split('.')
    t[-1] = str(int(t[-1]) + 1)
    return '.'.join(t)


if __name__ == '__main__':
    sys.exit(main())
