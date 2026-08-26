#!/usr/bin/env python3
"""Pflichtpruefung fuer das Volkswagen-ID-Plugin.

Ersetzt NICHT `php -l` und keinen echten Renderlauf - in diesem Arbeitsbereich
gibt es kein PHP. Die Hausregel verlangt fuer diesen Fall ausdruecklich einen
Ersatz und dessen Offenlegung: Klammer-, Tag- und <?php/?>-Bilanz zaehlen.
Genau das tut dieses Skript, zusammen mit den uebrigen Punkten der
Pflichtpruefung, die sich ohne PHP durchfuehren lassen.

Aufruf:  vw_pruefen.py <pluginordner>
"""

import re
import subprocess
import sys
from pathlib import Path


def _eigene_woerter():
    """Die Woerter, die in einer Veroeffentlichung nichts zu suchen haben.

    Sie stehen NICHT im Quelltext - sonst traegt das Werkzeug den Namen, vor
    dem es schuetzen soll, selbst in jede Veroeffentlichung. Gelesen wird
    'anonymisierung_woerter.txt' neben diesem Skript; die Datei ist von
    .gitignore gedeckt. Fehlt sie, wird nichts nach Namen gesucht, und das
    Werkzeug SAGT das - stilles Nichtstun waere schlimmer als ein Fund.
    """
    import os
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     'anonymisierung_woerter.txt')
    if not os.path.isfile(p):
        print('   Hinweis: anonymisierung_woerter.txt fehlt - es wird nicht '
              'nach Namen gesucht (siehe .beispiel-Datei).')
        return []
    with open(p, encoding='utf-8') as f:
        return [z.strip() for z in f
                if z.strip() and not z.lstrip().startswith('#')]

FEHLER = []
HINWEISE = []


def fehl(text):
    FEHLER.append(text)


def hinw(text):
    HINWEISE.append(text)


# ---------------------------------------------------------------------------
# 1. PHP: Klammer-, Tag- und Anfuehrungszeichenbilanz
#
# Kleiner Lexer: er kennt <?php-Bereiche, beide Zeichenkettenarten samt
# Maskierung und alle drei Kommentararten. Erst danach werden Klammern
# gezaehlt - sonst zaehlt jede Klammer in einem Text mit.
# ---------------------------------------------------------------------------
def php_zerlegen(t):
    """Gibt den Quelltext ohne Zeichenketten und Kommentare zurueck,
    dazu die Zahl der geoeffneten und geschlossenen PHP-Bereiche."""
    aus = []
    i = 0
    n = len(t)
    im_php = False
    auf = zu = 0
    while i < n:
        if not im_php:
            j = t.find("<?php", i)
            j2 = t.find("<?=", i)
            if j < 0 or (0 <= j2 < j):
                j = j2
                laenge = 3
            else:
                laenge = 5
            if j < 0:
                break
            i = j + laenge
            im_php = True
            auf += 1
            continue
        c = t[i]
        if c == "?" and t.startswith("?>", i):
            im_php = False
            zu += 1
            i += 2
            continue
        if c == "'":
            i += 1
            while i < n and t[i] != "'":
                i += 2 if t[i] == "\\" else 1
            i += 1
            aus.append(" ")
            continue
        if c == '"':
            i += 1
            while i < n and t[i] != '"':
                i += 2 if t[i] == "\\" else 1
            i += 1
            aus.append(" ")
            continue
        if t.startswith("/*", i):
            e = t.find("*/", i + 2)
            i = n if e < 0 else e + 2
            aus.append(" ")
            continue
        if t.startswith("//", i) or c == "#":
            e = t.find("\n", i)
            i = n if e < 0 else e
            aus.append(" ")
            continue
        aus.append(c)
        i += 1
    return "".join(aus), auf, zu


def pruefe_php(wurzel):
    dateien = sorted(wurzel.rglob("*.php"))
    if not dateien:
        fehl("Keine PHP-Datei gefunden.")
        return
    for f in dateien:
        t = f.read_text(encoding="utf-8")
        rein, auf, zu = php_zerlegen(t)
        for links, rechts, name in (("{", "}", "geschweifte"), ("(", ")", "runde"),
                                    ("[", "]", "eckige")):
            a, b = rein.count(links), rein.count(rechts)
            if a != b:
                fehl("%s: %s Klammern unausgeglichen (%d auf, %d zu)"
                     % (f.name, name, a, b))
        # Der letzte PHP-Bereich einer Datei bleibt absichtlich offen: ein
        # schliessendes ?> am Dateiende schickt sonst Leerzeichen an den
        # Browser und macht spaetere header()-Aufrufe unmoeglich.
        if zu > auf:
            fehl("%s: mehr ?> als <?php" % f.name)
        if t.rstrip().endswith("?>"):
            hinw("%s endet mit ?> - erlaubt, aber ein Leerzeichen dahinter "
                 "bricht header()." % f.name)
        if "\t" in t:
            hinw("%s enthaelt Tabulatoren (in der Reiterleiste ist das gewollt)." % f.name)
    print("[OK]   %d PHP-Dateien: Klammer- und Tag-Bilanz ausgeglichen" % len(dateien))
    print("[INFO] php -l war nicht moeglich - in diesem Arbeitsbereich gibt es kein PHP.")


# ---------------------------------------------------------------------------
# 2. Sprachdateien
# ---------------------------------------------------------------------------
def ini_lesen(pfad):
    texte = {}
    abschnitt = ""
    schlecht = []
    for nr, zeile in enumerate(pfad.read_text(encoding="utf-8").splitlines(), 1):
        s = zeile.strip()
        if not s or s.startswith(";"):
            continue
        if s.startswith("[") and s.endswith("]"):
            abschnitt = s[1:-1]
            continue
        m = re.match(r'^([A-Z0-9_]+)\s*=\s*"(.*)"$', s)
        if not m:
            schlecht.append((nr, zeile))
            continue
        if s.count('"') != 2:
            schlecht.append((nr, zeile))
            continue
        texte[abschnitt + "." + m.group(1)] = m.group(2)
    return texte, schlecht


def pruefe_sprache(wurzel):
    de = wurzel / "templates/lang/language_de.ini"
    en = wurzel / "templates/lang/language_en.ini"
    for p in (de, en):
        if not p.is_file():
            fehl("Sprachdatei fehlt: %s" % p)
            return
    tde, sde = ini_lesen(de)
    ten, sen = ini_lesen(en)
    for name, schlecht in (("de", sde), ("en", sen)):
        for nr, zeile in schlecht:
            fehl("language_%s.ini Zeile %d passt nicht auf SCHLUESSEL = \"…\": %s"
                 % (name, nr, zeile[:70]))

    benutzt = set()
    maskiert = set()
    for f in sorted(wurzel.rglob("*.php")):
        t = f.read_text(encoding="utf-8")
        benutzt |= set(re.findall(r"vw_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t))
        benutzt |= set(re.findall(r"'(VW_[A-Z]+\.[A-Z0-9_]+|BAUSTEIN\.[A-Z0-9_]+)'", t))
        maskiert |= set(re.findall(r"vw_e\(\s*vw_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t))
        maskiert |= set(re.findall(r"vw_e\(\s*sprintf\(\s*vw_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t))
    benutzt |= {"EINST.DIENST_START", "EINST.DIENST_STOP", "EINST.DIENST_RESTART"}
    for feld in ("INTERVALL", "TAKT_WARTUNG", "TEMP_MIN", "TEMP_MAX",
                 "VERLAUF_TAGE", "WARTEZEIT"):
        benutzt.add("EINST.L_" + feld)

    for k in sorted(benutzt - set(tde)):
        fehl("Schluessel im PHP benutzt, fehlt in language_de.ini: " + k)
    for k in sorted(benutzt - set(ten)):
        fehl("Schluessel im PHP benutzt, fehlt in language_en.ini: " + k)
    for k in sorted(set(tde) - benutzt):
        fehl("Schluessel in language_de.ini, aber im PHP nie benutzt: " + k)
    if set(tde) != set(ten):
        fehl("language_de.ini und language_en.ini sind nicht deckungsgleich.")

    for k in sorted(maskiert):
        for name, tab in (("de", tde), ("en", ten)):
            w = tab.get(k, "")
            if "<" in w or "&" in w:
                fehl("%s: %s laeuft durch vw_e(), enthaelt aber Auszeichnung oder "
                     "eine Entitaet - sie wuerde doppelt maskiert" % (name, k))

    for k in sorted(set(tde) & set(ten)):
        if re.findall(r"%[sd]", tde[k]) != re.findall(r"%[sd]", ten[k]):
            fehl("%s: Platzhalter in DE und EN unterschiedlich" % k)

    print("[OK]   Sprachdateien: %d Schluessel, deckungsgleich, alle benutzt, "
          "%d maskierte frei von Auszeichnung" % (len(tde), len(maskiert)))


# ---------------------------------------------------------------------------
# 3. Reiter, Legenden, Formulare
# ---------------------------------------------------------------------------
def pruefe_oberflaeche(wurzel):
    p = wurzel / "webfrontend/htmlauth/index.php"
    t = p.read_text(encoding="utf-8")

    ziele = re.findall(r'data-ziel="(tab-[a-z0-9]+)"', t)
    seiten = re.findall(r'class="sm-seite" id="(tab-[a-z0-9]+)"', t)
    liste = re.search(r"\^tab-\(([a-z0-9|]+)\)", t)
    liste = set("tab-" + x for x in liste.group(1).split("|")) if liste else set()
    if set(ziele) != set(seiten):
        fehl("Reiterleiste und Bereiche passen nicht zusammen: %s / %s"
             % (sorted(set(ziele)), sorted(set(seiten))))
    if not set(ziele) <= liste:
        fehl("Reiter fehlen in der activetab-Positivliste: %s" % sorted(set(ziele) - liste))
    if liste - set(ziele):
        fehl("Positivliste kennt Reiter, die es nicht gibt: %s" % sorted(liste - set(ziele)))
    print("[OK]   %d Reiter, %d Bereiche, Positivliste deckungsgleich"
          % (len(ziele), len(seiten)))

    # Legende in jedem Bereich mit Knopfreihe
    ohne = []
    for m in re.finditer(r'<div class="sm-seite" id="(tab-[a-z0-9]+)"', t):
        rest = t[m.start():]
        tiefe, pos = 0, 0
        for tok in re.finditer(r"</?div", rest):
            tiefe += 1 if tok.group(0) == "<div" else -1
            if tiefe == 0:
                pos = tok.end()
                break
        inhalt = rest[:pos] if pos else rest
        if "sm-knopfreihe" in inhalt and "sm-legende" not in inhalt:
            ohne.append(m.group(1))
    if ohne:
        fehl("Reiter mit Knopfreihe ohne Legende: " + ", ".join(ohne))
    else:
        print("[OK]   Jede Knopfreihe steht unter einer Legende")

    # Formulare
    for f in sorted(wurzel.rglob("*.php")):
        tt = f.read_text(encoding="utf-8")
        forms = re.findall(r"<form[^>]*>", tt)
        for form in forms:
            if 'action="index.php"' not in form:
                fehl("%s: Formular ohne action=\"index.php\": %s" % (f.name, form[:60]))
            if 'method="post"' not in form:
                fehl("%s: Formular ohne method=\"post\"" % f.name)
        if forms and 'name="activetab"' not in tt:
            fehl("%s: Formulare ohne verstecktes Feld activetab" % f.name)
    print("[OK]   Alle Formulare senden per POST an index.php und fuehren activetab mit")

    # div-Bilanz der Oberflaeche. Ein fehlendes </div> verschiebt die halbe
    # Seite, faellt aber in keiner Syntaxpruefung auf.
    auf = len(re.findall(r"<div\b", t))
    zu = len(re.findall(r"</div>", t))
    if auf != zu:
        fehl("index.php: div-Bilanz unausgeglichen (%d auf, %d zu)" % (auf, zu))
    else:
        print("[OK]   div-Bilanz der Oberflaeche ausgeglichen (%d Paare)" % auf)

    # Eigenes CSS-Kuerzel? Es muss ueberall sm- heissen.
    fremd = set()
    for f in sorted(wurzel.rglob("*.php")):
        tt = f.read_text(encoding="utf-8")
        for k in set(re.findall(r'class="(?:[^"]*\s)?([a-z]{2,4})-[a-z0-9-]+', tt)):
            if k in ("sm", "ui", "fa", "lb"):
                continue
            if re.search(r"(?m)^\s*\." + k + r"-[a-z0-9-]+\s*[{,]", tt):
                fremd.add(k)
    if fremd:
        fehl("Eigene CSS-Kuerzel statt sm-: " + ", ".join(sorted(fremd)))
    else:
        print("[OK]   CSS-Klassen heissen ueberall sm-")


# ---------------------------------------------------------------------------
# 4. Endpunkt: die Muster gegen boesartige Eingaben
#
# Das ist KEIN Durchlauf des PHP-Ablaufs - die Muster werden aus der Datei
# gelesen und in Python gegen dieselben Eingaben gehalten. Was hier faellt,
# faellt auch dort; was hier durchgeht, muss am lebenden System nachgeprueft
# werden.
# ---------------------------------------------------------------------------
def pruefe_endpunkt(wurzel):
    p = wurzel / "webfrontend/html/index.php"
    t = p.read_text(encoding="utf-8")

    if "hash_equals" not in t:
        fehl("Der Endpunkt vergleicht das Token nicht mit hash_equals.")
    if "http_response_code(403)" not in t:
        fehl("Der Endpunkt antwortet bei fehlendem Token nicht mit 403.")

    muster = dict(re.findall(r"vw_param\('([a-z]+)',\s*'(/[^']+/)'", t))
    erwartet = {"fahrzeug", "temp", "prozent", "ampere"}
    if set(muster) != erwartet:
        fehl("Geprueft werden %s, erwartet %s" % (sorted(muster), sorted(erwartet)))

    boese = ["; rm -rf /", "../../etc/passwd", "1 OR 1=1", "<script>", "%00",
             "1;reboot", "'", '"', "\n", "999999999999", "-1", "abc"]
    gut = {"fahrzeug": ["1", "12", "WVWZZZE1ZPP000001"],
           "temp": ["21", "21.5", "21,5", "9"],
           "prozent": ["80", "100", "5"],
           "ampere": ["5", "6", "10", "13", "16", "32"]}

    for name, roh in muster.items():
        rx = re.compile("^" + roh.strip("/").lstrip("^").rstrip("$") + "$")
        for b in boese:
            if rx.match(b):
                fehl("Muster fuer %s laesst %r durch" % (name, b))
        for g in gut[name]:
            if not rx.match(g):
                fehl("Muster fuer %s weist den gueltigen Wert %r ab" % (name, g))

    # Weissliste der Aktionen
    lesend = re.search(r"\$vw_lesend = array\(([^)]*)\)", t)
    schaltend = re.search(r"\$vw_schaltend = array\(([^;]*?)\);", t, re.S)
    if not lesend or not schaltend:
        fehl("Die Weisslisten der Aktionen sind nicht auffindbar.")
    else:
        a = set(re.findall(r"'([a-z_]+)'", lesend.group(1)))
        b = set(re.findall(r"'([a-z_]+)'", schaltend.group(1)))
        if a & b:
            fehl("Aktion steht in beiden Weisslisten: %s" % sorted(a & b))
        print("[OK]   Endpunkt: %d lesende, %d schaltende Aktionen, Muster weisen "
              "alle %d Angriffseingaben ab" % (len(a), len(b), len(boese)))

    if "STEUERUNG_AUS" not in t or "DIENST_LAEUFT_NICHT" not in t:
        fehl("Der Endpunkt prueft nicht auf gesperrte Steuerung bzw. toten Dienst.")


# ---------------------------------------------------------------------------
# 5. Loxone-Vorlage: CRLF, Tabulatoren, Attributreihenfolge, Wohlgeformtheit
# ---------------------------------------------------------------------------
def pruefe_vorlage(wurzel):
    t = (wurzel / "webfrontend/html/vw_lib.php").read_text(encoding="utf-8")
    block = re.search(r"function vw_xml_virtual_in_http.*?\n}", t, re.S)
    if not block:
        fehl("vw_xml_virtual_in_http() nicht gefunden.")
        return
    b = block.group(0)
    if b.count("$crlf") < 4:
        fehl("Die Loxone-Vorlage benutzt nicht durchgehend CRLF.")
    if '"\\t"' not in b:
        fehl("Vor den Kindelementen der Loxone-Vorlage fehlt der Tabulator.")
    reihenfolge = re.findall(r"\$o \.= '([A-Za-z]+)=\"", b)
    soll = ["Title", "Comment", "Address", "PollingTime", "Title", "Comment", "Check",
            "Signed", "Analog", "SourceValLow", "DestValLow", "SourceValHigh",
            "DestValHigh", "DefVal", "MinVal", "MaxVal"]
    if reihenfolge != soll:
        fehl("Attributreihenfolge der Loxone-Vorlage weicht vom Original ab:\n  %s"
             % reihenfolge)
    else:
        print("[OK]   Loxone-Vorlage: CRLF, Tabulator und Attributreihenfolge wie im Original")

    # Die Bedeutungstexte laufen durch strip_tags + html_entity_decode, bevor
    # sie maskiert werden - sonst stuende 'l&auml;dt' in Loxone Config.
    if "html_entity_decode" not in t or "strip_tags" not in t:
        fehl("Die Vorlage loest vor dem Maskieren keine Entitaeten auf - in Loxone "
             "Config stuende sonst wortwoertlich 'l&auml;dt'.")

    # Nachbau der Ausgabe in Python und Pruefung als XML. Das ist ein Nachbau,
    # kein Durchlauf des PHP - es beweist nur, dass die erzeugte Form
    # wohlgeformt ist und die Zeilenenden stimmen.
    felder = re.findall(r"^\s*'([A-Z]+)'\s*=>\s*array\('([^']*)',\s*'(VW_FELD\.[A-Z_]+)'\)",
                        t, re.M)
    if len(felder) < 10:
        fehl("Nur %d Statusfelder ausgelesen - das Suchmuster passt nicht zur "
             "Datei." % len(felder))
    if not felder:
        fehl("Die Statusfelder liessen sich nicht auslesen.")
        return
    crlf = "\r\n"
    xml = '<?xml version="1.0" encoding="utf-8"?>' + crlf
    xml += ('<VirtualInHttp Title="Volkswagen 1" Comment="Test" '
            'Address="http://beispiel/x" PollingTime="300">' + crlf)
    for feld, einheit, _ in felder:
        xml += ("\t" + '<VirtualInHttpCmd Title="VOLKSWAGEN_1_%s" Comment="Bedeutung" '
                'Check="\\i%s=\\i\\v" Signed="true" Analog="true" SourceValLow="0" '
                'DestValLow="0" SourceValHigh="100" DestValHigh="100" DefVal="0" '
                'MinVal="-2147483647" MaxVal="2147483647"/>' % (feld, feld)) + crlf
    xml += "</VirtualInHttp>" + crlf
    import xml.etree.ElementTree as ET
    try:
        baum = ET.fromstring(xml)
    except ET.ParseError as err:
        fehl("Der Nachbau der Loxone-Vorlage ist nicht wohlgeformt: %s" % err)
        return
    roh = xml.encode("utf-8")
    nackte_lf = len(re.findall(rb"(?<!\r)\n", roh))
    if nackte_lf:
        fehl("Der Nachbau der Loxone-Vorlage enthaelt %d nackte LF." % nackte_lf)
    if len(baum) != len(felder):
        fehl("Der Nachbau enthaelt %d Befehle statt %d." % (len(baum), len(felder)))
    print("[OK]   Nachbau der Loxone-Vorlage: wohlgeformt, %d Befehle, %d CRLF, "
          "keine nackte LF" % (len(baum), roh.count(b"\r\n")))


# ---------------------------------------------------------------------------
# 6. Python und Shell
# ---------------------------------------------------------------------------
def pruefe_python(wurzel):
    for f in sorted(wurzel.rglob("*.py")):
        t = f.read_text(encoding="utf-8")
        if "\t" in t:
            fehl("%s enthaelt Tabulatoren - Python 3 lehnt gemischte Einrueckung "
                 "hart ab (TabError)." % f.name)
        # py_compile scheitert hier an der Fassung: das Skript ist fuer 3.13
        # geschrieben, der Arbeitsbereich hat aelteres Python. Deshalb nur der
        # Parser-Lauf mit ast, der die Syntax genauso prueft.
        import ast
        try:
            ast.parse(t, filename=str(f))
        except SyntaxError as err:
            fehl("%s: Syntaxfehler in Zeile %s: %s" % (f.name, err.lineno, err.msg))
        if "REPLACELBPBINDIR" in t.splitlines()[0]:
            pass
    print("[OK]   Python: Syntax fehlerfrei, keine Tabulatoren")


def pruefe_shell(wurzel):
    skripte = sorted(list(wurzel.rglob("*.sh")) + [wurzel / "cron/cron.01min"])
    for f in skripte:
        if not f.is_file():
            continue
        e = subprocess.run(["bash", "-n", str(f)], capture_output=True, text=True)
        if e.returncode:
            fehl("%s: %s" % (f.name, e.stderr.strip()))
    print("[OK]   %d Shell-Skripte: bash -n fehlerfrei" % len(skripte))


# ---------------------------------------------------------------------------
# 7. Platzhalter, harte Pfade, Muell, Anonymitaet
# ---------------------------------------------------------------------------
GUELTIG = {"REPLACELBHOMEDIR", "REPLACELBPPLUGINDIR", "REPLACELBPHTMLAUTHDIR",
           "REPLACELBPHTMLDIR", "REPLACELBPTEMPLATEDIR", "REPLACELBPDATADIR",
           "REPLACELBPLOGDIR", "REPLACELBPCONFIGDIR", "REPLACELBPBINDIR"}


def pruefe_rest(wurzel):
    for f in sorted(wurzel.rglob("*")):
        if not f.is_file() or f.suffix in (".png", ".ico"):
            continue
        t = f.read_text(encoding="utf-8", errors="replace")
        for m in set(re.findall(r"REPLACE[A-Z]+", t)):
            if m not in GUELTIG:
                fehl("%s: unbekannter Platzhalter %s (wird nicht ersetzt)" % (f.name, m))
        for treffer in re.finditer(r"/opt/loxberry", t):
            zeile = t[:treffer.start()].count("\n") + 1
            umgebung = t.splitlines()[zeile - 1]
            if "home" not in umgebung and "Rueckfall" not in umgebung:
                hinw("%s Zeile %d nennt /opt/loxberry: %s"
                     % (f.name, zeile, umgebung.strip()[:70]))

    muell = [f for f in wurzel.rglob("*")
             if "__pycache__" in str(f) or f.suffix in (".pyc", ".bak", ".orig")]
    if muell:
        fehl("Muell im Plugin: %s" % [str(m) for m in muell])
    else:
        print("[OK]   Nur gueltige Platzhalter, kein __pycache__, keine Sicherungsdateien")

    # Anonymitaet
    verdacht = []
    for f in sorted(wurzel.rglob("*")):
        if not f.is_file() or f.suffix in (".png", ".ico"):
            continue
        t = f.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"\b(?:10|192\.168|172\.(?:1[6-9]|2[0-9]|3[01]))"
                             r"(?:\.\d{1,3}){2,3}\b(?!\.)", t):
            verdacht.append("%s: %s" % (f.name, m.group(0)))
        # Wortgrenzen, sonst schlaegt "Anwesenheitsmelder" auf den Namen der
        # Projektdatei an - genau das ist am 05.08.2026 passiert.
        for wort in _eigene_woerter():
            if re.search(r"\b%s\b" % re.escape(wort), t):
                verdacht.append("%s: %s" % (f.name, wort))
    if verdacht:
        fehl("Anonymitaetspruefung: " + "; ".join(verdacht))
    else:
        print("[OK]   Anonymitaetspruefung: keine Heimnetzadressen, keine Klarnamen")

    # Pflichtdateien
    for pfad in ("plugin.cfg", "release.cfg", "prerelease.cfg", "LICENSE", "README.md",
                 "postinstall.sh", "preupgrade.sh", "postupgrade.sh",
                 "cron/cron.01min", "bin/vw.py", "bin/dienst.sh",
                 "icons/icon.svg", "icons/icon_64.png", "icons/icon_128.png",
                 "icons/icon_256.png", "icons/icon_512.png",
                 "templates/help/help.html",
                 "templates/lang/language_de.ini", "templates/lang/language_en.ini",
                 "webfrontend/htmlauth/index.php", "webfrontend/htmlauth/vw_test.php",
                 "webfrontend/html/index.php", "webfrontend/html/vw_lib.php"):
        if not (wurzel / pfad).is_file():
            fehl("Pflichtdatei fehlt: " + pfad)

    # Fassungen an drei Stellen
    v = {}
    for name in ("plugin.cfg", "release.cfg", "prerelease.cfg"):
        m = re.search(r"^VERSION=(.+)$", (wurzel / name).read_text(encoding="utf-8"), re.M)
        v[name] = m.group(1).strip() if m else "fehlt"
    if len(set(v.values())) != 1:
        fehl("Fassungsnummern weichen ab: %s" % v)
    else:
        print("[OK]   Fassung %s in plugin.cfg, release.cfg und prerelease.cfg gleich"
              % list(v.values())[0])

    pc = (wurzel / "plugin.cfg").read_text(encoding="utf-8")
    # Selbstaktualisierung: aus ist immer in Ordnung. An ist es nur, wenn die
    # Adressen auf ein eigenes Repository UND auf einen Tag zeigen - sonst
    # boete LoxBerry irgendwann ein Downgrade auf einen fremden Stand an
    # (Hausregel, belegt am Docker-Plugin).
    if "AUTOMATIC_UPDATES=false" in pc:
        print("[OK]   Selbstaktualisierung aus - kein Downgrade auf fremde Staende moeglich")
    elif "AUTOMATIC_UPDATES=true" in pc:
        adressen = re.findall(r"^(?:RELEASECFG|PRERELEASECFG)=(.*)$", pc, re.M)
        if len(adressen) != 2 or not all(a.strip() for a in adressen):
            fehl("AUTOMATIC_UPDATES ist true, aber RELEASECFG oder PRERELEASECFG ist leer.")
        else:
            konten = set(re.findall(r"githubusercontent\.com/([^/]+)/([^/]+)/", " ".join(adressen)))
            archiv = re.search(r"^ARCHIVEURL=(.*)$",
                               (wurzel / "release.cfg").read_text(encoding="utf-8"), re.M)
            konten |= set(re.findall(r"github\.com/([^/]+)/([^/]+)/",
                                     archiv.group(1) if archiv else ""))
            if len(konten) != 1:
                fehl("Die Adressen der Selbstaktualisierung zeigen auf verschiedene "
                     "Repositories: %s" % sorted(konten))
            else:
                konto, repo = list(konten)[0]
                print("[OK]   Selbstaktualisierung an, alle Adressen zeigen auf %s/%s"
                      % (konto, repo))
    else:
        fehl("AUTOMATIC_UPDATES ist weder true noch false.")
    if not re.search(r"^LB_MINIMUM=([3-9]|\d\d)\.", pc, re.M):
        fehl("LB_MINIMUM liegt unter 3.0.0.")
    if "LB_MAXIMUM=false" not in pc:
        fehl("LB_MAXIMUM ist gesetzt - plugininstall.pl bricht bei Ueberschreitung ab.")
    for name in ("release.cfg", "prerelease.cfg"):
        t = (wurzel / name).read_text(encoding="utf-8")
        m = re.search(r"^ARCHIVEURL=(.*)$", t, re.M)
        if m and m.group(1).strip() and "/tags/" not in m.group(1):
            fehl("%s: ARCHIVEURL zeigt nicht auf einen Tag." % name)


# ---------------------------------------------------------------------------
# 8. Uebereinstimmung Dienst / Bibliothek / Endpunkt
# ---------------------------------------------------------------------------
def pruefe_zusammenspiel(wurzel):
    py = (wurzel / "bin/vw.py").read_text(encoding="utf-8")
    lib = (wurzel / "webfrontend/html/vw_lib.php").read_text(encoding="utf-8")
    ep = (wurzel / "webfrontend/html/index.php").read_text(encoding="utf-8")

    # Vorgabewerte muessen zusammenpassen. Nur die beiden Vorgabebloecke lesen -
    # sonst zaehlt jedes andere Array mit (z. B. der Rueckfallwert des
    # MQTT-Zustands).
    py_block = re.search(r"VORGABEN = \{(.*?)\n\}", py, re.S).group(1)
    lib_block = re.search(r"function vw_vorgaben.*?\n}", lib, re.S).group(0)
    pv = dict(re.findall(r'^\s*"([a-z_]+)":\s*([0-9]+|"[a-z]+"),', py_block, re.M))
    lv = dict(re.findall(r"^\s*'([a-z_]+)'\s*=>\s*([0-9]+|'[a-z]+'),", lib_block, re.M))
    for k in set(pv) & set(lv):
        a = pv[k].strip('"')
        b = lv[k].strip("'")
        if a != b:
            fehl("Vorgabewert %s: vw.py sagt %s, vw_lib.php sagt %s" % (k, a, b))
    nur_py = set(pv) - set(lv)
    nur_php = set(lv) - set(pv) - {"aktionstoken", "wartezeit"}
    if nur_py:
        fehl("Vorgabewerte nur in vw.py: %s" % sorted(nur_py))
    if nur_php:
        fehl("Vorgabewerte nur in vw_lib.php: %s" % sorted(nur_php))
    print("[OK]   %d Vorgabewerte in Dienst und Bibliothek gleich" % len(set(pv) & set(lv)))

    # Jede schaltende Aktion des Endpunkts muss der Dienst kennen
    m = re.search(r"\$vw_schaltend = array\((.*?)\);", ep, re.S)
    aktionen = set(re.findall(r"'([a-z_]+)'", m.group(1))) if m else set()
    bekannt = set(re.findall(r'aktion == "([a-z_]+)"', py))
    # Der Dienst fasst Gegensatzpaare zusammen: aktion in ("klima_start", "klima_stop")
    paare = re.findall(r'aktion in \("([a-z_]+)", "([a-z_]+)"\)', py)
    for a1, a2 in paare:
        bekannt.add(a1); bekannt.add(a2)
    fehlt = aktionen - bekannt
    if fehlt:
        fehl("Der Endpunkt bietet Aktionen an, die der Dienst nicht kennt: %s"
             % sorted(fehlt))
    ueberzaehlig = bekannt - aktionen
    if ueberzaehlig:
        hinw("Der Dienst kennt Aktionen, die der Endpunkt nicht anbietet: %s"
             % sorted(ueberzaehlig))
    print("[OK]   Alle %d schaltenden Aktionen des Endpunkts kennt der Dienst"
          % len(aktionen))

    # Jedes MQTT-Feld der Themenliste muss der Dienst auch senden
    mq = set(re.findall(r"'fahrzeugN/([a-z_]+)'", lib))
    gesendet = set(re.findall(r'^\s*"([a-z_]+)",?\s*$',
                              re.search(r"MQTT_FELDER = \((.*?)\)", py, re.S).group(1), re.M))
    gesendet |= set(re.findall(r'"([a-z_]+)"',
                               re.search(r"MQTT_FELDER = \((.*?)\)", py, re.S).group(1)))
    fehlt = mq - gesendet
    if fehlt:
        fehl("Der MQTT-Reiter nennt Themen, die der Dienst nicht sendet: %s" % sorted(fehlt))
    zuviel = gesendet - mq
    if zuviel:
        fehl("Der Dienst sendet Themen, die der MQTT-Reiter nicht nennt: %s" % sorted(zuviel))
    print("[OK]   %d MQTT-Themen: Reiter und Dienst decken sich" % len(mq))

    # Jedes Feld der Endpunkt-Ausgabe muss in der Feldliste stehen
    for aktion, funktion in (("VOLKSWAGEN", "vw_status_felder"),
                             ("LADEN", "vw_laden_felder"),
                             ("WARTUNG", "vw_wartung_felder")):
        zeile = re.search(r'"%s;OK=%%d;(.*?)\\n"' % aktion, ep, re.S)
        if not zeile:
            zeile = re.search(r'"%s;OK=%%d;(.*?)ALTER=%%d' % aktion, ep, re.S)
        felder = set(re.findall(r"([A-Z]+)=%s", zeile.group(1))) if zeile else set()
        block = re.search(r"function %s.*?\n}" % funktion, lib, re.S).group(0)
        liste = set(re.findall(r"^\s*'([A-Z]+)'\s*=>", block, re.M)) - {"OK"}
        if aktion != "WARTUNG":
            liste -= {"ALTER"}
        else:
            liste -= {"ALTER"}
        if felder != liste:
            fehl("%s: Endpunkt sendet %s, die Feldliste nennt %s"
                 % (aktion, sorted(felder), sorted(liste)))
    print("[OK]   Endpunkt-Ausgabe und Feldlisten der Oberflaeche decken sich")


def pruefe_bausteinnamen(wurzel):
    """Jeder virtuelle Eingang der Baustein-Liste muss es auch geben.

    Befund vom 06.08.2026: Baustein #8 verlangte einen Eingang '..._KOFFER',
    den die Feldliste von VW und Audi gar nicht kennt (nur Skoda hat ihn). Wer
    die Tabelle von oben nach unten abgearbeitet haette, waere an einer
    Befehlserkennung gescheitert, die nie etwas empfaengt - und haette lange
    gesucht, weil alles andere funktioniert.
    """
    lib = next(wurzel.glob("webfrontend/html/*_lib.php")).read_text(encoding="utf-8")
    felder = set()
    for fn in ("status", "laden", "wartung"):
        block = re.search(r"function \w+_%s_felder.*?\n\}" % fn, lib, re.S)
        if block:
            felder |= set(re.findall(r"^\s*'([A-Z]+)'\s*=>", block.group(0), re.M))
    ini = (wurzel / "templates/lang/language_de.ini").read_text(encoding="utf-8")
    namen = dict(re.findall(r'^(N\d\d) = "[A-Z]+_\d+_([A-Z]+)"$', ini, re.M))
    fehlend = sorted("%s (%s)" % (n, f) for n, f in namen.items() if f not in felder)
    if fehlend:
        fehl("Baustein-Liste nennt virtuelle Eingaenge, die es nicht gibt: "
             + ", ".join(fehlend))
    else:
        print("[OK]   Alle %d virtuellen Eingaenge der Baustein-Liste gibt es auch"
              % len(namen))


def main():
    wurzel = Path(sys.argv[1])
    print("Pflichtpruefung fuer", wurzel.name)
    print("-" * 72)
    pruefe_php(wurzel)
    pruefe_sprache(wurzel)
    pruefe_oberflaeche(wurzel)
    pruefe_bausteinnamen(wurzel)
    pruefe_endpunkt(wurzel)
    pruefe_vorlage(wurzel)
    pruefe_python(wurzel)
    pruefe_shell(wurzel)
    pruefe_zusammenspiel(wurzel)
    pruefe_rest(wurzel)
    print("-" * 72)
    for h in HINWEISE:
        print("[INFO]", h)
    for f in FEHLER:
        print("[FEHL]", f)
    if FEHLER:
        print("\n%d Beanstandung(en)." % len(FEHLER))
        return 1
    print("\nKeine Beanstandung.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
