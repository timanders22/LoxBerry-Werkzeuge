#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sprachplatzhalter_pruefen.py - zaehlt nach, ob Text und Aufrufstelle
dieselbe Zahl von Platzhaltern meinen.

WOZU
Ein sm_t('X.Y')-Text, der in sprintf() landet, muss genau so viele
Umwandlungen (%s, %d, %1$s ...) enthalten, wie die Aufrufstelle Argumente
mitgibt. Steht dort eine zu wenig, gibt PHP 8 einen ArgumentCountError -
die Seite bricht ab. Steht eine zu viel, verschluckt PHP das Argument
stillschweigend. Beides faellt beim Uebersetzen leicht auf den Boden,
weil DE und EN unabhaengig voneinander getippt werden.

Das Werkzeug liest DIE AUFRUFSTELLE, nicht eine gepflegte Liste. Eine
Liste waere eine zweite Wahrheit.

WAS ES NICHT KANN
- Es versteht nur sprintf(sm_t('K'), ...) und printf(sm_t('K'), ...) in
  genau dieser Schreibweise. sm_t() in einer Variablen, die spaeter an
  sprintf geht, sieht es nicht. Solche Stellen meldet es unter
  "ungeprueft", damit die Zahl nicht als Vollstaendigkeit missdeutet wird.
- Es prueft nicht, ob %s statt %d richtig ist - nur die Anzahl.

AUFRUF
    python sprachplatzhalter_pruefen.py <Plugin-Ordner>
Rueckgabe 0 = kein Widerspruch, 1 = Widerspruch, 2 = Aufrufproblem.
"""

import os
import re
import sys

# ERGAENZT 26.08.2026, Anlass Ultraschall 1.2.0.
#
# Hier stand "sm_t" fest - das Kuerzel der Linie, aus der dieses
# Werkzeug stammt. In jeder anderen Linie fand es damit NULL
# Aufrufstellen und meldete daraufhin jeden Schluessel mit einem
# Platzhalter als "wird nirgends durch sprintf gereicht". Gemessen an
# Ultraschall: 14 Widersprueche in 1.1.11, 16 in 1.1.12, 52 in 1.2.0 -
# kein einziger davon war einer.
#
# Das Kuerzel wird deshalb abgeleitet. Es ist eine NICHT fangende
# Gruppe: die beiden Gruppennummern unten haengen daran, und eine
# zusaetzliche haette den Schluessel auf group(3) geschoben.
AUFRUF = re.compile(r"\b(s?printf)\s*\(\s*(?:[a-z][a-z0-9_]{0,5})_t\s*\(\s*'([A-Za-z0-9_.]+)'\s*\)")
# Ein MANTEL um <kuerzel>_t(): eine Funktion mit genau einem Parameter, die
# diesen Parameter an ein _t() weiterreicht. Beispiel aus der Fensterbilanz:
#     function fb_klartext($schluessel)
#     { return trim(strip_tags(html_entity_decode(fb_t($schluessel), ...))); }
# Solche Maentel werden GEMESSEN statt aufgezaehlt - eine Namensliste im
# Werkzeug waere eine zweite Stelle, die niemand pflegt.
MANTEL = re.compile(
    r"function\s+([a-z][a-z0-9_]*)\s*\(\s*(\$[A-Za-z_][A-Za-z0-9_]*)\s*\)"
    r"\s*\{(?:[^{}]|\{[^{}]*\})*?\b[a-z][a-z0-9_]{0,5}_t\s*\(\s*\2\s*[,)]")
# Jeder Aufruf von <kuerzel>_t('X.Y'), gleich an welcher Stelle.
# Hier stand einmal "sm_t" fest verdrahtet, und benutzt wurde das Muster
# ueberhaupt nicht - beides ist berichtigt.
NUR_T = re.compile(r"\b[a-z][a-z0-9_]{0,5}_t\s*\(\s*'([A-Za-z0-9_.]+)'\s*\)")


def maentel_sammeln(dateien):
    """Alle Mantelnamen des Pluginordners, ueber ALLE Dateien gesucht.

    Je Datei zu suchen geht nicht auf: der Mantel steht in der Bibliothek,
    gerufen wird er in der Oberflaeche und im Testmodul.
    """
    namen = set()
    for pfad in dateien:
        try:
            with open(pfad, encoding='utf-8', errors='replace') as f:
                namen.update(m[0] for m in MANTEL.findall(f.read()))
        except OSError:
            continue
    return sorted(namen)


def muster_mit_maenteln(namen):
    """AUFRUF und NUR_T, erweitert um die gemessenen Maentel.

    Rueckgabe: (AUFRUF-Muster, NUR_T-Muster). Ohne Mantel sind es genau die
    beiden Muster oben - dann aendert sich an keiner Linie etwas.
    """
    if not namen:
        return AUFRUF, NUR_T
    zweig = '|'.join([re.escape(n) for n in namen] + [r'[a-z][a-z0-9_]{0,5}_t'])
    return (re.compile(r"\b(s?printf)\s*\(\s*(?:" + zweig +
                       r")\s*\(\s*'([A-Za-z0-9_.]+)'\s*\)"),
            re.compile(r"\b(?:" + zweig + r")\s*\(\s*'([A-Za-z0-9_.]+)'\s*\)"))
# Jede einfach angefuehrte Zeichenkette, die wie ein Sprachschluessel
# aussieht. Ob sie einer IST, entscheidet der Abgleich gegen die
# Sprachdateien - nicht dieses Muster.
LITERAL = re.compile(r"'([A-Za-z0-9_]+\.[A-Za-z0-9_]+)'")
# Jeder sprintf/printf-Aufruf, auch ohne _t als erstes Argument.
JEDES_SPRINTF = re.compile(r"\b(?:s?printf)\s*\(")
# %% ist ein ausgeschriebenes Prozentzeichen und verbraucht kein Argument.
UMWANDLUNG = re.compile(r"%(?:(\d+)\$)?[-+ 0#']*[0-9]*(?:\.[0-9]+)?[bcdeEfFgGosuxX]")


def argumente_zaehlen(text, ab):
    """Zaehlt die Argumente eines Aufrufs ab der offenen Klammer.

    Zaehlt Klammern und Anfuehrungszeichen mit, damit ein Komma INNERHALB
    eines verschachtelten Aufrufs oder einer Zeichenkette nicht als
    Argumenttrenner durchgeht - genau daran scheitert eine Zaehlung mit
    text.split(',').
    """
    tiefe = 0
    kommas = 0
    i = ab
    hoch = None
    while i < len(text):
        z = text[i]
        if hoch is not None:
            if z == '\\':
                i += 2
                continue
            if z == hoch:
                hoch = None
        elif z in ("'", '"'):
            hoch = z
        elif z in '([{':
            tiefe += 1
        elif z in ')]}':
            tiefe -= 1
            if tiefe == 0:
                return kommas, i
        elif z == ',' and tiefe == 1:
            kommas += 1
        i += 1
    return None, len(text)


def texte_lesen(pfad):
    werte = {}
    abschnitt = None
    with open(pfad, encoding='utf-8') as f:
        for zeile in f:
            s = zeile.strip()
            if s.startswith(';') or not s:
                continue
            if s.startswith('[') and s.endswith(']'):
                abschnitt = s[1:-1]
            elif '=' in s and abschnitt:
                k, v = s.split('=', 1)
                v = v.strip()
                if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
                    v = v[1:-1]
                werte[abschnitt + '.' + k.strip()] = v
    return werte


def umwandlungen_zaehlen(text):
    """Zahl der VERBRAUCHTEN Argumente.

    Bei nummerierten Platzhaltern (%1$s) ist das die hoechste Nummer, nicht
    die Zahl der Vorkommen - %1$s ... %1$s braucht ein Argument, nicht zwei.
    """
    ohne = text.replace('%%', '')
    treffer = UMWANDLUNG.findall(ohne)
    if not treffer:
        return 0
    # Gezaehlt wird wie PHP zaehlt: ein nummerierter Platzhalter (%3$s)
    # greift auf die genannte Stelle zu und ruecht den laufenden Zaehler
    # NICHT weiter; ein laufender nimmt die naechste freie Stelle. Gebraucht
    # werden so viele Argumente, wie die hoechste angesprochene Stelle sagt.
    #
    # Bis 05.09.2026 fiel der GEMISCHTE Fall durch: "%d %s %s %3$s %3$s"
    # ergab 5 statt 3, weil nur "alle nummeriert" gesondert behandelt war.
    # Gemessen an Beschattung Fensterbilanz (FEHLER.RAUM_GEAENDERT) unter
    # PHP 7.4.33 und 8.4.24: drei Argumente sind richtig.
    lauf = 0
    hoechste = 0
    for t in treffer:
        if t:
            hoechste = max(hoechste, int(t))
        else:
            lauf += 1
            hoechste = max(hoechste, lauf)
    return hoechste


# ERGAENZT 08.10.2026 (Werkzeug-V1c), wie vw/au/skoda/ww_pruefen.py (V1, V1b).
#
# Seit dem Sprachmodul (Nr. 36) traegt eine Linie eine Abschrift von
# Werkzeuge/gemeinsam/sprachausgabe.php und dessen Abschnitt [ANSAGE] aus
# gemeinsam/sprachausgabe_texte.json. Das Modul formatiert seine Texte selbst:
# ansage_t('K_...', $k) mit einer Kennung OHNE Abschnitt, oft zusammengesetzt
# ('K_' . $id) - dieses Werkzeug sieht davon nichts und meldete jeden
# Modulschluessel mit Platzhalter als "nirgends durch sprintf gereicht"
# (gemessen an der Skoda-Probe mit Stammfassung: 70 von 72 Widerspruechen).
#
# Uebergangen wird NUR, was zur Stammfassung gehoert: eine byte-gleiche
# Abschrift wird nicht durchsucht, und ein Schluessel ANSAGE.<k> faellt aus
# der Gegenrichtung, wenn sein Wert in language_de.ini UND language_en.ini
# gleich dem der Stammfassung ist. Eine aeltere oder veraenderte Abschrift,
# ein abweichender Wert oder ein eigener Schluessel der Linie bleiben wie
# bisher geprueft.
def _stamm():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gemeinsam')


def gemeinsame_abschriften(wurzel):
    """Dateien (realpath) der Linie, die byte-gleich mit einer Stammfassung sind."""
    stamm = _stamm()
    aus = set()
    if not os.path.isdir(stamm):
        return aus
    vorlagen = {}
    for name in os.listdir(stamm):
        p = os.path.join(stamm, name)
        if os.path.isfile(p):
            with open(p, 'rb') as f:
                vorlagen.setdefault(name, []).append(f.read())
    for tief, _, dateien in os.walk(wurzel):
        for name in dateien:
            if name in vorlagen:
                p = os.path.join(tief, name)
                try:
                    with open(p, 'rb') as f:
                        if f.read() in vorlagen[name]:
                            aus.add(os.path.realpath(p))
                except OSError:
                    pass
    return aus


def ansage_modulschluessel(sprachen, gem):
    """'ANSAGE.<k>' je Modulschluessel mit dem Wert der Stammfassung in DE und EN;
    leer, wenn sprachausgabe.php nicht unveraendert dasteht."""
    if not any(os.path.basename(p) == 'sprachausgabe.php' for p in gem):
        return set()
    quelle = os.path.join(_stamm(), 'sprachausgabe_texte.json')
    de, en = sprachen.get('language_de.ini'), sprachen.get('language_en.ini')
    if not os.path.isfile(quelle) or de is None or en is None:
        return set()
    import json
    with open(quelle, 'rb') as f:
        soll = json.loads(f.read().decode('utf-8'))
    aus = set()
    for k, w in soll.get('de', {}).items():
        voll = 'ANSAGE.' + k
        if de.get(voll) == w and voll in en and en[voll] == soll.get('en', {}).get(k):
            aus.add(voll)
    return aus


def main():
    if len(sys.argv) != 2:
        sys.stderr.write(__doc__.strip() + '\n')
        return 2
    wurzel = sys.argv[1]
    langdir = os.path.join(wurzel, 'templates', 'lang')
    if not os.path.isdir(langdir):
        sys.stderr.write('Kein Ordner templates/lang unter %s\n' % wurzel)
        return 2

    sprachen = {}
    for name in sorted(os.listdir(langdir)):
        if name.startswith('language_') and name.endswith('.ini'):
            sprachen[name] = texte_lesen(os.path.join(langdir, name))
    if not sprachen:
        sys.stderr.write('Keine language_*.ini gefunden.\n')
        return 2
    # Werkzeug-V1c: unveraenderte Abschriften und ihre Modulschluessel.
    gem = gemeinsame_abschriften(wurzel)
    frei = ansage_modulschluessel(sprachen, gem)

    bedarf = {}      # Schluessel -> {Zahl: [Fundstellen]}
    ungeprueft = []  # _t ohne erkennbaren sprintf-Zusammenhang
    # Schluessel, die IRGENDWO innerhalb eines sprintf-Aufrufs stehen, aber
    # nicht als dessen erstes Argument in der woertlichen Gestalt. Ihre
    # Argumentzahl ist nicht zu ermitteln - aber "wird nicht gereicht" waere
    # falsch. Anlass: Kodi NG 1.2.2, zwei Schluessel hinter einem
    # Bedingungsausdruck.
    mittelbar = {}
    # Erst die Maentel messen - ueber den GANZEN Ordner, weil der Mantel in
    # der Bibliothek steht und in der Oberflaeche gerufen wird. Findet sich
    # keiner, bleiben die Muster genau die urspruenglichen.
    alle_php = []
    for tief, _, dateien in os.walk(wurzel):
        for name in sorted(dateien):
            if name.endswith('.php'):
                alle_php.append(os.path.join(tief, name))
    maentel = maentel_sammeln(alle_php)
    m_aufruf, m_nur_t = muster_mit_maenteln(maentel)
    if maentel:
        print('Maentel um <kuerzel>_t: %s' % ', '.join(maentel))
    for tief, _, dateien in os.walk(wurzel):
        for name in sorted(dateien):
            if not name.endswith('.php'):
                continue
            pfad = os.path.join(tief, name)
            if os.path.realpath(pfad) in gem:
                continue
            with open(pfad, encoding='utf-8', errors='replace') as f:
                inhalt = f.read()
            kurz = os.path.relpath(pfad, wurzel).replace('\\', '/')
            gesehen = set()
            for m in m_aufruf.finditer(inhalt):
                klammer = inhalt.index('(', m.start())
                anzahl, ende = argumente_zaehlen(inhalt, klammer)
                zeile = inhalt.count('\n', 0, m.start()) + 1
                gesehen.add((m.start(), ende))
                if anzahl is None:
                    ungeprueft.append('%s:%d %s (Klammer nicht geschlossen)'
                                      % (kurz, zeile, m.group(2)))
                    continue
                bedarf.setdefault(m.group(2), {}).setdefault(
                    anzahl, []).append('%s:%d' % (kurz, zeile))

            # Zweiter Durchgang: alle sprintf-Aufrufe, und darin jedes _t.
            for m in JEDES_SPRINTF.finditer(inhalt):
                klammer = inhalt.index('(', m.start())
                _, ende = argumente_zaehlen(inhalt, klammer)
                if ende is None:
                    continue
                zeile = inhalt.count('\n', 0, m.start()) + 1
                block = inhalt[klammer:ende]
                for t in m_nur_t.finditer(block):
                    mittelbar.setdefault(t.group(1), []).append(
                        '%s:%d' % (kurz, zeile))
                # Und jede Zeichenkette in diesem Aufruf, die WIRKLICH ein
                # Schluessel einer Sprachdatei ist. Damit faellt auch der
                # Fall "hinter einem Bedingungsausdruck" hierher statt in
                # die Gegenrichtung - egal, ob ein Mantel dazwischenliegt.
                for t in LITERAL.finditer(block):
                    if any(t.group(1) in w for w in sprachen.values()):
                        mittelbar.setdefault(t.group(1), []).append(
                            '%s:%d' % (kurz, zeile))

    fehler = []
    for schluessel in sorted(bedarf):
        zahlen = bedarf[schluessel]
        if len(zahlen) > 1:
            fehler.append('%s: die Aufrufstellen sind sich uneins - %s'
                          % (schluessel, '; '.join(
                              '%d Argument(e) bei %s' % (z, ', '.join(o))
                              for z, o in sorted(zahlen.items()))))
            continue
        soll = list(zahlen)[0]
        for datei, werte in sorted(sprachen.items()):
            if schluessel not in werte:
                fehler.append('%s: fehlt in %s' % (schluessel, datei))
                continue
            ist = umwandlungen_zaehlen(werte[schluessel])
            if ist != soll:
                fehler.append(
                    '%s: %s hat %d Platzhalter, die Aufrufstelle gibt %d '
                    'Argument(e) (%s)'
                    % (schluessel, datei, ist, soll,
                       ', '.join(zahlen[soll])))

    # Gegenrichtung: ein Text MIT Platzhalter, der nirgends durch sprintf
    # laeuft, kommt beim Anwender als rohes %s an.
    ohne_sprintf = []
    for datei, werte in sorted(sprachen.items()):
        for schluessel, wert in sorted(werte.items()):
            if schluessel in bedarf or schluessel in frei:
                continue
            if umwandlungen_zaehlen(wert) <= 0:
                continue
            if schluessel in mittelbar:
                # Gereicht wird er - nur nicht zaehlbar. Das gehoert unter
                # "ungeprueft", nicht unter "FEHLER".
                if datei == sorted(sprachen)[0]:
                    ungeprueft.append(
                        '%s (in sprintf, aber nicht als erstes Argument: %s)'
                        % (schluessel, ', '.join(sorted(set(mittelbar[schluessel])))))
                continue
            ohne_sprintf.append('%s: %s traegt Platzhalter, wird aber '
                                'nirgends durch sprintf gereicht'
                                % (schluessel, datei))

    print('Sprachdateien : %s' % ', '.join(sorted(sprachen)))
    print('Schluessel je Datei: %s'
          % ', '.join('%s=%d' % (d, len(w)) for d, w in sorted(sprachen.items())))
    print('sprintf-Stellen mit <kuerzel>_t: %d Schluessel' % len(bedarf))
    for p in sorted(gem):
        print('uebergangen: %s - unveraenderte Abschrift von Werkzeuge/gemeinsam/%s%s'
              % (os.path.relpath(p, os.path.realpath(wurzel)).replace('\\', '/'),
                 os.path.basename(p),
                 (', dazu %d Modulschluessel in [ANSAGE] (das Modul formatiert sie selbst)'
                  % len(frei)) if os.path.basename(p) == 'sprachausgabe.php' else ''))
    for tief, _, dateien in os.walk(wurzel):
        if 'sprachausgabe.php' in dateien:
            p = os.path.join(tief, 'sprachausgabe.php')
            if os.path.realpath(p) not in gem:
                print('Hinweis: %s weicht von Werkzeuge/gemeinsam/sprachausgabe.php ab - '
                      'wird normal geprueft' % os.path.relpath(p, wurzel).replace('\\', '/'))
    if ungeprueft:
        print('ungeprueft (Zahl der Argumente nicht ermittelbar - '
              'diese Schluessel sind NICHT nachgezaehlt): %d' % len(ungeprueft))
        for u in ungeprueft:
            print('   ', u)
    for f in fehler + ohne_sprintf:
        print('FEHLER  ' + f)
    if fehler or ohne_sprintf:
        print('%d Widerspruch(e).' % (len(fehler) + len(ohne_sprintf)))
        return 1
    print('Kein Widerspruch zwischen Text und Aufrufstelle.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
