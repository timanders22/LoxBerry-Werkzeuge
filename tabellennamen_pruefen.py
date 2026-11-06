#!/usr/bin/env python3
"""Tabellenzeilen des Reiters "Einbindung in Loxone" gegen die erzeugten Vorlagen.

SEIT 17.10.2026 (Welle Bild 17). Fuer die Linien OHNE eigenen Linienpruefer:
BYD Autos und Renault NG. AudiConnect, Skoda-Connect-NG und VolkswagenID
pruefen dasselbe in au_pruefen.py, skoda_pruefen.py und vw_pruefen.py
(pruefe_tabellennamen) - gleiche Bauform, Muster
vb_bild_vw17_bau_skripte/namen_probe.py.

Die Tabellen stehen in Zeilen Z<seite>_<nr> = "Typ | Name | Bedeutung | Eingang"
der Sprachdatei. Jede Zeile, deren Typ mit "(Vorlage „X“)" endet, muss mit
ihrem Namen genau einen Befehl in der Vorlage mit dem Behaeltertitel X haben.
Verglichen wird gegen die ERZEUGTE Vorlage: das PHP des Plugins laeuft in
einer Wegwerf-Attrappe (LBHOMEDIR in einem Zeitordner, danach geloescht;
LBPPLUGINDIR = FOLDER aus plugin.cfg) und liefert die Vorlagen fuer
Fahrzeug 1 ohne Konfiguration.

Zeilen "(Vorlage „X“, Plugin Y)" nennen die Vorlage eines ANDEREN Plugins
(BYD: Spotpreis aWATTar). Sie werden gezaehlt und genannt, aber nicht
geprueft - dieses Plugin erzeugt sie nicht.

Aufruf:  tabellennamen_pruefen.py <pluginordner>
Rueckgabe: 0 ohne Befund, 1 mit Befund, 2 nicht messbar (keine Linie aus der
Tabelle unten, keine Tabellenzeile mit Vorlage, kein PHP).
"""

import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# FOLDER aus plugin.cfg -> (Bibliothek, Pfadaufruf, Vorlagenaufrufe)
LINIEN = {
    "bydautos": ("webfrontend/html/by_lib.php", "by_paths()",
                 ["by_vorlage(1)", "by_vorlage_vo(1)"]),
    "renault_ng": ("webfrontend/htmlauth/rn_lib.php", "rn_paths(false)",
                   ["rn_vorlage_vo()"]),
}
PHPS = [Path(p) for p in (r"C:\tmp\php-8.4.27-Win32-vs17-x64\php.exe",
                          r"C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe")]


def tabellenzeilen(wurzel):
    """[(Schluessel, Vorlage, Name)] und die Zahl der Zeilen mit fremder Vorlage."""
    ini = (wurzel / "templates/lang/language_de.ini").read_text(encoding="utf-8")
    zeilen, fremd = [], []
    for schl, wert in re.findall(r'^(Z\d+_\d+) = "(.*)"$', ini, re.M):
        teile = [html.unescape(t.strip()) for t in wert.split("|")]
        if len(teile) < 2:
            continue
        m = re.search(r"\(Vorlage „([^“]+)“\)$", teile[0])
        if m:
            zeilen.append((schl, m.group(1), teile[1]))
        elif re.search(r"\(Vorlage „[^“]+“, Plugin [^)]+\)$", teile[0]):
            fremd.append(schl)
    return zeilen, fremd


def vorlagen_erzeugen(wurzel, php, ordner, lib, pfade, aufrufe):
    """{Behaeltertitel: [Befehlstitel]} oder (None, Meldung)."""
    lb = Path(tempfile.mkdtemp(prefix="tabellennamen_lb_"))
    try:
        for t in ("config", "data", "log"):
            (lb / t / "plugins").mkdir(parents=True)
        skript = lb / "vorlagen.php"
        skript.write_text(
            "<?php\n$_SERVER['HTTP_HOST'] = 'loxberry';\n"
            "require %s;\n$p = %s;\n"
            "if (realpath($p['home']) !== realpath(getenv('LBHOMEDIR'))) "
            "{ fwrite(STDERR, \"Pfade zeigen nicht auf die Attrappe\\n\"); exit(2); }\n"
            "$aus = array();\n%s"
            "echo json_encode($aus);\n"
            % (json.dumps(str((wurzel / lib).resolve())), pfade,
               "".join("$v = %s; $aus[] = $v[1];\n" % a for a in aufrufe)),
            encoding="utf-8")
        umg = dict(os.environ)
        umg.update({"LBHOMEDIR": str(lb), "LBPPLUGINDIR": ordner, "LBLANG": "de",
                    "PYTHONDONTWRITEBYTECODE": "1"})
        r = subprocess.run([str(php), "-n", "-d", "display_errors=1",
                            "-d", "error_reporting=32767",
                            "-d", "date.timezone=Europe/Berlin", str(skript)],
                           capture_output=True, cwd=str(lb), env=umg, timeout=60)
    finally:
        shutil.rmtree(str(lb), ignore_errors=True)
    aus = r.stdout.decode("utf-8", "replace")
    try:
        texte = json.loads(aus)
    except ValueError:
        texte = None
    if r.returncode != 0 or r.stderr.strip() or texte is None:
        return None, "rc %d: %s" % (r.returncode, (r.stderr.decode("utf-8", "replace")
                                                   + aus).strip()[:300])
    vorlagen = {}
    for t in texte:
        kopf = re.search(r'<(?:VirtualInHttp|VirtualOut) [^>]*?Title="([^"]*)"', t)
        if kopf:
            vorlagen.setdefault(html.unescape(kopf.group(1)), []).extend(
                html.unescape(x) for x in
                re.findall(r'<(?:VirtualInHttpCmd|VirtualOutCmd) Title="([^"]*)"', t))
    return vorlagen, ""


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    wurzel = Path(sys.argv[1])
    print("Tabellennamen gegen erzeugte Vorlagen:", wurzel.name)
    cfg = (wurzel / "plugin.cfg").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^FOLDER=(\S+)", cfg, re.M)
    ordner = m.group(1) if m else ""
    if ordner not in LINIEN:
        print("[ -- ] Linie %r steht nicht in der Tabelle dieses Werkzeugs - nicht "
              "messbar (au/sk/vw: eigener Linienpruefer)" % ordner)
        return 2
    zeilen, fremd = tabellenzeilen(wurzel)
    if not zeilen:
        print("[ -- ] Keine Tabellenzeile mit \"(Vorlage ...)\" in language_de.ini - "
              "nicht messbar (Stand vor Welle Bild 17?)")
        return 2
    php = next((p for p in PHPS if p.is_file()), None)
    if php is None:
        print("[ -- ] Kein PHP da - die Vorlagen liessen sich nicht erzeugen, "
              "%d Zeilen ungeprueft" % len(zeilen))
        return 2
    lib, pfade, aufrufe = LINIEN[ordner]
    vorlagen, meldung = vorlagen_erzeugen(wurzel, php, ordner, lib, pfade, aufrufe)
    if vorlagen is None:
        print("[FEHL] Die Vorlagen liessen sich nicht erzeugen (%s)" % meldung)
        return 1
    befunde = []
    for schl, beh, name in zeilen:
        if beh not in vorlagen:
            befunde.append("%s: Vorlage '%s' erzeugt das Plugin nicht" % (schl, beh))
        elif vorlagen[beh].count(name) != 1:
            befunde.append("%s: '%s' steht %d-mal in der Vorlage '%s'"
                           % (schl, name, vorlagen[beh].count(name), beh))
    if fremd:
        print("[INFO] %d Zeile(n) mit Vorlage eines anderen Plugins nicht geprueft: %s"
              % (len(fremd), ", ".join(fremd)))
    for b in befunde:
        print("[FEHL] " + b)
    if befunde:
        print("\n%d von %d Tabellenzeilen mit Vorlage beanstandet." % (len(befunde), len(zeilen)))
        return 1
    print("[OK]   Alle %d Tabellenzeilen mit Vorlage finden ihren Namen genau einmal "
          "in der erzeugten Vorlage (%d Vorlagen, PHP %s)"
          % (len(zeilen), len(vorlagen), php.parent.name.split("-")[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
