#!/usr/bin/env python3
"""Erzeugt language_de.ini und language_en.ini der Funkwacht aus EINER Quelle.

WARUM ES DIESEN ERZEUGER GIBT
-----------------------------
Ab 1.0.0 hat das Plugin ueber 400 Schluessel in zwei Sprachen. Zwei Dateien
von Hand gleichzuhalten geht eine Weile gut und dann nicht mehr: es fehlt ein
Schluessel auf einer Seite, und die Oberflaeche zeigt dort den Schluesselnamen
statt eines Textes - ohne Fehlermeldung. Hier steht jedes Paar an EINER
Stelle; das Auseinanderlaufen ist damit nicht mehr moeglich.

WER EINE SPRACHDATEI VON HAND AENDERT, ZIEHT DIESEN ERZEUGER MIT. Sonst gibt
es zwei Wahrheiten im selben Archiv, und die eine loescht die andere beim
naechsten Lauf. Der Kopf der erzeugten Dateien sagt das auch dort.

REGELN FUER JEDEN WERT
----------------------
* Echte Umlaute, keine HTML-Entitaeten. Die Oberflaeche schickt die meisten
  Texte durch fw_e(); ein notiertes &uuml; erschiene beim Leser woertlich.
* Attribute in Auszeichnung EINFACH quotieren (class='sm-mono'). Ein zweites
  doppeltes Anfuehrungszeichen beendet den Wert vorzeitig - je nach Lesemodus
  abgeschnitten oder die ganze Datei abgewiesen, und beides still.
* Typografische Anfuehrungszeichen, nie gerade.

STAND (Werkzeug-S1, 02.10.2026): nachgezogen auf Funkwacht 1.0.9 - erzeugt
die vier .ini des Archivs LoxBerry-Plugin-Funkwacht-1.0.9.zip byteweise gleich
(68 Schluessel und der Abschnitt EINHEIT kamen dazu, 11 Werte neu gefasst).
NACHZUG G2 (02.10.2026): LOX.BAUSTEINE und LOX.BAUSTEINE_ERL (fertiges
HTML mit getippten Nummern) entfallen; an ihrer Stelle 57 LOX.BS_*-
Schluessel fuer fw_bausteinliste() (Regel A4: zwei ODER statt einem mit
drei Eingaengen). Erzeugt die .ini des Baus vb_g2_fw_bau (Funkwacht 1.0.10)
byteweise gleich.
NACHZUG KOPF-WELLE (08.10.2026, Entscheidung Nr. 43, Pruefung-Durchgang-
2026-09-29/vb_kopf_fw_bau_skripte/werkzeug_bauen.py): nachgezogen auf
Funkwacht 1.0.12. In 1.0.11 waren ueber Anker in die .ini gekommen, ohne
diesen Erzeuger: VORL.Z2MNG_MQTT, WARUM.DIENST_FEHLT, der neue Wert von
FW_MQTT.G_WARUMNR (bis 10), der Abschnitt [DURCHSAGE] (17 Schluessel) und
der Block [ANSAGE] der gemeinsamen Sprachausgabe. Die Werte sind wortgleich
aus der .ini von 1.0.12 uebernommen; [ANSAGE] kommt wie bei au_/ww_ aus
Werkzeuge/gemeinsam/sprachausgabe_texte.json (gemeinsam_pruefen). Erzeugt
die vier .ini von LoxBerry-Plugin-Funkwacht-1.0.12 byteweise gleich.
Seit Werkzeug-S2 (02.10.2026) wird ALLES geprueft, bevor die erste Datei
geschrieben wird - auch die Hilfe gegen help.html. Ein abgebrochener Lauf
schreibt nichts.

STAND (vb_x10_fw, 09.10.2026, Welle X-10 / Sprachmodul 1.1.2): Baustein-Liste in der Grammatik
von Werkzeuge/leitungen_setzen.py (LOX.BS_E_ZWEI "I1 = .., I2 = ..", LOX.BS_E_NUR "Ausgang der
einzigen Quelle (#n)", neu LOX.BS_E_V1 "V1 = .." am Statusbaustein); DURCHSAGE.SICH_EINTRAG
entfaellt (Satz K_TTS_EINTRAG kommt mit Modul 1.1.2). [ANSAGE] wie immer aus
Werkzeuge/gemeinsam/sprachausgabe_texte.json (157 Schluessel).

STAND (vb_bild_fw, 09.10.2026, Welle Bild / Musterprojekt, Entscheidung 45): neu
LOX.BILD_ALT, LOX.BILD_UNTERSCHRIFT, LOX.MUSTERPROJEKT (Bild der Bausteine aus dem
LoxBerry-Plugins Musterprojekt unter der Baustein-Liste); sonst unveraendert.

STAND (vb_bild_fw15, 17.10.2026, Welle Bild 15 / Musterprojekt, Vollausstattung): Reiter "Einbindung in
Loxone" auf drei Seiten (Entwurf Welle 15 fw, E12): die 52 LOX.BS_*-Schluessel der alten Liste entfallen
(BS_SP_* und BS_H_ZEIT bleiben), neu 93 Schluessel am Ende von [LOX] (Vortext, Kaesten, Hinweise, 57
Tabellenzeilen Z1_01..Z3_06); E10 Texte STUFE (zuletzt versucht), ALARM und Heilungen (ohne Fehler bzw.
Heilversuche) in TAB, FW_MQTT, FW_FELD, ALLG und Hilfe K28; LOX.AUSFALL_TEXT (Bausteine 4 und 19),
LOX.BILD_UNTERSCHRIFT mit %s je Seite, Hilfe K27.

STAND (vb_bild_fw15n, 17.10.2026, Welle Bild 15 N / Nachzug der Musterliste): Tabellenzeilen wieder
wortgleich mit Musterprojekt/baustein_listen.txt - Seite "Funkwacht" #1-#4, #7 Typ mit Config-Namen
(Status, Analogkomparator, Benachrichtigung; englisch unveraendert), Seite "Funkwacht Sticks" #7, #10, #15,
#27, #28 Heilversuche statt Heilungen (englisch healing attempts), Nachtrag #9; LOG.H_VERLAUF "Heilversuche
je Tag" / "Healing attempts per day". Kein Schluessel neu oder gestrichen.

STAND (Erzeuger-Nachzug 01.11.2026): erzeugt Funkwacht 1.0.18 byteweise gleich
(language_*.ini und help_*.ini). Grundlage vb_g44_fw_bau_skripte/fw_sprache_erzeugen_g44.py
(Gruppe 44: ZAEHLER, Vorlagen Zigbee2MqttNG, [BEFEHL] u. a., Hilfe K61-K63), dazu Hilfe K64
(Mehrfachziele, Sprachmodul 1.2.1).

STAND (Drift-Abgleich, 06.11.2026): angeglichen an Funkwacht 1.0.23, 0 Schluessel neu, 2 Werte
geaendert (DURCHSAGE.H und DURCHSAGE.TEXT_HILFE: Sprachausgabe "ab Werk an" statt "aus", je de
und en), 0 entfernt.

Aufruf:  python3 Werkzeuge/fw_sprache_erzeugen.py [<Plugin-Ordner>]
"""

import re
import sys
from pathlib import Path

VORGABE = (Path(__file__).resolve().parent.parent
           / "LoxBerry-Plugin-Funkwacht-1.0.0")

# ======================================================================
# Die Texte. Je Eintrag: (Schluessel, deutsch, englisch)
# ======================================================================

TEXTE = [
 ("REITER", [
  ("EINSTELLUNGEN", "Einstellungen", "Settings"),
  ("LOXONE", "Einbindung in Loxone", "Loxone integration"),
  ("TEST", "Test", "Test"),
  ("LOG", "Logdateien", "Log files"),
 ]),
 ("ALLG", [
  ("TITEL", "Funkwacht", "Funkwacht"),
  ("SPEICHERN", "Speichern", "Save"),
  ("GESPEICHERT", "Die Einstellungen wurden gespeichert.",
   "The settings have been saved."),
  ("BEANSTANDUNG", "Nichts wurde gespeichert. Bitte diese Punkte richtigstellen:",
   "Nothing was saved. Please correct these points:"),
  ("MISSLUNGEN", "Der Vorgang ist nicht gelungen:", "The action did not succeed:"),
  ("EINMAL_FEHL", "Das Ergebnis ließ sich nicht für die nächste Seite ablegen (data/plugins nicht beschreibbar) — es steht deshalb hier, ohne Umleitung. Ein Neuladen dieser Seite würde den Vorgang wiederholen.", "The result could not be stored for the next page (data/plugins not writable) — so it is shown here, without a redirect. Reloading this page would repeat the action."),
  ("JA", "ja", "yes"),
  ("NEIN", "nein", "no"),
  ("UNBEKANNT", "nicht feststellbar", "cannot be determined"),
  ("KEINE", "keine", "none"),
  # Ein Knopf, dessen Wirkung sich nicht zuruecknehmen laesst, braucht ein
  # Haekchen. Der Satz steht bewusst als Beanstandung und nicht als Hinweis:
  # der Anwender hat gedrueckt und soll erfahren, dass nichts geschehen ist.
  ("OHNE_HAKEN",
   "Es ist nichts geschehen: Für diesen Knopf muss das Häkchen daneben gesetzt sein. Das ist Absicht — die Wirkung lässt sich nicht zurücknehmen.",
   "Nothing happened: this button requires the check box next to it to be ticked. That is intentional — the effect cannot be undone."),
  ("DIENST", "Wächter", "Watchdog"),
  ("LAEUFT", "läuft", "running"),
  ("GESTOPPT", "steht", "stopped"),
  ("KEINE_PID", "kein Prozess gefunden", "no process found"),
  ("GERAETE", "Sticks", "Sticks"),
  ("UEBERWACHT", "werden beobachtet", "being watched"),
  ("GESTOERT", "gestört", "faulty"),
  ("GESUND", "gesund", "healthy"),
  ("GERADE", "gerade eben", "right now"),
  ("GEHEILT", "Geheilt", "Healed"),
  ("SEIT_BEGINN", "Heilbefehle ohne Fehler",
   "healing commands without error"),
  ("VERSUCHE", "Versuche", "Attempts"),
  ("DAVON", "Heilversuche insgesamt", "recovery attempts in total"),
  ("LETZTE_PRUEFUNG", "Letzte Prüfung", "Last check"),
  ("SEKUNDEN", "Sekunden her", "seconds ago"),
  ("NIE", "noch nie geprüft", "never checked yet"),
 ]),
 ("FEHLER", [
  ("KEINE_ZAHL", "%s: „%s“ ist keine Zahl.", "%s: „%s“ is not a number."),
  ("KEINE_GANZZAHL", "%s: „%s“ ist keine ganze Zahl. Es wird nichts gerundet — bitte eine ganze Zahl eintragen.", "%s: „%s“ is not a whole number. Nothing is rounded — please enter a whole number."),
  ("KEINE_UHRZEIT",
   "%s: „%s“ ist keine Uhrzeit. Erwartet wird HH:MM, etwa 22:00 — oder ein leeres Feld.",
   "%s: „%s“ is not a time. Expected HH:MM, for example 22:00 — or an empty field."),
  ("AUSSERHALB", "%s: %s liegt außerhalb von %s bis %s.",
   "%s: %s is outside the range %s to %s."),
  ("NAME_FEHLT",
   "Stick %d: Es sind Angaben eingetragen, aber kein Name. Ohne Namen wird die Zeile nicht überwacht.",
   "Stick %d: There are entries but no name. Without a name the row is not watched."),
  ("PFAD_FEHLT", "Stick %d: Für diese Art wird ein Pfad oder eine Adresse gebraucht.",
   "Stick %d: This kind needs a path or an address."),
  ("THEMA_FEHLT", "Stick %d: Für die Art „MQTT“ wird ein Thema gebraucht.",
   "Stick %d: The kind „MQTT“ needs a topic."),
  ("DIENST_FEHLT",
   "Stick %d: Für die Art „systemd-Dienst“ wird der Name der Einheit gebraucht — im Feld „Pfad oder Adresse“ oder im Feld „systemd-Dienst“.",
   "Stick %d: The kind „systemd service“ needs the unit name — in the field „path or address“ or in the field „systemd service“."),
  ("CONTAINER_FEHLT",
   "Stick %d: Für die Art „Docker“ wird der Name des Containers gebraucht.",
   "Stick %d: The kind „Docker“ needs the container name."),
  ("KENNUNG",
   "Stick %d: „%s“ ist keine USB-Kennung. Erwartet werden vier plus vier Zeichen mit Doppelpunkt, etwa 1a86:55d4 — sie stehen im Reiter Test unter „USB-Geräte auflisten“.",
   "Stick %d: „%s“ is not a USB identifier. Expected four plus four characters with a colon, for example 1a86:55d4 — they are listed in the Test tab under „list USB devices“."),
  ("KEIN_HEBEL",
   "Stick %d: Heilen ist eingeschaltet, aber es ist weder ein Dienst noch ein Container, ein USB-Pfad oder ein Verteiler eingetragen. Damit gäbe es nichts, woran der Wächter ziehen könnte.",
   "Stick %d: Healing is switched on, but neither a service nor a container, a USB path or a hub has been entered. There would be nothing for the watchdog to pull on."),
  ("UHUBCTL_UNVOLLSTAENDIG",
   "Stick %d: Höchststufe 3 verlangt einen Verteiler und eine Anschlussnummer größer als 0.",
   "Stick %d: Level 3 requires a hub and a port number greater than 0."),
  ("RUHE_ZU_LANG",
   "Stick %d: Die Erholungszeit (%d s) ist nicht kürzer als der Mindestabstand (%d s). Damit gilt der Stick bis zum nächsten erlaubten Versuch als gesund, und es käme nie wieder einer zustande.",
   "Stick %d: The recovery time (%d s) is not shorter than the minimum interval (%d s). The stick would count as healthy until the next attempt is due, so no attempt would ever happen."),
  ("THEMA",
   "Das MQTT-Thema „%s“ enthält unerlaubte Zeichen. Erlaubt sind Kleinbuchstaben, Ziffern, Bindestrich, Unterstrich und der Schrägstrich. Die Platzhalter + und # sind Suchmuster und als Ziel unbrauchbar.",
   "The MQTT topic „%s“ contains characters that are not allowed. Allowed are lower-case letters, digits, hyphen, underscore and the slash. The wildcards + and # are filter patterns and useless as a target."),
  ("BROKER_PORT",
   "Der Broker-Anschluss „%s“ ist keine Zahl zwischen 1 und 65535.",
   "The broker port „%s“ is not a number between 1 and 65535."),
  ("SIGNAL_URL",
   "Die Adresse für SignalBot sieht nicht wie eine Web-Adresse aus: „%s“. Erwartet wird etwas, das mit http:// oder https:// beginnt.",
   "The SignalBot address does not look like a web address: „%s“. Expected something starting with http:// or https://."),
  ("SIGNAL_LEER",
   "Die Weitergabe an SignalBot ist eingeschaltet, aber es steht keine Adresse da. Ein eingeschalteter Schalter ohne Ziel meldet nichts und sagt es auch nicht.",
   "Forwarding to SignalBot is switched on but no address is entered. A switch without a target reports nothing and does not say so."),
  ("ZU_VIELE", "Es sind schon %d Zeilen — mehr führt diese Oberfläche nicht.",
   "There are already %d rows — this interface does not manage more."),
  ("SPEICHERN",
   "Die Einstellungen konnten nicht geschrieben werden. Bitte die Rechte am Ordner config/plugins prüfen.",
   "The settings could not be written. Please check the permissions of config/plugins."),
  ("EINHEIT", "Stick %d: „%s“ taugt nicht als systemd-Dienst: %s", "Stick %d: „%s“ cannot be used as a systemd service: %s"),
  ("CONTAINER", "Stick %d: „%s“ taugt nicht als Containername. Erlaubt sind Buchstaben, Ziffern, Punkt, Bindestrich und Unterstrich, und das erste Zeichen ist ein Buchstabe oder eine Ziffer.", "Stick %d: „%s“ cannot be used as a container name. Allowed are letters, digits, dot, hyphen and underscore, and the first character is a letter or a digit."),
  ("KENNWORT_ZEICHEN", "Das Kennwort enthält Steuerzeichen, etwa einen Zeilenumbruch oder Tabulator. Solche Zeichen werden nicht angenommen — das bisherige Kennwort bleibt stehen.", "The password contains control characters, for example a line break or a tab. Such characters are not accepted — the previous password stays."),
  ("KENNUNG_PFLICHT", "Stick %d: Stufe 2 oder 3 ist eingeschaltet (Heilen an, USB-Pfad bzw. Verteiler eingetragen). Dann ist die erwartete USB-Kennung Pflicht — ohne sie setzte der Wächter auch ein fremdes Gerät zurück, das jemand in denselben Anschluss gesteckt hat. Die Kennung steht im Reiter Test unter „USB-Geräte auflisten“.", "Stick %d: level 2 or 3 is switched on (healing on, USB path or hub entered). Then the expected USB identifier is mandatory — without it the watchdog would also reset a foreign device somebody plugged into the same port. The identifier is listed in the Test tab under „list USB devices“."),
  ("FELD_LEER", "%s: Das Feld ist leer. Der bisherige Wert wird nicht still behalten — bitte eine Zahl eintragen.", "%s: the field is empty. The previous value is not silently kept — please enter a number."),
  ("ZEICHEN", "%s: „%s“ enthält Anführungs- oder Steuerzeichen. Sie werden nicht still entfernt — bitte ohne diese Zeichen eintragen.", "%s: „%s“ contains quotes or control characters. They are not silently removed — please enter it without them."),
  ("KEIN_TEXT", "%s: Die Eingabe kam nicht als einzelner Text an und wurde nicht übernommen.", "%s: the input did not arrive as a single text and was not accepted."),
  ("AUSWAHL", "%s: „%s“ gehört nicht zur Auswahl. Es wird nicht still ein anderer Wert gesetzt — bitte aus der Liste wählen.", "%s: „%s“ is not one of the choices. No other value is set silently — please choose from the list."),
  ("THEMA_LEER", "Das MQTT-Thema ist leer. Es wird nicht still auf „funkwacht“ gesetzt — bitte ein Thema eintragen.", "The MQTT topic is empty. It is not silently set to „funkwacht“ — please enter a topic."),
  ("THEMA_RAND", "Das MQTT-Thema „%s“ beginnt oder endet mit einem Schrägstrich. Er wird nicht still entfernt — im Broker ist /funkwacht ein anderes Thema als funkwacht.", "The MQTT topic „%s“ starts or ends with a slash. It is not silently removed — in the broker /funkwacht is a different topic from funkwacht."),
  ("FREMDES_FORMULAR",
   "Dieses Formular trug kein gültiges Merkmal und wurde abgewiesen. Das schützt davor, dass eine fremde Seite im Hintergrund Ihr Wortzeichen neu würfelt oder das Protokoll leert. Bitte die Seite neu laden und den Vorgang wiederholen.",
   "This form carried no valid marker and was rejected. That protects you from a foreign page silently re-rolling your access word or clearing the log. Please reload the page and try again."),
 ]),
 ("EINHEIT", [
  ("LEER", "Der Name ist leer.", "The name is empty."),
  ("ZEICHEN", "Erlaubt sind Buchstaben, Ziffern, @, Punkt, Bindestrich und Unterstrich.", "Allowed are letters, digits, @, dot, hyphen and underscore."),
  ("STRICH", "Ein Name, der mit einem Bindestrich beginnt, wäre für systemctl ein Schalter.", "A name starting with a hyphen would be an option for systemctl."),
  ("ENDUNG", "Neu gestartet wird nur ein Dienst (Endung .service oder gar keine Endung) — keine .target-, .socket-, .mount- oder andere Einheit.", "Only a service is restarted (ending .service or no ending at all) — no .target, .socket, .mount or other unit."),
  ("ANFANG", "Ein Name beginnt mit einem Buchstaben oder einer Ziffer — nicht mit Punkt, @ oder Unterstrich.", "A name starts with a letter or a digit — not with a dot, @ or underscore."),
  ("DOPPELT", "Die Endung steht doppelt (etwa .service.service) — so heißt keine Einheit.", "The suffix appears twice (such as .service.service) — no unit is called that."),
  ("VORLAGE", "Eine Vorlage mit @ braucht genau einen Namen davor und eine Instanz dahinter, etwa getty@tty1.", "A template with @ needs exactly one name in front and an instance behind it, such as getty@tty1."),
  ("TABU", "Einheiten der Art „%s“ startet die Funkwacht nie neu: ein Neustart träfe das ganze System, den Zugang, den Webserver, den Broker oder LoxBerry selbst.", "Funkwacht never restarts units of the kind „%s“: a restart would hit the whole system, remote access, the web server, the broker or LoxBerry itself."),
 ]),
 ("LEGENDE", [
  ("LESEN", "Grün fragt nur ab und verändert nichts.",
   "Green only reads and changes nothing."),
  ("LESEN_START", "Grün startet den Wächter — das ist umkehrbar und stört nichts.",
   "Green starts the watchdog — that is reversible and disturbs nothing."),
  ("TECHNIK", "Grau zeigt Technisches zum Nachsehen.",
   "Grey shows technical details."),
  ("TECHNIK_XML", "Grau lädt eine Vorlagendatei herunter.",
   "Grey downloads a template file."),
  ("TECHNIK_VORLAGE", "Grau füllt eine Zeile mit Vorschlagswerten — gespeichert wird sofort.",
   "Grey fills a row with suggested values — saved immediately."),
  ("TECHNIK_ZEILE", "Grau ändert die Zeilen der Liste.",
   "Grey changes the rows of the list."),
  ("TECHNIK_SICHERN", "Grau lädt die Einstellungen als Datei herunter.",
   "Grey downloads the settings as a file."),
  ("AKTION_SPEICHERN", "Orange schreibt die Einstellungen.",
   "Orange writes the settings."),
  ("AKTION_ZURUECK", "Orange überschreibt ALLE Einstellungen mit der hochgeladenen Datei.",
   "Orange overwrites ALL settings with the uploaded file."),
  ("AKTION_DIENST",
   "Orange greift in den laufenden Betrieb ein — der Wächter hält an oder startet neu.",
   "Orange interferes with the running operation — the watchdog stops or restarts."),
  ("AKTION_SCHALTEN",
   "Orange wirkt sofort auf das Gerät: ein Heilversuch startet wirklich einen Dienst neu oder zieht einem Anschluss den Strom.",
   "Orange acts on the device immediately: a healing attempt really restarts a service or cuts power to a port."),
  ("AKTION_TOKEN",
   "Orange erzeugt ein neues Wortzeichen — die alte Adresse gilt danach nicht mehr.",
   "Orange creates a new access word — the old address stops working."),
  ("AKTION_LOG", "Orange löscht das Protokoll.", "Orange clears the log."),
 ]),
 ("DIENST", [
  ("H", "Den Wächter schalten", "Control the watchdog"),
  ("ERKLAERUNG",
   "Der Minutentakt startet den Wächter von selbst, wenn er steht — bis zu einer Minute später. Diese Knöpfe wirken sofort. Nach jedem Schalten wird nachgesehen, ob der Prozess wirklich läuft; gemeldet wird die Wirkung, nicht der Rückgabewert.",
   "The one-minute cron starts the watchdog by itself when it is down — up to a minute later. These buttons act immediately. After each action the process is checked again; what is reported is the effect, not the return code."),
  ("MITHOERER",
   "Dazu läuft der MQTT-Mithörer, weil mindestens ein Stick auf die Art „MQTT“ steht: %s",
   "The MQTT listener runs alongside, because at least one stick uses the kind „MQTT“: %s"),
  ("K_START", "Wächter starten", "Start watchdog"),
  ("K_RESTART", "Wächter neu starten", "Restart watchdog"),
  ("K_STOP", "Wächter anhalten", "Stop watchdog"),
  ("START", "Starten", "Start"),
  ("RESTART", "Neustarten", "Restart"),
  ("STOP", "Anhalten", "Stop"),
  ("OK", "%s: erledigt — nachgemessen am laufenden Prozess.",
   "%s: done — verified against the running process."),
  ("FEHL", "%s ist nicht durchgegangen: %s", "%s did not succeed: %s"),
  ("RUECKGABE", "Rückgabewert %d, keine Ausgabe", "return value %d, no output"),
  ("UNBEKANNT", "unbekannter Schaltbefehl", "unknown switching command"),
  ("KEIN_SKRIPT",
   "Das Startskript dienst.sh wurde nicht gefunden. Bitte das Plugin neu installieren.",
   "The start script dienst.sh was not found. Please reinstall the plugin."),
 ]),
 ("EINST", [
  # Kopf wie alle Hausplugins (Entscheidung Nr. 43, 1.0.12): gruener Kasten
  # oben im Reiter Einstellungen, roh ausgegeben (fw_t ohne fw_e).
  ("WAS_IST_DAS",
   "<b>Wächter für Funksticks am LoxBerry — Zigbee, Z-Wave, Bluetooth.</b> Die Funkwacht prüft je Stick ein Lebenszeichen, etwa das Alter einer Protokolldatei, ein MQTT-Thema, den USB-Anschluss oder einen Dienst. Verstummt ein Stick, weckt sie ihn in Stufen wieder auf (Dienst neu starten, USB-Anschluss neu anmelden, Strom am Verteiler) und misst nach, ob es geholfen hat. Zustand und Zähler gehen über das MQTT-Gateway und einen HTTP-Endpunkt an den Miniserver; eine Störung meldet sie außerdem als LoxBerry-Meldung, auf Wunsch auch über SignalBot oder als Ansage.",
   "<b>Watchdog for radio sticks on the LoxBerry — Zigbee, Z-Wave, Bluetooth.</b> Funkwacht checks a sign of life for each stick, such as the age of a log file, an MQTT topic, the USB port or a service. If a stick falls silent, it wakes it up again in stages (restart the service, re-register the USB port, cut power at the hub) and measures whether that helped. State and counters reach the Miniserver over the MQTT gateway and an HTTP endpoint; a fault is also reported as a LoxBerry notification, and on request via SignalBot or as an announcement."),
  ("H_LAGE", "Wie steht es gerade?", "How are things right now?"),
  ("LAGE_ERKLAERUNG",
   "Der Wächter sieht in festem Takt nach, ob jeder eingetragene Funkstick noch Zeichen von sich gibt. Meldet einer sich zu lange nicht, wird er in Stufen wiederbelebt. Der Wächter fasst dabei <b>keinen</b> Stick an, der die Systemplatte trägt — und er heilt <b>nicht</b>, wenn von einem Stick noch nie ein Lebenszeichen kam: das ist fast immer ein Eintragungsfehler.",
   "The watchdog checks at a fixed interval whether every configured radio stick still shows signs of life. If one stays silent for too long it is revived in stages. The watchdog never touches a stick that carries the system disk — and it does <b>not</b> heal when a stick has never shown any sign of life: that is almost always a configuration mistake."),
  ("SPERRE_LAEUFT",
   "<b>Es wird gerade nicht geheilt:</b> %s. Gemeldet wird weiter — in Loxone stehen die Werte also aktuell da, nur eingegriffen wird nicht.",
   "<b>No healing is happening right now:</b> %s. Reporting continues — the values in Loxone stay current, only no action is taken."),
  ("NOCH_NICHTS",
   "Es liegt noch keine Messung vor. Entweder ist noch kein Stick eingetragen, oder der Wächter läuft noch nicht — der erste Durchlauf kommt spätestens nach einer Minute.",
   "There is no measurement yet. Either no stick has been entered, or the watchdog is not running yet — the first run happens within a minute."),
  ("TABU",
   "Nicht angefasst wird: %s. Diese Geräte tragen die Systemplatte oder den Startbereich; ein Zurücksetzen des Anschlusses hinge das laufende System ab.",
   "Never touched: %s. These devices carry the system disk or the boot area; resetting their port would detach the running system."),
  ("FAEHIGKEIT",
   "Rechte über sudo: %s. uhubctl vorhanden: %s. Verteiler, die den Strom wirklich schalten können: %s. Ein Verteiler, der hier nicht auftaucht, kann den Anschluss nicht stromlos machen — Stufe 3 bliebe dort wirkungslos.",
   "Permissions via sudo: %s. uhubctl present: %s. Hubs that can really switch power: %s. A hub that does not appear here cannot cut the power of a port — level 3 would have no effect there."),
  ("VERTEILER_HINWEIS", "Achtung, Stick %d: Stufe 3 am Verteiler „%s“ würde der Wächter ablehnen — %s Stufe 1 und 2 bleiben möglich. Welcher Verteiler das System nicht trägt, zeigt der Reiter Test unter „USB-Geräte auflisten“.", "Note, stick %d: the watchdog would refuse level 3 at hub „%s“ — %s Levels 1 and 2 remain possible. Which hub does not carry the system is shown in the Test tab under „list USB devices“."),
  ("VT_WURZEL", "„%s“ ist ein Wurzelverteiler; er speist alle Anschlüsse dieses Busses, auch die Systemplatte.", "„%s“ is a root hub; it feeds every port of this bus, the system disk included."),
  ("VT_FORM", "„%s“ sieht nicht wie eine Verteilerkennung aus (erwartet etwa 1-1).", "„%s“ does not look like a hub identifier (expected something like 1-1)."),
  ("VT_SYSTEM", "%s trägt das System (%s).", "%s carries the system (%s)."),
  ("VT_NACHBAR", "am Verteiler %s hängt ein Gerät, auf dem das System liegt (%s).", "a device carrying the system hangs on hub %s (%s)."),
  ("DOCKER_FEHLT", "<b>Docker fehlt auf diesem LoxBerry.</b> Zeile %s beobachtet einen Docker-Container; ohne Docker meldet sie nur „docker inspect antwortet nicht“. Docker lässt sich mit dem LoxBerry-Plugin <b>Docker NG</b> installieren (<a href='https://github.com/timanders22/LoxBerry-Plugin-Docker-NG' target='_blank' rel='noopener'>github.com/timanders22/LoxBerry-Plugin-Docker-NG</a>); danach diese Seite neu laden. Die Funkwacht legt selbst keine Container an.", "<b>Docker is missing on this LoxBerry.</b> Row %s watches a Docker container; without Docker it only reports „docker inspect does not answer“. Docker can be installed with the LoxBerry plugin <b>Docker NG</b> (<a href='https://github.com/timanders22/LoxBerry-Plugin-Docker-NG' target='_blank' rel='noopener'>github.com/timanders22/LoxBerry-Plugin-Docker-NG</a>); then reload this page. Funkwacht does not create containers itself."),
  ("DOCKER_KEIN_ZUGRIFF", "<b>Kein Zugriff auf Docker.</b> Zeile %s beobachtet einen Docker-Container, aber Docker antwortet dem Plugin nicht: %s Der Benutzer <span class='sm-mono'>loxberry</span> muss in der Gruppe <span class='sm-mono'>docker</span> sein, und der Docker-Dienst muss laufen. Beides richtet das LoxBerry-Plugin <b>Docker NG</b> ein (<a href='https://github.com/timanders22/LoxBerry-Plugin-Docker-NG' target='_blank' rel='noopener'>github.com/timanders22/LoxBerry-Plugin-Docker-NG</a>); danach diese Seite neu laden.", "<b>No access to Docker.</b> Row %s watches a Docker container, but Docker does not answer the plugin: %s The user <span class='sm-mono'>loxberry</span> must be in the group <span class='sm-mono'>docker</span>, and the Docker service must be running. The LoxBerry plugin <b>Docker NG</b> sets up both (<a href='https://github.com/timanders22/LoxBerry-Plugin-Docker-NG' target='_blank' rel='noopener'>github.com/timanders22/LoxBerry-Plugin-Docker-NG</a>); then reload this page."),
  ("DOCKER_G_HAENGT", "Docker antwortet nicht innerhalb von %d s.", "Docker does not answer within %d s."),
  ("DOCKER_G_GRUPPE", "Dem Benutzer loxberry fehlt die Gruppe docker.", "The user loxberry lacks the group docker."),
  ("DOCKER_G_DIENST", "Der Docker-Dienst läuft nicht.", "The Docker service is not running."),
  ("DOCKER_G_FEHLER", "Docker meldet Rückgabe %d.", "Docker reports return code %d."),
  ("H_GERAETE", "Welche Sticks sollen beobachtet werden?",
   "Which sticks should be watched?"),
  ("GERAETE_ERKLAERUNG",
   "Eine Zeile je Stick. Es zählt nur, was einen Namen hat. <b>Die Zeilennummer ist die Adresse</b> — Zeile 3 heißt in Loxone immer <span class='sm-mono'>G3…</span>, auch wenn Zeile 1 und 2 leer sind. So bleibt einem Stick seine Nummer erhalten, wenn ein anderer herausgenommen wird. <b>Der Wächter öffnet niemals selbst eine serielle Schnittstelle</b> — er sähe sonst nach, indem er sie Zigbee2MQTT wegnimmt.",
   "One row per stick. Only rows with a name count. <b>The row number is the address</b> — row 3 is always <span class='sm-mono'>G3…</span> in Loxone, even if rows 1 and 2 are empty. That way a stick keeps its number when another one is removed. <b>The watchdog never opens a serial port itself</b> — it would check by taking it away from Zigbee2MQTT."),
  ("GERAET", "Stick", "Stick"),
  ("L_NAME", "Name", "Name"),
  ("L_ART", "Woran erkennen?", "How to detect?"),
  ("L_PFAD", "Pfad oder Adresse", "Path or address"),
  ("L_THEMA", "MQTT-Thema", "MQTT topic"),
  ("L_KENNUNG", "USB-Kennung", "USB identifier"),
  ("L_ART2", "Zweites Kriterium", "Second criterion"),
  ("L_VERKN", "verknüpft mit", "combined with"),
  ("L_PFAD2", "Pfad oder Adresse (2)", "Path or address (2)"),
  ("L_THEMA2", "MQTT-Thema (2)", "MQTT topic (2)"),
  ("V_UND", "UND — beide müssen frisch sein", "AND — both must be fresh"),
  ("V_ODER", "ODER — eines genügt", "OR — one is enough"),
  ("L_HOECHSTALTER", "Stumm bis (s)", "Silent until (s)"),
  ("L_DIENST", "systemd-Dienst", "systemd service"),
  ("L_CONTAINER", "Docker-Container", "Docker container"),
  ("L_USB_PFAD", "USB-Pfad", "USB path"),
  ("L_HUB", "Verteiler / Anschluss", "Hub / port"),
  ("L_HOECHSTSTUFE", "Höchste Stufe", "Highest level"),
  ("L_FOLGE", "Reihenfolge", "Order"),
  ("F_NORMAL", "1 Dienst, 2 USB, 3 Strom", "1 service, 2 USB, 3 power"),
  ("F_USB", "2 USB, 1 Dienst, 3 Strom", "2 USB, 1 service, 3 power"),
  ("L_AKTIV", "beobachten", "watch"),
  ("L_HEILEN", "heilen dürfen", "may heal"),
  ("L_WACHSTUM", "Datei muss wachsen", "file must grow"),
  ("L_DIENSTNACH", "Dienst danach mitnehmen", "restart service afterwards"),
  ("L_LERNEN", "taube Stufe überspringen", "skip a level that never helps"),
  ("L_RUHE_S", "Erholung (s)", "Recovery (s)"),
  ("L_ABSTAND_S", "Abstand (s)", "Interval (s)"),
  ("L_JE_TAG", "Versuche je Tag", "Attempts per day"),
  ("L_PORT", "Anschluss", "Port"),
  ("L_TAKT", "Prüftakt (Sekunden)", "Check interval (seconds)"),
  ("L_ANLAUF_S", "Anlaufschonzeit (Sekunden)", "Start-up grace period (seconds)"),
  ("L_RUHEFENSTER", "Nicht heilen zwischen (HH:MM und HH:MM)",
   "Do not heal between (HH:MM and HH:MM)"),
  ("L_GLOBAL_AUS", "Nur melden, nichts heilen (alle Sticks)",
   "Report only, heal nothing (all sticks)"),
  ("L_LOG_KB", "Protokoll kappen ab (kB)", "Trim log above (kB)"),
  ("L_VERLAUF_TAGE", "Verlauf aufbewahren (Tage)", "Keep history (days)"),
  ("FELDER_HILFE",
   "<b>Woran erkennen:</b> „Datei“ sieht auf das Änderungsdatum; mit dem Haken <i>Datei muss wachsen</i> zählt nur, dass sie größer geworden ist — manche Dienste fassen ihr Protokoll auch dann an, wenn sie nichts mehr zu melden haben. „MQTT“ braucht den Mithörer aus dem Reiter MQTT. „HTTP“ ruft eine Adresse ab; dort gibt es nur „antwortet“ oder „antwortet nicht“, das Höchstalter bleibt also ohne Wirkung, und Weiterleitungen werden absichtlich <b>nicht</b> verfolgt. „USB“ sieht nach, ob der Stick überhaupt noch am Bus hängt — das ist die einzige Art, die „Stick weg“ von „Dienst hängt“ unterscheidet; in den Pfad gehört die Kennung wie <span class='sm-mono'>1-1.4</span>, in die USB-Kennung <span class='sm-mono'>1a86:55d4</span> als Gegenprobe gegen ein umgestecktes Gerät — Pflicht, sobald Stufe 2 oder 3 eingeschaltet ist. „systemd-Dienst“ und „Docker“ fragen den Dienst selbst (Docker richtet das Plugin Docker NG ein); beide melden zusätzlich den Neustartzähler — ein Dienst, den das System alle drei Minuten neu startet, ist nach dem Änderungsdatum seines Protokolls kerngesund. <b>Zweites Kriterium:</b> „USB vorhanden UND MQTT frisch“ trennt sauber zwischen den beiden Fehlerbildern. <b>Stumm bis:</b> Nach so vielen Sekunden ohne Lebenszeichen gilt der Stick als gestört; großzügig ansetzen. <b>Reihenfolge:</b> Bei manchen Aufbauten bringt ein Dienstneustart nichts, solange der Stick selbst festgefahren ist. <b>Dienst danach mitnehmen:</b> Ein unbind/bind lässt den Dienst mit einem toten Dateideskriptor zurück — der Neustart kommt deshalb gleich hinterher. <b>Erholung:</b> So lange nach einem Heilversuch gilt der Stick als gesund und nicht als gestört; der Wert muss kleiner sein als der Abstand. <b>Taube Stufe überspringen:</b> ab Werk aus. Eingeschaltet wird eine Stufe übergangen, die zehnmal versucht wurde und nie geholfen hat — aber nur, solange eine andere übrig ist.",
   "<b>How to detect:</b> „File“ looks at the modification time; with the tick <i>file must grow</i> only an increase in size counts — some services touch their log even when they have nothing left to report. „MQTT“ needs the listener from the MQTT tab. „HTTP“ calls an address; there it is only „answers“ or „does not answer“, so the maximum age has no effect, and redirects are deliberately <b>not</b> followed. „USB“ checks whether the stick is still on the bus at all — the only kind that separates „stick gone“ from „service stuck“; the path takes the identifier such as <span class='sm-mono'>1-1.4</span>, the USB identifier <span class='sm-mono'>1a86:55d4</span> as a cross-check against a device moved to another port — mandatory as soon as level 2 or 3 is switched on. „systemd service“ and „Docker“ ask the service itself (Docker is set up by the plugin Docker NG); both also report the restart counter — a service the system restarts every three minutes looks perfectly healthy by the modification time of its log. <b>Second criterion:</b> „USB present AND MQTT fresh“ cleanly separates the two failure modes. <b>Silent until:</b> after this many seconds without a sign of life the stick counts as faulty; be generous. <b>Order:</b> in some setups a service restart achieves nothing while the stick itself is locked up. <b>Restart service afterwards:</b> an unbind/bind leaves the service with a dead file descriptor — the restart therefore follows immediately. <b>Recovery:</b> for this long after an attempt the stick counts as healthy, not as faulty; the value must be smaller than the interval. <b>Skip a level that never helps:</b> off by default. When on, a level that has been tried ten times without ever helping is skipped — but only while another one is left."),
  ("H_BETRIEB", "Betrieb", "Operation"),
  ("H_TAKT",
   "So oft sieht der Wächter nach. 60 Sekunden sind ein guter Wert; kürzer bringt selten mehr, weil die Stummzeit ohnehin in Minuten gemessen wird.",
   "How often the watchdog looks. 60 seconds is a good value; shorter rarely helps, because the silence period is measured in minutes anyway."),
  ("H_ANLAUF",
   "So lange nach dem Systemstart wird nur gemeldet und nicht geheilt. Kurz nach einem Neustart ist jede Protokolldatei alt und jedes MQTT-Thema leer — ohne diese Schonzeit startete der Wächter einen Dienst neu, der gerade selbst hochfährt. 0 schaltet sie ab. Lässt sich die Betriebsdauer nicht lesen, gilt KEINE Schonzeit: ein Wächter, der im Zweifel gar nichts tut, wäre schlechter als einer, der zu früh anfängt.",
   "For this long after the system starts, the watchdog only reports and does not heal. Shortly after a reboot every log file is old and every MQTT topic empty — without this grace period the watchdog would restart a service that is still starting itself. 0 switches it off. If the uptime cannot be read, NO grace period applies: a watchdog that does nothing when in doubt would be worse than one that starts too early."),
  ("H_RUHEFENSTER",
   "In diesem Zeitfenster wird nur gemeldet. Gedacht für den Fall, dass ein Container-Neustart nachts eine Türsprechanlage für eine Minute stumm machen würde. Beide Felder leer heißt: kein Fenster. Ein Fenster über Mitternacht (22:00 bis 06:00) wird richtig behandelt.",
   "In this time window the watchdog only reports. Meant for cases where a container restart would silence a door intercom for a minute at night. Both fields empty means no window. A window across midnight (22:00 to 06:00) is handled correctly."),
  ("H_GLOBAL_AUS",
   "Der Schalter für einen Umbau: gemessen und gemeldet wird weiter, geheilt wird nichts. Er geht <b>nicht</b> von selbst wieder aus — dafür gibt es die Wartung im Reiter Test.",
   "The switch for maintenance work: measuring and reporting continue, nothing is healed. It does <b>not</b> switch itself off again — for that there is the maintenance mode in the Test tab."),
  ("H_LOG_KB",
   "Ab dieser Größe wird das Protokoll auf die letzten 400 Zeilen gekürzt. Der Ordner log/plugins liegt auf einer Ramdisk — eine unbegrenzt wachsende Datei frisst Arbeitsspeicher, nicht Plattenplatz. Der Wert gilt für den Wächter und für die Oberfläche.",
   "Above this size the log is trimmed to the last 400 lines. The folder log/plugins is on a RAM disk — a file that grows without limit eats memory, not disk space. The value applies to the watchdog and to the interface."),
  ("H_VERLAUF_TAGE",
   "So lange werden die Tagesdateien des Verlaufs aufbewahrt. Sie liegen unter data/ und überstehen damit einen Neustart; daraus entsteht das Balkenbild im Reiter Logdateien.",
   "The daily history files are kept for this long. They live under data/ and therefore survive a reboot; the bar chart in the Log files tab is built from them."),
  ("H_ZEILEN", "Zeilen der Liste", "Rows of the list"),
  ("H_ZEILEN_TEXT",
   "Eine geleerte Zeile behält ihren <b>Platz</b>. Würde sie herausfallen, rückten alle folgenden nach — und der virtuelle Eingang im Miniserver zeigte still auf einen anderen Stick.",
   "A cleared row keeps its <b>position</b>. If it dropped out, all following rows would move up — and the virtual input in the Miniserver would silently point at a different stick."),
  ("K_ZEILE_DAZU", "Eine Zeile hinzufügen", "Add a row"),
  ("K_ZEILE_LEER", "Zeile %d leeren (%s)", "Clear row %d (%s)"),
  ("ZEILE_DAZU_OK", "Es gibt jetzt %d Zeilen.", "There are now %d rows."),
  ("ZEILE_LEER_OK", "Zeile %d ist leer — ihre Nummer bleibt vergeben.",
   "Row %d is empty — its number stays assigned."),
 ]),
 ("VORL", [
  ("H", "Fertige Zeilen für die bekannten Fälle", "Ready-made rows for the common cases"),
  ("ERKLAERUNG",
   "Ein Klick füllt eine Zeile mit Vorschlagswerten und speichert sie. <b>Diese Pfade sind Vorschläge aus der Erfahrung, keine Messwerte</b> — sie gehören geprüft, und dafür gibt es im Reiter Test den Knopf „Jetzt messen“ neben jeder Zeile. Ein vorhandener Name bleibt stehen.",
   "One click fills a row with suggested values and saves it. <b>These paths are suggestions from experience, not measurements</b> — they need checking, and the Test tab has a „measure now“ button next to every row for exactly that. An existing name is kept."),
  ("SP_FALL", "Fall", "Case"),
  ("SP_WERTE", "Was gesetzt wird", "What is set"),
  ("SP_ZEILE", "in Zeile", "into row"),
  ("K_SETZEN", "einsetzen", "insert"),
  ("GESETZT", "Zeile %d wurde mit der Vorlage „%s“ gefüllt.",
   "Row %d has been filled from the template „%s“."),
  ("PRUEFEN",
   "Bitte den Pfad prüfen: im Reiter Test steht neben jeder Zeile ein Knopf „Jetzt messen“.",
   "Please check the path: the Test tab has a „measure now“ button next to every row."),
  ("UNBEKANNT", "Diese Vorlage oder diese Zeile gibt es nicht.",
   "There is no such template or no such row."),
  ("Z2M_PAKET", "Zigbee2MQTT als Paket", "Zigbee2MQTT as a package"),
  ("Z2M_MQTT", "Zigbee2MQTT über MQTT (nur melden)", "Zigbee2MQTT via MQTT (report only)"),
  ("Z2MNG_MQTT",
   "Zigbee2MqttNG über MQTT (nur melden)",
   "Zigbee2MqttNG via MQTT (report only)"),
  ("Z2M_DOCKER", "Zigbee2MQTT im Container", "Zigbee2MQTT in a container"),
  ("ZWAVEJS", "Z-Wave JS UI", "Z-Wave JS UI"),
  ("DECONZ", "deCONZ", "deCONZ"),
  ("BLUETOOTH", "Bluetooth-Adapter", "Bluetooth adapter"),
  ("SERIELL", "Serieller Stick", "Serial stick"),
 ]),
 ("MELD", [
  ("H", "Melden, wenn niemand hinsieht", "Reporting when nobody is watching"),
  ("ERKLAERUNG",
   "Gemeldet wird nur beim <b>Wechsel</b> des Befundes — und mit Entwarnung, sobald ein Stick wieder gesund ist. Eine Meldung je Minute wäre keine Meldung, sondern Rauschen.",
   "A message is sent only when the finding <b>changes</b> — and an all-clear follows as soon as a stick is healthy again. A message every minute would not be a message but noise."),
  ("L_ZENTRUM", "Ins LoxBerry-Benachrichtigungszentrum melden",
   "Report to the LoxBerry notification centre"),
  # „Nicht am Geraet erprobt“ steht dabei, weil der Endpunkt aus der
  # Oberflaeche des Nachbarplugins ABGESCHRIEBEN ist - belegt, aber nie
  # gegen einen laufenden Bot gemessen. Belegt und erprobt sind zweierlei.
  ("L_SIGNAL", "Zusätzlich an SignalBot schicken (nicht am Gerät erprobt)",
   "Also send to SignalBot (not tested on a device)"),
  ("L_SIGNAL_URL", "Adresse des SignalBot-Endpunkts", "Address of the SignalBot endpoint"),
  ("H_SIGNAL_URL",
   "Die vollständige Adresse mit dem Wortzeichen des SignalBot, ohne den Text — der wird angehängt. Sie steht dort im Reiter <i>Einbindung in Loxone</i>, etwa <span class='sm-mono'>http://loxberry/plugins/signalbot/index.php?token=xxx&amp;aktion=senden</span>. Sie wird hier <b>nicht zusammengebaut</b>: eine geratene Adresse für ein fremdes Plugin wäre eine Vermutung, eine abgeschriebene ist eine Angabe. <b>Belegt ist nicht erprobt:</b> dass die Adresse stimmt, ist abgelesen; ob ein laufender SignalBot die Meldung annimmt, wurde nie gemessen. Deshalb ist der Schalter ab Werk aus, und ein Fehlschlag hält den Wächter nicht an.",
   "The complete address including the SignalBot access word, without the text — that is appended. It is shown there in the <i>Loxone integration</i> tab, for example <span class='sm-mono'>http://loxberry/plugins/signalbot/index.php?token=xxx&amp;aktion=senden</span>. It is <b>not assembled</b> here: a guessed address for someone else's plugin would be an assumption, a copied one is a statement of fact. <b>Documented is not tested:</b> that the address is correct has been read off; whether a running SignalBot accepts the message has never been measured. That is why the switch is off by default, and a failure does not stop the watchdog."),
 ]),
 ("FW_ART", [
  ("KEINE", "— kein zweites Kriterium —", "— no second criterion —"),
  ("DATEI", "Datei (Änderungsdatum)", "File (modification time)"),
  ("MQTT", "MQTT (letzte Nachricht)", "MQTT (last message)"),
  ("HTTP", "HTTP (Adresse erreichbar)", "HTTP (address reachable)"),
  ("USB", "USB (Stick hängt am Bus)", "USB (stick present on the bus)"),
  ("SERIELL", "seriell (Gerätedatei vorhanden)", "serial (device node present)"),
  ("DIENST", "systemd-Dienst (läuft er)", "systemd service (is it running)"),
  ("DOCKER", "Docker (Container und Healthcheck)", "Docker (container and health check)"),
  ("BLUETOOTH", "Bluetooth (Adapter angemeldet)", "Bluetooth (adapter registered)"),
 ]),
 ("TAB", [
  ("NR", "Nr.", "No."),
  ("GERAET", "Stick", "Stick"),
  ("ZUSTAND", "Zustand", "State"),
  ("ALTER", "Stumm seit", "Silent for"),
  ("SEIT", "so seit %d s", "in this state for %d s"),
  ("STUFE", "Zuletzt versucht",
   "Last tried"),
  ("HEILUNGEN", "Geheilt", "Healed"),
  ("HEIL7T", "%d in sieben Tagen", "%d in seven days"),
  ("VERSUCHE", "Versuche", "Attempts"),
  ("ABGELEHNT", "davon %d abgelehnt", "%d of them refused"),
  ("LETZTE_TAT", "Zuletzt geschehen", "Last action"),
 ]),
 ("GRUND", [
  ("FRISCH", "meldet sich", "is reporting"),
  ("VERALTET", "schweigt zu lange", "silent for too long"),
  ("NIE_GESEHEN", "noch nie ein Lebenszeichen", "never seen a sign of life"),
  ("ZEITSPRUNG", "Zeitsprung der Systemuhr, nicht gewertet",
   "system clock jumped, not counted"),
  ("AUS", "wird nicht beobachtet", "not being watched"),
  ("ERHOLUNG", "erholt sich von einem Heilversuch",
   "recovering from a healing attempt"),
 ]),
 ("STUFE", [
  ("0", "nur melden", "report only"),
  ("1", "Dienst", "Service"),
  ("2", "USB lösen", "Release USB"),
  ("3", "Strom aus", "Power off"),
 ]),
 ("WARUM", [
  ("HEILEN_AUS", "Heilen ist für diesen Stick ausgeschaltet",
   "healing is switched off for this stick"),
  ("FREI", "es spricht nichts dagegen", "nothing speaks against it"),
  ("ABSTAND", "wartet den Mindestabstand zum letzten Versuch ab",
   "waiting for the minimum interval since the last attempt"),
  ("TAGESGRENZE", "die erlaubten Versuche für heute sind aufgebraucht",
   "the attempts allowed for today are used up"),
  ("KEINE_STUFE_MEHR",
   "es ist keine Stufe mehr übrig — entweder ist nichts hinterlegt, oder alle wurden schon versucht",
   "no level left — either nothing is configured, or all of them have been tried"),
  ("NIE_GESEHEN",
   "es kam noch nie ein Lebenszeichen — das ist fast immer ein Eintragungsfehler, und darauf wird nicht mit einem Neustart geantwortet",
   "no sign of life has ever arrived — that is almost always a configuration mistake, and a restart is not the answer to it"),
  ("ANLAUFZEIT",
   "das System ist gerade erst gestartet — in der Anlaufschonzeit wird nur gemeldet",
   "the system has just started — during the start-up grace period the watchdog only reports"),
  ("NACHTRUHE", "das Ruhefenster läuft", "the quiet window is active"),
  ("WARTUNG", "die Wartung läuft", "maintenance mode is active"),
  ("GLOBAL_AUS", "der Schalter „nur melden“ steht an",
   "the switch „report only“ is on"),
  ("DIENST_FEHLT",
   "der eingetragene Dienst ist auf diesem LoxBerry nicht vorhanden (nach dem Umstieg auf Zigbee2MqttNG: Dienst zigbee2mqttng eintragen) — gemeldet wird, geheilt nicht",
   "the configured service does not exist on this LoxBerry (after moving to Zigbee2MqttNG: enter the service zigbee2mqttng) — it is reported, not healed"),
 ]),
 ("AUFTR", [
  ("STICK", "Stick %d", "stick %d"),
  ("ALLE", "alle Sticks", "all sticks"),
  ("QUITTIERT",
   "Quittieren für %s ist vorgemerkt. Es wirkt beim nächsten Durchlauf des Wächters, also spätestens in %d Sekunden.",
   "Acknowledgement for %s has been queued. It takes effect at the watchdog's next pass, that is within %d seconds."),
  ("WARTUNG_EIN",
   "Wartung für %d Minuten ist vorgemerkt — sie wirkt spätestens in %d Sekunden und geht danach von selbst wieder aus.",
   "Maintenance for %d minutes has been queued — it takes effect within %d seconds and ends by itself afterwards."),
  ("WARTUNG_AUS", "Das Ende der Wartung ist vorgemerkt, es wirkt spätestens in %d Sekunden.",
   "The end of maintenance has been queued, it takes effect within %d seconds."),
  ("STATISTIK",
   "Das Zurücksetzen der Stufenstatistik ist vorgemerkt, es wirkt spätestens in %d Sekunden.",
   "Resetting the per-level statistics has been queued, it takes effect within %d seconds."),
  ("DAUER_FALSCH", "Die Wartungsdauer „%s“ ist keine ganze Zahl von 0 bis 1440 Minuten — es wurde nichts beauftragt.", "The maintenance duration „%s“ is not a whole number from 0 to 1440 minutes — nothing was requested."),
  ("FEHL",
   "Der Auftrag konnte nicht abgelegt werden. Bitte die Rechte am Ordner data/plugins prüfen.",
   "The request could not be stored. Please check the permissions of data/plugins."),
 ]),
 ("MQTT", [
  ("ERKLAERUNG",
   "Ist das MQTT-Gateway von LoxBerry eingeschaltet, meldet der Wächter bei jedem Durchlauf dorthin. Über MQTT gehen dieselben Werte hinaus wie über die Adresse für den Miniserver — nur das Alter fehlt, denn beim Senden wäre es immer null. An seiner Stelle kommt der Zeitstempel.",
   "If the LoxBerry MQTT gateway is switched on, the watchdog reports there on every run. MQTT carries the same values as the address for the Miniserver — only the age is missing, because on sending it would always be zero. The timestamp takes its place."),
  ("NICHT_GEFUNDEN",
   "Es wurde keine MQTT-Einstellung gefunden. Bitte das MQTT-Gateway unter „Dienste“ einrichten.",
   "No MQTT settings were found. Please set up the MQTT gateway under „Services“."),
  ("KEIN_AUTOSTART",
   "Das MQTT-Gateway ist eingerichtet, startet aber nicht von selbst mit. Solange es steht, kommt keine Nachricht an.",
   "The MQTT gateway is configured but does not start automatically. While it is down, no message arrives."),
  ("LAEUFT", "Das MQTT-Gateway ist eingerichtet und hört auf UDP-Anschluss %s.",
   "The MQTT gateway is configured and listens on UDP port %s."),
  ("EIN", "Werte an MQTT weitergeben", "Pass values on to MQTT"),
  ("THEMA", "Thema (Präfix)", "Topic (prefix)"),
  ("THEMA_HILFE",
   "Alle Nachrichten hängen unter diesem Präfix. Erlaubt sind Kleinbuchstaben, Ziffern, Bindestrich, Unterstrich und Schrägstrich — nicht am Anfang oder Ende. Leer wird nicht angenommen; ab Werk steht hier funkwacht.",
   "All messages hang below this prefix. Allowed are lower-case letters, digits, hyphen, underscore and slash — not at the start or end. Empty is not accepted; the default is funkwacht."),
  ("H_ABO", "Das Abonnement im Gateway", "The subscription in the gateway"),
  ("ABO_V1",
   "<b>Gateway Fassung 1:</b> Unter <i>Dienste → MQTT Gateway → Abonnements</i> muss <span class='sm-mono'>%s/#</span> eingetragen sein. <b>Ohne diesen Eintrag kommt am Miniserver nichts an</b> — das ist die häufigste Ursache dafür, dass ein Plugin sauber sendet und trotzdem nichts ankommt.",
   "<b>Gateway version 1:</b> Under <i>Services → MQTT Gateway → Subscriptions</i> the entry <span class='sm-mono'>%s/#</span> is required. <b>Without it nothing arrives at the Miniserver</b> — that is the most common reason why a plugin sends correctly and nothing shows up."),
  ("ABO_V2",
   "<b>MQTT-Gateway V2 erkennt die Themengruppe von selbst</b> — einzutragen ist hier nichts. In den <i>Abonnements</i> erscheint die Gruppe <span class='sm-mono'>%s/</span>; dort werden die gewünschten Datenpunkte einzeln angehakt.",
   "<b>MQTT gateway V2 detects the topic group by itself</b> — there is nothing to enter here. The group <span class='sm-mono'>%s/</span> appears under <i>Subscriptions</i>, where the desired data points are ticked individually."),
  # Die Fassung liess sich nicht lesen: dann stehen BEIDE Saetze da, und
  # dieser hier sagt, warum. Einen der beiden zu behaupten waere fuer die
  # Haelfte der Anlagen falsch.
  ("ABO_UNBEKANNT",
   "Die Fassung des Gateways ließ sich nicht lesen, deshalb stehen beide Fälle da. Welche gilt, steht unter <i>Dienste → MQTT Gateway</i>.",
   "The gateway version could not be read, so both cases are shown. Which one applies is shown under <i>Services → MQTT Gateway</i>."),
  ("H_MITHOERER", "Der Mithörer — für die Art „MQTT“",
   "The listener — for the kind „MQTT“"),
  ("MITHOERER_ERKLAERUNG",
   "Ein Stick auf der Art „MQTT“ gilt als lebendig, solange auf seinem Thema etwas ankommt. Dafür hört ein eigener kleiner Prozess am Broker mit und schreibt je Thema den Zeitpunkt der letzten Nachricht auf — den <b>Inhalt</b> wertet er nicht aus. Zurückbehaltene Nachrichten, die der Broker beim Abonnieren nachliefert, und leere Nachrichten zählen <b>nicht</b> als Lebenszeichen. Ein geändertes Thema abonniert er binnen weniger Sekunden selbst. Er läuft nur, wenn überhaupt ein Stick auf diese Art steht. Die Felder unten sind <b>leer richtig</b>: dann gelten die Zugangsdaten, die LoxBerry für seinen Broker führt. Nach einer Änderung muss der Wächter neu gestartet werden.",
   "A stick on the kind „MQTT“ counts as alive as long as something arrives on its topic. A small separate process listens at the broker and records the time of the last message per topic — it does not evaluate the <b>content</b>. Retained messages, which the broker delivers again on subscribing, and empty messages do <b>not</b> count as a sign of life. A changed topic is subscribed by itself within a few seconds. It only runs if at least one stick uses this kind. The fields below are <b>correct when empty</b>: the credentials LoxBerry keeps for its broker then apply. After a change the watchdog has to be restarted."),
  ("L_HOST", "Broker (Adresse und Anschluss)", "Broker (address and port)"),
  ("H_HOST", "Leer heißt: %s und Anschluss %d, so wie LoxBerry es führt.",
   "Empty means: %s and port %d, as LoxBerry has it."),
  ("L_USER", "Benutzername", "User name"),
  ("L_PASS", "Kennwort", "Password"),
  ("H_PASS",
   "Ein leeres Feld <b>löscht nichts</b> — sonst verlöre jedes Speichern das Kennwort, weil der Browser es nicht zurückschickt. Ist eines hinterlegt: %s",
   "An empty field <b>deletes nothing</b> — otherwise every save would lose the password, because the browser does not send it back. A password is stored: %s"),
  ("L_PASS_WEG", "Kennwort löschen", "Delete password"),
  ("L_ID", "Kennung am Broker", "Client identifier at the broker"),
  ("H_ID",
   "Leer heißt: eine Kennung mit der Prozessnummer. Eigene nur eintragen, wenn der Broker sie verlangt — zwei Verbindungen mit derselben Kennung werfen einander hinaus.",
   "Empty means: an identifier containing the process number. Only enter your own if the broker requires it — two connections with the same identifier throw each other out."),
  ("ALT_ABRAEUMEN", "Die zurückbehaltenen Themen der Funkwacht unter „%s/“ räumt der Wächter im nächsten Durchgang am Broker des MQTT-Gateways ab und liest nach.", "The watchdog clears the retained Funkwacht topics under „%s/“ at the broker of the MQTT gateway in its next run and reads back."),
  ("ALT_FEHL", "Das bisherige Präfix „%s“ ließ sich nicht zum Abräumen vormerken (data/plugins nicht beschreibbar) — die Themen darunter bleiben im Broker stehen.", "The previous prefix „%s“ could not be noted for clearing (data/plugins not writable) — the topics under it stay in the broker."),
  ("NEUSTART_NOETIG",
   "Damit der Mithörer die geänderten Angaben benutzt, muss der Wächter neu gestartet werden — der Knopf dafür steht im Reiter Einstellungen.",
   "For the listener to use the changed settings, the watchdog has to be restarted — the button for that is in the Settings tab."),
  ("H_THEMEN", "Diese Themen werden gesendet", "These topics are published"),
  ("SP_THEMA", "Thema", "Topic"),
  ("SP_BEDEUTUNG", "Bedeutung", "Meaning"),
  ("SP_RETAIN", "retained", "retained"),
  ("RETAIN_HILFE",
   "<b>retained</b> heißt: der Broker behält den letzten Wert, und Loxone hat ihn nach einem Neustart des Miniservers oder des Gateways sofort wieder. Zurückbehalten werden die <b>Einrichtung</b> (Zahl und Namen der Sticks) und der <b>Verlauf</b> (Summen, letzte Heilung). Nicht zurückbehalten werden die <b>Urteile des Wächters</b> — <span class='sm-mono'>ok</span>, <span class='sm-mono'>krank</span>, <span class='sm-mono'>alarm</span>, Grund, Stufe, Sperre —: stürbe der Wächter, stünde sonst „alle Sticks gesund“ für immer da. Ebenso wenig Werte, die von selbst veralten — eine Dauer in Sekunden, die Heilungen der letzten 24 Stunden oder 7 Tage —, Texte, die meist leer sind, und das Lebenszeichen <span class='sm-mono'>ts</span>: zurückbehalten sähe es immer frisch aus. Leert man eine Zeile im Reiter <i>Einstellungen</i>, löscht der Wächter die zurückbehaltenen Themen dieses Sticks im nächsten Durchgang am Broker; die Deinstallation löscht alle zurückbehaltenen Themen der Funkwacht.",
   "<b>retained</b> means: the broker keeps the last value, and Loxone has it again immediately after a restart of the Miniserver or the gateway. Retained are the <b>setup</b> (number and names of the sticks) and the <b>history</b> (totals, last heal). Not retained are the <b>verdicts of the watchdog</b> — <span class='sm-mono'>ok</span>, <span class='sm-mono'>krank</span>, <span class='sm-mono'>alarm</span>, reason, stage, lock —: if the watchdog died, „all sticks healthy“ would otherwise stay forever. Nor are values that age by themselves — a duration in seconds, the heals of the last 24 hours or 7 days —, texts that are usually empty, and the sign of life <span class='sm-mono'>ts</span>: retained it would always look fresh. If you empty a row in the <i>Settings</i> tab, the watchdog deletes the retained topics of that stick from the broker in its next pass; uninstalling deletes all retained Funkwacht topics."),
  ("GERAETN_HILFE",
   "Statt „geraetN“ steht dort die <b>Zeilennummer</b> des Sticks aus dem Reiter <i>Einstellungen</i>: die erste Zeile ist immer <span class='sm-mono'>geraet1</span>, die dritte immer <span class='sm-mono'>geraet3</span> — auch wenn Zeilen dazwischen leer sind. Das Gateway ersetzt in Themen nur den Schrägstrich und das Prozentzeichen durch einen Unterstrich; Punkte bleiben stehen.",
   "Instead of „geraetN“ the <b>row number</b> of the stick from the <i>Settings</i> tab appears: the first row is always <span class='sm-mono'>geraet1</span>, the third always <span class='sm-mono'>geraet3</span> — even if rows in between are empty. In topics the gateway only replaces the slash and the percent sign with an underscore; dots remain."),
 ]),
 ("FW_MQTT", [
  ("OK", "1, wenn alle beobachteten Sticks gesund sind",
   "1 if all watched sticks are healthy"),
  ("KRANK", "Anzahl der gerade gestörten Sticks", "number of currently faulty sticks"),
  ("GERAETE", "Anzahl der beobachteten Sticks", "number of watched sticks"),
  ("GEHEILT", "Heilbefehle ohne Fehler seit dem Einschalten, alle Sticks zusammen",
   "healing commands without error since start, all sticks together"),
  ("VERSUCHE", "Heilversuche insgesamt, auch die abgelehnten und fehlgeschlagenen",
   "recovery attempts in total, including refused and failed ones"),
  ("ALARM", "1, solange ein Stick gestört ist und in diesem Durchlauf kein Heilversuch läuft",
   "1 while a stick is faulty and no healing attempt runs in this pass"),
  ("GESPERRT", "1, solange eine Sperre das Heilen anhält (Ruhefenster, Wartung, Aus-Schalter)",
   "1 while a lock suspends healing (quiet window, maintenance, off switch)"),
  ("WARTUNG", "Sekunden, die die Wartung noch läuft; 0 heißt: keine",
   "seconds the maintenance mode still runs; 0 means none"),
  ("TS",
   "Zeitstempel des letzten Durchlaufs (Sekunden seit 1970). Das Alter rechnet Loxone daraus: (Loxone-Zeit + 1230768000) − TS",
   "timestamp of the last run (seconds since 1970). Loxone computes the age from it: (Loxone time + 1230768000) − TS"),
  ("G_OK", "1 gesund, 0 gestört", "1 healthy, 0 faulty"),
  ("G_STUFE", "zuletzt versuchte Stufe; 0 heißt: noch keine",
   "level tried last; 0 means: none yet"),
  ("G_ALTER", "Sekunden seit dem letzten Lebenszeichen; −1 heißt: noch nie eines",
   "seconds since the last sign of life; −1 means: never any"),
  ("G_HEILUNGEN", "Heilbefehle dieses Sticks ohne Fehler",
   "healing commands of this stick without error"),
  ("G_VERSUCHE", "Heilversuche dieses Sticks, auch die erfolglosen",
   "recovery attempts for this stick, including the unsuccessful ones"),
  ("G_ABGELEHNT",
   "Versuche, die das Plugin selbst abgelehnt hat (etwa auf einem Systemgerät)",
   "attempts the plugin refused itself (for example on a system device)"),
  ("G_HEIL24", "Heilversuche der letzten 24 Stunden, auch erfolglose",
   "healing attempts in the last 24 hours, unsuccessful ones included"),
  ("G_HEIL7T", "Heilversuche der letzten sieben Tage, auch erfolglose — die Verschleißkurve",
   "healing attempts in the last seven days, unsuccessful ones included — the wear curve"),
  ("G_SEIT", "Sekunden im jetzigen Zustand (gesund oder gestört)",
   "seconds in the current state (healthy or faulty)"),
  ("G_LETZTE", "Zeitstempel der letzten Heilung; 0 heißt: noch keine",
   "timestamp of the last recovery; 0 means: none yet"),
  ("G_NEUSTARTS",
   "wie oft der Dienst oder Container von selbst neu gestartet ist; −1 heißt: diese Art zählt das nicht",
   "how often the service or container has restarted by itself; −1 means: this kind does not count that"),
  ("G_GRUNDNR",
   "der Grund als Zahl: 0 meldet sich, 1 schweigt zu lange, 2 nie gesehen, 3 Zeitsprung, 4 aus, 5 Erholung",
   "the reason as a number: 0 reporting, 1 silent too long, 2 never seen, 3 clock jump, 4 off, 5 recovering"),
  ("G_WARUMNR",
   "warum nicht geheilt wird, als Zahl: 0 nichts spricht dagegen, 1 Heilen aus, 2 Abstand, 3 Tagesgrenze, 4 keine Stufe mehr, 5 nie gesehen, 6 Anlaufzeit, 7 Ruhefenster, 8 Wartung, 9 Aus-Schalter, 10 Dienst nicht vorhanden",
   "why no healing happens, as a number: 0 nothing speaks against it, 1 healing off, 2 interval, 3 daily limit, 4 no level left, 5 never seen, 6 start-up, 7 quiet window, 8 maintenance, 9 off switch, 10 service missing"),
  ("G_NAME", "Name des Sticks", "name of the stick"),
  ("G_GRUND", "Grund im Klartext", "reason in plain words"),
  ("G_WARUM", "Hinderungsgrund im Klartext; „-“ heißt: keiner", "reason against healing, in plain words; „-“ means: none"),
  ("G_LETZTE_TAT", "was zuletzt versucht wurde, im Klartext",
   "what was tried last, in plain words"),
  ("G_BEMERKUNG",
   "was die Messung nebenbei gesehen hat, etwa eine falsche USB-Kennung am Anschluss; „-“ heißt: nichts",
   "what the measurement noticed along the way, for example a wrong USB identifier at the port; „-“ means: nothing"),
 ]),
 ("LOX", [
  ("H", "Schritt für Schritt in Loxone", "Step by step in Loxone"),
  ("S1",
   "<b>1. Den Weg festlegen.</b> Zwei Wege stehen zur Wahl, und beide lassen sich gleichzeitig benutzen: über das <b>MQTT-Gateway</b> von LoxBerry oder über eine <b>Adresse</b>, die der Miniserver in festem Takt abfragt. MQTT ist der Regelweg — die Werte stehen dort ohne Zutun im Miniserver. Die Adresse ist der Weg für alle, die kein Gateway betreiben; sie liefert dieselben Zahlen.",
   "<b>1. Choose the route.</b> There are two, and both can be used at the same time: via the LoxBerry <b>MQTT gateway</b> or via an <b>address</b> the Miniserver polls at a fixed interval. MQTT is the standard route — the values appear in the Miniserver without further work. The address is the route for anyone not running a gateway; it delivers the same numbers."),
  ("S2_V1",
   "<b>2. Das Abonnement eintragen.</b> Unter <i>Dienste → MQTT Gateway → Abonnements</i> gehört <span class='sm-mono'>%s/#</span> hinein. <b>Ohne diesen Eintrag kommt am Miniserver nichts an.</b>",
   "<b>2. Enter the subscription.</b> Under <i>Services → MQTT Gateway → Subscriptions</i> add <span class='sm-mono'>%s/#</span>. <b>Without this entry nothing arrives at the Miniserver.</b>"),
  ("S2_V2",
   "<b>2. Das Abonnement — hier ist nichts zu tun.</b> MQTT-Gateway V2 erkennt die Themengruppe von selbst; die Gruppe <span class='sm-mono'>%s/</span> erscheint in den Abonnements, dort werden die Datenpunkte einzeln angehakt.",
   "<b>2. The subscription — nothing to do here.</b> MQTT gateway V2 detects the topic group by itself; the group <span class='sm-mono'>%s/</span> appears in the subscriptions, where the data points are ticked individually."),
  ("S3",
   "<b>3. Virtuelle Eingänge anlegen.</b> Entweder von Hand nach der Tabelle unten, oder in einem Zug über die Vorlagendatei weiter unten. Die Tabelle bleibt trotzdem stehen: sie sagt, was eingelesen wird.",
   "<b>3. Create virtual inputs.</b> Either by hand from the table below, or in one go with the template file further down. The table stays anyway: it says what is being imported."),
  ("H_ADRESSE", "Adressen", "Addresses"),
  ("ADRESSE_HILFE",
   "Diese Adressen antworten ohne Anmeldung, aber nur mit dem richtigen Wortzeichen. <b>Einen Heilbefehl gibt es bewusst nicht</b> — er wäre ein Hebel, mit dem sich der USB-Bus des LoxBerry von außen zurücksetzen ließe. Quittieren und Wartung sind etwas anderes: das eine <i>erlaubt</i> dem Wächter, wieder zu urteilen, das andere hält ihn an. Beide schalten am Gerät nichts.",
   "These addresses answer without a login, but only with the correct access word. <b>There is deliberately no healing command</b> — it would be a lever to reset the LoxBerry USB bus from outside. Acknowledging and maintenance are something else: one <i>allows</i> the watchdog to judge again, the other stops it. Neither switches anything on the device."),
  ("SP_ZWECK", "Zweck", "Purpose"),
  ("SP_ADRESSE", "Adresse", "Address"),
  ("Z_STATUS", "Alle Werte als Textzeilen (das liest die Vorlage)",
   "All values as text lines (this is what the template reads)"),
  ("Z_JSON", "Dasselbe als JSON, mit den Klartexten — für eigene Auswertungen",
   "The same as JSON, including the plain texts — for your own evaluations"),
  ("Z_QUITT", "Bremse und Eskalation zurücksetzen (wahlweise mit &nr=2 für einen Stick)",
   "Reset the brake and the escalation (optionally with &nr=2 for one stick)"),
  ("Z_WARTUNG", "Wartung für 60 Minuten; dauer=0 beendet sie, dieselbe Dauer binnen 60 s antwortet UNVERAENDERT=1",
   "Maintenance for 60 minutes; dauer=0 ends it, the same duration within 60 s answers UNVERAENDERT=1"),
  ("Z_SELFTEST", "Antwortet, OHNE etwas auszulösen — zum Prüfen der Kette",
   "Answers WITHOUT triggering anything — for testing the chain"),
  ("TOKEN_HINWEIS",
   "Das Wortzeichen steht in der Adresse und ist damit im Netzwerk sichtbar. Es schützt vor zufälligen Zugriffen, nicht vor einem Mithörer im selben Netz. Nach einem Wechsel muss die Vorlage neu eingelesen werden.",
   "The access word is part of the address and therefore visible on the network. It protects against accidental access, not against someone listening on the same network. After a change the template has to be imported again."),
  ("H_FELDER", "Die virtuellen Eingänge, einer je Zeile",
   "The virtual inputs, one per row"),
  ("FELDER_HILFE",
   "Die Titel stehen so, wie die Vorlage sie anlegt. <b>G&lt;n&gt;</b> ist die Zeilennummer des Sticks aus dem Reiter <i>Einstellungen</i>. Die Texte über MQTT (Name, Grund, zuletzt geschehen) stehen hier nicht: ein virtueller Eingang liest Zahlen. Wer sie braucht, holt sie über die JSON-Adresse.",
   "The titles are exactly the ones the template creates. <b>G&lt;n&gt;</b> is the row number of the stick from the <i>Settings</i> tab. The texts sent over MQTT (name, reason, last action) are not listed here: a virtual input reads numbers. If you need them, fetch them from the JSON address."),
  ("SP_TITEL", "Titel des Eingangs", "Title of the input"),
  ("SP_EINHEIT", "Einheit", "Unit"),
  ("SP_BEDEUTUNG", "Bedeutung", "Meaning"),
  ("KEINE_GERAETE",
   "Es ist noch kein Stick eingetragen. Die Vorlage enthielte nur die Summenwerte.",
   "No stick has been entered yet. The template would contain only the summary values."),
  ("H_BEFEHLE", "Befehle senden", "Sending commands"),
  ("BEFEHLE_TEXT",
   "Zwei Befehle kann Loxone schicken, und beide sind harmlos: <b>Quittieren</b> setzt Bremse und Eskalationsstand zurück — nützlich, wenn ein Stick auf „Tagesgrenze“ oder „keine Stufe mehr“ steht und jemand nachgesehen hat. <b>Wartung</b> hält das Heilen für eine Weile an und geht danach von selbst wieder aus. Beide gehen als Auftrag an den Wächter und wirken beim nächsten Durchlauf; die Antwort sagt, wie lange das höchstens dauert. <b>Einen Heilbefehl gibt es nicht</b> — siehe oben.",
   "Loxone can send two commands, and both are harmless: <b>acknowledge</b> resets the brake and the escalation state — useful when a stick sits at „daily limit“ or „no level left“ and somebody has looked at it. <b>Maintenance</b> suspends healing for a while and ends by itself afterwards. Both are queued as a request to the watchdog and take effect at its next pass; the answer says how long that takes at most. <b>There is no healing command</b> — see above."),
  ("H_ALLES", "Alles auf einmal anlegen", "Create everything at once"),
  ("ALLES_TEXT",
   "Der erste Knopf erzeugt die virtuellen Eingänge, der zweite die Steuerbefehle. In Loxone Config unter <b>Virtuelle Eingänge → Vorlage einlesen</b> beziehungsweise <b>Virtuelle Ausgänge → Vorlage einlesen</b> einspielen. Die Adresse samt Wortzeichen steckt bereits darin. <b>Loxone Config legt beim Einlesen neu an und überschreibt nichts — zweimal eingelesen heißt doppelte Objekte.</b> Nach jeder Änderung an den Sticks oder am Wortzeichen also erst die alten Objekte entfernen, dann neu einlesen. Die Adresse im Kopf ist ein Vorschlag: der Rechnername ist nicht zwingend der Name, unter dem der Miniserver den LoxBerry erreicht — bitte prüfen.",
   "The first button creates the virtual inputs, the second the control commands. Import them in Loxone Config under <b>Virtual inputs → Import template</b> and <b>Virtual outputs → Import template</b> respectively. The address including the access word is already inside. <b>Loxone Config creates new objects on import and overwrites nothing — importing twice means duplicate objects.</b> So after every change to the sticks or the access word, remove the old objects first, then import again. The address in the header is a suggestion: the host name is not necessarily the name under which the Miniserver reaches the LoxBerry — please check."),
  ("K_VI", "Vorlage für Loxone Config erzeugen", "Create template for Loxone Config"),
  ("K_VQ", "Vorlage der Steuerbefehle erzeugen", "Create template of the control commands"),
  ("FEHLER_VORLAGE", "Die Vorlage konnte nicht erzeugt werden.",
   "The template could not be created."),
  ("VO_QUITTIEREN", "Bremse und Eskalation für alle Sticks zurücksetzen",
   "Reset the brake and the escalation for all sticks"),
  ("VO_QUITT_EINZELN", "Bremse und Eskalation für %s zurücksetzen",
   "Reset the brake and the escalation for %s"),
  ("VO_WARTUNG", "Wartung: EIN hält das Heilen 60 Minuten an, AUS beendet sie sofort",
   "Maintenance: ON suspends healing for 60 minutes, OFF ends it immediately"),
  ("H_AUSFALL", "Ausfallerkennung", "Detecting an outage"),
  ("AUSFALL_TEXT", "<b>Virtuelle Eingänge behalten in Loxone ihren letzten Wert.</b> Fällt der Wächter aus, sieht in der App alles normal aus — die Werte stehen nur still. Zwei Größen verraten es: <span class='sm-mono'>FW_ALTER</span> steigt (das rechnet die Adresse im Augenblick der Frage), und über MQTT bleibt <span class='sm-mono'>ts</span> stehen. Beides gehört ausgewertet, siehe die Bausteine 4 und 19 der Seite „Funkwacht“ unten. <b>Die Schwelle deutlich über den Abholtakt legen</b> — das Fünffache des Prüftakts, mindestens 300 Sekunden.",
   "<b>Virtual inputs keep their last value in Loxone.</b> If the watchdog fails, everything looks normal in the app — the values simply stand still. Two things give it away: <span class='sm-mono'>FW_ALTER</span> rises (the address computes it at the moment of the request), and over MQTT <span class='sm-mono'>ts</span> stops moving. Both belong in the logic, see blocks 4 and 19 of the page “Funkwacht” below. <b>Set the threshold well above the polling interval</b> — five times the check interval, at least 300 seconds."),
  ("H_BAUSTEINE", "Die Bausteine, einer je Zeile", "The blocks, one per row"),
  ("BS_SP_NR", "#",
   "#"),
  ("BS_SP_TYP", "Baustein (Typ)",
   "Block (type)"),
  ("BS_SP_NAME", "Name (Vorschlag)",
   "Name (suggestion)"),
  ("BS_SP_PARAM", "Parameter",
   "Parameters"),
  ("BS_SP_EING", "Eingänge verbinden mit",
   "Connect inputs to"),
  ("BS_H_ZEIT", "<b>Loxone-Zeitrechnung:</b> Loxone zählt Sekunden seit dem 01.01.2009. Wer über MQTT mit <span class='sm-mono'>ts</span> rechnet: Alter = (Loxone-Zeit + 1230768000) − ts. Alle Bausteine findet Loxone Config über die Baustein-Suche mit <b>F5</b>.",
   "<b>Loxone time:</b> Loxone counts seconds since 01/01/2009. If you work with <span class='sm-mono'>ts</span> over MQTT: age = (Loxone time + 1230768000) − ts. All blocks can be found in Loxone Config through the block search with <b>F5</b>."),
  ("H_GEGENPROBE", "Gegenprobe", "Cross-check"),
  ("GEGENPROBE_TEXT",
   "In Loxone Config die Live-Ansicht öffnen: <span class='sm-mono'>FW_ALTER</span> muss im Prüftakt zurückfallen und darf nicht davonlaufen. <span class='sm-mono'>FW_GERAETE</span> muss die Zahl der eingetragenen Sticks zeigen. Bleibt ein Wert auf 0 stehen, stimmt die Adresse oder das Wortzeichen nicht — nicht der Baustein. Der Reiter <i>Test</i> beantwortet dieselbe Frage von hier aus, ohne Umweg über Loxone.",
   "Open the live view in Loxone Config: <span class='sm-mono'>FW_ALTER</span> must fall back at every check interval and must not run away. <span class='sm-mono'>FW_GERAETE</span> must show the number of configured sticks. If a value stays at 0, the address or the access word is wrong — not the block. The <i>Test</i> tab answers the same question from here, without the detour through Loxone."),
  ("H_TOKEN", "Das Wortzeichen wechseln", "Change the access word"),
  ("TOKEN_TEXT",
   "Ein neues Wortzeichen macht die alte Adresse ungültig. <b>Alle virtuellen Eingänge im Miniserver bekommen danach HTTP 403</b>, bis die Vorlagen neu eingelesen oder die Adressen von Hand berichtigt wurden. Nur wechseln, wenn das Wortzeichen in fremde Hände geraten sein könnte.",
   "A new access word invalidates the old address. <b>All virtual inputs in the Miniserver will then get HTTP 403</b> until the templates have been imported again or the addresses corrected by hand. Only change it if the access word might have fallen into the wrong hands."),
  ("TOKEN_NICHT",
   "Was dabei <b>nicht</b> geschieht: Einstellungen, Zähler und Verlauf bleiben unangetastet, der Wächter misst weiter, und am Funkstick ändert sich nichts. Ungültig werden nur die Adressen — und die stehen nach dem Neueinlesen der beiden Vorlagen wieder richtig da.",
   "What does <b>not</b> happen: settings, counters and history remain untouched, the watchdog keeps measuring, and nothing changes at the radio stick. Only the addresses become invalid — and they are correct again once both templates have been imported."),
  ("SICHER", "Ja, die Adressen dürfen ungültig werden",
   "Yes, the addresses may become invalid"),
  ("K_TOKEN_NEU", "Neues Wortzeichen", "New access word"),
  ("TOKEN_NEU_OK",
   "Es gilt ein neues Wortzeichen. Bitte beide Vorlagen neu herunterladen und in Loxone Config einlesen — die alten Adressen antworten nicht mehr.",
   "A new access word is in effect. Please download both templates again and import them into Loxone Config — the old addresses no longer answer."),
  # Welle Bild (Entscheidung 45): Bild der Bausteine aus dem gemeinsamen Musterprojekt
  ("BILD_ALT", "Bausteine des Plugins in Loxone Config",
   "Plugin blocks in Loxone Config"),
  ("BILD_UNTERSCHRIFT", "Seite „%s“ im LoxBerry-Plugins Musterprojekt. Config kürzt lange Bausteinnamen – Namen siehe Tabelle.",
   "Page “%s” in the LoxBerry plugins sample project. Config shortens long block names – see the table for the full names."),
  ("MUSTERPROJEKT", "Die ganze Projektdatei mit allen Plugin-Seiten und Vorlagen: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry-Plugins Musterprojekt</a>",
   "The complete project file with all plugin pages and templates: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry plugins sample project</a>"),
  # Welle Bild 15 (Funkwacht 1.0.15, 17.10.2026; Entwurf Welle 15 fw, E12): drei Seiten aus dem LoxBerry-
  # Plugins Musterprojekt - Vortext, Kasten- und Hinweistitel, Ueberschriften, Kaesten BSn_Sm, Hinweise
  # BSn_Hm, Tabellenzeilen Zn_mm = "Typ | Name | Parameter | Eingaenge" (fw_bausteinliste()).
  ("BAUSTEINE_VORTEXT", "Drei Seiten aus dem LoxBerry-Plugins Musterprojekt, dort in Loxone Config gebaut und verbunden; wer nur überwachen will, übernimmt die erste allein. Die Tabellen nennen den ersten eingetragenen Stick so, wie die Vorlage ihn liefert. Ohne eingetragenen Stick steht das Beispiel des Musterprojekts: Zeile 1, Name Zigbee, eingesetzt mit „%s“.",
   "Three pages from the LoxBerry plugins sample project, built and connected there in Loxone Config; if you only want monitoring, take over the first one alone. The tables name the first stick entered as the template delivers it. Without a stick entered they show the example of the sample project: row 1, name Zigbee, inserted with “%s”."),
  ("SCHRITTE_TITEL", "So übernehmen Sie diese Seite",
   "How to take over this page"),
  ("HINWEISE_TITEL", "Hinweise",
   "Notes"),
  ("BS1_H", "Funkwacht – läuft der Wächter, ist ein Stick gestört?",
   "Funkwacht – is the watchdog running, is a stick faulty?"),
  ("BS2_H", "Funkwacht Sticks – ein Stick im Einzelnen",
   "Funkwacht Sticks – one stick in detail"),
  ("BS3_H", "Funkwacht Steuerung – quittieren und Wartung aus Loxone",
   "Funkwacht Steuerung – acknowledge and maintenance from Loxone"),
  ("BS1_S1", "Im Plugin Reiter „%s“ unter „%s“ eine Zeile für Ihren Stick einsetzen, Namen geben, speichern; „%s“. Reiter „%s“ → „%s“: dort steht GERAETE=1 – dann trägt die Kette.",
   "In the plugin tab “%s” under “%s” insert a row for your stick, give it a name, save; “%s”. Tab “%s” → “%s”: it shows GERAETE=1 – then the chain works."),
  ("BS1_S2", "Reiter „%s“ → „%s“. In Loxone Config: Peripherie → Virtuelle Eingänge → Vorlage importieren. Nur EINMAL einlesen (zweimal ergibt doppelte Bausteine). Kommt später ein Stick dazu: dessen 13 Befehle von Hand am vorhandenen Eingang anlegen (Suchtext wie in der Tabelle der virtuellen Eingänge oben) oder den alten Eingang löschen und neu einlesen – dann sind die Leitungen weg.",
   "Tab “%s” → “%s”. In Loxone Config: Periphery → Virtual Inputs → Import template. Import only ONCE (twice gives duplicate blocks). If a stick is added later: create its 13 commands by hand on the existing input (search text as in the table of virtual inputs above) or delete the old input and import again – then the connections are gone."),
  ("BS1_S3", "Seite „Funkwacht“ anlegen. Aus „Funkwacht“ die zehn Befehle FW_OK … FW_VERSUCHE ziehen, dazu die Konstante 1. Bei FW_GEHEILT im Eigenschaftsfenster „Statistik“ einschalten.",
   "Create the page “Funkwacht”. Drag the ten commands FW_OK … FW_VERSUCHE from “Funkwacht”, plus the constant 1. For FW_GEHEILT switch on “Statistics” in the properties window."),
  ("BS1_S4", "Benachrichtigung „Meldung Funkwacht“ anlegen (Peripherie → Mitteilungen → Benachrichtigung), Text wie in der Liste, auf die Seite ziehen. Sie bekommt genau eine Leitung (von Nr. 21).",
   "Create the notification “Meldung Funkwacht” (Periphery → Messages → Notification), text as in the list, drag it onto the page. It gets exactly one connection (from no. 21)."),
  ("BS1_S5", "Die übrigen Bausteine über die Baustein-Suche (Taste F5) setzen, Parameter wie in der Liste, von oben nach unten verbinden. An der Analogwertvalidierung (Nr. 19) den Haken bei „En“ im Eigenschaftsfenster entfernen. Status „Funkwacht Zustand“: vorher viermal „+“ klicken (V5–V8). Jedes ODER hat zwei Eingänge. Die Zeilen der Status-Bausteine und den Mitteilungstext von Hand eintragen, in der angegebenen Reihenfolge, die Zeile ohne Bedingung zuletzt.",
   "Place the remaining blocks via the block search (key F5), parameters as in the list, connect from top to bottom. On the Value Validator (no. 19) remove the tick at “En” in the properties window. Status “Funkwacht Zustand”: click “+” four times first (V5–V8). Each OR has two inputs. Enter the rows of the status blocks and the message text by hand, in the given order, the row without condition last."),
  ("BS1_S6", "Speichern und übertragen. Probe: FW_TS ändert sich jede Minute; „Funkwacht Zustand“ zeigt „alle 1 Sticks gesund …“.",
   "Save and transfer. Check: FW_TS changes every minute; “Funkwacht Zustand” shows “alle 1 Sticks gesund …”."),
  ("BS1_H1", "Die Meldung kommt erst nach 5 Minuten Störung: einen Stick, den der Wächter schnell heilt, meldet Loxone nicht. Das Plugin selbst meldet jeden Wechsel zusätzlich im LoxBerry-Benachrichtigungszentrum (ab Werk an).",
   "The message only comes after 5 minutes of fault: a stick the watchdog heals quickly is not reported by Loxone. The plugin itself additionally reports every change in the LoxBerry notification centre (on by default)."),
  ("BS1_H2", "Zu Nr. 2 und 4: der zweite Eingang der Vergleicher bleibt frei – er gilt als 0. Von und Voff wie angegeben eintragen; mit der Werkseinstellung 5/1 meldet ein einzelner gestörter Stick nie, und „Wächter selbst tot“ schaltet grundlos.",
   "On no. 2 and 4: the second input of the comparators stays free – it counts as 0. Enter Von and Voff as given; with the factory setting 5/1 a single faulty stick never reports, and “Wächter selbst tot” switches for no reason."),
  ("BS1_H3", "Zu Nr. 5: FW_ALARM geht direkt an das ODER. Der Ausgang eines Status-Bausteins ist der Wert der zutreffenden Zeile, kein Ein/Aus – „Funkwacht Alarm“ (Nr. 3) ist nur Anzeige.",
   "On no. 5: FW_ALARM goes straight to the OR. The output of a status block is the value of the matching row, not on/off – “Funkwacht Alarm” (no. 3) is a display only."),
  ("BS1_H4", "Zu Nr. 19 bis 21: ein Virtueller Eingang behält seinen letzten Wert, wenn der LoxBerry steht. FW_TS ändert sich jede Minute; die Analogwertvalidierung meldet, wenn es fünf Minuten steht – erst über ODER und Verzögerung zur Meldung.",
   "On no. 19 to 21: a virtual input keeps its last value when the LoxBerry stands still. FW_TS changes every minute; the Value Validator reports when it has stood for five minutes – only via OR and delay to the message."),
  ("BS1_H5", "Die Benachrichtigung sendet nur beim Wechsel von Aus auf Ein und bekommt genau eine Quelle; alle Störungen laufen vorher über die ODER zusammen.",
   "The notification only sends on the change from off to on and gets exactly one source; all faults are combined beforehand via the ORs."),
  ("BS1_H6", "Wer den Prüftakt im Plugin ändert, setzt Tmc (Nr. 19), Von (Nr. 4) und die Verzögerung (Nr. 21) auf das Fünffache.",
   "If you change the check interval in the plugin, set Tmc (no. 19), Von (no. 4) and the delay (no. 21) to five times its value."),
  ("BS1_H7", "Nach „%s“ (Reiter „%s“) die Adresse am Virtuellen Eingang und am Virtuellen Ausgang erneuern.",
   "After “%s” (tab “%s”) renew the address on the virtual input and on the virtual output."),
  ("BS2_S1", "Seite „Funkwacht“ zuerst. Die Vorlage aus „%s“ enthält je Stick 13 Befehle FW_<NAME>_…; die Tabelle unten nennt die des ersten eingetragenen Sticks.",
   "Page “Funkwacht” first. The template from “%s” contains 13 commands FW_<NAME>_… per stick; the table below names those of the first stick entered."),
  ("BS2_S2", "Neue Seite „Funkwacht Sticks“. Die 13 Befehle FW_ZIGBEE_… ziehen (bei FW_ZIGBEE_HEILUNGEN im Eigenschaftsfenster „Statistik“ einschalten).",
   "New page “Funkwacht Sticks”. Drag the 13 commands FW_ZIGBEE_… (for FW_ZIGBEE_HEILUNGEN switch on “Statistics” in the properties window)."),
  ("BS2_S3", "Zwei Virtuelle Texteingänge anlegen (Peripherie → Virtuelle Eingänge → Virtueller Texteingang), Namen genau funkwacht_geraet1_letzte_tat und funkwacht_geraet1_bemerkung, je „In Visualisierung verwenden“ an. Sie füllen sich nur, wenn im Plugin Reiter MQTT „%s“ an ist und das MQTT-Gateway läuft; beim Gateway Fassung 1 das Abonnement aus Schritt 2 oben eintragen, bei V2 nichts.",
   "Create two virtual text inputs (Periphery → Virtual Inputs → Virtual text input), names exactly funkwacht_geraet1_letzte_tat and funkwacht_geraet1_bemerkung, each with “Use in User Interface” on. They only fill when “%s” is on in the plugin tab MQTT and the MQTT gateway is running; with gateway version 1 enter the subscription from step 2 above, with V2 nothing."),
  ("BS2_S4", "Benachrichtigung „Funkstick braucht Pflege“ anlegen (Peripherie → Mitteilungen → Benachrichtigung), Text wie in der Liste.",
   "Create the notification “Funkstick braucht Pflege” (Periphery → Messages → Notification), text as in the list."),
  ("BS2_S5", "Die übrigen Bausteine über die Baustein-Suche (Taste F5) setzen, verbinden wie in der Liste. An beiden Analogspeichern „Rem“ eingeschaltet lassen. Beide Status: vorher je viermal „+“ klicken (V5–V8). Jedes ODER hat zwei Eingänge; Statuszeilen und Mitteilungstext von Hand eintragen.",
   "Place the remaining blocks via the block search (key F5), connect as in the list. Leave “Rem” switched on at both analog memories. Both status blocks: click “+” four times first (V5–V8). Each OR has two inputs; enter the status rows and the message text by hand."),
  ("BS2_S6", "Speichern und übertragen. Probe: „Zigbee-Stick“ zeigt „meldet sich (vor … s)“; im Plugin Reiter „%s“ „%s“ – das Alter passt.",
   "Save and transfer. Check: “Zigbee-Stick” shows “meldet sich (vor … s)”; in the plugin tab “%s” “%s” – the age matches."),
  ("BS2_H1", "Jeder weitere Stick bekommt dieselbe Seite noch einmal mit seinen Namen (FW_<NAME>_… und Texteingänge mit seiner Zeilennummer).",
   "Every further stick gets the same page once more with its names (FW_<NAME>_… and text inputs with its row number)."),
  ("BS2_H2", "Dienst-Neustarts zählt die Funkwacht nur bei der Art „systemd-Dienst“ oder „Docker“. Für Zigbee2MqttNG im Plugin als „%s“ „%s“ mit zigbee2mqttng wählen, „%s“ UND – sonst bleibt „Zigbee-Dienst flattert“ immer aus.",
   "Funkwacht only counts service restarts with the kind “systemd service” or “Docker”. For Zigbee2MqttNG choose “%s” “%s” with zigbee2mqttng in the plugin, “%s” AND – otherwise “Zigbee-Dienst flattert” always stays off."),
  ("BS2_H3", "Fehlversuche und Neustarts zählen je Tag (Impuls um 0:00 und Analogspeicher); so geht die Meldung nach einem schlechten Tag wieder aus.",
   "Failed attempts and restarts count per day (pulse at 0:00 and analog memory); that way the message goes off again after a bad day."),
  ("BS2_H4", "Die Uhrzeit der letzten Heilung im Status ist der Zeitpunkt, zu dem Loxone die Änderung sah (bis zu 60 s später).",
   "The time of the last healing in the status is the moment Loxone saw the change (up to 60 s later)."),
  ("BS2_H5", "„Zigbee-Stick verschleißt“: steigt die Zahl über Wochen, ist ein Stick am Ende, lange bevor er ganz ausfällt.",
   "“Zigbee-Stick verschleißt”: if the number rises over weeks, a stick is at its end long before it fails completely."),
  ("BS3_S1", "Reiter „%s“ → „%s“. In Loxone Config: Peripherie → Virtuelle Ausgänge → Vorlage importieren. Nur EINMAL einlesen; kommt ein Stick dazu, dessen Befehl FW_QUITT_<NAME> von Hand anlegen.",
   "Tab “%s” → “%s”. In Loxone Config: Periphery → Virtual Outputs → Import template. Import only ONCE; if a stick is added, create its command FW_QUITT_<NAME> by hand."),
  ("BS3_S2", "Drei Virtuelle Eingänge anlegen: „Funkwacht quittieren“ und „Zigbee-Stick quittieren“ als Taste, „Funkwacht Wartung“ als Schalter, je „In Visualisierung verwenden“ an.",
   "Create three virtual inputs: “Funkwacht quittieren” and “Zigbee-Stick quittieren” as push button, “Funkwacht Wartung” as switch, each with “Use in User Interface” on."),
  ("BS3_S3", "Neue Seite „Funkwacht Steuerung“, die drei Befehle und die drei Eingänge darauf, verbinden wie in der Liste.",
   "New page “Funkwacht Steuerung”, put the three commands and the three inputs on it, connect as in the list."),
  ("BS3_S4", "Speichern und übertragen. Probe: „Funkwacht Wartung“ ein – nach höchstens einer Minute zeigt „Funkwacht Zustand“ „Wartung läuft noch … s“.",
   "Save and transfer. Check: “Funkwacht Wartung” on – after one minute at the most “Funkwacht Zustand” shows “Wartung läuft noch … s”."),
  ("BS3_H1", "Die Wartung braucht einen Schalter, keine Taste: eine Taste schickte beim Loslassen sofort „Wartung beenden“.",
   "Maintenance needs a switch, not a push button: a push button would send “end maintenance” immediately on release."),
  ("BS3_H2", "Quittieren heilt nichts; es erlaubt dem Wächter nur, wieder selbst zu urteilen. Einen Heilbefehl aus Loxone gibt es bewusst nicht.",
   "Acknowledging heals nothing; it only allows the watchdog to judge again by itself. There is deliberately no healing command from Loxone."),
  ("Z1_01", "Status | Funkwacht Zustand | Zeilen: V4 = 0 „noch keine Messung – im Plugin Reiter Einstellungen ‚Wächter starten‘; der erste Durchlauf kommt nach spätestens einer Minute“; V3 >= 300 „der Wächter steht seit <v3> s – im Plugin Reiter Einstellungen ‚Wächter neu starten‘; den Grund zeigt der Reiter Logdateien unter ‚Ausgabe beim Start‘“; V2 = 1 „LoxBerry antwortet nicht – alle Funkwacht-Werte sind eingefroren; LoxBerry im Browser öffnen, läuft er, im Plugin Reiter Test ‚Endpunkt aufrufen‘“; V6 = 0 „Wächter läuft, aber es ist noch kein Stick eingetragen – im Plugin Reiter Einstellungen unter ‚Fertige Zeilen für die bekannten Fälle‘ eine Zeile einsetzen“; V1 = 0 „<v5> von <v6> Sticks gestört – Status ‚Zigbee-Stick‘ lesen; im Plugin Reiter Test ‚Letzte Messung ansehen‘“; V8 > 0 „alle <v6> Sticks gesund – Wartung läuft noch <v8> s, solange wird nicht geheilt“; V7 = 1 „alle <v6> Sticks gesund – Heilen gerade gesperrt (Ruhefenster oder ‚Nur melden, nichts heilen‘)“; ohne Bedingung „alle <v6> Sticks gesund, letzte Prüfung vor <v3> s“; Visualisierung EIN | V1 = FW_OK, V2 = Ausgang E von #19, V3 = #11, V4 = #15, V5 = #9, V6 = #12, V7 = #13, V8 = #14",
   "Status | Funkwacht Zustand | rows: V4 = 0 “no measurement yet – in the plugin tab Settings ‘Start watchdog’; the first run comes after one minute at the latest”; V3 >= 300 “the watchdog has been standing for <v3> s – in the plugin tab Settings ‘Restart watchdog’; the tab Log files shows the reason under ‘Output at start’”; V2 = 1 “LoxBerry does not answer – all Funkwacht values are frozen; open the LoxBerry in the browser, if it runs, in the plugin tab Test ‘Call the endpoint’”; V6 = 0 “watchdog running, but no stick entered yet – in the plugin tab Settings under ‘Ready-made rows for the common cases’ insert a row”; V1 = 0 “<v5> of <v6> sticks faulty – read the status ‘Zigbee-Stick’; in the plugin tab Test ‘View the last measurement’”; V8 > 0 “all <v6> sticks healthy – maintenance still running for <v8> s, no healing until then”; V7 = 1 “all <v6> sticks healthy – healing currently blocked (quiet window or ‘Report only, heal nothing’)”; without condition “all <v6> sticks healthy, last check <v3> s ago”; visualisation ON | V1 = FW_OK, V2 = output E of #19, V3 = #11, V4 = #15, V5 = #9, V6 = #12, V7 = #13, V8 = #14"),
  ("Z1_02", "Analogkomparator | Ein Stick gestört | Von 0,5 / Voff 0,2 (zweiter Eingang offen = 0; Ein ab dem ersten gestörten Stick) | I1 = FW_KRANK",
   "Comparator | Ein Stick gestört | Von 0.5 / Voff 0.2 (second input open = 0; on from the first faulty stick) | I1 = FW_KRANK"),
  ("Z1_03", "Status | Funkwacht Alarm | Zeilen: V1 = 1 „Alarm – ein Stick ist gestört und wird gerade nicht geheilt; den Grund nennt der Status ‚Zigbee-Stick‘“; ohne Bedingung „kein Alarm – <v3> Heilversuche, davon <v2> ohne Fehler ausgeführt“; Visualisierung EIN | V1 = FW_ALARM, V2 = #16, V3 = #17",
   "Status | Funkwacht Alarm | rows: V1 = 1 “alarm – a stick is faulty and is not being healed right now; the status ‘Zigbee-Stick’ names the reason”; without condition “no alarm – <v3> healing attempts, <v2> of them carried out without error”; visualisation ON | V1 = FW_ALARM, V2 = #16, V3 = #17"),
  ("Z1_04", "Analogkomparator | Wächter selbst tot | Von 300 / Voff 120 (Sekunden seit der letzten Prüfung, fünfmal der Prüftakt von 60 s; zweiter Eingang offen = 0) | I1 = FW_ALTER",
   "Comparator | Wächter selbst tot | Von 300 / Voff 120 (seconds since the last check, five times the check interval of 60 s; second input open = 0) | I1 = FW_ALTER"),
  ("Z1_05", "ODER | Stick gestört oder Alarm | – | I1 = Ausgang Q von #2, I2 = FW_ALARM",
   "OR | Stick gestört oder Alarm | – | I1 = output Q of #2, I2 = FW_ALARM"),
  ("Z1_06", "ODER | Sammelstörung Funkwacht | – | I1 = #5, I2 = Ausgang Q von #4",
   "OR | Sammelstörung Funkwacht | – | I1 = #5, I2 = output Q of #4"),
  ("Z1_07", "Benachrichtigung | Meldung Funkwacht | Text: Funkwacht – ein Funkstick ist seit 5 Minuten gestört, der Wächter steht oder der LoxBerry antwortet nicht. In der App den Status ‚Funkwacht Zustand‘ lesen | Ausgang der einzigen Quelle (#21)",
   "Notification | Meldung Funkwacht | Text: Funkwacht – a radio stick has been faulty for 5 minutes, the watchdog is standing or the LoxBerry does not answer. Read the status ‘Funkwacht Zustand’ in the app | output of the only source (#21)"),
  ("Z1_08", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_OK | 1 = alle beobachteten Sticks gesund | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_OK | 1 = all watched sticks healthy | —"),
  ("Z1_09", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_KRANK | Zahl der gestörten Sticks | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_KRANK | number of faulty sticks | —"),
  ("Z1_10", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_ALARM | 1 = ein Stick ist gestört und wird in diesem Durchlauf nicht geheilt | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_ALARM | 1 = a stick is faulty and is not healed in this run | —"),
  ("Z1_11", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_ALTER | Sekunden seit der letzten Prüfung des Wächters | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_ALTER | seconds since the last check of the watchdog | —"),
  ("Z1_12", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_GERAETE | Zahl der beobachteten Sticks | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_GERAETE | number of watched sticks | —"),
  ("Z1_13", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_GESPERRT | 1 = Heilen gerade gesperrt (Ruhefenster, Wartung oder „Nur melden“) | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_GESPERRT | 1 = healing currently blocked (quiet window, maintenance or “report only”) | —"),
  ("Z1_14", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_WARTUNG | Sekunden, die die Wartung noch läuft; 0 = keine | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_WARTUNG | seconds the maintenance is still running; 0 = none | —"),
  ("Z1_15", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_TS | Zeit des letzten Durchlaufs (Sekunden seit 1970); ändert sich jede Minute – das Lebenszeichen von Wächter und LoxBerry | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_TS | time of the last run (seconds since 1970); changes every minute – the sign of life of watchdog and LoxBerry | —"),
  ("Z1_16", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_GEHEILT | Heilversuche, die ohne Fehler liefen, alle Sticks zusammen; Statistik ein | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_GEHEILT | healing attempts that ran without error, all sticks together; statistics on | —"),
  ("Z1_17", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_VERSUCHE | Heilversuche insgesamt, auch abgelehnte und fehlgeschlagene | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_VERSUCHE | healing attempts in total, including refused and failed ones | —"),
  ("Z1_18", "Konstante | Konstante 1 | Wert 1 | —",
   "Constant | Konstante 1 | value 1 | —"),
  ("Z1_19", "Analogwertvalidierung | Funkwacht-Werte eingefroren | Tmc 300 s (fünfmal die Abfragezeit von 60 s), Min 1, Max 2147483647; Haken bei „En“ im Eigenschaftsfenster entfernen | V = #15, En = #18",
   "Value Validator | Funkwacht-Werte eingefroren | Tmc 300 s (five times the polling interval of 60 s), Min 1, Max 2147483647; remove the tick at ‘En’ in the properties window | V = #15, En = #18"),
  ("Z1_20", "ODER | Funkwacht gestört gesamt | — (Sticks, Wächter oder LoxBerry stumm) | I1 = #6, I2 = Ausgang E von #19",
   "OR | Funkwacht gestört gesamt | — (sticks, watchdog or LoxBerry silent) | I1 = #6, I2 = output E of #19"),
  ("Z1_21", "Einschaltverzögerung | Funkwacht-Störung bestätigt | 300 s (ein Stick, den der Wächter binnen 5 Minuten heilt, meldet nicht; fängt auch den kurzen Impuls der Vergleicher bei jeder Abfrage ab) | Eingang = #20",
   "Switch-On Delay | Funkwacht-Störung bestätigt | 300 s (a stick that the watchdog heals within 5 minutes does not report; also absorbs the short pulse of the comparators at every poll) | Input = #20"),
  ("Z2_01", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_ZIGBEE_OK | 1 = der Stick „Zigbee“ meldet sich, 0 = gestört | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_ZIGBEE_OK | 1 = the stick “Zigbee” reports, 0 = faulty | —"),
  ("Z2_02", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_ZIGBEE_GRUNDNR | Befund als Zahl: 0 meldet sich, 1 schweigt zu lange, 2 noch nie ein Lebenszeichen, 3 Zeitsprung der Systemuhr, 4 wird nicht beobachtet, 5 erholt sich von einem Heilversuch | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_ZIGBEE_GRUNDNR | finding as a number: 0 reports, 1 silent too long, 2 never a sign of life, 3 jump of the system clock, 4 not watched, 5 recovering from a healing attempt | —"),
  ("Z2_03", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_ZIGBEE_WARUMNR | warum nicht geheilt wird: 0 nichts dagegen, 1 Heilen aus, 2 Mindestabstand, 3 Tagesgrenze, 4 keine Stufe mehr, 5 nie gesehen, 6 Anlaufschonzeit, 7 Ruhefenster, 8 Wartung, 9 „Nur melden“, 10 Dienst nicht vorhanden | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_ZIGBEE_WARUMNR | why it is not healed: 0 nothing against it, 1 healing off, 2 minimum interval, 3 daily limit, 4 no level left, 5 never seen, 6 start-up grace period, 7 quiet window, 8 maintenance, 9 “report only”, 10 service not present | —"),
  ("Z2_04", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_ZIGBEE_ALTER | Sekunden seit dem letzten Lebenszeichen; -1 = noch nie | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_ZIGBEE_ALTER | seconds since the last sign of life; -1 = never | —"),
  ("Z2_05", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_ZIGBEE_SEIT | Sekunden im jetzigen Zustand (gesund oder gestört) | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_ZIGBEE_SEIT | seconds in the current state (healthy or faulty) | —"),
  ("Z2_06", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_ZIGBEE_STUFE | zuletzt versuchte Heilstufe: 0 noch keine, 1 Dienst neu starten, 2 USB lösen, 3 Strom aus | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_ZIGBEE_STUFE | last healing level tried: 0 none yet, 1 restart service, 2 release USB, 3 power off | —"),
  ("Z2_07", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_ZIGBEE_HEIL7T | Heilversuche der letzten 7 Tage, auch erfolglose – die Verschleißkurve | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_ZIGBEE_HEIL7T | healing attempts of the last 7 days, unsuccessful ones included – the wear curve | —"),
  ("Z2_08", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_ZIGBEE_LETZTE | Zeitpunkt der letzten Heilung (Sekunden seit 1970), 0 = noch keine | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_ZIGBEE_LETZTE | time of the last healing (seconds since 1970), 0 = none yet | —"),
  ("Z2_09", "Status | Zigbee-Stick | Zeilen: V2 = 4 „wird nicht beobachtet – im Plugin Reiter Einstellungen den Haken ‚beobachten‘ setzen“; V2 = 2 „noch nie ein Lebenszeichen – meist ein Eintragungsfehler: im Plugin Reiter Test ‚Jetzt messen‘ neben der Zeile; es wird nicht geheilt“; V1 = 0 und V3 = 10 „gestört seit <v5> s – der eingetragene Dienst fehlt auf dem LoxBerry; im Plugin Reiter Einstellungen den Dienst zigbee2mqttng eintragen“; V1 = 0 und V3 = 4 „gestört seit <v5> s – alle Heilstufen sind versucht: Stick abziehen und wieder einstecken, dann ‚Zigbee-Stick quittieren‘“; V1 = 0 und V3 = 3 „gestört seit <v5> s – die Versuche für heute sind aufgebraucht; nachsehen, dann ‚Zigbee-Stick quittieren‘“; V1 = 0 und V3 = 1 „gestört seit <v5> s, stumm seit <v4> s – Heilen ist für diesen Stick aus, es wird nur gemeldet“; V1 = 0 und V3 = 8 „gestört seit <v5> s – Wartung läuft, es wird nicht geheilt“; V1 = 0 und V3 = 9 „gestört seit <v5> s – im Plugin steht ‚Nur melden, nichts heilen‘“; V1 = 0 und V3 = 7 „gestört seit <v5> s – Ruhefenster, geheilt wird danach“; V1 = 0 und V3 = 6 „gestört seit <v5> s – der LoxBerry ist gerade erst gestartet, geheilt wird nach der Anlaufschonzeit“; V1 = 0 und V3 = 2 „gestört seit <v5> s – wartet den Mindestabstand zum letzten Heilversuch ab (zuletzt Stufe <v6>)“; V1 = 0 „gestört seit <v5> s, stumm seit <v4> s – Heilversuch mit Stufe <v6> läuft“; V2 = 5 „erholt sich von einem Heilversuch – Stille ist jetzt erwartet“; V2 = 3 „Zeitsprung der Systemuhr – diese Messung zählt nicht“; V8 > 0 „meldet sich (vor <v4> s) – <v7> Heilversuche in 7 Tagen, letzte Heilung <v8.t>“; ohne Bedingung „meldet sich (vor <v4> s) – noch nie geheilt“; Visualisierung EIN | V1 = #1, V2 = #2, V3 = #3, V4 = #4, V5 = #5, V6 = #6, V7 = #7, V8 = #8",
   "Status | Zigbee-Stick | rows: V2 = 4 “not watched – in the plugin tab Settings set the tick ‘watch’”; V2 = 2 “never a sign of life – usually an entry error: in the plugin tab Test ‘Measure now’ next to the row; it is not healed”; V1 = 0 and V3 = 10 “faulty for <v5> s – the configured service is missing on the LoxBerry; in the plugin tab Settings enter the service zigbee2mqttng”; V1 = 0 and V3 = 4 “faulty for <v5> s – all healing levels have been tried: unplug the stick and plug it in again, then ‘Zigbee-Stick quittieren’”; V1 = 0 and V3 = 3 “faulty for <v5> s – today’s attempts are used up; check, then ‘Zigbee-Stick quittieren’”; V1 = 0 and V3 = 1 “faulty for <v5> s, silent for <v4> s – healing is off for this stick, it is only reported”; V1 = 0 and V3 = 8 “faulty for <v5> s – maintenance running, no healing”; V1 = 0 and V3 = 9 “faulty for <v5> s – the plugin is set to ‘Report only, heal nothing’”; V1 = 0 and V3 = 7 “faulty for <v5> s – quiet window, healing afterwards”; V1 = 0 and V3 = 6 “faulty for <v5> s – the LoxBerry has only just started, healing after the start-up grace period”; V1 = 0 and V3 = 2 “faulty for <v5> s – waiting for the minimum interval to the last healing attempt (last level <v6>)”; V1 = 0 “faulty for <v5> s, silent for <v4> s – healing attempt with level <v6> running”; V2 = 5 “recovering from a healing attempt – silence is expected now”; V2 = 3 “jump of the system clock – this measurement does not count”; V8 > 0 “reports (<v4> s ago) – <v7> healing attempts in 7 days, last healing <v8.t>”; without condition “reports (<v4> s ago) – never healed”; visualisation ON | V1 = #1, V2 = #2, V3 = #3, V4 = #4, V5 = #5, V6 = #6, V7 = #7, V8 = #8"),
  ("Z2_10", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_ZIGBEE_HEIL24 | Heilversuche der letzten 24 Stunden, auch erfolglose | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_ZIGBEE_HEIL24 | healing attempts of the last 24 hours, unsuccessful ones included | —"),
  ("Z2_11", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_ZIGBEE_HEILUNGEN | Heilbefehle, die ohne Fehler liefen, seit der Einrichtung; Statistik ein | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_ZIGBEE_HEILUNGEN | healing commands that ran without error, since setup; statistics on | —"),
  ("Z2_12", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_ZIGBEE_VERSUCHE | Heilversuche seit der Einrichtung, auch die erfolglosen | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_ZIGBEE_VERSUCHE | healing attempts since setup, including the unsuccessful ones | —"),
  ("Z2_13", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_ZIGBEE_ABGELEHNT | Versuche, die das Plugin selbst abgelehnt hat (Systemgerät, Verteiler) | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_ZIGBEE_ABGELEHNT | attempts the plugin refused itself (system device, hub) | —"),
  ("Z2_14", "Virtueller HTTP-Eingang (Vorlage „Funkwacht“) | FW_ZIGBEE_NEUSTARTS | wie oft der Dienst von selbst neu gestartet ist; -1 = diese Art zählt das nicht | —",
   "Virtual HTTP input (template “Funkwacht”) | FW_ZIGBEE_NEUSTARTS | how often the service restarted by itself; -1 = this kind does not count that | —"),
  ("Z2_15", "Schwellwertschalter | Zigbee-Stick verschleißt | Ein 4 / Aus 2 (Heilversuche in 7 Tagen) | V = #7",
   "Threshold Switch | Zigbee-Stick verschleißt | On 4 / Off 2 (healing attempts in 7 days) | V = #7"),
  ("Z2_16", "Impuls um | Tagesbeginn 0:00 | Zu bestimmter Uhrzeit, 00:00:00 | —",
   "Pulse at | Tagesbeginn 0:00 | At specific time, 00:00:00 | —"),
  ("Z2_17", "Formel | Zigbee Fehlversuche gesamt | I1-I2 (Heilversuche minus fehlerfrei ausgeführte) | I1 = #12, I2 = #11",
   "Formula | Zigbee Fehlversuche gesamt | I1-I2 (healing attempts minus those carried out without error) | I1 = #12, I2 = #11"),
  ("Z2_18", "Analogspeicher | Zigbee Fehlversuche bis heute früh | übernimmt um 0:00 den Stand; Remanenz an (Rem), damit ein Neustart des Miniservers den Tagesstand nicht löscht | V = #17, Set = Ausgang Q von #16",
   "Analog Memory | Zigbee Fehlversuche bis heute früh | takes over the value at 0:00; remanence on (Rem), so that a restart of the Miniserver does not clear the daily value | V = #17, Set = output Q of #16"),
  ("Z2_19", "Formel | Zigbee Fehlversuche heute | IF(I1>=I2;I1-I2;I1) – Stand minus Stand um Mitternacht | I1 = #17, I2 = #18",
   "Formula | Zigbee Fehlversuche heute | IF(I1>=I2;I1-I2;I1) – value minus value at midnight | I1 = #17, I2 = #18"),
  ("Z2_20", "Schwellwertschalter | Zigbee Heilbefehle scheitern | Ein 2 / Aus 1 (gescheiterte Heilbefehle heute) | V = #19",
   "Threshold Switch | Zigbee Heilbefehle scheitern | On 2 / Off 1 (failed healing commands today) | V = #19"),
  ("Z2_21", "Analogspeicher | Zigbee Neustarts bis heute früh | übernimmt um 0:00 den Stand; Remanenz an (Rem) | V = #14, Set = Ausgang Q von #16",
   "Analog Memory | Zigbee Neustarts bis heute früh | takes over the value at 0:00; remanence on (Rem) | V = #14, Set = output Q of #16"),
  ("Z2_22", "Formel | Zigbee Neustarts heute | IF(I1<0;0;IF(I1>=I2;I1-I2;I1)) – -1 (Art zählt nicht) ergibt 0 | I1 = #14, I2 = #21",
   "Formula | Zigbee Neustarts heute | IF(I1<0;0;IF(I1>=I2;I1-I2;I1)) – -1 (kind does not count) gives 0 | I1 = #14, I2 = #21"),
  ("Z2_23", "Schwellwertschalter | Zigbee-Dienst flattert | Ein 6 / Aus 2 (Neustarts heute) | V = #22",
   "Threshold Switch | Zigbee-Dienst flattert | On 6 / Off 2 (restarts today) | V = #22"),
  ("Z2_24", "ODER | Verschleiß oder Befehle scheitern | – | I1 = #15, I2 = #20",
   "OR | Verschleiß oder Befehle scheitern | – | I1 = #15, I2 = #20"),
  ("Z2_25", "ODER | Zigbee-Stick braucht Pflege | – | I1 = #24, I2 = #23",
   "OR | Zigbee-Stick braucht Pflege | – | I1 = #24, I2 = #23"),
  ("Z2_26", "Einschaltverzögerung | Pflegebedarf bestätigt | 5 s (fängt den kurzen Impuls der Schwellwertschalter bei jeder Abfrage ab) | Eingang = #25",
   "Switch-On Delay | Pflegebedarf bestätigt | 5 s (absorbs the short pulse of the threshold switches at every poll) | Input = #25"),
  ("Z2_27", "Benachrichtigung | Funkstick braucht Pflege | Text: Funkwacht – der Stick „Zigbee“ lässt nach: viele Heilversuche in 7 Tagen, gescheiterte Heilbefehle oder ein flatternder Dienst. In der App den Status ‚Zigbee-Stick Pflege‘ lesen | Ausgang der einzigen Quelle (#26)",
   "Notification | Funkstick braucht Pflege | Text: Funkwacht – the stick “Zigbee” is weakening: many healing attempts in 7 days, failed healing commands or a flapping service. Read the status ‘Zigbee-Stick Pflege’ in the app | output of the only source (#26)"),
  ("Z2_28", "Status | Zigbee-Stick Pflege | Zeilen: V2 >= 2 „heute <v2> Heilbefehle gescheitert – meist fehlen Rechte: im Plugin Reiter Test ‚Selbstprüfung‘“; V3 >= 6 „der Dienst ist heute <v3>-mal von selbst neu gestartet – er flattert; im Plugin Reiter Test ‚Protokoll des Dienstes‘ lesen“; V1 >= 4 „<v1> Heilversuche in 7 Tagen (<v5> in 24 Stunden) – der Stick lässt nach: USB-Verlängerung und Anschluss prüfen oder den Stick ersetzen“; V8 < 0 „<v1> Heilversuche in 7 Tagen, <v6> von <v7> Heilversuchen ohne Fehler, <v4> abgelehnt; Neustarts zählt diese Art nicht“; ohne Bedingung „<v1> Heilversuche in 7 Tagen, <v6> von <v7> Heilversuchen ohne Fehler, <v4> abgelehnt, <v3> Dienst-Neustarts heute“; Visualisierung EIN | V1 = #7, V2 = #19, V3 = #22, V4 = #13, V5 = #10, V6 = #11, V7 = #12, V8 = #14",
   "Status | Zigbee-Stick Pflege | rows: V2 >= 2 “today <v2> healing commands failed – usually permissions are missing: in the plugin tab Test ‘Self-check’”; V3 >= 6 “the service restarted by itself <v3> times today – it is flapping; in the plugin tab Test read ‘Log of the service’”; V1 >= 4 “<v1> healing attempts in 7 days (<v5> in 24 hours) – the stick is weakening: check the USB extension and the connection or replace the stick”; V8 < 0 “<v1> healing attempts in 7 days, <v6> of <v7> healing attempts without error, <v4> refused; this kind does not count restarts”; without condition “<v1> healing attempts in 7 days, <v6> of <v7> healing attempts without error, <v4> refused, <v3> service restarts today”; visualisation ON | V1 = #7, V2 = #19, V3 = #22, V4 = #13, V5 = #10, V6 = #11, V7 = #12, V8 = #14"),
  ("Z2_29", "Virtueller Texteingang | funkwacht_geraet1_letzte_tat | von Hand anlegen, Name genau so (Name, den das MQTT-Gateway vergibt), „In Visualisierung verwenden“ an; was zuletzt versucht wurde, z. B. „dienst: … – gelungen“ | —",
   "Virtual text input | funkwacht_geraet1_letzte_tat | create by hand, name exactly like this (the name the MQTT gateway gives), “Use in User Interface” on; what was tried last, e.g. “dienst: … – gelungen” | —"),
  ("Z2_30", "Virtueller Texteingang | funkwacht_geraet1_bemerkung | von Hand anlegen, Name genau so; was die Messung nebenbei gesehen hat, etwa eine falsche USB-Kennung am Anschluss; „-“ = nichts; „In Visualisierung verwenden“ an | —",
   "Virtual text input | funkwacht_geraet1_bemerkung | create by hand, name exactly like this; what the measurement noticed on the side, such as a wrong USB identifier at the port; “-” = nothing; “Use in User Interface” on | —"),
  ("Z3_01", "Virtueller Eingang (Taste) | Funkwacht quittieren | in der App; nach dem Nachsehen: Bremse und Eskalation aller Sticks zurücksetzen, der Wächter darf wieder heilen | —",
   "Virtual input (push button) | Funkwacht quittieren | in the app; after checking: reset brake and escalation of all sticks, the watchdog may heal again | —"),
  ("Z3_02", "Virtueller Ausgang Befehl (Vorlage „Funkwacht Steuerbefehle“) | FW_QUITTIEREN | Bremse und Eskalation für alle Sticks zurücksetzen; wirkt beim nächsten Durchlauf (höchstens 60 s) | Eingang = #1",
   "Virtual output command (template “Funkwacht Steuerbefehle”) | FW_QUITTIEREN | reset brake and escalation for all sticks; takes effect at the next run (at most 60 s) | Input = #1"),
  ("Z3_03", "Virtueller Eingang (Schalter) | Funkwacht Wartung | in der App; Ein = 60 Minuten nicht heilen (z. B. beim Umstecken), Aus = Wartung sofort beenden; nach 60 Minuten endet sie von selbst – danach den Schalter ausschalten | —",
   "Virtual input (switch) | Funkwacht Wartung | in the app; on = no healing for 60 minutes (e.g. while re-plugging), off = end maintenance immediately; after 60 minutes it ends by itself – then switch the switch off | —"),
  ("Z3_04", "Virtueller Ausgang Befehl (Vorlage „Funkwacht Steuerbefehle“) | FW_WARTUNG_EIN | Ein: Wartung 60 Minuten; Aus: Wartung beenden | Eingang = #3",
   "Virtual output command (template “Funkwacht Steuerbefehle”) | FW_WARTUNG_EIN | on: maintenance 60 minutes; off: end maintenance | Input = #3"),
  ("Z3_05", "Virtueller Eingang (Taste) | Zigbee-Stick quittieren | in der App; nur den Stick „Zigbee“ zurücksetzen | —",
   "Virtual input (push button) | Zigbee-Stick quittieren | in the app; reset only the stick “Zigbee” | —"),
  ("Z3_06", "Virtueller Ausgang Befehl (Vorlage „Funkwacht Steuerbefehle“) | FW_QUITT_ZIGBEE | Bremse und Eskalation für den Stick „Zigbee“ zurücksetzen | Eingang = #5",
   "Virtual output command (template “Funkwacht Steuerbefehle”) | FW_QUITT_ZIGBEE | reset brake and escalation for the stick “Zigbee” | Input = #5"),
 ]),
 ("FW_FELD", [
  ("OK", "1 gesund, 0 gestört", "1 healthy, 0 faulty"),
  ("STUFE", "zuletzt versuchte Stufe; 0 heißt: noch keine",
   "level tried last; 0 means: none yet"),
  ("G_ALTER", "Sekunden seit dem letzten Lebenszeichen; −1 heißt: noch nie eines",
   "seconds since the last sign of life; −1 means: never any"),
  ("HEILUNGEN", "Heilbefehle ohne Fehler",
   "healing commands without error"),
  ("VERSUCHE", "Heilversuche, auch die erfolglosen",
   "recovery attempts, including the unsuccessful ones"),
  ("ABGELEHNT", "Versuche, die das Plugin selbst abgelehnt hat",
   "attempts the plugin refused itself"),
  ("HEIL24", "Heilversuche der letzten 24 Stunden, auch erfolglose",
   "healing attempts in the last 24 hours, unsuccessful ones included"),
  ("HEIL7T", "Heilversuche der letzten sieben Tage, auch erfolglose — die Verschleißkurve",
   "healing attempts in the last seven days, unsuccessful ones included — the wear curve"),
  ("SEIT", "Sekunden im jetzigen Zustand", "seconds in the current state"),
  ("LETZTE", "Zeitstempel der letzten Heilung; 0 heißt: noch keine",
   "timestamp of the last recovery; 0 means: none yet"),
  ("NEUSTARTS", "Neustarts des Dienstes oder Containers; −1 heißt: wird hier nicht gezählt",
   "restarts of the service or container; −1 means: not counted for this kind"),
  ("GRUNDNR", "der Grund als Zahl (siehe Reiter MQTT)",
   "the reason as a number (see the MQTT tab)"),
  ("WARUMNR", "warum nicht geheilt wird, als Zahl (siehe Reiter MQTT)",
   "why no healing happens, as a number (see the MQTT tab)"),
  ("SUM_OK", "1, wenn alle Sticks gesund sind", "1 if all sticks are healthy"),
  ("SUM_KRANK", "Anzahl der gestörten Sticks", "number of faulty sticks"),
  ("SUM_GERAETE", "Anzahl der beobachteten Sticks", "number of watched sticks"),
  ("SUM_GEHEILT", "Heilbefehle ohne Fehler, alle Sticks",
   "healing commands without error, all sticks"),
  ("SUM_VERSUCHE", "Heilversuche insgesamt", "recovery attempts in total"),
  ("SUM_ALARM", "1, solange ein Stick gestört ist und in diesem Durchlauf kein Heilversuch läuft",
   "1 while a stick is faulty and no healing attempt runs in this pass"),
  ("SUM_GESPERRT", "1, solange eine Sperre das Heilen anhält",
   "1 while a lock suspends healing"),
  ("SUM_WARTUNG", "Sekunden, die die Wartung noch läuft",
   "seconds the maintenance mode still runs"),
  ("SUM_TS", "Zeitstempel des letzten Durchlaufs (Sekunden seit 1970)",
   "timestamp of the last run (seconds since 1970)"),
  ("SUM_ALTER", "Sekunden seit der letzten Prüfung", "seconds since the last check"),
 ]),
 ("FW_XML", [
  ("KOPF",
   "Funkwacht — erzeugt am %s. Nach jeder Änderung an den Sticks oder am Wortzeichen neu einlesen; Loxone Config legt dabei neu an und überschreibt nichts.",
   "Funkwacht — created on %s. Import again after every change to the sticks or the access word; Loxone Config creates new objects and overwrites nothing."),
  ("KOPF_VO",
   "Funkwacht Steuerbefehle — erzeugt am %s. Sie quittieren und schalten die Wartung; einen Heilbefehl gibt es bewusst nicht.",
   "Funkwacht control commands — created on %s. They acknowledge and switch maintenance; there is deliberately no healing command."),
 ]),
 ("SICH", [
  ("H", "Einstellungen sichern und zurückspielen", "Back up and restore the settings"),
  ("ERKLAERUNG",
   "Die Sicherung enthält <b>alle</b> Einstellungen — einschließlich Wortzeichen und Broker-Kennwort. Das ist Absicht: eine Sicherung ohne Wortzeichen wäre nach dem Zurückspielen wertlos, weil alle Adressen im Miniserver ungültig würden. Wer die Datei weitergibt, gibt beides mit. Beim Zurückspielen wird abgewiesen, was nicht passt — nichts wird zurechtgebogen.",
   "The backup contains <b>all</b> settings — including the access word and the broker password. That is intentional: a backup without the access word would be worthless after restoring, because all addresses in the Miniserver would become invalid. Anyone who passes the file on passes both on. On restoring, whatever does not fit is rejected — nothing is bent into shape."),
  ("K_SICHERN", "Einstellungen herunterladen", "Download the settings"),
  ("SICHER", "Ja, die jetzigen Einstellungen überschreiben",
   "Yes, overwrite the current settings"),
  ("K_ZURUECK", "Datei zurückspielen", "Restore from file"),
  ("KEINE_DATEI", "Es wurde keine Datei ausgewählt.", "No file was selected."),
  ("LEER", "Die Datei ist leer.", "The file is empty."),
  ("ZU_GROSS", "Die Datei ist größer als ein Megabyte — das ist keine Sicherung dieses Plugins.",
   "The file is larger than one megabyte — that is not a backup of this plugin."),
  ("KEIN_JSON", "Die Datei ist kein lesbares JSON: %s",
   "The file is not readable JSON: %s"),
  ("KEIN_FUNKWACHT",
   "In der Datei fehlt die Liste der Sticks. Das sieht nicht nach einer Sicherung der Funkwacht aus.",
   "The list of sticks is missing from the file. This does not look like a Funkwacht backup."),
  ("ZEILE_KAPUTT", "Zeile %d in der Datei ist keine Stick-Beschreibung.",
   "Row %d in the file is not a stick description."),
  ("OK", "Zurückgespielt: %d Sticks.",
   "Restored: %d sticks."),
  ("ABGEWIESEN", "Die Sicherung wurde abgewiesen — es wurde nichts geändert:", "The backup was rejected — nothing was changed:"),
  ("FREMD", "%s gehört nicht zu den Einstellungen der Funkwacht.", "%s does not belong to the Funkwacht settings."),
  ("FEHLT", "In der Datei fehlen diese Schlüssel: %s.", "These keys are missing in the file: %s."),
  ("SCHLUESSEL", "Schlüssel „%s“", "key „%s“"),
  ("ZEILE_FELD", "Stick %d, Feld „%s“", "stick %d, field „%s“"),
  ("ZEILE_FEHLT", "Stick %d: In der Datei fehlen die Felder %s.", "Stick %d: the fields %s are missing in the file."),
  ("W_ZAHL", "%s: keine ganze Zahl.", "%s: not a whole number."),
  ("W_BEREICH", "%s: liegt außerhalb von %d bis %d.", "%s: outside %d to %d."),
  ("W_HAKEN", "%s: erwartet wird 0 oder 1.", "%s: 0 or 1 expected."),
  ("W_AUSWAHL", "%s: erwartet wird einer dieser Werte: %s.", "%s: one of these values expected: %s."),
  ("W_TEXT", "%s: erwartet wird ein Text.", "%s: a text is expected."),
  ("W_ZEICHEN", "%s: enthält Steuerzeichen, Anführungszeichen oder Leerraum am Rand — das nimmt auch das Formular nicht an.", "%s: contains control characters, quotation marks or surrounding white space — the form does not accept that either."),
  ("W_LISTE", "%s: erwartet wird eine Liste von Stick-Zeilen.", "%s: a list of stick rows is expected."),
  ("W_ZU_VIELE", "%s: mehr als %d Zeilen führt diese Oberfläche nicht.", "%s: this interface keeps no more than %d rows."),
  ("W_TOKEN", "%s: kein Wortzeichen in der Form, die dieses Plugin erzeugt (24 Zeichen aus Kleinbuchstaben und Ziffern).", "%s: not an access word of the form this plugin creates (24 characters, lower-case letters and digits)."),
  ("W_THEMA", "%s: kein brauchbares MQTT-Thema. Erlaubt sind Kleinbuchstaben, Ziffern, Bindestrich, Unterstrich und Schrägstrich, nicht am Rand.", "%s: not a usable MQTT topic. Allowed are lower-case letters, digits, hyphen, underscore and slash, not at the edges."),
  ("W_UHRZEIT", "%s: erwartet wird HH:MM oder ein leerer Text.", "%s: HH:MM or an empty text expected."),
  ("W_ADRESSE", "%s: erwartet wird eine Adresse, die mit http:// oder https:// beginnt, oder ein leerer Text.", "%s: an address starting with http:// or https://, or an empty text, is expected."),
  ("W_PORT", "%s: erwartet wird eine Zahl zwischen 1 und 65535 oder ein leerer Text.", "%s: a number between 1 and 65535, or an empty text, is expected."),
  ("W_KENNWORT", "%s: enthält Steuerzeichen.", "%s: contains control characters."),
  ("SELBST_WARN", "Diese Sicherung ließe sich so nicht zurückspielen. Der Knopf liefert sie trotzdem (mit _warnung im Kopf) — besser vorher richtigstellen:", "This backup could not be restored as it is. The button delivers it anyway (with _warnung in the header) — better correct this first:"),
  ("DIENST_NEU", "Der Wächter lief und wurde mit den zurückgespielten Einstellungen neu gestartet (jetzt Prozessnummer %d).", "The watchdog was running and has been restarted with the restored settings (now process number %d)."),
  ("DIENST_LIEF_NICHT", "Der Wächter lief nicht und wurde nicht gestartet. Er übernimmt die Einstellungen, sobald er anläuft — der Minutentakt startet ihn von selbst.", "The watchdog was not running and has not been started. It picks up the settings as soon as it starts — the minute timer starts it by itself."),
  ("DIENST_FEHL", "Die Einstellungen sind zurückgespielt, aber der Neustart des Wächters ist gescheitert: %s", "The settings are restored, but restarting the watchdog failed: %s"),
  ("FEHL", "Die Sicherung konnte nicht erzeugt werden.",
   "The backup could not be created."),
 ]),
 ("TEST", [
  ("H", "Nachsehen, was wirklich geht", "See what really works"),
  ("ERKLAERUNG",
   "Die grünen und grauen Schaltflächen fragen ab und rechnen — geheilt wird dort nichts. Der erste Knopf beantwortet in einer Liste, ob die Einrichtung trägt; der zweite sagt, was jetzt geschähe, ohne es zu tun. Unten gibt es einen eigenen Abschnitt mit Knöpfen, die <b>wirklich schalten</b>.",
   "The green and grey buttons query and compute — nothing is healed there. The first button answers in a list whether the setup holds; the second says what would happen now, without doing it. Further down there is a separate section with buttons that <b>really act</b>."),
  ("K_SELBSTPRUEFUNG", "Selbstprüfung", "Self-check"),
  ("K_TROCKEN", "Was würde jetzt geschehen?", "What would happen now?"),
  ("K_FAEHIGKEIT", "Was kann dieses Gerät?", "What can this device do?"),
  ("K_MESSEN", "Letzte Messung ansehen", "View the last measurement"),
  ("K_USB", "USB-Geräte auflisten", "List USB devices"),
  ("K_DIENSTE", "Dienste vorschlagen", "Suggest services"),
  ("K_CONTAINER", "Container auflisten", "List containers"),
  ("K_SELBSTTEST", "Rechenkerne prüfen", "Check the decision cores"),
  ("K_ZEILE", "Antwortzeile ansehen", "View the reply line"),
  ("K_MQTT", "MQTT prüfen", "Check MQTT"),
  ("K_MQTTPROBE", "Zehn Sekunden am Broker zuhören", "Listen at the broker for ten seconds"),
  ("K_ENDPUNKT", "Endpunkt aufrufen", "Call the endpoint"),
  ("K_MESSEN1", "Jetzt messen", "Measure now"),
  ("K_JOURNAL", "Protokoll des Dienstes", "Log of the service"),
  ("K_HEILEN", "%s jetzt heilen", "Heal %s now"),
  ("K_QUITTIEREN", "Bremse für alle zurücksetzen", "Reset the brake for all"),
  ("K_WARTUNG_EIN", "Wartung für 60 Minuten", "Maintenance for 60 minutes"),
  ("K_WARTUNG_AUS", "Wartung beenden", "End maintenance"),
  ("SICHER_STATISTIK", "Ja, die gezählten Erfolge dürfen weg",
   "Yes, the counted successes may be discarded"),
  ("K_STATISTIK_WEG", "Stufenstatistik zurücksetzen", "Reset the per-level statistics"),
  ("H_JE_STICK", "Je Stick", "Per stick"),
  ("JE_STICK_TEXT",
   "„Jetzt messen“ misst genau diese eine Zeile und zeigt das Ergebnis sofort — ohne Speichern, ohne Warten, ohne einen anderen Reiter. „Protokoll des Dienstes“ holt die letzten Zeilen aus dem Journal des Dienstes oder Containers, den dieser Stick neu starten würde: warum er gestorben ist, steht dort und nicht im Protokoll der Funkwacht.",
   "„Measure now“ measures exactly this one row and shows the result immediately — no saving, no waiting, no other tab. „Log of the service“ fetches the last lines from the journal of the service or container this stick would restart: why it died is written there and not in the Funkwacht log."),
  ("SP_MESSEN", "Messen", "Measure"),
  ("SP_JOURNAL", "Protokoll", "Log"),
  ("H_SCHALTEN", "Schalten", "Switching"),
  ("SCHALTEN_TEXT",
   "<b>Diese Knöpfe wirken sofort auf das Gerät.</b> Ein Heilversuch startet wirklich einen Dienst neu, löst wirklich einen USB-Anschluss oder nimmt wirklich den Strom — mit allem, was daran hängt. Der Versuch zählt <b>nicht</b> in die Stufenstatistik: er kam von Hand und nicht aus einem gemessenen Ausfall. Ohne Auswahl wird die Stufe genommen, die als nächste dran wäre. Nach dem Versuch wird noch einmal gemessen und das Ergebnis gezeigt.",
   "<b>These buttons act on the device immediately.</b> A healing attempt really restarts a service, really releases a USB port or really cuts the power — with everything that depends on it. The attempt does <b>not</b> count towards the per-level statistics: it came by hand and not from a measured outage. Without a selection the level that would be next is used. After the attempt a new measurement is taken and the result shown."),
  ("STUFE_NAECHSTE", "die nächste Stufe", "the next level"),
  ("H_UNGUELTIG", "Diese Angabe ist keine gültige Stick-Nummer.",
   "This is not a valid stick number."),
  ("M_UNBEKANNT", "Diesen Test gibt es nicht.", "There is no such test."),
  ("M_KEIN_DIENST",
   "Die Datei funkwacht_dienst.py wurde nicht gefunden. Bitte das Plugin neu installieren.",
   "The file funkwacht_dienst.py was not found. Please reinstall the plugin."),
  ("M_KEIN_MITHOERER",
   "Die Datei fw_mqtt.py wurde nicht gefunden. Bitte das Plugin neu installieren.",
   "The file fw_mqtt.py was not found. Please reinstall the plugin."),
  ("M_KEINE_GERAETE", "Es ist noch kein Stick eingetragen.",
   "No stick has been entered yet."),
  ("M_SELBSTTEST_OK", "Ergebnis: Der Rechenkern arbeitet wie hinterlegt.",
   "Result: the decision core works as specified."),
  ("M_SELBSTTEST_FEHL",
   "Ergebnis: Mindestens ein Fall ist fehlgeschlagen. Bitte die Zeilen oben lesen und melden.",
   "Result: at least one case failed. Please read the lines above and report them."),
  ("M_STAND_ALTER", "Die letzte Messung liegt %d Sekunden zurück.",
   "The last measurement is %d seconds old."),
  ("M_SPERRE", "Es wird gerade nicht geheilt: %s",
   "No healing is happening right now: %s"),
  ("M_NOCH_NICHT", "noch nicht gemessen", "not measured yet"),
  ("M_ZEILE", "%s (%s), stumm seit %d s, nächste Stufe %d, %d geheilt bei %d Versuchen",
   "%s (%s), silent for %d s, next level %d, %d healed in %d attempts"),
  ("M_STUFE_STAT", "%s half %d von %d Mal", "%s helped %d out of %d times"),
  ("M_TABU", "Nicht angefasst wird: %s", "Never touched: %s"),
  ("M_ZEILE_KOPF", "Genau das schickt der Endpunkt an den Miniserver:",
   "This is exactly what the endpoint sends to the Miniserver:"),
  ("F_H_RECHTE", "Die vier Rechte, einzeln nachgesehen (sudo -n -l):",
   "The four permissions, checked individually (sudo -n -l):"),
  ("F_R_SYSTEMCTL", "  systemctl restart darf ausgeführt werden: %s",
   "  systemctl restart may be executed: %s"),
  ("F_R_DOCKER", "  docker restart darf ausgeführt werden: %s",
   "  docker restart may be executed: %s"),
  ("F_R_UHUBCTL", "  uhubctl darf ausgeführt werden: %s",
   "  uhubctl may be executed: %s"),
  ("F_R_TEE", "  tee auf die beiden sysfs-Dateien darf ausgeführt werden: %s",
   "  tee on the two sysfs files may be executed: %s"),
  ("F_H_WERKZEUGE", "Was auf diesem Gerät vorhanden ist:",
   "What is present on this device:"),
  ("F_SYSTEMCTL", "  systemctl vorhanden: %s", "  systemctl present: %s"),
  ("F_DOCKER", "  docker vorhanden: %s", "  docker present: %s"),
  ("F_JOURNALCTL", "  journalctl vorhanden: %s", "  journalctl present: %s"),
  ("F_PHP", "  php auf der Befehlszeile vorhanden (für die Meldungen): %s",
   "  php on the command line present (for the notifications): %s"),
  ("F_SYSFS", "  USB-Anschlüsse lassen sich über sysfs lösen: %s",
   "  USB ports can be released via sysfs: %s"),
  ("F_UHUBCTL", "  uhubctl vorhanden: %s", "  uhubctl present: %s"),
  ("F_UHUBCTL_ROOT", "  uhubctl ließ sich mit Verwalterrechten befragen: %s",
   "  uhubctl could be queried with administrator rights: %s"),
  ("F_HAEHNE", "  Verteiler, die den Strom wirklich schalten: %s",
   "  Hubs that really switch power: %s"),
  ("F_BETRIEBSDAUER", "Betriebsdauer des Systems: %d Sekunden (−1 heißt: nicht lesbar)",
   "Uptime of the system: %d seconds (−1 means: not readable)"),
  ("F_SYSTEMGERAETE",
   "Diese USB-Geräte tragen die Systemplatte und werden nie angefasst: %s",
   "These USB devices carry the system disk and are never touched: %s"),
  ("F_OHNE_SUDO",
   "Ohne die Rechte bleibt nur das Melden. Die Rechtedatei kommt mit dem Plugin-Archiv: LoxBerry legt sie bei der Installation selbst als /etc/sudoers.d/funkwacht ab. Fehlt sie, hilft eine Neuinstallation des Plugins.",
   "Without the permissions only reporting is left. The permission file comes with the plugin archive: LoxBerry itself places it as /etc/sudoers.d/funkwacht during installation. If it is missing, reinstalling the plugin helps."),
  ("MQ_GEFUNDEN", "MQTT-Einstellung gefunden: %s", "MQTT settings found: %s"),
  ("MQ_AUTOSTART", "Gateway startet selbst mit: %s", "Gateway starts automatically: %s"),
  ("MQ_PORT", "UDP-Anschluss: %s", "UDP port: %s"),
  ("MQ_FASSUNG", "Fassung des Gateways: %s", "Gateway version: %s"),
  ("MQ_EIN", "Weitergabe im Plugin eingeschaltet: %s",
   "Forwarding switched on in the plugin: %s"),
  ("MQ_BROKER", "Broker für den Mithörer: %s", "Broker for the listener: %s"),
  ("MQ_AUS_LB", "(aus der LoxBerry-Einstellung)", "(from the LoxBerry settings)"),
  ("MQ_THEMEN", "Diese Themen werden gesendet:", "These topics are published:"),
  ("MQ_SAEUBERUNG",
   "Probe der Säuberung (Zeilenumbrüche werden zu Leerzeichen, sonst zerfiele eine Nachricht in zwei): „%s“",
   "Sample of the cleanup (line breaks become spaces, otherwise a message would fall into two): „%s“"),
  ("EP_AUFRUF", "Aufgerufen wird: %s", "Calling: %s"),
  ("EP_FEHL",
   "Der Endpunkt hat nicht geantwortet. Läuft der Webserver, und ist der Ordner webfrontend/html vorhanden?",
   "The endpoint did not answer. Is the web server running, and does the folder webfrontend/html exist?"),
  ("EP_GEGENPROBE", "Gegenprobe mit falschem Wortzeichen:",
   "Cross-check with a wrong access word:"),
  # Der Rumpf allein genuegt nicht: eine Abweisung, die als HTTP 200
  # herausgeht, kommt beim Miniserver als Erfolg an. Deshalb steht der
  # Statuscode in der Zeile.
  ("EP_ABGEWIESEN_CODE", "Wurde abgewiesen, HTTP %d — so soll es sein.",
   "Rejected, HTTP %d — as it should be."),
  ("EP_CODE", "Statuscode: HTTP %d", "Status code: HTTP %d"),
  ("EP_OFFEN", "ACHTUNG: Der Endpunkt hat trotz falschem Wortzeichen geantwortet: %s",
   "WARNING: the endpoint answered despite a wrong access word: %s"),
  ("S_USB_SPALTEN", "Kennung,Hersteller,Verteiler,Port,Produkt,Gerätedatei", "Identifier,Vendor,Hub,Port,Product,Device file"),
  ("S_USB_KOPF",
   "Die USB-Geräte dieses Rechners. Die Spalte „Kennung“ ist der USB-Pfad für das Feld in den Einstellungen.",
   "The USB devices of this machine. The column „identifier“ is the USB path for the field in the settings."),
  ("S_USB_FUSS",
   "Mit << gekennzeichnete Geräte tragen die Systemplatte — sie werden nie angefasst, auch wenn man sie einträgt. Die Spalte Geräted atei ist der Pfad für die Art „seriell“, die Spalten Verteiler und Port sind die Angaben für Stufe 3.",
   "Devices marked with << carry the system disk — they are never touched, even if entered. The device-node column is the path for the kind „serial“, the hub and port columns are the values for level 3."),
  ("S_KEIN_USB",
   "Es wurde kein USB-Gerät gefunden. Auf diesem Gerät gibt es /sys/bus/usb/devices nicht — oder es hängt wirklich nichts daran.",
   "No USB device was found. This machine has no /sys/bus/usb/devices — or there really is nothing attached."),
  ("S_SYSTEM", "trägt das System, gesperrt", "carries the system, locked"),
  ("S_DIENSTE_KOPF", "Dienste, deren Name nach Funk aussieht:",
   "Services whose name looks like radio:"),
  ("S_DIENSTE_FUSS",
   "Das ist eine Vorschlagsliste, kein Filter — wer einen Dienst mit einem anderen Namen sucht, trägt ihn von Hand ein.",
   "This is a list of suggestions, not a filter — if your service has a different name, enter it by hand."),
  ("S_KEIN_DIENST",
   "Es wurde kein passender Dienst gefunden. Entweder gibt es systemctl hier nicht, oder kein Dienstname enthält eines der Funkworte.",
   "No matching service was found. Either systemctl does not exist here, or no service name contains one of the radio words."),
  ("S_CONTAINER_KOPF", "Die Docker-Container dieses Rechners:",
   "The Docker containers of this machine:"),
  ("S_KEIN_CONTAINER",
   "Es wurde kein Container gefunden. Entweder gibt es Docker hier nicht, oder der Benutzer loxberry darf es nicht befragen.",
   "No container was found. Either Docker does not exist here, or the user loxberry may not query it."),
  ("S_KEIN_WERKZEUG",
   "Die Suchhilfe bin/fw_suche.py wurde nicht gefunden. Bitte das Plugin neu installieren.",
   "The search helper bin/fw_suche.py was not found. Please reinstall the plugin."),
  ("S_MESS_KOPF", "Stick %d: %s (Art %s)", "Stick %d: %s (kind %s)"),
  ("S_MESS_ALTER", "  Gemessenes Alter: %s   (gilt als gestört ab %d s)",
   "  Measured age: %s   (counts as faulty from %d s)"),
  ("S_MESS_ZWEI", "  Kriterium 1: %s, Kriterium 2: %s",
   "  Criterion 1: %s, criterion 2: %s"),
  ("S_MESS_BEM", "  Bemerkung: %s", "  Note: %s"),
  ("S_MESS_NEUSTARTS", "  Neustarts des Dienstes: %d", "  Restarts of the service: %d"),
  ("S_MESS_URTEIL", "  Urteil: %s (%s)", "  Verdict: %s (%s)"),
  ("S_MESS_FUSS",
   "Das ist eine Messung von jetzt, unabhängig vom Wächter — es wurde nichts geheilt und nichts gespeichert.",
   "This is a measurement taken now, independent of the watchdog — nothing was healed and nothing saved."),
  ("S_MESS_FEHL", "Stick %d ließ sich nicht messen: %s",
   "Stick %d could not be measured: %s"),
  ("J_DIENST", "Die letzten 60 Zeilen aus dem Journal von %s:",
   "The last 60 lines from the journal of %s:"),
  ("J_CONTAINER", "Die letzten 60 Zeilen aus dem Protokoll des Containers %s:",
   "The last 60 lines from the log of container %s:"),
  ("J_UNBEKANNT", "Stick %d gibt es nicht.", "There is no stick %d."),
  ("J_NICHTS",
   "Für %s ist weder ein Dienst noch ein Container eingetragen — es gibt kein Protokoll zum Nachsehen.",
   "For %s neither a service nor a container is configured — there is no log to look at."),
  ("J_NAME_UNGUELTIG",
   "Der eingetragene Name enthält Zeichen, die in einem Dienst- oder Containernamen nichts zu suchen haben. Abgewiesen.",
   "The configured name contains characters that have no place in a service or container name. Rejected."),
  ("J_LEER", "Das Protokoll ist leer, oder der Benutzer loxberry darf es nicht lesen.",
   "The log is empty, or the user loxberry may not read it."),
  ("P_KOPF",
   "Trägt die Einrichtung? Jede Zeile ist eine Frage. [ ok ] heißt ja, [ !! ] heißt nein, [ -- ] heißt: hier lässt sich nichts messen — ein Kreuz wäre dort ein Kreuz, das nichts bedeutet.",
   "Does the setup hold? Every line is a question. [ ok ] means yes, [ !! ] means no, [ -- ] means: nothing can be measured here — a cross would be a cross that means nothing."),
  ("P_ENDPUNKT", "Antwortet der eigene Endpunkt so, wie der Miniserver ihn abfragt?",
   "Does the own endpoint answer the way the Miniserver queries it?"),
  ("P_ENDPUNKT_OK", "HTTP %d, und die Antwort beginnt mit der erwarteten Kennung.",
   "HTTP %d, and the answer starts with the expected marker."),
  ("P_ENDPUNKT_FEHL", "HTTP %d. Anfang der Antwort: %s",
   "HTTP %d. Beginning of the answer: %s"),
  ("P_ENDPUNKT_STUMM",
   "Keine Antwort. Das ist kein Befund: ein Webserver, der nur eine Anfrage zugleich bearbeitet, kann sich während des Seitenaufbaus nicht selbst aufrufen. Bitte die Adresse aus dem Reiter Einbindung in Loxone von Hand im Browser öffnen.",
   "No answer. This is not a finding: a web server that handles only one request at a time cannot call itself while building the page. Please open the address from the Loxone integration tab by hand in the browser."),
  ("P_GEGENPROBE", "Weist der Endpunkt ein falsches Wortzeichen ab?",
   "Does the endpoint reject a wrong access word?"),
  ("P_GEGENPROBE_FREMD",
   "Es hat etwas geantwortet, aber nicht dieses Plugin — vermutlich der Webserver mit einer Fehlerseite. Damit ist die Frage nicht beantwortet, weder mit ja noch mit nein. Anfang der Antwort: %s",
   "Something answered, but not this plugin — probably the web server with an error page. That leaves the question unanswered, neither yes nor no. Beginning of the answer: %s"),
  ("P_SELFTEST", "Antwortet ?selftest=1, OHNE etwas auszulösen?",
   "Does ?selftest=1 answer WITHOUT triggering anything?"),
  ("P_SELFTEST_OK",
   "Ja — die Selbstprobe meldet WIRKUNG=0, und es wurde nichts quittiert.",
   "Yes — the self-probe reports WIRKUNG=0, and nothing was acknowledged."),
  ("P_SELFTEST_FEHL", "Unerwartete Antwort: %s", "Unexpected answer: %s"),
  ("P_F_REITER", "Tragen Reiterleiste, Bereiche und Positivliste dieselben Namen?",
   "Do the tab bar, the sections and the allow list carry the same names?"),
  ("P_REITER", "Leiste %d, Bereiche %d, Liste %d: %s",
   "Bar %d, sections %d, list %d: %s"),
  ("P_F_SMACTIVE", "Setzt der Server die Klasse für den offenen Reiter selbst?",
   "Does the server set the class for the open tab itself?"),
  ("P_SMACTIVE",
   "Leiste %d, Bereiche %d von %d Reitern. Ohne das wäre die Seite ohne JavaScript leer.",
   "Bar %d, sections %d of %d tabs. Without it the page would be empty without JavaScript."),
  ("P_F_FELDER", "Liefert der Wächter genau die Felder, die die Vorlage anlegt?",
   "Does the watchdog deliver exactly the fields the template creates?"),
  ("P_FELDER_OK", "%d Felder, in Vorlage und Messung dieselben.",
   "%d fields, the same in template and measurement."),
  ("P_FELDER_ABW", "Fehlt in der Messung: %s. Zu viel in der Messung: %s",
   "Missing in the measurement: %s. Surplus in the measurement: %s"),
  ("P_F_NUMMERN", "Zählen Oberfläche und Wächter die Sticks gleich?",
   "Do the interface and the watchdog count the sticks the same way?"),
  ("P_NUMMERN", "Oberfläche: %s — Wächter: %s", "Interface: %s — watchdog: %s"),
  ("P_F_GRUENDE", "Kennt die Sprachdatei jeden Grund, den der Rechenkern erzeugen kann?",
   "Does the language file know every reason the decision core can produce?"),
  ("P_GRUENDE_OK", "%d Gründe und %d Hinderungsgründe, alle beschriftet.",
   "%d reasons and %d blocking reasons, all with a label."),
  ("P_GRUENDE_FEHLT", "Ohne Text: %s", "Without a text: %s"),
  ("P_F_DIENST", "Läuft der Wächter?", "Is the watchdog running?"),
  ("P_DIENST_OK", "Ja, Prozessnummer %d.", "Yes, process number %d."),
  ("P_DIENST_STEHT",
   "Nein. Der Minutentakt startet ihn wieder; der Knopf im Reiter Einstellungen tut es sofort.",
   "No. The one-minute cron will start it again; the button in the Settings tab does it immediately."),
  ("P_F_MESSUNG", "Ist die letzte Messung frisch?", "Is the last measurement fresh?"),
  ("P_MESSUNG", "%d Sekunden alt, Prüftakt %d Sekunden.",
   "%d seconds old, check interval %d seconds."),
  ("P_KEINE_MESSUNG", "Es liegt noch keine Messung vor.",
   "There is no measurement yet."),
  ("P_F_MITHOERER", "Läuft der MQTT-Mithörer, und hört er etwas?",
   "Is the MQTT listener running, and does it hear anything?"),
  ("P_MITH_UNNOETIG",
   "Kein Stick steht auf der Art „MQTT“ — der Mithörer wird nicht gebraucht.",
   "No stick uses the kind „MQTT“ — the listener is not needed."),
  ("P_MITH_STEHT",
   "Nein, er steht — dabei steht mindestens ein Stick auf der Art „MQTT“. Der Knopf „Wächter neu starten“ startet ihn mit.",
   "No, it is down — although at least one stick uses the kind „MQTT“. The button „restart watchdog“ starts it as well."),
  ("P_MITH_OK", "Ja, Prozessnummer %d, und auf %d Themen ist schon etwas angekommen.",
   "Yes, process number %d, and something has already arrived on %d topics."),
  ("P_MITH_ABO_UNBEKANNT", "Er läuft (Prozessnummer %d), hat aber noch keine Liste seiner Abonnements abgelegt — etwa, weil er gerade erst startet. In einer Minute noch einmal fragen.", "It is running (process number %d) but has not stored a list of its subscriptions yet — perhaps it is just starting. Ask again in a minute."),
  ("P_MITH_ABO_ABW", "Er läuft (Prozessnummer %d), aber seine Abonnements passen nicht zur Konfiguration. Abonniert, aber nicht eingerichtet: %s. Eingerichtet, aber nicht abonniert: %s. Er gleicht das binnen weniger Sekunden selbst ab — bleibt es stehen, den Wächter neu starten.", "It is running (process number %d), but its subscriptions do not match the configuration. Subscribed but not configured: %s. Configured but not subscribed: %s. It catches up by itself within a few seconds — if this stays, restart the watchdog."),
  ("P_MITH_STILL",
   "Er läuft (Prozessnummer %d), aber auf diesen Themen kam noch nichts an: %s. Das ist kein Befund — manche Themen kommen nur alle paar Minuten. Der Knopf „Zehn Sekunden am Broker zuhören“ sagt mehr.",
   "It is running (process number %d), but nothing has arrived yet on these topics: %s. That is not a finding — some topics only appear every few minutes. The button „listen at the broker for ten seconds“ says more."),
  ("P_F_RECHTE", "Darf der Wächter die vier Befehle ausführen, die er zum Heilen braucht?",
   "May the watchdog execute the four commands it needs for healing?"),
  ("P_RECHTE_UNBEKANNT",
   "Noch nicht gemessen — bitte zuerst „Was kann dieses Gerät?“ drücken.",
   "Not measured yet — please press „What can this device do?“ first."),
  ("P_F_ZWEITSCHRIFT", "Gibt es eine Zweitschrift der Einstellungen?",
   "Is there a second copy of the settings?"),
  ("P_ZWEITSCHRIFT_OK",
   "Ja, %s — und sie liegt neben dem Konfigurationsordner, nicht darin. Nur so überlebt sie eine Deinstallation.",
   "Yes, %s — and it lies next to the configuration folder, not inside it. Only that way does it survive an uninstall."),
  ("P_ZWEITSCHRIFT_FEHLT", "Nein. Sie entsteht beim ersten Speichern.",
   "No. It is created on the first save."),
  ("P_F_HEBEL", "Hat jeder Stick, der geheilt werden soll, auch einen Hebel dafür?",
   "Does every stick that should be healed also have a lever for it?"),
  ("P_HEBEL_OK", "Ja, bei jedem ist mindestens eine Stufe hinterlegt.",
   "Yes, every one has at least one level configured."),
  ("P_HEBEL_OHNE",
   "Ohne Hebel: %s. Bei diesen ist Heilen eingeschaltet, aber es steht weder Dienst noch Container, USB-Pfad oder Verteiler da.",
   "Without a lever: %s. For these healing is switched on, but no service, container, USB path or hub is entered."),
  ("P_F_VORLAGE", "Sind die erzeugten Loxone-Vorlagen wohlgeformt?",
   "Are the generated Loxone templates well-formed?"),
  ("P_VORLAGE_OK", "Ja — Eingänge %d Kindelemente, Steuerbefehle %d.",
   "Yes — inputs %d child elements, control commands %d."),
  ("P_VORLAGE_FEHL",
   "Nein — die Datei ließe sich in Loxone Config nicht einlesen. Bitte melden.",
   "No — the file could not be imported into Loxone Config. Please report this."),
  ("P_F_BESTAND", "Überstehen Zähler und Verlauf die nächste Aktualisierung?",
   "Will counters and history survive the next update?"),
  ("P_BESTAND_KEIN_ORDNER", "Den Datenordner gibt es hier nicht — das Plugin ist nicht installiert.",
   "The data folder does not exist here — the plugin is not installed."),
  ("P_BESTAND_GESPERRT",
   "In %s darf nicht geschrieben werden. Der Installer löscht den Datenordner bei jeder Aktualisierung; ohne Schreibrecht daneben sind Zähler und Verlauf danach weg.",
   "Writing to %s is not permitted. The installer deletes the data folder on every update; without write access next to it, counters and history are gone afterwards."),
  ("P_BESTAND_BEREIT",
   "Ja. Der Nachbarordner lässt sich anlegen — beim nächsten Update werden Zähler und Verlauf dorthin gerettet und danach zurückgeholt.",
   "Yes. The neighbouring folder can be created — at the next update, counters and history are saved there and brought back afterwards."),
  ("P_BESTAND_DA", "Ja. Aus der letzten Aktualisierung liegt bereits eine Sicherung bereit: %s (vom %s).",
   "Yes. A backup from the last update is already in place: %s (from %s)."),
  ("P_F_THEMEN", "Senden Wächter und Oberfläche dieselben MQTT-Themen, mit demselben „retained“?",
   "Do the watchdog and the interface use the same MQTT topics, with the same „retained“?"),
  ("P_THEMEN_OK", "Ja — %d Themen, davon %d retained, in beiden Tabellen gleich.",
   "Yes — %d topics, %d of them retained, identical in both tables."),
  ("P_THEMEN_OHNE_ZEILE", "(ohne Zeile in der Thementabelle)", "(without a row in the topic table)"),
  ("P_THEMEN_ABW", "Nein. Abweichend (Wächter/Oberfläche, 1 = retained): %s",
   "No. Differing (watchdog/interface, 1 = retained): %s"),
  ("P_THEMEN_NICHT", "Der Wächter ließ sich nicht nach seinen Themen fragen — hier lässt sich nichts messen.",
   "The watchdog could not be asked for its topics — nothing can be measured here."),
  ("P_F_SPERRE", "Wird gerade geheilt, oder hält eine Sperre den Wächter an?",
   "Is healing happening, or does a lock hold the watchdog back?"),
  ("P_SPERRE_KEINE", "Es hält nichts auf — es würde geheilt, wenn es nötig wäre.",
   "Nothing is holding it back — healing would happen if needed."),
  ("P_SPERRE",
   "Es wird gemessen und gemeldet, aber nicht geheilt: %s. Das ist kein Fehler — es erklärt nur, warum nichts geschieht.",
   "Measuring and reporting continue, but nothing is healed: %s. That is not a fault — it just explains why nothing happens."),
  ("P_KEINE_DATEI", "Die Oberflächendatei war nicht lesbar.",
   "The interface file could not be read."),
  ("P_ERGEBNIS", "Ergebnis: %d mit Haken, %d mit Kreuz, %d ohne Messung — %d Fragen angesehen.",
   "Result: %d with a tick, %d with a cross, %d without measurement — %d questions examined."),
  # ---- Nachgetragen 20.09.2026 aus den ausgelieferten .ini ------------------
  # Diese Schluessel standen nur dort; der Erzeuger wies deshalb jeden Lauf ab.
  # Neue Werte in doppelten Anfuehrungszeichen: sie enthalten Apostrophe.
  ("P_F_MARKE", "Läuft gerade eine Aktualisierung dieses Plugins?",
   "Is an update of this plugin running right now?"),
  ("P_MARKE_ALT", "Eine Marke liegt seit %d Stunden — sie gilt nicht mehr, der Wächter läuft wieder an. Vermutlich ist eine Aktualisierung abgebrochen. Die Datei darf weg: %s",
   "A marker has been lying around for %d hours — it no longer counts, the watchdog starts again. An update was probably aborted. The file may be deleted: %s"),
  ("P_MARKE_FRISCH", "Ja, seit %d Minuten. Solange startet der Minutentakt nichts; das letzte Hakenskript räumt die Marke weg. Nach einer Stunde gilt sie ohnehin nicht mehr.",
   "Yes, for %d minutes. While it lasts the minute task starts nothing; the last hook script removes the marker. After an hour it no longer counts anyway."),
  ("P_MARKE_KEINE", "Nein — es liegt keine Marke. Der Minutentakt darf den Wächter starten.",
   "No — there is no marker. The minute task is allowed to start the watchdog."),
  ("P_MARKE_UNLESBAR", "Es liegt eine Marke, aber ohne lesbare Uhrzeit — sie gilt nicht. Die Datei darf weg: %s",
   "There is a marker, but without a readable time — it does not count. The file may be deleted: %s"),
  ("P_MARKE_ZUKUNFT", "Es liegt eine Marke mit einer Uhrzeit in der Zukunft — sie gilt nicht. Bitte die Systemuhr ansehen. Die Datei: %s",
   "There is a marker with a time in the future — it does not count. Please check the system clock. The file: %s"),
 ]),
 ("LOG", [
  ("H", "Protokoll des Wächters", "Watchdog log"),
  ("ERKLAERUNG", "Die jüngsten 400 Zeilen, neueste zuerst. Die vollständige Datei liegt unter",
   "The most recent 400 lines, newest first. The complete file is at"),
  ("LEER", "Das Protokoll ist leer.", "The log is empty."),
  ("H_EREIGNISSE", "Was wann geschehen ist", "What happened when"),
  ("EREIGNISSE_TEXT",
   "Die letzten Heilungen, Quittierungen und Erfolgskontrollen mit Zeitpunkt. Diese Liste überlebt einen Neustart — nach einem Neustart des Miniservers war sonst nicht mehr feststellbar, WANN der letzte Ausfall war.",
   "The most recent recoveries, acknowledgements and success checks with their time. This list survives a reboot — after a restart of the Miniserver it was otherwise impossible to tell WHEN the last outage happened."),
  ("EREIGNISSE_LEER", "Es ist noch nichts geschehen. Das ist die beste Nachricht.",
   "Nothing has happened yet. That is the best news."),
  ("SP_ZEIT", "Zeitpunkt", "Time"),
  ("SP_WAS", "Was", "What"),
  ("H_VERLAUF", "Heilversuche je Tag", "Healing attempts per day"),
  ("VERLAUF_TEXT",
   "Die letzten dreißig Tage. <b>Das ist der nützlichste Blick des ganzen Plugins:</b> steigt der Balken über Wochen langsam an, ist ein Stick am Ende seiner Kräfte, lange bevor er ganz ausfällt.",
   "The last thirty days. <b>This is the most useful view of the whole plugin:</b> if the bars slowly rise over weeks, a stick is nearing the end of its life long before it fails completely."),
  ("VERLAUF_LEER",
   "In den letzten dreißig Tagen wurde nichts geheilt. Auch das ist eine Auskunft.",
   "Nothing was healed in the last thirty days. That is information too."),
  ("VERLAUF_DATEIEN", "%d Tagesdateien liegen unter %s — Spalten mit Semikolon getrennt.",
   "%d daily files are stored under %s — columns separated by semicolons."),
  ("H_START", "Ausgabe beim Start", "Output at start"),
  ("START_ERKLAERUNG",
   "Startet der Wächter nicht, steht der Grund hier — nicht im Protokoll darüber. Die Datei liegt unter",
   "If the watchdog does not start, the reason is here — not in the log above. The file is at"),
  ("START_LEER", "Beim Start gab es nichts zu melden. Das ist der Normalfall.",
   "There was nothing to report at start. That is the normal case."),
  ("H_MITHOERER", "Ausgabe des Mithörers", "Output of the listener"),
  ("K_LEEREN", "Protokoll leeren", "Clear log"),
  ("SICHER", "Ja, das Protokoll leeren (Ereignisliste, Zähler und Verlauf bleiben)", "Yes, clear the log (event list, counters and history stay)"),
  ("LEEREN_FEHL", "Das Protokoll %s ließ sich nicht leeren.", "The log %s could not be cleared."),
  ("GELEERT", "Das Protokoll wurde geleert.", "The log has been cleared."),
 ]),
 # Sprachausgabe (Funkwacht 1.0.11, Welle sp2) - nachgezogen 08.10.2026.
 ("DURCHSAGE", [
  ("H",
   "Ansage bei Störung (Sprachausgabe, ab Werk an)",
   "Announcement on fault (speech output, on by default)"),
  ("TEXT_HILFE",
   "Ein weiterer Meldeweg neben LoxBerry-Meldung, SignalBot und Loxone: Wechselt der Befund eines Sticks auf gestört oder zurück auf in Ordnung, sagt die Funkwacht das über die gemeinsame Sprachausgabe der Plugins dieses Hauses an – Loxone Music Server, MusicServer4Home, eine eigene Adressvorlage, Alexa-NG oder Google-Lautsprecher (Chromecast 4 Lox NG). Höchstens einmal je Anlass und Stick in 30 Minuten; Werte im Takt werden nie angesagt. Gesprochen wird aus dem Wächter, unabhängig von den übrigen Wegen. Adresse und Vorlage müssen im Heimnetz liegen. Ab Werk an.",
   "Another notification path next to the LoxBerry notification, SignalBot and Loxone: when the finding of a stick changes to faulty or back to OK, the radio watch announces it through the shared speech output of the plugins of this house – Loxone Music Server, MusicServer4Home, an own address template, Alexa-NG or Google speakers (Chromecast 4 Lox NG). At most once per occasion and stick in 30 minutes; values in the cycle are never announced. It speaks from the watchdog, independently of the other paths. Address and template must be in the home network. On by default."),
  ("L_ANLAESSE",
   "Anzusagende Ereignisse",
   "Events to announce"),
  ("H_ANLAESSE",
   "Jedes Ereignis lässt sich einzeln abwählen. Wirksam erst mit einer Ausgabeart unten.",
   "Each event can be deselected. Effective only with an output type below."),
  ("A_GESTOERT",
   "Stick gestört",
   "Stick faulty"),
  ("A_WIEDER",
   "Stick wieder in Ordnung",
   "Stick OK again"),
  ("TEXT_GESTOERT",
   "Funkwacht: %s ist gestört.",
   "Radio watch: %s is faulty."),
  ("TEXT_WIEDER",
   "Funkwacht: %s ist wieder in Ordnung.",
   "Radio watch: %s is OK again."),
  ("PRUEF",
   "Ansage bei Störung (Sprachausgabe)",
   "Announcement on fault (speech output)"),
  ("K_TEST",
   "Testansage",
   "Test announcement"),
  ("M_TEST_OK",
   "Testansage gesendet.",
   "Test announcement sent."),
  ("M_TEST_NICHTS",
   "Keine Testansage: %s",
   "No test announcement: %s"),
  ("M_TEST_FEHL",
   "Testansage nicht gesendet: %s",
   "Test announcement not sent: %s"),
  ("SICH_TOKEN",
   "Die Datei trägt ein Sprechtoken (%s). Eine Sicherung dieses Plugins enthält nie eines – die Datei wird abgewiesen, das geltende Token bleibt.",
   "The file carries a speech token (%s). A backup of this plugin never contains one – the file is rejected, the current token stays."),
  ("SICH_WERT",
   "Unzulässiger Wert in der Sprachausgabe (tts): %s",
   "Invalid value in the speech output (tts): %s"),
  ("SICH_BEHALTEN",
   "Die Sicherung stammt von vor der Sprachausgabe und enthält deren Einstellungen nicht (%s). Die geltenden Werte bleiben.",
   "The backup predates the speech output and does not contain its settings (%s). The current values stay."),
 ]),
]

# ======================================================================
# Die Hilfe. Die Schluessel muessen zu templates/help/help.html passen -
# jeder TMPL_VAR dort braucht hier einen Wert, und umgekehrt.
# ======================================================================

HILFE = [
 ("K01", "Funkwacht", "Funkwacht"),
 ("K02",
  "Funksticks für Zigbee, Z-Wave und Bluetooth fallen selten laut aus. Sie hören einfach auf zu antworten — der Dienst läuft weiter, die Oberfläche sieht normal aus, und erst Tage später fällt auf, dass kein Bewegungsmelder mehr meldet. Die Funkwacht sieht in festem Takt nach, ob noch etwas kommt, weckt einen stummen Stick in Stufen wieder auf — und misst danach nach, ob es geholfen hat.",
  "Radio dongles for Zigbee, Z-Wave and Bluetooth rarely fail loudly. They simply stop answering — the service keeps running, the interface looks normal, and only days later does someone notice that no motion sensor has reported in. Funkwacht checks at a fixed interval whether anything is still arriving, wakes a silent dongle up again in stages — and then measures whether that helped."),
 ("K03", "Warum nicht einfach am Stick nachsehen?",
  "Why not just look at the dongle itself?"),
 ("K04",
  "Weil das Nachsehen den Ausfall auslösen kann. Eine serielle Schnittstelle lässt sich nur von einem Programm gleichzeitig öffnen. Ein Wächter, der <span class='sm-mono'>/dev/ttyUSB0</span> öffnet, um zu prüfen, ob der Stick lebt, nimmt sie Zigbee2MQTT weg — und erzeugt genau den Zustand, den er verhindern soll.",
  "Because looking can cause the outage. A serial port can only be opened by one program at a time. A watchdog that opens <span class='sm-mono'>/dev/ttyUSB0</span> to check whether the dongle is alive takes it away from Zigbee2MQTT — creating exactly the state it is meant to prevent."),
 ("K05",
  "Die Funkwacht öffnet deshalb <b>niemals</b> selbst eine serielle Schnittstelle. Sie sieht auf das, was der Dienst hinterlässt.",
  "Funkwacht therefore <b>never</b> opens a serial port itself. It looks at what the service leaves behind."),
 ("K06", "Woran ein Lebenszeichen abgelesen wird",
  "How a sign of life is read"),
 ("K07", "Acht Arten stehen zur Wahl, und sie beantworten verschiedene Fragen:",
  "Eight kinds are available, and they answer different questions:"),
 ("K34",
  "<b>Datei</b> sieht auf das Änderungsdatum der Protokolldatei. Mit dem Haken <i>Datei muss wachsen</i> zählt nur, dass sie größer geworden ist — manche Dienste fassen ihr Protokoll auch dann an, wenn sie nichts mehr zu melden haben.",
  "<b>File</b> looks at the modification time of the log file. With the tick <i>file must grow</i> only an increase in size counts — some services touch their log even when they have nothing left to report."),
 ("K35",
  "<b>MQTT</b> merkt sich, wann auf einem Thema zuletzt etwas ankam. Dafür läuft ein eigener kleiner Mithörer — siehe weiter unten. Als Lebenszeichen taugt nur ein Thema, das <b>laufend</b> gesendet wird: zurückbehaltene Nachrichten, die der Broker beim Abonnieren nachliefert, und leere Nachrichten zählen nicht. Bei Zigbee2MQTT ist das <span class='sm-mono'>zigbee2mqtt/bridge/health</span> (Vorgabe alle zehn Minuten), nicht <span class='sm-mono'>bridge/state</span> — das ist zurückbehalten und kommt nur bei einer Änderung.",
  "<b>MQTT</b> records when something last arrived on a topic. A small separate listener does that — see below. Only a topic that is sent <b>continuously</b> works as a sign of life: retained messages, which the broker delivers again on subscribing, and empty messages do not count. For Zigbee2MQTT that is <span class='sm-mono'>zigbee2mqtt/bridge/health</span> (every ten minutes by default), not <span class='sm-mono'>bridge/state</span> — that one is retained and only comes on a change."),
 ("K36",
  "<b>USB</b> sieht nach, ob der Stick überhaupt noch am Bus hängt. Das ist die einzige Art, die <b>„Stick weg“ von „Dienst hängt“ unterscheidet</b>. Wer zusätzlich die Hersteller- und Produktkennung einträgt, merkt auch, wenn jemand ein anderes Gerät in denselben Anschluss gesteckt hat. <b>Für Stufe 2 und 3 ist die Kennung Pflicht:</b> ohne sie lehnt der Wächter diese Stufen ab.",
  "<b>USB</b> checks whether the dongle is still on the bus at all. This is the only kind that <b>separates „dongle gone“ from „service stuck“</b>. If you also enter the vendor and product ID, you will notice when someone has plugged a different device into the same port. <b>For levels 2 and 3 the identifier is mandatory:</b> without it the watchdog refuses these levels."),
 ("K37",
  "<b>systemd-Dienst</b> und <b>Docker</b> fragen den Dienst selbst — und melden zusätzlich seinen Neustartzähler. Ein Dienst, den das System alle drei Minuten neu startet, sieht am Änderungsdatum seines Protokolls kerngesund aus; der Zähler ist der einzige Wert, der ihn verrät. Docker selbst bringt das LoxBerry-Plugin <b>Docker NG</b> (<a href='https://github.com/timanders22/LoxBerry-Plugin-Docker-NG' target='_blank' rel='noopener'>github.com/timanders22/LoxBerry-Plugin-Docker-NG</a>); fehlt Docker oder der Zugriff darauf, sagt es der Reiter <i>Einstellungen</i>.",
  "<b>systemd service</b> and <b>Docker</b> ask the service itself — and also report its restart counter. A service the system restarts every three minutes looks perfectly healthy by the modification time of its log; the counter is the only value that gives it away. Docker itself comes with the LoxBerry plugin <b>Docker NG</b> (<a href='https://github.com/timanders22/LoxBerry-Plugin-Docker-NG' target='_blank' rel='noopener'>github.com/timanders22/LoxBerry-Plugin-Docker-NG</a>); if Docker or access to it is missing, the <i>Settings</i> tab says so."),
 ("K38",
  "<b>HTTP</b>, <b>seriell</b> und <b>Bluetooth</b> prüfen die Erreichbarkeit einer Adresse, das Vorhandensein der Gerätedatei und die Anmeldung des Adapters.",
  "<b>HTTP</b>, <b>serial</b> and <b>Bluetooth</b> check the reachability of an address, the presence of the device node and the registration of the adapter."),
 ("K39",
  "<b>Zwei Arten lassen sich je Stick verknüpfen.</b> „USB vorhanden UND MQTT frisch“ trennt sauber zwischen den beiden Fehlerbildern — und erlaubt, gleich die richtige Stufe zu ziehen.",
  "<b>Two kinds can be combined per dongle.</b> „USB present AND MQTT fresh“ cleanly separates the two failure modes — and allows going straight to the right stage."),
 ("K40", "Die drei Stufen", "The three stages"),
 ("K08",
  "Meldet sich ein Stick länger nicht, als unter „Stumm bis“ eingetragen ist, wird der Reihe nach versucht:",
  "If a dongle stays silent longer than the value under „Silent until“, the following is tried in order:"),
 ("K09",
  "<b>Stufe 1 — Dienst:</b> <span class='sm-mono'>systemctl restart</span> oder <span class='sm-mono'>docker restart</span>. Das hilft, wenn der Dienst hängt, der Stick aber gesund ist. Es kostet nichts und ist fast immer richtig.",
  "<b>Stage 1 — service:</b> <span class='sm-mono'>systemctl restart</span> or <span class='sm-mono'>docker restart</span>. This helps when the service is stuck but the dongle is healthy. It costs nothing and is almost always the right first move."),
 ("K10",
  "<b>Stufe 2 — USB-Anschluss:</b> Der Stick wird über <span class='sm-mono'>/sys/bus/usb/drivers/usb</span> abgemeldet und wieder angemeldet. Das entspricht Ausstecken und Einstecken, ohne dass jemand hingehen muss.",
  "<b>Stage 2 — USB port:</b> the dongle is unbound and rebound via <span class='sm-mono'>/sys/bus/usb/drivers/usb</span>. That amounts to unplugging and plugging it back in without anyone having to walk over."),
 ("K11",
  "<b>Stufe 3 — Strom:</b> <span class='sm-mono'>uhubctl</span> nimmt dem Anschluss am Verteiler die Spannung. Nur das setzt einen Stick zurück, dessen eigener Rechner abgestürzt ist.",
  "<b>Stage 3 — power:</b> <span class='sm-mono'>uhubctl</span> cuts power to the port on the hub. Only that resets a dongle whose own processor has crashed."),
 ("K12",
  "Übersprungen wird jede Stufe, für die nichts eingetragen ist. <b>Die Reihenfolge lässt sich umstellen:</b> bei manchen Aufbauten bringt ein Dienstneustart nichts, solange der Stick selbst festgefahren ist. <b>Kam von einem Stick noch nie ein Lebenszeichen, wird gar nicht geheilt</b> — das ist fast immer ein falscher Pfad, und darauf ist ein USB-Reset die falsche Antwort.",
  "Any stage with nothing configured is skipped. <b>The order can be changed:</b> in some setups a service restart achieves nothing while the dongle itself is locked up. <b>If a dongle has never shown any sign of life, nothing is healed at all</b> — that is almost always a wrong path, and a USB reset is the wrong answer to it."),
 ("K41",
  "<b>Nach Stufe 2 oder 3 kommt der Dienstneustart gleich hinterher.</b> Ein unbind/bind lässt den Dienst sonst mit einem toten Dateideskriptor zurück: der Stick ist da, aber Zigbee2MQTT redet nicht mehr mit ihm.",
  "<b>After stage 2 or 3 the service restart follows immediately.</b> Otherwise an unbind/bind leaves the service with a dead file descriptor: the dongle is back, but Zigbee2MQTT no longer talks to it."),
 ("K42", "Wirkt das Heilen überhaupt?", "Does the healing work at all?"),
 ("K43",
  "Nach der Erholungszeit misst die Funkwacht nach, ob der Stick wirklich zurück ist, und zählt das Ergebnis <b>je Stufe</b>. Im Reiter <i>Test</i> steht dann ein Satz wie „Stufe 1 half 12 von 14 Mal, Stufe 2 nie“.",
  "After the recovery time Funkwacht measures whether the dongle really came back, and counts the result <b>per stage</b>. The <i>Test</i> tab then says something like „stage 1 helped 12 out of 14 times, stage 2 never“."),
 ("K44",
  "Damit lässt sich auch die Gegenfrage beantworten: Gehen <span class='sm-mono'>VERSUCHE</span> und <span class='sm-mono'>HEILUNGEN</span> weit auseinander, wirkt das Heilen nicht — dann hilft kein weiterer Neustart, sondern ein Blick auf die Rechte oder auf die Verkabelung. Wer will, lässt eine Stufe, die zehnmal nichts gebracht hat, überspringen; der Haken heißt <i>taube Stufe überspringen</i> und ist ab Werk aus.",
  "This also answers the opposite question: if <span class='sm-mono'>VERSUCHE</span> and <span class='sm-mono'>HEILUNGEN</span> drift apart, healing is not working — then no further restart helps, but a look at the permissions or the cabling does. If you like, a stage that has achieved nothing ten times can be skipped; the tick is called <i>skip a level that never helps</i> and is off by default."),
 ("K13", "Stufe 3 verspricht mehr, als die meisten Verteiler halten",
  "Stage 3 promises more than most hubs deliver"),
 ("K14",
  "Strom am Anschluss abschalten kann nur ein Verteiler, der „per-port power switching“ beherrscht. <b>Der eingebaute Verteiler des Raspberry Pi 4 kann es nicht.</b> Ältere Modelle können bestenfalls den ganzen Bus auf einmal — womit auch Tastatur und Festplatte mitgingen.",
  "Only a hub that supports per-port power switching can cut power to a port. <b>The built-in hub of the Raspberry Pi 4 cannot.</b> Older models can at best switch the whole bus at once — which would take the keyboard and the hard disk with it."),
 ("K15",
  "Deshalb misst der Reiter <i>Test</i> nach: „Was kann dieses Gerät?“ zeigt genau die Verteiler, die den Strom wirklich schalten. Taucht dort keiner auf, ist Stufe 3 auf diesem Gerät wirkungslos — dann hilft nur ein externer Verteiler mit schaltbaren Anschlüssen.",
  "The <i>Test</i> tab therefore measures: „What can this machine do?“ lists exactly those hubs that really switch power. If none appears, stage 3 has no effect on this machine — then only an external hub with switchable ports helps."),
 ("K45", "Sechs Bremsen, und jede beantwortet eine andere Frage",
  "Six brakes, and each answers a different question"),
 ("K46",
  "Ein Wächter, der im Minutentakt zuschlägt, ist schlimmer als keiner. Deshalb:",
  "A watchdog that strikes every minute is worse than none. Therefore:"),
 ("K47",
  "<b>Erholung:</b> Nach einem Versuch braucht ein Zigbee-Netz ein bis zwei Minuten, bis alles zurück ist. So lange gilt der Stick als <b>gesund</b> — ohne das meldete jede Heilung eine Störung nach Loxone.",
  "<b>Recovery:</b> after an attempt a Zigbee network needs a minute or two to come back. For that long the dongle counts as <b>healthy</b> — without it every healing would report a fault to Loxone."),
 ("K48",
  "<b>Abstand</b> und <b>Versuche je Tag</b> begrenzen die Versuche: ein Stick, der wirklich kaputt ist, soll nicht im Minutentakt an- und abgeschaltet werden.",
  "<b>Interval</b> and <b>attempts per day</b> limit the attempts: a dongle that is truly broken should not be switched off and on every minute."),
 ("K49",
  "<b>Anlaufschonzeit:</b> Kurz nach einem Neustart ist jede Protokolldatei alt und jedes MQTT-Thema leer. Ohne diese Zeit startete der Wächter einen Dienst neu, der gerade selbst hochfährt.",
  "<b>Start-up grace period:</b> shortly after a reboot every log file is old and every MQTT topic empty. Without it the watchdog would restart a service that is still starting itself."),
 ("K50",
  "<b>Ruhefenster:</b> Ein Zeitfenster, in dem nur gemeldet wird — für den Fall, dass ein Container-Neustart nachts eine Türsprechanlage stumm machen würde.",
  "<b>Quiet window:</b> a time window in which the watchdog only reports — for cases where a container restart would silence a door intercom at night."),
 ("K51",
  "<b>Wartung:</b> Der Schalter für „ich stehe gerade am Gerät“ — und er geht <b>von selbst wieder aus</b>. Ein Schalter, den jemand von Hand setzt, wird vergessen.",
  "<b>Maintenance:</b> the switch for „I am standing at the device right now“ — and it <b>ends by itself</b>. A switch someone sets by hand gets forgotten."),
 ("K52",
  "<b>Nur melden:</b> der globale Schalter für einen Umbau. Er bleibt, bis ihn jemand zurücknimmt; die Oberfläche sagt das oben in einem Kasten, damit niemand lange sucht, warum nichts geschieht.",
  "<b>Report only:</b> the global switch for maintenance work. It stays until someone withdraws it; the interface says so in a box at the top, so that nobody searches long for why nothing happens."),
 ("K16", "Die Felder je Stick", "The fields per dongle"),
 ("K17",
  "Es zählt nur, was einen Namen hat. Und: <b>die Zeilennummer ist die Adresse</b> — Zeile 3 heißt in Loxone immer <span class='sm-mono'>G3…</span>, auch wenn Zeile 1 und 2 leer sind. Eine geleerte Zeile behält ihren Platz.",
  "Only rows with a name count. And: <b>the row number is the address</b> — row 3 is always <span class='sm-mono'>G3…</span> in Loxone, even if rows 1 and 2 are empty. A cleared row keeps its position."),
 ("K18",
  "<b>Woran erkennen / Pfad:</b> Bei „Datei“ der Pfad zur Protokolldatei, etwa <span class='sm-mono'>/opt/zigbee2mqtt/data/log/log.txt</span>. Bei „USB“ die Kennung wie <span class='sm-mono'>1-1.4</span>, bei „seriell“ die Gerätedatei, bei „HTTP“ die Adresse, bei den Diensten der Name der Einheit oder des Containers.",
  "<b>How to check / path:</b> for „file“ the path to the log file, for example <span class='sm-mono'>/opt/zigbee2mqtt/data/log/log.txt</span>. For „USB“ the identifier such as <span class='sm-mono'>1-1.4</span>, for „serial“ the device node, for „HTTP“ the address, for the services the name of the unit or container."),
 ("K19",
  "<b>Stumm bis:</b> Nach so vielen Sekunden ohne Lebenszeichen gilt der Stick als gestört. Großzügig ansetzen — ein Zigbee-Netz ohne Bewegung ist nachts still, ohne dass etwas kaputt wäre. Fünf Minuten sind ein vernünftiger Anfang, bei ruhigen Netzen eher fünfzehn.",
  "<b>Silent until:</b> after this many seconds without a sign of life the dongle counts as faulty. Be generous — a Zigbee network with nobody moving is quiet at night without anything being broken. Five minutes is a sensible start, fifteen for quiet networks."),
 ("K20",
  "<b>USB-Pfad, Verteiler und Anschluss</b> muss niemand mehr abtippen: Der Reiter <i>Test</i> listet mit „USB-Geräte auflisten“ alles auf, was am Bus hängt — samt Hersteller, Produkt, Gerätedatei und der Angabe, welche Geräte die Systemplatte tragen und deshalb gesperrt sind.",
  "<b>USB path, hub and port</b> no longer have to be typed by hand: the <i>Test</i> tab lists everything on the bus with „list USB devices“ — including vendor, product, device node and which devices carry the system disk and are therefore locked."),
 ("K21",
  "<b>Fertige Zeilen</b> für Zigbee2MQTT, Z-Wave JS, deCONZ und die übrigen bekannten Fälle stehen im Reiter <i>Einstellungen</i>. Ein Klick füllt die Zeile. <b>Diese Pfade sind Vorschläge, keine Messwerte</b> — deshalb steht neben jeder Zeile im Reiter Test ein Knopf „Jetzt messen“.",
  "<b>Ready-made rows</b> for Zigbee2MQTT, Z-Wave JS, deCONZ and the other common cases are in the <i>Settings</i> tab. One click fills the row. <b>These paths are suggestions, not measurements</b> — that is why the Test tab has a „measure now“ button next to every row."),
 ("K22",
  "<b>Dienst danach mitnehmen</b> und <b>Reihenfolge</b> gehören zusammen: das eine schickt den Dienstneustart hinter einen USB-Reset her, das andere dreht die Reihenfolge um, wenn der Dienstneustart allein nichts bringt.",
  "<b>Restart service afterwards</b> and <b>order</b> belong together: one sends the service restart after a USB reset, the other reverses the order when the service restart alone achieves nothing."),
 ("K53", "Das Heilen prüfen, ohne auf einen Ausfall zu warten",
  "Testing the healing without waiting for an outage"),
 ("K54",
  "Der Knopf <b>„Was würde jetzt geschehen?“</b> im Reiter <i>Test</i> druckt je Stick das gemessene Alter, das Urteil und den <b>vollständigen Befehl</b> aus, den die Funkwacht jetzt absetzen würde — ohne ihn abzusetzen. Auch die Ablehnung eines Systemgeräts steht dort, bevor sie im Ernstfall kommt.",
  "The button <b>„What would happen now?“</b> in the <i>Test</i> tab prints, per dongle, the measured age, the verdict and the <b>complete command</b> Funkwacht would issue now — without issuing it. The refusal of a system device is shown there too, before it happens in earnest."),
 ("K55",
  "Und wer es wirklich wissen will, drückt daneben <b>„… jetzt heilen“</b>. Das schaltet echt: ein Dienst startet wirklich neu, ein Anschluss verliert wirklich den Strom. Danach misst die Funkwacht noch einmal und zeigt, ob sich etwas gebessert hat. Dieser Versuch zählt nicht in die Stufenstatistik — er kam von Hand.",
  "And whoever really wants to know presses <b>„… heal now“</b> next to it. That really acts: a service really restarts, a port really loses power. Afterwards Funkwacht measures again and shows whether anything improved. This attempt does not count towards the per-stage statistics — it came by hand."),
 ("K23", "Was die Funkwacht niemals anfasst", "What Funkwacht never touches"),
 ("K24",
  "In jedem Durchlauf liest die Funkwacht <span class='sm-mono'>/proc/mounts</span> und ermittelt, welche USB-Geräte die Systemplatte und den Startbereich tragen. Wer von einer USB-SSD startet — und das tun viele LoxBerry-Installationen —, hätte sonst genau einen Tippfehler zwischen sich und einem abgehängten Wurzeldateisystem.",
  "On every pass Funkwacht reads <span class='sm-mono'>/proc/mounts</span> and works out which USB devices carry the system disk and the boot partition. Anyone booting from a USB SSD — and many LoxBerry installations do — would otherwise be exactly one typo away from an unmounted root file system."),
 ("K25",
  "Diese Geräte stehen im Reiter <i>Einstellungen</i> ausdrücklich als „nicht angefasst“ und in der USB-Liste des Reiters <i>Test</i> als gesperrt. Ein Heilversuch auf Stufe 2 oder 3 wird dort abgelehnt und im Protokoll vermerkt, auch wenn er ausdrücklich eingetragen wurde.",
  "These devices are listed explicitly as „left untouched“ in the <i>Settings</i> tab and as locked in the USB list of the <i>Test</i> tab. A healing attempt at stage 2 or 3 is refused there and noted in the log, even if it was configured deliberately."),
 ("K26", "Was nach Loxone geht", "What goes to Loxone"),
 ("K27",
  "Zwei Wege, beide gleichzeitig nutzbar: Das MQTT-Gateway von LoxBerry bekommt bei jedem Durchlauf die Werte, und der Miniserver kann die Adresse aus dem Reiter <i>Einbindung in Loxone</i> abfragen. <b>Beide tragen dieselben Werte</b> — nur geht über MQTT statt des Alters der Zeitstempel hinaus, denn ein Alter wäre beim Senden immer null. Dort stehen auch die Baustein-Listen der drei Seiten aus dem LoxBerry-Plugins Musterprojekt zum Nachbauen.",
  "Two routes, usable together: the LoxBerry MQTT gateway receives the values on every pass, and the Miniserver can poll the address from the <i>Loxone integration</i> tab. <b>Both carry the same values</b> — only over MQTT the timestamp goes out instead of the age, because an age would always be zero on sending. That tab also holds the block lists of the three pages from the LoxBerry plugins sample project for rebuilding them."),
 ("K28",
  "Nützlich ist vor allem <span class='sm-mono'>HEIL7T</span>: die Heilversuche der letzten sieben Tage. Steigt diese Zahl über Wochen langsam an, ist ein Stick am Ende seiner Kräfte, lange bevor er ganz ausfällt. Dasselbe zeigt das Balkenbild im Reiter <i>Logdateien</i>.",
  "The most useful value is <span class='sm-mono'>HEIL7T</span>: the recovery attempts of the last seven days. If this number slowly rises over weeks, a dongle is nearing the end of its life long before it fails completely. The bar chart in the <i>Log files</i> tab shows the same thing."),
 ("K56", "Zwei Befehle darf Loxone schicken", "Loxone may send two commands"),
 ("K57",
  "<span class='sm-mono'>quittieren</span> setzt Bremse und Eskalationsstand zurück — nützlich, wenn ein Stick auf „Tagesgrenze“ oder „keine Stufe mehr“ steht und jemand nachgesehen hat. <span class='sm-mono'>wartung</span> hält das Heilen für eine Weile an. Beide <b>schalten am Gerät nichts</b>: das eine erlaubt dem Wächter wieder zu urteilen, das andere hält ihn an.",
  "<span class='sm-mono'>quittieren</span> resets the brake and the escalation state — useful when a dongle sits at „daily limit“ or „no stage left“ and somebody has looked at it. <span class='sm-mono'>wartung</span> suspends healing for a while. Neither <b>switches anything on the device</b>: one allows the watchdog to judge again, the other stops it."),
 ("K58",
  "Beide gehen als Auftrag an den Wächter und wirken beim nächsten Durchlauf; die Antwort sagt, wie lange das höchstens dauert. Der Umweg hat einen Grund: die Datei mit den Zählern hat genau <b>einen</b> Schreiber, und das ist der Wächter — sonst wäre eine Änderung beim nächsten Durchlauf still überschrieben.",
  "Both are queued as a request to the watchdog and take effect at its next pass; the answer says how long that takes at most. The detour has a reason: the file with the counters has exactly <b>one</b> writer, and that is the watchdog — otherwise a change would be silently overwritten at the next pass."),
 ("K29", "Der Endpunkt hat keinen Heilbefehl",
  "The endpoint has no healing command"),
 ("K30",
  "Es gibt bewusst keinen Befehl, mit dem sich von außen ein USB-Anschluss zurücksetzen ließe.",
  "There is deliberately no command that would let a USB port be reset from outside."),
 ("K31",
  "Der Grund ist einfach: Das Wortzeichen steht in der Adresse und ist damit im Netzwerk sichtbar. Es schützt vor zufälligen Zugriffen, nicht vor einem Mithörer im gleichen Netz. Für eine Auskunft reicht das; für einen Hebel, der den USB-Bus des LoxBerry zurücksetzt, reicht es nicht.",
  "The reason is simple: the access word sits in the address and is therefore visible on the network. It protects against accidental access, not against someone listening on the same network. That is enough for a read-only answer; it is not enough for a lever that resets the LoxBerry USB bus."),
 ("K32", "Wenn nichts passiert", "When nothing happens"),
 ("K33",
  "Der häufigste Fall: Der Wächter läuft nicht. Die Kachel oben links sagt es, und im Reiter <i>Einstellungen</i> stehen drei Knöpfe, die ihn sofort starten, neu starten oder anhalten. Bleibt er stehen, steht der Grund im Reiter <i>Logdateien</i> unter „Ausgabe beim Start“.",
  "The most common case: the watchdog is not running. The tile at the top left says so, and the <i>Settings</i> tab has three buttons that start, restart or stop it immediately. If it stays down, the reason is in the <i>Log files</i> tab under „Output at start“."),
 ("K59",
  "Der zweithäufigste: Es fehlen die Rechte. Ohne die Datei <span class='sm-mono'>/etc/sudoers.d/funkwacht</span> darf der Wächter nur melden. Der Reiter <i>Test</i> sagt unter „Was kann dieses Gerät?“ für <b>jeden der vier Befehle einzeln</b>, ob er erlaubt ist.",
  "The second most common: permissions are missing. Without the file <span class='sm-mono'>/etc/sudoers.d/funkwacht</span> the watchdog can only report. Under „What can this machine do?“ the <i>Test</i> tab says for <b>each of the four commands separately</b> whether it is allowed."),
 ("K60",
  "Der dritte: eine Sperre. Läuft die Wartung, das Ruhefenster oder der Schalter „nur melden“, wird gemessen und gemeldet, aber nicht geheilt — die Oberfläche sagt es oben in einem Kasten, und die Selbstprüfung nennt es in der letzten Zeile. Ohne diesen Hinweis sucht man lange an der falschen Stelle.",
  "The third: a lock. While maintenance, the quiet window or the „report only“ switch is active, measuring and reporting continue but nothing is healed — the interface says so in a box at the top, and the self-check names it in its last line. Without that hint you search a long time in the wrong place."),
]

HILFE_KOPF_DE = """; Hilfetexte, deutsch. Gehoert zu templates/help/help.html.
;
; ERZEUGT von Werkzeuge/fw_sprache_erzeugen.py - NICHT von Hand aendern.
;
; LBWeb::gethelp() leitet den Namen dieser Datei aus dem Namen der
; Hilfedatei ab und sucht sie in templates/lang/ - nicht neben der
; Hilfe. Jeder Wert steht in doppelten Anfuehrungszeichen und enthaelt
; selbst keine; Auszeichnung bleibt roh, die Hilfe wird nicht
; maskiert ausgegeben.
"""

HILFE_KOPF_EN = """; Help texts, English. Belongs to templates/help/help.html.
;
; GENERATED by Werkzeuge/fw_sprache_erzeugen.py - do NOT edit by hand.
;
; LBWeb::gethelp() derives the name of this file from the name of the help
; file and looks for it in templates/lang/ - not next to the help file.
"""


KOPF_DE = """; Funkwacht - deutsche Texte
;
; ERZEUGT von Werkzeuge/fw_sprache_erzeugen.py - NICHT von Hand aendern.
; Wer hier etwas aendert, zieht den Erzeuger im selben Zug mit; sonst gibt es
; zwei Wahrheiten im selben Archiv, und die eine loescht die andere beim
; naechsten Lauf.
;
; ACHTUNG: Hier stehen ECHTE Umlaute, keine HTML-Entitaeten. Die Oberflaeche
; schickt die meisten Texte durch fw_e(); ein hier notiertes &uuml; erschiene
; beim Leser woertlich. Attribute in Auszeichnung werden EINFACH quotiert
; (class='sm-mono') - ein zweites doppeltes Anfuehrungszeichen beendet den
; Wert vorzeitig, und zwar still.
"""

KOPF_EN = """; Funkwacht - English texts
;
; GENERATED by Werkzeuge/fw_sprache_erzeugen.py - do NOT edit by hand.
; If you change something here, change the generator in the same go; otherwise
; there are two truths in the same archive, and one deletes the other on the
; next run.
;
; NOTE: real UTF-8 characters here, no HTML entities. Attributes in markup are
; quoted with SINGLE quotes - a second double quote would end the value early,
; and silently.
"""


def ansage_abschnitt(sprache):
    """Der Abschnitt [ANSAGE] der gemeinsamen Sprachausgabe - EINE Quelle:
    Werkzeuge/gemeinsam_pruefen.py baut ihn aus Werkzeuge/gemeinsam/
    sprachausgabe_texte.json (Schreibweise KEY="..." ohne Leerzeichen). Gesucht
    wird aufwaerts vom Ablageort dieses Erzeugers (wie au_sprache_erzeugen.py)."""
    for d in [Path(__file__).resolve().parent] + list(Path(__file__).resolve().parents):
        for w in (d, d / "Werkzeuge"):
            if (w / "gemeinsam_pruefen.py").is_file() and (w / "gemeinsam" / "sprachausgabe_texte.json").is_file():
                sys.path.insert(0, str(w))
                import gemeinsam_pruefen
                return gemeinsam_pruefen.ini_abschnitt(sprache)
    raise SystemExit("Werkzeuge/gemeinsam_pruefen.py nicht gefunden - es wurde nichts geschrieben.")


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
            zeilen.append('%s = "%s"' % (schluessel, wert))
    return zeilen


def main():
    ziel = Path(sys.argv[1]) if len(sys.argv) > 1 else VORGABE
    lang = ziel / "templates" / "lang"
    if not lang.is_dir():
        raise SystemExit("Kein Sprachordner: %s" % lang)

    # Dublettenprobe: derselbe Schluessel zweimal im selben Abschnitt wuerde
    # von parse_ini_file stillschweigend als der LETZTE gelesen. Genau daran
    # ist an anderer Stelle eine Ueberschrift zu einem langen Hinweistext
    # geworden.
    for abschnitt, paare in TEXTE:
        namen = [p[0] for p in paare]
        if len(namen) != len(set(namen)):
            doppelt = sorted(set(n for n in namen if namen.count(n) > 1))
            raise SystemExit("Doppelter Schluessel in [%s]: %s"
                             % (abschnitt, ", ".join(doppelt)))

    # Werkzeug-S2 (02.10.2026): erst ALLES bauen und pruefen, dann schreiben.
    # Bis dahin standen die language_*.ini schon auf der Platte, wenn die
    # Pruefung der Hilfe gegen help.html abbrach - ein abgebrochener Lauf hatte
    # also die halbe Arbeit getan (Fund 01.10. am Geschwister sm_). Jetzt
    # sammelt der Lauf die vier Inhalte in 'schreiben' und legt sie erst ab,
    # wenn keine Pruefung mehr abbrechen kann.
    schreiben = []
    for datei, kopf, index in (("language_de.ini", KOPF_DE, 1),
                               ("language_en.ini", KOPF_EN, 2)):
        # [ANSAGE] als letzter Abschnitt, durch eine Leerzeile getrennt
        # (Nachzug 1.0.12, 08.10.2026).
        text = (kopf + "\n".join(bauen(index)) + "\n\n"
                + ansage_abschnitt("de" if index == 1 else "en"))
        # LF seit der Hausregel vom 13.09.2026; bis dahin stand hier ein
        # replace("\n", "\r\n").
        schreiben.append((datei, text.encode("utf-8")))

    # --- Die Hilfe -----------------------------------------------------
    namen = [h[0] for h in HILFE]
    if len(namen) != len(set(namen)):
        raise SystemExit("Doppelter Hilfeschluessel")
    hilfe_html = (ziel / "templates" / "help" / "help.html")
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
                raise SystemExit("Gerades Anfuehrungszeichen in HILFE.%s" % eintrag[0])
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
    print("%d Schluessel in %d Abschnitten, beide Dateien geschrieben."
          % (n, len(TEXTE)))
    for datei in ("language_de.ini", "language_en.ini"):
        b = (lang / datei).read_bytes()
        crlf = b.count(b"\r\n")
        # An LF trennen: seit der LF-Umstellung (13.09.2026) ergab die Trennung
        # an CRLF die ganze Datei als EIN Stueck, und hier stand "1 Schluessel"
        # neben "517 Schluessel" (gemessen 24.09.2026).
        anzahl = sum(1 for z in b.decode("utf-8").split("\n") if " = " in z)
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
# ---- Gruppe 44 (Funkwacht 1.0.17): neue Schluessel (Pruefung-Durchgang-2026-09-29/vb_g44_fw_bau_skripte/sprache_g44.py) ----
def _g44():
    ab = {a: p for a, p in TEXTE}
    fm = ab["FW_MQTT"]
    i = [e[0] for e in fm].index("TS")
    fm.insert(i + 1, ("ZAEHLER", 'Lebenszeichen 0…999, je Durchgang eins weiter, nie zurückbehalten (Gateway V2: Noncached anhaken; Ausfallerkennung in Loxone)', 'sign of life 0…999, one up per pass, never retained (gateway V2: tick Noncached; failure detection in Loxone)'))
    vo = ab["VORL"]
    for j, e in enumerate(list(vo)):
        if e[0] == "Z2M_PAKET":
            vo[j] = ("Z2M_PAKET", 'Zigbee2MQTT oder Zigbee2MqttNG als Paket (Protokolldatei)', 'Zigbee2MQTT or Zigbee2MqttNG as a package (log file)')
        if e[0] == "Z2M_MQTT":
            vo[j] = ("Z2M_MQTT", 'Zigbee2MQTT oder Zigbee2MqttNG über MQTT (nur melden)', 'Zigbee2MQTT or Zigbee2MqttNG via MQTT (report only)')
    vo[:] = [e for e in vo if e[0] != "Z2MNG_MQTT"]
    TEXTE.extend([('BEFEHL', [('F_BRUECKE', 'Befehlsbrücke', 'Command bridge'), ('F_PRUEFEN', 'Befehlsbrücke: Einrichtung (--pruefen)', 'Command bridge: setup (--pruefen)'), ('T_PRUEFEN_OK', 'in Ordnung (Zuordnung, mosquitto_sub/_pub, Optionsdatei).', 'fine (mapping, mosquitto_sub/_pub, options file).'), ('H_ANNEHMEN', "Startet die Befehlsbrücke: Loxone sendet <span class='sm-mono'>publish funkwacht/befehl/&lt;name&gt; &lt;wert&gt;</span> an den Ausgang „LoxBerry MQTT-Gateway“, die Antwort steht unter <span class='sm-mono'>…/quittung</span> („angenommen“ heißt: an den Wächter übergeben, er führt es im nächsten Durchlauf aus). Beide Befehle schalten nichts: quittieren erlaubt dem Wächter, wieder selbst zu urteilen, Wartung hält das Heilen an. Wirkt nur mit eingeschaltetem MQTT. Ab Werk aus.", "Starts the command bridge: Loxone sends <span class='sm-mono'>publish funkwacht/befehl/&lt;name&gt; &lt;value&gt;</span> to the output “LoxBerry MQTT-Gateway”, the answer appears under <span class='sm-mono'>…/quittung</span> (“accepted” means: handed to the watchdog, it runs it in the next pass). Neither command switches anything: acknowledging lets the watchdog judge again by itself, maintenance pauses healing. Only works with MQTT switched on. Off by default."), ('H_ENDPUNKT', 'Die virtuellen HTTP-Eingänge und -Ausgänge mit Wortzeichen (Reiter Einbindung in Loxone). Neue Anlagen nehmen das MQTT-Gateway V2 und die Befehlsbrücke; ausgeschaltet antwortet der Endpunkt mit 403. Eine Anlage, die von einer Fassung vor 1.0.17 aktualisiert wurde, hat ihn an.', 'The virtual HTTP inputs and outputs with token (tab Loxone integration). New installations use the MQTT gateway V2 and the command bridge; switched off, the endpoint answers 403. An installation updated from a version before 1.0.17 has it on.'), ('H_STICKS', "Alle Sticks unter <span class='sm-mono'>…/befehl/quittieren</span>, ein Stick unter <span class='sm-mono'>…/befehl/&lt;n&gt;/quittieren</span> (n = Zeilennummer 1 bis 24 wie im Reiter Einstellungen). <span class='sm-mono'>…/befehl/wartung</span> nimmt Minuten von 0 bis 1440; 0 beendet die Wartung, dieselbe Dauer binnen 60 Sekunden gilt als unverändert.", "All sticks under <span class='sm-mono'>…/befehl/quittieren</span>, one stick under <span class='sm-mono'>…/befehl/&lt;n&gt;/quittieren</span> (n = row number 1 to 24 as in the Settings tab). <span class='sm-mono'>…/befehl/wartung</span> takes minutes from 0 to 1440; 0 ends maintenance, the same duration within 60 seconds counts as unchanged."), ('H_TITEL', 'Befehle aus Loxone über MQTT', 'Commands from Loxone via MQTT'), ('K_QUITTIEREN', 'Alle Sticks quittieren (Bremse zurücksetzen)', 'Acknowledge all sticks (reset the brake)'), ('K_QUITTIEREN_NR', 'Einen Stick quittieren', 'Acknowledge one stick'), ('K_WARTUNG', 'Wartung für so viele Minuten (0 = aus)', 'Maintenance for this many minutes (0 = off)'), ('K_VORLAGE', 'Vorlage Befehle über MQTT', 'Template commands via MQTT'), ('L_ANNEHMEN', 'Befehle über MQTT annehmen', 'Accept commands via MQTT'), ('L_ENDPUNKT', 'HTTP-Endpunkt für Loxone (bisheriger Weg)', 'HTTP endpoint for Loxone (previous way)'), ('M_SCHALTEN_FEHL', 'Die Befehlsbrücke ließ sich nicht schalten (%s): %s', 'The command bridge could not be switched (%s): %s'), ('STATUS_BEFEHLE', 'Lebenszeichen der Befehlsbrücke', 'Sign of life of the command bridge'), ('T_ART', 'Art', 'Type'), ('T_AUS', 'aus (Haken „Befehle über MQTT annehmen“ im Reiter MQTT nicht gesetzt).', 'off (box “Accept commands via MQTT” in the MQTT tab not ticked).'), ('T_DEFEKT', 'Die Einrichtung der Brücke ist fehlerhaft: %s', 'The bridge setup is faulty: %s'), ('T_ENDPUNKT_AUS', 'ausgeschaltet (Haken „HTTP-Endpunkt für Loxone“ im Reiter MQTT) – nicht aufgerufen.', 'switched off (box “HTTP endpoint for Loxone” in the MQTT tab) – not called.'), ('T_KEINER', 'Noch kein Befehl.', 'No command yet.'), ('T_LAEUFT', 'läuft (%d Prozess) – angenommen %d, abgelehnt %d.', 'running (%d process) – accepted %d, rejected %d.'), ('T_LETZTER', 'Letzter Befehl %s: %s, vor %d s.', 'Last command %s: %s, %d s ago.'), ('T_NICHT_DA', 'Die Befehlsbrücke (bin/befehlsbruecke.php) fehlt.', 'The command bridge (bin/befehlsbruecke.php) is missing.'), ('T_STEHT', 'soll laufen, steht aber (%s) – der Wächter startet sie binnen einer Minute neu.', 'should run but is stopped (%s) – the watchdog restarts it within a minute.'), ('T_TITEL', 'Titel in Loxone', 'Title in Loxone'), ('UDP_HINWEIS', 'Der UDP-Eingang des MQTT-Gateways (11884) nimmt im Heimnetz <b>ohne Anmeldung</b> an – jedes Gerät im WLAN kann einen Befehl schicken. Deshalb ist er ab Werk aus. Einen Heilbefehl gibt es auch über MQTT nicht.', 'The UDP input of the MQTT gateway (11884) accepts on the home network <b>without login</b> – every device on the Wi-Fi can send a command. That is why it is off by default. There is no healing command via MQTT either.')]), ('PRUEF', [('V2_FEHLT', 'Es fehlen: %s.', 'Missing: %s.'), ('V2_FRAGE', 'Gateway V2: sind alle Datenpunkte angehakt?', 'Gateway V2: are all data points ticked?'), ('V2_LEER', 'nicht feststellbar – die Themenliste des Wächters (bin/funkwacht_dienst.py) ist leer oder nicht lesbar.', 'cannot be determined – the topic list of the watchdog (bin/funkwacht_dienst.py) is empty or unreadable.'), ('V2_NC', 'Noncached falsch: %s.', 'Noncached wrong: %s.'), ('V2_NICHT_EINGERICHTET', 'noch nicht eingerichtet – angehakt wird, sobald Werte kommen (erst im Reiter Einstellungen eine Zeile ausfüllen).', 'not set up yet – tick them once values arrive (first fill in a row in the Settings tab).'), ('V2_UNKLAR', 'nicht feststellbar – die Gateway-Fassung oder die Subscriptions des Gateways lassen sich nicht lesen.', 'cannot be determined – the gateway version or the gateway subscriptions cannot be read.'), ('V2_V1', 'trifft nicht zu (Gateway V1 – dort gilt das Abo oben).', 'does not apply (gateway V1 – the subscription above applies there).'), ('V2_ZAHL', '%d von %d Datenpunkten angehakt.', '%d of %d data points ticked.')]), ('G44', [('H_V2', 'Datenpunkte für das MQTT-Gateway V2', 'Data points for the MQTT gateway V2'), ('V2_TEXT', "Im MQTT-Gateway V2 (LoxBerry, MQTT, Reiter Incoming Overview) diese Datenpunkte anhaken; in Loxone heißen die Virtuellen Eingänge wie die Spalte „Name in Loxone“. <b>Noncached</b> nur bei den Lebenszeichen (<span class='sm-mono'>ok</span>, <span class='sm-mono'>zaehler</span>, je Stick <span class='sm-mono'>ok</span>) und bei <span class='sm-mono'>status/befehle</span> – sonst käme ein unveränderter Wert nicht an und die Ausfallerkennung schlüge falsch an. Texte (Name, Grund, Bemerkung) und der Zeitstempel ts fehlen mit Absicht. Ohne eingetragene Zeile steht Stick 1 als Beispiel.", "Tick these data points in the MQTT gateway V2 (LoxBerry, MQTT, tab Incoming Overview); in Loxone the virtual inputs are named like the column “Name in Loxone”. <b>Noncached</b> only for the signs of life (<span class='sm-mono'>ok</span>, <span class='sm-mono'>zaehler</span>, per stick <span class='sm-mono'>ok</span>) and for <span class='sm-mono'>status/befehle</span> – otherwise an unchanged value would not arrive and failure detection would trip wrongly. Texts (name, reason, remark) and the timestamp ts are left out on purpose. Without a row entered, stick 1 is shown as an example."), ('V2_NUR_V1', 'Dieses Gateway ist Fassung V1 – es leitet alles unter dem Abo oben weiter; anzuhaken gibt es nichts.', 'This gateway is version V1 – it forwards everything under the subscription above; there is nothing to tick.'), ('T_NAME', 'Name in Loxone', 'Name in Loxone'), ('KACHEL_EIN', 'ein', 'on'), ('KACHEL_AUS', 'aus', 'off'), ('KACHEL_HILFE', 'Veröffentlichung dieses Plugins; Autostart des Gateways: %s; Gateway-Fassung: %s', 'Publishing of this plugin; gateway autostart: %s; gateway version: %s'), ('Z_KOPF', 'Zigbee-Dienst:', 'Zigbee service:'), ('Z_ERKANNT', 'erkannt %s (Plugin Zigbee2MqttNG in der Plugin-Datenbank: %s; systemd zigbee2mqttng.service: %s).', 'detected %s (plugin Zigbee2MqttNG in the plugin database: %s; systemd zigbee2mqttng.service: %s).'), ('Z_UNLESBAR', 'nicht lesbar', 'unreadable'), ('Z_HINWEIS', "Die beiden Zigbee2MQTT-Vorlagen setzen <span class='sm-mono'>zigbee2mqttng</span>, wenn Zigbee2MqttNG installiert ist, sonst <span class='sm-mono'>zigbee2mqtt</span>. Der Pfad der Protokolldatei unter Zigbee2MqttNG folgt dem Original und ist noch nicht am Gerät gemessen – bitte mit „Jetzt messen“ prüfen; ein falscher Pfad heilt nicht („nie gesehen“). Eine schon gespeicherte Zeile bleibt, wie sie ist.", "Both Zigbee2MQTT templates set <span class='sm-mono'>zigbee2mqttng</span> when Zigbee2MqttNG is installed, otherwise <span class='sm-mono'>zigbee2mqtt</span>. The log file path under Zigbee2MqttNG follows the original and has not been measured on a device yet – please check it with “measure now”; a wrong path does not heal (“never seen”). A row that is already saved stays as it is."), ('H_LOG_BRUECKE', 'Startprotokoll der Befehlsbrücke', 'Start log of the command bridge'), ('H_LOG_CRON', 'Fehlerausgabe des Minutentakts (cron.err)', 'Error output of the minute timer (cron.err)')])])
    HILFE.extend([('K61', 'Hausform seit 1.0.17: Gateway V2, Befehle über MQTT, Healthcheck', 'House form since 1.0.17: gateway V2, commands via MQTT, health check'), ('K62', "Die Werte gehen wie bisher über den UDP-Eingang des MQTT-Gateways. Neu ist das Lebenszeichen <span class='sm-mono'>funkwacht/zaehler</span> (0…999, je Durchgang eins weiter); im Reiter <i>MQTT</i> steht die Tabelle der Datenpunkte für das Gateway V2 mit dem Namen, den der Virtuelle Eingang in Loxone trägt, und mit dem Haken Noncached. Quittieren und Wartung nimmt ab 1.0.17 auch die Befehlsbrücke an (Haken „Befehle über MQTT annehmen“, ab Werk aus); der HTTP-Endpunkt hat einen eigenen Schalter – nach einem Update bleibt er an, eine Neuinstallation hat ihn aus. Der LoxBerry-Healthcheck sagt, ob der Wächter misst und wie alt seine Messung ist.", "Values go out via the UDP input of the MQTT gateway as before. New is the sign of life <span class='sm-mono'>funkwacht/zaehler</span> (0…999, one up per pass); the <i>MQTT</i> tab lists the data points for the gateway V2 with the name the virtual input carries in Loxone and with the Noncached box. From 1.0.17 the command bridge also accepts acknowledge and maintenance (box “Accept commands via MQTT”, off by default); the HTTP endpoint has its own switch – it stays on after an update, a new installation has it off. The LoxBerry health check tells whether the watchdog measures and how old its measurement is."), ('K63', "Zigbee: die Vorlagen „Zigbee2MQTT oder Zigbee2MqttNG“ setzen den Dienst <span class='sm-mono'>zigbee2mqttng</span>, wenn das Plugin Zigbee2MqttNG installiert ist, sonst <span class='sm-mono'>zigbee2mqtt</span>. Eine gespeicherte Zeile ändert sich dadurch nicht – wer von Zigbee2MQTT auf Zigbee2MqttNG umgestiegen ist, setzt die Vorlage einmal neu ein oder trägt den Dienst von Hand ein.", "Zigbee: the templates “Zigbee2MQTT or Zigbee2MqttNG” set the service <span class='sm-mono'>zigbee2mqttng</span> when the plugin Zigbee2MqttNG is installed, otherwise <span class='sm-mono'>zigbee2mqtt</span>. A saved row does not change by this – whoever moved from Zigbee2MQTT to Zigbee2MqttNG inserts the template once more or enters the service by hand.")])


_g44()


# ---- Nachzug 01.11.2026 auf Funkwacht 1.0.18 (veroeffentlicht 31.10.) ----
# Werte aus den veroeffentlichten language_*.ini / help_*.ini uebernommen - die Datei gilt.
# Diese drei Stellen waren nach Gruppe 44 direkt in die .ini geschrieben worden
# (Mehrfachziele-Welle, Sprachmodul 1.2.1); ohne sie wies der Erzeuger ab (K64)
# bzw. haette die sprachwache EINST.SICH_SPAET verschwinden sehen.
def _nachzug_1018():
    ab = {a: p for a, p in TEXTE}
    ab["EINST"].append(('SICH_SPAET', 'Nicht in der Sicherung, unverändert: %s (die Sicherung stammt aus einer früheren Fassung).', 'Not in the backup, unchanged: %s (the backup comes from an earlier version).'))
    g = ab["G44"]
    for j, e in enumerate(list(g)):
        if e[0] == 'Z_HINWEIS':
            g[j] = ('Z_HINWEIS', "Die beiden Zigbee2MQTT-Vorlagen setzen <span class='sm-mono'>zigbee2mqttng</span>, wenn Zigbee2MqttNG installiert ist, sonst <span class='sm-mono'>zigbee2mqtt</span>. Den Pfad der Protokolldatei liest die Paket-Vorlage aus <span class='sm-mono'>data/configuration.yaml</span> des Dienstes (<span class='sm-mono'>log_directory</span>, <span class='sm-mono'>log_file</span>; mit Zeitstempel-Platzhalter das jüngste Verzeichnis) – bitte trotzdem mit „Jetzt messen“ prüfen; ein falscher Pfad heilt nicht („nie gesehen“). Ein Verzeichnis mit Zeitstempel wechselt bei jedem Neustart des Dienstes, dann die Vorlage neu setzen. Eine schon gespeicherte Zeile bleibt, wie sie ist.", "Both Zigbee2MQTT templates set <span class='sm-mono'>zigbee2mqttng</span> when Zigbee2MqttNG is installed, otherwise <span class='sm-mono'>zigbee2mqtt</span>. The package template reads the log file path from the service’s <span class='sm-mono'>data/configuration.yaml</span> (<span class='sm-mono'>log_directory</span>, <span class='sm-mono'>log_file</span>; with a timestamp placeholder the newest directory) – please still check it with “measure now”; a wrong path does not heal (“never seen”). A directory with a timestamp changes with every restart of the service, then set the template again. A row that is already saved stays as it is.")
    HILFE.append(('K64', '<b>Mehrere Lautsprecher gleichzeitig</b> (seit 1.0.17, Sprachmodul 1.2.1): Unter der Ausgabeart (jetzt „Ziel 1“) steht die Tabelle <i>Weitere Ausgabeziele (gleichzeitig)</i> – bis zu 6 Ziele insgesamt, zum Beispiel Loxone Music Server, Google-Lautsprecher (Chromecast 4 Lox NG) und Amazon Echo (Alexa-NG). Jede Ansage geht gleichzeitig an Ziel 1 und an jedes eingeschaltete Ziel der Tabelle; scheitert eines, sprechen die anderen trotzdem, und die Ansage gilt als gesendet, sobald eines gesprochen hat (Protokoll und Reiter Test nennen jedes Ziel). Ist Ziel 1 aus, spricht keines; mit dem Original-Audioserver als Ziel 1 gehen keine weiteren Ziele. Neues Ziel: die leere Zeile ausfüllen und speichern. Mehrere Zonen desselben Music Servers bzw. mehrere Echos gehören in EIN Ziel (Zonenliste, Kommaliste, gruppe:&lt;Name&gt;). Das Sprechtoken steht einmal oben und gilt für alle Ziele dieser Art. Im Reiter Test spricht <i>Testansage</i> an alle Ziele, <i>Testansage an Ziel n</i> nur an dieses. Vor einem Zurückgehen auf eine Fassung vor 1.0.17 die weiteren Ziele entfernen – ältere Fassungen kennen die Liste nicht und fielen beim Laden auf die Werkseinstellung der Sprachausgabe zurück.', '<b>Several speakers at once</b> (since 1.0.17, speech module 1.2.1): below the output type (now “target 1”) the table <i>Further outputs (simultaneous)</i> takes up to 6 targets in total, for example Loxone Music Server, Google speakers (Chromecast 4 Lox NG) and Amazon Echo (Alexa-NG). Every announcement goes to target 1 and to every enabled target of the table at the same time; if one fails the others still speak, and the announcement counts as sent as soon as one has spoken (the log and the Test tab name every target). If target 1 is off, none speaks; the original Audio Server as target 1 cannot be combined with further targets. New target: fill in the empty row and save. Several zones of the same Music Server or several Echos belong in ONE target (zone list, comma list, gruppe:&lt;name&gt;). The speech token is entered once above and applies to all targets of that kind. In the Test tab <i>Test announcement</i> speaks to all targets, <i>Test announcement to target n</i> only to that one. Before going back to a version older than 1.0.17 remove the further targets – older versions do not know the list and would fall back to the factory settings of the speech output.'))


_nachzug_1018()

import sprachwache
sprachwache.einhaengen()


if __name__ == "__main__":
    raise SystemExit(main())
