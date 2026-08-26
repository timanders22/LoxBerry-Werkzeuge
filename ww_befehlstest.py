#!/usr/bin/env python3
"""Einzelpruefungen der Schreibbefehle des Weissware-Dienstes.

Statt der Schnittstelle steht eine Attrappe, die jede Anfrage mitschreibt und
eine einstellbare Antwort zurueckgibt. Damit ist belegt, WAS an welchen
Endpunkt geschickt wuerde - nicht, wie ein echtes Geraet darauf reagiert.

Aufruf:  ww_befehlstest.py [pfad/zu/bin/weissware.py]
"""

import importlib.util
import json
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

QUELLE = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    Path(__file__).resolve().parent.parent
    / "LoxBerry-Plugin-Weissware-0.9.0/LoxBerry-Plugin-Weissware/bin/weissware.py")
spec = importlib.util.spec_from_file_location("ww", QUELLE)
ww = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ww)

OK = FAIL = 0
SPUR = []


def pruefe(name, ist, soll):
    global OK, FAIL
    if ist == soll:
        OK += 1
    else:
        FAIL += 1
        print("  [FEHL] %-56s ist=%r soll=%r" % (name, ist, soll))


class Antwort:
    def __init__(self, code=204, rumpf=None):
        self.status_code = code
        self._rumpf = rumpf or {}
        self.text = json.dumps(self._rumpf) if rumpf else ""
        self.content = self.text.encode()

    def json(self):
        return self._rumpf

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("HTTP %d" % self.status_code)


class Attrappe:
    """Schreibt jede Anfrage mit und antwortet nach Vorgabe."""
    def __init__(self, code=204, rumpf=None):
        self.code = code
        self.rumpf = rumpf

    def _merke(self, verb, url, kwargs):
        SPUR.append((verb, url, kwargs.get("data")))
        if verb == "GET" and "/programs/selected" in url:
            return Antwort(200, {"data": {"key": "LaundryCare.Washer.Program.Cotton"}})
        return Antwort(self.code, self.rumpf)

    def get(self, url, **kw):
        return self._merke("GET", url, kw)

    def put(self, url, **kw):
        return self._merke("PUT", url, kw)

    def post(self, url, **kw):
        return self._merke("POST", url, kw)

    def delete(self, url, **kw):
        return self._merke("DELETE", url, kw)


CFG = dict(ww.VORGABEN, steuerung_ein=1)
CFG_AUS = dict(ww.VORGABEN, steuerung_ein=0)
Z = {"hc_client_id": "id", "hc_client_secret": "gh", "miele_client_id": "mid",
     "miele_client_secret": "ms", "st_token": "sttoken"}


def marken():
    """Gueltige Marken, damit die Erneuerung nicht anspringt."""
    return {"homeconnect": {"access_token": "hct", "refresh_token": "hcr",
                            "gueltig_bis": int(time.time()) + 86400},
            "miele": {"access_token": "mt", "refresh_token": "mr",
                      "gueltig_bis": int(time.time()) + 86400}}


HC = ww.ableiten({"anbieter": "homeconnect", "id": "SIEMENS-ABC-1", "name": "Waschmaschine",
                  "zustand": ww.BEREIT, "fernstart_frei": 1})
MI = ww.ableiten({"anbieter": "miele", "id": "000160102030", "name": "Geschirrspueler",
                  "zustand": ww.BEREIT, "fernstart_frei": 1})
ST = ww.ableiten({"anbieter": "smartthings", "id": "abc-123", "name": "Trockner",
                  "zustand": ww.BEREIT, "fernstart_frei": 1})
GESPERRT = ww.ableiten({"anbieter": "homeconnect", "id": "SIEMENS-ABC-2", "name": "Backofen",
                        "zustand": ww.BEREIT, "fernstart_frei": 0})
GERAETE = [HC, MI, ST, GESPERRT]


def ruf(b, cfg=CFG, code=204, rumpf=None):
    SPUR.clear()
    return ww.befehl_ausfuehren(Attrappe(code, rumpf), cfg, Z, marken(), GERAETE, b)


# --- Sperre und Auswahl ----------------------------------------------------
r = ruf({"aktion": "start", "geraet": "1"}, cfg=CFG_AUS)
pruefe("gesperrt: abgelehnt", r[0], 0)
pruefe("gesperrt: Grund genannt", "ausgeschaltet" in r[1], True)
pruefe("gesperrt: nichts gesendet", SPUR, [])
pruefe("abruf trotz Sperre", ruf({"aktion": "abruf"}, cfg=CFG_AUS)[0], 1)

r = ww.befehl_ausfuehren(Attrappe(), CFG, Z, marken(), [], {"aktion": "start", "geraet": "1"})
pruefe("ohne Geraet: abgelehnt", r[0], 0)
r = ruf({"aktion": "start", "geraet": "99"})
pruefe("Geraet 99: abgelehnt", r[0], 0)
pruefe("Geraet 99: Anzahl genannt", "4 Geraete" in r[1], True)

# --- Fernstart-Freigabe: abweisen statt 409 einfangen ----------------------
r = ruf({"aktion": "start", "geraet": "4"})
pruefe("ohne Fernstart-Freigabe: abgelehnt", r[0], 0)
pruefe("ohne Freigabe: Grund am Geraet genannt", "Fernstart" in r[1], True)
pruefe("ohne Freigabe: nichts gesendet", SPUR, [])
# Stop, Pause und Ausschalten brauchen die Freigabe nicht
pruefe("stop ohne Freigabe erlaubt", ruf({"aktion": "stop", "geraet": "4"})[0], 1)

# --- Home Connect: die richtigen Endpunkte und Rumpfe ----------------------
r = ruf({"aktion": "start", "geraet": "1"})
pruefe("HC start: angenommen", r[0], 1)
pruefe("HC start: erst das gewaehlte Programm geholt", SPUR[0][0:2],
       ("GET", "https://api.home-connect.com/api/homeappliances/SIEMENS-ABC-1/programs/selected"))
pruefe("HC start: dann PUT auf programs/active", SPUR[1][0:2],
       ("PUT", "https://api.home-connect.com/api/homeappliances/SIEMENS-ABC-1/programs/active"))
pruefe("HC start: Programmschluessel im Rumpf",
       json.loads(SPUR[1][2])["data"]["key"], "LaundryCare.Washer.Program.Cotton")
pruefe("HC start: Antwort nennt den Vorbehalt", "naechste Abruf" in r[1], True)

r = ruf({"aktion": "start", "geraet": "1", "programm": "LaundryCare.Washer.Program.EasyCare"})
pruefe("HC start mit Programm: kein Vorab-GET", SPUR[0][0], "PUT")
pruefe("HC start mit Programm: Schluessel uebernommen",
       json.loads(SPUR[0][2])["data"]["key"], "LaundryCare.Washer.Program.EasyCare")

ruf({"aktion": "stop", "geraet": "1"})
pruefe("HC stop: DELETE auf programs/active", SPUR[0][0:2],
       ("DELETE", "https://api.home-connect.com/api/homeappliances/SIEMENS-ABC-1/programs/active"))
ruf({"aktion": "pause", "geraet": "1"})
pruefe("HC pause: Kommando-Endpunkt", SPUR[0][1].endswith("/commands/BSH.Common.Command.PauseProgram"), True)
pruefe("HC pause: value true", json.loads(SPUR[0][2])["data"]["value"], True)
ruf({"aktion": "fortsetzen", "geraet": "1"})
pruefe("HC fortsetzen: Resume", SPUR[0][1].endswith("/commands/BSH.Common.Command.ResumeProgram"), True)
ruf({"aktion": "ein", "geraet": "1"})
pruefe("HC ein: PowerState-Einstellung", SPUR[0][1].endswith("/settings/BSH.Common.Setting.PowerState"), True)
pruefe("HC ein: Wert On", json.loads(SPUR[0][2])["data"]["value"],
       "BSH.Common.EnumType.PowerState.On")
ruf({"aktion": "aus", "geraet": "1"})
pruefe("HC aus: Wert Off", json.loads(SPUR[0][2])["data"]["value"],
       "BSH.Common.EnumType.PowerState.Off")

# --- Miele -----------------------------------------------------------------
r = ruf({"aktion": "start", "geraet": "2"})
pruefe("Miele start: angenommen", r[0], 1)
pruefe("Miele start: Aktionsendpunkt", SPUR[0][0:2],
       ("PUT", "https://api.mcs3.miele.com/v1/devices/000160102030/actions"))
pruefe("Miele start: processAction 1", json.loads(SPUR[0][2]), {"processAction": 1})
ruf({"aktion": "stop", "geraet": "2"})
pruefe("Miele stop: processAction 2", json.loads(SPUR[0][2]), {"processAction": 2})
ruf({"aktion": "pause", "geraet": "2"})
pruefe("Miele pause: processAction 3", json.loads(SPUR[0][2]), {"processAction": 3})
ruf({"aktion": "ein", "geraet": "2"})
pruefe("Miele ein: powerOn", json.loads(SPUR[0][2]), {"powerOn": True})
ruf({"aktion": "aus", "geraet": "2"})
pruefe("Miele aus: powerOff", json.loads(SPUR[0][2]), {"powerOff": True})

# --- SmartThings -----------------------------------------------------------
r = ruf({"aktion": "start", "geraet": "3"}, code=200)
pruefe("ST start: angenommen", r[0], 1)
pruefe("ST start: Befehlsendpunkt", SPUR[0][0:2],
       ("POST", "https://api.smartthings.com/v1/devices/abc-123/commands"))
rumpf = json.loads(SPUR[0][2])["commands"][0]
pruefe("ST start: Faehigkeit", rumpf["capability"], "washerOperatingState")
pruefe("ST start: Befehl", rumpf["command"], "setMachineState")
pruefe("ST start: Argument", rumpf["arguments"], ["run"])
ruf({"aktion": "ein", "geraet": "3"}, code=200)
pruefe("ST ein: switch on", json.loads(SPUR[0][2])["commands"][0]["command"], "on")

# --- Ablehnungen des Anbieters --------------------------------------------
r = ruf({"aktion": "start", "geraet": "1"}, code=409, rumpf={"error": {"key": "SDK.Error"}})
pruefe("409: abgelehnt", r[0], 0)
pruefe("409: Fernstart erwaehnt", "Fernstart" in r[1], True)
r = ruf({"aktion": "start", "geraet": "1"}, code=500)
pruefe("500: abgelehnt", r[0], 0)
pruefe("500: HTTP-Code genannt", "500" in r[1], True)

# --- Erfundene Aktion ------------------------------------------------------
r = ruf({"aktion": "sprengen", "geraet": "1"})
pruefe("erfundene Aktion: abgelehnt", r[0], 0)
pruefe("erfundene Aktion: nichts gesendet", SPUR, [])

print()
print("%d bestanden, %d durchgefallen" % (OK, FAIL))
sys.exit(1 if FAIL else 0)
