# -*- coding: utf-8 -*-
"""Eichung der Assistenten-Pruefstaende.

Jede Verbiegung des Codes MUSS mindestens einen der beiden Pruefstaende rot
machen. Eine Verbiegung, die gruen bleibt, misst nichts - die Zeile sieht
dann nur so aus, als pruefe sie etwas.

UMGEBAUT AM 30.08.2026. Die Fassung davor hatte zwei Loecher, und sie waren
nicht klein:

  1. Sie verbog AUSSCHLIESSLICH webfrontend/html/rk_lib.php. Der ganze
     Uebernahme-Teil steht aber in webfrontend/htmlauth/index.php -
     Freiheitstest, Duplikatwaechter, Formularmerkmal, Pfadzuweisung,
     Ueberlauf. Verbiegungen dort waren ausserhalb ihrer Reichweite.
  2. Sie startete AUSSCHLIESSLICH rk_assistent_pruefen.php. Die Knopfprobe,
     die als einzige bis in die Konfigurationsdatei sieht, lief nie mit.

Gemessen wurde damals: von zehn Verbiegungen blieben zehn gruen, die
irgendwo ausserhalb von rk_lib.php sassen. Dass drei davon trotzdem
auffielen, verdankte sich allein dem Umstand, dass jemand die Knopfprobe von
Hand mitlaufen liess.

Jetzt wird eine KOPIE DES GANZEN PLUGINS verbogen, und beide Pruefstaende
laufen dagegen.

Aufruf:
    python3 Werkzeuge/rk_assistent_eichung.py <scratch> <plugin> <php.exe>

Voraussetzung: rk_ms_attrappe.php laeuft auf drei Ports -
    MS_PORT        (Vorgabe 24500)  ohne Anmeldezwang
    MS_PORT_AUTH   (Vorgabe 24501)  mit MS_VERLANGT_ANMELDUNG=1
    MS_PORT_GROSS  (Vorgabe 24502)  mit MS_GROSSE_ANLAGE=1
Ohne den dritten bleiben Ueberlauf, halbe Raeume und die Mehrdeutigkeit
in derselben Kategorie ungemessen; das Werkzeug sagt es dann.
"""
import io
import json
import os
import shutil
import subprocess
import sys

S, R, PHP = sys.argv[1], sys.argv[2], sys.argv[3]
HIER = os.path.dirname(os.path.abspath(__file__))
PHPDIR = os.path.dirname(PHP)

PORT = os.environ.get('MS_PORT', '24500')
PORT_AUTH = os.environ.get('MS_PORT_AUTH', '24501')
PORT_GROSS = os.environ.get('MS_PORT_GROSS', '24502')
PORT_WEB = int(os.environ.get('EICH_PORT_WEB', '24790'))
BANK = os.environ.get('EICH_BANK', 'C:/tmp/rk_eichbank')

LIB = 'webfrontend/html/rk_lib.php'
IDX = 'webfrontend/htmlauth/index.php'

# (Bezeichnung, Datei, alt, neu)
FAELLE = [
    # ---- rk_lib.php: die Auswahl ----
    ('Statuscode wieder als Messwert zulassen', LIB,
     b"$nie = array('code', 'control'", b"$nie = array('kein_code', 'control'"),
    ('value nicht mehr allein entscheiden lassen', LIB,
     b"if ($wert_pfad !== '') {", b"if (false) {"),
    ('Zuordnung ueber den Namen statt ueber den Raum', LIB,
     b"$r = $b['raum'];", b"$r = $b['name'];"),
    ('abgeleitete Merker nicht mehr ausschliessen', LIB,
     b"'taupunkt', 'soll', 'ziel');", b"'taupunkt_x', 'soll_x', 'ziel');"),
    ('Kategoriefilter wirkungslos machen', LIB,
     b"&& stripos($b['kategorie'], $nur_kategorie) === false", b"&& false"),
    ('401 nicht mehr eigens melden', LIB,
     b"'MELD.MS_401'", b"'MELD.MS_HTTP'"),
    ('Bausteine ohne Raum doch vorschlagen', LIB,
     b"if ($b['raum'] === '') { continue; }", b"if (false) { continue; }"),
    ('Miniserverliste wieder ueber [0] statt reset()', LIB,
     b"return reset($alle);", b"return isset($alle[0]) ? $alle[0] : null;"),
    # ---- rk_lib.php: neu in 0.11.2 ----
    ('Raumvergleich ohne Trimmen und Kleinschreibung', LIB,
     b"return mb_strtolower_ersatz($a) === mb_strtolower_ersatz($b);",
     b"return $a === $b;"),
    ('freier Platz sieht nur auf drei Felder', LIB,
     b"foreach (array('name', 'quelle', 'quelle_rf', 'pfad_t', 'pfad_rf',",
     b"foreach (array('name', 'pfad_t', 'pfad_rf', 'x1', 'x2',"),
    ('Zugangsdaten wieder an jede Adresse', LIB,
     b"if (isset($bekannt[$wirt])) { return true; }",
     b"if (true) { return true; }"),
    ('HTTPS wieder ignorieren', LIB,
     b"$schema = !empty($ms['https']) ? 'https://' : 'http://';",
     b"$schema = 'http://';"),
    ('Preferhttps nicht mehr lesen', LIB,
     b"$https = in_array((string) $ms[$k], array('1', 'true'), true);",
     b"$https = false;"),
    ('je Bauart eine Probe wieder auf EINE Probe kuerzen', LIB,
     b"if (isset($aus[$g][$typ])) { continue; }",
     b"if ($aus[$g]) { continue; }"),
    # ---- index.php: der Uebernahme-Teil ----
    ('halbe Raeume doch uebernehmen', IDX,
     b"} elseif ($v['t'] === null || $v['rf'] === null) {",
     b"} elseif (false) {"),
    ('mehrdeutige Raeume wieder still uebernehmen', IDX,
     b"} elseif ($v['t_mehr'] > 0 || $v['rf_mehr'] > 0) {",
     b"} elseif (false) {"),
    ('Ueberlauf wieder verschweigen', IDX,
     b"} elseif ($rk_uebrig <= 0) {", b"} elseif (false) {"),
    ('Raumname wieder ungetrimmt schreiben', IDX,
     b"$rk_neu2[$rk_i]['name'] = trim((string) $rk_v['raum']);",
     b"$rk_neu2[$rk_i]['name'] = $rk_v['raum'];"),
    ('Feuchtepfad wieder vom Temperaturbaustein abschreiben', IDX,
     b"$rk_neu2[$rk_i]['pfad_rf'] = $rk_prf['pfad'];",
     b"$rk_neu2[$rk_i]['pfad_rf'] = $rk_pt['pfad'];"),
    ('Formularwaechter ausschalten', IDX,
     b"if ($rk_post && !rk_formtoken_ok()) {", b"if (false) {"),
    ('Duplikatwaechter ausschalten (der wirksame, in der Lage)', IDX,
     b"if ($rk_schon) {\n                    $rk_lage = 'schon_da';",
     b"if (false) {\n                    $rk_lage = 'schon_da';"),
    ('Rueckgabewert von rk_geheim_speichern wieder ignorieren', IDX,
     b"if (rk_geheim_speichern(array('benutzer' => $rk_ms['user'],",
     b"if (true || rk_geheim_speichern(array('benutzer' => $rk_ms['user'],"),
]


def bank_bauen(ziel, port):
    """Eine frische LoxBerry-Bank fuer die Knopfprobe."""
    ms = {"Name": "Attrappe", "Ipaddress": "127.0.0.1", "Port": str(port),
          "Admin": "admin", "Pass": "geheim123",
          "Credentials": "admin:geheim123", "Porthttps": str(port),
          "Preferhttps": "0", "Usecloudns": "0"}
    gen = {"Base": {"Version": "4.0.0", "Systemloglevel": "7",
                    "Sendstatistic": "0"},
           "Network": {"Interface": "eth0", "Friendlyname": "Eichbank",
                       "Ipaddress": "192.168.1.50", "Mask": "255.255.255.0",
                       "Gateway": "192.168.1.1", "Dns": "192.168.1.1"},
           "Timeserver": {"Method": "ntp", "Ntpserver": "pool.ntp.org"},
           "Miniserver": {"1": ms},
           "Webserver": {"Port": "80"}, "Ssdp": {"Enabled": "1"},
           "Mqtt": {"Brokerhost": "localhost", "Brokerport": "1883",
                    "Udpinport": "11884", "Uselocalbroker": "1",
                    "Websocketport": "9001", "Finderdisabled": False,
                    "Gatewayautostart": "1", "Gatewayversion": 1,
                    "Loglevel": "6"}}
    shutil.rmtree(ziel, ignore_errors=True)
    for d in ('config/system', 'config/plugins/raumklima',
              'data/plugins/raumklima', 'log/plugins/raumklima', 'libs/phplib'):
        os.makedirs(os.path.join(ziel, d.replace('/', os.sep)), exist_ok=True)
    io.open(os.path.join(ziel, 'config', 'system', 'general.json'), 'w',
            encoding='utf-8').write(json.dumps(gen, ensure_ascii=False))
    q = os.path.join(HIER, 'lb', 'libs', 'phplib')
    if os.path.isdir(q):
        shutil.rmtree(os.path.join(ziel, 'libs', 'phplib'), ignore_errors=True)
        shutil.copytree(q, os.path.join(ziel, 'libs', 'phplib'))
    shutil.copyfile(os.path.join(HIER, 'vorlauf.php'), 'C:/tmp/rk_vorlauf.php')


def attrappen_da():
    """Antworten alle drei Attrappen JETZT?

    ------------------------------------------------------------------------
    Am 30.08.2026 hat dieses Werkzeug "22 von 22 Verbiegungen bemerkt"
    gemeldet - und die Zahl war wertlos. Die Attrappen waren nach den ersten
    Laeufen gestorben; danach ging JEDER Lauf rot, gleichgueltig ob verbogen
    oder nicht. Eine Eichung, die den Grundstand nur EINMAL am Anfang misst,
    haelt einen abgestuerzten Pruefstand fuer eine bemerkte Verbiegung.

    Das ist derselbe Fehler, den die Eichung beim Pruefling sucht, nur eine
    Ebene hoeher. Deshalb wird vor jedem Fall nachgesehen - ein HTTP-Aufruf
    kostet nichts gegen einen falschen Bericht.
    ------------------------------------------------------------------------
    """
    import urllib.error
    import urllib.request
    for p in (PORT, PORT_AUTH, PORT_GROSS):
        if p in ('', '0'):
            continue
        try:
            urllib.request.urlopen(
                'http://127.0.0.1:%s/data/LoxAPP3.json' % p, timeout=5).read(64)
        except urllib.error.HTTPError as e:
            if e.code == 401:      # der Port mit Anmeldezwang - der lebt
                continue
            return False
        except Exception:
            return False
    return True


def bench(kopie):
    """rk_assistent_pruefen.php gegen die Kopie. Rueckgabe: (rot, Zeile)."""
    a = subprocess.run(
        [PHP, '-n', '-d', 'date.timezone=Europe/Berlin',
         '-d', 'extension_dir=' + PHPDIR + '/ext', '-d', 'extension=curl',
         '-d', 'extension=openssl',
         os.path.join(HIER, 'rk_assistent_pruefen.php')],
        env=dict(os.environ, RK_LIB=os.path.join(kopie, LIB.replace('/', os.sep)),
                 MS_PORT=PORT, MS_PORT_AUTH=PORT_AUTH, MS_PORT_GROSS=PORT_GROSS),
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        timeout=300)
    for z in (a.stdout + a.stderr).splitlines():
        if z.startswith('== Ergebnis'):
            return ('0 ROT' not in z), z.strip()
    return (True, 'KEIN ERGEBNIS: '
            + (a.stdout + a.stderr).strip().replace('\n', ' | ')[:140])


def knopf(kopie, port_web):
    """Die Knopfprobe gegen die Kopie. Rueckgabe: (rot, Zeile)."""
    bank_bauen(BANK, PORT)
    a = subprocess.run(
        [sys.executable, os.path.join(HIER, 'rk_assistent_knopfprobe.py'),
         kopie, BANK, PHPDIR, str(port_web)],
        env=dict(os.environ, MS_PORT_GROSS=PORT_GROSS),
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        timeout=600)
    for z in (a.stdout + a.stderr).splitlines():
        if z.startswith('== ') and 'Befund' in z:
            return ('0 Befund' not in z), z.strip()
    return (True, 'KEIN ERGEBNIS: '
            + (a.stdout + a.stderr).strip().replace('\n', ' | ')[:140])


def main():
    kopie = os.path.join(S, 'eich', 'plugin')
    shutil.rmtree(os.path.join(S, 'eich'), ignore_errors=True)
    os.makedirs(os.path.join(S, 'eich'), exist_ok=True)
    shutil.copytree(R, kopie)

    if PORT_GROSS in ('', '0'):
        print('  HINWEIS: MS_PORT_GROSS nicht gesetzt - Ueberlauf, halbe')
        print('           Raeume und die Mehrdeutigkeit in DERSELBEN')
        print('           Kategorie werden NICHT gemessen.')

    r1, z1 = bench(kopie)
    r2, z2 = knopf(kopie, PORT_WEB)
    print('  %-52s %s' % ('unveraendert, Bibliothek (muss GRUEN sein)', z1))
    print('  %-52s %s' % ('unveraendert, Knopfprobe  (muss GRUEN sein)', z2))
    if r1 or r2:
        # Eine Eichung auf rotem Grund misst nichts: jede Verbiegung sieht
        # dann bemerkt aus, auch die, die niemand bemerkt haette. Am
        # 29.08.2026 stand die Attrappe mit Anmeldezwang nicht - und alle
        # acht Zeilen meldeten trotzdem "ok".
        sys.exit('ABBRUCH: der unveraenderte Stand ist nicht gruen. Laufen die '
                 'Attrappen auf %s (ohne), %s (mit Anmeldung) und %s (gross)?'
                 % (PORT, PORT_AUTH, PORT_GROSS))

    roh = {}
    for d in (LIB, IDX):
        roh[d] = io.open(os.path.join(R, d.replace('/', os.sep)), 'rb').read()

    print()
    schlecht = 0
    for i, (bez, datei, alt, neu) in enumerate(FAELLE):
        if not attrappen_da():
            print('  [!! ] ABBRUCH: eine Attrappe antwortet nicht mehr.')
            print('        Alles ab hier waere aus dem falschen Grund rot.')
            return 2
        p = os.path.join(kopie, datei.replace('/', os.sep))
        if alt not in roh[datei]:
            print('  [!! ] %-52s ANKER FEHLT in %s' % (bez, os.path.basename(datei)))
            schlecht += 1
            continue
        io.open(p, 'wb').write(roh[datei].replace(alt, neu, 1))
        rb, zb = bench(kopie)
        rk, zk = (False, '-') if rb else knopf(kopie, PORT_WEB + 1 + i)
        io.open(p, 'wb').write(roh[datei])
        wo = 'Bibliothek' if rb else ('Knopfprobe' if rk else '')
        if not (rb or rk):
            schlecht += 1
            print('  [GRUEN GEBLIEBEN] %-46s %s' % (bez, zb))
        else:
            print('  [rot ] %-52s von der %s' % (bez, wo))
        # Verbiegungen in index.php DUERFEN die Bibliothekspruefung nicht
        # roetenen - sie laedt index.php gar nicht. Tut sie es doch, ist
        # nicht die Verbiegung bemerkt worden, sondern etwas anderes kaputt.
        if datei == IDX and rb:
            print('        ^ VERDACHT: die Bibliothekspruefung laedt index.php')
            print('          nicht. Rot kann hier nicht von der Verbiegung')
            print('          kommen - Attrappe pruefen.')
            schlecht += 1

    # Der Grundstand am ENDE. Ist er nicht mehr gruen, war der Pruefstand
    # zwischendurch kaputt, und alle Urteile darueber sind wertlos.
    rb2, zb2 = bench(kopie)
    rk2, zk2 = knopf(kopie, PORT_WEB + 99)
    print()
    print('  %-52s %s' % ('Grundstand am ENDE, Bibliothek', zb2))
    print('  %-52s %s' % ('Grundstand am ENDE, Knopfprobe', zk2))
    if rb2 or rk2:
        print('  ABBRUCH: der Grundstand ist am Ende nicht mehr gruen.')
        print('  Die Urteile oben sind NICHT gueltig.')
        return 2

    print()
    print('  %d von %d Verbiegungen wurden bemerkt.'
          % (len(FAELLE) - schlecht, len(FAELLE)))
    return 1 if schlecht else 0


if __name__ == '__main__':
    sys.exit(main())
