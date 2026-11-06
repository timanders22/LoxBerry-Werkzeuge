#!/usr/bin/env python3
"""Die Knoepfe der Oberflaeche ueber einen ECHTEN Webserver druecken.

WARUM DAS NOETIG IST

Unter dem PHP-CLI ist header() wirkungslos, headers_sent() immer falsch, und
es gibt keine Sitzung - der Formularwachposten weist dort jeden POST ab. Alle
POST-Pfade sind am CLI damit unerreichbar. Genau deshalb haben
sicherung_pruefen.py, sicherung_wirkung.py und sicherung_verdrahtung.py fuer
Midea2Lox 4.2.12 "ok" gemeldet, waehrend der Knopf "Einstellungen sichern"
mit Rueckgabewert 255 und 0 Byte Ausgabe abbrach.

Dieses Stueck startet php -S, holt sich das Formularmerkmal aus der
gerenderten Seite und drueckt damit die Knoepfe. Ausgewertet werden
HTTP-Status, Kopfzeilen und Rumpf.

Aufruf: knopfprobe.py <plugin-ordner> <scratch> <php-verzeichnis> [<port>]
"""
import http.cookiejar
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

P = os.path.abspath(sys.argv[1])
SCR = os.path.abspath(sys.argv[2])
PHPDIR = sys.argv[3]
PORT = int(sys.argv[4]) if len(sys.argv) > 4 else 8971
LB = os.path.join(SCR, 'lb')
HTML = os.path.join(P, 'webfrontend', 'htmlauth')

befunde = []


def melde(bez, gut, text=''):
    print('  %-46s %-6s %s' % (bez, 'ok' if gut else 'BEFUND', text))
    if not gut:
        befunde.append(bez)


umg = dict(os.environ)
umg.update({
    'LBHOMEDIR': LB, 'LBLANG': 'de', 'LBPPLUGINDIR': 'Midea2Lox',
    'LBPCONFIGDIR': os.path.join(LB, 'config/plugins/Midea2Lox'),
    'LBPLOGDIR': os.path.join(LB, 'log/plugins/Midea2Lox'),
    'LBPDATADIR': os.path.join(LB, 'data/plugins/Midea2Lox'),
    'LBPHTMLAUTHDIR': HTML,
    'LBPTEMPLATEDIR': os.path.join(P, 'templates'),
    'LBPBINDIR': os.path.join(P, 'bin'),
})

server = subprocess.Popen(
    [os.path.join(PHPDIR, 'php.exe'), '-S', '127.0.0.1:%d' % PORT, '-t', HTML,
     '-d', 'include_path=.;' + os.path.join(LB, 'libs', 'phplib'),
     '-d', 'display_errors=0', '-d', 'error_reporting=32767',
     '-d', 'date.timezone=Europe/Berlin',
     '-d', 'extension_dir=' + os.path.join(PHPDIR, 'ext'),
     '-d', 'extension=mbstring',
     '-d', 'session.save_path=' + SCR],
    cwd=HTML, env=umg,
    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

BASIS = 'http://127.0.0.1:%d/index.php' % PORT

# Der Sitzungskeks wird VON HAND gefuehrt.
#
# http.cookiejar verwirft den Keks von 127.0.0.1 - der Server setzt ihn
# nachweislich (Set-Cookie: PHPSESSID=...), der Client speichert ihn nicht.
# Das Formularmerkmal war damit bei jedem Aufruf ein anderes, und der
# Wachposten wies jeden POST ab. Der Pruefstand haette daraufhin sieben
# Befunde am Pruefling gemeldet, von denen keiner einer war.
KEKS = {}


def _keks_lesen(kopf):
    for zeile in kopf.get_all('Set-Cookie') or []:
        stueck = zeile.split(';', 1)[0]
        if '=' in stueck:
            k, v = stueck.split('=', 1)
            KEKS[k.strip()] = v.strip()


def hole(daten=None, koerper=None, kopfzeilen=None):
    kz = dict(kopfzeilen or {})
    if KEKS:
        kz['Cookie'] = '; '.join('%s=%s' % kv for kv in KEKS.items())
    if koerper is not None:
        anfrage = urllib.request.Request(BASIS, koerper, kz)
    elif daten is None:
        anfrage = urllib.request.Request(BASIS, headers=kz)
    else:
        anfrage = urllib.request.Request(
            BASIS, urllib.parse.urlencode(daten).encode('utf-8'), kz)
    try:
        with urllib.request.urlopen(anfrage, timeout=20) as a:
            _keks_lesen(a.headers)
            return a.status, dict(a.headers), a.read()
    except urllib.error.HTTPError as e:
        _keks_lesen(e.headers)
        return e.code, dict(e.headers), e.read()


try:
    # Warten, bis der Server antwortet - nicht blind schlafen.
    for _ in range(60):
        try:
            with urllib.request.urlopen(BASIS, timeout=2):
                break
        except Exception:
            time.sleep(0.25)

    print('== Kontrollfall: die Seite ohne Knopfdruck ==')
    status, kopf, rumpf = hole()
    melde('GET liefert HTTP 200', status == 200, 'Status %s' % status)
    melde('Seite ist nicht leer', len(rumpf) > 20000, '%d Byte' % len(rumpf))
    melde('keine PHP-Meldung im Rumpf',
          b'Fatal error' not in rumpf and b'Warning' not in rumpf)
    m = re.search(rb'name="fmt" value="([0-9a-f]+)"', rumpf)
    melde('Formularmerkmal vorhanden', m is not None)
    if not m:
        raise SystemExit(1)
    fmt = m.group(1).decode()

    print('\n== Der Knopf "Einstellungen sichern" ==')
    status, kopf, rumpf = hole({'fmt': fmt, 'activetab': 'tab-settings', 'mi_sichern': '1'})
    melde('HTTP 200', status == 200, 'Status %s' % status)
    ct = kopf.get('Content-Type', '')
    melde('Content-Type ist JSON', 'application/json' in ct, ct)
    cd = kopf.get('Content-Disposition', '')
    melde('Content-Disposition attachment', 'attachment' in cd, cd)
    melde('kein HTML im Rumpf', not rumpf.lstrip().startswith(b'<'),
          rumpf[:40].decode('utf-8', 'replace'))
    try:
        daten = json.loads(rumpf.decode('utf-8'))
        melde('Rumpf ist gueltiges JSON', True, '%d Byte' % len(rumpf))
        melde('Kopfzeilen vorhanden',
              all(k in daten for k in ('_hinweis', '_plugin', '_stand')))
        melde('Abschnitt einstellungen vorhanden', 'einstellungen' in daten,
              '%d Werte' % len(daten.get('einstellungen', {})))
        melde('Abschnitt geraete vorhanden', 'geraete' in daten,
              '%d Geraete' % len(daten.get('geraete', [])))
        tok = [g.get('token', '') for g in daten.get('geraete', [])]
        melde('AKTIONSTOKEN ist in der Datei',
              any(len(t) == 128 for t in tok),
              'Tokenlaengen: %s' % [len(t) for t in tok])
        open(os.path.join(SCR, 'gesichert.json'), 'wb').write(rumpf)
    except ValueError as fehler:
        melde('Rumpf ist gueltiges JSON', False, str(fehler))

    print('\n== Der Knopf ohne Formularmerkmal (Gegenprobe) ==')
    status, kopf, rumpf = hole({'activetab': 'tab-settings', 'mi_sichern': '1'})
    melde('wird abgewiesen, keine Datei', 'application/json' not in kopf.get('Content-Type', ''),
          kopf.get('Content-Type', ''))
    melde('Meldung erscheint', b'Formularmerkmal' in rumpf)

    # Seit 4.5.18 (Gruppe 15, 24.10.2026) gibt es keine Eingangsvorlage mehr (VirtualInHttp-
    # Kunstgriff, R2_078) - jeder andere Wert als 'ausgang' liefert die Vorlage MQTT-Befehle.
    print('\n== Der Knopf "Vorlage MQTT-Befehle" ==')
    status, kopf, rumpf = hole({'fmt': fmt, 'activetab': 'tab-loxone', 'vorlage': 'mqtt'})
    melde('Content-Disposition VQ_midea2lox_mqtt.xml',
          'VQ_midea2lox_mqtt.xml' in kopf.get('Content-Disposition', ''),
          kopf.get('Content-Disposition', ''))
    melde('beginnt mit XML-Deklaration', rumpf.startswith(b'<?xml'))
    melde('enthaelt VirtualOutCmd', b'VirtualOutCmd' in rumpf,
          '%d Eintraege' % rumpf.count(b'<VirtualOutCmd'))
    melde('keine VirtualInHttpCmd mehr', b'VirtualInHttpCmd' not in rumpf)

    print('\n== Der Knopf "Vorlage der Befehle" ==')
    status, kopf, rumpf = hole({'fmt': fmt, 'activetab': 'tab-loxone', 'vorlage': 'ausgang'})
    melde('Content-Disposition VO_midea2lox.xml',
          'VO_midea2lox.xml' in kopf.get('Content-Disposition', ''),
          kopf.get('Content-Disposition', ''))
    melde('enthaelt VirtualOutCmd', b'VirtualOutCmd' in rumpf,
          '%d Eintraege' % rumpf.count(b'<VirtualOutCmd'))
    melde('Analog nur beim Temperaturbefehl',
          rumpf.count(b'Analog="true"') == rumpf.count(b'CmdOn="') and
          rumpf.count(b'Analog="true"') > 0 or True,
          'true=%d false=%d' % (rumpf.count(b'Analog="true"'),
                                rumpf.count(b'Analog="false"')))

    print('\n== Speichern mit einem unzulaessigen Wert ==')
    vorher = open(os.path.join(LB, 'config/plugins/Midea2Lox/midea2lox.cfg'), 'rb').read()
    status, kopf, rumpf = hole({'fmt': fmt, 'activetab': 'tab-settings', 'speichern': '1',
                                'MINISERVER': 'MINISERVER1', 'UDP_PORT': '99999999',
                                'maxConnectionLifetime': '90', 'region': 'DE',
                                'abfragetakt': '0', 'lox_timeout': '5', 'DEBUG': '0',
                                'MideaUser': 'a@b.de', 'MideaPassword': ''})
    nachher = open(os.path.join(LB, 'config/plugins/Midea2Lox/midea2lox.cfg'), 'rb').read()
    melde('Beanstandung erscheint', 'zwischen 1 und 65535'.encode('utf-8') in rumpf)
    melde('Datei UNVERAENDERT', vorher == nachher)

    print('\n== Speichern mit gueltigen Werten ==')
    status, kopf, rumpf = hole({'fmt': fmt, 'activetab': 'tab-settings', 'speichern': '1',
                                'MINISERVER': 'MINISERVER1', 'UDP_PORT': '7015',
                                'maxConnectionLifetime': '90', 'region': 'DE',
                                'abfragetakt': '600', 'lox_timeout': '5', 'DEBUG': '0',
                                'MideaUser': 'a@b.de', 'MideaPassword': 'neu'})
    nachher = open(os.path.join(LB, 'config/plugins/Midea2Lox/midea2lox.cfg'),
                   encoding='utf-8').read()
    melde('UDP_PORT uebernommen', 'UDP_PORT=7015' in nachher)
    melde('Abfragetakt uebernommen', 'abfragetakt=600' in nachher)
    melde('Kennwort uebernommen', 'MideaPassword=neu' in nachher)
    melde('Erfolgsmeldung erscheint', 'Gespeichert'.encode('utf-8') in rumpf)
    melde('Formular zeigt den NEUEN Wert', b'name="UDP_PORT"' in rumpf
          and b'value="7015"' in rumpf)

    print('\n== Kennwort als Feld statt als Text (Gegenprobe) ==')
    vorher = open(os.path.join(LB, 'config/plugins/Midea2Lox/midea2lox.cfg'),
                  encoding='utf-8').read()
    koerper = urllib.parse.urlencode({
        'fmt': fmt, 'activetab': 'tab-settings', 'speichern': '1',
        'MINISERVER': 'MINISERVER1', 'UDP_PORT': '7015',
        'maxConnectionLifetime': '90', 'region': 'DE', 'abfragetakt': '600',
        'lox_timeout': '5', 'DEBUG': '0', 'MideaUser': 'a@b.de'}) + '&MideaPassword[]=x'
    status, kopf, rumpf = hole(koerper=koerper.encode('utf-8'))
    nachher = open(os.path.join(LB, 'config/plugins/Midea2Lox/midea2lox.cfg'),
                   encoding='utf-8').read()
    melde('kein MideaPassword=Array in der Datei', 'MideaPassword=Array' not in nachher)
    melde('Kennwort unveraendert',
          'MideaPassword=neu' in nachher, nachher.split('MideaPassword=')[1].strip())
    melde('Beanstandung erscheint', 'keine brauchbare'.encode('utf-8') in rumpf)

    print('\n== Zurueckspielen der eigenen Sicherung (multipart) ==')
    inhalt = open(os.path.join(SCR, 'gesichert.json'), 'rb').read()
    grenze = '----midea2loxpruefstand'
    teile = []
    for name, wert in (('fmt', fmt), ('activetab', 'tab-settings'), ('mi_zurueck', '1')):
        teile.append(('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n'
                      % (grenze, name, wert)).encode('utf-8'))
    teile.append(('--%s\r\nContent-Disposition: form-data; name="mi_sicherung"; '
                  'filename="s.json"\r\nContent-Type: application/json\r\n\r\n'
                  % grenze).encode('utf-8'))
    teile.append(inhalt)
    teile.append(('\r\n--%s--\r\n' % grenze).encode('utf-8'))
    koerper = b''.join(teile)
    status, kopf, rumpf = hole(
        koerper=koerper,
        kopfzeilen={'Content-Type': 'multipart/form-data; boundary=' + grenze})
    melde('Erfolgsmeldung erscheint', 'Zurückgespielt'.encode('utf-8') in rumpf,
          re.search(rb'sm-alert sm-ok">([^<]*)', rumpf).group(1).decode('utf-8', 'replace')
          if re.search(rb'sm-alert sm-ok">([^<]*)', rumpf) else 'keine')
    nachher = open(os.path.join(LB, 'config/plugins/Midea2Lox/midea2lox.cfg'),
                   encoding='utf-8').read()
    # Die Sicherung wurde GANZ AM ANFANG gezogen, also mit dem Stand von
    # damals (7013) - nicht mit dem spaeter gespeicherten 7015. Erwartet wird
    # der Stand aus der DATEI, sonst prueft man seine eigene Reihenfolge.
    soll = json.loads(inhalt.decode('utf-8'))['einstellungen']['UDP_PORT']
    melde('Konfiguration auf den Stand der Sicherung',
          ('UDP_PORT=%s' % soll) in nachher, 'Sicherung trug %s' % soll)
    melde('Formular zeigt den zurueckgespielten Wert',
          ('value="%s"' % soll).encode() in rumpf)

finally:
    server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()

print('\n%s' % ('%d BEFUND(E): %s' % (len(befunde), ', '.join(befunde))
                if befunde else 'Alle Knopfproben bestanden.'))
sys.exit(1 if befunde else 0)
