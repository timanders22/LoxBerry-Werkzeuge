#!/usr/bin/env python3
"""Prueft die AUSGELIEFERTE Seite auf verschachtelte oder offene Formulare.

HTML verbietet <form> in <form>. Der Browser wirft das innere weg - seine
Knoepfe senden dann an das aeussere Formular. Ein Testknopf loest damit ein
Speichern der Einstellungen aus, ein Speichern-Knopf schickt fremde Felder
mit. Das faellt beim Lesen des Quelltextes kaum auf, weil die Formulare oft
hunderte Zeilen auseinander stehen.

Gemessen wird an der gerenderten Seite, nicht am PHP-Quelltext: nur dort
steht, was der Browser wirklich sieht.

Aufruf - alle vier Formen sind zulaessig:

    python3 formularpruefung.py <Plugin-Ordner>       Pfad, unmittelbar
    python3 formularpruefung.py --verz=<pfad> <Name>  Name unter <pfad>
    python3 formularpruefung.py <Name>                Name unter stand/
    python3 formularpruefung.py                       alles unter stand/

Rueckgabewert: 0 in Ordnung, 1 mindestens ein Befund, 2 es wurde NICHTS
angesehen.

WARUM DIE 2 - UND WARUM DIESE DATEI AM 18.08.2026 UMGEBAUT WURDE

Bis dahin nahm dieses Werkzeug als einziges der Hauskette KEINEN Pfad. Es
setzte 'stand' fest und las seine Argumente als Plugin-Namen darunter. Wer
ihm einen Pfad gab - und genau so stand es in der Werkzeugtabelle in
REGELN_2 -, bekam kommentarlos "0 von 1 Linien mit Formularfehler" und
Rueckgabewert 0. Es hatte nichts angesehen und sagte es nicht.

Das war schlechter als die beiden Faelle vom 17.08.2026, um derentwillen die
Tabelle ueberhaupt angelegt wurde: installationslage_pruefen.py nennt
wenigstens die Null ("0 Dateien"), wirkungstest.py bricht seit dem 17.08. mit
Rueckgabewert 2 ab. Hier war die einzige Unterscheidung zwischen "nichts
gefunden" und "nichts angesehen" die Zahl hinter dem *von* - und die liest
man als Zahl der geprueften Linien.

Deshalb jetzt dasselbe Muster wie in wirkungstest.py: ein Argument, das
selbst ein Plugin-Ordner ist, wird unmittelbar genommen; und ist am Ende
nichts angesehen worden, endet der Lauf mit 2 und einer Zeile, die das sagt.

BEIM EICHEN KAM EIN DRITTER MANGEL HERAUS, der vorher niemandem aufgefallen
war: die alte Fassung endete **auch bei einem gefundenen Befund** mit
Rueckgabewert 0. Sie hatte gar kein sys.exit(). Richtig aufgerufen fand sie
die verschachtelten Formulare tadellos und meldete sie auch - nur konnte
eine Kette, die den Rueckgabewert auswertet, das nicht von einem sauberen
Lauf unterscheiden. Gemessen am 18.08.2026 an einer absichtlich zerbrochenen
Kopie: "1 von 1 Linien mit Formularfehler", Rueckgabewert 0.

Die Erkennung selbst ist unveraendert - sie war nie das Problem.

Die alte Aufrufform (Namen unter stand/) bleibt unveraendert gueltig: wer
sie gewohnt ist, merkt von diesem Umbau nichts ausser dem Rueckgabewert.
"""
import re
import sys
from pathlib import Path

import wirkungstest as W

OBERFLAECHE = 'webfrontend/htmlauth/index.php'


def oberflaeche(ziel, verzeichnis='stand'):
    """Den Pfad zur index.php finden - ob Pfad oder Name uebergeben wurde.

    Erst wird geprueft, ob das Argument selbst ein Plugin-Ordner ist, danach
    erst wird es als Name unter dem Grundverzeichnis gesucht. Diese
    Reihenfolge ist Absicht: ein vorhandener Pfad ist eine Tatsache, ein Name
    unter stand/ eine Annahme.
    """
    unmittelbar = Path(ziel) / OBERFLAECHE
    if unmittelbar.is_file():
        return unmittelbar
    unter = Path(verzeichnis) / ziel / OBERFLAECHE
    if unter.is_file():
        return unter
    return None


def pruefe(ziel, verzeichnis='stand'):
    """Rueckgabe: Liste der Befunde, leere Liste = in Ordnung, None = keine
    Oberflaeche gefunden.

    None und die leere Liste sind ausdruecklich NICHT dasselbe. Der Aufrufer
    muss beides unterscheiden, sonst zaehlt er ein Ueberspringen als
    bestanden - das war der Fehler, den dieser Umbau behebt.
    """
    datei = oberflaeche(ziel, verzeichnis)
    if datei is None:
        return None
    html, _ = W.lauf(datei, Path(ziel).name)
    if not html.strip():
        return ['Seite leer - nicht pruefbar']
    tiefe = 0
    verschachtelt = 0
    zuviel = 0
    for m in re.finditer(r'<form\b|</form\s*>', html, re.I):
        if m.group(0).lower().startswith('<form'):
            tiefe += 1
            if tiefe > 1:
                verschachtelt += 1
        else:
            tiefe -= 1
            if tiefe < 0:
                zuviel += 1
                tiefe = 0
    aus = []
    if verschachtelt:
        aus.append('%d verschachtelte <form> - der Browser verwirft sie' % verschachtelt)
    if tiefe:
        aus.append('%d Formular(e) nie geschlossen' % tiefe)
    if zuviel:
        aus.append('%d </form> ohne oeffnendes <form>' % zuviel)
    return aus


def main():
    verz = 'stand'
    namen = []
    for a in sys.argv[1:]:
        if a.startswith('--verz='):
            verz = a.split('=', 1)[1]
        elif not a.startswith('--'):
            namen.append(a)

    if not namen:
        wurzel = Path(verz)
        if not wurzel.is_dir():
            print('Grundverzeichnis %r gibt es nicht. Entweder einen '
                  'Plugin-Ordner unmittelbar uebergeben oder --verz=<pfad> '
                  'angeben.' % verz)
            return 2
        namen = [x.name for x in sorted(wurzel.iterdir()) if x.is_dir()]
        if not namen:
            print('Grundverzeichnis %r ist leer - es wurde nichts geprueft.' % verz)
            return 2

    schlecht = 0
    ohne = 0
    geprueft = 0
    for n in namen:
        b = pruefe(n, verz)
        if b is None:
            ohne += 1
            print('%-40s uebersprungen (keine %s gefunden)'
                  % (Path(n).name, OBERFLAECHE))
            continue
        geprueft += 1
        if b:
            schlecht += 1
            print('%-40s %s' % (Path(n).name, '; '.join(b)))
        else:
            print('%-40s ok' % Path(n).name)

    print('\n%d Linien geprueft, %d mit Formularfehler, %d ohne Oberflaeche '
          'uebersprungen.' % (geprueft, schlecht, ohne))
    if geprueft == 0:
        print('ACHTUNG: es wurde keine einzige Oberflaeche geprueft.')
        return 2
    return 1 if schlecht else 0


if __name__ == '__main__':
    sys.exit(main())
