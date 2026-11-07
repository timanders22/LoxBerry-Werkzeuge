#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft die BEZEICHNUNGEN in den Loxone-Importvorlagen - am Erzeugnis.

Aufruf:
    python vorlagen_pruefen.py                  alle Linien (hoechster Ordner)
    python vorlagen_pruefen.py <Pluginordner>   eine Linie
    python vorlagen_pruefen.py --datei X.xml    eine fertige Vorlage messen
        [--alle]               jede Fundstelle einzeln statt nur der Zahl
        [--behalten <ordner>]  die erzeugten Vorlagen dort ablegen

Rueckgabe 0, wenn kein BEFUND steht. Hinweise aendern den Rueckgabewert nicht.

WARUM ES DAS GIBT
-----------------
Die Plugins liefern keine XML mit; sie bauen die Vorlage beim Knopfdruck
zusammen. Was der Anwender nach dem Import in Loxone Config liest, steht
darum nirgends als Zeichenkette in einer Datei. Jede Pruefung, die den
Quelltext liest, misst deshalb etwas anderes als das Erzeugnis - gemessen
am 05.09.2026:

    Linie               umschrift_pruefen.py am Quelltext   erzeugte Vorlage
    Spotpreis-aWATTar                    0 Fundstellen                    28
    FerienFeiertage                      0 Fundstellen                    18
    AWM-Abfuhr                           4 Fundstellen                    28
    Robonect                             2 Fundstellen                    17

Nicht Nachlaessigkeit, sondern Bauform: diese Linien setzen den Text in der
Vorlagenfunktion zusammen und nicht in einer Feldtabelle mit den Schluesseln
'kurz'/'text'/'title'/'comment', die umschrift_pruefen.py ansieht.

WAS GEPRUEFT WIRD (Regeln/07, Abschnitte zu Comment und Titel)
--------------------------------------------------------------
BEFUND:
  b1  nicht wohlgeformt oder kein gueltiges UTF-8
  b2  '=' im Titel eines Ausgangs (aus '&lp=1' wurde 'EVCC_MODUS_LP=1')
  b3  derselbe Titel zweimal IN EINER Datei
  b4  Titel leer
  b5  Ausgang ohne Comment, dessen Titel ein Bezeichner ist (Punkt,
      Unterstrich oder durchgehend gross) - dann steht in Loxone Config
      z.B. 'Input.ContextMenu' als Anzeigename
Hinweis:
  h1  Comment laenger als 40 Zeichen: er wird zum Kachelnamen, nicht zur
      Dokumentation. Ueber etwa 40 Zeichen ist es ein Satz.
  h2  Ausgang ohne Comment mit lesbarem Titel (dann zeigt Config den Titel)
  h3  ASCII-Umschrift (faellig, naechste, Maeher) in Titel oder Comment
  h4  analoger HTTP-Eingang ohne 'Unit' - sonst steht eine nackte Zahl da
  h5  Titel und Comment wortgleich
  h6  Titel kommt in mehr als einer LINIE vor (nur im Gesamtlauf; die
      Bausteinsuche des Miniservers kennt den Geraeteknoten nicht)

SEIT 01.10.2026 (X-4, Anlass AudiConnect U6/U7 und AnkerSolix-c3)
-----------------------------------------------------------------
Befehle eines Ausgangs (VirtualOutCmd):
  BEFUND   b6  CmdOn UND CmdOff leer - der Ausgang sendet nichts
  BEFUND   b7  Adresse (/ ? =) in CmdOnMethod/CmdOffMethod: AudiConnect bis
               0.9.21 schrieb die Adresse dorthin, CmdOn fehlte (16 Befehle)
  Hinweis  h7  Methode fehlt oder ist nicht GET/POST/PUT/DELETE (BYD: "0";
               Config-Ausfuhr schreibt GET, ob "0" wirkt, ist ungemessen)
  Hinweis  h8  Platzhalter in <..>, der nicht <v> oder <v.N> ist; stehen
               gebliebener Erzeuger-Platzhalter ([LOXNAME], %s, {host}, $x)
  Hinweis  h9  Wurzeladresse + Befehl ergibt einen anderen Rechner (volle URL
               im Befehl, oder Befehl ohne fuehrenden '/'): Config haengt an
  Hinweis  h10 analoger Ausgang ohne <v> im Befehl - der Wert geht nicht mit
  Hinweis  h11 Endpunkt: /plugins/<x>/ ist nicht FOLDER aus plugin.cfg, oder
               die Datei fehlt in webfrontend/html (admin/: htmlauth). Auch
               fuer die Adresse eines VirtualInHttp. Nur im Linienlauf.
Wurzel:
  Hinweis  h12 kein HintText-Attribut (leer ist die Ausfuhrform von Config
               und bleibt still: 61 von 71 Vorlagen); HintText ueber 500 Zeichen
  Hinweis  h13 Info fehlt/steht nicht zuerst, templateType passt nicht zur
               Wurzel (1 UDP-Eingang, 2 HTTP-Eingang, 3 Ausgang), ohne minVersion
Einheit:
  h4 gilt jetzt auch fuer den UDP-Eingang; Hinweis h14: Unit ohne <v>
  (Config zeigt dann die Einheit ohne Wert). In der Kurzausgabe stehen die
  Eingaenge ohne Unit je Linie mit Namen ("ohne Unit: ...").
Mehr Vorlagen: der Treiber laeuft ein zweites Mal mit Musterwerten (siehe
vorlagen_treiber.php, MUSTERWERTE=1): jede Art, die eine Vorlagenfunktion
selbst kennt, und Pflichtargumente mit bekanntem Namen. Bestand 01.10.2026:
71 -> 105 Vorlagen, 36 -> 44 Linien. Solche Dateien heissen <LINIE>__<fn>__m-...
und sind in der Kopfzeile gezaehlt ("davon N nur mit Musterwerten").
Geeicht: Pruefung-Durchgang-2026-09-29/x4_werkzeug/eichung/eichen.py (je
Pruefung eine Vorlage mit und ohne Mangel, zwei Mini-Plugins fuer Endpunkt
und Musterwerte); AudiConnect 0.9.21 ergibt 43 BEFUND (b6/b7), 0.9.23 keinen.

WARUM h1 ein HINWEIS IST UND KEIN BEFUND
----------------------------------------
Ueber den Bestand gemessen (05.09.2026): 481 von 1380 Befehlen tragen einen
Comment ueber 40 Zeichen, verteilt auf 29 von 36 Linien. Ein Tor, das bei
vier Fuenfteln des Bestands rot wird, wird abgeschaltet. Sobald die Zahl
klein ist, gehoert daraus ein BEFUND - dafuer ist unten nur die Marke zu
tauschen.

WAS DIESES WERKZEUG NICHT MISST
-------------------------------
Gemessen wird die Vorlage OHNE eingerichtete Geraete: der Treiber ruft nur
Funktionen ohne Pflichtargument. 13 Linien liefern damit nichts (sieben
verlangen Argumente, drei brauchen ein eingerichtetes Geraet, drei haben
gar keine Vorlagenfunktion) - sie werden als 'keine Vorlage' gefuehrt, nicht
als 'in Ordnung'. Mit eingerichteten Geraeten entstehen MEHR Befehle,
nicht andere.

Es ist NICHT Teil des Freigabetors. Wer es dort einhaengt, eicht vorher ueber
den ganzen Bestand (Regeln/02, "Werkzeugaenderung eng fassen").

GEEICHT (05.09.2026, in beide Richtungen)
-----------------------------------------
  * KODI-NG meldet b5 26 mal (Titel 'Input.Back' & Co.), BYD-Autos schweigt.
  * Aus einer erzeugten Vorlage ein 'Unit' entfernt -> h4 meldet sie; im
    Original schweigt die Pruefung.
  * 'Automatik' steht in BatterieBMS und Robonect -> h6; alle uebrigen 1378
    Titel sind ueber die Linien hinweg eindeutig.
  * Die Ausfuhren von Loxone Config selbst (VI_/VO_-Dateien im
    Arbeitsordner) laufen ohne b1 durch.
"""

import collections
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

HIER = Path(__file__).resolve().parent
ARBEIT = HIER.parent
TREIBER = HIER / 'vorlagen_treiber.php'

sys.path.insert(0, str(HIER))
import rendern                      # PHPS, LB, VORLAUF - eine Quelle
import umschrift_pruefen as UM      # die Wortliste steht dort, nicht hier

GRENZE = 40          # Zeichen; Regeln/07: "ueber etwa 40 Zeichen ist ein Satz"

# Ein Titel, der wie ein Bezeichner aussieht: Punkt, Unterstrich, oder
# durchgehend Grossbuchstaben. 'Maeher starten' ist keiner, 'Input.Back' schon.
BEZEICHNER = re.compile(r'^[A-Z0-9_.]+$|[._]')


# ---------------------------------------------------------------- erzeugen

def hoechste_ordner():
    """Je Linie der Ordner mit der hoechsten Fassung."""
    def num(s):
        return tuple(int(x) for x in re.findall(r'\d+', s))
    linien = {}
    for d in ARBEIT.glob('LoxBerry-Plugin-*'):
        m = re.fullmatch(r'LoxBerry-Plugin-(.+)-(\d+\.\d+\.\d+)', d.name)
        if d.is_dir() and m:
            linien.setdefault(m.group(1), []).append((num(m.group(2)), d))
    return [(k, max(v)[1]) for k, v in sorted(linien.items())]


def erzeugen(linie, ordner, ziel):
    """Die Vorlagen einer Linie erzeugen. Gibt {dateiname: bytes} zurueck.

    Geschrieben wird NUR nach ziel - in den Pluginordner faellt nichts.
    """
    libs = [f for f in ordner.rglob('*_lib.php')
            if 'webfrontend' in str(f) or '/bin/' in f.as_posix()]
    if not libs:
        return {}, 'keine Bibliothek'
    # Seit 01.10.2026 (X-4) der Ordnername aus plugin.cfg: vorher stand hier
    # der Linienname klein ohne Bindestrich, in 17 von 49 Linien ein anderer
    # als FOLDER (Spotpreis-aWATTar -> 'spotpreis'). Die Endpunktpruefung
    # vergleicht die Adressen der Vorlage mit FOLDER; mit dem erfundenen Namen
    # haette sie den Pruefstand gemessen.
    kurz = plugin_ordnername(linie, ordner)
    umg = dict(os.environ)
    umg.update({
        'LBHOMEDIR': str(rendern.LB),
        'LBPPLUGINDIR': kurz,
        'LBPCONFIGDIR': str(rendern.LB / 'config/plugins' / kurz),
        'LBPLOGDIR': str(rendern.LB / 'log/plugins' / kurz),
        'LBPDATADIR': str(rendern.LB / 'data/plugins' / kurz),
        'LBPHTMLAUTHDIR': str(ordner / 'webfrontend/htmlauth'),
        'LBPHTMLDIR': str(ordner / 'webfrontend/html'),
        'LBPTEMPLATEDIR': str(ordner / 'templates'),
        'LBPBINDIR': str(ordner / 'bin'),
        'ZIEL': str(ziel), 'LINIE': linie,
    })
    for k in ('LBPCONFIGDIR', 'LBPLOGDIR', 'LBPDATADIR'):
        Path(umg[k]).mkdir(parents=True, exist_ok=True)
    php = rendern.PHPS[0][1]
    ruf = [php, '-n',
           '-d', 'include_path=.;' + str(rendern.LB / 'libs' / 'phplib'),
           # Schraegstriche: ein 8.3-Kurzpfad (...~1) und ein Backslash zerbrechen
           # den Wert eines -d-Schalters (Messfalle dieses Rechners).
           '-d', 'auto_prepend_file=' + str(rendern.VORLAUF).replace(chr(92), '/'),
           '-d', 'display_errors=0', '-d', 'date.timezone=Europe/Berlin',
           '-d', 'extension_dir=' + str(Path(php).parent / 'ext'),
           '-d', 'extension=curl', '-d', 'extension=openssl',
           '-d', 'extension=mbstring', '-d', 'extension=sockets',
           '-d', 'extension=fileinfo',
           # Absolute Pfade: gearbeitet wird IM Pluginordner (cwd), ein
           # relativer Pfad zeigt von dort aus ins Leere.
           str(TREIBER)] + [str(f.resolve()) for f in libs]
    try:
        subprocess.run(ruf, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', cwd=str(ordner), env=umg, timeout=180)
    except Exception as ex:
        return {}, 'Treiber gescheitert: %s' % ex
    # Zweiter Lauf mit Musterwerten (X-4), eigener Prozess: siehe Kopf des
    # Treibers. Scheitert er, bleibt der Grundlauf gueltig.
    umg['MUSTERWERTE'] = '1'
    try:
        subprocess.run(ruf, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', cwd=str(ordner), env=umg, timeout=180)
    except Exception:
        pass
    aus = {}
    for f in sorted(Path(ziel).glob(linie + '__*.xml')):
        aus[f.name] = f.read_bytes()
    return aus, ''


def plugin_ordnername(linie, ordner):
    """FOLDER aus plugin.cfg; fehlt er, der fruehere Kurzname."""
    try:
        for z in (ordner / 'plugin.cfg').read_text(encoding='utf-8', errors='replace').splitlines():
            if z.startswith('FOLDER='):
                w = z.split('=', 1)[1].strip().strip('"')
                if w:
                    return w
    except OSError:
        pass
    return linie.lower().replace('-', '')


def ist_muster(name):
    """Vorlage aus dem Musterwert-Lauf (Dateiname <LINIE>__<fn>__m-...)."""
    return '__m-' in name


def entdoppeln(dateien):
    """Gleiche Inhalte zusammenfassen.

    Noetig, weil manche Linien eine Paketfunktion haben, die dieselben
    Vorlagen noch einmal liefert (marstek_vorlage und marstek_vorlagen_alle).
    Ohne das meldete der erste Lauf am 05.09.2026 30 doppelte Titel, die es
    im Plugin nicht gibt - gemessen waere der Treiber gewesen, nicht das
    Plugin.
    """
    gesehen, rein = {}, {}
    # Grundlauf zuerst: eine Musterwert-Vorlage, die es schon ohne Argument
    # gibt, faellt weg - nicht umgekehrt (X-4).
    for name in sorted(dateien, key=lambda n: (ist_muster(n), n)):
        roh = dateien[name]
        if roh in gesehen:
            continue
        gesehen[roh] = name
        rein[name] = roh
    return rein


# ----------------------------------------------------------------- messen

METHODEN = ('GET', 'POST', 'PUT', 'DELETE')
INFO_SOLL = {'VirtualInUdp': '1', 'VirtualInHttp': '2', 'VirtualOut': '3'}
HINT_GRENZE = 500    # Zeichen; Bestand 01.10.2026: laengster HintText 294
# Loxone-Platzhalter im Befehl: <v> und <v.N> (Regeln/07). Alles andere in
# spitzen Klammern kennt Config nicht und schickt es woertlich.
LOX_PLATZHALTER = re.compile(r'<v(?:\.\d+)?>')
# Platzhalter eines Erzeugers, die stehen geblieben sind ([LOXNAME], %s, {host})
FREMD_PLATZHALTER = re.compile(r'%[sd]|\{[A-Za-z_]+\}|\[[A-Z_]{3,}\]|\$[A-Za-z_]\w*|__[A-Z]+__')


def _gegenstelle(url):
    """Rechner:Port einer http-Adresse, klein; '' wenn keine http-Adresse."""
    try:
        u = urllib.parse.urlsplit(url)
    except ValueError:
        return None
    if u.scheme.lower() not in ('http', 'https'):
        return ''
    return u.netloc.lower()


def endpunkt_pruefen(url, ordner, folder):
    """Zeigt eine http-Adresse auf den Endpunkt DIESES Plugins? Liefert Text oder ''."""
    try:
        pfad = urllib.parse.urlsplit(url).path
    except ValueError:
        return ''
    m = re.match(r'^/(admin/)?plugins/([^/]+)/?(.*)$', pfad)
    if not m:
        return ''
    # Linien, die den Ordner aus dem Ablageort der Bibliothek ableiten
    # (AnkerSolix: basename(dirname(__FILE__))), sagen auf dem Pruefstand
    # 'html' - am Geraet liegt die Datei in .../plugins/<ordner>/. Das misst
    # den Pruefstand, nicht das Plugin: kein Hinweis (gemessen 01.10.2026).
    if folder and m.group(2) != folder and m.group(2) not in ('html', 'htmlauth', 'bin'):
        return 'Adresse zeigt auf /plugins/%s/, der Pluginordner heisst %s' % (m.group(2), folder)
    datei = m.group(3)
    if ordner is None or not datei:
        return ''
    basis = ordner / 'webfrontend' / ('htmlauth' if m.group(1) else 'html')
    if not (basis / datei).is_file():
        return 'Endpunkt %s%s fehlt im Plugin' % ('admin/' if m.group(1) else '', datei)
    return ''


def messen(dateien, ordner=None, folder=None):
    """(marke, text)-Liste fuer die Vorlagen EINER Linie, dazu die Titel.

    ordner/folder nur im Linienlauf: dann wird auch geprueft, ob die Adressen
    auf den Endpunkt der Linie zeigen (Datei vorhanden, Ordnername).
    """
    aus = []
    titel_alle = []
    for name in sorted(dateien):
        roh = dateien[name]
        try:
            roh.decode('utf-8')
        except UnicodeDecodeError as e:
            aus.append(('BEFUND', '%s: kein gueltiges UTF-8 (%s)' % (name, e)))
            continue
        try:
            baum = ET.fromstring(roh)
        except ET.ParseError as e:
            aus.append(('BEFUND', '%s: nicht wohlgeformt (%s)' % (name, e)))
            continue
        ist_ausgang = baum.tag.startswith('VirtualOut')
        in_datei = collections.Counter()
        # --- Wurzel: HintText und Info (X-4, AudiConnect U7) ---------------
        if baum.tag in INFO_SOLL:
            ht = baum.get('HintText')
            if ht is None:
                aus.append(('Hinweis', '%s: Wurzel ohne HintText' % name))
            elif len(ht) > HINT_GRENZE:
                aus.append(('Hinweis', '%s: HintText der Wurzel %d Zeichen'
                            % (name, len(ht))))
            kinder = list(baum)
            if not kinder or kinder[0].tag != 'Info':
                aus.append(('Hinweis', '%s: Info-Element fehlt oder steht nicht zuerst'
                            % name))
            else:
                tt = kinder[0].get('templateType')
                if tt != INFO_SOLL[baum.tag]:
                    aus.append(('Hinweis', '%s: Info templateType=%s an %s (soll %s)'
                                % (name, tt, baum.tag, INFO_SOLL[baum.tag])))
                if not kinder[0].get('minVersion'):
                    aus.append(('Hinweis', '%s: Info ohne minVersion' % name))
        adresse = baum.get('Address') or ''
        endpunkte = collections.Counter()
        if baum.tag == 'VirtualInHttp' and adresse:
            t = endpunkt_pruefen(adresse, ordner, folder)
            if t:
                endpunkte[t] += 1
        for k in baum.iter():
            wurzel = not k.tag.endswith('Cmd')
            titel = (k.get('Title') or '')
            komm = (k.get('Comment') or '')
            # Umschrift gilt fuer Wurzel wie Befehl - beides sieht der Anwender
            for feld, wert in (('Titel', titel), ('Comment', komm)):
                if not wert:
                    continue
                tr = {}
                UM.woerter_pruefen(wert, tr, name)
                for w in sorted(tr):
                    aus.append(('Hinweis', '%s: ASCII-Umschrift "%s" im %s von %s'
                                % (name, w, feld, titel or '(Wurzel)')))
            if wurzel:
                continue
            in_datei[titel] += 1
            titel_alle.append(titel)
            if not titel.strip():
                aus.append(('BEFUND', '%s: Befehl ohne Titel (Comment "%s")'
                            % (name, komm[:40])))
            if ist_ausgang and '=' in titel:
                aus.append(('BEFUND', '%s: "=" im Titel eines Ausgangs: %s'
                            % (name, titel)))
            if len(komm) > GRENZE:
                aus.append(('Hinweis',
                            '%s: Comment %d Zeichen (wird zum Kachelnamen): %s -> "%s"'
                            % (name, len(komm), titel, komm[:60])))
            if not komm.strip() and k.tag == 'VirtualOutCmd':
                if BEZEICHNER.search(titel):
                    aus.append(('BEFUND',
                                '%s: Ausgang ohne Comment, Titel ist ein Bezeichner: %s'
                                % (name, titel)))
                else:
                    aus.append(('Hinweis',
                                '%s: Ausgang ohne Comment - Config zeigt den Titel: %s'
                                % (name, titel)))
            if komm.strip() and komm.strip() == titel.strip():
                aus.append(('Hinweis', '%s: Titel und Comment wortgleich: %s'
                            % (name, titel)))
            # Unit nur beim ANALOGEN Eingang: an einem digitalen Befehl ist
            # keine Einheit sinnvoll (gemessen: 17 der 184 Faelle digital).
            # Seit 01.10.2026 auch der UDP-Eingang (X-4, AnkerSolix-c3).
            if (k.tag in ('VirtualInHttpCmd', 'VirtualInUdpCmd')
                    and k.get('Analog') == 'true'):
                unit = k.get('Unit') or ''
                if not unit.strip():
                    aus.append(('Hinweis', '%s: analoger Eingang ohne Unit: %s'
                                % (name, titel)))
                elif '<v' not in unit:
                    # Regeln/07: Unit="<v.1> <Einheit>" - ohne Platzhalter
                    # zeigt Config die Einheit, aber keinen Wert.
                    aus.append(('Hinweis', '%s: Unit ohne <v>-Platzhalter: %s -> "%s"'
                                % (name, titel, unit[:20])))
            if k.tag == 'VirtualOutCmd':
                aus.extend(ausgang_pruefen(name, k, titel, adresse, ordner,
                                           folder, endpunkte))
        for t, n in sorted(endpunkte.items()):
            aus.append(('Hinweis', '%s: %s (%dx)' % (name, t, n)))
        for t, n in sorted(in_datei.items()):
            if n > 1:
                aus.append(('BEFUND', '%s: Titel %d mal in DERSELBEN Datei: %s'
                            % (name, n, t)))
    return aus, titel_alle


def ausgang_pruefen(name, k, titel, adresse, ordner, folder, endpunkte):
    """CmdOn/CmdOff eines VirtualOutCmd (X-4, Anlass AudiConnect U6).

    BEFUND nur, wo es eindeutig ist: kein Befehl in beiden Feldern (der
    Ausgang sendet nichts) und eine Adresse im Methodenfeld (AudiConnect bis
    0.9.21: CmdOnMethod="/plugins/...", CmdOn fehlte). Alles andere Hinweis.
    """
    aus = []
    on = (k.get('CmdOn') or '').strip()
    off = (k.get('CmdOff') or '').strip()
    if not on and not off:
        aus.append(('BEFUND', '%s: Ausgang ohne CmdOn und CmdOff (sendet nichts): %s'
                    % (name, titel)))
    for feld in ('CmdOnMethod', 'CmdOffMethod'):
        v = k.get(feld)
        befehl = on if feld == 'CmdOnMethod' else off
        if v is not None and re.search(r'[/?=]', v):
            aus.append(('BEFUND', '%s: Adresse in %s statt im Befehl: %s'
                        % (name, feld, titel)))
        elif v is None:
            aus.append(('Hinweis', '%s: %s fehlt, Ausfuhrform GET: %s'
                        % (name, feld, titel)))
        elif v.strip().upper() not in METHODEN and (v.strip() or befehl):
            aus.append(('Hinweis', '%s: %s ist keine Methode der Ausfuhr (%s): %s'
                        % (name, feld, v[:10], titel)))
    for feld, wert in (('CmdOn', on), ('CmdOff', off)):
        if not wert:
            continue
        for ph in re.findall(r'<[^<>]*>', wert):
            if not LOX_PLATZHALTER.fullmatch(ph):
                aus.append(('Hinweis', '%s: unbekannter Platzhalter %s in %s: %s'
                            % (name, ph[:20], feld, titel)))
        m = FREMD_PLATZHALTER.search(wert)
        if m:
            aus.append(('Hinweis', '%s: nicht ersetzter Platzhalter %s in %s: %s'
                        % (name, m.group(0)[:20], feld, titel)))
        # Config haengt den Befehl an die Adresse der Wurzel. Aendert das den
        # Rechner, geht der Befehl woandershin (volle URL im Befehl, oder ein
        # Befehl ohne fuehrenden Schraegstrich an 'http://loxberry').
        vorn = _gegenstelle(adresse)
        if vorn:
            if _gegenstelle(adresse + wert) != vorn:
                aus.append(('Hinweis',
                            '%s: Adresse + %s ergibt eine andere Gegenstelle: %s'
                            % (name, feld, titel)))
            else:
                t = endpunkt_pruefen(adresse + wert, ordner, folder)
                if t:
                    endpunkte[t] += 1
    if k.get('Analog') == 'true' and '<v' not in on + off:
        aus.append(('Hinweis', '%s: analoger Ausgang ohne <v> im Befehl: %s'
                    % (name, titel)))
    return aus


# ----------------------------------------------------------------- ausgabe

def bericht(name, funde, zahl_dateien, zahl_befehle, einzeln, muster=0):
    b = sum(1 for m, _ in funde if m == 'BEFUND')
    h = len(funde) - b
    print('%-42s %2d Vorlage(n) %4d Befehle   %s%s%s'
          % (name[:42], zahl_dateien, zahl_befehle,
             ('%d BEFUND' % b) if b else '0 BEFUND',
             (', %d Hinweis' % h) if h else '',
             ('   (davon %d Vorlage(n) nur mit Musterwerten)' % muster) if muster else ''))
    if not einzeln:
        # AnkerSolix-c3: die Eingaenge ohne Unit je Linie mit Namen, nicht
        # nur als Zahl - sie werden je Linie angesehen.
        ohne_unit = [t.rsplit('ohne Unit: ', 1)[1] for m, t in funde
                     if 'analoger Eingang ohne Unit: ' in t]
        if ohne_unit:
            print('      ohne Unit: %s' % ', '.join(ohne_unit[:12])
                  + (' ...' if len(ohne_unit) > 12 else ''))
        art = collections.Counter()
        for m, t in funde:
            kurz = t.split(': ', 1)[1] if ': ' in t else t
            kurz = re.sub(r'[:"].*$', '', kurz).strip()
            # Zahlen aus der Klasse nehmen, sonst steht jede Comment-Laenge
            # als eigene Zeile da ("Comment 41 Zeichen", "Comment 42 Zeichen").
            kurz = re.sub(r'\b\d+\b', 'N', kurz)
            art[(m, kurz[:52])] += 1
        for (m, k), n in sorted(art.items()):
            print('      %-8s %3dx  %s' % (m + ':', n, k))
    else:
        for m, t in funde:
            print('      %-8s %s' % (m + ':', t))
    return b


def main(argv):
    einzeln = '--alle' in argv
    argv = [a for a in argv if a != '--alle']
    behalten = None
    if '--behalten' in argv:
        i = argv.index('--behalten')
        behalten = Path(argv[i + 1])
        behalten.mkdir(parents=True, exist_ok=True)
        del argv[i:i + 2]

    if '--datei' in argv:
        i = argv.index('--datei')
        p = Path(argv[i + 1])
        dateien = {p.name: p.read_bytes()}
        funde, titel = messen(dateien)
        n = sum(1 for m, _ in funde if m == 'BEFUND')
        bericht(p.name, funde, 1, len(titel), True)
        return 1 if n else 0

    if argv:
        ziele = []
        for a in argv:
            d = Path(a)
            if not d.is_dir():
                print('ABBRUCH: %s ist kein Ordner' % a)
                return 2
            m = re.fullmatch(r'LoxBerry-Plugin-(.+)-(\d+\.\d+\.\d+)', d.name)
            ziele.append((m.group(1) if m else d.name, d))
    else:
        ziele = hoechste_ordner()

    tmp = Path(tempfile.mkdtemp(prefix='vorlagen_'))
    befunde_gesamt = 0
    titel_je_linie = {}
    ohne_vorlage = []
    zahlen = collections.Counter()
    try:
        for linie, ordner in ziele:
            dateien, grund = erzeugen(linie, ordner, tmp)
            dateien = entdoppeln(dateien)
            if not dateien:
                ohne_vorlage.append((linie, grund or 'keine Vorlage ohne Geraet'))
                continue
            if behalten:
                for nm, roh in dateien.items():
                    (behalten / nm).write_bytes(roh)
            funde, titel = messen(dateien, ordner, plugin_ordnername(linie, ordner))
            titel_je_linie[linie] = titel
            zahlen['dateien'] += len(dateien)
            zahlen['befehle'] += len(titel)
            muster = sum(1 for nm in dateien if ist_muster(nm))
            zahlen['muster'] += muster
            befunde_gesamt += bericht(linie, funde, len(dateien), len(titel),
                                      einzeln, muster)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # h6: derselbe Titel in mehreren LINIEN - nur im Gesamtlauf sinnvoll
    if len(titel_je_linie) > 1:
        wo = collections.defaultdict(set)
        for linie, titel in titel_je_linie.items():
            for t in titel:
                wo[t].add(linie)
        mehr = {t: sorted(l) for t, l in wo.items() if len(l) > 1}
        print()
        print('Titel, die in mehr als einer Linie vorkommen: %d' % len(mehr))
        for t, l in sorted(mehr.items()):
            print('      Hinweis: %-28s %s' % (t[:28], ', '.join(l)))

    print()
    print('%d Linien mit Vorlage, %d Vorlagen, %d Befehle, %d BEFUND'
          % (len(titel_je_linie), zahlen['dateien'], zahlen['befehle'], befunde_gesamt))
    if zahlen['muster']:
        print('davon %d Vorlagen nur mit Musterwerten erzeugt (Art-Parameter, '
              'Pflichtargumente; Treiberlauf MUSTERWERTE=1)' % zahlen['muster'])
    if ohne_vorlage:
        print('%d Linien ohne messbare Vorlage (NICHT "in Ordnung"):' % len(ohne_vorlage))
        for l, g in ohne_vorlage:
            print('      %-26s %s' % (l, g))
    return 1 if befunde_gesamt else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
