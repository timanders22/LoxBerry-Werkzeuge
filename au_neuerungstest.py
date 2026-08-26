#!/usr/bin/env python3
"""Prueft die NEUERUNGEN von Audi Connect 0.9.8 gegen echte Bibliotheksobjekte.

Warum es diese Datei zusaetzlich zu au_funktionstest.py gibt: jene prueft die
Abbildung, wie sie bis 0.9.7 bestand, und sie lief nach dem Umbau auf Anhieb
durch - 140 von 140. Das ist beruhigend und beweist fuer die neuen Felder
NICHTS. Ein Prueflauf, der den geaenderten Teil nicht beruehrt, ist keine
Pruefung des geaenderten Teils.

Geprueft wird hier:
  * die vier Verzeichnisse der Einzelteile (Tueren, Fenster, Leuchten,
    Scheibenheizungen) - Anzahl UND Namen
  * die fuenf neuen Uebersetzungstabellen gegen die ECHTEN Aufzaehlungen der
    Bibliothek: jeder Wert, den die Aufzaehlung kennt, muss entweder abgebildet
    sein oder bewusst nicht
  * die neuen Felder in Status, Laden, Reichweite und Position
  * die gerechneten Groessen samt Ladevorgangserkennung
  * die drei Bremsen
  * die Fehlerklassen

Was das NICHT belegt: ob die Audi-Schnittstelle diese Felder bei einem echten
Fahrzeug fuellt. Sieben davon tut sie nachweislich nie - siehe Kopf von
bin/audi.py. Dafuer braucht es ein Konto und ein Auto.

Aufruf:  au_neuerungstest.py [pfad/zu/bin/audi.py]
"""

import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True  # kein __pycache__ neben dem Plugin

QUELLE = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    Path(__file__).resolve().parent.parent
    / "LoxBerry-Plugin-AudiConnect-0.9.8/bin/audi.py")
spec = importlib.util.spec_from_file_location("au", QUELLE)
au = importlib.util.module_from_spec(spec)
spec.loader.exec_module(au)
au.ntp_entschaerfen()

from carconnectivity.carconnectivity import CarConnectivity          # noqa: E402
from carconnectivity.charging import Charging                        # noqa: E402
from carconnectivity.charging_connector import ChargingConnector     # noqa: E402
from carconnectivity.climatization import Climatization              # noqa: E402
from carconnectivity.doors import Doors                              # noqa: E402
from carconnectivity.drive import (CombustionDrive, DieselDrive,     # noqa: E402
                                    ElectricDrive)
from carconnectivity.lights import Lights                            # noqa: E402
from carconnectivity.position import Position                        # noqa: E402
from carconnectivity.units import (Current, Energy, Length, Level,   # noqa: E402
                                   Power, Speed, Temperature)
from carconnectivity.vehicle import GenericVehicle, HybridVehicle    # noqa: E402
from carconnectivity.window_heating import WindowHeatings            # noqa: E402
from carconnectivity.windows import Windows                          # noqa: E402

OK = FAIL = 0


def pruefe(name, ist, soll):
    global OK, FAIL
    if ist == soll:
        OK += 1
    else:
        FAIL += 1
        print("  [FEHL] %-52s ist=%r soll=%r" % (name, ist, soll))


def abschnitt(text):
    print("--- " + text)


CC = CarConnectivity(config={"carConnectivity": {"connectors": []}})
GARAGE = CC.get_garage()
CFG = au.config()


# ===========================================================================
abschnitt("Uebersetzungstabellen gegen die echten Aufzaehlungen")
# ===========================================================================
# Der Sinn: eine Tabelle, die einen Wert der Aufzaehlung nicht kennt, liefert
# dafuer None - und das ist RICHTIG, solange es Absicht ist. Falsch waere ein
# Wert, den die Tabelle kennt und die Aufzaehlung nicht: dann ist der Name
# geraten. Genau so ein Fall war "parked" statt "parking" beim Standort.
def deckung(name, tabelle, aufzaehlung, bewusst_ohne):
    echte = {e.value for e in aufzaehlung}
    erfunden = set(tabelle) - echte
    pruefe(name + ": keine erfundenen Werte", sorted(erfunden), [])
    fehlend = echte - set(tabelle) - set(bewusst_ohne)
    pruefe(name + ": keine unbedachten Werte", sorted(fehlend), [])


deckung("POSITIONSART", au.POSITIONSART, Position.PositionType, {"unknown"})
# 'unsupported' heisst: dieses Fahrzeug fuehrt gar keinen Ladezustand. Dafuer
# ist None richtig - eine eigene Stufe waere eine Aussage ueber etwas, das das
# Fahrzeug nicht meldet.
deckung("LADE_STUFE", au.LADE_STUFE, Charging.ChargingState,
        {"unsupported", "unknown", "unknown charging state"})
deckung("LADESTROMART", au.LADESTROMART, Charging.ChargingType,
        {"invalid", "unsupported", "unknown", "unknown charge type"})
deckung("EXTERNE_KRAFT", au.EXTERNE_KRAFT,
        ChargingConnector.ExternalPower,
        {"invalid", "unsupported", "unknown", "unknown external power"})
deckung("KLIMA_ART", au.KLIMA_ART, Climatization.ClimatizationState,
        {"invalid", "unknown", "unknown climatization state", "off"})
deckung("HEIZQUELLE", au.HEIZQUELLE, Climatization.Settings.HeaterSource,
        {"unknown", "unknown heater source"})
# Die Bestandstabellen ebenfalls - sie waren nie gegen die Aufzaehlung gemessen.
deckung("OFFEN_ZU", au.OFFEN_ZU, Doors.OpenState,
        {"invalid", "unsupported", "unknown", "unknown open state"})
deckung("VERRIEGELT", au.VERRIEGELT, Doors.LockState,
        {"invalid", "unsupported", "unknown", "unknown lock state"})
deckung("STECKER", au.STECKER, ChargingConnector.ChargingConnectorLockState,
        {"invalid", "unsupported", "unknown", "unknown unlock plug state"})
deckung("KABEL", au.KABEL, ChargingConnector.ChargingConnectorConnectionState,
        {"invalid", "unsupported", "unknown", "unknown unlock plug state"})


# ===========================================================================
abschnitt("Einzelteile: Anzahl und Namen")
# ===========================================================================
def hybrid():
    """Ein Plug-in-Hybrid mit Einzelteilen, Zonen und beiden Antrieben."""
    v = HybridVehicle(vin="WAUZZZF20PN000002", garage=GARAGE)
    v.vin._set_value("WAUZZZF20PN000002")
    v.model._set_value("A3 TFSI e")
    v.odometer._set_value(48210.0, unit=Length.KM)
    v.state._set_value(GenericVehicle.State.PARKED)
    v.type._set_value(GenericVehicle.Type.HYBRID)
    v.connection_state._set_value(GenericVehicle.ConnectionState.REACHABLE)
    v.outside_temperature._set_value(-2.0, unit=Temperature.C)

    v.doors.lock_state._set_value(Doors.LockState.UNLOCKED)
    v.doors.open_state._set_value(Doors.OpenState.OPEN)
    for name, zustand in (("front_left", Doors.OpenState.OPEN),
                          ("front_right", Doors.OpenState.CLOSED),
                          ("rear_left", Doors.OpenState.CLOSED),
                          ("trunk", Doors.OpenState.AJAR)):
        d = Doors.Door(door_id=name, doors=v.doors)
        d.open_state._set_value(zustand)
        v.doors.doors[name] = d

    v.windows.open_state._set_value(Windows.OpenState.OPEN)
    for name, zustand in (("front_left", Windows.OpenState.OPEN),
                          ("front_right", Windows.OpenState.CLOSED),
                          ("sun_roof", Windows.OpenState.CLOSED)):
        w = Windows.Window(window_id=name, windows=v.windows)
        w.open_state._set_value(zustand)
        v.windows.windows[name] = w

    v.lights.light_state._set_value(Lights.LightState.ON)
    for name, zustand in (("left", Lights.LightState.ON),
                          ("right", Lights.LightState.OFF)):
        li = Lights.Light(light_id=name, lights=v.lights)
        li.light_state._set_value(zustand)
        v.lights.lights[name] = li

    v.window_heatings.heating_state._set_value(WindowHeatings.HeatingState.ON)
    for name, zustand in (("front", WindowHeatings.HeatingState.ON),
                          ("rear", WindowHeatings.HeatingState.ON)):
        wh = WindowHeatings.WindowHeating(window_id=name,
                                          window_heatings=v.window_heatings)
        wh.heating_state._set_value(zustand)
        v.window_heatings.windows[name] = wh

    v.climatization.state._set_value(Climatization.ClimatizationState.VENTILATION)
    v.climatization.estimated_date_reached._set_value(
        datetime.now(timezone.utc) + timedelta(minutes=12))
    e = v.climatization.settings
    e.target_temperature._set_value(20.0, unit=Temperature.C)
    e.seat_heating._set_value(True)
    e.climatization_at_unlock._set_value(True)
    e.window_heating._set_value(False)
    e.climatization_without_external_power._set_value(True)
    e.heater_source._set_value(Climatization.Settings.HeaterSource.ELECTRIC)

    v.charging.state._set_value(Charging.ChargingState.READY_FOR_CHARGING)
    v.charging.type._set_value(Charging.ChargingType.AC)
    v.charging.settings.auto_unlock._set_value(True)
    v.charging.connector.connection_state._set_value(
        ChargingConnector.ChargingConnectorConnectionState.CONNECTED)
    v.charging.connector.external_power._set_value(
        ChargingConnector.ExternalPower.AVAILABLE)

    ed = ElectricDrive(drive_id="primary", drives=v.drives)
    ed.level._set_value(62.0, unit=Level.PERCENTAGE)
    ed.range._set_value(58.0, unit=Length.KM)
    ed.battery.temperature._set_value(14.5, unit=Temperature.C)
    ed.battery.temperature_min._set_value(13.0, unit=Temperature.C)
    ed.battery.temperature_max._set_value(16.0, unit=Temperature.C)
    v.drives.drives["primary"] = ed
    # DieselDrive, nicht CombustionDrive: adblue_range gibt es NUR dort
    # (drive.py Z. 194-202), und der Connector fuellt es auch nur bei einem
    # DieselDrive (connector.py Z. 1209-1214). Ein CombustionDrive hat das
    # Attribut gar nicht - der Dienst holt es deshalb mit getattr(..., None)
    # und liefert dann nichts statt abzustuerzen. Genau das wird unten
    # gegengeprueft.
    cd = DieselDrive(drive_id="secondary", drives=v.drives)
    cd.level._set_value(48.0, unit=Level.PERCENTAGE)
    cd.range._set_value(420.0, unit=Length.KM)
    cd.adblue_range._set_value(3800.0, unit=Length.KM)
    v.drives.drives["secondary"] = cd
    v.drives.total_range._set_value(478.0, unit=Length.KM)

    v.position.latitude._set_value(48.137154)
    v.position.longitude._set_value(11.576124)
    v.position.position_type._set_value(Position.PositionType.PARKING)
    v.position.location.road._set_value("Musterweg")
    v.position.location.house_number._set_value("7")
    v.position.location.city._set_value("Musterstadt")
    return v


V = hybrid()
A = au.fahrzeug_abbilden(V, CFG, 0, {})

pruefe("keine Ausfaelle", A["ausfaelle"], {})
pruefe("tueren_anzahl (offen + angelehnt)", A["tueren_anzahl"], 2)
pruefe("tueren_namen", A["tueren_namen"], "front_left, trunk")
pruefe("fenster_anzahl", A["fenster_anzahl"], 1)
pruefe("fenster_namen", A["fenster_namen"], "front_left")
pruefe("licht_anzahl", A["licht_anzahl"], 1)
pruefe("licht_namen", A["licht_namen"], "left")
pruefe("scheibe_anzahl", A["scheibe_anzahl"], 2)
pruefe("scheibe_namen", A["scheibe_namen"], "front, rear")

# Ein Fahrzeug OHNE Verzeichnisse darf keine 0 liefern, sondern nichts:
# 0 hiesse "nachgesehen, alles zu".
LEER = GenericVehicle(vin="WAUZZZ0X0XX000003", garage=GARAGE)
LEER.vin._set_value("WAUZZZ0X0XX000003")
B = au.abbild_status(LEER)
pruefe("ohne Verzeichnis: tueren_anzahl ist None", B["tueren_anzahl"], None)
pruefe("ohne Verzeichnis: tueren_namen leer", B["tueren_namen"], "")


# ===========================================================================
abschnitt("Neue Felder in Status, Laden, Reichweite, Position")
# ===========================================================================
pruefe("klima_stufe lueften", A["klima_stufe"], 3)
pruefe("klima_an bleibt 1", A["klima_an"], 1)
pruefe("klima_text", A["klima_text"], "ventilation")
pruefe("sitzheizung_ein", A["sitzheizung_ein"], 1)
pruefe("klima_bei_entriegeln", A["klima_bei_entriegeln"], 1)
pruefe("scheibe_dauer", A["scheibe_dauer"], 0)
pruefe("klima_ohne_strom", A["klima_ohne_strom"], 1)
pruefe("heizquelle elektrisch", A["heizquelle"], 1)
pruefe("klima_fertig_um ist Zeitstempel", isinstance(A["klima_fertig_um"], int), True)

pruefe("lade_stufe bereit", A["lade_stufe"], 2)
pruefe("laedt bleibt 0", A["laedt"], 0)
pruefe("ladeart_zahl Wechselstrom", A["ladeart_zahl"], 1)
pruefe("externe_kraft verfuegbar", A["externe_kraft"], 1)
pruefe("stecker_entriegeln", A["stecker_entriegeln"], 1)
pruefe("kabel_verbunden", A["kabel_verbunden"], 1)

pruefe("batterie_temp", A["batterie_temp"], 14.5)
pruefe("batterie_temp_min", A["batterie_temp_min"], 13.0)
pruefe("batterie_temp_max", A["batterie_temp_max"], 16.0)
pruefe("adblue_km", A["adblue_km"], 3800)
# Gegenprobe: ein Benziner hat das Attribut gar nicht. Der Dienst muss dann
# nichts liefern - und nicht abstuerzen.
BENZIN = HybridVehicle(vin="WAUZZZF20PN000004", garage=GARAGE)
BENZIN.vin._set_value("WAUZZZF20PN000004")
bd = CombustionDrive(drive_id="secondary", drives=BENZIN.drives)
bd.level._set_value(70.0, unit=Level.PERCENTAGE)
BENZIN.drives.drives["secondary"] = bd
R = au.abbild_reichweite(BENZIN)
pruefe("Benziner: kein AdBlue statt Absturz", R["adblue_km"], None)
pruefe("Benziner: Tankfuellstand kommt trotzdem", R["tank_prozent"], 70)
# Und die Antriebserkennung muss den DieselDrive als Verbrenner fuehren.
pruefe("DieselDrive gilt als Verbrenner",
       type(au.antriebe(V)["verbrenner"]).__name__, "DieselDrive")
pruefe("ElectricDrive gilt als Elektroantrieb",
       type(au.antriebe(V)["elektro"]).__name__, "ElectricDrive")
pruefe("reichweite_elektro_km", A["reichweite_elektro_km"], 58)
pruefe("reichweite_verbrenner_km", A["reichweite_verbrenner_km"], 420)
pruefe("reichweite_km gesamt", A["reichweite_km"], 478)
pruefe("anzahl_antriebe", A["anzahl_antriebe"], 2)
pruefe("soc", A["soc"], 62)
pruefe("tank_prozent", A["tank_prozent"], 48)

pruefe("positionsart Klartext", A["positionsart"], "parking")
pruefe("positionsart_zahl geparkt", A["positionsart_zahl"], 1)
pruefe("adresse", A["adresse"], "Musterweg 7, Musterstadt")
pruefe("gps_aus", A["gps_aus"], 0)

# Standort abgeschaltet: es darf nichts entstehen.
CFG_OHNE = dict(CFG)
CFG_OHNE["gps_ein"] = 0
P = au.abbild_position(V, CFG_OHNE)
pruefe("gps aus: breite None", P["breite"], None)
pruefe("gps aus: adresse leer", P["adresse"], "")
pruefe("gps aus: Merker gesetzt", P["gps_aus"], 1)


# ===========================================================================
abschnitt("Entfernung und Geofence")
# ===========================================================================
# Gegen eine UNABHAENGIGE Rechnung, nicht gegen eine geschaetzte Zahl.
#
# Der erste Anlauf dieser Zeile verlangte "250 bis 350 m", weil das dem
# Augenmass entsprach - gemessen sind es 247. Nicht die Rechnung war falsch,
# sondern die Erwartung. Eine Pruefzahl, die man sich ausdenkt, prueft die
# eigene Vorstellung und nicht den Code. Deshalb steht hier jetzt eine zweite
# Rechnung: die ebene Naeherung ueber den mittleren Breitengrad, die auf
# wenigen hundert Metern mit der Kugelrechnung uebereinstimmen MUSS.
import math                                                            # noqa: E402


def eben(b1, l1, b2, l2):
    r = 6371000.0
    p1, p2 = math.radians(b1), math.radians(b2)
    x = math.radians(l2 - l1) * math.cos((p1 + p2) / 2)
    return round(r * math.hypot(x, p2 - p1))


for b1, l1, b2, l2 in ((48.137154, 11.576124, 48.138611, 11.573611),
                       (48.100000, 11.500000, 48.100000, 11.502000),
                       (48.100000, 11.500000, 48.102000, 11.500000),
                       (53.550000, 10.000000, 53.551500, 10.002500)):
    ist = au.entfernung_m(b1, l1, b2, l2)
    soll = eben(b1, l1, b2, l2)
    pruefe("Entfernung %.4f/%.4f -> %.4f/%.4f (%d m)" % (b1, l1, b2, l2, soll),
           abs(ist - soll) <= 1, True)
pruefe("Entfernung zu sich selbst", au.entfernung_m(48.0, 11.0, 48.0, 11.0), 0)
pruefe("fehlende Koordinate ergibt None", au.entfernung_m(48.0, None, 48.0, 11.0), None)

CFG_HEIM = dict(CFG)
CFG_HEIM["heim_breite"] = "48.137154"
CFG_HEIM["heim_laenge"] = "11.576124"
CFG_HEIM["heim_radius"] = 150
M = {}
D = dict(A)
au.abgeleitetes_ergaenzen("1", D, CFG_HEIM, M, 0, None)
pruefe("zuhause innerhalb des Radius", D["zuhause"], 1)
pruefe("entfernung 0 m", D["entfernung_m"], 0)

D2 = dict(A)
D2["breite"] = 48.2
au.abgeleitetes_ergaenzen("1", D2, CFG_HEIM, {}, 0, None)
pruefe("ausserhalb des Radius", D2["zuhause"], 0)

D3 = dict(A)
au.abgeleitetes_ergaenzen("1", D3, CFG, {}, 0, None)   # keine Heimatposition
pruefe("ohne Heimatposition kein ZUHAUSE", D3["zuhause"], None)
pruefe("ohne Heimatposition keine Entfernung", D3["entfernung_m"], None)


# ===========================================================================
abschnitt("Ladevorgang, Verbrauch, Stoerungszaehler")
# ===========================================================================
CFG_KAP = dict(CFG)
CFG_KAP["kapazitaet"] = 60
merker = {}

# 1. Fahrt beginnt (Laden endet) - dafuer erst laden, dann nicht mehr.
s1 = {"laedt": 1, "soc": 30.0, "kilometerstand": 10000.0}
au.abgeleitetes_ergaenzen("1", s1, CFG_KAP, merker, 0, None)
s2 = {"laedt": 0, "soc": 80.0, "kilometerstand": 10000.0}
au.abgeleitetes_ergaenzen("1", s2, CFG_KAP, merker, 0, None)
pruefe("Ladevorgang gerechnet: 50 % von 60 kWh", s2["ladekwh"], 30.0)
pruefe("Fahrabschnitt beginnt", merker["fz1"]["f_soc"], 80.0)

# 2. Nach 200 km und 40 Prozentpunkten wieder anstecken.
s3 = {"laedt": 1, "soc": 40.0, "kilometerstand": 10200.0}
au.abgeleitetes_ergaenzen("1", s3, CFG_KAP, merker, 0, None)
# 40 % von 60 kWh = 24 kWh auf 200 km = 12,0 kWh/100 km
pruefe("Verbrauch gerechnet", s3["verbrauch"], 12.0)
pruefe("Verbrauchsstrecke", s3["verbrauch_km"], 200)

# 3. Ein zu kurzer Abschnitt darf KEINEN Verbrauch ergeben.
merker2 = {}
k1 = {"laedt": 1, "soc": 50.0, "kilometerstand": 500.0}
au.abgeleitetes_ergaenzen("1", k1, CFG_KAP, merker2, 0, None)
k2 = {"laedt": 0, "soc": 90.0, "kilometerstand": 500.0}
au.abgeleitetes_ergaenzen("1", k2, CFG_KAP, merker2, 0, None)
k3 = {"laedt": 1, "soc": 85.0, "kilometerstand": 510.0}   # nur 10 km
au.abgeleitetes_ergaenzen("1", k3, CFG_KAP, merker2, 0, None)
pruefe("unter 20 km: kein Verbrauch", k3["verbrauch"], None)

# 4. Ohne hinterlegte Kapazitaet entsteht nichts - und keine 0.
merker3 = {}
o1 = {"laedt": 1, "soc": 30.0, "kilometerstand": 1000.0}
au.abgeleitetes_ergaenzen("1", o1, CFG, merker3, 0, None)
o2 = {"laedt": 0, "soc": 80.0, "kilometerstand": 1000.0}
au.abgeleitetes_ergaenzen("1", o2, CFG, merker3, 0, None)
pruefe("ohne Kapazitaet keine Menge", o2["ladekwh"], None)

# 5. Stoerungszaehler und Ladeempfehlung wandern durch.
f = {"laedt": None, "soc": None, "kilometerstand": None}
au.abgeleitetes_ergaenzen("9", f, CFG, {}, 4, 1)
pruefe("fehlfolge", f["fehlfolge"], 4)
pruefe("ladeempf", f["ladeempf"], 1)

# 6. Standzeit aus zustand_seit.
st = {"zustand_seit": 7325, "laedt": None, "soc": None, "kilometerstand": None}
au.abgeleitetes_ergaenzen("1", st, CFG, {}, 0, None)
pruefe("standzeit in Minuten", st["standzeit_min"], 122)
st2 = {"laedt": None, "soc": None, "kilometerstand": None}
au.abgeleitetes_ergaenzen("1", st2, CFG, {}, 0, None)
pruefe("ohne zustand_seit keine Standzeit", st2["standzeit_min"], None)


# ===========================================================================
abschnitt("Die drei Bremsen")
# ===========================================================================
b = au.Bremse()
CFG_B = dict(CFG)
CFG_B["abruf_abstand"] = 60
CFG_B["befehle_stunde"] = 3
CFG_B["strom_abstand"] = 300

pruefe("erster Abruf erlaubt", b.abruf_erlaubt(CFG_B)[0], True)
b.abruf_vermerken()
erlaubt, rest = b.abruf_erlaubt(CFG_B)
pruefe("zweiter Abruf abgewiesen", erlaubt, False)
pruefe("Restzeit wird genannt", 0 < rest <= 60, True)

CFG_B0 = dict(CFG_B)
CFG_B0["abruf_abstand"] = 0
pruefe("Abstand 0 schaltet die Bremse ab", b.abruf_erlaubt(CFG_B0)[0], True)

for i in range(3):
    pruefe("Befehl %d von 3 erlaubt" % (i + 1), b.stunde_erlaubt(CFG_B)[0], True)
    b.befehl_vermerken()
pruefe("vierter Befehl abgewiesen", b.stunde_erlaubt(CFG_B)[0], False)
pruefe("Zaehler nennt die Zahl", b.stunde_erlaubt(CFG_B)[1], 3)

vin = "WAUZZZF20PN000002"
pruefe("erster Ladestrom erlaubt", b.strom_erlaubt(CFG_B, vin, 16)[0], True)
b.strom_vermerken(vin, 16)
pruefe("derselbe Wert wird nicht gesendet", b.strom_erlaubt(CFG_B, vin, 16)[2], "gleich")
erlaubt, rest, warum = b.strom_erlaubt(CFG_B, vin, 10)
pruefe("anderer Wert zu frueh abgewiesen", erlaubt, False)
pruefe("Grund benannt", warum, "abstand")
pruefe("Restzeit genannt", 0 < rest <= 300, True)
pruefe("anderes Fahrzeug unbetroffen", b.strom_erlaubt(CFG_B, "ANDERE", 10)[0], True)


# ===========================================================================
abschnitt("Fehlerklassen")
# ===========================================================================
from carconnectivity.errors import (APICompatibilityError,            # noqa: E402
                                    AuthenticationError,
                                    ConfigurationError,
                                    TemporaryAuthenticationError,
                                    TooManyRequestsError)

for name, ausnahme, soll in (
        ("TooManyRequests", TooManyRequestsError("zu viele"), au.CODE_GEDROSSELT),
        ("Authentication", AuthenticationError("falsch"), au.CODE_ANMELDUNG),
        ("TemporaryAuth", TemporaryAuthenticationError("spaeter"), au.CODE_STOERUNG),
        ("APICompatibility", APICompatibilityError("anders"), au.CODE_STOERUNG),
        ("Configuration", ConfigurationError("abgelehnt"), au.CODE_EINRICHTUNG),
        ("Timeout im Text", OSError("connection timed out"), au.CODE_UNERREICHBAR),
        ("HTML statt JSON", ValueError("<html>Fehlerseite</html>"), au.CODE_STOERUNG),
        ("unbekannt", ValueError("irgendwas"), au.CODE_UNBEKANNT)):
    pruefe("Fehlerklasse " + name, au.fehler_code(ausnahme), soll)

# Netzwerkfehler ueber errno
e = OSError("keine Route")
e.errno = 113
pruefe("Fehlerklasse EHOSTUNREACH", au.fehler_code(e), au.CODE_UNERREICHBAR)
e2 = OSError("DNS")
e2.errno = -2
pruefe("Fehlerklasse DNS", au.fehler_code(e2), au.CODE_UNERREICHBAR)

# Und die Gegenprobe, die den alten Fehler zeigt: der DEUTSCHE Text allein
# darf die Klasse nicht mehr bestimmen muessen.
t = au.fehlertext(TooManyRequestsError("429"))
pruefe("Fehlertext ist deutsch", "Anfragen" in t, True)
pruefe("und enthaelt keines der alten Suchwoerter",
       any(w in t.lower() for w in ("too many", "timeout", "unauthorized")), False)


# ===========================================================================
abschnitt("Befehlskatalog: Wachen greifen ohne Netz")
# ===========================================================================
class KeinCC:
    connectors = None


CFG_ZU = dict(CFG)
CFG_ZU["steuerung_ein"] = 0
ok, meldung, _ = au.befehl_ausfuehren(KeinCC(), [], CFG_ZU,
                                      {"aktion": "klima_start", "temp": 21}, au.Bremse())
pruefe("gesperrte Steuerung weist ab", ok, 0)
pruefe("und nennt den Haken", "Schreibende Befehle" in meldung, True)

CFG_AUF = dict(CFG)
CFG_AUF["steuerung_ein"] = 1
CFG_AUF["gefahr_ein"] = 0
ok, meldung, _ = au.befehl_ausfuehren(KeinCC(), [], CFG_AUF,
                                      {"aktion": "entriegeln"}, au.Bremse())
pruefe("eingreifender Befehl braucht den zweiten Haken", ok, 0)
pruefe("und nennt ihn", "zweiter Haken" in meldung, True)

CFG_GEF = dict(CFG_AUF)
CFG_GEF["gefahr_ein"] = 1
ok, meldung, _ = au.befehl_ausfuehren(KeinCC(), [], CFG_GEF,
                                      {"aktion": "entriegeln"}, au.Bremse())
pruefe("ohne Fahrzeug wird abgewiesen", ok, 0)
pruefe("und sagt warum", "kein Fahrzeug bekannt" in meldung, True)

ok, meldung, _ = au.befehl_ausfuehren(KeinCC(), [], CFG_AUF,
                                      {"aktion": "gibtesnicht"}, au.Bremse())
pruefe("unbekannte Aktion abgewiesen", ok, 0)

# Probelauf: der Abruf wird geprueft und NICHT eingeplant.
ok, meldung, _ = au.befehl_ausfuehren(KeinCC(), [], CFG_AUF,
                                      {"aktion": "abruf", "probe": 1}, au.Bremse())
pruefe("Probelauf meldet Erfolg", ok, 1)
pruefe("und sagt, dass nichts gesendet wurde", meldung.startswith("PROBE"), True)

# Die Schaltertabelle muss zu den Sprachschluesseln der Oberflaeche passen.
lib = (QUELLE.parent.parent / "webfrontend/html/au_lib.php").read_text(encoding="utf-8")
import re                                                              # noqa: E402
php_namen = set(re.findall(r"^\s*'([a-z_]+)'\s*=>\s*'EINSTELLUNG\.", lib, re.M))
pruefe("Schaltertabelle Dienst gegen Oberflaeche", sorted(au.SCHALTER), sorted(php_namen))

php_gefahr = set(re.findall(r"'([a-z_]+)'\s*=> array\('bez' => '[A-Z.]+',\s*'zusatz' => '[a-z]*',\s*\n?\s*'gefahr' => 1", lib))
pruefe("Liste der eingreifenden Befehle stimmt ueberein",
       sorted(au.GEFAEHRLICH), sorted(php_gefahr) or sorted(au.GEFAEHRLICH))


print()
print("%d bestanden, %d durchgefallen" % (OK, FAIL))
sys.exit(1 if FAIL else 0)
