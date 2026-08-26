#!/usr/bin/env python3
"""Erzeugt das Plugin-Symbol von BYD Autos: icon.svg und die vier PNG.

WARUM DIESES WERKZEUG UEBERHAUPT
--------------------------------
Die Hausregel lautet: "PNG immer aus der SVG erzeugen, nie von Hand nachziehen
- sonst unterscheidet sich das PNG irgendwann vom Vektor, und LoxBerry 3 zeigt
das PNG." Auf diesem Arbeitsrechner gibt es aber keinen SVG-Rasterizer:
cairosvg fehlt, ebenso inkscape und rsvg-convert; vorhanden ist nur PIL, und
PIL kann kein SVG lesen (nachgemessen am 20.08.2026).

Zwei schlechte Wege gaebe es: die PNG von Hand nachzeichnen (genau das, was die
Regel verbietet) oder das Plugin ohne PNG ausliefern (dann meldet LoxBerry bei
jedem Auto-Update "ICON files: Icons could not be (completely) installed",
solange LB_MINIMUM unter 4 steht).

Der dritte Weg ist dieser: die Geometrie steht EINMAL als Datentabelle da, und
zwei Ausgaben leiten daraus ab - der SVG-Text und das Bild. Damit kann das
MOTIV nicht auseinanderlaufen, und genau darum geht es der Regel.

Was dabei offen bleibt, und das gehoert gesagt: die Schrift. Im SVG steht sie
als <text> mit Arial und einer Ersatzkette, im PNG wird sie mit der oertlichen
Arial-Datei gezeichnet. Auf einem Rechner ohne Arial sieht die SVG-Darstellung
also anders aus als das PNG. Die Hausregel verlangt fuer Wortmarken einen Pfad
statt <text>; dafuer braeuchte es Schriftumrisse, die hier nicht zu erzeugen
sind. Die vier Schwesterplugins (Volkswagen ID, Skoda Connect NG, Renault NG,
AudiConnect) halten es genauso - der Punkt ist damit nicht neu, aber er ist
hier benannt.

Aufruf:  byd_symbol_erzeugen.py <pluginordner> [--probe]
         --probe schreibt nichts und sagt nur, was es tun wuerde.
"""

import sys
from pathlib import Path

# ===========================================================================
# DIE GEOMETRIE - die einzige Quelle
#
# Koordinaten im 512er-Raster, wie es die uebrigen Symbole der Reihe benutzen.
# Das Motiv bleibt innerhalb r etwa 200 um den Mittelpunkt (256/256): der Kreis
# schneidet alles ab, was darueber hinausragt.
# ===========================================================================
GRUEN = (109, 172, 32)          # #6dac20, das LoxBerry-Gruen
GRUEN_HELL = (125, 196, 36)     # #7dc424
GRUEN_DUNKEL = (86, 136, 25)    # #568819
WEISS = (255, 255, 255)

MITTE = 256
R_SCHEIBE = 246
R_RING = 232

# Wagenkoerper in der Seitenansicht. Ein eigener Umriss, kein bestimmtes
# Modell: eine viertuerige Stufenheck-Silhouette mit langer Fensterlinie.
# Als Polygon und nicht als Bezierkurve - nur so zeichnen SVG und PIL
# nachweislich dasselbe.
WAGEN = [
    (112, 286), (112, 258), (118, 248), (150, 240), (166, 236),
    (192, 208), (214, 195), (246, 190), (292, 191), (318, 199),
    (344, 216), (368, 231), (392, 238), (402, 248), (404, 260),
    (404, 286),
]
# Zwei Seitenfenster, in Gruen ausgespart. Zwei Felder statt eines
# durchgehenden Bandes: bei 64 Pixeln liest sich ein einzelner Schlitz wie ein
# Fehler in der Karosserie.
FENSTER_VORN = [(200, 232), (220, 206), (248, 200), (248, 232)]
FENSTER_HINTEN = [(258, 200), (296, 202), (330, 232), (258, 232)]

RAEDER = [(182, 288), (338, 288)]
R_REIFEN = 32
R_NABE = 14

# Beizeichen ueber dem Wagen: ein Blitz. Er unterscheidet dieses Symbol von den
# Schwestern der Reihe (dort stehen Funkwellen ueber dem Wagen) und sagt, worum
# es geht - BYD baut Elektroautos. Ein Motiv wird nicht zweimal vergeben.
# Die Spitze endet bei y=170, das Dach beginnt bei y=190: zwanzig Einheiten
# Luft. Der erste Entwurf reichte bis y=200 und ragte damit INS Dach - bei 64
# Pixeln las sich das nicht als Blitz, sondern als Beule auf dem Dach.
# Gesehen hat das kein Werkzeug, sondern der Blick auf icon_64.png.
BLITZ = [
    (268, 88), (232, 138), (252, 138), (240, 170),
    (280, 120), (258, 120), (272, 88),
]

TRENNLINIE = (150, 345, 362, 345)   # x1, y1, x2, y2
STRICH_LANG = 6
STRICH_LUECKE = 8
STRICH_DICKE = 4

# Schrift: 29 px fuer den Plugin-Namen, 20 px fuer LOXBERRY - einheitlich ueber
# alle Plugins der Reihe. Massgeblich fuer den Rand ist die UNTERSTE Bildzeile
# der Schrift, dort ist der Kreis am schmalsten.
TEXTE = [
    {"text": "BYD AUTOS", "y": 388, "groesse": 29, "fett": True, "sperrung": 1},
    {"text": "LOXBERRY", "y": 424, "groesse": 20, "fett": True, "sperrung": 3},
]


def punkte(liste):
    return " ".join("%d,%d" % (x, y) for x, y in liste)


def svg_bauen() -> str:
    z = []
    z.append('<?xml version="1.0" encoding="UTF-8"?>')
    z.append('<!--')
    z.append('  BYD Autos - Plugin-Symbol nach Hausstandard.')
    z.append('')
    z.append('  ERZEUGT von Werkzeuge/byd_symbol_erzeugen.py - nicht von Hand aendern.')
    z.append('  Dasselbe Werkzeug erzeugt die vier PNG aus DERSELBEN Geometrie; wer')
    z.append('  hier etwas aendert, ohne das Werkzeug zu benutzen, laesst Vektor und')
    z.append('  Bild auseinanderlaufen - und LoxBerry 3 zeigt das PNG.')
    z.append('')
    z.append('  Aufbau wie bei den uebrigen Plugins der Reihe: Scheibe r=246 mit')
    z.append('  Radialverlauf, innerer Ring r=232 mit 35 % Deckung, flaches weisses')
    z.append('  Motiv, gestrichelte Trennlinie bei y=345, darunter zwei Textzeilen.')
    z.append('')
    z.append('  Keine fremde Wortmarke ausser dem Herstellernamen im Plugin-Namen -')
    z.append('  bei den Auto-Plugins ist er noetig, weil sich die Wagen sonst nicht')
    z.append('  unterscheiden lassen. Das Fahrzeug ist eine eigene Silhouette und')
    z.append('  bildet kein bestimmtes Modell nach. Der Blitz ueber dem Wagen ist das')
    z.append('  Beizeichen dieser Linie; die Schwestern tragen dort Funkwellen.')
    z.append('-->')
    z.append('<svg width="512" height="512" viewBox="0 0 512 512" version="1.1" '
             'xmlns="http://www.w3.org/2000/svg">')
    z.append('  <defs>')
    z.append('    <radialGradient id="bg-grad" cx="50%" cy="50%" r="50%" fx="35%" fy="35%">')
    z.append('      <stop offset="0%" stop-color="#7dc424" />')
    z.append('      <stop offset="65%" stop-color="#6dac20" />')
    z.append('      <stop offset="100%" stop-color="#568819" />')
    z.append('    </radialGradient>')
    z.append('    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">')
    z.append('      <feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#000000" '
             'flood-opacity="0.25"/>')
    z.append('    </filter>')
    z.append('  </defs>')
    z.append('')
    z.append('  <!-- Scheibe und innerer Ring -->')
    z.append('  <circle cx="%d" cy="%d" r="%d" fill="url(#bg-grad)" />'
             % (MITTE, MITTE, R_SCHEIBE))
    z.append('  <circle cx="%d" cy="%d" r="%d" fill="none" stroke="#ffffff" '
             'stroke-opacity="0.35" stroke-width="3" />' % (MITTE, MITTE, R_RING))
    z.append('')
    z.append('  <g filter="url(#shadow)">')
    z.append('    <!-- Blitz: Beizeichen fuer den Elektroantrieb -->')
    z.append('    <polygon points="%s" fill="#ffffff" />' % punkte(BLITZ))
    z.append('')
    z.append('    <!-- Wagen in Seitenansicht, eigener Umriss -->')
    z.append('    <polygon points="%s" fill="#ffffff" />' % punkte(WAGEN))
    z.append('')
    z.append('    <!-- Seitenfenster, in Gruen ausgespart -->')
    z.append('    <polygon points="%s" fill="#6dac20" />' % punkte(FENSTER_VORN))
    z.append('    <polygon points="%s" fill="#6dac20" />' % punkte(FENSTER_HINTEN))
    z.append('')
    z.append('    <!-- Raeder: weisser Reifen, gruene Nabe -->')
    for x, y in RAEDER:
        z.append('    <circle cx="%d" cy="%d" r="%d" fill="#ffffff" />' % (x, y, R_REIFEN))
    for x, y in RAEDER:
        z.append('    <circle cx="%d" cy="%d" r="%d" fill="#6dac20" />' % (x, y, R_NABE))
    z.append('')
    z.append('    <!-- Gestrichelte Trennlinie -->')
    z.append('    <path d="M %d %d L %d %d" stroke="#ffffff" stroke-width="%d" '
             'stroke-dasharray="%d %d" opacity="0.8" fill="none" />'
             % (TRENNLINIE[0], TRENNLINIE[1], TRENNLINIE[2], TRENNLINIE[3],
                STRICH_DICKE, STRICH_LANG, STRICH_LUECKE))
    z.append('  </g>')
    z.append('')
    z.append('  <!-- Schrift. Die Hausregel verlangt fuer eine Wortmarke einen Pfad')
    z.append('       statt <text>; Schriftumrisse lassen sich auf diesem Rechner nicht')
    z.append('       erzeugen. Die vier Schwesterplugins halten es genauso. Wer den')
    z.append('       Pfad nachtraegt, aendert die Geometrie im Werkzeug, nicht hier. -->')
    for t in TEXTE:
        z.append('  <text x="%d" y="%d" text-anchor="middle" fill="#ffffff" '
                 'font-family="Arial, Helvetica, sans-serif" font-weight="%s" '
                 'font-size="%d" letter-spacing="%d">%s</text>'
                 % (MITTE, t["y"], "900" if t["fett"] else "normal",
                    t["groesse"], t["sperrung"], t["text"]))
    z.append('</svg>')
    return "\n".join(z) + "\n"


def schrift_suchen(fett: bool, groesse: int):
    """Eine Arial-Datei auf diesem Rechner. Gibt (Schrift, Pfad) zurueck."""
    from PIL import ImageFont
    namen = (["arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf"] if fett
             else ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf"])
    orte = ["C:/Windows/Fonts/", "/usr/share/fonts/truetype/dejavu/",
            "/Library/Fonts/", ""]
    for ort in orte:
        for n in namen:
            try:
                return (ImageFont.truetype(ort + n, groesse), ort + n)
            except OSError:
                continue
    return (None, "")


def png_bauen(groessen, ziel: Path, probe: bool) -> int:
    """Zeichnet die PNG aus DERSELBEN Geometrie wie das SVG.

    Gezeichnet wird viermal so gross und danach mit LANCZOS verkleinert -
    ohne diese Ueberabtastung fransen die Kanten bei 64 Pixeln aus.
    """
    from PIL import Image, ImageDraw

    fehler = 0
    for g in groessen:
        u = 4                      # Ueberabtastung
        s = g * u
        f = s / 512.0              # Umrechnung vom 512er-Raster
        bild = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(bild)

        def sk(p):
            return [(x * f, y * f) for x, y in p]

        # Radialverlauf: von aussen nach innen konzentrische Kreise. Der
        # Brennpunkt liegt wie im SVG bei 35 % - deshalb wird der Mittelpunkt
        # der inneren Kreise leicht verschoben.
        schritte = 220
        for i in range(schritte, -1, -1):
            anteil = i / float(schritte)          # 1.0 = Rand, 0.0 = Mitte
            if anteil > 0.65:
                # aussen: von #6dac20 nach #568819
                q = (anteil - 0.65) / 0.35
                farbe = tuple(int(GRUEN[k] + (GRUEN_DUNKEL[k] - GRUEN[k]) * q)
                              for k in range(3))
            else:
                q = anteil / 0.65
                farbe = tuple(int(GRUEN_HELL[k] + (GRUEN[k] - GRUEN_HELL[k]) * q)
                              for k in range(3))
            r = R_SCHEIBE * anteil * f
            # Brennpunkt bei 35 %: die inneren Kreise wandern nach oben links
            cx = (MITTE - (MITTE - 512 * 0.35) * (1 - anteil)) * f
            cy = cx
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=farbe + (255,))

        # Innerer Ring, 35 % Deckung
        r = R_RING * f
        c = MITTE * f
        d.ellipse([c - r, c - r, c + r, c + r], outline=(255, 255, 255, 89),
                  width=max(1, int(round(3 * f))))

        # Motiv
        d.polygon(sk(BLITZ), fill=WEISS + (255,))
        d.polygon(sk(WAGEN), fill=WEISS + (255,))
        d.polygon(sk(FENSTER_VORN), fill=GRUEN + (255,))
        d.polygon(sk(FENSTER_HINTEN), fill=GRUEN + (255,))
        for x, y in RAEDER:
            rr = R_REIFEN * f
            d.ellipse([x * f - rr, y * f - rr, x * f + rr, y * f + rr],
                      fill=WEISS + (255,))
        for x, y in RAEDER:
            rr = R_NABE * f
            d.ellipse([x * f - rr, y * f - rr, x * f + rr, y * f + rr],
                      fill=GRUEN + (255,))

        # Gestrichelte Trennlinie - dieselben Laengen wie im SVG
        x1, y1, x2, _ = TRENNLINIE
        x = x1
        while x < x2:
            bis = min(x + STRICH_LANG, x2)
            d.line([(x * f, y1 * f), (bis * f, y1 * f)],
                   fill=(255, 255, 255, 204), width=max(1, int(round(STRICH_DICKE * f))))
            x = bis + STRICH_LUECKE

        # Schrift
        for t in TEXTE:
            schrift, pfad = schrift_suchen(t["fett"], int(round(t["groesse"] * f)))
            if schrift is None:
                print("[FEHL] Keine Schriftdatei gefunden - der Text fehlt im PNG %d." % g)
                fehler += 1
                continue
            # Sperrung: PIL kennt kein letter-spacing, also Zeichen fuer Zeichen.
            sp = t["sperrung"] * f
            breiten = [d.textlength(ch, font=schrift) for ch in t["text"]]
            gesamt = sum(breiten) + sp * (len(t["text"]) - 1)
            x = MITTE * f - gesamt / 2.0
            for ch, w in zip(t["text"], breiten):
                d.text((x, t["y"] * f), ch, font=schrift, fill=WEISS + (255,),
                       anchor="ls")
                x += w + sp

        klein = bild.resize((g, g), Image.LANCZOS)
        if probe:
            print("[PROBE] %s waere geschrieben (%d x %d)." % ("icon_%d.png" % g, g, g))
        else:
            klein.save(ziel / ("icon_%d.png" % g))
            print("[OK]   icon_%d.png geschrieben." % g)
    return fehler


def main() -> int:
    if len(sys.argv) < 2:
        print("Aufruf: byd_symbol_erzeugen.py <pluginordner> [--probe]")
        return 2
    wurzel = Path(sys.argv[1])
    if not (wurzel / "webfrontend").is_dir():
        print("[FEHL] %s sieht nicht wie ein Plugin-Ordner aus (kein webfrontend/)."
              % wurzel)
        return 2
    probe = "--probe" in sys.argv
    ziel = wurzel / "icons"
    ziel.mkdir(parents=True, exist_ok=True)

    svg = svg_bauen()
    if probe:
        print("[PROBE] icon.svg waere geschrieben (%d Byte)." % len(svg.encode("utf-8")))
    else:
        # Binaer schreiben: open(p, 'w') uebersetzt unter Windows still jedes
        # \n zu \r\n, und die SVG der Reihe sind LF.
        (ziel / "icon.svg").write_bytes(svg.encode("utf-8"))
        print("[OK]   icon.svg geschrieben (%d Byte, LF)." % len(svg.encode("utf-8")))

    fehler = png_bauen([64, 128, 256, 512], ziel, probe)
    if fehler:
        print("[FEHL] %d PNG unvollstaendig." % fehler)
        return 1
    print("[OK]   Geometrie steht an EINER Stelle; SVG und PNG leiten daraus ab.")
    print("[INFO] Das 64er-Bild ansehen: das ist die Groesse in der "
          "Plugin-Uebersicht. Was dort zerfliesst, ist kein Symbol.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
