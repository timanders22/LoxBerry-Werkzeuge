#!/usr/bin/env python3
"""Sucht im Bestand die Bauarten, die an AudiConnect 0.9.14 am Geraet aufgefallen sind.

Anlass (11.09.2026): AudiConnect 0.9.14, frisch installiert, ohne Zugangsdaten,
einmal "Dienst starten" gedrueckt. Der Waechter startete den Dienst 444 Mal neu,
die Seite meldete ein Scheitern des Knopfs als "nichts gespeichert", und zwei
Hinweise verhinderten das Speichern. Die Bauarten dahinter sind nicht
Audi-eigen: die Linien sind aus denselben Geruesten gewachsen. Beschrieben in
Stand-Protokolle/2026-09-11_AudiConnect_0.9.15.md, Regeln/03 (Sollmerker) und
Regeln/04 (Knopf, der nichts speichert).

Rein lesend. Je Linie die HOECHSTE Fassung (Regeln/03: sonst meldet man
behobene Fehler als offene). Jeder Fund ist ein KANDIDAT - ein Muster im
Quelltext, kein gemessener Fehler. Wer ihn behebt, misst ihn vorher; die
Pruefstaende dafuer liegen unter Pruefung-AudiConnect-0.9.15-Pruefstaende/.

Muster:
  S1 zugang-nur-datei   Ein Startskript prueft die Zugangsdatei nur mit -f/-e/-s.
                        postinstall.sh legt sie oft als "{}" an - dann ist die
                        Pruefung nach jeder Installation erfuellt.
  S2 start-eine-sekunde Nach "nohup ... &" genau ein "sleep 1", dann das Urteil.
                        Ein Python-Dienst, der die Bibliothek laedt und abbricht,
                        lebte am Pi laenger als eine Sekunde: "gestartet" fuer
                        einen toten Dienst.
  S3 cron-schluckt      Die Cron-Datei ruft den Waechter mit >/dev/null 2>&1, und
                        das gerufene Skript lenkt seine Fehlerausgabe nicht selbst
                        um (exec 2>>...).
  O1 hinweis-sperrt     Ein Hinweisschluessel (..._WARN_/..._HINWEIS_) landet in
                        der Beanstandungsliste ($..fehler[]) - wird dort nur bei
                        leerer Liste gespeichert, verhindert er das Speichern.
  O2 knopf-als-beanst   Das Scheitern des Dienstknopfs landet in der
                        Beanstandungsliste - unter deren Ueberschrift
                        ("... nichts gespeichert").

Nicht gesucht, weil nicht als Muster greifbar: ob der Sollmerker im
Fehlerzweig entfernt wird, und was der Endpunkt vor dem ersten Abruf sagt.

Aufruf:  startweg_bestand_pruefen.py [ORDNER ...]
         ohne Ordner: je Linie die hoechste Fassung aller LoxBerry-Plugin-*
Rueckgabewert: 0 keine Kandidaten, 1 Kandidaten, 2 nichts gefunden.
Geeicht an AudiConnect 0.9.14 (alle fuenf Muster) gegen 0.9.15: dort bleibt
EIN O1 - EINST.WARN_PW_OHNE_KONTO steht bewusst in der Beanstandungsliste
(Passwort ohne Konto: jede Anmeldung schlaegt fehl, Speichern verhindern ist
richtig). Der Schluessel heisst nur "WARN_". So sieht ein Kandidat aus, der
keiner ist: nachsehen, nicht umbauen.
"""

import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent

ZUGANG = re.compile(
    r'\[\s*!?\s*-[efs]\s+"?\$\{?\w+\}?/[^"\s\]]*(zugang|credential|secret|login|konto|account)'
    r'[^"\s\]]*"?\s*\]', re.I)
INHALT = re.compile(r'json\.load|jq\s|python3?\s+-c|grep\s+-q[^\n]*(email|user|pass)', re.I)
HINWEIS = re.compile(r"\$(\w*fehler\w*)\[\]\s*=\s*(?:\w+_e\(\s*)?\w+_t\(\s*'[A-Z0-9_]+\."
                     r"(?:WARN|HINWEIS)_[A-Z0-9_]*'")
DIENSTKNOPF = re.compile(r"""isset\(\s*\$_POST\[\s*['"]dienst['"]\s*\]\s*\)""")
FEHLERLISTE = re.compile(r"\$\w*fehler\w*\[\]\s*=")


def lies(p):
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def zeile_von(text, pos):
    return text.count("\n", 0, pos) + 1


def schalen(ordner):
    aus = []
    for teil in ("bin", "daemon"):
        d = ordner / teil
        if not d.is_dir():
            continue
        for f in sorted(d.iterdir()):
            if not f.is_file():
                continue
            if f.suffix == ".sh" or (f.suffix == "" and lies(f).startswith("#!")
                                     and "sh" in lies(f).split("\n", 1)[0]):
                aus.append(f)
    return aus


def pruefe(ordner):
    funde = []
    for f in schalen(ordner):
        t = lies(f)
        rel = f.relative_to(ordner).as_posix()
        for m in ZUGANG.finditer(t):
            if not INHALT.search(t):
                funde.append(("S1", "%s:%d" % (rel, zeile_von(t, m.start()))))
        zeilen = t.split("\n")
        for i, z in enumerate(zeilen):
            if "nohup" in z and z.rstrip().endswith("&"):
                folge = zeilen[i + 1:i + 5]
                if any(x.strip() == "sleep 1" for x in folge) and \
                        not any(re.match(r"\s*(for|while)\s", x) for x in folge):
                    funde.append(("S2", "%s:%d" % (rel, i + 1)))
    cron = ordner / "cron"
    if cron.is_dir():
        for f in sorted(p for p in cron.rglob("*") if p.is_file()):
            t = lies(f)
            for i, z in enumerate(t.split("\n")):
                if not re.search(r">\s*/dev/null\s+2>&1", z) or z.lstrip().startswith("#"):
                    continue
                # Nur Zeilen, die ein Skript DES PLUGINS rufen. Eine Cron-Datei,
                # die selbst ein Skript ist, traegt viele solcher Zeilen fuer
                # eigene Hilfsaufrufe - die sind nicht gemeint (erster Anlauf
                # am 11.09.2026: 52 Treffer, fast alle solche).
                if not re.search(r"REPLACELBPBINDIR|/bin/plugins/|\$\{?LBPBINDIR", z):
                    continue
                m = re.search(r"([\w.-]+\.(?:sh|php|py|pl)|dienst[\w.-]*|waechter[\w.-]*)", z)
                ziel = ordner / "bin" / m.group(1) if m else None
                if ziel is not None and ziel.is_file() and "exec 2>>" in lies(ziel):
                    continue
                funde.append(("S3", "%s:%d" % (f.relative_to(ordner).as_posix(), i + 1)))
    for f in sorted((ordner / "webfrontend" / "htmlauth").glob("*.php")):
        t = lies(f)
        rel = f.relative_to(ordner).as_posix()
        for m in HINWEIS.finditer(t):
            funde.append(("O1", "%s:%d" % (rel, zeile_von(t, m.start()))))
        for m in DIENSTKNOPF.finditer(t):
            rest = t[m.end():]
            ende = re.search(r"\n(?:if \(|/\* -{4,})", rest)
            block = rest[:ende.start()] if ende else rest[:1500]
            if FEHLERLISTE.search(block):
                funde.append(("O2", "%s:%d" % (rel, zeile_von(t, m.start()))))
    return funde


def hoechste():
    beste = {}
    for d in WURZEL.glob("LoxBerry-Plugin-*"):
        m = re.match(r"LoxBerry-Plugin-(.+?)-(\d+(?:\.\d+)+)$", d.name)
        if not (d.is_dir() and m):
            continue
        v = tuple(int(x) for x in m.group(2).split("."))
        if m.group(1) not in beste or v > beste[m.group(1)][0]:
            beste[m.group(1)] = (v, d)
    return [d for _, (_, d) in sorted(beste.items())]


def main():
    ordner = [Path(a).resolve() for a in sys.argv[1:]] or hoechste()
    if not ordner:
        print("Kein Plugin-Ordner gefunden - nichts geprueft.")
        return 2
    zaehler = {}
    mit = 0
    for o in ordner:
        funde = pruefe(o)
        if not funde:
            continue
        mit += 1
        print("%s" % o.name)
        for code, ort in funde:
            zaehler[code] = zaehler.get(code, 0) + 1
            print("   %s  %s" % (code, ort))
    print()
    print("%d Ordner geprueft, %d mit Kandidaten. Je Muster: %s"
          % (len(ordner), mit, ", ".join("%s %d" % kv for kv in sorted(zaehler.items())) or "keine"))
    print("Ein Kandidat ist ein Muster im Quelltext, kein gemessener Fehler - vor dem Beheben messen.")
    return 1 if mit else 0


if __name__ == "__main__":
    sys.exit(main())
