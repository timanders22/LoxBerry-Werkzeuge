#!/usr/bin/env python3
"""Eichung von oberflaeche_sprachfaehig.py: schreibt es nur, wenn es soll?

Elf Faelle mit vorher feststehender Erwartung, jeder in einem eigenen
Wegwerfordner unter dem Temporaerordner. Gemessen wird die WIRKUNG: Liste und
Prueffsumme jeder Datei im Ordner vorher und nachher, nicht der Text der
Ausgabe. Der Rueckgabewert wird zusaetzlich gehalten.

    python -B oberflaeche_sprachfaehig_eichung.py [WERKZEUG.py]

Ohne Argument: Werkzeuge/oberflaeche_sprachfaehig.py neben diesem Skript
bzw. im Arbeitsordner. Mit --gegenprobe baut die Eichung je Wache eine Fassung
OHNE diese Wache (Anker muss genau einmal vorkommen) und verlangt, dass dann
genau der zugehoerige Fall rot wird - sonst prueft der Fall die Wache nicht.

Rueckgabe 0: alle Faelle wie erwartet (und mit --gegenprobe: jede entfernte
Wache macht ihren Fall rot); 1: Abweichung; 2: nicht messbar (kein PHP,
Werkzeug fehlt, Anker nicht eindeutig).
"""
import hashlib
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

sys.dont_write_bytecode = True

HIER = Path(__file__).resolve().parent
PHP = None
for k in (os.environ.get('PHP84'), r'C:\tmp\php-8.4.27-Win32-vs17-x64\php.exe'):
    if k and os.path.isfile(k):
        PHP = k
        break

SEITE_LF = (
    "<?php\n"
    "$L = parse_ini_file(__DIR__ . '/language_de.ini', true);\n"
    "if ($a > $b && $c < 5) { echo 1; }\n"
    "?>\n"
    "<h1>Einstellungen speichern</h1>\n"
    "<p>Hier stehen die Zugangsdaten</p>\n"
    "<p>/opt/loxberry/config</p>\n"
)
SEITE_OHNE_TEXT = (
    "<?php\n$x = 1;\n?>\n<p>/opt/loxberry/config</p>\n<p>12:30</p>\n"
)
INI = '[ALT]\nA = "b"\n'
INI_MIT_UI = '[UI]\nK001 = "schon da"\n'


def abbild(d):
    aus = {}
    for w, _, fs in os.walk(d):
        for f in fs:
            p = os.path.join(w, f)
            aus[os.path.relpath(p, d)] = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    return aus


def ordner(seite, ini=INI, crlf=False):
    d = Path(tempfile.mkdtemp(prefix='osf_'))
    s = seite.replace('\n', '\r\n') if crlf else seite
    (d / 'index.php').write_bytes(s.encode('utf-8'))
    if ini is not None:
        (d / 'language_de.ini').write_bytes(ini.encode('utf-8'))
    return d


def aufruf(werkzeug, args, cwd, umgebung=None):
    u = dict(os.environ)
    u['PYTHONDONTWRITEBYTECODE'] = '1'
    if umgebung:
        u.update(umgebung)
    r = subprocess.run([sys.executable, '-B', str(werkzeug)] + args, cwd=str(cwd),
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', env=u, timeout=120)
    return r.returncode, r.stdout + r.stderr


def im_prozess(werkzeug, args, cwd, patch):
    """Werkzeug als Modul laden, `patch(modul)` anwenden, main() rufen."""
    spec = importlib.util.spec_from_file_location('osf_pruefling', str(werkzeug))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    # m.subprocess IST das Modul subprocess dieses Prozesses - wer run() dort
    # ersetzt, ersetzt es fuer alle folgenden Faelle mit. Deshalb zurueck.
    echt_run = subprocess.run
    patch(m)
    alt_argv, alt_cwd = sys.argv, os.getcwd()
    puffer = io.StringIO()
    try:
        sys.argv = [str(werkzeug)] + args
        os.chdir(str(cwd))
        with redirect_stdout(puffer):
            try:
                rc = m.main()
            except Exception as e:          # ein Absturz ist ein eigener Ausgang
                rc = 'Ausnahme %s' % type(e).__name__
    finally:
        sys.argv = alt_argv
        os.chdir(alt_cwd)
        subprocess.run = echt_run
    return rc, puffer.getvalue()


def ohne_php(m):
    m.php_binaer = lambda: None


def php_l_haengt(m):
    echt = m.subprocess.run

    def run(argv, *a, **k):
        if '-l' in argv:
            raise m.subprocess.TimeoutExpired(argv, 60)
        return echt(argv, *a, **k)
    m.subprocess.run = run
    m.php_binaer = lambda: PHP


def falsches_php(m):
    """php -l meldet einen Parsefehler, egal was in der Datei steht."""
    echt = m.subprocess.run

    class R:
        returncode = 255
        stdout = 'PHP Parse error:  syntax error (Eichung) in x on line 1'
        stderr = ''

    def run(argv, *a, **k):
        if '-l' in argv:
            return R()
        return echt(argv, *a, **k)
    m.subprocess.run = run
    m.php_binaer = lambda: PHP


def faelle(werkzeug):
    """Liste (Name, Erwartung, Ergebnis-Text, gut?)."""
    aus = []

    def halte(name, erwartung, d, rc, text, soll_rc, soll_geschrieben, pruef=None):
        nach = abbild(d)
        geschrieben = nach != vorher_abbild[0]
        ok = (rc == soll_rc) and (geschrieben == soll_geschrieben)
        zusatz = ''
        if ok and pruef is not None:
            ok, zusatz = pruef(d)
        aus.append((name, erwartung, 'rc=%s, geschrieben=%s%s' % (rc, 'ja' if geschrieben else 'nein', zusatz), ok))
        shutil.rmtree(d, ignore_errors=True)

    vorher_abbild = [None]

    # F1 --schau schreibt nichts
    d = ordner(SEITE_LF); vorher_abbild[0] = abbild(d)
    rc, t = aufruf(werkzeug, ['--schau', 'index.php'], d)
    halte('F1 --schau', 'rc 0, nichts geschrieben', d, rc, t, 0, False)

    # F2 zweiter Pfad keine language_*.ini (Vorfall 28.08.2026)
    d = ordner(SEITE_LF); (d / 'zwei.php').write_bytes(b'<?php echo 1;\n'); vorher_abbild[0] = abbild(d)
    rc, t = aufruf(werkzeug, ['index.php', 'zwei.php'], d)
    halte('F2 zwei .php', 'rc 2, nichts geschrieben', d, rc, t, 2, False)

    # F3 ohne --schau nur ein Pfad
    d = ordner(SEITE_LF); vorher_abbild[0] = abbild(d)
    rc, t = aufruf(werkzeug, ['index.php'], d)
    halte('F3 ein Pfad', 'rc 2, nichts geschrieben', d, rc, t, 2, False)

    # F4 kein Textknoten: nichts schreiben (auch keinen leeren Abschnitt)
    d = ordner(SEITE_OHNE_TEXT); vorher_abbild[0] = abbild(d)
    rc, t = aufruf(werkzeug, ['index.php', 'language_de.ini'], d)
    halte('F4 nichts zu tun', 'rc 0, nichts geschrieben', d, rc, t, 0, False)

    # F5 Abschnitt [UI] steht schon da
    d = ordner(SEITE_LF, INI_MIT_UI); vorher_abbild[0] = abbild(d)
    rc, t = aufruf(werkzeug, ['index.php', 'language_de.ini'], d)
    halte('F5 Abschnitt doppelt', 'rc 2, nichts geschrieben', d, rc, t, 2, False)

    # F6 php -l meldet Parsefehler: nichts schreiben, keine Nebendatei
    d = ordner(SEITE_LF); vorher_abbild[0] = abbild(d)
    rc, t = im_prozess(werkzeug, ['index.php', 'language_de.ini'], d, falsches_php)
    halte('F6 Ergebnis kaputt', 'rc 1, nichts geschrieben', d, rc, t, 1, False)

    # F7 kein PHP: nichts schreiben
    d = ordner(SEITE_LF); vorher_abbild[0] = abbild(d)
    rc, t = im_prozess(werkzeug, ['index.php', 'language_de.ini'], d, ohne_php)
    halte('F7 kein PHP', 'rc 2, nichts geschrieben', d, rc, t, 2, False)

    # F8 php -l laeuft nicht zu Ende: nichts schreiben, KEINE Nebendatei
    d = ordner(SEITE_LF); vorher_abbild[0] = abbild(d)
    rc, t = im_prozess(werkzeug, ['index.php', 'language_de.ini'], d, php_l_haengt)
    halte('F8 php -l haengt', 'rc 2, nichts geschrieben', d, rc, t, 2, False)

    # F9 Gutfall LF: beide Dateien geschrieben, Ergebnis lintet, LF bleibt
    def pruef_gut(crlf):
        def p(dd):
            s = (dd / 'index.php').read_bytes()
            i = (dd / 'language_de.ini').read_bytes()
            fehler = []
            if sorted(os.listdir(dd)) != ['index.php', 'language_de.ini']:
                fehler.append('Dateiliste %s' % sorted(os.listdir(dd)))
            if crlf and s.count(b'\r\n') != s.count(b'\n'):
                fehler.append('CRLF nicht erhalten')
            if not crlf and b'\r' in s:
                fehler.append('LF nicht erhalten')
            if s.count(b"$L['UI.K") != 2:
                fehler.append('%d statt 2 Schluessel in index.php' % s.count(b"$L['UI.K"))
            if b'[UI]' not in i or i.count(b'K00') != 2 or b'[ALT]' not in i:
                fehler.append('INI unvollstaendig')
            if b'/opt/loxberry/config' not in s or b'$a > $b && $c < 5' not in s:
                fehler.append('Technik oder Code angefasst')
            r = subprocess.run([PHP, '-n', '-l', str(dd / 'index.php')],
                               capture_output=True, text=True)
            if r.returncode != 0:
                fehler.append('php -l %d' % r.returncode)
            return (not fehler), ('' if not fehler else ' - ' + '; '.join(fehler))
        return p

    d = ordner(SEITE_LF); vorher_abbild[0] = abbild(d)
    rc, t = aufruf(werkzeug, ['index.php', 'language_de.ini'], d, {'PHP84': PHP})
    halte('F9 Gutfall LF', 'rc 0, geschrieben, lintet, LF', d, rc, t, 0, True, pruef_gut(False))

    # F10 Gutfall CRLF
    d = ordner(SEITE_LF, crlf=True); vorher_abbild[0] = abbild(d)
    rc, t = aufruf(werkzeug, ['index.php', 'language_de.ini'], d, {'PHP84': PHP})
    halte('F10 Gutfall CRLF', 'rc 0, geschrieben, lintet, CRLF', d, rc, t, 0, True, pruef_gut(True))

    # F11 Gutfall ohne vorhandene INI: legt sie an
    def pruef_neu(dd):
        ok = (dd / 'language_de.ini').is_file() and b'[UI]' in (dd / 'language_de.ini').read_bytes()
        return ok, '' if ok else ' - INI fehlt'
    d = ordner(SEITE_LF, ini=None); vorher_abbild[0] = abbild(d)
    rc, t = aufruf(werkzeug, ['index.php', 'language_de.ini'], d, {'PHP84': PHP})
    halte('F11 INI neu', 'rc 0, geschrieben', d, rc, t, 0, True, pruef_neu)
    return aus


# Je Wache: (Fall, Anker, Ersatz). Der Anker muss im Werkzeug GENAU EINMAL stehen.
GEGENPROBEN = [
    ('F1 --schau', '    if schau:\n        return 0\n', '    pass\n'),
    # Die ganze Bedingung, beide Zeilen: "if False and A or B" bliebe wegen
    # der Bindung von and/or wirksam (erster Lauf 12.11.2026: Gegenprobe
    # gruen, weil die Wache gar nicht entfernt war - ein Fehler der Eichung).
    ('F2 zwei .php', "        if not Path(args[1]).name.startswith('language_') \\\n"
                     "                or not args[1].endswith('.ini'):\n",
     "        if False:\n"),
    ('F4 nichts zu tun', '    if not eintraege:\n', '    if False:\n'),
    ('F5 Abschnitt doppelt', "        if re.search(r'(?m)^\\s*\\[' + re.escape(abschnitt)",
     "        if False and re.search(r'(?m)^\\s*\\[' + re.escape(abschnitt)"),
    ('F6 Ergebnis kaputt', '    if r.returncode != 0:\n', '    if False:\n'),
    ('F7 kein PHP', '    if php is None:\n', '    if False:\n'),
    ('F8 php -l haengt', 'GEGENPROBE_F8', None),
]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    gegenprobe = '--gegenprobe' in sys.argv[1:]
    if args:
        werkzeug = Path(args[0]).resolve()
    else:
        werkzeug = HIER / 'oberflaeche_sprachfaehig.py'
        if not werkzeug.is_file():
            werkzeug = HIER.parent / 'Werkzeuge' / 'oberflaeche_sprachfaehig.py'
    if not werkzeug.is_file():
        print('NICHT MESSBAR: Werkzeug %s fehlt' % werkzeug)
        return 2
    if not PHP:
        print('NICHT MESSBAR: kein PHP 8.4 (PHP84=<pfad>)')
        return 2
    print('Werkzeug: %s  (sha256 %s)' % (werkzeug, hashlib.sha256(werkzeug.read_bytes()).hexdigest()[:16]))
    print('PHP:      %s' % PHP)
    erg = faelle(werkzeug)
    if not erg:
        print('NICHT MESSBAR: kein Fall gelaufen')
        return 2
    schlecht = 0
    for name, soll, ist, ok in erg:
        print('  [%s] %-22s erwartet: %-34s ist: %s' % ('ok ' if ok else 'ROT', name, soll, ist))
        schlecht += 0 if ok else 1
    print('%d Faelle, %d wie erwartet, %d abweichend' % (len(erg), len(erg) - schlecht, schlecht))
    if not gegenprobe:
        return 1 if schlecht else 0
    if schlecht:
        print('Gegenprobe uebersprungen: der Pruefling ist schon ohne Eingriff rot.')
        return 1
    print('\nGegenprobe: je Wache eine Fassung ohne sie - genau ihr Fall muss rot werden')
    quelle = werkzeug.read_text(encoding='utf-8')
    tmp = Path(tempfile.mkdtemp(prefix='osf_gp_'))
    fehl = 0
    nicht = 0
    try:
        for fall, anker, ersatz in GEGENPROBEN:
            if fall.startswith('F8'):
                # Die Wache aus der Berichtigung vom 12.11.2026: try/except um php -l
                # und Wegraeumen der Nebendatei. Ohne sie: der alte Ablauf.
                a1 = '    try:\n        r = subprocess.run([php, \'-l\', str(tmp)], capture_output=True, text=True,\n'
                if quelle.count(a1) != 1:
                    print('  [-- ] %-22s Anker nicht eindeutig (%d) - NICHT GEMESSEN' % (fall, quelle.count(a1)))
                    nicht += 1
                    continue
                anf = quelle.index(a1)
                ende = quelle.index('    if r.returncode != 0:\n', anf)
                alt = ("    r = subprocess.run([php, '-l', str(tmp)], capture_output=True, text=True,\n"
                       "                       encoding='utf-8', errors='replace', timeout=60)\n")
                neu = quelle[:anf] + alt + quelle[ende:]
            else:
                if quelle.count(anker) != 1:
                    print('  [-- ] %-22s Anker nicht eindeutig (%d) - NICHT GEMESSEN' % (fall, quelle.count(anker)))
                    nicht += 1
                    continue
                neu = quelle.replace(anker, ersatz)
            v = tmp / 'variante.py'
            v.write_text(neu, encoding='utf-8')
            erg = dict((n, ok) for n, _s, _i, ok in faelle(v))
            rot = [n for n, ok in erg.items() if not ok]
            gut = rot == [fall]
            fehl += 0 if gut else 1
            print('  [%s] ohne Wache %-22s rot: %s' % ('ok ' if gut else 'ROT', fall, ', '.join(rot) or 'nichts'))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('%d Gegenproben, %d wie erwartet, %d abweichend, %d nicht gemessen'
          % (len(GEGENPROBEN), len(GEGENPROBEN) - fehl - nicht, fehl, nicht))
    return 1 if fehl else (2 if nicht else 0)


if __name__ == '__main__':
    sys.exit(main())
