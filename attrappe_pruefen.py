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
                                [--plugin ORDNER]

--plugin schraenkt Frage 1 auf EIN Plugin ein. Ohne die Angabe wird der
ganze Arbeitsordner gelesen - das ist fuer den freien Lauf richtig, fuer
eine Freigabepruefung aber nicht: sonst faerbt die Luecke des einen
Plugins die Freigabe eines anderen rot. Die Fragen 2 bis 4 messen den
PRUEFSTAND selbst und bleiben deshalb immer ordnerweit.

--ohne-netz schaltet die Fragen 1 bis 3 ab - sie vergleichen gegen das
Original auf GitHub. Frage 4 (vier Staende, eine phplib) laeuft trotzdem:
sie vergleicht vier Ordner auf dieser Platte. Bis zum 29.08.2026 fiel sie
mit den drei anderen aus, obwohl sie nie ein Netz gebraucht hat.

Die Schlusszeile nennt die Zahl der Befunde, die Zeile darunter, WELCHE
Fragen gestellt wurden. Eine 0 aus einem Lauf, der drei Fragen gar nicht
gestellt hat, ist kein Haken - wer nur die Zahl liest, hat drei Pruefungen
weniger, als er glaubt.

Rueckgabe 0, wenn keine Luecke und keine Leiche gefunden wurde.
"""
import io
import os
import re
import sys
import urllib.error
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
PLUGIN = argv[argv.index('--plugin') + 1] if '--plugin' in argv else None


# Warum der Grund festgehalten wird: bis zum 31.08.2026 gab hole() bei jedem
# Fehler None zurueck. Ein 403 wegen erschoepfter Abrufgrenze sah damit aus
# wie ein Rechner ohne Netz, und gemeldet wurde "kein Netz?" - eine Ursache,
# die nicht stimmte. Gemessen an einem Durchgang ueber 41 Linien: ab der 24.
# war die Pruefung blind, das Freigabetor daneben meldete weiter "0 von 13".
GRUND = None


def hole(url, sekunden=20):
    global GRUND
    try:
        with urllib.request.urlopen(url, timeout=sekunden) as r:
            return r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        rest = e.headers.get('x-ratelimit-remaining')
        if e.code in (403, 429) and rest == '0':
            import datetime
            wann = e.headers.get('x-ratelimit-reset')
            uhr = ''
            if wann and wann.isdigit():
                uhr = datetime.datetime.fromtimestamp(int(wann)).strftime(' bis %H:%M')
            GRUND = 'GitHub-Abrufgrenze erschoepft%s' % uhr
        else:
            GRUND = 'HTTP %s' % e.code
        return None
    except Exception as e:
        GRUND = '%s' % (e.__class__.__name__,)
        return None


def zwischenspeicher(name, minuten=30):
    """Pfad im Temp-Verzeichnis, wenn er frisch genug ist - sonst None.

    ANGELEGT 31.08.2026. neueste_fassung() holte die Release-Liste des Kerns
    bei jedem Aufruf neu; ueber 41 Plugins waren das 41 Abfragen bei einem
    Kontingent von 60 je Stunde, alle mit derselben Antwort. Der Speicher
    liegt im Temp-Verzeichnis, nicht im Arbeitsordner: er ist ein
    Messhilfsmittel, kein Bestand.
    """
    import tempfile
    import time
    p = os.path.join(tempfile.gettempdir(), name)
    if os.path.isfile(p) and time.time() - os.path.getmtime(p) < minuten * 60:
        return p
    return None


def neueste_fassung():
    """Die neueste NICHT-Vorabfassung aus den Releases.

    Die Antwort ist fuer jedes Plugin dieselbe und wird deshalb eine halbe
    Stunde lang aufgehoben - siehe zwischenspeicher().
    """
    import json
    import tempfile
    name = 'lb_kern_releases.json'
    p = zwischenspeicher(name)
    t = None
    if p:
        try:
            with open(p, encoding='utf-8') as fh:
                t = fh.read()
        except OSError:
            t = None
    if t is None:
        t = hole('https://api.github.com/repos/mschlenstedt/Loxberry/releases?per_page=20')
        if t:
            try:
                with open(os.path.join(tempfile.gettempdir(), name), 'w',
                          encoding='utf-8') as fh:
                    fh.write(t)
            except OSError:
                pass
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


def staende_pruefen():
    """Frage 4: VIER Staende, eine Wahrheit - und das OHNE Netz.

    Der teuerste Befund vom 25.08.2026: es gibt nicht eine Attrappe,
    sondern vier Ordner mit derselben phplib - lb, lb_attrappe, lb_leer
    und lb_mqtt. Drei davon waren veraltet, und ausgerechnet der
    gepflegte (lb_attrappe) wurde von genau EINEM Werkzeug benutzt.
    rendern.py, wirkungstest.py und zwei weitere lasen `lb`.

    Eine Nachbesserung an lb_attrappe haette also nichts bewirkt, und
    niemand haette es gemerkt. Deshalb ist die Gleichheit Teil der Pruefung.

    HERAUSGELOEST am 29.08.2026. Diese Frage vergleicht vier Ordner auf
    dieser Platte - sie braucht das Original nicht und hat nie eines
    gebraucht. Sie hing trotzdem am selben Aufruf wie die drei Netzfragen
    und fiel mit ihnen aus: ohne Netz stieg main() aus, bevor sie an der
    Reihe war. Damit war ausgerechnet die Frage, die am 29.08.2026 wirklich
    anschlug - drei Staende waren nicht nachgezogen -, im Zug ohne Empfang
    und hinter jeder Firmensperre nicht messbar.
    """
    import hashlib
    staende = [d for d in ('lb', 'lb_attrappe', 'lb_leer', 'lb_mqtt')
               if os.path.isdir(os.path.join(HIER, d, 'libs', 'phplib'))]
    print('\n  --- Alle Staende tragen dieselbe phplib ---')
    if not staende:
        print('    ROT  kein einziger Stand gefunden')
        return 1
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
    return ungleich


def main():
    print('== LoxBerry-Attrappe gegen das Original ==\n')

    fehler = 0
    gemessen = []
    offen = []

    # ---- die Namen der Attrappe: liegen hier, brauchen kein Netz ----
    attr = {}
    fehlt = []
    for d in DATEIEN:
        p = os.path.join(ATTRAPPE, d)
        if not os.path.isfile(p):
            fehlt.append(d)
            continue
        attr.update(namen(io.open(p, encoding='utf-8').read()))
    if fehlt:
        # Frueher ein sofortiges `return 1`. Das nahm Frage 4 die Gelegenheit -
        # und gerade eine unvollstaendige Attrappe will man dort sehen.
        print('  ROT  Attrappe unvollstaendig: %s fehlt' % ', '.join(fehlt))
        fehler += len(fehlt)

    # ---- die Namen des Originals: NUR dafuer ist das Netz noetig ----
    #
    # Bei unvollstaendiger Attrappe wird gar nicht erst geholt. Die Fragen 1
    # bis 3 vergleichen dann eine halb gelesene Attrappe mit dem ganzen
    # Original, und JEDER Name der fehlenden Datei sieht aus wie eine Luecke.
    # Beim Nachstellen wurden aus einer fehlenden Datei sechs Befunde, vier
    # davon erfunden. Nicht messbar heisst nicht messbar - nicht "raten".
    tag = TAG
    if not fehlt and not tag and not OHNE_NETZ:
        tag = neueste_fassung()
    echt = {}
    grund = ''
    if fehlt:
        grund = 'Attrappe unvollstaendig'
    elif not tag:
        grund = ('ohne Netz' if OHNE_NETZ else
                 'Fassung nicht feststellbar: ' + (GRUND or 'kein Netz'))
    else:
        print('  Original: mschlenstedt/Loxberry, Fassung %s' % tag)
        for d in DATEIEN:
            tx = hole(ROH % (tag, d))
            if tx is None:
                grund = '%s nicht abrufbar' % d
                echt = {}
                break
            echt.update(namen(tx))

    if echt:
        print('  Attrappe: %d Namen, Original: %d Namen\n' % (len(attr), len(echt)))

        # ---- was rufen die Plugins? ----
        gerufen = {}
        leer_pfad = False
        if PLUGIN:
            pfad = os.path.abspath(PLUGIN)
            if not os.path.isdir(pfad):
                print('  ROT  --plugin zeigt ins Leere: %s' % pfad)
                fehler += 1
                leer_pfad = True
            pruefling = [(os.path.basename(pfad), pfad)]
        else:
            pruefling = [(x, os.path.join(ARBEIT, x))
                         for x in sorted(os.listdir(ARBEIT))
                         if x.startswith('LoxBerry-Plugin-')
                         and os.path.isdir(os.path.join(ARBEIT, x))]
        for eintrag, ordner in pruefling:
            for wurzel, _, ds in os.walk(ordner):
                for f in ds:
                    if not f.endswith('.php'):
                        continue
                    try:
                        tq = io.open(os.path.join(wurzel, f), encoding='utf-8',
                                     errors='replace').read()
                    except Exception:
                        continue
                    for n in set(echt) | set(attr):
                        if n.startswith('class '):
                            if re.search(r'\b' + n[6:] + r'\s*::', tq):
                                gerufen.setdefault(n, set()).add(eintrag)
                        elif re.search(r'(?<![\w$>])' + re.escape(n) + r'\s*\(', tq):
                            gerufen.setdefault(n, set()).add(eintrag)
        print('  Von den Plugins gerufen: %d Namen (%s)\n'
              % (len(gerufen), os.path.basename(os.path.abspath(PLUGIN)) if PLUGIN
                 else '%d Plugins im Arbeitsordner' % len(pruefling)))

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
                print('    ROT  %-34s %s'
                      % (n, 'wird gerufen!' if n in gerufen else '(niemand ruft es)'))
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
        gemessen += ['Leiche', 'Signaturen']
        if leer_pfad:
            # Ohne Ordner hat os.walk nichts zu lesen. "keine Luecke" waere
            # dann geraten, nicht gemessen - und die Zeile darunter, die es
            # behauptet, ist das eigentliche Uebel.
            offen.append('Luecke (--plugin-Pfad fehlt)')
        else:
            gemessen.insert(-2, 'Luecke')
    else:
        # Kein Original - aber das ist KEIN Grund, gar nichts zu messen.
        print('  Attrappe: %d Namen, Original: nicht gelesen (%s)\n'
              % (len(attr), grund))
        print('  --- Luecke / Leiche / Signaturen ---')
        print('    -- ohne das Original nicht messbar')
        offen.append('Luecke, Leiche, Signaturen (%s)' % grund)

    # ---- 4. Die vier Staende: immer, auch ohne Netz ----
    fehler += staende_pruefen()
    gemessen.append('Staende')

    # Die Schlusszeilen sind das, was freigabe_pruefen.py liest. Die Zahl
    # allein genuegt nicht: eine 0 aus einem Lauf, der drei von vier Fragen
    # gar nicht gestellt hat, ist kein Haken. Deshalb steht darunter, was
    # gemessen wurde und was nicht.
    print('\n== %d Befund(e) ==' % fehler)
    print('   gemessen: %s' % ', '.join(gemessen))
    if offen:
        print('   nicht gemessen: %s' % '; '.join(offen))
    return 1 if fehler else 0


if __name__ == '__main__':
    sys.exit(main())
