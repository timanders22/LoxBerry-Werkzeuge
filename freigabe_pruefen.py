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
        [--crlf-erlaubt D[,D]]  Dateien, die CRLF tragen DUERFEN - namentlich.
                                Fuer eine Linie, die noch nicht umgestellt ist.
        [--zeilenenden-neu D[,D]]  Dateien, deren Zeilenendstil sich gegenueber
                                der Grundlinie AENDERN darf - namentlich, mit
                                dem Pfad wie im Archiv. Wortgleich mit dem
                                Schalter von packen.py; wer dort eine Ausnahme
                                setzt, setzt sie hier auch. Alles Uebrige
                                bleibt geschuetzt, und die Ausnahme steht im
                                Bericht.
        [--ohne-netz]           GitHub-Abfragen ueberspringen

Rueckgabe 0 nur, wenn ALLES bestanden ist.
"""
import io
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


# Eine unbekannte Option galt bis 18.09.2026 als PFAD: aus
# "freigabe_pruefen.py --hilfe" wurde der Pruefling "." - das Werkzeug mass
# dann den GANZEN Arbeitsordner (3168 PHP-Dateien, 8 Beanstandungen ueber
# fremde Linien) und sah aus wie ein Befund an der gemeinten Linie. An einem
# Tag dreimal passiert. Eine unbekannte Option und ein fehlender Ordner
# brechen deshalb ab, statt etwas anderes zu messen (Rueckgabe 2 = nichts
# gemessen, nicht 1 = Befund).
BEKANNTE_OPTIONEN = ('--archiv', '--grundlinie', '--zeilenenden-neu',
                     '--crlf-erlaubt', '--ohne-netz')
_unbekannt = [a for a in argv
              if a.startswith('--') and a.split('=', 1)[0] not in BEKANNTE_OPTIONEN]
if _unbekannt:
    print('ABBRUCH: unbekannte Option %s' % ', '.join(_unbekannt))
    print('Aufruf: freigabe_pruefen.py PLUGINORDNER [--archiv DATEI.zip] '
          '[--grundlinie DATEI.zip] [--zeilenenden-neu LISTE] '
          '[--crlf-erlaubt LISTE] [--ohne-netz]')
    sys.exit(2)

ORDNER = next((a for a in argv if not a.startswith('--')
               and a not in (wert('--archiv'), wert('--grundlinie'),
                             wert('--zeilenenden-neu'),
                             wert('--crlf-erlaubt'))), None)
if ORDNER is None:
    print('ABBRUCH: kein Pluginordner genannt.')
    print('Aufruf: freigabe_pruefen.py PLUGINORDNER [--archiv DATEI.zip] '
          '[--grundlinie DATEI.zip] [--zeilenenden-neu LISTE] '
          '[--crlf-erlaubt LISTE] [--ohne-netz]')
    sys.exit(2)
# Der Name des Pruefling-Ordners, unabhaengig von der Pfadform.
# os.path.basename() kennt unter Windows Rueckstrich UND Schraegstrich;
# ORDNER.split(os.sep) kannte nur den Rueckstrich und lieferte bei einem
# Pfad mit Schraegstrichen den ganzen Pfad zurueck.
ORDNERNAME = os.path.basename(os.path.normpath(ORDNER.replace('\\', os.sep)))
ARCHIV = wert('--archiv')
GRUND = wert('--grundlinie')
ZE_NEU = wert('--zeilenenden-neu')
CRLF_OK = wert('--crlf-erlaubt')
ERLAUBT_STIL = set(t.strip().replace('\\', '/')
                   for t in (ZE_NEU or '').split(',') if t.strip())
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


# ---------- Zugelassene Ausnahmen (seit 31.10.2026) ----------
#
# Entscheidung des Hausherrn am 31.10.2026: "Veroeffentliche Zigbee2MqttNG
# 4.2.6 (Vorschlag 1)". Zigbee2MqttNG traegt seit 4.2.5 drei Beanstandungen
# aus FREMDEM Zubehoer (Twig im Ordner vendor_twig und der Twig-Cache, den
# das Tor beim Rendern selbst anlegt). 4.2.5 lief deshalb ueber eine
# einmalige Variante von linie_abschluss.sh, die das Tor-Urteil am Ende
# umdeutete - das ist eine Umgehung, keine Pruefung.
#
# Jetzt steht jede Ausnahme in Werkzeuge/freigabetor_ausnahmen.json, und sie
# ist so ENG wie moeglich: sie gilt nur fuer EIN Plugin (Repo aus
# RELEASECFG UND NAME/FOLDER in plugin.cfg), nur fuer EINE Pruefung, nur fuer
# einen genauen Pfad (oder ein genaues Muster) und nur fuer den genannten
# Befund (PHP-Fassung, Anschrift, Wort) - wo der Inhalt fest ist, zusaetzlich
# nur fuer genau diesen Dateiinhalt (sha256). Jeder andere Befund in derselben
# Zeile bleibt eine Beanstandung. Eine zugelassene Ausnahme ist LAUT: die
# Zeile sagt "zugelassen (Ausnahme ...)", und das Urteil zaehlt sie.
# Fehlt die Datei oder ist sie kaputt, gilt KEINE Ausnahme - das Tor wird
# dann strenger, nie lockerer.
AUSNAHMEN_DATEI = os.path.join(HIER, 'freigabetor_ausnahmen.json')
AUSNAHME_PFLICHT = ('id', 'repo', 'plugin_name', 'pruefung', 'befund',
                    'begruendung', 'datum', 'entscheidung')


def _plugin_kennung(wurzel):
    """(repo, NAME, FOLDER) aus plugin.cfg - oder Leeres, dann gilt nichts."""
    try:
        t = io.open(os.path.join(wurzel, 'plugin.cfg'), encoding='utf-8',
                    errors='replace').read()
    except OSError:
        return ('', '', '')
    abschnitt, werte = '', {}
    for z in t.splitlines():
        z = z.strip()
        if z.startswith('[') and z.endswith(']'):
            abschnitt = z[1:-1].strip().upper()
        elif '=' in z and not z.startswith('#'):
            k, v = z.split('=', 1)
            werte[(abschnitt, k.strip().upper())] = v.strip()
    m = re.match(r'https://raw\.githubusercontent\.com/([^/]+/[^/]+)/',
                 werte.get(('AUTOUPDATE', 'RELEASECFG'), ''))
    return (m.group(1) if m else '', werte.get(('PLUGIN', 'NAME'), ''),
            werte.get(('PLUGIN', 'FOLDER'), ''))


def _ausnahmen_laden():
    import json
    if not os.path.isfile(AUSNAHMEN_DATEI):
        return [], ''
    try:
        roh = json.load(io.open(AUSNAHMEN_DATEI, encoding='utf-8'))
        liste = roh['ausnahmen']
    except (ValueError, KeyError, TypeError) as e:
        return [], 'Ausnahmedatei unlesbar (%s) - es gilt KEINE Ausnahme' % e
    gut, schlecht = [], []
    for a in liste:
        if (isinstance(a, dict) and all(a.get(k) for k in AUSNAHME_PFLICHT)
                and [bool(a.get(k)) for k in ('pfad', 'pfad_muster', 'pfade')]
                .count(True) == 1
                and (not a.get('pfade') or (isinstance(a['pfade'], dict)
                                            and all(a['pfade'].values())))):
            gut.append(a)
        else:
            schlecht.append(str(a.get('id', '?') if isinstance(a, dict) else a))
    return gut, ('Ausnahme(n) %s unvollstaendig - gelten nicht'
                 % ', '.join(schlecht) if schlecht else '')


PLUGIN_KENNUNG = _plugin_kennung(ORDNER)
_alle_ausnahmen, AUSNAHMEN_HINWEIS = _ausnahmen_laden()
# Nur die Eintraege DIESES Plugins: Repo UND NAME UND FOLDER muessen passen.
AUSNAHMEN = [a for a in _alle_ausnahmen
             if PLUGIN_KENNUNG[0] and a['repo'] == PLUGIN_KENNUNG[0]
             and a['plugin_name'] == PLUGIN_KENNUNG[1] == PLUGIN_KENNUNG[2]]
AUSNAHMEN_BENUTZT = {}      # id -> Zahl der zugelassenen Fundstellen
_archiv_namen = None


def ausnahme_fuer(pruefung, rp, befund, zeile=None):
    """Die id der Ausnahme, die GENAU diesen Befund zulaesst - sonst None."""
    global _archiv_namen
    for a in AUSNAHMEN:
        if a['pruefung'] != pruefung or befund not in a['befund']:
            continue
        if a.get('pfad') and rp != a['pfad']:
            continue
        if a.get('pfad_muster') and not re.fullmatch(a['pfad_muster'], rp):
            continue
        # "pfade": {genauer Pfad: sha256} - mehrere Dateien, jede mit ihrem Inhalt.
        if a.get('pfade') and rp not in a['pfade']:
            continue
        if a.get('zeile_enthaelt') and (zeile is None
                                        or a['zeile_enthaelt'] not in zeile):
            continue
        soll = a['pfade'][rp] if a.get('pfade') else a.get('sha256')
        if soll:
            import hashlib
            try:
                h = hashlib.sha256(open(os.path.join(ORDNER, rp), 'rb')
                                   .read()).hexdigest()
            except OSError:
                continue
            if h != soll:
                continue
        if a.get('nur_ausserhalb_archiv'):
            # Nur zulaessig, wenn die Datei NICHT ausgeliefert wird - ohne
            # Archiv ist das nicht belegbar, dann gilt die Ausnahme nicht.
            if _archiv_namen is None:
                _archiv_namen = set()
                _a = wert('--archiv')
                if _a and os.path.isfile(_a):
                    with zipfile.ZipFile(_a) as _z:
                        _archiv_namen = set(_z.namelist()) | {'\0'}
            if '\0' not in _archiv_namen or rp in _archiv_namen:
                continue
        AUSNAHMEN_BENUTZT[a['id']] = AUSNAHMEN_BENUTZT.get(a['id'], 0) + 1
        return a['id']
    return None


def zugelassen_text(zugel):
    """zugel = [(befundtext, id)] -> Zusatz fuer die Pruefzeile."""
    if not zugel:
        return ''
    ids = sorted(set(i for _, i in zugel))
    return ' - zugelassen (Ausnahme %s: %s)' % (
        ', '.join(ids), ', '.join(t for t, _ in zugel[:4])
        + (' ...' if len(zugel) > 4 else ''))


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
#
# Gesucht wird nach INHALT, nicht nur nach Endung: ein Plugin darf
# ausfuehrbare Dateien ohne Endung mitliefern, und VolkswagenID tut es
# (bin/healthcheck, '#!/usr/bin/env php'). Bis zum 03.09.2026 zaehlte diese
# Zeile dort vier Dateien und meldete sie als geprueft; die fuenfte hat nie
# ein php -l gesehen.
def _php_dateien(wurzel):
    aus = []
    for w, _, ds in os.walk(wurzel):
        for name in sorted(ds):
            p = os.path.join(w, name)
            if name.endswith('.php'):
                aus.append(p)
                continue
            if '.' in name:
                continue
            try:
                with open(p, 'rb') as fh:
                    kopf = fh.readline(200).decode('utf-8', 'replace')
            except OSError:
                continue
            if kopf.startswith('#!') and 'php' in kopf:
                aus.append(p)
    return aus


# BEIDE Fassungen. LoxBerry 3.0 bis 4.0 fahren PHP 7.4, kuenftige 8.x - eine
# Pruefung gegen nur eine laesst die Haelfte durch. Bis zum 03.09.2026 lief
# hier ein blankes 'php' aus dem PATH, und das war auf diesem Rechner 7.4.
PHP_FASSUNGEN = [(v, p) for v, p in (
    ('7.4', r'C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe'),
    ('8.4', r'C:\tmp\php-8.4.27-Win32-vs17-x64\php.exe')) if os.path.isfile(p)]

phps = _php_dateien(ORDNER)
if not PHP_FASSUNGEN:
    melde('PHP-Syntax', None,
          '%d Dateien - keine der beiden PHP-Fassungen gefunden, nicht geprueft'
          % len(phps))
else:
    schlecht = []
    php_zugel = []
    for v, php in PHP_FASSUNGEN:
        for p in phps:
            r = subprocess.run([php, '-n', '-l', p], capture_output=True, text=True)
            # Die AUSGABE wird gelesen, nicht nur der Rueckgabewert.
            if r.returncode != 0 or 'No syntax errors' not in r.stdout:
                _t = '%s (%s)' % (os.path.basename(p), v)
                _id = ausnahme_fuer('PHP-Syntax', os.path.relpath(p, ORDNER)
                                    .replace(os.sep, '/'), v)
                (php_zugel.append((_t, _id)) if _id else schlecht.append(_t))
    melde('PHP-Syntax', not schlecht,
          '%d Dateien gegen %s%s' % (len(phps), ' und '.join(v for v, _ in PHP_FASSUNGEN),
                                     '' if not schlecht else
                                     ', FEHLER in ' + ', '.join(schlecht))
          + zugelassen_text(php_zugel))

# ---------- 1b. Perl-Syntax ----------
#
# NEU AM 07.09.2026, und der Anlass ist ein Fehler, der acht Fassungen lang
# durchging: Smartmeter classic gab am Geraet bei JEDEM Lauf
#
#     Prototype mismatch: sub main::decode_json ($) vs none
#
# aus - im Cron-Lauf ins Systemprotokoll, bei --themen und --roh mitten in
# die Antwort. Kein Werkzeug hat je "perl -c" gerufen, und die Perl-Attrappe
# schwieg dazu (sie bildete "use JSON;" nicht nach).
#
# ZWEI Dinge sind hier anders als bei PHP:
#
# 1. Der Rueckgabewert reicht NICHT. "perl -c" endet mit 0, obwohl es
#    warnt - genau diese Meldung ist eine Warnung. Gelesen wird deshalb die
#    AUSGABE, und alles ausser der Schlusszeile "... syntax OK" gilt.
# 2. Ohne die Attrappe unter Werkzeuge/perl_attrappe laesst sich kein
#    Plugin uebersetzen, das LoxBerry-Module einbindet. Fehlt sie, wird
#    NICHT geprueft und das auch so gesagt - eine Pruefung, die mangels
#    Umgebung immer gruen ist, ist schlimmer als keine.
def _perl_dateien(wurzel):
    """Wie bei PHP nach INHALT, nicht nur nach Endung."""
    aus = []
    for w, _, ds in os.walk(wurzel):
        for name in sorted(ds):
            q = os.path.join(w, name)
            if name.endswith('.pl') or name.endswith('.pm'):
                aus.append(q)
                continue
            # ERGAENZT 17.09.2026: eine Oberflaeche als .cgi fiel hier durch
            # den Punkt im Namen heraus. LoxoneIcons 2.0.4 fuehrte seine ganze
            # Oberflaeche als Perl in webfrontend/htmlauth/index.cgi, und das
            # Tor meldete "kein Perl in dieser Linie" - gruen, ohne zu messen.
            # .cgi zaehlt nur mit Perl-Kopfzeile; ein Shell-CGI bleibt draussen.
            if '.' in name and not name.endswith('.cgi'):
                continue
            try:
                with open(q, 'rb') as fh:
                    kopf = fh.readline(200).decode('utf-8', 'replace')
            except OSError:
                continue
            if kopf.startswith('#!') and 'perl' in kopf:
                aus.append(q)
    return aus


PERL_ATTRAPPE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'perl_attrappe')
perls = _perl_dateien(ORDNER)
if not perls:
    # ok=True, nicht None: hier war nicht "nichts zu messen", sondern
    # nichts DA. Ein Strich in 192 Linien ohne Perl wuerde die Zahl der
    # ungemessenen Punkte aufblaehen und den Blick auf die echten nehmen -
    # dasselbe Muster wie bei 'kein Archiv angegeben - entfaellt'.
    melde('Perl-Syntax', True, 'kein Perl in dieser Linie - entfaellt')
elif not os.path.isdir(PERL_ATTRAPPE):
    melde('Perl-Syntax', None,
          '%d Datei(en) - Werkzeuge/perl_attrappe fehlt, nicht geprueft'
          % len(perls))
else:
    _p_schlecht = []
    for q in perls:
        try:
            r = subprocess.run(['perl', '-I', PERL_ATTRAPPE, '-c', q],
                               capture_output=True, text=True)
        except OSError:
            _p_schlecht = None
            break
        # Die AUSGABE wird gelesen, nicht der Rueckgabewert: eine Warnung
        # laesst perl mit 0 enden.
        zeilen = [z.strip() for z in (r.stderr or '').splitlines() if z.strip()]
        rest = [z for z in zeilen if not z.endswith('syntax OK')]
        if r.returncode != 0 or rest:
            _p_schlecht.append('%s: %s' % (os.path.basename(q),
                                           rest[0] if rest else 'Rueckgabe %d'
                                           % r.returncode))
    if _p_schlecht is None:
        melde('Perl-Syntax', None,
              '%d Datei(en) - kein perl im Suchpfad, nicht geprueft' % len(perls))
    else:
        melde('Perl-Syntax', not _p_schlecht,
              '%d Datei(en) gegen die Attrappe%s'
              % (len(perls), '' if not _p_schlecht
                 else ', BEANSTANDET: ' + '; '.join(_p_schlecht)))

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
# Der Selbsttest muss kein PHP sein.
#
# Bis zum 03.09.2026 wurde nur nach 'bin/*_dienst.php' gesucht. VolkswagenID
# fuehrt seinen Selbsttest in bin/vw.py; das Tor fand nichts und meldete
# "entfaellt" - mit ok=True, also als bestandene Pruefung. Gesucht wird
# jetzt nach der SACHE: eine Datei unter bin/, die '--selbsttest' selbst
# auswertet.
def _selbsttest_suchen(wurzel, alle=False):
    # alle=True (seit 08.11.2026): JEDE Datei, die --selbsttest annimmt, als
    # Liste. Ohne Schalter wie bisher die erste - so liest es auch
    # selbsttest_bestand.py, das diese Funktion aus dem Quelltext loest.
    treffer = []
    bindir = os.path.join(wurzel, 'bin')
    if not os.path.isdir(bindir):
        return treffer if alle else None
    for name in sorted(os.listdir(bindir)):
        p = os.path.join(bindir, name)
        if not os.path.isfile(p):
            continue
        try:
            with open(p, 'rb') as fh:
                t = fh.read(400000).decode('utf-8', 'replace')
        except OSError:
            continue
        if '--selbsttest' not in t:
            continue
        # Die Zeichenfolge steht auch dort, wo sie nur WEITERGEREICHT wird.
        # bin/dienst.sh verteilt auf `selbsttest)` - ohne Striche - und ruft
        # damit ein anderes Programm auf; mit --selbsttest aufgerufen landet
        # es im Zweig *) und druckt seinen Hilfetext. Alphabetisch steht es
        # vor dem echten Selbsttest, und die Pruefung war dadurch dauerhaft
        # rot (gemessen 05.09.2026 an Govee 0.9.11-0.9.13 und Heimkino
        # 1.3.3/1.3.4; der echte Lauf php bin/govee_dienst.php --selbsttest
        # meldet 39 Faelle, 0 Fehlschlaege).
        #
        # Geprueft wird deshalb die AUFRUFFORM, nicht das Wort - dieselbe
        # Klasse wie eine Wache, die auf ein Wort prueft und auf den eigenen
        # Kommentar anschlaegt. Wer die Form nicht erfuellt, wird
        # uebersprungen, nicht genommen: dahinter liegt das richtige Programm.
        if name.endswith('.py'):
            if 'argv' not in t and 'argparse' not in t:
                continue
            # -B: kein bin/__pycache__ im PLUGIN-Ordner. Ohne den Schalter
            # legt der Selbsttestlauf ihn an, und die Hausstandard-Pruefung
            # meldet ihn danach als Muell - das Tor fiel ueber den eigenen
            # Rueckstand (gemessen 05.09.2026 an Dashboard 0.9.14).
            befehl = [PY, '-B', p]
        elif name.endswith('.php') or "env php" in t[:200]:
            if 'argv' not in t:
                continue
            befehl = [PHP_FASSUNGEN[0][1], p] if PHP_FASSUNGEN else None
        elif name.endswith('.sh') or t.startswith('#!'):
            # Ein Skript nimmt den Schalter nur an, wenn es ihn als Marke
            # fuehrt: `--selbsttest)` in einem case oder in Anfuehrungszeichen
            # in einem Vergleich. Ein blosses `prog --selbsttest` in einer
            # Befehlszeile ist Weitergabe, keine Annahme.
            # Nur im CODE, nicht in Kommentarzeilen: BatterieBMS 0.9.45
            # bin/dienst.sh nennt "(--einmal, --selbsttest)" in einem
            # Kommentar und wurde dadurch als Selbsttest gewaehlt (08.11.2026).
            t_code = '\n'.join(z for z in t.split('\n')
                               if not z.lstrip().startswith('#'))
            if ('--selbsttest)' not in t_code and '"--selbsttest"' not in t_code
                    and "'--selbsttest'" not in t_code):
                continue
            # Git Bash unter Windows findet "C:\...\bin\x.sh" nicht - der
            # gemischte Pfad endete mit Rueckgabe 127 (gemessen 08.11.2026 an
            # BatterieBMS, Bewaesserung, BLE-Scanner). Mit Schraegstrichen
            # geht er; unter Linux aendert das nichts.
            befehl = ['bash', p.replace(os.sep, '/')]
        else:
            continue
        if not alle:
            return befehl
        if befehl:
            treffer.append(befehl)
    return treffer if alle else None


dienste = _selbsttest_suchen(ORDNER, alle=True)
# SEIT 08.11.2026: JEDE Datei, die --selbsttest annimmt, und jede in einer
# LoxBerry-Umgebung.
#
# Bis dahin lief nur die ALPHABETISCH ERSTE. In 44 von 59 Linien ist das die
# gemeinsame bin/befehlsbruecke.php - und deren Selbsttest meldet in jeder
# Linie dasselbe "122 Faelle, 0 Fehlschlaege". Der eigene Selbsttest des
# Plugins lief nie. Gemessen 08.11.2026: Renault-NG 2.1.30 (veroeffentlicht)
# meldet in rn_selbsttest.php 158 Faelle, 1 Fehlschlag - das Tor zeigte gruen.
#
# Und die Umgebung: seit Spotpreis-Tibber 0.9.18 steht in tb_cron.php die
# Pruefung auf eine LoxBerry-Wurzel VOR dem Selbsttest (Regeln/06: nichts
# schreiben ohne Wurzel). Ohne LBHOMEDIR endet der Lauf mit Rueckgabe 1 und
# einer Meldung - "keine auswertbare Ausgabe", ein Kreuz ohne Befund. Mit
# einer frischen Kopie von lb_attrappe/ meldet derselbe Selbsttest 21 Faelle,
# 0 Fehlschlaege. Jeder Lauf bekommt deshalb seine EIGENE Kopie im
# Systemtemp: geschrieben wird dort, nie in die geteilte Attrappe Werkzeuge/lb
# und nie in den Pruefling (Arbeitsverzeichnis ist die Kopie).
#
# Auf einem eingerichteten LoxBerry (lb_da, unten) bleibt alles wie bisher:
# dort laeuft der Selbsttest in der echten Umgebung.
#
# Das Urteil ist das SCHLECHTESTE der Einzelurteile (Kreuz vor Strich vor
# Haken); die Zeile nennt jedes.
import shutil
import tempfile
lbhome = os.environ.get('LBHOMEDIR', '')
# Laeuft hier ueberhaupt ein LoxBerry? Die Marken-Form misst die
# EINRICHTUNG, nicht den Quelltext - ohne eingerichtete Anlage meldet sie
# zwangslaeufig Fehler, und keiner davon ist einer.
#
# Bis zum 03.09.2026 genuegte "LBHOMEDIR gesetzt und config/system da".
# Beides trifft auf die Attrappe unter Werkzeuge/lb zu - sie sieht aus
# wie ein LoxBerry. Sie ist aber keine eingerichtete Anlage: es gibt
# keine virtuelle Python-Umgebung, kein Konto, keine Zugangsdatei. Eine
# Einrichtungspruefung meldet dort zwangslaeufig Fehler, und keiner davon
# ist einer des Plugins. Gemessen an VolkswagenID 0.9.12: sieben [FEHL],
# alle aus der Umgebung.
#
# Der LoxBerry ist ein Debian. Laeuft die Freigabepruefung unter Windows,
# misst die Marken-Form nichts, was ueber das Plugin aussagt.
lb_da = (bool(lbhome) and os.path.isdir(os.path.join(lbhome, 'config', 'system'))
         and os.name != 'nt')
_st_ordner = PLUGIN_KENNUNG[2] or PLUGIN_KENNUNG[1]
_st_urteile = []
_st_reste = []


def _wegraeumen(pfad):
    """Kopie loeschen - und SAGEN, wenn es nicht geht. Rueckgabe: '' oder der Pfad.

    Bis 08.11.2026 stand hier rmtree(ignore_errors=True). Im Bestandslauf blieb
    so EINE Kopie still liegen (unter Windows haelt ein noch laufender Prozess
    sein Arbeitsverzeichnis fest); erst eine Zaehlung im Systemtemp fand sie.
    Drei Versuche mit kurzer Pause, dann der Pfad in die Meldung.
    """
    import time
    for _ in range(3):
        shutil.rmtree(pfad, ignore_errors=True)
        if not os.path.exists(pfad):
            return ''
        time.sleep(1)
    return pfad
for dienst in dienste:
    # ABSOLUT, bevor das Arbeitsverzeichnis wechselt: ORDNER kommt meist
    # relativ ("LoxBerry-Plugin-X-1.0.0"), und mit cwd in der Kopie fand
    # php die Datei nicht mehr (erster Eichlauf 08.11.2026: fuenf von fuenf
    # Linien "Could not open input file").
    dienst = dienst[:-1] + [os.path.abspath(dienst[-1]).replace(os.sep, '/')
                            if dienst[0] == 'bash' else os.path.abspath(dienst[-1])]
    # Unter Windows sucht CreateProcess ZUERST in System32 - dort liegt das
    # bash der WSL, das keine C:/-Pfade kennt (Rueckgabe 127, 08.11.2026).
    # Gemeint ist Git Bash vom PATH.
    #
    # Und das Urteil eines Skript-Selbsttests unter Windows ist ein STRICH,
    # wie die Marken-Form: Git Bash ist kein Debian. Gemessen 08.11.2026 an
    # BLE-Scanner 1.3.36, bl_haken.sh: 13 Faelle, 2 Fehlschlaege - beide in
    # der Prozesssuche (bl_dienste_finden), die es unter Git Bash nicht gibt.
    # Liefert das Skript GAR KEINE der Formen, bleibt es ein Kreuz.
    _st_skript_win = dienst[0] == 'bash' and os.name == 'nt' and not lb_da
    if dienst[0] == 'bash' and os.name == 'nt':
        dienst = [shutil.which('bash') or 'bash'] + dienst[1:]
    _st_name = os.path.basename(dienst[-1])
    _st_tmp = None
    if lb_da:
        _st_umg = None
        _st_cwd = None
    else:
        _st_tmp = tempfile.mkdtemp(prefix='freigabe_selbsttest_')
        _st_lb = os.path.join(_st_tmp, 'lb')
        shutil.copytree(os.path.join(HIER, 'lb_attrappe'), _st_lb)
        _st_umg = dict(os.environ, LBHOMEDIR=_st_lb, LBPPLUGINDIR=_st_ordner,
                       LBPCONFIGDIR=os.path.join(_st_lb, 'config', 'plugins', _st_ordner),
                       LBPDATADIR=os.path.join(_st_lb, 'data', 'plugins', _st_ordner),
                       LBPLOGDIR=os.path.join(_st_lb, 'log', 'plugins', _st_ordner))
        _st_cwd = _st_tmp
    try:
        r = subprocess.run(dienst + ['--selbsttest'], capture_output=True, text=True,
                           encoding='utf-8', errors='replace', env=_st_umg,
                           cwd=_st_cwd, timeout=300)
        _st_aus, _st_rc = r.stdout, r.returncode
    except subprocess.TimeoutExpired:
        _st_aus, _st_rc = None, None
    finally:
        _st_rest = _wegraeumen(_st_tmp) if _st_tmp else ''
    if _st_rest:
        _st_reste.append(_st_rest)
    if _st_aus is None:
        _st_urteile.append((False, '%s: Zeitueberschreitung (300 s)' % _st_name))
        continue
    m = re.search(r'(\d+) Faelle geprueft, (\d+) Fehlschl', _st_aus)
    # Dritte Form (08.11.2026): "SELBSTTEST gut/schlecht" als eigene Zeile,
    # Chromecast4lox seit 1.3.25. Bis dahin lief sie nie, weil davor die
    # Befehlsbruecke gewaehlt wurde.
    m3 = re.search(r'^SELBSTTEST (\d+)/(\d+)\s*$', _st_aus, re.M)
    marken = re.findall(r'^\[(OK|FEHL|INFO)\]', _st_aus, re.M)
    if m and _st_skript_win:
        _st_urteile.append((None, '%s: %s Faelle, %s Fehlschlaege - Skript unter '
                            'Git Bash, nicht auf Debian gemessen'
                            % ((_st_name,) + m.groups())))
    elif m:
        _st_urteile.append((m.group(2) == '0', '%s: %s Faelle, %s Fehlschlaege'
                            % ((_st_name,) + m.groups())))
    elif m3:
        _st_urteile.append((m3.group(2) == '0' and _st_rc == 0,
                            '%s: %s gut, %s schlecht, Rueckgabe %d'
                            % ((_st_name,) + m3.groups() + (_st_rc,))))
    elif marken and not lb_da:
        _st_urteile.append((None, '%s: %d Zeilen, %d [FEHL] - nicht an einer '
                            'eingerichteten Anlage gemessen' % (
                                _st_name, len(marken), marken.count('FEHL'))))
    elif marken:
        fehl = marken.count('FEHL')
        _st_urteile.append((fehl == 0 and _st_rc == 0, '%s: %d Zeilen, %d [FEHL], '
                            'Rueckgabe %d' % (_st_name, len(marken), fehl, _st_rc)))
    else:
        _st_erste = (_st_aus + r.stderr).strip().split('\n')[0][:100]
        _st_urteile.append((False, '%s: keine auswertbare Ausgabe (Rueckgabe %d): %s'
                            % (_st_name, _st_rc, _st_erste)))
if _st_urteile:
    _st_werte = [u for u, _ in _st_urteile]
    _st_gesamt = (False if False in _st_werte
                  else (None if None in _st_werte else True))
    melde('Selbsttest', _st_gesamt,
          '%d Selbsttest(s): %s' % (len(_st_urteile),
                                    '; '.join(t for _, t in _st_urteile))
          + ('; KOPIE NICHT ENTFERNT (laeuft dort noch ein Prozess?): %s'
             % ', '.join(_st_reste) if _st_reste else ''))
else:
    # STRICH, kein Haken. "Konnte nicht pruefen" ist nicht "geprueft und in
    # Ordnung"; wer das einsammelt, hat eine Pruefung weniger, als er glaubt.
    melde('Selbsttest', None,
          'unter bin/ wertet keine Datei --selbsttest aus - nichts gemessen')

# ---------- 3. Sprachdateien ----------
r = subprocess.run([PY, os.path.join(HIER, 'ini_pruefen.py'), ORDNER],
                   capture_output=True, text=True)
letzte = [z for z in r.stdout.strip().splitlines() if z.strip()][-1] if r.stdout.strip() else '?'
melde('Sprachdateien', r.returncode == 0, letzte[:70])

# ---------- 4. Oberflaechen-Hausstandard ----------
hs = os.path.join(HIER, 'hausstandard_pruefen.py')
if os.path.isfile(hs):
    r = subprocess.run([PY, hs, ORDNER], capture_output=True, text=True)
    zeile = [z for z in r.stdout.splitlines() if ORDNERNAME[:20] in z]
    kl = re.findall(r'\b([a-z]{2,6})\b', zeile[0].split(None, 1)[1]) if zeile else []
    # BERICHTIGT 04.09.2026: die ZUSATZZEILEN werden mitgelesen.
    #
    # Bis hierher las dieser Abschnitt nur die eine Zeile, die den
    # Pluginnamen traegt. Die Zusatzzeilen beginnen mit Leerzeichen und
    # tragen ihn nicht - sie fielen also durch. Deshalb war das Tor bei
    # Intercom 2.2.5 gruen ("14 Pruefungen, 0 Beanstandungen"), obwohl
    # hausstandard_pruefen.py die tote Klasse .sm-warnung gemeldet hatte;
    # die ging in fuenf Linien hinaus. Regeln/02 sagt ausdruecklich:
    # Zusatzzeilen werden gelesen wie ein Kreuz, nicht wie eine Fussnote.
    zusatz = [z.split(':', 1)[1].strip() for z in r.stdout.splitlines()
              if 'Zusatz-BEFUND:' in z]
    hinweise = [z for z in r.stdout.splitlines() if 'Zusatz-Hinweis:' in z]
    # Entscheidung 43 (08.10.2026, Hausherr wie empfohlen): kpf (Status ueber
    # den Reitern) und kas (Kasten oben im ersten Reiter) werden waehrend der
    # Umbau-Wellen nur ANGEZEIGT, nicht gesperrt - sonst waere das Tor fuer 49
    # von 51 Linien rot, auch fuer reine Fehlerbehebungen. Eine Linie, die den
    # Kopf schon traegt, faellt trotzdem auf: ihre Spalte waere dann klein und
    # stuende hier sichtbar im Text. Nach der letzten Welle KOPF_NUR_ANZEIGEN
    # auf False setzen.
    # 09.10.2026: alle Linien tragen den Kopf - ab jetzt sperrt er wieder.
    KOPF_NUR_ANZEIGEN = False
    kopf = [k for k in kl if k in ('kpf', 'kas')] if KOPF_NUR_ANZEIGEN else []
    sperrend = [k for k in kl if k not in kopf]
    text = 'offene Spalten: %s' % (', '.join(sperrend) if sperrend else 'keine')
    if kopf:
        text += ' (Kopf nach Nr. 43 noch offen, sperrt nicht: %s)' % ', '.join(kopf)
    if zusatz:
        text += '; Zusatz: ' + '; '.join(zusatz)
    elif hinweise:
        text += ', %d Hinweis(e)' % len(hinweise)
    # Die Rueckgabe des Pruefers ist 1, sobald irgendeine Spalte offen ist -
    # auch nur kpf/kas. Sie zaehlt deshalb nur, wenn sperrende Spalten offen
    # sind oder keine Zeile gelesen wurde.
    rc_ok = r.returncode == 0 or (bool(zeile) and not sperrend)
    melde('Hausstandard', rc_ok and not sperrend and not zusatz, text)
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
        kopf = [z for z in r.stdout.splitlines() if ORDNERNAME[:20] in z]
        # STRICH, kein Haken: findet sich die Zeile des Werkzeugs nicht,
        # ist die Frage NICHT gestellt worden. "Geprueft und in Ordnung"
        # und "konnte nicht pruefen" sind zwei verschiedene Ausgaenge.
        if kopf:
            melde('Loxone-Suchtexte', True, kopf[0].split(None, 1)[1].strip()[:70])
        else:
            melde('Loxone-Suchtexte', None,
                  'suchmuster_pruefen.py hat keine Zeile zu diesem Ordner '
                  'geliefert - nichts gemessen')
else:
    melde('Loxone-Suchtexte', True, 'suchmuster_pruefen.py fehlt - entfaellt')

# ---------- 4b2. Steuerzeichen in erzeugten Kommandozeilen ----------
#
# Der Anlass, 27.08.2026: MG iSmart baute
#     $cmd = 'while IFS="\\t" read -r t v; do ' . … ;
# In einem EINFACH angefuehrten PHP-String ist \t kein Tabulator. An die Schale
# ging woertlich IFS="\t", das Trennzeichen war damit der Buchstabe t. Gemessen
# mit dash ueber 68 Themen: 0 kamen richtig an, 26 mit leerer Nutzlast - und
# leer plus -r loescht ein behaltenes Thema. Drei Fassungen veroeffentlicht,
# durch neun gruene Pruefungen gegangen, gefunden von einem Anwender.
#
# Beanstandet wird nur, was die Schale NICHT aufloest (Klassen A, B, C des
# Werkzeugs). Die Hinweise - Backslash-Folgen, die ein printf, awk oder
# mosquitto_sub selbst aufloest - stehen im Einzelbericht, nicht hier.
sz = os.path.join(HIER, 'schalenzeichen_pruefen.py')
if os.path.isfile(sz):
    r = subprocess.run([PY, sz, ORDNER], capture_output=True, text=True)
    schlimm = [z.strip() for z in r.stdout.splitlines() if z.strip().startswith('BEFUND')]
    if schlimm:
        melde('Steuerzeichen', False, '%d Stelle(n), erste: %s'
              % (len(schlimm), schlimm[0][8:60]))
    else:
        melde('Steuerzeichen', True, 'keine Kommandozeile mit rohem Backslash')
else:
    melde('Steuerzeichen', True, 'schalenzeichen_pruefen.py fehlt - entfaellt')

# ---------- 4b3. Verschachtelte und unvollstaendige Formulare ----------
#
# Der Anlass, 13.09.2026: ZendureSolarFlow trug die Knoepfe "Konfiguration
# ausgeben" und "Konfiguration einlesen" in zwei <form>, die MITTEN im
# Einstellungsformular standen. Der Browser verwirft verschachtelte
# <form>-Marken; die Knoepfe gehoerten danach zum aeusseren Formular. Folge:
# "Ausgeben" speicherte nebenbei die Einstellungen, und "Einlesen" KONNTE
# nicht funktionieren - dem aeusseren Formular fehlt
# enctype="multipart/form-data", die Datei kam nie an. Still, ohne
# Fehlermeldung.
#
# Das steckte in drei veroeffentlichten Fassungen und ist durch jedes
# Freigabetor gegangen, weil diese Pruefung nicht darin war. Genau deshalb
# steht sie jetzt hier.
#
# Der Einbau kostet den Bestand nichts: am 14.09.2026 ueber alle 270
# Plugin-Ordner gemessen, 3 mit Befund - und alle drei sind alte
# Zendure-Staende (0.9.15 bis 0.9.17), die nicht mehr angefasst werden. Kein
# aktueller Arbeitsordner wird davon rot.
#
# Gemessen wird am GERENDERTEN HTML, nicht am Quelltext: <?php ?>-Zweige
# machen aus einer Datei mehrere moegliche Seiten, und die Schachtelung
# entsteht erst in der ausgelieferten.
#
# AN EINER KOPIE seit 08.11.2026 (CLAUDE.md Abschnitt 5: ein Pruefauftrag
# bekommt eine Kopie). Das Rendern fuehrt den Code des Plugins aus, und der
# schrieb in den Pruefling: AnkerSolix 0.9.40 legte config/ankersolix.json
# und .backup.json an (es nimmt den Ordnernamen mit Punkten aus LBPPLUGINDIR
# nicht an und arbeitet dann "nicht installiert" neben sich), Zigbee2MqttNG
# 4.2.12 seinen Twig-Zwischenspeicher unter templates/cache/ (er liegt unter
# LBPTEMPLATEDIR, und das ist hier der Pruefling). Beides stand danach im
# Ordner und waere mit dem naechsten Packen ins Archiv gegangen. Die Kopie
# traegt denselben Ordnernamen, damit die Attrappe dieselben Pfade sieht.
fp = os.path.join(HIER, 'formularpruefung.py')
if os.path.isfile(fp):
    import shutil
    import tempfile
    _fp_tmp = tempfile.mkdtemp(prefix='freigabe_formulare_')
    _fp_kopie = os.path.join(_fp_tmp, os.path.basename(os.path.abspath(ORDNER)))
    try:
        shutil.copytree(ORDNER, _fp_kopie, symlinks=True)
        r = subprocess.run([PY, fp, _fp_kopie], capture_output=True, text=True)
    finally:
        _fp_rest = _wegraeumen(_fp_tmp)
    zeilen = [z.strip() for z in r.stdout.splitlines() if z.strip()]
    schluss = [z for z in zeilen if 'Linien geprueft' in z]
    befund = [z for z in zeilen if z.startswith(os.path.basename(ORDNER))
              and not z.endswith(' ok')]
    if not schluss:
        melde('Formulare', None,
              'formularpruefung.py gab keine auswertbare Ausgabe - nicht gemessen')
    elif 'ohne Oberflaeche uebersprungen' in schluss[0] and '1 ohne' in schluss[0]:
        melde('Formulare', True, 'keine Oberflaeche in dieser Linie - entfaellt')
    elif r.returncode != 0 or befund:
        melde('Formulare', False,
              befund[0].split(None, 1)[1][:70] if befund else schluss[0][:70])
    else:
        melde('Formulare', True, 'keine verschachtelten <form>')
    if _fp_rest:
        melde('Formulare-Kopie', None,
              'Kopie nicht entfernt (laeuft dort noch ein Prozess?): %s' % _fp_rest)
else:
    melde('Formulare', True, 'formularpruefung.py fehlt - entfaellt')

# ---------- 4c. Die LoxBerry-Attrappe ----------
#
# Sie ist eine handgeschriebene Nachbildung und altert gegen das Original.
# Am 25.08.2026 fehlte ihr notify_ext(), das acht Plugins rufen - drei von
# vier Staenden waren ausserdem veraltet. Ohne Netz nicht messbar; dann ein
# Strich, kein Haken.
#
# NACHGEBESSERT am 29.08.2026 - zwei Maengel DIESER Zeile, nicht der Plugins.
#
# Der Hausherr mass an vier Plugins unabhaengig voneinander "2 Befund(e)" und
# suchte den Fehler in den Plugins. Er lag in keinem: die Zahl haengt
# ueberhaupt nicht am Pruefling. Zwei Dinge waren falsch.
#
# ERSTENS nannte die Zeile nur die ANZAHL. Wer wissen wollte, WAS die zwei
# sind, musste ein zweites Werkzeug von Hand starten - und bis dahin sah der
# Bericht aus, als sei das Plugin schuld. Es waren die vier Staende der
# phplib, von denen einer in derselben Nacht gehaertet worden war (LBLANG
# und LB_ATTRAPPE_LOGLIST) und die drei anderen nicht. Ein Befund am
# PRUEFSTAND, in der Zeile eines Plugins gemeldet.
#
# Das ist genau der Fall aus REGELN_1 „Ein Waechter, der Ausnahmen macht,
# zaehlt sie und nennt sie": eine Meldung, die bei jedem Lauf dieselbe ist,
# wird nicht mehr gelesen. Die Zeile nennt jetzt die Fundstellen mit
# Abschnitt und sagt dazu, ob sie am Plugin oder am Pruefstand haengen.
#
# ZWEITENS las die Attrappenpruefung den GANZEN Arbeitsordner. Die Luecke
# eines fremden Plugins haette die Freigabe dieses Plugins rot gefaerbt.
# Frage 1 laeuft jetzt mit --plugin nur ueber den Pruefling; die Fragen
# ueber den Pruefstand selbst bleiben ordnerweit, denn ein schiefer
# Pruefstand macht JEDE Messung an diesem Plugin fraglich.
#
# NACHGEZOGEN am 29.08.2026, zweiter Durchgang: --ohne-netz sprang die
# ganze Pruefung, obwohl EINE ihrer vier Fragen kein Netz braucht. Frage 4
# vergleicht die vier phplib-Staende unter Werkzeuge/ - vier Ordner auf
# dieser Platte. Ausgerechnet sie war der Befund vom 29.08.2026, und
# ausgerechnet sie fiel im Zug ohne Empfang mit aus.
#
# --ohne-netz wird jetzt durchgereicht statt den Aufruf zu unterdruecken.
# Was dann noch offen ist, sagt das Werkzeug in seiner Zeile
# „nicht gemessen:" selbst - und ein Lauf mit 0 Befunden aus drei
# ungestellten Fragen bekommt einen STRICH, keinen Haken. Sonst waere
# --ohne-netz der bequeme Weg zu einem gruenen Bericht.
ap = os.path.join(HIER, 'attrappe_pruefen.py')
if os.path.isfile(ap):
    ruf = [PY, ap, '--plugin', os.path.abspath(ORDNER)]
    if OHNE_NETZ:
        ruf.append('--ohne-netz')
    r = subprocess.run(ruf, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    m = re.search(r'== (\d+) Befund', r.stdout)
    offen = re.search(r'(?m)^\s*nicht gemessen: (.+?)\s*$', r.stdout)
    if m is None:
        melde('LoxBerry-Attrappe', None, 'kein Ergebnis - nicht gemessen')
    else:
        # Jede rote Zeile mit dem Abschnitt, unter dem sie stand.
        abschnitt, rote = 'Attrappe', []
        for z in r.stdout.splitlines():
            s = z.strip()
            if s.startswith('---') and s.endswith('---'):
                abschnitt = s.strip('- ').split(':')[0].strip()
                while len(abschnitt) > 26 and ' ' in abschnitt:
                    abschnitt = abschnitt.rsplit(' ', 1)[0]
            elif s.startswith('ROT'):
                rote.append((abschnitt, ' '.join(s[3:].split())))
        if int(m.group(1)):
            am_plugin = sum(1 for a, _ in rote if a.startswith('Luecke'))
            am_stand = len(rote) - am_plugin
            wo = ', '.join(x for x in (
                '%d am Plugin' % am_plugin if am_plugin else '',
                '%d am PRUEFSTAND' % am_stand if am_stand else '') if x)
            melde('LoxBerry-Attrappe', False,
                  '%s Befund(e)%s' % (m.group(1), ' - ' + wo if wo else ''))
            for a, s in rote[:8]:
                print('         %s: %s' % (a, s))
            if len(rote) > 8:
                print('         ... und %d weitere' % (len(rote) - 8))
            if not rote:
                # Die Zahl sagt "Befund", keine Zeile passte auf das Muster.
                # Dann ist die Ausgabe des Werkzeugs zu lesen, nicht diese.
                print('         (keine Fundzeile erkannt - '
                      'attrappe_pruefen.py von Hand aufrufen)')
            if offen:
                print('         offen geblieben: %s' % offen.group(1))
        elif offen:
            melde('LoxBerry-Attrappe', None,
                  'Staende gleich; nicht gemessen: %s' % offen.group(1))
        else:
            melde('LoxBerry-Attrappe', True,
                  'keine Luecke, keine Leiche, Staende gleich')
else:
    melde('LoxBerry-Attrappe', True, 'attrappe_pruefen.py fehlt - entfaellt')

# ---------- 4d. Fest verdrahtete Systempfade ----------
#
# ANLASS (27.08.2026): Kodi NG 1.2.0 wurde veroeffentlicht und meldete beim
# Einspielen "HARDCODED PATH'S" - ein fester Rueckfall auf die
# Installationswurzel in uninstall/uninstall. Diese Freigabepruefung war dabei
# ZEHNMAL GRUEN. Die Regel stand seit dem 22.08.2026 in REGELN_2, samt
# Vorlage; es gab nur kein Werkzeug, das danach sucht.
#
# ZWEI STUFEN, und der Unterschied ist gewollt:
#
#   sichtbar   endungslose Dateien (uninstall/uninstall, daemon/daemon).
#              Nur die sieht plugininstall.pl - sein grep in Zeile 778
#              ueberspringt jede Datei MIT Endung. Das ist die Beanstandung.
#
#   uebrige    Kommentare, README-Beispiele, .php und .sh. Nach der Regel
#              Befunde, aber sie loesen beim Einspielen nichts aus. Sie
#              stehen als Zahl im Text und werden bei der naechsten ohnehin
#              anstehenden Fassung mitgezogen - eine eigene Release-Welle
#              ueber fuenfzehn veroeffentlichte Linien waere teurer als der
#              Fehler.
hp = os.path.join(HIER, 'harte_pfade.py')
if os.path.isfile(hp):
    r = subprocess.run([PY, hp, ORDNER], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    m_s = re.search(r'sichtbar: (\d+) Fundstelle', r.stdout)
    m_d = re.search(r'(\d+) Dateien angesehen, (\d+) mit Fundstelle', r.stdout)
    if m_s is None or m_d is None:
        melde('Harte Systempfade', None, 'Werkzeug lieferte keine Zahl - nicht gemessen')
    elif int(m_d.group(1)) == 0:
        # Keine Datei angesehen heisst nicht "sauber", sondern "nichts gemessen".
        melde('Harte Systempfade', None, 'keine Datei angesehen - nicht gemessen')
    else:
        sichtbar = int(m_s.group(1))
        stellen = sum(1 for z in r.stdout.split('\n') if z.startswith('      '))
        if sichtbar:
            melde('Harte Systempfade', False,
                  '%d Fundstelle(n), die der Pluginpruefer meldet' % sichtbar)
        elif stellen:
            melde('Harte Systempfade', True,
                  '%d Dateien, %d Fundstelle(n) nur in Kommentaren - beim naechsten Anlass mitziehen'
                  % (int(m_d.group(1)), stellen // 2))
        else:
            melde('Harte Systempfade', True, '%d Dateien, keine Fundstelle' % int(m_d.group(1)))
else:
    melde('Harte Systempfade', True, 'harte_pfade.py fehlt - entfaellt')

# ---------- 5. Fassungslage ----------
if OHNE_NETZ:
    melde('Fassungslage', True, 'uebersprungen (--ohne-netz)')
else:
    r = subprocess.run([PY, os.path.join(HIER, 'fassungslage.py'), ORDNER],
                       capture_output=True, text=True)
    schlimm = 'DIESELBE NUMMER' in r.stdout or 'BIETET diese Nummer AN' in r.stdout
    m = re.search(r'plugin\.cfg\s+VERSION=(\S+)', r.stdout)
    # Eine ZEITUEBERSCHREITUNG gegen GitHub ist keine Abweichung, sondern ein
    # nicht zustandegekommener Vergleich. Am 30.08.2026 meldete diese Zeile
    # deshalb "ABWEICHUNG" fuer einen Ordner, der beim naechsten Lauf
    # unveraendert "stimmig" war - eine Netzstoerung, aus der ein
    # Inhaltsbefund wurde. Ein Strich sagt, was wirklich vorliegt: hier war
    # nichts zu messen.
    stumm = ('timed out' in r.stdout or 'Temporary failure' in r.stdout
             or 'Name or service not known' in r.stdout
             or 'getaddrinfo' in r.stdout)
    if stumm and not schlimm:
        melde('Fassungslage', None, 'Ordner %s - GitHub antwortete nicht, '
              'nicht feststellbar' % (m.group(1) if m else '?'))
    else:
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
erlaubt = {
    b'noreply@github.com',
    # Das Rechenbeispiel aus RFC 2617, Abschnitt 3.5. ACTiKamera prueft damit
    # seine Digest-Anmeldung gegen die veroeffentlichten Sollwerte. Wer die
    # Zeichenkette aendert, bricht den Selbsttest - der Hashwert im Standard
    # ist auf genau diesen Text gerechnet. Es ist eine Konstante aus einer
    # Festlegung, keine Person.
    b'testrealm@host.com',
}
BEISPIELDOMAENE = (b'@example.com', b'@example.net', b'@example.org')

# ======================================================================
# Fuenf Fehlalarme, gemessen am 29.08.2026 ueber ALLE 51 Plugins
# ======================================================================
#
# Der Abschnitt war in 19 von 51 Plugins rot und hatte in KEINEM davon
# recht: rund 60 Treffer, kein einziger echter. Er war damit nicht nur
# nutzlos, sondern schaedlich - `freigabe_eichung.py` kam gar nicht mehr
# zum Messen, weil sie eine gruene Ausgangslage braucht. Der Waechter hat
# also nebenbei seine eigene Eichung stillgelegt.
#
# Jede Ausnahme unten haengt am WERT oder am Zusammenhang, keine an einem
# Namen, und jede wird gezaehlt und im Ergebnis genannt.


def zeilenrand(b, pos):
    """Anfang und Ende der Zeile, in der pos steht."""
    a = b.rfind(b'\n', 0, pos) + 1
    e = b.find(b'\n', pos)
    return a, (e if e >= 0 else len(b))


# ---- 1. Die Adresse des Urhebers -------------------------------------
#
# michael@loxberry.de (Smartmeter, LoxoneIcons), m.i.dietrich@gmx.de
# (WOLF-ISM-NG) und dominik.holland@googlemail.com (WiFi-Scanner-NG)
# stehen in Apache-2.0-Urhebervermerken und in NOTICE-Dateien. Die Lizenz
# VERLANGT ihre Nennung (Abschnitt 4c und 4d) - sie zu entfernen waere ein
# Lizenzbruch, keine Verbesserung. REGELN_2 haelt denselben Fall fuer die
# NAMEN schon fest ("Christian Woerstenfeld", "Christian Fenzl"); die
# Adressen fehlten dort.
#
# Erkannt wird nicht die Adresse, sondern ihre ROLLE: eine Anschrift, die
# in DIESEM Plugin in einer NOTICE/LICENSE-Datei oder in einer
# Urheberzeile steht, ist die Anschrift des Urhebers - und dann ist sie es
# auch an jeder anderen Stelle desselben Plugins. Eine versehentlich
# hinterlassene Privatadresse steht in keiner Lizenzdatei.
LIZENZDATEI = ('NOTICE', 'LICENSE', 'LICENCE', 'COPYING', 'AUTHORS')
URHEBERWORT = (b'copyright', b'\xc2\xa9', b'(c)', b'autor', b'author',
               b'urheber', b'mailadresse', b'lizenz', b'license')

# ---- 2. Platzhalteradressen ------------------------------------------
#
# dein.name@mail.de steht in einem placeholder-Feld von Octopus. Am Namen
# der Anschrift ist das zu sehen, nicht an ihrer Herkunft.
# ZU WEIT im ersten Anlauf, von der Eichung sofort gefangen: die Liste
# trug `name@` und `vorname.nachname@`. Damit blieb der Eichfall "echte
# E-Mail-Adresse" (vorname.nachname@irgendeinehausadresse.de) GRUEN - eine
# Anschrift, die das Haus ausdruecklich gefunden haben will, und `name@`
# haette sie schon als Teilzeichenkette von "nachname@" ausgenommen.
#
# Zwei Verengungen daraus:
#   * geprueft wird nur der Teil VOR dem @, nicht die ganze Anschrift.
#     Sonst nimmt `ihr.` auch info@firma.ihr.de aus.
#   * das Wort muss den Namensteil ANFANGEN und mit einem Punkt enden
#     (oder ihn ganz ausmachen). Sonst faellt meinhard@... mit hinein.
MAIL_PLATZHALTER = (b'dein', b'deine', b'ihr', b'ihre', b'your', b'yours',
                    b'mein', b'meine', b'my', b'max.mustermann', b'john.doe',
                    b'jane.doe', b'erika.mustermann')


def ist_mail_platzhalter(tr):
    lok = tr.split(b'@')[0].lower()
    return any(lok == x or lok.startswith(x + b'.') for x in MAIL_PLATZHALTER)

# ---- 3. Platzhalter-MAC ----------------------------------------------
#
# 13 Treffer in BLE-Scanner, Heimkino und WiFi-Scanner-NG, alle aus
# Anleitungen und Selbsttests. AA:BB:CC:DD:EE:FF ist die uebliche
# Schreibhilfe; BLE-Scanner setzt das erste Feld ab (C4:, 4A:, 0A:), weil
# es genau daran den Adresstyp erklaert. Eine echte Geraeteadresse traegt
# nicht die aufsteigende Reihe BB:CC:DD:EE:FF.
MAC_PLATZHALTER_ENDE = b':BB:CC:DD:EE:FF'
MAC_PLATZHALTER_GANZ = (b'11:22:33:44:55:66', b'00:00:00:00:00:00',
                        b'FF:FF:FF:FF:FF:FF', b'12:34:56:78:9A:BC')

# ---- 4. Fassungsnummern, die wie Adressen aussehen -------------------
#
# 15 Treffer, und kein einziger war eine Adresse: LoxBerry 4.0.0.13 und
# 4.0.0.14, Miniserver-Firmware 17.1.7.27, "next/prev seit 13.3.1.10",
# App 1.19.1.1, Abschnitt 3.3.1.3 aus der MQTT-Festlegung und
# 999.999.999.999 als Gegenbeispiel in einem Kommentar ueber Pruefungen.
#
# ZWEI Bedingungen, wie am 29.08.2026 entschieden:
#   * die Zahl muss eine gueltige Adresse sein (jedes Feld <= 255) - das
#     allein erledigt 999.999.999.999
#   * die Zeile darf sie nicht selbst als Fassung ausweisen
#
# Die Woerter stehen einzeln da und sind gemessen, nicht geraten: jedes
# stammt aus einer der 15 Fundzeilen. "seit" ist das schwaechste davon und
# traegt drei Treffer ("next/prev seit 13.3.1.10"); es bleibt drin, weil
# die Ausnahme GEZAEHLT wird - wer die Zahl im Bericht sieht, kann
# nachsehen.
FASSUNGSWORT = (b'fassung', b'version', b'firmware', b'abschnitt',
                b'kapitel', b'release', b'ausgabe', b'loxberry',
                b'miniserver', b'seit ')

# ---- 5. Oeffentliche Namensdienste -----------------------------------
#
# 8.8.8.8 in Chromecast4lox, Octopus und aWATTar. Gemessen: ein
# UDP-connect, das NIE ein Paket sendet - es legt nur die Route fest,
# damit getsockname() die eigene Adresse verraet. Kein Gegenueber, keine
# Person, und der Quelltext sagt es an allen drei Stellen selbst.
OEFFENTLICHER_DNS = (b'8.8.8.8', b'8.8.4.4', b'1.1.1.1', b'9.9.9.9',
                     b'208.67.222.222')


def ist_gueltige_adresse(tr):
    teile = tr.split(b'.')
    return len(teile) == 4 and all(t.isdigit() and int(t) <= 255 for t in teile)


# ---- 6. Ein Anfuehrungszeichen, das SCHLIESST ------------------------
#
# cam.php schreibt   echo 'Passwort:    ' . strlen($d_cfg['pass'])
# und meldete damit einen Fund. Das Zeichen hinter "Passwort:" oeffnet
# dort nichts, es schliesst die Zeichenkette, die vor "Passwort" begonnen
# hat - was folgt, ist Rechenwerk und kein Geheimnis. Die Zeile verraet
# ausserdem nur die LAENGE des Passworts.
#
# Zwei Bedingungen, damit daraus kein Schlupfloch wird:
#   * vor dem Wort steht eine UNGERADE Zahl desselben Zeichens - wir sind
#     also mitten in einer Zeichenkette
#   * hinter dem Zeichen folgt ein Verknuepfer (. , ; ) + }), kein Wert
#
# Ein   $passwort = "geheim123";   hat null Anfuehrungszeichen davor und
# faellt durch beide Bedingungen. Gemessen in freigabe_eichung.py.
VERKNUEPFER = b'.,;)+}]'


def ist_schliessendes_zeichen(b, pos, treffer):
    """pos = Anfang des Treffers, treffer = die ganze Fundstelle."""
    i = min((treffer.find(z) for z in (b'"', b"'") if treffer.find(z) >= 0),
            default=-1)
    if i < 0:
        return False
    zeichen = treffer[i:i + 1]
    a, _ = zeilenrand(b, pos)
    if b[a:pos].count(zeichen) % 2 == 0:
        return False
    rest = treffer[i + 1:].lstrip()
    return bool(rest) and rest[:1] in VERKNUEPFER


# ---- 7. Beschriftungen ohne Hausvorsatz ------------------------------
#
# 22 Treffer der Form   PASSWORT = "Passwort"   in Sprachdateien. Die
# Ausnahme vom 20.08.2026 verlangte einen Vorsatz (L_, H_, F_, A_ ...);
# ein Schluessel, der einfach PASSWORT heisst, hatte keinen und fiel
# durch. Ebenso lange Saetze wie "Wird nie angezeigt, auch nicht
# verkuerzt."
#
# Die neue Bedingung haengt wieder am WERT und gilt NUR unter
# templates/lang/:
#   * der Wert traegt ein Leerzeichen - dann ist es ein Satz -, ODER
#   * der Wert IST genau das Beschriftungswort
#
# "geheim123" hat kein Leerzeichen und ist kein Beschriftungswort; auch
# "geheimnis" faellt durch. Beides ist geeicht.
BESCHRIFTUNGSWORT = (b'passwort', b'password', b'kennwort', b'passphrase',
                     b'passwoord', b'mot de passe', b'contrasena')


def ist_beschriftungswert(treffer):
    i = min((treffer.find(z) for z in (b'"', b"'") if treffer.find(z) >= 0),
            default=-1)
    if i < 0:
        return False
    wert = treffer[i + 1:].strip()
    if b' ' in wert:
        return True
    return wert.lower() in BESCHRIFTUNGSWORT


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

# ---- Vorlauf: welche Anschriften gehoeren zum Urhebervermerk? --------
urheberadressen = set()
for w, _, ds in os.walk(ORDNER):
    for d in ds:
        p = os.path.join(w, d)
        try:
            b = open(p, 'rb').read()
        except Exception:
            continue
        if b'\x00' in b:
            continue
        lizenzdatei = os.path.splitext(d)[0].upper() in LIZENZDATEI
        for m in re.finditer(muster[0][1], b):
            a, e = zeilenrand(b, m.start())
            if lizenzdatei or any(x in b[a:e].lower() for x in URHEBERWORT):
                urheberadressen.add(m.group(0))

funde = []
pb_zugel = []
beschriftungen = 0
beispiele = 0
platzhalter = 0
urheber = 0
mailplatz = 0
macplatz = 0
fassungen = 0
namensdienste = 0
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
                if name == 'E-Mail' and tr in urheberadressen:
                    urheber += 1
                    continue
                if name == 'E-Mail' and ist_mail_platzhalter(tr):
                    mailplatz += 1
                    continue
                if name == 'MAC' and (tr.upper().endswith(MAC_PLATZHALTER_ENDE)
                                      or tr.upper() in MAC_PLATZHALTER_GANZ):
                    macplatz += 1
                    continue
                if name == 'fremde IP':
                    if tr in OEFFENTLICHER_DNS:
                        namensdienste += 1
                        continue
                    za, ze = zeilenrand(b, m.start())
                    if (not ist_gueltige_adresse(tr)
                            or any(x in b[za:ze].lower() for x in FASSUNGSWORT)):
                        fassungen += 1
                        continue
                if name == 'Passwort' and ist_platzhalter(tr):
                    platzhalter += 1
                    continue
                if name == 'Passwort' and ist_schliessendes_zeichen(b, m.start(), tr):
                    platzhalter += 1
                    continue
                if name == 'Passwort' and rp.startswith('templates/lang/') and (
                        BESCHRIFTUNG.search(b[max(0, m.start() - 6):m.start()])
                        or ist_beschriftungswert(tr)):
                    beschriftungen += 1
                    continue
                _id = ausnahme_fuer('Personenbezogenes', rp, '%s:%s' % (
                    name, tr.decode('utf-8', 'replace')))
                if _id:
                    pb_zugel.append(('%s in %s: %s' % (name, d, tr.decode(
                        'utf-8', 'replace')[:34]), _id))
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
if urheber:
    ausnahmen.append('%d Anschrift(en) aus dem Urhebervermerk' % urheber)
if mailplatz:
    ausnahmen.append('%d Platzhalteranschrift(en)' % mailplatz)
if macplatz:
    ausnahmen.append('%d Platzhalter-MAC' % macplatz)
if fassungen:
    ausnahmen.append('%d Fassungs-/Abschnittsnummer(n)' % fassungen)
if namensdienste:
    ausnahmen.append('%d oeffentliche(r) Namensdienst' % namensdienste)
nachsatz = (' - ausgenommen: ' + ', '.join(ausnahmen)) if ausnahmen else ''
melde('Personenbezogenes', not funde,
      ('%d Fund(e), der erste: %s' % (len(funde), funde[0]) if funde
       else 'nichts gefunden') + nachsatz + zugelassen_text(pb_zugel))

# ---------- 6b. Woerter aus der Anonymisierungsliste ----------
#
# ERGAENZT 02.09.2026, nach einem Befund, der bis zum Veroeffentlichen
# durchgelaufen ist: bin/lox_client.py trug an fuenf Stellen den
# Benutzernamen der Anlage - als Testwert in genau der Selbstpruefung, die
# belegen soll, dass 'authwithtoken' WEDER HASH NOCH BENUTZERNAMEN zeigt.
# Die Pruefung, die den Namen schuetzt, lieferte ihn mit aus. Und die
# Freigabepruefung meldete dazu "Personenbezogenes: nichts gefunden" - eine
# Zusicherung, die niemand gemessen hatte.
#
# Die Muster in Pruefung 6 suchen Adressen, Marken und Kennungen. Ein
# KLARNAME hat keine Form, an der man ihn erkennt; er steht in einer Liste,
# und die gab es die ganze Zeit: Werkzeuge/anonymisierung_woerter.txt.
# Gelesen haben sie bis heute nur vier linienbezogene Pruefer (au_, skoda_,
# vw_, ww_) - das Freigabetor nicht.
#
# WORTGRENZEN sind Pflicht. Ein Wort der Liste kann der Anfang eines
# gewoehnlichen deutschen Wortes sein (so wie 'Rat' in 'Ratgeber'). Eine Suche ohne
# Grenzen meldet es, und ein Pruefer, der Fehlalarme liefert, wird beim
# dritten Mal abgehakt statt gelesen. Deshalb: Treffer nur, wenn links und
# rechts kein Buchstabe steht.
def anon_woerter():
    """Die Liste, oder eine leere Liste - dann sagt die Meldung das."""
    for kandidat in (os.path.join(HIER, 'anonymisierung_woerter.txt'),
                     os.path.join(os.path.dirname(HIER), 'Werkzeuge',
                                  'anonymisierung_woerter.txt')):
        if os.path.isfile(kandidat):
            aus = []
            for z in io.open(kandidat, encoding='utf-8', errors='replace'):
                z = z.strip()
                if z and not z.startswith('#'):
                    aus.append(z)
            return aus, kandidat
    return [], ''


# FREMDE ORIGINALAUTOREN sind keine Fundstelle. REGELN_2 nennt den Fall
# ausdruecklich: "'<Vorname> Woerstenfeld' und '<Vorname> Fenzl' -
# Originalautoren, deren Nennung die Apache-Lizenz bzw. der Anstand
# verlangt." In Spotpreis aWATTar steht der Name zweimal in der README, im
# Kapitel ueber das Verhaeltnis zum fremden Plugin.
#
# DIE AUSNAHME IST ENG: sie greift nur, wenn dem Vornamen UNMITTELBAR der
# Nachname folgt. Ein einzelner Vorname faellt weiter durch - und das
# ist der Fall, der schuetzenswert ist. Geeicht in beide Richtungen in
# freigabe_eichung.py.
#
# Und sie ist LAUT: was ausgenommen wurde, wird gezaehlt und gemeldet, wie
# in Pruefung 6. Eine stille Ausnahme waere dasselbe Uebel wie der
# Fehlalarm, nur in der anderen Richtung.
ANON_FREMDAUTOREN = ('Fenzl', 'Woerstenfeld', 'W\u00f6rstenfeld')

anon_liste, anon_datei = anon_woerter()
anon_funde = []
anon_zugel = []
anon_ausgenommen = 0
if anon_liste:
    _GRENZE_L = '(?<![A-Za-zÀ-ɏ])'
    _GRENZE_R = '(?![A-Za-zÀ-ɏ])'
    anon_muster = [(w, re.compile(_GRENZE_L + re.escape(w) + _GRENZE_R, re.I))
                   for w in anon_liste]
    for _w, _, _ds in os.walk(ORDNER):
        for _d in sorted(_ds):
            _p = os.path.join(_w, _d)
            _rp = os.path.relpath(_p, ORDNER).replace(os.sep, '/')
            try:
                _b = open(_p, 'rb').read()
            except OSError:
                continue
            if b'\x00' in _b[:8000]:        # Binaerdatei, etwa ein Symbol
                continue
            _text = _b.decode('utf-8', 'replace')
            for _wort, _mu in anon_muster:
                for _m in _mu.finditer(_text):
                    # Folgt dem Vornamen unmittelbar der Nachname eines
                    # fremden Originalautors, ist es kein Befund.
                    _danach = _text[_m.end():_m.end() + 24]
                    if any(_danach.startswith(' ' + _n)
                           for _n in ANON_FREMDAUTOREN):
                        anon_ausgenommen += 1
                        continue
                    _za = _text.rfind('\n', 0, _m.start()) + 1
                    _ze = _text.find('\n', _m.end())
                    _id = ausnahme_fuer('Anonymisierung', _rp, _wort,
                                        _text[_za:_ze if _ze >= 0 else None])
                    if _id:
                        anon_zugel.append(('%s:%d %s' % (
                            _rp, _text.count('\n', 0, _m.start()) + 1, _wort), _id))
                        continue
                    anon_funde.append('%s:%d %s'
                                      % (_rp,
                                         _text.count('\n', 0, _m.start()) + 1,
                                         _wort))

if not anon_liste:
    melde('Anonymisierung', False,
          'anonymisierung_woerter.txt nicht gefunden - '
          'es wurde NICHT auf Klarnamen geprueft')
else:
    anon_zusatz = ((' - ausgenommen: %d Nennung(en) fremder Originalautoren'
                    % anon_ausgenommen) if anon_ausgenommen else '')
    melde('Anonymisierung', not anon_funde,
          (('%d Fund(e), der erste: %s' % (len(anon_funde), anon_funde[0]))
           if anon_funde
           else '%d Wort/Woerter geprueft, keine Fundstelle' % len(anon_liste))
          + anon_zusatz + zugelassen_text(anon_zugel))

# ---------- 7. Gemischte Zeilenenden - ohne Grundlinie messbar ----------
#
# ERGAENZT 31.08.2026. Die Pruefung darunter braucht ein Grundlinien-Archiv
# und meldet ohne eines "entfaellt". Eine Datei, die IN SICH gemischt ist,
# faellt damit durch jedes Raster - gefunden an VolkswagenID, wo
# templates/lang/help_de.ini seit mindestens 0.9.10 neun CRLF und 31 LF
# traegt und trotzdem "0 Beanstandungen" bekam.
#
# Dieser Befund braucht keinen Vergleich: eine Mischung entsteht nur, wenn
# jemand einzelne Zeilen mit dem falschen Werkzeug angefasst hat.
gemischt = []
for w, _, ds in os.walk(ORDNER):
    for d in sorted(ds):
        p = os.path.join(w, d)
        b = open(p, 'rb').read()
        if b'\x00' in b:
            continue
        crlf = b.count(b'\r\n')
        lf = b.count(b'\n') - crlf
        if crlf and lf:
            gemischt.append('%s (CRLF=%d LF=%d)'
                            % (os.path.relpath(p, ORDNER).replace(os.sep, '/'),
                               crlf, lf))
melde('Zeilenenden gemischt', not gemischt,
      'keine Datei mit beiden Arten' if not gemischt
      else '%d Datei(en): %s' % (len(gemischt), ', '.join(gemischt[:4])))

# ---------- 7b. Zeilenenden einheitlich (LF) ----------
#
# ERGAENZT 13.09.2026, Regeln/01 Abschnitt 7: "In einem Plugin-Ordner fuehrt
# jede Textdatei LF." Die Pruefung darunter vergleicht gegen das
# veroeffentlichte Archiv und meldet ohne Grundlinie "entfaellt"; die davor
# findet nur IN SICH gemischte Dateien. Eine Linie, die durchgehend CRLF
# fuehrt, lief durch beide Raster - und genau so war es: 221 Dateien in 40 von
# 49 Linien, am 13.09.2026 gezaehlt.
#
# WARUM EIN AUSNAHMESCHALTER: umgestellt wird je Linie bei ihrer naechsten
# Veroeffentlichung, nicht in einem Sammeldurchgang. Ohne --crlf-erlaubt waere
# diese Zeile in 40 Linien rot, und eine Kette, die ueberall rot ist, liest
# niemand mehr. Mit dem Schalter ist "noch nicht dran" eine benannte
# Entscheidung - dieselbe Form wie --zeilenenden-neu.
#
# Binaerdateien bleiben aussen vor, und zwar nicht nach Endung: PNG tragen die
# Bytefolge 0D 0A in den BILDDATEN (gemessen: icon_128.png einmal,
# icon_512.png fuenfmal). Entschieden wird am Nullbyte, wie in 7.
crlf_erlaubt = set(x.strip() for x in (CRLF_OK or '').split(',') if x.strip())
crlf_dateien = []
crlf_geduldet = []
for w, _, ds in os.walk(ORDNER):
    for d in sorted(ds):
        p = os.path.join(w, d)
        b = open(p, 'rb').read()
        if b'\x00' in b:
            continue
        if not b.count(b'\r\n'):
            continue
        rp = os.path.relpath(p, ORDNER).replace(os.sep, '/')
        (crlf_geduldet if (rp in crlf_erlaubt or os.path.basename(rp) in crlf_erlaubt)
         else crlf_dateien).append(rp)
_zusatz = (' - geduldet: ' + ', '.join(crlf_geduldet)) if crlf_geduldet else ''
# "alle Textdateien LF" UND eine Duldungsliste waere ein Widerspruch in einer
# Zeile. Wo etwas geduldet wird, sagt die Zeile genau das.
if crlf_dateien:
    _text = '%d Datei(en) mit CRLF: %s' % (len(crlf_dateien),
                                           ', '.join(crlf_dateien[:6]))
elif crlf_geduldet:
    _text = 'keine unangemeldete CRLF-Datei'
else:
    _text = 'alle Textdateien LF'
melde('Zeilenenden einheitlich', not crlf_dateien, _text + _zusatz)

# ---------- 8. Zeilenenden gegen die Grundlinie ----------
#
# BERICHTIGT 04.09.2026. Hier stand
#     basis[n.split('/', 1)[1] if '/' in n else n] = z.read(n)
# also ein Abschneiden des ersten Pfadteils OHNE Bedingung. Das ist richtig
# fuer ein von GitHub erzeugtes Archiv (alles haengt unter "<repo>-<tag>/"),
# aber falsch fuer ein mit packen.py gebautes: dort steht plugin.cfg an der
# Wurzel, und aus "templates/lang/language_de.ini" wurde
# "lang/language_de.ini". Der Schluessel traf nicht, "rp not in basis" hat
# die Datei stumm uebersprungen - und die Zeile meldete trotzdem gruen.
#
# Gemessen am 04.09.2026 ueber sieben Linien: verglichen wurden 8 bis 12
# Dateien, richtig waren 22 bis 47. Die Pruefung, die es fuer genau diese
# Fehlerklasse gibt, hat also rund ein Viertel des Plugins angesehen.
# zeilenenden_vergleichen.py macht es seit jeher richtig; von dort kommt die
# Bedingung: abgeschnitten wird NUR, wenn wirklich ALLE Eintraege denselben
# ersten Pfadteil haben - sonst waere es geraten.
#
# Und die Zahl der verglichenen Dateien steht jetzt in der Meldung. "Geprueft
# und in Ordnung" und "nichts gefunden, weil nichts angesehen wurde" sind
# zwei verschiedene Ausgaenge.
if GRUND and os.path.isfile(GRUND):
    z = zipfile.ZipFile(GRUND)
    namen = [n for n in z.namelist() if not n.endswith('/')]
    erste = set(n.split('/')[0] for n in namen if '/' in n)
    kuerzen = len(erste) == 1 and all('/' in n for n in namen)
    basis = {}
    for n in namen:
        basis[n.split('/', 1)[1] if kuerzen else n] = z.read(n)
    z.close()
    abw = []
    gewollt = []
    verglichen = 0
    for w, _, ds in os.walk(ORDNER):
        for d in sorted(ds):
            p = os.path.join(w, d)
            rp = os.path.relpath(p, ORDNER).replace(os.sep, '/')
            b = open(p, 'rb').read()
            if b'\x00' in b or rp not in basis:
                continue
            verglichen += 1
            if stil(b) != stil(basis[rp]):
                eintrag = '%s (%s statt %s)' % (rp, stil(b), stil(basis[rp]))
                (gewollt if rp in ERLAUBT_STIL else abw).append(eintrag)
    # Eine genannte Datei, die sich gar nicht geaendert hat, ist ein
    # Tippfehler oder ein Rest aus einer frueheren Fassung - sie wird
    # benannt. Wortgleich mit packen.py; sonst haetten beide Werkzeuge
    # denselben Schalter mit verschiedener Strenge.
    ungenutzt = sorted(ERLAUBT_STIL - set(g.split(' ')[0] for g in gewollt))
    # Eine leere Menge ist kein Bestehen: traefe KEINE Datei zu, waere das
    # ein Messfehler (falsche Grundlinie, falscher Ordner), kein Ergebnis.
    melde('Zeilenenden', bool(verglichen) and not abw and not ungenutzt,
          '%d von %d Datei(en) der Grundlinie verglichen, gegen %s%s%s%s'
          % (verglichen, len(basis), os.path.basename(GRUND),
             '' if not abw else ' - ABWEICHUNG ' + ', '.join(abw),
             '' if not gewollt else ' - GEWOLLT umgestellt: ' + ', '.join(gewollt),
             '' if not ungenutzt else ' - --zeilenenden-neu nennt '
             + ', '.join(ungenutzt) + ', dort aendert sich aber nichts')
          if verglichen else
          'KEINE Datei wiedergefunden in %s - Grundlinie oder Ordner passt nicht'
          % os.path.basename(GRUND))
else:
    melde('Zeilenenden', None, 'keine Grundlinie angegeben - nicht gemessen')

# ---------- 9. Das Archiv ----------
if ARCHIV and os.path.isfile(ARCHIV):
    z = zipfile.ZipFile(ARCHIV)
    n = z.namelist()
    dateien = [x for x in n if not x.endswith('/')]
    anders = [x for x in dateien
              if not os.path.isfile(os.path.join(ORDNER, x.replace('/', os.sep)))
              or open(os.path.join(ORDNER, x.replace('/', os.sep)), 'rb').read() != z.read(x)]
    tiefer = [x for x in dateien if x.count('/') and x.endswith('plugin.cfg')]
    wurzel = 'plugin.cfg' in dateien
    # NEU 31.10.2026: Der Installer liest plugin.cfg mit Config::Simple, und
    # das macht aus jedem Wert mit Komma eine Liste - ARCHITECTURE=aarch64,x86_64
    # brach am LoxBerry 4.0.0.15 mit "wrong architecture ARRAY(0x...)" ab
    # (Audioserver NG 0.9.0). In Anfuehrungszeichen bleibt der Wert Text.
    komma = []
    if wurzel:
        for i, zl in enumerate(z.read('plugin.cfg').decode('utf-8', 'replace').splitlines(), 1):
            m = re.match(r'\s*([A-Za-z0-9_]+)\s*=\s*(.*?)\s*$', zl)
            if m and ',' in m.group(2) and not re.match(r'^"[^"]*"$', m.group(2)):
                komma.append('%s (Zeile %d)' % (m.group(1), i))
    z.close()
    ok = not anders and not tiefer and wurzel and not komma
    melde('Archiv', ok, '%d Eintraege, %d Byte%s'
          % (len(n), os.path.getsize(ARCHIV),
             '' if ok else ' - ' + (('abweichend: ' + ', '.join(anders[:3])) if anders
                                    else ('doppelt gepackt' if tiefer else 'plugin.cfg fehlt an der Wurzel'
                                          if not wurzel else 'plugin.cfg: Wert mit Komma ohne Anfuehrungszeichen '
                                          '(Config::Simple macht eine Liste daraus): ' + ', '.join(komma)))))
else:
    melde('Archiv', True, 'kein Archiv angegeben - entfaellt')

# ---------- Urteil ----------
#
# Ein Strich ist KEINE Beanstandung - aber er wird auch nicht verschwiegen.
# "Alles bestanden" darf nur dastehen, wenn wirklich alles gemessen wurde;
# sonst liest sich ein nicht durchgefuehrter Test wie ein bestandener.
schlecht = [n for n, ok in ergebnis if ok is False]
strich = [n for n, ok in ergebnis if ok is None]
print('\n== %d Pruefungen, %d Beanstandungen%s%s =='
      % (len(ergebnis), len(schlecht),
         '' if not strich else (', %d nicht feststellbar' % len(strich)),
         '' if not AUSNAHMEN_BENUTZT else
         (', %d Ausnahme(n) zugelassen' % len(AUSNAHMEN_BENUTZT))))
# Jede zugelassene Ausnahme steht mit Grund und Entscheidung im Bericht;
# eine eingetragene, die nicht mehr gebraucht wird, ebenso (dann gehoert sie
# aus der Datei).
for _a in AUSNAHMEN:
    if _a['id'] in AUSNAHMEN_BENUTZT:
        print('   zugelassen (Ausnahme %s, %s, %s): %s %s - %d Fundstelle(n); %s'
              % (_a['id'], _a['datum'], _a['entscheidung'], _a['pruefung'],
                 _a.get('pfad') or _a.get('pfad_muster')
                 or ', '.join(sorted(_a.get('pfade', {}))),
                 AUSNAHMEN_BENUTZT[_a['id']], _a['begruendung']))
    else:
        print('   Ausnahme %s (%s) nicht gebraucht - nichts zugelassen'
              % (_a['id'], _a['pruefung']))
if AUSNAHMEN_HINWEIS:
    print('   ' + AUSNAHMEN_HINWEIS)
if strich:
    print('   nicht gemessen: %s' % ', '.join(strich))
if schlecht:
    print('   offen: %s' % ', '.join(schlecht))
    sys.exit(1)
print('   Alles bestanden%s.' % ('' if not strich else ', was messbar war'))
