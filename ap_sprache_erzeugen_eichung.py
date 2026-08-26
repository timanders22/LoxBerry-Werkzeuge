# -*- coding: utf-8 -*-
"""Eicht die umgedrehte Wache des Sprachgenerators.

Eine Wache, die man beim Umstellen mitdreht, muss danach in die ANDERE
Richtung anschlagen. Sonst prueft sie das Gegenteil dessen, was gelten soll -
und man merkt es nie, weil sie ja gruen ist.

Gemessen wird an einer Kopie: die Ausgabe wieder auf CRLF gestellt, dann
derselbe Lauf. Erwartet: Rueckgabewert 1 und eine FEHL-Zeile.
"""
import io, os, shutil, subprocess, sys, tempfile

# Arbeitsordner: der Elternordner von Werkzeuge/, uebersteuerbar mit LOXWERK.
ARBEIT = (os.environ.get('LOXWERK') or
          os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ERZ = os.path.join(ARBEIT, 'Werkzeuge', 'ap_sprache_erzeugen.py')

CRLF = chr(92) + 'r' + chr(92) + 'n'
LF = chr(92) + 'n'
ALT = "    return '" + LF + "'.join(zeilen).rstrip('" + LF + "') + '" + LF + "'"
NEU = "    return '" + CRLF + "'.join(zeilen).rstrip('" + CRLF + "') + '" + CRLF + "'"

d = tempfile.mkdtemp()
kopie = os.path.join(d, 'erzeuger_kaputt.py')
t = io.open(ERZ, encoding='utf-8', newline='').read()
if t.count(ALT) != 1:
    raise SystemExit('ABBRUCH: Anker %d mal - Eichung nicht gefahren' % t.count(ALT))
io.open(kopie, 'w', encoding='utf-8', newline='').write(t.replace(ALT, NEU))

ziel = os.path.join(d, 'lang')
os.makedirs(ziel)

print('=== 1. Der richtige Erzeuger (soll GRUEN sein) ===')
r = subprocess.run([sys.executable, ERZ, ziel], capture_output=True, text=True,
                   encoding='utf-8', errors='replace',
                   env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
print('  Rueckgabewert %d   %s' % (r.returncode, r.stdout.strip().splitlines()[-1]))
gruen = r.returncode == 0

print('=== 2. Ausgabe auf CRLF zurueckgebaut (soll ROT sein) ===')
r = subprocess.run([sys.executable, kopie, ziel], capture_output=True, text=True,
                   encoding='utf-8', errors='replace',
                   env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
zeilen = [z for z in r.stdout.strip().splitlines() if 'FEHL' in z]
print('  Rueckgabewert %d   %s' % (r.returncode, zeilen[0] if zeilen else '(keine FEHL-Zeile)'))
rot = r.returncode != 0 and bool(zeilen)

shutil.rmtree(d, ignore_errors=True)
print()
print('Wache geeicht in beide Richtungen: %s' % ('ja' if (gruen and rot) else 'NEIN'))
sys.exit(0 if (gruen and rot) else 1)
