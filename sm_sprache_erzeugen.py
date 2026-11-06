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

STAND (vb_x10_smc, 09.10.2026, Welle X-10): Baustein-Liste in der Grammatik von
Werkzeuge/leitungen_setzen.py 1.1 - LOX.EINGAENGE entfaellt (einziger Leser war
Zelle #11), dafuer LOX.WEITERE ("I1 = #10, I2 = weitere eigene Meldungen ...").

STAND (vb_bild_smc, 10.10.2026, Welle Bild 7 / Musterprojekt): Schritt 6 im Reiter
Einbindung in Loxone zeigt zwei Baustein-Listen (Leseweg klassisch / vzLogger), wortgleich
mit Musterprojekt/baustein_listen.txt. Neu LOX.BL_*, LOX.BILD_*, LOX.MUSTERPROJEKT und die
Zellen BAUSTEIN.VHTTP_TYP, B*_TYP/NAME/PARAM/VERB, H_*; entfallen die alten Typnamen
[BAUSTEIN], LOX.N_*/P_*/Q_ENDPUNKT/EINGANG/WEITERE, LOX.S6_STATUSTEXT, S6_ZU4/10/1112
(samt _TEXT) und ALLG.OPTIONAL - ihr einziger Leser war die alte Liste.

STAND (vb_bild_smc11, 13.10.2026, Welle Bild 11 VOLL / Musterprojekt): Schritt 6 zeigt drei
Seiten (klassisch 24, vzLogger 27, Kosten und Fahrplan 25 Zeilen) je mit Kasten, Liste,
Hinweisen und Bild; Knopf und Vorlage VI_smartmeter_kosten.xml. Neu LOX.BL_KOSTEN,
K_VORLAGE_KO, KO_VORLAGE_TEXT, VORLAGE_TITEL_KO, VORLAGE_KOMMENTAR_KO, VE_K_*/VE_A_* und in
[BAUSTEIN] die Zellen der neuen Zeilen, Schritte und Hinweise; neu gefasst LOX.S6_TITEL/_TEXT,
BAUSTEIN.H_TAGESVERBRAUCH (Remanenz), H_BENACHRICHTIGUNG (Entscheidung 8) und
FELD.BEZUG_RECHNERISCH/EINSP_RECHNERISCH (Leistung, Entscheidung 7). Nichts entfaellt.

STAND (vb_bild_smc14, 16.10.2026, Welle Bild 14): neu BAUSTEIN.H_EN - Hinweis zu Nr. 11 auf
beiden Lesewegen: Config legt den Eingang En der Analogwertvalidierung negiert an, der Haken
muss weg. Nichts neu gefasst, nichts entfaellt.

STAND (vb_g1_sm, 18.10.2026, Gruppe 1 - Umstellung auf MQTT): Schritt 2 nach der
Gateway-Fassung (S2_TITEL neu gefasst, neu S2_TITEL_V2/_BEIDE, Hakenliste SP_DATENPUNKT,
SP_ZUSATZ, HAKEN_*), MQ.H_ABO/ABO_PFLICHT/ABO_V2 neu gefasst (die Wendungen fuer
gateway_wirkung.py bleiben), MQ.B_A_AKTIV -1 statt Strich, LOX.S5_TEXT (Lebenszeichen,
drei %s = Praefix), LOX.S6_TEXT (gleiche Eingangsnamen beider Lesewegseiten),
BAUSTEIN.K_H_TAKT; neu B11_PARAM_K, B12_VERB_K/_V, LF_* (Einschaltverzoegerung Nr. 25/28),
PRUEF.Z_HAKEN/HAKEN_*. Gestrichen: LOX.VORLAGE_TITEL, VORLAGE_TITEL_LG, VORLAGE_TITEL_KO
(Titel fest deutsch im Code, sm_vorlage_titel()) und BAUSTEIN.B12_VERB.
NACHTRAG 19.10.2026 (Hausherr: keine Importvorlage VirtualHttpIn fuer Gateway-Werte mehr):
neu LOX.NAMEN_* (Namenstabelle in Schritt 3), SP_BEREICH, SP_ART, KO_NAMEN, PRUEF.HAKEN_ART;
neu gefasst MQ.THEMEN_HINT, LOX.SP_TITEL_VE, BAUSTEIN.K_S3/K_S4/V_S3/V_S4/P_S3/P_S4, H_FEHLT,
P_H_REGELN; gestrichen die Vorlagenknoepfe und -texte (LOX.H_VORLAGE, H_VORLAGE_TEXT, K_VORLAGE,
K_VORLAGE_LG, K_VORLAGE_KO, KO_VORLAGE_TEXT, VORLAGE_LEER, VORLAGE_KOMMENTAR/_LG/_KO,
VORLAGE_TEXTFELDER), LEGENDE.VORLAGE und die XML-Pruefzeile (PRUEF.Z_XML, XML_*).

STAND (vb_g35_sm, 27.10.2026, Gruppe 35 - Smartmeter Classic 2.8.13): neu SICH.KOPF_FELDER/SPAET
(Positivlisten, Spaetliste), VZ.K_PHASEN/HINT_PHASEN/INSTALL_*, AB.LABEL_SPEICHER/HINT_SPEICHER/SL_*
(haus/speicher), KO.H_TAGE/SP_*/T_*/TAGE_LEER/K_CSV (Tagesabschluss), LEGENDE.VZ_PHASEN/EP_SPEICHERN/KO_CSV
(eine Legende je Reiter), LOX.EP_*/LG_* (Schalter), LOX.VE_A_SPEICHER/VE_K_GESTERN_*, MQ.B_K_GESTERN_*/
B_A_SPEICHER, PRUEF.Z_NONCACHED/Z_KOPF/Z_PROFILE/Z_USB/Z_DIENSTDATEI/Z_SPEICHER samt Texten, BAUSTEIN
B4_PARAM_K/_V, T_VQ_BEFEHL, SIG_*, P26-P34 (Entwurf G35 Abschnitt 9, P34 = A1 Musterprojekt-Bau);
neu gefasst AB.FEHLER_URL/SCHRANKE/
U_UNSICHER, KO.NUR_HEUTE/FEHLER_URL, LOX.S5_TEXT/S8_TEXT/KO_NAMEN, MQ.B_STATUS_TS/B_STATUS_ZAEHLER/B_A_SICHER,
BAUSTEIN.B3_PARAM/B11_PARAM/B11_PARAM_K/B18_PARAM_K/LF_PARAM_K/K_H_TAKT/P15/P20/P22/P_H_*; gestrichen
BAUSTEIN.B4_PARAM (je Leseweg). Hilfe: K12, K70 neu gefasst, neu K71-K80.

STAND (vb_g35b_sm, 28.10.2026, Gruppe 35b - Smartmeter Classic 2.8.14, Textnachzug): neu gefasst
BAUSTEIN.P_H_REGELN (je weitere Fahrplan-Regel Nr. 15-25, 33 und 34 kopieren - bisher nur Nr. 15-25).

STAND (Drift-Abgleich, 06.11.2026): angeglichen an Smartmeter-classic 2.8.20, 72 Schluessel neu,
0 Werte geaendert, 0 entfernt (MQ 54 haus/energie und frei_w, PRUEF 2, LEGENDE 2, neuer Abschnitt
[ANSAGEPLUGIN] 10, HILFE K81-K84); dazu der Abschnitt [ANSAGE] (314 Schluessel) nicht als Tabelle,
sondern aus Werkzeuge/gemeinsam_pruefen.ini_abschnitt() vor [ANSAGEPLUGIN] (ANSAGE_VOR).

Aufruf:  python3 Werkzeuge/sm_sprache_erzeugen.py [<Plugin-Ordner>]
Rueckgabe 0, wenn beide Dateien geschrieben wurden.
"""

# NACHGEZOGEN fuer den Durchgangsbau vb_smc (01.10.2026): 66 neue Schluessel, 2 geaenderte Werte,
# 2 neue Hilfetexte - Quelle vb_smc_bau_skripte/werkzeug_bauen.py.
import re
import sys
from pathlib import Path

# BERICHTIGT AM 17.09.2026. Hier stand 2.7.0 - der Ordner einer laengst
# veroeffentlichten Fassung. Ein Aufruf OHNE Argument schrieb die Texte von
# heute dort hinein; gemessen an einer Kopie: language_de.ini von
# e527090fe6e2... auf 24f5b695cf17..., Rueckgabewert 0, ohne Rueckfrage. Der
# Vorgabeordner ist deshalb der, zu dem die Texte gehoeren.
VORGABE = (Path(__file__).resolve().parent.parent
           / "LoxBerry-Plugin-Smartmeter-classic-2.8.3")

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
  ('UNGUELTIG',
   'ungültig',
   'invalid'),
  ('TEIL',
   'Der Vorgang ist nicht ganz gelungen:',
   'The action did not fully succeed:'),
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
  ('VZ_GESPEICHERT_ANGEHALTEN',
   'Gespeichert. Die Konfiguration wurde neu erzeugt; vzlogger ist angehalten, weil die Betriebsart vzLogger ausgeschaltet ist.',
   'Saved. The configuration was rebuilt; vzlogger is stopped because the vzLogger mode is switched off.'),
  ('VZ_ANGEHALTEN',
   'vzlogger ist angehalten – die Betriebsart vzLogger ist ausgeschaltet.',
   'vzlogger is stopped – the vzLogger mode is switched off.'),
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
  ('VZ_KAPUTT',
   'Die Datei %s ist beschädigt (kein gültiges JSON). Gespeichert wird nichts, bis sie berichtigt oder gelöscht ist – sonst überschriebe die angezeigte Werkseinstellung die eigene Einstellung.',
   'The file %s is damaged (no valid JSON). Nothing is saved until it has been repaired or deleted – otherwise the factory defaults shown would overwrite your own settings.'),
  ('VZ_CONF',
   'vzlogger.json ist gespeichert, aber vzlogger.conf ließ sich nicht schreiben. vzlogger wurde deshalb nicht neu gestartet und läuft gegebenenfalls mit der bisherigen Konfiguration.',
   'vzlogger.json has been saved, but vzlogger.conf could not be written. vzlogger was therefore not restarted and may still be running with the previous configuration.'),
  ('PROTOKOLL',
   'Das Protokoll „%s“ gibt es nicht – erlaubt sind SML und D0.',
   'There is no protocol “%s” – SML and D0 are allowed.'),
  ('ZEITSTEMPEL',
   'Die Auswahl beim Zeitstempel ist ungültig.',
   'The timestamp selection is invalid.'),
  ('SERIAL_LEER',
   'Die Zählernummer fehlt. Sie steht im MQTT-Thema und im UDP-Satz.',
   'The meter number is missing. It is part of the MQTT topic and the UDP record.'),
  ('SERIAL',
   'Die Zählernummer „%s“ enthält andere Zeichen als Buchstaben, Ziffern, - und _. Sie wird nicht mehr still gekürzt – bitte selbst berichtigen.',
   'The meter number “%s” contains characters other than letters, digits, - and _. It is no longer shortened silently – please correct it yourself.'),
  ('KANAELE_LEER',
   'Es ist kein OBIS-Kanal eingetragen. Die Vorgabe wird nicht mehr still eingesetzt – mindestens einen Kanal eintragen.',
   'No OBIS channel has been entered. The default is no longer inserted silently – enter at least one channel.'),
  ('PRAEFIX_LEER',
   'Das Themenpräfix fehlt.',
   'The topic prefix is missing.'),
  ('PRAEFIX_STEUERZEICHEN',
   'Das Themenpräfix enthält Steuerzeichen.',
   'The topic prefix contains control characters.'),
  ('PRAEFIX_LEERRAUM',
   'Das Themenpräfix enthält Leerraum. Das MQTT-Gateway trennt Thema und Wert am Leerzeichen – die Werte landeten unter einem anderen Thema.',
   'The topic prefix contains white space. The MQTT gateway splits topic and value at the space – the values would end up under a different topic.'),
  ('PRAEFIX_ANFUEHRUNG',
   'Das Themenpräfix enthält Anführungszeichen.',
   'The topic prefix contains quotation marks.'),
  ('PRAEFIX_PLATZHALTER',
   'Das Themenpräfix enthält # oder +. Das sind Platzhalter für Abonnements; in einem gesendeten Thema weist der Broker sie ab.',
   'The topic prefix contains # or +. These are wildcards for subscriptions; in a published topic the broker rejects them.'),
  ('PRAEFIX_SCHRAEGSTRICH',
   'Das Themenpräfix beginnt oder endet mit / oder enthält // (eine leere Ebene).',
   'The topic prefix starts or ends with / or contains // (an empty level).'),
  ('PRAEFIX_LANG',
   'Das Themenpräfix ist länger als 100 Zeichen.',
   'The topic prefix is longer than 100 characters.'),
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
  ('UPGRADE_LAEUFT',
   "Es läuft gerade eine Aktualisierung dieses Plugins. vzlogger wurde "
   "angehalten, aber nicht neu gestartet — sonst stünden nach der "
   "Aktualisierung zwei Prozesse an derselben seriellen Schnittstelle. "
   "Nach der Installation startet der Minutentakt ihn von selbst.",
   "An update of this plugin is running right now. vzlogger was stopped but "
   "not restarted — otherwise two processes would end up on the same serial "
   "port after the update. The one-minute cron job starts it again once the "
   "installation has finished."),
  ('KAPUTT',
   'Die Datei %s ist beschädigt (kein gültiges JSON). Unten stehen deshalb die Werkseinstellungen, nicht die gespeicherte Einstellung. Speichern ist gesperrt, bis die Datei berichtigt oder gelöscht ist; eine Sicherung lässt sich zurückspielen.',
   'The file %s is damaged (no valid JSON). The form below therefore shows the factory defaults, not the saved settings. Saving is blocked until the file has been repaired or deleted; a backup can be restored.'),
  ('NICHT_BEENDET',
   'Ein laufendes vzlogger ließ sich nicht beenden (PID %s). Bitte im Reiter Test nachsehen und den Prozess von Hand beenden.',
   'A running vzlogger could not be stopped (PID %s). Please check the Test tab and stop the process by hand.'),
  # Gruppe 35 (2.8.13): Schnellknopf Phasen & Spannungen (Fremd-E5), Installation im Hintergrund (T5-2).
  ('K_PHASEN',
   '+ Phasen & Spannungen',
   '+ phases & voltages'),
  ('HINT_PHASEN',
   'Trägt Strom und Spannung L1–L3 als Kanäle ein (31.7.0, 51.7.0, 71.7.0, 32.7.0, 52.7.0, 72.7.0), sofern sie fehlen; gespeichert wird erst mit „Speichern“. Ob der eigene Zähler sie liefert, zeigt %s im Reiter Test (Knopf „Rohwerte“) – am Hauszähler gemessen sind nur 1.8.0, 2.8.0 und 16.7.0.',
   'Adds current and voltage L1–L3 as channels (31.7.0, 51.7.0, 71.7.0, 32.7.0, 52.7.0, 72.7.0) if they are missing; nothing is stored until „Save“. Whether your meter delivers them is shown by %s in the Test tab (button „raw values“) – measured on the house meter are only 1.8.0, 2.8.0 and 16.7.0.'),
  ('INSTALL_GESTARTET',
   'Die Installation von vzlogger läuft im Hintergrund (höchstens 15 Minuten). Den Stand zeigt dieser Reiter beim nächsten Aufruf.',
   'The vzlogger installation is running in the background (at most 15 minutes). This tab shows its progress when reopened.'),
  ('INSTALL_LAEUFT',
   'Die Installation von vzlogger läuft seit %d s – bitte warten und den Reiter danach neu laden.',
   'The vzlogger installation has been running for %d s – please wait and reload the tab afterwards.'),
  ('INSTALL_NICHT_GESTARTET',
   'Die Installation wurde nicht gestartet: die Marke %s ließ sich nicht anlegen.',
   'The installation was not started: the marker %s could not be created.'),
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
   'Abo im MQTT-Gateway',
   'Subscription in the MQTT gateway'),
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
   'Das Plugin trägt das Abo <b>%s/#</b> selbst ein (Datei mqtt_subscriptions.cfg, das Gateway liest sie). Steht es unter <i>System → MQTT Gateway → Abonnements</i> nicht, dort von Hand eintragen. Ohne diesen Eintrag kommt am Miniserver nichts an.',
   'The plugin enters the subscription <b>%s/#</b> itself (file mqtt_subscriptions.cfg, which the gateway reads). If it is not listed under <i>System → MQTT Gateway → Subscriptions</i>, enter it there by hand. Without this entry nothing arrives at the Miniserver.'),
  ('ABO_V2',
   'Das Gateway erkennt die Themengruppe von selbst — ein Abo ist nicht einzutragen. Gateway V2 leitet aber nur weiter, was angehakt ist: unter <i>System → MQTT Gateway → Abonnements</i> die Datenpunkte darunter anhaken (genau die Namen aus Schritt 3). Bei den mit „Noncached“ markierten auch „Noncached“ setzen: sie bleiben meist gleich, und ohne den Haken stünden sie nach einem Neustart des Miniservers auf 0.',
   'The gateway detects the topic group by itself — no subscription needs to be entered. Gateway V2 only forwards what is ticked, though: under <i>System → MQTT Gateway → Subscriptions</i> tick the data points below (exactly the names from step 3). For those marked “Noncached” also set “Noncached”: they mostly stay the same, and without the tick they would read 0 after a restart of the Miniserver.'),
  ('ABO_UNBEKANNT',
   "Die Fassung des MQTT-Gateways ließ sich nicht feststellen. Deshalb "
   "stehen hier beide Fälle:",
   "The version of the MQTT gateway could not be determined. Both cases are "
   "therefore given here:"),
  ('THEMEN_HINT',
   "Genau diese Themen gehen hinaus – je eingeschaltetem Leseweg, dazu Lebenszeichen, Kostenrechnung und Fahrplan-Abgleich. Die Feldnamen kommen aus derselben Liste wie Namenstabelle und Dienst (<span class='sm-mono'>bin/sm_felder.json</span>); der klassische Leser zeigt je Lesekopf die Felder der letzten Messung. Punkte im Namen bleiben stehen; das Gateway ersetzt nur <span class='sm-mono'>/</span> und <span class='sm-mono'>%</span> durch <span class='sm-mono'>_</span>.",
   "Exactly these topics are published – for each reading route that is switched on, plus the sign of life, the cost calculation and the schedule check. The field names come from the same list as the name table and the service (<span class='sm-mono'>bin/sm_felder.json</span>); for the classic reader each reading head shows the fields of its last reading. Dots in a name remain; the gateway only replaces <span class='sm-mono'>/</span> and <span class='sm-mono'>%</span> with <span class='sm-mono'>_</span>."),
  ('EINHEIT_VZ',
   "Auf dem vzLogger-Weg steht hier <b>keine Einheit</b>, und das ist Absicht: "
   "vzlogger rechnet nicht um, es reicht den Wert des Zählers durch — welche "
   "Einheit das ist, hängt am Zähler und ist nicht nachgemessen. Eine "
   "angenommene Einheit wäre schlimmer als keine: sie stünde als Beschriftung "
   "am virtuellen Eingang, und niemand prüft sie nach. Der Knopf "
   "<i>vzLogger-Rohwerte</i> im Reiter <i>Test</i> zeigt, was wirklich "
   "ankommt. Wer die Einheit belegt hat, trägt sie als "
   "<span class='sm-mono'>einheit_vz</span> in den Feldkatalog ein — dann "
   "steht sie auch in der Loxone-Vorlage, samt passender Grenzen. Der "
   "klassische Leser rechnet dagegen um (Wh auf kWh, W auf kW); dort stehen "
   "die Einheiten deshalb da.",
   "On the vzLogger path <b>no unit</b> is shown here, and that is "
   "deliberate: vzlogger does not convert, it passes the meter's value "
   "through — which unit that is depends on the meter and has not been "
   "measured. An assumed unit would be worse than none: it would sit as the "
   "label on the virtual input, and nobody checks it. The button <i>vzLogger "
   "raw values</i> in the <i>Test</i> tab shows what actually arrives. Once "
   "the unit is established, enter it as "
   "<span class='sm-mono'>einheit_vz</span> in the field catalogue — then it "
   "appears in the Loxone template as well, with matching limits. The classic "
   "reader does convert (Wh to kWh, W to kW); that is why units are shown "
   "there."),
  ('HINT_TOPIC',
   'Erlaubt sind Buchstaben, Ziffern und Zeichen wie - _ . sowie / zwischen zwei Ebenen. Nicht erlaubt: Leerraum, Anführungszeichen, # und +, ein / am Anfang oder Ende. Eine falsche Eingabe wird beanstandet, nicht still berichtigt.',
   'Letters, digits and characters such as - _ . are allowed, and / between two levels. Not allowed: white space, quotation marks, # and +, a / at the start or end. A wrong entry is rejected, not silently corrected.'),
  ('SP_RETAINED',
   'retained',
   'retained'),
  ('RETAINED_HINT',
   "<b>retained</b> heißt: der Broker behält den letzten Wert und liefert ihn nach einem Neustart von Broker oder Gateway sofort wieder aus. Das gilt nur für Zustände; Messwerte, Zeitstempel und das Lebenszeichen gehen flüchtig hinaus. Ein Zustand gilt in Loxone nur zusammen mit <span class='sm-mono'>status/ok</span>. Nach einem Präfixwechsel, beim Abschalten von MQTT und bei der Deinstallation räumt das Plugin die retained Zustände ab.",
   "<b>retained</b> means: the broker keeps the last value and delivers it again right after a restart of broker or gateway. This applies to states only; measured values, timestamps and the sign of life are published non-retained. In Loxone a state is only valid together with <span class='sm-mono'>status/ok</span>. After a prefix change, when MQTT is switched off and on uninstall, the plugin clears the retained states."),
  ('G_KLASSISCH',
   'Klassischer Leser – je Lesekopf',
   'Classic reader – per reading head'),
  ('G_VZ',
   'vzLogger',
   'vzLogger'),
  ('G_STATUS',
   'Lebenszeichen – in jedem Lauf',
   'Sign of life – every run'),
  ('G_KOSTEN',
   'Kostenrechnung – alle fünf Minuten',
   'Cost calculation – every five minutes'),
  ('G_ABGLEICH',
   'Fahrplan-Abgleich – alle fünf Minuten, je Regel <n>',
   'Schedule check – every five minutes, per rule <n>'),
  ('AUS_KLASSISCH',
   'Der klassische Leser ist ausgeschaltet – er sendet nichts.',
   'The classic reader is switched off – it publishes nothing.'),
  ('AUS_VZ',
   'Die Betriebsart vzLogger ist ausgeschaltet – sie sendet nichts.',
   'The vzLogger mode is switched off – it publishes nothing.'),
  ('KEIN_KOPF',
   'Kein Lesekopf hat ein Zählerprofil – es wird nichts gelesen.',
   'No reading head has a meter profile – nothing is read.'),
  ('T_NOCH_KEINE',
   'Felder je nach Zählerprofil – sie stehen hier nach der ersten Messung.',
   'Fields depend on the meter profile – they are listed here after the first reading.'),
  ('B_STATUS_OK',
   '1, solange jeder eingeschaltete Lesekopf jünger ist als das Dreifache des Abfragetakts, sonst 0',
   '1 as long as every reading head that is switched on is younger than three times the polling cycle, otherwise 0'),
  ('B_STATUS_TS',
   'Zeit des Lebenszeichens (Unix-Sekunden, jede Minute)',
   'time of the sign of life (Unix seconds, every minute)'),
  ('B_STATUS_ZAEHLER',
   'umlaufender Zähler 0–999, eine Stelle je Minute (unabhängig vom Abfragetakt)',
   'wrapping counter 0–999, one step per minute (independent of the polling interval)'),
  ('B_K_QUELLE_OK',
   '1 = Preisquelle erreichbar, 0 = nicht',
   '1 = price source reachable, 0 = not'),
  ('B_K_STUNDE_CT',
   'Kosten der letzten vollen Stunde, -1 = unbekannt',
   'cost of the last full hour, -1 = unknown'),
  ('B_K_HEUTE_CT',
   'heute bisher, -1 = unbekannt',
   'today so far, -1 = unknown'),
  ('B_K_HEUTE_EUR',
   'dasselbe in Euro',
   'the same in euros'),
  ('B_K_HEUTE_KWH',
   'heute bisher verbraucht, -1 = unbekannt',
   'consumed today so far, -1 = unknown'),
  ('B_K_STUNDEN',
   'gerechnete Stunden',
   'hours calculated'),
  ('B_K_OFFEN',
   'Stunden ohne belegte Einheit',
   'hours without an established unit'),
  ('B_K_OHNE_PREIS',
   'Stunden ohne Preis',
   'hours without a price'),
  ('B_A_QUELLE_OK',
   '1 = Fahrplan erreichbar, 0 = nicht',
   '1 = schedule reachable, 0 = not'),
  ('B_A_AKTIV',
   'die Regel soll laufen (1/0); -1 = Regel steht nicht mehr im Fahrplan',
   'the rule is meant to run (1/0); -1 = rule no longer in the schedule'),
  ('B_A_SOLL',
   'Leistung mal Laufzeit',
   'power times running time'),
  ('B_A_IST',
   'gemessener Netzbezug',
   'measured grid consumption'),
  ('B_A_FEHLT',
   'Fehlbetrag',
   'shortfall'),
  ('B_A_DAUER',
   'Laufzeit',
   'running time'),
  ('B_A_SICHER',
   '1 = keine Einspeisung, kein entladender Speicher, Einheit belegt',
   '1 = no feed-in, no discharging battery, unit established'),
  ('B_A_OK',
   '1 zieht · 0 zieht nicht · -1 kein Urteil',
   '1 draws · 0 does not draw · -1 no verdict'),
  ('RAEUMEN_OK',
   'Unter %s/ steht kein zurückbehaltener Zustand dieses Plugins mehr (vom Broker bestätigt).',
   'No retained state of this plugin is left under %s/ (confirmed by the broker).'),
  ('RAEUMEN_OFFEN',
   '%d zurückbehaltene Zustände stehen noch unter %s/ (%s). Das Präfix bleibt vorgemerkt; die Deinstallation leert es mit. Von Hand: mosquitto_pub -r -n -t &lt;thema&gt;.',
   '%d retained states are still left under %s/ (%s). The prefix stays on record; uninstalling clears it as well. By hand: mosquitto_pub -r -n -t &lt;topic&gt;.'),
  ('RAEUMEN_UNGEPRUEFT',
   'Die zurückbehaltenen Zustände unter %s/ wurden zum Löschen gesendet, der Broker ließ sich aber nicht befragen. Das Präfix bleibt vorgemerkt; die Deinstallation leert es noch einmal.',
   'The retained states under %s/ were sent for deletion, but the broker could not be queried. The prefix stays on record; uninstalling clears it once more.'),
  ('RAEUMEN_KEIN_EINGANG',
   'Die zurückbehaltenen Zustände unter %s/ ließen sich nicht leeren: der UDP-Eingang des MQTT-Gateways ist nicht erreichbar. Das Präfix ist vorgemerkt; die Deinstallation leert es.',
   'The retained states under %s/ could not be cleared: the UDP input of the MQTT gateway is not reachable. The prefix is on record; uninstalling clears it.'),
  # Gruppe 35 (2.8.13): Themen kosten/gestern_*, abgleich/<n>/speicher.
  ('B_K_GESTERN_EUR',
   'Kosten des Vortags (Tagesabschluss), -1 = nicht gerechnet; nie retained',
   'cost of the previous day (daily close), -1 = not calculated; never retained'),
  ('B_K_GESTERN_KWH',
   'Verbrauch des Vortags mit Preis, -1 = nicht gerechnet',
   'consumption of the previous day with price, -1 = not calculated'),
  ('B_K_GESTERN_CT',
   'dasselbe in ct',
   'the same in ct'),
  ('B_K_GESTERN_STUNDEN',
   'gerechnete Stunden des Vortags',
   'hours calculated for the previous day'),
  ('B_A_SPEICHER',
   '1 Speicher entlud · 0 nein · -1 keine Aussage',
   '1 battery discharged · 0 no · -1 no statement'),
  ('H_HAUS_ENERGIE',
   'Werte für andere Plugins (haus/energie)',
   'Values for other plugins (haus/energie)'),
  ('HE_ERKLAERUNG',
   "Andere Plugins wollen wissen, ob das Haus gerade Strom aus dem Netz holt oder Sonnenstrom übrig hat – zum Beispiel die Klimaanlage, die bei Überschuss vorkühlt, die Wallbox, die Bewässerung oder das Dashboard. Statt dass jedes Plugin selbst einen Zähler abfragt, stellt der Smartmeter die Werte <b>einmal für alle</b> bereit: unter <span class='sm-mono'>haus/energie/…</span> im MQTT-Broker. Gesendet wird nur, was Ihr Zähler wirklich liefert. Die Leistung der Solaranlage kennt ein Netzzähler nicht – sie steht hier nie.",
   "Other plugins want to know whether the house is drawing power from the grid right now or has solar power to spare – for example the air conditioner that pre-cools on surplus, the wallbox, the irrigation or the dashboard. Instead of every plugin reading a meter itself, the smart meter provides the values <b>once for all</b>: under <span class='sm-mono'>haus/energie/…</span> on the MQTT broker. Only what your meter really delivers is sent. A grid meter does not know the output of the solar system – it never appears here."),
  ('HE_BEISPIEL',
   "Beispiel: Die Solaranlage erzeugt 4.000 W, im Haus laufen 1.500 W. Dann fließen 2.500 W ins Netz, und es kommt an: <span class='sm-mono'>netz_w = -2500</span>, <span class='sm-mono'>bezug_w = 0</span>, <span class='sm-mono'>ueberschuss_w = 2500</span>. Abends ohne Sonne bei 800 W im Haus: <span class='sm-mono'>netz_w = 800</span>, <span class='sm-mono'>bezug_w = 800</span>, <span class='sm-mono'>ueberschuss_w = 0</span>.",
   "Example: the solar system produces 4,000 W and the house uses 1,500 W. Then 2,500 W flow into the grid, and you get: <span class='sm-mono'>netz_w = -2500</span>, <span class='sm-mono'>bezug_w = 0</span>, <span class='sm-mono'>ueberschuss_w = 2500</span>. In the evening without sun at 800 W in the house: <span class='sm-mono'>netz_w = 800</span>, <span class='sm-mono'>bezug_w = 800</span>, <span class='sm-mono'>ueberschuss_w = 0</span>."),
  ('HE_LABEL_AN',
   'Werte für andere Plugins bereitstellen (haus/energie)',
   'Provide values for other plugins (haus/energie)'),
  ('HE_HINT_AN',
   'Ab Werk aus. Nur <b>ein</b> Plugin im Haus darf diese Werte liefern – haben Sie zwei Smartmeter-Installationen, schalten Sie es nur bei der ein, die am Hausanschluss misst. Wirkt nur, wenn oben „Werte per MQTT senden“ eingeschaltet ist. Gesendet wird jede Minute, neue Zählerwerte so oft, wie der Zähler gelesen wird. Beim Ausschalten bleibt nichts im Broker stehen.',
   'Off by default. Only <b>one</b> plugin in the house may supply these values – if you have two Smartmeter installations, switch it on only at the one that measures at the grid connection. Works only if „Send values via MQTT“ above is on. Sent every minute; new meter values as often as the meter is read. Nothing remains on the broker when switched off.'),
  ('HE_LABEL_ZAEHLER',
   'Welcher Zähler misst am Hausanschluss?',
   'Which meter measures at the grid connection?'),
  ('HE_ZAEHLER_AUTO',
   'automatisch – der einzige eingeschaltete Lesekopf',
   'automatic – the only reading head switched on'),
  ('HE_ZAEHLER_WEG',
   'nicht (mehr) eingeschaltet',
   'not (or no longer) switched on'),
  ('HE_HINT_ZAEHLER',
   'Haben Sie nur einen Lesekopf, lassen Sie „automatisch“ stehen. Bei mehreren (zum Beispiel ein zweiter Zähler für die Wärmepumpe) wählen Sie den Zähler am Hausanschluss – das Plugin rät hier nicht.',
   'If you have only one reading head, leave „automatic“. With several (for example a second meter for the heat pump) choose the meter at the grid connection – the plugin does not guess.'),
  ('HE_FEHLER_ZAEHLER',
   'Der gewählte Zähler hat keinen gültigen Namen – bitte aus der Liste wählen.',
   'The selected meter has no valid name – please choose from the list.'),
  ('G_HAUS_ENERGIE',
   'Für andere Plugins – haus/energie (ohne Präfix, jede Minute)',
   'For other plugins – haus/energie (no prefix, every minute)'),
  ('HE_THEMEN_HINT',
   'Gemeinsames Hausthema nach den Hausregeln. Alle flüchtig: fällt der Zähler aus, gehen nur ok = 0 und der Zähler hinaus, nie alte Werte. Ein Abnehmer verwendet die Werte nur, solange zaehler sich binnen 120 s ändert und ok = 1 ist; wie alt die Messung ist, sagt stand (bis zum Dreifachen des Abfragetakts).',
   'Shared house topic according to the house rules. All non-retained: if the meter fails, only ok = 0 and the counter go out, never old values. A consumer uses the values only while zaehler changes within 120 s and ok = 1; stand tells how old the measurement is (up to three times the polling interval).'),
  ('B_HE_NETZ',
   'Leistung am Netzanschluss: + = Bezug aus dem Netz, − = Einspeisung',
   'Power at the grid connection: + = drawn from the grid, − = fed in'),
  ('B_HE_BEZUG',
   'Bezug aus dem Netz, nie negativ',
   'Drawn from the grid, never negative'),
  ('B_HE_UEBERSCHUSS',
   'Einspeisung ins Netz (Überschuss), nie negativ',
   'Fed into the grid (surplus), never negative'),
  ('B_HE_BEZUG_KWH',
   'Zählerstand Bezug (OBIS 1.8.0)',
   'Meter reading consumption (OBIS 1.8.0)'),
  ('B_HE_EINSP_KWH',
   'Zählerstand Einspeisung (OBIS 2.8.0)',
   'Meter reading feed-in (OBIS 2.8.0)'),
  ('B_HE_STAND',
   'Zeitpunkt der Messung, zu der die Werte gehören (Unix-Sekunden); letztes Thema des Satzes',
   'Time of the measurement the values belong to (Unix seconds); last topic of the set'),
  ('B_HE_OK',
   '1 = frische Messung des Netzzählers, 0 = keine (dann gehen keine Werte hinaus)',
   '1 = fresh measurement of the grid meter, 0 = none (then no values go out)'),
  ('B_HE_ZAEHLER',
   'Lebenszeichen des Anbieters, 0–999, eine Stelle je Minute',
   'Heartbeat of the provider, 0–999, one step per minute'),
  ('HE_L_AUS',
   'haus/energie: aus.',
   'haus/energie: off.'),
  ('HE_L_OHNE_MQTT',
   'haus/energie: eingeschaltet, aber „Werte per MQTT senden“ ist aus – es wird nichts gesendet.',
   'haus/energie: switched on, but „Send values via MQTT“ is off – nothing is sent.'),
  ('HE_L_NOCH_NICHT',
   'haus/energie: eingeschaltet, aber noch nicht gesendet – der nächste Minutenlauf holt es nach.',
   'haus/energie: switched on, but not sent yet – the next minute run will do it.'),
  ('HE_L_STILL',
   'haus/energie: eingeschaltet, zuletzt gesendet %s – der Minutenlauf ist seitdem ausgeblieben.',
   'haus/energie: switched on, last sent %s – the minute run has not run since.'),
  ('HE_L_BROKER',
   'haus/energie: eingeschaltet, Versuch %s – der MQTT-Broker war nicht erreichbar, nichts gesendet.',
   'haus/energie: switched on, attempt %s – the MQTT broker was not reachable, nothing sent.'),
  ('HE_L_OHNE_WERTE',
   'haus/energie: eingeschaltet, zuletzt gesendet %s, aber ohne Werte (ok = 0): %s',
   'haus/energie: switched on, last sent %s, but without values (ok = 0): %s'),
  ('HE_L_OK',
   'haus/energie: eingeschaltet, zuletzt gesendet %s: %s (Quelle OBIS %s).',
   'haus/energie: switched on, last sent %s: %s (source OBIS %s).'),
  ('HE_G_KEIN_LESER',
   'kein Leseweg eingeschaltet.',
   'no reading path switched on.'),
  ('HE_G_WAEHLEN',
   'mehrere Leseköpfe – bitte den Zähler am Hausanschluss wählen.',
   'several reading heads – please choose the meter at the grid connection.'),
  ('HE_G_WEG',
   'der gewählte Zähler ist nicht eingeschaltet.',
   'the selected meter is not switched on.'),
  ('HE_G_KEINE_MESSUNG',
   'vom Zähler liegt noch keine Messung vor.',
   'no measurement from the meter yet.'),
  ('HE_G_ZU_ALT',
   'die letzte Messung ist älter als das Dreifache des Abfragetakts (Zähler antwortet nicht).',
   'the last measurement is older than three times the polling interval (meter does not answer).'),
  ('HE_G_NUR_START',
   'Abfragetakt „nur beim Systemstart“ – dabei gibt es keine Momentanwerte.',
   'polling interval „only at system start“ – there are no instantaneous values then.'),
  ('HE_G_KEINE_LEISTUNG',
   'der Zähler liefert keine Leistung mit bekannter Einheit (1.7.0/2.7.0 bzw. 16.7.0).',
   'the meter delivers no power with a known unit (1.7.0/2.7.0 or 16.7.0).'),
  ('B_HE_FREI',
   'Sonnenstrom übrig (+) oder Haus deckt sich aus Netz/Akku (−), in W – mit Hausakku gerechnet',
   'Solar power left over (+) or house supplied from grid/battery (−), in W – home battery included'),
  ('B_HE_FREI_QUELLE',
   'Woraus frei_w gerechnet ist: netz (kein Hausakku bekannt) oder netz+speicher',
   'What frei_w is based on: netz (no home battery known) or netz+speicher'),
  ('H_HAUS_FREI',
   'Sonnenstrom übrig? – frei_w (mit Hausakku)',
   'Solar power left over? – frei_w (with home battery)'),
  ('HEF_ERKLAERUNG',
   "Ein Netzzähler sieht nur, was über den Hausanschluss fließt. Haben Sie einen <b>Hausakku</b>, täuscht das: Lädt der Akku, fließt nichts ins Netz, obwohl Sonnenstrom übrig ist. Und entlädt er, um das Haus zu versorgen, holt das Haus nichts aus dem Netz – obwohl gerade Akkustrom verbraucht wird. Deshalb sendet das Plugin zusätzlich <span class='sm-mono'>haus/energie/frei_w</span>: <b>plus</b> heißt „so viel Sonnenstrom ist übrig“, <b>minus</b> heißt „so viel holt sich das Haus gerade aus Netz oder Akku“. Den Akku liest es aus <span class='sm-mono'>haus/speicher</span> (zum Beispiel vom Plugin Marstek Venus E). Ohne Hausakku ist frei_w einfach die Einspeisung (minus Bezug).",
   "A grid meter only sees what flows through the house connection. With a <b>home battery</b> that is misleading: while the battery charges, nothing flows into the grid although solar power is left over. And while it discharges to supply the house, the house takes nothing from the grid – although battery power is being used. That is why the plugin also sends <span class='sm-mono'>haus/energie/frei_w</span>: <b>plus</b> means “this much solar power is left over”, <b>minus</b> means “this much the house is currently taking from grid or battery”. The battery is read from <span class='sm-mono'>haus/speicher</span> (for example from the Marstek Venus E plugin). Without a home battery, frei_w is simply feed-in (minus consumption)."),
  ('HEF_BEISPIEL',
   "Beispiel mittags: Die Solaranlage erzeugt 4.500 W, das Haus braucht 1.500 W, der Akku lädt mit 3.000 W. Ins Netz fließt nichts: <span class='sm-mono'>ueberschuss_w = 0</span>, aber <span class='sm-mono'>frei_w = 3000</span>. Beispiel abends: Das Haus braucht 1.500 W, der Akku liefert sie, aus dem Netz kommt nichts: <span class='sm-mono'>bezug_w = 0</span>, aber <span class='sm-mono'>frei_w = -1500</span>.",
   "Example at noon: the solar system produces 4,500 W, the house needs 1,500 W, the battery charges with 3,000 W. Nothing flows into the grid: <span class='sm-mono'>ueberschuss_w = 0</span>, but <span class='sm-mono'>frei_w = 3000</span>. Example in the evening: the house needs 1,500 W, the battery supplies them, nothing comes from the grid: <span class='sm-mono'>bezug_w = 0</span>, but <span class='sm-mono'>frei_w = -1500</span>."),
  ('HEF_GRENZE',
   "Gut zu wissen: Wallbox, Wärmepumpe und andere große Verbraucher stecken im Hausverbrauch und werden nicht herausgerechnet – lädt das Auto, ist frei_w entsprechend kleiner. Ein Akku ohne <span class='sm-mono'>haus/speicher</span> zählt nicht mit. Hat das Plugin einmal einen Hausakku gesehen und schweigt der dann, wird frei_w <b>nicht</b> gesendet (sonst würde ein entladender Akku übersehen) – die anderen Plugins nehmen dann wieder Einspeisung und Bezug.",
   "Good to know: wallbox, heat pump and other large consumers are part of the house consumption and are not subtracted – while the car charges, frei_w is smaller accordingly. A battery without <span class='sm-mono'>haus/speicher</span> is not counted. Once the plugin has seen a home battery and it then falls silent, frei_w is <b>not</b> sent (otherwise a discharging battery would be missed) – the other plugins then use feed-in and consumption again."),
  ('HEF_L_AUS',
   'frei_w: aus (haus/energie ist aus).',
   'frei_w: off (haus/energie is off).'),
  ('HEF_L_OHNE_ZAEHLER',
   'frei_w: wird nicht gesendet – haus/energie hat gerade keine Zählerwerte (siehe oben).',
   'frei_w: not sent – haus/energie currently has no meter values (see above).'),
  ('HEF_L_SPEICHER',
   'frei_w: gesendet mit Hausakku – frei_w %s W (Netz %s W, Akku %+d W; + lädt, − entlädt).',
   'frei_w: sent with home battery – frei_w %s W (grid %s W, battery %+d W; + charges, − discharges).'),
  ('HEF_L_NETZ',
   'frei_w: gesendet ohne Hausakku – frei_w %s W (bisher kein Hausakku unter haus/speicher gesehen).',
   'frei_w: sent without home battery – frei_w %s W (no home battery seen under haus/speicher so far).'),
  ('HEF_L_STILL',
   'frei_w: wird zurückgehalten – ein Hausakku war da (seit %s), aber gerade %s Die anderen Plugins nehmen so lange Einspeisung und Bezug. Gibt es den Akku nicht mehr, unten „Hausakku vergessen“.',
   'frei_w: withheld – a home battery was present (since %s), but right now %s Meanwhile the other plugins use feed-in and consumption. If the battery is gone for good, use “Forget home battery” below.'),
  ('HEF_L_KEIN_NETZ',
   'frei_w: wird nicht gesendet – der Zähler liefert keinen Saldo (netz_w), nur Bezug oder nur Einspeisung.',
   'frei_w: not sent – the meter delivers no balance (netz_w), only consumption or only feed-in.'),
  ('HEF_S_KEINE_LAGE',
   'liegt keine Speicherlage vor (Leser noch nicht gelaufen oder MQTT aus).',
   'there is no battery reading yet (reader has not run or MQTT is off).'),
  ('HEF_S_SCHWEIGT',
   'schweigt haus/speicher (kein Lebenszeichen binnen 120 s).',
   'haus/speicher is silent (no sign of life within 120 s).'),
  ('HEF_S_ZU_ALT',
   'ist die letzte Speicherlage älter als 120 s.',
   'the last battery reading is older than 120 s.'),
  ('HEF_S_OHNE_AUSSAGE',
   'meldet haus/speicher „ohne Aussage“ (−1).',
   'haus/speicher reports “no statement” (−1).'),
  ('HEF_S_LEISTUNG',
   'fehlt die Akkuleistung.',
   'the battery power is missing.'),
  ('HEF_VERGESSEN',
   'Hausakku vergessen',
   'Forget home battery'),
  ('HEF_VERGESSEN_HINT',
   'Nur nötig, wenn Sie den Hausakku abgebaut oder sein Plugin entfernt haben: Dann rechnet das Plugin frei_w wieder ohne Akku. Taucht später ein Akku auf, merkt es sich ihn wieder.',
   'Only needed if you removed the home battery or its plugin: then frei_w is calculated without a battery again. If a battery shows up later, it is remembered again.'),
  ('HEF_VERGESSEN_OK',
   'Hausakku vergessen – frei_w wird ab dem nächsten Minutenlauf ohne Akku gerechnet, bis wieder einer gemeldet wird.',
   'Home battery forgotten – from the next minute run frei_w is calculated without a battery until one is reported again.'),
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
   'Schritt 2: Abo im MQTT-Gateway prüfen',
   'Step 2: check the subscription in the MQTT gateway'),
  ('S3_TITEL',
   'Schritt 3: Virtuelle Eingänge anlegen',
   'Step 3: create virtual inputs'),
  ('S3_HINT',
   'Die endgültigen Namen zeigt das Gateway unter <i>Eingehende Daten</i> – weichen sie ab, gelten die dort angezeigten.',
   'The gateway shows the final names under <i>Incoming data</i> – if they differ, the ones shown there apply.'),
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
   "Schweigt das Plugin oder der Zähler, behalten die virtuellen Eingänge ihren <b>letzten Wert</b>. Über MQTT gibt es kein Alter, nur Lebenszeichen. Deshalb zwei Wächter, wie auf den Seiten in Schritt 6: eine <i>Analogwertvalidierung</i> an <span class='sm-mono'>%s_status_zaehler</span> (er zählt seit 2.8.13 jede Minute eins weiter, unabhängig vom Abfragetakt; Tmc 300 s, Min 0, Max 999, an En die Konstante 1 – der Haken bei ‚En‘ muss weg; im MQTT-Gateway V2 „Noncached“ anhaken) meldet, wenn das Plugin nicht mehr läuft; ein <i>NICHT</i> an <span class='sm-mono'>%s_status_ok</span> meldet, wenn ein Lesekopf nichts mehr liefert. Wer zusätzlich das Alter der Messung sehen will: Formel <span class='sm-mono'>I1-I2</span>, I1 = aktuelle Zeit (Loxone-Zeit), I2 = <span class='sm-mono'>%s_&lt;Zählernummer&gt;_Last_UpdateLoxEpoche</span> – dieser Wert ist schon in Loxone-Zeit mit Zeitzone gerechnet.",
   "If the plugin or the meter falls silent, the virtual inputs keep their <b>last value</b>. Over MQTT there is no age, only signs of life. Hence two watchers, as on the pages in step 6: a <i>Value Validator</i> on <span class='sm-mono'>%s_status_zaehler</span> (since 2.8.13 it counts up by one every minute, independent of the polling interval; Tmc 300 s, Min 0, Max 999, constant 1 at En – the tick at ‘En’ must be removed; tick „Noncached“ in MQTT gateway V2) reports when the plugin no longer runs; a <i>NOT</i> on <span class='sm-mono'>%s_status_ok</span> reports when a reading head delivers nothing any more. If you also want to see the age of the reading: formula <span class='sm-mono'>I1-I2</span>, I1 = current time (Loxone time), I2 = <span class='sm-mono'>%s_&lt;meter number&gt;_Last_UpdateLoxEpoche</span> – this value is already calculated in Loxone time including the time zone."),
  ('S6_TITEL',
   'Schritt 6: Komplette Baustein-Listen zum 1:1-Nachbauen',
   'Step 6: complete block lists for rebuilding one to one'),
  ('S6_TEXT',
   'Drei Seiten wie im Musterprojekt, jede mit Anleitung, Baustein-Liste und Bild: je eine für den klassischen Leseweg und für vzLogger (nur den Leseweg bauen, den Sie betreiben) und eine für Kosten und Fahrplan-Abgleich (nur mit Schritt 10 und 11). Beide Lesewegseiten tragen dieselben Eingangsnamen – nur die Seite des betriebenen Lesewegs übernehmen, sonst bekommt nur eine von beiden die Werte. Die Bausteine findet man in Loxone Config über die Baustein-Suche (F5).',
   'Three pages as in the sample project, each with instructions, block list and picture: one each for the classic reading path and for vzLogger (build only the path you run) and one for costs and schedule check (only with steps 10 and 11). Both reading-path pages carry the same input names – take over only the page of the reading path you run, otherwise only one of the two gets the values. You find the blocks in Loxone Config via the block search (F5).'),
  ('S7_TITEL',
   'Schritt 7: Gegenprobe',
   'Step 7: cross-check'),
  ('S7_TEXT',
   'Im Reiter <i>Test</i> die <i>Antwort der HTTP-Schnittstelle</i> ansehen. Stehen dort Werte mit %s größer null, liest das Plugin. Kommen sie in Loxone trotzdem nicht an, fehlt fast immer das Abo aus Schritt&nbsp;2.',
   'On the <i>Test</i> tab, look at the <i>response of the HTTP interface</i>. If there are values with %s greater than zero, the plugin is reading. If they still do not arrive in Loxone, the subscription from step&nbsp;2 is almost always missing.'),
  ('S8_TEXT',
   'Neben MQTT und UDP kann das Plugin die zuletzt gelesenen Werte auch als Klartext über diese Adresse liefern – seit 2.8.13 nur mit dem Schalter unten (Neuinstallation aus, Update an). Ein virtueller HTTP-Eingang im Miniserver kann sie direkt abfragen:',
   'Besides MQTT and UDP the plugin can also serve the last readings as plain text at this address – since 2.8.13 only with the switch below (new installation off, update on). A virtual HTTP input on the Miniserver can poll it directly:'),
  ('S8_TITEL',
   'Schritt 8 — die Rohdaten direkt abholen (freiwillig)',
   'Step 8 — fetch the raw values directly (optional)'),
  ('SP_TITEL_VE',
   'Name des virtuellen Eingangs (genau so)',
   'Name of the virtual input (exactly)'),
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

  # --- Schritt 9: der Lastgang (2.6.0) ---
  ('S9_TITEL',
   'Schritt 9: Verbrauch je Stunde an das Spotpreis-Plugin',
   'Step 9: hourly consumption for the spot price plugin'),
  ('S9_TEXT',
   'Die Spotpreis-Plugins (aWATTar, Octopus, Tibber) gewichten ihren '
   'Tarifvergleich mit einem eingebauten <b>Haushaltsprofil</b> — einer '
   'Annahme über einen Durchschnittshaushalt. Mit Wärmepumpe, Wallbox oder '
   'PV liegt die daneben, und zwar in beide Richtungen. Dieses Plugin kann '
   'statt dessen den <b>gemessenen</b> Verbrauch je Stunde liefern; aus der '
   'Modellrechnung wird damit eine Messung. Die Adresse:',
   'The spot price plugins (aWATTar, Octopus, Tibber) weight their tariff '
   'comparison with a built-in <b>household profile</b> — an assumption '
   'about an average household. With a heat pump, a wallbox or PV that is '
   'off, and in both directions. This plugin can supply the <b>measured</b> '
   'hourly consumption instead, turning the model into a measurement. The '
   'address:'),
  ('S9_EINTRAGEN',
   'Im Spotpreis-Plugin unter „Eigener Lastgang“ eintragen:',
   'Enter in the spot price plugin under „Your own load curve“:'),
  ('S9_SP_FELD', 'Feld', 'Field'),
  ('S9_SP_WERT', 'Wert', 'Value'),
  ('S9_F_QUELLE', 'Quelle', 'Source'),
  ('S9_F_PFAD', 'Pfad im JSON', 'Path in the JSON'),
  ('S9_F_EINHEIT', 'Einheit', 'Unit'),
  ('S9_F_URL', 'Adresse', 'Address'),
  ('S9_LAGE',  # (3) Stunden heute, Zeilen gesamt, offene Stunden
   'Heute sind <b>%d von 24</b> Stunden gemessen, insgesamt stehen %d '
   'Stunden in der Historie (%d davon ohne belegte Einheit). Das '
   'Spotpreis-Plugin verlangt mindestens <b>20 der 24</b> Stunden — '
   'darunter nimmt es sein eingebautes Profil, und es sagt das auch. Die '
   'Historie wächst nur, solange ein Leser läuft; nach der Einrichtung '
   'dauert es also einen Tag, bis sie trägt.',
   'Today <b>%d of 24</b> hours are measured; the history holds %d hours in '
   'total (%d of them without an established unit). The spot price plugin '
   'requires at least <b>20 of 24</b> hours — below that it uses its '
   'built-in profile, and says so. The history only grows while a reader is '
   'running, so after setup it takes a day before it carries.'),
  ('S9_OFFEN',
   'Ein Teil der Stunden trägt <b>keine belegte Einheit</b>. Das ist der '
   'vzLogger-Weg: vzlogger reicht den Wert des Zählers durch, ohne '
   'umzurechnen, und welche Einheit das ist, ist an diesem Zähler noch '
   'nicht gemessen. Solche Stunden werden <b>nicht ausgeliefert</b> — eine '
   'Zahl mit geratener Einheit wäre in einer Kostenrechnung um den Faktor '
   '1000 daneben, und niemand sähe es. Der Knopf <i>vzLogger-Rohwerte</i> im '
   'Reiter <i>Test</i> zeigt, was wirklich ankommt.',
   'Some hours carry <b>no established unit</b>. That is the vzLogger path: '
   'vzlogger passes the meter value through without converting, and which '
   'unit that is has not been measured on this meter yet. Such hours are '
   '<b>not served</b> — a number with a guessed unit would be off by a '
   'factor of 1000 in a cost calculation, and nobody would see it. The '
   'button <i>vzLogger raw values</i> in the <i>Test</i> tab shows what '
   'actually arrives.'),
  ('KANAL_FEHLT',
   "dieser Kanal ist nicht eingestellt",
   "this channel is not configured"),
  ('BRUCH_250',  # (2) alter Name, neuer Name
   "<b>Fassung 2.5.0 benennt ein Feld um.</b> Der Schaltzustand des "
   "Zählers hieß %s — die Kennzahl im Namen war falsch: gelesen wird "
   "96.3.10, und 96.1.4 gehört der Software-Fassung des Zählers. Zwei "
   "verschiedene Größen unter einer Kennzahl. Er heißt jetzt %s. Wer diesen "
   "Wert in Loxone verwendet, benennt den virtuellen Eingang einmal um oder "
   "lädt die Vorlage neu; alle übrigen Eingänge bleiben unberührt. Betroffen "
   "sind nur Zähler, die diesen Wert überhaupt senden.",
   "<b>Version 2.5.0 renames one field.</b> The meter's breaker state was "
   "called %s — the OBIS code in the name was wrong: the value is read from "
   "96.3.10, while 96.1.4 belongs to the meter firmware version. Two "
   "different quantities under one code. It is now called %s. If you use "
   "this value in Loxone, rename the virtual input once or re-import the "
   "template; all other inputs are unaffected. Only meters that send this "
   "value at all are concerned."),
  ('S8_SELFTEST',
   "Dieselbe Adresse mit <span class='sm-mono'>?selftest=1</span> antwortet "
   "in einer Zeile, ob das Plugin gerade liest — ohne die Messwerte "
   "mitzuschicken:",
   "The same address with <span class='sm-mono'>?selftest=1</span> answers in "
   "a single line whether the plugin is currently reading — without sending "
   "the measured values along:"),
  ('S8_ZEILE', # (1) Beispielzeile
   "Angehängt an die Messwerte steht außerdem eine Zustandszeile: %s. <span class='sm-mono'>OK=1</span> heißt: jeder eingeschaltete Lesekopf ist frisch gelesen. <span class='sm-mono'>OK=0</span> steht, sobald eine Messung älter ist als <span class='sm-mono'>GRENZE</span> – das Dreifache des Abfragetakts, beim vzLogger-Weg 180 s. <span class='sm-mono'>ALTER</span> ist das Alter der jüngsten Messung in Sekunden, <span class='sm-mono'>ZAEHLER</span> der umlaufende Zähler, <span class='sm-mono'>KOEPFE</span> die Zahl der gelesenen Dateien. Dahinter stehen je eingeschaltetem Lesekopf <span class='sm-mono'>KOPF1_OK</span>, <span class='sm-mono'>KOPF1_ALTER</span> usw. in der Reihenfolge der Leseköpfe im Reiter Smartmeter (klassisch). <span class='sm-mono'>ALTER=-1</span> heißt: es hat noch keine erfolgreiche Messung gegeben.",
   "A status line is appended to the measured values as well: %s. <span class='sm-mono'>OK=1</span> means every reading head that is switched on has been read recently. <span class='sm-mono'>OK=0</span> appears as soon as a reading is older than <span class='sm-mono'>GRENZE</span> – three times the polling cycle, 180 s on the vzLogger route. <span class='sm-mono'>ALTER</span> is the age of the most recent reading in seconds, <span class='sm-mono'>ZAEHLER</span> the wrapping counter, <span class='sm-mono'>KOEPFE</span> the number of files read. After that come <span class='sm-mono'>KOPF1_OK</span>, <span class='sm-mono'>KOPF1_ALTER</span> and so on for each reading head that is switched on, in the order of the heads in the Smartmeter (classic) tab. <span class='sm-mono'>ALTER=-1</span> means there has not been a successful reading yet."),
  ('VE_STATUS_OK',
   'Lebenszeichen ok (1/0)',
   'Sign of life ok (1/0)'),
  ('VE_STATUS_TS',
   'Lebenszeichen Zeit',
   'Sign of life time'),
  ('VE_STATUS_ZAEHLER',
   'Lebenszeichen Zähler',
   'Sign of life counter'),
  # Welle Bild 7 (2.8.8, Musterprojekt): zwei Baustein-Listen im Reiter Einbindung in Loxone,
  # je Leseweg eine, mit Bild aus dem LoxBerry-Plugins Musterprojekt.
  ('BL_KLASSISCH',
   'Leseweg klassisch (Lesekopf direkt)',
   'Classic reading path (reading head directly)'),
  ('BL_VZLOGGER',
   'Leseweg vzLogger',
   'vzLogger reading path'),
  ('BL_ZAEHLERNUMMER',
   '<Zählernummer>',
   '<meter number>'),
  ('BILD_ALT',
   'Bausteine des Plugins in Loxone Config – %s',
   'Plugin blocks in Loxone Config – %s'),
  ('BILD_UNTERSCHRIFT',
   'Seite „%s“ im LoxBerry-Plugins Musterprojekt. Config kürzt lange Bausteinnamen – Namen siehe Tabelle.',
   'Page “%s” in the LoxBerry plugins sample project. Config shortens long block names – see the table for the full names.'),
  ('MUSTERPROJEKT',
   "Die ganze Projektdatei mit allen Plugin-Seiten und Vorlagen: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry-Plugins Musterprojekt</a>",
   "The complete project file with all plugin pages and templates: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry plugins sample project</a>"),
  # Welle Bild 11 VOLL (2.8.9, Musterprojekt): dritte Seite Kosten und Fahrplan-Abgleich,
  # Knopf und Vorlage VI_smartmeter_kosten.xml (Titel, Kommentar, Befehlskommentare).
  ('BL_KOSTEN',
   'Kosten und Fahrplan-Abgleich',
   'Costs and schedule check'),
  ('VE_K_QUELLE_OK',
   'Preise erreichbar (1/0)',
   'Prices reachable (1/0)'),
  ('VE_K_STUNDE_CT',
   'Kosten der letzten vollen Stunde, -1 = unbekannt',
   'Cost of the last full hour, -1 = unknown'),
  ('VE_K_HEUTE',
   'Kosten heute bisher, -1 = unbekannt',
   'Cost today so far, -1 = unknown'),
  ('VE_K_HEUTE_KWH',
   'heute verbraucht (Stunden mit Preis), -1 = unbekannt',
   'used today (hours with price), -1 = unknown'),
  ('VE_K_STUNDEN',
   'gerechnete Stunden heute',
   'hours calculated today'),
  ('VE_K_OFFEN',
   'Stunden ohne belegte Einheit',
   'hours without confirmed unit'),
  ('VE_K_OHNE_PREIS',
   'Stunden ohne Preis',
   'hours without price'),
  ('VE_A_QUELLE_OK',
   'Fahrplan erreichbar (1/0)',
   'Schedule reachable (1/0)'),
  ('VE_A_AKTIV',
   'Regel %s soll gerade laufen (1/0)',
   'Rule %s should be running (1/0)'),
  ('VE_A_SOLL',
   'Soll von Regel %s',
   'Target of rule %s'),
  ('VE_A_IST',
   'gemessener Netzbezug seit Beginn von Regel %s',
   'measured grid consumption since start of rule %s'),
  ('VE_A_FEHLT',
   'Fehlbetrag von Regel %s',
   'Shortfall of rule %s'),
  ('VE_A_DAUER',
   'Laufzeit von Regel %s',
   'Running time of rule %s'),
  ('VE_A_SICHER',
   'Urteil möglich (1/0)',
   'Verdict possible (1/0)'),
  ('VE_A_OK',
   '1 = zieht, 0 = zieht nicht, -1 = kein Urteil',
   '1 = draws, 0 = does not draw, -1 = no verdict'),
  # Gruppe 1 (2.8.11): Schritt 2 nach der Fassung des MQTT-Gateways (V2: Hakenliste aus
  # sm_v2_haken(), dieselben Eintraege wie die Vorlagen).
  ('S2_TITEL_V2',
   'Schritt 2: Datenpunkte im MQTT-Gateway anhaken',
   'Step 2: tick the data points in the MQTT gateway'),
  ('S2_TITEL_BEIDE',
   'Schritt 2: Abo im MQTT-Gateway prüfen (V1) bzw. Datenpunkte anhaken (V2)',
   'Step 2: check the subscription in the MQTT gateway (V1) or tick the data points (V2)'),
  ('SP_DATENPUNKT',
   'Datenpunkt im MQTT-Gateway',
   'Data point in the MQTT gateway'),
  ('SP_ZUSATZ',
   'zusätzlich',
   'additionally'),
  ('HAKEN_LEER',
   'Noch keine Datenpunkte: zuerst einen Leseweg einrichten (beim klassischen Weg die erste Messung abwarten); Kosten und Fahrplan erscheinen erst mit Schritt 10 bzw. 11.',
   'No data points yet: set up a reading path first (on the classic path wait for the first reading); costs and schedule appear only with step 10 or 11.'),
  ('HAKEN_QUELLE',
   'Die Liste entsteht aus denselben Einträgen wie die Namenstabelle in Schritt 3, nur für die eingeschalteten Teile. Nur den Leseweg anhaken, den Sie betreiben.',
   'The list is built from the same entries as the name table in step 3, only for the parts that are switched on. Tick only the reading path you run.'),
  ('NAMEN_ANLEITUNG',
   'Je Wert in Loxone Config unter Peripherie → Virtuelle Eingänge einen <b>Virtuellen Eingang</b> anlegen, für einen Text einen <b>Virtuellen Texteingang</b>. Als Namen genau den Namen aus der Tabelle eintragen (Knopf „kopieren“) und „Als Digitaleingang verwenden“ <b>nicht</b> aktivieren. Die Werte schreibt das MQTT-Gateway; nur die Eingänge anlegen, die Sie brauchen.',
   'For each value create a <b>virtual input</b> in Loxone Config under Periphery → Virtual inputs, for a text a <b>virtual text input</b>. Enter exactly the name from the table as the name (button “copy”) and do <b>not</b> activate “Use as digital input”. The MQTT gateway writes the values; create only the inputs you need.'),
  ('NAMEN_RECHTE',
   'Der Benutzer, mit dem der LoxBerry am Miniserver angemeldet ist, braucht in Loxone Config Rechte auf diese Eingänge – sonst kommen die Werte nicht an.',
   'The user with which the LoxBerry logs in to the Miniserver needs rights on these inputs in Loxone Config – otherwise the values do not arrive.'),
  ('NAMEN_MUSTER',
   'Wer die Seiten aus dem LoxBerry-Plugins Musterprojekt kopiert (Schritt 6), bekommt die Eingänge mit – dann nur die Zählernummer im Namen an die eigene anpassen.',
   'Whoever copies the pages from the LoxBerry plugins sample project (step 6) gets the inputs included – then only adapt the meter number in the name to your own.'),
  ('NAMEN_AUS',
   'derzeit ausgeschaltet – Werte kommen erst nach dem Einschalten',
   'currently switched off – values arrive only after switching on'),
  ('NAMEN_KOPIEREN',
   'kopieren',
   'copy'),
  ('NAMEN_KOPIERT',
   'kopiert',
   'copied'),
  ('NAMEN_MARKIEREN',
   'bitte von Hand markieren',
   'please select by hand'),
  ('NAMEN_ZAHL',
   'Zahl (Virtueller Eingang)',
   'number (virtual input)'),
  ('NAMEN_TEXT',
   'Text (Virtueller Texteingang)',
   'text (virtual text input)'),
  ('SP_BEREICH',
   'Einheit, Bereich',
   'Unit, range'),
  ('SP_ART',
   'Zahl/Text',
   'Number/text'),
  ('KO_NAMEN',
   'Die Namen der Eingänge für die Seite „Kosten und Fahrplan-Abgleich“ (Schritt 6) stehen in Schritt 3 in der Namenstabelle (Kostenrechnung, Fahrplan-Abgleich – mit allen Regeln, die der Fahrplan führt, und den Kosten von gestern). Die Werte kommen erst, wenn Schritt 10 und 11 eingeschaltet sind.',
   'The names of the inputs for the page “Costs and schedule check” (step 6) are in the name table in step 3 (cost calculation, schedule check – with every rule the schedule carries, and yesterday’s cost). The values arrive only when steps 10 and 11 are switched on.'),
  # Gruppe 35 (2.8.13): Schalter Endpunkt/Lastgang (E-E8), Namen kosten/gestern_*, abgleich/<n>/speicher.
  ('EP_LABEL',
   'Endpunkt für den Miniserver einschalten (ENDPUNKT_EIN)',
   'Switch on the endpoint for the Miniserver (ENDPUNKT_EIN)'),
  ('EP_HINT',
   'Ab Werk aus: die Werte gehen über das MQTT-Gateway V2. Wer einen Virtuellen HTTP-Eingang auf diese Adresse benutzt, lässt den Haken an – eine bestehende Anlage hat ihn beim Update behalten. Aus heißt: die Adresse antwortet 403 mit ERR=ENDPUNKT_AUS; der Selbsttest bleibt erreichbar.',
   'Off by default: the values go through the MQTT gateway V2. Anyone using a virtual HTTP input on this address keeps the box ticked – an existing installation kept it on update. Off means: the address answers 403 with ERR=ENDPUNKT_AUS; the self-test stays reachable.'),
  ('EP_AUS',
   'Der Endpunkt ist ausgeschaltet – er liefert keine Werte (403, ERR=ENDPUNKT_AUS).',
   'The endpoint is switched off – it delivers no values (403, ERR=ENDPUNKT_AUS).'),
  ('LG_LABEL',
   'Lastgang für die Spotpreis-Plugins einschalten (LASTGANG_EIN)',
   'Switch on the load profile for the spot price plugins (LASTGANG_EIN)'),
  ('LG_AUS',
   'Der Lastgang ist ausgeschaltet (403, LASTGANG_AUS) – das Spotpreis-Plugin rechnet dann mit seinem eingebauten Haushaltsprofil.',
   'The load profile is switched off (403, LASTGANG_AUS) – the spot price plugin then uses its built-in household profile.'),
  ('VE_A_SPEICHER',
   '1 = Speicher entlud im Regelfenster, 0 = nein, -1 = keine Aussage',
   '1 = battery discharged during the rule, 0 = no, -1 = no statement'),
  ('VE_K_GESTERN_EUR',
   'Kosten gestern (samt 23–24 Uhr), -1 = nicht gerechnet',
   'Cost yesterday (including 23–24 h), -1 = not calculated'),
  ('VE_K_GESTERN_KWH',
   'gestern verbraucht (Stunden mit Preis), -1 = nicht gerechnet',
   'consumed yesterday (hours with price), -1 = not calculated'),
  ('VE_K_GESTERN_CT',
   'Kosten gestern in ct, -1 = nicht gerechnet',
   'Cost yesterday in ct, -1 = not calculated'),
  ('VE_K_GESTERN_STUNDEN',
   'gerechnete Stunden gestern',
   'hours calculated yesterday'),
 ]),
 ('AB', [
  ('TITEL',
   'Schritt 10: Tut die Hardware, was der Fahrplan sagt?',
   'Step 10: is the hardware doing what the schedule says?'),
  ('TEXT',
   'Der Planer der Spotpreis-Plugins schaltet Regeln in die günstigen '
   'Stunden — ob das Gerät dann wirklich zieht, weiß er nicht: er sendet '
   'einen Befehl und sieht keinen Zähler. Dieses Plugin sieht den Zähler.',
   'The spot price plugins’ planner switches rules into the cheap hours — '
   'whether the device then actually draws power it cannot know: it sends a '
   'command and sees no meter. This plugin sees the meter.'),
  ('SCHRANKE',
   'Gerechnet wird eine <b>untere Schranke</b>, kein Delta: Läuft eine Regel mit 11 kW 47 Minuten, muss sie 8,6 kWh gezogen haben — der Netzbezug kann nur größer sein, weil der Rest des Hauses dazukommt und nie abzieht. Sind es 2,1 kWh, hat die Regel <b>nachweislich</b> nicht gezogen. Ein „geplanter Netzbezug“ dagegen existiert nicht: der Planer plant Schaltfenster einzelner Regeln, gemessen wird das ganze Haus. <b>Zwei Ausnahmen:</b> eigene Einspeisung und – mit dem Haken „Speicher berücksichtigen“ – ein entladender Hausspeicher drücken den Bezug, ohne dass die Regel weniger zieht — dann ist die Schranke keine, und es wird nicht geurteilt, sondern „unsicher“ gemeldet.',
   'What is computed is a <b>lower bound</b>, not a delta: if a rule rated at 11 kW runs for 47 minutes it must have drawn 8.6 kWh — grid consumption can only be larger, because the rest of the house adds to it and never subtracts. If it is 2.1 kWh, the rule <b>demonstrably</b> did not draw. A „planned grid consumption“ does not exist: the planner schedules windows for individual rules, while the meter sees the whole house. <b>Two exceptions:</b> your own feed-in and – with the box „take the battery into account“ – a discharging home battery lower consumption without the rule drawing less — then the bound is none, and no verdict is given but “uncertain” is reported.'),
  ('LABEL_AKTIV', 'Fahrplan-Abgleich einschalten',
   'Enable schedule cross-check'),
  ('LABEL_URL', 'Adresse des Fahrplans', 'Address of the schedule'),
  ('HINT_URL',
   'Der JSON-Endpunkt des örtlichen Spotpreis-Plugins, zum Beispiel '
   "<span class='sm-mono'>http://127.0.0.1/plugins/spotpreis/spot.php?json=1</span>. "
   'Der Ordnername hängt an der Linie (spotpreis, spotpreis-octopus, '
   'spotpreis-tibber). Nur http und https werden angenommen.',
   'The JSON endpoint of the local spot price plugin, for example '
   "<span class='sm-mono'>http://127.0.0.1/plugins/spotpreis/spot.php?json=1</span>. "
   'The folder name depends on the line (spotpreis, spotpreis-octopus, '
   'spotpreis-tibber). Only http and https are accepted.'),
  ('FEHLER_URL',
   'Die Adresse des Fahrplans muss mit http:// oder https:// beginnen, darf weder Leerzeichen, Anführungszeichen noch Steuerzeichen enthalten und höchstens 512 Zeichen lang sein.',
   'The schedule address must start with http:// or https://, must not contain spaces, quotes or control characters and may be at most 512 characters long.'),
  ('FEHLER_LEER',
   'Ohne Adresse lässt sich der Abgleich nicht einschalten — er hätte nichts '
   'abzufragen.',
   'The cross-check cannot be enabled without an address — there would be '
   'nothing to query.'),
  ('SP_REGEL', 'Regel', 'Rule'),
  ('SP_SOLL', 'Soll kWh', 'Target kWh'),
  ('SP_IST', 'Gemessen kWh', 'Measured kWh'),
  ('SP_FEHLT', 'Fehlt kWh', 'Missing kWh'),
  ('SP_URTEIL', 'Urteil', 'Verdict'),
  ('U_ZIEHT', 'zieht', 'drawing'),
  ('U_ZIEHT_NICHT', 'zieht NICHT', 'NOT drawing'),
  ('U_UNSICHER',
   'unsicher (Einspeisung, entladender Speicher oder Einheit offen)',
   'uncertain (feed-in, discharging battery, or unit not established)'),
  ('U_ZU_KURZ', 'zu kurz für ein Urteil', 'too short for a verdict'),
  ('U_LAEUFT_AN', 'läuft an', 'starting up'),
  ('U_OHNE_LEISTUNG', 'ohne eingetragene Leistung', 'no power rating entered'),
  ('U_KEIN_ZAEHLER', 'kein Zählerstand', 'no meter reading'),
  ('U_KEIN_START', 'kein Startpunkt', 'no starting point'),
  ('U_ZAEHLER_SPRANG', 'Zähler sprang', 'meter jumped'),
  ('QUELLE_WEG',  # (1) Grund
   'Der Fahrplan war beim letzten Lauf nicht erreichbar (%s). Die Zahlen '
   'oben sind der letzte bekannte Stand — sie werden nicht geleert, denn '
   'eine 0 wäre eine Aussage, und „unbekannt“ ist hier die richtige.',
   'The schedule was unreachable on the last run (%s). The numbers above are '
   'the last known state — they are not cleared, because a 0 would be a '
   'statement, and „unknown“ is the correct one here.'),
  ('NOCH_NICHTS',
   'Der Abgleich ist eingeschaltet, hat aber noch keine Regel beobachtet. Er '
   'läuft alle fünf Minuten; ein Urteil entsteht, sobald eine Regel länger '
   'als zehn Minuten aktiv war.',
   'The cross-check is enabled but has not observed a rule yet. It runs every '
   'five minutes; a verdict appears once a rule has been active for more than '
   'ten minutes.'),
  ('U_UNBEKANNT',
   'unbekanntes Urteil: %s',
   'unknown verdict: %s'),
  # Gruppe 35 (2.8.13): Abnehmer haus/speicher (Entscheidung 5).
  ('LABEL_SPEICHER',
   'Speicher im Fahrplan-Abgleich berücksichtigen (haus/speicher)',
   'Take the home battery into account in the schedule check (haus/speicher)'),
  ('HINT_SPEICHER',
   'Ab Werk aus; wirkt nur mit MQTT und eingeschaltetem Abgleich. Ein entladender Hausspeicher drückt den Netzbezug wie eine Einspeisung – entlädt er während einer Regel, gibt es kein Urteil („unsicher“) statt „zieht nicht“. Gelesen wird das Haus-Thema haus/speicher (Anbieter: Marstek Venus E ab 1.1.27); schweigt die Quelle, urteilt das Plugin wie bisher ohne Speicher.',
   'Off by default; only effective with MQTT and the schedule check switched on. A discharging home battery lowers grid consumption like feed-in – if it discharges while a rule runs, there is no verdict („uncertain“) instead of „does not draw“. The house topic haus/speicher is read (provider: Marstek Venus E from 1.1.27); if the source is silent, the plugin judges as before without the battery.'),
  ('SL_NOCH_KEINE',
   'haus/speicher: noch keine Lage – der Leser läuft nur, solange eine Regel aktiv ist.',
   'haus/speicher: no reading yet – the reader only runs while a rule is active.'),
  ('SL_QUELLE_SCHWEIGT',
   'haus/speicher: die Speicherquelle schweigt (letzte Lage vor %d s) – Urteil ohne Speicher.',
   'haus/speicher: the battery source is silent (last reading %d s ago) – verdict without the battery.'),
  ('SL_ENTLAEDT',
   'haus/speicher: der Speicher entlädt (Lage vor %d s) – eine laufende Regel wird nicht beurteilt.',
   'haus/speicher: the battery is discharging (reading %d s ago) – a running rule is not judged.'),
  ('SL_ENTLAEDT_NICHT',
   'haus/speicher: der Speicher entlädt nicht (Lage vor %d s).',
   'haus/speicher: the battery is not discharging (reading %d s ago).'),
  ('SL_OHNE_AUSSAGE',
   'haus/speicher: keine Aussage (Speicher stumm, Lage vor %d s) – Urteil ohne Speicher.',
   'haus/speicher: no statement (battery silent, reading %d s ago) – verdict without the battery.'),
 ]),

 ('KO', [
  ('TITEL',
   'Schritt 11: Was hat der Strom heute gekostet?',
   'Step 11: what did electricity cost today?'),
  ('TEXT',
   'Der Miniserver kann Zählerstände addieren, aber keine Stundenpreise '
   'nachhalten — bei einem dynamischen Tarif fehlt ihm für jede vergangene '
   'Stunde der Preis, der damals galt. Dieses Plugin hat beides: die Menge '
   'je Stunde aus dem Lastgang und den Stundenpreis vom örtlichen '
   'Spotpreis-Plugin.',
   'The Miniserver can add up meter readings, but it cannot keep hourly '
   'prices — with a dynamic tariff it lacks, for every past hour, the '
   'price that applied back then. This plugin has both: the amount per '
   'hour from the load profile and the hourly price from the local spot '
   'price plugin.'),
  ('NUR_HEUTE',
   'Gerechnet wird der <b>heutige Tag</b>; den <b>Vortag</b> schließt der erste Lauf nach 0 Uhr ab – samt der Stunde 23–24 Uhr, mit den Preisen, die sich das Plugin am Vortag selbst gemerkt hat (eine Zeile je Tag in kosten_historie.csv, MQTT kosten/gestern_*). Weiter zurück führt das Spotpreis-Plugin keine Stundenpreise; eine Zahl aus dem Tagesmittel hieße „Kosten“ und wäre keine. Genommen wird der <b>Endpreis</b> je Stunde, nicht der Börsenpreis.',
   '<b>Today</b> is computed; the first run after midnight closes the <b>previous day</b> – including the hour 23–24, with the prices the plugin noted itself the day before (one line per day in kosten_historie.csv, MQTT kosten/gestern_*). Further back the spot price plugin keeps no hourly prices; a number derived from the daily average would be called „cost“ and would not be one. What is used is the <b>end price</b> per hour, not the exchange price.'),
  ('LABEL_AKTIV',
   'Kostenrechnung einschalten',
   'Enable cost calculation'),
  ('LABEL_URL',
   'Adresse der Preise',
   'Address of the prices'),
  ('HINT_URL',
   'Derselbe JSON-Endpunkt wie beim Fahrplan-Abgleich. Bleibt das Feld '
   'leer, wird die dort eingetragene Adresse benutzt. Nur http und https '
   'werden angenommen.',
   'The same JSON endpoint as for the schedule cross-check. If this field '
   'is left empty, the address entered there is used. Only http and https '
   'are accepted.'),
  ('FEHLER_URL',
   'Die Adresse der Preise muss mit http:// oder https:// beginnen, darf weder Leerzeichen, Anführungszeichen noch Steuerzeichen enthalten und höchstens 512 Zeichen lang sein.',
   'The price address must start with http:// or https://, must not contain spaces, quotes or control characters and may be at most 512 characters long.'),
  ('FEHLER_LEER',
   'Ohne Adresse — hier oder beim Fahrplan-Abgleich — lässt sich die '
   'Kostenrechnung nicht einschalten; sie hätte keine Preise.',
   'Without an address — here or at the schedule cross-check — the cost '
   'calculation cannot be enabled; it would have no prices.'),
  ('SP_GROESSE',
   'Größe',
   'Quantity'),
  ('SP_WERT',
   'Wert',
   'Value'),
  ('Z_STUNDE',
   'letzte volle Stunde',
   'last full hour'),
  ('Z_HEUTE',
   'heute bisher',
   'today so far'),
  ('Z_MENGE',
   'heute bisher verbraucht',
   'consumed today so far'),
  ('Z_STUNDEN',
   'gerechnete Stunden',
   'hours computed'),
  ('UEBERGANGEN',
   'Übergangen: %d Stunde(n) ohne belegte Einheit, %d Stunde(n) ohne '
   'Preis. Sie werden gezählt und nicht mitgerechnet — mit dem Mittel '
   'gefüllt wären sie eine erfundene Zahl.',
   'Skipped: %d hour(s) without an established unit, %d hour(s) without a '
   'price. They are counted and not included — filled in from the average '
   'they would be an invented number.'),
  ('QUELLE_WEG',
   'Die Preise waren beim letzten Lauf nicht erreichbar (%s). Die Zahlen '
   'oben sind der letzte bekannte Stand.',
   'The prices were unreachable on the last run (%s). The numbers above '
   'are the last known state.'),
  ('NOCH_NICHTS',
   'Die Kostenrechnung ist eingeschaltet, hat aber noch nicht gerechnet. '
   'Sie läuft alle fünf Minuten und braucht mindestens eine abgeschlossene '
   'Stunde im Lastgang.',
   'The cost calculation is enabled but has not computed anything yet. It '
   'runs every five minutes and needs at least one completed hour in the '
   'load profile.'),
  # Gruppe 35 (2.8.13): Tagesabschluss, 14-Tage-Tabelle, CSV (Entscheidung 2, E-E14).
  ('H_TAGE',
   'Die letzten 14 Tage (Tagesabschluss samt 23–24 Uhr)',
   'The last 14 days (daily close including 23–24 h)'),
  ('SP_DATUM',
   'Tag',
   'Day'),
  ('SP_EUR',
   'Kosten (EUR)',
   'Cost (EUR)'),
  ('SP_KWH',
   'Verbrauch (kWh)',
   'Consumption (kWh)'),
  ('SP_CT_KWH',
   'Schnitt (ct/kWh)',
   'Average (ct/kWh)'),
  ('SP_STUNDEN',
   'Stunden',
   'Hours'),
  ('SP_HINWEIS',
   'Hinweis',
   'Note'),
  ('T_OHNE_PREIS',
   '%d Stunde(n) ohne Preis',
   '%d hour(s) without price'),
  ('T_OFFEN',
   '%d Stunde(n) ohne belegte Einheit',
   '%d hour(s) without established unit'),
  ('T_OHNE23',
   'ohne 23–24 Uhr (Frist 01:00 verstrichen)',
   'without 23–24 h (deadline 01:00 passed)'),
  ('TAGE_LEER',
   'Noch kein abgeschlossener Tag. Der erste Kostenlauf nach 0 Uhr schließt den Vortag ab – sobald dessen Stunde 23–24 Uhr im Lastgang steht, spätestens um 01:00.',
   'No completed day yet. The first cost run after midnight closes the previous day – as soon as its hour 23–24 is in the load profile, at the latest at 01:00.'),
  ('K_CSV',
   'Tageskosten als CSV herunterladen',
   'Download daily cost as CSV'),
 ]),

 ('BAUSTEIN', [
  # Welle Bild 7 (2.8.8): die Zellen der beiden Baustein-Listen (Musterprojekt/baustein_listen.txt,
  # Abschnitte Smartmeter klassisch und Smartmeter vzLogger). %s = Vorlagentitel, Einheit,
  # Zaehlernummer - sie unterscheiden die beiden Lesewege und kommen aus index.php.
  ('VHTTP_TYP',
   'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Smartmeter classic)',
   'Virtual input (name as assigned by the MQTT gateway, plugin Smartmeter classic)'),
  ('B1_PARAM',
   'Zählerstand Bezug in %s (%s = Zählernummer aus den Einstellungen)',
   'meter reading consumption in %s (%s = meter number from the settings)'),
  ('B2_PARAM',
   'aktuelle Wirkleistung in %s, Einspeisung negativ',
   'current active power in %s, feed-in negative'),
  ('B3_PARAM',
   '1 = alle Leseköpfe aktuell (kommt jede Minute; im MQTT-Gateway V2 „Noncached“ anhaken)',
   '1 = all reading heads up to date (arrives every minute; tick „Noncached“ in MQTT gateway V2)'),
  ('B5_TYP',
   'Konstante',
   'Constant'),
  ('B5_NAME',
   'Konstante 1',
   'Konstante 1'),
  ('B5_PARAM',
   'Wert 1',
   'value 1'),
  ('B6_TYP',
   'Impuls um',
   'Pulse at'),
  ('B6_NAME',
   'Tagesbeginn 0:00',
   'Tagesbeginn 0:00'),
  ('B6_PARAM',
   'Zu bestimmter Uhrzeit, 00:00:00',
   'At a set time, 00:00:00'),
  ('B7_TYP',
   'Analogspeicher',
   'Analog memory'),
  ('B7_NAME',
   'Stand bei Tagesbeginn (%s)',
   'Stand bei Tagesbeginn (%s)'),
  ('B7_VERB',
   'V = #1, Set = Ausgang Q von #6',
   'V = #1, Set = output Q of #6'),
  ('B8_TYP',
   'Formel',
   'Formula'),
  ('B8_NAME',
   'Verbrauch heute (%s)',
   'Verbrauch heute (%s)'),
  ('B8_PARAM',
   'I1-I2',
   'I1-I2'),
  ('B8_VERB',
   'I1 = #1, I2 = #7',
   'I1 = #1, I2 = #7'),
  ('B9_TYP',
   'Kleiner',
   'Less than'),
  ('B9_NAME',
   'Einspeisung aktiv',
   'Einspeisung aktiv'),
  ('B9_PARAM',
   'V2 = 0 (offen lassen)',
   'V2 = 0 (leave open)'),
  ('B9_VERB',
   'V1 = #2',
   'V1 = #2'),
  ('B10_TYP',
   'NICHT',
   'NOT'),
  ('B10_NAME',
   'Lesekopf meldet Fehler',
   'Lesekopf meldet Fehler'),
  ('B10_VERB',
   'I = #3',
   'I = #3'),
  ('B11_TYP',
   'Analogwertvalidierung',
   'Analog value validation'),
  ('B11_NAME',
   'Lesekopf zählt nicht mehr',
   'Lesekopf zählt nicht mehr'),
  ('B11_PARAM',
   'Tmc 300 s, Min 0, Max 999; Haken bei „En“ entfernen',
   'Tmc 300 s, Min 0, Max 999; remove the tick at „En“'),
  ('B11_VERB',
   'V = #4, En = #5',
   'V = #4, En = #5'),
  ('B12_TYP',
   'ODER',
   'OR'),
  ('B12_NAME',
   'Stromzähler gestört',
   'Stromzähler gestört'),
  ('B13_TYP',
   'Benachrichtigung',
   'Notification'),
  ('B13_NAME',
   'Stromzähler prüfen',
   'Stromzähler prüfen'),
  ('B13_PARAM',
   'Betreff und Text frei',
   'Subject and text as you like'),
  ('B13_VERB',
   'Eingang = #12',
   'Input = #12'),
  ('B14_TYP',
   'Status',
   'Status'),
  ('B14_NAME',
   'Strom aktuell',
   'Strom aktuell'),
  ('B14_PARAM',
   'Text z. B. „<v1> %s, Bezug <v2> %s“',
   'Text e.g. “<v1> %s, consumption <v2> %s”'),
  ('B14_VERB',
   'V1 = #2, V2 = #1',
   'V1 = #2, V2 = #1'),
  ('H_TAGESVERBRAUCH',
   'Verbrauch und Einspeisung heute: Der Impuls um 0:00 übernimmt den Zählerstand in den Analogspeicher (Remanenz an, sonst steht der Tagesbeginn nach einem Neustart des Miniservers auf 0), die Formel rechnet die Differenz. Die Werte stimmen erst ab dem ersten Mitternachtsimpuls nach dem Übertragen.',
   'Consumption and feed-in today: the pulse at 0:00 copies the meter reading into the analog memory (retentive on, otherwise the start of day is 0 after a Miniserver restart), the formula calculates the difference. The values are right only from the first midnight pulse after the transfer.'),
  ('H_STATISTIK',
   'Statistik ist kein Baustein: am Eingang der Wirkleistung ‚Statistik‘ einschalten.',
   'Statistics is not a block: switch on ‘Statistics’ at the input of the active power.'),
  ('H_EINHEITEN',
   'Der klassische Weg liefert kWh und kW, vzLogger Wh und W.',
   'The classic path delivers kWh and kW, vzLogger Wh and W.'),
  ('H_BENACHRICHTIGUNG',
   'Wer beide Lesewege betreibt, baut die Überwachung Nr. 10–13 nur einmal – beide Wege melden über dieselben Lebenszeichen %s und %s.',
   'If you run both reading paths, build the monitoring no. 10–13 only once – both paths report via the same signs of life %s and %s.'),
  ('H_ODER',
   '<b>Zu #12 und #13:</b> Der Benachrichtigungs-Baustein sendet nur beim Wechsel von Aus auf Ein. <b>Niemals mehrere Quellen direkt an seinen Eingang</b> — erst über ODER zusammenführen, sonst verschluckt eine dauerhaft aktive Quelle alle übrigen.',
   '<b>On #12 and #13:</b> The notification block only fires on a change from off to on. <b>Never wire several sources directly to its input</b> — merge them through an OR first, otherwise a permanently active source swallows all the others.'),
  # Welle Bild 11 VOLL (2.8.9): Vollausstattung aus Musterprojekt/baustein_listen.txt -
  # Zeilen 15-27 der Lesewege (_K klassisch, _V vzLogger), Seite Kosten und Fahrplan (P*),
  # Typnamen T_*, Kasten So uebernehmen Sie diese Seite (*_S*) und Hinweise (*_H_*).
  ('SCHRITTE_TITEL',
   'So übernehmen Sie diese Seite',
   'How to take over this page'),
  ('HINWEISE_TITEL',
   'Hinweise',
   'Notes'),
  ('T_ANALOGSPEICHER',
   'Analogspeicher',
   'Analog memory'),
  ('T_FORMEL',
   'Formel',
   'Formula'),
  ('T_STATUS',
   'Status',
   'Status'),
  ('T_SCHWELLWERT',
   'Schwellwertschalter',
   'Threshold switch'),
  ('T_EVZ',
   'Einschaltverzögerung',
   'On-delay'),
  ('T_ZAEHLER_BI',
   'Zähler Bidirektional',
   'Bidirectional meter'),
  ('T_NICHT',
   'NICHT',
   'NOT'),
  ('T_GLEICH',
   'Gleich',
   'Equal'),
  ('T_UND',
   'UND',
   'AND'),
  ('T_BENACHRICHTIGUNG',
   'Benachrichtigung',
   'Notification'),
  ('B7_PARAM',
   'Remanenz an (Rem), damit ein Neustart des Miniservers den Tagesstand nicht löscht',
   'Retentive on (Rem), so that a restart of the Miniserver does not erase the start-of-day reading'),
  ('B15_PARAM_K',
   'Zählerstand Einspeisung in kWh; fehlt der Eingang in der eigenen Vorlage, hat der Zähler kein Einspeisezählwerk – dann Nr. 15–17, 19 und 21–23 weglassen',
   'meter reading feed-in in kWh; if the input is missing in your own template, the meter has no feed-in register – then leave out no. 15–17, 19 and 21–23'),
  ('B15_PARAM_V',
   'Zählerstand Einspeisung in Wh; nur, wenn im Reiter vzLogger ein Kanal 2.8.0 eingetragen ist – sonst Nr. 15–17, 19, 21–23 und 26 weglassen',
   'meter reading feed-in in Wh; only if a channel 2.8.0 is entered in the vzLogger tab – otherwise leave out no. 15–17, 19, 21–23 and 26'),
  ('B16_NAME',
   'Einspeise-Stand bei Tagesbeginn (%s)',
   'Einspeise-Stand bei Tagesbeginn (%s)'),
  ('B16_VERB',
   'V = #15, Set = Ausgang Q von #6',
   'V = #15, Set = output Q of #6'),
  ('B17_NAME',
   'Einspeisung heute (%s)',
   'Einspeisung heute (%s)'),
  ('B17_PARAM',
   'I1-I2',
   'I1-I2'),
  ('B17_VERB',
   'I1 = #15, I2 = #16',
   'I1 = #15, I2 = #16'),
  ('B18_PARAM_K',
   'mittlere Bezugsleistung seit der letzten Ablesung in kW (aus dem Zählerstand gerechnet), 0 beim Einspeisen; nach einem Neustart des LoxBerry kommt der erste Wert erst mit der zweiten Ablesung',
   'average consumption power since the last reading in kW (calculated from the meter reading), 0 when feeding in; after a LoxBerry restart the first value arrives only with the second reading'),
  ('B18_PARAM_V',
   'Bezugsleistung jetzt in W (aus der Wirkleistung abgeleitet), 0 beim Einspeisen',
   'consumption power now in W (derived from the active power), 0 while feeding in'),
  ('B19_PARAM_K',
   'mittlere Einspeiseleistung seit der letzten Ablesung in kW, 0 beim Bezug',
   'average feed-in power since the last reading in kW, 0 while consuming'),
  ('B19_PARAM_V',
   'Einspeiseleistung jetzt in W (als positive Zahl), 0 beim Bezug',
   'feed-in power now in W (as a positive number), 0 while consuming'),
  ('B20_NAME',
   'Strom heute',
   'Strom heute'),
  ('B20_PARAM_K',
   'Zeilen: V5 = 1 „Stromzähler gestört – Stand der letzten Ablesung: heute Bezug <v1.2> kWh, Einspeisung <v2.2> kWh“; V4 > 0 „speist ein, im Mittel <v4.2> kW – heute Bezug <v1.2> kWh, Einspeisung <v2.2> kWh“; ohne Bedingung „bezieht, im Mittel <v3.2> kW – heute Bezug <v1.2> kWh, Einspeisung <v2.2> kWh“',
   'Lines: V5 = 1 “meter faulty – last reading: today consumption <v1.2> kWh, feed-in <v2.2> kWh”; V4 > 0 “feeding in, on average <v4.2> kW – today consumption <v1.2> kWh, feed-in <v2.2> kWh”; without condition “consuming, on average <v3.2> kW – today consumption <v1.2> kWh, feed-in <v2.2> kWh”'),
  ('B20_PARAM_V',
   'Zeilen: V5 = 1 „Stromzähler gestört – Stand der letzten Ablesung: heute Bezug <v1.0> Wh, Einspeisung <v2.0> Wh“; V4 > 0 „speist <v4.0> W ein – heute Bezug <v1.0> Wh, Einspeisung <v2.0> Wh“; ohne Bedingung „bezieht <v3.0> W – heute Bezug <v1.0> Wh, Einspeisung <v2.0> Wh“',
   'Lines: V5 = 1 “meter faulty – last reading: today consumption <v1.0> Wh, feed-in <v2.0> Wh”; V4 > 0 “feeding in <v4.0> W – today consumption <v1.0> Wh, feed-in <v2.0> Wh”; without condition “consuming <v3.0> W – today consumption <v1.0> Wh, feed-in <v2.0> Wh”'),
  ('B20_VERB',
   'V1 = #8, V2 = #17, V3 = #18, V4 = #19, V5 = #12',
   'V1 = #8, V2 = #17, V3 = #18, V4 = #19, V5 = #12'),
  ('B21_NAME',
   'PV-Überschuss',
   'PV-Überschuss'),
  ('B21_PARAM_K',
   'Ein 1,5 / Aus 0,3 (kW mittlere Einspeisung)',
   'On 1.5 / Off 0.3 (kW average feed-in)'),
  ('B21_PARAM_V',
   'Ein 1500 / Aus 300 (W Einspeisung)',
   'On 1500 / Off 300 (W feed-in)'),
  ('B21_VERB',
   'Eingang = #19',
   'Input = #19'),
  ('B22_NAME',
   'Überschuss hält an',
   'Überschuss hält an'),
  ('B22_PARAM',
   '300 s',
   '300 s'),
  ('B22_VERB',
   'Eingang = #21',
   'Input = #21'),
  ('B23_NAME',
   'Überschuss jetzt',
   'Überschuss jetzt'),
  ('B23_PARAM_K',
   'Zeilen: V1 = 1 „Überschuss: <v2.2> kW – eigener Verbraucher darf laufen“; V2 > 0 „speist <v2.2> kW ein – noch kein freigegebener Überschuss“; ohne Bedingung „kein Überschuss“',
   'Lines: V1 = 1 “surplus: <v2.2> kW – own consumer may run”; V2 > 0 “feeding in <v2.2> kW – no released surplus yet”; without condition “no surplus”'),
  ('B23_PARAM_V',
   'Zeilen: V1 = 1 „Überschuss: <v2.0> W – eigener Verbraucher darf laufen“; V2 > 0 „speist <v2.0> W ein – noch kein freigegebener Überschuss“; ohne Bedingung „kein Überschuss“',
   'Lines: V1 = 1 “surplus: <v2.0> W – own consumer may run”; V2 > 0 “feeding in <v2.0> W – no released surplus yet”; without condition “no surplus”'),
  ('B23_VERB',
   'V1 = #22, V2 = #19',
   'V1 = #22, V2 = #19'),
  ('ZB_NAME',
   'Stromzähler Netz',
   'Stromzähler Netz'),
  ('ZB_PARAM',
   'Einheiten <v.3> kW und <v.1> kWh; In Visualisierung verwenden an; zeigt in der App Bezug und Einspeisung für heute, Woche, Monat und Jahr',
   'Units <v.3> kW and <v.1> kWh; Use in visualization on; shows consumption and feed-in in the app for today, week, month and year'),
  ('ZB_VERB_K',
   'Pf = #2, Mr1 = #1, Mr2 = #15',
   'Pf = #2, Mr1 = #1, Mr2 = #15'),
  ('ZB_VERB_V',
   'Pf = #24, Mr1 = #25, Mr2 = #26',
   'Pf = #24, Mr1 = #25, Mr2 = #26'),
  ('V24_NAME',
   'Wirkleistung (kW)',
   'Wirkleistung (kW)'),
  ('V24_PARAM',
   'I1/1000 (der Zähler-Baustein rechnet in kW, das Plugin liefert W)',
   'I1/1000 (the meter block calculates in kW, the plugin delivers W)'),
  ('V24_VERB',
   'I1 = #2',
   'I1 = #2'),
  ('V25_NAME',
   'Bezug gesamt (kWh)',
   'Bezug gesamt (kWh)'),
  ('V25_PARAM',
   'I1/1000 (der Zähler-Baustein rechnet in kWh, das Plugin liefert Wh)',
   'I1/1000 (the meter block calculates in kWh, the plugin delivers Wh)'),
  ('V25_VERB',
   'I1 = #1',
   'I1 = #1'),
  ('V26_NAME',
   'Einspeisung gesamt (kWh)',
   'Einspeisung gesamt (kWh)'),
  ('V26_PARAM',
   'I1/1000',
   'I1/1000'),
  ('V26_VERB',
   'I1 = #15',
   'I1 = #15'),
  ('P1_PARAM',
   '1 = Preise vom Spotpreis-Plugin erreichbar, 0 = nicht; nur mit eingeschalteter Kostenrechnung (Plugin Reiter „Einbindung in Loxone“, Schritt 11)',
   '1 = prices from the spot price plugin reachable, 0 = not; only with the cost calculation switched on (plugin tab “Loxone integration”, step 11)'),
  ('P2_PARAM',
   'Kosten der letzten vollen Stunde in ct, -1 = unbekannt',
   'cost of the last full hour in ct, -1 = unknown'),
  ('P3_PARAM',
   'Kosten heute bisher in ct (Endpreis je Stunde), -1 = unbekannt',
   'cost today so far in ct (final price per hour), -1 = unknown'),
  ('P4_PARAM',
   'Kosten heute bisher in Euro, -1 = unbekannt',
   'cost today so far in euros, -1 = unknown'),
  ('P5_PARAM',
   'heute verbraucht in kWh (nur Stunden mit Preis), -1 = unbekannt',
   'used today in kWh (only hours with a price), -1 = unknown'),
  ('P6_PARAM',
   'gerechnete Stunden heute (0 bis 24)',
   'hours calculated today (0 to 24)'),
  ('P7_PARAM',
   'Stunden ohne belegte Einheit, nicht mitgerechnet',
   'hours without a confirmed unit, not included'),
  ('P8_PARAM',
   'Stunden ohne Preis, nicht mitgerechnet',
   'hours without a price, not included'),
  ('P9_NAME',
   'Durchschnittspreis heute (ct/kWh)',
   'Durchschnittspreis heute (ct/kWh)'),
  ('P9_PARAM',
   'IF(I2>0;I1/I2;-1) – -1 = noch nichts gerechnet',
   'IF(I2>0;I1/I2;-1) – -1 = nothing calculated yet'),
  ('P9_VERB',
   'I1 = #3, I2 = #5',
   'I1 = #3, I2 = #5'),
  ('P10_NAME',
   'Stromkosten heute',
   'Stromkosten heute'),
  ('P10_PARAM',
   'Zeilen: V1 = 0 „Preise nicht erreichbar – Spotpreis-Plugin prüfen; letzter Stand <v2.2> EUR“; V2 = -1 „noch nichts gerechnet – braucht eine volle Stunde“; V7 > 0 „heute <v2.2> EUR für <v3.2> kWh – <v7> Stunden ohne belegte Einheit nicht mitgerechnet“; V8 > 0 „heute <v2.2> EUR für <v3.2> kWh – <v8> Stunden ohne Preis nicht mitgerechnet“; V5 = -1 „heute <v2.2> EUR für <v3.2> kWh, im Schnitt <v4.1> ct/kWh (<v6> Stunden)“; ohne Bedingung „heute <v2.2> EUR für <v3.2> kWh, im Schnitt <v4.1> ct/kWh; letzte volle Stunde <v5.1> ct“',
   'Lines: V1 = 0 “prices not reachable – check the spot price plugin; last value <v2.2> EUR”; V2 = -1 “nothing calculated yet – needs one full hour”; V7 > 0 “today <v2.2> EUR for <v3.2> kWh – <v7> hours without confirmed unit not included”; V8 > 0 “today <v2.2> EUR for <v3.2> kWh – <v8> hours without price not included”; V5 = -1 “today <v2.2> EUR for <v3.2> kWh, on average <v4.1> ct/kWh (<v6> hours)”; without condition “today <v2.2> EUR for <v3.2> kWh, on average <v4.1> ct/kWh; last full hour <v5.1> ct”'),
  ('P10_VERB',
   'V1 = #1, V2 = #4, V3 = #5, V4 = #9, V5 = #2, V6 = #6, V7 = #7, V8 = #8',
   'V1 = #1, V2 = #4, V3 = #5, V4 = #9, V5 = #2, V6 = #6, V7 = #7, V8 = #8'),
  ('P11_NAME',
   'Preise fehlen',
   'Preise fehlen'),
  ('P11_VERB',
   'I = #1',
   'I = #1'),
  ('P12_NAME',
   'Preise fehlen an',
   'Preise fehlen an'),
  ('P12_PARAM',
   '3600 s (die Kostenrechnung läuft alle 5 min; eine Stunde ohne Preise)',
   '3600 s (the cost calculation runs every 5 min; one hour without prices)'),
  ('P12_VERB',
   'Eingang = #11',
   'Input = #11'),
  ('P13_NAME',
   'Stromkosten ohne Preise',
   'Stromkosten ohne Preise'),
  ('P13_PARAM',
   'Text: Die Kostenrechnung des Smartmeter-Plugins bekommt seit einer Stunde keine Preise – Spotpreis-Plugin und Adresse der Preise prüfen (Smartmeter-Plugin, Reiter „Einbindung in Loxone“, Schritt 11)',
   'Text: The cost calculation of the Smartmeter plugin has received no prices for an hour – check the spot price plugin and the price address (Smartmeter plugin, tab “Loxone integration”, step 11)'),
  ('P13_VERB',
   'Eingang = #12',
   'Input = #12'),
  ('P14_PARAM',
   '1 = Fahrplan des Spotpreis-Plugins erreichbar; nur mit eingeschaltetem Fahrplan-Abgleich (Schritt 10)',
   '1 = schedule of the spot price plugin reachable; only with the schedule check switched on (step 10)'),
  ('P15_PARAM',
   '1 = Regel 1 des Fahrplans soll gerade laufen, -1 = Regel steht nicht mehr im Fahrplan; für Regel 2–5 dieselben Bausteine mit _2_ … _5_ (Namen im Plugin, Reiter „Einbindung in Loxone“, Schritt 3)',
   '1 = rule 1 of the schedule should be running now, -1 = the rule is no longer in the schedule; for rules 2–5 the same blocks with _2_ … _5_ (names in the plugin, tab „Integration into Loxone“, step 3)'),
  ('P16_PARAM',
   'Soll von Regel 1: eingetragene Leistung mal Laufzeit, in kWh',
   'target of rule 1: entered power times running time, in kWh'),
  ('P17_PARAM',
   'gemessener Netzbezug seit Beginn von Regel 1, in kWh',
   'measured grid consumption since the start of rule 1, in kWh'),
  ('P18_PARAM',
   'Fehlbetrag in kWh (Soll minus gemessen, nicht unter 0)',
   'shortfall in kWh (target minus measured, not below 0)'),
  ('P19_PARAM',
   'Laufzeit von Regel 1 in s',
   'running time of rule 1 in s'),
  ('P20_PARAM',
   '1 = Urteil möglich (in der Zeit keine Einspeisung und – mit dem Haken „Speicher berücksichtigen“ – kein entladender Speicher)',
   '1 = verdict possible (no feed-in during the time and – with the box „take the battery into account“ – no discharging battery)'),
  ('P21_PARAM',
   '1 = zieht, 0 = zieht nachweislich nicht, -1 = kein Urteil',
   '1 = draws, 0 = demonstrably does not draw, -1 = no verdict'),
  ('P22_NAME',
   'Fahrplan Regel 1',
   'Fahrplan Regel 1'),
  ('P22_PARAM',
   'Zeilen: V1 = 0 „Fahrplan nicht erreichbar – Spotpreis-Plugin prüfen“; V8 = 1 „Regel 1 zieht: <v4.2> von <v3.2> kWh in <v6> s“; V8 = 0 und V7 = 1 „Regel 1 zieht NICHT: <v4.2> von <v3.2> kWh, es fehlen <v5.2> kWh – Gerät prüfen“; V2 = 1 und V7 = 2 „Regel 1 läuft – kein Urteil, weil der Hausspeicher entlädt“; V2 = 1 und V7 = 0 „Regel 1 läuft – kein Urteil, weil gerade eingespeist wird“; V2 = 1 „Regel 1 läuft seit <v6> s – Urteil frühestens nach 600 s“; ohne Bedingung „Regel 1 ruht“',
   'Lines: V1 = 0 „schedule not reachable – check the spot price plugin“; V8 = 1 „rule 1 draws: <v4.2> of <v3.2> kWh in <v6> s“; V8 = 0 and V7 = 1 „rule 1 does NOT draw: <v4.2> of <v3.2> kWh, <v5.2> kWh missing – check the device“; V2 = 1 and V7 = 2 „rule 1 running – no verdict, because the home battery is discharging“; V2 = 1 and V7 = 0 „rule 1 running – no verdict, because power is being fed in“; V2 = 1 „rule 1 running for <v6> s – verdict after 600 s at the earliest“; no condition „rule 1 idle“'),
  ('P22_VERB',
   'V1 = #14, V2 = #15, V3 = #16, V4 = #17, V5 = #18, V6 = #19, V7 = #34, V8 = #21',
   'V1 = #14, V2 = #15, V3 = #16, V4 = #17, V5 = #18, V6 = #19, V7 = #34, V8 = #21'),
  ('P23_NAME',
   'Regel 1 Urteil null',
   'Regel 1 Urteil null'),
  ('P23_PARAM',
   'V2 = 0 (offen lassen)',
   'V2 = 0 (leave open)'),
  ('P23_VERB',
   'V1 = #21',
   'V1 = #21'),
  ('P24_NAME',
   'Regel 1 zieht nicht',
   'Regel 1 zieht nicht'),
  ('P24_PARAM',
   '— (nur mit sicherem Urteil; vor dem ersten Wert stehen beide Eingänge auf 0 und es meldet nichts)',
   '— (only with a reliable verdict; before the first value both inputs are 0 and it reports nothing)'),
  ('P24_VERB',
   'I1 = #23, I2 = #20',
   'I1 = #23, I2 = #20'),
  ('P25_NAME',
   'Fahrplan-Regel 1 zieht nicht',
   'Fahrplan-Regel 1 zieht nicht'),
  ('P25_PARAM',
   'Text: Regel 1 des Spotpreis-Fahrplans lief, der Stromzähler sah aber zu wenig Netzbezug – das Gerät hat nicht gezogen (Smartmeter-Plugin, Reiter „Einbindung in Loxone“, Schritt 10)',
   'Text: Rule 1 of the spot price schedule ran, but the meter saw too little grid consumption – the device did not draw (Smartmeter plugin, tab “Loxone integration”, step 10)'),
  ('P25_VERB',
   'Eingang = #24',
   'Input = #24'),
  ('K_S1',
   'Im Plugin Reiter „%s“ den Lesekopf einrichten, Zählerprofil wählen und speichern. Warten, bis die erste Ablesung da ist (Reiter „%s“ → „%s“ zeigt Werte).',
   'In the plugin tab “%s” set up the reading head, choose the meter profile and save. Wait for the first reading (tab “%s” → “%s” shows values).'),
  ('S_MQTT',
   'Reiter „%s“: „%s“ einschalten, Themenpräfix %s lassen. Steht dort ein Abo (Gateway V1), es unter System → MQTT Gateway → Abonnements eintragen: %s/#.',
   'Tab “%s”: switch on “%s”, keep the topic prefix %s. If a subscription is shown there (gateway V1), enter it under System → MQTT Gateway → Subscriptions: %s/#.'),
  ('K_S3',
   'Reiter „%s“, Schritt 3: für die Eingänge Nr. 1–4, 15, 18, 19 je einen Virtuellen Eingang anlegen (Peripherie → Virtuelle Eingänge), Name genau wie in der Namenstabelle (Knopf „kopieren“), „Als Digitaleingang verwenden“ nicht aktivieren.',
   'Tab “%s”, step 3: for inputs no. 1–4, 15, 18, 19 create one virtual input each (Periphery → Virtual inputs), name exactly as in the name table (button “copy”), do not activate “Use as digital input”.'),
  ('K_S4',
   'Neue Seite „Smartmeter klassisch“. Aus dem Baum unter „Virtuelle Eingänge“ die Eingänge Nr. 1–4, 15, 18, 19 auf die Seite ziehen. Am Eingang 16.7.0 (Nr. 2) in den Eigenschaften „Statistik“ einschalten, wer einen Verlauf will.',
   'New page “Smartmeter klassisch”. From the tree under “Virtual inputs” drag inputs no. 1–4, 15, 18, 19 onto the page. At input 16.7.0 (no. 2) switch on “Statistics” in the properties if you want a history.'),
  ('S_BAUSTEINE',
   'Bausteine über die Baustein-Suche (F5) setzen, Parameter wie in der Liste, von oben nach unten verbinden. Bei den Analogspeichern Nr. 7 und Nr. 16 „Remanenz“ einschalten. Ein ODER hat zwei Eingänge. Status-Zeilen in der angegebenen Reihenfolge, die Zeile ohne Bedingung zuletzt; Status-Eingänge ab V5 erst nach Klick auf das „+“ am Baustein (bei „Strom heute“, Nr. 20).',
   'Place the blocks via the block search (F5), parameters as in the list, connect from top to bottom. Switch on “Retentive” at the analog memories no. 7 and no. 16. An OR has two inputs. Status lines in the order given, the line without condition last; status inputs from V5 on appear only after clicking the “+” on the block (at “Strom heute”, no. 20).'),
  ('K_S6',
   'Zähler Bidirektional (Nr. 24): F5 „Zähler“, Art Bidirektional mit Zählerstand (nicht „Impulszähler“). Leistung an 16.7.0 (Nr. 2), Zählerstand Bezug an 1.8.0 (Nr. 1), Zählerstand Einspeisung an 2.8.0 (Nr. 15). Einheiten <v.3> kW und <v.1> kWh. „In Visualisierung verwenden“ an.',
   'Bidirectional meter (no. 24): F5 “Meter”, type bidirectional with meter reading (not “pulse meter”). Power to 16.7.0 (no. 2), consumption reading to 1.8.0 (no. 1), feed-in reading to 2.8.0 (no. 15). Units <v.3> kW and <v.1> kWh. “Use in visualization” on.'),
  ('S_MELDUNG',
   'Benachrichtigung „Stromzähler prüfen“ anlegen (Peripherie → Mitteilungen → Benachrichtigung) und auf die Seite ziehen.',
   'Create the notification “Stromzähler prüfen” (Periphery → Messages → Notification) and drag it onto the page.'),
  ('K_S8',
   'Speichern, in den Miniserver übertragen. Probe: in der App zeigt „Strom heute“ den Bezug; „Stromzähler Netz“ zeigt ab dem nächsten Tag Tageswerte. Lesekopf abziehen → nach spätestens 30 min kommt „Stromzähler prüfen“.',
   'Save and transfer to the Miniserver. Check: in the app “Strom heute” shows the consumption; “Stromzähler Netz” shows daily values from the next day on. Unplug the reading head → after 30 min at the latest “Stromzähler prüfen” arrives.'),
  ('V_S1',
   'Im Plugin Reiter „%s“ den Haken „%s“ setzen, Kanäle 1.8.0, 2.8.0 (falls Einspeisezählwerk) und 16.7.0 eintragen, speichern.',
   'In the plugin tab “%s” tick “%s”, enter channels 1.8.0, 2.8.0 (if there is a feed-in register) and 16.7.0, save.'),
  ('V_S3',
   'Reiter „%s“, Schritt 3: für die Eingänge Nr. 1–4, 15, 18, 19 je einen Virtuellen Eingang anlegen (Peripherie → Virtuelle Eingänge), Name genau wie in der Namenstabelle (Knopf „kopieren“), „Als Digitaleingang verwenden“ nicht aktivieren.',
   'Tab “%s”, step 3: for inputs no. 1–4, 15, 18, 19 create one virtual input each (Periphery → Virtual inputs), name exactly as in the name table (button “copy”), do not activate “Use as digital input”.'),
  ('V_S4',
   'Neue Seite „Smartmeter vzLogger“, Eingänge Nr. 1–4, 15, 18, 19 aus „Virtuelle Eingänge“ auf die Seite ziehen.',
   'New page “Smartmeter vzLogger”, drag inputs no. 1–4, 15, 18, 19 from “Virtual inputs” onto the page.'),
  ('V_S6',
   'Die drei Formeln Nr. 24–26 (I1/1000) und den Zähler Bidirektional Nr. 27 setzen (F5 „Zähler“, Art Bidirektional mit Zählerstand); Leistung an Nr. 24, Zählerstand Bezug an Nr. 25, Zählerstand Einspeisung an Nr. 26. Einheiten <v.3> kW und <v.1> kWh, „In Visualisierung verwenden“ an.',
   'Place the three formulas no. 24–26 (I1/1000) and the bidirectional meter no. 27 (F5 “Meter”, type bidirectional with meter reading); power to no. 24, consumption reading to no. 25, feed-in reading to no. 26. Units <v.3> kW and <v.1> kWh, “Use in visualization” on.'),
  ('V_S8',
   'Speichern, übertragen. Probe wie beim klassischen Leseweg; vzLogger meldet jede Minute.',
   'Save and transfer. Check as for the classic reading path; vzLogger reports every minute.'),
  ('P_S1',
   'Nur mit einem Spotpreis-Plugin (aWATTar, Octopus oder Tibber). Eine der beiden Zählerseiten muss schon laufen – die Kosten kommen aus dem gemessenen Lastgang.',
   'Only with a spot price plugin (aWATTar, Octopus or Tibber). One of the two meter pages must already be running – the costs come from the measured load profile.'),
  ('P_S2',
   'Im Plugin Reiter „%s“, Schritt 10: „%s“, Adresse des Spotpreis-Plugins eintragen (z. B. http://127.0.0.1/plugins/spotpreis/spot.php?json=1), speichern. Schritt 11: „%s“ (Adresse leer lassen = dieselbe), speichern.',
   'In the plugin tab “%s”, step 10: “%s”, enter the address of the spot price plugin (e.g. http://127.0.0.1/plugins/spotpreis/spot.php?json=1), save. Step 11: “%s” (leave the address empty = the same), save.'),
  ('P_S3',
   'Reiter „%s“, Schritt 3: die 16 Eingänge Nr. 1–8 und 14–21 je als Virtuellen Eingang anlegen, Namen genau wie in der Namenstabelle (Kostenrechnung und Fahrplan-Abgleich), „Als Digitaleingang verwenden“ nicht aktivieren.',
   'Tab “%s”, step 3: create the 16 inputs no. 1–8 and 14–21 each as a virtual input, names exactly as in the name table (cost calculation and schedule check), do not activate “Use as digital input”.'),
  ('P_S4',
   'Neue Seite „Smartmeter Kosten und Fahrplan“, die 16 Eingänge aus „Virtuelle Eingänge“ auf die Seite ziehen.',
   'New page “Smartmeter Kosten und Fahrplan”, drag the 16 inputs from “Virtual inputs” onto the page.'),
  ('P_S5',
   'Formel, zwei Status, NICHT, Einschaltverzögerung, Gleich und UND setzen (F5); Status-Eingänge ab V5 erst nach Klick auf das „+“ am Baustein. Zwei Benachrichtigungen anlegen (Peripherie → Mitteilungen → Benachrichtigung, Texte wie in der Liste). Von oben nach unten verbinden.',
   'Place formula, two status blocks, NOT, on-delay, equal and AND (F5); status inputs from V5 on appear only after clicking the “+” on the block. Create two notifications (Periphery → Messages → Notification, texts as in the list). Connect from top to bottom.'),
  ('P_S6',
   'Speichern, übertragen. Probe: nach spätestens 5 Minuten steht in „Stromkosten heute“ ein Text, nach der ersten vollen Stunde ein Eurobetrag. Im Plugin (Schritt 11) stehen dieselben Zahlen.',
   'Save and transfer. Check: after 5 minutes at the latest “Stromkosten heute” shows a text, after the first full hour an amount in euros. The plugin (step 11) shows the same figures.'),
  ('H_FEHLT',
   'Fehlt ein Eingang (z. B. 2.8.0) in der Namenstabelle (Schritt 3), liefert Ihr Zähler den Wert nicht: die Zeilen, die ihn brauchen, weglassen. Liefert er mehr (Tarife 1.8.1/1.8.2, Phasen, Spannungen), sind das weitere Eingänge zum Anzeigen – Statistik am Eingang einschalten.',
   'If an input (e.g. 2.8.0) is missing in the name table (step 3), your meter does not deliver that value: leave out the lines that need it. If it delivers more (tariffs 1.8.1/1.8.2, phases, voltages), these are further inputs for display – switch on statistics at the input.'),
  ('K_H_UEBERSCHUSS',
   'Überschuss (Nr. 22, Ausgang Q): an den eigenen Verbraucher legen (Heizstab, Freigabe einer Steckdose). Der Verbraucher darf höchstens 1,2 kW ziehen (Ein-Schwelle 1,5 minus Aus-Schwelle 0,3), sonst schaltet er sich selbst wieder ab und pendelt. Größere Verbraucher: Ein-Schwelle höher setzen.',
   'Surplus (no. 22, output Q): connect it to your own consumer (heating element, release of a socket). The consumer may draw at most 1.2 kW (on threshold 1.5 minus off threshold 0.3), otherwise it switches itself off again and oscillates. Larger consumers: set the on threshold higher.'),
  ('K_H_TAKT',
   'Der klassische Leser misst so oft wie im Plugin eingestellt („Abfragetakt“). Das Lebenszeichen (Nr. 3 und 4) kommt seit Plugin 2.8.13 jede Minute, unabhängig vom Takt – Tmc 300 s in Nr. 11 und 300 s in Nr. 25 gelten für jeden Takt. Ob WERTE ankommen, sagt status_ok (Nr. 3): 1, solange jeder Lesekopf jünger ist als dreimal der Takt.',
   'The classic reader measures as often as set in the plugin (“polling interval”). Since plugin 2.8.13 the sign of life (no. 3 and 4) arrives every minute, independent of the interval – Tmc 300 s in no. 11 and 300 s in no. 25 apply to every interval. Whether VALUES arrive is told by status_ok (no. 3): 1 as long as every reading head is younger than three times the interval.'),
  ('H_EINWEG',
   'Nur einen Leseweg je Zähler betreiben (klassisch ODER vzLogger), nie beide für denselben Zähler – beide melden über dieselben Lebenszeichen-Eingänge, und zwei Zähler-Bausteine zählten denselben Strom doppelt.',
   'Run only one reading path per meter (classic OR vzLogger), never both for the same meter – both report via the same sign-of-life inputs, and two meter blocks would count the same electricity twice.'),
  ('V_H_FORMELN',
   'vzLogger liefert Wh und W, der Zähler-Baustein rechnet in kWh und kW – deshalb die drei Formeln Nr. 24–26. Ohne sie zeigt die App das Tausendfache.',
   'vzLogger delivers Wh and W, the meter block calculates in kWh and kW – hence the three formulas no. 24–26. Without them the app shows a thousand times the value.'),
  ('V_H_LEISTUNG',
   'Die Leistungen 1.99.0/2.99.0 (Nr. 18, 19) sind hier keine Mittelwerte, sondern die Wirkleistung aufgeteilt nach Bezug und Einspeisung.',
   'The powers 1.99.0/2.99.0 (no. 18, 19) are not averages here, but the active power split into consumption and feed-in.'),
  ('V_H_UEBERSCHUSS',
   'Überschuss (Nr. 22, Ausgang Q): an den eigenen Verbraucher legen. Er darf höchstens 1200 W ziehen (Ein-Schwelle 1500 minus Aus-Schwelle 300), sonst pendelt er. Größere Verbraucher: Ein-Schwelle höher setzen.',
   'Surplus (no. 22, output Q): connect it to your own consumer. It may draw at most 1200 W (on threshold 1500 minus off threshold 300), otherwise it oscillates. Larger consumers: set the on threshold higher.'),
  ('P_H_AUS',
   'Ohne eingeschaltete Kostenrechnung bleibt %s auf 0 – dann meldet Nr. 13 nach einer Stunde. Wer keine Kosten will, baut diese Seite nicht.',
   'Without the cost calculation switched on, %s stays at 0 – then no. 13 reports after one hour. If you do not want costs, do not build this page.'),
  ('P_H_HEUTE',
   'Gerechnet wird der heutige Tag; um Mitternacht beginnt er bei -1 („noch nichts gerechnet“). Den Vortag samt 23–24 Uhr schließt das Plugin nach 0 Uhr ab (Nr. 26–30, spätestens um 01:00).',
   'The current day is calculated; at midnight it starts at -1 (“nothing calculated yet”). The plugin closes the previous day including 23–24 h after midnight (no. 26–30, at the latest at 01:00).'),
  ('P_H_REGELN',
   'Mehrere Regeln im Fahrplan: Nr. 15–25, 33 und 34 kopieren und in den Namen „_1_“ durch „_2_“ … „_5_“ ersetzen (%s …). Die Namenstabelle in Schritt 3 nennt die Namen für jede Regel, die der Fahrplan führt (bis 5) – je als Virtuellen Eingang mit genau diesem Namen anlegen (Peripherie → Virtuelle Eingänge → Virtueller Eingang). %s (Nr. 14) gibt es nur einmal.',
   'Several rules in the schedule: copy no. 15–25, 33 and 34 and replace “_1_” by “_2_” … “_5_” in the names (%s …). The name table in step 3 lists the names for every rule the schedule carries (up to 5) – create each as a virtual input with exactly this name (Periphery → Virtual inputs → Virtual input). %s (no. 14) exists only once.'),
  ('P_H_URTEIL',
   '„zieht nicht“ ist eine sichere Aussage: Das Plugin urteilt nur ohne gleichzeitige Einspeisung (und mit dem Haken „Speicher berücksichtigen“ nur ohne entladenden Hausspeicher) und erst nach 10 Minuten Laufzeit; unter 80 Prozent des Solls heißt „zieht nicht“. Häufige Ursache: Gerät ausgeschaltet, Sicherung, falsche Leistung in der Regel eingetragen.',
   '“does not draw” is a reliable statement: the plugin only judges without simultaneous feed-in (and with the box „take the battery into account“ only without a discharging home battery) and only after 10 minutes of running time; below 80 percent of the target means “does not draw”. Common causes: device switched off, fuse, wrong power entered in the rule.'),
  # Welle Bild 14 (2.8.10): Analogwertvalidierung Nr. 11 - Eingang En nicht negieren
  # (Config legt ihn negiert an; Hinweis auf beiden Lesewegen).
  ('H_EN',
   '<b>Zu #11:</b> Config legt den Eingang En negiert an (Haken bei ‚En‘ im Eigenschaftsfenster unter Parameter). Diesen Haken entfernen, sonst kommt die Konstante 1 als 0 an und die Ausfallmeldung löst nie aus.',
   '<b>On #11:</b> Config creates input En inverted (tick at ‘En’ in the properties under Parameters). Remove this tick, otherwise constant 1 arrives as 0 and the failure message never triggers.'),
  # Gruppe 1 (2.8.11): Nr. 11 Takttabelle (klassisch), Nr. 12 Eingang I1 je Leseweg,
  # Einschaltverzoegerung Nr. 25 (klassisch) / Nr. 28 (vzLogger) gegen die Fehlmeldung
  # nach einem Neustart des Miniservers (Entwurf E3).
  ('B11_PARAM_K',
   'Tmc 300 s, Min 0, Max 999; Haken bei „En“ entfernen (ab Plugin 2.8.13 kommt das Lebenszeichen jede Minute – vorher dreimal der Abfragetakt)',
   'Tmc 300 s, Min 0, Max 999; remove the tick at „En“ (from plugin 2.8.13 the sign of life arrives every minute – before, three times the polling interval)'),
  ('B12_VERB_K',
   'I1 = #25, I2 = Ausgang E von #11',
   'I1 = #25, I2 = output E of #11'),
  ('B12_VERB_V',
   'I1 = #28, I2 = Ausgang E von #11',
   'I1 = #28, I2 = output E of #11'),
  ('LF_NAME',
   'Lesekopf-Fehler hält an',
   'Lesekopf-Fehler hält an'),
  ('LF_PARAM_K',
   '300 s (überbrückt den Neustart des Miniservers, bis status_ok wieder kommt; status_ok kommt ab Plugin 2.8.13 jede Minute)',
   '300 s (bridges the restart of the Miniserver until status_ok arrives again; from plugin 2.8.13 status_ok arrives every minute)'),
  ('LF_PARAM_V',
   '300 s (der vzLogger-Weg meldet jede Minute; überbrückt den Neustart des Miniservers, bis status_ok wieder kommt)',
   '300 s (the vzLogger path reports every minute; bridges the restart of the Miniserver until status_ok arrives again)'),
  ('LF_VERB',
   'Eingang = #10',
   'Input = #10'),
  # Gruppe 35 (2.8.13): Baustein-Listen wortgleich Entwurf G35 Abschnitt 9.
  ('B4_PARAM_K',
   'Lebenszeichen 0–999, zählt jede Minute eins weiter (ab Plugin 2.8.13 unabhängig vom Abfragetakt; im MQTT-Gateway V2 „Noncached“ anhaken; nie retained)',
   'Sign of life 0–999, counts up by one every minute (from plugin 2.8.13 independent of the polling interval; tick „Noncached“ in MQTT gateway V2; never retained)'),
  ('B4_PARAM_V',
   'Lebenszeichen 0–999, zählt jede Minute eins weiter (im MQTT-Gateway V2 „Noncached“ anhaken; nie retained)',
   'Sign of life 0–999, counts up by one every minute (tick „Noncached“ in MQTT gateway V2; never retained)'),
  ('T_VQ_BEFEHL',
   'Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT)',
   'Virtual output command (template „LoxBerry MQTT-Gateway“, MQTT)'),
  ('SIG_NAME',
   'Signal - Stromzähler gestört',
   'Signal - Stromzähler gestört'),
  ('SIG_PARAM_K',
   'Befehl bei EIN: publish signalbot/befehl/senden Stromzaehler meldet sich nicht – Smartmeter-Plugin, Reiter Test (nie retain); wirkt nur mit dem Haken „Befehle über MQTT annehmen“ im SignalBot (Reiter MQTT); derselbe Text binnen 60 s geht nur einmal hinaus',
   'Command on ON: publish signalbot/befehl/senden Stromzaehler meldet sich nicht – Smartmeter-Plugin, Reiter Test (never retain); only works with the box „accept commands via MQTT“ in SignalBot (MQTT tab); the same text within 60 s goes out only once'),
  ('SIG_PARAM_V',
   'wie „Smartmeter klassisch“ Nr. 26',
   'as „Smartmeter klassisch“ no. 26'),
  ('SIG_VERB',
   'Eingang = #12',
   'Input = #12'),
  ('P26_PARAM',
   'Kosten des ganzen gestrigen Tages in Euro (samt 23–24 Uhr), -1 = nicht gerechnet; kommt alle 5 Minuten, nie retained',
   'Cost of the whole previous day in euros (including 23–24 h), -1 = not calculated; arrives every 5 minutes, never retained'),
  ('P27_PARAM',
   'gestern verbraucht in kWh (Stunden mit Preis), -1 = nicht gerechnet',
   'consumed yesterday in kWh (hours with price), -1 = not calculated'),
  ('P28_PARAM',
   'gerechnete Stunden gestern (24; 23 bzw. 25 an den Tagen der Zeitumstellung), 0 = nichts gerechnet',
   'hours calculated yesterday (24; 23 or 25 on the days of the clock change), 0 = nothing calculated'),
  ('P29_NAME',
   'Durchschnittspreis gestern (ct/kWh)',
   'Durchschnittspreis gestern (ct/kWh)'),
  ('P29_PARAM',
   'IF(I2>0;I1*100/I2;-1) – -1 = nichts gerechnet',
   'IF(I2>0;I1*100/I2;-1) – -1 = nothing calculated'),
  ('P29_VERB',
   'I1 = #26, I2 = #27',
   'I1 = #26, I2 = #27'),
  ('P30_NAME',
   'Stromkosten gestern',
   'Stromkosten gestern'),
  ('P30_PARAM',
   'Zeilen: V1 = -1 „gestern nicht gerechnet – Preise oder Verbrauch fehlten (Smartmeter-Plugin, Reiter Test)“; V3 < 23 „gestern <v1.2> EUR für <v2.2> kWh – nur <v3> Stunden gerechnet“; ohne Bedingung „gestern <v1.2> EUR für <v2.2> kWh, im Schnitt <v4.1> ct/kWh“',
   'Lines: V1 = -1 „yesterday not calculated – prices or consumption missing (Smartmeter plugin, Test tab)“; V3 < 23 „yesterday <v1.2> EUR for <v2.2> kWh – only <v3> hours calculated“; no condition „yesterday <v1.2> EUR for <v2.2> kWh, on average <v4.1> ct/kWh“'),
  ('P30_VERB',
   'V1 = #26, V2 = #27, V3 = #28, V4 = #29',
   'V1 = #26, V2 = #27, V3 = #28, V4 = #29'),
  ('P31_NAME',
   'Signal - Fahrplan-Regel zieht nicht',
   'Signal - Fahrplan-Regel zieht nicht'),
  ('P31_PARAM',
   'Befehl bei EIN: publish signalbot/befehl/senden Fahrplan-Regel 1 zieht nicht – Geraet pruefen (Smartmeter-Plugin, Reiter Einbindung, Schritt 10) (nie retain); Haken wie „Smartmeter klassisch“ Nr. 26',
   'Command on ON: publish signalbot/befehl/senden Fahrplan-Regel 1 zieht nicht – Geraet pruefen (Smartmeter-Plugin, Reiter Einbindung, Schritt 10) (never retain); box as in „Smartmeter klassisch“ no. 26'),
  ('P31_VERB',
   'Eingang = #24',
   'Input = #24'),
  ('P32_NAME',
   'Sprachsteuerung: Ansage Regel zieht nicht',
   'Sprachsteuerung: Ansage Regel zieht nicht'),
  ('P32_PARAM',
   'Befehl bei EIN: publish sprachsteuerung/befehl/sprechen Die Fahrplan-Regel eins zieht keinen Strom (nie retain; Text ohne Umlaute; Ruhezeit und Stilllegen der Sprachsteuerung gelten); nur, wer statt oder neben Signal eine Ansage will – sonst weglassen',
   'Command on ON: publish sprachsteuerung/befehl/sprechen Die Fahrplan-Regel eins zieht keinen Strom (never retain; text without umlauts; quiet time and muting of the voice control apply); only for those who want an announcement instead of or besides Signal – otherwise leave out'),
  ('P32_VERB',
   'Eingang = #24',
   'Input = #24'),
  ('P33_PARAM',
   '1 = der Hausspeicher entlud während Regel 1 (über haus/speicher, z. B. Marstek Venus E), 0 = nein, -1 = keine Aussage',
   '1 = the home battery discharged during rule 1 (via haus/speicher, e.g. Marstek Venus E), 0 = no, -1 = no statement'),
  ('P34_NAME',
   'Urteil Regel 1 mit Speicher',
   'Urteil Regel 1 mit Speicher'),
  ('P34_PARAM',
   'IF(I2>0;2;I1) – 1 = Urteil möglich, 0 = eingespeist, 2 = der Hausspeicher entlud (fasst Nr. 20 und 33 für den Status Nr. 22 zusammen; ein Status hat nur acht Eingänge)',
   'IF(I2>0;2;I1) – 1 = verdict possible, 0 = fed in, 2 = the home battery discharged (combines no. 20 and 33 for the status no. 22; a status has only eight inputs)'),
  ('P34_VERB',
   'I1 = #20, I2 = #33',
   'I1 = #20, I2 = #33'),
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
  ('BEZUG_RECHNERISCH',
   'Bezugsleistung, rechnerisch',
   'Consumption power, computed'),
  ('BEZUGSLEISTUNG', "Bezugsleistung", "Consumption power"),
  ('EINSP_GESAMT', "Zählerstand Einspeisung, gesamt", "Meter reading, delivery, total"),
  ('EINSP_TARIF', "Zählerstand Einspeisung, Tarifzählwerk", "Delivery reading, tariff register"),
  ('EINSP_RECHNERISCH',
   'Einspeiseleistung, rechnerisch',
   'Delivery power, computed'),
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
  # Der Feldname sagt "Delivery/Consumption", die Beschriftung sagte
  # "Pruefsumme" - beides kann nicht stimmen, und "quelle": "doku" weist
  # den Eintrag ohnehin als ungemessen aus. Bis ein Zaehler antwortet,
  # wird die Kennzahl genannt und nichts behauptet.
  ('CFUENF', "OBIS C.5.0 (Bedeutung nicht gemessen)",
   "OBIS C.5.0 (meaning not measured)"),
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
  ('X3_WARNUNG',
   'Ein gespeicherter Wert würde das Zurückspielen dieser Sicherung nicht bestehen: %s. Die Sicherung wird trotzdem geliefert und trägt dazu eine Zeile _warnung; den Wert vorher in seinem Reiter berichtigen.',
   'A saved value would not pass when this backup is restored: %s. The backup is delivered anyway and carries a _warnung line; correct the value in its tab first.'),
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
  ('TOKEN_WERT',
   'TOKEN: kein gültiges Zugriffstoken – erlaubt sind 8 bis 128 Zeichen aus Buchstaben, Ziffern, - und _. Der Wert wird hier nicht angezeigt.',
   'TOKEN: not a valid access token – 8 to 128 characters from letters, digits, - and _ are allowed. The value is not shown here.'),
  ('TOKEN_BEHALTEN',
   'Die Sicherung trägt kein Zugriffstoken. Das hier geltende bleibt bestehen – wer den Endpunkt ohne Token betreiben will, entfernt es im Reiter Einbindung in Loxone.',
   'The backup carries no access token. The token in force here stays – to run the endpoint without a token, remove it in the Loxone integration tab.'),
  # Gruppe 35 (2.8.13): Positivlisten der Kopffelder (T4-2 + E6), Spaetliste.
  ('KOPF_FELDER',
   'Lesekopf %s: Feld(er) %s unzulässig (Positivliste) – die ganze Sicherung wurde abgewiesen, es wurde nichts geändert.',
   'Reading head %s: field(s) %s not permitted (allow-list) – the whole backup was rejected, nothing was changed.'),
  ('SPAET',
   'In der Sicherung fehlen %s (ältere Fassung) – hier gelten die bisherigen Werte weiter.',
   'The backup lacks %s (older version) – the current values here remain in force.'),
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
  ('ZEITGRENZE',  # (2) Weg, Dauer
   "%s: nach %s s abgebrochen — die Zeitgrenze war erreicht. Das ist KEINE "
   "Aussage über das Protokoll; der Weg war nur zu langsam.",
   "%s: aborted after %s s — the time limit was reached. That is NOT a "
   "statement about the protocol; this path was merely too slow."),
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
  ('K_ROH', "vzLogger-Rohwerte", "vzLogger raw values"),
  ('ROH_STUMM',  # (1) Rueckgabewert
   "Der Aufruf hat nichts ausgegeben (Rückgabewert %s). Läuft vzlogger, "
   "und stimmt der HTTP-Port im Reiter vzLogger?",
   "The call produced no output (return code %s). Is vzlogger running, and "
   "is the HTTP port in the vzLogger tab correct?"),
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
  ('Z_REITER', "Reiter", "Tabs"),
  ('Z_SMACTIVE', "Offener Reiter", "Open tab"),
  ('Z_FORM', "Formulare", "Forms"),
  ('Z_GATEWAY', "MQTT-Gateway", "MQTT gateway"),
  ('Z_ENDPUNKT', "Endpunkt", "Endpoint"),
  ('Z_MARKE', "Aktualisierung", "Update"),
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
  ('DIENST_VZ_MEHRFACH',  # (1) PIDs
   "Es laufen MEHRERE vzlogger mit unserer Konfiguration (PID %s). Sie "
   "greifen alle auf dieselbe serielle Schnittstelle und denselben "
   "HTTP-Port zu. Einmal „vzlogger neu starten“ im Reiter vzLogger räumt "
   "das auf.",
   "SEVERAL vzlogger processes are running with our configuration (PID %s). "
   "They all access the same serial port and the same HTTP port. One click "
   "on “restart vzlogger” in the vzLogger tab clears that up."),
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
  # --- Upgrade-Marke ---
  ('MARKE_KEINE',
   "Es läuft keine Aktualisierung dieses Plugins.",
   "No update of this plugin is running."),
  ('MARKE_LAEUFT',  # (1) Sekunden
   "Eine Aktualisierung dieses Plugins läuft seit %s Sekunden. Solange sie "
   "gilt, startet weder der Systemstart noch der Minutentakt noch der Knopf "
   "im Reiter vzLogger einen zweiten vzlogger.",
   "An update of this plugin has been running for %s seconds. While it is "
   "valid, neither the system start nor the one-minute cron job nor the "
   "button in the vzLogger tab starts a second vzlogger."),
  ('MARKE_ALT',  # (1) Sekunden
   "Es liegt eine Marke aus einer abgebrochenen Aktualisierung (%s Sekunden "
   "alt). Sie gilt nicht mehr und hält nichts auf; die Datei "
   "data/plugins/<Ordner>.upgrade_laeuft darf weg.",
   "A marker from an aborted update is lying around (%s seconds old). It is "
   "no longer valid and holds nothing back; the file "
   "data/plugins/<folder>.upgrade_laeuft may be removed."),
  ('MARKE_UNLESBAR',
   "Es liegt eine Marke, in der keine Unixzeit steht. Sie gilt nicht und "
   "hält nichts auf; die Datei data/plugins/<Ordner>.upgrade_laeuft darf weg.",
   "A marker is lying around that does not contain a Unix timestamp. It is "
   "not valid and holds nothing back; the file "
   "data/plugins/<folder>.upgrade_laeuft may be removed."),
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
  # Diese drei Texte sprachen bis 2.4.2 von einer Anführungszeichen-
  # Prüfung. Gemessen wird aber etwas anderes: ob in einem WERT der
  # Loxone-Suchtext steckt (Rückwärtsschrägstrich + i). Ein Text, der eine
  # Prüfung beschreibt, die nicht stattfindet, ist schlimmer als keine
  # Zeile. Und die Zahl war die der gelesenen DATEIEN, nicht der Werte.
  ('INI_MUSTER',  # (2) Anzahl, Fundstellen
   "%s Werte enthalten den Loxone-Suchtext (Rückwärtsschrägstrich + i): %s. "
   "Loxone deutet ihn als Befehlserkennung; in einem Anzeigetext hat er "
   "nichts zu suchen.",
   "%s values contain the Loxone command pattern (backslash + i): %s. Loxone "
   "reads it as a command recognition; it has no place in a display text."),
  ('INI_OK',  # (2) Zeilen, Dateien
   "%s Wertzeilen in %s Sprachdateien geprüft, kein Loxone-Suchtext darin.",
   "%s value lines in %s language files checked, no Loxone command pattern."),
  # --- XML-Vorlagen ---
  # Gemessen wird der COMMENT eines Befehls, nicht sein Titel. Der Text
  # sagte bis zum 26.08.2026 das Falsche - und schickte damit jeden, der
  # ihn liest, an die falsche Stelle.
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
  ('Z_VZJSON',
   'Ist vzlogger.json heil?',
   'Is vzlogger.json intact?'),
  ('VZJSON_OK',
   'gültiges JSON, %d Schlüssel.',
   'valid JSON, %d keys.'),
  ('VZJSON_FEHLT',
   'Es gibt keine vzlogger.json – es gelten die Werkseinstellungen. Das ist ein Zustand, kein Fehler.',
   'There is no vzlogger.json – the factory defaults apply. That is a state, not an error.'),
  ('VZJSON_KAPUTT',
   '%s ist beschädigt (kein gültiges JSON). Der Reiter vzLogger zeigt die Werkseinstellungen; Speichern ist gesperrt, bis die Datei berichtigt oder gelöscht ist.',
   '%s is damaged (no valid JSON). The vzLogger tab shows the factory defaults; saving is blocked until the file has been repaired or deleted.'),
  # Gruppe 1 (2.8.11): Pruefzeile Hakenliste Gateway V2 gegen die drei Vorlagen.
  ('Z_HAKEN',
   'Hakenliste Gateway V2',
   'Tick list gateway V2'),
  ('HAKEN_OK',
   '%s Datenpunkte, gleich den gesendeten Themen (Reiter MQTT), Zahl/Text und Noncached richtig.',
   '%s data points, equal to the published topics (MQTT tab), number/text and Noncached correct.'),
  ('HAKEN_KEINE',
   'Kein Leseweg, keine Kostenrechnung und kein Fahrplan-Abgleich eingeschaltet – nichts zu vergleichen.',
   'No reading path, no cost calculation and no schedule check switched on – nothing to compare.'),
  ('HAKEN_FEHLT',
   '%s gesendete(s) Thema/Themen fehlen in der Hakenliste, z. B. %s.',
   '%s published topic(s) missing from the tick list, e.g. %s.'),
  ('HAKEN_ZUVIEL',
   '%s Datenpunkt(e) der Hakenliste werden nicht gesendet, z. B. %s.',
   '%s data point(s) of the tick list are not published, e.g. %s.'),
  ('HAKEN_MERKER',
   'Merker „Noncached“ falsch an %s.',
   'Flag “Noncached” wrong at %s.'),
  ('HAKEN_ART',
   'Zahl/Text weicht vom gesendeten Thema ab: %s.',
   'Number/text differs from the published topic: %s.'),
  # Gruppe 35 (2.8.13): Selbsttest: Noncached V2, Leseköpfe, Profile, USB, Dienstdatei, haus/speicher.
  ('Z_NONCACHED',
   'Noncached im MQTT-Gateway V2',
   'Noncached in MQTT gateway V2'),
  ('NC_OK',
   '%d Datenpunkt(e) mit Haken und „Noncached“.',
   '%d data point(s) ticked and „Noncached“.'),
  ('NC_FEHLT',
   'Bei %d Datenpunkt(en) fehlt der Haken oder „Noncached“: %s – System → MQTT Gateway → Abonnements.',
   '%d data point(s) lack the tick or „Noncached“: %s – System → MQTT Gateway → Subscriptions.'),
  ('NC_KEIN_V2',
   'Das MQTT-Gateway läuft nicht als V2 – hier ist nichts zu prüfen.',
   'The MQTT gateway is not running as V2 – nothing to check here.'),
  ('NC_KEINE_DATEI',
   'Die Abonnements des MQTT-Gateways V2 (subscriptions.json) sind nicht lesbar.',
   'The subscriptions of MQTT gateway V2 (subscriptions.json) are not readable.'),
  ('Z_KOPF',
   'Leseköpfe gegen die Positivlisten',
   'Reading heads against the allow-lists'),
  ('KOPF_KEINER',
   'Kein Lesekopf eingerichtet.',
   'No reading head configured.'),
  ('KOPF_OK',
   '%d Lesekopf/Leseköpfe: alle Felder zulässig.',
   '%d reading head(s): all fields permitted.'),
  ('KOPF_FELD',
   'Kopf %s: %s',
   'head %s: %s'),
  ('KOPF_BEANSTANDET',
   'Unzulässig: %s – in smartmeter.cfg berichtigen oder im Reiter Smartmeter (klassisch) neu speichern; sm_logger.pl prüft CRC zusätzlich selbst.',
   'Not permitted: %s – correct it in smartmeter.cfg or save again in the Smartmeter (classic) tab; sm_logger.pl also checks CRC itself.'),
  ('Z_PROFILE',
   'Zählerprofile gegen sm_logger.pl',
   'Meter profiles against sm_logger.pl'),
  ('PROFILE_OK',
   '%d Profile, jedes mit einem Zweig in sm_logger.pl.',
   '%d profiles, each with a branch in sm_logger.pl.'),
  ('PROFILE_ABWEICHUNG',
   'Nur in der Oberfläche: %s; nur in sm_logger.pl: %s.',
   'Only in the interface: %s; only in sm_logger.pl: %s.'),
  ('Z_USB',
   'Geräte unter /dev/serial/smartmeter',
   'Devices under /dev/serial/smartmeter'),
  ('USB_KEINE',
   'Kein Gerät unter /dev/serial/smartmeter.',
   'No device under /dev/serial/smartmeter.'),
  ('USB_OK',
   '%s – die udev-Regel ist die engere (0660, Gruppe loxberry).',
   '%s – the udev rule is the narrower one (0660, group loxberry).'),
  ('USB_FREMD',
   '%s – %s sieht nicht nach einem Lesekopf aus: die udev-Regel nimmt jeden USB-Seriell-Adapter auf. Bitte prüfen.',
   '%s – %s does not look like a reading head: the udev rule picks up every USB serial adapter. Please check.'),
  ('Z_DIENSTDATEI',
   'Dienstdatei vorhanden',
   'Daemon file present'),
  ('DIENSTDATEI_OK',
   'system/daemons/plugins/%s liegt.',
   'system/daemons/plugins/%s is present.'),
  ('DIENSTDATEI_FEHLT',
   '%s fehlt – beim Systemstart entstehen weder udev-Regel noch vzlogger-Start. Häufigste Ursache: ein Plugin „smartmeter“ (das Original) wurde aktualisiert oder deinstalliert. Abhilfe: dieselbe Fassung dieses Plugins drüberinstallieren.',
   '%s is missing – at system start neither the udev rule nor the vzlogger start is created. Most common cause: a plugin „smartmeter“ (the original) was updated or uninstalled. Remedy: install the same version of this plugin over it.'),
  ('DIENSTDATEI_NICHT_MESSBAR',
   'Nicht messbar (kein LoxBerry-Ordner system/daemons/plugins).',
   'Not measurable (no LoxBerry folder system/daemons/plugins).'),
  ('Z_SPEICHER',
   'haus/speicher (Fahrplan-Abgleich)',
   'haus/speicher (schedule check)'),
  ('SPEICHER_AUS',
   'Haken „Speicher berücksichtigen“ aus – Urteil ohne Speicher.',
   'Box „take the battery into account“ off – verdict without the battery.'),
  ('Z_HAUS_ENERGIE',
   'haus/energie (Werte für andere Plugins)',
   'haus/energie (values for other plugins)'),
  ('Z_HAUS_FREI',
   'haus/energie/frei_w (Sonnenstrom übrig, mit Hausakku)',
   'haus/energie/frei_w (solar power left over, with home battery)'),
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
   'Der klassische Leser ist abgeschaltet, seine Cron-Verknüpfung ist entfernt.',
   'The classic reader is switched off, its cron link has been removed.'),
  ('NUR_EINTRAG',
   'Die Einstellungen sind gespeichert — nur der Cron-Eintrag liess sich '
   'nicht setzen. Der klassische Leser wird deshalb NICHT aufgerufen:',
   'The settings have been saved — only the cron entry could not be set. '
   'The classic reader will therefore NOT be called:'),
  ('UNBEKANNT',  # (1) der eingestellte Wert
   'In der Konfiguration steht ein Abfragetakt, den das Plugin nicht kennt: %s. '
   'Im Feld darüber einen gültigen Takt wählen und speichern.',
   'The configuration holds a polling interval the plugin does not know: %s. '
   'Please pick a valid interval in the field above and save.'),
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
  ('AB_SPEICHERN',
   'Speichert die Einstellungen des Fahrplan-Abgleichs',
   'Saves the settings of the schedule cross-check'),
  ('KO_SPEICHERN',
   'Speichert die Einstellungen der Kostenrechnung',
   'Saves the settings of the cost calculation'),
  ('TOKEN', "Ändert die Adresse, unter der der Miniserver liest",
   "Changes the address the Miniserver reads from"),
  # Gruppe 35 (2.8.13): eine gesammelte Legende je Reiter (Regeln/04).
  ('VZ_PHASEN',
   'Hilfe beim Ausfüllen — trägt Zeilen ins Formular ein, gespeichert wird erst mit Speichern',
   'Filling aid — adds lines to the form, nothing is stored until Save'),
  ('EP_SPEICHERN',
   'Schaltet Endpunkt oder Lastgang ein oder aus',
   'Switches the endpoint or the load profile on or off'),
  ('KO_CSV',
   'Ansehen — lädt die Tageskosten als Datei herunter',
   'View — downloads the daily cost as a file'),
  ('HE_SPEICHERN',
   'Schaltet die Werte für andere Plugins (haus/energie) ein oder aus',
   'Switches the values for other plugins (haus/energie) on or off'),
  ('HE_VERGESSEN',
   'Vergisst den Hausakku für frei_w (nur nach Abbau des Akkus)',
   'Forgets the home battery for frei_w (only after removing it)'),
 ]),
 # Kopf wie alle Hausplugins (Entscheidung Nr. 43, 2.8.6): Statusuebersicht
 # ueber den Reitern und gruener Kasten oben im Reiter vzLogger
 # (WAS_IST_DAS roh ausgegeben, sm_t ohne sm_e).
 ('KOPF', [
  ('EIGENSCHAFT',
   'Eigenschaft',
   'Property'),
  ('WERT',
   'Wert',
   'Value'),
  ('VZ',
   'Leseweg vzlogger',
   'Reading path vzlogger'),
  ('LEGACY',
   'Klassischer Leser',
   'Classic reader'),
  ('LAEUFT',
   'läuft, PID %s',
   'running, PID %s'),
  ('LAEUFT_NICHT',
   'eingeschaltet, läuft aber gerade nicht',
   'switched on, but not running right now'),
  ('AUS',
   'abgeschaltet',
   'switched off'),
  ('KOEPFE',
   'Erkannte Leseköpfe',
   'Detected reading heads'),
  ('LASTGANG',
   'Lastgang heute',
   'Load profile today'),
  ('LASTGANG_WERT',
   '%s von 24 Stunden belegt',
   '%s of 24 hours covered'),
  ('WAS_IST_DAS',
   '<b>Stromzähler mit optischem IR-Lesekopf in Loxone – mit zwei Lesewegen nebeneinander.</b> Das Plugin liest den Zähler wahlweise mit vzlogger oder mit dem klassischen Perl-Leser; man nimmt, was beim eigenen Zähler funktioniert. Die Werte gehen per MQTT (Standardweg) oder UDP an den Miniserver, der sie über das MQTT-Gateway liest; dazu kommen ein HTTP-Endpunkt mit Zustandszeile und ein stündlicher Lastgang für die Spotpreis-Plugins.',
   '<b>Electricity meters with an optical IR reading head in Loxone – with two reading paths side by side.</b> The plugin reads the meter either with vzlogger or with the classic Perl reader; use whichever works with your meter. The values go to the Miniserver over MQTT (the default) or UDP, read through the MQTT gateway; in addition there is an HTTP endpoint with a status line and an hourly load profile for the spot price plugins.'),
 ]),
 ('ANSAGEPLUGIN', [
  ('H',
   'Sprachansagen',
   'Announcements'),
  ('K_SPEICHERN',
   'Sprachansagen speichern',
   'Save announcements'),
  ('K_TEST',
   'Testansage an alle Ziele',
   'Test announcement to all targets'),
  ('M_OK',
   'Sprachansagen gespeichert.',
   'Announcements saved.'),
  ('M_FEHL',
   'Die Sprachansagen ließen sich nicht speichern.',
   'The announcements could not be saved.'),
  ('M_TEST_OK',
   'Testansage gesendet.',
   'Test announcement sent.'),
  ('M_TEST_FEHL',
   'Testansage nicht gesendet:',
   'Test announcement not sent:'),
  ('L_ZAEHLER',
   'Zähler antwortet seit 15 Minuten nicht, und wieder da',
   'Meter has not answered for 15 minutes, and back again'),
  ('SATZ_ZAEHLER',
   'Der Stromzähler antwortet nicht mehr.',
   'The electricity meter is not responding.'),
  ('SATZ_WIEDER',
   'Der Stromzähler antwortet wieder.',
   'The electricity meter is responding again.'),
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
  'Der Reiter <i>vzLogger</i> prüft acht Dinge einzeln und zeigt Haken, Ausrufezeichen oder Kreuz: Betriebsart, Programm, Prozess, Konfiguration, Lesekopf, Belegung der Schnittstelle, HTTP-Schnittstelle, Messwerte. <b>Die erste rote Zeile von oben ist die Ursache</b>, alles darunter meist die Folge. Im Reiter <i>Test</i> steht zusätzlich ein Selbsttest, der das Plugin selbst prüft — Katalog, Themen, Reiter, Formulare, Gateway, Haken im MQTT-Gateway V2, Leseköpfe, Dienstdatei. Ein <b>Strich</b> dort heißt „hier ist nichts zu messen“ und ausdrücklich nicht „in Ordnung“.',
  'The <i>vzLogger</i> tab checks eight things one by one and shows a tick, an exclamation mark or a cross: operating mode, program, process, configuration, reading head, port usage, HTTP interface, readings. <b>The first red line from the top is the cause</b>, everything below it is usually the consequence. The <i>Test</i> tab additionally holds a self-test checking the plugin itself — catalogue, topics, tabs, forms, gateway, ticks in MQTT gateway V2, reading heads, daemon file. A <b>dash</b> there means „nothing to measure here“ and expressly not „all good“.'),
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
 ('K69',
  '<code>OK</code> in der Zustandszeile des Endpunkts geht auf 0, sobald eine Messung älter ist als das <b>Dreifache des Abfragetakts</b> (vzLogger-Weg: 180 s) – bei 5 Minuten also nach 15 Minuten. Bei mehreren Leseköpfen gilt das für <b>jeden</b> eingeschalteten Kopf einzeln; hinten in der Zeile stehen dazu <code>KOPF1_OK</code>, <code>KOPF1_ALTER</code> usw. Schweigt der Zähler, gehen seine alten Werte nicht erneut hinaus: die Datendatei bleibt stehen, und ihr Alter wächst.',
  '<code>OK</code> in the status line of the endpoint drops to 0 as soon as a reading is older than <b>three times the polling cycle</b> (vzLogger route: 180 s) – with 5 minutes, after 15 minutes. With several reading heads this applies to <b>each</b> head that is switched on; the end of the line carries <code>KOPF1_OK</code>, <code>KOPF1_ALTER</code> and so on. If the meter goes silent, its old values are not sent again: the data file stays, and its age grows.'),
 ('K70',
  'Dazu geht jede Minute das Lebenszeichen hinaus, flüchtig und seit 2.8.13 unabhängig vom Abfragetakt: <code>&lt;Präfix&gt;/status/ok</code> (1, solange jeder eingeschaltete Lesekopf frisch ist), <code>status/ts</code> und <code>status/zaehler</code>. Die Zustände <code>Breaker_State_Electricity_96.3.10</code>, <code>Tarif_Indicator_Electricity_96.14.0</code>, <code>Message_Code_96.13.1</code> und <code>abgleich/&lt;n&gt;/aktiv</code> gehen <b>retained</b> hinaus; in Loxone gilt ein Zustand nur zusammen mit <code>status/ok</code>. Liefert der Zähler einen Zustand nicht mehr, setzt das Plugin ihn direkt am Broker auf -1 und liest das zurück; nach einem Präfixwechsel, beim Abschalten von MQTT und bei der Deinstallation räumt es sie ab.',
  'In addition, the sign of life is published every minute, non-retained and since 2.8.13 independent of the polling interval: <code>&lt;prefix&gt;/status/ok</code> (1 as long as every reading head that is switched on is fresh), <code>status/ts</code> and <code>status/zaehler</code>. The states <code>Breaker_State_Electricity_96.3.10</code>, <code>Tarif_Indicator_Electricity_96.14.0</code>, <code>Message_Code_96.13.1</code> and <code>abgleich/&lt;n&gt;/aktiv</code> are published <b>retained</b>; in Loxone a state is only valid together with <code>status/ok</code>. If the meter no longer delivers a state, the plugin sets it to -1 directly at the broker and reads it back; after a prefix change, when MQTT is switched off and on uninstall, the plugin clears them.'),
 # Gruppe 35 (2.8.13): MQTT-Gateway V2, -1-Ausnahme, Tagesabschluss, haus/speicher, Meldungen, Schalter.
 ('K71',
  'MQTT-Gateway V2',
  'MQTT gateway V2'),
 ('K72',
  'Die Hausform ist das <b>MQTT-Gateway V2</b>: je Wert ein Virtueller Eingang mit dem Namen aus der Namenstabelle (Reiter <i>Einbindung in Loxone</i>, Schritt 3) und ein Haken je Datenpunkt im Gateway (System → MQTT Gateway → Abonnements). <code>status/ok</code>, <code>status/zaehler</code>, <code>kosten/quelle_ok</code>, <code>abgleich/quelle_ok</code> und <code>abgleich/&lt;n&gt;/ok</code> brauchen zusätzlich <b>Noncached</b> – sonst verschluckt das Gateway V2 einen gleichen Wert, und nach einem Neustart des Miniservers meldet die Ausfallerkennung zu Unrecht. Der Healthcheck und der Selbsttest sagen es, wenn ein Haken fehlt. Das Abo <code>&lt;Präfix&gt;/#</code> ist nur noch der Rückfall für Anlagen auf Gateway V1.',
  'The house form is the <b>MQTT gateway V2</b>: one virtual input per value with the name from the name table (tab <i>Integration into Loxone</i>, step 3) and one tick per data point in the gateway (System → MQTT Gateway → Subscriptions). <code>status/ok</code>, <code>status/zaehler</code>, <code>kosten/quelle_ok</code>, <code>abgleich/quelle_ok</code> and <code>abgleich/&lt;n&gt;/ok</code> additionally need <b>Noncached</b> – otherwise gateway V2 swallows an identical value, and after a restart of the Miniserver the failure detection reports wrongly. The health check and the self-test say so when a tick is missing. The subscription <code>&lt;prefix&gt;/#</code> remains only as the fallback for installations on gateway V1.'),
 ('K73',
  '<b>Keine -1 für Zählerstände und Leistungen.</b> Schweigt der Zähler, bleiben Zählerstände und Leistungen stehen; den Ausfall sagt <code>status/ok</code>. Das ist eine bewusste Abweichung von der Hausform: ein -1 an einem Zählerstand ließe den Baustein „Zähler Bidirektional“ und den Tagesstand springen, und bei 16.7.0 ist -1 ein echter Wert (Einspeisung negativ).',
  '<b>No -1 for meter readings and power values.</b> If the meter falls silent, readings and power values stay where they are; the failure is told by <code>status/ok</code>. This is a deliberate deviation from the house form: a -1 on a meter reading would make the „Meter bidirectional“ block and the daily reading jump, and for 16.7.0 -1 is a real value (feed-in negative).'),
 ('K74',
  'Die Kosten von gestern',
  'Yesterday’s cost'),
 ('K75',
  'Die Kostenrechnung merkt sich die Stundenpreise des laufenden Tages selbst. Der erste Lauf nach 0 Uhr schließt den Vortag ab – samt der Stunde 23–24 Uhr, sobald sie im Lastgang steht, spätestens um 01:00 (dann ohne sie, die Zeile sagt es). Je Tag entsteht genau eine Zeile in <code>kosten_historie.csv</code>; die letzten 14 Tage stehen im Reiter <i>Einbindung in Loxone</i>, Schritt 11, zum Herunterladen. Über MQTT gehen <code>kosten/gestern_eur</code>, <code>gestern_kwh</code>, <code>gestern_ct</code> und <code>gestern_stunden</code> – nie retained. Fehlen die Preise des Vortags (Plugin aus, Update zur falschen Zeit), steht -1 da, kein erfundener Preis. Am Tag der Zeitumstellung mit 25 Stunden tragen beide 2-Uhr-Stunden denselben Preis.',
  'The cost calculation notes the hourly prices of the current day itself. The first run after midnight closes the previous day – including the hour 23–24 once it is in the load profile, at the latest at 01:00 (then without it, the line says so). Each day gets exactly one line in <code>kosten_historie.csv</code>; the last 14 days are shown in the tab <i>Integration into Loxone</i>, step 11, for download. Over MQTT <code>kosten/gestern_eur</code>, <code>gestern_kwh</code>, <code>gestern_ct</code> and <code>gestern_stunden</code> are published – never retained. If the previous day’s prices are missing (plugin off, update at the wrong time), -1 is shown, not an invented price. On the 25-hour day of the clock change both 2 o’clock hours carry the same price.'),
 ('K76',
  'Hausspeicher im Fahrplan-Abgleich',
  'Home battery in the schedule check'),
 ('K77',
  'Mit dem Haken „Speicher berücksichtigen“ (Schritt 10, ab Werk aus) liest das Plugin das Haus-Thema <code>haus/speicher</code> (Anbieter: Marstek Venus E ab 1.1.27). Entlädt der Speicher, während eine Regel läuft, gibt es für diese Regel kein Urteil – er drückt den Netzbezug wie eine Einspeisung. Schweigt die Quelle oder meldet der Speicher keine Richtung, urteilt das Plugin wie bisher. Umgekehrt kann die Netzleistung des Zählers (16.7.0) einem Speicher als Sollwertgeber dienen – im Musterprojekt auf der Seite „Marstek Venus E Steuerung“ (Überschuss = Batterie − Netz).',
  'With the box „take the battery into account“ (step 10, off by default) the plugin reads the house topic <code>haus/speicher</code> (provider: Marstek Venus E from 1.1.27). If the battery discharges while a rule runs, there is no verdict for that rule – it lowers grid consumption like feed-in. If the source is silent or the battery reports no direction, the plugin judges as before. Conversely, the grid power of the meter (16.7.0) can serve a battery as set-point source – in the sample project on the page „Marstek Venus E Steuerung“ (surplus = battery − grid).'),
 ('K78',
  'Meldungen über Signal oder Ansage',
  'Notifications via Signal or announcement'),
 ('K79',
  'Das Plugin selbst sendet keine Nachrichten. „Stromzähler gestört“ und „Fahrplan-Regel zieht nicht“ stehen als Bausteine im LoxBerry-Plugins Musterprojekt (Seiten „Smartmeter klassisch“ Nr. 26, „Smartmeter vzLogger“ Nr. 29, „Smartmeter Kosten und Fahrplan“ Nr. 31 und – für wer will – die Ansage Nr. 32) und gehen über die Befehlsbrücken von SignalBot und Sprachsteuerung.',
  'The plugin itself sends no messages. „Stromzähler gestört“ and „Fahrplan-Regel zieht nicht“ are blocks in the LoxBerry-Plugins sample project (pages „Smartmeter klassisch“ no. 26, „Smartmeter vzLogger“ no. 29, „Smartmeter Kosten und Fahrplan“ no. 31 and – for those who want it – the announcement no. 32) and go through the command bridges of SignalBot and voice control.'),
 ('K80',
  '<b>Endpunkt und Lastgang ab Werk aus.</b> Seit 2.8.13 antworten die unangemeldeten Adressen für den Miniserver (<code>index.php</code>) und für die Spotpreis-Plugins (<code>lastgang.php</code>) nur mit eingeschaltetem Schalter (Reiter <i>Einbindung in Loxone</i>, Schritt 8 und 9). Eine bestehende Anlage behält beide beim Update.',
  '<b>Endpoint and load profile off by default.</b> Since 2.8.13 the unauthenticated addresses for the Miniserver (<code>index.php</code>) and for the spot price plugins (<code>lastgang.php</code>) only answer with the switch on (tab <i>Integration into Loxone</i>, steps 8 and 9). An existing installation keeps both on update.'),
 ('K81',
  'Werte für andere Plugins (haus/energie)',
  'Values for other plugins (haus/energie)'),
 ('K82',
  'Mit dem Haken „Werte für andere Plugins bereitstellen“ im Reiter <i>MQTT</i> (ab Werk aus, nur <b>ein</b> Anbieter je Haus) sendet das Plugin jede Minute unter <code>haus/energie/</code>: <code>netz_w</code> (+ Bezug, − Einspeisung), <code>bezug_w</code>, <code>ueberschuss_w</code> (je ganze W, nie negativ), <code>bezug_kwh</code> und <code>einspeisung_kwh</code> (Zählerstände 1.8.0/2.8.0), <code>stand</code> (Zeitpunkt der Messung) sowie <code>ok</code> und <code>zaehler</code> als Lebenszeichen. Gerechnet wird aus 1.7.0 und 2.7.0, sonst aus 16.7.0; nur Werte, die Ihr Zähler wirklich liefert und deren Einheit bekannt ist. Alles flüchtig: schweigt der Zähler, geht nur <code>ok</code> = 0 hinaus, nie ein alter Wert. Die PV-Erzeugung kennt ein Netzzähler nicht – sie kommt hier nie. Andere Plugins (zum Beispiel Midea2Lox, EVCC, Bewässerung, Dashboard) können das künftig lesen; mit mehreren Leseköpfen wählen Sie den Zähler am Hausanschluss.',
  'With the box „Provide values for other plugins“ in the tab <i>MQTT</i> (off by default, only <b>one</b> provider per house) the plugin sends every minute under <code>haus/energie/</code>: <code>netz_w</code> (+ consumption, − feed-in), <code>bezug_w</code>, <code>ueberschuss_w</code> (whole W each, never negative), <code>bezug_kwh</code> and <code>einspeisung_kwh</code> (meter readings 1.8.0/2.8.0), <code>stand</code> (time of the measurement) and <code>ok</code> and <code>zaehler</code> as heartbeat. Calculated from 1.7.0 and 2.7.0, otherwise from 16.7.0; only values your meter really delivers and whose unit is known. All non-retained: if the meter is silent only <code>ok</code> = 0 goes out, never an old value. A grid meter does not know the PV production – it never appears here. Other plugins (for example Midea2Lox, EVCC, irrigation, dashboard) can read this in future; with several reading heads choose the meter at the grid connection.'),
 ('K83',
  'Sonnenstrom übrig – frei_w (seit 2.8.19)',
  'Solar power left over – frei_w (since 2.8.19)'),
 ('K84',
  'Mit eingeschaltetem haus/energie sendet das Plugin zusätzlich <code>haus/energie/frei_w</code> (ganze W, + = Sonnenstrom übrig, − = das Haus deckt sich aus Netz oder Akku) und <code>frei_quelle</code> (<code>netz</code> oder <code>netz+speicher</code>). Gerechnet wird frei_w = −netz_w + Akku, Akku = + Ladeleistung bzw. − Entladeleistung aus <code>haus/speicher</code>. Beispiel: Akku lädt 3.000 W, Einspeisung 0 → frei_w = 3000; Akku entlädt 1.500 W, Bezug 0 → frei_w = −1500. Ohne je gesehenen Hausakku gilt frei_w = −netz_w. War ein Akku da und schweigt er jetzt, wird frei_w nicht gesendet – die Abnehmer (Midea2Lox ab 4.5.23) nehmen dann Einspeisung und Bezug. Wallbox und andere Großverbraucher werden nicht herausgerechnet. Der Reiter <i>Test</i> zeigt in der Zeile „haus/energie/frei_w“, womit gerechnet wird oder warum frei_w fehlt.',
  'With haus/energie switched on, the plugin also sends <code>haus/energie/frei_w</code> (whole W, + = solar power left over, − = the house is supplied from grid or battery) and <code>frei_quelle</code> (<code>netz</code> or <code>netz+speicher</code>). frei_w = −netz_w + battery, battery = + charging power or − discharging power from <code>haus/speicher</code>. Example: battery charges 3,000 W, feed-in 0 → frei_w = 3000; battery discharges 1,500 W, consumption 0 → frei_w = −1500. If no home battery was ever seen, frei_w = −netz_w. If a battery was present and is silent now, frei_w is not sent – consumers (Midea2Lox from 4.5.23) then use feed-in and consumption. Wallbox and other large consumers are not subtracted. The <i>Test</i> tab shows in the row “haus/energie/frei_w” what is used or why frei_w is missing.'),
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


def ansage_abschnitt(sprache):
    """Der Abschnitt [ANSAGE] der gemeinsamen Sprachausgabe - EINE Quelle:
    Werkzeuge/gemeinsam_pruefen.py baut ihn aus Werkzeuge/gemeinsam/sprachausgabe_texte.json
    (Form SCHLUESSEL="Wert", ohne Leerzeichen). Fehlt die Quelle, wird nichts geschrieben."""
    w = Path(__file__).resolve().parent
    if (w / "gemeinsam_pruefen.py").is_file() and (w / "gemeinsam" / "sprachausgabe_texte.json").is_file():
        sys.path.insert(0, str(w))
        import gemeinsam_pruefen
        return gemeinsam_pruefen.ini_abschnitt(sprache)
    raise SystemExit("Werkzeuge/gemeinsam_pruefen.py nicht gefunden - es wurde nichts geschrieben.")


# Drift-Abgleich 06.11.2026 (Smartmeter 2.8.20): der Abschnitt [ANSAGE] steht in der .ini
# unmittelbar vor diesem Abschnitt der Tabelle TEXTE.
ANSAGE_VOR = "ANSAGEPLUGIN"


def bauen(index):
    zeilen = []
    for abschnitt, paare in TEXTE:
        if abschnitt == ANSAGE_VOR:
            zeilen.append("")
            zeilen += ansage_abschnitt("de" if index == 1 else "en").rstrip("\n").split("\n")
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

    # Werkzeug-S2 (02.10.2026): erst ALLES bauen und pruefen, dann schreiben.
    # Bis dahin standen die language_*.ini schon auf der Platte, wenn die
    # Pruefung der Hilfe gegen help.html weiter unten abbrach (Fund 01.10.
    # abends, Smartmeter-Bau). Jetzt sammelt der Lauf die vier Inhalte in
    # 'schreiben' und legt sie erst ab, wenn keine Pruefung mehr abbrechen kann.
    schreiben = []
    for datei, kopf, index in (("language_de.ini", KOPF_DE, 1),
                               ("language_en.ini", KOPF_EN, 2)):
        text = kopf + "\n".join(bauen(index)) + "\n"
        # Beide Sprachdateien waren im Bestand CRLF; seit der Hausregel
        # vom 13.09.2026 schreibt der Erzeuger LF.
        schreiben.append((datei, text.encode("utf-8")))

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
        schreiben.append((datei, (kopf + "\n".join(zeilen) + "\n").encode("utf-8")))

    # Die Sprachwache prueft je Datei erst unmittelbar vor dem Schreiben; ein
    # Abbruch bei der dritten Datei liesse die ersten beiden geschrieben. Darum
    # hier einmal ueber alle vier vorab (eine Meldung "werden neu gefasst"
    # erscheint dadurch zweimal). Ab hier bricht keine Pruefung mehr ab.
    for datei, inhalt in schreiben:
        sprachwache.pruefen(str(lang / datei), inhalt.decode("utf-8"))
    for datei, inhalt in schreiben:
        (lang / datei).write_bytes(inhalt)

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
    raise SystemExit(main())
