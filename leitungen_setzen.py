#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Leitungen aus der Baustein-Liste eines Plugins in eine Loxone-Projektdatei eintragen.

Entscheidung Nr. 36, naechster Schritt nach dem Pilot (02.10.2026). Ersetzt die
von Hand eingetragene Zuordnung in ../verbinden.py.

Ablauf: Die Bausteine sind in Loxone Config gesetzt, benannt und gespeichert,
aber (ganz oder teilweise) unverbunden. Das Werkzeug liest die Baustein-Liste
(Reiter "Einbindung in Loxone"), sucht jeden Baustein in der Datei nach Name und
Typ und traegt fuer jede ableitbare Zeile die Leitung ein:

    <Co K="I1" Nc="1" U="<Eingang>">
        <In Input="<Ausgang>"/>
    </Co>

Ohne --schreiben ist es ein Trockenlauf (Tabelle der geplanten Leitungen).
Mit --schreiben ZIEL entsteht eine NEUE Datei; die Eingabedatei wird nie
ueberschrieben. BOM und Zeilenenden bleiben, alles andere bleibt byte-gleich.

Abbruch (Rueckgabe 2) bei: Baustein fehlt, Name mehrdeutig, Typ passt nicht,
Eingang schon verbunden oder nicht genau einmal unverbunden vorhanden,
Ausgang unbekannt, Zelle mit mehreren Wegen ohne --weg.

Neu in 1.1.0 (09.10.2026, Welle X-10):
- Vor dem "=" darf jeder Anschlussname stehen ("V = #1", "Gpwr = #3", "AI1 = ...").
  Er muss genau so (Gross-/Kleinschreibung egal) als <Co K="..."> am Baustein in der
  Projektdatei stehen, sonst Abbruch. "Eingang = #N" ist der Standardeingang.
  I<n>/V<n> bleiben wie in 1.0.0 (V1 am Status -> I1).
- "Konstante <Wert>" ergibt keine Leitung, nur einen Hinweis (Anschluss wird geprueft).
- HTTP-/UDP-Befehle als Quelle: "Ausgang von <Befehl> (#N)", wenn #N eine Zeile
  "Virtueller HTTP-/UDP-Eingang(-Befehl)" ist, und "Eingang <Befehl>", wenn die Liste
  den Namen nicht als Zeile fuehrt, aber genau eine HTTP-/UDP-Zeile hat. Der Befehl
  wird in der Projektdatei nach seinem Titel gesucht (VirtualHttpInCmd/VirtualUdpInCmd),
  die Quelle ist der Eingangsbaustein auf der Seite, der auf ihn verweist (InputRef Ref=).
- "I2 = #10 (negiert)": Leitung und Inv="true" am Eingang (Form wie Config sie speichert).
- "AI1 = #7" an einem Baustein ohne Anschluss AI1: Anschluss Input1 (Vergleicher), mit Hinweis.
- Zellen mit Zwischenbaustein ohne eigene Listenzeile ("ueber einen Schwellwertschalter")
  bleiben Hinweis, mit eigener Meldung.

Neu in 1.2.0 (09.10.2026, Leitungen-1.2):
- Vorlagen-Eingaenge: "Eingang FW_OK" oder der blosse Name "FW_OK" (mit Unterstrich) ohne
  Listenzeile werden in der Projektdatei gesucht (virtueller Eingang, HTTP-/UDP-Befehl; genauer
  Titel). Fehlt der Titel oder ist er mehrdeutig: Abbruch mit aehnlichen Titeln.
- Zeilennummern mit Buchstaben ("18a", Verweis "#18a") und "18 (optional)" als Zeile 18.
- Status: AI1 ... AI8 wie V1 ... V8 auf I1 ... I8.
- Analogwertvalidierung (Typ Validator): Standardausgang error (Config: E), Eingang inval;
  Config-Beschriftungen V/En/E an diesem Baustein -> inval/enable/error.
- Flankenerkennung (EdgeDetection): Ausgang nach "(steigend)"/"(fallend)" im Listentyp.
- Folgetyp "Ausgangsbefehl <Titel>" in Ketten, und Zeilen "Virtueller Ausgang ... Befehle" mit
  "befehl1, befehl2 ← #9; befehl3 ← #10" (mehrere Folgebausteine nebeneinander).

Neu in 1.3.0 (09.10.2026, Leitungen-1.3; am Musterprojekt in Config gemessen):
- Config-Beschriftungen je Typ: Schwellwertschalter V -> Input; Analogkomparator Ausgang De -> Q;
  Status Ausgang Val -> AQ; Validator V/En/E -> inval/enable/error jetzt in Config gegengeprueft.
- Analogkomparator (AnalogComparator): Standardeingang Input1, Standardausgang Q (blosser Name
  "FW_KRANK" und "I1 = #2" ohne "Ausgang Q von").
- Typnamen "Statusbaustein", "Analogwert-Vergleicher"/"Analogkomparator"; aus den Standardtiteln
  einer von Config gespeicherten Datei (Leer.Loxone) "Treppenlichtschalter", "Alarmanlage",
  "Bewaesserung", "Energiemanager".
- Standardanschluesse nach den Anschlusslisten von Referenz_Bausteine.Loxone/Leer.Loxone fuer
  Groesser/Kleiner/Gleich-Vergleicher, Monoflop, Ein-/Ausschaltverzoegerung, Analogspeicher, Merker
  (nur Eingang) und Treppenlichtschalter.

Neu in 1.3.1 (09.10.2026, Musterprojekt Ultraschall):
- Config-Beschriftungen am Analogspeicher (AMemory): V/Set/Off -> Input/Trigger/Reset.

Neu in 1.3.2 (10.10.2026, Musterprojekt Bewaesserung, in Config abgelesen):
- Aufwaertszaehler (Counter): Eingaenge C/Off -> Trigger/Reset, Ausgang V -> AQ.
- Bewaesserung (Irrigation): Eingaenge Act/Sel/Raf/Off -> A/AIv/Rf/Reset, Ausgang P -> Qp.
- Flankenerkennung (EdgeDetection): Ausgaenge P/On/Off -> Edge/RisingEdge/FallingEdge;
  Analogspeicher Ausgang V -> AQ.

Neu in 1.3.3 (16.10.2026, Analogwertvalidierung):
- Config legt den Eingang enable negiert an (Inv="true"). Eine dort angeschlossene Konstante 1
  kommt als 0 an, und die Validierung prueft Tmc nicht (Loxone-Beschreibung). Eine nicht negierte
  Leitung an enable wird jetzt ohne Inv eingetragen; ist sie schon vorhanden und negiert, Abbruch.

Aufruf siehe ANLEITUNG.md oder --help.
"""
import argparse
import difflib
import html
import os
import re
import sys
import xml.etree.ElementTree as ET

FASSUNG = '1.3.3'


class Abbruch(Exception):
    pass


# ---------------------------------------------------------------------------
# Hilfen
# ---------------------------------------------------------------------------

def glatt(s, tags_weg=False):
    """Leerraum zusammenfassen; bei HTML-Herkunft Tags und Entitaeten aufloesen."""
    if tags_weg:
        s = re.sub(r'<br\s*/?>', ' ', s, flags=re.I)
        s = re.sub(r'<[^>]+>', '', s)
        s = html.unescape(s)
    s = s.replace(' ', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def schluessel(s):
    return glatt(s).casefold()


LEER = {'', '—', '–', '-', '--'}


def _nr_schl(x):
    return (int(x), getattr(x, 'zusatz', ''))


class Nr(int):
    """1.2: Zeilennummer mit Buchstabe ("18a"). Nur fuer solche Nummern; alle anderen bleiben int.
    Zahlwert 18 (alte Aufrufer mit "%d" laufen weiter), Vergleich, Hash und Text mit Buchstabe."""

    def __new__(cls, zahl, zusatz):
        o = int.__new__(cls, zahl)
        o.zusatz = zusatz
        return o

    def __str__(self):
        return '%d%s' % (int(self), self.zusatz)

    __repr__ = __str__

    def __hash__(self):
        return hash(_nr_schl(self))

    def __eq__(self, o):
        return isinstance(o, int) and _nr_schl(self) == _nr_schl(o)

    def __ne__(self, o):
        return not self.__eq__(o)

    def __lt__(self, o):
        return _nr_schl(self) < _nr_schl(o)

    def __le__(self, o):
        return _nr_schl(self) <= _nr_schl(o)

    def __gt__(self, o):
        return _nr_schl(self) > _nr_schl(o)

    def __ge__(self, o):
        return _nr_schl(self) >= _nr_schl(o)


# 1.2: "18", "#18", "18a", "18 (optional)", "18 optional", "18 *optional*"
NR_MUSTER = r'#?(\d+)((?-i:[a-z])?)(?:\s*[(*]*\s*optional\s*[)*]*)?'


def nr_lesen(s):
    m = re.fullmatch(NR_MUSTER, s.strip(), re.I)
    if not m:
        raise Abbruch('Zeilennummer nicht lesbar: %s' % s)
    return Nr(int(m.group(1)), m.group(2)) if m.group(2) else int(m.group(1))


class Zeile:
    def __init__(self, nr, typ, name, param, verb):
        self.nr, self.typ, self.name, self.param, self.verb = nr, typ, name, param, verb
        # "UND → Virtueller Ausgang": erster Typ traegt den Namen, weitere haengen am Ausgang
        self.typen = [t.strip() for t in re.split(r'\s*(?:→|->)\s*', typ) if t.strip()]

    def __repr__(self):
        return '#%s %s "%s"' % (self.nr, self.typ, self.name)


class BefehlsZiel(str):
    """1.2: Ziel ist ein Ausgangsbefehl der Zeile (Virtueller Ausgang samt Befehlen), kein Anschlussname."""


# ---------------------------------------------------------------------------
# 1. Baustein-Liste lesen (Textform wie baustein_listen.txt oder gerendertes HTML)
# ---------------------------------------------------------------------------

def liste_lesen(pfad):
    roh = open(pfad, 'rb').read().decode('utf-8-sig')
    if re.search(r'<t[dh]\b', roh, re.I):
        return html_lesen(roh)
    abschnitte = {}
    aktuell = ''
    for nr_z, z in enumerate(roh.splitlines(), 1):
        if z.startswith('====='):
            aktuell = z.strip('= \t')
            abschnitte.setdefault(aktuell, [])
            continue
        if not re.match(r'\s*' + NR_MUSTER + r'\s*\|', z, re.I):
            continue  # Kopfzeile, Leerzeile, Freitext
        teile = [t.strip() for t in z.split('|')]
        if len(teile) < 5:
            raise Abbruch('Liste %s Zeile %d: weniger als 5 Spalten: %s' % (pfad, nr_z, z))
        abschnitte.setdefault(aktuell, []).append(Zeile(
            nr_lesen(teile[0]), glatt(teile[1]), glatt(teile[2]),
            glatt(' | '.join(teile[3:-1])), glatt(teile[-1])))
    return abschnitte


def html_lesen(roh):
    """Jede Tabelle mit Kopf '... verbinden mit' ist ein Abschnitt; Name = letzte Ueberschrift davor."""
    abschnitte = {}
    for i, m in enumerate(re.finditer(r'<table\b.*?</table>', roh, re.I | re.S), 1):
        tab = m.group(0)
        if 'verbinden mit' not in glatt(tab, True):
            continue
        davor = re.findall(r'<h\d[^>]*>(.*?)</h\d>', roh[:m.start()], re.I | re.S)
        name = glatt(davor[-1], True) if davor else 'Tabelle %d' % i
        if name in abschnitte:
            name = '%s (%d)' % (name, i)
        zeilen = []
        for tr in re.findall(r'<tr\b.*?</tr>', tab, re.I | re.S):
            zellen = [glatt(c, True) for c in re.findall(r'<td\b[^>]*>(.*?)</td>', tr, re.I | re.S)]
            if len(zellen) < 5 or not re.fullmatch(NR_MUSTER, zellen[0], re.I):
                continue
            zeilen.append(Zeile(nr_lesen(zellen[0]), zellen[1], zellen[2],
                                ' | '.join(zellen[3:-1]), zellen[-1]))
        abschnitte[name] = zeilen
    return abschnitte


def verweise_der_zeile(z, weg):
    """Liefert [(Bezeichner oder None, Verweistext)] und Hinweise fuer nicht Ableitbares."""
    v = z.verb.strip()
    if v in LEER:
        return [], []
    hinweise = []
    # "HTTP-Weg: Eingang ALTER. MQTT-Weg: Lebenszeichen, ..."
    stuecke = re.split(r'(?:^|(?<=\.)\s+)([A-Za-z]+)-Weg:\s*', v)
    if len(stuecke) > 1 and stuecke[0].strip() == '':
        wege = {stuecke[i].casefold(): stuecke[i + 1].strip() for i in range(1, len(stuecke) - 1, 2)}
        if weg is None:
            raise Abbruch('#%s "%s": Die Zelle nennt mehrere Wege (%s). Bitte --weg angeben.'
                          % (z.nr, z.name, ', '.join(k.upper() for k in wege)))
        if weg.casefold() not in wege:
            return [], ['#%s: kein %s-Weg in "%s"' % (z.nr, weg, v)]
        v = wege[weg.casefold()].rstrip('.').strip()
    # 1.2: "beamer-wol, xbox-an ← #9; beamer-aus ← #10" an einer Zeile "Virtueller Ausgang ... Befehle":
    # jeder genannte Ausgangsbefehl (eigener Baustein auf der Seite) bekommt die Leitung von #N.
    # Nur bei Mehrzahl "Befehle(n)" im Typ: aeltere Listen schreiben "I ← #34" an "Virtueller Ausgang (Befehl)".
    if '←' in v and len(z.typen) == 1 and re.search(r'virtuell\w* .*ausgang.*\bbefehlen?\b', schluessel(z.typen[0])):
        stuecke = [BEFEHLS_ZIELE.fullmatch(s) for s in v.rstrip('.').split(';')]
        if all(stuecke):
            return [(BefehlsZiel(b.strip()), m.group(2)) for m in stuecke for b in m.group(1).split(',')], hinweise
    # 1.1: jeder Anschlussname vor dem "=" (I1, V1, V, En, AI1, Gpwr, Eingang ...)
    if re.match(r'^[A-Za-z][A-Za-z0-9]*\s*=', v):
        teile = re.findall(r'([A-Za-z][A-Za-z0-9]*)\s*=\s*(.*?)\s*(?=,\s*[A-Za-z][A-Za-z0-9]*\s*=|$)', v)
        return [(b, t) for b, t in teile], hinweise
    return [(None, v)], hinweise


def verweis_lesen(t):
    """('zeile', nr, Ausgang|None, Name|None) / ('eingang', name, ausdruecklich) / None

    Name ist der Text zwischen "Ausgang von" und "(#N)" (1.1: Befehlsname, wenn #N eine
    HTTP-/UDP-Zeile ist; sonst ohne Bedeutung). Die ersten drei Stellen sind wie in 1.0.0."""
    t = NEGIERT.sub('', t.strip().rstrip('.').strip())  # 1.1: "#10 (negiert)" -> Leitung, Inv am Ziel
    m = re.fullmatch(r'#(\d+[a-z]?)', t)  # 1.2: auch "#18a"
    if m:
        return ('zeile', nr_lesen(m.group(1)), None, None)
    m = re.fullmatch(r'Ausgang (?:von|des|der)\b\s*([^#]*?)\s*\(?#(\d+[a-z]?)\)?', t)
    if m:
        return ('zeile', nr_lesen(m.group(2)), None, m.group(1) or None)
    m = re.fullmatch(r'Ausgang ([A-Za-z][A-Za-z0-9]*) (?:von|des|der)\b\s*([^#]*?)\s*\(?#(\d+[a-z]?)\)?', t)
    if m:
        return ('zeile', nr_lesen(m.group(3)), m.group(1), m.group(2) or None)
    m = re.fullmatch(r'Eingang ([A-Za-z0-9_\-]+)', t)
    if m:
        return ('eingang', m.group(1), True)
    if re.fullmatch(r'[A-Za-z0-9_]+', t):
        return ('eingang', t, False)
    return None


# ---------------------------------------------------------------------------
# 2. Projektdatei: Seiten, Bausteine, Anschluesse
# ---------------------------------------------------------------------------

class Baustein:
    def __init__(self, el, seite):
        self.typ = el.get('Type')
        self.titel = el.get('Title') or ''
        self.u = el.get('U')
        self.seite = seite
        self.text = el.get('Text') == 'true'
        self.ref = el.get('Ref')  # 1.1: InputRef -> U des Befehls/Eingangs im Baum
        self.cos = {}  # K -> (U, [Input-U ...])
        for co in el.findall('Co'):
            self.cos[co.get('K')] = (co.get('U'), [i.get('Input') for i in co.findall('In')])
        self.inv = {co.get('K') for co in el.findall('Co') if co.get('Inv') == 'true'}  # 1.1: negierte Eingaenge

    def __repr__(self):
        return '%s "%s" (Seite "%s", U=%s)' % (self.typ, self.titel, self.seite, self.u)


def datei_lesen(pfad):
    return datei_lesen_aus(open(pfad, 'rb').read())


def datei_lesen_aus(roh):
    bom = roh.startswith(b'\xef\xbb\xbf')
    text = roh.decode('utf-8-sig')
    try:
        wurzel = ET.fromstring(text.encode('utf-8'))
    except ET.ParseError as e:
        raise Abbruch('Projektdatei nicht wohlgeformt: %s' % e)
    seiten = []
    for s in wurzel.iter('C'):
        if s.get('Type') == 'Page':
            bl = [Baustein(c, s.get('Title')) for c in s.iter('C') if c is not s]
            seiten.append((s.get('Title'), bl))
    return roh, bom, text, seiten


# 1.1: Befehle der virtuellen HTTP-/UDP-Eingaenge, wie Loxone Config sie speichert
# (geeicht: Demo_Abfahrt_Alexa.Loxone, 17 VirtualHttpInCmd unter VirtualHttpIn; auf der
# Seite steht je Befehl ein InputRef mit Ref = U des Befehls). Die Vorlagen-XML heisst
# anders (VirtualInHttpCmd/VirtualInUdpCmd) - die kommt hier nie an.
BEFEHLS_TYPEN = {'http': {'VirtualHttpInCmd'}, 'udp': {'VirtualUdpInCmd'}}
# 1.2: Quellen ohne Listenzeile (Vorlagen-Eingaenge). Auf der Seite je ein InputRef mit Ref = U und
# gleichem Titel, Leitung von AQ - gezaehlt an der von Config gespeicherten Hausdatei 20260703
# (VirtualIn 49/49 InputRef mit gleichem Titel; alle 25 genutzten Ausgaenge solcher InputRef sind AQ,
# auch bei digitalen VirtualIn). VirtualTextIn wird erkannt, aber nicht verbunden (nicht geeicht).
QUELL_TYPEN = {'VirtualIn', 'VirtualTextIn'} | BEFEHLS_TYPEN['http'] | BEFEHLS_TYPEN['udp']
# 1.2: Ausgangsbefehle; auf der Seite je ein OutputRef mit Ref = U und gleichem Titel, Eingang AI
# (geeicht: Demo_Abfahrt_Alexa.Loxone, von Config gespeichert, 2 verbundene OutputRef auf
# VirtualOutCmd; Hausdatei 15/15 OutputRef mit gleichem Titel, Eingang AI)
AUSGANGSBEFEHL_TYPEN = {'VirtualOutCmd'}


def befehle_lesen_aus(text):
    """U -> (Typ, Titel, Titel des Geraets) fuer alle HTTP-/UDP-Befehle der Datei
    (1.2: dazu virtuelle Eingaenge und Ausgangsbefehle)."""
    alle = set().union(*BEFEHLS_TYPEN.values()) | QUELL_TYPEN | AUSGANGSBEFEHL_TYPEN
    erg = {}
    for g in ET.fromstring(text.encode('utf-8')).iter('C'):
        for c in g.findall('C'):
            if c.get('Type') in alle:
                erg[c.get('U')] = (c.get('Type'), c.get('Title') or '', g.get('Title') or '')
    return erg


def befehls_art(typ):
    """'http' / 'udp', wenn der Listentyp ein virtueller HTTP-/UDP-Eingang(-Befehl) ist."""
    k = schluessel(re.sub(r'\([^)]*\)', '', typ))
    m = re.search(r'virtuell\w* (http|udp)\b.*eingang', k)
    return m.group(1) if m else None


# deutsche Typangabe der Liste -> XML-Typen (Bausteine auf der Seite)
TYPEN = [
    (r'virtuell\w* .*eingang', {'InputRef'}),
    (r'virtuell\w* .*ausgang', {'OutputRef'}),
    (r'benachrichtigung', {'OutputRefLM'}),
    (r'^und\b', {'And'}),
    (r'^oder\b', {'Or'}),
    (r'^exklusiv oder\b', {'Xor'}),
    (r'^nicht\b', {'Not'}),
    (r'^formel\b', {'Formula'}),
    (r'^schwellwertschalter\b', {'AnalogThresholdTrigger'}),
    (r'^einschaltverz(ö|oe)gerung speichernd', {'RetOnDelay'}),
    (r'^einschaltverz(ö|oe)gerung', {'OnDelay'}),
    (r'^ausschaltverz(ö|oe)gerung', {'OffDelay'}),
    # 1.3: auch "Statusbaustein" - nur allein (Klammerzusatz ist schon weg), nicht "Statusbaustein oder Formel"
    (r'^status\b|^statusbaustein$', {'State'}),
    (r'^radiotasten', {'Radio', 'Radio2'}),
    # 1.1: eine Konstante liegt auf der Seite als InputRef (Ref auf den Constant im Baum)
    (r'^konstante\b', {'InputRef'}),
    # 1.2: Typnamen aus Referenz_Bausteine.Loxone/Leer.Loxone (von Config gespeichert; Anschluesse
    # Validator: inval, enable, mintime, minval, maxval, delay, outval, error;
    # EdgeDetection: Input, PulseTime, Edge, RisingEdge, FallingEdge). Leitungen daran nicht in Config geeicht
# (1.3: Validator im Musterprojekt von Config verbunden gespeichert; EdgeDetection weiter nicht).
    (r'^analogwert-?validierung', {'Validator'}),
    (r'^flankenerkennung', {'EdgeDetection'}),
    (r'^ausgangsbefehl\b', {'OutputRef'}),
    # 1.3: Analogkomparator; im Musterprojekt (von Config gespeichert) AnalogComparator mit
    # Input1, Input2, On, Off, Q. Die Listen schreiben "Analogwert-Vergleicher".
    # Alle 1.3-Namen nur allein (ohne "oder ..."); ein Klammerzusatz wie "(optional)" ist vorher entfernt.
    (r'^(?:analogwert-?vergleicher|analogkomparator)$', {'AnalogComparator'}),
    # 1.3: Standardtitel, die Config beim Ablegen vergibt (Leer.Loxone, von Config 17.1 gespeichert)
    (r'^treppenlichtschalter$', {'StairwayLS'}),
    (r'^alarmanlage$', {'Alarm'}),
    (r'^bew(ä|ae)sserung$', {'Irrigation'}),
    (r'^energiemanager(?: 2)?$', {'EnergyManager2'}),
]

# erster Eingang ohne Bezeichner in der Liste ("Ausgang von #11")
EIN_STANDARD = {
    'AnalogThresholdTrigger': 'Input', 'OnDelay': 'InputTrigger', 'OffDelay': 'InputTrigger',
    'RetOnDelay': 'InputTrigger', 'OutputRef': 'AI', 'OutputRefLM': 'AI', 'Formula': 'Input1',
    'And': 'I1', 'Or': 'I1', 'Xor': 'I1', 'Not': 'I', 'State': 'I1',
    'Validator': 'inval', 'EdgeDetection': 'Input',  # 1.2
    # 1.3: Analogkomparator am Musterprojekt (von Config verbunden); sonst der erste Eingang laut
    # Referenz_Bausteine.Loxone/Leer.Loxone
    'AnalogComparator': 'Input1', 'Greater': 'Input1', 'GreaterEqual': 'Input1', 'Less': 'Input1',
    'LessEqual': 'Input1', 'Equal': 'Input1', 'NotEqual': 'Input1', 'Monoflop': 'InputTrigger',
    'OnOffDelay': 'InputTrigger', 'AMemory': 'Input', 'Memory': 'Input', 'StairwayLS': 'InputTrigger',
}

# Ausgang ohne Angabe in der Liste ("Ausgang von #13", "I1 = #13")
AUS_STANDARD = {
    'InputRef': 'AQ', 'AnalogThresholdTrigger': 'Q', 'And': 'Q', 'Or': 'Q', 'Xor': 'Q', 'Not': 'Q',
    'OnDelay': 'Q', 'OffDelay': 'Q', 'RetOnDelay': 'Q', 'Formula': 'AQ', 'Radio': 'AQ', 'Radio2': 'AQ',
    'Validator': 'error',  # 1.2: Standardausgang der Analogwertvalidierung (Config: E) -> Benachrichtigung
    # 1.3: Bausteine mit genau einem Ausgang in den von Config gespeicherten Dateien (Merker: AQ und Q, keiner)
    'AnalogComparator': 'Q', 'Greater': 'Q', 'GreaterEqual': 'Q', 'Less': 'Q', 'LessEqual': 'Q', 'Equal': 'Q',
    'NotEqual': 'Q', 'Monoflop': 'Q', 'OnOffDelay': 'Q', 'AMemory': 'AQ', 'StairwayLS': 'Q',
}

# 1.2: Config-Beschriftung -> Anschluss in der Datei, je Typ. 1.3: alle in Config abgelesen und im
# Musterprojekt (LoxBerry-Plugins_Musterprojekt.Loxone, von Config gespeichert, 09.10.2026) verbunden
# gefunden: Validator V/En/E, Schwellwertschalter V, Analogkomparator Ausgang De, Status Ausgang Val.
# Analogkomparator V1/V2 bzw. I1/I2 -> Input1/Input2 geht ueber den allgemeinen Weg I<n>/V<n>.
BESCHRIFTUNG_EIN = {'Validator': {'v': 'inval', 'en': 'enable'}, 'AnalogThresholdTrigger': {'v': 'Input'},
                    'AMemory': {'v': 'Input', 'set': 'Trigger', 'off': 'Reset'},  # 1.3.1
                    'Counter': {'c': 'Trigger', 'off': 'Reset'},  # 1.3.2
                    'Irrigation': {'act': 'A', 'sel': 'AIv', 'raf': 'Rf', 'off': 'Reset'}}  # 1.3.2
BESCHRIFTUNG_AUS = {'Validator': {'e': 'error'}, 'AnalogComparator': {'de': 'Q'}, 'State': {'val': 'AQ'},
                    'Counter': {'v': 'AQ'}, 'AMemory': {'v': 'AQ'}, 'Irrigation': {'p': 'Qp'},  # 1.3.2
                    'EdgeDetection': {'p': 'Edge', 'on': 'RisingEdge', 'off': 'FallingEdge'}}  # 1.3.2

# 1.1: Namen, die nie ein Eingang sind ("Q = #3" waere eine Leitung in einen Ausgang);
# dazu alles, was mit Q, AQ oder TQ beginnt (AQp, AQ1 ... am Energiezaehler). Andere
# Ausgaenge (O, OL1 am Energiemanager) erkennt die Datei nicht - Gegenprobe in Config.
AUSGANG_NAMEN = {'Q', 'AQ', 'TQ', 'API', 'OutputAPI'} | set(AUS_STANDARD.values()) \
    | {'outval', 'Edge', 'RisingEdge', 'FallingEdge'}  # 1.2

# 1.2: blosser Name einer Vorlagen-Quelle ("FW_OK", "pumpe_status_zaehler"): mit Unterstrich, sonst
# bleibt ein blosses Wort ("Lebenszeichen") wie bisher Freitext
VORLAGEN_NAME = re.compile(r'[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+')
# 1.2: Folgetyp "Ausgangsbefehl play"
AUSGANGSBEFEHL = re.compile(r'Ausgangsbefehl\s+(\S.*)', re.I)
# 1.2: "beamer-wol, xbox-an ← #9"
BEFEHLS_ZIELE = re.compile(r'\s*([A-Za-z0-9_.\-]+(?:\s*,\s*[A-Za-z0-9_.\-]+)*)\s*←\s*(#\d+[a-z]?)\s*')

# 1.1: Zelle nennt einen Zwischenbaustein ohne eigene Zeile ("ueber einen Schwellwertschalter")
ZWISCHEN = re.compile(r'\b(?:über|ueber) (?:ein|eine|einen|einem)\b[^,;.]*', re.I)
# 1.1: negierter Eingang "I2 = #10 (negiert)"; Config speichert <Co K="I2" Inv="true" Nc="1" U="...">
# (Reihenfolge K, Inv, Def, Nc, U - gezaehlt an einer von Config gespeicherten Hausdatei: 69 verbundene
# und 143 unverbundene Eingaenge mit Inv, alle in dieser Reihenfolge)
NEGIERT = re.compile(r'\s*\(negiert\)$', re.I)
KONSTANTE = re.compile(r'Konstante\s+(\S+)(?:\s.*)?', re.I)


def xml_typen(typ):
    k = schluessel(re.sub(r'\([^)]*\)', '', typ))
    for muster, menge in TYPEN:
        if re.search(muster, k):
            return menge
    return None  # unbekannt: nur nach Name suchen, mit Hinweis


# ---------------------------------------------------------------------------
# 3. Planen
# ---------------------------------------------------------------------------

class Planer:
    def __init__(self, zeilen, bloecke, weg, ohne, ziele, befehle=None):
        self.befehle = befehle  # 1.1: befehle_lesen_aus(); None = ohne Projektdatei
        self.zeilen = {}
        for z in zeilen:
            if z.nr in self.zeilen:
                raise Abbruch('Liste: Nummer #%s kommt doppelt vor.' % z.nr)
            self.zeilen[z.nr] = z
        self.bloecke, self.weg, self.ohne, self.ziele = bloecke, weg, ohne, ziele
        self.cache = {}
        self.plan, self.hinweise = [], []
        self.namen = {schluessel(z.name) for z in zeilen}

    def block(self, z, typ):
        if (z.nr, typ) in self.cache:
            return self.cache[(z.nr, typ)]
        erwartet = xml_typen(typ)
        gleichnamig = [b for b in self.bloecke if schluessel(b.titel) == schluessel(z.name)]
        if erwartet is None:
            self.hinweise.append('#%s: Typ "%s" unbekannt, nur nach Name gesucht.' % (z.nr, typ))
            treffer = gleichnamig
        else:
            treffer = [b for b in gleichnamig if b.typ in erwartet]
        if not treffer:
            if gleichnamig:
                raise Abbruch('#%s "%s": Typ passt nicht. Liste: %s (%s), Datei: %s'
                              % (z.nr, z.name, typ, '/'.join(sorted(erwartet)),
                                 '; '.join(map(repr, gleichnamig))))
            raise Abbruch('#%s "%s" (%s): Baustein fehlt auf der Seite. Ist er nicht gebaut, '
                          '--ohne %s angeben.' % (z.nr, z.name, typ, z.nr))
        if len(treffer) > 1:
            raise Abbruch('#%s "%s": Name mehrdeutig, %d Bausteine: %s'
                          % (z.nr, z.name, len(treffer), '; '.join(map(repr, treffer))))
        self.cache[(z.nr, typ)] = treffer[0]
        return treffer[0]

    def ketten_block(self, z, typ, stufe):
        schl = '%s.%d' % (z.nr, stufe)
        if schl in self.ziele or (stufe == 1 and str(z.nr) in self.ziele):
            titel = self.ziele.get(schl) or self.ziele.get(str(z.nr))
            return self.block(Zeile(z.nr, typ, titel, '', ''), typ)
        m = AUSGANGSBEFEHL.fullmatch(typ)
        if m:  # 1.2: "UND → Ausgangsbefehl play": der Befehl mit genau diesem Titel, sein Baustein auf der Seite
            return self.ausgangsbefehl_block(m.group(1).strip(), None, z)
        erwartet = xml_typen(typ)
        if erwartet is None:
            raise Abbruch('#%s: Folgetyp "%s" unbekannt; --ziel %s=<Titel> angeben.' % (z.nr, typ, z.nr))
        frei = [b for b in self.bloecke if b.typ in erwartet and schluessel(b.titel) not in self.namen]
        if len(frei) != 1:
            raise Abbruch('#%s "%s" → %s: %d passende Bausteine ohne eigene Listenzeile (%s); '
                          '--ziel %s=<Titel> angeben.'
                          % (z.nr, z.name, typ, len(frei), '; '.join(map(repr, frei)) or 'keiner', z.nr))
        return frei[0]

    def eingang_zeile(self, name, ausdruecklich, z):
        return self.eingang_zeile_befehl(name, ausdruecklich, z)[0]

    def eingang_zeile_befehl(self, name, ausdruecklich, z):
        """(Zeile, None) wie 1.0.0, oder 1.1: (HTTP-/UDP-Zeile, Befehlsname), wenn die Liste den
        ausdruecklich genannten Eingang nicht fuehrt, aber genau eine Befehlsquelle hat."""
        k = name.casefold()
        treffer = [r for r in self.zeilen.values()
                   if 'eingang' in r.typen[0].casefold()
                   and (r.name.casefold() == k or r.name.casefold().endswith('_' + k))]
        if len(treffer) == 1:
            return treffer[0], None
        if len(treffer) > 1:
            raise Abbruch('#%s: Eingang "%s" mehrdeutig in der Liste: %s' % (z.nr, name, treffer))
        if ausdruecklich:
            quellen = [r for r in self.zeilen.values() if befehls_art(r.typen[0])]
            befehlszeilen = [r for r in quellen if 'befehl' in r.typen[0].casefold()]
            if befehlszeilen:
                quellen = befehlszeilen
            if len(quellen) == 1:
                return quellen[0], name
            if len(quellen) > 1:
                raise Abbruch('#%s: Eingang "%s" steht nicht in der Liste, und die Liste hat mehrere '
                              'HTTP-/UDP-Zeilen (%s). Bitte "Ausgang von %s (#N)" schreiben, N = die Zeile '
                              'des Befehls.' % (z.nr, name, ', '.join('#%s' % r.nr for r in quellen), name))
            raise Abbruch('#%s: Eingang "%s" steht nicht in der Liste.' % (z.nr, name))
        return None, None

    def befehl_block(self, qz, name, art, z):
        """1.1: Eingangsbaustein auf der Seite zum HTTP-/UDP-Befehl "name" (Quelle Zeile qz)."""
        if (qz.nr, 'befehl', name) in self.cache:
            return self.cache[(qz.nr, 'befehl', name)]
        if self.befehle is None:
            raise Abbruch('#%s: Quelle ist der Befehl "%s" (#%s) - dafür braucht es die Projektdatei.'
                          % (z.nr, name, qz.nr))
        typen = BEFEHLS_TYPEN[art]
        kand = [(u, t) for u, t in self.befehle.items() if t[0] in typen and schluessel(t[1]) == schluessel(name)]
        if not kand:
            aehnlich = sorted({t[1] for t in self.befehle.values() if t[0] in typen
                               and schluessel(name) in schluessel(t[1])})
            raise Abbruch('#%s: %s-Befehl "%s" (Quelle #%s "%s") gibt es in der Projektdatei nicht. Der Name '
                          'muss genau der Titel des Befehls in Config sein.%s'
                          % (z.nr, art.upper(), name, qz.nr, qz.name,
                             (' Ähnlich: %s' % ', '.join(aehnlich[:8])) if aehnlich else ''))
        if len(kand) > 1:
            raise Abbruch('#%s: %s-Befehl "%s" mehrdeutig, %d Befehle: %s' % (
                z.nr, art.upper(), name, len(kand),
                '; '.join('%s "%s" unter "%s" (U=%s)' % (t[0], t[1], t[2], u) for u, t in kand)))
        u, t = kand[0]
        auf_seite = [b for b in self.bloecke if b.typ == 'InputRef' and b.ref == u]
        if not auf_seite:
            raise Abbruch('#%s: %s-Befehl "%s" (unter "%s") liegt nicht auf der Seite. In Config aus dem '
                          'Baum auf die Seite ziehen.' % (z.nr, art.upper(), t[1], t[2]))
        if len(auf_seite) > 1:
            raise Abbruch('#%s: %s-Befehl "%s" liegt %d-mal auf der Seite: %s'
                          % (z.nr, art.upper(), t[1], len(auf_seite), '; '.join(map(repr, auf_seite))))
        self.cache[(qz.nr, 'befehl', name)] = auf_seite[0]
        return auf_seite[0]

    def quelle_suchen(self, name, ausdruecklich, z):
        """1.2: ('zeile', Zeile, Befehlsname|None) wie eingang_zeile_befehl, ('vorlage', name) fuer einen
        Eingang ohne Listenzeile, den das Werkzeug in der Projektdatei sucht, oder None (Freitext).
        Vorlage: "Eingang X", wenn die Liste weder X noch eine HTTP-/UDP-Zeile hat (1.1: Abbruch),
        und ein blosser Name mit Unterstrich ("FW_OK"; 1.1: Freitext)."""
        k = name.casefold()
        treffer = [r for r in self.zeilen.values()
                   if 'eingang' in r.typen[0].casefold()
                   and (r.name.casefold() == k or r.name.casefold().endswith('_' + k))]
        if treffer or ausdruecklich and any(befehls_art(r.typen[0]) for r in self.zeilen.values()):
            r, befehl = self.eingang_zeile_befehl(name, ausdruecklich, z)  # wie 1.1
            return ('zeile', r, befehl) if r else None
        if ausdruecklich or VORLAGEN_NAME.fullmatch(name):
            return ('vorlage', name)
        return None

    def _titel_suchen(self, name, typen, geraet=None):
        """[(U, (Typ, Titel, Geraet))] mit genau diesem Titel (sonst ohne Gross-/Kleinschreibung) und
        Liste aehnlicher Titel fuer die Meldung."""
        alle = [(u, t) for u, t in self.befehle.items() if t[0] in typen
                and (geraet is None or schluessel(t[2]) == schluessel(geraet))]
        kand = [(u, t) for u, t in alle if t[1] == name] or \
            [(u, t) for u, t in alle if schluessel(t[1]) == schluessel(name)]
        titel = sorted({t[1] for _, t in alle})
        aehnlich = [x for x in titel if schluessel(name) in schluessel(x) or schluessel(x) in schluessel(name)]
        for x in difflib.get_close_matches(name, titel, n=8, cutoff=0.75):
            if x not in aehnlich:
                aehnlich.append(x)
        return kand, aehnlich[:8]

    def _auf_seite(self, u, typ, was, z):
        auf_seite = [b for b in self.bloecke if b.typ == typ and b.ref == u]
        if not auf_seite:
            raise Abbruch('#%s: %s liegt nicht auf der Seite. In Config aus dem Baum auf die Seite ziehen.'
                          % (z.nr, was))
        if len(auf_seite) > 1:
            raise Abbruch('#%s: %s liegt %d-mal auf der Seite: %s'
                          % (z.nr, was, len(auf_seite), '; '.join(map(repr, auf_seite))))
        return auf_seite[0]

    def vorlage_block(self, name, z):
        """1.2: Eingangsbaustein auf der Seite zu einem virtuellen Eingang/HTTP-/UDP-Befehl ohne Listenzeile."""
        if ('vorlage', name) in self.cache:
            return self.cache[('vorlage', name)]
        if self.befehle is None:
            raise Abbruch('#%s: "%s" hat keine Listenzeile; das Werkzeug sucht ihn als virtuellen Eingang in '
                          'der Projektdatei - dafür braucht es die Projektdatei.' % (z.nr, name))
        kand, aehnlich = self._titel_suchen(name, QUELL_TYPEN)
        if not kand:
            raise Abbruch('#%s: Eingang "%s" steht nicht in der Liste, und die Projektdatei hat keinen virtuellen '
                          'Eingang oder HTTP-/UDP-Befehl mit genau diesem Titel. Ist die Vorlage nicht importiert '
                          'oder der Baustein nicht gebaut: --ohne %s.%s'
                          % (z.nr, name, z.nr, (' Ähnlich: %s' % ', '.join(aehnlich)) if aehnlich else ''))
        if len(kand) > 1:
            raise Abbruch('#%s: Eingang "%s" mehrdeutig in der Projektdatei, %d Treffer: %s' % (
                z.nr, name, len(kand), '; '.join('%s "%s" unter "%s" (U=%s)' % (t[0], t[1], t[2], u)
                                                 for u, t in kand)))
        u, t = kand[0]
        if t[0] == 'VirtualTextIn':
            raise Abbruch('#%s: "%s" ist ein virtueller Texteingang. Als Quelle ist er nicht geeicht; '
                          'in Config von Hand verbinden.' % (z.nr, t[1]))
        b = self._auf_seite(u, 'InputRef', '%s "%s" (unter "%s")' % (t[0], t[1], t[2]), z)
        self.hinweise.append('#%s: "%s" hat keine Listenzeile; Quelle ist %s "%s" (unter "%s") aus der '
                             'Projektdatei.' % (z.nr, name, t[0], t[1], t[2]))
        self.cache[('vorlage', name)] = b
        return b

    def ausgangsbefehl_block(self, name, geraet, z):
        """1.2: Ausgangsbaustein auf der Seite zum Ausgangsbefehl "name" (wenn geraet: nur unter diesem
        virtuellen Ausgang)."""
        if ('ausgangsbefehl', name, geraet) in self.cache:
            return self.cache[('ausgangsbefehl', name, geraet)]
        if self.befehle is None:
            raise Abbruch('#%s: Ziel ist der Ausgangsbefehl "%s" - dafür braucht es die Projektdatei.' % (z.nr, name))
        kand, aehnlich = self._titel_suchen(name, AUSGANGSBEFEHL_TYPEN, geraet)
        unter = (' unter "%s"' % geraet) if geraet else ''
        if not kand:
            raise Abbruch('#%s: Ausgangsbefehl "%s"%s gibt es in der Projektdatei nicht. Der Name muss genau der '
                          'Titel des Befehls in Config sein.%s'
                          % (z.nr, name, unter, (' Ähnlich: %s' % ', '.join(aehnlich)) if aehnlich else ''))
        if len(kand) > 1:
            raise Abbruch('#%s: Ausgangsbefehl "%s" mehrdeutig, %d Befehle: %s; --ziel %s=<Titel> angeben.' % (
                z.nr, name, len(kand), '; '.join('"%s" unter "%s" (U=%s)' % (t[1], t[2], u) for u, t in kand),
                z.nr))
        u, t = kand[0]
        b = self._auf_seite(u, 'OutputRef', 'Ausgangsbefehl "%s" (unter "%s")' % (t[1], t[2]), z)
        self.cache[('ausgangsbefehl', name, geraet)] = b
        return b

    def flanken_ausgang(self, b, listentyp, z):
        """1.2: Ausgang der Flankenerkennung nach der Richtung im Listentyp; sonst None (Abbruch in ausgang_k)."""
        if b.typ != 'EdgeDetection':
            return None
        k = schluessel(listentyp)
        aus = 'RisingEdge' if 'steigend' in k else 'FallingEdge' if 'fallend' in k else None
        h = '#%s: Flankenerkennung "%s": Ausgang %s nach „%s“.' % (
            z.nr, b.titel, aus, 'steigend' if aus == 'RisingEdge' else 'fallend')
        if aus and h not in self.hinweise:
            self.hinweise.append(h)
        return aus

    def eingang_k(self, b, bez, z):
        if bez and bez.casefold() == 'eingang':
            bez = None  # 1.1: "Eingang = #N" ist der Standardeingang
        m = re.fullmatch(r'AI(\d+)', bez or '', re.I)
        if m and not any(k.casefold() == bez.casefold() for k in b.cos):
            # 1.1: Analogeingang AI<n> (so beschriftet Config z. B. "Groesser oder gleich"); in der Datei
            # heisst er Input<n> (geeicht an Greater/GreaterEqual/Equal/Less einer Hausdatei). Nur dieser Schritt.
            # 1.2: am Status (Typ State, Hausdatei: I1 ... I8) wie V<n> auf I<n>
            k = ('I' if b.typ == 'State' else 'Input') + m.group(1)
            if k not in b.cos:
                raise Abbruch('#%s: %r hat weder "%s" noch "%s". Anschlüsse in der Datei: %s'
                              % (z.nr, b, bez, k, ', '.join(b.cos) or 'keine'))
            self.hinweise.append('#%s: %s an %s "%s" als Anschluss %s gelesen.' % (z.nr, bez, b.typ, b.titel, k))
            return k
        if bez and not re.fullmatch(r'[IViv]\d+', bez):  # i1/v1 wie I1/V1
            # 1.1: Anschlussname aus der Projektdatei, nie geraten
            treffer = [k for k in b.cos if k == bez] or [k for k in b.cos if k.casefold() == bez.casefold()]
            alias = BESCHRIFTUNG_EIN.get(b.typ, {}).get(bez.casefold())
            if not treffer and alias in b.cos:  # 1.2: Config-Beschriftung (Validator: V -> inval)
                self.hinweise.append('#%s: %s an %s "%s" als Anschluss %s gelesen (Config-Beschriftung).'
                                     % (z.nr, bez, b.typ, b.titel, alias))
                treffer = [alias]
            if len(treffer) != 1:
                raise Abbruch('#%s: %r hat keinen Anschluss "%s". Anschlüsse in der Datei: %s'
                              % (z.nr, b, bez, ', '.join(b.cos) or 'keine'))
            if treffer[0] in AUSGANG_NAMEN or re.match(r'[AT]?Q', treffer[0]):
                raise Abbruch('#%s: "%s" an %r ist ein Ausgang, kein Eingang.' % (z.nr, treffer[0], b))
            return treffer[0]
        if bez:
            n = bez[1:]
            for k in ('I' + n, 'Input' + n, 'InputTrigger ' + n, 'AI' + n):
                if k in b.cos:
                    return k
            raise Abbruch('#%s: %r hat keinen Eingang %s.' % (z.nr, b, bez))
        k = EIN_STANDARD.get(b.typ)
        if not k or k not in b.cos:
            raise Abbruch('#%s: Eingang von %r unbekannt; in der Liste "I1 = ..." schreiben.' % (z.nr, b))
        return k

    def ausgang_k(self, b, ziel, ausdruecklich, z):
        if ausdruecklich:
            k = ausdruecklich
            alias = BESCHRIFTUNG_AUS.get(b.typ, {}).get(k.casefold())
            if k not in b.cos and alias in b.cos:  # 1.2: Config-Beschriftung (Validator: E -> error)
                self.hinweise.append('#%s: Ausgang %s an %s "%s" als %s gelesen (Config-Beschriftung).'
                                     % (z.nr, k, b.typ, b.titel, alias))
                k = alias
        elif b.typ == 'State':
            k = 'TQ' if ziel.text else 'AQ'
        else:
            k = AUS_STANDARD.get(b.typ)
        if not k or k not in b.cos:
            raise Abbruch('#%s: Ausgang %s von %r unbekannt; in der Liste "Ausgang AQ von #N" schreiben.'
                          % (z.nr, k or '?', b))
        return k

    def leitung(self, z, ziel, ziel_k, quelle, quelle_k, text, negiert=False):
        self.plan.append({'nr': z.nr, 'ziel': ziel, 'ziel_k': ziel_k, 'ziel_u': ziel.cos[ziel_k][0],
                          'quelle': quelle, 'quelle_k': quelle_k, 'quelle_u': quelle.cos[quelle_k][0],
                          'text': text, 'negiert': negiert})

    def hinweis_frei(self, z, bez, text):
        """Hinweis fuer eine Angabe ohne Leitung (1.1: eigene Meldung fuer Konstante und
        Zwischenbaustein; sonst Wortlaut wie 1.0.0)."""
        vor = (bez + ' = ') if bez else ''
        m = KONSTANTE.fullmatch(text.strip().rstrip('.').strip())
        if m:
            if bez and z.nr not in self.ohne:
                self.eingang_k(self.block(z, z.typen[0]), bez, z)  # Anschlussname pruefen
            return ('#%s "%s": %s%s – keine Leitung: eine Konstante ist kein Baustein der Liste. '
                    'Wert %s in Loxone Config von Hand setzen, oder die Konstante als eigene Listenzeile '
                    '(Typ "Konstante") führen und "%s#N" schreiben.'
                    % (z.nr, z.name, vor, text, m.group(1), vor or 'Eingang = '))
        zw = [x.group(0).strip() for x in ZWISCHEN.finditer(text)]
        if zw:
            return ('#%s "%s": nicht ableitbar, bleibt frei: %s%s – die Zelle nennt einen Zwischenbaustein '
                    'ohne eigene Listenzeile (%s). Das Werkzeug setzt keine Bausteine: ihn in Config von Hand '
                    'setzen und verbinden, oder ihn als eigene Zeile in die Liste aufnehmen ("Ausgang von #N").'
                    % (z.nr, z.name, vor, text, '; '.join('„%s“' % x for x in zw)))
        return '#%s "%s": nicht ableitbar, bleibt frei: %s%s' % (z.nr, z.name, vor, text)

    def planen(self):
        for z in sorted(self.zeilen.values(), key=lambda r: r.nr):
            verweise, h = verweise_der_zeile(z, self.weg)
            self.hinweise += h
            for bez, text in verweise:
                befehls_ziel = isinstance(bez, BefehlsZiel)  # 1.2: "beamer-wol ← #9"
                vor = (bez + ' ← ') if befehls_ziel else (bez + ' = ') if bez else ''
                v = verweis_lesen(text)
                vorlage = None
                if v and v[0] == 'eingang':
                    q = self.quelle_suchen(v[1], v[2], z)  # 1.2 (vorher eingang_zeile_befehl)
                    if q is None:
                        v = None
                    elif q[0] == 'vorlage':
                        vorlage, v = q[1], ('vorlage', None, None, None)
                    else:
                        v = ('zeile', q[1].nr, None, q[2])
                if v is None:
                    self.hinweise.append(self.hinweis_frei(z, bez, text))
                    continue
                qnr, qk = v[1], v[2]
                if vorlage is None and qnr not in self.zeilen:
                    raise Abbruch('#%s: Verweis auf #%s, die Liste hat keine solche Zeile.' % (z.nr, qnr))
                if z.nr in self.ohne or (vorlage is None and qnr in self.ohne):
                    self.hinweise.append('#%s: %s%s übersprungen (--ohne).' % (z.nr, vor, text))
                    continue
                qz = self.zeilen.get(qnr)
                if befehls_ziel:
                    ziel = self.ausgangsbefehl_block(str(bez), z.name, z)
                else:
                    ziel = self.block(z, z.typen[0])
                art = befehls_art(qz.typen[0]) if qz else None
                if vorlage is not None:
                    quelle = self.vorlage_block(vorlage, z)  # 1.2: Vorlagen-Eingang ohne Listenzeile
                elif art and v[3]:
                    quelle = self.befehl_block(qz, v[3], art, z)  # 1.1: HTTP-/UDP-Befehl als Quelle
                else:
                    quelle = self.block(qz, qz.typen[0])
                zk = self.eingang_k(ziel, None if befehls_ziel else bez, z)
                if qk is None and qz is not None:
                    qk = self.flanken_ausgang(quelle, qz.typen[0], z)  # 1.2
                negiert = bool(NEGIERT.search(text.strip().rstrip('.').strip()))
                if negiert:
                    self.hinweise.append('#%s: Eingang %s von "%s" wird negiert (Inv="true" wie in Config).'
                                         % (z.nr, zk, ziel.titel))
                self.leitung(z, ziel, zk, quelle, self.ausgang_k(quelle, ziel, qk, z),
                             '%s%s' % (vor, text), negiert)
            # Kette "UND → Virtueller Ausgang"
            if len(z.typen) > 1 and z.nr not in self.ohne:
                vorher = self.block(z, z.typen[0])
                for stufe, typ in enumerate(z.typen[1:], 1):
                    nach = self.ketten_block(z, typ, stufe)
                    self.leitung(z, nach, self.eingang_k(nach, None, z), vorher,
                                 self.ausgang_k(vorher, nach, self.flanken_ausgang(vorher, z.typen[stufe - 1], z),
                                                z), '→ %s' % typ)
                    vorher = nach
        ziele = {}
        for p in self.plan:
            if p['ziel_u'] in ziele:
                raise Abbruch('Eingang %s "%s" ist zweimal geplant (#%s und #%s).'
                              % (p['ziel_k'], p['ziel'].titel, ziele[p['ziel_u']], p['nr']))
            ziele[p['ziel_u']] = p['nr']
        return self.plan


# ---------------------------------------------------------------------------
# 4. Pruefen und Schreiben
# ---------------------------------------------------------------------------

def frei_muster(u):
    return re.compile(r'(?m)^(\t*)<Co K="([^"]+)"((?: (?!U=|Nc=)[A-Za-z]+="[^"]*")*) U="'
                      + re.escape(u) + r'"/>(?=(\r?\n))')


def pruefen(text, plan, gleiche_lassen):
    for p in plan:
        n = len(re.findall(r'\bU="' + re.escape(p['quelle_u']) + '"', text))
        if n != 1:
            raise Abbruch('#%s: Ausgang %s von "%s" kommt %d-mal vor.' % (p['nr'], p['quelle_k'], p['quelle'].titel, n))
        vorhanden = p['ziel'].cos[p['ziel_k']][1]
        if vorhanden:
            if gleiche_lassen and vorhanden == [p['quelle_u']]:
                if p['negiert'] and p['ziel_k'] not in p['ziel'].inv:
                    raise Abbruch('#%s: Eingang %s von "%s" ist verbunden, aber nicht negiert.'
                                  % (p['nr'], p['ziel_k'], p['ziel'].titel))
                if validator_enable(p) and p['ziel_k'] in p['ziel'].inv:  # 1.3.3
                    raise Abbruch('#%s: Eingang enable von "%s" ist negiert (Inv="true") - die Konstante kommt als 0 an, '
                                  'die Validierung prueft Tmc nicht. Negation entfernen.' % (p['nr'], p['ziel'].titel))
                p['status'] = 'vorhanden'
                continue
            raise Abbruch('#%s: Eingang %s von "%s" ist schon verbunden (mit %s).'
                          % (p['nr'], p['ziel_k'], p['ziel'].titel, ', '.join(vorhanden)))
        n = len(frei_muster(p['ziel_u']).findall(text))
        if n != 1:
            raise Abbruch('#%s: Eingang %s von "%s" ist nicht genau einmal unverbunden (%d).'
                          % (p['nr'], p['ziel_k'], p['ziel'].titel, n))
        p['status'] = 'neu'


def validator_enable(p):  # 1.3.3
    return p['ziel'].typ == 'Validator' and p['ziel_k'] == 'enable' and not p['negiert']


def eintragen(text, plan):
    for p in plan:
        if p['status'] != 'neu':
            continue

        def ersetze(m, p=p):
            ein, nl, attr = m.group(1), m.group(4), m.group(3)
            if p['negiert'] and ' Inv=' not in attr:
                attr = ' Inv="true"' + attr  # 1.1: Inv direkt nach K, wie Config
            if validator_enable(p):
                attr = attr.replace(' Inv="true"', '')  # 1.3.3: Config-Vorgabe Inv an enable weg
            return '%s<Co K="%s"%s Nc="1" U="%s">%s%s\t<In Input="%s"/>%s%s</Co>' % (
                ein, m.group(2), attr, p['ziel_u'], nl, ein, p['quelle_u'], nl, ein)
        text, n = frei_muster(p['ziel_u']).subn(ersetze, text, count=1)
        if n != 1:
            raise Abbruch('Eintragen gescheitert: %s' % p['ziel_u'])
    return text


def tabelle(plan, aus):
    kopf = ('Nr', 'Ziel (Eingang)', 'Quelle (Ausgang)', 'Listentext', 'Stand')
    zeilen = [('#%s' % p['nr'], '%s "%s" %s' % (p['ziel'].typ, p['ziel'].titel, p['ziel_k']),
               '%s "%s" %s' % (p['quelle'].typ, p['quelle'].titel, p['quelle_k']),
               p['text'], p.get('status', '?')) for p in plan]
    breite = [max(len(r[i]) for r in [kopf] + zeilen) for i in range(5)]
    for r in [kopf, tuple('-' * b for b in breite)] + zeilen:
        aus(' | '.join(r[i].ljust(breite[i]) for i in range(5)).rstrip())


def hausdatei_kern():
    """Kern des Namens der eigenen Hausdatei (Form 'Projekt_Name').

    Er steht NICHT im Quelltext, denn er traegt einen Familiennamen. Gelesen
    wird LOX_HAUSDATEI, sonst die erste Zeile von hausdatei.txt neben diesem
    Skript (privat, .gitignore). Fehlt beides, ist das Ergebnis leer.
    """
    k = os.environ.get('LOX_HAUSDATEI', '').strip()
    if k:
        return k
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hausdatei.txt')
    try:
        with open(p, encoding='utf-8') as f:
            for z in f:
                z = z.strip()
                if z and not z.startswith('#'):
                    return z
    except OSError:
        pass
    return ''


def main(argv=None):
    for strom in (sys.stdout, sys.stderr):
        try:
            strom.reconfigure(encoding='utf-8')
        except Exception:
            pass
    ap = argparse.ArgumentParser(description='Leitungen aus der Baustein-Liste in eine Loxone-Projektdatei eintragen '
                                             '(Trockenlauf ohne --schreiben).')
    ap.add_argument('projekt', help='von Loxone Config gespeicherte .Loxone-Datei (wird nie verändert)')
    ap.add_argument('--liste', required=True, help='Baustein-Liste: Textform (Nr | Typ | Name | Parameter | '
                                                   'Eingänge verbinden mit) oder gerendertes HTML')
    ap.add_argument('--abschnitt', help='Abschnitt der Liste ("===== Name" oder Überschrift vor der Tabelle)')
    ap.add_argument('--seite', help='Programmseite in Config (Titel); ohne Angabe alle Seiten')
    ap.add_argument('--weg', help='bei Zellen "HTTP-Weg: … MQTT-Weg: …" den gebauten Weg wählen (HTTP/MQTT)')
    ap.add_argument('--ohne', action='append', default=[], metavar='NR',
                    help='Listenzeile ist bewusst nicht gebaut; Leitungen von/zu ihr auslassen (mehrfach)')
    ap.add_argument('--ziel', action='append', default=[], metavar='NR=TITEL',
                    help='bei "UND → Virtueller Ausgang": Titel des Folgebausteins festlegen')
    ap.add_argument('--gleiche-lassen', action='store_true',
                    help='Eingänge, die schon mit genau dem geplanten Ausgang verbunden sind, stehen lassen '
                         '(sonst Abbruch)')
    ap.add_argument('--schreiben', metavar='ZIEL', help='Ergebnis in diese NEUE Datei schreiben')
    ap.add_argument('--ueberschreiben', action='store_true', help='ZIEL darf schon bestehen (nie die Eingabe)')
    a = ap.parse_args(argv)
    try:
        kern = hausdatei_kern()
        if not kern:
            print('HINWEIS: Schutz der Hausdatei aus - LOX_HAUSDATEI nicht gesetzt '
                  'und hausdatei.txt fehlt.', file=sys.stderr)
        elif re.search('_' + re.escape(kern), os.path.basename(a.projekt)):
            raise Abbruch('Hausdatei – das Werkzeug ist für Demo-Projekte gedacht.')
        abschnitte = liste_lesen(a.liste)
        if a.abschnitt is None:
            if len(abschnitte) != 1:
                raise Abbruch('Die Liste hat %d Abschnitte (%s); --abschnitt angeben.'
                              % (len(abschnitte), ', '.join(abschnitte)))
            a.abschnitt = next(iter(abschnitte))
        if a.abschnitt not in abschnitte:
            raise Abbruch('Abschnitt "%s" fehlt; vorhanden: %s' % (a.abschnitt, ', '.join(abschnitte)))
        zeilen = abschnitte[a.abschnitt]
        if not zeilen:
            raise Abbruch('Abschnitt "%s" hat keine Zeilen.' % a.abschnitt)
        roh, bom, text, seiten = datei_lesen(a.projekt)
        if a.seite is not None:
            gew = [s for s in seiten if s[0] == a.seite]
            if len(gew) != 1:
                raise Abbruch('Seite "%s": %d Treffer; vorhanden: %s'
                              % (a.seite, len(gew), ', '.join(s[0] for s in seiten)))
            seiten = gew
        bloecke = [b for _, bl in seiten for b in bl]
        ohne = set()
        for o in a.ohne:
            ohne |= {nr_lesen(x) for x in re.split(r'[,\s]+', o.strip().lstrip('#')) if x}  # 1.2: auch "18a"
        ziele = {}
        for zv in a.ziel:
            if '=' not in zv:
                raise Abbruch('--ziel braucht NR=TITEL: %s' % zv)
            k, t = zv.split('=', 1)
            ziele[k.strip().lstrip('#')] = t.strip()
        planer = Planer(zeilen, bloecke, a.weg, ohne, ziele, befehle_lesen_aus(text))
        plan = planer.planen()
        pruefen(text, plan, a.gleiche_lassen)

        print('Liste: %s, Abschnitt "%s" (%d Zeilen); Projekt: %s; Seite: %s'
              % (a.liste, a.abschnitt, len(zeilen), a.projekt, a.seite or 'alle'))
        tabelle(plan, print)
        neu = sum(1 for p in plan if p['status'] == 'neu')
        print('Geplant: %d Leitungen, davon neu %d, schon vorhanden %d.' % (len(plan), neu, len(plan) - neu))
        for h in planer.hinweise:
            print('Hinweis: ' + h)

        if not a.schreiben:
            print('Trockenlauf – nichts geschrieben. Zum Schreiben --schreiben ZIEL angeben.')
            return 0
        if os.path.abspath(a.schreiben) == os.path.abspath(a.projekt) or \
                (os.path.exists(a.schreiben) and os.path.samefile(a.schreiben, a.projekt)):
            raise Abbruch('ZIEL ist die Eingabedatei – das Werkzeug überschreibt sie nie.')
        if os.path.exists(a.schreiben) and not a.ueberschreiben:
            raise Abbruch('ZIEL besteht schon: %s (--ueberschreiben)' % a.schreiben)
        neu_text = eintragen(text, plan)
        daten = (b'\xef\xbb\xbf' if bom else b'') + neu_text.encode('utf-8')
        # Gegenprobe vor dem Schreiben: wohlgeformt und jede Leitung genau so vorhanden
        _, _, _, kontrolle = datei_lesen_aus(daten)
        alle = {b.u: b for _, bl in kontrolle for b in bl}
        for p in plan:
            b = alle.get(p['ziel'].u)
            if b is None or b.cos[p['ziel_k']][1] != [p['quelle_u']]:
                raise Abbruch('Gegenprobe: Leitung #%s fehlt im Ergebnis.' % p['nr'])
            if p['negiert'] and p['ziel_k'] not in b.inv:
                raise Abbruch('Gegenprobe: Eingang von #%s ist im Ergebnis nicht negiert.' % p['nr'])
        if (b'\r\n' in roh) and re.search(rb'(?<!\r)\n', daten):
            raise Abbruch('Gegenprobe: Ergebnis hat LF ohne CR.')
        with open(a.schreiben, 'wb') as f:
            f.write(daten)
        print('Geschrieben: %s (%d Bytes, %d neue Leitungen). Jetzt in Loxone Config öffnen (Gegenprobe).'
              % (a.schreiben, len(daten), neu))
        return 0
    except Abbruch as e:
        print('ABBRUCH: %s' % e, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
