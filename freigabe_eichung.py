#!/usr/bin/env python3
"""Eicht den Abschnitt "Personenbezogenes" von freigabe_pruefen.py.

Warum es diese Datei gibt: am 20.08.2026 wurde der Passwort-Waechter
geschaerft, weil er in ALLEN VIER Auto-Plugins denselben Fehlalarm gab
(`L_PASSWORT = "Passwort des Kontos"` in den Sprachdateien). Eine Schaerfung
ohne Gegenprobe ist aber nur eine Abschwaechung mit guter Absicht: sie sieht
so lange richtig aus, wie niemand ein echtes Geheimnis hinlegt.

Also wird beides gemessen, in einer Kopie und nie am Bestand:

  * jeder Fall, der gefunden werden MUSS, wird hingelegt und muss rot werden
  * jeder Fall, der ausgenommen sein SOLL, wird hingelegt und muss gruen
    bleiben

Aufruf:
    python3 Werkzeuge/freigabe_eichung.py PLUGINORDNER
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
PRUEFER = HIER / "freigabe_pruefen.py"

# (Beschreibung, Zieldatei im Plugin, angehaengter Text, muss_gefunden_werden)
#
# Die Zieldatei ist Teil des Falls und nicht Beiwerk. Es gibt zwei Ausnahmen,
# und sie greifen an verschiedenen Stellen:
#
#   * die Beschriftung nach dem NAMEN - nur fuer einen Hausschluessel
#     (L_/H_/F_/A_/K_/M_/T_) und nur unterhalb von templates/lang/. Derselbe
#     Text in einer PHP-Datei muss gefunden werden.
#   * der Platzhalter nach dem WERT - ueberall, aber nur bei
#     Auslassungspunkten oder einem geschrienen Wert, der sich selbst als
#     Platzhalter benennt.
#
# Deshalb steht bei jedem Fall dabei, WO er liegt.
FAELLE = [
    ("echtes Geheimnis in PHP",
     "webfrontend/html/by_lib.php",
     '\n// EICHUNG\n$passwort = "geheim123";\n', True),
    ("echtes Geheimnis in einer Sprachdatei, klein geschrieben",
     "templates/lang/language_de.ini",
     '\npassword = "geheim123"\n', True),
    ("echtes Geheimnis in einer Sprachdatei mit Hausschluessel",
     "templates/lang/language_de.ini",
     '\nDB_PASSWORD = "geheim123"\n', True),
    ("dieselbe Beschriftung in einer PHP-Datei",
     "webfrontend/html/by_lib.php",
     '\n// EICHUNG\n$x = "L_PASSWORT = \'Passwort des Kontos\'";\n', True),
    ("echte E-Mail-Adresse",
     "webfrontend/html/by_lib.php",
     '\n// EICHUNG: vorname.nachname@irgendeinehausadresse.de\n', True),
    ("Beschriftung in der Sprachdatei",
     "templates/lang/language_de.ini",
     '\nL_PASSWORT = "Passwort des Kontos"\n', False),
    ("Beispieladresse nach RFC 2606",
     "webfrontend/htmlauth/index.php",
     '\n<!-- EICHUNG: placeholder="name@example.com" -->\n', False),

    # ---- Die Platzhalter-Regel (20.08.2026), beide Richtungen ----
    #
    # Die drei Faelle, die GEFUNDEN werden muessen, liegen absichtlich knapp
    # neben der Ausnahme: geschrieben, aber ohne Selbstbekenntnis; mit
    # Leerzeichen; mit Bindestrich. Waere die Regel "nur Grossbuchstaben" oder
    # "enthaelt ein Leerzeichen", fiele hier ein echtes Geheimnis durch.
    ("Platzhalter mit Auslassungspunkten",
     "webfrontend/html/by_lib.php",
     '\n// EICHUNG: -e MQTT_USER=\u2026 -e MQTT_PASSWORD=\u2026\n', False),
    ("geschriener Platzhalter, der sich selbst benennt",
     "webfrontend/html/by_lib.php",
     '\n// EICHUNG: -e SAIC_PASSWORD="IHR-ISMART-PASSWORT"\n', False),
    ("GESCHRIENES Geheimnis ohne Selbstbekenntnis",
     "webfrontend/html/by_lib.php",
     '\n// EICHUNG\n$passwort = "HUNTER2";\n', True),
    ("Geheimnis mit Bindestrich, aber ohne Selbstbekenntnis",
     "webfrontend/html/by_lib.php",
     '\n// EICHUNG\n$passwort = "GEHEIM-123";\n', True),
    ("Geheimnis mit Leerzeichen",
     "webfrontend/html/by_lib.php",
     '\n// EICHUNG\n$passwort = "mein geheimes wort";\n', True),
]


def personenbezug(ordner: Path):
    """Rueckgabe: (gruen, Meldungstext) des Abschnitts Personenbezogenes."""
    r = subprocess.run([sys.executable, str(PRUEFER), str(ordner), "--ohne-netz"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=300)
    for z in (r.stdout + r.stderr).splitlines():
        if "Personenbezogenes" in z and ("[ok ]" in z or "[FEHL]" in z):
            return ("[ok ]" in z, re.sub(r"\s+", " ", z).strip())
    return (None, "der Abschnitt kam in der Ausgabe nicht vor")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    quelle = Path(sys.argv[1]).resolve()
    if not (quelle / "webfrontend").is_dir():
        print("[FEHL] %s sieht nicht wie ein Plugin-Ordner aus." % quelle)
        return 2

    # Zuerst der Ausgangszustand. Ist der schon rot, sagt kein einziger Fall
    # danach etwas aus - dann wird abgebrochen statt gemessen.
    gruen, text = personenbezug(quelle)
    if gruen is not True:
        print("[FEHL] Der Ausgangszustand ist nicht gruen: %s" % text)
        print("       Ohne gruene Ausgangslage misst kein Eichfall etwas.")
        return 1
    print("[ok  ] %-62s %s" % ("Ausgangszustand gruen", text[-60:]))

    fehl = 0
    for beschreibung, datei, text_an, muss_rot in FAELLE:
        tmp = Path(tempfile.mkdtemp(prefix="freigabe_eich_"))
        try:
            kopie = tmp / quelle.name
            shutil.copytree(quelle, kopie)
            ziel = kopie / datei
            if not ziel.is_file():
                print("[FEHL] %-62s %s fehlt" % (beschreibung, datei))
                fehl += 1
                continue
            # Angehaengt wird BYTEWEISE: der Zeilenendstil der Datei bleibt
            # damit unberuehrt, und der Waechter sieht denselben Text, den er
            # im Ernstfall sehen wuerde.
            with open(ziel, "ab") as f:
                f.write(text_an.encode("utf-8"))
            g, m = personenbezug(kopie)
            if g is None:
                print("[FEHL] %-62s %s" % (beschreibung, m))
                fehl += 1
            elif muss_rot and g:
                print("[FEHL] %-62s bleibt GRUEN - wird nicht gefunden" % beschreibung)
                fehl += 1
            elif not muss_rot and not g:
                print("[FEHL] %-62s wird ROT - Fehlalarm: %s" % (beschreibung, m[-70:]))
                fehl += 1
            else:
                print("[ok  ] %-62s %s" % (beschreibung,
                                           "wird rot" if muss_rot else "bleibt gruen"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    print("")
    print("%d von %d Eichfaellen in Ordnung." % (len(FAELLE) - fehl, len(FAELLE)))
    print("Gemessen wurde der Abschnitt Personenbezogenes, nichts sonst.")
    return 1 if fehl else 0


if __name__ == "__main__":
    sys.exit(main())
