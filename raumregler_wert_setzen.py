#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setzt einen Def-Parameter an einem oder mehreren Raumreglern - byteweise.

Die Parameter eines Bausteins stehen als Def am Anschluss, nicht als Attribut
am <C> (REGELN_3 B7a). Dieses Werkzeug fasst genau diese eine Stelle an und
prueft hinterher, dass sich die Dateigroesse um exakt den Unterschied der
Ziffern geaendert hat - alles andere waere ein Fehler.

Gemessene Zuordnung (30.08.2026, am Miniserver gegengelesen):
    TComfort   = Komforttemperatur Heizen   (comfortTemperature)
    TComfortC  = Komforttemperatur Kuehlen  (comfortTemperatureCool)

ACHTUNG, hier stand bis 01.09.2026 TComfortHC als Komforttemperatur
Heizen - das ist falsch. Am 29.08.2026 wurden die Schlafzimmer zunaechst
ueber TComfortHC gesetzt, ohne jede Wirkung. Der Miniserver meldete
comfortTemperature aus TComfort:
    EG Flur   TComfort 17    TComfortHC 22    live: 17
TComfortHC regelt NICHT; seine Rolle ist ungeklaert. Siehe REGELN_3 und
Loxone_Bausteine_Bedeutung.md.

Aufruf:
    raumregler_wert_setzen.py <quelle> <ziel> <Schluessel> <Wert> <Raum> [<Raum> ...]
    raumregler_wert_setzen.py <datei> --zeigen <Schluessel>
"""
import pathlib
import re
import sys


def regler(z):
    """[(Zeilennummer, Titel, Endzeile)] aller Raumregler."""
    raus = []
    for i, x in enumerate(z):
        if '<C Type="HeatIRoomController2"' not in x:
            continue
        t = re.search(r'Title="([^"]*)"', x)
        d = len(x) - len(x.lstrip("\t"))
        e = next(j for j in range(i + 1, len(z))
                 if z[j].strip() == "</C>"
                 and (len(z[j]) - len(z[j].lstrip("\t"))) == d)
        raus.append((i, t.group(1) if t else "-", e))
    return raus


def wert_zeile(z, i, e, schluessel):
    tr = [j for j in range(i + 1, e)
          if re.match(r'<Co K="%s"[^>]*\bDef="' % re.escape(schluessel), z[j].strip())]
    return tr[0] if len(tr) == 1 else None


def main() -> int:
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    quelle = pathlib.Path(sys.argv[1])
    roh = quelle.read_bytes()
    assert roh[:3] == b"\xef\xbb\xbf", "BOM fehlt"
    crlf = roh.count(b"\r\n")
    lf = roh.count(b"\n") - crlf
    # Die Zahl der einzelnen LF ist KEINE Konstante. An den eigenen
    # Projektdateien gemessen (01.09.2026): Config 17.1.6.30 schrieb 104,
    # Config 17.1.7.27 schreibt 236 - derselbe Sprung hob auch
    # <ControlList Version> von 272 auf 273. Hier stand frueher
    # `assert lf == 236`; das waere beim naechsten Config-Sprung
    # fehlgeschlagen, ohne dass an der Datei etwas falsch gewesen waere.
    # Geprueft wird deshalb, was wirklich gelten muss: die Datei ist
    # CRLF-getrennt, und der Schreibvorgang unten darf die HIER gemessene
    # Zahl nicht verschieben.
    assert crlf > 0, "keine CRLF - durch eine Zeilenendeumwandlung gelaufen"
    z = roh.decode("utf-8-sig").split("\r\n")

    if sys.argv[2] == "--zeigen":
        s = sys.argv[3]
        for i, titel, e in regler(z):
            j = wert_zeile(z, i, e, s)
            v = re.search(r'\bDef="([^"]*)"', z[j]).group(1) if j else "(nicht gesetzt)"
            print("   %-32s %s = %s"
                  % (titel.encode("latin-1", "replace").decode("latin-1")[:32], s, v))
        return 0

    ziel = pathlib.Path(sys.argv[2])
    schluessel, wert = sys.argv[3], sys.argv[4]
    raeume = sys.argv[5:]
    if not raeume:
        print("Kein Raum genannt - es wird nichts pauschal geaendert.")
        return 2

    erwartet = 0
    for raum in raeume:
        treffer = [(i, t, e) for i, t, e in regler(z) if t == raum]
        assert len(treffer) == 1, "%s: %d Regler gefunden" % (raum, len(treffer))
        i, _, e = treffer[0]
        j = wert_zeile(z, i, e, schluessel)
        assert j is not None, "%s: %s nicht eindeutig" % (raum, schluessel)
        alt = re.search(r'\bDef="([^"]*)"', z[j]).group(1)
        if alt == wert:
            print("   %-32s stand schon auf %s" % (raum, alt))
            continue
        neu = re.sub(r'(<Co K="%s"[^>]*\bDef=")[^"]*(")' % re.escape(schluessel),
                     lambda m: m.group(1) + wert + m.group(2), z[j], count=1)
        erwartet += len(neu.encode("utf-8")) - len(z[j].encode("utf-8"))
        z[j] = neu
        print("   %-32s %s: %s -> %s" % (raum, schluessel, alt, wert))

    neu_roh = b"\xef\xbb\xbf" + "\r\n".join(z).encode("utf-8")
    assert neu_roh.count(b"\n") - neu_roh.count(b"\r\n") == lf, \
        "einzelne LF verschoben: %d statt %d" % (
            neu_roh.count(b"\n") - neu_roh.count(b"\r\n"), lf)
    assert neu_roh.count(b"\r\n") == crlf, "CRLF verschoben"
    assert len(neu_roh) - len(roh) == erwartet, \
        "unerwartete Groessenaenderung %+d statt %+d" % (len(neu_roh) - len(roh), erwartet)
    ziel.write_bytes(neu_roh)
    print("geschrieben: %s  (%d Bytes, %+d, CRLF %d, einzelne LF %d)"
          % (ziel.name, len(neu_roh), len(neu_roh) - len(roh), crlf, lf))
    return 0


if __name__ == "__main__":
    sys.exit(main())
