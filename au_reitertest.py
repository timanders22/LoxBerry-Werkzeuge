#!/usr/bin/env python3
"""Jeden Reiter der Oberflaeche EINZELN rendern - unter PHP 7.4 und 8.4.

Warum es das zusaetzlich zu rendern.py gibt: jenes ruft die Seite ohne
Parameter auf und misst damit nur den Vorgabereiter. Seit der Hausstandard
verlangt, dass der SERVER entscheidet, welcher Reiter offen ist, ist das zu
wenig - ein Reiter, dessen Inhalt einen Fehler wirft, faellt nicht auf,
solange sein Bereich nie als offen gerendert wird.

Geprueft wird je Reiter:
  * keine Warnung, kein Hinweis, keine Verfallsmeldung (ueber vorlauf_getpost)
  * genau EIN Bereich traegt sm-active
  * und zwar der verlangte
  * die Seite ist nicht verdaechtig kurz

$_GET wird ueber vorlauf_getpost.php gefuellt: PHP tut das unter der
Kommandozeile nicht, und ohne diesen Umweg misst der Prueflauf sechsmal
denselben Reiter und sieht dabei aus, als habe er sechs geprueft.

Aufruf:  au_reitertest.py [pluginordner]
"""

import os
import subprocess
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
LB = HIER / "lb"
VORLAUF = HIER / "vorlauf_getpost.php"
PLUGIN = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    HIER.parent / "LoxBerry-Plugin-AudiConnect-0.9.8")
PHPS = [("7.4", r"C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe"),
        ("8.4", r"C:\tmp\php-8.4.24-Win32-vs17-x64\php.exe")]
ORDNER = "audiconnect"


def reiter_aus_quelltext(datei):
    """Die Reiterliste aus der Oberflaeche lesen, nicht von Hand fuehren.

    Steht sie hier fest eingetragen, prueft dieses Werkzeug nach dem naechsten
    neuen Reiter weiterhin die alten - und meldet Erfolg.
    """
    import re
    t = datei.read_text(encoding="utf-8")
    feld = re.search(r"\$\w*reiter\s*=\s*array\((.*?)\);", t, re.S)
    if feld:
        namen = re.findall(r"'([a-z0-9]+)'\s*=>", feld.group(1))
        if namen:
            return namen
    namen = re.findall(r'data-ziel="tab-([a-z0-9]+)"', t)
    return sorted(set(namen), key=namen.index)


def main():
    seite = PLUGIN / "webfrontend/htmlauth/index.php"
    if not seite.is_file():
        print("Oberflaeche nicht gefunden:", seite)
        return 2
    reiter = reiter_aus_quelltext(seite)
    if not reiter:
        print("[FEHL] Es liess sich kein einziger Reiter auslesen - das "
              "Suchmuster passt nicht zur Datei.")
        return 1

    fehler = 0
    gelaufen = 0
    for fassung, php in PHPS:
        if not Path(php).is_file():
            print("[INFO] PHP %s nicht vorhanden - uebersprungen." % fassung)
            continue
        for r in reiter:
            umg = dict(os.environ)
            umg.update({
                "LBHOMEDIR": str(LB),
                "LBPPLUGINDIR": ORDNER,
                "LBPCONFIGDIR": str(LB / "config/plugins" / ORDNER),
                "LBPLOGDIR": str(LB / "log/plugins" / ORDNER),
                "LBPDATADIR": str(LB / "data/plugins" / ORDNER),
                "LBPHTMLAUTHDIR": str(seite.parent.resolve()),
                "LBPHTMLDIR": str((PLUGIN / "webfrontend/html").resolve()),
                "LBPTEMPLATEDIR": str((PLUGIN / "templates").resolve()),
                "LBPBINDIR": str((PLUGIN / "bin").resolve()),
                "REQUEST_METHOD": "GET",
                "HTTP_HOST": "loxberry.pruefstand",
                "QUERY_STRING": "form=" + r,
            })
            for k in ("LBPCONFIGDIR", "LBPLOGDIR", "LBPDATADIR"):
                Path(umg[k]).mkdir(parents=True, exist_ok=True)
            p = subprocess.run(
                [php, "-n", "-d", "include_path=.;" + str(LB / "libs" / "phplib"),
                 "-d", "auto_prepend_file=" + str(VORLAUF),
                 "-d", "display_errors=0", "-d", "error_reporting=32767",
                 "-d", "date.timezone=Europe/Berlin",
                 "-d", "extension_dir=" + str(Path(php).parent / "ext"),
                 "-d", "extension=curl", "-d", "extension=openssl",
                 "-d", "extension=mbstring", "-d", "extension=sockets",
                 "-d", "extension=fileinfo",
                 str(seite.resolve())],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                cwd=str(seite.parent.resolve()), env=umg, timeout=90)
            aus = p.stdout
            befunde = []
            if "###BEFUNDE###" in p.stderr:
                befunde = [z for z in p.stderr.split("###BEFUNDE###", 1)[1].strip().splitlines()
                           if z.strip()]
            offen = aus.count("sm-seite sm-active")
            richtig = ('sm-seite sm-active" id="tab-' + r + '"') in aus
            schlecht = bool(befunde) or offen != 1 or not richtig or len(aus) < 20000
            gelaufen += 1
            if schlecht:
                fehler += 1
            print("PHP %s  %-10s %-5s %7d Zeichen, %d offener Bereich, richtiger Reiter: %s"
                  % (fassung, r, "FEHL" if schlecht else "ok", len(aus), offen, richtig))
            for b in befunde:
                print("        " + b)

    print()
    print("%d Laeufe, %d Beanstandung(en)." % (gelaufen, fehler))
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
