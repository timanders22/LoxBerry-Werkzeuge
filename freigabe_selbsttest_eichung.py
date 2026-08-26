#!/usr/bin/env python3
"""Eichung der Selbsttest-Zeile in `freigabe_pruefen.py`.

Anlass (25.08.2026): die Zeile kannte nur EINE Ausgabeform - die
Rechenkern-Form "N Faelle geprueft, M Fehlschlaege". Zendure SolarFlow gibt
eine Einrichtungspruefung mit den Marken [OK]/[FEHL]/[INFO] aus, und dafuer
meldete die Pruefung `keine auswertbare Ausgabe`: ein rotes Kreuz ohne
Befund, bei jedem Lauf.

Eine Regel, die ein Werkzeug prueft, ist hinterlegt - aber nur, wenn das
Werkzeug in BEIDE Richtungen geeicht ist. Sonst weiss niemand, ob die
Nachbesserung noch etwas findet.

    python3 freigabe_selbsttest_eichung.py

Rueckgabe 0, wenn alle vier Faelle so ausgehen wie erwartet.
"""
import os
import re
import subprocess
import sys
import tempfile

HIER = os.path.dirname(os.path.abspath(__file__))


def selbsttest_urteil(ausgabe, rueckgabe):
    """Genau die Logik aus freigabe_pruefen.py - hier zum Eichen isoliert.

    Aenderungen an der Pruefung gehoeren HIER mitgezogen; laeuft die Eichung
    danach nicht mehr, ist das die Meldung, auf die es ankommt.
    """
    m = re.search(r'(\d+) Faelle geprueft, (\d+) Fehlschl', ausgabe)
    marken = re.findall(r'^\[(OK|FEHL|INFO)\]', ausgabe, re.M)
    if m:
        return ('rechenkern', m.group(2) == '0')
    if marken:
        return ('marken', marken.count('FEHL') == 0 and rueckgabe == 0)
    return ('nichts', False)


FAELLE = [
    # (Name, Ausgabe, Rueckgabewert, erwartete Form, erwartetes Urteil)
    ('Rechenkern, alles gut',
     'Rechenkern: 42 Faelle geprueft, 0 Fehlschlaege.\n', 0, 'rechenkern', True),
    ('Rechenkern mit Fehlschlaegen',
     'Rechenkern: 42 Faelle geprueft, 3 Fehlschlaege.\n', 1, 'rechenkern', False),
    ('Marken, alles gut',
     '[OK]   PHP 8.4.24\n[OK]   2 Geraet(e) eingerichtet\n[INFO] Takt 15 s\n',
     0, 'marken', True),
    ('Marken mit [FEHL]',
     '[OK]   PHP 8.4.24\n[FEHL] Es ist kein Geraet eingerichtet\n', 1, 'marken', False),
    # Der Fall, der die Nachbesserung ausgeloest hat, muss WEITER anschlagen:
    ('gar keine Ausgabe', '', 0, 'nichts', False),
    # Und die Gegenprobe zum Rueckgabewert: Marken ohne [FEHL], aber der
    # Prozess meldet einen Fehler. Ohne diese Zeile waere der Rueckgabewert
    # nur Zierde.
    ('Marken ohne [FEHL], aber Rueckgabe 1',
     '[OK]   alles schoen\n', 1, 'marken', False),
]


def main():
    breit = max(len(f[0]) for f in FAELLE)
    fehler = 0
    for name, ausgabe, rc, soll_form, soll_urteil in FAELLE:
        form, urteil = selbsttest_urteil(ausgabe, rc)
        gut = (form == soll_form and urteil == soll_urteil)
        print('  %-4s %-*s  Form %-10s Urteil %-5s (erwartet %s / %s)'
              % ('OK' if gut else 'ROT', breit, name, form, urteil,
                 soll_form, soll_urteil))
        if not gut:
            fehler += 1

    # Und einmal am echten Plugin, damit die Eichung nicht nur sich selbst prueft.
    print()
    arbeitsordner = os.path.dirname(HIER)
    echt = None
    for kandidat in sorted(os.listdir(arbeitsordner), reverse=True):
        d = os.path.join(arbeitsordner, kandidat, 'bin')
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.endswith('_dienst.php'):
                echt = os.path.join(d, f)
                break
        if echt:
            break
    if echt:
        r = subprocess.run(['php', echt, '--selbsttest'],
                           capture_output=True, text=True, encoding='utf-8',
                           errors='replace')
        form, urteil = selbsttest_urteil(r.stdout, r.returncode)
        print('  am echten Dienst: %s  Form %s, Urteil %s'
              % (os.path.relpath(echt, arbeitsordner), form, urteil))
        if form == 'nichts':
            print('  ROT  der echte Dienst liefert keine der beiden Formen')
            fehler += 1
    else:
        print('  --   kein bin/*_dienst.php gefunden - nicht gemessen')

    print()
    print('%d Faelle, %d Abweichungen' % (len(FAELLE), fehler))
    return 1 if fehler else 0


if __name__ == '__main__':
    sys.exit(main())
