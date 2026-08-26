#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Die neuen Sprachschluessel der Fassung 3.0.8 aus EINER Quelle.

Beide Dateien entstehen aus derselben Tabelle - so koennen sie nicht
auseinanderlaufen. Der Erzeuger WEIST AB statt zurechtzubiegen:

  * ein gerades Anfuehrungszeichen im Wert  -> Abbruch
    (parse_ini_file schneidet dort ab oder bringt die ganze Datei zu Fall)
  * ein mehrzeiliger Wert                   -> Abbruch
  * ein Schluessel, den es schon gibt       -> Abbruch
  * eine HTML-Entitaet in einem Abschnitt, der maskiert ausgegeben wird
    (PZ, PRUEF, ALTER, ZAEHLER) -> Abbruch. Das ist der Befund mit 40
    Fundstellen in 13 Plugins, und er entsteht genau hier.

Aufruf:  python wi_sprache_erzeugen.py <plugin-ordner>
Ohne Argument wird nur geprueft, nichts geschrieben.
"""
import os
import re
import sys

# Abschnitte, deren Werte MASKIERT ausgegeben werden - dort ist Auszeichnung
# verboten, weil sie sonst woertlich am Bildschirm stuende.
ROH_VERBOTEN = ('PZ', 'PRUEF', 'ALTER', 'ZAEHLER', 'ARTEN', 'BAUSTEIN')

# schluessel: (deutsch, englisch)
TEXTE = {

# ---------------------------------------------------------------- REITER
'REITER.MQTT': ('MQTT', 'MQTT'),

# ---------------------------------------------------------------- KOPF
'KOPF.WERTE': ('%s Werte im Abbild, %s',
               '%s values in the snapshot, %s'),

# ---------------------------------------------------------------- ALTER
'ALTER.UNBEKANNT': ('Alter unbekannt', 'age unknown'),
'ALTER.SEK': ('vor %d s', '%d s ago'),
'ALTER.MIN': ('vor %d min', '%d min ago'),
'ALTER.STD': ('vor %d h', '%d h ago'),

# ---------------------------------------------------------------- MELDUNG
'MELDUNG.UEBERNOMMEN': ('Der Dienst hat die Änderung ohne Neustart übernommen — die Verbindung zum ISM8 blieb bestehen.',
                        'The service applied the change without a restart — the connection to the ISM8 stayed up.'),
'MELDUNG.ZAHL_UNGUELTIG': ('%s: „%s“ liegt nicht zwischen %d und %d. Es bleibt bei %s.',
                           '%s: “%s” is not between %d and %d. Keeping %s.'),
'MELDUNG.OUT_UNGUELTIG': ('Ausgabeformat „%s“ ist nicht bekannt. Es bleibt bei %s.',
                          'Output format “%s” is not known. Keeping %s.'),
'MELDUNG.PRAEFIX_UNGUELTIG': ('Das Themen-Präfix „%s“ ist unzulässig — erlaubt sind Kleinbuchstaben, Ziffern, Unterstrich und Bindestrich, höchstens 32 Zeichen. Es bleibt bei %s.',
                              'The topic prefix “%s” is not allowed — permitted are lowercase letters, digits, underscore and hyphen, at most 32 characters. Keeping %s.'),
'MELDUNG.SICH_KEINE_DATEI': ('Es wurde keine Datei ausgewählt.', 'No file was selected.'),
'MELDUNG.SICH_ZU_GROSS': ('Die Datei ist größer als 64 kB — das ist keine Sicherung dieses Plugins.',
                          'The file is larger than 64 kB — that is not a backup of this plugin.'),
'MELDUNG.SICH_ABGELEHNT': ('Die Sicherung wurde <b>nicht</b> übernommen. Die bestehenden Einstellungen sind unverändert.',
                           'The backup was <b>not</b> applied. The existing settings are unchanged.'),
'MELDUNG.SICH_UEBERNOMMEN': ('Die Sicherung wurde übernommen.', 'The backup was applied.'),
'MELDUNG.SICH_ZEILE': ('Zeile mit anderer Feldzahl übersprungen: %s', 'Line with a different number of fields skipped: %s'),
'MELDUNG.SICH_SCHLUESSEL': ('Unbekannter Schlüssel: %s', 'Unknown key: %s'),
'MELDUNG.SICH_LEER': ('Die Datei enthält keine einzige gültige Zeile.', 'The file does not contain a single valid line.'),

# ---------------------------------------------------------------- EINSTELLUNGEN
'EINST.H_UEBERWACHUNG': ('Überwachung', 'Monitoring'),
'EINST.H_SICHERUNG': ('Einstellungen sichern und zurückspielen', 'Back up and restore settings'),
'EINST.WEG_HINT': ('MQTT ist der empfohlene Weg und wohnt im eigenen Reiter. Hier steht nur die <b>zusätzliche</b> Direktausgabe über TCP/UDP — der alte Weg, den man braucht, wenn eine bestehende Loxone-Konfiguration daran hängt.',
                   'MQTT is the recommended path and lives in its own tab. What follows is only the <b>additional</b> direct output over TCP/UDP — the old path, needed when an existing Loxone configuration depends on it.'),
'EINST.OUTPUT': ('Direktausgabe über TCP/UDP', 'Direct output over TCP/UDP'),
'EINST.OUT_NONE': ('aus', 'off'),
'EINST.OUT_DATA': ('data — Kennung und Wert, für Loxone', 'data — id and value, for Loxone'),
'EINST.OUT_CSV': ('csv — mit Semikolon getrennt', 'csv — semicolon separated'),
'EINST.OUT_FHEM': ('fhem — Sonderformat des Ursprungsmoduls', 'fhem — special format of the original module'),
'EINST.OUTPUT_HINT': ('Für Loxone ist <span class=sm-mono>data</span> das richtige. Die Formate <span class=sm-mono>csv</span> und <span class=sm-mono>fhem</span> gibt es nur noch, weil bestehende Anlagen sie benutzen — bis 3.0.7 konnte die Oberfläche sie nicht anzeigen und hat sie beim ersten Speichern stillschweigend verworfen.',
                      'For Loxone, <span class=sm-mono>data</span> is the right choice. The formats <span class=sm-mono>csv</span> and <span class=sm-mono>fhem</span> only exist because existing installations use them — up to 3.0.7 the interface could not display them and silently discarded them on the first save.'),
'EINST.GRUPPE': ('Multicast-Gruppe 239.7.7.77 (alle Miniserver)', 'Multicast group 239.7.7.77 (all Miniservers)'),
'EINST.HERZSCHLAG': ('Lebenszeichen alle … Sekunden', 'Heartbeat every … seconds'),
'EINST.HERZSCHLAG_HINT': ('Das ISM8 sendet nur bei Wertänderung. Ohne ein Lebenszeichen ist ein toter Dienst von einer ruhigen Heizung nicht zu unterscheiden. 0 schaltet es ab.',
                          'The ISM8 only sends on value changes. Without a heartbeat, a dead service cannot be told apart from a quiet heating system. 0 switches it off.'),
'EINST.ABGLEICH': ('Vollabzug alle … Sekunden', 'Full refresh every … seconds'),
'EINST.ABGLEICH_HINT': ('Fordert alle Werte neu an. <b>Ab Werk aus</b>, und das mit Grund: ob das ISM8 den Vollabzug überhaupt annimmt, ist nicht gemessen. Wer es an seiner Anlage geprüft hat, schaltet es ein.',
                        'Requests all values again. <b>Off by default</b>, for a reason: whether the ISM8 accepts the full refresh at all has not been measured. Switch it on once you have verified it on your own installation.'),
'EINST.SICHERUNG_HINT': ('Die Sicherung ist eine einfache Textdatei im Format der Konfiguration. Beim Zurückspielen wird jede Zeile geprüft; eine halb gültige Datei überschreibt <b>nichts</b>.',
                         'The backup is a plain text file in the format of the configuration. On restore every line is checked; a partially valid file overwrites <b>nothing</b>.'),
'EINST.SICHERN': ('Einstellungen herunterladen', 'Download settings'),
'EINST.LADEN_DATEI': ('Sicherung auswählen', 'Select backup'),
'EINST.LADEN_HINT': ('Höchstens 64 kB. Unbekannte Schlüssel und Zeilen mit falscher Feldzahl werden beanstandet.',
                     'At most 64 kB. Unknown keys and lines with the wrong number of fields are reported.'),
'EINST.LADEN': ('Einstellungen zurückspielen', 'Restore settings'),

# ---------------------------------------------------------------- MQTT
'MQTT.H_EINSTELLUNG': ('MQTT-Einstellungen', 'MQTT settings'),
'MQTT.EIN': ('Werte über MQTT senden', 'Send values over MQTT'),
'MQTT.EIN_HINT': ('Der empfohlene Weg. Die Themen sind benannt, die Werte kommen retained an, und im MQTT Finder des Gateways ist sichtbar, was tatsächlich ankommt.',
                  'The recommended path. Topics are named, values arrive retained, and the gateway’s MQTT finder shows what actually arrives.'),
'MQTT.PRAEFIX': ('Themen-Präfix', 'Topic prefix'),
'MQTT.PRAEFIX_HINT': ('<b>Achtung:</b> Ein geändertes Präfix benennt <b>sämtliche</b> Themen um. Jeder virtuelle Eingang im Miniserver, der darauf hört, muss nachgezogen werden, und die alten Werte bleiben retained im Broker stehen — dafür gibt es unten das Aufräumen. Ändern Sie das nur, wenn Sie zwei ISM8 am selben Broker betreiben.',
                      '<b>Careful:</b> Changing the prefix renames <b>all</b> topics. Every virtual input in the Miniserver listening to them must be updated, and the old values stay retained in the broker — that is what the cleanup below is for. Only change this if you run two ISM8 modules on the same broker.'),
'MQTT.PRAEFIX_GEWECHSELT': ('Das Präfix wurde von %s auf %s geändert — die alten Themen stehen noch im Broker.',
                            'The prefix was changed from %s to %s — the old topics are still in the broker.'),
'MQTT.SPEICHERN': ('MQTT-Einstellungen speichern', 'Save MQTT settings'),
'MQTT.H_GATEWAY': ('Zustand des MQTT-Gateways', 'State of the MQTT gateway'),
'MQTT.GW_UNBEKANNT': ('Das MQTT-Gateway ist nicht auffindbar — <span class=sm-mono>config/system/general.json</span> ließ sich nicht lesen. Der Gateway ist seit LoxBerry 3 Bestandteil des Systems und muss nicht nachinstalliert werden.',
                      'The MQTT gateway could not be found — <span class=sm-mono>config/system/general.json</span> was not readable. The gateway has been part of the system since LoxBerry 3 and does not need to be installed separately.'),
'MQTT.GW_AUTOSTART': ('Autostart: <b>%s</b>', 'Autostart: <b>%s</b>'),
'MQTT.GW_FASSUNG': ('Fassung des Gateways: <b>%s</b>', 'Gateway version: <b>%s</b>'),
'MQTT.JA': ('ja', 'yes'),
'MQTT.NEIN': ('nein', 'no'),
'MQTT.UNBEKANNT': ('nicht lesbar', 'not readable'),
'MQTT.H_ABO': ('Was im Gateway einzutragen ist', 'What to enter in the gateway'),
'MQTT.ABO_V1_H': ('Gateway Fassung 1', 'Gateway version 1'),
'MQTT.ABO_V1': ('Unter <i>System &rarr; MQTT Gateway &rarr; Subscriptions</i> das Abonnement %s eintragen. <b>Ohne diesen Eintrag kommt am Miniserver nichts an.</b>',
                'Under <i>System &rarr; MQTT Gateway &rarr; Subscriptions</i> enter the subscription %s. <b>Without this entry nothing arrives at the Miniserver.</b>'),
'MQTT.ABO_V2_H': ('Gateway Fassung 2', 'Gateway version 2'),
'MQTT.ABO_V2': ('Hier ist <b>nichts einzutragen</b>. Die Themengruppe erscheint von selbst in den Abonnements; dort werden die gewünschten Datenpunkte angehakt.',
                'Here there is <b>nothing to enter</b>. The topic group appears in the subscriptions by itself; tick the data points you want there.'),
'MQTT.ABO_UNKLAR': ('Die Fassung des Gateways ließ sich nicht lesen, deshalb stehen <b>beide</b> Sätze da. Einen von beiden zu behaupten wäre für die Hälfte der Anlagen falsch.',
                    'The gateway version could not be read, so <b>both</b> notes are shown. Claiming just one of them would be wrong for half of all installations.'),
'MQTT.H_THEMEN': ('Alle veröffentlichten Themen', 'All published topics'),
'MQTT.THEMEN_HINT': ('Die Themen folgen dem Muster %s.', 'Topics follow the pattern %s.'),
'MQTT.TH_BEDEUTUNG': ('Bedeutung', 'Meaning'),
'MQTT.B_ONLINE': ('1 = das ISM8 ist verbunden, 0 = nicht. Geht retained hinaus und trägt den letzten Willen — bricht die Verbindung zum Broker ab, setzt der Broker es selbst auf 0.',
                  '1 = the ISM8 is connected, 0 = it is not. Sent retained and carrying the last will — if the broker connection drops, the broker itself sets it to 0.'),
'MQTT.B_ZEIT': ('Unix-Zeit des letzten Lebenszeichens. Geht bei jedem Takt hinaus, auch wenn sich kein Wert geändert hat.',
                'Unix time of the last heartbeat. Sent on every tick, even when no value has changed.'),
'MQTT.B_ZAEHLER': ('0…999, umlaufend, eine Stelle je Takt. Darauf legt man in Loxone eine Änderungsüberwachung — bleibt der Zähler stehen, schweigt das Plugin.',
                   '0…999, wrapping, one step per tick. Put a change monitor on this in Loxone — if the counter stops, the plugin has gone silent.'),
'MQTT.THEMEN_ZAHL': ('%s Themen. %s Datenpunkte sind nicht dabei: Uhrzeit und Datum taugen nicht als Analogwert und werden nicht veröffentlicht.',
                     '%s topics. %s data points are not included: time and date are of no use as analogue values and are not published.'),
'MQTT.H_AUFRAEUMEN': ('Retained gebliebene Themen aufräumen', 'Clean up leftover retained topics'),
'MQTT.AUFRAEUMEN_HINT': ('Nach einem Firmwarewechsel, nach einer Präfix-Änderung und vor dem Deinstallieren bleiben Werte im Broker stehen. Der Trockenlauf zeigt, was hinausginge, und schickt nichts.',
                         'After a firmware change, after a prefix change and before uninstalling, values stay behind in the broker. The dry run shows what would be sent and sends nothing.'),
'MQTT.AUFRAEUMEN_PROBE': ('Trockenlauf: was würde aufgeräumt?', 'Dry run: what would be cleaned up?'),
'MQTT.AUFRAEUMEN': ('Retained-Themen wirklich löschen', 'Really delete retained topics'),

# ---------------------------------------------------------------- LOXONE
'LOXONE.S5': ('<b>5. Befehle senden</b> (nur wenn Loxone schalten soll). Virtueller Ausgang auf %s, Befehlstext <span class=sm-mono>&lt;Kennung&gt;;&lt;v.0&gt;</span> — die Kennung dreistellig, etwa <span class=sm-mono>199;&lt;v.0&gt;</span>. Seit 3.0.8 antwortet der Server mit <span class=sm-mono>OK</span> oder <span class=sm-mono>ERR</span>.',
              '<b>5. Sending commands</b> (only if Loxone should switch). Virtual output on %s, command text <span class=sm-mono>&lt;id&gt;;&lt;v.0&gt;</span> — the id three digits, e.g. <span class=sm-mono>199;&lt;v.0&gt;</span>. Since 3.0.8 the server answers with <span class=sm-mono>OK</span> or <span class=sm-mono>ERR</span>.'),
'LOXONE.S6': ('<b>6. Ausfallerkennung.</b> Virtuelle Eingänge behalten ihren letzten Wert — schweigt die Heizung, sieht in der App alles normal aus. Legen Sie deshalb eine Änderungsüberwachung auf %s und werten Sie %s aus.',
              '<b>6. Failure detection.</b> Virtual inputs keep their last value — if the heating goes quiet, everything still looks normal in the app. So put a change monitor on %s and evaluate %s.'),
'LOXONE.S7': ('<b>7. Bausteine nachbauen</b> — die vollständige Liste steht unten.',
              '<b>7. Rebuild the blocks</b> — the complete list is below.'),
'LOXONE.S8': ('<b>8. Gegenprobe.</b> Im MQTT Finder des Gateways auf %s achten, oder in Loxone Config einen virtuellen Eingang ansehen: steht dort ein Wert ungleich 0, ist der Weg vollständig.',
              '<b>8. Cross-check.</b> Watch %s in the gateway’s MQTT finder, or look at a virtual input in Loxone Config: if a value other than 0 is shown, the path is complete.'),
'LOXONE.DOPPELT': ('<b>Loxone Config legt beim Import neu an und überschreibt nichts.</b> Zweimal importiert heißt doppelte Objekte — bei dieser Datenpunktzahl schnell mehrere hundert.',
                   '<b>Loxone Config creates new objects on import and overwrites nothing.</b> Importing twice means duplicate objects — with this number of data points, quickly several hundred.'),
'LOXONE.GESEHEN_N': ('%d gesehen', '%d seen'),
'LOXONE.NURGESEHEN': ('Nur Datenpunkte aufnehmen, für die schon ein Telegramm kam',
                      'Only include data points that have already sent a telegram'),
'LOXONE.NURGESEHEN_HINT': ('Aus dem Zustandsabbild des Dienstes: derzeit %d Datenpunkte. So wird aus der vollständigen Tabelle die tatsächliche Anlage — ein virtueller Eingang, der nie einen Wert bekommt, sieht in Loxone genauso aus wie einer mit 0.',
                           'From the service snapshot: currently %d data points. This turns the full table into your actual installation — a virtual input that never receives a value looks exactly like one showing 0 in Loxone.'),
'LOXONE.NURGESEHEN_LEER': ('Noch kein einziges Telegramm empfangen — deshalb ist diese Auswahl abgeschaltet. Sie wird brauchbar, sobald das ISM8 gesendet hat.',
                           'Not a single telegram received yet — that is why this option is disabled. It becomes usable once the ISM8 has sent something.'),
'LOXONE.FILTER_GERAET': ('Gerät', 'Device'),
'LOXONE.FILTER_SUCHE': ('Suche in Name und Thema', 'Search in name and topic'),
'LOXONE.FILTER_RICHTUNG': ('Richtung', 'Direction'),
'LOXONE.FILTER_ALLE': ('alle', 'all'),
'LOXONE.DP_ZAHL': ('%s von %s Datenpunkten', '%s of %s data points'),

# ---------------------------------------------------------------- BAUSTEINE
'BAUSTEIN.H': ('Bausteine in Loxone Config — zum Nachbauen', 'Blocks in Loxone Config — to rebuild'),
'BAUSTEIN.EINLEITUNG': ('Wer diese Tabelle von oben nach unten abarbeitet, hat die Funktion nachgebaut, ohne nachzudenken. Die Bausteine findet man in Loxone Config über die Bausteinsuche (F5).',
                        'Anyone working through this table from top to bottom has rebuilt the function without having to think. The blocks are found in Loxone Config via the block search (F5).'),
'BAUSTEIN.TH_TYP': ('Baustein (Typ)', 'Block (type)'),
'BAUSTEIN.TH_NAME': ('Name (Vorschlag)', 'Name (suggestion)'),
'BAUSTEIN.TH_PARAM': ('Parameter', 'Parameters'),
'BAUSTEIN.TH_EINGANG': ('Eingänge verbinden mit', 'Connect inputs to'),

'BAUSTEIN.B1_TYP': ('Statusbaustein', 'Status block'),
'BAUSTEIN.B1_NAME': ('Wolf Betriebsart', 'Wolf operating mode'),
'BAUSTEIN.B1_PARAM': ('Statustexte aus der Tabelle unten kopieren', 'Copy status texts from the table below'),
'BAUSTEIN.B1_EIN': ('virtueller Eingang der Betriebsart (DPT_HVACContrMode)', 'virtual input of the operating mode (DPT_HVACContrMode)'),

'BAUSTEIN.B2_TYP': ('Änderungsüberwachung (Monoflop, retriggerbar)', 'Change monitor (retriggerable monoflop)'),
'BAUSTEIN.B2_NAME': ('Wolf Lebenszeichen', 'Wolf heartbeat'),
'BAUSTEIN.B2_PARAM': ('Haltezeit deutlich über dem eingestellten Lebenszeichen-Takt, Vorschlag 300 s bei 60 s Takt', 'Hold time clearly above the configured heartbeat interval, suggested 300 s for a 60 s interval'),
'BAUSTEIN.B2_EIN': ('virtueller Eingang des Zählers — jeder Wechsel triggert nach', 'virtual input of the counter — every change retriggers'),

'BAUSTEIN.B3_TYP': ('ODER', 'OR'),
'BAUSTEIN.B3_NAME': ('Wolf Sammelstörung', 'Wolf collective fault'),
'BAUSTEIN.B3_PARAM': ('so viele Eingänge wie Störmeldungen', 'as many inputs as fault messages'),
'BAUSTEIN.B3_EIN': ('alle Störungs-Eingänge und der Ausgang von #2', 'all fault inputs and the output of #2'),

'BAUSTEIN.B4_TYP': ('Benachrichtigungsbaustein', 'Notification block'),
'BAUSTEIN.B4_NAME': ('Wolf Meldung', 'Wolf message'),
'BAUSTEIN.B4_PARAM': ('Empfänger und Text nach Wunsch', 'Recipients and text as desired'),
'BAUSTEIN.B4_EIN': ('ausschließlich der Ausgang von #3', 'exclusively the output of #3'),

'BAUSTEIN.B5_TYP': ('Analogspeicher / Merker', 'Analogue memory / marker'),
'BAUSTEIN.B5_NAME': ('Wolf Kesseltemperatur', 'Wolf boiler temperature'),
'BAUSTEIN.B5_PARAM': ('keine', 'none'),
'BAUSTEIN.B5_EIN': ('virtueller Eingang der Kesseltemperatur', 'virtual input of the boiler temperature'),

'BAUSTEIN.B6_TYP': ('Analog-Sollwertgeber', 'Analogue setpoint'),
'BAUSTEIN.B6_NAME': ('Wolf Kesselsoll', 'Wolf boiler setpoint'),
'BAUSTEIN.B6_PARAM': ('Grenzen aus der Datenpunkttabelle, für Temperaturen −60 bis 250', 'Limits from the data point table, for temperatures −60 to 250'),
'BAUSTEIN.B6_EIN': ('Ausgang auf den virtuellen Ausgang der Sollwertvorgabe', 'output to the virtual output of the setpoint'),

'BAUSTEIN.B7_TYP': ('Auswahlschalter', 'Selector switch'),
'BAUSTEIN.B7_NAME': ('Wolf Warmwasser-Betriebsart', 'Wolf hot water mode'),
'BAUSTEIN.B7_PARAM': ('nur 0, 2 und 4 sind gültig — andere Werte weist der Server ab', 'only 0, 2 and 4 are valid — the server rejects other values'),
'BAUSTEIN.B7_EIN': ('Ausgang auf den virtuellen Ausgang der Warmwasser-Betriebsart', 'output to the virtual output of the hot water mode'),

'BAUSTEIN.B8_TYP': ('Statistik', 'Statistics'),
'BAUSTEIN.B8_NAME': ('Wolf Verbrauch', 'Wolf consumption'),
'BAUSTEIN.B8_PARAM': ('Zählerstand, nicht Momentanwert', 'Meter reading, not instantaneous value'),
'BAUSTEIN.B8_EIN': ('virtueller Eingang der Energiemenge (DPT_ActiveEnergy)', 'virtual input of the energy amount (DPT_ActiveEnergy)'),

'BAUSTEIN.ZU1': ('Zu #2: Das ISM8 sendet nur bei Wertänderung. Eine Überwachung auf einen Messwert schlägt deshalb Fehlalarm, sobald die Heizung ruhig ist — der umlaufende Zähler ändert sich dagegen unabhängig davon.',
                 'On #2: The ISM8 only sends on value changes. A monitor on a measured value therefore raises false alarms as soon as the heating is quiet — the wrapping counter changes regardless.'),
'BAUSTEIN.ZU2': ('Zu #3 und #4: Der Benachrichtigungsbaustein sendet nur beim Wechsel von Aus auf Ein. Niemals mehrere Quellen direkt an seinen Eingang — sonst verschluckt eine dauerhaft aktive Quelle alle übrigen. Erst über ODER zusammenführen.',
                 'On #3 and #4: The notification block only sends on a change from off to on. Never connect several sources directly to its input — a permanently active source would swallow all the others. Combine them with OR first.'),
'BAUSTEIN.ZU3': ('Zu #6 und #7: Ein Schreibbefehl braucht einen virtuellen Ausgang, keinen Eingang. Ob er angekommen ist, sagt seit 3.0.8 die Antwort des Servers — im Reiter Test lässt sich das mit der Schreibprobe trocken durchspielen.',
                 'On #6 and #7: A write command needs a virtual output, not an input. Since 3.0.8 the server’s reply says whether it arrived — the Test tab lets you rehearse this as a dry run.'),
'BAUSTEIN.ZU4': ('Zu #8: Loxone rechnet Zeiten in Sekunden seit dem 01.01.2009. Liefert ein Zeit-Baustein Unix-Zeit (Werte um 1,7 Milliarden), müssen 1230768000 abgezogen werden — das betrifft den Zeitstempel des Lebenszeichens.',
                 'On #8: Loxone counts time in seconds since 2009-01-01. If a time block delivers Unix time (values around 1.7 billion), subtract 1230768000 — this concerns the heartbeat timestamp.'),

# ---------------------------------------------------------------- BETRIEBSARTEN
'ARTEN.H': ('Betriebsarten im Klartext', 'Operating modes in plain text'),
'ARTEN.HINT': ('Über MQTT geht die nackte Zahl hinaus. Diese Tabellen sagen, was sie bedeutet - und die Zeile darunter ist der fertige Statustext für den Loxone-Statusbaustein.',
               'Over MQTT the bare number is sent. These tables say what it means - and the line below is the ready-made status text for the Loxone status block.'),
'ARTEN.TH_WERT': ('Wert', 'Value'),
'ARTEN.TH_TEXT': ('Bedeutung', 'Meaning'),
'ARTEN.STATUSTEXT': ('Statustext zum Kopieren:', 'Status text to copy:'),

# ---------------------------------------------------------------- STOERCODES
'STOER.H': ('Störcodes im Klartext', 'Fault codes in plain text'),
'STOER.LEER': ('<b>Es ist keine Störcode-Tabelle hinterlegt.</b> Der Datenpunkt „Zuletzt aktiver Störcode“ (372, Firmware 1.8 und 1.9) kommt deshalb als nackte Zahl in Loxone an. Die Zuordnung steht in der Wolf-Dokumentation und wurde hier bewusst <b>nicht erfunden</b>.',
               '<b>No fault code table is stored.</b> The data point “last active fault code” (372, firmware 1.8 and 1.9) therefore arrives in Loxone as a bare number. The mapping is in the Wolf documentation and was deliberately <b>not invented</b> here.'),
'STOER.WOHIN': ('Legen Sie eine Datei %s an, je Zeile <span class=sm-mono>Nummer;Klartext</span>. Zeilen mit einem Doppelkreuz am Anfang werden übersprungen. Die Datei liegt unter <span class=sm-mono>config/</span> und überlebt damit ein Update.',
                'Create a file %s, one line per entry as <span class=sm-mono>number;plain text</span>. Lines starting with a hash are skipped. The file lives under <span class=sm-mono>config/</span> and therefore survives an update.'),
'STOER.ANZAHL': ('%d Störcodes hinterlegt.', '%d fault codes stored.'),

# ---------------------------------------------------------------- TEST
'TEST.H_SELBST': ('Selbstprüfung', 'Self-check'),
'TEST.SELBST_BILANZ': ('%d von %d beantwortet, %d mit Kreuz, %d nicht messbar. Ein Strich heißt „hier war nichts zu messen“ und zählt nicht als bestanden.',
                       '%d of %d answered, %d marked with a cross, %d not measurable. A dash means “nothing to measure here” and does not count as passed.'),
'TEST.H_ZAEHLER': ('Zähler des Dienstes', 'Service counters'),
'TEST.H_SCHREIBEN': ('Schreibprobe', 'Write test'),
'TEST.SCHREIBEN_HINT': ('Erst der Trockenlauf: er zeigt das Telegramm, das hinausginge, und sendet <b>nichts</b>. Erst der orange Knopf schaltet wirklich.',
                        'The dry run comes first: it shows the telegram that would be sent and sends <b>nothing</b>. Only the orange button really switches.'),
'TEST.SP_DP': ('Datenpunkt (nur beschreibbare)', 'Data point (writable only)'),
'TEST.SP_WERT': ('Wert', 'Value'),
'TEST.SP_TROCKEN': ('Prüfen (Trockenlauf)', 'Check (dry run)'),
'TEST.SP_ERNST': ('Wirklich senden', 'Really send'),
'TEST.VORLAGENPROBE': ('Loxone-Vorlagen prüfen', 'Check Loxone templates'),

# ---------------------------------------------------------------- LOG
'LOG.H_VERWALTUNG': ('Protokollverwaltung', 'Log management'),
'LOG.VERWALTUNG_HINT': ('Ältere Läufe, Loglevel und Herunterladen — die Verwaltung des LoxBerry.',
                        'Older runs, log level and downloading — the LoxBerry log management.'),
'LOG.GROESSE': ('Größe: %s kB', 'Size: %s kB'),
'LOG.LEEREN': ('Datenpunkt-Protokoll leeren', 'Clear data point log'),

# ---------------------------------------------------------------- PRUEFZEILEN
'PZ.EIN': ('Ist der Server eingeschaltet?', 'Is the server switched on?'),
'PZ.EIN_JA': ('Ja - der Haken im Reiter Einstellungen steht.', 'Yes - the box in the Settings tab is ticked.'),
'PZ.EIN_NEIN': ('Nein. Solange er aus ist, laeuft nichts, und alle weiteren Zeilen sagen nichts über die Einrichtung.',
                'No. While it is off nothing runs, and all further lines say nothing about the setup.'),
'PZ.WATCHDOG': ('Laeuft der Wächter?', 'Is the watchdog running?'),
'PZ.MODUL': ('Laeuft das Auswertungsmodul?', 'Is the evaluation module running?'),
'PZ.PID': ('Ja, PID %d.', 'Yes, PID %d.'),
'PZ.LAEUFT_NICHT': ('Nein.', 'No.'),
'PZ.MODULE': ('Sind alle Perl-Module vorhanden?', 'Are all Perl modules present?'),
'PZ.MODULE_OK': ('Ja, alle %d.', 'Yes, all %d.'),
'PZ.MODULE_FEHLT': ('Nein, es fehlen: %s. Ohne sie startet der Server nicht.', 'No, missing: %s. Without them the server does not start.'),
'PZ.TABELLE': ('Ist die Datenpunkttabelle lesbar?', 'Is the data point table readable?'),
'PZ.TABELLE_OK': ('Ja, %d Datenpunkte für Firmware %s.', 'Yes, %d data points for firmware %s.'),
'PZ.TABELLE_FEHLT': ('Nein - für Firmware %s ist keine Tabelle vorhanden.', 'No - there is no table for firmware %s.'),
'PZ.KONFIG': ('Ist die Konfiguration vollständig?', 'Is the configuration complete?'),
'PZ.KONFIG_OK': ('Ja, alle %d Schlüssel stehen darin.', 'Yes, all %d keys are present.'),
'PZ.KONFIG_LUECKE': ('Nein, es fehlen: %s. Für diese gilt der Vorgabewert - und der ist von einem gewählten nicht zu unterscheiden.',
                     'No, missing: %s. The default applies for those - and a default cannot be told apart from a chosen value.'),
'PZ.KONFIG_FEHLT': ('Die Datei %s gibt es nicht.', 'The file %s does not exist.'),
'PZ.ABBILD': ('Schreibt der Dienst sein Zustandsabbild?', 'Is the service writing its snapshot?'),
'PZ.ABBILD_KEINS': ('Es gibt noch keines. Der Dienst schreibt es, sobald der erste Wert ankommt.',
                    'There is none yet. The service writes it as soon as the first value arrives.'),
'PZ.ABBILD_ALTER': ('Ja, geschrieben %s.', 'Yes, written %s.'),
'PZ.OHNE_ABBILD': ('Ohne Zustandsabbild lässt sich das nicht sagen.', 'Without the snapshot this cannot be answered.'),
'PZ.VERBUNDEN': ('Hat sich das ISM8 schon einmal verbunden?', 'Has the ISM8 ever connected?'),
'PZ.VERBUNDEN_JA': ('Ja, %d Verbindungen seit dem Start, zuletzt von %s.', 'Yes, %d connections since start, most recently from %s.'),
'PZ.VERBUNDEN_NIE': ('Nein, noch kein einziges Mal. Steht im ISM8 die richtige Adresse und der richtige Port?',
                     'No, not once. Are the correct address and port set in the ISM8?'),
'PZ.WERTE': ('Kommen Werte an?', 'Are values arriving?'),
'PZ.WERTE_JA': ('Ja, %d von %d Datenpunkten haben schon gesendet.', 'Yes, %d of %d data points have already sent.'),
'PZ.WERTE_KEINE': ('Nein, noch kein einziger. Das ISM8 sendet nur bei Wertänderung - eine Solltemperatur am Gerät zu verstellen erzwingt ein Telegramm.',
                   'No, not a single one. The ISM8 only sends on value changes - adjusting a setpoint on the device forces a telegram.'),
'PZ.FW': ('Passt die eingestellte Firmware zu dem, was ankommt?', 'Does the configured firmware match what is arriving?'),
'PZ.FW_OK': ('Nichts spricht dagegen: mit Tabelle %s kam keine unbekannte Datenpunktkennung an. Der umgekehrte Fall - Tabelle zu neu - ist von hier aus NICHT erkennbar.',
             'Nothing speaks against it: with table %s no unknown data point id arrived. The reverse case - table too new - is NOT detectable from here.'),
'PZ.FW_VERDACHT': ('Nein. %d Telegramme trugen Kennungen zwischen %d und %d, die in der eingestellten Tabelle nicht stehen. Diese Kennungen kennt Firmware %s - eingestellt ist %s.',
                   'No. %d telegrams carried ids between %d and %d that are not in the configured table. Firmware %s knows these ids - %s is configured.'),
'PZ.FW_UNBEKANNT': ('Nein. %d Telegramme trugen Kennungen zwischen %d und %d, die keine mitgelieferte Tabelle kennt.',
                    'No. %d telegrams carried ids between %d and %d that none of the shipped tables knows.'),
'PZ.HERZ': ('Geht ein Lebenszeichen hinaus?', 'Is a heartbeat being sent?'),
'PZ.HERZ_JA': ('Ja, alle %d Sekunden.', 'Yes, every %d seconds.'),
'PZ.HERZ_AUS': ('Nein, abgeschaltet. Dann ist ein toter Dienst von einer ruhigen Heizung nicht zu unterscheiden.',
                'No, switched off. A dead service then cannot be told apart from a quiet heating system.'),
'PZ.AUSFALL': ('Ist die Ausfallerkennung eingeschaltet?', 'Is failure detection switched on?'),
'PZ.AUSFALL_JA': ('Ja, nach %d Sekunden ohne Daten gilt das ISM8 als offline.', 'Yes, after %d seconds without data the ISM8 counts as offline.'),
'PZ.AUSFALL_AUS': ('Nein - online_timeout steht auf -1. Bleibt das ISM8 stumm, während die Verbindung steht, merkt es niemand.',
                   'No - online_timeout is -1. If the ISM8 goes silent while the connection is up, nobody notices.'),
'PZ.MQTT': ('Ist der MQTT-Weg vollständig?', 'Is the MQTT path complete?'),
'PZ.MQTT_AUS': ('MQTT ist abgeschaltet - dazu ist nichts zu sagen.', 'MQTT is switched off - nothing to say about it.'),
'PZ.MQTT_KEIN_GW': ('Das Gateway ist nicht auffindbar. Ohne es kommt am Miniserver nichts an.',
                    'The gateway cannot be found. Without it nothing arrives at the Miniserver.'),
'PZ.MQTT_OK': ('Ja, Autostart steht, Gateway-Fassung %s.', 'Yes, autostart is on, gateway version %s.'),
'PZ.MQTT_KEIN_AUTOSTART': ('Der Gateway steht nicht auf Autostart. Es wird gesendet, aber vermutlich hört niemand zu.',
                           'The gateway is not set to autostart. Data is sent, but probably nobody is listening.'),
'PZ.CRON': ('Ist der eigene Cron-Eintrag da?', 'Is the plugin’s own cron entry present?'),
'PZ.CRON_JA': ('Ja: %s. Stirbt der Wächter, startet ihn der Cron binnen fünf Minuten nach.',
               'Yes: %s. If the watchdog dies, cron restarts it within five minutes.'),
'PZ.CRON_NEIN': ('Nein - %s fehlt. Stirbt der Wächter, laeuft bis zum nächsten Neustart des Rechners nichts wieder an.',
                 'No - %s is missing. If the watchdog dies, nothing restarts until the machine reboots.'),
'PZ.CRON_UNBEKANNT': ('Der LoxBerry-Ordner ist nicht bekannt - das lässt sich hier nicht messen.',
                      'The LoxBerry directory is unknown - this cannot be measured here.'),
'PZ.VORLAGEN': ('Sind die erzeugten Loxone-Vorlagen wohlgeformt?', 'Are the generated Loxone templates well-formed?'),
'PZ.VORLAGEN_OK': ('Ja, %d von %d durch den XML-Leser gelaufen.', 'Yes, %d of %d passed through the XML parser.'),
'PZ.VORLAGEN_KAPUTT': ('Nein: %s ist nicht wohlgeformt. Loxone Config meldet dazu nichts Brauchbares.',
                       'No: %s is not well-formed. Loxone Config reports nothing useful about it.'),
'PZ.VORLAGEN_KEINE_DP': ('Ohne Datenpunkttabelle lässt sich keine Vorlage erzeugen.',
                         'Without a data point table no template can be generated.'),
'PZ.VORLAGEN_NICHTS': ('Es entstand keine einzige Vorlage - hier wurde nichts gemessen.',
                       'Not a single template was generated - nothing was measured here.'),
'PZ.REITER': ('Passen Reiterleiste, Bereiche und Positivliste zusammen?', 'Do the tab bar, panes and allow-list match?'),
'PZ.REITER_ZAHL': ('Leiste %d, Bereiche %d, Liste %d.', 'Bar %d, panes %d, list %d.'),
'PZ.REITER_UNLESBAR': ('Die eigene index.php ließ sich nicht lesen - hier wurde nichts gemessen.',
                       'The plugin’s own index.php could not be read - nothing was measured here.'),
'PZ.ARTEN': ('Stimmen die Betriebsart-Tabellen mit dem Dienst überein?', 'Do the operating mode tables match the service?'),
'PZ.ARTEN_OK': ('Ja, alle %d Klartexte stehen auch im Auswertungsmodul.', 'Yes, all %d plain texts are also in the evaluation module.'),
'PZ.ARTEN_ABWEICHUNG': ('Nein, %d Klartexte fehlen im Auswertungsmodul, darunter: %s. Die beiden Tabellen sind auseinandergelaufen.',
                        'No, %d plain texts are missing in the evaluation module, among them: %s. The two tables have drifted apart.'),
'PZ.ARTEN_KEIN_PERL': ('Das Auswertungsmodul ist von hier aus nicht lesbar.', 'The evaluation module is not readable from here.'),

# ---------------------------------------------------------------- ZAEHLER
'ZAEHLER.TELEGRAMME': ('Telegramme', 'telegrams'),
'ZAEHLER.DATENPUNKTE': ('Datenpunkte', 'data points'),
'ZAEHLER.GESENDET': ('weitergegeben', 'forwarded'),
'ZAEHLER.VERWORFEN': ('ohne Wert verworfen', 'dropped, no value'),
'ZAEHLER.UNBEKANNT': ('unbekannte Kennung', 'unknown id'),
'ZAEHLER.RAHMENFEHLER': ('Rahmenfehler', 'frame errors'),
'ZAEHLER.UDP_FEHLER': ('UDP-Fehler', 'UDP errors'),
'ZAEHLER.BEFEHLE_OK': ('Befehle angenommen', 'commands accepted'),
'ZAEHLER.BEFEHLE_WEG': ('Befehle abgewiesen', 'commands rejected'),
'ZAEHLER.VERBINDUNGEN': ('Verbindungen', 'connections'),

# ---------------------------------------------------------------- WERTETABELLE
'WERT.H': ('Aktuelle Werte', 'Current values'),
'WERT.HINT': ('Aus dem Zustandsabbild des Dienstes, geschrieben %s. Die Tabelle zeigt, was das ISM8 zuletzt geschickt hat — unabhängig davon, welcher Ausgabeweg eingestellt ist.',
              'From the service snapshot, written %s. The table shows what the ISM8 last sent — regardless of which output path is configured.'),
'WERT.LEER': ('Es liegt noch kein Zustandsabbild vor, oder es ist leer. Der Dienst schreibt es, sobald das erste Telegramm ankommt — das ISM8 sendet nur bei Wertänderung.',
              'There is no snapshot yet, or it is empty. The service writes it as soon as the first telegram arrives — the ISM8 only sends on value changes.'),
'WERT.FILTER': ('Suche in Gerät, Datenpunkt und Wert', 'Search in device, data point and value'),
'WERT.ZAHL': ('%s von %s Werten', '%s of %s values'),
'WERT.TH_WERT': ('Wert', 'Value'),
'WERT.TH_KLARTEXT': ('Klartext', 'Plain text'),
'WERT.TH_ALTER': ('Alter', 'Age'),
'WERT.UNBEKANNT': ('(Zahl steht in keiner Tabelle)', '(number is in no table)'),
'WERT.KEIN_STOERTEXT': ('(keine Störcode-Tabelle hinterlegt)', '(no fault code table stored)'),

# ---------------------------------------------------------------- PRUEF (Testausgaben)
'PRUEF.T_VORLAGEN': ('Loxone-Vorlagen', 'Loxone templates'),
'PRUEF.VP_BEISPIEL': ('Beispiel %s mit %d Datenpunkten, erste Zeilen:', 'Example %s with %d data points, first lines:'),
'PRUEF.VP_WEITERE': ('... und %d weitere Zeilen.', '... and %d more lines.'),
'PRUEF.T_SP_TROCKEN': ('Schreibprobe - Trockenlauf', 'Write test - dry run'),
'PRUEF.T_SP_ERNST': ('Schreibprobe - wirklich gesendet', 'Write test - really sent'),
'PRUEF.SP_ID_UNGUELTIG': ('Die Datenpunktkennung „%s“ ist keine Zahl.', 'The data point id “%s” is not a number.'),
'PRUEF.SP_UNBEKANNT': ('Den Datenpunkt %d gibt es in Firmware %s nicht.', 'Data point %d does not exist in firmware %s.'),
'PRUEF.SP_NICHT_SCHREIBBAR': ('Datenpunkt %d (%s) lässt sich nicht beschreiben - er ist nur lesbar.',
                              'Data point %d (%s) cannot be written - it is read-only.'),
'PRUEF.SP_KEIN_WERT': ('Es wurde kein Wert eingetragen.', 'No value was entered.'),
'PRUEF.SP_TROCKEN': ('TROCKENLAUF - es wurde NICHTS gesendet.\n\nGerät:       %s\nDatenpunkt:  %s\nKNX-Typ:     %s\n\nGesendet WÜRDE die Zeile:\n    %s\nan tcp://%s:%s\n\nDer Server prüfte den Wert danach noch einmal selbst und antwortet mit OK oder ERR.',
                     'DRY RUN - NOTHING was sent.\n\nDevice:     %s\nData point: %s\nKNX type:   %s\n\nThe line that WOULD be sent:\n    %s\nto tcp://%s:%s\n\nThe server would then check the value again itself and answer with OK or ERR.'),
'PRUEF.SP_ERNST': ('Gesendet wurde die Zeile:\n    %s\n\nAntwort des Servers:\n    %s',
                   'The following line was sent:\n    %s\n\nServer reply:\n    %s'),
'PRUEF.SP_KEINE_ANTWORT': ('(keine Antwort - laeuft der Server, und stimmt der Befehls-Port?)',
                           '(no reply - is the server running, and is the command port correct?)'),
'PRUEF.T_AUFRAEUMEN': ('Retained-Themen aufräumen', 'Cleaning up retained topics'),
'PRUEF.AR_KOPF': ('Betroffen sind %d Themen - alle Firmwarefassungen zusammen, weil nach einem Wechsel auch die alten noch im Broker stehen.',
                  '%d topics are affected - across all firmware versions, because after a change the old ones remain in the broker too.'),
'PRUEF.AR_TROCKEN': ('TROCKENLAUF - es wurde NICHTS gesendet. Diese Themen würden geleert:',
                     'DRY RUN - NOTHING was sent. These topics would be cleared:'),
'PRUEF.AR_WEITERE': ('... und %d weitere.', '... and %d more.'),
'PRUEF.AR_KEIN_PORT': ('Der UDP-Eingangsport des MQTT-Gateways ist nicht gesetzt - ohne ihn gibt es keinen Weg zum Broker. Im Gateway unter „UDP In“ einen Port eintragen.',
                       'The MQTT gateway’s UDP input port is not set - without it there is no path to the broker. Set a port under “UDP In” in the gateway.'),
'PRUEF.AR_KEIN_SOCKET': ('Der UDP-Port %d ließ sich nicht öffnen: %s',
                         'UDP port %d could not be opened: %s'),
'PRUEF.AR_ERNST': ('%d Loeschauftraege an den UDP-Eingang des Gateways (Port %d) geschickt.',
                   'Sent %d clear requests to the gateway’s UDP input (port %d).'),
'PRUEF.AR_VORBEHALT': ('VORBEHALT: Ob das Gateway eine LEERE Nutzlast als Löschung weiterreicht, ist an einem Broker zu prüfen und hier NICHT gemessen. Sehen Sie im MQTT Finder nach, ob die Themen verschwunden sind.',
                       'CAVEAT: Whether the gateway forwards an EMPTY payload as a deletion must be checked against a broker and is NOT measured here. Check in the MQTT finder whether the topics have disappeared.'),
'PRUEF.T_DPLOG': ('Datenpunkt-Protokoll', 'Data point log'),
'PRUEF.DL_KEINE': ('Es gibt kein Datenpunkt-Protokoll - die Protokollierung ist ausgeschaltet.',
                   'There is no data point log - logging is switched off.'),
'PRUEF.DL_FEHLER': ('Die Datei %s ließ sich nicht leeren.', 'The file %s could not be cleared.'),
'PRUEF.DL_OK': ('%s geleert - vorher %s kB, jetzt %d Byte.', '%s cleared - %s kB before, %d bytes now.'),
}

# Berechnete Schluessel, die kein Suchmuster findet - sie stehen im PHP als
# wi_t('BAUSTEIN.B' . $i . '_TYP') und dergleichen. Deshalb hier ausdruecklich
# aufgezaehlt, damit der Erzeuger sie mitzaehlt.
BERECHNET = [k for k in TEXTE
             if re.match(r'^(BAUSTEIN\.(B\d|ZU)|ZAEHLER\.|EINST\.OUT_)', k)]


def pruefe_werte():
    fehler = []
    for k, (de, en) in sorted(TEXTE.items()):
        abschnitt = k.split('.')[0]
        for name, w in (('DE', de), ('EN', en)):
            if '"' in w:
                fehler.append('%s (%s): gerades Anfuehrungszeichen im Wert' % (k, name))
            if '\r' in w:
                fehler.append('%s (%s): Wagenruecklauf im Wert' % (k, name))
            if abschnitt in ROH_VERBOTEN and re.search(r'&[a-zA-Z]+;|&#\d+;|<[a-z/]', w):
                fehler.append('%s (%s): Auszeichnung in einem maskierten Abschnitt'
                              % (k, name))
        # Platzhalter muessen in beiden Sprachen gleich oft vorkommen.
        if len(re.findall(r'%[sd]', de)) != len(re.findall(r'%[sd]', en)):
            fehler.append('%s: verschieden viele Platzhalter (DE %d, EN %d)'
                          % (k, len(re.findall(r'%[sd]', de)),
                             len(re.findall(r'%[sd]', en))))
    return fehler


def einbauen(pfad, sprache):
    """Die neuen Schluessel in die vorhandene .ini einsortieren."""
    roh = open(pfad, 'rb').read()
    vor_crlf = roh.count(b'\r\n')
    vor_lf = roh.count(b'\n') - vor_crlf
    if vor_crlf and vor_lf:
        raise SystemExit('ABBRUCH %s: gemischte Zeilenenden' % pfad)
    ze = '\r\n' if vor_crlf else '\n'
    t = roh.decode('utf-8')

    nach_abschnitt = {}
    for k, paar in TEXTE.items():
        a, s = k.split('.', 1)
        nach_abschnitt.setdefault(a, []).append((s, paar[0 if sprache == 'de' else 1]))

    def abschnitt_text(name):
        """Nur den Inhalt EINES Abschnitts.

        Die Dublettenwache suchte im ersten Anlauf den Schluesselnamen in der
        GANZEN Datei. KOPF.WERTE und TEST.WERTE heissen beide WERTE - der Lauf
        brach deshalb ab, obwohl nichts doppelt war. Ein Suchmuster, das zu
        viel trifft, ist auch dann falsch, wenn es abbricht statt zu schreiben.
        """
        m = re.search(r'(?m)^\[%s\]\s*$' % re.escape(name), t)
        if not m:
            return ''
        rest = t[m.end():]
        n = re.search(r'(?m)^\[', rest)
        return rest[:n.start()] if n else rest

    neu = 0
    for a in sorted(nach_abschnitt):
        zeilen = ''.join('%s = "%s"%s' % (s, w.replace('\n', '\\n'), ze)
                         for s, w in sorted(nach_abschnitt[a]))
        vorhanden = abschnitt_text(a)
        for s, w in nach_abschnitt[a]:
            if re.search(r'(?m)^%s\s*=' % re.escape(s), vorhanden):
                # Schon vorhanden - der Erzeuger schreibt NICHTS darueber.
                raise SystemExit('ABBRUCH %s: %s.%s steht schon da' % (pfad, a, s))
        # Der Anker muss am ZEILENANFANG stehen. Der erste Anlauf suchte
        # '[KOPF]' als Teilzeichenfolge - und traf den Kommentar im Dateikopf,
        # in dem woertlich '[KOPF] bis [LOG]' steht. Die Schluessel landeten
        # damit VOR dem ersten Abschnitt, wo parse_ini_file sie nicht findet.
        # Genau diese Fehlerklasse steht in REGELN_1 dreimal: ein Kommentar,
        # der die gesuchte Form selbst enthaelt.
        kopf = re.search(r'(?m)^\[%s\]\s*$' % re.escape(a), t)
        if kopf:
            # Ans Ende des Abschnitts: geankert am ANFANG des naechsten.
            rest = t[kopf.end():]
            m = re.search(r'(?m)^\[', rest)
            if m:
                stelle = kopf.end() + m.start()
                t = t[:stelle] + zeilen + ze + t[stelle:]
            else:
                t = t.rstrip() + ze + zeilen
        else:
            t = t.rstrip() + ze + ze + '[%s]%s' % (a, ze) + zeilen
        neu += len(nach_abschnitt[a])

    aus = t.encode('utf-8')
    n_crlf = aus.count(b'\r\n')
    n_lf = aus.count(b'\n') - n_crlf
    if (n_crlf > 0) != (vor_crlf > 0) or (n_lf > 0) != (vor_lf > 0):
        raise SystemExit('ABBRUCH %s: Zeilenenden veraendert' % pfad)
    open(pfad, 'wb').write(aus)
    return neu


if __name__ == '__main__':
    fehler = pruefe_werte()
    if fehler:
        print('ABBRUCH - der Erzeuger weist ab statt zurechtzubiegen:')
        for f in fehler:
            print('  ' + f)
        sys.exit(1)
    print('%d Schluessel, davon %d berechnete; alle Werte geprueft.'
          % (len(TEXTE), len(BERECHNET)))
    if len(sys.argv) < 2:
        print('Kein Plugin-Ordner angegeben - es wurde nur geprueft.')
        sys.exit(0)
    ordner = sys.argv[1]
    for sp in ('de', 'en'):
        p = os.path.join(ordner, 'templates', 'lang', 'language_%s.ini' % sp)
        n = einbauen(p, sp)
        print('  %s: %d Schluessel eingebaut' % (os.path.basename(p), n))
