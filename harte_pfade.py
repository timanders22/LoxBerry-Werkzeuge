#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fest verdrahtete LoxBerry-Pfade finden - in Code UND in Kommentaren.

ANLASS (27.08.2026, Kodi NG 1.2.0)
Der Pluginpruefer meldete beim Einspielen:

    WARNING Kodi NG: HARDCODED PATH'S: Das Plugin nutzt einen hardkodierten
    Pfad zu <Wurzel> ... /uploads/<zufall>/LoxBerry-Plugin-KODI-NG-1.2.0/
    uninstall/uninstall

Die Regel dagegen steht seit dem 22.08.2026 in REGELN_2 ("Ein fest
verdrahteter Systempfad"), samt Vorlage. Sie wurde trotzdem gebrochen - und
zwar in derselben Fassung, die an anderer Stelle genau so einen Pfad ENTFERNT
hat. Die ganze Pruefkette war dabei gruen: zehn Pruefungen, null
Beanstandungen. Es gab schlicht kein Werkzeug, das danach sucht.

    Eine Regel, die ein Werkzeug prueft, ist hinterlegt -
    eine Regel in Prosa ist eine Hoffnung.

Das ist dieses Werkzeug.

WAS ES SUCHT
Die bekannten Installationswurzeln von LoxBerry als Zeichenkette, in jeder
Textdatei eines Plugin-Ordners. AUCH IN KOMMENTAREN: der Pruefer von LoxBerry
liest die Datei und sucht die Zeichenkette, ohne den Zusammenhang zu lesen.
Ein Kommentar, der erklaert, warum der Pfad falsch waere, wird deshalb selbst
beanstandet. In Erlaeuterungen gehoert <LoxBerry-Wurzel> statt des Pfades.

WAS DER PRUEFER VON LOXBERRY DAVON SIEHT
Nicht alles. plugininstall.pl:778 lautet

    next if ( !$ext or grep { "/$ext/" } @extensionExcludeList );

Der grep-Block liefert immer eine nichtleere Zeichenkette und ist damit stets
wahr - JEDE Datei mit einer Endung wird uebersprungen. Uebrig bleiben
endungslose Dateien wie uninstall/uninstall oder daemon/daemon. Die Spalte
"Pruefer" unten sagt deshalb, ob die Fundstelle beim Einspielen auch wirklich
gemeldet wird. Die uebrigen sind trotzdem Befunde: die Regel ist aelter und
weiter als das, was der Pruefer davon erwischt.

AUFRUF
    python3 harte_pfade.py                  alle LoxBerry-Plugin-* daneben
    python3 harte_pfade.py <ordner> [...]   nur diese
    python3 harte_pfade.py --alle           auch Fundstellen ohne Befund zeigen

Rueckgabewert 1, sobald eine Fundstelle da ist; 2, wenn keine einzige Datei
angesehen wurde (dann hat die Pruefung nichts gemessen).
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HIER = os.path.dirname(os.path.abspath(__file__))
ARBEIT = os.path.dirname(HIER)

# Die bekannten Wurzeln. Ausgeschrieben, damit man sieht, wonach gesucht wird -
# diese Datei ist ein Werkzeug und wird nicht mit ausgeliefert.
WURZELN = (
    '/opt/loxberry',
    '/usr/local/loxberry',
)
MUSTER = re.compile('|'.join(re.escape(w) for w in WURZELN))

# Was nie mitgelesen wird.
AUS_ORDNER = ('.git', '__pycache__', 'node_modules', '.idea', '.vscode')
BINAER = ('.png', '.jpg', '.jpeg', '.gif', '.ico', '.zip', '.gz', '.bz2',
          '.xz', '.pdf', '.woff', '.woff2', '.ttf', '.eot', '.mo', '.pyc')


def textdateien(wurzel):
    """Alle Textdateien eines Plugin-Ordners, relativ benannt."""
    for verz, unter, dateien in os.walk(wurzel):
        unter[:] = [u for u in unter if u not in AUS_ORDNER]
        for d in sorted(dateien):
            if d.lower().endswith(BINAER):
                continue
            voll = os.path.join(verz, d)
            try:
                if os.path.getsize(voll) > 4 * 1024 * 1024:
                    continue
                roh = io.open(voll, 'rb').read()
            except OSError:
                continue
            if b'\x00' in roh:          # doch binaer
                continue
            rel = os.path.relpath(voll, wurzel).replace(os.sep, '/')
            yield rel, roh.decode('utf-8', 'replace')


def sieht_der_pruefer(rel):
    """Erwischt plugininstall.pl diese Datei ueberhaupt?

    Nur endungslose Dateien - siehe der Kopf dieser Datei. Das ist KEINE
    Entwarnung fuer die uebrigen, sondern eine Auskunft darueber, welche
    Fundstelle beim naechsten Einspielen als WARNING erscheint.
    """
    return '.' not in os.path.basename(rel)


def pruefe(ordner, alle=False):
    name = os.path.basename(os.path.normpath(ordner))
    angesehen = 0
    funde = []
    for rel, text in textdateien(ordner):
        angesehen += 1
        for nr, zeile in enumerate(text.split('\n'), 1):
            if MUSTER.search(zeile):
                funde.append((rel, nr, zeile.strip()[:96], sieht_der_pruefer(rel)))
    return name, angesehen, funde


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith('--')]
    alle = '--alle' in sys.argv[1:]

    if argv:
        ordner = []
        for a in argv:
            p = a if os.path.isdir(a) else os.path.join(ARBEIT, a)
            if not os.path.isdir(p):
                print('Kein Ordner: %s' % a)
                return 2
            ordner.append(p)
    else:
        ordner = [os.path.join(ARBEIT, e) for e in sorted(os.listdir(ARBEIT))
                  if e.startswith('LoxBerry-Plugin-')
                  and os.path.isdir(os.path.join(ARBEIT, e))]

    if not ordner:
        print('Es wurde kein einziger Plugin-Ordner gefunden - nichts gemessen.')
        return 2

    gesamt_dateien = 0
    gesamt_sichtbar = 0
    mit_befund = []
    print('%-42s %7s  %s' % ('Plugin', 'Dateien', 'Fundstellen'))
    print('-' * 96)
    for o in ordner:
        name, angesehen, funde = pruefe(o, alle)
        gesamt_dateien += angesehen
        if funde:
            mit_befund.append(name)
        pruefer = sum(1 for f in funde if f[3])
        gesamt_sichtbar += pruefer
        zusatz = ''
        if funde:
            zusatz = '%d, davon %d fuer den Pruefer sichtbar' % (len(funde), pruefer)
        print('%-42s %7d  %s' % (name[:42], angesehen, zusatz or '-'))
        for rel, nr, zeile, sichtbar in funde:
            print('      %s %s:%d' % ('!!' if sichtbar else '  ', rel, nr))
            print('         %s' % zeile)
    print('-' * 96)
    print('%d Ordner, %d Dateien angesehen, %d mit Fundstelle'
          % (len(ordner), gesamt_dateien, len(mit_befund)))
    # Die Zahl wird HIER genannt, statt sie den Leser aus der Ausgabe
    # zaehlen zu lassen. Beim ersten Lauf hat ein grep -c auf die Marke die
    # LEGENDE mitgezaehlt und eine 1 gemeldet, wo null Fundstellen waren -
    # dieselbe Klasse wie jede andere Zahl aus einer Mustersuche.
    print('davon fuer den Pluginpruefer sichtbar: %d Fundstelle(n)' % gesamt_sichtbar)
    if gesamt_dateien == 0:
        print('KEINE Datei angesehen - diese Pruefung hat nichts gemessen.')
        return 2
    if mit_befund:
        print('\nDie mit !! bezeichneten Zeilen meldet der Pluginpruefer beim')
        print('Einspielen als HARDCODED PATH. Die uebrigen sieht er nicht -')
        print('Befunde sind sie trotzdem (siehe den Kopf dieser Datei).')
        print('Zu erledigen: %s' % ', '.join(mit_befund))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
