#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zwei Fragen, die die Pruefkette bis zum 29.08.2026 NICHT stellen konnte.

    1. Aendert sich die Oberflaeche ueberhaupt, wenn die Sprache wechselt?
    2. Was zeigt der Reiter mit den Logdateien, wenn LoxBerry KEIN Protokoll
       kennt?

WARUM ES DIESES WERKZEUG GIBT

Beide Fragen waren unbeantwortbar, weil die SDK-Attrappe zu nachsichtig war:
lblanguage() lieferte fest 'de', und loglist_html() lieferte IMMER eine
Zeichenkette. Zwei Befunde an Midea2Lox sind daran vorbeigelaufen und erst
dem Anwender am Geraet aufgefallen:

  * die halbe Oberflaeche war fest deutsch - zwoelf Renderlaeufe in "beiden"
    Sprachen lieferten byteweise dasselbe,
  * der Reiter "Logdateien" zeigte auf dem Geraet ausser der Ueberschrift
    nichts, weil das Plugin ein Entweder-oder gebaut hatte und der
    Python-Dienst sein Protokoll nicht ueber LoxBerry::Log anmeldet.

Seit der Haertung achtet lblanguage() die Variable LBLANG, und
LB_ATTRAPPE_LOGLIST=leer laesst loglist_html() einen Leerstring liefern.
Dieses Werkzeug legt beide Schalter um. Ein Schalter, den niemand umlegt, ist
nicht vorhanden.

GEEICHT am bekannten Paar Midea2Lox 4.3.1 (kaputt) gegen 4.3.2 (heil):

    4.3.1  loglist=leer  ->  Reiter voellig leer          ROT
    4.3.2  loglist=leer  ->  Pfad und Inhalt stehen da    GRUEN

WAS EIN FUND HEISST

Ein Fund ist eine Frage, kein Urteil.

  * "einsprachig": beide Sprachen liefern byteweise dasselbe. Bei einem
    Plugin, das ueberhaupt keine Sprachdateien hat, ist das kein Mangel -
    dann meldet die Spalte "ohne Sprachdateien".
  * "Logreiter leer": der Reiter enthaelt nichts als seine Ueberschrift,
    sobald LoxBerry kein Protokoll kennt. Wer sein Protokoll ueber
    LoxBerry::Log anmeldet, ist davon zu Recht nicht betroffen - dann steht
    dort auf dem Geraet die Liste. Wessen Dienst die Datei selbst schreibt,
    hat hier einen echten Befund.

Aufruf:  attrappe_streng.py <ordner> [<ordner> ...]
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
LB = HIER / 'lb'
PHP = r'C:\tmp\php-8.4.27-Win32-vs17-x64\php.exe'

# Woran ein Reiter mit Protokollen zu erkennen ist. Gesucht wird die id, mit
# der die Haus-Oberflaechen ihre Flaechen benennen.
LOG_IDS = ('tab-log', 'tab-logs', 'tab-logdateien', 'tab-protokoll')


def oberflaeche(d):
    for f in sorted(d.rglob('index.php')):
        if 'htmlauth' in str(f):
            return f
    return None


def base_lang_setzen(sprache):
    """Base.Lang in der general.json der Attrappe mitfuehren.

    Nicht jedes Plugin fragt lblanguage(). Die Ecowitt-Weiche liest die
    Sprache aus Base.Lang in config/system/general.json - das ist der Weg,
    den LoxBerry selbst benutzt, und er ist kein Mangel. Ein Werkzeug, das
    nur LBLANG umlegt, meldet so ein Plugin faelschlich als einsprachig.
    Genau so ist es beim ersten Durchgang passiert.

    Rueckgabe: der vorherige Inhalt, damit der Aufrufer ihn zuruecklegt.
    """
    p = LB / 'config' / 'system' / 'general.json'
    if not p.is_file():
        return None
    roh = p.read_text(encoding='utf-8', errors='replace')
    try:
        d = json.loads(roh)
    except ValueError:
        return roh
    d.setdefault('Base', {})['Lang'] = sprache
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding='utf-8')
    return roh


def lauf(datei, plugin, sprache, loglist):
    umg = dict(os.environ)
    umg['LBHOMEDIR'] = str(LB)
    umg['LBLANG'] = sprache
    umg['LB_ATTRAPPE_LOGLIST'] = loglist
    umg['LBPPLUGINDIR'] = plugin.lower()
    umg['LBPCONFIGDIR'] = str(LB / 'config/plugins' / plugin.lower())
    umg['LBPLOGDIR'] = str(LB / 'log/plugins' / plugin.lower())
    umg['LBPDATADIR'] = str(LB / 'data/plugins' / plugin.lower())
    umg['LBPHTMLAUTHDIR'] = str(datei.parent.resolve())
    umg['LBPHTMLDIR'] = str((datei.parent.parent / 'html').resolve())
    umg['LBPTEMPLATEDIR'] = str((datei.parent.parent.parent / 'templates').resolve())
    umg['LBPBINDIR'] = str((datei.parent.parent.parent / 'bin').resolve())
    for k in ('LBPCONFIGDIR', 'LBPLOGDIR', 'LBPDATADIR'):
        Path(umg[k]).mkdir(parents=True, exist_ok=True)
    vorher = base_lang_setzen(sprache)
    try:
        r = subprocess.run(
            [PHP, '-n', '-d', 'include_path=.;' + str(LB / 'libs' / 'phplib'),
             '-d', 'display_errors=0', '-d', 'error_reporting=32767',
             '-d', 'date.timezone=Europe/Berlin',
             '-d', 'extension_dir=' + str(Path(PHP).parent / 'ext'),
             '-d', 'extension=curl', '-d', 'extension=openssl',
             '-d', 'extension=mbstring', '-d', 'extension=sockets',
             '-d', 'extension=fileinfo',
             str(datei.resolve())],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            cwd=str(datei.parent.resolve()), env=umg, timeout=90)
    except subprocess.TimeoutExpired:
        return None, 'Zeitueberschreitung'
    finally:
        # Die gemeinsame Attrappe bleibt, wie sie war.
        if vorher is not None:
            (LB / 'config' / 'system' / 'general.json').write_text(
                vorher, encoding='utf-8')
    # Den RUECKGABEWERT auswerten, nicht nur die Ausgabe: PHP endet bei einem
    # fatalen Fehler mit 255, und eine leere Ausgabe ist dann kein Ergebnis.
    if r.returncode != 0:
        return None, 'Rueckgabewert %d' % r.returncode
    if len(r.stdout) < 500:
        return None, 'Ausgabe nur %d Byte' % len(r.stdout)
    return r.stdout, ''


def logreiter(html):
    """Der Inhalt des Protokoll-Reiters - oder None, wenn es keinen gibt."""
    for kennung in LOG_IDS:
        m = re.search(r'id="%s"' % re.escape(kennung), html)
        if not m:
            continue
        # HINTER das oeffnende Tag springen, nicht hinter die id.
        #
        # Beim ersten Anlauf begann der Ausschnitt unmittelbar hinter
        # id="tab-log" - also mitten im <div>-Tag. Die uebrig gebliebenen
        # zwei Zeichen ">  zaehlten als Inhalt, weil kein < davorsteht und
        # die Tag-Entfernung sie nicht trifft. Ein leerer Reiter sah damit
        # gefuellt aus, und die Eichung am bekannten kaputten Stand blieb
        # gruen. Aufgefallen genau daran.
        schluss = html.find('>', m.end())
        rest = html[(schluss + 1) if schluss != -1 else m.end():]
        tiefe = 1
        for tok in re.finditer(r'</?div\b', rest):
            tiefe += 1 if tok.group(0) == '<div' else -1
            if tiefe == 0:
                return rest[:tok.start()]
        return rest
    return None


def leer(teil):
    """Steht in dem Abschnitt ausser Ueberschriften noch etwas?"""
    ohne = re.sub(r'<h[1-6][^>]*>.*?</h[1-6]>', ' ', teil, flags=re.S)
    ohne = re.sub(r'<[^>]+>', ' ', ohne)
    return re.sub(r'[\s\u00a0]+', '', ohne) == ''


def pruefe(d):
    plugin = d.name
    datei = oberflaeche(d)
    if datei is None:
        return ('-', '-', 'ohne Oberflaeche')
    hat_lang = ((d / 'templates/lang/language_de.ini').is_file()
                and (d / 'templates/lang/language_en.ini').is_file())

    de, f1 = lauf(datei, plugin, 'de', 'voll')
    if de is None:
        return ('?', '?', 'nicht gerendert: ' + f1)
    en, f2 = lauf(datei, plugin, 'en', 'voll')
    if en is None:
        return ('?', '?', 'nicht gerendert (en): ' + f2)

    if not hat_lang:
        sprache = 'ohne Sprachdateien'
    elif de == en:
        sprache = 'EINSPRACHIG'
    else:
        # Wie viel aendert sich? Eine Oberflaeche, die nur die Reiterleiste
        # uebersetzt, ist nicht zweisprachig - die Zahl macht das sichtbar.
        anteil = 100.0 * abs(len(de) - len(en)) / max(len(de), 1)
        sprache = 'zweisprachig (%.1f%% Laengenunterschied)' % anteil

    leerlauf, f3 = lauf(datei, plugin, 'de', 'leer')
    if leerlauf is None:
        return (sprache, '?', 'Leerlauf: ' + f3)
    teil = logreiter(leerlauf)
    if teil is None:
        log = 'kein Protokoll-Reiter'
    elif leer(teil):
        log = 'LEER'
    else:
        log = 'traegt eigenen Inhalt'
    return (sprache, log, '')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    print('%-48s %-34s %s' % ('Plugin', 'Sprache', 'Protokoll-Reiter ohne LoxBerry-Liste'))
    print('-' * 118)
    befunde = 0
    gemessen = 0
    for arg in sys.argv[1:]:
        d = Path(arg)
        if not d.is_dir():
            continue
        sprache, log, hinweis = pruefe(d)
        # NICHT kuerzen. Beim ersten Durchgang stand d.name[:42] hier -
        # und aus 'Beschattungswaechter-0.9.10' und '-0.9.12' wurde beide
        # Male '-0.9.1'. Ein Ordner, den es gar nicht gibt, und zwei
        # Faelle, die nicht mehr auseinanderzuhalten sind. Ein falsches
        # Etikett ist eine falsche Messung.
        print('%-48s %-34s %s%s' % (d.name, sprache, log,
                                    ('   ' + hinweis) if hinweis else ''))
        if sprache in ('EINSPRACHIG',) or log == 'LEER':
            befunde += 1
        if sprache not in ('?', '-'):
            gemessen += 1
    print('-' * 118)
    print('%d Linie(n) gerendert, %d mit Befund.' % (gemessen, befunde))
    print('Ein Fund ist eine Frage, kein Urteil - siehe Kopf dieser Datei.')
    sys.exit(1 if befunde else 0)
