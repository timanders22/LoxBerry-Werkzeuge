# -*- coding: utf-8 -*-
"""Eine Wache für jeden Sprachdatei-Erzeuger: nichts verlieren, was schon da ist.

WARUM ES DIESE DATEI GIBT
=========================
Am 06.09.2026 gemessen: `Werkzeuge/ap_sprache_erzeugen.py` erzeugte 320
Schlüssel, die Datei des Plugins führte 337. Siebzehn waren nach der letzten
Fassung von Hand dazugekommen, dazu eine Umlautberichtigung. Der Kopfsatz der
`.ini` behauptete trotzdem weiterhin, sie sei von diesem Erzeuger gemacht —
ein gutgläubiger Aufruf hätte beides stillschweigend gelöscht, und aufgefallen
wäre es dem Anwender.

Am selben Tag über alle Erzeuger nachgemessen (jeder in einen leeren Ordner
bzw. gegen eine Kopie des Plugins gefahren): **vier** waren hinter ihren
Dateien zurück — `renault_` um 114 Schlüssel, `mi_` um 70, `mo_` um 13,
`sp_` um 3.

**Ein Erzeugerkopf in einer Datei ist eine Aussage über die Vergangenheit,
nie über den heutigen Stand des Erzeugers.**

WAS SIE TUT
===========
`einhaengen()` legt sich vor jeden Schreibweg, den ein Erzeuger benutzt
(`open`, `io.open`, `Path.write_text`, `Path.write_bytes`). Vor dem
Überschreiben einer `.ini` wird die vorhandene Datei gelesen und verglichen.
Verschwände ein Schlüssel, bricht der Lauf mit Rückgabewert 2 ab —
**bevor** irgendetwas geschrieben ist. Ein geänderter **Wert** ist kein
Abbruchgrund: er wird gemeldet („… bestehende Werte werden neu gefasst“)
und geschrieben; die Begründung steht in `pruefen()`.
Berichtigt am 24.09.2026: bis dahin stand hier, auch ein überschriebener
Wert breche ab. Das tat diese Wache nie; gemessen an
`fw_sprache_erzeugen.py` (Pruefung-Funkwacht-1.0.7, Sprachwache).

Der Weg über die Schreibwege statt über die Erzeuger selbst ist Absicht: die
dreizehn Erzeuger schreiben auf sieben verschiedene Arten (`ini_schreiben`,
`schreibe`, `schreiben`, `write_text`, `open(...,'wb')`, …). Eine Wache je
Erzeuger wären dreizehn Gelegenheiten, eine davon falsch zu treffen; so gibt
es eine Quelle und eine überall gleiche Einhängung.

ABSICHTLICH LÖSCHEN
===================
Wer wirklich Schlüssel entfernen will, sagt es ausdrücklich:

    SPRACHWACHE=aus python3 <erzeuger>.py <ordner>

Dann meldet die Wache, was sie durchgelassen hat, und schreibt.
"""
import io as _io
import os as _os
import re as _re
import sys as _sys

_EIN = False
_ECHT_OPEN = None
_ECHT_WRITE_TEXT = None
_ECHT_WRITE_BYTES = None


def _aus():
    return _os.environ.get('SPRACHWACHE', '').strip().lower() in (
        'aus', 'off', '0', 'nein')


def schluessel(text):
    """Die Schlüssel einer .ini als {ABSCHNITT.NAME: Wert}.

    Abschnittslos gelesene Zeilen bekämen sonst denselben Namen; deshalb
    trägt jeder Schlüssel seinen Abschnitt vor sich.

    Zwei Schreibweisen (Werkzeug-SW1, 09.10.2026): `KEY = "…"` und
    `KEY="…"`. Bis dahin zählte nur die mit Leerzeichen; der [ANSAGE]-Block,
    den die Sprachausgabe in die Sprachdateien schreibt, steht aber ohne -
    Funkwacht 1.0.12: 0 von 152 Zeilen gesehen. Ein Erzeuger, dem nur dieser
    Block fehlte, hätte ihn ohne Abbruch gelöscht.
    Die Form mit Leerzeichen wird genau wie vorher gelesen (Trennung am
    ersten ' = '), damit sich am bisher erkannten Bestand nichts verschiebt.
    Die Form ohne zählt nur, wenn vor dem ersten '=' ein schlichter Name
    steht - so wird kein Fließtext mit Gleichheitszeichen zum Schlüssel.
    """
    d = {}
    ab = ''
    for z in text.replace('\r\n', '\n').split('\n'):
        t = z.strip()
        if t.startswith('['):
            ab = t.strip('[]')
        elif t and not t.startswith(';') and ' = ' in t:
            k, v = t.split(' = ', 1)
            d[ab + '.' + k.strip()] = v.strip().strip('"')
        elif t and not t.startswith(';') and '=' in t:
            k, v = t.split('=', 1)
            k = k.strip()
            if _re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.\-]*', k):
                d[ab + '.' + k] = v.strip().strip('"')
    return d


def _lies(pfad):
    try:
        with _ECHT_OPEN(pfad, 'rb') as f:
            return f.read().decode('utf-8', 'replace')
    except (OSError, ValueError):
        return None


def pruefen(pfad, neuer_text):
    """Bricht ab, wenn ein Schlüssel verschwände oder ein Wert überschrieben
    würde. Gibt zurück, ob überhaupt etwas zu vergleichen war."""
    alt_roh = _lies(pfad)
    if alt_roh is None:
        return False                      # neue Datei - nichts zu verlieren
    alt = schluessel(alt_roh)
    if not alt:
        return False                      # keine Wertzeilen - kein Urteil
    neu = schluessel(neuer_text)
    if not neu:
        _melden(pfad, ['der neue Inhalt enthält KEINE Wertzeile - '
                       'das wäre eine leere Sprachdatei'])
        return True
    weg = sorted(set(alt) - set(neu))
    anders = sorted(k for k in set(alt) & set(neu) if alt[k] != neu[k])

    # Geänderte WERTE sind kein Abbruchgrund.
    #
    # Einen Wert zu ändern ist der Zweck eines Erzeugers; einen Schlüssel zu
    # verlieren ist es nie. Bei der Eichung am 06.09.2026 hätte die erste
    # Fassung dieser Wache `skoda_sprache_erzeugen.py` abgewiesen, weil er 63
    # Texte neu fasst — genau seine Aufgabe. Eine Wache, die den Normalfall
    # abweist, wird mit SPRACHWACHE=aus umgangen und schützt dann nie mehr.
    # Deshalb: gemeldet wird es, angehalten wird deswegen nicht.
    if anders:
        _sys.stderr.write(
            'sprachwache: %s - %d bestehende Werte werden neu gefasst: %s%s\n'
            % (_os.path.basename(str(pfad)), len(anders),
               ', '.join(anders[:6]), ' …' if len(anders) > 6 else ''))
    if not weg:
        return True
    zeilen = ['%d Schlüssel würden VERSCHWINDEN: %s%s'
              % (len(weg), ', '.join(weg[:8]), ' …' if len(weg) > 8 else '')]
    if _aus():
        _sys.stderr.write(
            'sprachwache: DURCHGELASSEN (SPRACHWACHE=aus) fuer %s\n  %s\n'
            % (pfad, '\n  '.join(zeilen)))
        return True
    _melden(pfad, zeilen)
    return True


def _melden(pfad, zeilen):
    _sys.stderr.write(
        'ABBRUCH - der Erzeuger ist hinter der Datei zurueck:\n'
        '  Datei: %s\n' % pfad)
    for z in zeilen:
        _sys.stderr.write('  %s\n' % z)
    _sys.stderr.write(
        'Es wurde NICHTS geschrieben.\n'
        'Entweder die fehlenden Schluessel in den Erzeuger nachtragen, oder\n'
        'die Datei von Hand pflegen und den Kopfsatz "ERZEUGT von ..." dort\n'
        'streichen. Absichtliches Loeschen: SPRACHWACHE=aus davorsetzen.\n')
    _sys.exit(2)


def _ist_sprachdatei(pfad):
    try:
        n = _os.path.basename(str(pfad)).lower()
    except Exception:                                     # noqa: BLE001
        return False
    return n.endswith('.ini')


class _Wachdatei:
    """Sammelt, was geschrieben werden soll, und prüft vor dem Durchreichen."""

    def __init__(self, pfad, modus, args, kwargs):
        self._pfad = pfad
        self._modus = modus
        # Die ueberzaehligen Argumente werden MITGEFUEHRT, nicht verworfen.
        # Gemessen 13.09.2026: `Path.open('w', encoding='utf-8', newline='')`
        # reicht an io.open POSITIONELL weiter - (-1, 'utf-8', None, '') -,
        # es kommt also nichts in kwargs an. Wer nur kwargs weiterreicht,
        # oeffnet die Datei beim Zurueckschreiben in der Kodierung des
        # Systems; auf Windows ist das cp1252, und der Lauf endet mit
        # UnicodeEncodeError beim ersten Pfeil im Text - oder, schlimmer,
        # schriebe eine falsch kodierte .ini.
        self._args = args
        self._kwargs = kwargs
        self._binaer = 'b' in modus
        self._stuecke = []

    def write(self, stueck):
        self._stuecke.append(stueck)
        return len(stueck)

    def writelines(self, zeilen):
        for z in zeilen:
            self.write(z)

    def _text(self):
        if self._binaer:
            roh = b''.join(self._stuecke)
            return roh.decode('utf-8', 'replace'), roh
        text = ''.join(self._stuecke)
        return text, text

    def close(self):
        if self._stuecke is None:
            return
        text, nutzlast = self._text()
        pruefen(self._pfad, text)
        with _ECHT_OPEN(self._pfad, self._modus, *self._args, **self._kwargs) as f:
            f.write(nutzlast)
        self._stuecke = None

    def flush(self):
        pass

    def __del__(self):
        # `wi_sprache_erzeugen.py` schreibt als Einzeiler:
        #     open(pfad, 'wb').write(aus)
        # ohne `with` und ohne close(). Ohne diesen Aufräumer bliebe der
        # gesammelte Inhalt liegen und die Datei ungeschrieben — die Wache
        # hätte den Erzeuger stillschweigend unwirksam gemacht. Genau die
        # Art Schaden, gegen die sie gedacht ist.
        #
        # `sys.exit()` taugt hier nicht: Python verschluckt jede Ausnahme aus
        # `__del__` ("Exception ignored in") und liefe mit Rückgabewert 0
        # weiter — ein Abbruch, den niemand merkt. Deshalb `os._exit(2)`,
        # nachdem die Begründung auf der Fehlerausgabe steht.
        try:
            self.close()
        except SystemExit:
            _sys.stderr.flush()
            _os._exit(2)
        except Exception:                                 # noqa: BLE001
            pass

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        self.close()
        return False

    def __getattr__(self, name):
        raise AttributeError(
            'sprachwache: "%s" wird auf einer ueberwachten .ini nicht '
            'unterstuetzt. Bitte die Datei in einem Stueck schreiben.' % name)


def _open(pfad, modus='r', *a, **kw):
    if ('w' in modus or 'a' in modus) and _ist_sprachdatei(pfad) \
            and 'a' not in modus:
        return _Wachdatei(pfad, modus, a, kw)
    return _ECHT_OPEN(pfad, modus, *a, **kw)


def einhaengen():
    """Ab hier wird jede .ini vor dem Ueberschreiben geprueft."""
    global _EIN, _ECHT_OPEN, _ECHT_WRITE_TEXT, _ECHT_WRITE_BYTES
    if _EIN:
        return
    import builtins
    from pathlib import Path

    _ECHT_OPEN = builtins.open
    _ECHT_WRITE_TEXT = Path.write_text
    _ECHT_WRITE_BYTES = Path.write_bytes

    def wt(selbst, daten, *a, **kw):
        if _ist_sprachdatei(selbst):
            pruefen(str(selbst), daten)
        return _ECHT_WRITE_TEXT(selbst, daten, *a, **kw)

    def wb(selbst, daten, *a, **kw):
        if _ist_sprachdatei(selbst):
            pruefen(str(selbst), daten.decode('utf-8', 'replace'))
        return _ECHT_WRITE_BYTES(selbst, daten, *a, **kw)

    builtins.open = _open
    _io.open = _open
    Path.write_text = wt
    Path.write_bytes = wb
    _EIN = True


if __name__ == '__main__':
    _sys.stderr.write(
        'sprachwache ist kein Programm, sondern ein Baustein.\n'
        'In einem Erzeuger:  import sprachwache; sprachwache.einhaengen()\n')
    _sys.exit(2)
