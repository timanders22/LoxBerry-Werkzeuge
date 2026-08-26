# -*- coding: utf-8 -*-
"""Erzeugt help_de.ini und help_en.ini aus EINER Quelle.

Wie beim Sprachgenerator: ein Schluessel kann nicht nur in einer Sprache
stehen. Die Hilfe wird ROH ausgegeben (nicht maskiert), Auszeichnung ist
deshalb erlaubt - gerade Anfuehrungszeichen dagegen nicht, sie wuerden den
INI-Wert beenden.

Aufruf:  python3 Werkzeuge/ap_hilfe_erzeugen.py <Plugin-Ordner>
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
  'und gestartet. Zwei Stolpersteine gibt es dabei:',
  'The plugin measures nothing itself — it queries <code>apcupsd</code>, the '
  'service that talks to the UPS. It is installed and started along with the '
  'plugin. There are two pitfalls:'),
 ('K05',
  'In <code>/etc/default/apcupsd</code> steht nach der Paketinstallation '
  '<code>ISCONFIGURED=no</code>. Solange das so ist, startet apcupsd nicht. '
  'Die Installation dieses Plugins setzt den Wert auf <code>yes</code> — das '
  'ist die einzige Systemdatei, die angefasst wird.',
  'After the package installation <code>/etc/default/apcupsd</code> contains '
  '<code>ISCONFIGURED=no</code>. While that is the case apcupsd does not start. '
  'Installing this plugin sets the value to <code>yes</code> — that is the only '
  'system file it touches.'),
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
  '<b>Das Abo im MQTT-Gateway eintragen.</b> Ohne diesen Eintrag kommt am '
  'Miniserver nichts an — das ist die häufigste Fehlerursache überhaupt. Das '
  'einzutragende Thema steht im Reiter <i>MQTT</i> zum Abschreiben.',
  '<b>Enter the subscription in the MQTT gateway.</b> Without this entry '
  'nothing arrives at the Miniserver — this is the most common cause of failure '
  'by far. The topic to enter is shown in the <i>MQTT</i> tab.'),
 ('K10',
  '<b>Reiter Einbindung in Loxone → Vorlage herunterladen</b> und in Loxone '
  'Config über <i>Vorlage einfügen</i> einlesen. Die vollständige '
  'Baustein-Liste im selben Reiter zeigt, was danach zu verdrahten ist.',
  '<b>Loxone integration tab → download the template</b> and read it into '
  'Loxone Config via <i>Insert template</i>. The complete list of blocks in the '
  'same tab shows what to wire up afterwards.'),
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
  'Sekunden. Für neue Anlagen ist MQTT trotzdem der bessere Weg: der '
  'Miniserver muss nichts abfragen, und es kommen deutlich mehr Größen heraus.',
  'The original version provided an XML page that Loxone fetches itself. That '
  'page still exists and returns the same structure — anyone who has wired it '
  'up need not change anything. Since 1.2.0 it also honours the setting <i>UPS '
  'on another machine</i> and includes the derived values in a <code>CALC</code> '
  'block, together with their age in seconds. For new installations MQTT is '
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
 ('K35', '0 Netz, 1 Akku, 2 Vorwarnung, 3 Abschaltung läuft. Leer bei '
         'abgerissener Verbindung',
         '0 mains, 1 battery, 2 advance warning, 3 shutdown running. Empty when '
         'the connection is lost'),
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


fehl = 0
for i, sp in enumerate(('de', 'en')):
    text = bau(i)
    pfad = os.path.join(ZIEL, 'help_%s.ini' % sp)
    with io.open(pfad, 'wb') as fh:
        fh.write(text.encode('utf-8'))
    n = len([z for z in text.split('\n') if ' = "' in z])
    print('%s  %d Wertzeilen' % (pfad, n))
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
sys.exit(1 if fehl else 0)
