#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wirkt der Wachposten - und laesst er das Richtige durch?

WOZU, WENN ES SCHON ZWEI WERKZEUGE GIBT

  sicherung_formtoken.py  misst, ob die FORMULARE ein Merkmalsfeld fuehren.
  wachposten_pruefen.py   misst, ob jeder Zweig vom Wachposten GEDECKT ist.

Beide lesen. Keines drueckt. Ein Wachposten, der abweist und trotzdem
schreiben laesst, besteht beide - und ist trotzdem keiner. Genauso einer,
der so gruendlich abweist, dass auch der richtige Knopf nichts mehr tut;
der faellt niemandem auf, bis ein Anwender schreibt, dass Speichern nicht
geht.

Deshalb misst dieses Werkzeug den EFFEKT: veraendert der POST die
Konfigurationsdatei - ja oder nein?

VIER FAELLE, und der vierte ist der, den man vergisst:

    1. richtiges Merkmal  -> MUSS schreiben
    2. falsches Merkmal   -> darf NICHT schreiben, und es muss gemeldet werden
    3. ohne Merkmal       -> darf NICHT schreiben, und es muss gemeldet werden
    4. LEERES Merkmal     -> darf NICHT schreiben

Der vierte, weil hash_equals('', '') in PHP TRUE ergibt. Wer das Feld
nicht vor dem Vergleich auf leer prueft, hat einen Wachposten gebaut, den
jeder passiert, der das Feld einfach leer laesst.

    python wachposten_wirkung.py [<Pluginordner> ...]

Ohne Argumente werden alle Linien geprueft, die einen Wachposten haben.
Rueckgabe 1, wenn eine Linie einen Fall nicht besteht.
"""
import hashlib
import hmac
import io
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HIER = Path(__file__).resolve().parent
ARBEIT = HIER.parent
LB = HIER / 'lb'
VORLAUF_POST = HIER / 'vorlauf_post.php'
PHPS = [('7.4', r'C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe'),
        ('8.4', r'C:\tmp\php-8.4.27-Win32-vs17-x64\php.exe')]
TOKEN = 'PRUEFTOKEN1234'

# Woran ein Wachposten zu erkennen ist: eine Pruefung des Formularmerkmals,
# die bei einem POST greift. Der Feldname ist nicht ueberall gleich.
WACHE = re.compile(r'(?m)^\s*if\s*\(.*&&\s*!\w+_formtoken_ok\(')
FELD = re.compile(r'name="(fmt|formtoken|form_token|csrf)"')


def php_da(p):
    return os.path.isfile(p)


def linien(argv):
    if argv:
        return [Path(a).resolve() for a in argv]
    aus = []
    for e in sorted(os.listdir(str(ARBEIT))):
        o = ARBEIT / e
        if not e.startswith('LoxBerry-Plugin-') or not o.is_dir():
            continue
        idx = o / 'webfrontend' / 'htmlauth' / 'index.php'
        if idx.is_file() and WACHE.search(idx.read_text(encoding='utf-8', errors='replace')):
            aus.append(o)
    return aus


# Wo die Bibliothek liegen darf. Der html-Zweig ist der Regelfall; Kodi NG
# legt sie unter bin/ ab, damit der Cron-Sender sie ueber __DIR__ findet -
# auf dem installierten System sind bin/ und webfrontend/ getrennte Baeume.
# Bis zum 28.08.2026 stand hier nur der html-Zweig, und jede Linie mit einer
# anderen Lage wurde stumm uebersprungen.
LIB_ORTE = (('webfrontend', 'html'), ('webfrontend', 'htmlauth'), ('bin',))


def lib_pfad(ordner):
    """Die Bibliothek des Plugins - an den drei Orten, an denen sie liegt."""
    for teile in LIB_ORTE:
        d = ordner.joinpath(*teile)
        if not d.is_dir():
            continue
        for f in sorted(d.glob('*_lib.php')):
            return f
    return None


def kuerzel_von(ordner):
    """Das Plugin-Kuerzel aus dem Namen der Bibliothek."""
    f = lib_pfad(ordner)
    return f.name[:-len('_lib.php')] if f else None


def konfigname(ordner, kz):
    """Wie heisst die Konfigurationsdatei? Steht in xx_paths()."""
    t = lib_pfad(ordner).read_text(encoding='utf-8', errors='replace')
    # Der Name der Ordnervariablen ist nicht ueberall gleich: die meisten
    # Linien fuehren $ordner, VolkswagenID fuehrt $dir. Wer nur einen der
    # beiden kennt, meldet "nicht ablesbar" und misst nichts - und das liest
    # sich beim Ueberfliegen wie ein uebersprungener Sonderfall.
    m = re.search(r"'config'\s*=>\s*\$home\s*\.\s*'/config/plugins/'\s*\.\s*"
                  r"\$[a-z_]+\s*\.\s*'/([A-Za-z0-9_.-]+)'", t)
    if m:
        return m.group(1)
    # Der Name darf auch eine Konstante sein - das ist die sauberere
    # Schreibweise, weil er dann nur an einer Stelle steht. Kodi NG macht es
    # so; bis zum 28.08.2026 meldete das Werkzeug daraufhin "nicht ablesbar"
    # und mass gar nichts.
    m = re.search(r"'config'\s*=>\s*\$home\s*\.\s*'/config/plugins/'\s*\.\s*"
                  r"\$[a-z_]+\s*\.\s*'/'\s*\.\s*([A-Z][A-Z0-9_]*)", t)
    if m:
        k = re.search(r"define\s*\(\s*'%s'\s*,\s*'([A-Za-z0-9_.-]+)'\s*\)"
                      % re.escape(m.group(1)), t)
        return k.group(1) if k else None
    return None


def merkmalsdatei(ordner):
    """Fuehrt die Linie ein eigenes Formularmerkmal als Datei?

    Zwei Bauarten sind im Hause im Gebrauch:
      (a) das Merkmal ist hmac(Aktionstoken, 'formular-v1') - dann gibt es
          keine eigene Datei, und der Wert laesst sich errechnen.
      (b) das Merkmal ist ein eigenes Geheimnis in einer Datei neben der
          Konfiguration (Kodi NG: ko_formkey). Dann laesst es sich NICHT
          errechnen; man muss es hinterlegen und genau so schicken.
    Wer nur (a) kennt, meldet an jeder Linie der Bauart (b) einen Befund am
    ersten Fall - an einem Wachposten, der tadellos arbeitet.
    """
    t = lib_pfad(ordner).read_text(encoding='utf-8', errors='replace')
    m = re.search(r"'formkey'\s*=>\s*\$home\s*\.\s*'/config/plugins/'\s*\.\s*"
                  r"\$[a-z_]+\s*\.\s*'/([A-Za-z0-9_.-]+)'", t)
    return m.group(1) if m else None


def ordnername(ordner, kz):
    """Unter welchem Namen sucht das Plugin seinen Konfigordner?"""
    t = lib_pfad(ordner).read_text(encoding='utf-8', errors='replace')
    m = re.search(r"\$[a-z_]+\s*=\s*'([a-z0-9_-]+)';\s*//", t)
    if m:
        return m.group(1)
    m = re.search(r"\$[a-z_]+\s*===\s*'html'.*?\$[a-z_]+\s*=\s*'([a-z0-9_-]+)'", t, re.S)
    return m.group(1) if m else kz


def lauf(php, ordner, kz, pd, post):
    umg = dict(os.environ)
    seite = ordner / 'webfrontend' / 'htmlauth' / 'index.php'
    umg.update({
        'LBHOMEDIR': str(LB), 'LBPPLUGINDIR': pd,
        'LBPCONFIGDIR': str(LB / 'config/plugins' / pd),
        'LBPLOGDIR': str(LB / 'log/plugins' / pd),
        'LBPDATADIR': str(LB / 'data/plugins' / pd),
        'LBPHTMLAUTHDIR': str(seite.parent),
        'LBPHTMLDIR': str(ordner / 'webfrontend' / 'html'),
        'LBPTEMPLATEDIR': str(ordner / 'templates'),
        'LBPBINDIR': str(ordner / 'bin')})
    pf = HIER / 'post_wache.json'
    pf.write_text(json.dumps(post), encoding='utf-8')
    umg['PRUEF_POST'] = str(pf)
    r = subprocess.run(
        [php, '-n', '-d', 'include_path=.;' + str(LB / 'libs' / 'phplib'),
         '-d', 'auto_prepend_file=' + str(VORLAUF_POST),
         '-d', 'display_errors=0', '-d', 'error_reporting=32767',
         '-d', 'date.timezone=Europe/Berlin',
         '-d', 'extension_dir=' + str(Path(php).parent / 'ext'),
         '-d', 'extension=curl', '-d', 'extension=openssl',
         '-d', 'extension=mbstring', '-d', 'extension=sockets', str(seite)],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        env=umg, cwd=str(seite.parent), timeout=180)
    return r.stdout or ''


def pruefe(ordner):
    kz = kuerzel_von(ordner)
    if kz is None:
        return ['NICHTMESSBAR|%s: keine Bibliothek xx_lib.php gefunden' % ordner.name]
    datei = konfigname(ordner, kz)
    if datei is None:
        return ['NICHTMESSBAR|%s: Konfigurationsdatei nicht aus %s_paths() ablesbar'
                % (ordner.name, kz)]
    pd = ordnername(ordner, kz)
    cfgpfad = LB / 'config/plugins' / pd / datei

    seite = (ordner / 'webfrontend' / 'htmlauth' / 'index.php').read_text(
        encoding='utf-8', errors='replace')
    # Der Feldname steht nicht ueberall in der Oberflaeche selbst: wo das
    # versteckte Feld von einer Bibliotheksfunktion erzeugt wird (VolkswagenID:
    # vw_formfeld()), steht der Name dort. Wer nur die Oberflaeche liest,
    # nimmt den Rueckfall 'fmt', schickt ein Feld, das es nicht gibt, und
    # meldet daraufhin einen Befund am ersten Fall - obwohl der Wachposten
    # genau richtig gearbeitet hat. Gemessen am 27.08.2026.
    lib_t = lib_pfad(ordner).read_text(encoding='utf-8', errors='replace')
    m = FELD.search(seite) or FELD.search(lib_t)
    feld = m.group(1) if m else 'fmt'
    # Der Merkmalswert wird genauso gebildet wie im Plugin - und das ist
    # nicht ueberall dasselbe (siehe merkmalsdatei()).
    mdatei = merkmalsdatei(ordner)
    if mdatei:
        # 32 Hexziffern: die Gestalt, die Kodi NG selbst wuerfelt und prueft.
        fmt_gut = 'a1b2c3d4e5f60718293a4b5c6d7e8f90'
    else:
        fmt_gut = hmac.new(TOKEN.encode(), b'formular-v1', hashlib.sha256).hexdigest()

    # Welchen Knopf und welche Felder braucht DIESE Linie, damit ihr
    # Speichern-Handler ueberhaupt anlaeuft?
    #
    # Bis zum 27.08.2026 standen hier fest die Felder des aWATTar-Plugins
    # (save, cheap, expensive, window, consumption). An einer Linie mit anderen
    # Feldnamen lief kein Handler an, nichts wurde geschrieben - und weil der
    # erste Fall ein Schreiben ERWARTET, meldete das Werkzeug einen Befund an
    # einem Wachposten, der tadellos arbeitete. Ein Pruefstand, der die falsche
    # Lage aufbaut, bestaetigt den Fehler.
    #
    # Was hier nicht steht, wird als NICHT MESSBAR gemeldet, nicht als Befund.
    sonderfall = {
        'vw': ('intervall', {'intervall': 300},
               {'speichern': '1', 'activetab': 'tab-settings', 'intervall': '900',
                'takt_wartung': '24', 'temp_min': '18', 'temp_max': '26',
                'verlauf_tage': '30', 'wartezeit': '8', 'wartezeit_endpunkt': '3',
                'heim_radius': '150', 'abstand_abruf': '120', 'befehle_stunde': '30',
                'entprellung': '20', 'abfahrt_vorlauf': '20', 'abfahrt_temp': '21',
                'heim_breite': '', 'heim_laenge': '', 'empf_grenze': '',
                'empf_thema': '', 'abfahrt_thema': ''}),
    }
    # Pumpenwacht. Beobachtet wird an_w - eine Zahl, die der Handler
    # durch pw_wert_pruefen() schickt und dann schreibt. Die Felder sind
    # aus $pw_zahlfelder und $pw_sperrfelder der Oberflaeche abgeschrieben.
    # Kaesten, die nicht mitgeschickt werden, gelten als aus; das ist so
    # gewollt und faellt hier nicht ins Gewicht, weil nur an_w gemessen wird.
    sonderfall['pw'] = (
        'an_w', {'an_w': 20},
        {'speichern': '1', 'activetab': 'tab-settings',
         'modell': '3-45', 'quelle': 'loxone', 'quelle_topic': '',
         'an_w': '30', 'trocken_w': '228', 'trocken_s': '5',
         'ueberlast_w': '1092', 'dauerlauf_s': '900', 'starts_h': '25',
         'anlauf_s': '0', 'stale_s': '300',
         'sperren_ein': '1', 'sperre_trockenlauf': '1',
         'sperre_dauerlauf': '1', 'sperre_kein_anlauf': '1',
         'quittung_noetig': '1', 'mqtt_ein': '1', 'mqtt_topic': 'pumpe'})

    sonderfall['sk'] = (
        'intervall', {'intervall': 300},
        {'speichern': '1', 'activetab': 'tab-settings', 'intervall': '900',
         'takt_stamm': '12', 'takt_wartung': '24', 'temp_min': '18', 'temp_max': '26',
         'verlauf_tage': '30', 'wartezeit': '8', 'abstand_abruf': '60',
         'befehle_stunde': '30', 'entprellung': '20', 'heim_radius': '150',
         'heim_breite': '', 'heim_laenge': '', 'email': '', 'passwort': ''})

    # Kodi NG: der Knopf heisst wie im Rueckfall "save", die Felder sind
    # andere. Gemessen wird kodi_port, weil es eine Zahl ist, der Handler
    # es durch ko_wert_pruefen() schickt und es in JEDER Fassung im Formular
    # "save" steht. Bis 17.09.2026 stand hier sender_takt - das wanderte in
    # Kodi NG 1.2.7 in den Reiter MQTT (eigener Handler mqtt_save), und die
    # Messung meldete "richtiges Merkmal - unveraendert" als Befund, obwohl
    # der Wachposten richtig arbeitete.
    sonderfall['ko'] = (
        'kodi_port', {'kodi_port': '8080'},
        {'save': '1', 'activetab': 'tab-settings',
         'kodi_host': '127.0.0.1', 'kodi_port': '8081',
         'kodi_user': '', 'kodi_pass': '', 'sender_takt': '600',
         'hat_sender_ein': '1', 'sender_ein': '1',
         'hat_rpc_ein': '1', 'rpc_ein': '0'})

    if kz in sonderfall:
        pruef_feld, grund_cfg, grund_post = sonderfall[kz]
    else:
        # DER RUECKFALL WIRD GEGENGEPRUEFT, BEVOR ER BENUTZT WIRD.
        #
        # Er baut die Felder des aWATTar-Plugins auf. An einer Linie, die
        # diese Felder nicht kennt, laeuft kein Handler an, es wird nichts
        # geschrieben - und weil der erste Fall ein Schreiben ERWARTET, meldete
        # dieses Werkzeug einen Befund an einem Wachposten, der tadellos
        # arbeitete. Genau davor warnt der Kommentar zwanzig Zeilen weiter
        # oben; eingeloest war es nicht. Gemessen am 27.08.2026 an Skoda
        # Connect NG 0.9.13: zwei Befunde, beide falsch.
        pruef_feld = 'cheap'
        grund_cfg = {'cheap': 20.0}
        grund_post = {'save': '1', 'activetab': 'tab-settings', 'cheap': '7.5',
                      'expensive': '35', 'window': '3', 'consumption': '3500'}
        if 'name="cheap"' not in seite:
            return ['NICHTMESSBAR|%s: die Felder des Rueckfalls (cheap, expensive ...) '
                    'gibt es in dieser Oberflaeche nicht. Ein Eintrag in der Tabelle '
                    'sonderfall fehlt - ohne ihn wuerde der erste Fall zwangslaeufig '
                    'einen Befund melden, den es nicht gibt.' % ordner.name]
    vorher_wert = float(grund_cfg[pruef_feld])

    befunde = []
    for v, php in PHPS:
        if not php_da(php):
            continue
        for name, extra, soll in (('richtiges Merkmal', {feld: fmt_gut}, True),
                                  ('falsches Merkmal', {feld: 'a' * 64}, False),
                                  ('ohne Merkmal', {}, False),
                                  ('leeres Merkmal', {feld: ''}, False)):
            for d in (LB / 'config/plugins' / pd, LB / 'data/plugins' / pd,
                      LB / 'log/plugins' / pd):
                shutil.rmtree(str(d), ignore_errors=True)
                d.mkdir(parents=True, exist_ok=True)
            shutil.rmtree(str(Path('C:/tmp') / pd), ignore_errors=True)
            json.dump(dict({'aktionstoken': TOKEN}, **grund_cfg),
                      io.open(str(cfgpfad), 'w', encoding='utf-8'))
            if mdatei:
                # Ohne diese Zeile wuerfelt das Plugin bei JEDEM Aufruf ein
                # neues Merkmal, hash_equals scheitert immer, und alle vier
                # Faelle laegen unveraendert da - der erste faelschlich.
                io.open(str(cfgpfad.parent / mdatei), 'w',
                        encoding='ascii').write(fmt_gut)
            post = dict(grund_post)
            post.update(extra)
            lauf(php, ordner, kz, pd, post)
            try:
                nachher = json.load(io.open(str(cfgpfad), encoding='utf-8')).get(pruef_feld)
            except Exception:
                nachher = None
            geschrieben = (nachher is not None and abs(float(nachher) - vorher_wert) > 1e-9)
            gut = (geschrieben == soll)
            print('  %-4s %-20s %-14s %s' % (
                v, name, 'geschrieben' if geschrieben else 'unveraendert',
                'ok' if gut else 'BEFUND'))
            if not gut:
                befunde.append('%s: %s unter PHP %s' % (ordner.name, name, v))
    return befunde


ordner = linien(sys.argv[1:])
if not ordner:
    print('Keine Linie mit einem Wachposten gefunden.')
    sys.exit(0)

# ZWEI Listen, nicht eine.
#
# "Der Wachposten laesst einen POST ohne Merkmal durch" ist ein Befund am
# PLUGIN. "Die Konfigurationsdatei liess sich nicht ablesen" ist ein
# Befund am WERKZEUG - sein Sucher kennt die Schreibweise jener Linie
# nicht. Beides in einen Topf zu werfen hiesse, ein halbes Dutzend Linien
# rot zu melden, an denen nichts gemessen wurde. Ein Strich ist kein
# Haken, aber er ist auch kein Kreuz.
echt, unmessbar = [], []
for o in ordner:
    print(o.name)
    for b in pruefe(o):
        if b.startswith('NICHTMESSBAR|'):
            unmessbar.append(b.split('|', 1)[1])
        else:
            echt.append(b)
print('-' * 60)
if echt:
    print('BEFUNDE am Plugin:')
    for b in echt:
        print('  - ' + b)
gemessen = len(ordner) - len(unmessbar)
print('%d von %d Linie(n) gemessen, %d Befund(e).' % (gemessen, len(ordner), len(echt)))
if unmessbar:
    print('NICHT GEMESSEN (der Sucher dieses Werkzeugs kennt die Schreibweise nicht -')
    print('das ist eine offene Frage, kein Freispruch):')
    for b in unmessbar:
        print('  - ' + b)
sys.exit(1 if echt else 0)
