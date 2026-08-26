#!/usr/bin/env python3
"""Wer behauptet den V1-Satz, ohne die Gateway-Fassung zu messen?

Anlass (25.08.2026): die Oberflaeche des Zendure-Plugins behauptete
unbedingt

    "Ohne diesen Eintrag kommt am Miniserver nichts an."

Der Satz stimmt fuer das MQTT-Gateway **V1**, wo jedes Thema von Hand auf
der Abo-Seite eingetragen werden muss. Unter **V2** erkennt das Gateway die
Themengruppe selbst - dort gibt es die Seite nicht mehr, und der Satz
schickt jeden V2-Anwender zu einem Eingabeplatz, den es nicht gibt.

MGiSmart 1.1.0 loest das richtig: es liest `Mqtt.Gatewayversion` aus
`config/system/general.json` - den Wert, den der LoxBerry selbst fuehrt
(ab Werk 1).

    python3 gateway_fassung_reihe.py

Drei Spalten, und nur die Kombination sagt etwas:

    MQTT      benutzt das Plugin ueberhaupt MQTT?
    misst     liest es Gatewayversion?
    behauptet steht der unbedingte V1-Satz in einer Sprachdatei?

Ein Plugin, das behauptet ohne zu messen, ist ein Befund. Eines ohne MQTT
geht die Frage nichts an.
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HIER = os.path.dirname(os.path.abspath(__file__))
ARBEIT = os.path.dirname(HIER)

# Der Satz in seinen bekannten Fassungen. Gesucht wird der KERN, damit
# Umformulierungen nicht durchrutschen.
V1_SATZ = re.compile(
    r'(ohne\s+(diesen|den)\s+eintrag\s+kommt\s+am\s+miniserver\s+nichts\s+an'
    r'|without\s+th(is|e)\s+entry\s+nothing\s+arrives\s+at\s+the\s+miniserver)',
    re.I)

# Wer die Fassung misst, nennt diesen Schluessel.
MISST = re.compile(r'Gatewayversion', re.I)

# Benutzt das Plugin MQTT? Nicht am Namen erkennen, sondern an dem, was es tut.
MQTT = re.compile(r'mqtt_connectiondetails|mosquitto_(pub|sub)|Mqtt\W|mqttgateway', re.I)


def dateien(ordner, endungen=('.php', '.pl', '.py', '.ini', '.html')):
    for w, _, ds in os.walk(ordner):
        if os.sep + '.git' in w:
            continue
        for d in ds:
            if d.endswith(endungen):
                yield os.path.join(w, d)


def main():
    zeilen = []
    for e in sorted(os.listdir(ARBEIT)):
        o = os.path.join(ARBEIT, e)
        if not (e.startswith('LoxBerry-Plugin-') and os.path.isdir(o)):
            continue
        nutzt = misst = False
        behauptet = []
        for p in dateien(o):
            try:
                t = io.open(p, encoding='utf-8', errors='replace').read()
            except Exception:
                continue
            if MQTT.search(t):
                nutzt = True
            if MISST.search(t):
                misst = True
            if p.endswith('.ini') and V1_SATZ.search(t):
                behauptet.append(os.path.basename(p))
        if not (nutzt or behauptet):
            continue
        zeilen.append((e[16:], nutzt, misst, behauptet))

    print('%-34s %-6s %-7s %s' % ('Plugin', 'MQTT', 'misst', 'behauptet den V1-Satz'))
    print('-' * 88)
    befunde = []
    for name, nutzt, misst, behauptet in zeilen:
        marke = ''
        if behauptet and not misst:
            marke = '  <== BEFUND'
            befunde.append(name)
        print('%-34s %-6s %-7s %s%s'
              % (name[:33], 'ja' if nutzt else '-', 'ja' if misst else 'nein',
                 ', '.join(behauptet) or '-', marke))
    print('-' * 88)
    print('%d Plugins mit MQTT oder V1-Satz, %d Befund(e)' % (len(zeilen), len(befunde)))
    if befunde:
        print('\nZu erledigen: %s' % ', '.join(befunde))
    return 1 if befunde else 0


if __name__ == '__main__':
    sys.exit(main())
