#!/usr/bin/env python3
"""Erzeugt das Plugin-Symbol der Ecowitt-Weiche: icon.svg und die vier PNG.

WARUM DIESES WERKZEUG
---------------------
Hausregel: "PNG immer aus der SVG erzeugen, nie von Hand nachziehen - sonst
unterscheidet sich das PNG irgendwann vom Vektor, und LoxBerry 3 zeigt das
PNG." Auf diesem Rechner gibt es keinen SVG-Rasterizer (cairosvg, inkscape und
rsvg-convert fehlen, nachgemessen am 20.08.2026); vorhanden ist nur PIL, und
PIL liest kein SVG.

Der Ausweg ist derselbe wie bei BYD Autos: die Geometrie steht EINMAL als
Datentabelle da, und zwei Ausgaben leiten daraus ab - der SVG-Text und das
Bild. Damit kann das MOTIV nicht auseinanderlaufen, und genau darum geht es
der Regel. Offen bleibt allein die Schrift: im SVG steht sie als <text>, im
PNG wird sie mit der oertlichen Schriftdatei gezeichnet.

DAS MOTIV
---------
Eine Weiche. Links zwei Schnittstellen, rechts der eine Strang, der zum
Miniserver geht. Der obere Zweig traegt gerade - durchgezogen, mit gefuelltem
Knoten. Der untere wartet - gestrichelt, nur umrandet. Dass genau eine der
beiden Seiten traegt und die andere bereitsteht, ist die ganze Aussage des
Plugins; mehr soll das Symbol nicht sagen.

Aufruf:  ew_symbol_erzeugen.py <pluginordner> [--probe]
         --probe schreibt nichts und sagt nur, was es tun wuerde.
"""

import math
import sys
from pathlib import Path

# ===========================================================================
# DIE GEOMETRIE - die einzige Quelle
# Koordinaten im 512er-Raster wie bei den uebrigen Symbolen dieser Reihe.
# ===========================================================================
GRUEN = (109, 172, 32)          # #6dac20, das LoxBerry-Gruen
GRUEN_HELL = (125, 196, 36)     # #7dc424
GRUEN_DUNKEL = (86, 136, 25)    # #568819
WEISS = (255, 255, 255)

MITTE = 256
R_SCHEIBE = 246
R_RING = 232

KNOTEN = (300, 240)             # die Weiche selbst
OBEN = (150, 160)               # traegt gerade
UNTEN = (150, 312)              # steht bereit
AUSGANG = (398, 240)            # Richtung Miniserver
R_KNOPF = 30                    # Radius der beiden Schnittstellen-Knoepfe
STRICHBREITE = 20

# Der Pfeil am Ausgang, als Polygon - eine Bezierkurve zeichneten SVG und PIL
# nicht nachweislich gleich.
PFEIL = [(390, 206), (452, 240), (390, 274)]

# Die Wortmarke. Zwei Zeilen wie bei den Schwesterplugins.
WORT1 = "Ecowitt"
WORT2 = "LOXBERRY"


def strecke(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def striche(a, b, strich=20.0, luecke=16.0):
    """Zerlegt eine Strecke in Teilstuecke.

    Gestrichelt wird hier NICHT ueber stroke-dasharray: PIL kennt das nicht,
    und die Regel verlangt, dass beide Ausgaben aus derselben Tabelle kommen.
    Also wird die Strecke einmal zerlegt, und SVG wie PNG zeichnen dieselben
    Teilstuecke.
    """
    laenge = strecke(a, b)
    if laenge <= 0:
        return []
    ex = (b[0] - a[0]) / laenge
    ey = (b[1] - a[1]) / laenge
    aus = []
    pos = 0.0
    while pos < laenge:
        ende = min(pos + strich, laenge)
        aus.append(((a[0] + ex * pos, a[1] + ey * pos),
                    (a[0] + ex * ende, a[1] + ey * ende)))
        pos = ende + luecke
    return aus


STRICHE_UNTEN = striche(UNTEN, KNOTEN)


def hex6(rgb):
    return "#%02x%02x%02x" % rgb


def svg_bauen() -> str:
    t = []
    a = t.append
    a('<?xml version="1.0" encoding="UTF-8"?>')
    a('<svg width="512" height="512" viewBox="0 0 512 512" version="1.1"'
      ' xmlns="http://www.w3.org/2000/svg">')
    a('  <defs>')
    a('    <radialGradient id="bg-grad" cx="50%" cy="50%" r="50%" fx="35%" fy="35%">')
    a('      <stop offset="0%%" stop-color="%s" />' % hex6(GRUEN_HELL))
    a('      <stop offset="65%%" stop-color="%s" />' % hex6(GRUEN))
    a('      <stop offset="100%%" stop-color="%s" />' % hex6(GRUEN_DUNKEL))
    a('    </radialGradient>')
    a('    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">')
    a('      <feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#000000"'
      ' flood-opacity="0.25"/>')
    a('    </filter>')
    a('  </defs>')
    a('')
    a('  <!-- Scheibe und Ring -->')
    a('  <circle cx="256" cy="256" r="%d" fill="url(#bg-grad)" />' % R_SCHEIBE)
    a('  <circle cx="256" cy="256" r="%d" fill="none" stroke="#ffffff"'
      ' stroke-opacity="0.35" stroke-width="3" />' % R_RING)
    a('')
    a('  <g filter="url(#shadow)">')
    a('    <!-- Der wartende Zweig: gestrichelt, weil er gerade nicht traegt -->')
    for p, q in STRICHE_UNTEN:
        a('    <line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#ffffff"'
          ' stroke-opacity="0.55" stroke-width="%d" stroke-linecap="round" />'
          % (p[0], p[1], q[0], q[1], STRICHBREITE))
    a('    <!-- Der tragende Zweig: durchgezogen, von der Schnittstelle ueber die'
      ' Weiche zum Miniserver -->')
    a('    <polyline points="%d,%d %d,%d %d,%d" fill="none" stroke="#ffffff"'
      ' stroke-width="%d" stroke-linecap="round" stroke-linejoin="round" />'
      % (OBEN[0], OBEN[1], KNOTEN[0], KNOTEN[1], AUSGANG[0], AUSGANG[1],
         STRICHBREITE))
    a('    <polygon points="%s" fill="#ffffff" />'
      % ' '.join('%d,%d' % p for p in PFEIL))
    a('    <!-- Die Weiche selbst -->')
    a('    <circle cx="%d" cy="%d" r="16" fill="#ffffff" />' % KNOTEN)
    a('    <!-- Oben: die Schnittstelle, die traegt - gefuellt -->')
    a('    <circle cx="%d" cy="%d" r="%d" fill="#ffffff" />'
      % (OBEN[0], OBEN[1], R_KNOPF))
    a('    <circle cx="%d" cy="%d" r="13" fill="%s" />'
      % (OBEN[0], OBEN[1], hex6(GRUEN)))
    a('    <!-- Unten: die Schnittstelle, die bereitsteht - nur umrandet -->')
    a('    <circle cx="%d" cy="%d" r="%d" fill="%s" stroke="#ffffff"'
      ' stroke-opacity="0.55" stroke-width="9" />'
      % (UNTEN[0], UNTEN[1], R_KNOPF - 4, hex6(GRUEN)))
    a('  </g>')
    a('')
    a('  <!-- Wortmarke -->')
    a('  <text x="256" y="388" text-anchor="middle" fill="#ffffff"'
      ' font-family="Arial, sans-serif" font-weight="900" font-size="46"'
      ' letter-spacing="0.5">%s</text>' % WORT1)
    a('  <text x="256" y="424" text-anchor="middle" fill="#ffffff"'
      ' font-family="Arial, sans-serif" font-weight="bold" font-size="20"'
      ' letter-spacing="3">%s</text>' % WORT2)
    a('</svg>')
    return "\n".join(t) + "\n"


def schrift_suchen(fett: bool, groesse: int):
    from PIL import ImageFont
    kandidaten = [
        "C:/Windows/Fonts/arialbd.ttf" if fett else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if fett else "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if fett
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for k in kandidaten:
        if Path(k).is_file():
            try:
                return ImageFont.truetype(k, groesse)
            except Exception:
                pass
    return ImageFont.load_default()


def png_bauen(groessen, ziel: Path, probe: bool) -> int:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("PIL fehlt - die PNG koennen nicht erzeugt werden.")
        return 1

    # Vierfach zeichnen und herunterrechnen: PIL kennt kein Antialiasing beim
    # Zeichnen selbst, wohl aber beim Verkleinern.
    S = 4
    N = 512 * S

    def sk(p):
        return (p[0] * S, p[1] * S)

    bild = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(bild)

    # Scheibe. Der Verlauf der SVG laesst sich mit PIL nicht nachbilden; hier
    # steht deshalb die mittlere Farbe. Das ist der einzige bewusste
    # Unterschied zwischen beiden Ausgaben, und er faellt bei 64 Pixeln nicht
    # auf.
    m = MITTE * S
    r = R_SCHEIBE * S
    d.ellipse([m - r, m - r, m + r, m + r], fill=GRUEN + (255,))
    r = R_RING * S
    d.ellipse([m - r, m - r, m + r, m + r], outline=WEISS + (90,), width=3 * S)

    br = STRICHBREITE * S
    for p, q in STRICHE_UNTEN:
        d.line([sk(p), sk(q)], fill=WEISS + (140,), width=br, joint="curve")
        # Runde Enden: PIL kennt kein stroke-linecap, also je ein Kreis.
        for e in (p, q):
            x, y = sk(e)
            d.ellipse([x - br / 2, y - br / 2, x + br / 2, y + br / 2],
                      fill=WEISS + (140,))

    d.line([sk(OBEN), sk(KNOTEN), sk(AUSGANG)], fill=WEISS + (255,),
           width=br, joint="curve")
    for e in (OBEN, KNOTEN, AUSGANG):
        x, y = sk(e)
        d.ellipse([x - br / 2, y - br / 2, x + br / 2, y + br / 2],
                  fill=WEISS + (255,))
    d.polygon([sk(p) for p in PFEIL], fill=WEISS + (255,))

    def kreis(mp, radius, fuellung, rand=None, randbreite=0):
        x, y = sk(mp)
        rr = radius * S
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=fuellung,
                  outline=rand, width=randbreite * S)

    kreis(KNOTEN, 16, WEISS + (255,))
    kreis(OBEN, R_KNOPF, WEISS + (255,))
    kreis(OBEN, 13, GRUEN + (255,))
    kreis(UNTEN, R_KNOPF - 4, GRUEN + (255,), WEISS + (140,), 9)

    f1 = schrift_suchen(True, 46 * S)
    f2 = schrift_suchen(True, 20 * S)
    d.text((256 * S, 388 * S), WORT1, font=f1, fill=WEISS + (255,), anchor="ms")
    # letter-spacing kennt PIL nicht - die zweite Zeile deshalb Zeichen fuer
    # Zeichen, damit sie im PNG so breit steht wie im SVG.
    text2 = WORT2
    abstand = 3 * S
    breiten = [d.textlength(c, font=f2) for c in text2]
    gesamt = sum(breiten) + abstand * (len(text2) - 1)
    x = 256 * S - gesamt / 2
    for c, b in zip(text2, breiten):
        d.text((x, 424 * S), c, font=f2, fill=WEISS + (255,), anchor="ls")
        x += b + abstand

    if probe:
        print("  wuerde schreiben: " + ", ".join("icon_%d.png" % g for g in groessen))
        return 0
    for g in groessen:
        klein = bild.resize((g, g), Image.LANCZOS)
        klein.save(ziel / ("icon_%d.png" % g))
        print("  icon_%d.png" % g)
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    ordner = Path(sys.argv[1])
    probe = "--probe" in sys.argv[2:]
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
