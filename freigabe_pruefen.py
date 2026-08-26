#!/usr/bin/env python3
"""Alles, was vor einer Veroeffentlichung zu pruefen ist - in einem Aufruf.

Der Anlass: die Punkte aus REGELN_4 „Vor jeder Veroeffentlichung" standen
als Liste da. Eine Liste wird abgehakt; eine Pruefung laeuft. Am 19.08.2026
sind an einem Tag vier Dinge durchgerutscht, die auf dieser Liste stehen
oder haetten stehen muessen:

  - dieselbe Fassungsnummer fuer zwei verschiedene Staende
  - release.cfg zweimal eine Fassung zurueck
  - 14 Werte je Sprachdatei mit geraden Anfuehrungszeichen (englische
    Oberflaeche waere textlos gewesen)
  - eine Prueflinie, die ihre Zahl aus dem eigenen Quelltext druckte

Aufruf:
    python3 freigabe_pruefen.py PLUGINORDNER
        [--archiv X.zip]        zusaetzlich das gepackte Archiv pruefen
        [--grundlinie Y.zip]    Zeilenenden gegen die VEROEFFENTLICHTE Fassung
        [--ohne-netz]           GitHub-Abfragen ueberspringen

Rueckgabe 0 nur, wenn ALLES bestanden ist.
"""
import os
import re
import subprocess
import sys
import zipfile

argv = sys.argv[1:]


def wert(name, vorgabe=None):
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return argv[i + 1]
    return vorgabe


ORDNER = next((a for a in argv if not a.startswith('--')
               and a not in (wert('--archiv'), wert('--grundlinie'))), '.')
ARCHIV = wert('--archiv')
GRUND = wert('--grundlinie')
OHNE_NETZ = '--ohne-netz' in argv
HIER = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable or 'python3'

ergebnis = []


def melde(name, ok, text=''):
    """ok = True Haken, False Kreuz, None Strich ("nicht feststellbar").

    Der Strich zaehlt nicht als Beanstandung - aber er zaehlt auch nicht als
    bestanden. Er steht dort, wo in DIESER Umgebung nichts zu messen war;
    wer ihn beim Ueberfliegen wie einen Haken einsammelt, hat eine Pruefung
    weniger, als er glaubt. Deshalb steht am Ende, wie viele es waren.
    """
    ergebnis.append((name, ok))
    marke = ' -- ' if ok is None else ('ok ' if ok else 'FEHL')
    print('  [%s] %-26s %s' % (marke, name, text))


def stil(b):
    crlf = b.count(b'\r\n')
    lf = b.count(b'\n') - crlf
    if b.count(b'\r') - crlf:
        return 'einzelne CR'
    if crlf and lf:
        return 'gemischt'
    return 'CRLF' if crlf else ('LF' if lf else 'ohne')


print('== Freigabepruefung: %s ==\n' % os.path.abspath(ORDNER))

# ---------- 1. PHP-Syntax ----------
phps = [os.path.join(w, d) for w, _, ds in os.walk(ORDNER) for d in sorted(ds)
        if d.endswith('.php')]
schlecht = []
for p in phps:
    r = subprocess.run(['php', '-l', p], capture_output=True, text=True)
    if r.returncode != 0:
        schlecht.append(os.path.basename(p))
melde('PHP-Syntax', not schlecht,
      '%d Dateien%s' % (len(phps), '' if not schlecht else ', FEHLER in ' + ', '.join(schlecht)))

# ---------- 2. Selbsttest ----------
#
# ZWEI Ausgabeformen, und beide sind richtig. Bis zum 25.08.2026 kannte diese
# Pruefung nur die erste und meldete fuer jedes Plugin mit der zweiten
# "keine auswertbare Ausgabe" - ein rotes Kreuz ohne Befund, und genau die
# Klasse, vor der REGELN_4 warnt: beim dritten Mal sieht niemand mehr hin.
#
#   a) Rechenkern-Form   "N Faelle geprueft, M Fehlschlaege."
#                        Ein Selbsttest ueber Testfaelle (BatterieBMS).
#   b) Marken-Form       Zeilen mit [OK] / [FEHL] / [INFO]
#                        Eine Einrichtungspruefung (Zendure SolarFlow).
#                        Gezaehlt werden die [FEHL]-Zeilen, dazu der
#                        Rueckgabewert - eine Ausgabe ohne [FEHL], deren
#                        Prozess trotzdem 1 liefert, ist ein Befund.
#
# Kommt weder das eine noch das andere, bleibt es bei der Beanstandung: ein
# Dienst, der auf --selbsttest gar nichts sagt, ist einer.
dienst = [p for p in phps if p.endswith('_dienst.php') and os.sep + 'bin' + os.sep in p]
if dienst:
    r = subprocess.run(['php', dienst[0], '--selbsttest'], capture_output=True, text=True)
    m = re.search(r'(\d+) Faelle geprueft, (\d+) Fehlschl', r.stdout)
    marken = re.findall(r'^\[(OK|FEHL|INFO)\]', r.stdout, re.M)
    # Laeuft hier ueberhaupt ein LoxBerry? Die Marken-Form misst die
    # EINRICHTUNG, nicht den Quelltext - ohne LBHOMEDIR und ohne
    # config/plugins/<name> meldet sie zwangslaeufig Fehler, und keiner
    # davon ist einer. Gemessen wird das an der Umgebung, nicht geraten.
    lbhome = os.environ.get('LBHOMEDIR', '')
    lb_da = bool(lbhome) and os.path.isdir(os.path.join(lbhome, 'config', 'system'))
    if m:
        melde('Selbsttest', m.group(2) == '0', '%s Faelle, %s Fehlschlaege' % m.groups())
    elif marken and not lb_da:
        fehl = marken.count('FEHL')
        melde('Selbsttest', None,
              '%d Zeilen, %d [FEHL] - ohne LoxBerry-Umgebung nicht aussagekraeftig'
              % (len(marken), fehl))
    elif marken:
        fehl = marken.count('FEHL')
        melde('Selbsttest', fehl == 0 and r.returncode == 0,
              '%d Zeilen, %d [FEHL], Rueckgabe %d' % (len(marken), fehl, r.returncode))
    else:
        melde('Selbsttest', False, 'keine auswertbare Ausgabe')
else:
    melde('Selbsttest', True, 'kein bin/*_dienst.php - entfaellt')

# ---------- 3. Sprachdateien ----------
r = subprocess.run([PY, os.path.join(HIER, 'ini_pruefen.py'), ORDNER],
                   capture_output=True, text=True)
letzte = [z for z in r.stdout.strip().splitlines() if z.strip()][-1] if r.stdout.strip() else '?'
melde('Sprachdateien', r.returncode == 0, letzte[:70])

# ---------- 4. Oberflaechen-Hausstandard ----------
hs = os.path.join(HIER, 'hausstandard_pruefen.py')
if os.path.isfile(hs):
    r = subprocess.run([PY, hs, ORDNER], capture_output=True, text=True)
    zeile = [z for z in r.stdout.splitlines() if ORDNER.split(os.sep)[-1][:20] in z]
    kl = re.findall(r'\b([a-z]{2,6})\b', zeile[0].split(None, 1)[1]) if zeile else []
    melde('Hausstandard', r.returncode == 0 and not kl,
          'offene Spalten: %s' % (', '.join(kl) if kl else 'keine'))
else:
    melde('Hausstandard', True, 'hausstandard_pruefen.py fehlt - entfaellt')

# ---------- 4b. Suchtexte fuer Loxone ----------
#
# Der Fehler, der diesen Abschnitt ausgeloest hat: der Suchtext \iKM=\i\v traf
# in der Antwortzeile zuerst INSPKM= - der Kilometerstand las die
# Inspektionsvorgabe. Gefunden in DREI Linien dieser Familie; dreimal derselbe
# Fehler heisst, dass keine Pruefung ihn kannte.
#
# Beanstandet wird nur, was HEUTE falsch trifft. Ein Suchtext ohne
# Trennzeichen, der mit der jetzigen Feldliste eindeutig ist, steht im
# Einzelbericht des Werkzeugs als Hinweis - hier nicht: eine
# Freigabepruefung, die bei der Haelfte des Bestands rot wird, wird
# abgeschaltet.
sm = os.path.join(HIER, 'suchmuster_pruefen.py')
if os.path.isfile(sm):
    r = subprocess.run([PY, sm, ORDNER], capture_output=True, text=True)
    schlimm = [z.strip() for z in r.stdout.splitlines() if 'trifft zuerst' in z]
    if schlimm:
        melde('Loxone-Suchtexte', False, schlimm[0][:70])
    else:
        kopf = [z for z in r.stdout.splitlines() if ORDNER.split(os.sep)[-1][:20] in z]
        melde('Loxone-Suchtexte', True,
              (kopf[0].split(None, 1)[1].strip()[:70]) if kopf else 'nichts zu messen')
else:
    melde('Loxone-Suchtexte', True, 'suchmuster_pruefen.py fehlt - entfaellt')

# ---------- 4c. Die LoxBerry-Attrappe ----------
#
# Sie ist eine handgeschriebene Nachbildung und altert gegen das Original.
# Am 25.08.2026 fehlte ihr notify_ext(), das acht Plugins rufen - drei von
# vier Staenden waren ausserdem veraltet. Ohne Netz nicht messbar; dann ein
# Strich, kein Haken.
ap = os.path.join(HIER, 'attrappe_pruefen.py')
if os.path.isfile(ap) and not OHNE_NETZ:
    r = subprocess.run([PY, ap], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    m = re.search(r'== (\d+) Befund', r.stdout)
    if 'nicht gemessen' in r.stdout or m is None:
        melde('LoxBerry-Attrappe', None, 'nicht abrufbar - nicht gemessen')
    else:
        melde('LoxBerry-Attrappe', m.group(1) == '0', '%s Befund(e)' % m.group(1))
elif os.path.isfile(ap):
    melde('LoxBerry-Attrappe', None, 'uebersprungen (--ohne-netz)')
else:
    melde('LoxBerry-Attrappe', True, 'attrappe_pruefen.py fehlt - entfaellt')

# ---------- 5. Fassungslage ----------
if OHNE_NETZ:
    melde('Fassungslage', True, 'uebersprungen (--ohne-netz)')
else:
    r = subprocess.run([PY, os.path.join(HIER, 'fassungslage.py'), ORDNER],
                       capture_output=True, text=True)
    schlimm = 'DIESELBE NUMMER' in r.stdout or 'BIETET diese Nummer AN' in r.stdout
    m = re.search(r'plugin\.cfg\s+VERSION=(\S+)', r.stdout)
    melde('Fassungslage', not schlimm, 'Ordner %s%s'
          % (m.group(1) if m else '?', ', ABWEICHUNG' if schlimm else ', stimmig'))

# ---------- 6. Personenbezogenes ----------
muster = [('E-Mail', rb'[\w.+-]+@[\w-]+\.[\w.]{2,}'),
          ('MAC', rb'(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}'),
          ('Zugangsmarke', rb'(?i)(ghp_|github_pat_|Bearer\s+[A-Za-z0-9._-]{20,})'),
          ('Passwort', rb'(?i)passwor[dt]\s*[=:]\s*["\'][^"\']{3,}'),
          # 224.-239. ist Multicast: keine Gegenstelle, sondern eine Gruppe, an
          # die gesendet wird (SSDP 239.255.255.250 etwa gehoert zum Govee-
          # Protokoll und steht in dessen Anleitung). 169.254. ist link-local.
          # Beides sind keine 'fremden IP', und beides fehlte bis 20.08.2026.
          ('fremde IP', rb'\b(?!10\.|127\.|192\.168\.|192\.0\.2\.|198\.51\.100\.|203\.0\.113\.'
                        rb'|172\.(?:1[6-9]|2\d|3[01])\.|0\.|255\.|169\.254\.'
                        rb'|22[4-9]\.|23\d\.)(?:\d{1,3}\.){3}\d{1,3}\b')]
# example.com, .net und .org sind durch RFC 2606 GENAU dafuer reserviert,
# als Beispiel zu dienen; sie sind an niemanden zugeteilt. Ein
# Platzhaltertext im Eingabefeld ist damit kein Personenbezug. Der Fund
# lag in zwei Plugins hinter dem Passwort-Fehlalarm verborgen, weil die
# Meldung nur den ERSTEN Fund zeigt - ein Waechter, der einen Fund pro Lauf
# nennt, verdeckt mit einem Fehlalarm alles dahinter. Deshalb nennt die
# Meldung jetzt auch die Gesamtzahl.
erlaubt = {b'noreply@github.com'}
BEISPIELDOMAENE = (b'@example.com', b'@example.net', b'@example.org')

# Der Fehlalarm vom 20.08.2026, gemessen in ALLEN VIER Auto-Plugins: in den
# Sprachdateien steht L_PASSWORT = "Passwort des Kontos". Das ist eine
# Beschriftung und kein Geheimnis. Ein Waechter, dessen Meldung bei jedem
# Lauf dieselbe ist, wird nicht mehr gelesen - und dann uebersieht man
# daneben den echten Fund. Ausgenommen wird deshalb GENAU dieser Fall und
# kein anderer:
#
#   * die Datei liegt unter templates/lang/
#   * dem Wort geht ein Schluessel der Hausform <1-3 GROSSBUCHSTABEN>_
#     voraus
#
# Ein echter Zugangsschluessel heisst 'password', 'passwort' oder
# 'db_password' - klein geschrieben - und bleibt damit sichtbar. Wer ein
# Geheimnis durch diese Ausnahme schmuggeln wollte, muesste es unter
# L_PASSWORT in eine Sprachdatei schreiben, wo es auf dem Bildschirm steht.
#
# Und was ausgenommen wurde, wird GEZAEHLT und gemeldet. Eine stille
# Ausnahme waere dasselbe Uebel wie der Fehlalarm, nur in der anderen
# Richtung.
# Die Vorsaetze stehen EINZELN da und nicht als [A-Z]{1,3}_. Der Grund ist
# gemessen: die Eichung (Werkzeuge/freigabe_eichung.py) legte
# DB_PASSWORD = "geheim123" in eine Sprachdatei, und die weite Form nahm
# es aus - ein echter Zugangsschluessel waere durchgefallen. Es sind die
# Rollenvorsaetze der Hausschluessel, und es sind genau die vier, die in
# den Sprachdateien des Bestands vor PASSWORT stehen (gemessen am
# 20.08.2026 in vier Auto-Plugins): Label, Hilfe, Frage, Antwort.
BESCHRIFTUNG = re.compile(rb'(?:^|[^A-Za-z0-9_])(?:L|H|F|A|K|M|T)_$')

# Ein Platzhalter, erkannt am WERT und nicht am Namen. Siehe den Befund in
# MG iSmart: drei Fehlalarme auf ein Docker-Beispiel, das dem Anwender
# angezeigt wird. Die Namen dort heissen E_MQTT_USER_E_MQTT_PASSWORD und
# SAIC_PASSWORD - am Namen ist das nicht zu entscheiden.
#
# GESCHRIEN heisst hier: nur Grossbuchstaben, Ziffern, Strich und
# Unterstrich. Das allein waere zu weit - HUNTER2 ist ein Passwort -, also
# muss der Wert sich zusaetzlich selbst als Platzhalter benennen. Beides
# case-sensitiv gross: sonst waere jeder Wert ausgenommen, der irgendwo
# das Wort "Passwort" traegt, und 'MeinPasswortIst123' fiele durch.
PLATZHALTER_WORT = (b'IHR', b'DEIN', b'YOUR', b'MEIN', b'XXX', b'BEISPIEL',
                    b'EXAMPLE', b'CHANGEME', b'DUMMY', b'HIER')
GESCHRIEN = re.compile(rb'[A-Z0-9_-]{3,64}$')


def ist_platzhalter(treffer):
    """treffer ist die ganze Fundstelle - der Wert beginnt am ersten
    Anfuehrungszeichen darin."""
    i = min((treffer.find(z) for z in (b'"', b"'") if treffer.find(z) >= 0),
            default=-1)
    if i < 0:
        return False
    wert = treffer[i + 1:].strip()
    if wert == b'':
        return False
    if '\u2026'.encode('utf-8') in wert or b'...' in wert:
        return True
    return bool(GESCHRIEN.match(wert)) and any(w in wert for w in PLATZHALTER_WORT)

funde = []
beschriftungen = 0
beispiele = 0
platzhalter = 0
for w, _, ds in os.walk(ORDNER):
    for d in sorted(ds):
        p = os.path.join(w, d)
        rp = os.path.relpath(p, ORDNER).replace(os.sep, '/')
        b = open(p, 'rb').read()
        if b'\x00' in b:
            continue
        for name, mu in muster:
            gesehen = set()
            for m in re.finditer(mu, b):
                tr = m.group(1) if m.groups() else m.group(0)
                if tr in gesehen:
                    continue
                gesehen.add(tr)
                if b'noreply' in tr or tr in erlaubt:
                    continue
                if name == 'E-Mail' and tr.lower().endswith(BEISPIELDOMAENE):
                    beispiele += 1
                    continue
                if name == 'Passwort' and ist_platzhalter(tr):
                    platzhalter += 1
                    continue
                if (name == 'Passwort' and rp.startswith('templates/lang/')
                        and BESCHRIFTUNG.search(b[max(0, m.start() - 6):m.start()])):
                    beschriftungen += 1
                    continue
                funde.append('%s in %s: %s' % (name, d, tr.decode('utf-8', 'replace')[:34]))
ausnahmen = []
if beschriftungen:
    ausnahmen.append('%d Beschriftung(en) *_PASSWORT in Sprachdateien'
                     % beschriftungen)
if beispiele:
    ausnahmen.append('%d Beispieladresse(n) nach RFC 2606' % beispiele)
if platzhalter:
    ausnahmen.append('%d Platzhalter (Auslassungspunkte oder geschrieben)'
                     % platzhalter)
nachsatz = (' - ausgenommen: ' + ', '.join(ausnahmen)) if ausnahmen else ''
melde('Personenbezogenes', not funde,
      ('%d Fund(e), der erste: %s' % (len(funde), funde[0]) if funde
       else 'nichts gefunden') + nachsatz)

# ---------- 7. Zeilenenden gegen die Grundlinie ----------
if GRUND and os.path.isfile(GRUND):
    z = zipfile.ZipFile(GRUND)
    basis = {}
    for n in z.namelist():
        if not n.endswith('/'):
            basis[n.split('/', 1)[1] if '/' in n else n] = z.read(n)
    z.close()
    abw = []
    for w, _, ds in os.walk(ORDNER):
        for d in sorted(ds):
            p = os.path.join(w, d)
            rp = os.path.relpath(p, ORDNER).replace(os.sep, '/')
            b = open(p, 'rb').read()
            if b'\x00' in b or rp not in basis:
                continue
            if stil(b) != stil(basis[rp]):
                abw.append(rp)
    melde('Zeilenenden', not abw, 'gegen %s%s'
          % (os.path.basename(GRUND), '' if not abw else ' - ABWEICHUNG ' + ', '.join(abw)))
else:
    melde('Zeilenenden', True, 'keine Grundlinie angegeben - entfaellt')

# ---------- 8. Das Archiv ----------
if ARCHIV and os.path.isfile(ARCHIV):
    z = zipfile.ZipFile(ARCHIV)
    n = z.namelist()
    dateien = [x for x in n if not x.endswith('/')]
    anders = [x for x in dateien
              if not os.path.isfile(os.path.join(ORDNER, x.replace('/', os.sep)))
              or open(os.path.join(ORDNER, x.replace('/', os.sep)), 'rb').read() != z.read(x)]
    tiefer = [x for x in dateien if x.count('/') and x.endswith('plugin.cfg')]
    wurzel = 'plugin.cfg' in dateien
    z.close()
    ok = not anders and not tiefer and wurzel
    melde('Archiv', ok, '%d Eintraege, %d Byte%s'
          % (len(n), os.path.getsize(ARCHIV),
             '' if ok else ' - ' + (('abweichend: ' + ', '.join(anders[:3])) if anders
                                    else ('doppelt gepackt' if tiefer else 'plugin.cfg fehlt an der Wurzel'))))
else:
    melde('Archiv', True, 'kein Archiv angegeben - entfaellt')

# ---------- Urteil ----------
#
# Ein Strich ist KEINE Beanstandung - aber er wird auch nicht verschwiegen.
# "Alles bestanden" darf nur dastehen, wenn wirklich alles gemessen wurde;
# sonst liest sich ein nicht durchgefuehrter Test wie ein bestandener.
schlecht = [n for n, ok in ergebnis if ok is False]
strich = [n for n, ok in ergebnis if ok is None]
print('\n== %d Pruefungen, %d Beanstandungen%s =='
      % (len(ergebnis), len(schlecht),
         '' if not strich else (', %d nicht feststellbar' % len(strich))))
if strich:
    print('   nicht gemessen: %s' % ', '.join(strich))
if schlecht:
    print('   offen: %s' % ', '.join(schlecht))
    sys.exit(1)
print('   Alles bestanden%s.' % ('' if not strich else ', was messbar war'))
