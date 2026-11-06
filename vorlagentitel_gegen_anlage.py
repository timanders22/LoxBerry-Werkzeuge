#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Treffen die Titel der Loxone-Vorlagen auf Namen, die in der Anlage schon stehen?

Aufruf:
    python vorlagentitel_gegen_anlage.py <Vorlagenordner> <LoxAPP3.json>
        [--alle]   jede Fundstelle einzeln statt nur der Zahl

Rueckgabe 0, wenn kein BEFUND steht; 1 bei Befund; 2, wenn nichts gemessen
werden konnte.

WARUM ES DAS GIBT
-----------------
`vorlagen_pruefen.py` misst die Titel der Vorlagen GEGENEINANDER (h3 je Datei,
h6 ueber die Linien). Es misst sie nicht gegen die ANLAGE. Genau dort wirkt die
Regel aber:

    Regeln/07: "Der TITEL eines Bausteins wird gelesen ... Ein Praefix
    (`WW 1 …`) bleibt noetig, weil in der Bausteinsuche der Geraeteknoten
    fehlt."
    Regeln/07: "Zweimal eingelesen sind zwei Bausteine - Loxone Config meldet
    nichts, legt neu an und ueberschreibt nichts."

Wer eine Vorlage einliest, deren Titel schon als Anzeigename in der Anlage
steht, bekommt zwei Bausteine mit demselben Namen. Loxone Config sagt nichts;
die Bausteinsuche und die Visualisierung zeigen danach zwei gleich heissende
Eintraege, und welcher gemeint ist, sieht man nicht mehr.

WAS GEMESSEN WIRD
-----------------
Aus der Strukturdatei des laufenden Miniservers (`LoxAPP3.json`) kommen:
  * `controls[*].name`               die Anzeigenamen der Bausteine
  * `controls[*].subControls[*].name`
Aus den Vorlagen:
  * jedes `Title`-Attribut eines Kindelements (`VirtualInHttpCmd`,
    `VirtualInUdpCmd`, `VirtualOutCmd`)

BEFUND, wenn ein Vorlagentitel EXAKT einem Anzeigenamen der Anlage entspricht
und die Vorlage nicht die ist, aus der dieser Name stammt - das laesst sich von
aussen nicht unterscheiden, deshalb ist jeder Treffer eine FRAGE und wird als
Befund gemeldet, mit der Linie daneben. Wer ihn geprueft hat, traegt ihn in die
Ausnahmeliste am Kopf dieser Datei ein, mit Datum und Grund.

WAS ES NICHT MISST
------------------
* Es misst gegen EINE Strukturdatei, also gegen DIESE Anlage. Eine fremde
  Anlage hat andere Namen; ein Titel, der hier frei ist, kann dort belegt sein.
  Deshalb ist ein sprechendes Praefix je Linie die eigentliche Abhilfe, nicht
  das Ausweichen vor einem einzelnen Treffer.
* Es misst nicht, ob ein Baustein aus einer Vorlage stammt. Die Strukturdatei
  sagt das nicht.
* Ohne `isSecured`/Visualisierungshaken taucht ein Eingang in der Strukturdatei
  gar nicht auf (Regeln/07, "Objekte am Miniserver ueber den Anzeigenamen
  suchen"). Was hier nicht steht, ist deshalb nicht "frei", sondern
  "nicht sichtbar" - die Zahl der angesehenen Namen steht im Bericht.
"""
import json
import re
import sys
from pathlib import Path

# Geprueft und bewusst behalten: Titel => (Linie, Datum, Grund)
AUSNAHMEN = {
    'Messerwechsel quittieren': (
        'Robonect', '06.09.2026',
        'An der Projektdatei nachgesehen: der Name steht dort als VirtualOutCmd '
        'UND als PushButton - ein gewolltes Paar, nicht zwei Bausteine aus '
        'zweimaligem Import.'),
}

TITEL = re.compile(r'<(?:VirtualInHttpCmd|VirtualInUdpCmd|VirtualOutCmd)\b[^>]*?\bTitle="([^"]*)"')
# Das WURZELELEMENT traegt den Geraetenamen, nicht einen Bausteinnamen. Es wird
# getrennt gemessen und getrennt gemeldet: ein Geraet und ein Baustein gleichen
# Namens sind nicht dasselbe wie zwei Bausteine gleichen Namens - in der
# Bausteinsuche stehen sie trotzdem nebeneinander.
#
# Aufgefallen bei der Eichung am 06.09.2026: die erste eingeschleuste Marke
# landete im Wurzelelement und wurde NICHT gemeldet. Die Eichung hat damit
# zuerst nur das Schweigen des Werkzeugs gemessen, nicht sein Anschlagen.
WURZEL = re.compile(r'<(?:VirtualInHttp|VirtualInUdp|VirtualOut)\b[^>]*?\bTitle="([^"]*)"')
# Der COMMENT eines EINGANGSbefehls wird in Loxone Config zum Desc und damit
# zum Anzeigenamen - an der Projektdatei belegt (Regeln/07, 05.09.2026: von 18
# gemeinsamen Titeln tragen 14 ein Desc byteweise gleich dem Comment, 0 ein
# abweichendes). Wer nur die Titel misst, misst am Anzeigenamen vorbei.
#
# Ergaenzt am 07.09.2026, nachdem die Blindstelle an der eigenen Arbeit
# aufgefallen war: Saugroboter 1.1.4 gab dem Statusfeld den Kachelnamen
# "Status" - und so heisst in dieser Anlage bereits ein TextState. Die
# Titelmessung war dabei still, weil der Titel ROBO_CODE heisst.
KOMMENTAR = re.compile(r'<(?:VirtualInHttpCmd|VirtualInUdpCmd|VirtualOutCmd)\b[^>]*?\bComment="([^"]*)"')


def namen_der_anlage(pfad):
    d = json.loads(Path(pfad).read_text(encoding='utf-8'))
    namen = {}
    for uuid, c in (d.get('controls') or {}).items():
        if isinstance(c, dict) and c.get('name'):
            namen.setdefault(str(c['name']), []).append(c.get('type', '?'))
            for su in (c.get('subControls') or {}).values():
                if isinstance(su, dict) and su.get('name'):
                    namen.setdefault(str(su['name']), []).append(su.get('type', '?'))
    return namen


def titel_der_vorlagen(ordner):
    """Bausteintitel, Geraetenamen und Anzeigenamen getrennt zurueckgeben."""
    aus, wurzel, komm = {}, {}, {}
    dateien = sorted(Path(ordner).glob('*.xml'))
    for f in dateien:
        text = f.read_text(encoding='utf-8', errors='replace')
        for t in TITEL.findall(text):
            aus.setdefault(t, []).append(f.name)
        for t in WURZEL.findall(text):
            wurzel.setdefault(t, []).append(f.name)
        for t in KOMMENTAR.findall(text):
            if t.strip():
                komm.setdefault(t, []).append(f.name)
    return aus, wurzel, komm, len(dateien)


def main():
    argv = sys.argv[1:]
    alle = '--alle' in argv
    argv = [a for a in argv if a != '--alle']
    if len(argv) != 2:
        print(__doc__.split('WARUM')[0])
        return 2

    namen = namen_der_anlage(argv[1])
    titel, wurzel, komm, anz_dateien = titel_der_vorlagen(argv[0])

    if not namen:
        print('ACHTUNG: 0 Anzeigenamen aus der Strukturdatei gelesen - nichts gemessen.')
        return 2
    if not titel:
        print('ACHTUNG: 0 Titel aus den Vorlagen gelesen - nichts gemessen.')
        return 2

    print('%d Anzeigenamen aus der Anlage, %d Titel aus %d Vorlagen.'
          % (len(namen), len(titel), anz_dateien))

    treffer = sorted(set(titel) & set(namen))
    offen = [t for t in treffer if t not in AUSNAHMEN]
    print('%d Titel treffen einen Anzeigenamen der Anlage, %d davon ohne Ausnahme.'
          % (len(treffer), len(offen)))
    print('')

    for t in (offen if not alle else treffer):
        herkunft = sorted(set(titel[t]))
        linien = sorted({n.split('__')[0] for n in herkunft})
        print('  BEFUND  %-40s Anlage: %s' % (t[:40], ', '.join(sorted(set(namen[t])))))
        print('          aus %s' % ', '.join(linien))
        if alle and t in AUSNAHMEN:
            print('          Ausnahme: %s' % (AUSNAHMEN[t],))
    if not offen:
        print('  Kein Bausteintitel einer Vorlage trifft einen Anzeigenamen dieser Anlage.')
    print('')

    # Die Geraetenamen (Wurzelelement) - getrennt gezaehlt, getrennt gemeldet.
    w_treffer = sorted(set(wurzel) & set(namen))
    print('%d Geraetenamen (Wurzelelement) in den Vorlagen, %d treffen einen '
          'Anzeigenamen der Anlage.' % (len(wurzel), len(w_treffer)))
    for t in w_treffer:
        linien = sorted({n.split('__')[0] for n in wurzel[t]})
        print('  Hinweis %-38s Anlage: %-14s aus %s'
              % (t[:38], ', '.join(sorted(set(namen[t]))), ', '.join(linien)))
    w_dopp = {k: sorted({n.split('__')[0] for n in v}) for k, v in wurzel.items()
              if len({n.split('__')[0] for n in v}) > 1}
    print('%d Geraetenamen kommen in mehr als einer Linie vor.' % len(w_dopp))
    for k, v in sorted(w_dopp.items()):
        print('  Hinweis %-38s %s' % (k[:38], ', '.join(v)))
    # Die ANZEIGENAMEN (Comment der Befehle). Getrennt gemessen, getrennt
    # gemeldet und ausdruecklich als Hinweis: ein Treffer heisst hier meist,
    # dass die EIGENE Vorlage dieser Linie schon einmal eingelesen wurde -
    # von aussen ist das nicht von einer fremden Namensgleichheit zu
    # unterscheiden. Wer die Zahl rot machen wuerde, macht ein Tor rot, das
    # bei jeder eingerichteten Linie anschlaegt.
    k_treffer = sorted(set(komm) & set(namen))
    print('%d Anzeigenamen (Comment der Befehle) in den Vorlagen, %d treffen einen '
          'Anzeigenamen der Anlage.' % (len(komm), len(k_treffer)))
    for t in k_treffer:
        linien = sorted({n.split('__')[0] for n in komm[t]})
        print('  Hinweis %-38s Anlage: %-14s aus %s'
              % (t[:38], ', '.join(sorted(set(namen[t]))), ', '.join(linien)))
    if k_treffer:
        print('          Meist die eigene Vorlage, schon eingelesen. Nachsehen muss man,')
        print('          ob der Name ohne Vorsatz auskommt (Regeln/07, Bausteinsuche).')
    print('')
    print('Gemessen: Titel gegen DIESE Anlage. Eine fremde Anlage hat andere Namen -')
    print('ein sprechendes Praefix je Linie ist die Abhilfe, nicht das Ausweichen.')
    return 1 if offen else 0


if __name__ == '__main__':
    sys.exit(main())
