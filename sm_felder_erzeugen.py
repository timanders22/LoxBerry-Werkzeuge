#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Erzeugt bin/sm_felder.json fuer Smartmeter classic - die EINE Quelle.

Warum es diese Datei gibt
-------------------------
Das Plugin bildet den Namen eines Messwertes an vier Stellen: im Perl-Dienst
(fetch_vzlogger.pl), im PHP-Abholer (fetch.php), in der Themen-Tabelle der
Oberflaeche und in der erzeugten Loxone-Vorlage. Am 26.08.2026 wurde gemessen,
dass drei dieser Stellen auseinandergelaufen waren: die Vorlage legte
smartmeter_vzlogger_1_0_1_8_0 an, veroeffentlicht wurde
smartmeter/vzlogger/Consumption_Total_OBIS_1.8.0 - kein einziger der erzeugten
Eingaenge konnte je einen Wert bekommen.

Ueber die Sprachgrenze hinweg gibt es keine gemeinsame Funktion. Also eine
gemeinsame DATENDATEI, die Perl und PHP lesen - so wie Chromecast4lox seine
Themen in bin/cc_themen.json fuehrt und APC-UPS seine in bin/apc_themen.json.

Was hier gemessen und was gesetzt ist
-------------------------------------
GEMESSEN, aus dem Quelltext gelesen:
  * die Schluesselmenge      aus den print-F-Zeilen von bin/sm_logger.pl
  * die OBIS-Zuordnung       aus der Tabelle %SM_NAME in bin/fetch_vzlogger.pl
  * die Einheiten des
    klassischen Weges        aus bin/sml_parser.php (Wh -> kWh, W -> kW)

GESETZT, also eine Wahl dieses Hauses und als solche gekennzeichnet:
  * Nachkommastellen, Min- und Maxwerte der Loxone-Vorlage
  * die Zuordnung Schluessel -> Sprachschluessel der Bedeutung

NICHT GEMESSEN und deshalb leer:
  * die Einheit auf dem vzLogger-Weg. vzlogger rechnet nicht um, es reicht den
    Wert des Zaehlers durch; der klassische Weg rechnet in sml_parser.php auf
    kWh und kW um. Ob dieselbe Kennzahl auf beiden Wegen dieselbe Groessen-
    ordnung hat, ist ohne Zaehler nicht zu entscheiden. Es wird deshalb NICHT
    umgerechnet und NICHT behauptet - das Feld "einheit_vz" bleibt leer, und
    die Oberflaeche sagt das.

Aufruf
------
    python3 Werkzeuge/sm_felder_erzeugen.py <Pluginordner>
    python3 Werkzeuge/sm_felder_erzeugen.py <Pluginordner> --schau

--schau schreibt nichts und zeigt nur, was entstuende.
"""

import json
import os
import re
import sys

# ---------------------------------------------------------------- Metadaten
# Die Regeln stehen als Muster ueber dem Schluesselnamen. Was kein Muster
# trifft, faellt in "unbekannt" und wird am Ende ausdruecklich gemeldet -
# eine stille Vorgabe waere hier genau der Fehler, den die Datei abstellen
# soll.
#
# Felder je Eintrag:
#   typ        zahl | text     Text bekommt in Loxone KEINEN virtuellen Eingang
#   einheit    Einheit auf dem KLASSISCHEN Weg (gemessen an sml_parser.php)
#   nk         Nachkommastellen fuer die Loxone-Vorlage (gesetzt)
#   min, max   Grenzen fuer die Loxone-Vorlage (gesetzt)
#   signed     darf der Wert negativ werden
#   bed        Sprachschluessel der Bedeutung
#   quelle     bestand = im Betrieb gegen eine echte Antwort geprueft
#              doku    = aus der Beschreibung uebernommen, an KEINER Anlage
#                        gemessen
REGELN = [
    # (Muster, typ, einheit, nk, min, max, signed, bed, quelle)
    (r"^Last_Update$",
     "text", "", 0, 0, 0, False, "FELD.LAST_UPDATE", "bestand"),
    (r"^Last_UpdateLoxEpoche$",
     "zahl", "s", 0, 0, 2147483647, False, "FELD.LAST_UPDATE_LOX", "bestand"),
    # NEU in 2.4.0. Der Unterschied zu den beiden darueber ist der Grund,
    # aus dem es diesen Schluessel gibt: Last_Update und
    # Last_UpdateLoxEpoche schreibt der Leser bei JEDEM Durchlauf, auch bei
    # einem, der keinen einzigen Wert gelesen hat. Sie beweisen, dass der
    # Leser lief - nicht, dass der Zaehler geantwortet hat.
    # Last_UpdateUnix wird nur geschrieben, wenn wirklich ein Wert ankam.
    # Daran haengen der Healthcheck und die Zeile "Herzschlag" im
    # Selbsttest.
    (r"^Last_UpdateUnix$",
     "zahl", "s", 0, 0, 2147483647, False, "FELD.LAST_UPDATE_UNIX", "bestand"),

    (r"^Consumption_Total_OBIS_1\.8\.0$",
     "zahl", "kWh", 3, 0, 1000000, False, "FELD.BEZUG_GESAMT", "bestand"),
    (r"^Delivery_Total_OBIS_2\.8\.0$",
     "zahl", "kWh", 3, 0, 1000000, False, "FELD.EINSP_GESAMT", "bestand"),
    (r"^Consumption_Total_OBIS_6\.8\.0$",
     "zahl", "kWh", 3, 0, 1000000, False, "FELD.WAERME_GESAMT", "doku"),
    (r"^Consumption_Tarif\d_OBIS_1\.8\.\d$",
     "zahl", "kWh", 3, 0, 1000000, False, "FELD.BEZUG_TARIF", "bestand"),
    (r"^Delivery_Tarif\d_OBIS_2\.8\.\d$",
     "zahl", "kWh", 3, 0, 1000000, False, "FELD.EINSP_TARIF", "bestand"),
    (r"^Consumption_Tarif\d_OBIS_6\.8\.\d$",
     "zahl", "kWh", 3, 0, 1000000, False, "FELD.WAERME_TARIF", "doku"),

    (r"^Consumption_CalculatedPower_OBIS_1\.99\.0$",
     "zahl", "kW", 4, 0, 100000, False, "FELD.BEZUG_RECHNERISCH", "bestand"),
    (r"^Delivery_CalculatedPower_OBIS_2\.99\.0$",
     "zahl", "kW", 4, 0, 100000, False, "FELD.EINSP_RECHNERISCH", "bestand"),

    (r"^Total_Power_OBIS_16\.7\.0$",
     "zahl", "kW", 3, -100000, 100000, True, "FELD.WIRKLEISTUNG", "bestand"),
    (r"^Total_Power_OBIS_15\.7\.0$",
     "zahl", "kW", 3, 0, 100000, False, "FELD.WIRKLEISTUNG_BETRAG", "bestand"),
    (r"^Consumption_Power_OBIS_1\.7\.0$",
     "zahl", "kW", 3, 0, 100000, False, "FELD.BEZUGSLEISTUNG", "bestand"),
    (r"^Delivery_Power_OBIS_2\.7\.0$",
     "zahl", "kW", 3, 0, 100000, False, "FELD.EINSPEISELEISTUNG", "bestand"),
    (r"^Consumption_Power_L[123]_OBIS_\d+\.7\.0$",
     "zahl", "kW", 3, -100000, 100000, True, "FELD.LEISTUNG_PHASE", "bestand"),

    (r"^Instantaneous_Voltage_L[123]_\d+\.7\.0$",
     "zahl", "V", 1, 0, 500, False, "FELD.SPANNUNG", "bestand"),
    (r"^Instantaneous_Current_L[123]_\d+\.7\.0$",
     "zahl", "A", 2, 0, 200, False, "FELD.STROM", "bestand"),

    (r"^Max_Power_OBIS_6\.6\.0$",
     "zahl", "kW", 3, 0, 100000, False, "FELD.MAXLEISTUNG", "doku"),
    (r"^Volume_OBIS_6\.26\.0$",
     "zahl", "m3", 3, 0, 1000000, False, "FELD.VOLUMEN", "doku"),
    (r"^Flow_OBIS_6\.33\.0$",
     "zahl", "m3/h", 3, 0, 10000, False, "FELD.DURCHFLUSS", "doku"),
    (r"^Hour_OBIS_(6\.31\.0|6\.32\.0|9\.31\.0)$",
     "zahl", "h", 0, 0, 1000000, False, "FELD.STUNDEN", "doku"),
    (r"^Heating_(Flow|Return)_OBIS_9\.4$",
     "zahl", "C", 1, -50, 200, True, "FELD.TEMPERATUR", "doku"),

    (r"^Tarif_Indicator_Electricity_96\.14\.0$",
     "zahl", "", 0, 0, 99, False, "FELD.TARIF", "doku"),
    (r"^Breaker_State_Electricity_96\.1\.4$",
     "zahl", "", 0, 0, 9, False, "FELD.SCHALTER", "doku"),
    (r"^Message_Code_96\.13\.1$",
     "zahl", "", 0, 0, 999999, False, "FELD.MELDECODE", "doku"),
    (r"^Version_Information_96\.1\.4$",
     "zahl", "", 0, 0, 999999, False, "FELD.FASSUNG", "doku"),
    (r"^Equipment_Identifier_96\.1\.1$",
     "text", "", 0, 0, 0, False, "FELD.GERAETEKENNUNG", "doku"),
    (r"^Text_Message_96\.13\.0$",
     "text", "", 0, 0, 0, False, "FELD.MELDETEXT", "doku"),
    (r"^Delivery_Consumption_OBIS_C\.5\.0$",
     "zahl", "", 0, 0, 999999, False, "FELD.CFUENF", "doku"),
]


def abbruch(text):
    """Abbruch mit Rueckgabewert 2: nichts gemessen, nichts geschrieben.

    Zwei ist der Wert, den die Hauswerkzeuge fuer "ich konnte nichts ansehen"
    fuehren - eine Eins waere von einem gefundenen Mangel nicht zu
    unterscheiden.
    """
    sys.stderr.write("ABBRUCH: " + text + "\n")
    sys.exit(2)


def schluessel_aus_logger(pfad):
    """Jeder Schluessel, den bin/sm_logger.pl schreiben kann - gemessen.

    ZWEI Schreibweisen, und beide zaehlen:

        &DATA_WERT("NAME", $var);     seit 2.4.0 die Regel - 93 Zeilen
        print F "$serial:NAME:...     die Handvoll, die DATA_SCHLIESSEN
                                      selbst schreibt (Last_Update und die
                                      beiden Zeitstempel daneben)

    Bis 2.4.0 stand hier nur die zweite. Nach dem Umbau des Lesers fand das
    Muster noch drei Schluessel statt 65 - und ein Werkzeug, das 62 Felder
    verliert und trotzdem eine Datei schreibt, ist schlimmer als eines, das
    abbricht. Deshalb steht unten eine Untergrenze.
    """
    with open(pfad, "r", encoding="utf-8", errors="replace") as f:
        s = f.read()
    aus = set(re.findall(r'print F "\$serial:([A-Za-z0-9_.]+):', s))
    aus |= set(re.findall(r'&DATA_WERT\(\s*"([A-Za-z0-9_.]+)"', s))
    if len(aus) < 40:
        abbruch("Nur %d Schluessel in %s gefunden - das Muster passt nicht "
                "mehr zum Quelltext. Es wird nichts geschrieben."
                % (len(aus), pfad))
    return sorted(aus)


# ------------------------------------------------------------------ OBIS
# Die Zuordnung OBIS-Kennzahl -> Feldname.
#
# Bis 2.3.14 wurde sie aus der Tabelle %SM_NAME in bin/fetch_vzlogger.pl
# GELESEN. Diese Tabelle gibt es nicht mehr: der Dienst liest die Namen
# jetzt aus bin/sm_felder.json, also aus genau der Datei, die hier
# entsteht. Sie von dort zu lesen waere ein Kreis - das Werkzeug wuerde
# seine eigene Ausgabe abschreiben und jede Luecke fuer immer festhalten.
#
# Sie steht deshalb hier, und sie ist EINGEFROREN: an diesen Namen haengen
# in bestehenden Anlagen virtuelle Eingaenge. Wer einen aendert, aendert
# nicht eine Bezeichnung, sondern nimmt einem Miniserver seinen Messwert
# weg. Angeglichen wird die Anleitung an diese Tabelle, nie umgekehrt.
OBIS = {
    "1.8.0":  "Consumption_Total_OBIS_1.8.0",
    "1.8.1":  "Consumption_Tarif1_OBIS_1.8.1",
    "1.8.2":  "Consumption_Tarif2_OBIS_1.8.2",
    "2.8.0":  "Delivery_Total_OBIS_2.8.0",
    "2.8.1":  "Delivery_Tarif1_OBIS_2.8.1",
    "2.8.2":  "Delivery_Tarif2_OBIS_2.8.2",
    "16.7.0": "Total_Power_OBIS_16.7.0",
}


def obis_gegenpruefen(pfad):
    """Fuehrt der Dienst WIEDER eine eigene Tabelle? Dann gibt es zwei.

    Die Gegenrichtung zur Regel oben: sobald jemand %SM_NAME zurueckbaut,
    stehen die Namen an zwei Stellen, und zwei Listen halten sich nicht von
    selbst gleich. Das ist genau der Zustand, den 2.4.0 abgestellt hat.
    """
    with open(pfad, "r", encoding="utf-8", errors="replace") as f:
        s = f.read()
    if re.search(r"my\s+%SM_NAME\s*=\s*\(", s):
        abbruch("%s fuehrt wieder eine eigene Tabelle %%SM_NAME. Damit gibt "
                "es die Namen zweimal. Es wird nichts geschrieben." % pfad)
    if "sm_felder.json" not in s:
        abbruch("%s liest sm_felder.json nicht. Der Dienst wuerde unter "
                "anderen Namen veroeffentlichen als diese Datei sagt." % pfad)
    return OBIS


def metadaten(name):
    for muster, typ, einheit, nk, mn, mx, sg, bed, quelle in REGELN:
        if re.match(muster, name):
            return {
                "typ": typ, "einheit": einheit, "einheit_vz": "",
                "nk": nk, "min": mn, "max": mx, "signed": sg,
                "bed": bed, "quelle": quelle,
            }
    return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    schau = "--schau" in sys.argv
    if len(args) != 1:
        abbruch(__doc__)
    ordner = args[0]
    logger = os.path.join(ordner, "bin", "sm_logger.pl")
    vzfetch = os.path.join(ordner, "bin", "fetch_vzlogger.pl")
    ziel = os.path.join(ordner, "bin", "sm_felder.json")
    for p in (logger, vzfetch):
        if not os.path.isfile(p):
            abbruch(p + " fehlt.")

    keys = schluessel_aus_logger(logger)
    obis = obis_gegenpruefen(vzfetch)
    print("gelesen: %d Schluessel aus sm_logger.pl; %d OBIS-Zuordnungen aus "
          "der eingefrorenen Tabelle (fetch_vzlogger.pl gegengeprueft)"
          % (len(keys), len(obis)))

    # Die abgeleiteten OBIS-Namen gehoeren mit in die Menge: sie entstehen
    # nur auf dem vzLogger-Weg und stehen deshalb in keiner Zeile des
    # klassischen Lesers.
    alle = sorted(set(keys) | set(obis.values()))

    felder = {}
    fehlend = []
    for k in alle:
        md = metadaten(k)
        if md is None:
            fehlend.append(k)
            continue
        felder[k] = md

    if fehlend:
        # Abweisen statt zurechtbiegen: ein Schluessel ohne Metadaten bekaeme
        # sonst stillschweigend eine Einheit, die niemand gewaehlt hat.
        print("ABBRUCH: fuer %d Schluessel gibt es keine Regel:" % len(fehlend))
        for k in fehlend:
            print("   " + k)
        return 2

    daten = {
        "_kopf": {
            "zweck": "Die EINE Quelle fuer Feldnamen, Einheiten und Bedeutungen. "
                     "Gelesen von PHP (webfrontend) und Perl (bin).",
            "erzeugt_von": "Werkzeuge/sm_felder_erzeugen.py",
            "nicht_von_hand_aendern": True,
            "einheit": "gilt fuer den KLASSISCHEN Weg; bin/sml_parser.php rechnet "
                       "Wh auf kWh und W auf kW um.",
            "einheit_vz": "LEER und das mit Absicht: vzlogger rechnet nicht um, es "
                          "reicht den Wert des Zaehlers durch. Welche Einheit das "
                          "ist, laesst sich ohne Zaehler nicht entscheiden und wird "
                          "deshalb nicht behauptet.",
            "quelle": "bestand = gegen eine echte Antwort geprueft; doku = aus der "
                      "Beschreibung, an KEINER Anlage gemessen.",
        },
        "obis": obis,
        "felder": felder,
    }
    text = json.dumps(daten, indent=2, ensure_ascii=True, sort_keys=False) + "\n"

    gezaehlt = {"bestand": 0, "doku": 0}
    for v in felder.values():
        gezaehlt[v["quelle"]] += 1
    print("Felder: %d gesamt, %d bestand, %d doku, %d Textfelder"
          % (len(felder), gezaehlt["bestand"], gezaehlt["doku"],
             sum(1 for v in felder.values() if v["typ"] == "text")))

    if schau:
        print("--schau: nichts geschrieben.")
        return 0
    # Binaer schreiben, LF - der Stil aller uebrigen Dateien unter bin/.
    with open(ziel, "wb") as f:
        f.write(text.encode("utf-8"))
    print("geschrieben: " + ziel + " (%d Byte, LF)" % len(text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
