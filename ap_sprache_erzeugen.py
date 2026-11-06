# -*- coding: utf-8 -*-
"""Erzeugt language_de.ini und language_en.ini aus EINER Quelle.

Warum ein Erzeuger: bis 1.1.6 standen die beiden Dateien nebeneinander und
mussten von Hand gleichgehalten werden. Hier kann kein Schlüssel nur in
einer Sprache stehen - er hat immer beide Werte oder gar keinen.

Regeln, die hier eingehalten und am Ende gemessen werden:
  * Jeder Wert in doppelten Anfuehrungszeichen, genau zwei je Zeile.
  * KEIN doppeltes Anfuehrungszeichen im Wert - HTML-Attribute einfach
    quotieren (class='sm-mono'), Anfuehrung typografisch.
  * Beschriftungen, die durch ap_e() laufen, tragen echte UTF-8-Umlaute und
    KEINE Entitaeten - sonst steht die Entitaet woertlich am Bildschirm.
  * Zeilenenden LF.

    ACHTUNG, das war bis 1.2.0 CRLF. Umgestellt am 20.08.2026, weil die
    .gitattributes des Repositories (* text=auto) die Dateien beim
    Erzeugen des GitHub-Archivs ohnehin auf LF normalisiert hat: der
    Anwender bekam seit v1.0.0 LF, waehrend der Arbeitsordner CRLF
    fuehrte. Seit 1.2.1 stimmen beide ueberein. Einzelheiten in
    REGELN_4, 'Das ausgelieferte Archiv ist nicht das, das man packt'.
  * [THEMA] ist eine BESCHRIFTUNG, kein Satz: der Wert wandert als Comment
    in die Loxone-Vorlage und wird dort zum Anzeigenamen der Kachel.

STAND (vb_bild_ap, 09.10.2026, Welle Bild 3 / Musterprojekt, Entscheidung 45): neu
LOXONE.BILD_ALT, LOXONE.BILD_UNTERSCHRIFT, LOXONE.MUSTERPROJEKT (Bild der Bausteine aus dem
LoxBerry-Plugins Musterprojekt unter der Baustein-Liste); sonst unveraendert.

STAND (vb_bild_ap12, 14.10.2026, Welle Bild 12 VOLL / Musterprojekt, APC-UPS NG 1.2.20): [LOXONE]
neu gefasst SCHRITT6, BAUSTEINE_VORTEXT, VORLAGE_ZAHL (Textthemen legt das Gateway nicht selbst an),
BILD_ALT, BILD_UNTERSCHRIFT (Seitenname als %s); gestrichen die 28 Schluessel der alten Liste
(B_VE ... ZU_6); neu 164 Schluessel der zwei Listen (Typen, Eingaenge, Namen, Parameter, Schritte,
Hinweise) und VORLAGE_FUSS, VORLAGE_HINWEIS_MQTT, VORLAGE_HINWEIS_XML (Comment und HintText der
Loxone-Vorlagen uebersetzt, Titel fest).

STAND (vb_bild_ap12b, 14.10.2026, APC-UPS NG 1.2.21, Praefix mit Schraegstrich): [LOXONE] neu
PRAEFIX_SCHRAEG (Hinweis im Reiter Einbindung in Loxone: in Loxone steht fuer den Schraegstrich
des Praefixes ein Unterstrich); sonst unveraendert.

STAND (vb_bild_ap14, 16.10.2026, Welle Bild 14, APC-UPS NG 1.2.22): [LOXONE] neu S1_H9 (Hinweis:
Config legt den Eingang En der Analogwertvalidierung #19 negiert an - Haken entfernen); neu gefasst
S1_H4 ('bekommt an En die Konstante 1' statt 'nur mit der Konstante 1 an En' - unbeschaltet steht
En auf EIN); sonst unveraendert.

STAND (vb_g16_ap, 25.10.2026, Gruppe 16 / MQTT, APC-UPS NG 1.2.23): Block _g16_anwenden() hinter T und
hinter THEMA_LANG - gestrichen 6 Schluessel (Vorlage des MQTT-Wegs, E6: LOXONE.KNOPF_MQTT, LOXONE.VORLAGE_HINWEIS_MQTT, LOXONE.VORLAGE_ZAHL, LOXONE.E_GATEWAY, LEGENDE.TECHNIK_DATEI, TEST.V_TEXTTHEMEN), gesetzt/neu 151 (Bausteinliste
nach Entwurf Abschnitt 9 wortgleich zu baustein_listen.txt, Namenstabelle, V2-Haken, Endpunkt, Sprachausgabe,
Haus-Thema, Pruefzeilen); [THEMA] +3 (status/*); neu die Abschnitte [ANSAGE] (aus
Werkzeuge/gemeinsam_pruefen.py ini_abschnitt(), Quelle gemeinsam/sprachausgabe_texte.json) und [ANSAGE_TEXT].

STAND (Drift-Abgleich, 06.11.2026): angeglichen an APC-UPS NG 1.2.29, 10 Schluessel neu
(ALLGEMEIN.KACHEL_MQTT_HILFE, TEST.F_V2_HAKEN und acht TEST.V2_*, am Ende von _G16_SETZEN),
3 Werte geaendert (EINST.ANSAGE_AUDIOSERVER, EINST.ANSAGE_AUSFALL, EINST.ANSAGE_ANLAESSE_HILFE),
0 entfernt.
"""
import io, os, re, sys

ZIEL = sys.argv[1]

# ---------------------------------------------------------------------------
# (schluessel, deutsch, englisch)
# ---------------------------------------------------------------------------
T = [
 # ---------------- REITER ----------------
 ('REITER.EINSTELLUNGEN', 'Einstellungen', 'Settings'),
 ('REITER.LOXONE', 'Einbindung in Loxone', 'Loxone integration'),
 ('REITER.TEST', 'Test', 'Test'),
 ('REITER.LOG', 'Logdateien', 'Log files'),

 # ---------------- LEGENDE ----------------
 ('LEGENDE.LESEN', 'Ansehen — fragt nur ab, verändert nichts',
                   'View — reads only, changes nothing'),
 ('LEGENDE.TECHNIK', 'Technische Auskunft — für die Fehlersuche',
                     'Technical details — for troubleshooting'),
 ('LEGENDE.TECHNIK_DATEI', 'Technische Auskunft — erzeugt eine Datei zum Herunterladen',
                           'Technical details — creates a file to download'),
 ('LEGENDE.AKTION', 'Löst etwas aus — sendet, speichert oder verändert',
                    'Triggers something — sends, saves or changes'),

 # ---------------- ALLGEMEIN ----------------
 ('ALLGEMEIN.JA', 'ja', 'yes'),
 ('ALLGEMEIN.NEIN', 'nein', 'no'),
 ('ALLGEMEIN.EIN', 'ein', 'on'),
 ('ALLGEMEIN.AUS', 'aus', 'off'),
 ('ALLGEMEIN.UNBEKANNT', 'nicht feststellbar', 'cannot be determined'),
 ('ALLGEMEIN.SPEICHERN', 'Speichern', 'Save'),
 ('ALLGEMEIN.DIENST', 'Dienst', 'Service'),
 ('ALLGEMEIN.PLUGIN', 'Plugin', 'Plugin'),
 ('ALLGEMEIN.USV', 'USV', 'UPS'),
 ('ALLGEMEIN.LAEUFT', 'läuft', 'running'),
 ('ALLGEMEIN.LAEUFT_NICHT', 'läuft nicht', 'not running'),
 ('ALLGEMEIN.STAND_SEKUNDEN', 'Stand vor … Sekunden', 'measured … seconds ago'),
 ('ALLGEMEIN.KEINE_VERBINDUNG', 'Die USV antwortet nicht.',
                                'The UPS is not answering.'),
 ('ALLGEMEIN.KEINE_VERBINDUNG_LANG',
  'apcupsd meldet <b>COMMLOST</b>. Es liefert trotzdem einen vollständig '
  'aussehenden Datensatz — die Zahlen darin stammen aus der letzten '
  'funktionierenden Abfrage oder stehen auf null. Sie sagen nichts über den '
  'jetzigen Zustand der USV. Zuerst das USB-Kabel und den Dienst apcupsd prüfen.',
  'apcupsd reports <b>COMMLOST</b>. It still returns a complete looking data '
  'set — the numbers in it come from the last working query or are zero. They '
  'say nothing about the current state of the UPS. Check the USB cable and the '
  'apcupsd service first.'),

 # ---------------- TEXT (Meldungen) ----------------
 ('TEXT.GESPEICHERT', 'Gespeichert.', 'Saved.'),
 ('TEXT.HINWEIS', 'Hinweis:', 'Note:'),
 ('TEXT.SCHREIBFEHLER', 'Die Konfiguration ließ sich nicht schreiben:',
                        'The configuration could not be written:'),
 ('TEXT.DIENST_NEU_GESTARTET', 'Der Dienst wurde neu gestartet.',
                               'The service has been restarted.'),
 ('TEXT.DIENST_LAEUFT_NICHT',
  'Der Dienst läuft nicht. Die Ursache steht im Reiter Logdateien.',
  'The service is not running. The reason is in the Log files tab.'),
 ('TEXT.DIENST_ANGEHALTEN',
  'Der Dienst bleibt angehalten (Knopf „Dienst anhalten“ im Reiter Test). Die '
  'Einstellungen gelten, sobald „Dienst neu starten“ ihn wieder startet.',
  'The service stays stopped (button “Stop service” in the Test tab). The '
  'settings take effect once “Restart service” starts it again.'),
 # U6 (1.2.14): bis 1.2.13 standen diese Saetze fest deutsch in ap_dienst().
 ('TEXT.D_BEENDET_EINER', 'Dienst %d beendet.', 'Service %d stopped.'),
 ('TEXT.D_BEENDET_MEHRERE', 'Dienste %s beendet.', 'Services %s stopped.'),
 ('TEXT.D_LIEF_KEINER', 'Es lief kein Dienst.', 'No service was running.'),
 ('TEXT.D_PID_ENTFERNT', 'Eine liegengebliebene PID-Datei wurde entfernt.',
                         'A leftover PID file was removed.'),
 ('TEXT.D_NICHT_GEFUNDEN', 'Dienst nicht gefunden: %s', 'Service not found: %s'),
 ('TEXT.D_LAEUFT_BEREITS', 'Der Dienst läuft bereits (PID %d) — kein zweiter Start.',
                           'The service is already running (PID %d) — no second start.'),
 ('TEXT.HOST_UNGUELTIG',
  'Der USV-Host „%s“ passt nicht auf Rechnername oder Adresse. Erlaubt sind '
  'Buchstaben, Ziffern, Punkt, Bindestrich und Unterstrich, notfalls mit :Port.',
  'The UPS host “%s” is neither a host name nor an address. Allowed are '
  'letters, digits, dot, hyphen and underscore, optionally with :port.'),
 ('TEXT.ALTES_FORMAT',
  'In der Konfiguration stehen noch Schlüssel der Originalfassung. Sie werden '
  'beim nächsten Speichern entfernt; Ihre Einstellungen bleiben erhalten.',
  'The configuration still contains keys from the original version. They will '
  'be removed on the next save; your settings are kept.'),
 ('TEXT.FORMULAR_ABGEWIESEN',
  'Das Formular wurde abgewiesen, weil sein Merkmal nicht zur Konfiguration '
  'passt. Das schützt davor, dass eine fremde Seite in Ihrem angemeldeten '
  'Browser etwas auslöst. Bitte die Seite neu laden und noch einmal absenden.',
  'The form was rejected because its marker does not match the configuration. '
  'This protects against another web page triggering something in your '
  'logged-in browser. Please reload the page and submit again.'),
 ('TEXT.THEMENDATEI_FEHLT',
  'Die Themenliste %s fehlt oder ist unlesbar. Ohne sie weiß weder der Dienst '
  'noch diese Oberfläche, welche Themen es gibt.',
  'The topic list %s is missing or unreadable. Without it neither the service '
  'nor this page knows which topics exist.'),

 # ---------------- EINSTELLUNGEN ----------------
 # Kopf wie alle Hausplugins (Entscheidung Nr. 43, 1.2.17): gruener Kasten
 # oben im Reiter Einstellungen, roh ausgegeben (ap_t ohne ap_e).
 ('EINST.WAS_IST_DAS',
  '<b>Wächter für eine APC-USV am LoxBerry.</b> Das Plugin liest die USV '
  'über apcupsd aus – Zustand, Akkuladung, Restlaufzeit, Last und eine '
  'gestufte Alarmstufe – und meldet die Werte per MQTT an den Loxone '
  'Miniserver. Bei Stromausfall und Netzrückkehr kommt zusätzlich eine '
  'LoxBerry-Benachrichtigung, auf Wunsch auch eine E-Mail. An der USV '
  'schaltet das Plugin nichts; ob und wann der LoxBerry bei leerem Akku '
  'herunterfährt, entscheidet apcupsd.',
  '<b>Watchdog for an APC UPS on the LoxBerry.</b> The plugin reads the UPS '
  'through apcupsd – state, battery charge, runtime left, load and a graded '
  'alarm level – and reports the values over MQTT to the Loxone Miniserver. '
  'On a power failure and when mains power returns there is also a LoxBerry '
  'notification, and an email on request. The plugin does not switch '
  'anything on the UPS; whether and when the LoxBerry shuts down on an '
  'empty battery is decided by apcupsd.'),
 ('EINST.AKTUELLER_ZUSTAND', 'Aktueller Zustand', 'Current state'),
 ('EINST.NETZAUSFALL', 'Netzausfall', 'power failure'),
 ('EINST.NOCH_KEINE_WERTE',
  'Es liegen noch keine Werte vor. Der Reiter <b>Test</b> zeigt mit '
  '<i>Jetzt abfragen</i>, ob die USV antwortet.',
  'No values yet. The <b>Test</b> tab shows with <i>Query now</i> whether the '
  'UPS answers.'),
 ('EINST.BETRIEB', 'Betrieb', 'Operation'),
 ('EINST.PLUGIN_EINGESCHALTET', 'Plugin eingeschaltet', 'Plugin switched on'),
 ('EINST.PLUGIN_EINGESCHALTET_HILFE',
  'Solange das nicht angehakt ist, läuft der Dienst zwar, fragt aber nichts ab '
  'und sendet nichts.',
  'While this is unchecked the service runs but queries nothing and sends nothing.'),
 ('EINST.INTERVALL', 'Abfragen alle … Sekunden', 'Query every … seconds'),
 ('EINST.AKTUALISIERUNG', 'Alles neu melden alle … Sekunden',
                          'Republish everything every … seconds'),
 ('EINST.AKTUALISIERUNG_HILFE',
  'Sonst geht nur hinaus, was sich geändert hat.',
  'Otherwise only changed values are sent.'),
 ('EINST.HOST', 'USV auf einem anderen Rechner', 'UPS on another machine'),
 ('EINST.HOST_HILFE',
  'Leer lassen für die örtliche USV. Sonst Rechnername oder Adresse des '
  'Rechners, auf dem apcupsd läuft — notfalls mit <span class=\'sm-mono\'>:Port</span>. '
  'Der Wert gilt seit 1.2.0 auch für den alten XML-Weg.',
  'Leave empty for the local UPS. Otherwise the host name or address of the '
  'machine running apcupsd — optionally with <span class=\'sm-mono\'>:port</span>. '
  'Since 1.2.0 this also applies to the old XML endpoint.'),
 ('EINST.VORWARNUNG', 'Vorwarnung vor der Abschaltung',
                      'Advance warning before shutdown'),
 ('EINST.VORWARNUNG_HILFE',
  'Ob und wann der LoxBerry heruntergefahren wird, entscheidet apcupsd — nicht '
  'dieses Plugin. Das Plugin liest die Schwellen aber aus und meldet über '
  '<span class=\'sm-mono\'>alarm_level</span> vorher, wie eng es wird: '
  '0 Netzbetrieb, 1 Akkubetrieb, 2 Vorwarnung, 3 apcupsd fährt jetzt herunter. '
  'Damit kann der Miniserver Verbraucher gestaffelt abwerfen, statt vom '
  'Systemhalt überrascht zu werden. Liefert die USV keine Schwellen, bleibt es '
  'bei Stufe 1 — eine erfundene Schwelle wäre schlimmer als keine Stufung.',
  'Whether and when the LoxBerry shuts down is decided by apcupsd — not by this '
  'plugin. The plugin does read the thresholds and reports through '
  '<span class=\'sm-mono\'>alarm_level</span> how close it is: 0 mains, '
  '1 on battery, 2 advance warning, 3 apcupsd is shutting down now. This lets '
  'the Miniserver shed loads in stages instead of being surprised by the halt. '
  'If the UPS reports no thresholds, level 1 is the maximum — an invented '
  'threshold would be worse than no staging.'),
 ('EINST.VORWARN_MIN', 'Vorwarnung ab … Minuten über der Schwelle',
                       'Advance warning from … minutes above the threshold'),
 ('EINST.VORWARN_PROZENT', 'Vorwarnung ab … Prozentpunkten über der Schwelle',
                           'Advance warning from … percentage points above the threshold'),
 ('EINST.LOG_KB', 'Protokolldatei höchstens … Kilobyte',
                  'Log file at most … kilobytes'),
 ('EINST.LOG_KB_HILFE',
  'Der Protokollordner liegt auf einer Ramdisk. Wird die Grenze überschritten, '
  'schneidet der Dienst die ältere Hälfte weg.',
  'The log folder is on a RAM disk. When the limit is exceeded the service cuts '
  'away the older half.'),
 ('EINST.MELDEWEGE', 'Meldewege bei einem Zustandswechsel',
                     'Notification paths on a state change'),
 ('EINST.BENACHRICHTIGUNG', 'LoxBerry-Benachrichtigung',
                            'LoxBerry notification'),
 ('EINST.BENACHRICHTIGUNG_HILFE',
  'Erscheint oben in der LoxBerry-Oberfläche im Glockensymbol.',
  'Appears at the top of the LoxBerry interface under the bell symbol.'),
 ('EINST.EMAIL', 'Zusätzlich eine E-Mail verschicken',
                 'Additionally send an email'),
 ('EINST.EMAIL_HILFE',
  'Der Weg der Originalfassung über <span class=\'sm-mono\'>sendmail</span>. '
  'Setzt voraus, dass auf dem LoxBerry ein Mailversand eingerichtet ist.',
  'The path of the original version, using <span class=\'sm-mono\'>sendmail</span>. '
  'Requires a working mail setup on the LoxBerry.'),
 ('EINST.EMAIL_AN', 'E-Mail an', 'Email to'),
 ('EINST.EMAIL_AN_HILFE',
  'Voreingestellt ist der örtliche Benutzer <span class=\'sm-mono\'>root</span>. '
  'Wohin das tatsächlich geht, entscheidet die Mailkonfiguration des Systems.',
  'The default is the local user <span class=\'sm-mono\'>root</span>. Where this '
  'actually ends up is decided by the mail configuration of the system.'),
 ('EINST.EMAIL_UNGUELTIG',
  'Der Empfänger „%s“ ist weder ein Benutzer dieses Rechners noch eine gültige '
  'E-Mail-Adresse.',
  'The recipient “%s” is neither a user of this machine nor a valid email '
  'address.'),
 # C3/C7 (1.2.14): EINE Pruefung fuer Formular und Sicherung (ap_wert_pruefen).
 ('EINST.NICHT_GESPEICHERT',
  'Nicht gespeichert — die gespeicherten Einstellungen bleiben unverändert. '
  'Bitte berichtigen:',
  'Not saved — the stored settings remain unchanged. Please correct:'),
 ('EINST.W_TYP', '%s: der Wert hat die falsche Form (%s statt Text).',
                 '%s: the value has the wrong form (%s instead of text).'),
 ('EINST.W_SCHALTER', '%s: zulässig sind nur 0 und 1, nicht „%s“.',
                      '%s: only 0 and 1 are allowed, not “%s”.'),
 ('EINST.W_ZAHL', '%s: „%s“ ist keine ganze Zahl von %d bis %d.',
                  '%s: “%s” is not a whole number from %d to %d.'),
 ('EINST.W_ROHFELDER',
  '%s: „%s“ ist keine kommagetrennte Liste von apcaccess-Feldnamen in '
  'Großbuchstaben.',
  '%s: “%s” is not a comma-separated list of apcaccess field names in '
  'capitals.'),
 ('EINST.SPEICHERN_HILFE',
  'Beim Speichern wird der Dienst neu gestartet.',
  'Saving restarts the service.'),
 ('EINST.VON_NENNLEISTUNG', 'von %s W Nennleistung', 'of %s W rated power'),
 ('EINST.VON_NENNSPANNUNG', 'von %s V Nennspannung', 'of %s V nominal voltage'),
 ('EINST.AKKU_ALTER', 'rund %s Monate alt', 'about %s months old'),
 ('EINST.AKKU_ALTER_UNKLAR',
  'Alter nicht bestimmbar — das Datumsformat ist zweideutig',
  'age cannot be determined — the date format is ambiguous'),
 ('EINST.AUSTAUSCH_FAELLIG', 'Austausch fällig', 'replacement due'),
 ('EINST.ABSCHALTSCHWELLEN', 'Abschaltschwellen von apcupsd',
                             'Shutdown thresholds of apcupsd'),
 ('EINST.SCHWELLEN_UNBEKANNT',
  'Diese USV meldet keine Schwellen — alarm_level bleibt deshalb bei höchstens 1',
  'This UPS reports no thresholds — alarm_level therefore stays at 1 at most'),
 ('EINST.STUFE_0', 'Netzbetrieb', 'on mains'),
 ('EINST.STUFE_1', 'Akkubetrieb', 'on battery'),
 ('EINST.STUFE_2', 'Vorwarnung', 'advance warning'),
 ('EINST.STUFE_3', 'apcupsd fährt jetzt herunter', 'apcupsd is shutting down now'),
 ('EINST.NOTABSCHALTUNG', 'Notabschaltung', 'Emergency shutdown'),
 ('EINST.NOTABSCHALTUNG_HILFE',
  'Ob und wann der LoxBerry bei leerem Akku heruntergefahren wird, entscheidet '
  '<b>apcupsd</b>, nicht dieses Plugin. Die Schwellen stehen in '
  '<span class=\'sm-mono\'>/etc/apcupsd/apcupsd.conf</span> unter '
  '<span class=\'sm-mono\'>BATTERYLEVEL</span>, <span class=\'sm-mono\'>MINUTES</span> '
  'und <span class=\'sm-mono\'>TIMEOUT</span>. Das ist bewusst nicht in diese '
  'Oberfläche geholt: es ist eine Systemdatei, die apcupsd selbst verwaltet, und '
  'zwei Stellen mit verschiedenen Schwellen wären schlechter als eine. Die '
  'geltenden Werte zeigt die Tabelle oben.',
  'Whether and when the LoxBerry shuts down on an empty battery is decided by '
  '<b>apcupsd</b>, not by this plugin. The thresholds are in '
  '<span class=\'sm-mono\'>/etc/apcupsd/apcupsd.conf</span> under '
  '<span class=\'sm-mono\'>BATTERYLEVEL</span>, <span class=\'sm-mono\'>MINUTES</span> '
  'and <span class=\'sm-mono\'>TIMEOUT</span>. This is deliberately not pulled into '
  'this page: it is a system file managed by apcupsd, and two places with '
  'different thresholds would be worse than one. The values in force are shown '
  'in the table above.'),

 # Sichern und Zurueckspielen. Nachgetragen am 13.09.2026: diese vierzehn
 # standen seit 1.2.x nur in den .ini-Dateien, nicht hier.
 ('EINST.H_SICHERUNG', 'Einstellungen sichern und zurückspielen',
                       'Back up and restore settings'),
 ('EINST.K_SICHERN', 'Einstellungen sichern', 'Back up settings'),
 ('EINST.K_ZURUECK', 'Zurückspielen', 'Restore'),
 ('EINST.SICH_ERKLAERUNG',
  'Für den <b>Umzug auf einen zweiten LoxBerry</b>: die Datei enthält alle '
  'Einstellungen dieses Plugins und lässt sich dort wieder einspielen.',
  'For <b>moving to a second LoxBerry</b>: the file contains all settings of '
  'this plugin and can be restored there.'),
 ('EINST.SICH_WARNUNG',
  '<b>Was in der Datei steht:</b> alle Einstellungen der Reiter Einstellungen '
  'und MQTT, darunter der USV-Host und der E-Mail-Empfänger. Zugangsdaten '
  'stehen keine darin — die Anmeldung am MQTT-Broker verwaltet LoxBerry selbst '
  '—, und das Formularmerkmal bleibt auf diesem LoxBerry. Wer die Datei '
  'weitergibt, gibt Rechnernamen und Empfänger weiter, sonst nichts.',
  '<b>What the file contains:</b> all settings of the Settings and MQTT tabs, '
  'including the UPS host and the email recipient. It contains no credentials — '
  'LoxBerry itself manages the login to the MQTT broker — and the form marker '
  'stays on this LoxBerry. Whoever passes the file on passes on host names and '
  'recipients, nothing else.'),
 ('EINST.SICH_ABGELEHNT',
  'Die Datei wurde <b>nicht</b> übernommen — es ist nichts geändert worden:',
  'The file was <b>not</b> accepted — nothing has been changed:'),
 ('EINST.SICH_UEBERNOMMEN', 'Einstellungen zurückgespielt: %d Werte übernommen.',
                            'Settings restored: %d values taken over.'),
 ('EINST.SICH_FEHLEND',
  'In der Datei fehlen %d Einstellungen: %s. Eine unvollständige Sicherung wird '
  'nicht zurückgespielt — sonst fielen die fehlenden Werte stillschweigend auf '
  'die Werkseinstellung zurück, ohne dass an der Oberfläche etwas davon zu sehen '
  'wäre.',
  'The file is missing %d settings: %s. An incomplete backup is not restored — '
  'otherwise the missing values would silently fall back to the factory '
  'defaults, with nothing on the page to show it.'),
 ('EINST.SICH_FREMD', 'Unbekannte Einstellung in der Datei: %s',
                      'Unknown setting in the file: %s'),
 ('EINST.SICH_KEINE_DATEI',
  'Es wurde keine Datei ausgewählt oder der Upload ist fehlgeschlagen.',
  'No file was selected, or the upload failed.'),
 ('EINST.SICH_KEIN_JSON', 'Die Datei ist keine gültige Sicherung dieses Plugins.',
                          'The file is not a valid backup of this plugin.'),
 ('EINST.SICH_LEER', 'Die Datei enthält keine bekannte Einstellung.',
                     'The file contains no known setting.'),
 ('EINST.SICH_SCHREIBFEHLER', 'Die Einstellungen ließen sich nicht schreiben.',
                              'The settings could not be written.'),
 ('EINST.SICH_ZU_GROSS',
  'Die Datei ist größer als erlaubt — eine Sicherung dieses Plugins ist wenige '
  'Kilobyte groß.',
  'The file is larger than allowed — a backup of this plugin is a few '
  'kilobytes.'),
 ('EINST.SICH_STAND', 'Fassung %s, gesichert am %s', 'Version %s, saved on %s'),
 ('EINST.SICH_KOPF_HINWEIS',
  'Einstellungen des Plugins APC-UPS NG. Die Datei enthält keine Zugangsdaten '
  'und nicht das Formularmerkmal. Zurückspielen im Reiter Einstellungen; '
  'Schlüssel, die mit einem Unterstrich beginnen, werden dabei überlesen.',
  'Settings of the APC-UPS NG plugin. The file contains no credentials and not '
  'the form marker. Restore it in the Settings tab; keys starting with an '
  'underscore are skipped there.'),
 ('EINST.SICH_DIENST_NICHT',
  'Der Dienst lief nicht und wurde nicht gestartet; die Einstellungen gelten '
  'bei seinem nächsten Start.',
  'The service was not running and has not been started; the settings take '
  'effect at its next start.'),
 # X-2 (Regeln/04, 30.09.2026): nach einer Beanstandung stehen die
 # eingetippten Werte wieder im Formular.
 ('EINST.EINGABEN_ZURUECK',
  'Im Formular stehen die eingetippten Werte, das beanstandete Feld ist rot '
  'umrandet. Gespeichert ist weiterhin der bisherige Stand.',
  'The form shows the values you typed; the rejected field has a red border. '
  'The previously stored settings remain in force.'),
 # X-3 (30.09.2026): Sichern warnt, wenn das eigene Zurueckspielen die Datei
 # abweisen wuerde - ueber dieselbe Pruefung (ap_sicherung_lesen).
 ('EINST.SICH_EIGEN_WARNUNG',
  'Diese Sicherung würde beim Zurückspielen abgewiesen, weil gespeicherte '
  'Werte die Prüfung nicht bestehen: %s. „Einstellungen sichern“ liefert die '
  'Datei trotzdem; wer sie später zurückspielen will, berichtigt die Werte '
  'vorher und speichert.',
  'This backup would be rejected on restore because stored values fail the '
  'check: %s. “Back up settings” still delivers the file; to restore it '
  'later, correct the values first and save.'),
 ('EINST.SICH_KOPF_WARNUNG',
  'Achtung: diese Datei würde beim Zurückspielen abgewiesen. Betroffene '
  'Einstellungen: %s',
  'Caution: this file would be rejected on restore. Affected settings: %s'),

 # ---------------- MQTT ----------------
 ('MQTT.ZUSTAND', 'Zustand des Gateways', 'State of the gateway'),
 ('MQTT.BROKER', 'Broker', 'Broker'),
 ('MQTT.KEIN_BROKER', 'nicht gefunden', 'not found'),
 ('MQTT.KEIN_BROKER_LANG',
  'In general.json steht keine Brokeradresse. Der MQTT-Gateway ist seit '
  'LoxBerry 3 Bestandteil des Systems und wird unter System → MQTT Gateway '
  'eingerichtet — er muss nicht nachinstalliert werden.',
  'general.json contains no broker address. Since LoxBerry 3 the MQTT gateway is '
  'part of the system and is configured under System → MQTT Gateway — it does '
  'not need to be installed separately.'),
 ('MQTT.AUTOSTART', 'Gateway startet selbst', 'Gateway starts by itself'),
 ('MQTT.PRAEFIX', 'Themenpräfix', 'Topic prefix'),
 ('MQTT.PRAEFIX_HILFE',
  'Alle Themen dieses Plugins beginnen damit. Wer ihn ändert, muss das Abo im '
  'Gateway und die virtuellen Eingänge in Loxone nachziehen.',
  'All topics of this plugin start with it. If you change it you must also '
  'adjust the subscription in the gateway and the virtual inputs in Loxone.'),
 ('MQTT.PRAEFIX_GEAENDERT',
  'Aus dem Themenpräfix wurden Zeichen entfernt, die in einem MQTT-Thema nicht '
  'zulässig sind. Bitte oben nachsehen, was jetzt dort steht.',
  'Characters that are not allowed in an MQTT topic were removed from the topic '
  'prefix. Please check above what it says now.'),
 # M5 (1.2.14): bis 1.2.13 wurde das Praefix still gesaeubert (PRAEFIX_GEAENDERT,
 # seither unbenutzt); jetzt wird es abgewiesen.
 ('MQTT.PRAEFIX_UNGUELTIG',
  'Das Themenpräfix „%s“ ist nicht zulässig und wurde nicht gespeichert. Erlaubt '
  'sind Buchstaben, Ziffern, Unterstrich und Bindestrich, Ebenen durch einen '
  'einzelnen Schrägstrich getrennt — kein Schrägstrich am Anfang oder am Ende, '
  'kein # und kein +, höchstens 64 Zeichen.',
  'The topic prefix “%s” is not allowed and was not saved. Allowed are letters, '
  'digits, underscore and hyphen, levels separated by a single slash — no slash '
  'at the start or end, no # and no +, at most 64 characters.'),
 ('MQTT.PRAEFIX_GESPEICHERT_UNGUELTIG',
  'Das gespeicherte Themenpräfix „%s“ ist nicht zulässig. Der Dienst sendet '
  'damit nichts, bis es hier berichtigt und gespeichert ist.',
  'The stored topic prefix “%s” is not allowed. The service sends nothing with '
  'it until it has been corrected and saved here.'),
 ('MQTT.ALT_RAEUMEN',
  'Unter dem bisherigen Präfix „%s/“ räumt der Dienst die behaltenen Themen '
  'dieses Plugins im Broker ab, sobald er die neue Einstellung liest; das '
  'Protokoll nennt das Ergebnis.',
  'Under the previous prefix “%s/” the service clears the retained topics of '
  'this plugin in the broker as soon as it reads the new setting; the log '
  'states the result.'),
 ('MQTT.EINSTELLUNGEN', 'Einstellungen', 'Settings'),
 ('MQTT.EINSCHALTEN', 'Werte über MQTT veröffentlichen',
                      'Publish values over MQTT'),
 ('MQTT.EINSCHALTEN_HILFE',
  'MQTT ist der Regelweg. Der alte XML-Weg bleibt daneben bestehen.',
  'MQTT is the standard path. The old XML endpoint remains available alongside.'),
 ('MQTT.ROHFELDER', 'Zusätzliche Rohfelder von apcaccess',
                    'Additional raw fields from apcaccess'),
 ('MQTT.ROHFELDER_HILFE',
  'Kommagetrennte Feldnamen, genau so geschrieben wie in der Ausgabe von '
  'apcaccess. Sie gehen unverändert unter '
  '<span class=\'sm-mono\'>&lt;Präfix&gt;/raw/&lt;FELD&gt;</span> hinaus. Damit '
  'lassen sich Werte holen, die nur bestimmte Modelle liefern, ohne auf eine '
  'neue Fassung des Plugins zu warten. Ab Werk leer. Steht darin etwas, das '
  'kein Feldname ist, oder ein Name doppelt, wird nichts gespeichert. '
  'Kleinbuchstaben werden zu Großbuchstaben; Komma, Semikolon und Leerzeichen '
  'trennen gleichermaßen.',
  'Comma separated field names, spelled exactly as in the output of apcaccess. '
  'They are published unchanged under '
  '<span class=\'sm-mono\'>&lt;prefix&gt;/raw/&lt;FIELD&gt;</span>. This lets you '
  'fetch values that only certain models provide, without waiting for a new '
  'version of the plugin. Empty by default. If it contains anything that is not '
  'a field name, or a name twice, nothing is saved. Lower case is turned into '
  'capitals; comma, semicolon and space all work as separators.'),
 ('MQTT.ROHFELD_ABGEWIESEN',
  'Diese Angaben in der gespeicherten Einstellung sehen nicht wie '
  'apcaccess-Feldnamen aus und werden nicht veröffentlicht: %s.',
  'These entries in the stored setting do not look like apcaccess field names '
  'and are not published: %s.'),
 # Nr. 19 (01.10.2026): beanstanden statt still verwerfen - nichts wird
 # gespeichert, das Feld ist markiert, die Eingabe kommt zurueck (X-2).
 ('MQTT.ROHFELD_BEANSTANDET',
  '%s: Diese Angaben sehen nicht wie apcaccess-Feldnamen aus (zuerst ein '
  'Buchstabe, dann Buchstaben, Ziffern oder _, höchstens 32 Zeichen): %s.',
  '%s: These entries do not look like apcaccess field names (a letter first, '
  'then letters, digits or _, at most 32 characters): %s.'),
 ('MQTT.ROHFELD_DOPPELT',
  '%s: Diese Feldnamen stehen mehrfach in der Liste: %s.',
  '%s: These field names appear more than once in the list: %s.'),
 # Die Ueberschrift ist neutral: unter Gateway V2 ist nichts einzutragen,
 # und der LoxBerry-Kern schaltet dort die Eingabeknoepfe ab. Die
 # Aufforderung steht deshalb nur noch im V1-Satz ABO_OHNE.
 ('MQTT.ABO_UEBERSCHRIFT', 'Das Abo im MQTT-Gateway',
                           'The subscription in the MQTT gateway'),
 ('MQTT.ABO_SATZ', 'Die Themengruppe dieses Plugins lautet:',
                   'The topic group of this plugin is:'),
 ('MQTT.ABO_WEG',
  'Das MQTT-Gateway ist seit LoxBerry 3 Bestandteil des Systems und liegt '
  'unter <b>System → MQTT Gateway</b>.',
  'Since LoxBerry 3 the MQTT gateway is part of the system and can be found '
  'under <b>System → MQTT Gateway</b>.'),
 # Seit 1.2.14 bringt das Plugin das Abo selbst mit (config/plugins/<ordner>/
 # mqtt_subscriptions.cfg), und das Gateway liest diese Datei. Bis 1.2.13 hiess
 # es hier "Ohne diesen Eintrag kommt am Miniserver nichts an".
 ('MQTT.ABO_OHNE',
  'Das Plugin trägt das Abo selbst ein (Datei <i>mqtt_subscriptions.cfg</i>), '
  'das MQTT-Gateway liest sie. Kommt am Miniserver trotzdem nichts an, unter '
  '<i>System → MQTT Gateway</i> im Abschnitt <i>Subscriptions</i> nachsehen, ob '
  'die Zeile dort steht.',
  'The plugin enters the subscription itself (file <i>mqtt_subscriptions.cfg</i>), '
  'and the MQTT gateway reads it. If nothing arrives at the Miniserver anyway, '
  'check under <i>System → MQTT Gateway</i> in the <i>Subscriptions</i> section '
  'whether the line is there.'),
 ('MQTT.W_AUTOSTART',
  'Der MQTT-Gateway ist nicht auf Selbststart eingestellt. Nach einem Neustart '
  'des LoxBerry kommt dann nichts mehr an. Einzustellen unter '
  'System → MQTT Gateway.',
  'The MQTT gateway is not set to start automatically. After a restart of the '
  'LoxBerry nothing will arrive any more. Set it under System → MQTT Gateway.'),
 ('MQTT.W_AUSGESCHALTET',
  'MQTT ist ausgeschaltet. Es geht nichts an den Broker, und die Vorlage für '
  'Loxone bringt so nichts.',
  'MQTT is switched off. Nothing is sent to the broker, and the Loxone template '
  'is of no use like this.'),
 ('MQTT.THEMEN', 'Was veröffentlicht wird', 'What is published'),
 ('MQTT.THEMEN_HILFE',
  'Diese Liste kommt aus <span class=\'sm-mono\'>bin/apc_themen.json</span> — '
  'derselben Datei, aus der auch der Dienst liest. Zwei getrennte Listen liefen '
  'bis 1.1.6 auseinander.',
  'This list comes from <span class=\'sm-mono\'>bin/apc_themen.json</span> — the '
  'same file the service reads. Up to 1.1.6 two separate lists had drifted apart.'),
 ('MQTT.SP_THEMA', 'Thema', 'Topic'),
 ('MQTT.SP_ART', 'Art', 'Type'),
 ('MQTT.SP_EINHEIT', 'Einheit', 'Unit'),
 ('MQTT.SP_RETAIN', 'retained', 'retained'),
 ('MQTT.SP_BEDEUTUNG', 'Bedeutung', 'Meaning'),
 ('MQTT.RETAIN_ERKLAERUNG',
  '<b>Retained heißt:</b> der Broker merkt sich den letzten Wert und gibt ihn '
  'jedem neuen Abnehmer sofort. Das ist für Zustände richtig — Modell, '
  'Seriennummer, ob die USV am Netz hängt. Für Messwerte wäre es schädlich: '
  'wer sich nach einer Stunde neu verbindet, bekäme eine stundenalte '
  'Restlaufzeit serviert und hielte sie für aktuell. Deshalb ist nur ein Teil '
  'der Themen retained; die Spalte oben sagt für jedes einzelne, welcher. '
  'Wie frisch ein Wert ist, sagt <span class=\'sm-mono\'>timestamp</span>.',
  '<b>Retained means:</b> the broker remembers the last value and hands it to '
  'every new subscriber immediately. That is right for states — model, serial '
  'number, whether the UPS is on mains. For measurements it would be harmful: '
  'anyone reconnecting after an hour would be served an hour-old runtime and '
  'take it for current. Therefore only part of the topics is retained; the '
  'column above says which, for every single one. How fresh a value is, is told '
  'by <span class=\'sm-mono\'>timestamp</span>.'),
 ('MQTT.RETAIN_KURZ',
  'Mit R gekennzeichnete Themen bleiben im Broker liegen; die übrigen kommen '
  'nur beim Senden. Wie frisch ein Wert ist, sagt das Thema timestamp.',
  'Topics marked with R stay in the broker; the others arrive only when sent. '
  'How fresh a value is, is told by the timestamp topic.'),

 # Die Abo-Zeile haengt an der Gateway-Fassung. Nachgetragen am 13.09.2026.
 ('MQTT.ABO_GEMESSEN', '(gemessen: Gateway&nbsp;V%d)',
                       '(measured: gateway&nbsp;V%d)'),
 ('MQTT.ABO_V2',
  '<b>MQTT&#8209;Gateway V2 erkennt die Themengruppe von selbst</b> — '
  'einzutragen ist hier nichts. In den <i>Subscriptions</i> erscheint die '
  'Gruppe; dort werden die gewünschten Datenpunkte einzeln angehakt. Erscheint '
  'sie nicht, hat noch nichts veröffentlicht.',
  '<b>MQTT gateway V2 detects the topic group by itself</b> — nothing needs to '
  'be entered here. The group appears under <i>Subscriptions</i>; tick the data '
  'points you want there. If it does not appear, nothing has been published '
  'yet.'),
 ('MQTT.ABO_UNBEKANNT',
  'Welche Fassung Ihr MQTT&#8209;Gateway hat, ließ sich nicht feststellen. '
  '<b>Fassung&nbsp;1:</b> ohne diesen Eintrag kommt am Miniserver nichts an; '
  'die Zeile gehört unter <i>System → MQTT Gateway</i> in den Abschnitt '
  '<i>Subscriptions</i>. <b>Fassung&nbsp;2 und neuer:</b> die Themengruppe '
  'erscheint von selbst in den Subscriptions, einzutragen ist nichts.',
  'The version of your MQTT gateway could not be determined. '
  '<b>Version&nbsp;1:</b> without this entry nothing arrives at the Miniserver; '
  'the line belongs under <i>System → MQTT Gateway</i> in the '
  '<i>Subscriptions</i> section. <b>Version&nbsp;2 and newer:</b> the topic '
  'group appears by itself under Subscriptions, nothing needs to be entered.'),

 # ---------------- LOXONE ----------------
 ('LOXONE.SCHRITT1', 'Schritt 1: Weg festlegen', 'Step 1: choose the path'),
 ('LOXONE.SCHRITT1_TEXT',
  '<b>MQTT ist der Regelweg.</b> Das Gateway erzeugt die Namen der virtuellen '
  'Eingänge selbst; in Loxone genügt ein passend benannter virtueller Eingang. '
  'Der alte XML-Weg bleibt für bestehende Anlagen erhalten und ist weiter unten '
  'beschrieben. Zuerst im Reiter <b>Test</b> mit <i>Jetzt abfragen</i> prüfen, '
  'ob die USV überhaupt antwortet — kommen dort Werte, ist der schwierige Teil '
  'erledigt.',
  '<b>MQTT is the standard path.</b> The gateway creates the names of the '
  'virtual inputs itself; in Loxone a suitably named virtual input is enough. '
  'The old XML path remains for existing installations and is described below. '
  'First check in the <b>Test</b> tab with <i>Query now</i> whether the UPS '
  'answers at all — if values arrive there, the hard part is done.'),
 ('LOXONE.SCHRITT2', 'Schritt 2: Das Abo im MQTT-Gateway',
                     'Step 2: the subscription in the MQTT gateway'),
 ('LOXONE.SCHRITT2_TEXT',
  'Die Themengruppe dieses Plugins lautet:',
  'The topic group of this plugin is:'),
 ('LOXONE.SCHRITT3', 'Schritt 3: Virtuelle Eingänge anlegen',
                     'Step 3: create the virtual inputs'),
 ('LOXONE.SCHRITT3_TEXT',
  'Die Importdatei legt alle Eingänge samt Titel, Einheit und Grenzen an. In '
  'Loxone Config über <i>Vorlage einfügen</i> einlesen. Welche Themen es gibt '
  'und was sie bedeuten, steht im Reiter MQTT.',
  'The import file creates all inputs including title, unit and limits. Read it '
  'into Loxone Config via <i>Insert template</i>. Which topics exist and what '
  'they mean is listed in the MQTT tab.'),
 ('LOXONE.KNOPF_MQTT', 'Vorlage für den MQTT-Weg erzeugen',
                       'Create template for the MQTT path'),
 ('LOXONE.KNOPF_XML', 'Vorlage für den alten XML-Weg erzeugen',
                      'Create template for the old XML path'),
 ('LOXONE.VORLAGE_ZAHL',
  'Die MQTT-Vorlage legt %d virtuelle Eingänge an. Die %d Textthemen sind '
  'bewusst nicht dabei: das nachgebaute Vorlagenformat ist nur für Zahlenwerte '
  'belegt, und ein analoger Eingang auf einem Text zeigt dauerhaft 0. Wer sie '
  'in Loxone braucht, legt sie von Hand als Virtuellen Texteingang an, Titel = '
  'Präfix_Thema (z. B. %s).',
  'The MQTT template creates %d virtual inputs. The %d text topics are '
  'deliberately not included: the rebuilt template format is only proven for '
  'numeric values, and an analogue input on a text permanently shows 0. '
  'Whoever needs them in Loxone creates them by hand as a virtual text input, '
  'title = prefix_topic (e.g. %s).'),
 # 1.2.21 (Hausherr 14.10.2026): Hinweis bei einem Praefix mit Schraegstrich (index.php,
 # Schritt 3); maskiert ausgegeben (ap_e), keine Auszeichnung.
 ('LOXONE.PRAEFIX_SCHRAEG',
  'Ihr Themenpräfix „%s“ enthält einen Schrägstrich. In Loxone steht dafür ein '
  'Unterstrich, so wie das MQTT-Gateway die Eingänge benennt: %s statt %s. '
  'Vorlage und Baustein-Listen auf dieser Seite verwenden schon diese Namen.',
  'Your topic prefix “%s” contains a slash. In Loxone it becomes an '
  'underscore, just as the MQTT gateway names the inputs: %s instead of %s. '
  'The template and the block lists on this page already use these names.'),
 ('LOXONE.IMPORT_DOPPELT',
  'Loxone Config legt beim Import neu an und überschreibt nichts. Zweimal '
  'importiert heißt doppelte Objekte.',
  'On import Loxone Config creates new objects and overwrites nothing. Importing '
  'twice means duplicate objects.'),
 ('LOXONE.SCHRITT4', 'Schritt 4: Befehle senden', 'Step 4: sending commands'),
 ('LOXONE.SCHRITT4_TEXT',
  'Dieses Plugin schaltet nichts an der USV. Es gibt deshalb keinen virtuellen '
  'Ausgang und keine Vorlage dafür. Der Grund ist nicht Bequemlichkeit: der '
  'Messdienst läuft bewusst ohne Rootrechte, und ein Befehl an die USV braucht '
  'sie. Was die USV bei leerem Akku tut, entscheidet apcupsd — siehe Reiter '
  'Einstellungen, Abschnitt Notabschaltung.',
  'This plugin does not switch anything on the UPS. There is therefore no virtual '
  'output and no template for one. The reason is not convenience: the monitoring '
  'service deliberately runs without root privileges, and a command to the UPS '
  'needs them. What the UPS does on an empty battery is decided by apcupsd — see '
  'the Settings tab, section Emergency shutdown.'),
 ('LOXONE.SCHRITT5', 'Schritt 5: Ausfallerkennung', 'Step 5: detecting a failure'),
 ('LOXONE.SCHRITT5_TEXT',
  'Ein virtueller Eingang behält seinen letzten Wert, wenn nichts mehr kommt. '
  'In der App sieht dann alles normal aus, obwohl längst nichts mehr gemessen '
  'wird. Drei Themen sind dagegen da: '
  '<span class=\'sm-mono\'>service/online</span> fällt auf 0, sobald der Dienst '
  'stirbt (der Broker setzt das selbst, auch bei einem Absturz); '
  '<span class=\'sm-mono\'>data_valid</span> fällt auf 0, wenn apcupsd die USV '
  'nicht mehr erreicht; und <span class=\'sm-mono\'>timestamp</span> sagt, wann '
  'zuletzt gemessen wurde. Eine Zeitüberwachung auf timestamp sollte deutlich '
  'über dem eingestellten Abfragetakt liegen, damit ein einzelner verpasster '
  'Durchlauf keine Meldung auslöst.',
  'A virtual input keeps its last value when nothing arrives any more. In the app '
  'everything then looks normal although nothing has been measured for a long '
  'time. Three topics guard against this: '
  '<span class=\'sm-mono\'>service/online</span> drops to 0 as soon as the service '
  'dies (the broker sets this itself, even on a crash); '
  '<span class=\'sm-mono\'>data_valid</span> drops to 0 when apcupsd can no longer '
  'reach the UPS; and <span class=\'sm-mono\'>timestamp</span> says when the last '
  'measurement was taken. A timeout watching timestamp should be set well above '
  'the configured query interval so that a single missed round does not trigger '
  'a message.'),
 ('LOXONE.SCHRITT6',
  'Schritt 6: Zwei komplette Baustein-Listen zum Nachbauen',
  'Step 6: two complete block lists to rebuild'),
 ('LOXONE.BAUSTEINE_VORTEXT',
  'Zwei Seiten aus dem LoxBerry-Plugins Musterprojekt, jede Zeile ein Baustein '
  '(Baustein-Suche in Loxone Config: Taste <b>F5</b>). Die erste zeigt '
  'Stromausfall, Vorwarnung und Abschaltung, meldet Störungen der Abfrage und '
  'wirft bei knappem Akku Verbraucher ab – sie genügt für den Anfang. Die '
  'zweite zeigt Akku, Netz, Last und Gerätedaten und meldet Überlast, Wärme, '
  'einen Akku, der nicht lädt, und ein unruhiges Netz. Die Eingänge kommen aus '
  'der Vorlage für den MQTT-Weg (Schritt 3), die Texteingänge legen Sie von '
  'Hand an; die Namen vergibt das MQTT-Gateway – sie bleiben, wie sie sind.',
  'Two pages from the LoxBerry plugins sample project, every row one block '
  '(block search in Loxone Config: key <b>F5</b>). The first shows power '
  'failure, advance warning and shutdown, reports faults of the query and '
  'sheds loads when the battery runs low – it is enough to start with. The '
  'second shows battery, mains, load and device data and reports overload, '
  'heat, a battery that does not charge and an unsteady mains. The inputs come '
  'from the template for the MQTT path (step 3), the text inputs are created '
  'by hand; the MQTT gateway assigns the names – keep them as they are.'),
 ('LOXONE.SP_BAUSTEIN', 'Baustein (Typ)', 'Block (type)'),
 ('LOXONE.SP_NAME', 'Name (Vorschlag)', 'Name (suggestion)'),
 ('LOXONE.SP_PARAMETER', 'Parameter', 'Parameters'),
 ('LOXONE.SP_EINGAENGE', 'Eingänge verbinden mit', 'Connect inputs to'),
 # Welle Bild 12 VOLL (1.2.20): zwei Baustein-Listen aus dem LoxBerry-Plugins Musterprojekt
 # (Seiten APC-UPS NG / APC-UPS NG Akku und Netz). Alle Werte werden MASKIERT ausgegeben
 # (ap_e): keine Auszeichnung, keine Entitaeten. Ersetzt B_VE ... ZU_6 der Liste bis 1.2.19.
 ('LOXONE.S1_01_PARAM',
  '1 = Akkubetrieb (Stromausfall)',
  '1 = on battery (power failure)'),
 ('LOXONE.S1_02_PARAM',
  '0 Netz, 1 Akku, 2 Vorwarnung, 3 Abschaltung',
  '0 mains, 1 battery, 2 advance warning, 3 shutdown'),
 ('LOXONE.S1_03_PARAM',
  '1 = Werte brauchbar; 0 = apcupsd erreicht die USV nicht',
  '1 = values usable; 0 = apcupsd cannot reach the UPS'),
 ('LOXONE.S1_04_PARAM',
  '1 = die USV meldet ‚Akku tauschen‘',
  '1 = the UPS reports ‘replace battery’'),
 ('LOXONE.S1_05_PARAM',
  'Restlaufzeit in Minuten',
  'runtime left in minutes'),
 ('LOXONE.S1_06_PARAM',
  'Zeitpunkt der letzten Abfrage (Sekunden seit 1970); ändert sich bei jeder '
  'Abfrage, ab Werk alle 30 s',
  'time of the last query (seconds since 1970); changes with every query, '
  'every 30 s by default'),
 ('LOXONE.S1_07_PARAM',
  '1 = Dienst läuft; 0 setzt der Broker selbst, wenn der Dienst abstürzt oder '
  'angehalten wird',
  '1 = service running; the broker itself sets 0 when the service crashes or '
  'is stopped'),
 ('LOXONE.S1_08_PARAM',
  '10 s',
  '10 s'),
 ('LOXONE.S1_08_NAME',
  'Netzausfall entprellt',
  'Netzausfall entprellt'),
 ('LOXONE.S1_09_NAME',
  'Keine Verbindung zur USV',
  'Keine Verbindung zur USV'),
 ('LOXONE.S1_10_NAME',
  'Sammelstörung, erste Stufe',
  'Sammelstörung, erste Stufe'),
 ('LOXONE.S1_11_NAME',
  'Sammelstörung USV',
  'Sammelstörung USV'),
 ('LOXONE.S1_12_PARAM',
  'Text: USV – Stromausfall oder Störung der USV-Abfrage; in der App die '
  'Status ‚USV-Zustand‘ und ‚USV-Abfrage‘ lesen',
  'text: UPS – power failure or fault of the UPS query; read the states '
  '‘USV-Zustand’ and ‘USV-Abfrage’ in the app'),
 ('LOXONE.S1_12_NAME',
  'USV-Meldung',
  'USV-Meldung'),
 ('LOXONE.S1_13_PARAM',
  'Ein 2 / Aus 1 (ab Stufe 2 Vorwarnung)',
  'On 2 / Off 1 (from level 2, advance warning)'),
 ('LOXONE.S1_13_NAME',
  'Lastabwurf ab Vorwarnung',
  'Lastabwurf ab Vorwarnung'),
 ('LOXONE.S1_14_PARAM',
  'Visualisierung EIN; im eigenen Projekt an die Verbraucher legen, die bei '
  'knappem Akku aus sollen',
  'visualisation ON; in your own project connect it to the loads that should '
  'switch off when the battery runs low'),
 ('LOXONE.S1_14_NAME',
  'Stromsparen aktiv',
  'Stromsparen aktiv'),
 ('LOXONE.S1_15_PARAM',
  'Zeilen: V4 = 0 „keine gültigen Werte – siehe Status ‚USV-Abfrage‘“; V1 = 3 '
  '„Abschaltung läuft – apcupsd fährt herunter“; V1 = 2 „Vorwarnung – Akku '
  '<v3.0> %, noch etwa <v2.0> min; Verbraucher abwerfen“; V1 = 1 „Stromausfall '
  'seit <v5.0> s – Akku <v3.0> %, noch etwa <v2.0> min“; ohne Bedingung '
  '„Netzbetrieb – Akku <v3.0> %, Überbrückung etwa <v2.0> min; zuletzt: <v6>“; '
  'Visualisierung EIN',
  'rows: V4 = 0 “no valid values – see status ‘USV-Abfrage’”; V1 = 3 “shutdown '
  'running – apcupsd is shutting down”; V1 = 2 “advance warning – battery '
  '<v3.0> %, about <v2.0> min left; shed loads”; V1 = 1 “power failure since '
  '<v5.0> s – battery <v3.0> %, about <v2.0> min left”; without condition “on '
  'mains – battery <v3.0> %, bridging about <v2.0> min; last: <v6>”; '
  'visualisation ON'),
 ('LOXONE.S1_15_NAME',
  'USV-Zustand',
  'USV-Zustand'),
 ('LOXONE.S1_16_PARAM',
  'Akkuladung in %',
  'battery charge in %'),
 ('LOXONE.S1_17_PARAM',
  '1 = letzte Abfrage bei apcupsd gelungen; 0 = apcupsd antwortet nicht '
  '(Dienst läuft aber)',
  '1 = last query to apcupsd succeeded; 0 = apcupsd does not answer (but the '
  'service is running)'),
 ('LOXONE.S1_18_PARAM',
  'Wert 1',
  'value 1'),
 ('LOXONE.S1_18_NAME',
  'Konstante 1',
  'Konstante 1'),
 ('LOXONE.S1_19_PARAM',
  'Tmc 150 s (fünfmal „Abfragen alle 30 Sekunden“), Min 0, Max 2147483647',
  'Tmc 150 s (five times “Query every 30 seconds”), Min 0, Max 2147483647'),
 ('LOXONE.S1_19_NAME',
  'USV-Abfrage stumm',
  'USV-Abfrage stumm'),
 ('LOXONE.S1_20_NAME',
  'APC-Dienst aus',
  'APC-Dienst aus'),
 ('LOXONE.S1_21_NAME',
  'apcupsd antwortet nicht',
  'apcupsd antwortet nicht'),
 ('LOXONE.S1_22_PARAM',
  '— (Dienst aus oder keine neuen Abfragen)',
  '— (service off or no new queries)'),
 ('LOXONE.S1_22_NAME',
  'APC-Dienst gestört',
  'APC-Dienst gestört'),
 ('LOXONE.S1_23_PARAM',
  '— (Dienst gestört oder apcupsd antwortet nicht)',
  '— (service disturbed or apcupsd does not answer)'),
 ('LOXONE.S1_23_NAME',
  'USV-Abfrage gestört',
  'USV-Abfrage gestört'),
 ('LOXONE.S1_24_PARAM',
  '60 s (zwei Abfragen; ein Neustart des Dienstes meldet nicht)',
  '60 s (two queries; a restart of the service does not report)'),
 ('LOXONE.S1_24_NAME',
  'Abfrage länger gestört',
  'Abfrage länger gestört'),
 ('LOXONE.S1_25_PARAM',
  'Text: USV – die USV meldet „Akku tauschen“; Ersatzakku einsetzen, solange '
  'das Netz da ist. In der App den Status „USV Akku“ lesen',
  'text: UPS – the UPS reports “replace battery”; insert a replacement battery '
  'while mains power is there. Read the status “USV Akku” in the app'),
 ('LOXONE.S1_25_NAME',
  'USV Akku tauschen',
  'USV Akku tauschen'),
 ('LOXONE.S1_26_PARAM',
  'Sekunden im laufenden Akkubetrieb; 0 bei Netzbetrieb',
  'seconds in the current battery operation; 0 on mains'),
 ('LOXONE.S1_27_NAME',
  'Netzausfall endet',
  'Netzausfall endet'),
 ('LOXONE.S1_28_PARAM',
  'Text: USV – das Netz ist wieder da, die USV lädt den Akku; abgeworfene '
  'Verbraucher wieder einschalten',
  'text: UPS – mains power is back, the UPS is charging the battery; switch '
  'shed loads back on'),
 ('LOXONE.S1_28_NAME',
  'USV Netz wieder da',
  'USV Netz wieder da'),
 ('LOXONE.S1_29_PARAM',
  '5 s (fängt den kurzen Impuls des Schwellwertschalters ab)',
  '5 s (absorbs the short pulse of the threshold switch)'),
 ('LOXONE.S1_29_NAME',
  'Vorwarnung bestätigt',
  'Vorwarnung bestätigt'),
 ('LOXONE.S1_30_PARAM',
  'Text: USV – Vorwarnung: der Akku reicht nur noch wenige Minuten bis zur '
  'Abschaltung; nicht benötigte Geräte am USV-Ausgang ausschalten',
  'text: UPS – advance warning: the battery only lasts a few more minutes '
  'until shutdown; switch off devices at the UPS output that are not needed'),
 ('LOXONE.S1_30_NAME',
  'USV Akku bald leer',
  'USV Akku bald leer'),
 ('LOXONE.S1_31_PARAM',
  '1 = Abschaltschwelle erreicht, apcupsd fährt jetzt herunter',
  '1 = shutdown threshold reached, apcupsd is shutting down now'),
 ('LOXONE.S1_32_PARAM',
  'Text: USV – Abschaltschwelle erreicht; apcupsd fährt jetzt den Rechner '
  'herunter, an dem die USV hängt. Geräte am USV-Ausgang gehen gleich aus',
  'text: UPS – shutdown threshold reached; apcupsd is now shutting down the '
  'computer the UPS is connected to. Devices at the UPS output will go off '
  'shortly'),
 ('LOXONE.S1_32_NAME',
  'USV Abschaltung',
  'USV Abschaltung'),
 ('LOXONE.S1_33_PARAM',
  'Zustandstext der USV, z. B. ONLINE, ONBATT, COMMLOST; „-“ = apcupsd '
  'antwortet nicht; Titel genau so (Name, den das MQTT-Gateway vergibt), „In '
  'Visualisierung verwenden“ an',
  'state text of the UPS, e.g. ONLINE, ONBATT, COMMLOST; “-” = apcupsd does '
  'not answer; title exactly like this (the name the MQTT gateway assigns), '
  '“Use in visualisation” on'),
 ('LOXONE.S1_34_PARAM',
  'letztes Ereignis, z. B. „Stromausfall“, „Netz wieder da“; Titel genau so',
  'last event, e.g. “Stromausfall”, “Netz wieder da”; title exactly like this'),
 ('LOXONE.S1_35_PARAM',
  'Fehlermeldung der letzten Abfrage, leer = in Ordnung; Titel genau so',
  'error message of the last query, empty = OK; title exactly like this'),
 ('LOXONE.S1_36_PARAM',
  'Zeilen: V1 = 0 „Dienst läuft nicht – im Plugin Reiter Test ‚Dienst neu '
  'starten‘“; V2 = 1 „Dienst fragt nicht mehr ab – letzte Abfrage <v3.t>; im '
  'Plugin Reiter Einstellungen ‚Plugin eingeschaltet‘ prüfen, sonst Reiter '
  'Test ‚Dienst neu starten‘“; V4 = 0 „apcupsd antwortet nicht: <v5> – im '
  'Plugin Reiter Test ‚apcupsd prüfen‘“; V6 = 0 „apcupsd erreicht die USV '
  'nicht (Kabel?) – <v7>“; ohne Bedingung „in Ordnung – USV meldet <v7>, '
  'letzte Abfrage <v3.t>“',
  'rows: V1 = 0 “service not running – on the Test tab of the plugin press '
  '‘Restart service’”; V2 = 1 “service no longer queries – last query <v3.t>; '
  'on the Settings tab of the plugin check ‘Plugin switched on’, otherwise '
  '‘Restart service’ on the Test tab”; V4 = 0 “apcupsd does not answer: <v5> – '
  'on the Test tab of the plugin press ‘Check apcupsd’”; V6 = 0 “apcupsd '
  'cannot reach the UPS (cable?) – <v7>”; without condition “OK – UPS reports '
  '<v7>, last query <v3.t>”'),
 ('LOXONE.S1_36_NAME',
  'USV-Abfrage',
  'USV-Abfrage'),
 ('LOXONE.S2_01_PARAM',
  'Akkuladung in % (zweite Instanz, auch auf Seite „APC-UPS NG“); Statistik ein',
  'battery charge in % (second instance, also on page “APC-UPS NG”); '
  'statistics on'),
 ('LOXONE.S2_02_PARAM',
  'Auslastung der USV in %',
  'load of the UPS in %'),
 ('LOXONE.S2_03_PARAM',
  'Last in W, gerechnet aus Auslastung und Nennleistung; bleibt 0, wenn die '
  'USV keine Nennleistung meldet; Statistik ein',
  'load in W, calculated from load and rated power; stays 0 if the UPS reports '
  'no rated power; statistics on'),
 ('LOXONE.S2_04_PARAM',
  'Nennleistung der USV in W',
  'rated power of the UPS in W'),
 ('LOXONE.S2_05_PARAM',
  'Netzspannung in V; Statistik ein',
  'mains voltage in V; statistics on'),
 ('LOXONE.S2_06_PARAM',
  'Spannung am USV-Ausgang in V',
  'voltage at the UPS output in V'),
 ('LOXONE.S2_07_PARAM',
  'Netzfrequenz in Hz; nicht jedes Modell liefert sie (dann 0)',
  'mains frequency in Hz; not every model provides it (then 0)'),
 ('LOXONE.S2_08_PARAM',
  'Akkuspannung in V',
  'battery voltage in V'),
 ('LOXONE.S2_09_PARAM',
  'Nennspannung des Akkus in V',
  'nominal voltage of the battery in V'),
 ('LOXONE.S2_10_PARAM',
  'Innentemperatur in °C; nicht jedes Modell liefert sie (dann 0); Statistik '
  'ein',
  'internal temperature in °C; not every model provides it (then 0); '
  'statistics on'),
 ('LOXONE.S2_11_PARAM',
  'Akkualter in Monaten aus dem Einbaudatum; 0, wenn das Datum fehlt oder '
  'zweideutig ist',
  'battery age in months from the installation date; 0 if the date is missing '
  'or ambiguous'),
 ('LOXONE.S2_12_PARAM',
  '1 = die USV meldet „Akku tauschen“ (zweite Instanz, auch auf Seite „APC-UPS '
  'NG“)',
  '1 = the UPS reports “replace battery” (second instance, also on page '
  '“APC-UPS NG”)'),
 ('LOXONE.S2_13_PARAM',
  'Zahl der Umschaltungen auf Akku (Zählerstand von apcupsd)',
  'number of transfers to battery (counter reading of apcupsd)'),
 ('LOXONE.S2_14_PARAM',
  'Sekunden auf Akku insgesamt',
  'seconds on battery in total'),
 ('LOXONE.S2_15_PARAM',
  'Abschaltschwelle von apcupsd: Ladung in %',
  'shutdown threshold of apcupsd: charge in %'),
 ('LOXONE.S2_16_PARAM',
  'Abschaltschwelle von apcupsd: Restlaufzeit in Minuten',
  'shutdown threshold of apcupsd: runtime left in minutes'),
 ('LOXONE.S2_17_PARAM',
  'Zeitlimit von apcupsd im Akkubetrieb in s; 0 = kein Zeitlimit',
  'time limit of apcupsd on battery in s; 0 = no time limit'),
 ('LOXONE.S2_18_PARAM',
  '1 = Netzbetrieb (auch während die USV die Spannung anhebt oder absenkt)',
  '1 = on mains (also while the UPS raises or lowers the voltage)'),
 ('LOXONE.S2_19_PARAM',
  'Modell der USV; Titel genau so (Name, den das MQTT-Gateway vergibt)',
  'model of the UPS; title exactly like this (the name the MQTT gateway '
  'assigns)'),
 ('LOXONE.S2_20_PARAM',
  'Seriennummer der USV; Titel genau so',
  'serial number of the UPS; title exactly like this'),
 ('LOXONE.S2_21_PARAM',
  'Einbaudatum des Akkus, wie die USV es speichert; Titel genau so',
  'installation date of the battery, as the UPS stores it; title exactly like '
  'this'),
 ('LOXONE.S2_22_PARAM',
  'Ergebnis des letzten Selbsttests, wie apcupsd es meldet (Kürzel); Titel '
  'genau so',
  'result of the last self-test, as apcupsd reports it (abbreviation); title '
  'exactly like this'),
 ('LOXONE.S2_23_PARAM',
  'Abstand der automatischen Selbsttests, wie apcupsd es meldet; Titel genau so',
  'interval of the automatic self-tests, as apcupsd reports it; title exactly '
  'like this'),
 ('LOXONE.S2_24_PARAM',
  'Grund der letzten Umschaltung auf Akku, wie apcupsd es meldet; Titel genau '
  'so',
  'reason for the last transfer to battery, as apcupsd reports it; title '
  'exactly like this'),
 ('LOXONE.S2_25_PARAM',
  'Ein 80 / Aus 70 (Prozent)',
  'On 80 / Off 70 (percent)'),
 ('LOXONE.S2_25_NAME',
  'USV überlastet',
  'USV überlastet'),
 ('LOXONE.S2_26_PARAM',
  '60 s (zwei Abfragen)',
  '60 s (two queries)'),
 ('LOXONE.S2_26_NAME',
  'Überlast länger',
  'Überlast länger'),
 ('LOXONE.S2_27_PARAM',
  'Text: USV – Auslastung seit einer Minute über 80 %; bei Stromausfall reicht '
  'der Akku dann deutlich kürzer, bei Überlast schaltet die USV ab. Geräte vom '
  'USV-Ausgang nehmen',
  'text: UPS – load for one minute above 80 %; on a power failure the battery '
  'then lasts much shorter, on overload the UPS switches off. Remove devices '
  'from the UPS output'),
 ('LOXONE.S2_27_NAME',
  'USV überlastet',
  'USV überlastet'),
 ('LOXONE.S2_28_PARAM',
  'Ein 40 / Aus 35 (°C)',
  'On 40 / Off 35 (°C)'),
 ('LOXONE.S2_28_NAME',
  'USV zu warm',
  'USV zu warm'),
 ('LOXONE.S2_29_PARAM',
  '600 s',
  '600 s'),
 ('LOXONE.S2_29_NAME',
  'Wärme länger',
  'Wärme länger'),
 ('LOXONE.S2_30_PARAM',
  'Text: USV – Innentemperatur seit 10 Minuten über 40 °C; Lüftung und '
  'Aufstellort prüfen, Wärme verkürzt die Lebensdauer des Akkus',
  'text: UPS – internal temperature above 40 °C for 10 minutes; check '
  'ventilation and location, heat shortens the life of the battery'),
 ('LOXONE.S2_30_NAME',
  'USV zu warm',
  'USV zu warm'),
 ('LOXONE.S2_31_PARAM',
  'Ein 80 / Aus 95 (Prozent; schaltet beim Unterschreiten von 80 ein, über 95 '
  'wieder aus)',
  'On 80 / Off 95 (percent; switches on when falling below 80, off again above '
  '95)'),
 ('LOXONE.S2_31_NAME',
  'Akku nicht voll',
  'Akku nicht voll'),
 ('LOXONE.S2_32_PARAM',
  '— (nicht voll, obwohl Netz da)',
  '— (not full although mains power is there)'),
 ('LOXONE.S2_32_NAME',
  'Akku lädt nicht',
  'Akku lädt nicht'),
 ('LOXONE.S2_33_PARAM',
  '21600 s',
  '21600 s'),
 ('LOXONE.S2_33_NAME',
  'Akku lädt seit 6 Stunden nicht',
  'Akku lädt seit 6 Stunden nicht'),
 ('LOXONE.S2_34_PARAM',
  'Text: USV – der Akku ist seit 6 Stunden unter 80 %, obwohl das Netz da ist; '
  'in der App „USV Akku“ lesen, im Plugin Reiter Test „Letzte Werte“ ansehen, '
  'Akku prüfen oder tauschen',
  'text: UPS – for 6 hours the battery has been below 80 % although mains '
  'power is there; read “USV Akku” in the app, look at “Last values” on the '
  'Test tab of the plugin, check or replace the battery'),
 ('LOXONE.S2_34_NAME',
  'USV Akku lädt nicht',
  'USV Akku lädt nicht'),
 ('LOXONE.S2_35_PARAM',
  'Zu bestimmter Uhrzeit, 00:00:00',
  'at a specific time, 00:00:00'),
 ('LOXONE.S2_35_NAME',
  'Tagesbeginn 0:00',
  'Tagesbeginn 0:00'),
 ('LOXONE.S2_36_PARAM',
  'übernimmt um 0:00 den Zählerstand',
  'takes over the counter reading at 0:00'),
 ('LOXONE.S2_36_NAME',
  'Umschaltungen bis heute früh',
  'Umschaltungen bis heute früh'),
 ('LOXONE.S2_37_PARAM',
  'IF(I2>0;IF(I1>=I2;I1-I2;I1);0) – Zählerstand minus Stand um Mitternacht; '
  'nach einem Neustart von apcupsd zählt er von vorn, nach einem Neustart des '
  'Miniservers bis Mitternacht 0',
  'IF(I2>0;IF(I1>=I2;I1-I2;I1);0) – counter reading minus reading at midnight; '
  'after a restart of apcupsd it counts from zero, after a restart of the '
  'Miniserver 0 until midnight'),
 ('LOXONE.S2_37_NAME',
  'Umschaltungen heute',
  'Umschaltungen heute'),
 ('LOXONE.S2_38_PARAM',
  'Ein 5 / Aus 1 (Umschaltungen am Tag)',
  'On 5 / Off 1 (transfers per day)'),
 ('LOXONE.S2_38_NAME',
  'Netz unruhig',
  'Netz unruhig'),
 ('LOXONE.S2_39_PARAM',
  'Text: USV – heute schon 5 Umschaltungen auf Akku, das Netz hat '
  'Spannungseinbrüche; jede Umschaltung kostet den Akku. In der App „USV Netz '
  'und Last“ den Grund lesen',
  'text: UPS – already 5 transfers to battery today, the mains has voltage '
  'dips; every transfer costs the battery. Read the reason in “USV Netz und '
  'Last” in the app'),
 ('LOXONE.S2_39_NAME',
  'USV Netz unruhig',
  'USV Netz unruhig'),
 ('LOXONE.S2_40_PARAM',
  'Zeilen: V1 = 1 „Akku tauschen – die USV meldet einen verbrauchten Akku '
  '(eingebaut <v4>)“; V3 >= 48 „Akku <v3.0> Monate alt (eingebaut <v4>) – '
  'Ersatz einplanen; Ladung <v2.0> %“; ohne Bedingung „Ladung <v2.0> %, <v5.1> '
  'V (Nennspannung <v6.0> V), eingebaut <v4>, letzter Selbsttest <v7>, '
  'insgesamt <v8.0> s auf Akku“',
  'rows: V1 = 1 “replace battery – the UPS reports a worn battery (installed '
  '<v4>)”; V3 >= 48 “battery <v3.0> months old (installed <v4>) – plan a '
  'replacement; charge <v2.0> %”; without condition “charge <v2.0> %, <v5.1> V '
  '(nominal voltage <v6.0> V), installed <v4>, last self-test <v7>, <v8.0> s '
  'on battery in total”'),
 ('LOXONE.S2_40_NAME',
  'USV Akku',
  'USV Akku'),
 ('LOXONE.S2_41_PARAM',
  'Zeilen: V4 >= 80 „überlastet: <v4.0> % (<v5.0> W von <v6.0> W) – Geräte vom '
  'USV-Ausgang nehmen“; ohne Bedingung „Netz <v1.0> V / <v2.1> Hz, Ausgang '
  '<v3.0> V, Last <v4.0> % (<v5.0> W von <v6.0> W); heute <v7.0> '
  'Umschaltungen, zuletzt wegen: <v8>“',
  'rows: V4 >= 80 “overloaded: <v4.0> % (<v5.0> W of <v6.0> W) – remove '
  'devices from the UPS output”; without condition “mains <v1.0> V / <v2.1> '
  'Hz, output <v3.0> V, load <v4.0> % (<v5.0> W of <v6.0> W); today <v7.0> '
  'transfers, last because of: <v8>”'),
 ('LOXONE.S2_41_NAME',
  'USV Netz und Last',
  'USV Netz und Last'),
 ('LOXONE.S2_42_PARAM',
  'Zeilen: V4 = 0 und V5 = 0 „<v1> (Nr. <v2>) – die USV meldet keine '
  'Abschaltschwellen, die Vorwarnung (Stufe 2) kommt deshalb nie; Selbsttest: '
  '<v3>“; V6 > 0 „<v1> (Nr. <v2>) – apcupsd schaltet ab bei <v4.0> % Ladung, '
  '<v5.0> min Restzeit oder nach <v6.0> s auf Akku; Selbsttest: <v3>“; ohne '
  'Bedingung „<v1> (Nr. <v2>) – apcupsd schaltet ab bei <v4.0> % Ladung oder '
  '<v5.0> min Restzeit; Selbsttest: <v3>“',
  'rows: V4 = 0 and V5 = 0 “<v1> (no. <v2>) – the UPS reports no shutdown '
  'thresholds, so the advance warning (level 2) never comes; self-test: <v3>”; '
  'V6 > 0 “<v1> (no. <v2>) – apcupsd shuts down at a charge of <v4.0> %, '
  '<v5.0> min runtime left or after <v6.0> s on battery; self-test: <v3>”; '
  'without condition “<v1> (no. <v2>) – apcupsd shuts down at <v5.0> min '
  'runtime left or a charge of <v4.0> %; self-test: <v3>”'),
 ('LOXONE.S2_42_NAME',
  'USV Gerät',
  'USV Gerät'),
 ('LOXONE.TYP_VI',
  'Virtueller HTTP-Eingang (Vorlage „%s“)',
  'Virtual HTTP input (template “%s”)'),
 ('LOXONE.T_TEXTEIN',
  'Virtueller Texteingang',
  'Virtual text input'),
 ('LOXONE.T_EVZ',
  'Einschaltverzögerung',
  'On-delay'),
 ('LOXONE.T_NICHT',
  'NICHT',
  'NOT'),
 ('LOXONE.T_ODER',
  'ODER',
  'OR'),
 ('LOXONE.T_UND',
  'UND',
  'AND'),
 ('LOXONE.T_BENACHR',
  'Benachrichtigung',
  'Notification'),
 ('LOXONE.T_SCHWELL',
  'Schwellwertschalter',
  'Threshold switch'),
 ('LOXONE.T_MERKER',
  'Merker (Visu)',
  'Memory flag (visualisation)'),
 ('LOXONE.T_STATUS',
  'Status',
  'Status'),
 ('LOXONE.T_KONSTANTE',
  'Konstante',
  'Constant'),
 ('LOXONE.T_VALID',
  'Analogwertvalidierung',
  'Analog value validation'),
 ('LOXONE.T_FLANKE',
  'Flankenerkennung',
  'Edge detection'),
 ('LOXONE.T_IMPULS',
  'Impuls um',
  'Pulse at'),
 ('LOXONE.T_SPEICHER',
  'Analogspeicher',
  'Analog memory'),
 ('LOXONE.T_FORMEL',
  'Formel',
  'Formula'),
 ('LOXONE.E_EIN',
  'Eingang = #%d',
  'Input = #%d'),
 ('LOXONE.E_AUSGANG',
  'Ausgang %s von #%d',
  'output %s of #%d'),
 ('LOXONE.E_EIN_AUSGANG',
  'Eingang = Ausgang %s von #%d',
  'Input = output %s of #%d'),
 ('LOXONE.E_GATEWAY',
  '— (kommt über das Gateway)',
  '— (arrives via the gateway)'),
 ('LOXONE.SCHRITTE_TITEL',
  'So übernehmen Sie diese Seite',
  'How to take over this page'),
 ('LOXONE.HINWEISE_TITEL',
  'Hinweise',
  'Notes'),
 ('LOXONE.BL_S1',
  'Zustand, Störung und Stromausfall',
  'State, faults and power failure'),
 ('LOXONE.BL_S2',
  'Akku, Netz und Last',
  'Battery, mains and load'),
 ('LOXONE.S1_SCHRITT1',
  'apcupsd muss laufen und die USV sehen. Im Plugin Reiter „%s“ → „%s“: kommen '
  'Werte, ist der schwierige Teil erledigt. Im Reiter „%s“ „%s“ setzen, die '
  'Vorwarnung prüfen (ab Werk 5 Minuten bzw. 10 Prozentpunkte über der '
  'Abschaltschwelle) und speichern.',
  'apcupsd must be running and see the UPS. In the plugin, tab “%s” → “%s”: if '
  'values arrive, the hard part is done. On the tab “%s” tick “%s”, check the '
  'advance warning (by default 5 minutes or 10 percentage points above the '
  'shutdown threshold) and save.'),
 ('LOXONE.S1_SCHRITT2',
  'LoxBerry → MQTT Gateway: das Abo %s trägt das Plugin selbst ein (Schritt 2 '
  'oben sagt, was bei Ihrem Gateway gilt). Gateway V2: unter %s die '
  'Datenpunkte anhaken, auch status, event und last_error.',
  'LoxBerry → MQTT Gateway: the plugin enters the subscription %s itself (step '
  '2 above says what applies to your gateway). Gateway V2: tick the data '
  'points under %s, including status, event and last_error.'),
 ('LOXONE.S1_SCHRITT3',
  'Oben in diesem Reiter (Schritt 3) „%s“ drücken. In Loxone Config: '
  'Peripherie → Virtuelle Eingänge → Vorlage importieren → %s. Nur EINMAL '
  'einlesen (zweimal ergibt doppelte Bausteine). Die Vorlage für den alten '
  'XML-Weg NICHT dazu einlesen – sie liefert fünf der Werte ein zweites Mal.',
  'Above on this tab (step 3) press “%s”. In Loxone Config: Periphery → '
  'Virtual Inputs → import template → %s. Import it only ONCE (twice gives '
  'duplicate blocks). Do NOT import the template for the old XML path as well '
  '– it delivers five of the values a second time.'),
 ('LOXONE.S1_SCHRITT4',
  'Drei Virtuelle Texteingänge anlegen (Peripherie → Virtuelle Eingänge → '
  'Virtueller Texteingang), Name genau so: %s, %s, %s; „In Visualisierung '
  'verwenden“ an. So benennt das MQTT-Gateway die Werte (mit dem Themenpräfix '
  'aus dem Reiter MQTT) – ein anderer Name bekommt nie einen Wert.',
  'Create three virtual text inputs (Periphery → Virtual Inputs → Virtual text '
  'input), name exactly like this: %s, %s, %s; “Use in visualisation” on. This '
  'is how the MQTT gateway names the values (with the topic prefix from the '
  'MQTT tab) – any other name never gets a value.'),
 ('LOXONE.S1_SCHRITT5',
  'Seite „APC-UPS NG“ anlegen. Aus „%s“ ziehen: %s; dazu die drei Texteingänge '
  'und die Konstante 1.',
  'Create the page “APC-UPS NG”. Drag from “%s”: %s; in addition the three '
  'text inputs and the constant 1.'),
 ('LOXONE.S1_SCHRITT6',
  'Fünf Benachrichtigungen anlegen (Peripherie → Mitteilungen → '
  'Benachrichtigung): „USV-Meldung“, „USV Akku tauschen“, „USV Netz wieder '
  'da“, „USV Akku bald leer“, „USV Abschaltung“, Texte wie in der Liste, und '
  'auf die Seite ziehen. Jede bekommt genau eine Leitung.',
  'Create five notifications (Periphery → Messages → Notification): '
  '“USV-Meldung”, “USV Akku tauschen”, “USV Netz wieder da”, “USV Akku bald '
  'leer”, “USV Abschaltung”, texts as in the list, and drag them onto the '
  'page. Each gets exactly one connection.'),
 ('LOXONE.S1_SCHRITT7',
  'Merker „Stromsparen aktiv“ anlegen (im Baum „Merker“ wählen, im Menüband '
  '„Merker“, auf die Seite klicken).',
  'Create the memory flag “Stromsparen aktiv” (select “Memory flags” in the '
  'tree, “Memory flag” in the ribbon, click on the page).'),
 ('LOXONE.S1_SCHRITT8',
  'Die übrigen Bausteine über die Baustein-Suche (Taste F5) setzen, Parameter '
  'wie in der Liste, nach der Spalte „%s“ von oben nach unten verbinden. '
  'Status-Eingänge ab V5 erscheinen erst nach Klick auf das „+“ am Baustein: '
  '„USV-Abfrage“ dreimal (V5–V7), „USV-Zustand“ zweimal (V5/V6). ODER und UND '
  'haben je zwei Eingänge. Die Zeilen der Status-Bausteine stehen in der '
  'Spalte „%s“ und werden von Hand eingetragen – in der angegebenen '
  'Reihenfolge, die Zeile ohne Bedingung zuletzt.',
  'Place the remaining blocks via the block search (key F5), parameters as in '
  'the list, and wire them from top to bottom according to the column “%s”. '
  'Status inputs from V5 only appear after clicking the “+” on the block: '
  '“USV-Abfrage” three times (V5–V7), “USV-Zustand” twice (V5/V6). OR and AND '
  'have two inputs each. The rows of the status blocks are in the column “%s” '
  'and are entered by hand – in the given order, the row without condition '
  'last.'),
 ('LOXONE.S1_SCHRITT9',
  'Speichern und in den Miniserver übertragen. Probe: %s ändert sich alle 30 '
  's; der Status „USV-Abfrage“ zeigt „in Ordnung – USV meldet ONLINE …“; im '
  'Plugin Reiter „%s“ → „%s“ steht dieselbe Ladung wie in Loxone.',
  'Save and transfer to the Miniserver. Test: %s changes every 30 s; the '
  'status “USV-Abfrage” shows “OK – UPS reports ONLINE …”; in the plugin, tab '
  '“%s” → “%s” shows the same charge as Loxone.'),
 ('LOXONE.S1_H1',
  'Zu #8: Die Einschaltverzögerung fängt den kurzen Netzwischer ab. Ohne sie '
  'meldet das Haus jeden Spannungseinbruch von zwei Sekunden.',
  'On #8: the on-delay absorbs short mains dips. Without it the house reports '
  'every two-second voltage drop.'),
 ('LOXONE.S1_H2',
  'Zu #10 bis #12: Der Benachrichtigungs-Baustein meldet nur beim Wechsel von '
  'Aus auf Ein. „USV-Meldung“ kommt bei Stromausfall (nach 10 s), bei '
  'abgerissener Verbindung zur USV und bei gestörter Abfrage; hält eine dieser '
  'Störungen an, bleibt eine weitere stumm – das ODER davor ändert daran '
  'nichts. Eine Dauerstörung wie der Akkutausch hat deshalb eine eigene '
  'Meldung (#25), sie würde sonst jede spätere Meldung verschlucken.',
  'On #10 to #12: the notification block only reports on a change from off to '
  'on. “USV-Meldung” comes on a power failure (after 10 s), on a lost '
  'connection to the UPS and on a disturbed query; while one of these faults '
  'persists, another one stays silent – the OR in front of it does not change '
  'that. A permanent fault such as the battery replacement therefore has its '
  'own notification (#25); otherwise it would swallow every later message.'),
 ('LOXONE.S1_H3',
  'Zu #13 und #14: Lastabwurf ab Stufe 2 (Vorwarnung). Den Merker „Stromsparen '
  'aktiv“ im eigenen Projekt an die Verbraucher legen, die bei knappem Akku '
  'aus sollen – erst Komfort, dann Nebenräume. Kennt die USV keine '
  'Abschaltschwellen, kommt Stufe 2 nie; auf der Seite „APC-UPS NG Akku und '
  'Netz“ sagt es der Status „USV Gerät“.',
  'On #13 and #14: load shedding from level 2 (advance warning). In your own '
  'project connect the memory flag “Stromsparen aktiv” to the loads that '
  'should switch off when the battery runs low – comfort first, then side '
  'rooms. If the UPS knows no shutdown thresholds, level 2 never comes; on the '
  'page “APC-UPS NG Akku und Netz” the status “USV Gerät” says so.'),
 ('LOXONE.S1_H4',
  'Zu #6 und #19: Loxone rechnet in Sekunden seit 2009, dieses Thema in '
  'Sekunden seit 1970. Die Analogwertvalidierung braucht den Wert nicht '
  'umzurechnen, sie prüft nur, ob er sich ändert, und bekommt an En die '
  'Konstante 1. Tmc ist das Fünffache des Abfragetakts: wer „%s“ ändert, setzt Tmc '
  'auf das Fünffache des neuen Werts.',
  'On #6 and #19: Loxone counts seconds since 2009, this topic seconds since '
  '1970. The analog value validation does not need to convert the value, it '
  'only checks whether it changes, and gets the constant 1 at En. Tmc is '
  'five times the query interval: whoever changes “%s” sets Tmc to five times '
  'the new value.'),
 # 1.2.22 (Welle Bild 14, 16.10.2026): Config legt En der Analogwertvalidierung negiert an;
 # Hinweis im Kasten der Seite APC-UPS NG hinter S1_H4 (index.php), maskiert, ohne Platzhalter.
 ('LOXONE.S1_H9',
  'Zu #19: Config legt den Eingang En negiert an (Haken bei ‚En‘ im '
  'Eigenschaftsfenster unter Parameter). Diesen Haken entfernen, sonst kommt '
  'die Konstante 1 als 0 an und die Ausfallmeldung löst nie aus.',
  'On #19: Config creates input En inverted (tick at ‚En‘ in the properties '
  'under Parameters). Remove this tick, otherwise constant 1 arrives as 0 and '
  'the failure message never triggers.'),
 ('LOXONE.S1_H5',
  'Zu #32: Hängt die USV am LoxBerry selbst, fährt apcupsd den LoxBerry '
  'herunter – danach kommt vom Plugin nichts mehr, bis er wieder läuft. Die '
  'Meldung geht vorher hinaus.',
  'On #32: if the UPS is connected to the LoxBerry itself, apcupsd shuts the '
  'LoxBerry down – after that nothing comes from the plugin until it runs '
  'again. The notification goes out before.'),
 ('LOXONE.S1_H6',
  'Zu #33 bis #35: Die Virtuellen Texteingänge stehen in keiner Vorlage. '
  'Peripherie → Virtuelle Eingänge → Virtueller Texteingang, Name genau wie in '
  'der Spalte „%s“ – den Namen vergibt das MQTT-Gateway.',
  'On #33 to #35: the virtual text inputs are in no template. Periphery → '
  'Virtual Inputs → Virtual text input, name exactly as in the column “%s” – '
  'the MQTT gateway assigns the name.'),
 ('LOXONE.S1_H7',
  'Die Vorlage für den alten XML-Weg nicht zusätzlich zur MQTT-Vorlage '
  'einlesen – sie liefert fünf der Werte ein zweites Mal.',
  'Do not import the template for the old XML path in addition to the MQTT '
  'template – it delivers five of the values a second time.'),
 ('LOXONE.S1_H8',
  'Die LoxBerry-Benachrichtigung des Plugins (Glocke, E-Mail) läuft daneben '
  'weiter; wer nur die Loxone-App will, schaltet sie im Reiter „%s“ unter „%s“ '
  'ab.',
  'The LoxBerry notification of the plugin (bell, email) keeps running '
  'alongside; if you only want the Loxone app, switch it off on the tab “%s” '
  'under “%s”.'),
 ('LOXONE.S2_SCHRITT1',
  'Seite „APC-UPS NG“ zuerst übernehmen (Vorlage und Gateway wie dort, '
  'Schritte 1–3).',
  'Take over the page “APC-UPS NG” first (template and gateway as there, steps '
  '1–3).'),
 ('LOXONE.S2_SCHRITT2',
  'Sechs Virtuelle Texteingänge anlegen (Peripherie → Virtuelle Eingänge → '
  'Virtueller Texteingang), Name genau so: %s, %s, %s, %s, %s, %s; „In '
  'Visualisierung verwenden“ an. Gateway V2: diese Datenpunkte ebenfalls '
  'anhaken.',
  'Create six virtual text inputs (Periphery → Virtual Inputs → Virtual text '
  'input), name exactly like this: %s, %s, %s, %s, %s, %s; “Use in '
  'visualisation” on. Gateway V2: tick these data points as well.'),
 ('LOXONE.S2_SCHRITT3',
  'Neue Seite „APC-UPS NG Akku und Netz“. Aus „%s“ die 18 Eingänge der Liste '
  '(Nr. 1–18) ziehen – %s und %s ein zweites Mal, nicht neu anlegen. Bei %s, '
  '%s, %s und %s im Eigenschaftsfenster „Statistik“ einschalten.',
  'New page “APC-UPS NG Akku und Netz”. Drag the 18 inputs of the list (no. '
  '1–18) from “%s” – %s and %s a second time, do not create them anew. For %s, '
  '%s, %s and %s switch on “Statistics” in the properties window.'),
 ('LOXONE.S2_SCHRITT4',
  'Vier Benachrichtigungen anlegen (Peripherie → Mitteilungen → '
  'Benachrichtigung): „USV überlastet“, „USV zu warm“, „USV Akku lädt nicht“, '
  '„USV Netz unruhig“, Texte wie in der Liste. Jede bekommt genau eine Leitung.',
  'Create four notifications (Periphery → Messages → Notification): “USV '
  'überlastet”, “USV zu warm”, “USV Akku lädt nicht”, “USV Netz unruhig”, '
  'texts as in the list. Each gets exactly one connection.'),
 ('LOXONE.S2_SCHRITT5',
  'Die übrigen Bausteine über die Baustein-Suche (Taste F5) setzen, Parameter '
  'wie in der Liste, nach der Spalte „%s“ verbinden. Status-Eingänge ab V5 '
  'erscheinen erst nach Klick auf das „+“ am Baustein: „USV Akku“ und „USV '
  'Netz und Last“ viermal (V5–V8), „USV Gerät“ zweimal (V5/V6). Das UND hat '
  'zwei Eingänge. Die Zeilen der Status-Bausteine stehen in der Spalte „%s“ '
  'und werden von Hand eingetragen, die Zeile ohne Bedingung zuletzt. „Impuls '
  'um“ bleibt auf 00:00:00.',
  'Place the remaining blocks via the block search (key F5), parameters as in '
  'the list, and wire them according to the column “%s”. Status inputs from V5 '
  'only appear after clicking the “+” on the block: “USV Akku” and “USV Netz '
  'und Last” four times (V5–V8), “USV Gerät” twice (V5/V6). The AND has two '
  'inputs. The rows of the status blocks are in the column “%s” and are '
  'entered by hand, the row without condition last. “Pulse at” stays at '
  '00:00:00.'),
 ('LOXONE.S2_SCHRITT6',
  'Speichern und übertragen. Probe: „USV Gerät“ zeigt Modell und '
  'Abschaltschwellen; „USV Netz und Last“ zeigt dieselbe Netzspannung wie im '
  'Plugin Reiter „%s“ → „%s“.',
  'Save and transfer. Test: “USV Gerät” shows model and shutdown thresholds; '
  '“USV Netz und Last” shows the same mains voltage as the plugin, tab “%s” → '
  '“%s”.'),
 ('LOXONE.S2_H1',
  'Schwellen nach der eigenen USV wählen: Überlast 80/70 %, zu warm 40/35 °C, '
  '„Akku lädt nicht“ 6 Stunden unter 80 %. Liefert die USV keine Temperatur '
  'oder keine Netzfrequenz, steht dort 0 – dann wirkt die Meldung „zu warm“ '
  'nie.',
  'Choose the thresholds for your own UPS: overload 80/70 %, too warm 40/35 '
  '°C, “Akku lädt nicht” 6 hours below 80 %. If the UPS provides no '
  'temperature or no mains frequency, 0 stands there – then the notification '
  '“zu warm” never triggers.'),
 ('LOXONE.S2_H2',
  'Statistik ist eine Eigenschaft des Eingangs im Baum – sie gilt dann auch '
  'für %s auf der Seite „APC-UPS NG“.',
  'Statistics is a property of the input in the tree – it then also applies to '
  '%s on the page “APC-UPS NG”.'),
 ('LOXONE.S2_H3',
  'Akkualter: ab 48 Monaten zeigt „USV Akku“ „Ersatz einplanen“; eine eigene '
  'Meldung gibt es bewusst nicht. Nach einem Akkutausch das Einbaudatum in der '
  'USV neu setzen (apcupsd-Programm apctest), sonst zählt das Alter weiter.',
  'Battery age: from 48 months “USV Akku” shows that a replacement should be '
  'planned; there is deliberately no notification of its own. After replacing '
  'the battery set the installation date in the UPS anew (apcupsd program '
  'apctest), otherwise the age keeps counting.'),
 ('LOXONE.S2_H4',
  '„Umschaltungen heute“ zählt ab Mitternacht. Nach einem Neustart des '
  'Miniservers steht sie bis zur nächsten Mitternacht auf 0; nach einem '
  'Neustart von apcupsd zählt apcupsd von vorn.',
  '“Umschaltungen heute” counts from midnight. After a restart of the '
  'Miniserver it stays at 0 until the next midnight; after a restart of '
  'apcupsd, apcupsd counts from zero.'),
 ('LOXONE.S2_H5',
  'Selbsttest und Grund der letzten Umschaltung stehen so da, wie apcupsd sie '
  'meldet (Kürzel, englisch) – das Plugin übersetzt sie nicht.',
  'Self-test and reason for the last transfer appear as apcupsd reports them '
  '(abbreviations, English) – the plugin does not translate them.'),
 ('LOXONE.SCHRITT7', 'Schritt 7: Gegenprobe', 'Step 7: verification'),
 ('LOXONE.SCHRITT7_TEXT',
  'Im MQTT-Gateway unter <i>Incoming overview</i> nachsehen: dort müssen die '
  'Themen mit dem Präfix erscheinen, sobald der Dienst einmal gesendet hat. '
  'Erscheinen sie dort nicht, fehlt das Abo aus Schritt 2 — dann ist alles '
  'Weitere in Loxone vergeblich. Erscheinen sie dort, aber nicht in Loxone, '
  'stimmen die Namen der virtuellen Eingänge nicht.',
  'Check <i>Incoming overview</i> in the MQTT gateway: the topics with the prefix '
  'must appear there as soon as the service has sent once. If they do not appear, '
  'the subscription from step 2 is missing — then everything further in Loxone is '
  'in vain. If they appear there but not in Loxone, the names of the virtual '
  'inputs do not match.'),
 ('LOXONE.ALTER_WEG', 'Der alte XML-Weg bleibt erhalten',
                      'The old XML path remains available'),
 ('LOXONE.ALTER_WEG_TEXT',
  'Die Originalfassung stellte unter dieser Adresse eine XML-Seite bereit, die '
  'Loxone selbst abholt. Sie bleibt unverändert, damit bestehende Anlagen '
  'weiterlaufen. Seit 1.2.0 beachtet sie auch die Einstellung <i>USV auf einem '
  'anderen Rechner</i> und liefert zusätzlich zu den Rohfeldern die abgeleiteten '
  'Werte im Block <span class=\'sm-mono\'>CALC</span> — dieselben, die über MQTT '
  'hinausgehen, samt ihrem Alter in Sekunden. Seit 1.2.14 stehen am Anfang des '
  'Blocks <span class=\'sm-mono\'>OK</span> und <span class=\'sm-mono\'>ALTER</span>: '
  'OK fällt auf 0, sobald die Werte älter sind als das Dreifache des '
  'Abfragetakts — etwa weil der Dienst steht; ALTER nennt dieses Alter in '
  'Sekunden.',
  'The original version provided an XML page at this address which Loxone fetches '
  'itself. It stays unchanged so that existing installations keep working. Since '
  '1.2.0 it also honours the setting <i>UPS on another machine</i> and, in '
  'addition to the raw fields, provides the derived values in a '
  '<span class=\'sm-mono\'>CALC</span> block — the same ones sent over MQTT, '
  'together with their age in seconds. Since 1.2.14 the block starts with '
  '<span class=\'sm-mono\'>OK</span> and <span class=\'sm-mono\'>ALTER</span>: OK '
  'drops to 0 as soon as the values are older than three times the query '
  'interval — for instance because the service has stopped; ALTER gives that '
  'age in seconds.'),
 ('LOXONE.ALTER_WEG_ADRESSE',
  'Der Rechnername ist ein Vorschlag. Bitte prüfen, unter welchem Namen der '
  'Miniserver den LoxBerry wirklich erreicht.',
  'The host name is a suggestion. Please check under which name the Miniserver '
  'actually reaches the LoxBerry.'),
 # Welle Bild (Entscheidung 45): Bild der Bausteine aus dem gemeinsamen Musterprojekt
 ('LOXONE.BILD_ALT',
  'Bausteine des Plugins in Loxone Config – Seite „%s“',
  'Plugin blocks in Loxone Config – page “%s”'),
 ('LOXONE.BILD_UNTERSCHRIFT',
  'Seite „%s“ im LoxBerry-Plugins Musterprojekt. Config kürzt lange '
  'Bausteinnamen – Namen siehe Tabelle.',
  'Page “%s” in the LoxBerry plugins sample project. Config shortens long '
  'block names – see the table for the full names.'),
 ('LOXONE.MUSTERPROJEKT',
  'Die ganze Projektdatei mit allen Plugin-Seiten und Vorlagen: '
  '<a href=\'https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt\' target=\'_blank\' rel=\'noopener\'>LoxBerry-Plugins Musterprojekt</a>',
  'The complete project file with all plugin pages and templates: '
  '<a href=\'https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt\' target=\'_blank\' rel=\'noopener\'>LoxBerry plugins sample project</a>'),
 # Welle Bild 12 VOLL (1.2.20, Entscheidung 10, Sprachregel 13.10.2026): Wurzel-Comment und
 # HintText beider Loxone-Vorlagen (ap_vorlage()); die Titel bleiben fest im Code.
 ('LOXONE.VORLAGE_FUSS',
  'Erzeugt vom LoxBerry-Plugin APC-UPS NG (%s)',
  'Created by the LoxBerry plugin APC-UPS NG (%s)'),
 ('LOXONE.VORLAGE_HINWEIS_MQTT',
  'Die Werte kommen vom MQTT-Gateway, nicht von dieser Adresse.',
  'The values come from the MQTT gateway, not from this address.'),
 ('LOXONE.VORLAGE_HINWEIS_XML',
  'Die Adresse ist ein Vorschlag – bitte prüfen, unter welchem Namen der '
  'Miniserver den LoxBerry erreicht.',
  'The address is a suggestion – please check under which name the Miniserver '
  'reaches the LoxBerry.'),

 # ---------------- LOG ----------------
 ('LOG.DATEI', 'Datei:', 'File:'),
 ('LOG.NEUESTE_OBEN', '— neueste Zeile oben.', '— newest line at the top.'),
 ('LOG.LEER', 'Es gibt noch keine Protokolldatei.', 'There is no log file yet.'),

 # ---------------- TEST: Selbstpruefung ----------------
 ('TEST.SELBSTPRUEFUNG', 'Selbstprüfung', 'Self-check'),
 ('TEST.SELBSTPRUEFUNG_HILFE',
  'Diese Zeilen beantworten <b>ohne Loxone</b>, ob die Einrichtung trägt. Ein '
  'Punkt statt Haken oder Kreuz heißt: die Frage lässt sich hier nicht '
  'beantworten — er zählt weder als bestanden noch als durchgefallen.',
  'These lines answer <b>without Loxone</b> whether the setup works. A dot '
  'instead of a tick or a cross means the question cannot be answered here — it '
  'counts neither as passed nor as failed.'),
 ('TEST.BILANZ', '%d von %d beantwortbaren Fragen in Ordnung, %d Kreuze.',
                 '%d of %d answerable questions are fine, %d crosses.'),
 ('TEST.SELBSTPRUEFUNG_LADEN',
  'Die Selbstprüfung ruft systemctl auf, startet Python und fragt den eigenen '
  'Endpunkt über HTTP ab. Sie läuft deshalb nicht bei jedem Seitenaufbau mit, '
  'sondern erst, wenn dieser Reiter wirklich geöffnet wird.',
  'The self-check calls systemctl, starts Python and queries the plugin endpoint '
  'over HTTP. It therefore does not run on every page load, but only when this '
  'tab is actually opened.'),
 ('TEST.SELBSTPRUEFUNG_KNOPF', 'Selbstprüfung jetzt ausführen',
                               'Run the self-check now'),
 ('TEST.F_APCACCESS', 'Ist apcaccess vorhanden?', 'Is apcaccess present?'),
 ('TEST.A_APCACCESS_FEHLT', 'nicht gefunden', 'not found'),
 ('TEST.F_APCUPSD', 'Läuft der Dienst apcupsd?', 'Is the apcupsd service running?'),
 ('TEST.A_KEIN_SYSTEMCTL', 'systemctl antwortet nicht', 'systemctl does not answer'),
 ('TEST.F_ISCONFIGURED', 'Steht ISCONFIGURED auf yes?', 'Is ISCONFIGURED set to yes?'),
 ('TEST.A_DATEI_FEHLT', '/etc/default/apcupsd ist nicht lesbar',
                        '/etc/default/apcupsd is not readable'),
 ('TEST.A_ISCONF_EGAL',
  'ohne Belang, solange apcupsd läuft: die systemd-Unit liest diese Datei nicht',
  'irrelevant while apcupsd is running: the systemd unit does not read this '
  'file'),
 ('TEST.F_DIENST', 'Läuft der Dienst dieses Plugins?',
                   'Is the service of this plugin running?'),
 ('TEST.A_DIENST_TOT', 'nein — siehe Reiter Logdateien', 'no — see the Log files tab'),
 ('TEST.A_DIENST_ANGEHALTEN',
  'nein — bewusst angehalten (Knopf „Dienst anhalten“); „Dienst neu starten“ '
  'startet ihn wieder',
  'no — deliberately stopped (button “Stop service”); “Restart service” starts '
  'it again'),
 ('TEST.F_FRISCH', 'Sind die Werte frisch?', 'Are the values fresh?'),
 ('TEST.A_ALTER', '%d Sekunden alt, erlaubt sind %d',
                  '%d seconds old, allowed are %d'),
 ('TEST.A_KEINE_DATEI', 'Es gibt noch keine Zustandsdatei.',
                        'There is no state file yet.'),
 ('TEST.F_VERBINDUNG', 'Antwortet die USV wirklich?', 'Is the UPS really answering?'),
 ('TEST.A_COMMLOST',
  '%s — apcupsd erreicht die USV nicht, die Zahlen sind wertlos',
  '%s — apcupsd cannot reach the UPS, the numbers are worthless'),
 ('TEST.A_NOCH_KEINE_WERTE', 'Es liegen noch keine Werte vor.',
                             'There are no values yet.'),
 ('TEST.F_SCHWELLEN', 'Kennt das Plugin die Abschaltschwellen?',
                      'Does the plugin know the shutdown thresholds?'),
 ('TEST.A_SCHWELLEN', 'ab %s %% Ladung bzw. %s Minuten Restlaufzeit',
                      'from %s %% charge or %s minutes runtime'),
 ('TEST.A_SCHWELLEN_FEHLEN',
  'Diese USV meldet sie nicht — alarm_level bleibt deshalb bei höchstens 1',
  'This UPS does not report them — alarm_level therefore stays at 1 at most'),
 ('TEST.F_BROKER', 'Ist ein MQTT-Broker eingetragen?', 'Is an MQTT broker configured?'),
 ('TEST.A_KEIN_BROKER', 'in general.json steht keiner', 'none in general.json'),
 ('TEST.A_MQTT_AUS', 'MQTT ist ausgeschaltet', 'MQTT is switched off'),
 ('TEST.F_AUTOSTART', 'Startet der MQTT-Gateway selbst?',
                      'Does the MQTT gateway start by itself?'),
 ('TEST.F_PAHO', 'Ist die MQTT-Bibliothek für Python da?',
                 'Is the MQTT library for Python present?'),
 ('TEST.F_THEMENDATEI', 'Ist die Themenliste lesbar?', 'Is the topic list readable?'),
 ('TEST.A_THEMENDATEI', '%d Themen aus %s', '%d topics from %s'),
 ('TEST.A_THEMENDATEI_FEHLT', '%s fehlt oder ist unlesbar',
                              '%s is missing or unreadable'),
 ('TEST.F_KONGRUENZ', 'Meinen Liste, Dienst und Oberfläche dieselben Themen?',
                      'Do list, service and interface mean the same topics?'),
 ('TEST.TH_OK', 'ja, %d Themen auf allen drei Seiten',
                'yes, %d topics on all three sides'),
 ('TEST.TH_ABWEICHUNG', 'nein — abweichend: %s', 'no — differing: %s'),
 ('TEST.TH_KEIN_SKRIPT', 'apc_lesen.py nicht gefunden: %s',
                         'apc_lesen.py not found: %s'),
 ('TEST.TH_UNLESBAR', 'die Antwort war nicht lesbar (Rückgabewert %d)',
                      'the answer was not readable (exit code %d)'),
 ('TEST.F_ENDPUNKT', 'Antwortet der Endpunkt für Loxone?',
                     'Does the endpoint for Loxone answer?'),
 ('TEST.EP_OK', 'ja — %s', 'yes — %s'),
 ('TEST.EP_FALSCH', 'nein — HTTP %d, Antwort begann mit: %s',
                    'no — HTTP %d, answer started with: %s'),
 ('TEST.EP_KEINE_ANTWORT',
  'keine Antwort von %s — das kann am Prüfaufbau liegen und sagt nichts über '
  'den Endpunkt',
  'no answer from %s — this may be due to the test setup and says nothing about '
  'the endpoint'),
 ('TEST.F_VORLAGE', 'Ist die Loxone-Vorlage wohlgeformt?',
                    'Is the Loxone template well-formed?'),
 ('TEST.A_VORLAGE', '%s, %d Eingänge, %d Textthemen bleiben außen vor',
                    '%s, %d inputs, %d text topics are left out'),
 ('TEST.A_VORLAGE_KAPUTT', 'nein — die erzeugte Datei ist kein gültiges XML',
                           'no — the generated file is not valid XML'),
 ('TEST.F_REITER', 'Passen Reiterleiste, Bereiche und Positivliste zusammen?',
                   'Do tab bar, panes and allow list match?'),
 ('TEST.A_REITER', '%d Namen in der Quelle, %d in der Leiste, %d Bereiche',
                   '%d names in the source, %d in the bar, %d panes'),
 ('TEST.F_WAECHTER', 'Gibt es den Wächter, der den Dienst nachstartet?',
                     'Is there a watchdog that restarts the service?'),
 ('TEST.A_WAECHTER_DA', 'ja, %s', 'yes, %s'),
 ('TEST.A_WAECHTER_UNBEKANNT',
  'nicht feststellbar — dieses Plugin liegt nicht in einer LoxBerry-Installation '
  '(Archiv oder Prüfordner)',
  'cannot be determined — this plugin is not inside a LoxBerry installation '
  '(archive or test folder)'),
 ('TEST.A_WAECHTER_FEHLT',
  'nein — unter system/cron liegt kein Eintrag für dieses Plugin (erwartet %s). '
  'Ein gestorbener Dienst startet damit nicht wieder; das Plugin neu installieren.',
  'no — there is no entry for this plugin under system/cron (expected %s). A '
  'service that died will not be restarted; reinstall the plugin.'),
 # U4 (1.2.14): Pflichtzeile nach Regeln/04.
 ('TEST.F_FORMULARE', 'Tragen alle Formulare das Merkmal?',
                      'Do all forms carry the marker?'),
 ('TEST.A_FORMULARE', '%d von %d Formularen tragen das Merkmal (index.php und ap_test.php)',
                      '%d of %d forms carry the marker (index.php and ap_test.php)'),
 ('TEST.A_FORMULARE_UNLESBAR',
  'nicht feststellbar — die Quelle der Oberfläche ist nicht lesbar oder enthält '
  'kein Formular',
  'cannot be determined — the source of the interface is not readable or '
  'contains no form'),
 # U5 (1.2.14): Kreuz, wenn die Vorlage keinen Eingang traegt.
 ('TEST.A_VORLAGE_LEER',
  '%s ist wohlgeformt, trägt aber keinen einzigen Eingang — die Themenliste '
  'fehlt oder ist leer',
  '%s is well-formed but carries no input at all — the topic list is missing '
  'or empty'),

 # ---------------- TEST: Knoepfe ----------------
 ('TEST.KNOEPFE', 'Weitere Auskünfte', 'Further information'),
 ('TEST.G_ANSEHEN', 'Ansehen', 'View'),
 ('TEST.G_TECHNIK', 'Technische Auskunft', 'Technical details'),
 ('TEST.G_AKTION', 'Löst etwas aus', 'Triggers something'),
 ('TEST.G_AKTION_HILFE',
  'Diese Knöpfe wirken sofort: sie legen eine Meldung an oder greifen in den '
  'laufenden Dienst ein.',
  'These buttons take effect immediately: they create a notification or '
  'interfere with the running service.'),
 ('TEST.K_STATUS', 'Zustand des Dienstes', 'State of the service'),
 ('TEST.K_WERTE', 'Letzte Werte', 'Last values'),
 ('TEST.K_EREIGNISSE', 'Ereignisse', 'Events'),
 ('TEST.K_MQTT', 'MQTT-Gateway', 'MQTT gateway'),
 ('TEST.K_APCUPSD', 'apcupsd prüfen', 'Check apcupsd'),
 ('TEST.K_KONFIG', 'Konfiguration anzeigen', 'Show configuration'),
 ('TEST.K_UMGEBUNG', 'Umgebung und Module', 'Environment and modules'),
 ('TEST.K_VORLAGE', 'Loxone-Vorlage prüfen', 'Check Loxone template'),
 ('TEST.K_ABFRAGEN', 'Jetzt abfragen', 'Query now'),
 ('TEST.K_MELDEN', 'Testmeldung ablegen', 'Create test notification'),
 ('TEST.K_RESTART', 'Dienst neu starten', 'Restart service'),
 ('TEST.K_STOP', 'Dienst anhalten', 'Stop service'),
 ('TEST.NOCH_NICHTS',
  'Noch nichts abgefragt. Die Ausgabe eines Knopfes erscheint hier.',
  'Nothing queried yet. The output of a button appears here.'),

 # ---------------- TEST: Ausgaben ----------------
 ('TEST.Z_ZUSTANDSDATEI', 'Zustandsdatei', 'State file'),
 ('TEST.Z_NICHT_VORHANDEN', 'nicht vorhanden', 'not present'),
 ('TEST.Z_SEKUNDEN_ALT', '%d Sekunden alt', '%d seconds old'),
 ('TEST.Z_TAKT', 'Takt', 'Interval'),
 ('TEST.Z_OERTLICH', 'örtlich', 'local'),
 ('TEST.Z_ALTES_FORMAT',
  'In der Konfiguration stehen noch Schlüssel der Originalfassung. Sie werden '
  'beim nächsten Speichern entfernt.',
  'The configuration still contains keys from the original version. They will be '
  'removed on the next save.'),
 ('TEST.Z_DIENST_TOT',
  'Der Dienst läuft nicht. Die Ursache steht meistens im Protokoll (Reiter '
  'Logdateien). Mit dem Knopf Dienst neu starten erneut versuchen.',
  'The service is not running. The reason is usually in the log (Log files tab). '
  'Try again with the Restart service button.'),
 ('TEST.Z_DIENST_STUMM',
  'Der Dienst läuft, hat aber seit %d Sekunden nichts mehr geschrieben - '
  'länger als drei Takte.',
  'The service is running but has written nothing for %d seconds - longer than '
  'three intervals.'),
 ('TEST.Z_KEINE_ANGABEN', 'Keine Angaben.', 'No information.'),
 ('TEST.W_STAND', 'Stand: vor %d Sekunden', 'Measured %d seconds ago'),
 ('TEST.W_KEINE_DATEI',
  'Es gibt noch keine Zustandsdatei. Sie entsteht, sobald der Dienst die USV '
  'das erste Mal abgefragt hat.',
  'There is no state file yet. It is created as soon as the service has queried '
  'the UPS for the first time.'),
 ('TEST.W_KEINE_WERTE', 'Keine brauchbaren Werte.', 'No usable values.'),
 ('TEST.W_ROHFELDER', '--- zusätzliche Rohfelder ---', '--- additional raw fields ---'),
 ('TEST.E_LEER',
  'Es ist noch kein Ereignis aufgezeichnet worden. Das heißt NICHT, dass alles '
  'in Ordnung ist - die Liste entsteht erst mit dem ersten Zustandswechsel, und '
  'sie wird seit Fassung 1.2.0 geführt.',
  'No event has been recorded yet. That does NOT mean everything is fine - the '
  'list only starts with the first state change, and it has been kept since '
  'version 1.2.0.'),
 ('TEST.E_ANZAHL', '%d aufgezeichnete Ereignisse, neuestes zuerst:',
                   '%d recorded events, newest first:'),
 ('TEST.AB_AUSGEWERTET', '--- ausgewertete Werte ---', '--- evaluated values ---'),
 ('TEST.AB_ROHDATEN', '--- Rohdaten von apcaccess ---', '--- raw data from apcaccess ---'),
 ('TEST.AB_STATFLAG_STREIT',
  'ACHTUNG: Statustext und STATFLAG widersprechen sich bei %s. Maßgeblich '
  'bleibt der Statustext - die Bittabelle stammt aus dem Quelltext von apcupsd '
  'und ist an dieser Anlage nicht nachgemessen.',
  'ATTENTION: status text and STATFLAG disagree on %s. The status text remains '
  'authoritative - the bit table comes from the apcupsd source code and has not '
  'been verified on this installation.'),
 # Ein Wert einer .ini kann NICHT ueber mehrere Zeilen gehen. Deshalb vier
 # Schlüssel, die der Reiter Test untereinander setzt - nicht ein Wert mit
 # eingebauten Zeilenumbruechen.
 ('TEST.AB_WAS_PRUEFEN', 'Was man prüfen kann:', 'What you can check:'),
 ('TEST.AB_PRUEF_1', '- Läuft apcupsd?  systemctl status apcupsd',
                     '- Is apcupsd running?  systemctl status apcupsd'),
 ('TEST.AB_PRUEF_2', '- Steht ISCONFIGURED in /etc/default/apcupsd auf yes?',
                     '- Is ISCONFIGURED in /etc/default/apcupsd set to yes?'),
 ('TEST.AB_PRUEF_3', '- Ist die USV per USB angeschlossen und erkannt?  lsusb',
                     '- Is the UPS connected by USB and recognised?  lsusb'),
 ('TEST.ABFRAGE_KEIN_SKRIPT', 'apc_lesen.py nicht gefunden: %s',
                              'apc_lesen.py not found: %s'),
 ('TEST.ABFRAGE_HAENGT',
  'Die Abfrage hat nicht innerhalb von 30 Sekunden geantwortet und wurde '
  'abgebrochen. Das deutet auf einen hängenden apcupsd oder eine nicht '
  'erreichbare Gegenstelle hin.',
  'The query did not answer within 30 seconds and was aborted. This points to a '
  'hanging apcupsd or an unreachable remote host.'),
 ('TEST.ABFRAGE_RC', 'Die Abfrage endete mit Rückgabewert %d.',
                     'The query ended with exit code %d.'),
 ('TEST.ABFRAGE_UNLESBAR', 'Die Abfrage lieferte keine verwertbare Antwort:',
                           'The query returned no usable answer:'),
 ('TEST.AP_NICHT_IM_PFAD', 'nicht im Pfad', 'not in the path'),
 ('TEST.AP_DIENSTZUSTAND', 'Dienstzustand', 'Service state'),
 ('TEST.AP_NICHT_LESBAR', 'nicht lesbar', 'not readable'),
 ('TEST.AP_ISCONFIGURED',
  'Steht ISCONFIGURED auf no, startet apcupsd nicht. Die Installation dieses '
  'Plugins setzt den Wert auf yes.',
  'If ISCONFIGURED is set to no, apcupsd does not start. Installing this plugin '
  'sets the value to yes.'),
 ('TEST.AP_USB', 'angeschlossene USB-Geraete', 'connected USB devices'),
 ('TEST.AP_KEIN_LSUSB', 'lsusb ist nicht vorhanden', 'lsusb is not present'),
 ('TEST.KO_DATEI', 'Datei:', 'File:'),
 ('TEST.KO_FEHLT',
  'Die Datei gibt es noch nicht. Sie entsteht beim ersten Speichern. Bis dahin '
  'gelten die Voreinstellungen:',
  'The file does not exist yet. It is created on the first save. Until then the '
  'defaults apply:'),
 ('TEST.U_NICHT_GEFUNDEN', 'nicht gefunden', 'not found'),
 ('TEST.U_PROGRAMME', 'Programme', 'Programs'),
 ('TEST.U_PROTOKOLLE', 'Protokolle', 'Logs'),
 ('TEST.U_THEMENDATEI', 'Themenliste', 'Topic list'),
 ('TEST.U_MODULE', 'Python-Module:', 'Python modules:'),
 ('TEST.U_HILFSPROGRAMME', 'Hilfsprogramme:', 'Helper programs:'),
 ('TEST.U_FEHLT', 'fehlt', 'missing'),
 ('TEST.V_WOHLGEFORMT', 'wohlgeformt', 'well-formed'),
 ('TEST.V_EINTRAEGE', 'Einträge', 'Entries'),
 ('TEST.V_ZEILENENDEN', 'Zeilenenden', 'Line endings'),
 ('TEST.V_TEXTTHEMEN',
  'Diese Textthemen bleiben bewusst außen vor: %s',
  'These text topics are deliberately left out: %s'),
 ('TEST.M_UEBERSCHRIFT',
  'Themen, die der Dienst setzt: %d insgesamt, davon %d retained (mit R '
  'gekennzeichnet).',
  'Topics the service sets: %d in total, %d of them retained (marked with R).'),
 ('TEST.M_LEBEN_OK',
  'Lebenszeichen, Aussagen des Dienstes über sich selbst und das Akkualter sind '
  'nicht retained — geprüft für %d Themen. So verlangt es der Hausstandard: ein '
  'zurückbehaltener Wert dieser Art zeigt auch dann noch „lebt“, „in Ordnung“ '
  'oder ein altes Alter an, wenn der Dienst längst steht.',
  'Heartbeat, statements of the service about itself and the battery age are not '
  'retained — checked for %d topics. That is what the house standard requires: '
  'a retained value of this kind still reports “alive”, “fine” or an old age '
  'long after the service has stopped.'),
 ('TEST.M_LEBEN_ROT',
  'BEANSTANDUNG: diese Themen dürfen nicht retained sein (Lebenszeichen, '
  'Aussage des Dienstes über sich selbst oder ein Alter): %s. Zu berichtigen in '
  'bin/apc_themen.json.',
  'OBJECTION: these topics must not be retained (heartbeat, statement of the '
  'service about itself or an age): %s. To be corrected in bin/apc_themen.json.'),
 ('TEST.M_LEBEN_FEHLT',
  'Nicht prüfbar: keines der Themen, die nie retained sein dürfen (%s), steht '
  'in der Themenliste.',
  'Cannot be checked: none of the topics that must never be retained (%s) is '
  'in the topic list.'),
 ('TEST.ARCHIV_VERWEIGERT',
  'Diese Oberfläche liegt nicht in einer LoxBerry-Installation, sondern in %s '
  '(ausgepacktes Archiv oder Prüfordner). Dienst- und Meldeknöpfe wirken von '
  'hier aus nicht — sonst träfen sie Dienst und Benachrichtigungen einer '
  'installierten Anlage.',
  'This interface is not inside a LoxBerry installation but in %s (unpacked '
  'archive or test folder). Service and notification buttons have no effect '
  'from here — otherwise they would hit the service and notifications of an '
  'installed system.'),
 ('TEST.ME_KEIN_SKRIPT', 'apc_notify.php nicht gefunden: %s',
                         'apc_notify.php not found: %s'),
 ('TEST.ME_TEXT',
  'Testmeldung des Plugins APC-UPS NG. Wenn du das liest, funktionieren die '
  'Benachrichtigungen.',
  'Test notification from the APC-UPS NG plugin. If you can read this, '
  'notifications work.'),
 ('TEST.ME_OK',
  'Die Meldung wurde abgelegt. Sie erscheint oben in der LoxBerry-Oberfläche '
  'im Glockensymbol.',
  'The notification has been created. It appears at the top of the LoxBerry '
  'interface under the bell symbol.'),
 ('TEST.ME_FEHL', 'Die Meldung konnte nicht abgelegt werden.',
                  'The notification could not be created.'),
 ('TEST.R_LAEUFT', 'Der Dienst läuft wieder (PID %d).',
                   'The service is running again (PID %d).'),
 ('TEST.R_LAEUFT_NICHT',
  'Der Dienst läuft nicht. Die Ursache steht im Reiter Logdateien.',
  'The service is not running. The reason is in the Log files tab.'),
 ('TEST.S_LAEUFT_NOCH', 'Der Dienst läuft noch (PID %d).',
                        'The service is still running (PID %d).'),
 ('TEST.S_ANGEHALTEN', 'Der Dienst wurde angehalten.', 'The service has been stopped.'),
 ('TEST.S_BLEIBT',
  'Er bleibt angehalten, bis „Dienst neu starten“ gedrückt wird — weder der '
  'Wächter noch ein Neustart des LoxBerry noch eine Aktualisierung starten ihn.',
  'It stays stopped until “Restart service” is pressed — neither the watchdog '
  'nor a LoxBerry restart nor an update will start it.'),
 ('TEST.S_MERKER_FEHLT',
  'ACHTUNG: der Merker %s ließ sich nicht anlegen — der Wächter startet den '
  'Dienst binnen fünf Minuten wieder.',
  'WARNING: the marker %s could not be created — the watchdog will start the '
  'service again within five minutes.'),
 ('TEST.UNBEKANNT', 'Unbekannte Aktion', 'Unknown action'),
 ('TEST.UNBEKANNT_LANG', 'Diese Aktion gibt es nicht: %s',
                         'This action does not exist: %s'),
]

# ---------------------------------------------------------------------------
# Gruppe 16 (1.2.23, 25.10.2026): MQTT-Umstellung, Namenstabelle, Endpunkt, Sprachausgabe (V1),
# Haus-Thema (V2), Bausteinliste nach Entwurf Abschnitt 9. Gestrichen wird, was die Vorlage des
# MQTT-Wegs (E6) brauchte; die Werte der Bausteinliste sind wortgleich zu baustein_listen.txt.
# ---------------------------------------------------------------------------
_G16_ENTFALLEN = [
 'LOXONE.KNOPF_MQTT',
 'LOXONE.VORLAGE_HINWEIS_MQTT',
 'LOXONE.VORLAGE_ZAHL',
 'LOXONE.E_GATEWAY',
 'LEGENDE.TECHNIK_DATEI',
 'TEST.V_TEXTTHEMEN',
]
_G16_SETZEN = [
 ('LOXONE.S1_01_PARAM', '1 = Akkubetrieb (Stromausfall), 0 = nicht, -1 = keine Aussage (apcupsd erreicht die USV nicht oder antwortet nicht); zurückbehalten; MQTT-Gateway Fassung 2: Haken', '1 = on battery (power failure), 0 = not, -1 = no statement (apcupsd cannot reach the UPS or does not answer); retained; MQTT gateway version 2: tick'),
 ('LOXONE.S1_02_PARAM', '0 Netz, 1 Akku, 2 Vorwarnung, 3 Abschaltung, -1 = keine Aussage; zurückbehalten; Fassung 2: Haken', '0 mains, 1 battery, 2 advance warning, 3 shutdown, -1 = no statement; retained; version 2: tick'),
 ('LOXONE.S1_03_PARAM', '1 = Werte brauchbar; 0 = apcupsd erreicht die USV nicht oder antwortet nicht (auch bei ausgeschaltetem Plugin); zurückbehalten; Fassung 2: Haken', '1 = values usable; 0 = apcupsd cannot reach the UPS or does not answer (also with the plugin switched off); retained; version 2: tick'),
 ('LOXONE.S1_04_PARAM', '1 = die USV meldet ‚Akku tauschen‘, -1 = keine Aussage; zurückbehalten; Fassung 2: Haken', '1 = the UPS reports ‘replace battery’, -1 = no statement; retained; version 2: tick'),
 ('LOXONE.S1_05_PARAM', 'Restlaufzeit in Minuten; -1 = keine Aussage; nie zurückbehalten; Fassung 2: Haken', 'runtime left in minutes; -1 = no statement; never retained; version 2: tick'),
 ('LOXONE.S1_06_PARAM', 'Lebenszeichen: zählt bei jedem Lauf des Plugins (ab Werk alle 30 s) eins weiter, 0 bis 999, läuft um – auch wenn apcupsd schweigt oder das Plugin ausgeschaltet ist; nie zurückbehalten; Fassung 2: Haken', 'heartbeat: counts up by one on every run of the plugin (every 30 s by default), 0 to 999, wraps around – also when apcupsd is silent or the plugin is switched off; never retained; version 2: tick'),
 ('LOXONE.S1_07_PARAM', '1 = Dienst läuft (bei jedem Lauf gesendet); 0 setzt der Broker selbst, wenn der Dienst abstürzt oder angehalten wird; nie zurückbehalten; Fassung 2: Haken und „Noncached“', '1 = service running (sent on every run); the broker itself sets 0 when the service crashes or is stopped; never retained; version 2: tick and “Noncached”'),
 ('LOXONE.S1_13_PARAM', 'Ein 2 / Aus 1 (ab Stufe 2 Vorwarnung; -1 = keine Aussage bleibt aus)', 'On 2 / Off 1 (from level 2, advance warning; -1 = no statement stays off)'),
 ('LOXONE.S1_15_PARAM', 'Zeilen: V4 = 0 „keine gültigen Werte – apcupsd erreicht die USV nicht oder antwortet nicht; Status ‚USV-Abfrage‘ lesen“; V1 < 0 „Zustand unbekannt – die USV meldet weder Netz- noch Akkubetrieb; Status ‚USV-Abfrage‘ lesen“; V1 = 3 „Abschaltung läuft – apcupsd fährt herunter“; V1 = 2 „Vorwarnung – Akku <v3.0> Proz., noch etwa <v2.0> min; Verbraucher abwerfen“; V1 = 1 „Stromausfall seit <v5.0> s – Akku <v3.0> Proz., noch etwa <v2.0> min“; V2 < 0 „Netzbetrieb – Akku <v3.0> Proz., die USV nennt keine Überbrückungszeit; zuletzt: <v6>“; ohne Bedingung „Netzbetrieb – Akku <v3.0> Proz., Überbrückung etwa <v2.0> min; zuletzt: <v6>“; Visualisierung EIN', 'rows: V4 = 0 “no valid values – apcupsd cannot reach the UPS or does not answer; read status ‘USV-Abfrage’”; V1 < 0 “state unknown – the UPS reports neither mains nor battery operation; read status ‘USV-Abfrage’”; V1 = 3 “shutdown running – apcupsd is shutting down”; V1 = 2 “advance warning – battery <v3.0> percent, about <v2.0> min left; shed loads”; V1 = 1 “power failure since <v5.0> s – battery <v3.0> percent, about <v2.0> min left”; V2 < 0 “on mains – battery <v3.0> percent, the UPS states no bridging time; last: <v6>”; without condition “on mains – battery <v3.0> percent, bridging about <v2.0> min; last: <v6>”; visualisation ON'),
 ('LOXONE.S1_16_PARAM', 'Akkuladung in Proz.; -1 = keine Aussage; nie zurückbehalten; Fassung 2: Haken', 'battery charge in percent; -1 = no statement; never retained; version 2: tick'),
 ('LOXONE.S1_17_PARAM', 'letzte Abfrage bei apcupsd: 1 gelungen, 0 gescheitert oder Plugin ausgeschaltet (Dienst läuft aber), -1 seit dem Start des Dienstes noch keine; nie zurückbehalten; Fassung 2: Haken und „Noncached“', 'last query to apcupsd: 1 succeeded, 0 failed or plugin switched off (but the service is running), -1 none yet since the service started; never retained; version 2: tick and “Noncached”'),
 ('LOXONE.S1_19_PARAM', 'Tmc 150 s (fünf Lebenszeichen à 30 s ohne neuen Wert), Min 0, Max 999 – steht der LoxBerry, das MQTT-Gateway oder der Dienst, bleibt der Zähler stehen; Haken bei ‚En‘ im Eigenschaftsfenster entfernen', 'Tmc 150 s (five heartbeats of 30 s without a new value), Min 0, Max 999 – if the LoxBerry, the MQTT gateway or the service stops, the counter stops; remove the tick at ‘En’ in the properties'),
 ('LOXONE.S1_22_PARAM', '— (Dienst aus oder kein Lebenszeichen)', '— (service off or no heartbeat)'),
 ('LOXONE.S1_26_PARAM', 'Sekunden im laufenden Akkubetrieb; 0 bei Netzbetrieb, -1 = keine Aussage; nie zurückbehalten; Fassung 2: Haken', 'seconds in the current battery operation; 0 on mains, -1 = no statement; never retained; version 2: tick'),
 ('LOXONE.S1_31_PARAM', '1 = Abschaltschwelle erreicht, apcupsd fährt jetzt herunter; -1 = keine Aussage; zurückbehalten; Fassung 2: Haken', '1 = shutdown threshold reached, apcupsd is shutting down now; -1 = no statement; retained; version 2: tick'),
 ('LOXONE.S1_33_PARAM', 'Zustandstext der USV, z. B. ONLINE, ONBATT, COMMLOST; „-“ = apcupsd antwortet nicht oder Plugin ausgeschaltet; Titel genau so (Name, den das MQTT-Gateway vergibt), „In Visualisierung verwenden“ an; zurückbehalten; Fassung 2: Haken', 'state text of the UPS, e.g. ONLINE, ONBATT, COMMLOST; “-” = apcupsd does not answer or plugin switched off; title exactly like this (the name the MQTT gateway assigns), “Use in visualisation” on; retained; version 2: tick'),
 ('LOXONE.S1_34_PARAM', 'letztes Ereignis, z. B. „Stromausfall“, „Netz wieder da“ – bleibt stehen, bis ein neues kommt (zurückbehalten, gewollt); Titel genau so; Fassung 2: Haken', 'last event, e.g. “Stromausfall”, “Netz wieder da” – stays until a new one comes (retained, intended); title exactly like this; version 2: tick'),
 ('LOXONE.S1_35_PARAM', 'Fehlermeldung der letzten Abfrage, leer = in Ordnung, „Plugin ausgeschaltet“ = im Plugin nicht eingeschaltet; Titel genau so; nie zurückbehalten; Fassung 2: Haken', 'error message of the last query, empty = OK, “Plugin ausgeschaltet” = not switched on in the plugin; title exactly like this; never retained; version 2: tick'),
 ('LOXONE.S1_36_PARAM', 'Zeilen: V1 = 0 „Dienst läuft nicht – im Plugin Reiter Test ‚Dienst neu starten‘“; V2 = 1 „seit über 2 Minuten kein Lebenszeichen (zuletzt <v3.t>) – LoxBerry, MQTT-Gateway (Fassung 1: Abo apcups/#, Fassung 2: Haken an apcups/status/zaehler) und Dienst prüfen; im Plugin Reiter Test ‚Dienst neu starten‘“; V4 < 0 „Dienst gestartet, noch keine Abfrage – einen Augenblick warten“; V4 = 0 „apcupsd antwortet nicht: <v5> – im Plugin Reiter Test ‚apcupsd prüfen‘; bei ‚Plugin ausgeschaltet‘ im Reiter Einstellungen ‚Plugin eingeschaltet‘ anhaken“; V6 = 0 „apcupsd erreicht die USV nicht (Kabel?) – <v7>“; ohne Bedingung „in Ordnung – USV meldet <v7>, letzte Abfrage <v3.t>“; Visualisierung EIN', 'rows: V1 = 0 “service not running – on the Test tab of the plugin press ‘Restart service’”; V2 = 1 “no heartbeat for more than 2 minutes (last <v3.t>) – check LoxBerry, MQTT gateway (version 1: subscription apcups/#, version 2: tick at apcups/status/zaehler) and service; on the Test tab of the plugin press ‘Restart service’”; V4 < 0 “service started, no query yet – wait a moment”; V4 = 0 “apcupsd does not answer: <v5> – on the Test tab of the plugin press ‘Check apcupsd’; with ‘Plugin ausgeschaltet’ tick ‘Plugin switched on’ on the Settings tab”; V6 = 0 “apcupsd cannot reach the UPS (cable?) – <v7>”; without condition “OK – UPS reports <v7>, last query <v3.t>”; visualisation ON'),
 ('LOXONE.S1_37_PARAM', 'IF(I1>0;1;0) – nur 1 zählt als Stromausfall, -1 (keine Aussage) nicht', 'IF(I1>0;1;0) – only 1 counts as power failure, -1 (no statement) does not'),
 ('LOXONE.S1_37_NAME', 'Akkubetrieb gemeldet (USV)', 'Akkubetrieb gemeldet (USV)'),
 ('LOXONE.S1_38_PARAM', 'IF(I1>0;1;0) – nur 1 löst die Meldung aus, -1 nicht', 'IF(I1>0;1;0) – only 1 triggers the notification, -1 does not'),
 ('LOXONE.S1_38_NAME', 'Akku tauschen gemeldet (USV)', 'Akku tauschen gemeldet (USV)'),
 ('LOXONE.S1_39_PARAM', 'IF(I1>0;1;0) – nur 1 löst die Meldung aus, -1 nicht', 'IF(I1>0;1;0) – only 1 triggers the notification, -1 does not'),
 ('LOXONE.S1_39_NAME', 'Abschaltung gemeldet (USV)', 'Abschaltung gemeldet (USV)'),
 ('LOXONE.S2_01_PARAM', 'Akkuladung in Proz. (zweite Instanz, auch auf Seite „APC-UPS NG“); -1 = keine Aussage; Statistik ein', 'battery charge in percent (second instance, also on page “APC-UPS NG”); -1 = no statement; statistics on'),
 ('LOXONE.S2_02_PARAM', 'Auslastung der USV in Proz.; -1 = keine Aussage; nie zurückbehalten; Fassung 2: Haken', 'load of the UPS in percent; -1 = no statement; never retained; version 2: tick'),
 ('LOXONE.S2_03_PARAM', 'Last in W, gerechnet aus Auslastung und Nennleistung; -1, wenn die USV keine Nennleistung meldet oder keine Aussage; Statistik ein; nie zurückbehalten; Fassung 2: Haken', 'load in W, calculated from load and rated power; -1 if the UPS reports no rated power or no statement; statistics on; never retained; version 2: tick'),
 ('LOXONE.S2_04_PARAM', 'Nennleistung der USV in W; -1 = meldet die USV nicht; zurückbehalten; Fassung 2: Haken', 'rated power of the UPS in W; -1 = not reported by the UPS; retained; version 2: tick'),
 ('LOXONE.S2_05_PARAM', 'Netzspannung in V; -1 = keine Aussage; Statistik ein; nie zurückbehalten; Fassung 2: Haken', 'mains voltage in V; -1 = no statement; statistics on; never retained; version 2: tick'),
 ('LOXONE.S2_06_PARAM', 'Spannung am USV-Ausgang in V; -1 = keine Aussage; nie zurückbehalten; Fassung 2: Haken', 'voltage at the UPS output in V; -1 = no statement; never retained; version 2: tick'),
 ('LOXONE.S2_07_PARAM', 'Netzfrequenz in Hz; -1, wenn das Modell sie nicht liefert oder keine Aussage; nie zurückbehalten; Fassung 2: Haken', 'mains frequency in Hz; -1 if the model does not provide it or no statement; never retained; version 2: tick'),
 ('LOXONE.S2_08_PARAM', 'Akkuspannung in V; -1 = keine Aussage; nie zurückbehalten; Fassung 2: Haken', 'battery voltage in V; -1 = no statement; never retained; version 2: tick'),
 ('LOXONE.S2_09_PARAM', 'Nennspannung des Akkus in V; -1 = meldet die USV nicht; zurückbehalten; Fassung 2: Haken', 'nominal voltage of the battery in V; -1 = not reported by the UPS; retained; version 2: tick'),
 ('LOXONE.S2_10_PARAM', 'Innentemperatur in °C; -999, wenn das Modell sie nicht liefert oder keine Aussage; Statistik ein; nie zurückbehalten; Fassung 2: Haken', 'internal temperature in °C; -999 if the model does not provide it or no statement; statistics on; never retained; version 2: tick'),
 ('LOXONE.S2_11_PARAM', 'Akkualter in Monaten aus dem Einbaudatum; -1, wenn das Datum fehlt oder zweideutig ist oder keine Aussage; nie zurückbehalten; Fassung 2: Haken', 'battery age in months from the installation date; -1 if the date is missing or ambiguous or no statement; never retained; version 2: tick'),
 ('LOXONE.S2_12_PARAM', '1 = die USV meldet „Akku tauschen“, -1 = keine Aussage (zweite Instanz, auch auf Seite „APC-UPS NG“)', '1 = the UPS reports “replace battery”, -1 = no statement (second instance, also on page “APC-UPS NG”)'),
 ('LOXONE.S2_13_PARAM', 'Zahl der Umschaltungen auf Akku (Zählerstand von apcupsd); -1 = keine Aussage; nie zurückbehalten; Fassung 2: Haken', 'number of transfers to battery (counter reading of apcupsd); -1 = no statement; never retained; version 2: tick'),
 ('LOXONE.S2_14_PARAM', 'Sekunden auf Akku insgesamt; -1 = keine Aussage; nie zurückbehalten; Fassung 2: Haken', 'seconds on battery in total; -1 = no statement; never retained; version 2: tick'),
 ('LOXONE.S2_15_PARAM', 'Abschaltschwelle von apcupsd: Ladung in Proz.; -1 = meldet die USV nicht; zurückbehalten; Fassung 2: Haken', 'shutdown threshold of apcupsd: charge in percent; -1 = not reported by the UPS; retained; version 2: tick'),
 ('LOXONE.S2_16_PARAM', 'Abschaltschwelle von apcupsd: Restlaufzeit in Minuten; -1 = meldet die USV nicht; zurückbehalten; Fassung 2: Haken', 'shutdown threshold of apcupsd: runtime left in minutes; -1 = not reported by the UPS; retained; version 2: tick'),
 ('LOXONE.S2_17_PARAM', 'Zeitlimit von apcupsd im Akkubetrieb in s; 0 = kein Zeitlimit, -1 = meldet die USV nicht; zurückbehalten; Fassung 2: Haken', 'time limit of apcupsd on battery in s; 0 = no time limit, -1 = not reported by the UPS; retained; version 2: tick'),
 ('LOXONE.S2_18_PARAM', '1 = Netzbetrieb (auch während die USV die Spannung anhebt oder absenkt), 0 = nicht, -1 = keine Aussage; zurückbehalten; Fassung 2: Haken', '1 = on mains (also while the UPS raises or lowers the voltage), 0 = not, -1 = no statement; retained; version 2: tick'),
 ('LOXONE.S2_19_PARAM', 'Modell der USV; Titel genau so (Name, den das MQTT-Gateway vergibt); zurückbehalten; Fassung 2: Haken', 'model of the UPS; title exactly like this (the name the MQTT gateway assigns); retained; version 2: tick'),
 ('LOXONE.S2_20_PARAM', 'Seriennummer der USV; Titel genau so; zurückbehalten; Fassung 2: Haken', 'serial number of the UPS; title exactly like this; retained; version 2: tick'),
 ('LOXONE.S2_21_PARAM', 'Einbaudatum des Akkus, wie die USV es speichert; Titel genau so; zurückbehalten; Fassung 2: Haken', 'installation date of the battery, as the UPS stores it; title exactly like this; retained; version 2: tick'),
 ('LOXONE.S2_22_PARAM', 'Ergebnis des letzten Selbsttests, wie apcupsd es meldet (Kürzel); Titel genau so; zurückbehalten; Fassung 2: Haken', 'result of the last self-test, as apcupsd reports it (abbreviation); title exactly like this; retained; version 2: tick'),
 ('LOXONE.S2_23_PARAM', 'Abstand der automatischen Selbsttests, wie apcupsd es meldet; Titel genau so; zurückbehalten; Fassung 2: Haken', 'interval of the automatic self-tests, as apcupsd reports it; title exactly like this; retained; version 2: tick'),
 ('LOXONE.S2_24_PARAM', 'Grund der letzten Umschaltung auf Akku, wie apcupsd es meldet, „-“ = keine Aussage; Titel genau so; nie zurückbehalten; Fassung 2: Haken', 'reason for the last transfer to battery, as apcupsd reports it, “-” = no statement; title exactly like this; never retained; version 2: tick'),
 ('LOXONE.S2_27_PARAM', 'Text: USV – Auslastung seit einer Minute über 80 Proz.; bei Stromausfall reicht der Akku dann deutlich kürzer, bei Überlast schaltet die USV ab. Geräte vom USV-Ausgang nehmen', 'text: UPS – load for one minute above 80 percent; on a power failure the battery then lasts much shorter, on overload the UPS switches off. Remove devices from the UPS output'),
 ('LOXONE.S2_28_PARAM', 'Ein 40 / Aus 35 (°C; -999 = keine Aussage bleibt aus)', 'On 40 / Off 35 (°C; -999 = no statement stays off)'),
 ('LOXONE.S2_31_PARAM', 'Ein 80 / Aus 95 (Prozent; schaltet beim Unterschreiten von 80 ein, über 95 wieder aus; bei -1 = keine Aussage ein, das UND #32 hält es dann über #43 zurück)', 'On 80 / Off 95 (percent; switches on when falling below 80, off again above 95; on -1 = no statement on, the AND #32 then holds it back via #43)'),
 ('LOXONE.S2_34_PARAM', 'Text: USV – der Akku ist seit 6 Stunden unter 80 Proz., obwohl das Netz da ist; in der App „USV Akku“ lesen, im Plugin Reiter Test „Letzte Werte“ ansehen, Akku prüfen oder tauschen', 'text: UPS – for 6 hours the battery has been below 80 percent although mains power is there; read “USV Akku” in the app, look at “Last values” on the Test tab of the plugin, check or replace the battery'),
 ('LOXONE.S2_37_PARAM', 'IF(I1<0;-1;IF(I2>0;IF(I1>=I2;I1-I2;I1);0)) – Zählerstand minus Stand um Mitternacht; -1, solange die USV keine Aussage macht; nach einem Neustart von apcupsd zählt er von vorn, nach einem Neustart des Miniservers bis Mitternacht 0', 'IF(I1<0;-1;IF(I2>0;IF(I1>=I2;I1-I2;I1);0)) – counter reading minus reading at midnight; -1 while the UPS makes no statement; after a restart of apcupsd it counts from zero, after a restart of the Miniserver 0 until midnight'),
 ('LOXONE.S2_40_PARAM', 'Zeilen: V1 = 1 „Akku tauschen – die USV meldet einen verbrauchten Akku (eingebaut <v4>)“; V2 < 0 „keine Akkuwerte – die USV ist gerade nicht erreichbar; Status ‚USV-Abfrage‘ lesen“; V3 >= 48 „Akku <v3.0> Monate alt (eingebaut <v4>) – Ersatz einplanen; Ladung <v2.0> Proz.“; ohne Bedingung „Ladung <v2.0> Proz., <v5.1> V (Nennspannung <v6.0> V), eingebaut <v4>, letzter Selbsttest <v7>, insgesamt <v8.0> s auf Akku (-1 = meldet die USV nicht)“; Visualisierung EIN', 'rows: V1 = 1 “replace battery – the UPS reports a worn battery (installed <v4>)”; V2 < 0 “no battery values – the UPS cannot be reached right now; read status ‘USV-Abfrage’”; V3 >= 48 “battery <v3.0> months old (installed <v4>) – plan a replacement; charge <v2.0> percent”; without condition “charge <v2.0> percent, <v5.1> V (nominal voltage <v6.0> V), installed <v4>, last self-test <v7>, <v8.0> s on battery in total (-1 = not reported by the UPS)”; visualisation ON'),
 ('LOXONE.S2_41_PARAM', 'Zeilen: V1 < 0 „keine Netz- und Lastwerte – die USV ist gerade nicht erreichbar; Status ‚USV-Abfrage‘ lesen“; V4 >= 80 „überlastet: <v4.0> Proz. (<v5.0> W von <v6.0> W) – Geräte vom USV-Ausgang nehmen“; V5 < 0 „Netz <v1.0> V / <v2.1> Hz, Ausgang <v3.0> V, Last <v4.0> Proz. (die USV meldet keine Nennleistung); heute <v7.0> Umschaltungen, zuletzt wegen: <v8>“; ohne Bedingung „Netz <v1.0> V / <v2.1> Hz, Ausgang <v3.0> V, Last <v4.0> Proz. (<v5.0> W von <v6.0> W); heute <v7.0> Umschaltungen, zuletzt wegen: <v8> (-1 = meldet die USV nicht)“; Visualisierung EIN', 'rows: V1 < 0 “no mains and load values – the UPS cannot be reached right now; read status ‘USV-Abfrage’”; V4 >= 80 “overloaded: <v4.0> percent (<v5.0> W of <v6.0> W) – remove devices from the UPS output”; V5 < 0 “mains <v1.0> V / <v2.1> Hz, output <v3.0> V, load <v4.0> percent (the UPS reports no rated power); today <v7.0> transfers, last because of: <v8>”; without condition “mains <v1.0> V / <v2.1> Hz, output <v3.0> V, load <v4.0> percent (<v5.0> W of <v6.0> W); today <v7.0> transfers, last because of: <v8> (-1 = not reported by the UPS)”; visualisation ON'),
 ('LOXONE.S2_42_PARAM', 'Zeilen: V4 < 0 und V5 < 0 „<v1> (Nr. <v2>) – die USV meldet keine Abschaltschwellen, die Vorwarnung (Stufe 2) kommt deshalb nie; Selbsttest: <v3>“; V6 > 0 „<v1> (Nr. <v2>) – apcupsd schaltet ab bei <v4.0> Proz. Ladung, <v5.0> min Restzeit oder nach <v6.0> s auf Akku; Selbsttest: <v3>“; ohne Bedingung „<v1> (Nr. <v2>) – apcupsd schaltet ab bei <v4.0> Proz. Ladung oder <v5.0> min Restzeit; Selbsttest: <v3>“; Visualisierung EIN', 'rows: V4 < 0 and V5 < 0 “<v1> (no. <v2>) – the UPS reports no shutdown thresholds, so the advance warning (level 2) never comes; self-test: <v3>”; V6 > 0 “<v1> (no. <v2>) – apcupsd shuts down at a charge of <v4.0> percent, <v5.0> min runtime left or after <v6.0> s on battery; self-test: <v3>”; without condition “<v1> (no. <v2>) – apcupsd shuts down at a charge of <v4.0> percent or <v5.0> min runtime left; self-test: <v3>”; visualisation ON'),
 ('LOXONE.S2_43_PARAM', 'IF(I1>0;1;0) – nur 1 zählt als „Netz da“, -1 (keine Aussage) nicht', 'IF(I1>0;1;0) – only 1 counts as “mains present”, -1 (no statement) does not'),
 ('LOXONE.S2_43_NAME', 'Netzbetrieb gemeldet (USV)', 'Netzbetrieb gemeldet (USV)'),
 ('EINST.PLUGIN_EINGESCHALTET_HILFE', 'Solange das nicht angehakt ist, läuft der Dienst weiter und meldet sich (Lebenszeichen), fragt die USV aber nicht ab: alle Zustände und Messwerte stehen auf „keine Aussage“ (-1), letzter Fehler „Plugin ausgeschaltet“.', 'While this is unchecked the service keeps running and reports in (heartbeat), but does not query the UPS: all states and measured values are set to “no statement” (-1), last error “Plugin ausgeschaltet”.'),
 ('LOXONE.SCHRITT3_TEXT', 'Seit 1.2.23 ohne Vorlage: je Wert ein Virtueller Eingang mit genau dem Namen, den das MQTT-Gateway vergibt. Die Tabelle nennt alle Namen, die Bauform, den Bereich mit Fehlwert und die Stelle auf den Musterseiten.', 'Since 1.2.23 without a template: one virtual input per value with exactly the name the MQTT gateway assigns. The table lists all names, the type, the range with missing value and the place on the sample pages.'),
 ('LOXONE.SCHRITT4', 'Schritt 4: Befehle', 'Step 4: commands'),
 ('LOXONE.SCHRITT4_TEXT', 'Befehle: keine – das Plugin liest nur. Die Abschaltung macht apcupsd selbst (siehe Reiter Einstellungen, Abschnitt Notabschaltung). Es gibt deshalb keinen virtuellen Ausgang.', 'Commands: none – the plugin only reads. The shutdown is done by apcupsd itself (see the Settings tab, section Emergency shutdown). There is therefore no virtual output.'),
 ('LOXONE.SCHRITT5_TEXT', "Ein virtueller Eingang behält seinen letzten Wert, wenn nichts mehr kommt. Dagegen: <span class='sm-mono'>status/zaehler</span> zählt bei jedem Lauf des Dienstes eins weiter (0 bis 999, auch bei ausgeschaltetem Plugin) – eine Analogwertvalidierung mit Tmc = fünfmal der Abfragetakt (ab Werk 150 s) meldet, wenn er stehen bleibt; den Haken bei ‚En‘ im Eigenschaftsfenster entfernen. <span class='sm-mono'>status/ok</span> (1 gelungen, 0 gescheitert oder ausgeschaltet, -1 noch keine Abfrage) und <span class='sm-mono'>service/online</span> (0 setzt der Broker selbst, wenn der Dienst abstürzt) unter Gateway V2 auf „Noncached“ stellen. <span class='sm-mono'>status/ts</span> und <span class='sm-mono'>timestamp</span> nicht für eine Altersrechnung verwenden (Ortszeit).", "A virtual input keeps its last value when nothing arrives any more. Against this: <span class='sm-mono'>status/zaehler</span> counts up by one on every run of the service (0 to 999, also with the plugin switched off) – an analog value validation with Tmc = five times the query interval (150 s by default) reports when it stops; remove the tick at ‚En‘ in the properties. <span class='sm-mono'>status/ok</span> (1 succeeded, 0 failed or switched off, -1 no query yet) and <span class='sm-mono'>service/online</span> (the broker sets 0 itself when the service crashes) set to “Noncached” under gateway V2. Do not use <span class='sm-mono'>status/ts</span> and <span class='sm-mono'>timestamp</span> for an age calculation (local time)."),
 ('LOXONE.BAUSTEINE_VORTEXT', 'Zwei Seiten aus dem LoxBerry-Plugins Musterprojekt, jede Zeile ein Baustein (Baustein-Suche in Loxone Config: Taste <b>F5</b>). Die erste zeigt Stromausfall, Vorwarnung und Abschaltung, meldet Störungen der Abfrage und wirft bei knappem Akku Verbraucher ab – sie genügt für den Anfang. Die zweite zeigt Akku, Netz, Last und Gerätedaten und meldet Überlast, Wärme, einen Akku, der nicht lädt, und ein unruhiges Netz. Die Eingänge sind Virtuelle Eingänge und Texteingänge mit dem Namen, den das MQTT-Gateway vergibt (Schritt 3) – die Namen bleiben, wie sie sind.', 'Two pages from the LoxBerry plugins sample project, every row one block (block search in Loxone Config: key <b>F5</b>). The first shows power failure, advance warning and shutdown, reports faults of the query and sheds loads when the battery runs low – it is enough to start with. The second shows battery, mains, load and device data and reports overload, heat, a battery that does not charge and an unsteady mains. The inputs are virtual inputs and text inputs with the name the MQTT gateway assigns (step 3) – keep the names as they are.'),
 ('LOXONE.TYP_VI', 'Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin APC-UPS NG)', 'Virtual input (name as the MQTT gateway assigns it, plugin APC-UPS NG)'),
 ('LOXONE.ALTER_WEG', 'Bestehende Anlagen: der alte XML-Weg', 'Existing installations: the old XML path'),
 ('LOXONE.ALTER_WEG_TEXT', "Die Originalfassung stellte unter dieser Adresse eine XML-Seite bereit, die Loxone selbst abholt. Seit 1.2.23 antwortet sie nur mit dem Haken unten (Neuinstallation aus; ein Update lässt ihn bei bestehenden Anlagen an). Sie beachtet die Einstellung <i>USV auf einem anderen Rechner</i> und liefert zusätzlich zu den Rohfeldern die abgeleiteten Werte im Block <span class='sm-mono'>CALC</span> – als Rohwerte (ein fehlender Wert bleibt leer), samt <span class='sm-mono'>OK</span> und <span class='sm-mono'>ALTER</span>: OK fällt auf 0, sobald die Werte älter sind als das Dreifache des Abfragetakts.", "The original version provided an XML page at this address which Loxone fetches itself. Since 1.2.23 it only answers with the tick below (new installation off; an update leaves it on for existing installations). It honours the setting <i>UPS on another machine</i> and, in addition to the raw fields, provides the derived values in a <span class='sm-mono'>CALC</span> block – as raw values (a missing value stays empty), together with <span class='sm-mono'>OK</span> and <span class='sm-mono'>ALTER</span>: OK drops to 0 as soon as the values are older than three times the query interval."),
 ('LOXONE.ALTER_WEG_ADRESSE', 'Adresse prüfen – sie muss aus Sicht des Miniservers stimmen (LAN-Adresse des LoxBerry, Webserver-Port, wenn er nicht 80 ist).', 'Check the address – it must be right from the Miniserver’s point of view (LAN address of the LoxBerry, web server port if it is not 80).'),
 ('LOXONE.S1_SCHRITT2', 'LoxBerry → MQTT Gateway: das Abo %s trägt das Plugin selbst ein (Schritt 2 oben sagt, was bei Ihrem Gateway gilt). Gateway V2: die Haken aus Schritt 2 setzen; %s und %s zusätzlich auf „Noncached“.', 'LoxBerry → MQTT Gateway: the plugin enters the subscription %s itself (step 2 above says what applies to your gateway). Gateway V2: set the ticks from step 2; additionally set %s and %s to “Noncached”.'),
 ('LOXONE.S1_SCHRITT3', 'Die elf Virtuellen Eingänge dieser Seite anlegen (Peripherie → Virtuelle Eingänge → Virtueller Eingang), Name genau so: %s. „Als Digitaleingang“ NICHT anhaken. Oben in Schritt 3 kopiert ein Knopf alle Namen.', 'Create the eleven virtual inputs of this page (Periphery → Virtual Inputs → Virtual input), name exactly like this: %s. Do NOT tick “Use as digital input”. Above in step 3 a button copies all names.'),
 ('LOXONE.S1_SCHRITT5', 'Seite „APC-UPS NG“ anlegen. Die elf Eingänge, die drei Texteingänge und die Konstante 1 darauf ziehen.', 'Create the page “APC-UPS NG”. Drag the eleven inputs, the three text inputs and the constant 1 onto it.'),
 ('LOXONE.S1_SCHRITT8', 'Die übrigen Bausteine über die Baustein-Suche (Taste F5) setzen, Parameter wie in der Liste, nach der Spalte „%s“ von oben nach unten verbinden. Die drei Formeln (#37 bis #39) stehen zwischen Eingang und Meldung. Status-Eingänge ab V5 erscheinen erst nach Klick auf das „+“ am Baustein: „USV-Abfrage“ dreimal (V5–V7), „USV-Zustand“ zweimal (V5/V6). ODER und UND haben je zwei Eingänge. Die Zeilen der Status-Bausteine stehen in der Spalte „%s“ und werden von Hand eingetragen – in der angegebenen Reihenfolge, die Zeile ohne Bedingung zuletzt.', 'Place the remaining blocks via the block search (key F5), parameters as in the list, and wire them from top to bottom according to the column “%s”. The three formulas (#37 to #39) sit between input and notification. Status inputs from V5 only appear after clicking the “+” on the block: “USV-Abfrage” three times (V5–V7), “USV-Zustand” twice (V5/V6). OR and AND have two inputs each. The rows of the status blocks are in the column “%s” and are entered by hand – in the given order, the row without condition last.'),
 ('LOXONE.S1_SCHRITT9', 'Speichern und in den Miniserver übertragen. Probe: %s zählt alle 30 s eins weiter; der Status „USV-Abfrage“ zeigt „in Ordnung – USV meldet ONLINE …“; im Plugin Reiter „%s“ → „%s“ steht dieselbe Ladung wie in Loxone.', 'Save and transfer to the Miniserver. Test: %s counts up by one every 30 s; the status “USV-Abfrage” shows “OK – UPS reports ONLINE …”; in the plugin, tab “%s” → “%s” shows the same charge as Loxone.'),
 ('LOXONE.S1_H4', 'Zu #6 und #19: Der Zähler läuft bei jedem Lauf des Dienstes eins weiter (0 bis 999), auch bei ausgeschaltetem Plugin. Die Analogwertvalidierung prüft nur, ob er sich ändert, und bekommt an En die Konstante 1. Tmc ist das Fünffache des Abfragetakts: wer „%s“ ändert, setzt Tmc auf das Fünffache des neuen Werts.', 'On #6 and #19: the counter counts up by one on every run of the service (0 to 999), also with the plugin switched off. The analog value validation only checks whether it changes, and gets the constant 1 at En. Tmc is five times the query interval: whoever changes “%s” sets Tmc to five times the new value.'),
 ('LOXONE.S1_H6', 'Zu #33 bis #35: Virtuelle Texteingänge (Peripherie → Virtuelle Eingänge → Virtueller Texteingang), Name genau wie in der Spalte „%s“ – den Namen vergibt das MQTT-Gateway.', 'On #33 to #35: virtual text inputs (Periphery → Virtual Inputs → Virtual text input), name exactly as in the column “%s” – the MQTT gateway assigns the name.'),
 ('LOXONE.S1_H7', 'Zu #37 bis #39: -1 heißt „keine Aussage“ (apcupsd erreicht die USV nicht, antwortet nicht, oder das Plugin ist ausgeschaltet). Die Formeln lassen nur eine 1 durch – eine -1 löst weder die Einschaltverzögerung noch eine Benachrichtigung aus.', 'On #37 to #39: -1 means “no statement” (apcupsd cannot reach the UPS, does not answer, or the plugin is switched off). The formulas only let a 1 through – a -1 triggers neither the on-delay nor a notification.'),
 ('LOXONE.S2_SCHRITT1', 'Seite „APC-UPS NG“ zuerst übernehmen (Gateway und Namen wie dort, Schritte 1–3).', 'Take over the page “APC-UPS NG” first (gateway and names as there, steps 1–3).'),
 ('LOXONE.S2_SCHRITT3', 'Neue Seite „APC-UPS NG Akku und Netz“. Die übrigen 16 Virtuellen Eingänge der Liste anlegen (Nr. 2–11 und 13–18, Name wie in der Tabelle, „Als Digitaleingang“ nicht anhaken); %s und %s stehen schon auf der Seite „APC-UPS NG“ – ein zweites Mal hineinziehen, nicht neu anlegen. Bei %s, %s, %s und %s im Eigenschaftsfenster „Statistik“ einschalten.', 'New page “APC-UPS NG Akku und Netz”. Create the remaining 16 virtual inputs of the list (no. 2–11 and 13–18, name as in the table, do not tick “Use as digital input”); %s and %s are already on the page “APC-UPS NG” – drag them in a second time, do not create them anew. For %s, %s, %s and %s switch on “Statistics” in the properties window.'),
 ('LOXONE.S2_SCHRITT5', 'Die übrigen Bausteine über die Baustein-Suche (Taste F5) setzen, Parameter wie in der Liste, nach der Spalte „%s“ verbinden. Die Formel #43 steht zwischen #18 und dem UND #32. Status-Eingänge ab V5 erscheinen erst nach Klick auf das „+“ am Baustein: „USV Akku“ und „USV Netz und Last“ viermal (V5–V8), „USV Gerät“ zweimal (V5/V6). Das UND hat zwei Eingänge. Die Zeilen der Status-Bausteine stehen in der Spalte „%s“ und werden von Hand eingetragen, die Zeile ohne Bedingung zuletzt. „Impuls um“ bleibt auf 00:00:00.', 'Place the remaining blocks via the block search (key F5), parameters as in the list, and wire them according to the column “%s”. The formula #43 sits between #18 and the AND #32. Status inputs from V5 only appear after clicking the “+” on the block: “USV Akku” and “USV Netz und Last” four times (V5–V8), “USV Gerät” twice (V5/V6). The AND has two inputs. The rows of the status blocks are in the column “%s” and are entered by hand, the row without condition last. “Pulse at” stays at 00:00:00.'),
 ('LOXONE.S2_H1', 'Schwellen nach der eigenen USV wählen: Überlast 80/70 Proz., zu warm 40/35 °C, „Akku lädt nicht“ 6 Stunden unter 80 Proz. Liefert die USV keine Temperatur, steht dort -999 – dann wirkt die Meldung „zu warm“ nie; eine fehlende Netzfrequenz steht als -1 da.', 'Choose the thresholds for your own UPS: overload 80/70 percent, too warm 40/35 °C, “Akku lädt nicht” 6 hours below 80 percent. If the UPS provides no temperature, -999 stands there – then the notification “zu warm” never triggers; a missing mains frequency shows as -1.'),
 ('LOXONE.S2_H4', '„Umschaltungen heute“ zählt ab Mitternacht und zeigt -1, solange die USV keine Aussage macht. Nach einem Neustart des Miniservers steht sie bis zur nächsten Mitternacht auf 0; nach einem Neustart von apcupsd zählt apcupsd von vorn.', '“Umschaltungen heute” counts from midnight and shows -1 while the UPS makes no statement. After a restart of the Miniserver it stays at 0 until the next midnight; after a restart of apcupsd, apcupsd counts from zero.'),
 ('TEST.A_VORLAGE', '%s, %d Eingänge (alter XML-Weg)', '%s, %d inputs (old XML path)'),
 ('LEGENDE.TECHNIK_HILFSMITTEL', 'Hilfsmittel — kopiert Namen oder erzeugt eine Datei, verändert nichts', 'Tools — copies names or creates a file, changes nothing'),
 ('EINST.HAUS_USV_EIN', 'Stufe an andere Plugins geben (haus/usv/stufe)', 'Pass the level on to other plugins (haus/usv/stufe)'),
 ('EINST.HAUS_USV_HILFE', "Sendet die Alarmstufe der USV als <span class='sm-mono'>haus/usv/stufe</span> (0 Netz, 1 Akku, 2 Vorwarnung, 3 Abschaltung, -1 ohne Aussage; zurückbehalten) und das Lebenszeichen <span class='sm-mono'>haus/usv/zaehler</span> an den Broker – ohne Themenpräfix, für andere Plugins (Regeln Nr. 15). Nur eine USV im Haus darf das liefern. Abnehmer (z. B. Sprachsteuerung lokal) können damit bei knappem Akku Dienste anhalten. Wirkt nur mit MQTT. Beim Ausschalten räumt das Plugin das Thema am Broker wieder ab. Ab Werk aus.", "Sends the alarm level of the UPS as <span class='sm-mono'>haus/usv/stufe</span> (0 mains, 1 battery, 2 advance warning, 3 shutdown, -1 no statement; retained) and the heartbeat <span class='sm-mono'>haus/usv/zaehler</span> to the broker – without the topic prefix, for other plugins (rules no. 15). Only one UPS in the house may provide it. Consumers (e.g. local voice control) can use it to pause services when the battery runs low. Only works with MQTT. When switched off, the plugin removes the topic from the broker again. Off by default."),
 ('EINST.ANSAGE_UEBERSCHRIFT', 'Sprachausgabe bei Stromausfall', 'Voice announcement on power failure'),
 ('EINST.ANSAGE_LAUTSPRECHER', '<b>Bei einem Stromausfall hängen Lautsprecher, Echo, Router und WLAN oft NICHT an der USV</b> – dann kommt die Ansage nicht an. Sie hilft nur, wenn der ganze Weg (LoxBerry, Netzwerk, Ausgabegerät) über die USV läuft. Die Benachrichtigungen (LoxBerry, E-Mail, Loxone-App) bleiben der verlässliche Weg. Fährt apcupsd den LoxBerry selbst herunter, kann die Abschaltungsansage abbrechen.', '<b>During a power failure, speakers, Echo, router and Wi-Fi are often NOT connected to the UPS</b> – then the announcement does not arrive. It only helps if the whole path (LoxBerry, network, output device) runs through the UPS. The notifications (LoxBerry, email, Loxone app) remain the reliable way. If apcupsd shuts down the LoxBerry itself, the shutdown announcement may be cut off.'),
 ('EINST.ANSAGE_AUDIOSERVER', 'Original-Audioserver: er hat keine Schnittstelle für Plugins – dort sagt Loxone über die Benachrichtigungen der Musterseite an. Ab Werk ist die Ausgabe an; mit der Ausgabeart „aus“ spricht der Dienst nie.', 'Original Audio Server: it has no interface for plugins – there Loxone announces through the notifications of the sample page. The output is on by default; with the output type “off” the service never speaks.'),
 ('EINST.ANSAGE_ANLAESSE', 'Ansagen bei', 'Announce on'),
 ('EINST.ANSAGE_AUSFALL', 'Stromausfall (dringend)', 'power failure (urgent)'),
 ('EINST.ANSAGE_RUECKKEHR', 'Strom wieder da (nur nach einer angesagten Störung)', 'power back (only after an announced failure)'),
 ('EINST.ANSAGE_VORWARNUNG', 'Vorwarnung (Akku bald leer, dringend)', 'advance warning (battery low soon, urgent)'),
 ('EINST.ANSAGE_ABSCHALTUNG', 'Abschaltung beginnt (dringend)', 'shutdown begins (urgent)'),
 ('EINST.ANSAGE_ANLAESSE_HILFE', 'Je Abfrage höchstens eine Ansage, die dringendste. Stromausfall, Vorwarnung und Abschaltung gehen „dringend“ hinaus: Sie sprechen auch in der Nachtruhe, und Alexa NG übergeht „Bitte nicht stören“. „Netz wieder da“ spricht nur nach einem angesagten Ausfall und nicht nachts. Verbindungsverlust zur USV und Akkutausch werden nicht angesagt – dafür gibt es die Benachrichtigungen.', 'At most one announcement per query, the most urgent one. Power failure, advance warning and shutdown go out as “urgent”: they also speak during quiet hours, and Alexa NG overrides “Do not disturb”. “Mains back” only speaks after an announced failure and not at night. Lost connection to the UPS and battery replacement are not announced – the notifications are there for that.'),
 ('EINST.ANSAGE_SPERRE', 'Derselbe Anlass höchstens alle … Sekunden', 'Same occasion at most every … seconds'),
 ('EINST.ANSAGE_SPERRE_HILFE', '60 bis 3600, ab Werk 600. Schützt vor einer Ansage je Umschaltung bei unruhigem Netz; je Ausfall kommt die Vorwarnung und die Abschaltungsansage ohnehin höchstens einmal.', '60 to 3600, default 600. Prevents one announcement per transfer on an unsteady mains; per failure the advance warning and the shutdown announcement come at most once anyway.'),
 ('EINST.ANSAGE_TEST', 'Testansage', 'Test announcement'),
 ('EINST.ANSAGE_TEST_HILFE', 'Spricht den Testsatz über die <b>gespeicherte</b> Ausgabeart – erst speichern, dann testen.', 'Speaks the test sentence through the <b>saved</b> output type – save first, then test.'),
 ('EINST.K_TESTANSAGE', 'Testansage sprechen', 'Speak test announcement'),
 ('EINST.ANSAGE_TEST_OK', 'Testansage gesendet.', 'Test announcement sent.'),
 ('EINST.ANSAGE_TEST_NICHTS', 'Testansage nicht gesendet: %s', 'Test announcement not sent: %s'),
 ('EINST.ANSAGE_TEST_FEHL', 'Testansage gescheitert: %s', 'Test announcement failed: %s'),
 ('EINST.W_ANSAGE', '%s: %s', '%s: %s'),
 ('EINST.ZWEITSCHRIFT_FEHLT', 'Gespeichert, aber die Zweitschrift neben dem Konfigurationsordner ließ sich nicht aktualisieren – ein Update spielte im Notfall den älteren Stand ein.', 'Saved, but the second copy next to the configuration folder could not be updated – in an emergency an update would restore the older state.'),
 ('EINST.SICH_TOKEN', 'Die Datei trägt ein Sprechtoken (%s) – sie stammt nicht aus „Einstellungen sichern“.', 'The file contains a speech token (%s) – it does not come from “Back up settings”.'),
 ('EINST.SICH_WAHLFREI', 'Nicht in der Sicherung, unverändert geblieben (neu seit 1.2.23): %s', 'Not in the backup, left unchanged (new since 1.2.23): %s'),
 ('LOXONE.V2_HAKEN_TEXT', 'MQTT-Gateway Fassung 2: diese %d Datenpunkte anhaken (so viele brauchen die zwei Musterseiten); die beiden mit „Noncached“ zusätzlich auf Noncached stellen.', 'MQTT gateway version 2: tick these %d data points (that many are needed by the two sample pages); set the two marked “Noncached” to Noncached as well.'),
 ('LOXONE.V2_NONCACHED', 'Noncached', 'Noncached'),
 ('LOXONE.V2_HAUS_HINWEIS', "<span class='sm-mono'>haus/usv/stufe</span> (Reiter Einstellungen, ab Werk aus) liegt außerhalb des Präfixes und ist für andere Plugins gedacht; wer es in Loxone sehen will, hakt es unter Fassung 2 von Hand an.", "<span class='sm-mono'>haus/usv/stufe</span> (Settings tab, off by default) lies outside the prefix and is meant for other plugins; whoever wants to see it in Loxone ticks it by hand under version 2."),
 ('LOXONE.NT_NAME', 'Name in Loxone', 'Name in Loxone'),
 ('LOXONE.NT_BAUFORM', 'Anlegen als', 'Create as'),
 ('LOXONE.NT_VI', 'Virtueller Eingang', 'Virtual input'),
 ('LOXONE.NT_BEREICH', 'Bereich', 'Range'),
 ('LOXONE.NT_FEHLWERT', 'Fehlwert', 'Missing value'),
 ('LOXONE.NT_V2', 'Gateway V2', 'Gateway V2'),
 ('LOXONE.NT_HAKEN', 'Haken', 'tick'),
 ('LOXONE.NT_HAKEN_NC', 'Haken, Noncached', 'tick, Noncached'),
 ('LOXONE.NT_MUSTER', 'Musterseite', 'Sample page'),
 ('LOXONE.NT_BESTAND', 'Bestand – für neue Projekte status_zaehler bzw. status_ok nehmen', 'legacy – for new projects use status_zaehler or status_ok'),
 ('LOXONE.K_NAMEN_KOPIEREN', 'Namen der Musterseiten kopieren', 'Copy names of the sample pages'),
 ('LOXONE.NAMEN_HINWEIS', 'Zahlen als <b>Virtueller Eingang</b> (Peripherie → Virtuelle Eingänge), „Als Digitaleingang“ <b>nicht</b> anhaken – sonst gehen -1 und die Stufen 2 und 3 verloren; Texte als <b>Virtueller Texteingang</b>, „In Visualisierung verwenden“ an. Der Name muss genau stimmen – das MQTT-Gateway liefert nur an diesen Namen. Der LoxBerry-Benutzer des Gateways braucht im Miniserver die Rechte dafür. Fehlwerte: -1 = keine Aussage (apcupsd erreicht die USV nicht, antwortet nicht oder das Plugin ist ausgeschaltet), -999 = Temperatur fehlt, „-“ bei Texten. Spalte Musterseite: 1 = „APC-UPS NG“, 2 = „APC-UPS NG Akku und Netz“.', 'Numbers as <b>virtual input</b> (Periphery → Virtual Inputs), do <b>not</b> tick “Use as digital input” – otherwise -1 and levels 2 and 3 are lost; texts as <b>virtual text input</b>, “Use in visualisation” on. The name must match exactly – the MQTT gateway only delivers to this name. The LoxBerry user of the gateway needs the rights for it in the Miniserver. Missing values: -1 = no statement (apcupsd cannot reach the UPS, does not answer or the plugin is switched off), -999 = temperature missing, “-” for texts. Column sample page: 1 = “APC-UPS NG”, 2 = “APC-UPS NG Akku und Netz”.'),
 ('LOXONE.VORLAGE_ENTFALLEN', 'Diese Vorlage gibt es seit 1.2.23 nicht mehr – die Eingänge legen Sie nach der Namenstabelle im Reiter Einbindung in Loxone an (Schritt 3).', 'This template no longer exists since 1.2.23 – create the inputs according to the name table in the Loxone integration tab (step 3).'),
 ('LOXONE.ALTER_WEG_ZU', 'Bestehende Anlagen: HTTP-Endpunkt (XML)', 'Existing installations: HTTP endpoint (XML)'),
 ('LOXONE.ENDPUNKT_EIN', 'HTTP-Endpunkt für Loxone annehmen (alter Weg, XML)', 'Accept HTTP endpoint for Loxone (old path, XML)'),
 ('LOXONE.ENDPUNKT_EIN_HILFE', 'Nur für Anlagen, die die XML-Seite noch selbst abholen. Ausgeschaltet antwortet die Adresse mit HTTP 403 und ruft apcaccess nicht auf. Ab Werk aus; ein Update lässt ihn bei bestehenden Anlagen an. Die Seite nennt Modell und Seriennummer der USV jedem im Heimnetz.', 'Only for installations that still fetch the XML page themselves. When switched off the address answers with HTTP 403 and does not call apcaccess. Off by default; an update leaves it on for existing installations. The page shows model and serial number of the UPS to anyone in the home network.'),
 ('LOXONE.ENDPUNKT_AN', 'HTTP-Endpunkt eingeschaltet – die XML-Seite antwortet.', 'HTTP endpoint switched on – the XML page answers.'),
 ('LOXONE.ENDPUNKT_AUS', 'HTTP-Endpunkt ausgeschaltet – die XML-Seite antwortet mit HTTP 403.', 'HTTP endpoint switched off – the XML page answers with HTTP 403.'),
 ('TEST.EP_AUS', 'aus (gewollt) – im Reiter Einbindung in Loxone abgeschaltet; nicht aufgerufen', 'off (intended) – switched off in the Loxone integration tab; not called'),
 ('TEST.V_MQTT_ENTFALLEN', 'Die Vorlage für den MQTT-Weg ist seit 1.2.23 entfallen – Namenstabelle im Reiter Einbindung in Loxone.', 'The template for the MQTT path has been dropped since 1.2.23 – name table in the Loxone integration tab.'),
 ('TEST.F_NAMEN', 'Stimmt die Namenstabelle (Gateway-Namen, Haken)?', 'Is the name table right (gateway names, ticks)?'),
 ('TEST.A_NAMEN', '%d Namen aus der Themenliste, %d Haken für Gateway V2, davon %d Noncached', '%d names from the topic list, %d ticks for gateway V2, %d of them Noncached'),
 ('TEST.A_NAMEN_FALSCH', 'nein — ohne gesendetes Thema oder falsch gebildet: %s', 'no — without a sent topic or built wrongly: %s'),
 ('TEST.F_ANSAGE', 'Sprachausgabe bei Stromausfall', 'Voice announcement on power failure'),
 ('TEST.F_ANLAESSE', 'Anlässe der Sprachausgabe', 'Occasions of the announcement'),
 ('TEST.A_ANLAESSE', 'Anlässe: %s; Sperrzeit %s s.', 'Occasions: %s; lock time %s s.'),
 ('TEST.A_ANSAGE_DIENST', 'Letzte Ansage des Dienstes: %s, %s, vor %d s.', 'Last announcement of the service: %s, %s, %d s ago.'),
 ('TEST.A_ANSAGE_DIENST_KEINE', 'Der Dienst hat noch nichts angesagt.', 'The service has not announced anything yet.'),
 ('TEST.A_ANSAGE_MODUL_FEHLT', 'nein — sprachausgabe.php fehlt neben ap_lib.php', 'no — sprachausgabe.php is missing next to ap_lib.php'),
 ('TEST.F_HAUS', 'Haus-Thema haus/usv/stufe', 'House topic haus/usv/stufe'),
 ('TEST.A_HAUS_AUS', 'aus (ab Werk)', 'off (default)'),
 ('TEST.A_HAUS_AUS_MERKER', 'aus – das Thema steht noch am Broker; der Dienst räumt es ab (neuer Versuch alle zehn Minuten)', 'off – the topic is still on the broker; the service removes it (new attempt every ten minutes)'),
 ('TEST.A_HAUS_OHNE_MQTT', 'eingeschaltet, wirkt aber nur mit MQTT (Reiter MQTT)', 'switched on, but only works with MQTT (MQTT tab)'),
 ('TEST.A_HAUS_AN', 'ja — Stufe %s wird gesendet, das Lebenszeichen haus/usv/zaehler läuft je Abfrage', 'yes — level %s is being sent, the heartbeat haus/usv/zaehler runs with every query'),
 ('TEST.A_HAUS_NOCH_NICHT', 'eingeschaltet, noch nicht gesendet – der Dienst sendet beim nächsten Lauf', 'switched on, not sent yet – the service sends on its next run'),
 ('ANSAGE_TEXT.AUSFALL', 'Stromausfall. Die USV versorgt die Geräte aus dem Akku. Ladung %1$s Prozent, noch etwa %2$s Minuten.', 'Power failure. The UPS is supplying the devices from the battery. Charge %1$s percent, about %2$s minutes left.'),
 ('ANSAGE_TEXT.AUSFALL_OHNE', 'Stromausfall. Die USV versorgt die Geräte aus dem Akku.', 'Power failure. The UPS is supplying the devices from the battery.'),
 ('ANSAGE_TEXT.RUECKKEHR', 'Der Strom ist wieder da. Die USV lädt den Akku.', 'Power is back. The UPS is charging the battery.'),
 ('ANSAGE_TEXT.VORWARNUNG', 'Achtung: Der Akku der USV ist bald leer, noch etwa %s Minuten. Nicht benötigte Geräte jetzt ausschalten.', 'Attention: the UPS battery will soon be empty, about %s minutes left. Switch off devices that are not needed now.'),
 ('ANSAGE_TEXT.VORWARNUNG_OHNE', 'Achtung: Der Akku der USV ist bald leer. Nicht benötigte Geräte jetzt ausschalten.', 'Attention: the UPS battery will soon be empty. Switch off devices that are not needed now.'),
 ('ANSAGE_TEXT.ABSCHALTUNG', 'Achtung: Die Abschaltung beginnt. Geräte an der USV gehen gleich aus.', 'Attention: the shutdown begins. Devices on the UPS will switch off shortly.'),
 # Drift-Abgleich 06.11.2026: wortgleich aus APC-UPS 1.2.29 (templates/lang/language_*.ini)
 ('ALLGEMEIN.KACHEL_MQTT_HILFE', 'Veröffentlichung dieses Plugins; Autostart des Gateways: %s', 'Publishing by this plugin; gateway autostart: %s'),
 ('TEST.F_V2_HAKEN', 'Gateway V2: sind alle Datenpunkte der Hakenliste angehakt?', 'Gateway V2: are all data points of the tick list ticked?'),
 ('TEST.V2_AUS', 'trifft nicht zu – die MQTT-Veröffentlichung dieses Plugins ist aus.', 'not applicable – MQTT publishing of this plugin is switched off.'),
 ('TEST.V2_V1', 'trifft nicht zu (MQTT-Gateway V1).', 'not applicable (MQTT gateway V1).'),
 ('TEST.V2_UNKLAR', 'nicht feststellbar (Gateway-Fassung oder config/system/subscriptions.json nicht lesbar).', 'cannot be determined (gateway version or config/system/subscriptions.json not readable).'),
 ('TEST.V2_LEER', 'nicht feststellbar – die Hakenliste ist leer (Themenliste des Plugins nicht lesbar).', 'cannot be determined – the tick list is empty (topic list of the plugin not readable).'),
 ('TEST.V2_ZAHL', '%d von %d Datenpunkten angehakt.', '%d of %d data points ticked.'),
 ('TEST.V2_FEHLT', 'Es fehlen: %s.', 'Missing: %s.'),
 ('TEST.V2_NC_FEHLT', 'Noncached fehlt: %s.', 'Noncached missing: %s.'),
 ('TEST.V2_NC_ZUVIEL', 'Noncached zu viel: %s.', 'Noncached not expected: %s.'),
]


def _g16_anwenden(t, weg, setzen):
    """Schluessel streichen, vorhandene Werte ersetzen (an ihrer Stelle), neue anhaengen."""
    neu = {k: (de, en) for k, de, en in setzen}
    aus = []
    for k, de, en in t:
        if k in weg:
            continue
        if k in neu:
            de, en = neu.pop(k)
        aus.append((k, de, en))
    for k, de, en in setzen:
        if k in neu:
            aus.append((k, de, en))
    return aus


T = _g16_anwenden(T, set(_G16_ENTFALLEN), _G16_SETZEN)

# ---------------------------------------------------------------------------
# [THEMA] - kurze Beschriftung. Wandert als Comment in die Loxone-Vorlage und
# wird dort zum ANZEIGENAMEN der Kachel: deshalb Beschriftung, nicht Satz.
# ---------------------------------------------------------------------------
THEMA = [
 ('status',                'Zustandstext der USV', 'UPS state text'),
 ('data_valid',            'Werte brauchbar', 'Values usable'),
 ('comm_lost',             'Verbindung abgerissen', 'Connection lost'),
 ('on_line',               'Netzbetrieb', 'On mains'),
 ('on_battery',            'Akkubetrieb', 'On battery'),
 ('alarm_level',           'Alarmstufe 0-3', 'Alarm level 0-3'),
 ('shutdown_pending',      'Abschaltung steht bevor', 'Shutdown imminent'),
 ('battery_charge',        'Akkuladung', 'Battery charge'),
 ('time_left',             'Restlaufzeit', 'Runtime left'),
 ('line_voltage',          'Netzspannung', 'Mains voltage'),
 ('output_voltage',        'Ausgangsspannung', 'Output voltage'),
 ('line_frequency',        'Netzfrequenz', 'Mains frequency'),
 ('load_percent',          'Auslastung', 'Load'),
 ('load_watt',             'Last geschätzt', 'Load estimated'),
 ('nominal_power',         'Nennleistung', 'Rated power'),
 ('battery_voltage',       'Akkuspannung', 'Battery voltage'),
 ('nominal_battery_volt',  'Akku-Nennspannung', 'Nominal battery voltage'),
 ('internal_temp',         'Innentemperatur', 'Internal temperature'),
 ('replace_battery',       'Akkutausch fällig', 'Battery replacement due'),
 ('battery_age_months',    'Akkualter', 'Battery age'),
 ('self_test_result',      'Letzter Selbsttest', 'Last self-test'),
 ('self_test_interval',    'Selbsttest-Abstand', 'Self-test interval'),
 ('time_on_battery',       'Zeit im Akkubetrieb', 'Time on battery'),
 ('cumulative_on_battery', 'Akkubetrieb insgesamt', 'Time on battery total'),
 ('transfers',             'Umschaltungen', 'Transfers'),
 ('last_transfer',         'Grund der letzten Umschaltung', 'Reason for last transfer'),
 ('shutdown_charge',       'Abschaltschwelle Ladung', 'Shutdown threshold charge'),
 ('shutdown_minutes',      'Abschaltschwelle Restzeit', 'Shutdown threshold runtime'),
 ('shutdown_timeout',      'Abschaltschwelle Zeitlimit', 'Shutdown threshold timeout'),
 ('status_flag',           'Statusbits roh', 'Status flags raw'),
 ('model',                 'Modell', 'Model'),
 ('serial',                'Seriennummer', 'Serial number'),
 ('battery_date',          'Akku eingebaut am', 'Battery installed on'),
 ('timestamp',             'Zeitpunkt der Messung', 'Time of measurement'),
 ('valid',                 'Letzte Abfrage brauchbar', 'Last query usable'),
 ('service/online',        'Dienst läuft', 'Service running'),
 ('event',                 'Letztes Ereignis', 'Last event'),
 ('last_error',            'Letzte Fehlermeldung', 'Last error message'),
]

# [THEMA_LANG] - die ausfuehrliche Erklaerung. Bleibt in der Oberfläche und
# geht NICHT in die Vorlage. Nur dort, wo eine Beschriftung nicht reicht.
THEMA_LANG = [
 ('data_valid',
  '0 bedeutet COMMLOST: apcaccess liefert dann zwar einen vollständig '
  'aussehenden Datensatz, aber die Zahlen darin sind wertlos.',
  '0 means COMMLOST: apcaccess then returns a complete looking data set, but the '
  'numbers in it are worthless.'),
 ('alarm_level',
  '0 Netzbetrieb, 1 Akkubetrieb, 2 Vorwarnung, 3 apcupsd fährt herunter. Ein '
  'Strich (-), solange die Verbindung zur USV abgerissen ist oder apcaccess '
  'nicht antwortet — eine 0 hieße dort „alles ruhig“, und das weiß niemand.',
  '0 on mains, 1 on battery, 2 advance warning, 3 apcupsd is shutting down. A '
  'dash (-) while the connection to the UPS is lost or apcaccess does not '
  'answer — a 0 would mean „all quiet“ there, and nobody knows that.'),
 ('load_watt',
  'Gerechnet aus Auslastung und Nennleistung. Bleibt leer, wenn die USV keine '
  'Nennleistung meldet.',
  'Calculated from load and rated power. Stays empty if the UPS reports no rated '
  'power.'),
 ('battery_age_months',
  'Aus dem Einbaudatum gerechnet. Bleibt leer, wenn das Datumsformat zweideutig '
  'ist — ein falsches Akkualter wäre schlimmer als keines.',
  'Calculated from the installation date. Stays empty if the date format is '
  'ambiguous — a wrong battery age would be worse than none.'),
 ('status_flag',
  'Das rohe Statusbitfeld von apcupsd, unverändert durchgereicht. Die Bedeutung '
  'der einzelnen Bits ist an dieser Anlage nicht nachgemessen; massgeblich '
  'bleibt der Statustext.',
  'The raw status bit field from apcupsd, passed through unchanged. The meaning '
  'of the individual bits has not been verified on this installation; the status '
  'text remains authoritative.'),
 ('timestamp',
  'Sekunden seit 1970 zum Zeitpunkt der Messung. Damit lässt sich in Loxone '
  'unterscheiden, ob ein Wert frisch ist oder seit Stunden im Broker liegt.',
  'Seconds since 1970 at the time of measurement. This lets Loxone distinguish '
  'whether a value is fresh or has been sitting in the broker for hours.'),
 ('service/online',
  'Der Broker setzt es beim Verbindungsabbruch selbst auf 0 — auch dann, wenn '
  'der Dienst abstürzt.',
  'The broker sets it to 0 itself when the connection breaks — even if the '
  'service crashes.'),
]


# Gruppe 16 (1.2.23): Lebenszeichen status/* in [THEMA], Erklaerungen mit -1 statt leer/Strich.
_G16_THEMA = [
 ('status/zaehler', 'Lebenszeichen', 'Heartbeat'),
 ('status/ok', 'Letzte Abfrage gelungen', 'Last query succeeded'),
 ('status/ts', 'Zeitpunkt des Laufs', 'Time of the run'),
]
_G16_THEMA_LANG = [
 ('alarm_level', '0 Netzbetrieb, 1 Akkubetrieb, 2 Vorwarnung, 3 apcupsd fährt herunter. -1 (keine Aussage), solange die Verbindung zur USV abgerissen ist, apcaccess nicht antwortet oder das Plugin ausgeschaltet ist — eine 0 hieße dort „alles ruhig“, und das weiß niemand.', '0 on mains, 1 on battery, 2 advance warning, 3 apcupsd is shutting down. -1 (no statement) while the connection to the UPS is lost, apcaccess does not answer or the plugin is switched off — a 0 would mean „all quiet“ there, and nobody knows that.'),
 ('load_watt', 'Gerechnet aus Auslastung und Nennleistung. -1, wenn die USV keine Nennleistung meldet.', 'Calculated from load and rated power. -1 if the UPS reports no rated power.'),
 ('battery_age_months', 'Aus dem Einbaudatum gerechnet. -1, wenn das Datumsformat zweideutig ist — ein falsches Akkualter wäre schlimmer als keines.', 'Calculated from the installation date. -1 if the date format is ambiguous — a wrong battery age would be worse than none.'),
 ('timestamp', 'Sekunden seit 1970 zum Zeitpunkt der Messung. Bestand – für neue Projekte status/zaehler nehmen.', 'Seconds since 1970 at the time of measurement. Legacy – for new projects use status/zaehler.'),
 ('valid', 'Bestand – für neue Projekte status/ok nehmen (dort zusätzlich -1, solange seit dem Start noch keine Abfrage lief).', 'Legacy – for new projects use status/ok (there additionally -1 while no query has run since the start).'),
 ('event', 'Das letzte Ereignis – bleibt stehen, bis ein neues kommt (zurückbehalten, gewollt). Kein frisches Ereignis.', 'The last event – stays until a new one comes (retained, intended). Not a fresh event.'),
 ('status/zaehler', 'Zählt bei jedem Lauf des Dienstes eins weiter (0 bis 999), auch bei ausgeschaltetem Plugin; nie zurückbehalten.', 'Counts up by one on every run of the service (0 to 999), also with the plugin switched off; never retained.'),
 ('status/ok', '1 = letzte Abfrage gelungen, 0 = gescheitert oder Plugin ausgeschaltet, -1 = seit dem Start noch keine.', '1 = last query succeeded, 0 = failed or plugin switched off, -1 = none yet since the start.'),
 ('status/ts', 'Unix-Sekunden des Laufs. Nicht für eine Altersrechnung in Loxone verwenden (Ortszeit).', 'Unix seconds of the run. Do not use for an age calculation in Loxone (local time).'),
]
THEMA = _g16_anwenden(THEMA, set(), _G16_THEMA)
THEMA_LANG = _g16_anwenden(THEMA_LANG, set(), _G16_THEMA_LANG)

# ---------------------------------------------------------------------------

def bau(sprache):
    idx = 1 if sprache == 'de' else 2
    ab = {}
    reihenfolge = []
    for schluessel, de, en in T:
        a, s = schluessel.split('.', 1)
        if a not in ab:
            ab[a] = []
            reihenfolge.append(a)
        ab[a].append((s, (de, en)[idx - 1]))
    for k, de, en in THEMA:
        a = 'THEMA'
        if a not in ab:
            ab[a] = []
            reihenfolge.append(a)
        ab[a].append((k.upper().replace('/', '_').replace('-', '_'), (de, en)[idx - 1]))
    for k, de, en in THEMA_LANG:
        a = 'THEMA_LANG'
        if a not in ab:
            ab[a] = []
            reihenfolge.append(a)
        ab[a].append((k.upper().replace('/', '_').replace('-', '_'), (de, en)[idx - 1]))

    zeilen = [
        '; APC-UPS NG - Sprachdatei ' + sprache.upper(),
        ';',
        '; ERZEUGT von Werkzeuge/ap_sprache_erzeugen.py. Nicht von Hand aendern -',
        '; die naechste Erzeugung ueberschreibt es. Beide Sprachen kommen aus',
        '; EINER Quelle; ein Schlüssel kann deshalb nicht nur in einer stehen.',
        ';',
        '; Jeder Wert steht in doppelten Anfuehrungszeichen. Innerhalb eines',
        '; Wertes darf KEIN doppeltes Anfuehrungszeichen mehr stehen -',
        '; HTML-Attribute deshalb einfach quotieren (class=\'sm-mono\').',
        '',
    ]
    for a in reihenfolge:
        zeilen.append('[' + a + ']')
        for s, w in ab[a]:
            zeilen.append('%s = "%s"' % (s, w))
        zeilen.append('')
    # Gruppe 16 (1.2.23): der Abschnitt [ANSAGE] der gemeinsamen Sprachausgabe - wortgleich aus
    # Werkzeuge/gemeinsam_pruefen.py (ini_abschnitt), damit gemeinsam_pruefen.py ihn als gleich meldet.
    import gemeinsam_pruefen
    zeilen.append(gemeinsam_pruefen.ini_abschnitt(sprache).rstrip('\n'))
    zeilen.append('')
    return '\n'.join(zeilen).rstrip('\n') + '\n'


gesamt = 0

# Wache gegen stillen Schluesselverlust - eine Quelle fuer alle Erzeuger.
#
# Werkzeuge/sprachwache.py legt sich vor jeden Schreibweg und vergleicht die
# .ini, die geschrieben werden soll, mit der, die schon dasteht. Verschwaende
# ein Schluessel, bricht der Lauf ab, BEVOR etwas geschrieben ist; ein
# geaenderter WERT wird gemeldet und durchgelassen - einen Wert zu aendern ist
# die Aufgabe eines Erzeugers, einen Schluessel zu verlieren nie.
#
# Bis zum 13.09.2026 stand hier eine eigene, aeltere Fassung derselben Wache:
# sie hielt auch bei geaenderten Werten an und kannte kein SPRACHWACHE=aus.
# Der Anlass, aus dem die gemeinsame Wache gebaut wurde, war GENAU dieser
# Erzeuger (06.09.2026: 320 erzeugte gegen 337 vorhandene Schluessel) - er war
# als einziger nie darauf umgestellt.
#
# Ein Erzeugerkopf in einer Datei ist eine Aussage ueber die Vergangenheit,
# nie ueber den heutigen Stand des Erzeugers.
#
# Absichtlich loeschen:  SPRACHWACHE=aus python3 <erzeuger>.py <ordner>
import sprachwache
sprachwache.einhaengen()

texte = {sp: bau(sp) for sp in ('de', 'en')}
for sp in ('de', 'en'):
    text = texte[sp]
    # An LF trennen, nicht an CRLF. Beim Umstellen der Ausgabe stand hier
    # noch die alte Trennung - das Ergebnis war 1 statt 320, weil die
    # ganze Datei ein einziges Element ergab. Dieselbe Klasse wie die
    # Zeilenenden-Vergleiche in REGELN_1, nur andersherum.
    n = len([z for z in text.split('\n') if ' = "' in z])
    gesamt = n
    print('language_%s.ini  %d Wertzeilen, %d Byte' % (sp, n, len(text.encode('utf-8'))))

# --- Wachen: das, was die Hausregeln verlangen, hier gemessen --------------
# Erst pruefen, dann schreiben (06.11.2026): bis dahin liefen diese Wachen
# ueber die schon geschriebenen Dateien - ein Wert mit geradem Anfuehrungs-
# zeichen stand also auf der Platte, bevor die Rueckgabe 1 kam.
fehl = 0
for sp in ('de', 'en'):
    b = texte[sp].encode('utf-8')
    t = b.decode('utf-8')
    crlf = b.count(b'\r\n')
    # Die Wache ist mitgedreht: frueher schlug sie bei LF an, jetzt bei CRLF.
    if crlf:
        print('FEHL %s: %d CRLF - die Dateien sind seit 1.2.1 LF' % (sp, crlf))
        fehl += 1
    for i, z in enumerate(t.split('\n'), 1):
        if ' = "' not in z:
            continue
        if z.count('"') != 2:
            print('FEHL %s Zeile %d: %d Anfuehrungszeichen: %s' % (sp, i, z.count('"'), z[:80]))
            fehl += 1
        if not re.match(r'^[A-Z0-9_]+ = ".*"$', z):
            print('FEHL %s Zeile %d passt nicht auf SCHLUESSEL = "...": %s' % (sp, i, z[:80]))
            fehl += 1
print('Zeilenenden LF, je %d Wertzeilen, %d Verstoesse' % (gesamt, fehl))
if fehl:
    print('Es wurde NICHTS geschrieben.')
    sys.exit(1)
for sp in ('de', 'en'):
    pfad = os.path.join(ZIEL, 'language_%s.ini' % sp)
    with io.open(pfad, 'wb') as fh:
        fh.write(texte[sp].encode('utf-8'))
    print('Geschrieben: %s' % pfad)
sys.exit(0)
