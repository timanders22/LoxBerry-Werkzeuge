# -*- coding: utf-8 -*-
"""Nennt die README-Kopfzeile dieselbe Fassung wie die plugin.cfg?

Reihenpruefung ueber den ganzen Bestand. Anlass: bei der Einspeisebremse
nennt die Kopfzeile 0.9.10, die plugin.cfg 0.9.12. Das alte Muster in
fassung_setzen.py haette sie beim naechsten Hochsetzen einfach auf die neue
Nummer gesetzt - die Abweichung waere nie aufgefallen, und die Kopfzeile
haette zwei Fassungen lang gelogen.

    python3 readme_kopfzeile_reihe.py

NICHT jeder Treffer ist ein Befund. Bei Ultraschall 1.1.10 steht im Kopf
"Version 0.30 aus dem Jahr 2015" - die Fassung des URSPRUNGSPLUGINS von
Dietmar Wimmer. Diese Liste ist eine Frageliste, kein Urteil; jede Zeile
gehoert angesehen.
"""
import io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
# Der Arbeitsordner ist der Elternordner von Werkzeuge/; mit der
# Umgebungsvariablen LOXWERK laesst er sich uebersteuern.
os.chdir(os.environ.get('LOXWERK') or
         os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

KOPFZEILEN = 20

def kopf_fassung(d):
    """Die erste Fassung im Kopfbereich, ausserhalb von Ueberschriften."""
    zeilen = d.split(b'\n')[:KOPFZEILEN]
    for i, z in enumerate(zeilen):
        if z.lstrip(b' \t>*_').startswith(b'#'):
            continue
        # Eine Kopfzeile steht als EIGENER ABSATZ. Ohne diese Bedingung
        # traf die Suche bei Ultraschall 1.1.10 eine FORTSETZUNGSZEILE:
        # "Grundlage ist das Plugin ... von Dietmar Wimmer," bricht um, und
        # die naechste Zeile beginnt mit "Version 0.30 aus dem Jahr 2015".
        # Sie beginnt also mit "Version" und ist trotzdem keine Kopfzeile.
        if i > 0 and zeilen[i - 1].strip() != b'':
            continue
        m = re.search(rb'(?<![0-9.])Version[ :]+([0-9]+\.[0-9][0-9.]*)', z)
        if m:
            return (i + 1, m.group(1).decode())
    return (None, None)

print('%-34s %-9s %-9s %s' % ('Plugin', 'plugin.cfg', 'README', 'Befund'))
print('-' * 78)
n = ab = ohne = 0
for e in sorted(os.listdir('.')):
    r, c = os.path.join(e, 'README.md'), os.path.join(e, 'plugin.cfg')
    if not (e.startswith('LoxBerry-Plugin-') and os.path.isfile(r) and os.path.isfile(c)):
        continue
    m = re.search(rb'^VERSION=([^\r\n]*)', io.open(c, 'rb').read(), re.M)
    if not m:
        continue
    cfg = m.group(1).decode().strip()
    zeile, rm = kopf_fassung(io.open(r, 'rb').read())
    n += 1
    if rm is None:
        ohne += 1
        continue
    if rm != cfg:
        ab += 1
        print('%-34s %-9s %-9s Zeile %d weicht ab' % (e[16:50], cfg, rm, zeile))
print('-' * 78)
print('%d Plugins: %d mit abweichender Kopfzeile, %d ohne Fassungszeile im Kopf, '
      '%d stimmig' % (n, ab, ohne, n - ab - ohne))
