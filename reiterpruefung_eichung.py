#!/usr/bin/env python3
"""Eicht die Reiterpruefung im Reiter Test von VW und Skoda.

Warum es diese Datei gibt: die Zeile wurde am 20.08.2026 nachgezogen, weil
hausstandard_pruefen.py bei einer ERZEUGTEN Reiterleiste nichts messen kann und
einen Strich meldete - der sich wie "nichts zu beanstanden" liest. Eine
Pruefzeile, die dieselbe Luecke schliessen soll, muss selbst gemessen werden,
sonst ist sie nur eine zweite Zeile, die nichts sagt.

Also wird jede Abweichung, die sie finden soll, in einer KOPIE hergestellt, und
es wird nachgesehen, ob die Zeile rot wird und WELCHEN Grund sie nennt. Der
Grund gehoert dazu: eine Zeile, die aus dem falschen Grund rot wird, wird beim
naechsten Mal falsch behoben.

Gemessen wird gegen die SDK-Attrappe unter Werkzeuge/lb, nicht gegen ein
Geraet, und der Pruefling wird kopiert - der Ordner im Arbeitsordner wird nur
gelesen.

Aufruf:
    python3 Werkzeuge/reiterpruefung_eichung.py PLUGINORDNER PRAEFIX
    python3 Werkzeuge/reiterpruefung_eichung.py LoxBerry-Plugin-VolkswagenID-0.9.8 vw
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
LB = HIER / "lb"
VORLAUF = HIER / "vorlauf.php"
PHPS = [("7.4", r"C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe"),
        ("8.4", r"C:\tmp\php-8.4.24-Win32-vs17-x64\php.exe")]

# Das Pruefstueck ruft die Selbstpruefung auf und gibt GENAU die Zeile aus, um
# die es geht - Stand und Antwort, durch | getrennt. Keine Oberflaeche, kein
# HTML: was hier steht, ist die Aussage der Pruefzeile selbst.
STUECK = """<?php
error_reporting(E_ALL & ~E_DEPRECATED & ~E_NOTICE);
require_once 'loxberry_web.php';
require_once dirname(__DIR__) . '/html/%(p)s_lib.php';
require_once __DIR__ . '/%(p)s_test.php';
$frage = %(p)s_t('TEST.F_REITER');
foreach (%(p)s_pruefungen() as $z) {
    if ($z['frage'] === $frage) {
        echo '###ZEILE###' . $z['stand'] . '|'
           . preg_replace('/\\s+/', ' ', strip_tags($z['antwort'])) . "\\n";
    }
}
"""

# (Beschreibung, Datei, alt, neu, erwarteter Wortlaut im Grund)
#
# Der erwartete Wortlaut ist absichtlich ein STUECK des Textes und nicht der
# ganze: er soll die Ursache festnageln, ohne bei jeder Umformulierung des
# Textes zu brechen.
FAELLE = {
    "vw": [
        ("ein Name fehlt in der Positivliste",
         "webfrontend/htmlauth/index.php",
         "$vw_reiter_ids = array('settings', 'mqtt', 'loxone', 'test', 'log');",
         "$vw_reiter_ids = array('settings', 'mqtt', 'loxone', 'test');",
         "nicht in der Liste"),
        ("eine Flaeche fehlt",
         "webfrontend/htmlauth/index.php",
         'id="tab-log">',
         'id="tab-logdateien">',
         "ohne Fl"),
        ("eine Beschriftung fehlt",
         "webfrontend/htmlauth/index.php",
         "    'test'     => 'REITER.TEST',          'log'  => 'REITER.LOG',",
         "    'test'     => 'REITER.TEST',",
         "ohne Beschriftung"),
    ],
    "sk": [
        ("ein Name fehlt in der Liste",
         "webfrontend/htmlauth/index.php",
         "    'log'      => sk_t('REITER.LOG'),\n",
         "",
         "nicht in der Liste"),
        ("eine Flaeche fehlt",
         "webfrontend/htmlauth/index.php",
         'id="tab-log">',
         'id="tab-logdateien">',
         "ohne Fl"),
    ],
}


def umgebung(plugin_htmlauth: Path, name: str) -> dict:
    u = dict(os.environ)
    u["LBHOMEDIR"] = str(LB)
    u["LBPPLUGINDIR"] = name
    u["LBPCONFIGDIR"] = str(LB / "config/plugins" / name)
    u["LBPLOGDIR"] = str(LB / "log/plugins" / name)
    u["LBPDATADIR"] = str(LB / "data/plugins" / name)
    u["LBPHTMLAUTHDIR"] = str(plugin_htmlauth)
    u["LBPHTMLDIR"] = str(plugin_htmlauth.parent / "html")
    u["LBPTEMPLATEDIR"] = str(plugin_htmlauth.parent.parent / "templates")
    u["LBPBINDIR"] = str(plugin_htmlauth.parent.parent / "bin")
    for k in ("LBPCONFIGDIR", "LBPLOGDIR", "LBPDATADIR"):
        Path(u[k]).mkdir(parents=True, exist_ok=True)
    return u


def zeile_holen(kopie: Path, praefix: str, php: str):
    """Rueckgabe: (stand, grund) oder (None, Fehlertext)."""
    ha = kopie / "webfrontend" / "htmlauth"
    probe = ha / "_eich_probe.php"
    probe.write_text(STUECK % {"p": praefix}, encoding="utf-8")
    try:
        r = subprocess.run(
            [php, "-n",
             "-d", "include_path=.;" + str(LB / "libs" / "phplib"),
             "-d", "auto_prepend_file=" + os.path.realpath(str(VORLAUF)),
             "-d", "display_errors=0", "-d", "error_reporting=32767",
             "-d", "date.timezone=Europe/Berlin",
             "-d", "extension_dir=" + str(Path(php).parent / "ext"),
             "-d", "extension=curl", "-d", "extension=openssl",
             "-d", "extension=mbstring", "-d", "extension=sockets",
             str(probe)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(ha), env=umgebung(ha, kopie.name.lower()), timeout=60)
    finally:
        probe.unlink(missing_ok=True)
    for z in r.stdout.splitlines():
        if z.startswith("###ZEILE###"):
            stand, _, grund = z[len("###ZEILE###"):].partition("|")
            return (int(stand), grund.strip())
    return (None, (r.stderr.strip() or r.stdout.strip() or "keine Ausgabe")[:200])


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    quelle = Path(sys.argv[1]).resolve()
    praefix = sys.argv[2]
    if praefix not in FAELLE:
        print("[FEHL] Unbekannter Praefix '%s'. Bekannt: %s"
              % (praefix, ", ".join(sorted(FAELLE))))
        return 2
    if not (quelle / "webfrontend").is_dir():
        print("[FEHL] %s sieht nicht wie ein Plugin-Ordner aus." % quelle)
        return 2

    phps = [(v, p) for v, p in PHPS if Path(p).is_file()]
    if not phps:
        print("[FEHL] Keine PHP-Fassung gefunden.")
        return 2

    fehl = 0
    gelaufen = 0
    for v, php in phps:
        print("== PHP %s" % v)
        # Ausgangslage. Ist die schon rot, sagt kein Eichfall danach etwas aus.
        tmp = Path(tempfile.mkdtemp(prefix="reiter_eich_"))
        try:
            kopie = tmp / quelle.name
            shutil.copytree(quelle, kopie)
            stand, grund = zeile_holen(kopie, praefix, php)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        gelaufen += 1
        if stand != 1:
            print("[FEHL] Ausgangszustand ist kein Haken (Stand %s): %s"
                  % (stand, grund))
            print("       Ohne gruene Ausgangslage misst kein Eichfall etwas -")
            print("       die %d Eichfaelle dieser Fassung wurden UEBERSPRUNGEN."
                  % len(FAELLE[praefix]))
            fehl += 1
            continue
        print("[ok  ] %-46s %s" % ("Ausgangszustand: Haken", grund[:70]))

        for beschreibung, datei, alt, neu, erwartet in FAELLE[praefix]:
            gelaufen += 1
            tmp = Path(tempfile.mkdtemp(prefix="reiter_eich_"))
            try:
                kopie = tmp / quelle.name
                shutil.copytree(quelle, kopie)
                p = kopie / datei
                b = p.read_bytes()
                # Byteweise, und der Anker wird GEZAEHLT: ein Anker, der
                # zweimal vorkommt, schneidet quer durch zwei Zweige, und eine
                # Eichung gegen kaputtes PHP ist wertlos.
                roh_alt = alt.encode("utf-8")
                roh_neu = neu.encode("utf-8")
                if b.count(b"\r\n") > b.count(b"\n") - b.count(b"\r\n"):
                    roh_alt = roh_alt.replace(b"\n", b"\r\n")
                    roh_neu = roh_neu.replace(b"\n", b"\r\n")
                if b.count(roh_alt) != 1:
                    print("[FEHL] %-46s Anker kommt %dx vor - nicht geeicht"
                          % (beschreibung, b.count(roh_alt)))
                    fehl += 1
                    continue
                p.write_bytes(b.replace(roh_alt, roh_neu))
                stand, grund = zeile_holen(kopie, praefix, php)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
            if stand is None:
                print("[FEHL] %-46s keine Antwort: %s" % (beschreibung, grund))
                fehl += 1
            elif stand == 1:
                print("[FEHL] %-46s bleibt HAKEN - die Zeile prueft das nicht"
                      % beschreibung)
                fehl += 1
            elif erwartet not in grund:
                # Rot ist nicht genug: eine Zeile, die aus dem falschen Grund
                # rot wird, wird beim naechsten Mal falsch behoben.
                print("[FEHL] %-46s wird rot, nennt aber nicht '%s': %s"
                      % (beschreibung, erwartet, grund[:90]))
                fehl += 1
            else:
                print("[ok  ] %-46s wird rot: %s" % (beschreibung, grund[:70]))

    print("")
    # Gezaehlt wird, was WIRKLICH gelaufen ist. Ein uebersprungener Eichfall
    # darf nicht als bestanden erscheinen - das ist derselbe Fehler wie ein
    # Strich, der sich wie ein Haken liest.
    erwartet = (len(FAELLE[praefix]) + 1) * len(phps)
    print("%d von %d gelaufenen Pruefungen in Ordnung (%d Eichfaelle je "
          "PHP-Fassung, dazu die Ausgangslage)."
          % (gelaufen - fehl, gelaufen, len(FAELLE[praefix])))
    if gelaufen < erwartet:
        print("ACHTUNG: %d von %d vorgesehenen Pruefungen sind nicht gelaufen."
              % (erwartet - gelaufen, erwartet))
    return 1 if fehl else 0


if __name__ == "__main__":
    sys.exit(main())
