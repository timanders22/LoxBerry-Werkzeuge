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

WAS ES NICHT TUT
Es ersetzt den Test am Geraet nicht. Es beantwortet eine einzige Frage:
findet jedes Skript seine Bibliotheken auch dann, wenn die Baeume getrennt
sind? Netzzugriffe werden ueber einen unerreichbaren Proxy ins Leere geleitet
und die Konfiguration bleibt leer, damit die Skripte frueh aussteigen.

AUFRUF
    python3 Werkzeuge/installationslage_pruefen.py [<plugin-ordner> ...]

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
    os.environ.get('PHP84') or r'C:\tmp\php-8.4.24-Win32-vs17-x64\php.exe',
    os.environ.get('PHP74') or r'C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe',
    'php',
]

# Die Klasse, um die es geht - alles andere ist ein anderer Befund.
PFADFEHLER = re.compile(r'Failed opening required|failed to open stream', re.I)
FATAL = re.compile(r'\bFatal error\b|\bParse error\b', re.I)

# Verdaechtiges Muster, auch wenn der Lauf durchgeht: aus bin/ heraus ueber
# eine feste Zahl von ".." in den Web-Baum greifen.
VERDACHT = re.compile(r'(?:require|include)(?:_once)?\s*\(?\s*dirname\s*\(\s*__DIR__\s*\)'
                      r'[^;]*webfrontend', re.I)


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
    """Rueckgabe: (Zahl angesehener Dateien, Pfadbefunde, sonstige Meldungen)."""
    quelle = Path(pfad)
    ordner = plugin_ordner(quelle)
    befunde, sonst = [], []
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
                angesehen += 1
                aus = lauf(php, f, u, vorlauf=vorlauf)
                kurz = zweig.split('/plugins/')[0] + '/' + f.name
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

        # Zweite, billige Sicht: das Muster selbst, auch wenn der Lauf durchging.
        for f in sorted((quelle / 'bin').rglob('*.php')) if (quelle / 'bin').is_dir() else []:
            t = f.read_text(encoding='utf-8', errors='replace')
            if VERDACHT.search(t) and 'abf_kandidaten' not in t and 'kandidaten' not in t.lower():
                sonst.append('bin/%s greift mit dirname(__DIR__) in den Web-Baum '
                             '(im Archiv richtig, installiert nicht)' % f.name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return angesehen, befunde, sonst


def main():
    php = php_binaer()
    if php is None:
        print('Kein PHP gefunden. Ueber PHP84= bzw. PHP74= einen Pfad angeben.')
        return 2

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
    for n in namen:
        if not Path(n).is_dir():
            print('%-46s uebersprungen (kein Ordner)' % Path(n).name)
            continue
        anz, befunde, sonst = pruefe(n, php)
        gesamt_dateien += anz
        if befunde:
            schlecht += 1
            print('%-46s %d Dateien, %d BEFUND(E)' % (Path(n).name, anz, len(befunde)))
            for kurz, gesucht in befunde:
                print('   ! %s findet seine Bibliothek nicht' % kurz)
                print('     gesucht: ' + str(gesucht))
        else:
            print('%-46s %d Dateien, in Ordnung' % (Path(n).name, anz))
        for s in sonst[:8]:
            print('   . ' + s)

    print('\n%d Linien geprueft, %d Dateien aufgerufen, %d mit Pfadbefund.'
          % (len(namen), gesamt_dateien, schlecht))
    print('Die mit "." gekennzeichneten Zeilen sind keine Befunde dieser '
          'Klasse - ansehen muss man sie trotzdem.')
    return 1 if schlecht else 0


if __name__ == '__main__':
    sys.exit(main())
