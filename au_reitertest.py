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
# ERGAENZT 18.10.2026: AU_LB lenkt auf eine eigene Kopie der Attrappe um (wie
# au_endpunkttest.py). Ohne AU_LB nur unter .kette_sperre laufen lassen.
if os.environ.get("AU_LB"):
    LB = Path(os.environ["AU_LB"])
VORLAUF = HIER / "vorlauf_getpost.php"
def neuester_ordner(arbeit, praefix):
    """Der Pluginordner mit der HOECHSTEN Fassungsnummer (wie au_endpunkttest.py).

    BERICHTIGT 18.10.2026: die Vorgabe zeigte auf "LoxBerry-Plugin-AudiConnect-
    0.9.8" - den Ordner gibt es seit der 0.9.10 nicht mehr."""
    import re

    def nummer(name):
        m = re.search(r"(\d+)\.(\d+)\.(\d+)$", name)
        return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)
    k = sorted((d for d in arbeit.iterdir()
                if d.is_dir() and d.name.startswith(praefix)
                and (d / "plugin.cfg").is_file()), key=lambda d: nummer(d.name))
    if not k:
        raise SystemExit("ABBRUCH: kein Ordner %s* im Arbeitsordner." % praefix)
    return k[-1]


PLUGIN = (Path(sys.argv[1]) if len(sys.argv) > 1
          else neuester_ordner(HIER.parent, "LoxBerry-Plugin-AudiConnect-"))
PHPS = [("7.4", r"C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe"),
        ("8.4", r"C:\tmp\php-8.4.27-Win32-vs17-x64\php.exe")]
def ordner_aus_plugincfg(plugin):
    """Der Ordnername, unter dem LoxBerry das Plugin fuehrt.

    BERICHTIGT 31.08.2026. Hier stand ORDNER = "audiconnect" fest verdrahtet -
    in genau der Datei, die zwanzig Zeilen weiter oben erklaert, warum die
    Reiterliste NICHT fest eingetragen werden darf ("dieses Werkzeug prueft
    nach dem naechsten neuen Reiter weiterhin die alten - und meldet Erfolg").

    Was der feste Wert angerichtet hat: LBPCONFIGDIR, LBPDATADIR und LBPLOGDIR
    zeigten fuer JEDES gepruefte Plugin auf AudiConnects Ordner. Ein Lauf gegen
    Skoda-Connect-NG 0.9.13 meldete am 31.08.2026 10 von 10 Laeufen rot mit
    "Undefined array key kennzeichen/motorart/software" - gemessen wurde dabei
    die Skoda-Oberflaeche an AUDIS Abbild, das diese drei Schluessel gar nicht
    fuehrt. Der Befund war echt (mit einem eigenen Teilabbild nachgestellt),
    die Messung war es nicht. Ein Werkzeug, das die Bank des einen Plugins
    unter ein anderes schiebt, ERZEUGT Befunde statt sie zu finden - und das
    ist teurer als eines, das nichts findet.

    Genommen wird FOLDER aus der plugin.cfg: das ist der Name, unter dem
    LoxBerry die Ordner anlegt, und die Attrappe unter Werkzeuge/lb ist genau
    so bestueckt (audiconnect, skodaconnect, heimkino ...). Fehlt die Angabe,
    gilt der Ordnername in Kleinschreibung wie in rendern.py.
    """
    import re
    cfg = plugin / "plugin.cfg"
    if cfg.is_file():
        m = re.search(r"^\s*FOLDER\s*=\s*(\S+)\s*$",
                      cfg.read_text(encoding="utf-8", errors="replace"), re.M)
        if m:
            return m.group(1).lower()
    return plugin.name.lower()


ORDNER = ordner_aus_plugincfg(PLUGIN)


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



def bank_hinlegen():
    """Die Bank aus Werkzeuge/banken/ nach lb/data/plugins/<ordner>/ kopieren.

    Ueberschrieben wird nur, was hier auch als Vorlage liegt - ein Abbild, das
    jemand von Hand in die Attrappe gelegt hat, bleibt unangetastet, wenn es
    dafuer keine Vorlage gibt.
    """
    import shutil
    quelle = HIER / "banken" / (ORDNER + ".loxone.json")
    if not quelle.is_file():
        return False
    ziel = LB / "data/plugins" / ORDNER / "loxone.json"
    ziel.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(str(quelle), str(ziel))
    return True


def bank_wiegt(ordner):
    """Steht in der Bank ueberhaupt ein Abbild - und wie viele Fahrzeuge?

    ERGAENZT 31.08.2026, nach einem eigenen Fehlschlag. Fuer Skoda-Connect-NG
    lag unter data/plugins/skodaconnect ein Abbild mit zwei Fahrzeugen, davon
    eines als Teilabbild; der Lauf meldete damit sechs ungeschuetzte
    Feldzugriffe. Waehrend der Behebung ist die Datei verschwunden - und der
    naechste Lauf meldete "10 Laeufe, 0 Beanstandungen". Die Seite war
    5772 Zeichen kuerzer, weil sie gar keine Fahrzeugtabelle mehr enthielt.

    Ein gruener Haken, der aus einer leeren Bank kommt, ist die teuerste
    Meldung dieser Sammlung: er sieht aus wie ein Beleg und ist keiner. Ohne
    Abbild gibt es hier nichts zu messen, und das WIRD JETZT GESAGT.
    """
    import json
    bank = LB / "data/plugins" / ORDNER / "loxone.json"
    if not bank.is_file():
        return (0, str(bank))
    try:
        d = json.loads(bank.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return (0, str(bank) + " (unlesbar)")
    return (len(d.get("fahrzeuge") or {}), str(bank))

def mit_at_unterdrueckt(befund):
    """Hat die Stelle diese Meldung selbst mit @ unterdrueckt?

    ERGAENZT 18.10.2026. vorlauf_getpost.php sieht auch Meldungen hinter einem
    @ (der Fehlerbehandler wird unabhaengig von error_reporting() gerufen). Seit
    0.9.22 probt der Reiter "test" den eigenen Endpunkt mit @fopen ueber
    127.0.0.1 (U12) und wertet false selbst aus; am Pruefstand gibt es keinen
    Webserver, und jede Seite meldete deshalb eine Warnung. rendern.py trennt
    solche Meldungen seit 25.09.2026 ebenso ab ("kein Befund").
    Eng gefasst: nur wenn die gemeldete Zeile genau die Funktion der Meldung mit
    @ davor ruft und der Dateiname im Plugin eindeutig ist - sonst Befund.
    """
    import re
    m = re.match(r"(?:WARNUNG|HINWEIS|VERFALL)\|(\w+)\(", befund)
    ort = re.search(r"\|([^|]+\.php):(\d+)$", befund)
    if not m or not ort:
        return False
    treffer = [f for f in PLUGIN.rglob(ort.group(1)) if f.is_file()]
    if len(treffer) != 1:
        return False
    zeilen = treffer[0].read_text(encoding="utf-8", errors="replace").splitlines()
    nr = int(ort.group(2))
    if not 1 <= nr <= len(zeilen):
        return False
    return re.search(r"@\s*" + re.escape(m.group(1)) + r"\s*\(", zeilen[nr - 1]) is not None


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

    if bank_hinlegen():
        print("[INFO] Bank aus Werkzeuge/banken/ hingelegt.")
    anzahl, wo = bank_wiegt(PLUGIN)
    if anzahl == 0:
        print("[FEHL] Die Bank hat kein Abbild mit Fahrzeugen: %s" % wo)
        print("       Die Oberflaeche zeigt dann keine Fahrzeugtabelle, und")
        print("       jeder Feldzugriff darauf bleibt UNGEMESSEN. Das ist kein")
        print("       bestandener Lauf, sondern ein nicht durchgefuehrter.")
        return 1
    print("[INFO] Bank: %d Fahrzeug(e) in %s" % (anzahl, wo))

    fehler = 0
    gelaufen = 0
    zahl_unterdrueckt = 0
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
            # Eine Meldung mit Zeilenumbruch im Text (PHP 7.4, fopen) kommt als
            # zwei Zeilen; die zweite beginnt mit "|datei:zeile".
            ganz = []
            for z in befunde:
                if z.startswith("|") and ganz:
                    ganz[-1] = ganz[-1].rstrip() + z
                else:
                    ganz.append(z)
            unterdrueckt = [b for b in ganz if mit_at_unterdrueckt(b)]
            befunde = [b for b in ganz if b not in unterdrueckt]
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
            for b in unterdrueckt:
                print("        [INFO] mit @ unterdrueckt, kein Befund: " + b)
                zahl_unterdrueckt += 1

    print()
    print("%d Laeufe, %d Beanstandung(en)." % (gelaufen, fehler))
    if zahl_unterdrueckt:
        print("%d Meldung(en) mit @ unterdrueckt (kein Befund)." % zahl_unterdrueckt)
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
