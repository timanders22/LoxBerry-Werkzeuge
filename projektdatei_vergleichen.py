# -*- coding: utf-8 -*-
"""Zwei Loxone-Projektdateien vergleichen: Bausteine, Verbindungen, Attribute.

Aufruf:
    python projektdatei_vergleichen.py <ALT.Loxone> <NEU.Loxone> [--geometrie] [--markdown DATEI]

Rein lesend. Schreibt nur, wenn --markdown DATEI angegeben ist, und dann nur dorthin.

Rueckgabewert: 0 = keine Unterschiede, 1 = Unterschiede gefunden, 2 = Fehler (Datei fehlt,
XML nicht lesbar).

Warum es dieses Werkzeug gibt (Regeln/08_projektdatei-bearbeiten.md, "Was Config beim
Oeffnen und Speichern still veraendert"): Loxone Config wirft beim Speichern Verbindungen
weg, berechnet WF selbst und schreibt Dinge um, die niemand angefasst hat - und meldet
dabei Erfolg. Ein Zeilen-Diff zweier 4-MB-Dateien zeigt das nicht lesbar. Dieses Werkzeug
sagt in Bausteinsprache, was zwischen zwei Fassungen anders ist:

  1. Bausteine, die nur in einer Fassung vorkommen (nach UUID).
  2. Bausteine, deren Attribute sich unterscheiden (Titel, Parameter, WF, on, ...).
  3. Verbindungen (<In Input=...> an einem <Co>), die nur in einer Fassung vorkommen -
     mit Quelle und Ziel in Klarnamen.
  4. Anschluss-Attribute (<Co ... Inv= Def= Nc=>), die sich unterscheiden.
  5. Innere Daten eines Bausteins (IoData, Display, StateText, ...), die sich unterscheiden.
  6. Kopfzeile (ControlList: Version, NextObj, NumO, Date des Document).

Lage (Px, Py, Px2, Py2) wird ohne --geometrie NICHT verglichen: eine verschobene Kachel
aendert das Verhalten nicht.

Eichung (02.09.2026, an zwei Fassungen der Hausdatei vom 30.08.2026, 00:15 und 00:22):
  - Datei gegen sich selbst: 0 Unterschiede, Rueckgabewert 0.
  - Eine <In>-Zeile aus einer Kopie entfernt: genau diese eine Verbindung als "nur in ALT"
    gemeldet, sonst nichts, Rueckgabewert 1.
  - Ein Title in einer Kopie geaendert: genau dieser Baustein als geaendert gemeldet.
  - Ein Display-Attribut geaendert: genau dieser Baustein unter "Innere Daten" gemeldet.
  - Ein ganzer UND-Baustein entfernt: 1 Baustein nur in ALT, seine drei Verbindungen nur in
    ALT, und in NEU eine TOTE VERBINDUNG (der Nachfolger zeigt auf den fehlenden Ausgang).
  - Eine Kachel verschoben (Px/Py): ohne --geometrie 0 Unterschiede, mit --geometrie 1.
  - Fehlende Datei: Rueckgabewert 2.
  - 0015 gegen 0022 (zwei echte Config-Speicherstaende): siehe Regeln/08, Abschnitt
    "Vor- und Nachfassung vergleichen".

Was das Werkzeug NICHT kann: es liest die Datei als XML. Dafuer muss sie wohlgeformt
sein; die doppelten Title-Attribute der ApiActor-Zeilen (Regeln/08, A6) werden vorher
entdoppelt wie in projektdatei_pruefkette.py. Es sagt nichts darueber, ob der Miniserver
die Datei geladen hat - dafuer ist miniserver_abgleich.py.
"""
import sys, re, io
import xml.etree.ElementTree as ET

CRLF = "\r\n"
GEOMETRIE = ("Px", "Py", "Px2", "Py2")
KOPF_ATTRIBUTE = ("Version", "LxAV", "NextObj", "NextConst", "NextNote", "NextMem")
DOKUMENT_ATTRIBUTE = ("Date", "DateS", "ConfigVersion", "NumO", "V")


def entdoppeln(zeile):
    """Zweites und weitere Title="..." in einer Zeile entfernen (ApiActor-Zeilen, A6)."""
    st = [m.start() for m in re.finditer(' Title="', zeile)]
    if len(st) < 2:
        return zeile
    for anf in reversed(st[1:]):
        ende = zeile.index('"', anf + 8) + 1
        zeile = zeile[:anf] + zeile[ende:]
    return zeile


def lesen(pfad):
    b = open(pfad, "rb").read()
    s = b.decode("utf-8-sig")
    zeilen = s.split(CRLF)
    ber = CRLF.join([entdoppeln(z) if 'Type="ApiActor"' in z else z for z in zeilen])
    wurzel = ET.fromstring(ber)
    return wurzel


def kanon(el):
    """Kanonische Textform eines Elements samt Kindern (ohne Co/In), fuer den Vergleich innerer Daten."""
    teile = [el.tag + "".join(" %s=%s" % (k, v) for k, v in sorted(el.attrib.items()))]
    for k in el:
        if k.tag in ("Co", "C"):
            continue
        teile.append(kanon(k))
    return "<" + "|".join(teile) + ">"


def sammeln(wurzel, geometrie):
    """Bausteine, Anschluesse, Verbindungen einer Datei einsammeln."""
    bausteine = {}   # U -> dict
    co_besitzer = {} # Co-U -> (Baustein-U, K)
    eltern = {}      # Baustein-U -> Titel des Elternbausteins (Seite/Kategorie)

    def gehe(el, elter_titel):
        for c in el:
            if c.tag != "C":
                continue
            u = c.get("U", "")
            attr = {k: v for k, v in c.attrib.items() if geometrie or k not in GEOMETRIE}
            anschl = {}
            for co in c:
                if co.tag != "Co":
                    continue
                k = co.get("K", "")
                cu = co.get("U", "")
                co_besitzer[cu] = (u, k)
                eing = [i.get("Input", "") for i in co if i.tag == "In"]
                a = {kk: vv for kk, vv in co.attrib.items() if kk not in ("K", "U")}
                anschl[k] = {"U": cu, "attr": a, "eingaenge": eing}
            bausteine[u] = {
                "Type": c.get("Type", ""), "Title": c.get("Title", ""), "attr": attr,
                "anschl": anschl, "innen": kanon(c), "elter": elter_titel,
            }
            gehe(c, c.get("Title", "") or elter_titel)
    gehe(wurzel, "")
    return bausteine, co_besitzer


def name(bausteine, u):
    b = bausteine.get(u)
    if not b:
        return "<unbekannt %s>" % u
    t = b["Title"] or "(ohne Titel)"
    return "%s [%s]" % (t, b["Type"])


def verbindungen(bausteine, co_besitzer):
    """Menge aller Verbindungen: (Quelle-Baustein-U, Quelle-K, Ziel-Baustein-U, Ziel-K)."""
    menge = set()
    for u, b in bausteine.items():
        for k, co in b["anschl"].items():
            for q in co["eingaenge"]:
                qb, qk = co_besitzer.get(q, ("", ""))
                menge.add((qb, qk, u, k, q))
    return menge


def vergleichen(alt, neu, geometrie):
    ba, coa = sammeln(alt, geometrie)
    bn, con = sammeln(neu, geometrie)
    bericht = {"kopf": [], "nur_alt": [], "nur_neu": [], "geaendert": [],
               "verb_nur_alt": [], "verb_nur_neu": [], "anschluss": [], "innen": []}

    # 6. Kopf
    for k in KOPF_ATTRIBUTE:
        if alt.get(k) != neu.get(k):
            bericht["kopf"].append(("ControlList " + k, alt.get(k), neu.get(k)))
    da = [c for c in alt if c.tag == "C" and c.get("Type") == "Document"]
    dn = [c for c in neu if c.tag == "C" and c.get("Type") == "Document"]
    if da and dn:
        for k in DOKUMENT_ATTRIBUTE:
            if da[0].get(k) != dn[0].get(k):
                bericht["kopf"].append(("Document " + k, da[0].get(k), dn[0].get(k)))

    # 1. Bausteine
    for u in ba:
        if u not in bn:
            bericht["nur_alt"].append((u, name(ba, u), ba[u]["elter"]))
    for u in bn:
        if u not in ba:
            bericht["nur_neu"].append((u, name(bn, u), bn[u]["elter"]))

    # 2. Attribute, 4. Anschluss-Attribute, 5. innere Daten
    for u in ba:
        if u not in bn:
            continue
        a, n = ba[u], bn[u]
        unterschiede = []
        for k in sorted(set(a["attr"]) | set(n["attr"])):
            if a["attr"].get(k) != n["attr"].get(k):
                unterschiede.append((k, a["attr"].get(k), n["attr"].get(k)))
        if unterschiede:
            bericht["geaendert"].append((u, name(ba, u), unterschiede))
        for k in sorted(set(a["anschl"]) | set(n["anschl"])):
            ca, cn = a["anschl"].get(k), n["anschl"].get(k)
            if ca is None or cn is None:
                bericht["anschluss"].append((u, name(ba, u), k, "Anschluss nur in " + ("ALT" if cn is None else "NEU"), None, None))
                continue
            for kk in sorted(set(ca["attr"]) | set(cn["attr"])):
                if ca["attr"].get(kk) != cn["attr"].get(kk):
                    bericht["anschluss"].append((u, name(ba, u), k, kk, ca["attr"].get(kk), cn["attr"].get(kk)))
        # Innere Daten: nur die Kinder (IoData, Display, ...), nicht die Attribute des <C> selbst
        if kanon_kinder(a) != kanon_kinder(n):
            bericht["innen"].append((u, name(ba, u)))

    # 3. Verbindungen
    va, vn = verbindungen(ba, coa), verbindungen(bn, con)
    for (qb, qk, zb, zk, q) in sorted(va - vn):
        bericht["verb_nur_alt"].append(verb_text(ba, qb, qk, zb, zk, q))
    for (qb, qk, zb, zk, q) in sorted(vn - va):
        bericht["verb_nur_neu"].append(verb_text(bn, qb, qk, zb, zk, q))
    zahlen = {"bausteine_alt": len(ba), "bausteine_neu": len(bn), "verb_alt": len(va), "verb_neu": len(vn)}
    return bericht, zahlen


def verb_text(bausteine, qb, qk, zb, zk, q):
    """Eine Verbindung in Klarnamen. Eine Quelle ohne Besitzer ist eine TOTE Verbindung:
    <In Input=...> zeigt auf einen Anschluss, den es in dieser Datei nicht gibt - genau das,
    was Config beim naechsten Speichern still verwirft (Regeln/08, B7e)."""
    if not qb:
        return "TOTE VERBINDUNG (Quelle %s fehlt)  ->  %s.%s" % (q, name(bausteine, zb), zk)
    return "%s.%s  ->  %s.%s" % (name(bausteine, qb), qk, name(bausteine, zb), zk)


def kanon_kinder(b):
    # innerer Kanon ohne die Attribute des <C> selbst: alles ab dem ersten "|"
    s = b["innen"]
    i = s.find("|")
    return s[i:] if i >= 0 else ""


def ausgeben(bericht, zahlen, pfad_alt, pfad_neu, out):
    w = out.write
    w("# Vergleich zweier Projektdateien\n\n")
    w("ALT: %s  (%d Bausteine, %d Verbindungen)\n" % (pfad_alt, zahlen["bausteine_alt"], zahlen["verb_alt"]))
    w("NEU: %s  (%d Bausteine, %d Verbindungen)\n\n" % (pfad_neu, zahlen["bausteine_neu"], zahlen["verb_neu"]))
    gesamt = sum(len(v) for v in bericht.values())
    if gesamt == 0:
        w("Keine Unterschiede (Lage der Kacheln nicht verglichen, ausser mit --geometrie).\n")
        return 0
    if bericht["kopf"]:
        w("## Kopfzeile\n\n| Feld | ALT | NEU |\n|---|---|---|\n")
        for k, a, n in bericht["kopf"]:
            w("| %s | %s | %s |\n" % (k, a, n))
        w("\n")
    if bericht["nur_alt"]:
        w("## Bausteine nur in ALT (%d) - in NEU verschwunden\n\n" % len(bericht["nur_alt"]))
        for u, nm, elter in bericht["nur_alt"]:
            w("- %s  (unter: %s)  `%s`\n" % (nm, elter, u))
        w("\n")
    if bericht["nur_neu"]:
        w("## Bausteine nur in NEU (%d) - neu hinzugekommen\n\n" % len(bericht["nur_neu"]))
        for u, nm, elter in bericht["nur_neu"]:
            w("- %s  (unter: %s)  `%s`\n" % (nm, elter, u))
        w("\n")
    if bericht["verb_nur_alt"]:
        w("## Verbindungen nur in ALT (%d) - in NEU weggefallen\n\n" % len(bericht["verb_nur_alt"]))
        for z in bericht["verb_nur_alt"]:
            w("- %s\n" % z)
        w("\n")
    if bericht["verb_nur_neu"]:
        w("## Verbindungen nur in NEU (%d) - neu gezogen\n\n" % len(bericht["verb_nur_neu"]))
        for z in bericht["verb_nur_neu"]:
            w("- %s\n" % z)
        w("\n")
    if bericht["geaendert"]:
        w("## Bausteine mit geaenderten Attributen (%d)\n\n" % len(bericht["geaendert"]))
        for u, nm, unt in bericht["geaendert"]:
            w("- %s  `%s`\n" % (nm, u))
            for k, a, n in unt:
                w("    - %s: %s  ->  %s\n" % (k, a if a is not None else "(fehlt)", n if n is not None else "(fehlt)"))
        w("\n")
    if bericht["anschluss"]:
        w("## Anschluss-Attribute geaendert (%d)\n\n| Baustein | Anschluss | Attribut | ALT | NEU |\n|---|---|---|---|---|\n" % len(bericht["anschluss"]))
        for u, nm, k, kk, a, n in bericht["anschluss"]:
            w("| %s | %s | %s | %s | %s |\n" % (nm, k, kk, a if a is not None else "(fehlt)", n if n is not None else "(fehlt)"))
        w("\n")
    if bericht["innen"]:
        w("## Innere Daten geaendert (%d) - IoData, Display, StateText, Perioden usw.\n\n" % len(bericht["innen"]))
        for u, nm in bericht["innen"]:
            w("- %s  `%s`\n" % (nm, u))
        w("\n")
    w("Summe: %d Unterschiede.\n" % gesamt)
    return 1


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    geometrie = "--geometrie" in argv
    md = None
    if "--markdown" in argv:
        i = argv.index("--markdown")
        if i + 1 >= len(argv):
            print("--markdown braucht einen Dateinamen"); return 2
        md = argv[i + 1]
        args = [a for a in args if a != md]
    if len(args) != 2:
        print(__doc__); return 2
    try:
        alt, neu = lesen(args[0]), lesen(args[1])
    except Exception as e:
        print("[FEHL] Datei nicht lesbar: %s" % e); return 2
    bericht, zahlen = vergleichen(alt, neu, geometrie)
    buf = io.StringIO()
    rc = ausgeben(bericht, zahlen, args[0], args[1], buf)
    text = buf.getvalue()
    sys.stdout.write(text)
    if md:
        with open(md, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
