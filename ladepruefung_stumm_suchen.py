#!/usr/bin/env python3
"""Welche Installationsskripte werfen Pythons Meldung weg?

WARUM ES DIESES WERKZEUG GIBT
=============================
Regeln/06 seit 12.09.2026 (Anlass Anker SOLIX 0.9.14): eine Ladepruefung, die
Pythons Meldung nach /dev/null schickt, verschweigt die Ursache. Im
Installationsprotokoll steht, DASS es nicht geht, nirgends WARUM - und `pip`
meldet auch dann Erfolg, wenn keine einzige Abhaengigkeit mitgekommen ist.
Erst der Ladeversuch beantwortet die Frage, und nur SEINE Meldung nennt das
fehlende Paket beim Namen.

An der Sprachsteuerung 0.11.5 (13.09.2026) stand dieselbe Bauart dreimal.
Dieses Werkzeug sucht sie ueber den ganzen Bestand: wer einen Befund behebt,
sucht alle Stellen derselben Bauart.

WAS ES MISST UND WAS NICHT
==========================
Es liest Text, es fuehrt nichts aus. Jeder Fund ist ein **Kandidat**, kein
gemessener Fehler - ob die Meldung im Protokoll fehlt, zeigt erst eine
Installation. Gesucht wird in den Hakenskripten und allem, was sie aufrufen:

  a) ein **Tor**: `if ! <python> -c '...import...'`, dessen Scheitern zu einer
     Meldung fuehrt - und dessen Zeile die Fehlerausgabe verwirft
     (`2>/dev/null`, `2>&-`, `&>/dev/null`). NUR das ist der Befund.

     Nicht gemeldet werden **Proben**: eine Fassungsabfrage
     (`sys.version_info`, `importlib.metadata`) oder ein Wert, der in eine
     Variable geht und einen Ersatz hat (`|| echo unbekannt`). Sie verwerfen
     die Meldung mit Absicht - es gibt nichts zu sagen. Eine Pruefung, die
     bei jedem Lauf Fehlalarm gibt, ist eine abgeschaltete Pruefung.
  b) ein `pip install`, dessen Ausgabe verworfen wird UND dem kein
     Ladeversuch folgt,
  c) fehlendes `pip list` am Ende (die Fassungen der Pakete gehoeren ins
     Protokoll) - nur gemeldet, wenn die Linie ueberhaupt pip benutzt.

Gegenprobe eingebaut: findet der Lauf in KEINER Linie einen Aufruf, ist das
kein Ergebnis, sondern ein Suchfehler - dann bricht er mit Rueckgabewert 2 ab.

Aufruf:
    python3 Werkzeuge/ladepruefung_stumm_suchen.py [ORDNER ...]
    ohne Argument: alle LoxBerry-Plugin-* im Arbeitsordner
"""
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HIER = Path(__file__).resolve().parent
ARBEIT = HIER.parent

SKRIPTE = ("postinstall.sh", "preinstall.sh", "preupgrade.sh", "postupgrade.sh",
           "postroot.sh", "preroot.sh", "uninstall/uninstall")

STUMM = ("2>/dev/null", "2> /dev/null", "2>&-", "&>/dev/null", "&> /dev/null")


def linien(argv):
    if argv:
        return [Path(a) for a in argv]
    return sorted(p for p in ARBEIT.iterdir()
                  if p.is_dir() and p.name.startswith("LoxBerry-Plugin-")
                  and (p / "plugin.cfg").is_file())


def hoechste(pfade):
    """Je Linie nur die hoechste Fassung - sonst zaehlt man Dubletten."""
    aus = {}
    for p in pfade:
        stamm = re.sub(r"-\d+(\.\d+)*$", "", p.name)
        sch = [int(x) if x.isdigit() else 0
               for x in p.name[len(stamm) + 1:].split(".")]
        if stamm not in aus or sch > aus[stamm][0]:
            aus[stamm] = (sch, p)
    return [v[1] for _k, v in sorted(aus.items())]


def ist_probe(zeile):
    """Verwirft diese Zeile die Meldung mit Absicht?

    Eine Fassungsabfrage hat keine Meldung, die jemandem hilft, und ein Wert
    mit Ersatzwert faengt sein Scheitern selbst ab. Beides ist kein Befund -
    und wer es meldet, macht die Pruefung wertlos.
    """
    z = zeile.strip()
    if "sys.version_info" in z or "importlib.metadata" in z:
        return True
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=\$\(", z):        # WERT=$(python3 -c …)
        return True
    if "|| echo" in z or "||echo" in z:
        return True
    return False


def pruefen(ordner):
    """(Ladeversuche, stumme Tore, pip-Zeilen ohne Ladeversuch, pip_list_fehlt)."""
    lade, stumm, pip_stumm = [], [], []
    hat_pip = False
    hat_pip_list = False
    for name in SKRIPTE:
        datei = ordner / name
        if not datei.is_file():
            continue
        try:
            text = datei.read_bytes().decode("utf-8", "replace")
        except OSError:
            continue
        zeilen = text.replace("\r\n", "\n").split("\n")
        for nr, z in enumerate(zeilen, 1):
            if "pip" in z and ("install" in z or " list" in z):
                hat_pip = True
                if re.search(r"pip[^|;]*\blist\b", z):
                    hat_pip_list = True
            # a) Ladeversuch: ein Python mit -c und einem import darin
            if re.search(r"python[0-9.]*[\"']?\s+-c\s+.{0,200}import", z):
                lade.append((name, nr, z.strip()))
                if any(s in z for s in STUMM) and not ist_probe(z):
                    stumm.append((name, nr, z.strip()[:110]))
            # b) pip install, dessen Ausgabe verworfen wird
            elif re.search(r"pip\s+install", z) and any(s in z for s in STUMM):
                pip_stumm.append((name, nr, z.strip()[:110]))
    return lade, stumm, pip_stumm, (hat_pip and not hat_pip_list)


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    ordner = hoechste(linien(argv))
    if not ordner:
        print("Keine Plugin-Ordner gefunden - nichts gemessen.")
        return 2

    lade_gesamt = 0
    betroffen = []
    ohne_liste = []
    print("%-46s %5s %6s %8s" % ("Linie", "Lade", "Tore", "pip stumm"))
    print("-" * 72)
    for o in ordner:
        lade, stumm, pip_stumm, fehlt_liste = pruefen(o)
        lade_gesamt += len(lade)
        if fehlt_liste:
            ohne_liste.append(o.name)
        if not (stumm or pip_stumm):
            continue
        betroffen.append((o, stumm, pip_stumm))
        print("%-46s %5d %6d %8d" % (o.name[:46], len(lade), len(stumm),
                                     len(pip_stumm)))
    print("-" * 72)
    print("%d Linien geprueft, %d Ladeversuche insgesamt gefunden."
          % (len(ordner), lade_gesamt))

    # Gegenprobe: kein einziger Aufruf ueber den ganzen Bestand waere kein
    # Ergebnis, sondern ein Suchfehler.
    if lade_gesamt == 0:
        print("[FEHL] Kein einziger Ladeversuch gefunden - das Muster greift "
              "nicht. Dieser Lauf hat nichts gemessen.")
        return 2

    if betroffen:
        print()
        print("KANDIDATEN - Fundstellen, kein gemessener Fehler:")
        for o, stumm, pip_stumm in betroffen:
            print("  %s" % o.name)
            for name, nr, z in stumm:
                print("    %s:%d  Tor ohne Meldung:  %s" % (name, nr, z))
            for name, nr, z in pip_stumm:
                print("    %s:%d  pip install stumm:  %s" % (name, nr, z))
    else:
        print("Kein stummes Tor im Bestand - alle stummen Zeilen sind Proben.")

    if ohne_liste:
        print()
        print("Nebenbefund - benutzen pip, schreiben aber kein 'pip list' ins "
              "Protokoll (%d):" % len(ohne_liste))
        for n in ohne_liste:
            print("    " + n)

    return 1 if betroffen else 0


if __name__ == "__main__":
    sys.exit(main())
