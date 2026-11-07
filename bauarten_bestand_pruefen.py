# -*- coding: utf-8 -*-
"""Sucht im Bestand die drei Bauarten, die an Ultraschall 1.2.6 aufgefallen sind.

Anlass (13.09.2026): die Durchsicht von Ultraschall fand drei Dinge, die
keine Eigenart dieser Linie sind - die Linien sind aus denselben Geruesten
gewachsen. Beschrieben in Regeln/02 (Zeitstempel, Eichung), Regeln/03
(Fassungskonstante, tote Inoden) und der Uebergabe
Stand-Protokolle/2026-09-13_Ultraschall_1.2.6.md.

Aufruf:  python3 Werkzeuge/bauarten_bestand_pruefen.py

Rein lesend, je Linie die HOECHSTE Fassung (sonst meldet man behobene Fehler
als offene). Jeder Fund ist ein KANDIDAT - ein Muster im Quelltext, kein
gemessener Fehler.

A  Fassungsnummer als Konstante im Quelltext, die von plugin.cfg abweicht.
B  Tote-Inode-Befund halb behoben: WatchedFileHandler da, aber ein Startweg
   leitet weiter in DIESELBE Protokolldatei.
C  Zeitstempel im Kopf der geschriebenen Konfiguration - macht
   wirkungstest.py zufaellig rot.
"""
import os
import re
from pathlib import Path

# Arbeitsordner: der Elternordner von Werkzeuge/, uebersteuerbar mit LOXWERK.
ARBEIT = Path(os.environ.get('LOXWERK') or Path(os.path.abspath(__file__)).parent.parent)


def nummer(name):
    return tuple(int(x) for x in re.findall(r"\d+", name)) or (0,)


def hoechste():
    linien = {}
    for e in ARBEIT.iterdir():
        if not e.is_dir() or not e.name.startswith("LoxBerry-Plugin-"):
            continue
        if not (e / "plugin.cfg").is_file():
            continue
        rumpf = re.sub(r"-\d+(\.\d+)*$", "", e.name)
        if rumpf not in linien or nummer(e.name) > nummer(linien[rumpf].name):
            linien[rumpf] = e
    return dict(sorted(linien.items()))


def cfg_fassung(ordner):
    for z in (ordner / "plugin.cfg").read_bytes().decode("utf-8", "replace").splitlines():
        if z.strip().startswith("VERSION="):
            return z.split("=", 1)[1].strip()
    return ""


def text(p):
    try:
        return p.read_bytes().decode("utf-8", "replace")
    except OSError:
        return ""


a, b, c = [], [], []
linien = hoechste()
for rumpf, o in linien.items():
    soll = cfg_fassung(o)

    # --- A: eingetragene Fassungskonstante -------------------------------
    for datei in sorted(set(o.glob("bin/**/*.py"))):
        for m in re.finditer(r'^\s*(VERSION|__version__|FASSUNG)\s*=\s*[\'"]([0-9][0-9.]*)[\'"]',
                             text(datei), re.M):
            if m.group(2) != soll:
                a.append("%-44s %s:%s = %r, plugin.cfg %s"
                         % (o.name, datei.relative_to(o).as_posix(),
                            m.group(1), m.group(2), soll))

    # --- B: Handler da, Umleitung noch in dieselbe Datei ------------------
    hat_handler = any("WatchedFileHandler" in text(p) for p in o.glob("bin/*.py"))
    if hat_handler:
        wege = []
        for p in list(o.glob("daemon/*")) + list(o.glob("cron/*")) \
                + list(o.glob("*.sh")) + list(o.glob("webfrontend/**/*.php")):
            if not p.is_file():
                continue
            for zeile in text(p).splitlines():
                if "nohup" not in zeile or zeile.lstrip().startswith(("#", "*", "//")):
                    continue
                if ">>" in zeile and "_start.log" not in zeile:
                    wege.append(p.relative_to(o).as_posix())
                    break
        if wege:
            b.append("%-44s %s" % (o.name, ", ".join(sorted(set(wege)))))

    # --- C: Zeitstempel im Konfigurationskopf -----------------------------
    for p in o.glob("webfrontend/**/*.php"):
        t = text(p)
        for m in re.finditer(r"^.*date\('[dmYHis:. ]+'\).*$", t, re.M):
            zeile = m.group(0)
            if zeile.lstrip().startswith(("*", "//", "#")):
                continue
            # ENG: nur, wo der Zeitstempel in den Text wandert, der als
            # KONFIGURATION geschrieben wird. Die breite Suche fand 23
            # Linien, davon 21 mit date() in einem Vorlagen-Kommentar oder
            # in einer Protokollzeile - das Muster gemessen, nicht die
            # Aussage.
            if not re.search(r"\$(t|txt|kopf|inhalt)\s*\.?=", zeile):
                continue
            if "comment" in zeile or "Address=" in zeile:
                continue
            if True:
                c.append("%-44s %s: %s"
                         % (o.name, p.relative_to(o).as_posix(), zeile.strip()[:70]))
                break

print("== %d Linien angesehen (je hoechste Fassung) ==" % len(linien))
for titel, liste in (("A  Fassungskonstante weicht von plugin.cfg ab", a),
                     ("B  Handler da, Startweg leitet weiter ins Protokoll", b),
                     ("C  Zeitstempel im Kopf der Konfiguration", c)):
    print()
    print("%s  -  %d Fund(e)" % (titel, len(liste)))
    for z in liste:
        print("   " + z)
print()
print("Ein Kandidat ist ein Muster im Quelltext, kein gemessener Fehler.")
