#!/usr/bin/env python3
"""Ist der Sicherungszweig ueberhaupt ANGESCHLOSSEN?

sicherung_wirkung.py misst die Lesefunktion - ob eine gueltige Datei
uebernommen und eine fremde abgelehnt wird. Das ist die halbe Miete. Die
andere Haelfte ist die Frage, ob der Zweig jemals anlaeuft, und die hat
diese Pruefung lange nicht gestellt.

Gemessen am 26.08.2026: ZWOELF Linien trugen einen Zweig der Form

    if ($ap_post && isset($_POST['ap_sichern'])) { ... }

waehrend die Datei ihre Wache $ap_ist_post nennt. PHP wertet eine
undefinierte Variable als false aus, ohne Fehler und ohne Warnung im
Protokoll. Die Seite zeigte zwei Knoepfe, die Wirkungspruefung meldete
gruen - und kein Knopfdruck tat je etwas.

Geprueft wird deshalb die VERDRAHTUNG, in vier Punkten:

    1. die Variable der POST-Bedingung wird zugewiesen - und zwar VOR dem
       Zweig, nicht irgendwo
    2. die Fehlerablage gibt es, und sie wird vorher angelegt
    3. die Meldungsablage ebenso
    4. die Uebersetzungsfunktion, die der Zweig ruft, ist erreichbar

Rueckgabewert 1, wenn etwas fehlt - fuer die Pruefkette.

    python3 sicherung_verdrahtung.py [<Pluginordner> ...]
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HIER = os.path.dirname(os.path.abspath(__file__))
ARBEIT = os.path.dirname(HIER)

ZWEIG = re.compile(
    r"(?m)^if \((.*?) && isset\(\$_POST\['(\w+)_(sichern|zurueck)'\]\)\)")


def zuweisung(z, name, vor):
    """Zeile der ersten Zuweisung von $name - oder None."""
    m = re.compile(r'^\s*\$' + re.escape(name) + r'\s*(=[^=]|\[\]\s*=)')
    for i, y in enumerate(z[:vor]):
        if m.match(y):
            return i
    return None


def pruefe(o):
    idx = os.path.join(o, 'webfrontend', 'htmlauth', 'index.php')
    if not os.path.isfile(idx):
        return None
    s = io.open(idx, encoding='utf-8', errors='replace').read()
    z = s.split('\n')
    m = ZWEIG.search(s)
    if not m:
        return None
    zeile = s[:m.start()].count('\n')
    prae = m.group(2)
    mangel = []

    # ---- 1. die Wache ----
    v = re.match(r'^\$(\w+)$', m.group(1).strip())
    if v and zuweisung(z, v.group(1), zeile) is None:
        mangel.append('$%s nie zugewiesen' % v.group(1))

    # ---- 2./3. Fehler- und Meldungsablage ----
    # Nur der ZWEIG selbst, nicht die naechsten 3000 Zeichen: sonst zaehlen
    # Schleifenvariablen des folgenden Codes als "nie angelegt". Matter2Lox
    # meldete so acht Befunde, von denen keiner einer war.
    tiefe, j = 0, s.index('{', m.start())
    while j < len(s):
        if s[j] == '{':
            tiefe += 1
        elif s[j] == '}':
            tiefe -= 1
            if tiefe == 0:
                break
        j += 1
    block = s[m.start():j + 1]
    # Nur die ABLAGEN pruefen - erkennbar daran, dass ihnen eine Uebersetzung
    # zugewiesen wird. Alles andere im Block sind Variablen, die der Zweig
    # selbst anlegt; die vorher zu verlangen waere Unsinn.
    for name in sorted(set(re.findall(
            r'\$(\w+)(?:\[\])?\s*=\s*(?:sprintf\()?\w+_t(?:xt)?\(', block))):
        if zuweisung(z, name, zeile) is None:
            mangel.append('$%s nie angelegt' % name)

    # ---- 4. die Uebersetzung ----
    tf = re.findall(r'(\w+_t(?:xt)?)\(', block)
    if tf:
        fn = tf[0]
        da = False
        for w, _, ds in os.walk(o):
            if os.sep + '.git' in w:
                continue
            for d in ds:
                if d.endswith('.php') and re.search(
                        r'(?m)^function\s+' + fn + r'\s*\(',
                        io.open(os.path.join(w, d), encoding='utf-8',
                                errors='replace').read()):
                    da = True
                    break
            if da:
                break
        if not da:
            mangel.append('%s() nicht gefunden' % fn)
    return mangel


def main():
    ordner = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not ordner:
        ordner = [e for e in sorted(os.listdir(ARBEIT))
                  if e.startswith('LoxBerry-Plugin-')
                  and os.path.isdir(os.path.join(ARBEIT, e))]
    print('%-32s %s' % ('Plugin', 'Verdrahtung'))
    print('-' * 76)
    n = 0
    gemessen = 0
    for e in ordner:
        o = e if os.path.isdir(e) else os.path.join(ARBEIT, e)
        if not os.path.isdir(o):
            continue
        r = pruefe(o)
        if r is None:
            continue
        gemessen += 1
        if r:
            n += 1
        print('%-32s %s' % (os.path.basename(o)[16:47],
                            ('ROT ' + '; '.join(r)) if r else 'ok'))
    print('-' * 76)
    print('%d Linie(n) gemessen, %d mit Befund' % (gemessen, n))
    return 1 if n else 0


if __name__ == '__main__':
    sys.exit(main())
