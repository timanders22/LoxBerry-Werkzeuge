# -*- coding: utf-8 -*-
"""Bestandsmessung fuer die Uebergabe:
A) Protokollzeilen mit veraenderlichem Text, aber festem Einmal-Schluessel
   (der Schluessel verdeckt einen neuen Grund - Befund aus WaermepumpeCloud 0.9.21).
B) Linien, die ein Passwort an ein HTML-Anmeldeformular schicken
   (Kandidaten fuer eine Bot-Pruefung wie bei myVAILLANT).
Gemessen wird im JEWEILS NEUESTEN Arbeitsordner je Linie.
"""
import os, re, sys
from collections import defaultdict

# Arbeitsordner: der Elternordner von Werkzeuge/, uebersteuerbar mit LOXWERK.
BASIS = (os.environ.get('LOXWERK') or
         os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fassung_schluessel(s):
    return [int(t) for t in re.findall(r'\d+', s)]

linien = defaultdict(list)
for n in os.listdir(BASIS):
    m = re.match(r'^(LoxBerry-Plugin-.+?)-(\d+(?:\.\d+)+)$', n)
    if m and os.path.isdir(os.path.join(BASIS, n)):
        linien[m.group(1)].append((fassung_schluessel(m.group(2)), n))

neueste = {k: sorted(v)[-1][1] for k, v in linien.items()}
print('Linien mit Arbeitsordner:', len(neueste))

# A) fester Einmal-Schluessel bei veraenderlichem Text
# Muster: <log-funktion>( <etwas mit . $variable> , 'fester_text' )
muster_a = re.compile(r"""(\w*log\w*)\s*\(\s*((?:'[^']*'|"[^"]*")\s*\.\s*[^;]{0,200}?)\s*,\s*('[a-z0-9_]+'|"[a-z0-9_]+")\s*\)""",
                      re.S)
var = re.compile(r'\$[A-Za-z_]')
treffer_a = defaultdict(list)
treffer_b = defaultdict(list)
muster_b = re.compile(r"(password|passwort|'pwd'|j_password)", re.I)
form_b = re.compile(r"(login-actions|authenticate|signin|login\.php|/login|auth/realms|SAMLRequest)", re.I)

for linie, ordner in sorted(neueste.items()):
    wurzel = os.path.join(BASIS, ordner)
    for pfad, _, dateien in os.walk(wurzel):
        for d in dateien:
            if not d.endswith(('.php', '.py', '.pl')):
                continue
            p = os.path.join(pfad, d)
            try:
                t = open(p, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            rel = os.path.relpath(p, wurzel).replace('\\', '/')
            for m in muster_a.finditer(t):
                if var.search(m.group(2)):
                    zeile = t[:m.start()].count('\n') + 1
                    treffer_a[linie].append('%s:%d %s(... , %s)' % (rel, zeile, m.group(1), m.group(3)))
            if muster_b.search(t) and form_b.search(t):
                treffer_b[linie].append(rel)

print('\n=== A) fester Einmal-Schluessel bei veraenderlichem Text ===')
for linie in sorted(treffer_a):
    print('%-46s %d' % (neueste[linie], len(treffer_a[linie])))
    for z in treffer_a[linie][:6]:
        print('      ', z)
print('Linien mit Befund A:', len(treffer_a))

print('\n=== B) Passwort an eine Anmeldeseite (Bot-Pruefung moeglich) ===')
for linie in sorted(treffer_b):
    print('%-46s %s' % (neueste[linie], ', '.join(sorted(set(treffer_b[linie]))[:4])))
print('Linien mit Befund B:', len(treffer_b))
