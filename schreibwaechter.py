# -*- coding: utf-8 -*-
"""Schreibwaechter fuer Claude Code: lehnt Schreibvorgaenge ab, die etwas zerstoeren wuerden.

Wird von Claude Code als PreToolUse-Hook vor Write, Edit, MultiEdit und Bash gerufen
(.claude/settings.json im Arbeitsordner). Bekommt auf stdin das JSON des Werkzeugaufrufs,
antwortet mit Rueckgabewert 0 (durchlassen) oder 2 (abgelehnt; der Grund geht ueber stderr
an Claude zurueck und wird dort gelesen).

Anlass (03.09.2026): ein Skript hat beim Entfernen eines angehaengten Blocks die vier
REGELN-Dateien ab der Fundstelle bis zum Dateiende abgeschnitten - 338 000 Zeichen aus
spaeteren Sitzungen, still, ohne Groessenpruefung. Die Regel "Lesen -> bauen -> Anker
zaehlen -> schreiben" stand in CLAUDE.md; sie wurde nicht befolgt. Dieser Waechter macht
daraus etwas, das nicht vergessen werden kann.

Was abgelehnt wird:
  1. Jedes Schreiben, Aendern, Verschieben oder Loeschen unter GESCHUETZTEN Pfaden:
       Archiv/**, Stand-Protokolle/** (dort darf eine NEUE Datei entstehen, bestehende nicht
       geaendert werden), REGELN_*.md (wo auch immer), *.zip,
       *.Loxone (ausser Dateien, die juenger als eine Stunde sind - die baut gerade jemand),
       CLAUDE.md.vor-schichtung
  2. Jedes Write/Edit, das eine bestehende Datei um mehr als 20 % UND mehr als 2 000 Byte
     verkuerzt - es sei denn, im Arbeitsordner liegt die Marke `.kuerzen-erlaubt`
     (leere Datei; wer sie anlegt, hat entschieden, und entfernt sie danach wieder).
  3. Bash-Befehle, in denen ein geschuetzter Pfad zusammen mit einem schreibenden Operator
     vorkommt (>, >>, sed -i, rm, mv, del, rmdir, truncate, tee, cp/copy als Ziel).
     Lesen (cat, grep, diff, md5sum, python ... ohne Umleitung) geht durch.

Was NICHT abgefangen wird: Schreibvorgaenge aus Skripten, die Claude per Bash startet und
deren Ziel nicht im Befehl steht (python skript.py, das intern eine Datei kuerzt). Dafuer
gilt weiter die Regel - und die Marke: ein Skript, das kuerzen darf, wird mit der Marke
gefahren, sonst prueft es selbst die Groesse vorher und nachher.

Fail closed: kann der Waechter nicht pruefen (unlesbares JSON, unerwartete Form), lehnt er
ab und sagt warum - ein Waechter, der bei Zweifel schweigt, ist keiner (Regeln/01, Abschnitt 5).

Eichung: Werkzeuge/schreibwaechter_eichung.py (21 Faelle in beide Richtungen; 03.09.2026).
"""
import json
import os
import re
import sys
import time

SCHWELLE_ANTEIL = 0.20
SCHWELLE_BYTE = 2000
LOXONE_FRISCH_S = 3600
MARKE = ".kuerzen-erlaubt"

GESCHUETZT_ORDNER = ("Archiv", "Stand-Protokolle")
GESCHUETZT_NAMEN = ("CLAUDE.md.vor-schichtung",)
GESCHUETZT_MUSTER = (re.compile(r"(^|[\\/])REGELN_[^\\/]*\.md(\.vor-ablage)?$", re.I),
                     re.compile(r"\.zip$", re.I))


def projekt():
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def norm(p):
    p = p.replace("\\", "/")
    root = projekt().replace("\\", "/").rstrip("/")
    if p.lower().startswith(root.lower() + "/"):
        p = p[len(root) + 1:]
    return p


def geschuetzt(pfad):
    """Grund als Text, sonst None."""
    p = norm(pfad)
    teile = p.split("/")
    for o in GESCHUETZT_ORDNER:
        if teile and teile[0].lower() == o.lower():
            if o == "Stand-Protokolle":
                voll = pfad if os.path.isabs(pfad) else os.path.join(projekt(), pfad)
                if not os.path.exists(voll):
                    return None   # neue Uebergabe anlegen ist erlaubt; bestehende bleiben unveraendert
            return "liegt unter %s/ - dort wird nichts mehr geaendert" % o
    if teile and teile[-1] in GESCHUETZT_NAMEN:
        return "ist eine Sicherungskopie"
    for m in GESCHUETZT_MUSTER:
        if m.search(p):
            return "ist eine abgeloeste Regeldatei oder ein Archiv (%s)" % teile[-1]
    if p.lower().endswith(".loxone"):
        voll = pfad if os.path.isabs(pfad) else os.path.join(projekt(), pfad)
        if os.path.isfile(voll) and time.time() - os.path.getmtime(voll) > LOXONE_FRISCH_S:
            return "ist eine Projektdatei, aelter als eine Stunde - eine neue Fassung bekommt einen neuen Namen"
    return None


def groesse(pfad):
    voll = pfad if os.path.isabs(pfad) else os.path.join(projekt(), pfad)
    return os.path.getsize(voll) if os.path.isfile(voll) else None


def kuerzung(pfad, neu_bytes):
    alt = groesse(pfad)
    if alt is None or alt == 0:
        return None
    verlust = alt - neu_bytes
    if verlust > SCHWELLE_BYTE and verlust / alt > SCHWELLE_ANTEIL:
        if os.path.isfile(os.path.join(projekt(), MARKE)):
            return None
        return ("wuerde von %d auf %d Byte verkuerzt (%d Byte, %.0f %% weniger). "
                "Wenn das Absicht ist: Marke %s im Arbeitsordner anlegen, Vorgang wiederholen, Marke entfernen."
                % (alt, neu_bytes, verlust, 100.0 * verlust / alt, MARKE))
    return None


BASH_SCHREIBEND = re.compile(
    r"(>{1,2}|\bsed\s+-[a-zA-Z]*i|\brm\b|\bmv\b|\bdel\b|\brmdir\b|\btruncate\b|\btee\b|"
    r"\bcp\b|\bcopy\b|\bmove\b|\bren\b|\bRemove-Item\b|\bMove-Item\b|\bSet-Content\b|\bOut-File\b)")


def bash_pruefen(cmd):
    if not BASH_SCHREIBEND.search(cmd):
        return None
    # Alle Pfadartigen Token ansehen
    for tok in re.findall(r"[\w./\\:\-()]+", cmd):
        if len(tok) < 4:
            continue
        g = geschuetzt(tok)
        if g:
            return "Bash-Befehl schreibt, verschiebt oder loescht %s - %s" % (tok, g)
    return None


def main():
    try:
        daten = json.load(sys.stdin)
    except Exception as e:
        sys.stderr.write("SCHREIBWAECHTER: Aufruf nicht lesbar (%s) - abgelehnt, fail closed.\n" % e)
        return 2
    werkzeug = daten.get("tool_name", "")
    ein = daten.get("tool_input", {}) or {}
    gruende = []
    try:
        if werkzeug in ("Write", "Edit", "MultiEdit"):
            pfad = ein.get("file_path", "")
            if not pfad:
                gruende.append("kein file_path im Aufruf")
            else:
                g = geschuetzt(pfad)
                if g:
                    gruende.append("%s %s" % (norm(pfad), g))
                else:
                    alt = groesse(pfad)
                    if werkzeug == "Write":
                        neu = len((ein.get("content") or "").encode("utf-8"))
                    elif werkzeug == "Edit" and alt is not None:
                        a = len((ein.get("old_string") or "").encode("utf-8"))
                        n = len((ein.get("new_string") or "").encode("utf-8"))
                        if ein.get("replace_all"):
                            try:
                                voll = pfad if os.path.isabs(pfad) else os.path.join(projekt(), pfad)
                                k = open(voll, "rb").read().count((ein.get("old_string") or "").encode("utf-8"))
                            except Exception:
                                k = 1
                            neu = alt - k * a + k * n
                        else:
                            neu = alt - a + n
                    elif werkzeug == "MultiEdit" and alt is not None:
                        neu = alt
                        for e in ein.get("edits", []) or []:
                            neu += len((e.get("new_string") or "").encode("utf-8")) - len((e.get("old_string") or "").encode("utf-8"))
                    else:
                        neu = None
                    if neu is not None:
                        k = kuerzung(pfad, neu)
                        if k:
                            gruende.append("%s %s" % (norm(pfad), k))
        elif werkzeug == "Bash":
            g = bash_pruefen(ein.get("command", "") or "")
            if g:
                gruende.append(g)
    except Exception as e:
        gruende.append("Waechter konnte nicht pruefen (%s) - fail closed" % e)
    if gruende:
        sys.stderr.write("SCHREIBWAECHTER: abgelehnt. " + " | ".join(gruende) +
                         "\nRegel: CLAUDE.md Abschnitt 5 (Lesen -> bauen -> Anker zaehlen -> schreiben); "
                         "Archiv/ und Rohfassung werden nicht geaendert.\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
