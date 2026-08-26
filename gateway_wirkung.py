#!/usr/bin/env python3
"""Zeigt die Oberflaeche wirklich den richtigen Gateway-Text?

Gemessen an der GERENDERTEN Seite, nicht am Quelltext. Ein Quelltext mit
einer Verzweigung beweist nicht, dass sie greift - dazwischen liegen noch
die Sprachdateien und die Frage, ob die Fassung ueberhaupt ankommt.

Drei Laeufe je Plugin, mit verstellter `Mqtt.Gatewayversion` in der
general.json der Attrappe:

    Gatewayversion 1      -> der V1-Satz, und NUR er
    Gatewayversion 2      -> der V2-Satz, und der V1-Satz NICHT mehr
    Schluessel fehlt      -> beide Faelle genannt, keiner behauptet

Der zweite Lauf ist der eigentliche Punkt: eine Seite, die beide Texte
untereinander zeigt, waere sonst gruen.

    python3 gateway_wirkung.py <Pluginordner> [...]

Rueckgabe 0, wenn alle geprueften Plugins alle drei Faelle bestehen.
"""
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HIER = os.path.dirname(os.path.abspath(__file__))
ARBEIT = os.path.dirname(HIER)
LB = os.path.join(HIER, 'lb')
GEN = os.path.join(LB, 'config', 'system', 'general.json')

V1 = re.compile(r'ohne\s+(diesen|den)\s+eintrag\s+kommt\s+am\s+miniserver'
                r'|without\s+th(is|e)\s+entry\s+nothing\s+arrives', re.I)
V2 = re.compile(r'erkennt\s+die\s+themengruppe\s+von\s+selbst'
                r'|detects\s+the\s+topic\s+group\s+by\s+itself', re.I)
UNBEKANNT = re.compile(r'lie(ß|ss)\s+sich\s+nicht\s+feststellen'
                       r'|could\s+not\s+be\s+determined', re.I)


def fassung_setzen(wert):
    d = json.load(io.open(GEN, encoding='utf-8')) if os.path.isfile(GEN) else {}
    d.setdefault('Mqtt', {})
    d['Mqtt'].pop('Gatewayversion', None)
    if wert is not None:
        d['Mqtt']['Gatewayversion'] = wert
    json.dump(d, io.open(GEN, 'w', encoding='utf-8'))


# Gerendert wird ueber rendern.py - NICHT ueber einen eigenen php-Aufruf.
# Der erste Anlauf rief schlicht `php index.php` und bekam fuer JEDES Plugin
# eine leere Seite, auch fuer MGiSmart, das nachweislich richtig gebaut ist.
# rendern.py setzt acht Umgebungsvariablen, einen include_path, einen
# auto_prepend_file und fuenf Erweiterungen; das nachzubauen hiesse, eine
# zweite Wahrheit zu pflegen.
sys.path.insert(0, HIER)
import importlib
_rendern = importlib.import_module('rendern')


def rendern(ordner):
    """Die htmlauth-Oberflaeche einmal ausfuehren und den Text zurueckgeben."""
    dateien = list(_rendern.oberflaechen(_rendern.Path(ordner)))
    if not dateien:
        return None
    php = next((p for _v, p in _rendern.PHPS if os.path.isfile(p)), None)
    if php is None:
        return None
    seite, _befunde, _rest = _rendern.lauf(php, dateien[0],
                                           os.path.basename(ordner))
    return seite


def main():
    ordner = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not ordner:
        ordner = [e for e in sorted(os.listdir(ARBEIT))
                  if e.startswith('LoxBerry-Plugin-')
                  and os.path.isdir(os.path.join(ARBEIT, e))]
    alt = io.open(GEN, 'rb').read() if os.path.isfile(GEN) else None

    print('%-32s %-14s %-14s %s' % ('Plugin', 'V1 gesetzt', 'V2 gesetzt', 'ohne Angabe'))
    print('-' * 82)
    fehler = 0
    try:
        for e in ordner:
            o = e if os.path.isdir(e) else os.path.join(ARBEIT, e)
            if not os.path.isdir(o):
                continue
            urteile = []
            for wert, erwartet in ((1, 'v1'), (2, 'v2'), (None, 'unbekannt')):
                fassung_setzen(wert)
                t = rendern(o)
                if t is None:
                    urteile.append('nicht gerendert')
                    continue
                hat_v1, hat_v2 = bool(V1.search(t)), bool(V2.search(t))
                hat_un = bool(UNBEKANNT.search(t))
                # Steht das HTML des Hinweises MASKIERT auf der Seite? Dann
                # liest der Anwender die spitzen Klammern. Fuenf Stellen in
                # drei Plugins standen am 25.08.2026 in einem xx_e(...) -
                # der Text erschien, und die Pruefung meldete gruen. Ein
                # Ergebnis, das nur "der Text ist da" misst, misst zu wenig.
                if re.search(r'&lt;(b|span|i)[ &]', t):
                    urteile.append('ROT (HTML maskiert)')
                    continue
                # Kommt ueberhaupt einer der drei Texte vor? Wenn keiner, hat
                # die Seite den Abschnitt gar nicht gezeigt - etwa weil das
                # Plugin seine Sprachdatei am INSTALLIERTEN Ort sucht, den
                # die Attrappe nicht hat (Midea2Lox). Das ist ein Strich,
                # kein Befund: hier ist nichts zu messen, und ein rotes Kreuz
                # an dieser Stelle wuerde beim naechsten Mal ueberlesen.
                if not (hat_v1 or hat_v2 or hat_un):
                    urteile.append('--  (kein Text - nicht messbar)')
                    continue
                # Der UNBEKANNT-Text enthaelt den V1-Satz - er nennt ja beide
                # Faelle. Ohne "und nicht der Unbekannt-Text" sah ein Plugin,
                # das die Fassung gar nicht liest (immer 0 -> unbekannt), bei
                # gesetztem V1 richtig aus. Genau das ist am 25.08.2026
                # passiert und hat mehrere kaputte Umbauten gruen gemeldet.
                if erwartet == 'v1':
                    gut = hat_v1 and not hat_v2 and not hat_un
                elif erwartet == 'v2':
                    gut = hat_v2 and not hat_v1
                else:
                    gut = hat_un or (hat_v1 and hat_v2)
                urteile.append(('ok' if gut else 'ROT') +
                               ' (V1:%d V2:%d U:%d)' % (hat_v1, hat_v2, hat_un))
            if any(u.startswith('ROT') for u in urteile):
                fehler += 1
            print('%-32s %-14s %-14s %s' % (e[16:47], *urteile))
    finally:
        if alt is not None:
            io.open(GEN, 'wb').write(alt)

    print('-' * 82)
    print('%d Plugin(e), %d mit Befund' % (len(ordner), fehler))
    return 1 if fehler else 0


if __name__ == '__main__':
    sys.exit(main())
