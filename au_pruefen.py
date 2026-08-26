#!/usr/bin/env python3
"""Pflichtpruefung fuer das Audi-Connect-Plugin.

Ersetzt NICHT `php -l` und keinen echten Renderlauf - in diesem Arbeitsbereich
gibt es kein PHP. Die Hausregel verlangt fuer diesen Fall ausdruecklich einen
Ersatz und dessen Offenlegung: Klammer-, Tag- und <?php/?>-Bilanz zaehlen.
Genau das tut dieses Skript, zusammen mit den uebrigen Punkten der
Pflichtpruefung, die sich ohne PHP durchfuehren lassen.

Aufruf:  au_pruefen.py <pluginordner>
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
        benutzt |= set(re.findall(r"au_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t))
        # ERWEITERT 20.08.2026. Bis dahin wurden nur au_t('...') und zwei feste
        # Abschnitte gefunden. Seit die Feldliste, der Befehlskatalog und die
        # Reiterliste die Schluessel als WERTE in Feldern fuehren
        # ('bez' => 'AU_FELD.SOC') und die Oberflaeche sie ueber eine Variable
        # aufloest (au_t($info['bez'])), fand das alte Muster sie nicht mehr -
        # und meldete 33 einwandfrei benutzte Schluessel als verwaist. Jetzt
        # gilt: jede Zeichenkette der Form ABSCHNITT.SCHLUESSEL im PHP zaehlt
        # als benutzt. Das ist grosszuegiger, aber ein falscher Alarm in dieser
        # Richtung kostet Vertrauen in die ganze Pruefung.
        # Kein Treffer, der auf '_' endet: das sind Praefixe aus einer
        # Verkettung ('EINST.DIENST_' . strtoupper($befehl)), keine
        # Schluessel. Und nicht der Platzhalter aus dem Kommentar von au_t().
        for k in re.findall(r"'([A-Z][A-Z0-9_]*\.[A-Z0-9_]+)'", t):
            if not k.endswith("_") and k != "ABSCHNITT.SCHLUESSEL":
                benutzt.add(k)
        maskiert |= set(re.findall(r"au_e\(\s*au_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t))
        maskiert |= set(re.findall(r"au_e\(\s*sprintf\(\s*au_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t))
    benutzt |= {"EINST.DIENST_START", "EINST.DIENST_STOP", "EINST.DIENST_RESTART"}
    # Die Beschriftungen werden ueber au_t('EINST.L_' . strtoupper($feld))
    # gebildet. Massgeblich sind die Feldnamen der Pruefschleifen im
    # Speichern-Handler - so bleibt die Liste hier richtig, wenn dort etwas
    # dazukommt, statt von Hand nachgezogen werden zu muessen.
    oberflaeche = (wurzel / "webfrontend/htmlauth/index.php").read_text(encoding="utf-8")
    for feld in re.findall(r"^\s*'([a-z_]+)'\s*=>\s*array\(-?[0-9]+,\s*-?[0-9]+",
                           oberflaeche, re.M):
        benutzt.add("EINST.L_" + feld.upper())
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
                fehl("%s: %s laeuft durch au_e(), enthaelt aber Auszeichnung oder "
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

    # BERICHTIGT 20.08.2026. Die beiden Suchmuster verlangten wortwoertlich
    # class="sm-seite" und data-ziel="tab-x" - also die Form, in der die
    # Reiterleiste von Hand ausgeschrieben ist. Seit der Hausstandard das
    # serverseitige sm-active verlangt, steht dort
    #     class="sm-seite<?= $tab === 'tab-x' ? ' sm-active' : '' ?>"
    # und die Leiste entsteht aus einer foreach-Schleife. Beide Muster fanden
    # dann NICHTS - und die Zeile darunter meldete "0 Reiter, 0 Bereiche,
    # Positivliste deckungsgleich" als [OK]. Eine Pruefung, die bei null
    # Funden beruhigt, ist schlimmer als keine: sie sagt genau dann nichts,
    # wenn sich etwas geaendert hat.
    #
    # Jetzt werden beide Formen getroffen, die Positivliste wird auch aus
    # einem erzeugenden Feld gelesen, und null Funde sind ein FEHLER.
    ziele = re.findall(r'data-ziel="(tab-[a-z0-9]+)"', t)
    seiten = re.findall(r'class="sm-seite(?:[^"]*)" id="(tab-[a-z0-9]+)"', t)
    if not ziele:
        # Die Leiste entsteht aus dem erzeugenden Feld: data-ziel="tab-<?= ... ?>".
        # Dann ist das Feld selbst die Leiste - und genau das verlangt der
        # Hausstandard seit 07.08.2026 ("Die Reiterliste steht genau einmal").
        feld = re.search(r"\$\w*reiter\s*=\s*array\((.*?)\);", t, re.S)
        if feld and 'data-ziel="tab-<?=' in t:
            ziele = ["tab-" + x for x in re.findall(r"'([a-z0-9]+)'\s*=>", feld.group(1))]
    liste = re.search(r"\^tab-\(([a-z0-9|]+)\)", t)
    if liste:
        liste = set("tab-" + x for x in liste.group(1).split("|"))
    else:
        # Die Positivliste entsteht aus einem Feld: implode('|', array_keys(...)).
        feld = re.search(r"\$\w*reiter\s*=\s*array\((.*?)\);", t, re.S)
        liste = set("tab-" + x for x in re.findall(r"'([a-z0-9]+)'\s*=>", feld.group(1))) \
            if feld else set()
    if not ziele or not seiten:
        fehl("Es wurde kein Reiter gefunden (%d Leisteneintraege, %d Bereiche). "
             "Entweder fehlt die Reiterleiste, oder das Suchmuster trifft die "
             "verwendete Schreibweise nicht - beides ist ein Befund, kein OK."
             % (len(ziele), len(seiten)))
    # Der Hausstandard verlangt seit 20.08.2026, dass der Server entscheidet,
    # welcher Reiter offen ist: .sm-seite steht auf display:none, ohne
    # serverseitiges sm-active ist die Seite ohne JavaScript vollstaendig leer.
    if "sm-seite<?=" not in t and "sm-seite<?php" not in t:
        fehl("Kein Bereich setzt sm-active serverseitig. Ohne JavaScript zeigt "
             "die Seite dann nur die Reiterleiste und sonst nichts.")
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
    for m in re.finditer(r'<div class="sm-seite(?:[^"]*)" id="(tab-[a-z0-9]+)"', t):
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

    muster = dict(re.findall(r"au_param\('([a-z]+)',\s*'(/[^']+/)'", t))
    # Die Mindestmenge, nicht die Gesamtmenge: ein Plugin darf weitere
    # Parameter pruefen (0.9.8 kam mit dauer, name, wert, probe und tag). Bis
    # dahin verlangte diese Zeile Gleichheit und brach ab, sobald einer
    # dazukam - das Werkzeug bestand dann auf einem alten Stand.
    erwartet = {"fahrzeug", "temp", "prozent", "ampere"}
    if not erwartet <= set(muster):
        fehl("Es fehlen Parameterpruefungen: %s" % sorted(erwartet - set(muster)))

    # "abc" gehoert nur bei ZAHLENparametern zu den boesen Werten. Bei
    # 'name' ist eine Buchstabenfolge die erwartete Form; dort haelt nicht das
    # Muster, sondern die Weissliste dahinter den unbekannten Namen ab - und
    # genau so gehoert es sich: das Muster filtert die Schreibweise, die
    # Weissliste die Bedeutung.
    boese_alle = ["; rm -rf /", "../../etc/passwd", "1 OR 1=1", "<script>", "%00",
                  "1;reboot", "'", '"', "\n", "999999999999"]
    nur_zahlen = ["-1", "abc"]
    zahlenfelder = {"temp", "prozent", "ampere", "dauer", "wert", "probe", "tag"}
    gut = {"fahrzeug": ["1", "12", "WAUZZZ4M0PD000001"],
           "temp": ["21", "21.5", "21,5", "9"],
           "prozent": ["80", "100", "5"],
           "ampere": ["5", "6", "10", "13", "16", "32"],
           "dauer": ["1", "10", "60"],
           "name": ["stecker_auto", "zone_vl"],
           "wert": ["0", "1"],
           "probe": ["0", "1"],
           "tag": ["20260820"]}
    # Ein Muster, fuer das es hier keine gueltigen Beispiele gibt, wird
    # BENANNT und nicht stillschweigend uebersprungen - sonst waechst die
    # Zahl der ungeprueften Parameter, ohne dass es jemand merkt.
    for name in sorted(set(muster) - set(gut)):
        hinw("Fuer den Parameter '%s' kennt dieses Werkzeug keine gueltigen "
             "Beispielwerte - nur die boesen wurden geprueft." % name)

    for name, roh in muster.items():
        rx = re.compile("^" + roh.strip("/").lstrip("^").rstrip("$") + "$")
        boese = list(boese_alle)
        if name in zahlenfelder or name == "fahrzeug":
            boese += nur_zahlen
        for b in boese:
            if rx.match(b):
                fehl("Muster fuer %s laesst %r durch" % (name, b))
        for g in gut.get(name, []):
            if not rx.match(g):
                fehl("Muster fuer %s weist den gueltigen Wert %r ab" % (name, g))

    # Weissliste der Aktionen.
    #
    # ERWEITERT 20.08.2026: die schaltende Liste ist seit 0.9.8 nicht mehr
    # ausgeschrieben, sondern array_keys(au_befehle()) - eine Quelle fuer
    # Endpunkt, Tabelle, Vorlage und Testreiter. Wird sie so gebildet, wird
    # der Katalog gelesen.
    lesend = re.search(r"\$au_lesend = array\(([^)]*)\)", t)
    schaltend = re.search(r"\$au_schaltend = array\(([^;]*?)\);", t, re.S)
    b = set()
    if schaltend:
        b = set(re.findall(r"'([a-z_]+)'", schaltend.group(1)))
    elif re.search(r"\$au_schaltend\s*=\s*array_keys\(au_befehle\(\)\)", t):
        libtext = (wurzel / "webfrontend/html/au_lib.php").read_text(encoding="utf-8")
        kat = re.search(r"function au_befehle\(\)\s*\{(.*?)\n\}", libtext, re.S)
        if kat:
            b = set(re.findall(r"^\s*'([a-z_]+)'\s*=>\s*array\('bez'", kat.group(1), re.M))
    if not lesend or not b:
        fehl("Die Weisslisten der Aktionen sind nicht auffindbar (lesend %s, "
             "schaltend %d Eintraege)." % ("gefunden" if lesend else "fehlt", len(b)))
    else:
        a = set(re.findall(r"'([a-z_]+)'", lesend.group(1)))
        if a & b:
            fehl("Aktion steht in beiden Weisslisten: %s" % sorted(a & b))
        print("[OK]   Endpunkt: %d lesende, %d schaltende Aktionen, Muster weisen "
              "alle Angriffseingaben ab" % (len(a), len(b)))

    if "STEUERUNG_AUS" not in t or "DIENST_LAEUFT_NICHT" not in t:
        fehl("Der Endpunkt prueft nicht auf gesperrte Steuerung bzw. toten Dienst.")


# ---------------------------------------------------------------------------
# 5. Loxone-Vorlage: CRLF, Tabulatoren, Attributreihenfolge, Wohlgeformtheit
# ---------------------------------------------------------------------------
def pruefe_vorlage(wurzel):
    t = (wurzel / "webfrontend/html/au_lib.php").read_text(encoding="utf-8")
    block = re.search(r"function au_xml_virtual_in_http.*?\n}", t, re.S)
    if not block:
        fehl("au_xml_virtual_in_http() nicht gefunden.")
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
    felder = re.findall(r"^\s*'([A-Z]+)'\s*=>\s*array\('([^']*)',\s*'(AU_FELD\.[A-Z_]+)'\)",
                        t, re.M)
    if not felder:
        # Seit 0.9.8 ist der Datensatz benannt statt zweistellig:
        #   'SOC' => array('quelle_feld' => 'soc', 'einheit' => '%', 'bez' => ...)
        # Das alte Muster fand dann nichts. Es geht hier nur darum, EINHEIT und
        # Bezeichnung fuer den XML-Nachbau zu bekommen.
        for m in re.finditer(r"^\s*'([A-Z][A-Z0-9]*)'\s*=>\s*array\((.*?)\),\s*$",
                             t, re.M | re.S):
            e = re.search(r"'einheit'\s*=>\s*'([^']*)'", m.group(2))
            b = re.search(r"'bez'\s*=>\s*'([A-Z_0-9.]+)'", m.group(2))
            if e is not None and b is not None:
                felder.append((m.group(1), e.group(1), b.group(1)))
    if len(felder) < 10:
        fehl("Nur %d Felder ausgelesen - das Suchmuster passt nicht zur "
             "Datei." % len(felder))
    if not felder:
        fehl("Die Felder liessen sich nicht auslesen.")
        return
    crlf = "\r\n"
    xml = '<?xml version="1.0" encoding="utf-8"?>' + crlf
    xml += ('<VirtualInHttp Title="Audi 1" Comment="Test" '
            'Address="http://beispiel/x" PollingTime="300">' + crlf)
    for feld, einheit, _ in felder:
        xml += ("\t" + '<VirtualInHttpCmd Title="AUDI_1_%s" Comment="Bedeutung" '
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
                 "cron/cron.01min", "bin/audi.py", "bin/dienst.sh",
                 "icons/icon.svg", "icons/icon_64.png", "icons/icon_128.png",
                 "icons/icon_256.png", "icons/icon_512.png",
                 "templates/help/help.html",
                 "templates/lang/language_de.ini", "templates/lang/language_en.ini",
                 "webfrontend/htmlauth/index.php", "webfrontend/htmlauth/au_test.php",
                 "webfrontend/html/index.php", "webfrontend/html/au_lib.php"):
        if not (wurzel / pfad).is_file():
            fehl("Pflichtdatei fehlt: " + pfad)

    # Fassungen an drei Stellen
    v = {}
    for name in ("plugin.cfg", "release.cfg", "prerelease.cfg"):
        m = re.search(r"^VERSION=(.+)$", (wurzel / name).read_text(encoding="utf-8"), re.M)
        v[name] = m.group(1).strip() if m else "fehlt"
    if v["release.cfg"] != v["prerelease.cfg"]:
        fehl("release.cfg und prerelease.cfg tragen verschiedene Nummern: %s" % v)
    elif len(set(v.values())) == 1:
        print("[OK]   Fassung %s in plugin.cfg, release.cfg und prerelease.cfg gleich"
              % list(v.values())[0])
    else:
        # ERGAENZT 20.08.2026. Vorher war jede Abweichung ein Fehler. Das ist
        # bei der Vorbereitung einer Fassung aber der RICHTIGE Zustand:
        # plugin.cfg traegt schon die neue Nummer, die beiden .cfg noch die
        # zuletzt veroeffentlichte. Stuenden sie zu frueh auf der neuen, boten
        # sie jeder Anlage eine Fassung an, die es als Tag noch nicht gibt -
        # und keine koennte sie laden. Falsch herum ist es dagegen immer ein
        # Fehler: dann wird eine Fassung angeboten, die das Archiv nicht hat.
        def nz(s):
            return tuple(int(x) for x in re.findall(r"\d+", s)) or (0,)
        if nz(v["plugin.cfg"]) > nz(v["release.cfg"]):
            hinw("Fassung in Vorbereitung: plugin.cfg %s, veroeffentlicht %s. "
                 "Die beiden .cfg gehoeren erst hochgezogen, wenn der Tag "
                 "antwortet (Werkzeuge/fassung_setzen.py --auch-release)."
                 % (v["plugin.cfg"], v["release.cfg"]))
        else:
            fehl("release.cfg bietet %s an, das Plugin ist aber %s - es wird eine "
                 "Fassung angeboten, die dieses Archiv nicht enthaelt: %s"
                 % (v["release.cfg"], v["plugin.cfg"], v))

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
    py = (wurzel / "bin/audi.py").read_text(encoding="utf-8")
    lib = (wurzel / "webfrontend/html/au_lib.php").read_text(encoding="utf-8")
    ep = (wurzel / "webfrontend/html/index.php").read_text(encoding="utf-8")

    # Vorgabewerte muessen zusammenpassen. Nur die beiden Vorgabebloecke lesen -
    # sonst zaehlt jedes andere Array mit (z. B. der Rueckfallwert des
    # MQTT-Zustands).
    py_block = re.search(r"VORGABEN = \{(.*?)\n\}", py, re.S).group(1)
    lib_block = re.search(r"function au_vorgaben.*?\n}", lib, re.S).group(0)
    pv = dict(re.findall(r'^\s*"([a-z_]+)":\s*([0-9]+|"[a-z]+"),', py_block, re.M))
    lv = dict(re.findall(r"^\s*'([a-z_]+)'\s*=>\s*([0-9]+|'[a-z]+'),", lib_block, re.M))
    for k in set(pv) & set(lv):
        a = pv[k].strip('"')
        b = lv[k].strip("'")
        if a != b:
            fehl("Vorgabewert %s: audi.py sagt %s, au_lib.php sagt %s" % (k, a, b))
    nur_py = set(pv) - set(lv)
    # Schluessel, die es nur in der Bibliothek gibt: sie betreffen Endpunkt und
    # Oberflaeche, der Dienst liest sie nie. Wer hier etwas hinzufuegt, muss
    # begruenden koennen, warum der Dienst es nicht braucht.
    nur_php = set(lv) - set(pv) - {"aktionstoken", "schalttoken", "wartezeit",
                                   "nur_miniserver"}
    if nur_py:
        fehl("Vorgabewerte nur in audi.py: %s" % sorted(nur_py))
    if nur_php:
        fehl("Vorgabewerte nur in au_lib.php: %s" % sorted(nur_php))
    print("[OK]   %d Vorgabewerte in Dienst und Bibliothek gleich" % len(set(pv) & set(lv)))

    # Jede schaltende Aktion des Endpunkts muss der Dienst kennen.
    #
    # ERWEITERT 20.08.2026: die Weissliste ist seit 0.9.8 nicht mehr
    # ausgeschrieben, sondern array_keys(au_befehle()) - EINE Quelle fuer
    # Endpunkt, Tabelle, Vorlage und Testreiter. Findet sich das Feld nicht,
    # wird der Katalog gelesen. Ein Muster, das nichts findet, darf nicht in
    # eine leere Menge und damit in ein stilles [OK] laufen.
    m = re.search(r"\$au_schaltend = array\((.*?)\);", ep, re.S)
    if m:
        aktionen = set(re.findall(r"'([a-z_]+)'", m.group(1)))
    else:
        kat = re.search(r"function au_befehle\(\)\s*\{(.*?)\n\}", lib, re.S)
        aktionen = set(re.findall(r"^\s*'([a-z_]+)'\s*=>\s*array\('bez'", kat.group(1), re.M)) \
            if kat else set()
    if not aktionen:
        fehl("Die Weissliste der schaltenden Aktionen liess sich nicht auslesen - "
             "weder als Feld im Endpunkt noch als Katalog in au_lib.php.")
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

    # Jedes MQTT-Feld der Themenliste muss der Dienst auch senden - und
    # umgekehrt. Ein Thema, das der Dienst sendet und keine Tabelle nennt, ist
    # ein Wert, den niemand findet.
    #
    # ERWEITERT 20.08.2026: die Themenliste entsteht seit 0.9.8 aus der
    # Feldliste ('mqtt' => '...'), aus einem Block fuer die Klartexte und aus
    # einzelnen Zeilen $t['fahrzeugN/...']. Alle drei Formen werden gelesen.
    mq = set(re.findall(r"'fahrzeugN/([a-z_0-9]+)'", lib))
    mq |= set(x for x in re.findall(r"'mqtt'\s*=>\s*'([a-z_0-9]*)'", lib) if x)
    block = re.search(r"foreach \(array\('zustand_text'(.*?)\) as \$k => \$b\)", lib, re.S)
    if block:
        mq |= set(re.findall(r"'([a-z_0-9]+)'\s*=>", block.group(1))) | {"zustand_text"}
    roh = re.search(r"MQTT_FELDER = \((.*?)\n\)", py, re.S).group(1)
    gesendet = set(re.findall(r'"([a-z_0-9]+)"', roh))
    texte = re.search(r"MQTT_TEXTE = \((.*?)\)", py, re.S)
    if texte:
        gesendet |= set(re.findall(r'"([a-z_0-9]+)"', texte.group(1)))
    fehlt = mq - gesendet
    if fehlt:
        fehl("Der MQTT-Reiter nennt Themen, die der Dienst nicht sendet: %s" % sorted(fehlt))
    zuviel = gesendet - mq
    if zuviel:
        fehl("Der Dienst sendet Themen, die der MQTT-Reiter nicht nennt: %s" % sorted(zuviel))
    print("[OK]   %d MQTT-Themen: Reiter und Dienst decken sich" % len(mq))

    # Jedes Feld der Endpunkt-Ausgabe muss in der Feldliste stehen.
    #
    # NEU GEFASST 20.08.2026. Bis 0.9.7 schrieb der Endpunkt jede Zeile mit
    # einem eigenen printf, und diese Pruefung verglich die Formatzeichenkette
    # mit der Feldliste. Genau diese Verdopplung war die Fehlerquelle: ALTER
    # ging in zwei Zeilen hinaus und stand in keiner der beiden Listen, GRUND
    # und FEHLERTEXT in allen und in keiner.
    #
    # Seit 0.9.8 baut au_zeile() die Antwort AUS der Feldliste. Ein Vergleich
    # zweier Listen ist damit sinnlos - es gibt nur noch eine. Geprueft wird
    # deshalb, dass es dabei bleibt: kein eigenes printf mit einer
    # Statuszeile, und jede Aktion geht durch au_zeile().
    eigenbau = re.findall(r'printf\("(AUDI|LADEN|WARTUNG|POSITION);', ep)
    if eigenbau:
        fehl("Der Endpunkt baut die Zeile %s selbst zusammen, statt sie aus der "
             "Feldliste zu erzeugen. Damit gibt es wieder zwei Listen, die "
             "auseinanderlaufen koennen." % sorted(set(eigenbau)))
    elif re.search(r"function \w+_zeile\(", lib):
        gebaut = set(re.findall(r"\w+_zeile\('([A-Z]+)'", ep))
        erwartet = {"AUDI", "LADEN", "WARTUNG", "POSITION"}
        if not erwartet <= gebaut:
            fehl("Diese Endpunktzeilen entstehen nicht aus der Feldliste: %s"
                 % sorted(erwartet - gebaut))
        else:
            print("[OK]   Alle %d Endpunktzeilen entstehen aus der einen Feldliste"
                  % len(gebaut))
    else:
        fehl("Weder ein eigenes printf noch eine erzeugende Funktion gefunden - "
             "die Herkunft der Endpunktzeilen liess sich nicht feststellen.")


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
    for fn in ("status", "laden", "wartung", "position"):
        block = re.search(r"function \w+_%s_felder.*?\n\}" % fn, lib, re.S)
        if block:
            felder |= set(re.findall(r"^\s*'([A-Z]+)'\s*=>", block.group(0), re.M))
    # ERWEITERT 20.08.2026: seit 0.9.8 gibt es EINE Feldliste, aus der die vier
    # Endpunktlisten abgeleitet werden - die vier Funktionen enthalten dann
    # keine Feldnamen mehr, und die Schleife darueber fand nichts. Ein leeres
    # Ergebnis haette JEDEN Bausteinnamen als "gibt es nicht" gemeldet.
    einzeln = re.search(r"function \w+_felder\(\)\s*\{(.*?)\n\}", lib, re.S)
    if einzeln:
        felder |= set(re.findall(r"^\s*'([A-Z][A-Z0-9]*)'\s*=>\s*array\(", einzeln.group(1), re.M))
    if not felder:
        fehl("Es liess sich keine einzige Feldbezeichnung auslesen - das "
             "Suchmuster passt nicht zur Datei. Ohne Feldliste ist jede "
             "Aussage ueber die Baustein-Liste wertlos.")
        return
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
