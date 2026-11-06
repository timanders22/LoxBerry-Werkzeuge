#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Eichung von `sprachabbild.py` - in beide Richtungen, Erwartung vorher fest.

Sieben Faelle. Der wichtigste ist der zweite: eine reine UMORDNUNG der Zeilen
muss schweigen - dafuer gibt es das Werkzeug. Waeren die uebrigen nicht dabei,
maesse man nur sein Schweigen.

    python3 sprachabbild_eichung.py
Rueckgabe 0 = alle Faelle wie erwartet, 1 = ein Fall nicht.
Schreibt nur in einen eigenen Kratzordner und raeumt ihn auf.
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
WERKZEUG = os.path.join(HIER, 'sprachabbild.py')
PY = sys.executable or 'python3'

# Die Konsole dieses Rechners ist cp1252: eine Ausgabe mit Umlauten aus
# einem Unterprozess braeche den Lauf sonst mit UnicodeEncodeError ab.
try:
    sys.stdout.reconfigure(errors='replace')
except (AttributeError, ValueError):
    pass

KOPF = '; Eichung\n\n[EINST]\n'

ZEILEN_DE = [
    'A_ERSTE = "erster Wert"',
    'B_ZWEITE = "zweiter Wert"',
    'C_DRITTE = "dritter Wert"',
]
ZEILEN_EN = [
    'A_ERSTE = "first value"',
    'B_ZWEITE = "second value"',
    'C_DRITTE = "third value"',
]


def schreiben(ordner, de, en):
    os.makedirs(ordner, exist_ok=True)
    for sp, zeilen in (('de', de), ('en', en)):
        io.open(os.path.join(ordner, 'language_%s.ini' % sp), 'wb').write(
            (KOPF + '\n'.join(zeilen) + '\n').encode('utf-8'))


def ruf(*args):
    p = subprocess.run([PY, '-B', WERKZEUG] + list(args), capture_output=True,
                       text=True, encoding='utf-8', errors='replace',
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def main():
    kratz = tempfile.mkdtemp(prefix='sprachabbild_eichung_')
    lang = os.path.join(kratz, 'lang')
    abbild = os.path.join(kratz, 'vorher.json')
    fehl = 0
    try:
        schreiben(lang, ZEILEN_DE, ZEILEN_EN)
        rc, aus = ruf('sichern', lang, abbild)
        if rc != 0 or '3 Schluessel' not in aus:
            print('FEHL  Vorbereitung: sichern lieferte rc=%d\n%s' % (rc, aus))
            return 1

        faelle = [
            ('unveraendert',
             ZEILEN_DE, ZEILEN_EN, 0, '0 Befund(e)'),
            ('nur umgeordnet - MUSS schweigen',
             list(reversed(ZEILEN_DE)), list(reversed(ZEILEN_EN)), 0, '0 Befund(e)'),
            ('ein Schluessel geloescht',
             ZEILEN_DE[:2], ZEILEN_EN, 1, 'NUR VORHER   EINST.C_DRITTE'),
            ('ein Wert geaendert',
             [ZEILEN_DE[0], 'B_ZWEITE = "anders"', ZEILEN_DE[2]], ZEILEN_EN,
             1, 'ANDERER WERT EINST.B_ZWEITE'),
            ('ein Schluessel dazu',
             ZEILEN_DE + ['D_NEUE = "neu"'], ZEILEN_EN,
             1, 'NUR JETZT    EINST.D_NEUE'),
            ('beides zugleich',
             [ZEILEN_DE[0], 'B_ZWEITE = "anders"'], ZEILEN_EN,
             1, '2 Befund(e)'),
        ]
        for name, de, en, erwartet_rc, erwartet_text in faelle:
            schreiben(lang, de, en)
            rc, aus = ruf('halten', abbild, lang)
            ok = (rc == erwartet_rc and erwartet_text in aus)
            print('%-4s %-34s rc=%d (erwartet %d), "%s" %s'
                  % ('ok' if ok else 'FEHL', name, rc, erwartet_rc,
                     erwartet_text, 'gefunden' if erwartet_text in aus else 'FEHLT'))
            if not ok:
                fehl += 1
                print(aus)

        # Siebter Fall: die Datei ist weg. Das ist "nicht gemessen", nicht
        # "in Ordnung" - die beiden Ausgaenge muessen unterscheidbar bleiben.
        schreiben(lang, ZEILEN_DE, ZEILEN_EN)
        os.unlink(os.path.join(lang, 'language_en.ini'))
        rc, aus = ruf('halten', abbild, lang)
        ok = (rc == 1 and 'NICHT gemessen' in aus)
        print('%-4s %-34s rc=%d (erwartet 1), "NICHT gemessen" %s'
              % ('ok' if ok else 'FEHL', 'eine Sprachdatei fehlt', rc,
                 'gefunden' if 'NICHT gemessen' in aus else 'FEHLT'))
        if not ok:
            fehl += 1
            print(aus)

        # Achter Fall: ein leerer Ordner darf kein Abbild ergeben.
        leer = os.path.join(kratz, 'leer')
        os.makedirs(leer, exist_ok=True)
        rc, aus = ruf('sichern', leer, os.path.join(kratz, 'leer.json'))
        ok = (rc == 2)
        print('%-4s %-34s rc=%d (erwartet 2)'
              % ('ok' if ok else 'FEHL', 'leerer Ordner beim Sichern', rc))
        if not ok:
            fehl += 1
            print(aus)
    finally:
        shutil.rmtree(kratz, ignore_errors=True)

    print('%d Fall/Faelle nicht wie erwartet' % fehl)
    return 1 if fehl else 0


if __name__ == '__main__':
    sys.exit(main())
