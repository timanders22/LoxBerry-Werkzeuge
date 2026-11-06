#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Eichung von `reiterlauf.py` - in beide Richtungen, Erwartung vorher fest.

Gebaut wird eine winzige Oberflaeche im Kratzordner, einmal heil und dann mit
je einem eingebauten Schaden. Jede Prueflinie des Werkzeugs muss an ihrem
Schaden anschlagen und an der heilen Fassung schweigen.

Der siebte Fall eicht den Vorgabewert fuer `REQUEST_METHOD`, den
`vorlauf_getpost.php` seit 13.09.2026 setzt: dieselbe heile Oberflaeche einmal
mit dem ausgelieferten Vorlauf (muss schweigen) und einmal mit einem
„nackten", den diese Eichung sich selbst in den Kratzordner schreibt und der
den Wert wieder wegnimmt (muss auf JEDEM Reiter einen Scheinbefund melden).
Der nackte Vorlauf wird hier gebaut und nicht aus dem Bestand geholt - sonst
haenge die Eichung daran, was eine andere Datei gerade tut.

    python3 reiterlauf_eichung.py
Rueckgabe 0 = alle Faelle wie erwartet, 1 = ein Fall nicht, 2 = kein PHP.
Schreibt in einen eigenen Kratzordner und in den Pruefstand unter `lb/`;
beides wird am Ende aufgeraeumt.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
WERKZEUG = HIER / 'reiterlauf.py'
PY = sys.executable or 'python3'

# Die Konsole dieses Rechners ist cp1252: eine Ausgabe mit Umlauten aus
# einem Unterprozess braeche den Lauf sonst mit UnicodeEncodeError ab.
try:
    sys.stdout.reconfigure(errors='replace')
except (AttributeError, ValueError):
    pass
NAME = 'Eichung-Reiterlauf-0.0.1'

KOPF = """<?php
// Winzige Oberflaeche fuer die Eichung. Sie liest REQUEST_METHOD absichtlich
// OHNE isset() - genau so, wie es eine echte Oberflaeche tut, und genau
// daran haengt der siebte Fall.
$reiter = array('alpha', 'beta', 'gamma');
$form = isset($_GET['form']) ? (string) $_GET['form'] : 'alpha';
if (!in_array($form, $reiter, true)) { $form = 'alpha'; }
$ist_post = ($_SERVER['REQUEST_METHOD'] === 'POST');
echo "<h1>Eichung</h1>";
echo '<a href="index.php?form=alpha">alpha</a>';
echo '<a href="index.php?form=beta">beta</a>';
echo '<a href="index.php?form=gamma">gamma</a>';
"""

FUELL = "str_repeat('Ein Satz mit genug Zeichen. ', 40)"

# Die heile Fassung: der angeforderte Reiter ist der offene.
HEIL = KOPF + """
foreach ($reiter as $r) {
    $k = ($r === $form) ? 'sm-seite sm-active' : 'sm-seite';
    echo '<div class="' . $k . '" id="tab-' . $r . '">' . %s . '</div>';
}
""" % FUELL

# Schaden 1: $_GET wird uebergangen - immer der erste Reiter offen.
GET_EGAL = KOPF + """
foreach ($reiter as $r) {
    $k = ($r === 'alpha') ? 'sm-seite sm-active' : 'sm-seite';
    echo '<div class="' . $k . '" id="tab-' . $r . '">' . %s . '</div>';
}
""" % FUELL

# Schaden 2: kein Reiter offen - ohne JavaScript unbedienbar.
KEIN_OFFEN = KOPF + """
foreach ($reiter as $r) {
    echo '<div class="sm-seite" id="tab-' . $r . '">' . %s . '</div>';
}
""" % FUELL

# Schaden 3: ein Sprachschluessel steht unaufgeloest am Bildschirm.
ROHER_SCHLUESSEL = KOPF + """
foreach ($reiter as $r) {
    $k = ($r === $form) ? 'sm-seite sm-active' : 'sm-seite';
    echo '<div class="' . $k . '" id="tab-' . $r . '">EINST.SICH_FEHLEND ' . %s . '</div>';
}
""" % FUELL

# Schaden 4: die Seite liefert fast nichts.
ZU_KURZ = KOPF + """
echo '<div class="sm-seite sm-active" id="tab-alpha">kurz</div>';
"""

# Schaden 5: keine Reiterverweise - es gibt nichts zu messen.
OHNE_REITER = """<?php
echo "<h1>Eichung</h1>";
echo '<div class="sm-seite sm-active" id="tab-alpha">""" + "x" * 600 + """</div>';
"""


# Der "nackte" Vorlauf der Gegenprobe: er bindet den ausgelieferten ein und
# nimmt genau das eine wieder weg, worum es geht. So misst der Fall den
# Vorgabewert und nicht nebenbei noch das Fuellen von $_GET.
NACKT = ('<?php\n'
         "require '%s';\n"
         "unset($_SERVER['REQUEST_METHOD']);\n")


def nackter_vorlauf(wurzel):
    p = wurzel / 'vorlauf_nackt.php'
    p.write_bytes((NACKT % (HIER / 'vorlauf_getpost.php').as_posix()).encode('utf-8'))
    return p


def oberflaeche(wurzel, quelltext):
    d = wurzel / NAME / 'webfrontend' / 'htmlauth'
    d.mkdir(parents=True, exist_ok=True)
    (d / 'index.php').write_bytes(quelltext.encode('utf-8'))
    (wurzel / NAME / 'webfrontend' / 'html').mkdir(parents=True, exist_ok=True)


def ruf(wurzel, *zusatz):
    p = subprocess.run([PY, '-B', str(WERKZEUG), str(wurzel / NAME),
                        '--sprachen', 'de'] + list(zusatz),
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace',
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def aufraeumen():
    for zweig in ('config', 'data', 'log'):
        shutil.rmtree(HIER / 'lb' / zweig / 'plugins' / NAME.lower(), ignore_errors=True)
    shutil.rmtree(HIER / 'lb' / 'reiterlauf' / ('%s_de' % NAME), ignore_errors=True)


def main():
    sys.path.insert(0, str(HIER))
    import rendern
    da = [v for v, p in rendern.PHPS if Path(p).is_file()]
    if not da:
        print('KEIN PHP bereit - nichts gemessen.')
        return 2
    print('PHP-Fassungen bereit: %s' % ', '.join(da))
    je_lauf = len(da) * 3   # drei Reiter

    kratz = Path(tempfile.mkdtemp(prefix='reiterlauf_eichung_'))
    fehl = 0

    def pruefe(name, quelltext, erwartet_rc, erwartet_text, zusatz=()):
        nonlocal fehl
        oberflaeche(kratz, quelltext)
        rc, aus = ruf(kratz, *zusatz)
        ok = (rc == erwartet_rc and erwartet_text in aus)
        print('%-4s %-42s rc=%d (erwartet %d), "%s" %s'
              % ('ok' if ok else 'FEHL', name, rc, erwartet_rc, erwartet_text,
                 'gefunden' if erwartet_text in aus else 'FEHLT'))
        if not ok:
            fehl += 1
            print(aus)
        return aus

    try:
        aus = pruefe('heil - MUSS schweigen', HEIL, 0, '0 Befund(e)')
        if ('%d Lauf/Laeufe' % je_lauf) not in aus:
            print('FEHL  heil: es wurden nicht %d Laeufe gemacht' % je_lauf)
            fehl += 1

        pruefe('$_GET uebergangen', GET_EGAL, 1, 'OFFEN IST alpha, ANGEFORDERT WAR beta')
        pruefe('kein Reiter offen', KEIN_OFFEN, 1, 'KEIN REITER OFFEN')
        pruefe('roher Sprachschluessel im HTML', ROHER_SCHLUESSEL, 1,
               'UNAUFGELOESTE SCHLUESSEL: EINST.SICH_FEHLEND')
        pruefe('Ausgabe zu kurz', ZU_KURZ, 1, 'AUSGABE ZU KURZ')
        pruefe('keine Reiterverweise', OHNE_REITER, 2, 'kein Reiter gefunden')

        # Siebter Fall: die Gegenprobe zum Vorgabewert.
        aus = pruefe('ohne Vorgabewert - MUSS melden', HEIL, 1,
                     'REQUEST_METHOD',
                     zusatz=('--vorlauf', str(nackter_vorlauf(kratz))))
        # und zur Sicherheit noch einmal heil, damit klar ist, dass der
        # Unterschied am Vorlauf hing und nicht an der Reihenfolge der Faelle
        pruefe('wieder mit vorlauf_getpost.php', HEIL, 0, '0 Befund(e)')

        # Achter Fall: gibt es die Oberflaeche gar nicht, ist das kein
        # sauberer Lauf - und kein "in Ordnung".
        shutil.rmtree(kratz / NAME / 'webfrontend', ignore_errors=True)
        (kratz / NAME).mkdir(parents=True, exist_ok=True)
        rc, aus = ruf(kratz)
        ok = (rc == 2 and 'keine webfrontend/htmlauth/index.php' in aus)
        print('%-4s %-42s rc=%d (erwartet 2)'
              % ('ok' if ok else 'FEHL', 'keine Oberflaeche vorhanden', rc))
        if not ok:
            fehl += 1
            print(aus)
    finally:
        shutil.rmtree(kratz, ignore_errors=True)
        aufraeumen()

    print('%d Fall/Faelle nicht wie erwartet' % fehl)
    return 1 if fehl else 0


if __name__ == '__main__':
    sys.exit(main())
