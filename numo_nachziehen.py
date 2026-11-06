#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zieht das NumO im Kopf der Projektdatei auf die Zahl der Bausteine nach.

WARUM ES DIESES WERKZEUG GIBT
-----------------------------
Config fuehrt am `<C Type="Document">` ein Attribut `NumO` mit, das die
`<C>`-Bausteine der Datei zaehlt. Wer Bausteine mit einem Skript einfuegt,
muss diese Zahl mitziehen - sonst steht im Kopf eine andere Zahl als im Rumpf.

Am 27.08.2026 am gesamten Bestand geeicht: in allen 100 aus Config
gespeicherten Fassungen stimmte NumO, in allen 61 skriptgebauten stand es
still. Seither ist das Punkt 11 der Pruefkette (REGELN_3 A2), und dieses
Werkzeug ist die Gegenseite dazu: es macht den Punkt gruen, statt ihn zu
umgehen.

NICHT GEMESSEN ist, ob der Miniserver NumO ueberhaupt liest. Bisher hat Config
die Zahl beim Speichern stillschweigend berichtigt, und die Datei geht nie
ohne Config an die Anlage. Das Werkzeug haelt die Datei in sich stimmig - mehr
behauptet es nicht.

NICHT ANGEFASST wird `NextObj` in der `<ControlList>`-Zeile. Config zaehlt das
ebenfalls hoch, aber wonach genau, ist nicht gemessen - und was ich nicht
gemessen habe, schreibe ich nicht.

BYTEWEISE
---------
Geaendert werden ausschliesslich die Ziffern hinter `NumO="`. BOM, CRLF und
die Zahl der einzelnen LF werden vorher und nachher gezaehlt; weicht eine der
drei Zahlen ab, wird nichts geschrieben.

Aufruf:  numo_nachziehen.py <projektdatei> [--schreiben]
         Ohne --schreiben wird nur berichtet. Rueckgabewert 0 = stimmt
         bereits, 1 = muesste nachgezogen werden (bzw. wurde es), 2 = Fehler.
"""

import re
import sys
from pathlib import Path

BOM = b"\xef\xbb\xbf"
CRLF = b"\r\n"
KOPF = re.compile(r'(<C Type="Document"[^>]*?\bNumO=")(\d+)(")')


def kennzahlen(roh: bytes):
    return (roh[:3] == BOM, roh.count(CRLF), roh.count(b"\n") - roh.count(CRLF))


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    datei = Path(sys.argv[1])
    schreiben = "--schreiben" in sys.argv[2:]
    if not datei.is_file():
        print("Keine Datei: %s" % datei)
        return 2

    roh = datei.read_bytes()
    hat_bom, crlf, lf = kennzahlen(roh)
    if not hat_bom:
        print("[FEHL] Kein BOM - das ist keine Loxone-Projektdatei, wie sie hier "
              "gepflegt wird.")
        return 2
    s = roh.decode("utf-8-sig")

    treffer = KOPF.findall(s)
    if len(treffer) != 1:
        print("[FEHL] NumO am Document: %d Fundstellen, erwartet genau eine."
              % len(treffer))
        return 2
    steht = int(treffer[0][1])
    anzahl = len(re.findall(r"<C[ >]", s))

    print("%s" % datei.name)
    print("   NumO im Kopf     : %d" % steht)
    print("   <C>-Bausteine    : %d" % anzahl)

    if steht == anzahl:
        print("   stimmt bereits - nichts zu tun.")
        return 0

    if not schreiben:
        print("   [FEHL] Abweichung %+d. Mit --schreiben wird es nachgezogen."
              % (anzahl - steht))
        return 1

    neu_s = KOPF.sub(lambda m: m.group(1) + str(anzahl) + m.group(3), s, count=1)
    neu = BOM + neu_s.encode("utf-8")

    hat_bom2, crlf2, lf2 = kennzahlen(neu)
    if (hat_bom2, crlf2, lf2) != (True, crlf, lf):
        print("   [FEHL] Kodierung haette sich veraendert (BOM %s, CRLF %d, "
              "einzelne LF %d) - es wird nichts geschrieben."
              % (hat_bom2, crlf2, lf2))
        return 2
    # Ausser den Ziffern darf sich nichts geruehrt haben.
    if len(neu) - len(roh) != len(str(anzahl)) - len(str(steht)):
        print("   [FEHL] Mehr als die Ziffern haetten sich geaendert - es wird "
              "nichts geschrieben.")
        return 2

    datei.write_bytes(neu)
    print("   nachgezogen: %d -> %d  (%d Bytes, %+d)"
          % (steht, anzahl, len(neu), len(neu) - len(roh)))
    return 1


if __name__ == "__main__":
    sys.exit(main())
