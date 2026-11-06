#!/usr/bin/env python3
"""Erzeugt das Plugin-Symbol des Beschattungswaechters: icon.svg und vier PNG.

Wie bei den Schwestersymbolen: die Geometrie steht EINMAL als Datentabelle da,
SVG und Bild leiten daraus ab. Auf diesem Rechner gibt es keinen
SVG-Rasterizer (nachgemessen 20.08.2026), nur PIL - und PIL liest kein SVG.

DAS MOTIV
---------
Ein halb heruntergelassener Rollladen mit Lamellen, davor die Sonne, und in
der Ecke das eingekreiste A. Das A ist der Kern: dieses Plugin drueckt genau
den Knopf, den in Loxone sonst nur ein Mensch druecken kann.

WAS AM 29.08.2026 BERICHTIGT WURDE
----------------------------------
Beim Nachsehen lagen im Plugin DREI verschiedene Symbole nebeneinander:

  * icon.svg (4715 Byte, von Hand)   Fenster, Sonne, A - und Verlauf, Schatten
  * icon_*.png (mitgeliefert)        ein Blatt mit dem Schriftzug
                                     "Beschattungswaechter LOXBERRY"
  * was dieses Werkzeug erzeugte     Fenster, Sonne, A - plus dieselben zwei
                                     Woerter

LoxBerry 3 zeigt das PNG. Bei 64 Pixeln - der Groesse in der Uebersicht - war
der Schriftzug ein Fleck. Genau davor warnt der Hausstandard: "Was dort
zerfliesst, ist kein Symbol", und "PNG immer aus der SVG erzeugen, nie von
Hand nachziehen - sonst unterscheidet sich das PNG irgendwann vom Vektor".

Berichtigt wurde deshalb dreierlei, und alles drei steht im Hausstandard:

  1. KEIN SCHRIFTZUG. Das Symbol steht in der Kachelliste unter seinem Namen;
     den Namen ein zweites Mal hineinzuschreiben kostet nur die Flaeche, in
     der man das Motiv erkennen koennte.
  2. KEIN VERLAUF, KEIN SCHATTEN. Flache Scheibe #6dac20, randfuellend
     (r = 256, nicht 246), zweiter Ring bei r = 232 in Weiss mit
     Deckkraft 0.28 und Strichbreite 6. Das ist der Wiedererkennungswert
     aller Symbole dieses Hauses.
  3. DAS "A" ALS PFAD, nicht als <text>. Ein Textelement haengt von den
     Schriften des Rechners ab, der es darstellt - im SVG genauso wie beim
     Rastern. Drei Striche sind unabhaengig davon und sehen ueberall gleich
     aus.

Aufruf:  bw_symbol_erzeugen.py <pluginordner> [--probe]
"""

import math
import sys
from pathlib import Path

GRUEN = (109, 172, 32)
WEISS = (255, 255, 255)
SONNE = (255, 205, 60)

MITTE = 256
R_SCHEIBE = 256           # randfuellend - der Kreis schneidet ab, was darueber liegt
R_RING = 232
RING_DECK = 0.28
RING_BREITE = 6

# Rollladen: Kasten oben, Lamellen bis zur halben Hoehe, freies Fenster darunter
FENSTER = (146, 120, 220, 210)        # x, y, Breite, Hoehe
LAMELLEN_BIS = 120                    # so weit reicht der Behang hinunter
LAMELLEN = [140, 160, 180, 200, 220]  # Mittellinien der Lamellen
SONNE_MITTE = (330, 300)
SONNE_R = 40
A_MITTE = (150, 350)
A_R = 46


def hex6(rgb):
    return "#%02x%02x%02x" % rgb


def a_striche(mx, my, r):
    """Der Buchstabe A als drei Strecken - unabhaengig von jeder Schrift.

    Rueckgabe: Liste von ((x1,y1),(x2,y2),Breite). Die Masse haengen am
    Radius des Kreises, damit das A mitwaechst, wenn jemand ihn aendert.
    """
    h = r * 1.10          # Hoehe des Buchstabens
    w = r * 0.82          # Breite unten
    dick = max(4, int(round(r * 0.20)))
    oben = (mx, my - h / 2)
    lu = (mx - w / 2, my + h / 2)
    ru = (mx + w / 2, my + h / 2)
    # Der Querstrich sitzt auf 62 Prozent der Hoehe
    t = 0.62
    ql = (oben[0] + (lu[0] - oben[0]) * t, oben[1] + (lu[1] - oben[1]) * t)
    qr = (oben[0] + (ru[0] - oben[0]) * t, oben[1] + (ru[1] - oben[1]) * t)
    return [(oben, lu, dick), (oben, ru, dick), (ql, qr, dick)]


def svg_bauen():
    x, y, b, h = FENSTER
    t = []
    a = t.append
    a('<?xml version="1.0" encoding="UTF-8"?>')
    a('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"'
      ' width="512" height="512">')
    a('  <!-- Runde Scheibe, randfuellend, LoxBerry-Gruen. Kein Verlauf und')
    a('       kein Schatten: die Kachelansicht stellt die Symbole nebeneinander,')
    a('       und eine Mischung aus flach und plastisch sieht dort aus wie zwei')
    a('       Plugin-Sammlungen. -->')
    a('  <circle cx="256" cy="256" r="%d" fill="%s"/>' % (R_SCHEIBE, hex6(GRUEN)))
    a('  <circle cx="256" cy="256" r="%d" fill="none" stroke="#ffffff"'
      ' stroke-opacity="%s" stroke-width="%d"/>'
      % (R_RING, RING_DECK, RING_BREITE))
    a('')
    a('  <!-- Die Sonne steht HINTER dem Rollladen - darum zuerst -->')
    a('  <circle cx="%d" cy="%d" r="%d" fill="%s"/>'
      % (SONNE_MITTE[0], SONNE_MITTE[1], SONNE_R, hex6(SONNE)))
    for i in range(8):
        w = math.radians(i * 45)
        x1 = SONNE_MITTE[0] + math.cos(w) * (SONNE_R + 12)
        y1 = SONNE_MITTE[1] + math.sin(w) * (SONNE_R + 12)
        x2 = SONNE_MITTE[0] + math.cos(w) * (SONNE_R + 26)
        y2 = SONNE_MITTE[1] + math.sin(w) * (SONNE_R + 26)
        a('  <line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s"'
          ' stroke-width="9" stroke-linecap="round"/>'
          % (x1, y1, x2, y2, hex6(SONNE)))
    a('')
    a('  <!-- Fensterrahmen -->')
    a('  <rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="none"'
      ' stroke="#ffffff" stroke-width="12"/>' % (x, y, b, h))
    a('  <!-- Rollladenkasten -->')
    a('  <rect x="%d" y="%d" width="%d" height="22" rx="6" fill="#ffffff"/>'
      % (x - 12, y - 26, b + 24))
    a('  <!-- Behang, halb heruntergelassen -->')
    a('  <rect x="%d" y="%d" width="%d" height="%d" fill="#ffffff"/>'
      % (x + 6, y + 6, b - 12, LAMELLEN_BIS))
    for ly in LAMELLEN:
        a('  <line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s"'
          ' stroke-width="5" stroke-linecap="round"/>'
          % (x + 16, ly, x + b - 16, ly, hex6(GRUEN)))
    a('  <!-- Schlussschiene -->')
    a('  <rect x="%d" y="%d" width="%d" height="10" rx="3" fill="%s"/>'
      % (x + 8, y + LAMELLEN_BIS - 4, b - 16, hex6(GRUEN)))
    a('')
    a('  <!-- Der Knopf, um den es geht. Das A ist gezeichnet, nicht gesetzt:')
    a('       ein Schriftelement haengt von den Schriften des Rechners ab, der')
    a('       es darstellt. Der Name dieses Elements steht hier absichtlich')
    a('       nicht - eine Suche nach ihm soll in dieser Datei nichts finden. -->')
    a('  <circle cx="%d" cy="%d" r="%d" fill="#ffffff"/>'
      % (A_MITTE[0], A_MITTE[1], A_R))
    for (p1, p2, dick) in a_striche(A_MITTE[0], A_MITTE[1], A_R):
        a('  <line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"'
          ' stroke-width="%d" stroke-linecap="round"/>'
          % (p1[0], p1[1], p2[0], p2[1], hex6(GRUEN), dick))
    a('</svg>')
    return "\n".join(t) + "\n"


def png_bauen(groessen, ziel, probe):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("PIL fehlt - die PNG koennen nicht erzeugt werden.")
        return 1
    # Achtfache Ueberabtastung, sonst fransen die Kanten bei 64 Pixeln aus.
    S, N = 8, 512 * 8

    def sk(v):
        return v * S

    bild = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(bild)
    m, r = sk(MITTE), sk(R_SCHEIBE)
    d.ellipse([m - r, m - r, m + r - 1, m + r - 1], fill=GRUEN + (255,))
    r = sk(R_RING)
    d.ellipse([m - r, m - r, m + r, m + r],
              outline=WEISS + (int(round(255 * RING_DECK)),), width=RING_BREITE * S)

    sx, sy, sr = sk(SONNE_MITTE[0]), sk(SONNE_MITTE[1]), sk(SONNE_R)
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=SONNE + (255,))
    for i in range(8):
        w = math.radians(i * 45)
        d.line([(sx + math.cos(w) * sk(SONNE_R + 12), sy + math.sin(w) * sk(SONNE_R + 12)),
                (sx + math.cos(w) * sk(SONNE_R + 26), sy + math.sin(w) * sk(SONNE_R + 26))],
               fill=SONNE + (255,), width=9 * S)

    x, y, b, h = FENSTER
    d.rounded_rectangle([sk(x), sk(y), sk(x + b), sk(y + h)], radius=10 * S,
                        outline=WEISS + (255,), width=12 * S)
    d.rounded_rectangle([sk(x - 12), sk(y - 26), sk(x + b + 12), sk(y - 4)],
                        radius=6 * S, fill=WEISS + (255,))
    d.rectangle([sk(x + 6), sk(y + 6), sk(x + b - 6), sk(y + 6 + LAMELLEN_BIS)],
                fill=WEISS + (255,))
    for ly in LAMELLEN:
        d.line([(sk(x + 16), sk(ly)), (sk(x + b - 16), sk(ly))],
               fill=GRUEN + (255,), width=5 * S)
    d.rounded_rectangle([sk(x + 8), sk(y + LAMELLEN_BIS - 4),
                         sk(x + b - 8), sk(y + LAMELLEN_BIS + 6)],
                        radius=3 * S, fill=GRUEN + (255,))

    ax, ay, ar = sk(A_MITTE[0]), sk(A_MITTE[1]), sk(A_R)
    d.ellipse([ax - ar, ay - ar, ax + ar, ay + ar], fill=WEISS + (255,))
    for (p1, p2, dick) in a_striche(A_MITTE[0], A_MITTE[1], A_R):
        d.line([(sk(p1[0]), sk(p1[1])), (sk(p2[0]), sk(p2[1]))],
               fill=GRUEN + (255,), width=dick * S, joint="curve")

    if probe:
        print("  wuerde schreiben: " + ", ".join("icon_%d.png" % g for g in groessen))
        return 0
    for g in groessen:
        bild.resize((g, g), Image.LANCZOS).save(ziel / ("icon_%d.png" % g))
        print("  icon_%d.png" % g)
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    ordner = Path(sys.argv[1])
    probe = "--probe" in sys.argv[2:]
    unbekannt = [a for a in sys.argv[2:] if a.startswith("--") and a != "--probe"]
    if unbekannt:
        print("Unbekannte(r) Schalter: %s - bekannt ist --probe" % ", ".join(unbekannt))
        return 2
    if not ordner.is_dir():
        print("Kein Ordner: %s" % ordner)
        return 2
    ziel = ordner / "icons"
    if not probe:
        ziel.mkdir(exist_ok=True)
    svg = svg_bauen()
    if probe:
        print("  wuerde schreiben: icon.svg (%d Bytes)" % len(svg.encode("utf-8")))
    else:
        (ziel / "icon.svg").write_bytes(svg.encode("utf-8"))
        print("  icon.svg")
    return png_bauen([64, 128, 256, 512], ziel, probe)


if __name__ == "__main__":
    sys.exit(main())
