# -*- coding: utf-8 -*-
"""Liegt jedes Einbindungsbild eines Plugins byteweise gleich im Musterprojekt-Repository?

Anlass (07.11.2026): Die Seiten von Weatherdata wurden am 05.11. im lokalen Musterprojekt gebaut, gedruckt und ins
Plugin uebernommen - ins Repository LoxBerry-Plugins-Musterprojekt kamen sie nie. Gemessen waren danach 10 Bilder
aus 5 Linien nicht im Repository (Weatherdata fehlte ganz; MGiSmart, Smartmeter, Dashboard neuer im Plugin;
Kodi-NG aelter im Plugin). Der Schritt "Repository nachziehen" war in keiner Kette.

Aufruf:
  python musterprojekt_bilder_pruefen.py [--bilder ORDNER] [PLUGINORDNER ...]
    --bilder   Bilderordner des Musterprojekts (Vorgabe: LoxBerry-Plugins-Musterprojekt/bilder im Arbeitsordner,
               vorher 'git pull' dort, sonst misst man einen alten Stand)
    ohne PLUGINORDNER: je Linie der hoechste Ordner LoxBerry-Plugin-<Name>-X.Y.Z im Arbeitsordner
Rein lesend. Gibt nur Namen und Pruefsummen-Anfaenge aus.
Rueckgabe: 0 = jedes Bild vorhanden; 1 = mindestens ein Bild fehlt im Repository; 2 = nicht pruefbar
(Bilderordner leer/fehlt, kein Plugin mit Einbindungsbild).
Eichung 07.11.2026: gegen den Repository-Stand 9ec173e (01.11.) 7 Bilder aus 4 Linien rot (bekannter Fehlfall:
Weatherdata 2, MGiSmart 1, Dashboard 1, Smartmeter 3); gegen den nachgezogenen Stand 0; leerer Bilderordner = 2.
Die erste Fassung zaehlte KODI-NG-1.2.20 (alter Ordnername) als eigene Linie und meldete 3 Fehlalarme.
"""
import glob, hashlib, os, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = sys.argv[1:]
bilder = os.path.join(B, 'LoxBerry-Plugins-Musterprojekt', 'bilder')
if '--bilder' in args:
    i = args.index('--bilder'); bilder = args[i + 1]; del args[i:i + 2]
if not os.path.isdir(bilder):
    print('NICHT PRUEFBAR: Bilderordner fehlt: %s' % bilder); sys.exit(2)
repo = {}
for f in os.listdir(bilder):
    if f.lower().endswith('.png'):
        repo.setdefault(hashlib.md5(open(os.path.join(bilder, f), 'rb').read()).hexdigest(), f)
if not repo:
    print('NICHT PRUEFBAR: keine Bilder in %s' % bilder); sys.exit(2)
if args:
    ordner = args
else:
    hoch = {}
    for d in glob.glob(os.path.join(B, 'LoxBerry-Plugin-*-*')):
        m = re.match(r'LoxBerry-Plugin-(.+)-(\d+)\.(\d+)\.(\d+)$', os.path.basename(d))
        if m and os.path.isdir(d):
            v = tuple(int(x) for x in m.groups()[1:])
            # Linie ohne Ruecksicht auf Gross-/Kleinschreibung: KODI-NG-1.2.20 (alter Name) und Kodi-NG-1.2.27 sind
            # eine Linie - sonst meldet der alte Ordner Fehlalarme (gemessen 07.11.2026).
            k = m.group(1).lower()
            if k not in hoch or v > hoch[k][0]:
                hoch[k] = (v, d)
    ordner = [d for _, d in sorted(hoch.values(), key=lambda x: x[1])]
mit, fehlt = 0, []
for d in ordner:
    pngs = sorted(glob.glob(os.path.join(d, 'webfrontend', '**', 'einbindung*.png'), recursive=True))
    if not pngs:
        continue
    mit += 1
    for p in pngs:
        h = hashlib.md5(open(p, 'rb').read()).hexdigest()
        if h not in repo:
            fehlt.append((os.path.basename(d), os.path.basename(p), h[:8]))
if mit == 0:
    print('NICHT PRUEFBAR: kein Plugin mit Einbindungsbild unter %d Ordner(n)' % len(ordner)); sys.exit(2)
print('%d Plugin(s) mit Einbindungsbildern geprueft gegen %d Bilder in %s' % (mit, len(repo), bilder))
for d, f, h in fehlt:
    print('  FEHLT IM MUSTERPROJEKT: %s %s (%s)' % (d, f, h))
print('Ergebnis: %s' % ('alle Einbindungsbilder im Musterprojekt' if not fehlt else '%d Bild(er) nicht im Musterprojekt - Repository nachziehen oder Plugin-Bild pruefen' % len(fehlt)))
sys.exit(1 if fehlt else 0)
