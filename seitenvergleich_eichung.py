#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Eichung von `seitenvergleich.py` - in beide Richtungen, Erwartung vorher fest.

Sechs Faelle. Die beiden ersten gehoeren zusammen: was herausgerechnet wird,
MUSS schweigen (Token, Fassungsnummer, Uhrzeit) - und alles andere MUSS
anschlagen. Ein Werkzeug, das nur das eine kann, ist entweder blind oder ein
Dauerfehlalarm.

    python3 seitenvergleich_eichung.py
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
WERKZEUG = os.path.join(HIER, 'seitenvergleich.py')
PY = sys.executable or 'python3'

# Die Konsole dieses Rechners ist cp1252: eine Ausgabe mit Umlauten aus
# einem Unterprozess braeche den Lauf sonst mit UnicodeEncodeError ab.
try:
    sys.stdout.reconfigure(errors='replace')
except (AttributeError, ValueError):
    pass

SEITE = ('<h1>Pruefstand</h1>\n'
         '<p>Fassung %(fassung)s, erzeugt am %(zeit)s</p>\n'
         '<form method="post"><input name="ap_formtoken" value="%(token)s">\n'
         '<p>%(text)s</p></form>\n')


def schreiben(ordner, name, fassung, zeit, token, text):
    os.makedirs(ordner, exist_ok=True)
    io.open(os.path.join(ordner, name), 'w', encoding='utf-8').write(
        SEITE % dict(fassung=fassung, zeit=zeit, token=token, text=text))


def ruf(*args):
    p = subprocess.run([PY, '-B', WERKZEUG] + list(args), capture_output=True,
                       text=True, encoding='utf-8', errors='replace',
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def main():
    kratz = tempfile.mkdtemp(prefix='seitenvergleich_eichung_')
    alt = os.path.join(kratz, 'linie-1.2.7_de')
    neu = os.path.join(kratz, 'linie-1.2.8_de')
    fehl = 0

    def pruefe(name, erwartet_rc, erwartet_text):
        nonlocal fehl
        rc, aus = ruf(alt, neu)
        ok = (rc == erwartet_rc and erwartet_text in aus)
        print('%-4s %-40s rc=%d (erwartet %d), "%s" %s'
              % ('ok' if ok else 'FEHL', name, rc, erwartet_rc, erwartet_text,
                 'gefunden' if erwartet_text in aus else 'FEHLT'))
        if not ok:
            fehl += 1
            print(aus)

    try:
        # 1. Nur die Ausnahmen unterscheiden sich: Token, Fassung, Uhrzeit.
        schreiben(alt, 'settings.html', '1.2.7', '07.09.2026 09:38',
                  'a1b2c3d4e5f60718293a4b5c6d7e8f90', 'Einstellungen sichern')
        schreiben(neu, 'settings.html', '1.2.8', '13.09.2026 11:02',
                  '0f9e8d7c6b5a49382716f5e4d3c2b1a0', 'Einstellungen sichern')
        pruefe('nur Token, Fassung und Zeit verschieden', 0, '1 Datei(en) verglichen, 0 verschieden')

        # 2. Ein einziges Wort im Text - das MUSS anschlagen.
        schreiben(neu, 'settings.html', '1.2.8', '13.09.2026 11:02',
                  '0f9e8d7c6b5a49382716f5e4d3c2b1a0', 'EINST.K_SICHERN')
        pruefe('ein Wort im Text geaendert', 1, 'VERSCHIEDEN')

        # 3. Eine Seite gibt es nur auf einer Seite.
        schreiben(neu, 'settings.html', '1.2.8', '13.09.2026 11:02',
                  '0f9e8d7c6b5a49382716f5e4d3c2b1a0', 'Einstellungen sichern')
        schreiben(neu, 'test.html', '1.2.8', '13.09.2026 11:02',
                  '0f9e8d7c6b5a49382716f5e4d3c2b1a0', 'Test')
        pruefe('Seite nur auf einer Seite', 1, 'NUR IN')

        # 4. Beide Ordner leer: das ist "nichts gemessen", nicht "gleich".
        shutil.rmtree(alt, ignore_errors=True)
        shutil.rmtree(neu, ignore_errors=True)
        os.makedirs(alt)
        os.makedirs(neu)
        pruefe('beide Ordner leer', 2, 'nichts gemessen')

        # 5. Ein Ordner fehlt ganz.
        shutil.rmtree(neu, ignore_errors=True)
        pruefe('ein Ordner fehlt', 2, 'ABBRUCH')

        # 6. Steht keine Fassungsnummer im Ordnernamen, sagt es das - und
        #    rechnet dann auch keine heraus.
        ohne_a = os.path.join(kratz, 'alt')
        ohne_b = os.path.join(kratz, 'neu')
        schreiben(ohne_a, 's.html', '1.2.7', '07.09.2026 09:38', 'aa', 'gleich')
        schreiben(ohne_b, 's.html', '1.2.8', '13.09.2026 11:02', 'bb', 'gleich')
        rc, aus = ruf(ohne_a, ohne_b)
        ok = (rc == 1 and 'KEINE Fassungsnummer gefunden' in aus)
        print('%-4s %-40s rc=%d (erwartet 1), Hinweis %s'
              % ('ok' if ok else 'FEHL', 'ohne Fassung im Ordnernamen', rc,
                 'gefunden' if 'KEINE Fassungsnummer gefunden' in aus else 'FEHLT'))
        if not ok:
            fehl += 1
            print(aus)
    finally:
        shutil.rmtree(kratz, ignore_errors=True)

    print('%d Fall/Faelle nicht wie erwartet' % fehl)
    return 1 if fehl else 0


if __name__ == '__main__':
    sys.exit(main())
