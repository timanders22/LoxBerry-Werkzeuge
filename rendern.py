#!/usr/bin/env python3
"""Rendert jede Plugin-Oberflaeche unter PHP 7.4 und 8.4 gegen die SDK-Attrappe.

Rein lesend fuer den Arbeitsordner: gearbeitet wird auf der Kopie unter stand/.
"""
import os, re, subprocess, sys, json
from pathlib import Path

HIER = Path(__file__).resolve().parent
LB = HIER / 'lb'
VORLAUF = HIER / 'vorlauf.php'
PHPS = [('7.4', r'C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe'),
        ('8.4', r'C:\tmp\php-8.4.24-Win32-vs17-x64\php.exe')]


def oberflaechen(d):
    aus = []
    for name in ('index.php',):
        for f in d.rglob(name):
            if 'htmlauth' in str(f):
                aus.append(f)
    return aus


def lauf(php, datei, plugin):
    umg = dict(os.environ)
    umg['LBHOMEDIR'] = str(LB)
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
    r = subprocess.run(
        [php, '-n', '-d', 'include_path=.;' + str(LB / 'libs' / 'phplib'),
         '-d', 'auto_prepend_file=' + str(VORLAUF),
         '-d', 'display_errors=0', '-d', 'error_reporting=32767',
         '-d', 'date.timezone=Europe/Berlin',
         '-d', 'extension_dir=' + str(Path(php).parent / 'ext'),
         '-d', 'extension=curl', '-d', 'extension=openssl', '-d', 'extension=mbstring',
         '-d', 'extension=sockets', '-d', 'extension=fileinfo',
         str(datei.resolve())],
        capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=str(datei.parent.resolve()), env=umg, timeout=60)
    befunde = []
    if '###BEFUNDE###' in r.stderr:
        befunde = [z for z in r.stderr.split('###BEFUNDE###', 1)[1].strip().splitlines() if z.strip()]
    rest = r.stderr.split('###BEFUNDE###')[0].strip()
    return r.stdout, befunde, rest


if __name__ == '__main__':
    ziel = sys.argv[1] if len(sys.argv) > 1 else 'stand'
    ergebnis = {}
    for d in sorted(Path(ziel).iterdir()):
        if not d.is_dir():
            continue
        for datei in oberflaechen(d):
            for v, php in PHPS:
                if not Path(php).is_file():
                    continue
                try:
                    out, bef, rest = lauf(php, datei, d.name)
                except subprocess.TimeoutExpired:
                    ergebnis.setdefault(d.name, []).append((v, 'ZEITUEBERSCHREITUNG', ''))
                    continue
                for b in bef:
                    ergebnis.setdefault(d.name, []).append((v, b, len(out)))
                if rest:
                    ergebnis.setdefault(d.name, []).append((v, 'STDERR|' + rest[:200], len(out)))
                if len(out) < 500:
                    ergebnis.setdefault(d.name, []).append((v, 'AUSGABE ZU KURZ (%d Zeichen)' % len(out), len(out)))
    json.dump({k: [list(map(str, x)) for x in v] for k, v in ergebnis.items()},
              open('render.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for p in sorted(ergebnis):
        print('== ' + p)
        gesehen = set()
        for v, b, n in ergebnis[p]:
            k = (v, b)
            if k in gesehen:
                continue
            gesehen.add(k)
            print('   [%s] %s' % (v, b))
