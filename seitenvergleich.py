#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Das gelieferte HTML zweier Fassungen Seite fuer Seite gegeneinander halten.

WOZU
====
Eine Aenderung, die am Bildschirm nichts aendern SOLL - eine umgeordnete
Sprachdatei, ein umsortierter Codeblock, eine neu gepackte Vorlage -, ist erst
dann belegt, wenn das gelieferte HTML beider Fassungen gleich ist. „Der
Prueflauf war gruen" belegt es nicht: ein Pruefstueck misst die Fragen, die
jemand gestellt hat.

Verglichen wird der TEXT, den die Oberflaeche liefert (etwa aus
`reiterlauf.py`), nicht der Quelltext. Herausgerechnet wird nur, was sich
zwangslaeufig unterscheidet und mit der Aenderung nichts zu tun hat:

  * der zufaellig erzeugte Formulartoken und jede lange Hexfolge
  * die Fassungsnummer (sie steckt im Ordnernamen und damit in Pfaden)
  * Datums- und Uhrzeitangaben

Jede dieser Ausnahmen steht im Bericht, damit niemand sie fuer „gleich" haelt.
Alles Uebrige muss Zeichen fuer Zeichen stimmen.

BEIDE SEITEN MUESSEN AUS DEMSELBEN STAND KOMMEN
===============================================
`rendern.py` leitet `LBPCONFIGDIR`, `LBPDATADIR` und `LBPLOGDIR` aus dem
ORDNERNAMEN ab - zwei Fassungen haben also zwei getrennte Pruefstaende. Hat
einer davon inzwischen etwas gesehen (ein `wirkungstest.py`-Lauf, der einen
Dienst angestossen und ein Protokoll geschrieben hat), unterscheiden sich die
Seiten wegen des Pruefstands, nicht wegen der Fassung. Gemessen 13.09.2026:
1162 Zeichen Unterschied im Reiter „Logdateien", und der Inhalt war ein
`ModuleNotFoundError: fcntl` aus einem Windows-Lauf.
Abhilfe: beide Seiten mit `reiterlauf.py --stand-leeren` rendern (oder
`config/`, `data/`, `log/` der alten Fassung auf die neue spiegeln, Regeln/02).

Anlass: APC-UPS 1.2.8, 13.09.2026 - 20 Seiten (5 Reiter x 2 Sprachen x
PHP 7.4/8.4) gegen 1.2.7, byteweise gleich.

AUFRUF
======
    python3 seitenvergleich.py <Ordner_alt> <Ordner_neu> [--fassungen 1.2.7,1.2.8]

    --fassungen  Fassungsnummern, die herausgerechnet werden. Ohne Angabe
                 werden Nummern der Form X.Y.Z gesucht, die in BEIDEN
                 Ordnernamen stecken - steht dort keine, wird auch keine
                 herausgerechnet, und das sagt der Bericht.

Rueckgabe 0 = alle Seiten gleich, 1 = Unterschied, 2 = nichts gemessen.
Rein lesend.
"""
import difflib
import io
import os
import re
import sys

# Kein \b am Ende: der Ordner heisst oft „…-1.2.7_de", und '_' ist ein
# Wortzeichen - mit \b faende das Muster dort NICHTS und der Bericht meldete
# „keine Fassungsnummer gefunden", obwohl eine dasteht.
FASSUNG = re.compile(r'(?<![\d.])\d+\.\d+\.\d+(?![\d.])')


def _feste(argv, wertflaggen):
    """Die Argumente ohne Schalter - und ohne deren WERTE.

    Ohne diese Unterscheidung landet der Wert eines Schalters in getrennter
    Schreibweise (`--sprachen de,en`) unter den festen Argumenten, und die
    Zaehlung darunter weist einen richtigen Aufruf ab.
    """
    aus = []
    ueberspringen = False
    for a in argv:
        if ueberspringen:
            ueberspringen = False
            continue
        if a.startswith('--'):
            ueberspringen = a in wertflaggen
            continue
        aus.append(a)
    return aus


def _wert(argv, name, vorgabe=None):
    for i, a in enumerate(argv):
        if a == name and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith(name + '='):
            return a.split('=', 1)[1]
    return vorgabe


def regeln(fassungen):
    r = []
    for f in fassungen:
        r.append((re.compile(re.escape(f)), '<FASSUNG>'))
    r += [
        (re.compile(r'(name="[A-Za-z0-9_]*form[A-Za-z0-9_]*" value=")[0-9a-f]*(")'),
         r'\1<TOKEN>\2'),
        (re.compile(r'\b[0-9a-f]{32,64}\b'), '<HEX>'),
        (re.compile(r'\d{2}\.\d{2}\.\d{4},?(\s+\d{2}:\d{2}(:\d{2})?)?'), '<ZEIT>'),
        (re.compile(r'\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2}(:\d{2})?)?'), '<ZEIT>'),
        (re.compile(r'\b\d{2}:\d{2}:\d{2}\b'), '<UHR>'),
    ]
    return r


def eichen(t, r):
    for muster, ersatz in r:
        t = muster.sub(ersatz, t)
    return t


def main(argv):
    fest = _feste(argv, ('--fassungen',))
    if len(fest) != 2:
        sys.stderr.write(__doc__.split('AUFRUF')[1].strip() + '\n')
        return 2
    alt, neu = fest
    for d in (alt, neu):
        if not os.path.isdir(d):
            sys.stderr.write('ABBRUCH: %s ist kein Ordner\n' % d)
            return 2

    angabe = _wert(argv, '--fassungen')
    if angabe:
        fassungen = [f.strip() for f in angabe.split(',') if f.strip()]
    else:
        fassungen = sorted(set(FASSUNG.findall(os.path.basename(os.path.abspath(alt))))
                           | set(FASSUNG.findall(os.path.basename(os.path.abspath(neu)))))
    print('Herausgerechnet: Formulartoken, lange Hexfolgen, Datum und Uhrzeit%s'
          % (', Fassungsnummer(n) ' + ', '.join(fassungen) if fassungen
             else ' — KEINE Fassungsnummer gefunden, es wird keine herausgerechnet'))
    r = regeln(fassungen)

    namen = sorted(set(os.listdir(alt)) | set(os.listdir(neu)))
    namen = [n for n in namen
             if os.path.isfile(os.path.join(alt, n)) or os.path.isfile(os.path.join(neu, n))]
    if not namen:
        print('BEIDE ORDNER LEER - nichts gemessen.')
        return 2

    fehl = 0
    for name in namen:
        a = os.path.join(alt, name)
        b = os.path.join(neu, name)
        if not (os.path.isfile(a) and os.path.isfile(b)):
            wo = alt if os.path.isfile(a) else neu
            print('%-24s NUR IN %s' % (name, wo))
            fehl += 1
            continue
        ta = eichen(io.open(a, encoding='utf-8', errors='replace').read(), r)
        tb = eichen(io.open(b, encoding='utf-8', errors='replace').read(), r)
        if ta == tb:
            print('%-24s gleich (%d Zeichen, nach Eichung)' % (name, len(ta)))
            continue
        fehl += 1
        print('%-24s VERSCHIEDEN:' % name)
        d = list(difflib.unified_diff(ta.splitlines(), tb.splitlines(),
                                      'alt', 'neu', lineterm='', n=1))
        for z in d[:30]:
            print('    ' + z[:200])
        if len(d) > 30:
            print('    ... %d weitere Zeilen' % (len(d) - 30))

    print('%d Datei(en) verglichen, %d verschieden' % (len(namen), fehl))
    return 1 if fehl else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
