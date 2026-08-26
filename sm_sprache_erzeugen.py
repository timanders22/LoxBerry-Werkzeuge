#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Erzeugt language_de.ini und language_en.ini von Smartmeter classic aus
EINER Quelle.

WARUM ES DIESEN ERZEUGER GIBT
-----------------------------
Mit 2.3.14 hat das Plugin ueber 440 Schluessel in zwei Sprachen. Zwei
Dateien von Hand gleichzuhalten geht eine Weile gut und dann nicht mehr:
es fehlt ein Schluessel auf einer Seite, und die Oberflaeche zeigt dort
den SCHLUESSELNAMEN statt eines Textes - ohne Fehlermeldung, ohne Eintrag
im Protokoll. Hier steht jedes Paar an EINER Stelle; das Auseinanderlaufen
ist damit nicht mehr moeglich.

WER EINE SPRACHDATEI VON HAND AENDERT, ZIEHT DIESEN ERZEUGER MIT. Sonst
gibt es zwei Wahrheiten im selben Archiv, und die eine loescht die andere
beim naechsten Lauf. Der Kopf der erzeugten Dateien sagt das auch dort.

REGELN FUER JEDEN WERT
----------------------
* Echte Umlaute, keine HTML-Entitaeten. Die meisten Texte laufen durch
  sm_e(); ein notiertes &uuml; erschiene beim Leser woertlich.
* Attribute in Auszeichnung EINFACH quotieren (class='sm-mono'). Ein
  zweites doppeltes Anfuehrungszeichen beendet den Wert vorzeitig - je
  nach Lesemodus abgeschnitten oder die ganze Datei abgewiesen, und
  beides still. Der Erzeuger bricht deshalb ab, statt es zu schreiben.
* Typografische Anfuehrungszeichen, nie gerade.
* Ein %s im Text braucht an der Aufrufstelle ein Argument und umgekehrt.
  Nachgemessen wird das nicht hier, sondern von
  Werkzeuge/sprachplatzhalter_pruefen.py - es liest die AUFRUFSTELLE und
  nicht eine zweite gepflegte Liste.

DREI FAMILIEN, DIE EINE SUCHE NACH sm_t('...') NICHT FINDET
-----------------------------------------------------------
    [FELD]        kommt aus bin/sm_felder.json ueber sm_feld()['bed']
    [OBIS]        dasselbe fuer die Kennzahlen
    SUCHE.W_*     kommt aus sm_suche_wege() ueber sm_t($w['bez'])

Wer hier einen davon streicht, bekommt keinen Fehler, sondern einen
Schluesselnamen in einer Tabelle. Werkzeuge/sprachschluessel_pruefen.py
prueft solche Familien eigens mit.

Aufruf:  python3 Werkzeuge/sm_sprache_erzeugen.py [<Plugin-Ordner>]
Rueckgabe 0, wenn beide Dateien geschrieben wurden.
"""

import re
import sys
from pathlib import Path

VORGABE = (Path(__file__).resolve().parent.parent
           / "LoxBerry-Plugin-Smartmeter-classic-2.4.0")

# ======================================================================
# Die Texte. Je Eintrag: (Schluessel, deutsch, englisch)
# ======================================================================

TEXTE = [
 ('ALLG', [
  ('TITEL',
   'Smartmeter',
   'Smartmeter'),
  ('SPEICHERN',
   'Speichern',
   'Save'),
  ('NICHT_GESPEICHERT',
   'Nicht gespeichert:',
   'Not saved:'),
  ('GERAET',
   'Gerät',
   'Device'),
  ('KEINES',
   'keines',
   'none'),
  ('WERT',
   'Wert',
   'Value'),
  ('GROESSE',
   'Größe',
   'Quantity'),
  ('EINHEIT',
   'Einheit',
   'Unit'),
  ('BEDEUTUNG',
   'Bedeutung',
   'Meaning'),
  ('AUSGABE',
   'Ausgabe',
   'Output'),
  ('KEINE_AUSGABE',
   'keine Ausgabe',
   'no output'),
  ('VORGABE',
   'Vorgabe',
   'Default'),
  ('OPTIONAL',
   'optional',
   'optional'),
  ('UDPPORT',
   'UDP-Port',
   'UDP port'),
  ('UDP_ZUSAETZLICH',
   'zusätzlich per UDP senden',
   'also send via UDP'),

  ('JA', "ja", "yes"),
  ('NEIN', "nein", "no"),
  ('UNBEKANNT', "ließ sich nicht feststellen", "could not be determined"),
  ('TEXTFELD', "Textfeld", "text field"),
  ('AUSWAHLFELD',
   "Nur angesteckte Leseköpfe stehen zur Wahl. Fehlt der eigene, hilft "
   "Abziehen und neu Anstecken — die udev-Regel legt das Plugin beim Start an.",
   "Only reading heads that are plugged in can be chosen. If yours is "
   "missing, unplug it and plug it in again — the plugin creates the udev "
   "rule at startup."),
 ]),
 ('TAB', [
  ('VZ',
   'Smartmeter (vzLogger)',
   'Smartmeter (vzLogger)'),
  ('LEGACY',
   'Smartmeter (klassisch)',
   'Smartmeter (classic)'),
  ('MQTT',
   'MQTT',
   'MQTT'),
  ('LOXONE',
   'Einbindung in Loxone',
   'Loxone integration'),
  ('TEST',
   'Test',
   'Test'),
  ('LOG',
   'Logdateien',
   'Log files'),
 ]),
 ('MELD', [
  ('GESPEICHERT',
   'Gespeichert.',
   'Saved.'),
  ('VZ_GESPEICHERT',
   'Gespeichert. Die Konfiguration wurde neu erzeugt.',
   'Saved. The configuration was rebuilt.'),
  ('VZ_GESPEICHERT_NEUSTART',
   'Gespeichert. Die Konfiguration wurde neu erzeugt und vzlogger neu gestartet.',
   'Saved. The configuration was rebuilt and vzlogger restarted.'),
  ('VZ_NEUSTART',
   'vzlogger wurde neu gestartet.',
   'vzlogger has been restarted.'),
  ('MQTT_GESPEICHERT',
   'Die MQTT-Einstellungen wurden gespeichert.',
   'The MQTT settings have been saved.'),
  ('CACHE',
   'Zwischenspeicher geleert (%s Datei(en) entfernt).',
   'Cache cleared (%s file(s) removed).'),

  ('ERGAENZT',  # (1) Liste der ergaenzten Schluessel
   "In der Konfiguration fehlten Schlüssel; sie wurden mit der Vorgabe "
   "ergänzt und einmalig gespeichert: %s",
   "Keys were missing from the configuration; they have been filled in with "
   "their default and saved once: %s"),
 ]),
 ('FEHLER', [
  ('BAUDRATE',
   'Die Baudrate ist eine Zahl zwischen 300 und 921600.',
   'The baud rate must be a number between 300 and 921600.'),
  ('RAHMUNG',
   'Die Zeichenrahmung muss 8n1, 7n1, 7e1 oder 8e1 sein.',
   'The character framing must be 8n1, 7n1, 7e1 or 8e1.'),
  ('PORT',
   'Der %s-Port ist eine Zahl zwischen 1 und 65535.',
   'The %s port must be a number between 1 and 65535.'),
  ('OBIS',
   'Der Kanal %s sieht nicht wie eine OBIS-Kennzahl aus.',
   'The channel %s does not look like an OBIS code.'),
  ('SCHREIBEN',
   'Die Datei %s ließ sich nicht schreiben.',
   'The file %s could not be written.'),
  ('SCHREIBEN_TEIL',
   'Die Datei %s ließ sich nicht vollständig schreiben.',
   'The file %s could not be written completely.'),
  ('SCHREIBEN_RECHTE',
   'Die Datei %s ließ sich nicht schreiben. Rechte im Konfigurationsordner prüfen.',
   'The file %s could not be written. Check the permissions of the configuration folder.'),
  ('TAKT',
   'Der Abfragetakt muss aus der Liste gewählt werden.',
   'The polling interval must be chosen from the list.'),
  ('LG_UDPPORT',
   'Der UDP-Port des klassischen Lesers ist eine Zahl zwischen 1 und 65535.',
   'The UDP port of the classic reader must be a number between 1 and 65535.'),
  ('BEIDE_LESER',
   'vzLogger ist eingeschaltet. Bitte dort zuerst abschalten – beide Leser greifen auf dieselbe serielle Schnittstelle zu.',
   'vzLogger is switched on. Please turn it off there first – both readers use the same serial interface.'),
  ('PROFIL',
   'Unbekanntes Zählerprofil für %s.',
   'Unknown meter profile for %s.'),

  ('CSRF',
   "Das Formular trug kein gültiges Merkmal. Es wurde nichts geändert. "
   "Bitte die Seite neu laden und noch einmal absenden.",
   "The form did not carry a valid marker. Nothing has been changed. Please "
   "reload the page and submit again."),
  ('CSRF_KEIN_MERKMAL',
   "Es ließ sich kein Formularmerkmal erzeugen — die Konfigurationsdatei ist "
   "vermutlich nicht beschreibbar. Solange das so ist, nimmt diese Seite "
   "keine Änderung an.",
   "No form marker could be created — the configuration file is probably not "
   "writable. As long as that is the case, this page accepts no changes."),
  ('BEIDE_LESER_VZ',
   "Der klassische Leser ist eingeschaltet. Bitte dort zuerst abschalten — "
   "beide Leser greifen auf dieselbe serielle Schnittstelle zu.",
   "The classic reader is switched on. Please switch it off there first — "
   "both readers access the same serial port."),
 ]),
 ('VZ', [
  ('H_ZUSTAND',
   'Zustand',
   'Status'),
  ('H_INSTALLAUSGABE',
   'Ausgabe der Installation',
   'Installation output'),
  ('H_LESEWEG',
   'Leseweg',
   'Reading path'),
  ('H_LESEKOPF',
   'Lesekopf',
   'Optical head'),
  ('H_KANAELE',
   'Kanäle',
   'Channels'),
  ('H_WEITERGABE',
   'Weitergabe',
   'Forwarding'),
  ('K_INSTALL',
   'vzlogger installieren',
   'Install vzlogger'),
  ('K_NEUSTART',
   'vzlogger neu starten',
   'Restart vzlogger'),
  ('K_SPEICHERN',
   'Speichern und vzlogger neu starten',
   'Save and restart vzlogger'),
  ('LABEL_ENABLED',
   'vzLogger einschalten',
   'Enable vzLogger'),
  ('LABEL_PROTOCOL',
   'Protokoll',
   'Protocol'),
  ('LABEL_BAUDRATE',
   'Baudrate',
   'Baud rate'),
  ('LABEL_PARITY',
   'Zeichenrahmung',
   'Character framing'),
  ('LABEL_LOCALTIME',
   'Zeitstempel',
   'Timestamp'),
  ('LABEL_CHANNELS',
   'OBIS-Kennzahlen, eine je Zeile',
   'OBIS codes, one per line'),
  ('LABEL_SERIAL',
   'Zählernummer',
   'Meter number'),
  ('LABEL_HTTPPORT',
   'HTTP-Port von vzlogger',
   'HTTP port of vzlogger'),
  ('OPT_SML',
   'SML – der Zähler sendet von selbst',
   'SML – the meter sends on its own'),
  ('OPT_D0',
   'D0 – der Zähler muss gefragt werden',
   'D0 – the meter has to be asked'),
  ('OPT_LOKALZEIT',
   'Rechner-Uhrzeit (empfohlen)',
   'Computer clock (recommended)'),
  ('OPT_ZAEHLERZEIT',
   'Uhr des Zählers',
   'Clock of the meter'),
  ('NICHT_VORHANDEN',
   'derzeit nicht vorhanden',
   'currently not present'),
  ('HINT_EINLESER',
   'Es darf immer nur <b>ein</b> Leser laufen. Ist die klassische Abfrage eingeschaltet, belegt sie dieselbe serielle Schnittstelle – die Diagnose oben weist darauf hin.',
   'Only <b>one</b> reader may run at a time. If the classic reader is switched on, it occupies the same serial interface – the diagnosis above points this out.'),
  ('HINT_BAUDRATE',
   '9600 bei SML, oft 300 bei D0.',
   '9600 for SML, often 300 for D0.'),
  ('HINT_LOCALTIME',
   'Viele Haushaltszähler senden keine gestellte Uhr. vzlogger verwirft solche Telegramme dann mit %s – der Zähler wird gelesen, aber kein einziger Wert kommt an.',
   'Many household meters do not send a set clock. vzlogger then discards such telegrams with %s – the meter is read, but not a single value arrives.'),
  ('HINT_SERIAL',
   'Erscheint im MQTT-Thema und im UDP-Satz.',
   'Appears in the MQTT topic and in the UDP record.'),
  ('HINT_UDP',
   'MQTT ist der Regelweg. UDP nur, wo Werte anders nicht ankommen.',
   'MQTT is the normal path. Use UDP only where values do not arrive otherwise.'),
  ('HINT_HTTPPORT',
   'Über diesen Port holt das Plugin die Messwerte ab. Nur ändern, wenn der Port schon belegt ist.',
   'The plugin fetches the readings through this port. Change it only if the port is already in use.'),
  ('WARN_KEINKOPF',
   'Es wurde kein Lesekopf erkannt (%s). Lesekopf abziehen und neu anstecken – die udev-Regel wird beim Start des Plugins angelegt.',
   'No optical head was detected (%s). Unplug the head and plug it in again – the udev rule is created when the plugin starts.'),

  ('KEIN_VZLOGGER',  # (1) Architektur
   "vzlogger ist nicht installiert (%s).",
   "vzlogger is not installed (%s)."),
  ('NICHT_AUSFUEHRBAR',  # (1) Pfad
   "%s ist vorhanden, lässt sich aber nicht ausführen.",
   "%s exists but cannot be executed."),
  ('STARTET_NICHT_RC',  # (2) Rückgabewert, Ausgabe
   "Rückgabewert %s, Ausgabe: %s",
   "Return code %s, output: %s"),
  ('VORHANDEN_STARTET_NICHT',  # (1) Pfad
   "%s ist vorhanden, meldet aber keine Fassung.",
   "%s exists but does not report a version."),
  ('PAKETHELFER_FEHLT',  # (1) Pfad
   "Der Installationshelfer %s fehlt. Ohne ihn lässt sich vzlogger von hier "
   "aus nicht einrichten.",
   "The installation helper %s is missing. Without it vzlogger cannot be set "
   "up from here."),
  ('START_GEFALLEN',
   "Der Start wurde angestoßen, der Prozess war danach aber nicht zu finden. "
   "Das Protokoll unten sagt, woran es lag.",
   "The start was triggered, but the process could not be found afterwards. "
   "The log below says why."),
 ]),
 ('LG', [
  ('ABFRAGE_ZEITGRENZE',
   'Die Abfrage wurde nach %d Sekunden abgebrochen. Der Lesekopf antwortet nicht — Steckverbindung, Zählerprofil und die Ausrichtung des Kopfes auf der Zähler-Schnittstelle prüfen.',
   'The query was cancelled after %d seconds. The reading head is not answering — check the plug, the meter profile and how the head sits on the meter interface.'),
  ('H_LESER',
   'Der klassische Leser',
   'The classic reader'),
  ('H_ABFRAGE',
   'Abfrage',
   'Polling'),
  ('H_KOEPFE',
   'Leseköpfe',
   'Optical heads'),
  ('H_WIE',
   'Wie der Leser arbeitet',
   'How the reader works'),
  ('K_SPEICHERN',
   'Speichern und Abfragetakt setzen',
   'Save and set polling interval'),
  ('K_ABFRAGEN',
   'Jetzt einmal abfragen',
   'Poll once now'),
  ('K_CACHE',
   'Zwischenspeicher leeren',
   'Clear cache'),
  ('LABEL_ENABLED',
   'Klassischen Leser einschalten',
   'Enable classic reader'),
  ('LABEL_TAKT',
   'Abfragetakt',
   'Polling interval'),
  ('LABEL_NAME',
   'Bezeichnung',
   'Label'),
  ('LABEL_PROFIL',
   'Zählerprofil',
   'Meter profile'),
  ('HINT_LESER',
   'Fragt den Zähler über ein <b>Zählerprofil</b> ab – 41 Modelle sind hinterlegt. Der Weg ist älter als vzLogger, funktioniert aber auch dort, wo vzLogger nichts liefert.',
   'Polls the meter using a <b>meter profile</b> – 41 models are included. This path is older than vzLogger, but it also works where vzLogger delivers nothing.'),
  ('HINT_TAKT',
   'Der Takt <i>nur beim Systemstart</i> liefert genau eine Ablesung je Neustart des LoxBerry und danach keine mehr. Bis 2.3.14 hiess er „dauerhaft“ und versprach das Gegenteil.',
   'The cycle <i>only at system start</i> yields exactly one reading per reboot of the LoxBerry and none after that. Up to 2.3.14 it was called „continuous“ and promised the opposite.'),
  ('HINT_MQTT',
   'MQTT wird im Reiter <i>MQTT</i> eingestellt – er gilt für beide Lesewege.',
   'MQTT is configured on the <i>MQTT</i> tab – it applies to both reading paths.'),
  ('WARN_EINLESER',
   'Es darf immer nur ein Leser laufen. Beide greifen auf dieselbe serielle Schnittstelle zu.',
   'Only one reader may run at a time. Both use the same serial interface.'),
  ('WARN_KEINKOPF',
   'Es ist kein Lesekopf eingerichtet. Lesekopf anstecken und die Seite neu laden – er wird dann selbständig eingetragen.',
   'No optical head is configured. Plug in a head and reload the page – it will then be registered automatically.'),
  ('VZ_AN',
   'vzLogger ist derzeit <b>eingeschaltet</b> – bitte zuerst dort abschalten.',
   'vzLogger is currently <b>switched on</b> – please turn it off there first.'),
  ('VZ_AUS',
   'vzLogger ist derzeit ausgeschaltet.',
   'vzLogger is currently switched off.'),
  ('LAEUFT',
   'Der Leser läuft gerade (PID %s).',
   'The reader is running (PID %s).'),
  ('LAEUFT_NICHT',
   'Der Leser läuft gerade nicht.',
   'The reader is not running.'),
  ('TAKT_LAUT_LINK',
   'Abfragetakt laut Verknüpfung',
   'Polling interval according to the cron link'),
  ('KEIN_TAKT',
   'keine eingerichtet',
   'none configured'),
  ('NICHT_ANGESTECKT',
   'derzeit nicht angesteckt',
   'currently not plugged in'),
  ('ZULETZT',
   'Zuletzt gelesen',
   'Last reading'),
  ('FETCH_FEHLT',
   'fetch.php wurde nicht gefunden (%s).',
   'fetch.php was not found (%s).'),
  ('TEXT_WIE',
   'Die Oberfläche und der Abholer (%s) sind PHP. Der eigentliche Leser %s ist bewusst Perl geblieben: er spricht über %s mit dem Zähler und wechselt bei D0-Zählern mitten in der Sitzung die Baudrate. Dafür gibt es in PHP kein verlässliches Gegenstück, und die 41 Profile ließen sich ohne 41 Zähler auch nicht nachprüfen.',
   'The user interface and the fetcher (%s) are PHP. The reader itself, %s, has deliberately stayed Perl: it talks to the meter through %s and switches the baud rate mid-session on D0 meters. There is no dependable PHP equivalent for that, and the 41 profiles could not have been verified without 41 meters either.'),
 ]),
 ('MQ', [
  ('W_AUTOSTART',
   'Das MQTT-Gateway steht nicht auf Autostart (System → MQTT Gateway). Es wird gesendet, aber vermutlich hört niemand zu.',
   'The MQTT gateway is not set to autostart (System → MQTT Gateway). Data is being sent, but most likely nobody is listening.'),
  ('H_ZUSTAND',
   'Zustand des MQTT-Gateways',
   'State of the MQTT gateway'),
  ('H_EINSTELLUNGEN',
   'Einstellungen',
   'Settings'),
  ('H_ABO',
   'Das einzutragende Abo',
   'The subscription to enter'),
  ('H_THEMEN',
   'Veröffentlichte Themen',
   'Published topics'),
  ('LABEL_AN',
   'Werte per MQTT senden',
   'Send values via MQTT'),
  ('LABEL_TOPIC',
   'Themenpräfix',
   'Topic prefix'),
  ('SP_THEMA',
   'Thema',
   'Topic'),
  ('HINT_GATEWAY',
   'Das MQTT-Gateway ist seit LoxBerry&nbsp;3 <b>Bestandteil des Systems</b> und kein Plugin. Es wird unter <i>System → MQTT Gateway</i> eingerichtet.',
   'Since LoxBerry&nbsp;3 the MQTT gateway is <b>part of the system</b>, not a plugin. It is set up under <i>System → MQTT Gateway</i>.'),
  ('HINT_EINZIGE',
   'Dies ist die <b>einzige</b> Stelle, an der MQTT eingestellt wird – beide Lesewege benutzen sie.',
   'This is the <b>only</b> place where MQTT is configured – both reading paths use it.'),
  ('ABO_WO',
   'Einzutragen unter <i>System → MQTT Gateway → Abonnements</i>',
   'To be entered under <i>System → MQTT Gateway → Subscriptions</i>'),

  ('Z_AUTOSTART', "Autostart", "Autostart"),
  ('Z_FASSUNG', "Fassung des Gateways", "Gateway version"),
  ('Z_UDPIN', "UDP-Eingang des Gateways", "UDP input of the gateway"),
  # DIE DREI SAETZE ZUR GATEWAY-FASSUNG.
  # Der Wortlaut ist gebunden: Werkzeuge/gateway_wirkung.py sucht genau
  # diese Wendungen in der GERENDERTEN Seite. Wer sie umformuliert, macht
  # die Pruefung blind, nicht rot.
  ('ABO_PFLICHT',
   "Ohne diesen Eintrag kommt am Miniserver nichts an.",
   "Without this entry nothing arrives at the Miniserver."),
  ('ABO_V2',
   "Das Gateway erkennt die Themengruppe von selbst — ein Abo ist nicht "
   "einzutragen. Der Kern schaltet die Knöpfe dafür aus.",
   "The gateway detects the topic group by itself — no subscription needs to "
   "be entered. The core disables the buttons for it."),
  ('ABO_UNBEKANNT',
   "Die Fassung des MQTT-Gateways ließ sich nicht feststellen. Deshalb "
   "stehen hier beide Fälle:",
   "The version of the MQTT gateway could not be determined. Both cases are "
   "therefore given here:"),
  ('THEMEN_HINT',
   "Genau diese Namen veröffentlicht der Dienst — Tabelle, Vorlage und "
   "Dienst lesen dieselbe Liste aus <span class='sm-mono'>bin/sm_felder.json"
   "</span>. Punkte im Namen bleiben stehen; das Gateway ersetzt nur "
   "<span class='sm-mono'>/</span> und <span class='sm-mono'>%</span> durch "
   "<span class='sm-mono'>_</span>.",
   "These are exactly the names the service publishes — table, template and "
   "service read the same list from <span class='sm-mono'>bin/sm_felder.json"
   "</span>. Dots in a name remain; the gateway only replaces "
   "<span class='sm-mono'>/</span> and <span class='sm-mono'>%</span> with "
   "<span class='sm-mono'>_</span>."),
  ('EINHEIT_VZ',
   "Die Einheiten gelten für den klassischen Leser. Ob vzLogger dieselben "
   "Einheiten liefert, ist hier nicht nachgemessen — dafür fehlt ein Zähler. "
   "Deshalb rechnet das Plugin nichts um; im Zweifel gilt, was der Zähler "
   "sendet.",
   "The units apply to the classic reader. Whether vzLogger delivers the same "
   "units has not been measured here — that would need a meter. The plugin "
   "therefore converts nothing; in case of doubt what the meter sends applies."),
 ]),
 ('LOX', [
  ('H_TITEL',
   'Einbindung in Loxone – Schritt für Schritt',
   'Loxone integration – step by step'),
  ('S1_TITEL',
   'Schritt 1: Weg festlegen',
   'Step 1: choose the path'),
  ('S1_TEXT',
   '<b>MQTT ist der Regelweg.</b> Das Gateway legt die Namen selbst an; in Loxone braucht man nur virtuelle Eingänge mit passendem Titel. UDP steht als Ausweichweg bereit – einzuschalten im Reiter <i>Smartmeter (vzLogger)</i>.',
   '<b>MQTT is the normal path.</b> The gateway creates the names itself; in Loxone you only need virtual inputs with a matching title. UDP is available as a fallback – switch it on in the <i>Smartmeter (vzLogger)</i> tab.'),
  ('S2_TITEL',
   'Schritt 2: Abo im MQTT-Gateway eintragen',
   'Step 2: enter the subscription in the MQTT gateway'),
  ('S3_TITEL',
   'Schritt 3: Virtuelle Eingänge anlegen',
   'Step 3: create virtual inputs'),
  ('S3_HINT',
   'Die endgültigen Namen zeigt das Gateway unter <i>Eingehende Daten</i> – weichen sie ab, gelten die dort angezeigten.',
   'The gateway shows the final names under <i>Incoming data</i> – if they differ, the ones shown there apply.'),
  ('H_VORLAGE',
   'Alles auf einmal anlegen',
   'Create everything at once'),
  ('H_VORLAGE_TEXT',
   'Statt jeden Eingang von Hand anzulegen: diese Datei legt die Eingänge mit den richtigen Namen an; die Werte kommen dann vom MQTT-Gateway. <b>Achtung:</b> Loxone Config legt beim Import neu an und überschreibt nichts - zweimal eingelesen ergibt doppelte Bausteine.',
   'Instead of creating every input by hand: this file creates the inputs with the correct names; the values then come from the MQTT gateway. <b>Note:</b> Loxone Config always creates new objects on import - importing twice yields duplicate blocks.'),
  ('K_VORLAGE',
   'Vorlage für Loxone Config erzeugen',
   'Create template for Loxone Config'),
  ('S4_TITEL',
   'Schritt 4: Der UDP-Weg',
   'Step 4: the UDP path'),
  ('S4_AN',
   'Ein <i>virtueller UDP-Eingang</i> auf Port %s, je Wert ein Befehl mit dieser Erkennung:',
   'One <i>virtual UDP input</i> on port %s, one command per value with this recognition:'),
  ('S4_AUS',
   'UDP ist derzeit <b>ausgeschaltet</b>. Einschalten im Reiter <i>Smartmeter (vzLogger)</i>.',
   'UDP is currently <b>switched off</b>. Switch it on in the <i>Smartmeter (vzLogger)</i> tab.'),
  ('S5_TITEL',
   'Schritt 5: Ausfallerkennung',
   'Step 5: failure detection'),
  ('S5_TEXT',
   'Schweigt der Zähler, behalten die virtuellen Eingänge ihren <b>letzten Wert</b> – in der App sieht dann alles normal aus. Deshalb die aktuelle Wirkleistung mitführen: sie ändert sich ständig. Bleibt sie exakt stehen, kommt nichts mehr an.',
   'If the meter falls silent, the virtual inputs keep their <b>last value</b> – everything looks normal in the app. That is why the current active power should be carried along: it changes constantly. If it stays exactly put, nothing is arriving any more.'),
  ('S6_TITEL',
   'Schritt 6: Komplette Baustein-Liste zum 1:1-Nachbauen',
   'Step 6: complete block list for rebuilding one to one'),
  ('S6_TEXT',
   'Von oben nach unten abarbeiten. Die Bausteine findet man in Loxone Config über die Baustein-Suche (F5):',
   'Work through it from top to bottom. The blocks can be found in Loxone Config via the block search (F5):'),
  ('S6_STATUSTEXT',
   'Statustext für #12:',
   'Status text for #12:'),
  ('S7_TITEL',
   'Schritt 7: Gegenprobe',
   'Step 7: cross-check'),
  ('S7_TEXT',
   'Im Reiter <i>Test</i> die <i>Antwort der HTTP-Schnittstelle</i> ansehen. Stehen dort Werte mit %s größer null, liest das Plugin. Kommen sie in Loxone trotzdem nicht an, fehlt fast immer das Abo aus Schritt&nbsp;2.',
   'On the <i>Test</i> tab, look at the <i>response of the HTTP interface</i>. If there are values with %s greater than zero, the plugin is reading. If they still do not arrive in Loxone, the subscription from step&nbsp;2 is almost always missing.'),
  ('S8_TEXT',
   'Neben MQTT und UDP liefert das Plugin die zuletzt gelesenen Werte auch als Klartext über diese Adresse. Ein virtueller HTTP-Eingang im Miniserver kann sie direkt abfragen:',
   'Besides MQTT and UDP the plugin also serves the last readings as plain text at this address. A virtual HTTP input on the Miniserver can poll it directly:'),
  ('S8_TITEL',
   'Schritt 8 — die Rohdaten direkt abholen (freiwillig)',
   'Step 8 — fetch the raw values directly (optional)'),
  ('SP_TITEL_VE',
   'Titel des virtuellen Eingangs',
   'Title of the virtual input'),
  ('SP_BAUSTEIN',
   'Baustein (Typ)',
   'Block (type)'),
  ('SP_NAME',
   'Name (Vorschlag)',
   'Name (suggestion)'),
  ('SP_PARAMETER',
   'Parameter',
   'Parameter'),
  ('SP_EINGAENGE',
   'Eingänge verbinden mit',
   'Connect inputs to'),
  ('EINGANG',
   'Eingang',
   'Input'),
  ('EINGAENGE',
   'Eingänge',
   'Inputs'),
  ('P_MITTERNACHT',
   'Rücksetzen um Mitternacht',
   'Reset at midnight'),
  ('P_ANALOG',
   'Aufzeichnung analog',
   'Analogue recording'),
  ('P_SCHWELLE0',
   'Schwelle 0&nbsp;W, Richtung kleiner',
   'Threshold 0&nbsp;W, direction less than'),
  ('P_VERZOEGERUNG',
   'Verzögerung',
   'Delay'),
  ('P_TEXT_FREI',
   'Text frei',
   'Text free'),
  ('P_STATUSTEXT',
   'Statustext siehe unten',
   'Status text see below'),
  ('N_ZAEHLER_PRUEFEN',
   'Stromzaehler_pruefen',
   'Check_electricity_meter'),
  ('TOKEN_AKTIV',
   "Die Adresse ist durch ein Token geschützt. Ohne den Zusatz <span class='sm-mono'>?token=…</span> antwortet sie mit 403.",
   "The address is protected by a token. Without the <span class='sm-mono'>?token=…</span> suffix it answers with 403."),
  ('TOKEN_ENTFERNEN',
   'Token entfernen',
   'Remove token'),
  ('TOKEN_ERNEUERN',
   'Neues Token',
   'New token'),
  ('TOKEN_NEU',
   'Ein neues Token wurde gesetzt. Die Adresse im Miniserver muss angepasst werden.',
   'A new token has been set. The address on the Miniserver needs updating.'),
  ('TOKEN_OFFEN',
   '<b>Diese Adresse ist ohne Kennwort erreichbar.</b> Sie liegt im unangemeldeten Bereich, damit der Miniserver ohne Zugangsdaten liest — damit liest sie aber auch jedes andere Gerät im Netz. Ein Token schließt das. <b>Achtung:</b> Nach dem Setzen muss die Adresse im Miniserver angepasst werden, sonst kommen dort keine Werte mehr an.',
   '<b>This address is reachable without a password.</b> It sits in the unauthenticated area so the Miniserver can read it without credentials — which also means every other device on the network can. A token closes that. <b>Note:</b> after setting one you must update the address on the Miniserver, otherwise no values will arrive there.'),
  ('TOKEN_SETZEN',
   'Token setzen',
   'Set token'),
  ('TOKEN_WEG',
   'Das Token wurde entfernt. Die Adresse ist wieder ohne Zusatz erreichbar.',
   'The token has been removed. The address works without a suffix again.'),

  ('VORLAGE_LEER',
   "Es gibt nichts, woraus sich eine Vorlage bauen ließe: es ist kein Feld "
   "bekannt. Erst lesen lassen, dann die Vorlage erzeugen.",
   "There is nothing to build a template from: no field is known. Let it read "
   "first, then create the template."),
  ('K_VORLAGE_LG', "Vorlage für den klassischen Leser",
   "Template for the classic reader"),
  ('P_ZAEHLER', "fortlaufend, springt nach 999 auf 0",
   "counts up, wraps from 999 to 0"),
  ('S6_ZU4', "Zu #4:", "On #4:"),
  ('S6_ZU4_TEXT',
   "<span class='sm-mono'>ZAEHLER</span> zählt jede erfolgreiche Ablesung "
   "mit und läuft bei 999 wieder auf 0. Er ist der einzige Wert, der sich "
   "auch dann ändert, wenn der Zählerstand gerade stillsteht — daran erkennt "
   "Loxone einen stummen Zähler.",
   "<span class='sm-mono'>ZAEHLER</span> counts every successful reading and "
   "wraps from 999 back to 0. It is the only value that keeps changing even "
   "while the meter reading stands still — that is how Loxone spots a silent "
   "meter."),
  ('S6_ZU10', "Zu #10:", "On #10:"),
  ('S6_ZU10_TEXT',
   "Die Schwelle muss deutlich über dem Abfragetakt liegen, damit ein "
   "einzelnes verpasstes Telegramm keine Meldung auslöst. Der oben "
   "eingetragene Wert ist das Doppelte der Altersgrenze, mindestens aber 600 "
   "Sekunden.",
   "The threshold must be well above the polling cycle so that a single "
   "missed telegram does not raise an alert. The value given above is twice "
   "the age limit, but at least 600 seconds."),
  ('S6_ZU1112', "Zu #11 und #12:", "On #11 and #12:"),
  ('S6_ZU1112_TEXT',
   "Der Benachrichtigungs-Baustein sendet nur beim Wechsel von Aus auf Ein. "
   "<b>Niemals mehrere Quellen direkt an seinen Eingang</b> — erst über ODER "
   "zusammenführen, sonst verschluckt eine dauerhaft aktive Quelle alle "
   "übrigen.",
   "The notification block only fires on a change from off to on. <b>Never "
   "wire several sources directly to its input</b> — merge them through an OR "
   "first, otherwise a permanently active source swallows all the others."),
  ('S8_SELFTEST',
   "Dieselbe Adresse mit <span class='sm-mono'>?selftest=1</span> antwortet "
   "in einer Zeile, ob das Plugin gerade liest — ohne die Messwerte "
   "mitzuschicken:",
   "The same address with <span class='sm-mono'>?selftest=1</span> answers in "
   "a single line whether the plugin is currently reading — without sending "
   "the measured values along:"),
  ('S8_ZEILE',  # (1) Beispielzeile
   "Angehängt an die Messwerte steht außerdem eine Zustandszeile: %s. "
   "<span class='sm-mono'>OK=1</span> heißt gelesen, "
   "<span class='sm-mono'>ALTER</span> ist das Alter der letzten Messung in "
   "Sekunden, <span class='sm-mono'>ZAEHLER</span> der umlaufende Zähler.",
   "A status line is appended to the measured values as well: %s. "
   "<span class='sm-mono'>OK=1</span> means it is reading, "
   "<span class='sm-mono'>ALTER</span> is the age of the last reading in "
   "seconds, <span class='sm-mono'>ZAEHLER</span> the wrapping counter."),
  ('VORLAGE_TITEL', "Smartmeter (vzLogger)", "Smartmeter (vzLogger)"),
  ('VORLAGE_TITEL_LG', "Smartmeter (klassisch)", "Smartmeter (classic)"),
  ('VORLAGE_KOMMENTAR',  # (2) Datum, Themenpraefix
   "Erzeugt vom Plugin Smartmeter classic am %s. Themenpräfix: %s. Die Werte "
   "liefert das MQTT-Gateway.",
   "Created by the Smartmeter classic plugin on %s. Topic prefix: %s. The "
   "values are delivered by the MQTT gateway."),
  ('VORLAGE_KOMMENTAR_LG',  # (2) Datum, Zahl der Lesekoepfe
   "Erzeugt vom Plugin Smartmeter classic am %s für %s Lesekopf/Leseköpfe. "
   "Die Werte liefert das MQTT-Gateway.",
   "Created by the Smartmeter classic plugin on %s for %s reading head(s). "
   "The values are delivered by the MQTT gateway."),
  ('VORLAGE_TEXTFELDER',  # (1) Anzahl
   "%s davon sind Textfelder und gehören an einen virtuellen Texteingang.",
   "%s of them are text fields and belong on a virtual text input."),
 ]),
 ('BAUSTEIN', [
  ('VE',
   'Virtueller Eingang',
   'Virtual input'),
  ('ZAEHLER',
   'Zähler',
   'Counter'),
  ('STATISTIK',
   'Statistik',
   'Statistics'),
  ('VERGLEICHER',
   'Vergleicher',
   'Comparator'),
  ('ANALOGSPEICHER',
   'Analogspeicher',
   'Analogue memory'),
  ('FORMEL',
   'Formel',
   'Formula'),
  ('EVZ',
   'Einschaltverzögerung',
   'Switch-on delay'),
  ('ODER',
   'ODER',
   'OR'),
  ('BENACHRICHTIGUNG',
   'Benachrichtigung',
   'Notification'),
  ('STATUS',
   'Status',
   'Status'),
 ]),
 ('OBIS', [
  ('BEZUG',
   'Bezug',
   'consumption'),
  ('EINSPEISUNG',
   'Einspeisung',
   'feed-in'),
  ('LEISTUNG',
   'aktuelle Leistung',
   'current power'),
  ('ZAEHLERSTAND',
   'Zählerstand',
   'meter reading'),
 ]),
 # ------------------------------------------------------------------
 # [FELD] und [OBIS] - hier gilt eine HARTE LAENGENGRENZE.
 #
 # Diese Texte werden in der Loxone-Vorlage zum Comment eines Befehls, und
 # Loxone Config macht daraus den ANZEIGENAMEN des virtuellen Eingangs.
 # Ueber 40 Byte ist das kein Name mehr, sondern ein Satz. Der Erzeuger
 # bricht deshalb ab, statt es zu schreiben - gemessen wird in BYTE, weil
 # die Pruefung in sm_test.php strlen() benutzt und ein Umlaut dort zwei
 # zaehlt.
 # ------------------------------------------------------------------
 ('FELD', [
  ('BEZUG_GESAMT', "Zählerstand Bezug, gesamt", "Meter reading, consumption, total"),
  ('BEZUG_TARIF', "Zählerstand Bezug, Tarifzählwerk", "Consumption reading, tariff register"),
  ('BEZUG_RECHNERISCH', "Zählerstand Bezug, rechnerisch", "Meter reading, consumption, computed"),
  ('BEZUGSLEISTUNG', "Bezugsleistung", "Consumption power"),
  ('EINSP_GESAMT', "Zählerstand Einspeisung, gesamt", "Meter reading, delivery, total"),
  ('EINSP_TARIF', "Zählerstand Einspeisung, Tarifzählwerk", "Delivery reading, tariff register"),
  ('EINSP_RECHNERISCH', "Zählerstand Einspeisung, rechnerisch", "Meter reading, delivery, computed"),
  ('EINSPEISELEISTUNG', "Einspeiseleistung", "Delivery power"),
  ('WIRKLEISTUNG', "aktuelle Wirkleistung", "current active power"),
  ('WIRKLEISTUNG_BETRAG', "aktuelle Wirkleistung, Betrag", "current active power, magnitude"),
  ('LEISTUNG_PHASE', "Wirkleistung je Phase", "active power per phase"),
  ('MAXLEISTUNG', "höchste gemessene Leistung", "highest measured power"),
  ('SPANNUNG', "Spannung", "voltage"),
  ('STROM', "Stromstärke", "current"),
  ('STUNDEN', "Betriebsstunden", "operating hours"),
  ('TARIF', "gerade gültiger Tarif", "currently active tariff"),
  ('SCHALTER', "Stellung des Schaltausgangs", "state of the switching output"),
  ('MELDECODE', "Meldecode des Zählers", "meter status code"),
  ('MELDETEXT', "Meldetext des Zählers", "meter status text"),
  ('GERAETEKENNUNG', "Gerätekennung", "device identifier"),
  ('FASSUNG', "Fassung der Zähler-Software", "meter firmware version"),
  ('CFUENF', "Prüfsumme C.5", "checksum C.5"),
  ('TEMPERATUR', "Temperatur", "temperature"),
  ('VOLUMEN', "Volumen", "volume"),
  ('DURCHFLUSS', "Durchfluss", "flow rate"),
  ('WAERME_GESAMT', "Wärmemenge, gesamt", "heat quantity, total"),
  ('WAERME_TARIF', "Wärmemenge, Tarifzählwerk", "heat quantity, tariff register"),
  ('LAST_UPDATE', "Zeitpunkt der letzten Ablesung", "time of the last reading"),
  ('LAST_UPDATE_LOX', "Ablesezeit, Loxone-Zeitrechnung",
   "reading time, Loxone epoch"),
  # Der Unterschied zu den beiden darueber ist der ganze Zweck: die
  # schreibt der Leser bei JEDEM Durchlauf, auch bei einem ohne einen
  # einzigen Wert. Dieser hier steht nur da, wenn der Zaehler geantwortet
  # hat - daran haengt die Ausfallerkennung.
  ('LAST_UPDATE_UNIX', "Zeit der letzten Messung, Unix",
   "time of the last reading, Unix"),
 ]),
 ('EINST', [
  ('H_SICHERUNG', "Einstellungen sichern und zurückspielen",
   "Back up and restore the settings"),
  ('SICHERUNG_HINT',
   "Eine Textdatei mit allen Einstellungen beider Lesewege — Zählerprofile, "
   "Bezeichnungen, Abfragetakt, Themenpräfix und das Zugriffstoken. Sie lässt "
   "sich auf einem anderen LoxBerry wieder einlesen.",
   "A text file holding all settings of both reading paths — meter profiles, "
   "labels, polling cycle, topic prefix and the access token. It can be read "
   "back in on another LoxBerry."),
  ('SICHERUNG_GEHEIM',
   "<b>Die Datei trägt das Zugriffstoken im Klartext.</b> Ohne es wäre sie "
   "nach dem Zurückspielen wertlos — der Miniserver käme mit der alten "
   "Adresse nicht mehr durch. Deshalb gehört sie nicht in ein Forum und nicht "
   "in einen geteilten Ordner.",
   "<b>The file carries the access token in plain text.</b> Without it the "
   "file would be worthless after restoring — the Miniserver would no longer "
   "get through with the old address. So it does not belong in a forum or in "
   "a shared folder."),
  ('SICHERN', "Einstellungen sichern", "Back up settings"),
  ('LADEN', "Sicherung zurückspielen", "Restore backup"),
  ('LADEN_HINT',
   "Zurückgespielt wird nur eine Datei, die durchgängig gelesen werden kann. "
   "Findet sich auch nur eine unverständliche Zeile, bleibt alles, wie es "
   "ist — eine halb eingelesene Konfiguration wäre schlimmer als gar keine.",
   "Only a file that can be read from beginning to end is restored. If even a "
   "single line cannot be understood, everything stays as it is — a half-read "
   "configuration would be worse than none."),
 ]),
 ('SICH', [
  ('KEINE_DATEI',
   "Es wurde keine Datei ausgewählt.", "No file was selected."),
  ('ZU_GROSS',
   "Die Datei ist größer als 64 kB. Eine Sicherung dieses Plugins ist es "
   "damit nicht; es wurde nichts gelesen.",
   "The file is larger than 64 kB. That is not a backup of this plugin; "
   "nothing has been read."),
  ('ABGELEHNT',
   "Die Datei wurde abgewiesen. Es wurde nichts geändert.",
   "The file was rejected. Nothing has been changed."),
  ('UEBERNOMMEN', "Die Sicherung wurde übernommen.",
   "The backup has been applied."),
  ('DIENST_NEU', "vzlogger wurde neu gestartet.",
   "vzlogger has been restarted."),
  ('DIENST_AUS', "vzLogger ist in der Sicherung ausgeschaltet — der Dienst "
   "wurde nicht gestartet.",
   "vzLogger is switched off in the backup — the service has not been started."),
  ('LEER',
   "Die Datei enthält keinen einzigen lesbaren Eintrag.",
   "The file contains not a single readable entry."),
  ('KOPF_FEHLT',  # (2) Abschnitt, Geraet
   "Der Lesekopf %s zeigt auf %s — dieses Gerät ist derzeit nicht "
   "angesteckt. Die Einstellung wurde trotzdem übernommen.",
   "Reading head %s points to %s — that device is not plugged in at the "
   "moment. The setting has been applied nonetheless."),
  ('UEBERGANGEN',  # (1) Schluessel
   "%s stand in der Datei und wurde übergangen: dieser Wert gehört zu diesem "
   "LoxBerry und nicht in eine Sicherung.",
   "%s was in the file and has been skipped: that value belongs to this "
   "LoxBerry, not in a backup."),
  ('ABSCHNITT',  # (2) Zeilennummer, Abschnitt
   "Zeile %s: der Abschnitt [%s] gehört nicht in eine Sicherung dieses "
   "Plugins.",
   "Line %s: the section [%s] does not belong in a backup of this plugin."),
  ('ZEILE',  # (2) Zeilennummer, Zeileninhalt
   "Zeile %s ist weder Abschnitt noch Zuweisung: %s",
   "Line %s is neither a section nor an assignment: %s"),
  ('SCHLUESSEL',  # (2) Zeilennummer, Schluessel
   "Zeile %s: den Schlüssel %s gibt es in diesem Plugin nicht.",
   "Line %s: this plugin has no key called %s."),
  ('KOPF_OHNE_NAME',  # (1) Zeilennummer
   "Zeile %s: ein Lesekopf-Abschnitt ohne Namen.",
   "Line %s: a reading-head section without a name."),
  ('OHNE_ABSCHNITT',  # (2) Zeilennummer, Schluessel
   "Zeile %s: %s steht vor dem ersten Abschnitt.",
   "Line %s: %s appears before the first section."),
  ('WERT',  # (2) Schluessel, Wert
   "%s trägt einen Wert, den dieses Plugin nicht setzen kann: %s",
   "%s carries a value this plugin cannot set: %s"),
 ]),
 ('SUCHE', [
  ('H', "Zählerprofil suchen", "Search for a meter profile"),
  ('HINT',
   "Probiert nacheinander vier allgemeine Lesewege am gewählten Lesekopf aus "
   "und zeigt, welcher antwortet. Der Suchlauf ändert nichts — er schlägt nur "
   "vor. Er dauert bis zu einer Minute und braucht die serielle "
   "Schnittstelle für sich.",
   "Tries four generic reading paths one after another on the selected "
   "reading head and shows which one answers. The search changes nothing — it "
   "only makes a suggestion. It takes up to a minute and needs the serial "
   "port to itself."),
  ('K', "Suchlauf starten", "Start search"),
  ('H_ERGEBNIS', "Ergebnis des Suchlaufs", "Result of the search"),
  ('W_SML9600', "SML, 9600 Baud, 8N1", "SML, 9600 baud, 8N1"),
  ('W_SML300', "SML, 300 Baud, 7E1", "SML, 300 baud, 7E1"),
  ('W_D09600', "D0, 9600 Baud, 8N1", "D0, 9600 baud, 8N1"),
  ('W_D0300', "D0, Start 300 Baud, dann 9600, 7E1",
   "D0, starting at 300 baud, then 9600, 7E1"),
  ('KEIN_GERAET',  # (1) Geraet
   "%s gibt es nicht. Es wurde nichts gesucht.",
   "%s does not exist. Nothing has been searched."),
  ('LESER_LAEUFT',
   "Es läuft gerade ein Leser. Der Suchlauf braucht die serielle "
   "Schnittstelle für sich — bitte erst abschalten.",
   "A reader is currently running. The search needs the serial port to "
   "itself — please switch it off first."),
  ('BELEGT',  # (2) Geraet, Belegung
   "%s ist belegt: %s. Es wurde nichts gesucht.",
   "%s is in use: %s. Nothing has been searched."),
  ('TREFFER',  # (4) Weg, Dauer, Zahl der Werte, Werte
   "%s: nach %s s antwortet der Zähler mit %s Wert(en): %s",
   "%s: after %s s the meter answers with %s value(s): %s"),
  ('NICHTS',  # (2) Weg, Dauer
   "%s: nach %s s keine Antwort.",
   "%s: no answer after %s s."),
  ('VORSCHLAG',  # (1) Weg
   "Vorschlag: %s. Dieses Profil im Feld darüber einstellen und speichern.",
   "Suggestion: %s. Set this profile in the field above and save."),
  ('MEHRDEUTIG',  # (1) Namen
   "Mehrere Wege antworten: %s. Es wird nichts vorgeschlagen — welcher der "
   "richtige ist, entscheidet der Zählertyp, nicht dieser Suchlauf.",
   "Several paths answer: %s. No suggestion is made — which one is right is "
   "decided by the meter type, not by this search."),
  ('NICHTS_GEFUNDEN',
   "Kein Weg hat geantwortet. Das schließt den Zähler nicht aus: die vier "
   "Wege sind allgemein gehalten, viele Zähler brauchen ihr eigenes Profil.",
   "No path answered. That does not rule the meter out: the four paths are "
   "generic, and many meters need their own profile."),
  ('UEBERNEHMEN',  # (1) Vorschlag
   "Der Suchlauf schlägt %s vor. Übernommen wird nichts von selbst — die "
   "Einstellung gehört in das Feld oben.",
   "The search suggests %s. Nothing is applied automatically — the setting "
   "belongs in the field above."),
 ]),
 ('TEST', [
  ('H_DIAGNOSE',
   'Diagnose',
   'Diagnosis'),
  ('H_NACHSEHEN',
   'Nachsehen',
   'Look up'),
  ('K_UMGEBUNG',
   'Umgebung prüfen',
   'Check environment'),
  ('K_HTTP',
   'Antwort der HTTP-Schnittstelle',
   'Response of the HTTP interface'),
  ('K_LEGACY',
   'Einstellungen des klassischen Lesers',
   'Settings of the classic reader'),
  ('HTTP_STUMM',
   'Keine Antwort auf Port %s.',
   'No response on port %s.'),
  ('UNBEKANNT',
   'unbekannt',
   'unknown'),
  ('U_PHP',
   'PHP-Fassung',
   'PHP version'),
  ('U_ARCH',
   'Architektur',
   'Architecture'),
  ('U_GRUND',
   'Grund',
   'Reason'),
  ('U_NICHT_LAUFFAEHIG',
   'nicht lauffaehig',
   'not runnable'),
  ('U_PAKET_INST',
   'Paket installiert',
   'Package installed'),
  ('U_PAKET_VERF',
   'Paket verfügbar',
   'Package available'),
  ('U_KOEPFE',
   'Leseköpfe',
   'Optical heads'),
  ('U_KEINER',
   'keiner erkannt',
   'none detected'),
  ('U_VORHANDEN',
   'vorhanden (%s kB)',
   'present (%s kB)'),
  ('U_NICHT_VORHANDEN',
   'nicht vorhanden',
   'not present'),
  ('LG_AN',
   'Der klassische Leser ist EINGESCHALTET - er belegt die serielle Schnittstelle.',
   'The classic reader is SWITCHED ON - it occupies the serial interface.'),
  ('LG_AUS',
   'Der klassische Leser ist ausgeschaltet.',
   'The classic reader is switched off.'),
  ('UNBEKANNTE_PRUEFUNG',
   'Unbekannte Prüfung',
   'Unknown check'),
  ('GIBT_ES_NICHT',
   'Diese Prüfung gibt es nicht.',
   'This check does not exist.'),

  ('H_SELBST', "Selbsttest", "Self-test"),
  ('STRICHE',  # (2) Zahl der Pruefungen, Zahl der Striche
   "%s Prüfungen. %s davon sind ein Strich (–): dort ist nichts zu messen — "
   "ein Strich ist kein Haken.",
   "%s checks. %s of them are a dash (–): there is nothing to measure there — "
   "a dash is not a tick."),
  ('K_MITSCHNITT', "Mitschnitt des letzten Telegramms",
   "Recording of the last telegram"),
  ('U_KATALOG',  # (2) Zahl der Felder, Zahl der OBIS-Kennzahlen
   "vorhanden, %s Felder und %s OBIS-Kennzahlen",
   "present, %s fields and %s OBIS codes"),
  ('LG_NICHT_GESETZT', "nicht gesetzt", "not set"),
  ('LG_GESETZT',  # (1) Laenge
   "gesetzt (%s Zeichen)", "set (%s characters)"),
  ('MITSCHNITT_LEER',
   "Es liegt kein Mitschnitt vor. Er entsteht bei der nächsten Abfrage.",
   "No recording is available. One is made at the next reading."),
  ('MITSCHNITT_WARNUNG',
   "Ein Mitschnitt enthält den Rohtext des Zählers — darin steht in der Regel "
   "die Zählernummer. Vor dem Einstellen in ein Forum bitte durchsehen.",
   "A recording contains the raw text from the meter — which as a rule "
   "includes the meter number. Please look through it before posting it to a "
   "forum."),
 ]),
 ('PRUEF', [
  ('Z_DIENST', "Dienst", "Service"),
  ('Z_HERZ', "Herzschlag", "Heartbeat"),
  ('Z_CRON', "Abfragetakt", "Polling cycle"),
  ('Z_KONFIG', "Konfiguration", "Configuration"),
  ('Z_KATALOG', "Feldkatalog", "Field catalogue"),
  ('Z_THEMEN', "Themen", "Topics"),
  ('Z_MUSTER', "Suchmuster", "Search patterns"),
  ('Z_INI', "INI-Muster", "INI patterns"),
  ('Z_XML', "XML-Vorlagen", "XML templates"),
  ('Z_REITER', "Reiter", "Tabs"),
  ('Z_SMACTIVE', "Offener Reiter", "Open tab"),
  ('Z_FORM', "Formulare", "Forms"),
  ('Z_GATEWAY', "MQTT-Gateway", "MQTT gateway"),
  ('Z_ENDPUNKT', "Endpunkt", "Endpoint"),
  ('NICHT_LESBAR',  # (1) Dateiname
   "%s ließ sich nicht lesen — hier ist nichts zu messen.",
   "%s could not be read — there is nothing to measure here."),
  # --- Dienst ---
  ('DIENST_BEIDE',
   "Beide Leser sind eingeschaltet. Sie greifen auf dieselbe serielle "
   "Schnittstelle zu; einer von beiden gehört abgeschaltet.",
   "Both readers are switched on. They access the same serial port; one of "
   "them should be switched off."),
  ('DIENST_KEINER',
   "Es ist kein Leser eingeschaltet — es wird nichts gelesen. Das ist eine "
   "Einstellung, kein Fehler.",
   "No reader is switched on — nothing is being read. That is a setting, not "
   "a fault."),
  ('DIENST_VZ',  # (1) PID
   "vzlogger läuft, PID %s.", "vzlogger is running, PID %s."),
  ('DIENST_VZ_TOT',
   "vzLogger ist eingeschaltet, es läuft aber kein Prozess mit unserer "
   "Konfiguration.",
   "vzLogger is switched on, but no process is running with our "
   "configuration."),
  ('DIENST_LG_LAEUFT',  # (1) PID
   "Der klassische Leser ist eingeschaltet und läuft gerade, PID %s.",
   "The classic reader is switched on and running right now, PID %s."),
  ('DIENST_LG',
   "Der klassische Leser ist eingeschaltet. Zwischen zwei Abfragen läuft "
   "kein Prozess — das ist so gewollt.",
   "The classic reader is switched on. Between two readings no process runs — "
   "that is intended."),
  # --- Herzschlag ---
  ('HERZ_NIE',
   "Der Zähler wurde noch kein einziges Mal erfolgreich gelesen. Solange das "
   "so ist, gibt es kein Alter zu prüfen.",
   "The meter has never once been read successfully. As long as that is so, "
   "there is no age to check."),
  ('HERZ_NUR_START',  # (2) Zaehlerstand, Alter
   "Zähler %s, letzte Messung vor %s s. Der Abfragetakt steht auf „nur beim "
   "Systemstart“ — über etwas, das absichtlich alt ist, wird hier nicht "
   "geurteilt.",
   "Counter %s, last reading %s s ago. The polling cycle is set to „only at "
   "system start“ — nothing that is deliberately old is judged here."),
  ('HERZ_ALT',  # (3) Zaehlerstand, Alter, Grenze
   "Der Zähler schweigt: Zähler %s, letzte Messung vor %s s, erlaubt sind "
   "%s s. In Loxone behalten die virtuellen Eingänge ihren letzten Wert.",
   "The meter is silent: counter %s, last reading %s s ago, %s s allowed. In "
   "Loxone the virtual inputs keep their last value."),
  ('HERZ_OK',  # (2) Zaehlerstand, Alter
   "Zähler %s, letzte Messung vor %s s.",
   "Counter %s, last reading %s s ago."),
  # --- Konfiguration ---
  ('CFG_FEHLT',  # (1) Pfad
   "%s fehlt.", "%s is missing."),
  ('CFG_LEER',
   "Die Konfiguration ist leer.", "The configuration is empty."),
  ('CFG_FEHLEND',  # (3) Zahl fehlend, Zahl gesamt, Namen
   "%s von %s Schlüsseln fehlen: %s",
   "%s of %s keys are missing: %s"),
  ('CFG_FREMD',  # (1) Namen
   "In der Konfiguration stehen Schlüssel, die dieses Plugin nicht kennt: %s",
   "The configuration holds keys this plugin does not know: %s"),
  ('CFG_OK',  # (1) Anzahl
   "Alle %s Schlüssel vorhanden.", "All %s keys present."),
  # --- Feldkatalog ---
  ('KAT_FEHLT',
   "bin/sm_felder.json fehlt. Ohne Katalog kennt weder die Oberfläche noch "
   "der Dienst die Feldnamen.",
   "bin/sm_felder.json is missing. Without the catalogue neither the "
   "interface nor the service knows the field names."),
  ('KAT_LEER',  # (1) Datei
   "%s enthält kein einziges Feld.", "%s contains not a single field."),
  ('KAT_ZWEITE_LISTE',
   "Im Leser steht wieder eine eigene Feldliste. Damit gibt es zwei "
   "Wahrheiten — der Katalog ist dann nicht mehr die eine Quelle.",
   "The reader carries its own field list again. That makes two truths — the "
   "catalogue is then no longer the single source."),
  ('KAT_DIENST_LIEST_NICHT',
   "Der Dienst liest den Katalog nicht. Er würde unter anderen Namen "
   "veröffentlichen als die Tabelle im Reiter MQTT anzeigt.",
   "The service does not read the catalogue. It would publish under names "
   "other than the ones the table in the MQTT tab shows."),
  ('KAT_OK',  # (2) Felder, OBIS
   "%s Felder und %s OBIS-Kennzahlen; Oberfläche und Dienst lesen dieselbe "
   "Datei.",
   "%s fields and %s OBIS codes; interface and service read the same file."),
  # --- Themen ---
  ('THEMEN_STUMM',  # (1) Rueckgabewert
   "Der Leser beantwortet --themen nicht (Rückgabewert %s) — die Namen "
   "lassen sich von hier aus nicht gegenprüfen.",
   "The reader does not answer --themen (return code %s) — the names cannot "
   "be cross-checked from here."),
  ('THEMEN_ABWEICHUNG',  # (3) hier, Dienst, Namen
   "Die Oberfläche zeigt %s Themen, der Dienst nennt %s. Abweichend: %s",
   "The interface shows %s topics, the service names %s. Differing: %s"),
  ('THEMEN_OK',  # (1) Anzahl
   "%s Themen — Oberfläche und Dienst nennen dieselben.",
   "%s topics — interface and service name the same ones."),
  # --- Suchmuster ---
  ('MUSTER_LEER',
   "Es ist kein Suchmuster hinterlegt — hier ist nichts zu messen.",
   "No search pattern is on file — there is nothing to measure here."),
  ('MUSTER_KOLLISION',  # (2) Anzahl, Namen
   "%s Muster passen auf mehr als ein Feld: %s. Der zuerst gefundene "
   "gewinnt, und das ist Zufall.",
   "%s patterns match more than one field: %s. Whichever is found first "
   "wins, and that is chance."),
  ('MUSTER_OK',  # (1) Anzahl
   "%s Felder, jedes Muster trifft genau eines.",
   "%s fields, each pattern matches exactly one."),
  # --- INI-Muster ---
  ('INI_KEINE',
   "Es liegt keine Sprachdatei vor — hier ist nichts zu messen.",
   "There is no language file — there is nothing to measure here."),
  ('INI_MUSTER',  # (2) Anzahl, Beispiele
   "%s Werte enthalten ein gerades Anführungszeichen: %s. Je nach Lesemodus "
   "wird der Wert abgeschnitten oder die ganze Datei abgewiesen — beides "
   "still.",
   "%s values contain a straight double quote: %s. Depending on the reading "
   "mode the value is truncated or the whole file is rejected — both "
   "silently."),
  ('INI_OK',  # (1) Anzahl
   "%s Werte geprüft, kein gerades Anführungszeichen.",
   "%s values checked, no straight double quote."),
  # --- XML-Vorlagen ---
  ('XML_KEIN_PARSER',
   "In diesem PHP fehlt SimpleXML — die Vorlagen lassen sich von hier aus "
   "nicht prüfen.",
   "SimpleXML is missing from this PHP — the templates cannot be checked from "
   "here."),
  ('XML_KEINE',
   "Es wurde keine Vorlage erzeugt — hier ist nichts zu messen.",
   "No template was created — there is nothing to measure here."),
  ('XML_KAPUTT',  # (1) Namen
   "Diese Vorlage ist kein gültiges XML: %s. Loxone Config weist sie ab.",
   "This template is not valid XML: %s. Loxone Config rejects it."),
  # Gemessen wird der COMMENT eines Befehls, nicht sein Titel. Der Text
  # sagte bis zum 26.08.2026 das Falsche - und schickte damit jeden, der
  # ihn liest, an die falsche Stelle.
  ('XML_KOMMENTAR',  # (2) Anzahl, erstes
   "%s Kommentar(e) sind länger als 40 Zeichen. Loxone Config macht daraus "
   "den Anzeigenamen des Befehls — dafür taugt kein Satz. Der erste: %s",
   "%s comment(s) are longer than 40 characters. Loxone Config turns them "
   "into the display name of the command — a sentence is no good for that. "
   "The first: %s"),
  ('XML_OK',  # (1) Anzahl
   "%s Vorlage(n) geprüft, gültiges XML.",
   "%s template(s) checked, valid XML."),
  # --- Reiter ---
  ('REITER_OHNE_FLAECHE',  # (1) Namen
   "Zu diesen Reitern gibt es keine Fläche: %s. Der Verweis führt ins Leere.",
   "These tabs have no pane: %s. The link leads nowhere."),
  ('REITER_UNERREICHBAR',  # (1) Namen
   "Diese Flächen stehen im HTML, aber kein Reiter führt hin: %s",
   "These panes are in the HTML, but no tab leads to them: %s"),
  ('REITER_OHNE_LEISTE',  # (1) Namen
   "Diese Reiter fehlen in der Leiste: %s",
   "These tabs are missing from the bar: %s"),
  ('REITER_OK',  # (1) Anzahl
   "%s Reiter — Liste, Leiste und Flächen tragen dieselben Namen.",
   "%s tabs — list, bar and panes carry the same names."),
  # --- Offener Reiter ---
  ('SMACTIVE_OK',  # (2) Anzahl in der Leiste, in den Flaechen
   "Der offene Reiter steht schon im ausgelieferten HTML (%s in der Leiste, "
   "%s an den Flächen) — er ist auch ohne JavaScript zu sehen.",
   "The open tab is already in the delivered HTML (%s in the bar, %s on the "
   "panes) — it is visible without JavaScript too."),
  ('SMACTIVE_FEHLT',  # (3) Leiste, Bereiche, Anzahl
   "Der offene Reiter wird erst von JavaScript gesetzt (Leiste %s, Flächen "
   "%s, zusammen %s). Ohne JavaScript sieht der Anwender keinen Inhalt.",
   "The open tab is only set by JavaScript (bar %s, panes %s, %s together). "
   "Without JavaScript the user sees no content."),
  # --- Formulare ---
  ('FORM_KEINS',
   "Es gibt kein Formular — hier ist nichts zu messen.",
   "There is no form — there is nothing to measure here."),
  ('FORM_OHNE',  # (2) ohne, gesamt
   "%s von %s Formularen tragen kein Merkmal. Sie ließen sich von einer "
   "fremden Seite aus absenden.",
   "%s of %s forms carry no marker. They could be submitted from a foreign "
   "page."),
  ('FORM_OK',  # (1) Anzahl
   "%s Formulare, jedes trägt ein Merkmal.",
   "%s forms, each carries a marker."),
  # --- Gateway ---
  # Dieser Zweig greift, wenn SENDMQTT ausgeschaltet ist - nicht, wenn das
  # Gateway schweigt. Der Text sagte bis zum 26.08.2026 das Zweite.
  ('GW_AUS',
   "Das Senden per MQTT ist ausgeschaltet — hier ist nichts zu messen.",
   "Sending via MQTT is switched off — there is nothing to measure here."),
  ('GW_UNLESBAR',
   "Die general.json des LoxBerry ließ sich nicht lesen — über das Gateway "
   "ist von hier aus nichts zu sagen.",
   "The general.json of the LoxBerry could not be read — nothing can be said "
   "about the gateway from here."),
  ('GW_UNBEKANNT',
   "Die Fassung des Gateways steht nicht in der general.json. Die Seite nennt "
   "deshalb beide Fälle, statt einen zu behaupten.",
   "The gateway version is not in general.json. The page therefore names both "
   "cases instead of asserting one."),
  ('GW_KEIN_UDPIN',
   "Das Gateway nennt keinen UDP-Eingang. Der UDP-Weg ginge damit ins Leere.",
   "The gateway names no UDP input. The UDP path would lead nowhere."),
  ('GW_OK',  # (2) Fassung, UDP-Port
   "Gateway-Fassung %s, UDP-Eingang %s.",
   "Gateway version %s, UDP input %s."),
  # --- Endpunkt ---
  ('EP_NICHT_MESSBAR',  # (1) Adresse
   "%s ließ sich von hier aus nicht abrufen — hier ist nichts zu messen.",
   "%s could not be fetched from here — there is nothing to measure here."),
  ('EP_KEINE_ANTWORT',  # (1) Adresse
   "%s antwortet nicht.", "%s does not answer."),
  ('EP_OK',  # (1) Code
   "Der Endpunkt antwortet mit %s.", "The endpoint answers with %s."),
  ('EP_FALSCH',  # (2) Code, Antwort
   "Der Endpunkt antwortet mit %s: %s",
   "The endpoint answers with %s: %s"),
 ]),
 ('DIAG', [
  ('BETRIEBSART',
   'Betriebsart',
   'Mode'),
  ('PROGRAMM',
   'Programm',
   'Program'),
  ('PROZESS',
   'Prozess',
   'Process'),
  ('KONFIG',
   'Konfiguration',
   'Configuration'),
  ('LESEKOPF',
   'Lesekopf',
   'Optical head'),
  ('BELEGT',
   'Schnittstelle belegt',
   'Interface in use'),
  ('HTTP',
   'HTTP-Schnittstelle',
   'HTTP interface'),
  ('MESSWERTE',
   'Messwerte',
   'Readings'),
  ('VZ_AUS',
   'vzLogger ist ausgeschaltet. Es wird nichts gelesen.',
   'vzLogger is switched off. Nothing is being read.'),
  ('VZ_AN',
   'vzLogger ist eingeschaltet.',
   'vzLogger is switched on.'),
  ('PAKET',
   'Paket %s',
   'package %s'),
  ('PAKET_VERFUEGBAR',
   'verfügbar %s',
   'available %s'),
  ('LAEUFT_PID',
   'läuft, PID %s',
   'running, PID %s'),
  ('KEIN_PROZESS',
   'Es läuft kein vzlogger mit unserer Konfiguration (%s).',
   'No vzlogger is running with our configuration (%s).'),
  ('KONFIG_FEHLT',
   '%s fehlt. Einmal Speichern erzeugt sie neu.',
   '%s is missing. Saving once creates it again.'),
  ('KONFIG_OHNE_METERS',
   'In %s steht kein meters-Abschnitt.',
   'There is no meters section in %s.'),
  ('KONFIG_OHNE_KANAL',
   'Kein einziger Kanal in der Konfiguration. Ohne Kanal liest vzlogger nichts.',
   'Not a single channel in the configuration. Without a channel vzlogger reads nothing.'),
  ('KONFIG_INTERVAL',
   '%s Kanäle - aber es steht ein negatives interval darin. Bei sendenden SML-Zählern gehört der Schlüssel weggelassen.',
   '%s channels - but there is a negative interval in it. For SML meters that send on their own the key should be left out.'),
  ('KONFIG_OK',
   '%s Kanäle, kein interval-Schlüssel (richtig für sendende SML-Zähler).',
   '%s channels, no interval key (correct for SML meters that send on their own).'),
  ('KEIN_GERAET',
   'Kein Gerät ausgewählt.',
   'No device selected.'),
  ('GERAET_FEHLT',
   '%s gibt es nicht. Lesekopf abziehen und neu anstecken; die udev-Regel wird beim Start des Plugins angelegt.',
   '%s does not exist. Unplug the optical head and plug it in again; the udev rule is created when the plugin starts.'),
  ('GERAET_RECHTE',
   '%s ist nicht lesbar (Rechte).',
   '%s is not readable (permissions).'),
  ('BELEGT_LEGACY',
   'Die klassische Abfrage ist eingeschaltet und greift auf dasselbe Gerät zu. Zwei Leser können sich eine serielle Schnittstelle nicht teilen. Entweder den klassischen Leser abschalten oder vzLogger.',
   'The classic reader is switched on and accesses the same device. Two readers cannot share one serial interface. Switch off either the classic reader or vzLogger.'),
  ('BELEGT_FREMD',
   'Fremder Zugriff auf %s: %s',
   'Foreign access to %s: %s'),
  ('BELEGT_FREI',
   'Niemand sonst greift auf %s zu.',
   'Nobody else is accessing %s.'),
  ('HTTP_STUMM',
   'Port %s antwortet nicht. Entweder läuft vzlogger nicht, oder der Port ist belegt.',
   'Port %s does not respond. Either vzlogger is not running, or the port is in use.'),
  ('HTTP_OK',
   'Port %s antwortet, %s Kanäle angemeldet.',
   'Port %s responds, %s channels registered.'),
  ('KEINE_WERTE',
   'Keine Werte - ohne HTTP-Schnittstelle kann das Plugin sie nicht abholen.',
   'No values - without the HTTP interface the plugin cannot fetch them.'),
  ('KEINE_KANAELE',
   'vzlogger läuft, kennt aber keine Kanäle. Einmal Speichern und danach den Dienst neu starten.',
   'vzlogger is running but knows no channels. Save once and then restart the service.'),
  ('ZEITSTEMPEL',
   'Der Zähler wird gelesen, aber vzlogger verwirft jedes Telegramm: „timestamp before 1990, IGNORING“. Dieser Zähler sendet keine gestellte Uhr. Abhilfe: „Zeitstempel“ auf „Rechner-Uhrzeit“ stellen und speichern.',
   'The meter is being read, but vzlogger discards every telegram: „timestamp before 1990, IGNORING“. This meter does not send a set clock. Remedy: set „Timestamp“ to „Computer clock“ and save.'),
  ('ZEITSTEMPEL_ZUSATZ',
   'Die Einstellung steht derzeit auf der Uhr des Zählers.',
   'The setting is currently on the clock of the meter.'),
  ('ALLE_NULL',
   'Alle %s Kanäle stehen auf last=0 - es ist noch kein einziges Telegramm angekommen. Prüfe Sitz des Lesekopfs, Baudrate und Protokoll. Das Protokoll unten zeigt, was vzlogger meldet.',
   'All %s channels are at last=0 - not a single telegram has arrived yet. Check the seating of the optical head, the baud rate and the protocol. The log below shows what vzlogger reports.'),
  ('WERTE_OK',
   '%s von %s Kanälen liefern Werte, letzter Empfang vor %s Sekunden.',
   '%s of %s channels deliver values, last reception %s seconds ago.'),

  ('ALTER_HINWEIS',  # (1) Alter in Sekunden
   "Diese Diagnose ist zwischengespeichert und %s Sekunden alt. Sie wird "
   "höchstens alle 300 Sekunden neu erhoben — sie fragt sonst bei jedem "
   "Seitenaufbau die serielle Schnittstelle und das Netz ab.",
   "This diagnosis is cached and %s seconds old. It is refreshed at most "
   "every 300 seconds — otherwise it would query the serial port and the "
   "network on every page load."),
 ]),
 ('PROFIL', [
  ('OFFEN',
   'noch nicht festgelegt',
   'not yet chosen'),
  ('MANUELL',
   'von Hand einstellen',
   'set by hand'),
  ('D0',
   'Allgemeines D0-Protokoll',
   'Generic D0 protocol'),
  ('SML',
   'Allgemeines SML-Protokoll',
   'Generic SML protocol'),
 ]),
 ('TAKT', [
  ('MIN01',
   'jede Minute',
   'every minute'),
  ('MIN03',
   'alle 3 Minuten',
   'every 3 minutes'),
  ('MIN05',
   'alle 5 Minuten',
   'every 5 minutes'),
  ('MIN10',
   'alle 10 Minuten',
   'every 10 minutes'),
  ('MIN15',
   'alle 15 Minuten',
   'every 15 minutes'),
  ('MIN30',
   'alle 30 Minuten',
   'every 30 minutes'),
  ('STUENDLICH',
   'stündlich',
   'hourly'),

  ('START',
   "nur beim Systemstart – eine Ablesung je Neustart",
   "only at system start – one reading per reboot"),
 ]),
 ('CRON', [
  ('ABGESCHALTET',
   'Der klassische Leser ist abgeschaltet, alle Cron-Einträge entfernt.',
   'The classic reader is switched off, all cron entries removed.'),
  ('UNBEKANNT',
   'Unbekannter Abfragetakt.',
   'Unknown polling interval.'),
  ('DATEI_FEHLT',
   'Die Datei %s fehlt.',
   'The file %s is missing.'),
  ('ORDNER_FEHLT',
   'Den Ordner %s gibt es nicht.',
   'The folder %s does not exist.'),
  ('LINK_FEHLER',
   'Die Verknüpfung %s ließ sich nicht anlegen.',
   'The link %s could not be created.'),
  ('GESETZT',
   'Abfragetakt gesetzt: %s.',
   'Polling interval set: %s.'),

  ('LAGE_UNBEKANNT',
   "Der Cron-Ordner ließ sich nicht lesen. Ob ein Abfragetakt eingerichtet "
   "ist, ist von hier aus nicht feststellbar.",
   "The cron folder could not be read. Whether a polling cycle is set up "
   "cannot be determined from here."),
  ('LAGE_VERZEICHNIS',  # (1) Namen
   "Statt einer Verknüpfung liegt dort ein Verzeichnis: %s. Cron führt es "
   "nicht aus. Es muss von Hand entfernt werden.",
   "A directory is there instead of a link: %s. Cron does not execute it. It "
   "has to be removed by hand."),
  ('LAGE_UEBERZAEHLIG',  # (1) Namen
   "Der Leser ist abgeschaltet, es liegen aber noch Einträge: %s. Sie werden "
   "weiter ausgeführt.",
   "The reader is switched off, but entries are still there: %s. They keep "
   "being executed."),
  ('LAGE_AUS',
   "Der klassische Leser ist abgeschaltet, es liegt kein Cron-Eintrag.",
   "The classic reader is switched off, there is no cron entry."),
  ('LAGE_FEHLT',
   "Der klassische Leser ist eingeschaltet, aber es liegt kein einziger "
   "Cron-Eintrag. Es wird nichts abgefragt. Einmal Speichern setzt ihn.",
   "The classic reader is switched on, but there is not a single cron entry. "
   "Nothing is being polled. Saving once sets it."),
  ('LAGE_MEHRFACH',  # (1) Namen
   "Es liegen mehrere Cron-Einträge nebeneinander: %s. Der Zähler wird "
   "mehrfach abgefragt; zwei Abfragen gleichzeitig behindern sich an der "
   "seriellen Schnittstelle.",
   "Several cron entries exist side by side: %s. The meter is polled several "
   "times; two simultaneous readings get in each other's way at the serial "
   "port."),
  ('LAGE_FALSCH',  # (2) gefunden, erwartet
   "Der Cron-Eintrag steht in %s, eingestellt ist aber %s. Es gilt der "
   "Eintrag, nicht die Einstellung.",
   "The cron entry is in %s, but the setting says %s. The entry applies, not "
   "the setting."),
  ('LAGE_OK',  # (1) Ordner
   "Genau ein Cron-Eintrag, in %s — passend zur Einstellung.",
   "Exactly one cron entry, in %s — matching the setting."),
 ]),
 ('LOG', [
  ('H_PROTOKOLLE',
   'Protokolle',
   'Logs'),
  ('H_LOXBERRY',
   'Logdateien des LoxBerry',
   'Log files of the LoxBerry'),
  ('HINT',
   'Die letzten Zeilen aus %s und %s.',
   'The last lines from %s and %s.'),

  ('RAMDISK',
   "Die Protokolle liegen auf der Ramdisk. Sie sind nach jedem Neustart des "
   "LoxBerry leer — was hier fehlt, ist deshalb nicht unbedingt nie "
   "geschrieben worden.",
   "The logs live on the ramdisk. They are empty after every reboot of the "
   "LoxBerry — so what is missing here has not necessarily never been "
   "written."),
  ('NOCH_NICHTS',
   "Es wurde noch nichts protokolliert.",
   "Nothing has been logged yet."),
 ]),
 ('LEGENDE', [
  ('LESEN',
   'Ansehen — fragt nur ab, verändert nichts',
   'View — only reads, changes nothing'),
  ('VZ_INSTALL',
   'Richtet eine Paketquelle ein und installiert ein Paket',
   'Sets up a package source and installs a package'),
  ('VZ_NEUSTART',
   'Unterbricht das Lesen kurz',
   'Interrupts reading briefly'),
  ('VZ_SPEICHERN',
   'Schreibt die Konfiguration neu und unterbricht das Lesen kurz',
   'Rewrites the configuration and interrupts reading briefly'),
  ('LG_ABFRAGEN',
   'Ansehen — fragt den Zähler einmal ab',
   'View — polls the meter once'),
  ('LG_CACHE',
   'Technischer Eingriff — verwirft zwischengespeicherte Werte',
   'Technical action — discards cached values'),
  ('LG_SPEICHERN',
   'Ändert den Abfragetakt',
   'Changes the polling interval'),
  ('MQ_SPEICHERN',
   'Ändert, wohin die Werte gemeldet werden',
   'Changes where the values are reported to'),

  ('SICHERN', "Ansehen — lädt die Einstellungen als Datei herunter",
   "Read only — downloads the settings as a file"),
  ('LADEN', "Ändert alle Einstellungen und zieht den Dienst nach",
   "Changes all settings and restarts the service accordingly"),
  ('VORLAGE', "Technischer Eingriff — erzeugt eine Datei für Loxone Config",
   "Technical action — creates a file for Loxone Config"),
  ('TOKEN', "Ändert die Adresse, unter der der Miniserver liest",
   "Changes the address the Miniserver reads from"),
 ]),
]

HILFE = [
 ('K01',
  'Smartmeter Classic',
  'Smartmeter Classic'),
 ('K02',
  'LoxBerry-Plugin zum Auslesen von Stromzählern über optische IR-Leseköpfe — mit <b>beiden</b> Lesewegen: dem klassischen Perl-Leser und vzlogger.',
  'A LoxBerry plugin for reading electricity meters through optical IR reading heads — with <b>both</b> reading routes: the classic Perl reader and vzlogger.'),
 ('K03',
  "<b>Abspaltung.</b> Dieses Plugin führt das eingestellte <a href='https://github.com/mschlenstedt/LoxBerry-Plugin-Smartmeter' target='_blank'>Smartmeter-Plugin</a> von Michael Schlenstedt weiter. Dessen Nachfolger <a href='https://github.com/mschlenstedt/LoxBerry-Plugin-Smartmeter-NG' target='_blank'>Smartmeter-NG</a> setzt ausschließlich auf vzlogger und hat den Legacy-Leser entfernt. Einzelheiten und Lizenzangaben stehen in der Datei <code>NOTICE</code> im Plugin-Verzeichnis und im <a href='https://github.com/timanders22/LoxBerry-Plugin-Smartmeter-classic' target='_blank'>Repository dieser Abspaltung</a>.",
  "<b>A fork.</b> This plugin continues the discontinued <a href='https://github.com/mschlenstedt/LoxBerry-Plugin-Smartmeter' target='_blank'>Smartmeter plugin</a> by Michael Schlenstedt. Its successor <a href='https://github.com/mschlenstedt/LoxBerry-Plugin-Smartmeter-NG' target='_blank'>Smartmeter-NG</a> relies exclusively on vzlogger and has removed the legacy reader. Details and licence information are in the file <code>NOTICE</code> in the plugin directory and in the <a href='https://github.com/timanders22/LoxBerry-Plugin-Smartmeter-classic' target='_blank'>repository of this fork</a>."),
 ('K04',
  'Warum zwei Lesewege',
  'Why two reading routes'),
 ('K05',
  'vzlogger ist der modernere Weg und für die meisten Zähler die bessere Wahl. Er ist aber nicht überall verfügbar oder erfolgreich:',
  'vzlogger is the more modern route and the better choice for most meters. But it is not available or successful everywhere:'),
 ('K06',
  'Auf manchen Installationen lässt sich kein passendes vzlogger-Paket installieren.',
  'On some installations no suitable vzlogger package can be installed.'),
 ('K07',
  'Manche Zähler liefern Telegramme, die vzlogger verwirft, bevor man den Grund kennt.',
  'Some meters deliver telegrams that vzlogger discards before you know why.'),
 ('K08',
  'Der klassische Perl-Leser braucht kein zusätzliches Programm und liest solche Zähler weiterhin. <b>Beide Wege stehen in diesem Plugin nebeneinander</b> — man wählt, was funktioniert.',
  'The classic Perl reader needs no additional program and keeps reading such meters. <b>Both routes exist side by side in this plugin</b> — you choose whichever works.'),
 ('K09',
  '<b>Achtung:</b> Nur <b>einer</b> von beiden darf gleichzeitig aktiv sein — eine serielle Schnittstelle kann immer nur ein Prozess öffnen. Die Diagnose warnt, wenn beide auf dasselbe Gerät zugreifen.',
  '<b>Careful:</b> only <b>one</b> of the two may be active at a time — a serial interface can only ever be opened by one process. The diagnosis warns if both access the same device.'),
 ('K10',
  'Oberfläche',
  'Interface'),
 ('K11',
  'Die Diagnose',
  'The diagnosis'),
 ('K12',
  'Der Reiter <i>vzLogger</i> prüft acht Dinge einzeln und zeigt Haken, Ausrufezeichen oder Kreuz: Betriebsart, Programm, Prozess, Konfiguration, Lesekopf, Belegung der Schnittstelle, HTTP-Schnittstelle, Messwerte. <b>Die erste rote Zeile von oben ist die Ursache</b>, alles darunter meist die Folge. Im Reiter <i>Test</i> steht zusätzlich ein Selbsttest mit vierzehn Zeilen, der das Plugin selbst prüft — Katalog, Themen, Reiter, Formulare, Gateway. Ein <b>Strich</b> dort heißt „hier ist nichts zu messen“ und ausdrücklich nicht „in Ordnung“.',
  'The <i>vzLogger</i> tab checks eight things one by one and shows a tick, an exclamation mark or a cross: operating mode, program, process, configuration, reading head, port usage, HTTP interface, readings. <b>The first red line from the top is the cause</b>, everything below it is usually the consequence. The <i>Test</i> tab additionally holds a self-test of fourteen lines checking the plugin itself — catalogue, topics, tabs, forms, gateway. A <b>dash</b> there means „nothing to measure here“ and expressly not „all good“.'),
 ('K13',
  'Darunter stehen die letzten Zeilen des vzlogger-Protokolls. Genau daran hing die Fehlersuche, aus der dieses Plugin entstanden ist: vzlogger las den Zähler einwandfrei und verwarf jedes Telegramm, weil der Zähler keine gestellte Uhr sendet. Ohne Protokoll ist das nicht zu finden.',
  'Below that are the last lines of the vzlogger log. That is exactly what the troubleshooting that gave rise to this plugin hinged on: vzlogger read the meter perfectly and discarded every telegram because the meter sends no set clock. Without the log that cannot be found.'),
 ('K14',
  'vzlogger',
  'vzlogger'),
 ('K15',
  'Das Plugin liefert <b>kein</b> vzlogger mit. Es installiert es bei Bedarf aus der signierten Paketquelle von volkszaehler.org — der Paketmanager löst die Abhängigkeiten passend zur eigenen Debian-Fassung und Architektur auf.',
  'The plugin does <b>not</b> ship vzlogger. It installs it if needed from the signed package source of volkszaehler.org — the package manager resolves the dependencies to match your own Debian version and architecture.'),
 ('K16',
  'Der vom Paket mitgebrachte systemd-Dienst wird dabei abgeschaltet und maskiert; vzlogger wird vom Plugin gestartet und von einem Wächter überwacht, der es nach Update, Neustart und Absturz binnen einer Minute zurückholt.',
  'The systemd service that comes with the package is switched off and masked in the process; vzlogger is started by the plugin and watched by a guard that brings it back within a minute after an update, a restart or a crash.'),
 ('K17',
  'Beim Deinstallieren wird vzlogger nur entfernt, wenn dieses Plugin es installiert hat.',
  'On uninstalling, vzlogger is only removed if this plugin installed it.'),
 ('K18',
  'Werte an den Miniserver',
  'Values to the Miniserver'),
 ('K19',
  '<b>MQTT ist der Standardweg.</b> Themen:',
  '<b>MQTT is the standard route.</b> Topics:'),
 ('K20',
  '&lt;Präfix&gt;/&lt;Zählernummer&gt;/&lt;Kennzahl&gt;',
  '&lt;prefix&gt;/&lt;meter number&gt;/&lt;OBIS code&gt;'),
 ('K21',
  '<b>Beide Betriebsarten senden dasselbe Schema</b> — dieselben Schlüssel, dasselbe Thema, denselben UDP-Satz. Ein Wechsel zwischen klassischem Leser und vzlogger ändert im Miniserver nichts, solange im Reiter <i>vzLogger</i> dieselbe <b>Zählernummer</b> eingetragen ist.',
  '<b>Both operating modes send the same scheme</b> — the same keys, the same topic, the same UDP record. Switching between the classic reader and vzlogger changes nothing on the Miniserver, as long as the same <b>meter number</b> is entered on the <i>vzLogger</i> tab.'),
 ('K22',
  'Das MQTT-Gateway ersetzt in den Themen nur <code>/</code> und <code>%</code> durch <code>_</code>; Punkte bleiben stehen. Der virtuelle Eingang heißt also <code>smartmeter_1234_Consumption_Total_OBIS_1.8.0</code>.',
  'In the topics the MQTT gateway only replaces <code>/</code> and <code>%</code> with <code>_</code>; dots stay. So the virtual input is called <code>smartmeter_1234_Consumption_Total_OBIS_1.8.0</code>.'),
 ('K23',
  'In der vzLogger-Betriebsart abgeleitete Werte',
  'Values derived in vzLogger mode'),
 ('K24',
  'vzlogger liefert weder Zeitstempel noch die kalkulierten Leistungen. Das Plugin ergänzt sie, damit vorhandene Auswertungen weiterlaufen:',
  'vzlogger delivers neither timestamps nor the calculated power values. The plugin adds them so that existing evaluations keep working:'),
 ('K25',
  '<b>Der klassische Leser rechnet die beiden letzten anders</b> — aus dem Zählerfortschritt. Für Zähler mit <code>16.7.0</code> ist die Ableitung genauer, aber es ist nicht dieselbe Größe. Wer beide Betriebsarten vergleicht, wird kleine Unterschiede sehen.',
  '<b>The classic reader calculates the last two differently</b> — from the progress of the meter reading. For meters with <code>16.7.0</code> the derivation is more precise, but it is not the same quantity. Anyone comparing the two modes will see small differences.'),
 ('K26',
  'Ob im MQTT-Gateway ein Abo einzutragen ist, hängt an seiner Fassung. <b>Gateway V1:</b> das Abo <code>&lt;Präfix&gt;/#</code> muss eingetragen sein, sonst kommt am Miniserver nichts an. <b>Gateway V2:</b> das Gateway erkennt die Themengruppe von selbst, ein Abo ist nicht einzutragen — der Kern schaltet die Knöpfe dafür sogar ab. Welche Fassung hier läuft, steht im Reiter <i>MQTT</i>; dort steht auch nur der Satz, der auf diese Anlage zutrifft.',
  'Whether a subscription has to be entered in the MQTT gateway depends on its version. <b>Gateway V1:</b> the subscription <code>&lt;prefix&gt;/#</code> has to be entered, otherwise nothing arrives at the Miniserver. <b>Gateway V2:</b> the gateway detects the topic group by itself, no subscription needs to be entered — the core even disables the buttons for it. Which version is running here is shown in the <i>MQTT</i> tab; that tab shows only the sentence that applies to this installation.'),
 ('K27',
  'UDP steht weiterhin zur Verfügung, wo es gebraucht wird.',
  'UDP is still available where it is needed.'),
 ('K28',
  'Zähler ohne gestellte Uhr',
  'Meters without a set clock'),
 ('K29',
  'Viele Haushaltszähler senden keinen gültigen Zeitstempel. vzlogger verwirft solche Telegramme mit <code>timestamp before 1990, IGNORING</code> — der Zähler wird gelesen, aber kein Wert kommt an.',
  'Many household meters send no valid timestamp. vzlogger discards such telegrams with <code>timestamp before 1990, IGNORING</code> — the meter is read, but no value arrives.'),
 ('K30',
  'Die Einstellung <b>Zeitstempel</b> steht deshalb standardmäßig auf <i>Rechner-Uhrzeit</i>. Der Zeitstempel des Zählers wird nur gebraucht, wenn eine Middleware eine Zeitreihe erwartet; bei der Weitergabe an den Miniserver stempelt dieser selbst.',
  "That is why the <b>timestamp</b> setting defaults to <i>machine time</i>. The meter's timestamp is only needed if a middleware expects a time series; when passing values on to the Miniserver, the Miniserver stamps them itself."),
 ('K31',
  'Voraussetzungen',
  'Prerequisites'),
 ('K32',
  'LoxBerry ab 3.0.0 (so steht es auch in der plugin.cfg)',
  'LoxBerry 3.0.0 or newer (as stated in plugin.cfg)'),
 ('K33',
  'optischer IR-Lesekopf am USB — die udev-Regel legt das Plugin an',
  'an optical IR reading head on USB — the plugin creates the udev rule'),
 ('K34',
  'für die vzLogger-Betriebsart ein installierbares vzlogger-Paket',
  'for vzLogger mode, an installable vzlogger package'),
 ('K35',
  'Reiter',
  'Tab'),
 ('K36',
  'Inhalt',
  'Contents'),
 ('K37',
  '<b>Smartmeter (vzLogger)</b>',
  '<b>Smartmeter (vzLogger)</b>'),
 ('K38',
  'Einstellungen und eine achtstufige Diagnose',
  'settings and an eight-step diagnosis'),
 ('K39',
  '<b>Smartmeter (klassisch)</b>',
  '<b>Smartmeter (classic)</b>'),
 ('K40',
  'der klassische Leser mit Zählerprofilen',
  'the classic reader with meter profiles'),
 ('K41',
  '<b>MQTT</b>',
  '<b>MQTT</b>'),
 ('K42',
  'die einzige Stelle, an der MQTT eingestellt wird',
  'the only place where MQTT is configured'),
 ('K43',
  '<b>Einbindung in Loxone</b>',
  '<b>Loxone integration</b>'),
 ('K44',
  'MQTT-Themen, UDP-Port, HTTP-Adresse — mit den gespeicherten Werten',
  'MQTT topics, UDP port, HTTP address — with the saved values'),
 ('K45',
  '<b>Test</b>',
  '<b>Test</b>'),
 ('K46',
  'Selbsttest, Diagnose und Knopfreihen nach Farbregel',
  'self-test, diagnosis and button rows following the colour rule'),
 ('K47',
  '<b>Logdateien</b>',
  '<b>Log files</b>'),
 ('K48',
  'vzlogger- und Abholprotokoll',
  'the vzlogger and the collection log'),
 ('K49',
  'Schlüssel',
  'Key'),
 ('K50',
  'Herkunft',
  'Origin'),
 ('K51',
  '<code>Last_Update</code>, <code>Last_UpdateLoxEpoche</code>',
  '<code>Last_Update</code>, <code>Last_UpdateLoxEpoche</code>'),
 ('K52',
  'Rechner-Uhrzeit zum Abholzeitpunkt',
  'machine time at the moment of collection'),
 ('K53',
  '<code>Consumption_CalculatedPower_OBIS_1.99.0</code>',
  '<code>Consumption_CalculatedPower_OBIS_1.99.0</code>'),
 ('K54',
  'aus <code>16.7.0</code>, positiver Anteil',
  'from <code>16.7.0</code>, the positive part'),
 ('K55',
  '<code>Delivery_CalculatedPower_OBIS_2.99.0</code>',
  '<code>Delivery_CalculatedPower_OBIS_2.99.0</code>'),
 ('K56',
  'aus <code>16.7.0</code>, negativer Anteil',
  'from <code>16.7.0</code>, the negative part'),
 ('K57',
  '<code>Last_UpdateUnix</code>',
  '<code>Last_UpdateUnix</code>'),
 ('K58',
  'dieselbe Uhrzeit als Zahl — geschrieben nur, wenn wirklich ein Wert gelesen wurde',
  'the same time as a number — written only if a value was actually read'),
 ('K59',
  '<code>ZAEHLER</code>',
  '<code>ZAEHLER</code>'),
 ('K60',
  'zählt jede erfolgreiche Ablesung, läuft bei 999 auf 0 zurück',
  'counts every successful reading, wraps from 999 back to 0'),
 ('K61',
  'Einstellungen sichern und zurückspielen',
  'Backing up and restoring the settings'),
 ('K62',
  'Im Reiter <i>Smartmeter (vzLogger)</i> stehen zwei Knöpfe. <i>Einstellungen sichern</i> lädt eine Textdatei mit allen Einstellungen beider Lesewege herunter — Zählerprofile, Bezeichnungen, Abfragetakt, Themenpräfix und das Zugriffstoken. <i>Sicherung zurückspielen</i> liest sie wieder ein.',
  'The <i>Smartmeter (vzLogger)</i> tab holds two buttons. <i>Back up settings</i> downloads a text file with all settings of both reading routes — meter profiles, labels, polling cycle, topic prefix and the access token. <i>Restore backup</i> reads it back in.'),
 ('K63',
  '<b>Die Datei trägt das Zugriffstoken im Klartext.</b> Ohne das wäre sie nach dem Zurückspielen wertlos — der Miniserver käme mit der alten Adresse nicht mehr durch. Sie gehört deshalb nicht in ein Forum. Zurückgespielt wird nur eine Datei, die sich durchgängig lesen lässt: findet sich auch nur eine unverständliche Zeile, bleibt alles, wie es ist. Eine halb eingelesene Konfiguration wäre schlimmer als gar keine, weil sie aussieht wie eine ganze.',
  '<b>The file carries the access token in plain text.</b> Without it the file would be worthless after restoring — the Miniserver would no longer get through with the old address. So it does not belong in a forum. Only a file that can be read from beginning to end is restored: if even a single line cannot be understood, everything stays as it is. A half-read configuration would be worse than none, because it looks like a whole one.'),
 ('K64',
  'Das richtige Zählerprofil finden',
  'Finding the right meter profile'),
 ('K65',
  'Der klassische Leser braucht ein Zählerprofil; 41 Modelle sind hinterlegt. Steht das eigene nicht darunter, probiert der <i>Suchlauf</i> im Reiter <i>Smartmeter (klassisch)</i> vier allgemeine Lesewege durch und zeigt, welcher antwortet. Er ändert nichts und schlägt nur vor — und er schlägt nur dann etwas vor, wenn genau ein Weg geantwortet hat. Antworten mehrere, entscheidet der Zählertyp, nicht der Suchlauf. Der Suchlauf braucht die serielle Schnittstelle für sich und dauert bis zu einer Minute.',
  'The classic reader needs a meter profile; 41 models are on file. If yours is not among them, the <i>search</i> in the <i>Smartmeter (classic)</i> tab tries four generic reading routes and shows which one answers. It changes nothing and only suggests — and it only suggests something if exactly one route answered. If several answer, the meter type decides, not the search. The search needs the serial port to itself and takes up to a minute.'),
 ('K66',
  'Wenn der Zähler schweigt',
  'When the meter goes silent'),
 ('K67',
  'Das ist der unangenehmste Fall, weil er nach nichts aussieht: in Loxone behält ein virtueller Eingang seinen <b>letzten Wert</b>. Auf dem Bildschirm sieht ein stummer Zähler deshalb aus wie ein ruhiger Tag.',
  'This is the nastiest case because it looks like nothing at all: in Loxone a virtual input keeps its <b>last value</b>. On screen a silent meter therefore looks like a quiet day.'),
 ('K68',
  'Dagegen gibt es drei Dinge. <code>ZAEHLER</code> ändert sich bei jeder erfolgreichen Ablesung, auch wenn der Zählerstand stillsteht — Schritt 6 im Reiter <i>Einbindung in Loxone</i> baut daraus eine Meldung. Der Selbsttest im Reiter <i>Test</i> nennt das Alter der letzten Messung. Und der <i>Healthcheck</i> des LoxBerry fragt dieses Plugin von sich aus — auch dann, wenn niemand die Plugin-Seite öffnet.',
  'There are three things against that. <code>ZAEHLER</code> changes with every successful reading, even while the meter reading stands still — step 6 in the <i>Loxone integration</i> tab builds an alert from it. The self-test in the <i>Test</i> tab names the age of the last reading. And the LoxBerry <i>healthcheck</i> queries this plugin by itself — even when nobody opens the plugin page.'),
]

KOPF_DE = """; Smartmeter classic - deutsche Texte
;
; ERZEUGT von Werkzeuge/sm_sprache_erzeugen.py - NICHT von Hand aendern.
; Wer hier etwas aendert, aendert den Erzeuger im selben Zug; sonst gibt es
; zwei Wahrheiten im selben Archiv, und die eine loescht die andere beim
; naechsten Lauf.
;
; Gelesen von sm_t() in webfrontend/htmlauth/sm_lib.php. Die Schluessel sind
; mit language_en.ini deckungsgleich; Englisch ist die Rueckfallebene.
;
; HINWEIS: echte UTF-8-Zeichen, keine HTML-Entitaeten. Attribute in
; Auszeichnung sind EINFACH quotiert (class='sm-mono') - ein zweites
; doppeltes Anfuehrungszeichen beendet den Wert vorzeitig, und zwar still.
; %s sind Platzhalter (sprintf) und muessen in Zahl und Reihenfolge
; erhalten bleiben.
"""

KOPF_EN = """; Smartmeter classic - English texts
;
; GENERATED by Werkzeuge/sm_sprache_erzeugen.py - do NOT edit by hand.
; If you change something here, change the generator in the same go;
; otherwise there are two truths in the same archive, and one deletes the
; other on the next run.
;
; Read by sm_t() in webfrontend/htmlauth/sm_lib.php. The keys match
; language_de.ini; English is the fallback level.
;
; NOTE: real UTF-8 characters here, no HTML entities. Attributes in markup
; are quoted with SINGLE quotes - a second double quote would end the value
; early, and silently. %s are placeholders (sprintf) and must be kept in
; number and order.
"""

HILFE_KOPF_DE = """; Hilfetexte, deutsch. Gehoert zu templates/help/help.html.
;
; ERZEUGT von Werkzeuge/sm_sprache_erzeugen.py - NICHT von Hand aendern.
;
; LBWeb::gethelp() leitet den Namen dieser Datei aus dem Namen der
; Hilfedatei ab und sucht sie in templates/lang/ - nicht neben der Hilfe.
; Jeder Wert steht in doppelten Anfuehrungszeichen und enthaelt selbst
; keine; Auszeichnung bleibt roh, die Hilfe wird nicht maskiert ausgegeben.
"""

HILFE_KOPF_EN = """; Help texts, English. Belongs to templates/help/help.html.
;
; GENERATED by Werkzeuge/sm_sprache_erzeugen.py - do NOT edit by hand.
;
; LBWeb::gethelp() derives the name of this file from the name of the help
; file and looks for it in templates/lang/ - not next to the help file.
; Every value is in double quotes and contains none itself; markup stays
; raw, the help is not output escaped.
"""


def bauen(index):
    zeilen = []
    for abschnitt, paare in TEXTE:
        zeilen.append("")
        zeilen.append("[%s]" % abschnitt)
        for eintrag in paare:
            schluessel = eintrag[0]
            wert = eintrag[index]
            if '"' in wert:
                raise SystemExit("Gerades Anfuehrungszeichen in %s.%s"
                                 % (abschnitt, schluessel))
            if "\n" in wert or "\r" in wert:
                raise SystemExit("Zeilenumbruch im Wert %s.%s"
                                 % (abschnitt, schluessel))
            zeilen.append('%s = "%s"' % (schluessel, wert))
    return zeilen


def main():
    ziel = Path(sys.argv[1]) if len(sys.argv) > 1 else VORGABE
    lang = ziel / "templates" / "lang"
    if not lang.is_dir():
        raise SystemExit("Kein Sprachordner: %s" % lang)

    # Dublettenprobe: derselbe Schluessel zweimal im selben Abschnitt wuerde
    # von parse_ini_file stillschweigend als der LETZTE gelesen. Genau daran
    # ist anderswo eine Ueberschrift zu einem langen Hinweistext geworden.
    for abschnitt, paare in TEXTE:
        namen = [p[0] for p in paare]
        if len(namen) != len(set(namen)):
            doppelt = sorted(set(n for n in namen if namen.count(n) > 1))
            raise SystemExit("Doppelter Schluessel in [%s]: %s"
                             % (abschnitt, ", ".join(doppelt)))
    abschnitte = [a for a, _ in TEXTE]
    if len(abschnitte) != len(set(abschnitte)):
        raise SystemExit("Doppelter Abschnitt in TEXTE")

    # Die Laengengrenze der Bedeutungen. Sie landen als Comment eines
    # Befehls in der Loxone-Vorlage, und Loxone Config macht daraus den
    # Anzeigenamen. sm_test.php misst mit strlen() - also in BYTE, ein
    # Umlaut zaehlt zwei. Hier wird deshalb genauso gemessen.
    #
    # Aufgefallen ist die Grenze am 26.08.2026, als drei frisch
    # geschriebene Bedeutungen sie rissen und der Selbsttest ein Kreuz
    # zeigte. Besser hier abbrechen als dort melden.
    for abschnitt, paare in TEXTE:
        if abschnitt not in ("FELD", "OBIS"):
            continue
        for eintrag in paare:
            for index, sprache in ((1, "deutsch"), (2, "englisch")):
                n = len(eintrag[index].encode("utf-8"))
                if n > 40:
                    raise SystemExit(
                        "%s.%s (%s) ist %d Byte lang - hoechstens 40 sind "
                        "erlaubt, sonst wird der Anzeigename in Loxone "
                        "Config zum Satz." % (abschnitt, eintrag[0],
                                              sprache, n))

    # Ein leerer Wert ist kein Text, sondern ein vergessener Text: sm_t()
    # gaebe ihn zurueck, und die Stelle bliebe stumm statt aufzufallen.
    for abschnitt, paare in TEXTE:
        for eintrag in paare:
            for index, sprache in ((1, "deutsch"), (2, "englisch")):
                if eintrag[index].strip() == "":
                    raise SystemExit("Leerer Wert (%s) in %s.%s"
                                     % (sprache, abschnitt, eintrag[0]))

    for datei, kopf, index in (("language_de.ini", KOPF_DE, 1),
                               ("language_en.ini", KOPF_EN, 2)):
        text = kopf + "\n".join(bauen(index)) + "\n"
        # Beide Sprachdateien sind im Bestand CRLF - das bleibt so.
        (lang / datei).write_bytes(text.replace("\n", "\r\n").encode("utf-8"))

    # --- Die Hilfe ---------------------------------------------------
    #
    # Sie wird gegen help.html gegengeprueft, und zwar in BEIDE
    # Richtungen: ein Platzhalter ohne Text erschiene beim Leser als
    # roher Schluesselname, ein Text ohne Platzhalter waere geschrieben
    # und wuerde nie jemand lesen. Keines von beidem faellt sonst auf.
    namen = [h[0] for h in HILFE]
    if len(namen) != len(set(namen)):
        doppelt = sorted(set(x for x in namen if namen.count(x) > 1))
        raise SystemExit("Doppelter Hilfeschluessel: %s" % ", ".join(doppelt))
    hilfe_html = ziel / "templates" / "help" / "help.html"
    if hilfe_html.is_file():
        html = hilfe_html.read_text(encoding="utf-8")
        benutzt = set(re.findall(r"TMPL_VAR\s+HILFE\.(K\d+)", html))
        da = set(namen)
        if benutzt - da:
            raise SystemExit("help.html benutzt Schluessel ohne Text: %s"
                             % ", ".join(sorted(benutzt - da)))
        if da - benutzt:
            raise SystemExit("Text ohne Platzhalter in help.html: %s"
                             % ", ".join(sorted(da - benutzt)))
        print("Hilfe: %d Platzhalter, %d Texte - deckungsgleich."
              % (len(benutzt), len(da)))
    for datei, kopf, index in (("help_de.ini", HILFE_KOPF_DE, 1),
                               ("help_en.ini", HILFE_KOPF_EN, 2)):
        zeilen = ["", "[HILFE]"]
        for eintrag in HILFE:
            if '"' in eintrag[index]:
                raise SystemExit("Gerades Anfuehrungszeichen in HILFE.%s"
                                 % eintrag[0])
            if eintrag[index].strip() == "":
                raise SystemExit("Leerer Hilfetext HILFE.%s" % eintrag[0])
            zeilen.append('%s = "%s"' % (eintrag[0], eintrag[index]))
        # Die Hilfedateien sind im Bestand LF - das bleibt so.
        (lang / datei).write_bytes(
            (kopf + "\n".join(zeilen) + "\n").encode("utf-8"))

    n = sum(len(p) for _, p in TEXTE)
    print("%d Schluessel in %d Abschnitten, %d Hilfetexte geschrieben."
          % (n, len(TEXTE), len(HILFE)))
    for datei in ("language_de.ini", "language_en.ini",
                  "help_de.ini", "help_en.ini"):
        b = (lang / datei).read_bytes()
        crlf = b.count(b"\r\n")
        # Nach dem TATSAECHLICHEN Zeilenende trennen. Ein festes "\r\n"
        # liefert bei den LF-Hilfedateien genau einen Brocken und meldet
        # damit "1 Schluessel" - eine Zahl, die nach einem Befund aussieht
        # und keiner ist.
        anzahl = sum(1 for z in b.decode("utf-8").splitlines() if " = " in z)
        print("  %-16s %5d Schluessel, CRLF %d, reine LF %d, %d Byte"
              % (datei, anzahl, crlf, b.count(b"\n") - crlf, len(b)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
