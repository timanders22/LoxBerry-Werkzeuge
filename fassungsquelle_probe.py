# -*- coding: utf-8 -*-
"""Misst, welche Fassung eine Linie im INSTALLIERTEN Zustand von sich nennt.

Aufruf:
    python3 Werkzeuge/fassungsquelle_probe.py ORDNER BAUM LIB FUNKTION
      ORDNER    Plugin-Ordner im Arbeitsordner
      BAUM      html oder htmlauth - wo die Bibliothek installiert liegt
      LIB       Name der Bibliotheksdatei (z. B. mt_lib.php)
      FUNKTION  Name der Fassungsfunktion (z. B. mt_fassung)

Rueckgabe 0, wenn beide Lagen die erwartete Antwort geben; 1 sonst; 2, wenn
nichts zu messen war.

WARUM ES DIESEN STAND GIBT
--------------------------
`plugininstall.pl` installiert die `plugin.cfg` NIRGENDWOHIN. Eine Linie, die
ihre Fassung nur aus Dateien liest, nennt auf einer Installation gar keine.
Im Arbeitsordner faellt das nie auf: dort trifft der Archivfall jeder
Kandidatenliste (`dirname(dirname(__DIR__))/plugin.cfg`).

ZWEI LAGEN, UND BEIDE MUESSEN STIMMEN
-------------------------------------
  L1 INSTALLIERT   drei getrennte Baeume, KEINE plugin.cfg, dafuer eine
                   plugindatabase.json mit einer unmoeglichen Nummer
                   (9.9.9-probe). Erwartet: genau diese Nummer.
  L2 ARCHIV        der Auspackordner: plugin.cfg an ihrer Stelle, KEINE
                   plugindatabase.json. Erwartet: die Nummer aus der Datei
                   (1.1.1-ausdatei).

L2 ist nicht Beiwerk. Eine Berichtigung, die L1 heilt und dabei L2 zerstoert,
nimmt der Freigabepruefung im Arbeitsordner die Fassungsangabe weg.

DIE ATTRAPPE DES SDK
--------------------
`Werkzeuge/lb/libs/phplib/loxberry_system.php` gibt in `pluginversion()` ein
FESTES '9.9.9' zurueck - damit sieht jede Linie heil aus, auch eine kaputte.
Dieser Stand bringt deshalb eine eigene, kleine Nachbildung mit, die sich wie
das Geraet verhaelt: sie liest `data/system/plugindatabase.json` und sucht
ueber `$lbpplugindir`. Vorbild ist `loxberry_system.php:403` auf dem Geraet
(LoxBerry 4.0.0.15).

GEEICHT AM GERAET (07.09.2026)
-----------------------------
Fuer die installierten Linien stimmt die Antwort dieses Standes mit der am
Geraet gemessenen ueberein:
    marstekvenus  Geraet EIGEN=[]        Stand L1 leer      -> BEFUND
    spotpreis     Geraet EIGEN=[]        Stand L1 leer      -> BEFUND
    bewaesserung  Geraet EIGEN=[]        Stand L1 leer      -> BEFUND
    pumpenwacht   Geraet EIGEN=[0.9.13]  Stand L1 9.9.9-probe -> in Ordnung
    smartmeter    Geraet EIGEN=[2.8.0]   Stand L1 9.9.9-probe -> in Ordnung

WAS DIESER STAND NICHT MISST
----------------------------
Kein echtes Update, keinen Browser, kein Geraet. Er baut die Lage nach, die
das Installationsprotokoll und `plugininstall.pl` belegen.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
ARBEIT = HIER.parent
QUELL_LB = HIER / 'lb'
PHPS = [r'C:\tmp\php-8.4.27-Win32-vs17-x64\php.exe',
        r'C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe']
# BERICHTIGT 07.09.2026: die Probenummern tragen KEINEN Zusatz mehr.
# Mit '1.1.1-ausdatei' meldete dieser Stand aWATTar und VolkswagenID
# faelschlich als Befund - ihre Muster lassen nur Ziffern und Punkte zu
# (/^VERSION=([0-9][0-9.]*)$/), und die Probe scheiterte am Zusatz, nicht
# am Pfad. Wer den Pfad messen will, darf nicht am Muster haengenbleiben.
# (Dass eine Fassung wie 2.1.7-beta von diesen Mustern gekuerzt wuerde,
#  ist eine eigene, kleinere Frage - hier nicht gemessen.)
DB_NUMMER = '9.9.9'
CFG_NUMMER = '7.7.7'

SDK_NACHBILDUNG = """<?php
/* Nachbildung des LoxBerry-SDK, so weit dieser Stand es braucht.
 * Vorbild: /opt/loxberry/libs/phplib/loxberry_system.php:403 (4.0.0.15) -
 * pluginversion() geht ueber plugindata() in die plugindatabase.json und
 * sucht ueber $lbpplugindir. Die Attrappe unter Werkzeuge/lb gibt dort ein
 * festes '9.9.9' zurueck; damit waere jede Linie heil. */
class LBSystem
{
    public static function plugindata($query = '')
    {
        $home = getenv('LBHOMEDIR');
        $ordner = $query !== '' ? $query : (getenv('LBPPLUGINDIR') ?: '');
        if (!$home || !$ordner) { return null; }
        $roh = @file_get_contents($home . '/data/system/plugindatabase.json');
        if ($roh === false) { return null; }
        $d = @json_decode($roh, true);
        if (!is_array($d)) { return null; }
        $liste = isset($d['plugins']) && is_array($d['plugins']) ? $d['plugins'] : $d;
        foreach ($liste as $e) {
            if (is_array($e) && isset($e['folder'])
                && (string) $e['folder'] === (string) $ordner) {
                return array(
                    'PLUGINDB_TITLE'   => isset($e['title']) ? $e['title'] : '',
                    'PLUGINDB_VERSION' => isset($e['version']) ? $e['version'] : '',
                    'PLUGINDB_FOLDER'  => $e['folder'],
                );
            }
        }
        return null;
    }

    public static function pluginversion($query = '')
    {
        $p = self::plugindata($query);
        return isset($p['PLUGINDB_VERSION']) ? $p['PLUGINDB_VERSION'] : null;
    }
}
"""


def php_finden():
    for p in PHPS:
        if Path(p).is_file():
            return p
    return None


def lage_bauen(wurzel, plugin, ordner, lage):
    """lage: 'installiert' oder 'archiv'. Gibt (lb, umgebung) zurueck."""
    if wurzel.exists():
        shutil.rmtree(wurzel, ignore_errors=True)
    lb = wurzel / 'lb'
    shutil.copytree(QUELL_LB, lb)
    # Die feste 9.9.9-Antwort der Attrappe muss weg, sonst misst sie sich selbst.
    (lb / 'libs' / 'phplib' / 'ic_sdk_probe.php').write_text(
        SDK_NACHBILDUNG, encoding='utf-8')

    for teil in ('config/plugins', 'data/plugins', 'log/plugins'):
        (lb / teil / ordner).mkdir(parents=True, exist_ok=True)

    if lage == 'installiert':
        # Verteilen wie plugininstall.pl: drei Baeume, keine plugin.cfg.
        for quelle, ziel in (('webfrontend/htmlauth', 'webfrontend/htmlauth/plugins/' + ordner),
                             ('webfrontend/html', 'webfrontend/html/plugins/' + ordner),
                             ('templates', 'templates/plugins/' + ordner),
                             ('bin', 'bin/plugins/' + ordner)):
            q = plugin / quelle
            if not q.is_dir():
                continue
            zt = lb / ziel
            if zt.exists():
                shutil.rmtree(zt)
            zt.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(q, zt)
        pdb = lb / 'data/system/plugindatabase.json'
        pdb.parent.mkdir(parents=True, exist_ok=True)
        pdb.write_text(json.dumps({'plugins': {'aa': {
            'name': ordner, 'folder': ordner, 'title': 'Probe',
            'version': DB_NUMMER, 'interface': '2.0'}}}), encoding='utf-8')
    else:
        # Auspackordner: alles unter einem Dach, plugin.cfg an ihrer Stelle,
        # KEINE Datenbank.
        zt = lb / 'auspack' / ordner
        shutil.copytree(plugin, zt)
        (zt / 'plugin.cfg').write_text(
            '# Kommentar mit Raute - PHPs INI-Zerleger stolpert darueber\n'
            '[PLUGIN]\nVERSION=' + CFG_NUMMER + '\nTITLE=Probe\n', encoding='utf-8')
        pdb = lb / 'data/system/plugindatabase.json'
        if pdb.is_file():
            pdb.unlink()

    umg = dict(os.environ)
    umg['LBHOMEDIR'] = str(lb)
    umg['LBPPLUGINDIR'] = ordner
    umg['LBPCONFIGDIR'] = str(lb / 'config/plugins' / ordner)
    umg['LBPLOGDIR'] = str(lb / 'log/plugins' / ordner)
    umg['LBPDATADIR'] = str(lb / 'data/plugins' / ordner)
    return lb, umg


def messen(php, wurzel, lb, umg, libpfad, funktion):
    treiber = wurzel / 'probe.php'
    lib = str(libpfad).replace(os.sep, '/')
    sdk = str(lb / 'libs' / 'phplib' / 'ic_sdk_probe.php').replace(os.sep, '/')
    treiber.write_text(
        "<?php\n"
        "$lbpplugindir = getenv('LBPPLUGINDIR');\n"
        "require_once '" + sdk + "';\n"
        "require_once '" + lib + "';\n"
        "echo function_exists('" + funktion + "')\n"
        "     ? (string) @" + funktion + "() : '(FUNKTION FEHLT)';\n",
        encoding='utf-8')
    r = subprocess.run(
        [php, '-n', '-d', 'include_path=.;' + str(lb / 'libs' / 'phplib'),
         '-d', 'display_errors=0', '-d', 'error_reporting=0',
         '-d', 'date.timezone=Europe/Berlin',
         '-d', 'extension_dir=' + str(Path(php).parent / 'ext'),
         '-d', 'extension=curl', '-d', 'extension=mbstring', '-d', 'extension=gd',
         '-d', 'extension=sockets', '-d', 'extension=openssl', '-d', 'extension=fileinfo',
         str(treiber)],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        env=umg, cwd=str(libpfad.parent), timeout=90)
    return (r.stdout or '').strip().splitlines()[-1] if (r.stdout or '').strip() else ''


def main():
    if len(sys.argv) < 5:
        print(__doc__.split('WARUM')[0])
        return 2
    ordnername, baum, lib, funktion = sys.argv[1:5]
    plugin = (ARBEIT / ordnername).resolve()
    if not plugin.is_dir():
        print('Kein Plugin-Ordner: %s' % plugin)
        return 2
    php = php_finden()
    if not php:
        print('Kein PHP gefunden.')
        return 2
    # BERICHTIGT 07.09.2026: der Ordnername kommt aus der plugin.cfg der
    # Linie, nicht aus einem erfundenen 'pruefling'. Grund, gemessen:
    # hk_paths()['plugin'] faellt auf den festen Namen 'heimkino' zurueck.
    # Unter 'pruefling' fand Heimkino seinen Eintrag in der Datenbank
    # nicht - der Stand meldete einen Befund, den es nicht gibt.
    ordner = 'pruefling'
    m = re.search(r'^\s*FOLDER\s*=\s*(\S+)', 
                  (plugin / 'plugin.cfg').read_text(encoding='utf-8',
                                                    errors='replace'), re.M | re.I)
    if m:
        ordner = m.group(1).strip().strip('"').strip("'")
    print('   (Ordnername aus plugin.cfg: %s)' % ordner)
    wurzel = Path(tempfile.gettempdir()) / 'fassungsprobe'

    print('== %s  (%s/%s, %s)' % (ordnername, baum, lib, funktion))
    ergebnis = []

    lb, umg = lage_bauen(wurzel, plugin, ordner, 'installiert')
    p = lb / 'webfrontend' / baum / 'plugins' / ordner / lib
    ist = messen(php, wurzel, lb, umg, p, funktion) if p.is_file() else '(LIB FEHLT)'
    ok1 = (ist == DB_NUMMER)
    ergebnis.append(ok1)
    print('   L1 installiert (keine plugin.cfg): [%s]   %s'
          % (ist, 'in Ordnung' if ok1 else 'BEFUND - erwartet war ' + DB_NUMMER))

    lb, umg = lage_bauen(wurzel, plugin, ordner, 'archiv')
    p = lb / 'auspack' / ordner / 'webfrontend' / baum / lib
    ist = messen(php, wurzel, lb, umg, p, funktion) if p.is_file() else '(LIB FEHLT)'
    ok2 = (ist == CFG_NUMMER)
    ergebnis.append(ok2)
    print('   L2 Auspackordner (keine Datenbank): [%s]   %s'
          % (ist, 'in Ordnung' if ok2 else 'BEFUND - erwartet war ' + CFG_NUMMER))

    shutil.rmtree(wurzel, ignore_errors=True)
    return 0 if all(ergebnis) else 1


if __name__ == '__main__':
    sys.exit(main())
