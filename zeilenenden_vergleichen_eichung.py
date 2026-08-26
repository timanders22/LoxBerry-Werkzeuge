# -*- coding: utf-8 -*-
"""Eicht das nachgebesserte zeilenenden_vergleichen.py in vier Richtungen.

Ein Werkzeug wird geeicht, bevor man ihm glaubt - an einem bekannten Befund
UND an einem bekannt sauberen Fall.
"""
import io, os, shutil, subprocess, sys, tempfile, zipfile

ARBEIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.path.join(ARBEIT, 'Werkzeuge', 'zeilenenden_vergleichen.py')
LOKAL = os.path.join(ARBEIT, 'LoxBerry-Plugin-APC-UPS-1.2.0.zip')  # ohne
ORDNER = os.path.join(ARBEIT, 'LoxBerry-Plugin-APC-UPS-1.2.1')

# Das GitHub-Archiv wird GEHOLT, nicht irgendwo erwartet.
#
# Die erste Fassung dieser Eichung suchte es im eigenen Ablageordner. Beim
# Verschieben der Datei nach Werkzeuge/ war es dort nicht mehr, und die
# Eichung meldete drei Verstoesse, die keine waren - ein Pruefstand, der
# einen Pfad erbt statt ihn auszuschreiben. Steht in REGELN_1 fuenfmal.
URL = ('https://github.com/timanders22/LoxBerry-Plugin-APC-UPS'
       '/archive/refs/tags/v1.2.0.zip')
GITHUB = os.path.join(tempfile.gettempdir(), 'eichung_v1.2.0.zip')
if not os.path.isfile(GITHUB):
    try:
        import urllib.request
        print('Hole den Bezug: %s' % URL)
        urllib.request.urlretrieve(URL, GITHUB)
    except Exception as fehler:                      # noqa: BLE001
        print('ABBRUCH: das Archiv liess sich nicht holen (%s: %s).'
              % (type(fehler).__name__, fehler))
        print('Ohne Netz laesst sich diese Eichung nicht fahren - sie prueft')
        print('gerade den Fall "Archiv mit oberstem Ordner". Nichts gemessen.')
        sys.exit(2)


def lauf(bezug, ziel):
    r = subprocess.run([sys.executable, W, 'angleichen', bezug, ziel],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace',
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    return r.returncode, r.stdout.strip()


fehl = 0


def pruefe(marke, rc, aus, soll_rc, muss_enthalten):
    global fehl
    ok = rc == soll_rc and all(m in aus for m in muss_enthalten)
    if not ok:
        fehl += 1
    print('  %-52s %s  RC=%d' % (marke, '[OK]  ' if ok else '[FEHL]', rc))
    for z in aus.splitlines():
        if z.startswith(('Bezug:', 'ABBRUCH', 'ACHTUNG')) or 'angeglichen' in z:
            print('        %s' % z[:110])


# --- 1. GitHub-Archiv als Bezug: muss jetzt WIRKLICH vergleichen ----------
d = tempfile.mkdtemp()
kopie = os.path.join(d, 'k1')
shutil.copytree(ORDNER, kopie)
rc, aus = lauf(GITHUB, kopie)
pruefe('GitHub-Archiv als Bezug (oberster Ordner)', rc, aus, 0,
       ['oberster Ordner abgeschnitten', '0 Datei(en) angeglichen'])
# Und: es darf NICHTS mehr als "neu" gelten ausser dem, was wirklich neu ist.
neu_zeile = [z for z in aus.splitlines() if z.startswith('Neue Dateien')]
print('        %s' % (neu_zeile[0][:110] if neu_zeile else 'keine neuen Dateien'))
if neu_zeile and neu_zeile[0].count(',') > 1:
    print('        FEHL: es gelten immer noch viele Dateien als neu')
    fehl += 1

# --- 2. Lokales ZIP als Bezug: die alte Aufrufform muss weiter tragen -----
kopie = os.path.join(d, 'k2')
shutil.copytree(os.path.join(ARBEIT, 'LoxBerry-Plugin-APC-UPS-1.2.0'), kopie)
rc, aus = lauf(LOKAL, kopie)
pruefe('lokal gepacktes ZIP als Bezug (kein Rueckschritt)', rc, aus, 0,
       ['0 Datei(en) angeglichen'])

# --- 3. Ein Bezug, der NICHT passt: muss ABBRECHEN ------------------------
fremd = os.path.join(d, 'fremd.zip')
with zipfile.ZipFile(fremd, 'w') as z:
    z.writestr('ganz/woanders/datei_a.txt', b'eins\n')
    z.writestr('ganz/woanders/datei_b.txt', b'zwei\n')
kopie = os.path.join(d, 'k3')
shutil.copytree(ORDNER, kopie)
vorher = io.open(os.path.join(kopie, 'plugin.cfg'), 'rb').read()
rc, aus = lauf(fremd, kopie)
pruefe('unpassender Bezug bricht ab', rc, aus, 2, ['ABBRUCH'])
nachher = io.open(os.path.join(kopie, 'plugin.cfg'), 'rb').read()
if vorher != nachher:
    print('        FEHL: es wurde trotz Abbruch geschrieben')
    fehl += 1
else:
    print('        Nichts geschrieben - der Ordner ist unveraendert.')

# --- 4. Ein bekannter Befund: eine CRLF-Datei auf LF gestellt -------------
kopie = os.path.join(d, 'k4')
shutil.copytree(ORDNER, kopie)
p = os.path.join(kopie, 'templates', 'lang', 'help_de.ini')
b = io.open(p, 'rb').read()
io.open(p, 'wb').write(b.replace(b'\n', b'\r\n'))   # LF -> CRLF, absichtlich
rc, aus = lauf(GITHUB, kopie)
zurueck = io.open(p, 'rb').read() == b
pruefe('absichtlich verstellte Datei wird zurueckgestellt', rc, aus, 0,
       ['1 Datei(en) angeglichen'])
print('        Datei wieder byte-gleich: %s' % ('ja' if zurueck else 'NEIN'))
if not zurueck:
    fehl += 1

shutil.rmtree(d, ignore_errors=True)
print()
print('Verstoesse: %d' % fehl)
sys.exit(1 if fehl else 0)
