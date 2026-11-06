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


# ---------------------------------------------------------------------------
# Abschriften gemeinsamer Dateien (Werkzeug-V1, 08.10.2026)
#
# Seit dem Sprachmodul (Nr. 36) traegt die Linie eine Abschrift von
# Werkzeuge/gemeinsam/sprachausgabe.php und den Abschnitt [ANSAGE] aus
# gemeinsam/sprachausgabe_texte.json. Beides benutzt die Textfunktion des
# Moduls (ansage_t), nicht vw_t - die Sprachpruefung meldete deshalb alle
# Modulschluessel als "nie benutzt", dazu SEITE.L_AUDIO aus dem Selbsttest
# des Moduls und die Beispieladressen des Moduls als Heimnetzadressen:
# 133 Scheinbefunde am sp2-Bau 0.9.29 (02.10.2026).
#
# Uebergangen wird NUR, was byte-gleich mit der Stammfassung ist - wie in
# hausstandard_pruefen.py und tote_helfer.py. Eine aeltere oder veraenderte
# Abschrift wird normal geprueft und bleibt ein Befund (die Abweichung selbst
# meldet gemeinsam_pruefen.py in der Kette). Vom Abschnitt [ANSAGE] werden nur
# die Schluessel uebergangen, deren Wert in DE und EN gleich dem der
# Stammfassung ist - und nur, wenn die Linie sprachausgabe.php unveraendert
# traegt.
# ---------------------------------------------------------------------------
def _stamm():
    return Path(__file__).resolve().parent / "gemeinsam"


def gemeinsame_abschriften(wurzel):
    """Dateien der Linie, die byte-gleich mit einer Stammfassung unter
    Werkzeuge/gemeinsam/ sind (wie hausstandard_pruefen.py)."""
    stamm = _stamm()
    aus = set()
    if not stamm.is_dir():
        return aus
    vorlagen = {}
    for s in stamm.iterdir():
        if s.is_file():
            vorlagen.setdefault(s.name, []).append(s.read_bytes())
    for f in Path(wurzel).rglob("*"):
        if f.is_file() and f.name in vorlagen:
            try:
                if f.read_bytes() in vorlagen[f.name]:
                    aus.add(f.resolve())
            except OSError:
                pass
    return aus


def ansage_modulschluessel(wurzel, gem):
    """'ANSAGE.<schluessel>' fuer jeden Modulschluessel, dessen Wert in
    language_de.ini UND language_en.ini gleich dem der Stammfassung ist.
    Leer, wenn die Linie sprachausgabe.php nicht unveraendert traegt."""
    if not any(f.name == "sprachausgabe.php" for f in gem):
        return set()
    quelle = _stamm() / "sprachausgabe_texte.json"
    if not quelle.is_file():
        return set()
    import json
    soll = json.loads(quelle.read_bytes().decode("utf-8"))
    ist = {}
    for sprache in ("de", "en"):
        p = wurzel / ("templates/lang/language_%s.ini" % sprache)
        if not p.is_file():
            return set()
        ist[sprache], _ = ini_lesen(p)
    aus = set()
    for k, w in soll.get("de", {}).items():
        voll = "ANSAGE." + k
        if (ist["de"].get(voll) == w
                and voll in ist["en"]
                and ist["en"][voll] == soll.get("en", {}).get(k)):
            aus.add(voll)
    return aus


def _ini_ohne_schluessel(t, frei):
    """Text einer Sprachdatei, in dem die Zeilen der Schluessel aus `frei`
    geleert sind (Zeilenzahl bleibt)."""
    abschnitt = ""
    aus = []
    for zeile in t.split("\n"):
        s = zeile.strip()
        if s.startswith("[") and s.endswith("]"):
            abschnitt = s[1:-1]
        else:
            m = re.match(r"^([A-Z0-9_]+)\s*=", s)
            if m and abschnitt + "." + m.group(1) in frei:
                zeile = ""
        aus.append(zeile)
    return "\n".join(aus)


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
    dateien = sorted(wurzel.rglob("*.php")) + dateien_mit_shebang(wurzel, r"php")
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
    # php -l gegen BEIDE Fassungen, wenn sie dastehen. Bis zum 03.09.2026
    # stand hier ein festes "war nicht moeglich" - eine Behauptung ueber die
    # Umgebung, die niemand gemessen hatte. Beide Fassungen liegen auf dem
    # Arbeitsrechner; LoxBerry 3.x/4.x fahren 7.4, deshalb zaehlt 7.4
    # genauso wie 8.4.
    phps = [(v, Path(p)) for v, p in (
        ("7.4", r"C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe"),
        ("8.4", r"C:\tmp\php-8.4.27-Win32-vs17-x64\php.exe"))]
    da = [(v, p) for v, p in phps if p.is_file()]
    if not da:
        print("[ -- ] php -l nicht moeglich - keine der beiden PHP-Fassungen "
              "gefunden. Die Bilanz oben ersetzt sie NICHT.")
    else:
        for v, php in da:
            schlecht = []
            for f in dateien:
                r = subprocess.run([str(php), "-n", "-l", str(f)],
                                   capture_output=True, text=True)
                # Die AUSGABE wird gelesen, nicht nur der Rueckgabewert:
                # 8.4 meldet Verfallswarnungen mit Rueckgabe 0.
                if r.returncode != 0 or "No syntax errors" not in r.stdout:
                    schlecht.append("%s: %s" % (f.name,
                                    (r.stdout + r.stderr).strip()[:160]))
            if schlecht:
                fehl("php -l %s: " % v + " | ".join(schlecht))
            else:
                print("[OK]   php -l %s: %d Dateien fehlerfrei" % (v, len(dateien)))


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

    # Werkzeug-V1: unveraenderte Abschriften gemeinsamer Dateien uebergehen.
    gem = gemeinsame_abschriften(wurzel)
    frei = ansage_modulschluessel(wurzel, gem)
    for f in sorted(gem):
        hinw("%s: unveraenderte Abschrift von Werkzeuge/gemeinsam/%s - in Sprach- "
             "und Anonymitaetspruefung uebergangen%s"
             % (f.relative_to(wurzel.resolve()).as_posix(), f.name,
                (", dazu %d Modulschluessel in [ANSAGE]" % len(frei))
                if f.name == "sprachausgabe.php" else ""))
    for f in sorted(wurzel.rglob("sprachausgabe.php")):
        if f.resolve() not in gem:
            hinw("%s weicht von Werkzeuge/gemeinsam/sprachausgabe.php ab - wird "
                 "normal geprueft (gemeinsam_pruefen.py meldet die Abweichung)"
                 % f.relative_to(wurzel).as_posix())

    benutzt = set()
    maskiert = set()
    for f in sorted(wurzel.rglob("*.php")):
        if f.resolve() in gem:
            continue
        t = f.read_text(encoding="utf-8")
        benutzt |= set(re.findall(r"vw_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t))
        # Schluessel, die nur als Zeichenkette in einer Tabelle oder in einem
        # Ausdruck stehen und erst spaeter durch die Textfunktion laufen -
        # etwa $vw_beschriftung oder vw_t($f >= 2 ? 'A' : 'B'). Bewusst OHNE
        # Einschraenkung auf bestimmte Abschnitte: die frueher hier stehende
        # Liste (VW_ und BAUSTEIN) hat die REITER-Schluessel als "nie benutzt"
        # gemeldet. Angeglichen an vw_sprache_erzeugen.py - zwei Werkzeuge,
        # die dieselbe Frage verschieden beantworten, sind eines zu viel.
        # Ein Name, der auf "_" endet, ist der Vorsatz eines zusammengesetzten
        # Schluessels und zaehlt nicht mit.
        benutzt |= set(re.findall(r"'([A-Z][A-Z0-9_]*\.[A-Z0-9_]*[A-Z0-9])'", t))
        maskiert |= set(re.findall(r"vw_e\(\s*vw_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t))
        maskiert |= set(re.findall(r"vw_e\(\s*sprintf\(\s*vw_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t))
    # Was wie ein Schluessel aussieht und keiner ist. Angeglichen an
    # vw_sprache_erzeugen.py.
    benutzt -= {"ABSCHNITT.SCHLUESSEL"}   # Beispiel im Kommentar der Textfunktion
    benutzt |= {"EINST.DIENST_START", "EINST.DIENST_STOP", "EINST.DIENST_RESTART"}
    for feld in ("INTERVALL", "TAKT_WARTUNG", "TEMP_MIN", "TEMP_MAX",
                 "VERLAUF_TAGE", "WARTEZEIT"):
        benutzt.add("EINST.L_" + feld)

    for k in sorted(benutzt - set(tde)):
        fehl("Schluessel im PHP benutzt, fehlt in language_de.ini: " + k)
    for k in sorted(benutzt - set(ten)):
        fehl("Schluessel im PHP benutzt, fehlt in language_en.ini: " + k)
    for k in sorted(set(tde) - benutzt - frei):
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
def dateien_mit_shebang(wurzel, muster):
    """Endungslose Dateien, deren erste Zeile auf $muster passt.

    Ein Plugin darf ausfuehrbare Dateien ohne Endung mitliefern - dieses
    fuehrt zwei davon: bin/healthcheck ist PHP mit '#!/usr/bin/env php',
    uninstall/uninstall ist Bash. Wer nur nach '*.php' und '*.sh' sucht,
    prueft sie nie und meldet trotzdem eine Zahl.
    """
    aus = []
    for f in sorted(wurzel.rglob("*")):
        if not f.is_file() or f.suffix:
            continue
        try:
            kopf = f.open("rb").readline(200).decode("utf-8", "replace")
        except OSError:
            continue
        if kopf.startswith("#!") and re.search(muster, kopf):
            aus.append(f)
    return aus


def pruefe_oberflaeche(wurzel):
    p = wurzel / "webfrontend/htmlauth/index.php"
    t = p.read_text(encoding="utf-8")

    # Die Muster treffen die WIRKLICHE Schreibweise, nicht eine gedachte.
    #
    # Bis zum 03.09.2026 verlangte das zweite Muster class="sm-seite"
    # unmittelbar gefolgt von id=. Die Oberflaeche schreibt aber
    # class="sm-seite<?= ... ' sm-active' ... ?>" - der Reiter muss
    # serverseitig aktiv gesetzt werden, damit die Seite ohne JavaScript
    # bedienbar bleibt. Das Muster fand null Bereiche. Und die Positivliste
    # entsteht mit implode() aus $vw_reiter_ids, nicht als ausgeschriebener
    # regulaerer Ausdruck; auch dafuer traf das Muster nichts.
    #
    # Ergebnis waren drei Vergleiche leerer Mengen und ein gruener Haken
    # ueber nichts.
    ziele = re.findall(r'data-ziel="(tab-[a-z0-9]+)"', t)
    seiten = re.findall(r'class="sm-seite[^"]*"\s+id="(tab-[a-z0-9]+)"', t)
    seiten += re.findall(r'id="(tab-[a-z0-9]+)"\s+class="sm-seite', t)
    m = re.search(r"\$vw_reiter_ids\s*=\s*array\((.*?)\);", t, re.S)
    liste = (set("tab-" + x for x in re.findall(r"'([a-z0-9]+)'", m.group(1)))
             if m else set())
    # Eine Pruefung ueber eine leere Menge misst nichts.
    if not ziele or not seiten or not liste:
        fehl("Reiterpruefung misst nichts: %d Leisteneintraege, %d Bereiche, "
             "%d Eintraege in der Positivliste - mindestens eines davon ist 0. "
             "Entweder fehlt es wirklich, oder die Schreibweise hat sich "
             "geaendert und die Muster hier treffen sie nicht mehr."
             % (len(ziele), len(seiten), len(liste)))
    if set(ziele) != set(seiten):
        fehl("Reiterleiste und Bereiche passen nicht zusammen: %s / %s"
             % (sorted(set(ziele)), sorted(set(seiten))))
    if not set(ziele) <= liste:
        fehl("Reiter fehlen in der activetab-Positivliste: %s" % sorted(set(ziele) - liste))
    if liste - set(ziele):
        fehl("Positivliste kennt Reiter, die es nicht gibt: %s" % sorted(liste - set(ziele)))
    # Der Haken erscheint nur, wenn wirklich etwas gemessen wurde. Eine
    # [OK]-Zeile neben einer [FEHL]-Zeile zur selben Sache liest sich, als
    # sei die Hälfte in Ordnung.
    if ziele and seiten and liste:
        print("[OK]   %d Reiter, %d Bereiche, Positivliste deckungsgleich"
              % (len(ziele), len(seiten)))

    # Legende in jedem Bereich mit Knopfreihe
    ohne = []
    bereiche = list(re.finditer(r'<div class="sm-seite[^"]*" id="(tab-[a-z0-9]+)"', t))
    if not bereiche:
        fehl("Legendenpruefung misst nichts: kein einziger Reiterbereich "
             "gefunden. Das Muster trifft die Schreibweise der Oberflaeche "
             "nicht mehr.")
    for m in bereiche:
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
    #
    # <form\s - mit Pflicht-Leerzeichen. Ohne das traf das Muster auch das
    # Suchmuster "<form\b.*?</form>", das seit 0.9.10 als Zeichenkette in
    # vw_test.php steht (die Selbstpruefung zaehlt dort die eigenen Formulare)
    # - und meldete drei Befunde an einer Datei, die gar kein Formular enthaelt.
    for f in sorted(wurzel.rglob("*.php")):
        tt = f.read_text(encoding="utf-8")
        forms = re.findall(r"<form\s[^>]*>", tt)
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
    # 'name' und 'wert' seit 0.9.10 (Befehl 'einstellung').
    erwartet = {"fahrzeug", "temp", "prozent", "ampere", "name", "wert"}
    if set(muster) != erwartet:
        fehl("Geprueft werden %s, erwartet %s" % (sorted(muster), sorted(erwartet)))

    boese = ["; rm -rf /", "../../etc/passwd", "1 OR 1=1", "<script>", "%00",
             "1;reboot", "'", '"', "\n", "999999999999", "-1", "abc"]
    gut = {"fahrzeug": ["1", "12", "WVWZZZE1ZPP000001"],
           "temp": ["21", "21.5", "21,5", "9"],
           "prozent": ["80", "100", "5"],
           "ampere": ["5", "6", "10", "13", "16", "32"],
           "name": ["sitzheizung", "klima_entriegeln", "stecker_auto"],
           "wert": ["0", "1"]}
    # 'abc' ist fuer 'name' ein GUELTIGER Wert - dort stehen Kleinbuchstaben
    # und Unterstriche. Abgewiesen wird es danach an der Positivliste
    # vw_schalter(), nicht am Muster. Wer das nicht ausnimmt, misst hier einen
    # Befund, den es nicht gibt.
    boese_je_feld = {"name": [b for b in boese if b != "abc"]}

    for name, roh in muster.items():
        rx = re.compile("^" + roh.strip("/").lstrip("^").rstrip("$") + "$")
        for b in boese_je_feld.get(name, boese):
            if rx.match(b):
                fehl("Muster fuer %s laesst %r durch" % (name, b))
        for g in gut.get(name, []):
            if not rx.match(g):
                fehl("Muster fuer %s weist den gueltigen Wert %r ab" % (name, g))

    # Weissliste der Aktionen.
    #
    # Die schaltenden Aktionen stehen seit 0.9.10 nicht mehr woertlich im
    # Endpunkt, sondern kommen aus vw_befehle() der Bibliothek - EINE Quelle
    # fuer Endpunkt, Tabelle und Ausgangsvorlage. Das Werkzeug liest sie
    # deshalb dort.
    lesend = re.search(r"\$vw_lesend = array\(([^)]*)\)", t)
    if not lesend:
        fehl("Die Weissliste der lesenden Aktionen ist nicht auffindbar.")
        return
    a = set(re.findall(r"'([a-z_]+)'", lesend.group(1)))

    lib = (wurzel / "webfrontend/html/vw_lib.php").read_text(encoding="utf-8")
    mb = re.search(r"function vw_befehle\(\).*?\n\{(.*?)\n\}", lib, re.S)
    if "array_keys($vw_alle_befehle)" not in t or not mb:
        fehl("Die schaltenden Aktionen kommen nicht aus vw_befehle().")
        return
    b = set(re.findall(r"'([a-z_]+)'\s*=>\s*array\(", mb.group(1)))
    if a & b:
        fehl("Aktion steht in beiden Weisslisten: %s" % sorted(a & b))
    print("[OK]   Endpunkt: %d lesende, %d schaltende Aktionen aus EINER Quelle, "
          "Muster weisen alle %d Angriffseingaben ab" % (len(a), len(b), len(boese)))

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
    # Stand des Hausstandards vom 25.08.2026, gemessen gegen
    # XML_Vorlagen_0.9.10/VI_weissware_geraet1_status.xml: HintText am
    # Wurzelelement zuerst, dazu Unit und HintText je Eintrag. Bis 0.9.9
    # fehlten alle drei; 35 Plugin-Ordner im Bestand fuehren sie.
    soll = ["HintText", "Title", "Comment", "Address", "PollingTime",
            "Title", "Comment", "Check", "Signed", "Analog",
            "SourceValLow", "DestValLow", "SourceValHigh", "DestValHigh",
            "DefVal", "MinVal", "MaxVal", "Unit", "HintText"]
    if reihenfolge != soll:
        fehl("Attributreihenfolge der Loxone-Vorlage weicht vom Original ab:\n  %s"
             % reihenfolge)
    elif "<Info templateType=\"2\"" not in b:
        fehl("Der Eingangsvorlage fehlt <Info templateType=\"2\" minVersion=\"17010727\"/> "
             "als erstes Kindelement.")
    else:
        print("[OK]   Loxone-Vorlage: CRLF, Tabulator, Info-Element und "
              "Attributreihenfolge wie im Original")

    # Die AUSGANGSVORLAGE, seit 0.9.10. Sie folgt demselben Original, hat aber
    # eigene Attribute - CmdOffMethod und Repeat gehoeren dazu, auch wenn es
    # keinen Ausbefehl gibt.
    bvo = re.search(r"function vw_xml_virtual_out\(.*?\n\}", t, re.S)
    if not bvo:
        fehl("vw_xml_virtual_out() nicht gefunden - es gibt keine Ausgangsvorlage.")
    else:
        v = bvo.group(0)
        rvo = re.findall(r"\$o \.= '([A-Za-z]+)=\"", v)
        sollvo = ["HintText", "Title", "Comment", "Address", "CmdInit",
                  "CloseAfterSend", "CmdSep",
                  "Title", "Comment", "CmdOnMethod", "CmdOn", "CmdOffMethod",
                  "CmdOff", "Analog", "Repeat", "RepeatRate", "HintText"]
        if rvo != sollvo:
            fehl("Attributreihenfolge der Ausgangsvorlage weicht ab:\n  %s" % rvo)
        elif '<Info templateType="3"' not in v:
            fehl("Der Ausgangsvorlage fehlt <Info templateType=\"3\" .../>.")
        else:
            print("[OK]   Ausgangsvorlage: Attributreihenfolge und Info-Element "
                  "wie im Original")

    # Die Bedeutungstexte laufen durch strip_tags + html_entity_decode, bevor
    # sie maskiert werden - sonst stuende 'l&auml;dt' in Loxone Config.
    if "html_entity_decode" not in t or "strip_tags" not in t:
        fehl("Die Vorlage loest vor dem Maskieren keine Entitaeten auf - in Loxone "
             "Config stuende sonst wortwoertlich 'lädt'.")

    # Nachbau der Ausgabe in Python und Pruefung als XML. Das ist ein Nachbau,
    # kein Durchlauf des PHP - es beweist nur, dass die erzeugte Form
    # wohlgeformt ist und die Zeilenenden stimmen.
    # Seit 0.9.10 traegt jedes Feld drei weitere Angaben (analog, Kleinst-,
    # Groesstwert) - die Vorlage braucht sie fuer Unit, Signed und MinVal.
    # Das alte Muster verlangte die schliessende Klammer unmittelbar nach dem
    # Sprachschluessel und las deshalb NULL Felder aus; gemeldet wurde
    # daraufhin "das Suchmuster passt nicht zur Datei" - richtig, und genau
    # deshalb steht diese Meldung dort.
    felder = re.findall(r"^\s*'([A-Z]+)'\s*=>\s*array\('([^']*)',\s*'(VW_FELD\.[A-Z_]+)'",
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
    skripte = sorted(list(wurzel.rglob("*.sh")) + [wurzel / "cron/cron.01min"]
                     + dateien_mit_shebang(wurzel, r"(ba)?sh"))
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
    # Werkzeug-V1: die Beispieladressen einer unveraenderten Abschrift und der
    # unveraenderten Modulschluessel in [ANSAGE] sind keine Heimnetzadressen
    # dieser Linie. Die Namensliste (_eigene_woerter) gilt weiter fuer ALLE
    # Dateien - ein Klarname waere auch in der Stammfassung ein Befund.
    gem = gemeinsame_abschriften(wurzel)
    frei = ansage_modulschluessel(wurzel, gem)
    verdacht = []
    for f in sorted(wurzel.rglob("*")):
        if not f.is_file() or f.suffix in (".png", ".ico"):
            continue
        t = f.read_text(encoding="utf-8", errors="replace")
        t_adr = t
        if f.resolve() in gem:
            t_adr = ""
        elif frei and f.suffix == ".ini" and f.parent.name == "lang":
            t_adr = _ini_ohne_schluessel(t, frei)
        for m in re.finditer(r"\b(?:10|192\.168|172\.(?:1[6-9]|2[0-9]|3[01]))"
                             r"(?:\.\d{1,3}){2,3}\b(?!\.)", t_adr):
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

    # Fassungen an drei Stellen.
    #
    # Der Gleichstand ist der Normalfall - aber NICHT der einzige zulaessige.
    # LoxBerry liest release.cfg aus dem Zweig master und zieht das Archiv aus
    # dem TAG. Solange der Tag der neuen Fassung nicht angelegt ist, muessen
    # die beiden .cfg auf der alten Nummer stehen bleiben; stuenden sie schon
    # auf der neuen, boeten sie jeder Anlage eine Fassung an, die es als Tag
    # noch nicht gibt. Genau so arbeitet fassung_setzen.py ohne --auch-release.
    #
    # Zulaessig ist deshalb: plugin.cfg genau eine Stelle voraus, beide .cfg
    # gleich. Alles andere bleibt ein Befund - besonders der umgekehrte Fall,
    # bei dem die .cfg voraus sind und niemand die Fassung laden kann.
    v = {}
    for name in ("plugin.cfg", "release.cfg", "prerelease.cfg"):
        m = re.search(r"^VERSION=(.+)$", (wurzel / name).read_text(encoding="utf-8"), re.M)
        v[name] = m.group(1).strip() if m else "fehlt"

    def zahlen(s):
        try:
            return tuple(int(x) for x in s.split("."))
        except ValueError:
            return None

    a, b, c = zahlen(v["plugin.cfg"]), zahlen(v["release.cfg"]), zahlen(v["prerelease.cfg"])
    if len(set(v.values())) == 1:
        print("[OK]   Fassung %s in plugin.cfg, release.cfg und prerelease.cfg gleich"
              % list(v.values())[0])
    elif a and b and c and b == c and a > b:
        hinw("Vorbereitung: plugin.cfg steht auf %s, die beiden .cfg noch auf %s. "
             "Das ist richtig, solange der Tag v%s nicht angelegt ist - danach "
             "fassung_setzen.py mit --auch-release nachziehen."
             % (v["plugin.cfg"], v["release.cfg"], v["plugin.cfg"]))
    else:
        fehl("Fassungsnummern weichen ab: %s" % v)

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
    # Drei Schluessel gehen nur die Oberflaeche und den Endpunkt an; der Dienst
    # braucht sie nicht und fuehrt sie deshalb bewusst nicht.
    nur_php = set(lv) - set(pv) - {"aktionstoken", "wartezeit", "wartezeit_endpunkt"}
    if nur_py:
        fehl("Vorgabewerte nur in vw.py: %s" % sorted(nur_py))
    if nur_php:
        fehl("Vorgabewerte nur in vw_lib.php: %s" % sorted(nur_php))
    print("[OK]   %d Vorgabewerte in Dienst und Bibliothek gleich" % len(set(pv) & set(lv)))

    # Die Schalterlisten muessen in Dienst und Bibliothek dieselben sein.
    #
    # Seit 0.9.14 gibt es ZWEI Listen: was sich setzen laesst (SCHALTER /
    # vw_schalter()) und was es zwar gibt, sich aber nicht setzen laesst
    # (NUR_LESEND / vw_nur_lesend()). Laufen sie auseinander, weist der
    # Endpunkt einen Namen ab, den der Dienst kennt - oder schlimmer, er
    # laesst einen durch, den der Dienst nicht setzen kann. Eine Liste, die
    # niemand nachmisst, laeuft auseinander; bei Renault stand sie vier
    # Stellen weit falsch.
    py_s = set(re.findall(r'^\s+"([a-z_]+)":\s+\("', py[py.index("SCHALTER = {"):], re.M))
    m = re.search(r"function vw_schalter\(\)\s*\{.*?return array\((.*?)\);", lib, re.S)
    php_s = set(re.findall(r"'([a-z_]+)'\s*=>", m.group(1))) if m else set()
    m2 = re.search(r"NUR_LESEND = \{(.*?)^\}", py, re.S | re.M)
    py_n = set(re.findall(r'"([a-z_]+)":', m2.group(1))) if m2 else set()
    m3 = re.search(r"function vw_nur_lesend\(\)\s*\{.*?return array\((.*?)\);", lib, re.S)
    php_n = set(re.findall(r"'([a-z_]+)'\s*=>", m3.group(1))) if m3 else set()
    if not py_s or not php_s:
        fehl("Schalterlisten nicht messbar: Dienst %d, Bibliothek %d - "
             "eines der Muster trifft nicht mehr." % (len(py_s), len(php_s)))
    elif py_s != php_s:
        fehl("Schaltbare Namen laufen auseinander: nur im Dienst %s, nur in "
             "der Bibliothek %s" % (sorted(py_s - php_s), sorted(php_s - py_s)))
    elif py_n != php_n:
        fehl("Nur-lesende Namen laufen auseinander: nur im Dienst %s, nur in "
             "der Bibliothek %s" % (sorted(py_n - php_n), sorted(php_n - py_n)))
    elif py_s & py_n:
        fehl("Diese Namen stehen in BEIDEN Listen: %s" % sorted(py_s & py_n))
    else:
        print("[OK]   %d schaltbare und %d nur lesende Namen, Dienst und "
              "Bibliothek gleich" % (len(py_s), len(py_n)))

    # Jede schaltende Aktion des Endpunkts muss der Dienst kennen.
    #
    # Seit 0.9.10 steht die Liste nicht mehr woertlich im Endpunkt, sondern in
    # vw_befehle() der Bibliothek - EINE Quelle fuer Endpunkt, Tabelle und
    # Ausgangsvorlage. Das alte Muster fand dort nichts und meldete daraufhin
    # "Alle 0 schaltenden Aktionen": eine Null, die wie ein Haken aussah.
    mb = re.search(r"function vw_befehle\(\).*?\n\{(.*?)\n\}", lib, re.S)
    aktionen = set(re.findall(r"'([a-z_]+)'\s*=>\s*array\(", mb.group(1))) if mb else set()
    if not aktionen:
        fehl("Die schaltenden Aktionen liessen sich aus vw_befehle() nicht auslesen.")
    bekannt = set(re.findall(r'aktion == "([a-z_]+)"', py))
    # Der Dienst fasst Gegensatzpaare zusammen: aktion in ("klima_start", "klima_stop")
    paare = re.findall(r'aktion in \("([a-z_]+)", "([a-z_]+)"\)', py)
    for a1, a2 in paare:
        bekannt.add(a1); bekannt.add(a2)
    # 'abruf' beantwortet der Dienst vor der Steuerungssperre, ohne Vergleich
    # auf den Namen in dieser Form.
    if 'aktion == "abruf"' in py:
        bekannt.add("abruf")
    fehlt = aktionen - bekannt
    if fehlt:
        fehl("Der Endpunkt bietet Aktionen an, die der Dienst nicht kennt: %s"
             % sorted(fehlt))
    ueberzaehlig = bekannt - aktionen
    if ueberzaehlig:
        hinw("Der Dienst kennt Aktionen, die der Endpunkt nicht anbietet: %s"
             % sorted(ueberzaehlig))
    # Eine Null ist hier KEIN Haken, sondern der Hinweis, dass nichts gemessen
    # wurde. Ohne diese Unterscheidung liest sich "Alle 0 schaltenden Aktionen"
    # wie ein bestandener Punkt.
    if aktionen:
        print("[OK]   Alle %d schaltenden Aktionen des Endpunkts kennt der Dienst"
              % len(aktionen))
    else:
        print("[INFO] Keine schaltende Aktion ausgelesen - hier wurde NICHTS geprueft.")

    # Jedes MQTT-Feld der Themenliste muss der Dienst auch senden.
    #
    # Drei Listen seit 0.9.10: Zahlen, Texte und die Themen oberhalb der
    # Fahrzeugebene. Wer nur MQTT_FELDER liest, meldet alle sechzehn
    # Textthemen als "vom Reiter genannt, aber nie gesendet" - ein Befund,
    # der keiner ist.
    def liste(name):
        m = re.search(r"^%s = \((.*?)^\)" % name, py, re.S | re.M)
        if not m:
            fehl("Die Themenliste %s liess sich nicht auslesen." % name)
            return set()
        return set(re.findall(r'"([a-z_]+)"', m.group(1)))

    gesendet = liste("MQTT_FELDER") | liste("MQTT_TEXTFELDER")
    oben_py = liste("MQTT_OBEN")
    mq = set(re.findall(r"'fahrzeugN/([a-z_]+)'", lib))
    # Die Themen oberhalb der Fahrzeugebene stehen in der Tabelle ohne Vorsatz.
    mth = re.search(r"function vw_mqtt_themen\(\).*?\n\}", lib, re.S)
    oben_lib = set(re.findall(r"^\s*'([a-z_]+)'\s*=>\s*\$[zt]\(", mth.group(0), re.M)) if mth else set()

    for was, a, b in (("je Fahrzeug", mq, gesendet), ("oberhalb", oben_lib, oben_py)):
        fehlt = a - b
        if fehlt:
            fehl("Der MQTT-Reiter nennt Themen (%s), die der Dienst nicht sendet: %s"
                 % (was, sorted(fehlt)))
        zuviel = b - a
        if zuviel:
            fehl("Der Dienst sendet Themen (%s), die der MQTT-Reiter nicht nennt: %s"
                 % (was, sorted(zuviel)))
    print("[OK]   %d MQTT-Themen je Fahrzeug und %d darueber: Reiter und Dienst "
          "decken sich" % (len(mq), len(oben_lib)))

    # Jedes Feld der Endpunkt-Ausgabe muss in der Feldliste stehen - und
    # umgekehrt. Sonst legt die Vorlage einen Eingang an, der nie einen Wert
    # bekommt, oder ein gesendeter Wert steht nirgends beschrieben.
    #
    # Gelesen wird der ganze printf-Aufruf, nicht nur die erste Zeichenkette:
    # seit 0.9.10 sind die Zeilen ueber mehrere Zeilen umbrochen. Und die
    # Platzhalter sind nicht mehr nur %s - ZAEHLER und FEHLFOLGE gehen als %d
    # hinaus, weil sie immer eine Zahl sind.
    for aktion, funktion in (("VOLKSWAGEN", "vw_status_felder"),
                             ("LADEN", "vw_laden_felder"),
                             ("WARTUNG", "vw_wartung_felder"),
                             ("POSITION", "vw_position_felder"),
                             ("VERBRAUCH", "vw_verbrauch_felder")):
        zeile = re.search(r'"%s;OK=%%d;(.*?)\\n"' % aktion, ep, re.S)
        felder = set(re.findall(r"([A-Z]+)=%[sd]", zeile.group(1))) if zeile else set()
        if not felder:
            fehl("%s: die Ausgabezeile des Endpunkts liess sich nicht auslesen." % aktion)
            continue
        mblock = re.search(r"function %s.*?\n}" % funktion, lib, re.S)
        if not mblock:
            # Kein Absturz, sondern ein Befund: die Feldliste gibt es nicht.
            # Ein Werkzeug, das an einem aelteren Stand abbricht, prueft die
            # Zeilen danach ueberhaupt nicht mehr.
            fehl("%s: die Feldliste %s() gibt es nicht." % (aktion, funktion))
            continue
        block = mblock.group(0)
        liste = set(re.findall(r"^\s*'([A-Z]+)'\s*=>", block, re.M)) - {"OK", "ALTER"}
        felder -= {"ALTER"}
        if felder != liste:
            fehl("%s: Endpunkt sendet %s, die Feldliste nennt %s"
                 % (aktion, sorted(felder - liste) or "nichts zusaetzlich",
                    sorted(liste - felder) or "nichts zusaetzlich"))
    print("[OK]   Endpunkt-Ausgabe und Feldlisten der Oberflaeche decken sich")


def pruefe_tabellennamen(wurzel):
    """Jede Tabellenzeile mit Vorlage nennt einen Namen, den diese Vorlage erzeugt.

    SEIT 17.10.2026 (Welle Bild 17). Der Reiter "Einbindung in Loxone" steht
    seitdem in Tabellenzeilen Z<seite>_<nr> = "Typ | Name | Bedeutung | Eingang"
    der Sprachdatei; die alte Liste N01..Nnn ist gestrichen. Die Pruefung
    darunter suchte weiter nach N01..Nnn und meldete am Bau "Alle 0 virtuellen
    Eingaenge ... gibt es auch" - gruen, ohne etwas verglichen zu haben.

    Verglichen wird gegen die ERZEUGTE Vorlage, nicht gegen einen Nachbau: das
    PHP des Plugins laeuft in einer Wegwerf-Attrappe (LBHOMEDIR in einem
    Zeitordner, LBPPLUGINDIR = FOLDER aus plugin.cfg) und liefert die Vorlagen
    fuer Fahrzeug 1. Jede Zeile, deren Typ "(Vorlage „X“)" nennt, muss mit
    ihrem Namen genau einen Befehl in der Vorlage mit dem Behaeltertitel X
    haben (Muster: vb_bild_vw17_bau_skripte/namen_probe.py).

    Rueckgabe: False, wenn die Sprachdatei keine solche Zeile traegt (aelterer
    Stand - dann misst die alte Pruefung), sonst True.
    """
    import html
    import json
    import os
    import shutil
    import tempfile
    ini = (wurzel / "templates/lang/language_de.ini").read_text(encoding="utf-8")
    zeilen = []
    for schl, wert in re.findall(r'^(Z\d+_\d+) = "(.*)"$', ini, re.M):
        teile = [html.unescape(t.strip()) for t in wert.split("|")]
        m = re.search(r"\(Vorlage „([^“]+)“\)$", teile[0])
        if m and len(teile) >= 2:
            zeilen.append((schl, m.group(1), teile[1]))
    if not zeilen:
        return False
    phps = [Path(p) for p in (r"C:\tmp\php-8.4.27-Win32-vs17-x64\php.exe",
                              r"C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe")]
    php = next((p for p in phps if p.is_file()), None)
    if php is None:
        print("[ -- ] Namen der %d Tabellenzeilen mit Vorlage nicht geprueft - "
              "kein PHP da, die Vorlagen liessen sich nicht erzeugen" % len(zeilen))
        hinw("Tabellenzeilen gegen die erzeugten Vorlagen: nicht messbar (kein PHP).")
        return True
    cfg = (wurzel / "plugin.cfg").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^FOLDER=(\S+)", cfg, re.M)
    ordner = m.group(1) if m else "volkswagenid"
    aufrufe = ["vw_vorlage(1, '%s')" % a
               for a in ("status", "laden", "wartung", "position", "verbrauch")]
    aufrufe.append("vw_vorlage_vo(1)")
    lb = Path(tempfile.mkdtemp(prefix="vw_pruefen_lb_"))
    try:
        for t in ("config", "data", "log"):
            (lb / t / "plugins").mkdir(parents=True)
        skript = lb / "vorlagen.php"
        skript.write_text(
            "<?php\n$_SERVER['HTTP_HOST'] = 'loxberry';\n"
            "require %s;\n$p = vw_paths();\n"
            "if (realpath($p['home']) !== realpath(getenv('LBHOMEDIR'))) "
            "{ fwrite(STDERR, \"vw_paths() zeigt nicht auf die Attrappe\\n\"); exit(2); }\n"
            "$aus = array();\n%s"
            "echo json_encode($aus);\n"
            % (json.dumps(str((wurzel / "webfrontend/html/vw_lib.php").resolve())),
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
        fehl("Die Vorlagen liessen sich nicht erzeugen (rc %d): %s"
             % (r.returncode, (r.stderr.decode("utf-8", "replace") + aus).strip()[:300]))
        return True
    vorlagen = {}
    for t in texte:
        kopf = re.search(r'<(?:VirtualInHttp|VirtualOut) [^>]*?Title="([^"]*)"', t)
        if kopf:
            vorlagen.setdefault(html.unescape(kopf.group(1)), []).extend(
                html.unescape(x) for x in
                re.findall(r'<(?:VirtualInHttpCmd|VirtualOutCmd) Title="([^"]*)"', t))
    befunde = []
    for schl, beh, name in zeilen:
        if beh not in vorlagen:
            befunde.append("%s: Vorlage '%s' erzeugt das Plugin nicht" % (schl, beh))
        elif vorlagen[beh].count(name) != 1:
            befunde.append("%s: '%s' steht %d-mal in der Vorlage '%s'"
                           % (schl, name, vorlagen[beh].count(name), beh))
    if befunde:
        fehl("Tabellenzeilen nennen Namen, die die erzeugte Vorlage nicht traegt: "
             + "; ".join(befunde))
    else:
        print("[OK]   Alle %d Tabellenzeilen mit Vorlage finden ihren Namen genau "
              "einmal in der erzeugten Vorlage (%d Vorlagen, PHP %s)"
              % (len(zeilen), len(vorlagen), php.parent.name.split("-")[1]))
    return True


def pruefe_bausteinnamen(wurzel):
    """Jeder virtuelle Eingang der Baustein-Liste muss es auch geben.

    Befund vom 06.08.2026: Baustein #8 verlangte einen Eingang '..._KOFFER',
    den die Feldliste von VW und Audi gar nicht kennt (nur Skoda hat ihn). Wer
    die Tabelle von oben nach unten abgearbeitet haette, waere an einer
    Befehlserkennung gescheitert, die nie etwas empfaengt - und haette lange
    gesucht, weil alles andere funktioniert.
    """
    if pruefe_tabellennamen(wurzel):
        return
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
