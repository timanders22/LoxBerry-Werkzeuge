#!/usr/bin/env python3
"""Erzeugt language_de.ini und language_en.ini fuer Midea2Lox aus EINER Quelle.

NACHZUG KOPF-WELLE (08.10.2026, Entscheidung Nr. 43, Pruefung-Durchgang-
2026-09-29/vb_kopf_mid_bau_skripte/werkzeug_bauen.py): nachgezogen auf
Midea2Lox 4.5.13. Von Hand in die .ini gekommen waren (4.5.9 bis 4.5.12)
44 Schluessel und der Abschnitt [REGION]; 6 Werte waren dort neu gefasst,
1 Schluessel dort entfernt. Werte und Reihenfolge sind wortgleich aus der
.ini von 4.5.13 uebernommen. Erzeugt die beiden language_*.ini von
LoxBerry-Plugin-Midea2Lox-4.5.13 byteweise gleich.

STAND (vb_x10_mid, 09.10.2026, Welle X-10): Baustein-Liste in der Grammatik von
Werkzeuge/leitungen_setzen.py 1.1 - UI.BL_GATEWAY, BL_EINGANG5, BL_EINGANG11,
BL_ALTER_EIN, BL_ALTER_AUS, BL_ODER, BL_VOM_ODER neu gefasst (gleiche Verbindungen).

STAND (vb_bild_md19, 18.10.2026, Welle Bild 19 / Musterprojekt, Vollausstattung): Reiter "Einbindung in
Loxone", Schritt 6 mit drei Seiten aus dem Musterprojekt (Entwurf Welle 19 md, E16/E17): die alte Liste
(50 Schluessel UI.BL_* und UI.OPTIONAL) entfaellt; neuer Abschnitt [BAUSTEIN] mit 121 Schluesseln
(90 Tabellenzeilen Z1_01..Z3_33, Kaesten, Hinweise), 7 UI.* (Kasten-/Hinweistitel, Bild, Link,
Behaelter-Kommentare der Vorlagen, E7) und BEF.HUM (E6); neu gefasst:
UI.SCHRITT1, UI.SCHRITT1_TEXT, UI.SCHRITT3_TEXT, UI.H_VORLAGE_TEXT, UI.SCHRITT4_TEMP, UI.SCHRITT5_TEXT,
UI.SCHRITT6, UI.SCHRITT6_TEXT, UI.NAME_VORSCHLAG.

STAND (vb_bild_md20, 18.10.2026, Welle Bild 20 / Textnachzug, Midea2Lox 4.5.16): Seite "Midea2Lox" #30
"Automatik (Midea)" mit V4 = #29 (Texteingang Midea2Lox_automatik_grund als <v4> im Status); nur
BAUSTEIN.Z1_30 neu gefasst (de/en).

STAND (vb_g15_mi, 24.10.2026, Gruppe 15 / MQTT, Midea2Lox 4.5.18): Reiter "Einbindung in Loxone" ohne
HTTP-Vorlage (Namenstabelle mit Fehlwert und V2, Befehle ueber MQTT, Vorlage MQTT-Befehle, UDP-Weg zugeklappt);
Bausteinliste nach Musterprojekt/baustein_listen.txt 79b695e2 (31/27/40 Zeilen); neu Haken der MQTT-Befehle,
Anwesenheit (V1), Pruefzeilen, BEF.RATE_*/LEVEL_* (E4); entfallen UI.H_VORLAGE, UI.H_VORLAGE_TEXT, UI.K_VORLAGE,
UI.VI_KOMMENTAR, UI.GERAET_UEBERSCHRIFT, UI.TITEL_EINGANG - vor dem Lauf auf 4.5.18 aus den .ini streichen
(eigene Verlustpruefung).

STAND (Drift-Abgleich, 06.11.2026): angeglichen an Midea2Lox 4.5.24, 67 Schluessel neu, 0 Werte
geaendert, 0 entfernt (PRUEF 3, WERT 2, UI 49 - Vorkuehlen mit Sonnenstrom -, neuer Abschnitt
[ANSAGEPLUGIN] 13); dazu der Abschnitt [ANSAGE] (314 Schluessel) nicht als Tabelle, sondern aus
Werkzeuge/gemeinsam_pruefen.ini_abschnitt() vor [ANSAGEPLUGIN] (ANSAGE_VOR); die Verlustpruefung
zaehlt diese Schluessel mit.

Aufruf:  python mi_sprache_erzeugen.py <plugin-ordner>

WARUM EIN ERZEUGER

Zwei Sprachdateien von Hand deckungsgleich zu halten geht so lange gut, bis
jemand einen Schluessel nur in einer von beiden ergaenzt. Hier stehen beide
Texte in derselben Zeile; auseinanderlaufen koennen sie nicht.

WAS DER ERZEUGER ABWEIST, STATT ES ZURECHTZUBIEGEN

  * ein gerades Anfuehrungszeichen im Wert - es beendet den INI-Wert, und
    der Rest des Satzes wird STILL abgeschnitten (kein Fehler, keine
    Warnung, nur ein Satz, der mitten im Wort aufhoert),
  * ein Zeilenumbruch im Wert - INI kennt keine mehrzeiligen Werte,
  * ein Schluesselname, den der INI-Parser als Schluesselwort liest
    (TRUE, FALSE, ON, OFF, YES, NO, NULL, NONE),
  * HTML-Entitaeten fuer Umlaute - die Dateien tragen echte UTF-8-Zeichen.

Die Werte stehen in doppelten Anfuehrungszeichen. Ohne sie faellt bei einem
Wert mit & ( ) ! oder ? die GANZE Datei aus, nicht nur die eine Zeile.
"""
import io
import os
import re
import sys

SCHLUESSELWOERTER = {'TRUE', 'FALSE', 'ON', 'OFF', 'YES', 'NO', 'NULL', 'NONE'}
ENTITAETEN = re.compile(r'&(auml|ouml|uuml|Auml|Ouml|Uuml|szlig);')

# ---------------------------------------------------------------------------
# Die Texte. Aufbau: ABSCHNITT -> [(SCHLUESSEL, deutsch, englisch), ...]
# ---------------------------------------------------------------------------
TEXTE = {

'COMMON': [
 ('LABEL_SETTINGS', 'Einstellungen', 'Settings'),
 ('LABEL_MQTT', 'MQTT', 'MQTT'),
 ('LABEL_LOXONE', 'Einbindung in Loxone', 'Loxone integration'),
 ('LABEL_TEST', 'Test', 'Test'),
 ('LABEL_LOG', 'Logdateien', 'Log files'),
 ('LABEL_AUTOMATIK', 'Automatik', 'Automation'),
],

'SETTINGS': [
 ('HEAD_SERVICE', 'Dienst', 'Service'),
 ('HEAD_LOXONE', 'Verbindung zum Miniserver', 'Connection to the Miniserver'),
 ('HEAD_MIDEA', 'Midea-Konto', 'Midea account'),
 ('HEAD_ADVANCED', 'Erweitert', 'Advanced'),
 ('HEAD_DEVICES', 'Gefundene Klimageräte', 'Discovered air conditioners'),
],

'TEST': [
 ('HEAD_SELFCHECK', 'Selbstprüfung', 'Self-check'),
],

# --- Die Zeilen der Selbstpruefung ---------------------------------------
'PRUEF': [
 ('VENV', 'Ist die virtuelle Python-Umgebung da?', 'Is the Python virtual environment present?'),
 ('MSMART', 'Lässt sich msmart-ng laden?', 'Can msmart-ng be loaded?'),
 ('PYTHON', 'Welche Python-Fassung läuft in der Umgebung?', 'Which Python version runs in the environment?'),
 ('PAHO', 'Welche Fassung hat paho-mqtt?', 'Which version of paho-mqtt is installed?'),
 ('DIENST', 'Läuft der Dienst?', 'Is the service running?'),
 ('SOLL', 'Soll der Dienst laufen?', 'Is the service supposed to run?'),
 ('MARKE', 'Läuft gerade eine Aktualisierung?', 'Is an update currently running?'),
 ('HERZSCHLAG', 'Arbeitet der Dienst noch?', 'Is the service still working?'),
 ('KONFIGURATION', 'Ist die Konfiguration heil?', 'Is the configuration intact?'),
 ('UDP_PORT', 'Ist der UDP-Port zulässig?', 'Is the UDP port valid?'),
 ('KONTO', 'Welches Midea-Konto benutzt die Gerätesuche?', 'Which Midea account does the device search use?'),
 ('REGION', 'Lässt sich die Region einem Serverbereich zuordnen?', 'Can the region be mapped to a server area?'),
 ('GERAETE', 'Sind Klimageräte hinterlegt?', 'Are air conditioners configured?'),
 ('GATEWAY', 'Zustand des MQTT-Gateways', 'State of the MQTT gateway'),
 ('GATEWAY_FASSUNG', 'Welche Fassung hat das MQTT-Gateway?', 'Which version is the MQTT gateway?'),
 ('ABO_DATEI', 'Bringt das Plugin das passende Abo mit?', 'Does the plugin ship the matching subscription?'),
 ('ABO_EINGETRAGEN', 'Ist unser Thema im Gateway abonniert?', 'Is our topic subscribed in the gateway?'),
 ('REITER', 'Passen Reiterleiste, Flächen und Positivliste zusammen?', 'Do the tab bar, panes and allow-list match?'),
 ('FORMULARE', 'Tragen alle Formulare das Merkmal?', 'Do all forms carry the token?'),
 ('THEMEN', 'Stimmt die Themenliste mit dem Sendecode überein?', 'Does the topic list match the sending code?'),
 ('SPRACHE', 'Sind alle Sprachschlüssel der Tabellen vorhanden?', 'Are all language keys of the tables present?'),
 ('VORLAGEN', 'Sind die Loxone-Vorlagen wohlgeformt?', 'Are the Loxone templates well-formed?'),
 ('AUTO_LAEUFT', 'Läuft die Automatik?', 'Is the automation running?'),
 ('AUTO_REGEL', 'Kommt das Preissignal an?', 'Is the price signal arriving?'),
 ('AUTO_PV', 'Kommt der PV-Überschuss an?', 'Is the PV surplus arriving?'),
 ('RETAIN', 'Führen Oberfläche und Dienst dieselbe Retain-Liste?', 'Do interface and service keep the same retain list?'),
 ('FENSTER', 'Fenster offen: Gerät aus - läuft die Kopplung?', 'Window open: device off - is the coupling running?'),
 ('FENSTER_QUELLE', 'Kommt %s an?', 'Is %s arriving?'),
 ('FENSTER_BEFEHL', 'Aus-Befehl an %s', 'Off command to %s'),
 # ---- Gruppe 15 (4.5.18): MQTT-Befehle, Namenstabelle, Anwesenheit, Fehlwerte
 ('LOXBERRYIP', 'Zeigt die UDP-Vorlage auf die Adresse dieses LoxBerry?', 'Does the UDP template point to the address of this LoxBerry?'),
 ('MQTT_BEFEHLE', 'Befehle über MQTT', 'Commands via MQTT'),
 ('ZUORDNUNG', 'Zuordnung MQTT-Befehle = UDP-Befehle?', 'Mapping MQTT commands = UDP commands?'),
 ('FEHLWERTE', 'Fehlwerte Dienst = Oberfläche?', 'Default values service = interface?'),
 ('NAMEN', 'Namenstabelle nach der Regel des Gateways?', 'Name table following the gateway rule?'),
 ('ANWESENHEIT', 'Anwesenheit (haus/anwesenheit/jemand)', 'Presence (haus/anwesenheit/jemand)'),
 ('VK_FELDER', 'Vorkühlen: Feldtabelle Oberfläche = Dienst?', 'Pre-cooling: field table interface = service?'),
 ('VK_ENERGIE', 'haus/energie für „Mit Sonnenstrom vorkühlen“', 'haus/energie for “Pre-cool with solar power”'),
 ('VK_GERAET', 'Vorkühlen: %s', 'Pre-cooling: %s'),
],

# --- Die veroeffentlichten Werte -----------------------------------------
'WERT': [
 ('POWER_STATE', 'Ein/Aus', 'Power on/off'),
 ('ONLINE', 'Erreichbarkeit', 'Reachability'),
 ('INDOOR_TEMPERATURE', 'Raumtemperatur', 'Indoor temperature'),
 ('OUTDOOR_TEMPERATURE', 'Außentemperatur', 'Outdoor temperature'),
 ('TARGET_TEMPERATURE', 'Solltemperatur', 'Target temperature'),
 ('OPERATIONAL_MODE', 'Betriebsart', 'Operating mode'),
 ('FAN_SPEED', 'Lüfterstufe', 'Fan speed'),
 ('SWING_MODE', 'Schwenken', 'Swing mode'),
 ('AUDIBLE_FEEDBACK', 'Quittungston beim Schalten', 'Audible feedback when switching'),
 ('ECO_MODE', 'Sparbetrieb', 'Eco mode'),
 ('TURBO_MODE', 'Schnellbetrieb', 'Turbo mode'),
 ('DISPLAY_ON', 'Anzeige am Gerät', 'Display on the unit'),
 ('SLEEP_MODE', 'Nachtbetrieb', 'Sleep mode'),
 ('FOLLOW_ME', 'Regelung nach Fernbedienung', 'Follow-me control'),
 ('FREEZE_PROTECTION', 'Frostschutz', 'Freeze protection'),
 ('PURIFIER', 'Luftreinigung', 'Air purifier'),
 ('SELF_CLEAN', 'Selbstreinigung läuft', 'Self-cleaning active'),
 ('FILTER_ALERT', 'Filter reinigen', 'Filter needs cleaning'),
 ('TARGET_HUMIDITY', 'Sollfeuchte', 'Target humidity'),
 ('INDOOR_HUMIDITY', 'Raumfeuchte', 'Indoor humidity'),
 ('H_SWING_ANGLE', 'Schwenkwinkel waagerecht', 'Horizontal swing angle'),
 ('V_SWING_ANGLE', 'Schwenkwinkel senkrecht', 'Vertical swing angle'),
 ('RATE_SELECT', 'Leistungsbegrenzung', 'Power limit'),
 ('BREEZE_MODE', 'Sanfter Luftstrom', 'Breeze mode'),
 ('IECO', 'iECO-Betrieb', 'iECO mode'),
 ('TOTAL_ENERGY', 'Energie gesamt', 'Total energy'),
 ('CURRENT_ENERGY', 'Energie seit dem Einschalten', 'Energy since power on'),
 ('REAL_TIME_POWER', 'Augenblickliche Leistung', 'Current power draw'),
 ('ST_OK', 'Letzter Durchgang: 1 gemessen, 0 gescheitert, -1 noch keiner', 'Last cycle: 1 measured, 0 failed, -1 none yet'),
 ('ST_TS', 'Zeitstempel des letzten Durchgangs, Unix-Sekunden', 'Timestamp of the last cycle, Unix seconds'),
 ('ST_ZAEHLER', 'Umlaufender Zähler, 0 bis 999', 'Rolling counter, 0 to 999'),
 ('ST_DIENST', 'Der Dauerläufer läuft - gemessen vom Cron-Lauf', 'The daemon is running - measured by the cron job'),
 ('AU_AKTIV', 'Automatik greift gerade (1) oder nicht (0)', 'automation engaged (1) or not (0)'),
 ('AU_GESPERRT', 'Restzeit der Handsperre in Sekunden', 'remaining manual lockout in seconds'),
 ('AU_GERAETE', 'Zahl der Geräte mit laufender Verschiebung', 'number of devices with an active shift'),
 ('AU_GRUND', 'Klartext: warum die Automatik greift oder nicht', 'plain text: why the automation is engaged or not'),
 ('ST_VERBINDUNG', 'Verbindung des Dienstes zum Broker: connected bei jedem Verbinden, disconnected setzt der Broker als Letzten Willen (beide zurückbehalten)', 'Connection of the service to the broker: connected on every connect, disconnected is set by the broker as last will (both retained)'),
 # ---- Gruppe 15 (4.5.18): MQTT-Befehle, Namenstabelle, Anwesenheit, Fehlwerte
 ('ST_BEFEHLE', 'Befehle über MQTT: 1 = werden angenommen (Abo bestätigt), 0 = Haken aus, -1 = Haken an, aber kein Abo; nie zurückbehalten', 'Commands via MQTT: 1 = accepted (subscription confirmed), 0 = tick off, -1 = tick on, but no subscription; never retained'),
 ('ANW_AKTIV', 'Abwesenheitsbetrieb: 1 = das Plugin hält Klimageräte wegen „niemand zu Hause“, 0 = nicht, -1 = Kopplung an, aber die Quelle schweigt; nie zurückbehalten', 'Away mode: 1 = the plugin holds air conditioners because of “nobody at home”, 0 = not, -1 = coupling on, but the source is silent; never retained'),
 ('VK_AKTIV', 'Mit Sonnenstrom vorkühlen: Zahl der Geräte, die das Plugin gerade vorkühlt (0 = keines); jede Minute, solange ein Gerät eingeschaltet ist; nie zurückbehalten', 'Pre-cool with solar power: number of devices the plugin is pre-cooling right now (0 = none); every minute while a device is switched on; never retained'),
 ('VK_MELDUNG', 'Mit Sonnenstrom vorkühlen: die letzte Aktion als kurzer Text (Uhrzeit, Gerät, ein, aus oder Hand), „-“ ohne Aktion seit dem Dienststart; nie zurückbehalten', 'Pre-cool with solar power: the last action as short text (time, device, on, off or manual), “-” without action since the service started; never retained'),
],

# --- Die Befehle ----------------------------------------------------------
'BEF': [
 ('EIN_AUS', 'Ein- und ausschalten', 'Switch on and off'),
 ('MODE_AUTO', 'Betriebsart Automatik', 'Operating mode automatic'),
 ('MODE_COOL', 'Betriebsart Kühlen', 'Operating mode cooling'),
 ('MODE_HEAT', 'Betriebsart Heizen', 'Operating mode heating'),
 ('MODE_DRY', 'Betriebsart Entfeuchten', 'Operating mode dehumidify'),
 ('MODE_FAN', 'Betriebsart nur Lüften', 'Operating mode fan only'),
 ('FAN_AUTO', 'Lüfterstufe Automatik', 'Fan speed automatic'),
 ('FAN_SILENT', 'Lüfterstufe leise', 'Fan speed silent'),
 ('FAN_LOW', 'Lüfterstufe niedrig', 'Fan speed low'),
 ('FAN_MEDIUM', 'Lüfterstufe mittel', 'Fan speed medium'),
 ('FAN_HIGH', 'Lüfterstufe hoch', 'Fan speed high'),
 ('FAN_FULL', 'Lüfterstufe höchste', 'Fan speed maximum'),
 ('SWING_OFF', 'Schwenken aus', 'Swing off'),
 ('SWING_VERT', 'Schwenken senkrecht', 'Swing vertical'),
 ('SWING_HORZ', 'Schwenken waagerecht', 'Swing horizontal'),
 ('SWING_BOTH', 'Schwenken in beide Richtungen', 'Swing both directions'),
 ('ECO', 'Sparbetrieb', 'Eco mode'),
 ('TURBO', 'Schnellbetrieb', 'Turbo mode'),
 ('SLEEP', 'Nachtbetrieb', 'Sleep mode'),
 ('FOLLOW', 'Regelung nach Fernbedienung', 'Follow-me control'),
 ('FREEZE', 'Frostschutz', 'Freeze protection'),
 ('PURIFIER', 'Luftreinigung', 'Air purifier'),
 ('TONE', 'Quittungston', 'Audible feedback'),
 ('DISPLAY', 'Anzeige am Gerät umschalten', 'Toggle the display on the unit'),
 ('SELFCLEAN', 'Selbstreinigung starten', 'Start self-cleaning'),
 ('STATUS', 'Zustand abfragen', 'Query the state'),
 ('TEMP', 'Solltemperatur stufenlos', 'Target temperature, continuous'),
 ('HUM', 'Sollfeuchte stufenlos', 'Target humidity, continuous'),
 # ---- Gruppe 15 (4.5.18): MQTT-Befehle, Namenstabelle, Anwesenheit, Fehlwerte
 ('RATE_OFF', 'Leistungsbegrenzung aus', 'Power limitation off'),
 ('RATE_50', 'Leistungsbegrenzung 50 Prozent', 'Power limitation 50 per cent'),
 ('RATE_75', 'Leistungsbegrenzung 75 Prozent', 'Power limitation 75 per cent'),
 ('LEVEL_1', 'Leistungsstufe 1', 'Power level 1'),
 ('LEVEL_2', 'Leistungsstufe 2', 'Power level 2'),
 ('LEVEL_3', 'Leistungsstufe 3', 'Power level 3'),
 ('LEVEL_4', 'Leistungsstufe 4', 'Power level 4'),
 ('LEVEL_5', 'Leistungsstufe 5', 'Power level 5'),
],

'UI': [
 # --- Wachposten ---
 ('WACHE_FEHLT', 'Die Anfrage trug kein Formularmerkmal und wurde abgewiesen. Bitte die Seite neu laden und den Vorgang wiederholen.', 'The request carried no form token and was rejected. Please reload the page and try again.'),
 ('WACHE_FALSCH', 'Das Formularmerkmal war ungültig - vermutlich ist die Sitzung abgelaufen. Bitte die Seite neu laden.', 'The form token was invalid - the session has probably expired. Please reload the page.'),

 # --- Meldungen ---
 ('NICHT_GESPEICHERT', 'Es wurde nichts gespeichert:', 'Nothing was saved:'),
 ('GESPEICHERT_NEUSTART', 'Gespeichert. Der Dienst wurde neu gestartet.', 'Saved. The service was restarted.'),
 ('GESPEICHERT_OHNE_DIENST', 'Gespeichert. Der Dienst ließ sich nicht neu starten - bitte im Reiter Test nachsehen.', 'Saved. The service could not be restarted - please check the Test tab.'),
 ('GESPEICHERT_SUCHE', 'Gespeichert. Das Ergebnis der Gerätesuche steht im Reiter Test; der Dienst wurde danach neu gestartet.', 'Saved. The result of the device search is in the Test tab; the service was restarted afterwards.'),
 ('MQTT_GESPEICHERT', 'Gespeichert. Das Abo wurde mitgeschrieben und der Dienst neu gestartet (auch die Haken der MQTT-Befehle wirken erst damit).', 'Saved. The subscription was written as well and the service restarted (the ticks of the MQTT commands take effect only with that, too).'),
 ('CFG_SCHREIBFEHLER', 'Die Datei midea2lox.cfg ließ sich nicht schreiben. Bitte die Rechte im Konfigurationsordner prüfen.', 'The file midea2lox.cfg could not be written. Please check the permissions of the configuration folder.'),
 ('CFG_ERGAENZT', 'Die Konfiguration war unvollständig und wurde vervollständigt. Ergänzt wurden: %s', 'The configuration was incomplete and has been completed. Added: %s'),
 ('BEZ_GESPEICHERT', 'Die Bezeichnungen wurden gespeichert.', 'The labels have been saved.'),
 ('BEZ_SCHREIBFEHLER', 'Die Bezeichnungen ließen sich nicht schreiben - devices.cfg ist nicht beschreibbar.', 'The labels could not be written - devices.cfg is not writable.'),
 ('DIENST_GESTARTET', 'Der Dienst wurde gestartet.', 'The service was started.'),
 ('DIENST_ANGEHALTEN', 'Der Dienst wurde angehalten.', 'The service was stopped.'),
 ('DIENST_NEU', 'Der Dienst wurde neu gestartet.', 'The service was restarted.'),
 ('DIENST_SKRIPT_FEHLT', 'Der Dienst ließ sich nicht steuern - das Startskript %s fehlt.', 'The service could not be controlled - the start script %s is missing.'),
 ('DIENST_UNBEKANNT', 'Unbekannte Aktion für den Dienst - es wurde nichts ausgeführt.', 'Unknown service action - nothing was executed.'),
 ('DIENST_UPGRADE', 'Es läuft gerade eine Aktualisierung dieses Plugins. Der Dienst wurde deshalb nicht gestartet; er läuft, sobald die Aktualisierung fertig ist.', 'An update of this plugin is currently running. The service was therefore not started; it will run as soon as the update has finished.'),
 ('REGION_UNBEKANNT', 'Die eingetragene Region %s lässt sich keinem Serverbereich von msmart-ng zuordnen. Bitte im Reiter Einstellungen neu wählen.', 'The configured region %s cannot be mapped to any msmart-ng server area. Please choose again in the Settings tab.'),

 # --- Pruefmeldungen (EINE Positivliste, von Formular und Sicherung benutzt) ---
 ('PRUEF_UNTAUGLICH', 'Der Wert für %s ist keine brauchbare Zeichenkette.', 'The value for %s is not a usable string.'),
 ('PRUEF_MINISERVER', 'Der Miniserver muss aus der Liste gewählt werden.', 'The Miniserver must be chosen from the list.'),
 ('PRUEF_UDP_PORT', 'Der UDP-Port ist eine Zahl zwischen 1 und 65535.', 'The UDP port is a number between 1 and 65535.'),
 ('PRUEF_LEBENSDAUER', 'Die Verbindungsdauer ist eine Zahl zwischen 10 und 3600 Sekunden.', 'The connection lifetime is a number between 10 and 3600 seconds.'),
 ('PRUEF_TIMEOUT', 'Die Wartezeit auf den Miniserver ist eine Zahl zwischen 1 und 60 Sekunden.', 'The Miniserver timeout is a number between 1 and 60 seconds.'),
 ('PRUEF_TAKT', 'Der Abfragetakt ist 0 (aus) oder eine Zahl zwischen 30 und 86400 Sekunden.', 'The polling interval is 0 (off) or a number between 30 and 86400 seconds.'),
 ('PRUEF_DEBUG', 'Das ausführliche Protokoll ist ein oder aus.', 'The verbose log is either on or off.'),
 ('PRUEF_REGION', 'Die Region muss aus der Liste gewählt werden.', 'The region must be chosen from the list.'),
 ('PRUEF_PRAEFIX', 'Das MQTT-Präfix darf nur Buchstaben, Ziffern, Punkt, Strich, Unterstrich und Schrägstriche enthalten - kein # und kein +, und es beginnt und endet nicht mit einem Schrägstrich.', 'The MQTT prefix may only contain letters, digits, dot, dash, underscore and slashes - no # and no +, and it does not start or end with a slash.'),
 ('PRUEF_IP', 'Die IP-Adresse des LoxBerry ist keine gültige Adresse.', 'The IP address of the LoxBerry is not a valid address.'),
 ('PRUEF_UNBEKANNT', 'Die Einstellung %s ist unbekannt.', 'The setting %s is unknown.'),
 ('PRUEF_GERAETE_ID', 'Die Gerätenummer %s ist keine gültige Nummer.', 'The device number %s is not a valid number.'),
 ('PRUEF_BEZEICHNUNG', 'Die Bezeichnung für Gerät %s ist unbrauchbar oder zu lang.', 'The label for device %s is unusable or too long.'),

 # --- Dienstzustand ---
 ('DIENST_STARTEN', 'Dienst starten', 'Start service'),
 ('DIENST_NEU_STARTEN', 'Dienst neu starten', 'Restart service'),
 ('DIENST_ANHALTEN', 'Dienst anhalten', 'Stop service'),
 ('DIENST_LAEUFT_PID', 'Der Dienst läuft (PID %s).', 'The service is running (PID %s).'),
 ('DIENST_GESTOPPT_SIEHE', 'Der Dienst ist gestoppt - siehe Reiter %s.', 'The service is stopped - see the %s tab.'),
 ('DIENST_LAEUFT_NICHT', 'Der Dienst läuft nicht - über einen Herzschlag ist damit nichts zu sagen.', 'The service is not running - nothing can be said about a heartbeat.'),
 ('KEIN_LEBENSZEICHEN', 'Es liegt noch kein Lebenszeichen vor. Nach spätestens einer Minute sollte eines da sein.', 'No heartbeat yet. One should appear within a minute.'),
 ('HERZSCHLAG_ALTER', 'vor %d s, Zähler %s, letzter Durchgang ok=%s', '%d s ago, counter %s, last cycle ok=%s'),
 ('HERZSCHLAG_OHNE_DURCHGANG', 'vor %d s, Zähler %d - noch kein Gerätedurchgang, das ist kein Fehler', '%d s ago, counter %d - no device cycle yet, that is not an error'),
 ('HERZSCHLAG_OHNE_DURCHGANG_ROH', 'vor %d s, Zähler %d, noch kein Gerätedurchgang', '%d s ago, counter %d, no device cycle yet'),
 ('HERZSCHLAG_ALTER_ROH', 'vor %d s, Zähler %s, ok=%s', '%d s ago, counter %s, ok=%s'),
 ('LAEUFT_PID', 'läuft, PID %s', 'running, PID %s'),
 ('GESTOPPT', 'gestoppt', 'stopped'),
 ('SOLL_JA', 'Ja - der Merker soll_laufen liegt.', 'Yes - the marker soll_laufen is present.'),
 ('SOLL_NEIN', 'Nein - der Dienst ist bewusst angehalten. Der Knopf Dienst starten legt den Merker wieder an.', 'No - the service has been stopped on purpose. The button Start service creates the marker again.'),
 ('MARKE_JA', 'Ja - seit %d Sekunden. Solange wird kein Dienst gestartet.', 'Yes - for %d seconds. No service is started while it lasts.'),
 ('MARKE_NEIN', 'Nein - es liegt keine Marke.', 'No - there is no marker.'),
 ('MARKE_ALT', 'Nein - es liegt eine Marke, die nicht mehr gilt (%s). Sie stört nicht und wird beim nächsten Update überschrieben.', 'No - there is a marker that no longer counts (%s). It does no harm and is overwritten by the next update.'),
 ('MSMART_NG', 'msmart-ng', 'msmart-ng'),
 ('PYTHON', 'Python', 'Python'),
 ('UNBEKANNT', 'unbekannt', 'unknown'),
 ('VORHANDEN', 'vorhanden', 'present'),
 ('NICHT_LADBAR', 'nicht ladbar - bitte das Plugin neu installieren', 'cannot be loaded - please reinstall the plugin'),
 ('VENV_FEHLT', 'Die virtuelle Python-Umgebung fehlt (%s). Bitte das Plugin neu installieren.', 'The Python virtual environment is missing (%s). Please reinstall the plugin.'),
 ('FASSUNG_IST', 'Fassung %s', 'version %s'),

 # --- Konfigurationslage ---
 ('LAGE_OK', 'vollständig und lesbar', 'complete and readable'),
 ('LAGE_FEHLT', 'Die Datei midea2lox.cfg gibt es nicht. Bitte einmal speichern.', 'The file midea2lox.cfg does not exist. Please save once.'),
 ('LAGE_LEER', 'Die Datei midea2lox.cfg ist leer. Bitte einmal speichern.', 'The file midea2lox.cfg is empty. Please save once.'),
 ('LAGE_KAPUTT', 'Die Datei midea2lox.cfg lässt sich nicht lesen - der Abschnitt [default] fehlt oder die Datei ist beschädigt.', 'The file midea2lox.cfg cannot be read - the [default] section is missing or the file is damaged.'),
 ('LAGE_UNVOLLSTAENDIG', 'Es fehlen Schlüssel: %s. Sie werden beim nächsten Aufruf ergänzt.', 'Keys are missing: %s. They will be added on the next page load.'),

 # --- Felder ---
 ('MINISERVER', 'Miniserver', 'Miniserver'),
 ('UDP_PORT', 'UDP-Port', 'UDP port'),
 ('UDP_PORT_HILFE', 'Auf diesem Port nimmt der Dienst Befehle aus Loxone per UDP entgegen (bestehende Anlagen; neu: Befehle über MQTT, Reiter MQTT). Er muss mit der Adresse des virtuellen Ausgangs übereinstimmen.', 'On this port the service accepts commands from Loxone via UDP (existing installations; new: commands via MQTT, tab MQTT). It must match the address of the virtual output.'),
 ('LOX_TIMEOUT', 'Wartezeit auf den Miniserver (Sekunden)', 'Miniserver timeout (seconds)'),
 ('LOX_TIMEOUT_HILFE', 'Länger als hier eingestellt wartet das Plugin nicht auf eine Antwort des Miniservers. Ohne Grenze stünde der ganze Dienst, sobald der Miniserver hängt.', 'The plugin waits no longer than this for an answer from the Miniserver. Without a limit the whole service would stall as soon as the Miniserver hangs.'),
 ('BENUTZER', 'Benutzer (E-Mail-Adresse)', 'User (e-mail address)'),
 ('PASSWORT', 'Passwort', 'Password'),
 ('PASSWORT_GESETZT', 'gespeichert - leer lassen, um es zu behalten', 'stored - leave empty to keep it'),
 ('PASSWORT_LEER', 'noch nicht gesetzt', 'not set yet'),
 ('PASSWORT_LOESCHEN', 'Gespeichertes Passwort löschen', 'Delete the stored password'),
 ('KONTO_ERKLAERUNG', 'Dieselben Zugangsdaten wie in der Hersteller-App (SmartHome oder NetHome Plus). Sie werden <b>nur bei der Gerätesuche</b> gebraucht, um für Geräte mit Protokoll V3 Token und Schlüssel abzuholen; danach läuft alles im eigenen Netz. <b>Ohne eigenes Konto geht es auch</b> - msmart-ng benutzt dann seine Sammelkonten. Ein eigenes Konto hilft, wenn die Suche für ein V3-Gerät keinen Token liefert.', 'The same credentials as in the manufacturer app (SmartHome or NetHome Plus). They are needed <b>only for the device search</b>, to fetch token and key for protocol V3 devices; afterwards everything runs on the local network. <b>It also works without your own account</b> - msmart-ng then uses its shared accounts. Your own account helps when the search returns no token for a V3 device.'),
 ('REGION', 'Region des Kontos', 'Region of the account'),
 ('REGION_SERVER', 'Server %s', 'server %s'),
 ('REGION_HILFE', 'msmart-ng kennt drei Serverbereiche: DE, KR und US. Die europäischen Länder gehen alle über den Server DE. Ohne Angabe würde msmart-ng den Server US nehmen - für ein europäisches Konto der falsche.', 'msmart-ng knows three server areas: DE, KR and US. All European countries use the DE server. Without a setting msmart-ng would use the US server - the wrong one for a European account.'),
 ('ABFRAGETAKT', 'Abfragetakt (Sekunden, 0 = aus)', 'Polling interval (seconds, 0 = off)'),
 ('ABFRAGETAKT_HILFE', 'Ab Werk aus. Steht hier eine Zahl, fragt das Plugin von sich aus alle Geräte in diesem Takt ab, ohne dass Loxone etwas schicken muss. Untergrenze 30 Sekunden. Wer den Takt schon in Loxone gebaut hat, lässt das Feld auf 0 - sonst wird jedes Gerät doppelt abgefragt.', 'Off by default. With a number here the plugin polls all devices at this interval on its own, without Loxone having to send anything. Lower limit 30 seconds. If you already built the cycle in Loxone, leave this at 0 - otherwise every device is polled twice.'),
 ('LEBENSDAUER', 'Verbindungsdauer je Gerät (Sekunden)', 'Connection lifetime per device (seconds)'),
 ('LEBENSDAUER_HILFE', 'Nach dieser Zeit baut das Plugin die Verbindung zum Klimagerät neu auf.', 'After this time the plugin rebuilds the connection to the air conditioner.'),
 ('DEBUG', 'Ausführliches Protokoll', 'Verbose log'),
 ('DEBUG_HILFE', 'Nur zur Fehlersuche einschalten. Die Logdatei wächst damit deutlich schneller.', 'Switch on for troubleshooting only. The log file grows much faster.'),
 ('EIN', 'ein', 'on'),
 ('AUS', 'aus', 'off'),
 ('JA', 'ja', 'yes'),
 ('OHNE', 'ohne', 'none'),
 ('SPEICHERN_NEUSTART', 'Speichern und Dienst neu starten', 'Save and restart service'),
 ('SPEICHERN_SUCHEN', 'Speichern und Geräte suchen', 'Save and search for devices'),

 # --- Geraete ---
 ('KLIMAGERAET', 'Klimagerät', 'Air conditioner'),
 ('GERAETE_ID', 'Geräte-Nummer', 'Device number'),
 ('IP_ADRESSE', 'IP-Adresse', 'IP address'),
 ('PROTOKOLL', 'Protokoll', 'Protocol'),
 ('PROTOKOLL_V2', 'V2 (ohne Token)', 'V2 (no token)'),
 ('PROTOKOLL_V3', 'V3 (mit Token)', 'V3 (with token)'),
 ('BEZEICHNUNG', 'Bezeichnung', 'Label'),
 ('BEZ_SPEICHERN', 'Bezeichnungen speichern', 'Save labels'),
 ('KEINE_GERAETE', 'Es sind noch keine Klimageräte hinterlegt. Bitte im Reiter Test auf <i>Jetzt nach Geräten suchen</i> drücken.', 'No air conditioners have been configured yet. Please press <i>Search for devices now</i> in the Test tab.'),
 ('GERAETE_DATEI', 'Die Liste steht in', 'The list is stored in'),
 ('GERAETE_UEBERLEBT', 'und übersteht Updates.', 'and survives updates.'),
 ('GERAETE_ANZAHL', '%d Gerät(e)', '%d device(s)'),
 ('GERAETE_KEINE', 'keine - bitte suchen lassen', 'none - please run a search'),

 # --- Konto in der Selbstpruefung ---
 ('KONTO_EIGEN', 'eigenes Konto %s', 'own account %s'),
 ('KONTO_SAMMEL', 'kein eigenes Konto - es gelten die Sammelkonten von msmart-ng. Das genügt in aller Regel.', 'no own account - the shared accounts of msmart-ng apply. That is usually enough.'),
 ('KONTO_HALB', 'Es ist nur eines von beiden eingetragen. msmart-ng verlangt Benutzer UND Passwort zusammen, sonst weist es die Suche ab. Bitte beides eintragen oder beides leeren.', 'Only one of the two is set. msmart-ng requires user AND password together, otherwise it rejects the search. Please enter both or clear both.'),
 ('REGION_ZUORDNUNG', '%s wird auf den Serverbereich %s abgebildet', '%s is mapped to server area %s'),

 # --- MQTT ---
 ('H_MQTT_ZUSTAND', 'Zustand des MQTT-Gateways', 'State of the MQTT gateway'),
 ('H_MQTT_EINSTELLUNGEN', 'Einstellungen', 'Settings'),
 ('H_ABO', 'Das Abo im MQTT-Gateway', 'The subscription in the MQTT gateway'),
 ('H_THEMEN', 'Veröffentlichte Themen', 'Published topics'),
 ('MQTT_SYSTEMBESTANDTEIL', 'Das MQTT-Gateway ist seit LoxBerry 3 <b>Bestandteil des Systems</b> und kein Plugin. Es wird unter <i>System → MQTT Gateway</i> eingerichtet (<span class=\'sm-mono\'>/admin/system/mqtt.cgi</span>).', 'Since LoxBerry 3 the MQTT gateway is <b>part of the system</b> and not a plugin. It is configured under <i>System → MQTT Gateway</i> (<span class=\'sm-mono\'>/admin/system/mqtt.cgi</span>).'),
 ('MQTT_UNLESBAR', 'Die Systemkonfiguration <span class=\'sm-mono\'>config/system/general.json</span> ist nicht lesbar. Der UDP-Weg funktioniert trotzdem.', 'The system configuration <span class=\'sm-mono\'>config/system/general.json</span> is not readable. The UDP path still works.'),
 ('GROESSE', 'Größe', 'Item'),
 ('WERT', 'Wert', 'Value'),
 ('BROKER', 'Broker', 'Broker'),
 ('BROKER_FREMD', 'nein - es wird ein fremder Broker verwendet', 'no - an external broker is used'),
 ('EIGENER_BROKER', 'Eigener Broker auf dem LoxBerry', 'Own broker on the LoxBerry'),
 ('GATEWAY_AUTOSTART', 'Gateway startet automatisch', 'Gateway starts automatically'),
 ('AUTOSTART_AUS', 'nein - nach einem Neustart kommt nichts an', 'no - after a reboot nothing arrives'),
 ('MQTT_PRAEFIX', 'Themen-Präfix', 'Topic prefix'),
 ('MQTT_PRAEFIX_HILFE', 'Der erste Teil jedes Themas. Beim Ändern wird die mitgelieferte Abo-Datei mitgeschrieben - und in Loxone müssen die virtuellen Eingänge umbenannt werden, denn das Gateway ordnet ausschließlich über den Namen zu.', 'The first part of every topic. When you change it the shipped subscription file is updated as well - and in Loxone the virtual inputs have to be renamed, because the gateway matches by name only.'),
 ('MQTT_SPEICHERN', 'MQTT speichern und Dienst neu starten', 'Save MQTT and restart service'),
 ('ABO_UNBEKANNT', 'Welche Fassung Ihr MQTT-Gateway hat, ließ sich nicht feststellen. <b>Fassung 1:</b> ohne diesen Eintrag kommt am Miniserver nichts an. <b>Fassung 2 und neuer:</b> die Themengruppe erscheint von selbst in den Subscriptions, einzutragen ist nichts.', 'The version of your MQTT gateway could not be determined. <b>Version 1:</b> without this entry nothing arrives at the Miniserver. <b>Version 2 and newer:</b> the topic group appears by itself under Subscriptions, nothing needs to be entered.'),
 ('ABO_V2', '<b>MQTT-Gateway V2 erkennt die Themengruppe von selbst</b> - einzutragen ist hier nichts. In den <i>Subscriptions</i> erscheint die Gruppe; dort werden die gewünschten Datenpunkte einzeln angehakt. Erscheint sie nicht, hat noch nichts veröffentlicht.', '<b>MQTT gateway V2 detects the topic group by itself</b> - nothing needs to be entered here. The group appears under <i>Subscriptions</i>; tick the data points you want there. If it does not appear, nothing has been published yet.'),
 ('OHNE_DIESEN_EINTRAG_KOMMT_AM', 'Ohne diesen Eintrag kommt am Miniserver nichts an.', 'Without this entry nothing arrives at the Miniserver.'),
 ('ABO_GEMESSEN', '(gemessen: Gateway V%d)', '(measured: gateway V%d)'),
 ('ABO_MITGELIEFERT', "Das Plugin liefert diesen Eintrag in <span class='sm-mono'>config/plugins/Midea2Lox/mqtt_subscriptions.cfg</span> mit, und <b>das Gateway liest ihn</b>: am Gerät belegt (13.09.2026, Gateway V1) im Quelltext und am laufenden Gateway. In der Abo-Liste der Oberfläche taucht er trotzdem nicht auf - Plugin-Abos hält das Gateway nur im Arbeitsspeicher. Sie müssen also in aller Regel <b>nichts</b> von Hand eintragen. Ob es wirklich trägt, sagt die Zeile <i>Ist unser Thema im Gateway abonniert?</i> im Reiter Test.", "The plugin ships this entry in <span class='sm-mono'>config/plugins/Midea2Lox/mqtt_subscriptions.cfg</span>, and <b>the gateway reads it</b>: measured on the device (2026-09-13, gateway V1) both in its source and on the running gateway. It still does not show up in the subscription list of the web interface - plugin subscriptions are kept in memory only. So as a rule you need to enter <b>nothing</b> by hand. Whether it really holds is answered by the line <i>Is our topic subscribed in the gateway?</i> in the Test tab."),
 ('ABO_DATEI_FEHLT', 'Die Datei <span class=\'sm-mono\'>mqtt_subscriptions.cfg</span> fehlt. Sie wird beim nächsten Speichern im Reiter MQTT neu angelegt.', 'The file <span class=\'sm-mono\'>mqtt_subscriptions.cfg</span> is missing. It will be recreated the next time you save in the MQTT tab.'),
 ('ABO_DATEI_ABWEICHEND', 'Die mitgelieferte Abo-Datei enthält <span class=\'sm-mono\'>%s</span>, zum eingestellten Präfix gehört aber <span class=\'sm-mono\'>%s</span>. Einmal im Reiter MQTT speichern bringt beides wieder zusammen.', 'The shipped subscription file contains <span class=\'sm-mono\'>%s</span>, but the configured prefix requires <span class=\'sm-mono\'>%s</span>. Saving once in the MQTT tab brings both back together.'),
 ('ABO_LISTE_UNLESBAR', "Die Abonnementliste des Gateways ist nicht lesbar (gesucht in <span class='sm-mono'>config/system/mqttgateway.json</span>, danach in <span class='sm-mono'>config/system/subscriptions.json</span>).", "The subscription list of the gateway is not readable (looked for <span class='sm-mono'>config/system/mqttgateway.json</span>, then <span class='sm-mono'>config/system/subscriptions.json</span>)."),
 ('ABO_LISTE_LEER', 'Das Gateway hat noch gar kein Abonnement - damit ist die Frage nicht beantwortet, sondern offen.', 'The gateway has no subscription at all - so the question is not answered but open.'),
 ('ABO_EINGETRAGEN_JA', 'ja: %s (von %d Abonnements insgesamt)', 'yes: %s (of %d subscriptions in total)'),
 ('ABO_EINGETRAGEN_NEIN', 'nein - unter den %2$d Abonnements des Gateways ist keines, das mit %1$s beginnt. Bitte im Reiter MQTT nachlesen und dort von Hand eintragen.', 'no - none of the %2$d subscriptions of the gateway starts with %1$s. Please read the MQTT tab and enter it there by hand.'),
 ('THEMA', 'Thema', 'Topic'),
 ('EINHEIT', 'Einheit', 'Unit'),
 ('BEDEUTUNG', 'Bedeutung', 'Meaning'),
 ('GRUPPE_GRUND', 'Grundwerte', 'Basic values'),
 ('GRUPPE_KOMFORT', 'Komfort und Zusatzfunktionen', 'Comfort and extra functions'),
 ('GRUPPE_ENERGIE', 'Energie', 'Energy'),
 ('GRUPPE_STATUS', 'Lebenszeichen des Plugins', 'Heartbeat of the plugin'),
 ('STATUS_ERKLAERUNG', 'Diese Themen gelten für das Plugin, nicht für ein einzelnes Gerät. Sie beantworten die Frage, die ein virtueller Eingang von sich aus nicht beantwortet: <b>ist der Wert von eben, oder steht er seit dem Ausfall still?</b> Ein virtueller Eingang behält seinen letzten Wert, mit Retain sogar über einen Neustart des Miniservers hinweg - ohne Lebenszeichen sieht ein toter Dienst in der App aus wie ein ruhiger.', 'These topics apply to the plugin, not to a single device. They answer the question a virtual input cannot answer by itself: <b>is the value current, or has it been standing still since the failure?</b> A virtual input keeps its last value, with retain even across a restart of the Miniserver - without a sign of life a dead service looks like a quiet one in the app.'),
 ('THEMEN_OHNE_GERAETE', 'Sobald Geräte hinterlegt sind, entstehen die Themen nach dem Muster <span class=\'sm-mono\'>%s/&lt;Geräte-Nummer&gt;/&lt;Wert&gt;</span>.', 'As soon as devices are configured, topics follow the pattern <span class=\'sm-mono\'>%s/&lt;device number&gt;/&lt;value&gt;</span>.'),
 ('MQTT_REGELWEG', 'MQTT ist der Regelweg.', 'MQTT is the standard path.'),
 ('UDP_AUSWEICHWEG', 'Ist kein Broker erreichbar, sendet der Dienst per HTTP an virtuelle Eingänge des Miniservers - mit den Namen aus dem Reiter Einbindung in Loxone (Unterstrich statt Schrägstrich).', 'If no broker can be reached, the service sends via HTTP to virtual inputs of the Miniserver - with the names from the Loxone integration tab (underscore instead of slash).'),

 # --- Einbindung in Loxone ---
 ('H_EINBINDUNG', 'Einbindung in Loxone, Schritt für Schritt', 'Loxone integration, step by step'),
 ('EINBINDUNG_EINLEITUNG', 'Das Musterprojekt liest die Werte über das MQTT-Gateway in einfache <b>Virtuelle Eingänge</b> und gibt Befehle über <b>MQTT</b> an das Plugin (Haken „Befehle über MQTT annehmen“ im Reiter MQTT). Eine Vorlage mit Virtuellen HTTP-Eingängen gibt es nicht mehr. Der UDP-Befehlseingang (Port %s) bleibt für bestehende Anlagen; seine Vorlage steht unten zugeklappt.', 'The sample project reads the values via the MQTT gateway into plain <b>Virtual Inputs</b> and sends commands to the plugin via <b>MQTT</b> (tick “Accept commands via MQTT” in the tab MQTT). There is no template with Virtual HTTP Inputs any more. The UDP command input (port %s) stays for existing installations; its template is collapsed below.'),
 ('EINBINDUNG_OHNE_GERAETE', '<b>Es sind noch keine Geräte hinterlegt.</b> Die Beispiele unten benutzen deshalb die Platzhalter-Nummer %s. Bitte zuerst im Reiter Test nach Geräten suchen lassen - danach stehen hier die echten Nummern.', '<b>No devices are configured yet.</b> The examples below therefore use the placeholder number %s. Please run a device search in the Test tab first - afterwards the real numbers appear here.'),
 ('SCHRITT1', 'Schritt 1: Der Weg der Werte – MQTT', 'Step 1: the path of the values – MQTT'),
 ('SCHRITT1_TEXT', '<b>MQTT</b> ist der Weg: der Dienst meldet den Zustand der Klimageräte an den Broker, das MQTT-Gateway reicht ihn an Loxone weiter, und Befehle kommen über MQTT zurück. Das Gateway ist seit LoxBerry 3 Bestandteil des Systems und muss nicht nachinstalliert werden. <b>Das Plugin sendet nicht beides</b>: ist kein Broker erreichbar, schreibt der Dienst die Werte per HTTP an virtuelle Eingänge des Miniservers mit denselben Namen (Rückfallweg, im Musterprojekt nicht gebaut).', '<b>MQTT</b> is the way: the service reports the state of the air conditioners to the broker, the MQTT gateway passes it on to Loxone, and commands come back via MQTT. The gateway has been part of the system since LoxBerry 3 and does not need to be installed. <b>The plugin does not send both</b>: if no broker can be reached, the service writes the values via HTTP to virtual inputs of the Miniserver with the same names (fallback, not built in the sample project).'),
 ('SCHRITT2', 'Schritt 2: Abo im MQTT-Gateway', 'Step 2: subscription in the MQTT gateway'),
 ('SCHRITT2_TEXT', 'Fassung 1 des MQTT-Gateways: das Abo bringt das Plugin mit (config/mqtt_subscriptions.cfg). Fassung 2: die Themen mit „V2“ in der Namenstabelle (Schritt 3) anhaken, status/ok und online zusätzlich „Noncached“.', 'Version 1 of the MQTT gateway: the plugin brings the subscription (config/mqtt_subscriptions.cfg). Version 2: tick the topics marked “V2” in the name table (step 3), status/ok and online additionally “Noncached”.'),
 ('SCHRITT3', 'Schritt 3: Virtuelle Eingänge anlegen', 'Step 3: create virtual inputs'),
 ('SCHRITT3_TEXT', 'In <b>Loxone Config</b> unter <i>Virtuelle Eingänge</i> je Zahlenwert einen <b>Virtuellen Eingang</b> mit genau dem Namen aus der Tabelle, „Als Digitaleingang“ nicht anhaken; je Text einen <i>Virtuellen Texteingang</i>, „In Visualisierung verwenden“ an. <b>Der Name muss exakt stimmen</b> – das Gateway ordnet ausschließlich über den Namen zu. Der LoxBerry-Benutzer braucht Rechte im Miniserver.', 'In <b>Loxone Config</b> under <i>Virtual Inputs</i> create one <b>Virtual Input</b> per number with exactly the name from the table, do not tick “Use as digital input”; per text a <i>Virtual Text Input</i>, “Use in User Interface” on. <b>The name must match exactly</b> – the gateway assigns solely by name. The LoxBerry user needs rights in the Miniserver.'),
 ('UDP_WEG', "Port <b>%s</b> ist der <b>UDP-Befehlsport</b> des Dienstes (Absenderfilter: nur die Miniserver und der LoxBerry selbst). Die Werte kommen immer über das MQTT-Gateway (Abo <span class='sm-mono'>%s/#</span>); einen virtuellen UDP-Eingang braucht es nicht.", "Port <b>%s</b> is the <b>UDP command port</b> of the service (sender filter: only the Miniservers and the LoxBerry itself). The values always arrive via the MQTT gateway (subscription <span class='sm-mono'>%s/#</span>); no virtual UDP input is needed."),
 ('K_VORLAGE_AUS', 'Vorlage Ausgang (UDP)', 'Template output (UDP)'),
 ('VORLAGE_WARNUNG', '<b>Achtung:</b> Loxone Config legt beim Import immer neu an und überschreibt nichts. Zweimal eingelesen ergibt doppelte Bausteine, und das fällt niemandem auf.', '<b>Note:</b> Loxone Config always creates new objects on import and overwrites nothing. Importing twice yields duplicate blocks, and nobody notices.'),
 ('SCHRITT4', 'Schritt 4: Befehle an das Klimagerät', 'Step 4: commands to the air conditioner'),
 ('SCHRITT4_TEXT', 'Zum Schalten einen <i>virtuellen Ausgang</i> anlegen. Adresse - %s ist der LoxBerry, %s der eingestellte UDP-Port:', 'To switch, create a <i>virtual output</i>. Address - %s is the LoxBerry, %s the configured UDP port:'),
 ('SCHRITT4_TEXT2', 'Darunter je Befehl einen <i>virtuellen Ausgang Befehl</i>. Der Befehlstext besteht aus der Geräte-Nummer, einem <b>Leerzeichen</b> und dem Befehl:', 'Below it add one <i>virtual output command</i> per command. The command text consists of the device number, a <b>space</b> and the command:'),
 ('SCHRITT4_TEMP', "<b>Solltemperatur und Sollfeuchte stufenlos:</b> der Befehl schickt <span class='sm-mono'>temp.&lt;v.1&gt;</span> bzw. <span class='sm-mono'>humidity.&lt;v.0&gt;</span>; der angeschlossene Analogwert setzt die Temperatur (halbe Grad gehen, zum Beispiel <span class='sm-mono'>temp.20.5</span>) bzw. die Sollfeuchte in ganzen Prozent. Bis 4.5.14 stand im Temperaturbefehl <span class='sm-mono'>&lt;v&gt;</span> - halbe Grad und einstellige Werte verwarf der Dienst. Wer die Befehlsvorlage früher importiert hat, ändert den Befehl von Hand oder importiert sie neu.", "<b>Continuous target temperature and target humidity:</b> the command sends <span class='sm-mono'>temp.&lt;v.1&gt;</span> or <span class='sm-mono'>humidity.&lt;v.0&gt;</span>; the connected analogue value sets the temperature (half degrees work, for example <span class='sm-mono'>temp.20.5</span>) or the target humidity in whole percent. Up to 4.5.14 the temperature command carried <span class='sm-mono'>&lt;v&gt;</span> - the service discarded half degrees and single-digit values. Whoever imported the command template earlier changes the command by hand or imports it again."),
 ('WAS', 'Was', 'What'),
 ('BEFEHL_EIN', 'Befehl bei Ein', 'Command for on'),
 ('BEFEHL_AUS', 'Befehl bei Aus', 'Command for off'),
 ('SCHRITT5', 'Schritt 5: Ausfallerkennung', 'Step 5: failure detection'),
 ('SCHRITT5_TEXT', "Fällt etwas aus, behält ein Virtueller Eingang seinen <b>letzten Wert</b>. Für das Plugin zählt das Lebenszeichen <span class='sm-mono'>status_zaehler</span> jede Minute weiter – eine Analogwertvalidierung (Tmc 300 s, fünfmal der Herzschlag) meldet, wenn es steht. Für das Gerät gibt es <span class='sm-mono'>online</span> (nur mit Abfragetakt, Reiter Einstellungen 60 s); <span class='sm-mono'>status_ok</span> und <span class='sm-mono'>online</span> unter Gateway V2 als „Noncached“. <span class='sm-mono'>status_ts</span> nicht verwenden (Ortszeit). Siehe „Lebenszeichen fehlt (Midea)“ auf der Seite „Midea2Lox“ in Schritt 6.", "If something fails, a Virtual Input keeps its <b>last value</b>. For the plugin the sign of life <span class='sm-mono'>status_zaehler</span> counts up every minute – a value validator (Tmc 300 s, five heartbeats) reports when it stops. For the device there is <span class='sm-mono'>online</span> (only with a polling interval, tab Settings 60 s); <span class='sm-mono'>status_ok</span> and <span class='sm-mono'>online</span> as “Noncached” under gateway V2. Do not use <span class='sm-mono'>status_ts</span> (local time). See “Lebenszeichen fehlt (Midea)” on page “Midea2Lox” in step 6."),
 ('SCHRITT6', 'Schritt 6: Drei fertige Seiten aus dem Musterprojekt', 'Step 6: three ready-made pages from the sample project'),
 ('SCHRITT6_TEXT', 'Die drei Seiten des LoxBerry-Plugins Musterprojekts für <b>ein</b> Klimagerät: „Midea2Lox“ (läuft es, ein/aus mit Fenster- und Abwesenheitssperre, Solltemperatur, Automatik), „Midea2Lox Betrieb“ (Betriebsart, Lüfterstufe, Schwenken, Sollfeuchte) und „Midea2Lox Komfort und Energie“ (Sonderfunktionen, Filter, Leistung und Energie). Je Seite eine Anleitung zum Übernehmen, die Tabelle, Hinweise und ein Bild. Wer die Tabelle von oben nach unten abarbeitet, hat die Seite nachgebaut; die Bausteine findet man in Loxone Config über die Baustein-Suche (F5). Die Namen der Eingänge und Befehle stehen hier mit dem eingestellten Präfix und der Nummer des ersten Geräts.', 'The three pages of the LoxBerry plugins sample project for <b>one</b> air conditioner: “Midea2Lox” (is it running, on/off with window and absence lock, target temperature, automation), “Midea2Lox Betrieb” (operating mode, fan speed, swing, target humidity) and “Midea2Lox Komfort und Energie” (special functions, filter, power and energy). For each page instructions for taking it over, the table, notes and a picture. Working through the table from top to bottom rebuilds the page; the blocks can be found in Loxone Config via the block search (F5). The names of the inputs and commands are shown here with the configured prefix and the number of the first device.'),
 ('BAUSTEIN_TYP', 'Baustein (Typ)', 'Block (type)'),
 ('NAME_VORSCHLAG', 'Name', 'Name'),
 ('PARAMETER', 'Parameter', 'Parameters'),
 ('EINGAENGE', 'Eingänge verbinden mit', 'Connect inputs to'),
 ('SCHRITT7', 'Schritt 7: Gegenprobe', 'Step 7: verification'),
 ('SCHRITT7_TEXT', 'Nach dem Speichern in Loxone im Reiter Test auf <i>Zustand aller Geräte abfragen</i> klicken. Erscheinen dort Werte, sendet das Plugin. Kommt in Loxone trotzdem nichts an, liegt es am Abo oder am Namen eines virtuellen Eingangs - beides steht in Schritt 2 und 3.', 'After saving in Loxone, click <i>Query the state of all devices</i> in the Test tab. If values appear there, the plugin is sending. If nothing arrives in Loxone anyway, it is either the subscription or the name of a virtual input - both are covered in steps 2 and 3.'),

 # --- Reiter Test ---
 ('FRAGE', 'Frage', 'Question'),
 ('ANTWORT', 'Antwort', 'Answer'),
 ('H_NACHSEHEN', 'Nachsehen', 'Inspect'),
 ('H_SCHALTEN', 'Schalten', 'Switch'),
 ('H_GERAETESUCHE', 'Gerätesuche', 'Device search'),
 ('K_UMGEBUNG', 'Umgebung prüfen', 'Check environment'),
 ('K_STATUS', 'Zustand aller Geräte abfragen', 'Query the state of all devices'),
 ('K_THEMEN', 'Themenliste gegen den Dienst halten', 'Compare topic list against the service'),
 ('K_SUCHEN', 'Jetzt nach Geräten suchen', 'Search for devices now'),
 ('K_TROCKEN', 'Trockenlauf - nur anzeigen', 'Dry run - show only'),
 ('K_SENDEN', 'Befehl jetzt senden', 'Send command now'),
 ('SCHALTEN_WARNUNG', '<b>Diese Knöpfe wirken sofort.</b> Der Befehl geht über denselben Weg wie ein Befehl aus Loxone - was hier funktioniert, funktioniert dort. Der Trockenlauf daneben zeigt nur, was gesendet würde.', '<b>These buttons take effect immediately.</b> The command travels the same path as a command from Loxone - what works here works there. The dry run next to it only shows what would be sent.'),
 ('SCHALT_GERAET', 'Gerät', 'Device'),
 ('SCHALT_BEFEHL', 'Befehl', 'Command'),
 ('SCHALT_ID_UNBEKANNT', 'Diese Geräte-Nummer ist nicht hinterlegt. Es wurde nichts gesendet.', 'This device number is not configured. Nothing was sent.'),
 ('SCHALT_BEFEHL_UNBEKANNT', 'Dieser Befehl steht nicht in der Liste. Es wurde nichts gesendet.', 'This command is not in the list. Nothing was sent.'),
 ('SCHALT_ZIEL', 'Ziel: %s Port %d', 'Target: %s port %d'),
 ('SCHALT_PAKET', 'Paket:', 'Packet:'),
 ('SCHALT_TROCKEN_HINWEIS', 'Trockenlauf - es wurde nichts gesendet.', 'Dry run - nothing was sent.'),
 ('SCHALT_GESENDET', 'Gesendet, %d Byte.', 'Sent, %d bytes.'),
 ('SCHALT_NICHT_GESENDET', 'Das Paket ließ sich nicht schreiben.', 'The packet could not be written.'),
 ('SCHALT_FEHLER', 'Die Verbindung kam nicht zustande (%d): %s', 'The connection could not be established (%d): %s'),
 ('SCHALT_NACHSEHEN', 'UDP bestätigt nichts. Ob der Befehl angekommen ist, steht im Reiter Logdateien. (Befehle über MQTT quittiert das Plugin unter …/quittung.)', 'UDP confirms nothing. Whether the command arrived is shown in the tab Log files. (Commands via MQTT are acknowledged by the plugin under …/quittung.)'),
 ('GERAETESUCHE_TEXT', 'Spricht mit dem Midea-Konto und schreibt das Ergebnis nach devices.cfg. Das dauert bis zu einer Minute.', 'Talks to the Midea account and writes the result to devices.cfg. This takes up to a minute.'),
 ('T_SUCHE', 'Gerätesuche', 'Device search'),
 ('T_STATUS', 'Zustand aller Geräte', 'State of all devices'),
 ('T_THEMEN', 'Themenliste gegen den Dienst', 'Topic list against the service'),
 ('T_UMGEBUNG', 'Umgebung', 'Environment'),
 ('T_TROCKEN', 'Trockenlauf', 'Dry run'),
 ('T_SCHALTEN', 'Befehl gesendet', 'Command sent'),
 ('T_UNBEKANNT', 'Unbekannte Prüfung', 'Unknown check'),
 ('T_UNBEKANNT_TEXT', 'Diese Prüfung gibt es nicht.', 'This check does not exist.'),
 ('DISCOVER_FEHLT', 'discover.py wurde nicht gefunden (%s).', 'discover.py was not found (%s).'),
 ('DISCOVER_ABBRUCH', 'Die Gerätesuche wurde mit Rückgabewert %d abgebrochen. Eine leere Ausgabe ist hier kein Erfolg, sondern das Gegenteil.', 'The device search aborted with exit code %d. An empty output here is not a success but the opposite.'),
 ('DISCOVER_OHNE_AUSGABE', 'Die Gerätesuche hat nichts ausgegeben.', 'The device search produced no output.'),
 ('STATUS_KEINE_GERAETE', 'Es sind keine Geräte hinterlegt. Bitte zuerst nach Geräten suchen lassen.', 'No devices are configured. Please run a device search first.'),
 ('STATUS_HINTERLEGT', 'Hinterlegte Geräte:', 'Configured devices:'),
 ('STATUS_LEBENSZEICHEN', 'Lebenszeichen:', 'Heartbeat:'),
 ('STATUS_LETZTE_ZEILEN', 'Letzte Zeilen aus midea2lox.log:', 'Last lines from midea2lox.log:'),
 ('STATUS_KEIN_LOG', 'Es gibt noch keine Logdatei. Läuft der Dienst?', 'There is no log file yet. Is the service running?'),
 ('THEMEN_ZAHLEN', '%d gesendet, %d in der Tabelle', '%d sent, %d in the table'),
 ('THEMEN_ZAHLEN_ROH', 'Der Dienst sendet %d Themen je Gerät, die Tabelle nennt %d.', 'The service sends %d topics per device, the table lists %d.'),
 ('THEMEN_DECKUNGSGLEICH', 'Beide Listen sind deckungsgleich.', 'Both lists match.'),
 ('THEMEN_ABWEICHEND', 'Diese Namen stehen nur auf einer der beiden Seiten:', 'These names appear on only one of the two sides:'),
 ('DIENST_NICHT_LESBAR', 'Der Quelltext des Dienstes ist nicht lesbar - die Zahlen ließen sich nicht vergleichen.', 'The source of the service is not readable - the numbers could not be compared.'),
 ('REITER_ZAHLEN', 'Positivliste %d, Verweise %d, Flächen %d', 'allow-list %d, links %d, panes %d'),
 ('FORMULAR_ZAHLEN', '%d Formulare, %d Merkmalsfelder', '%d forms, %d token fields'),
 ('NICHTS_ANGESEHEN', 'Es wurde keine einzige Stelle angesehen - das ist kein Ergebnis, sondern ein blinder Fleck.', 'Not a single place was examined - that is not a result but a blind spot.'),
 ('SPRACHE_ZAHLEN', '%d Schlüssel geprüft, alle vorhanden', '%d keys checked, all present'),
 ('SPRACHE_FEHLEN', '%d von %d Schlüsseln fehlen: %s', '%d of %d keys are missing: %s'),
 ('VORLAGEN_OK', '%d Vorlage(n), wohlgeformt', '%d template(s), well-formed'),
 ('VORLAGEN_KAPUTT', 'Die Vorlage %s ist nicht wohlgeformt.', 'The template %s is not well-formed.'),
 ('GATEWAY_UNLESBAR', 'Die Systemkonfiguration ist nicht lesbar - UDP funktioniert trotzdem.', 'The system configuration is not readable - UDP still works.'),
 ('GATEWAY_OHNE_AUTOSTART', '%s, startet aber nicht automatisch mit', '%s, but does not start automatically'),
 ('GATEWAY_OK', '%s, Autostart ein', '%s, autostart on'),
 ('GATEWAY_FASSUNG_IST', 'Fassung %d', 'version %d'),
 ('GATEWAY_FASSUNG_UNBEKANNT', 'Der Schlüssel Mqtt.Gatewayversion steht nicht in der general.json. Es gelten beide Fälle - siehe Reiter MQTT.', 'The key Mqtt.Gatewayversion is not present in general.json. Both cases apply - see the MQTT tab.'),

 # --- Umgebung ---
 ('U_ORDNER', 'Pluginordner', 'Plugin folder'),
 ('U_VENV', 'Python-Umgebung', 'Python environment'),
 ('U_PYTHON', 'Python', 'Python'),
 ('U_GATEWAY', 'MQTT-Gateway', 'MQTT gateway'),
 ('U_PRAEFIX', 'Themen-Präfix', 'Topic prefix'),
 ('U_REGION', 'Region', 'Region'),
 ('U_FEHLT', 'FEHLT', 'MISSING'),
 ('U_VORHANDEN_KB', 'vorhanden (%s kB)', 'present (%s kB)'),
 ('U_NICHT_VORHANDEN', 'nicht vorhanden', 'not present'),

 # --- Logdateien ---
 ('H_LOGDATEIEN', 'Logdateien', 'Log files'),
 ('H_LOG_EIGEN', 'Protokoll dieses Plugins', 'Log of this plugin'),
 ('LOG_RUECKFALL', 'Neueste Zeile oben. Datei:', 'Newest line first. File:'),
 ('LOG_LEER', 'Die Protokolldatei ist leer oder noch nicht angelegt.', 'The log file is empty or has not been created yet.'),

 # --- Sicherung ---
 ('H_SICHERUNG', 'Einstellungen sichern und zurückspielen', 'Back up and restore settings'),
 ('SICH_ERKLAERUNG', 'Für den <b>Umzug auf einen zweiten LoxBerry</b>: die Datei enthält alle Einstellungen dieses Plugins <b>und die gefundenen Geräte samt Token und Schlüssel</b>. Auf dem anderen Gerät eingespielt, läuft das Plugin sofort - eine neue Gerätesuche ist nicht nötig.', 'For <b>moving to a second LoxBerry</b>: the file contains all settings of this plugin <b>and the discovered devices including token and key</b>. Restored on the other machine the plugin works immediately - no new device search is needed.'),
 ('SICH_WARNUNG', '<b>Die Datei enthält Ihre Zugangsdaten und die Schlüssel der Klimageräte.</b> Wer sie hat, kann die Geräte im selben Netz steuern. Behandeln Sie die Datei wie ein Passwort: nicht in ein Forum hängen und nicht an einen Fehlerbericht heften.', '<b>The file contains your credentials and the keys of the air conditioners.</b> Anyone who has it can control the devices on the same network. Treat the file like a password: do not post it in a forum and do not attach it to a bug report.'),
 ('SICH_HILFE', 'Die Datei ist wenige Kilobyte groß. Beim Zurückspielen wird sie vollständig geprüft: eine halb gültige Datei ändert gar nichts.', 'The file is a few kilobytes in size. When restoring it is checked completely: a half-valid file changes nothing at all.'),
 ('SICH_KOPF', 'Sicherung des LoxBerry-Plugins Midea2Lox. Enthält Zugangsdaten und Geräteschlüssel - wie ein Passwort behandeln.', 'Backup of the LoxBerry plugin Midea2Lox. Contains credentials and device keys - treat it like a password.'),
 ('K_SICHERN', 'Einstellungen sichern', 'Back up settings'),
 ('K_ZURUECK', 'Zurückspielen', 'Restore'),
 ('SICH_ABGELEHNT', 'Die Datei wurde <b>nicht</b> übernommen - es ist nichts geändert worden:', 'The file was <b>not</b> accepted - nothing has been changed:'),
 ('SICH_KEIN_JSON', 'Die Datei ist keine gültige Sicherung dieses Plugins.', 'The file is not a valid backup of this plugin.'),
 ('SICH_FREMD', 'Unbekannte Einstellung in der Datei: %s', 'Unknown setting in the file: %s'),
 ('SICH_FREMDES_PLUGIN', 'Die Datei stammt vom Plugin %s, nicht von Midea2Lox.', 'The file comes from the plugin %s, not from Midea2Lox.'),
 ('SICH_LEER', 'Die Datei enthält keine bekannte Einstellung.', 'The file contains no known setting.'),
 ('SICH_KEINE_DATEI', 'Es wurde keine Datei ausgewählt, oder der Upload ist fehlgeschlagen.', 'No file was selected, or the upload failed.'),
 ('SICH_ZU_GROSS', 'Die Datei ist größer als erlaubt - eine Sicherung dieses Plugins ist wenige Kilobyte groß.', 'The file is larger than allowed - a backup of this plugin is a few kilobytes.'),
 ('SICH_SCHREIBFEHLER', 'Die Einstellungen ließen sich nicht schreiben.', 'The settings could not be written.'),
 ('SICH_GERAETE_SCHREIBFEHLER', 'Die Geräteliste ließ sich nicht schreiben - es wurde nichts übernommen, auch keine Einstellung. Bitte die Rechte im Konfigurationsordner prüfen und den Vorgang wiederholen.', 'The device list could not be written - nothing was applied, not even a setting. Please check the permissions of the configuration folder and repeat.'),
 ('SICH_UEBERNOMMEN', 'Zurückgespielt: %d Einstellungen und %d Gerät(e). Der Dienst wurde neu gestartet.', 'Restored: %d settings and %d device(s). The service was restarted.'),
 ('SICH_UEBERNOMMEN_OHNE_DIENST', 'Zurückgespielt: %d Einstellungen und %d Gerät(e). Der Dienst ließ sich nicht neu starten - bitte im Reiter Test nachsehen.', 'Restored: %d settings and %d device(s). The service could not be restarted - please check the Test tab.'),
 ('SICH_GERAETE_FORM', 'Der Abschnitt mit den Geräten hat nicht die erwartete Form.', 'The section with the devices does not have the expected shape.'),
 ('SICH_GERAET_FORM', 'Gerät %d in der Datei hat nicht die erwartete Form.', 'Device %d in the file does not have the expected shape.'),
 ('SICH_GERAET_ID', 'Gerät %d hat keine gültige Nummer.', 'Device %d has no valid number.'),
 ('SICH_GERAET_IP', 'Gerät %d hat keine gültige IP-Adresse.', 'Device %d has no valid IP address.'),
 ('SICH_GERAET_PORT', 'Gerät %d hat keinen gültigen Port.', 'Device %d has no valid port.'),
 ('SICH_GERAET_TOKEN', 'Gerät %d hat keinen gültigen Token - erwartet werden 128 Hexziffern.', 'Device %d has no valid token - 128 hex digits are expected.'),
 ('SICH_GERAET_KEY', 'Gerät %d hat keinen gültigen Schlüssel - erwartet werden 64 Hexziffern.', 'Device %d has no valid key - 64 hex digits are expected.'),
 ('SICH_GERAET_PAAR', 'Bei Gerät %d fehlt eine Hälfte des Paares aus Token und Schlüssel. Mit nur einer Hälfte kann sich das Gerät nicht anmelden.', 'Device %d is missing one half of the token and key pair. With only one half the device cannot authenticate.'),
 ('SICH_GERAET_BEZ', 'Die Bezeichnung von Gerät %d ist unbrauchbar oder zu lang.', 'The label of device %d is unusable or too long.'),
 ('SICH_GERAET_TYP', 'Der Typ von Gerät %d enthält unerlaubte Zeichen.', 'The type of device %d contains characters that are not allowed.'),

 # --- Farblegende ---
 ('LEG_LESEN', 'liest nur oder startet', 'reads only or starts'),
 ('LEG_TECHNIK', 'technischer Eingriff', 'technical operation'),
 ('LEG_AKTION', 'greift in den laufenden Betrieb ein', 'affects running operation'),
 ('NEIN', 'nein', 'no'),
 ('AUTO_EINLEITUNG', 'Die Automatik hört auf <b>MQTT</b> und verschiebt daraufhin die Solltemperatur. Sie holt <b>keine</b> Preise selbst - das tun die Plugins <i>Spotpreis-aWATTar</i>, <i>Spotpreis-Tibber</i> oder <i>Spotpreis-Octopus</i> bereits, und der PV-Überschuss kommt aus <i>Einspeisebremse</i>. Hier wird nur eingetragen, auf welche Themen gehorcht werden soll.', 'The automation listens on <b>MQTT</b> and shifts the target temperature accordingly. It does <b>not</b> fetch prices itself - the plugins <i>Spotpreis-aWATTar</i>, <i>Spotpreis-Tibber</i> or <i>Spotpreis-Octopus</i> already do that, and the PV surplus comes from <i>Einspeisebremse</i>. All you enter here is which topics to listen to.'),
 ('AUTO_K_LAGE', 'Zustand', 'State'),
 ('AUTO_K_GRUND', 'Begründung des letzten Durchgangs', 'Reason given by the last pass'),
 ('AUTO_K_GERAETE', 'Geräte mit Verschiebung', 'Devices currently shifted'),
 ('AUTO_LAGE_AUS', 'ausgeschaltet', 'switched off'),
 ('AUTO_LAGE_OK', 'läuft', 'running'),
 ('AUTO_LAGE_FEHLT', 'eingeschaltet, aber noch kein Durchgang', 'switched on, but no pass yet'),
 ('AUTO_LAGE_ALT', 'seit %d s kein Durchgang', 'no pass for %d s'),
 ('AUTO_LAGE_UNLESBAR', 'Zustandsdatei unlesbar', 'state file cannot be read'),
 ('AUTO_LAEUFT_SEIT', 'letzter Durchgang vor %d s: %s', 'last pass %d s ago: %s'),
 ('AUTO_KEIN_THEMA', 'kein Thema eingetragen - diese Quelle wird nicht genutzt', 'no topic entered - this source is not used'),
 ('AUTO_NICHT_MESSBAR', 'lässt sich erst beurteilen, wenn die Automatik einen Durchgang hatte (%s)', 'can only be judged once the automation has had a pass (%s)'),
 ('AUTO_NICHTS_EMPFANGEN', 'seit dem Start ist auf %s nichts angekommen. Sendet das Nachbarplugin, und gibt das MQTT-Gateway das Thema an den Broker weiter?', 'nothing has arrived on %s since the start. Is the neighbouring plugin sending, and does the MQTT gateway pass the topic on to the broker?'),
 ('AUTO_EMPFANGEN', '%s zuletzt: %s', '%s last value: %s'),
 ('AUTO_S1', 'Schritt 1: Woher das Signal kommt', 'Step 1: where the signal comes from'),
 ('AUTO_S1_TEXT', 'Zwei Quellen, beide freiwillig. Ein leeres Feld heißt: diese Quelle wird nicht benutzt. Die Automatik greift, sobald <b>eine</b> von beiden zutrifft.', 'Two sources, both optional. An empty field means: this source is not used. The automation engages as soon as <b>one</b> of them applies.'),
 ('AUTO_S1_HINWEIS', "Die üblichen Themen sind <span class='sm-mono'>spot_awattar/regel/1/aktiv</span> oder <span class='sm-mono'>tibber/regel/1/aktiv</span> für den Preis und <span class='sm-mono'>einspeisebremse/ueberschuss</span> für die Leistung in Watt. Die genauen Namen stehen im jeweiligen Plugin unter <i>MQTT</i>. Ob wirklich etwas ankommt, sagt der Reiter <b>Test</b> - sehen Sie dort nach, bevor Sie die Automatik einschalten.", "The usual topics are <span class='sm-mono'>spot_awattar/regel/1/aktiv</span> or <span class='sm-mono'>tibber/regel/1/aktiv</span> for the price and <span class='sm-mono'>einspeisebremse/ueberschuss</span> for the power in watts. The exact names are in the respective plugin under <i>MQTT</i>. Whether anything actually arrives is shown in the <b>Test</b> tab - look there before switching the automation on."),
 ('AUTO_S2', 'Schritt 2: Was am Gerät geschehen soll', 'Step 2: what should happen at the device'),
 ('AUTO_S2_TEXT', 'Die Verschiebung wirkt <b>je nach Betriebsart</b> in die sinnvolle Richtung: beim Kühlen wird der Sollwert gesenkt (vorkühlen), beim Heizen angehoben (vorwärmen). In Betriebsarten ohne Sollwert geschieht nichts.', 'The shift works <b>in the direction that makes sense for the mode</b>: when cooling the target is lowered (pre-cooling), when heating it is raised (pre-heating). In modes without a target nothing happens.'),
 ('AUTO_S2_WARNUNG', '<b>Ein- und Ausschalten ist der tiefste Eingriff.</b> Die Automatik schaltet ein Gerät nur dann wieder aus, wenn <b>sie es selbst eingeschaltet hat</b>. Ein Gerät, das Sie eingeschaltet vorgefunden haben, bleibt an.', '<b>Switching on and off is the deepest intervention.</b> The automation switches a device off again only if <b>it switched it on itself</b>. A device you had switched on stays on.'),
 ('AUTO_S3', 'Schritt 3: Vorrang und Sicherheitsnetz', 'Step 3: precedence and safety net'),
 ('AUTO_S3_TEXT', 'Jeder Befehl aus Loxone oder vom Reiter Test setzt die Automatik für die Sperrzeit aus - eine reine Statusabfrage nicht. Sie stellt dabei den Sollwert zurück, <b>schaltet aber nicht</b>: ein Gerät, das Sie gerade eingeschaltet haben, würde sie sonst Sekunden später wieder ausschalten. Bleibt ein Signal dagegen länger aus als die Höchstdauer, ist niemand da, der etwas anderes wollte - dann stellt sie den vorgefundenen Zustand ganz wieder her, auch geschaltet.', 'Any command from Loxone or from the Test tab suspends the automation for the lockout time - a plain status query does not. It puts the target back but <b>does not switch</b>: a device you have just switched on would otherwise be switched off again seconds later. If a signal stays away longer than the maximum age, however, nobody is there who wanted something else - then it restores the state it found completely, switching included.'),
 ('AUTO_S4', 'Was die Automatik selbst veröffentlicht', 'What the automation publishes itself'),
 ('AUTO_S4_TEXT', 'Diese Themen sendet das Plugin, damit in Loxone sichtbar ist, was die Automatik und die Anwesenheit tun und warum.', 'The plugin sends these topics so that Loxone shows what the automation and the presence coupling do and why.'),
 ('AUTO_TH_THEMA', 'Thema', 'Topic'),
 ('AUTO_TH_BEDEUTUNG', 'Bedeutung', 'Meaning'),
 ('AUTO_T_AKTIV', '1, solange die Automatik greift, sonst 0', '1 while the automation is engaged, otherwise 0'),
 ('AUTO_T_GRUND', 'Klartext, warum sie greift oder nicht', 'plain text: why it is engaged or not'),
 ('AUTO_T_GESPERRT', 'Restzeit der Handsperre in Sekunden, sonst 0', 'remaining lockout time in seconds, otherwise 0'),
 ('AUTO_T_GERAETE', 'Zahl der Geräte mit einer laufenden Verschiebung', 'number of devices with an active shift'),
 ('AUTO_F_EIN', 'Automatik', 'Automation'),
 ('AUTO_F_THEMA_REGEL', 'Thema des Preissignals', 'Topic of the price signal'),
 ('AUTO_F_THEMA_PV', 'Thema des PV-Überschusses', 'Topic of the PV surplus'),
 ('AUTO_F_PV_AB', 'Automatik greift ab', 'Automation engages from'),
 ('AUTO_F_VERSCHIEBUNG', 'Verschiebung des Sollwerts', 'Shift of the target'),
 ('AUTO_F_VERSCHIEBUNG_EINHEIT', 'Zehntelkelvin - 20 sind 2,0 K', 'tenths of a kelvin - 20 means 2.0 K'),
 ('AUTO_F_SOLL_MIN', 'Sollwert nie unter', 'Target never below'),
 ('AUTO_F_SOLL_MAX', 'Sollwert nie über', 'Target never above'),
 ('AUTO_F_TURBO', 'Zusätzlich Turbo einschalten', 'Also switch on turbo'),
 ('AUTO_F_SCHALTEN', 'Gerät selbst ein- und ausschalten', 'Switch the device on and off'),
 ('AUTO_F_SPERRZEIT', 'Handbetrieb sperrt die Automatik', 'Manual operation suspends the automation for'),
 ('AUTO_F_MAX_ALTER', 'Signal gilt höchstens', 'A signal is valid for at most'),
 ('AUTO_F_TAKT', 'Die Automatik sieht nach alle', 'The automation looks every'),
 ('AUTO_F_GERAETE', 'Nur diese Geräte', 'Only these devices'),
 ('AUTO_F_GERAETE_LEER', 'leer = alle Geräte', 'empty = all devices'),
 ('AUTO_MINUTEN', 'Minuten', 'minutes'),
 ('AUTO_SEKUNDEN', 'Sekunden', 'seconds'),
 ('AUTO_SPEICHERN', 'Automatik speichern', 'Save automation'),
 ('AUTO_GESPEICHERT', 'Gespeichert, der Dienst wurde neu gestartet. Der Reiter Test zeigt, ob auf den Themen etwas ankommt.', 'Saved, the service was restarted. The Test tab shows whether anything is arriving on the topics.'),
 ('AUTO_GESPEICHERT_OHNE_DIENST', 'Gespeichert - der Dienst ließ sich aber nicht neu starten. Bis dahin arbeitet die Automatik mit den alten Einstellungen.', 'Saved - but the service could not be restarted. Until then the automation keeps working with the old settings.'),
 ('PRUEF_JANEIN', 'Dieses Feld kennt nur ja und nein.', 'This field only knows yes and no.'),
 ('PRUEF_ABOTHEMA', 'Das ist kein brauchbares MQTT-Thema. Erlaubt sind Buchstaben, Ziffern, Punkt, Strich und Unterstrich, durch Schrägstriche getrennt - und kein Platzhalter (# oder +).', 'That is not a usable MQTT topic. Allowed are letters, digits, dot, dash and underscore, separated by slashes - and no wildcard (# or +).'),
 ('PRUEF_PV_AB', 'Die Schwelle ist eine Zahl zwischen 0 und 100000 Watt.', 'The threshold is a number between 0 and 100000 watts.'),
 ('PRUEF_VERSCHIEBUNG', 'Die Verschiebung steht in Zehntelkelvin, zwischen 0 und 100 (also bis 10,0 K).', 'The shift is given in tenths of a kelvin, between 0 and 100 (up to 10.0 K).'),
 ('PRUEF_SOLLGRENZE', 'Die Sollwertgrenze ist eine Zahl zwischen 5 und 35 Grad.', 'The target limit is a number between 5 and 35 degrees.'),
 ('PRUEF_SOLL_VERDREHT', 'Die Untergrenze des Sollwerts liegt über der Obergrenze.', 'The lower target limit is above the upper one.'),
 ('PRUEF_MAX_ALTER', 'Die Höchstdauer ist eine Zahl zwischen 60 und 86400 Sekunden.', 'The maximum age is a number between 60 and 86400 seconds.'),
 ('PRUEF_SPERRZEIT', 'Die Sperrzeit ist eine Zahl zwischen 0 und 1440 Minuten.', 'The lockout time is a number between 0 and 1440 minutes.'),
 ('PRUEF_AUTO_TAKT', 'Der Takt ist eine Zahl zwischen 60 und 3600 Sekunden.', 'The interval is a number between 60 and 3600 seconds.'),
 ('PRUEF_AUTO_GERAETE', '%s ist keine Gerätenummer - erwartet werden 10 bis 19 Ziffern.', '%s is not a device number - 10 to 19 digits are expected.'),
 ('PRUEF_AUTO_OHNE_THEMA', 'Die Automatik lässt sich nicht einschalten, solange kein einziges Thema eingetragen ist - sie könnte nichts entscheiden.', 'The automation cannot be switched on while no topic at all is entered - it would have nothing to decide on.'),
 ('ABO_EINGETRAGEN_MITGELIEFERT', 'abonniert über die mitgelieferte Datei (%s) - das Gateway liest sie ein; in der Abo-Liste der Oberfläche steht sie deshalb nicht (dort %d Einträge)', 'subscribed via the shipped file (%s) - the gateway reads it; that is why it does not appear in the subscription list of the web interface (%d entries there)'),
 ('THEMA_RETAIN', 'zurückbehalten', 'retained'),
 ('RETAIN_JA', 'ja', 'yes'),
 ('RETAIN_NEIN', 'nein', 'no'),
 ('RETAIN_ERKLAERUNG', '<b>Zurückbehalten</b> (retained) heißt: der Broker hält den letzten Wert fest, und Loxone hat ihn nach einem Neustart sofort wieder. Das ist bei <i>Zuständen des Geräts</i> richtig und bei <i>Messwerten</i> falsch - ein alter Messwert sähe aus wie ein aktueller. Nie zurückbehalten ist auch, was der Dienst über sich selbst sagt: das <i>Lebenszeichen</i> (es würde sonst noch „lebt“ melden, wenn der Dienst längst tot ist), die Erreichbarkeit <i>online</i> (der Dienst stellt sie aus seiner eigenen Abfrage fest) und die Themen der <i>Automatik</i>. Zurückbehalten ist dagegen <i>connection/status</i>: „connected“ beim Verbinden, „disconnected“ als Letzter Wille, den der Broker selbst setzt; die Deinstallation räumt das Thema ab.', '<b>Retained</b> means the broker keeps the last value, so Loxone has it again right after a restart. That is right for <i>device states</i> and wrong for <i>measured values</i> - an old reading would look like a current one. Whatever the service says about itself is never retained either: the <i>heartbeat</i> (it would keep reporting „alive“ long after the service has died), the reachability <i>online</i> (the service determines it from its own query) and the <i>automation</i> topics. <i>connection/status</i>, on the other hand, is retained: „connected“ on connecting, „disconnected“ as the last will that the broker sets by itself; uninstalling clears the topic.'),
 ('RETAIN_GLEICH', 'deckungsgleich, %d Themen mit Retain', 'identical, %d topics with retain'),
 ('RETAIN_UNGLEICH', 'laufen auseinander: %s', 'they diverge: %s'),

 # ---- NACHGEPFLEGT 31.08.2026: standen in der .ini und im PHP,
 #      aber nicht mehr hier. Dieser Erzeuger verweigert NICHT -
 #      ein Lauf haette sie kommentarlos geloescht.
 ('ABO_SCHREIBFEHLER', "Die Abo-Datei <span class='sm-mono'>%s</span> ließ sich nicht schreiben. Das Thema im Reiter MQTT von Hand ins Gateway eintragen.", "The subscription file <span class='sm-mono'>%s</span> could not be written. Enter the topic from the MQTT tab into the gateway by hand."),
 ('DIENST_FEHLGESCHLAGEN', 'Das Startskript hat mit einem Fehler geendet. Der Grund steht im Protokoll - meist eine unvollständige Konfiguration. Der Reiter Test zeigt unter <i>Ist die Konfiguration heil?</i>, was fehlt.', 'The start script ended with an error. The reason is in the log - usually an incomplete configuration. The Test tab shows what is missing under <i>Is the configuration intact?</i>'),
 ('GESPEICHERT_SUCHE_OHNE_DIENST', 'Gespeichert, das Ergebnis der Gerätesuche steht im Reiter Test - der Dienst ließ sich aber nicht neu starten. Bis dahin arbeitet er mit den alten Werten.', 'Saved, and the result of the device search is in the Test tab - but the service could not be restarted. Until then it keeps working with the old values.'),
 ('LOCALIP_UNBRAUCHBAR', 'Die eigene Adresse ließ sich nicht ermitteln (%s ist keine IP-Adresse). Der bisherige Wert bleibt stehen; bitte im Feld nachsehen.', 'The own address could not be determined (%s is not an IP address). The previous value stays; please check the field.'),
 ('MEHRERE_AKTIONEN', 'Die Anfrage forderte mehrere Vorgänge auf einmal an (%s). Es wurde keiner ausgeführt.', 'The request asked for several operations at once (%s). None of them was carried out.'),
 ('NICHT_FESTSTELLBAR', 'nicht feststellbar', 'not determinable'),
 ('OHNE_VENV', 'ohne virtuelle Umgebung nicht feststellbar', 'not determinable without the virtual environment'),
 ('PRUEF_MINISERVER_FEHLT', 'Den Miniserver %s gibt es in der LoxBerry-Konfiguration nicht. Der Dienst würde damit beim Start abbrechen.', 'Miniserver %s does not exist in the LoxBerry configuration. The service would abort on start.'),
 ('SICH_DL_FEHLER', 'Die Sicherung ließ sich nicht erzeugen. Vermutlich steht in der Gerätedatei ein Zeichen, das kein gültiges UTF-8 ist.', 'The backup could not be created. Most likely the device file contains a character that is not valid UTF-8.'),
 ('SICH_HALB', 'Die Gerätedatei ist zurückgespielt, die Einstellungen aber nicht - für sie gilt weiter der bisherige Stand. Bitte die Rechte im Konfigurationsordner prüfen und den Vorgang wiederholen.', 'The device file was restored, the settings were not - for those the previous state still applies. Please check the permissions in the configuration folder and try again.'),
 ('SICH_UNBERUEHRT', 'Diese Einstellungen standen nicht in der Datei und sind unverändert geblieben: %s', 'These settings were not in the file and have been left unchanged: %s'),
 ('SICH_UPLOAD_FEHLER', 'Die Datei kam nicht vollständig an (Fehlercode %d). Meist ist sie größer, als der Webserver entgegennimmt.', 'The file did not arrive completely (error code %d). Usually it is larger than the web server accepts.'),
 ('WACHE_UNABLEGBAR', "Das Plugin kann sein Formularmerkmal nicht ablegen - <span class='sm-mono'>%s</span> ist nicht beschreibbar. Solange das so ist, wird JEDE Eingabe abgewiesen, und Neuladen hilft nicht. Bitte die Rechte dieses Verzeichnisses prüfen.", "The plugin cannot store its form token - <span class='sm-mono'>%s</span> is not writable. While that is the case EVERY input is rejected, and reloading does not help. Please check the permissions of that directory."),
 ('PRUEF_RANDLEER', 'Das Feld %s beginnt oder endet mit einem Leerzeichen. Die Konfigurationsdatei kann das nicht halten - der Dienst läse den Wert ohne diese Leerzeichen. Bitte ohne Rand-Leerzeichen eingeben.', 'The field %s starts or ends with a space. The configuration file cannot keep that - the service would read the value without these spaces. Please enter it without leading or trailing spaces.'),
 ('SICH_GERAET_FELDTYP', 'Gerät %d: das Feld %s ist keine Zeichenkette.', 'Device %d: the field %s is not a string.'),
 ('SICH_GERAET_DOPPELT', 'Gerät %d: die Nummer %s steht schon bei Gerät %d. Mit einer doppelten Gerätenummer könnte der Dienst die Gerätedatei nicht mehr lesen.', 'Device %d: the number %s is already used by device %d. With a duplicate device number the service could no longer read the device file.'),
 ('EINMAL_UNABLEGBAR', 'Das Ergebnis ließ sich nicht für die Umleitung ablegen (%s). Die Seite antwortet deshalb unmittelbar - ein Neuladen (F5) würde den Vorgang wiederholen.', 'The result could not be stored for the redirect (%s). The page therefore answers directly - reloading (F5) would repeat the action.'),
 ('VORGANG_MISSLUNGEN', 'Der Vorgang ist nicht gelungen:', 'The action did not succeed:'),
 ('MINISERVER_WAEHLEN', 'Bitte im Reiter Einstellungen einen vorhandenen Miniserver wählen und speichern.', 'Please choose an existing Miniserver in the Settings tab and save.'),
 ('MINISERVER_NICHT_DA', '(nicht vorhanden: %s)', '(not present: %s)'),
 ('FASSUNG_IM_TEST', '(noch nicht ermittelt - der Reiter Test misst die Fassungen)', '(not determined yet - the Test tab measures the versions)'),
 ('PRUEFUNG_NUR_IM_TEST', 'Die Selbstprüfung läuft, wenn der Reiter Test geöffnet wird. Sie startet dafür Python und dauert einige Sekunden.', 'The self-check runs when the Test tab is opened. It starts Python for that and takes a few seconds.'),
 ('PRAEFIX_ALT_ABRAEUMEN', 'Das bisherige Präfix %s ist vermerkt: der Dienst räumt seine zurückbehaltenen Themen nach dem Neustart am Broker ab, spätestens die Deinstallation.', 'The previous prefix %s has been noted: the service clears its retained topics at the broker after the restart, the uninstall at the latest.'),
 ('PRAEFIX_LISTE_FEHLER', 'Die Präfixliste %s ließ sich nicht schreiben - die zurückbehaltenen Themen unter %s bleiben im Broker stehen. Von Hand: mosquitto_pub -r -n -t &lt;thema&gt;', 'The prefix list %s could not be written - the retained topics under %s stay in the broker. By hand: mosquitto_pub -r -n -t &lt;topic&gt;'),
 ('T_SCHALTEN_NICHT', 'Befehl nicht gesendet', 'Command not sent'),
 ('DISCOVER_OHNE_NEUSTART', 'Der Dienst übernimmt geänderte Adressen, Token und Schlüssel aus devices.cfg beim nächsten Befehl - ohne Neustart.', 'The service picks up changed addresses, tokens and keys from devices.cfg with the next command - without a restart.'),
 ('PRUEF_KENNWORT_ZITAT', 'Das Feld %s beginnt mit einem Anführungszeichen und Leerzeichen (oder endet mit Leerzeichen und Anführungszeichen). So lässt es sich nicht eindeutig speichern - bitte ein anderes Kennwort wählen. Leerzeichen am Rand allein sind erlaubt.', 'The field %s starts with a quotation mark followed by a space (or ends with a space followed by a quotation mark). It cannot be stored unambiguously like this - please choose a different password. Leading or trailing spaces alone are allowed.'),
 ('PRUEF_FENSTER_FRIST', 'Die Frist bis zum Ausschalten ist eine ganze Zahl von 0 bis 600 Sekunden.', 'The delay before switching off is a whole number from 0 to 600 seconds.'),
 ('PRUEF_FENSTER_ZUORDNUNG', 'Die Zuordnung hat die Form <i>Gerätenummer:name+name</i>, mehrere Geräte durch Komma getrennt, zum Beispiel <i>123456789012345:wohnzimmer_links+wohnzimmer_rechts</i>. Jede Gerätenummer nur einmal; Namen klein, nur a-z, 0-9 und _, höchstens 40 Zeichen - so wie im Thema haus/tuer/<i>name</i>/offen.', 'The assignment has the form <i>device number:name+name</i>, several devices separated by commas, for example <i>123456789012345:living_room_left+living_room_right</i>. Each device number only once; names in lower case, only a-z, 0-9 and _, at most 40 characters - as in the topic haus/tuer/<i>name</i>/offen.'),
 ('PRUEF_FENSTER_OHNE_ZUORDNUNG', 'Fenster offen: Gerät aus ist eingeschaltet, aber kein Fenster ist einem Gerät zugeordnet - der Schalter hätte keine Wirkung.', 'Window open: device off is switched on, but no window is assigned to a device - the switch would have no effect.'),
 ('FENSTER_GERAET_UNBEKANNT', 'Gespeichert. Die Gerätenummer(n) %s kennt die Geräteliste nicht - für sie geschieht erst etwas, wenn die Gerätesuche sie findet.', 'Saved. The device number(s) %s are not in the device list - nothing happens for them until the device search finds them.'),
 ('FENSTER_S', 'Fenster offen: Gerät aus', 'Window open: device off'),
 ('FENSTER_S_TEXT', 'Ab Werk aus. Eingeschaltet hört das Plugin auf die Haus-Themen <b>haus/tuer/<i>name</i>/offen</b> (0 = zu, 1 = offen, - = keine Aussage). Sie kommen von <b>Matter2Lox</b>, wenn dort die Haus-Themen eingeschaltet sind; jeder Kontaktsensor gilt dort als Tür, also auch ein Fensterkontakt. Bleibt ein zugeordnetes Fenster länger offen als die Frist, bekommt das Gerät <b>einen</b> Aus-Befehl - einen je Öffnung, auch wenn weitere Fenster dazukommen. <b>Schließt das Fenster, wird das Gerät nicht wieder eingeschaltet.</b> Solange ein Fenster offen ist, greift auch die Automatik bei diesem Gerät nicht zu.', 'Off by default. When switched on, the plugin listens to the house topics <b>haus/tuer/<i>name</i>/offen</b> (0 = closed, 1 = open, - = no statement). They come from <b>Matter2Lox</b> when its house topics are switched on; every contact sensor counts as a door there, so a window contact does too. If an assigned window stays open longer than the delay, the device gets <b>one</b> off command - one per opening, even if further windows open. <b>When the window closes, the device is not switched back on.</b> While a window is open, the automation does not act on this device either.'),
 ('FENSTER_F_EIN', 'Fenster offen: Gerät aus', 'Window open: device off'),
 ('FENSTER_F_FRIST', 'Frist bis zum Ausschalten (0-600)', 'Delay before switching off (0-600)'),
 ('FENSTER_F_ZUORDNUNG', 'Zuordnung Gerät:Fenster', 'Assignment device:windows'),
 ('FENSTER_S_HINWEIS', 'Die Namen stehen so in der Themenliste von Matter2Lox (klein, ä zu ae, Leerzeichen zu _). Ein Wert, der beim Start oder nach einem Wiederverbinden nur aus dem Speicher des Brokers kommt, löst nichts aus - erst ein frisch gesendetes Öffnen. Schweigt die Quelle, passiert nichts; der Reiter Test sagt, was ankommt.', 'The names are the ones in the topic list of Matter2Lox (lower case, umlauts spelled out, spaces as _). A value that only comes from the broker memory at start-up or after a reconnect triggers nothing - only a freshly sent opening does. If the source is silent, nothing happens; the Test tab shows what arrives.'),
 ('FENSTER_LAGE_AUS', 'ausgeschaltet (ab Werk)', 'switched off (default)'),
 ('FENSTER_LAGE_FEHLT', 'eingeschaltet, aber der Dienst hat noch keinen Stand abgelegt - läuft er, und wurde er nach dem Speichern neu gestartet? Bis dahin wird nichts ausgeschaltet.', 'switched on, but the service has not stored a state yet - is it running, and was it restarted after saving? Until then nothing is switched off.'),
 ('FENSTER_LAGE_UNLESBAR', 'der Stand des Dienstes ist nicht lesbar - bis zum nächsten Stand wird nichts ausgeschaltet.', 'the state of the service cannot be read - nothing is switched off until the next state.'),
 ('FENSTER_LAGE_ALT', 'der letzte Stand des Dienstes ist %d s alt - läuft er noch? Ohne Dienst wird nichts ausgeschaltet.', 'the last state of the service is %d s old - is it still running? Without the service nothing is switched off.'),
 ('FENSTER_OHNE_MQTT', 'der Dienst ist nicht mit dem Broker verbunden und hört keine Fenster - die Kopplung ruht, die Geräte laufen wie ohne sie.', 'the service is not connected to the broker and hears no windows - the coupling rests, the devices run as without it.'),
 ('FENSTER_LAEUFT', 'eingeschaltet, Frist %d s, %d Gerät(e) zugeordnet', 'switched on, delay %d s, %d device(s) assigned'),
 ('FENSTER_NIE', 'noch nichts empfangen - solange nichts kommt, passiert nichts. Sind in Matter2Lox die Haus-Themen eingeschaltet, und stimmt der Name?', 'nothing received yet - as long as nothing comes, nothing happens. Are the house topics switched on in Matter2Lox, and is the name right?'),
 ('FENSTER_KEINE_AUSSAGE', 'die Quelle meldet - (keine Aussage) - es passiert nichts, bis sie wieder 0 oder 1 sendet.', 'the source reports - (no statement) - nothing happens until it sends 0 or 1 again.'),
 ('FENSTER_NUR_RETAIN', 'nur ein zurückbehaltener Wert (%s) aus dem Broker, Alter unbekannt - er löst nichts aus, erst ein frisch gesendeter Wert.', 'only a retained value (%s) from the broker, age unknown - it triggers nothing, only a freshly sent value does.'),
 ('FENSTER_UNLESBAR', 'der Wert %s ist weder 0 noch 1 - gilt als nicht offen.', 'the value %s is neither 0 nor 1 - counts as not open.'),
 ('FENSTER_EMPFANGEN', 'zuletzt %s, frisch empfangen vor %d s', 'last %s, received fresh %d s ago'),
 ('FENSTER_OFFEN_SEIT', 'offen, frisch gemeldet vor %d s', 'open, reported fresh %d s ago'),
 ('FENSTER_AUS_BEFOHLEN', 'vor %d s gesendet (einer je Öffnung; beim Schließen wird nicht wieder eingeschaltet)', 'sent %d s ago (one per opening; closing does not switch it back on)'),
 ('X2_EINGABEN', 'Das Formular zeigt Ihre letzte Eingabe; gespeichert ist weiter der bisherige Stand. Die beanstandeten Felder sind rot umrandet. Ein Kennwort wird aus Sicherheitsgründen nicht wieder eingesetzt.', 'The form shows your last input; what is stored is still the previous state. The rejected fields have a red frame. A password is not filled in again, for security reasons.'),
 ('SICH_ALTWERT', '<b>Achtung:</b> Die gespeicherten Werte <b>%s</b> würden das Zurückspielen dieser Sicherung nicht bestehen - die Datei wird trotzdem vollständig geliefert. Bitte die Werte vorher im jeweiligen Reiter berichtigen und speichern.', '<b>Attention:</b> the stored values <b>%s</b> would not pass restoring this backup - the file is delivered complete anyway. Please correct the values in their tab and save first.'),
 ('SICH_ALTWERT_KOPF', 'Achtung: die Werte %s würden das Zurückspielen dieser Sicherung nicht bestehen. Bitte vorher berichtigen.', 'Attention: the values %s would not pass restoring this backup. Please correct them first.'),
 ('SCHRITTE_TITEL', 'So übernehmen Sie diese Seite', 'How to take over this page'),
 ('HINWEISE_TITEL', 'Hinweise', 'Notes'),
 ('BILD_ALT', 'Bausteine der Seite „%s“ in Loxone Config', 'Blocks of the page “%s” in Loxone Config'),
 ('BILD_UNTERSCHRIFT', 'Seite „%s“ im LoxBerry-Plugins Musterprojekt. Config kürzt lange Bausteinnamen – Namen siehe Tabelle.', 'Page “%s” in the LoxBerry plugins sample project. Config shortens long block names – see the table for the full names.'),
 ('MUSTERPROJEKT', "Die ganze Projektdatei mit allen Plugin-Seiten und Vorlagen: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry-Plugins Musterprojekt</a>", "The complete project file with all plugin pages and templates: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry plugins sample project</a>"),
 ('VQ_KOMMENTAR', 'Erzeugt vom LoxBerry-Plugin Midea2Lox. Befehle gehen per UDP an den LoxBerry.', 'Generated by the LoxBerry plugin Midea2Lox. Commands go to the LoxBerry via UDP.'),
 # ---- Gruppe 15 (4.5.18): MQTT-Befehle, Namenstabelle, Anwesenheit, Fehlwerte
 ('LOXBERRYIP_OK', 'ja – %s', 'yes – %s'),
 ('LOXBERRYIP_ALT', 'eingetragen ist %s, dieser LoxBerry hat %s. Die UDP-Vorlage in Loxone zeigt auf eine alte Adresse – Einstellungen speichern und die Vorlage neu laden. (Der Dienst selbst horcht auf allen Adressen.)', '%s is entered, this LoxBerry has %s. The UDP template in Loxone points to an old address – save the settings and load the template again. (The service itself listens on all addresses.)'),
 ('BEFEHLE_LAGE_AUS', 'aus (ab Werk) – Haken „Befehle über MQTT annehmen“ im Reiter MQTT', 'off (default) – tick “Accept commands via MQTT” in the tab MQTT'),
 ('BEFEHLE_LAGE_STUMM', 'Haken an, aber der Dienst meldet sich nicht (Lebenszeichen fehlt oder älter als 180 s)', 'tick on, but the service does not report (sign of life missing or older than 180 s)'),
 ('BEFEHLE_LAGE_OK', 'Abo bestätigt – noch kein Befehl eingegangen', 'subscription confirmed – no command received yet'),
 ('BEFEHLE_LAGE_ZULETZT', 'Abo bestätigt; zuletzt %s: %s (vor %d s)', 'subscription confirmed; last %s: %s (%d s ago)'),
 ('BEFEHLE_LAGE_ABO', 'Abo abgelehnt oder keine Verbindung zum Broker – Rechte des Brokerbenutzers prüfen; nach dem Speichern im Reiter MQTT startet der Dienst neu', 'subscription refused or no connection to the broker – check the rights of the broker user; after saving in the tab MQTT the service restarts'),
 ('ZUORDNUNG_GLEICH', 'ja – %d Befehle, jede Abbildung steht in der Befehlsliste', 'yes – %d commands, every mapping is in the command list'),
 ('ZUORDNUNG_UNGLEICH', 'nein – %s', 'no – %s'),
 ('FEHLWERTE_GLEICH', 'ja – %d Themen', 'yes – %d topics'),
 ('FEHLWERTE_UNGLEICH', 'nein – %s', 'no – %s'),
 ('NAMEN_OK', 'ja – %d Namen, %d Haken für Gateway V2', 'yes – %d names, %d ticks for gateway V2'),
 ('NAMEN_FALSCH', 'nein – %s', 'no – %s'),
 ('ANW_LAGE_AUS', 'aus (ab Werk) – ohne Kopplung', 'off (default) – without coupling'),
 ('ANW_LAGE_STUMM', 'Haken an, aber der Dienst meldet sich nicht (anwesenheit.json fehlt oder älter als 180 s)', 'tick on, but the service does not report (anwesenheit.json missing or older than 180 s)'),
 ('ANW_OHNE_MQTT', 'ohne MQTT hört der Dienst nichts – es gilt das Verhalten ohne Anwesenheit', 'without MQTT the service hears nothing – the behaviour without presence applies'),
 ('ANW_NIE', 'haus/anwesenheit hat noch nie gesendet – es gilt das Verhalten ohne Kopplung. Anbieter: BLE-Scanner NG ab 1.3.28, dort „Anwesenheit für andere Plugins bereitstellen“', 'haus/anwesenheit has never sent – the behaviour without coupling applies. Provider: BLE-Scanner NG from 1.3.28, there “Provide presence for other plugins”'),
 ('ANW_SCHWEIGT', 'haus/anwesenheit schweigt seit %d s (oder sagt „-“) – es gilt das Verhalten ohne Kopplung; Verstelltes wurde zurückgestellt', 'haus/anwesenheit has been silent for %d s (or says “-”) – the behaviour without coupling applies; changes were restored'),
 ('ANW_LAEUFT', 'jemand = %s, Lebenszeichen vor %d s; hält %d Gerät(e) (%s)', 'jemand = %s, sign of life %d s ago; holds %d device(s) (%s)'),
 ('VQ_MQTT_KOMMENTAR', 'Midea2Lox: Befehle über MQTT (nie retain)', 'Midea2Lox: commands via MQTT (never retain)'),
 ('WACHE_NICHTS', 'Es wurde nichts ausgeführt – %s', 'Nothing was carried out – %s'),
 ('PRUEF_ANW_VERHALTEN', 'Verhalten bei Abwesenheit: verschieben, spar oder aus.', 'Behaviour when away: verschieben, spar or aus.'),
 ('PRUEF_ANW_FRIST', 'Frist der Anwesenheit: 0 bis 3600 Sekunden.', 'Delay of presence: 0 to 3600 seconds.'),
 ('F_BEFEHLE_MQTT', 'Befehle über MQTT annehmen', 'Accept commands via MQTT'),
 ('F_BEFEHLE_EINGREIFEND', 'Ein/Aus, Betriebsart, Frostschutz und Selbstreinigung über MQTT zulassen', 'Allow on/off, operating mode, freeze protection and self-cleaning via MQTT'),
 ('BEFEHLE_HILFE', "Befehle kommen als <span class='sm-mono'>publish &lt;Präfix&gt;/befehl/&lt;Gerätenummer&gt;/&lt;Name&gt; &lt;Wert&gt;</span> über den UDP-Eingang des MQTT-Gateways und laufen durch dieselbe Warteschlange wie die UDP-Befehle (gleicher Wert binnen 60 s geht nicht erneut hinaus, Handvorrang der Automatik). Das Plugin quittiert unter …/quittung. Ein zurückbehaltener Befehl wird verworfen. Speichern startet den Dienst neu.", "Commands arrive as <span class='sm-mono'>publish &lt;prefix&gt;/befehl/&lt;device number&gt;/&lt;name&gt; &lt;value&gt;</span> via the UDP input of the MQTT gateway and run through the same queue as the UDP commands (the same value within 60 s is not sent again, manual priority of the automation). The plugin acknowledges under …/quittung. A retained command is discarded. Saving restarts the service."),
 ('BEFEHLE_HEIMNETZ', 'Jeder im Heimnetz kann über den UDP-Eingang des MQTT-Gateways Befehle senden – deshalb sind beide Haken ab Werk aus.', 'Anyone in the home network can send commands via the UDP input of the MQTT gateway – that is why both ticks are off by default.'),
 ('BEFEHLE_GATEWAY', 'Für Befehle ist unter Gateway V1 und V2 nichts einzutragen.', 'For commands nothing needs to be entered under gateway V1 or V2.'),
 ('ABO_BEFEHL_NICHT_ANHAKEN', "Unter Gateway V2 erscheinen auch <span class='sm-mono'>befehl/…</span>, die Quittungen und <span class='sm-mono'>status/befehle</span> als Kandidaten – nicht anhaken. Unter V1 reicht das Abo sie als Werte an den Miniserver; da es dort keinen Eingang mit diesen Namen gibt, ist das harmlos.", "Under gateway V2 also <span class='sm-mono'>befehl/…</span>, the acknowledgements and <span class='sm-mono'>status/befehle</span> appear as candidates – do not tick them. Under V1 the subscription passes them to the Miniserver as values; as there is no input with these names, that is harmless."),
 ('SP_GATEWAYNAME', 'Name des Virtuellen Eingangs (Thema darunter)', 'Name of the Virtual Input (topic below)'),
 ('SP_ART', 'Art', 'Kind'),
 ('SP_FEHLWERT', 'Fehlwert', 'Default value'),
 ('ART_TEXT', 'Text', 'Text'),
 ('ART_ZAHL', 'Zahl', 'Number'),
 ('V2_HAKEN', 'Haken', 'tick'),
 ('V2_NONCACHED', 'Haken, Noncached', 'tick, Noncached'),
 ('NAMENSTABELLE_HILFE', 'Name genau so; ein Text (Art „Text“) als Virtueller Texteingang, sonst Virtueller Eingang ohne „Als Digitaleingang“. Fehlwert -1 = keine Aussage, -999 = Temperatur fehlt, „-“ = Text ohne Aussage; ein Offline-Gerät meldet nur online = 0, seine Zustände bleiben stehen. Spalte V2: diese Themen im MQTT-Gateway Fassung 2 anhaken (das Musterprojekt braucht genau diese). Eine neue Gerätenummer ergibt neue Namen.', 'Name exactly like this; a text (kind “Text”) as Virtual Text Input, otherwise Virtual Input without “Use as digital input”. Default value -1 = no statement, -999 = temperature missing, “-” = text without statement; an offline device reports only online = 0, its states stay. Column V2: tick these topics in MQTT gateway version 2 (the sample project needs exactly these). A new device number gives new names.'),
 ('K_NAMEN_KOPIEREN', 'Namen kopieren', 'Copy names'),
 ('KOPIERT', 'kopiert', 'copied'),
 ('SCHRITT4_MQTT', 'Schritt 4: Befehle aus Loxone (MQTT)', 'Step 4: commands from Loxone (MQTT)'),
 ('SCHRITT4_MQTT_TEXT', "Im Plugin Reiter MQTT „Befehle über MQTT annehmen“ setzen (für Ein/Aus, Betriebsart, Frostschutz und Selbstreinigung zusätzlich den zweiten Haken). In Loxone Config die Befehle in den Virtuellen Ausgang <b>LoxBerry MQTT-Gateway</b> (Vorlage aus dem Musterprojekt) legen – oder alle auf einmal mit der Vorlage unten (eigener Ausgang „Midea2Lox MQTT-Befehle“). Befehl bei EIN <span class='sm-mono'>publish &lt;Thema&gt; &lt;Wert&gt;</span>, nie „retain“:", "In the plugin tab MQTT set “Accept commands via MQTT” (for on/off, operating mode, freeze protection and self-cleaning additionally the second tick). In Loxone Config put the commands into the Virtual Output <b>LoxBerry MQTT-Gateway</b> (template from the sample project) – or all at once with the template below (own output “Midea2Lox MQTT-Befehle”). Command for ON <span class='sm-mono'>publish &lt;topic&gt; &lt;value&gt;</span>, never “retain”:"),
 ('MQTT_BEFEHLE_UNLESBAR', 'Die Tabelle der MQTT-Befehle (data/mi_mqtt.py) ist nicht lesbar – im Reiter Test nachsehen.', 'The table of the MQTT commands (data/mi_mqtt.py) is not readable – check the tab Test.'),
 ('SP_BEFEHLSTITEL', 'Befehl (Titel in Loxone)', 'Command (title in Loxone)'),
 ('SP_THEMA', 'Thema', 'Topic'),
 ('SP_HAKEN', 'wirkt mit', 'works with'),
 ('HAKEN_EINER', 'Befehle über MQTT annehmen', 'Accept commands via MQTT'),
 ('HAKEN_BEIDE', 'beide Haken', 'both ticks'),
 ('K_VORLAGE_MQTT', 'Vorlage MQTT-Befehle', 'Template MQTT commands'),
 ('UDP_ALT_TITEL', 'Bestehende Anlagen: Befehle über UDP (aufklappen)', 'Existing installations: commands via UDP (expand)'),
 ('ANW_S', 'Anwesenheit (haus/anwesenheit/jemand, z. B. vom BLE-Scanner NG)', 'Presence (haus/anwesenheit/jemand, e.g. from BLE-Scanner NG)'),
 ('ANW_S_TEXT', 'Ab Werk aus. Eingeschaltet hört das Plugin auf <b>haus/anwesenheit/jemand</b> (1 = jemand da, 0 = alle weg) und dessen Lebenszeichen haus/anwesenheit/zaehler. Sendet die Quelle live 0 und bleibt es die Frist dabei, wird <b>einmal je Abwesenheit</b> an jedem eingeschalteten Gerät der Sollwert in die sparsame Richtung verschoben (Kühlen höher, Heizen tiefer) – wahlweise Sparbetrieb oder Ausschalten. Bei der Rückkehr stellt das Plugin nur zurück, was es selbst verstellt hat, und <b>schaltet nie ein</b>. Schweigt die Quelle länger als 120 s oder sagt sie „-“, stellt es ebenso zurück und tut nichts weiter. Jeder Befehl aus Loxone beendet den Abwesenheitsbetrieb des Geräts.', 'Off by default. Switched on, the plugin listens to <b>haus/anwesenheit/jemand</b> (1 = somebody there, 0 = all away) and its sign of life haus/anwesenheit/zaehler. If the source sends 0 live and stays so for the delay, the target value of every switched-on device is shifted <b>once per absence</b> in the economical direction (cooling higher, heating lower) – optionally eco mode or switching off. On return the plugin restores only what it changed itself and <b>never switches on</b>. If the source is silent for more than 120 s or says “-”, it restores as well and does nothing else. Every command from Loxone ends the away mode of the device.'),
 ('ANW_F_EIN', 'Anwesenheit berücksichtigen', 'Consider presence'),
 ('ANW_F_VERHALTEN', 'Bei Abwesenheit', 'When away'),
 ('ANW_V_VERSCHIEBEN', 'Sollwert verschieben (sparsam)', 'shift target (economical)'),
 ('ANW_V_SPAR', 'Sparbetrieb einschalten', 'switch on eco mode'),
 ('ANW_V_AUS', 'ausschalten (bei Rückkehr nicht wieder ein)', 'switch off (not on again on return)'),
 ('ANW_F_VERSCHIEBUNG', 'Verschiebung bei Abwesenheit', 'Shift when away'),
 ('ANW_F_FRIST', 'Frist, bis „niemand da“ wirkt', 'Delay until “nobody there” acts'),
 ('ANW_F_GERAETE', 'Geräte (leer = alle)', 'Devices (empty = all)'),
 ('ANW_S_HINWEIS', 'Anbieter ist der BLE-Scanner NG ab 1.3.28 („Anwesenheit für andere Plugins bereitstellen“). Solange die Kopplung ein Gerät hält, greift die Automatik dort nicht; eine laufende Verschiebung lässt sie vorher los. Im Musterprojekt dann den Schalter „Niemand zu Hause (eigene Quelle)“ nicht verwenden, sonst arbeiten zwei Logiken nebeneinander.', 'The provider is BLE-Scanner NG from 1.3.28 (“Provide presence for other plugins”). As long as the coupling holds a device, the automation does not act there; a running shift is released first. In the sample project then do not use the switch “Niemand zu Hause (eigene Quelle)”, otherwise two logics work side by side.'),
 ('PRUEF_VK', 'Mit Sonnenstrom vorkühlen: eine Eingabe passt nicht (%s). Erlaubt sind: Einspeisung 100 bis 20000 W, Dauer 1 bis 120 Minuten, Bezug 0 bis 20000 W, Uhrzeit von 0 bis 23 und bis 1 bis 24 (von vor bis), außen −20 bis 50 °C oder leer, Raum 10 bis 40 °C oder leer, Solltemperatur 16 bis 30 °C, Mindestlaufzeit 0 bis 120 und Mindestpause 0 bis 240 Minuten, nur ganze Zahlen.', 'Pre-cool with solar power: an entry does not fit (%s). Allowed: feed-in 100 to 20000 W, duration 1 to 120 minutes, grid draw 0 to 20000 W, hour from 0 to 23 and until 1 to 24 (from before until), outdoor −20 to 50 °C or empty, room 10 to 40 °C or empty, set temperature 16 to 30 °C, minimum run time 0 to 120 and minimum pause 0 to 240 minutes, whole numbers only.'),
 ('VK_S', 'Mit Sonnenstrom vorkühlen (haus/energie, z. B. vom Smartmeter)', 'Pre-cool with solar power (haus/energie, e.g. from Smartmeter)'),
 ('VK_S_TEXT', 'Ab Werk für jedes Gerät <b>aus</b>. Eingeschaltet kühlt das Klimagerät mit Strom von Ihrer Solaranlage, den Sie sonst für wenige Cent ins Netz verkaufen würden – die Wohnung ist dann am Abend schon kühl. Das Plugin schaltet das Gerät dazu selbst <b>ein</b>, stellt <b>Kühlen</b> und die Solltemperatur ein und schaltet es später wieder <b>aus</b>. Es schaltet nur ein Gerät aus, das es selbst eingeschaltet hat; ein Gerät, das schon läuft, fasst es nicht an. Bedienen Sie das laufende Gerät selbst (ausschalten, andere Betriebsart oder Temperatur, ein Befehl aus Loxone), hat Ihre Hand Vorrang: das Plugin lässt das Gerät dann bis zum nächsten Tag in Ruhe.', '<b>Off</b> for every device by default. Switched on, the air conditioner cools with power from your solar system that you would otherwise sell to the grid for a few cents – the home is already cool in the evening. For this the plugin switches the device <b>on</b> itself, sets <b>cooling</b> and the set temperature, and later switches it <b>off</b> again. It only switches off a device it switched on itself; a device that is already running is left alone. If you operate the running device yourself (switch off, other mode or temperature, a command from Loxone), your hand takes precedence: the plugin leaves the device alone until the next day.'),
 ('VK_S_BEISPIEL', '<b>Beispiel:</b> Es ist 13 Uhr, draußen 27 °C, und Ihre Anlage speist seit 10 Minuten mehr als 800 W ins Netz ein. Das Plugin schaltet die Klimaanlage im Wohnzimmer auf Kühlen mit 23 °C. Ziehen Wolken auf und das Haus bezieht 5 Minuten lang mehr als 200 W aus dem Netz, schaltet es sie wieder aus – frühestens nach 20 Minuten Laufzeit, und eingeschaltet wird frühestens 15 Minuten später wieder.', '<b>Example:</b> it is 1 pm, 27 °C outside, and your system has been feeding more than 800 W into the grid for 10 minutes. The plugin switches the living room air conditioner to cooling at 23 °C. If clouds come up and the house draws more than 200 W from the grid for 5 minutes, it switches it off again – after 20 minutes of running at the earliest, and it switches on again 15 minutes later at the earliest.'),
 ('VK_OHNE_GERAETE', 'Noch kein Klimagerät gefunden – bitte zuerst im Reiter Einstellungen nach Geräten suchen.', 'No air conditioner found yet – please search for devices in the Settings tab first.'),
 ('VK_F_EIN', 'Mit Sonnenstrom vorkühlen', 'Pre-cool with solar power'),
 ('VK_F_AB', 'Einschalten bei Sonnenstrom-Überschuss ab', 'Switch on with solar surplus from'),
 ('VK_F_MINDESTENS', 'mindestens', 'for at least'),
 ('VK_F_AB_HILFE', 'Wählen Sie mindestens so viel, wie das Gerät beim Kühlen braucht (Typenschild, meist 500 bis 1200 W) – sonst kauft es den Rest aus dem Netz.', 'Choose at least as much as the device needs when cooling (type plate, usually 500 to 1200 W) – otherwise it buys the rest from the grid.'),
 ('VK_F_BEZUG', 'Ausschalten, wenn das Haus aus Netz oder Hausakku bezieht über', 'Switch off when the house draws from grid or home battery above'),
 ('VK_F_BEZUG_HILFE', 'Erst wenn das so lange anhält, wird ausgeschaltet – eine einzelne Wolke reicht nicht. Mit Hausakku (Smartmeter ab 2.8.19) zählt auch, was der Akku für das Haus abgibt.', 'Only when this lasts this long is the device switched off – a single cloud is not enough. With a home battery (Smartmeter from 2.8.19), what the battery delivers to the house counts as well.'),
 ('VK_F_FENSTER', 'Nur zwischen', 'Only between'),
 ('VK_UHR', 'Uhr', 'o’clock'),
 ('VK_F_AUSSEN', 'Nur ab Außentemperatur', 'Only from outdoor temperature'),
 ('VK_F_AUSSEN_HILFE', 'Leer = egal. Die Temperatur kommt vom Plugin Weatherdata (haus/wetter); ohne gültige Wetterdaten entfällt diese Bedingung.', 'Empty = any. The temperature comes from the Weatherdata plugin (haus/wetter); without valid weather data this condition is dropped.'),
 ('VK_F_RAUM', 'Nur ab Raumtemperatur', 'Only from room temperature'),
 ('VK_F_RAUM_HILFE', 'Leer = egal. Gemessen vom Klimagerät selbst; meldet es keine Raumtemperatur, entfällt die Bedingung.', 'Empty = any. Measured by the air conditioner itself; if it reports no room temperature, the condition is dropped.'),
 ('VK_F_SOLL', 'Solltemperatur beim Vorkühlen', 'Set temperature while pre-cooling'),
 ('VK_F_SCHUTZ', 'Schutz des Kompressors', 'Compressor protection'),
 ('VK_F_LAUF', 'läuft mindestens', 'runs at least'),
 ('VK_F_PAUSE', 'danach Pause mindestens', 'then pauses at least'),
 ('VK_F_SCHUTZ_HILFE', 'Häufiges Ein- und Ausschalten verschleißt den Kompressor. Vor Ablauf der Mindestlaufzeit wird nicht ausgeschaltet, vor Ablauf der Pause nicht wieder eingeschaltet.', 'Frequent switching wears the compressor. It is not switched off before the minimum run time, and not switched on again before the pause has passed.'),
 ('VK_F_ANW', 'Anwesenheit', 'Presence'),
 ('VK_ANW_EGAL', 'egal', 'any'),
 ('VK_ANW_DA', 'nur wenn jemand zu Hause ist', 'only when someone is at home'),
 ('VK_ANW_WEG', 'nur wenn niemand zu Hause ist', 'only when nobody is at home'),
 ('VK_F_PROGNOSE', 'PV-Prognose beachten', 'Observe PV forecast'),
 ('VK_F_PROGNOSE_HILFE', 'Ja = nicht einschalten, wenn die Prognose für die nächste Stunde (Weatherdata, haus/pv) unter der Einschaltschwelle liegt. Ohne gültige Prognose wird sie nicht beachtet.', 'Yes = do not switch on if the forecast for the next hour (Weatherdata, haus/pv) is below the switch-on threshold. Without a valid forecast it is ignored.'),
 ('VK_F_AKKU', 'Hausakku: Sonnenstrom, der gerade in den Akku geht, darf zum Vorkühlen genutzt werden', 'Home battery: solar power currently going into the battery may be used for pre-cooling'),
 ('VK_F_AKKU_HILFE', "Gilt nur, wenn der Smartmeter (ab 2.8.19) <span class='sm-mono'>haus/energie/frei_w</span> meldet – also auch Ihren Hausakku kennt. <b>Ja</b> (Vorgabe): Mittags erzeugt die Anlage 4.500 W, das Haus braucht 1.500 W, der Akku lädt mit 3.000 W, ins Netz geht nichts – das Plugin sieht 3.000 W übrig und kühlt vor; der Akku lädt dann eben etwas langsamer. <b>Nein</b>: Es zählt nur, was wirklich ins Netz fließt – im Beispiel 0 W, also kein Vorkühlen, solange der Akku lädt (erst wenn er voll ist und eingespeist wird). In <b>beiden</b> Fällen gilt: Muss der Akku das laufende Gerät versorgen (Beispiel abends: Akku gibt 1.500 W ab, aus dem Netz kommt nichts), wird ausgeschaltet – Akkustrom wird nicht verkühlt.", "Only applies if Smartmeter (from 2.8.19) reports <span class='sm-mono'>haus/energie/frei_w</span> – i.e. it also knows your home battery. <b>Yes</b> (default): at noon the system produces 4,500 W, the house needs 1,500 W, the battery charges with 3,000 W, nothing goes into the grid – the plugin sees 3,000 W left over and pre-cools; the battery then simply charges a bit more slowly. <b>No</b>: only what really flows into the grid counts – 0 W in the example, so no pre-cooling while the battery charges (only once it is full and feeds in). In <b>both</b> cases: if the battery has to supply the running device (example in the evening: battery delivers 1,500 W, nothing comes from the grid), the device is switched off – battery power is not spent on cooling."),
 ('VK_S_HINWEIS', "Einspeisung und Bezug kommen vom Plugin Smartmeter (dort Reiter MQTT: „Werte für andere Plugins bereitstellen (haus/energie)“); ab Smartmeter 2.8.19 auch <span class='sm-mono'>frei_w</span>, das einen Hausakku mitrechnet – dann gilt diese Größe, sonst Einspeisung und Bezug. Schweigt diese Quelle oder meldet sie keine frische Messung, wird <b>nichts eingeschaltet</b>; fällt sie während einer Vorkühlung länger als 5 Minuten aus, wird regulär ausgeschaltet. Bei offenem Fenster, solange die Anwesenheitskopplung oder die Automatik das Gerät hält, wird nicht eingeschaltet. Jede Aktion steht im Protokoll und kurz unter &lt;Präfix&gt;/vorkuehlen/meldung; der Reiter Test zeigt, worauf jedes Gerät wartet und welche Größe gilt. Der zweite Haken der MQTT-Befehle ist dafür nicht nötig: er schützt den Eingang für fremde Befehle, dieser Schalter hier ist Ihre Zustimmung.", "Feed-in and grid draw come from the Smartmeter plugin (there tab MQTT: “Provide values for other plugins (haus/energie)”); from Smartmeter 2.8.19 also <span class='sm-mono'>frei_w</span>, which includes a home battery – then this value applies, otherwise feed-in and grid draw. If this source is silent or reports no fresh measurement, <b>nothing is switched on</b>; if it fails for more than 5 minutes during pre-cooling, the device is switched off regularly. With an open window, or while the presence coupling or the automation holds the device, nothing is switched on. Every action is logged and briefly published under &lt;prefix&gt;/vorkuehlen/meldung; the Test tab shows what each device is waiting for and which value applies. The second tick of the MQTT commands is not needed for this: it protects the input for foreign commands, this switch here is your consent."),
 ('VK_LAGE_AUS', 'für kein Gerät eingeschaltet (ab Werk)', 'switched on for no device (default)'),
 ('VK_LAGE_STUMM', 'eingeschaltet, aber der Dienst meldet sich nicht (vorkuehlen.json fehlt oder ist älter als 180 s) – nach dem Speichern startet der Dienst neu', 'switched on, but the service does not report (vorkuehlen.json missing or older than 180 s) – the service restarts after saving'),
 ('VK_OHNE_MQTT', 'ohne MQTT hört der Dienst haus/energie nicht – es wird nichts eingeschaltet', 'without MQTT the service does not hear haus/energie – nothing is switched on'),
 ('VK_ENERGIE_OK', 'empfangen: Einspeisung %d W, Bezug %s W, zuletzt vor %d s', 'received: feed-in %d W, grid draw %s W, last %d s ago'),
 ('VK_ENERGIE_NIE', 'haus/energie hat noch nie gesendet – es wird nichts eingeschaltet. Anbieter: Smartmeter ab 2.8.18, dort „Werte für andere Plugins bereitstellen (haus/energie)“', 'haus/energie has never sent – nothing is switched on. Provider: Smartmeter from 2.8.18, there “Provide values for other plugins (haus/energie)”'),
 ('VK_ENERGIE_STILL', 'haus/energie schweigt seit %d s – es wird nichts eingeschaltet', 'haus/energie silent for %d s – nothing is switched on'),
 ('VK_ENERGIE_OK0', 'haus/energie lebt, aber ohne frische Messung (ok = %s, zuletzt vor %s s) – es wird nichts eingeschaltet', 'haus/energie alive, but without fresh measurement (ok = %s, last %s s ago) – nothing is switched on'),
 ('VK_ENERGIE_OK_FREI', 'empfangen: frei_w %d W (Quelle %s) – das gilt; dazu Einspeisung %s W, Bezug %s W, zuletzt vor %d s', 'received: frei_w %d W (source %s) – this applies; also feed-in %s W, grid draw %s W, last %d s ago'),
 ('VK_ENERGIE_OHNE_FREI', '– ohne frei_w (Smartmeter vor 2.8.19 oder Hausakku schweigt): es gelten Einspeisung und Bezug', '– without frei_w (Smartmeter before 2.8.19 or home battery silent): feed-in and grid draw apply'),
 ('VK_GROESSE_FREI', 'Sonnenstrom übrig (frei_w)', 'solar power left over (frei_w)'),
 ('VK_GROESSE_UEBER', 'Einspeisung (ueberschuss_w)', 'feed-in (ueberschuss_w)'),
 ('VK_GROESSE_BEZUG', 'Bezug (bezug_w)', 'grid draw (bezug_w)'),
 ('VK_GILT', 'Start nach %s, Stopp nach %s', 'start by %s, stop by %s'),
 ('VK_LAEUFT_SEIT', 'läuft seit %d min', 'running for %d min'),
 ('VK_GERAET_AUS', 'Schalter aus', 'switch off'),
 ('VK_WARTET', 'wartet: %s', 'waiting: %s'),
 ('VK_FELDER_GLEICH', '%d Felder gleich', '%d fields equal'),
 ('VK_FELDER_UNGLEICH', 'abweichend: %s', 'different: %s'),
],

# --- Welle Bild 19 (Midea2Lox 4.5.15, 18.10.2026; Entwurf Welle 19 md, E1-E18): drei Seiten aus dem
# LoxBerry-Plugins Musterprojekt im Reiter Einbindung, Schritt 6 - Tabellenzeilen Zn_mm = "Typ | Name |
# Parameter | Eingaenge" (Zeilen mit Prozentzeichen doppelt, ueber sprintf), Kaesten SEITEn_SCHRITTm
# (Klartext), Hinweise SEITEn_Hm (HTML); mi_bausteinliste() in htmlauth/index.php. Die alte Liste
# (50 Schluessel: 49 UI.BL_* und UI.OPTIONAL) ist entfallen.
'BAUSTEIN': [
 ('Z1_01', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_status_zaehler | Lebenszeichen: zählt bei jedem Herzschlag des Plugins (alle 60 s) eins weiter, 0 bis 999, läuft um; nie zurückbehalten; MQTT-Gateway Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_status_zaehler | Sign of life: counts up by one with every heartbeat of the plugin (every 60 s), 0 to 999, wraps around; never retained; MQTT gateway version 2: tick | —'),
 ('Z1_02', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_status_ok | letzte Geräteabfrage: 1 gelungen, 0 gescheitert, -1 noch keine; nie zurückbehalten; Fassung 2: Haken und „Noncached“ | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_status_ok | last device query: 1 succeeded, 0 failed, -1 none yet; never retained; version 2: tick and “Noncached” | —'),
 ('Z1_03', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_online | 1 = das Klimagerät hat bei der letzten Abfrage geantwortet, 0 = nicht (im eigenen Projekt steht hier die eigene Gerätenummer); kommt mit jeder Abfrage (im Plugin Abfragetakt 60 s); nie zurückbehalten; Fassung 2: Haken und „Noncached“ | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_online | 1 = the air conditioner answered the last query, 0 = not (in your own project your own device number stands here); arrives with every query (plugin polling interval 60 s); never retained; version 2: tick and “Noncached” | —'),
 ('Z1_04', 'Konstante | Konstante 1 | Wert 1 | —', 'Constant | Konstante 1 | Value 1 | —'),
 ('Z1_05', 'Analogwertvalidierung | Lebenszeichen fehlt (Midea) | Tmc 300 s (fünf Lebenszeichen à 60 s ohne neuen Wert), Min 0, Max 999 – steht der LoxBerry, das MQTT-Gateway oder der Dienst, bleibt der Zähler stehen; Haken bei ‚En‘ im Eigenschaftsfenster entfernen | V = #1, En = #4', 'Value Validator | Lebenszeichen fehlt (Midea) | Tmc 300 s (five signs of life of 60 s each without a new value), Min 0, Max 999 – if the LoxBerry, the MQTT gateway or the service stops, the counter stops; remove the tick at ‘En’ in the properties window | V = #1, En = #4'),
 ('Z1_06', 'NICHT | Keine frischen Daten (Midea) | — (das Klimagerät antwortet nicht) | I = #3', 'NOT | Keine frischen Daten (Midea) | — (the air conditioner does not answer) | I = #3'),
 ('Z1_07', 'ODER | Störung (Midea) | — (keine frischen Daten oder Lebenszeichen fehlt) | I1 = #6, I2 = Ausgang E von #5', 'OR | Störung (Midea) | — (no fresh data or sign of life missing) | I1 = #6, I2 = output E of #5'),
 ('Z1_08', 'Einschaltverzögerung | Störung bestätigt (Midea) | 600 s (zehn Lebenszeichen à 60 s, bei Abfragetakt 60 s zugleich zehn Geräteabfragen; eine einzelne verpasste Abfrage und ein Neustart melden nichts) | Eingang = #7', 'Switch-On Delay | Störung bestätigt (Midea) | 600 s (ten signs of life of 60 s each, with a polling interval of 60 s at the same time ten device polls; a single missed poll and a restart report nothing) | Input = #7'),
 ('Z1_09', 'Benachrichtigung | Meldung Plugin gestört (Midea) | Text: Midea2Lox – das Klimagerät antwortet seit über 10 Minuten nicht, oder das Plugin meldet sich seit etwa 15 Minuten nicht (LoxBerry, MQTT-Gateway oder Dienst angehalten). Werte in der App sind dann alt, Befehle wirken nicht. In der App den Status „Zustand (Midea)“ lesen, im Plugin Reiter Test „Zustand aller Geräte abfragen“ | Eingang = #8', 'Notification | Meldung Plugin gestört (Midea) | Text: Midea2Lox – the air conditioner has not answered for more than 10 minutes, or the plugin has not reported for about 15 minutes (LoxBerry, MQTT gateway or service stopped). Values in the app are old then, commands have no effect. Read the status “Zustand (Midea)” in the app, in the plugin tab Test “Query the state of all devices” | Input = #8'),
 ('Z1_10', 'Status | Zustand (Midea) | Zeilen: V1 = 1 „seit über 5 Minuten kein Lebenszeichen – LoxBerry, MQTT-Gateway (Fassung 1: Abo Midea2Lox/#, Fassung 2: Haken an Midea2Lox/status/zaehler) und Dienst prüfen; im Plugin Reiter Test ‚Umgebung prüfen‘“; V3 < 0 „das Plugin läuft, hat aber noch kein Klimagerät abgefragt – im Plugin Reiter Test ‚Jetzt nach Geräten suchen‘, dann Reiter Einstellungen ‚Abfragetakt‘ 60 eintragen“; V2 = 0 „das Klimagerät antwortet nicht – Strom und WLAN des Geräts prüfen; im Plugin Reiter Test ‚Zustand aller Geräte abfragen‘“; ohne Bedingung „läuft – Klimagerät erreichbar, Lebenszeichen <v4>“; Visualisierung EIN | V1 = Ausgang E von #5, V2 = #3, V3 = #2, V4 = #1', 'Status | Zustand (Midea) | Rows: V1 = 1 “no sign of life for more than 5 minutes – check LoxBerry, MQTT gateway (version 1: subscription Midea2Lox/#, version 2: tick at Midea2Lox/status/zaehler) and service; in the plugin tab Test ‘Check environment’”; V3 < 0 “the plugin runs but has not polled an air conditioner yet – in the plugin tab Test ‘Search for devices now’, then enter 60 at ‘Polling interval’ in the tab Settings”; V2 = 0 “the air conditioner does not answer – check power and Wi-Fi of the device; in the plugin tab Test ‘Query the state of all devices’”; without condition “running – air conditioner reachable, sign of life <v4>”; visualisation ON | V1 = output E of #5, V2 = #3, V3 = #2, V4 = #1'),
 ('Z1_11', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_power_state | 1 = Gerät eingeschaltet, 0 = aus (auch am Gerät oder mit der Fernbedienung geschaltet), -1 = das Gerät meldet keinen Zustand; zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_power_state | 1 = device switched on, 0 = off (also switched at the device or with the remote control), -1 = the device reports no state; retained; gateway version 2: tick | —'),
 ('Z1_12', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_indoor_temperature | Raumtemperatur am Innengerät in °C; -999 = das Gerät liefert keinen Raumwert; nie zurückbehalten; Statistik ein; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_indoor_temperature | room temperature at the indoor unit in °C; -999 = the device supplies no room value; never retained; statistics on; gateway version 2: tick | —'),
 ('Z1_13', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_outdoor_temperature | Temperatur am Außengerät in °C; -999 = das Gerät liefert keinen Außenwert (manche Geräte nur bei laufendem Außengerät); nie zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_outdoor_temperature | temperature at the outdoor unit in °C; -999 = the device supplies no outdoor value (some devices only while the outdoor unit runs); never retained; gateway version 2: tick | —'),
 ('Z1_14', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_target_temperature | Solltemperatur, die das Gerät gerade hat, in °C; -999 = das Gerät nennt keinen Sollwert; zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_target_temperature | target temperature the device currently has, in °C; -999 = the device names no target value; retained; gateway version 2: tick | —'),
 ('Z1_15', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_indoor_humidity | Raumfeuchte in Proz.; -1 bei Geräten ohne Feuchtefühler; nie zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_indoor_humidity | room humidity in per cent; -1 for devices without a humidity sensor; never retained; gateway version 2: tick | —'),
 ('Z1_16', 'Virtueller Eingang (Schalter) | Klima ein (Midea) | in der App: 1 = Klimagerät einschalten, 0 = ausschalten; Startwert aus | —', 'Virtual Input (Switch) | Klima ein (Midea) | in the app: 1 = switch the air conditioner on, 0 = off; start value off | —'),
 ('Z1_17', 'Virtueller Eingang (Schalter) | Fenster offen (eigene Quelle) | 1 = ein Fenster im Raum des Klimageräts ist offen; in der App zum Ausprobieren; im eigenen Projekt die Leitung vom eigenen Fensterkontakt statt dieses Schalters an Nr. 18 legen; alternativ schaltet das Plugin selbst aus (Reiter Automatik „Fenster offen → Gerät aus“, Fensterkontakt über haus/tuer/…/offen, z. B. von Matter2Lox) | —', 'Virtual Input (Switch) | Fenster offen (eigene Quelle) | 1 = a window in the room of the air conditioner is open; in the app for trying it out; in your own project connect your own window contact to no. 18 instead of this switch; alternatively the plugin switches off by itself (tab Automation “Window open → device off”, window contact via haus/tuer/…/offen, e.g. from Matter2Lox) | —'),
 ('Z1_18', 'Einschaltverzögerung | Fenster länger offen (Midea) | 60 s (kurzes Lüften schaltet das Gerät nicht aus) | Eingang = #17', 'Switch-On Delay | Fenster länger offen (Midea) | 60 s (airing briefly does not switch the device off) | Input = #17'),
 ('Z1_19', 'Virtueller Eingang (Schalter) | Niemand zu Hause (eigene Quelle) | 1 = alle sind weg (weitere Instanz, derselbe Platzhalter wie auf „Alexa NG“, „Intercom“ und „Kodi-NG Wiedergabe“); im eigenen Projekt die Leitung von der eigenen Anwesenheit statt dieses Schalters an Nr. 20 legen; alternativ im Plugin „Anwesenheit berücksichtigen“ (haus/anwesenheit/jemand vom BLE-Scanner NG, Reiter Automatik) – dann diesen Schalter nicht verwenden, sonst arbeiten zwei Logiken nebeneinander | —', 'Virtual Input (Switch) | Niemand zu Hause (eigene Quelle) | 1 = everybody is away (further instance, the same placeholder as on “Alexa NG”, “Intercom” and “Kodi-NG Wiedergabe”); in your own project connect your own presence to no. 20 instead of this switch; alternatively “Consider presence” in the plugin (haus/anwesenheit/jemand from BLE-Scanner NG, tab Automation) – then do not use this switch, otherwise two logics work side by side | —'),
 ('Z1_20', 'UND | Klima darf laufen (Midea) | — (beide Eingänge negiert: in Config auf den Eingangspunkt klicken, es erscheint ein kleiner Kreis; 1 = kein Fenster länger offen und jemand zu Hause) | I1 = #18 (negiert), I2 = #19 (negiert)', 'AND | Klima darf laufen (Midea) | — (both inputs inverted: in Config click the input point, a small circle appears; 1 = no window open for long and somebody at home) | I1 = #18 (inverted), I2 = #19 (inverted)'),
 ('Z1_21', 'UND | Klima einschalten (Midea) | — (Schalter ein und Freigabe) | I1 = #16, I2 = #20', 'AND | Klima einschalten (Midea) | — (switch on and release) | I1 = #16, I2 = #20'),
 ('Z1_22', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Ein- und ausschalten | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/ein 1, bei AUS: publish Midea2Lox/befehl/123456789012/ein 0 (nie retain; im eigenen Projekt die eigene Gerätenummer); auch wenn das Fenster aufgeht oder alle gehen; danach wieder ein, solange der Schalter ein ist; wirkt nur mit den Plugin-Haken „Befehle über MQTT annehmen“ UND „Ein/Aus, Betriebsart, Frostschutz und Selbstreinigung über MQTT zulassen“ (Reiter MQTT) | Eingang = #21', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Ein- und ausschalten | Command for ON: publish Midea2Lox/befehl/123456789012/ein 1, for OFF: publish Midea2Lox/befehl/123456789012/ein 0 (never retain; in your own project your own device number); also when the window opens or everybody leaves; afterwards on again as long as the switch is on; works only with the plugin ticks “Befehle über MQTT annehmen” AND “Ein/Aus, Betriebsart, Frostschutz und Selbstreinigung über MQTT zulassen” (tab MQTT) | Input = #21'),
 ('Z1_23', 'Virtueller Eingang (Schieberegler) | Solltemperatur (Midea) | Min 16, Max 30, Schritt 0,5, Startwert 22 (°C); in der App | —', 'Virtual Input (Slider) | Solltemperatur (Midea) | Min 16, Max 30, step 0.5, start value 22 (°C); in the app | —'),
 ('Z1_24', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Solltemperatur | Befehl bei Analogwert: publish Midea2Lox/befehl/123456789012/soll <v.1> (°C, halbe Grad gehen; nie retain); ein Wert außerhalb des Gerätebereichs wird vom Plugin verworfen; wirkt nur mit dem Plugin-Haken „Befehle über MQTT annehmen“ | Eingang = #23', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Solltemperatur | Command for analogue value: publish Midea2Lox/befehl/123456789012/soll <v.1> (°C, half degrees work; never retain); a value outside the device range is discarded by the plugin; works only with the plugin tick “Befehle über MQTT annehmen” | Input = #23'),
 ('Z1_25', 'Status | Klima (Midea) | Zeilen: V1 < 0 „Zustand unbekannt – das Gerät meldet nicht, ob es läuft; Status ‚Zustand (Midea)‘ lesen“; V2 < -100 „Raumtemperatur fehlt – das Gerät liefert keinen Raumwert; im Plugin Reiter Test ‚Zustand aller Geräte abfragen‘“; V1 = 1 und V4 < -100 „läuft – Raum <v2.1> °C, Soll <v3.1> °C (die Außentemperatur liefert das Gerät gerade nicht)“; V1 = 1 und V5 < 0 „läuft – Raum <v2.1> °C, Soll <v3.1> °C, außen <v4.1> °C“; V1 = 1 „läuft – Raum <v2.1> °C, Soll <v3.1> °C, außen <v4.1> °C, Feuchte <v5> Proz.“; V6 = 0 und V4 < -100 „aus – Raum <v2.1> °C“; V6 = 0 „aus – Raum <v2.1> °C, außen <v4.1> °C“; V7 = 0 „gesperrt – Fenster länger als 1 Minute offen oder niemand zu Hause; schaltet von selbst wieder ein“; ohne Bedingung „eingeschaltet, das Gerät meldet aber aus – am Gerät oder mit der Fernbedienung ausgeschaltet, oder im Plugin fehlen die Haken für MQTT-Befehle? Schalter ‚Klima ein (Midea)‘ aus- und wieder einschalten“; Visualisierung EIN | V1 = #11, V2 = #12, V3 = #14, V4 = #13, V5 = #15, V6 = #16, V7 = #20', 'Status | Klima (Midea) | Rows: V1 < 0 “state unknown – the device does not report whether it runs; read status ‘Zustand (Midea)’”; V2 < -100 “room temperature missing – the device supplies no room value; in the plugin tab Test ‘Query the state of all devices’”; V1 = 1 and V4 < -100 “running – room <v2.1> °C, target <v3.1> °C (the device currently supplies no outdoor temperature)”; V1 = 1 and V5 < 0 “running – room <v2.1> °C, target <v3.1> °C, outside <v4.1> °C”; V1 = 1 “running – room <v2.1> °C, target <v3.1> °C, outside <v4.1> °C, humidity <v5> per cent”; V6 = 0 and V4 < -100 “off – room <v2.1> °C”; V6 = 0 “off – room <v2.1> °C, outside <v4.1> °C”; V7 = 0 “blocked – window open for more than 1 minute or nobody at home; switches on again by itself”; without condition “switched on, but the device reports off – switched off at the device or with the remote control, or are the ticks for MQTT commands missing in the plugin? Switch ‘Klima ein (Midea)’ off and on again”; visualisation ON | V1 = #11, V2 = #12, V3 = #14, V4 = #13, V5 = #15, V6 = #16, V7 = #20'),
 ('Z1_26', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_automatik_aktiv | 1 = die Automatik des Plugins verschiebt gerade die Solltemperatur (günstiger Strom oder PV-Überschuss); nur mit eingeschalteter Automatik (Reiter Automatik, ab Werk aus); nie zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_automatik_aktiv | 1 = the automation of the plugin is shifting the target temperature right now (cheap power or PV surplus); only with the automation switched on (tab Automation, off by default); never retained; gateway version 2: tick | —'),
 ('Z1_27', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_automatik_gesperrt | Sekunden, die die Automatik nach einem Befehl aus Loxone noch ruht (Handvorrang, ab Werk 120 min); nie zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_automatik_gesperrt | seconds the automation still rests after a command from Loxone (manual priority, 120 min by default); never retained; gateway version 2: tick | —'),
 ('Z1_28', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_automatik_geraete | Zahl der Geräte, deren Solltemperatur die Automatik gerade verschiebt; nie zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_automatik_geraete | number of devices whose target temperature the automation is shifting right now; never retained; gateway version 2: tick | —'),
 ('Z1_29', 'Virtueller Texteingang | Midea2Lox_automatik_grund | von Hand anlegen, Name genau so (Name, den das MQTT-Gateway vergibt), „In Visualisierung verwenden“ an; Klartext, warum die Automatik greift oder nicht; nur mit eingeschalteter Automatik; nie zurückbehalten; Fassung 2: Haken | —', 'Virtual Text Input | Midea2Lox_automatik_grund | create by hand, name exactly like this (the name the MQTT gateway assigns), “Use in User Interface” on; plain text why the automation acts or not; only with the automation switched on; never retained; gateway version 2: tick | —'),
 ('Z1_30', 'Status | Automatik (Midea) | Zeilen: V5 = 1 „Abwesenheit – das Plugin hält die Klimageräte sparsam (Sollwert verschoben, Sparbetrieb oder aus – Reiter Automatik ‚Anwesenheit‘); bei der Rückkehr stellt es zurück, was es verstellt hat“; V5 < 0 „Anwesenheit eingeschaltet, aber die Quelle schweigt – es gilt das Verhalten ohne Anwesenheit; im Plugin Reiter Test die Zeile ‚Anwesenheit‘ lesen“; V2 > 0 „Handvorrang – die Automatik ruht noch <v2> s (jeder Befehl aus Loxone setzt sie aus)“; V1 = 1 „greift – verschiebt die Solltemperatur an <v3> Gerät(en): <v4>“; ohne Bedingung „greift nicht: <v4> – einschalten im Plugin Reiter Automatik“; Visualisierung EIN | V1 = #26, V2 = #27, V3 = #28, V4 = #29, V5 = #31', 'Status | Automatik (Midea) | Rows: V5 = 1 “away – the plugin keeps the air conditioners economical (target shifted, eco mode or off – tab Automation ‘Presence’); on return it restores what it changed”; V5 < 0 “presence switched on, but the source is silent – the behaviour without presence applies; in the plugin tab Test read the row ‘Presence’”; V2 > 0 “manual priority – the automation still rests <v2> s (every command from Loxone suspends it)”; V1 = 1 “acting – shifts the target temperature of <v3> device(s): <v4>”; without condition “not acting: <v4> – switch it on in the plugin tab Automation”; visualisation ON | V1 = #26, V2 = #27, V3 = #28, V4 = #29, V5 = #31'),
 ('Z2_01', 'Radiotasten | Betriebsart (Midea) | Taste 1 „Automatik“, Taste 2 „Kühlen“, Taste 3 „Heizen“, Taste 4 „Entfeuchten“, Taste 5 „nur Lüften“; Text für „keine Taste gewählt“: „wie am Gerät“; Remanenz aus (nach einem Neustart des Miniservers wird nichts geschickt) | —', 'Radio Buttons | Betriebsart (Midea) | Button 1 “Automatik”, button 2 “Kühlen”, button 3 “Heizen”, button 4 “Entfeuchten”, button 5 “nur Lüften”; text for “no button selected”: “wie am Gerät”; remanence off (after a restart of the Miniserver nothing is sent) | —'),
 ('Z2_02', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Betriebsart Automatik | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/betriebsart automatik (nie retain); das Gerät stellt dann auch die Lüfterstufe selbst; wirkt nur mit den Plugin-Haken „Befehle über MQTT annehmen“ UND „Ein/Aus, Betriebsart, Frostschutz und Selbstreinigung über MQTT zulassen“ | Eingang = Ausgang Q1 von #1', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Betriebsart Automatik | Command for ON: publish Midea2Lox/befehl/123456789012/betriebsart automatik (never retain); the device then also sets the fan speed itself; works only with the plugin ticks “Befehle über MQTT annehmen” AND “Ein/Aus, Betriebsart, Frostschutz und Selbstreinigung über MQTT zulassen” | Input = output Q1 of #1'),
 ('Z2_03', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Betriebsart Kühlen | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/betriebsart kuehlen (nie retain); Haken wie Nr. 2 | Eingang = Ausgang Q2 von #1', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Betriebsart Kühlen | Command for ON: publish Midea2Lox/befehl/123456789012/betriebsart kuehlen (never retain); ticks as no. 2 | Input = output Q2 of #1'),
 ('Z2_04', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Betriebsart Heizen | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/betriebsart heizen (nie retain); Haken wie Nr. 2 | Eingang = Ausgang Q3 von #1', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Betriebsart Heizen | Command for ON: publish Midea2Lox/befehl/123456789012/betriebsart heizen (never retain); ticks as no. 2 | Input = output Q3 of #1'),
 ('Z2_05', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Betriebsart Entfeuchten | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/betriebsart entfeuchten (nie retain); mit Feuchteregelung bis zur Sollfeuchte Nr. 19; Haken wie Nr. 2 | Eingang = Ausgang Q4 von #1', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Betriebsart Entfeuchten | Command for ON: publish Midea2Lox/befehl/123456789012/betriebsart entfeuchten (never retain); with humidity control up to the target humidity no. 19; ticks as no. 2 | Input = output Q4 of #1'),
 ('Z2_06', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Betriebsart nur Lüften | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/betriebsart lueften (nie retain); nur Lüften, ohne Kühlen und Heizen; Haken wie Nr. 2 | Eingang = Ausgang Q5 von #1', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Betriebsart nur Lüften | Command for ON: publish Midea2Lox/befehl/123456789012/betriebsart lueften (never retain); fan only, without cooling and heating; ticks as no. 2 | Input = output Q5 of #1'),
 ('Z2_07', 'Radiotasten | Lüfterstufe (Midea) | Taste 1 „Automatik“, Taste 2 „leise“, Taste 3 „niedrig“, Taste 4 „mittel“, Taste 5 „hoch“, Taste 6 „höchste“; Text für „keine Taste gewählt“: „wie am Gerät“; Remanenz aus | —', 'Radio Buttons | Lüfterstufe (Midea) | Button 1 “Automatik”, button 2 “leise”, button 3 “niedrig”, button 4 “mittel”, button 5 “hoch”, button 6 “höchste”; text for “no button selected”: “wie am Gerät”; remanence off | —'),
 ('Z2_08', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Lüfterstufe Automatik | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/luefter automatik (nie retain); wirkt nur mit dem Plugin-Haken „Befehle über MQTT annehmen“ | Eingang = Ausgang Q1 von #7', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Lüfterstufe Automatik | Command for ON: publish Midea2Lox/befehl/123456789012/luefter automatik (never retain); works only with the plugin tick “Befehle über MQTT annehmen” | Input = output Q1 of #7'),
 ('Z2_09', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Lüfterstufe leise | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/luefter leise (nie retain); in der Betriebsart Automatik stellt das Gerät zurück auf Automatik; Haken wie Nr. 8 | Eingang = Ausgang Q2 von #7', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Lüfterstufe leise | Command for ON: publish Midea2Lox/befehl/123456789012/luefter leise (never retain); in the operating mode automatic the device returns to automatic; ticks as no. 8 | Input = output Q2 of #7'),
 ('Z2_10', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Lüfterstufe niedrig | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/luefter niedrig (nie retain); Haken wie Nr. 8 | Eingang = Ausgang Q3 von #7', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Lüfterstufe niedrig | Command for ON: publish Midea2Lox/befehl/123456789012/luefter niedrig (never retain); ticks as no. 8 | Input = output Q3 of #7'),
 ('Z2_11', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Lüfterstufe mittel | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/luefter mittel (nie retain); Haken wie Nr. 8 | Eingang = Ausgang Q4 von #7', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Lüfterstufe mittel | Command for ON: publish Midea2Lox/befehl/123456789012/luefter mittel (never retain); ticks as no. 8 | Input = output Q4 of #7'),
 ('Z2_12', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Lüfterstufe hoch | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/luefter hoch (nie retain); Haken wie Nr. 8 | Eingang = Ausgang Q5 von #7', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Lüfterstufe hoch | Command for ON: publish Midea2Lox/befehl/123456789012/luefter hoch (never retain); ticks as no. 8 | Input = output Q5 of #7'),
 ('Z2_13', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Lüfterstufe höchste | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/luefter hoechste (nie retain); höchste Lüfterstufe; Haken wie Nr. 8 | Eingang = Ausgang Q6 von #7', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Lüfterstufe höchste | Command for ON: publish Midea2Lox/befehl/123456789012/luefter hoechste (never retain); highest fan speed; ticks as no. 8 | Input = output Q6 of #7'),
 ('Z2_14', 'Radiotasten | Schwenken (Midea) | Taste 1 „aus“, Taste 2 „senkrecht“, Taste 3 „waagerecht“, Taste 4 „beide Richtungen“; Text für „keine Taste gewählt“: „wie am Gerät“; Remanenz aus | —', 'Radio Buttons | Schwenken (Midea) | Button 1 “aus”, button 2 “senkrecht”, button 3 “waagerecht”, button 4 “beide Richtungen”; text for “no button selected”: “wie am Gerät”; remanence off | —'),
 ('Z2_15', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Schwenken aus | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/schwenken aus (nie retain); Luftlamellen stehen; Haken wie Nr. 8 | Eingang = Ausgang Q1 von #14', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Schwenken aus | Command for ON: publish Midea2Lox/befehl/123456789012/schwenken aus (never retain); louvres stand still; ticks as no. 8 | Input = output Q1 of #14'),
 ('Z2_16', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Schwenken senkrecht | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/schwenken senkrecht (nie retain); Lamellen schwenken auf und ab; Haken wie Nr. 8 | Eingang = Ausgang Q2 von #14', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Schwenken senkrecht | Command for ON: publish Midea2Lox/befehl/123456789012/schwenken senkrecht (never retain); louvres swing up and down; ticks as no. 8 | Input = output Q2 of #14'),
 ('Z2_17', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Schwenken waagerecht | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/schwenken waagerecht (nie retain); Lamellen schwenken nach links und rechts; Haken wie Nr. 8 | Eingang = Ausgang Q3 von #14', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Schwenken waagerecht | Command for ON: publish Midea2Lox/befehl/123456789012/schwenken waagerecht (never retain); louvres swing left and right; ticks as no. 8 | Input = output Q3 of #14'),
 ('Z2_18', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Schwenken in beide Richtungen | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/schwenken beide (nie retain); Lamellen schwenken in beide Richtungen; Haken wie Nr. 8 | Eingang = Ausgang Q4 von #14', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Schwenken in beide Richtungen | Command for ON: publish Midea2Lox/befehl/123456789012/schwenken beide (never retain); louvres swing in both directions; ticks as no. 8 | Input = output Q4 of #14'),
 ('Z2_19', 'Virtueller Eingang (Schieberegler) | Sollfeuchte (Midea) | Min 35, Max 70, Schritt 5, Startwert 50 (Proz.); in der App; wirkt in der Betriebsart Entfeuchten | —', 'Virtual Input (Slider) | Sollfeuchte (Midea) | Min 35, max 70, step 5, start value 50 (per cent); in the app; works in the operating mode dehumidify | —'),
 ('Z2_20', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Sollfeuchte | Befehl bei Analogwert: publish Midea2Lox/befehl/123456789012/feuchte <v.0> (ganze Proz.; nie retain): Sollfeuchte; nur Geräte mit Feuchteregelung, andere übergehen den Befehl; Haken wie Nr. 8 | Eingang = #19', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Sollfeuchte | Command for analogue value: publish Midea2Lox/befehl/123456789012/feuchte <v.0> (whole per cent; never retain): target humidity; only devices with humidity control, others ignore the command; ticks as no. 8 | Input = #19'),
 ('Z2_21', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_target_humidity | Sollfeuchte, die das Gerät gerade hat, in Proz.; -1 = das Gerät nennt keine (ohne Feuchteregelung); zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_target_humidity | target humidity the device currently has, in per cent; -1 = the device names none (without humidity control); retained; gateway version 2: tick | —'),
 ('Z2_22', 'Virtueller Texteingang | Midea2Lox_123456789012_operational_mode | von Hand anlegen, Name genau so (Name, den das MQTT-Gateway vergibt), „In Visualisierung verwenden“ an; Betriebsart, wie das Gerät sie meldet: „operational_mode_enum.auto/cool/heat/dry/fan_only“, „-“ = meldet keine; zurückbehalten; Fassung 2: Haken; erscheint im Status Nr. 27 | —', 'Virtual Text Input | Midea2Lox_123456789012_operational_mode | create by hand, name exactly like this (the name the MQTT gateway assigns), “Use in User Interface” on; operating mode as the device reports it: “operational_mode_enum.auto/cool/heat/dry/fan_only”, “-” = reports none; retained; gateway version 2: tick; appears in status no. 27 | —'),
 ('Z2_23', 'Virtueller Texteingang | Midea2Lox_123456789012_fan_speed | von Hand anlegen, Name genau so, „In Visualisierung verwenden“ an; Lüfterstufe: „fan_speed_enum.Auto/Silent/Low/Medium/High/Full“ (manche Geräte eine Zahl), „-“ = meldet keine; zurückbehalten; Fassung 2: Haken; erscheint im Status Nr. 27 | —', 'Virtual Text Input | Midea2Lox_123456789012_fan_speed | create by hand, name exactly like this, “Use in User Interface” on; fan speed: “fan_speed_enum.Auto/Silent/Low/Medium/High/Full” (some devices a number), “-” = reports none; retained; gateway version 2: tick; appears in status no. 27 | —'),
 ('Z2_24', 'Virtueller Texteingang | Midea2Lox_123456789012_swing_mode | von Hand anlegen, Name genau so, „In Visualisierung verwenden“ an; Schwenken: „swing_mode_enum.Off/Vertical/Horizontal/Both“, „-“ = meldet keine; zurückbehalten; Fassung 2: Haken; erscheint im Status Nr. 27 | —', 'Virtual Text Input | Midea2Lox_123456789012_swing_mode | create by hand, name exactly like this, “Use in User Interface” on; swing: “swing_mode_enum.Off/Vertical/Horizontal/Both”, “-” = reports none; retained; gateway version 2: tick; appears in status no. 27 | —'),
 ('Z2_25', 'Virtueller Eingang (Taste) | Jetzt abfragen (Midea) | in der App: alle Werte des Klimageräts sofort neu holen (sonst einmal je Minute über den Abfragetakt des Plugins) | —', 'Virtual Input (Push Button) | Jetzt abfragen (Midea) | in the app: fetch all values of the air conditioner right now (otherwise once per minute through the polling interval of the plugin) | —'),
 ('Z2_26', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Zustand abfragen | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/abfragen 1 (nie retain); Gerät abfragen, die Werte kommen über das MQTT-Gateway zurück; setzt die Automatik nicht aus; Haken wie Nr. 8 | Eingang = #25', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Zustand abfragen | Command for ON: publish Midea2Lox/befehl/123456789012/abfragen 1 (never retain); query the device, the values come back via the MQTT gateway; does not suspend the automation; ticks as no. 8 | Input = #25'),
 ('Z2_27', 'Status | Betrieb (Midea) | Zeilen: V1 = 1 „Automatik gewählt – das Gerät wählt Kühlen oder Heizen und die Lüfterstufe selbst; es meldet <v4>, <v5>“; V1 = 2 „Kühlen gewählt – das Gerät meldet <v4>, <v5>, <v6>“; V1 = 3 „Heizen gewählt – das Gerät meldet <v4>, <v5>, <v6>“; V1 = 4 „Entfeuchten gewählt – Sollfeuchte <v2> Proz., das Gerät meldet <v3> Proz. (-1 = ohne Feuchteregelung)“; V1 = 5 „nur Lüften gewählt – das Gerät meldet <v5>, <v6>“; ohne Bedingung „in der App noch keine Betriebsart gewählt – das Gerät meldet <v4>, <v5>, <v6>“; Visualisierung EIN | V1 = #1, V2 = #19, V3 = #21, V4 = #22, V5 = #23, V6 = #24', 'Status | Betrieb (Midea) | Rows: V1 = 1 “automatic selected – the device chooses cooling or heating and the fan speed itself; it reports <v4>, <v5>”; V1 = 2 “cooling selected – the device reports <v4>, <v5>, <v6>”; V1 = 3 “heating selected – the device reports <v4>, <v5>, <v6>”; V1 = 4 “dehumidify selected – target humidity <v2> per cent, the device reports <v3> per cent (-1 = without humidity control)”; V1 = 5 “fan only selected – the device reports <v5>, <v6>”; without condition “no operating mode selected in the app yet – the device reports <v4>, <v5>, <v6>”; visualisation ON | V1 = #1, V2 = #19, V3 = #21, V4 = #22, V5 = #23, V6 = #24'),
 ('Z3_01', 'Virtueller Eingang (Schalter) | Sparbetrieb (Midea) | in der App: 1 = Sparbetrieb ein, 0 = aus; Startwert aus | —', 'Virtual Input (Switch) | Sparbetrieb (Midea) | in the app: 1 = eco mode on, 0 = off; start value off | —'),
 ('Z3_02', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Sparbetrieb | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/spar 1, bei AUS: publish Midea2Lox/befehl/123456789012/spar 0 (nie retain); nur Geräte, die es können; wirkt nur mit dem Plugin-Haken „Befehle über MQTT annehmen“ | Eingang = #1', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Sparbetrieb | Command for ON: publish Midea2Lox/befehl/123456789012/spar 1, for OFF: publish Midea2Lox/befehl/123456789012/spar 0 (never retain); only devices that can do it; works only with the plugin tick “Befehle über MQTT annehmen” | Input = #1'),
 ('Z3_03', 'Virtueller Eingang (Schalter) | Schnellbetrieb (Midea) | in der App: 1 = volle Leistung zum schnellen Kühlen oder Heizen; Startwert aus | —', 'Virtual Input (Switch) | Schnellbetrieb (Midea) | in the app: 1 = full power for fast cooling or heating; start value off | —'),
 ('Z3_04', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Schnellbetrieb | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/schnell 1, bei AUS: … schnell 0 (nie retain); nur Geräte, die es können; Haken wie Nr. 2 | Eingang = #3', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Schnellbetrieb | Command for ON: publish Midea2Lox/befehl/123456789012/schnell 1, for OFF: … schnell 0 (never retain); only devices that can do it; ticks as no. 2 | Input = #3'),
 ('Z3_05', 'Virtueller Eingang (Schalter) | Nachtbetrieb (Midea) | in der App: 1 = leiser Nachtbetrieb, Sollwert wandert langsam; Startwert aus | —', 'Virtual Input (Switch) | Nachtbetrieb (Midea) | in the app: 1 = quiet sleep mode, the setpoint drifts slowly; start value off | —'),
 ('Z3_06', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Nachtbetrieb | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/nacht 1, bei AUS: … nacht 0 (nie retain); Haken wie Nr. 2 | Eingang = #5', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Nachtbetrieb | Command for ON: publish Midea2Lox/befehl/123456789012/nacht 1, for OFF: … nacht 0 (never retain); ticks as no. 2 | Input = #5'),
 ('Z3_07', 'Virtueller Eingang (Schalter) | Frostschutz (Midea) | in der App: 1 = Frostschutz (das Gerät heizt auf etwa 8 °C, z. B. im leeren Ferienhaus); Startwert aus | —', 'Virtual Input (Switch) | Frostschutz (Midea) | in the app: 1 = freeze protection (the device heats to about 8 °C, e.g. in an empty holiday home); start value off | —'),
 ('Z3_08', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Frostschutz | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/frostschutz 1 – das Plugin stellt dazu Heizen ein; bei AUS: … frostschutz 0 (nie retain); nur Geräte, die es können; wirkt nur mit den Plugin-Haken „Befehle über MQTT annehmen“ UND „Ein/Aus, Betriebsart, Frostschutz und Selbstreinigung über MQTT zulassen“ | Eingang = #7', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Frostschutz | Command for ON: publish Midea2Lox/befehl/123456789012/frostschutz 1 – the plugin also sets heating; for OFF: … frostschutz 0 (never retain); only devices that can do it; works only with the plugin ticks “Befehle über MQTT annehmen” AND “Ein/Aus, Betriebsart, Frostschutz und Selbstreinigung über MQTT zulassen” | Input = #7'),
 ('Z3_09', 'Virtueller Eingang (Schalter) | Luftreinigung (Midea) | in der App: 1 = Luftreinigung (Ionisator) ein; Startwert aus | —', 'Virtual Input (Switch) | Luftreinigung (Midea) | in the app: 1 = air purification (ioniser) on; start value off | —'),
 ('Z3_10', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Luftreinigung | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/luftreinigung 1, bei AUS: … luftreinigung 0 (nie retain); nur Geräte, die es können; Haken wie Nr. 2 | Eingang = #9', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Luftreinigung | Command for ON: publish Midea2Lox/befehl/123456789012/luftreinigung 1, for OFF: … luftreinigung 0 (never retain); only devices that can do it; ticks as no. 2 | Input = #9'),
 ('Z3_11', 'Virtueller Eingang (Schalter) | Regelung nach Fernbedienung (Midea) | in der App: 1 = das Gerät regelt nach dem Fühler in der Fernbedienung statt nach seinem eigenen; Startwert aus | —', 'Virtual Input (Switch) | Regelung nach Fernbedienung (Midea) | in the app: 1 = the device controls by the sensor in the remote control instead of its own; start value off | —'),
 ('Z3_12', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Regelung nach Fernbedienung | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/fernbedienung 1, bei AUS: … fernbedienung 0 (nie retain); Haken wie Nr. 2 | Eingang = #11', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Regelung nach Fernbedienung | Command for ON: publish Midea2Lox/befehl/123456789012/fernbedienung 1, for OFF: … fernbedienung 0 (never retain); ticks as no. 2 | Input = #11'),
 ('Z3_13', 'Virtueller Eingang (Schalter) | Quittungston (Midea) | in der App: 1 = das Gerät piept bei jedem Befehl, 0 = still; Startwert aus | —', 'Virtual Input (Switch) | Quittungston (Midea) | in the app: 1 = the device beeps with every command, 0 = silent; start value off | —'),
 ('Z3_14', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Quittungston | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/ton 1, bei AUS: … ton 0 (nie retain); Haken wie Nr. 2 | Eingang = #13', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Quittungston | Command for ON: publish Midea2Lox/befehl/123456789012/ton 1, for OFF: … ton 0 (never retain); ticks as no. 2 | Input = #13'),
 ('Z3_15', 'Virtueller Eingang (Taste) | Anzeige umschalten (Midea) | in der App: die Anzeige am Innengerät an- bzw. ausschalten (jeder Druck wechselt) | —', 'Virtual Input (Push Button) | Anzeige umschalten (Midea) | in the app: switch the display on the indoor unit on or off (every press toggles) | —'),
 ('Z3_16', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Anzeige am Gerät umschalten | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/anzeige 1 (nie retain); nur Geräte, die es können; Haken wie Nr. 2 | Eingang = #15', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Anzeige am Gerät umschalten | Command for ON: publish Midea2Lox/befehl/123456789012/anzeige 1 (never retain); only devices that can do it; ticks as no. 2 | Input = #15'),
 ('Z3_17', 'Virtueller Eingang (Taste) | Selbstreinigung starten (Midea) | in der App: Selbstreinigung des Wärmetauschers starten (Gerät vorher ausschalten) | —', 'Virtual Input (Push Button) | Selbstreinigung starten (Midea) | in the app: start the self-cleaning of the heat exchanger (switch the device off first) | —'),
 ('Z3_18', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Selbstreinigung starten | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/selbstreinigung 1 (nie retain); nur Geräte, die es können; Haken wie Nr. 8 | Eingang = #17', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Selbstreinigung starten | Command for ON: publish Midea2Lox/befehl/123456789012/selbstreinigung 1 (never retain); only devices that can do it; ticks as no. 8 | Input = #17'),
 ('Z3_19', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_eco_mode | 1 = Sparbetrieb läuft, -1 = meldet das Gerät nicht; zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_eco_mode | 1 = eco mode running, -1 = the device does not report it; retained; gateway version 2: tick | —'),
 ('Z3_20', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_turbo_mode | 1 = Schnellbetrieb läuft, -1 = meldet das Gerät nicht; zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_turbo_mode | 1 = turbo mode running, -1 = the device does not report it; retained; gateway version 2: tick | —'),
 ('Z3_21', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_sleep_mode | 1 = Nachtbetrieb läuft, -1 = meldet das Gerät nicht; zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_sleep_mode | 1 = sleep mode running, -1 = the device does not report it; retained; gateway version 2: tick | —'),
 ('Z3_22', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_freeze_protection_mode | 1 = Frostschutz läuft, -1 = meldet das Gerät nicht; zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_freeze_protection_mode | 1 = freeze protection running, -1 = the device does not report it; retained; gateway version 2: tick | —'),
 ('Z3_23', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_purifier | 1 = Luftreinigung läuft, -1 = meldet das Gerät nicht; zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_purifier | 1 = air purification running, -1 = the device does not report it; retained; gateway version 2: tick | —'),
 ('Z3_24', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_follow_me | 1 = Regelung nach Fernbedienung, -1 = meldet das Gerät nicht; zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_follow_me | 1 = control by the remote control sensor, -1 = the device does not report it; retained; gateway version 2: tick | —'),
 ('Z3_25', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_display_on | 1 = Anzeige am Innengerät an, -1 = meldet das Gerät nicht; zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_display_on | 1 = display at the indoor unit on, -1 = the device does not report it; retained; gateway version 2: tick | —'),
 ('Z3_26', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_self_clean_active | 1 = Selbstreinigung läuft, -1 = meldet das Gerät nicht; zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_self_clean_active | 1 = self-cleaning running, -1 = the device does not report it; retained; gateway version 2: tick | —'),
 ('Z3_27', 'Status | Komfort (Midea) | Zeilen: V8 = 1 „Selbstreinigung läuft“; V4 = 1 „Frostschutz läuft – das Gerät hält etwa 8 °C“; ohne Bedingung „Spar <v1>, Schnell <v2>, Nacht <v3>, Luftreinigung <v5>, Fernbedienung <v6>, Anzeige <v7> (1 = an, -1 = meldet das Gerät nicht)“; Visualisierung EIN | V1 = #19, V2 = #20, V3 = #21, V4 = #22, V5 = #23, V6 = #24, V7 = #25, V8 = #26', 'Status | Komfort (Midea) | Rows: V8 = 1 “self-cleaning running”; V4 = 1 “freeze protection running – the device holds about 8 °C”; without condition “eco <v1>, turbo <v2>, sleep <v3>, air purification <v5>, remote control <v6>, display <v7> (1 = on, -1 = the device does not report it)”; visualisation ON | V1 = #19, V2 = #20, V3 = #21, V4 = #22, V5 = #23, V6 = #24, V7 = #25, V8 = #26'),
 ('Z3_28', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_filter_alert | 1 = das Gerät meldet „Filter reinigen“, -1 = meldet es nicht; zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_filter_alert | 1 = the device reports “clean filter”, -1 = it does not report it; retained; gateway version 2: tick | —'),
 ('Z3_29', 'Benachrichtigung | Meldung Filter reinigen (Midea) | Text: Midea2Lox – das Klimagerät meldet „Filter reinigen“. Gerät ausschalten, Frontklappe öffnen, Luftfilter herausnehmen, mit Wasser ausspülen, trocknen lassen, wieder einsetzen; danach am Gerät die Filteranzeige zurücksetzen (Taste laut Bedienungsanleitung) | Eingang = #34', 'Notification | Meldung Filter reinigen (Midea) | Text: Midea2Lox – the air conditioner reports “clean filter”. Switch the device off, open the front flap, take out the air filter, rinse it with water, let it dry, put it back; then reset the filter indicator at the device (button as described in the operating manual) | Input = #34'),
 ('Z3_30', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_real_time_power_usage | augenblickliche Leistung in W; -1 = das Gerät liefert keine Energiewerte; nie zurückbehalten; Statistik ein; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_real_time_power_usage | momentary power in W; -1 = the device supplies no energy values; never retained; statistics on; gateway version 2: tick | —'),
 ('Z3_31', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_total_energy_usage | Energie gesamt in kWh (Zählerstand des Geräts); -1 = liefert das Gerät nicht; nie zurückbehalten; Statistik ein; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_total_energy_usage | total energy in kWh (meter reading of the device); -1 = the device does not supply it; never retained; statistics on; gateway version 2: tick | —'),
 ('Z3_32', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_123456789012_current_energy_usage | Energie seit dem letzten Einschalten in kWh; -1 = liefert das Gerät nicht; nie zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_123456789012_current_energy_usage | energy since the last switch-on in kWh; -1 = the device does not supply it; never retained; gateway version 2: tick | —'),
 ('Z3_33', 'Status | Energie (Midea) | Zeilen: V2 < 0 „das Gerät liefert keine Energiewerte – nicht jedes Gerät kann das“; V1 < 0 „Leistung liefert das Gerät nicht – gesamt <v2.2> kWh“; V1 > 0 „nimmt <v1> W auf – seit dem Einschalten <v3.2> kWh, gesamt <v2.2> kWh“; ohne Bedingung „nimmt keine Leistung auf (aus) – gesamt <v2.2> kWh“; Visualisierung EIN | V1 = #30, V2 = #31, V3 = #32', 'Status | Energie (Midea) | Rows: V2 < 0 “the device supplies no energy values – not every device can do that”; V1 < 0 “the device does not supply the power – total <v2.2> kWh”; V1 > 0 “draws <v1> W – since switch-on <v3.2> kWh, total <v2.2> kWh”; without condition “draws no power (off) – total <v2.2> kWh”; visualisation ON | V1 = #30, V2 = #31, V3 = #32'),
 ('SEITE1_SCHRITT1', 'Im Plugin Reiter „Test“ → „Jetzt nach Geräten suchen“. Das Klimagerät erscheint mit seiner Nummer (10 bis 19 Ziffern). Im Reiter „Einstellungen“ dem Gerät eine Bezeichnung geben (z. B. „Klima Wohnzimmer“) und „Abfragetakt“ auf 60 stellen, speichern – ohne Abfragetakt kommen „online“ und die Gerätewerte nicht, und die Störung meldet nach 10 Minuten. Reiter „Test“ → „Zustand aller Geräte abfragen“: es erscheinen Werte.', 'In the plugin tab “Test” → “Search for devices now”. The air conditioner appears with its number (10 to 19 digits). In the tab “Settings” give the device a name (e.g. “Klima Wohnzimmer”) and set the “Polling interval” to 60, save – without a polling interval “online” and the device values never arrive, and the fault reports after 10 minutes. Tab “Test” → “Query the state of all devices”: values appear.'),
 ('SEITE1_SCHRITT2', 'Im Plugin Reiter „MQTT“ die Haken „Befehle über MQTT annehmen“ und „Ein/Aus, Betriebsart, Frostschutz und Selbstreinigung über MQTT zulassen“ setzen und speichern (beide ab Werk aus). MQTT-Gateway Fassung 1: das Abo „Midea2Lox/#“ bringt das Plugin mit (Reiter „Test“, Zeile „Ist unser Thema im Gateway abonniert?“). Fassung 2: die Themen der Namenstabelle mit „V2“ anhaken, status/ok und online zusätzlich „Noncached“; befehl/… nicht anhaken.', 'In the plugin tab “MQTT” set the ticks “Accept commands via MQTT” and “Allow on/off, operating mode, freeze protection and self-cleaning via MQTT” and save (both off by default). MQTT gateway version 1: the plugin brings the subscription “Midea2Lox/#” (tab “Test”, row “Is our topic subscribed in the gateway?”). Version 2: tick the topics of the name table marked “V2”, status/ok and online additionally “Noncached”; do not tick befehl/….'),
 ('SEITE1_SCHRITT3', 'In Loxone Config unter Peripherie → Virtuelle Eingänge die Virtuellen Eingänge der Liste anlegen – Name genau wie in der Namenstabelle des Plugins (Reiter „Einbindung in Loxone“, Kopierknopf), „Als Digitaleingang“ NICHT anhaken; die Texte (automatik_grund, Betriebsart, Lüfter, Schwenken, Leistungsstufe) als Virtueller Texteingang. Der LoxBerry-Benutzer braucht Rechte im Miniserver. Die Befehle kommen in den Virtuellen Ausgang „LoxBerry MQTT-Gateway“ (Vorlage VQ_loxberry_mqtt_gateway.xml aus dem Musterprojekt) oder alle auf einmal mit der Vorlage „MQTT-Befehle“ des Plugins.', 'In Loxone Config under Periphery → Virtual Inputs create the Virtual Inputs of the list – name exactly as in the name table of the plugin (tab “Loxone integration”, copy button), do NOT tick “Use as digital input”; the texts (automatik_grund, operating mode, fan, swing, power level) as Virtual Text Input. The LoxBerry user needs rights in the Miniserver. The commands go into the Virtual Output “LoxBerry MQTT-Gateway” (template VQ_loxberry_mqtt_gateway.xml from the sample project) or all at once with the template “MQTT commands” of the plugin.'),
 ('SEITE1_SCHRITT4', 'Seite „Midea2Lox“ anlegen. Die 12 Eingänge der Liste ziehen (Nr. 1–3, 11–15, 26–28, 31) und die zwei Befehle Nr. 22 und 24; dazu „Konstante 1“ und „Niemand zu Hause (eigene Quelle)“, falls schon im Projekt (sonst als Konstante bzw. Schalter neu). Neu anlegen (Peripherie → Virtuelle Eingänge): Schalter „Klima ein (Midea)“, Schalter „Fenster offen (eigene Quelle)“, Schieberegler „Solltemperatur (Midea)“ (16–30, Schritt 0,5); Virtueller Texteingang „Midea2Lox_automatik_grund“ – Name genau so.', 'Create the page “Midea2Lox”. Drag the 12 inputs of the list (no. 1–3, 11–15, 26–28, 31) and the two commands no. 22 and 24; also “Konstante 1” and “Niemand zu Hause (eigene Quelle)” if already in the project (otherwise new as constant or switch). Create new (Periphery → Virtual Inputs): switch “Klima ein (Midea)”, switch “Fenster offen (eigene Quelle)”, slider “Solltemperatur (Midea)” (16–30, step 0.5); Virtual Text Input “Midea2Lox_automatik_grund” – name exactly like this.'),
 ('SEITE1_SCHRITT5', 'Benachrichtigung „Meldung Plugin gestört (Midea)“ anlegen (Peripherie → Mitteilungen → Benachrichtigung), Text wie in der Liste. Sie bekommt genau eine Leitung (von Nr. 8).', 'Create the notification “Meldung Plugin gestört (Midea)” (Periphery → Messages → Notification), text as in the list. It gets exactly one connection (from no. 8).'),
 ('SEITE1_SCHRITT6', 'Übrige Bausteine über die Baustein-Suche (F5), Parameter wie in der Liste, von oben nach unten verbinden. Analogwertvalidierung Nr. 5: Haken bei ‚En‘ im Eigenschaftsfenster entfernen (Config legt En negiert an; sonst kommt die Konstante 1 als 0 an). UND Nr. 20: beide Eingänge negieren – auf den Eingangspunkt klicken, danach zeigt der Eingang einen kleinen Kreis. Status „Klima (Midea)“: vorher dreimal „+“; Zeilen in der angegebenen Reihenfolge, die ohne Bedingung zuletzt. „Statistik“ am Eingang Nr. 12 (Raumtemperatur) einschalten.', 'Remaining blocks via the block search (F5), parameters as in the list, connect from top to bottom. Value validator no. 5: remove the tick at ‘En’ in the properties window (Config creates En negated; otherwise the constant 1 arrives as 0). AND no. 20: negate both inputs – click on the input point, afterwards the input shows a small circle. Status “Klima (Midea)”: press “+” three times first; rows in the given order, the one without condition last. Switch on “Statistics” at input no. 12 (room temperature).'),
 ('SEITE1_SCHRITT7', 'Speichern und übertragen. Probe: „Zustand (Midea)“ zeigt „läuft – Klimagerät erreichbar“; Midea2Lox_status_zaehler zählt jede Minute weiter; der Schalter „Klima ein (Midea)“ schaltet das Gerät nach wenigen Sekunden (im Plugin Reiter „Test“ steht die Quittung „angenommen“).', 'Save and transfer. Check: “Zustand (Midea)” shows “running – air conditioner reachable”; Midea2Lox_status_zaehler counts up every minute; the switch “Klima ein (Midea)” switches the device within a few seconds (the plugin tab “Test” shows the acknowledgement “angenommen”).'),
 ('SEITE1_H1', "<b>Zu Nr. 1 und 5:</b> steht der LoxBerry, das MQTT-Gateway oder der Dienst, behalten alle Eingänge ihren letzten Wert – nur der stehende Zähler <span class='sm-mono'>Midea2Lox_status_zaehler</span> verrät es. Kommt innerhalb Tmc (300 s) kein neuer Wert, meldet die Analogwertvalidierung an ihrem Ausgang E. Den Haken bei ‚En‘ im Eigenschaftsfenster entfernen.", "<b>On no. 1 and 5:</b> if the LoxBerry, the MQTT gateway or the service stops, all inputs keep their last value – only the stopped counter <span class='sm-mono'>Midea2Lox_status_zaehler</span> gives it away. If no new value arrives within Tmc (300 s), the value validator reports at its output E. Remove the tick at ‘En’ in the properties window."),
 ('SEITE1_H2', '<b>Zu Nr. 3 und 6 bis 9:</b> „online“ kommt nur mit Abfragetakt (Schritt 1). Die Meldung „Plugin gestört“ kommt nach etwa 10 Minuten, wenn das Gerät nicht antwortet, und nach etwa 15 Minuten (5 Minuten Lebenszeichen und 10 Minuten), wenn das Plugin steht. Eine Benachrichtigung bekommt nur eine Quelle – beide Störungen laufen über das ODER Nr. 7.', '<b>On no. 3 and 6 to 9:</b> “online” arrives only with a polling interval (step 1). The notification “Plugin gestört” comes after about 10 minutes when the device does not answer, and after about 15 minutes (5 minutes sign of life and 10 minutes) when the plugin stands still. A notification gets only one source – both faults run via the OR no. 7.'),
 ('SEITE1_H3', '<b>Zu Nr. 17 bis 21:</b> beide Eingänge des UND Nr. 20 sind negiert. Das Gerät geht nach 1 Minute offenem Fenster bzw. sofort bei „niemand zu Hause“ aus und wieder an, sobald beides vorbei und der Schalter ein ist. Das Plugin kann beides auch selbst (Reiter Automatik: „Fenster offen: Gerät aus“ über haus/tuer/…, „Anwesenheit berücksichtigen“ über haus/anwesenheit/jemand) – dort schaltet es NICHT wieder ein. Im eigenen Haus je Aufgabe nur einen der beiden Wege wählen.', '<b>On no. 17 to 21:</b> both inputs of the AND no. 20 are negated. The device goes off after 1 minute of open window or immediately at “nobody at home” and on again as soon as both are over and the switch is on. The plugin can do both itself (tab Automation: “Window open: device off” via haus/tuer/…, “Consider presence” via haus/anwesenheit/jemand) – there it does NOT switch on again. In your own house choose only one of the two ways per task.'),
 ('SEITE1_H4', 'Im eigenen Projekt steht in jedem Namen und in jedem Befehl die eigene Gerätenummer statt 123456789012 – die Namenstabelle und die Vorlage MQTT-Befehle des Plugins bringen das richtig mit.', 'In your own project every name and every command carries your own device number instead of 123456789012 – the name table and the template MQTT commands of the plugin bring that correctly.'),
 ('SEITE1_H5', 'Jeder Befehl aus Loxone setzt die Automatik des Plugins für die Sperrzeit aus (ab Werk 120 Minuten) – „Handvorrang“ – und beendet den Abwesenheitsbetrieb des Geräts. Eine Abfrage nicht. Die Automatik-Werte (Nr. 26–30) kommen nur, wenn die Automatik im Plugin eingeschaltet ist; sonst bleiben sie 0.', 'Every command from Loxone suspends the automation of the plugin for the lock time (120 minutes by default) – “manual priority” – and ends the away mode of the device. A query does not. The automation values (no. 26–30) arrive only when the automation is switched on in the plugin; otherwise they stay 0.'),
 ('SEITE1_H6', 'Mehrere Klimageräte: für jedes Gerät dieselben Gerätebausteine mit seiner Nummer; die Störungen über weitere ODER (je zwei Eingänge) vor Nr. 8 führen – nie mehrere Quellen direkt an die Benachrichtigung.', 'Several air conditioners: for each device the same device blocks with its number; route the faults via further ORs (two inputs each) before no. 8 – never several sources directly to the notification.'),
 ('SEITE1_H7', "Die Befehle gehen als <span class='sm-mono'>publish Midea2Lox/befehl/&lt;Nummer&gt;/&lt;Name&gt;</span> über den UDP-Eingang des MQTT-Gateways; jeder im Heimnetz kann dorthin senden – deshalb sind beide Haken im Plugin ab Werk aus. Nie „retain“: ein zurückbehaltener Befehl wird verworfen. Das Plugin quittiert unter …/quittung (im Reiter Test sichtbar). Fehlwerte: -1 = keine Aussage, -999 = Temperatur fehlt.", "The commands go as <span class='sm-mono'>publish Midea2Lox/befehl/&lt;number&gt;/&lt;name&gt;</span> via the UDP input of the MQTT gateway; anyone in the home network can send there – that is why both ticks in the plugin are off by default. Never “retain”: a retained command is discarded. The plugin acknowledges under …/quittung (visible in the tab Test). Default values: -1 = no statement, -999 = temperature missing."),
 ('SEITE1_H8', 'Wer die Loxone-Klimaanlagensteuerung oder die Intelligente Raumregelung nutzt, legt deren Sollwert an „Midea2Lox: Solltemperatur“ (Nr. 24) und deren Ein/Aus an „Midea2Lox: Ein- und ausschalten“ (Nr. 22) – nicht Teil des Musterprojekts.', 'Whoever uses the Loxone air conditioner controller or the Intelligent Room Controller connects its target value to “Midea2Lox: Solltemperatur” (no. 24) and its on/off to “Midea2Lox: Ein- und ausschalten” (no. 22) – not part of the sample project.'),
 ('SEITE1_H9', "Bewusst nicht im Musterprojekt: <span class='sm-mono'>status/ts</span>, <span class='sm-mono'>status/dienst</span> (der Zähler sagt es zuverlässiger), <span class='sm-mono'>status/befehle</span> und die Quittungen (Reiter Test), <span class='sm-mono'>connection/status</span>, iECO, Schwenkwinkel, Lüfterstufen als Zahl, <span class='sm-mono'>breeze_mode</span>, die Leistungsstufen LEVEL_1–5 und der HTTP-Rückfallweg ohne Broker.", "Deliberately not in the sample project: <span class='sm-mono'>status/ts</span>, <span class='sm-mono'>status/dienst</span> (the counter tells it more reliably), <span class='sm-mono'>status/befehle</span> and the acknowledgements (tab Test), <span class='sm-mono'>connection/status</span>, iECO, swing angles, fan speeds as a number, <span class='sm-mono'>breeze_mode</span>, the power levels LEVEL_1–5 and the HTTP fallback without broker."),
 ('SEITE2_SCHRITT1', 'Eingänge und Befehle wie auf Seite „Midea2Lox“ (Namenstabelle, Virtueller Ausgang „LoxBerry MQTT-Gateway“).', 'Inputs and commands as on page “Midea2Lox” (name table, Virtual Output “LoxBerry MQTT-Gateway”).'),
 ('SEITE2_SCHRITT2', 'Neue Seite „Midea2Lox Betrieb“, die 17 Befehle und den Eingang Nr. 21 der Liste ziehen. Neu anlegen: Schieberegler „Sollfeuchte (Midea)“ (35–70, Schritt 5), Taste „Jetzt abfragen (Midea)“, drei Virtuelle Texteingänge mit den Namen Nr. 22–24 genau so, „In Visualisierung verwenden“ an.', 'New page “Midea2Lox Betrieb”, drag the 17 commands and the input no. 21 of the list. Create new: slider “Sollfeuchte (Midea)” (35–70, step 5), push button “Jetzt abfragen (Midea)”, three Virtual Text Inputs with the names no. 22–24 exactly like this, “Use in User Interface” on.'),
 ('SEITE2_SCHRITT3', 'Drei Radiotasten über F5: Anzahl der Tasten und Tastentexte wie in der Liste, Remanenz abhaken. Ausgang Q1, Q2, Q3 … der Radiotasten an den Befehl derselben Zeile (Q1 an den ersten Befehl darunter usw.).', 'Three radio buttons via F5: number of buttons and button texts as in the list, untick remanence. Output Q1, Q2, Q3 … of the radio buttons to the command of the same row (Q1 to the first command below and so on).'),
 ('SEITE2_SCHRITT4', 'Status „Betrieb (Midea)“ setzen, die drei Texteingänge an V4–V6 legen. Speichern und übertragen. Probe: in der App „Kühlen“ wählen – nach der nächsten Abfrage (höchstens 1 Minute, oder „Jetzt abfragen“) zeigt der Status „Kühlen gewählt – das Gerät meldet operational_mode_enum.cool …“.', 'Place status “Betrieb (Midea)”, connect the three text inputs to V4–V6. Save and transfer. Check: select “Kühlen” in the app – after the next query (at most 1 minute, or “Jetzt abfragen”) the status shows “Kühlen gewählt – das Gerät meldet operational_mode_enum.cool …”.'),
 ('SEITE2_H1', 'Die Radiotasten zeigen, was zuletzt aus der App gewählt wurde; was das Gerät wirklich tut (auch nach der Fernbedienung), zeigen die Texteingänge Nr. 22–24 im Status Nr. 27.', 'The radio buttons show what was last selected from the app; what the device really does (also after the remote control) is shown by the text inputs no. 22–24 in status no. 27.'),
 ('SEITE2_H2', '<b>Zu Nr. 1, 7 und 14:</b> Remanenz aus – sonst schickt der Miniserver nach einem Neustart die zuletzt gewählte Taste erneut, und jeder Befehl setzt den Handvorrang der Automatik.', '<b>On no. 1, 7 and 14:</b> remanence off – otherwise the Miniserver sends the last selected button again after a restart, and every command sets the manual priority of the automation.'),
 ('SEITE2_H3', 'In der Betriebsart Automatik stellt das Gerät die Lüfterstufe selbst; eine andere Stufe setzt das Plugin auf Automatik zurück. Die Betriebsart braucht im Plugin beide Haken (Reiter MQTT).', 'In the operating mode automatic the device sets the fan speed itself; the plugin resets another speed to automatic. The operating mode needs both ticks in the plugin (tab MQTT).'),
 ('SEITE2_H4', 'Die Sollfeuchte wirkt nur bei Geräten mit Feuchteregelung (Entfeuchten); andere übergehen den Befehl, die Quittung lautet dann „abgelehnt: KANN_DAS_GERAET_NICHT“.', 'The target humidity works only for devices with humidity control (dehumidify); others ignore the command, the acknowledgement then reads “abgelehnt: KANN_DAS_GERAET_NICHT”.'),
 ('SEITE3_SCHRITT1', 'Neue Seite „Midea2Lox Komfort und Energie“, die 12 Befehle und 12 Eingänge der Liste ziehen; „Statistik“ an Leistung (Nr. 30) und Energie gesamt (Nr. 31) einschalten.', 'New page “Midea2Lox Komfort und Energie”, drag the 12 commands and 12 inputs of the list; switch on “Statistics” at power (no. 30) and total energy (no. 31).'),
 ('SEITE3_SCHRITT2', 'Neu anlegen: sieben Schalter, zwei Tasten (Namen wie in der Liste), Formel Nr. 34, Radiotasten Nr. 35, Virtueller Texteingang Nr. 39 (Name genau so), Benachrichtigung „Meldung Filter reinigen (Midea)“ an die Formel Nr. 34.', 'Create new: seven switches, two push buttons (names as in the list), formula no. 34, radio buttons no. 35, Virtual Text Input no. 39 (name exactly like this), notification “Meldung Filter reinigen (Midea)” at formula no. 34.'),
 ('SEITE3_SCHRITT3', 'Status über F5; „Komfort (Midea)“ vorher viermal „+“. Speichern und übertragen. Probe: „Sparbetrieb (Midea)“ ein – nach der nächsten Abfrage zeigt „Komfort (Midea)“ „Spar 1“.', 'Status via F5; “Komfort (Midea)” press “+” four times first. Save and transfer. Check: “Sparbetrieb (Midea)” on – after the next query “Komfort (Midea)” shows “Spar 1”.'),
 ('SEITE3_H1', 'Nicht jedes Gerät kann jede Funktion; was es nicht kann, übergeht das Plugin mit einer Warnung im Protokoll und der Quittung „abgelehnt: KANN_DAS_GERAET_NICHT“; meldet das Gerät einen Zustand nicht, steht -1 da.', 'Not every device can do every function; what it cannot do, the plugin ignores with a warning in the log and the acknowledgement “abgelehnt: KANN_DAS_GERAET_NICHT”; if the device does not report a state, -1 is shown.'),
 ('SEITE3_H2', 'Frostschutz stellt das Gerät auf Heizen; Frostschutz und Selbstreinigung brauchen im Plugin beide Haken (Reiter MQTT).', 'Freeze protection sets the device to heating; freeze protection and self-cleaning need both ticks in the plugin (tab MQTT).'),
 ('SEITE3_H3', '<b>Zu Nr. 28, 34 und 29:</b> die Formel lässt nur 1 durch – -1 (meldet das Gerät nicht) löst keine Meldung aus. Die Filter-Meldung kommt nach jedem Übertragen erneut, solange das Gerät „Filter reinigen“ meldet – Filter reinigen, am Gerät zurücksetzen.', '<b>On no. 28, 34 and 29:</b> the formula lets only 1 pass – -1 (the device does not report it) triggers no notification. The filter notification comes again after every transfer as long as the device reports “clean filter” – clean the filter, reset at the device.'),
 ('SEITE3_H4', 'Leistung und Energie liefern nicht alle Geräte; dann steht dort -1.', 'Power and energy are not supplied by all devices; then -1 is shown.'),
 # ---- Gruppe 15 (4.5.18): MQTT-Befehle, Namenstabelle, Anwesenheit, Fehlwerte
 ('Z1_31', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Midea2Lox) | Midea2Lox_anwesenheit_aktiv | 1 = Abwesenheitsbetrieb: das Plugin hält Klimageräte wegen „niemand zu Hause“ (haus/anwesenheit/jemand, Reiter Automatik „Anwesenheit berücksichtigen“, ab Werk aus), 0 = nicht, -1 = eingeschaltet, aber die Quelle schweigt; nie zurückbehalten; Fassung 2: Haken | —', 'Virtual Input (name as assigned by the MQTT gateway, plugin Midea2Lox) | Midea2Lox_anwesenheit_aktiv | 1 = away mode: the plugin holds air conditioners because of “nobody at home” (haus/anwesenheit/jemand, tab Automation “Consider presence”, off by default), 0 = not, -1 = switched on, but the source is silent; never retained; gateway version 2: tick | —'),
 ('Z3_34', 'Formel | Filter reinigen gemeldet (Midea) | IF(I1>0;1;0) – nur 1 löst die Meldung aus, -1 (meldet das Gerät nicht) nicht | I1 = #28', 'Formula | Filter reinigen gemeldet (Midea) | IF(I1>0;1;0) – only 1 triggers the notification, -1 (the device does not report it) does not | I1 = #28'),
 ('Z3_35', 'Radiotasten | Leistungsbegrenzung (Midea) | Taste 1 „aus“, Taste 2 „50 Prozent“, Taste 3 „75 Prozent“; Text für „keine Taste gewählt“: „wie am Gerät“; Remanenz aus; nur Geräte, die es können (im Plugin-Protokoll in der Fähigkeitsliste unter supported_rate_selects) – z. B. um bei wenig PV-Überschuss sparsam zu kühlen | —', 'Radio Buttons | Leistungsbegrenzung (Midea) | Button 1 “aus”, button 2 “50 Prozent”, button 3 “75 Prozent”; text for “no button selected”: “wie am Gerät”; remanence off; only devices that can do it (in the plugin log in the capability list under supported_rate_selects) – e.g. to cool economically with little PV surplus | —'),
 ('Z3_36', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Leistungsbegrenzung aus | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/leistungsstufe aus (nie retain); volle Leistung; Haken wie Nr. 2 | Eingang = Ausgang Q1 von #35', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Leistungsbegrenzung aus | Command for ON: publish Midea2Lox/befehl/123456789012/leistungsstufe aus (never retain); full power; ticks as no. 2 | Input = output Q1 of #35'),
 ('Z3_37', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Leistungsbegrenzung 50 Prozent | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/leistungsstufe gear_50 (nie retain); Leistung auf etwa die Hälfte begrenzt; Haken wie Nr. 2 | Eingang = Ausgang Q2 von #35', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Leistungsbegrenzung 50 Prozent | Command for ON: publish Midea2Lox/befehl/123456789012/leistungsstufe gear_50 (never retain); power limited to about half; ticks as no. 2 | Input = output Q2 of #35'),
 ('Z3_38', 'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT) | Midea2Lox: Leistungsbegrenzung 75 Prozent | Befehl bei EIN: publish Midea2Lox/befehl/123456789012/leistungsstufe gear_75 (nie retain); Leistung auf etwa drei Viertel begrenzt; Haken wie Nr. 2 | Eingang = Ausgang Q3 von #35', 'Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT) | Midea2Lox: Leistungsbegrenzung 75 Prozent | Command for ON: publish Midea2Lox/befehl/123456789012/leistungsstufe gear_75 (never retain); power limited to about three quarters; ticks as no. 2 | Input = output Q3 of #35'),
 ('Z3_39', 'Virtueller Texteingang | Midea2Lox_123456789012_rate_select | von Hand anlegen, Name genau so (Name, den das MQTT-Gateway vergibt), „In Visualisierung verwenden“ an; Leistungsstufe, wie das Gerät sie meldet: „OFF“, „GEAR_50“, „GEAR_75“ (andere Geräte „LEVEL_1“ bis „LEVEL_5“), „-“ = das Gerät kann es nicht; zurückbehalten; Fassung 2: Haken | —', 'Virtual Text Input | Midea2Lox_123456789012_rate_select | create by hand, name exactly like this (the name the MQTT gateway assigns), “Use in User Interface” on; power level as the device reports it: “OFF”, “GEAR_50”, “GEAR_75” (other devices “LEVEL_1” to “LEVEL_5”), “-” = the device cannot do it; retained; gateway version 2: tick | —'),
 ('Z3_40', 'Status | Leistung (Midea) | Zeilen: V1 = 2 „auf 50 Prozent begrenzt gewählt – das Gerät meldet <v2>“; V1 = 3 „auf 75 Prozent begrenzt gewählt – das Gerät meldet <v2>“; V1 = 1 „ohne Begrenzung gewählt – das Gerät meldet <v2>“; ohne Bedingung „in der App nichts gewählt – das Gerät meldet <v2> („-“ = kann es nicht)“; Visualisierung EIN | V1 = #35, V2 = #39', 'Status | Leistung (Midea) | Rows: V1 = 2 “limited to 50 per cent selected – the device reports <v2>”; V1 = 3 “limited to 75 per cent selected – the device reports <v2>”; V1 = 1 “no limit selected – the device reports <v2>”; without condition “nothing selected in the app – the device reports <v2> (“-” = cannot do it)”; visualisation ON | V1 = #35, V2 = #39'),
 ('SEITE3_H5', '<b>Zu Nr. 35 bis 40:</b> Leistungsbegrenzung nur bei Geräten, die sie melden (Fähigkeitsliste im Plugin-Protokoll, supported_rate_selects); andere quittieren „abgelehnt: KANN_DAS_GERAET_NICHT“, und der Texteingang Nr. 39 zeigt „-“. Die Stufen LEVEL_1–5 stehen nur in den Vorlagen des Plugins.', '<b>On no. 35 to 40:</b> power limitation only for devices that report it (capability list in the plugin log, supported_rate_selects); others acknowledge “abgelehnt: KANN_DAS_GERAET_NICHT”, and the text input no. 39 shows “-”. The levels LEVEL_1–5 are only in the templates of the plugin.'),
],

# --- nachgezogen 08.10.2026 (Kopf-Welle 2) aus der .ini von 4.5.13 ---
'REGION': [
 ('DE', 'Deutschland', 'Germany'),
 ('AT', 'Österreich', 'Austria'),
 ('CH', 'Schweiz', 'Switzerland'),
 ('NL', 'Niederlande', 'Netherlands'),
 ('IT', 'Italien', 'Italy'),
 ('ES', 'Spanien', 'Spain'),
 ('FR', 'Frankreich', 'France'),
 ('PL', 'Polen', 'Poland'),
 ('GB', 'Großbritannien', 'United Kingdom'),
 ('US', 'USA', 'USA'),
 ('KR', 'Südkorea', 'South Korea'),
],

# --- Kopf wie alle Hausplugins (Entscheidung Nr. 43, 4.5.13): Statusuebersicht
#     ueber den Reitern und gruener Kasten oben im Reiter Einstellungen
#     (WAS_IST_DAS roh ausgegeben, mi_t ohne mi_e).
'KOPF': [
 ('EIGENSCHAFT', 'Eigenschaft', 'Property'),
 ('WERT', 'Wert', 'Value'),
 ('KONTO_EIGEN', 'eigenes Konto eingetragen', 'own account entered'),
 ('KONTO_SAMMEL', 'kein eigenes - msmart-ng nimmt seine Sammelkonten', 'none of its own - msmart-ng uses its shared accounts'),
 ('WAS_IST_DAS', '<b>Klimageräte der Midea-Gruppe in Loxone – im eigenen Netz, ohne Umweg über die Wolke des Herstellers.</b> Ein Dienst auf dem LoxBerry schickt die Befehle des Miniservers über msmart-ng an die Geräte (Midea und Handelsmarken wie Comfee, Kaisai oder Qlima) – über MQTT oder, für bestehende Anlagen, per UDP. Ihren Zustand meldet er über MQTT zurück; Loxone liest ihn über das MQTT-Gateway. Das Hersteller-Konto braucht es nur bei der Gerätesuche, für Token und Schlüssel von Geräten mit Protokoll V3.', '<b>Air conditioners of the Midea group in Loxone – on your own network, without a detour via the manufacturer cloud.</b> A service on the LoxBerry sends the commands of the Miniserver via msmart-ng to the devices (Midea and brands such as Comfee, Kaisai or Qlima) – via MQTT or, for existing installations, via UDP. It reports their state back via MQTT; Loxone reads it via the MQTT gateway. The manufacturer account is needed only for the device search, for token and key of devices with protocol V3.'),
],

# --- Drift-Abgleich 06.11.2026 (Midea2Lox 4.5.24): Sprachansagen des Plugins; der Abschnitt
#     [ANSAGE] davor kommt aus der gemeinsamen Quelle (ansage_abschnitt()).
'ANSAGEPLUGIN': [
 ('H', 'Sprachansagen', 'Announcements'),
 ('K_SPEICHERN', 'Sprachansagen speichern', 'Save announcements'),
 ('K_TEST', 'Testansage an alle Ziele', 'Test announcement to all targets'),
 ('M_OK', 'Sprachansagen gespeichert.', 'Announcements saved.'),
 ('M_FEHL', 'Die Sprachansagen ließen sich nicht speichern.', 'The announcements could not be saved.'),
 ('M_TEST_OK', 'Testansage gesendet.', 'Test announcement sent.'),
 ('M_TEST_FEHL', 'Testansage nicht gesendet:', 'Test announcement not sent:'),
 ('L_AUSFALL', 'Gerät antwortet seit 30 Minuten nicht, und wieder da', 'Device has not answered for 30 minutes, and back again'),
 ('L_FEHLER', 'Gerät meldet einen Fehlercode, und behoben', 'Device reports an error code, and cleared'),
 ('SATZ_AUSFALL', 'Ein Midea-Gerät antwortet nicht mehr.', 'A Midea device is not responding.'),
 ('SATZ_WIEDER', 'Das Midea-Gerät antwortet wieder.', 'The Midea device is responding again.'),
 ('SATZ_FEHLER', 'Ein Midea-Gerät meldet einen Fehler.', 'A Midea device reports an error.'),
 ('SATZ_BEHOBEN', 'Der Fehler am Midea-Gerät ist behoben.', 'The error on the Midea device has cleared.'),
],
}


def pruefe():
    """Der Erzeuger weist ab, statt zurechtzubiegen."""
    fehler = []
    for abschnitt, zeilen in TEXTE.items():
        gesehen = set()
        for schluessel, de, en in zeilen:
            ort = '%s.%s' % (abschnitt, schluessel)
            if schluessel in gesehen:
                fehler.append('%s: doppelter Schluessel' % ort)
            gesehen.add(schluessel)
            if schluessel.upper() in SCHLUESSELWOERTER:
                fehler.append('%s: der INI-Parser liest diesen Namen als '
                              'Schluesselwort' % ort)
            if not re.match(r'^[A-Z][A-Z0-9_]*$', schluessel):
                fehler.append('%s: unzulaessiger Schluesselname' % ort)
            for name, wert in (('DE', de), ('EN', en)):
                if '"' in wert:
                    fehler.append('%s (%s): gerades Anfuehrungszeichen - es '
                                  'beendet den INI-Wert und schneidet den Rest '
                                  'STILL ab' % (ort, name))
                if '\n' in wert or '\r' in wert:
                    fehler.append('%s (%s): Zeilenumbruch im Wert' % (ort, name))
                if ENTITAETEN.search(wert):
                    fehler.append('%s (%s): HTML-Entitaet fuer einen Umlaut - '
                                  'die Dateien tragen echte UTF-8-Zeichen'
                                  % (ort, name))
                if wert.strip() == '':
                    fehler.append('%s (%s): leerer Wert' % (ort, name))
            # Platzhalter müssen in BEIDEN Sprachen gleich oft vorkommen,
            # sonst wirft sprintf in einer von beiden.
            pde = re.findall(r'%[-0-9.]*[a-z]', de)
            pen = re.findall(r'%[-0-9.]*[a-z]', en)
            if pde != pen:
                fehler.append('%s: Platzhalter DE %s gegen EN %s'
                              % (ort, pde or '-', pen or '-'))
    return fehler


KOPF_DE = """; Midea2Lox - deutsche Texte
;
; ERZEUGT von Werkzeuge/mi_sprache_erzeugen.py - NICHT von Hand aendern.
; Wer einen Text aendern will, aendert ihn dort und laesst den Erzeuger
; laufen; sonst laeuft die naechste Erzeugung ueber die Aenderung hinweg.
;
; Gelesen von mi_t() in webfrontend/htmlauth/mi_lib.php. Die Schluessel sind
; mit language_en.ini deckungsgleich; Englisch ist die Rueckfallebene fuer
; jede Sprache ohne eigene Datei.
;
; DREI FALLEN, alle beim Umbau aufgelaufen:
;
; 1. Werte MUESSEN in Anfuehrungszeichen stehen. PHP weist einen INI-Wert
;    mit &, (, ), ! oder ? sonst als Syntaxfehler zurueck - und dann faellt
;    die GANZE Datei aus, nicht nur die eine Zeile.
; 2. Ein GERADES Anfuehrungszeichen IM Wert beendet ihn: der Rest des Satzes
;    wird still abgeschnitten. Kein Fehler, keine Warnung, nur ein Satz, der
;    mitten im Wort aufhoert. Attribute in der Auszeichnung deshalb einfach
;    quotieren (class='sm-mono').
; 3. Schluesselnamen duerfen nicht TRUE, FALSE, ON, OFF, YES, NO, NULL oder
;    NONE heissen - das sind fuer den INI-Parser Schluesselwoerter.
;
; Umlaute stehen als echte UTF-8-Zeichen, nicht als Entitaet.
; Werte NICHT ueber mehrere Zeilen umbrechen: INI kennt das nicht.
"""

KOPF_EN = """; Midea2Lox - English texts
;
; GENERATED by Werkzeuge/mi_sprache_erzeugen.py - do NOT edit by hand.
; Change the text there and run the generator; otherwise the next run walks
; over your change.
;
; Read by mi_t() in webfrontend/htmlauth/mi_lib.php. The keys match
; language_de.ini; English is the fallback for every language without its
; own file.
;
; Values MUST be quoted, must not contain a straight double quote, and must
; not span several lines. Key names must not be TRUE, FALSE, ON, OFF, YES,
; NO, NULL or NONE.
"""


def vorhandene_schluessel(pfad):
    """Die Schluessel einer schon vorhandenen .ini - Abschnitt.NAME."""
    import re as _re
    aus, abschnitt = set(), ''
    try:
        with io.open(pfad, encoding='utf-8', errors='replace') as fh:
            for z in fh:
                z = z.rstrip('\r\n')
                m = _re.match(r'\s*\[([^\]]+)\]\s*$', z)
                if m:
                    abschnitt = m.group(1)
                    continue
                m = _re.match(r'\s*([A-Za-z0-9_]+)\s*=', z)
                if m:
                    aus.add(abschnitt + '.' + m.group(1))
    except OSError:
        return set()
    return aus


def wuerde_verlieren(pfad, eigene):
    """Welche Schluessel stuenden nachher NICHT mehr in der Datei?

    ANGELEGT 31.08.2026. Dieses Werkzeug schrieb ohne jede Ruecksicht auf das,
    was schon dastand - anders als die Erzeuger der anderen Linien, die sich
    in genau diesem Fall weigern. Gemessen: ein Lauf haette 21 (Midea2Lox)
    beziehungsweise 16 (Renault) Schluessel geloescht, die im PHP benutzt
    werden; bei Renault darunter die drei Gateway-Texte, die am selben Tag
    erst berichtigt worden waren.

    Geprueft werden nur die NAMEN. Einen Wert zu aendern ist der Zweck des
    Werkzeugs; einen Schluessel zu verlieren ist es nie.
    """
    return sorted(vorhandene_schluessel(pfad) - set(eigene))

def ansage_abschnitt(sprache):
    """Der Abschnitt [ANSAGE] der gemeinsamen Sprachausgabe - EINE Quelle:
    Werkzeuge/gemeinsam_pruefen.py baut ihn aus Werkzeuge/gemeinsam/sprachausgabe_texte.json
    (Form SCHLUESSEL="Wert", ohne Leerzeichen). Fehlt die Quelle, wird nichts geschrieben.
    Drift-Abgleich 06.11.2026 (Midea2Lox 4.5.24)."""
    w = os.path.dirname(os.path.abspath(__file__))
    if os.path.isfile(os.path.join(w, 'gemeinsam_pruefen.py')) and \
            os.path.isfile(os.path.join(w, 'gemeinsam', 'sprachausgabe_texte.json')):
        sys.path.insert(0, w)
        import gemeinsam_pruefen
        return gemeinsam_pruefen.ini_abschnitt(sprache)
    print('Werkzeuge/gemeinsam_pruefen.py nicht gefunden - es wurde nichts geschrieben.')
    sys.exit(2)


# Der Abschnitt [ANSAGE] steht in der .ini unmittelbar vor diesem Abschnitt von TEXTE.
ANSAGE_VOR = 'ANSAGEPLUGIN'


def schreibe(pfad, kopf, spalte, ansage=None):
    zeilen = [kopf]
    for abschnitt in TEXTE:
        if abschnitt == ANSAGE_VOR:
            if ansage is None:
                ansage = ansage_abschnitt(spalte)
            zeilen.append('')
            zeilen.extend(ansage.rstrip('\n').split('\n'))
        zeilen.append('')
        zeilen.append('[%s]' % abschnitt)
        for schluessel, de, en in TEXTE[abschnitt]:
            wert = de if spalte == 'de' else en
            zeilen.append('%s = "%s"' % (schluessel, wert))
    # LF, seit der Hausregel vom 13.09.2026 ("alles wird auf LF gestellt").
    # Bis dahin stand hier '\r\n'.join(...) samt einem inneren Join, der ein
    # eingebettetes \n im Kopf oder in einem Wert auf CRLF hob; mit LF ist der
    # ein Nichts und faellt weg.
    text = '\n'.join(zeilen) + '\n'
    # BINAER schreiben - und das gilt fuer LF erst recht: open(p, 'w')
    # uebersetzt unter Windows still jedes \n zu \r\n und machte die
    # Umstellung damit wirkungslos.
    with open(pfad, 'wb') as f:
        f.write(text.encode('utf-8'))
    return sum(len(v) for v in TEXTE.values())


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


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    fehler = pruefe()
    if fehler:
        print('ABGEWIESEN - es wurde nichts geschrieben:')
        for f in fehler:
            print('   ', f)
        sys.exit(1)
    ordner = os.path.join(sys.argv[1], 'templates', 'lang')
    if not os.path.isdir(ordner):
        print('Nicht gefunden: %s' % ordner)
        sys.exit(2)
    eigene = {'%s.%s' % (a, s)
              for a in TEXTE for s, _d, _e in TEXTE[a]}
    # [ANSAGE] VOR jedem Schreiben holen: fehlt die Quelle, wird nichts geschrieben.
    ansage = {sp: ansage_abschnitt(sp) for sp in ('de', 'en')}
    for datei, sp in (('language_de.ini', 'de'), ('language_en.ini', 'en')):
        eigene_sp = eigene | {'ANSAGE.' + z.split('=', 1)[0]
                              for z in ansage[sp].split('\n') if '=' in z}
        weg = wuerde_verlieren(os.path.join(ordner, datei), eigene_sp)
        if weg:
            print('ABGEWIESEN - es wurde nichts geschrieben.')
            print('%s wuerde %d Schluessel verlieren:' % (datei, len(weg)))
            for x in weg:
                print('    ' + x)
            sys.exit(1)
    n = schreibe(os.path.join(ordner, 'language_de.ini'), KOPF_DE, 'de', ansage['de'])
    schreibe(os.path.join(ordner, 'language_en.ini'), KOPF_EN, 'en', ansage['en'])
    print('%d Schluessel in %d Abschnitten, je Sprache geschrieben.'
          % (n, len(TEXTE)))
    sys.exit(0)
