#!/usr/bin/env python3
"""Installationslage: laeuft das Plugin auch dort, wo es spaeter liegt?

WOZU DIESES WERKZEUG
Auf dem installierten LoxBerry liegen die Baeume eines Plugins an voellig
anderen Stellen als im entpackten Archiv:

    Archiv                       installiert
    bin/                         bin/plugins/<ordner>/
    webfrontend/html/            webfrontend/html/plugins/<ordner>/
    webfrontend/htmlauth/        webfrontend/htmlauth/plugins/<ordner>/
    templates/                   templates/plugins/<ordner>/

Ein `require_once dirname(__DIR__) . '/webfrontend/html/xx_lib.php'` aus `bin/`
geht deshalb im Archiv auf und installiert nicht. Die uebrige Pruefkette sieht
das nicht, weil sie am entpackten Archiv arbeitet - dort stimmt der Pfad.

Genau so ist der Hintergrunddienst des Abfahrts-Assistenten von 1.5.0 bis
1.5.7 bei JEDEM Cron-Lauf abgebrochen, ohne dass es jemandem auffiel: der Cron
schreibt nach /dev/null, und der Endpunkt gab danach `OK=0` aus - was in Loxone
aussieht wie "kein Termin gefunden" und nicht wie ein Defekt.

WAS ES TUT
Es baut je Plugin eine Wegwerf-Attrappe im INSTALLIERTEN Aufbau, legt die
Dateien dorthin, wo LoxBerry sie hinlegt, und ruft jedes PHP-Skript einmal
wirklich auf. Gemeldet wird die Fehlerklasse, um die es geht:

    Failed opening required / failed to open stream

Andere Meldungen werden getrennt ausgegeben - sie koennen an der Attrappe
liegen (fehlende Konfiguration, kein Netz) und sind kein Befund dieser Klasse.
Ansehen muss man sie trotzdem.

WIE ES MISST
Jedes Skript wird aufgerufen, und ausgewertet werden BEIDE Quellen: der Text
auf den Ausgaben und der RUECKGABEWERT. Der Rueckgabewert ist noetig, weil ein
Skript schweigen kann - `ini_set('display_errors', '0')` steht in jedem
Loxone-Endpunkt nach Hausstandard, und PHP gibt dann keine Zeile aus, sondern
nur die 255. Am 16.08.2026 hat das Werkzeug deshalb "5 Dateien, in Ordnung"
gemeldet, waehrend der Endpunkt bei jedem Aufruf abbrach - genau die
Fehlerklasse, fuer die es dieses Werkzeug gibt. Schweigt ein Lauf und endet
trotzdem mit einem Fehler, wird er ein zweites Mal mit einem Vorlauf
aufgerufen, der `error_get_last()` selbst ausgibt.

DIE ZWEITE, TEXTLICHE SICHT (erweitert 31.08.2026)
Der Aufruf oben findet den Fehler nur, wenn die require-Zeile beim Aufruf auch
WIRKLICH ausgefuehrt wird. Ein Endpunkt nach Hausstandard prueft aber zuerst
das Token, weist ohne Token mit 403 ab und steigt aus - die fehlerhafte Zeile
darunter wird nie erreicht, der Lauf endet mit 0, und das Werkzeug meldete
"in Ordnung".

Deshalb sucht eine zweite, rein textliche Sicht das Muster, ohne es ausfuehren
zu muessen. Sie durchsuchte bis zum 31.08.2026 ausschliesslich `bin/` - also
ausgerechnet nicht den Baum, in dem die Klasse zuletzt dreimal aufgetreten ist
(Heimkino, SignalBot, Ecowitt-Weiche). Sie sieht jetzt `bin/`,
`webfrontend/html/` und `webfrontend/htmlauth/`, meldet Datei UND Zeile, und
sie zaehlt ihre Ausnahmen, statt sie zu verschweigen.

GEEICHT GEGEN DAS GERAET (05.09.2026)
Die Lage der Attrappe wurde gegen die auf dem LoxBerry installierte
plugininstall.pl (4.0.0.15, Geraet/2026-09-05/08_plugininstall.pl) gemessen:
bin/ -> bin/plugins/<FOLDER> (:923-:937), templates/ -> templates/plugins/
<FOLDER> (:942-:955), webfrontend/htmlauth/ und html/ -> .../plugins/<FOLDER>
(:1046-:1078), config/, data/, log/ als leere Ordner unter .../plugins/<FOLDER>
(:904, :1009, :1027). Das stimmt mit `attrappe_bauen()` ueberein. Nicht
nachgebaut, weil fuer diese Fehlerklasse ohne Belang: icons/, daemon/, cron/,
sudoers/. Abweichung, die man kennen muss: die Attrappe setzt LBPPLUGINDIR und
die LBP*DIR ueber die Umgebung; auf dem Geraet setzt Cron sie NICHT (Geraet/
2026-09-05/11_cron.txt: `cd / && for f in .../cron.01min/*; do ($f ...)`) - ob
loxberry_system.php sie dort aus dem Skriptpfad ableitet, ist GEMESSEN (05.09.2026,
Zeilen 30-54: /plugins/<ordner>/ unter bin, html, htmlauth, templates, log, data,
config, daemons) - die Abweichung ist folgenlos, wenn die Datei am richtigen Ort liegt. Ein
Skript, das erst ueber getenv('LBPBINDIR') seine Bibliothek findet, kann hier
gruen sein und am Geraet scheitern.

WAS ES NICHT TUT
Es ersetzt den Test am Geraet nicht. Es beantwortet eine einzige Frage:
findet jedes Skript seine Bibliotheken auch dann, wenn die Baeume getrennt
sind? Netzzugriffe werden ueber einen unerreichbaren Proxy ins Leere geleitet
und die Konfiguration bleibt leer, damit die Skripte frueh aussteigen.

Eine Datei, deren Aufruf in die Zeitschranke laeuft, ist NICHT gemessen. Sie
zaehlt getrennt und weder als bestanden noch als Befund - "0 von 0 ist in
Ordnung" ist kein Haken.

AUFRUF
    python3 Werkzeuge/installationslage_pruefen.py [--ausnahmen] [<plugin-ordner> ...]

`--ausnahmen` listet jede uebergangene Fundstelle einzeln auf. Ohne den
Schalter steht nur ihre ZAHL in der Zeile des Prueflings - eine Ausnahme wird
gezaehlt und genannt, aber zweihundert Zeilen Ausnahme erschlagen den Befund,
um den es geht.

Ohne Argumente werden alle `LoxBerry-Plugin-*`-Ordner im aktuellen Verzeichnis
geprueft.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Dieselben Interpreter wie die uebrige Pruefkette. Beide Fassungen muessen
# tragen (LoxBerry faehrt 7.4, Debian 13 bringt 8.x) - fuer diese Fehlerklasse
# genuegt aber jede vorhandene.
PHP_KANDIDATEN = [
    os.environ.get('PHP84') or r'C:\tmp\php-8.4.27-Win32-vs17-x64\php.exe',
    os.environ.get('PHP74') or r'C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe',
    'php',
]

# Die Klasse, um die es geht - alles andere ist ein anderer Befund.
PFADFEHLER = re.compile(r'Failed opening required|failed to open stream', re.I)
FATAL = re.compile(r'\bFatal error\b|\bParse error\b', re.I)

# Verdaechtiges Muster, auch wenn der Lauf durchgeht: aus dem eigenen Ordner
# heraus ueber eine feste Zahl von ".." in einen FREMDEN Baum greifen.
#
# ERWEITERT 31.08.2026. Bis dahin verlangte das Muster das Wort "webfrontend"
# hinter dirname(__DIR__) - es traf damit nur die Richtung bin/ -> Web-Baum.
# Die haeufigere Richtung sah es nicht:
#
#     webfrontend/html/index.php:     dirname(__DIR__) . '/htmlauth/xx_lib.php'
#     webfrontend/htmlauth/index.php: dirname(__DIR__) . '/html/xx_lib.php'
#
# Genau diese Zeile hat Heimkino, SignalBot und die Ecowitt-Weiche getroffen -
# installiert liegen html/ und htmlauth/ in getrennten Baeumen, und der Pfad
# zeigt dann auf .../html/plugins/htmlauth/, das es nicht gibt.
#
# DIE UNTERSCHEIDUNG, die Richtig von Falsch trennt, ist das Wort "plugins":
#
#     falsch   dirname(__DIR__) . '/htmlauth/xx_lib.php'
#     richtig  dirname(dirname(dirname(__DIR__))) . '/html/plugins/' . basename(__DIR__) . '/xx_lib.php'
#
# Die installierte Lage traegt IMMER eine plugins-Ebene. Ein Pfad ohne sie
# meint den Archivbau. Das ist gemessen, nicht geraten: alle Kandidatenlisten
# des Bestands schreiben plugins aus.
BAEUME = r'webfrontend|htmlauth|html|bin|templates'
VERDACHT = re.compile(
    r'(?:require|include)(?:_once)?\s*\(?[^;]{0,200}?'
    r'dirname\s*\('                       # mindestens ein dirname(
    r'[^;]{0,120}?__DIR__'                # ... um __DIR__ herum
    r'[^;]{0,200}?'
    r'[\'"]/(?:' + BAEUME + r')/',        # und dann quer in einen fremden Baum
    re.I)
# Traegt der Ausdruck eine plugins-Ebene, meint er die INSTALLIERTE Lage und
# ist richtig. Geprueft wird je Fundstelle, nicht je Datei - eine Datei darf
# eine richtige und eine falsche Zeile zugleich haben.
#
# UND ZWAR AM GANZEN AUSDRUCK, nicht am Treffer. Das Suchmuster endet am ersten
# Baumnamen ('/html/), die plugins-Ebene steht erst dahinter. Der erste Anlauf
# am 31.08.2026 prueste nur den Treffer und meldete deshalb die RICHTIGE
# installierte Form als Hinweis - ein Fehlalarm an genau der Stelle, an der das
# Werkzeug schweigen soll. Der Messwert war richtig, der Auswerter nicht.
INSTALLIERTE_LAGE = re.compile(r'\bplugins\b', re.I)


# Zweite Musterklasse, ergaenzt 31.08.2026.
#
# Nicht jeder Pfad quer durch die Baeume steht in einem require. MGiSmart 1.1.6
# baut ihn in eine Variable und liest die Datei danach:
#
#     $datei = dirname(__DIR__) . '/htmlauth/index.php';
#     if (!is_file($datei)) { return 2; }        // 2 = "nicht feststellbar"
#
# Installiert liegt die Bibliothek in webfrontend/html/plugins/<ordner>/; ein
# dirname fuehrt auf webfrontend/html/plugins/htmlauth/. Die Datei gibt es
# dort nicht, und DREI Selbstpruefungen stehen auf jedem echten Geraet
# dauerhaft auf "nicht feststellbar" - drei Striche, die sich beim
# Ueberfliegen wie Haken lesen. Genau die Klasse, gegen die die Selbstpruefung
# gebaut war.
#
# DIE TRENNSCHAERFE IST GEMESSEN, NICHT GESCHAETZT. Ueber 51 Linien:
#     jeder Baumwechsel                                133 Fundstellen
#     ohne plugins-Ebene und ohne Feld/array/foreach    24
#     zusaetzlich ohne Kommentare                       19
# Die 114 uebergangenen sind fast alle das LETZTE Glied einer Kandidatenliste
# - also der ausdruecklich vorgesehene Rueckfall auf die Archivlage. Ein
# Werkzeug, das die alle meldet, wird nach dem dritten Mal nicht mehr gelesen.
VERDACHT_PFAD = re.compile(
    r'dirname\s*\([^;\n]{0,120}?__DIR__[^;\n]{0,200}?'
    r'[\'"]/(?:' + BAEUME + r')/', re.I)
# Ein zweiter Weg im selben Ausdruck: das Glied einer Kandidatenliste, ein
# Feldeintrag, eine foreach-Schleife. Dann ist der Pfad ein Rueckfall und
# kein einziger Weg.
ZWEITER_WEG = re.compile(r'\[\s*\]\s*=|\barray\s*\(|=>|\bas\s+\$')

# Und der zweite Weg muss keine Liste sein. Die haeufigere Form im Bestand ist
# ein Rueckfall in zwei Schritten:
#
#     $datei = ap_paths()['bindir'] . '/apc_themen.json';   // installiert
#     if (!is_file($datei)) {
#         $datei = dirname(dirname(__DIR__)) . '/bin/apc_themen.json';  // Archiv
#     }
#
# Das ist voellig richtig gebaut. Der erste Anlauf am 31.08.2026 hat es
# trotzdem gemeldet - eine Schaerfung, die eine neue Fehlalarmklasse erzeugt,
# ist keine Verbesserung. Gemessen wurden zwei Stichproben an der Primaerquelle
# (APC-UPS ap_lib.php:422, AnkerSolix ak_lib.php:1143); beide waren Rueckfaelle.
#
# Erkannt wird die Form daran, dass KURZ DAVOR auf Vorhandensein geprueft wird.
# Wirkung ueber den ganzen Bestand gemessen:
#     jeder Baumwechsel                                    133
#     ohne plugins-Ebene                                    92
#     ohne Feld/array/foreach                               24
#     ohne gefuehrten Rueckfall und ohne Kommentare          4
VORHER_GEPRUEFT = re.compile(r'\b(is_file|file_exists|is_readable|is_dir)\s*\(', re.I)

# Dieselbe Form, nur andersherum geschrieben: der Baumwechsel steht ZUERST,
# der Rueckfall dahinter.
#     $t = dirname(__DIR__) . '/html/tafel.php';
#     if (!is_file($t)) { $t = db_paths()['home'] . '/webfrontend/html/...'; }
# Das ist ein zweiter Weg und kein Befund. Entscheidend ist NICHT, dass eine
# Pruefung folgt - das tun auch die Faelle, die aufgeben (return 2, '') -,
# sondern dass der Fehlzweig DIESELBE Variable noch einmal belegt.
# Geeicht an drei bekannten Stellen: Dashboard db_test.php:157 belegt neu
# (Ausnahme), MGiSmart mg_lib.php:2542 und Weissware ww_test.php:137 geben
# auf (bleiben Befund).
NACHHER_ERSETZT_VAR = re.compile(r'^\s*(\$\w+)\s*=(?!=)')


def nachher_ersetzt(text, ende, ganz):
    """Wird die zugewiesene Variable im gefuehrten Fehlzweig neu belegt?"""
    v = NACHHER_ERSETZT_VAR.match(ganz)
    if not v:
        return False
    fenster = text[ende:ende + 300]
    if not VORHER_GEPRUEFT.search(fenster):
        return False
    return re.search(re.escape(v.group(1)) + r'\s*=(?!=)', fenster) is not None


def ohne_kommentare(t):
    """Kommentare durch Leerzeichen ersetzen - LAENGENTREU.

    Zeichenketten bleiben stehen: in ihnen steht der Pfad, um den es geht.
    Die Laenge und jeder Zeilenumbruch bleiben erhalten, damit die
    Zeilennummern der Fundstellen weiter stimmen - ein Maskierer, der die
    Zeilenzahl verschiebt, laesst jede Fundstelle auf die falsche Stelle
    zeigen.
    """
    aus = []
    i, n = 0, len(t)
    while i < n:
        c = t[i]
        if c in '"\'':
            j = i + 1
            while j < n:
                if t[j] == '\\':
                    j += 2
                    continue
                if t[j] == c:
                    break
                j += 1
            aus.append(t[i:j + 1])
            i = j + 1
        elif t.startswith('/*', i):
            j = t.find('*/', i + 2)
            j = n if j < 0 else j + 2
            aus.append(''.join(ch if ch == '\n' else ' ' for ch in t[i:j]))
            i = j
        elif t.startswith('//', i) or c == '#':
            j = t.find('\n', i)
            j = n if j < 0 else j
            aus.append(' ' * (j - i))
            i = j
        else:
            aus.append(c)
            i += 1
    return ''.join(aus)


def _anweisung(text, ab):
    """Der ganze Ausdruck ab der Fundstelle bis zum naechsten Semikolon.

    Ohne Semikolon (letzte Zeile einer Datei) bis zum Zeilenende - und
    hoechstens 400 Zeichen, damit eine Datei ohne Semikolon nicht die ganze
    Datei als eine Anweisung liest.
    """
    ende = text.find(';', ab)
    if ende < 0 or ende - ab > 400:
        ende = text.find('\n', ab)
    if ende < 0:
        ende = min(len(text), ab + 400)
    return text[ab:ende]


# Der Vorlauf fuer den zweiten Anlauf. Er setzt KEINE Fehlerstufen und
# unterdrueckt nichts - er schreibt nur, was am Ende wirklich schiefging.
# Die Meldung traegt den Wortlaut von PHP ("Failed opening required '...'"),
# damit die vorhandene Auswertung sie ohne Sonderfall erkennt.
VORLAUF_PHP = '''<?php
register_shutdown_function(function () {
    $l = error_get_last();
    if ($l && in_array($l['type'], array(E_ERROR, E_PARSE, E_COMPILE_ERROR, E_CORE_ERROR), true)) {
        fwrite(STDERR, "\\nFatal error: " . $l['message']
            . " in " . $l['file'] . " on line " . $l['line'] . "\\n");
    }
});
'''


def php_binaer():
    for k in PHP_KANDIDATEN:
        if not k:
            continue
        try:
            r = subprocess.run([k, '-v'], capture_output=True, timeout=20)
            if r.returncode == 0:
                return k
        except (OSError, subprocess.SubprocessError):
            continue
    return None


def plugin_ordner(p):
    """FOLDER aus der plugin.cfg - nicht aus dem Verzeichnisnamen raten.

    Der Verzeichnisname traegt die Fassungsnummer; LoxBerry legt das Plugin
    aber unter FOLDER ab. Wer vom einen auf den andere schliesst, prueft eine
    Lage, die es so nie gibt.
    """
    cfg = Path(p) / 'plugin.cfg'
    if cfg.is_file():
        for zl in cfg.read_text(encoding='utf-8', errors='replace').splitlines():
            m = re.match(r'^\s*FOLDER\s*=\s*(\S+)', zl)
            if m:
                return m.group(1).strip()
    return re.sub(r'^LoxBerry-Plugin-|-[0-9.]+$', '', Path(p).name).lower()


HIER = Path(__file__).resolve().parent
KERN = HIER / 'lb_attrappe'      # loxberry_system.php, _web.php, _io.php, _log.php


def attrappe_bauen(quelle, ordner, ziel):
    """Die Baeume dorthin legen, wo plugininstall.pl sie hinlegt.

    Der LoxBerry-Kern kommt aus `Werkzeuge/lb_attrappe/` - er MUSS mit hinein.
    Beim ersten Durchlauf am 16.08.2026 fehlte er, und jedes Plugin, das
    `require_once 'loxberry_system.php'` schreibt, wurde als Befund gemeldet:
    20 von 25 Treffern waren Fehlalarme des Werkzeugs, nicht Fehler der
    Plugins. Ein Werkzeug, das man erst nachrechnen muss, ist keins.
    """
    quelle, ziel = Path(quelle), Path(ziel)
    if KERN.is_dir():
        shutil.copytree(KERN, ziel, dirs_exist_ok=True)
    lagen = [
        ('bin', 'bin/plugins/' + ordner),
        ('webfrontend/html', 'webfrontend/html/plugins/' + ordner),
        ('webfrontend/htmlauth', 'webfrontend/htmlauth/plugins/' + ordner),
        ('templates', 'templates/plugins/' + ordner),
    ]
    for von, nach in lagen:
        q = quelle / von
        if q.is_dir():
            shutil.copytree(q, ziel / nach, dirs_exist_ok=True)
    for d in ('config/plugins/' + ordner, 'log/plugins/' + ordner,
              'data/plugins/' + ordner, 'config/system', 'libs/phplib'):
        (ziel / d).mkdir(parents=True, exist_ok=True)
    # Ein Gateway-Abschnitt, damit die MQTT-Zweige nicht schon an der
    # fehlenden Datei aussteigen und den eigentlichen Pfad nie erreichen.
    # Bringt die Kern-Attrappe eine general.json mit, gilt ihre.
    gj = ziel / 'config/system/general.json'
    if not gj.is_file():
        gj.write_text('{"Mqtt":{"Udpinport":"11884","Gatewayautostart":1},'
                      '"Webserver":{"Port":80}}', encoding='utf-8')
    return ziel


def umgebung(lb, ordner):
    u = dict(os.environ)
    u['LBHOMEDIR'] = str(lb)
    u['LBPPLUGINDIR'] = ordner
    u['LBPCONFIGDIR'] = str(lb / 'config/plugins' / ordner)
    u['LBPLOGDIR'] = str(lb / 'log/plugins' / ordner)
    u['LBPDATADIR'] = str(lb / 'data/plugins' / ordner)
    u['LBPBINDIR'] = str(lb / 'bin/plugins' / ordner)
    u['LBPHTMLDIR'] = str(lb / 'webfrontend/html/plugins' / ordner)
    u['LBPHTMLAUTHDIR'] = str(lb / 'webfrontend/htmlauth/plugins' / ordner)
    u['LBPTEMPLATEDIR'] = str(lb / 'templates/plugins' / ordner)
    # Netz ins Leere leiten: die Skripte sollen ihre Bibliotheken finden,
    # nicht bei einer fremden Schnittstelle anklopfen.
    for k in ('http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY'):
        u[k] = 'http://127.0.0.1:9'
    return u


CODE_BAEUME = ('/bin/plugins/', '/webfrontend/html/plugins/',
               '/webfrontend/htmlauth/plugins/', '/templates/plugins/')
DATEN_BAEUME = ('/config/plugins/', '/data/plugins/', '/log/plugins/')


def lage_befund(gesucht):
    """Ist die fehlende Datei ein Befund ueber die INSTALLATIONSLAGE?

    Nur dann, wenn ein Skript aus einem eigenen Pfad heraus (also mit
    __DIR__/dirname) eine Datei in einem der CODE-Baeume sucht und dort
    danebengreift. Alles andere sagt nichts ueber die Lage:

    * ein relativer Name (loxberry_io.php, phpMQTT/phpMQTT.php) wird ueber den
      include_path gesucht - fehlt er, ist die Attrappe unvollstaendig, nicht
      das Plugin falsch gebaut;
    * eine Datei unter config/, data/ oder log/ entsteht erst beim Einrichten
      und fehlt in einer frischen Attrappe zu Recht.

    Diese Unterscheidung ist am 16.08.2026 entstanden, nachdem der erste
    Durchlauf 25 Treffer meldete, von denen 22 Fehlalarme des Werkzeugs waren.
    """
    g = (gesucht or '').replace('\\', '/')
    if g in ('', '?'):
        return False
    if not (g.startswith('/') or re.match(r'^[A-Za-z]:/', g)):
        return False                       # ueber include_path gesucht
    if any(t in g for t in DATEN_BAEUME):
        return False                       # Konfiguration, keine Bibliothek
    return any(t in g for t in CODE_BAEUME)


def warum_kein_befund(gesucht):
    g = (gesucht or '').replace('\\', '/')
    if not (g.startswith('/') or re.match(r'^[A-Za-z]:/', g)):
        return 'ueber include_path gesucht, Kern-Attrappe unvollstaendig'
    if any(t in g for t in DATEN_BAEUME):
        return 'Konfigurations- oder Datendatei, entsteht erst beim Einrichten'
    return 'liegt ausserhalb der Plugin-Baeume'


def _einmal(php, datei, u, grenze, vorlauf=None):
    """Ein Aufruf. Rueckgabe: (Ausgabe, Rueckgabewert).

    Der Rueckgabewert ist der Teil, der bei einem schweigenden Skript als
    einziger noch etwas sagt. Eine Zeitueberschreitung gilt NICHT als Fehler:
    ein Dauerlaeufer, der lauscht, ist genau das, was er sein soll - er
    bekommt deshalb 0.
    """
    argv = [php, '-d', 'display_errors=1', '-d', 'error_reporting=E_ALL',
            '-d', 'max_execution_time=15',
            '-d', 'include_path=.' + os.pathsep + u.get('LBHOMEDIR', '') + '/libs/phplib']
    if vorlauf:
        # Der Wert hinter -d wird als ini-Zeile gelesen. Eine kurze
        # Windows-Form mit Tilde (C:\Users\BENUTZ~1\...) bricht dort den
        # Parser: "PHP:  syntax error, unexpected '~'". Der Vorlauf wird dann
        # STILL nicht geladen, und der zweite Anlauf haette wieder nichts
        # gemessen - der blinde Fleck waere nur verschoben.
        # Gemessen am 17.08.2026 durch subprocess: kurz+unquotiert scheitert
        # (rc=255, "Failed to open stream"), quotiert traegt, realpath()
        # traegt ebenfalls. Beides zusammen kostet nichts.
        argv += ['-d', 'auto_prepend_file="%s"' % os.path.realpath(str(vorlauf))]
    argv.append(str(datei))
    try:
        r = subprocess.run(argv, capture_output=True, text=True, encoding='utf-8',
                           errors='replace', env=u, cwd=str(Path(datei).parent),
                           timeout=grenze)
        return (r.stdout or '') + (r.stderr or ''), r.returncode
    except subprocess.TimeoutExpired:
        return '<<Zeitueberschreitung nach %d s>>' % grenze, 0
    except OSError as e:
        return '<<konnte nicht gestartet werden: %s>>' % e, 0


def lauf(php, datei, u, grenze=25, vorlauf=None):
    """Ausgabe eines Aufrufs - und zwar auch die, die das Skript verschweigt.

    Bricht der Lauf ab (Rueckgabewert ungleich 0), hat aber nichts Lesbares
    hinterlassen, wird er mit dem Vorlauf wiederholt. Alles andere bleibt beim
    Alten: wer ohnehin redet, wird kein zweites Mal aufgerufen.
    """
    aus, rc = _einmal(php, datei, u, grenze)
    if rc != 0 and vorlauf and not (PFADFEHLER.search(aus) or FATAL.search(aus)):
        nach, _rc2 = _einmal(php, datei, u, grenze, vorlauf)
        if nach.strip():
            aus = (aus + '\n' + nach).strip()
        else:
            # Auch das ist eine Auskunft: abgebrochen, und niemand sagt warum.
            aus = (aus + '\nFatal error: Abbruch ohne Meldung, Rueckgabewert %d '
                         '(display_errors abgeschaltet?)' % rc).strip()
    return aus


def pruefe(pfad, php):
    """Rueckgabe: (gemessen, Pfadbefunde, Meldungen, unmessbar, Ausnahmen).

    `gemessen` zaehlt nur die Dateien, bei denen der Aufruf wirklich zu Ende
    gekommen ist. Eine Zeitueberschreitung ist KEIN bestandener Lauf - sie ist
    ein nicht durchgefuehrter, und sie zaehlt seit dem 31.08.2026 getrennt.
    Vorher stand sie in derselben Zahl wie ein sauberer Lauf, und eine Linie
    voller Zeitueberschreitungen las sich wie eine geprueste.
    """
    quelle = Path(pfad)
    ordner = plugin_ordner(quelle)
    befunde, sonst, unmessbar, ausnahmen = [], [], [], []
    angesehen = 0

    tmp = Path(tempfile.mkdtemp(prefix='lage_'))
    try:
        lb = attrappe_bauen(quelle, ordner, tmp / 'lb')
        u = umgebung(lb, ordner)
        # Liegt im Wegwerf-Ordner und verschwindet mit ihm.
        vorlauf = tmp / 'vorlauf_lage.php'
        vorlauf.write_text(VORLAUF_PHP, encoding='utf-8')
        for zweig in ('bin/plugins/' + ordner,
                      'webfrontend/html/plugins/' + ordner,
                      'webfrontend/htmlauth/plugins/' + ordner):
            d = lb / zweig
            if not d.is_dir():
                continue
            for f in sorted(d.rglob('*.php')):
                aus = lauf(php, f, u, vorlauf=vorlauf)
                kurz = zweig.split('/plugins/')[0] + '/' + f.name
                if aus.startswith('<<'):
                    # Zeitueberschreitung oder gar nicht gestartet. Das ist
                    # keine Aussage ueber den Prueflig - es ist die Abwesenheit
                    # einer Aussage.
                    unmessbar.append('%s: %s' % (kurz, aus.strip('<>')))
                    continue
                angesehen += 1
                if PFADFEHLER.search(aus):
                    gesucht = ''
                    m = re.search(r"required '([^']+)'", aus) or \
                        re.search(r'\(([^()]*\.php)\)', aus)
                    if m:
                        gesucht = m.group(1)
                    befunde.append((kurz, gesucht or '?')) if lage_befund(gesucht) \
                        else sonst.append('%s findet %s nicht - %s'
                                          % (kurz, gesucht or '?', warum_kein_befund(gesucht)))
                elif FATAL.search(aus):
                    zeile = next((z.strip() for z in aus.splitlines()
                                  if FATAL.search(z)), aus.strip()[:160])
                    sonst.append('%s: %s' % (kurz, zeile[:160]))

        # ------------------------------------------------------------------
        # Zweite, TEXTLICHE Sicht: das Muster selbst, auch wenn der Lauf
        # durchging.
        #
        # WARUM SIE GEBRAUCHT WIRD - und warum sie mehr als bin/ sehen muss.
        # Der Lauf oben findet den Pfadfehler nur, wenn die require-Zeile beim
        # Aufruf auch WIRKLICH ausgefuehrt wird. Ein Endpunkt nach Hausstandard
        # tut genau das nicht: er prueft zuerst das Token, weist ohne Token mit
        # 403 ab und steigt aus - die fehlerhafte Zeile darunter wird nie
        # erreicht. Der Lauf endet mit Rueckgabewert 0 und einer sauberen
        # Antwort, und das Werkzeug meldete "in Ordnung".
        #
        # Am 31.08.2026 an einem Eichstand nachgestellt: eine html/index.php
        # mit Tokenpruefung und einer falschen require-Zeile dahinter ergab
        # "3 Dateien, in Ordnung", Rueckgabewert 0, KEINE Zusatzzeile. Am
        # Geraet bricht dieselbe Datei mit HTTP 500 und leerem Rumpf ab.
        #
        # Bis dahin durchsuchte diese Sicht ausschliesslich bin/ - also
        # ausgerechnet nicht den Baum, in dem die Klasse zuletzt dreimal
        # aufgetreten ist (Heimkino, SignalBot, Ecowitt-Weiche).
        # ------------------------------------------------------------------
        for zweig in ('bin', 'webfrontend/html', 'webfrontend/htmlauth'):
            d = quelle / zweig
            if not d.is_dir():
                continue
            for f in sorted(d.rglob('*.php')):
                roh = f.read_text(encoding='utf-8', errors='replace')
                t = ohne_kommentare(roh)
                gemeldet = set()

                # (a) Ein require/include, das quer in einen fremden Baum greift.
                for m in VERDACHT.finditer(t):
                    stelle = _anweisung(t, m.start())
                    zeile = t.count('\n', 0, m.start()) + 1
                    if INSTALLIERTE_LAGE.search(stelle):
                        # Der Ausdruck nennt die plugins-Ebene und meint damit
                        # die installierte Lage. Kein Befund - aber gezaehlt
                        # und genannt, denn eine stille Ausnahme ist dasselbe
                        # Uebel wie ein Fehlalarm, nur in der anderen Richtung.
                        gemeldet.add(zeile)
                        ausnahmen.append('%s/%s:%d nennt die plugins-Ebene '
                                         '(installierte Lage, richtig)'
                                         % (zweig, f.name, zeile))
                        continue
                    gemeldet.add(zeile)
                    sonst.append('%s/%s:%d laedt mit dirname(__DIR__) aus einem '
                                 'fremden Baum, ohne plugins-Ebene - im Archiv '
                                 'richtig, installiert nicht'
                                 % (zweig, f.name, zeile))

                # (b) Ein Pfad quer in einen fremden Baum, der KEIN Glied einer
                #     Kandidatenliste ist - also der einzige Weg. Er muss nicht
                #     in einem require stehen; er wird oft nur gelesen.
                for m in VERDACHT_PFAD.finditer(t):
                    zeile = t.count('\n', 0, m.start()) + 1
                    if zeile in gemeldet:
                        continue
                    stelle = _anweisung(t, m.start())
                    anf = max(t.rfind(';', 0, m.start()), t.rfind('{', 0, m.start()),
                              t.rfind('}', 0, m.start())) + 1
                    ganz = t[anf:anf + len(stelle) + (m.start() - anf)]
                    if INSTALLIERTE_LAGE.search(ganz):
                        ausnahmen.append('%s/%s:%d nennt die plugins-Ebene '
                                         '(installierte Lage, richtig)'
                                         % (zweig, f.name, zeile))
                        continue
                    if ZWEITER_WEG.search(ganz):
                        ausnahmen.append('%s/%s:%d ist ein Glied einer '
                                         'Kandidatenliste (Rueckfall, richtig)'
                                         % (zweig, f.name, zeile))
                        continue
                    if VORHER_GEPRUEFT.search(t[max(0, m.start() - 250):m.start()]):
                        ausnahmen.append('%s/%s:%d ist ein gefuehrter Rueckfall '
                                         '- kurz davor wird auf Vorhandensein '
                                         'geprueft (richtig)'
                                         % (zweig, f.name, zeile))
                        continue
                    if nachher_ersetzt(t, m.start() + len(stelle), ganz):
                        ausnahmen.append('%s/%s:%d ist ein gefuehrter Rueckfall '
                                         '- der Fehlzweig belegt dieselbe '
                                         'Variable neu (richtig)'
                                         % (zweig, f.name, zeile))
                        continue
                    gemeldet.add(zeile)
                    sonst.append('%s/%s:%d baut mit dirname(__DIR__) einen Pfad '
                                 'quer in einen fremden Baum - ohne plugins-Ebene '
                                 'und ohne zweiten Weg. Installiert zeigt er ins '
                                 'Leere.' % (zweig, f.name, zeile))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return angesehen, befunde, sonst, unmessbar, ausnahmen


def main():
    php = php_binaer()
    if php is None:
        print('Kein PHP gefunden. Ueber PHP84= bzw. PHP74= einen Pfad angeben.')
        return 2

    zeige_ausnahmen = '--ausnahmen' in sys.argv[1:]
    namen = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not namen:
        namen = sorted(str(p) for p in Path('.').iterdir()
                       if p.is_dir() and p.name.startswith('LoxBerry-Plugin-'))
    if not namen:
        print('Keine Plugin-Ordner gefunden.')
        return 2

    print('Interpreter: %s' % php)
    print('Aufbau: getrennte Baeume wie auf dem installierten LoxBerry\n')
    schlecht = 0
    gesamt_dateien = 0
    gesamt_unmessbar = 0
    gesamt_ausnahmen = 0
    for n in namen:
        if not Path(n).is_dir():
            print('%-46s uebersprungen (kein Ordner)' % Path(n).name)
            continue
        anz, befunde, sonst, unmessbar, ausnahmen = pruefe(n, php)
        gesamt_dateien += anz
        gesamt_unmessbar += len(unmessbar)
        gesamt_ausnahmen += len(ausnahmen)
        # Die Zahl der nicht messbaren Dateien gehoert in DIESELBE Zeile wie
        # das Urteil. Ein Lauf, der die Haelfte nicht messen konnte, darf sich
        # nicht wie ein vollstaendiger lesen.
        rest = (', %d nicht messbar' % len(unmessbar)) if unmessbar else ''
        if ausnahmen:
            rest += ', %d Ausnahme(n)' % len(ausnahmen)
        if befunde:
            schlecht += 1
            print('%-46s %d Dateien%s, %d BEFUND(E)'
                  % (Path(n).name, anz, rest, len(befunde)))
            for kurz, gesucht in befunde:
                print('   ! %s findet seine Bibliothek nicht' % kurz)
                print('     gesucht: ' + str(gesucht))
        elif anz == 0:
            # "0 von 0 ist in Ordnung" ist kein Haken, sondern ein Strich.
            print('%-46s NICHTS GEMESSEN (0 Dateien%s)' % (Path(n).name, rest))
        else:
            print('%-46s %d Dateien%s, in Ordnung' % (Path(n).name, anz, rest))
        for s in sonst[:8]:
            print('   . ' + s)
        for s in unmessbar[:4]:
            print('   - nicht messbar: ' + s)
        if ausnahmen and zeige_ausnahmen:
            for s in ausnahmen:
                print('   ~ Ausnahme: ' + s)

    print('\n%d Linien geprueft, %d Dateien aufgerufen, %d mit Pfadbefund.'
          % (len(namen), gesamt_dateien, schlecht))
    if gesamt_unmessbar:
        print('%d Datei(en) konnten NICHT gemessen werden - sie zaehlen weder '
              'als bestanden noch als Befund.' % gesamt_unmessbar)
    if gesamt_ausnahmen:
        print('%d Fundstelle(n) als Ausnahme gewertet - installierte Lage '
              'oder Glied einer Kandidatenliste.%s'
              % (gesamt_ausnahmen,
                 '' if zeige_ausnahmen else ' Mit --ausnahmen einzeln ansehen.'))
    print('Die mit "." gekennzeichneten Zeilen sind keine Befunde dieser '
          'Klasse - ansehen muss man sie trotzdem.')
    return 1 if schlecht else 0


if __name__ == '__main__':
    sys.exit(main())
