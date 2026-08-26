#!/usr/bin/env python3
"""Rendert eine Plugin-Oberflaeche in der INSTALLIERTEN Lage, nicht im Archiv.

WARUM ES DIESES WERKZEUG GIBT
-----------------------------
Am 23.08.2026 lief die Ecowitt-Weiche im Pruefstand unter PHP 7.4 und 8.4
fehlerfrei durch - und auf der Anlage kam HTTP 500. Der Grund war eine einzige
Zeile:

    require_once dirname(__DIR__) . '/html/ew_lib.php';

Im Archiv liegt

    <plugin>/webfrontend/htmlauth/index.php
    <plugin>/webfrontend/html/ew_lib.php

und die Zeile trifft. Installiert liegt aber

    $LB/webfrontend/htmlauth/plugins/<ordner>/index.php
    $LB/webfrontend/html/plugins/<ordner>/ew_lib.php

und dieselbe Zeile zeigt auf .../htmlauth/plugins/html/ew_lib.php - eine Datei,
die es nicht gibt. Zwischen beiden Lagen liegt genau EINE Stufe, und rendern.py
kennt nur die erste. Es hat den Fehler also nicht uebersehen, sondern
BESTAETIGT.

Dieses Werkzeug baut die zweite Lage nach: es legt die Dateien dorthin, wo der
Installer sie hinlegt, und ruft die Oberflaeche einmal MIT und einmal OHNE die
LBP*-Umgebungsvariablen auf. Ohne sie, weil ein Notnagel, der nie geprueft
wird, kein Notnagel ist - sondern eine Zeile, von der man glaubt, sie trage.

Rein lesend fuer den Plugin-Ordner: gearbeitet wird auf einer Kopie.

Aufruf:  installationslage_rendern.py <pluginordner> [<pluginname>]
         Der Name ist der FOLDER aus plugin.cfg; ohne Angabe wird er dort
         nachgelesen.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
LB_VORLAGE = HIER / 'lb'
VORLAUF = HIER / 'vorlauf.php'
PHPS = [('7.4', r'C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe'),
        ('8.4', r'C:\tmp\php-8.4.24-Win32-vs17-x64\php.exe')]


def ordnername(plugin: Path) -> str:
    cfg = plugin / 'plugin.cfg'
    if cfg.is_file():
        m = re.search(r'^FOLDER=(.+)$', cfg.read_text(encoding='utf-8', errors='replace'),
                      re.M)
        if m:
            return m.group(1).strip()
    return plugin.name.lower()


def aufbauen(plugin: Path, ordner: str, ziel: Path) -> Path:
    """Legt die Dateien dorthin, wo plugininstall.pl sie hinlegt."""
    lb = ziel / 'loxberry'
    if LB_VORLAGE.is_dir():
        shutil.copytree(LB_VORLAGE, lb)
    else:
        lb.mkdir(parents=True)
    umzug = [
        ('webfrontend/htmlauth', 'webfrontend/htmlauth/plugins/' + ordner),
        ('webfrontend/html', 'webfrontend/html/plugins/' + ordner),
        ('templates', 'templates/plugins/' + ordner),
        ('bin', 'bin/plugins/' + ordner),
        ('cron', 'system/cron'),
    ]
    for quelle, nach in umzug:
        q = plugin / quelle
        if not q.is_dir():
            continue
        z = lb / nach
        z.parent.mkdir(parents=True, exist_ok=True)
        if z.exists():
            shutil.rmtree(z)
        shutil.copytree(q, z)
    for teil in ('config/plugins/' + ordner, 'log/plugins/' + ordner,
                 'data/plugins/' + ordner):
        (lb / teil).mkdir(parents=True, exist_ok=True)
    return lb


def lauf(php: str, lb: Path, ordner: str, mit_umgebung: bool):
    datei = lb / 'webfrontend' / 'htmlauth' / 'plugins' / ordner / 'index.php'
    umg = dict(os.environ)
    # Alles Alte wegraeumen, damit ein vergessener Rest nicht die Antwort gibt.
    for k in list(umg):
        if k.startswith('LBP') or k == 'LBHOMEDIR':
            del umg[k]
    umg['LBHOMEDIR'] = str(lb)
    if mit_umgebung:
        umg['LBPPLUGINDIR'] = ordner
        umg['LBPCONFIGDIR'] = str(lb / 'config/plugins' / ordner)
        umg['LBPLOGDIR'] = str(lb / 'log/plugins' / ordner)
        umg['LBPDATADIR'] = str(lb / 'data/plugins' / ordner)
        umg['LBPHTMLAUTHDIR'] = str(datei.parent)
        umg['LBPHTMLDIR'] = str(lb / 'webfrontend/html/plugins' / ordner)
        umg['LBPTEMPLATEDIR'] = str(lb / 'templates/plugins' / ordner)
        umg['LBPBINDIR'] = str(lb / 'bin/plugins' / ordner)
    befehl = [php, '-n',
              '-d', 'include_path=.;' + str(lb / 'libs' / 'phplib'),
              '-d', 'display_errors=0', '-d', 'error_reporting=32767',
              '-d', 'date.timezone=Europe/Berlin',
              '-d', 'extension_dir=' + str(Path(php).parent / 'ext'),
              '-d', 'extension=curl', '-d', 'extension=openssl',
              '-d', 'extension=mbstring', '-d', 'extension=sockets',
              '-d', 'extension=fileinfo']
    if VORLAUF.is_file():
        befehl[2:2] = ['-d', 'auto_prepend_file=' + str(VORLAUF)]
    befehl.append(str(datei))
    r = subprocess.run(befehl, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', cwd=str(datei.parent), env=umg, timeout=90)
    befunde = []
    if '###BEFUNDE###' in r.stderr:
        befunde = [z for z in r.stderr.split('###BEFUNDE###', 1)[1].strip().splitlines()
                   if z.strip()]
    rest = r.stderr.split('###BEFUNDE###')[0].strip()
    return r.stdout, befunde, rest


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    plugin = Path(sys.argv[1]).resolve()
    if not plugin.is_dir():
        print('Kein Ordner: %s' % plugin)
        return 2
    ordner = sys.argv[2] if len(sys.argv) > 2 else ordnername(plugin)

    tmp = Path(tempfile.mkdtemp(prefix='instlage_'))
    schlecht = 0
    try:
        lb = aufbauen(plugin, ordner, tmp)
        print('Installationslage aufgebaut unter %s' % lb)
        print('  Oberflaeche : webfrontend/htmlauth/plugins/%s/index.php' % ordner)
        print('  Unterbau    : webfrontend/html/plugins/%s/' % ordner)
        print('')
        for mit in (True, False):
            wie = 'mit LBP*-Variablen' if mit else 'OHNE LBP*-Variablen (Notnagel)'
            for v, php in PHPS:
                if not Path(php).is_file():
                    continue
                try:
                    out, bef, rest = lauf(php, lb, ordner, mit)
                except subprocess.TimeoutExpired:
                    print('[FEHL] %-4s %-32s ZEITUEBERSCHREITUNG' % (v, wie))
                    schlecht += 1
                    continue
                mangel = []
                if bef:
                    mangel += bef
                if rest:
                    mangel.append('STDERR: ' + rest[:200])
                if len(out) < 500:
                    mangel.append('Ausgabe zu kurz (%d Zeichen)' % len(out))
                # Der haeufigste Fall: die Oberflaeche steht, aber der Unterbau
                # fehlt. Ohne diese Zeile saehe eine lesbare Fehlerseite wie ein
                # gelungener Aufbau aus.
                if 'nicht gefunden' in out and 'Unterbau' in out:
                    mangel.append('Unterbau nicht gefunden (Ersatzseite)')
                # Der LoxBerry-Rahmen. Wer class_exists('LBWeb') abfragt, ohne
                # libs/phplib/loxberry_web.php einzubinden, bekommt IMMER
                # falsch - Kopf und Fuss entfallen dann stillschweigend, und
                # die Seite erscheint auf der Anlage ohne Menue. Gemessen am
                # 23.08.2026 an der Ecowitt-Weiche 0.9.1: der Prueflauf war
                # gruen, die Seite stand allein im Netz.
                if '<!-- lbheader' not in out:
                    mangel.append('kein LoxBerry-Kopf (lbheader) - Seite ohne Menue')
                if '<!-- lbfooter' not in out:
                    mangel.append('kein LoxBerry-Fuss (lbfooter)')
                for schluessel in re.findall(r'\b(?:TEXT|REITER|LEGENDE|FELD)\.[A-Z_]+', out):
                    mangel.append('unuebersetzter Schluessel ' + schluessel)
                    break
                if mangel:
                    schlecht += 1
                    print('[FEHL] %-4s %-32s %d Zeichen' % (v, wie, len(out)))
                    for m in mangel[:6]:
                        print('         %s' % m)
                else:
                    print('[OK]   %-4s %-32s %d Zeichen' % (v, wie, len(out)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('')
    print('In Ordnung.' if not schlecht else '%d Laeufe mit Befund.' % schlecht)
    return 0 if not schlecht else 1


if __name__ == '__main__':
    sys.exit(main())
