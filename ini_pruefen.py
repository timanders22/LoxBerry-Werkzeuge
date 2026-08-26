#!/usr/bin/env python3
"""Sprachdateien auf gerade Anfuehrungszeichen in Werten pruefen.

Der Anlass, 19.08.2026: in der Einspeisebremse enthielten 14 Werte je
Sprachdatei gerade Anfuehrungszeichen - fast alle als HTML-Attribut
(class="sm-mono"). Ein Wert steht in "..."; ein weiteres " darin beendet
ihn vorzeitig.

Die Folgen sind unterschiedlich schlimm und BEIDE stumm:

    Modus NORMAL / TYPED   der Wert wird abgeschnitten (deutsch: 780 statt
                           1464 Zeichen, mitten im Satz), oder die GANZE
                           Datei wird abgewiesen (englisch: parse_ini_file()
                           liefert false - die Oberflaeche waere textlos)
    Modus RAW              faellt gar nichts auf

Zwoelf der vierzehn Werte steckten schon in der veroeffentlichten Fassung
0.9.8. Aufgefallen ist es erst, als jemand dieselben Dateien mit dem
Standardmodus gelesen hat.

DESHALB PRUEFT DIESES WERKZEUG BEIDES: die Ursache (gerade
Anfuehrungszeichen) und die Wirkung (liefern alle Lesemodi dasselbe?).

Abhilfe im Text:
    HTML-Attribute einfach quotieren     class='sm-mono'
    typografische Anfuehrungszeichen     „so“ statt „so"

Aufruf:  python3 ini_pruefen.py ORDNER_ODER_DATEI [...]
Rueckgabe 1, sobald etwas gefunden wurde - fuer den Bauablauf.
"""
import os
import re
import subprocess
import sys
import json

ZIELE = [a for a in sys.argv[1:] if not a.startswith('--')] or ['.']


def dateien(ziel):
    if os.path.isfile(ziel):
        return [ziel]
    r = []
    for wurzel, _, ds in os.walk(ziel):
        for d in sorted(ds):
            if d.endswith('.ini'):
                r.append(os.path.join(wurzel, d))
    return sorted(r)


def php_da():
    try:
        subprocess.run(['php', '-v'], capture_output=True, timeout=10)
        return True
    except Exception:
        return False


PHP = php_da()
PRUEFSKRIPT = r'''
$p = $argv[1];
$aus = array();
foreach (array("RAW"=>INI_SCANNER_RAW, "NORMAL"=>INI_SCANNER_NORMAL,
               "TYPED"=>INI_SCANNER_TYPED) as $name => $m) {
    $i = @parse_ini_file($p, true, $m);
    if ($i === false) { $aus[$name] = null; continue; }
    $n = 0; $laenge = 0;
    foreach ($i as $abs) foreach ($abs as $v) { $n++; $laenge += strlen((string)$v); }
    $aus[$name] = array($n, $laenge);
}
echo json_encode($aus);
'''

gefunden = 0
for ziel in ZIELE:
    for p in dateien(ziel):
        roh = open(p, 'rb').read()
        crlf = roh.count(b'\r\n')
        trenner = '\r\n' if crlf else '\n'
        zeilen = roh.decode('utf-8', 'replace').split(trenner)
        abschnitt = None
        treffer = []
        for nr, z in enumerate(zeilen, 1):
            if z.startswith('['):
                abschnitt = z.strip('[]')
                continue
            m = re.match(r'^([A-Z0-9_]+)\s*=\s*"(.*)"\s*$', z)
            if m and '"' in m.group(2):
                attr = len(re.findall(r'\s[a-zA-Z-]+="', m.group(2)))
                treffer.append((nr, abschnitt or '?', m.group(1),
                                m.group(2).count('"'), attr))
        print('== %s (%s, %d Zeilen) ==' % (p, 'CRLF' if crlf else 'LF', len(zeilen)))
        for nr, abs_, k, anz, attr in treffer:
            print('  Zeile %-5d %-14s %-32s %2d gerade "  (%d als Attribut)'
                  % (nr, abs_, k, anz, attr))
        if treffer:
            gefunden += len(treffer)
            print('  ---> %d betroffene Werte' % len(treffer))
        else:
            print('  ---> keine geraden Anfuehrungszeichen in Werten')

        # Die Wirkung, nicht nur die Ursache.
        if PHP:
            r = subprocess.run(['php', '-r', PRUEFSKRIPT, p],
                               capture_output=True, text=True, timeout=30)
            try:
                d = json.loads(r.stdout)
            except Exception:
                print('  (Lesemodi nicht pruefbar: %s)' % (r.stderr.strip()[:60] or 'keine Antwort'))
                print()
                continue
            zeile = '  Lesemodi: '
            schlecht = False
            grund = d.get('RAW')
            for name in ('RAW', 'NORMAL', 'TYPED'):
                w = d.get(name)
                if w is None:
                    zeile += '%s=FALSE  ' % name
                    schlecht = True
                else:
                    zeile += '%s=%d/%dZ  ' % (name, w[0], w[1])
                    if grund and w != grund:
                        schlecht = True
            print(zeile + ('  <== WEICHEN AB' if schlecht else '  alle gleich'))
            if schlecht:
                gefunden += 1
        print()

if gefunden:
    print('BEFUND: %d Beanstandungen. HTML-Attribute einfach quotieren '
          '(class=\'sm-mono\'), typografische Anfuehrungszeichen schliessen.' % gefunden)
    sys.exit(1)
print('In Ordnung.')
