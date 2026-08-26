#!/usr/bin/env python3
"""Einzelpruefungen der Abbildungsfunktionen des Weissware-Dienstes.

Geprueft wird gegen **nachgebaute Antworten der drei Schnittstellen**, deren
Form aus den Entwicklerdokumentationen stammt (Home Connect Quickstart und
States, Miele General Concept und Device capabilities, SmartThings API).
Das belegt die Zuordnung und das Verhalten bei fehlenden Werten - es belegt
NICHT, dass ein echtes Geraet genau diese Felder fuellt.

Aufruf:  ww_funktionstest.py [pfad/zu/bin/weissware.py]
"""

import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True

QUELLE = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    Path(__file__).resolve().parent.parent
    / "LoxBerry-Plugin-Weissware-0.9.0/LoxBerry-Plugin-Weissware/bin/weissware.py")
spec = importlib.util.spec_from_file_location("ww", QUELLE)
ww = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ww)

OK = FAIL = 0


def pruefe(name, ist, soll):
    global OK, FAIL
    if ist == soll:
        OK += 1
    else:
        FAIL += 1
        print("  [FEHL] %-52s ist=%r soll=%r" % (name, ist, soll))


# ===========================================================================
# Hilfsfunktionen
# ===========================================================================
pruefe("zahl None", ww.zahl(None), None)
pruefe("zahl leer", ww.zahl(""), None)
pruefe("zahl Text", ww.zahl("viel"), None)
pruefe("zahl 0 bleibt 0", ww.zahl(0), 0)
pruefe("zahl True", ww.zahl(True), 1)
pruefe("zahl False", ww.zahl(False), 0)
pruefe("zahl 1,5", ww.zahl("1,5", 1), 1.5)

pruefe("miele_zahl null", ww.miele_zahl(None), None)
pruefe("miele_zahl -32768 -> None", ww.miele_zahl(-32768), None)
pruefe("miele_zahl 0 bleibt 0", ww.miele_zahl(0), 0)
pruefe("miele_zahl 5", ww.miele_zahl(5), 5)

pruefe("miele_dauer [1,30]", ww.miele_dauer([1, 30]), 90)
pruefe("miele_dauer [0,0]", ww.miele_dauer([0, 0]), 0)
pruefe("miele_dauer leer", ww.miele_dauer(None), None)
pruefe("miele_dauer [-32768,-32768]", ww.miele_dauer([-32768, -32768]), None)

pruefe("hc_kurz Enum", ww.hc_kurz("BSH.Common.EnumType.OperationState.Run"), "Run")
pruefe("hc_kurz leer", ww.hc_kurz(None), "")

k = ww.kopfzeilen("abc", "de-DE")
pruefe("Kopfzeile Bearer", k["Authorization"], "Bearer abc")
pruefe("Kopfzeile User-Agent gesetzt", k["User-Agent"].startswith("LoxBerry"), True)
pruefe("Kopfzeile Sprache", k["Accept-Language"], "de-DE")
pruefe("Kopfzeile ohne Sprache", "Accept-Language" in ww.kopfzeilen("abc"), False)

# ===========================================================================
# Home Connect - Form aus der Quickstart- und States-Dokumentation
# ===========================================================================
HC_GERAET = {"name": "Waschmaschine", "brand": "SIEMENS", "vib": "HCS03WCH1",
             "connected": True, "type": "Washer", "enumber": "HCS03WCH1/03",
             "haId": "SIEMENS-HCS03WCH1-456227783F78"}
HC_STATUS = {
    "BSH.Common.Status.OperationState": "BSH.Common.EnumType.OperationState.Run",
    "BSH.Common.Status.DoorState": "BSH.Common.EnumType.DoorState.Closed",
    "BSH.Common.Status.RemoteControlStartAllowed": True,
    "BSH.Common.Status.RemoteControlActive": True,
}
HC_SETTINGS = {"BSH.Common.Setting.PowerState": "BSH.Common.EnumType.PowerState.On"}
HC_AKTIV = {
    "__key": "LaundryCare.Washer.Program.Cotton",
    "BSH.Common.Option.RemainingProgramTime": 5400,
    "BSH.Common.Option.ProgramProgress": 42,
    "BSH.Common.Option.ElapsedProgramTime": 1800,
    "LaundryCare.Washer.Option.Temperature": "LaundryCare.Washer.EnumType.Temperature.GC40",
    "LaundryCare.Washer.Option.SpinSpeed": "LaundryCare.Washer.EnumType.SpinSpeed.RPM1200",
}
A = ww.ableiten(ww.hc_abbilden(HC_GERAET, HC_STATUS, HC_SETTINGS, HC_AKTIV))
pruefe("HC anbieter", A["anbieter"], "homeconnect")
pruefe("HC id", A["id"], "SIEMENS-HCS03WCH1-456227783F78")
pruefe("HC marke", A["marke"], "SIEMENS")
pruefe("HC typ", A["typ"], "Washer")
pruefe("HC verbunden", A["verbunden"], 1)
pruefe("HC zustand laeuft", A["zustand"], ww.LAEUFT)
pruefe("HC laeuft abgeleitet", A["laeuft"], 1)
pruefe("HC fertig abgeleitet", A["fertig"], 0)
pruefe("HC tuer zu", A["tuer_offen"], 0)
pruefe("HC programm_text", A["programm_text"], "Cotton")
pruefe("HC fortschritt", A["fortschritt"], 42)
pruefe("HC Sekunden -> Minuten (Rest)", A["restzeit_min"], 90)
pruefe("HC Sekunden -> Minuten (Laufzeit)", A["laufzeit_min"], 30)
pruefe("HC Fernstart frei", A["fernstart_frei"], 1)
pruefe("HC Netz ein", A["netz_ein"], 1)
pruefe("HC Schleuderdrehzahl aus Enum", A["schleuderdrehzahl"], 1200)
pruefe("HC kein Verbrauch", (A["energie_kwh"], A["wasser_l"]), (None, None))
pruefe("HC fertig_um gesetzt", isinstance(A["fertig_um"], int), True)

# Geraet aus, kein OperationState
B = ww.ableiten(ww.hc_abbilden(HC_GERAET, {},
                {"BSH.Common.Setting.PowerState": "BSH.Common.EnumType.PowerState.Off"}, {}))
pruefe("HC aus ueber Netzschalter", B["zustand"], ww.AUS)
pruefe("HC aus: laeuft 0", B["laeuft"], 0)

# Getrenntes Geraet: nichts darf zu 0 werden
C = ww.ableiten(ww.hc_abbilden(dict(HC_GERAET, connected=False), {}, {}, {}))
pruefe("HC getrennt: verbunden 0", C["verbunden"], 0)
for feld in ("zustand", "tuer_offen", "fortschritt", "restzeit_min", "fernstart_frei",
             "netz_ein", "temperatur", "schleuderdrehzahl"):
    pruefe("HC getrennt: %s bleibt None" % feld, C[feld], None)

# Programmende
D = ww.ableiten(ww.hc_abbilden(HC_GERAET,
      {"BSH.Common.Status.OperationState": "BSH.Common.EnumType.OperationState.Finished"},
      HC_SETTINGS, {}))
pruefe("HC fertig erkannt", (D["zustand"], D["fertig"], D["laeuft"]), (ww.FERTIG, 1, 0))
E = ww.ableiten(ww.hc_abbilden(HC_GERAET,
      {"BSH.Common.Status.OperationState": "BSH.Common.EnumType.OperationState.Error"},
      HC_SETTINGS, {}))
pruefe("HC Stoerung erkannt", E["zustand"], ww.STOERUNG)
F = ww.ableiten(ww.hc_abbilden(HC_GERAET,
      {"BSH.Common.Status.OperationState": "BSH.Common.EnumType.OperationState.DelayedStart",
       "BSH.Common.Status.RemoteControlStartAllowed": False},
      HC_SETTINGS, {"BSH.Common.Option.StartInRelative": 7200}))
pruefe("HC Startvorwahl", F["startzeit_min"], 120)
pruefe("HC Fernstart gesperrt", F["fernstart_frei"], 0)

# ===========================================================================
# Miele - Form aus General Concept und Device capabilities
# ===========================================================================
MIELE = {
    "ident": {"type": {"key_localized": "Geraetetyp", "value_raw": 1,
                       "value_localized": "Waschmaschine"},
              "deviceName": "Waschmaschine Keller",
              "deviceIdentLabel": {"fabNumber": "000160102030"}},
    "state": {
        "status": {"value_raw": 5, "value_localized": "In Betrieb", "key_localized": "Status"},
        "ProgramID": {"value_raw": 1, "value_localized": "Baumwolle"},
        "programType": {"value_raw": 1, "value_localized": "Programm"},
        "remainingTime": [1, 12],
        "startTime": [0, 0],
        "elapsedTime": [0, 48],
        "targetTemperature": [{"value_raw": 4000, "unit": "Celsius"},
                              {"value_raw": -32768, "unit": "Celsius"}],
        "spinningSpeed": {"value_raw": 1200, "unit": "rpm"},
        "signalDoor": False,
        "remoteEnable": {"fullRemoteControl": True, "smartGrid": False, "mobileStart": True},
        "ecoFeedback": {"currentWaterConsumption": {"unit": "l", "value": 12.5},
                        "currentEnergyConsumption": {"unit": "kWh", "value": 0.75}},
    },
}
M = ww.ableiten(ww.miele_abbilden("000160102030", MIELE))
pruefe("Miele anbieter", M["anbieter"], "miele")
pruefe("Miele name", M["name"], "Waschmaschine Keller")
pruefe("Miele typ", M["typ"], "Waschmaschine")
pruefe("Miele zustand laeuft", M["zustand"], ww.LAEUFT)
pruefe("Miele zustand_text lokalisiert", M["zustand_text"], "In Betrieb")
pruefe("Miele Restzeit [1,12] -> 72", M["restzeit_min"], 72)
pruefe("Miele Laufzeit [0,48] -> 48", M["laufzeit_min"], 48)
pruefe("Miele Fortschritt gerechnet", M["fortschritt"], 40)
pruefe("Miele Tuer zu", M["tuer_offen"], 0)
pruefe("Miele Fernstart frei", M["fernstart_frei"], 1)
pruefe("Miele Temperatur 4000 -> 40,0", M["temperatur"], 40.0)
pruefe("Miele Schleuder", M["schleuderdrehzahl"], 1200)
pruefe("Miele Energie", M["energie_kwh"], 0.75)
pruefe("Miele Wasser", M["wasser_l"], 12.5)
pruefe("Miele programm_text", M["programm_text"], "Baumwolle")

# Der Kern der Miele-Eigenheit: -32768 und null duerfen nie zu 0 werden
LEER = {"ident": {"type": {"value_localized": "Geschirrspueler"}},
        "state": {"status": {"value_raw": 1, "value_localized": "Aus"},
                  "remainingTime": [-32768, -32768],
                  "elapsedTime": [-32768, -32768],
                  "startTime": None,
                  "targetTemperature": [{"value_raw": -32768}],
                  "spinningSpeed": {"value_raw": None},
                  "signalDoor": None,
                  "remoteEnable": {},
                  "ecoFeedback": None}}
L = ww.ableiten(ww.miele_abbilden("XYZ", LEER))
pruefe("Miele aus", L["zustand"], ww.AUS)
for feld in ("restzeit_min", "laufzeit_min", "startzeit_min", "fortschritt",
             "temperatur", "schleuderdrehzahl", "energie_kwh", "wasser_l",
             "tuer_offen", "fernstart_frei"):
    pruefe("Miele leer: %s bleibt None" % feld, L[feld], None)

pruefe("Miele Stoerung (8)", ww.miele_abbilden("X", {"state": {"status": {"value_raw": 8}}})["zustand"],
       ww.STOERUNG)
pruefe("Miele Programmende (7)", ww.miele_abbilden("X", {"state": {"status": {"value_raw": 7}}})["zustand"],
       ww.FERTIG)
pruefe("Miele unbekannter Status", ww.miele_abbilden("X", {"state": {"status": {"value_raw": 999}}})["zustand"],
       None)
pruefe("Miele ohne state", ww.miele_abbilden("X", {})["zustand"], None)

# ===========================================================================
# SmartThings - Form aus der API-Referenz
# ===========================================================================
ST_GERAET = {"deviceId": "abc-123", "label": "Waschmaschine",
             "name": "Samsung Washer", "manufacturerName": "Samsung Electronics",
             "deviceTypeName": "Samsung OCF Washer"}
from datetime import datetime, timedelta, timezone                     # noqa: E402
ende = (datetime.now(timezone.utc) + timedelta(minutes=45)).isoformat().replace("+00:00", "Z")
ST_ZUSTAND = {"components": {"main": {
    "washerOperatingState": {"machineState": {"value": "run"},
                             "washerJobState": {"value": "wash"},
                             "completionTime": {"value": ende}},
    "switch": {"switch": {"value": "on"}},
    "remoteControlStatus": {"remoteControlEnabled": {"value": "on"}},
}}}
S = ww.ableiten(ww.st_abbilden(ST_GERAET, ST_ZUSTAND))
pruefe("ST anbieter", S["anbieter"], "smartthings")
pruefe("ST name", S["name"], "Waschmaschine")
pruefe("ST typ uebersetzt", S["typ"], "Waschmaschine")
pruefe("ST zustand laeuft", S["zustand"], ww.LAEUFT)
pruefe("ST Restzeit aus Fertigzeitpunkt", S["restzeit_min"] in (44, 45), True)
pruefe("ST Fernstart frei", S["fernstart_frei"], 1)
pruefe("ST Netz ein", S["netz_ein"], 1)
pruefe("ST kein Fortschritt", S["fortschritt"], None)
pruefe("ST leeres Geraet", ww.st_abbilden(ST_GERAET, {})["zustand"], None)
pruefe("ST Restzeit unlesbar", ww.st_restzeit("morgen"), None)
pruefe("ST Restzeit Vergangenheit -> 0", ww.st_restzeit("2020-01-01T00:00:00Z"), 0)

# ===========================================================================
# Geraetewahl
# ===========================================================================
liste = [A, M, S]
pruefe("Wahl per Nummer 1", ww.geraet_waehlen(liste, "1") is A, True)
pruefe("Wahl per Nummer 3", ww.geraet_waehlen(liste, 3) is S, True)
pruefe("Wahl per Kennung", ww.geraet_waehlen(liste, "abc-123") is S, True)
pruefe("Wahl per Kennung gross", ww.geraet_waehlen(liste, "ABC-123") is S, True)
pruefe("Wahl zu gross", ww.geraet_waehlen(liste, "9"), None)
pruefe("Wahl leere Liste", ww.geraet_waehlen([], "1"), None)

# ===========================================================================
# Konfigurationsgrenzen
# ===========================================================================
import json as _json                                                   # noqa: E402
tmp = Path("/tmp/wwtest_cfg.json")
tmp.parent.mkdir(parents=True, exist_ok=True)
ww.DATEI_CONFIG = tmp
tmp.write_text(_json.dumps({"takt_betrieb": 5, "takt_ruhe": 10, "sprache": "xx"}))
c = ww.config()
pruefe("Takt Betrieb auf 60 gekappt", c["takt_betrieb"], 60)
pruefe("Takt Ruhe nie kleiner als Betrieb", c["takt_ruhe"], 60)
pruefe("unbekannte Sprache -> de-DE", c["sprache"], "de-DE")
tmp.write_text("{ kaputt")
pruefe("unlesbare Konfiguration -> Vorgaben", ww.config()["takt_ruhe"], 300)

# ===========================================================================
# Fehlertexte
# ===========================================================================
class Antwort:
    def __init__(self, code):
        self.status_code = code


class HTTPFehler(Exception):
    def __init__(self, code):
        super().__init__("boom")
        self.response = Antwort(code)


pruefe("Fehler 429 nennt den Takt", "429" in ww.fehlertext(HTTPFehler(429)), True)
pruefe("Fehler 401 nennt Neuanmeldung", "401" in ww.fehlertext(HTTPFehler(401)), True)
pruefe("Fehler 403 nennt Berechtigung", "403" in ww.fehlertext(HTTPFehler(403)), True)
pruefe("Fehler 409 nennt Fernstart", "Fernstart" in ww.fehlertext(HTTPFehler(409)), True)
pruefe("Fehler 503 nicht LoxBerry", "nicht am LoxBerry" in ww.fehlertext(HTTPFehler(503)), True)
pruefe("Fehler HTML statt JSON", "HTML statt JSON" in ww.fehlertext(Exception("<html>x")), True)

print()
print("%d bestanden, %d durchgefallen" % (OK, FAIL))
sys.exit(1 if FAIL else 0)
