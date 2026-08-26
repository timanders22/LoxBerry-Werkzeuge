#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Freigabepruefung: was vor jeder Veroeffentlichung gemessen gehoert.

REGELN_4, "Die Freigabepruefung gehoert in ein Skript, nicht in eine Liste":
drei der Punkte liefern Zahlen, die in die Freigabenotiz gehoeren, und zwei
sind von Hand kaum zu pruefen.

Geprueft wird gegen das ARCHIV, nicht gegen den Ordner - das Archiv ist das,
was ausgeliefert wird. Ein Packwerkzeug, das Zeilenenden umsetzt, faellt nur
so auf.

  1. Zahl und Groesse des Archivs
  2. Nicht doppelt gepackt: plugin.cfg an der Wurzel, kein Plugin-Ordner
     im Plugin-Ordner
  3. Gegenprobe des Packwerkzeugs: jede Datei byteweise gegen den
     Arbeitsordner, in BEIDE Richtungen auf Vollstaendigkeit
  4. Zeilenenden je Datei gegen die zuletzt veroeffentlichte Fassung.
     Keine Regel nach Dateiendung - Binaerdateien werden am Null-Byte
     erkannt, nicht an der Endung.
  5. Personenbezogenes und Zugangsmarken
  6. Keine routbare fremde Beispieladresse im ausgelieferten Code
     (RFC 5737 und die privaten Bereiche sind unbedenklich)

ZWEI GRUPPEN, UND DAS IST ABSICHT
Punkt 5 kennt Treffer, die fast immer falsch waeren (Zugangsmarken, echte
Kennwoerter) und solche, die ein Mensch je Fassung EINMAL beurteilen muss -
eine E-Mail-Adresse kann die bewusste Autorenangabe sein oder ein
Versehen. Erstere sind BEFUNDE und lassen den Lauf scheitern; letztere
stehen unter ANZUSEHEN und gehoeren woertlich in die Freigabenotiz. Wer sie
nur wegdrueckt, hat keinen Beleg, dass jemand hingesehen hat.

EICHUNG
Das Werkzeug hat im ersten Anlauf 14 Treffer gemeldet, von denen 14 seine
eigenen Fehlalarme waren: eine Sprachzeile PASSWORT = "Passwort" ist keine
Passwortzuweisung, und PHP-Code, der ein Kennwort MASKIERT, erst recht
nicht. Dazu meldete es denselben Treffer viermal, weil es je Fundstelle den
ERSTEN Treffer der Datei ausgab. Beides ist berichtigt; die Gegenprobe
gegen eine absichtlich zerbrochene Kopie steht in
Pruefung-ACTiKamera-1.9.8/.

Aufruf:  python freigabepruefung.py <plugin-ordner> <neues.zip> [<altes.zip>]

Rueckgabewert: 0 = kein Befund, 1 = mindestens ein Befund,
2 = falsch aufgerufen (dann wurde NICHTS geprueft - eine Null ist kein
Ergebnis, sondern ein blinder Fleck).
"""
import hashlib
import os
import re
import sys
import zipfile

if len(sys.argv) < 3:
    sys.stderr.write(__doc__)
    sys.exit(2)

ORDNER = sys.argv[1]
NEU = sys.argv[2]
ALT = sys.argv[3] if len(sys.argv) > 3 else ''

if not os.path.isdir(ORDNER) or not os.path.isfile(NEU):
    sys.stderr.write('ABBRUCH: Ordner oder Archiv nicht gefunden.\n')
    sys.exit(2)

befunde = []
ansehen = []
angesehen = {'dateien': 0, 'zeilenenden': 0, 'personen': 0}


def melde(punkt, text):
    befunde.append('%s: %s' % (punkt, text))


def anzusehen(punkt, text):
    ansehen.append('%s: %s' % (punkt, text))


def art(b):
    """Zeilenendenart. Binaer wird am NULL-Byte erkannt, nicht an der Endung -
    PNG-Symbole enthalten CR-Bytes als Bilddaten."""
    if b'\x00' in b:
        return 'BINAER'
    crlf = b.count(b'\r\n')
    lf = b.count(b'\n') - crlf
    if crlf and lf:
        return 'GEMISCHT'
    return 'CRLF' if crlf else ('LF' if lf else '-')


def inhalt(pfad):
    z = zipfile.ZipFile(pfad)
    aus = {}
    for i in z.namelist():
        if not i.endswith('/'):
            aus[i] = z.read(i)
    oberste = set(k.split('/')[0] for k in aus if '/' in k)
    if len(oberste) == 1 and all('/' in k for k in aus):
        aus = dict((k.split('/', 1)[1], v) for k, v in aus.items())
    return aus


neu = inhalt(NEU)
groesse = os.path.getsize(NEU)

print('=' * 72)
print('Freigabepruefung  %s' % os.path.basename(NEU))
print('=' * 72)

# --- 1. Zahl und Groesse -------------------------------------------------
print('\n1. Umfang')
print('   %d Dateien, %d Byte' % (len(neu), groesse))

# --- 2. Nicht doppelt gepackt -------------------------------------------
print('\n2. Nicht doppelt gepackt')
print('   plugin.cfg an der Wurzel: %s' % ('ja' if 'plugin.cfg' in neu else 'NEIN'))
if 'plugin.cfg' not in neu:
    melde('2', 'plugin.cfg liegt NICHT an der Wurzel des Archivs')
tiefer = [k for k in neu if k.endswith('plugin.cfg') and k != 'plugin.cfg']
print('   weitere plugin.cfg im Baum: %d' % len(tiefer))
for k in tiefer:
    melde('2', 'zweite plugin.cfg im Baum: %s' % k)
print('   Ordner an der Wurzel: %s'
      % ', '.join(sorted(set(k.split('/')[0] for k in neu if '/' in k))))

# --- 3. Gegenprobe des Packwerkzeugs ------------------------------------
print('\n3. Gegenprobe: Archiv gegen Arbeitsordner, byteweise')
imordner = {}
for wurzel, verz, dateien in os.walk(ORDNER):
    verz[:] = [v for v in verz if v not in ('.git', '__pycache__')]
    for d in dateien:
        p = os.path.join(wurzel, d)
        imordner[os.path.relpath(p, ORDNER).replace(os.sep, '/')] = open(p, 'rb').read()

nur_archiv = sorted(set(neu) - set(imordner))
nur_ordner = sorted(set(imordner) - set(neu))
beide = sorted(set(neu) & set(imordner))
anders = [k for k in beide
          if hashlib.sha256(neu[k]).digest() != hashlib.sha256(imordner[k]).digest()]
angesehen['dateien'] = len(beide)
print('   %d Dateien verglichen, %d nur im Archiv, %d nur im Ordner, %d verschieden'
      % (len(beide), len(nur_archiv), len(nur_ordner), len(anders)))
for k in nur_archiv:
    melde('3', 'nur im Archiv: %s' % k)
for k in nur_ordner:
    melde('3', 'nur im Ordner: %s' % k)
for k in anders:
    melde('3', 'inhaltlich verschieden: %s' % k)

# --- 4. Zeilenenden gegen die zuletzt veroeffentlichte Fassung ----------
print('\n4. Zeilenenden gegen die zuletzt veroeffentlichte Fassung')
gemischt = [k for k in neu if art(neu[k]) == 'GEMISCHT']
for k in gemischt:
    melde('4', 'gemischte Zeilenenden: %s' % k)
if not ALT or not os.path.isfile(ALT):
    print('   kein Vorgaengerarchiv angegeben - diese Zeile ist KEIN Nachweis.')
    print('   (auf gemischte Zeilenenden wurde trotzdem geprueft: %d)' % len(gemischt))
else:
    alt = inhalt(ALT)
    wechsel = 0
    for k in sorted(set(neu) & set(alt)):
        a, n = art(alt[k]), art(neu[k])
        angesehen['zeilenenden'] += 1
        if a != n:
            wechsel += 1
            melde('4', 'Stilwechsel %s: %s -> %s' % (k, a, n))
    print('   %d Dateien gegen die Vorfassung gehalten, %d Stilwechsel, %d gemischt'
          % (angesehen['zeilenenden'], wechsel, len(gemischt)))
    dazu = sorted(set(neu) - set(alt))
    if dazu:
        print('   neu in dieser Fassung (ohne Vergleichsstand): %s' % ', '.join(dazu))

# --- 5. Personenbezogenes und Zugangsmarken -----------------------------
print('\n5. Personenbezogenes und Zugangsmarken')

# Ein Wert, der nur eine Beschriftung ist ("PASSWORT = Passwort"), ist kein
# Kennwort. Und PHP-Code, der ein Kennwort MASKIERT, erst recht nicht.
WORTE = (b'passwort', b'password', b'passwd', b'pass', b'pwd', b'kennwort',
         b'kamerapasswort', b'benutzerpasswort')
CODE = (b'$', b'. ', b' .', b'(', b')', b'::', b'->')


def ist_beschriftung(wert):
    return wert.strip().lower() in WORTE


def ist_code(wert):
    return any(z in wert for z in CODE)


def sieht_aus_wie_kennwort(wert):
    """Traegt der Wert die Merkmale eines Kennworts?

    Ein Kennwort hat kein Leerzeichen, ist mindestens acht Zeichen lang und
    enthaelt Ziffern UND Buchstaben. Deutscher Fliesstext ueber Passwoerter
    faellt damit heraus, ohne dass eine Positivliste gepflegt werden muss.

    GRENZE, ausdruecklich: ein reines Buchstabenkennwort ('geheim') findet
    diese Zeile NICHT. Dafuer sind die Muster fuer Zugangsmarken da, und der
    haeufigste Fall - ein zum Ausprobieren hart eingetragenes Kennwort -
    traegt fast immer eine Zahl.
    """
    w = wert.strip()
    if len(w) < 8 or b' ' in w:
        return False
    hat_ziffer = any(48 <= z <= 57 for z in bytearray(w))
    hat_buchstabe = any(65 <= z <= 90 or 97 <= z <= 122 for z in bytearray(w))
    return hat_ziffer and hat_buchstabe


BEFUND_MUSTER = (
    ('MAC', re.compile(rb'\b([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b'), None),
    ('GitHub-Marke', re.compile(rb'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}'), None),
    ('Bearer', re.compile(rb'Bearer\s+[A-Za-z0-9._-]{20,}'), None),
    # Die Wortgrenze am Anfang ist Pflicht: ohne sie traf das Muster mitten
    # in einem Schluessel wie DAS_KAMERA_PASS und meldete den Fliesstext
    # dahinter als Kennwort.
    ('Kennwort', re.compile(
        rb'(?i)(?<![A-Za-z0-9_])\$?(?:pass|pwd|passwort|password|kennwort)[a-z_]*'
        rb'\s*(?:=>|=|:)\s*["\']([^"\']{4,})["\']'), 1),
)
ANSEHEN_MUSTER = (
    ('E-Mail', re.compile(rb'[\w.+-]+@[\w-]+\.[\w.]{2,}'), None),
)

for k in sorted(neu):
    if art(neu[k]) == 'BINAER':
        continue
    angesehen['personen'] += 1
    for name, m, gruppe in BEFUND_MUSTER:
        # finditer, nicht findall + search: sonst steht bei jedem Treffer der
        # ERSTE der Datei, und derselbe Fund wird mehrfach gemeldet.
        gesehen = set()
        for tr in m.finditer(neu[k]):
            ganz = tr.group(0)
            if name == 'Kennwort':
                wert = tr.group(gruppe)
                if (ist_beschriftung(wert) or ist_code(wert)
                        or not sieht_aus_wie_kennwort(wert)):
                    continue
            if ganz in gesehen:
                continue
            gesehen.add(ganz)
            melde('5', '%s in %s: %s' % (name, k, ganz.decode('utf-8', 'replace')[:70]))
    for name, m, _ in ANSEHEN_MUSTER:
        gesehen = set()
        for tr in m.finditer(neu[k]):
            ganz = tr.group(0)
            if ganz in gesehen:
                continue
            gesehen.add(ganz)
            anzusehen('5', '%s in %s: %s' % (name, k, ganz.decode('utf-8', 'replace')))
print('   %d Textdateien durchsucht' % angesehen['personen'])

# --- 6. Keine routbare fremde Beispieladresse ---------------------------
print('\n6. Beispieladressen')
IP = re.compile(rb'\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b')


def unbedenklich(a, b, c, d):
    if a == 10 or a == 127 or (a == 192 and b == 168) or (a == 172 and 16 <= b <= 31):
        return True                      # private Bereiche
    if a == 192 and b == 0 and c == 2:
        return True                      # RFC 5737
    if a == 198 and b == 51 and c == 100:
        return True
    if a == 203 and b == 0 and c == 113:
        return True
    if a == 0 or a >= 224:
        return True
    return False


fremde = 0
for k in sorted(neu):
    if art(neu[k]) == 'BINAER':
        continue
    for t in IP.finditer(neu[k]):
        z = tuple(int(x) for x in t.groups())
        if max(z) > 255:
            continue                     # keine IP, etwa eine Fassungsnummer
        if not unbedenklich(*z):
            fremde += 1
            melde('6', 'routbare fremde Adresse in %s: %s'
                  % (k, '.'.join(str(x) for x in z)))
print('   %d routbare fremde Adressen' % fremde)

# --- Ergebnis ------------------------------------------------------------
print('\n' + '=' * 72)
if ansehen:
    print('ANZUSEHEN (%d) - gehoert beurteilt und woertlich in die Freigabenotiz:'
          % len(ansehen))
    for a in ansehen:
        print('  ? ' + a)
    print('')
if befunde:
    print('%d BEFUNDE:' % len(befunde))
    for b in befunde:
        print('  - ' + b)
    sys.exit(1)
print('Kein Befund. %d Dateien byteweise verglichen, %d gegen die Vorfassung auf '
      'Zeilenenden, %d auf Personenbezogenes durchsucht.'
      % (angesehen['dateien'], angesehen['zeilenenden'], angesehen['personen']))
sys.exit(0)
