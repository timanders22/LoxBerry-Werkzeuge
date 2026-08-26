#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Traegt der MQTT-Weg dieselben Werte wie der HTTP-Weg?

Gemessen wird nicht der Rueckgabewert, sondern was wirklich als UDP-Meldung
beim MQTT-Gateway ankaeme: das Werkzeug traegt einen eigenen Port in die
general.json der Attrappe ein und horcht darauf.

Fuenf Schritte je Linie:

  1. Cron meldet die vier Merker ann, audio, push, ptest.
  2. Cron ohne Aenderung meldet gar nichts (Signatur greift).
  3. Ein gesetzter ptest loest eine Meldung aus - er steht also in der
     Signatur. Fehlt er dort, laege er bis zum halbstuendlichen
     Lebenszeichen, sein Fenster ist aber nur fuenf Minuten breit.
  4. ?ptest=1 meldet sofort, nicht erst beim naechsten Cron-Lauf.
  5. Die Werte aus HTTP-Zeile und MQTT-Meldung stimmen ueberein.
  6. Ohne Token loest ?ptest=1 nichts aus - kein Merker, keine Meldung.
  7. ?selftest=1 beantwortet die Tokenfrage, ohne etwas auszuloesen.

Aufruf:  python mqtt_vollstaendig_pruefen.py [Kuerzel ...]
         ohne Argumente werden alle bekannten Linien geprueft.

Hintergrund: REGELN_2, Abschnitt "Der MQTT-Weg traegt dieselben Werte wie
der HTTP-Weg" (Beschluss 16.08.2026).
"""
import io, json, os, re, shutil, socket, subprocess, sys, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HIER = Path(__file__).resolve().parent
B = HIER.parent
PHP = r'C:\tmp\php-8.4.24-Win32-vs17-x64\php.exe'
PORT = 15987
LB = HIER / 'lb_mqtt'
VORLAUF_TEST = HIER / 'vorlauf_mqtt.php'

# Kuerzel -> (Ordnerpraefix, Konfigdatei, Cron, Endpunkt, Standardthema,
#             tmp-Name, Geraeteliste in der Konfiguration)
LINIEN = {
    'robonect':  ('LoxBerry-Plugin-Robonect', 'mower.json',
                  'webfrontend/html/cron.php', 'webfrontend/html/mower.php',
                  'maeher', 'robonect',
                  ('mowers', {'name': 'Pruefmaeher', 'ip': '127.0.0.1', 'user': '', 'pass': ''})),
    'saugrobo':  ('LoxBerry-Plugin-Saugroboter', 'robo.json',
                  'bin/cron.php', 'webfrontend/html/robo.php',
                  'saugrobo', 'saugrobo',
                  ('robots', {'name': 'Pruefsauger', 'ip': '127.0.0.1', 'port': 1})),
    'awmabfuhr': ('LoxBerry-Plugin-AWM-Abfuhr', 'awm.json',
                  'webfrontend/html/cron.php', 'webfrontend/html/awm.php',
                  'awm', 'awmabfuhr',
                  ('cals', {'name': 'Pruefkalender', 'url': 'http://127.0.0.1:1/pruef.ics'})),
    'ferien':    ('LoxBerry-Plugin-FerienFeiertage', 'ferien.json',
                  'bin/cron.php', 'webfrontend/html/ferien.php',
                  'ferien', 'ferien', None),
}

FLAGS = ('ann', 'audio', 'push', 'ptest')

# MarstekVenus hat kein Meldefenster und keine Freigaben - dort ist die Frage
# eine andere: die kWh-Zaehler (?energy) und die Spotpreis-Raenge (?ranks)
# gab es ueber HTTP seit jeher, ueber MQTT gar nicht. Geprueft wird deshalb
# gegen diese Themenliste.
MARSTEK_ENERGIE = ['energie_' + k for k in
                   ('ok', 'chgt', 'dist', 'chgd', 'disd', 'chgm', 'dism', 'cyc', 'eff')]
MARSTEK_RAENGE = ['rang_' + k for k in ('ok', 'n', 'rank', 'rankd', 'curp', 'neg')]


def neuester_ordner(praefix):
    """Der Ordner mit der hoechsten Version - Ordnernamen tragen sie im Namen."""
    def schluessel(p):
        m = re.search(r'-(\d+)\.(\d+)\.(\d+)$', p.name)
        return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)
    kandidaten = [p for p in B.iterdir()
                  if p.is_dir() and p.name.startswith(praefix + '-')
                  and (p / 'plugin.cfg').is_file()]
    return max(kandidaten, key=schluessel) if kandidaten else None


def vorlauf_schreiben():
    VORLAUF_TEST.write_text(
        "<?php\n"
        "/* Wie vorlauf.php, zusaetzlich wird die Abfragezeichenkette aus der\n"
        " * Umgebungsvariablen TEST_QUERY nach $_GET uebernommen - PHP im\n"
        " * Kommandozeilenbetrieb tut das von sich aus nicht. */\n"
        "require_once getenv('TEST_VORLAUF');\n"
        "$tq = (string) getenv('TEST_QUERY');\n"
        "if ($tq !== '') {\n"
        "    parse_str($tq, $_GET);\n"
        "    $_SERVER['QUERY_STRING'] = $tq;\n"
        "}\n", encoding='utf-8')


def lb_aufbauen():
    if LB.exists():
        shutil.rmtree(LB, ignore_errors=True)
    shutil.copytree(HIER / 'lb', LB)
    gj = json.loads((LB / 'config/system/general.json').read_text(encoding='utf-8'))
    gj['Mqtt'] = {'Udpinport': str(PORT), 'Gatewayautostart': '1',
                  'Brokerhost': '127.0.0.1', 'Brokerport': '1883'}
    (LB / 'config/system/general.json').write_text(json.dumps(gj, ensure_ascii=False),
                                                   encoding='utf-8')


def cfg_schreiben(pd, datei, thema, geraet):
    d = LB / 'config/plugins' / pd
    d.mkdir(parents=True, exist_ok=True)
    cfg = {}
    if (d / datei).is_file():
        try:
            cfg = json.loads((d / datei).read_text(encoding='utf-8'))
        except Exception:
            cfg = {}
    cfg.update({'mqtt_enabled': 1, 'mqtt_topic': thema})
    # Ohne konfiguriertes Geraet laeuft die Schleife im Cron gar nicht erst.
    # 127.0.0.1 auf einem toten Port: die Verbindung wird sofort abgelehnt,
    # der Test wartet also nicht in einen Zeitablauf hinein.
    if geraet:
        cfg[geraet[0]] = [geraet[1]]
    cfg.setdefault('notify', {})
    cfg['notify']['audio'] = 1     # AUDIO muss 1 werden
    cfg['notify']['push'] = 0      # PUSH muss 0 bleiben - sonst sagt der Test nichts
    # Setzen, nicht vorschlagen: in der Attrappe kann aus einem frueheren
    # Werkzeuglauf ein erzeugtes Token liegen. Mit setdefault() bliebe es
    # stehen, und ?ptest=1 antwortete bei den tokenpflichtigen Linien mit
    # ERR=TOKEN - was wie ein Plugin-Fehler aussaehe und keiner waere.
    cfg['aktionstoken'] = 'PRUEFTOKEN'
    (d / datei).write_text(json.dumps(cfg, ensure_ascii=False), encoding='utf-8')


def lauf(datei, pd, ordner, query=''):
    umg = dict(os.environ)
    umg['LBHOMEDIR'] = str(LB)
    umg['LBPPLUGINDIR'] = pd
    umg['LBPCONFIGDIR'] = str(LB / 'config/plugins' / pd)
    umg['LBPLOGDIR'] = str(LB / 'log/plugins' / pd)
    umg['LBPDATADIR'] = str(LB / 'data/plugins' / pd)
    umg['LBPHTMLDIR'] = str((ordner / 'webfrontend/html').resolve())
    umg['LBPHTMLAUTHDIR'] = str((ordner / 'webfrontend/htmlauth').resolve())
    umg['LBPTEMPLATEDIR'] = str((ordner / 'templates').resolve())
    umg['LBPBINDIR'] = str((ordner / 'bin').resolve())
    umg['TEST_VORLAUF'] = str(HIER / 'vorlauf.php')
    umg['TEST_QUERY'] = query
    for k in ('LBPCONFIGDIR', 'LBPLOGDIR', 'LBPDATADIR'):
        Path(umg[k]).mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [PHP, '-n', '-d', 'include_path=.;' + str(LB / 'libs' / 'phplib'),
         '-d', 'auto_prepend_file=' + str(VORLAUF_TEST),
         '-d', 'display_errors=0', '-d', 'error_reporting=32767',
         '-d', 'date.timezone=Europe/Berlin',
         '-d', 'extension_dir=' + str(Path(PHP).parent / 'ext'),
         '-d', 'extension=curl', '-d', 'extension=openssl', '-d', 'extension=mbstring',
         '-d', 'extension=sockets', '-d', 'extension=fileinfo',
         str(datei.resolve())],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        cwd=str(datei.parent.resolve()), env=umg, timeout=120)
    befunde = []
    if '###BEFUNDE###' in r.stderr:
        befunde = [z for z in r.stderr.split('###BEFUNDE###', 1)[1].strip().splitlines() if z.strip()]
    # Der Pruefling fragt ein Geraet auf 127.0.0.1 ab, das es nicht gibt. Im
    # Plugin steht davor ein @, der Fehler ist also unterdrueckt - nur der
    # eigene Fehler-Aufnehmer des Pruefstands sieht ihn trotzdem, weil
    # set_error_handler auch bei @ gerufen wird. Kein Befund, sondern Aufbau.
    befunde = [b for b in befunde if not ('file_get_contents' in b and '127.0.0.1' in b)]
    return r.stdout, befunde


def ernten(sock):
    aus = {}
    sock.settimeout(0.25)
    while True:
        try:
            d, _ = sock.recvfrom(4096)
        except socket.timeout:
            break
        m = re.match(r'^publish\s+(\S+)\s*(.*)$', d.decode('utf-8', 'replace').strip())
        if m:
            aus[m.group(1)] = m.group(2)
    return aus


def pruefe(kuerzel, sock):
    praefix, cfgdatei, cron, endpunkt, thema, tmpname, geraet = LINIEN[kuerzel]
    ordner = neuester_ordner(praefix)
    if ordner is None:
        print('  kein Ordner %s-* gefunden' % praefix)
        return ['%s: Ordner fehlt' % kuerzel]
    print('  %s' % ordner.name)
    befunde = []
    cfg_schreiben(kuerzel, cfgdatei, thema, geraet)
    tmp = Path('C:/tmp') / tmpname
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / 'ptest').unlink(missing_ok=True)
    for f in list(tmp.glob('mqtt_sig*')) + list(tmp.glob('mqtt_beat*')):
        f.unlink(missing_ok=True)
    ernten(sock)

    out, bef = lauf(ordner / cron, kuerzel, ordner)
    n1 = ernten(sock)
    fehlt = [f for f in FLAGS if not any(k.endswith('/' + f) for k in n1)]
    print('  1. Cron:              %3d Themen, Merker: %s'
          % (len(n1), 'alle vier' if not fehlt else 'ES FEHLEN ' + ', '.join(fehlt)))
    if fehlt:
        befunde.append('%s: Merker fehlen in der MQTT-Meldung (%s)' % (kuerzel, ', '.join(fehlt)))
    if bef:
        print('     BEFUNDE: %s' % '; '.join(bef[:3]))
        befunde.append('%s: PHP-Befunde im Cron' % kuerzel)

    lauf(ordner / cron, kuerzel, ordner)
    n2 = ernten(sock)
    # Das LEBENSZEICHEN ist ausgenommen, und zwar mit Absicht.
    #
    # Der Hausstandard verlangt seit dem 26.08.2026, dass <praefix>/status/ok,
    # /ts und /zaehler bei JEDEM Durchgang hinausgehen - auch unveraendert.
    # Sonst faellt bei einem Geraet, das sich tagelang nicht ruehrt, genau das
    # Zeichen aus, das sagen soll, dass das Plugin noch lebt.
    #
    # Bis dahin lautete die Erwartung hier "0 Themen". Robonect 1.1.0 und
    # Saugroboter 1.1.0 wurden dadurch beanstandet, weil sie die Regel
    # BEFOLGEN. Eine Pruefzeile, die das Richtige rot meldet, wird
    # abgeschaltet - deshalb wird sie hier berichtigt statt entfernt.
    lebens = {k for k in n2 if k.rsplit('/', 2)[-2:-1] == ['status']
              and k.rsplit('/', 1)[-1] in ('ok', 'ts', 'zaehler', 'listener')}
    rest2 = {k: v for k, v in n2.items() if k not in lebens}
    print('  2. Cron unveraendert: %3d Themen, davon Lebenszeichen %d '
          '(erwartet: nur Lebenszeichen)' % (len(n2), len(lebens)))
    if rest2:
        print('     WIEDERHOLT: %s' % ', '.join(sorted(rest2)[:6]))
        befunde.append('%s: Cron sendet trotz unveraenderter Signatur' % kuerzel)

    (tmp / 'ptest').write_text('1')
    lauf(ordner / cron, kuerzel, ordner)
    n3 = ernten(sock)
    pt = [v for k, v in n3.items() if k.endswith('/ptest')]
    print('  3. ptest gesetzt:     %3d Themen, ptest=%s' % (len(n3), pt or 'NICHT GEMELDET'))
    if not n3 or '1' not in pt:
        befunde.append('%s: gesetzter ptest loest keine MQTT-Meldung aus '
                       '(steht er in der Signatur?)' % kuerzel)

    (tmp / 'ptest').unlink(missing_ok=True)
    ernten(sock)
    out, bef = lauf(ordner / endpunkt, kuerzel, ordner, 'ptest=1&token=PRUEFTOKEN')
    n4 = ernten(sock)
    pt4 = [v for k, v in n4.items() if k.endswith('/ptest')]
    print('  4. ?ptest=1:          %3d Themen, ptest=%s   Antwort: %s'
          % (len(n4), pt4 or 'NICHT GEMELDET',
             out.strip().splitlines()[0] if out.strip() else '(leer)'))
    if '1' not in pt4:
        befunde.append('%s: ?ptest=1 meldet nicht sofort per MQTT' % kuerzel)
    if bef:
        print('     BEFUNDE: %s' % '; '.join(bef[:3]))
        befunde.append('%s: PHP-Befunde beim Endpunkt' % kuerzel)

    # Sauberer Ausgangspunkt: ptest weg, Signatur weg - dann meldet der Cron
    # in jedem Fall, und beide Wege beschreiben denselben Augenblick.
    (tmp / 'ptest').unlink(missing_ok=True)
    for f in list(tmp.glob('mqtt_sig*')) + list(tmp.glob('mqtt_beat*')):
        f.unlink(missing_ok=True)
    ernten(sock)
    out, bef = lauf(ordner / endpunkt, kuerzel, ordner)
    zeile = next((z for z in out.splitlines() if ';ANN=' in z), '')
    http = dict(re.findall(r'([A-Z]+)=([^;\s]*)', zeile))
    lauf(ordner / cron, kuerzel, ordner)
    mq = {k.rsplit('/', 1)[-1]: v for k, v in ernten(sock).items()
          if k.rsplit('/', 1)[-1] in FLAGS}
    abw = [f for f in FLAGS if f.upper() in http and f in mq and http[f.upper()] != mq[f]]
    print('  5. HTTP gegen MQTT:   HTTP %s | MQTT %s -> %s'
          % ({f.upper(): http.get(f.upper(), '-') for f in FLAGS},
             {f: mq.get(f, '-') for f in FLAGS},
             'gleich' if mq and not abw else ('ABWEICHUNG ' + ', '.join(abw) if abw else 'MQTT leer')))
    if abw:
        befunde.append('%s: HTTP und MQTT weichen ab (%s)' % (kuerzel, ', '.join(abw)))
    if not mq:
        befunde.append('%s: keine Merker im Vergleichsschritt gemeldet' % kuerzel)

    # 6. Die Tokenpflicht muss auch greifen. Ein Endpunkt, der ohne Token
    #    ausloest, ist schlimmer als einer ohne Tokenpflicht: er sieht
    #    geschuetzt aus. Geprueft wird der Effekt - kein ptest-Merker, keine
    #    MQTT-Meldung - nicht nur der Text der Antwort.
    (tmp / 'ptest').unlink(missing_ok=True)
    ernten(sock)
    out, bef = lauf(ordner / endpunkt, kuerzel, ordner, 'ptest=1')
    n6 = ernten(sock)
    gesetzt = (tmp / 'ptest').is_file()
    abgewiesen = 'ERR=TOKEN' in out
    print('  6. ?ptest=1 OHNE Token: %s, Merker gesetzt=%s, %d Themen'
          % (out.strip().splitlines()[0] if out.strip() else '(leer)',
             'ja' if gesetzt else 'nein', len(n6)))
    if not abgewiesen or gesetzt or n6:
        befunde.append('%s: ?ptest=1 loest OHNE Token aus' % kuerzel)

    # 7. Selbsttest: richtiges Token bejaht, falsches verneint, und in beiden
    #    Faellen darf nichts passieren.
    out_ok, _ = lauf(ordner / endpunkt, kuerzel, ordner, 'selftest=1&token=PRUEFTOKEN')
    out_falsch, _ = lauf(ordner / endpunkt, kuerzel, ordner, 'selftest=1&token=FALSCH')
    n7 = ernten(sock)
    gut = 'SELFTEST;OK=1' in out_ok and 'SELFTEST;OK=0;ERR=TOKEN' in out_falsch
    print('  7. ?selftest=1:       richtig=%s falsch=%s, %d Themen (erwartet 0)'
          % (out_ok.strip().splitlines()[0] if out_ok.strip() else '(leer)',
             out_falsch.strip().splitlines()[0] if out_falsch.strip() else '(leer)', len(n7)))
    if not gut:
        befunde.append('%s: ?selftest=1 antwortet nicht nach Hausstandard' % kuerzel)
    if n7 or (tmp / 'ptest').is_file():
        befunde.append('%s: ?selftest=1 loest etwas aus - das darf es nicht' % kuerzel)
    return befunde


def pruefe_marstek(sock):
    """MarstekVenus: tragen energie_* und rang_* wirklich ueber MQTT?"""
    ordner = neuester_ordner('LoxBerry-Plugin-MarstekVenus')
    if ordner is None:
        print('  kein Ordner LoxBerry-Plugin-MarstekVenus-* gefunden')
        return ['marstekvenus: Ordner fehlt']
    print('  %s' % ordner.name)
    befunde = []
    d = LB / 'config/plugins/marstekvenus'
    d.mkdir(parents=True, exist_ok=True)
    # Modbus an, damit der Cron die Energiezaehler ueberhaupt anfasst; die IP
    # zeigt auf einen toten Port, der Abruf scheitert also sofort und liefert
    # ok=0. Gemeldet werden muss trotzdem - genau das ist der Pruefpunkt.
    (d / 'marstek.json').write_text(json.dumps({
        'devices': [{'name': 'Pruefspeicher', 'ip': '127.0.0.1', 'port': 1, 'modbus': 1}],
        'mqtt_enabled': 1, 'mqtt_topic': 'marstek', 'aktionstoken': 'PRUEFTOKEN',
        'awattar': 'de', 'vat': 1.19, 'fallback_min': 0,
    }, ensure_ascii=False), encoding='utf-8')
    tmp = Path('C:/tmp/marstekvenus')
    tmp.mkdir(parents=True, exist_ok=True)
    for f in list(tmp.glob('mqtt_sig*')) + list(tmp.glob('mqtt_beat*')) + list(tmp.glob('energy_*')):
        f.unlink(missing_ok=True)
    ernten(sock)

    lauf(ordner / 'bin/cron.php', 'marstekvenus', ordner)
    n1 = ernten(sock)
    kurz = {k.rsplit('/', 1)[-1]: v for k, v in n1.items()}
    fehlt_e = [t for t in MARSTEK_ENERGIE if t not in kurz]
    fehlt_r = [t for t in MARSTEK_RAENGE if t not in kurz]
    print('  1. Cron:               %3d Themen' % len(n1))
    print('     Energiezaehler:     %s' % ('alle neun' if not fehlt_e else 'ES FEHLEN ' + ', '.join(fehlt_e)))
    print('     Spotpreis-Raenge:   %s' % ('alle sechs' if not fehlt_r else 'ES FEHLEN ' + ', '.join(fehlt_r)))
    if fehlt_e:
        befunde.append('marstekvenus: energie_* fehlen (%s)' % ', '.join(fehlt_e))
    if fehlt_r:
        befunde.append('marstekvenus: rang_* fehlen (%s)' % ', '.join(fehlt_r))

    # 2. Unveraendert: die neuen Meldungen duerfen nicht jede Minute wiederholt
    #    werden. Der Status darf weiterhin durchgehen - der haengt am Geraet.
    lauf(ordner / 'bin/cron.php', 'marstekvenus', ordner)
    n2 = ernten(sock)
    kurz2 = {k.rsplit('/', 1)[-1] for k in n2}
    wiederholt = sorted(kurz2 & (set(MARSTEK_ENERGIE) | set(MARSTEK_RAENGE)))
    print('  2. Cron unveraendert:  %3d Themen, davon energie_/rang_: %d'
          % (len(n2), len(wiederholt)))
    if wiederholt:
        befunde.append('marstekvenus: energie_/rang_ werden trotz unveraenderter '
                       'Werte wiederholt (%s ...)' % wiederholt[0])

    # 3. HTTP gegen MQTT: dieselben Zahlen?
    for f in list(tmp.glob('mqtt_sig*')) + list(tmp.glob('mqtt_beat*')):
        f.unlink(missing_ok=True)
    ernten(sock)
    out_e, _ = lauf(ordner / 'webfrontend/html/marstek.php', 'marstekvenus', ordner, 'energy')
    out_r, _ = lauf(ordner / 'webfrontend/html/marstek.php', 'marstekvenus', ordner, 'ranks')
    n3 = {k.rsplit('/', 1)[-1]: v for k, v in ernten(sock).items()}
    # Die beiden Zeilen GETRENNT auswerten: ENERGY und RANKS haben beide ein
    # Feld OK. In einen Topf geworfen verglichen sich energie_ok und rang_ok
    # gegen denselben Wert - das meldete am 16.08. eine Abweichung, die keine
    # war. Der Prueflingsaufbau, nicht das Plugin.
    abw = []
    for zeile, topics in ((out_e, MARSTEK_ENERGIE), (out_r, MARSTEK_RAENGE)):
        http = dict(re.findall(r'([A-Z]+)=([^;\s]*)', zeile))
        for topic in topics:
            feld = topic.split('_', 1)[1].upper()
            if feld in http and topic in n3 and float(http[feld]) != float(n3[topic]):
                abw.append('%s (HTTP %s / MQTT %s)' % (topic, http[feld], n3[topic]))
    print('  3. HTTP gegen MQTT:    %d Themen verglichen -> %s'
          % (len(n3), 'gleich' if n3 and not abw else ('ABWEICHUNG ' + '; '.join(abw) if abw else 'MQTT leer')))
    if abw:
        befunde.append('marstekvenus: HTTP und MQTT weichen ab (%s)' % '; '.join(abw))
    if not n3:
        befunde.append('marstekvenus: der Endpunkt meldet nichts per MQTT')
    return befunde


if __name__ == '__main__':
    namen = [a for a in sys.argv[1:] if a in LINIEN] or sorted(LINIEN)
    unbekannt = [a for a in sys.argv[1:] if a not in LINIEN]
    for u in unbekannt:
        print('unbekannte Linie: %s (bekannt: %s)' % (u, ', '.join(sorted(LINIEN))))
    vorlauf_schreiben()
    lb_aufbauen()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', PORT))
    alle = []
    for n in namen:
        print('=' * 72)
        alle += pruefe(n, s)
    if not sys.argv[1:] or 'marstekvenus' in sys.argv[1:]:
        print('=' * 72)
        alle += pruefe_marstek(s)
    s.close()
    print('=' * 72)
    if alle:
        print('BEFUNDE:\n  - ' + '\n  - '.join(alle))
        sys.exit(1)
    print('ALLE PRUEFUNGEN BESTANDEN')
