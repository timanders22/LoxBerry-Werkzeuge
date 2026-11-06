#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Steht jeder Plugin-Ordner noch byteweise gleich mit seinem Archiv?

Aufruf:
    python archivlage.py                  alle Linien, je hoechste Fassung
    python archivlage.py <Ordner> [...]   nur diese
        --alle    jede abweichende Datei nennen statt der ersten sechs

Rueckgabewert 0, wenn jeder Ordner zu seinem Archiv passt; 1 bei Abweichung;
2, wenn nichts gemessen werden konnte.

WARUM ES DAS GIBT
-----------------
Das Archiv neben dem Ordner ist der BELEGTE Stand einer Linie - die
Plugin-Ordner liegen nicht im Git. `packen.py` sichert das im Augenblick des
Packens byteweise zu. Danach sichert es niemand mehr.

Am 07.09.2026 gemessen, nachdem zwei Durchgaenge (Sektionsberichtigung an
`SICH_FEHLEND`, Entitaeten-Umstellung) ueber den Bestand gelaufen waren:
von 49 Linien passten **10**, 18 hatten gar kein Archiv daneben (der
Normalfall direkt nach einer Veroeffentlichung), und **21 Ordner wichen von
ihrem Archiv ab** - fast durchweg `templates/lang/*.ini`.

Das ist fuer sich noch kein Fehler. Es wird einer, sobald der Ordner die
BEREITS VEROEFFENTLICHTE Nummer traegt: dann laesst sich der Unterschied
nicht mehr unter derselben Nummer packen, ohne dass das Archiv dem Tag auf
GitHub widerspricht. Deshalb nennt dieses Werkzeug zu jeder Abweichung, ob
`plugin.cfg` und `release.cfg` dieselbe Nummer tragen. Am 07.09.2026 traf
das auf 7 der 21 zu.

ABGRENZUNG
----------
* `packen.py` prueft dasselbe - aber nur, waehrend es packt.
* `fassungslage.py` prueft gegen das Archiv auf GITHUB. Das braucht Netz und
  faellt unter die Abrufgrenze von 60 Aufrufen je Stunde; nach 23 Linien
  misst ein Durchgang still nichts mehr. Dieses Werkzeug braucht kein Netz.
* Es urteilt NICHT darueber, welche Fassung die richtige ist. Es sagt nur,
  dass Ordner und Archiv auseinanderstehen, und wer das entscheiden muss.

MESSFALLE, die es selbst vermeidet
----------------------------------
Die Liste der zu pruefenden Ordner wird HIER gebaut, nicht uebergeben. Eine
uebergebene Liste veraltet, sobald eine Linie ihre Nummer wechselt; das
Werkzeug findet dann den Ordner nicht mehr und meldet "alle Dateien fehlen" -
eine Abweichung, die es gar nicht gibt. Genau das ist am 07.09.2026 bei einer
ersten Messung passiert.
"""
import os
import re
import sys
import zipfile

BS = chr(92)


def hoechste_fassungen(wurzel='.'):
    """Je Linie den Ordner mit der hoechsten Nummer."""
    aus = {}
    for e in sorted(os.listdir(wurzel)):
        if not os.path.isdir(os.path.join(wurzel, e)) or not e.startswith('LoxBerry-Plugin-'):
            continue
        m = re.match(r'(LoxBerry-Plugin-.+?)-(\d+(?:\.\d+)*)$', e)
        if not m:
            continue
        v = tuple(int(x) for x in m.group(2).split('.'))
        if m.group(1) not in aus or v > aus[m.group(1)][0]:
            aus[m.group(1)] = (v, e)
    return [d for _, d in sorted(aus.values())]


def nummer(ordner, datei):
    p = os.path.join(ordner, datei)
    if not os.path.isfile(p):
        return ''
    for z in open(p, encoding='utf-8', errors='replace'):
        if z.startswith('VERSION'):
            return z.split('=', 1)[1].strip()
    return ''


def vergleichen(d):
    """(geaendert, fehlt_im_ordner, nur_im_ordner) oder None ohne Archiv."""
    z = d + '.zip'
    if not os.path.isfile(z):
        return None
    zf = zipfile.ZipFile(z)
    anders, fehlt = [], []
    for i in zf.infolist():
        if i.filename.endswith('/'):
            continue
        p = os.path.join(d, i.filename)
        if not os.path.isfile(p):
            fehlt.append(i.filename)
        elif zf.read(i) != open(p, 'rb').read():
            anders.append(i.filename)
    imzip = set(i.filename for i in zf.infolist() if not i.filename.endswith('/'))
    ueber = []
    for root, _, files in os.walk(d):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), d).replace(BS, '/')
            if rel not in imzip:
                ueber.append(rel)
    return (anders, fehlt, ueber)


def main():
    argv = [a for a in sys.argv[1:] if a != '--alle']
    alle = '--alle' in sys.argv[1:]
    ordner = argv if argv else hoechste_fassungen()
    if not ordner:
        print('ACHTUNG: kein Plugin-Ordner gefunden - nichts gemessen.')
        return 2

    print('%d Ordner angesehen%s.' % (len(ordner), '' if argv else ', je hoechste Fassung je Linie'))
    print('')
    gleich, ohne, abw = 0, [], []
    for d in ordner:
        if not os.path.isdir(d):
            print('ACHTUNG: %s gibt es nicht - uebersprungen.' % d)
            continue
        e = vergleichen(d)
        if e is None:
            ohne.append(d)
        elif any(e):
            abw.append((d, e))
        else:
            gleich += 1

    print('%d Ordner byteweise gleich mit ihrem Archiv.' % gleich)
    print('%d Ordner ohne Archiv daneben (nach einer Veroeffentlichung normal):' % len(ohne))
    for d in ohne:
        print('    %s' % d)
    print('')
    print('%d Ordner weichen von ihrem Archiv ab:' % len(abw))
    veroeffentlicht = []
    for d, (anders, fehlt, ueber) in abw:
        p, r = nummer(d, 'plugin.cfg'), nummer(d, 'release.cfg')
        lage = 'NUMMER IST DRAUSSEN' if (p and p == r) else 'Nummer noch offen (release %s)' % (r or '?')
        if p and p == r:
            veroeffentlicht.append(d)
        teile = []
        if anders:
            teile.append('%d geaendert' % len(anders))
        if fehlt:
            teile.append('%d fehlen im Ordner' % len(fehlt))
        if ueber:
            teile.append('%d nur im Ordner' % len(ueber))
        print('    %-46s %-28s %s' % (d, ', '.join(teile), lage))
        namen = anders + ['(fehlt) ' + x for x in fehlt] + ['(neu) ' + x for x in ueber]
        for n in (namen if alle else namen[:6]):
            print('        %s' % n)
        if not alle and len(namen) > 6:
            print('        … %d weitere (--alle)' % (len(namen) - 6))

    if veroeffentlicht:
        print('')
        print('%d davon tragen eine BEREITS VEROEFFENTLICHTE Nummer:' % len(veroeffentlicht))
        for d in veroeffentlicht:
            print('    %s' % d)
        print('    Dort ist ein Neupacken unter derselben Nummer kein Ausweg - das')
        print('    Archiv widerspraeche dann dem Tag. Diese Aenderungen gehoeren in')
        print('    die naechste Nummer.')
    return 1 if (abw or ohne) else 0


if __name__ == '__main__':
    sys.exit(main())
