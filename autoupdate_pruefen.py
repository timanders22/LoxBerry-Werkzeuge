#!/usr/bin/env python3
"""Steht das Auto-Update an - und darf es?

Anlass, 28.08.2026: die LoxBerry-Pluginverwaltung meldete fuer
Beschattungswaechter 0.9.9 "No AutoUpdate". Der Grund stand seit dem ersten
Tag in der plugin.cfg:

    # Bewusst AUS, solange es das Repository noch nicht gibt.
    AUTOMATIC_UPDATES=false

Das war richtig - am 23./25.08., als es die Repositorien noch nicht gab.
Danach hat es niemand zurueckgedreht, weil nichts danach gefragt hat. Eine
Bedingung, die niemand nachprueft, bleibt fuer immer wahr.

DAS WERKZEUG PRUEFT DREI DINGE JE LINIE

  1. Steht AUTOMATIC_UPDATES auf true?
  2. Zeigen RELEASECFG und PRERELEASECFG auf das EIGENE Repositorium?
     Ein fremdes waere schlimmer als keines: LoxBerry vergleicht Fassungen
     als Zahl, und ein fremdes 2021.05.14 ist groesser als 0.9.0 - daraus
     wuerde ein stilles Downgrade auf ein voellig anderes Plugin.
  3. Gibt es den Zweig, auf den die Adressen zeigen, und traegt er die
     beiden .cfg? (Nur mit --fern, sonst wird nicht ins Netz gefasst.)

Es aendert nichts.

Aufruf:  autoupdate_pruefen.py [--fern] [ORDNER ...]
"""
import glob, os, re, subprocess, sys

fern = '--fern' in sys.argv
argv = [a for a in sys.argv[1:] if a != '--fern']


def aktuelle():
    st = {}
    for d in sorted(glob.glob('LoxBerry-Plugin-*')):
        if not os.path.isdir(d):
            continue
        m = re.match(r'(LoxBerry-Plugin-.+?)-(\d[\d.]*)$', d)
        if not m:
            continue
        k = tuple(int(x) for x in m.group(2).split('.'))
        if m.group(1) not in st or k > st[m.group(1)][0]:
            st[m.group(1)] = (k, d)
    return [v[1] for v in st.values()]


print('%-42s %-6s %-8s %s' % ('Plugin', 'Auto', 'Adressen', 'Zweig'))
print('-' * 78)
n_aus = n_fremd = 0
for d in sorted(argv or aktuelle()):
    p = os.path.join(d, 'plugin.cfg')
    if not os.path.isfile(p):
        continue
    t = open(p, encoding='utf-8', errors='replace').read().replace('\r\n', '\n')
    t = '\n'.join(z for z in t.split('\n') if not z.lstrip().startswith('#'))
    auto = (re.search(r'^AUTOMATIC_UPDATES=(\w+)', t, re.M) or [None, '?'])[1]
    eigen = os.path.basename(d)
    eigen = re.sub(r'-\d[\d.]*$', '', eigen)
    adr = re.findall(r'^(?:PRE)?RELEASECFG=(\S+)', t, re.M)
    passend = all(('/timanders22/%s/' % eigen) in a for a in adr) and len(adr) == 2
    zweig = '-'
    if fern and adr:
        m = re.search(r'/timanders22/([^/]+)/([^/]+)/', adr[0])
        if m:
            r = subprocess.run(['git', 'ls-remote',
                                'https://github.com/timanders22/%s.git' % m.group(1),
                                m.group(2)], capture_output=True, text=True)
            zweig = 'da' if r.stdout.strip() else 'FEHLT'
    if auto != 'true':
        n_aus += 1
    if not passend:
        n_fremd += 1
    print('%-42s %-6s %-8s %s'
          % (os.path.basename(d)[16:58], auto,
             'eigen' if passend else 'PRUEFEN', zweig))
print('-' * 78)
print('%d Linie(n) ohne Auto-Update, %d mit fragwuerdigen Adressen.' % (n_aus, n_fremd))
if n_aus:
    print('Ein "false" ist nur so lange richtig, wie seine Bedingung gilt.')
