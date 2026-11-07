#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Jeden Reiter einzeln rendern - mit wirklich gefuelltem `$_GET`.

WOZU
====
`rendern.py` misst unter der Kommandozeile IMMER den Vorgabereiter: PHP fuellt
dort `$_GET` nicht aus `QUERY_STRING` - weder mit `variables_order=EGPCS` noch
mit `register_argc_argv=0` (beides am 20.08.2026 gemessen). Ein Lauf gegen
`?form=<reiter>` sieht aus, als habe er alle Reiter geprueft, und hat es nicht.

Dieses Werkzeug haengt deshalb `vorlauf_getpost.php` ein und ruft jeden Reiter
einzeln, unter PHP 7.4 UND 8.4, in jeder verlangten Sprache. Gemessen wird je
Lauf:

  * die Befunde des Fehler-Aufnehmers (HINWEIS, WARNUNG, VERFALL, FATAL)
  * ob der ANGEFORDERTE Reiter auch der offene ist (`sm-active`) - ohne
    JavaScript; ist keiner offen, ist die Seite ohne Skript unbedienbar
  * ob ein unaufgeloester Sprachschluessel (`ABSCHNITT.NAME`) im HTML steht -
    genau die Form, in der ein verlorener Schluessel am Bildschirm stuende
  * die Laenge der Ausgabe

Die Reiterliste wird aus der Oberflaeche GELESEN (`index.php?form=<name>`),
nicht gepflegt - eine gepflegte Liste waere eine zweite Wahrheit.

WO ES BLIND IST
===============
Die Netzsperre wirkt hier nur halb. Der Sperr-Proxy von `rendern.py` faengt
curl; die STROEME (`file_get_contents('http://…')`) faengt sonst der Wrapper
aus `vorlauf.php` - und der ist hier nicht eingehaengt, weil dieser Lauf
`vorlauf_getpost.php` braucht (beides in EINER Datei gaebe es nur um den Preis
einer dritten Fassung derselben Sache). Eine Seite, die beim Aufbau ueber einen Strom
nach aussen greift, tut das also wirklich, und was sie daraus macht, steht als
Befund im Bericht. Bei einem Selbsttest gegen `127.0.0.1` ist das Rauschen der
Umgebung: gegenpruefen, ob dieselbe Zeile auch in der VORIGEN Fassung steht.

Anlass: APC-UPS 1.2.8, 13.09.2026. Die Sprachdateien waren neu geschrieben
worden; `rendern.py` allein haette vier der fuenf Reiter nie angesehen.

AUFRUF
======
    python3 reiterlauf.py <Plugin-Ordner> [--sprachen de,en] [--aus <Ordner>]
                          [--reiter a,b,c] [--stand-leeren]

    --stand-leeren  Leert vor dem Lauf `lb/config/plugins/<ordner>`,
           `lb/data/plugins/<ordner>` und `lb/log/plugins/<ordner>`. Noetig,
           wenn zwei Fassungen VERGLICHEN werden sollen: `rendern.py` leitet
           diese Pfade aus dem Ordnernamen ab, jede Fassung hat also ihren
           eigenen Pruefstand, und ein Protokoll, das nur eine Seite gesehen
           hat, steht danach als Unterschied in der Seite (gemessen
           13.09.2026: 1162 Zeichen im Reiter „Logdateien").

    --vorlauf <datei>  Ein anderer `auto_prepend_file` als `vorlauf_getpost.php`.
           Nur fuer die Eichung gedacht: damit laesst sich vorfuehren, dass der
           Vorgabewert fuer REQUEST_METHOD wirklich gebraucht wird. Im Alltag
           nicht setzen.

    --aus  Ordner fuer das gelieferte HTML. Vorgabe:
           Werkzeuge/lb/reiterlauf/<Ordnername>_<Sprache>/
           Er wird VOR jedem Lauf geleert - ein Sammelordner traegt sonst
           Dateien frueherer, auch misslungener Laeufe weiter und der naechste
           Vergleich misst die alten mit (gemessen 13.09.2026).

Rueckgabe 0 = kein Befund, 1 = Befund, 2 = nichts gemessen / Aufrufproblem.
Rein lesend fuer den Plugin-Ordner; geschrieben wird nur das HTML im
Ausgabeordner (Pruefstand).
"""
import io
import os
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import rendern

# os.path.realpath(): liegt der Ausgabe- oder Werkzeugpfad unter einer kurzen
# Windows-Form (C:\Users\ABCDEF~1\...), bricht das '~' den ini-Parser von
# `php -d` - und die Option wird STILL verworfen. Die Seite liefert dann ein
# paar hundert Byte statt zehntausender. Gemessen 17.08.2026, am 13.09.2026
# wieder aufgelaufen.
#
# vorlauf_getpost.php setzt seit 13.09.2026 auch den Vorgabewert fuer
# $_SERVER['REQUEST_METHOD']. Bis dahin hing hier eine eigene Datei
# (vorlauf_reiter.php), die nichts anderes tat als das nachzutragen; sie ist
# mit der Berichtigung weggefallen.
rendern.VORLAUF = Path(os.path.realpath(str(HIER / 'vorlauf_getpost.php')))

# Ein unaufgeloester Schluessel sieht aus wie EINST.SICH_FEHLEND: zwei Teile
# in Grossbuchstaben, durch einen Punkt getrennt, ohne Leerzeichen. Das Muster
# darf nicht auf Dateinamen oder MQTT-Themen anschlagen - deshalb je Teil
# mindestens drei Zeichen und kein Kleinbuchstabe.
SCHLUESSEL = re.compile(r'\b[A-Z][A-Z0-9_]{2,}\.[A-Z][A-Z0-9_]{2,}\b')


def _feste(argv, wertflaggen):
    """Die Argumente ohne Schalter - und ohne deren WERTE.

    Ohne diese Unterscheidung landet der Wert eines Schalters in getrennter
    Schreibweise (`--sprachen de,en`) unter den festen Argumenten, und die
    Zaehlung darunter weist einen richtigen Aufruf ab.
    """
    aus = []
    ueberspringen = False
    for a in argv:
        if ueberspringen:
            ueberspringen = False
            continue
        if a.startswith('--'):
            ueberspringen = a in wertflaggen
            continue
        aus.append(a)
    return aus


def _wert(argv, name, vorgabe=None):
    for i, a in enumerate(argv):
        if a == name and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith(name + '='):
            return a.split('=', 1)[1]
    return vorgabe


def reiter_lesen(datei):
    """Die Reiternamen aus der Oberflaeche selbst: index.php?form=<name>."""
    t = io.open(datei, 'rb').read().decode('utf-8', 'replace')
    namen = []
    for m in re.finditer(r'index\.php\?form=([A-Za-z0-9_-]+)', t):
        if m.group(1) not in namen:
            namen.append(m.group(1))
    return namen


def stand_leeren(name):
    """config/, data/ und log/ dieses Ordnernamens unter lb/ leeren.

    Nur DIESE drei Pfade und nur die Dateien darin - der Pruefstand selbst
    bleibt stehen. Was geleert wurde, steht im Bericht.
    """
    geleert = 0
    for zweig in ('config', 'data', 'log'):
        d = HIER / 'lb' / zweig / 'plugins' / name.lower()
        if not d.is_dir():
            continue
        for f in sorted(d.rglob('*')):
            if f.is_file():
                f.unlink()
                geleert += 1
        print('  geleert: %s' % d)
    print('  %d Datei(en) aus dem Pruefstand entfernt' % geleert)


def lauf(ordner, sprache, aus, reiter, sperre):
    datei = ordner / 'webfrontend' / 'htmlauth' / 'index.php'
    if aus.is_dir():
        for alt in aus.iterdir():
            if alt.is_file():
                alt.unlink()
    aus.mkdir(parents=True, exist_ok=True)
    fehl = 0
    n = 0
    for r in reiter:
        for v, php in rendern.PHPS:
            if not Path(php).is_file():
                print('  PHP %s liegt nicht bereit - NICHT gemessen' % v)
                fehl += 1
                continue
            os.environ['QUERY_STRING'] = 'form=%s&lang=%s' % (r, sprache)
            vorher = len(sperre.ziele)
            sperre.stroeme = []
            out, bef, rest = rendern.lauf(php, datei, ordner.name, sperre)
            abgewiesen = sperre.ziele[vorher:] + sperre.stroeme
            n += 1
            io.open(aus / ('%s_%s_%s.html' % (r, sprache, v.replace('.', ''))),
                    'w', encoding='utf-8').write(out)
            zeile = '  %-10s [%s] %6d Zeichen' % (r, v, len(out))
            if bef:
                zeile += '  BEFUNDE: ' + ' | '.join(bef)
                fehl += len(bef)
            if rest:
                zeile += '  STDERR: ' + rest[:150]
                fehl += 1
            offen = re.findall(r'class="[^"]*\bsm-active\b[^"]*"\s+id="tab-([A-Za-z0-9_-]+)"', out)
            if not offen:
                zeile += '  KEIN REITER OFFEN (ohne JavaScript unbedienbar)'
                fehl += 1
            elif r not in offen:
                zeile += '  OFFEN IST %s, ANGEFORDERT WAR %s' % (','.join(offen), r)
                fehl += 1
            roh = sorted(set(SCHLUESSEL.findall(out)))
            if roh:
                zeile += '  UNAUFGELOESTE SCHLUESSEL: ' + ', '.join(roh)
                fehl += len(roh)
            if abgewiesen:
                zeile += '  NETZ ABGEWIESEN (kein Befund): ' + ', '.join(
                    sorted(set(rendern.Netzsperre.wirt(z) for z in abgewiesen)))
            if len(out) < 500:
                zeile += '  AUSGABE ZU KURZ'
                fehl += 1
            print(zeile)
    return n, fehl


def main(argv):
    fest = _feste(argv, ('--sprachen', '--aus', '--reiter', '--vorlauf'))
    if len(fest) != 1:
        sys.stderr.write(__doc__.split('AUFRUF')[1].strip() + '\n')
        return 2
    ordner = Path(fest[0]).resolve()
    datei = ordner / 'webfrontend' / 'htmlauth' / 'index.php'
    if not datei.is_file():
        sys.stderr.write('ABBRUCH: keine webfrontend/htmlauth/index.php unter %s\n' % ordner)
        return 2

    sprachen = [s.strip() for s in (_wert(argv, '--sprachen', 'de,en')).split(',') if s.strip()]
    vorgabe_reiter = _wert(argv, '--reiter')
    reiter = ([r.strip() for r in vorgabe_reiter.split(',') if r.strip()]
              if vorgabe_reiter else reiter_lesen(datei))
    if not reiter:
        sys.stderr.write('ABBRUCH: kein Reiter gefunden (kein index.php?form=… in der '
                         'Oberflaeche) - nichts gemessen\n')
        return 2
    aus_vorgabe = _wert(argv, '--aus')
    eigener = _wert(argv, '--vorlauf')
    if eigener:
        rendern.VORLAUF = Path(os.path.realpath(eigener))
        print('Vorlauf (abweichend): %s' % rendern.VORLAUF)

    print('%s: %d Reiter (%s), %d Sprache(n)'
          % (ordner.name, len(reiter), ', '.join(reiter), len(sprachen)))
    if '--stand-leeren' in argv:
        stand_leeren(ordner.name)
    sperre = rendern.Netzsperre()
    n = fehl = 0
    try:
        for sp in sprachen:
            aus = (Path(aus_vorgabe) / sp if aus_vorgabe
                   else HIER / 'lb' / 'reiterlauf' / ('%s_%s' % (ordner.name, sp)))
            print('== %s -> %s' % (sp, aus))
            a, b = lauf(ordner, sp, aus, reiter, sperre)
            n += a
            fehl += b
    finally:
        sperre.ende()
    print('reiterlauf.py: %d Lauf/Laeufe, %d Befund(e).' % (n, fehl))
    if n == 0:
        print('NICHTS GERENDERT - das ist kein sauberer Lauf.')
        return 2
    return 1 if fehl else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
