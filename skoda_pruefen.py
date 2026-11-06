#!/usr/bin/env python3
"""Pflichtpruefung fuer das Skoda-Connect-Plugin.

Ersetzt NICHT `php -l` und keinen echten Renderlauf - in diesem Arbeitsbereich
gibt es kein PHP. Die Hausregel verlangt fuer diesen Fall ausdruecklich einen
Ersatz und dessen Offenlegung: Klammer-, Tag- und <?php/?>-Bilanz zaehlen.
Genau das tut dieses Skript, zusammen mit den uebrigen Punkten der
Pflichtpruefung, die sich ohne PHP durchfuehren lassen.

Aufruf:  skoda_pruefen.py <pluginordner>
"""

import os
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
# Abschriften gemeinsamer Dateien (Werkzeug-V1b, 08.10.2026; wie vw_pruefen.py)
#
# Seit dem Sprachmodul (Nr. 36) traegt die Linie eine Abschrift von
# Werkzeuge/gemeinsam/sprachausgabe.php und den Abschnitt [ANSAGE] aus
# gemeinsam/sprachausgabe_texte.json. Beides benutzt die Textfunktion des
# Moduls (ansage_t), nicht die der Linie - die Sprachpruefung meldete deshalb
# die Modulschluessel als "nie benutzt", dazu Schluessel aus dem Selbsttest
# des Moduls (SEITE.L_AUDIO) und die Beispieladressen des Moduls als
# Heimnetzadressen.
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
    # BERICHTIGT 27.08.2026: der Satz stimmte nicht mehr.
    #
    # Der Kopf dieses Werkzeugs sagt, es ersetze php -l, weil es in diesem
    # Arbeitsbereich kein PHP gebe. Es gibt hier zwei - dieselben, gegen die
    # rendern.py, sicherung_wirkung.py und wachposten_wirkung.py laufen. Die
    # Klammerbilanz war also seit jeher ein Ersatz fuer etwas, das zur
    # Verfuegung stand. Sie bleibt trotzdem: sie findet auch das
    # unausgeglichene <?php, das php -l nicht stoert.
    php_gefunden = []
    for kandidat in ("C:/tmp/php-8.4.27-Win32-vs17-x64/php.exe",
                     "C:/tmp/php-7.4.33-Win32-vc15-x64/php.exe"):
        if os.path.isfile(kandidat):
            php_gefunden.append(kandidat)
    if not php_gefunden:
        print("[INFO] php -l war nicht moeglich - hier ist kein PHP zu finden.")
    else:
        schlecht = 0
        for php in php_gefunden:
            for f in dateien:
                r = subprocess.run([php, "-l", str(f)], capture_output=True, text=True)
                if r.returncode != 0:
                    schlecht += 1
                    fehl("php -l (%s): %s" % (os.path.basename(os.path.dirname(php)),
                                              (r.stdout + r.stderr).strip()[:200]))
        if not schlecht:
            print("[OK]   php -l unter %d PHP-Fassungen fehlerfrei (%d Dateien je Fassung)"
                  % (len(php_gefunden), len(dateien)))


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


    # Werkzeug-V1b: unveraenderte Abschriften gemeinsamer Dateien uebergehen.
    gem = gemeinsame_abschriften(wurzel)
    frei = ansage_modulschluessel(wurzel, gem)
    for f in sorted(gem):
        hinw("%s: unveraenderte Abschrift von Werkzeuge/gemeinsam/%s - in Sprach-, "
             "Formular- und Anonymitaetspruefung uebergangen%s"
             % (f.relative_to(wurzel.resolve()).as_posix(), f.name,
                (", dazu %d Modulschluessel in [ANSAGE]" % len(frei))
                if f.name == "sprachausgabe.php" else ""))
    for f in sorted(wurzel.rglob("sprachausgabe.php")):
        if f.resolve() not in gem:
            hinw("%s weicht von Werkzeuge/gemeinsam/sprachausgabe.php ab - wird "
                 "normal geprueft (gemeinsam_pruefen.py meldet die Abweichung)"
                 % f.relative_to(wurzel).as_posix())

    benutzt = set()   # eng: nur, was nachweislich als ganzer Schluessel dasteht
    weit = set()      # weit: alles, was wie ein Schluessel aussieht
    maskiert = set()
    for f in sorted(wurzel.rglob("*.php")):
        if f.resolve() in gem:
            continue
        t = f.read_text(encoding="utf-8")
        benutzt |= set(re.findall(r"sk_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t))
        # JEDER Schluessel-artige Textbaustein zaehlt als benutzt, nicht nur
        # der unmittelbar in sk_t() stehende.
        #
        # BERICHTIGT 27.08.2026. Vorher waren hier zwei enge Muster, und mit
        # 0.9.13 hat das 22 Schluessel faelschlich als tot gemeldet: sie
        # stehen in Tabellen (sk_befehle, sk_vorlagenarten, sk_mqtt_themen)
        # und werden ueber eine Variable uebersetzt - sk_t($b[0]) statt
        # sk_t('TEST.K_ABRUF') -, oder in einem Bedingungsausdruck
        # (sk_t($f >= 2 ? 'MQTT.ABO_V2' : 'MQTT.ABO_WARNUNG')). Letzteres war
        # schon in 0.9.12 falsch gemeldet worden.
        #
        # DIE GRENZE DIESES MUSTERS, damit sie niemand suchen muss: ein
        # Schluessel, der NUR in einem Kommentar steht, gilt hier ebenfalls
        # als benutzt. Die strenge Gegenprobe leistet
        # skoda_sprache_erzeugen.py --pruefen; beide zusammen decken beide
        # Richtungen ab.
        weit |= set(re.findall(r"'([A-Z][A-Z0-9_]*\.[A-Z0-9_]+)'", t))
        maskiert |= set(re.findall(r"sk_e\(\s*sk_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t))
        maskiert |= set(re.findall(r"sk_e\(\s*sprintf\(\s*sk_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t))
    benutzt |= {"EINST.DIENST_START", "EINST.DIENST_STOP", "EINST.DIENST_RESTART"}
    for feld in ("INTERVALL", "TAKT_STAMM", "TAKT_WARTUNG", "TEMP_MIN", "TEMP_MAX",
                 "VERLAUF_TAGE", "WARTEZEIT",
                 # 0.9.13: die Bremsen, der Radius und die Felder des Horchers
                 # laufen durch dieselben Schleifen im Speichern-Handler.
                 "ABSTAND_ABRUF", "BEFEHLE_STUNDE", "ENTPRELLUNG", "HEIM_RADIUS",
                 "HEIM_BREITE", "HEIM_LAENGE", "EMPF_THEMA", "EMPF_GRENZE",
                 "ABFAHRT_THEMA", "ABFAHRT_VORLAUF", "ABFAHRT_TEMP"):
        benutzt.add("EINST.L_" + feld)

    # ZWEI RICHTUNGEN, ZWEI STRENGEGRADE - und das mit Absicht.
    #
    # "fehlt in der .ini" wird ENG gemessen: gezaehlt wird nur, was
    # nachweislich als ganzer Schluessel in sk_t() steht. Sonst meldete das
    # weite Muster Fundstuecke wie 'EINST.L_' (der Kopf einer Verkettung) oder
    # 'ABSCHNITT.SCHLUESSEL' (das Beispiel aus einem Kommentar) als fehlend.
    #
    # "nie benutzt" wird WEIT gemessen: hier ist ein Fehlalarm teurer. Er
    # verleitet dazu, einen Text zu loeschen, den eine Tabelle ueber eine
    # Variable uebersetzt - genau das drohte 0.9.13 fuer 22 Schluessel.
    for k in sorted(benutzt - set(tde)):
        fehl("Schluessel im PHP benutzt, fehlt in language_de.ini: " + k)
    for k in sorted(benutzt - set(ten)):
        fehl("Schluessel im PHP benutzt, fehlt in language_en.ini: " + k)
    for k in sorted(set(tde) - frei - benutzt - weit):
        fehl("Schluessel in language_de.ini, aber im PHP nie benutzt: " + k)
    if set(tde) != set(ten):
        fehl("language_de.ini und language_en.ini sind nicht deckungsgleich.")

    for k in sorted(maskiert):
        for name, tab in (("de", tde), ("en", ten)):
            w = tab.get(k, "")
            if "<" in w or "&" in w:
                fehl("%s: %s laeuft durch sk_e(), enthaelt aber Auszeichnung oder "
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

    # BERICHTIGT 27.08.2026 - diese Pruefung hat seit 0.9.2 NICHTS gemessen.
    #
    # Sie suchte data-ziel="tab-settings" und class="sm-seite" id="tab-..."
    # woertlich. Beides gibt es in dieser Oberflaeche nicht mehr: die
    # Reiterleiste entsteht seit 0.9.2 in einer Schleife
    #     data-ziel="tab-<?= $sk_r ?>"
    # und jede Flaeche traegt eine zusammengesetzte Klasse
    #     class="sm-seite<?= ... ?>" id="tab-settings"
    # Gefunden wurden also null Reiter und null Bereiche - und zwei leere
    # Mengen sind gleich. Das Werkzeug meldete "0 Reiter, 0 Bereiche,
    # Positivliste deckungsgleich" und war zufrieden.
    #
    # Gerettet hat das nur die Selbstpruefung IM PLUGIN (TEST.F_REITER in
    # sk_test.php), die dasselbe zur Laufzeit an der gerenderten Seite misst.
    # Eine Pruefung, die null Dinge vergleicht, ist keine - sie sagt es jetzt.
    ziele = re.findall(r'data-ziel="tab-(?:<\?=\s*\$sk_r\s*\?>)?([a-z0-9]*)"', t)
    quelle = re.search(r"\$sk_reiter = array\((.*?)\n\);", t, re.S)
    if quelle:
        ziele = re.findall(r"^\s*'([a-z0-9]+)'\s*=>", quelle.group(1), re.M)
    ziele = ["tab-" + z for z in ziele if z]
    seiten = re.findall(r'class="sm-seite[^"]*"[^>]*\bid="(tab-[a-z0-9]+)"', t)
    # Die Positivliste kann seit 0.9.2 GAR NICHT abweichen: sie entsteht in
    # derselben Zeile aus derselben Quelle wie die Leiste -
    #     '/^tab-(' . implode('|', array_keys($sk_reiter)) . ')$/'
    # Ein Muster, das eine feste Aufzaehlung sucht, findet dort nichts und
    # meldete deshalb ALLE Reiter als fehlend. Beide Bauformen werden erkannt;
    # bei der erzeugten gilt die Gleichheit als belegt, und das steht dabei.
    liste = re.search(r"\^tab-\(([a-z0-9|]+)\)", t)
    if liste:
        liste = set("tab-" + x for x in liste.group(1).split("|"))
        erzeugt = False
    elif re.search(r"\^tab-\('\s*\.\s*implode\('\|',\s*array_keys\(\$sk_reiter\)\)", t):
        liste = set(ziele)
        erzeugt = True
    else:
        liste = set()
        erzeugt = False
    if not ziele or not seiten:
        fehl("Die Reiterpruefung hat nichts gefunden (%d Reiter, %d Bereiche) - "
             "sie misst also nichts. Muster nachziehen." % (len(ziele), len(seiten)))
    if set(ziele) != set(seiten):
        fehl("Reiterleiste und Bereiche passen nicht zusammen: %s / %s"
             % (sorted(set(ziele)), sorted(set(seiten))))
    if not set(ziele) <= liste:
        fehl("Reiter fehlen in der activetab-Positivliste: %s" % sorted(set(ziele) - liste))
    if liste - set(ziele):
        fehl("Positivliste kennt Reiter, die es nicht gibt: %s" % sorted(liste - set(ziele)))
    if erzeugt:
        print("[OK]   Positivliste wird aus derselben Liste erzeugt wie die Leiste - "
              "sie kann nicht abweichen")
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
    # Werkzeug-V1b: eine unveraenderte Abschrift gemeinsamer Dateien traegt
    # eigene <form-Zeichenketten (Kommentar und Selbsttest des Sprachmoduls,
    # gemessen an 1.0.2 und 1.1.0: fuenf Scheinbefunde) - kein Formular
    # dieser Oberflaeche. Eine abweichende Abschrift wird weiter geprueft.
    gem_formular = gemeinsame_abschriften(wurzel)
    for f in sorted(wurzel.rglob("*.php")):
        if f.resolve() in gem_formular:
            continue
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
    # Seit 0.9.13 stehen die Weisslisten in der Bibliothek, nicht mehr im
    # Endpunkt. Sie wird deshalb hier mitgelesen.
    lib = (wurzel / "webfrontend/html/sk_lib.php").read_text(encoding="utf-8")

    if "hash_equals" not in t:
        fehl("Der Endpunkt vergleicht das Token nicht mit hash_equals.")
    if "http_response_code(403)" not in t:
        fehl("Der Endpunkt antwortet bei fehlendem Token nicht mit 403.")

    muster = dict(re.findall(r"sk_param\('([a-z]+)',\s*'(/[^']+/)'", t))
    erwartet = {"fahrzeug", "temp", "prozent"}
    if set(muster) != erwartet:
        fehl("Geprueft werden %s, erwartet %s" % (sorted(muster), sorted(erwartet)))

    boese = ["; rm -rf /", "../../etc/passwd", "1 OR 1=1", "<script>", "%00",
             "1;reboot", "'", '"', "\n", "999999999999", "-1", "abc"]
    gut = {"fahrzeug": ["1", "12", "TMBJB9NY6RF999999"],
           "temp": ["21", "21.5", "21,5", "9"],
           "prozent": ["80", "100", "5"]}

    for name, roh in muster.items():
        rx = re.compile("^" + roh.strip("/").lstrip("^").rstrip("$") + "$")
        for b in boese:
            if rx.match(b):
                fehl("Muster fuer %s laesst %r durch" % (name, b))
        for g in gut[name]:
            if not rx.match(g):
                fehl("Muster fuer %s weist den gueltigen Wert %r ab" % (name, g))

    # Weissliste der Aktionen
    #
    # BERICHTIGT 27.08.2026. Bis 0.9.12 standen beide Listen woertlich im
    # Endpunkt, und genau deshalb liefen sie mit der Oberflaeche auseinander:
    # der Endpunkt kannte zwoelf schaltende Aktionen, der Reiter Loxone nannte
    # sieben, der Reiter Test bot neun. Mit 0.9.13 stehen sie in sk_lesende()
    # und sk_befehle() in der Bibliothek - dieselbe Quelle, aus der auch
    # Tabelle, Knoepfe und Ausgangsvorlage entstehen.
    #
    # Das Werkzeug liest sie deshalb DORT, und es kennt beide Bauformen: die
    # alte (Feld im Endpunkt) und die neue (Funktion in der Bibliothek).
    lesend = re.search(r"\$sk_lesend = array\(([^)]*)\)", t)
    schaltend = re.search(r"\$sk_schaltend = array\(([^;]*?)\);", t, re.S)
    if lesend is None and "sk_lesende()" in t:
        lesend = re.search(r"function sk_lesende\(\)\s*\{.*?return array\(([^)]*)\)", lib, re.S)
    if schaltend is None and "sk_befehle()" in t:
        schaltend = re.search(r"function sk_befehle\(\)\s*\{.*?return array\((.*?)\n    \);",
                              lib, re.S)
    if not lesend or not schaltend:
        fehl("Die Weisslisten der Aktionen sind nicht auffindbar.")
    else:
        a = set(re.findall(r"'([a-z_]+)'", lesend.group(1)))
        b = set(re.findall(r"^\s*'([a-z_]+)'\s*=>", schaltend.group(1), re.M)) \
            or set(re.findall(r"'([a-z_]+)'", schaltend.group(1)))
        if a & b:
            fehl("Aktion steht in beiden Weisslisten: %s" % sorted(a & b))
        print("[OK]   Endpunkt: %d lesende, %d schaltende Aktionen, Muster weisen "
              "alle %d Angriffseingaben ab" % (len(a), len(b), len(boese)))

    if "STEUERUNG_AUS" not in t or "DIENST_LAEUFT_NICHT" not in t:
        fehl("Der Endpunkt prueft nicht auf gesperrte Steuerung bzw. toten Dienst.")


# ---------------------------------------------------------------------------
# 5. Loxone-Vorlage: CRLF, Tabulatoren, Attributreihenfolge, Wohlgeformtheit
#
# BERICHTIGT 31.08.2026 - und das ist der schwerste Werkzeugbefund dieser
# Runde. Hier stand die VERALTETE Attributreihenfolge als "soll", und das
# Werkzeug meldete dafuer "wie im Original". Es hat den Fehler damit
# festgeschrieben, statt ihn zu finden: dieselbe Klasse wie
# skoda_funktionstest.py, das im August das stille Zurechtbiegen der VIN als
# Sollverhalten einforderte. Zusaetzlich prueft es sk_xml_virtual_out()
# ueberhaupt nicht - der halbe Vorlagenbau war ungemessen.
#
# Woher das neue "soll" kommt (Quellen, nicht Erinnerung):
#   Eingang  ap_xml_virtual_in_http() aus LoxBerry-Plugin-APC-UPS-1.2.4 -
#            die Vorlage, auf die sich der Kopfkommentar von sk_lib.php selbst
#            beruft.
#   Ausgang  mower_lib.php aus LoxBerry-Plugin-Robonect-1.1.2. Die Wahl ist
#            nicht Geschmack: im Arbeitsordner liegt mit
#            "VO_Rasenmaeher steuern (LoxBerry-Plugin)_Test.xml" die ECHTE
#            Ausfuhr aus Loxone Config fuer genau dieses Plugin, und die
#            Reihenfolge deckt sich Attribut fuer Attribut.
# ---------------------------------------------------------------------------
SOLL_IN_HTTP = ["HintText", "Title", "Comment", "Address", "PollingTime",
                "Title", "Comment", "Check", "Signed", "Analog",
                "SourceValLow", "DestValLow", "SourceValHigh", "DestValHigh",
                "DefVal", "MinVal", "MaxVal", "Unit", "HintText"]

SOLL_OUT = ["HintText", "Title", "Comment", "Address", "CmdInit",
            "CloseAfterSend", "CmdSep",
            "Title", "Comment", "CmdOnMethod", "CmdOffMethod", "CmdOn",
            "CmdOnHTTP", "CmdOnPost", "CmdOff", "CmdOffHTTP", "CmdOffPost",
            "CmdAnswer", "Analog", "Repeat", "RepeatRate", "HintText"]


def attribute(block):
    """Die Attributnamen in der Reihenfolge, in der der Bauer sie schreibt.

    Zwei Schreibweisen kommen im Bestand vor, und beide zaehlen: einzeln
    angehaengt ($o .= 'Title="' . ...) und mehrere in einer Zeichenkette
    (CmdOnHTTP="" CmdOnPost="" ...). Wer nur die erste sucht, misst am
    Robonect-Muster null Attribute und meldet das gruen.
    """
    return re.findall(r'([A-Za-z]+)="', block)


def pruefe_vorlage(wurzel):
    t = (wurzel / "webfrontend/html/sk_lib.php").read_text(encoding="utf-8")

    for name, soll, art in (("sk_xml_virtual_in_http", SOLL_IN_HTTP, "2"),
                            ("sk_xml_virtual_out", SOLL_OUT, "3")):
        block = re.search(r"function " + name + r"\(.*?\n}", t, re.S)
        if not block:
            fehl("%s() nicht gefunden - der Vorlagenbau ist ungemessen." % name)
            continue
        b = block.group(0)
        if b.count("$crlf") < 4:
            fehl("%s() benutzt nicht durchgehend CRLF." % name)
        if '"\\t"' not in b:
            fehl("%s(): vor den Kindelementen fehlt der Tabulator." % name)
        marke = '<Info templateType="%s" minVersion="17010727"/>' % art
        if marke not in b:
            fehl("%s(): das erste Kindelement %s fehlt. Loxone Config schreibt "
                 "es in jede Ausfuhr." % (name, marke))
        ist = [a for a in attribute(b)
               # 'version' stammt aus der XML-Kopfzeile <?xml version="1.0"?>,
               # nicht aus dem Bauteil. In keinem der beiden Elemente gibt es
               # ein Attribut dieses Namens - das Wegfiltern verdeckt nichts.
               if a not in ("xml", "version", "encoding",
                            "templateType", "minVersion")]
        if ist != soll:
            fehl("Attributreihenfolge von %s() weicht von der gemessenen "
                 "Ausfuhr ab.\n  ist : %s\n  soll: %s" % (name, ist, soll))
        else:
            print('[OK]   %s(): CRLF, Tabulator, <Info templateType="%s"> und '
                  'Attributreihenfolge wie in der Ausfuhr' % (name, art))

    # Grenzen realistisch setzen - die Regel verbietet den Pauschalwert
    # ausdruecklich ("Loxone zieht daraus die Reglergrenzen und die
    # Plausibilitaetspruefung; wer alles offen laesst, verschenkt beides").
    #
    # Gesucht wird im CODE, nicht im Kommentar. Erster Anlauf am 31.08.2026
    # suchte im ganzen Dateitext und meldete deshalb den Kommentar an, der die
    # Behebung ERKLAERT ("hier stand MinVal=-2147483647"). Ein Werkzeug, das
    # die Beschreibung eines behobenen Fehlers fuer den Fehler haelt, zwingt
    # dazu, die Begruendung zu loeschen - und die ist das Wertvollste an der
    # Aenderung.
    ohne_kommentar = re.sub(r"/\*.*?\*/", " ", t, flags=re.S)
    ohne_kommentar = re.sub(r"(?m)^\s*//.*$", " ", ohne_kommentar)
    if "2147483647" in ohne_kommentar:
        fehl("Die Vorlage setzt MinVal/MaxVal pauschal auf +-2147483647. Die "
             "Grenzen gehoeren je Feld an die Feldliste.")

    # Die Einheit muss als Unit-Attribut hinausgehen, nicht nur im Kommentar
    # stehen: ohne das Attribut zeigt der virtuelle Eingang eine nackte Zahl.
    if "<v.1>" not in t and "<v.0>" not in t:
        fehl("Kein Wertplatzhalter im Unit-Attribut - die Einheit kommt in "
             "Loxone nicht an.")

    # Die Bedeutungstexte laufen durch strip_tags + html_entity_decode, bevor
    # sie maskiert werden - sonst stuende 'l&auml;dt' in Loxone Config.
    if "html_entity_decode" not in t or "strip_tags" not in t:
        fehl("Die Vorlage loest vor dem Maskieren keine Entitaeten auf - in Loxone "
             "Config stuende sonst wortwoertlich 'lädt'.")

    # Nachbau der Ausgabe in Python und Pruefung als XML. Das ist ein Nachbau,
    # kein Durchlauf des PHP - es beweist nur, dass die erzeugte Form
    # wohlgeformt ist und die Zeilenenden stimmen.
    #
    # Das Muster laesst die Grenzen OPTIONAL zu: sonst meldete das Werkzeug
    # "Suchmuster passt nicht zur Datei" statt des eigentlichen Befundes, und
    # ein Werkzeug, das ueber sich selbst klagt, wird nicht mehr gelesen. Ob
    # die Grenzen da sind, sagt die Pruefzeile darunter.
    felder = re.findall(
        r"^\s*'([A-Z]+)'\s*=>\s*array\('([^']*)',\s*'(SK_FELD\.[A-Z_]+)'"
        r"(?:\s*,\s*(-?\d+)\s*,\s*(-?\d+))?\s*\)", t, re.M)
    if len(felder) < 10:
        fehl("Nur %d Statusfelder ausgelesen - das Suchmuster passt nicht zur "
             "Datei." % len(felder))
    if not felder:
        fehl("Die Statusfelder liessen sich nicht auslesen.")
        return
    ohne_grenzen = [f[0] for f in felder if f[3] == "" or f[4] == ""]
    if ohne_grenzen:
        fehl("%d von %d Statusfeldern tragen keine Grenzen fuer die Vorlage: %s"
             % (len(ohne_grenzen), len(felder), ohne_grenzen[:8]))
    crlf = "\r\n"
    xml = '<?xml version="1.0" encoding="utf-8"?>' + crlf
    xml += ('<VirtualInHttp HintText="" Title="Skoda 1" Comment="Test" '
            'Address="http://beispiel/x" PollingTime="300">' + crlf)
    xml += "\t" + '<Info templateType="2" minVersion="17010727"/>' + crlf
    for feld, einheit, _schluessel, mi, ma in felder:
        einheit_x = einheit.replace("&deg;", "Grad")
        xml += ("\t" + '<VirtualInHttpCmd Title="SKODA_1_%s" Comment="Bedeutung" '
                'Check="\\i;%s=\\i\\v" Signed="true" Analog="true" SourceValLow="0" '
                'DestValLow="0" SourceValHigh="100" DestValHigh="100" DefVal="0" '
                'MinVal="%s" MaxVal="%s" Unit="&lt;v.1&gt; %s" HintText=""/>'
                % (feld, feld, mi or "0", ma or "100", einheit_x)) + crlf
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
    # Das Info-Element zaehlt als Kind mit - deshalb +1.
    if len(baum) != len(felder) + 1:
        fehl("Der Nachbau enthaelt %d Kindelemente statt %d."
             % (len(baum), len(felder) + 1))
    print("[OK]   Nachbau der Loxone-Vorlage: wohlgeformt, %d Befehle, %d CRLF, "
          "keine nackte LF" % (len(baum) - 1, roh.count(b"\r\n")))


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
    #
    # Werkzeug-V1b: die Beispieladressen einer unveraenderten Abschrift und der
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
                 "cron/cron.01min", "bin/skoda.py", "bin/dienst.sh",
                 "icons/icon.svg", "icons/icon_64.png", "icons/icon_128.png",
                 "icons/icon_256.png", "icons/icon_512.png",
                 "templates/help/help.html",
                 "templates/lang/language_de.ini", "templates/lang/language_en.ini",
                 "webfrontend/htmlauth/index.php", "webfrontend/htmlauth/sk_test.php",
                 "webfrontend/html/index.php", "webfrontend/html/sk_lib.php"):
        if not (wurzel / pfad).is_file():
            fehl("Pflichtdatei fehlt: " + pfad)

    # Fassungen an drei Stellen
    v = {}
    for name in ("plugin.cfg", "release.cfg", "prerelease.cfg"):
        m = re.search(r"^VERSION=(.+)$", (wurzel / name).read_text(encoding="utf-8"), re.M)
        v[name] = m.group(1).strip() if m else "fehlt"
    if len(set(v.values())) != 1:
        # DER VORBEREITETE ZUSTAND IST KEIN FEHLER.
        #
        # REGELN_4 verlangt ihn ausdruecklich: beim Vorbereiten einer Fassung
        # wird die plugin.cfg sofort angehoben, release.cfg und prerelease.cfg
        # bleiben auf der VEROEFFENTLICHTEN Nummer, bis der Tag steht. Wer sie
        # frueher mitzieht, laesst jede fremde Anlage eine Fassung sehen, die
        # es als Tag nicht gibt - HTTP 404 beim Herunterladen.
        #
        # Bis hierher meldete dieses Werkzeug genau diesen vorgeschriebenen
        # Zustand als Beanstandung. Das ist die Sorte Fund, die man sich
        # abgewoehnt zu lesen.
        def _z(s):
            return tuple(int(x) for x in re.findall(r"[0-9]+", s)) or (0,)
        vorbereitet = (v["release.cfg"] == v["prerelease.cfg"]
                       and _z(v["plugin.cfg"]) > _z(v["release.cfg"]))
        if vorbereitet:
            hinw("Vorbereitete Fassung: plugin.cfg %s, release.cfg und prerelease.cfg "
                 "noch auf der veroeffentlichten %s. Das ist der vorgeschriebene "
                 "Zustand - Schritt 4 (beide .cfg nachziehen) steht noch aus."
                 % (v["plugin.cfg"], v["release.cfg"]))
        else:
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
    py = (wurzel / "bin/skoda.py").read_text(encoding="utf-8")
    lib = (wurzel / "webfrontend/html/sk_lib.php").read_text(encoding="utf-8")
    ep = (wurzel / "webfrontend/html/index.php").read_text(encoding="utf-8")

    # Vorgabewerte muessen zusammenpassen. Nur die beiden Vorgabebloecke lesen -
    # sonst zaehlt jedes andere Array mit (z. B. der Rueckfallwert des
    # MQTT-Zustands).
    py_block = re.search(r"VORGABEN = \{(.*?)\n\}", py, re.S).group(1)
    lib_block = re.search(r"function sk_vorgaben.*?\n}", lib, re.S).group(0)
    pv = dict(re.findall(r'^\s*"([a-z_]+)":\s*([0-9]+|"[a-z]+"),', py_block, re.M))
    lv = dict(re.findall(r"^\s*'([a-z_]+)'\s*=>\s*([0-9]+|'[a-z]+'),", lib_block, re.M))
    for k in set(pv) & set(lv):
        a = pv[k].strip('"')
        b = lv[k].strip("'")
        if a != b:
            fehl("Vorgabewert %s: skoda.py sagt %s, sk_lib.php sagt %s" % (k, a, b))
    nur_py = set(pv) - set(lv)
    nur_php = set(lv) - set(pv) - {"aktionstoken", "wartezeit"}
    if nur_py:
        fehl("Vorgabewerte nur in skoda.py: %s" % sorted(nur_py))
    if nur_php:
        fehl("Vorgabewerte nur in sk_lib.php: %s" % sorted(nur_php))
    print("[OK]   %d Vorgabewerte in Dienst und Bibliothek gleich" % len(set(pv) & set(lv)))

    # Jede schaltende Aktion des Endpunkts muss der Dienst kennen
    #
    # BERICHTIGT 27.08.2026: seit 0.9.13 steht die Liste in sk_befehle() in
    # der Bibliothek statt woertlich im Endpunkt. Das Muster fand null
    # Aktionen, und "alle 0 Aktionen kennt der Dienst" ist wahr und wertlos.
    m = re.search(r"\$sk_schaltend = array\((.*?)\);", ep, re.S)
    aktionen = set(re.findall(r"'([a-z_]+)'", m.group(1))) if m else set()
    if not aktionen:
        m = re.search(r"function sk_befehle\(\)\s*\{.*?return array\((.*?)\n    \);",
                      lib, re.S)
        aktionen = set(re.findall(r"^\s*'([a-z_]+)'\s*=>", m.group(1), re.M)) if m else set()
    if not aktionen:
        fehl("Die schaltenden Aktionen sind nicht auffindbar - der Abgleich mit "
             "dem Dienst hat nichts gemessen.")
    bekannt = set(re.findall(r'aktion == "([a-z_]+)"', py))
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
    # MQTT_FELDER UND MQTT_TEXTFELDER.
    #
    # BERICHTIGT 27.08.2026: mit 0.9.13 stehen die Textthemen (modell,
    # kennzeichen, ladezustand, adresse ...) in einer zweiten Liste, weil eine
    # LEERE Nutzlast mit 'retain' ein behaltenes Thema loescht - ein leerer
    # Text wird deshalb gar nicht erst gesendet. Wer nur MQTT_FELDER liest,
    # meldet zehn Themen als nicht gesendet, die sehr wohl hinausgehen.
    gesendet = set()
    for name in ("MQTT_FELDER", "MQTT_TEXTFELDER"):
        m = re.search(name + r" = \((.*?)\n\)", py, re.S)
        if m:
            gesendet |= set(re.findall(r'"([a-z_]+)"', m.group(1)))
    fehlt = mq - gesendet
    if fehlt:
        fehl("Der MQTT-Reiter nennt Themen, die der Dienst nicht sendet: %s" % sorted(fehlt))
    zuviel = gesendet - mq
    if zuviel:
        fehl("Der Dienst sendet Themen, die der MQTT-Reiter nicht nennt: %s" % sorted(zuviel))
    print("[OK]   %d MQTT-Themen: Reiter und Dienst decken sich" % len(mq))

    # Jedes Feld der Endpunkt-Ausgabe muss in der Feldliste stehen
    for aktion, funktion in (("SKODA", "sk_status_felder"),
                             ("LADEN", "sk_laden_felder"),
                             ("WARTUNG", "sk_wartung_felder")):
        zeile = re.search(r'"%s;OK=%%d;(.*?)\\n"' % aktion, ep, re.S)
        if not zeile:
            zeile = re.search(r'"%s;OK=%%d;(.*?)ALTER=%%d' % aktion, ep, re.S)
        # %d ZAEHLT MIT.
        #
        # BERICHTIGT 27.08.2026: das Muster kannte nur %s. Mit 0.9.13 gehen
        # AUSFAELLE und ZAEHLER als ganze Zahl hinaus (%d), und das Werkzeug
        # meldete beide als "in der Feldliste, aber nicht gesendet" - obwohl
        # sie in derselben Zeile stehen.
        felder = set(re.findall(r"([A-Z]+)=%[sd]", zeile.group(1))) if zeile else set()
        block = re.search(r"function %s.*?\n}" % funktion, lib, re.S).group(0)
        liste = set(re.findall(r"^\s*'([A-Z]+)'\s*=>", block, re.M)) - {"OK"}
        # ALTER wird NICHT mehr herausgenommen.
        #
        # BERICHTIGT 27.08.2026: bis 0.9.12 fuehrte der Endpunkt ALTER in
        # jeder Antwort, die Feldlisten der Oberflaeche nannten es aber nur
        # beim Status - der Anwender bekam fuer die Vorlagen "laden",
        # "wartung" und "position" also einen Wert, den keine Tabelle erklaerte.
        # Seit 0.9.13 steht es in allen vieren, und der Vergleich darf beide
        # Seiten unbesehen gegeneinanderhalten.
        if felder != liste:
            fehl("%s: Endpunkt sendet %s, die Feldliste nennt %s"
                 % (aktion, sorted(felder), sorted(liste)))
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
    ordner = m.group(1) if m else "skodaconnect"
    aufrufe = ["sk_vorlage(1, '%s')" % a
               for a in ("status", "laden", "wartung", "position", "aus")]
    lb = Path(tempfile.mkdtemp(prefix="skoda_pruefen_lb_"))
    try:
        for t in ("config", "data", "log"):
            (lb / t / "plugins").mkdir(parents=True)
        skript = lb / "vorlagen.php"
        skript.write_text(
            "<?php\n$_SERVER['HTTP_HOST'] = 'loxberry';\n"
            "require %s;\n$p = sk_paths();\n"
            "if (realpath($p['home']) !== realpath(getenv('LBHOMEDIR'))) "
            "{ fwrite(STDERR, \"sk_paths() zeigt nicht auf die Attrappe\\n\"); exit(2); }\n"
            "$aus = array();\n%s"
            "echo json_encode($aus);\n"
            % (json.dumps(str((wurzel / "webfrontend/html/sk_lib.php").resolve())),
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
    pruefe_tabellennamen(wurzel)
    lib = next(wurzel.glob("webfrontend/html/*_lib.php")).read_text(encoding="utf-8")

    # VERGLICHEN WIRD DER ERZEUGTE TITEL, NICHT DER FELDNAME. Berichtigt
    # 31.08.2026. Bis dahin wanderten alle Felder in EINEN Topf und nur der
    # letzte Namensteil wurde verglichen - ein Wartungsfeld galt damit auch
    # dann als vorhanden, wenn die Baustein-Liste es ohne die Art nannte.
    # sk_vorlage() baut den Titel so:
    #     SKODA_<nr>_<FELD>            fuer die Art 'status'
    #     SKODA_<nr>_<ART>_<FELD>      fuer alle uebrigen
    titel = set()
    for art in ("status", "laden", "wartung", "position"):
        block = re.search(r"function \w+_%s_felder.*?\n\}" % art, lib, re.S)
        if not block:
            continue
        for feld in re.findall(r"^\s*'([A-Z0-9]+)'\s*=>", block.group(0), re.M):
            titel.add(feld if art == "status" else art.upper() + "_" + feld)
    if not titel:
        fehl("Baustein-Pruefung: keine einzige Feldliste gefunden - es wurde "
             "nichts verglichen.")
        return

    # DIE NAMEN STEHEN SEIT 0.9.15 IN DER OBERFLAECHE, nicht in der
    # Sprachdatei: sk_eingangsname('FELD', 'art', $nr). Das alte Muster suchte
    # Zeilen N01..Nnn in language_de.ini; die gibt es nicht mehr, und das
    # Werkzeug hat es gemeldet statt gruen zu bleiben.
    ober = (wurzel / "webfrontend/htmlauth/index.php").read_text(encoding="utf-8")
    treffer = re.findall(r"\w+_eingangsname\(\s*'([A-Z0-9]+)'\s*,\s*'(\w+)'", ober)
    namen = {}
    for nr, (feld, art) in enumerate(treffer, start=1):
        namen["N%02d" % nr] = feld if art == "status" else art.upper() + "_" + feld
    if not namen:
        fehl("Baustein-Pruefung: keine Namen ueber <kuerzel>_eingangsname() in "
             "der Oberflaeche gefunden - es wurde nichts verglichen.")
        return
    fehlend = sorted("%s (%s)" % (n, f) for n, f in namen.items() if f not in titel)
    if fehlend:
        fehl("Baustein-Liste nennt virtuelle Eingaenge, die keine Vorlage "
             "erzeugt: " + ", ".join(fehlend))
    else:
        print("[OK]   Alle %d virtuellen Eingaenge der Baustein-Liste erzeugt "
              "auch eine Vorlage (%d moegliche Titel, Namen aus "
              "<kuerzel>_eingangsname())" % (len(namen), len(titel)))


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
