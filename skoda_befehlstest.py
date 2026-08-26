#!/usr/bin/env python3
"""Einzelpruefungen der Schreibbefehle des Skoda-Dienstes.

Laedt bin/skoda.py und prueft die Funktionen einzeln gegen erfundene Antworten.
Das ersetzt KEIN Fahrzeug: geprueft wird die Zuordnung und das Abweisen
ungueltiger Eingaben, nicht ob die Feldnamen der Skoda-Cloud stimmen.

Aufruf:  skoda_befehlstest.py [pfad/zu/bin/skoda.py]
"""
import sys

# Kein __pycache__ neben dem Plugin anlegen - es darf nicht ins Archiv.
sys.dont_write_bytecode = True
import importlib.util, asyncio, sys
from pathlib import Path
QUELLE = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    Path(__file__).resolve().parent.parent
    / "LoxBerry-Plugin-SkodaConnect-0.9.0/LoxBerry-Plugin-SkodaConnect/bin/skoda.py")
spec = importlib.util.spec_from_file_location("skoda", QUELLE); sk = importlib.util.module_from_spec(spec); spec.loader.exec_module(sk)

ok = fail = 0
def pruefe(name, ist, soll):
    global ok, fail
    if ist == soll: ok += 1
    else:
        fail += 1; print("  [FEHL] %-46s ist=%r soll=%r" % (name, ist, soll))

class Attrappe:
    """Gegenstelle, die nur mitschreibt, was aufgerufen wurde."""
    def __init__(self): self.spur = []
    async def start_air_conditioning(self, vin, t): self.spur.append(("klima", vin, t))
    async def stop_air_conditioning(self, vin): self.spur.append(("klima_aus", vin))
    async def set_target_temperature(self, vin, t): self.spur.append(("ziel", vin, t))
    async def start_charging(self, vin): self.spur.append(("laden", vin))
    async def stop_charging(self, vin): self.spur.append(("laden_aus", vin))
    async def set_charge_limit(self, vin, p): self.spur.append(("grenze", vin, p))
    async def start_window_heating(self, vin): self.spur.append(("scheibe", vin))
    async def stop_window_heating(self, vin): self.spur.append(("scheibe_aus", vin))
    async def start_ventilation(self, vin): self.spur.append(("lueft", vin))
    async def stop_ventilation(self, vin): self.spur.append(("lueft_aus", vin))
    async def wakeup(self, vin): self.spur.append(("wecken", vin))

VINS = ["TMBAAA000AA000001", "TMBBBB000BB000002"]
CFG_AUS = dict(sk.VORGABEN); CFG_AUS["steuerung_ein"] = 0
CFG = dict(sk.VORGABEN); CFG["steuerung_ein"] = 1; CFG["temp_min"] = 16; CFG["temp_max"] = 29

async def lauf():
    a = Attrappe()
    # Steuerung gesperrt
    r = await sk.befehl_ausfuehren(a, VINS, CFG_AUS, {"aktion": "klima_start", "temp": 21})
    pruefe("gesperrt: abgelehnt", r[0], 0)
    pruefe("gesperrt: Grund genannt", "ausgeschaltet" in r[1], True)
    pruefe("gesperrt: nichts gesendet", a.spur, [])

    # Abruf geht auch bei gesperrter Steuerung
    r = await sk.befehl_ausfuehren(a, VINS, CFG_AUS, {"aktion": "abruf"})
    pruefe("abruf trotz Sperre", r[0], 1)

    # Kein Fahrzeug bekannt
    r = await sk.befehl_ausfuehren(a, [], CFG, {"aktion": "klima_start", "temp": 21})
    pruefe("ohne Fahrzeug: abgelehnt", r[0], 0)

    # Unbekanntes Fahrzeug
    r = await sk.befehl_ausfuehren(a, VINS, CFG, {"aktion": "klima_start", "fahrzeug": "9", "temp": 21})
    pruefe("Fahrzeug 9: abgelehnt", r[0], 0)
    pruefe("Fahrzeug 9: Anzahl genannt", "2 Fahrzeuge" in r[1], True)

    # Temperatur ausserhalb der Grenzen wird ABGEWIESEN, nicht gekappt
    r = await sk.befehl_ausfuehren(a, VINS, CFG, {"aktion": "klima_start", "fahrzeug": "1", "temp": 35})
    pruefe("35 Grad: abgelehnt", r[0], 0)
    pruefe("35 Grad: Grenzen genannt", "16 bis 29" in r[1], True)
    pruefe("35 Grad: nichts gesendet", len(a.spur), 0)
    r = await sk.befehl_ausfuehren(a, VINS, CFG, {"aktion": "klima_start", "fahrzeug": "1", "temp": 5})
    pruefe("5 Grad: abgelehnt", r[0], 0)
    r = await sk.befehl_ausfuehren(a, VINS, CFG, {"aktion": "klima_start", "fahrzeug": "1", "temp": "zwanzig"})
    pruefe("Text als Temperatur: abgelehnt", r[0], 0)
    r = await sk.befehl_ausfuehren(a, VINS, CFG, {"aktion": "klima_start", "fahrzeug": "1"})
    pruefe("Temperatur fehlt: abgelehnt", r[0], 0)

    # Gueltige Temperatur, auch halbe Grad
    r = await sk.befehl_ausfuehren(a, VINS, CFG, {"aktion": "klima_start", "fahrzeug": "1", "temp": "21.5"})
    pruefe("21,5 Grad: angenommen", r[0], 1)
    pruefe("21,5 Grad: gesendet", a.spur[-1], ("klima", VINS[0], 21.5))
    pruefe("Antwort sagt, dass nicht bestaetigt wurde", "naechste Abruf" in r[1], True)

    # Ladegrenze
    for p, soll in ((80, 1), (50, 1), (100, 1), (49, 0), (101, 0), (0, 0)):
        r = await sk.befehl_ausfuehren(a, VINS, CFG, {"aktion": "ladegrenze", "fahrzeug": "1", "prozent": p})
        pruefe("Ladegrenze %s" % p, r[0], soll)
    r = await sk.befehl_ausfuehren(a, VINS, CFG, {"aktion": "ladegrenze", "fahrzeug": "1", "prozent": "viel"})
    pruefe("Ladegrenze Text: abgelehnt", r[0], 0)

    # VIN statt Nummer
    r = await sk.befehl_ausfuehren(a, VINS, CFG, {"aktion": "laden_start", "fahrzeug": VINS[1]})
    pruefe("laden per VIN", a.spur[-1], ("laden", VINS[1]))

    # Alle uebrigen Aktionen laufen durch
    for aktion, erw in (("klima_stop","klima_aus"), ("laden_stop","laden_aus"),
                        ("scheibe_ein","scheibe"), ("scheibe_aus","scheibe_aus"),
                        ("lueftung_start","lueft"), ("lueftung_stop","lueft_aus"),
                        ("wecken","wecken")):
        r = await sk.befehl_ausfuehren(a, VINS, CFG, {"aktion": aktion, "fahrzeug": "1"})
        pruefe("Aktion %s" % aktion, (r[0], a.spur[-1][0]), (1, erw))
    pruefe("Weckruf nennt die Grenze", "dreimal" in r[1], True)

    # Erfundene Aktion
    r = await sk.befehl_ausfuehren(a, VINS, CFG, {"aktion": "sprengen", "fahrzeug": "1"})
    pruefe("erfundene Aktion: abgelehnt", r[0], 0)

asyncio.run(lauf())
print()
print("%d bestanden, %d durchgefallen" % (ok, fail))
sys.exit(1 if fail else 0)
