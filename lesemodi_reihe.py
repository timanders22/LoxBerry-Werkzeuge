#!/usr/bin/env python3
"""Zeigt die Oberflaeche den Text, der in der Sprachdatei steht?

`parse_ini_file` liest je nach Scanner verschieden:

    INI_SCANNER_RAW      \\\\i bleibt \\\\i
    INI_SCANNER_NORMAL   \\\\i wird zu \\i

Ein Plugin, das mit RAW liest und `\\\\iFELDNAME=\\\\i\\\\v` in der Datei
stehen hat, zeigt dem Anwender ein Suchmuster mit DOPPELTEN Backslashes.
Wer es nach Loxone kopiert, bekommt eine Befehlserkennung, die nie trifft -
dieselbe Klasse wie ein fehlendes Trennzeichen.

Gemessen wird deshalb beides zusammen: welcher Scanner benutzt wird UND ob
die beiden Lesarten auseinandergehen.

    python3 lesemodi_reihe.py [<Pluginordner> ...]

Rueckgabe 0, wenn kein Plugin einen Wert hat, der je nach Scanner anders
herauskommt, als sein eigener Scanner ihn liest.
"""
import io
import os
import re
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HIER = os.path.dirname(os.path.abspath(__file__))
ARBEIT = os.path.dirname(HIER)
PHP = next((p for p in (r'C:\tmp\php-8.4.24-Win32-vs17-x64\php.exe',
                        r'C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe', 'php')
            if p == 'php' or os.path.isfile(p)), 'php')

PROBE = r'''<?php
$d = $argv[1];
$raw = @parse_ini_file($d, true, INI_SCANNER_RAW);
$nor = @parse_ini_file($d, true, INI_SCANNER_NORMAL);
if (!is_array($raw)) { exit(0); }
foreach ($raw as $ab => $paare) {
    if (!is_array($paare)) { continue; }
    foreach ($paare as $k => $v) {
        $vr = trim((string) $v, '"');
        $vn = isset($nor[$ab][$k]) ? (string) $nor[$ab][$k] : '';
        if ($vr !== $vn) {
            echo $ab . '.' . $k . "\t" . substr($vr, 0, 60) . "\n";
        }
    }
}
'''


def scanner(o):
    """Mit welchem Scanner liest das Plugin? (RAW / NORMAL / unbekannt)"""
    for w, _, ds in os.walk(o):
        if os.sep + '.git' in w:
            continue
        for d in sorted(ds):
            if not d.endswith('.php'):
                continue
            t = io.open(os.path.join(w, d), encoding='utf-8', errors='replace').read()
            if 'parse_ini_file' not in t:
                continue
            if 'INI_SCANNER_RAW' in t:
                return 'RAW'
            if 'INI_SCANNER_TYPED' in t:
                return 'TYPED'
            if re.search(r'parse_ini_file\s*\([^)]*\)', t):
                return 'NORMAL'
    return '?'


def main():
    ordner = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not ordner:
        ordner = [e for e in sorted(os.listdir(ARBEIT))
                  if e.startswith('LoxBerry-Plugin-')
                  and os.path.isdir(os.path.join(ARBEIT, e))]
    fd, probe = tempfile.mkstemp(suffix='.php')
    os.write(fd, PROBE.encode('utf-8'))
    os.close(fd)

    print('%-32s %-7s %s' % ('Plugin', 'Scanner', 'Werte, die je nach Scanner anders lauten'))
    print('-' * 92)
    betroffen = 0
    try:
        for e in ordner:
            o = e if os.path.isdir(e) else os.path.join(ARBEIT, e)
            if not os.path.isdir(o):
                continue
            sc = scanner(o)
            treffer = []
            for w, _, ds in os.walk(os.path.join(o, 'templates')):
                for d in sorted(ds):
                    if not d.endswith('.ini'):
                        continue
                    r = subprocess.run([PHP, probe, os.path.join(w, d)],
                                       capture_output=True, text=True,
                                       encoding='utf-8', errors='replace')
                    for z in r.stdout.strip().splitlines():
                        if z.strip():
                            treffer.append(z.split('\t')[0])
            if treffer:
                betroffen += 1
                print('%-32s %-7s %s' % (os.path.basename(o)[16:47], sc,
                                         ', '.join(sorted(set(treffer))[:4])))
    finally:
        os.unlink(probe)
    print('-' * 92)
    print('%d Plugin(e) geprueft, %d mit abweichenden Werten'
          % (len(ordner), betroffen))
    return 1 if betroffen else 0


if __name__ == '__main__':
    sys.exit(main())
