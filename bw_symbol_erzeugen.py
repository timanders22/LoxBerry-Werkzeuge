#!/usr/bin/env python3
"""Erzeugt das Plugin-Symbol des Beschattungswaechters: icon.svg und vier PNG.

Wie bei den Schwestersymbolen: die Geometrie steht EINMAL als Datentabelle da,
SVG und Bild leiten daraus ab. Auf diesem Rechner gibt es keinen
SVG-Rasterizer (nachgemessen 20.08.2026), nur PIL - und PIL liest kein SVG.

DAS MOTIV
---------
Ein halb heruntergelassener Rollladen mit Lamellen, davor die Sonne, und in
der Ecke das eingekreiste A. Das A ist der Kern: dieses Plugin druegt genau
den Knopf, den in Loxone sonst nur ein Mensch druecken kann.

Aufruf:  bw_symbol_erzeugen.py <pluginordner> [--probe]
"""

import sys
from pathlib import Path

GRUEN = (109, 172, 32)
GRUEN_HELL = (125, 196, 36)
GRUEN_DUNKEL = (86, 136, 25)
WEISS = (255, 255, 255)
SONNE = (255, 205, 60)

MITTE = 256
R_SCHEIBE = 246
R_RING = 232

# Rollladen: Kasten oben, Lamellen bis zur halben Hoehe, freies Fenster darunter
FENSTER = (146, 120, 220, 210)        # x, y, Breite, Hoehe
LAMELLEN_BIS = 120                    # so weit reicht der Behang hinunter
LAMELLEN = [140, 160, 180, 200, 220]  # Mittellinien der Lamellen
SONNE_MITTE = (330, 300)
SONNE_R = 40
A_MITTE = (150, 350)
A_R = 46

WORT1 = "Beschattung"
WORT2 = "LOXBERRY"


def hex6(rgb):
    return "#%02x%02x%02x" % rgb


def svg_bauen() -> str:
    x, y, b, h = FENSTER
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
    a('  <circle cx="256" cy="256" r="%d" fill="url(#bg-grad)" />' % R_SCHEIBE)
    a('  <circle cx="256" cy="256" r="%d" fill="none" stroke="#ffffff"'
      ' stroke-opacity="0.35" stroke-width="3" />' % R_RING)
    a('')
    a('  <!-- Die Sonne steht HINTER dem Rollladen - darum zuerst -->')
    a('  <circle cx="%d" cy="%d" r="%d" fill="%s" />'
      % (SONNE_MITTE[0], SONNE_MITTE[1], SONNE_R, hex6(SONNE)))
    for i in range(8):
        import math
        w = math.radians(i * 45)
        x1 = SONNE_MITTE[0] + math.cos(w) * (SONNE_R + 12)
        y1 = SONNE_MITTE[1] + math.sin(w) * (SONNE_R + 12)
        x2 = SONNE_MITTE[0] + math.cos(w) * (SONNE_R + 26)
        y2 = SONNE_MITTE[1] + math.sin(w) * (SONNE_R + 26)
        a('  <line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s"'
          ' stroke-width="9" stroke-linecap="round" />'
          % (x1, y1, x2, y2, hex6(SONNE)))
    a('')
    a('  <g filter="url(#shadow)">')
    a('    <!-- Fensterrahmen -->')
    a('    <rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="none"'
      ' stroke="#ffffff" stroke-width="12" />' % (x, y, b, h))
    a('    <!-- Rollladenkasten -->')
    a('    <rect x="%d" y="%d" width="%d" height="22" rx="6" fill="#ffffff" />'
      % (x - 12, y - 26, b + 24))
    a('    <!-- Behang, halb heruntergelassen -->')
    a('    <rect x="%d" y="%d" width="%d" height="%d" fill="#ffffff" />'
      % (x + 6, y + 6, b - 12, LAMELLEN_BIS))
    for ly in LAMELLEN:
        a('    <line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s"'
          ' stroke-width="5" stroke-linecap="round" />'
          % (x + 16, ly, x + b - 16, ly, hex6(GRUEN)))
    a('    <!-- Schlussschiene -->')
    a('    <rect x="%d" y="%d" width="%d" height="10" rx="3" fill="%s" />'
      % (x + 8, y + LAMELLEN_BIS - 4, b - 16, hex6(GRUEN)))
    a('  </g>')
    a('')
    a('  <!-- Der Knopf, um den es geht -->')
    a('  <circle cx="%d" cy="%d" r="%d" fill="#ffffff" />'
      % (A_MITTE[0], A_MITTE[1], A_R))
    a('  <text x="%d" y="%d" text-anchor="middle" fill="%s"'
      ' font-family="Arial, sans-serif" font-weight="900" font-size="58">A</text>'
      % (A_MITTE[0], A_MITTE[1] + 21, hex6(GRUEN)))
    a('')
    a('  <text x="256" y="446" text-anchor="middle" fill="#ffffff"'
      ' font-family="Arial, sans-serif" font-weight="900" font-size="34"'
      ' letter-spacing="0.5">%s</text>' % WORT1)
    a('  <text x="256" y="478" text-anchor="middle" fill="#ffffff"'
      ' font-family="Arial, sans-serif" font-weight="bold" font-size="18"'
      ' letter-spacing="3">%s</text>' % WORT2)
    a('</svg>')
    return "\n".join(t) + "\n"


def schrift_suchen(groesse: int):
    from PIL import ImageFont
    for k in ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
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
    import math
    S, N = 4, 512 * 4
    def sk(v):
        return v * S
    bild = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(bild)
    m, r = sk(MITTE), sk(R_SCHEIBE)
    d.ellipse([m - r, m - r, m + r, m + r], fill=GRUEN + (255,))
    r = sk(R_RING)
    d.ellipse([m - r, m - r, m + r, m + r], outline=WEISS + (90,), width=3 * S)

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
    d.text((ax, ay), "A", font=schrift_suchen(58 * S), fill=GRUEN + (255,), anchor="mm")

    d.text((sk(256), sk(446)), WORT1, font=schrift_suchen(34 * S),
           fill=WEISS + (255,), anchor="ms")
    f2 = schrift_suchen(18 * S)
    abstand = 3 * S
    breiten = [d.textlength(c, font=f2) for c in WORT2]
    x0 = sk(256) - (sum(breiten) + abstand * (len(WORT2) - 1)) / 2
    for c, bb in zip(WORT2, breiten):
        d.text((x0, sk(478)), c, font=f2, fill=WEISS + (255,), anchor="ls")
        x0 += bb + abstand

    if probe:
        print("  wuerde schreiben: " + ", ".join("icon_%d.png" % g for g in groessen))
        return 0
    for g in groessen:
        bild.resize((g, g), Image.LANCZOS).save(ziel / ("icon_%d.png" % g))
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
