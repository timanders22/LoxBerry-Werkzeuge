#!/usr/bin/env python3
"""Steht ein Download-Handler HINTER lbheader()? Dann liefert der Knopf keine Datei.

Anlass: MGiSmart 1.1.2 (26.08.2026). Die Sicherungs-Handler standen hinter
LBWeb::lbheader(); der Seitenkopf war schon geschrieben, und
header('Content-Type: application/json') kam zu spaet. Der Knopf lieferte
eine Seite mit angehaengtem JSON statt einer Datei.

BERICHTIGT am 26.08.2026, noch im ersten Lauf: die erste Fassung suchte
zeilenweise und liess nur Zeilen aus, die mit *, // oder # BEGINNEN. Damit
traf sie in Robonect 1.1.0 die Zeile

    /* --- Downloads zuerst: sie enden mit exit und muessen VOR lbheader() --- */

als vermeintlichen Aufruf - ausgerechnet den Kommentar, der die richtige
Reihenfolge erklaert. Ergebnis: ein Fehlalarm bei genau der Linie, die den
Fehler behoben hat. Jetzt werden Kommentare und Zeichenketten vorher
ausgeblendet.

Ein Fund bleibt eine Frage: gemessen wird die Zeilennummer, nicht die
Ausfuehrungsreihenfolge. Steht der Aufruf in einer Funktion, die frueher
gerufen wird, ist der Fund keiner.
"""
import os, re, sys

def ohne_kommentare(text):
    """Kommentare und Zeichenketten durch Leerzeichen ersetzen, Zeilen behalten."""
    aus = []
    i, n = 0, len(text)
    while i < n:
        z = text[i]
        if z == '/' and i + 1 < n and text[i+1] == '*':
            j = text.find('*/', i + 2)
            j = n if j < 0 else j + 2
            aus.append(''.join(c if c == '\n' else ' ' for c in text[i:j])); i = j
        elif (z == '/' and i + 1 < n and text[i+1] == '/') or z == '#':
            j = text.find('\n', i)
            j = n if j < 0 else j
            aus.append(' ' * (j - i)); i = j
        elif z in '"\'':
            j = i + 1
            while j < n and text[j] != z:
                j += 2 if text[j] == '\\' else 1
            j = min(j + 1, n)
            aus.append(''.join(c if c == '\n' else ' ' for c in text[i:j])); i = j
        else:
            aus.append(z); i += 1
    return ''.join(aus)

LBHEADER = re.compile(r'\blbheader\s*\(')
SENDET   = re.compile(r'\bheader\s*\(')
WAS      = re.compile(r"""Content-(Type|Disposition)\s*:""", re.I)

def pruefe(pfad):
    roh = open(pfad, encoding='utf-8', errors='replace').read()
    blank = ohne_kommentare(roh)
    zeilen_roh, zeilen = roh.split('\n'), blank.split('\n')
    kopf = next((i for i, z in enumerate(zeilen, 1) if LBHEADER.search(z)), None)
    if kopf is None:
        return None
    spaet = [(i, zeilen_roh[i-1].strip()[:88])
             for i, z in enumerate(zeilen, 1)
             if i > kopf and SENDET.search(z) and WAS.search(zeilen_roh[i-1])]
    return (kopf, spaet) if spaet else None

for wurzel in sys.argv[1:]:
    for w, _, ds in os.walk(wurzel):
        if '.git' in w.split(os.sep):
            continue
        for d in sorted(ds):
            if not d.endswith('.php'):
                continue
            p = os.path.join(w, d)
            try:
                e = pruefe(p)
            except OSError:
                continue
            if e:
                kopf, spaet = e
                print("%s" % os.path.relpath(p, os.path.dirname(wurzel)))
                print("   lbheader() in Zeile %d, danach:" % kopf)
                for i, z in spaet:
                    print("      %5d  %s" % (i, z))
