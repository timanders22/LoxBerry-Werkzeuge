#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schreibt den Zustand aller zustandshaltenden Bausteine ab und vergleicht ihn.

WARUM ES DIESES WERKZEUG GIBT
-----------------------------
Am 06.09.2026 setzte ein Programm-Upload (mit Firmware-Wechsel auf 17.2.8.28)
JEDEN eingeschalteten Schalter der Anlage auf aus. Gemessen an sieben
Schaltern, fuer die ein Vorwert vorlag:

    Beschattung zyklisch scharfstellen   1 -> 0
    Frostsicherung                       1 -> 0
    Pilot Beschattung (EG Flur)          1 -> 0
    die vier uebrigen (Wert 0)           0 -> 0

`Remanence Inv="true"` am `PushButton` schuetzt davor nicht. Und es gibt keine
Rettung im Nachhinein: von 142 `PushButton` der Anlage fuehrt KEINER eine
Statistik, und `control_history` ueberlebt den Neustart ohnehin nicht. Wer den
Zustand nicht vorher abgeschrieben hat, hat ihn verloren.

Schon am 05.09.2026 traf es den Zaehler `c1ea0711-171c`: 211 -> 1, eine Woche
Messung weg. Siehe Regeln/08 und die Erinnerung "Remanenz ueberlebt keinen
Upload".

AUFRUF
------
    schalterstand.py <DATEI.Loxone> --liste [--ziel liste.json]
        Liest die zustandshaltenden Bausteine aus der Projektdatei und
        schreibt sie als JSON. Rein lesend an der Projektdatei.

    schalterstand.py --vergleichen ALT.json NEU.json [--markdown BERICHT.md]
        Vergleicht zwei Zustandsabzuege. Rueckgabewert 0 = gleich,
        1 = Unterschiede, 2 = Fehler.

ZUSTANDSDATEI
-------------
    {"zeitpunkt": "2026-09-06 12:00:00",
     "quelle": "wie erhoben",
     "zustaende": {"<uuid>": {"titel": "...", "typ": "PushButton", "wert": 1}}}

Der Abzug selbst wird NICHT von diesem Werkzeug geholt: die Zustaende stehen
weder in der Projektdatei noch in der Strukturdatei `LoxAPP3.json`, sondern
nur am laufenden Miniserver. Wer sie erhebt (Claude ueber das Loxone-MCP, ein
eigenes Skript ueber die Weboberflaeche), schreibt sie in dieses Format.
`--liste` liefert dafuer die Bausteinliste.
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Bausteintypen, die einen von Hand oder ueber Logik gesetzten Zustand halten
# und ihn bei einem Upload verlieren koennen. Am 06.09.2026 in der Anlage
# gezaehlt: PushButton 142, Memory 153, AMemory 44, Mode 26, Counter 4,
# Radio 3, Switch2Button 3.
TYPEN = ("PushButton", "Radio", "Radio2", "Switch2Button", "PushButton2",
         "PushButtonSel", "StepSel", "MultiFuncSW",
         "Memory", "AMemory", "Counter")

C_ZEILE = re.compile(r'<C Type="([^"]*)"')
ATTR_U = re.compile(r'\bU="([^"]*)"')
ATTR_T = re.compile(r'\bTitle="([^"]*)"')
ATTR_D = re.compile(r'\bDesc="([^"]*)"')


def bausteine(pfad, typen=TYPEN):
    """[(uuid, titel, typ)] aller zustandshaltenden Bausteine der Datei."""
    roh = Path(pfad).read_bytes()
    if roh[:3] != b"\xef\xbb\xbf":
        raise SystemExit("BOM fehlt: %s ist keine Loxone-Projektdatei" % pfad)
    z = roh.decode("utf-8-sig").split("\r\n")
    raus = []
    for x in z:
        s = x.strip()
        if not s.startswith("<C Type="):
            continue
        typ = C_ZEILE.match(s).group(1)
        if typ not in typen:
            continue
        u = ATTR_U.search(s)
        if not u:
            continue
        t = ATTR_T.search(s)
        d = ATTR_D.search(s)
        raus.append((u.group(1),
                     (d or t).group(1) if (d or t) else "",
                     typ))
    return raus


def laden(pfad):
    d = json.loads(Path(pfad).read_text(encoding="utf-8"))
    if "zustaende" not in d:
        raise SystemExit("%s ist keine Zustandsdatei (Schluessel 'zustaende' fehlt)" % pfad)
    return d


def vergleichen(alt, neu):
    """(verloren, gewonnen, geaendert, unveraendert, nur_alt, nur_neu)"""
    a, b = alt["zustaende"], neu["zustaende"]
    gemeinsam = set(a) & set(b)
    verloren, gewonnen, geaendert, gleich = [], [], [], 0
    for u in sorted(gemeinsam, key=lambda u: a[u].get("titel", "")):
        wa, wb = a[u].get("wert"), b[u].get("wert")
        if wa == wb:
            gleich += 1
            continue
        eintrag = (a[u].get("titel", "?"), a[u].get("typ", "?"), u, wa, wb)
        if wa == 1 and wb == 0:
            verloren.append(eintrag)
        elif wa == 0 and wb == 1:
            gewonnen.append(eintrag)
        else:
            geaendert.append(eintrag)
    return (verloren, gewonnen, geaendert, gleich,
            sorted(set(a) - set(b)), sorted(set(b) - set(a)))


def bericht(alt, neu, apfad, bpfad):
    verloren, gewonnen, geaendert, gleich, nur_a, nur_b = vergleichen(alt, neu)
    z = ["# Schalterstand: Vergleich zweier Abzuege", ""]
    z.append("| | Zeitpunkt | Bausteine |")
    z.append("|---|---|---|")
    z.append("| ALT | %s | %d |" % (alt.get("zeitpunkt", "?"), len(alt["zustaende"])))
    z.append("| NEU | %s | %d |" % (neu.get("zeitpunkt", "?"), len(neu["zustaende"])))
    z.append("")

    # Erst pruefen, ob die Menge leer ist - sonst misst man sein eigenes
    # Schweigen (Regeln: jede Pruefzeile, die ueber eine Menge urteilt).
    if not alt["zustaende"] or not neu["zustaende"]:
        z.append("**Einer der Abzuege ist leer — es wurde nichts verglichen.**")
        return "\n".join(z) + "\n", 2

    if verloren:
        z.append("## AUSGESCHALTET — war an, ist jetzt aus (%d)" % len(verloren))
        z.append("")
        z.append("| Baustein | Typ | UUID |")
        z.append("|---|---|---|")
        for t, ty, u, _, _ in verloren:
            z.append("| **%s** | %s | `%s` |" % (t, ty, u))
        z.append("")
    if gewonnen:
        z.append("## Eingeschaltet — war aus, ist jetzt an (%d)" % len(gewonnen))
        z.append("")
        for t, ty, u, _, _ in gewonnen:
            z.append("- %s [%s]  `%s`" % (t, ty, u))
        z.append("")
    if geaendert:
        z.append("## Wert geaendert (%d)" % len(geaendert))
        z.append("")
        z.append("| Baustein | Typ | ALT | NEU |")
        z.append("|---|---|---|---|")
        for t, ty, u, wa, wb in geaendert:
            z.append("| %s | %s | %s | %s |" % (t, ty, wa, wb))
        z.append("")
    if nur_a or nur_b:
        z.append("## Nur in einem Abzug")
        z.append("")
        for u in nur_a:
            z.append("- nur ALT: %s  `%s`" % (alt["zustaende"][u].get("titel", "?"), u))
        for u in nur_b:
            z.append("- nur NEU: %s  `%s`" % (neu["zustaende"][u].get("titel", "?"), u))
        z.append("")

    n = len(verloren) + len(gewonnen) + len(geaendert) + len(nur_a) + len(nur_b)
    z.append("Unveraendert: %d. Unterschiede: %d." % (gleich, n))
    if verloren:
        z.append("")
        z.append("**%d Baustein(e) waren an und sind jetzt aus.** Das ist das "
                 "Schadensbild eines Uploads (Regeln/08). Wieder einschalten." % len(verloren))
    return "\n".join(z) + "\n", (1 if n else 0)


def main(argv):
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("datei", nargs="?")
    p.add_argument("--liste", action="store_true")
    p.add_argument("--ziel")
    p.add_argument("--vergleichen", nargs=2, metavar=("ALT", "NEU"))
    p.add_argument("--markdown")
    p.add_argument("--hilfe", "-h", action="store_true")
    a = p.parse_args(argv)

    if a.hilfe or (not a.liste and not a.vergleichen):
        print(__doc__)
        return 2

    if a.vergleichen:
        alt, neu = laden(a.vergleichen[0]), laden(a.vergleichen[1])
        text, rc = bericht(alt, neu, *a.vergleichen)
        if a.markdown:
            Path(a.markdown).write_text(text, encoding="utf-8")
            print("geschrieben: %s" % a.markdown)
        print(text)
        return rc

    if not a.datei:
        print("Ohne Projektdatei keine Liste.")
        return 2
    bs = bausteine(a.datei)
    if not bs:
        print("KEIN zustandshaltender Baustein gefunden — das ist ein Messfehler, "
              "kein Ergebnis. Erwartet werden Typen: %s" % ", ".join(TYPEN))
        return 2
    daten = {"quelle": Path(a.datei).name,
             "erzeugt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "bausteine": [{"uuid": u, "titel": t, "typ": ty} for u, t, ty in bs]}
    if a.ziel:
        Path(a.ziel).write_text(json.dumps(daten, ensure_ascii=False, indent=1),
                                encoding="utf-8")
        print("geschrieben: %s" % a.ziel)
    zahl = {}
    for _, _, ty in bs:
        zahl[ty] = zahl.get(ty, 0) + 1
    print("%d zustandshaltende Bausteine in %s" % (len(bs), Path(a.datei).name))
    for ty in sorted(zahl, key=lambda k: -zahl[k]):
        print("   %-16s %4d" % (ty, zahl[ty]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
