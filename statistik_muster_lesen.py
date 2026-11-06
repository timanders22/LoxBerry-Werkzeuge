#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Liest ab, wie Config die Statistik eines Bausteins in die Datei schreibt.

WARUM ES DIESES WERKZEUG GIBT
-----------------------------
Am 28.08.2026 sollte die Zaehlerkachel *Einbrueche der Beschattungsfreigabe*
eine Statistik bekommen. Der Marker war unbekannt, und einen Wert zu erfinden
waere genau die Sorte Vermutung, die in derselben Woche schon einmal einen Tag
Beschattung gekostet hat. Also hat der Hausherr den Haken in Config gesetzt,
und dieses Werkzeug liest ab, was Config daraufhin geschrieben hat.

DER ERSTE ANLAUF WAR FALSCH. Das Werkzeug suchte `<statGrp .../>` als
Kindelement - so steht es bei den Zaehlerbausteinen. Bei einer Kachel schreibt
Config aber ATTRIBUTE an das `<C>` selbst:

    StateV  (analoge Kachel)  StatsType="8"  StatsAutoDel="1"
    Memory  (digitaler Wert)  StatsType="7"  StatsAutoDel="1"

Ein eigenes Intervall-Attribut gibt es nicht; die Wahl steckt offenbar in
`StatsType`. Deshalb liest dieses Werkzeug jetzt BEIDES - Attribute und
Kindelemente - und vergleicht zwei Fassungen, damit man aus einer Reihe von
Speicherungen mit verschiedenen Einstellungen die Bedeutung ablesen kann,
statt sie zu raten.

Aufruf:
    statistik_muster_lesen.py <datei>
        Listet jeden Baustein, der eine Statistik traegt.
    statistik_muster_lesen.py <nachher> <vorher>
        Zeigt nur, was hinzugekommen oder anders geworden ist.
    statistik_muster_lesen.py --tabelle <uuidteil> <datei> [<datei> ...]
        Eine Zeile je Datei mit den Stats-Attributen EINES Bausteins - die
        Entschluesselungstabelle einer Messreihe.
"""

import re
import sys
from pathlib import Path

# Die Konsole dieses Rechners ist cp1252. In den Einheiten stehen Zeichen, die
# es dort nicht gibt (gemessen 28.08.2026: ein griechisches my liess das
# Werkzeug abstuerzen). Lieber ein Fragezeichen als ein Abbruch im Bericht.
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

STAT_KIND = re.compile(r"<statGrp\b[^>]*/>")
ATTR = re.compile(r'(\w+)="([^"]*)"')


def stats_attribute(kopf: str):
    """Alle Attribute, die mit 'Stats' anfangen, in Reihenfolge."""
    return {k: v for k, v in ATTR.findall(kopf) if k.startswith("Stats")}


def bausteine_mit_statistik(pfad):
    """[(UUID, Typ, Titel, StatsAttribute, [statGrp-Zeilen], [Zusatzzeilen])]"""
    z = Path(pfad).read_bytes().decode("utf-8-sig").split("\r\n")
    raus = []
    for i, x in enumerate(z):
        s = x.strip()
        if not s.startswith("<C Type="):
            continue
        a = dict(ATTR.findall(s))
        attr = stats_attribute(s)
        stat, zusatz = [], []
        if not s.endswith("/>"):
            d = len(x) - len(x.lstrip("\t"))
            try:
                e = next(j for j in range(i + 1, len(z))
                         if z[j].strip() == "</C>"
                         and (len(z[j]) - len(z[j].lstrip("\t"))) == d)
            except StopIteration:
                continue
            # NUR direkte Kinder - sonst meldet jede Seite die Statistik ihrer
            # Enkel.
            for j in range(i + 1, e):
                if len(z[j]) - len(z[j].lstrip("\t")) != d + 1:
                    continue
                t = z[j].strip()
                if STAT_KIND.match(t):
                    stat.append(t)
                elif t.startswith(("<IoData", "<Display")):
                    zusatz.append(t)
        if not attr and not stat:
            continue
        raus.append((a.get("U", "?"), a.get("Type", "?"),
                     a.get("Title", a.get("Desc", "-")), attr, stat, zusatz))
    return raus


def kurz(s, n=54):
    return s.encode("latin-1", "replace").decode("latin-1")[:n]


def zeigen(eintraege, ueberschrift):
    print(ueberschrift)
    if not eintraege:
        print("   keine.")
        return
    for u, typ, titel, attr, stat, zusatz in eintraege:
        print("   %-16s %s" % (typ, kurz(titel)))
        print("      %s" % u)
        if attr:
            print("      " + "  ".join('%s="%s"' % kv for kv in attr.items()))
        for s in stat:
            print("      %s" % s)
        for s in zusatz:
            print("      %s" % s[:180])
        print()


def tabelle(uuidteil, dateien):
    print("%-46s %s" % ("Datei", "Stats-Attribute"))
    print("-" * 78)
    for p in dateien:
        treffer = [e for e in bausteine_mit_statistik(p) if uuidteil in e[0]]
        if not treffer:
            print("%-46s (keine Statistik an diesem Baustein)" % Path(p).name)
            continue
        for e in treffer:
            print("%-46s %s" % (Path(p).name,
                  "  ".join('%s="%s"' % kv for kv in e[3].items()) or "(nur statGrp)"))
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    if sys.argv[1] == "--tabelle":
        if len(sys.argv) < 4:
            print(__doc__)
            return 2
        return tabelle(sys.argv[2], sys.argv[3:])

    datei = Path(sys.argv[1])
    if not datei.is_file():
        print("Keine Datei: %s" % datei)
        return 2
    jetzt = bausteine_mit_statistik(datei)

    if len(sys.argv) < 3:
        nach_typ = {}
        for e in jetzt:
            nach_typ[e[1]] = nach_typ.get(e[1], 0) + 1
        zeigen(jetzt, "Bausteine mit Statistik in %s:" % datei.name)
        print("Zusammen %d, nach Typ: %s"
              % (len(jetzt), ", ".join("%s %d" % kv for kv in sorted(nach_typ.items()))))
        return 0

    vorher = Path(sys.argv[2])
    if not vorher.is_file():
        print("Keine Datei: %s" % vorher)
        return 2
    alt = {e[0]: e for e in bausteine_mit_statistik(vorher)}
    neu = [e for e in jetzt if e[0] not in alt]
    geaendert = [e for e in jetzt
                 if e[0] in alt and (alt[e[0]][3], alt[e[0]][4]) != (e[3], e[4])]
    zeigen(neu, "NEU mit Statistik in %s gegenueber %s:" % (datei.name, vorher.name))
    if geaendert:
        print("GEAENDERT:")
        for e in geaendert:
            a = alt[e[0]]
            print("   %-16s %s" % (e[1], kurz(e[2])))
            print("      vorher : %s" % ("  ".join('%s="%s"' % kv for kv in a[3].items())
                                         or "(keine Attribute)"))
            print("      nachher: %s" % ("  ".join('%s="%s"' % kv for kv in e[3].items())
                                         or "(keine Attribute)"))
            print()
    if not neu and not geaendert:
        print("Nichts hinzugekommen und nichts geaendert.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
