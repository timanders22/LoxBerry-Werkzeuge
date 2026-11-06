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

STAND (vb_x10_ble, 09.10.2026, Welle X-10): BAUSTEIN.E_GILT schreibt den negierten
Eingang als "I2 = #18 (negiert)" - so liest ihn Werkzeuge/leitungen_setzen.py 1.1.

STAND (vb_bild_bl19, 18.10.2026, Welle Bild 19 / Musterprojekt, Vollausstattung): Reiter "Einbindung in
Loxone", Schritt 7 mit drei Seiten aus dem Musterprojekt (Entwurf Welle 19 bl, E15): die alte Liste
[BAUSTEIN] (61 Schluessel) und TEXT.LOX_MESSWERTE entfallen; neu 86 BAUSTEIN.* (55 Tabellenzeilen
Z1_01..Z3_13, Kaesten, Hinweise), 5 LOX.* (Kasten-/Hinweistitel, Bild, Link) und 3 KURZ.PERSON_* (E13);
neu gefasst:
LOX.S4_TEXT, LOX.S5_TEXT, TEXT.BAUSTEINLISTE, TEXT.BAUSTEIN_EINLEITUNG, TEXT.LOX_MESSWERTE_TEXT,
TEXT.SP_NAMENSVORSCHLAG.

STAND (vb_bild_bl20, 18.10.2026, Welle Bild 20 / Textnachzug 1.3.25): BAUSTEIN.Z2_13 (Seite "BLE-Scanner NG
Tags", Status "Person 1 mit WLAN (BLE)") mit V2 = #12 und der Zeile "zu Hause (erkannt ueber <v2>)" - der
Texteingang blescanner_person_Person1_quelle ist jetzt angeschlossen statt nur genannt.

STAND (vb_g13_bl, 24.10.2026, Gruppe 13 / MQTT, 1.3.28): Reiter "Einbindung in Loxone" ohne HTTP-Vorlage
(Namenstabelle, Befehle, Vorlage MQTT-Befehle); Bausteinliste nach Musterprojekt/baustein_listen.txt 55f214a5
(Seite Tags 23 Zeilen); neu BEFEHL.*, IRK, BTHome, Haus-Themen, Testmodus-Kasten, Pruefzeilen; berichtigt
TEST.STOP_OK (B20), FELD.BEACON/TEXT.BEACON_HILFE (B28), TEST.TESTMODUS_LAEUFT (E3); entfallen KURZ.* und die
Texte der HTTP-Vorlage (E12) - der Lauf auf 1.3.28 braucht deshalb einmal SPRACHWACHE=aus.

STAND (Drift-Abgleich, 06.11.2026): angeglichen an BLE-Scanner NG 1.3.34, 120 Schluessel neu, 18 Werte geaendert, 0 entfernt.
[ANSAGE] kommt jetzt aus Werkzeuge/gemeinsam/sprachausgabe_texte.json (gemeinsam_pruefen.ini_abschnitt), [ANSAGEPLUGIN]
steht dahinter in Tabellenreihenfolge (NACH_ANSAGE).

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
    ("KNOPF.BTEIN", "Bluetooth einschalten", "Switch Bluetooth on"),
    ("KNOPF.KONFIG", "Konfiguration anzeigen", "Show configuration"),
    ("KNOPF.UMGEBUNG", "Umgebung und Module", "Environment and modules"),
    ("KNOPF.MQTTINFO", "MQTT-Gateway", "MQTT gateway"),
    ("KNOPF.PROBEWERT", "Probewert an Miniserver senden", "Send test value to Miniserver"),
    ("KNOPF.BATTERIE", "Batterielauf jetzt anstoßen", "Run battery check now"),
    ("KNOPF.TESTMODUS", "Testmodus 60 s", "Test mode 60 s"),
    ("KNOPF.KALIBRIEREN", "Auf 1 m kalibrieren", "Calibrate at 1 m"),

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
    ("TEXT.BEANSTANDUNGEN", "Gespeichert wurde nichts – auch die übrigen Werte nicht. Beanstandet:",
     "Nothing was saved – not even the other values. Objections:"),
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
    ("TEXT.SP_NAMENSVORSCHLAG", "Name",
     "Name"),
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
    # Kopf wie alle Hausplugins (Entscheidung Nr. 43, 1.3.22): gruener Kasten
    # oben im Reiter Einstellungen, roh ausgegeben (bl_t ohne bl_e).
    ("TEXT.WAS_IST_DAS",
     "<b>Anwesenheit per Bluetooth Low Energy für den Loxone Miniserver.</b> Der Dienst hört über BlueZ auf die Funksignale der BLE-Geräte in Reichweite und meldet für jeden hinterlegten Tag, etwa einen Schlüsselanhänger, ob er anwesend ist – samt Signalstärke und, wo das Gerät sie mitsendet, Temperatur, Luftfeuchte und Batteriestand. Die Werte gehen über MQTT an den Miniserver, auf Wunsch zusätzlich per HTTP an virtuelle Eingänge.",
     "<b>Presence via Bluetooth Low Energy for the Loxone Miniserver.</b> The service listens through BlueZ for the radio signals of BLE devices in range and reports for every registered tag, such as a key fob, whether it is present – together with signal strength and, where the device sends them, temperature, humidity and battery level. The values reach the Miniserver over MQTT and, on request, additionally over HTTP to virtual inputs."),
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
    ("TEXT.BEACON_HILFE", "Liest die Werbedaten mit: iBeacon, Eddystone, ATC/pvvx, RuuviTag, Xiaomi MiBeacon (unverschlüsselt am Gerät gemessen; verschlüsselt mit dem Bind-Key je Gerät, AES-CCM mit geprüftem MIC), Qingping und BTHome v2 (unverschlüsselt). Damit liefern Beacons und Thermometer Temperatur, Luftfeuchte und Batteriestand über das MQTT-Gateway V2, ohne dass eine Verbindung aufgebaut werden muss. Die Anordnung der ATC-Daten ist gegen die Formatbeschreibung gebaut, nicht an einem Gerät gemessen.",
     "Reads the advertising data: iBeacon, Eddystone, ATC/pvvx, RuuviTag, Xiaomi MiBeacon (unencrypted measured on a device; encrypted with the bind key per device, AES-CCM with checked MIC), Qingping and BTHome v2 (unencrypted). Beacons and thermometers thus deliver temperature, humidity and battery level via MQTT gateway V2 without a connection. The arrangement of the ATC data is built against the format description, not measured on a device."),
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
    # Aus 1.3.11 (unvollstaendige Sicherungsdatei wird abgewiesen). Wortgleich
    # uebernommen; der Erzeuger kannte den Schluessel nicht, ein blindes
    # Neuerzeugen haette ihn geloescht. Gemessen am 13.09.2026: 491 Schluessel
    # in der Datei, 490 in der Tabelle.
    ("TEXT.SICH_FEHLEND",
     "In der Datei fehlen %d Einstellungen: %s. Eine unvollständige Sicherung wird "
     "nicht zurückgespielt — sonst fielen die fehlenden Werte stillschweigend auf "
     "die Werkseinstellung zurück, ohne dass an der Oberfläche etwas davon zu "
     "sehen wäre.",
     "The file is missing %d settings: %s. An incomplete backup is not restored — "
     "otherwise the missing values would silently fall back to the factory "
     "defaults, with nothing on the page to show it."),

    # ---------------- Retain je Thema (Hausstandard 03.09.2026), neu in 1.3.12
    ("TEXT.SP_RETAIN", "Retain", "Retain"),
    ("TEXT.RETAIN_JA", "ja", "yes"),
    ("TEXT.RETAIN_NEIN", "nein", "no"),
    ("TEXT.RETAIN_ERKLAERUNG",
     "Retain heißt: der Broker behält den letzten Wert und gibt ihn jedem neuen "
     "Abonnenten sofort. Zustände gehen so hinaus, damit Loxone nach einem Neustart "
     "des Miniservers den Stand hat. Messwerte mit Zeitbezug nicht — sonst erschiene "
     "nach einem Ausfall ein alter Wert als aktuell. Das Lebenszeichen server/ts "
     "nie: zurückbehalten zeigte es auf Dauer, der Dienst lebe. Ebenso nie, was der "
     "Dienst über sich selbst sagt (server/ok, server/adapter_ok). server/online ist "
     "der Letzte Wille: 1 beim Verbinden, 0 setzt der Broker selbst, wenn der Dienst "
     "wegbricht; die Deinstallation räumt das Thema ab.",
     "Retain means the broker keeps the last value and hands it to every new "
     "subscriber immediately. States are sent that way so that Loxone has the "
     "situation after a Miniserver restart. Time-related measurements are not — "
     "otherwise an old value would appear current after an outage. The heartbeat "
     "server/ts never is: retained it would claim forever that the service is "
     "alive. Neither is anything the service says about itself (server/ok, "
     "server/adapter_ok). server/online is the last will: 1 on connecting, 0 is set "
     "by the broker itself when the service drops out; uninstalling clears the "
     "topic."),
    ("MANGEL.ALIAS_RESERVIERT", "%s: der Alias %s ist ein Name, den der Themenbaum selbst belegt (%s). Er wurde nicht übernommen — sonst stritte das Thema des Tags mit einem allgemeinen Thema um dieselbe Stelle. Es bleibt bei %s.",
     "%s: the alias %s is a name the topic tree itself uses (%s). It was not applied — otherwise the tag topic would compete with a general topic for the same place. %s is kept."),
    ("PRUEF.RETAIN",
     "Stimmen die Retain-Tabellen, und ist jedes Thema eingeordnet?",
     "Do the retain tables match, and is every topic classified?"),
    ("TEST.RETAIN_ANDERS", "unterschiedlich eingeordnet: %s",
     "classified differently: %s"),
    ("TEST.RETAIN_OHNE_EINTRAG",
     "wird gesendet, steht aber in keiner Retain-Tabelle: %s",
     "published but in no retain table: %s"),
    ("TEST.RETAIN_BILANZ", "%d zurückbehalten, %d flüchtig.",
     "%d retained, %d transient."),
    ("TEST.RESERVIERT_ANDERS",
     "Die reservierten Zweignamen weichen zwischen PHP und Python ab.",
     "The reserved branch names differ between PHP and Python."),

    # ---------------- Bluetooth-Lage, neu in 1.3.12
    # Formulartoken - der Befund vom 13.09.2026: 18 von 24 Formularen ohne
    ("PRUEF.TOKEN", "Tragen alle Formulare ihr Token?",
     "Do all forms carry their token?"),
    ("PRUEF.TOKEN_BILANZ", "%d Formulare, %d mit Token, %d ohne",
     "%d forms, %d with token, %d without"),
    ("PRUEF.TOKEN_UNLESBAR",
     "index.php war nicht lesbar - die Zahl der Formulare blieb ungemessen.",
     "index.php was not readable - the number of forms stayed unmeasured."),
    ("PRUEF.ADAPTER_DA", "Ist ein Bluetooth-Adapter vorhanden?",
     "Is a Bluetooth adapter present?"),
    # ---------------- Schalter "Bluetooth einschalten", neu in 1.3.12
    ("TEST.T_BTEIN", "Bluetooth einschalten", "Switch Bluetooth on"),
    ("TEST.BTEIN_RUFE", "Aufgerufen wird %s (als root über eine sudo-Regel, "
     "die genau diesen Pfad und keine Argumente nennt).",
     "Calling %s (as root through a sudo rule naming exactly this path and no "
     "arguments)."),
    ("TEST.BTEIN_OHNE_HELFER",
     "Der Helfer %s ist nicht vorhanden. Er wird von postroot.sh beim "
     "Installieren abgelegt — bei einer Installation, die vor 1.3.12 gemacht "
     "wurde, gibt es ihn noch nicht. Das Plugin einmal neu einspielen, dann ist "
     "er da.",
     "The helper %s is missing. postroot.sh places it during installation — an "
     "installation made before 1.3.12 does not have it yet. Install the plugin "
     "once more and it will be there."),
    ("TEST.BTEIN_VON_HAND",
     "Von Hand geht es auch, als root: sudo modprobe hci_uart && sudo "
     "systemctl start bluetooth",
     "By hand as root: sudo modprobe hci_uart && sudo systemctl start "
     "bluetooth"),
    ("TEST.BTEIN_OK", "Der Adapter ist jetzt da.", "The adapter is there now."),
    ("TEST.BTEIN_NICHTS",
     "Es ist trotzdem kein Adapter angemeldet.",
     "Still no adapter registered."),
    ("TEST.BTEIN_DIENST",
     "Der Dienst hat beim Start vermutlich noch keinen Adapter gesehen. Einmal "
     "neu starten (Knopf „Dienst neu starten“), sonst kommen die Werte erst "
     "beim nächsten Anlauf.",
     "The service probably saw no adapter when it started. Restart it once "
     "(button „Restart service“), otherwise values arrive only on its next "
     "attempt."),
    ("TEST.BTEIN_NUR_BIS_NEUSTART", "Das gilt bis zum nächsten Neustart des LoxBerry. Eine blacklist-Zeile in /etc/modprobe.d verhindert nur das selbsttätige Laden, nicht dieses ausdrückliche; beim Hochlaufen greift sie wieder. Dauerhaft auf einem DietPi — am Gerät am 13.09.2026 gemessen, als root (der Benutzer loxberry darf das nicht, also zuerst su -): sudo /boot/dietpi/func/dietpi-set_hardware bluetooth enable. Das entfernt die blacklist-Datei, schaltet bluetooth.service und hciuart ein und überlebt einen Neustart. Wer lieber klickt: dietpi-config, Advanced Options, Bluetooth. Das Plugin ändert diese Datei nicht — sie gehört dem System, und dietpi-config würde eine fremde Änderung daran ohnehin überschreiben.",
     "This holds until the LoxBerry is rebooted next. A blacklist line in /etc/modprobe.d only prevents automatic loading, not this explicit one; on boot it applies again. Permanently on DietPi - measured on the device on 13/09/2026, as root (the loxberry user may not, so run su - first): sudo /boot/dietpi/func/dietpi-set_hardware bluetooth enable. That removes the blacklist file, enables bluetooth.service and hciuart, and survives a reboot. If you prefer a menu: dietpi-config, Advanced Options, Bluetooth. The plugin does not change that file - it belongs to the system, and dietpi-config would overwrite a foreign change anyway."),
    ("PRUEF.ADAPTER_KEIN_GERAET",
     "Der Kernel kennt kein Bluetooth-Gerät: /sys/class/bluetooth fehlt, und "
     "auch der Gerätebaum führt keines. Damit startet systemd bluetooth.service "
     "gar nicht, und jede Anfrage an org.bluez läuft in die Wartezeit. Hier "
     "hilft nur ein USB-Bluetooth-Adapter.",
     "The kernel knows no Bluetooth device: /sys/class/bluetooth is missing, and "
     "the device tree holds none either. systemd therefore does not start "
     "bluetooth.service at all, and every request to org.bluez runs into the "
     "timeout. Only a USB Bluetooth adapter helps here."),
    # Der haeufigere Fall, am 13.09.2026 an dieser Anlage gemessen: die Hardware
    # ist da (Geraetebaum und serdev-Bus fuehren sie), aber eine Blacklist haelt
    # die Treiber zurueck. Wer hier "kein Adapter vorhanden" liest, kauft einen
    # USB-Stecker, den er nicht braucht.
    ("PRUEF.ADAPTER_GESPERRT", "Eingebautes Bluetooth ist vorhanden, aber die Treiber sind gesperrt: %s führt „blacklist %s“. Einmalig einschalten: sudo modprobe btbcm hci_uart && sudo systemctl start bluetooth. Dauerhaft auf einem DietPi, als root (zuerst su -): sudo /boot/dietpi/func/dietpi-set_hardware bluetooth enable — oder über dietpi-config, Advanced Options, Bluetooth. Das Plugin ändert diese Datei nicht – sie ist eine Einstellung des Systems.",
     "Onboard Bluetooth is present, but its drivers are blacklisted: %s holds ‘blacklist %s’. To switch it on once: sudo modprobe btbcm hci_uart && sudo systemctl start bluetooth. Permanently on DietPi, as root (run su - first): sudo /boot/dietpi/func/dietpi-set_hardware bluetooth enable - or via dietpi-config, Advanced Options, Bluetooth. The plugin does not change that file - it is a system setting."),
    ("PRUEF.ADAPTER_KEIN_TREIBER",
     "Eingebautes Bluetooth ist vorhanden, aber es ist kein Treiber geladen. "
     "Prüfen mit: systemctl status bluetooth und journalctl -k | grep -i blue.",
     "Onboard Bluetooth is present, but no driver is loaded. Check with: "
     "systemctl status bluetooth and journalctl -k | grep -i blue."),
    ("PRUEF.ADAPTER_LEER",
     "Es ist kein Adapter angemeldet (/sys/class/bluetooth ist leer).",
     "No adapter is registered (/sys/class/bluetooth is empty)."),
    ("PRUEF.ADAPTER_ANDERER", "vorhanden ist %s, eingestellt ist %s",
     "present is %s, configured is %s"),
    ("PRUEF.ADAPTER_DIENST_AUS",
     "Ein Adapter ist da, aber bluetooth.service ist %s.",
     "An adapter is present, but bluetooth.service is %s."),

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
    ("TEXT.SUCHLAUF_ZEITGRENZE",
     "Der Suchlauf wurde nach %d Sekunden abgebrochen (Rückgabe %d). BlueZ antwortet "
     "nicht — prüfen mit: systemctl status bluetooth",
     "The scan was aborted after %d seconds (exit code %d). BlueZ is not answering — "
     "check with: systemctl status bluetooth"),
    ("TEXT.ARCHIV_VERWEIGERT",
     "Diese Oberfläche liegt nicht in der Installation (ausgepacktes Archiv oder "
     "Prüfordner; gefundene LoxBerry-Wurzel: %s). Damit nichts in die Anlage kommt, "
     "wird hier kein Dienst gestartet oder angehalten und kein Auftrag abgelegt.",
     "This page is not part of the installation (unpacked archive or test folder; "
     "LoxBerry root found: %s). To keep the installation untouched, no service is "
     "started or stopped here and no request is stored."),

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
    ("FELD.BEACON", "Werbedaten dekodieren (iBeacon, Eddystone, ATC, Ruuvi, Xiaomi MiBeacon, Qingping, BTHome)",
     "Decode advertising data (iBeacon, Eddystone, ATC, Ruuvi, Xiaomi MiBeacon, Qingping, BTHome)"),
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
    ("MANGEL.DOPPELT", "%s steht mehrfach in der Liste.",
     "%s appears more than once in the list."),
    ("MANGEL.TAG_ABW", "%s: Abwesend nach %s liegt außerhalb von 5 bis 3600 Sekunden. Es bleibt bei %s (- heißt: der globale Wert gilt).",
     "%s: away after %s is outside 5 to 3600 seconds. %s is kept (- means: the global value applies)."),
    ("MANGEL.TAG_REF", "%s: Bezugswert %s liegt außerhalb von -120 bis 0 dBm. Es bleibt bei %s (- heißt: keiner).",
     "%s: reference value %s is outside -120 to 0 dBm. %s is kept (- means: none)."),
    ("MANGEL.UHRZEIT",
     "Uhrzeit des Batterielaufs: %s ist keine Uhrzeit im Format HH:MM. Es bleibt bei %s.",
     "Time of the battery run: %s is not a time in HH:MM format. %s is kept."),
    ("MANGEL.SCANNERNAME", "Scannername: %s enthält Zeichen, die in einem MQTT-Thema nichts zu suchen haben. Erlaubt sind Buchstaben, Ziffern, Bindestrich und Unterstrich. Es bleibt bei %s.",
     "Scanner name: %s contains characters that do not belong in an MQTT topic. Letters, digits, hyphen and underscore are allowed. %s is kept."),
    ("MANGEL.PRAEFIX",
     "Themenpräfix: %s enthält Zeichen, die in einem MQTT-Thema nichts zu suchen haben. "
     "Es bleibt bei %s.",
     "Topic prefix: %s contains characters that do not belong in an MQTT topic. %s is "
     "kept."),
    ("MANGEL.PRAEFIX_LEER", "Das Themenpräfix darf nicht leer sein.",
     "The topic prefix must not be empty."),

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
    # Die Ueberschrift ist neutral: unter Gateway V2 ist nichts einzutragen,
    # und der LoxBerry-Kern schaltet dort die Eingabeknoepfe ab. Die
    # Aufforderung steht deshalb nur noch im V1-Satz ABO_PFLICHT, ABO_WO ist
    # eine reine Auskunft.
    ("TEXT.ABO_EINTRAGEN", "Das Abo im MQTT-Gateway",
     "The subscription in the MQTT gateway"),
    ("TEXT.ABO_PFLICHT", "Gilt für MQTT-Gateway V1: das Plugin trägt das Abo seit 1.3.20 selbst in seine Abo-Datei ein (config/plugins/&lt;Ordner&gt;/mqtt_subscriptions.cfg), die das Gateway beim Start und bei jeder Änderung liest. In der Liste unter System, MQTT Gateway, Subscriptions erscheint es nicht - dort muss nichts eingetragen werden. Ob die Datei das Präfix führt, zeigt der Reiter Test.",
     "Applies to MQTT gateway V1: since 1.3.20 the plugin enters the subscription itself in its subscription file (config/plugins/&lt;folder&gt;/mqtt_subscriptions.cfg), which the gateway reads at start and on every change. It does not appear in the list under System, MQTT Gateway, Subscriptions - nothing needs to be entered there. The Test tab shows whether the file carries the prefix."),
    ("TEXT.ABO_WO",
     "Die Themengruppe dieses Plugins lautet:",
     "The topic group of this plugin is:"),
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
    ("LOX.S2", "Schritt 2: Das Abo im MQTT-Gateway",
     "Step 2: the subscription in the MQTT gateway"),
    ("LOX.S3", "Schritt 3: Virtuelle Eingänge anlegen",
     "Step 3: create the virtual inputs"),
    ("LOX.S3_TEXT", "Je Zeile der Namenstabelle einen Virtuellen Eingang (Zahl) bzw. Virtuellen Texteingang (Text) anlegen, Name genau wie in der Tabelle, „Als Digitaleingang“ nicht anhaken. Der LoxBerry-Benutzer braucht im Miniserver Rechte. Ein anderes Präfix oder ein anderer Alias heißt: alle Namen neu.",
     "Create one Virtual Input (number) or Virtual Text Input (text) per row of the name table, name exactly as in the table, do not tick “Use as digital input”. The LoxBerry user needs rights in the Miniserver. A different prefix or alias means: all names new."),
    ("LOX.S4", "Schritt 4: Kachel in der App", "Step 4: tile in the app"),
    ("LOX.S4_TEXT", "Den Status „Anwesenheit (BLE)“ von der Seite „BLE-Scanner NG“ (Schritt 7) als Kachel in die App legen: er nennt, wer zu Hause ist, und zeigt „unbekannt“, wenn der Scanner gestört ist. Wie viele Tags in Reichweite sind (summary_present), zeigt der Status „Zustand (BLE)“.",
     "Put the status “Anwesenheit (BLE)” from the page “BLE-Scanner NG” (step 7) into the app as a tile: it says who is at home and shows “unknown” when the scanner is faulty. How many tags are in range (summary_present) is shown by the status “Zustand (BLE)”."),
    ("LOX.S5", "Schritt 5: Ausfallerkennung", "Step 5: failure detection"),
    ("LOX.S5_TEXT", "Virtuelle Eingänge behalten ihren letzten Wert. Fällt der Dienst aus, sieht in der App alles normal aus. Deshalb server_online auswerten – das setzt der Broker als Letzten Willen selbst auf 0 – und das Lebenszeichen status_zaehler mit einer Analogwertvalidierung (Tmc 120 s), denn es zählt höchstens alle 30 Sekunden weiter. server_ok taugt dafür nicht: es kommt nach einem harten Absturz nicht mehr. Die Anwesenheit (z. B. person_Person1_anwesend_gesamt) gilt nur zusammen mit server_online.",
     "Virtual inputs keep their last value. If the service fails, everything looks normal in the app. Therefore evaluate server_online – the broker itself sets it to 0 as last will – and the sign of life status_zaehler with a Value Validator (Tmc 120 s), as it counts on at most every 30 seconds. server_ok is not suitable for that: it no longer arrives after a hard crash. The presence (e.g. person_Person1_anwesend_gesamt) is only valid together with server_online."),
    ("LOX.S6", "Schritt 6: Anwesenheit entprellen", "Step 6: debounce presence"),
    ("LOX.S6_TEXT",
     "BLE-Tags senden nicht ununterbrochen. Ein einzelner verpasster Empfang darf keine "
     "Abwesenheit auslösen. Dafür gibt es im Plugin Abwesend nach, und in Loxone "
     "zusätzlich eine Ausschaltverzögerung. Der Reiter Verlauf nennt eine Zahl, sobald "
     "genug Daten da sind.",
     "BLE tags do not transmit continuously. A single missed reception must not trigger "
     "absence. The plugin has the away delay for that, and Loxone an additional switch "
     "off delay. The History tab suggests a number once there is enough data."),
    ("TEXT.VORLAGE_OHNE_TAG",
     "Kein Tag ist aktiv — die Vorlage hätte keine Einträge.",
     "No tag is active — the template would have no entries."),
    ("TEXT.BAUSTEINLISTE", "Schritt 7: Baustein-Listen aus dem Musterprojekt",
     "Step 7: block lists from the sample project"),
    ("TEXT.BAUSTEIN_EINLEITUNG", "Drei fertig verbundene Seiten aus dem LoxBerry-Plugins Musterprojekt. Wer eine Tabelle von oben nach unten abarbeitet, hat die Seite nachgebaut. Die Namen der Gateway-Eingänge rechnet die Tabelle aus den Einstellungen (Präfix, Alias und Person der Tags); ohne eingetragene Tags stehen die Beispielnamen des Musterprojekts da. Die Bausteine findet Loxone Config über die Baustein-Suche mit F5.",
     "Three fully connected pages from the LoxBerry plugins sample project. Whoever works through a table from top to bottom has rebuilt the page. The table computes the names of the gateway inputs from the settings (prefix, alias and person of the tags); without configured tags the example names of the sample project are shown. Loxone Config finds the blocks via the block search with F5."),
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
    # ---- Welle Bild 19 (BLE-Scanner NG 1.3.24, 18.10.2026; Entwurf Welle 19 bl, E1-E16): drei Seiten aus
    # dem LoxBerry-Plugins Musterprojekt - Tabellenzeilen Zs_nn = "Typ | Name | Parameter | Eingaenge" (Zeilen
    # mit Prozentzeichen doppelt, ueber sprintf), Kaesten SEITEn_SCHRITTm (Klartext), Hinweise SEITEn_Hm (HTML);
    # bl_bausteinliste() in htmlauth/bl_lib.php. Die alte Liste (61 Schluessel, 19 Zeilen) ist entfallen.
    ("BAUSTEIN.Z1_01", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_server_online | 1 = der Dienst ist mit dem MQTT-Broker verbunden; 0 setzt der Broker selbst, sobald der Dienst wegfällt (Letzter Wille, auch bei einem Absturz, nach etwa 90 s); zurückbehalten; MQTT-Gateway Fassung 2: Haken (weitere Instanz auf Seite „BLE-Scanner NG Messwerte“) | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_server_online | 1 = the service is connected to the MQTT broker; the broker itself sets 0 as soon as the service drops out (last will, also after a crash, after about 90 s); retained; MQTT gateway version 2: tick (further instance on page “BLE-Scanner NG Messwerte”) | —"),
    ("BAUSTEIN.Z1_02", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_status_zaehler | Lebenszeichen: zählt höchstens alle 30 s eins weiter, 0 bis 999, läuft um (nie retained); Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_status_zaehler | Sign of life: counts on by one at most every 30 s, 0 to 999, wraps around (never retained); version 2: tick | —"),
    ("BAUSTEIN.Z1_03", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_server_ok | 1 = der Dienst arbeitet und hört Bluetooth-Werbung; 0 = Bluetooth-Adapter aus oder blind; nie retained; Fassung 2: Haken und „Noncached“ | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_server_ok | 1 = the service works and hears Bluetooth advertising; 0 = Bluetooth adapter off or blind; never retained; version 2: tick and “Noncached” | —"),
    ("BAUSTEIN.Z1_04", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_summary_present | Anzahl der aktiven Tags in Reichweite (zählt auch Thermometer mit); zurückbehalten; Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_summary_present | Number of active tags in range (thermometers count too); retained; version 2: tick | —"),
    ("BAUSTEIN.Z1_05", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_summary_tags | Anzahl der aktiven Tags; zurückbehalten; Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_summary_tags | Number of active tags; retained; version 2: tick | —"),
    ("BAUSTEIN.Z1_06", "Konstante | Konstante 1 | Wert 1 | —",
     "Constant | Konstante 1 | value 1 | —"),
    ("BAUSTEIN.Z1_07", "Analogwertvalidierung | Lebenszeichen fehlt (BLE) | Tmc 120 s (vier Lebenszeichen ohne neuen Wert), Min 0, Max 999; Haken bei ‚En‘ im Eigenschaftsfenster entfernen | V = #2, En = #6",
     "Value Validator | Lebenszeichen fehlt (BLE) | Tmc 120 s (four signs of life without a new value), Min 0, Max 999; remove the tick at ‘En’ in the properties window | V = #2, En = #6"),
    ("BAUSTEIN.Z1_08", "NICHT | Keine frischen Daten (BLE) | — (der Dienst hört keine Bluetooth-Werbung) | I = #3",
     "NOT | Keine frischen Daten (BLE) | — (the service hears no Bluetooth advertising) | I = #3"),
    ("BAUSTEIN.Z1_09", "NICHT | Dienst nicht verbunden (BLE) | — (Letzter Wille des Brokers) | I = #1",
     "NOT | Dienst nicht verbunden (BLE) | — (last will of the broker) | I = #1"),
    ("BAUSTEIN.Z1_10", "ODER | Dienst nicht verbunden oder Adapter blind (BLE) | — | I1 = #8, I2 = #9",
     "OR | Dienst nicht verbunden oder Adapter blind (BLE) | — | I1 = #8, I2 = #9"),
    ("BAUSTEIN.Z1_11", "ODER | Störung (BLE) | — (Dienst weg, Adapter blind oder Lebenszeichen fehlt); sperrt sofort „Niemand zu Hause (BLE)“ | I1 = #10, I2 = Ausgang E von #7",
     "OR | Störung (BLE) | — (service gone, adapter blind or sign of life missing); immediately blocks “Niemand zu Hause (BLE)” | I1 = #10, I2 = output E of #7"),
    ("BAUSTEIN.Z1_12", "Einschaltverzögerung | Störung bestätigt (BLE) | 600 s (das Lebenszeichen kommt alle 30 s, also zwanzig Lebenszeichen; ein Neustart des Dienstes oder des Miniservers meldet nichts) | Eingang = #11",
     "Switch-On Delay | Störung bestätigt (BLE) | 600 s (the sign of life arrives every 30 s, so twenty signs of life; a restart of the service or of the Miniserver reports nothing) | Input = #11"),
    ("BAUSTEIN.Z1_13", "Benachrichtigung | Meldung Plugin gestört (BLE) | Text: BLE-Scanner NG – der Dienst meldet sich seit über 10 Minuten nicht oder hört kein Bluetooth (LoxBerry, MQTT-Gateway oder Bluetooth-Adapter). Solange gilt die Anwesenheit nicht, „Niemand zu Hause (BLE)“ schaltet nicht. In der App den Status „Zustand (BLE)“ lesen, im Plugin Reiter Test „Zustand des Dienstes“ | Eingang = #12",
     "Notification | Meldung Plugin gestört (BLE) | Text: BLE-Scanner NG – for more than 10 minutes the service has not reported or hears no Bluetooth (LoxBerry, MQTT gateway or Bluetooth adapter). Meanwhile presence is not valid, “Niemand zu Hause (BLE)” does not switch. Read the status “Zustand (BLE)” in the app, in the plugin tab Test “Service state” | Input = #12"),
    ("BAUSTEIN.Z1_14", "Status | Zustand (BLE) | Zeilen: V1 = 1 „das Plugin meldet sich seit mindestens 2 Minuten nicht (kein Lebenszeichen) – LoxBerry und MQTT-Gateway prüfen (Fassung 1: Abo blescanner/#, Fassung 2: Haken an blescanner/status/zaehler); im Plugin Reiter Test ‚Zustand des Dienstes‘, dann ‚Dienst neu starten‘“; V3 = 0 „der Dienst ist nicht mit dem MQTT-Broker verbunden – im Plugin Reiter Einstellungen ‚Dienst starten‘; hilft das nicht, Reiter Logdateien lesen“; V2 = 0 „der Dienst läuft, hört aber kein Bluetooth – im Plugin Reiter Test ‚Bluetooth prüfen‘, bei Bedarf ‚Bluetooth einschalten‘“; V5 = 0 „kein Tag aktiv – im Plugin Reiter Einstellungen ‚Geräte suchen‘, Tags anhaken und speichern“; ohne Bedingung „läuft – <v4> von <v5> Tags in Reichweite“; Visualisierung EIN | V1 = Ausgang E von #7, V2 = #3, V3 = #1, V4 = #4, V5 = #5",
     "Status | Zustand (BLE) | Rows: V1 = 1 “the plugin has not reported for at least 2 minutes (no sign of life) – check LoxBerry and MQTT gateway (version 1: subscription blescanner/#, version 2: tick at blescanner/status/zaehler); in the plugin tab Test ‘Service state’, then ‘Restart service’”; V3 = 0 “the service is not connected to the MQTT broker – in the plugin tab Settings ‘Start service’; if that does not help, read the tab Log files”; V2 = 0 “the service runs but hears no Bluetooth – in the plugin tab Test ‘Check Bluetooth’, if needed ‘Switch Bluetooth on’”; V5 = 0 “no tag active – in the plugin tab Settings ‘Search for devices’, tick tags and save”; without condition “running – <v4> of <v5> tags in range”; visualisation ON | V1 = output E of #7, V2 = #3, V3 = #1, V4 = #4, V5 = #5"),
    ("BAUSTEIN.Z1_15", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_person_Person1_anwesend_gesamt | 1 = Person 1 zu Hause (ein Tag mit der Zusatzangabe „Person“ = Person1 in Reichweite; mit WLAN-Kopplung zählt auch ihr Telefon), 0 = weg, -1 = keine Aussage; kommt immer, auch ohne Kopplung; zurückbehalten; gilt nur zusammen mit blescanner_server_online; Fassung 2: Haken (weitere Instanz auf Seite „BLE-Scanner NG Tags“) | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_person_Person1_anwesend_gesamt | 1 = person 1 at home (a tag with the additional setting “Person” = Person1 in range; with the WiFi coupling the phone counts too), 0 = away, -1 = no statement; always arrives, also without coupling; retained; only valid together with blescanner_server_online; version 2: tick (further instance on page “BLE-Scanner NG Tags”) | —"),
    ("BAUSTEIN.Z1_16", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_person_Person2_anwesend_gesamt | dasselbe für Person 2 (Zusatzangabe „Person“ = Person2); Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_person_Person2_anwesend_gesamt | the same for person 2 (additional setting “Person” = Person2); version 2: tick | —"),
    ("BAUSTEIN.Z1_17", "Formel | Person 1 da und Dienst online (BLE) | IF(I1>0;IF(I2>0;1;0);0) – nur 1 zählt als „da“, -1 (keine Aussage) nicht; stirbt der Dienst, bleibt „da“ im Broker stehen, erst mit dem Letzten Willen wird daraus „weg“ | I1 = #15, I2 = #1",
     "Formula | Person 1 da und Dienst online (BLE) | IF(I1>0;IF(I2>0;1;0);0) – only 1 counts as “present”, -1 (no statement) does not; if the service dies, “present” stays in the broker, only the last will turns it into “away” | I1 = #15, I2 = #1"),
    ("BAUSTEIN.Z1_18", "Formel | Person 2 da und Dienst online (BLE) | IF(I1>0;IF(I2>0;1;0);0) | I1 = #16, I2 = #1",
     "Formula | Person 2 da und Dienst online (BLE) | IF(I1>0;IF(I2>0;1;0);0) | I1 = #16, I2 = #1"),
    ("BAUSTEIN.Z1_19", "Ausschaltverzögerung | Person 1 da, entprellt (BLE) | 120 s, zusätzlich zu „Abwesend nach“ im Plugin (Werk 30 s): ein verpasster Funkspruch löst keine Abwesenheit aus; je sparsamer der Anhänger sendet, desto länger (der Plugin-Reiter Verlauf nennt eine Zahl) | Eingang = #17",
     "Switch-Off Delay | Person 1 da, entprellt (BLE) | 120 s, in addition to “Away after” in the plugin (default 30 s): a missed broadcast does not trigger absence; the more sparingly the fob sends, the longer (the plugin tab History gives a number) | Input = #17"),
    ("BAUSTEIN.Z1_20", "Ausschaltverzögerung | Person 2 da, entprellt (BLE) | 120 s | Eingang = #18",
     "Switch-Off Delay | Person 2 da, entprellt (BLE) | 120 s | Input = #18"),
    ("BAUSTEIN.Z1_21", "ODER | Jemand zu Hause (BLE) | — Ausgang Q ersetzt im eigenen Projekt den Platzhalter „Anwesenheit (eigene Quelle)“ (Seiten Saugroboter, Chromecast4lox, Abfahrtsassistent, Autos): dessen Abnehmer an diesen Ausgang legen, den Platzhalter löschen; weitere Personen über weitere ODER (je zwei Eingänge) davor | I1 = #19, I2 = #20",
     "OR | Jemand zu Hause (BLE) | — output Q replaces the placeholder “Anwesenheit (eigene Quelle)” in your own project (pages Saugroboter, Chromecast4lox, Abfahrtsassistent, cars): connect its consumers to this output, delete the placeholder; further persons via further OR blocks (two inputs each) in front | I1 = #19, I2 = #20"),
    ("BAUSTEIN.Z1_22", "UND | Niemand zu Hause (BLE) | — (I1 und I2 negiert: in Config auf den Eingangspunkt klicken, es erscheint ein kleiner Kreis) 1 = alle weg UND der Scanner läuft; bei Störung 0 – eine tote Erkennung schaltet keine Abwesenheitslogik. Ausgang Q ersetzt im eigenen Projekt den Platzhalter „Niemand zu Hause (eigene Quelle)“ (Seiten Alexa NG, Kodi-NG, Intercom, Ferien und Feiertage …) | I1 = #21 (negiert), I2 = #11 (negiert)",
     "AND | Niemand zu Hause (BLE) | — (I1 and I2 inverted: in Config click the input point, afterwards the input shows a small circle) 1 = everybody away AND the scanner is running; on a fault 0 – a dead detection switches no absence logic. Output Q replaces the placeholder “Niemand zu Hause (eigene Quelle)” in your own project (pages Alexa NG, Kodi-NG, Intercom, Ferien und Feiertage …) | I1 = #21 (inverted), I2 = #11 (inverted)"),
    ("BAUSTEIN.Z1_23", "Flankenerkennung | Erster ist gekommen (BLE) | Pd 1 s (Werkseinstellung); Ausgang On = Impuls, wenn der Erste heimkommt (z. B. Willkommensszene; nicht Teil der Liste) | Eingang = #21",
     "Edge Detection | Erster ist gekommen (BLE) | Pd 1 s (default); output On = pulse when the first one comes home (e.g. welcome scene; not part of the list) | Input = #21"),
    ("BAUSTEIN.Z1_24", "Flankenerkennung | Letzter ist gegangen (BLE) | Pd 1 s (Werkseinstellung); Ausgang On = Impuls, wenn der Letzte gegangen ist (z. B. Zentral-Aus; nicht Teil der Liste) | Eingang = #22",
     "Edge Detection | Letzter ist gegangen (BLE) | Pd 1 s (default); output On = pulse when the last one has left (e.g. central off; not part of the list) | Input = #22"),
    ("BAUSTEIN.Z1_25", "Formel | Wer ist da (BLE) | I1+2*I2 (0 = niemand, 1 = Person 1, 2 = Person 2, 3 = beide) | I1 = #19, I2 = #20",
     "Formula | Wer ist da (BLE) | I1+2*I2 (0 = nobody, 1 = person 1, 2 = person 2, 3 = both) | I1 = #19, I2 = #20"),
    ("BAUSTEIN.Z1_26", "Status | Anwesenheit (BLE) | Zeilen: V3 = 1 „unbekannt – der BLE-Scanner ist gestört; Status ‚Zustand (BLE)‘ lesen“; V2 = 1 „niemand zu Hause“; V1 = 3 „Person 1 und Person 2 zu Hause“; V1 = 1 „Person 1 zu Hause“; V1 = 2 „Person 2 zu Hause“; ohne Bedingung „keine Aussage“; Visualisierung EIN | V1 = #25, V2 = #22, V3 = #11",
     "Status | Anwesenheit (BLE) | Rows: V3 = 1 “unknown – the BLE scanner is faulty; read the status ‘Zustand (BLE)’”; V2 = 1 “nobody at home”; V1 = 3 “person 1 and person 2 at home”; V1 = 1 “person 1 at home”; V1 = 2 “person 2 at home”; without condition “no statement”; visualisation ON | V1 = #25, V2 = #22, V3 = #11"),
    ("BAUSTEIN.Z1_27", "Benachrichtigung | Meldung Alle gegangen (BLE) | Text: BLE-Scanner NG – niemand mehr zu Hause: alle Schlüsselanhänger sind seit 2 Minuten außer Reichweite. Fenster, Herd und Licht prüfen | Eingang = #22",
     "Notification | Meldung Alle gegangen (BLE) | Text: BLE-Scanner NG – nobody at home any more: all key fobs have been out of range for 2 minutes. Check windows, stove and lights | Input = #22"),
    ("BAUSTEIN.Z2_01", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_schluessel1_present | 1 = Schlüssel 1 in Reichweite (Tag mit Alias „schluessel1“); zurückbehalten; gilt nur zusammen mit blescanner_server_online; weitere Instanz nicht nötig – die Personen auf Seite „BLE-Scanner NG“ tragen die Anwesenheit; Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_schluessel1_present | 1 = key 1 in range (tag with alias “schluessel1”); retained; only valid together with blescanner_server_online; no further instance needed – the persons on page “BLE-Scanner NG” carry the presence; version 2: tick | —"),
    ("BAUSTEIN.Z2_02", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_schluessel1_level | Signalstufe: 3 nah (ab -65 dBm), 2 mittel (ab -85 dBm), 1 schwach, 0 weg; Schwellen im Plugin Reiter Einstellungen; zurückbehalten; Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_schluessel1_level | Signal level: 3 near (from -65 dBm), 2 medium (from -85 dBm), 1 weak, 0 gone; thresholds in the plugin tab Settings; retained; version 2: tick | —"),
    ("BAUSTEIN.Z2_03", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_schluessel1_rssi_avg | geglättete Signalstärke in dBm; -255 = außer Reichweite (bewusst nicht -1, das läge am starken Ende); nie retained; Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_schluessel1_rssi_avg | smoothed signal strength in dBm; -255 = out of range (deliberately not -1, that would be at the strong end); never retained; version 2: tick | —"),
    ("BAUSTEIN.Z2_04", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_schluessel1_last_seen | Sekunden seit dem letzten Funkspruch; -1 = noch nie gehört; nie retained; Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_schluessel1_last_seen | seconds since the last radio packet; -1 = never heard; never retained; version 2: tick | —"),
    ("BAUSTEIN.Z2_05", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_schluessel1_distance | geschätzte Entfernung in m; -1 = ohne Bezugswert; nur mit „Entfernung schätzen und veröffentlichen“ (Reiter Einstellungen) und einem Bezugswert am Tag (Nr. 18–23 oder Reiter Test „Auf 1 m kalibrieren“); nie retained; Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_schluessel1_distance | estimated distance in m; -1 = without reference value; only with “Estimate and publish distance” (tab Settings) and a reference value on the tag (no. 18–23 or tab Test “Calibrate at 1 m”); never retained; version 2: tick | —"),
    ("BAUSTEIN.Z2_06", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_schluessel1_battery | Batteriestand in %% aus dem täglichen Batterielauf (Werk 04:00); nur mit „Batteriestand über eine Verbindung lesen“ und am Tag „Batterie lesen“ (manche Schlüsselfinder piepen dabei); -1 = noch nie gelesen oder nicht lesbar; zurückbehalten; Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_schluessel1_battery | Battery level in %% from the daily battery run (default 04:00); only with “Read battery level via a connection” and “Read battery” on the tag (some key finders beep then); -1 = never read or not readable; retained; version 2: tick | —"),
    ("BAUSTEIN.Z2_07", "Status | Schlüssel 1 (BLE) | Zeilen: V1 = 0 und V4 < 0 „noch nie gehört – Alias im Plugin prüfen, dann ‚Testmodus Schlüssel 1‘ (Nr. 16) drücken“; V1 = 0 „außer Reichweite – zuletzt vor <v4> s gehört“; V6 > 0 und V6 < 20 „in Reichweite, Batterie schwach (<v6> %%) – Knopfzelle tauschen“; V2 = 3 und V5 > 0 „nah – <v3> dBm, etwa <v5.1> m“; V2 = 3 „nah – <v3> dBm“; V2 = 2 und V5 > 0 „mittlere Entfernung – <v3> dBm, etwa <v5.1> m“; V2 = 2 „mittlere Entfernung – <v3> dBm“; ohne Bedingung „schwacher Empfang am Rand der Reichweite – <v3> dBm“; Visualisierung EIN | V1 = #1, V2 = #2, V3 = #3, V4 = #4, V5 = #5, V6 = #6",
     "Status | Schlüssel 1 (BLE) | Rows: V1 = 0 and V4 < 0 “never heard – check the alias in the plugin, then press ‘Testmodus Schlüssel 1’ (no. 16)”; V1 = 0 “out of range – last heard <v4> s ago”; V6 > 0 and V6 < 20 “in range, battery weak (<v6> %%) – replace the coin cell”; V2 = 3 and V5 > 0 “near – <v3> dBm, about <v5.1> m”; V2 = 3 “near – <v3> dBm”; V2 = 2 and V5 > 0 “medium distance – <v3> dBm, about <v5.1> m”; V2 = 2 “medium distance – <v3> dBm”; without condition “weak reception at the edge of the range – <v3> dBm”; visualisation ON | V1 = #1, V2 = #2, V3 = #3, V4 = #4, V5 = #5, V6 = #6"),
    ("BAUSTEIN.Z2_08", "Formel | Batterie Schlüssel 1 schwach (BLE) | IF(I1>0;IF(I1<20;1;0);0) – unter 20 Prozent; -1 (noch nie gelesen) zählt nicht | I1 = #6",
     "Formula | Batterie Schlüssel 1 schwach (BLE) | IF(I1>0;IF(I1<20;1;0);0) – below 20 percent; -1 (never read) does not count | I1 = #6"),
    ("BAUSTEIN.Z2_09", "Einschaltverzögerung | Batterie Schlüssel 1 schwach bestätigt (BLE) | 600 s | Eingang = #8",
     "Switch-On Delay | Batterie Schlüssel 1 schwach bestätigt (BLE) | 600 s | Input = #8"),
    ("BAUSTEIN.Z2_10", "Benachrichtigung | Meldung Batterie Schlüssel 1 schwach (BLE) | Text: BLE-Scanner NG – die Batterie von Schlüssel 1 ist unter 20 Prozent. Knopfzelle tauschen, sonst fällt die Anwesenheit dieses Anhängers bald aus | Eingang = #9",
     "Notification | Meldung Batterie Schlüssel 1 schwach (BLE) | Text: BLE-Scanner NG – the battery of key 1 is below 20 percent. Replace the button cell, otherwise the presence of this fob will soon fail | Input = #9"),
    ("BAUSTEIN.Z2_11", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_person_Person1_anwesend_gesamt | weitere Instanz von Seite „BLE-Scanner NG“ Nr. 15: kommt immer; mit „Anwesenheit mit dem WLAN-Scanner zusammenführen“ und der Zuordnung „Beispiel=Person1“ (derselbe Name wie wifi_ng_Beispiel auf Seite „WiFi-Scanner-NG“; sendet der WLAN-Scanner für diese Person -1, zählt das als keine Aussage) zählt auch das Telefon; 1 = da, 0 = weg, -1 = keine Aussage; wer die Kopplung einschaltet, verdrahtet nichts um | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_person_Person1_anwesend_gesamt | further instance of page “BLE-Scanner NG” no. 15: always arrives; with “Merge presence with the WiFi scanner” and the assignment “Beispiel=Person1” (the same name as wifi_ng_Beispiel on page “WiFi-Scanner-NG”; if the WiFi scanner sends -1 for this person, that counts as no statement) the phone counts too; 1 = present, 0 = away, -1 = no statement; switching the coupling on needs no rewiring | —"),
    ("BAUSTEIN.Z2_12", "Virtueller Texteingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_person_Person1_quelle | Titel genau so, „In Visualisierung verwenden“ an; welche Quelle die Aussage trägt: ble, wlan, ble+wlan oder - ; kommt immer (ohne Kopplung „ble“); zurückbehalten; Fassung 2: Haken | —",
     "Virtual Text Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_person_Person1_quelle | title exactly like this, “Use in visualisation” on; which source carries the statement: ble, wlan, ble+wlan or - ; always arrives (without coupling “ble”); retained; version 2: tick | —"),
    ("BAUSTEIN.Z2_13", "Status | Person 1 mit WLAN (BLE) | Zeilen: V1 = 1 „zu Hause (erkannt über <v2>)“; V1 = 0 „weg (laut <v2>)“; ohne Bedingung „keine Aussage – Dienst gestört oder alle Quellen schweigen“; Visualisierung EIN | V1 = #11, V2 = #12",
     "Status | Person 1 mit WLAN (BLE) | Rows: V1 = 1 “at home (detected via <v2>)”; V1 = 0 “away (according to <v2>)”; without condition “no statement – service disturbed or all sources silent”; visualisation ON | V1 = #11, V2 = #12"),
    ("BAUSTEIN.Z2_14", "Virtueller Texteingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_summary_names | Titel genau so, „In Visualisierung verwenden“ an; Bezeichnungen der Tags in Reichweite, durch Komma getrennt; leer, wenn niemand da ist; nie retained; Fassung 2: Haken | —",
     "Virtual Text Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_summary_names | title exactly like this, “Use in visualisation” on; names of the tags in range, separated by commas; empty when nobody is there; never retained; version 2: tick | —"),
    ("BAUSTEIN.Z2_15", "Virtueller Texteingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_schluessel1_raum | Titel genau so, „In Visualisierung verwenden“ an; nur mit mehreren Scannern und „Raumzuordnung aus mehreren Scannern bilden“: Name des Scanners mit dem stärksten Signal; „-“ = keine Aussage; zurückbehalten; Fassung 2: Haken | —",
     "Virtual Text Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_schluessel1_raum | title exactly like this, “Use in visualisation” on; only with several scanners and “Build room assignment from several scanners”: name of the scanner with the strongest signal; “-” = no statement; retained; version 2: tick | —"),
    ("BAUSTEIN.Z3_01", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_thermometer_wohnzimmer_present | 1 = das Thermometer (Tag mit Alias „thermometer_wohnzimmer“, z. B. Xiaomi MJ_HT_V1) ist in Reichweite; zurückbehalten; Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_thermometer_wohnzimmer_present | 1 = the thermometer (tag with alias “thermometer_wohnzimmer”, e.g. Xiaomi MJ_HT_V1) is in range; retained; version 2: tick | —"),
    ("BAUSTEIN.Z3_02", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_thermometer_wohnzimmer_sensor_temperatur | Temperatur in °C aus dem Funkspruch, ohne Kopplung; verschlüsselnde Xiaomi-Fühler mit dem Bind-Key im Plugin (Reiter Einstellungen, auch aus der Xiaomi-Cloud); -999 = keine Aussage (seit der Frist im Plugin, Werk 30 Minuten, kein Messwert, oder Funkspruch nicht lesbar – Grund in Nr. 14); Statistik ein (ein -999 erscheint dort als Lücke); nie retained (Messwert) – nach einem Neustart des Miniservers holt der zentrale reconnect den letzten Wert aus dem Gateway; kann im eigenen Projekt den Platzhalter „Raumtemperatur Wohnzimmer (eigene Quelle)“ (Seite Fensterbilanz) ersetzen, dann -999 vorher abfangen; Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_thermometer_wohnzimmer_sensor_temperatur | temperature in °C from the radio packet, without pairing; encrypting Xiaomi sensors with the bind key in the plugin (tab Settings, also from the Xiaomi cloud); -999 = no statement (no reading since the deadline in the plugin, default 30 minutes, or packet not readable – reason in no. 14); statistics on (a -999 shows there as a gap); never retained (measured value) – after a restart of the Miniserver the central reconnect fetches the last value from the gateway; can replace the placeholder “Raumtemperatur Wohnzimmer (eigene Quelle)” (page Fensterbilanz) in your own project, then catch -999 first; version 2: tick | —"),
    ("BAUSTEIN.Z3_03", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_thermometer_wohnzimmer_sensor_feuchte | relative Luftfeuchte in %% aus dem Funkspruch; -1 = keine Aussage (wie Nr. 2); Statistik ein; nie retained; Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_thermometer_wohnzimmer_sensor_feuchte | relative humidity in %% from the radio packet; -1 = no statement (as no. 2); statistics on; never retained; version 2: tick | —"),
    ("BAUSTEIN.Z3_04", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_thermometer_wohnzimmer_sensor_batterie | Batteriestand in %%; kommt in eigenen, selteneren Funksprüchen (sparsame Fühler etwa einmal je Stunde); -1 = noch nicht gemeldet oder seit 24 Stunden kein Batteriesatz; nie retained; Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_thermometer_wohnzimmer_sensor_batterie | battery level in %%; arrives in separate, rarer packets (economical sensors about once per hour); -1 = not yet reported or no battery record for 24 hours; never retained; version 2: tick | —"),
    ("BAUSTEIN.Z3_05", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_thermometer_wohnzimmer_last_seen | Sekunden seit dem letzten Funkspruch; -1 = noch nie gehört; nie retained; Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_thermometer_wohnzimmer_last_seen | seconds since the last radio packet; -1 = never heard; never retained; version 2: tick | —"),
    ("BAUSTEIN.Z3_06", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_server_online | 1 = der Dienst ist verbunden (weitere Instanz von Seite „BLE-Scanner NG“ Nr. 1) | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_server_online | 1 = the service is connected (further instance of page “BLE-Scanner NG” no. 1) | —"),
    ("BAUSTEIN.Z3_07", "Status | Thermometer Wohnzimmer (BLE) | Zeilen: V1 = 0 und V5 < 0 „noch nie gehört – Alias im Plugin prüfen, Thermometer näher an den LoxBerry“; V1 = 0 „seit <v5> s nichts gehört – Werte veraltet; Batterie und Abstand zum LoxBerry prüfen“; V6 = 2 „verschlüsselt – im Plugin den Bind-Key eintragen oder ‚Bind-Key aus der Xiaomi-Cloud holen‘ (Reiter Einstellungen)“; V6 = 3 „der Bind-Key passt nicht – er ändert sich bei jedem neuen Koppeln in Mi Home; im Plugin neu holen“; V6 = 5 „sendet die alte verschlüsselte Form – das Plugin kann sie nicht lesen“; V6 = 4 „in Reichweite, aber seit <v7> s kein Messwert – Werte ungültig; Batterie prüfen“; V4 < 0 „<v2.1> °C, <v3.0> %% rF – Batterie noch nicht gemeldet“; V4 < 20 „<v2.1> °C, <v3.0> %% rF – Batterie schwach (<v4> %%)“; ohne Bedingung „<v2.1> °C, <v3.0> %% rF, Batterie <v4> %%“; Visualisierung EIN | V1 = #1, V2 = #2, V3 = #3, V4 = #4, V5 = #5, V6 = #14, V7 = #15",
     "Status | Thermometer Wohnzimmer (BLE) | Rows: V1 = 0 and V5 < 0 “never heard – check the alias in the plugin, move the thermometer closer to the LoxBerry”; V1 = 0 “nothing heard for <v5> s – values outdated; check battery and distance to the LoxBerry”; V6 = 2 “encrypted – enter the bind key in the plugin or use ‘Get bind key from the Xiaomi cloud’ (tab Settings)”; V6 = 3 “the bind key does not match – it changes with every new pairing in Mi Home; fetch it again in the plugin”; V6 = 5 “sends the old encrypted form – the plugin cannot read it”; V6 = 4 “in range, but no reading for <v7> s – values invalid; check the battery”; V4 < 0 “<v2.1> °C, <v3.0> %% RH – battery not yet reported”; V4 < 20 “<v2.1> °C, <v3.0> %% RH – battery weak (<v4> %%)”; without condition “<v2.1> °C, <v3.0> %% RH, battery <v4> %%”; visualisation ON | V1 = #1, V2 = #2, V3 = #3, V4 = #4, V5 = #5, V6 = #14, V7 = #15"),
    ("BAUSTEIN.Z3_08", "Formel | Batterie Thermometer schwach (BLE) | IF(I1>0;IF(I1<20;1;0);0) – unter 20 Prozent; -1 (noch nicht gemeldet) zählt nicht | I1 = #4",
     "Formula | Batterie Thermometer schwach (BLE) | IF(I1>0;IF(I1<20;1;0);0) – below 20 percent; -1 (not yet reported) does not count | I1 = #4"),
    ("BAUSTEIN.Z3_09", "Einschaltverzögerung | Batterie Thermometer schwach bestätigt (BLE) | 600 s | Eingang = #8",
     "Switch-On Delay | Batterie Thermometer schwach bestätigt (BLE) | 600 s | Input = #8"),
    ("BAUSTEIN.Z3_10", "Benachrichtigung | Meldung Batterie Thermometer schwach (BLE) | Text: BLE-Scanner NG – die Batterie des Thermometers im Wohnzimmer ist unter 20 Prozent. Batterie tauschen, bevor die Werte ausbleiben | Eingang = #9",
     "Notification | Meldung Batterie Thermometer schwach (BLE) | Text: BLE-Scanner NG – the battery of the thermometer in the living room is below 20 percent. Replace the battery before the values stop | Input = #9"),
    ("BAUSTEIN.Z3_11", "UND | Thermometer verstummt (BLE) | — (I1 negiert: in Config auf den Eingangspunkt klicken, es erscheint ein kleiner Kreis) nur bei laufendem Dienst – ein Ausfall des Scanners meldet schon „Meldung Plugin gestört (BLE)“ | I1 = #1 (negiert), I2 = #6",
     "AND | Thermometer verstummt (BLE) | — (I1 inverted: in Config click the input point, afterwards the input shows a small circle) only while the service is running – a failure of the scanner already reports “Meldung Plugin gestört (BLE)” | I1 = #1 (inverted), I2 = #6"),
    ("BAUSTEIN.Z3_12", "Einschaltverzögerung | Thermometer verstummt bestätigt (BLE) | 1800 s (das Thermometer sendet alle paar Sekunden eine Werbung, Messwerte bei sparsamen Fühlern nur alle 10 Minuten; eine halbe Stunde fängt Funklöcher ab; „veraltet“ (Nr. 14 = 4) entsteht erst nach der Frist im Plugin, die Meldung kommt dann nach etwa einer Stunde) | Eingang = #17",
     "On-Delay | Thermometer verstummt bestätigt (BLE) | 1800 s (the thermometer advertises every few seconds, economical sensors send readings only every 10 minutes; half an hour bridges radio gaps; “outdated” (no. 14 = 4) arises only after the deadline in the plugin, the message then comes after about one hour) | Input = #17"),
    ("BAUSTEIN.Z3_13", "Benachrichtigung | Meldung Thermometer verstummt (BLE) | Text: BLE-Scanner NG – vom Thermometer im Wohnzimmer kommen seit 30 Minuten keine gültigen Messwerte mehr (außer Reichweite, Batterie leer oder Bind-Key fehlt bzw. passt nicht); Temperatur und Feuchte sind veraltet. In der App den Status „Thermometer Wohnzimmer (BLE)“ lesen, im Plugin Reiter Test die Lage des Thermometers | Eingang = #12",
     "Notification | Meldung Thermometer verstummt (BLE) | Text: BLE-Scanner NG – no valid readings from the thermometer in the living room for 30 minutes (out of range, battery empty or bind key missing or wrong); temperature and humidity are outdated. Read the status “Thermometer Wohnzimmer (BLE)” in the app, in the plugin tab Test the state of the thermometer | Input = #12"),
    ("BAUSTEIN.SEITE1_SCHRITT1", "Im Plugin Reiter „Einstellungen“ → „Geräte suchen“, die Schlüsselanhänger anhaken (nur Geräte mit fester Adresse – Telefone wechseln ihre Adresse; dafür gibt es die Tag-Art IRK), speichern. Je Tag die Zusatzangaben setzen: „Alias“ (z. B. schluessel1 – dann bleibt der Name in Loxone gleich, wenn der Anhänger getauscht wird) und „Person“ (z. B. Person1; mehrere Anhänger einer Person bekommen denselben Namen). Speichern.",
     "In the plugin tab “Settings” → “Search for devices”, tick the key fobs (only devices with a fixed address – phones change their address; for them there is the tag type IRK), save. Set the additional settings per tag: “Alias” (e.g. schluessel1 – then the name in Loxone stays the same when the fob is replaced) and “Person” (e.g. Person1; several fobs of one person get the same name). Save."),
    ("BAUSTEIN.SEITE1_SCHRITT2", "Reiter „MQTT“: „Zustände per MQTT veröffentlichen“ ist ab Werk an. Gateway V1: das Abo blescanner/# trägt das Plugin selbst ein. Gateway V2: unter System → MQTT Gateway → Subscriptions die Themen der Namenstabelle (oben) anhaken, server/ok zusätzlich „Noncached“.",
     "Tab “MQTT”: “Publish states via MQTT” is on by default. Gateway V1: the plugin enters the subscription blescanner/# itself. Gateway V2: under System → MQTT Gateway → Subscriptions tick the topics of the name table (above), server/ok additionally “Noncached”."),
    ("BAUSTEIN.SEITE1_SCHRITT3", "In Loxone Config je Eingang der Liste einen Virtuellen Eingang anlegen (Peripherie → Virtuelle Eingänge), Name genau wie in der Spalte „Name“ (bzw. der Namenstabelle oben), „Als Digitaleingang“ NICHT anhaken; Texte als Virtueller Texteingang. Der LoxBerry-Benutzer braucht im Miniserver Rechte. Eine Vorlage mit Virtuellen HTTP-Eingängen gibt es nicht mehr.",
     "In Loxone Config create one Virtual Input per input of the list (Periphery → Virtual Inputs), name exactly as in the column “Name” (or the name table above), do NOT tick “Use as digital input”; texts as Virtual Text Input. The LoxBerry user needs rights in the Miniserver. There is no template with Virtual HTTP Inputs any more."),
    ("BAUSTEIN.SEITE1_SCHRITT4", "Seite „BLE-Scanner NG“ anlegen, die 7 Eingänge der Liste ziehen (Nr. 1–5, 15, 16), dazu die Konstante 1 (Nr. 6).",
     "Create the page “BLE-Scanner NG”, drag the 7 inputs of the list (no. 1–5, 15, 16), plus the constant 1 (no. 6)."),
    ("BAUSTEIN.SEITE1_SCHRITT5", "Zwei Benachrichtigungen anlegen (Peripherie → Mitteilungen → Benachrichtigung): „Meldung Plugin gestört (BLE)“ und „Meldung Alle gegangen (BLE)“, Texte wie in der Tabelle.",
     "Create two notifications (Periphery → Messages → Notification): “Meldung Plugin gestört (BLE)” and “Meldung Alle gegangen (BLE)”, texts as in the table."),
    ("BAUSTEIN.SEITE1_SCHRITT6", "Übrige Bausteine über die Baustein-Suche (F5), Parameter wie in der Tabelle, von oben nach unten verbinden. Analogwertvalidierung Nr. 7: Haken bei ‚En‘ im Eigenschaftsfenster entfernen (Config legt En negiert an; sonst kommt die Konstante 1 als 0 an). Formeln Nr. 17/18 wie angegeben (statt UND: -1 = keine Aussage zählt nicht als „da“). UND Nr. 22: beide Eingänge negieren – auf den Eingangspunkt klicken, danach zeigt der Eingang einen kleinen Kreis. Status „Zustand (BLE)“: vorher einmal „+“ (V5). Statuszeilen in der angegebenen Reihenfolge, die ohne Bedingung zuletzt.",
     "Add the remaining blocks via the block search (F5), parameters as in the table, connect from top to bottom. Value Validator no. 7: remove the tick at ‘En’ in the properties window (Config creates En negated; otherwise the constant 1 arrives as 0). Formulas no. 17/18 as given (instead of AND: -1 = no statement does not count as “present”). AND no. 22: negate both inputs – click the input point, the input then shows a small circle. Status “Zustand (BLE)”: press “+” once beforehand (V5). Status rows in the given order, the one without condition last."),
    ("BAUSTEIN.SEITE1_SCHRITT7", "Speichern und übertragen. Probe: „Zustand (BLE)“ zeigt „läuft – … Tags in Reichweite“; einen Anhänger aus dem Haus tragen – nach „Abwesend nach“ (30 s) und 2 Minuten zeigt „Anwesenheit (BLE)“ die andere Person bzw. „niemand zu Hause“.",
     "Save and transfer. Check: “Zustand (BLE)” shows “running – … tags in range”; carry a fob out of the house – after “Absent after” (30 s) and 2 minutes “Anwesenheit (BLE)” shows the other person or “nobody at home”."),
    ("BAUSTEIN.SEITE1_H1", "<b>Zu Nr. 7:</b> Virtuelle Eingänge behalten ihren letzten Wert; nur das stehende Lebenszeichen verrät einen hängenden Dienst. Kommt innerhalb Tmc kein neuer Wert, meldet die Analogwertvalidierung an ihrem Ausgang E – den Haken bei ‚En‘ im Eigenschaftsfenster entfernen.",
     "<b>On no. 7:</b> virtual inputs keep their last value; only the standing sign of life reveals a hanging service. If no new value arrives within Tmc, the Value Validator reports at its output E – remove the tick at ‘En’ in the properties window."),
    ("BAUSTEIN.SEITE1_H2", "<b>Zu Nr. 9 und 17:</b> blescanner_server_online ist der Letzte Wille; blescanner_server_ok taugt nicht dafür, es kommt nach einem harten Absturz nicht mehr.",
     "<b>On no. 9 and 17:</b> blescanner_server_online is the last will; blescanner_server_ok is not suitable for that, it no longer arrives after a hard crash."),
    ("BAUSTEIN.SEITE1_H3", "<b>Zu Nr. 15 bis 18:</b> anwesend_gesamt kommt immer – ohne WLAN-Kopplung ist es die BLE-Anwesenheit (-1 = keine Aussage). Wer die Kopplung später einschaltet, muss nichts umverdrahten.",
     "<b>On no. 15 to 18:</b> anwesend_gesamt always arrives – without the WiFi coupling it is the BLE presence (-1 = no statement). Switching the coupling on later needs no rewiring."),
    ("BAUSTEIN.SEITE1_H4", "<b>Zu Nr. 19 und 20:</b> die Verzögerung kommt zur Einstellung „Abwesend nach“ im Plugin hinzu; beide zusammen ergeben die Gesamtzeit.",
     "<b>On no. 19 and 20:</b> the delay adds to the setting “Absent after” in the plugin; together they make up the total time."),
    ("BAUSTEIN.SEITE1_H5", "<b>Zu Nr. 21 und 22:</b> „Jemand zu Hause (BLE)“ und „Niemand zu Hause (BLE)“ sind die fertigen Schaltsignale. Im eigenen Projekt ersetzen sie die Platzhalter „Anwesenheit (eigene Quelle)“ und „Niemand zu Hause (eigene Quelle)“: deren Abnehmer an Nr. 21 bzw. 22 legen, Platzhalter löschen. Bei einer Störung bleibt Nr. 22 auf 0 – eine tote Erkennung darf keine Abwesenheitslogik auslösen.",
     "<b>On no. 21 and 22:</b> “Jemand zu Hause (BLE)” and “Niemand zu Hause (BLE)” are the finished switching signals. In your own project they replace the placeholders “Anwesenheit (eigene Quelle)” and “Niemand zu Hause (eigene Quelle)”: connect their consumers to no. 21 or 22, delete the placeholders. During a fault no. 22 stays at 0 – a dead detection must not trigger absence logic."),
    ("BAUSTEIN.SEITE1_H6", "Eine dritte Person: Eingang anwesend_gesamt, Formel wie Nr. 17, Ausschaltverzögerung wie Nr. 19, dann über ein weiteres ODER (je zwei Eingänge) zu Nr. 21.",
     "A third person: input anwesend_gesamt, formula as no. 17, off delay as no. 19, then via a further OR (two inputs each) to no. 21."),
    ("BAUSTEIN.SEITE1_H7", "Andere Plugins lesen die Anwesenheit nicht aus diesen Eingängen, sondern aus haus/anwesenheit/… (Reiter Einstellungen „Anwesenheit für andere Plugins bereitstellen“, ab Werk aus).",
     "Other plugins do not read the presence from these inputs but from haus/anwesenheit/… (tab Settings “Provide presence for other plugins”, off by default)."),
    ("BAUSTEIN.SEITE1_H8", "Die Meldungen kommen frühestens nach 10 Minuten Störung; „Meldung Alle gegangen (BLE)“ einmal je Weggang (und nach jedem Übertragen erneut, solange niemand da ist).",
     "The notifications come after 10 minutes of fault at the earliest; “Meldung Alle gegangen (BLE)” once per departure (and again after every transfer while nobody is there)."),
    ("BAUSTEIN.SEITE2_SCHRITT1", "Für die Entfernung im Plugin „Entfernung schätzen und veröffentlichen“ einschalten und den Anhänger einmal in 1 m Abstand kalibrieren (Nr. 18 oder Reiter Test „Auf 1 m kalibrieren“), den Wert am Tag als „ref“ eintragen; für die Batterie „Batteriestand über eine Verbindung lesen“ und am Tag „Batterie lesen“. Ohne das bleiben Nr. 5 und Nr. 6 auf -1 – die Seite funktioniert trotzdem.",
     "For the distance switch on “Estimate and publish distance” in the plugin and calibrate the fob once at 1 m (no. 18 or tab Test “Calibrate at 1 m”), enter the value on the tag as “ref”; for the battery “Read battery level via a connection” and “Read battery” on the tag. Without that no. 5 and no. 6 stay at -1 – the page works anyway."),
    ("BAUSTEIN.SEITE2_SCHRITT2", "Neue Seite, die Virtuellen Eingänge Nr. 1–6, 11 und 22 anlegen und ziehen (Name genau wie in der Tabelle); drei Virtuelle Texteingänge (Nr. 12, 14, 15), „In Visualisierung verwenden“ an.",
     "New page, create and drag the Virtual Inputs no. 1–6, 11 and 22 (name exactly as in the table); three Virtual Text Inputs (no. 12, 14, 15), “Use in visualisation” on."),
    ("BAUSTEIN.SEITE2_SCHRITT3", "Drei Tasten (Nr. 16, 18, 20) als Virtueller Eingang mit Eingangsart Taster; drei Befehle (Nr. 17, 19, 21) am gemeinsamen Ausgang „LoxBerry MQTT-Gateway“ – oder die Vorlage „MQTT-Befehle“ (grauer Knopf oben) importieren. Im Plugin „Befehle über MQTT annehmen“ einschalten, für den Batterielauf zusätzlich „Eingreifende Befehle über MQTT annehmen“.",
     "Three push buttons (no. 16, 18, 20) as Virtual Input with input type push button; three commands (no. 17, 19, 21) at the common output “LoxBerry MQTT-Gateway” – or import the template “MQTT commands” (grey button above). In the plugin switch on “Accept commands via MQTT”, for the battery run additionally “Accept intervening commands via MQTT”."),
    ("BAUSTEIN.SEITE2_SCHRITT4", "Benachrichtigung „Meldung Batterie Schlüssel 1 schwach (BLE)“ anlegen.",
     "Create the notification “Meldung Batterie Schlüssel 1 schwach (BLE)”."),
    ("BAUSTEIN.SEITE2_SCHRITT5", "Übrige Bausteine über F5. „+“: „Schlüssel 1 (BLE)“ zweimal (V5, V6).",
     "Remaining blocks via F5. “+”: “Schlüssel 1 (BLE)” twice (V5, V6)."),
    ("BAUSTEIN.SEITE2_H1", "Nr. 11 bis 13: mit dem Plugin WiFi-Scanner NG und eingeschalteter Kopplung (Reiter Einstellungen, Zuordnung „Beispiel=Person1“) zählt auch das Telefon; ohne Kopplung zeigen sie die BLE-Anwesenheit (Quelle „ble“).",
     "No. 11 to 13: with the plugin WiFi-Scanner NG and the coupling switched on (tab Settings, assignment “Beispiel=Person1”) the phone counts too; without coupling they show the BLE presence (source “ble”)."),
    ("BAUSTEIN.SEITE2_H2", "Nr. 15 nur mit mehreren LoxBerry-Scannern im Haus („Raumzuordnung aus mehreren Scannern bilden“); sonst weglassen.",
     "No. 15 only with several LoxBerry scanners in the house (“Build room assignment from several scanners”); otherwise leave it out."),
    ("BAUSTEIN.SEITE2_H3", "Nr. 17, 19, 21: jeder im Heimnetz kann über den UDP-Eingang des MQTT-Gateways Befehle senden – deshalb sind beide Haken im Plugin ab Werk aus. Die Quittung steht unter blescanner/befehl/&lt;Name&gt;/quittung; Nr. 22 zeigt das Ergebnis der Kalibrierung.",
     "No. 17, 19, 21: anyone in the home network can send commands via the UDP input of the MQTT gateway – that is why both ticks in the plugin are off by default. The acknowledgement is under blescanner/befehl/&lt;name&gt;/quittung; no. 22 shows the result of the calibration."),
    ("BAUSTEIN.SEITE3_SCHRITT1", "Im Plugin das Thermometer anhaken, Alias „thermometer_wohnzimmer“ (ohne „Person“ – sonst gilt es als Mensch); „Werbedaten dekodieren“ ist ab Werk an. Erst wenn es Werte gesendet hat (Reiter Einstellungen zeigt sie), stehen die Messwerte in der Namenstabelle.",
     "In the plugin tick the thermometer, alias “thermometer_wohnzimmer” (without “Person” – otherwise it counts as a human); “Decode advertising data” is on by default. Only once it has sent values (tab Settings shows them) do the measured values appear in the name table."),
    ("BAUSTEIN.SEITE3_SCHRITT2", "Neue Seite, die 7 Virtuellen Eingänge anlegen und ziehen (mit sensor_lage und sensor_alter), dazu blescanner_server_online ein weiteres Mal; „Statistik“ an Temperatur und Feuchte einschalten.",
     "New page, create and drag the 7 Virtual Inputs (with sensor_lage and sensor_alter), plus blescanner_server_online once more; switch on “Statistics” at temperature and humidity."),
    ("BAUSTEIN.SEITE3_SCHRITT3", "Zwei Benachrichtigungen anlegen: „Meldung Batterie Thermometer schwach (BLE)“, „Meldung Thermometer verstummt (BLE)“.",
     "Create two notifications: “Meldung Batterie Thermometer schwach (BLE)”, “Meldung Thermometer verstummt (BLE)”."),
    ("BAUSTEIN.SEITE3_SCHRITT4", "Übrige Bausteine über F5. UND Nr. 11: Eingang I1 negieren – auf den Eingangspunkt klicken, danach zeigt der Eingang einen kleinen Kreis. ODER Nr. 17 mit genau zwei Eingängen. „+“: Status dreimal (V5 bis V7).",
     "Remaining blocks via F5. AND no. 11: negate input I1 – click the input point, the input then shows a small circle. OR no. 17 with exactly two inputs. “+”: status three times (V5 to V7)."),
    ("BAUSTEIN.SEITE3_SCHRITT5", "Speichern und übertragen. Probe: Temperatur in „Thermometer Wohnzimmer (BLE)“ mit der Anzeige am Thermometer vergleichen.",
     "Save and transfer. Check: compare the temperature in “Thermometer Wohnzimmer (BLE)” with the display on the thermometer."),
    ("BAUSTEIN.SEITE3_H1", "Das Thermometer zählt im Plugin als Tag: „&lt;v4&gt; von &lt;v5&gt; Tags in Reichweite“ auf Seite „BLE-Scanner NG“ schließt es ein; die Anwesenheit (Personen) nicht.",
     "The thermometer counts as a tag in the plugin: “&lt;v4&gt; of &lt;v5&gt; tags in range” on page “BLE-Scanner NG” includes it; the presence (persons) does not."),
    ("BAUSTEIN.SEITE3_H2", "Andere Fühler (ATC/pvvx, RuuviTag, Eddystone, Qingping, BTHome v2) liefern teils Luftdruck, Batteriespannung oder Helligkeit – gleiche Bauart, Eingang …_sensor_druck usw. Verschlüsselnde Xiaomi-Fühler brauchen den Bind-Key im Plugin (Reiter Einstellungen).",
     "Other sensors (ATC/pvvx, RuuviTag, Eddystone, Qingping, BTHome v2) partly deliver air pressure, battery voltage or illuminance – same design, input …_sensor_druck etc. Encrypting Xiaomi sensors need the bind key in the plugin (tab Settings)."),
    ("BAUSTEIN.SEITE3_H3", "Weitere Räume: je Thermometer dieselben Bausteine mit seinem Alias.",
     "Further rooms: the same blocks per thermometer with its alias."),

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
    ("PRUEF.VORLAGE", "Ist die Vorlage MQTT-Befehle wohlgeformt?",
     "Is the template MQTT commands well-formed?"),
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
    ("TEST.ZEITGRENZE_HART",
     "[Zeitgrenze] Der Befehl reagierte nach der Wartezeit nicht auf SIGTERM und "
     "wurde hart beendet (SIGKILL). BlueZ oder D-Bus hängen — prüfen mit: "
     "systemctl status bluetooth",
     "[Timeout] The command did not react to SIGTERM after the waiting time and was "
     "killed (SIGKILL). BlueZ or D-Bus are hanging — check with: "
     "systemctl status bluetooth"),
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
    ("TEST.TESTMODUS_LAEUFT", "Der Testmodus für %s läuft 60 Sekunden. Die Einzelmessungen erscheinen im Reiter Test unter ‚Testmodus‘ und erneuern sich von selbst.",
     "The test mode for %s runs for 60 seconds. The single measurements appear in the tab Test under ‘Test mode’ and refresh themselves."),
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
    ("TEST.STEUER_OHNE_DIENST",
     "Der Dienst läuft nicht — der Auftrag wurde nicht abgelegt. Erst den Dienst "
     "starten, dann erneut drücken. (Ein Auftrag gilt 60 Sekunden; ein älterer wird "
     "beim Start verworfen.)",
     "The service is not running — the request was not stored. Start the service "
     "first, then press again. (A request is valid for 60 seconds; an older one is "
     "discarded at start.)"),
    ("TEST.JETZT_PID", "Der Dienst läuft jetzt (PID %d).",
     "The service is now running (PID %d)."),
    ("TEST.START_FEHLGESCHLAGEN",
     "Der Dienst läuft nicht. Protokoll im Reiter Logdateien prüfen.",
     "The service is not running. Check the log in the Log files tab."),
    ("TEST.STOP_LAEUFT_NOCH",
     "Es läuft noch etwas — bitte Protokoll prüfen.",
     "Something is still running — please check the log."),
    ("TEST.STOP_OK", "Angehalten. Der Dienst bleibt über Neustart und Update angehalten, bis ‚Dienst starten‘ gedrückt wird.",
     "Stopped. The service stays stopped across reboots and updates until ‘Start service’ is pressed."),

    # ---------------- Themen
    ("THEMA.PRESENT", "Tag in Reichweite - gilt nur, solange server/online 1 ist",
     "Tag in range - only valid while server/online is 1"),
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
    ("THEMA.BATTERY", "Batteriestand in Prozent (-1 = noch nie gelesen oder nicht lesbar)",
     "Battery level in percent (-1 = never read or not readable)"),
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
    ("THEMA.SRV_TS", "Herzschlag: Zeitstempel, höchstens alle 30 s",
     "Heartbeat: timestamp, at most every 30 s"),
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

    # ---------------- NACHGEPFLEGT 31.08.2026
    # Diese 18 Schluessel standen in der ausgelieferten .ini und im
    # PHP, aber nicht in dieser Tabelle - ein Lauf haette sie
    # geloescht. Sie konnten hier nicht stehen, solange pruefe()
    # jede Auszeichnung pauschal verbot; siehe dort.
    ('TEXT.ABO_GEMESSEN', '(gemessen: Gateway&nbsp;V%d)',
     '(measured: gateway&nbsp;V%d)'),
    ("TEXT.ABO_UNBEKANNT", "Welche Fassung Ihr MQTT&#8209;Gateway hat, ließ sich nicht feststellen. <b>Fassung&nbsp;1:</b> das Plugin trägt das Abo selbst in seine Abo-Datei ein, die das Gateway liest. <b>Fassung&nbsp;2 und neuer:</b> die Themengruppe erscheint von selbst in den Subscriptions, einzutragen ist nichts.",
     "The version of your MQTT gateway could not be determined. <b>Version&nbsp;1:</b> the plugin enters the subscription itself in its subscription file, which the gateway reads. <b>Version&nbsp;2 and newer:</b> the topic group appears by itself under Subscriptions, nothing needs to be entered."),
    ('TEXT.ABO_V2', '<b>MQTT&#8209;Gateway V2 erkennt die Themengruppe von selbst</b> — einzutragen ist hier nichts. In den <i>Subscriptions</i> erscheint die Gruppe; dort werden die gewünschten Datenpunkte einzeln angehakt. Erscheint sie nicht, hat noch nichts veröffentlicht.',
     '<b>MQTT gateway V2 detects the topic group by itself</b> — nothing needs to be entered here. The group appears under <i>Subscriptions</i>; tick the data points you want there. If it does not appear, nothing has been published yet.'),
    ('TEXT.H_SICHERUNG', 'Einstellungen sichern und zurückspielen',
     'Back up and restore settings'),
    ('TEXT.K_SICHERN', 'Einstellungen sichern',
     'Back up settings'),
    ('TEXT.K_ZURUECK', 'Zurückspielen',
     'Restore'),
    ('TEXT.SICH_ABGELEHNT', 'Die Datei wurde <b>nicht</b> übernommen — es ist nichts geändert worden:',
     'The file was <b>not</b> accepted — nothing has been changed:'),
    ("TEXT.SICH_ERKLAERUNG", "Für den <b>Umzug auf einen zweiten LoxBerry</b>: die Datei enthält alle Einstellungen dieses Plugins, alle eingetragenen Tags und die hinterlegten Schlüssel (Bind-Keys, IRK) und lässt sich dort wieder einspielen. Zurückgespielt wird nur eine vollständige, gültige Datei; eine Sicherung ohne Schlüssel-Abschnitte lässt die hinterlegten Schlüssel stehen. Danach wird der Dienst neu gestartet, wenn er lief.",
     "For <b>moving to a second LoxBerry</b>: the file contains all settings of this plugin, all registered tags and the stored keys (bind keys, IRK) and can be restored there. Only a complete, valid file is restored; a backup without key sections leaves the stored keys in place. Afterwards the service is restarted if it was running."),
    ('TEXT.SICH_FREMD', 'Unbekannte Einstellung in der Datei: %s',
     'Unknown setting in the file: %s'),
    ('TEXT.SICH_KEINE_DATEI', 'Es wurde keine Datei ausgewählt oder der Upload ist fehlgeschlagen.',
     'No file was selected, or the upload failed.'),
    ('TEXT.SICH_KEIN_JSON', 'Die Datei ist keine gültige Sicherung dieses Plugins.',
     'The file is not a valid backup of this plugin.'),
    ('TEXT.SICH_LEER', 'Die Datei enthält keine bekannte Einstellung.',
     'The file contains no known setting.'),
    ('TEXT.SICH_SCHREIBFEHLER', 'Die Einstellungen ließen sich nicht schreiben.',
     'The settings could not be written.'),
    ("TEXT.SICH_UEBERNOMMEN", "Einstellungen zurückgespielt: %d Werte und %d Tags übernommen.",
     "Settings restored: %d values and %d tags taken over."),
    ("TEXT.SICH_WARNUNG", "<b>Die Datei ist eine Anwesenheitsliste und trägt Schlüssel.</b> Sie enthält die MAC-Adressen der Tags, die Namen der Personen, die sie tragen, die Bind-Keys der Xiaomi-Thermometer und die IRK der Telefone. Behandeln Sie die Datei wie ein Passwort: nicht in ein Forum hängen und nicht an einen Fehlerbericht heften.",
     "<b>The file is a presence list and carries keys.</b> It contains the MAC addresses of the tags, the names of the people carrying them, the bind keys of the Xiaomi thermometers and the IRK of the phones. Treat the file like a password: do not post it in a forum and do not attach it to a bug report."),
    ('TEXT.SICH_ZU_GROSS', 'Die Datei ist größer als erlaubt — eine Sicherung dieses Plugins ist wenige Kilobyte groß.',
     'The file is larger than allowed — a backup of this plugin is a few kilobytes.'),
    ('WACHE.FALSCH', 'Das Formularmerkmal war ungültig - vermutlich ist die Sitzung abgelaufen. Bitte die Seite neu laden.',
     'The form token was invalid - the session has probably expired. Please reload the page.'),
    ('WACHE.FEHLT', 'Die Anfrage trug kein Formularmerkmal und wurde abgewiesen. Bitte die Seite neu laden und den Vorgang wiederholen.',
     'The request carried no form token and was rejected. Please reload the page and try again.'),
    # ---- Nachgetragen 20.09.2026 aus den ausgelieferten .ini ------------------
    # Diese Schluessel standen nur dort; der Erzeuger wies deshalb jeden Lauf ab.
    # Neue Werte in doppelten Anfuehrungszeichen: sie enthalten Apostrophe.
    ("PRUEF.FORMATE", "Passt die Formattabelle zu den Dekodern?",
     "Does the format table match the decoders?"),
    ("PRUEF.GRENZEN", "Stimmen die Messwertgrenzen mit dem Dekoder überein?",
     "Do the measurement limits match the decoder?"),
    ("TEST.FORMATE_ANDERS", "Formattabelle weicht ab: %s",
     "Format table differs: %s"),
    ("TEST.FORMATE_OK", "%d Beaconformat(e), Tabelle und Dekoder gleich",
     "%d beacon format(s), table and decoders identical"),
    ("TEST.FORMATE_UNLESBAR", "FORMAT_GROESSEN in bin/bl_beacon.py ist nicht lesbar — der Vergleich fand nicht statt.",
     "FORMAT_GROESSEN in bin/bl_beacon.py could not be read - the comparison did not happen."),
    ("TEST.GRENZEN_ANDERS", "Grenzen weichen ab: %s",
     "Limits differ: %s"),
    ("TEST.GRENZEN_OK", "%d Messwert(e), Grenzen in PHP und Python gleich",
     "%d measurement(s), limits identical in PHP and Python"),
    ("TEST.GRENZEN_UNLESBAR", "GRENZEN in bin/bl_beacon.py ist nicht lesbar — der Vergleich fand nicht statt.",
     "GRENZEN in bin/bl_beacon.py could not be read - the comparison did not happen."),
    ("TEST.THEMA_OHNE_EINTRAG", "wird gesendet und gilt als bedingt, hat aber nirgends einen Eintrag — die Loxone-Vorlage kann es nie führen: %s",
     "is published and counts as conditional, but has no entry anywhere - the Loxone template can never carry it: %s"),
    ("TEXT.LOX_MESSWERTE_HINWEIS", "Die heruntergeladene Vorlage führt diese Eingänge nur für Tags, die schon einmal Messwerte gesendet haben — ein Schlüsselanhänger bekäme sonst Eingänge, die dauerhaft auf 0 stehen. Erscheint ein Wert nicht: den Tag einmal senden lassen (der Reiter Einstellungen zeigt die zuletzt gesehenen Werte) und die Vorlage danach neu herunterladen. Messwerte gehen flüchtig hinaus, nicht zurückbehalten: nach einem Neustart des Miniservers steht der Eingang auf 0, bis der Sensor das nächste Mal sendet.",
     "The downloaded template carries these inputs only for tags that have already sent measurements - a key fob would otherwise get inputs permanently stuck at 0. If a value is missing: let the tag send once (the Settings tab shows the most recent values) and download the template again. Measurements are published non-retained: after a Miniserver restart the input reads 0 until the sensor sends again."),
    ("TEXT.LOX_MESSWERTE_TEXT", "Sendet ein Tag Messwerte in seinen Werbedaten, veröffentlicht das Plugin sie unter <Präfix>/<Tag>/sensor/<Name>. Für Anzeige, Statistik oder Regelung genügt ein virtueller Eingang; die Seite ergänzt Batterie- und Ausfallmeldungen. Gelesen werden die Werte ohne Verbindung und ohne Kopplung, allein aus dem Funkspruch: ein Xiaomi-Thermometer MJ_HT_V1 (LYWSDCGQ/01ZM) liefert damit Temperatur und Luftfeuchte je Raum, ohne WLAN und ohne Cloud.",
     "If a tag sends measurements in its advertising data, the plugin publishes them under <prefix>/<tag>/sensor/<name>. For display, statistics or control a virtual input is enough; the page adds battery and failure messages. The values are read without a connection and without pairing, from the broadcast alone: a Xiaomi thermometer MJ_HT_V1 (LYWSDCGQ/01ZM) thereby delivers temperature and humidity per room, without WiFi and without cloud."),
    ("THEMA.S_BATTERIE", "Batteriestand des Sensors in Prozent, aus den Werbedaten",
     "Sensor battery level in percent, from advertising data"),
    ("THEMA.S_BATTERIE_MV", "Batteriespannung des Sensors in Millivolt, aus den Werbedaten",
     "Sensor battery voltage in millivolts, from advertising data"),
    ("THEMA.S_BEWEGUNG", "Bewegungszähler des Sensors, aus den Werbedaten",
     "Sensor movement counter, from advertising data"),
    ("THEMA.S_DRUCK", "Luftdruck in Hektopascal, aus den Werbedaten",
     "Air pressure in hectopascal, from advertising data"),
    ("THEMA.S_FEUCHTE", "Relative Luftfeuchte in Prozent, aus den Werbedaten",
     "Relative humidity in percent, from advertising data"),
    ("THEMA.S_FOLGE", "Folgenummer des Funkspruchs — steigt je Paket, zeigt Ausfälle",
     "Packet sequence number - increments per packet, reveals gaps"),
    ("THEMA.S_LAUFZEIT_S", "Betriebszeit des Sensors in Sekunden, aus den Werbedaten",
     "Sensor uptime in seconds, from advertising data"),
    ("THEMA.S_PAKETE", "Anzahl gesendeter Werbepakete, aus den Werbedaten",
     "Number of advertising packets sent, from advertising data"),
    ("THEMA.S_TEMPERATUR", "Temperatur in Grad Celsius, aus den Werbedaten",
     "Temperature in degrees Celsius, from advertising data"),

    # ---------------- nachgezogen 30.09.2026 aus dem Bau 1.3.20 (Durchgang)
    ("MANGEL.ANFUEHRUNG", "%s: %s enthält ein Anführungs- oder Steuerzeichen und wurde nicht übernommen. Es bleibt bei %s.",
     "%s: %s contains a quotation mark or control character and was not applied. %s is kept."),
    ("MANGEL.KENNUNG_BLEIBT", "%s ist weder eine Bluetooth-Adresse noch eine iBeacon-Kennung. Es bleibt bei %s, samt Bezeichnung und Zusatzangaben.",
     "%s is neither a Bluetooth address nor an iBeacon identifier. %s is kept, including its name and options."),
    ("MANGEL.KENNUNG_LEER", "%s: das Adressfeld ist leer. Der Tag bleibt eingetragen; entfernt wird er mit dem Haken Entfernen.",
     "%s: the address field is empty. The tag stays registered; it is removed with the Remove tick."),
    ("MANGEL.SCHWELLEN_VERTAUSCHT", "Die Schwelle mittel (%s) liegt über nah (%s). Beide bleiben bei ihren bisherigen Werten (nah %s, mittel %s).",
     "The medium threshold (%s) is above near (%s). Both keep their previous values (near %s, medium %s)."),
    ("PRUEF.ABO_DATEI", "Führt die Abo-Datei des MQTT-Gateways das Präfix?",
     "Does the MQTT gateway subscription file carry the prefix?"),
    ("PRUEF.ABO_DATEI_NEIN", "nicht auf dem eingestellten Präfix - der Dienst schreibt sie beim nächsten Start, Speichern im Reiter MQTT sofort",
     "not on the configured prefix - the service writes it on its next start, saving in the MQTT tab at once"),
    ("PRUEF.AKTIV", "Setzt der Server sm-active?",
     "Does the server set sm-active?"),
    ("PRUEF.AKTIV_ZAHLEN", "%d von %d Stellen (Leiste und Bereiche) setzen es serverseitig",
     "%d of %d places (bar and sections) set it on the server"),
    ("PRUEF.DIENST_ANGEHALTEN", "- im Reiter Einstellungen angehalten",
     "- stopped in the Settings tab"),
    ("PRUEF.KONFIG_FEHLT", "fehlt: %s - es gelten die Vorgaben",
     "missing: %s - the defaults apply"),
    ("PRUEF.KONFIG_HEIL", "ja, %d von %d Schlüsseln",
     "yes, %d of %d keys"),
    ("PRUEF.KONFIG_HEIL_FRAGE", "Ist die Konfiguration heil?",
     "Is the configuration intact?"),
    ("PRUEF.KONFIG_KAPUTT", "kaputt: %d Byte, aber ohne [CONFIG], ohne Zeile schluessel=wert oder ohne Zeilenende am Schluss - vermutlich abgeschnitten",
     "broken: %d bytes, but without [CONFIG], without a key=value line or without a final line break - probably truncated"),
    ("PRUEF.KONFIG_LEER", "leer: %s",
     "empty: %s"),
    ("PRUEF.KONFIG_UNVOLLSTAENDIG", "unvollständig: %d von %d Schlüsseln, es fehlen: %s (es gilt die Vorgabe; das nächste Speichern ergänzt sie)",
     "incomplete: %d of %d keys, missing: %s (the default applies; the next save adds them)"),
    ("PRUEF.REITER", "Passen Reiterleiste, Bereiche und Positivliste zusammen?",
     "Do tab bar, sections and allow list match?"),
    ("PRUEF.REITER_ABWEICHUNG", "nicht überall: %s",
     "not everywhere: %s"),
    ("PRUEF.REITER_UNLESBAR", "index.php ist nicht lesbar.",
     "index.php is not readable."),
    ("PRUEF.REITER_ZAHLEN", "Positivliste %d, Leiste %d, Bereiche %d",
     "allow list %d, bar %d, sections %d"),
    ("TEST.LAEUFT_SCHON", "Der Dienst läuft bereits (PID %s) - es wurde kein zweiter gestartet.",
     "The service is already running (PID %s) - no second one was started."),
    ("TEXT.ABO_DATEI_FEHLER", "Die Abo-Datei des MQTT-Gateways (%s) ließ sich nicht schreiben.",
     "The MQTT gateway subscription file (%s) could not be written."),
    ("TEXT.KEINE_AUSSAGE_ALT", "keine Aussage (Stand von %s, %d s alt - Grenze %d s)",
     "no statement (state of %s, %d s old - limit %d s)"),
    ("TEXT.KEINE_AUSSAGE_OHNE", "keine Aussage (noch kein Abbild des Dienstes)",
     "no statement (no state file of the service yet)"),
    ("TEXT.KEINE_AUSSAGE_TOT", "keine Aussage (Dienst läuft nicht)",
     "no statement (service not running)"),
    ("TEXT.KEINE_AUSSAGE_TOT_STAND", "keine Aussage (Dienst läuft nicht / Stand von %s)",
     "no statement (service not running / state of %s)"),
    ("TEXT.KEIN_DIENST_ANGEHALTEN", "Der Dienst ist angehalten (Knopf Dienst anhalten). Er bleibt es auch über einen Neustart des LoxBerry und ein Update, bis im Reiter Einstellungen Dienst starten gedrückt wird. Solange zeigt diese Seite keine Anwesenheit.",
     "The service is stopped (Stop service button). It stays stopped across a LoxBerry restart and an update until Start service is pressed in the Settings tab. Meanwhile this page shows no presence."),
    ("TEXT.KEIN_DIENST_SOLL", "Der Dienst läuft nicht, obwohl er laufen soll. Im Reiter Einstellungen Dienst starten drücken; die Ursache steht im Reiter Logdateien (ble_scanner_ng_start.log und ble_scanner_ng.log). Der Wächter versucht es alle fünf Minuten selbst. Bis dahin zeigt diese Seite keine Anwesenheit.",
     "The service is not running although it should. Press Start service in the Settings tab; the cause is in the Log files tab (ble_scanner_ng_start.log and ble_scanner_ng.log). The watchdog tries by itself every five minutes. Until then this page shows no presence."),
    ("TEXT.NICHT_GELUNGEN", "Der Vorgang ist nicht gelungen:",
     "The action did not succeed:"),
    ("TEXT.PRESENT_NUR_MIT_ONLINE", "present gilt nur zusammen mit server/online: stirbt der Dienst, bleibt der letzte Stand retained im Broker stehen, und nur server/online (Letzter Wille) sagt, dass niemand mehr misst. In Loxone deshalb present mit server_online verknüpfen (Reiter Einbindung in Loxone, Baustein #19). Ohne Aussage (Adapter blind oder nichts zu hören) steht present auf -1 und nicht auf 0; nach einem Dienststart bleibt der letzte Stand stehen, bis die Frist des Tags gelaufen ist.",
     "present is only valid together with server/online: if the service dies, the last state stays retained in the broker, and only server/online (last will) says that nobody is measuring any more. In Loxone therefore link present with server_online (tab Integration into Loxone, block #19). Without a statement (adapter blind or nothing to hear) present is -1, not 0; after a service start the last state stays until the tag's period has passed."),
    ("TEXT.PRUEFUNG_BEIM_OEFFNEN", "Die Selbstprüfung läuft, wenn dieser Reiter geöffnet wird - nicht bei jedem Seitenaufruf.",
     "The self-check runs when this tab is opened - not on every page load."),
    ("TEXT.PRUEFUNG_JETZT", "Jetzt prüfen",
     "Check now"),
    ("TEXT.PRUEFUNG_STAND", "Stand der Selbstprüfung von vor %d s.",
     "Self-check result from %d s ago."),
    ("TEXT.SICH_KEIN_KOPF", "Die Datei ist keine Sicherung dieses Plugins: der Kopf _ mit plugin = ble_scanner_ng fehlt.",
     "The file is not a backup of this plugin: the header _ with plugin = ble_scanner_ng is missing."),
    ("TEXT.SICH_KOPF", "Sicherung der Einstellungen des LoxBerry-Plugins BLE-Scanner NG, mit allen Tags (MAC-Adressen und Namen). Enthält die Bind-Keys der Xiaomi-Thermometer und die IRK der Telefone – wie ein Passwort behandeln. Außerdem MAC-Adressen und die Namen der überwachten Personen.",
     "Backup of the settings of the LoxBerry plugin BLE-Scanner NG, with all tags (MAC addresses and names). Contains the bind keys of the Xiaomi thermometers and the IRK of the phones – treat it like a password. Also MAC addresses and the names of the monitored persons."),
    ("TEXT.SICH_OHNE_TAGS", "In der Datei fehlt die Liste der Tags (tags) - sonst löschte das Zurückspielen alle eingetragenen Tags.",
     "The list of tags (tags) is missing from the file - otherwise restoring would delete all registered tags."),
    ("TEXT.SICH_SCHWELLEN", "Die Schwelle mittel liegt in der Datei über nah.",
     "In the file the medium threshold is above near."),
    ("TEXT.SICH_TAG", "Tag Nr. %d in der Datei ist ungültig (Feld %s).",
     "Tag no. %d in the file is invalid (field %s)."),
    ("TEXT.SICH_WERT", "Einstellung %s: der Wert %s passt nicht zu den Regeln des Formulars.",
     "Setting %s: the value %s does not match the rules of the form."),
    ("THEMA.P_LAST_SEEN_TS", "Zeitstempel der letzten Sichtung eines Tags dieser Person; beim Wechsel sofort, sonst höchstens alle 60 s",
     "Timestamp of the last sighting of a tag of this person; on a change at once, otherwise at most every 60 s"),
    ("THEMA.P_PRESENT", "Person anwesend: ODER über ihre aktiven Tags",
     "Person present: OR over her active tags"),
    ("THEMA.SC_PRESENT", "Tag in Reichweite dieses Scanners (zweiter Themenzweig)",
     "Tag in range of this scanner (second topic branch)"),
    ("THEMA.SC_RSSI", "Signalstärke an diesem Scanner mit Ausgleich, -255 außer Reichweite",
     "Signal strength at this scanner with offset, -255 out of range"),

    # ---------------- nachgezogen 01.10.2026 aus dem Verbesserungsbau Welle 3
    # (BLE-Scanner NG, vb_ble_bau_skripte/bau_texte.py: a2, b1, Anwesenheit-1,
    # X-2/Entscheidung 16, X-3). Geaenderte Werte stehen an ihrer alten Stelle.
    ("TEXT.EINGABEN_ZURUECK", "Die eingetippten Werte stehen wieder im Formular, das beanstandete Feld ist rot umrandet. Nach dem Berichtigen erneut speichern. Ein erneutes Laden der Seite zeigt wieder die gespeicherten Werte.",
     "The values you typed are back in the form; the rejected field has a red border. Correct it and save again. Reloading the page shows the saved values again."),
    ("TEXT.LOG_NAME_DIENST", "Dienstprotokoll (ble_scanner_ng.log)",
     "Service log (ble_scanner_ng.log)"),
    ("TEXT.LOG_NAME_START", "Startprotokoll (ble_scanner_ng_start.log)",
     "Start log (ble_scanner_ng_start.log)"),
    ("TEXT.LOG_WER_DIENST", "Schreibt der laufende Dienst selbst: Suche, Kommen und Gehen, MQTT, Störungen. Es wird ab der eingestellten Größe gekappt.",
     "Written by the running service itself: scanning, arrivals and departures, MQTT, faults. It is trimmed from the configured size on."),
    ("TEXT.LOG_WER_START", "Hier steht, was beim Starten scheitert, bevor der Dienst sein eigenes Protokoll öffnet: welcher Startweg ihn rief (daemon, Wächter, Oberfläche, Installation), ein Python-Fehler beim Laden, eine belegte Sperre.",
     "Holds what fails while starting, before the service opens its own log: which start path called it (daemon, watchdog, web interface, installation), a Python error on load, a held lock."),
    ("TEXT.LOG_WER_WEITERE", "Weitere Datei im Protokollordner des Plugins.",
     "Another file in the log folder of the plugin."),
    ("TEXT.LOG_STAND", "Stand",
     "as of"),
    ("TEXT.LOG_DATEI_LEER", "Die Datei ist leer.",
     "The file is empty."),
    ("TEXT.BT_KASTEN", "Bluetooth fehlt – ohne Adapter und bluez findet der Scanner nichts. Der Befehl ist zum Abtippen auf der Konsole des LoxBerry (SSH):",
     "Bluetooth is missing – without an adapter and bluez the scanner finds nothing. The command is for typing on the LoxBerry console (SSH):"),
    ("TEXT.BT_KASTEN_GESPERRT", "Eingebautes Bluetooth ist vorhanden, aber die Treiber sind gesperrt: %s führt „blacklist %s“. Einmalig einschalten (dauerhaft: siehe Reiter Test):",
     "Onboard Bluetooth is present, but its drivers are blacklisted: %s holds ‘blacklist %s’. To switch it on once (permanently: see the Test tab):"),
    ("TEXT.BT_KASTEN_KEIN_TREIBER", "Eingebautes Bluetooth ist vorhanden, aber es ist kein Treiber geladen. Nachsehen, was der Kernel dazu meldet:",
     "Onboard Bluetooth is present, but no driver is loaded. See what the kernel reports:"),
    ("TEXT.BT_KASTEN_KEIN_GERAET", "Der Kernel kennt kein Bluetooth-Gerät (/sys/class/bluetooth fehlt, und der Gerätebaum führt keines). Hier hilft nur ein USB-Bluetooth-Adapter. Nach dem Einstecken muss dieser Befehl hci0 zeigen:",
     "The kernel knows no Bluetooth device (/sys/class/bluetooth is missing and the device tree lists none). Only a USB Bluetooth adapter helps here. After plugging it in, this command must show hci0:"),
    ("TEXT.BT_KASTEN_LEER", "Es ist kein Adapter angemeldet (/sys/class/bluetooth ist leer). Den Bluetooth-Dienst neu starten:",
     "No adapter is registered (/sys/class/bluetooth is empty). Restart the Bluetooth service:"),
    ("TEXT.BT_KASTEN_BLUEZ_FEHLT", "Das Paket bluez fehlt (kein bluetoothd gefunden). Nachinstallieren:",
     "The package bluez is missing (no bluetoothd found). Install it:"),
    ("TEXT.BT_KASTEN_DIENST_AUS", "Ein Adapter ist da, aber bluetooth.service ist %s. Einschalten und beim Systemstart mitstarten:",
     "An adapter is present, but bluetooth.service is %s. Start it and enable it at boot:"),
    ("TEXT.BT_KASTEN_DANACH", "Danach im Reiter Einstellungen Dienst neu starten. Der Kasten verschwindet, sobald Adapter und bluez da sind; die Einzelheiten stehen im Reiter Test (Ist ein Bluetooth-Adapter vorhanden?).",
     "Then restart the service in the Settings tab. The box disappears as soon as adapter and bluez are present; the details are in the Test tab (Is a Bluetooth adapter present?)."),
    ("TEXT.WLAN_UEBERSCHRIFT", "Anwesenheit mit dem WLAN-Scanner (ab Werk aus)",
     "Presence with the WiFi scanner (off by default)"),
    ("TEXT.WLAN_HILFE", "Führt je Person die Anwesenheit aus diesem Plugin und aus dem Plugin WiFi-Scanner NG zusammen. Gelesen werden nur dessen MQTT-Themen: wifi_ng/<Name> (0/1), das Lebenszeichen wifi_ng/status/ts und wifi_ng/status/ok. Der WiFi-Scanner sendet nur dann über MQTT, wenn dort UDP ausgeschaltet ist. Gesendet wird person/<Person>/anwesend_gesamt (1, wenn eine Quelle da sagt; 0, wenn beide weg sagen; - ohne Aussage) und person/<Person>/quelle (ble, wlan, ble+wlan oder -), beide retained. Schweigt der WiFi-Scanner länger als dreimal sein Takt (mindestens 3 Minuten), zählt nur BLE – der Reiter Test sagt es.",
     "Combines, per person, the presence from this plugin and from the plugin WiFi-Scanner NG. Only its MQTT topics are read: wifi_ng/<Name> (0/1), the heartbeat wifi_ng/status/ts and wifi_ng/status/ok. The WiFi scanner only sends via MQTT when UDP is switched off there. Sent are person/<Person>/anwesend_gesamt (1 if one source says present; 0 if both say away; - without a statement) and person/<Person>/quelle (ble, wlan, ble+wlan or -), both retained. If the WiFi scanner is silent for longer than three times its interval (at least 3 minutes), only BLE counts – the Test tab says so."),
    ("TEXT.WLAN_ZUORDNUNG_HILFE", "Je Person ein Paar WLAN-Name=Person, durch Kommas getrennt, z. B. Anna_Handy=Anna. Links der Name, unter dem der WiFi-Scanner die Person sendet (wifi_ng/Anna_Handy), rechts der Name aus der Zusatzangabe Person der Tags (Thema person/Anna/present). Erlaubt sind Buchstaben, Ziffern, Bindestrich und Unterstrich; jeder Name höchstens einmal, höchstens 20 Paare.",
     "One pair WiFi-name=person per person, separated by commas, e.g. Anna_Phone=Anna. On the left the name under which the WiFi scanner sends the person (wifi_ng/Anna_Phone), on the right the name from the Person option of the tags (topic person/Anna/present). Letters, digits, hyphen and underscore are allowed; each name at most once, at most 20 pairs."),
    ("FELD.WLAN_KOPPLUNG", "Anwesenheit mit dem WLAN-Scanner zusammenführen",
     "Combine presence with the WiFi scanner"),
    ("FELD.WLAN_ZUORDNUNG", "Zuordnung WLAN-Name = Person",
     "Mapping WiFi name = person"),
    ("MANGEL.WLAN_ZUORDNUNG", "Zuordnung WLAN-Name = Person: %s passt nicht zur Form Name=Person, Name=Person (Buchstaben, Ziffern, Bindestrich und Unterstrich; jeder Name höchstens einmal, höchstens 20 Paare). Es bleibt bei %s.",
     "Mapping WiFi name = person: %s does not match the form name=person, name=person (letters, digits, hyphen and underscore; each name at most once, at most 20 pairs). It stays at %s."),
    ("MANGEL.WLAN_OHNE_ZUORDNUNG", "Anwesenheit mit dem WLAN-Scanner: eingeschaltet, aber ohne Zuordnung – es gäbe nichts zusammenzuführen.",
     "Presence with the WiFi scanner: switched on, but without a mapping – there would be nothing to combine."),
    ("PRUEF.WLAN", "Anwesenheit mit dem WLAN-Scanner: meldet sich der WiFi-Scanner?",
     "Presence with the WiFi scanner: is the WiFi scanner reporting?"),
    ("PRUEF.WLAN_OHNE_ZUORDNUNG", "eingeschaltet, aber keine Zuordnung WLAN-Name = Person eingetragen",
     "switched on, but no mapping WiFi name = person entered"),
    ("PRUEF.WLAN_OHNE_MQTT", "MQTT ist ausgeschaltet – der WiFi-Scanner ist nur über MQTT zu hören; es zählt nur BLE.",
     "MQTT is switched off – the WiFi scanner can only be heard via MQTT; only BLE counts."),
    ("PRUEF.WLAN_NOCH_NICHT", "Der Dienst hat noch nicht zusammengeführt (der erste Durchlauf steht aus, oder es läuft eine Fassung ohne diese Kopplung).",
     "The service has not combined yet (the first pass is pending, or a version without this coupling is running)."),
    ("PRUEF.WLAN_PERSON", "%s (WLAN-Name %s): BLE %s, WLAN %s → gesamt %s, Quelle %s",
     "%s (WiFi name %s): BLE %s, WiFi %s → combined %s, source %s"),
    ("PRUEF.WLAN_FRISCH", "Lebenszeichen wifi_ng/status/ts vor %d s (Grenze %d s), status/ok = 1 – beide Quellen zählen.",
     "Heartbeat wifi_ng/status/ts %d s ago (limit %d s), status/ok = 1 – both sources count."),
    ("PRUEF.WLAN_SCHWEIGT", "Der WiFi-Scanner schweigt: %s Es zählt nur BLE.",
     "The WiFi scanner is silent: %s Only BLE counts."),
    ("PRUEF.WLAN_GRUND_ALT", "letztes Lebenszeichen vor %d s, Grenze %d s.",
     "last heartbeat %d s ago, limit %d s."),
    ("PRUEF.WLAN_GRUND_OK", "wifi_ng/status/ok = %s (sein letzter Lauf hatte eine Störung).",
     "wifi_ng/status/ok = %s (its last run had a fault)."),
    ("PRUEF.WLAN_GRUND_NIE", "seit dem Start des Dienstes kein Lebenszeichen wifi_ng/status/ts (sendet der WiFi-Scanner über MQTT? Dort muss UDP ausgeschaltet sein).",
     "no heartbeat wifi_ng/status/ts since the service started (does the WiFi scanner send via MQTT? UDP must be switched off there)."),
    ("PRUEF.KONFIG_SPAETER", "Noch nicht in der Datei (es gilt die Werkseinstellung; eingetragen beim nächsten Speichern): %s",
     "Not yet in the file (the factory setting applies; written on the next save): %s"),
    ("THEMA.P_GESAMT", "Person anwesend (1/0, -1 ohne Aussage) – ohne WLAN-Kopplung die BLE-Anwesenheit, mit Kopplung BLE und WLAN-Scanner",
     "Person present (1/0, -1 without statement) – without WiFi coupling the BLE presence, with coupling BLE and WiFi scanner"),
    ("THEMA.P_QUELLE", "Welche Quelle die Aussage trägt: ble, wlan, ble+wlan oder -; nur mit eingeschalteter Kopplung",
     "Which source carries the statement: ble, wlan, ble+wlan or -; only with the coupling switched on"),
    ("TEXT.SICH_ALTWERTE", "Achtung: gespeicherte Werte würden das eigene Zurückspielen nicht bestehen: %s. Die Sicherung wird trotzdem vollständig geliefert; zurückspielen lässt sie sich erst, wenn diese Werte im Formular berichtigt und gespeichert sind.",
     "Caution: stored values would not pass their own restore: %s. The backup is still delivered in full; it can only be restored once these values have been corrected in the form and saved."),
    ("TEXT.SICH_ALTWERTE_KOPF", "Diese gespeicherten Werte bestehen das Zurückspielen nicht: %s. Vor dem Zurückspielen berichtigen.",
     "These stored values do not pass the restore: %s. Correct them before restoring."),

    # ---- Welle Bild 19 (1.3.24): Seitenbloecke im Reiter Einbindung, Kurznamen der Personenthemen (E13)
    ("LOX.SCHRITTE_TITEL", "So übernehmen Sie diese Seite",
     "How to take over this page"),
    ("LOX.HINWEISE_TITEL", "Hinweise",
     "Notes"),
    ("LOX.BILD_ALT", "Bausteine der Seite „%s“ in Loxone Config",
     "Blocks of the page “%s” in Loxone Config"),
    ("LOX.BILD_UNTERSCHRIFT", "Seite „%s“ im LoxBerry-Plugins Musterprojekt. Config kürzt lange Bausteinnamen – Namen siehe Tabelle.",
     "Page “%s” in the LoxBerry plugins sample project. Config shortens long block names – see the table for the full names."),
    ("LOX.MUSTERPROJEKT", "Die ganze Projektdatei mit allen Plugin-Seiten und Vorlagen: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry-Plugins Musterprojekt</a>",
     "The complete project file with all plugin pages and templates: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry plugins sample project</a>"),
    # ---------------- Gruppe 13 (1.3.28): MQTT-Gateway, Befehlsbruecke, IRK, BTHome, Haus-Themen
    ("BAUSTEIN.Z2_16", "Virtueller Eingang (Taste) | Testmodus Schlüssel 1 | in der App; 60 s lang erscheint jede Einzelmessung im Plugin Reiter Test (Kasten „Testmodus“) – zum Platzieren des LoxBerry oder eines Anhängers | —",
     "Virtual Input (push button) | Testmodus Schlüssel 1 | in the app; for 60 s every single measurement appears in the plugin tab Test (box “Test mode”) – for placing the LoxBerry or a fob | —"),
    ("BAUSTEIN.Z2_17", "Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | BLE-Scanner NG: Testmodus Schlüssel 1 | Befehl bei EIN: publish blescanner/befehl/testmodus schluessel1 (nie retain); hinter „testmodus “ den Alias des eigenen Tags eintragen; wirkt nur mit dem Haken „Befehle über MQTT annehmen“ (Plugin Reiter Einstellungen) und laufendem Dienst | Eingang = #16",
     "Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | BLE-Scanner NG: Testmodus Schlüssel 1 | Command on ON: publish blescanner/befehl/testmodus schluessel1 (never retain); after “testmodus ” enter the alias of your own tag; works only with the tick “Accept commands via MQTT” (plugin tab Settings) and a running service | Input = #16"),
    ("BAUSTEIN.Z2_18", "Virtueller Eingang (Taste) | Auf 1 m kalibrieren (Schlüssel 1) | in der App; den Anhänger genau 1 m vor den LoxBerry legen, dann drücken – 10 s Messung | —",
     "Virtual Input (push button) | Auf 1 m kalibrieren (Schlüssel 1) | in the app; place the fob exactly 1 m in front of the LoxBerry, then press – 10 s measurement | —"),
    ("BAUSTEIN.Z2_19", "Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | BLE-Scanner NG: Kalibrieren Schlüssel 1 | Befehl bei EIN: publish blescanner/befehl/kalibrierung schluessel1 (nie retain); Alias wie Nr. 17; Ergebnis im Plugin Reiter Test und als Nr. 22; Haken wie Nr. 17 | Eingang = #18",
     "Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | BLE-Scanner NG: Kalibrieren Schlüssel 1 | Command on ON: publish blescanner/befehl/kalibrierung schluessel1 (never retain); alias as no. 17; result in the plugin tab Test and as no. 22; tick as no. 17 | Input = #18"),
    ("BAUSTEIN.Z2_20", "Virtueller Eingang (Taste) | Batterie jetzt lesen | in der App; liest den Batteriestand aller Tags mit „Batterie lesen“ sofort statt erst zur eingestellten Uhrzeit; manche Schlüsselfinder piepen dabei | —",
     "Virtual Input (push button) | Batterie jetzt lesen | in the app; reads the battery level of all tags with “Read battery” at once instead of at the set time; some key finders beep then | —"),
    ("BAUSTEIN.Z2_21", "Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | BLE-Scanner NG: Batterielauf | Befehl bei EIN: publish blescanner/befehl/batterie 1 (nie retain); wirkt nur mit „Befehle über MQTT annehmen“ UND „Eingreifende Befehle über MQTT annehmen“ sowie „Batteriestand über eine Verbindung lesen“; höchstens einmal je Stunde, sonst quittiert das Plugin „abgelehnt“ | Eingang = #20",
     "Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | BLE-Scanner NG: Batterielauf | Command on ON: publish blescanner/befehl/batterie 1 (never retain); works only with “Accept commands via MQTT” AND “Accept intervening commands via MQTT” as well as “Read battery level via a connection”; at most once per hour, otherwise the plugin acknowledges “abgelehnt” | Input = #20"),
    ("BAUSTEIN.Z2_22", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_schluessel1_kalibrierung | Ergebnis der letzten Kalibrierung: Median der Signalstärke in dBm; -255 = keine Messung; kommt einmal nach 10 s, nie retained; Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_schluessel1_kalibrierung | Result of the last calibration: median of the signal strength in dBm; -255 = no measurement; arrives once after 10 s, never retained; version 2: tick | —"),
    ("BAUSTEIN.Z2_23", "Status | Kalibrierung Schlüssel 1 (BLE) | Zeilen: V1 < -254 „keine Messung – Anhänger näher an den LoxBerry, dann erneut ‚Auf 1 m kalibrieren‘“; V1 = 0 „noch nicht kalibriert – Nr. 18 drücken“; ohne Bedingung „bei 1 m gemessen: <v1> dBm – im Plugin am Tag als Bezugswert (ref) eintragen, dann zeigt Nr. 5 die Entfernung“; Visualisierung EIN | V1 = #22",
     "Status | Kalibrierung Schlüssel 1 (BLE) | Rows: V1 < -254 “no measurement – fob closer to the LoxBerry, then ‘Calibrate at 1 m’ again”; V1 = 0 “not calibrated yet – press no. 18”; without condition “measured at 1 m: <v1> dBm – enter it on the tag in the plugin as reference value (ref), then no. 5 shows the distance”; visualisation ON | V1 = #22"),
    ("BAUSTEIN.SEITE2_SCHRITT6", "Speichern und übertragen. Probe: mit dem Anhänger durchs Haus gehen – die Signalstufe wechselt zwischen nah und mittel; „Testmodus Schlüssel 1“ drücken – im Plugin Reiter Test erscheinen die Einzelmessungen.",
     "Save and transfer. Check: walk through the house with the fob – the signal level changes between near and medium; press “Testmodus Schlüssel 1” – the single measurements appear in the plugin tab Test."),
    ("BAUSTEIN.SEITE2_H4", "Weitere Anhänger: dieselben Bausteine mit ihrem Alias.",
     "Further fobs: the same blocks with their alias."),
    ("BEFEHL.K_TESTMODUS", "Testmodus",
     "Test mode"),
    ("BEFEHL.K_KALIBRIERUNG", "Kalibrierung 1 m",
     "Calibration 1 m"),
    ("BEFEHL.K_BATTERIE", "Batterielauf",
     "Battery run"),
    ("BEFEHL.M_GESTARTET", "Befehlsbrücke gestartet (%s).",
     "Command bridge started (%s)."),
    ("BEFEHL.M_ANGEHALTEN", "Befehlsbrücke angehalten (%s).",
     "Command bridge stopped (%s)."),
    ("BEFEHL.M_START_FEHL", "Die Befehlsbrücke ließ sich nicht starten (%s) – der Wächter versucht es binnen einer Minute erneut; Reiter Test nennt den Grund.",
     "The command bridge could not be started (%s) – the watchdog retries within a minute; tab Test names the reason."),
    ("BEFEHL.M_STOP_FEHL", "Die Befehlsbrücke ließ sich nicht anhalten (%s).",
     "The command bridge could not be stopped (%s)."),
    ("BEFEHL.M_GESPEICHERT", "Gespeichert. Der Dienst läuft unverändert weiter (nur die Haken der Befehlsbrücke wurden geändert).",
     "Saved. The service keeps running unchanged (only the ticks of the command bridge were changed)."),
    ("BEFEHL.T_FEHLT", "bin/befehlsbruecke.php fehlt oder lässt sich nicht laden.",
     "bin/befehlsbruecke.php is missing or cannot be loaded."),
    ("BEFEHL.T_DEFEKT", "Zuordnung der Befehlsbrücke fehlerhaft: %s",
     "Command bridge assignment faulty: %s"),
    ("BEFEHL.T_AUS", "aus – „Befehle über MQTT annehmen“ ist nicht angehakt (ab Werk).",
     "off – “Accept commands via MQTT” is not ticked (default)."),
    ("BEFEHL.T_ARCHIV", "keine Aussage – nicht installiert.",
     "no statement – not installed."),
    ("BEFEHL.T_STEHT", "Haken an, aber die Befehlsbrücke läuft nicht – der Wächter (cron.01min) startet sie binnen einer Minute.",
     "Tick on, but the command bridge is not running – the watchdog (cron.01min) starts it within a minute."),
    ("BEFEHL.T_HAENGT", "die Befehlsbrücke meldet sich seit %d s nicht.",
     "the command bridge has not reported for %d s."),
    ("BEFEHL.T_OHNE_ABO", "die Befehlsbrücke läuft ohne Abo beim Broker: %s",
     "the command bridge runs without a subscription at the broker: %s"),
    ("BEFEHL.T_LAEUFT", "läuft seit %s; angenommen %d, abgelehnt %d; zuletzt %s",
     "running since %s; accepted %d, rejected %d; last %s"),
    ("BEFEHL.T_UNKLAR", "die Einrichtungsprüfung lieferte nichts.",
     "the setup check returned nothing."),
    ("BEFEHL.T_EINRICHTUNG", "(mosquitto-clients gehört zu den Paketen des Plugins; nach einem Update erneut prüfen)",
     "(mosquitto-clients is one of the plugin packages; check again after an update)"),
    ("BEFEHL.T_PRAEFIX", "Präfix %s taugt für die Befehlsbrücke.",
     "Prefix %s is valid for the command bridge."),
    ("BEFEHL.T_PRAEFIX_FALSCH", "Präfix %s taugt nicht für die Befehlsbrücke (höchstens 40 Zeichen je Ebene) – Befehle kommen nicht an.",
     "Prefix %s is not valid for the command bridge (at most 40 characters per level) – commands do not arrive."),
    ("FELD.BEFEHLE_MQTT", "Befehle über MQTT annehmen (Testmodus, Kalibrierung aus Loxone)",
     "Accept commands via MQTT (test mode, calibration from Loxone)"),
    ("FELD.BEFEHLE_EINGREIFEND", "Eingreifende Befehle über MQTT annehmen (Batterielauf)",
     "Accept intervening commands via MQTT (battery run)"),
    ("TEXT.BEFEHLE_HILFE", "Befehle kommen als publish <Präfix>/befehl/<Name> <Wert> über den UDP-Eingang des MQTT-Gateways; das Plugin quittiert unter <Präfix>/befehl/<Name>/quittung. Jeder im Heimnetz kann dorthin senden – deshalb sind beide Haken ab Werk aus. Der Batterielauf verbindet sich mit den Anhängern und braucht den zweiten Haken; höchstens einmal je Stunde. Die Haken starten den Dienst nicht neu.",
     "Commands arrive as publish <prefix>/befehl/<name> <value> via the UDP input of the MQTT gateway; the plugin acknowledges under <prefix>/befehl/<name>/quittung. Anyone in the home network can send there – that is why both ticks are off by default. The battery run connects to the fobs and needs the second tick; at most once per hour. The ticks do not restart the service."),
    ("TEXT.BEFEHLE_HEIMNETZ", "Jeder im Heimnetz kann über den UDP-Eingang des MQTT-Gateways Befehle senden – deshalb sind beide Haken ab Werk aus.",
     "Anyone in the home network can send commands via the UDP input of the MQTT gateway – that is why both ticks are off by default."),
    ("TEXT.BEFEHLE_GATEWAY", "Für Befehle ist unter Gateway V1 und V2 nichts einzutragen. Der Zweig des Tags (Alias) steht im Befehl, nie die Adresse.",
     "For commands nothing needs to be entered under gateway V1 or V2. The branch of the tag (alias) is in the command, never the address."),
    ("TEXT.HAKEN_EINER", "Befehle über MQTT annehmen",
     "Accept commands via MQTT"),
    ("TEXT.HAKEN_BEIDE", "beide Haken, dazu Batteriestand über eine Verbindung lesen",
     "both ticks, plus read battery level via a connection"),
    ("TEXT.SP_BEFEHLSTITEL", "Befehl (Titel in Loxone)",
     "Command (title in Loxone)"),
    ("TEXT.SP_BEFEHL_EIN", "Befehl bei EIN",
     "Command on ON"),
    ("TEXT.SP_HAKEN", "wirkt mit",
     "works with"),
    ("KNOPF.VORLAGE_MQTT", "Vorlage MQTT-Befehle",
     "Template MQTT commands"),
    ("PRUEF.BRUECKE", "Befehlsbrücke",
     "Command bridge"),
    ("PRUEF.BRUECKE_EINRICHTUNG", "Befehlsbrücke eingerichtet (mosquitto-clients, Zuordnung)?",
     "Command bridge set up (mosquitto-clients, assignment)?"),
    ("PRUEF.PRAEFIX_BRUECKE", "Präfix für die Befehlsbrücke gültig?",
     "Prefix valid for the command bridge?"),
    ("PRUEF.AUFTRAG", "Auftragsdatei frei?",
     "Order file free?"),
    ("TEST.AUFTRAG_FREI", "keine Auftragsdatei liegt",
     "no order file pending"),
    ("TEST.AUFTRAG_LIEGT", "eine Auftragsdatei liegt seit %d s – der Dienst hat sie noch nicht gelesen",
     "an order file has been pending for %d s – the service has not read it yet"),
    ("TEST.STEUER_BELEGT", "Ein anderer Auftrag wartet noch auf den Dienst – bitte gleich noch einmal.",
     "Another order is still waiting for the service – please try again in a moment."),
    ("TEST.BATTERIE_AUS", "Kein Batterielauf möglich: „Batteriestand über eine Verbindung lesen“ ist aus oder kein aktiver Tag hat „Batterie lesen“.",
     "No battery run possible: “Read battery level via a connection” is off or no active tag has “Read battery”."),
    ("TEXT.LOX_KOPF", "Das Musterprojekt liest die Werte über das MQTT-Gateway in einfache Virtuelle Eingänge und gibt Befehle über MQTT. Eine Vorlage mit Virtuellen HTTP-Eingängen gibt es nicht mehr.",
     "The sample project reads the values via the MQTT gateway into plain Virtual Inputs and sends commands via MQTT. There is no template with Virtual HTTP Inputs any more."),
    ("TEXT.NAMENSTABELLE", "Namen der Virtuellen Eingänge (wie das MQTT-Gateway sie vergibt)",
     "Names of the Virtual Inputs (as the MQTT gateway assigns them)"),
    ("TEXT.NAMENSTABELLE_HILFE", "Virtueller Eingang (Zahl) bzw. Virtueller Texteingang (Text), Name genau wie in der Tabelle, „Als Digitaleingang“ nicht anhaken. Spalte V2: N = in den Subscriptions zusätzlich „Noncached“, R = „Resetaftersend“. Ein anderes Präfix oder ein anderer Alias ergibt andere Namen. Messwerte erscheinen, sobald der Tag einmal gesendet hat.",
     "Virtual Input (number) or Virtual Text Input (text), name exactly as in the table, do not tick “Use as digital input”. Column V2: N = additionally “Noncached” in the subscriptions, R = “Resetaftersend”. A different prefix or alias gives different names. Measured values appear once the tag has sent."),
    ("TEXT.SP_GATEWAYNAME", "Name (Gateway) / Thema",
     "Name (gateway) / topic"),
    ("TEXT.SP_MUSTER", "Musterprojekt",
     "Sample project"),
    ("TEXT.ART_ZAHL", "Zahl",
     "Number"),
    ("TEXT.ART_TEXT", "Text",
     "Text"),
    ("TEXT.KOPIERT", "kopiert",
     "copied"),
    ("KNOPF.NAMEN_KOPIEREN", "Namen kopieren",
     "Copy names"),
    ("TEXT.HTTP_BESTAND_TITEL", "Bestehende Anlagen: HTTP-Push an den Miniserver",
     "Existing installations: HTTP push to the Miniserver"),
    ("TEXT.HTTP_BESTAND_TEXT", "Der Weg der Originalfassung (Reiter Einstellungen, „Weg zum Miniserver“, ab Werk aus) bleibt unverändert erhalten, damit bestehende Konfigurationen weiterlaufen. Neue Anlagen nehmen MQTT.",
     "The path of the original version (tab Settings, “Path to the Miniserver”, off by default) remains unchanged so that existing configurations keep running. New installations use MQTT."),
    ("LOX.S2_TEXT", "Gateway V2: die Themen der Namenstabelle (unten) in den Subscriptions anhaken; server/ok zusätzlich „Noncached“, Taster (button) „Resetaftersend“.",
     "Gateway V2: tick the topics of the name table (below) in the subscriptions; server/ok additionally “Noncached”, push buttons (button) “Resetaftersend”."),
    ("LOX.S7", "Schritt 7: Befehle aus Loxone",
     "Step 7: Commands from Loxone"),
    ("LOX.S7_TEXT", "Am gemeinsamen Ausgang „LoxBerry MQTT-Gateway“ je Befehl einen Virtuellen Ausgang Befehl mit dem Befehl bei EIN – oder die Vorlage MQTT-Befehle (grauer Knopf) importieren. Der Titel beginnt mit „BLE-Scanner NG:“ und gleicht damit keinem Gateway-Eingang.",
     "At the common output “LoxBerry MQTT-Gateway” one Virtual Output Command per command with the command on ON – or import the template MQTT commands (grey button). The title starts with “BLE-Scanner NG:” and thus matches no gateway input."),
    ("THEMA.STATUS_ZAEHLER", "Lebenszeichen für Loxone: zählt höchstens alle 30 s eins weiter (0–999), nie retained",
     "Sign of life for Loxone: counts on by one at most every 30 s (0–999), never retained"),
    ("THEMA.SC_ZAEHLER", "Lebenszeichen dieses Scanners (nur mit zweitem Themenzweig je Scanner)",
     "Sign of life of this scanner (only with the second topic branch per scanner)"),
    ("THEMA.BUTTON", "Taster-Ereignis (BTHome v2): press, double_press, long_press …; nie retained",
     "Push button event (BTHome v2): press, double_press, long_press …; never retained"),
    ("THEMA.KALIBRIERUNG", "Ergebnis der letzten Kalibrierung auf 1 m (dBm, -255 ohne Messung), nie retained",
     "Result of the last calibration at 1 m (dBm, -255 without measurement), never retained"),
    ("THEMA.S_HELLIGKEIT", "Beleuchtungsstärke aus den Werbedaten (BTHome)",
     "Illuminance from the advertising data (BTHome)"),
    ("THEMA.S_FENSTER", "Fensterkontakt aus den Werbedaten (BTHome): 1 offen, 0 zu",
     "Window contact from the advertising data (BTHome): 1 open, 0 closed"),
    ("THEMA.S_BEWEGUNGSMELDER", "Bewegungsmelder aus den Werbedaten (BTHome): 1 Bewegung, 0 frei",
     "Motion sensor from the advertising data (BTHome): 1 motion, 0 clear"),
    ("PRUEF.NAMEN", "Namenstabelle = gesendete Themen?",
     "Name table = topics sent?"),
    ("PRUEF.LEBENSZEICHEN", "Lebenszeichen status/zaehler",
     "Sign of life status/zaehler"),
    ("TEST.NAMEN", "%d Namen, jeder aus seinem Thema nach der Gateway-Regel",
     "%d names, each from its topic according to the gateway rule"),
    ("TEST.NAMEN_FEHL", "Name oder Thema passt nicht zum Sendecode: %s",
     "Name or topic does not match the sending code: %s"),
    ("TEST.ZAEHLER", "zählt (zuletzt %d)",
     "counting (last %d)"),
    ("TEST.ZAEHLER_ALT", "das Abbild trägt noch keinen Zähler – Dienst neu starten",
     "the image carries no counter yet – restart the service"),
    ("TEST.VORLAGE_GLEICH", "Befehlstitel gleich einem Gateway-Namen: %s",
     "Command title equal to a gateway name: %s"),
    ("TEST.VORLAGE_MQTT", "wohlgeformt, %d Befehle, kein Titel gleicht einem Gateway-Namen",
     "well-formed, %d commands, no title matches a gateway name"),
    ("TEST.THEMEN_ALLGEMEIN", "allgemein",
     "general"),
    ("TEST.THEMEN_BRUECKE", "Quittungen und Zustand der Befehlsbrücke, nie retained",
     "acknowledgements and state of the command bridge, never retained"),
    ("TEST.SPRACHEN_OK", "%d Abschnitte (Oberfläche und Hilfe), de = en",
     "%d sections (interface and help), de = en"),
    ("PRUEF.RESERVIERT", "Kein Tag-Alias auf einem reservierten Zweig?",
     "No tag alias on a reserved branch?"),
    ("TEST.ALIAS_RESERVIERT_DA", "Alias umbenennen – er belegt einen Zweig des Themenbaums: %s",
     "Rename the alias – it occupies a branch of the topic tree: %s"),
    ("MANGEL.TRENNZEICHEN", "%s: „%s“ enthält ein Trennzeichen (, = |) – es bleibt bei „%s“.",
     "%s: “%s” contains a separator (, = |) – it stays at “%s”."),
    ("MANGEL.TAG_PRUEFUNG", "%s: das Feld %s ist beanstandet – bitte berichtigen; gespeichert wird erst danach, gelöscht wird nichts.",
     "%s: the field %s is objected to – please correct it; saving happens only then, nothing is deleted."),
    ("TEXT.ALTOPTION_WEG", "Altoption min/raum entfernt (wirkungslos): %s.",
     "Old option min/raum removed (had no effect): %s."),
    ("FELD.IRK", "Schlüssel (IRK, 32 Hex)",
     "Key (IRK, 32 hex)"),
    ("FELD.IRK_AUFLOESEN", "Wechselnde Adressen über einen Schlüssel (IRK) auflösen",
     "Resolve changing addresses via a key (IRK)"),
    ("TEXT.IRK_AUFLOESEN_HILFE", "Ab Werk aus. Für Telefone und Uhren mit wechselnder Adresse: als Tag IRK:<Name> eintragen (Alias Pflicht) und den Identitätsschlüssel des Geräts hinterlegen. Er steht nur in irk.json (Rechte 0600), nie im Protokoll und nie in der Oberfläche. Eine Bluetooth-Kopplung wird nicht angefasst.",
     "Off by default. For phones and watches with a changing address: enter as tag IRK:<name> (alias required) and store the identity key of the device. It is only kept in irk.json (rights 0600), never in the log and never in the interface. No Bluetooth pairing is touched."),
    ("TEXT.IRK_HILFE", "Nur Schreiben: ein neuer Wert ersetzt den hinterlegten, leer lässt ihn stehen. Woher: auf einem gekoppelten Linux-Rechner /var/lib/bluetooth/<Adapter>/<Gerät>/info, Abschnitt IdentityResolvingKey.",
     "Write only: a new value replaces the stored one, empty keeps it. Where from: on a paired Linux computer /var/lib/bluetooth/<adapter>/<device>/info, section IdentityResolvingKey."),
    ("TEXT.IRK_HINTERLEGT", "hinterlegt",
     "stored"),
    ("TEXT.IRK_FEHLT", "kein Schlüssel hinterlegt",
     "no key stored"),
    ("MANGEL.IRK", "%s: der Schlüssel muss genau 32 Hex-Zeichen haben (nur bei einem Tag IRK:<Name>) – nichts hinterlegt.",
     "%s: the key must have exactly 32 hex characters (only for a tag IRK:<name>) – nothing stored."),
    ("PRUEF.IRK", "Wechselnde Adressen (IRK)",
     "Changing addresses (IRK)"),
    ("TEST.IRK_AUS", "aus (ab Werk)",
     "off (default)"),
    ("TEST.IRK_AUS_MIT_TAGS", "aus – IRK-Tags bleiben unsichtbar, bis der Haken gesetzt ist",
     "off – IRK tags stay invisible until the tick is set"),
    ("TEST.IRK_FEHLT", "kein Schlüssel hinterlegt für: %s",
     "no key stored for: %s"),
    ("TEST.IRK_RECHTE", "irk.json hat die Rechte %s statt 600",
     "irk.json has the rights %s instead of 600"),
    ("TEST.IRK_OK", "%d IRK-Tag(s), AES über %s",
     "%d IRK tag(s), AES via %s"),
    ("FELD.BTHOME", "BTHome v2 dekodieren (Shelly BLU u. a., unverschlüsselt)",
     "Decode BTHome v2 (Shelly BLU etc., unencrypted)"),
    ("TEXT.BTHOME_HILFE", "Temperatur, Feuchte, Helligkeit, Fenster- und Bewegungsmelder, Batterie und Taster (Thema <Tag>/button, nie retained, je Druck einmal – entprellt über die Paket-Id). Nur mit „Werbedaten dekodieren“. Bei einer Neuinstallation an, nach einem Update aus. Gegen die Formatbeschreibung bthome.io geprüft, nicht an einem Gerät.",
     "Temperature, humidity, illuminance, window and motion sensors, battery and push buttons (topic <tag>/button, never retained, once per press – debounced via the packet id). Only with “Decode advertising data”. On for a new installation, off after an update. Checked against the format description bthome.io, not on a device."),
    ("TEXT.HAUS_UEBERSCHRIFT", "Anwesenheit für andere Plugins (haus/…)",
     "Presence for other plugins (haus/…)"),
    ("FELD.HAUS_ANWESENHEIT", "Anwesenheit für andere Plugins bereitstellen (haus/anwesenheit/…)",
     "Provide presence for other plugins (haus/anwesenheit/…)"),
    ("TEXT.HAUS_HILFE", "Ab Werk aus. Sendet haus/anwesenheit/<person> und haus/anwesenheit/jemand (1/0, ohne Aussage -, retained) und als Lebenszeichen haus/anwesenheit/zaehler (alle 30 s, nie retained). Je Tag mit dem Haken „an andere Plugins melden“ zusätzlich haus/tag/<name>/da. Nur ein Scanner im Haus darf Anbieter sein. Ausgeschaltet und bei der Deinstallation räumt das Plugin nur seine eigenen Haus-Themen ab.",
     "Off by default. Sends haus/anwesenheit/<person> and haus/anwesenheit/jemand (1/0, no statement -, retained) and as sign of life haus/anwesenheit/zaehler (every 30 s, never retained). For each tag with the tick “report to other plugins” additionally haus/tag/<name>/da. Only one scanner in the house may be the provider. When switched off and on uninstall the plugin removes only its own haus topics."),
    ("FELD.HAUS_JE_TAG", "an andere Plugins melden (haus/tag)",
     "report to other plugins (haus/tag)"),
    ("PRUEF.HAUS", "Anwesenheit für andere Plugins (haus/…)",
     "Presence for other plugins (haus/…)"),
    ("TEST.HAUS_AUS", "aus (ab Werk)",
     "off (default)"),
    ("TEST.HAUS_UNKLAR", "keine Aussage – kein gültiges Abbild",
     "no statement – no valid image"),
    ("TEST.HAUS_OK", "%d Thema/Themen: %s; Zähler %d",
     "%d topic(s): %s; counter %d"),
    ("TEST.HAUS_NAMEN", "Namensregel PHP/Dienst ungleich - im Abbild fehlt: %s",
     "Name rule PHP/service differs - missing in the image: %s"),
    ("TEXT.TESTMODUS_KASTEN", "Testmodus",
     "Test mode"),
    ("TEXT.TESTMODUS_KOPF", "%1 – noch %2 s, %3 Messungen, Median %4 dBm (min %5, max %6)",
     "%1 – %2 s left, %3 measurements, median %4 dBm (min %5, max %6)"),
    ("TEXT.SP_UHRZEIT", "Uhrzeit",
     "Time"),
    ("TEXT.SP_DBM", "dBm",
     "dBm"),
    # ---------------- Drift-Abgleich 06.11.2026: wortgleich aus BLE-Scanner 1.3.34 nachgetragen
    # ---------------- BAUSTEIN
    ("BAUSTEIN.Z3_14", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_thermometer_wohnzimmer_sensor_lage | Lage der Messwerte: 0 frisch, 1 noch kein Messwert seit dem Start des Dienstes, 2 verschlüsselt – kein Bind-Key hinterlegt, 3 Bind-Key passt nicht, 4 veraltet (seit der Frist im Plugin kein Messwert), 5 alte verschlüsselte Form – nicht lesbar; zurückbehalten; gilt nur zusammen mit blescanner_server_online; Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_thermometer_wohnzimmer_sensor_lage | state of the readings: 0 fresh, 1 no reading yet since the service started, 2 encrypted – no bind key stored, 3 bind key does not match, 4 outdated (no reading since the deadline in the plugin), 5 old encrypted form – not readable; retained; only valid together with blescanner_server_online; version 2: tick | —"),
    ("BAUSTEIN.Z3_15", "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin BLE-Scanner NG) | blescanner_thermometer_wohnzimmer_sensor_alter | Sekunden seit dem letzten gültigen Messwert (Temperatur oder Feuchte); -1 = noch nie; höchstens einmal je Minute neu; nie retained; Fassung 2: Haken | —",
     "Virtual Input (name as the MQTT gateway assigns it, plugin BLE-Scanner NG) | blescanner_thermometer_wohnzimmer_sensor_alter | seconds since the last valid reading (temperature or humidity); -1 = never; renewed at most once per minute; never retained; version 2: tick | —"),
    ("BAUSTEIN.Z3_16", "Formel | Messwerte fehlen (BLE) | IF(I1>1.5;1;0) – 1 bei Lage 2 bis 5 (kein Schlüssel, Schlüssel falsch, veraltet, alte Form); Lage 1 (Dienst eben gestartet) zählt nicht | I1 = #14",
     "Formula | Messwerte fehlen (BLE) | IF(I1>1.5;1;0) – 1 at state 2 to 5 (no key, wrong key, outdated, old form); state 1 (service just started) does not count | I1 = #14"),
    ("BAUSTEIN.Z3_17", "ODER | Thermometer verstummt oder ohne Messwerte (BLE) | — (außer Reichweite bei laufendem Dienst ODER in Reichweite ohne gültige Messwerte) | I1 = Ausgang Q von #11, I2 = #16",
     "OR | Thermometer verstummt oder ohne Messwerte (BLE) | — (out of range while the service runs OR in range without valid readings) | I1 = output Q of #11, I2 = #16"),
    # ---------------- CLOUD
    ("CLOUD.ABRUF_TEXT", "Verschlüsselnde Xiaomi-Fühler senden ihre Werte nur mit dem Bind-Key (BLE KEY) lesbar. Mit Ihrer Xiaomi-Anmeldung holt das Plugin die Liste Ihrer Bluetooth-Geräte samt Schlüssel; Sie übernehmen ein Gerät in die Tag-Liste. Das Kennwort wird nur für diesen einen Abruf benutzt – nie gespeichert, nie protokolliert. Captcha und Zweitfaktor tippen Sie selbst; Zwischenstände liegen höchstens 10 Minuten (0600) im Datenordner. Die Liste zeigt nie einen Schlüssel.",
     "Encrypting Xiaomi sensors send readable values only with the bind key (BLE KEY). With your Xiaomi login the plugin fetches the list of your Bluetooth devices including the key; you take a device over into the tag list. The password is used only for this one request – never stored, never logged. You type captcha and second factor yourself; intermediate states stay at most 10 minutes (0600) in the data folder. The list never shows a key."),
    ("CLOUD.ABRUF_TITEL", "Anmelden und Bluetooth-Geräte abrufen",
     "Sign in and fetch Bluetooth devices"),
    ("CLOUD.CAPTCHA_BILD", "Captcha von Xiaomi",
     "Captcha from Xiaomi"),
    ("CLOUD.CAPTCHA_LOESUNG", "Zeichen aus dem Bild",
     "Characters from the image"),
    ("CLOUD.CAPTCHA_TEXT", "Xiaomi verlangt ein Captcha. Tippen Sie die Zeichen aus dem Bild und Ihr Kennwort erneut ein – ein Versuch, 10 Minuten.",
     "Xiaomi asks for a captcha. Type the characters from the image and your password again – one attempt, 10 minutes."),
    ("CLOUD.CODE", "Code",
     "Code"),
    ("CLOUD.F_ABGELAUFEN", "Abgelaufen (10 Minuten) – neu anmelden.",
     "Expired (10 minutes) – sign in again."),
    ("CLOUD.F_ANTWORT", "Unerwartete Antwort von Xiaomi.",
     "Unexpected response from Xiaomi."),
    ("CLOUD.F_API", "Die Geräteliste war in keiner Region abrufbar.",
     "The device list could not be fetched in any region."),
    ("CLOUD.F_CAPTCHA_BILD", "Das Captcha-Bild ließ sich nicht holen.",
     "The captcha image could not be fetched."),
    ("CLOUD.F_CAPTCHA_FALSCH", "Das Captcha war falsch – neu anmelden.",
     "The captcha was wrong – sign in again."),
    ("CLOUD.F_CODE", "Der Code ist unzulässig (4 bis 12 Zeichen).",
     "The code is invalid (4 to 12 characters)."),
    ("CLOUD.F_KEINE", "Keine Bluetooth-Geräte im Konto (Regionen: %s).",
     "No Bluetooth devices in the account (regions: %s)."),
    ("CLOUD.F_KENNWORT", "Anmeldung abgelehnt – Konto oder Kennwort falsch.",
     "Sign-in refused – account or password wrong."),
    ("CLOUD.F_KONTO", "Das Konto enthält unzulässige Zeichen.",
     "The account contains invalid characters."),
    ("CLOUD.F_LEER", "Konto und Kennwort eintragen.",
     "Enter account and password."),
    ("CLOUD.F_LOESUNG", "Die Captcha-Zeichen fehlen oder sind unzulässig.",
     "The captcha characters are missing or invalid."),
    ("CLOUD.F_NETZ", "Xiaomi ist nicht erreichbar.",
     "Xiaomi is not reachable."),
    ("CLOUD.F_SCHREIBEN", "Der Zwischenstand ließ sich nicht schreiben (Datenordner).",
     "The intermediate state could not be written (data folder)."),
    ("CLOUD.F_SENDEN", "Xiaomi hat den Code nicht verschickt – den anderen Weg versuchen.",
     "Xiaomi did not send the code – try the other way."),
    ("CLOUD.F_UEB_ABGELAUFEN", "Die Auswahl ist abgelaufen oder verbraucht – neu abrufen.",
     "The selection has expired or been used – fetch again."),
    ("CLOUD.F_UEB_MAC", "Gerät %s: MAC fehlt in der Antwort – über „Geräte suchen“ anlegen und den Schlüssel von Hand eintragen.",
     "Device %s: MAC missing in the response – add via “Search for devices” and enter the key manually."),
    ("CLOUD.F_UEB_SCHLUESSEL", "Gerät %s: kein brauchbarer Schlüssel in der Antwort.",
     "Device %s: no usable key in the response."),
    ("CLOUD.F_UEB_SCHREIBEN", "Gerät %s: Konfiguration oder bindkey.json nicht schreibbar.",
     "Device %s: configuration or bindkey.json not writable."),
    ("CLOUD.F_UEB_TAG", "Gerät %s: als Tag nicht zulässig (Name).",
     "Device %s: not allowed as a tag (name)."),
    ("CLOUD.F_UEB_WAHL", "Kein Gerät gewählt.",
     "No device chosen."),
    ("CLOUD.F_WEG", "Diesen Weg bietet Xiaomi für das Konto nicht an.",
     "Xiaomi does not offer this way for the account."),
    ("CLOUD.F_ZIEL", "Abgebrochen: Xiaomi leitete auf eine fremde Adresse um.",
     "Aborted: Xiaomi redirected to a foreign address."),
    ("CLOUD.H_BINDKEY", "Bind-Key aus der Xiaomi-Cloud holen",
     "Get bind key from the Xiaomi cloud"),
    ("CLOUD.KENNWORT", "Kennwort",
     "Password"),
    ("CLOUD.KENNWORT_HINWEIS", "Das Kennwort wird nicht gespeichert und nach dem Abruf verworfen.",
     "The password is not stored and is discarded after the request."),
    ("CLOUD.KONTO", "Xiaomi-Konto (Mail, Telefon oder Xiaomi-Kennung)",
     "Xiaomi account (mail, phone or Xiaomi ID)"),
    ("CLOUD.K_CAPTCHA", "Captcha senden",
     "Send captcha"),
    ("CLOUD.K_CODE", "Code senden",
     "Send code"),
    ("CLOUD.K_HOLEN", "Geräte abrufen",
     "Fetch devices"),
    ("CLOUD.K_UEBERNEHMEN", "Übernehmen",
     "Take over"),
    ("CLOUD.K_WEG_MAIL", "Code per Mail anfordern",
     "Request code by mail"),
    ("CLOUD.K_WEG_SMS", "Code per SMS anfordern",
     "Request code by SMS"),
    ("CLOUD.MAC_FEHLT", "MAC fehlt in der Antwort – Gerät über „Geräte suchen“ anlegen und den Schlüssel von Hand eintragen",
     "MAC missing in the response – add the device via “Search for devices” and enter the key manually"),
    ("CLOUD.M_ALTE_FORM", "Achtung: 24-Hex-Schlüssel – alte verschlüsselte Form, das Plugin kann sie nicht lesen.",
     "Note: 24-hex key – old encrypted form, the plugin cannot read it."),
    ("CLOUD.M_CAPTCHA", "Captcha nötig – unten lösen.",
     "Captcha needed – solve it below."),
    ("CLOUD.M_CODE_MAIL", "Code per Mail angefordert – unten eintragen.",
     "Code requested by mail – enter it below."),
    ("CLOUD.M_CODE_SMS", "Code per SMS angefordert – unten eintragen.",
     "Code requested by SMS – enter it below."),
    ("CLOUD.M_GEFUNDEN", "%d Bluetooth-Gerät(e) gefunden (Regionen: %s) – unten übernehmen.",
     "%d Bluetooth device(s) found (regions: %s) – take over below."),
    ("CLOUD.M_UEB_BESTEHEND", "Bind-Key am Tag %s hinterlegt.",
     "Bind key stored on tag %s."),
    ("CLOUD.M_UEB_NEU", "Neuer Tag %s mit Alias und Bind-Key angelegt.",
     "New tag %s with alias and bind key created."),
    ("CLOUD.M_UEB_NEU_OHNE_ALIAS", "Neuer Tag %s mit Bind-Key angelegt – ohne Alias (Name belegt oder unzulässig), das Thema heißt nach der MAC.",
     "New tag %s with bind key created – without alias (name taken or not allowed), the topic is named after the MAC."),
    ("CLOUD.M_ZWEITFAKTOR", "Zweiter Faktor nötig – unten den Weg wählen.",
     "Second factor needed – choose the way below."),
    ("CLOUD.REGION", "Region",
     "Region"),
    ("CLOUD.REGION_ALLE", "alle Regionen",
     "all regions"),
    ("CLOUD.REGION_CN", "China (cn)",
     "China (cn)"),
    ("CLOUD.REGION_DE", "Europa (de)",
     "Europe (de)"),
    ("CLOUD.REGION_I2", "Indien (i2)",
     "India (i2)"),
    ("CLOUD.REGION_RU", "Russland (ru)",
     "Russia (ru)"),
    ("CLOUD.REGION_SG", "Singapur (sg)",
     "Singapore (sg)"),
    ("CLOUD.REGION_US", "USA (us)",
     "USA (us)"),
    ("CLOUD.SP_MODELL", "Modell",
     "Model"),
    ("CLOUD.SP_NAME", "Name",
     "Name"),
    ("CLOUD.SP_REGION", "Region",
     "Region"),
    ("CLOUD.UEBERNEHMEN_TEXT", "Übernehmen setzt den Schlüssel am Tag mit dieser MAC; gibt es keinen, entsteht ein neuer aktiver Tag mit dem Namen aus der Cloud und – wenn frei – einem Alias daraus. Die Liste gilt 10 Minuten.",
     "Take over sets the key on the tag with this MAC; if there is none, a new active tag with the name from the cloud and – if free – an alias derived from it is created. The list is valid for 10 minutes."),
    ("CLOUD.WEG2", "Ohne Anmeldung im Plugin: der Xiaomi-cloud-tokens-extractor (PiotrMachowski, MIT) zeigt den Schlüssel als „BLE KEY“ – dann in die Tag-Zeile unter „Bind-Key (Xiaomi)“ eintragen.",
     "Without signing in via the plugin: the Xiaomi-cloud-tokens-extractor (PiotrMachowski, MIT) shows the key as “BLE KEY” – then enter it in the tag row under “Bind key (Xiaomi)”."),
    ("CLOUD.ZWEITFAKTOR_LINK", "Seite der Identitätsprüfung bei Xiaomi",
     "Identity check page at Xiaomi"),
    ("CLOUD.ZWEITFAKTOR_TEXT", "Tragen Sie den Code ein, den Xiaomi geschickt hat (10 Minuten ab der Anmeldung, ein Versuch).",
     "Enter the code Xiaomi sent (10 minutes from the sign-in, one attempt)."),
    ("CLOUD.ZWEITFAKTOR_WAHL", "Xiaomi verlangt einen zweiten Faktor. Wählen Sie, wohin der Code geschickt wird.",
     "Xiaomi asks for a second factor. Choose where the code is sent."),
    # ---------------- FELD
    ("FELD.BINDKEY", "Bind-Key (Xiaomi)",
     "Bind key (Xiaomi)"),
    ("FELD.BINDKEY_WEG", "Schlüssel löschen",
     "Delete key"),
    ("FELD.MESSWERT_FRIST", "Frist der Messwerte (Sekunden, 300 bis 21600)",
     "Deadline of the readings (seconds, 300 to 21600)"),
    ("FELD.XIAOMI_REGION", "Region der Xiaomi-Cloud (Vorwahl für den Bind-Key-Abruf)",
     "Region of the Xiaomi cloud (preselection for fetching bind keys)"),
    # ---------------- MANGEL
    ("MANGEL.BINDKEY", "Bind-Key von %s: 32 (oder 24) Hex-Zeichen erwartet, an einer MAC-Zeile – nicht übernommen.",
     "Bind key of %s: 32 (or 24) hex characters expected, on a MAC row – not taken over."),
    ("MANGEL.BINDKEY_BEIDES", "Bind-Key von %s: neuer Schlüssel und „Schlüssel löschen“ zugleich – bitte eines von beiden.",
     "Bind key of %s: new key and “Delete key” at the same time – please only one of them."),
    ("MANGEL.REGION", "Region %s unbekannt – erlaubt de, cn, i2, ru, sg, us, alle.",
     "Region %s unknown – allowed de, cn, i2, ru, sg, us, alle."),
    # ---------------- PRUEF
    ("PRUEF.BINDKEY", "Bind-Keys",
     "Bind keys"),
    ("PRUEF.CCM", "AES-CCM (MiBeacon)",
     "AES-CCM (MiBeacon)"),
    ("PRUEF.THERMO", "Thermometer %s",
     "Thermometer %s"),
    ("PRUEF.V2_HAKEN", "Gateway V2: sind alle Datenpunkte der Hakenliste angehakt?",
     "Gateway V2: are all data points of the tick list ticked?"),
    # ---------------- TEST
    ("TEST.BINDKEY_OK", "%d hinterlegt, vom Dienst geladen %s; bindkey.json 0600",
     "%d stored, loaded by the service %s; bindkey.json 0600"),
    ("TEST.BINDKEY_RECHTE", "bindkey.json hat die Rechte %s statt 600.",
     "bindkey.json has the permissions %s instead of 600."),
    ("TEST.BINDKEY_WAISEN", "%d Schlüssel ohne passende MAC-Zeile (z. B. nach Handbearbeitung) – Speichern räumt sie ab.",
     "%d keys without a matching MAC row (e.g. after manual editing) – saving removes them."),
    ("TEST.CCM_FEHL", "von %d Fällen fehlgeschlagen (AES über %s): %s",
     "of %d cases failed (AES via %s): %s"),
    ("TEST.CCM_OK", "%d Fälle bestanden (NIST SP 800-38C Anhang C, Beispiel 1 und 2, MiBeacon-Testpaket), AES über %s %s",
     "%d cases passed (NIST SP 800-38C appendix C, example 1 and 2, MiBeacon test packet), AES via %s %s"),
    ("TEST.THERMO", "%s; Alter %d s; %s; %s",
     "%s; age %d s; %s; %s"),
    ("TEST.V2_AUS", "trifft nicht zu – die MQTT-Veröffentlichung dieses Plugins ist aus.",
     "not applicable – MQTT publishing of this plugin is switched off."),
    ("TEST.V2_FEHLT", "Es fehlen: %s.",
     "Missing: %s."),
    ("TEST.V2_NC_FEHLT", "Noncached fehlt: %s.",
     "Noncached missing: %s."),
    ("TEST.V2_NC_ZUVIEL", "Noncached zu viel: %s.",
     "Noncached not expected: %s."),
    ("TEST.V2_UNKLAR", "nicht feststellbar (Gateway-Fassung oder config/system/subscriptions.json nicht lesbar).",
     "cannot be determined (gateway version or config/system/subscriptions.json not readable)."),
    ("TEST.V2_LEER", "nicht feststellbar – die Hakenliste ist leer (Themenliste des Plugins nicht lesbar).",
     "cannot be determined – the tick list is empty (topic list of the plugin not readable)."),
    ("TEST.V2_V1", "trifft nicht zu (MQTT-Gateway V1).",
     "not applicable (MQTT gateway V1)."),
    ("TEST.V2_ZAHL", "%d von %d Datenpunkten angehakt.",
     "%d of %d data points ticked."),
    # ---------------- TEXT
    ("TEXT.BINDKEY_ALT", "Bind-Key: hinterlegt (24 Hex, alte Form – nicht lesbar)",
     "Bind key: stored (24 hex, old form – not readable)"),
    ("TEXT.BINDKEY_FEHLT", "Bind-Key: fehlt",
     "Bind key: missing"),
    ("TEXT.BINDKEY_HILFE", "Nur Schreiben: ein neuer Wert ersetzt den hinterlegten, leer lässt ihn stehen, der Haken löscht ihn. Nur für verschlüsselnde Xiaomi-Fühler nötig (32 Hex, „BLE KEY“); der runde Mi-Fühler (LYWSDCGQ) braucht keinen. Der Schlüssel liegt in bindkey.json (0600) und erscheint nirgends.",
     "Write only: a new value replaces the stored one, empty keeps it, the tick deletes it. Only needed for encrypting Xiaomi sensors (32 hex, “BLE KEY”); the round Mi sensor (LYWSDCGQ) needs none. The key is kept in bindkey.json (0600) and is shown nowhere."),
    ("TEXT.BINDKEY_HINTERLEGT", "Bind-Key: hinterlegt (32 Hex)",
     "Bind key: stored (32 hex)"),
    ("TEXT.LAGE_0", "Messwerte frisch",
     "readings fresh"),
    ("TEXT.LAGE_1", "noch kein Messwert seit dem Start des Dienstes",
     "no reading yet since the service started"),
    ("TEXT.LAGE_2", "verschlüsselt – kein Bind-Key hinterlegt",
     "encrypted – no bind key stored"),
    ("TEXT.LAGE_3", "Bind-Key passt nicht",
     "bind key does not match"),
    ("TEXT.LAGE_3_HILFE", "Der Bind-Key ändert sich bei jedem neuen Koppeln in Mi Home – neu holen.",
     "The bind key changes with every new pairing in Mi Home – fetch it again."),
    ("TEXT.LAGE_4", "veraltet – seit der Frist kein Messwert",
     "outdated – no reading since the deadline"),
    ("TEXT.LAGE_5", "verschlüsselt, alte Form – nicht lesbar",
     "encrypted, old form – not readable"),
    ("TEXT.MESSWERT_FRIST_HILFE", "Kommt so lange kein gültiger Messwert, geht über das MQTT-Gateway V2 Temperatur -999 und Feuchte -1 hinaus, die Lage wird 4 (veraltet); die Batterie wird erst nach 24 Stunden ohne Batteriesatz -1. Sparsame Fühler senden nur alle 5 bis 10 Minuten – ab Werk 1800 s.",
     "If no valid reading arrives for this long, temperature -999 and humidity -1 go out via MQTT gateway V2, the state becomes 4 (outdated); the battery becomes -1 only after 24 hours without a battery record. Economical sensors send only every 5 to 10 minutes – default 1800 s."),
    ("TEXT.SICH_SCHLUESSEL", "Schlüssel aus der Sicherung: Bind-Keys %s, IRK %s (- = Abschnitt fehlt, hinterlegte bleiben).",
     "Keys from the backup: bind keys %s, IRK %s (- = section missing, stored ones stay)."),
    ("TEXT.SICH_SCHLUESSEL_UEBERGANGEN", "Abschnitt %s: Eintrag %s übergangen (falsche Form oder kein Tag dazu).",
     "Section %s: entry %s skipped (wrong form or no tag for it)."),
    ("TEXT.VOR_SEKUNDEN", "(vor %d s)",
     "(%d s ago)"),
    # ---------------- THEMA
    ("THEMA.S_ALTER", "Sekunden seit dem letzten gültigen Messwert, -1 = noch nie",
     "Seconds since the last valid reading, -1 = never"),
    ("THEMA.S_LAGE", "Lage der Messwerte: 0 frisch, 1 noch keiner seit dem Start, 2 kein Bind-Key, 3 Bind-Key passt nicht, 4 veraltet, 5 alte Form",
     "State of the readings: 0 fresh, 1 none yet since start, 2 no bind key, 3 bind key wrong, 4 outdated, 5 old form"),
    # ---------------- ANSAGEPLUGIN (Reihenfolge = Ausgabereihenfolge, siehe NACH_ANSAGE)
    ("ANSAGEPLUGIN.H", "Sprachansagen",
     "Announcements"),
    ("ANSAGEPLUGIN.K_SPEICHERN", "Sprachansagen speichern",
     "Save announcements"),
    ("ANSAGEPLUGIN.K_TEST", "Testansage an alle Ziele",
     "Test announcement to all targets"),
    ("ANSAGEPLUGIN.M_OK", "Sprachansagen gespeichert.",
     "Announcements saved."),
    ("ANSAGEPLUGIN.M_FEHL", "Die Sprachansagen ließen sich nicht speichern.",
     "The announcements could not be saved."),
    ("ANSAGEPLUGIN.M_TEST_OK", "Testansage gesendet.",
     "Test announcement sent."),
    ("ANSAGEPLUGIN.M_TEST_FEHL", "Testansage nicht gesendet:",
     "Test announcement not sent:"),
    ("ANSAGEPLUGIN.L_AUSFALL", "Scanner fällt aus (Adapter oder BlueZ), und wieder da",
     "Scanner fails (adapter or BlueZ), and back again"),
    ("ANSAGEPLUGIN.SATZ_AUSFALL", "Der Bluetooth-Scanner ist ausgefallen.",
     "The Bluetooth scanner has failed."),
    ("ANSAGEPLUGIN.SATZ_WIEDER", "Der Bluetooth-Scanner läuft wieder.",
     "The Bluetooth scanner is running again."),
]


def maskierte_schluessel(wurzel):
    """Welche Schluessel laufen im PHP durch bl_e()?

    Nur fuer diese ist Auszeichnung im Wert ein Fehler - sie erschiene dort
    als spitze Klammer im Klartext. Dieselbe Unterscheidung fuehren
    byd_ und ww_sprache_erzeugen.py seit langem.

    Gesucht werden beide Schachtelungen: bl_e(bl_t(...)) und
    bl_e(sprintf(bl_t(...))). Ein Muster, das nur eine kennt, uebersieht die
    Haelfte.
    """
    treffer = set()
    if wurzel is None:
        return treffer
    for f in sorted(Path(wurzel).rglob("*.php")):
        t = f.read_text(encoding="utf-8", errors="replace")
        for muster in (r"bl_e\(\s*bl_t\(\s*'([A-Z0-9_]+\.[A-Z0-9_]+)'",
                       r"bl_e\(\s*sprintf\(\s*bl_t\(\s*'([A-Z0-9_]+\.[A-Z0-9_]+)'"):
            for x in re.finditer(muster, t):
                treffer.add(x.group(1))
    return treffer

def pruefe(maskiert=frozenset()):
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
            # Auszeichnung und Entitaeten sind NUR dort verboten, wo der Wert
            # durch bl_e() laeuft. bl_t() gibt ihn sonst roh zurueck, und in
            # einem <div class="sm-hinweis"> ist ein <b> genau richtig.
            #
            # BERICHTIGT 31.08.2026: hier stand das Verbot pauschal. Es traf
            # damit die drei Gateway-Texte, die dreizehn der Sicherung und die
            # zwei des Wachpostens - allesamt Werte, die roh ausgegeben werden.
            # Sie konnten deshalb nie in diese Tabelle und sind von Hand in die
            # .ini geschrieben worden, wo der naechste Lauf sie geloescht
            # haette. Eine Wache, die das Richtige mitverbietet, wird umgangen.
            # BERICHTIGT 20.09.2026: das Verbot traf jede spitze Klammer und
            # damit auch Platzhalter - "<Praefix>/<Tag>/sensor/<Name>" in
            # TEXT.LOX_MESSWERTE_TEXT. Dieser Wert laeuft durch bl_e() und
            # soll woertlich so auf dem Bildschirm stehen; er konnte deshalb
            # nie in diese Tabelle, stand nur in der .ini, und der Erzeuger
            # wies seit 1.3.16 jeden Lauf ab. Verboten bleibt, was als
            # Auszeichnung gemeint ist: ein Ende-Tag, ein bekanntes HTML-Tag
            # oder eine Entitaet. Geeicht in beide Richtungen,
            # Pruefung-Spracherzeuger-Bestand/wache_eichung.py.
            if schluessel in maskiert:
                if re.search(r'</\s*\w|<\s*(?:b|i|u|em|strong|span|div|p|br|hr|ul|ol|li|a|'
                             r'code|pre|small|sup|sub|table|thead|tbody|tr|td|th|h[1-6])\b',
                             wert, re.I):
                    fehler.append("Markup im maskierten Wert (%s, %s)"
                                  % (schluessel, sprache))
                if re.search(r'&(?:[a-zA-Z][a-zA-Z0-9]*|#\d+|#[xX][0-9a-fA-F]+);', wert):
                    fehler.append("Entitaet im maskierten Wert (%s, %s)"
                                  % (schluessel, sprache))
            if "\n" in wert or "\r" in wert:
                fehler.append("Zeilenumbruch im Wert (%s, %s)" % (schluessel, sprache))
        # Platzhalter muessen in beiden Sprachen gleich oft vorkommen.
        if de.count("%s") != en.count("%s") or de.count("%d") != en.count("%d"):
            fehler.append("Platzhalter ungleich: " + schluessel)
    return fehler


# Abschnitte, die hinter [ANSAGE] stehen und in Tabellenreihenfolge ausgegeben werden
# (in 1.3.34 gemessen: [ANSAGEPLUGIN] steht nach [ANSAGE] und ist nicht sortiert).
NACH_ANSAGE = ("ANSAGEPLUGIN",)


def ansage_abschnitt(sprache):
    """Der Abschnitt [ANSAGE] der gemeinsamen Sprachausgabe - EINE Quelle:
    Werkzeuge/gemeinsam_pruefen.py baut ihn aus Werkzeuge/gemeinsam/sprachausgabe_texte.json
    (wie renault_ und au_sprache_erzeugen.py). Gesucht wird aufwaerts vom Ablageort."""
    import os
    hier = os.path.dirname(os.path.abspath(__file__))
    while True:
        for w in (hier, os.path.join(hier, "Werkzeuge")):
            if (os.path.isfile(os.path.join(w, "gemeinsam_pruefen.py"))
                    and os.path.isfile(os.path.join(w, "gemeinsam", "sprachausgabe_texte.json"))):
                sys.path.insert(0, w)
                import gemeinsam_pruefen
                return gemeinsam_pruefen.ini_abschnitt(sprache)
        oben = os.path.dirname(hier)
        if oben == hier:
            raise SystemExit("Werkzeuge/gemeinsam_pruefen.py nicht gefunden - es wurde nichts geschrieben.")
        hier = oben


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
        if abschnitt in NACH_ANSAGE:
            continue
        zeilen.append("[%s]\n" % abschnitt)
        for name, wert in sorted(aus[abschnitt]):
            zeilen.append('%s = "%s"\n' % (name, wert))
        zeilen.append("\n")
    # Drift-Abgleich 06.11.2026, gemessen an 1.3.34: nach den sortierten Abschnitten folgen
    # eine Leerzeile, [ANSAGE] (gemeinsames Sprachmodul, eine Quelle) und danach die Abschnitte
    # aus NACH_ANSAGE in Tabellenreihenfolge, unsortiert, ohne Leerzeile am Dateiende.
    zeilen.append("\n")
    zeilen.append(ansage_abschnitt(sprache))
    for abschnitt in NACH_ANSAGE:
        zeilen.append("\n[%s]\n" % abschnitt)
        for name, wert in aus.get(abschnitt, []):
            zeilen.append('%s = "%s"\n' % (name, wert))
    return "".join(zeilen)


def main():
    argumente = [a for a in sys.argv[1:] if not a.startswith("--")]
    probe = "--probe" in sys.argv
    if not argumente:
        print("Aufruf: ble_sprache_erzeugen.py <plugin-ordner> [--probe]")
        return 2
    ziel = Path(argumente[0]) / "templates" / "lang"

    fehler = pruefe(maskierte_schluessel(argumente[0]))
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


# Wache gegen stillen Schluesselverlust - eine Quelle fuer alle Erzeuger.
#
# Werkzeuge/sprachwache.py legt sich vor jeden Schreibweg und vergleicht die
# .ini, die geschrieben werden soll, mit der, die schon dasteht. Verschwaende
# ein Schluessel, bricht der Lauf mit Rueckgabewert 2 ab, BEVOR etwas
# geschrieben ist. Ein geaenderter WERT wird nur gemeldet ("... bestehende
# Werte werden neu gefasst") und geschrieben - einen Wert zu aendern ist die
# Aufgabe eines Erzeugers (sprachwache.pruefen()). Jeder Schluessel in dieser
# Meldung, den man nicht selbst geaendert hat, ist ein Befund am Erzeuger.
# BERICHTIGT 24.09.2026: bis dahin stand hier, auch ein ueberschriebener
# Wert breche ab. Das tat die gemeinsame Wache nie; gemessen an diesem
# Werkzeugbestand (Pruefung-Funkwacht-1.0.7, Sprachwache): geaenderter Wert
# rc 0 und geschrieben, fremder Schluessel rc 2 und nichts geschrieben.
#
# Anlass: am 06.09.2026 ueber alle Erzeuger gemessen. Zwei von vierzehn
# hätten beim Lauf gegen ihren eigenen Plugin-Ordner Schluessel verloren
# (Robonect 13, Sprachsteuerung 3); die uebrigen waren nur zufaellig gleich-
# auf. Ein Erzeugerkopf in einer Datei ist eine Aussage ueber die Vergangen-
# heit, nie ueber den heutigen Stand des Erzeugers.
#
# Absichtlich loeschen:  SPRACHWACHE=aus python3 <erzeuger>.py <ordner>
import sprachwache
sprachwache.einhaengen()


if __name__ == "__main__":
    sys.exit(main())
