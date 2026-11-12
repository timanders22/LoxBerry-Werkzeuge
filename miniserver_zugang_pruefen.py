#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kodierte Miniserver-Zugangsdaten als Anmeldung? - nur lesend.

ANLASS (Beschattungswaechter Issue #2, 26.10.2026; Bauart gefunden 09.11.2026)
LoxBerry fuehrt Benutzer und Passwort des Miniservers zweimal:
'Admin'/'Pass'/'Credentials' fuer Adressen KODIERT (aus '!' wird '%21'),
'Admin_raw'/'Pass_raw'/'Credentials_raw' (Perl/PHP-Bibliothek: *_RAW) im
Klartext. Belegt am Geraet: LoxBerry/System.pm und der Test
perllib/t/auth_ms.t ("Passwort aus Pass_raw, nicht aus Pass"). Wer das
kodierte Feld in eine Basic-Anmeldung steckt, bekommt bei jedem Passwort mit
Sonderzeichen HTTP 401. Gefunden in Beschattungswaechter, Raumklima und
BLE-Scanner (vier Stellen) - kein Pruefwerkzeug hatte danach gesucht.

WAS ES SUCHT
Jeden Zugriff auf einen der Schluessel Pass, Admin, Credentials (PHP
$x['Pass'], Python .get("Pass") / ["Pass"], Perl {Pass}) in .php, .py, .pl,
.pm, .cgi. Ein Zugriff gilt als BEHANDELT, wenn in einem Fenster von 15 Zeilen
davor oder danach entweder das Klartextfeld (*_raw / *_RAW) oder eine
Rueckwandlung (rawurldecode, urldecode, unquote, uri_unescape) steht. Sonst
ist es ein Befund mit Datei und Zeile. Das Fenster ist eine Naeherung: ein
Befund ist eine Frage, die man am Code beantwortet, kein Urteil.
Nicht gemeint: Brokerpass, Password, Pass_raw selbst, Kommentare (Zeilen, die
mit //, #, * oder /* beginnen).

AUFRUF
    python Werkzeuge/miniserver_zugang_pruefen.py ORDNER [ORDNER ...]
ORDNER ist ein Plugin-Ordner oder ein Verzeichnis mit Plugin-Ordnern (dann je
Linie die hoechste Fassung). Rueckgabe 0 ohne Befund, 1 mit Befund, 2 wenn
keine Datei angesehen wurde. Die letzte Zeile ist immer eine Zaehlzeile.

GEEICHT (10.11.2026, Pruefung-Miniserver-Zugang-2026-11-09/eichung.txt)
Schlecht: die vier Stellen vor der Korrektur (alt/) - muss je anschlagen.
Gut: die berichtigten Fassungen und Dashboard, Sprachsteuerung, Intercom, die
das Klartextfeld schon nehmen - muss schweigen.
"""
import os
import re
import sys

ZUGRIFF = re.compile(
    r"""\[\s*['"](Pass|Admin|Credentials)['"]\s*\]"""      # PHP/Python $x['Pass'], x["Pass"]
    r"""|\.get\(\s*['"](Pass|Admin|Credentials)['"]"""     # Python .get("Pass")
    r"""|\{\s*(Pass|Admin|Credentials)\s*\}""")            # Perl {Pass}
BEHANDELT = re.compile(r'_raw\b|_RAW\b|rawurldecode|urldecode|unquote|uri_unescape', re.I)
KOMMENTAR = re.compile(r'^\s*(//|#|\*|/\*)')
ENDUNGEN = ('.php', '.py', '.pl', '.pm', '.cgi')
FENSTER = 15


def plugin_ordner(wurzel):
    """Ein Plugin-Ordner oder je Linie die hoechste Fassung darunter."""
    if os.path.isfile(os.path.join(wurzel, 'plugin.cfg')):
        return [wurzel]
    linien = {}
    for name in os.listdir(wurzel):
        m = re.match(r'^(LoxBerry-Plugin-.+?)-(\d+(?:\.\d+)+)$', name)
        p = os.path.join(wurzel, name)
        if not m or not os.path.isfile(os.path.join(p, 'plugin.cfg')):
            continue
        fass = tuple(int(x) for x in m.group(2).split('.'))
        if m.group(1) not in linien or fass > linien[m.group(1)][0]:
            linien[m.group(1)] = (fass, p)
    return [v[1] for _, v in sorted(linien.items())]


def datei_pruefen(pfad):
    try:
        zeilen = open(pfad, 'rb').read().decode('utf-8', 'replace').splitlines()
    except OSError:
        return None
    befunde = []
    for i, z in enumerate(zeilen):
        if KOMMENTAR.match(z) or not ZUGRIFF.search(z):
            continue
        um = zeilen[max(0, i - FENSTER):i + FENSTER + 1]
        if any(BEHANDELT.search(u) for u in um):
            continue
        befunde.append((i + 1, z.strip()[:140]))
    return befunde


def main(argv):
    if not argv:
        print(__doc__.split('AUFRUF')[1].split('GEEICHT')[0].strip())
        return 2
    ordner = []
    for a in argv:
        ordner.extend(plugin_ordner(a))
    dateien = 0
    gesamt = 0
    linien_mit = 0
    for o in ordner:
        eigene = 0
        for w, ds, fs in os.walk(o):
            ds[:] = [d for d in ds if d not in ('__pycache__', '.git')]
            for f in sorted(fs):
                if not f.endswith(ENDUNGEN):
                    continue
                p = os.path.join(w, f)
                b = datei_pruefen(p)
                if b is None:
                    continue
                dateien += 1
                for nr, z in b:
                    print('BEFUND %s:%d  %s' % (os.path.relpath(p), nr, z))
                    eigene += 1
        gesamt += eigene
        linien_mit += 1 if eigene else 0
    print('miniserver_zugang_pruefen: %d Ordner, %d Dateien angesehen, %d Befund(e) in %d Ordner(n).'
          % (len(ordner), dateien, gesamt, linien_mit))
    if dateien == 0:
        return 2
    return 1 if gesamt else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
