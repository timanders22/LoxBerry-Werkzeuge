#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VERALTET SEIT 01.11.2026 - NICHT MEHR BENUTZEN.

Seit Spotpreis aWATTar 1.2.42 traegt die Linie das Symbol, das der Hausherr
selbst geliefert hat (Paket aus Downloads, byte-gleich uebernommen). Dieses
Skript wuerde es mit dem alten, hier gezeichneten Motiv ueberschreiben.
Hausregel (Regeln/04, Abschnitt Symbole): Symbole vom Hausherrn haben Vorrang
und werden von keinem Erzeuger ueberschrieben. Das Skript bricht deshalb beim
Start ab; ausfuehren nur mit dem ausdruecklichen Schalter --trotzdem
(z. B. fuer einen Vergleich in einem Wegwerfordner, nie gegen icons/ einer Linie).

------------------------------------------------------------------------------
Erzeugt das Plugin-Symbol von Spotpreis aWATTar: icon.svg und vier PNG.

Wie bei den Schwestersymbolen steht die Geometrie EINMAL als Datentabelle da;
SVG und Bild leiten daraus ab. Gerastert wird mit cairosvg - auf diesem
Rechner vorhanden, nachgemessen 02.09.2026.

    python spot_symbol_erzeugen.py <icons-Ordner>

DAS MOTIV
---------
Zwei Gegenstaende, klar in Ober- und Unterhaelfte geteilt - so, wie es der
Hausstandard fuer zwei Motive verlangt (Uhr ueber Auto beim
Abfahrtsassistenten):

    oben   ein Blitz          - Strom
    unten  eine Preiskurve    - der stuendlich wechselnde Boersenpreis

Mehr nicht. Bei 64 Pixeln - der Groesse in der Plugin-Uebersicht - ist alles
Weitere ein Fleck.

WAS AM 02.09.2026 BERICHTIGT WURDE
----------------------------------
Das vorgefundene icon.svg wich an SIEBEN Stellen vom verbindlichen Muster ab.
Gemessen an REGELN_2, Abschnitt "Symbole - das verbindliche Muster":

  1. SCHEIBE NICHT RANDFUELLEND    r=246 statt 256
  2. FARBVERLAUF STATT FLAECHE     radialGradient #7dc424 -> #6dac20 -> #568819
     Der Hausstandard nennt genau eine Farbe: #6dac20, flach.
  3. RING FALSCH                   stroke-opacity 0.35, stroke-width 3
     statt 0.28 und 6. Der Ring ist der Wiedererkennungswert aller Symbole
     dieses Hauses; wer ihn veraendert, veraendert die Kachelliste.
  4. SCHLAGSCHATTEN                <feDropShadow> auf dem ganzen Motiv.
     "Motiv in Weiss, flach. Keine Farbverlaeufe, keine Schatten."
  5. SCHRIFTZUEGE                  zwei <text>: "Spotpreis aWATTar" und
     "LOXBERRY". Beides steht in der Kachelliste ohnehin unter dem Symbol;
     bei 64 Pixeln waren die 29 bzw. 20 Einheiten hohen Zeilen ein Fleck.
     Dazu haengt <text> von den Schriften des rasternden Rechners ab -
     derselbe Grund, aus dem das "A" beim Beschattungswaechter ein Pfad ist.
  6. VIER GEGENSTAENDE             Balkendiagramm, Blitz, ein eingekreistes
     Euro-Zeichen (wieder als <text>), ein eingekreister Trendpfeil, dazu
     eine gestrichelte Linie. "Vier Gegenstaende in einem Symbol sind bei 64
     Pixeln ein Fleck."
  7. STRICHSTAERKEN ZU FEIN        Balken 10 Einheiten breit, der Trendpfeil
     3 Einheiten stark, die gestrichelte Linie 4. Der Hausstandard nennt 14
     als Untergrenze - darunter verschwinden sie bei 64 Pixeln.

Und: das Motiv reichte weit ueber r=200 hinaus. Die untere Textzeile stand
bei y=424, also 168 Einheiten unter der Mitte und fast randbreit.

MASSVERHAELTNISSE, nachgerechnet
--------------------------------
Alles bleibt innerhalb r=200 um (256, 256). Die weiteste Ecke ist der
Fusspunkt der Grundlinie links: (139, 414) -> dx=-117, dy=158 -> r=197.
"""
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------- Geometrie
# Balken: (x, Hoehe). Alle 34 breit, Fussgrund bei y = 400, Abstand 48.
BALKEN = [(147, 70), (195, 100), (243, 130), (291, 94), (339, 56)]
BREITE = 34
FUSS = 400
# Grundlinie unter den Balken
LINIE = (139, 400, 234, 14)          # x, y, Breite, Hoehe
# Blitz, als Pfad. Sechs Punkte, keine Strichlinie - eine Flaeche.
BLITZ = "M 272 88 L 192 206 L 238 206 L 220 264 L 312 142 L 262 142 Z"

KOPF = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <!-- Spotpreis aWATTar. Erzeugt von Werkzeuge/spot_symbol_erzeugen.py -
       nicht von Hand aendern, sonst laufen SVG und PNG auseinander.

       Aufbau nach REGELN_2: randfuellende Scheibe #6dac20, zweiter Ring bei
       r=232 in Weiss mit Deckkraft 0.28 und Strichbreite 6, Motiv flach in
       Weiss. Kein Verlauf, kein Schatten, kein Schriftzug.

       Motiv: Blitz ueber Preiskurve - oben der Strom, unten der Preis. -->
  <circle cx="256" cy="256" r="256" fill="#6dac20"/>
  <circle cx="256" cy="256" r="232" fill="none"
          stroke="#ffffff" stroke-opacity="0.28" stroke-width="6"/>
"""


def svg():
    z = [KOPF]
    z.append('  <!-- Blitz -->\n')
    z.append('  <path d="%s" fill="#ffffff"/>\n' % BLITZ)
    z.append('  <!-- Preiskurve: fuenf Stundenbalken auf einer Grundlinie -->\n')
    z.append('  <g fill="#ffffff">\n')
    for x, h in BALKEN:
        z.append('    <rect x="%d" y="%d" width="%d" height="%d" rx="6"/>\n'
                 % (x, FUSS - h, BREITE, h))
    z.append('    <rect x="%d" y="%d" width="%d" height="%d" rx="7"/>\n' % LINIE)
    z.append('  </g>\n')
    z.append('</svg>\n')
    return ''.join(z)


def pruefen():
    """Bleibt alles innerhalb r=200 um die Mitte? Und ist nichts zu fein?"""
    punkte = []
    for x, h in BALKEN:
        punkte += [(x, FUSS - h), (x + BREITE, FUSS - h), (x, FUSS), (x + BREITE, FUSS)]
    lx, ly, lb, lh = LINIE
    punkte += [(lx, ly), (lx + lb, ly), (lx, ly + lh), (lx + lb, ly + lh)]
    for teil in BLITZ.replace('M ', '').replace('L ', '').replace(' Z', '').split('  '):
        pass
    import re
    zahlen = [int(n) for n in re.findall(r'\d+', BLITZ)]
    punkte += list(zip(zahlen[0::2], zahlen[1::2]))
    weit = max(((x - 256) ** 2 + (y - 256) ** 2) ** 0.5 for x, y in punkte)
    print('   weitester Punkt vom Mittelpunkt: r = %.0f  (erlaubt 200)' % weit)
    if weit > 200:
        raise SystemExit('ABBRUCH: das Motiv reicht ueber r=200 hinaus')
    duenn = min([BREITE, lh])
    print('   feinste Strichstaerke:           %d  (Untergrenze 14)' % duenn)
    if duenn < 14:
        raise SystemExit('ABBRUCH: eine Flaeche ist feiner als 14 Einheiten')


def main():
    ziel = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    print('Symbol Spotpreis aWATTar -> %s' % ziel)
    pruefen()
    (ziel / 'icon.svg').write_bytes(svg().encode('utf-8'))
    print('   icon.svg geschrieben (%d Byte)' % (ziel / 'icon.svg').stat().st_size)

    import cairosvg
    for n in (64, 128, 256, 512):
        cairosvg.svg2png(url=str(ziel / 'icon.svg'),
                         write_to=str(ziel / ('icon_%d.png' % n)),
                         output_width=n, output_height=n)
        print('   icon_%d.png  %d Byte' % (n, (ziel / ('icon_%d.png' % n)).stat().st_size))


if __name__ == '__main__':
    # Gesperrt seit 01.11.2026 (siehe Kopf): ohne --trotzdem wird nichts geschrieben.
    if '--trotzdem' not in sys.argv[1:]:
        sys.stderr.write(
            'ABBRUCH: spot_symbol_erzeugen.py ist veraltet (seit 01.11.2026).\n'
            'Spotpreis aWATTar traegt seit 1.2.42 das Symbol des Hausherrn; dieses\n'
            'Skript wuerde es ueberschreiben (Regeln/04, Abschnitt Symbole).\n'
            'Es wurde nichts geschrieben. Nur fuer einen Vergleich in einem\n'
            'Wegwerfordner: python spot_symbol_erzeugen.py <ordner> --trotzdem\n')
        sys.exit(3)
    sys.argv = [a for a in sys.argv if a != '--trotzdem']
    sys.exit(main())
