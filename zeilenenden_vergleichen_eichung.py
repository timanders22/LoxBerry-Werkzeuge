# -*- coding: utf-8 -*-
"""Eicht zeilenenden_vergleichen.py - an bekannten Befunden UND bekannt sauberen Faellen.

Ein Werkzeug wird geeicht, bevor man ihm glaubt - an einem bekannten Befund
UND an einem bekannt sauberen Fall.

UMGEBAUT 16.09.2026, aus zwei Gruenden:

1. Die LF-Ordnung in Plugin-Ordnern ist dazugekommen (Faelle 5 bis 11). Fall 5
   ist der Fehler, um den es ging: das Werkzeug drehte eine erledigte
   LF-Umstellung zurueck, weil das veroeffentlichte Archiv CRLF trug
   (AWM-Abfuhr 1.4.9; ueber den Bestand 67 Dateien in 29 Linien, alle von LF
   nach CRLF). Wird die Berichtigung im Werkzeug zurueckgebaut, MUSS Fall 5
   rot werden - mit ZV_WERKZEUG=<alte Fassung> laesst sich das nachfahren.

2. Die bisherige Eichung lief nicht mehr. Sie kopierte die Ordner
   LoxBerry-Plugin-APC-UPS-1.2.0 und -1.2.1 aus dem Arbeitsordner, und die
   waren beim Aufraeumen des Bestands verschwunden: FileNotFoundError, bevor
   ein einziger Fall gemessen war. Eine Eichung, die an einer bestimmten
   Plugin-Fassung haengt, verrottet mit dem Bestand. Alle Faelle bauen ihre
   Stuecke jetzt selbst - auch das Archiv mit oberstem Ordner, das bisher von
   GitHub geholt wurde. Damit braucht die Eichung weder Netz noch einen
   bestimmten Ordner.

Rueckgabe: 0 alles bestanden, 1 mindestens ein Verstoss.
"""
import io, os, shutil, subprocess, sys, tempfile, zipfile

ARBEIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.environ.get('ZV_WERKZEUG') or os.path.join(ARBEIT, 'Werkzeuge', 'zeilenenden_vergleichen.py')
if not os.path.isfile(W):
    print('ABBRUCH: das Werkzeug %s fehlt - nichts gemessen.' % W)
    sys.exit(2)
print('Geeicht wird: %s' % W)


def lauf(bezug, ziel, *zusatz):
    r = subprocess.run([sys.executable, W, 'angleichen', bezug, ziel] + list(zusatz),
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace',
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    return r.returncode, r.stdout.strip()


fehl = 0
faelle = 0


def pruefe(marke, rc, aus, soll_rc, muss_enthalten, darf_nicht=()):
    global fehl, faelle
    faelle += 1
    ok = (rc == soll_rc and all(m in aus for m in muss_enthalten)
          and not any(m in aus for m in darf_nicht))
    if not ok:
        fehl += 1
    print('  %-60s %s  RC=%d' % (marke, '[OK]  ' if ok else '[FEHL]', rc))
    for z in aus.splitlines():
        if z.startswith(('Bezug:', 'ABBRUCH', 'ACHTUNG', 'Ordnung:', 'PROBE', 'BEFUND',
                         'SHEBANG', '    --zeilenenden-neu', 'Neue Dateien')) \
                or 'angeglichen' in z:
            print('        %s' % z[:110])
    if not ok:
        fehlt = [m for m in muss_enthalten if m not in aus]
        stoert = [m for m in darf_nicht if m in aus]
        if fehlt:
            print('        erwartet, aber nicht ausgegeben: %s' % fehlt)
        if stoert:
            print('        ausgegeben, aber verboten: %s' % stoert)


def sollwert(bedingung, text):
    global fehl
    if not bedingung:
        fehl += 1
    print('        %-56s %s' % (text, 'ja' if bedingung else 'NEIN  <<< FEHL'))


def lese(p):
    return io.open(p, 'rb').read()


def schreibe(p, b):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, 'wb').write(b)


d = tempfile.mkdtemp(prefix='zv_eichung_')

CFG_LF = b'[PLUGIN]\nVERSION=1.0.1\nNAME=eich\n'
CFG_CRLF = CFG_LF.replace(b'\n', b'\r\n')
TXT_LF = b'eins\nzwei\ndrei\n'
TXT_CRLF = TXT_LF.replace(b'\n', b'\r\n')


def baue(name, im_ordner, im_bezug, plugin=True, oberster=None):
    """Ordner und ZIP-Bezug anlegen. Werte sind Bytes.

    plugin=True legt eine plugin.cfg (LF) in den Ordner, sofern keine
    genannt ist, und eine CRLF-plugin.cfg in den Bezug - das ist die Lage
    einer Linie, deren .cfg zuletzt noch CRLF veroeffentlicht wurde.
    oberster='repo-v1.0.0' haengt im Bezug alles unter einen obersten
    Ordner, wie es GitHub tut."""
    ordner = os.path.join(d, name)
    os.makedirs(ordner, exist_ok=True)
    for rel, inhalt in im_ordner.items():
        schreibe(os.path.join(ordner, rel), inhalt)
    if plugin and 'plugin.cfg' not in im_ordner:
        schreibe(os.path.join(ordner, 'plugin.cfg'), CFG_LF)
    bezug = os.path.join(d, name + '_bezug.zip')
    with zipfile.ZipFile(bezug, 'w') as z:
        eintraege = dict(im_bezug)
        if plugin and 'plugin.cfg' not in eintraege:
            eintraege['plugin.cfg'] = CFG_LF
        for rel, inhalt in eintraege.items():
            z.writestr((oberster + '/' + rel) if oberster else rel, inhalt)
    return ordner, bezug


# --- 1. Archiv mit oberstem Ordner (GitHub-Form): wird wirklich verglichen -
o, z = baue('k1', {'a.txt': TXT_LF, 'lang/b.ini': TXT_LF},
                  {'a.txt': TXT_LF, 'lang/b.ini': TXT_LF}, oberster='repo-v1.0.0')
rc, aus = lauf(z, o)
pruefe('1  Archiv mit oberstem Ordner: abgeschnitten, alles gefunden', rc, aus, 0,
       ['oberster Ordner abgeschnitten', '0 Datei(en) angeglichen'],
       darf_nicht=['Neue Dateien'])

# --- 2. Archiv ohne obersten Ordner (packen.py-Form) --------------------
o, z = baue('k2', {'a.txt': TXT_LF}, {'a.txt': TXT_LF})
rc, aus = lauf(z, o)
pruefe('2  lokal gepacktes Archiv: nichts zu tun', rc, aus, 0,
       ['0 Datei(en) angeglichen'], darf_nicht=['abgeschnitten', 'Neue Dateien'])

# --- 3. Ein Bezug, der NICHT passt: muss ABBRECHEN ----------------------
o, _ = baue('k3', {'a.txt': TXT_CRLF}, {'a.txt': TXT_CRLF})
fremd = os.path.join(d, 'fremd.zip')
with zipfile.ZipFile(fremd, 'w') as zf:
    zf.writestr('ganz/woanders/datei_a.txt', b'eins\n')
    zf.writestr('ganz/woanders/datei_b.txt', b'zwei\n')
vorher = lese(os.path.join(o, 'a.txt'))
rc, aus = lauf(fremd, o)
pruefe('3  unpassender Bezug bricht ab', rc, aus, 2, ['ABBRUCH'])
sollwert(vorher == lese(os.path.join(o, 'a.txt')), 'nichts geschrieben (die CRLF-Datei blieb)')

# --- 3b. Ein leerer Bezug: muss ABBRECHEN --------------------------------
leer = os.path.join(d, 'leer.zip')
zipfile.ZipFile(leer, 'w').close()
rc, aus = lauf(leer, o)
pruefe('3b leerer Bezug bricht ab', rc, aus, 2, ['ABBRUCH', 'fehlt oder ist leer'])

# --- 4. Eine LF-Datei versehentlich auf CRLF verstellt: zurueck ----------
o, z = baue('k4', {'help_de.ini': TXT_CRLF}, {'help_de.ini': TXT_LF})
rc, aus = lauf(z, o)
pruefe('4  versehentlich verstellte Datei wird zurueckgestellt', rc, aus, 0,
       ['angeglichen auf lf', 'help_de.ini', '1 Datei(en) angeglichen'])
sollwert(lese(os.path.join(o, 'help_de.ini')) == TXT_LF, 'Datei wieder byte-gleich mit LF')


# =========================================================================
# Die LF-Ordnung in Plugin-Ordnern (seit 16.09.2026)
# =========================================================================

# --- 5. DER GEMELDETE FEHLER: erledigte LF-Umstellung, Bezug CRLF -------
o, z = baue('k5', {'plugin.cfg': CFG_LF, 'release.cfg': TXT_LF},
                  {'plugin.cfg': CFG_CRLF, 'release.cfg': TXT_CRLF})
rc, aus = lauf(z, o)
pruefe('5  Plugin-Ordner: LF bleibt LF, auch wenn der Bezug CRLF sagt', rc, aus, 0,
       ['0 Datei(en) angeglichen', '--zeilenenden-neu plugin.cfg,release.cfg'])
sollwert(lese(os.path.join(o, 'plugin.cfg')) == CFG_LF, 'plugin.cfg weiter LF')
sollwert(lese(os.path.join(o, 'release.cfg')) == TXT_LF, 'release.cfg weiter LF')

# --- 6. Plugin-Ordner: eine CRLF-Datei wird LF --------------------------
o, z = baue('k6', {'language_de.ini': TXT_CRLF}, {'language_de.ini': TXT_CRLF})
rc, aus = lauf(z, o)
pruefe('6  Plugin-Ordner: CRLF-Datei wird LF und wird zum Anmelden genannt', rc, aus, 0,
       ['angeglichen auf lf', '--zeilenenden-neu language_de.ini'])
sollwert(lese(os.path.join(o, 'language_de.ini')) == TXT_LF, 'Datei jetzt LF, Inhalt gleich')

# --- 7. --crlf-erlaubt: "noch nicht dran" bleibt CRLF --------------------
o, z = baue('k7', {'language_de.ini': TXT_CRLF}, {'language_de.ini': TXT_CRLF})
rc, aus = lauf(z, o, '--crlf-erlaubt', 'language_de.ini')
pruefe('7  --crlf-erlaubt haelt die genannte Datei auf CRLF', rc, aus, 0,
       ['0 Datei(en) angeglichen'], darf_nicht=['BEFUND', '--zeilenenden-neu'])
sollwert(lese(os.path.join(o, 'language_de.ini')) == TXT_CRLF, 'Datei weiter CRLF')

# --- 7b. --crlf-erlaubt mit vollem Pfad (dieselbe Auslegung wie das Tor) --
o, z = baue('k7b', {'templates/lang/language_de.ini': TXT_CRLF},
                   {'templates/lang/language_de.ini': TXT_CRLF})
rc, aus = lauf(z, o, '--crlf-erlaubt', 'templates/lang/language_de.ini')
pruefe('7b --crlf-erlaubt nimmt auch den vollen Pfad', rc, aus, 0,
       ['0 Datei(en) angeglichen'], darf_nicht=['BEFUND'])

# --- 8. KEIN Plugin-Ordner: die alte Ordnung gilt (Loxone-Vorlagen) ------
o, z = baue('k8', {'VI_Eichung.xml': TXT_LF}, {'VI_Eichung.xml': TXT_CRLF}, plugin=False)
rc, aus = lauf(z, o)
pruefe('8  ohne plugin.cfg: Stil des Vorzustands (hier CRLF)', rc, aus, 0,
       ['KEIN Plugin-Ordner', 'angeglichen auf crlf'])
sollwert(lese(os.path.join(o, 'VI_Eichung.xml')) == TXT_CRLF, 'Vorlage zurueck auf CRLF')

# --- 9. --probe schreibt nichts ------------------------------------------
o, z = baue('k9', {'language_de.ini': TXT_CRLF}, {'language_de.ini': TXT_CRLF})
rc, aus = lauf(z, o, '--probe')
pruefe('9  --probe meldet, schreibt aber nicht', rc, aus, 0,
       ['PROBE', 'wuerde angleichen auf lf'])
sollwert(lese(os.path.join(o, 'language_de.ini')) == TXT_CRLF, 'Datei unveraendert')

# --- 10. Binaerdatei mit 0D 0A in den Bilddaten bleibt byte-gleich -------
png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR' + b'\r\n' * 5 + b'\x00\x00'
o, z = baue('k10', {'icons/icon_512.png': png, 'a.txt': TXT_CRLF},
                   {'icons/icon_512.png': png, 'a.txt': TXT_CRLF})
rc, aus = lauf(z, o)
pruefe('10 Symbol mit 0D 0A in den Bilddaten', rc, aus, 0, ['a.txt'],
       darf_nicht=['icon_512.png'])
sollwert(lese(os.path.join(o, 'icons', 'icon_512.png')) == png, 'PNG byte-gleich')

# --- 11. Shebang bleibt LF, auch mit --crlf-erlaubt ----------------------
sh = b'#!/bin/sh\necho hallo\n'
o, z = baue('k11', {'cron/cron.01min': sh}, {'cron/cron.01min': sh.replace(b'\n', b'\r\n')})
rc, aus = lauf(z, o, '--crlf-erlaubt', 'cron.01min')
pruefe('11 Shebang-Datei bleibt LF, auch wenn erlaubt', rc, aus, 0,
       ['SHEBANG', '0 Datei(en) angeglichen'])
sollwert(lese(os.path.join(o, 'cron', 'cron.01min')) == sh, 'Datei weiter LF')

# --- 12. Neue Datei im Plugin-Ordner (nicht im Bezug) wird LF ------------
o, z = baue('k12', {'a.txt': TXT_LF, 'neu.php': TXT_CRLF}, {'a.txt': TXT_CRLF})
rc, aus = lauf(z, o)
pruefe('12 neue Datei im Plugin-Ordner wird LF', rc, aus, 0,
       ['Neue Dateien: neu.php', 'angeglichen auf lf   : neu.php'])
sollwert(lese(os.path.join(o, 'neu.php')) == TXT_LF, 'neu.php jetzt LF')

shutil.rmtree(d, ignore_errors=True)
print()
if faelle == 0:
    print('ABBRUCH: kein einziger Fall gelaufen - diese Eichung hat nichts gemessen.')
    sys.exit(2)
print('%d Faelle, %d Verstoesse.' % (faelle, fehl))
sys.exit(1 if fehl else 0)
