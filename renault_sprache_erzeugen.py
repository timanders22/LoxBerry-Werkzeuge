# -*- coding: utf-8 -*-
"""Erzeugt language_de.ini und language_en.ini aus EINER Quelle.

Damit koennen die beiden Schluesselmengen gar nicht auseinanderlaufen -
das war bis 2.0.6 nur eine Zusage in der README (und die nannte dazu die
falsche Zahl: 223 statt 227).

Regeln, die hier eingehalten werden:
  * Werte stehen in doppelten Anfuehrungszeichen und enthalten selbst
    keine - parse_ini_file mit INI_SCANNER_RAW gibt sie sonst mit zurueck.
  * Echte Umlaute, keine ASCII-Umschrift (umschrift_pruefen.py).
  * Zeilenenden LF (Hausregel vom 13.09.2026; bis dahin CRLF).

STAND (Werkzeug-S1, 02.10.2026): nachgezogen auf Renault NG 2.1.15 - erzeugt
language_de.ini und language_en.ini des Archivs
LoxBerry-Plugin-Renault-NG-2.1.15.zip byteweise gleich (35 Schluessel kamen
dazu, 3 Werte neu gefasst). Die help_*.ini schreibt dieser Erzeuger nicht.

STAND (vb_x10_ren, 09.10.2026, Welle X-10 / Sprachmodul 1.1.2): TEXT.SICH_TTS_EINTRAG
entfaellt (Satz K_TTS_EINTRAG kommt mit Modul 1.1.2, wortgleich), TEXT.S_EINGANG entfaellt
(Baustein-Liste in index.php sprachfrei). [ANSAGE] wie immer aus
Werkzeuge/gemeinsam/sprachausgabe_texte.json (157 Schluessel).

STAND (vb_bild_rn17, 17.10.2026, Welle Bild 17 / Musterprojekt, Renault NG 2.1.19): neuer Abschnitt
[BAUSTEIN] (119 Schluessel: Kaesten, Hinweise und die 88 Zeilen der drei Musterseiten), in [TEXT] neu
S_NAME, BILD_ALT, BILD_UNTERSCHRIFT, MUSTERPROJEKT; neu gefasst THEMA.CHARGINGSTATUS, TEXT.SCHRITT5_TEXT,
SCHRITT6, SCHRITT6_TEXT, ZU_10, H_VORLAGE_TEXT; gestrichen die 16 Schluessel der alten Liste (S_NAME_VORSCHLAG,
B_*, P_*, S_VON_VISU, ZU_9, ZU_9_TEXT).

STAND (Drift-Abgleich, 06.11.2026): angeglichen an Renault NG 2.1.30, 174 Schluessel neu, 23 Werte geaendert, 0 entfernt.
Neu die Abschnitte [ALLG], [HAUS], [VORKLIMA], [HEIM], [SIGNAL]; die Abschnittsfolge in bauen() folgt der .ini. [ANSAGE] unveraendert aus
Werkzeuge/gemeinsam/sprachausgabe_texte.json. Neu ROH_AUSGEGEBEN: drei BEFEHL-Werte mit Auszeichnung, die
index.php ohne rn_e() ausgibt, sind vom Abschnittsverbot NUR_TEXT ausgenommen.
"""
# NACHGEZOGEN (Sprachausgabe Renault NG 2.1.16, Nr. 36 b, vb_sp2b_bau_skripte/rn/werkzeug_bauen.py):
# 28 neue Schluessel (de und en) und der Abschnitt [ANSAGE] aus Werkzeuge/gemeinsam/sprachausgabe_texte.json
# (gemeinsam_pruefen.ini_abschnitt()). Werkzeuge/ selbst ist unveraendert.
import io, os, sys

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
s('THEMA', 'CHARGINGSTATUS', 'Ladestatus als Zahl: 1 = lädt, unter 0 = Störung', 'Charging status as a number: 1 = charging, below 0 = fault')
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
s('BEFEHL', 'H',
  'Befehle über MQTT',
  'Commands via MQTT')
s('BEFEHL', 'H_UDP',
  'Der UDP-Eingang des MQTT-Gateways (11884) ist im Heimnetz <b>ohne Anmeldung</b> erreichbar. Schutz sind die Haken: <i>Befehle über MQTT annehmen</i> (hier) und für Laden, Vorklimatisierung und Ladeplan zusätzlich <i>Steuerung</i> (Reiter Einstellungen).',
  'The UDP input of the MQTT gateway (11884) can be reached in the home network <b>without login</b>. The protection is the checkboxes: <i>Accept commands via MQTT</i> (here) and for charging, pre-conditioning and charge schedule additionally <i>Switching</i> (Settings tab).')
s('BEFEHL', 'L_EIN',
  'Befehle über MQTT annehmen (ab Werk aus)',
  'Accept commands via MQTT (off by default)')
s('BEFEHL', 'S_LAGE',
  'Befehlsbrücke',
  'Command bridge')
s('BEFEHL', 'S_WERTE',
  'Werte',
  'Values')
s('BEFEHL', 'S_QUITTUNG',
  'Quittung',
  'Acknowledgement')
s('BEFEHL', 'H_QUITTUNG',
  "Die Quittung kommt unter <span class='sm-mono'>Renault/befehl/&lt;name&gt;/quittung</span>, nie retained. <i>ausgefuehrt</i>: Renault hat den Befehl angenommen (oder derselbe Sollwert ging vor weniger als 60 s hinaus). <i>uebergeben</i>: der Abruf wurde angestossen bzw. der Wert gemerkt. Fahrzeug 2 bis 4: <span class='sm-mono'>Renault/befehl/&lt;n&gt;/&lt;name&gt;</span>.",
  "The acknowledgement comes under <span class='sm-mono'>Renault/befehl/&lt;name&gt;/quittung</span>, never retained. <i>ausgefuehrt</i>: Renault accepted the command (or the same setpoint went out less than 60 s ago). <i>uebergeben</i>: the retrieval was started or the value stored. Vehicles 2 to 4: <span class='sm-mono'>Renault/befehl/&lt;n&gt;/&lt;name&gt;</span>.")
s('BEFEHL', 'M_SCHALTEN',
  'Befehlsbrücke %s: %s',
  'Command bridge %s: %s')
s('BEFEHL', 'SCHRITT',
  'Schritt 3: Befehle über MQTT',
  'Step 3: commands via MQTT')
s('BEFEHL', 'SCHRITT_TEXT',
  "Die Vorlage legt einen eigenen virtuellen Ausgang <i>Renault MQTT-Befehle</i> an (Adresse <span class='sm-mono'>/dev/udp/&lt;LoxBerry&gt;/11884</span>). Wirkt nur mit dem Haken <i>Befehle über MQTT annehmen</i> im Reiter MQTT. Im MQTT-Gateway V2 zusätzlich <span class='sm-mono'>Renault/status/befehle</span> (Noncached) anhaken.",
  "The template creates its own virtual output <i>Renault MQTT-Befehle</i> (address <span class='sm-mono'>/dev/udp/&lt;LoxBerry&gt;/11884</span>). Works only with the checkbox <i>Accept commands via MQTT</i> on the MQTT tab. In MQTT gateway V2 also tick <span class='sm-mono'>Renault/status/befehle</span> (Noncached).")
s('BEFEHL', 'K_VORLAGE',
  'Vorlage Befehle über MQTT',
  'Template commands via MQTT')
s('BEFEHL', 'K_AUFFRISCHEN',
  'Werte abfragen',
  'Fetch values')
s('BEFEHL', 'K_LADEN',
  'Laden 1 an / 0 aus',
  'Charging 1 on / 0 off')
s('BEFEHL', 'K_KLIMA_AN',
  'Vorklimatisierung ein',
  'Pre-conditioning on')
s('BEFEHL', 'K_KLIMA_AUS',
  'Vorklimatisierung aus',
  'Pre-conditioning off')
s('BEFEHL', 'K_LADEPLAN',
  'Ladeplan 1 an / 0 aus',
  'Charge schedule 1 on / 0 off')
s('BEFEHL', 'K_AUSSENTEMP',
  'Außentemperatur aus Loxone',
  'Outside temperature from Loxone')
s('BEFEHL', 'T_NICHT_DA',
  'Die Befehlsbrücke (bin/befehlsbruecke.php) fehlt oder lässt sich nicht laden – Plugin neu installieren.',
  'The command bridge (bin/befehlsbruecke.php) is missing or cannot be loaded – reinstall the plugin.')
s('BEFEHL', 'T_AUS',
  'aus (Haken „Befehle über MQTT annehmen“)',
  'off (checkbox “Accept commands via MQTT”)')
s('BEFEHL', 'T_DEFEKT',
  'Einrichtung fehlerhaft: %s',
  'Setup faulty: %s')
s('BEFEHL', 'T_LAEUFT',
  'läuft (%d Dienst), angenommen %d, abgelehnt %d.',
  'running (%d service), accepted %d, rejected %d.')
s('BEFEHL', 'T_LETZTER',
  'Letzter Befehl: %s – %s, vor %d s.',
  'Last command: %s – %s, %d s ago.')
s('BEFEHL', 'T_KEINER',
  'Noch kein Befehl seit dem Start.',
  'No command since the start.')
s('BEFEHL', 'T_STEHT',
  'soll laufen, steht aber (%s) – der Minutentakt startet sie neu (höchstens alle 10 min).',
  'should run but is stopped (%s) – the minute run restarts it (at most every 10 min).')

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
s('FELD', 'GPS_UNIX',
  'GPS-Zeit (Unix-Sekunden)',
  'GPS time (Unix seconds)')
s('FELD', 'FAHRZEUGZEIT',
  'Zeitstempel der Fahrzeugantwort (Unix-Sekunden)',
  'Timestamp of the vehicle response (Unix seconds)')
s('FELD', 'HVAC',
  'Klimatisierung (letzter Abruf)',
  'Climate control (last retrieval)')

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

t('L_HAUS_FAHRZEUG_EIN',
  'Sammelthemen haus/fahrzeug/… senden',
  'Send the collective topics haus/fahrzeug/…')
t('H_HAUS_FAHRZEUG',
  'Sammelthemen',
  'Collective topics')
t('H_HAUS_FAHRZEUG_EIN',
  "Ab Werk an. Ladestand, Reichweite, Kabel, lädt und zu Hause unter <span class='sm-mono'>haus/fahrzeug/&lt;name&gt;/…</span> (<span class='sm-mono'>soc</span>, <span class='sm-mono'>reichweite_km</span>, <span class='sm-mono'>kabel</span>, <span class='sm-mono'>laedt</span>, <span class='sm-mono'>zuhause</span> retained, ohne Aussage ein Strich; <span class='sm-mono'>zaehler</span> je Minute, nie retained), damit andere Plugins und Loxone ein Fahrzeug lesen können, gleich welcher Marke. Liefert Renault keine Fahrzeugdaten (zum Beispiel ohne Online-Abo), steht überall der Strich und nur der Zähler läuft. Kein Standort, keine Fahrgestellnummer. Ausschalten räumt die Themen ab.",
  "On by default. State of charge, range, cable, charging and at home under <span class='sm-mono'>haus/fahrzeug/&lt;name&gt;/…</span> (<span class='sm-mono'>soc</span>, <span class='sm-mono'>reichweite_km</span>, <span class='sm-mono'>kabel</span>, <span class='sm-mono'>laedt</span>, <span class='sm-mono'>zuhause</span> retained, a dash when there is no statement; <span class='sm-mono'>zaehler</span> every minute, never retained), so other plugins and Loxone can read a vehicle whatever its make. If Renault delivers no vehicle data (for example without an online subscription), every value is a dash and only the counter runs. No location, no VIN. Switching it off clears the topics.")
t('H_KABEL',
  'Kabel vergessen',
  'Cable forgotten')
t('KABEL_HILFE',
  'Meldet sich, wenn das Auto zu Hause steht, das Kabel nicht steckt und der Akku unter der Schwelle liegt: höchstens einmal je Standzeit und je Tag, nur mit einem Fahrzeugstand bis 12 Stunden. In der Nachtruhe wartet die Meldung. Braucht die Heimzone oben; unbekannte Werte warnen nie, ohne Fahrzeugdaten also nie. Der Haken für die Ansage steht bei den Anlässen der Sprachausgabe.',
  'Reports when the car stands at home, the cable is not plugged in and the battery is below the threshold: at most once per stay and per day, only with vehicle data up to 12 hours old. During the night rest the message waits. Needs the home zone above; unknown values never warn, so without vehicle data it never does. The tick for the announcement is among the occasions of the speech output.')
t('L_KABEL_SOC',
  'Warnen unter Akku (%)',
  'Warn below battery (%)')
t('L_KABEL_UHR',
  'Warnen ab Uhrzeit',
  'Warn from this time')
t('L_KABEL_ABFAHRT_MIN',
  'Auch warnen, wenn die Abfahrt in so vielen Minuten ansteht',
  'Also warn when departure is due within this many minutes')
t('H_KABEL_ABFAHRT_MIN',
  '0 = nicht. Wirkt nur mit dem Haken für die Minuten bis zur Abfahrt aus dem Haus-Thema.',
  '0 = no. Only works with the tick for the minutes until departure from the house topic.')
t('L_SIGNAL_KABEL',
  'Kabel vergessen über SignalBot melden',
  'Report a forgotten cable through SignalBot')
t('L_ANSAGE_KABEL',
  'Das Auto steht zu Hause ohne Kabel, der Akku ist niedrig',
  'The car is at home without a cable and the battery is low')
t('ANSAGE_S_KABEL',
  '%s steht ohne Ladekabel zu Hause, der Akku steht bei %s Prozent.',
  '%s is at home without a charging cable, the battery is at %s percent.')
t('L_VORKLIMA_MIN_SOC',
  'Vorklimatisierung nur ab Akku (%)',
  'Pre-conditioning only from battery (%)')
t('L_VORKLIMA_NUR_KABEL',
  'Vorklimatisierung nur mit gestecktem Kabel',
  'Pre-conditioning only with the cable plugged in')
t('H_VORKLIMA_GRENZEN',
  'Akku-Grenze 0 = keine Grenze. Darunter wird nicht gesendet, kein Versuch wird verbraucht (Vorklima = 5). Der Kabel-Haken ist ab Werk aus (Vorklima = 6). Sind die Werte unbekannt, klimatisiert das Plugin wie bisher, auch ohne Fahrzeugdaten.',
  'Battery limit 0 = no limit. Below it nothing is sent and no attempt is used up (Vorklima = 5). The cable tick is off by default (Vorklima = 6). If the values are unknown, the plugin pre-conditions as before, also without vehicle data.')
t('F_HAUS_FAHRZEUG',
  'Sammelthemen haus/fahrzeug',
  'Collective topics haus/fahrzeug')
t('A_HAUS_FAHRZEUG',
  'gesendet für: %s',
  'sent for: %s')
t('A_HAUS_FAHRZEUG_NOCH',
  'eingeschaltet, noch nichts gesendet (der Minutentakt sendet, sobald Konto und Fahrgestellnummer eingetragen sind)',
  'switched on, nothing sent yet (the minute run sends as soon as account and VIN are entered)')
t('A_HAUS_FAHRZEUG_AUS',
  'ausgeschaltet',
  'switched off')
t('A_HAUS_FAHRZEUG_FREMD',
  'Unter haus/fahrzeug/%s sendet auch eine andere Linie (fremder Zähler). Bitte einem der Fahrzeuge einen anderen Namen geben: Bis dahin überschreiben sich die Werte, und dieses Plugin räumt die Themen dort nicht ab.',
  'Under haus/fahrzeug/%s another plugin is sending too (foreign counter). Please give one of the vehicles a different name: until then the values overwrite each other, and this plugin does not clear the topics there.')
t('NICHT_GESPEICHERT', 'Nicht gespeichert:', 'Not saved:')
t('F_GEHEIM_NEU',
  'Eingetippte Kennwörter, Schlüssel und Sprechtoken werden nicht zurückgegeben: Die markierten Felder bitte erneut ausfüllen.',
  'Typed passwords, keys and speech tokens are not handed back: please fill in the marked fields again.')
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
  'Grundlage des Diagramms im Reiter Ladehistorie. Eine Zeile entsteht, wenn sich der Stand des Fahrzeugs ändert (Zeitstempel, Kilometer, Ladestand, Reichweite, Kabel, Ladestatus).',
  'Basis of the chart on the charge history tab. A line is written when the state of the vehicle changes (timestamp, mileage, charge level, range, cable, charging status).')

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
t('H_ABRP',
  'Beide Felder müssen gefüllt sein, sonst wird nichts gesendet. Gilt nur für Fahrzeug 1.',
  'Both fields must be filled in, otherwise nothing is sent. Applies to vehicle 1 only.')

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
t('M_GESPEICHERT',
  'Gespeichert.',
  'Saved.')
t('M_TOKEN_NEU',
  'Neues Token erzeugt. <b>Die Adressen in Loxone müssen angepasst werden</b> – die alten '
  'funktionieren nicht mehr.',
  'New token generated. <b>The addresses in Loxone must be updated</b> – the old ones no longer work.')
t('M_LOG_LEER', 'Das Protokoll wurde geleert.', 'The log has been cleared.')
t('M_CACHE_LEER', 'Zwischenspeicher und Anmeldung wurden verworfen. Der nächste Abruf meldet sich neu an.',
  'Cache and login have been discarded. The next retrieval will log in again.')
t('NICHT_GELUNGEN', "Der Vorgang ist nicht gelungen:", "The operation did not succeed:")
t('F_LOG_LEEREN', "Das Protokoll ließ sich nicht vollständig leeren; es stehen noch: <span class='sm-mono'>%s</span>.", "The log could not be cleared completely; still present: <span class='sm-mono'>%s</span>.")
t('F_CACHE_LEEREN', "Zwischenspeicher und Anmeldung ließen sich nicht vollständig verwerfen; es stehen noch: <span class='sm-mono'>%s</span>.", "Cache and login could not be discarded completely; still present: <span class='sm-mono'>%s</span>.")
t('F_EXEC', "Das Feld <b>%s</b> enthält Sonderzeichen der Schale (; &amp; | ` $ ( ) &lt; &gt;) — so würde der Befehl nie ausgeführt. Erlaubt ist ein Programm mit einfachen Argumenten.", "The field <b>%s</b> contains shell special characters (; &amp; | ` $ ( ) &lt; &gt;) — the command would never be run like this. Allowed is a program with plain arguments.")
t('F_WERT_ALLG', "Unzulässiger Wert für die Einstellung <span class='sm-mono'>%s</span> — so ließe sich die eigene Sicherung nicht zurückspielen.", "Invalid value for the setting <span class='sm-mono'>%s</span> — the plugin's own backup could not be restored like this.")
t('F_LOESCHEN_WIDERSPRUCH', "%s: ein neuer Wert ist eingetragen und zugleich „löschen“ angehakt — bitte nur eines von beiden.", "%s: a new value is entered and “delete” is ticked at the same time — please choose one.")
t('L_PASSWORT_LOESCHEN', "Gespeichertes Passwort löschen", "Delete stored password")
t('L_SCHLUESSEL_LOESCHEN', "Gespeicherten Schlüssel löschen", "Delete stored key")
t('H_GEHEIM', "Der gespeicherte Wert wird nie angezeigt. Ein leeres Feld lässt ihn unverändert.", "The stored value is never shown. An empty field leaves it unchanged.")
t('SICH_TOKEN_BEHALTEN', "Die Sicherung trägt kein Aktionstoken; das geltende Token bleibt, und die Adressen in Loxone gelten weiter.", "The backup carries no action token; the current token stays, and the addresses in Loxone remain valid.")
t('SICH_NICHT_WIRKSAM', "Die Sicherung wurde geschrieben, beim Zurücklesen stehen aber andere Werte da (<span class='sm-mono'>%s</span>) — das Zurückspielen ist NICHT wirksam geworden. Bitte das Protokoll ansehen.", "The backup was written, but reading it back shows different values (<span class='sm-mono'>%s</span>) — the restore did NOT take effect. Please check the log.")
t('M_MQTT_ALTNAME_LEER', "MQTT: unter <span class='sm-mono'>%s</span> (umbenanntes oder entferntes Fahrzeug) stand nichts zurückbehalten — der Broker bestätigt es.", "MQTT: nothing was retained under <span class='sm-mono'>%s</span> (renamed or removed vehicle) — confirmed by the broker.")
t('M_MQTT_ALTNAME_GELOESCHT', "MQTT: %d zurückbehaltene Themen unter <span class='sm-mono'>%s</span> (umbenanntes oder entferntes Fahrzeug) sind gelöscht — der Broker bestätigt es.", "MQTT: %d retained topics under <span class='sm-mono'>%s</span> (renamed or removed vehicle) have been deleted — confirmed by the broker.")
t('F_MQTT_ALTNAME_OFFEN', "MQTT: unter <span class='sm-mono'>%s</span> stehen nach dem Löschen noch %d zurückbehaltene Themen (%s). Von Hand: LoxBerry → System → MQTT Gateway.", "MQTT: under <span class='sm-mono'>%s</span>, %d retained topics are still present after deleting (%s). By hand: LoxBerry → System → MQTT Gateway.")
t('F_MQTT_ALTNAME_BROKER', "MQTT: der Broker war nicht zu befragen — die zurückbehaltenen Themen unter <span class='sm-mono'>%s</span> (umbenanntes oder entferntes Fahrzeug) sind NICHT gelöscht. Von Hand: LoxBerry → System → MQTT Gateway.", "MQTT: the broker could not be queried — the retained topics under <span class='sm-mono'>%s</span> (renamed or removed vehicle) have NOT been deleted. By hand: LoxBerry → System → MQTT Gateway.")
t('H_ADRESSE_PRUEFEN', "Der Rechnername <span class='sm-mono'>%s</span> stammt aus der Adresse, unter der Sie diese Seite geöffnet haben. Erreicht der Miniserver den LoxBerry unter einem anderen Namen oder einer IP-Adresse, tragen Sie diese ein.", "The host name <span class='sm-mono'>%s</span> comes from the address under which you opened this page. If the Miniserver reaches the LoxBerry under another name or an IP address, enter that one.")

# --- Reiter MQTT
t('H_GATEWAY', 'Zustand des MQTT-Gateways', 'State of the MQTT gateway')
t('H_GATEWAY_TEXT', 'Das MQTT-Gateway ist seit LoxBerry 3 <b>Bestandteil des Systems</b> und kein Plugin. Es wird unter <i>System → MQTT Gateway</i> eingerichtet.', 'Since LoxBerry 3 the MQTT gateway is <b>part of the system</b> and not a plugin. It is configured under <i>System → MQTT Gateway</i>.')
t('H_KEIN_BROKER', "In <span class='sm-mono'>config/system/general.json</span> steht kein Broker. Das Plugin kann seine Werte nirgends hinschicken. Unter <i>System → MQTT Gateway</i> einrichten.", "There is no broker in <span class='sm-mono'>config/system/general.json</span>. The plugin has nowhere to send its values. Configure it under <i>System → MQTT Gateway</i>.")
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
t('H_ABO',
  'Gateway V2: Datenpunkte anhaken',
  'Gateway V2: tick the data points')
t('H_ABO_PFLICHT', 'Ohne diesen Eintrag kommt am Miniserver nichts an. Die Zeile gehört unter <i>System → MQTT Gateway</i> in den Abschnitt <i>Subscriptions</i>; danach speichern.', 'Without this entry nothing arrives at the Miniserver. The line belongs under <i>System → MQTT Gateway</i> in the <i>Subscriptions</i> section; save afterwards.')
t('H_ABO_WO',
  'Abo für Gateway V1 (Rückfall):',
  'Subscription for gateway V1 (fallback):')
t('H_THEMEN', 'Veröffentlichte Themen', 'Published topics')
# Seit Renault NG 2.1.11: "ok" ist keine Aussage ueber das Fahrzeug, sondern
# ueber den letzten Abruf des Plugins und geht nicht mehr retained hinaus
# (Regeln/07 Abschnitt 3, 18./19.09.2026); der Satz nannte es bis dahin unter
# den Zustaenden.
t("H_THEMEN_TEXT", "<b>Zustände</b> des Fahrzeugs (Ladestatus, Kabel, Lademodus, Klimatisierung, Name, Kilometerstand) gehen <b>retained</b> hinaus — ein neu verbundener Teilnehmer bekommt sofort den letzten Stand. <b>Messwerte</b>, das <b>Lebenszeichen</b> und <b>ok</b> (ob der letzte Abruf des Plugins gelang) gehen ohne Retain hinaus, damit kein alter Wert als frisch erscheint und ein angehaltenes Plugin nicht in Ordnung meldet; ein leerer Wert geht nie retained. Was frühere Fassungen zurückbehalten haben, räumt das Plugin einmal ab. Die Spalte <i>retained</i> kommt aus derselben Tabelle, nach der gesendet wird. Diese Liste wird im Reiter Test gegen den Programmcode geprüft; bis 2.0.6 nannte sie fünf Themen, die es nie gab.",
  "<b>States</b> of the vehicle (charging status, cable, charge mode, climate control, name, mileage) are sent <b>retained</b> — a newly connected subscriber immediately receives the last known state. <b>Measurements</b>, the <b>heartbeat</b> and <b>ok</b> (whether the last fetch of the plugin succeeded) are sent without retain, so that no old value appears fresh and a stopped plugin does not report ok; an empty value is never retained. Values that earlier versions retained are cleared once by the plugin. The <i>retained</i> column comes from the same table the plugin sends by. This list is checked against the program code on the Test tab; until 2.0.6 it named five topics that never existed.")
t('S_PHASE', 'Phase %s', 'phase %s')
t('S_THEMA', 'Thema', 'Topic')
t('S_BEDEUTUNG', 'Bedeutung', 'Meaning')

# --- Reiter Einbindung in Loxone
t('H_LOXONE', 'Einbindung in Loxone, Schritt für Schritt', 'Loxone integration, step by step')
t('H_LOXONE_TEXT',
  'Das Plugin holt die Fahrzeugdaten von Renault und legt sie im MQTT-Broker ab. Loxone liest sie über das MQTT-Gateway V2 (Datenpunkte anhaken). Befehle schickt Loxone seit 2.1.20 über die Befehlsbrücke (UDP an das Gateway); der bisherige HTTP-Endpunkt bleibt eingeklappt erhalten.',
  'The plugin fetches the vehicle data from Renault and publishes it to the MQTT broker. Loxone reads it via MQTT gateway V2 (tick the data points). Since 2.1.20 Loxone sends commands via the command bridge (UDP to the gateway); the previous HTTP endpoint is kept, collapsed.')
t('SCHRITT1', 'Schritt 1: Weg festlegen', 'Step 1: choose the path')
t('SCHRITT1_TEXT',
  '<b>MQTT ist der Regelweg</b> für alle Messwerte (Gateway V2, Schritt 2) und für die Befehle (Befehlsbrücke, Schritt 3). Der bisherige HTTP-Endpunkt steht eingeklappt darunter; neue Anlagen brauchen ihn nicht.',
  '<b>MQTT is the standard path</b> for all measured values (gateway V2, step 2) and for commands (command bridge, step 3). The previous HTTP endpoint is collapsed below; new installations do not need it.')
t('SCHRITT2',
  'Schritt 2: Gateway V2 – Datenpunkte anhaken',
  'Step 2: gateway V2 – tick the data points')
t('SCHRITT3',
  'Zu Schritt 2: die Namen der virtuellen Eingänge',
  'For step 2: the names of the virtual inputs')
t("SCHRITT3_TEXT", "Das MQTT-Gateway legt die Eingänge selbst an, sobald der erste Wert ankommt. Der Titel ist das Thema mit Unterstrich statt Schrägstrich und darf nicht geändert werden — sonst entsteht beim nächsten Wert ein zweiter Eingang. Den lesbaren Namen setzen Sie in Loxone Config aus der Spalte <i>Bedeutung</i>. Eine Importdatei für die Eingänge gibt es seit 2.1.9 nicht mehr; wer sie früher eingelesen hat, behält seine Eingänge, und sie bekommen weiter Werte. Fünf Themen tragen Text statt einer Zahl: <span class='sm-mono'>Name</span>, <span class='sm-mono'>HvAcStatus</span> (<span class='sm-mono'>on</span>/<span class='sm-mono'>off</span>), <span class='sm-mono'>ChargeMode</span>, <span class='sm-mono'>GPSTime</span> (Uhrzeit als <span class='sm-mono'>HH:MM</span>) und <span class='sm-mono'>chargeEndStatus</span> (Abschlussmeldung der Renault-Schnittstelle); sie gehören an einen virtuellen Texteingang — für die Klimatisierung gibt es <span class='sm-mono'>HvAcStatusBin</span> als Zahl. <span class='sm-mono'>HvAcStatus</span> und <span class='sm-mono'>ChargeMode</span> lauten <span class='sm-mono'>n/a</span>, wenn das Fahrzeug die Abfrage nicht kennt. Ein Zustand ohne Wert steht als <span class='sm-mono'>-</span> da; ein Messwert ohne Wert wird nicht gesendet, der Eingang behält dann seinen letzten Wert.",
  "The MQTT gateway creates the inputs itself as soon as the first value arrives. The title is the topic with underscores instead of slashes and must not be changed — otherwise the next value creates a second input. Set the readable name in Loxone Config from the <i>Meaning</i> column. Since 2.1.9 there is no import file for the inputs any more; anyone who imported it earlier keeps those inputs, and they keep receiving values. Five topics carry text instead of a number: <span class='sm-mono'>Name</span>, <span class='sm-mono'>HvAcStatus</span> (<span class='sm-mono'>on</span>/<span class='sm-mono'>off</span>), <span class='sm-mono'>ChargeMode</span>, <span class='sm-mono'>GPSTime</span> (time as <span class='sm-mono'>HH:MM</span>) and <span class='sm-mono'>chargeEndStatus</span> (final status reported by the Renault interface); they belong on a virtual text input — for climate control there is <span class='sm-mono'>HvAcStatusBin</span> as a number. <span class='sm-mono'>HvAcStatus</span> and <span class='sm-mono'>ChargeMode</span> read <span class='sm-mono'>n/a</span> if the vehicle does not know the query. A state without a value reads <span class='sm-mono'>-</span>; a measured value without a value is not sent, and the input keeps its last value.")
t('S_TITEL', 'Titel', 'Title')
t('S_EINHEIT', 'Einheit', 'Unit')
t("H_VORLAGE", "Importdatei für die Befehle",
  "Import file for the commands")
t('H_VORLAGE_TEXT',
  'Diese Datei legt die Befehle aus Schritt 4 als virtuelle Ausgänge an, samt Aktionstoken. <b>Achtung:</b> Loxone Config legt beim Import neu an und überschreibt nichts — zweimal eingelesen ergibt doppelte Bausteine. Die Adresse im Kopf ist ein Vorschlag; bitte prüfen, unter welchem Namen der Miniserver den LoxBerry erreicht. Die Befehlstitel sind seit 2.1.19 fest deutsch (wie im Musterprojekt), auch bei englischer Oberfläche; nur die Kommentare sind übersetzt.',
  'This file creates the commands from step 4 as virtual outputs, including the action token. <b>Note:</b> Loxone Config creates new objects on import and overwrites nothing — importing twice results in duplicate blocks. The address in the header is a suggestion; please check under which name the Miniserver reaches the LoxBerry. Since 2.1.19 the command titles are fixed German (as in the sample project), also with an English interface; only the comments are translated.')
t('K_VORLAGE_VQ', 'Importdatei für die Befehle erzeugen', 'Create import file for the commands')
t('SCHRITT4',
  'Befehle über den HTTP-Endpunkt (bisheriger Weg)',
  'Commands via the HTTP endpoint (previous path)')
t('SCHRITT4_TEXT',
  "Je Befehl ein <b>virtueller Ausgang Befehl</b>. Die Adresse des virtuellen Ausgangs ist <span class='sm-mono'>%s</span>, im Befehl bei EIN steht dann:",
  "One <b>virtual output command</b> per command. The address of the virtual output is <span class='sm-mono'>%s</span>, and the command on ON is then:")
t('SCHRITT4_ENDPUNKT',
  "Der Endpunkt liegt im unangemeldeten Bereich und ist durch das Token geschützt. Der Selbsttest in der letzten Zeile beantwortet, ob das in Loxone eingetragene Token noch stimmt — <b>ohne am Fahrzeug etwas zu schalten</b>. Antwort bei richtigem Token: <span class='sm-mono'>SELFTEST;OK=1;TOKEN=OK</span>. Derselbe Schaltbefehl für dasselbe Fahrzeug geht innerhalb von 60 Sekunden nur einmal an Renault; eine Wiederholung antwortet mit HTTP 200 und <span class='sm-mono'>UNVERAENDERT=1</span>, ein anderer Befehl geht sofort hinaus.",
  "The endpoint is in the unauthenticated area and is protected by the token. The self-test in the last row answers whether the token entered in Loxone is still valid — <b>without switching anything on the vehicle</b>. Response with a valid token: <span class='sm-mono'>SELFTEST;OK=1;TOKEN=OK</span>. The same switching command for the same vehicle is sent to Renault only once within 60 seconds; a repetition answers HTTP 200 with <span class='sm-mono'>UNVERAENDERT=1</span>, a different command goes out at once.")
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
t('SCHRITT5',
  'Schritt 4: Ausfallerkennung',
  'Step 4: failure detection')
t('SCHRITT5_TEXT',
  "Schweigt Renault oder steht der LoxBerry, behalten die virtuellen Eingänge ihren letzten Wert — in der App sieht dann alles normal aus. Deshalb zwei Zeichen mitführen (Seite „Renault NG“ in Schritt 6): Das <b>Lebenszeichen</b> <span class='sm-mono'>status/zaehler</span> zählt bei jedem Durchgang des Plugins (alle 3 Minuten) eins weiter, auch ohne Abruf; eine Analogwertvalidierung (Tmc 900 s) meldet, wenn es steht – dann steht der LoxBerry, das MQTT-Gateway oder die Anmeldung bei Renault (seit 2.1.20 gehen bei einem Anmeldefehler je Fahrzeug ok = 0 und das Lebenszeichen hinaus). <span class='sm-mono'>ok</span> geht bei einem gescheiterten Abruf auf 0. <span class='sm-mono'>phpCall</span> zeigt nur die Uhrzeit des letzten erfolgreichen Abrufs. Bis 2.1.18 nannte dieser Schritt <span class='sm-mono'>ok</span> und <span class='sm-mono'>phpCall</span> mit einem Treppenlichtschalter – der stand im Normalbetrieb auf Ein und erkannte keinen Ausfall.",
  "If Renault goes silent or the LoxBerry stands still, the virtual inputs keep their last value — in the app everything then looks normal. Therefore carry two signs (page “Renault NG” in step 6): the <b>heartbeat</b> <span class='sm-mono'>status/zaehler</span> counts up by one with every run of the plugin (every 3 minutes), even without a retrieval; a Value Validator (Tmc 900 s) reports when it stops – then the LoxBerry, the MQTT gateway or the login at Renault is stuck (since 2.1.20 a login error sends ok = 0 and the heartbeat per vehicle). <span class='sm-mono'>ok</span> goes to 0 on a failed retrieval. <span class='sm-mono'>phpCall</span> only shows the time of the last successful retrieval. Until 2.1.18 this step named <span class='sm-mono'>ok</span> and <span class='sm-mono'>phpCall</span> with a stairwell light switch – it was on in normal operation and did not detect a failure.")
t('SCHRITT6',
  'Schritt 5: Drei Seiten aus dem Musterprojekt zum Nachbauen',
  'Step 5: three pages from the sample project to rebuild')
t('SCHRITT6_TEXT',
  'Drei Seiten aus dem LoxBerry-Plugins Musterprojekt, dort in Loxone Config gebaut und verbunden. Jede Zeile ein Baustein; Loxone Config findet alle über die Baustein-Suche (Taste F5). Wer nur überwachen will, übernimmt die erste Seite allein; „Laden und Klima“ braucht die freigegebene Steuerung, „Fahrzeug“ ist reine Anzeige. Die Tabellen gelten für Fahrzeug 1: Die Namen der Gateway-Eingänge sind aus dem eingestellten Fahrzeugnamen gerechnet (Renault_<i>Fahrzeugname</i>_<i>Thema</i>, wie in Schritt 3), die Befehlstitel sind fest deutsch, auch bei englischer Oberfläche.',
  'Three pages from the LoxBerry plugins sample project, built and connected there in Loxone Config. One block per row; Loxone Config finds them all via the block search (key F5). If you only want monitoring, take over the first page alone; “Laden und Klima” needs switching to be enabled, “Fahrzeug” is display only. The tables apply to vehicle 1: the names of the gateway inputs are worked out from the configured vehicle name (Renault_<i>vehiclename</i>_<i>topic</i>, as in step 3), the command titles are fixed German, also with an English interface.')
t('S_BAUSTEIN', 'Baustein (Typ)', 'Block (type)')
# Welle Bild 17 (2.1.19): Spaltenkopf "Name" statt "Name (Vorschlag)" - fuer die Gateway-Eingaenge ist der
# Name Pflicht (Entwurf Welle 17 rn, B1).
t('S_NAME',
  'Name',
  'Name')
t('S_PARAMETER', 'Parameter', 'Parameter')
t('S_EINGAENGE', 'Eingänge verbinden mit', 'Connect inputs to')
# Welle Bild 17 (2.1.19): Bild je Musterseite und Link aufs Musterprojekt; die alte Liste (B_*, P_*,
# S_VON_VISU, ZU_9) ist mit den drei Seiten in [BAUSTEIN] entfallen.
t('BILD_ALT',
  'Bausteine des Plugins in Loxone Config',
  'Plugin blocks in Loxone Config')
t('BILD_UNTERSCHRIFT',
  'Seite „%s“ im LoxBerry-Plugins Musterprojekt. Config kürzt lange Bausteinnamen – Namen siehe Tabelle.',
  'Page “%s” in the LoxBerry plugins sample project. Config shortens long block names – see the table for the full names.')
t('MUSTERPROJEKT',
  "Die ganze Projektdatei mit allen Plugin-Seiten und Vorlagen: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry-Plugins Musterprojekt</a>",
  "The complete project file with all plugin pages and templates: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry plugins sample project</a>")
t('ZU_10',
  'Zu allen Benachrichtigungen:',
  'On all notifications:')
t('ZU_10_TEXT',
  'Der Benachrichtigungs-Baustein sendet nur beim Wechsel von Aus auf Ein. <b>Niemals mehrere Quellen '
  'direkt an seinen Eingang</b> — erst über ODER zusammenführen, sonst verschluckt eine dauerhaft '
  'aktive Quelle alle übrigen.',
  'The notification block only sends on a transition from off to on. <b>Never connect several sources '
  'directly to its input</b> — merge them through an OR first, otherwise a permanently active source '
  'swallows all the others.')
t('SCHRITT7',
  'Schritt 6: Gegenprobe',
  'Step 6: cross-check')
t('SCHRITT7_TEXT',
  "Im Reiter Test den Knopf <i>Daten sofort neu abrufen</i> drücken oder in Loxone <i>Renault Werte abfragen (MQTT)</i> auslösen, danach in Loxone Config die virtuellen Eingänge ansehen. Die Quittung jedes Befehls steht unter <span class='sm-mono'>Renault/befehl/&lt;name&gt;/quittung</span>.",
  "On the Test tab press <i>Fetch data now</i> or trigger <i>Renault Werte abfragen (MQTT)</i> in Loxone, then look at the virtual inputs in Loxone Config. The acknowledgement of each command is under <span class='sm-mono'>Renault/befehl/&lt;name&gt;/quittung</span>.")

# --- Reiter Test
t('H_SELBSTPRUEFUNG', 'Selbstprüfung', 'Self-check')
t('S_FRAGE', 'Frage', 'Question')
t('S_ANTWORT', 'Antwort', 'Answer')
t('H_NACHSEHEN', 'Nachsehen', 'Inspect')
t('K_UMGEBUNG', 'Umgebung prüfen', 'Check environment')
t('K_KONFIG', 'Gespeicherte Konfiguration', 'Stored configuration')
t('K_ZWISCHEN', 'Zwischengespeicherte Daten', 'Cached data')
t('K_THEMEN', 'Themen abgleichen', 'Compare topics')
t("K_VORLAGE_PRUEFEN", "Importdatei prüfen",
  "Check import file")
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
  "Ist die Aufzeichnung im Reiter <i>Einstellungen</i> eingeschaltet, entsteht eine Zeile in <span class='sm-mono'>database.csv</span>, wenn sich der Stand des Fahrzeugs ändert (Zeitstempel, Kilometer, Ladestand, Reichweite, Kabel, Ladestatus) — seit 2.1.20 nicht mehr bei jedem Abruf. Das Diagramm zeigt die letzten 24 Stunden nach den Zeitstempeln. Beim Update rettet <span class='sm-mono'>preupgrade.sh</span> die Datei daneben und holt sie danach zurück; das Update auf 2.1.20 fasst alte gleiche Zeilen einmal zusammen (die alte Datei liegt als <span class='sm-mono'>database.csv.vor_2120</span> daneben).",
  "If recording is enabled on the <i>Settings</i> tab, a line is written to <span class='sm-mono'>database.csv</span> when the state of the vehicle changes (timestamp, mileage, charge level, range, cable, charging status) — since 2.1.20 no longer on every retrieval. The chart shows the last 24 hours by timestamp. On an update <span class='sm-mono'>preupgrade.sh</span> rescues the file next to its folder and puts it back afterwards; the update to 2.1.20 merges old identical lines once (the old file stays as <span class='sm-mono'>database.csv.vor_2120</span>).")
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

# ---- NACHGEPFLEGT 31.08.2026: standen in der .ini und im PHP,
#      aber nicht mehr hier. Dieser Erzeuger verweigert NICHT -
#      ein Lauf haette sie kommentarlos geloescht. Darunter die
#      Sicherung und die drei Gateway-Texte.
t('ABO_GEMESSEN', '(gemessen: Gateway&nbsp;V%d)', '(measured: gateway&nbsp;V%d)')
t('ABO_UNBEKANNT', 'Welche Fassung Ihr MQTT&#8209;Gateway hat, ließ sich nicht feststellen. <b>Fassung&nbsp;1:</b> ohne diesen Eintrag kommt am Miniserver nichts an. <b>Fassung&nbsp;2 und neuer:</b> die Themengruppe erscheint von selbst in den Subscriptions, einzutragen ist nichts.', 'The version of your MQTT gateway could not be determined. <b>Version&nbsp;1:</b> without this entry nothing arrives at the Miniserver. <b>Version&nbsp;2 and newer:</b> the topic group appears by itself under Subscriptions, nothing needs to be entered.')
t('ABO_V2',
  '<b>Diese Datenpunkte im MQTT&#8209;Gateway V2 anhaken</b> (<i>System → MQTT Gateway → Subscriptions</i>), die mit Noncached als Noncached. Die Tabelle nennt jeden Namen, den das Gateway vergibt.',
  '<b>Tick these data points in MQTT gateway V2</b> (<i>System → MQTT Gateway → Subscriptions</i>), the Noncached ones as Noncached. The table names every name the gateway assigns.')
t('H_SICHERUNG', 'Einstellungen sichern und zurückspielen', 'Back up and restore settings')
t('K_SICHERN', 'Einstellungen sichern', 'Back up settings')
t('K_ZURUECK', 'Zurückspielen', 'Restore')
t('SICH_ABGELEHNT', 'Die Datei wurde <b>nicht</b> übernommen — es ist nichts geändert worden:', 'The file was <b>not</b> accepted — nothing has been changed:')
t('SICH_ERKLAERUNG', 'Für den <b>Umzug auf einen zweiten LoxBerry</b>: die Datei enthält alle Einstellungen dieses Plugins und lässt sich dort wieder einspielen.', 'For <b>moving to a second LoxBerry</b>: the file contains all settings of this plugin and can be restored there.')
t('SICH_FREMD', 'Unbekannte Einstellung in der Datei: %s', 'Unknown setting in the file: %s')
t('SICH_KEINE_DATEI', 'Es wurde keine Datei ausgewählt oder der Upload ist fehlgeschlagen.', 'No file was selected, or the upload failed.')
t('SICH_KEIN_JSON', 'Die Datei ist keine gültige Sicherung dieses Plugins.', 'The file is not a valid backup of this plugin.')
t('SICH_LEER', 'Die Datei enthält keine bekannte Einstellung.', 'The file contains no known setting.')
t('SICH_SCHREIBFEHLER', 'Die Einstellungen ließen sich nicht schreiben.', 'The settings could not be written.')
t('SICH_UEBERNOMMEN', 'Einstellungen zurückgespielt: %d Werte übernommen.', 'Settings restored: %d values taken over.')
t('SICH_WARNUNG', '<b>Die Datei enthält Ihre Zugangsdaten.</b> Ohne sie stünden nach dem Zurückspielen alle Felder richtig, und das Plugin käme trotzdem nicht an die Anlage. Behandeln Sie die Datei wie ein Passwort: nicht in ein Forum hängen und nicht an einen Fehlerbericht heften.', '<b>The file contains your credentials.</b> Without them all fields would look right after restoring and the plugin still would not reach the installation. Treat the file like a password: do not post it in a forum and do not attach it to a bug report.')
t('SICH_ZU_GROSS', 'Die Datei ist größer als erlaubt — eine Sicherung dieses Plugins ist wenige Kilobyte groß.', 'The file is larger than allowed — a backup of this plugin is a few kilobytes.')


# ---- Nachgetragen 20.09.2026 aus den ausgelieferten .ini ------------------
# Diese Schluessel standen nur dort; der Erzeuger wies deshalb jeden Lauf ab.
# Neue Werte in doppelten Anfuehrungszeichen: sie enthalten Apostrophe.
s("CSV", "AUSSEN", "Außentemperatur",
  "Outside temperature")
s("CSV", "DATUM", "Datum",
  "Date")
s("CSV", "GPSBREITE", "GPS-Breite",
  "GPS latitude")
s("CSV", "GPSDATUM", "GPS-Datum",
  "GPS date")
s("CSV", "GPSLAENGE", "GPS-Länge",
  "GPS longitude")
s("CSV", "GPSZEIT", "GPS-Zeit",
  "GPS time")
s("CSV", "KABEL", "Kabelstatus",
  "Cable status")
s("CSV", "KAPAZITAET", "Batteriekapazität",
  "Battery capacity")
s("CSV", "KM", "Kilometerstand",
  "Mileage")
s("CSV", "LADELEISTUNG", "Ladeleistung",
  "Charging speed")
s("CSV", "LADEMODUS", "Lademodus",
  "Charging schedule")
s("CSV", "LADESTATUS", "Ladestatus",
  "Charging status")
s("CSV", "REICHWEITE", "Reichweite",
  "Range")
s("CSV", "RESTZEIT", "Restladezeit",
  "Remaining charging time")
s("CSV", "SOC", "Batteriestand",
  "Battery level")
s("CSV", "WETTER", "Wetterlage",
  "Weather condition")
s("CSV", "ZEIT", "Uhrzeit",
  "Time")
s("PRUEF", "ABO_DATEI", "Bringt das Plugin sein Gateway-Abonnement mit?",
  "Does the plugin bring its gateway subscription?")
s("PRUEF", "ABO_DATEI_FEHLT", "nein — %s fehlt oder nennt Renault/# nicht; Plugin neu installieren oder das Thema im Gateway von Hand eintragen",
  "no — %s is missing or does not name Renault/#; reinstall the plugin or enter the topic in the gateway by hand")
s("PRUEF", "ABO_DATEI_OK", "ja — %s, das Gateway liest es selbst",
  "yes — %s, the gateway reads it by itself")
s('PRUEF', 'CRON',
  'Sind die Cron-Einträge da?',
  'Are the cron entries in place?')
s("PRUEF", "CRON_FEHLT", "es fehlen: %s",
  "missing: %s")
s("PRUEF", "ENDPUNKT", "Antwortet der eigene Endpunkt?",
  "Does our own endpoint answer?")
s("PRUEF", "EP_FALSCH", "HTTP %d — Antwort: %s",
  "HTTP %d — answer: %s")
s("PRUEF", "EP_KEINE_ANTWORT", "keine Antwort. Ein Webserver, der nur eine Anfrage zugleich bearbeitet, kann sich während des Seitenaufbaus nicht selbst aufrufen — im Prüfaufbau ist das der Normalfall.",
  "no answer. A web server that handles one request at a time cannot call itself while building the page — in a test setup this is the normal case.")
s("PRUEF", "EP_KEIN_TOKEN", "kein Aktionstoken eingerichtet — nichts zu fragen",
  "no action token set up — nothing to ask")
s("PRUEF", "EP_NICHT_MESSBAR", "nicht feststellbar — weder curl noch allow_url_fopen vorhanden",
  "not determinable — neither curl nor allow_url_fopen available")
s("PRUEF", "EP_NUR_IM_REITER", "wird nur gemessen, wenn dieser Reiter der offene ist",
  "only measured when this tab is the open one")
s("PRUEF", "EP_OK", "ja, HTTP 200 mit der erwarteten Kennung",
  "yes, HTTP 200 with the expected marker")
s("PRUEF", "FEHLENDE_SCHLUESSEL", "%d von %d — es fehlen: %s (gelesen wird die Vorgabe)",
  "%d of %d — missing: %s (the default is used)")
s("PRUEF", "FORMULARE", "Tragen alle Formulare das Merkmal gegen fremde Absender?",
  "Do all forms carry the marker against foreign senders?")
s("PRUEF", "IST_ORDNER", "ist ein Verzeichnis, keine Datei",
  "is a directory, not a file")
s("PRUEF", "LAGE", "Ist die Konfiguration heil?",
  "Is the configuration intact?")
s("PRUEF", "LAGE_ABGESCHNITTEN", "beschädigt — die Datei bricht mitten in einem Wert ab",
  "damaged — the file breaks off inside a value")
s("PRUEF", "LAGE_AUS_DER_ZWEITSCHRIFT", "aus der Zweitschrift wiederhergestellt — bitte die Einstellungen nachsehen",
  "restored from the second copy — please check your settings")
s("PRUEF", "LAGE_FEHLT", "noch keine vorhanden — sie entsteht beim ersten Speichern",
  "none yet — it is created on the first save")
s("PRUEF", "LAGE_KAPUTT", "beschädigt — es stand keine bekannte Einstellung darin",
  "damaged — it contained no known setting")
s("PRUEF", "LAGE_KAPUTT_OHNE_ZWEITSCHRIFT", "beschädigt, und es gab keine brauchbare Zweitschrift",
  "damaged, and there was no usable second copy")
s("PRUEF", "LAGE_NICHT_GELESEN", "nicht gelesen",
  "not read")
s("PRUEF", "LAGE_OHNE_TOKEN", "gelesen, aber ohne Aktionstoken",
  "read, but without an action token")
s("PRUEF", "LAGE_OK", "ja, gelesen und vollständig",
  "yes, read and complete")
s("PRUEF", "LAGE_UNLESBAR", "die Datei ist nicht lesbar (Rechte?)",
  "the file cannot be read (permissions?)")
s("PRUEF", "MASKIERUNG_OK_N", "keine doppelte Maskierung, %d Aufrufstellen geprüft",
  "no double escaping, %d call sites checked")
s("PRUEF", "N_STELLEN", "%d Stelle(n) im Quelltext",
  "%d place(s) in the source")
s("PRUEF", "N_VON_N", "%d von %d",
  "%d of %d")
s("PRUEF", "SMACTIVE", "Setzt der Server den offenen Reiter, nicht erst das JavaScript?",
  "Does the server set the open tab, rather than the JavaScript alone?")
s("PRUEF", "VOLLSTAENDIG", "Ist die Konfiguration vollständig?",
  "Is the configuration complete?")
s("PRUEFTEXT", "ABO", "Einzutragendes Abo",
  "Subscription to enter")
s("PRUEFTEXT", "ABRPTOKEN", "ABRP-Token",
  "ABRP token")
s("PRUEFTEXT", "AKTIONSTOKEN", "Aktionstoken",
  "Action token")
s("PRUEFTEXT", "ANMELDUNG", "Anmeldung",
  "Login")
s("PRUEFTEXT", "AUFZEICHNUNG", "Aufzeichnung",
  "Recording")
s("PRUEFTEXT", "AUS_VORGABE", "aus (Vorgabe)",
  "off (default)")
s("PRUEFTEXT", "BENUTZER", "Benutzer",
  "User")
s("PRUEFTEXT", "BESCHREIBBAR", "beschreibbar",
  "writable")
s("PRUEFTEXT", "DATENORDNER", "Datenordner",
  "Data folder")
s("PRUEFTEXT", "DATUM", "Datum",
  "Date")
s("PRUEFTEXT", "DA_KB", "vorhanden (%s kB)",
  "present (%s kB)")
s("PRUEFTEXT", "DA_KB_RECHTE", "vorhanden (%s kB, Rechte %s)",
  "present (%s kB, permissions %s)")
s("PRUEFTEXT", "EIN", "EIN",
  "ON")
s("PRUEFTEXT", "ERWEITERUNG", "Erweiterung",
  "Extension")
s("PRUEFTEXT", "EXEC_GESPERRT", "gesperrt (config.php wird ungeprüft geschrieben)",
  "blocked (config.php is written unchecked)")
s("PRUEFTEXT", "FAHRGESTELLNUMMER", "Fahrgestellnummer",
  "VIN")
s("PRUEFTEXT", "FAHRZEUG_N", "Fahrzeug %d: %s",
  "Vehicle %d: %s")
s("PRUEFTEXT", "FEHLT", "FEHLT",
  "MISSING")
s("PRUEFTEXT", "FELDER_GESAMT", "Felder insgesamt",
  "Fields in total")
s("PRUEFTEXT", "GENERATION", "Generation",
  "Generation")
s("PRUEFTEXT", "GRAD", "Grad",
  "degrees")
s("PRUEFTEXT", "KAMEREONKONTO", "Kamereon-Konto",
  "Kamereon account")
s("PRUEFTEXT", "KEINE", "keine",
  "none")
s("PRUEFTEXT", "KEIN_ABRUF", "(noch kein Abruf)",
  "(no retrieval yet)")
s("PRUEFTEXT", "KEIN_BROKER_GEFUNDEN", "nicht in general.json gefunden — MQTT-Gateway eingerichtet?",
  "not found in general.json — is the MQTT gateway set up?")
s("PRUEFTEXT", "KONFIGORDNER", "Konfigurationsordner",
  "Configuration folder")
s("PRUEFTEXT", "LADEZIEL", "Ladeziel min / soll",
  "Charge target min / goal")
s("PRUEFTEXT", "LAND", "Land",
  "Country")
s("PRUEFTEXT", "LEER", "LEER",
  "EMPTY")
s("PRUEFTEXT", "MELDESCHWELLE", "Meldeschwelle",
  "Notification threshold")
s("PRUEFTEXT", "MQTTBROKER", "MQTT-Broker",
  "MQTT broker")
s("PRUEFTEXT", "NICHT_BESCHREIBBAR", "NICHT beschreibbar",
  "NOT writable")
s("PRUEFTEXT", "NICHT_GESETZT", "nicht gesetzt",
  "not set")
s("PRUEFTEXT", "NICHT_VORHANDEN", "nicht vorhanden",
  "not present")
s("PRUEFTEXT", "NICHT_WOHLGEFORMT", "NICHT WOHLGEFORMT",
  "NOT WELL-FORMED")
s("PRUEFTEXT", "N_ELEMENTE", "%d Elemente",
  "%d elements")
s("PRUEFTEXT", "PASSWORT", "Passwort",
  "Password")
s("PRUEFTEXT", "PHASE_N", "Phase %s",
  "phase %s")
s("PRUEFTEXT", "PHPFASSUNG", "PHP-Fassung",
  "PHP version")
s("PRUEFTEXT", "PROTOKOLLORDNER", "Protokollordner",
  "Log folder")
s("PRUEFTEXT", "SITZUNGSTOKEN", "Sitzungstoken",
  "Session token")
s("PRUEFTEXT", "STEUERUNG", "Steuerung",
  "Switching")
s("PRUEFTEXT", "TAKT", "Takt normal / laden",
  "Interval normal / charging")
s("PRUEFTEXT", "THEMEN_CODE", "Im Programmcode veröffentlicht : %d Themen",
  "Published by the code   : %d topics")
s("PRUEFTEXT", "THEMEN_FUNDSTELLEN", "Fundstellen im Programmcode:",
  "Places in the source:")
s("PRUEFTEXT", "THEMEN_GLEICH", "Beide Listen sind deckungsgleich.",
  "Both lists match.")
s("PRUEFTEXT", "THEMEN_LISTE", "In der Anleitung aufgeführt    : %d Themen",
  "Listed in the manual    : %d topics")
s("PRUEFTEXT", "THEMEN_NUR_CODE", "GESENDET, ABER NICHT IN DER ANLEITUNG",
  "SENT BUT NOT IN THE MANUAL")
s("PRUEFTEXT", "THEMEN_NUR_LISTE", "IN DER ANLEITUNG, ABER NIE GESENDET",
  "IN THE MANUAL BUT NEVER SENT")
s("PRUEFTEXT", "THEMEN_NUR_LISTE_ZUSATZ", "(wer diese Eingänge anlegt, bekommt nie einen Wert)",
  "(anyone creating these inputs never gets a value)")
s("PRUEFTEXT", "UNBEKANNT", "unbekannt",
  "unknown")
s("PRUEFTEXT", "VERFUEGBAR", "verfügbar",
  "available")
s("PRUEFTEXT", "VORHANDEN", "vorhanden",
  "present")
s("PRUEFTEXT", "VORLAGE_ABGLEICH", "Abgleich der Einheiten in der Namenstabelle mit dem Sendecode:",
  "Comparing the units in the name table with the sending code:")
s("PRUEFTEXT", "VORLAGE_FEHLT", "ACHTUNG — die Namenstabelle nennt Einheiten für Themen, die nie gesendet werden:",
  "ATTENTION — the name table lists units for topics that are never sent:")
s("PRUEFTEXT", "VORLAGE_OK", "Jedes Thema mit Einheit wird vom Programmcode auch gesendet.",
  "Every topic with a unit is also sent by the code.")
s("PRUEFTEXT", "WETTERSCHLUESSEL", "Wetterschlüssel",
  "Weather key")
s("PRUEFTEXT", "WOHLGEFORMT", "wohlgeformt",
  "well-formed")
s("PRUEFTEXT", "ZIELTEMPERATUR", "Klima-Zieltemperatur",
  "A/C target temperature")
s("PRUEFTEXT", "ZWEITSCHRIFT", "Zweitschrift",
  "Second copy")
s("PRUEFTEXT", "ZWISCHENSPEICHER", "Zwischenspeicher",
  "Cache")
s('PRUEFTEXT', 'V2_UNKLAR',
  'nicht feststellbar (Gateway-Fassung oder subscriptions.json nicht lesbar)',
  'cannot be determined (gateway version or subscriptions.json not readable)')
s('PRUEFTEXT', 'V2_V1',
  'trifft nicht zu (Gateway V1 – es gilt das Abo Renault/#)',
  'not applicable (gateway V1 – the subscription Renault/# applies)')
s('PRUEFTEXT', 'V2_ZAHL',
  '%d von %d angehakt.',
  '%d of %d ticked.')
s('PRUEFTEXT', 'V2_FEHLT',
  'Es fehlen: %s.',
  'Missing: %s.')
s('PRUEFTEXT', 'V2_NC',
  'Noncached falsch: %s.',
  'Noncached wrong: %s.')
s('PRUEFTEXT', 'V2_NICHT_EINGERICHTET',
  'noch nicht eingerichtet – angehakt wird erst, wenn Werte kommen.',
  'not set up yet – tick them once values arrive.')
s('PRUEFTEXT', 'VORLAGEN_CRLF',
  '%d Vorlagen CRLF und wohlgeformt',
  '%d templates CRLF and well-formed')
s('TEXT', 'ABO_MITGELIEFERT',
  "Rückfall Gateway V1: das Plugin bringt das Abo <span class='sm-mono'>Renault/#</span> selbst mit (<span class='sm-mono'>mqtt_subscriptions.cfg</span> im Konfigurationsordner) — einzutragen ist dort nichts.",
  "Fallback gateway V1: the plugin brings the subscription <span class='sm-mono'>Renault/#</span> itself (<span class='sm-mono'>mqtt_subscriptions.cfg</span> in the configuration folder) — nothing needs to be entered there.")
s("TEXT", "H_ABRUF_TEST", "Daten holen",
  "Fetch data")
s("TEXT", "H_ABRUF_TEST_TEXT", "Dieser Knopf holt nur Daten vom Fahrzeug ab und verändert nichts. Er wirkt auch dann, wenn das Schalten unten ausgeschaltet ist.",
  "This button only fetches data from the vehicle and changes nothing. It works even when switching is turned off below.")
s("TEXT", "H_LOG_RAMDISK", "<b>Das Protokoll übersteht keinen Neustart.</b> Es liegt unter <span class='sm-mono'>log/plugins</span>, und dieser Ordner ist auf dem LoxBerry eine Ramdisk. Wer eine Meldung aufheben will, kopiert sie vorher heraus.",
  "<b>The log does not survive a reboot.</b> It lives under <span class='sm-mono'>log/plugins</span>, and on the LoxBerry that folder is a RAM disk. To keep a message, copy it out first.")
s('TEXT', 'SICH_DIENST',
  'Zwischenspeicher und Anmeldung wurden verworfen; der Abruf meldet sich beim nächsten Cron-Lauf neu an, spätestens in %d Minuten.',
  'Cached data and the stored login were discarded; the retrieval logs in again on the next cron run, within %d minutes at the latest.')
s("TEXT", "SICH_FEHLT", "In der Datei fehlen %d von %d Einstellungen (%s). Eine vom Plugin erzeugte Sicherung führt immer alle.",
  "The file is missing %d of %d settings (%s). A backup created by this plugin always contains all of them.")
s("TEXT", "SICH_WERT", "Unzulässiger Wert für die Einstellung %s — die Datei wurde nicht übernommen.",
  "Invalid value for setting %s — the file was not applied.")
s("TEXT", "S_NICHT_MESSBAR", "%d Zeile(n) konnten hier nichts messen — sie stehen als Punkt und sind weder Haken noch Kreuz.",
  "%d line(s) could not measure anything here — they show a dot and are neither a tick nor a cross.")
s("TEXT", "S_RETAINED", "retained",
  "retained")
t('F_ZEICHEN', "<b>%s</b>: Anführungs- und Steuerzeichen sind hier nicht erlaubt – bitte entfernen.", "<b>%s</b>: quotation marks and control characters are not allowed here – please remove them.")
t('F_AUSWAHL', "<b>%s</b>: nur ja oder nein ist zulässig.", "<b>%s</b>: only yes or no is allowed.")
t('SICH_WARN_KNOPF', "<b>Achtung:</b> Das Zurückspielen dieser Sicherung würde abgewiesen – wegen <span class='sm-mono'>%s</span>. Die Datei wird trotzdem vollständig geliefert; bitte diese Einstellungen vorher richtigstellen und speichern.", "<b>Caution:</b> restoring this backup would be rejected – because of <span class='sm-mono'>%s</span>. The file is still delivered in full; please correct these settings and save them first.")
t('SICH_WARN_KOPF', "Das Zurückspielen dieser Datei würde abgewiesen – wegen: %s. Bitte diese Einstellungen richtigstellen, speichern und neu sichern.", "Restoring this file would be rejected – because of: %s. Please correct these settings, save them and back up again.")
t('SICH_GANZE_DATEI', "die ganze Datei", "the whole file")
t('KAPUTT_ANGEBOT', "<b>Neben der Konfiguration liegt eine beiseitegelegte, unbrauchbare Fassung</b> (<span class='sm-mono'>%s</span>, Stand %s). Sie entsteht, wenn ein Update oder die Selbstheilung eine beschädigte <span class='sm-mono'>config.php</span> ersetzt.", "<b>An unusable configuration has been set aside next to the configuration</b> (<span class='sm-mono'>%s</span>, as of %s). This happens when an update or the self-repair replaces a damaged <span class='sm-mono'>config.php</span>.")
t('KAPUTT_FELDER', "Daraus ließen sich diese Einstellungen lesen, die vom jetzigen Stand abweichen: <span class='sm-mono'>%s</span>. Der Knopf holt sie ins Formular; gespeichert wird erst mit „Speichern“.", "These settings could be read from it and differ from the current ones: <span class='sm-mono'>%s</span>. The button puts them into the form; nothing is stored until you press “Save”.")
t('KAPUTT_GEHEIM', "Außerdem stand darin: <span class='sm-mono'>%s</span>. Geheimnisse kommen nie ins Formular; das Passwort lässt sich beim Speichern über den Haken am Passwortfeld übernehmen, Schlüssel bitte neu eintragen.", "It also contained: <span class='sm-mono'>%s</span>. Secrets never go into the form; the password can be taken over when saving via the tick box at the password field, please enter keys again.")
t('K_KAPUTT_UEBERNEHMEN', "Gelesene Werte ins Formular holen", "Put the read values into the form")
t('K_KAPUTT_VERWERFEN', "Beiseitegelegte Datei löschen", "Delete the set-aside file")
t('L_KAPUTT_JA', "Ja, löschen", "Yes, delete")
t('M_KAPUTT_IM_FORMULAR', "Die gelesenen Werte stehen jetzt im Formular (<span class='sm-mono'>%s</span>). <b>Gespeichert ist noch nichts</b> – bitte prüfen und „Speichern“ drücken.", "The read values are now in the form (<span class='sm-mono'>%s</span>). <b>Nothing has been saved yet</b> – please check and press “Save”.")
t('F_KAPUTT_WEG', "Es gibt keine beiseitegelegte Konfiguration (mehr) mit lesbaren, abweichenden Werten.", "There is no (longer a) set-aside configuration with readable, differing values.")
t('F_KAPUTT_HAKEN', "Zum Löschen bitte den Haken „Ja, löschen“ setzen – es wurde nichts gelöscht.", "To delete, please tick “Yes, delete” – nothing was deleted.")
t('M_KAPUTT_GELOESCHT', "Gelöscht: <span class='sm-mono'>%s</span>.", "Deleted: <span class='sm-mono'>%s</span>.")
t('F_KAPUTT_LOESCHEN', "Diese Datei ließ sich nicht löschen: <span class='sm-mono'>%s</span>.", "This file could not be deleted: <span class='sm-mono'>%s</span>.")
t('L_PASSWORT_AUS_KAPUTT', "Passwort aus der beiseitegelegten Datei übernehmen (%s)", "Take over the password from the set-aside file (%s)")
t('F_PASSWORT_AUS_KAPUTT', "Das Passwort ließ sich aus der beiseitegelegten Datei nicht lesen – bitte von Hand eintragen.", "The password could not be read from the set-aside file – please enter it by hand.")
t('F_PASSWORT_DOPPELT', "Passwort: bitte entweder ein neues eintragen, löschen oder aus der beiseitegelegten Datei übernehmen – nicht zwei davon zugleich.", "Password: please either enter a new one, delete it or take it over from the set-aside file – not two of these at once.")
s("THEMA", "STATUS_TS", "Zeitstempel des letzten Cron-Durchgangs in Unix-Sekunden. Er geht bei jedem Durchgang hinaus, auch wenn nichts geholt wurde, und ist nicht zurückbehalten. Alter in Loxone: (Loxone-Zeit + 1230768000) − ts.",
  "Timestamp of the last cron run in Unix seconds. It is sent on every run, even when nothing was fetched, and is not retained. Age in Loxone: (Loxone time + 1230768000) − ts.")
s("THEMA", "STATUS_ZAEHLER", "Läuft mit jedem Cron-Durchgang um eins weiter, 0 bis 999. Ändert er sich nicht mehr, steht der Cron.",
  "Increments by one on every cron run, 0 to 999. If it stops changing, the cron has stopped.")
s('THEMA', 'ZUHAUSE',
  'Zu Hause: 1 ja, 0 unterwegs, -1 ohne Aussage (Heimzone, retained)',
  'At home: 1 yes, 0 away, -1 no statement (home zone, retained)')
s('THEMA', 'ENTFERNUNG',
  'Entfernung zum Heimpunkt in km (-1 ohne Aussage)',
  'Distance to the home point in km (-1 no statement)')
s('THEMA', 'VORKLIMA',
  'Vorklimatisierung: 0 nichts/aus, 1 gesendet, 2 mild übersprungen, 3 wartet auf Wiederholung, 4 wartet auf Anwesenheit, 5 nicht gesendet (Akku unter der Grenze), 6 nicht gesendet (Kabel fehlt), -1 gescheitert',
  'Pre-conditioning: 0 nothing/off, 1 sent, 2 skipped (mild), 3 waiting for retry, 4 waiting for presence, 5 not sent (battery below the limit), 6 not sent (cable missing), -1 failed')
s('THEMA', 'LADUNG_KOSTEN',
  'Letzte Ladung: Kosten in Euro (Endpreis ohne Grundpreis, -1 ohne Aussage)',
  'Last charge: cost in euro (final price without base fee, -1 no statement)')
s('THEMA', 'LADUNG_ENERGIE',
  'Letzte Ladung: Energie in den Akku in kWh (-1 nicht bestimmbar)',
  'Last charge: energy into the battery in kWh (-1 not determinable)')
s('THEMA', 'LADUNG_PREIS',
  'Letzte Ladung: Durchschnittspreis in ct/kWh (-1 ohne Aussage)',
  'Last charge: average price in ct/kWh (-1 no statement)')
s('THEMA', 'STATUS_BEFEHLE',
  'Befehlsbrücke: 1 läuft, 0 aus, -1 Fehler (Noncached)',
  'Command bridge: 1 running, 0 off, -1 error (Noncached)')

# Abschnitte, deren Werte AUSNAHMSLOS ueber rn_e() ausgegeben werden. Ein
# "&" oder "<" darin wird im Browser woertlich sichtbar - das ist die
# doppelte Maskierung, der teuerste Einzelbefund der Pruefreihe (40 Stellen
# in 13 Plugins). Deshalb steht die Regel hier als Wache und nicht als Satz
# in einer Anleitung.
# ---- Sprachausgabe (Nr. 36 b) ----
s('PRUEF', 'ANSAGE', 'Sprachausgabe', 'Speech output')
s('PRUEF', 'V2',
  'Gateway V2: sind alle Datenpunkte angehakt?',
  'Gateway V2: are all data points ticked?')
s('PRUEF', 'NAMEN_RESERVIERT',
  'Trägt ein Fahrzeug einen reservierten Namen (status, befehl)?',
  'Does a vehicle carry a reserved name (status, befehl)?')
s('PRUEF', 'NAMEN_RESERVIERT_JA',
  'ja: %s – fällt mit Renault/status/befehle bzw. Renault/befehl/ zusammen; im Reiter Einstellungen umbenennen',
  'yes: %s – collides with Renault/status/befehle or Renault/befehl/; rename it on the Settings tab')
s('PRUEF', 'NAMEN_RESERVIERT_NEIN',
  'nein',
  'no')
s('PRUEF', 'ENDPUNKT_EIN',
  'Nimmt der bisherige HTTP-Endpunkt Befehle an?',
  'Does the previous HTTP endpoint accept commands?')
s('PRUEF', 'ENDPUNKT_EIN_JA',
  'ja (Haken im Reiter Einstellungen)',
  'yes (checkbox on the Settings tab)')
s('PRUEF', 'ENDPUNKT_EIN_NEIN',
  'nein – jeder Aufruf ausser ?selftest bekommt 403 ENDPUNKT_AUS',
  'no – every call except ?selftest gets 403 ENDPUNKT_AUS')
s('PRUEF', 'SPERRE_ORT',
  'Wo liegt die Abrufsperre (Cron und Endpunkt)?',
  'Where is the retrieval lock (cron and endpoint)?')
s('PRUEF', 'BRUECKE',
  'Läuft die Befehlsbrücke?',
  'Is the command bridge running?')
s('PRUEF', 'BRUECKE_PRUEFEN',
  'Einrichtung der Befehlsbrücke (befehlsbruecke.php --pruefen)',
  'Setup of the command bridge (befehlsbruecke.php --pruefen)')
s('PRUEF', 'MOSQUITTO',
  'Sind mosquitto_sub und mosquitto_pub da (Leser, Brücke, Testmeldung)?',
  'Are mosquitto_sub and mosquitto_pub present (reader, bridge, test message)?')
s('PRUEF', 'MOSQUITTO_FEHLT',
  'nein – Paket mosquitto-clients fehlt; Haus-Themen und Brücke ruhen',
  'no – package mosquitto-clients missing; house topics and bridge are idle')
s('PRUEF', 'NICHT_EINGERICHTET',
  'noch nicht eingerichtet – keine Zugangsdaten',
  'not set up yet – no credentials')
s('PRUEF', 'VORKLIMA',
  'Vorklimatisierung %s',
  'Pre-conditioning %s')
s('PRUEF', 'VORKLIMA_STAND',
  'Vorklima %d, Abfahrt %s, Versuche %d.',
  'Vorklima %d, departure %s, attempts %d.')
s('PRUEF', 'VORKLIMA_WIRKT_NICHT',
  'Wirkt erst mit Steuerung und dem Haken für die Abfahrt aus dem Haus-Thema.',
  'Takes effect only with switching and the checkbox for the departure from the house topic.')
s('PRUEF', 'HEIM',
  'Heimzone: Heimpunkt gesetzt, letzte Aussage',
  'Home zone: home point set, last statement')
s('PRUEF', 'HEIM_GESETZT',
  'Heimpunkt gesetzt: ja',
  'Home point set: yes')
s('PRUEF', 'HEIM_FEHLT',
  'Heimpunkt gesetzt: nein',
  'Home point set: no')
s('PRUEF', 'LADUNG',
  'Laufende Ladung %s',
  'Running charge %s')
s('PRUEF', 'LADUNG_STAND',
  '%d Abrufe, %d von %d Minuten mit Preis.',
  '%d retrievals, %d of %d minutes with price.')
s('PRUEF', 'VORLAGEN',
  'Sind die Loxone-Vorlagen CRLF und wohlgeformt?',
  'Are the Loxone templates CRLF and well-formed?')
s('TEXT', 'H_ANSAGE',
  'Sprachausgabe (Ansagen, ab Werk an)',
  'Speech output (announcements, on by default)')
s('TEXT', 'ANSAGE_ERKLAERUNG',
  'Der Abruf kann einzelne Ereignisse ansagen – über den Loxone Music Server, MusicServer4Home, eine eigene Adressvorlage, Alexa-NG oder Google-Lautsprecher (Chromecast 4 Lox NG). Ab Werk ist die Ausgabe <b>an</b>. Angesagt wird nur ein Wechsel, nie ein Wert im Takt; derselbe Anlass wird für dasselbe Fahrzeug höchstens einmal je Stunde angesagt, und nach einer Neuinstallation oder einer Pause von mehr als sechs Stunden setzt der erste Abruf nur den Ausgangsstand. MQTT, Loxone, Mail und exec bleiben davon unberührt. Adresse und Vorlage müssen im Heimnetz liegen.',
  'The poll can announce single events – through the Loxone Music Server, MusicServer4Home, an own address template, Alexa-NG or Google speakers (Chromecast 4 Lox NG). The output is <b>on</b> by default. Only a change is announced, never a value on every poll; the same event is announced for the same vehicle at most once per hour, and after a new installation or a pause of more than six hours the first poll only sets the starting point. MQTT, Loxone, mail and exec are not affected. Address and template must be in the home network.')
s('TEXT', 'H_ANSAGE_ANLAESSE', 'Anlässe', 'Events')
s('TEXT', 'L_ANSAGE_LADEN_FERTIG', 'Ladung beendet (Ladeziel erreicht oder unbekannt)', 'Charging finished (target reached or unknown)')
s('TEXT', 'L_ANSAGE_LADEN_ABBRUCH', 'Ladung unter dem Ladeziel oder mit Störung beendet', 'Charging ended below the target or with a fault')
s('TEXT', 'L_ANSAGE_AKKU', 'Ladeschwelle erreicht (Akkustand für die Meldung, oben)', 'Charge threshold reached (battery level for the notification, above)')
s('TEXT', 'L_ANSAGE_AUSFALL', 'Keine Daten mehr (drei Abrufe in Folge gescheitert)', 'No more data (three polls in a row failed)')
s('TEXT', 'H_ANSAGE_ANLAESSE_HILFE', 'Jeder Anlass lässt sich einzeln abwählen; er wirkt erst, wenn oben eine Ausgabeart gewählt ist. Das Ladeziel ist das oben eingetragene (soc_target); ohne Ladeziel heißt jedes Ladeende „beendet“. Die Testansage steht im Reiter <i>Test</i>.', 'Each event can be deselected; it only takes effect once an output is chosen above. The charge target is the one entered above (soc_target); without a target every end of charging counts as finished. The test announcement is on the <i>Test</i> tab.')
s('TEXT', 'SICH_TTS_TOKEN', 'Die Datei trägt ein Sprechtoken (%s). Eine Sicherung dieses Plugins enthält nie eines – die Datei wird abgewiesen, das geltende Token bleibt.', 'The file carries a speech token (%s). A backup of this plugin never contains one – the file is rejected, the current token stays.')
s('TEXT', 'SICH_TTS', 'Unzulässiger Wert in der Sprachausgabe (tts_*): %s', 'Invalid value in the speech output (tts_*): %s')
s('TEXT', 'SICH_OHNE_ANSAGE', 'Die Sicherung stammt aus einer Fassung vor 2.1.16 und kennt die Sprachausgabe noch nicht – deren Einstellungen bleiben, wie sie sind.', 'The backup comes from a version before 2.1.16 and does not know the speech output yet – its settings stay as they are.')
t('SICH_SPAET',
  'Nicht in der Sicherung, unverändert: %s (die Sicherung stammt aus einer früheren Fassung).',
  'Not in the backup, unchanged: %s (the backup comes from an earlier version).')
s('TEXT', 'SICH_OHNE_SPRECHTOKEN', 'Die Sprechtoken der Sprachausgabe (Alexa-NG, Chromecast 4 Lox NG) stehen nie in der Sicherung; nach dem Zurückspielen auf einer neuen Anlage dort neu eintragen.', 'The speech tokens of the speech output (Alexa-NG, Chromecast 4 Lox NG) are never in the backup; enter them again after restoring on a new system.')
s('TEXT', 'A_ANSAGE_ANLAESSE', 'Eingeschaltete Anlässe (%s): %s.', 'Events switched on (%s): %s.')
s('TEXT', 'A_ANSAGE_KEINE', 'keiner', 'none')
s('TEXT', 'H_ANSAGE_TEST', 'Sprachausgabe', 'Speech output')
s('TEXT', 'ANSAGE_TEST_TEXT', 'Spricht den Prüfsatz über die eingestellte Ausgabeart – unabhängig von den Anlässen.', 'Speaks the test sentence through the chosen output – independent of the events.')
s('TEXT', 'K_ANSAGE_TEST', 'Testansage', 'Test announcement')
s('TEXT', 'M_ANSAGE_TEST_OK', 'Testansage gesendet.', 'Test announcement sent.')
s('TEXT', 'M_ANSAGE_TEST_NICHTS', 'Keine Testansage: %s', 'No test announcement: %s')
s('TEXT', 'M_ANSAGE_TEST_FEHL', 'Testansage nicht gesendet: %s', 'Test announcement not sent: %s')
s('TEXT', 'ANSAGE_S_LADEN_FERTIG', '%s: Die Ladung ist beendet.', '%s: Charging has finished.')
s('TEXT', 'ANSAGE_S_LADESTAND', 'Ladestand %s Prozent.', 'Battery at %s percent.')
s('TEXT', 'ANSAGE_S_LADEN_ABBRUCH', '%s: Die Ladung wurde bei %s Prozent beendet, unter dem Ladeziel von %s Prozent.', '%s: Charging ended at %s percent, below the charge target of %s percent.')
s('TEXT', 'ANSAGE_S_LADEN_STOERUNG', '%s: Die Ladung wurde mit einer Störung beendet.', '%s: Charging ended with a fault.')
s('TEXT', 'ANSAGE_S_AKKU', '%s: Der Akku ist auf %s Prozent geladen.', '%s: The battery is charged to %s percent.')
s('TEXT', 'ANSAGE_S_AUSFALL', '%s: Seit drei Abrufen kommen keine Daten mehr.', '%s: no data for three polls.')
# Kopf wie alle Hausplugins (Entscheidung Nr. 43, 2.1.17): Statusuebersicht ueber den
# Reitern und gruener Kasten oben im Reiter Einstellungen (WAS_IST_DAS roh, rn_t ohne rn_e).
s('TEXT', 'KOPF_EIGENSCHAFT', 'Eigenschaft', 'Property')
s('TEXT', 'KOPF_ABRUF', 'Abruf', 'Polling')
s('TEXT', 'KOPF_OHNE_DIENST', 'ohne Dienst – Cron alle %d min, beim Laden alle %d min', 'no service – cron every %d min, every %d min while charging')
s('TEXT', 'KOPF_KONTO', 'My-Renault-Konto', 'My Renault account')
s('TEXT', 'KOPF_KONTO_JA', 'Zugangsdaten eingetragen', 'credentials entered')
s('TEXT', 'KOPF_KONTO_NEIN', 'keine Zugangsdaten', 'no credentials')
s('TEXT', 'KOPF_LETZTER_ERFOLG', 'Letzter erfolgreicher Abruf (%s)', 'Last successful poll (%s)')
s('TEXT', 'KOPF_NOCH_KEIN', 'noch kein Abruf', 'no poll yet')
t('KOPF_KEINE_DATEN',
  'Fahrzeugdaten %s',
  'Vehicle data %s')
t('KEINE_DATEN_HINWEIS',
  'Renault liefert für dieses Fahrzeug keine Batteriedaten (HTTP 404) – häufig: Online-Abo ausgelaufen. Prüfen in der My-Renault-App. Das Plugin fragt alle %d Minuten weiter nach und schaltet von selbst zurück, sobald wieder Daten kommen.',
  'Renault returns no battery data for this vehicle (HTTP 404) – often: online subscription expired. Check in the My Renault app. The plugin keeps asking every %d minutes and switches back by itself as soon as data arrives.')
s('TEXT', 'KOPF_BROKER', 'MQTT-Broker', 'MQTT broker')
s('TEXT', 'KOPF_KEIN_BROKER', 'nicht eingerichtet (System → MQTT Gateway)', 'not configured (System → MQTT Gateway)')
s('TEXT', 'KOPF_SCHALTEN', 'Schaltbefehle aus Loxone', 'Switching commands from Loxone')
s('TEXT', 'KOPF_SCHALTEN_JA', 'erlaubt', 'allowed')
s('TEXT', 'KOPF_SCHALTEN_NEIN', 'gesperrt (Vorgabe)', 'blocked (default)')
s('TEXT', 'WAS_IST_DAS', '<b>Renault-Elektrofahrzeuge am Loxone Miniserver – über das My-Renault-Konto.</b> Ein Abruf im eingestellten Takt (Cron, ohne eigenen Dienst) holt für bis zu vier Fahrzeuge Batteriestand, Reichweite, Ladestatus, Kilometerstand, Position und weitere Werte über die My-Renault-Schnittstelle. Die Werte gehen per MQTT über das LoxBerry MQTT Gateway an den Miniserver. Vorklimatisierung und Ladesteuerung lassen sich aus Loxone über einen tokengeschützten HTTP-Endpunkt auslösen – schaltende Befehle sind ab Werk gesperrt.', '<b>Renault electric vehicles on the Loxone Miniserver – via the My Renault account.</b> A poll at the configured interval (cron, no service of its own) fetches battery level, range, charging state, mileage, location and further values for up to four vehicles through the My Renault interface. The values reach the Miniserver over MQTT through the LoxBerry MQTT Gateway. Pre-conditioning and charging control can be triggered from Loxone through a token-protected HTTP endpoint – switching commands are disabled by default.')
t('F_NAME_RESERVIERT',
  'Fahrzeug %d: der Name <b>%s</b> ist reserviert (fiele mit Renault/status/befehle bzw. Renault/befehl/ zusammen) – bitte einen anderen wählen.',
  'Vehicle %d: the name <b>%s</b> is reserved (would collide with Renault/status/befehle or Renault/befehl/) – please choose another.')
t('F_WERT_FELD',
  '<b>%s</b>: der Wert ist nicht zulässig.',
  '<b>%s</b>: the value is not allowed.')
t('L_ENDPUNKT_EIN',
  'Befehle über den bisherigen HTTP-Endpunkt annehmen (mit Token)',
  'Accept commands via the previous HTTP endpoint (with token)')
t('H_ENDPUNKT_EIN',
  "Ab Werk aus bei einer Neuinstallation; ein Update von 2.1.19 lässt ihn an, damit eine vorhandene HTTP-Vorlage weiter wirkt. Neue Anlagen nehmen Gateway V2 und die Befehlsbrücke (Reiter MQTT). Ist er aus, antwortet jeder Aufruf ausser <span class='sm-mono'>?selftest</span> mit 403.",
  "Off by default on a new installation; an update from 2.1.19 leaves it on so that an existing HTTP template keeps working. New installations use gateway V2 and the command bridge (MQTT tab). When off, every call except <span class='sm-mono'>?selftest</span> answers with 403.")
t('H_ENDPUNKT_AUS',
  '<b>Dieser Weg ist ausgeschaltet</b> (Reiter Einstellungen, <i>Befehle über den bisherigen HTTP-Endpunkt annehmen</i>). Jeder Aufruf ausser dem Selbsttest bekommt HTTP 403.',
  '<b>This path is switched off</b> (Settings tab, <i>Accept commands via the previous HTTP endpoint</i>). Every call except the self-test gets HTTP 403.')
t('H_HTTP_BISHER',
  'Bisheriger Weg über HTTP (aufklappen)',
  'Previous path via HTTP (expand)')
t('H_HTTP_BISHER_TEXT',
  "Wer die HTTP-Vorlage <span class='sm-mono'>VQ_renault_steuern.xml</span> schon nutzt, ändert nichts – der Endpunkt bleibt beim Update offen. Neue Anlagen nehmen Gateway V2 und die Befehlsbrücke (Schritt 3). Ein Befehl geht sofort hinaus; der Abruf danach nur, wenn gerade kein anderer läuft (sonst die Zeile <span class='sm-mono'>ABRUF=SKIP</span> – der Cron holt binnen 3 Minuten).",
  "Anyone already using the HTTP template <span class='sm-mono'>VQ_renault_steuern.xml</span> changes nothing – the endpoint stays open on update. New installations use gateway V2 and the command bridge (step 3). A command goes out immediately; the retrieval after it only if no other one is running (otherwise the line <span class='sm-mono'>ABRUF=SKIP</span> – the cron fetches within 3 minutes).")
t('H_KEINE_AENDERUNG_24H',
  'In den letzten 24 Stunden hat sich am Fahrzeug nichts geändert.',
  'Nothing has changed on the vehicle in the last 24 hours.')
t('H_V2_TABELLE',
  'Je Fahrzeug die Datenpunkte, die das Plugin sendet; <b>Titel</b> ist der Name, den das Gateway vergibt (Schrägstrich, Prozent und Leerzeichen werden Unterstrich). Ein Zahlthema ohne Wert kommt mit seinem <b>Fehlwert</b> (-1, Temperaturen -99, GPS -999); ein Ladestatus ohne Wert wird nicht gesendet, weil -1 bei Renault Ladefehler heisst.',
  'Per vehicle the data points the plugin sends; <b>title</b> is the name the gateway assigns (slash, percent and space become underscore). A numeric topic without a value arrives with its <b>missing value</b> (-1, temperatures -99, GPS -999); a charging status without a value is not sent, because -1 means charging error at Renault.')
t('SCHRITT2_V2',
  "Im MQTT-Gateway V2 die Datenpunkte aus der Tabelle des Reiters MQTT anhaken; <span class='sm-mono'>ok</span>, <span class='sm-mono'>status/zaehler</span> und <span class='sm-mono'>Renault/status/befehle</span> als Noncached. Die Namen stehen in der Tabelle darunter.",
  "In MQTT gateway V2 tick the data points from the table on the MQTT tab; <span class='sm-mono'>ok</span>, <span class='sm-mono'>status/zaehler</span> and <span class='sm-mono'>Renault/status/befehle</span> as Noncached. The names are in the table below.")
t('S_FAHRZEUG',
  'Fahrzeug',
  'Vehicle')
t('S_FEHLWERT',
  'Fehlwert',
  'Missing value')
t('S_FEHLWERT_KEINER',
  'wird nicht gesendet',
  'not sent')
t('S_NONCACHED',
  'Noncached',
  'Noncached')
t('M_SESSION_VERWORFEN',
  'Der Zwischenspeicher von %s wurde verworfen (andere Fahrgestellnummer, Phase oder Zugangsdaten) – der nächste Abruf holt alles neu.',
  'The cache of %s was discarded (different VIN, phase or credentials) – the next retrieval fetches everything anew.')

# ---------------------------------------------------------------- BAUSTEIN
# Welle Bild 17 (Renault NG 2.1.19, 17.10.2026): die drei Seiten aus dem LoxBerry-Plugins Musterprojekt im
# Reiter "Einbindung in Loxone", Schritt 6 - Kaesten "So uebernehmen Sie diese Seite", Hinweise und je
# Tabellenzeile ein Schluessel Z<seite>_<nn> = "Typ | Name | Parameter | Eingaenge" (deutsch wortgleich mit
# Musterprojekt/baustein_listen.txt, englisch: Typnamen nach Config, Namen deutsch). Alles reiner Text,
# index.php gibt jede Zelle maskiert aus (rn_e). Quelle: vb_bild_rn17_bau_skripte/rn_daten.py.
s('BAUSTEIN', 'SCHRITTE_TITEL',
  'So übernehmen Sie diese Seite',
  'How to take over this page')
s('BAUSTEIN', 'HINWEISE_TITEL',
  'Hinweise',
  'Notes')
s('BAUSTEIN', 'S1_SCHRITT1',
  'Im Plugin, Reiter „%s“: My-Renault-Benutzer und Passwort, Fahrgestellnummer und Fahrzeuggeneration eintragen, speichern. Der Fahrzeugname bildet die Namen der Eingänge (Renault_Fahrzeugname_Thema): mit dem Werksnamen „Renault“ gleichen sie dem Musterprojekt, ein anderer Name ist in den Tabellen schon eingerechnet. Reiter „%s“ → „%s“; im Reiter „%s“ steht danach „Batterie-Status … OK“.',
  'In the plugin, tab “%s”: enter the My Renault user and password, the VIN and the vehicle generation, save. The vehicle name forms the names of the inputs (Renault_vehiclename_topic): with the factory name “Renault” they match the sample project, another name is already worked into the tables. Tab “%s” → “%s”; the tab “%s” then shows “Batterie-Status … OK”.')
s('BAUSTEIN', 'S1_SCHRITT2',
  'In Loxone Config unter Peripherie → Virtuelle Eingänge für Nr. 1–7 je einen „Virtuellen Eingang“ anlegen. Die Bezeichnung genau so schreiben wie in der Tabelle – das ist der Name, den das MQTT-Gateway vergibt (vollständige Namenstabelle oben in Schritt 3). Haken „Analog“ setzen und den lesbaren Namen aus der Tabelle (z. B. „Ladestand (Renault)“) als Beschreibung eintragen. Die Bezeichnung NICHT verschönern, sonst legt das Gateway beim nächsten Wert einen zweiten Eingang an. Eine Importdatei für diese Eingänge gibt es bewusst nicht.',
  'In Loxone Config under Periphery → Virtual Inputs create one “Virtual input” each for no. 1–7. Write the name exactly as in the table – it is the name the MQTT gateway gives (complete name table above in step 3). Tick “Analog” and enter the readable name from the table (e.g. “Ladestand (Renault)”) as description. Do NOT beautify the name, otherwise the gateway creates a second input with the next value. There is deliberately no import file for these inputs.')
s('BAUSTEIN', 'S1_SCHRITT3',
  'Vier Benachrichtigungen anlegen (Peripherie → Mitteilungen → Benachrichtigung), Texte wie in der Tabelle. Jede bekommt genau eine Leitung.',
  'Create four notifications (Periphery → Messages → Notification), texts as in the table. Each gets exactly one connection.')
s('BAUSTEIN', 'S1_SCHRITT4',
  'Seite „Renault NG“ anlegen. Die 7 Eingänge, die „Konstante 1“ und die vier Benachrichtigungen auf die Seite ziehen.',
  'Create the page “Renault NG”. Drag the 7 inputs, the “Konstante 1” and the four notifications onto the page.')
s('BAUSTEIN', 'S1_SCHRITT5',
  'Die übrigen Bausteine über die Baustein-Suche (Taste F5) setzen, Parameter wie in der Tabelle, von oben nach unten verbinden. „Gleich“ und „Kleiner“: den zweiten Eingang offen lassen, den Vergleichswert im Eigenschaftsfenster eintragen. UND Nr. 22: den Eingang I2 negieren – in Config auf seinen Eingangspunkt klicken, danach zeigt er einen kleinen Kreis. Analogwertvalidierung Nr. 11: den Haken bei ‚En‘ im Eigenschaftsfenster entfernen (Config legt En negiert an; sonst kommt die Konstante 1 als 0 an und die Ausfallmeldung löst nie aus). Status „Ladestand und Reichweite (Renault)“: vorher zweimal „+“ klicken (V5, V6); die Zeilen der Status-Bausteine in der angegebenen Reihenfolge eintragen, die ohne Bedingung zuletzt. „Statistik“ an Nr. 4 und 5 einschalten.',
  'Place the remaining blocks via the block search (key F5), parameters as in the table, connect from top to bottom. “Equal” and “Less”: leave the second input open and enter the comparison value in the properties window. AND no. 22: negate input I2 – click its input point in Config; it then shows a small circle. Value Validator no. 11: remove the tick at ‘En’ in the properties window (Config creates En inverted; otherwise constant 1 arrives as 0 and the failure message never triggers). Status “Ladestand und Reichweite (Renault)”: click “+” twice first (V5, V6); enter the rows of the status blocks in the given order, the one without condition last. Switch on “Statistics” on no. 4 and 5.')
s('BAUSTEIN', 'S1_SCHRITT6',
  'Speichern und übertragen. Probe: „Zustand (Renault)“ zeigt „läuft – letzter erfolgreicher Abruf um …“, das Lebenszeichen zählt alle 3 Minuten weiter.',
  'Save and send to the Miniserver. Check: “Zustand (Renault)” shows “läuft – letzter erfolgreicher Abruf um …”, the heartbeat counts on every 3 minutes.')
s('BAUSTEIN', 'S1_H1',
  'Steht der LoxBerry oder das MQTT-Gateway, behalten alle Eingänge ihren letzten Wert; nur das stehende Lebenszeichen verrät es. Die Meldung kommt dann nach etwa 25 Minuten (15 Minuten bis zur Analogwertvalidierung, 10 Minuten Bestätigung). Ein falsches Passwort zeigt sich ebenso – das Plugin sendet dann gar nichts, auch kein ok = 0.',
  'If the LoxBerry or the MQTT gateway stands still, all inputs keep their last value; only the stopped heartbeat gives it away. The message then comes after about 25 minutes (15 minutes until the Value Validator, 10 minutes confirmation). A wrong password shows up the same way – the plugin then sends nothing at all, not even ok = 0.')
s('BAUSTEIN', 'S1_H2',
  'Nur der Ladestatus 1 heißt „lädt“, unter 0 meldet das Auto eine Störung – deshalb „Gleich“ und „Kleiner“ statt eines Digitaleingangs.',
  'Only charging status 1 means “charging”, below 0 the car reports a fault – hence “Equal” and “Less” instead of a digital input.')
s('BAUSTEIN', 'S1_H3',
  '„Ladung beendet“ kommt bei jedem Ladeende, auch wenn das Kabel während der Ladung gezogen wird. Erst nach einer Minute Laden zählt die Ladung; ein kurzer Ausreißer meldet nichts.',
  '“Ladung beendet” comes at every end of charging, also when the cable is pulled during charging. A charge only counts after one minute; a short outlier reports nothing.')
s('BAUSTEIN', 'S1_H4',
  'Ansagen („Die Ladung ist beendet“ usw.) spricht das Plugin selbst (Reiter „%s“, Abschnitt „%s“); dafür braucht es keinen Baustein. Die Mail bei erreichtem Akkustand stellt man ebenfalls im Plugin ein.',
  'Announcements (“charging has finished” etc.) are spoken by the plugin itself (tab “%s”, section “%s”); no block is needed for them. The e-mail at a reached battery level is also set in the plugin.')
s('BAUSTEIN', 'S1_H5',
  'Zweites Fahrzeug: im Plugin mit eigenem Namen eintragen (z. B. „Renault2“); seine Eingänge heißen dann Renault_Renault2_… Die Bausteine dieser Seite kopieren, den Zusatz „(Renault)“ anpassen und die Störungen über weitere ODER (je zwei Eingänge) vor die Benachrichtigung führen. Die Tabellen hier gelten für Fahrzeug 1.',
  'Second vehicle: enter it in the plugin with its own name (e.g. “Renault2”); its inputs are then called Renault_Renault2_… Copy the blocks of this page, adapt the suffix “(Renault)” and lead the faults through further ORs (two inputs each) to the notification. The tables here apply to vehicle 1.')
s('BAUSTEIN', 'S2_SCHRITT1',
  'Im Plugin, Reiter „%s“, Abschnitt „%s“: „%s“ einschalten und die Zieltemperatur der Vorklimatisierung wählen, speichern. Ohne das weist das Plugin jeden schaltenden Befehl ab (HTTP 403).',
  'In the plugin, tab “%s”, section “%s”: switch on “%s” and choose the target temperature for preconditioning, save. Without this the plugin rejects every switching command (HTTP 403).')
s('BAUSTEIN', 'S2_SCHRITT2',
  'Reiter „%s“ → „%s“. In Loxone Config: Baum „Virtuelle Ausgänge“ → „Vordefinierte Geräte → Vorlage importieren…“, Datei VQ_renault_steuern.xml. Nur EINMAL einlesen (zweimal ergibt doppelte Befehle). Die Adresse im Kopf ist ein Vorschlag; sie muss der Name oder die IP sein, unter der der Miniserver den LoxBerry erreicht. Probe: die Selbsttest-Adresse aus Schritt 4 im Browser öffnen → SELFTEST;OK=1;TOKEN=OK.',
  'Tab “%s” → “%s”. In Loxone Config: tree “Virtual Outputs” → “Predefined devices → Import template…”, file VQ_renault_steuern.xml. Import only ONCE (twice gives duplicate commands). The address in the header is a suggestion; it must be the name or IP under which the Miniserver reaches the LoxBerry. Check: open the self-test address from step 4 in the browser → SELFTEST;OK=1;TOKEN=OK.')
s('BAUSTEIN', 'S2_SCHRITT3',
  'Die Eingänge Nr. 3, 4, 5, 24, 25 und 26 wie auf Seite „Renault NG“ anlegen (Bezeichnung genau wie in der Tabelle, Analog, Beschreibung); „Statistik“ an Nr. 4. Nr. 6 als „Virtueller Texteingang“ mit genau diesem Titel anlegen, „In Visualisierung verwenden“ an.',
  'Create the inputs no. 3, 4, 5, 24, 25 and 26 as on page “Renault NG” (name exactly as in the table, analog, description); “Statistics” on no. 4. Create no. 6 as “Virtual text input” with exactly this title, “Use in User Interface” on.')
s('BAUSTEIN', 'S2_SCHRITT4',
  'Im Baum diese Eingänge anlegen: einen Schieberegler „Ladeziel (Renault) (Proz)“ (Min 50, Max 100, Schritt 5, Startwert 80), zwei Schalter („Am Ladeziel anhalten (Renault)“, „Ladeplan (Renault)“) und vier Tasten („Laden anhalten“, „Laden starten“, „Klima jetzt“, „Klima aus“, je mit „(Renault)“). „Anwesenheit (eigene Quelle)“ steht schon im Baum, wenn eine andere Musterseite übernommen ist; sonst als Virtuellen Eingang anlegen.',
  'Create these inputs in the tree: one slider “Ladeziel (Renault) (Proz)” (Min 50, Max 100, step 5, start value 80), two switches (“Am Ladeziel anhalten (Renault)”, “Ladeplan (Renault)”) and four push buttons (“Laden anhalten”, “Laden starten”, “Klima jetzt”, “Klima aus”, each with “(Renault)”). “Anwesenheit (eigene Quelle)” is already in the tree if another sample page has been taken over; otherwise create it as a virtual input.')
s('BAUSTEIN', 'S2_SCHRITT5',
  'Seite „Renault NG Laden und Klima“ anlegen, alles aus der Tabelle setzen (Schaltuhr und Logik über F5) und von oben nach unten verbinden. Status „Laden (Renault)“: vorher zweimal „+“ klicken (V5, V6). In der Schaltuhr Nr. 29 Montag bis Freitag 06:40–07:00 eintragen (eigene Abfahrtszeiten); UND Nr. 31 bekommt den Ausgang AQ der Schaltuhr.',
  'Create the page “Renault NG Laden und Klima”, place everything from the table (schedule and logic via F5) and connect from top to bottom. Status “Laden (Renault)”: click “+” twice first (V5, V6). In the schedule no. 29 enter Monday to Friday 06:40–07:00 (your own departure times); AND no. 31 gets the output AQ of the schedule.')
s('BAUSTEIN', 'S2_SCHRITT6',
  'Speichern und übertragen. Probe: „Klima jetzt“ drücken. Im Plugin, Reiter „%s“, steht danach „Befehl acnow an … HTTP …“, und nach dem nächsten Abruf zeigt „Klima (Renault)“ „läuft“.',
  'Save and send to the Miniserver. Check: press “Klima jetzt”. In the plugin, tab “%s”, the line “Befehl acnow an … HTTP …” appears, and after the next retrieval “Klima (Renault)” shows “läuft”.')
s('BAUSTEIN', 'S2_H1',
  '„Am Ladeziel anhalten“ ist für Fahrzeuge ohne eigenes Ladeziel gedacht (z. B. Zoe). Neuere Modelle (Megane E-Tech, R5, R4, A290, Master) halten selbst an, wenn im Plugin ein Ladeziel eingetragen ist; der Schalter bleibt dann aus. Das Laden kann bis zum nächsten Abruf (beim Laden alle 3 Minuten) etwas über das Ziel gehen.',
  '“Am Ladeziel anhalten” is meant for vehicles without their own charge target (e.g. Zoe). Newer models (Megane E-Tech, R5, R4, A290, Master) stop by themselves when a charge target is entered in the plugin; the switch then stays off. Charging can go slightly beyond the target until the next retrieval (every 3 minutes while charging).')
s('BAUSTEIN', 'S2_H2',
  'Der Schalter „Ladeplan“ sendet nur beim Umschalten (Flankenerkennung); ein Neustart des Miniservers schaltet nichts um. Was in der My-Renault-App umgestellt wird, kennt er nicht – den echten Stand zeigt der Texteingang Nr. 6 (ChargeMode).',
  'The switch “Ladeplan” only sends when it is switched (edge detection); a restart of the Miniserver switches nothing. It does not know what is changed in the My Renault app – the real state is shown by the text input no. 6 (ChargeMode).')
s('BAUSTEIN', 'S2_H3',
  'Die Zieltemperatur der Vorklimatisierung stellt das Plugin ein (Reiter „%s“); Loxone gibt sie nicht vor, deshalb gibt es hier keinen Regler.',
  'The target temperature for preconditioning is set in the plugin (tab “%s”); Loxone does not set it, so there is no controller here.')
s('BAUSTEIN', 'S2_H4',
  'Derselbe Befehl für dasselbe Fahrzeug geht innerhalb von 60 Sekunden nur einmal ans Auto. Die Befehlstitel sind fest deutsch, auch bei englischer Oberfläche; bei mehreren Fahrzeugen steht der Fahrzeugname vorn.',
  'The same command for the same vehicle goes to the car only once within 60 seconds. The command titles are fixed German, also with an English interface; with several vehicles the vehicle name comes first.')
s('BAUSTEIN', 'S2_H5',
  'Ein Ausgangsbefehl darf in Loxone nur einmal eingefügt werden – „Daten sofort neu abrufen“ steht deshalb nur auf der Seite „Renault NG Fahrzeug“.',
  'An output command may only be inserted once in Loxone – “Daten sofort neu abrufen” is therefore only on the page “Renault NG Fahrzeug”.')
s('BAUSTEIN', 'S2_H6',
  'Wer eine Wallbox über EVCC regelt, nimmt für Ladepunkt, PV- und Preisladen die Seiten „EVCC …“; hier steht nur, was das Auto selbst kann. Beides zugleich mit einem Ladeziel einzustellen, stört sich.',
  'If you control a wallbox through EVCC, use the pages “EVCC …” for charge point, PV and price charging; this page only covers what the car itself can do. Setting a charge target in both places interferes.')
s('BAUSTEIN', 'S3_SCHRITT1',
  'Die Eingänge Nr. 1–3, 5, 6 und 12–17 wie auf Seite „Renault NG“ anlegen, Nr. 4, 7 und 18 als Virtuelle Texteingänge (Titel genau so, „In Visualisierung verwenden“ an). An Nr. 2 und 3 fünf Nachkommastellen einstellen, an Nr. 1 „Statistik“ einschalten. Dazu eine Taste „Jetzt abrufen (Renault)“.',
  'Create the inputs no. 1–3, 5, 6 and 12–17 as on page “Renault NG”, no. 4, 7 and 18 as virtual text inputs (title exactly like this, “Use in User Interface” on). Set five decimal places on no. 2 and 3, switch on “Statistics” on no. 1. Add a push button “Jetzt abrufen (Renault)”.')
s('BAUSTEIN', 'S3_SCHRITT2',
  'Seite „Renault NG Fahrzeug“ anlegen, die Bausteine der Tabelle setzen (Impuls um, Analogspeicher, Formel und Status über F5) und verbinden; der Befehl „Daten sofort neu abrufen“ kommt aus dem Behälter „Renault steuern (LoxBerry-Plugin)“. An den Status Nr. 11 und 19 je zweimal „+“ klicken (V5, V6). Den Analogspeicher mit Rem lassen (Vorgabe).',
  'Create the page “Renault NG Fahrzeug”, place the blocks of the table (Pulse at, Analog Memory, Formula and Status via F5) and connect them; the command “Daten sofort neu abrufen” comes from the container “Renault steuern (LoxBerry-Plugin)”. Click “+” twice on each of the status blocks no. 11 and 19 (V5, V6). Leave Rem on the Analog Memory (default).')
s('BAUSTEIN', 'S3_SCHRITT3',
  'Speichern und übertragen. Probe: die Taste „Jetzt abrufen (Renault)“ drücken; Kilometerstand und Position erscheinen.',
  'Save and send to the Miniserver. Check: press the button “Jetzt abrufen (Renault)”; odometer and position appear.')
s('BAUSTEIN', 'S3_H1',
  'Die Ladehistorie kommt alle 10 Minuten neu, immer der jüngste abgeschlossene Ladevorgang des letzten Monats. Generation 2 liefert oft keinen Ladestand am Anfang und Ende; dann stehen dort 0.',
  'The charging history is refreshed every 10 minutes, always the latest completed charging session of the last month. Generation 2 often delivers no state of charge at the start and end; then 0 is shown there.')
s('BAUSTEIN', 'S3_H2',
  'Generation 1 meldet keine Position, dafür die Batterietemperatur; Generation 2 umgekehrt. Der Status Nr. 11 wählt seine Zeile nach Nr. 5.',
  'Generation 1 reports no position but the battery temperature; generation 2 the other way round. Status no. 11 picks its row according to no. 5.')
s('BAUSTEIN', 'S3_H3',
  'Die Position ist eine Zahl. Seit 2.1.20 gibt es mit eingeschalteter Heimzone die Themen Zuhause (1/0/-1) und Entfernung (km).',
  'The position is a number. Since 2.1.20, with the home zone switched on, there are the topics Zuhause (1/0/-1) and Entfernung (km).')
s('BAUSTEIN', 'Z1_01',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_ok | Analog ein; Anzeigename „Abruf erfolgreich (Renault)“; 1 = letzter Abruf bei Renault gelungen, 0 = gescheitert (kommt nur bei einem echten Abruf, im Ruhezustand alle 6 Minuten) | —',
  'Virtual input (MQTT gateway) | Renault_Renault_ok | Analog on; display name “Abruf erfolgreich (Renault)”; 1 = last retrieval from Renault succeeded, 0 = failed (only comes with a real retrieval, every 6 minutes when idle) | —')
s('BAUSTEIN', 'Z1_02',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_status_zaehler | Analog ein; Anzeigename „Lebenszeichen (Renault)“; zählt bei jedem Durchgang des Plugins (alle 3 Minuten) eins weiter, 0 bis 999, läuft um | —',
  'Virtual input (MQTT gateway) | Renault_Renault_status_zaehler | Analog on; display name “Lebenszeichen (Renault)”; counts up by one with every run of the plugin (every 3 minutes), 0 to 999, wraps around | —')
s('BAUSTEIN', 'Z1_03',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_phpCall | Analog ein; Anzeigename „Letzter Abruf (Renault)“; Uhrzeit des letzten erfolgreichen Abrufs als Zahl HHMM, 1435 = 14:35 | —',
  'Virtual input (MQTT gateway) | Renault_Renault_phpCall | Analog on; display name “Letzter Abruf (Renault)”; time of the last successful retrieval as a number HHMM, 1435 = 14:35 | —')
s('BAUSTEIN', 'Z1_04',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_BattSOC | Analog ein; Anzeigename „Ladestand (Renault)“; Ladestand in %%; Statistik ein | —',
  'Virtual input (MQTT gateway) | Renault_Renault_BattSOC | Analog on; display name “Ladestand (Renault)”; state of charge in %%; statistics on | —')
s('BAUSTEIN', 'Z1_05',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_Range | Analog ein; Anzeigename „Reichweite (Renault)“; Reichweite in km; Statistik ein | —',
  'Virtual input (MQTT gateway) | Renault_Renault_Range | Analog on; display name “Reichweite (Renault)”; range in km; statistics on | —')
s('BAUSTEIN', 'Z1_06',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_ChargingStatus | Analog ein; Anzeigename „Ladestatus (Renault)“; 1 = lädt; unter 0 = Störung; andere Werte = lädt nicht | —',
  'Virtual input (MQTT gateway) | Renault_Renault_ChargingStatus | Analog on; display name “Ladestatus (Renault)”; 1 = charging; below 0 = fault; other values = not charging | —')
s('BAUSTEIN', 'Z1_07',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_CableStatus | Analog ein; Anzeigename „Ladekabel (Renault)“; 1 = Kabel eingesteckt, 0 = nicht | —',
  'Virtual input (MQTT gateway) | Renault_Renault_CableStatus | Analog on; display name “Ladekabel (Renault)”; 1 = cable plugged in, 0 = not | —')
s('BAUSTEIN', 'Z1_08',
  'Gleich | Lädt (Renault) | V2 = 1 (zweiten Eingang offen lassen; nur der Ladestatus 1 heißt „lädt“) | I1 = #6',
  'Equal | Lädt (Renault) | V2 = 1 (leave the second input open; only charging status 1 means “charging”) | I1 = #6')
s('BAUSTEIN', 'Z1_09',
  'Gleich | Ladekabel steckt (Renault) | V2 = 1 (zweiten Eingang offen lassen) | I1 = #7',
  'Equal | Ladekabel steckt (Renault) | V2 = 1 (leave the second input open) | I1 = #7')
s('BAUSTEIN', 'Z1_10',
  'Konstante | Konstante 1 | Wert 1 | —',
  'Constant | Konstante 1 | value 1 | —')
s('BAUSTEIN', 'Z1_11',
  'Analogwertvalidierung | Lebenszeichen fehlt (Renault) | Tmc 900 s (fünf Durchgänge ohne neues Lebenszeichen), Min 0, Max 999; Haken bei ‚En‘ im Eigenschaftsfenster entfernen | V = #2, En = #10',
  'Value Validator | Lebenszeichen fehlt (Renault) | Tmc 900 s (five runs without a new heartbeat), Min 0, Max 999; remove the tick at ‘En’ in the properties window | V = #2, En = #10')
s('BAUSTEIN', 'Z1_12',
  'NICHT | Keine frischen Daten (Renault) | — | I = #1',
  'NOT | Keine frischen Daten (Renault) | — | I = #1')
s('BAUSTEIN', 'Z1_13',
  'ODER | Störung (Renault) | — (keine frischen Daten oder Lebenszeichen fehlt) | I1 = #12, I2 = Ausgang E von #11',
  'OR | Störung (Renault) | — (no fresh data or heartbeat missing) | I1 = #12, I2 = output E of #11')
s('BAUSTEIN', 'Z1_14',
  'Einschaltverzögerung | Störung bestätigt (Renault) | 600 s (zwei Abfragen; ein Neustart und ein einzelner Fehlabruf melden nichts) | Eingang = #13',
  'Switch-On Delay | Störung bestätigt (Renault) | 600 s (two polls; a restart and a single failed retrieval report nothing) | Input = #13')
s('BAUSTEIN', 'Z1_15',
  'Benachrichtigung | Meldung Auto gestört (Renault) | Text: Renault NG – seit 10 Minuten kein erfolgreicher Abruf bei Renault, oder das Plugin meldet sich seit etwa 25 Minuten nicht (LoxBerry, MQTT-Gateway oder Anmeldung bei Renault). In der App den Status „Zustand (Renault)“ lesen, im Plugin den Reiter Logdateien | Eingang = #14',
  'Notification | Meldung Auto gestört (Renault) | Text: Renault NG – no successful retrieval from Renault for 10 minutes, or the plugin has not reported for about 25 minutes (LoxBerry, MQTT gateway or login at Renault). Read the status “Zustand (Renault)” in the app, in the plugin the tab Log files | Input = #14')
s('BAUSTEIN', 'Z1_16',
  'Status | Zustand (Renault) | Zeilen: V1 = 1 „das Plugin meldet sich seit mindestens 15 Minuten nicht – LoxBerry, MQTT-Gateway oder die Anmeldung bei Renault steht; im Plugin Reiter Logdateien lesen (‚LOGIN FAILED‘: Benutzer und Passwort im Reiter Einstellungen prüfen)“; V2 = 0 „letzter Abruf bei Renault gescheitert – zuletzt erfolgreich um <v3> (HHMM); im Plugin Reiter Logdateien lesen“; ohne Bedingung „läuft – letzter erfolgreicher Abruf um <v3> (HHMM, 1435 = 14:35), Lebenszeichen <v4>“; Visualisierung EIN | V1 = Ausgang E von #11, V2 = #1, V3 = #3, V4 = #2',
  'Status | Zustand (Renault) | rows: V1 = 1 “the plugin has not reported for at least 15 minutes – LoxBerry, MQTT gateway or the login at Renault is stuck; in the plugin read the tab Log files (‘LOGIN FAILED’: check user and password on the tab Settings)”; V2 = 0 “last retrieval from Renault failed – last successful at <v3> (HHMM); in the plugin read the tab Log files”; without condition “running – last successful retrieval at <v3> (HHMM, 1435 = 14:35), heartbeat <v4>”; visualisation ON | V1 = output E of #11, V2 = #1, V3 = #3, V4 = #2')
s('BAUSTEIN', 'Z1_17',
  'Formel | Ladestand für Meldung (Renault) | IF(I1>0;I1;100) – ein nie gemeldeter Ladestand (0: Verbrenner oder vor dem ersten Abruf) zählt nicht als niedrig | I1 = #4',
  'Formula | Ladestand für Meldung (Renault) | IF(I1>0;I1;100) – a state of charge never reported (0: combustion engine or before the first retrieval) does not count as low | I1 = #4')
s('BAUSTEIN', 'Z1_18',
  'Schwellwertschalter | Ladestand niedrig (Renault) | Ein 20 / Aus 25 (%%; schaltet beim Unterschreiten von 20 %% ein, über 25 %% wieder aus) | Eingang = #17',
  'Threshold Switch | Ladestand niedrig (Renault) | On 20 / Off 25 (%%; switches on when falling below 20 %%, off again above 25 %%) | Input = #17')
s('BAUSTEIN', 'Z1_19',
  'Formel | Reichweite für Meldung (Renault) | IF(I1>0;I1;999) – eine nie gemeldete Reichweite (0) zählt nicht als gering | I1 = #5',
  'Formula | Reichweite für Meldung (Renault) | IF(I1>0;I1;999) – a range never reported (0) does not count as low | I1 = #5')
s('BAUSTEIN', 'Z1_20',
  'Schwellwertschalter | Reichweite gering (Renault) | Ein 50 / Aus 70 (km; schaltet beim Unterschreiten von 50 km ein, über 70 km wieder aus) | Eingang = #19',
  'Threshold Switch | Reichweite gering (Renault) | On 50 / Off 70 (km; switches on when falling below 50 km, off again above 70 km) | Input = #19')
s('BAUSTEIN', 'Z1_21',
  'ODER | Ladestand oder Reichweite knapp (Renault) | — | I1 = #18, I2 = #20',
  'OR | Ladestand oder Reichweite knapp (Renault) | — | I1 = #18, I2 = #20')
s('BAUSTEIN', 'Z1_22',
  'UND | Knapp und nicht angesteckt (Renault) | — (I2 negiert: in Config auf den Eingangspunkt klicken, es erscheint ein kleiner Kreis; am Ladekabel meldet nichts) | I1 = #21, I2 = #9 (negiert)',
  'AND | Knapp und nicht angesteckt (Renault) | — (I2 negated: click the input point in Config, a small circle appears; nothing is reported while the charging cable is plugged in) | I1 = #21, I2 = #9 (negated)')
s('BAUSTEIN', 'Z1_23',
  'Einschaltverzögerung | Knapp bestätigt (Renault) | 600 s (schluckt den kurzen Impuls der Schwellwertschalter bei jeder Abfrage) | Eingang = #22',
  'Switch-On Delay | Knapp bestätigt (Renault) | 600 s (swallows the short pulse of the threshold switches at every poll) | Input = #22')
s('BAUSTEIN', 'Z1_24',
  'Benachrichtigung | Meldung Ladestand niedrig (Renault) | Text: Renault NG – Ladestand unter 20 %% oder Reichweite unter 50 km, und das Auto ist nicht angesteckt. Bitte laden; Werte in der App unter „Ladestand und Reichweite (Renault)“ | Eingang = #23',
  'Notification | Meldung Ladestand niedrig (Renault) | Text: Renault NG – state of charge below 20 %%, or range below 50 km, and the car is not plugged in. Please charge; values in the app under “Ladestand und Reichweite (Renault)” | Input = #23')
s('BAUSTEIN', 'Z1_25',
  'Status | Ladestand und Reichweite (Renault) | Zeilen: V5 = 1 „Ladestörung – <v1.0> %%, Reichweite <v2.0> km; Kabel und Ladestation prüfen“; V3 = 1 „lädt – <v1.0> %%, Reichweite <v2.0> km“; V6 = 1 „knapp – <v1.0> %%, nur noch <v2.0> km – bitte anstecken“; V4 = 1 „angesteckt, lädt nicht – <v1.0> %%, Reichweite <v2.0> km (Ladeplan wartet oder Ladeziel erreicht)“; ohne Bedingung „<v1.0> %%, Reichweite <v2.0> km – nicht angesteckt“; Visualisierung EIN | V1 = #4, V2 = #5, V3 = #8, V4 = #9, V5 = #30, V6 = #23',
  'Status | Ladestand und Reichweite (Renault) | rows: V5 = 1 “charging fault – <v1.0> %%, range <v2.0> km; check cable and charging station”; V3 = 1 “charging – <v1.0> %%, range <v2.0> km”; V6 = 1 “low – <v1.0> %%, only <v2.0> km left – please plug in”; V4 = 1 “plugged in, not charging – <v1.0> %%, range <v2.0> km (charging schedule waiting or charge target reached)”; without condition “<v1.0> %%, range <v2.0> km – not plugged in”; visualisation ON | V1 = #4, V2 = #5, V3 = #8, V4 = #9, V5 = #30, V6 = #23')
s('BAUSTEIN', 'Z1_26',
  'Einschaltverzögerung | Lädt seit einer Minute (Renault) | 60 s (erst eine echte Ladung zählt; ein kurzer Ausreißer meldet kein Ladeende) | Eingang = #8',
  'Switch-On Delay | Lädt seit einer Minute (Renault) | 60 s (only a real charge counts; a short outlier reports no end of charging) | Input = #8')
s('BAUSTEIN', 'Z1_27',
  'Flankenerkennung | Ladung endet (Renault) | Pd 1 s; benutzt wird der Ausgang Off (fallende Flanke) | Eingang = #26',
  'Edge Detection | Ladung endet (Renault) | Pd 1 s; the output Off (falling edge) is used | Input = #26')
s('BAUSTEIN', 'Z1_28',
  'Benachrichtigung | Meldung Ladung beendet (Renault) | Text: Renault NG – die Ladung ist beendet (Ladeziel erreicht, Ladeplan pausiert oder Kabel gezogen). Ladestand in der App unter „Ladestand und Reichweite (Renault)“ | Eingang = Ausgang Off von #27',
  'Notification | Meldung Ladung beendet (Renault) | Text: Renault NG – charging has ended (charge target reached, charging schedule paused or cable pulled). State of charge in the app under “Ladestand und Reichweite (Renault)” | Input = output Off of #27')
s('BAUSTEIN', 'Z1_29',
  'Kleiner | Auto meldet Ladestörung (Renault) | V2 = 0 (zweiten Eingang offen lassen; Ladestatus unter 0 = Störung) | I1 = #6',
  'Less | Auto meldet Ladestörung (Renault) | V2 = 0 (leave the second input open; charging status below 0 = fault) | I1 = #6')
s('BAUSTEIN', 'Z1_30',
  'UND | Ladestörung am Kabel (Renault) | — (nur bei gestecktem Kabel) | I1 = #29, I2 = #9',
  'AND | Ladestörung am Kabel (Renault) | — (only with the cable plugged in) | I1 = #29, I2 = #9')
s('BAUSTEIN', 'Z1_31',
  'Einschaltverzögerung | Ladestörung bestätigt (Renault) | 600 s | Eingang = #30',
  'Switch-On Delay | Ladestörung bestätigt (Renault) | 600 s | Input = #30')
s('BAUSTEIN', 'Z1_32',
  'Benachrichtigung | Meldung Ladestörung (Renault) | Text: Renault NG – das Auto meldet seit 10 Minuten eine Ladestörung, das Kabel steckt. Kabel, Ladestation und deren Sicherung prüfen; in der App den Status „Ladestand und Reichweite (Renault)“ lesen | Eingang = #31',
  'Notification | Meldung Ladestörung (Renault) | Text: Renault NG – the car has been reporting a charging fault for 10 minutes, the cable is plugged in. Check cable, charging station and its fuse; read the status “Ladestand und Reichweite (Renault)” in the app | Input = #31')
s('BAUSTEIN', 'Z2_01',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_ChargingStatus | Analog ein; Anzeigename „Ladestatus (Renault)“; 1 = lädt (weitere Instanz, auch auf Seite „Renault NG“) | —',
  'Virtual input (MQTT gateway) | Renault_Renault_ChargingStatus | Analog on; display name “Ladestatus (Renault)”; 1 = charging (further instance, also on page “Renault NG”) | —')
s('BAUSTEIN', 'Z2_02',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_BattSOC | Analog ein; Anzeigename „Ladestand (Renault)“; Ladestand in %% (weitere Instanz) | —',
  'Virtual input (MQTT gateway) | Renault_Renault_BattSOC | Analog on; display name “Ladestand (Renault)”; state of charge in %% (further instance) | —')
s('BAUSTEIN', 'Z2_03',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_ChargingTime | Analog ein; Anzeigename „Restladezeit (Renault)“; Restdauer der Ladung in min | —',
  'Virtual input (MQTT gateway) | Renault_Renault_ChargingTime | Analog on; display name “Restladezeit (Renault)”; remaining charging time in min | —')
s('BAUSTEIN', 'Z2_04',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_ChargingEffekt | Analog ein; Anzeigename „Ladeleistung (Renault)“; Ladeleistung in kW; Statistik ein | —',
  'Virtual input (MQTT gateway) | Renault_Renault_ChargingEffekt | Analog on; display name “Ladeleistung (Renault)”; charging power in kW; statistics on | —')
s('BAUSTEIN', 'Z2_05',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_EnergieOnBoard | Analog ein; Anzeigename „Energie im Akku (Renault)“; verfügbare Energie in kWh (nur Generation 2) | —',
  'Virtual input (MQTT gateway) | Renault_Renault_EnergieOnBoard | Analog on; display name “Energie im Akku (Renault)”; available energy in kWh (generation 2 only) | —')
s('BAUSTEIN', 'Z2_06',
  'Virtueller Texteingang | Renault_Renault_ChargeMode | Titel genau so (Name, den das MQTT-Gateway vergibt), „In Visualisierung verwenden“ an; always_charging = immer laden, schedule_mode = Ladeplan, n/a = kennt das Fahrzeug nicht | —',
  'Virtual text input | Renault_Renault_ChargeMode | title exactly like this (the name the MQTT gateway gives), “Use in User Interface” on; always_charging = always charge, schedule_mode = charging schedule, n/a = the vehicle does not know it | —')
s('BAUSTEIN', 'Z2_07',
  'Gleich | Lädt gerade (Renault) | V2 = 1 (zweiten Eingang offen lassen) | I1 = #1',
  'Equal | Lädt gerade (Renault) | V2 = 1 (leave the second input open) | I1 = #1')
s('BAUSTEIN', 'Z2_08',
  'Status | Laden (Renault) | Zeilen: V1 = 1 „lädt mit <v2.1> kW – <v5.0> %% (Ziel <v6.0> %%), fertig in etwa <v3> min; <v4.1> kWh im Akku“; V1 < 0 „Ladestörung – das Auto meldet einen Fehler beim Laden“; ohne Bedingung „lädt nicht – <v5.0> %% (Ziel <v6.0> %%), <v4.1> kWh im Akku“; Visualisierung EIN | V1 = #1, V2 = #4, V3 = #3, V4 = #5, V5 = #2, V6 = #9',
  'Status | Laden (Renault) | rows: V1 = 1 “charging at <v2.1> kW – <v5.0> %% (target <v6.0> %%), finished in about <v3> min; <v4.1> kWh in the battery”; V1 < 0 “charging fault – the car reports an error while charging”; without condition “not charging – <v5.0> %% (target <v6.0> %%), <v4.1> kWh in the battery”; visualisation ON | V1 = #1, V2 = #4, V3 = #3, V4 = #5, V5 = #2, V6 = #9')
s('BAUSTEIN', 'Z2_09',
  'Virtueller Eingang (Schieberegler) | Ladeziel (Renault) (Proz) | in der App; Min 50, Max 100, Schritt 5, Startwert 80 | —',
  'Virtual input (slider) | Ladeziel (Renault) (Proz) | in the app; Min 50, Max 100, step 5, start value 80 | —')
s('BAUSTEIN', 'Z2_10',
  'Größer oder gleich | Ladeziel erreicht (Renault) | — (Ladestand ≥ Ladeziel) | I1 = #2, I2 = #9',
  'Greater or Equal | Ladeziel erreicht (Renault) | — (state of charge ≥ charge target) | I1 = #2, I2 = #9')
s('BAUSTEIN', 'Z2_11',
  'Virtueller Eingang (Schalter) | Am Ladeziel anhalten (Renault) | in der App; ab Werk aus. Ein = Loxone hält das Laden am Ladeziel an; für Fahrzeuge, die kein eigenes Ladeziel kennen (z. B. Zoe) | —',
  'Virtual input (switch) | Am Ladeziel anhalten (Renault) | in the app; off by default. On = Loxone stops charging at the charge target; for vehicles that do not know their own charge target (e.g. Zoe) | —')
s('BAUSTEIN', 'Z2_12',
  'UND | Ladeziel beim Laden erreicht (Renault) | — | I1 = #10, I2 = #7',
  'AND | Ladeziel beim Laden erreicht (Renault) | — | I1 = #10, I2 = #7')
s('BAUSTEIN', 'Z2_13',
  'UND | Ladeziel-Stopp freigegeben (Renault) | — | I1 = #12, I2 = #11',
  'AND | Ladeziel-Stopp freigegeben (Renault) | — | I1 = #12, I2 = #11')
s('BAUSTEIN', 'Z2_14',
  'Einschaltverzögerung | Ladeziel-Stopp bestätigt (Renault) | 60 s (schluckt ein Verstellen des Reglers) | Eingang = #13',
  'Switch-On Delay | Ladeziel-Stopp bestätigt (Renault) | 60 s (swallows an adjustment of the slider) | Input = #13')
s('BAUSTEIN', 'Z2_15',
  'Virtueller Eingang (Taste) | Laden anhalten (Renault) | in der App | —',
  'Virtual input (push button) | Laden anhalten (Renault) | in the app | —')
s('BAUSTEIN', 'Z2_16',
  'ODER | Laden anhalten angefordert (Renault) | — (Taste oder Ladeziel) | I1 = #15, I2 = #14',
  'OR | Laden anhalten angefordert (Renault) | — (button or charge target) | I1 = #15, I2 = #14')
s('BAUSTEIN', 'Z2_17',
  'Virtueller Ausgang Befehl (Vorlage „Renault steuern (LoxBerry-Plugin)“) | Laden anhalten | hält das Laden an; schaltende Befehle im Plugin freigeben (Reiter Einstellungen, Abschnitt Schalten) | Eingang = #16',
  'Virtual output command (template “Renault steuern (LoxBerry-Plugin)”) | Laden anhalten | stops charging; release switching commands in the plugin (tab Settings, section Switching) | Input = #16')
s('BAUSTEIN', 'Z2_18',
  'Virtueller Eingang (Taste) | Laden starten (Renault) | in der App; lädt sofort, auch gegen den Ladeplan | —',
  'Virtual input (push button) | Laden starten (Renault) | in the app; charges immediately, even against the charging schedule | —')
s('BAUSTEIN', 'Z2_19',
  'Virtueller Ausgang Befehl (Vorlage „Renault steuern (LoxBerry-Plugin)“) | Sofort laden starten | — | Eingang = #18',
  'Virtual output command (template “Renault steuern (LoxBerry-Plugin)”) | Sofort laden starten | — | Input = #18')
s('BAUSTEIN', 'Z2_20',
  'Virtueller Eingang (Schalter) | Ladeplan (Renault) | in der App; Ein = nach dem Ladeplan des Autos laden, Aus = immer laden; ab Werk aus | —',
  'Virtual input (switch) | Ladeplan (Renault) | in the app; On = charge according to the charging schedule of the car, Off = always charge; off by default | —')
s('BAUSTEIN', 'Z2_21',
  'Flankenerkennung | Ladeplan umgeschaltet (Renault) | Pd 1 s; Ausgang On beim Einschalten, Off beim Ausschalten | Eingang = #20',
  'Edge Detection | Ladeplan umgeschaltet (Renault) | Pd 1 s; output On when switching on, Off when switching off | Input = #20')
s('BAUSTEIN', 'Z2_22',
  'Virtueller Ausgang Befehl (Vorlage „Renault steuern (LoxBerry-Plugin)“) | Ladeplan aktivieren | — | Eingang = Ausgang On von #21',
  'Virtual output command (template “Renault steuern (LoxBerry-Plugin)”) | Ladeplan aktivieren | — | Input = output On of #21')
s('BAUSTEIN', 'Z2_23',
  'Virtueller Ausgang Befehl (Vorlage „Renault steuern (LoxBerry-Plugin)“) | Ladeplan abschalten (immer laden) | — | Eingang = Ausgang Off von #21',
  'Virtual output command (template “Renault steuern (LoxBerry-Plugin)”) | Ladeplan abschalten (immer laden) | — | Input = output Off of #21')
s('BAUSTEIN', 'Z2_24',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_HvAcStatusBin | Analog ein; Anzeigename „Vorklimatisierung (Renault)“; 1 = läuft, 0 = aus | —',
  'Virtual input (MQTT gateway) | Renault_Renault_HvAcStatusBin | Analog on; display name “Vorklimatisierung (Renault)”; 1 = running, 0 = off | —')
s('BAUSTEIN', 'Z2_25',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_InTemp | Analog ein; Anzeigename „Innentemperatur (Renault)“; °C (nicht jedes Fahrzeug liefert sie) | —',
  'Virtual input (MQTT gateway) | Renault_Renault_InTemp | Analog on; display name “Innentemperatur (Renault)”; °C (not every vehicle provides it) | —')
s('BAUSTEIN', 'Z2_26',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_OutTemp | Analog ein; Anzeigename „Außentemperatur (Renault)“; °C, vom Fahrzeug, ersatzweise vom Wetterdienst | —',
  'Virtual input (MQTT gateway) | Renault_Renault_OutTemp | Analog on; display name “Außentemperatur (Renault)”; °C, from the vehicle, otherwise from the weather service | —')
s('BAUSTEIN', 'Z2_27',
  'Status | Klima (Renault) | Zeilen: V1 = 1 „Vorklimatisierung läuft – innen <v2.1> °C, außen <v3.1> °C“; ohne Bedingung „Vorklimatisierung aus – innen <v2.1> °C, außen <v3.1> °C (die Innentemperatur liefert nicht jedes Fahrzeug)“; Visualisierung EIN | V1 = #24, V2 = #25, V3 = #26',
  'Status | Klima (Renault) | rows: V1 = 1 “preconditioning running – inside <v2.1> °C, outside <v3.1> °C”; without condition “preconditioning off – inside <v2.1> °C, outside <v3.1> °C (not every vehicle provides the interior temperature)”; visualisation ON | V1 = #24, V2 = #25, V3 = #26')
s('BAUSTEIN', 'Z2_28',
  'Virtueller Eingang (Taste) | Klima jetzt (Renault) | in der App; startet die Klimatisierung mit der Zieltemperatur aus dem Plugin | —',
  'Virtual input (push button) | Klima jetzt (Renault) | in the app; starts climate control with the target temperature from the plugin | —')
s('BAUSTEIN', 'Z2_29',
  'Schaltuhr | Abfahrt vorklimatisieren (Renault) | EIN = vorklimatisieren: Montag bis Freitag 06:40–07:00 (20 Minuten vor der Abfahrt um 07:00; eigene Abfahrtszeiten eintragen) | —',
  'Schedule | Abfahrt vorklimatisieren (Renault) | ON = precondition: Monday to Friday 06:40–07:00 (20 minutes before departure at 07:00; enter your own departure times) | —')
s('BAUSTEIN', 'Z2_30',
  'Virtueller Eingang | Anwesenheit (eigene Quelle) | 1 = jemand zu Hause (weitere Instanz, derselbe Eingang wie auf „Saugroboter“, „Chromecast4lox“, „Abfahrtsassistent“); im eigenen Projekt aus der eigenen Anwesenheit speisen | —',
  'Virtual input | Anwesenheit (eigene Quelle) | 1 = somebody at home (further instance, the same input as on “Saugroboter”, “Chromecast4lox”, “Abfahrtsassistent”); in your own project feed it from your own presence detection | —')
s('BAUSTEIN', 'Z2_31',
  'UND | Vorklimatisieren nur bei Anwesenheit (Renault) | — (im Urlaub klimatisiert nichts) | I1 = Ausgang AQ von #29, I2 = #30',
  'AND | Vorklimatisieren nur bei Anwesenheit (Renault) | — (nothing is preconditioned during holidays) | I1 = output AQ of #29, I2 = #30')
s('BAUSTEIN', 'Z2_32',
  'ODER | Klima anfordern (Renault) | — (Taste oder Schaltuhr) | I1 = #28, I2 = #31',
  'OR | Klima anfordern (Renault) | — (button or schedule) | I1 = #28, I2 = #31')
s('BAUSTEIN', 'Z2_33',
  'Virtueller Ausgang Befehl (Vorlage „Renault steuern (LoxBerry-Plugin)“) | Vorklimatisierung starten | Zieltemperatur aus dem Plugin (Reiter Einstellungen, ab Werk 21 °C); nur Einbefehl | Eingang = #32',
  'Virtual output command (template “Renault steuern (LoxBerry-Plugin)”) | Vorklimatisierung starten | target temperature from the plugin (tab Settings, 21 °C by default); on command only | Input = #32')
s('BAUSTEIN', 'Z2_34',
  'Virtueller Eingang (Taste) | Klima aus (Renault) | in der App; hält die Klimatisierung an | —',
  'Virtual input (push button) | Klima aus (Renault) | in the app; stops climate control | —')
s('BAUSTEIN', 'Z2_35',
  'Virtueller Ausgang Befehl (Vorlage „Renault steuern (LoxBerry-Plugin)“) | Vorklimatisierung beenden | nur Einbefehl | Eingang = #34',
  'Virtual output command (template “Renault steuern (LoxBerry-Plugin)”) | Vorklimatisierung beenden | on command only | Input = #34')
s('BAUSTEIN', 'Z3_01',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_Mileage | Analog ein; Anzeigename „Kilometerstand (Renault)“; km; Statistik ein | —',
  'Virtual input (MQTT gateway) | Renault_Renault_Mileage | Analog on; display name “Kilometerstand (Renault)”; km; statistics on | —')
s('BAUSTEIN', 'Z3_02',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_GPS-Latitude | Analog ein; Anzeigename „Breitengrad (Renault)“; fünf Nachkommastellen; nur Generation 2 | —',
  'Virtual input (MQTT gateway) | Renault_Renault_GPS-Latitude | Analog on; display name “Breitengrad (Renault)”; five decimal places; generation 2 only | —')
s('BAUSTEIN', 'Z3_03',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_GPS-Longitude | Analog ein; Anzeigename „Längengrad (Renault)“; fünf Nachkommastellen; nur Generation 2 | —',
  'Virtual input (MQTT gateway) | Renault_Renault_GPS-Longitude | Analog on; display name “Längengrad (Renault)”; five decimal places; generation 2 only | —')
s('BAUSTEIN', 'Z3_04',
  'Virtueller Texteingang | Renault_Renault_GPSTime | Titel genau so (Name, den das MQTT-Gateway vergibt), „In Visualisierung verwenden“ an; Uhrzeit der letzten Positionsmeldung, HH:MM | —',
  'Virtual text input | Renault_Renault_GPSTime | title exactly like this (the name the MQTT gateway gives), “Use in User Interface” on; time of the last position report, HH:MM | —')
s('BAUSTEIN', 'Z3_05',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_RenaultPHMode | Analog ein; Anzeigename „Fahrzeuggeneration (Renault)“; 1 oder 2, wie im Plugin eingestellt | —',
  'Virtual input (MQTT gateway) | Renault_Renault_RenaultPHMode | Analog on; display name “Fahrzeuggeneration (Renault)”; 1 or 2, as set in the plugin | —')
s('BAUSTEIN', 'Z3_06',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_BatTemp | Analog ein; Anzeigename „Batterietemperatur (Renault)“; °C; kommt nur bei Generation 1, sonst bleibt der Eingang leer | —',
  'Virtual input (MQTT gateway) | Renault_Renault_BatTemp | Analog on; display name “Batterietemperatur (Renault)”; °C; only comes with generation 1, otherwise the input stays empty | —')
s('BAUSTEIN', 'Z3_07',
  'Virtueller Texteingang | Renault_Renault_Name | Titel genau so (Name, den das MQTT-Gateway vergibt), „In Visualisierung verwenden“ an; Fahrzeugname aus dem Plugin | —',
  'Virtual text input | Renault_Renault_Name | title exactly like this (the name the MQTT gateway gives), “Use in User Interface” on; vehicle name from the plugin | —')
s('BAUSTEIN', 'Z3_08',
  'Impuls um | Tagesbeginn 0:00 (Renault) | Zu bestimmter Uhrzeit, 00:00:00 | —',
  'Pulse at | Tagesbeginn 0:00 (Renault) | at a specific time, 00:00:00 | —')
s('BAUSTEIN', 'Z3_09',
  'Analogspeicher | Kilometerstand um Mitternacht (Renault) | übernimmt um 0:00 den Kilometerstand; Rem ein (Vorgabe), damit der Stand einen Neustart übersteht | V = #1, Set = Ausgang Q von #8',
  'Analog Memory | Kilometerstand um Mitternacht (Renault) | takes over the odometer reading at 0:00; Rem on (default), so that the value survives a restart | V = #1, Set = output Q of #8')
s('BAUSTEIN', 'Z3_10',
  'Formel | Heute gefahren in km (Renault) | IF(I2>0;IF(I1>=I2;I1-I2;0);0) – Kilometerstand minus Stand um Mitternacht; nach einem Neustart des Miniservers bis Mitternacht 0 | I1 = #1, I2 = #9',
  'Formula | Heute gefahren in km (Renault) | IF(I2>0;IF(I1>=I2;I1-I2;0);0) – odometer minus the reading at midnight; 0 until midnight after a restart of the Miniserver | I1 = #1, I2 = #9')
s('BAUSTEIN', 'Z3_11',
  'Status | Standort und Kilometer (Renault) | Zeilen: V5 = 1 „<v1.0> km, heute <v2.0> km gefahren – Batterie <v6.1> °C (Generation 1 meldet keine Position)“; ohne Bedingung „<v1.0> km, heute <v2.0> km gefahren – Position <v3.5>, <v4.5>“; Visualisierung EIN | V1 = #1, V2 = #10, V3 = #2, V4 = #3, V5 = #5, V6 = #6',
  'Status | Standort und Kilometer (Renault) | rows: V5 = 1 “<v1.0> km, <v2.0> km driven today – battery <v6.1> °C (generation 1 reports no position)”; without condition “<v1.0> km, <v2.0> km driven today – position <v3.5>, <v4.5>”; visualisation ON | V1 = #1, V2 = #10, V3 = #2, V4 = #3, V5 = #5, V6 = #6')
s('BAUSTEIN', 'Z3_12',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_chargeStartBatteryLevel(Prozent) | Analog ein; Anzeigename „Ladevorgang Start (Proz) (Renault)“; Ladestand am Anfang der letzten Ladung in %% | —',
  'Virtual input (MQTT gateway) | Renault_Renault_chargeStartBatteryLevel(Prozent) | Analog on; display name “Ladevorgang Start (Proz) (Renault)”; state of charge at the start of the last charge in %% | —')
s('BAUSTEIN', 'Z3_13',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_chargeEndBatteryLevel(Prozent) | Analog ein; Anzeigename „Ladevorgang Ende (Proz) (Renault)“; Ladestand am Ende der letzten Ladung in %% | —',
  'Virtual input (MQTT gateway) | Renault_Renault_chargeEndBatteryLevel(Prozent) | Analog on; display name “Ladevorgang Ende (Proz) (Renault)”; state of charge at the end of the last charge in %% | —')
s('BAUSTEIN', 'Z3_14',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_chargeDuration(min) | Analog ein; Anzeigename „Ladevorgang Dauer (Renault)“; Dauer der letzten Ladung in min | —',
  'Virtual input (MQTT gateway) | Renault_Renault_chargeDuration(min) | Analog on; display name “Ladevorgang Dauer (Renault)”; duration of the last charge in min | —')
s('BAUSTEIN', 'Z3_15',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_chargeEnergyRecovered(kWh) | Analog ein; Anzeigename „Ladevorgang Energie (Renault)“; geladene Energie der letzten Ladung in kWh | —',
  'Virtual input (MQTT gateway) | Renault_Renault_chargeEnergyRecovered(kWh) | Analog on; display name “Ladevorgang Energie (Renault)”; energy charged in the last charge in kWh | —')
s('BAUSTEIN', 'Z3_16',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_chargePowerAverage(kW) | Analog ein; Anzeigename „Ladevorgang Leistung (Renault)“; mittlere Leistung der letzten Ladung in kW | —',
  'Virtual input (MQTT gateway) | Renault_Renault_chargePowerAverage(kW) | Analog on; display name “Ladevorgang Leistung (Renault)”; average power of the last charge in kW | —')
s('BAUSTEIN', 'Z3_17',
  'Virtueller Eingang (MQTT-Gateway) | Renault_Renault_chargeStartInstantaneousPower | Analog ein; Anzeigename „Ladevorgang Startleistung (Renault)“; Leistung beim Anstecken in W | —',
  'Virtual input (MQTT gateway) | Renault_Renault_chargeStartInstantaneousPower | Analog on; display name “Ladevorgang Startleistung (Renault)”; power when plugged in, in W | —')
s('BAUSTEIN', 'Z3_18',
  'Virtueller Texteingang | Renault_Renault_chargeEndStatus | Titel genau so (Name, den das MQTT-Gateway vergibt), „In Visualisierung verwenden“ an; Abschlussmeldung der letzten Ladung, wie Renault sie liefert | —',
  'Virtual text input | Renault_Renault_chargeEndStatus | title exactly like this (the name the MQTT gateway gives), “Use in User Interface” on; final status of the last charge as Renault delivers it | —')
s('BAUSTEIN', 'Z3_19',
  'Status | Letzter Ladevorgang (Renault) | Zeilen: V3 = 0 „im letzten Monat kein abgeschlossener Ladevorgang gemeldet (nicht jedes Fahrzeug kennt die Ladehistorie)“; ohne Bedingung „<v1.0> %% → <v2.0> %% in <v3> min; <v4.1> kWh, im Mittel <v5.1> kW (beim Anstecken <v6.0> W)“; Visualisierung EIN | V1 = #12, V2 = #13, V3 = #14, V4 = #15, V5 = #16, V6 = #17',
  'Status | Letzter Ladevorgang (Renault) | rows: V3 = 0 “no completed charging session reported in the last month (not every vehicle knows the charging history)”; without condition “<v1.0> %% → <v2.0> %% in <v3> min; <v4.1> kWh, on average <v5.1> kW (<v6.0> W when plugged in)”; visualisation ON | V1 = #12, V2 = #13, V3 = #14, V4 = #15, V5 = #16, V6 = #17')
s('BAUSTEIN', 'Z3_20',
  'Virtueller Eingang (Taste) | Jetzt abrufen (Renault) | in der App; holt sofort neue Werte statt auf den Takt zu warten (höchstens einmal je Minute) | —',
  'Virtual input (push button) | Jetzt abrufen (Renault) | in the app; fetches new values immediately instead of waiting for the interval (at most once per minute) | —')
s('BAUSTEIN', 'Z3_21',
  'Virtueller Ausgang Befehl (Vorlage „Renault steuern (LoxBerry-Plugin)“) | Daten sofort neu abrufen | geht auch bei ausgeschalteter Steuerung | Eingang = #20',
  'Virtual output command (template “Renault steuern (LoxBerry-Plugin)”) | Daten sofort neu abrufen | also works with switching disabled | Input = #20')

# --------------------------------------------------------------------- ALLG
# NEU (Drift-Abgleich 06.11.2026): Abschnitt aus Renault NG 2.1.30 wortgleich uebernommen.
s('ALLG', 'EIN',
  'ein',
  'on')
s('ALLG', 'AUS',
  'aus',
  'off')
s('ALLG', 'NICHT_FESTSTELLBAR',
  'nicht feststellbar',
  'cannot be determined')
s('ALLG', 'KACHEL_MQTT_HILFE',
  'Veröffentlichung dieses Plugins (ohne eigenen Schalter: an, sobald ein Broker eingerichtet ist); Autostart des Gateways: %s; Gateway-Fassung: %s',
  'Publishing of this plugin (no own switch: on as soon as a broker is set up); gateway autostart: %s; gateway version: %s')

# --------------------------------------------------------------------- HAUS
# NEU (Drift-Abgleich 06.11.2026): Abschnitt aus Renault NG 2.1.30 wortgleich uebernommen.
s('HAUS', 'H',
  'Haus-Themen: Ankunft und Ladekosten',
  'House topics: arrival and charging costs')
s('HAUS', 'H_TEXT',
  "Das Plugin liest Haus-Themen anderer Plugins über das MQTT-Gateway (Nr. 15) mit einem abgekoppelten Leser – es schreibt nichts unter <span class='sm-mono'>haus/</span>. Alles ab Werk aus.",
  "The plugin reads house topics of other plugins via the MQTT gateway (no. 15) with a decoupled reader – it writes nothing under <span class='sm-mono'>haus/</span>. Everything off by default.")
s('HAUS', 'L_ABFAHRT_EIN',
  'Minuten bis zur Abfahrt aus dem Haus-Thema (haus/abfahrt)',
  'Minutes until departure from the house topic (haus/abfahrt)')
s('HAUS', 'L_ANWESEND_EIN',
  'Vorklimatisierung nur, wenn jemand zu Hause ist (haus/anwesenheit/jemand)',
  'Pre-conditioning only when someone is at home (haus/anwesenheit/jemand)')
s('HAUS', 'L_ANKUNFT_EIN',
  'Bei Ankunft sofort abfragen (höchstens einmal je 30 min und Fahrzeug)',
  'Fetch immediately on arrival (at most once per 30 min and vehicle)')
s('HAUS', 'L_STROMPREIS_EIN',
  'Strompreis vom Spotpreis-Plugin für die Ladekosten (haus/strompreis)',
  'Electricity price from the spot price plugin for the charging costs (haus/strompreis)')
s('HAUS', 'L_ANKUNFT_QUELLE',
  'Ankunftsquelle',
  'Arrival source')
s('HAUS', 'H_ANKUNFT_QUELLE',
  "<span class='sm-mono'>tag:&lt;name&gt;</span> (BLE-Tag im Auto, haus/tag/&lt;name&gt;/da – empfohlen) oder <span class='sm-mono'>person:&lt;name&gt;</span> (haus/anwesenheit/&lt;name&gt;); leer = keine Ankunftsabfrage für dieses Fahrzeug. Ein Wechsel live von 0 auf 1 fragt das Fahrzeug einmal ab, nur wenn der letzte Abruf älter als 5 Minuten ist.",
  "<span class='sm-mono'>tag:&lt;name&gt;</span> (BLE tag in the car, haus/tag/&lt;name&gt;/da – recommended) or <span class='sm-mono'>person:&lt;name&gt;</span> (haus/anwesenheit/&lt;name&gt;); empty = no arrival query for this vehicle. A live change from 0 to 1 queries the vehicle once, only if the last retrieval is older than 5 minutes.")
s('HAUS', 'L_AKKU_KWH',
  'Nutzbare Akkukapazität in kWh (nur für die Ladekosten)',
  'Usable battery capacity in kWh (for the charging costs only)')
s('HAUS', 'H_AKKU_KWH',
  'Nur nötig, wenn das Fahrzeug die Energie im Akku nicht meldet (Generation 1 und manche Modelle). Leer: dann bleiben die Kosten ohne Aussage.',
  'Only needed if the vehicle does not report the energy in the battery (generation 1 and some models). Empty: the costs then have no statement.')
s('HAUS', 'H_KOSTEN',
  "Rechenweg: Renault liefert die Ladeleistung nicht im Minutentakt. Die Energie je Abschnitt zwischen zwei Abrufen kommt aus der vom Fahrzeug <b>gemeldeten Energie im Akku</b>, sonst aus der <b>Akkustand-Differenz × eingetragener Kapazität</b>; jede Minute trägt den Preis, den das Plugin in ihr aus <span class='sm-mono'>haus/strompreis</span> mitschreibt (Endpreis ohne Grundpreis). Gerechnet wird die in den Akku geladene Energie, <b>ohne Ladeverluste</b>. Kosten -1, wenn die Energie nicht bestimmbar ist, der Preis für mehr als 10 Prozent der Energie fehlt oder die Ladung nicht zu Hause begann (Heimzone) – <b>nie geschätzt</b>.",
  "Calculation: Renault does not report the charging power every minute. The energy per section between two retrievals comes from the <b>energy in the battery reported by the vehicle</b>, otherwise from the <b>charge level difference × entered capacity</b>; every minute carries the price the plugin records in it from <span class='sm-mono'>haus/strompreis</span> (final price without base fee). Calculated is the energy charged into the battery, <b>without charging losses</b>. Costs -1 if the energy cannot be determined, the price is missing for more than 10 percent of the energy or the charge did not start at home (home zone) – <b>never estimated</b>.")
s('HAUS', 'H_LADUNGEN',
  'Ladekosten der letzten Ladungen',
  'Charging costs of the last charges')
s('HAUS', 'H_KEINE_LADUNG',
  'Noch keine Ladung abgeschlossen.',
  'No charge completed yet.')
s('HAUS', 'S_ENDE',
  'Ende',
  'End')
s('HAUS', 'S_KWH',
  'Akku (kWh)',
  'Battery (kWh)')
s('HAUS', 'S_PREIS',
  'Ø Preis (ct/kWh)',
  'Ø price (ct/kWh)')
s('HAUS', 'S_KOSTEN',
  'Kosten (€)',
  'Cost (€)')
s('HAUS', 'S_GRUND',
  'Grund',
  'Reason')
s('HAUS', 'Q_ABFAHRT',
  'Haus-Thema Abfahrt (haus/abfahrt)',
  'House topic departure (haus/abfahrt)')
s('HAUS', 'Q_ANWESENHEIT',
  'Haus-Thema Anwesenheit (haus/anwesenheit)',
  'House topic presence (haus/anwesenheit)')
s('HAUS', 'Q_STROMPREIS',
  'Haus-Thema Strompreis (haus/strompreis)',
  'House topic electricity price (haus/strompreis)')
s('HAUS', 'FRISCH',
  'frisch (Zähler vor %d s)',
  'fresh (counter %d s ago)')
s('HAUS', 'SCHWEIGT',
  'schweigt seit %s – es gilt %s',
  'silent for %s – %s applies')
s('HAUS', 'NIE',
  'dem Start (noch nie live gesehen)',
  'the start (never seen live)')
s('HAUS', 'RUECK_ABFAHRT',
  'keine Vorklimatisierung durch das Plugin (Weg ohne Haus-Thema: Schaltuhr in Loxone)',
  'no pre-conditioning by the plugin (path without house topic: timer in Loxone)')
s('HAUS', 'RUECK_ANWESENHEIT',
  'Anwesenheit nicht gesetzt (Vorklimatisierung wie ohne diesen Haken), keine Ankunftsabfrage',
  'presence not set (pre-conditioning as without this checkbox), no arrival query')
s('HAUS', 'RUECK_STROMPREIS',
  'Kosten -1 (kein Preis)',
  'costs -1 (no price)')
s('HAUS', 'LESER',
  'Leser der Haus-Themen',
  'Reader of the house topics')
s('HAUS', 'KEIN_MOSQUITTO',
  'mosquitto_sub fehlt (Paket mosquitto-clients) – es gilt das bisherige Verhalten',
  'mosquitto_sub missing (package mosquitto-clients) – the previous behaviour applies')

# ----------------------------------------------------------------- VORKLIMA
# NEU (Drift-Abgleich 06.11.2026): Abschnitt aus Renault NG 2.1.30 wortgleich uebernommen.
s('VORKLIMA', 'H',
  'Vorklimatisierung zur Abfahrt',
  'Pre-conditioning for departure')
s('VORKLIMA', 'H_EINE_QUELLE',
  '<b>Nur eine Quelle nutzen:</b> Schaltuhr in Loxone <b>oder</b> dieser Haken – sonst kommen zwei Befehle.',
  '<b>Use only one source:</b> timer in Loxone <b>or</b> this checkbox – otherwise two commands arrive.')
s('VORKLIMA', 'H_TEXT',
  "Löst bei frischem Haus-Thema <span class='sm-mono'>haus/abfahrt</span> (Abfahrts-Assistent) und 1 ≤ Minuten bis zur Abfahrt ≤ Vorlauf die Vorklimatisierung aus – <b>höchstens zwei</b> Klima-ein je Abfahrt (Senden – Abruf – Senden), danach eine LoxBerry-Benachrichtigung. Wirkt nur mit eingeschalteter <i>Steuerung</i>, dem Haken für das Haus-Thema Abfahrt und Zugangsdaten. Schweigt das Haus-Thema oder kommt -1, klimatisiert das Plugin <b>nicht</b>.",
  "Triggers pre-conditioning with a fresh house topic <span class='sm-mono'>haus/abfahrt</span> (departure assistant) and 1 ≤ minutes to departure ≤ lead time – <b>at most two</b> climate-on per departure (send – retrieve – send), then a LoxBerry notification. Works only with <i>Switching</i> on, the checkbox for the departure house topic and credentials. If the house topic is silent or reports -1, the plugin does <b>not</b> pre-condition.")
s('VORKLIMA', 'L_EIN',
  'Vorklimatisierung zur Abfahrt (ab Werk aus)',
  'Pre-conditioning for departure (off by default)')
s('VORKLIMA', 'L_WETTER_EIN',
  'Nur bei Kälte oder Hitze (Wettergrenze)',
  'Only when cold or hot (weather limit)')
s('VORKLIMA', 'L_VORLAUF',
  'Vorlauf in Minuten (5–60)',
  'Lead time in minutes (5–60)')
s('VORKLIMA', 'L_FAHRZEUGE',
  'Fahrzeuge (Nummern, z. B. 1 oder 1,2)',
  'Vehicles (numbers, e.g. 1 or 1,2)')
s('VORKLIMA', 'L_KALT',
  'Kalt unter (°C)',
  'Cold below (°C)')
s('VORKLIMA', 'L_HEISS',
  'Heiß über (°C)',
  'Hot above (°C)')
s('VORKLIMA', 'H_WETTER',
  "Wettergrenze: zuerst die Außentemperatur aus Loxone (<span class='sm-mono'>Renault/befehl/aussentemp</span>, höchstens 30 min alt), sonst die des Fahrzeugs (aus einem Abruf, höchstens 60 min alt). Liegt sie zwischen Kalt und Heiß, unterbleibt die Vorklimatisierung (Vorklima 2). Ohne Aussage wird klimatisiert.",
  "Weather limit: first the outside temperature from Loxone (<span class='sm-mono'>Renault/befehl/aussentemp</span>, at most 30 min old), otherwise the vehicle's (from a retrieval at most 60 min old). If it lies between cold and hot, pre-conditioning is skipped (Vorklima 2). Without a statement it pre-conditions.")
s('VORKLIMA', 'F_GRENZEN',
  'Wettergrenze: <b>Kalt unter</b> muss kleiner sein als <b>Heiß über</b>.',
  'Weather limit: <b>cold below</b> must be lower than <b>hot above</b>.')
s('VORKLIMA', 'GESCHEITERT',
  'Vorklimatisierung für %s gescheitert',
  'Pre-conditioning for %s failed')

# --------------------------------------------------------------------- HEIM
# NEU (Drift-Abgleich 06.11.2026): Abschnitt aus Renault NG 2.1.30 wortgleich uebernommen.
s('HEIM', 'H',
  'Heimzone',
  'Home zone')
s('HEIM', 'H_TEXT',
  "Gilt nur für Fahrzeuge der Generation 2, die eine Position melden. Das Plugin sendet <span class='sm-mono'>Zuhause</span> (1/0/-1, retained) und <span class='sm-mono'>Entfernung</span> (km). Die Position gilt, solange sie höchstens 60 Minuten älter ist als die letzte Antwort des Fahrzeugs. Die Koordinaten stehen in der Konfiguration, die nur das Plugin lesen kann. Weist das Speichern ein Feld ab, liegen sie kurz in einer ebenso geschützten Hilfsdatei, bis die Seite neu geladen ist. Ins Protokoll und an MQTT kommen sie nie.",
  "Applies only to generation 2 vehicles that report a position. The plugin sends <span class='sm-mono'>Zuhause</span> (1/0/-1, retained) and <span class='sm-mono'>Entfernung</span> (km). The position applies as long as it is at most 60 minutes older than the last vehicle response. The coordinates are stored in the configuration, which only the plugin can read. If saving rejects a field, they stay briefly in an equally protected helper file until the page has reloaded. They never go to the log or to MQTT.")
s('HEIM', 'L_EIN',
  'Heimzone auswerten (ab Werk aus)',
  'Evaluate home zone (off by default)')
s('HEIM', 'L_BREITE',
  'Breitengrad des Hauses',
  'Latitude of the house')
s('HEIM', 'KARTE',
  'Karte öffnen (mapatlas.eu): Adresse eingeben, die Zahlen unter „Dezimalgrad“ kopieren',
  'Open the map (mapatlas.eu): enter the address, copy the numbers under „Decimal degrees“')
s('HEIM', 'KARTE_ZUSAMMEN',
  'Beide Zahlen dürfen auch zusammen hier hinein (etwa 50.123, 8.456); das Plugin teilt sie beim Speichern auf.',
  'Both numbers may also be pasted here together (e.g. 50.123, 8.456); the plugin splits them when saving.')
s('HEIM', 'L_LAENGE',
  'Längengrad des Hauses',
  'Longitude of the house')
s('HEIM', 'H_PUNKT',
  'Punkt als Dezimaltrenner, bis 8 Nachkommastellen, z. B. 48.1234 und 11.5678.',
  'Dot as decimal separator, up to 8 decimal places, e.g. 48.1234 and 11.5678.')
s('HEIM', 'L_RADIUS',
  'Radius in Metern (20–20000)',
  'Radius in metres (20–20000)')
s('HEIM', 'F_PUNKT_FEHLT',
  'Heimzone: ohne <b>Breitengrad</b> und <b>Längengrad</b> lässt sie sich nicht einschalten.',
  'Home zone: it cannot be switched on without <b>latitude</b> and <b>longitude</b>.')
s('HEIM', 'ZU_HAUSE',
  'zu Hause',
  'at home')
s('HEIM', 'UNTERWEGS',
  'unterwegs',
  'away')
s('HEIM', 'OHNE_AUSSAGE',
  'ohne Aussage',
  'no statement')

# ------------------------------------------------------------------- SIGNAL
# NEU (Drift-Abgleich 06.11.2026): Abschnitt aus Renault NG 2.1.30 wortgleich uebernommen.
s('SIGNAL', 'H',
  'Meldungen an SignalBot',
  'Messages to SignalBot')
s('SIGNAL', 'H_TEXT',
  "Sendet die Meldungen <i>Akkustand erreicht</i> und <i>Ladung beendet</i> zusätzlich über die Brücke des Plugins SignalBot (<span class='sm-mono'>&lt;Präfix&gt;/befehl/plugin/renault_ng</span>, nie retained). Wirkt nur, wenn SignalBot den Absender <span class='sm-mono'>renault_ng</span> freigibt (dort unter Einstellungen <i>Meldungen anderer Plugins annehmen von</i>). Ist die Vorklimatisierung an, geht mit einem der beiden Haken auch <i>Vorklimatisierung gescheitert</i> dorthin.",
  "Additionally sends the messages <i>charge level reached</i> and <i>charging finished</i> via the bridge of the SignalBot plugin (<span class='sm-mono'>&lt;prefix&gt;/befehl/plugin/renault_ng</span>, never retained). Works only if SignalBot allows the sender <span class='sm-mono'>renault_ng</span> (there under settings <i>accept messages of other plugins from</i>). If pre-conditioning is on, either checkbox also sends <i>pre-conditioning failed</i> there.")
s('SIGNAL', 'L_BL',
  'Akkustand erreicht an SignalBot (ab Werk aus)',
  'Charge level reached to SignalBot (off by default)')
s('SIGNAL', 'L_CSF',
  'Ladung beendet an SignalBot (ab Werk aus)',
  'Charging finished to SignalBot (off by default)')
s('SIGNAL', 'L_PRAEFIX',
  'Präfix des SignalBot',
  'SignalBot prefix')
s('SIGNAL', 'H_PRAEFIX',
  'Wie im SignalBot eingestellt (ab Werk signalbot). Das Plugin liest keine fremde Konfiguration.',
  'As set in SignalBot (default signalbot). The plugin reads no foreign configuration.')
s('SIGNAL', 'H_TEST',
  'SignalBot',
  'SignalBot')
s('SIGNAL', 'H_TEST_TEXT',
  'Sendet einen festen Satz an SignalBot und liest dessen Quittung bis 5 Sekunden. Mit Freigabe im SignalBot kommt eine echte Nachricht aufs Handy.',
  'Sends a fixed sentence to SignalBot and reads its acknowledgement for up to 5 seconds. With approval in SignalBot a real message arrives on the phone.')
s('SIGNAL', 'K_TEST',
  'Testmeldung an SignalBot',
  'Test message to SignalBot')
s('SIGNAL', 'TESTSATZ',
  'Testmeldung des Plugins Renault NG.',
  'Test message of the Renault NG plugin.')
s('SIGNAL', 'T_ANGENOMMEN',
  'SignalBot: angenommen.',
  'SignalBot: accepted.')
s('SIGNAL', 'T_ABGELEHNT',
  'SignalBot: %s – im SignalBot unter Einstellungen „Meldungen anderer Plugins annehmen von“ renault_ng anhaken.',
  'SignalBot: %s – in SignalBot under settings “accept messages of other plugins from” tick renault_ng.')
s('SIGNAL', 'T_KEINE_ANTWORT',
  'SignalBot: keine Antwort – SignalBot nicht installiert oder seine Brücke aus.',
  'SignalBot: no answer – SignalBot not installed or its bridge off.')
s('SIGNAL', 'T_NICHT_MOEGLICH',
  'SignalBot: nicht möglich – mosquitto-Programme, Broker oder ein gültiger Ordnername/Präfix fehlen.',
  'SignalBot: not possible – mosquitto programs, broker or a valid folder name/prefix missing.')


NUR_TEXT = ('REITER', 'LEGENDE', 'THEMA', 'BEFEHL', 'FELD', 'PRUEF')
# Ausnahmen von NUR_TEXT, je Schluessel (Drift-Abgleich 06.11.2026): diese drei Werte tragen in
# Renault NG 2.1.30 Auszeichnung und werden in webfrontend/htmlauth/index.php OHNE rn_e()
# ausgegeben - gemessen: BEFEHL.H_UDP Z. 1699 und 1783, BEFEHL.H_QUITTUNG Z. 1731,
# BEFEHL.SCHRITT_TEXT Z. 1782, jeweils "echo rn_t('...')". Das Verbot fuer den ganzen
# Abschnitt traf sie mit und hielt sie aus der Tabelle.
ROH_AUSGEGEBEN = ('BEFEHL.H_UDP', 'BEFEHL.H_QUITTUNG', 'BEFEHL.SCHRITT_TEXT')


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
    """Der Abschnitt [ANSAGE] der gemeinsamen Sprachausgabe (Nr. 36 b) - EINE Quelle:
    Werkzeuge/gemeinsam_pruefen.py baut ihn aus Werkzeuge/gemeinsam/sprachausgabe_texte.json. Gesucht wird
    aufwaerts vom Ablageort dieses Erzeugers."""
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


def ansage_schluessel():
    """Die Schluessel von [ANSAGE] als ANSAGE.<name> (fuer die Wache wuerde_verlieren())."""
    aus = set()
    for z in ansage_abschnitt("de").splitlines():
        if "=" in z and not z.startswith("["):
            aus.add("ANSAGE." + z.split("=", 1)[0].strip())
    return aus


def bauen(spalte):
    """Der Inhalt einer Sprachdatei; bricht ab, bevor irgendetwas geschrieben ist.

    Werkzeug-S4 (02.10.2026): bis dahin baute und schrieb schreiben() in einem
    Zug - language_de.ini stand schon auf der Platte, wenn die Pruefung eines
    englischen Wertes abbrach."""
    aus = []
    # Reihenfolge wie in der ausgelieferten .ini (20.09.2026); CSV und
    # PRUEFTEXT kamen dort dazu, ohne dass dieser Schreibteil sie kannte.
    for abschnitt in ('REITER', 'LEGENDE', 'THEMA', 'BEFEHL', 'FELD', 'MELDUNG', 'PRUEF', 'TEXT', 'CSV', 'PRUEFTEXT', 'BAUSTEIN', 'ALLG', 'HAUS', 'VORKLIMA', 'HEIM', 'SIGNAL'):
        aus.append('[%s]' % abschnitt)
        for schluessel, de, en in T[abschnitt]:
            wert = de if spalte == 'de' else en
            # HTML-Attribute in den Texten einfach quotieren. Ein doppeltes
            # Anfuehrungszeichen im Wert beendet fuer parse_ini_file die
            # Zeichenkette; der Rest der Zeile ginge verloren. HTML erlaubt
            # beide Formen, also nehmen wir die, die hier durchgeht.
            wert = wert.replace('="', "='").replace('">', "'>")
            if (abschnitt in NUR_TEXT and '%s.%s' % (abschnitt, schluessel) not in ROH_AUSGEGEBEN
                    and ('&' in wert or '<' in wert)):
                raise SystemExit(
                    'Auszeichnung oder Entitaet in %s.%s: %r - dieser Abschnitt '
                    'geht durch rn_e() und wuerde doppelt maskiert.'
                    % (abschnitt, schluessel, wert))
            if '"' in wert:
                raise SystemExit('Anfuehrungszeichen im Wert %s.%s: %r'
                                 % (abschnitt, schluessel, wert))
            aus.append('%s = "%s"' % (schluessel, wert))
        aus.append('')
    # Nr. 36 b: der Abschnitt der gemeinsamen Sprachausgabe zuletzt.
    aus.append(ansage_abschnitt(spalte).rstrip('\n'))
    aus.append('')
    return '\n'.join(aus)


def schreiben(pfad, text):
    # newline ausdruecklich: ohne die Angabe uebersetzt Windows still
    # jedes \n zu \r\n. Bis 13.09.2026 stand hier '\r\n'.
    with io.open(pfad, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)
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
eigene = {'%s.%s' % (a, s) for a in T for s, _d, _e in T[a]} | ansage_schluessel()
for datei in ('language_de.ini', 'language_en.ini'):
    weg = wuerde_verlieren(os.path.join(ziel, datei), eigene)
    if weg:
        print('[FEHL] ABGEWIESEN - es wurde nichts geschrieben.')
        print('       %s wuerde %d Schluessel verlieren:' % (datei, len(weg)))
        for x in weg:
            print('           ' + x)
        sys.exit(1)
# Werkzeug-S4: erst beide Inhalte bauen (jede Pruefung bricht hier ab, bevor
# etwas geschrieben ist), dann die Sprachwache vorab ueber beide, dann schreiben.
text_de, text_en = bauen('de'), bauen('en')
sprachwache.pruefen(os.path.join(ziel, 'language_de.ini'), text_de)
sprachwache.pruefen(os.path.join(ziel, 'language_en.ini'), text_en)
n1 = schreiben(os.path.join(ziel, 'language_de.ini'), text_de)
n2 = schreiben(os.path.join(ziel, 'language_en.ini'), text_en)
print('Geschrieben, je %d Schluessel:' % n1)
print('  ' + os.path.join(ziel, 'language_de.ini'))
print('  ' + os.path.join(ziel, 'language_en.ini'))
