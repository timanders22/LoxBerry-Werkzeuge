#!/usr/bin/env python3
"""Halten die Plugins dieselbe innere Form?

Anlass, 28.08.2026: beim Einbau des Wachpostens in dreizehn Linien musste je
Linie sieben Angaben von Hand gemessen werden, weil dieselbe Sache in jedem
Plugin anders hiess. Das kostet bei JEDER Aenderung, die mehrere Linien
betrifft - und der Bestand hat rund fuenfzig.

Dieses Werkzeug misst die Abweichung, damit sie sichtbar bleibt. Es
veraendert nichts.

WAS ALS HAUSFORM GILT (siehe REGELN_2, "Die innere Form eines Plugins")

  Pfadfunktion            <p>_paths()          nicht _pfade
  Datenverzeichnis        Schluessel 'datadir' nicht 'data'
  Escape-Helfer           <p>_e() in der BIBLIOTHEK, nicht in index.php
  Meldeziel               $<p>_fehler = array(), also eine LISTE
  Uebersetzer             <p>_t()

WAS NICHT VEREINHEITLICHT WIRD - und warum

  WO die Bibliothek liegt, ist eine Entscheidung, keine Schreibweise:
  html/ ist ohne Anmeldung lesbar. Dorthin gehoert sie NUR, wenn der
  Endpunkt sie braucht; sonst nach htmlauth/. Eine Linie, die sie ohne
  Not nach html/ legt, macht mehr lesbar als noetig - das waere
  Gleichmacherei gegen die Sache.

Aufruf:  hausform_pruefen.py [ORDNER ...]      (ohne Angabe: alle aktuellen)
"""
import glob, os, re, sys

SOLL = ('_paths', 'datadir', 'Bibliothek', 'Liste', 'fehler')


def aktuelle():
    st = {}
    for d in sorted(glob.glob('LoxBerry-Plugin-*')):
        if not os.path.isdir(d):
            continue
        m = re.match(r'(LoxBerry-Plugin-.+?)-(\d[\d.]*)$', d)
        if not m:
            continue
        k = tuple(int(x) for x in m.group(2).split('.'))
        if m.group(1) not in st or k > st[m.group(1)][0]:
            st[m.group(1)] = (k, d)
    return [v[1] for v in st.values()]


def messe(d):
    idx = os.path.join(d, 'webfrontend', 'htmlauth', 'index.php')
    libs = (glob.glob(os.path.join(d, 'webfrontend', 'html', '*_lib.php'))
            + glob.glob(os.path.join(d, 'webfrontend', 'htmlauth', '*_lib.php')))
    if not os.path.isfile(idx) or not libs:
        return None
    ti = open(idx, encoding='utf-8', errors='replace').read()
    tl = open(libs[0], encoding='utf-8', errors='replace').read()

    pf = '_pfade' if re.search(r'function [a-z]+_pfade\b', tl) else (
        '_paths' if re.search(r'function [a-z]+_paths\b', tl) else '?')
    if re.search(r"'datadir'\s*=>", tl):
        key = 'datadir'
    elif re.search(r"'data'\s*=>", tl):
        key = 'data'
    else:
        key = '?'
    esc = re.findall(r'function ([a-z]+_e)\s*\(', ti + tl)
    wo = ('Bibliothek' if esc and re.search(r'function %s\s*\(' % esc[0], tl)
          else ('index.php' if esc else '?'))
    liste = re.findall(r'\$([a-z_]*(?:fehler|mangel)[a-z_]*)\s*=\s*array\(\)', ti)
    skalar = re.findall(r"\$([a-z_]*fehler[a-z_]*)\s*=\s*''", ti)
    art = 'Liste' if liste else ('Zeichenkette' if skalar else '?')
    name = re.sub(r'^[a-z]+_', '', (liste or skalar or ['?'])[0])
    return (pf, key, wo, art, name)


ordner = sys.argv[1:] or aktuelle()
print('%-30s %-8s %-9s %-11s %-13s %-11s %s'
      % ('Plugin', 'Pfadfn', 'Datenschl', 'Escape in', 'Meldeziel', 'heisst', 'Abweichungen'))
print('-' * 100)
n_ab = 0
for d in sorted(ordner):
    r = messe(d)
    if r is None:
        continue
    ab = sum(1 for ist, soll in zip(r, SOLL) if ist != soll)
    n_ab += 1 if ab else 0
    print('%-30s %-8s %-9s %-11s %-13s %-11s %s'
          % (os.path.basename(d)[16:46], r[0], r[1], r[2], r[3], r[4],
             ab if ab else '-'))
print('-' * 100)
print('%d von %d Linien weichen ab. Eine Abweichung ist kein Fehler - sie '
      'kostet bei jeder\nAenderung, die mehrere Linien betrifft.'
      % (n_ab, len([1 for d in ordner if messe(d)])))
