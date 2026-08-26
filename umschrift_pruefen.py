#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Findet ASCII-Umschrift (ue/ae/oe/ss) in sichtbarem deutschem Text.

Aufruf:
    python umschrift_pruefen.py                 alle Plugins im Arbeitsordner
    python umschrift_pruefen.py <Plugin>        eines
    python umschrift_pruefen.py <Plugin> --alle jede Fundstelle einzeln

Warum es das gibt: der Hausstandard verlangt direkte UTF-8-Umlaute. Die Regel
war bisher nur Prosa, und `umlaute_umstellen.py` fasst nur ENTITAETEN an
(&auml; -> ä). Die dritte Form - "pruefen" statt "prüfen" - blieb dadurch
unbemerkt. Am 16.08.2026 gemessen: 34 von 47 Plugins tragen sie, im Dashboard
allein 72 Fundstellen, und dieselbe Datei enthielt beide Schreibweisen
("Schlüssel" und "Schluessel").

Das Werkzeug SCHREIBT NICHT. Es liefert eine Liste zum Entscheiden, denn nicht
jedes ue/ae/oe ist ein Umlaut: "Steuerung", "Quelle", "neue", "virtueller",
"dauerhaft", "zuerst", "graue" sind richtig. Solche Woerter stehen unten in
ECHT; wer eines vermisst, traegt es dort nach - mit demselben Blick, mit dem
man es sonst von Hand uebersehen haette.

Angesehen wird nur der WERT von language_de.ini und help_de.ini. Der
Schluesselname bleibt aussen vor: er ist ein Bezeichner, kein Text.
"""

import io
import os
import re
import sys

# Stämme, in denen die Buchstabenpaare echt sind. Absichtlich als Teilwort
# geprueft - "Steuer" faengt auch "Lichtsteuerung" und "Tafelsteuerung".
ECHT_TEIL = (
    'steuer', 'quell', 'quere', 'quem', 'neu', 'virtuell', 'dauer', 'aktuell',
    'manuell', 'individuell', 'eventuell', 'punktuell', 'zuerst', 'teuer',
    'treu', 'feuer', 'abenteuer', 'bau', 'grau',
    'blau', 'genau', 'lau', 'schau', 'sequen', 'frequen', 'konsequen',
    # ERGAENZT 26.08.2026, Anlass Ultraschall 1.1.12.
    # 'zueinander' ist keine Umschrift, sondern 'zu' + 'einander' - dieselbe
    # Bauart wie 'zuerst' eine Zeile hoeher, das aus demselben Grund schon
    # hier steht. Die Regel ECHT_UE greift nicht, weil davor ein Mitlaut
    # steht; genau dafuer gibt es diese Liste.
    'zueinander',
)
# Ganze Woerter, die nicht deutsch sind oder als Eigenname stehen.
ECHT_WORT = {
    'bluetooth', 'requests', 'request', 'true', 'false', 'value', 'values',
    'continue', 'unique', 'queue', 'sudoers', 'segoe', 'appdaemon', 'jquery',
    'overdue', 'assistant', 'class', 'boe', 'noe',
    # Eigennamen - hier waere jede Regel falsch, nur die Liste hilft.
    'michael', 'rafael', 'raphael', 'israel', 'daenemark', 'aegypten',
    'aeneas', 'gabriel', 'samuel', 'manuel', 'emanuel',
    # Software- und Projektnamen aus den Hilfetexten
    'bluez', 'pybluez', 'issue', 'issues',
    # 'daemon' ist keine Umschrift von "Daemon": es ist das englische Wort und
    # zugleich Teil des Dateinamens /etc/docker/daemon.json, den ein Anwender
    # abtippen muss. 'appdaemon' stand aus demselben Grund schon oben in dieser
    # Liste. Ergaenzt am 22.08.2026 beim Bau von Docker NG 1.3.0.
    'daemon',
}
# Stämme, in denen ss fuer ein ß steht. Absichtlich eine ABSCHLIESSENDE Liste
# statt einer Regel: nach kurzem Vokal ist ss richtig (muss, Fluss, Schluss,
# Wasser, lassen), nach langem Vokal und nach Doppellaut steht ß. Diesen
# Unterschied hoert man, aber man rechnet ihn nicht aus. Was hier fehlt, findet
# das Werkzeug nicht - das ist der Preis dafuer, dass es nichts Falsches meldet.
SZ_STAMM = (
    'gross', 'groess', 'heiss', 'weiss', 'schliess', 'liess', 'fliess', 'giess',
    'geniess', 'stoss', 'gruess', 'suess', 'massnahme', 'strass', 'fuss',
    'aussen', 'draussen', 'gemaess', 'spass', 'reiss', 'beiss', 'schweiss',
    'einfluss', 'blooss', 'schoss',
)

# Bezeichner und Eigennamen, die genau so geschrieben bleiben MUESSEN: Namen
# virtueller Ein-/Ausgaenge, Loxone-Textzeilen, MQTT-Themen, Dateinamen,
# Projekt- und Personennamen. Ein Umlaut darin ist keine Verbesserung, sondern
# ein Bruch der Anlage. Am 16.08.2026 aus 45 Plugins zusammengetragen.
BEZEICHNER = {
    'boerse', 'bruecke', 'mbruecke', 'ibruecke', 'imbruecke', 'durchlaeufe',
    'idurchlaeufe', 'flaeche', 'iflaeche', 'iflaecheg', 'giessen', 'igiessen',
    'geraet', 'geraetn', 'geraete', 'iaussen', 'ilaedt', 'laedt', 'imaeht',
    'maeht', 'laeuft', 'kueche', 'muell', 'stromzaehler', 'tuer', 'tueren',
    'zoephp', 'zoe', 'raes', 'woerstenfeld', 'volkszaehler', 'weissware',
    # Ergaenzt 20.08.2026 aus Audi Connect 0.9.8. Beide Faelle sind keine
    # Umschrift, sondern muessen genau so stehen:
    #   adblue    Markenname der BASF - so steht er auch im Fahrzeugschein.
    #   itueren   kein Wort, sondern ein Loxone-Suchmuster: \iTUEREN=\i\t.
    #             Das i davor ist Loxone-Syntax, das ue gehoert zum Feldnamen
    #             TUEREN, der ohnehin schon in dieser Liste steht.
    'adblue', 'ituer', 'itueren',
}

PAAR = re.compile(r'(?:ue|ae|oe)', re.I)
# Vor einem echten ue steht ein Vokal (Mauer, neue, Steuer, teuer) oder ein q
# (Quelle, bequem, Sequenz). Ein umgeschriebenes ü hat dort einen Mitlaut:
# pruefen, genuegt, fuer. Die Ausnahmen dazu stehen in ECHT_TEIL.
ECHT_UE = re.compile(r'[aeiouäöüq]ue', re.I)
WORT = re.compile(r'[A-Za-zÄÖÜäöüß]{3,}')
WERT = re.compile(r'^\s*[A-Za-z0-9_.]+\s*=\s*"(.*)"\s*$')
MARKE = re.compile(r'<[^>]+>')

# ERGAENZT 26.08.2026, Anlass Smartmeter classic 2.3.14.
#
# Der Hausstandard hat eine eigene Auszeichnung fuer "das hier ist woertlich
# so gemeint und kein deutsches Wort": class='sm-mono'. Darin stehen
# MQTT-Themen, Dateinamen und Befehle. Smartmeter veroeffentlicht ein Thema,
# das tatsaechlich ZAEHLER heisst. Ein Umlaut darin waere kein besserer
# Text, sondern ein falscher Themenname.
#
# Der bequeme Weg waere gewesen, 'zaehler' in BEZEICHNER aufzunehmen. Das
# haette das Wort in ALLEN Plugins stumm gestellt, auch dort, wo es wirklich
# eine Umschrift von "Zaehler" ist. Diese Zeile schweigt nur da, wo der Text
# selbst sagt, dass er woertlich gemeint ist.
#
# <code> und <pre> zaehlen mit - dieselbe Aussage, andere Auszeichnung.
MONO = re.compile(
    r"<span[^>]*class=['\"][^'\"]*sm-mono[^'\"]*['\"][^>]*>.*?</span>"
    r"|<code\b[^>]*>.*?</code>"
    r"|<pre\b[^>]*>.*?</pre>",
    re.I | re.S)


def verdaechtig(w):
    """True, wenn das Wort nach ASCII-Umschrift aussieht."""
    klein = w.lower()
    if klein in ECHT_WORT or klein in BEZEICHNER:
        return False
    if any(t in klein for t in ECHT_TEIL):
        return False
    treffer = PAAR.search(klein)
    if not treffer:
        return False
    # Ein Wort, das schon einen Umlaut traegt, hat jemand mit den richtigen
    # Zeichen geschrieben. Das uebrige ue/ae/oe darin ist dann echt.
    if re.search(r'[äöüß]', w):
        return False
    if treffer.group(0) == 'ue' and ECHT_UE.search(klein):
        return False
    return True


def verdaechtig_ss(w):
    klein = w.lower()
    if klein in BEZEICHNER or klein in ECHT_WORT:
        return False
    # Preis+satz, Preis+schwelle: das erste s gehoert zum Fugen-s, nicht zum ss.
    if 'preiss' in klein or 'einfluss' in klein:
        return False
    return 'ss' in klein and any(t in klein for t in SZ_STAMM)


def pruefen(plugin):
    """Liefert {wort: [fundstelle, ...]} fuer ein Plugin."""
    treffer = {}
    for name in ('language_de.ini', 'help_de.ini'):
        pfad = os.path.join(plugin, 'templates', 'lang', name)
        if not os.path.isfile(pfad):
            continue
        text = io.open(pfad, encoding='utf-8', errors='replace').read()
        for nr, zeile in enumerate(text.split('\n'), 1):
            treff = WERT.match(zeile)
            if not treff:
                continue
            # Erst den woertlich gemeinten Inhalt heraus, dann die Marken.
            # Die Reihenfolge ist entscheidend: nach MARKE.sub waeren die
            # span-Grenzen fort und der Themenname stuende blank im Text.
            wert = MARKE.sub(' ', MONO.sub(' ', treff.group(1)))
            for m in re.finditer(r'[A-Za-zÄÖÜäöüß]{3,}', wert):
                w = m.group(0)
                vor = wert[m.start() - 1:m.start()]
                nach = wert[m.end():m.end() + 1]
                if vor == '_' or nach == '_':
                    continue        # Teil von NAME_NAME
                if verdaechtig(w) or verdaechtig_ss(w):
                    treffer.setdefault(w, []).append('%s:%d' % (name, nr))
    return treffer


def main(argv):
    ziele = [a for a in argv[1:] if not a.startswith('--')]
    alle = '--alle' in argv[1:]
    if not ziele:
        ziele = sorted(d for d in os.listdir('.')
                       if os.path.isdir(os.path.join(d, 'templates', 'lang')))
    if not ziele:
        print('[FEHL] kein Plugin mit templates/lang gefunden')
        return 1

    gesamt = 0
    for plugin in ziele:
        treffer = pruefen(plugin.rstrip('/\\'))
        anzahl = sum(len(v) for v in treffer.values())
        gesamt += anzahl
        marke = '[OK]  ' if not treffer else '[FEHL]'
        print('%s %-46s %3d Fundstellen, %2d Woerter' %
              (marke, plugin[:46], anzahl, len(treffer)))
        if treffer:
            for w in sorted(treffer, key=str.lower):
                stellen = treffer[w]
                if alle:
                    print('         %-24s %s' % (w, ', '.join(stellen)))
                else:
                    print('         %-24s %dx  %s' % (w, len(stellen), stellen[0]))
    print('')
    print('%d Plugin(s) geprueft, %d Fundstellen insgesamt.' % (len(ziele), gesamt))
    print('Kein Fund heisst nicht "richtig geschrieben" - nur "keine Umschrift".')
    return 1 if gesamt else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
