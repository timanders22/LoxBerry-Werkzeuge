#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sagt preupgrade.sh die Wahrheit darueber, ob es einen Dienst angehalten hat?

DER BEFUND, gegen den dieses Werkzeug steht
-------------------------------------------
Am 11.09.2026 meldete das Installationsprotokoll eines Upgrades „Laufender
Dienst angehalten." - der Dienst war aber gestoppt. Die Zeile stand
bedingungslos hinter dem stop-Aufruf; dessen Antwort („laeuft nicht") ging
nach /dev/null. Gemessen ueber den Bestand: dasselbe Muster in AnkerSolix
0.9.13, Bewaesserung 0.9.26, Dashboard 0.9.19 und Weissware 0.9.19. Alle
vier `anhalten()` geben ohne laufenden Dienst 0 zurueck - auch die Form
`if "$DIENST" stop; then echo ...` meldet also immer.

WAS GEMESSEN WIRD
-----------------
`preupgrade.sh` wird in einem Wegwerfbaum WIRKLICH ausgefuehrt: mit den sechs
Argumenten des Installers und einer Attrappe des Dienstskripts, deren
Antwort auf `status` man vorgibt. Kein LoxBerry, kein Dienst, kein Netz.

Zwei Laeufe je Ordner:

    lief NICHT -> keine Zeile darf behaupten, es sei etwas angehalten worden
    lief       -> genau das muss behauptet werden (Gegenprobe: eine Fassung,
                  die gar nichts mehr meldet, waere ebenso falsch)

Dazu in beiden Laeufen: `stop` muss gerufen worden sein (es raeumt auch den
Sollmerker ab), und das Skript muss mit 0 enden.

Der Meldungstext ist je Linie anders („angehalten", „ueber dienst.sh
angehalten", „(Sollmerker entfernt)"). Geprueft wird deshalb nicht auf einen
festen Satz, sondern auf die AUSSAGE: eine Zeile, die „angehalten", „gestoppt"
oder „beendet" sagt, ohne im selben Satz zu verneinen.

WAS ER NICHT MISST
------------------
Den echten Installer und die Wirkung des Anhaltens. Der Upgrade-Zweig selbst
ist am 11.09.2026 an einer Linie am Geraet gelaufen (BYD Autos 0.9.8 -> 0.9.9).

Aufruf:  preupgrade_meldung_pruefen.py <Plugin-Ordner> [<weiterer Ordner> ...]
Rueckgabe: 0 alles wie erwartet, 1 mindestens eine Pruefung nicht, 2 nichts
gemessen (keine bash, kein preupgrade.sh).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASH = shutil.which("bash")

# Die Attrappe des Dienstskripts. Sie merkt sich jeden Aufruf und richtet sich
# bei `status` danach, ob die Datei `laeuft` daneben liegt. `stop` antwortet
# wie die Vorbilder im Bestand: ohne laufenden Dienst „laeuft nicht“ und
# Rueckgabe 0 - genau daran scheitern die Meldungen.
ATTRAPPE = """#!/bin/sh
echo "$1" >> "$(dirname "$0")/aufrufe"
case "$1" in
  status) [ -f "$(dirname "$0")/laeuft" ] && { echo laeuft; exit 0; }; echo gestoppt; exit 1 ;;
  stop)   if [ -f "$(dirname "$0")/laeuft" ]; then rm -f "$(dirname "$0")/laeuft"; echo angehalten; else echo "laeuft nicht"; fi; exit 0 ;;
esac
exit 0
"""

BEHAUPTUNG = re.compile(r"angehalten|gestoppt|beendet", re.I)
VERNEINUNG = re.compile(r"\bnicht\b|\bkein\b|\bnichts\b", re.I)


def schalenpfad(p: Path) -> str:
    """Pfad in der Form, die bash versteht.

    Unter Windows wird aus „C:/x“ ein „/c/x“: mit dem Laufwerksbuchstaben
    liest das tar von Git-Bash „C:“ als Rechnernamen und bricht ab
    („Cannot connect to C: resolve failed“, gemessen 11.09.2026) - dann
    scheitert eine Sicherung im Skript, und der Pruefstand haelt das faelschlich
    fuer einen Befund am Plugin.
    """
    s = p.as_posix()
    if os.name == "nt" and len(s) > 1 and s[1] == ":":
        s = "/" + s[0].lower() + s[2:]
    return s


def ordnername(plugin: Path) -> str:
    """Den Installationsordner lesen, nicht raten: FOLDER aus plugin.cfg."""
    cfg = plugin / "plugin.cfg"
    if cfg.is_file():
        t = cfg.read_text(encoding="utf-8", errors="replace")
        for schluessel in ("FOLDER", "NAME"):
            m = re.search(r"^%s\s*=\s*(\S+)" % schluessel, t, re.M)
            if m:
                return m.group(1).strip()
    return plugin.name.replace("LoxBerry-Plugin-", "").split("-")[0].lower()


def dienstweg(preupgrade: Path, folder: str) -> str:
    """WO liegt das Skript, das preupgrade.sh zum Anhalten ruft?

    Aus dem Skript GELESEN statt angenommen - sonst liegt die Attrappe unter
    einem Namen, den niemand ruft, und der Lauf misst „kein Dienstskript da“.

    Im Bestand gibt es zwei Bauarten: das eigene Dienstskript unter
    `bin/plugins/<ordner>/<name>.sh` und den LoxBerry-Daemon unter
    `system/daemons/plugins/<ordner>` (so Midea2Lox 4.5.3). Wurde nur die erste
    gesucht, fiel die zweite mit drei roten Zeilen durch - ohne dass an der
    Linie etwas falsch war (gemessen 11.09.2026). Findet sich keine von beiden,
    kommt "" zurueck: dann ist der Prueffall hier nicht anwendbar.
    """
    t = preupgrade.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"bin/plugins/\$\{?(?:PFOLDER|ARGV3)\}?/([A-Za-z0-9_.-]+\.sh)", t)
    if m:
        return "bin/plugins/%s/%s" % (folder, m.group(1))
    # Dritte Bauart: der Pfad steht in einer VARIABLEN, und das Skript wird
    # spaeter ueber sie gerufen - PBIN="$BASE/bin/plugins/$PFOLDER", danach
    # "$PBIN/dienst.sh" stop. Das Muster oben verlangte beides in EINER Zeile
    # und meldete fuer diese Linien "NICHT ANWENDBAR", obwohl der Fall besteht:
    # ein Strich, wo eine Messung hingehoert. Gemessen am 15.09.2026 ueber den
    # ganzen Bestand: 19 Ordner in drei Linien (BYD Autos, Matter2Lox,
    # Spotpreis Tibber) fielen so durch die Pruefung.
    for name in re.findall(
            r"^\s*([A-Z_][A-Z0-9_]*)=\"?\$\{?\w+\}?/bin/plugins/"
            r"\$\{?(?:PFOLDER|ARGV3)\}?\"?\s*$", t, re.M):
        m = re.search(r'"\$\{?%s\}?/([A-Za-z0-9_.-]+\.sh)"' % re.escape(name), t)
        if m:
            return "bin/plugins/%s/%s" % (folder, m.group(1))
    if re.search(r"system/daemons/plugins/\$\{?(?:ARGV3|PFOLDER)\}?", t):
        return "system/daemons/plugins/%s" % folder
    return ""


def lauf(plugin: Path, laeuft: bool) -> dict:
    folder = ordnername(plugin)
    weg = dienstweg(plugin / "preupgrade.sh", folder)
    if not weg:
        return {"unanwendbar": True}
    hof = Path(tempfile.mkdtemp(prefix="preupg_"))
    try:
        for u in ("config/plugins/%s" % folder, "data/plugins/%s" % folder,
                  "bin/plugins/%s" % folder, "arbeit", "log/plugins/%s" % folder,
                  "config/system"):
            (hof / u).mkdir(parents=True, exist_ok=True)
        # config/system/general.json MUSS liegen: mehrere preupgrade-Skripte
        # pruefen daran, ob sie wirklich in einer LoxBerry-Wurzel stehen, und
        # beenden sonst mit exit 2, BEVOR sie irgendetwas tun (Bewaesserung
        # 0.9.26 tut das ausdruecklich). Ohne diese Datei misst der Pruefstand
        # seinen eigenen halb gebauten Hof - vier rote Zeilen, kein Befund.
        (hof / "config/system/general.json").write_text(
            '{"Mqtt":{"Brokerhost":"localhost","Brokerport":1883,'
            '"Udpinport":11884},"Base":{"Version":"4.0.0"}}\n')
        # Etwas Konfiguration, damit ein Sicherungsschritt etwas zu tun hat.
        for name in ("config.json", "%s.json" % folder, "zugang.json"):
            (hof / "config/plugins" / folder / name).write_text('{"a":1}\n')
        (hof / "data/plugins" / folder / "soll_laufen").write_text("")
        d = hof / weg
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_text(ATTRAPPE, newline="\n")
        d.chmod(0o755)
        if laeuft:
            (d.parent / "laeuft").write_text("1")
        else:
            # Ein Dienst, der nicht laufen soll, hat auch keinen Sollmerker.
            (hof / "data/plugins" / folder / "soll_laufen").unlink()
        skript = hof / "preupgrade.sh"
        shutil.copy(plugin / "preupgrade.sh", skript)
        e = subprocess.run(
            [BASH, str(skript), "KENNUNG123", plugin.name, folder, "9.9.9",
             schalenpfad(hof), schalenpfad(hof / "arbeit")],
            capture_output=True, text=True, timeout=120)
        aufrufe = d.parent / "aufrufe"
        return {"rc": e.returncode, "text": e.stdout + e.stderr,
                "aufrufe": aufrufe.read_text().split() if aufrufe.exists() else []}
    finally:
        shutil.rmtree(hof, ignore_errors=True)


def behauptungen(text: str) -> list:
    """Zeilen, die etwas angehalten haben WOLLEN, ohne zu verneinen."""
    return [z.strip() for z in text.splitlines()
            if BEHAUPTUNG.search(z) and not VERNEINUNG.search(z)]


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    if not BASH:
        print("[ -- ] Keine bash gefunden - NICHT GEMESSEN. Das ist kein Haken.")
        return 2
    fehler = 0
    gemessen = 0
    for arg in sys.argv[1:]:
        p = Path(arg).resolve()
        print("== %s ==" % p.name)
        if not (p / "preupgrade.sh").is_file():
            print("  [ -- ] kein preupgrade.sh - diese Linie hat den Fall nicht.")
            continue
        aus = lauf(p, False)
        an = lauf(p, True)
        if aus.get("unanwendbar"):
            print("  [ -- ] preupgrade.sh haelt keinen Dienst ueber ein Skript an -")
            print("         weder bin/plugins/<ordner>/*.sh noch")
            print("         system/daemons/plugins/<ordner>. NICHT ANWENDBAR.")
            print("         Ein Strich ist kein Haken und kein Kreuz.")
            continue
        gemessen += 1

        # Ein Abbruch VOR dem Anhalten ist kein Befund am Plugin, sondern eine
        # unvollstaendige Pruefbank. Kennzeichen: stop wurde nie gerufen und
        # das Skript endete mit einem Wert ungleich 0. Dann wird laut nichts
        # behauptet - lieber „nicht gemessen" als vier erfundene rote Zeilen.
        for name, e in (("ohne Dienst", aus), ("mit Dienst", an)):
            if "stop" not in e["aufrufe"] and e["rc"] != 0:
                print("  [ -- ] NICHT GEMESSEN (%s): das Skript brach mit %d ab, "
                      "bevor es anhielt." % (name, e["rc"]))
                zeilen = [z.strip() for z in e["text"].splitlines() if z.strip()]
                print("         %s" % (" | ".join(zeilen)[:200] or "(keine Ausgabe)"))
                print("         Das ist ein Befund an der Pruefbank, nicht am Plugin.")
                return_wert = True
                break
        else:
            return_wert = False
        if return_wert:
            continue

        b_aus, b_an = behauptungen(aus["text"]), behauptungen(an["text"])
        reihen = [
            ("lief NICHT: keine Behauptung, es sei etwas angehalten worden",
             not b_aus),
            ("lief NICHT: stop wurde trotzdem gerufen", "stop" in aus["aufrufe"]),
            ("lief: es wird gesagt, dass angehalten wurde", bool(b_an)),
            ("lief: stop wurde gerufen", "stop" in an["aufrufe"]),
            ("beide Laeufe enden mit 0", aus["rc"] == 0 and an["rc"] == 0),
        ]
        for titel, wahr in reihen:
            if not wahr:
                fehler += 1
            print("  [%s] %s" % ("ok " if wahr else "FEHL", titel))
        if b_aus:
            print("      ohne Dienst behauptet: %s" % " | ".join(b_aus)[:150])
        zeilen = [z.strip() for z in aus["text"].splitlines() if "Dienst" in z]
        print("      Meldungen ohne Dienst: %s" % (" | ".join(zeilen)[:150] or "(keine)"))
    print()
    if not gemessen:
        print("Nichts gemessen.")
        return 2
    print("Alle Pruefungen wie erwartet." if not fehler
          else "%d Pruefung(en) NICHT wie erwartet." % fehler)
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
