#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Welche Linien melden per MQTT, welche nicht?

Rein lesend. Gesucht wird nach dem, was ein LoxBerry-Plugin zum Melden
braucht - nicht nach dem Wort "MQTT" in der Dokumentation:

  * eine Sendefunktion mit 'publish ' als UDP-Nutzlast (das Gateway-Relais),
  * ODER eine Bibliothek wie phpMQTT/Net::MQTT, die selbst zum Broker geht,
  * dazu ein Schalter mqtt_enabled in der Konfiguration und ein Themen-Praefix.

Ausgegeben wird je Linie, WAS gefunden wurde - damit sich unterscheiden
laesst: meldet gar nicht, meldet ueber das Gateway, meldet selbst.
"""
import io, os, re, sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
B = Path(__file__).resolve().parent.parent


def neueste_ordner():
    """Je Linie nur der Ordner mit der hoechsten Fassung."""
    nach_linie = {}
    for p in sorted(B.iterdir()):
        if not p.is_dir() or not p.name.startswith('LoxBerry-Plugin-'):
            continue
        if not (p / 'plugin.cfg').is_file():
            continue
        m = re.match(r'^(.*)-(\d+)\.(\d+)\.(\d+)$', p.name)
        if m:
            linie = m.group(1)
            v = tuple(int(x) for x in m.groups()[1:])
        else:
            linie, v = p.name, (0, 0, 0)
        if linie not in nach_linie or v > nach_linie[linie][1]:
            nach_linie[linie] = (p, v)
    return [p for p, _ in sorted(nach_linie.values(), key=lambda t: t[0].name.lower())]


def quelltexte(ordner):
    aus = []
    for muster in ('**/*.php', '**/*.pl', '**/*.pm', '**/*.py', '**/*.sh'):
        for f in ordner.glob(muster):
            if '__pycache__' in str(f):
                continue
            try:
                aus.append((f, f.read_text(encoding='utf-8', errors='replace')))
            except Exception:
                pass
    return aus


GATEWAY = re.compile(r"['\"]publish\s")               # UDP-Relais des Gateways
EIGEN = re.compile(r'phpMQTT|Net::MQTT|paho|mosquitto_pub|MqttClient', re.I)
SCHALTER = re.compile(r'mqtt_enabled|mqtt_ein\b|Mqtt.{0,3}enabled', re.I)
THEMA = re.compile(r'mqtt_topic|mqtt_praefix|mqtt_prefix', re.I)
ABO = re.compile(r'subscribe|mqtt_abo', re.I)

print('%-34s %-9s %-8s %-7s %-6s %s' % ('Linie', 'Fassung', 'sendet', 'Schalter', 'Thema', 'wie'))
print('-' * 92)
ohne = []
mit = []
for ordner in neueste_ordner():
    cfg = (ordner / 'plugin.cfg').read_text(encoding='utf-8', errors='replace')
    v = re.search(r'^VERSION=(\S+)', cfg, re.M)
    v = v.group(1) if v else '?'
    dateien = quelltexte(ordner)
    gw = any(GATEWAY.search(t) for _, t in dateien)
    eig = any(EIGEN.search(t) for _, t in dateien)
    sch = any(SCHALTER.search(t) for _, t in dateien)
    thm = any(THEMA.search(t) for _, t in dateien)
    abo = any(ABO.search(t) for _, t in dateien)
    wie = []
    if gw:
        wie.append('Gateway (UDP)')
    if eig:
        wie.append('eigener Broker-Zugang')
    if abo and not (gw or eig):
        wie.append('nur Abo, kein Senden')
    print('%-34s %-9s %-8s %-8s %-6s %s'
          % (ordner.name.replace('LoxBerry-Plugin-', '')[:34], v,
             'ja' if (gw or eig) else 'NEIN',
             'ja' if sch else '-', 'ja' if thm else '-',
             ', '.join(wie) or '-'))
    (mit if (gw or eig) else ohne).append(ordner.name.replace('LoxBerry-Plugin-', ''))

print('-' * 92)
print('%d Linien insgesamt: %d senden per MQTT, %d nicht.' % (len(mit) + len(ohne), len(mit), len(ohne)))
if ohne:
    print('\nOhne MQTT-Meldung:')
    for n in ohne:
        print('  - %s' % n)
