#!/usr/bin/env python3
"""Einzelpruefungen der Schreibbefehle des Volkswagen-Dienstes.

Auch hier gegen **echte Objekte der Bibliothek**: die Befehle sind die
richtigen Befehlsklassen von carconnectivity, nur der letzte Schritt - die
HTTPS-Anfrage an Volkswagen - ist durch einen Mitschreiber ersetzt. Damit
laeuft die Argumentzerlegung der Bibliothek wirklich mit, und ein falsch
gebauter Befehlstext faellt hier auf statt erst am Fahrzeug.

Aufruf:  vw_befehlstest.py [pfad/zu/bin/vw.py]
"""

import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # kein __pycache__ neben dem Plugin

QUELLE = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    Path(__file__).resolve().parent.parent
    / "LoxBerry-Plugin-VolkswagenID-0.9.0/LoxBerry-Plugin-VolkswagenID/bin/vw.py")
spec = importlib.util.spec_from_file_location("vw", QUELLE)
vw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vw)
vw.ntp_entschaerfen()

from carconnectivity.carconnectivity import CarConnectivity            # noqa: E402
from carconnectivity.command_impl import (ChargingStartStopCommand,    # noqa: E402
                                          ClimatizationStartStopCommand,
                                          WakeSleepCommand,
                                          WindowHeatingStartStopCommand)
from carconnectivity.units import Current, Level, Temperature          # noqa: E402
from carconnectivity.vehicle import ElectricVehicle                    # noqa: E402

OK = FAIL = 0
SPUR = []


def pruefe(name, ist, soll):
    global OK, FAIL
    if ist == soll:
        OK += 1
    else:
        FAIL += 1
        print("  [FEHL] %-52s ist=%r soll=%r" % (name, ist, soll))


CC = CarConnectivity(config={"carConnectivity": {"connectors": []}})
GARAGE = CC.get_garage()


def mitschreiber(marke):
    """Ersetzt die HTTPS-Anfrage an Volkswagen durch einen Eintrag in SPUR."""
    def haken(befehl, argumente):
        SPUR.append((marke, argumente))
        return argumente
    return haken


def setz_haken(marke):
    def haken(attribut, wert):
        SPUR.append((marke, wert))
        return wert
    return haken


def fahrzeug(mit_befehlen=True):
    v = ElectricVehicle(vin="WVWZZZE1ZPP000001", garage=GARAGE)
    v.vin._set_value("WVWZZZE1ZPP000001")
    v.climatization.settings.target_temperature._set_value(20.0, unit=Temperature.C)
    v.charging.settings.target_level._set_value(80.0, unit=Level.PERCENTAGE)
    v.charging.settings.maximum_current._set_value(16.0, unit=Current.A)
    if not mit_befehlen:
        return v
    for klasse, eltern, marke in (
            (ClimatizationStartStopCommand, v.climatization.commands, "klima"),
            (ChargingStartStopCommand, v.charging.commands, "laden"),
            (WindowHeatingStartStopCommand, v.window_heatings.commands, "scheibe"),
            (WakeSleepCommand, v.commands, "wecken")):
        c = klasse(parent=eltern)
        c._add_on_set_hook(mitschreiber(marke))
        c._is_changeable = True
        c.enabled = True
        eltern.add_command(c)
    for attribut, marke in ((v.climatization.settings.target_temperature, "zieltemp"),
                            (v.charging.settings.target_level, "ladegrenze"),
                            (v.charging.settings.maximum_current, "ladestrom")):
        attribut._add_on_set_hook(setz_haken(marke))
        attribut._is_changeable = True
    return v


CFG_AUS = dict(vw.VORGABEN, steuerung_ein=0)
CFG = dict(vw.VORGABEN, steuerung_ein=1, temp_min=16, temp_max=29)

# --- Steuerung gesperrt ----------------------------------------------------
F = [fahrzeug()]
SPUR.clear()
r = vw.befehl_ausfuehren(F, CFG_AUS, {"aktion": "klima_start", "temp": 21})
pruefe("gesperrt: abgelehnt", r[0], 0)
pruefe("gesperrt: Grund genannt", "ausgeschaltet" in r[1], True)
pruefe("gesperrt: nichts gesendet", SPUR, [])
r = vw.befehl_ausfuehren(F, CFG_AUS, {"aktion": "abruf"})
pruefe("abruf trotz Sperre", r[0], 1)

# --- Fahrzeugwahl ----------------------------------------------------------
r = vw.befehl_ausfuehren([], CFG, {"aktion": "klima_start", "temp": 21})
pruefe("ohne Fahrzeug: abgelehnt", r[0], 0)
r = vw.befehl_ausfuehren(F, CFG, {"aktion": "klima_start", "fahrzeug": "9", "temp": 21})
pruefe("Fahrzeug 9: abgelehnt", r[0], 0)
pruefe("Fahrzeug 9: Anzahl genannt", "1 Fahrzeuge" in r[1], True)

# --- Temperatur: abweisen statt kappen -------------------------------------
for temp, soll in ((35, 0), (5, 0), ("warm", 0), (None, 0), (16, 1), (29, 1), (21.5, 1)):
    SPUR.clear()
    b = {"aktion": "klima_start", "fahrzeug": "1"}
    if temp is not None:
        b["temp"] = temp
    r = vw.befehl_ausfuehren(F, CFG, b)
    pruefe("Klima %r" % temp, r[0], soll)
    if soll == 0:
        pruefe("Klima %r: nichts gesendet" % temp, SPUR, [])
r = vw.befehl_ausfuehren(F, CFG, {"aktion": "klima_start", "fahrzeug": "1", "temp": 35})
pruefe("35 Grad: Grenzen genannt", "16 bis 29" in r[1], True)

# --- Was tatsaechlich an die Bibliothek geht -------------------------------
SPUR.clear()
r = vw.befehl_ausfuehren(F, CFG, {"aktion": "klima_start", "fahrzeug": "1", "temp": "21.5"})
pruefe("Klima 21,5: angenommen", r[0], 1)
pruefe("Klima 21,5: genau ein Befehl", len(SPUR), 1)
marke, arg = SPUR[0]
pruefe("Klima: an die Klimatisierung", marke, "klima")
pruefe("Klima: Befehl start", str(arg.get("command")), "start")
pruefe("Klima: Zieltemperatur uebergeben", float(arg.get("target_temperature")), 21.5)
pruefe("Klima: Einheit Celsius", str(arg.get("target_temperature_unit")), "°C")
pruefe("Antwort sagt, dass nicht bestaetigt wurde", "naechste Abruf" in r[1], True)

SPUR.clear()
vw.befehl_ausfuehren(F, CFG, {"aktion": "klima_stop", "fahrzeug": "1"})
pruefe("Klima aus", (SPUR[0][0], str(SPUR[0][1].get("command"))), ("klima", "stop"))

SPUR.clear()
vw.befehl_ausfuehren(F, CFG, {"aktion": "laden_start", "fahrzeug": "1"})
pruefe("Laden ein", (SPUR[0][0], str(SPUR[0][1].get("command"))), ("laden", "start"))
SPUR.clear()
vw.befehl_ausfuehren(F, CFG, {"aktion": "laden_stop", "fahrzeug": "1"})
pruefe("Laden aus", (SPUR[0][0], str(SPUR[0][1].get("command"))), ("laden", "stop"))
SPUR.clear()
vw.befehl_ausfuehren(F, CFG, {"aktion": "scheibe_ein", "fahrzeug": "1"})
pruefe("Scheibe ein", (SPUR[0][0], str(SPUR[0][1].get("command"))), ("scheibe", "start"))
SPUR.clear()
vw.befehl_ausfuehren(F, CFG, {"aktion": "scheibe_aus", "fahrzeug": "1"})
pruefe("Scheibe aus", (SPUR[0][0], str(SPUR[0][1].get("command"))), ("scheibe", "stop"))
SPUR.clear()
r = vw.befehl_ausfuehren(F, CFG, {"aktion": "wecken", "fahrzeug": "1"})
pruefe("Wecken", (SPUR[0][0], str(SPUR[0][1].get("command"))), ("wecken", "wake"))

# --- Zieltemperatur als Einstellung ---------------------------------------
SPUR.clear()
r = vw.befehl_ausfuehren(F, CFG, {"aktion": "zieltemperatur", "fahrzeug": "1", "temp": 22})
pruefe("Zieltemperatur gesetzt", (r[0], SPUR[0][0], SPUR[0][1]), (1, "zieltemp", 22.0))
r = vw.befehl_ausfuehren(F, CFG, {"aktion": "zieltemperatur", "fahrzeug": "1", "temp": 40})
pruefe("Zieltemperatur 40: abgelehnt", r[0], 0)

# --- Ladegrenze ------------------------------------------------------------
for p, soll in ((80, 1), (10, 1), (100, 1), (9, 0), (101, 0), ("viel", 0)):
    SPUR.clear()
    r = vw.befehl_ausfuehren(F, CFG, {"aktion": "ladegrenze", "fahrzeug": "1", "prozent": p})
    pruefe("Ladegrenze %r" % p, r[0], soll)
    if soll == 0:
        pruefe("Ladegrenze %r: nichts gesendet" % p, SPUR, [])
SPUR.clear()
vw.befehl_ausfuehren(F, CFG, {"aktion": "ladegrenze", "fahrzeug": "1", "prozent": 70})
pruefe("Ladegrenze an die Einstellung", (SPUR[0][0], SPUR[0][1]), ("ladegrenze", 70.0))

# --- Ladestrom: nur die Stufen, die der Connector kennt --------------------
for a, soll in ((5, 1), (6, 1), (10, 1), (13, 1), (16, 1), (32, 1),
                (7, 0), (0, 0), (64, 0), ("viel", 0)):
    SPUR.clear()
    r = vw.befehl_ausfuehren(F, CFG, {"aktion": "ladestrom", "fahrzeug": "1", "ampere": a})
    pruefe("Ladestrom %r" % a, r[0], soll)
r = vw.befehl_ausfuehren(F, CFG, {"aktion": "ladestrom", "fahrzeug": "1", "ampere": 7})
pruefe("Ladestrom 7: Stufen genannt", "5, 6, 10, 13, 16, 32" in r[1], True)

# --- Fahrzeug ohne diese Faehigkeit ----------------------------------------
OHNE = [fahrzeug(mit_befehlen=False)]
for aktion, b in (("klima_start", {"temp": 21}), ("klima_stop", {}), ("laden_start", {}),
                  ("scheibe_ein", {}), ("wecken", {})):
    r = vw.befehl_ausfuehren(OHNE, CFG, dict(b, aktion=aktion, fahrzeug="1"))
    pruefe("ohne Faehigkeit: %s abgelehnt" % aktion, r[0], 0)
    pruefe("ohne Faehigkeit: %s nennt den Grund" % aktion, "bietet" in r[1], True)

# --- Erfundene Aktion ------------------------------------------------------
r = vw.befehl_ausfuehren(F, CFG, {"aktion": "sprengen", "fahrzeug": "1"})
pruefe("erfundene Aktion: abgelehnt", r[0], 0)

# --- Auswahl per Fahrgestellnummer ----------------------------------------
SPUR.clear()
r = vw.befehl_ausfuehren(F, CFG, {"aktion": "laden_start", "fahrzeug": "WVWZZZE1ZPP000001"})
pruefe("Auswahl per Fahrgestellnummer", (r[0], SPUR[0][0]), (1, "laden"))

print()
print("%d bestanden, %d durchgefallen" % (OK, FAIL))
sys.exit(1 if FAIL else 0)
