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
 ('TEXT.HOST_UNGUELTIG',
  'Der eingetragene USV-Host passt nicht auf Rechnername oder Adresse und wurde '
  'nicht übernommen. Erlaubt sind Buchstaben, Ziffern, Punkt, Bindestrich und '
  'Unterstrich, notfalls mit :Port.',
  'The UPS host you entered is neither a host name nor an address and was not '
  'saved. Allowed are letters, digits, dot, hyphen and underscore, optionally '
  'with :port.'),
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
  'Der Empfänger ist weder ein Benutzer dieses Rechners noch eine gültige '
  'E-Mail-Adresse. Eingetragen wurde deshalb root. Alles Übrige wurde '
  'gespeichert.',
  'The recipient is neither a user of this machine nor a valid email address. '
  'root was saved instead. Everything else has been saved.'),
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
  'neue Fassung des Plugins zu warten. Ab Werk leer.',
  'Comma separated field names, spelled exactly as in the output of apcaccess. '
  'They are published unchanged under '
  '<span class=\'sm-mono\'>&lt;prefix&gt;/raw/&lt;FIELD&gt;</span>. This lets you '
  'fetch values that only certain models provide, without waiting for a new '
  'version of the plugin. Empty by default.'),
 ('MQTT.ROHFELD_ABGEWIESEN',
  'Diese Angaben sehen nicht wie apcaccess-Feldnamen aus und wurden nicht '
  'übernommen: %s. Alles Übrige wurde gespeichert.',
  'These entries do not look like apcaccess field names and were not saved: %s. '
  'Everything else has been saved.'),
 ('MQTT.ABO_UEBERSCHRIFT', 'Das Abo im MQTT-Gateway eintragen',
                           'Enter the subscription in the MQTT gateway'),
 ('MQTT.ABO_SATZ', 'Dieses Abo gehört in das MQTT-Gateway',
                   'This subscription belongs in the MQTT gateway'),
 ('MQTT.ABO_WEG',
  'Einzutragen unter <b>System → MQTT Gateway</b> im Feld <i>Subscriptions</i>. '
  'Der MQTT-Gateway ist seit LoxBerry 3 Bestandteil des Systems.',
  'Enter it under <b>System → MQTT Gateway</b> in the <i>Subscriptions</i> field. '
  'Since LoxBerry 3 the MQTT gateway is part of the system.'),
 ('MQTT.ABO_OHNE',
  'Ohne diesen Eintrag kommt am Miniserver nichts an.',
  'Without this entry nothing arrives at the Miniserver.'),
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
 ('LOXONE.SCHRITT2', 'Schritt 2: Abo im MQTT-Gateway eintragen',
                     'Step 2: enter the subscription in the MQTT gateway'),
 ('LOXONE.SCHRITT2_TEXT',
  'Unter <b>System → MQTT Gateway</b> im Feld <i>Subscriptions</i> eintragen:',
  'Under <b>System → MQTT Gateway</b> enter this in the <i>Subscriptions</i> field:'),
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
  'belegt, und ein analoger Eingang auf einem Text zeigt dauerhaft 0. Sie gehen '
  'trotzdem nicht verloren — das MQTT-Gateway legt beim ersten Empfang selbst '
  'einen passenden Eingang an.',
  'The MQTT template creates %d virtual inputs. The %d text topics are '
  'deliberately not included: the rebuilt template format is only proven for '
  'numeric values, and an analogue input on a text permanently shows 0. They are '
  'not lost — the MQTT gateway creates a suitable input itself on first receipt.'),
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
 ('LOXONE.SCHRITT6', 'Schritt 6: Komplette Baustein-Liste zum 1:1-Nachbauen',
                     'Step 6: complete list of blocks to rebuild 1:1'),
 ('LOXONE.BAUSTEINE_VORTEXT',
  'So sieht die vollständige Logik auf der Programmierseite aus — jede Zeile ist '
  'ein Baustein. Alle Bausteine findet man in Loxone Config über die '
  'Baustein-Suche (F5).',
  'This is what the complete logic looks like on the programming page — every row '
  'is one block. All blocks can be found in Loxone Config via the block search (F5).'),
 ('LOXONE.SP_BAUSTEIN', 'Baustein (Typ)', 'Block (type)'),
 ('LOXONE.SP_NAME', 'Name (Vorschlag)', 'Name (suggestion)'),
 ('LOXONE.SP_PARAMETER', 'Parameter', 'Parameters'),
 ('LOXONE.SP_EINGAENGE', 'Eingänge verbinden mit', 'Connect inputs to'),
 ('LOXONE.B_VE', 'Virtueller Eingang', 'Virtual input'),
 ('LOXONE.B_VOM_GATEWAY', 'kommt über das Gateway', 'arrives via the gateway'),
 ('LOXONE.B_ANALOG_MIN', 'analog, Einheit Minuten', 'analogue, unit minutes'),
 ('LOXONE.B_ANALOG_S', 'analog, Sekunden seit 1970', 'analogue, seconds since 1970'),
 ('LOXONE.B_EINVERZ', 'Einschaltverzögerung', 'On delay'),
 ('LOXONE.B_NICHT', 'NICHT', 'NOT'),
 ('LOXONE.B_ODER', 'ODER', 'OR'),
 ('LOXONE.B_BENACHR', 'Benachrichtigung', 'Notification'),
 ('LOXONE.B_SCHWELL', 'Schwellwertschalter', 'Threshold switch'),
 ('LOXONE.B_MERKER', 'Merker (Visu)', 'Flag (visualisation)'),
 ('LOXONE.B_STATUS', 'Status', 'Status'),
 ('LOXONE.E_EINGANG', 'Eingang =', 'Input ='),
 ('LOXONE.N_ENTPRELLT', 'Netzausfall entprellt', 'Power failure debounced'),
 ('LOXONE.N_KEINE_DATEN', 'Keine Verbindung zur USV', 'No connection to the UPS'),
 ('LOXONE.N_SAMMEL', 'Sammelstörung USV', 'Collective UPS fault'),
 ('LOXONE.N_MELDUNG', 'USV-Meldung', 'UPS message'),
 ('LOXONE.N_LASTABWURF', 'Lastabwurf ab Vorwarnung', 'Load shedding from advance warning'),
 ('LOXONE.N_STROMSPAREN', 'Stromsparen aktiv', 'Power saving active'),
 ('LOXONE.N_STATUS', 'USV-Zustand', 'UPS state'),
 ('LOXONE.P_MELDETEXT',
  'Text zum Beispiel „Die USV läuft auf Akku.“',
  'Text for example „The UPS is running on battery.“'),
 ('LOXONE.P_SCHWELL',
  'Ein 2 / Aus 1 — schaltet ein, sobald alarm_level 2 erreicht',
  'On 2 / Off 1 — switches on as soon as alarm_level reaches 2'),
 ('LOXONE.P_VISU', 'Visualisierung EIN', 'Visualisation ON'),
 ('LOXONE.P_STATUS', 'Statustext je Stufe, Visualisierung EIN',
                     'Status text per level, visualisation ON'),
 ('LOXONE.ZU_10',
  'Der Benachrichtigungs-Baustein sendet nur beim Wechsel von Aus auf Ein. '
  'Niemals mehrere Quellen direkt an seinen Eingang legen — eine dauerhaft '
  'aktive Quelle verschluckt sonst alle übrigen. Deshalb erst über ODER '
  'zusammenführen.',
  'The notification block only sends on a change from off to on. Never connect '
  'several sources directly to its input — a permanently active source would '
  'swallow all the others. Combine them with an OR block first.'),
 ('LOXONE.ZU_8',
  'Die Einschaltverzögerung fängt den kurzen Netzwischer ab. Ohne sie meldet '
  'das Haus jeden Spannungseinbruch von zwei Sekunden.',
  'The on delay absorbs short mains dips. Without it the house reports every '
  'two-second voltage drop.'),
 ('LOXONE.ZU_12',
  'Hier hängt der eigentliche Nutzen: ab Stufe 2 bleiben noch die eingestellte '
  'Vorwarnzeit und die Vorwarn-Prozentpunkte, bevor apcupsd herunterfährt. In '
  'dieser Zeit kann der Miniserver Verbraucher gestaffelt abwerfen — erst '
  'Komfort, dann Nebenräume, zuletzt alles außer der Heizungssteuerung.',
  'This is where the actual benefit sits: from level 2 there are still the '
  'configured advance warning time and percentage points left before apcupsd '
  'shuts down. In that time the Miniserver can shed loads in stages — comfort '
  'first, then side rooms, finally everything except the heating control.'),
 ('LOXONE.ZU_6',
  'Loxone rechnet in Sekunden seit dem 1.1.2009, dieses Thema in Sekunden seit '
  '1970. Wer beide vergleichen will, zieht 1230768000 ab.',
  'Loxone counts seconds since 1 January 2009, this topic counts seconds since '
  '1970. To compare the two, subtract 1230768000.'),
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
  'hinausgehen, samt ihrem Alter in Sekunden.',
  'The original version provided an XML page at this address which Loxone fetches '
  'itself. It stays unchanged so that existing installations keep working. Since '
  '1.2.0 it also honours the setting <i>UPS on another machine</i> and, in '
  'addition to the raw fields, provides the derived values in a '
  '<span class=\'sm-mono\'>CALC</span> block — the same ones sent over MQTT, '
  'together with their age in seconds.'),
 ('LOXONE.ALTER_WEG_ADRESSE',
  'Der Rechnername ist ein Vorschlag. Bitte prüfen, unter welchem Namen der '
  'Miniserver den LoxBerry wirklich erreicht.',
  'The host name is a suggestion. Please check under which name the Miniserver '
  'actually reaches the LoxBerry.'),

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
 ('TEST.F_DIENST', 'Läuft der Dienst dieses Plugins?',
                   'Is the service of this plugin running?'),
 ('TEST.A_DIENST_TOT', 'nein — siehe Reiter Logdateien', 'no — see the Log files tab'),
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
 ('TEST.A_WAECHTER_DA', 'ja, cron/cron.05min', 'yes, cron/cron.05min'),
 ('TEST.A_WAECHTER_UNBEKANNT',
  'hier nicht feststellbar — auf dem Gerät liegt er unter system/cron',
  'cannot be determined here — on the device it is under system/cron'),

 # ---------------- TEST: Knoepfe ----------------
 ('TEST.KNOEPFE', 'Weitere Auskünfte', 'Further information'),
 ('TEST.G_ANSEHEN', 'Ansehen', 'View'),
 ('TEST.G_TECHNIK', 'Technische Auskunft', 'Technical details'),
 ('TEST.G_AKTION', 'Löst etwas aus', 'Triggers something'),
 ('TEST.G_AKTION_HILFE',
  'Diese Knöpfe wirken sofort: sie fragen das Gerät ab, legen eine Meldung an '
  'oder greifen in den laufenden Dienst ein.',
  'These buttons take effect immediately: they query the device, create a '
  'notification or interfere with the running service.'),
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
 ('TEST.AB_PRUEF_1', '- Laeuft apcupsd?  systemctl status apcupsd',
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
 ('TEST.UNBEKANNT', 'Unbekannte Aktion', 'Unknown action'),
 ('TEST.UNBEKANNT_LANG', 'Diese Aktion gibt es nicht: %s',
                         'This action does not exist: %s'),
]

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
  '0 Netzbetrieb, 1 Akkubetrieb, 2 Vorwarnung, 3 apcupsd fährt herunter. Leer, '
  'solange die Verbindung zur USV abgerissen ist — eine 0 hieße dort „alles '
  'ruhig“, und das weiß niemand.',
  '0 on mains, 1 on battery, 2 advance warning, 3 apcupsd is shutting down. '
  'Empty while the connection to the UPS is lost — a 0 would mean „all quiet“ '
  'there, and nobody knows that.'),
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
    return '\n'.join(zeilen).rstrip('\n') + '\n'


gesamt = 0
for sp in ('de', 'en'):
    text = bau(sp)
    pfad = os.path.join(ZIEL, 'language_%s.ini' % sp)
    with io.open(pfad, 'wb') as fh:
        fh.write(text.encode('utf-8'))
    # An LF trennen, nicht an CRLF. Beim Umstellen der Ausgabe stand hier
    # noch die alte Trennung - das Ergebnis war 1 statt 320, weil die
    # ganze Datei ein einziges Element ergab. Dieselbe Klasse wie die
    # Zeilenenden-Vergleiche in REGELN_1, nur andersherum.
    n = len([z for z in text.split('\n') if ' = "' in z])
    gesamt = n
    print('%s  %d Wertzeilen, %d Byte' % (pfad, n, len(text.encode('utf-8'))))

# --- Wachen: das, was die Hausregeln verlangen, hier gemessen --------------
fehl = 0
for sp in ('de', 'en'):
    b = io.open(os.path.join(ZIEL, 'language_%s.ini' % sp), 'rb').read()
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
sys.exit(1 if fehl else 0)
