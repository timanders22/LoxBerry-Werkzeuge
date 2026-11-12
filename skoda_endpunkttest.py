#!/usr/bin/env python3
"""Ruft den Miniserver-Endpunkt von Skoda Connect NG wirklich auf - als CGI,
unter PHP 7.4 UND PHP 8.4.

WARUM ES DAS BRAUCHT. skoda_befehlstest.py und skoda_funktionstest.py laden
beide nur bin/skoda.py und starten NIE einen PHP-Prozess. Der einzige oeffentlich
erreichbare Teil des Plugins - webfrontend/html/index.php - war damit vollstaendig
ungeprueft: kein Statuscode, kein Content-Type, keine einzige Antwortzeile.

WARUM php-cgi UND NICHT php.exe. Die Kommandozeile (CLI-SAPI) kennt keine
Kopfzeilen: header() ist dort ein Nichtstuer und headers_list() bleibt leer.
Ein Prueflauf ueber php.exe kann also nur die Zeichenkette vergleichen - und
sieht damit genau das nicht, was die Hausregel ausdruecklich verlangt: eine
PHP-Warnung VOR http_response_code() nimmt dem Aufrufer den Statuscode weg,
die Abweisung kommt als HTTP 200 an, und die Antwortzeile ist trotzdem richtig.
Die CGI-SAPI schreibt Status und Content-Type in den Kopf, so wie der Webserver
sie ausliefert, und fuellt $_GET selbst aus QUERY_STRING - auch die Feldform
?token[]=x, die ein nachgebauter Vorlauf nur simulieren wuerde.

GEMESSEN WIRD JE FALL: Statuscode, Content-Type, erste Zeile, ob eine PHP-
Meldung anfiel und ob eine Datei in der Warteschlange entstanden ist.

EIGENE PRUEFBANK. LBHOMEDIR zeigt auf ein Wegwerfverzeichnis, das dieser Lauf
selbst anlegt und am Ende wieder abraeumt. Werkzeuge/lb wird NICHT angefasst.
Der Ordnername kommt aus FOLDER= der plugin.cfg des geprueften Plugins - nicht
fest verdrahtet. au_reitertest.py hatte "audiconnect" im Quelltext stehen und
mass dadurch jedes Plugin an fremden Daten.

Die Aktionslisten werden nicht von Hand gefuehrt, sondern mit sk_lesende() und
sk_befehle() aus dem Plugin selbst geholt. Sonst prueft dieses Werkzeug nach der
naechsten neuen Aktion weiterhin die alten.

Aufruf:  skoda_endpunkttest.py [pluginordner]
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.dont_write_bytecode = True

HIER = Path(__file__).resolve().parent
VORLAUF = HIER / "vorlauf.php"
PHPS = [("7.4", r"C:\tmp\php-7.4.33-Win32-vc15-x64"),
        ("8.4", r"C:\tmp\php-8.4.27-Win32-vs17-x64")]

TOKEN = "pruefstandstoken1234"

PRUEFUNGEN = 0
BEANSTANDUNGEN = 0
ANTWORTEN = []          # jede Antwort dieses Laufs, fuer die Schlussdurchsicht
QUER = {}               # Werte, die zwischen den PHP-Fassungen verglichen werden


# ---------------------------------------------------------------------------
# Zaehlwerk
# ---------------------------------------------------------------------------

def pruefe(name, ist, soll):
    global PRUEFUNGEN, BEANSTANDUNGEN
    PRUEFUNGEN += 1
    if ist == soll:
        return True
    BEANSTANDUNGEN += 1
    print("  [BEFUND] %-52s ist=%r soll=%r" % (name, ist, soll))
    return False


def enthaelt(name, text, teil):
    global PRUEFUNGEN, BEANSTANDUNGEN
    PRUEFUNGEN += 1
    if teil in text:
        return True
    BEANSTANDUNGEN += 1
    print("  [BEFUND] %-52s '%s' fehlt in: %s" % (name, teil, text[:150]))
    return False


def fehlt_nicht(name, text, teil):
    global PRUEFUNGEN, BEANSTANDUNGEN
    PRUEFUNGEN += 1
    if teil not in text:
        return True
    BEANSTANDUNGEN += 1
    print("  [BEFUND] %-52s '%s' steht faelschlich in: %s" % (name, teil, text[:150]))
    return False


def nichts_gemessen(name, was):
    """Ein Suchmuster, das nichts findet, ist ein Befund - kein Bestehen.

    Drei Werkzeuge im Bestand haben still nichts gemessen und dabei gruen
    gemeldet. Jede Stelle, an der dieses Werkzeug etwas SUCHT, geht durch
    diese Funktion."""
    global PRUEFUNGEN, BEANSTANDUNGEN
    PRUEFUNGEN += 1
    BEANSTANDUNGEN += 1
    print("  [BEFUND] %-52s hat nichts gemessen: %s" % (name, was))


def feld(zeile, name):
    """Der Wert eines Feldes NAME=... aus einer Antwortzeile, sonst <fehlt>."""
    for t in zeile.split(";"):
        if t.startswith(name + "="):
            return t.split("=", 1)[1]
    return "<fehlt>"


# ---------------------------------------------------------------------------
# Pluginordner und Ordnername
# ---------------------------------------------------------------------------

def neuester_skoda():
    """Den aktuellen Skoda-Ordner suchen - nicht auf eine Fassung verdrahten."""
    kandidaten = []
    for d in HIER.parent.iterdir():
        if d.is_dir() and d.name.startswith("LoxBerry-Plugin-Skoda-Connect-NG-"):
            teil = d.name.rsplit("-", 1)[-1]
            schluessel = tuple(int(x) if x.isdigit() else 0 for x in teil.split("."))
            kandidaten.append((schluessel, d))
    if not kandidaten:
        print("[ABBRUCH] Kein Ordner LoxBerry-Plugin-Skoda-Connect-NG-* gefunden.")
        sys.exit(2)
    return sorted(kandidaten)[-1][1]


PLUGIN = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else neuester_skoda()
if not (PLUGIN / "webfrontend/html/index.php").is_file():
    print("[ABBRUCH] %s ist kein Skoda-Pluginordner." % PLUGIN)
    sys.exit(2)


def ordner_aus_cfg(pfad):
    """FOLDER= aus der plugin.cfg des GEPRUEFTEN Plugins - nicht geraten."""
    if not pfad.is_file():
        return ""
    for zeile in pfad.read_text(encoding="utf-8", errors="replace").splitlines():
        z = zeile.strip()
        if z.upper().startswith("FOLDER="):
            return z.split("=", 1)[1].strip()
    return ""


ORDNER = ordner_aus_cfg(PLUGIN / "plugin.cfg")
if not ORDNER:
    print("[ABBRUCH] In %s/plugin.cfg steht kein FOLDER=." % PLUGIN.name)
    sys.exit(2)

print("Plugin:  %s" % PLUGIN.name)
print("Ordner:  %s (aus plugin.cfg)" % ORDNER)


# ---------------------------------------------------------------------------
# Pruefbank aufbauen
# ---------------------------------------------------------------------------
BANK = Path(tempfile.mkdtemp(prefix="sk_endpunkt_"))
CONFIG = BANK / "config/plugins" / ORDNER
DATA = BANK / "data/plugins" / ORDNER
LANG = BANK / "templates/plugins" / ORDNER / "lang"
ZIEL = BANK / "webfrontend/html/plugins" / ORDNER
SICHERUNG = BANK / "config/plugins" / (ORDNER + ".backup.skoda.json")
for d in (CONFIG, DATA, LANG, ZIEL):
    d.mkdir(parents=True, exist_ok=True)
# Der Endpunkt leitet seinen Pluginordner aus dem ABLAGEORT ab; die Bibliothek
# muss also dort liegen, wo eine Installation sie haette. Kopiert wird, nie
# verschoben - das Archiv bleibt unberuehrt.
for name in ("index.php", "sk_lib.php"):
    (ZIEL / name).write_bytes((PLUGIN / "webfrontend/html" / name).read_bytes())
for name in ("language_de.ini", "language_en.ini"):
    quelle = PLUGIN / "templates/lang" / name
    if quelle.is_file():
        (LANG / name).write_bytes(quelle.read_bytes())
# Der Vorlauf kommt als Kopie MIT KURZEM NAMEN in den Arbeitsordner: php-cgi
# verschluckt unter Windows alle -d-Angaben ab der ersten, deren Wert ein
# Leerzeichen enthaelt - und der Name des Arbeitsordners enthaelt zwei. Gemessen am
# 31.08.2026: mit dem langen Pfad wirkte weder auto_prepend_file noch das
# danach stehende display_errors, und der Lauf sah trotzdem gruen aus.
(ZIEL / "_vorlauf.php").write_bytes(VORLAUF.read_bytes())


def bank_leeren():
    """Vor jedem PHP-Durchlauf dieselbe Ausgangslage.

    Ohne diese Zeilen nimmt der zweite Durchlauf mit, was der erste hinterlassen
    hat - und misst dann etwas anderes als der erste, ohne dass es auffaellt."""
    for d in (DATA,):
        if d.is_dir():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)
    if SICHERUNG.is_file():
        SICHERUNG.unlink()
    konfig()


def konfig(**zusatz):
    werte = {"aktionstoken": TOKEN, "steuerung_ein": 0, "intervall": 300,
             "wartezeit": 0}
    werte.update(zusatz)
    (CONFIG / "skoda.json").write_text(
        json.dumps(werte, ensure_ascii=False), encoding="utf-8", newline="\n")


def fahrzeug(nr, vin, modell, **zusatz):
    f = {
        "vin": vin, "modell": modell, "kennzeichen": "M-XY %d" % (1000 + nr),
        "soc": 62, "tank_prozent": 48, "reichweite_km": 478,
        "reichweite_batterie_km": 210, "kilometerstand": 48210,
        "verriegelt": 1, "tueren_offen": 0, "fenster_offen": 0,
        "kofferraum_offen": 0, "motorhaube_offen": 0, "licht_an": 0,
        "klima_an": 1, "zieltemperatur": 21.0, "aussentemperatur": 14.5,
        "warnleuchten": 0, "erreichbar": 1, "in_bewegung": 0, "zuendung_an": 0,
        "zuhause": 1, "heim_entfernung_m": 12, "laedt": 0,
        "ladeleistung_kw": 0.0, "ladetempo_kmh": 0.0, "restzeit_min": 0,
        "ladegrenze": 80, "kabel_verbunden": 1,
        "inspektion_tage": 201, "inspektion_km": 14000,
        "oelservice_tage": 88, "oelservice_km": 9000,
        "breite": 48.137154, "laenge": 11.576124,
        "adresse": "Musterweg 7, Musterstadt",
        "ausfaelle_n": 0, "ok": 1,
    }
    f.update(zusatz)
    return f


VIN1 = "TMBJJ7NE1J0000001"
VIN2 = "TMBJJ7NE1J0000002"


def abbild(alter=30, ok=1, modell2="Enyaq iV 80", **fz2):
    """loxone.json mit zwei Fahrzeugen schreiben. alter negativ = Zukunft."""
    (DATA / "loxone.json").write_text(json.dumps({
        "ok": ok, "fehler": "", "ts": int(time.time()) - alter,
        "letzter_versuch": int(time.time()), "zaehler": 7, "empfehlung": 1,
        "anzahl_fahrzeuge": 2,
        "fahrzeuge": {"1": fahrzeug(1, VIN1, "Octavia iV"),
                      "2": fahrzeug(2, VIN2, modell2, **fz2)},
    }, ensure_ascii=False), encoding="utf-8", newline="\n")


def ladungen_schreiben():
    """ladungen.csv mit je einer Ladung pro Fahrzeug.

    Spalten: beginn;ende;fahrzeug;vin;soc_von;soc_bis;dauer_min;kw_max;ort"""
    jetzt = int(time.time())
    zeilen = ["beginn;ende;fahrzeug;vin;soc_von;soc_bis;dauer_min;kw_max;ort",
              "%d;%d;1;%s;20;80;120;11.0;Zuhause" % (jetzt - 7200, jetzt - 3600, VIN1),
              "%d;%d;2;%s;30;90;100;50.0;Autohof" % (jetzt - 5400, jetzt - 1800, VIN2)]
    (DATA / "ladungen.csv").write_text("\n".join(zeilen) + "\n",
                                       encoding="utf-8", newline="\n")


def warteschlange():
    """Die Dateien in data/plugins/<ordner>/befehle.

    WAS DIESE ZEILEN AUF WINDOWS KOENNEN UND WAS NICHT. sk_dienst_pid() sieht
    in /proc nach; unter Windows gibt es das nicht, der Dienst gilt also immer
    als gestoppt, und sk_befehl_absetzen() kommt nie bis zum Schreiben. Eine
    Beanstandung kann hier deshalb nur eines bedeuten - und genau darum geht
    es: index.php hat eine Befehlsdatei angelegt, BEVOR es Token, Fahrzeug,
    Steuerungssperre und Dienst geprueft hat. Dass die Warteschlange im
    Regelfall leer bleibt, ist kein Beleg dafuer, dass das Einreihen selbst
    richtig arbeitet; das misst skoda_befehlstest.py am Dienst."""
    o = DATA / "befehle"
    return sorted(p.name for p in o.glob("*")) if o.is_dir() else []


# ---------------------------------------------------------------------------
# Der Aufruf
# ---------------------------------------------------------------------------

class Antwort(object):
    def __init__(self, name, code, ctype, rumpf, befunde, rest, roh, angezeigt):
        self.name = name
        self.code = code
        self.ctype = ctype
        self.rumpf = rumpf            # bytes, unveraendert
        self.text = rumpf.decode("utf-8", "replace")
        self.zeile1 = self.text.split("\n", 1)[0]
        self.befunde = befunde
        self.rest = rest
        self.roh = roh                # aktion=roh: JSON statt Klartext
        self.angezeigt = angezeigt    # mit display_errors=1 gemessen


def ruf(php_dir, name, qs, zeige_fehler=False):
    """Einen echten CGI-Aufruf gegen webfrontend/html/index.php."""
    umg = dict(os.environ)
    umg["LBHOMEDIR"] = str(BANK)
    umg["LBPPLUGINDIR"] = ORDNER
    umg["LBLANG"] = "de"
    umg["GATEWAY_INTERFACE"] = "CGI/1.1"
    umg["SERVER_PROTOCOL"] = "HTTP/1.1"
    umg["REQUEST_METHOD"] = "GET"
    umg["SCRIPT_FILENAME"] = str(ZIEL / "index.php")
    umg["SCRIPT_NAME"] = "/plugins/%s/index.php" % ORDNER
    umg["REQUEST_URI"] = "/plugins/%s/index.php?%s" % (ORDNER, qs)
    umg["QUERY_STRING"] = qs
    umg["HTTP_HOST"] = "loxberry.pruefstand"
    umg["SERVER_NAME"] = "loxberry.pruefstand"
    umg["REMOTE_ADDR"] = "192.168.1.99"
    umg["CONTENT_LENGTH"] = "0"
    umg["REDIRECT_STATUS"] = "1"
    schalter = [str(Path(php_dir) / "php-cgi.exe"), "-n",
                "-d", "display_errors=" + ("1" if zeige_fehler else "0"),
                "-d", "html_errors=0",
                "-d", "error_reporting=32767",
                "-d", "date.timezone=Europe/Berlin",
                "-d", "extension_dir=" + str(Path(php_dir) / "ext"),
                "-d", "extension=mbstring"]
    if not zeige_fehler:
        # Der Vorlauf faengt JEDE Meldung ab und gibt sie ueber stderr aus -
        # auch die, die das Plugin sich selbst mit error_reporting() abstellt.
        schalter += ["-d", "auto_prepend_file=_vorlauf.php"]
    # Bei zeige_fehler bleibt er ABSICHTLICH weg: sein Aufnehmer gibt true
    # zurueck und unterdrueckt damit die PHP-eigene Ausgabe - also genau das,
    # was diese Messung im Rumpf sehen soll. Mit Vorlauf ist der Rumpf immer
    # sauber, und die Zeile bestuende gruen, ohne etwas gemessen zu haben.
    r = subprocess.run(schalter, capture_output=True, cwd=str(ZIEL), env=umg,
                       timeout=60)
    aus = r.stdout
    kopf, _, rumpf = aus.partition(b"\r\n\r\n")
    code = 200
    ctype = ""
    for zeile in kopf.decode("utf-8", "replace").split("\r\n"):
        k, _, w = zeile.partition(":")
        if k.strip().lower() == "status":
            m = re.match(r"\s*(\d{3})", w)
            if m:
                code = int(m.group(1))
        elif k.strip().lower() == "content-type":
            ctype = w.strip()
    fehler = r.stderr.decode("utf-8", "replace")
    befunde = []
    if "###BEFUNDE###" in fehler:
        befunde = [z for z in fehler.split("###BEFUNDE###", 1)[1].strip().splitlines()
                   if z.strip()]
    rest = fehler.split("###BEFUNDE###")[0].strip()
    a = Antwort(name, code, ctype, rumpf, befunde, rest,
                "aktion=roh" in qs, zeige_fehler)
    ANTWORTEN.append(a)
    return a


def antwort_pruefen(name, a, code, grund=None, befunde_leer=True):
    """Statuscode, Grund und PHP-Meldungen in einem - die drei Fragen, die zu
    jedem Fall gehoeren."""
    pruefe(name + ": Statuscode", a.code, code)
    if grund is not None:
        pruefe(name + ": GRUND", feld(a.zeile1, "GRUND"), grund)
    if befunde_leer:
        pruefe(name + ": keine PHP-Meldung", a.befunde, [])


# ---------------------------------------------------------------------------
# Die Aktionslisten aus dem Plugin holen
# ---------------------------------------------------------------------------

def listen_holen(php_dir):
    hilfs = ZIEL / "_listen.php"
    hilfs.write_text(
        "<?php require_once __DIR__ . '/sk_lib.php';\n"
        "echo 'LESEND=' . implode(',', sk_lesende()) . \"\\n\";\n"
        "echo 'SCHALTEND=' . implode(',', array_keys(sk_befehle())) . \"\\n\";\n",
        encoding="utf-8", newline="\n")
    r = subprocess.run(
        [str(Path(php_dir) / "php.exe"), "-n", "-d", "display_errors=0",
         "-d", "date.timezone=Europe/Berlin", str(hilfs)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ZIEL), env={**os.environ, "LBHOMEDIR": str(BANK),
                            "LBPPLUGINDIR": ORDNER}, timeout=60)
    hilfs.unlink()
    lesend = schaltend = []
    for zeile in r.stdout.splitlines():
        if zeile.startswith("LESEND="):
            lesend = [x for x in zeile[7:].split(",") if x]
        elif zeile.startswith("SCHALTEND="):
            schaltend = [x for x in zeile[10:].split(",") if x]
    return lesend, schaltend


# ---------------------------------------------------------------------------
# Ein Durchlauf gegen EINE PHP-Fassung
# ---------------------------------------------------------------------------

def durchlauf(fassung, php_dir):
    print("=== PHP " + fassung)
    bank_leeren()

    lesend, schaltend = listen_holen(php_dir)
    if not lesend:
        nichts_gemessen("Aktionslisten", "sk_lesende() lieferte nichts")
        return
    if not schaltend:
        nichts_gemessen("Aktionslisten", "sk_befehle() lieferte nichts")
        return
    pruefe("Listen: sk_lesende() gelesen", len(lesend) >= 3, True)
    pruefe("Listen: sk_befehle() gelesen", len(schaltend) >= 3, True)
    # Aktionen, die ein Fahrzeug tragen: alles Lesende ausser den beiden
    # kontolosen, und alles Schaltende ausser abruf.
    mit_fahrzeug = [a for a in lesend if a not in ("fahrzeuge", "roh")]
    mit_fahrzeug += [a for a in schaltend if a != "abruf"]
    if not mit_fahrzeug:
        nichts_gemessen("Fahrzeugliste", "keine Aktion traegt ein Fahrzeug")
        return

    # ---------------- Fall 1: kein Token gesetzt ----------------
    konfig(aktionstoken="")
    abbild()
    a = ruf(php_dir, "F1 ohne Token", "aktion=status&fahrzeug=1")
    antwort_pruefen("F1 kein Token gesetzt", a, 403, "KEIN_TOKEN_GESETZT")
    enthaelt("F1 Marker FEHLER", a.zeile1, "FEHLER;OK=0;")

    # ---------------- Fall 2: Token gesetzt, aber unzulaessig ----------------
    # sk_regeln() weist 'abc+def' ab, sk_config_lage() setzt die Vorgabe (leer)
    # ein - und der Endpunkt meldet daraufhin, es sei NIE eines gesetzt worden.
    # Das ist die falsche Auskunft: das Token steht in der Datei.
    konfig(aktionstoken="abc+def")
    a = ruf(php_dir, "F2 unzulaessiges Token", "token=abc%2Bdef&aktion=status&fahrzeug=1")
    antwort_pruefen("F2 unzulaessiges Token", a, 403, "TOKEN_UNZULAESSIG")

    # ---------------- Fall 3: falsches Token ----------------
    konfig()
    a = ruf(php_dir, "F3 falsches Token", "token=falsch&aktion=status&fahrzeug=1")
    antwort_pruefen("F3 falsches Token", a, 403, "TOKEN")
    a = ruf(php_dir, "F3 Token als Feld", "token[]=x&aktion=status&fahrzeug=1")
    antwort_pruefen("F3 token[]=x", a, 403, "TOKEN")
    a = ruf(php_dir, "F3 Token 6000 Zeichen",
            "token=" + "a" * 6000 + "&aktion=status&fahrzeug=1")
    antwort_pruefen("F3 Token 6000 Zeichen", a, 403, "TOKEN")
    # Token in der Konfiguration als JSON-ZAHL, nicht als Zeichenkette.
    (CONFIG / "skoda.json").write_text(
        '{"aktionstoken": 12345678, "steuerung_ein": 0, "wartezeit": 0}',
        encoding="utf-8", newline="\n")
    a = ruf(php_dir, "F3 Token als JSON-Zahl", "token=falsch&aktion=status&fahrzeug=1")
    antwort_pruefen("F3 Token als JSON-Zahl abgewiesen", a, 403, "TOKEN")
    konfig()

    # ---------------- Fall 4: falsches Token schreibt keine Konfiguration ----
    # sk_config_lage() heilt eine leere Konfiguration aus der Zweitschrift -
    # und index.php ruft sk_config() VOR der Tokenpruefung. Ein Unbefugter
    # loest damit einen Schreibvorgang aus, ohne ein Token zu kennen.
    (CONFIG / "skoda.json").write_bytes(b"")
    SICHERUNG.write_text(
        '{"aktionstoken": "ausderzweitschrift", "steuerung_ein": 1}',
        encoding="utf-8", newline="\n")
    vorher = (CONFIG / "skoda.json").stat().st_size
    a = ruf(php_dir, "F4 falsches Token bei leerer Konfiguration",
            "token=falsch&aktion=status&fahrzeug=1")
    nachher = (CONFIG / "skoda.json").stat().st_size
    pruefe("F4 Konfiguration vorher 0 Byte", vorher, 0)
    pruefe("F4 Konfiguration bleibt 0 Byte", nachher, 0)
    pruefe("F4 Statuscode", a.code, 403)
    SICHERUNG.unlink()
    konfig()
    abbild()

    # ---------------- Fall 5: Feldform statt Zeichenkette ----------------
    a = ruf(php_dir, "F5 aktion[]=status", "token=%s&aktion[]=status&fahrzeug=1" % TOKEN)
    antwort_pruefen("F5 aktion[]=status", a, 400, "PARAMETER")
    a = ruf(php_dir, "F5 fahrzeug[]=1", "token=%s&aktion=status&fahrzeug[]=1" % TOKEN)
    antwort_pruefen("F5 fahrzeug[]=1", a, 400, "PARAMETER")

    # ---------------- Fall 6: unbrauchbare Werte ----------------
    faelle = [
        ("aktion=UNBEKANNT", "aktion=UNBEKANNT", "UNBEKANNTE_AKTION"),
        ("aktion=STATUS gross", "aktion=STATUS", "UNBEKANNTE_AKTION"),
        ("aktion=status%00", "aktion=status%00", "UNBEKANNTE_AKTION"),
        ("fahrzeug=Pfad", "aktion=status&fahrzeug=..%2F..%2F..%2Fetc%2Fpasswd", "PARAMETER"),
        ("aktion 6000 Zeichen", "aktion=" + "a" * 6000, "UNBEKANNTE_AKTION"),
        ("fahrzeug 6000 Zeichen", "aktion=status&fahrzeug=" + "1" * 6000, "PARAMETER"),
    ]
    for name, teil, grund in faelle:
        a = ruf(php_dir, "F6 " + name, "token=%s&%s" % (TOKEN, teil))
        antwort_pruefen("F6 " + name, a, 400, grund)

    # ---------------- Fall 7: fuehrende Null und unbekanntes Fahrzeug -------
    a = ruf(php_dir, "F7 fahrzeug=01", "token=%s&aktion=status&fahrzeug=01" % TOKEN)
    pruefe("F7 fahrzeug=01 liest Fahrzeug 1: Statuscode", a.code, 200)
    enthaelt("F7 fahrzeug=01 liefert Werte", a.zeile1, "SKODA;OK=1;")
    pruefe("F7 fahrzeug=01: keine PHP-Meldung", a.befunde, [])

    ladungen_schreiben()
    # steuerung_ein=1, damit die Steuerungssperre den Blick auf die
    # Fahrzeugpruefung nicht verstellt. temp und prozent stehen immer dabei -
    # sonst antworten klima_start und ladegrenze mit ihrem eigenen Grund.
    konfig(steuerung_ein=1)
    for aktion in mit_fahrzeug:
        vorher = warteschlange()
        a = ruf(php_dir, "F7 %s&fahrzeug=99" % aktion,
                "token=%s&aktion=%s&fahrzeug=99&temp=21&prozent=80" % (TOKEN, aktion))
        antwort_pruefen("F7 %s fahrzeug=99" % aktion, a, 404, "FAHRZEUG_UNBEKANNT")
        pruefe("F7 %s fahrzeug=99: nichts eingereiht" % aktion,
               warteschlange(), vorher)
    konfig()

    # ---------------- Fall 8: ladungen je Fahrzeug ----------------
    a = ruf(php_dir, "F8 ladungen mit VIN",
            "token=%s&aktion=ladungen&fahrzeug=%s" % (TOKEN, VIN2))
    pruefe("F8 ladungen mit VIN: Statuscode", a.code, 200)
    pruefe("F8 ladungen mit VIN: N=1", feld(a.zeile1, "N"), "1")
    zeilen = [z for z in a.text.split("\n")[1:] if z.strip()]
    if not zeilen:
        nichts_gemessen("F8 ladungen mit VIN", "keine Ladungszeile in der Antwort")
    else:
        pruefe("F8 ladungen mit VIN: nur Fahrzeug 2", [z.split(";")[1] for z in zeilen],
               ["2"])
    a = ruf(php_dir, "F8 ladungen Nummer 2",
            "token=%s&aktion=ladungen&fahrzeug=2" % TOKEN)
    pruefe("F8 ladungen Nummer 2: N=1", feld(a.zeile1, "N"), "1")

    # ---------------- Fall 9: Steuerung aus ----------------
    konfig(steuerung_ein=0)
    for aktion in schaltend:
        vorher = warteschlange()
        a = ruf(php_dir, "F9 %s bei gesperrter Steuerung" % aktion,
                "token=%s&aktion=%s&fahrzeug=1&temp=21&prozent=80" % (TOKEN, aktion))
        antwort_pruefen("F9 %s gesperrt" % aktion, a, 403, "STEUERUNG_AUS")
        pruefe("F9 %s gesperrt: nichts eingereiht" % aktion, warteschlange(), vorher)

    # ---------------- Fall 14: Dienst laeuft nicht ----------------
    konfig(steuerung_ein=1)
    for aktion in ("wecken", "abruf"):
        if aktion not in schaltend:
            nichts_gemessen("F14 " + aktion, "Aktion steht nicht in sk_befehle()")
            continue
        vorher = warteschlange()
        a = ruf(php_dir, "F14 %s ohne Dienst" % aktion,
                "token=%s&aktion=%s&fahrzeug=1" % (TOKEN, aktion))
        antwort_pruefen("F14 %s ohne Dienst" % aktion, a, 503, "DIENST_LAEUFT_NICHT")
        pruefe("F14 %s: nichts eingereiht" % aktion, warteschlange(), vorher)
    konfig()

    # ---------------- Fall 10: Zeitstempel in der Zukunft ----------------
    abbild(alter=-3600)
    a = ruf(php_dir, "F10 Abbild aus der Zukunft",
            "token=%s&aktion=status&fahrzeug=1" % TOKEN)
    pruefe("F10 Zukunft: ALTER=999999", feld(a.zeile1, "ALTER"), "999999")
    pruefe("F10 Zukunft: OK=0", feld(a.zeile1, "OK"), "0")
    pruefe("F10 Zukunft: keine PHP-Meldung", a.befunde, [])
    abbild()

    # ---------------- Fall 11: Modellname mit Semikolon und Zeilenumbruch ----
    abbild(modell2="Enyaq;iV 80\nFAHRZEUGE;OK=1;N=9")
    a = ruf(php_dir, "F11 Modellname mit Trennzeichen", "token=%s&aktion=fahrzeuge" % TOKEN)
    pruefe("F11 fahrzeuge: Statuscode", a.code, 200)
    pruefe("F11 fahrzeuge: N=2", feld(a.zeile1, "N"), "2")
    zeilen = [z for z in a.text.split("\n")[1:] if z.strip()]
    if not zeilen:
        nichts_gemessen("F11 fahrzeuge", "keine Fahrzeugzeile in der Antwort")
    else:
        pruefe("F11 fahrzeuge: genau 2 Zeilen", len(zeilen), 2)
        pruefe("F11 fahrzeuge: je 5 Felder",
               sorted(set(z.count(";") + 1 for z in zeilen)), [5])
    abbild()

    # ---------------- Fall 12: Ziffern mit angehaengtem Leerzeichen ---------
    # is_numeric("55 ") ist in PHP 8.0 wahr geworden und war in 7.4 falsch.
    # Derselbe Zwischenspeicher darf nicht zwei verschiedene Antworten geben.
    (DATA / "loxone.json").write_text(json.dumps({
        "ok": 1, "ts": int(time.time()) - 30, "zaehler": 7, "empfehlung": 1,
        "fahrzeuge": {"1": fahrzeug(1, VIN1, "Octavia iV", soc="55 ")},
    }, ensure_ascii=False), encoding="utf-8", newline="\n")
    a = ruf(php_dir, "F12 soc mit Leerzeichen",
            "token=%s&aktion=status&fahrzeug=1" % TOKEN)
    QUER.setdefault("F12 SOC", {})[fassung] = feld(a.zeile1, "SOC")
    pruefe("F12 soc mit Leerzeichen: keine PHP-Meldung", a.befunde, [])
    abbild()

    # ---------------- Fall 13: adresse ist kein Text ----------------
    for art, wert in (("Feld", ["Musterweg 7", "Musterstadt"]),
                      ("Objekt", {"strasse": "Musterweg 7", "ort": "Musterstadt"})):
        (DATA / "loxone.json").write_text(json.dumps({
            "ok": 1, "ts": int(time.time()) - 30, "zaehler": 7, "empfehlung": 1,
            "fahrzeuge": {"1": fahrzeug(1, VIN1, "Octavia iV", adresse=wert)},
        }, ensure_ascii=False), encoding="utf-8", newline="\n")
        a = ruf(php_dir, "F13 adresse als " + art,
                "token=%s&aktion=position&fahrzeug=1" % TOKEN)
        pruefe("F13 adresse als %s: Statuscode 200" % art, a.code, 200)
        pruefe("F13 adresse als %s: keine PHP-Meldung" % art, a.befunde, [])
        # Zweiter Anlauf MIT eingeschalteter Anzeige: so sieht der Rumpf aus,
        # wenn display_errors auf dem Zielsystem an ist. Dann darf erst recht
        # kein Dateipfad hinausgehen.
        b = ruf(php_dir, "F13 adresse als %s (Anzeige an)" % art,
                "token=%s&aktion=position&fahrzeug=1" % TOKEN, zeige_fehler=True)
        fehlt_nicht("F13 %s: kein Dateipfad im Rumpf" % art, b.text, ".php")
        fehlt_nicht("F13 %s: kein Bankpfad im Rumpf" % art, b.text, str(BANK))
        pruefe("F13 %s: Statuscode auch mit Anzeige 200" % art, b.code, 200)
    abbild()

    # ---------------- Fall 15: loxone.json fehlt oder ist kaputt ------------
    for art in ("fehlt", "kaputt"):
        datei = DATA / "loxone.json"
        if art == "fehlt":
            if datei.is_file():
                datei.unlink()
        else:
            datei.write_text("{das ist kein JSON", encoding="utf-8", newline="\n")
        for aktion in ("status", "fahrzeuge"):
            a = ruf(php_dir, "F15 %s bei loxone.json %s" % (aktion, art),
                    "token=%s&aktion=%s&fahrzeug=1" % (TOKEN, aktion))
            pruefe("F15 %s/%s: OK=0" % (aktion, art), feld(a.zeile1, "OK"), "0")
            pruefe("F15 %s/%s: keine PHP-Meldung" % (aktion, art), a.befunde, [])
            fehlt_nicht("F15 %s/%s: kein HTML" % (aktion, art), a.text, "<")
            pruefe("F15 %s/%s: Content-Type" % (aktion, art), a.ctype,
                   "text/plain; charset=utf-8")
    abbild()

    # ---------------- Fall 16: roh ist JSON ----------------
    a = ruf(php_dir, "F16 aktion=roh", "token=%s&aktion=roh" % TOKEN)
    pruefe("F16 roh: Content-Type", a.ctype, "application/json; charset=utf-8")
    pruefe("F16 roh: Statuscode", a.code, 200)
    try:
        json.loads(a.text)
        pruefe("F16 roh: Rumpf ist JSON", True, True)
    except ValueError as e:
        pruefe("F16 roh: Rumpf ist JSON", str(e), "")

    # Der Regelfall zum Schluss, damit die Schlussdurchsicht auch eine
    # vollstaendige Antwort jeder lesenden Aktion gesehen hat.
    for aktion in lesend:
        a = ruf(php_dir, "Regelfall " + aktion,
                "token=%s&aktion=%s&fahrzeug=1" % (TOKEN, aktion))
        pruefe("Regelfall %s: Statuscode 200" % aktion, a.code, 200)
        pruefe("Regelfall %s: keine PHP-Meldung" % aktion, a.befunde, [])


# ---------------------------------------------------------------------------
# Lauf
# ---------------------------------------------------------------------------
try:
    gelaufen = []
    for fassung, php_dir in PHPS:
        if not (Path(php_dir) / "php-cgi.exe").is_file():
            print("[INFO] PHP %s (php-cgi.exe) nicht vorhanden." % fassung)
            continue
        gelaufen.append(fassung)
        durchlauf(fassung, php_dir)

    print("=== Beide Fassungen im Vergleich")
    if len(gelaufen) < 2:
        nichts_gemessen("F12 Vergleich 7.4/8.4",
                        "nur %d PHP-Fassung(en) vorhanden" % len(gelaufen))
    else:
        for name, werte in sorted(QUER.items()):
            if len(werte) < 2:
                nichts_gemessen(name, "nicht in beiden Fassungen gemessen")
                continue
            pruefe("%s: 7.4 und 8.4 gleich" % name,
                   werte.get("7.4"), werte.get("8.4"))

    # ---------------- Schlussdurchsicht ueber JEDE Antwort ----------------
    print("=== Schlussdurchsicht ueber alle Antworten")
    klartext = [a for a in ANTWORTEN if not a.roh and not a.angezeigt]
    if not klartext:
        nichts_gemessen("F16 Schlussdurchsicht", "keine Antwort aufgezeichnet")
    else:
        pruefe("F16 Anzahl durchgesehener Antworten", len(klartext) > 40, True)
        falsch = sorted(set((a.ctype or "<leer>") for a in klartext
                            if a.ctype != "text/plain; charset=utf-8"))
        pruefe("F16 Content-Type aller Klartextantworten", falsch, [])
        crlf = sorted(set(a.name for a in klartext if b"\r\n" in a.rumpf))
        pruefe("F16 Zeilenenden sind LF", crlf, [])
        ohne_marker = sorted(set(a.name for a in klartext
                                 if not re.match(r"^[A-Z]+;", a.zeile1)))
        pruefe("F16 erste Zeile beginnt mit einem Marker", ohne_marker, [])
        ohne_ok = sorted(set(a.name for a in klartext if "OK=" not in a.zeile1))
        pruefe("F16 erste Zeile nennt OK=", ohne_ok, [])
        stderr_rest = sorted(set(a.name for a in ANTWORTEN if a.rest))
        pruefe("F16 nichts Unerwartetes auf stderr", stderr_rest, [])
finally:
    shutil.rmtree(BANK, ignore_errors=True)

print()
print("%d Pruefungen, %d Beanstandung(en)" % (PRUEFUNGEN, BEANSTANDUNGEN))
sys.exit(1 if BEANSTANDUNGEN else 0)
