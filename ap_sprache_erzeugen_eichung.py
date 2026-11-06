# -*- coding: utf-8 -*-
"""Eicht die umgedrehte Wache des Sprachgenerators.

Eine Wache, die man beim Umstellen mitdreht, muss danach in die ANDERE
Richtung anschlagen. Sonst prueft sie das Gegenteil dessen, was gelten soll -
und man merkt es nie, weil sie ja gruen ist.

Gemessen wird an einer Kopie: die Ausgabe wieder auf CRLF gestellt, dann
derselbe Lauf. Erwartet: Rueckgabewert 1 und eine FEHL-Zeile.

Seit 30.09.2026 (Verbesserungsbau APC-UPS-a2) zusaetzlich, wenn ein
Plugin-Ordner angegeben ist: der Erzeuger gegen die ausgelieferten
language_de/en.ini dieses Ordners, byteweise. Ohne Ordner wird dazu nichts
behauptet.

Aufruf:  python ap_sprache_erzeugen_eichung.py [<Plugin-Ordner>]
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
# Die Kopie liegt im Zeitordner, nicht neben dem Erzeuger. Seit 13.09.2026
# bindet der Erzeuger Werkzeuge/sprachwache.py ein; ohne diesen Suchpfad
# endete die Kopie mit ModuleNotFoundError - Rueckgabewert 1, aber keine
# FEHL-Zeile -, und die Eichung meldete NEIN, obwohl nicht die Wache
# versagt hatte, sondern der Aufbau der Probe (gemessen 30.09.2026,
# Verbesserungsbau APC-UPS-a2).
suchpfad = os.path.dirname(ERZ)
if os.environ.get('PYTHONPATH'):
    suchpfad += os.pathsep + os.environ['PYTHONPATH']
r = subprocess.run([sys.executable, kopie, ziel], capture_output=True, text=True,
                   encoding='utf-8', errors='replace',
                   env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
                            PYTHONPATH=suchpfad))
zeilen = [z for z in r.stdout.strip().splitlines() if 'FEHL' in z]
print('  Rueckgabewert %d   %s' % (r.returncode, zeilen[0] if zeilen else '(keine FEHL-Zeile)'))
if not zeilen:
    # Sagen, WARUM keine FEHL-Zeile kam: ein Absturz der Kopie ist kein
    # Anschlagen der Wache, und ohne diese Zeile sieht beides gleich aus.
    grund = [z for z in r.stderr.strip().splitlines() if z.strip()]
    print('  Die Kopie kam nicht bis zur Wache: %s' % (grund[-1] if grund else '(stderr leer)'))
rot = r.returncode != 0 and bool(zeilen)



def _werte(roh):
    """{ABSCHNITT.SCHLUESSEL: Wertzeile} - nur fuer die Beschreibung einer Abweichung."""
    d, ab = {}, ''
    for z in roh.decode('utf-8', 'replace').split('\n'):
        z = z.strip()
        if z.startswith('['):
            ab = z.strip('[]')
        elif z and not z.startswith(';') and ' = ' in z:
            k, v = z.split(' = ', 1)
            d[ab + '.' + k] = v
    return d


# 3. Am Bestand (seit 30.09.2026): Erzeuger gegen die ausgelieferten Dateien.
#    Gedaechtnis "Sprachdateien und Erzeuger": Erzeuger driften gegen ihre
#    .ini, etwa in der Entitaetenform. Nur mit Argument.
bestand_ok = True
if len(sys.argv) > 1:
    plugin = sys.argv[1]
    print('=== 3. Erzeuger gegen den Bestand (soll byte-gleich sein) ===')
    print('  Ordner: %s' % plugin)
    ziel3 = os.path.join(d, 'bestand')
    os.makedirs(ziel3)
    r = subprocess.run([sys.executable, ERZ, ziel3], capture_output=True, text=True,
                       encoding='utf-8', errors='replace',
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    if r.returncode != 0:
        bestand_ok = False
        print('  Erzeuger: Rueckgabewert %d' % r.returncode)
    for sp in ('de', 'en'):
        n = 'language_%s.ini' % sp
        try:
            a = io.open(os.path.join(ziel3, n), 'rb').read()
            b = io.open(os.path.join(plugin, 'templates', 'lang', n), 'rb').read()
        except (IOError, OSError) as e:
            bestand_ok = False
            print('  %s: nicht lesbar (%s)' % (n, e))
            continue
        if a == b:
            print('  %s: byte-gleich (%d Byte)' % (n, len(a)))
            continue
        bestand_ok = False
        wa, wb = _werte(a), _werte(b)
        nur_erz = sorted(set(wa) - set(wb))
        nur_dat = sorted(set(wb) - set(wa))
        anders = sorted(k for k in set(wa) & set(wb) if wa[k] != wb[k])
        print('  %s: WEICHT AB (%d gegen %d Byte) - nur im Erzeuger %d, nur in der '
              'Datei %d, Wert verschieden %d: %s'
              % (n, len(a), len(b), len(nur_erz), len(nur_dat), len(anders),
                 ', '.join((nur_erz + nur_dat + anders)[:6]) or '(nur Rahmen/Zeilenenden)'))

shutil.rmtree(d, ignore_errors=True)
print()
print('Wache geeicht in beide Richtungen: %s' % ('ja' if (gruen and rot) else 'NEIN'))
if len(sys.argv) > 1:
    print('Erzeuger gleich dem Bestand: %s' % ('ja' if bestand_ok else 'NEIN'))
sys.exit(0 if (gruen and rot and bestand_ok) else 1)
