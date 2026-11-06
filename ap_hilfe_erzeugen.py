# -*- coding: utf-8 -*-
"""Erzeugt help_de.ini und help_en.ini aus EINER Quelle.

Wie beim Sprachgenerator: ein Schluessel kann nicht nur in einer Sprache
stehen. Die Hilfe wird ROH ausgegeben (nicht maskiert), Auszeichnung ist
deshalb erlaubt - gerade Anfuehrungszeichen dagegen nicht, sie wuerden den
INI-Wert beenden.

Aufruf:  python3 Werkzeuge/ap_hilfe_erzeugen.py <Plugin-Ordner>

STAND (vb_bild_ap12, 14.10.2026, Welle Bild 12 VOLL / Musterprojekt, APC-UPS NG 1.2.20): K10
nennt die zwei Baustein-Listen im Reiter Einbindung in Loxone; sonst unveraendert.

STAND (vb_g16_ap, 25.10.2026, Gruppe 16 / MQTT, APC-UPS NG 1.2.23): K35, K49, K51, K53 neu gefasst;
K54-K61 neu (Sprachausgabe mit Lautsprecher-Hinweis, Haus-Thema, Lebenszeichen und Fehlwerte).

STAND (Drift-Abgleich, 06.11.2026): angeglichen an APC-UPS 1.2.29, 1 Schluessel neu (K62),
2 Werte geaendert (K55, K59), 0 entfernt. Schreibt erst nach bestandener Pruefung.
"""
import io, os, re, sys

ZIEL = os.path.join(sys.argv[1], 'templates', 'lang')

H = [
 ('K01', 'APC-UPS NG', 'APC-UPS NG'),
 ('K02',
  'Das Plugin liest eine APC-USV über <code>apcupsd</code> aus und meldet '
  'Zustand, Akkuladung, Restlaufzeit, Last und eine gestufte Alarmstufe per '
  'MQTT an den Loxone Miniserver. Bei Stromausfall und Netzrückkehr gibt es '
  'zusätzlich eine Benachrichtigung.',
  'The plugin reads an APC UPS through <code>apcupsd</code> and reports state, '
  'battery charge, remaining runtime, load and a staged alarm level over MQTT '
  'to the Loxone Miniserver. On power failure and return there is also a '
  'notification.'),
 ('K03', 'Voraussetzung: apcupsd muss laufen',
         'Requirement: apcupsd must be running'),
 ('K04',
  'Das Plugin misst nichts selbst — es fragt <code>apcupsd</code> ab, den '
  'Dienst, der mit der USV spricht. Der wird bei der Installation mitgebracht '
  'und gestartet. Zwei Dinge sind dabei zu wissen:',
  'The plugin measures nothing itself — it queries <code>apcupsd</code>, the '
  'service that talks to the UPS. It is installed and started along with the '
  'plugin. There are two things to know:'),
 ('K05',
  'In <code>/etc/default/apcupsd</code> steht nach der Paketinstallation '
  '<code>ISCONFIGURED=no</code>. Auf dem LoxBerry ist das ohne Folgen: apcupsd '
  'startet über systemd, und dessen Unit liest diese Datei nicht (am Gerät '
  'gemessen: <code>ISCONFIGURED=no</code>, und apcupsd läuft). Die Installation '
  'versucht zwar, den Wert auf <code>yes</code> zu setzen, darf die Datei als '
  '<code>loxberry</code> aber nicht schreiben und sagt das im Protokoll — eine '
  'Systemdatei ändert das Plugin damit nicht. Nur wer apcupsd über das alte '
  'init-Skript startet, setzt den Wert von Hand.',
  'After the package installation <code>/etc/default/apcupsd</code> contains '
  '<code>ISCONFIGURED=no</code>. On the LoxBerry this has no effect: apcupsd '
  'starts via systemd, and its unit does not read this file (measured on the '
  'device: <code>ISCONFIGURED=no</code>, and apcupsd is running). The '
  'installation does try to set the value to <code>yes</code>, but as '
  '<code>loxberry</code> it may not write the file and says so in the log — so '
  'the plugin changes no system file. Only whoever starts apcupsd through the '
  'old init script sets the value by hand.'),
 ('K06',
  'Die USV muss per USB angeschlossen und erkannt sein. Im Reiter <i>Test</i> '
  'zeigt <i>apcupsd prüfen</i> die angeschlossenen USB-Geräte.',
  'The UPS must be connected by USB and recognised. In the <i>Test</i> tab '
  '<i>Check apcupsd</i> shows the connected USB devices.'),
 ('K07', 'Einrichtung in sieben Schritten', 'Setup in seven steps'),
 ('K08',
  '<b>Reiter Test → Jetzt abfragen.</b> Kommen dort Werte, ist der schwierige '
  'Teil erledigt. Die Selbstprüfung darüber beantwortet Zeile für Zeile, was '
  'noch fehlt.',
  '<b>Test tab → Query now.</b> If values arrive there, the hard part is done. '
  'The self-check above answers line by line what is still missing.'),
 ('K09',
  '<b>Das Abo im MQTT-Gateway prüfen.</b> Seit 1.2.14 trägt das Plugin es selbst '
  'ein (Datei <i>mqtt_subscriptions.cfg</i>), das Gateway liest sie; auch nach '
  'einem Wechsel des Themenpräfixes wird sie nachgeführt. Kommt am Miniserver '
  'nichts an, zuerst unter <i>System → MQTT Gateway → Subscriptions</i> nachsehen, '
  'ob die Themengruppe dort steht; sie steht im Reiter <i>MQTT</i> zum Vergleich.',
  '<b>Check the subscription in the MQTT gateway.</b> Since 1.2.14 the plugin '
  'enters it itself (file <i>mqtt_subscriptions.cfg</i>) and the gateway reads '
  'it; it is also updated after a change of the topic prefix. If nothing arrives '
  'at the Miniserver, first check under <i>System → MQTT Gateway → '
  'Subscriptions</i> whether the topic group is listed; the <i>MQTT</i> tab shows '
  'it for comparison.'),
 ('K10',
  '<b>Reiter Einbindung in Loxone → Vorlage herunterladen</b> und in Loxone '
  'Config über <i>Vorlage einfügen</i> einlesen. Die zwei Baustein-Listen im '
  'selben Reiter (Schritt 6) zeigen, was danach zu verdrahten ist – Zustand, '
  'Störung und Stromausfall sowie Akku, Netz und Last –, je mit Bild und '
  'Schritt-für-Schritt-Anleitung.',
  '<b>Loxone integration tab → download the template</b> and read it into '
  'Loxone Config via <i>Insert template</i>. The two block lists in the same '
  'tab (step 6) show what to wire up afterwards – state, faults and power '
  'failure as well as battery, mains and load –, each with a picture and '
  'step-by-step instructions.'),
 ('K11', 'Was veröffentlicht wird', 'What is published'),
 ('K12',
  'Die vollständige Liste mit Art, Einheit und Bedeutung steht im Reiter '
  '<i>MQTT</i>. <b>Nicht alle Themen sind retained.</b> Zustände wie Modell, '
  'Seriennummer oder <code>on_battery</code> bleiben im Broker liegen, damit '
  'ein neu verbundener Abnehmer sie sofort kennt. Messwerte wie die '
  'Restlaufzeit dagegen nicht: wer sich nach einer Stunde neu verbindet, bekäme '
  'sonst eine stundenalte Restlaufzeit serviert und hielte sie für aktuell. '
  'Welche Themen retained sind, sagt die Spalte in der Tabelle; wie frisch ein '
  'Wert ist, sagt <code>timestamp</code>.',
  'The complete list with type, unit and meaning is in the <i>MQTT</i> tab. '
  '<b>Not all topics are retained.</b> States such as model, serial number or '
  '<code>on_battery</code> stay in the broker so that a newly connected '
  'subscriber knows them immediately. Measurements such as the remaining '
  'runtime are not: anyone reconnecting after an hour would otherwise be served '
  'an hour-old runtime and take it for current. Which topics are retained is '
  'shown by the column in the table; how fresh a value is, is told by '
  '<code>timestamp</code>.'),
 ('K13', 'Was sich zum Schalten anbietet', 'What is useful for switching'),
 ('K14',
  '<code>alarm_level</code> ist der Wert, für den sich der Aufwand lohnt: 0 '
  'Netzbetrieb, 1 Akkubetrieb, 2 Vorwarnung, 3 apcupsd fährt jetzt herunter. '
  'Die Schwellen für 2 und 3 liest das Plugin aus apcupsd selbst aus, sie sind '
  'nicht geraten. Damit kann der Miniserver Verbraucher gestaffelt abwerfen, '
  'statt vom Systemhalt überrascht zu werden. <code>on_battery</code> genügt '
  'für die einfache Meldung, <code>time_left</code> sagt, wie lange noch Zeit '
  'bleibt.',
  '<code>alarm_level</code> is the value worth the effort: 0 on mains, 1 on '
  'battery, 2 advance warning, 3 apcupsd is shutting down now. The thresholds '
  'for 2 and 3 are read from apcupsd itself, they are not guessed. This lets '
  'the Miniserver shed loads in stages instead of being surprised by the halt. '
  '<code>on_battery</code> is enough for a simple message, '
  '<code>time_left</code> says how much time is left.'),
 ('K15', 'Der alte XML-Weg', 'The old XML path'),
 ('K16',
  'Die Originalfassung stellte eine XML-Seite bereit, die Loxone selbst '
  'abholt. Diese Seite gibt es weiterhin und liefert dieselbe Struktur — wer '
  'sie eingebunden hat, muss nichts ändern. Seit 1.2.0 beachtet sie auch die '
  'Einstellung <i>USV auf einem anderen Rechner</i> und liefert die '
  'abgeleiteten Werte im Block <code>CALC</code> mit, samt ihrem Alter in '
  'Sekunden. Seit 1.2.14 stehen am Anfang des Blocks <code>OK</code> und '
  '<code>ALTER</code>: <code>OK</code> fällt auf 0, sobald die Werte älter sind '
  'als das Dreifache des Abfragetakts (etwa weil der Dienst steht), '
  '<code>ALTER</code> nennt das Alter in Sekunden. Für neue Anlagen ist MQTT '
  'trotzdem der bessere Weg: der '
  'Miniserver muss nichts abfragen, und es kommen deutlich mehr Größen heraus.',
  'The original version provided an XML page that Loxone fetches itself. That '
  'page still exists and returns the same structure — anyone who has wired it '
  'up need not change anything. Since 1.2.0 it also honours the setting <i>UPS '
  'on another machine</i> and includes the derived values in a <code>CALC</code> '
  'block, together with their age in seconds. Since 1.2.14 the block starts '
  'with <code>OK</code> and <code>ALTER</code>: <code>OK</code> drops to 0 as '
  'soon as the values are older than three times the query interval (for '
  'instance because the service has stopped), <code>ALTER</code> gives the age '
  'in seconds. For new installations MQTT is '
  'still the better path: the Miniserver has to query nothing, and considerably '
  'more values are available.'),
 ('K17', 'Benachrichtigungen', 'Notifications'),
 ('K18',
  'Beim Wechsel zwischen Netz- und Akkubetrieb legt das Plugin eine Meldung im '
  'LoxBerry-Benachrichtigungsbereich ab (Glockensymbol oben). Ob das '
  'funktioniert, zeigt im Reiter <i>Test</i> der Knopf <i>Testmeldung '
  'ablegen</i>. Seit 1.2.0 wird auch der Zustand beim Start des Dienstes '
  'gemeldet — wer den Dienst während eines Stromausfalls neu startete, bekam '
  'vorher keine Meldung, weil es keinen Wechsel gab.',
  'On a change between mains and battery operation the plugin creates a message '
  'in the LoxBerry notification area (bell symbol at the top). Whether this '
  'works is shown by the <i>Create test notification</i> button in the '
  '<i>Test</i> tab. Since 1.2.0 the state at service start is reported as well — '
  'previously, restarting the service during a power failure produced no '
  'message because there was no change.'),
 ('K19',
  'Zusätzlich kann eine E-Mail verschickt werden. Das setzt voraus, dass auf '
  'dem LoxBerry ein Mailversand eingerichtet ist — sonst passiert '
  'stillschweigend nichts, und der Grund steht im Protokoll.',
  'An email can be sent in addition. This requires a working mail setup on the '
  'LoxBerry — otherwise nothing happens silently, and the reason is in the log.'),
 ('K20', 'Notabschaltung bei leerem Akku', 'Emergency shutdown on empty battery'),
 ('K21',
  'Das entscheidet <b>apcupsd</b>, nicht dieses Plugin. Die Schwellen stehen '
  'in <code>/etc/apcupsd/apcupsd.conf</code> unter <code>BATTERYLEVEL</code>, '
  '<code>MINUTES</code> und <code>TIMEOUT</code>. Das Plugin liest sie aus und '
  'zeigt die <b>tatsächlich geltenden</b> Werte im Reiter <i>Einstellungen</i> '
  'an — es nennt hier bewusst keine Vorgabewerte, weil sie je nach '
  'Paketfassung und Gerät verschieden sind.',
  'This is decided by <b>apcupsd</b>, not by this plugin. The thresholds are in '
  '<code>/etc/apcupsd/apcupsd.conf</code> under <code>BATTERYLEVEL</code>, '
  '<code>MINUTES</code> and <code>TIMEOUT</code>. The plugin reads them and '
  'shows the <b>values actually in force</b> in the <i>Settings</i> tab — it '
  'deliberately quotes no defaults here, because they differ between package '
  'versions and devices.'),
 ('K22', 'USV an einem anderen Rechner', 'UPS on another machine'),
 ('K23',
  'Hängt die USV nicht am LoxBerry selbst, sondern an einem anderen Rechner '
  'mit apcupsd, lässt sich dessen Adresse im Reiter <i>Einstellungen</i> unter '
  '<i>USV auf einem anderen Rechner</i> eintragen. Dort muss apcupsd den '
  'Netzzugriff erlauben (<code>NETSERVER on</code>). Seit 1.2.0 gilt die '
  'Einstellung auch für den alten XML-Weg; vorher fragte der stillschweigend '
  'die örtliche USV ab.',
  'If the UPS is not connected to the LoxBerry itself but to another machine '
  'running apcupsd, its address can be entered in the <i>Settings</i> tab under '
  '<i>UPS on another machine</i>. apcupsd there must allow network access '
  '(<code>NETSERVER on</code>). Since 1.2.0 the setting also applies to the old '
  'XML path; before that it silently queried the local UPS.'),
 ('K24', 'Wenn nichts kommt', 'When nothing arrives'),
 ('K25',
  '<b>Reiter Test → Selbstprüfung:</b> die Zeilen dort beantworten der Reihe '
  'nach, woran es hängt — von apcaccess über den eigenen Dienst bis zum Abo im '
  'Gateway.',
  '<b>Test tab → self-check:</b> the lines there answer in order what the '
  'problem is — from apcaccess through the plugin service to the subscription '
  'in the gateway.'),
 ('K26',
  '<b>Reiter Test → Jetzt abfragen:</b> zeigt die Fehlermeldung von '
  '<code>apcaccess</code> im Klartext.',
  '<b>Test tab → Query now:</b> shows the error message from '
  '<code>apcaccess</code> in plain text.'),
 ('K27', '<b>Reiter Logdateien:</b> dort steht die Ursache.',
         '<b>Log files tab:</b> the cause is there.'),
 ('K28', 'Herkunft', 'Origin'),
 ('K29',
  'Grundlage ist das Plugin von Christian Woerstenfeld, Apache-Lizenz 2.0. Die '
  'von der Lizenz verlangte Nennung steht in <code>NOTICE</code>, in '
  '<code>README.md</code> und im Kopf der Python-Dateien. In '
  '<code>plugin.cfg</code> stehen dagegen Name und E-Mail dieser '
  'Fortführung — LoxBerry benutzt beide als <b>Kennung</b> des Plugins, nicht '
  'als Urhebervermerk; die Kennung eines fremden Plugins zu tragen und '
  'gleichzeitig auf ein anderes Repository zu zeigen, ergäbe eine Mischform, '
  'die LoxBerry nicht auflösen kann.',
  'This is based on the plugin by Christian Woerstenfeld, Apache License 2.0. '
  'The attribution required by the license is in <code>NOTICE</code>, in '
  '<code>README.md</code> and in the header of the Python files. '
  '<code>plugin.cfg</code>, in contrast, carries the name and email of this '
  'continuation — LoxBerry uses both as the <b>identifier</b> of the plugin, '
  'not as an attribution; carrying the identifier of a foreign plugin while '
  'pointing at a different repository would produce a hybrid that LoxBerry '
  'cannot resolve.'),
 # --- Tabelle -----------------------------------------------------------
 ('K30', 'Thema', 'Topic'),
 ('K31', 'Bedeutung', 'Meaning'),
 ('K32', '<code>status</code>', '<code>status</code>'),
 ('K33', 'Zustandstext, z.&nbsp;B. ONLINE oder ONBATT',
         'State text, for example ONLINE or ONBATT'),
 ('K34', '<code>alarm_level</code>', '<code>alarm_level</code>'),
 ('K35', '0 Netz, 1 Akku, 2 Vorwarnung, 3 Abschaltung läuft. Ein Strich (-) bei '
         'abgerissener Verbindung oder wenn apcaccess nicht antwortet',
         '0 mains, 1 battery, 2 advance warning, 3 shutdown running. A dash (-) '
         'when the connection is lost or apcaccess does not answer'),
 ('K36', '<code>on_battery</code>', '<code>on_battery</code>'),
 ('K37', '1 = Netzausfall, die USV speist aus dem Akku',
         '1 = power failure, the UPS is running on battery'),
 ('K38', '<code>data_valid</code>', '<code>data_valid</code>'),
 ('K39', '0 = apcupsd erreicht die USV nicht; die übrigen Zahlen sind dann '
         'wertlos',
         '0 = apcupsd cannot reach the UPS; the other numbers are worthless then'),
 ('K40', '<code>battery_charge</code>', '<code>battery_charge</code>'),
 ('K41', 'Akkuladung in Prozent', 'Battery charge in percent'),
 ('K42', '<code>time_left</code>', '<code>time_left</code>'),
 ('K43', 'verbleibende Laufzeit in Minuten', 'Remaining runtime in minutes'),
 ('K44', '<code>load_watt</code>', '<code>load_watt</code>'),
 ('K45', 'geschätzte Last in Watt', 'Estimated load in watts'),
 ('K46', '<code>replace_battery</code>', '<code>replace_battery</code>'),
 ('K47', '1 = die USV hält einen Akkutausch für fällig',
         '1 = the UPS considers a battery replacement due'),
 ('K48', '<code>battery_age_months</code>', '<code>battery_age_months</code>'),
 ('K49', 'Alter des Akkus in Monaten. Leer, wenn das Datumsformat der USV '
         'zweideutig ist',
         'Age of the battery in months. Empty if the date format of the UPS is '
         'ambiguous'),
 ('K50', '<code>timestamp</code>', '<code>timestamp</code>'),
 ('K51', 'Sekunden seit 1970 zum Zeitpunkt der Messung — daran erkennt Loxone '
         'einen alten Wert',
         'Seconds since 1970 at the time of measurement — this is how Loxone '
         'recognises a stale value'),
 ('K52', '<code>event</code>', '<code>event</code>'),
 ('K53', 'Kurztext beim Zustandswechsel', 'Short text on a state change'),
]

# Gruppe 16 (1.2.23): K35/K49/K51/K53 neu gefasst (-1 statt leer/Strich, timestamp Bestand, event = letztes
# Ereignis), K54-K61 neu (Sprachausgabe, Haus-Thema, Lebenszeichen/Fehlwerte, Zeile status/zaehler).
_G16_H = [
 ('K35', '0 Netz, 1 Akku, 2 Vorwarnung, 3 Abschaltung läuft; -1 = keine Aussage (apcupsd erreicht die USV nicht, antwortet nicht oder das Plugin ist ausgeschaltet)', '0 mains, 1 battery, 2 advance warning, 3 shutdown running; -1 = no statement (apcupsd cannot reach the UPS, does not answer or the plugin is switched off)'),
 ('K49', 'Alter des Akkus in Monaten. -1, wenn das Datumsformat der USV zweideutig ist', 'Age of the battery in months. -1 if the date format of the UPS is ambiguous'),
 ('K51', 'Sekunden seit 1970 zum Zeitpunkt der Messung — Bestand; für neue Projekte <code>status/zaehler</code>', 'Seconds since 1970 at the time of measurement — legacy; for new projects <code>status/zaehler</code>'),
 ('K53', 'das letzte Ereignis (Stromausfall, Netz wieder da …) – bleibt stehen, bis ein neues kommt', 'the last event (power failure, power back …) – stays until a new one comes'),
 ('K54', 'Sprachausgabe bei Stromausfall', 'Voice announcement on power failure'),
 ('K55', 'Im Reiter <i>Einstellungen</i> lässt sich eine Ansage einschalten (gemeinsames Sprachmodul: Alexa NG, Chromecast, Music Server, Sonos4Lox, SonoX, eigene Adresse; ab Werk aus): bei Stromausfall, Rückkehr des Stroms, Vorwarnung und beginnender Abschaltung, die letzten beiden dringend. <b>Bei einem Stromausfall hängen Lautsprecher, Echo, Router und WLAN oft nicht an der USV</b> – dann kommt die Ansage nicht an. Die Benachrichtigungen bleiben der verlässliche Weg.', 'In the <i>Settings</i> tab an announcement can be switched on (shared voice module: Alexa NG, Chromecast, Music Server, Sonos4Lox, SonoX, own address; off by default): on power failure, return of power, advance warning and beginning shutdown, the last two urgent. <b>During a power failure, speakers, Echo, router and Wi-Fi are often not connected to the UPS</b> – then the announcement does not arrive. The notifications remain the reliable way.'),
 ('K56', 'Stufe für andere Plugins', 'Level for other plugins'),
 ('K57', 'Mit <i>Stufe an andere Plugins geben</i> (ab Werk aus) sendet das Plugin <code>haus/usv/stufe</code> (0–3, -1 ohne Aussage, zurückbehalten) und das Lebenszeichen <code>haus/usv/zaehler</code>. Nur eine USV im Haus darf das liefern; beim Ausschalten und bei der Deinstallation räumt das Plugin das Thema ab.', 'With <i>Pass the level on to other plugins</i> (off by default) the plugin sends <code>haus/usv/stufe</code> (0–3, -1 no statement, retained) and the heartbeat <code>haus/usv/zaehler</code>. Only one UPS in the house may provide it; when switched off and on uninstalling, the plugin removes the topic.'),
 ('K58', 'Lebenszeichen und fehlende Werte', 'Heartbeat and missing values'),
 ('K59', 'Fehlt ein Wert – apcaccess antwortet nicht, die Verbindung zur USV ist abgerissen (COMMLOST) oder das Plugin ist ausgeschaltet –, sendet das Plugin -1 (Temperatur -999, Texte „-“), nie nichts. <code>status/zaehler</code> zählt bei jedem Lauf eins weiter; in Loxone überwacht eine Analogwertvalidierung, ob er stehen bleibt. Die Eingänge legen Sie nach der Namenstabelle im Reiter <i>Einbindung in Loxone</i> an. Unter MQTT-Gateway V2 prüft der Reiter <i>Test</i> seit 1.2.24, ob alle Datenpunkte der Hakenliste angehakt sind und „Noncached“ stimmt.', 'If a value is missing – apcaccess does not answer, the connection to the UPS is lost (COMMLOST) or the plugin is switched off –, the plugin sends -1 (temperature -999, texts “-”), never nothing. <code>status/zaehler</code> counts up by one on every run; in Loxone an analog value validation watches whether it stops. Create the inputs according to the name table in the <i>Loxone integration</i> tab. Under MQTT gateway V2 the <i>Test</i> tab checks since 1.2.24 that all data points of the tick list are ticked and “Noncached” is right.'),
 ('K60', '<code>status/zaehler</code>', '<code>status/zaehler</code>'),
 ('K61', 'Lebenszeichen, 0 bis 999, je Lauf eins weiter', 'Heartbeat, 0 to 999, one up per run'),
 ('K62', '<b>Mehrere Lautsprecher gleichzeitig</b> (seit 1.2.24, Sprachmodul 1.2.1): Unter der Ausgabeart (jetzt „Ziel 1“) steht die Tabelle <i>Weitere Ausgabeziele (gleichzeitig)</i> – bis zu 6 Ziele insgesamt, zum Beispiel Loxone Music Server, Google-Lautsprecher (Chromecast 4 Lox NG) und Amazon Echo (Alexa-NG). Jede Ansage geht gleichzeitig an Ziel 1 und an jedes eingeschaltete Ziel der Tabelle; scheitert eines, sprechen die anderen trotzdem, und die Ansage gilt als gesendet, sobald eines gesprochen hat (Protokoll und Reiter Test nennen jedes Ziel). Ist Ziel 1 aus, spricht keines; mit dem Original-Audioserver als Ziel 1 gehen keine weiteren Ziele. Neues Ziel: die leere Zeile ausfüllen und speichern. Mehrere Zonen desselben Music Servers bzw. mehrere Echos gehören in EIN Ziel (Zonenliste, Kommaliste, gruppe:&lt;Name&gt;). Das Sprechtoken steht einmal oben und gilt für alle Ziele dieser Art. Im Reiter Test spricht <i>Testansage</i> an alle Ziele, <i>Testansage an Ziel n</i> nur an dieses. Vor einem Zurückgehen auf eine Fassung vor 1.2.24 die weiteren Ziele entfernen – ältere Fassungen kennen die Liste nicht und fielen beim Laden auf die Werkseinstellung der Sprachausgabe zurück.', '<b>Several speakers at once</b> (since 1.2.24, speech module 1.2.1): below the output type (now “target 1”) the table <i>Further outputs (simultaneous)</i> takes up to 6 targets in total, for example Loxone Music Server, Google speakers (Chromecast 4 Lox NG) and Amazon Echo (Alexa-NG). Every announcement goes to target 1 and to every enabled target of the table at the same time; if one fails the others still speak, and the announcement counts as sent as soon as one has spoken (the log and the Test tab name every target). If target 1 is off, none speaks; the original Audio Server as target 1 cannot be combined with further targets. New target: fill in the empty row and save. Several zones of the same Music Server or several Echos belong in ONE target (zone list, comma list, gruppe:&lt;name&gt;). The speech token is entered once above and applies to all targets of that kind. In the Test tab <i>Test announcement</i> speaks to all targets, <i>Test announcement to target n</i> only to that one. Before going back to a version older than 1.2.24 remove the further targets – older versions do not know the list and would fall back to the factory settings of the speech output.'),
]
_G16_HD = {k: (de, en) for k, de, en in _G16_H}
H = [(k,) + _G16_HD.pop(k) if k in _G16_HD else (k, de, en) for k, de, en in H]
H += [z for z in _G16_H if z[0] in _G16_HD]

KOPF_DE = [
 '; Hilfetexte, deutsch. Gehoert zu templates/help/help.html.',
 ';',
 '; ERZEUGT von Werkzeuge/ap_hilfe_erzeugen.py - nicht von Hand aendern.',
 '; Beide Sprachen kommen aus EINER Quelle; ein Schluessel kann deshalb',
 '; nicht nur in einer stehen.',
 ';',
 '; LBWeb::gethelp() leitet den Namen dieser Datei aus dem Namen der',
 '; Hilfedatei ab und sucht sie in templates/lang/ - nicht neben der Hilfe.',
 '; Jeder Wert steht in doppelten Anfuehrungszeichen und enthaelt selbst',
 '; keine; Auszeichnung bleibt roh, die Hilfe wird nicht maskiert ausgegeben.',
 '',
]


def bau(idx):
    zeilen = list(KOPF_DE)
    zeilen.append('[HILFE]')
    for k, de, en in H:
        zeilen.append('%s = "%s"' % (k, (de, en)[idx]))
    return '\n'.join(zeilen) + '\n'


# Erst pruefen, dann schreiben (06.11.2026): bis dahin standen die Dateien schon
# auf der Platte, wenn die Pruefung danach Verstoesse meldete (Rueckgabe 1).
fehl = 0
texte = {}
for i, sp in enumerate(('de', 'en')):
    text = bau(i)
    texte[sp] = text
    n = len([z for z in text.split('\n') if ' = "' in z])
    print('help_%s.ini  %d Wertzeilen' % (sp, n))
    for j, z in enumerate(text.split('\n'), 1):
        if ' = "' not in z:
            continue
        if z.count('"') != 2:
            print('  FEHL Zeile %d: %d Anfuehrungszeichen' % (j, z.count('"')))
            fehl += 1
        if not re.match(r'^K[0-9]+ = ".*"$', z):
            print('  FEHL Zeile %d passt nicht auf K.. = "..."' % j)
            fehl += 1

# Jeder Platzhalter der Hilfeseite braucht in BEIDEN Sprachen einen Wert.
hp = os.path.join(sys.argv[1], 'templates', 'help', 'help.html')
if os.path.isfile(hp):
    ph = set(re.findall(r'HILFE\.(K[0-9]+)', io.open(hp, encoding='utf-8').read()))
    hab = set(k for k, _, _ in H)
    fehlend = sorted(ph - hab)
    ueber = sorted(hab - ph)
    print('Platzhalter in help.html: %d, Schluessel: %d' % (len(ph), len(hab)))
    if fehlend:
        print('  FEHL: ohne Wert: %s' % fehlend); fehl += 1
    if ueber:
        print('  FEHL: nie benutzt: %s' % ueber); fehl += 1
else:
    print('  FEHL: help.html nicht gefunden'); fehl += 1

print('Verstoesse: %d' % fehl)
if fehl:
    print('Es wurde NICHTS geschrieben.')
    sys.exit(1)
for sp in ('de', 'en'):
    pfad = os.path.join(ZIEL, 'help_%s.ini' % sp)
    with io.open(pfad, 'wb') as fh:
        fh.write(texte[sp].encode('utf-8'))
    print('Geschrieben: %s' % pfad)
sys.exit(0)
