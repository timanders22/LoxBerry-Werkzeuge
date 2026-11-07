#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Liest aus der Reihe der gespeicherten Projektdateien, was Config schreibt.

WARUM ES DIESES WERKZEUG GIBT
-----------------------------
Am 28.08.2026 musste der Hausherr zwoelfmal dieselbe Datei mit je einer
anderen Einstellung speichern, damit die Bedeutung von `StatsType` messbar
wurde. Das war die richtige Methode - aber sie war nicht noetig: der Ordner
enthaelt 162 datierte Fassungen seit Juli. Jede Aenderung, die je in Config
gemacht wurde, steht als Differenz zwischen zwei benachbarten Dateien darin.

Dieses Werkzeug geht die Reihe chronologisch durch, wirft die bekannte
Speicher-Kosmetik weg und sammelt alles Uebrige: welcher Bausteintyp welche
Eigenschaft je getragen hat, mit welchen Werten, wann zuerst gesehen und an
welchem Baustein. Das ist das Rohmaterial fuer die Spalte, die der
Baustein-Referenz fehlt - die Bedeutung.

Ein Fund ist keine Bedeutung. Das Werkzeug sagt, DASS sich etwas geaendert
hat und WIE die Werte aussehen; was die Einstellung in Config heisst, muss
danebengelegt werden.

Aufruf:
    woerterbuch_lernen.py <ordner> [--ziel <datei.md>] [--ab <praefix>]
                          [--typ <Bausteintyp>]
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

# Was Config bei jedem Speichern von sich aus umschreibt - gemessen 27.-29.08.
KOSMETIK = {
    "WF", "Px", "Py", "Px2", "Py2", "LtE", "Date", "DateS", "NumO", "NextObj",
    "UserModes", "Cl", "U", "Title", "Desc", "NDOC", "V", "Nio", "Nc",
    "SpStates", "IName", "TId", "CDate", "BDate",
}


def einlesen(pfad):
    """{UUID: (Typ, Titel, {Eigenschaft: Wert})}"""
    z = Path(pfad).read_bytes().decode("utf-8-sig").split("\r\n")
    raus = {}
    for i, x in enumerate(z):
        s = x.strip()
        if not s.startswith("<C Type="):
            continue
        a = dict(ATTR.findall(s))
        u = a.get("U")
        if not u:
            continue
        eig = {k: v for k, v in a.items() if k not in KOSMETIK and k != "Type"}
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
        raus[u] = (a.get("Type", "?"), a.get("Title", a.get("Desc", "-")), eig)
    return raus


def kurz(s, n=40):
    return s.encode("latin-1", "replace").decode("latin-1")[:n]


def hausdatei_kern() -> str:
    """Kern des Namens der eigenen Hausdatei (Form 'Projekt_Name').

    Er steht NICHT im Quelltext, denn er traegt einen Familiennamen. Gelesen
    wird LOX_HAUSDATEI, sonst die erste Zeile von hausdatei.txt neben diesem
    Skript (privat, .gitignore). Fehlt beides, ist das Ergebnis leer.
    """
    import os
    k = os.environ.get("LOX_HAUSDATEI", "").strip()
    if k:
        return k
    p = Path(os.path.abspath(__file__)).with_name("hausdatei.txt")
    try:
        for z in p.read_text(encoding="utf-8").splitlines():
            z = z.strip()
            if z and not z.startswith("#"):
                return z
    except OSError:
        pass
    return ""


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    ordner = Path(sys.argv[1])
    ziel = None
    if "--ziel" in sys.argv:
        ziel = Path(sys.argv[sys.argv.index("--ziel") + 1])
    ab = sys.argv[sys.argv.index("--ab") + 1] if "--ab" in sys.argv else ""
    nur_typ = sys.argv[sys.argv.index("--typ") + 1] if "--typ" in sys.argv else None

    kern = hausdatei_kern()
    if not kern:
        print("ABBRUCH: LOX_HAUSDATEI nicht gesetzt und hausdatei.txt fehlt - "
              "ohne den Namen der Hausdatei wird nichts geraten.")
        return 2
    dateien = sorted(p for p in ordner.glob("2026*_" + kern + "_KI.Loxone")
                     if p.name >= ab)
    if len(dateien) < 2:
        print("Weniger als zwei Fassungen gefunden.")
        return 2
    print("%d Fassungen, %s bis %s\n" % (len(dateien), dateien[0].name[:13],
                                         dateien[-1].name[:13]))

    # (Typ, Eigenschaft) -> {Wert: [(Datum, Titel)]}
    tafel = collections.defaultdict(lambda: collections.defaultdict(list))
    aenderungen = 0
    vorher, vorname = None, None
    for p in dateien:
        try:
            jetzt = einlesen(p)
        except Exception as e:
            print("   uebersprungen: %s (%s)" % (p.name, e))
            continue
        if vorher is not None:
            for u, (typ, titel, eig) in jetzt.items():
                if nur_typ and typ != nur_typ:
                    continue
                alt = vorher.get(u)
                if alt is None:
                    continue
                for k, v in eig.items():
                    v_alt = alt[2].get(k)
                    if v_alt == v:
                        continue
                    tafel[(typ, k)][v].append((p.name[:13], titel))
                    aenderungen += 1
                for k in alt[2]:
                    if k not in eig:
                        tafel[(typ, k)]["(entfernt)"].append((p.name[:13], titel))
                        aenderungen += 1
        vorher, vorname = jetzt, p.name

    zeilen = []
    zeilen.append("# Was Config in diese Anlage schreibt")
    zeilen.append("")
    zeilen.append("Aus %d gespeicherten Fassungen abgelesen (%s bis %s), "
                  "%d beobachtete Aenderungen." % (len(dateien), dateien[0].name[:13],
                                                   dateien[-1].name[:13], aenderungen))
    zeilen.append("")
    zeilen.append("Erzeugt von `Werkzeuge/woerterbuch_lernen.py`. Eine Zeile sagt, "
                  "DASS sich eine Eigenschaft geaendert hat und welche Werte "
                  "vorkamen - **nicht**, wie die Einstellung in Config heisst. "
                  "Diese Spalte gehoert von Hand daneben.")
    zeilen.append("")
    zeilen.append("| Bausteintyp | Eigenschaft | beobachtete Werte | zuletzt | Beispiel |")
    zeilen.append("| --- | --- | --- | --- | --- |")
    for (typ, eig) in sorted(tafel):
        werte = tafel[(typ, eig)]
        alle = sorted(werte, key=lambda w: -len(werte[w]))
        zuletzt = max(d for w in werte for d, _ in werte[w])
        beispiel = werte[alle[0]][-1][1]
        w_text = ", ".join("`%s`" % (w or "(leer)") for w in alle[:8])
        if len(alle) > 8:
            w_text += ", … (%d weitere)" % (len(alle) - 8)
        zeilen.append("| %s | %s | %s | %s | %s |"
                      % (typ, eig, w_text, zuletzt, kurz(beispiel)))
    text = "\n".join(zeilen) + "\n"

    print("%d beobachtete Aenderungen, %d verschiedene (Typ, Eigenschaft)"
          % (aenderungen, len(tafel)))
    if ziel:
        ziel.write_bytes(text.encode("utf-8"))
        print("geschrieben: %s (%d Bytes)" % (ziel, len(text.encode("utf-8"))))
    else:
        print()
        print(text[:4000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
