#!/usr/bin/env python3
"""Eichung von wirkungstest.py an gebauten Oberflaechen, Erwartung vorher fest.

    W1 ms4h      Knoepfe ms4h_suchen (zuerst) und speichern; speichern verliert
                 das Aktionstoken                       -> Befund "Knopf speichern"
    W2 gut       dasselbe Formular, speichern behaelt alles -> ok, 2 Absendungen
    W3 verz      W2 ueber --verz=<ordner> <name> statt Pfad -> ok
    W3b ohne     --verz auf einen Ordner, den es nicht gibt -> Rueckgabe 2
    W4 fatal     speichern ruft eine unbekannte Funktion (Rueckgabewert 255),
                 Konfiguration bleibt                   -> Befund "Rueckgabewert 255"
    W5 puffer    GET legt data/.../endpunkt.json an, speichern loescht ihn
                 (Pruefpuffer, Ausnahme PRUEFPUFFER)      -> ok
    W6 puffer+   wie W5, speichern loescht zusaetzlich die Konfiguration
                                                        -> Befund VERSCHWUNDEN probe.json,
                                                           keine Zeile zu endpunkt.json
    W7 neu       speichern legt endpunkt.json NEU an      -> Befund "NEU angelegt: endpunkt.json"
    W8 beinahe   speichern loescht data/.../zustand.json  -> Befund "VERSCHWUNDEN: zustand.json"

Jede Probe-Oberflaeche liegt in einem Wegwerfordner; was sie in der Attrappe
des Werkzeugs (<werkzeugordner>/lb) anlegt, wird danach entfernt. Gegen
Werkzeuge/wirkungstest.py gerufen, schreibt sie in die GEMEINSAME Attrappe
Werkzeuge/lb (Ordner wteich_*); ein gleichzeitiger Wirkungstest eines anderen
sieht das als "[liegt in wteich_..., nicht im erwarteten Ordner]". Wer nicht
allein arbeitet, eicht eine Kopie mit eigener lb/ (Muster:
Pruefung-Nachtpruefung-2026-11-12/werkzeuge/wt/).

    python -B wirkungstest_eichung.py WERKZEUG.py

Rueckgabe 0: alle Erwartungen erfuellt; 1: Abweichung; 2: nicht messbar.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

KOPF = r'''<?php
$cd = getenv('LBPCONFIGDIR'); @mkdir($cd, 0777, true);
$dd = getenv('LBPDATADIR');   @mkdir($dd, 0777, true);
$f = $cd . '/probe.json';
if (!is_file($f)) { file_put_contents($f, json_encode(array('name' => 'a', 'aktionstoken' => 'abc123'))); }
$c = json_decode(file_get_contents($f), true);
/* Wie ein Plugin nach Hausstandard: fehlt das Token, entsteht es beim Ansehen
 * neu. Sonst ginge es schon im Einlauf des Werkzeugs verloren, und die
 * Messung danach haette nichts mehr zu verlieren. */
if (is_array($c) && !array_key_exists('aktionstoken', $c) && $_SERVER['REQUEST_METHOD'] !== 'POST') {
    $c['aktionstoken'] = 'abc123'; file_put_contents($f, json_encode($c));
}
'''
FORM = r'''
echo str_repeat("<!-- Fuellzeile fuer die Mindestlaenge der Seite -->\n", 6);
echo '<form method="post"><input type="text" name="name" value="' . htmlspecialchars($c['name']) . '">'
   . '<button name="ms4h_suchen" value="1">Suchen</button>'
   . '<button name="speichern" value="1">Speichern</button></form>';
'''

PROBEN = {
    'wteich_ms4h': KOPF + r'''
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['speichern'])) { file_put_contents($f, json_encode(array('name' => $_POST['name']))); }
    header('Location: index.php'); exit;
}''' + FORM,
    'wteich_gut': KOPF + r'''
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['speichern'])) { $c['name'] = $_POST['name']; file_put_contents($f, json_encode($c)); }
    header('Location: index.php'); exit;
}''' + FORM,
    'wteich_fatal': KOPF + r'''
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['speichern'])) { gibt_es_nicht_eichung(); }
    header('Location: index.php'); exit;
}''' + FORM,
    'wteich_puffer': KOPF + r'''
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['speichern'])) { $c['name'] = $_POST['name']; file_put_contents($f, json_encode($c)); @unlink($dd . '/endpunkt.json'); }
    header('Location: index.php'); exit;
}
if (!is_file($dd . '/endpunkt.json')) { file_put_contents($dd . '/endpunkt.json', json_encode(array('ok' => 1, 'text' => 'ok'))); }
''' + FORM,
    'wteich_pufferplus': KOPF + r'''
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['speichern'])) { @unlink($dd . '/endpunkt.json'); @unlink($f); }
    header('Location: index.php'); exit;
}
if (!is_file($dd . '/endpunkt.json')) { file_put_contents($dd . '/endpunkt.json', json_encode(array('ok' => 1, 'text' => 'ok'))); }
''' + FORM,
    'wteich_neu': KOPF + r'''
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['speichern'])) { @unlink($dd . '/endpunkt.json'); }
    if (isset($_POST['ms4h_suchen'])) { file_put_contents($dd . '/endpunkt.json', json_encode(array('ok' => 1, 'n' => mt_rand()))); }
    header('Location: index.php'); exit;
}''' + FORM,
    'wteich_beinahe': KOPF + r'''
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['speichern'])) { @unlink($dd . '/zustand.json'); }
    header('Location: index.php'); exit;
}
if (!is_file($dd . '/zustand.json')) { file_put_contents($dd . '/zustand.json', json_encode(array('z' => 1))); }
''' + FORM,
}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    werkzeug = Path(sys.argv[1]).resolve()
    if not werkzeug.is_file():
        print('NICHT MESSBAR: %s fehlt' % werkzeug)
        return 2
    lb = werkzeug.parent / 'lb'
    tmp = Path(tempfile.mkdtemp(prefix='wteich_'))
    u = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    erg = {}
    try:
        for name, php in PROBEN.items():
            d = tmp / name / 'webfrontend' / 'htmlauth'
            d.mkdir(parents=True)
            (d / 'index.php').write_text(php, encoding='utf-8')

        def ruf(args):
            r = subprocess.run([sys.executable, '-B', str(werkzeug)] + args, cwd=str(tmp),
                               capture_output=True, text=True, encoding='utf-8',
                               errors='replace', env=u, timeout=600)
            return r.returncode, r.stdout + r.stderr
        for name in PROBEN:
            erg[name] = ruf([str(tmp / name)])
        erg['verz'] = ruf(['--verz=' + str(tmp), 'wteich_gut'])
        erg['ohne'] = ruf(['--verz=' + str(tmp / 'gibt_es_nicht'), 'wteich_gut'])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        for b in ('config', 'data', 'log', 'templates'):
            for name in PROBEN:
                shutil.rmtree(lb / b / 'plugins' / name, ignore_errors=True)

    def hat(name, muster):
        return re.search(muster, erg[name][1], re.M) is not None

    pruef = [
        ('W1 ms4h: Befund am Knopf speichern', erg['wteich_ms4h'][0] == 1
         and hat('wteich_ms4h', r"Knopf speichern\): probe\.json: /aktionstoken\s+'abc123' -> None")),
        ('W2 gut: ok, 2 Absendungen', erg['wteich_gut'][0] == 0
         and hat('wteich_gut', r'wteich_gut\s+ok \(2 Absendungen')),
        ('W3 --verz=: ok', erg['verz'][0] == 0 and hat('verz', r'wteich_gut\s+ok \(2 Absendungen')),
        ('W3b --verz fehlt: Rueckgabe 2', erg['ohne'][0] == 2),
        ('W4 fatal: Befund Rueckgabewert 255', erg['wteich_fatal'][0] == 1
         and hat('wteich_fatal', r'Knopf speichern\): Absenden endet mit Rueckgabewert 255')),
        ('W5 Puffer weg: ok', erg['wteich_puffer'][0] == 0
         and hat('wteich_puffer', r'wteich_puffer\s+ok \(2 Absendungen')),
        ('W6 Puffer + Konfiguration weg: nur Konfiguration', erg['wteich_pufferplus'][0] == 1
         and hat('wteich_pufferplus', r'VERSCHWUNDEN: probe\.json')
         and not hat('wteich_pufferplus', r'endpunkt\.json')),
        ('W7 Puffer neu angelegt: Befund', erg['wteich_neu'][0] == 1
         and hat('wteich_neu', r'NEU angelegt: endpunkt\.json')),
        ('W8 anderer Name verschwunden: Befund', erg['wteich_beinahe'][0] == 1
         and hat('wteich_beinahe', r'VERSCHWUNDEN: zustand\.json')),
    ]
    schlecht = 0
    for name, ok in pruef:
        print('  [%s] %s' % ('ok ' if ok else 'ROT', name))
        schlecht += 0 if ok else 1
    print('%d Erwartungen, %d erfuellt, %d abweichend (Werkzeug %s)'
          % (len(pruef), len(pruef) - schlecht, schlecht, werkzeug))
    if '--zeigen' in sys.argv:
        for k, (rc, t) in erg.items():
            print('--- %s rc=%d\n%s' % (k, rc, t.strip()))
    return 1 if schlecht else 0


if __name__ == '__main__':
    sys.exit(main())
