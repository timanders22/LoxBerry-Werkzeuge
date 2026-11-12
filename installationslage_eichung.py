#!/usr/bin/env python3
"""Eichung von installationslage_pruefen.py: sieht es, was ein Skript verschweigt?

Baut zwei winzige Plugins in einem Wegwerfordner und haelt die Ausgabe des
Werkzeugs gegen Erwartungen, die VOR dem Lauf feststehen:

  Plugin P (FOLDER lageprobe)
    L1 bin/L1_schweigt.php     display_errors aus, require einer fremden
                               absoluten Datei, keine Ausgabe -> Zeile "." "findet ... nicht"
                               (erste Fassung erwartete "Fatal" - das Werkzeug
                               nennt den Fall genauer; Erwartung berichtigt)
    L2 bin/L2_pfad.php         display_errors aus, ERST Ausgabe, dann require in
                               webfrontend/html/plugins/<ordner>/ -> BEFUND
    L3 bin/L3_exit3.php        Ausgabe, dann exit(3), kein Fehler -> Zeile "."
                               mit "Rueckgabewert 3" (Berichtigung 12.11.2026)
    L4 bin/L4_still.php        exit(3) ohne Ausgabe -> Zeile "." "Abbruch ohne Meldung"
    L5 bin/L5_report0.php      error_reporting(0) + display_errors aus + require
                               im eigenen html-Baum -> BEFUND
    L6 bin/L6_gut.php          sauber, Rueckgabewert 0 -> KEINE Zeile
    L7 html/L7_token.php       Token-Abweisung vor einer falschen require-Zeile
                               -> textliche Sicht, Zeile "." "laedt mit dirname"
    L8 html/L8_richtig.php     dirname(...) . '/html/plugins/' . basename(__DIR__)
                               -> KEINE Zeile, eine Ausnahme gezaehlt
  Plugin Q (FOLDER vieleprobe): zehn Skripte, je Ausgabe + exit(5)
    Q  -> acht Zeilen "." und eine Zeile "... und 2 weitere" (Berichtigung 12.11.2026)

    python -B installationslage_eichung.py [WERKZEUG.py]

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
HIER = Path(__file__).resolve().parent

P = {
    'bin/L1_schweigt.php': "<?php\nini_set('display_errors', '0');\nrequire '/gibt/es/nicht/fremd.php';\n",
    'bin/L2_pfad.php': ("<?php\nini_set('display_errors', '0');\necho \"OK=0\\n\";\n"
                        "$p = getenv('LBHOMEDIR') . '/webfrontend/html/plugins/' . getenv('LBPPLUGINDIR') . '/fehlt_lib.php';\n"
                        "require $p;\n"),
    'bin/L3_exit3.php': "<?php\necho \"FEHLER: keine Konfiguration\\n\";\nexit(3);\n",
    'bin/L4_still.php': "<?php\nexit(3);\n",
    'bin/L5_report0.php': ("<?php\nerror_reporting(0);\nini_set('display_errors', '0');\n"
                           "$p = getenv('LBHOMEDIR') . '/webfrontend/html/plugins/' . getenv('LBPPLUGINDIR') . '/auch_weg.php';\n"
                           "require $p;\n"),
    'bin/L6_gut.php': "<?php\necho \"OK\\n\";\n",
    'webfrontend/html/L7_token.php': ("<?php\nif (!isset($_GET['token'])) { echo 'verweigert'; exit(0); }\n"
                                      "require_once dirname(__DIR__) . '/htmlauth/lib.php';\n"),
    'webfrontend/html/L8_richtig.php': ("<?php\n$f = dirname(dirname(dirname(__DIR__))) . '/html/plugins/' . basename(__DIR__) . '/lib.php';\n"
                                        "if (is_file($f)) { require_once $f; }\necho 'ok';\n"),
}


def plugin(ziel, folder, dateien):
    ziel.mkdir(parents=True)
    (ziel / 'plugin.cfg').write_text('[PLUGIN]\nVERSION=0.0.1\nNAME=%s\nFOLDER=%s\n' % (folder, folder), encoding='utf-8')
    for rel, inhalt in dateien.items():
        p = ziel / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(inhalt.encode('utf-8'))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    werkzeug = Path(args[0]).resolve() if args else HIER / 'installationslage_pruefen.py'
    if not werkzeug.is_file():
        print('NICHT MESSBAR: %s fehlt' % werkzeug)
        return 2
    tmp = Path(tempfile.mkdtemp(prefix='lageeich_'))
    try:
        plugin(tmp / 'LoxBerry-Plugin-Lageprobe-0.0.1', 'lageprobe', P)
        plugin(tmp / 'LoxBerry-Plugin-Vieleprobe-0.0.1', 'vieleprobe',
               dict(('bin/Q%02d.php' % i, "<?php\necho \"x\\n\";\nexit(5);\n") for i in range(1, 11)))
        u = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        r = subprocess.run([sys.executable, '-B', str(werkzeug),
                            str(tmp / 'LoxBerry-Plugin-Lageprobe-0.0.1'),
                            str(tmp / 'LoxBerry-Plugin-Vieleprobe-0.0.1')],
                           capture_output=True, text=True, encoding='utf-8', errors='replace',
                           cwd=str(tmp), env=u, timeout=600)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    aus = r.stdout + r.stderr
    teile = re.split(r'(?m)^(?=LoxBerry-Plugin-)', aus)
    p_text = next((t for t in teile if t.startswith('LoxBerry-Plugin-Lageprobe')), '')
    q_text = next((t for t in teile if t.startswith('LoxBerry-Plugin-Vieleprobe')), '')
    if not p_text or not q_text:
        print('NICHT MESSBAR: Ausgabe ohne die beiden Plugin-Abschnitte (rc %d)' % r.returncode)
        print(aus[-1500:])
        return 2

    def zeilen(text, muster):
        return [z for z in text.splitlines() if re.search(muster, z)]

    pruef = [
        ('L1 schweigt, fremde Datei', bool(zeilen(p_text, r'^\s+\. bin/L1_schweigt\.php .*fremd\.php nicht'))),
        ('L2 Pfad nach Ausgabe', bool(zeilen(p_text, r'^\s+! bin/L2_pfad\.php findet'))),
        ('L3 exit(3) mit Ausgabe', bool(zeilen(p_text, r'^\s+\. bin/L3_exit3\.php: endet mit Rueckgabewert 3'))),
        ('L4 exit(3) still', bool(zeilen(p_text, r'^\s+\. bin/L4_still\.php.*Abbruch ohne Meldung, Rueckgabewert 3'))),
        ('L5 error_reporting(0)', bool(zeilen(p_text, r'^\s+! bin/L5_report0\.php findet'))),
        ('L6 sauber schweigt', not zeilen(p_text, r'L6_gut')),
        ('L7 textliche Sicht', bool(zeilen(p_text, r'^\s+\. webfrontend/html/L7_token\.php:3 laedt mit dirname'))),
        ('L8 richtig schweigt', not zeilen(p_text, r'L8_richtig') and bool(zeilen(p_text, r'1 Ausnahme'))),
        ('P Urteil: 2 Befunde', bool(zeilen(p_text, r'^LoxBerry-Plugin-Lageprobe-0\.0\.1\s+\d+ Dateien.*2 BEFUND'))),
        ('Q acht Zeilen gezeigt', len(zeilen(q_text, r'^\s+\. bin/Q\d\d\.php: endet mit Rueckgabewert 5')) == 8),
        ('Q Rest genannt', bool(zeilen(q_text, r'^\s+\. \.\.\. und 2 weitere'))),
        ('Rueckgabe 1 (Befund)', r.returncode == 1),
    ]
    schlecht = 0
    for name, ok in pruef:
        print('  [%s] %s' % ('ok ' if ok else 'ROT', name))
        schlecht += 0 if ok else 1
    print('%d Erwartungen, %d erfuellt, %d abweichend (Werkzeug %s)'
          % (len(pruef), len(pruef) - schlecht, schlecht, werkzeug.name))
    if '--zeigen' in sys.argv:
        print(aus)
    return 1 if schlecht else 0


if __name__ == '__main__':
    sys.exit(main())
