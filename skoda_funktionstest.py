#!/usr/bin/env python3
"""Einzelpruefungen der Abbildungsfunktionen des Skoda-Dienstes.

Laedt bin/skoda.py und prueft die Funktionen einzeln gegen erfundene Antworten.
Das ersetzt KEIN Fahrzeug: geprueft wird die Zuordnung und das Abweisen
ungueltiger Eingaben, nicht ob die Feldnamen der Skoda-Cloud stimmen.

Aufruf:  skoda_funktionstest.py [pfad/zu/bin/skoda.py]
"""
import sys

# Kein __pycache__ neben dem Plugin anlegen - es darf nicht ins Archiv.
sys.dont_write_bytecode = True
import importlib.util, sys, types, os, json, re
from pathlib import Path

QUELLE = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    Path(__file__).resolve().parent.parent
    / "LoxBerry-Plugin-SkodaConnect-0.9.0/LoxBerry-Plugin-SkodaConnect/bin/skoda.py")
spec = importlib.util.spec_from_file_location("skoda", QUELLE)
sk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sk)

ok = fail = 0
def pruefe(name, ist, soll):
    global ok, fail
    if ist == soll:
        ok += 1
    else:
        fail += 1
        print("  [FEHL] %-40s ist=%r soll=%r" % (name, ist, soll))

class O:
    def __init__(self, **kw):
        for k, v in kw.items(): setattr(self, k, v)

class E(str):
    """Enum-artig: hat .value wie die StrEnum der Bibliothek."""
    @property
    def value(self): return str(self)

# --- zahl() ---
pruefe("zahl None", sk.zahl(None), None)
pruefe("zahl leer", sk.zahl(""), None)
pruefe("zahl text", sk.zahl("abc"), None)
pruefe("zahl 21.5 -> int", sk.zahl("21.5"), 22)
pruefe("zahl 21,5 mit Nachkomma", sk.zahl("21,5", 1), 21.5)
pruefe("zahl 0 bleibt 0", sk.zahl(0), 0)
pruefe("zahl bool -> None (keine stille 0)", sk.zahl(False), None)

# --- hole() ---
pruefe("hole tief", sk.hole(O(a=O(b=O(c=7))), "a","b","c"), 7)
pruefe("hole fehlend", sk.hole(O(a=None), "a","b"), None)
pruefe("hole gar nicht da", sk.hole(None, "a"), None)

# --- text() / kennzahl() ---
pruefe("text enum", sk.text(E("LOCKED")), "LOCKED")
pruefe("text None", sk.text(None), "")
pruefe("kennzahl verriegelt YES", sk.kennzahl(E("YES"), sk.VERRIEGELT), 1)
pruefe("kennzahl verriegelt NO", sk.kennzahl(E("NO"), sk.VERRIEGELT), 0)
pruefe("kennzahl unbekannt -> None", sk.kennzahl(E("UNKNOWN"), sk.VERRIEGELT), None)
pruefe("kennzahl offen OPEN", sk.kennzahl(E("OPEN"), sk.OFFEN_ZU), 1)
pruefe("kennzahl offen UNSUPPORTED", sk.kennzahl(E("UNSUPPORTED"), sk.OFFEN_ZU), None)
pruefe("kennzahl klima HEATING", sk.kennzahl(E("HEATING"), sk.KLIMA_AN), 1)
pruefe("kennzahl klima OFF", sk.kennzahl(E("OFF"), sk.KLIMA_AN), 0)
pruefe("kennzahl laden CHARGING", sk.kennzahl(E("CHARGING"), sk.LADEN_AN), 1)
pruefe("kennzahl laden CONSERVING", sk.kennzahl(E("CONSERVING"), sk.LADEN_AN), 0)

# --- abbild_status ---
st = O(overall=O(locked=E("YES"), doors_locked=E("YES"), doors=E("CLOSED"),
                 windows=E("OPEN"), lights=E("OFF")),
       detail=O(bonnet=E("CLOSED"), trunk=E("OPEN"), sunroof=E("UNSUPPORTED")))
d = sk.abbild_status(st)
pruefe("status verriegelt", d["verriegelt"], 1)
pruefe("status fenster offen", d["fenster_offen"], 1)
pruefe("status kofferraum", d["kofferraum_offen"], 1)
pruefe("status schiebedach unbekannt", d["schiebedach_offen"], None)
pruefe("status licht", d["licht_an"], 0)
pruefe("status einzeltuer ohne Bildadresse", d["tuer_vorn_links"], None)

# --- abbild_reichweite ---
dr = O(total_range_in_km=412, car_type=E("hybrid"),
       primary_engine_range=O(engine_type=E("gasoline"), current_soc_in_percent=None,
                              current_fuel_level_in_percent=63, remaining_range_in_km=380),
       secondary_engine_range=O(engine_type=E("electric"), current_soc_in_percent=44,
                                current_fuel_level_in_percent=None, remaining_range_in_km=32),
       ad_blue_range=None)
d = sk.abbild_reichweite(dr)
pruefe("reichweite gesamt", d["reichweite_km"], 412)
pruefe("reichweite tank", d["tank_prozent"], 63)
pruefe("reichweite soc fehlt -> None", d["soc"], None)
pruefe("reichweite soc sekundaer", d["soc_sekundaer"], 44)
pruefe("reichweite adblue None", d["adblue_km"], None)

# --- abbild_laden ---
ch = O(status=O(battery=O(state_of_charge_in_percent=44,
                          remaining_cruising_range_in_meters=32000),
                state=E("CHARGING"), charge_power_in_kw=10.83,
                charging_rate_in_kilometers_per_hour=48.0, charge_type=E("AC"),
                remaining_time_to_fully_charged_in_minutes=95),
       settings=O(target_state_of_charge_in_percent=80, preferred_charge_mode=E("MANUAL"),
                  max_charge_current_ac=E("MAXIMUM"), charging_care_mode=E("DEACTIVATED"),
                  auto_unlock_plug_when_charged=E("OFF")),
       is_vehicle_in_saved_location=True)
d = sk.abbild_laden(ch)
pruefe("laden soc", d["soc"], 44)
pruefe("laden laedt", d["laedt"], 1)
pruefe("laden kw", d["ladeleistung_kw"], 10.8)
pruefe("laden restzeit", d["restzeit_min"], 95)
pruefe("laden grenze", d["ladegrenze"], 80)
pruefe("laden reichweite noch leer", d["reichweite_batterie_km"], None)
pruefe("meter->km Umrechnung", sk.zahl(32000/1000), 32)

# --- abbild_klima ---
ac = O(state=E("VENTILATION"), target_temperature=O(temperature_value=21.5),
       outside_temperature=O(temperature_value=4.0),
       window_heating_state=O(front=E("ON"), rear=E("OFF")),
       charger_connection_state=E("CONNECTED"), charger_lock_state=E("LOCKED"),
       heater_source=E("ELECTRIC"),
       seat_heating_activated=O(front_left=True, front_right=False),
       estimated_date_time_to_reach_target_temperature=None)
d = sk.abbild_klima(ac)
pruefe("klima an", d["klima_an"], 1)
pruefe("klima ziel", d["zieltemperatur"], 21.5)
pruefe("klima aussen", d["aussentemperatur"], 4.0)
pruefe("klima scheibe vorn", d["scheibe_vorn"], 1)
pruefe("klima scheibe hinten", d["scheibe_hinten"], 0)
pruefe("klima kabel", d["kabel_verbunden"], 1)
pruefe("klima sitz links", d["sitzheizung_vorn_links"], 1)

# --- Klima ohne Werte: nichts wird zu 0 ---
d = sk.abbild_klima(O(state=None, target_temperature=None, outside_temperature=None,
                      window_heating_state=None, charger_connection_state=None,
                      charger_lock_state=None, heater_source=None,
                      seat_heating_activated=None,
                      estimated_date_time_to_reach_target_temperature=None))
pruefe("klima leer: ziel None", d["zieltemperatur"], None)
pruefe("klima leer: aussen None", d["aussentemperatur"], None)
pruefe("klima leer: scheibe None", d["scheibe_vorn"], None)

# --- abbild_position ---
po = O(positions=[O(type=E("PARKING"), gps_coordinates=O(latitude=1.0, longitude=2.0), address=None),
                  O(type=E("VEHICLE"), gps_coordinates=O(latitude=48.137154, longitude=11.576124),
                    address=O(city="Musterstadt", street="Musterweg", house_number="7"))])
d = sk.abbild_position(po)
pruefe("position breite", d["breite"], 48.137154)
pruefe("position adresse", d["adresse"], "Musterweg 7, Musterstadt")
d = sk.abbild_position(O(positions=[]))
pruefe("position leer", d["breite"], None)

# --- gesundheit / wartung / verbindung ---
he = O(warning_lights=[O(category=E("TIRE"), defects=[]), O(category=E("BRAKE"), defects=[])],
       mileage_in_km=54321)
d = sk.abbild_gesundheit(he)
pruefe("gesundheit km", d["kilometerstand"], 54321)
pruefe("gesundheit warn", d["warnleuchten"], 2)
pruefe("gesundheit text", d["warnleuchten_text"], "TIRE, BRAKE")

ma = O(maintenance_report=O(inspection_due_in_days=201, inspection_due_in_km=14000,
                            oil_service_due_in_days=None, oil_service_due_in_km=None,
                            mileage_in_km=54321))
d = sk.abbild_wartung(ma)
pruefe("wartung insp tage", d["inspektion_tage"], 201)
pruefe("wartung oel None", d["oelservice_tage"], None)
d = sk.abbild_wartung(O(maintenance_report=None))
pruefe("wartung ohne Bericht", d["inspektion_tage"], None)

vs = O(unreachable=False, in_motion=True, ignition_on=None)
d = sk.abbild_verbindung(vs)
pruefe("verbindung erreichbar", d["erreichbar"], 1)
pruefe("verbindung bewegung", d["in_bewegung"], 1)
pruefe("verbindung zuendung unbekannt", d["zuendung_an"], None)

# --- vin_waehlen ---
vins = ["TMBAAA000AA000001", "TMBBBB000BB000002"]
pruefe("vin per Nummer 1", sk.vin_waehlen(vins, "1"), vins[0])
pruefe("vin per Nummer 2", sk.vin_waehlen(vins, 2), vins[1])
pruefe("vin per VIN", sk.vin_waehlen(vins, "tmbbbb000bb000002"), vins[1])
pruefe("vin zu gross", sk.vin_waehlen(vins, "9"), None)
pruefe("vin Muell -> 1", sk.vin_waehlen(vins, "quatsch"), vins[0])
pruefe("vin leere Liste", sk.vin_waehlen([], "1"), None)

# --- kann() ---
pruefe("kann ohne Liste", sk.kann({}, "CHARGING"), True)
pruefe("kann mit Liste ja", sk.kann({"faehigkeiten": ["CHARGING"]}, "CHARGING"), True)
pruefe("kann mit Liste nein", sk.kann({"faehigkeiten": ["STATE"]}, "CHARGING"), False)

# --- fehlertext ---
class TermsAndConditionsError(Exception): pass
class AuthorizationFailedError(Exception): pass
class Http(Exception):
    def __init__(self, s): super().__init__("boom"); self.status = s
pruefe("fehler AGB", "Nutzungsbedingungen" in sk.fehlertext(TermsAndConditionsError()), True)
pruefe("fehler Anmeldung", "Passwort" in sk.fehlertext(AuthorizationFailedError()), True)
pruefe("fehler 429", "429" in sk.fehlertext(Http(429)), True)
pruefe("fehler 404", "404" in sk.fehlertext(Http(404)), True)
pruefe("fehler 503 nicht LoxBerry", "nicht am LoxBerry" in sk.fehlertext(Http(503)), True)
pruefe("fehler HTML statt JSON", "HTML statt JSON" in sk.fehlertext(Exception("<html><body>Fehler")), True)
class OSErr(Exception):
    def __init__(self): super().__init__("x"); self.errno = 111
pruefe("fehler ECONNREFUSED", "ECONNREFUSED" in sk.fehlertext(OSErr()), True)

# --- config()-Grenzen ---
sk.DATEI_CONFIG = Path("/tmp/sktest/leer.json")
c = sk.config()
pruefe("config Vorgabe Takt", c["intervall"], 300)
Path("/tmp/sktest/cfg.json").write_text(json.dumps(
    {"intervall": 5, "temp_min": 28, "temp_max": 17, "verlauf_tage": 999,
     "takt_stamm": 0}))
sk.DATEI_CONFIG = Path("/tmp/sktest/cfg.json")
c = sk.config()
pruefe("config Takt gekappt", c["intervall"], 60)
pruefe("config Temperaturen getauscht", (c["temp_min"], c["temp_max"]), (17, 28))
pruefe("config Verlauf gekappt", c["verlauf_tage"], 90)
pruefe("config takt_stamm gekappt", c["takt_stamm"], 1)
Path("/tmp/sktest/cfg.json").write_text('{ kaputt')
c = sk.config()
pruefe("config unlesbar -> Vorgaben", c["intervall"], 300)

print()
print("%d bestanden, %d durchgefallen" % (ok, fail))
sys.exit(1 if fail else 0)
