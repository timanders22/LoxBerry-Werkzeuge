# -*- coding: utf-8 -*-
"""Versionsstand des Arbeitsordners sichern und zurueckholen - nur lokal, kein Remote.

Aufruf:
    python Werkzeuge/stand_sichern.py                     Stand sichern (Commit mit Datum und Zusammenfassung)
    python Werkzeuge/stand_sichern.py "Intercom 2.2.6"    Stand sichern mit eigenem Stichwort
    python Werkzeuge/stand_sichern.py --lage              Was hat sich seit dem letzten Stand geaendert? (nichts wird geschrieben)
    python Werkzeuge/stand_sichern.py --verlauf DATEI     Alle Staende, in denen DATEI anders war
    python Werkzeuge/stand_sichern.py --zurueck DATEI [STAND]
                                                          DATEI aus dem letzten (oder dem genannten) Stand als
                                                          DATEI.aus-stand-<kurz> daneben legen - NIE ueberschreiben

Anlass (03.09.2026): ein Skript hat vier Regeldateien um 338 000 Zeichen abgeschnitten. Gerettet
hat sie eine zufaellig vorhandene Kopie. Das soll kein Zufall mehr sein: jede Sitzung endet mit
diesem Aufruf (VORLAGE_Sitzungsuebergabe.md, Abschnitt 1), und jeder Schnitt ist danach ein
--zurueck, keine Rettungsaktion.

Was im Stand liegt und was nicht, sagt .gitignore im Arbeitsordner: Regeln, Stand, Werkzeuge,
Vorlagen, Notizen, Dokumente drin; Plugin-Ordner (eigene Repositories), Projektdateien, Archive,
Pruefstaende mit Zugangsdaten und Zugangsdaten-Dateien draussen.

Grundsaetze: kein Remote (das Werkzeug legt keines an und schiebt nichts); core.autocrlf=false und
core.fileMode=false, damit Git keine Zeilenenden und keine Rechte umschreibt (Regeln/11, Abschnitt
6); --zurueck ueberschreibt nie, es legt daneben - der Vergleich und das Ersetzen bleiben Handarbeit.

Rueckgabewert: 0 in Ordnung, 1 nichts zu sichern / nichts gefunden, 2 Fehler.
"""
import datetime
import os
import subprocess
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.dirname(HIER)


def git(*args, ok=(0,)):
    p = subprocess.run(["git"] + list(args), cwd=WURZEL, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode not in ok:
        sys.stderr.write("git %s: %s\n" % (" ".join(args), p.stderr.strip()))
        sys.exit(2)
    return p.stdout


def repo_pruefen():
    if not os.path.isdir(os.path.join(WURZEL, ".git")):
        sys.stderr.write("Kein Versionsstand unter %s - zuerst einrichten (git init, .gitignore).\n" % WURZEL)
        sys.exit(2)
    for k, soll in (("core.autocrlf", "false"), ("core.fileMode", "false")):
        ist = git("config", "--get", k, ok=(0, 1)).strip()
        if ist != soll:
            git("config", k, soll)
    remotes = git("remote").strip()
    if remotes:
        sys.stderr.write("ACHTUNG: dieses Repository hat ein Remote (%s). Vorgesehen ist keines.\n" % remotes.replace("\n", ", "))


def lage():
    aus = git("status", "--porcelain", "-uall")
    zeilen = [z for z in aus.splitlines() if z.strip()]
    letzter = git("log", "-1", "--format=%h  %s", ok=(0, 128)).strip()
    print("Letzter Stand: %s" % (letzter or "keiner"))
    if not zeilen:
        print("Seitdem nichts geaendert.")
        return []
    neu = [z[3:] for z in zeilen if z[:2].strip() in ("??", "A")]
    geaendert = [z[3:] for z in zeilen if z[:2].strip() in ("M", "MM", "AM")]
    weg = [z[3:] for z in zeilen if "D" in z[:2]]
    sonst = [z for z in zeilen if z[3:] not in neu + geaendert + weg]
    for titel, liste in (("neu", neu), ("geaendert", geaendert), ("entfernt", weg), ("sonstiges", sonst)):
        if liste:
            print("  %-10s %d" % (titel + ":", len(liste)))
            for d in liste[:40]:
                print("     %s" % d)
            if len(liste) > 40:
                print("     ... und %d weitere" % (len(liste) - 40))
    return zeilen


def sichern(stichwort):
    zeilen = lage()
    if not zeilen:
        return 1
    git("add", "-A")
    n_neu = sum(1 for z in zeilen if z[:2].strip() in ("??", "A"))
    n_ge = sum(1 for z in zeilen if "M" in z[:2])
    n_weg = sum(1 for z in zeilen if "D" in z[:2])
    stempel = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    text = "%s - %s (%d neu, %d geaendert, %d entfernt)" % (stempel, stichwort or "Stand gesichert", n_neu, n_ge, n_weg)
    git("commit", "-q", "-m", text)
    kurz = git("rev-parse", "--short", "HEAD").strip()
    print("Gesichert als %s: %s" % (kurz, text))
    return 0


def verlauf(datei):
    aus = git("log", "--format=%h  %s", "--", datei)
    if not aus.strip():
        print("Kein Stand enthaelt %s." % datei)
        return 1
    print(aus.rstrip())
    return 0


def zurueck(datei, stand):
    stand = stand or "HEAD"
    inhalt = subprocess.run(["git", "show", "%s:%s" % (stand, datei.replace(os.sep, "/"))], cwd=WURZEL, capture_output=True)
    if inhalt.returncode != 0:
        sys.stderr.write("%s gibt es im Stand %s nicht: %s\n" % (datei, stand, inhalt.stderr.decode("utf-8", "replace").strip()))
        return 1
    kurz = git("rev-parse", "--short", stand).strip()
    ziel = os.path.join(WURZEL, datei + ".aus-stand-" + kurz)
    if os.path.exists(ziel):
        sys.stderr.write("%s liegt schon da - nichts ueberschrieben.\n" % ziel)
        return 2
    with open(ziel, "wb") as f:
        f.write(inhalt.stdout)
    jetzt = os.path.join(WURZEL, datei)
    print("Zurueckgeholt nach %s (%d Byte)." % (ziel, len(inhalt.stdout)))
    if os.path.isfile(jetzt):
        print("Die heutige Datei hat %d Byte. Vergleichen, dann von Hand ersetzen - dieses Werkzeug ueberschreibt nicht." % os.path.getsize(jetzt))
    return 0


def main(argv):
    repo_pruefen()
    if "--lage" in argv:
        return 0 if lage() is not None else 2
    if "--verlauf" in argv:
        i = argv.index("--verlauf")
        return verlauf(argv[i + 1]) if i + 1 < len(argv) else 2
    if "--zurueck" in argv:
        i = argv.index("--zurueck")
        if i + 1 >= len(argv):
            print(__doc__); return 2
        return zurueck(argv[i + 1], argv[i + 2] if i + 2 < len(argv) else None)
    stichwort = " ".join(a for a in argv if not a.startswith("--"))
    return sichern(stichwort)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
