#!/usr/bin/env python3
"""Einzelpruefungen der Abbildungsfunktionen des Audi-Dienstes.

Anders als beim Skoda-Plugin wird hier NICHT gegen erfundene Attrappen
geprueft, sondern gegen **echte Objekte der Bibliothek**: es wird ein
Fahrzeug im Speicher aufgebaut, mit Werten gefuellt und durch die komplette
Abbildung geschickt. Damit ist belegt, dass die Attributnamen, die
Einheitenumrechnung und die Zustandsuebersetzung zu carconnectivity passen.

Was das NICHT belegt: ob die Audi-Schnittstelle diese Felder bei einem
echten Fahrzeug auch fuellt. Dafuer braucht es ein Konto und ein Auto.

Aufruf:  au_funktionstest.py [pfad/zu/bin/audi.py]
"""

import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True  # kein __pycache__ neben dem Plugin

QUELLE = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    Path(__file__).resolve().parent.parent
    / "LoxBerry-Plugin-AudiConnect-0.9.0/LoxBerry-Plugin-AudiConnect/bin/audi.py")
spec = importlib.util.spec_from_file_location("au", QUELLE)
au = importlib.util.module_from_spec(spec)
spec.loader.exec_module(au)
au.ntp_entschaerfen()

from carconnectivity.carconnectivity import CarConnectivity          # noqa: E402
from carconnectivity.charging import Charging                        # noqa: E402
from carconnectivity.charging_connector import ChargingConnector     # noqa: E402
from carconnectivity.climatization import Climatization              # noqa: E402
from carconnectivity.doors import Doors                              # noqa: E402
from carconnectivity.drive import CombustionDrive, ElectricDrive     # noqa: E402
from carconnectivity.lights import Lights                            # noqa: E402
from carconnectivity.units import (Current, Energy, Length, Level,   # noqa: E402
                                   Power, Speed, Temperature)
from carconnectivity.vehicle import (ElectricVehicle, GenericVehicle,  # noqa: E402
                                     HybridVehicle)
from carconnectivity.window_heating import WindowHeatings            # noqa: E402
from carconnectivity.windows import Windows                          # noqa: E402

OK = FAIL = 0


def pruefe(name, ist, soll):
    global OK, FAIL
    if ist == soll:
        OK += 1
    else:
        FAIL += 1
        print("  [FEHL] %-46s ist=%r soll=%r" % (name, ist, soll))


def leere_umgebung():
    return CarConnectivity(config={"carConnectivity": {"connectors": []}})


CC = leere_umgebung()
GARAGE = CC.get_garage()


def id4():
    """Ein vollstaendig gefuelltes Elektrofahrzeug."""
    v = ElectricVehicle(vin="WAUZZZ4M0PD000001", garage=GARAGE)
    v.vin._set_value("WAUZZZ4M0PD000001")
    v.name._set_value("Mein ID.4")
    v.model._set_value("ID.4 Pro Performance")
    v.manufacturer._set_value("Audi")
    v.model_year._set_value(2023)
    v.license_plate._set_value("XX-YY 123")
    v.odometer._set_value(23456.0, unit=Length.KM)
    v.parking_brake._set_value(True)
    v.outside_temperature._set_value(3.5, unit=Temperature.C)
    v.state._set_value(GenericVehicle.State.PARKED)
    v.type._set_value(GenericVehicle.Type.ELECTRIC)
    v.connection_state._set_value(GenericVehicle.ConnectionState.REACHABLE)
    v.software.version._set_value("3.7")
    v.doors.lock_state._set_value(Doors.LockState.LOCKED)
    v.doors.open_state._set_value(Doors.OpenState.CLOSED)
    v.windows.open_state._set_value(Windows.OpenState.OPEN)
    v.lights.light_state._set_value(Lights.LightState.OFF)
    v.window_heatings.heating_state._set_value(WindowHeatings.HeatingState.ON)
    v.climatization.state._set_value(Climatization.ClimatizationState.HEATING)
    v.climatization.settings.target_temperature._set_value(21.5, unit=Temperature.C)
    v.climatization.settings.seat_heating._set_value(True)
    v.climatization.settings.climatization_at_unlock._set_value(False)
    v.charging.state._set_value(Charging.ChargingState.CHARGING)
    v.charging.type._set_value(Charging.ChargingType.AC)
    v.charging.power._set_value(10.8, unit=Power.KW)
    v.charging.rate._set_value(48.0, unit=Speed.KMH)
    v.charging.settings.target_level._set_value(80.0, unit=Level.PERCENTAGE)
    v.charging.settings.maximum_current._set_value(16.0, unit=Current.A)
    v.charging.settings.auto_unlock._set_value(False)
    v.charging.connector.connection_state._set_value(ChargingConnector.ChargingConnectorConnectionState.CONNECTED)
    v.charging.connector.lock_state._set_value(ChargingConnector.ChargingConnectorLockState.LOCKED)
    v.charging.estimated_date_reached._set_value(datetime.now(timezone.utc) + timedelta(minutes=95))
    d = ElectricDrive(drive_id="primary", drives=v.drives)
    d.level._set_value(44.0, unit=Level.PERCENTAGE)
    d.range._set_value(210.0, unit=Length.KM)
    d.battery.total_capacity._set_value(77.0, unit=Energy.KWH)
    v.drives.drives["primary"] = d
    v.drives.total_range._set_value(210.0, unit=Length.KM)
    v.position.latitude._set_value(48.137154)
    v.position.longitude._set_value(11.576124)
    v.position.location.road._set_value("Musterweg")
    v.position.location.house_number._set_value("7")
    v.position.location.city._set_value("Musterstadt")
    v.maintenance.inspection_due_at._set_value(datetime.now(timezone.utc) + timedelta(days=201))
    v.maintenance.inspection_due_after._set_value(14000.0, unit=Length.KM)
    return v


CFG = au.config()

# ---------------------------------------------------------------------------
# Vollstaendig gefuelltes Elektrofahrzeug
# ---------------------------------------------------------------------------
A = au.fahrzeug_abbilden(id4(), CFG, 0, {})
pruefe("ok", A["ok"], 1)
pruefe("keine Ausfaelle", A["ausfaelle"], {})
pruefe("vin", A["vin"], "WAUZZZ4M0PD000001")
pruefe("modell", A["modell"], "ID.4 Pro Performance")
pruefe("baujahr", A["baujahr"], 2023)
pruefe("kennzeichen", A["kennzeichen"], "XX-YY 123")
pruefe("antriebsart", A["antriebsart"], "electric")
pruefe("software", A["software"], "3.7")
pruefe("kilometerstand", A["kilometerstand"], 23456)
pruefe("zustand geparkt", A["zustand"], 1)
pruefe("zustand_text", A["zustand_text"], "parked")
pruefe("erreichbar", A["erreichbar"], 1)
pruefe("verriegelt", A["verriegelt"], 1)
pruefe("tueren zu", A["tueren_offen"], 0)
pruefe("fenster offen", A["fenster_offen"], 1)
pruefe("licht aus", A["licht_an"], 0)
pruefe("handbremse", A["handbremse"], 1)
pruefe("aussentemperatur", A["aussentemperatur"], 3.5)
pruefe("klima an", A["klima_an"], 1)
pruefe("zieltemperatur", A["zieltemperatur"], 21.5)
pruefe("scheibenheizung", A["scheibenheizung"], 1)
pruefe("sitzheizung", A["sitzheizung_ein"], 1)
pruefe("klima bei entriegeln", A["klima_bei_entriegeln"], 0)
pruefe("soc", A["soc"], 44)
pruefe("reichweite", A["reichweite_km"], 210)
pruefe("reichweite elektro", A["reichweite_elektro_km"], 210)
pruefe("batterie kWh", A["batterie_kwh"], 77.0)
pruefe("anzahl antriebe", A["anzahl_antriebe"], 1)
pruefe("kein Tank beim Stromer", A["tank_prozent"], None)
pruefe("laedt", A["laedt"], 1)
pruefe("ladeleistung", A["ladeleistung_kw"], 10.8)
pruefe("ladetempo", A["ladetempo_kmh"], 48.0)
pruefe("ladeart", A["ladeart"], "ac")
pruefe("ladegrenze", A["ladegrenze"], 80)
pruefe("ladestrom", A["ladestrom_a"], 16)
pruefe("kabel verbunden", A["kabel_verbunden"], 1)
pruefe("stecker verriegelt", A["stecker_verriegelt"], 1)
pruefe("stecker entriegeln aus", A["stecker_entriegeln"], 0)
pruefe("breite", A["breite"], 48.137154)
pruefe("laenge", A["laenge"], 11.576124)
pruefe("adresse", A["adresse"], "Musterweg 7, Musterstadt")
pruefe("inspektion in Tagen", A["inspektion_tage"], 201)
pruefe("inspektion in km", A["inspektion_km"], 14000)
pruefe("oelservice fehlt beim Stromer", A["oelservice_tage"], None)
pruefe("laden fertig ist Zeitstempel", isinstance(A["laden_fertig_um"], int), True)

# ---------------------------------------------------------------------------
# Einheiten: Meilen und Fahrenheit muessen umgerechnet werden
# ---------------------------------------------------------------------------
v = id4()
v.odometer._set_value(10000.0, unit=Length.MI)
v.drives.total_range._set_value(100.0, unit=Length.MI)
v.outside_temperature._set_value(50.0, unit=Temperature.F)
B = au.fahrzeug_abbilden(v, CFG, 0, {})
pruefe("Meilen -> Kilometer (Zaehler)", B["kilometerstand"], 16093)
pruefe("Meilen -> Kilometer (Reichweite)", B["reichweite_km"], 161)
pruefe("Fahrenheit -> Celsius", B["aussentemperatur"], 10.0)

# ---------------------------------------------------------------------------
# Nacktes Fahrzeug: nichts darf zu 0 werden
# ---------------------------------------------------------------------------
leer = ElectricVehicle(vin="WAUZZZ4M0PD000002", garage=GARAGE)
C = au.fahrzeug_abbilden(leer, CFG, 0, {})
for feld in ("kilometerstand", "soc", "reichweite_km", "verriegelt", "tueren_offen",
             "fenster_offen", "licht_an", "klima_an", "zieltemperatur", "aussentemperatur",
             "laedt", "ladeleistung_kw", "ladegrenze", "kabel_verbunden", "breite", "laenge",
             "inspektion_tage", "inspektion_km", "zustand", "erreichbar", "scheibenheizung",
             "handbremse", "tank_prozent"):
    pruefe("leer: %s bleibt None" % feld, C[feld], None)
pruefe("leer: Adresse leer", C["adresse"], "")
pruefe("leer: trotzdem ok", C["ok"], 1)

# ---------------------------------------------------------------------------
# Hybrid: zwei Antriebe, beide Fuellstaende
# ---------------------------------------------------------------------------
h = HybridVehicle(vin="WAUZZZF5XPA000003", garage=GARAGE)
e = ElectricDrive(drive_id="primary", drives=h.drives)
e.level._set_value(61.0, unit=Level.PERCENTAGE)
e.range._set_value(48.0, unit=Length.KM)
h.drives.drives["primary"] = e
b = CombustionDrive(drive_id="secondary", drives=h.drives)
b.level._set_value(72.0, unit=Level.PERCENTAGE)
b.range._set_value(540.0, unit=Length.KM)
b.oil_level._set_value(88.0, unit=Level.PERCENTAGE)
h.drives.drives["secondary"] = b
h.drives.total_range._set_value(588.0, unit=Length.KM)
D = au.fahrzeug_abbilden(h, CFG, 0, {})
pruefe("Hybrid: zwei Antriebe", D["anzahl_antriebe"], 2)
pruefe("Hybrid: Ladezustand", D["soc"], 61)
pruefe("Hybrid: Tank", D["tank_prozent"], 72)
pruefe("Hybrid: Reichweite elektrisch", D["reichweite_elektro_km"], 48)
pruefe("Hybrid: Reichweite Verbrenner", D["reichweite_verbrenner_km"], 540)
pruefe("Hybrid: Gesamtreichweite", D["reichweite_km"], 588)
pruefe("Hybrid: Oelstand", D["oelstand_prozent"], 88)

# ---------------------------------------------------------------------------
# Zustandsuebersetzungen einzeln
# ---------------------------------------------------------------------------
v = id4()
for zustand, zahl in ((GenericVehicle.State.OFFLINE, 0), (GenericVehicle.State.PARKED, 1),
                      (GenericVehicle.State.IGNITION_ON, 2), (GenericVehicle.State.DRIVING, 3),
                      (GenericVehicle.State.UNKNOWN, None), (GenericVehicle.State.INVALID, None)):
    v.state._set_value(zustand)
    pruefe("Zustand %s" % zustand.value, au.abbild_status(v)["zustand"], zahl)
for zustand, zahl in ((Doors.LockState.LOCKED, 1), (Doors.LockState.UNLOCKED, 0),
                      (Doors.LockState.INVALID, None), (Doors.LockState.UNKNOWN, None)):
    v.doors.lock_state._set_value(zustand)
    pruefe("Verriegelung %s" % zustand.value, au.abbild_status(v)["verriegelt"], zahl)
for zustand, zahl in ((Doors.OpenState.CLOSED, 0), (Doors.OpenState.OPEN, 1),
                      (Doors.OpenState.AJAR, 1), (Doors.OpenState.UNSUPPORTED, None)):
    v.doors.open_state._set_value(zustand)
    pruefe("Tueren %s" % zustand.value, au.abbild_status(v)["tueren_offen"], zahl)
for zustand, zahl in ((Charging.ChargingState.CHARGING, 1), (Charging.ChargingState.OFF, 0),
                      (Charging.ChargingState.READY_FOR_CHARGING, 0),
                      (Charging.ChargingState.CONSERVATION, 0),
                      (Charging.ChargingState.ERROR, 0),
                      (Charging.ChargingState.UNSUPPORTED, None)):
    v.charging.state._set_value(zustand)
    pruefe("Laden %s" % zustand.value, au.abbild_laden(v)["laedt"], zahl)
for zustand, zahl in ((Climatization.ClimatizationState.OFF, 0),
                      (Climatization.ClimatizationState.HEATING, 1),
                      (Climatization.ClimatizationState.COOLING, 1),
                      (Climatization.ClimatizationState.VENTILATION, 1),
                      (Climatization.ClimatizationState.INVALID, None)):
    v.climatization.state._set_value(zustand)
    pruefe("Klima %s" % zustand.value, au.abbild_status(v)["klima_an"], zahl)

# ---------------------------------------------------------------------------
# Ein abgeschaltetes Attribut zaehlt wie ein fehlendes
# ---------------------------------------------------------------------------
v = id4()
v.odometer.enabled = False
pruefe("abgeschaltetes Attribut -> None", au.abbild_stamm(v)["kilometerstand"], None)

# ---------------------------------------------------------------------------
# Termine in der Vergangenheit ergeben negative Tage, keine 0
# ---------------------------------------------------------------------------
v = id4()
v.maintenance.inspection_due_at._set_value(datetime.now(timezone.utc) - timedelta(days=12))
pruefe("ueberfaellige Inspektion", au.abbild_wartung(v)["inspektion_tage"], -12)

# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------
pruefe("wert_zahl None", au.wert_zahl(None), None)
pruefe("wert_zahl leer", au.wert_zahl(""), None)
pruefe("wert_zahl Text", au.wert_zahl("warm"), None)
pruefe("wert_zahl 21", au.wert_zahl("21"), 21)
pruefe("wert_zahl 21,5", au.wert_zahl("21,5"), 21.5)
pruefe("wert(None)", au.wert(None), None)
pruefe("etext(None)", au.etext(None), "")
pruefe("kennzahl unbekannt", au.kennzahl(None, au.VERRIEGELT), None)

liste = [id4()]
pruefe("Fahrzeugwahl per Nummer", au.fahrzeug_waehlen(liste, "1") is liste[0], True)
pruefe("Fahrzeugwahl per VIN", au.fahrzeug_waehlen(liste, "wvwzzze1zpp000001") is liste[0], True)
pruefe("Fahrzeugwahl zu gross", au.fahrzeug_waehlen(liste, "5"), None)
pruefe("Fahrzeugwahl leere Liste", au.fahrzeug_waehlen([], "1"), None)

# ---------------------------------------------------------------------------
# Takt: die Bibliothek verlangt mindestens 180 s
# ---------------------------------------------------------------------------
import json as _json                                                  # noqa: E402
tmp = Path("/tmp/vwtest_cfg.json")
tmp.parent.mkdir(parents=True, exist_ok=True)
au.DATEI_CONFIG = tmp
tmp.write_text(_json.dumps({"intervall": 30, "temp_min": 28, "temp_max": 17,
                            "takt_wartung": 0, "verlauf_tage": 999}))
c = au.config()
pruefe("Takt auf 180 gekappt", c["intervall"], 180)
pruefe("Temperaturen getauscht", (c["temp_min"], c["temp_max"]), (17, 28))
pruefe("Wartungstakt gekappt", c["takt_wartung"], 1)
pruefe("Verlauf gekappt", c["verlauf_tage"], 90)
tmp.write_text("{ kaputt")
pruefe("unlesbare Konfiguration -> Vorgaben", au.config()["intervall"], 300)

# ---------------------------------------------------------------------------
# Die Konfiguration fuer die Bibliothek muss die Untergrenze einhalten
# ---------------------------------------------------------------------------
bc = au.bibliothek_config({"email": "a@b.de", "passwort": "x", "spin": ""},
                          dict(au.VORGABEN, intervall=30))
pruefe("Bibliothekstakt nie unter 180", bc["carConnectivity"]["connectors"][0]["config"]["interval"], 180)
pruefe("ohne S-PIN kein Eintrag", "spin" in bc["carConnectivity"]["connectors"][0]["config"], False)
bc = au.bibliothek_config({"email": "a@b.de", "passwort": "x", "spin": "1234"}, au.VORGABEN)
pruefe("mit S-PIN", bc["carConnectivity"]["connectors"][0]["config"]["spin"], "1234")
pruefe("Connector-Typ", bc["carConnectivity"]["connectors"][0]["type"], "audi")
# force_enable_access kennt der Audi-Connector nicht - anders als der fuer
# Volkswagen. Stuende es hier, laege ein unbekannter Schluessel in der
# Konfiguration.
pruefe("kein force_enable_access",
       "force_enable_access" in bc["carConnectivity"]["connectors"][0]["config"], False)

# ---------------------------------------------------------------------------
# Der Audi-Connector muss die Befehle wirklich anbieten, die das Plugin
# benutzt. Geprueft wird an seinem Quelltext, nicht an einer Vermutung -
# er ist jung, und was heute da ist, muss morgen nicht da sein.
# ---------------------------------------------------------------------------
import inspect as _inspect                                            # noqa: E402
import carconnectivity_connectors.audi.connector as _acon             # noqa: E402
_quelle = _inspect.getsource(_acon)
for _name in ("ClimatizationStartStopCommand", "ChargingStartStopCommand",
              "WindowHeatingStartStopCommand", "WakeSleepCommand"):
    pruefe("Connector registriert %s" % _name, _name + "(parent" in _quelle, True)
for _attr in ("target_temperature", "target_level", "maximum_current"):
    pruefe("Connector macht %s aenderbar" % _attr,
           "settings.%s._is_changeable" % _attr in _quelle, True)
pruefe("Untergrenze 180 s im Connector",
       "Intervall must be at least 180 seconds" in _quelle, True)
pruefe("Untergrenze 180 s im Plugin", au.TAKT_MIN, 180)
pruefe("Connector meldet sich als audi", _acon.Connector.get_type(None),
       "carconnectivity-connector-audi")

# Und die Bibliothek muss sie auch annehmen - hier faellt auf, wenn sich das
# Format aendert. Ohne Netz scheitert danach die Anmeldung; das ist erwartet
# und beweist zugleich, dass die Konfiguration bis zur Anmeldung durchkam.
# Ein ConfigurationError dagegen waere ein echter Befund.
try:
    CarConnectivity(config=au.bibliothek_config(
        {"email": "a@b.de", "passwort": "x", "spin": ""}, au.VORGABEN))
    pruefe("Bibliothek nimmt die Konfiguration an", True, True)
except Exception as err:                                              # noqa: BLE001
    art = type(err).__name__
    text = str(err).lower()
    netzfehler = ("connection" in text or "proxy" in text or "timed out" in text
                  or "name resolution" in text or "max retries" in text)
    if art == "ConfigurationError":
        pruefe("Bibliothek nimmt die Konfiguration an", "ConfigurationError: " + str(err),
               "kein Konfigurationsfehler")
    elif netzfehler or art in ("AuthenticationError", "TemporaryAuthenticationError",
                               "RetrievalError", "APIError"):
        # Bis hierher kam sie nur, weil die Konfiguration gueltig war.
        pruefe("Bibliothek nimmt die Konfiguration an (Anmeldung ohne Netz erwartet gescheitert: "
               "%s)" % art, True, True)
    else:
        pruefe("Bibliothek nimmt die Konfiguration an", art + ": " + str(err), "kein Fehler")

print()
print("%d bestanden, %d durchgefallen" % (OK, FAIL))
sys.exit(1 if FAIL else 0)
