#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Die Knoepfe des Einrichtungs-Assistenten ueber einen ECHTEN Webserver.

Unter dem PHP-CLI weist der Formularwachposten jeden POST ab - alle
POST-Pfade sind dort unerreichbar. Deshalb php -S, Formularmerkmal aus der
gerenderten Seite holen, Knoepfe druecken, und danach in die
KONFIGURATIONSDATEI schauen: nicht "hat geantwortet", sondern "was steht
jetzt drin".

Aufruf: assistent_knopfprobe.py <plugin> <lb-bank> <phpdir> <port>
"""
import http.cookiejar
import io
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
LB = os.path.abspath(sys.argv[2])
PHPDIR = sys.argv[3]
PORT = int(sys.argv[4])
HTML = os.path.join(P, 'webfrontend', 'htmlauth')
CFG = os.path.join(LB, 'config/plugins/raumklima/raumklima.json')
# Der Port kommt aus der Bank, nicht aus dem Quelltext. Bis 0.11.1
# stand hier die getippte 24500; wer die Bank auf einen anderen Port
# stellte, bekam einen Befund des Pruefstands, der wie einer des
# Prueflings aussah.
_gen = json.load(io.open(os.path.join(LB, 'config/system/general.json'),
                        encoding='utf-8'))
_ms = _gen['Miniserver']['1']
MS_WIRT = '%s:%s' % (_ms['Ipaddress'],
                     _ms['Porthttps'] if _ms.get('Preferhttps') == '1'
                     else _ms['Port'])
MS_SCHEMA = 'https' if _ms.get('Preferhttps') == '1' else 'http'
GEH = os.path.join(LB, 'config/plugins/raumklima/geheim.json')

# Vor jedem Lauf die Bank leerraeumen - UND ZWAR AUCH DIE ZWEITSCHRIFT.
# Wird nur config/plugins/raumklima/raumklima.json geloescht, holt
# rk_config() die Konfiguration aus config/plugins/raumklima.backup.json
# zurueck, und der Pruefstand sieht schon beim ersten GET zwoelf fertig
# eingerichtete Raeume. Das sah am 29.08.2026 nach einem schweren Fehler aus
# ("die Seite schreibt beim blossen Aufrufen") und war die dokumentierte
# Selbstheilung. Ein schmutziger Pruefstand erfindet Befunde.
import shutil
for d in ('config/plugins/raumklima', 'data/plugins/raumklima',
          'log/plugins/raumklima'):
    shutil.rmtree(os.path.join(LB, d), ignore_errors=True)
    os.makedirs(os.path.join(LB, d), exist_ok=True)
for f in ('config/plugins/raumklima.backup.json',):
    try:
        os.remove(os.path.join(LB, f))
    except OSError:
        pass

befunde = []


def melde(bez, gut, text=''):
    print('  [%s] %-52s %s' % ('ok ' if gut else 'ROT', bez, text))
    if not gut:
        befunde.append(bez)


umg = dict(os.environ)
umg.update({'LBHOMEDIR': LB, 'LBLANG': 'de', 'LBPPLUGINDIR': 'raumklima',
            'LBPCONFIGDIR': os.path.join(LB, 'config/plugins/raumklima'),
            'LBPLOGDIR': os.path.join(LB, 'log/plugins/raumklima'),
            'LBPDATADIR': os.path.join(LB, 'data/plugins/raumklima'),
            'LBPHTMLAUTHDIR': HTML,
            'LBPHTMLDIR': os.path.join(P, 'webfrontend', 'html'),
            'LBPTEMPLATEDIR': os.path.join(P, 'templates'),
            'LBPBINDIR': os.path.join(P, 'bin')})

# NICHT im Scratchpad: dessen Pfad enthaelt einen 8.3-Kurznamen (Form ABCDEF~1), und
# PHP schneidet einen -d-Wert an der Tilde ab ("Failed opening required
# 'C:/Users/CHRIST'"). Am 29.08.2026 gemessen.
VORLAUF = 'C:/tmp/rk_vorlauf.php'
server = subprocess.Popen(
    [os.path.join(PHPDIR, 'php.exe'), '-S', '127.0.0.1:%d' % PORT, '-t', HTML,
     '-d', 'include_path=.;' + os.path.join(LB, 'libs', 'phplib'),
     '-d', 'display_errors=0', '-d', 'error_reporting=32767',
     '-d', 'date.timezone=Europe/Berlin',
     '-d', 'extension_dir=' + os.path.join(PHPDIR, 'ext'),
     '-d', 'extension=curl', '-d', 'extension=openssl', '-d', 'extension=mbstring',
     '-d', 'extension=sockets', '-d', 'extension=fileinfo',
     '-d', 'auto_prepend_file=' + VORLAUF],
    env=umg, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=HTML)

oeffner = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def hole(daten=None):
    d = urllib.parse.urlencode(daten).encode() if daten else None
    try:
        with oeffner.open('http://127.0.0.1:%d/index.php' % PORT, d, timeout=60) as a:
            return a.status, a.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace')


def raeume_der_cfg():
    if not os.path.isfile(CFG):
        return []
    d = json.load(io.open(CFG, encoding='utf-8'))
    return [x for x in d.get('raeume', []) if str(x.get('name', '')).strip() != '']


try:
    code, seite = 0, ''
    for _ in range(40):
        try:
            code, seite = hole()
            if code:
                break
        except Exception:
            time.sleep(0.25)
    if not code:
        print('Server kam nicht hoch')
        print(server.stdout.read(2000).decode('utf-8', 'replace'))
        sys.exit(2)

    print('== 1. Die Seite ohne Zutun ==')
    melde('HTTP 200', code == 200, str(code))
    melde('Assistentenabschnitt ist da', 'Einrichtung' in seite)
    m = re.search(r'name="formtoken" value="([^"]+)"', seite)
    melde('Formularmerkmal in der Seite', m is not None,
          (m.group(1)[:12] + '...') if m else '-')
    if not m:
        sys.exit(1)
    ft = m.group(1)
    melde('kein Leersatz - die Bank kennt einen Miniserver',
          'kennt keinen Miniserver' not in seite)
    melde('Uebernahmeknopf steht noch NICHT da',
          'name="ms_uebernehmen"' not in seite)
    melde('Konfiguration noch ohne Raeume', len(raeume_der_cfg()) == 0,
          '%d' % len(raeume_der_cfg()))

    print('== 2. Knopf "Raeume vom Miniserver holen" ==')
    code, seite = hole({'formtoken': ft, 'activetab': 'tab-settings', 'ms_suchen': '1'})
    melde('HTTP 200', code == 200, str(code))
    melde('kein PHP-Fehler in der Antwort',
          'Fatal error' not in seite and 'Warning:' not in seite)
    melde('meldet die Raeume des Miniservers', '13 R' in seite)
    # ELF, nicht zwoelf - und das ist die Behebung, nicht ein Fehler.
    # EG Kueche hat ohne Kategoriefilter ZWEI Temperaturbewerber (den
    # Fuehler und den Raumregler in Kategorie c2). Bis 0.11.1 nahm der
    # Assistent stillschweigend den ersten und schrieb trotzdem "wird
    # angelegt"; an der echten Anlage waere das im KG Technikraum die
    # Gehaeusetemperatur eines Relaismoduls gewesen. Seit 0.11.2 wird ein
    # mehrdeutiger Raum uebersprungen und GENANNT.
    melde('elf Raeume werden angelegt, EG Kueche ist mehrdeutig',
          seite.count('wird angelegt') == 11,
          '%d mal "wird angelegt"' % seite.count('wird angelegt'))
    melde('die Mehrdeutigkeit steht in der Tabelle',
          'Kategorie eingrenzen' in seite or 'narrow the category' in seite)
    melde('und die Zahl steht als Warnung darueber',
          '1 Raum/R' in seite or '1 room(s)' in seite)
    melde('Probe Temperatur abgelesen', 'Probe Temperatur' in seite)
    melde('Probe Feuchte EIGENS abgelesen', 'Probe Feuchte' in seite)
    melde('nicht vom Temperaturbaustein abgeschrieben',
          'abgeschrieben' in seite)
    melde('Pfad LL.value in der Seite', 'LL.value' in seite)
    melde('Uebernahmeknopf steht jetzt da', 'name="ms_uebernehmen"' in seite)
    melde('Knopf 1 hat NICHTS geschrieben', len(raeume_der_cfg()) == 0,
          '%d Raeume' % len(raeume_der_cfg()))

    print('== 3. Knopf "Vorschlag uebernehmen" ==')
    code, seite = hole({'formtoken': ft, 'activetab': 'tab-settings',
                        'ms_uebernehmen': '1', 'ms_kategorie': ''})
    melde('HTTP 200', code == 200, str(code))
    melde('kein PHP-Fehler', 'Fatal error' not in seite and 'Warning:' not in seite)
    r = raeume_der_cfg()
    melde('elf Raeume in der Konfiguration', len(r) == 11, '%d' % len(r))
    e = [x for x in r if x.get('name') == 'OG Schlafzimmer Eltern']
    melde('der Raum mit der abweichend benannten Kachel ist dabei', len(e) == 1)
    if e:
        e = e[0]
        melde('Adresse zeigt auf den Miniserver der Bank',
              MS_WIRT in str(e.get('quelle', '')), str(e.get('quelle', ''))[:70])
        melde('und traegt das Schema aus der general.json',
              str(e.get('quelle', '')).startswith(MS_SCHEMA + '://'),
              str(e.get('quelle', ''))[:24])
        melde('Pfad Temperatur gesetzt', e.get('pfad_t', '') == 'LL.value',
              str(e.get('pfad_t')))
        melde('Pfad Feuchte gesetzt', e.get('pfad_rf', '') == 'LL.value',
              str(e.get('pfad_rf')))
        melde('eigene Adresse fuer die Feuchte',
              str(e.get('quelle_rf', '')).strip() != ''
              and e.get('quelle_rf') != e.get('quelle'),
              str(e.get('quelle_rf', ''))[:70])
    # Die Zugangsdaten stehen NICHT in raumklima.json, sondern in
    # geheim.json - dort holt rk_holen() sie ab. Am 29.08.2026 nachgesehen.
    g = json.load(io.open(GEH, encoding='utf-8')) if os.path.isfile(GEH) else {}
    melde('Zugangsdaten in geheim.json uebernommen',
          str(g.get('benutzer', '')) == 'admin'
          and str(g.get('passwort', '')) == 'geheim123',
          'benutzer=%s' % g.get('benutzer', '-'))
    melde('die Zugangsdaten stehen NICHT in raumklima.json',
          'geheim123' not in io.open(CFG, encoding='utf-8').read())

    def bank_setzen(raeume=None):
        """Die Raumtabelle von Hand setzen - VOR jedem Abschnitt.

        Bis zum 30.08.2026 bauten die Abschnitte aufeinander auf, und weil
        nach der ersten Uebernahme kein Platz mehr frei war, kamen die
        Waechter der Abschnitte 5 und 6 gar nicht mehr an ihre Stelle. Sie
        blieben gruen, ohne sie je zu betreten: die Eichung konnte den
        FORMULARWAECHTER ausschalten, und Abschnitt 5 meldete weiter "ok" -
        nicht weil kein Vorschlag entstand, sondern weil ohnehin keiner
        mehr entstehen konnte.

        Das ist dieselbe Falle, die Abschnitt 7 ausdruecklich umgeht. Jetzt
        setzt jeder Abschnitt seine Vorbedingung selbst.
        """
        d = json.load(io.open(CFG, encoding='utf-8'))
        for x in d['raeume']:
            for k in ('name', 'quelle', 'quelle_rf', 'pfad_t', 'pfad_rf',
                      'pfad_co2', 'pfad_fenster', 'pfad_zuluft'):
                x[k] = ''
        for i, felder in enumerate(raeume or []):
            d['raeume'][i].update(felder)
        io.open(CFG, 'w', encoding='utf-8').write(
            json.dumps(d, ensure_ascii=False, indent=1))

    print('== 4. Derselbe Knopf ein zweites Mal - nichts darf sich aendern ==')
    vorher = io.open(CFG, encoding='utf-8').read()
    code, seite = hole({'formtoken': ft, 'activetab': 'tab-settings',
                        'ms_uebernehmen': '1', 'ms_kategorie': ''})
    nachher = io.open(CFG, encoding='utf-8').read()
    melde('HTTP 200', code == 200, str(code))
    melde('Konfiguration Zeichen fuer Zeichen gleich', vorher == nachher)
    melde('die Seite sagt, dass nichts neu war',
          'nichts eingetragen' in seite or 'Nothing was entered' in seite)

    print('== 5. GEGENFALL: ohne Formularmerkmal ==')
    # Erst leerraeumen: auf einer vollen Tabelle entstuende auch MIT
    # gueltigem Merkmal kein Vorschlag, und die Zeile maesse nichts.
    bank_setzen()
    code, seite = hole({'activetab': 'tab-settings', 'ms_suchen': '1'})
    melde('kein Vorschlag ohne Merkmal',
          'name="ms_uebernehmen"' not in seite
          and seite.count('wird angelegt') == 0, 'HTTP %s' % code)

    print('== 6. GEGENFALL: eine belegte Zeile wird nicht ueberschrieben ==')
    # Leere Tabelle, nur Platz 0 belegt - damit die Uebernahme wirklich
    # etwas zu tun hat und den belegten Platz UEBERGEHEN muss.
    bank_setzen([{'pfad_t': 'HAND.ANGELEGT'}])
    code, seite = hole({'formtoken': ft, 'activetab': 'tab-settings',
                        'ms_uebernehmen': '1', 'ms_kategorie': ''})
    d2 = json.load(io.open(CFG, encoding='utf-8'))
    melde('der von Hand gesetzte Pfad steht noch',
          d2['raeume'][0].get('pfad_t') == 'HAND.ANGELEGT',
          str(d2['raeume'][0].get('pfad_t')))
    melde('und Platz 0 blieb ohne Namen',
          str(d2['raeume'][0].get('name', '')) == '',
          repr(d2['raeume'][0].get('name')))
    # Gegenprobe: es wurde ueberhaupt etwas eingetragen. Ohne sie waere die
    # Zeile darueber auch dann gruen, wenn die Uebernahme gar nicht lief.
    melde('und die uebrigen Plaetze wurden gefuellt',
          len(raeume_der_cfg()) >= 10, '%d Raeume' % len(raeume_der_cfg()))
    print('== 7. Ein Raum steht schon, ein Platz ist SCHEINBAR frei ==')
    # Warum eigens: das Plugin hat zwoelf Plaetze und die Anlage zwoelf
    # Raeume. Nach der ersten Uebernahme ist kein Platz mehr frei - damit
    # sind die beiden Waechter "Raum steht schon" und "Zeile ist belegt"
    # gar nicht erreichbar. Am 29.08.2026 blieben genau diese zwei
    # Eichungen gruen; nicht weil der Code richtig war, sondern weil der
    # Pruefstand die Stelle nie betrat.
    #
    # Also von vorn, und die Tabelle vorbereiten:
    #   Platz 0: Raum 'Dachboden' von Hand - den gibt es am Miniserver
    #            auch, er darf KEIN zweites Mal angelegt werden. Der Name
    #            ist mit Bedacht der ALPHABETISCH ERSTE: der Assistent geht
    #            die Raeume sortiert durch und hat nach zehn freien Plaetzen
    #            keinen mehr. Stuende hier der letzte Name (OG Wannenbad),
    #            kaeme er ohnehin nie an die Reihe, und die Zeile waere
    #            gruen, ohne den Waechter je zu beruehren - am 29.08.2026
    #            genau so gemessen.
    #   Platz 1: ohne Namen, aber mit einem Pfad - sieht leer aus, ist es
    #            aber nicht und darf nicht ueberschrieben werden.
    # Bleiben zehn wirklich freie Plaetze fuer elf uebrige Raeume.
    d = json.load(io.open(CFG, encoding='utf-8'))
    for x in d['raeume']:
        for k in ('name', 'quelle', 'quelle_rf', 'pfad_t', 'pfad_rf'):
            x[k] = ''
    d['raeume'][0]['name'] = 'Dachboden'
    d['raeume'][1]['pfad_t'] = 'VON.HAND'
    io.open(CFG, 'w', encoding='utf-8').write(
        json.dumps(d, ensure_ascii=False, indent=1))
    code, seite = hole({'formtoken': ft, 'activetab': 'tab-settings',
                        'ms_uebernehmen': '1', 'ms_kategorie': ''})
    melde('HTTP 200', code == 200, str(code))
    d2 = json.load(io.open(CFG, encoding='utf-8'))
    namen = [x.get('name', '') for x in d2['raeume']]
    melde('der von Hand angelegte Raum steht noch auf Platz 0',
          namen[0] == 'Dachboden', namen[0])
    melde('Platz 0 blieb unberuehrt (keine Adresse eingetragen)',
          str(d2['raeume'][0].get('quelle', '')) == '',
          str(d2['raeume'][0].get('quelle', ''))[:40])
    melde('die scheinbar leere Zeile blieb frei',
          d2['raeume'][1].get('pfad_t') == 'VON.HAND'
          and str(d2['raeume'][1].get('name', '')) == '',
          'pfad_t=%s name=%r' % (d2['raeume'][1].get('pfad_t'),
                                 d2['raeume'][1].get('name')))
    melde('Dachboden steht genau EINMAL in der Tabelle',
          namen.count('Dachboden') == 1, '%d mal' % namen.count('Dachboden'))
    besetzt = [x for x in d2['raeume'] if str(x.get('name', '')).strip() != '']
    melde('elf Raeume belegt: der eigene plus zehn neue',
          len(besetzt) == 11, '%d' % len(besetzt))
    melde('die Seite nennt die Zahl der uebernommenen Raeume',
          '10 Raum' in seite or '10 room' in seite)

    print('== 8. MIT Kategoriefilter: die Mehrdeutigkeit verschwindet ==')
    bank_setzen()
    code, seite = hole({'formtoken': ft, 'activetab': 'tab-settings',
                        'ms_suchen': '1', 'ms_kategorie': 'Feuchte'})
    melde('HTTP 200', code == 200, str(code))
    melde('jetzt zwoelf mal "wird angelegt"',
          seite.count('wird angelegt') == 12,
          '%d mal' % seite.count('wird angelegt'))
    melde('keine Mehrdeutigkeit mehr',
          'Kategorie eingrenzen' not in seite and 'narrow the category' not in seite)
    code, seite = hole({'formtoken': ft, 'activetab': 'tab-settings',
                        'ms_uebernehmen': '1', 'ms_kategorie': 'Feuchte'})
    r8 = raeume_der_cfg()
    melde('zwoelf Raeume uebernommen', len(r8) == 12, '%d' % len(r8))
    melde('der Filter wird in den zweiten Schritt mitgenommen',
          'EG K' in ' '.join(x.get('name', '') for x in r8))

    print('== 9. Der zweite Druck sagt, dass nichts neu war ==')
    # Eigener Abschnitt, weil $rk_voll jetzt LEER sein kann (alle Raeume
    # stehen schon). Der erste Entwurf von 0.11.2 behandelte nur den
    # Erfolgsfall - der Anwender bekam gar keine Antwort mehr.
    vorher = io.open(CFG, encoding='utf-8').read()
    code, seite = hole({'formtoken': ft, 'activetab': 'tab-settings',
                        'ms_uebernehmen': '1', 'ms_kategorie': 'Feuchte'})
    nachher = io.open(CFG, encoding='utf-8').read()
    melde('Konfiguration Zeichen fuer Zeichen gleich', vorher == nachher)
    melde('und die Seite sagt es auch',
          'nichts eingetragen' in seite or 'Nothing was entered' in seite)

    print('== 10. Ein Platz mit ADRESSE, aber ohne Namen, ist NICHT frei ==')
    # Bis 0.11.1 sah der Freiheitstest nur auf name/pfad_t/pfad_rf. Eine von
    # Hand eingetragene Shelly-Adresse wurde ueberschrieben.
    bank_setzen([{'quelle': 'http://192.168.1.66/rpc/Shelly.GetStatus'}])
    code, seite = hole({'formtoken': ft, 'activetab': 'tab-settings',
                        'ms_uebernehmen': '1', 'ms_kategorie': 'Feuchte'})
    d10 = json.load(io.open(CFG, encoding='utf-8'))
    melde('die von Hand eingetragene Adresse steht noch',
          d10['raeume'][0].get('quelle') == 'http://192.168.1.66/rpc/Shelly.GetStatus',
          str(d10['raeume'][0].get('quelle'))[:50])
    melde('Platz 0 hat weiterhin keinen Namen',
          str(d10['raeume'][0].get('name', '')) == '',
          repr(d10['raeume'][0].get('name')))

    print('== 11. Mehr Raeume als Plaetze - der Ueberhang wird GENANNT ==')
    # Nur messbar gegen die grosse Attrappe (MS_PORT_GROSS). Ohne sie hat
    # die Anlage genau zwoelf vollstaendige Raeume fuer zwoelf Plaetze, und
    # der Ueberlauf ist strukturell unsichtbar.
    gross = os.environ.get('MS_PORT_GROSS', '')
    if not gross:
        print('  [-- ] MS_PORT_GROSS nicht gesetzt - der Ueberlauf wurde NICHT gemessen')
    else:
        gen = json.load(io.open(os.path.join(LB, 'config/system/general.json'),
                                encoding='utf-8'))
        gen['Miniserver']['1']['Port'] = gross
        gen['Miniserver']['1']['Porthttps'] = gross
        io.open(os.path.join(LB, 'config/system/general.json'), 'w',
                encoding='utf-8').write(json.dumps(gen, ensure_ascii=False))
        bank_setzen()
        code, seite = hole({'formtoken': ft, 'activetab': 'tab-settings',
                            'ms_suchen': '1', 'ms_kategorie': 'Feuchte'})
        melde('HTTP 200', code == 200, str(code))
        melde('die Vorschau zeigt "kein Platz mehr frei"',
              'kein Platz mehr' in seite or 'no free row' in seite)
        melde('und nennt die Zahl als Warnung',
              'passen nicht mehr hinein' in seite or 'no longer fit' in seite)
        angelegt = seite.count('wird angelegt')
        melde('hoechstens zwoelf stehen auf "wird angelegt"', angelegt <= 12,
              '%d' % angelegt)
        code, seite = hole({'formtoken': ft, 'activetab': 'tab-settings',
                            'ms_uebernehmen': '1', 'ms_kategorie': 'Feuchte'})
        r11 = raeume_der_cfg()
        melde('genau zwoelf uebernommen', len(r11) == 12, '%d' % len(r11))
        melde('die Meldung nennt den Ueberhang',
              'passen nicht mehr hinein' in seite or 'no longer fit' in seite)
        melde('Raumname mit Randleerzeichen wurde GETRIMMT gespeichert',
              all(x.get('name') == str(x.get('name')).strip() for x in r11))
        namen = [x.get('name') for x in r11]
        melde('kein Raum steht doppelt', len(namen) == len(set(namen)),
              '%d Namen, %d verschieden' % (len(namen), len(set(namen))))
        # Keller Nord traegt einen Feuchtebaustein der Bauart ShellyHT mit
        # einem ANDEREN Umschlag. Bis 0.11.1 wurde sein Pfad vom
        # Temperaturbaustein abgeschrieben und war damit falsch - der Raum
        # haette nie einen Feuchtewert bekommen.
        kn = [x for x in r11 if x.get('name') == 'Keller Nord']
        melde('Keller Nord ist dabei', len(kn) == 1)
        if kn:
            melde('sein Feuchtepfad ist EIGENS gemessen',
                  kn[0].get('pfad_rf') == 'daten.zustand.aktuell',
                  str(kn[0].get('pfad_rf')))
            melde('und weicht vom Temperaturpfad ab',
                  kn[0].get('pfad_rf') != kn[0].get('pfad_t'),
                  '%s / %s' % (kn[0].get('pfad_t'), kn[0].get('pfad_rf')))

    print('== 12. Preferhttps wird gelesen ==')
    # rk_miniserver() las bis 0.11.1 nur `Port` und rk_ms_url() baute fest
    # http://. Ein LoxBerry mit Preferhttps=1 redete damit Klartext gegen
    # einen Port, der TLS erwartet - und der Assistent meldete "antwortet
    # nicht". Gemessen wird hier nur, dass das SCHEMA umschaltet; ein
    # TLS-Server gehoert nicht in diese Probe.
    gen = json.load(io.open(os.path.join(LB, 'config/system/general.json'),
                            encoding='utf-8'))
    gen['Miniserver']['1']['Preferhttps'] = '1'
    gen['Miniserver']['1']['Porthttps'] = '24999'
    io.open(os.path.join(LB, 'config/system/general.json'), 'w',
            encoding='utf-8').write(json.dumps(gen, ensure_ascii=False))
    bank_setzen()
    code, seite = hole({'formtoken': ft, 'activetab': 'tab-settings',
                        'ms_suchen': '1', 'ms_kategorie': 'Feuchte'})
    melde('mit Preferhttps=1 wird der TLS-Port angesprochen',
          '24999' in seite, 'Port 24999 in der Meldung' if '24999' in seite else '-')
    melde('und der Abruf schlaegt fehl statt still http zu reden',
          'wird angelegt' not in seite)

finally:
    server.terminate()
    try:
        server.wait(timeout=5)
    except Exception:
        server.kill()

print('\n== %d Befund(e) ==' % len(befunde))
sys.exit(1 if befunde else 0)
