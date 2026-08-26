#!/usr/bin/env python3
"""Sagt die Fassungsnummer die Wahrheit?

Am 19.08.2026 stand dieselbe Nummer 0.9.8 fuer drei verschiedene Dinge: den
veroeffentlichten Stand auf GitHub, ein lokales Archiv mit mehr Inhalt und
die Fassung auf dem LoxBerry. Aufgefallen ist es durch Zufall - eine
Pruefung hatte sogar "release.cfg unveraendert auf 0.9.7" GEDRUCKT, ohne die
Datei zu lesen.

Dieses Werkzeug liest. Es beantwortet in einem Aufruf:

  1. Welche Nummer steht in plugin.cfg, release.cfg und prerelease.cfg?
  2. Welche Nummer steht in release.cfg im Zweig master auf GitHub?
  3. Welche Tags und Releases gibt es dort?
  4. Antwortet das Archiv zu der Nummer, die master nennt?
  5. Ist das veroeffentlichte Archiv INHALTLICH dasselbe wie der Ordner?

Rein lesend. Ohne Netz laeuft es trotzdem und sagt, was es nicht pruefen
konnte - eine Pruefung, die bei fehlendem Netz schweigt, ist schlimmer als
keine.

Aufruf:  python3 fassungslage.py ORDNER [--ohne-netz]
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
import zipfile
import hashlib
import io

ORDNER = sys.argv[1] if len(sys.argv) > 1 else '.'
OHNE_NETZ = '--ohne-netz' in sys.argv


def version_aus(pfad):
    """VERSION= aus einer cfg lesen. None, wenn es die Datei nicht gibt."""
    if not os.path.isfile(pfad):
        return None
    for zeile in open(pfad, encoding='utf-8', errors='replace').read().splitlines():
        if zeile.startswith('VERSION'):
            return zeile.split('=', 1)[1].strip()
    return ''


def feld_aus(pfad, name):
    if not os.path.isfile(pfad):
        return None
    for zeile in open(pfad, encoding='utf-8', errors='replace').read().splitlines():
        if zeile.startswith(name):
            return zeile.split('=', 1)[1].strip()
    return ''


def hol(url, roh=False, zeit=20):
    try:
        with urllib.request.urlopen(url, timeout=zeit) as a:
            d = a.read()
        return d if roh else d.decode('utf-8', 'replace')
    except Exception as e:
        return ('FEHLER: %s' % e) if not roh else None


print('== Der Ordner ==')
print('  %s' % os.path.abspath(ORDNER))
p_ver = version_aus(os.path.join(ORDNER, 'plugin.cfg'))
r_ver = version_aus(os.path.join(ORDNER, 'release.cfg'))
pr_ver = version_aus(os.path.join(ORDNER, 'prerelease.cfg'))
if p_ver is None:
    print('  KEINE plugin.cfg - ist das ein Plugin-Ordner?')
    sys.exit(1)
print('  plugin.cfg      VERSION=%s   <- was in diesem Ordner steckt' % p_ver)
print('  release.cfg     VERSION=%s' % r_ver)
print('  prerelease.cfg  VERSION=%s' % pr_ver)
if r_ver != pr_ver:
    print('  ACHTUNG: release.cfg und prerelease.cfg nennen VERSCHIEDENE Nummern.')

url = feld_aus(os.path.join(ORDNER, 'release.cfg'), 'ARCHIVEURL') or ''
m = re.search(r'github\.com/([^/]+)/([^/]+)/archive', url)
if not m:
    print('\n  ARCHIVEURL nennt kein GitHub-Repository - der Rest entfaellt.')
    sys.exit(0)
nutzer, repo = m.group(1), m.group(2)
print('  Repository      %s/%s' % (nutzer, repo))

if OHNE_NETZ:
    print('\n== GitHub == uebersprungen (--ohne-netz)')
    sys.exit(0)

print('\n== GitHub, Zweig master ==')
mroh = hol('https://raw.githubusercontent.com/%s/%s/master/release.cfg' % (nutzer, repo))
m_ver = None
if mroh.startswith('FEHLER'):
    print('  release.cfg nicht abrufbar: %s' % mroh)
else:
    for zeile in mroh.splitlines():
        if zeile.startswith('VERSION'):
            m_ver = zeile.split('=', 1)[1].strip()
    print('  release.cfg     VERSION=%s   <- was fremde Anlagen ANGEBOTEN bekommen' % m_ver)

print('\n== Releases ==')
rj = hol('https://api.github.com/repos/%s/%s/releases' % (nutzer, repo))
tags = []
if rj.startswith('FEHLER'):
    print('  nicht abrufbar: %s' % rj)
else:
    try:
        d = json.loads(rj)
        if isinstance(d, dict):
            print('  %s' % d.get('message', '?'))
        else:
            for r in d:
                tags.append(r['tag_name'])
            print('  %s' % (', '.join(tags) if tags else 'keine'))
    except Exception as e:
        print('  Antwort unlesbar: %s' % e)

# ---- Die entscheidende Frage: passt die angebotene Nummer zu einem Archiv? ----
print('\n== Antwortet das Archiv? ==')
for nr in sorted({v for v in (m_ver, p_ver, r_ver) if v}):
    u = 'https://github.com/%s/%s/archive/refs/tags/v%s.zip' % (nutzer, repo, nr)
    try:
        with urllib.request.urlopen(u, timeout=25) as a:
            code = a.getcode()
            inhalt = a.read()
    except urllib.error.HTTPError as e:
        code, inhalt = e.code, None
    except Exception as e:
        code, inhalt = str(e), None
    marke = ''
    if nr == m_ver and code != 200:
        marke = '   <== master BIETET diese Nummer AN, das Archiv fehlt!'
    print('  v%-8s HTTP %-24s %d Byte%s'
          % (nr, code, len(inhalt) if inhalt else 0, marke))

    # ---- Und wenn es antwortet: ist es INHALTLICH der Ordner? ----
    if inhalt and nr == p_ver:
        z = zipfile.ZipFile(io.BytesIO(inhalt))
        drin = {}
        for n in z.namelist():
            if not n.endswith('/'):
                drin[n.split('/', 1)[1]] = z.read(n)
        z.close()
        anders, fehlt, neu = [], [], []
        for wurzel, verz, dateien in os.walk(ORDNER):
            verz.sort()
            for dd in sorted(dateien):
                voll = os.path.join(wurzel, dd)
                rp = os.path.relpath(voll, ORDNER).replace(os.sep, '/')
                b = open(voll, 'rb').read()
                if rp not in drin:
                    neu.append(rp)
                elif b != drin[rp]:
                    anders.append(rp)
        vorhanden = {os.path.relpath(os.path.join(w, dd), ORDNER).replace(os.sep, '/')
                     for w, _, ds in os.walk(ORDNER) for dd in ds}
        fehlt = sorted(set(drin) - vorhanden)
        print('    Inhalt gegen den Ordner:')
        print('      abweichend: %s' % (', '.join(anders) if anders else 'keine'))
        print('      nur hier:   %s' % (', '.join(neu) if neu else 'keine'))
        print('      nur dort:   %s' % (', '.join(fehlt) if fehlt else 'keine'))
        if anders or neu or fehlt:
            print('      >>> DIESELBE NUMMER, VERSCHIEDENER INHALT. Nummer erhoehen.')
        else:
            print('      >>> byte-gleich. Die Nummer sagt die Wahrheit.')

print('\n== Beurteilung ==')
if m_ver and p_ver and m_ver == p_ver:
    print('  Der Ordner traegt dieselbe Nummer wie das, was master anbietet.')
    print('  Das ist nur dann in Ordnung, wenn beide byte-gleich sind (siehe oben).')
elif m_ver and p_ver:
    print('  Ordner %s, angeboten wird %s.' % (p_ver, m_ver))
    if r_ver == m_ver:
        print('  release.cfg im Ordner steht auf der angebotenen Nummer - richtig,')
        print('  solange der Tag zur Ordner-Nummer noch nicht existiert (REGELN_4).')
    else:
        print('  release.cfg im Ordner (%s) weicht von master (%s) ab - nachsehen.' % (r_ver, m_ver))
