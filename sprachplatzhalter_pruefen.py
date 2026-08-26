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
NUR_T = re.compile(r"sm_t\s*\(\s*'([A-Za-z0-9_.]+)'\s*\)")
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
    nummern = [int(t) for t in treffer if t]
    if nummern and len(nummern) == len(treffer):
        return max(nummern)
    return len(treffer)


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

    bedarf = {}      # Schluessel -> {Zahl: [Fundstellen]}
    ungeprueft = []  # sm_t ohne erkennbaren sprintf-Zusammenhang
    for tief, _, dateien in os.walk(wurzel):
        for name in sorted(dateien):
            if not name.endswith('.php'):
                continue
            pfad = os.path.join(tief, name)
            with open(pfad, encoding='utf-8', errors='replace') as f:
                inhalt = f.read()
            kurz = os.path.relpath(pfad, wurzel).replace('\\', '/')
            gesehen = set()
            for m in AUFRUF.finditer(inhalt):
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
            if schluessel in bedarf:
                continue
            if umwandlungen_zaehlen(wert) > 0:
                ohne_sprintf.append('%s: %s traegt Platzhalter, wird aber '
                                    'nirgends durch sprintf gereicht'
                                    % (schluessel, datei))

    print('Sprachdateien : %s' % ', '.join(sorted(sprachen)))
    print('Schluessel je Datei: %s'
          % ', '.join('%s=%d' % (d, len(w)) for d, w in sorted(sprachen.items())))
    print('sprintf-Stellen mit <kuerzel>_t: %d Schluessel' % len(bedarf))
    if ungeprueft:
        print('ungeprueft: %d' % len(ungeprueft))
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
