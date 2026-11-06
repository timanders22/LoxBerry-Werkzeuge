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


def frische_bremse():
    """Setzt die Drosselung zurueck.

    Seit 0.9.12 trennt das Plugin fragen und buchen: ein abgewiesener Befehl
    verbraucht kein Kontingent mehr und setzt keine Entprellmarke. Bis dahin
    hat dieser Test unbemerkt davon gelebt - er schickt zweimal
    hintereinander 'klima_start' mit 21,5 Grad, und nur weil ein
    dazwischenliegender ABGELEHNTER Befehl (35 Grad) die Marke ueberschrieb,
    lief der zweite durch. Jetzt entprellt der Test sich sonst selbst.

    Vor jedem Block, der NICHT die Drosselung misst, wird sie zurueckgesetzt.
    Der Block, der sie misst, steht am Ende und setzt sie selbst.
    """
    vw._BREMSE = vw.Bremse()


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
    # Die Ja/Nein-Einstellungen - genau so, wie der echte Connector sie
    # anlegt. Am Geraet gemessen (Connector 0.10.6, 06.09.2026): diese drei
    # tragen _is_changeable UND einen Schreibhaken.
    for attribut, marke in (
            (v.climatization.settings.climatization_at_unlock, "klima_entriegeln"),
            (v.climatization.settings.climatization_without_external_power,
             "klima_ohne_netz"),
            (v.charging.settings.auto_unlock, "stecker_auto")):
        attribut._add_on_set_hook(setz_haken(marke))
        attribut._is_changeable = True
    # 'seat_heating' bekommt BEIDES NICHT - der Connector macht es nicht
    # schreibbar, es ist dort ein abgeleiteter Anzeigewert aus den vier
    # Sitzzonen. Wer diese Zeile "der Vollstaendigkeit halber" ergaenzt,
    # macht den Pruefstand grosszuegiger als das Geraet und deckt genau den
    # Fehler zu, fuer den es ihn gibt.
    return v


CFG_AUS = dict(vw.VORGABEN, steuerung_ein=0)
CFG = dict(vw.VORGABEN, steuerung_ein=1, temp_min=16, temp_max=29)

frische_bremse()
# --- Steuerung gesperrt ----------------------------------------------------
F = [fahrzeug()]
SPUR.clear()
r = vw.befehl_ausfuehren(F, CFG_AUS, {"aktion": "klima_start", "temp": 21})
pruefe("gesperrt: abgelehnt", r[0], 0)
pruefe("gesperrt: Grund genannt", "ausgeschaltet" in r[1], True)
pruefe("gesperrt: nichts gesendet", SPUR, [])
r = vw.befehl_ausfuehren(F, CFG_AUS, {"aktion": "abruf"})
pruefe("abruf trotz Sperre", r[0], 1)

frische_bremse()
# --- Fahrzeugwahl ----------------------------------------------------------
r = vw.befehl_ausfuehren([], CFG, {"aktion": "klima_start", "temp": 21})
pruefe("ohne Fahrzeug: abgelehnt", r[0], 0)
r = vw.befehl_ausfuehren(F, CFG, {"aktion": "klima_start", "fahrzeug": "9", "temp": 21})
pruefe("Fahrzeug 9: abgelehnt", r[0], 0)
pruefe("Fahrzeug 9: Anzahl genannt", "1 Fahrzeuge" in r[1], True)

frische_bremse()
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

frische_bremse()
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

frische_bremse()
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

frische_bremse()
# --- Ladestrom: nur die Stufen, die der Connector kennt --------------------
for a, soll in ((5, 1), (6, 1), (10, 1), (13, 1), (16, 1), (32, 1),
                (7, 0), (0, 0), (64, 0), ("viel", 0)):
    SPUR.clear()
    r = vw.befehl_ausfuehren(F, CFG, {"aktion": "ladestrom", "fahrzeug": "1", "ampere": a})
    pruefe("Ladestrom %r" % a, r[0], soll)
r = vw.befehl_ausfuehren(F, CFG, {"aktion": "ladestrom", "fahrzeug": "1", "ampere": 7})
pruefe("Ladestrom 7: Stufen genannt", "5, 6, 10, 13, 16, 32" in r[1], True)

frische_bremse()
# --- Fahrzeug ohne diese Faehigkeit ----------------------------------------
OHNE = [fahrzeug(mit_befehlen=False)]
for aktion, b in (("klima_start", {"temp": 21}), ("klima_stop", {}), ("laden_start", {}),
                  ("scheibe_ein", {}), ("wecken", {})):
    r = vw.befehl_ausfuehren(OHNE, CFG, dict(b, aktion=aktion, fahrzeug="1"))
    pruefe("ohne Faehigkeit: %s abgelehnt" % aktion, r[0], 0)
    pruefe("ohne Faehigkeit: %s nennt den Grund" % aktion, "bietet" in r[1], True)

frische_bremse()
# --- Erfundene Aktion ------------------------------------------------------
r = vw.befehl_ausfuehren(F, CFG, {"aktion": "sprengen", "fahrzeug": "1"})
pruefe("erfundene Aktion: abgelehnt", r[0], 0)

frische_bremse()
# --- Auswahl per Fahrgestellnummer ----------------------------------------
SPUR.clear()
r = vw.befehl_ausfuehren(F, CFG, {"aktion": "laden_start", "fahrzeug": "WVWZZZE1ZPP000001"})
pruefe("Auswahl per Fahrgestellnummer", (r[0], SPUR[0][0]), (1, "laden"))

# --- Drosselung: gebucht wird, was hinausgeht -------------------------------
#
# Die Eichung zu S3 (0.9.12). Sie gehoert dauerhaft hierher, weil kein
# anderes Werkzeug diese Reihenfolge misst.
#
# Vorher gemessen (0.9.11): sechs inhaltlich falsche Befehle ergaben
# "gebucht=6, gesendet=0"; nach dreissig davon wurde ein gueltiger Befehl
# abgewiesen. Nachher (0.9.12): gebucht=0, und der gueltige Befehl geht durch.
frische_bremse()
SPUR.clear()
CFG_BR = dict(CFG, befehle_stunde=6, entprellung=0)
for wert in (7, 0, 64, 99, 3, 1):
    vw.befehl_ausfuehren(F, CFG_BR, {"aktion": "ladestrom", "fahrzeug": "1",
                                     "ampere": wert})
pruefe("Bremse: sechs falsche Befehle - nichts gesendet", len(SPUR), 0)
pruefe("Bremse: sechs falsche Befehle - nichts gebucht", len(vw._BREMSE.stunde), 0)
r = vw.befehl_ausfuehren(F, CFG_BR, {"aktion": "ladestrom", "fahrzeug": "1",
                                     "ampere": 16})
pruefe("Bremse: der gueltige Befehl danach geht durch", r[0], 1)
pruefe("Bremse: und wird gebucht", len(vw._BREMSE.stunde), 1)

# Die Grenze greift trotzdem - sie zaehlt nur das Richtige.
frische_bremse()
SPUR.clear()
CFG_BR2 = dict(CFG, befehle_stunde=3, entprellung=0)
for wert in (5, 6, 10, 13):
    vw.befehl_ausfuehren(F, CFG_BR2, {"aktion": "ladestrom", "fahrzeug": "1",
                                      "ampere": wert})
pruefe("Bremse: Obergrenze greift", len(SPUR), 3)
r = vw.befehl_ausfuehren(F, CFG_BR2, {"aktion": "ladestrom", "fahrzeug": "1",
                                      "ampere": 16})
pruefe("Bremse: der vierte wird abgewiesen", r[0], 0)
pruefe("Bremse: mit der Obergrenze als Grund", "Obergrenze" in r[1], True)

# Entprellung: derselbe Befehl mit demselben Wert geht nicht zweimal.
frische_bremse()
SPUR.clear()
CFG_EP = dict(CFG, befehle_stunde=0, entprellung=60)
vw.befehl_ausfuehren(F, CFG_EP, {"aktion": "ladestrom", "fahrzeug": "1", "ampere": 16})
r = vw.befehl_ausfuehren(F, CFG_EP, {"aktion": "ladestrom", "fahrzeug": "1", "ampere": 16})
pruefe("Entprellung: derselbe Wert wird gehalten", r[0], 0)
pruefe("Entprellung: nur einmal gesendet", len(SPUR), 1)
r = vw.befehl_ausfuehren(F, CFG_EP, {"aktion": "ladestrom", "fahrzeug": "1", "ampere": 13})
pruefe("Entprellung: ein ANDERER Wert geht durch", r[0], 1)

# Ein abgewiesener Befehl setzt KEINE Entprellmarke.
frische_bremse()
SPUR.clear()
vw.befehl_ausfuehren(F, CFG_EP, {"aktion": "ladestrom", "fahrzeug": "1", "ampere": 7})
r = vw.befehl_ausfuehren(F, CFG_EP, {"aktion": "ladestrom", "fahrzeug": "1", "ampere": 16})
pruefe("Abgewiesener Befehl setzt keine Marke", r[0], 1)

# --- Ja/Nein-Einstellungen: schaltbar und nur lesend ------------------------
#
# Am Geraet gemessen (06.09.2026, Connector 0.10.6): drei der vier bisherigen
# Schalter sind im Connector schreibbar, 'sitzheizung' nicht - dort ist
# 'seat_heating' ein abgeleiteter Anzeigewert aus den vier Sitzzonen.
# Seit 0.9.14 fuehrt der Dienst deshalb zwei Listen.
frische_bremse()
if hasattr(vw, "NUR_LESEND"):
    for name in sorted(vw.SCHALTER):
        SPUR.clear()
        r = vw.befehl_ausfuehren(F, CFG, {"aktion": "einstellung", "fahrzeug": "1",
                                          "name": name, "wert": 1})
        pruefe("Einstellung %s: angenommen" % name, r[0], 1)
    for name in sorted(vw.NUR_LESEND):
        SPUR.clear()
        r = vw.befehl_ausfuehren(F, CFG, {"aktion": "einstellung", "fahrzeug": "1",
                                          "name": name, "wert": 1})
        pruefe("Nur lesend %s: abgewiesen" % name, r[0], 0)
        pruefe("Nur lesend %s: nichts gesendet" % name, SPUR, [])
        # Die Meldung muss den GRUND nennen, nicht nur "unbekannt" - sonst
        # sucht der Betreiber den Fehler bei sich.
        pruefe("Nur lesend %s: Grund genannt" % name,
               "nicht setzen" in r[1] or "not " in r[1].lower(), True)
        pruefe("Nur lesend %s: sagt, was stattdessen geht" % name,
               any(s in r[1] for s in vw.SCHALTER), True)
        pruefe("Nur lesend %s: nicht als unbekannt abgetan" % name,
               "Unbekannte Einstellung" in r[1], False)
    # Kein Name steht in beiden Listen.
    pruefe("Listen ueberschneiden sich nicht",
           sorted(set(vw.SCHALTER) & set(vw.NUR_LESEND)), [])
r = vw.befehl_ausfuehren(F, CFG, {"aktion": "einstellung", "fahrzeug": "1",
                                  "name": "gibtesnicht", "wert": 1})
pruefe("Erfundene Einstellung: abgewiesen", r[0], 0)

print()
print("%d bestanden, %d durchgefallen" % (OK, FAIL))
sys.exit(1 if FAIL else 0)
