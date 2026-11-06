#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nennt der MQTT-Rueckruf den Grund einer abgelehnten Anmeldung im Klartext -
unter paho 1.x UND unter paho 2.x?

DER BEFUND
----------
paho 1.x liefert die CONNACK-Codes aus MQTT 3.1.1 (1-5), paho 2.x bildet
dieselben Faelle auf die Ursachencodes von MQTT 5 ab (132-136). Ein Rueckruf,
der nur 4 und 5 kennt, meldet unter paho 2.x nur noch die nackte Zahl -
ausgerechnet bei falschen Zugangsdaten. Am Geraet gemessen (11.09.2026): die
paho-Fassung haengt am Venv JEDER Linie einzeln (dort 1.6.1 und 2.1.0 im
selben Haus), die Linie kann sich also nicht auf eine Fassung verlassen.

WAS GEMESSEN WIRD
-----------------
Die Funktion `on_connect` (bzw. der an client.on_connect gebundene Name des
Dienstes, siehe rueckrufname(); seit 02.10.2026 nicht mehr die erste Bindung
der Datei) wird aus der
Datei GESCHNITTEN und in einem eigenen Namensraum ausgefuehrt - mit Attrappen
fuer Protokoll und Client, ohne paho, ohne Broker. Dann werden Codes
durchgespielt und die Protokollzeile angesehen.

Gefragt wird nach der AUSSAGE, nicht nach einem festen Satz: zu jedem Code
muss ein Klartext erscheinen, und er muss fuer 4/134 und 5/135 dasselbe sagen.

Aufruf:  connack_klartext_pruefen.py <Datei.py> [<weitere Datei.py> ...]
Rueckgabe: 0 wie erwartet, 1 nicht, 2 nichts gemessen.
"""
import re
import sys
from pathlib import Path

# Paare, die dasselbe bedeuten muessen: (paho-1-Code, paho-2-Code, Stichwort)
PAARE = [(1, 132, None), (2, 133, None), (3, 136, None),
         (4, 134, "passwort"), (5, 135, "autorisiert")]


class Protokoll:
    """Attrappe eines Loggers: merkt sich, was gemeldet wurde."""

    def __init__(self):
        self.zeilen = []

    def _sammeln(self, text, *args):
        try:
            self.zeilen.append(str(text) % args if args else str(text))
        except Exception:                                   # noqa: BLE001
            self.zeilen.append("%s %s" % (text, args))

    error = warning = info = debug = _sammeln


class Client:
    """Attrappe des MQTT-Clients: schluckt alles."""

    def publish(self, *a, **k):
        return type("M", (), {"mid": 0})()

    def subscribe(self, *a, **k):
        return (0, 1)


class ReasonCode:
    """Nachbau des paho-2-Objekts: traegt den Wert in .value."""

    def __init__(self, wert):
        self.value = wert

    def __eq__(self, anderes):
        return self.value == getattr(anderes, "value", anderes)

    def __str__(self):
        return "ReasonCode(%d)" % self.value


def schneiden(quelle: str, name: str) -> str:
    """Den Block einer Funktion samt vorangehender Modulkonstanten holen."""
    m = re.search(r"^def %s\(.*?(?=^\S|\Z)" % re.escape(name), quelle,
                  re.S | re.M)
    if not m:
        return ""
    # Alles, was der Block an Modul-Grossbuchstaben-Tabellen braucht, kommt mit.
    tabellen = re.findall(r"^[A-Z_]+ = \{.*?^\}\n", quelle, re.S | re.M)
    return "".join(tabellen) + "\n" + m.group(0)


def rueckrufname(quelle: str) -> str:
    """Der Anmelde-Rueckruf DES DIENSTES.

    Werkzeug-C1 (02.10.2026): bis dahin galt die ERSTE Zuweisung an
    .on_connect in der Datei. In Ultraschall ist das seit 1.2.8 der
    verschachtelte Rueckruf von broker_leeren() (`k.on_connect =
    bei_verbindung`, eingerueckt, nicht schneidbar) - das Werkzeug meldete
    "nicht gemessen" statt den Rueckruf des Dienstes (`self.client.on_connect
    = mqtt_angemeldet`) zu messen. Jetzt in dieser Reihenfolge:
      1. an ein Objekt namens client gebunden (client.on_connect,
         self.client.on_connect, ...) UND als Funktion auf oberster Ebene
         definiert,
      2. sonst irgendeine Bindung an eine Funktion auf oberster Ebene,
      3. sonst wie bisher die erste Bindung, 4. sonst "on_connect".
    """
    bindungen = re.findall(r"([\w.]*)\.on_connect\s*=\s*(\w+)", quelle)
    oben = set(re.findall(r"^def (\w+)\(", quelle, re.M))
    for ziel, name in bindungen:
        if ziel.split(".")[-1].lower().endswith("client") and name in oben:
            return name
    for _ziel, name in bindungen:
        if name in oben:
            return name
    return bindungen[0][1] if bindungen else "on_connect"


def messen(datei: Path) -> dict:
    quelle = datei.read_text(encoding="utf-8", errors="replace")
    name = rueckrufname(quelle)
    block = schneiden(quelle, name)
    if not block:
        return {"fehler": "Rueckruf %s nicht gefunden" % name}
    raum = {"_LOGGER": Protokoll(), "mqtt_error": 1}
    try:
        exec(compile(block, str(datei), "exec"), raum)      # noqa: S102
    except Exception as err:                               # noqa: BLE001
        return {"fehler": "Block liess sich nicht laden: %s" % err}
    fn = raum.get(name)
    if not callable(fn):
        return {"fehler": "%s ist nicht aufrufbar" % name}

    aus = {}
    for code in [c for paar in PAARE for c in paar[:2]]:
        for form, wert in (("zahl", code), ("objekt", ReasonCode(code))):
            raum["_LOGGER"].zeilen = []
            try:
                fn(Client(), None, {}, wert)
            except Exception as err:                       # noqa: BLE001
                aus[(code, form)] = "AUSNAHME: %s" % err
                continue
            aus[(code, form)] = " | ".join(raum["_LOGGER"].zeilen)
    return {"name": name, "ausgaben": aus}


def bedeutung(text: str) -> str:
    """Der Klartextanteil einer Meldung, ohne Zahlen und Rahmen."""
    t = re.sub(r"\(?Code\s*\d+\)?|ReasonCode\(\d+\)|\d+", "", text or "")
    return re.sub(r"[^a-zA-Zaeoeuess ]+", " ", t.replace("MQTT:", "")).strip().lower()


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    fehler = 0
    # Nicht gemessen ist KEIN "wie erwartet". Bis 17.09.2026 fiel ein nicht
    # gefundener Rueckruf hier durch: 9 von 10 Dateien des Bestands waren
    # nicht gemessen, und alle 10 Laeufe meldeten "Alle Pruefungen wie
    # erwartet." mit Rueckgabe 0.
    ungemessen = 0
    for arg in sys.argv[1:]:
        d = Path(arg).resolve()
        print("== %s ==" % d.name)
        e = messen(d)
        if "fehler" in e:
            print("  [ -- ] NICHT GEMESSEN: %s" % e["fehler"])
            ungemessen += 1
            continue
        a = e["ausgaben"]
        for eins, zwei, stichwort in PAARE:
            t1 = a.get((eins, "zahl"), "")
            t2 = a.get((zwei, "objekt"), "")
            hat1, hat2 = bool(bedeutung(t1)), bool(bedeutung(t2))
            gleich = bedeutung(t1) == bedeutung(t2)
            for titel, wahr in (
                    ("Code %-3d (paho 1.x) wird benannt" % eins, hat1),
                    ("Code %-3d (paho 2.x) wird benannt" % zwei, hat2),
                    ("%d und %d sagen dasselbe" % (eins, zwei), gleich and hat1)):
                if not wahr:
                    fehler += 1
                print("  [%s] %s" % ("ok " if wahr else "FEHL", titel))
            if stichwort and stichwort not in (t2 or "").lower():
                fehler += 1
                print("  [FEHL] Code %d nennt nicht das Stichwort %r: %r"
                      % (zwei, stichwort, (t2 or "")[:90]))
        print("      Beispiel 135 (paho 2.x): %s" % (a.get((135, "objekt")) or "(nichts)")[:120])
        print("      Beispiel   5 (paho 1.x): %s" % (a.get((5, "zahl")) or "(nichts)")[:120])
    print()
    if fehler:
        print("%d Pruefung(en) NICHT wie erwartet." % fehler)
    elif ungemessen:
        print("Nichts beanstandet, aber %d von %d Datei(en) NICHT GEMESSEN - "
              "das ist kein Haken." % (ungemessen, len(sys.argv) - 1))
    else:
        print("Alle Pruefungen wie erwartet.")
    if ungemessen and fehler:
        print("Dazu %d Datei(en) NICHT GEMESSEN." % ungemessen)
    return 1 if fehler else (2 if ungemessen else 0)


if __name__ == "__main__":
    sys.exit(main())
