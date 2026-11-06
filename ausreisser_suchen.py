#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sucht Bausteine, deren Einstellung von der ihrer Artgenossen abweicht.

WARUM ES DIESES WERKZEUG GIBT
-----------------------------
Am 29.08.2026 kam heraus, dass der Wohnzimmerfuehler eine Wertekorrektur
17,3 -> 22 trug, waehrend zwoelf gleichartige Fuehler 100 -> 100 stehen
hatten. Loxone rechnet das als Verstaerkung durch den Nullpunkt: der Raum
meldete 32,7 statt 25,8 Grad, seit Monaten, Tag und Nacht.

Gefunden wurde das, weil der Hausherr zufaellig eine zweite Messung im selben
Raum hatte. Genau diese Sorte Fehler ist in der Datei nicht als Fehler
erkennbar - die Zahl ist gueltig, die Datei ist heil, die Pruefkette schweigt.
Sichtbar wird sie nur im Vergleich mit den Artgenossen.

DAS VERFAHREN
-------------
Bausteine desselben Typs nach Eigenschaft gruppieren. Wo die grosse Mehrheit
denselben Wert traegt und einzelne einen anderen, ist das ein Kandidat - kein
Befund. Eine Abweichung kann voellig gewollt sein (die Fassadenrichtung eines
Rollladens SOLL sich unterscheiden). Das Werkzeug denkt nicht, es zeigt hin.

Aufruf:  ausreisser_suchen.py <projektdatei> [--alle] [--mindestens N]
         --alle       zeigt auch Gruppen mit vielen verschiedenen Werten
         --mindestens Gruppengroesse ab der geprueft wird (Vorgabe 5)
"""

import collections
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

ATTR = re.compile(r'(\w+)="([^"]*)"')

# Was nichts ueber die Einstellung sagt: Identitaet, Lage, Farbe, Anzeige.
EGAL = {
    "U", "Title", "Desc", "Px", "Py", "Px2", "Py2", "Cl", "WF", "NDOC", "LtE",
    "V", "IName", "SpStates", "TId", "N", "Nio", "Nc", "Type", "Ref", "Input",
    "K", "Cr", "Pr", "Ugr", "Ugx", "IconV", "Unit", "CaptionType", "SubType",
    "Miniserver", "ConfigVersion", "Date", "DateS", "CDate", "BDate", "NumO",
    "Analog", "Tx", "Def",  # Def wird ueber die Co-Schluessel gesondert erfasst
}


def einlesen(pfad):
    """[(Typ, Titel, {Eigenschaft: Wert})] - Attribute am <C> plus Co-Def."""
    z = Path(pfad).read_bytes().decode("utf-8-sig").split("\r\n")
    raus = []
    for i, x in enumerate(z):
        s = x.strip()
        if not s.startswith("<C Type="):
            continue
        a = dict(ATTR.findall(s))
        typ = a.get("Type", "?")
        eig = {k: v for k, v in a.items() if k not in EGAL}
        if not s.endswith("/>"):
            d = len(x) - len(x.lstrip("\t"))
            try:
                e = next(j for j in range(i + 1, len(z))
                         if z[j].strip() == "</C>"
                         and (len(z[j]) - len(z[j].lstrip("\t"))) == d)
            except StopIteration:
                continue
            for j in range(i + 1, e):
                if len(z[j]) - len(z[j].lstrip("\t")) != d + 1:
                    continue
                m = re.match(r'<Co K="([^"]+)"[^>]*\bDef="([^"]*)"', z[j].strip())
                if m:
                    eig["Def:" + m.group(1)] = m.group(2)
        raus.append((typ, a.get("Title", a.get("Desc", "-")), eig))
    return raus


def kurz(s, n=44):
    return s.encode("latin-1", "replace").decode("latin-1")[:n]


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    pfad = Path(sys.argv[1])
    if not pfad.is_file():
        print("Keine Datei: %s" % pfad)
        return 2
    alle = "--alle" in sys.argv
    mind = 5
    if "--mindestens" in sys.argv:
        mind = int(sys.argv[sys.argv.index("--mindestens") + 1])

    bausteine = einlesen(pfad)
    print("%d Bausteine gelesen aus %s\n" % (len(bausteine), pfad.name))

    # Typ -> Eigenschaft -> Wert -> [Titel]
    tafel = collections.defaultdict(lambda: collections.defaultdict(
        lambda: collections.defaultdict(list)))
    zahl = collections.Counter()
    for typ, titel, eig in bausteine:
        zahl[typ] += 1
        for k, v in eig.items():
            tafel[typ][k][v].append(titel)

    kandidaten = 0
    for typ in sorted(tafel):
        if zahl[typ] < mind:
            continue
        for eig in sorted(tafel[typ]):
            werte = tafel[typ][eig]
            # Nur Eigenschaften, die (fast) alle Artgenossen tragen
            getragen = sum(len(v) for v in werte.values())
            if getragen < zahl[typ] * 0.8:
                continue
            haeufig, n_haeufig = max(werte.items(), key=lambda kv: len(kv[1]))
            n_haeufig = len(n_haeufig)
            if n_haeufig < getragen * 0.6:
                if not alle:
                    continue
            abweichend = [(w, t) for w, t in werte.items() if w != haeufig]
            if not abweichend:
                continue
            # Wenn fast jeder einen eigenen Wert hat, ist es keine Einstellung,
            # sondern eine Kenngroesse (Fassadenrichtung, Adresse, Name).
            if len(werte) > max(3, getragen * 0.5) and not alle:
                continue
            print("%s . %s      Mehrheit %s (%d von %d)"
                  % (typ, eig, haeufig or "(leer)", n_haeufig, getragen))
            for w, titel in sorted(abweichend, key=lambda kv: len(kv[1])):
                for t in titel[:4]:
                    print("      %-10s %s" % (w or "(leer)", kurz(t)))
                if len(titel) > 4:
                    print("      %-10s ... und %d weitere" % ("", len(titel) - 4))
                kandidaten += len(titel)
            print()

    print("%d Kandidaten. Ein Kandidat ist KEIN Befund - eine Abweichung kann"
          % kandidaten)
    print("gewollt sein. Das Werkzeug zeigt hin, entschieden wird von Hand.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
