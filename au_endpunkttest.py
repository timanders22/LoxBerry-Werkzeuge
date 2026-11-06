#!/usr/bin/env python3
"""Ruft den Miniserver-Endpunkt wirklich auf - unter PHP 7.4 und PHP 8.4.

Warum es das braucht: au_pruefen.py liest den Quelltext, au_neuerungstest.py
prueft den Python-Dienst. Was zwischen beiden liegt - die Antwortzeile, die
Loxone tatsaechlich bekommt - hat bis 0.9.7 niemand ausgefuehrt gesehen.
Genau dort steckten drei der gefundenen Fehler: das ungeschuetzte
mb_strtolower, die geratene Fehlerklasse und die Felder, die hinausgingen und
in keiner Tabelle standen.

Der Endpunkt spricht nie mit Audi. Er liest den Zwischenspeicher - und der
laesst sich schreiben. Damit ist der ganze Weg pruefbar, ohne Konto und ohne
Fahrzeug.

Aufruf:  au_endpunkttest.py [pluginordner]
"""

import json
import os
import subprocess
import re
import sys
import time
from pathlib import Path

HIER = Path(__file__).resolve().parent
LB = HIER / "lb"
# ERGAENZT 18.10.2026: AU_LB lenkt auf eine eigene Kopie der Attrappe um. Dieses
# Werkzeug schreibt config/plugins/audiconnect/audi.json und loxone.json - in
# der gemeinsamen Attrappe stoert das eine laufende Pruefkette (Marstek, 15:20).
# Ohne AU_LB nur unter .kette_sperre laufen lassen.
if os.environ.get("AU_LB"):
    LB = Path(os.environ["AU_LB"])
# vorlauf_getpost.php statt vorlauf.php: PHP fuellt unter der Kommandozeile
# $_GET NICHT aus QUERY_STRING. Ohne diesen Vorlauf sieht der Endpunkt keinen
# einzigen Parameter, antwortet folgerichtig mit GRUND=TOKEN - und ein
# Prueflauf, der das nicht bemerkt, misst den Pruefstand statt des Endpunkts.
VORLAUF = HIER / "vorlauf_getpost.php"
PHPS = [("7.4", r"C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe"),
        ("8.4", r"C:\tmp\php-8.4.27-Win32-vs17-x64\php.exe")]

def neuester_ordner(arbeit, praefix):
    """Der Pluginordner mit der HOECHSTEN Fassungsnummer.

    BERICHTIGT 31.08.2026. Die Vorgabe zeigte auf "LoxBerry-Plugin-AudiConnect-
    0.9.8" - den Ordner gibt es seit der 0.9.10 nicht mehr, und der Lauf endete
    mit einem FileNotFoundError auf au_lib.php statt mit einer Auskunft. Nach
    Fassungszahlen sortiert, nicht alphabetisch: sonst gewaenne 0.9.9 gegen
    0.9.10.
    """
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
# BERICHTIGT 31.08.2026: hier stand ORDNER = "audiconnect" fest. Solange das
# Werkzeug nur gegen AudiConnect laeuft, faellt das nicht auf - au_reitertest.py
# trug denselben festen Wert und wurde gegen Skoda-Connect-NG gerichtet. Es
# schob damit AudiConnects Abbild unter die fremde Oberflaeche und meldete
# 10 von 10 Laeufen rot. Der Befund war echt, die Messung nicht.
def ordner_aus_plugincfg(plugin):
    """FOLDER aus der plugin.cfg - der Name, unter dem LoxBerry die Ordner
    anlegt und unter dem die Attrappe bestueckt ist."""
    import re
    cfg = plugin / "plugin.cfg"
    if cfg.is_file():
        m = re.search(r"^\s*FOLDER\s*=\s*(\S+)\s*$",
                      cfg.read_text(encoding="utf-8", errors="replace"), re.M)
        if m:
            return m.group(1).lower()
    return plugin.name.lower()


ORDNER = ordner_aus_plugincfg(PLUGIN)

OK = FAIL = 0


def pruefe(name, ist, soll):
    global OK, FAIL
    if ist == soll:
        OK += 1
    else:
        FAIL += 1
        print("  [FEHL] %-46s ist=%r soll=%r" % (name, ist, soll))


def enthaelt(name, text, teil):
    global OK, FAIL
    if teil in text:
        OK += 1
    else:
        FAIL += 1
        print("  [FEHL] %-46s '%s' fehlt in: %s" % (name, teil, text[:160]))


def fehlt_nicht(name, text, teil):
    global OK, FAIL
    if teil not in text:
        OK += 1
    else:
        FAIL += 1
        print("  [FEHL] %-46s '%s' steht faelschlich in: %s" % (name, teil, text[:160]))


# ---------------------------------------------------------------------------
# Zwischenspeicher und Konfiguration schreiben
# ---------------------------------------------------------------------------
CONFIG = LB / "config/plugins" / ORDNER
DATA = LB / "data/plugins" / ORDNER
for d in (CONFIG, DATA):
    d.mkdir(parents=True, exist_ok=True)

TOKEN_LESEN = "lesetokenfuerdenpruefstand"
TOKEN_SCHALT = "schalttokenfuerdenpruefstand"

(CONFIG / "audi.json").write_text(json.dumps({
    "aktionstoken": TOKEN_LESEN,
    "schalttoken": TOKEN_SCHALT,
    "steuerung_ein": 0,
    "gefahr_ein": 0,
    "nur_miniserver": 0,
}), encoding="utf-8")

FAHRZEUG = {
    "vin": "WAUZZZF20PN000002", "modell": "A3 TFSI e",
    "soc": 62, "tank_prozent": 48, "reichweite_km": 478,
    "reichweite_elektro_km": 58, "reichweite_verbrenner_km": 420,
    "kilometerstand": 48210, "verriegelt": 0, "tueren_offen": 1,
    "tueren_anzahl": 2, "tueren_namen": "front_left, trunk",
    "fenster_offen": 1, "fenster_anzahl": 1, "fenster_namen": "front_left",
    "licht_an": 1, "licht_namen": "left", "handbremse": None,
    "klima_an": 1, "klima_stufe": 3, "klima_text": "ventilation",
    "zieltemperatur": 20.0, "aussentemperatur": -2.0, "scheibenheizung": 1,
    "scheibe_namen": "front, rear", "zustand": 1, "zustand_text": "parked",
    "erreichbar": 1, "aktiv": 1, "sitzheizung_ein": 1,
    "klima_bei_entriegeln": 1, "standzeit_min": 122, "fehlfolge": 0,
    "klima_fertig_um": int(time.time()) + 720,
    "laedt": 0, "lade_stufe": 2, "ladezustand_text": "ready_for_charging",
    "ladeleistung_kw": 0.0, "ladetempo_kmh": 0.0, "ladegrenze": 80,
    "ladestrom_a": 16, "kabel_verbunden": 1, "stecker_verriegelt": 1,
    "stecker_entriegeln": 1, "externe_kraft": 1, "ladeart_zahl": 1,
    "laden_fertig_um": int(time.time()) + 5400, "batterie_temp": 14.5,
    "verbrauch": 12.0, "ladekwh": 30.0, "ladeempf": 1,
    "inspektion_tage": 201, "inspektion_km": 14000,
    "oelservice_tage": 88, "oelservice_km": 9000, "adblue_km": 3800,
    "oelstand_prozent": None,
    "breite": 48.137154, "laenge": 11.576124, "positionsart_zahl": 1,
    "adresse": "Musterweg 7, Musterstadt", "zuhause": 1, "entfernung_m": 0,
    "saeule_name": "Stadtwerke Musterstadt", "ausfaelle": {}, "ok": 1,
}


def zwischenspeicher(ok=1, fehler="", code=0, alter=30):
    (DATA / "loxone.json").write_text(json.dumps({
        "ok": ok, "fehler": fehler, "fehler_code": code,
        "ts": int(time.time()) - alter,
        "letzter_versuch": int(time.time()),
        "anzahl_fahrzeuge": 1, "fahrzeuge": {"1": FAHRZEUG},
    }), encoding="utf-8")


def ruf(php, woher="192.168.1.99", **parameter):
    umg = dict(os.environ)
    umg["LBHOMEDIR"] = str(LB)
    umg["LBPPLUGINDIR"] = ORDNER
    umg["REQUEST_METHOD"] = "GET"
    umg["HTTP_HOST"] = "loxberry.pruefstand"
    umg["REMOTE_ADDR"] = woher
    umg["QUERY_STRING"] = "&".join("%s=%s" % kv for kv in parameter.items())
    r = subprocess.run(
        [php, "-n", "-d", "include_path=.;" + str(LB / "libs" / "phplib"),
         "-d", "auto_prepend_file=" + str(VORLAUF),
         "-d", "display_errors=0", "-d", "error_reporting=32767",
         "-d", "date.timezone=Europe/Berlin",
         "-d", "extension_dir=" + str(Path(php).parent / "ext"),
         "-d", "extension=mbstring", "-d", "extension=openssl",
         str((PLUGIN / "webfrontend/html/index.php").resolve())],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str((PLUGIN / "webfrontend/html").resolve()), env=umg, timeout=60)
    befunde = []
    if "###BEFUNDE###" in r.stderr:
        befunde = [z for z in r.stderr.split("###BEFUNDE###", 1)[1].strip().splitlines()
                   if z.strip()]
    return r.stdout, befunde


# Der Endpunkt liegt unter webfrontend/html/; au_paths() leitet den
# Pluginordner aus dem ABLAGEORT ab. Damit die Attrappe greift, wird die
# Bibliothek dorthin gespiegelt, wo eine Installation sie haette.
ZIEL = LB / "webfrontend/html/plugins" / ORDNER
ZIEL.mkdir(parents=True, exist_ok=True)
# ERGAENZT 18.10.2026: seit 0.9.25 bindet au_lib.php die gemeinsame
# sprachausgabe.php ein (require_once). Ohne sie endete jeder Aufruf mit FATAL,
# die Antwort war leer, und der Lauf brach bei "position" mit IndexError ab.
# Fehlt sie im Plugin, obwohl au_lib.php sie verlangt, wird das gesagt: eine
# Abschrift vom vorigen Lauf laege sonst noch in der Attrappe und machte den
# Lauf gruen (gemessen 18.10.2026 an einer Kopie ohne die Datei).
_spiegel = ["au_lib.php", "index.php"]
if "sprachausgabe.php" in (PLUGIN / "webfrontend/html/au_lib.php").read_text(
        encoding="utf-8", errors="replace"):
    if not (PLUGIN / "webfrontend/html/sprachausgabe.php").is_file():
        print("  [FEHL] au_lib.php bindet sprachausgabe.php ein, die Datei fehlt "
              "in webfrontend/html/ - der Endpunkt endet am Geraet mit FATAL.")
        print()
        print("0 bestanden, 1 durchgefallen")
        sys.exit(1)
    _spiegel.append("sprachausgabe.php")
for name in _spiegel:
    (ZIEL / name).write_bytes((PLUGIN / "webfrontend/html" / name).read_bytes())
LANG = LB / "templates/plugins" / ORDNER / "lang"
LANG.mkdir(parents=True, exist_ok=True)
for name in ("language_de.ini", "language_en.ini"):
    (LANG / name).write_bytes((PLUGIN / "templates/lang" / name).read_bytes())


class Umleitung:
    """Der Endpunkt wird aus dem gespiegelten Ort gerufen, nicht aus dem Archiv."""
    pfad = ZIEL / "index.php"


PLUGIN_ECHT = PLUGIN
PLUGIN = type("P", (), {"__truediv__": lambda self, x: (
    ZIEL / "index.php" if str(x) == "webfrontend/html/index.php"
    else ZIEL if str(x) == "webfrontend/html" else PLUGIN_ECHT / x)})()

for fassung, php in PHPS:
    if not Path(php).is_file():
        print("[INFO] PHP %s nicht vorhanden - uebersprungen." % fassung)
        continue
    print("=== PHP " + fassung)

    # Jeder Durchlauf beginnt mit derselben Ausgangslage. Ohne diese Zeilen
    # nimmt der zweite PHP-Lauf die Konfiguration mit, die der erste am Ende
    # hinterlassen hat - und misst dann etwas anderes als der erste, ohne dass
    # es auffaellt.
    (CONFIG / "audi.json").write_text(json.dumps({
        "aktionstoken": TOKEN_LESEN, "schalttoken": TOKEN_SCHALT,
        "steuerung_ein": 0, "gefahr_ein": 0, "nur_miniserver": 0}), encoding="utf-8")

    # ---------------- Regelfall ----------------
    zwischenspeicher()
    aus, bef = ruf(php, token=TOKEN_LESEN, aktion="status", fahrzeug="1")
    pruefe("status: keine PHP-Befunde", bef, [])
    zeile = aus.strip().splitlines()[0] if aus.strip() else ""
    enthaelt("status beginnt richtig", zeile, "AUDI;OK=1;")
    for stueck in ("SOC=62", "TANK=48", "REICHW=478", "REICHWVERBR=420",
                   "KM=48210", "VERR=0", "TUEREN=1", "TUERANZ=2",
                   "FENSTERANZ=1", "KLIMAART=3", "SITZHEIZ=1", "AKTIV=1",
                   "STANDZEIT=122", "ZUHAUSE=1", "ENTF=0", "FZOK=1",
                   "AUSFALL=0", "FEHLFOLGE=0", "GRUND=0"):
        enthaelt("status enthaelt " + stueck, zeile, ";" + stueck)
    # Ein Wert, den der Connector nie liefert, muss ein Strich sein - keine 0.
    enthaelt("nicht geliefertes Feld ist ein Strich", zeile, ";HANDBR=-")
    # KLIMAFERTIG wird aus dem Zeitstempel gerechnet: rund 12 Minuten.
    minuten = [t for t in zeile.split(";") if t.startswith("KLIMAFERTIG=")]
    pruefe("KLIMAFERTIG gerechnet", minuten and minuten[0] in
           ("KLIMAFERTIG=12", "KLIMAFERTIG=13"), True)
    fehlt_nicht("kein FEHLERTEXT im Regelfall", zeile, "FEHLERTEXT=")

    aus, bef = ruf(php, token=TOKEN_LESEN, aktion="laden", fahrzeug="1")
    pruefe("laden: keine PHP-Befunde", bef, [])
    z = aus.strip()
    enthaelt("laden beginnt richtig", z, "LADEN;OK=1;")
    for stueck in ("LADESTUFE=2", "LADEART=1", "EXTSTROM=1", "STECKERAUTO=1",
                   "BATTTEMP=14.5", "VERBRAUCH=12", "LADEKWH=30", "LADEEMPF=1",
                   "REICHWBAT=58", "ALTER="):
        enthaelt("laden enthaelt " + stueck, z, ";" + stueck)

    aus, bef = ruf(php, token=TOKEN_LESEN, aktion="wartung", fahrzeug="1")
    pruefe("wartung: keine PHP-Befunde", bef, [])
    z = aus.strip()
    enthaelt("wartung: AdBlue", z, ";ADBLUE=3800")
    enthaelt("wartung: Kilometerstand", z, ";KM=48210")
    enthaelt("wartung: Inspektionskilometer", z, ";INSPKM=14000")
    # Der Kilometerstand darf NICHT von INSPKM getroffen werden - dafuer
    # traegt jeder Suchtext das Semikolon. Gegenprobe an der echten Antwort:
    pruefe("KM kommt genau einmal mit Semikolon vor", z.count(";KM="), 1)

    aus, bef = ruf(php, token=TOKEN_LESEN, aktion="position", fahrzeug="1")
    pruefe("position: keine PHP-Befunde", bef, [])
    # Leere Antwort ist ein FEHL, kein IndexError (18.10.2026: so brach der
    # Lauf ab, als sprachausgabe.php in der Attrappe fehlte).
    zeilen = (aus.strip().splitlines() + ["", ""])[:2]
    enthaelt("position: Breite", zeilen[0], ";BREITE=48.137154")
    enthaelt("position: Art", zeilen[0], ";POSART=1")
    pruefe("position: zweite Zeile ist die Anschrift",
           zeilen[1], "ADRESSE;Musterweg 7, Musterstadt")

    aus, bef = ruf(php, token=TOKEN_LESEN, aktion="text", fahrzeug="1")
    pruefe("text: keine PHP-Befunde", bef, [])
    enthaelt("text: Zustand im Klartext", aus, "ZUSTAND=parked")
    enthaelt("text: welche Tuer", aus, "TUEREN=front_left, trunk")
    enthaelt("text: Ladesaeule", aus, "SAEULE=Stadtwerke Musterstadt")

    # ---------------- Die Suchtexte an der ECHTEN Antwort ----------------
    #
    # Werkzeuge/suchmuster_pruefen.py liest den Quelltext und kann seit 0.9.8
    # die Antwortzeilen nicht mehr finden - sie sind keine Zeichenketten mehr,
    # sondern entstehen aus der Feldliste. Es meldet ein fehlendes Trennzeichen
    # deshalb nur noch als RISIKO ("heute kein Namenspaar, das kollidiert"),
    # weil ihm die Zeile zum Gegenmessen fehlt.
    #
    # Hier ist sie. Geprueft wird die Eigenschaft, auf die es ankommt: der
    # Suchtext jedes Feldes muss in der Antwort GENAU EINMAL vorkommen, und
    # unmittelbar dahinter muss der Wert dieses Feldes stehen - nicht der eines
    # anderen, dessen Name auf denselben Buchstaben endet. Genau das ging bis
    # 0.9.6 schief: \iKM= traf INSPKM=15000 statt KM=48210.
    antworten = {}
    for art, kopf in (("status", "AUDI"), ("laden", "LADEN"),
                      ("wartung", "WARTUNG"), ("position", "POSITION")):
        zwischenspeicher()
        a, _ = ruf(php, token=TOKEN_LESEN, aktion=art, fahrzeug="1")
        antworten[art] = a.strip().splitlines()[0] if a.strip() else ""

    suchtexte, _ = ruf(php, token=TOKEN_LESEN, aktion="status", fahrzeug="1")
    # Die Suchtexte holt das Plugin selbst - nicht dieses Skript. Ein
    # nachgebauter Suchtext pruefte den Nachbau.
    hilfs = ZIEL / "_suchtexte.php"
    hilfs.write_text(
        "<?php require_once __DIR__ . '/au_lib.php';\n"
        "foreach (array('status','laden','wartung','position') as $z) {\n"
        "  foreach (au_felder_von($z) as $f => $i) {\n"
        "    if ($f === 'FEHLERTEXT') { continue; }\n"
        "    echo $z . '|' . $f . '|' . au_check($f) . \"\\n\";\n"
        "  }\n"
        "}\n", encoding="utf-8")
    r = subprocess.run(
        [php, "-n", "-d", "include_path=.;" + str(LB / "libs" / "phplib"),
         "-d", "display_errors=0", "-d", "date.timezone=Europe/Berlin",
         str(hilfs)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**os.environ, "LBHOMEDIR": str(LB), "LBPPLUGINDIR": ORDNER},
        cwd=str(ZIEL), timeout=60)
    paare = [z.split("|", 2) for z in r.stdout.strip().splitlines() if z.count("|") == 2]
    pruefe("Suchtexte ausgelesen", len(paare) > 60, True)
    for zeile, feld, muster in paare:
        # \i;NAME=\i\v  ->  der wortwoertliche Teil ist ';NAME='
        wortwoertlich = muster.replace("\\i", "").replace("\\v", "")
        antwort = antworten[zeile]
        treffer = antwort.count(wortwoertlich)
        if treffer != 1:
            pruefe("Suchtext %s/%s kommt genau einmal vor" % (zeile, feld), treffer, 1)
            continue
        hinter = antwort.split(wortwoertlich, 1)[1].split(";")[0]
        soll = antwort.split(";")
        # Der Wert hinter dem Suchtext muss zu DIESEM Feld gehoeren.
        eigen = [t.split("=", 1)[1] for t in soll if t.split("=", 1)[0] == feld]
        pruefe("Suchtext %s/%s trifft das eigene Feld" % (zeile, feld),
               hinter, eigen[0] if eigen else "<fehlt>")
    hilfs.unlink()

    # ---------------- Absicherung ----------------
    aus, bef = ruf(php, aktion="status")
    enthaelt("ohne Token abgewiesen", aus, "GRUND=TOKEN")
    aus, bef = ruf(php, token="falsch", aktion="status")
    enthaelt("falsches Token abgewiesen", aus, "GRUND=TOKEN")
    aus, bef = ruf(php, token=TOKEN_LESEN, aktion="quatsch")
    enthaelt("unbekannte Aktion abgewiesen", aus, "GRUND=UNBEKANNTE_AKTION")
    aus, bef = ruf(php, token=TOKEN_LESEN, aktion="status", fahrzeug="'; rm -rf /")
    enthaelt("boeser Parameter abgewiesen", aus, "GRUND=PARAMETER")

    # Das Lesetoken darf nicht schalten - der Kern der Trennung.
    aus, bef = ruf(php, token=TOKEN_LESEN, aktion="wecken", fahrzeug="1")
    pruefe("Lesetoken schaltet nicht: keine PHP-Befunde", bef, [])
    enthaelt("Lesetoken schaltet nicht", aus, "GRUND=LESETOKEN_SCHALTET_NICHT")

    # Mit dem Schalttoken kommt man bis zur Steuerungssperre - und nicht weiter.
    aus, bef = ruf(php, token=TOKEN_SCHALT, aktion="wecken", fahrzeug="1")
    enthaelt("gesperrte Steuerung", aus, "GRUND=STEUERUNG_AUS")

    # Eingreifender Befehl bei freigegebener Steuerung, aber ohne zweiten Haken.
    (CONFIG / "audi.json").write_text(json.dumps({
        "aktionstoken": TOKEN_LESEN, "schalttoken": TOKEN_SCHALT,
        "steuerung_ein": 1, "gefahr_ein": 0, "nur_miniserver": 0}), encoding="utf-8")
    aus, bef = ruf(php, token=TOKEN_SCHALT, aktion="entriegeln", fahrzeug="1")
    enthaelt("Eingriff ohne zweiten Haken gesperrt", aus, "GRUND=EINGRIFF_GESPERRT")
    # Ein gewoehnlicher Befehl kommt dagegen bis zur Dienstpruefung.
    aus, bef = ruf(php, token=TOKEN_SCHALT, aktion="wecken", fahrzeug="1")
    enthaelt("ohne laufenden Dienst wird nicht eingereiht", aus,
             "GRUND=DIENST_LAEUFT_NICHT")

    # ---------------- Stoerungsfall ----------------
    # Genau hier lag der alte Fehler: die Klasse wurde aus dem deutschen Text
    # geraten und war fast immer 9.
    (CONFIG / "audi.json").write_text(json.dumps({
        "aktionstoken": TOKEN_LESEN, "schalttoken": TOKEN_SCHALT,
        "steuerung_ein": 0, "gefahr_ein": 0, "nur_miniserver": 0}), encoding="utf-8")
    zwischenspeicher(ok=0, code=3,
                     fehler="Audi hat wegen zu vieler Anfragen abgewiesen. Den Takt "
                            "in den Einstellungen vergroessern; unter 300 Sekunden "
                            "ist erfahrungsgemaess zu dicht.")
    aus, bef = ruf(php, token=TOKEN_LESEN, aktion="status", fahrzeug="1")
    pruefe("Stoerung: keine PHP-Befunde", bef, [])
    z = aus.strip()
    # BERICHTIGT 18.10.2026: seit 0.9.22 (C6/U14, Entscheidung 4) setzt ein
    # einzelner misslungener Abruf OK NICHT auf 0 - das Abbild ist 30 s alt und
    # gilt noch, GRUND nennt die Stoerung. OK=0 kommt erst mit dem Alter (unten).
    enthaelt("Stoerung: OK=1 bei frischem Abbild", z, "AUDI;OK=1;")
    enthaelt("Stoerung: Klasse 3 statt 9", z, ";GRUND=3;")
    enthaelt("Stoerung: Klartext dabei", z, "FEHLERTEXT=Audi hat wegen zu vieler")
    pruefe("Stoerungstext enthaelt kein Semikolon",
           (z.split("FEHLERTEXT=") + [""])[1].count(";"), 0)
    # Die alten Werte bleiben stehen - Loxone behaelt sie ohnehin.
    enthaelt("Stoerung: letzter Ladezustand bleibt", z, ";SOC=62")

    # Abbild aelter als das Dreifache des Takts (Takt mindestens 180 s), der
    # letzte Abruf gelang: OK=0 und GRUND=10 ("laeuft der Dienst?").
    zwischenspeicher(alter=100000)
    aus, bef = ruf(php, token=TOKEN_LESEN, aktion="status", fahrzeug="1")
    pruefe("veraltetes Abbild: keine PHP-Befunde", bef, [])
    z = aus.strip()
    enthaelt("veraltetes Abbild: OK=0", z, "AUDI;OK=0;")
    enthaelt("veraltetes Abbild: Klasse 10", z, ";GRUND=10;")

    # ---------------- Beschraenkung auf den Miniserver ----------------
    #
    # Die Attrappe fuehrt einen Miniserver unter 192.0.2.10 (Dokumentationsnetz, bis 18.10.2026 192.168.1.10) - nachgesehen in
    # lb/config/system/general.json, nicht angenommen. Der erste Anlauf dieser
    # Zeilen ging davon aus, es sei keiner hinterlegt, und beanstandete
    # daraufhin das richtige Verhalten.
    (CONFIG / "audi.json").write_text(json.dumps({
        "aktionstoken": TOKEN_LESEN, "schalttoken": TOKEN_SCHALT,
        "steuerung_ein": 0, "gefahr_ein": 0, "nur_miniserver": 1}), encoding="utf-8")
    zwischenspeicher()
    aus, bef = ruf(php, woher="192.0.2.10", token=TOKEN_LESEN,
                   aktion="status", fahrzeug="1")
    pruefe("Miniserver-Haken: keine PHP-Befunde", bef, [])
    enthaelt("vom Miniserver kommt die Antwort", aus, "AUDI;OK=1;")
    aus, bef = ruf(php, woher="192.168.1.99", token=TOKEN_LESEN,
                   aktion="status", fahrzeug="1")
    enthaelt("von fremder Adresse abgewiesen", aus, "GRUND=FREMDE_ADRESSE")
    aus, bef = ruf(php, woher="127.0.0.1", token=TOKEN_LESEN,
                   aktion="status", fahrzeug="1")
    enthaelt("vom LoxBerry selbst weiterhin erlaubt", aus, "AUDI;OK=1;")

print()
print("%d bestanden, %d durchgefallen" % (OK, FAIL))
sys.exit(1 if FAIL else 0)
