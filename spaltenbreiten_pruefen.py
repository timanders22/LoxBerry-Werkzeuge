# -*- coding: utf-8 -*-
"""Eine Tabellenspalte ohne Breitenangabe bekommt, was die anderen uebrig
lassen - und das kann sehr wenig sein.

Anlass: Robonect 1.1.8, am Bildschirm gemessen. In der Maehertabelle trugen
sieben von acht Spalten eine Breite (36px, 24%, 18%, 20%, 110px, 110px,
70px), die achte - ausgerechnet die Adresse - keine. Uebrig blieben 46 px
gerechnet, 66 px gerendert, das Eingabefeld war 51 px breit und zeigte von
"192.168.1.34" nur "192.". Behoben in 1.1.9.

Gemeldet wird nur der Fall, der wehtut: eine Kopfzeile, in der MINDESTENS
eine Spalte ohne Breite steht UND die uebrigen Angaben so viel belegen, dass
fuer jede breitenlose Spalte weniger als 12 % der Tabelle bleiben. Eine
Tabelle ohne jede Breitenangabe ist in Ordnung - dann teilt der Browser
gleichmaessig auf.

Gerechnet wird gegen 980 px (die Hausbreite: .sm-wrap max-width: 980px).
Das ist eine Abschaetzung und ersetzt die Messung im Browser nicht - der
Bericht sagt deshalb "nachmessen", nicht "kaputt".

Aufruf:
    python3 Werkzeuge/spaltenbreiten_pruefen.py                 (alle Linien)
    python3 Werkzeuge/spaltenbreiten_pruefen.py ORDNER [...]
"""
import glob
import io
import os
import re
import sys

BREITE = 980.0
GRENZE = 12.0          # Prozent, unter denen es eng wird
TR = re.compile(r'<tr>(.*?)</tr>', re.S | re.I)
TH = re.compile(r'<th([^>]*)>', re.I)
WID = re.compile(r'width\s*:\s*([0-9.]+)\s*(px|%)', re.I)


def kopfzeilen(text):
    """Jede <tr>, die ueberwiegend aus <th> besteht."""
    for m in TR.finditer(text):
        roh = m.group(1)
        ths = TH.findall(roh)
        if len(ths) >= 3:
            yield m.start(), ths


def urteil(ths):
    fest_px, prozent, ohne = 0.0, 0.0, 0
    for a in ths:
        w = WID.search(a)
        if not w:
            ohne += 1
            continue
        wert, einheit = float(w.group(1)), w.group(2)
        if einheit == '%':
            prozent += wert
        else:
            fest_px += wert
    if ohne == 0 or ohne == len(ths):
        # Keine Angabe, oder gar keine: im zweiten Fall teilt der Browser
        # gleichmaessig auf, und das ist in Ordnung. Nur die MISCHUNG aus
        # festen und fehlenden Angaben macht eine Spalte schmal.
        return None
    rest = BREITE - fest_px - (prozent / 100.0) * BREITE
    je = rest / ohne
    return (ohne, fest_px, prozent, je, je / BREITE * 100.0)


def eine(ordner):
    treffer = []
    for pfad in glob.glob(os.path.join(ordner, 'webfrontend', '**', '*.php'),
                          recursive=True):
        text = io.open(pfad, encoding='utf-8', errors='replace').read()
        for pos, ths in kopfzeilen(text):
            u = urteil(ths)
            if u is None:
                continue
            ohne, fest, proz, je, anteil = u
            if anteil < GRENZE:
                zeile = text[:pos].count('\n') + 1
                rel = os.path.relpath(pfad, ordner).replace(os.sep, '/')
                treffer.append((rel, zeile, len(ths), ohne, fest, proz, je, anteil))
    return treffer


def main():
    ordner = sys.argv[1:]
    if not ordner:
        # Je Linie nur die HOECHSTE Fassung - sonst meldet der Bericht
        # dieselbe Stelle fuenfmal, einmal je liegengebliebenem Ordner.
        hoechste = {}
        for d in glob.glob('LoxBerry-Plugin-*/'):
            if not os.path.isdir(d):
                continue
            d = d.rstrip(os.sep).rstrip('/')
            m = re.match(r'(.*?)-(\d+(?:\.\d+)*)$', os.path.basename(d))
            if not m:
                continue
            linie, fassung = m.group(1), tuple(int(x) for x in m.group(2).split('.'))
            if linie not in hoechste or fassung > hoechste[linie][0]:
                hoechste[linie] = (fassung, d)
        ordner = [v[1] for _, v in sorted(hoechste.items())]
    gesamt = 0
    linien = 0
    for o in ordner:
        t = eine(o)
        if not t:
            continue
        linien += 1
        gesamt += len(t)
        print('%s' % os.path.basename(o))
        for rel, zeile, n, ohne, fest, proz, je, anteil in t:
            print('   %s:%d  %d Spalten, %d ohne Breite; fest %.0f px + %.0f %% '
                  '-> je %.0f px (%.1f %%) - im Browser nachmessen'
                  % (rel, zeile, n, ohne, fest, proz, je, anteil))
    print()
    print('%d Linie(n) geprueft, %d mit enger Spalte, %d Kopfzeile(n) insgesamt.'
          % (len(ordner), linien, gesamt))
    print('Eine Tabelle ganz ohne Breitenangaben ist in Ordnung und wird nicht')
    print('gemeldet. Gerechnet gegen %d px; die Zahl ersetzt die Messung am'
          % int(BREITE))
    print('Bildschirm nicht.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
