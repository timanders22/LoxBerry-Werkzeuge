#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vergleicht ein INSTALLIERTES Plugin auf dem LoxBerry mit seinem Tag-Archiv.

Anlass (WOLF-ISM-NG, 07.09.2026): das Geraet meldete Fassung 3.1.1, die
Plugindatenbank meldete 3.1.1, der Installationslog meldete Erfolg - und
trotzdem lag EINE Datei im alten Stand von v3.1.0 dort. Die Installation lief
um 09:29 Uhr, der Tag-Commit entstand um 09:31 Uhr: zwei Minuten Wettlauf,
und niemand haette es gemerkt, weil die Fassungsnummer aus plugin.cfg kommt und
nicht aus dem Inhalt der Dateien. Genau diesen Fall misst dieses Werkzeug.

    python geraetestand_vergleichen.py <lokaler Pluginordner> [Optionen]

    --geraet NAME   SSH-Ziel (Vorgabe: loxberry-claude)
    --tag vX.Y.Z    Anderes Tag vergleichen als das aus release.cfg
                    (dient auch der Eichung: gegen die VORIGE Fassung muss
                    dieses Werkzeug rot werden)
    --ordner NAME   Installationsordner auf dem Geraet, falls er vom
                    FOLDER-Eintrag der plugin.cfg abweicht (LoxBerry haengt
                    01, 02, ... an, wenn der Name schon vergeben ist)

Rueckgabe 0 = das Geraet traegt den veroeffentlichten Stand
         1 = Abweichung
         2 = nichts gemessen (kein SSH, kein Tag, keine Dateien)

DREI ARTEN VON UNTERSCHIED, und nur die dritte ist ein Befund:

1. Zeilenenden. Der Installer wandelt Textdateien nach Unix
   (`plugininstall.pl`, "Converting all plugin files (ASCII) to Unix
   fileformat"). Eine CRLF-Datei im Archiv liegt auf dem Geraet als LF.
2. Platzhalter. Der Installer ersetzt neun Zeichenketten
   (`plugininstall.pl:1834-1842`), von REPLACELBHOMEDIR bis REPLACELBPBINDIR.
   Eine Datei, die einen davon enthaelt, MUSS auf dem Geraet anders aussehen.
3. Alles andere. Das ist der Befund.

WAS DIESES WERKZEUG NICHT VERGLEICHT: `config/plugins/<ordner>/` und
`data/plugins/<ordner>/`. Das sind die Daten des Anwenders; sie sollen
abweichen. Wer sie hier hineinnaehme, bekaeme bei jeder Anlage einen Fehlalarm
- und ein Dauerfehlalarm ist eine abgeschaltete Pruefung.
"""
import argparse
import hashlib
import io
import os
import re
import subprocess
import sys
import urllib.request
import zipfile

# Wo die Teile eines Plugins auf dem Geraet landen. Gemessen an einem
# Installationsprotokoll (LoxBerry 4.0.0.15, plugininstall.pl).
BAEUME = [
    ('bin/',                   '/opt/loxberry/bin/plugins/%s'),
    ('webfrontend/htmlauth/',  '/opt/loxberry/webfrontend/htmlauth/plugins/%s'),
    ('webfrontend/html/',      '/opt/loxberry/webfrontend/html/plugins/%s'),
    ('templates/',             '/opt/loxberry/templates/plugins/%s'),
]

PLATZHALTER = (
    'REPLACELBHOMEDIR', 'REPLACELBPPLUGINDIR', 'REPLACELBPHTMLAUTHDIR',
    'REPLACELBPHTMLDIR', 'REPLACELBPTEMPLATEDIR', 'REPLACELBPDATADIR',
    'REPLACELBPLOGDIR', 'REPLACELBPCONFIGDIR', 'REPLACELBPBINDIR',
)


def cfg_wert(pfad, schluessel):
    if not os.path.isfile(pfad):
        return ''
    with io.open(pfad, encoding='utf-8', errors='replace') as f:
        for z in f:
            z = z.strip()
            if z.startswith(schluessel + '='):
                return z[len(schluessel) + 1:].strip()
    return ''


def laden(url):
    """Ein Archiv holen. Liefert (bytes, HTTP-Code)."""
    try:
        with urllib.request.urlopen(url, timeout=60) as a:
            return a.read(), a.getcode()
    except urllib.error.HTTPError as e:
        return b'', e.code
    except Exception as e:                                  # Netz, DNS, TLS
        sys.stderr.write('  Abruf gescheitert: %s\n' % e)
        return b'', 0


def geraetefassung(ziel, pordner):
    """Welche Fassung meldet die Plugindatenbank des Geraets?

    Die Nummer stammt aus plugin.cfg und sagt NICHTS ueber den Inhalt der
    installierten Dateien - genau deshalb gibt es dieses Werkzeug. Sie wird
    hier nur benutzt, um das passende Tag zu waehlen.
    """
    code = ('import json\n'
            'd=json.load(open("/opt/loxberry/data/system/plugindatabase.json"))\n'
            'p=d.get("plugins",d)\n'
            'for v in (p.values() if isinstance(p,dict) else []):\n'
            '    if isinstance(v,dict) and v.get("folder")=="%s":\n'
            '        print(v.get("version",""))\n' % pordner)
    r = subprocess.run(['ssh', ziel, 'python3 -'], input=code,
                       capture_output=True, text=True, timeout=60)
    return r.stdout.strip().split('\n')[0].strip()


def main():
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument('ordner')
    p.add_argument('--geraet', default='loxberry-claude')
    p.add_argument('--tag', default='')
    p.add_argument('--ordner', dest='installordner', default='')
    a = p.parse_args()

    lokal = os.path.abspath(a.ordner)
    pcfg = os.path.join(lokal, 'plugin.cfg')
    if not os.path.isfile(pcfg):
        sys.stderr.write('ABBRUCH: %s hat keine plugin.cfg\n' % lokal)
        return 2

    pordner = a.installordner or cfg_wert(pcfg, 'FOLDER') or cfg_wert(pcfg, 'NAME')
    archivurl = cfg_wert(os.path.join(lokal, 'release.cfg'), 'ARCHIVEURL')
    m = re.match(r'https://github\.com/([^/]+/[^/]+)/archive/refs/tags/(.+)\.zip$',
                 archivurl or '')
    if not m:
        sys.stderr.write('ABBRUCH: ARCHIVEURL in release.cfg nicht lesbar: %r\n'
                         % archivurl)
        return 2
    linie = m.group(1)

    # Gegen WELCHES Tag wird verglichen? Gegen das der INSTALLIERTEN Fassung,
    # nicht gegen die neueste. Sonst meldete jedes Geraet, das noch nicht
    # aktualisiert wurde, lauter Abweichungen - und diese Pruefung ginge in
    # ihren eigenen Fehlalarmen unter. Ob eine neuere Fassung draussen ist,
    # steht als eigene Zeile daneben; das ist eine andere Frage.
    installiert = geraetefassung(a.geraet, pordner)
    if a.tag:
        tag = a.tag
    elif installiert:
        tag = 'v' + installiert
    else:
        tag = m.group(2)

    print('== Geraetestand gegen Tag ==')
    print('   Linie:            %s' % linie)
    print('   Am Geraet:        %s' % (installiert or 'nicht ermittelt'))
    print('   In release.cfg:   %s' % cfg_wert(os.path.join(lokal, 'release.cfg'),
                                               'VERSION'))
    print('   Verglichen gegen: %s' % tag)
    print('   Ordner am Geraet: %s' % pordner)
    print('   SSH-Ziel:         %s\n' % a.geraet)

    # --- Gegenprobe zuerst: ein Tag, das es nicht gibt, MUSS 404 liefern.
    # Ohne sie beweist ein HTTP 200 nichts - eine Weiterleitung auf eine
    # Fehlerseite saehe genauso aus.
    _, code = laden('https://api.github.com/repos/%s/zipball/refs/tags/'
                    'v99.99.99' % linie)
    if code != 404:
        sys.stderr.write('ABBRUCH: die Gegenprobe mit v99.99.99 lieferte %s '
                         'statt 404 - der Abruf misst nichts\n' % code)
        return 2
    print('   Gegenprobe v99.99.99 -> HTTP 404, wie erwartet')

    roh, code = laden('https://api.github.com/repos/%s/zipball/refs/tags/%s'
                      % (linie, tag))
    if code != 200 or not roh:
        sys.stderr.write('ABBRUCH: Tag %s lieferte HTTP %s\n' % (tag, code))
        return 2
    z = zipfile.ZipFile(io.BytesIO(roh))
    namen = [n for n in z.namelist() if not n.endswith('/')]
    huelle = namen[0].split('/')[0] + '/'
    archiv = {n[len(huelle):]: z.read(n) for n in namen}
    print('   Tag-Archiv:       HTTP 200, %d Dateien\n' % len(archiv))

    # --- Was liegt auf dem Geraet?
    befehle = []
    for _, muster in BAEUME:
        befehle.append('if [ -d %s ]; then find %s -type f -exec sha256sum {} '
                       '\\; ; fi' % (muster % pordner, muster % pordner))
    r = subprocess.run(['ssh', a.geraet, '; '.join(befehle)],
                       capture_output=True, text=True, timeout=300)
    zeilen = [z2 for z2 in r.stdout.split('\n') if '  /opt/' in z2]
    if not zeilen:
        sys.stderr.write('ABBRUCH: keine Datei am Geraet gefunden - nichts '
                         'gemessen\n%s\n' % r.stderr.strip()[:300])
        return 2

    def archivname(pfad):
        for vor, muster in BAEUME:
            wurzel = (muster % pordner) + '/'
            if pfad.startswith(wurzel):
                return vor + pfad[len(wurzel):]
        return None

    gleich = zeilenenden = ersetzt = befunde = fremd = 0
    gesehen = set()
    for z2 in zeilen:
        h, pfad = z2.strip().split('  ', 1)
        name = archivname(pfad)
        if name is None or name not in archiv:
            fremd += 1
            print('   [??] am Geraet, nicht im Tag: %s' % pfad)
            continue
        gesehen.add(name)
        inhalt = archiv[name]
        if hashlib.sha256(inhalt).hexdigest() == h:
            gleich += 1
        elif hashlib.sha256(inhalt.replace(b'\r\n', b'\n')).hexdigest() == h:
            zeilenenden += 1
        elif any(pl.encode() in inhalt for pl in PLATZHALTER):
            ersetzt += 1
        else:
            befunde += 1
            print('   [BEFUND] %s traegt NICHT den Inhalt des Tags' % name)

    fehlen = [n for n in archiv
              if archivname_moeglich(n) and n not in gesehen]
    for n in fehlen:
        print('   [BEFUND] %s liegt im Tag, aber nicht am Geraet' % n)

    print('\n== %d Dateien verglichen ==' % len(zeilen))
    print('   byteweise gleich:        %d' % gleich)
    print('   nur Zeilenenden:         %d  (Installer wandelt nach Unix)' % zeilenenden)
    print('   Platzhalter ersetzt:     %d  (plugininstall.pl:1834-1842)' % ersetzt)
    print('   nicht im Tag:            %d' % fremd)
    print('   ABWEICHEND:              %d' % (befunde + len(fehlen)))

    if befunde or fehlen:
        print('\nDas Geraet traegt NICHT den veroeffentlichten Stand.')
        return 1
    print('\nDas Geraet traegt den veroeffentlichten Stand.')
    return 0


def archivname_moeglich(name):
    """Liegt diese Archivdatei ueberhaupt in einem der verglichenen Baeume?"""
    return any(name.startswith(vor) for vor, _ in BAEUME)


if __name__ == '__main__':
    sys.exit(main())
