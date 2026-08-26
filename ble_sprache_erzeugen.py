#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sprachdateien fuer BLE-Scanner NG aus EINER Quelle erzeugen.

Warum ein Erzeuger und nicht zwei gepflegte Dateien: sie laufen sonst
auseinander. Bis 1.2.10 waren die Schluesselnamen maschinell aus deutschen
Satzanfaengen gebildet (TEXT.GRER_ALS_65_HEIT_NAH_GRER_ALS_85_M), ganze
Saetze in Fragmente zersaegt und die halbe Oberflaeche gar nicht
angeschlossen - der Reiter Test war durchgehend deutsch.

Regeln, die dieser Erzeuger einhaelt (REGELN_2):
  * Jeder Wert steht in doppelten Anfuehrungszeichen und enthaelt SELBST
    keine - parse_ini_file schneidet sonst am zweiten ab.
  * Umlaute als direkte UTF-8-Zeichen, keine Entitaeten. Die Oberflaeche
    schickt jeden Wert durch bl_e(); eine Entitaet waere doppelt maskiert
    und stuende woertlich auf dem Bildschirm.
  * Kein Markup in den Werten - aus demselben Grund.
  * Deutsch und Englisch tragen dieselben Schluessel.

Aufruf:
    python3 ble_sprache_erzeugen.py <plugin-ordner>
    python3 ble_sprache_erzeugen.py <plugin-ordner> --probe   (schreibt nichts)
"""

import re
import sys
from pathlib import Path

# (Schluessel, deutsch, englisch)
TEXTE = [
    # ---------------- Reiter
    ("REITER.EINSTELLUNGEN", "Einstellungen", "Settings"),
    ("REITER.LOXONE", "Einbindung in Loxone", "Loxone integration"),
    ("REITER.VERLAUF", "Verlauf", "History"),
    ("REITER.TEST", "Test", "Test"),
    ("REITER.LOG", "Logdateien", "Log files"),

    # ---------------- Legende
    ("LEGENDE.LESEN", "Ansehen — fragt nur ab, verändert nichts",
     "View — only reads, changes nothing"),
    ("LEGENDE.TECHNIK", "Technische Auskunft — für die Fehlersuche",
     "Technical information — for troubleshooting"),
    ("LEGENDE.AKTION", "Löst etwas aus — sendet oder verändert",
     "Triggers something — sends or changes"),

    # ---------------- Knöpfe
    ("KNOPF.SPEICHERN", "Speichern", "Save"),
    ("KNOPF.SUCHEN", "Geräte suchen", "Search for devices"),
    ("KNOPF.START", "Dienst starten", "Start service"),
    ("KNOPF.RESTART", "Dienst neu starten", "Restart service"),
    ("KNOPF.STOP", "Dienst anhalten", "Stop service"),
    ("KNOPF.SELBSTTEST", "Selbstprüfung als Text", "Self-check as text"),
    ("KNOPF.STATUS", "Zustand des Dienstes", "Service state"),
    ("KNOPF.TAGS", "Zustand der Tags", "Tag states"),
    ("KNOPF.SICHTBAR", "Sichtbare Geräte", "Visible devices"),
    ("KNOPF.THEMEN", "MQTT-Themen anzeigen", "Show MQTT topics"),
    ("KNOPF.VERLAUF", "Verlauf auswerten", "Evaluate history"),
    ("KNOPF.VERLAUF_CSV", "Verlauf herunterladen (CSV)", "Download history (CSV)"),
    ("KNOPF.BLUETOOTH", "Bluetooth prüfen", "Check Bluetooth"),
    ("KNOPF.KONFIG", "Konfiguration anzeigen", "Show configuration"),
    ("KNOPF.UMGEBUNG", "Umgebung und Module", "Environment and modules"),
    ("KNOPF.MQTTINFO", "MQTT-Gateway", "MQTT gateway"),
    ("KNOPF.PROBEWERT", "Probewert an Miniserver senden", "Send test value to Miniserver"),
    ("KNOPF.BATTERIE", "Batterielauf jetzt anstoßen", "Run battery check now"),
    ("KNOPF.TESTMODUS", "Testmodus 60 s", "Test mode 60 s"),
    ("KNOPF.KALIBRIEREN", "Auf 1 m kalibrieren", "Calibrate at 1 m"),
    ("KNOPF.VORLAGE", "Vorlage für Loxone Config erzeugen",
     "Create template for Loxone Config"),

    # ---------------- Allgemeine Wörter
    ("TEXT.JA", "ja", "yes"),
    ("TEXT.NEIN", "nein", "no"),
    ("TEXT.EIN", "ein", "on"),
    ("TEXT.AUS", "aus", "off"),
    ("TEXT.NEU", "neu", "new"),
    ("TEXT.LAEUFT", "läuft", "running"),
    ("TEXT.LAEUFT_NICHT", "läuft nicht", "not running"),
    ("TEXT.ANWESEND", "anwesend", "present"),
    ("TEXT.ABWESEND", "abwesend", "away"),
    ("TEXT.NICHT_AKTIV", "(nicht aktiv)", "(inactive)"),
    ("TEXT.GESPEICHERT", "Gespeichert.", "Saved."),
    ("TEXT.FEHLER", "Fehler:", "Error:"),
    ("TEXT.BEANSTANDUNGEN",
     "Diese Eingaben wurden nicht übernommen — der bisherige Wert bleibt stehen:",
     "These entries were not applied — the previous value remains:"),
    ("TEXT.QUELLE", "Quelle", "Source"),
    ("TEXT.BROKER", "Broker", "Broker"),
    ("TEXT.AUTOSTART", "Autostart des Gateways", "Gateway autostart"),
    ("TEXT.VERBUNDEN", "Verbunden", "Connected"),
    ("TEXT.GESENDET", "Gesendete Nachrichten", "Messages sent"),
    ("TEXT.VERLUSTE", "Nicht abgesetzt", "Not delivered"),

    # ---------------- Kacheln
    ("TEXT.K_DIENST", "Dienst", "Service"),
    ("TEXT.K_ANWESEND", "anwesend", "present"),
    ("TEXT.K_AKTIVE_TAGS", "aktive Tags", "active tags"),
    ("TEXT.K_EMPFANG", "s seit letztem Empfang", "s since last reception"),
    ("TEXT.K_ABBILD", "s seit letztem Abbild", "s since last snapshot"),

    # ---------------- Spaltenüberschriften
    ("TEXT.SP_KENNUNG", "Kennung", "Identifier"),
    ("TEXT.SP_BEZEICHNUNG", "Bezeichnung", "Label"),
    ("TEXT.SP_AKTIV", "aktiv", "active"),
    ("TEXT.SP_ENTFERNEN", "entfernen", "remove"),
    ("TEXT.SP_ZUSTAND", "Zustand", "State"),
    ("TEXT.SP_ADRESSE", "Adresse", "Address"),
    ("TEXT.SP_SIGNAL", "Signal", "Signal"),
    ("TEXT.SP_ADRESSTYP", "Adresstyp", "Address type"),
    ("TEXT.SP_GEMELDETER_NAME", "Gemeldeter Name", "Reported name"),
    ("TEXT.SP_THEMA", "Thema", "Topic"),
    ("TEXT.SP_ART", "Art", "Type"),
    ("TEXT.SP_BEDEUTUNG", "Bedeutung", "Meaning"),
    ("TEXT.SP_THEMENZWEIG", "Themenzweig", "Topic branch"),
    ("TEXT.SP_ANGABE", "Angabe", "Item"),
    ("TEXT.SP_WERT", "Wert", "Value"),
    ("TEXT.SP_BAUSTEIN", "Baustein (Typ)", "Block (type)"),
    ("TEXT.SP_NAMENSVORSCHLAG", "Name (Vorschlag)", "Name (suggestion)"),
    ("TEXT.SP_PARAMETER", "Parameter", "Parameters"),
    ("TEXT.SP_EINGAENGE", "Eingänge verbinden mit", "Connect inputs to"),
    ("TEXT.SP_PRUEFUNG", "Prüfung", "Check"),
    ("TEXT.SP_ANMERKUNG", "Anmerkung", "Note"),
    ("TEXT.SP_KOMMT", "kommt", "arrivals"),
    ("TEXT.SP_GEHT", "geht", "departures"),
    ("TEXT.SP_LUECKE", "größte Lücke", "largest gap"),
    ("TEXT.SP_EMPFEHLUNG", "Empfehlung", "Recommendation"),
    ("TEXT.SP_ZEIT", "Zeit", "Time"),
    ("TEXT.SP_EREIGNIS", "Ereignis", "Event"),
    ("TEXT.E_KOMMT", "kommt", "arrives"),
    ("TEXT.E_GEHT", "geht", "leaves"),

    # ---------------- Reiter Einstellungen
    ("TEXT.DIENST_STEUERN", "Dienst steuern", "Control the service"),
    ("TEXT.DIENST_SOFORT",
     "Diese Knöpfe wirken sofort. Starten ist harmlos und umkehrbar; Anhalten und "
     "Neustarten unterbrechen die Anwesenheitserkennung für einige Sekunden.",
     "These buttons take effect immediately. Starting is harmless and reversible; "
     "stopping and restarting interrupt presence detection for a few seconds."),
    ("TEXT.TAGS", "Tags", "Tags"),
    ("TEXT.TAGS_HILFE",
     "Jeder Tag wird über seine Bluetooth-Adresse erkannt. Nur aktive Tags werden "
     "gemeldet. Zum Entfernen den Haken in der Spalte entfernen setzen und speichern.",
     "Each tag is identified by its Bluetooth address. Only active tags are reported. "
     "To delete a tag, tick the remove box and save."),
    ("TEXT.PH_BEZEICHNUNG", "z. B. Schlüssel Anna", "e.g. Anna's keys"),
    ("TEXT.PH_VON_HAND", "von Hand hinzufügen", "add manually"),
    ("TEXT.MEHR_EINSTELLUNGEN", "Mehr Einstellungen für diesen Tag",
     "More settings for this tag"),
    ("TEXT.ALIAS_HILFE",
     "Der Alias tritt an die Stelle der Adresse im MQTT-Thema und im Namen des "
     "virtuellen Eingangs. Damit bleibt die Loxone-Konfiguration gültig, wenn ein "
     "defekter Anhänger getauscht wird. Person fasst mehrere Tags zu einem Menschen "
     "zusammen.",
     "The alias replaces the address in the MQTT topic and in the virtual input name. "
     "That keeps the Loxone configuration valid when a broken tag is replaced. Person "
     "groups several tags into one human being."),
    ("TEXT.ADRESSE_WECHSELT", "Adresse wechselt — als Tag ungeeignet",
     "address rotates — unsuitable as a tag"),
    ("TEXT.GEFUNDENE_GERAETE", "Gefundene Geräte", "Devices found"),
    ("TEXT.GERAETE_ANHAKEN", "Gerät(e). Anhaken und speichern übernimmt sie.",
     "device(s). Tick and save to adopt them."),
    ("TEXT.NICHTS_NEUES", "Der Suchlauf hat nichts Neues gefunden.",
     "The scan found nothing new."),
    ("TEXT.WECHSELNDE_WARNUNG",
     "Geräte mit wechselnder Adresse (Telefone, Uhren, Kopfhörer) taugen nicht zur "
     "Anwesenheitserkennung: die eingetragene Adresse gilt nur bis zum nächsten "
     "Wechsel, meist eine Viertelstunde.",
     "Devices with rotating addresses (phones, watches, headphones) are unsuitable for "
     "presence detection: the stored address is only valid until the next change, "
     "typically a quarter of an hour."),
    ("TEXT.SUCHLAUF_HILFE",
     "Läuft der Dienst, werden dessen Sichtungen benutzt. Läuft er nicht, wird zwölf "
     "Sekunden lang selbst gesucht. Eingetippte Zeilen bleiben dabei erhalten.",
     "If the service is running, its sightings are used. If not, a twelve second scan "
     "is run. Values typed into the table are preserved."),
    ("TEXT.WEG_ZUM_MINISERVER", "Weg zum Miniserver", "Path to the Miniserver"),
    ("TEXT.MQTT_IM_REITER",
     "MQTT steht vollständig im eigenen Reiter MQTT. Hier steht nur der zusätzliche "
     "HTTP-Weg.",
     "MQTT lives entirely in its own MQTT tab. Only the additional HTTP path is set "
     "here."),
    ("TEXT.HTTP_HILFE",
     "Der Weg der Originalfassung: bei jeder Änderung werden virtuelle Eingänge am "
     "Miniserver gesetzt. Es werden dieselben Werte gesendet wie über MQTT. Nur "
     "einschalten, wenn eine bestehende Loxone-Konfiguration darauf aufbaut.",
     "The original approach: on every change virtual inputs are set on the Miniserver. "
     "The same values are sent as over MQTT. Only switch this on if an existing Loxone "
     "configuration relies on it."),
    ("TEXT.LOXBERRY_ID_HILFE",
     "Nur für den HTTP-Weg. Wird dem Eingangsnamen vorangestellt und muss zu den "
     "virtuellen Eingängen in Loxone passen.",
     "Only for the HTTP path. Prefixed to the input name and must match the virtual "
     "inputs in Loxone."),
    ("TEXT.MINISERVER_IST", "Angesprochen wird:", "The target is:"),
    ("TEXT.ADAPTER_UND_BETRIEB", "Adapter und Betrieb", "Adapter and operation"),
    ("TEXT.ADAPTER_HILFE", "Fast immer hci0.", "Almost always hci0."),
    ("TEXT.BA_SIGNAL", "Signalbetrieb — BlueZ meldet jede Änderung (empfohlen)",
     "Signal mode — BlueZ reports every change (recommended)"),
    ("TEXT.BA_ABFRAGE", "Abfragebetrieb — der Dienst fragt getaktet nach",
     "Polling mode — the service asks at fixed intervals"),
    ("TEXT.BETRIEBSART_HILFE",
     "Im Signalbetrieb sieht der Dienst jedes Werbepaket statt einer Stichprobe je "
     "Runde; die Glättung wird dadurch deutlich brauchbarer. Fehlt python3-gi, wird "
     "automatisch auf den Abfragebetrieb zurückgefallen, und das Protokoll sagt es.",
     "In signal mode the service sees every advertising packet instead of one sample "
     "per round, which makes smoothing far more useful. If python3-gi is missing it "
     "automatically falls back to polling and says so in the log."),
    ("TEXT.WACHHUND_HILFE",
     "Kommt über längere Zeit kein einziges Advertisement mehr an, wird die Suche neu "
     "gestartet und danach der Adapter aus- und wieder eingeschaltet. Das ist der "
     "häufigste Dauerbetriebsfehler: BlueZ läuft, meldet Erfolg, und es kommt trotzdem "
     "nichts mehr an.",
     "If no advertisement arrives at all for a longer period, discovery is restarted "
     "and then the adapter is powered off and on again. This is the most common "
     "long-run failure: BlueZ runs, reports success, and still nothing arrives."),
    ("TEXT.DISCOVERY_HILFE",
     "0 heißt aus. Ein Wert wie -90 sorgt dafür, dass BlueZ schwächere Geräte gar "
     "nicht erst meldet — das hält die Geräteliste klein. Zu scharf gesetzt "
     "verschwindet ein weit entfernter eigener Tag.",
     "0 means off. A value such as -90 makes BlueZ ignore weaker devices altogether, "
     "which keeps the device list small. Set too aggressively, a distant tag of your "
     "own disappears."),
    ("TEXT.LOGKAPPUNG_HILFE",
     "Ab dieser Größe bleiben die letzten 200 Zeilen stehen. Das Protokollverzeichnis "
     "liegt auf einer Ramdisk — eine unbegrenzt wachsende Datei trifft irgendwann alle "
     "Plugins.",
     "Above this size only the last 200 lines are kept. The log directory is on a "
     "ramdisk — a file growing without limit eventually affects every plugin."),
    ("TEXT.ZEITEN_UND_SCHWELLEN", "Zeiten und Schwellen", "Timing and thresholds"),
    ("TEXT.ABWESEND_HILFE",
     "Wie lange ein Tag nach der letzten Sichtung noch als anwesend gilt. Der Reiter "
     "Verlauf schlägt einen Wert vor, sobald genug Daten da sind.",
     "How long a tag still counts as present after its last sighting. The History tab "
     "suggests a value once there is enough data."),
    ("TEXT.ANKUNFT_HILFE",
     "So viele Sichtungen hintereinander müssen vorliegen, bevor abwesend zu anwesend "
     "wird. 1 heißt: ein einziges Paket genügt. Beim Weggehen gibt es ohnehin die "
     "Wartezeit oben; ohne diesen Wert ist die Logik unsymmetrisch, und ein Anhänger "
     "in der Tasche eines Passanten schaltet die Anwesenheit ein.",
     "This many consecutive sightings are required before away becomes present. 1 "
     "means a single packet is enough. Leaving already has the delay above; without "
     "this value the logic is asymmetric and a tag carried past on the street switches "
     "presence on."),
    ("TEXT.RSSI_MINIMUM_HILFE",
     "Schwächere Pakete zählen nicht als Sichtung. -100 heißt praktisch aus.",
     "Weaker packets do not count as a sighting. -100 means practically off."),
    ("TEXT.GLAETTUNG_HILFE",
     "Median über die letzten Messungen statt des zuletzt empfangenen Wertes. Ohne "
     "Glättung wechselt die Signalstufe bei einem Anhänger, der genau auf der Schwelle "
     "liegt, in jeder Runde.",
     "Median over the last measurements instead of the most recent value. Without "
     "smoothing the signal level of a tag sitting exactly on the threshold changes "
     "every round."),
    ("TEXT.HYSTERESE_HILFE",
     "Die Stufe wechselt erst, wenn die Schwelle um diesen Betrag überschritten wird. "
     "0 schaltet die Hysterese ab.",
     "The level only changes once the threshold is exceeded by this amount. 0 disables "
     "hysteresis."),
    ("TEXT.MEHR_WERTE", "Zusätzliche Werte", "Additional values"),
    ("TEXT.BEACON_HILFE",
     "Liest die Werbedaten mit: iBeacon, Eddystone, ATC/pvvx und RuuviTag. Damit "
     "liefern Beacons und Thermometer Temperatur, Luftfeuchte und Batteriestand, ohne "
     "dass eine Verbindung aufgebaut werden muss. Die Anordnung der ATC-Daten ist "
     "gegen die Formatbeschreibung gebaut, nicht an einem Gerät gemessen.",
     "Decodes advertising data: iBeacon, Eddystone, ATC/pvvx and RuuviTag. Beacons and "
     "thermometers thereby deliver temperature, humidity and battery level without any "
     "connection. The ATC layout is built from the format description, not measured on "
     "a device."),
    ("TEXT.ENTFERNUNG_HILFE",
     "Schätzt die Entfernung in Metern aus der Signalstärke. Das ist eine SCHÄTZUNG: "
     "in Innenräumen liegt sie leicht um den Faktor zwei daneben. Genauer wird sie mit "
     "einem je Tag kalibrierten Bezugswert (Reiter Test).",
     "Estimates the distance in metres from signal strength. This is an ESTIMATE: "
     "indoors it is easily off by a factor of two. It improves with a per-tag reference "
     "value calibrated in the Test tab."),
    ("TEXT.DAEMPFUNG_HILFE",
     "Dämpfungsexponent: 2,0 bei freier Sicht, 2,5 bis 3,5 in einer Wohnung, mehr "
     "durch Wände.",
     "Path loss exponent: 2.0 in free space, 2.5 to 3.5 inside a flat, more through "
     "walls."),
    ("TEXT.BATTERIE_HILFE",
     "Liest einmal täglich den Batteriestand über eine Verbindung. Achtung: der Scan "
     "steht dabei still, die meisten Beacons sind gar nicht verbindungsfähig, und "
     "manche Schlüsselfinder PIEPEN beim Verbinden. Deshalb je Tag einzeln einschalten.",
     "Reads the battery level once a day over a connection. Careful: scanning pauses "
     "meanwhile, most beacons cannot be connected to at all, and some key finders BEEP "
     "when connected. Enable it per tag."),
    ("TEXT.AUFZEICHNUNG", "Aufzeichnung", "Recording"),
    ("TEXT.EREIGNISSE_HILFE",
     "Schreibt jedes Kommen und Gehen mit. Nur damit lässt sich beantworten, ob "
     "Abwesend nach richtig eingestellt ist — siehe Reiter Verlauf.",
     "Records every arrival and departure. Only this makes it possible to answer "
     "whether the away delay is set correctly — see the History tab."),
    ("TEXT.MEHRERE_SCANNER", "Mehrere Scanner", "Multiple scanners"),
    ("TEXT.SCANNER_HILFE",
     "Wer zwei LoxBerrys mit diesem Plugin am selben Broker betreibt, überschreibt sich "
     "sonst gegenseitig die Zustände. Der Scannername trennt die Themen; die "
     "Raumzuordnung wählt daraus den stärksten Scanner.",
     "Running two LoxBerrys with this plugin against the same broker otherwise means "
     "they overwrite each other's states. The scanner name separates the topics; room "
     "assignment then picks the strongest scanner."),
    ("TEXT.RAUM_HILFE",
     "Bildet aus den Meldungen aller Scanner einen Raumnamen je Tag. Braucht "
     "eingeschaltete Scanner-Themen auf jedem beteiligten Gerät.",
     "Derives a room name per tag from the reports of all scanners. Requires scanner "
     "topics enabled on every participating device."),
    ("TEXT.AUSGLEICH_HILFE",
     "Ausgleich für DIESEN Scanner. Ein USB-Adapter mit externer Antenne hört "
     "systematisch stärker als ein Pi Zero; ohne Ausgleich gewinnt immer derselbe.",
     "Correction for THIS scanner. A USB adapter with an external antenna hears "
     "systematically stronger than a Pi Zero; without correction the same one always "
     "wins."),
    ("TEXT.SPEICHERN_HILFE",
     "Beim Speichern wird der Dienst neu gestartet, sofern er lief.",
     "Saving restarts the service, provided it was running."),
    ("TEXT.DIENST_NEU_GESTARTET", "Der Dienst wurde neu gestartet.",
     "The service was restarted."),
    ("TEXT.DIENST_LAEUFT_NICHT",
     "Der Dienst läuft nicht — siehe Reiter Logdateien.",
     "The service is not running — see the Log files tab."),
    ("TEXT.DIENST_WAR_AUS",
     "Der Dienst war angehalten und wurde nicht gestartet.",
     "The service was stopped and was not started."),
    ("TEXT.SCHREIBFEHLER",
     "Die Konfigurationsdatei konnte nicht geschrieben werden: %s",
     "The configuration file could not be written: %s"),
    ("TEXT.ALTES_FORMAT",
     "Die Konfiguration stammt noch aus der Originalfassung. Sie wird gelesen und beim "
     "nächsten Speichern ins neue Format geschrieben.",
     "The configuration still uses the original format. It is read and rewritten in "
     "the new format on the next save."),
    ("TEXT.DISCOVER_FEHLT", "bl_discover.py nicht gefunden: %s",
     "bl_discover.py not found: %s"),
    ("TEXT.SUCHLAUF_UNVERSTAENDLICH",
     "Der Suchlauf lieferte keine verwertbare Antwort:",
     "The scan returned no usable answer:"),

    # ---------------- Felder
    ("FELD.HTTP_PUSH", "Zusätzlich virtuelle Eingänge per HTTP setzen",
     "Additionally set virtual inputs via HTTP"),
    ("FELD.LOXBERRY_ID", "Kennung vor dem Eingangsnamen",
     "Prefix before the input name"),
    ("FELD.ADAPTER", "Bluetooth-Adapter", "Bluetooth adapter"),
    ("FELD.BETRIEBSART", "Betriebsart", "Operating mode"),
    ("FELD.WACHHUND", "Adapter wiederbeleben, wenn nichts mehr ankommt",
     "Revive the adapter when nothing arrives any more"),
    ("FELD.STILLE", "Stille bis zum Eingriff (Sekunden)",
     "Silence before intervening (seconds)"),
    ("FELD.DISCOVERY_RSSI", "Signalgrenze im BlueZ-Filter (dBm, 0 = aus)",
     "Signal limit in the BlueZ filter (dBm, 0 = off)"),
    ("FELD.LOGKAPPUNG", "Protokoll kappen ab (kB)", "Trim log above (kB)"),
    ("FELD.INTERVALL", "Auswertung alle (Sekunden)", "Evaluate every (seconds)"),
    ("FELD.ABWESEND", "Abwesend nach (Sekunden)", "Away after (seconds)"),
    ("FELD.AKTUALISIERUNG", "Alles neu melden alle (Sekunden)",
     "Report everything again every (seconds)"),
    ("FELD.ANKUNFT", "Sichtungen bis anwesend", "Sightings until present"),
    ("FELD.RSSI_MINIMUM", "Mindest-Signalstärke (dBm)", "Minimum signal strength (dBm)"),
    ("FELD.RSSI_NAH", "Schwelle nah (dBm)", "Threshold near (dBm)"),
    ("FELD.RSSI_MITTEL", "Schwelle mittel (dBm)", "Threshold medium (dBm)"),
    ("FELD.GLAETTUNG", "Signalstärke glätten", "Smooth signal strength"),
    ("FELD.FENSTER", "Messungen im Glättungsfenster",
     "Measurements in the smoothing window"),
    ("FELD.HYSTERESE", "Hysterese der Signalstufe (dB)",
     "Hysteresis of the signal level (dB)"),
    ("FELD.BEACON", "Werbedaten dekodieren (iBeacon, Eddystone, ATC, Ruuvi)",
     "Decode advertising data (iBeacon, Eddystone, ATC, Ruuvi)"),
    ("FELD.ENTFERNUNG", "Entfernung schätzen und veröffentlichen",
     "Estimate and publish distance"),
    ("FELD.DAEMPFUNG", "Dämpfungsexponent", "Path loss exponent"),
    ("FELD.BATTERIE", "Batteriestand über eine Verbindung lesen",
     "Read battery level over a connection"),
    ("FELD.BATTERIE_UHRZEIT", "Uhrzeit des Batterielaufs", "Time of the battery run"),
    ("FELD.EREIGNISSE", "Kommen und Gehen aufzeichnen", "Record arrivals and departures"),
    ("FELD.EREIGNISTAGE", "Verlauf aufbewahren (Tage)", "Keep history (days)"),
    ("FELD.SCANNER_NAME", "Name dieses Scanners", "Name of this scanner"),
    ("FELD.SCANNER_THEMEN", "Zusätzlichen Themenzweig je Scanner senden",
     "Publish an additional topic branch per scanner"),
    ("FELD.RAUM", "Raumzuordnung aus mehreren Scannern bilden",
     "Derive room assignment from several scanners"),
    ("FELD.RAUM_HYST", "Hysterese der Raumzuordnung (dB)",
     "Hysteresis of the room assignment (dB)"),
    ("FELD.RAUM_AUSGLEICH", "Ausgleich dieses Scanners (dB)",
     "Correction for this scanner (dB)"),
    ("FELD.MQTT", "Zustände per MQTT veröffentlichen (empfohlen)",
     "Publish states via MQTT (recommended)"),
    ("FELD.THEMENPRAEFIX", "MQTT-Themenpräfix", "MQTT topic prefix"),
    ("FELD.ALIAS", "Alias", "Alias"),
    ("FELD.PERSON", "Person", "Person"),
    ("FELD.ABW_JE_TAG", "Abwesend nach (s)", "Away after (s)"),
    ("FELD.REF_JE_TAG", "Bezug 1 m (dBm)", "Reference 1 m (dBm)"),
    ("FELD.BATT_JE_TAG", "Batterie lesen", "Read battery"),
    ("FELD.TESTTAG", "Tag für Testmodus und Kalibrierung",
     "Tag for test mode and calibration"),

    # ---------------- Beanstandungen
    ("MANGEL.KEINE_ZAHL",
     "%s: %s ist keine Zahl. Es bleibt bei %s.",
     "%s: %s is not a number. %s is kept."),
    ("MANGEL.AUSSERHALB",
     "%s: %s liegt außerhalb von %s bis %s. Es bleibt bei %s.",
     "%s: %s is outside %s to %s. %s is kept."),
    ("MANGEL.ADAPTER",
     "Bluetooth-Adapter: %s passt nicht zum Muster hciN. Es bleibt bei %s.",
     "Bluetooth adapter: %s does not match the pattern hciN. %s is kept."),
    ("MANGEL.BETRIEBSART", "Betriebsart: %s ist unbekannt.",
     "Operating mode: %s is unknown."),
    ("MANGEL.KENNUNG",
     "%s ist weder eine Bluetooth-Adresse noch eine iBeacon-Kennung. Die Zeile wurde "
     "nicht übernommen.",
     "%s is neither a Bluetooth address nor an iBeacon identifier. The row was not "
     "applied."),
    ("MANGEL.DOPPELT", "%s steht mehrfach in der Liste. Nur die erste Zeile gilt.",
     "%s appears more than once. Only the first row is used."),
    ("MANGEL.TAG_ABW",
     "%s: Abwesend nach %s liegt außerhalb von 5 bis 3600 Sekunden. Der globale Wert "
     "gilt.",
     "%s: away after %s is outside 5 to 3600 seconds. The global value applies."),
    ("MANGEL.TAG_REF",
     "%s: Bezugswert %s liegt außerhalb von -120 bis 0 dBm. Er wurde nicht übernommen.",
     "%s: reference value %s is outside -120 to 0 dBm. It was not applied."),
    ("MANGEL.UHRZEIT",
     "Uhrzeit des Batterielaufs: %s ist keine Uhrzeit im Format HH:MM. Es bleibt bei %s.",
     "Time of the battery run: %s is not a time in HH:MM format. %s is kept."),
    ("MANGEL.SCANNERNAME",
     "Scannername: %s enthält Zeichen, die in einem MQTT-Thema nichts zu suchen haben. "
     "Erlaubt sind Buchstaben, Ziffern, Bindestrich und Unterstrich.",
     "Scanner name: %s contains characters that do not belong in an MQTT topic. "
     "Letters, digits, hyphen and underscore are allowed."),
    ("MANGEL.PRAEFIX",
     "Themenpräfix: %s enthält Zeichen, die in einem MQTT-Thema nichts zu suchen haben. "
     "Es bleibt bei %s.",
     "Topic prefix: %s contains characters that do not belong in an MQTT topic. %s is "
     "kept."),
    ("MANGEL.PRAEFIX_LEER", "Das Themenpräfix darf nicht leer sein.",
     "The topic prefix must not be empty."),
    ("MANGEL.SCHWELLEN_GEDREHT",
     "Die Schwellen nah und mittel waren vertauscht und wurden getauscht.",
     "The near and medium thresholds were swapped and have been exchanged."),

    # ---------------- MQTT-Reiter
    ("TEXT.MQTT_UEBERTRAGUNG", "Übertragung per MQTT", "Transmission via MQTT"),
    ("TEXT.MQTT_HILFE",
     "MQTT ist der Regelweg. Die Zustände kommen zurückbehalten an; nach einem Neustart "
     "des Miniservers steht die Anwesenheit sofort wieder da.",
     "MQTT is the standard path. States arrive retained; after a Miniserver restart "
     "presence is available again immediately."),
    ("TEXT.PRAEFIX_HILFE",
     "Erlaubt sind Buchstaben, Ziffern, Bindestrich und Unterstrich. Ändern Sie ihn, "
     "bleiben die alten Themen im Broker stehen, bis sie dort entfernt werden.",
     "Letters, digits, hyphen and underscore are allowed. If you change it, the old "
     "topics remain in the broker until they are removed there."),
    ("TEXT.W_AUTOSTART",
     "Das MQTT-Gateway steht nicht auf Autostart (System, MQTT Gateway). Es wird "
     "gesendet, aber vermutlich hört niemand zu.",
     "The MQTT gateway is not set to autostart (System, MQTT Gateway). Data is sent, "
     "but probably nobody is listening."),
    ("TEXT.W_AUTOSTART_UNBEKANNT",
     "Der Autostart des MQTT-Gateways ließ sich nicht ablesen — general.json war nicht "
     "lesbar.",
     "The autostart setting of the MQTT gateway could not be read — general.json was "
     "not readable."),
    ("TEXT.GATEWAY_ZUSTAND", "Zustand des Gateways", "Gateway state"),
    ("TEXT.GATEWAY_FEHLT", "MQTT-Gateway nicht gefunden", "MQTT gateway not found"),
    ("TEXT.ABO_EINTRAGEN", "Abo im MQTT-Gateway eintragen",
     "Enter the subscription in the MQTT gateway"),
    ("TEXT.ABO_PFLICHT",
     "Ohne diesen Eintrag kommt am Miniserver nichts an.",
     "Without this entry nothing arrives at the Miniserver."),
    ("TEXT.ABO_WO",
     "Einzutragen unter System, MQTT Gateway, Subscriptions:",
     "To be entered under System, MQTT Gateway, Subscriptions:"),
    ("TEXT.THEMEN_TABELLE", "Alle veröffentlichten Themen",
     "All published topics"),
    ("TEXT.T_STEHT_FUER",
     "T steht für den Themenzweig eines Tags: die Adresse ohne Trennzeichen oder der "
     "eingetragene Alias. Das Gateway ersetzt jeden Schrägstrich durch einen "
     "Unterstrich; Punkte bleiben stehen.",
     "T stands for the topic branch of a tag: the address without separators, or the "
     "alias entered. The gateway replaces every slash with an underscore; dots remain."),
    ("TEXT.THEMEN_DER_TAGS", "Themen der eingetragenen Tags",
     "Topics of the configured tags"),

    # ---------------- Loxone-Reiter
    ("TEXT.LOX_SCHRITT_FUER_SCHRITT", "Einbindung in Loxone, Schritt für Schritt",
     "Loxone integration, step by step"),
    ("TEXT.LOX_EINLEITUNG",
     "Der Dienst sucht laufend nach den eingetragenen Tags und veröffentlicht die "
     "Zustände zurückbehalten. Loxone muss nichts abfragen.",
     "The service continuously scans for the configured tags and publishes their states "
     "retained. Loxone does not have to poll anything."),
    ("LOX.S1", "Schritt 1: Tags eintragen", "Step 1: enter the tags"),
    ("LOX.S1_TEXT",
     "Im Reiter Einstellungen, am einfachsten über Geräte suchen, anhaken und "
     "speichern. Ein Gerät, dessen Adresse als wechselnd angezeigt wird, taugt nicht.",
     "In the Settings tab, easiest via Search for devices, tick and save. A device "
     "whose address is shown as rotating is unsuitable."),
    ("LOX.S2", "Schritt 2: Abo im MQTT-Gateway eintragen",
     "Step 2: enter the subscription in the MQTT gateway"),
    ("LOX.S2_TEXT",
     "Ohne diesen Eintrag kommt am Miniserver nichts an. Einzutragen unter System, "
     "MQTT Gateway, Subscriptions:",
     "Without this entry nothing arrives at the Miniserver. To be entered under System, "
     "MQTT Gateway, Subscriptions:"),
    ("LOX.S3", "Schritt 3: Virtuelle Eingänge anlegen",
     "Step 3: create the virtual inputs"),
    ("LOX.S3_TEXT",
     "Am schnellsten über die Vorlage weiter unten. Von Hand angelegt heißt ein Eingang "
     "genau so wie das Thema, mit Unterstrich statt Schrägstrich.",
     "Fastest via the template below. Created by hand, an input is named exactly like "
     "the topic, with underscores instead of slashes."),
    ("LOX.S4", "Schritt 4: Kachel in der App", "Step 4: tile in the app"),
    ("LOX.S4_TEXT",
     "Einen Status-Baustein anlegen und v1 mit summary_present verbinden. Das ist die "
     "Zahl der anwesenden Tags; als Statustext eignet sich v1.0 von N sind da.",
     "Create a status block and connect v1 to summary_present. That is the number of "
     "present tags; a suitable status text is v1.0 of N are here."),
    ("LOX.S5", "Schritt 5: Ausfallerkennung", "Step 5: failure detection"),
    ("LOX.S5_TEXT",
     "Virtuelle Eingänge behalten ihren letzten Wert. Fällt der Dienst aus, sieht in "
     "der App alles normal aus. Deshalb server_ok und server_ts auswerten: ts ist ein "
     "Zeitstempel und wird in jedem Durchlauf neu gesetzt.",
     "Virtual inputs keep their last value. If the service fails, everything looks "
     "normal in the app. Therefore evaluate server_ok and server_ts: ts is a timestamp "
     "and is renewed in every cycle."),
    ("LOX.S6", "Schritt 6: Anwesenheit entprellen", "Step 6: debounce presence"),
    ("LOX.S6_TEXT",
     "BLE-Tags senden nicht ununterbrochen. Ein einzelner verpasster Empfang darf keine "
     "Abwesenheit auslösen. Dafür gibt es im Plugin Abwesend nach, und in Loxone "
     "zusätzlich eine Ausschaltverzögerung. Der Reiter Verlauf nennt eine Zahl, sobald "
     "genug Daten da sind.",
     "BLE tags do not transmit continuously. A single missed reception must not trigger "
     "absence. The plugin has the away delay for that, and Loxone an additional switch "
     "off delay. The History tab suggests a number once there is enough data."),
    ("TEXT.ALLES_AUF_EINMAL", "Alles auf einmal anlegen", "Create everything at once"),
    ("TEXT.VORLAGE_ANZAHL",
     "Für %d aktive Tag(s) entstehen %d Einträge.",
     "For %d active tag(s) this creates %d entries."),
    ("TEXT.VORLAGE_OHNE_TEXT",
     "Textthemen bleiben außen vor — das Vorlagenformat ist nur für Zahlenwerte belegt. "
     "Betroffen sind:",
     "Text topics are left out — the template format is only documented for numeric "
     "values. Affected are:"),
    ("TEXT.VORLAGE_IMPORT_HINWEIS",
     "Loxone Config legt beim Import neu an und überschreibt nichts. Zweimal "
     "importiert heißt doppelte Objekte.",
     "Loxone Config creates new objects on import and overwrites nothing. Importing "
     "twice means duplicate objects."),
    ("TEXT.VORLAGE_OHNE_TAG",
     "Kein Tag ist aktiv — die Vorlage hätte keine Einträge.",
     "No tag is active — the template would have no entries."),
    ("TEXT.BAUSTEINLISTE", "Schritt 7: Komplette Baustein-Liste",
     "Step 7: complete block list"),
    ("TEXT.BAUSTEIN_EINLEITUNG",
     "Wer diese Tabelle von oben nach unten abarbeitet, hat die Funktion nachgebaut. "
     "T steht für den Themenzweig eines Tags. Die Bausteine findet Loxone Config über "
     "die Baustein-Suche mit F5.",
     "Working through this table from top to bottom reproduces the function. T stands "
     "for the topic branch of a tag. Loxone Config finds the blocks via block search "
     "with F5."),
    ("TEXT.GEGENPROBE", "Schritt 8: Gegenprobe", "Step 8: verification"),
    ("TEXT.GEGENPROBE_TEXT",
     "Im MQTT Finder des Gateways auf den Themenzweig achten und den Anhänger einmal "
     "aus der Reichweite tragen. Kommt dort nichts an, fehlt meist das Abo aus "
     "Schritt 2.",
     "Watch the topic branch in the gateway MQTT finder and carry the tag out of range "
     "once. If nothing arrives there, the subscription from step 2 is usually missing."),
    ("TEXT.NICHT_VERLASSEN", "Worauf man sich nicht verlassen kann",
     "What you cannot rely on"),
    ("TEXT.NICHT_VERLASSEN_TEXT",
     "Mobiltelefone, Uhren und Kopfhörer wechseln ihre Bluetooth-Adresse regelmäßig, "
     "meist alle 15 Minuten. Das ist eine Datenschutzfunktion und lässt sich nicht "
     "abschalten. Zuverlässig sind einfache BLE-Beacons und Schlüsselfinder mit fester "
     "Adresse; der Suchlauf zeigt in der Spalte Adresstyp, was vorliegt.",
     "Mobile phones, watches and headphones rotate their Bluetooth address regularly, "
     "usually every 15 minutes. This is a privacy feature and cannot be switched off. "
     "Simple BLE beacons and key finders with a fixed address are reliable; the scan "
     "shows which is which in the address type column."),

    # ---------------- Bausteine
    ("BAUSTEIN.VI", "Virtueller Eingang", "Virtual input"),
    ("BAUSTEIN.DIGITAL", "digital", "digital"),
    ("BAUSTEIN.DIGITAL_JE_TAG", "digital, je Tag einer", "digital, one per tag"),
    ("BAUSTEIN.ANALOG_ZEIT", "analog, Sekunden seit 1970",
     "analog, seconds since 1970"),
    ("BAUSTEIN.ANALOG_ANZAHL", "analog, Anzahl", "analog, count"),
    ("BAUSTEIN.VOM_GATEWAY", "kommt über das Gateway", "comes via the gateway"),
    ("BAUSTEIN.AUS", "Ausschaltverzögerung", "Off delay"),
    ("BAUSTEIN.EIN", "Einschaltverzögerung", "On delay"),
    ("BAUSTEIN.ODER", "ODER", "OR"),
    ("BAUSTEIN.UND", "UND", "AND"),
    ("BAUSTEIN.NICHT", "NICHT", "NOT"),
    ("BAUSTEIN.FLANKE_F", "Flankenerkennung fallend", "Edge detection falling"),
    ("BAUSTEIN.FLANKE_S", "Flankenerkennung steigend", "Edge detection rising"),
    ("BAUSTEIN.FORMEL", "Formel", "Formula"),
    ("BAUSTEIN.STATUS", "Status", "Status"),
    ("BAUSTEIN.N_ENTPRELLT", "Schlüssel da, entprellt", "Keys here, debounced"),
    ("BAUSTEIN.P_ENTPRELLT", "120 s, je sparsamer das Tag, desto länger",
     "120 s, the more frugal the tag, the longer"),
    ("BAUSTEIN.E_ENTPRELLT", "Eingang = #5", "Input = #5"),
    ("BAUSTEIN.N_JEMAND", "Jemand ist zu Hause", "Somebody is at home"),
    ("BAUSTEIN.P_JEMAND", "eine Quelle je Person", "one source per person"),
    ("BAUSTEIN.E_JEMAND", "I1 bis In: je ein #7", "I1 to In: one #7 each"),
    ("BAUSTEIN.N_LETZTER", "Letzter ist gegangen", "Last one has left"),
    ("BAUSTEIN.E_LETZTER", "Eingang = #8", "Input = #8"),
    ("BAUSTEIN.N_ERSTER", "Erster ist gekommen", "First one has arrived"),
    ("BAUSTEIN.E_ERSTER", "Eingang = #8", "Input = #8"),
    ("BAUSTEIN.N_TOT", "Dienst antwortet nicht", "Service does not answer"),
    ("BAUSTEIN.E_TOT", "Eingang = #2", "Input = #2"),
    ("BAUSTEIN.N_AUSFALL", "Ausfall bestätigt", "Failure confirmed"),
    ("BAUSTEIN.P_AUSFALL", "900 s", "900 s"),
    ("BAUSTEIN.E_AUSFALL", "Eingang = #11, Ausgang an Benachrichtigung",
     "Input = #11, output to notification"),
    ("BAUSTEIN.N_GILT", "Abwesenheit gilt", "Absence is valid"),
    ("BAUSTEIN.E_GILT", "I1 = #9, I2 = #11 invertiert",
     "I1 = #9, I2 = #11 inverted"),
    ("BAUSTEIN.N_WIELANGE", "Wie lange schon weg", "How long already away"),
    ("BAUSTEIN.P_WIELANGE", "(Loxone-Zeit + 1230768000) - I1",
     "(Loxone time + 1230768000) - I1"),
    ("BAUSTEIN.E_WIELANGE", "I1 = #6", "I1 = #6"),
    ("BAUSTEIN.N_ANWESENHEIT", "Anwesenheit", "Presence"),
    ("BAUSTEIN.P_STATUS", "Statustext siehe Schritt 4", "status text see step 4"),
    ("BAUSTEIN.E_STATUS", "v1 = #4", "v1 = #4"),
    ("BAUSTEIN.ZU13", "Zu #13:", "On #13:"),
    ("BAUSTEIN.ZU13_TEXT",
     "Die wichtigste Zeile. Fällt der Dienst aus, melden alle Tags abwesend — ohne "
     "diese Verknüpfung löst das die volle Abwesenheitslogik aus.",
     "The most important row. If the service fails, all tags report absent — without "
     "this link that triggers the full absence logic."),
    ("BAUSTEIN.ZU7", "Zu #7:", "On #7:"),
    ("BAUSTEIN.ZU7_TEXT",
     "Die Ausschaltverzögerung kommt zusätzlich zur Einstellung Abwesend nach im "
     "Plugin. Beide zusammen ergeben die Gesamtzeit.",
     "The off delay is additional to the away delay in the plugin. Together they make "
     "up the total time."),
    ("BAUSTEIN.ZU14", "Zu #14:", "On #14:"),
    ("BAUSTEIN.ZU14_TEXT",
     "Loxone rechnet in Sekunden seit dem 01.01.2009. Aus dem Zeitstempel wird die "
     "Dauer deshalb mit dem Zuschlag 1230768000 gebildet.",
     "Loxone counts seconds since 1 January 2009. The duration is therefore derived "
     "from the timestamp using the offset 1230768000."),
    ("BAUSTEIN.ZU12", "Zu #12:", "On #12:"),
    ("BAUSTEIN.ZU12_TEXT",
     "Ein Benachrichtigungs-Baustein sendet nur beim Wechsel von Aus auf Ein. Niemals "
     "mehrere Quellen direkt an seinen Eingang, sondern erst über ODER zusammenführen.",
     "A notification block only sends on a change from off to on. Never connect several "
     "sources directly to its input; merge them via OR first."),

    # ---------------- Verlauf
    ("TEXT.VERLAUF_UEBERSCHRIFT", "Kommen und Gehen der letzten 24 Stunden",
     "Arrivals and departures of the last 24 hours"),
    ("TEXT.VERLAUF_EINLEITUNG",
     "Die größte Lücke ist die längste Zeit, die ein Tag am Stück nicht zu hören war. "
     "Die Empfehlung für Abwesend nach ist das Doppelte davon, aufgerundet.",
     "The largest gap is the longest stretch during which a tag was not heard. The "
     "recommendation for the away delay is twice that, rounded up."),
    ("TEXT.LETZTE_EREIGNISSE", "Letzte Ereignisse", "Recent events"),
    ("TEXT.EMPFEHLUNG", "mindestens %d s", "at least %d s"),
    ("TEXT.ZU_WENIG_DATEN", "noch zu wenig Daten", "not enough data yet"),
    ("TEXT.KEIN_VERLAUF",
     "Es gibt noch keinen Verlauf. Er entsteht, sobald ein Tag zum ersten Mal kommt "
     "oder geht — vorausgesetzt, die Aufzeichnung ist eingeschaltet.",
     "There is no history yet. It starts as soon as a tag arrives or leaves for the "
     "first time — provided recording is enabled."),

    # ---------------- Test-Reiter
    ("TEXT.SELBSTPRUEFUNG", "Selbstprüfung", "Self-check"),
    ("TEXT.SELBSTPRUEFUNG_HILFE",
     "Beantwortet ohne Loxone, ob die Einrichtung trägt. Ein Strich ist kein Haken: "
     "was nicht gemessen werden konnte, steht als Strich da und nicht als bestanden.",
     "Answers without Loxone whether the setup holds. A dash is not a tick: whatever "
     "could not be measured is shown as a dash, not as passed."),
    ("TEXT.BILANZ", "%d bestanden, %d fehlgeschlagen, %d nicht prüfbar.",
     "%d passed, %d failed, %d not verifiable."),
    ("TEXT.G_ANSEHEN", "Ansehen", "View"),
    ("TEXT.G_TECHNIK", "Technische Auskunft", "Technical information"),
    ("TEXT.G_AKTION", "Löst etwas aus", "Triggers something"),
    ("TEXT.G_KALIBRIEREN", "Testmodus und Kalibrierung",
     "Test mode and calibration"),
    ("TEXT.AKTION_SOFORT",
     "Diese Knöpfe wirken sofort und greifen in den laufenden Betrieb ein.",
     "These buttons take effect immediately and interfere with running operation."),
    ("TEXT.KALIBRIEREN_HILFE",
     "Testmodus schreibt 60 Sekunden lang jede Einzelmessung dieses Tags mit. Zum "
     "Kalibrieren den Tag auf einen Meter Abstand legen und den Knopf drücken; der "
     "Median der Messungen ist der Bezugswert für die Entfernungsschätzung und gehört "
     "danach in das Feld Bezug 1 m dieses Tags.",
     "Test mode records every single measurement of this tag for 60 seconds. To "
     "calibrate, place the tag one metre away and press the button; the median of the "
     "measurements is the reference value for distance estimation and belongs in the "
     "reference 1 m field of that tag."),
    ("TEXT.KALIBRIERERGEBNIS",
     "Kalibrierung für %s: %d Messungen, Median %s dBm.",
     "Calibration for %s: %d measurements, median %s dBm."),
    ("TEXT.NOCH_NICHTS_ABGEFRAGT",
     "Noch nichts abgefragt. Die Ausgabe der Knöpfe erscheint hier.",
     "Nothing queried yet. The output of the buttons appears here."),

    # ---------------- Logdateien
    ("TEXT.LOG_RAMDISK",
     "Das Protokollverzeichnis liegt auf einer Ramdisk — nach einem Neustart ist das "
     "Protokoll leer.",
     "The log directory is on a ramdisk — after a restart the log is empty."),
    ("TEXT.LOG_DATEI", "Datei", "File"),
    ("TEXT.LOG_NEUESTE", "neueste Zeile zuerst", "newest line first"),
    ("TEXT.LOG_LEER",
     "Noch keine Protokolldatei vorhanden. Sie entsteht, sobald der Dienst zum ersten "
     "Mal läuft.",
     "No log file yet. It appears as soon as the service runs for the first time."),

    # ---------------- Prüfzeilen
    ("PRUEF.DIENST", "Läuft der Dienst?", "Is the service running?"),
    ("PRUEF.DIENST_NEIN", "kein Prozess gefunden", "no process found"),
    ("PRUEF.ABBILD", "Ist das Abbild des Dienstes frisch?",
     "Is the service snapshot fresh?"),
    ("PRUEF.ABBILD_KEINS", "kein Abbild vorhanden", "no snapshot available"),
    ("PRUEF.ABBILD_ALTER", "vor %d s geschrieben", "written %d s ago"),
    ("PRUEF.EMPFANG", "Kommen überhaupt Advertisements an?",
     "Are any advertisements arriving at all?"),
    ("PRUEF.EMPFANG_UNBEKANNT",
     "noch keine Sichtung seit dem Start — das ist erst nach längerer Stille ein Befund",
     "no sighting since start — this only becomes a finding after prolonged silence"),
    ("PRUEF.EMPFANG_VOR", "letzte Sichtung vor %d s", "last sighting %d s ago"),
    ("PRUEF.ADAPTER_OK", "Meldet der Dienst den Adapter als in Ordnung?",
     "Does the service report the adapter as healthy?"),
    ("PRUEF.BETRIEBSART", "Läuft die eingestellte Betriebsart?",
     "Is the configured operating mode active?"),
    ("PRUEF.BETRIEBSART_IST", "läuft als %s, eingestellt ist %s",
     "running as %s, configured is %s"),
    ("PRUEF.MODUL", "Python-Modul %s vorhanden?", "Python module %s available?"),
    ("PRUEF.MODUL_FEHLT", "fehlt", "missing"),
    ("PRUEF.BLUETOOTHCTL", "Ist bluetoothctl vorhanden?", "Is bluetoothctl available?"),
    ("PRUEF.TAGS", "Ist mindestens ein Tag aktiv?", "Is at least one tag active?"),
    ("PRUEF.TAGS_ANZAHL", "%d eingetragen, %d aktiv", "%d configured, %d active"),
    ("PRUEF.ADRESSTYP", "Haben alle Tags eine feste Adresse?",
     "Do all tags have a fixed address?"),
    ("PRUEF.BROKER", "Ist ein MQTT-Broker eingetragen?",
     "Is an MQTT broker configured?"),
    ("PRUEF.AUTOSTART", "Steht das MQTT-Gateway auf Autostart?",
     "Is the MQTT gateway set to autostart?"),
    ("PRUEF.AUTOSTART_UNBEKANNT", "general.json nicht lesbar",
     "general.json not readable"),
    ("PRUEF.MQTT_VERBUNDEN", "Ist der Dienst mit dem Broker verbunden?",
     "Is the service connected to the broker?"),
    ("PRUEF.MQTT_ZAHLEN", "%d gesendet, %d nicht abgesetzt",
     "%d sent, %d not delivered"),
    ("PRUEF.MINISERVER", "Ist ein Miniserver eingetragen?",
     "Is a Miniserver configured?"),
    ("PRUEF.PUSH_OFFEN", "Sind alle HTTP-Werte am Miniserver angekommen?",
     "Have all HTTP values reached the Miniserver?"),
    ("PRUEF.PUSH_ZAHLEN", "%d offen, %d Fehlversuche", "%d pending, %d failures"),
    ("PRUEF.LESER",
     "Lesen PHP und Python dieselbe Konfiguration?",
     "Do PHP and Python read the same configuration?"),
    ("PRUEF.VORGABEN", "Sind die Vorgabewerte beider Seiten deckungsgleich?",
     "Are the default values on both sides identical?"),
    ("PRUEF.THEMENLISTE",
     "Passt die Themenliste zu dem, was der Sendecode veröffentlicht?",
     "Does the topic list match what the sending code publishes?"),
    ("PRUEF.VORLAGE", "Ist die erzeugte Loxone-Vorlage wohlgeformt?",
     "Is the generated Loxone template well formed?"),
    ("PRUEF.SPRACHEN", "Sind beide Sprachdateien deckungsgleich?",
     "Are both language files identical in keys?"),
    ("PRUEF.FASSUNG", "Nennen Datei und Dienst dieselbe Fassung?",
     "Do file and service report the same version?"),
    ("PRUEF.FASSUNG_KEINE",
     "fassung.txt fehlt — es gilt der Rückfallwert %s aus bl_common.py",
     "fassung.txt missing — the fallback %s from bl_common.py applies"),
    ("PRUEF.FASSUNG_IST", "Datei %s, Dienst %s", "file %s, service %s"),
    ("PRUEF.PYTHON_SELBSTTEST", "Besteht die Python-Seite ihre eigene Prüfung?",
     "Does the Python side pass its own check?"),
    ("PRUEF.PYTHON_ZAHLEN", "%d bestanden, %d fehlgeschlagen, %d nicht prüfbar",
     "%d passed, %d failed, %d not verifiable"),
    ("PRUEF.PROTOKOLL", "Bleibt das Protokoll unter der Kappungsgrenze?",
     "Does the log stay below the trim limit?"),
    ("PRUEF.PROTOKOLL_GROESSE", "%d kB, gekappt wird ab %d kB",
     "%d kB, trimmed above %d kB"),

    # ---------------- Test-Ausgaben
    ("TEST.T_SELBSTTEST", "Selbstprüfung", "Self-check"),
    ("TEST.T_STATUS", "Zustand des Dienstes", "Service state"),
    ("TEST.T_SICHTBAR", "Sichtbare Geräte", "Visible devices"),
    ("TEST.T_TAGS", "Zustand der Tags", "Tag states"),
    ("TEST.T_THEMEN", "MQTT-Themen", "MQTT topics"),
    ("TEST.T_VERLAUF", "Verlauf", "History"),
    ("TEST.T_BLUETOOTH", "Bluetooth", "Bluetooth"),
    ("TEST.T_KONFIG", "Konfiguration", "Configuration"),
    ("TEST.T_UMGEBUNG", "Umgebung", "Environment"),
    ("TEST.T_MQTT", "MQTT-Gateway", "MQTT gateway"),
    ("TEST.T_PROBEWERT", "Probewert an den Miniserver", "Test value to the Miniserver"),
    ("TEST.T_TESTMODUS", "Testmodus", "Test mode"),
    ("TEST.T_KALIBRIEREN", "Kalibrierung", "Calibration"),
    ("TEST.T_BATTERIE", "Batterielauf", "Battery run"),
    ("TEST.T_START", "Dienst starten", "Start service"),
    ("TEST.T_RESTART", "Dienst neu starten", "Restart service"),
    ("TEST.T_STOP", "Dienst anhalten", "Stop service"),
    ("TEST.T_UNBEKANNT", "Unbekannt", "Unknown"),
    ("TEST.UNBEKANNTE_AKTION", "Diese Aktion gibt es nicht.",
     "This action does not exist."),
    ("TEST.ZEITGRENZE_LEER",
     "[Zeitgrenze] Der Befehl hat innerhalb der Wartezeit nichts geliefert und wurde "
     "abgebrochen. Das heißt NICHT, dass kein Adapter da ist — es heißt, dass BlueZ "
     "nicht antwortet. Prüfen mit: systemctl status bluetooth",
     "[Timeout] The command returned nothing within the waiting time and was aborted. "
     "This does NOT mean there is no adapter — it means BlueZ is not answering. Check "
     "with: systemctl status bluetooth"),
    ("TEST.ZEITGRENZE_HALB",
     "[Zeitgrenze] Abgebrochen — die Ausgabe oben ist unvollständig.",
     "[Timeout] Aborted — the output above is incomplete."),
    ("TEST.BEFEHL_FEHLT",
     "[fehlt] Der Befehl ist auf diesem System nicht vorhanden. Bei bluetoothctl hilft: "
     "sudo apt-get install -y bluez",
     "[missing] The command does not exist on this system. For bluetoothctl this helps: "
     "sudo apt-get install -y bluez"),
    ("TEST.RUECKGABEWERT",
     "[Rückgabewert %d] Der Befehl endete mit einem Fehler, ohne etwas auszugeben.",
     "[Exit code %d] The command ended with an error without producing output."),
    ("TEST.SKRIPT_FEHLT", "Skript nicht gefunden: %s", "Script not found: %s"),
    ("TEST.KEINE_TEMPDATEI",
     "Es ließ sich keine temporäre Datei anlegen — die Prüfung wurde nicht gefahren.",
     "No temporary file could be created — the check was not run."),
    ("TEST.LESER_ABWEICHUNG",
     "Fall %d (%s): PHP liest [%s], Python liest [%s]",
     "Case %d (%s): PHP reads [%s], Python reads [%s]"),
    ("TEST.NUR_PHP", "nur in PHP: %s", "only in PHP: %s"),
    ("TEST.NUR_PYTHON", "nur in Python: %s", "only in Python: %s"),
    ("TEST.ANDERER_WERT", "unterschiedlicher Vorgabewert: %s",
     "different default value: %s"),
    ("TEST.SENDECODE_FEHLT",
     "ble_scanner_ng.py war nicht lesbar — die Themen konnten nicht verglichen werden.",
     "ble_scanner_ng.py was not readable — the topics could not be compared."),
    ("TEST.THEMA_FEHLT",
     "in der Anleitung, aber nicht im Sendecode: %s",
     "documented but not published by the sending code: %s"),
    ("TEST.THEMA_UNDOKUMENTIERT",
     "wird gesendet, steht aber in keiner Tabelle: %s",
     "published but listed in no table: %s"),
    ("TEST.KEIN_SIMPLEXML",
     "simplexml_load_string fehlt — die Vorlage konnte nicht geprüft werden.",
     "simplexml_load_string is missing — the template could not be checked."),
    ("TEST.VORLAGE_KAPUTT", "Die erzeugte Datei ist nicht wohlgeformt.",
     "The generated file is not well formed."),
    ("TEST.VORLAGE_ZEILENENDEN",
     "Zeilenenden gemischt: %d CRLF von %d Umbrüchen.",
     "Mixed line endings: %d CRLF out of %d breaks."),
    ("TEST.VORLAGE_INFO_FEHLT",
     "Das Kindelement Info templateType fehlt.",
     "The Info templateType child element is missing."),
    ("TEST.VORLAGE_GRENZEN",
     "Es stehen pauschale Grenzen von plusminus 2147483647 darin.",
     "It contains blanket limits of plus/minus 2147483647."),
    ("TEST.VORLAGE_ANZAHL", "%d Einträge erzeugt, %d Textthemen ausgelassen.",
     "%d entries created, %d text topics omitted."),
    ("TEST.BILANZ", "%d bestanden, %d fehlgeschlagen, %d nicht prüfbar.",
     "%d passed, %d failed, %d not verifiable."),
    ("TEST.F_DIENST", "Dienst", "Service"),
    ("TEST.F_FASSUNG", "Fassung", "Version"),
    ("TEST.F_SCANNER", "Scannername", "Scanner name"),
    ("TEST.F_BETRIEBSART", "Betriebsart", "Operating mode"),
    ("TEST.F_ABBILD", "Abbild", "Snapshot"),
    ("TEST.F_EMPFANG", "Letzte Sichtung", "Last sighting"),
    ("TEST.F_TAGS", "Tags aktiv / gesamt", "Tags active / total"),
    ("TEST.F_ADAPTER", "Adapter", "Adapter"),
    ("TEST.F_MQTT", "MQTT", "MQTT"),
    ("TEST.F_HTTP", "HTTP an Miniserver", "HTTP to Miniserver"),
    ("TEST.F_BROKER", "Broker", "Broker"),
    ("TEST.F_AUTOSTART", "Autostart des Gateways", "Gateway autostart"),
    ("TEST.F_PRAEFIX", "Themenpräfix", "Topic prefix"),
    ("TEST.F_VERBUNDEN", "Verbunden", "Connected"),
    ("TEST.F_GESENDET", "Gesendet", "Sent"),
    ("TEST.F_VERLUSTE", "Nicht abgesetzt", "Not delivered"),
    ("TEST.F_DATEI", "Datei", "File"),
    ("TEST.LAEUFT_PID", "läuft (PID %d)", "running (PID %d)"),
    ("TEST.LAEUFT_NICHT", "läuft nicht", "not running"),
    ("TEST.NICHT_VORHANDEN", "nicht vorhanden", "not available"),
    ("TEST.SEKUNDEN_ALT", "%d Sekunden alt", "%d seconds old"),
    ("TEST.VOR_SEKUNDEN", "vor %d s", "%d s ago"),
    ("TEST.STAND_VOR", "Stand: vor %d Sekunden", "As of: %d seconds ago"),
    ("TEST.ALTES_FORMAT",
     "Die Konfiguration liegt noch im Format der Originalfassung. Sie wird gelesen und "
     "beim nächsten Speichern umgeschrieben.",
     "The configuration is still in the original format. It is read and rewritten on "
     "the next save."),
    ("TEST.DIENST_TOT",
     "Der Dienst läuft nicht. Die Ursache steht meistens im Protokoll (Reiter "
     "Logdateien).",
     "The service is not running. The cause is usually in the log (Log files tab)."),
    ("TEST.KEIN_EMPFANG",
     "Seit %d Sekunden ist kein einziges Advertisement angekommen. Das deutet auf ein "
     "hängendes BlueZ hin — Bluetooth prüfen gibt Aufschluss.",
     "No advertisement at all has arrived for %d seconds. That points to a stuck BlueZ "
     "— Check Bluetooth gives more detail."),
    ("TEST.KEINE_ANGABEN", "Keine Angaben.", "No information."),
    ("TEST.KEIN_ABBILD",
     "Es gibt noch kein Abbild. Es entsteht, sobald der Dienst den ersten Durchlauf "
     "beendet hat.",
     "There is no snapshot yet. It appears once the service has finished its first "
     "cycle."),
    ("TEST.KEIN_ABBILD_KURZ",
     "(Kein Abbild — der Dienst läuft vermutlich nicht.)",
     "(No snapshot — the service is probably not running.)"),
    ("TEST.KEIN_TAG", "Es ist kein Tag eingetragen.", "No tag is configured."),
    ("TEST.KEIN_AKTIVER_TAG",
     "Kein Tag ist aktiv — es wird nichts je Tag veröffentlicht.",
     "No tag is active — nothing is published per tag."),
    ("TEST.NICHTS_GESEHEN",
     "(nichts gesehen)  BLE-Geräte senden nur, wenn sie eingeschaltet sind und aktiv "
     "werben. Manche Tags tun das nur nach einem Tastendruck.",
     "(nothing seen)  BLE devices only transmit when switched on and actively "
     "advertising. Some tags only do so after a button press."),
    ("TEST.SP_KENNUNG", "Kennung", "Identifier"),
    ("TEST.SP_NAME", "Name", "Name"),
    ("TEST.SP_AKTIV", "aktiv", "active"),
    ("TEST.SP_DA", "da", "here"),
    ("TEST.SP_STUFE", "Stufe", "Level"),
    ("TEST.SP_ZULETZT", "zuletzt", "last seen"),
    ("TEST.SP_ADRESSE", "Adresstyp", "Address type"),
    ("TEST.SP_KOMMT", "kommt", "arrivals"),
    ("TEST.SP_GEHT", "geht", "departures"),
    ("TEST.SP_LUECKE", "größte Lücke", "largest gap"),
    ("TEST.SP_EMPFEHLUNG", "Empfehlung", "Recommendation"),
    ("TEST.THEMEN_KOPF",
     "Zustände — zurückbehalten, der Miniserver hat den Stand also sofort nach einem "
     "Neustart wieder:",
     "States — retained, so the Miniserver has them again immediately after a restart:"),
    ("TEST.THEMEN_LIVE", "Zuletzt tatsächlich veröffentlicht:",
     "Actually published most recently:"),
    ("TEST.VERLAUF_KOPF", "Auswertung der letzten 24 Stunden",
     "Evaluation of the last 24 hours"),
    ("TEST.VERLAUF_ZEILEN", "%d Ereignisse in diesem Zeitraum.",
     "%d events in this period."),
    ("TEST.EMPFEHLUNG", "mindestens %d s", "at least %d s"),
    ("TEST.ZU_WENIG_DATEN", "noch zu wenig Daten", "not enough data yet"),
    ("TEST.KEIN_VERLAUF",
     "Es gibt noch keine Verlaufsdatei.", "There is no history file yet."),
    ("TEST.BT_GESUCHT", "Gesucht wird auf Adapter: %s",
     "Scanning on adapter: %s"),
    ("TEST.BT_HINWEIS",
     "Wird kein Adapter aufgelistet, fehlt die Hardware oder der Benutzer darf nicht "
     "auf BlueZ zugreifen. Ein Raspberry Pi ohne eingebautes Bluetooth braucht einen "
     "USB-Adapter. Fehlt loxberry in der Gruppe bluetooth, hilft: sudo usermod -a -G "
     "bluetooth loxberry und danach ein Neustart.",
     "If no adapter is listed, the hardware is missing or the user is not allowed to "
     "access BlueZ. A Raspberry Pi without built-in Bluetooth needs a USB adapter. If "
     "loxberry is missing from the bluetooth group this helps: sudo usermod -a -G "
     "bluetooth loxberry followed by a reboot."),
    ("TEST.KEINE_DATEI",
     "Datei nicht vorhanden — es gelten die Vorgabewerte:",
     "File not present — the default values apply:"),
    ("TEST.RECHTE", "Rechte: %s", "Permissions: %s"),
    ("TEST.MODULE", "Benötigte Python-Module:", "Required Python modules:"),
    ("TEST.WERKZEUGE", "Werkzeuge:", "Tools:"),
    ("TEST.VORHANDEN", "vorhanden", "available"),
    ("TEST.FEHLT", "FEHLT", "MISSING"),
    ("TEST.NACHINSTALLIEREN",
     "Fehlt etwas, hat die Installation die Pakete nicht eingerichtet. Nachholen mit: "
     "sudo apt-get install -y bluez python3-dbus python3-gi python3-paho-mqtt",
     "If something is missing, the installation did not set up the packages. Catch up "
     "with: sudo apt-get install -y bluez python3-dbus python3-gi python3-paho-mqtt"),
    ("TEST.NICHT_GEFUNDEN", "nicht gefunden", "not found"),
    ("TEST.KEIN_GATEWAY",
     "Ohne MQTT-Gateway kann das Plugin nichts veröffentlichen. Das Gateway ist seit "
     "LoxBerry 3 Bestandteil des Systems und steht unter System, MQTT Gateway.",
     "Without the MQTT gateway the plugin cannot publish anything. The gateway has been "
     "part of the system since LoxBerry 3 and is found under System, MQTT Gateway."),
    ("TEST.MITLESEN",
     "Zum Mitlesen eignet sich der MQTT Finder des Gateways; dort auf %s achten.",
     "The gateway MQTT finder is suitable for watching; look for %s there."),
    ("TEST.KEIN_MINISERVER",
     "In general.json ist kein Miniserver eingetragen.",
     "No Miniserver is configured in general.json."),
    ("TEST.PROBE_KEINE_ANTWORT",
     "Keine Antwort — der Miniserver war nicht erreichbar.",
     "No answer — the Miniserver could not be reached."),
    ("TEST.PROBE_HINWEIS",
     "Ein HTTP 404 heißt: der Miniserver antwortet, kennt den virtuellen Eingang %s "
     "aber nicht. Ein 401 heißt: falsche Zugangsdaten in den LoxBerry-Einstellungen.",
     "An HTTP 404 means the Miniserver answers but does not know the virtual input %s. "
     "A 401 means wrong credentials in the LoxBerry settings."),
    ("TEST.TESTMODUS_OHNE_TAG",
     "Es wurde kein Tag ausgewählt.", "No tag was selected."),
    ("TEST.TESTMODUS_LAEUFT",
     "Der Testmodus für %s läuft 60 Sekunden. Die Einzelmessungen erscheinen im Abbild; "
     "die Seite erneuert die Kacheln von selbst.",
     "Test mode for %s runs for 60 seconds. The individual measurements appear in the "
     "snapshot; the page refreshes the tiles by itself."),
    ("TEST.KALIBRIERUNG_LAEUFT",
     "Die Kalibrierung läuft zehn Sekunden. Den Tag dabei auf einen Meter Abstand "
     "halten; das Ergebnis erscheint danach oben in diesem Reiter.",
     "Calibration runs for ten seconds. Keep the tag one metre away; the result then "
     "appears at the top of this tab."),
    ("TEST.BATTERIE_ANGEFORDERT",
     "Der Batterielauf wurde angefordert. Er startet im nächsten Durchlauf; der Scan "
     "steht dabei kurz still.",
     "The battery run was requested. It starts in the next cycle; scanning pauses "
     "briefly."),
    ("TEST.STEUER_FEHLER",
     "Der Auftrag ließ sich nicht ablegen. Läuft der Dienst, und ist die Ramdisk "
     "beschreibbar?",
     "The request could not be stored. Is the service running and the ramdisk "
     "writable?"),
    ("TEST.JETZT_PID", "Der Dienst läuft jetzt (PID %d).",
     "The service is now running (PID %d)."),
    ("TEST.START_FEHLGESCHLAGEN",
     "Der Dienst läuft nicht. Protokoll im Reiter Logdateien prüfen.",
     "The service is not running. Check the log in the Log files tab."),
    ("TEST.STOP_LAEUFT_NOCH",
     "Es läuft noch etwas — bitte Protokoll prüfen.",
     "Something is still running — please check the log."),
    ("TEST.STOP_OK",
     "Angehalten. Beim nächsten Systemstart startet der Dienst wieder.",
     "Stopped. The service starts again at the next system boot."),

    # ---------------- Themen
    ("THEMA.PRESENT", "Tag in Reichweite", "Tag in range"),
    ("THEMA.RSSI", "Signalstärke in dBm, -255 wenn nicht in Reichweite",
     "Signal strength in dBm, -255 when out of range"),
    ("THEMA.RSSI_AVG", "Geglättete Signalstärke in dBm",
     "Smoothed signal strength in dBm"),
    ("THEMA.LEVEL", "Signalstufe: 3 nah, 2 mittel, 1 schwach, 0 weg",
     "Signal level: 3 near, 2 medium, 1 weak, 0 gone"),
    ("THEMA.LAST_SEEN", "Sekunden seit der letzten Sichtung, -1 wenn nie",
     "Seconds since the last sighting, -1 if never"),
    ("THEMA.LAST_SEEN_TS",
     "Zeitstempel der letzten Sichtung in Sekunden seit 1970",
     "Timestamp of the last sighting in seconds since 1970"),
    ("THEMA.PRESENT_SINCE",
     "Zeitstempel des letzten Wechsels zwischen anwesend und abwesend",
     "Timestamp of the last change between present and away"),
    ("THEMA.NAME", "Bezeichnung des Tags", "Label of the tag"),
    ("THEMA.DISTANCE", "Geschätzte Entfernung in Metern, -1 ohne Bezugswert",
     "Estimated distance in metres, -1 without a reference value"),
    ("THEMA.BATTERY", "Batteriestand in Prozent", "Battery level in percent"),
    ("THEMA.BATTERY_TS", "Zeitstempel des Batteriewertes",
     "Timestamp of the battery value"),
    ("THEMA.RAUM", "Name des Scanners mit dem stärksten Signal",
     "Name of the scanner with the strongest signal"),
    ("THEMA.RAUM_SEIT", "Zeitstempel des letzten Raumwechsels",
     "Timestamp of the last room change"),
    ("THEMA.SRV_ONLINE", "Der Dienst läuft (Testament des Brokers)",
     "The service is running (broker last will)"),
    ("THEMA.SRV_OK", "Der Dienst arbeitet und hört Advertisements",
     "The service is working and hearing advertisements"),
    ("THEMA.SRV_TS", "Herzschlag: Zeitstempel jedes Durchlaufs",
     "Heartbeat: timestamp of every cycle"),
    ("THEMA.SRV_ADAPTER", "Der Bluetooth-Adapter antwortet",
     "The Bluetooth adapter is responding"),
    ("THEMA.SRV_SICHT", "Zeitstempel der letzten Sichtung irgendeines Gerätes",
     "Timestamp of the last sighting of any device"),
    ("THEMA.SUM_PRESENT", "Anzahl anwesender aktiver Tags",
     "Number of present active tags"),
    ("THEMA.SUM_TAGS", "Anzahl aktiver Tags", "Number of active tags"),
    ("THEMA.SUM_GESAMT", "Anzahl aller eingetragenen Tags",
     "Number of all configured tags"),
    ("THEMA.SUM_NAMES", "Bezeichnungen der anwesenden Tags",
     "Labels of the present tags"),
    ("THEMA.SRV_VERSION", "Fassung des Plugins", "Plugin version"),
    ("THEMA.SRV_SCANNER", "Name dieses Scanners", "Name of this scanner"),

    # ---------------- Adresstyp und Art
    ("ADRESSTYP.FEST", "fest", "fixed"),
    ("ADRESSTYP.STATISCH", "statisch zufällig", "static random"),
    ("ADRESSTYP.WECHSELND", "wechselt", "rotating"),
    ("ADRESSTYP.UNBEKANNT", "unbekannt", "unknown"),
    ("ART.DIGITAL", "digital", "digital"),
    ("ART.ANALOG", "analog", "analog"),
    ("ART.TEXT", "Text", "text"),

    # ---------------- Vorlage
    ("VORLAGE.FUSS", "Erzeugt vom LoxBerry-Plugin BLE-Scanner NG (%s)",
     "Created by the LoxBerry plugin BLE-Scanner NG (%s)"),
]


def pruefe():
    """Vor dem Schreiben: die Regeln fuer INI-Werte einhalten."""
    fehler = []
    gesehen = set()
    for schluessel, de, en in TEXTE:
        if schluessel in gesehen:
            fehler.append("Schluessel doppelt: " + schluessel)
        gesehen.add(schluessel)
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*\.[A-Z][A-Z0-9_]*", schluessel):
            fehler.append("Schluesselform: " + schluessel)
        for sprache, wert in (("de", de), ("en", en)):
            if '"' in wert:
                fehler.append("Anfuehrungszeichen im Wert (%s, %s)" % (schluessel, sprache))
            if "<" in wert or ">" in wert:
                fehler.append("Markup im Wert (%s, %s)" % (schluessel, sprache))
            if "&" in wert and ";" in wert:
                fehler.append("moegliche Entitaet im Wert (%s, %s)" % (schluessel, sprache))
            if "\n" in wert or "\r" in wert:
                fehler.append("Zeilenumbruch im Wert (%s, %s)" % (schluessel, sprache))
        # Platzhalter muessen in beiden Sprachen gleich oft vorkommen.
        if de.count("%s") != en.count("%s") or de.count("%d") != en.count("%d"):
            fehler.append("Platzhalter ungleich: " + schluessel)
    return fehler


def erzeugen(sprache):
    aus = {}
    for schluessel, de, en in TEXTE:
        abschnitt, name = schluessel.split(".", 1)
        aus.setdefault(abschnitt, []).append((name, de if sprache == "de" else en))
    kopf = (
        "; BLE-Scanner NG - Sprachdatei ({0})\n"
        "; ERZEUGT von Werkzeuge/ble_sprache_erzeugen.py - nicht von Hand aendern.\n"
        "; Beide Sprachen entstehen aus derselben Tabelle; sie koennen deshalb nicht\n"
        "; auseinanderlaufen. Wer einen Text aendert, aendert ihn dort.\n"
        ";\n"
        "; Jeder Wert steht in doppelten Anfuehrungszeichen und enthaelt selbst keine.\n"
        "; Umlaute stehen als direkte UTF-8-Zeichen: die Oberflaeche schickt jeden\n"
        "; Wert durch bl_e(), eine Entitaet waere doppelt maskiert.\n"
        "\n").format(sprache)
    zeilen = [kopf]
    for abschnitt in sorted(aus):
        zeilen.append("[%s]\n" % abschnitt)
        for name, wert in sorted(aus[abschnitt]):
            zeilen.append('%s = "%s"\n' % (name, wert))
        zeilen.append("\n")
    return "".join(zeilen)


def main():
    argumente = [a for a in sys.argv[1:] if not a.startswith("--")]
    probe = "--probe" in sys.argv
    if not argumente:
        print("Aufruf: ble_sprache_erzeugen.py <plugin-ordner> [--probe]")
        return 2
    ziel = Path(argumente[0]) / "templates" / "lang"

    fehler = pruefe()
    if fehler:
        print("ABBRUCH - die Tabelle verletzt die Regeln:")
        for f in fehler:
            print("  " + f)
        return 1

    print("%d Schluessel in %d Abschnitten."
          % (len(TEXTE), len({s.split('.')[0] for s, _d, _e in TEXTE})))
    if probe:
        print("Probe - es wurde nichts geschrieben.")
        return 0

    ziel.mkdir(parents=True, exist_ok=True)
    for sprache in ("de", "en"):
        pfad = ziel / ("language_%s.ini" % sprache)
        # write_bytes, damit die Zeilenenden nicht kippen (LF, wie im Bestand).
        pfad.write_bytes(erzeugen(sprache).encode("utf-8"))
        print("geschrieben: %s" % pfad)
    return 0


if __name__ == "__main__":
    sys.exit(main())
