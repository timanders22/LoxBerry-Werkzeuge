# -*- coding: utf-8 -*-
"""Erzeugt language_de.ini und language_en.ini aus EINER Quelle.

Damit koennen die beiden Schluesselmengen gar nicht auseinanderlaufen -
das war bis 2.0.6 nur eine Zusage in der README (und die nannte dazu die
falsche Zahl: 223 statt 227).

Regeln, die hier eingehalten werden:
  * Werte stehen in doppelten Anfuehrungszeichen und enthalten selbst
    keine - parse_ini_file mit INI_SCANNER_RAW gibt sie sonst mit zurueck.
  * Echte Umlaute, keine ASCII-Umschrift (umschrift_pruefen.py).
  * Zeilenenden CRLF, wie in allen anderen .ini dieses Hauses.
"""
import io, os, sys

T = {}   # abschnitt -> [(schluessel, de, en)]


def s(abschnitt, schluessel, de, en):
    T.setdefault(abschnitt, []).append((schluessel, de, en))


# ------------------------------------------------------------------ REITER
s('REITER', 'EINSTELLUNGEN', 'Einstellungen', 'Settings')
s('REITER', 'LOXONE', 'Einbindung in Loxone', 'Loxone integration')
s('REITER', 'TEST', 'Test', 'Test')
s('REITER', 'VERLAUF', 'Ladehistorie', 'Charging history')
s('REITER', 'LOG', 'Logdateien', 'Log files')

# ----------------------------------------------------------------- LEGENDE
s('LEGENDE', 'LESEN', 'Ansehen — fragt nur ab, verändert nichts',
  'View — reads only, changes nothing')
s('LEGENDE', 'TECHNIK', 'Technische Auskunft — für die Fehlersuche',
  'Technical information — for troubleshooting')
s('LEGENDE', 'AKTION', 'Löst etwas aus — speichert oder sendet',
  'Triggers something — saves or sends')
s('LEGENDE', 'AKTION_TOKEN', 'Macht die bisherigen Adressen in Loxone ungültig',
  'Invalidates the addresses currently entered in Loxone')
s('LEGENDE', 'AKTION_LOG', 'Löscht die Protokolldatei', 'Deletes the log file')

# ------------------------------------------------------------------- THEMA
s('THEMA', 'BATTSOC', 'Batteriestand in Prozent', 'Battery level in percent')
s('THEMA', 'RANGE', 'Reichweite in km', 'Range in km')
s('THEMA', 'CHARGINGSTATUS', 'Ladestatus als Zahl (1 = lädt)', 'Charging status as a number (1 = charging)')
s('THEMA', 'CABLESTATUS', 'Kabel eingesteckt (1) oder nicht (0)', 'Cable plugged in (1) or not (0)')
s('THEMA', 'CHARGINGTIME', 'Restdauer des Ladevorgangs in Minuten', 'Remaining charging time in minutes')
s('THEMA', 'CHARGINGEFFEKT', 'Ladeleistung in kW', 'Charging power in kW')
s('THEMA', 'CHARGEMODE', 'Lademodus (always_charging oder schedule_mode)',
  'Charge mode (always_charging or schedule_mode)')
s('THEMA', 'MILEAGE', 'Kilometerstand', 'Odometer')
s('THEMA', 'NAME', 'Name des Fahrzeugs aus den Einstellungen', 'Vehicle name from the settings')
s('THEMA', 'HVACSTATUS', 'Vorklimatisierung: on oder off', 'Preconditioning: on or off')
s('THEMA', 'HVACSTATUSBIN', 'Vorklimatisierung als 0/1 für Loxone', 'Preconditioning as 0/1 for Loxone')
s('THEMA', 'INTEMP', 'Innentemperatur in Grad Celsius (nicht jedes Fahrzeug liefert sie)',
  'Interior temperature in degrees Celsius (not every vehicle provides it)')
s('THEMA', 'OUTTEMP', 'Außentemperatur in Grad Celsius — vom Fahrzeug, ersatzweise vom Wetterdienst',
  'Outside temperature in degrees Celsius — from the vehicle, otherwise from the weather service')
s('THEMA', 'PHPCALL', 'Uhrzeit des letzten ERFOLGREICHEN Abrufs als HHMM',
  'Time of the last SUCCESSFUL retrieval as HHMM')
s('THEMA', 'LASTDATA', 'dasselbe wie phpCall, unter dem älteren Namen',
  'same as phpCall, under the older name')
s('THEMA', 'OK', 'Letzter Abruf erfolgreich (1) oder nicht (0)',
  'Last retrieval successful (1) or not (0)')
s('THEMA', 'BATTEMP', 'Batterietemperatur in Grad Celsius (nur Phase 1)',
  'Battery temperature in degrees Celsius (phase 1 only)')
s('THEMA', 'PHMODE1', 'Fahrzeuggeneration: 1', 'Vehicle generation: 1')
s('THEMA', 'PHMODE2', 'Fahrzeuggeneration: 2', 'Vehicle generation: 2')
s('THEMA', 'GPSLAT', 'Breitengrad des Fahrzeugs', 'Latitude of the vehicle')
s('THEMA', 'GPSLON', 'Längengrad des Fahrzeugs', 'Longitude of the vehicle')
s('THEMA', 'GPSTIME', 'Uhrzeit der letzten Positionsmeldung', 'Time of the last position report')
s('THEMA', 'ENERGIE', 'Verfügbare Energie in kWh', 'Available energy in kWh')
s('THEMA', 'CHG_START_SOC', 'Ladevorgang: Batteriestand am Anfang, in Prozent',
  'Charging session: battery level at the start, in percent')
s('THEMA', 'CHG_END_SOC', 'Ladevorgang: Batteriestand am Ende, in Prozent',
  'Charging session: battery level at the end, in percent')
s('THEMA', 'CHG_DAUER', 'Ladevorgang: Dauer in Minuten', 'Charging session: duration in minutes')
s('THEMA', 'CHG_LEISTUNG', 'Ladevorgang: mittlere Leistung in kW',
  'Charging session: average power in kW')
s('THEMA', 'CHG_ENERGIE', 'Ladevorgang: geladene Energie in kWh',
  'Charging session: energy recovered in kWh')
s('THEMA', 'CHG_STATUS', 'Ladevorgang: Abschlussmeldung', 'Charging session: end status')
s('THEMA', 'CHG_STARTLEISTUNG', 'Ladevorgang: Leistung beim Anstecken, in Watt',
  'Charging session: power when plugged in, in watts')

# ------------------------------------------------------------------ BEFEHL
s('BEFEHL', 'ACNOW', 'Vorklimatisierung starten', 'Start preconditioning')
s('BEFEHL', 'ACOFF', 'Vorklimatisierung beenden', 'Stop preconditioning')
s('BEFEHL', 'CHARGENOW', 'Sofort laden starten', 'Start charging now')
s('BEFEHL', 'CHARGESTOP', 'Laden anhalten', 'Stop charging')
s('BEFEHL', 'CMON', 'Ladeplan aktivieren', 'Activate charging schedule')
s('BEFEHL', 'CMOFF', 'Ladeplan abschalten (immer laden)', 'Deactivate charging schedule (always charge)')
s('BEFEHL', 'ABRUF', 'Daten sofort neu abrufen', 'Fetch data now')

# -------------------------------------------------------------------- FELD
s('FELD', 'LETZTER_ABRUF', 'Zeitpunkt des letzten Versuchs', 'Time of the last attempt')
s('FELD', 'LETZTER_ERFOLG', 'Zeitpunkt des letzten erfolgreichen Abrufs',
  'Time of the last successful retrieval')
s('FELD', 'KILOMETERSTAND', 'Kilometerstand', 'Odometer')
s('FELD', 'DATUM_STATUS', 'Datum des Statusupdates', 'Date of the status update')
s('FELD', 'UHRZEIT_STATUS', 'Uhrzeit des Statusupdates', 'Time of the status update')
s('FELD', 'LADESTATUS', 'Ladestatus', 'Charging status')
s('FELD', 'KABELSTATUS', 'Kabelstatus', 'Cable status')
s('FELD', 'BATTERIESTAND', 'Batteriestand in Prozent', 'Battery level in percent')
s('FELD', 'REICHWEITE', 'Reichweite in km', 'Range in km')
s('FELD', 'LADEMODUS', 'Lademodus', 'Charge mode')
s('FELD', 'MODELLCODE', 'Modellkennung laut Renault', 'Model code as reported by Renault')
s('FELD', 'INNENTEMPERATUR', 'Innentemperatur', 'Interior temperature')
s('FELD', 'AUSSENTEMPERATUR', 'Außentemperatur des Fahrzeugs', 'Outside temperature from the vehicle')

# ----------------------------------------------------------------- MELDUNG
s('MELDUNG', 'AKKUSTAND_ERREICHT', 'Der eingestellte Akkustand ist erreicht.',
  'The configured battery level has been reached.')
s('MELDUNG', 'LADEN_BEENDET', 'Der Ladevorgang ist beendet.', 'Charging has finished.')
s('MELDUNG', 'AKKUSTAND', 'Akkustand', 'Battery level')
s('MELDUNG', 'RESTLADEZEIT', 'Restladezeit', 'Remaining charging time')
s('MELDUNG', 'REICHWEITE', 'Reichweite', 'Range')
s('MELDUNG', 'STATUSUPDATE', 'Statusupdate', 'Status update')
s('MELDUNG', 'MINUTEN', 'Minuten', 'minutes')
s('MELDUNG', 'WENIGE', 'wenige', 'a few')
s('MELDUNG', 'START', 'Start', 'Start')
s('MELDUNG', 'LADEVORGANG', 'Ladevorgang', 'Charging session')
s('MELDUNG', 'BIS', 'bis', 'to')
s('MELDUNG', 'IN', 'in', 'in')
s('MELDUNG', 'LEISTUNG', 'Leistung', 'Power')
s('MELDUNG', 'STATUS', 'Status', 'Status')
s('MELDUNG', 'UM', 'um', 'at')

# ------------------------------------------------------------------- PRUEF
s('PRUEF', 'ZUGANG', 'Zugangsdaten hinterlegt?', 'Credentials stored?')
s('PRUEF', 'VIN', 'Fahrgestellnummer gesetzt?', 'Vehicle identification number set?')
s('PRUEF', 'RECHTE', 'Rechte der Konfigurationsdatei (soll 0600)',
  'Permissions of the configuration file (should be 0600)')
s('PRUEF', 'GATEWAY', 'MQTT-Gateway eingerichtet?', 'MQTT gateway configured?')
s('PRUEF', 'AUTOSTART', 'Startet das Gateway automatisch?', 'Does the gateway start automatically?')
s('PRUEF', 'ALTER', 'Wie alt ist der letzte Abruf von %s?',
  'How old is the last retrieval for %s?')
s('PRUEF', 'STEUERUNG', 'Dürfen Befehle aus Loxone schalten?',
  'Are switching commands from Loxone allowed?')
s('PRUEF', 'TOKEN', 'Aktionstoken vorhanden?', 'Action token present?')
s('PRUEF', 'THEMEN', 'Stimmt die Themenliste mit dem Programmcode überein?',
  'Does the topic list match the program code?')
s('PRUEF', 'REITER', 'Stimmen Reiterleiste und Bereiche überein?',
  'Do the tab bar and the panes match?')
s('PRUEF', 'PROTOKOLL', 'Protokoll vorhanden?', 'Log file present?')
s('PRUEF', 'JA', 'ja', 'yes')
s('PRUEF', 'NEIN', 'nein', 'no')
s('PRUEF', 'NEIN_EINSTELLUNGEN', 'nein — Reiter Einstellungen', 'no — see the Settings tab')
s('PRUEF', 'KEINE_CONFIG', 'noch keine Konfigurationsdatei', 'no configuration file yet')
s('PRUEF', 'KEIN_BROKER', 'kein Broker in general.json', 'no broker in general.json')
s('PRUEF', 'KEIN_AUTOSTART', 'nein — nach einem Neustart kommt nichts an',
  'no — after a reboot nothing will arrive')
s('PRUEF', 'UNBEKANNT', 'unbekannt', 'unknown')
s('PRUEF', 'NIE', 'noch nie erfolgreich abgerufen', 'never retrieved successfully')
s('PRUEF', 'UNLESBAR', 'Zeitstempel unlesbar', 'timestamp unreadable')
s('PRUEF', 'VOR_MINUTEN', 'vor %d Minuten (Schwelle %d)', '%d minutes ago (threshold %d)')
s('PRUEF', 'N_FAHRZEUGE', '%d Fahrzeug(e) mit Nummer', '%d vehicle(s) with a number')
s('PRUEF', 'N_ZEICHEN', 'ja, %d Zeichen', 'yes, %d characters')
s('PRUEF', 'N_ZEILEN', 'ja, %d Zeilen gelesen', 'yes, %d lines read')
s('PRUEF', 'LEER', 'noch leer', 'still empty')
s('PRUEF', 'STEUERUNG_EIN', 'ja — schaltende Befehle sind freigegeben',
  'yes — switching commands are enabled')
s('PRUEF', 'STEUERUNG_AUS', 'nein (Vorgabe) — nur lesende Aufrufe',
  'no (default) — read-only calls')
s('PRUEF', 'THEMEN_OK', 'ja, alle %d Themen stimmen überein', 'yes, all %d topics match')
s('PRUEF', 'THEMEN_ABWEICHUNG',
  'NEIN — %d in der Anleitung ohne Sendecode, %d gesendet ohne Anleitung. Knopf Themen abgleichen.',
  'NO — %d documented without code, %d sent without documentation. Use the Compare topics button.')
s('PRUEF', 'REITER_OK', 'ja, %d Reiter kongruent', 'yes, %d tabs congruent')
s('PRUEF', 'REITER_ABWEICHUNG',
  'NEIN — Quelle, Leiste und Bereiche nennen nicht dieselben Namen',
  'NO — source, bar and panes do not name the same tabs')
s('PRUEF', 'MASKIERUNG', 'Wird ein Text doppelt maskiert ausgegeben?',
  'Is any text output double-escaped?')
s('PRUEF', 'MASKIERUNG_OK', 'nein', 'no')
s('PRUEF', 'MASKIERUNG_ABWEICHUNG',
  'JA, %d Stelle(n): %s — der Text erscheint im Browser wörtlich',
  'YES, %d place(s): %s — the markup shows up literally in the browser')

s('PRUEF', 'H_UNVOLLSTAENDIG',
  'Solange Benutzer oder Passwort fehlen, wird nichts an Renault gesendet.',
  'As long as user name or password are missing, nothing is sent to Renault.')
s('PRUEF', 'UNBEKANNT_TITEL', 'Unbekannte Prüfung', 'Unknown check')
s('PRUEF', 'UNBEKANNT_TEXT', 'Diese Prüfung gibt es nicht.', 'This check does not exist.')

# -------------------------------------------------------------------- TEXT
def t(k, de, en):
    s('TEXT', k, de, en)

t('NICHT_GESPEICHERT', 'Nicht gespeichert:', 'Not saved:')
# --- Ueberschriften und Erklaerungen, Reiter Einstellungen
t('H_KONTO', 'Zugang zum Renault-Konto', 'Access to the Renault account')
t('H_KONTO_TEXT',
  'Dieselben Zugangsdaten wie in der My-Renault-App. Sie liegen in <span class="sm-mono">config.php</span> '
  'mit den Rechten 0600 und werden nur an Renault geschickt.',
  'The same credentials as in the My Renault app. They are stored in <span class="sm-mono">config.php</span> '
  'with permissions 0600 and are only sent to Renault.')
t('L_BENUTZER', 'Benutzer (E-Mail-Adresse)', 'User (e-mail address)')
t('L_PASSWORT', 'Passwort', 'Password')
t('P_GESPEICHERT', 'gespeichert – leer lassen, um es zu behalten',
  'stored – leave empty to keep it')
t('P_NICHT_GESETZT', 'noch nicht gesetzt', 'not set yet')
t('H_PASSWORT', 'Das gespeicherte Passwort wird nie angezeigt. Ein leeres Feld lässt es unverändert.',
  'The stored password is never displayed. An empty field leaves it unchanged.')
t('L_LAND', 'Land', 'Country')
t('L_ANDERE', 'andere / Englisch', 'other / English')

t('H_FAHRZEUGE', 'Fahrzeuge', 'Vehicles')
t('H_FAHRZEUGE_TEXT',
  'Bis zu vier Fahrzeuge desselben Kontos. Jedes bekommt seinen eigenen MQTT-Themenpfad, '
  'seinen eigenen Zwischenspeicher und seine eigene Aufzeichnung. Die Anmeldung bei Renault '
  'ist gemeinsam — es wird also nicht je Fahrzeug angemeldet.',
  'Up to four vehicles from the same account. Each gets its own MQTT topic path, its own cache '
  'and its own recording. The Renault login is shared — there is no separate login per vehicle.')
t('H_FAHRZEUG_NR', 'Fahrzeug %d', 'Vehicle %d')
t('H_OPTIONAL', 'optional', 'optional')
t('L_NAME', 'Name des Fahrzeugs', 'Vehicle name')
t('H_NAME', 'Bildet den MQTT-Themenpfad, ohne / # und +:', 'Forms the MQTT topic path, without / # and +:')
t('L_VIN', 'Fahrgestellnummer (VIN)', 'Vehicle identification number (VIN)')
t('H_VIN', '17 Zeichen ohne I, O und Q. Steht im Fahrzeugschein und in der My-Renault-App unter Fahrzeugdaten.',
  '17 characters without I, O and Q. Shown in the vehicle registration and in the My Renault app under vehicle data.')
t('L_PHASE', 'Fahrzeuggeneration', 'Vehicle generation')
t('O_PHASE1', 'Phase 1 (mit Batterietemperatur)', 'Phase 1 (with battery temperature)')
t('O_PHASE2', 'Phase 2 (mit GPS-Position)', 'Phase 2 (with GPS position)')
t('H_PHASE', 'Welche Werte Renault liefert, hängt an der Generation.',
  'Which values Renault provides depends on the generation.')
t('H_MODELLKENNUNG', 'Ihr Fahrzeug meldet die Modellkennung %s.', 'Your vehicle reports model code %s.')

t('H_TAKT', 'Abruftakt', 'Retrieval interval')
t('H_TAKT_TEXT',
  'Der Cron läuft alle drei Minuten und fragt erst dann bei Renault nach, wenn der eingestellte '
  'Abstand erreicht ist. Während das Fahrzeug lädt, gilt der kürzere Wert. Beide Werte standen '
  'bis 2.0.6 nur in der Konfigurationsdatei und waren aus der Oberfläche nicht erreichbar.',
  'The cron job runs every three minutes and only queries Renault once the configured interval has '
  'elapsed. While the vehicle is charging, the shorter value applies. Until 2.0.6 both values existed '
  'only in the configuration file and could not be reached from the user interface.')
t('L_CRON_NCS', 'Abstand im Normalbetrieb (Minuten)', 'Interval in normal operation (minutes)')
t('L_CRON_ACS', 'Abstand während des Ladens (Minuten)', 'Interval while charging (minutes)')

t('H_SCHALTEN', 'Schalten', 'Switching')
t('H_SCHALTEN_TEXT',
  '<b>Ab Werk ausgeschaltet.</b> Solange dieser Schalter auf aus steht, weist der Endpunkt jeden '
  'Befehl ab, der am Fahrzeug etwas verändert — Vorklimatisierung, Laden, Ladeplan. Lesende '
  'Aufrufe sind davon nicht betroffen. Ein frisch installiertes Plugin soll nicht aus dem Stand '
  'heraus die Klimaanlage starten können.',
  '<b>Off by default.</b> While this switch is off, the endpoint rejects every command that changes '
  'anything on the vehicle — preconditioning, charging, charging schedule. Read-only calls are '
  'not affected. A freshly installed plugin must not be able to start the air conditioning right away.')
t('L_STEUERUNG', 'Befehle aus Loxone dürfen schalten', 'Allow switching commands from Loxone')
t('O_AUS_VORGABE', 'aus (Vorgabe)', 'off (default)')
t('O_EIN', 'ein', 'on')
t('L_AC_TEMP', 'Zieltemperatur der Vorklimatisierung (Grad Celsius)',
  'Target temperature for preconditioning (degrees Celsius)')
t('H_AC_TEMP', 'Erlaubt sind 16 bis 30. Bis 2.0.6 stand hier fest 21 im Quelltext.',
  'Allowed range 16 to 30. Until 2.0.6 this was hard-coded to 21.')

t('H_MELDUNGEN', 'Meldungen', 'Notifications')
t('H_MELDUNGEN_TEXT',
  'Diese Funktionen gibt es seit Langem im Programmcode, aber bis 2.0.6 gab es kein Feld dafür — '
  'wer sie nutzen wollte, musste config.php von Hand bearbeiten. <b>Ab Werk sind alle aus.</b>',
  'These functions have existed in the program code for a long time, but until 2.0.6 there was no '
  'field for them — anyone wanting to use them had to edit config.php by hand. <b>All are off by default.</b>')
t('L_BL_SCHWELLE', 'Meldung bei diesem Akkustand (Prozent)', 'Notify at this battery level (percent)')
t('L_MAIL_BL', 'E-Mail bei erreichtem Akkustand', 'E-mail when the battery level is reached')
t('L_CMON_BL', 'Bei erreichtem Akkustand auf Ladeplan umschalten',
  'Switch to charging schedule when the battery level is reached')
t('L_MAIL_CSF', 'E-Mail bei beendetem Ladevorgang', 'E-mail when charging has finished')
t('L_EXEC_BL', 'Befehl bei erreichtem Akkustand', 'Command when the battery level is reached')
t('L_EXEC_CSF', 'Befehl bei beendetem Ladevorgang', 'Command when charging has finished')
t('H_EXEC',
  'Der Befehl wird auf dem LoxBerry ausgeführt; die Meldung hängt als ein einzelnes, maskiertes '
  'Argument daran. Beispiel: <span class="sm-mono">/usr/bin/logger -t renault</span>. Der Befehl '
  'selbst wird nicht maskiert — er ist Ihre Eingabe, kein Fremdwert.',
  'The command is executed on the LoxBerry; the message is appended as a single, escaped argument. '
  'Example: <span class="sm-mono">/usr/bin/logger -t renault</span>. The command itself is not '
  'escaped — it is your own input, not a foreign value.')

t('H_LADEZIEL', 'Ladeziel', 'Charge target')
t('H_LADEZIEL_TEXT',
  'Untergrenze und Zielwert des Ladestands. <b>Das können nur die neueren Plattformen</b> '
  '(Megane E-Tech, Scenic, R5, R4, A290, Master). Zoe Phase 1 und Phase 2 kennen den Endpunkt nicht; '
  'dort bleibt eine Eingabe wirkungslos und wird einmal im Protokoll vermerkt. Beide Felder leer '
  'lassen heißt: das Plugin fasst das Ladeziel nicht an.',
  'Lower limit and target value of the state of charge. <b>Only the newer platforms support this</b> '
  '(Megane E-Tech, Scenic, R5, R4, A290, Master). Zoe phase 1 and phase 2 do not know this endpoint; '
  'there an entry has no effect and is noted once in the log. Leaving both fields empty means the '
  'plugin does not touch the charge target.')
t('L_SOC_MIN', 'Untergrenze (Prozent)', 'Lower limit (percent)')
t('L_SOC_TARGET', 'Zielwert (Prozent)', 'Target value (percent)')
t('H_SOC_LEER', 'Leer lassen = nicht anfassen. Erlaubt sind 20 bis 100.',
  'Leave empty = do not touch. Allowed range 20 to 100.')

t('O_JA', 'ja', 'yes')
t('O_NEIN', 'nein', 'no')

t('H_AUFZEICHNUNG', 'Aufzeichnung', 'Recording')
t('L_SAVE_IN_DB', 'Werte in database.csv mitschreiben', 'Record values in database.csv')
t('O_JA_ANHAENGEN', 'ja, jede Abfrage anhängen', 'yes, append every query')
t('H_AUFZEICHNUNG_TEXT',
  'Grundlage des Diagramms im Reiter Ladehistorie. Die Datei wächst langsam, aber stetig.',
  'This is what the chart on the Charging history tab is based on. The file grows slowly but steadily.')

t('H_FREMDDIENSTE', 'Fremddienste', 'Third-party services')
t('L_WETTER', 'OpenWeatherMap-Schlüssel', 'OpenWeatherMap key')
t('H_WETTER',
  'Nur als Ersatz gedacht: die Außentemperatur liefert bei vielen Fahrzeugen die Renault-Schnittstelle '
  'selbst (Thema OutTemp). Der hier benutzte Endpunkt der Fassung 2.5 ist bei OpenWeatherMap '
  'abgekündigt; antwortet er mit einem Fehler, steht das im Protokoll.',
  'Intended only as a fallback: for many vehicles the outside temperature comes from the Renault '
  'interface itself (topic OutTemp). The version 2.5 endpoint used here has been retired by '
  'OpenWeatherMap; if it answers with an error, that is noted in the log.')
t('L_ABRP_TOKEN', 'ABRP-Token', 'ABRP token')
t('L_ABRP_MODEL', 'ABRP-Fahrzeugmodell', 'ABRP car model')
t('H_ABRP', 'Beide Felder müssen gefüllt sein, sonst wird nichts gesendet.',
  'Both fields must be filled in, otherwise nothing is sent.')

t('K_SPEICHERN', 'Speichern', 'Save')

# --- Beanstandungen
t('F_NAME_LEER', 'Der Name von Fahrzeug 1 darf nicht leer sein – er bildet den MQTT-Themenpfad.',
  'The name of vehicle 1 must not be empty – it forms the MQTT topic path.')
t('F_NAME_SONDERZEICHEN',
  'Der Name von Fahrzeug %d darf kein <span class="sm-mono">/</span>, <span class="sm-mono">#</span> '
  'oder <span class="sm-mono">+</span> enthalten – das sind Sonderzeichen in MQTT-Themen.',
  'The name of vehicle %d must not contain <span class="sm-mono">/</span>, <span class="sm-mono">#</span> '
  'or <span class="sm-mono">+</span> – these are special characters in MQTT topics.')
t('F_NAME_DOPPELT', 'Der Name %s ist zweimal vergeben – zwei Fahrzeuge lägen im selben Themenpfad.',
  'The name %s is used twice – two vehicles would share the same topic path.')
t('F_VIN', 'Die Fahrgestellnummer von Fahrzeug %d besteht aus 17 Zeichen ohne I, O und Q.',
  'The vehicle identification number of vehicle %d consists of 17 characters without I, O and Q.')
t('F_PHASE', 'Die Generation von Fahrzeug %d muss 1 oder 2 sein.',
  'The generation of vehicle %d must be 1 or 2.')
t('F_AUFZEICHNUNG', 'Die Aufzeichnung kennt nur ja oder nein.', 'Recording only knows yes or no.')
t('F_STEUERUNG', 'Die Steuerung kennt nur ein oder aus.', 'Switching only knows on or off.')
t('F_LAND', 'Das Land ist ein Kürzel aus zwei Großbuchstaben.',
  'The country is a two-letter uppercase code.')
t('F_ZAHL', 'Der Wert für %s muss eine ganze Zahl zwischen %d und %d sein.',
  'The value for %s must be a whole number between %d and %d.')
t('F_SOC_REIHENFOLGE', 'Die Untergrenze des Ladeziels darf nicht über dem Zielwert liegen.',
  'The lower limit of the charge target must not exceed the target value.')
t('F_BENUTZER_FEHLT', 'Es ist ein Passwort hinterlegt, aber kein Benutzername.',
  'A password is stored, but no user name.')
t('F_SCHREIBEN',
  'Die Datei <span class="sm-mono">config.php</span> ließ sich nicht schreiben. Rechte im '
  'Konfigurationsordner prüfen – der Reiter Test zeigt ihn an.',
  'The file <span class="sm-mono">config.php</span> could not be written. Check the permissions of '
  'the configuration folder – the Test tab shows where it is.')
t('F_TOKEN_SCHREIBEN', 'Das Aktionstoken konnte nicht gespeichert werden.',
  'The action token could not be saved.')
t('F_FORMTOKEN',
  'Das Formular trug kein gültiges Merkmal – es wurde <b>nichts</b> übernommen. '
  'Bitte die Seite neu laden und den Vorgang wiederholen. Der Schutz verhindert, dass '
  'eine fremde Seite im Namen der angemeldeten Sitzung Einstellungen ändert – hier wäre '
  'das besonders teuer, denn zu den Feldern gehören zwei Befehlszeilen, die der Abruf '
  'später ausführt.',
  'The form did not carry a valid marker – <b>nothing</b> was applied. Please reload the '
  'page and repeat the action. The protection stops a foreign page from changing settings '
  'in the name of the signed-in session – which would be particularly costly here, because '
  'two of the fields are command lines that the retrieval later executes.')
t('M_GESPEICHERT', 'Gespeichert. Der Zwischenspeicher wurde geleert, der nächste Abruf holt alles neu.',
  'Saved. The cache has been cleared; the next retrieval will fetch everything anew.')
t('M_TOKEN_NEU',
  'Neues Token erzeugt. <b>Die Adressen in Loxone müssen angepasst werden</b> – die alten '
  'funktionieren nicht mehr.',
  'New token generated. <b>The addresses in Loxone must be updated</b> – the old ones no longer work.')
t('M_LOG_LEER', 'Das Protokoll wurde geleert.', 'The log has been cleared.')
t('M_CACHE_LEER', 'Zwischenspeicher und Anmeldung wurden verworfen. Der nächste Abruf meldet sich neu an.',
  'Cache and login have been discarded. The next retrieval will log in again.')

# --- Reiter MQTT
t('H_GATEWAY', 'Zustand des MQTT-Gateways', 'State of the MQTT gateway')
t('H_GATEWAY_TEXT',
  'Das MQTT-Gateway ist seit LoxBerry 3 <b>Bestandteil des Systems</b> und kein Plugin. Es wird unter '
  '<i>System &rarr; MQTT Gateway</i> eingerichtet.',
  'Since LoxBerry 3 the MQTT gateway is <b>part of the system</b> and not a plugin. It is configured '
  'under <i>System &rarr; MQTT Gateway</i>.')
t('H_KEIN_BROKER',
  'In <span class="sm-mono">config/system/general.json</span> steht kein Broker. Das Plugin kann seine '
  'Werte nirgends hinschicken. Unter <i>System &rarr; MQTT Gateway</i> einrichten.',
  'There is no broker in <span class="sm-mono">config/system/general.json</span>. The plugin has nowhere '
  'to send its values. Configure it under <i>System &rarr; MQTT Gateway</i>.')
t('S_GROESSE', 'Größe', 'Item')
t('S_WERT', 'Wert', 'Value')
t('S_BROKER', 'Broker', 'Broker')
t('S_LOKAL', 'Eigener Broker auf dem LoxBerry', 'Local broker on the LoxBerry')
t('S_FREMDER_BROKER', 'nein – es wird ein fremder Broker verwendet',
  'no – an external broker is used')
t('S_AUTOSTART', 'Gateway startet automatisch', 'Gateway starts automatically')
t('S_KEIN_AUTOSTART', 'nein – nach einem Neustart kommt nichts an',
  'no – after a reboot nothing will arrive')
t('S_BENUTZER', 'Benutzer', 'User')
t('H_ABO', 'Das einzutragende Abonnement', 'The subscription to enter')
t('H_ABO_PFLICHT', 'Ohne diesen Eintrag kommt am Miniserver nichts an.',
  'Without this entry nothing arrives at the Miniserver.')
t('H_ABO_WO', 'Einzutragen unter <i>System &rarr; MQTT Gateway &rarr; Abonnements</i>:',
  'To be entered under <i>System &rarr; MQTT Gateway &rarr; Subscriptions</i>:')
t('H_THEMEN', 'Veröffentlichte Themen', 'Published topics')
t('H_THEMEN_TEXT',
  'Alle Werte werden <b>retained</b> gesendet — ein neu verbundener Teilnehmer bekommt sofort den '
  'letzten Stand. Diese Liste wird im Reiter Test gegen den Programmcode geprüft; bis 2.0.6 nannte sie '
  'fünf Themen, die es nie gab.',
  'All values are sent <b>retained</b> — a newly connected subscriber immediately receives the last '
  'known state. This list is checked against the program code on the Test tab; until 2.0.6 it named five '
  'topics that never existed.')
t('S_PHASE', 'Phase %s', 'phase %s')
t('S_THEMA', 'Thema', 'Topic')
t('S_BEDEUTUNG', 'Bedeutung', 'Meaning')

# --- Reiter Einbindung in Loxone
t('H_LOXONE', 'Einbindung in Loxone, Schritt für Schritt', 'Loxone integration, step by step')
t('H_LOXONE_TEXT',
  'Das Plugin holt die Fahrzeugdaten von Renault und legt sie im MQTT-Broker ab. Loxone liest sie von '
  'dort. Umgekehrt schickt Loxone Befehle an einen Endpunkt dieses Plugins.',
  'The plugin fetches the vehicle data from Renault and publishes it to the MQTT broker. Loxone reads it '
  'from there. Conversely, Loxone sends commands to an endpoint of this plugin.')
t('SCHRITT1', 'Schritt 1: Weg festlegen', 'Step 1: choose the path')
t('SCHRITT1_TEXT',
  '<b>MQTT ist der Regelweg</b> für alle Messwerte. Für die Befehle gibt es den Endpunkt aus Schritt 4.',
  '<b>MQTT is the standard path</b> for all measured values. For commands there is the endpoint from step 4.')
t('SCHRITT2', 'Schritt 2: Abonnement im MQTT-Gateway eintragen',
  'Step 2: enter the subscription in the MQTT gateway')
t('SCHRITT3', 'Schritt 3: Virtuelle Eingänge anlegen', 'Step 3: create virtual inputs')
t('SCHRITT3_TEXT',
  'Das MQTT-Gateway legt die Eingänge selbst an, sobald der erste Wert ankommt. Wer sie vorher haben '
  'will, benutzt die Importdatei weiter unten.',
  'The MQTT gateway creates the inputs itself as soon as the first value arrives. To have them beforehand, '
  'use the import file below.')
t('S_TITEL', 'Titel', 'Title')
t('S_EINHEIT', 'Einheit', 'Unit')
t('H_VORLAGE', 'Alles auf einmal anlegen', 'Create everything at once')
t('H_VORLAGE_TEXT',
  'Statt jeden Eingang von Hand anzulegen: diese Datei legt sie mit den richtigen Namen an; die Werte '
  'kommen dann vom MQTT-Gateway. <b>Achtung:</b> Loxone Config legt beim Import neu an und überschreibt '
  'nichts — zweimal eingelesen ergibt doppelte Bausteine. Die Adresse im Kopf ist ein Vorschlag; '
  'bitte prüfen, unter welchem Namen der Miniserver den LoxBerry erreicht.',
  'Instead of creating every input by hand, this file creates them with the correct names; the values then '
  'come from the MQTT gateway. <b>Note:</b> Loxone Config creates new objects on import and overwrites '
  'nothing — importing twice results in duplicate blocks. The address in the header is a suggestion; '
  'please check under which name the Miniserver reaches the LoxBerry.')
t('K_VORLAGE_VI', 'Importdatei für die Eingänge erzeugen', 'Create import file for the inputs')
t('K_VORLAGE_VQ', 'Importdatei für die Befehle erzeugen', 'Create import file for the commands')
t('SCHRITT4', 'Schritt 4: Befehle senden', 'Step 4: send commands')
t('SCHRITT4_TEXT',
  'Je Befehl ein <b>virtueller Ausgang Befehl</b>. Die Adresse des virtuellen Ausgangs ist '
  '<span class="sm-mono">http://&lt;LoxBerry&gt;</span>, im Befehl bei EIN steht dann:',
  'One <b>virtual output command</b> per command. The address of the virtual output is '
  '<span class="sm-mono">http://&lt;LoxBerry&gt;</span>, and the command on ON is then:')
t('SCHRITT4_ENDPUNKT',
  'Der Endpunkt liegt im unangemeldeten Bereich und ist durch das Token geschützt. Der Selbsttest in der '
  'letzten Zeile beantwortet, ob das in Loxone eingetragene Token noch stimmt — <b>ohne am Fahrzeug '
  'etwas zu schalten</b>. Antwort bei richtigem Token: '
  '<span class="sm-mono">SELFTEST;OK=1;TOKEN=OK</span>.',
  'The endpoint is in the unauthenticated area and is protected by the token. The self-test in the last row '
  'answers whether the token entered in Loxone is still valid — <b>without switching anything on the '
  'vehicle</b>. Response with a valid token: <span class="sm-mono">SELFTEST;OK=1;TOKEN=OK</span>.')
t('S_ZWECK', 'Zweck', 'Purpose')
t('S_BEFEHL_EIN', 'Befehl bei EIN', 'Command on ON')
t('S_SELBSTTEST', 'Selbsttest (schaltet nichts)', 'Self-test (switches nothing)')
t('H_STEUERUNG_AUS',
  '<b>Die Steuerung ist ausgeschaltet.</b> Schaltende Befehle werden mit HTTP 403 abgewiesen. Einschalten '
  'im Reiter Einstellungen, Abschnitt Schalten. Lesende Aufrufe '
  '(<span class="sm-mono">aktion=abruf</span>) und der Selbsttest gehen trotzdem.',
  '<b>Switching is disabled.</b> Switching commands are rejected with HTTP 403. Enable it on the Settings '
  'tab, section Switching. Read-only calls (<span class="sm-mono">aktion=abruf</span>) and the self-test '
  'still work.')
t('K_TOKEN_NEU', 'Neues Token erzeugen', 'Generate a new token')
t('SCHRITT5', 'Schritt 5: Ausfallerkennung', 'Step 5: failure detection')
t('SCHRITT5_TEXT',
  'Schweigt Renault, behalten die virtuellen Eingänge ihren letzten Wert — in der App sieht dann alles '
  'normal aus. Deshalb <span class="sm-mono">ok</span> und <span class="sm-mono">phpCall</span> mitführen: '
  '<span class="sm-mono">ok</span> geht bei einem fehlgeschlagenen Abruf auf 0, und '
  '<span class="sm-mono">phpCall</span> ändert sich nur bei einem <b>erfolgreichen</b> Abruf. Bis 2.0.6 '
  'wurde der Zeitstempel auch im Fehlerfall aufgefrischt — die Ausfallerkennung konnte also gar nicht '
  'ansprechen. Die Schwelle deutlich über den Abruftakt legen.',
  'If Renault goes silent, the virtual inputs keep their last value — in the app everything then looks '
  'normal. Therefore carry <span class="sm-mono">ok</span> and <span class="sm-mono">phpCall</span>: '
  '<span class="sm-mono">ok</span> goes to 0 on a failed retrieval, and <span class="sm-mono">phpCall</span> '
  'only changes on a <b>successful</b> one. Until 2.0.6 the timestamp was refreshed even on failure — '
  'so failure detection could never trigger. Set the threshold well above the retrieval interval.')
t('SCHRITT6', 'Schritt 6: Komplette Baustein-Liste', 'Step 6: complete block list')
t('SCHRITT6_TEXT',
  'Von oben nach unten abarbeiten. Die Bausteine findet Loxone Config über die Baustein-Suche (F5).',
  'Work through it from top to bottom. Loxone Config finds the blocks via the block search (F5).')
t('S_BAUSTEIN', 'Baustein (Typ)', 'Block (type)')
t('S_NAME_VORSCHLAG', 'Name (Vorschlag)', 'Name (suggestion)')
t('S_PARAMETER', 'Parameter', 'Parameter')
t('S_EINGAENGE', 'Eingänge verbinden mit', 'Connect inputs to')
t('S_EINGANG', 'Eingang', 'Input')
t('B_VI', 'Virtueller Eingang', 'Virtual input')
t('B_VQ', 'Virtueller Ausgang Befehl', 'Virtual output command')
t('B_STATUS', 'Statusbaustein', 'Status block')
t('B_VERGLEICHER', 'Vergleicher', 'Comparator')
t('B_TREPPENLICHT', 'Treppenlichtschalter', 'Stairwell light switch')
t('B_ODER', 'ODER', 'OR')
t('B_BENACHRICHTIGUNG', 'Benachrichtigung', 'Notification')
t('P_STATUS', 'Text je Ladestatus', 'Text per charging status')
t('P_SCHWELLE20', 'Schwelle 20', 'Threshold 20')
t('P_HALTEZEIT', 'Haltezeit 1200 s', 'Hold time 1200 s')
t('P_FLANKE', 'Eingang: Flankenerkennung von', 'Input: edge detection from')
t('P_TEXT_FREI', 'Text frei', 'Free text')
t('S_VON_VISU', 'von der Visualisierung', 'from the visualisation')
t('ZU_9', 'Zu #9:', 'On #9:')
t('ZU_9_TEXT',
  'Der Treppenlichtschalter wird von jeder Änderung an <span class="sm-mono">phpCall</span> neu angestoßen. '
  'Läuft er ab, hat das Plugin länger nichts Neues geliefert.',
  'The stairwell light switch is retriggered by every change of <span class="sm-mono">phpCall</span>. If it '
  'expires, the plugin has not delivered anything new for a while.')
t('ZU_10', 'Zu #10 und #11:', 'On #10 and #11:')
t('ZU_10_TEXT',
  'Der Benachrichtigungs-Baustein sendet nur beim Wechsel von Aus auf Ein. <b>Niemals mehrere Quellen '
  'direkt an seinen Eingang</b> — erst über ODER zusammenführen, sonst verschluckt eine dauerhaft '
  'aktive Quelle alle übrigen.',
  'The notification block only sends on a transition from off to on. <b>Never connect several sources '
  'directly to its input</b> — merge them through an OR first, otherwise a permanently active source '
  'swallows all the others.')
t('SCHRITT7', 'Schritt 7: Gegenprobe', 'Step 7: verification')
t('SCHRITT7_TEXT',
  'Im Reiter Test den Knopf <i>Daten sofort neu abrufen</i> drücken, danach in Loxone Config die virtuellen '
  'Eingänge ansehen. Ob das Token stimmt, beantwortet der Selbsttest aus Schritt 4.',
  'On the Test tab press <i>Fetch data now</i>, then look at the virtual inputs in Loxone Config. Whether the '
  'token is valid is answered by the self-test from step 4.')

# --- Reiter Test
t('H_SELBSTPRUEFUNG', 'Selbstprüfung', 'Self-check')
t('S_FRAGE', 'Frage', 'Question')
t('S_ANTWORT', 'Antwort', 'Answer')
t('H_NACHSEHEN', 'Nachsehen', 'Inspect')
t('K_UMGEBUNG', 'Umgebung prüfen', 'Check environment')
t('K_KONFIG', 'Gespeicherte Konfiguration', 'Stored configuration')
t('K_ZWISCHEN', 'Zwischengespeicherte Daten', 'Cached data')
t('K_THEMEN', 'Themen abgleichen', 'Compare topics')
t('K_VORLAGE_PRUEFEN', 'Importdateien prüfen', 'Check import files')
t('H_TECHNIK', 'Technischer Eingriff', 'Technical intervention')
t('K_CACHE_LEEREN', 'Zwischenspeicher und Anmeldung verwerfen', 'Discard cache and login')
t('H_SCHALTEN_TEST', 'Schalten', 'Switching')
t('H_SCHALTEN_TEST_TEXT',
  'Diese Knöpfe sprechen <b>sofort</b> mit Renault und wirken am Fahrzeug. Sie rufen denselben Endpunkt auf, '
  'den auch Loxone benutzt — wer hier etwas auslöst, prüft damit zugleich Token und Adresse.',
  'These buttons talk to Renault <b>immediately</b> and take effect on the vehicle. They call the same '
  'endpoint that Loxone uses — triggering something here also verifies token and address.')
t('H_LETZTER_STAND', 'Letzter Stand', 'Last known state')
t('H_KEIN_ABRUF', 'Es wurde noch kein Abruf durchgeführt.', 'No retrieval has been performed yet.')
t('S_FELD', 'Feld', 'Field')

# --- Reiter Ladehistorie
t('H_VERLAUF', 'Aufgezeichnete Werte', 'Recorded values')
t('H_VERLAUF_TEXT',
  'Ist die Aufzeichnung im Reiter <i>Einstellungen</i> eingeschaltet, hängt jeder erfolgreiche Abruf eine '
  'Zeile an <span class="sm-mono">database.csv</span> an. Die Datei überlebt Updates und Neuinstallationen.',
  'If recording is enabled on the <i>Settings</i> tab, every successful retrieval appends a line to '
  '<span class="sm-mono">database.csv</span>. The file survives updates and reinstallations.')
t('H_AUFZEICHNUNG_AUS',
  'Die Aufzeichnung ist derzeit <b>ausgeschaltet</b>. Ohne sie bleibt dieses Diagramm leer.',
  'Recording is currently <b>switched off</b>. Without it this chart stays empty.')
t('H_KEINE_CSV',
  'Noch keine <span class="sm-mono">database.csv</span> vorhanden. Sie entsteht beim ersten erfolgreichen '
  'Abruf mit eingeschalteter Aufzeichnung.',
  'No <span class="sm-mono">database.csv</span> yet. It is created on the first successful retrieval with '
  'recording enabled.')
t('H_CSV_LEER', 'Die Datei enthält noch keine Datenzeile.', 'The file does not contain a data row yet.')
t('H_ZU_WENIG_PUNKTE', 'Für ein Diagramm braucht es mindestens zwei lesbare Zeilen.',
  'A chart needs at least two readable rows.')
t('S_BATTERIESTAND', 'Batteriestand in Prozent', 'Battery level in percent')
t('S_REICHWEITE_MAX', 'Reichweite, auf %d km normiert', 'Range, normalised to %d km')
t('H_TABELLE_30', 'Die letzten 30 Zeilen, neueste oben.', 'The last 30 rows, newest first.')

# --- Reiter Logdateien
t('H_LOG', 'Protokoll', 'Log')
t('H_LOG_TEXT', 'Neueste Zeile oben. Datei:', 'Newest line first. File:')
t('H_LOG_LEER', 'Die Protokolldatei ist leer oder noch nicht vorhanden.',
  'The log file is empty or does not exist yet.')
t('K_LOG_LEEREN', 'Protokoll leeren', 'Clear log')


# Abschnitte, deren Werte AUSNAHMSLOS ueber rn_e() ausgegeben werden. Ein
# "&" oder "<" darin wird im Browser woertlich sichtbar - das ist die
# doppelte Maskierung, der teuerste Einzelbefund der Pruefreihe (40 Stellen
# in 13 Plugins). Deshalb steht die Regel hier als Wache und nicht als Satz
# in einer Anleitung.
NUR_TEXT = ('REITER', 'LEGENDE', 'THEMA', 'BEFEHL', 'FELD', 'PRUEF')


def schreiben(pfad, spalte):
    aus = []
    for abschnitt in ('REITER', 'LEGENDE', 'THEMA', 'BEFEHL', 'FELD', 'MELDUNG', 'PRUEF', 'TEXT'):
        aus.append('[%s]' % abschnitt)
        for schluessel, de, en in T[abschnitt]:
            wert = de if spalte == 'de' else en
            # HTML-Attribute in den Texten einfach quotieren. Ein doppeltes
            # Anfuehrungszeichen im Wert beendet fuer parse_ini_file die
            # Zeichenkette; der Rest der Zeile ginge verloren. HTML erlaubt
            # beide Formen, also nehmen wir die, die hier durchgeht.
            wert = wert.replace('="', "='").replace('">', "'>")
            if abschnitt in NUR_TEXT and ('&' in wert or '<' in wert):
                raise SystemExit(
                    'Auszeichnung oder Entitaet in %s.%s: %r - dieser Abschnitt '
                    'geht durch rn_e() und wuerde doppelt maskiert.'
                    % (abschnitt, schluessel, wert))
            if '"' in wert:
                raise SystemExit('Anfuehrungszeichen im Wert %s.%s: %r'
                                 % (abschnitt, schluessel, wert))
            aus.append('%s = "%s"' % (schluessel, wert))
        aus.append('')
    with io.open(pfad, 'w', encoding='utf-8', newline='\r\n') as fh:
        fh.write('\n'.join(aus))
    return sum(len(v) for v in T.values())


# Angenommen wird BEIDES: der Plugin-Ordner (wie bei den Erzeugern der
# anderen Linien) und der Zielordner selbst. Wer den Plugin-Ordner uebergab,
# bekam bis 20.08.2026 zwei Sprachdateien in die WURZEL des Plugins - neben
# die echten unter templates/lang, die unveraendert blieben. Die Meldung sagte
# "geschrieben", und das war wahr, nur am falschen Ort. Deshalb steht der Pfad
# jetzt in der Meldung.
if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(2)
ziel = sys.argv[1]
if os.path.isdir(os.path.join(ziel, 'templates', 'lang')):
    ziel = os.path.join(ziel, 'templates', 'lang')
elif os.path.isdir(os.path.join(ziel, 'webfrontend')):
    print('[FEHL] %s sieht wie ein Plugin-Ordner aus, aber templates/lang fehlt darin.'
          % ziel)
    sys.exit(2)
if not os.path.isdir(ziel):
    print('[FEHL] %s ist kein Verzeichnis.' % ziel)
    sys.exit(2)
n1 = schreiben(os.path.join(ziel, 'language_de.ini'), 'de')
n2 = schreiben(os.path.join(ziel, 'language_en.ini'), 'en')
print('Geschrieben, je %d Schluessel:' % n1)
print('  ' + os.path.join(ziel, 'language_de.ini'))
print('  ' + os.path.join(ziel, 'language_en.ini'))
