#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Traegt das Sicherungsformular den Formulartoken, den die Linie verlangt?

Sechs Linien weisen JEDEN POST ohne gueltigen Formulartoken ab - meist mit
$_POST = array(), sodass danach kein einziger Zweig mehr anlaeuft. Ein
Sicherungsformular ohne Tokenfeld erscheint dort zwar, tut aber nichts und
meldet stattdessen einen CSRF-Fehler.

Gemessen wird an der GERENDERTEN Seite, und der Massstab ist die Seite
selbst: was ein bestehendes Formular an verstecken Feldern fuehrt, muessen
die beiden neuen auch fuehren.
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HIER = os.path.dirname(os.path.abspath(__file__))
ARBEIT = os.path.dirname(HIER)
sys.path.insert(0, HIER)
import importlib
_r = importlib.import_module('rendern')


def seite(o):
    d = list(_r.oberflaechen(_r.Path(o)))
    p = next((x for _v, x in _r.PHPS if os.path.isfile(x)), None)
    if not d or p is None:
        return None
    return _r.lauf(p, d[0], os.path.basename(o))[0]


def formulare(t):
    return re.findall(r'<form\b.*?</form>', t, re.S | re.I)


print('%-30s %-16s %s' % ('Plugin', 'Seite verlangt', 'Sicherungsformulare'))
print('-' * 78)
befund = []
for e in sorted(os.listdir(ARBEIT)):
    o = os.path.join(ARBEIT, e)
    if not e.startswith('LoxBerry-Plugin-') or not os.path.isdir(o):
        continue
    idx = os.path.join(o, 'webfrontend', 'htmlauth', 'index.php')
    if not os.path.isfile(idx):
        continue
    q = open(idx, encoding='utf-8', errors='replace').read()
    if '_zurueck' not in q:
        continue
    t = seite(o)
    if not t:
        print('%-30s %s' % (e[16:45], 'nicht gerendert'))
        continue
    fs = formulare(t)
    # Welche versteckten Felder fuehren die BESTEHENDEN Formulare?
    pflicht = set()
    for f in fs:
        if '_zurueck' in f or '_sichern' in f:
            continue
        for n in re.findall(r'type=["\']hidden["\'][^>]*name=["\'](\w+)["\']', f):
            pflicht.add(n)
        for n in re.findall(r'name=["\'](\w+)["\'][^>]*type=["\']hidden["\']', f):
            pflicht.add(n)
    # 'fmt' gehoert dazu: Heimkino und MGiSmart lesen genau diesen
    # Schluessel. Die erste Fassung kannte ihn nicht und meldete fuer
    # beide einen Strich - der sich wie ein Haken einsammelt.
    pflicht &= {'formtoken', 'fmt', 'merkmal', 'token', 'csrf'}
    meine = [f for f in fs if '_zurueck' in f or '_sichern' in f]
    if not meine:
        print('%-30s %-16s %s' % (e[16:45], ','.join(pflicht) or '-', 'KEINE gefunden'))
        continue
    fehlt = set()
    for f in meine:
        for n in pflicht:
            if not re.search(r'name=["\']%s["\']' % n, f):
                fehlt.add(n)
    if fehlt:
        befund.append((e, sorted(fehlt)))
    print('%-30s %-16s %s' % (e[16:45], ','.join(sorted(pflicht)) or '-',
                              ('ROT fehlt: ' + ','.join(sorted(fehlt))) if fehlt
                              else 'ok (%d)' % len(meine)))
print('-' * 78)
print('%d Linie(n) mit Befund' % len(befund))
