#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Liest die WERKSEINSTELLUNGEN aus einem frisch angelegten Loxone-Projekt.

WARUM ES DIESES WERKZEUG GIBT
-----------------------------
`Loxone_Baustein_Referenz.md` nennt zu jedem Anschluss einen `Def`-Wert. Am
30.08.2026 stellte sich heraus: das sind **keine Werkseinstellungen**. Die
Datei, aus der sie stammen, ist die Projektdatei des Hauses mit eingefuegten
Bausteinen - und auch die eingefuegten waren teils schon verstellt:

    AnalogThresholdTrigger
       alte Liste               On=0.5   Off=0.2    "Regen > 0,5 mm/h"
       Musterstein O1084        On=45    Off=30     ebenfalls verstellt
       Config, frisch angelegt  On=5     Off=1      die echte Vorgabe

Eine O-Nummer im Titel heisst "unbenannt", nicht "unveraendert". Es gibt daher
nur eine verlaessliche Quelle: ein Baustein, den Config gerade erst angelegt
hat und den niemand angefasst hat.

DIE GEGENPROBE
--------------
Kommt ein Typ mehrfach vor, muessen alle Exemplare Anschluss fuer Anschluss
und Wert fuer Wert gleich sein. Weichen sie ab, war eines angefasst - dann
meldet das Werkzeug den Typ als UNSICHER und nimmt ihn nicht auf. Ohne diese
Probe waere die neue Liste so viel wert wie die alte.

Aufruf:
    werksvorgaben_lesen.py <leeres_projekt.Loxone> [--ziel <datei.md>]
    werksvorgaben_lesen.py <datei> --pruefen <Typ>
"""

import collections
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

CO = re.compile(r'<Co K="([^"]*)"(?P<rest>[^>]*)')
DEF = re.compile(r'\bDef="([^"]*)"')
INV = re.compile(r'\bInv="true"')
ATTR = re.compile(r'(\w+)="([^"]*)"')

# Was am <C> steht und KEINE Einstellung ist: Identitaet, Lage, Darstellung.
KEINE_EINSTELLUNG = {
    "Type", "U", "Title", "Desc", "V", "Px", "Py", "Px2", "Py2", "Cl", "WF",
    "Nio", "Nc", "NDOC", "LtE", "IName", "SpStates", "TId", "Ref", "Modes",
    "Cr", "Pr", "Ugr", "Ugx", "IconV", "Date", "DateS", "CDate", "BDate",
    "NumO", "ConfigVersion", "PaperFormat", "Miniserver",
}


def frisch(titel, typ):
    """In einem eigens angelegten leeren Projekt ist JEDER Baustein frisch.

    Der erste Anlauf am 30.08.2026 pruefte auf Typname oder O-Nummer im Titel
    und uebersah dadurch genau die wichtigen Bausteine: Config gibt grossen
    Bausteinen einen deutschen Standardnamen - "Automatikbeschattung",
    "Schaltuhr", "Wecker". Das Kriterium war falsch gewaehlt.

    Das tragende Kriterium ist nicht der Titel, sondern die GEGENPROBE weiter
    unten: kommt ein Typ mehrfach vor, muessen alle Exemplare uebereinstimmen.
    Deshalb wird hier nichts mehr ausgesiebt.
    """
    return True


def einlesen(pfad):
    """{Typ: [(Titel, [(Anschluss, Def, Inv)])]} - nur frische Bausteine."""
    z = Path(pfad).read_bytes().decode("utf-8-sig", errors="replace").split("\r\n")
    raus = collections.defaultdict(list)
    for i, x in enumerate(z):
        s = x.strip()
        if not s.startswith("<C Type=") or s.endswith("/>"):
            continue
        typ = re.search(r'<C Type="([^"]*)"', s).group(1)
        ti = re.search(r'Title="([^"]*)"', s)
        titel = ti.group(1) if ti else ""
        if not frisch(titel, typ):
            continue
        d = len(x) - len(x.lstrip("\t"))
        try:
            e = next(j for j in range(i + 1, len(z))
                     if z[j].strip() == "</C>"
                     and (len(z[j]) - len(z[j].lstrip("\t"))) == d)
        except StopIteration:
            continue
        anschl = []
        for j in range(i + 1, e):
            if len(z[j]) - len(z[j].lstrip("\t")) != d + 1:
                continue
            m = CO.match(z[j].strip())
            if not m:
                continue
            rest = m.group("rest")
            dv = DEF.search(rest)
            anschl.append((m.group(1), dv.group(1) if dv else None,
                           bool(INV.search(rest))))
        # UUIDs sind Identitaet, keine Einstellung. Am 30.08.2026 fielen
        # HeatIRoomController2 und LightController2 durch die Gegenprobe,
        # nur weil ihre Exemplare verschiedene UUIDTimer bzw. uuidSeqencing
        # trugen - ein Unterschied ohne Bedeutung.
        attr = [(k, v) for k, v in ATTR.findall(s)
                if k not in KEINE_EINSTELLUNG
                and "uuid" not in k.lower()
                and not re.fullmatch(
                    r'(?:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{16},?)+', v)]
        raus[typ].append((titel, anschl, attr))
    return raus


def darstellen(anschl):
    teile = []
    for k, dv, inv in anschl:
        s = k
        if dv is not None:
            s += "=" + dv
        if inv:
            s += " INV"
        teile.append(s)
    return ", ".join(teile)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    quelle = Path(sys.argv[1])
    if not quelle.is_file():
        print("Keine Datei: %s" % quelle)
        return 2
    daten = einlesen(quelle)

    if "--pruefen" in sys.argv:
        typ = sys.argv[sys.argv.index("--pruefen") + 1]
        for titel, anschl, attr in daten.get(typ, []):
            print("   %-10s %s" % (titel, darstellen(anschl)))
            if attr:
                print("   %-10s Attribute: %s"
                      % ("", ", ".join('%s="%s"' % kv for kv in attr)))
        if typ not in daten:
            print("   %s: kein frischer Baustein in %s" % (typ, quelle.name))
        return 0

    sicher, unsicher = {}, {}
    for typ, liste in daten.items():
        saetze = [(a, at) for _, a, at in liste]
        if all(s == saetze[0] for s in saetze):
            sicher[typ] = (saetze[0][0], saetze[0][1], len(liste))
        else:
            unsicher[typ] = liste

    ziel = None
    if "--ziel" in sys.argv:
        ziel = Path(sys.argv[sys.argv.index("--ziel") + 1])

    zeilen = ["# Werkseinstellungen der Loxone-Bausteine", ""]
    zeilen.append("Abgelesen aus `%s` — einem **frisch angelegten, leeren "
                  "Projekt**. Jeder hier aufgeführte Baustein wurde von Config "
                  "angelegt und danach nicht angefasst; die Werte hinter `=` "
                  "sind deshalb Werkseinstellungen." % quelle.name)
    zeilen.append("")
    zeilen.append("Erzeugt von `Werkzeuge/werksvorgaben_lesen.py`. **Nicht** zu "
                  "verwechseln mit der `Def`-Spalte in "
                  "`Loxone_Baustein_Referenz.md` — die enthält Hauswerte.")
    zeilen.append("")
    zeilen.append("Gegenprobe: Typen, die mehrfach vorkommen, müssen in allen "
                  "Exemplaren übereinstimmen. %d Typen aufgenommen, %d wegen "
                  "Abweichung verworfen." % (len(sicher), len(unsicher)))
    zeilen.append("")
    zeilen.append("`INV` heißt: der unbeschaltete Eingang steht auf 1.")
    zeilen.append("")
    # Der deutsche Name, sofern MESSBAR: Config vergibt vielen frisch
    # eingefuegten Bausteinen ihren deutschen Namen als Titel. Wo nur eine
    # O-Nummer steht, ist er aus der Datei NICHT zu holen - dann bleibt die
    # Spalte leer. Geraten wird hier nichts.
    # ZWEI Belege sind noetig. Der Titel allein reicht nicht: beim ersten
    # Versuch am 30.08.2026 lieferte er fuer HeatIRoomController2 den Raumnamen
    # "Zentral" und fuer Memory die laufende Nummer "M1". Ein Titel gilt nur
    # dann als deutscher Bausteinname, wenn er zusaetzlich im Verzeichnis
    # loxone_bausteinnamen_de.txt steht.
    namen = set()
    nd = Path(__file__).with_name("loxone_bausteinnamen_de.txt")
    if nd.is_file():
        namen = {z.strip() for z in nd.read_text(encoding="utf-8").splitlines()
                 if z.strip() and not z.startswith("#")}
    # Vorrang hat die gemessene Zuordnung aus loxone_typ_deutsch.txt: dort
    # steht, was am 30.08.2026 aus Config-Bildschirmfotos abgelesen und ueber
    # die Bezeichnung in dieser Datei nachgeschlagen wurde.
    deutsch = {}
    td = Path(__file__).with_name("loxone_typ_deutsch.txt")
    if td.is_file():
        for zeile in td.read_text(encoding="utf-8").splitlines():
            zeile = zeile.split("#")[0].strip()
            if "=" in zeile:
                k, v = zeile.split("=", 1)
                deutsch[k.strip()] = v.strip()
    for typ, liste in daten.items():
        for titel, _, _ in liste:
            if titel in namen:
                deutsch.setdefault(typ, titel)
                break

    zeilen.append("| Typ | deutscher Name | Anschlüsse mit Werkseinstellung | Attribute am `<C>` | Beleg |")
    zeilen.append("| --- | --- | --- | --- | --- |")
    for typ in sorted(sicher):
        anschl, attr, n = sicher[typ]
        beleg = ("**%d Exemplare, übereinstimmend**" % n) if n > 1 else "1 Exemplar"
        at = ", ".join('`%s="%s"`' % kv for kv in attr) if attr else "—"
        zeilen.append("| `%s` | %s | %s | %s | %s |"
                      % (typ, deutsch.get(typ, "**?**"),
                         darstellen(anschl) or "—", at, beleg))
    ohne = sorted(t for t in sicher if t not in deutsch)
    if ohne:
        zeilen += ["", "## Ohne gemessenen deutschen Namen (%d)" % len(ohne), "",
                   "Diese Bausteine tragen in `Leer.Loxone` nur eine O-Nummer. "
                   "Der deutsche Name steht nicht in der Datei und wird hier "
                   "**nicht geraten**. Er lässt sich messen, indem man den "
                   "Baustein in Config anwählt — die Kopfzeile des "
                   "Eigenschaftenfensters nennt ihn.", "",
                   "`" + "`, `".join(ohne) + "`"]
    if unsicher:
        zeilen += ["", "## Verworfen — Exemplare weichen voneinander ab", ""]
        for typ, liste in sorted(unsicher.items()):
            zeilen.append("* **`%s`**" % typ)
            for titel, a, at in liste:
                zeilen.append("  * `%s`: %s | %s"
                              % (titel, darstellen(a),
                                 ", ".join('%s="%s"' % kv for kv in at)))
    text = "\n".join(zeilen) + "\n"

    print("%d Typen mit frischen Bausteinen, davon %d gesichert, %d verworfen"
          % (len(daten), len(sicher), len(unsicher)))
    if ziel:
        ziel.write_bytes(text.encode("utf-8"))
        print("geschrieben: %s (%d Bytes)" % (ziel, len(text.encode("utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
