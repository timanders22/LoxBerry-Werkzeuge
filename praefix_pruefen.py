# -*- coding: utf-8 -*-
"""Praefix-1 (08.10.2026): Plugin-Namen, die Anfang eines anderen sind.

LoxBerry ruft beim Deinstallieren jedes data/system/uninstall/<NAME>* auf
(plugininstall.pl, glob "$pname*") und loescht danach uninstall/<NAME>* und
system/daemons/plugins/<NAME>*. Ist NAME A der Anfang von NAME B, laeuft beim
Deinstallieren von A auch das Uninstall-Skript von B - mit NAME und Ordner
von A. Am 08.10.2026 entfernte so die Deinstallation von zigbee2mqtt den
Dienst von zigbee2mqttng.

Aufruf (im Arbeitsordner): python praefix_pruefen.py [fremdnamen.txt] [--linie ORDNER]
  Liest [PLUGIN] NAME aus der neuesten Fassung jeder Linie
  (LoxBerry-Plugin-<Linie>-<x.y.z>/plugin.cfg). fremdnamen.txt: weitere
  Namen (Originale, Fremd-Plugins am Geraet), durch Leerraum getrennt
  (im Werkzeugordner: Werkzeuge/praefix_fremdnamen.txt).
  --linie ORDNER (seit 09.10.2026, fuer linie_abschluss.sh): ORDNER steht fuer
  seine Linie statt deren neuester Fassung (die zu veroeffentlichende Fassung
  ist nicht immer die neueste). Die Rueckgabe betrifft dann NUR diese Linie.
Meldet:
  PAAR   A -> B          B wird beim Deinstallieren von A mitgerufen
  OHNE SPERRE  B         eigenes Plugin B ist gefaehrdet und prueft $2/$3 nicht
Rueckgabe 1, wenn ein eigenes gefaehrdetes Plugin ohne Sperre ist; mit
--linie nur, wenn ORDNER selbst gefaehrdet ist und keine Sperre traegt.
Rueckgabe 2 bei Aufruffehlern (ORDNER fehlt, kein NAME in seiner plugin.cfg).
"""
import os
import re
import sys


def neueste_ordner(wurzel='.'):
    best = {}
    for d in os.listdir(wurzel):
        m = re.match(r'LoxBerry-Plugin-(.+)-(\d+(?:\.\d+)+)$', d)
        if m and os.path.isfile(os.path.join(wurzel, d, 'plugin.cfg')):
            v = tuple(int(x) for x in m.group(2).split('.'))
            if m.group(1) not in best or v > best[m.group(1)][0]:
                best[m.group(1)] = (v, d)
    return sorted(x[1] for x in best.values())


def plugin_name(ordner):
    t = open(os.path.join(ordner, 'plugin.cfg'), encoding='utf-8', errors='replace').read()
    m = re.search(r'(?ms)^\[PLUGIN\]\s*$(.*?)(?=^\[|\Z)', t)
    if not m:
        return None
    n = re.search(r'(?m)^NAME=(\S+)', m.group(1))
    return n.group(1).strip() if n else None


def hat_sperre(ordner, name):
    """Prueft das Uninstall-Skript auf einen Vergleich von $2/$3 mit dem eigenen Namen."""
    d = os.path.join(ordner, 'uninstall')
    if not os.path.isdir(d):
        return None
    for f in os.listdir(d):
        t = open(os.path.join(d, f), encoding='utf-8', errors='replace').read()
        # "$2" != "name"  oder  "$PSHNAME" != "name" (Variable, die $2 traegt)
        varn = set(re.findall(r'(?m)^\s*([A-Z_][A-Z0-9_]*)=["\']?\$\{?2\b', t)) | {'2'}
        for v in varn:
            if re.search(r'"\$\{?' + re.escape(v) + r'\}?"\s*!=\s*"' + re.escape(name) + '"', t):
                return True
    return False


def main():
    argv = sys.argv[1:]
    linie = None
    if '--linie' in argv:
        i = argv.index('--linie')
        if i + 1 >= len(argv):
            print('ABBRUCH: --linie ohne ORDNER')
            return 2
        linie = argv[i + 1].rstrip('/\\')
        del argv[i:i + 2]
    eigene = {}
    for o in neueste_ordner():
        n = plugin_name(o)
        if n:
            eigene[n] = o
    if linie is not None:
        m = re.match(r'LoxBerry-Plugin-(.+)-(\d+(?:\.\d+)+)$', os.path.basename(linie))
        if not m or not os.path.isfile(os.path.join(linie, 'plugin.cfg')):
            print('ABBRUCH: --linie %s ist kein Linienordner mit plugin.cfg' % linie)
            return 2
        lname = plugin_name(linie)
        if not lname:
            print('ABBRUCH: kein [PLUGIN] NAME in %s/plugin.cfg' % linie)
            return 2
        # andere Fassungen derselben Linie (gleicher Ordnerstamm) ersetzen
        for n, o in list(eigene.items()):
            mo = re.match(r'LoxBerry-Plugin-(.+)-(\d+(?:\.\d+)+)$', o)
            if mo and mo.group(1) == m.group(1):
                del eigene[n]
        eigene[lname] = linie
    fremde = set()
    if argv:
        fremde = set(open(argv[0], encoding='utf-8').read().split()) - set(eigene)
    alle = set(eigene) | fremde
    print('%d eigene Namen, %d weitere Namen' % (len(eigene), len(fremde)))
    offen = 0
    linie_offen = False
    for a in sorted(alle):
        for b in sorted(alle):
            if a != b and b.startswith(a):
                art_a = 'eigen' if a in eigene else 'fremd'
                art_b = 'eigen' if b in eigene else 'fremd'
                zeile = 'PAAR   %s (%s) -> %s (%s)' % (a, art_a, b, art_b)
                if b in eigene:
                    s = hat_sperre(eigene[b], b)
                    zeile += '   Sperre in %s: %s' % (eigene[b], {True: 'ja', False: 'NEIN', None: 'kein uninstall/'}[s])
                    if s is False:
                        offen += 1
                        if linie is not None and b == lname:
                            linie_offen = True
                print(zeile)
    if offen:
        print('OHNE SPERRE: %d gefaehrdete eigene Plugins' % offen)
    else:
        print('keine gefaehrdeten eigenen Plugins ohne Sperre')
    if linie is not None:
        if linie_offen:
            print('LINIE %s (NAME %s): gefaehrdet und OHNE SPERRE' % (linie, lname))
        else:
            print('LINIE %s (NAME %s): nicht gefaehrdet oder mit Sperre' % (linie, lname))
        return 1 if linie_offen else 0
    return 1 if offen else 0


if __name__ == '__main__':
    sys.exit(main())
