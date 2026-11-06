#!/usr/bin/env python3
"""Sagt die Fassungsnummer die Wahrheit?

Am 19.08.2026 stand dieselbe Nummer 0.9.8 fuer drei verschiedene Dinge: den
veroeffentlichten Stand auf GitHub, ein lokales Archiv mit mehr Inhalt und
die Fassung auf dem LoxBerry. Aufgefallen ist es durch Zufall - eine
Pruefung hatte sogar "release.cfg unveraendert auf 0.9.7" GEDRUCKT, ohne die
Datei zu lesen.

Dieses Werkzeug liest. Es beantwortet in einem Aufruf:

  1. Welche Nummer steht in plugin.cfg, release.cfg und prerelease.cfg?
  2. Welche Nummer steht in release.cfg im Standardzweig auf GitHub?
  3. Welche Tags und Releases gibt es dort?
  4. Antwortet das Archiv zu der Nummer, die der Zweig nennt?
  5. Ist das veroeffentlichte Archiv INHALTLICH dasselbe wie der Ordner?

Zu 5: drei Abweichungen sind KEIN Befund und werden benannt statt gemeldet -
Zeilenenden (Git normalisiert beim Schieben), release.cfg/prerelease.cfg
(REGELN_4 laesst sie erst NACH dem Tag heben, das Tag-Archiv traegt deshalb
fuer immer die vorige Nummer) und Punktdateien des Zweiges. Jede wird eng
geprueft; alles andere bleibt rot und wird namentlich genannt.

Seit 29.08.2026, in beide Richtungen geeicht. Am 01.09.2026 erweitert: bei den
beiden .cfg zaehlen die WIRKSAMEN Zeilen, nicht die Bytes - ein geaenderter
Kommentar ist kein Befund, eine geaenderte Adresse sehr wohl. Die Regel steht
in cfg_abweichung.py und wird von cfg_abweichung_eichung.py an 16 Faellen
gemessen (6 gruen, 10 rot).

Seit 03.09.2026: der Zweig wird nicht mehr fest als 'master' angenommen. Er
kommt aus der RELEASECFG-Adresse der plugin.cfg (dort MUSS er der Standardzweig
des Repositories sein, REGELN_4); fehlt die Angabe, wird main, dann master
versucht. Anlass: 20 der 49 Linien nennen in der plugin.cfg 'main', 29
'master' (gemessen 02.09.2026). Gemessen am 03.09.2026: alle 20 main-Linien
fuehren daneben einen Zweig master mit derselben Nummer - das feste 'master'
hat also bisher NICHT falsch gemessen. Es misst nur den falschen Zweig: den,
den LoxBerry NICHT liest. Laufen die beiden Zweige einmal auseinander, waere
der Befund falsch, ohne dass es jemand saehe. Deshalb jetzt der Zweig aus
der plugin.cfg, und eine Warnung, wenn es ihn nicht gibt.

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

# Die Frage "ist der Unterschied zweier release.cfg genau der des
# Veroeffentlichens?" steht in einem eigenen Modul - damit
# cfg_abweichung_eichung.py sie in beide Richtungen messen kann, ohne dass
# dafuer dieses Werkzeug mit Netzzugriff laufen muss.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from cfg_abweichung import erklaerbar as _cfg_erklaerbar
except ImportError:                                   # pragma: no cover
    _cfg_erklaerbar = None

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

# ---- Welcher Zweig? Aus der plugin.cfg, sonst main, dann master ----
zweig_cfg = ''
rc_url = feld_aus(os.path.join(ORDNER, 'plugin.cfg'), 'RELEASECFG') or ''
mz = re.search(r'raw\.githubusercontent\.com/[^/]+/[^/]+/([^/]+)/', rc_url)
if mz:
    zweig_cfg = mz.group(1)
kandidaten = [zweig_cfg] if zweig_cfg else []
kandidaten += [z for z in ('main', 'master') if z not in kandidaten]
zweig, mroh = None, 'FEHLER: kein Zweig geprueft'
for z in kandidaten:
    roh = hol('https://raw.githubusercontent.com/%s/%s/%s/release.cfg' % (nutzer, repo, z))
    if not roh.startswith('FEHLER'):
        zweig, mroh = z, roh
        break
    mroh = roh
print('\n== GitHub, Zweig %s ==' % (zweig or '?'))
if zweig_cfg:
    print('  plugin.cfg nennt in RELEASECFG den Zweig %s' % zweig_cfg)
else:
    print('  plugin.cfg nennt keinen Zweig (RELEASECFG fehlt oder ohne raw-Adresse)')
if zweig and zweig_cfg and zweig != zweig_cfg:
    print('  ACHTUNG: unter %s liegt keine release.cfg, gefunden unter %s -'
          ' die plugin.cfg zeigt auf einen Zweig, den es nicht gibt.' % (zweig_cfg, zweig))
m_ver = None
if mroh.startswith('FEHLER'):
    print('  release.cfg in keinem Zweig (%s) abrufbar: %s' % (', '.join(kandidaten), mroh))
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
        marke = '   <== Zweig %s BIETET diese Nummer AN, das Archiv fehlt!' % zweig
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

        # ---- Drei erklaerte Abweichungen, die KEIN Befund sind ----
        #
        # ANLASS (29.08.2026): dieses Werkzeug war nach JEDER Veroeffentlichung
        # rot. REGELN_4 verlangt "erst taggen, DANN release.cfg heben" - also
        # traegt das Tag-Archiv in release.cfg und prerelease.cfg fuer immer die
        # ALTE Nummer, der Ordner die neue. Gemessen an vier unberuehrten,
        # laengst veroeffentlichten Linien (Robonect 1.1.2, Sprachsteuerung
        # 0.10.0, Octopus 1.1.2, SignalBot 0.9.18): alle vier rot, alle vier zu
        # Unrecht. Ein Waechter, dessen Meldung immer gleich lautet, wird nicht
        # mehr gelesen - und am selben Tag wich eine Linie WIRKLICH im Code ab,
        # mit genau derselben Meldung.
        #
        # Die Ausnahmen sind bewusst eng. Jede prueft, dass der Unterschied
        # genau der erwartete ist, nicht bloss, dass die Datei so heisst:
        #
        #   Zeilenenden   Git schreibt beim Schieben CRLF auf LF um. Ein Ordner
        #                 mit CRLF-Dateien kann nie byte-gleich mit seinem
        #                 Tag-Archiv sein (Smartmeter classic, Docker-NG).
        #                 Geprueft wird: nach dem Angleichen gleich.
        #   Fassungszeile release.cfg/prerelease.cfg, und der Ordner traegt eine
        #                 HOEHERE Nummer. Geprueft wird: ersetzt man im Tag die
        #                 alte Nummer durch die neue, kommt Zeichen fuer Zeichen
        #                 die Datei des Ordners heraus. Damit faellt jede andere
        #                 Aenderung an diesen Dateien durch.
        #   Repodateien   .gitignore und .gitattributes AN DER WURZEL. Ein
        #                 Tag-Archiv enthaelt die Punktdateien des Zweiges; der
        #                 Arbeitsordner hat sie nicht oder anders. Sie werden
        #                 nicht mitinstalliert (REGELN_4, 26.08.2026).
        #                 NAMENTLICH und nur an der Wurzel - nicht "alles mit
        #                 Punkt": webfrontend/htmlauth/.user.ini ist eine
        #                 wirksame PHP-Konfiguration und muss rot bleiben.
        #
        # NACHTRAG 01.09.2026: die enge Fassung der Ausnahme hat NICHT
        # getragen. Beschattungswaechter 0.9.13 hat in beiden .cfg einen
        # Kommentar ergaenzt; damit war die Datei nicht mehr durch blosses
        # Ersetzen der Nummer zu erzeugen, und eine frisch und richtig
        # veroeffentlichte Fassung stand rot da. Die Entscheidung liegt jetzt
        # in cfg_abweichung.py: verglichen werden die WIRKSAMEN Zeilen
        # (Abschnittskopf, SCHLUESSEL=WERT), Kommentare zaehlen nicht. Streng
        # bleibt der Rest - dieselben Schluessel in derselben Reihenfolge, die
        # Nummer im Ordner hoeher, und jeder abweichende Wert muss aus dem
        # alten entstehen, indem man die alte Nummer durch die neue ersetzt.
        # Bleibt eine .cfg trotzdem rot, nennt der Bericht den Grund.
        #
        # Wer hier eine weitere Ausnahme anbaut, misst sie vorher in BEIDE
        # Richtungen: ein Fall, der gruen werden soll, und einer, der rot
        # bleiben muss.
        def _fassung(b):
            m2 = re.search(rb'^VERSION=([^\r\n]+)', b, re.M)
            return m2.group(1).decode('utf-8', 'replace').strip() if m2 else ''

        def _zahlen(v):
            try:
                return tuple(int(x) for x in v.split('.'))
            except ValueError:
                return None

        _lf = lambda b: b.replace(b'\r\n', b'\n')
        # Nur an der WURZEL und nur diese Namen. Ein Pfad mit '/' faellt
        # durch, damit webfrontend/htmlauth/.user.ini nicht mitrutscht.
        REPODATEIEN = ('.gitignore', '.gitattributes')
        zeilenenden, fassungszeile, echt, repodateien = [], [], [], []
        cfg_grund = {}          # warum eine .cfg NICHT erklaert werden konnte
        for rp in anders:
            a_b = drin[rp]
            n_b = open(os.path.join(ORDNER, rp.replace('/', os.sep)), 'rb').read()
            if _lf(a_b) == _lf(n_b):
                zeilenenden.append(rp)
                continue
            if rp in ('release.cfg', 'prerelease.cfg'):
                if _cfg_erklaerbar is not None:
                    ok, grund = _cfg_erklaerbar(a_b, n_b)
                    if ok:
                        fassungszeile.append('%s (%s)' % (rp, grund))
                        continue
                    cfg_grund[rp] = grund
                else:
                    # Rueckfallebene, falls cfg_abweichung.py fehlt: die enge
                    # Fassung vom 29.08.2026, die nur die Nummer erklaert.
                    a_v, n_v = _fassung(a_b), _fassung(n_b)
                    a_z, n_z = _zahlen(a_v), _zahlen(n_v)
                    if (a_z and n_z and n_z > a_z
                            and _lf(a_b).replace(a_v.encode(), n_v.encode()) == _lf(n_b)):
                        fassungszeile.append(rp)
                        continue
            if rp in REPODATEIEN:
                repodateien.append(rp)
                continue
            echt.append(rp)
        # Beide Richtungen, seit 07.09.2026. Bis dahin war nur "fehlt im
        # Ordner" erklaert - der umgekehrte Fall blieb rot, obwohl er der
        # haeufigere ist: linie_veroeffentlichen.sh nimmt .gitattributes von
        # der Uebertragung aus ("Entscheidung des Hausherrn, zweimal",
        # Werkzeuge/linie_veroeffentlichen.sh:37). Die Datei liegt damit im
        # Ordner und nie im Zweig, und die Linie stand nach JEDER
        # Veroeffentlichung als "DIESELBE NUMMER, VERSCHIEDENER INHALT" da.
        # Ein Fehlalarm bei jedem Lauf ist eine abgeschaltete Pruefung.
        # Es bleibt bei der engen Fassung: NAMENTLICH und nur an der Wurzel.
        repodateien += [x for x in fehlt if x in REPODATEIEN]
        repodateien += [x for x in neu if x in REPODATEIEN]
        fehlt_echt = [x for x in fehlt if x not in REPODATEIEN]
        neu = [x for x in neu if x not in REPODATEIEN]

        for was, liste in (('nur Zeilenenden (Git normalisiert)', zeilenenden),
                           ('nur die Fassungszeile, Ordner hoeher', fassungszeile),
                           ('Repodateien des Zweiges', repodateien)):
            if liste:
                print('      erklaert - %-36s %s' % (was + ':', ', '.join(liste)))

        if echt or neu or fehlt_echt:
            print('      >>> DIESELBE NUMMER, VERSCHIEDENER INHALT. Nummer erhoehen.')
            if echt:
                print('          wirklich abweichend: %s' % ', '.join(echt))
                for _rp in echt:
                    if _rp in cfg_grund:
                        print('            %-18s %s' % (_rp + ':', cfg_grund[_rp]))
            if neu:
                print('          nur im Ordner:       %s' % ', '.join(neu))
            if fehlt_echt:
                print('          fehlt im Ordner:     %s' % ', '.join(fehlt_echt))
        elif zeilenenden or fassungszeile or repodateien:
            print('      >>> Kein Befund. Jede Abweichung ist erklaert (siehe oben) -')
            print('          das ist der Normalzustand NACH dem Veroeffentlichen.')
        else:
            print('      >>> byte-gleich. Die Nummer sagt die Wahrheit.')

print('\n== Beurteilung ==')
if m_ver and p_ver and m_ver == p_ver:
    print('  Der Ordner traegt dieselbe Nummer wie das, was Zweig %s anbietet.' % zweig)
    print('  In Ordnung ist das, solange der Abschnitt oben KEINEN Befund nennt -')
    print('  byte-gleich, oder jede Abweichung erklaert (Zeilenenden,')
    print('  Fassungszeile, Punktdateien). Steht dort "Nummer erhoehen",')
    print('  nennt die Zeile darunter die Datei, um die es geht.')
elif m_ver and p_ver:
    print('  Ordner %s, angeboten wird %s.' % (p_ver, m_ver))
    if r_ver == m_ver:
        print('  release.cfg im Ordner steht auf der angebotenen Nummer - richtig,')
        print('  solange der Tag zur Ordner-Nummer noch nicht existiert (REGELN_4).')
    else:
        print('  release.cfg im Ordner (%s) weicht von Zweig %s (%s) ab - nachsehen.' % (r_ver, zweig, m_ver))
