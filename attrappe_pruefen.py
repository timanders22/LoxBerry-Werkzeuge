#!/usr/bin/env python3
"""Deckt die LoxBerry-Attrappe noch, was die Plugins benutzen?

Die Attrappe unter `lb_attrappe/libs/phplib/` ist eine HANDGESCHRIEBENE
Nachbildung - kein Klon. Sie bildet nach, was die Plugins wirklich rufen.
Das hat einen Vorteil (sie laeuft unter Windows und ohne LoxBerry) und eine
Gefahr: das Original entwickelt sich weiter, und eine Nachbildung, die
danebenliegt, prueft gegen etwas, das es nicht gibt.

Gefragt wird deshalb nicht "ist die Attrappe vollstaendig" - das soll sie
gar nicht sein -, sondern:

  1. Welche SDK-Namen rufen die Plugins im Arbeitsordner?
  2. Welche davon kennt die Attrappe NICHT?          <- die Luecke
  3. Welche kennt sie, die es im Original nicht mehr gibt?  <- die Leiche
  4. Weichen die Signaturen ab?

    python3 attrappe_pruefen.py [--tag 4.0.0.15] [--ohne-netz]

Rueckgabe 0, wenn keine Luecke und keine Leiche gefunden wurde.
"""
import io
import os
import re
import sys
import urllib.request

HIER = os.path.dirname(os.path.abspath(__file__))
ARBEIT = os.path.dirname(HIER)
ATTRAPPE = os.path.join(HIER, 'lb_attrappe', 'libs', 'phplib')
DATEIEN = ('loxberry_system.php', 'loxberry_web.php',
           'loxberry_log.php', 'loxberry_io.php')
ROH = 'https://raw.githubusercontent.com/mschlenstedt/Loxberry/%s/libs/phplib/%s'

argv = sys.argv[1:]
TAG = argv[argv.index('--tag') + 1] if '--tag' in argv else None
OHNE_NETZ = '--ohne-netz' in argv


def hole(url, sekunden=20):
    try:
        with urllib.request.urlopen(url, timeout=sekunden) as r:
            return r.read().decode('utf-8', 'replace')
    except Exception as e:
        return None


def neueste_fassung():
    """Die neueste NICHT-Vorabfassung aus den Releases."""
    import json
    t = hole('https://api.github.com/repos/mschlenstedt/Loxberry/releases?per_page=20')
    if not t:
        return None
    for r in json.loads(t):
        if not r.get('prerelease'):
            return r['tag_name']
    return None


# PHP-Eigennamen und Sprachbestandteile - sie stehen in jeder Klasse und
# haben mit dem SDK nichts zu tun. Ohne diese Liste meldete das Werkzeug
# beim ersten Lauf "__construct" als fehlende SDK-Funktion.
KEIN_SDK = frozenset((
    '__construct', '__destruct', '__toString', '__get', '__set', '__call',
    '__invoke', '__clone', 'class Exception',
))


def namen(text):
    """Funktionen, Klassen und deren statische Methoden - mit Argumentzahl."""
    aus = {}
    for m in re.finditer(r'(?m)^\s*function\s+(\w+)\s*\(([^)]*)\)', text):
        aus[m.group(1)] = m.group(2).strip()
    for m in re.finditer(r'(?m)^\s*(?:public\s+)?static\s+function\s+(\w+)\s*\(([^)]*)\)', text):
        aus[m.group(1)] = m.group(2).strip()
    for m in re.finditer(r'(?m)^\s*class\s+(\w+)', text):
        aus['class ' + m.group(1)] = ''
    for k in list(aus):
        if k in KEIN_SDK:
            del aus[k]
    return aus


def argzahl(sig):
    """Pflichtargumente und Gesamtzahl aus einer Argumentliste."""
    if not sig.strip():
        return (0, 0)
    teile = [t for t in re.split(r',(?![^(]*\))', sig) if t.strip()]
    pflicht = sum(1 for t in teile if '=' not in t)
    return (pflicht, len(teile))


def main():
    print('== LoxBerry-Attrappe gegen das Original ==\n')

    tag = TAG
    if not tag and not OHNE_NETZ:
        tag = neueste_fassung()
    if not tag:
        print('  -- Fassung nicht feststellbar (kein Netz?) - nicht gemessen')
        return 0
    print('  Original: mschlenstedt/Loxberry, Fassung %s' % tag)

    # ---- die Namen der Attrappe ----
    attr = {}
    for d in DATEIEN:
        p = os.path.join(ATTRAPPE, d)
        if not os.path.isfile(p):
            print('  ROT  Attrappe unvollstaendig: %s fehlt' % d)
            return 1
        attr.update(namen(io.open(p, encoding='utf-8').read()))

    # ---- die Namen des Originals ----
    echt = {}
    for d in DATEIEN:
        t = hole(ROH % (tag, d))
        if t is None:
            print('  -- %s nicht abrufbar - nicht gemessen' % d)
            return 0
        echt.update(namen(t))
    print('  Attrappe: %d Namen, Original: %d Namen\n' % (len(attr), len(echt)))

    # ---- was rufen die Plugins? ----
    gerufen = {}
    for eintrag in sorted(os.listdir(ARBEIT)):
        ordner = os.path.join(ARBEIT, eintrag)
        if not eintrag.startswith('LoxBerry-Plugin-') or not os.path.isdir(ordner):
            continue
        for wurzel, _, ds in os.walk(ordner):
            for f in ds:
                if not f.endswith('.php'):
                    continue
                try:
                    t = io.open(os.path.join(wurzel, f), encoding='utf-8',
                                errors='replace').read()
                except Exception:
                    continue
                for n in set(echt) | set(attr):
                    if n.startswith('class '):
                        if re.search(r'\b' + n[6:] + r'\s*::', t):
                            gerufen.setdefault(n, set()).add(eintrag)
                    elif re.search(r'(?<![\w$>])' + re.escape(n) + r'\s*\(', t):
                        gerufen.setdefault(n, set()).add(eintrag)
    print('  Von den Plugins gerufen: %d Namen\n' % len(gerufen))

    fehler = 0

    # ---- 1. Die LUECKE: gerufen, im Original vorhanden, in der Attrappe nicht ----
    luecke = sorted(n for n in gerufen if n in echt and n not in attr)
    print('  --- Luecke: von Plugins gerufen, Attrappe kennt es nicht ---')
    if luecke:
        for n in luecke:
            wer = sorted(gerufen[n])
            print('    ROT  %-34s %s%s' % (n, ', '.join(w[16:] for w in wer[:3]),
                                           ' …' if len(wer) > 3 else ''))
        fehler += len(luecke)
    else:
        print('    keine')

    # ---- 2. Die LEICHE: in der Attrappe, im Original nicht mehr ----
    leiche = sorted(n for n in attr if n not in echt and not n.startswith('_'))
    print('\n  --- Leiche: Attrappe kennt es, das Original nicht (mehr) ---')
    if leiche:
        for n in leiche:
            print('    ROT  %-34s %s' % (n, 'wird gerufen!' if n in gerufen else '(niemand ruft es)'))
        fehler += len(leiche)
    else:
        print('    keine')

    # ---- 3. Signaturen der gemeinsamen Namen ----
    print('\n  --- Signaturen der nachgebildeten Namen ---')
    krumm = 0
    for n in sorted(set(attr) & set(echt)):
        if n.startswith('class '):
            continue
        a, e = argzahl(attr[n]), argzahl(echt[n])
        # Die Attrappe darf MEHR annehmen als noetig, aber nicht weniger:
        # ein Aufruf mit e[1] Argumenten muss durchgehen, und ein Aufruf mit
        # e[0] Pflichtargumenten auch.
        if a[1] < e[1] or a[0] > e[0]:
            print('    ROT  %-30s Attrappe (%d..%d), Original (%d..%d)'
                  % (n, a[0], a[1], e[0], e[1]))
            krumm += 1
    if krumm == 0:
        print('    alle %d vertragen die Aufrufe des Originals'
              % len(set(attr) & set(echt)))
    fehler += krumm

    # ---- 4. VIER Staende, eine Wahrheit ----
    #
    # Der teuerste Befund vom 25.08.2026: es gibt nicht eine Attrappe,
    # sondern vier Ordner mit derselben phplib - lb, lb_attrappe, lb_leer
    # und lb_mqtt. Drei davon waren veraltet, und ausgerechnet der
    # gepflegte (lb_attrappe) wurde von genau EINEM Werkzeug benutzt.
    # rendern.py, wirkungstest.py und zwei weitere lasen `lb`.
    #
    # Eine Nachbesserung an lb_attrappe haette also nichts bewirkt, und
    # niemand haette es gemerkt. Deshalb ist die Gleichheit ab jetzt Teil
    # der Pruefung.
    import hashlib
    staende = [d for d in ('lb', 'lb_attrappe', 'lb_leer', 'lb_mqtt')
               if os.path.isdir(os.path.join(HIER, d, 'libs', 'phplib'))]
    print('\n  --- Alle Staende tragen dieselbe phplib ---')
    ungleich = 0
    for d in DATEIEN:
        summen = {}
        for st in staende:
            p = os.path.join(HIER, st, 'libs', 'phplib', d)
            if not os.path.isfile(p):
                summen.setdefault('(fehlt)', []).append(st)
                continue
            h = hashlib.md5(io.open(p, 'rb').read()).hexdigest()[:8]
            summen.setdefault(h, []).append(st)
        if len(summen) > 1:
            print('    ROT  %-24s %s' % (d, ' | '.join(
                '%s: %s' % (h, ', '.join(v)) for h, v in sorted(summen.items()))))
            ungleich += 1
    if ungleich == 0:
        print('    alle %d Staende gleich (%s)' % (len(staende), ', '.join(staende)))
    fehler += ungleich

    print('\n== %d Befund(e) ==' % fehler)
    return 1 if fehler else 0


if __name__ == '__main__':
    sys.exit(main())
