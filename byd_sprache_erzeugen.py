#!/usr/bin/env python3
"""Erzeugt die Sprachdateien des Plugins BYD Autos.

Warum erzeugt und nicht von Hand gepflegt: beim Handpflegen bleiben drei
Fehlerklassen unsichtbar, die in dieser Reihe alle schon aufgetreten sind.

1. Doppelte Maskierung. Ein Text, der durch by_e() laeuft und selbst eine
   HTML-Entitaet oder Auszeichnung enthaelt, erscheint im Browser woertlich
   als "pr&amp;uuml;fen". Der Befund hat 40 Fundstellen in 13 Plugins gehabt.
   Dieses Skript liest aus dem PHP, welche Schluessel maskiert ausgegeben
   werden, und laesst dort weder Auszeichnung noch Entitaet zu.

2. Gerade Anfuehrungszeichen im Wert. Ein Wert steht in "..."; ein weiteres "
   darin beendet ihn vorzeitig. Was dann geschieht, haengt vom Lesemodus ab
   und ist IN JEDEM FALL STUMM - im Standardmodus wird der Wert abgeschnitten
   oder die GANZE Datei abgewiesen, mit INI_SCANNER_RAW faellt gar nichts auf.
   Gemessen kamen an einer Linie 780 von 1464 Zeichen an, und die englische
   Datei fiel ganz aus.

3. Platzhalter, die zwischen den Sprachen auseinanderlaufen. Ein sprintf, dem
   in einer Sprache ein %s fehlt, gibt dort einen abgeschnittenen Satz aus -
   und das faellt in der Sprache auf, die niemand einstellt.

STAND (vb_x10_byd, 09.10.2026, Welle X-10 / Sprachmodul 1.1.2): EINST.SICH_TTS_EINTRAG
entfaellt (Satz K_TTS_EINTRAG kommt mit Modul 1.1.2, wortgleich). [ANSAGE] wie immer aus
Werkzeuge/gemeinsam/sprachausgabe_texte.json (157 Schluessel).

STAND (vb_bild_by17, 17.10.2026, Welle Bild 17 / Musterprojekt, Vollausstattung): Reiter "Einbindung in
Loxone" auf vier Seiten aus dem Musterprojekt (Entwurf Welle 17 by, E13): die alte Liste [BAUSTEIN] (41
Schluessel) und LOX.S8_ERLAEUTERUNG entfallen; neu 170 Schluessel (BAUSTEIN.* Kasten- und Hinweistitel, Kaesten,
Hinweise, 115 Tabellenzeilen Z1_01..Z4_22; LOX.* Bild, Link, Vorlage-Knoepfe je Fahrzeug, zweiter Haken;
EINST.L_/H_GEFAHR_EIN und TEST.* fuer den zweiten Haken, Hausherr 17.10.2026); neu gefasst LOX.EINLEITUNG, LOX.S1_TEXT, LOX.S5_TEXT, LOX.S7_TEXT, LOX.S8_TITEL, LOX.S8_TEXT, EINST.STEUERUNG_ERKLAERUNG.

STAND (vb_g1_tz_by, 18.10.2026, Gruppe 1 / Textnachzug): BAUSTEIN.Z2_06 (Seite "BYD Autos Laden und Klima" #6) neu
gefasst - Typ Virtueller Eingang (Gateway-Name), Name spot_awattar_rank (Spotpreis aWATTar liefert die Werte jetzt ueber
MQTT); dazu Kasten/Hinweise S2_H2, S2_SCHRITT2 mit den neuen
Namen und der Herkunft der Vorlage (ab Spotpreis aWATTar 1.2.38). Sonst unveraendert.

STAND (vb_by28, 20.10.2026, BYD Autos 0.9.28 / Reifendruecke immer in bar, Issue #1): BY_FELD.REIFENEH nennt die
Kennungen (1 = bar, 2 = psi, 3 = kPa) und dass das Plugin umrechnet; BAUSTEIN.S4_H3 (Seite "BYD Autos Werte") sagt
statt "an einem Fahrzeug in bar gehalten" jetzt "immer in bar, das Plugin rechnet um, -1 = unplausibel". Je de und en.
Sonst unveraendert.

STAND (Drift-Abgleich, 06.11.2026): angeglichen an BYD Autos 0.9.36, 134 Schluessel neu (je de
und en; Abschnitte BEFEHL, G42, HAUS, PRUEF, SIGNAL und Einzelne in ALLG, BY_ANSAGE, BY_FELD,
BY_MQTT, EINST, LADUNG - Block DRIFT-ABGLEICH am Ende von DE und EN), 4 Werte geaendert
(BAUSTEIN.S1_H5, EINST.ANSAGE_ERKLAERUNG, EINST.H_ANSAGE: Sprachausgabe ab Werk an;
MQTT.RETAIN_ERKLAERUNG), 0 entfernt. Neu in KEINE_SCHLUESSEL: BEFEHL.K_X (Attrappe der Selbst-
pruefung in bin/befehlsbruecke.php). OFFEN: der Erzeuger sortiert je Abschnitt (ini_schreiben,
sorted()); die .ini von 0.9.36 fuehrt [EINST] (12 Bruchstellen), [BY_ANSAGE] und [G42] (je 1)
nicht alphabetisch. Schluessel, Werte und Bytezahl sind gleich, nur die Folge nicht.

Aufruf:  byd_sprache_erzeugen.py <pluginordner> [--pruefen]

Geschrieben wird nur, wenn alle Pruefungen bestehen. Ein Erzeuger, der im
Zweifel die Haelfte schreibt, kostet die Sprachausgabe.
"""

# NACHGEZOGEN (Sprachausgabe BYD Autos 0.9.23, Nr. 36 b, vb_sp2b_bau_skripte/byd/werkzeug_bauen.py): 24 neue Schluessel (de und en); die Abschrift
# sprachausgabe.php zaehlt nicht als Code der Linie, und der Abschnitt [ANSAGE] kommt aus
# Werkzeuge/gemeinsam/sprachausgabe_texte.json (gemeinsam_pruefen.ini_abschnitt()).
# Werkzeuge/ selbst ist unveraendert.
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Deutsch
#
# Umlaute als direkte UTF-8-Zeichen, keine Entitaeten - das beseitigt die
# Doppelmaskierung als Fehlerklasse. Entitaeten stehen nur dort, wo der Wert
# ROH ausgegeben wird und ein typografisches Zeichen gebraucht ist.
# HTML-Attribute werden EINFACH quotiert (class='sm-mono').
# ---------------------------------------------------------------------------
DE = {
# ---- Sprachausgabe (Nr. 36 b) ----
"EINST.H_ANSAGE": "Sprachausgabe (Ansagen, ab Werk an)",
"EINST.ANSAGE_ERKLAERUNG": "Das Plugin kann einzelne Ereignisse ansagen – über den Loxone Music Server, MusicServer4Home, eine eigene Adressvorlage, Alexa-NG oder Google-Lautsprecher (Chromecast 4 Lox NG). Ab Werk ist die Ausgabe <b>an</b>. Angesagt wird nur ein Wechsel, nie ein Wert im Takt; derselbe Anlass wird für dasselbe Fahrzeug höchstens einmal je eingestellter Sperrzeit, in der Nachtruhe nicht angesagt, und nach einem Neustart des Dienstes spricht die erste Abfrage nie. MQTT, Loxone und Benachrichtigungen bleiben davon unberührt. Adresse und Vorlage müssen im Heimnetz liegen.",
"EINST.H_ANSAGE_ANLAESSE": "Anlässe",
"EINST.L_ANSAGE_LADEN_FERTIG": "Ladung beendet (mit Ladestand)",
"EINST.L_ANSAGE_AUSFALL": "Keine Daten mehr (drei Abrufe in Folge gescheitert)",
"EINST.H_ANSAGE_ANLAESSE_HILFE": "Jeder Anlass lässt sich einzeln abwählen; er wirkt erst, wenn oben eine Ausgabeart gewählt ist. Türen, Schloss, Licht und Klimatisierung werden nicht angesagt: BYD liefert Türen und Schloss nur als gerätespezifische Rohwerte, Licht und Klimatisierung gar nicht. Die Testansage steht im Reiter <i>Test</i>.",
"EINST.SICH_TTS_TOKEN": "Die Datei trägt ein Sprechtoken (%s). Eine Sicherung dieses Plugins enthält nie eines – die Datei wird abgewiesen, das geltende Token bleibt.",
"EINST.SICH_TTS": "Unzulässiger Wert in der Sprachausgabe (tts): %s",
"EINST.SICH_OHNE_ANSAGE": "Die Sicherung stammt aus einer Fassung vor 0.9.23 und kennt die Sprachausgabe noch nicht – deren Einstellungen bleiben, wie sie sind.",
"EINST.SICH_OHNE_SPRECHTOKEN": "Die Sprechtoken der Sprachausgabe (Alexa-NG, Chromecast 4 Lox NG) stehen nie in der Sicherung; nach dem Zurückspielen auf einer neuen Anlage dort neu eintragen.",
"TEST.F_ANSAGE": "Sprachausgabe",
"TEST.A_ANSAGE_ANLAESSE": "Eingeschaltete Anlässe (%s): %s.",
"TEST.A_ANSAGE_KEINE": "keiner",
"TEST.H_ANSAGE": "Sprachausgabe",
"TEST.ANSAGE_TEST_TEXT": "Spricht den Prüfsatz über die eingestellte Ausgabeart – unabhängig von den Anlässen.",
"TEST.K_ANSAGE_TEST": "Testansage",
"TEST.M_ANSAGE_TEST_OK": "Testansage gesendet.",
"TEST.M_ANSAGE_TEST_NICHTS": "Keine Testansage: %s",
"TEST.M_ANSAGE_TEST_FEHL": "Testansage nicht gesendet: %s",
"BY_ANSAGE.FAHRZEUG_NR": "Fahrzeug %s",
"BY_ANSAGE.S_LADEN_FERTIG": "%s: Die Ladung ist beendet.",
"BY_ANSAGE.S_LADESTAND": "Ladestand %s Prozent.",
"BY_ANSAGE.S_AUSFALL": "BYD: Seit drei Abrufen kommen keine Daten mehr.",

# ---- Verbesserungsbau 30.09.2026 (vb_byd: BYD-b1, BYD-b2, X-2, X-3, Laden-1) ----
"LADUNG.K_CSV": "Ladevorgänge herunterladen (CSV)",
"LADUNG.H_CSV": "Lädt <b>alle</b> aufgezeichneten Ladevorgänge als Tabelle herunter, der älteste zuerst: Fahrzeug, Beginn, Ende, Dauer in Minuten, Ladezustand vorher und nachher, Kilometerstand, geladene kWh. Trennzeichen Semikolon, Dezimalpunkt; ein leeres Feld heißt <i>nicht bekannt</i>. Ohne Ladevorgang enthält die Datei nur die Kopfzeile. Der Knopf verändert nichts.",
"EINST.SICH_KOPF_HINWEIS": "Sicherung der Einstellungen des Plugins BYD Autos. Enthält das Aktionstoken sowie Benutzername, Passwort, Steuer-PIN und Land des BYD-Kontos - wie ein Passwort behandeln. Zurückspielen im Reiter Einstellungen; Schlüssel, die mit _ beginnen, werden dabei übergangen.",
"EINST.SICH_ALTWERT": "<b>Diese Sicherung ließe sich so nicht zurückspielen.</b> Der gespeicherte Wert von %s würde beim Zurückspielen abgewiesen (dieselbe Prüfung wie dort). Die Datei wird trotzdem vollständig geliefert und nennt es in ihrem Kopf. Berichtigen Sie den Wert oben im Formular, speichern Sie und sichern Sie danach erneut.",
"EINST.SICH_ALTWERT_KOPF": "Diese Sicherung ließe sich so nicht zurückspielen - abgewiesen würde: %s. Den Wert in der Oberfläche berichtigen, speichern und erneut sichern.",
"EINST.EINGABEN_ZURUECK": "Die Felder dieses Formulars zeigen Ihre Eingaben - gespeichert wurde nichts. Das rot umrandete Feld ist beanstandet; nach dem Berichtigen bitte erneut speichern. Passwort und Steuer-PIN werden aus Sicherheitsgründen nicht wieder eingesetzt: ein eben eingetipptes Passwort ist nicht übernommen und muss noch einmal eingegeben werden.",
"EINST.H_PREISEMPF": "Ladeempfehlung aus Spotpreis aWATTar oder Tibber",
"EINST.PREISEMPF_ERKLAERUNG": "Das Plugin hört den <b>Rang der laufenden Stunde</b> bei einem der beiden Spotpreis-Plugins mit (1 = günstigste der nächsten 24 Stunden) und sendet über MQTT <code>lade_empfehlung</code>: 1, wenn die Stunde zu den eingestellten günstigsten Stunden gehört, sonst 0, dazu <code>lade_empfehlung_grund</code>. Schweigt die Quelle oder fehlt ein Rang, geht <code>-</code> hinaus, und der Reiter Test zeigt es gelb. Es <b>schaltet nichts</b> am Auto. Voraussetzung: das Spotpreis-Plugin sendet über MQTT (dort im Reiter MQTT eingeschaltet). Nach einem Start des Dienstes kommt der erste Rang erst mit dem nächsten vollen Satz der Quelle - bei aWATTar spätestens nach 30 Minuten, bei Tibber mit der nächsten Stunde.",
"EINST.L_PREISEMPF_EIN": "Ladeempfehlung nach Strompreis senden",
"EINST.L_PREISEMPF_QUELLE": "Preisquelle",
"EINST.O_PREISEMPF_AWATTAR": "Spotpreis aWATTar",
"EINST.O_PREISEMPF_TIBBER": "Spotpreis Tibber",
"EINST.H_PREISEMPF_QUELLE": "Auswahlfeld: welches Spotpreis-Plugin den Rang liefert. Beide sind auf diesem LoxBerry als Plugin zu installieren; gelesen werden nur ihre MQTT-Themen, nie ihre Dateien.",
"EINST.L_PREISEMPF_PRAEFIX": "MQTT-Präfix der Preisquelle",
"EINST.H_PREISEMPF_PRAEFIX": "Leer lassen, solange das Spotpreis-Plugin seinen Vorgabepräfix benutzt (aWATTar <code>spot_awattar</code>, Tibber <code>tibber</code>). Wer ihn dort im Reiter MQTT geändert hat, trägt ihn hier genauso ein. Gelesen werden <code>&lt;präfix&gt;/rank</code>, <code>/rankd</code> und das Lebenszeichen <code>/status/…</code>.",
"EINST.L_PREISEMPF_STUNDEN": "Günstigste Stunden je 24 Stunden",
"EINST.H_PREISEMPF_STUNDEN": "Von 1 bis 12. Die Empfehlung ist 1, wenn der Rang der laufenden Stunde höchstens diese Zahl ist - also in den soundso vielen günstigsten Stunden der nächsten 24 Stunden liegt. Liegen nur wenige Stunden vor (vor der Veröffentlichung der Preise für morgen), zählt die kürzere Rangfolge.",
"EINST.FEHLER_PREISEMPF_QUELLE": "Preisquelle: erlaubt sind Spotpreis aWATTar und Spotpreis Tibber. Die bisherige Auswahl bleibt.",
"EINST.SICH_R_QUELLE": "die Preisquelle ist awattar oder tibber.",
"BY_MQTT.LADE_EMPFEHLUNG": "Nur bei eingeschalteter Ladeempfehlung nach Strompreis: 1 = die laufende Stunde gehört zu den eingestellten günstigsten Stunden, 0 = nicht, - = keine Aussage (Preisquelle schweigt, kein Rang, Dienst beendet oder die Einstellung eben ausgeschaltet). Gesendet bei jeder Änderung und sonst alle 5 Minuten.",
"BY_MQTT.LADE_EMPFEHLUNG_GRUND": "Kennwort zur Empfehlung: GUENSTIG, TEUER, QUELLE_SCHWEIGT, QUELLE_OHNE_PREISE, KEIN_RANG, HORCHER (keine Verbindung zum Broker), AUS, DIENST_AUS. Text, kein virtueller Eingang.",
"TEST.F_PREISEMPF": "Kommt die Ladeempfehlung nach Strompreis an?",
"TEST.A_PREISEMPF_AUS": "sie ist ausgeschaltet - es wird kein Thema gesendet",
"TEST.A_PREISEMPF_KEIN_DIENST": "eingeschaltet, aber der Abrufdienst läuft nicht - gerechnet wird nur im Dienst. Es gibt keine Empfehlung.",
"TEST.A_PREISEMPF_NOCH_NICHTS": "eingeschaltet, aber der Dienst hat noch keinen Stand abgelegt (er rechnet alle 30 Sekunden). Seite in einer Minute neu laden.",
"TEST.A_PREISEMPF_OK": "ja: Empfehlung %d - Rang %d von %d, Grenze %d (Quelle %s, Themen <code>%s/rank</code>)",
"TEST.A_PREISEMPF_OHNE": "keine Aussage von %s (Themen <code>%s/…</code>): %s Gesendet wird <code>-</code> - es gibt keine Empfehlung, wie ohne diese Einstellung.",
"TEST.A_PREISEMPF_OHNE_MQTT": "MQTT ist im Reiter MQTT ausgeschaltet - gerechnet wird, gesendet nicht.",
"TEST.PREIS_G_HORCHER": "keine Verbindung zum Broker (siehe die Zeile zu den fremden MQTT-Themen).",
"TEST.PREIS_G_QUELLE_SCHWEIGT": "seit über 5 Minuten kein Lebenszeichen. Ist das Spotpreis-Plugin installiert, sendet es über MQTT, und stimmt der Präfix?",
"TEST.PREIS_G_QUELLE_OHNE_PREISE": "die Quelle lebt, meldet aber status/ok = 0 - sie hat keine Preise für heute.",
"TEST.PREIS_G_KEIN_RANG": "die Quelle lebt, aber seit über 65 Minuten kam kein Rang. Nach einem Start des Dienstes ist das bis zum nächsten vollen Satz der Quelle normal.",
"TEST.PREIS_G_ANLAUF": "eben eingeschaltet, gestartet oder die Quelle gewechselt - das erste Lebenszeichen der Quelle steht noch aus (bis 2 Minuten).",

# ---- Reiter und Legende ----------------------------------------------------
"REITER.EINSTELLUNGEN": "Einstellungen",
"REITER.LOXONE": "Einbindung in Loxone",
"REITER.TEST": "Test",
"REITER.LOG": "Logdateien",

"LEGENDE.LESEN": "Ansehen — fragt nur ab, verändert nichts",
"LEGENDE.TECHNIK": "Technische Auskunft — für die Fehlersuche",
"LEGENDE.AKTION": "Löst etwas aus — sendet oder verändert",
"LEGENDE.AKTION_TOKEN": "Löst etwas aus — ein neues Token macht alle Adressen im Miniserver ungültig",
"LEGENDE.AKTION_LOG": "Löst etwas aus — die bisherigen Zeilen sind danach fort",

# ---- Allgemein -------------------------------------------------------------
"ALLG.BEANSTANDUNG": "Bitte diese Punkte berichtigen:",
"ALLG.FEHLER_FORMTOKEN": "Das Formular trug kein gültiges Merkmal dieser Sitzung. Es wurde nichts geändert. Bitte die Seite neu laden und noch einmal absenden. Steht noch kein Aktionstoken in der Konfiguration, entsteht es beim ersten Aufruf dieser Seite — dann genügt ein Neuladen.",
"ALLG.FEHLER_FORMULAR": "Das Formular hat sich nicht zu erkennen gegeben. Es wurde nichts geändert — ein falsch geratenes Formular löscht sonst genau das, was behalten werden sollte.",
"ALLG.DIENST": "Abrufdienst",
"ALLG.LAEUFT": "läuft",
"ALLG.GESTOPPT": "gestoppt",
"ALLG.KEINE_PID": "keine Prozessnummer",
"ALLG.LETZTER_ABRUF": "Letzter Abruf",
"ALLG.NIE": "noch nie",
"ALLG.FAHRZEUGE": "Fahrzeuge",
"ALLG.FAHRZEUG": "Fahrzeug",
"ALLG.LIB_FEHLT": "Bibliothek fehlt",
"ALLG.SELBSTPRUEFUNG": "Selbstprüfung",
"ALLG.HINWEISE": "dazu %d Hinweise",
"ALLG.LETZTE_STOERUNG": "Letzte Störung:",
"ALLG.OHNE_NAMEN": "ohne Modellangabe",
"ALLG.SOC": "Ladezustand",
"ALLG.REICHWEITE": "Reichweite",
"ALLG.KM": "Kilometerstand",
"ALLG.VERLAUF_HINWEIS": "Ladezustand des heutigen Tages. Ein Messpunkt höchstens alle vier Minuten.",
"ALLG.OHNE_TREFFER": "Felder ohne Treffer:",
"ALLG.OHNE_TREFFER_HINWEIS": "Diese Felder bleiben leer, weil die Antwort der Bibliothek keinen der hinterlegten Namen enthielt. Der Knopf <b>Feldzuordnung vorschlagen</b> im Reiter Test zeigt, wie die Felder in dieser Fassung wirklich heißen.",
"ALLG.AUSFAELLE": "Abrufe, die dieses Fahrzeug nicht beantwortet hat:",
"ALLG.EIGENSCHAFT": "Eigenschaft",
"ALLG.WERT": "Wert",
"ALLG.SEKUNDEN": "Sekunden",
"ALLG.SPEICHERN": "Speichern",
"ALLG.EIN": "ein",
"ALLG.AUS": "aus",
"ALLG.JA": "ja",
"ALLG.NEIN": "nein",

# ---- Einstellungen ---------------------------------------------------------
"EINST.UNGEPRUEFT": "<b>Diese Fassung ist ungeprüft.</b> Das Plugin wurde ohne BYD-Konto und ohne Fahrzeug gebaut. BYD veröffentlicht keine Schnittstellenbeschreibung; die Feldnamen stammen aus offenen Quellen und sind an keinem Fahrzeug gemessen. Was die installierte Bibliothek wirklich liefert, zeigt der Reiter Test. Schreibende Befehle sind deshalb ab Werk gesperrt.",
# Kopf wie alle Hausplugins (Entscheidung Nr. 43, 0.9.24): gruener Kasten oben im Reiter Einstellungen, roh ausgegeben (by_t ohne by_e).
"EINST.WAS_IST_DAS": "<b>BYD-Fahrzeuge über das BYD-Konto am Loxone Miniserver.</b> Ein Abrufdienst holt im eingestellten Takt Ladezustand, Reichweite, Türen, Schlösser und Fenster, Reifendrücke, Standort und weitere Werte über die Bibliothek pybyd aus der BYD-Cloud. Die Werte gehen über MQTT und über einen tokengeschützten HTTP-Endpunkt an den Miniserver. Über denselben Endpunkt lassen sich Verriegelung, Klimatisierung sowie Sitz- und Batterieheizung schalten – ab Werk gesperrt, und jeder Befehl lässt sich vorher als Trockenlauf prüfen.",
"EINST.H_DIENST": "Abrufdienst",
"EINST.DIENST_ERKLAERUNG": "Der Dienst holt die Werte im eingestellten Takt und legt sie als Zwischenspeicher ab. Oberfläche und Miniserver lesen nur diesen Zwischenspeicher — deshalb antwortet der Endpunkt in Millisekunden und nicht in Sekunden.",
"EINST.K_START": "Dienst starten",
"EINST.K_RESTART": "Dienst neu starten",
"EINST.K_STOP": "Dienst anhalten",
"EINST.DIENST_START": "Der Dienst wurde gestartet.",
"EINST.DIENST_STOP": "Der Dienst wurde angehalten.",
"EINST.DIENST_RESTART": "Der Dienst wurde neu gestartet.",
"EINST.H_KONTO": "BYD-Konto",
"EINST.KONTO_ERKLAERUNG": "Es sind die Zugangsdaten des BYD-Kontos aus der BYD-App, nicht die eines Händlerportals. Sie liegen in einer eigenen Datei mit den Rechten 0600 und werden nie angezeigt — nur ihre Länge. Ein leer gelassenes Passwortfeld löscht nichts.",
"EINST.L_BENUTZER": "Benutzername",
"EINST.H_BENUTZER": "Derselbe Name, mit dem Sie sich in der BYD-App anmelden — je nach Konto eine E-Mail-Adresse oder eine Telefonnummer. Es wird nichts umgeschrieben: was hier steht, geht so an die Schnittstelle.",
"EINST.L_PASSWORT": "Passwort",
"EINST.H_PASSWORT": "Leer lassen behält das gespeicherte Passwort.",
"EINST.PW_GESETZT": "gespeichert, %d Zeichen",
"EINST.PW_LEER": "noch keines gespeichert",
"EINST.L_PIN": "Steuer-PIN",
"EINST.H_PIN": "Die PIN, mit der die BYD-App schreibende Befehle freigibt. Ohne sie weist BYD jeden Schaltbefehl ab; für das reine Ablesen wird sie nicht gebraucht. Vier bis acht Ziffern.",
"EINST.PIN_GESETZT": "gespeichert",
"EINST.PIN_LEER": "noch keine gespeichert",
"EINST.L_LAND": "Länderkennung",
"EINST.H_LAND": "Zwei Buchstaben, etwa DE oder AT. Nur nötig, wenn die Bibliothek danach fragt — ob sie das tut, sagt der Selbsttest im Reiter Test in der Zeile über die erkannten Konfigurationsfelder. Leer lassen, wenn unklar.",
"EINST.L_ZUGANG_LOESCHEN": "Benutzername, Passwort und PIN vollständig löschen",
"EINST.H_ZUGANG_LOESCHEN": "Löscht auch die Zweitschrift neben dem Konfigurationsordner. Ohne diesen Haken bliebe sie liegen und wäre bei der nächsten Neuinstallation wieder da — ein Löschen, das nicht löscht, ist schlimmer als keines.",
"EINST.H_TAKT": "Abruftakt",
"EINST.TAKT_WARNUNG": "Jeder Abruf <b>weckt das Fahrzeug</b>: die Schnittstelle fordert das Auto zur Meldung auf, statt in einen Zwischenspeicher der Wolke zu sehen. Ein zu dichter Takt kostet Ruhestrom und kann in eine Sperre laufen. Die Untergrenze von 120 Sekunden ist eine eigene Wahl und keine Angabe von BYD.",
"EINST.L_INTERVALL": "Takt in Sekunden",
"EINST.H_INTERVALL": "120 bis 3600. Die Vorgabe von 300 Sekunden entspricht der Vorgabe des ioBroker-Adapters derselben Schnittstelle.",
"EINST.L_VERLAUF_TAGE": "Verlauf aufbewahren (Tage)",
"EINST.H_VERLAUF_TAGE": "Je Tag und Fahrzeug eine kleine CSV-Datei im Datenordner. Ältere werden entfernt.",
"EINST.L_GPS_EIN": "Standort mit abfragen",
"EINST.H_GPS_EIN": "Der Standort ist eine eigene Abfrage. Wer ihn nicht braucht, spart je Takt einen Aufruf — und die Position des Fahrzeugs verlässt dann den Wagen nicht.",
"EINST.L_MQTT_BIBLIOTHEK": "Die Bibliothek darf ihren eigenen MQTT-Weg benutzen",
"EINST.H_MQTT_BIBLIOTHEK": "Das ist <b>nicht</b> das MQTT-Gateway des LoxBerry, sondern der Broker von BYD: die Bibliothek wartet damit auf die Bestätigung eines Befehls, statt zu pollen. Ohne diesen Haken dauert eine Rückmeldung länger. Der Weg zum Miniserver bleibt davon unberührt.",
"EINST.H_STEUERUNG": "Schreibende Befehle",
"EINST.STEUERUNG_ERKLAERUNG": "Ab Werk gesperrt, und das ist Absicht: ein Vorgabewert, der beim ersten Lauf ungefragt schaltet, ist ein Fehler. Mit dem Haken darf der Miniserver klimatisieren, Sitz- und Batterieheizung stellen und die Fenster schließen. <b>Verriegeln, Entriegeln, Fahrzeug suchen und Blinken</b> brauchen seit 0.9.26 zusätzlich den zweiten Haken darunter. Was BYD annimmt, ist damit noch nicht gesagt — die Quittung ist nicht die Wirkung.",
"EINST.L_STEUERUNG_EIN": "Schreibende Befehle zulassen",
"EINST.L_TEMP_MIN": "Zieltemperatur, kleinster erlaubter Wert",
"EINST.L_TEMP_MAX": "Zieltemperatur, größter erlaubter Wert",
"EINST.H_TEMP": "Grenzen für die Klimatisierung. Ein Wert außerhalb wird <b>abgewiesen</b> und nicht stillschweigend gekappt: ein still veränderter Sollwert führt zu einem Fahrzeug, das etwas anderes tut als angezeigt.",
"EINST.L_WARTEZEIT": "Wartezeit auf die Antwort (Sekunden)",
"EINST.H_WARTEZEIT": "So lange wartet die Oberfläche auf die Antwort des Dienstes, bevor sie „Ergebnis unbekannt“ meldet. 0 heißt: einreihen und nicht warten.",
"EINST.H_ERKANNT": "Erkannte Fahrzeuge",
"EINST.KEINE_FAHRZEUGE": "Es ist noch kein Fahrzeug bekannt. Das ist bis zum ersten erfolgreichen Abruf normal: Zugangsdaten eintragen, Dienst starten, einen Takt abwarten.",
"EINST.T_NR": "Nr.",
"EINST.T_MARKE": "Marke",
"EINST.T_MODELL": "Modell",
"EINST.T_NAME": "Name im Konto",
"EINST.T_KENNZEICHEN": "Kennzeichen",
"EINST.T_VIN": "Fahrgestellnummer",
"EINST.T_ANTRIEB": "Antriebsart",
"EINST.T_TBOX": "Steuergerät",
"EINST.VIN_HINWEIS": "Die laufende Nummer ist nach Fahrgestellnummer sortiert und bleibt damit stabil. In den Adressen für Loxone lässt sich statt der Nummer auch die Fahrgestellnummer angeben — das ist die haltbarere Angabe.",
"EINST.GESPEICHERT": "Die Einstellungen wurden gespeichert.",
"EINST.NICHT_GESPEICHERT": "Es wurde nichts gespeichert: %d Eingabe(n) sind beanstandet - sie stehen oben. Die Felder zeigen Ihre Eingaben; nach dem Berichtigen bitte erneut speichern.",
"EINST.HINWEIS_BENUTZER_GESAEUBERT": "Aus dem Benutzernamen wurden Zeichen entfernt, die dort nicht stehen dürfen (Steuerzeichen, Anführungszeichen). Gespeichert wurde die bereinigte Fassung – wenn Ihre Kennung solche Zeichen wirklich enthält, schlägt die Anmeldung fehl.",
"EINST.HINWEIS_LAND_GESAEUBERT": "Aus dem Länderkürzel wurden Zeichen entfernt: aus „%s“ wurde „%s“. Erlaubt sind zwei Buchstaben.",
"EINST.FEHLER_ZAHL": "%s: bitte eine ganze Zahl eintragen.",
"EINST.FEHLER_BEREICH": "%s: der Wert muss zwischen %d und %d liegen.",
"EINST.FEHLER_TEMP_TAUSCH": "Die kleinste Zieltemperatur ist größer als die größte. Bitte tauschen.",
"EINST.FEHLER_PIN": "Die Steuer-PIN wurde nicht übernommen, die bisher gespeicherte bleibt: sie besteht aus vier bis acht Ziffern.",
"EINST.FEHLER_LAND": "Die Länderkennung wurde nicht übernommen, die bisherige bleibt: sie besteht aus genau zwei Buchstaben, etwa DE.",
"EINST.FEHLER_ZUGANG_SPEICHERN": "Die Zugangsdaten ließen sich nicht speichern. Rechte im Konfigurationsordner prüfen.",
"EINST.FEHLER_ZUGANG_LOESCHEN": "Die Zugangsdaten ließen sich nicht vollständig löschen.",
"EINST.ZUGANG_GELOESCHT": "Benutzername, Passwort und PIN wurden gelöscht, die Zweitschrift ebenfalls.",
"EINST.WARN_PW_OHNE_KONTO": "Es ist ein Passwort hinterlegt, aber kein Benutzername. So kann die Anmeldung nicht gelingen.",
"EINST.HINWEIS_PIN_FEHLT": "Schreibende Befehle sind zugelassen, es ist aber keine Steuer-PIN hinterlegt. BYD wird jeden Schaltbefehl abweisen.",
"EINST.FEHLER_SPEICHERN": "Die Konfiguration ließ sich nicht schreiben (%s).",
"EINST.FEHLER_TOPIC": "Der Themenpfad darf nur Buchstaben, Ziffern, Bindestrich, Unterstrich und Schrägstrich enthalten.",
"EINST.L_MQTT_EIN": "Werte über MQTT senden",
"EINST.L_MQTT_TOPIC": "Themenpfad",
"EINST.H_MQTT_TOPIC": "Vorsatz aller Themen. Ihn nachträglich zu ändern benennt auf einer bestehenden Anlage <b>sämtliche</b> Themen um — die virtuellen Eingänge in Loxone und die Werte im Broker hängen daran.",

# ---- MQTT ------------------------------------------------------------------
"MQTT.GATEWAY_ERKLAERUNG": "Das MQTT-Gateway ist seit LoxBerry 3 <b>Bestandteil des Systems</b> und kein Plugin. Es wird nicht nachinstalliert, sondern unter <span class='sm-mono'>System → MQTT Gateway</span> eingeschaltet.",
"MQTT.H_ZUSTAND": "Zustand des Gateways",
"MQTT.NICHT_GEFUNDEN": "In der <span class='sm-mono'>general.json</span> des LoxBerry ist kein MQTT-Abschnitt zu finden. Ohne ihn kann nichts weitergeleitet werden.",
"MQTT.AUTOSTART_AUS": "Das MQTT-Gateway steht nicht auf Autostart (<span class='sm-mono'>System → MQTT Gateway</span>). Es wird gesendet, aber vermutlich hört niemand zu.",
"MQTT.AUTOSTART_EIN": "Das Gateway steht auf Autostart. Es startet nach einem Neustart des LoxBerry von selbst.",
"MQTT.T_AUTOSTART": "Autostart des Gateways",
"MQTT.T_BROKER": "Broker",
"MQTT.T_UDP": "UDP-Eingang des Gateways",
"MQTT.T_PLUGIN": "Dieses Plugin sendet über MQTT",
"MQTT.H_ABO": "Das Abo im MQTT-Gateway",
"MQTT.ABO_WARNUNG": "<b>MQTT&#8209;Gateway V1.</b> Das Plugin trägt dieses Abo selbst in die Datei <span class='sm-mono'>mqtt_subscriptions.cfg</span> seines Konfigurationsordners ein, und das Gateway V1 liest sie (im Quelltext des Gateways belegt). Ein Eintrag von Hand unter <i>System → MQTT Gateway</i>, Abschnitt <i>Subscriptions</i>, ist damit nicht mehr nötig; steht er schon da, schadet er nicht. Kommt trotzdem nichts an, ist das Abo der erste Ort zum Nachsehen.",
"MQTT.ABO_SCHRITTE": "Die Themengruppe dieses Plugins lautet:",
"MQTT.H_THEMEN": "Alle Themen, die dieses Plugin veröffentlicht",
"MQTT.THEMEN_ERKLAERUNG": "Diese Liste entsteht aus derselben Quelle wie die Statuszeile des Endpunkts. Der MQTT-Weg trägt damit dieselben Werte wie der HTTP-Weg — ein Plugin, dessen MQTT-Meldung weniger enthält, macht die Umstellung unmöglich, und zwar unauffällig: es kommen ja Werte an, nur eben nicht alle. Der Reiter Test misst die Übereinstimmung nach.",
"MQTT.T_THEMA": "Thema",
"MQTT.T_BEDEUTUNG": "Bedeutung",
"MQTT.T_RETAIN": "Zurückbehalten",
"MQTT.RETAIN_ERKLAERUNG": "Zurückbehalten (retain) gehen nur Zustände – etwa Zündung, Schloss oder Ladezustand –, damit Loxone nach einem Neustart des Miniservers oder des Gateways sofort den Stand hat. Messwerte mit Zeitbezug gehen ohne, damit nach einem Ausfall kein alter Wert aktuell aussieht. Der Zeitstempel ts und die beiden OK-Themen gehen nie zurückbehalten: sie sind das Lebenszeichen. Ebenso FEHLFOLGE: der Zähler erfolgloser Abrufe ist eine Aussage des Dienstes über sich selbst, und ein zurückbehaltenes „0“ bliebe nach dem Ende des Dienstes stehen. Ein Zustand ohne Aussage geht als <b>-</b> (Strich) zurückbehalten hinaus, nie leer. Schweigt ein Fahrzeug nur zeitweise, bleiben seine Zustände stehen, und fahrzeugN/OK geht auf 0 – ein Zustand gilt nur zusammen mit OK. Ein Messwert ohne Aussage geht als <b>-1</b> hinaus (die Innenraumtemperatur als <b>-999</b>); Breite und Länge gehen dann gar nicht hinaus, weil -1 dort ein echter Ort wäre. Die HTTP-Statuszeile zeigt dafür weiter einen Strich.",
"MQTT.PLATZHALTER": "<span class='sm-mono'>N</span> steht für die laufende Nummer des Fahrzeugs, beginnend bei 1.",
"MQTT.UMBENENNUNG": "Über MQTT wird der <b>Zeitstempel</b> gesendet, nicht das Alter: beim Senden ist das Alter immer null. Die Gegenseite rechnet es aus. In Loxone gilt <span class='sm-mono'>Alter = (Loxone-Zeit + 1230768000) − ts</span> — Loxone zählt Sekunden seit dem 01.01.2009.",

# ---- Einbindung in Loxone --------------------------------------------------
"LOX.H_TITEL": "Einbindung in Loxone",
"LOX.EINLEITUNG": "Zwei Wege stehen offen, gleichwertig, und sie schließen sich nicht aus. Über <b>MQTT</b> legt das Gateway die virtuellen Eingänge selbst an; der <b>HTTP-Endpunkt</b> liefert alle Werte eines Fahrzeugs in einem Abruf, mit fertigen Vorlagen – und er ist der einzige Weg für schreibende Befehle. Das Musterprojekt und die vier Seiten in Schritt 8 nutzen HTTP.",
"LOX.S1_TITEL": "Schritt 1: Weg festlegen",
"LOX.S1_TEXT": "Beide Wege sind gleichwertig. <b>HTTP</b> (Schritt 3): eine Vorlage je Fahrzeug, ein Abruf für alle Werte, das Alter jedes Werts steht dabei, und im Browser sieht man sofort, was ankommt – so arbeiten das Musterprojekt und die Seiten in Schritt 8. <b>MQTT</b> (ab Werk aus): das Gateway erzeugt die Namen der Eingänge selbst und liefert zusätzlich die Ladeempfehlung nach Strompreis. Beide Wege gleichzeitig ergeben doppelte Eingänge.",
"LOX.S2_TITEL": "Schritt 2: Das Abo im MQTT-Gateway",
"LOX.S2_TEXT": "Die Themengruppe dieses Plugins lautet:",
"LOX.S3_TITEL": "Schritt 3: Virtuelle Eingänge über HTTP",
"LOX.S3_TEXT": "Ein virtueller HTTP-Eingang mit dieser Adresse holt alle Werte in einem Aufruf. Je Wert eine Befehlserkennung mit dem Suchtext aus der Tabelle darunter.",
"LOX.S3_BEFEHLE": "<p>Der Titel ist für Menschen, der Suchtext für die Maschine: der Titel darf sich ändern, ohne dass eine bestehende Anlage etwas merkt — gesucht wird weiter nach dem Text in der zweiten Spalte. Das Semikolon gehört <b>ins Muster</b>: Loxone sucht wörtlich und nimmt den ersten Treffer, und ohne das Semikolon steckte <span class='sm-mono'>KM=</span> auch in einem künftigen <span class='sm-mono'>RESTKM=</span>.</p>",
"LOX.S3_STRICH": "Ein <b>Strich</b> als Wert bedeutet: dieser Wert liegt nicht vor. Es wird bewusst keine 0 gesendet — eine 0 sähe aus wie ein Messwert. Loxone behält dann den letzten gültigen Wert, und dass er alt ist, sagt das Feld ALTER.",
"LOX.S3_HERKUNFT": "Die Spalte <b>Herkunft</b> ist ernst gemeint. <b>Dokumentation</b> heißt: der Feldname stammt aus einer offenen Quelle und ist an keinem Fahrzeug dieses Hauses gemessen. <b>Gerechnet</b> heißt: das Feld kommt gar nicht vom Fahrzeug, sondern entsteht hier — fehlt die Zutat, bleibt es leer. Ein Feld, das niemand gemessen hat, darf nicht aussehen wie eines, das jemand gemessen hat. Der Reiter Test zeigt, welche Felder die Bibliothek bei <b>Ihrem</b> Fahrzeug wirklich getroffen hat.",
"LOX.T_ADRESSE": "Adresse",
"LOX.T_ZYKLUS": "Abfragezyklus",
"LOX.T_TITEL": "Titel (Vorschlag)",
"LOX.T_BEFEHL": "Suchtext (Befehlserkennung)",
"LOX.T_EINHEIT": "Einheit",
"LOX.T_BEDEUTUNG": "Bedeutung",
"LOX.T_HERKUNFT": "Herkunft",
"LOX.HERKUNFT_DOKU": "Dokumentation",
"LOX.HERKUNFT_BESTAND": "gemessen",
"LOX.HERKUNFT_GERECHNET": "gerechnet",
"LOX.HERKUNFT_UNBEKANNT": "unbekannte Herkunft (%s)",
"LOX.MEHRERE_FAHRZEUGE": "Mehrere Fahrzeuge: je Fahrzeug eine eigene Adresse",
"LOX.H_ALLES": "Alles auf einmal anlegen",
"LOX.ALLES_TEXT": "Die beiden Knöpfe erzeugen fertige Importdateien für Loxone Config. Die Eingänge liest man unter <span class='sm-mono'>Virtuelle Eingänge → Vordefinierte HTTP-Geräte → Vorlage Importieren…</span> ein, die Ausgänge unter <span class='sm-mono'>Virtuelle Ausgänge → Vordefinierte Geräte → Vorlage Importieren…</span> — beim Ausgang fehlt im Knopfnamen der Zusatz HTTP.",
"LOX.K_VORLAGE": "Vorlage für Loxone Config erzeugen",
"LOX.K_VORLAGE_VO": "Vorlage der Steuerbefehle erzeugen",
"LOX.VORLAGE_ZWEIMAL": "Loxone Config <b>legt beim Import neu an und überschreibt nichts</b>. Zweimal eingelesen heißt doppelte Bausteine, beide auf derselben Adresse — und Config meldet dazu nichts.",
"LOX.VORLAGE_HINWEIS": "Erzeugt vom LoxBerry-Plugin BYD Autos. Zweimal eingelesen ergibt doppelte Bausteine.",
"LOX.VORLAGE_UNGEPRUEFT": "Dieses Fahrzeug hat noch nie geantwortet - es sind alle Felder enthalten. Nach dem ersten erfolgreichen Abruf die Vorlage erneut holen, dann stehen nur noch die Felder darin, die das Fahrzeug wirklich liefert.",
"LOX.VORLAGE_VO_HINWEIS": "Steuerbefehle des LoxBerry-Plugins BYD Autos. Sie wirken nur, wenn im Reiter Einstellungen schreibende Befehle zugelassen sind.",
"LOX.S4_TITEL": "Schritt 4: Standort",
"LOX.S4_TEXT": "Der Standort steht in einer eigenen Antwort, damit die Statuszeile aus reinen Ganzzahlen besteht. Ein Breitengrad mit Punkt zwischen Ganzzahlen wäre für eine Befehlserkennung eine Falle.",
"LOX.S5_TITEL": "Schritt 5: Befehle senden",
"LOX.S5_TEXT": "Je Befehl ein virtueller Ausgang. Als Adresse des Ausgangs trägt man den Rechnernamen des LoxBerry ein, als Befehl den Pfad aus der Tabelle; die erzeugte Importdatei macht das so. Klima, Sitz- und Batterieheizung sind dort <b>analoge</b> Ausgänge: den Wert liefert der Baustein, der den Ausgang ansteuert – die Zieltemperatur als <span class='sm-mono'>&lt;v.1&gt;</span>, die Stufe als <span class='sm-mono'>&lt;v.0&gt;</span>. <b>Klima</b> hat seit 0.9.26 keinen Ausbefehl mehr, angehalten wird über den eigenen Befehl <span class='sm-mono'>BYD_1_KLIMA_AUS</span>; Sitz- und Batterieheizung senden beim Ausschalten Stufe 0. Am Miniserver ist das nicht gemessen. Verriegeln, Entriegeln, Fahrzeug suchen und Blinken brauchen zusätzlich den zweiten Haken im Reiter Einstellungen.",
"LOX.S5_WARNUNG": "Diese Adressen enthalten das Token. Wer ein neues Token erzeugt, muss sie alle nachziehen — ein virtueller Ausgang wertet die Antwort nicht aus, ein Ausfall bliebe also still.",
"LOX.S5_KEIN_LADEN": "<b>Laden starten und anhalten gibt es hier nicht.</b> Die verwendete Bibliothek nennt dafür keine Methode. Ein Ausgang, den der Hersteller nicht bedienen kann, wird gar nicht erst angeboten: ein Baustein, der nur Absagen erntet, ist schlimmer als keiner.",
"LOX.S6_TITEL": "Schritt 6: Token und Selbsttest",
"LOX.S6_TEXT": "Das Token schützt den unangemeldeten Endpunkt. Die zweite Adresse beantwortet die Frage „stimmt das in Loxone eingetragene Token noch?“ <b>ohne am Fahrzeug etwas auszulösen</b> — kein Gerätekontakt, kein Schreibzugriff. Ohne so einen Weg gibt es nur zwei schlechte Möglichkeiten: entweder man schaltet wirklich, oder man erfährt es nie.",
"LOX.T_TOKEN": "Token",
"LOX.T_SELBSTTEST": "Selbsttest (löst nichts aus)",
"LOX.K_TOKEN_NEU": "Neues Token erzeugen",
"LOX.TOKEN_NEU": "Es wurde ein neues Token erzeugt. Alle bisherigen Adressen im Miniserver sind damit ungültig und müssen nachgezogen werden.",
"LOX.S7_TITEL": "Schritt 7: Ausfallerkennung",
"LOX.S7_TEXT": "<b>Virtuelle Eingänge behalten ihren letzten Wert.</b> Fällt der Dienst aus, sieht in der App alles normal aus. Verdrahtet werden deshalb drei Dinge: <span class='sm-mono'>OK</span> (0 heißt: dieser Abruf hat nichts gebracht, oder das Abbild ist älter als das Dreifache des Abrufintervalls), <span class='sm-mono'>ALTER</span> (wächst, solange nichts Neues kommt) und eine <b>Analogwertvalidierung</b> auf ALTER: steht der LoxBerry selbst, frieren OK und ALTER ein, und nur die Validierung merkt, dass sich ALTER nicht mehr ändert (Seite „BYD Autos“ in Schritt 8, Tmc dreimal die Abfragezeit). Der Sonderfall <span class='sm-mono'>ALTER = −1</span> heißt „es hat noch nie einen erfolgreichen Abruf gegeben“ – OK ist deshalb immer mit auszuwerten.",
"LOX.S8_TITEL": "Schritt 8: Vier Seiten aus dem Musterprojekt zum Nachbauen",
"LOX.S8_TEXT": "Vier Seiten aus dem LoxBerry-Plugins Musterprojekt, dort in Loxone Config gebaut und verbunden. Jede Zeile ein Baustein; Loxone Config führt alle in der Baustein-Suche (Taste F5). Wer nur überwachen will, übernimmt die erste Seite allein. Die Namen gelten für Fahrzeug 1 so, wie die Vorlagen sie anlegen; die Titel der Vorlagen sind fest (BYD_1_…), auch bei englischer Oberfläche. Eingreifende Befehle (Verriegeln, Suchen, Blinken) nutzt das Musterprojekt nicht.",
"LOX.T_BAUSTEIN": "Baustein (Typ)",
"LOX.T_NAMENSVORSCHLAG": "Name (Vorschlag)",
"LOX.T_PARAMETER": "Parameter",
"LOX.T_EINGAENGE": "Eingänge verbinden mit",
"LOX.S9_TITEL": "Schritt 9: Gegenprobe",
"LOX.S9_TEXT": "Diese vier Adressen einmal im Browser aufrufen. Die vierte ist die wichtigste: erst eine <b>Absage</b> auf eine erfundene Aktion macht die drei Erfolge aussagekräftig.",
"LOX.T_PRUEFUNG": "Aufruf",
"LOX.T_ERWARTUNG": "Erwartete Antwort",

# ---- Baustein-Liste: seit BYD Autos 0.9.26 im Block "Welle Bild 17" am Ende von DE und EN ----------

# ---- Test ------------------------------------------------------------------
"TEST.H_SELBSTPRUEFUNG": "Selbstprüfung",
"TEST.EINLEITUNG": "Diese Prüfungen beantworten <b>ohne Loxone und ohne BYD-Konto</b>, ob die Einrichtung trägt. Was sich nur mit Fahrzeug prüfen ließe, steht am Ende der Seite als solches benannt.",
"TEST.BILANZ": "%d von %d Prüfungen bestanden, dazu %d Hinweise.",
"TEST.T_FRAGE": "Frage",
"TEST.T_BEFUND": "Befund",
"TEST.LEGENDE_PUNKT": "Ein grauer Punkt ist ein <b>Hinweis</b>: die Zeile trifft hier nicht zu oder lässt sich in diesem Aufbau nicht messen. Ein gelber Punkt heißt: eingeschaltet, aber die Zutat einer anderen Linie fehlt (etwa die Preisquelle der Ladeempfehlung). Beide zählen bewusst nicht als bestanden — eine Zusammenfassung darf nicht besser aussehen als ihr schlechtester Punkt.",
"TEST.H_LESEN": "Ansehen",
"TEST.K_STATUS": "Statuszeile aufrufen",
"TEST.K_POSITION": "Standort aufrufen",
"TEST.K_FAHRZEUGE": "Fahrzeugliste aufrufen",
"TEST.K_SELFTEST": "Selbsttest des Endpunkts",
"TEST.H_TECHNIK": "Technische Auskunft",
"TEST.K_SELBSTTEST": "Selbsttest des Dienstes",
"TEST.K_ENDPUNKT": "Endpunkt jetzt messen",
"TEST.K_FELDER": "Feldzuordnung vorschlagen",
"TEST.K_JSON": "Abbild als JSON ansehen",
"TEST.H_FELDER_ERKLAERUNG": "<b>Feldzuordnung vorschlagen</b> fragt das Fahrzeug und listet <b>jedes Blatt der Antwort mit seinem Pfad</b> auf — samt der Angabe, welches Feld darauf getroffen hat. Damit beantwortet das Gerät die Frage nach den Namen, nicht eine Vermutung. Der Aufruf braucht Zugangsdaten und Netz und dauert einige Sekunden.",
"TEST.H_SCHALTEN": "Schalten",
"TEST.SCHALTEN_WARNUNG": "<b>Diese Knöpfe wirken sofort am Fahrzeug.</b> Sie sind kein Trockenlauf. Ob BYD einen Befehl annimmt, sagt die Antwort; ob das Fahrzeug ihn ausführt, zeigt erst der nächste Abruf.",
"TEST.SCHALTEN_GESPERRT": "Schreibende Befehle sind gesperrt. Die Knöpfe werden abgewiesen, bis der Haken im Reiter Einstellungen gesetzt ist.",
"TEST.L_FAHRZEUG": "Fahrzeug",
"TEST.H_FAHRZEUG": "Die laufende Nummer aus der Fahrzeugliste.",
"TEST.L_TEMP": "Zieltemperatur in Grad Celsius",
"TEST.H_TEMP": "Ganze oder halbe Grad. Außerhalb der eingestellten Grenzen wird abgewiesen.",
"TEST.L_MINUTEN": "Laufzeit in Minuten (freiwillig)",
"TEST.H_MINUTEN": "Nur wirksam, wenn die installierte Bibliothek dafür einen Parameter kennt. Kann sie es nicht, steht das ausdrücklich in der Antwort — eine Angabe, die nicht ankommt, wird genannt und nicht stillschweigend übergangen.",
"TEST.L_STUFE": "Stufe für Sitz- und Batterieheizung",
"TEST.H_STUFE": "Welche Stufen dieses Fahrzeug kennt, ist nicht dokumentiert. 0 schaltet aus.",
"TEST.K_ABRUF": "Sofort abrufen",
"TEST.H_UNGEPRUEFT": "Was hier nicht geprüft werden kann",
"TEST.UNGEPRUEFT": "Ob die Anmeldung an der BYD-Schnittstelle gelingt, ob die Feldnamen dieser Feldtabelle bei diesem Fahrzeug zutreffen und ob die schreibenden Befehle am Fahrzeug die erwartete Wirkung haben — das entscheidet sich am Konto und am Auto, nicht hier. Die Feldnamen stammen aus offenen Quellen und sind an keinem Fahrzeug dieses Hauses gemessen.",
"TEST.UNBEKANNT": "Ergebnis unbekannt:",
"TEST.KEINE_MESSPUNKTE": "keine Messpunkte für heute",
"TEST.F_ENDPUNKT": "Antwortet der eigene Endpunkt über HTTP?",
"TEST.A_ENDPUNKT_AUS_SPEICHER": "diese Antwort stammt aus dem Zwischenspeicher und ist %d s alt",
"TEST.A_ENDPUNKT_UNKLAR": "nicht feststellbar — es gibt hier weder curl noch allow_url_fopen, oder der Webserver kann sich während des Seitenaufbaus nicht selbst aufrufen. Das ist keine Aussage über den Endpunkt.",
"TEST.A_ENDPUNKT_OK": "ja, HTTP 200 mit der erwarteten Kennung (Messung %d s alt)",
"TEST.A_ENDPUNKT_FEHL": "nein: HTTP %d, Antwort: %s",
"TEST.A_LEER": "leer",
"TEST.F_VENV": "Ist die virtuelle Python-Umgebung vorhanden?",
"TEST.A_VENV_FEHLT": "nein — das Plugin neu installieren, die Installation legt sie an",
"TEST.F_PYTHON": "Ist das Python neu genug (3.11 oder neuer)?",
"TEST.A_PYTHON_ZU_ALT": "zu alt für pybyd",
"TEST.A_PYTHON_UNBEKANNT": "nicht feststellbar",
"TEST.F_LIB": "Lässt sich die Bibliothek laden, und in welcher Fassung?",
"TEST.A_LIB_FEHLT": "nein — ohne pybyd kann der Dienst nicht arbeiten",
"TEST.F_DIENST": "Läuft der Abrufdienst?",
"TEST.A_DIENST_LAEUFT": "ja, Prozessnummer",
"TEST.A_DIENST_SOLL_TOT": "nein — er soll laufen, tut es aber nicht. Der Grund steht im Reiter Logdateien.",
"TEST.A_DIENST_GESTOPPT": "nein, bewusst angehalten",
"TEST.F_KONTO": "Ist ein Benutzername hinterlegt?",
"TEST.A_KONTO_FEHLT": "nein — Reiter Einstellungen",
"TEST.F_PASSWORT": "Ist ein Passwort hinterlegt?",
"TEST.A_PASSWORT_DA": "ja, %d Zeichen (der Inhalt wird nicht angezeigt)",
"TEST.A_PASSWORT_FEHLT": "nein — Reiter Einstellungen",
"TEST.F_PIN": "Ist die Steuer-PIN hinterlegt?",
"TEST.A_PIN_DA": "ja, %d Ziffern",
"TEST.A_PIN_FEHLT": "nein — BYD wird jeden schreibenden Befehl abweisen",
"TEST.A_PIN_UNNOETIG": "für das reine Ablesen nicht nötig. Sie wird erst gebraucht, wenn schreibende Befehle zugelassen werden.",
"TEST.F_RECHTE": "Ist die Zugangsdatei vor fremden Blicken geschützt?",
"TEST.A_ZUGANGSDATEI_FEHLT": "die Zugangsdatei fehlt",
"TEST.F_SICHERUNG": "Gibt es eine Zweitschrift der Konfiguration?",
"TEST.A_SICHERUNG_FEHLT": "noch keine. Sie entsteht beim ersten Speichern und liegt <b>neben</b> dem Konfigurationsordner — darin würde sie beim Update mit gelöscht.",
"TEST.F_FAHRZEUGE": "Sind Fahrzeuge erkannt?",
"TEST.A_FAHRZEUGE": "ja, %d",
"TEST.A_KEINE_FAHRZEUGE": "nein — bis zum ersten erfolgreichen Abruf ist das normal",
"TEST.F_ZUORDNUNG": "Wurden die Felder in der Antwort gefunden?",
"TEST.A_ZUORDNUNG_LEER": "keine Aussage möglich: es ist kein Fahrzeug im Abbild. Eine Prüfung über eine leere Menge ist kein Haken.",
"TEST.A_ZUORDNUNG_UNBEKANNT": "keine Aussage möglich: dieser Fahrzeugsatz führt gar keine Liste der offen gebliebenen Felder. Das heißt nicht „nichts offen“ – es heißt, dass nichts darüber bekannt ist.",
"TEST.F_ZUORDNUNG_N": "Wurden die Felder bei Fahrzeug %s gefunden?",
"TEST.A_ZUORDNUNG": "%d von %d Feldern aufgelöst",
"TEST.F_HERKUNFT": "Woher stammen die Feldnamen?",
"TEST.A_HERKUNFT": "%d gemessen, %d aus der Dokumentation, %d hier gerechnet. Die zweite Zahl ist kein Defekt, sondern eine Eigenschaft dieser Fassung: BYD veröffentlicht keine Schnittstellenbeschreibung. Die dritte kommt nicht vom Fahrzeug.",
"TEST.A_HERKUNFT_UNBEKANNT": "es gibt Felder mit einer Herkunft, die die Oberfläche nicht kennt: %s. Sie würden in der Spalte Herkunft benannt, aber keiner der drei Klassen zugeordnet.",
"TEST.F_ABRUF": "Wie frisch ist das Abbild?",
"TEST.A_NIE_ABGERUFEN": "es hat noch kein erfolgreicher Abruf stattgefunden",
"TEST.A_ABRUF_ALTER": "%d Sekunden alt",
"TEST.F_LETZTER_FEHLER": "Letzte gemeldete Störung",
"TEST.F_MQTT": "Zustand des MQTT-Gateways",
"TEST.A_MQTT_UNBENUTZT": "dieses Plugin sendet nicht über MQTT — der Zustand des Gateways ist dann ohne Belang",
"TEST.A_MQTT_NICHT_GEFUNDEN": "in der general.json ist kein MQTT-Abschnitt zu finden",
"TEST.A_MQTT_AUS": "das Gateway steht nicht auf Autostart. Ohne das kommt am Miniserver nichts an.",
"TEST.F_VORGABEN": "Führen Dienst und Oberfläche dieselben Vorgabewerte?",
"TEST.A_VORGABEN_UNKLAR": "die Liste im Dienst ließ sich nicht auslesen — der Vergleich wurde nicht gemacht",
"TEST.A_VORGABEN_OK": "ja, alle %d Vorgaben des Dienstes stehen auch in der Oberfläche",
"TEST.A_VORGABEN_FEHLT": "nein — nur im Dienst: %s",
"TEST.F_REITER": "Stimmen Reiterliste, Reiterleiste und Bereiche überein?",
"TEST.F_AKTIV": "Trägt jeder Reiter die Bedingung, die ihn sichtbar macht?",
"TEST.A_AKTIV_OK": "%d Anker in der Leiste und %d Bereiche, jeder mit der Bedingung für sm-active",
"TEST.A_AKTIV_FEHL": "nur %d von %d Stellen tragen die Bedingung. Ein Bereich ohne sie bleibt verborgen, und über die Leiste ist er nicht erreichbar.",
"TEST.A_AKTIV_KEINE": "keine Aussage möglich: es wurde keine Reiterleiste gefunden.",
"TEST.F_VOLLSTAENDIG": "Führt die gespeicherte Konfiguration jeden Schlüssel?",
"TEST.A_VOLLSTAENDIG_OK": "%d Schlüssel, keiner fehlt",
"TEST.A_VOLLSTAENDIG_FEHLT": "in der Datei fehlen: %s. Die Oberfläche zeigt dafür den Vorgabewert — wer ihn nicht anfasst, speichert ihn auch nicht.",
"TEST.A_VOLLSTAENDIG_KEINE": "keine Aussage möglich: es gibt noch keine Konfigurationsdatei, oder sie ist unlesbar.",
"TEST.F_LEGENDEN": "Führt jeder Reiter mit Knöpfen genau eine Legende, und nennt sie die richtigen Farben?",
"TEST.A_LEGENDEN_OK": "%d Reiter mit Knöpfen, jeder mit genau einer Legende; die Farben decken sich in beide Richtungen",
"TEST.A_LEGENDEN_FEHL": "nicht genau eine Legende: %s — Farben passen nicht: %s",
"TEST.A_LEGENDEN_KEINE": "keine Aussage möglich: es gibt keinen Reiter mit Knöpfen.",
"TEST.F_FORMULARE": "Trägt jedes Formular seine Marke, und kennt die Positivliste sie?",
"TEST.A_FORMULARE_OK": "%d Formulare, jedes mit einer Marke; die Positivliste führt %d Namen",
"TEST.A_FORMULARE_FEHL": "nur %d von %d Formularen tragen eine Marke; nicht in der Positivliste: %s",
"TEST.A_FORMULARE_UNKLAR": "keine Aussage möglich: die Positivliste ließ sich in index.php nicht finden. Das ist kein Befund über die Formulare, sondern über diese Prüfung.",
"TEST.A_FORMULARE_KEINE": "keine Aussage möglich: die Seite führt gar kein Formular.",
"TEST.A_REITER_UNKLAR": "die Liste ließ sich nicht auslesen — der Vergleich wurde nicht gemacht",
"TEST.A_REITER_OK": "ja, alle drei Stellen führen dieselben %d Namen",
"TEST.A_REITER_FEHL": "nein: Liste %d, Leiste %d, Bereiche %d. Fehlt ein Name in der Liste, springt die Seite nach jedem Absenden zurück.",
"TEST.F_MUSTER": "Ist jeder Suchtext in der Statuszeile eindeutig?",
"TEST.A_MUSTER_OK": "ja, alle %d Suchtexte kommen genau einmal vor",
"TEST.A_MUSTER_FEHL": "nein — mehrdeutig: %s. Loxone nimmt den ersten Treffer und liefert damit den Wert eines anderen Feldes.",
"TEST.F_WEGE": "Trägt der MQTT-Weg dieselben Werte wie der HTTP-Weg?",
"TEST.A_WEGE_OK": "ja: %d Werte in der Statuszeile, %d Themen in der Liste, deckungsgleich mit dem Dienst",
"TEST.A_WEGE_FEHL": "nein — ohne Thema: %s; nur der Dienst sendet: %s; nur die Liste nennt: %s",
"TEST.F_TEXTE": "Hat jedes Feld und jeder Befehl einen Text in dieser Sprache?",
"TEST.A_TEXTE_OK": "ja, alle %d",
"TEST.A_TEXTE_FEHL": "nein — ohne Text: %s. In der Tabelle stünde dann der Schlüsselname.",
"TEST.F_AUSWAHL": "Sind die Auswahlfelder als solche erkennbar?",
"TEST.A_AUSWAHL_KEINE": "diese Seite hat kein Auswahlfeld",
"TEST.A_AUSWAHL": "%d von %d Auswahlfeldern tragen das Merkmal, eigener Pfeil vorhanden: %s",
"TEST.F_MASKE": "Wird ein Text doppelt maskiert ausgegeben?",
"TEST.A_MASKE_OK": "nein, %d maskierte Texte geprüft",
"TEST.A_MASKE_FEHL": "ja — betroffen: %s. Im Browser stünde dort die Entität im Wortlaut.",
"TEST.F_STEUERUNG": "Sind schreibende Befehle zugelassen?",
"TEST.A_STEUERUNG_EIN": "ja",
"TEST.A_STEUERUNG_AUS": "nein — das ist die Vorgabe und damit richtig, solange nichts geschaltet werden soll",
"TEST.M_FAHRZEUG_UNGUELTIG": "Die Fahrzeugnummer ist keine Zahl.",
"TEST.M_TEMP_UNGUELTIG": "Die Zieltemperatur ist keine ganze oder halbe Zahl.",
"TEST.M_STUFE_UNGUELTIG": "Die Stufe ist keine Zahl.",
"TEST.M_UNBEKANNT": "Unbekannte Prüfung.",
"TEST.M_FELDER_STUMM": "Der Aufruf hat gar nichts ausgegeben. Das ist keine Feldliste – und auch keine Fehlermeldung, an der sich etwas ablesen ließe.",

# ---- Logdateien ------------------------------------------------------------
"LOG.H_TITEL": "Logdateien",
"LOG.ERKLAERUNG": "Neueste Zeile oben. Das Protokoll wird ab 500 kB auf die letzten 200 Zeilen gekappt, und dieselbe Meldung erscheint höchstens einmal je Stunde — sonst geht in einer Dauerstörung jede andere Zeile unter. <b>Es übersteht keinen Neustart:</b> der Ordner liegt auf einer Ramdisk. Wer eine Meldung aufheben will, kopiert sie vorher heraus.",
"LOG.LEER": "Das Protokoll ist leer.",
"LOG.K_LEEREN": "Protokoll leeren",
"LOG.GELEERT": "Das Protokoll wurde geleert.",

# ---- Feldnamen -------------------------------------------------------------
"BY_FELD.OK": "Abruf in Ordnung (1) oder nicht (0)",
"BY_FELD.SOC": "Ladezustand der Antriebsbatterie",
"BY_FELD.KM": "Kilometerstand",
"BY_FELD.REICHW": "Restreichweite",
"BY_FELD.LAEDT": "Fahrzeug lädt (1) oder nicht (0)",
"BY_FELD.KABEL": "Ladekabel steckt (1) oder nicht (0)",
"BY_FELD.LADEZUST": "Ladezustand als Kennzahl der Schnittstelle",
"BY_FELD.RESTMIN": "Restzeit des Ladevorgangs",
"BY_FELD.FEHLFOLGE": "Aufeinanderfolgende erfolglose Abrufe (0 = der letzte Abruf hat Werte gebracht)",
"BY_FELD.ZUHAUSE": "Fahrzeug im Umkreis der Heimatposition (1) oder nicht (0)",
"BY_FELD.VERBRAUCH": "Verbrauch der letzten abgeschlossenen Fahrt",
"BY_FELD.LADEEMPF": "Ladeempfehlung aus dem Strompreis (1 = jetzt laden)",
"BY_FELD.LADEKWH": "Geladene Energie des letzten Ladevorgangs",
"BY_FELD.TEMPO": "Geschwindigkeit",
"BY_FELD.FAHRZUST": "Fahrzeugzustand als Kennzahl der Schnittstelle",
"BY_FELD.ONLINE": "Fahrzeug erreichbar als Kennzahl der Schnittstelle",
"BY_FELD.ZUENDUNG": "Zündung als Kennzahl der Schnittstelle",
"BY_FELD.SCHLOSSVL": "Türschloss vorne links (Fahrertür)",
"BY_FELD.BATTHEIZ": "Batterieheizung als Kennzahl der Schnittstelle",
"BY_FELD.SITZHEIZ": "Sitzheizung Fahrersitz als Kennzahl der Schnittstelle",
"BY_FELD.ALTER": "Alter des Abbilds",
"BY_FELD.BREITE": "Breitengrad des Standorts",
"BY_FELD.LAENGE": "Längengrad des Standorts",
"BY_FELD.REIFENVL": "Reifendruck vorne links",
"BY_FELD.REIFENVR": "Reifendruck vorne rechts",
"BY_FELD.REIFENHL": "Reifendruck hinten links",
"BY_FELD.REIFENHR": "Reifendruck hinten rechts",
"BY_FELD.VERBRBYD": "Durchschnittsverbrauch laut Fahrzeug, kumuliert über die ganze Laufleistung",

# Neu 15.09.2026 (Issue #1). Die Kennzahlen heissen ausdruecklich "als Kennzahl
# der Schnittstelle": gemessen ist, WELCHE Zahl an einem Fahrzeug dastand,
# nicht, wofuer sie steht.
"BY_FELD.INNENTEMP": "Innenraumtemperatur",
"BY_FELD.FAHRSTUFE": "Fahrstufe als Kennzahl der Schnittstelle",
"BY_FELD.SCHLOSSVR": "Türschloss vorne rechts (Beifahrertür)",
"BY_FELD.SCHLOSSHL": "Türschloss hinten links",
"BY_FELD.SCHLOSSHR": "Türschloss hinten rechts",
"BY_FELD.TUERVL": "Tür vorne links (Fahrertür) als Kennzahl der Schnittstelle",
"BY_FELD.TUERVR": "Tür vorne rechts (Beifahrertür) als Kennzahl der Schnittstelle",
"BY_FELD.TUERHL": "Tür hinten links als Kennzahl der Schnittstelle",
"BY_FELD.TUERHR": "Tür hinten rechts als Kennzahl der Schnittstelle",
"BY_FELD.KOFFER": "Heckklappe als Kennzahl der Schnittstelle",
"BY_FELD.FENSTERVL": "Fenster vorne links als Kennzahl der Schnittstelle",
"BY_FELD.FENSTERVR": "Fenster vorne rechts als Kennzahl der Schnittstelle",
"BY_FELD.FENSTERHL": "Fenster hinten links als Kennzahl der Schnittstelle",
"BY_FELD.FENSTERHR": "Fenster hinten rechts als Kennzahl der Schnittstelle",
"BY_FELD.DACHFENSTER": "Schiebedach als Kennzahl der Schnittstelle",
"BY_FELD.REIFENEH": "Einheitenkennung der Reifendrücke laut Schnittstelle: 1 = bar, 2 = psi, 3 = kPa; die vier Drücke rechnet das Plugin immer in bar um (nur über MQTT und aktion=json)",
"BY_FELD.VERBR50": "Durchschnittsverbrauch der letzten 50 km laut Fahrzeug",

# ---- Befehle ---------------------------------------------------------------
"BY_BEF.ABRUF": "Sofort abrufen",
"BY_BEF.VERRIEGELN": "Verriegeln",
"BY_BEF.ENTRIEGELN": "Entriegeln",
"BY_BEF.KLIMA_START": "Klimatisierung starten",
"BY_BEF.KLIMA_STOP": "Klimatisierung anhalten",
"BY_BEF.KLIMA_PLAN": "Klimatisierung planen",
"BY_BEF.SITZKLIMA": "Sitzheizung stellen",
"BY_BEF.BATTHEIZ": "Batterieheizung stellen",
"BY_BEF.SUCHEN": "Fahrzeug suchen (Hupe und Licht)",
"BY_BEF.BLINKEN": "Blinken",
"BY_BEF.FENSTER_ZU": "Fenster schließen",

# ---- MQTT-Themen -----------------------------------------------------------
"BY_MQTT.OK": "1 wenn der letzte Abruf Werte gebracht hat, sonst 0. Wird bei jedem Durchlauf gesendet, auch bei einer Störung.",
"BY_MQTT.TS": "Zeitstempel der letzten erfolgreichen Messung, in Unix-Sekunden. Daraus rechnet die Gegenseite das Alter — über MQTT ist das Alter beim Senden immer null.",
"BY_MQTT.FAHRZEUGE": "Anzahl der erkannten Fahrzeuge",
# ---- Vorklimatisierung am Abfahrtsassistenten ------------------------------
"EINST.H_ABFAHRT": "Vorklimatisierung am Abfahrtsassistenten",
"EINST.ABFAHRT_ERKLAERUNG": "<b>Ungeprüft.</b> Der Abfahrtsassistent sendet unter seinem Themenpfad die Minuten bis zur Abfahrt (<code>ABFAHRT_IN</code>) und einen Freigabewert (<code>OK</code>). Dieses Plugin <i>hört zu</i> und setzt den Klimabefehl ab, sobald der Vorlauf erreicht ist. Gemessen ist bisher nur, dass der Assistent diese beiden Themen führt — nicht, dass ein BYD-Fahrzeug den Klimabefehl annimmt. Erst ausschalten, bis der Trockenlauf im Reiter Test das Gegenteil zeigt.",
"EINST.L_ABFAHRT_EIN": "Vorklimatisierung einschalten",
"EINST.L_ABFAHRT_PRAEFIX": "Themenpfad des Abfahrtsassistenten",
"EINST.H_ABFAHRT_PRAEFIX": "Ohne Schrägstrich am Anfang oder Ende. Abonniert werden <code>&lt;Pfad&gt;/ABFAHRT_IN</code> und <code>&lt;Pfad&gt;/OK</code>. Leer heißt: es wird nichts abonniert und nichts geschaltet.",
"EINST.L_ABFAHRT_VORLAUF": "Vorlauf vor der Abfahrt (Minuten)",
"EINST.H_ABFAHRT_VORLAUF": "So viele Minuten vor der gemeldeten Abfahrt wird der Klimabefehl abgesetzt — und nur einmal je Abfahrt.",
"EINST.L_ABFAHRT_TEMP": "Zieltemperatur der Vorklimatisierung (°C)",
"EINST.L_ABFAHRT_FAHRZEUG": "Fahrzeug für die Vorklimatisierung",
"EINST.H_ABFAHRT_FAHRZEUG": "Die Nummer aus dem Reiter Test. Der Abfahrtsassistent kennt keine Fahrzeuge, also muss hier eine feste Wahl stehen.",
"EINST.L_ABFAHRT_ALTER": "Höchstalter der Abfahrtsmeldung (Sekunden)",
"EINST.H_ABFAHRT_ALTER": "Ältere Meldungen gelten als verfallen und lösen nichts aus. Ein stehengebliebener Wert im Broker würde sonst jeden Tag dieselbe Abfahrt behaupten.",
"EINST.FEHLER_ABFAHRT_TEMP": "Die Zieltemperatur der Vorklimatisierung (%d °C) liegt außerhalb der Grenzen für schreibende Befehle (%d bis %d °C).",
"EINST.FEHLER_THEMA": "%s: erlaubt sind Buchstaben, Ziffern, Bindestrich, Unterstrich und Schrägstrich — keine Platzhalter wie + oder #.",

# ---- Ladeempfehlung --------------------------------------------------------
"EINST.H_LADEEMPF": "Ladeempfehlung nach Strompreis",
"EINST.LADEEMPF_ERKLAERUNG": "Das Plugin hört einen vorhandenen Preiswert im Broker mit und sendet daraus das Feld <code>LADEEMPF</code> (1 = jetzt laden, 0 = nicht). Es <b>schaltet nichts</b>: die Empfehlung ist ein Wert für die Loxone-Logik, damit dort sichtbar bleibt, wer die Ladung auslöst. Der Preis muss von einer anderen Quelle kommen — BYD liefert keinen.",
"EINST.L_LADEEMPF_EIN": "Ladeempfehlung berechnen",
"EINST.L_LADEEMPF_THEMA": "MQTT-Thema mit dem Preis",
"EINST.H_LADEEMPF_THEMA": "Vollständiges Thema, so wie es im Broker steht, ohne Platzhalter. Ohne Thema wird nichts gerechnet und nichts gesendet.",
"EINST.L_LADEEMPF_GRENZE": "Grenzwert",
"EINST.H_LADEEMPF_GRENZE": "In derselben Einheit wie der Wert im Thema. Komma oder Punkt, beides wird verstanden.",
"EINST.L_LADEEMPF_UNTER": "Empfehlen, wenn der Wert UNTER dem Grenzwert liegt",
"EINST.H_LADEEMPF_UNTER": "Angehakt für Preise (billig = laden), abgehakt für Überschuss (viel = laden). Welche Richtung stimmt, entscheidet allein die Bedeutung des Themas — deshalb wird sie nicht geraten.",
"EINST.L_LADEEMPF_ALTER": "Höchstalter des Preiswertes (Sekunden)",
"EINST.H_LADEEMPF_ALTER": "Ist der letzte Preiswert älter, wird <code>LADEEMPF</code> auf 0 gesetzt. Eine Empfehlung, die verstummt, muss 0 sagen und nicht schweigen: ein fehlender Wert liest sich in Loxone wie der letzte gültige.",
"EINST.FEHLER_LADEEMPF_OHNE_THEMA": "Die Ladeempfehlung ist eingeschaltet, aber kein MQTT-Thema eingetragen. Sie würde nichts rechnen.",
"EINST.FEHLER_DEZIMAL": "%s: bitte eine Zahl eintragen, Komma oder Punkt als Trennzeichen.",
# B-Nachzug 01.10.2026 (vb_byd2, Nr. 19): Zugangsfeld als Feld statt Text.
"EINST.FEHLER_KEIN_TEXT": "%s: Die Eingabe kam nicht als einzelner Text an und wurde nicht übernommen.",
# Nachbesserung 01.10.2026 (vb_byd2, Nr. 19/21): Schraegstrich am Rand wird beanstandet.
"EINST.FEHLER_THEMA_RAND": "%s: ohne Schrägstrich am Anfang oder Ende eintragen – im Broker ist /haus/byd ein anderes Thema als haus/byd.",

# ---- Gerechnete Groessen ---------------------------------------------------
"EINST.H_GERECHNET": "Gerechnete Größen",
"EINST.GERECHNET_ERKLAERUNG": "Diese Felder kommen nicht vom Fahrzeug, sondern werden hier gerechnet. Fehlt die Zutat, bleibt das Feld leer — es wird nie eine 0 gesendet, die wie eine Messung aussieht.",
"EINST.L_KAPAZITAET": "Nutzbare Batteriekapazität (kWh)",
"EINST.H_KAPAZITAET": "Aus dem Fahrzeugschein oder dem Datenblatt. Sie ist die Zutat für die geladene Energie und den Verbrauch; 0 heißt: beides bleibt leer. BYD liefert diesen Wert nicht mit.",
"EINST.L_HEIM_BREITE": "Heimatposition: Breite",
"EINST.KARTE": "Karte öffnen (mapatlas.eu): Adresse eingeben, die Zahlen unter „Dezimalgrad“ kopieren",
"EINST.KARTE_ZUSAMMEN": "Beide Zahlen dürfen auch zusammen hier hinein (etwa 50.123, 8.456); das Plugin teilt sie beim Speichern auf.",
"EINST.L_HEIM_LAENGE": "Heimatposition: Länge",
"EINST.H_HEIM": "Dezimalgrad, wie in Loxone. Beide Werte oder keinen — aus einer halben Position lässt sich kein Abstand rechnen. Daraus entsteht das Feld <code>ZUHAUSE</code>.",
"EINST.L_HEIM_RADIUS": "Umkreis (Meter)",
"EINST.H_HEIM_RADIUS": "Innerhalb dieses Umkreises gilt das Fahrzeug als zuhause. Zu klein gewählt springt das Feld, weil auch ein stehendes Fahrzeug streuende Positionen meldet.",
"EINST.FEHLER_HEIM_HALB": "Die Heimatposition braucht Breite UND Länge. Mit nur einem Wert lässt sich kein Abstand rechnen; das Feld bleibt leer.",

# ---- Reiter Ladevorgaenge --------------------------------------------------
"REITER.LADUNGEN": "Ladevorgänge",
"LADUNG.H_TITEL": "Erkannte Ladevorgänge",
"LADUNG.ERKLAERUNG": "Ein Ladevorgang wird am Wechsel des Feldes <code>LAEDT</code> erkannt — nicht von BYD gemeldet. Die Liste steht in <code>verlauf/ladungen.csv</code> im Datenordner. <b>Das Installationsprogramm des LoxBerry räumt diesen Ordner bei jeder Aktualisierung vollständig ab</b>; das Plugin trägt die Liste deshalb selbst hinüber: <code>preupgrade.sh</code> legt sie neben den Konfigurationsordner, <code>postinstall.sh</code> holt sie zurück. Eine <b>Deinstallation</b> überlebt sie nicht — dabei wird auch diese Zweitschrift entfernt. Wer sie darüber hinaus behalten will, kopiert die Datei vorher aus dem Datenordner.",
"LADUNG.LEER": "Noch kein Ladevorgang aufgezeichnet. Eingetragen wird erst, wenn der Dienst einen <i>Wechsel</i> von „lädt“ auf „lädt nicht“ gesehen hat — eine bereits laufende Ladung beim ersten Start zählt also nicht mit.",
"LADUNG.K_ANZAHL": "Aufgezeichnet",
"LADUNG.K_ANZAHL_H": "Zeilen in der Datei",
"LADUNG.K_SUMME": "Geladene Energie",
"LADUNG.K_SUMME_H": "gerechnet über %d von %d Zeilen, nur die mit hinterlegter Kapazität",
"LADUNG.T_START": "Beginn",
"LADUNG.T_ENDE": "Ende",
"LADUNG.T_DAUER": "Dauer",
"LADUNG.T_SOC": "Ladezustand",
"LADUNG.T_KWH": "kWh",
"LADUNG.T_KM": "Kilometerstand",
"LADUNG.GENAUIGKEIT": "<b>Was diese Zahlen sind.</b> Beginn und Ende sind die Zeitpunkte der <i>Abrufe</i>, an denen der Wechsel auffiel — sie liegen bis zu einem Abrufabstand neben der Wirklichkeit. Die kWh sind aus der Änderung des Ladezustands und der eingetragenen Kapazität gerechnet, nicht gemessen: Ladeverluste stecken nicht darin, und ein falsch eingetragener Kapazitätswert verfälscht jede Zeile gleichmäßig.",

# ---- Trockenlauf -----------------------------------------------------------
"TEST.L_PROBE": "Trockenlauf: nur zeigen, was passieren würde",
"TEST.H_PROBE": "Angehakt geht der Befehl denselben Weg bis unmittelbar vor das Senden: die Wachen greifen, das Fahrzeug und die Bibliotheksfunktion werden gesucht, die Parameter werden geprüft — nur abgesetzt wird nichts. Die Antwort beginnt dann mit „PROBE“. Das ist der Weg, um die Feldzuordnung und die Befehlsnamen an einem echten Fahrzeug zu klären, ohne es zu bewegen.",

# ---- Pruefzeilen der neuen Funktionen --------------------------------------
"TEST.F_HORCHER": "Sind die fremden MQTT-Themen abonniert?",
"TEST.A_HORCHER_UNNOETIG": "keine Funktion braucht ein fremdes Thema — Vorklimatisierung und Ladeempfehlung sind aus",
"TEST.A_HORCHER_FEHLER": "nein, der Dienst meldet: %s",
"TEST.A_HORCHER_KEIN_DIENST": "der Dienst läuft nicht — %d Themen wären zu abonnieren, verglichen werden kann hier nichts",
"TEST.A_HORCHER_ABWEICHUNG": "nein. Nicht abonniert: %s. Zusätzlich abonniert: %s. Solange ein Thema fehlt, löst die zugehörige Funktion nie aus, und das sieht aus wie eine stille Gegenseite.",
"TEST.A_HORCHER_OK": "ja, %d Themen und der Broker ist verbunden: %s",
"TEST.A_HORCHER_GETRENNT": "die Themenliste stimmt, aber der Dienst ist nicht mit dem Broker verbunden. Läuft das MQTT-Gateway, und stimmen Benutzer und Passwort?",
"TEST.F_SELBSTBEZUG": "Hört das Plugin auf sich selbst?",
"TEST.A_SELBSTBEZUG_UNNOETIG": "es wird kein fremdes Thema abonniert",
"TEST.A_SELBSTBEZUG_OK": "nein, kein abonniertes Thema liegt unter dem eigenen Pfad (%s)",
"TEST.A_SELBSTBEZUG_FEHL": "ja: %s liegt unter dem eigenen Themenpfad %s. Das Plugin wäre sein eigener Zulieferer — die Ladeempfehlung rechnete mit ihrem eigenen Ergebnis, die Vorklimatisierung wartete auf eine Abfahrt, die niemand ankündigt.",
"TEST.F_ABFAHRT": "Kann die Vorklimatisierung schalten?",
"TEST.A_ABFAHRT_AUS": "sie ist ausgeschaltet",
"TEST.A_ABFAHRT_GESPERRT": "nein: sie ist eingeschaltet, aber schreibende Befehle sind gesperrt. Sie würde zur Abfahrtszeit nichts absetzen — eine eingeschaltete Funktion, die nichts tut, fällt niemandem auf.",
"TEST.A_ABFAHRT_TEMP": "nein: die Zieltemperatur %d °C liegt außerhalb der Grenzen %d bis %d °C, der Befehl würde abgewiesen",
"TEST.A_ABFAHRT_OK": "ja, %d Minuten vor der Abfahrt auf %d °C, Fahrzeug %d. Ob BYD den Befehl annimmt, zeigt erst der Trockenlauf.",
"TEST.F_ZUTATEN": "Sind die Zutaten der gerechneten Größen da?",
"TEST.A_ZUTATEN_HALB": "nein: die Heimatposition ist nur halb eingetragen. Aus einem einzelnen Wert lässt sich kein Abstand rechnen, das Feld ZUHAUSE bleibt leer — obwohl etwas eingetragen ist.",
"TEST.A_ZUTATEN_OK": "ja: %d kWh Kapazität und eine Heimatposition mit %d m Umkreis",
"TEST.A_ZUTATEN_OFFEN": "nicht vollständig, und das ist erlaubt. Es fehlt: %s. Die davon abhängigen Felder bleiben leer statt eine 0 zu senden.",
"TEST.Z_KAPAZITAET": "die Batteriekapazität (VERBRAUCH und LADEKWH bleiben leer)",
"TEST.Z_HEIM": "die Heimatposition (ZUHAUSE bleibt leer)",
"TEST.F_LADUNGEN": "Lässt sich die Liste der Ladevorgänge lesen?",
"TEST.A_LADUNGEN_KEINE": "es ist noch keine Datei angelegt — erst ein erkannter Wechsel von „lädt“ auf „lädt nicht“ schreibt die erste Zeile",
"TEST.A_LADUNGEN_OK": "ja, %d von %d Zeilen gelesen",
"TEST.A_LADUNGEN_UNLESBAR": "nein: die Datei hat %d Zeilen, aber keine davon ließ sich lesen. Der Reiter zeigte eine leere Liste und behauptete damit, es habe nie geladen.",

# NACHGEPFLEGT 31.08.2026. Diese 21 Schluessel standen in der
# ausgelieferten .ini und im PHP, aber nicht mehr hier - ein Lauf
# haette sie geloescht. Die Werte sind aus der .ini geholt und mit
# der umgekehrten Tabelle aus umlaute_umstellen.py in die
# Entitaetenform zurueckgerechnet.
"EINST.H_SICHERUNG": "Einstellungen sichern und zurückspielen",
"EINST.K_SICHERN": "Einstellungen sichern",
"EINST.K_ZURUECK": "Zurückspielen",
"EINST.H_ZURUECK": "Sicherung zurückspielen",
"EINST.H_ZURUECK_TEXT": "Wirkt sofort: die Datei überschreibt die gespeicherten Einstellungen. Eine halb gültige Datei ändert gar nichts — erst wird alles geprüft, dann geschrieben. Jeder Wert wird mit derselben Regel geprüft wie im Formular, auch die Zugangsdaten; ein leeres Token in der Datei heißt: das geltende bleibt.",
"EINST.SICH_ABGELEHNT": "Die Datei wurde <b>nicht</b> übernommen — es ist nichts geändert worden:",
"EINST.SICH_ERKLAERUNG": "Für den <b>Umzug auf einen zweiten LoxBerry</b>: die Datei enthält alle Einstellungen dieses Plugins und lässt sich dort wieder einspielen.",
"EINST.SICH_FREMD": "Unbekannte Einstellung in der Datei: %s",
"EINST.SICH_FEHLEND": "In der Datei fehlen %d Einstellungen: %s. Eine unvollständige Sicherung wird nicht zurückgespielt — sonst fielen die fehlenden Werte stillschweigend auf die Werkseinstellung zurück, ohne dass an der Oberfläche etwas davon zu sehen wäre.",
"EINST.SICH_WERT": "Der Wert von %s taugt nicht für eine Einstellung — er ist keine Zahl und kein Text, zu lang, oder er enthält Steuerzeichen.",
"EINST.SICH_BEREICH": "%s liegt außerhalb des zulässigen Bereichs (%d bis %d).",
"EINST.SICH_KEINE_DATEI": "Es wurde keine Datei ausgewählt oder der Upload ist fehlgeschlagen.",
"EINST.SICH_KEIN_JSON": "Die Datei ist keine gültige Sicherung dieses Plugins.",
"EINST.SICH_LEER": "Die Datei enthält keine bekannte Einstellung.",
"EINST.SICH_SCHREIBFEHLER": "Die Einstellungen ließen sich nicht schreiben.",
"EINST.SICH_UEBERNOMMEN": "Einstellungen zurückgespielt: %d Werte übernommen.",
"EINST.SICH_WARNUNG": "<b>Die Datei enthält Ihre Zugangsdaten.</b> Ohne sie stünden nach dem Zurückspielen alle Felder richtig, und das Plugin käme trotzdem nicht an die Anlage. Behandeln Sie die Datei wie ein Passwort: nicht in ein Forum hängen und nicht an einen Fehlerbericht heften.",
"EINST.SICH_ZU_GROSS": "Die Datei ist größer als erlaubt — eine Sicherung dieses Plugins ist wenige Kilobyte groß.",
"MQTT.ABO_GEMESSEN": "(gemessen: Gateway&nbsp;V%d)",
"MQTT.ABO_UNBEKANNT": "Welche Fassung Ihr MQTT&#8209;Gateway hat, ließ sich nicht feststellen. <b>Fassung&nbsp;1</b> liest die Abodatei, die das Plugin selbst anlegt – ein Eintrag von Hand ist nicht nötig. <b>Fassung&nbsp;2:</b> ob die Themengruppe dort von selbst erscheint, ist an dieser Anlage nicht gemessen.",
"MQTT.ABO_V2": "<b>MQTT&#8209;Gateway V2.</b> Belegt ist nur, was im Quelltext des LoxBerry steht: die Seite <i>Subscriptions</i> hat unter V2 eine eigene Oberfläche, ihre Knöpfe sind abgeschaltet. Dass die Themengruppe dort von selbst erscheint und die Datenpunkte angehakt werden, ist an dieser Anlage <b>nicht gemessen</b>. Das Plugin legt seine Abodatei trotzdem an; ob V2 sie liest, ist ebenfalls nicht gemessen.",
"TEST.H_ROHDATEN": "Rohdaten der BYD-Gegenstelle",
"TEST.K_ROH": "Rohdaten der Gegenstelle ansehen",
"TEST.ROHDATEN_LEER": "Es liegen noch keine Rohdaten vor. Erst nach dem ersten erfolgreichen Abruf gibt es hier etwas zu sehen.",
"TEST.ROHDATEN_STAND": "Stand: %s",
"TEST.ROHDATEN_WARNUNG": "Hier stehen die <b>echten Feldnamen</b> Ihres Fahrzeugs, so wie die Gegenstelle sie liefert. Genau die braucht, wer prüfen will, ob die Zuordnung dieses Plugins passt: bleibt ein Wert leer, ist das eher ein falsch geratener Feldname als eine Störung. Die Anzeige gibt es nur hier im angemeldeten Bereich — die Datei trägt die Rechte 0600, weil Fahrzeugkennung und Standort darin stehen.",

# ---- Marke der laufenden Aktualisierung (0.9.15) ---------------------------
# T_TITEL und T_TEXT laufen durch by_e() - kein Markup, keine Entitaeten.
"UPGRADE.T_TITEL": "Eine Aktualisierung dieses Plugins läuft gerade.",
"UPGRADE.T_TEXT": "Bis sie abgeschlossen ist, zeigt diese Seite keine Einstellungen an, speichert nichts und startet den Dienst nicht. Ihre Zugangsdaten und die bisherigen Einstellungen werden am Ende der Installation zurückgeholt. Bitte die Seite in einer Minute neu laden.",
"TEST.F_MARKE": "Liegt eine Marke „Aktualisierung läuft“?",
"TEST.A_MARKE_KEINE": "nein — dieses Plugin wird gerade nicht aktualisiert",
"TEST.A_MARKE_GILT": "ja, seit %d Sekunden. Solange sie gilt, speichert die Oberfläche nichts und der Dienst wird nicht gestartet.",
"TEST.A_MARKE_ALT": "eine Marke von vor %d Minuten liegt noch da. Sie gilt nicht mehr — nach einer Stunde zählt sie nicht, damit eine abgebrochene Installation das Plugin nicht für immer stilllegt. Sie darf gelöscht werden: %s",
"TEST.A_MARKE_UNLESBAR": "eine Marke liegt da, ihr Inhalt ist aber keine Unixzeit. Sie gilt damit nicht und sperrt nichts; sie darf gelöscht werden: %s",
# Nachgezogen 30.09.2026 aus dem Bau 0.9.19 (Durchgang)
"ALLG.ANMELDESPERRE": "Die Anmeldung bei BYD wurde %d-mal innerhalb von 24 Stunden abgewiesen. Das Plugin meldet sich nicht mehr an, bis im Reiter Einstellungen neue Zugangsdaten gespeichert sind – so sperrt BYD das Konto nicht.",
"ALLG.VORGANG_GESCHEITERT": "Der Vorgang ist nicht gelungen:",
"EINST.FEHLER_TOPIC_EBENE": "Der Themenpfad darf keine leere Ebene enthalten (zwei Schrägstriche hintereinander) – der Dienst sendete sonst unter einem anderen Thema, als diese Seite anzeigt.",
"EINST.SICH_OHNE_ZUGANG": "Die Datei enthält keine Zugangsdaten (Sicherung einer älteren Fassung) – die gespeicherten bleiben unverändert.",
"EINST.SICH_REGEL": "%s wurde nicht übernommen: %s",
"EINST.SICH_R_BENUTZER": "der Benutzername enthält Steuerzeichen oder Anführungszeichen.",
"EINST.SICH_R_DEZIMAL": "erwartet ist eine Zahl mit Punkt im zulässigen Bereich.",
"EINST.SICH_R_LAND": "die Länderkennung besteht aus zwei Großbuchstaben oder ist leer.",
"EINST.SICH_R_PIN": "die Steuer-PIN besteht aus vier bis acht Ziffern oder ist leer.",
"EINST.SICH_R_PRAEFIX": "der Themenpfad folgt der Regel des Reiters MQTT: Buchstaben, Ziffern, Bindestrich, Unterstrich und Schrägstrich, keine leere Ebene, kein Schrägstrich am Rand.",
"EINST.SICH_R_SCHALTER": "ein Schalter kennt nur 0 und 1.",
"EINST.SICH_R_THEMA": "das Thema folgt der Regel des Formulars (Buchstaben, Ziffern, Bindestrich, Unterstrich, Schrägstrich, kein Schrägstrich am Rand) oder ist leer.",
"EINST.SICH_R_TOKEN": "das Aktionstoken besteht aus 1 bis 64 Zeichen (Buchstaben, Ziffern, Punkt, Bindestrich, Unterstrich) oder ist leer.",
"EINST.SICH_R_UNBEKANNT": "für diesen Wert ist keine Regel hinterlegt.",
"EINST.SICH_R_ZUGANG": "der Wert ist kein Text oder enthält Steuerzeichen.",
"EINST.SICH_ZUGANG_UEBERNOMMEN": "Die Zugangsdaten des BYD-Kontos aus der Datei sind übernommen; sie gelten ab dem nächsten Start des Dienstes.",
"MQTT.ABGERAEUMT": "Behaltene Themen unter dem bisherigen Präfix %s:",
"MQTT.ABODATEI_FEHLER": "Die Abodatei mqtt_subscriptions.cfg ließ sich nicht schreiben – das Abo im MQTT-Gateway bitte von Hand prüfen.",
"MQTT.ABODATEI_NEU": "Die Abodatei des MQTT-Gateways lautet jetzt %s.",
"LOX.S3_OK": "OK ist 0, sobald das Abbild älter ist als das Dreifache des Abrufintervalls (derzeit %d Sekunden); ALTER steht unverändert daneben. Gibt es noch gar keine Daten, antwortet der Endpunkt mit HTTP 503 und GRUND=KEINE_DATEN.",
"TEST.A_ABRUF_OHNE_DIENST": "der Dienst läuft nicht, über die Frische wird nicht geurteilt",
"TEST.A_MERKMAL_FEHL": "nein — nur %d von %d Formularen tragen ein Merkmal mit Wert; ein Absenden der übrigen wird abgewiesen.",
"TEST.A_MERKMAL_KEINE": "keine Aussage möglich: die Seite führt kein Formular.",
"TEST.A_MERKMAL_OK": "ja: %d von %d Formularen",
"TEST.A_WEGE_UNKLAR": "keine Aussage möglich: die Themen des Dienstes ließen sich aus bin/byd.py nicht lesen.",
"TEST.F_MERKMAL": "Trägt jedes Formular der gerenderten Seite ein Merkmal mit Wert?",
"LOG.BLEIBT": "Geleert wurde nur byd.log; Einstellungen, Zugangsdaten, Ladevorgänge und die Startdatei byd_start.log bleiben unberührt.",
"LOG.H_BESTAETIGEN": "Ohne den Haken geschieht nichts. Geleert wird nur byd.log – die bisherigen Zeilen sind danach fort. Einstellungen, Zugangsdaten, Ladevorgänge und die Startdatei byd_start.log bleiben.",
"LOG.L_BESTAETIGEN": "Ja, das Protokoll leeren",
"LOG.NICHT_BESTAETIGT": "Das Protokoll wurde nicht geleert: der Haken zur Bestätigung fehlte.",
"LOG.NICHT_GELEERT": "Das Protokoll ließ sich nicht leeren: %s ist nicht beschreibbar. Es ist unverändert.",
"BY_MQTT.FZ_OK": "1 wenn der letzte Abruf für dieses Fahrzeug Werte gebracht hat, sonst 0 – daran ist ein Teilausfall zu erkennen. Geht auch bei einer Störung, ohne Zugangsdaten und beim Ende des Dienstes hinaus.",
"MELDUNG.DIENSTSKRIPT_FEHLT": "dienst.sh nicht gefunden: %s",
"MELDUNG.DIENST_UNBEKANNT": "Unbekannter Befehl.",
"MELDUNG.EXEC_DIENST": "exec() ist in dieser PHP-Einrichtung gesperrt. Der Dienst lässt sich von hier aus nicht schalten.",
"MELDUNG.EXEC_GESPERRT": "exec() ist in dieser PHP-Einrichtung gesperrt - byd.py lässt sich von hier aus nicht aufrufen.",
"MELDUNG.KEIN_DIENST": "Der Abrufdienst läuft nicht - es wurde nichts eingereiht. Reiter Einstellungen, Knopf Dienst starten.",
"MELDUNG.KEIN_JSON": "Der Befehl ließ sich nicht als JSON darstellen (ungültiges UTF-8).",
"MELDUNG.NICHT_ABGELEGT": "Der Befehl ließ sich nicht ablegen: %s",
"MELDUNG.OHNE_ANTWORT": "Eingereiht, aber der Dienst hat innerhalb von %d s nicht geantwortet. Das Ergebnis ist damit unbekannt - es wird kein Erfolg gemeldet, den niemand geprüft hat.",
"MELDUNG.ORDNER_FEHLT": "Der Ordner für die Warteschlange ließ sich nicht anlegen: %s",
"MELDUNG.VENV_FEHLT": "Die virtuelle Python-Umgebung oder byd.py fehlt. Erwartet: %s und %s. Abhilfe: Plugin neu installieren; die Installation legt beides an.",
"MELDUNG.VENV_FEHLT_KURZ": "Die virtuelle Python-Umgebung oder byd.py fehlt - es wurde nichts abgeräumt.",

# ---- Welle Bild 17 (BYD Autos 0.9.26, 17.10.2026; Entwurf Welle 17 by, gemeinsame Form der fuenf Autos):
# vier Seiten aus dem LoxBerry-Plugins Musterprojekt - Kasten- und Hinweistitel, Kaesten BAUSTEIN.Sn_SCHRITTm,
# Hinweise BAUSTEIN.Sn_Hm, Tabellenzeilen BAUSTEIN.Zn_mm = "Typ | Name | Parameter | Eingaenge"
# (by_bausteinseiten() in htmlauth/index.php); LOX: Bild, Link, Vorlage-Knoepfe je Fahrzeug, zweiter Haken an
# Vorlage und Befehlstabelle; EINST/TEST: der zweite Haken (Hausherr 17.10.2026). ---------------------------
"BAUSTEIN.SCHRITTE_TITEL": "So übernehmen Sie diese Seite",
"BAUSTEIN.HINWEISE_TITEL": "Hinweise",
"BAUSTEIN.S1_SCHRITT1": "Im Plugin Reiter „%s“ Benutzername, Passwort und Steuer-PIN des BYD-Kontos eintragen, „%s“ drücken und einen Takt (5 Minuten) warten. Wer geladene Energie und Verbrauch will, trägt die nutzbare Batteriekapazität ein, wer „zu Hause“ will, die Heimatposition. Reiter „%s“ → „%s“: es kommt eine Zeile BYD;OK=1;SOC=…",
"BAUSTEIN.S1_SCHRITT2": "Reiter „%s“ → bei „Fahrzeug 1“ die Knöpfe „%s“ und „%s“. In Loxone Config die Eingänge im Baum „Virtuelle Eingänge“ wählen, Menüband „Vordefinierte HTTP-Geräte → Vorlage importieren…“, die Steuerbefehle im Baum „Virtuelle Ausgänge“ → „Vordefinierte Geräte → Vorlage importieren…“. Jede Datei nur EINMAL einlesen (zweimal ergibt doppelte Bausteine). Die beiden Behälter „BYD 1“ und „BYD 1 steuern“ dienen allen vier Seiten.",
"BAUSTEIN.S1_SCHRITT3": "Seite „BYD Autos“ anlegen. Aus dem Behälter „BYD 1“ die 11 Befehle der Liste ziehen (Nr. 1–11), dazu die Konstante 1. An BYD_1_SOC und BYD_1_REICHW im Eigenschaftsfenster „Statistik“ einschalten.",
"BAUSTEIN.S1_SCHRITT4": "Drei Benachrichtigungen anlegen (Peripherie → Mitteilungen → Benachrichtigung): „Meldung Auto gestört (BYD)“, „Meldung Ladestand niedrig (BYD)“ und „Meldung Ladung beendet (BYD)“, Texte wie in der Liste. Jede bekommt genau eine Leitung.",
"BAUSTEIN.S1_SCHRITT5": "Übrige Bausteine über die Baustein-Suche (Taste F5) setzen, Parameter wie in der Liste, von oben nach unten verbinden. An der Analogwertvalidierung Nr. 13 den Haken bei ‚En‘ im Eigenschaftsfenster entfernen (Config legt En negiert an; sonst kommt die Konstante 1 als 0 an). UND Nr. 24: den Eingang I2 negieren – in Config auf den Eingangspunkt klicken, danach zeigt der Eingang einen kleinen Kreis. Status Nr. 18: vorher zweimal „+“ klicken (V5, V6), Status Nr. 27 dreimal (V5–V7); die Zeilen in der angegebenen Reihenfolge eintragen, die ohne Bedingung zuletzt. Flankenerkennung Nr. 29: die Leitung zur Benachrichtigung geht vom Ausgang Off ab.",
"BAUSTEIN.S1_SCHRITT6": "Speichern und übertragen. Probe: „Zustand (BYD)“ zeigt „läuft – Werte … s alt“; BYD_1_ALTER springt alle 5 Minuten zurück.",
"BAUSTEIN.S1_H1": "Die Meldung „Auto gestört“ kommt erst nach 10 Minuten Störung. Steht der LoxBerry selbst, merkt es die Analogwertvalidierung nach 15 Minuten; die Meldung folgt 10 Minuten später.",
"BAUSTEIN.S1_H2": "Zu Nr. 13: steht der LoxBerry, behalten alle Eingänge ihren letzten Wert; nur das stehende BYD_1_ALTER verrät es. Jeder Abruf weckt das Fahrzeug – den Takt im Plugin nicht unter 300 s stellen; wer ihn oder die Abfragezeit am Behälter erhöht, setzt Tmc auf das Dreifache der Abfragezeit.",
"BAUSTEIN.S1_H3": "Zu Nr. 19–25: ein Schwellwertschalter hinter einem abgefragten Eingang gibt bei jeder Abfrage einen kurzen Impuls; die Einschaltverzögerung Nr. 25 schluckt ihn. Die Formeln Nr. 19 und 21 sorgen dafür, dass ein nie gemeldeter Wert (0, etwa nach einem Neustart des Miniservers) nicht als knapp zählt.",
"BAUSTEIN.S1_H4": "Zu Nr. 28–30: „Meldung Ladung beendet“ kommt bei jedem Ladeende nach mindestens einer Minute Laden – auch beim Kabelziehen oder einem Abbruch.",
"BAUSTEIN.S1_H5": "Die Ansagen „Ladung beendet“ und „Keine Daten mehr“ spricht das Plugin selbst (Reiter Einstellungen, Sprachausgabe, ab Werk an) – dafür braucht es keinen Baustein.",
"BAUSTEIN.S1_H6": "Zweites Fahrzeug: im Reiter „Einbindung in Loxone“ die Vorlagen für Fahrzeug 2 holen (Behälter „BYD 2“, Befehle BYD_2_…) und die Seiten mit diesen Befehlen ein zweites Mal anlegen; die Störungen beider Fahrzeuge über ein weiteres ODER vor die Einschaltverzögerung führen – nie zwei Quellen direkt an eine Benachrichtigung.",
"BAUSTEIN.S1_H7": "Ein Strich vom Plugin heißt „liegt nicht vor“ – der Eingang behält dann seinen letzten Wert. Hat das Fahrzeug schon einmal geantwortet, enthält die Eingangsvorlage nur die Felder, die es liefert; vorher alle 42, so wie im Musterprojekt.",
"BAUSTEIN.S2_SCHRITT1": "Im Plugin Reiter „%s“ den Haken „%s“ setzen (ab Werk aus) und die Steuer-PIN eintragen. Wer die Ladeempfehlung des Plugins will: „%s“ einschalten und das MQTT-Thema mit Preis oder Überschuss eintragen.",
"BAUSTEIN.S2_SCHRITT2": "Die Behälter „BYD 1“ und „BYD 1 steuern“ kommen von der Seite „BYD Autos“, Schritt 2 (nicht erneut einlesen). Seite „BYD Autos Laden und Klima“ anlegen, die 8 Befehle aus „BYD 1“ ziehen (Nr. 1–5 und 16–18), dazu spot_awattar_rank (Virtuellen Eingang mit dem Namen aus der Namenstabelle im Reiter ‚Einbindung in Loxone‘ des Plugins Spotpreis aWATTar, ab 1.2.38, anlegen; ohne Spotpreis-Plugin Nr. 6–9 weglassen und an Nr. 10 den Eingang I2 frei lassen) und die fünf Ausgangsbefehle BYD_1_KLIMA, BYD_1_KLIMA_AUS, BYD_1_SITZKLIMA, BYD_1_BATTERIEHEIZUNG und BYD_1_ABRUF aus „BYD 1 steuern“.",
"BAUSTEIN.S2_SCHRITT3": "Sieben Virtuelle Eingänge anlegen (Schalter Nr. 12 und 32, Schieberegler Nr. 19 und 30, Tasten Nr. 20, 27 und 34; je „In Visualisierung verwenden“ an) und „Anwesenheit (eigene Quelle)“ aus dem Baum ziehen. Schaltuhr Nr. 21 über die Baustein-Suche setzen und im Schaltuhr-Editor Montag bis Freitag 06:40–07:00 EIN eintragen; ihr Ausgang AQ geht an das UND Nr. 23.",
"BAUSTEIN.S2_SCHRITT4": "Übrige Bausteine über die Baustein-Suche (Taste F5) setzen, Parameter wie in der Liste, verbinden. Größer Nr. 7 und Kleiner oder gleich Nr. 8: den Vergleichswert als Parameter V2 eintragen, den zweiten Eingang offen lassen. Status Nr. 15: vorher dreimal „+“ klicken (V5–V7).",
"BAUSTEIN.S2_SCHRITT5": "Speichern und übertragen. Probe: „Klima jetzt (BYD)“ drücken – im Plugin Reiter „%s“ steht der Befehl klima_start mit 21 °C; „Klima aus (BYD)“ hält die Klimatisierung an.",
"BAUSTEIN.S2_H1": "„Ladefreigabe bestätigt (BYD)“ (Nr. 14) ist der Schaltausgang für eine Wallbox ohne eigene Regelung. Wer EVCC nutzt, lässt Nr. 12–14 weg: EVCC regelt die Wallbox selbst. Laden starten oder anhalten kann das Fahrzeug über BYD nicht – das Plugin bietet dafür keinen Befehl.",
"BAUSTEIN.S2_H2": "Zu Nr. 7–9: spot_awattar_rank -1 heißt „kein Rang“ und zählt nicht als günstig; ohne Spotpreis-Plugin bleibt der Eingang 0, also nie günstig. Die Einschaltverzögerung Nr. 14 schluckt den Impuls der Vergleicher bei jeder Abfrage.",
"BAUSTEIN.S2_H3": "Zu Nr. 25 und 26: der Klima-Befehl ist analog und sendet die Zieltemperatur (<v.1>). Solange nichts angefordert ist, liefert die Formel -1 – diesen Wert weist das Plugin ohne Wirkung ab. Angehalten wird nur über „Klima aus (BYD)“ (Nr. 27 und 28).",
"BAUSTEIN.S2_H4": "Die Zieltemperatur muss zwischen den Grenzen im Plugin liegen (ab Werk 16–30 °C), sonst weist das Plugin den Befehl ab und es passiert nichts. Wie lange das Fahrzeug klimatisiert, entscheidet BYD.",
"BAUSTEIN.S2_H5": "Wer im Plugin die Vorklimatisierung am Abfahrtsassistenten eingeschaltet hat, lässt die Schaltuhr Nr. 21 leer – sonst gibt es zwei Auslöser für dieselbe Klimatisierung. Die Schaltuhr klimatisiert nur, wenn „Anwesenheit (eigene Quelle)“ 1 ist (im Urlaub nichts).",
"BAUSTEIN.S2_H6": "Sitz- und Batterieheizung: Stufe 0 schaltet aus – der Ausbefehl der Steuervorlage sendet sie (seit 0.9.26). Welche Stufen das Fahrzeug kennt, ist nicht dokumentiert; im Plugin Reiter Test „Schalten“ mit Trockenlauf ansehen.",
"BAUSTEIN.S2_H7": "Jeder Sofortabruf (Nr. 34 und 35) weckt das Fahrzeug – die Taste nicht im Takt auslösen.",
"BAUSTEIN.S3_SCHRITT1": "Die Behälter kommen von der Seite „BYD Autos“, Schritt 2 (nicht erneut einlesen). Seite „BYD Autos Fahrzeug“ anlegen, die 16 Befehle aus „BYD 1“ ziehen (Nr. 1–16), den Ausgangsbefehl BYD_1_FENSTER_ZU aus „BYD 1 steuern“ und „Regensensor (eigene Quelle)“ aus dem Baum.",
"BAUSTEIN.S3_SCHRITT2": "Zwei Virtuelle Eingänge anlegen: den Schieberegler Nr. 17 „Schloss-Kennzahl verriegelt (BYD)“ (Startwert 2) und die Taste Nr. 23 „Fenster schließen (BYD)“ (je „In Visualisierung verwenden“ an). Die Benachrichtigung „Meldung Fahrzeug offen (BYD)“ anlegen, Text wie in der Liste.",
"BAUSTEIN.S3_SCHRITT3": "Übrige Bausteine über die Baustein-Suche (Taste F5) setzen, Parameter wie in der Liste, verbinden. Status Nr. 27: vorher viermal „+“ klicken (V5–V8), Status Nr. 28 dreimal (V5–V7).",
"BAUSTEIN.S3_SCHRITT4": "Einmal mit der BYD-App vergleichen: das Fahrzeug verriegeln, nach dem nächsten Abruf BYD_1_SCHLOSSVL ablesen und den Schieberegler „Schloss-Kennzahl verriegelt (BYD)“ auf diesen Wert stellen (am gemessenen Fahrzeug 2).",
"BAUSTEIN.S3_SCHRITT5": "Speichern und übertragen. Probe: „Fenster schließen (BYD)“ drücken – im Plugin Reiter „%s“ steht der Befehl fenster_zu.",
"BAUSTEIN.S3_H1": "Schlösser, Türen und Fenster liefert BYD nur als Kennzahlen; was 0, 1 oder 2 heißt, ist von BYD nicht beschrieben. Deshalb vergleicht Nr. 18 mit dem Schieberegler statt mit einem festen Wert.",
"BAUSTEIN.S3_H2": "Zu Nr. 19–21: während der Fahrt ist das Auto oft nicht verriegelt – gemeldet wird nur, wenn es steht (Geschwindigkeit 0) und die Werte frisch sind, und erst nach 5 Minuten.",
"BAUSTEIN.S3_H3": "Bei Regen schickt der Miniserver einmal „Fenster schließen“ – auch wenn das Fahrzeug woanders steht; das schadet nicht.",
"BAUSTEIN.S3_H4": "Verriegeln, Entriegeln, Fahrzeug suchen (Hupe und Licht) und Blinken stehen bewusst nicht auf dieser Seite: sie greifen in ein Fahrzeug im öffentlichen Raum ein. Das Plugin bietet sie nur mit einem zweiten Haken an („%s“, ab Werk aus); ohne ihn weist der Endpunkt sie ab, und die Steuervorlage enthält sie nicht.",
"BAUSTEIN.S4_SCHRITT1": "Seite „BYD Autos Werte“ anlegen, die 12 Befehle aus „BYD 1“ ziehen (Nr. 1–12); an BYD_1_KM im Eigenschaftsfenster „Statistik“ einschalten.",
"BAUSTEIN.S4_SCHRITT2": "Die Benachrichtigung „Meldung Reifendruck niedrig (BYD)“ anlegen. Übrige Bausteine über die Baustein-Suche (Taste F5) setzen und verbinden: Impuls um Nr. 19 „Zu bestimmter Uhrzeit“ 00:00:00; der Analogspeicher Nr. 20 behält Rem (Vorgabe). Status Nr. 18: vorher einmal „+“ klicken (V5), Status Nr. 22 viermal (V5–V8).",
"BAUSTEIN.S4_SCHRITT3": "Speichern und übertragen. Probe: „Reifendruck (BYD)“ mit der BYD-App vergleichen.",
"BAUSTEIN.S4_H1": "„Heute gefahren“ zeigt nach einem Neustart des Miniservers bis Mitternacht 0.",
"BAUSTEIN.S4_H2": "Den Verbrauch der letzten Fahrt rechnet das Plugin nur mit eingetragener Batteriekapazität (Fahrten ab 20 km); die beiden anderen Verbrauchswerte meldet das Fahrzeug selbst.",
"BAUSTEIN.S4_H3": "Die Reifendrücke kommen immer in bar; das Fahrzeug kann bar, psi oder kPa melden (REIFENEH 1/2/3), das Plugin rechnet um. 2,2 und 2,4 bar an Nr. 14 passen damit für jedes Fahrzeug. -1 heißt: Wert unplausibel (unbekannte Einheit) – dann meldet auch Nr. 14; Reifen und REIFENEH prüfen.",
"BAUSTEIN.S4_H4": "Fahrstufe und Zündung sind Kennzahlen der Schnittstelle ohne beschriebene Bedeutung; der Status zeigt sie nur an.",
"BAUSTEIN.Z1_01": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_OK | 1 = letzter Abruf hat Werte gebracht und sie sind höchstens dreimal so alt wie der Abruftakt (ab Werk 300 s), sonst 0 | —",
"BAUSTEIN.Z1_02": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_ALTER | Sekunden seit dem letzten erfolgreichen Abruf; -1 = noch nie einer gelungen – das Lebenszeichen: ändert sich bei jeder Abfrage | —",
"BAUSTEIN.Z1_03": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_FEHLFOLGE | erfolglose Abrufe in Folge; 0 = der letzte hat Werte gebracht | —",
"BAUSTEIN.Z1_04": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_ONLINE | Erreichbarkeit des Fahrzeugs als Kennzahl der Schnittstelle (Rohwert, Bedeutung nicht belegt) | —",
"BAUSTEIN.Z1_05": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_FAHRZUST | Fahrzeugzustand als Kennzahl der Schnittstelle (Rohwert, Bedeutung nicht belegt) | —",
"BAUSTEIN.Z1_06": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_SOC | Ladezustand der Antriebsbatterie in %%; Statistik ein | —",
"BAUSTEIN.Z1_07": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_REICHW | Restreichweite in km; Statistik ein | —",
"BAUSTEIN.Z1_08": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_LAEDT | 1 = Fahrzeug lädt, 0 = lädt nicht | —",
"BAUSTEIN.Z1_09": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_KABEL | 1 = Ladekabel steckt, 0 = nicht | —",
"BAUSTEIN.Z1_10": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_RESTMIN | Restzeit des Ladevorgangs in min | —",
"BAUSTEIN.Z1_11": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_ZUHAUSE | 1 = Fahrzeug im Umkreis der Heimatposition (ab Werk 150 m), 0 = unterwegs; ohne Heimatposition im Plugin kommt kein Wert | —",
"BAUSTEIN.Z1_12": "Konstante | Konstante 1 | Wert 1 | —",
"BAUSTEIN.Z1_13": "Analogwertvalidierung | Lebenszeichen fehlt (BYD) | Tmc 900 s (dreimal die Abfragezeit von 300 s), Min -1, Max 999999 – steht der LoxBerry, bleibt das Alter auf seinem letzten Wert; Haken bei ‚En‘ im Eigenschaftsfenster entfernen | V = #2, En = #12",
"BAUSTEIN.Z1_14": "NICHT | Keine frischen Daten (BYD) | — | I = #1",
"BAUSTEIN.Z1_15": "ODER | Störung (BYD) | — (keine frischen Daten oder Lebenszeichen fehlt) | I1 = #14, I2 = Ausgang E von #13",
"BAUSTEIN.Z1_16": "Einschaltverzögerung | Störung bestätigt (BYD) | 600 s (zwei Abfragen; ein Neustart und ein einzelner Fehlabruf melden nichts) | Eingang = #15",
"BAUSTEIN.Z1_17": "Benachrichtigung | Meldung Auto gestört (BYD) | Text: BYD – seit 10 Minuten keine frischen Fahrzeugwerte, oder der LoxBerry antwortet nicht. In der App den Status „Zustand (BYD)“ lesen | Eingang = #16",
"BAUSTEIN.Z1_18": "Status | Zustand (BYD) | Zeilen: V1 = 1 „Lebenszeichen fehlt seit mindestens 15 Minuten – LoxBerry oder Plugin antwortet nicht; LoxBerry im Browser öffnen, im Plugin Reiter Einstellungen ‚Dienst starten‘“; V3 < 0 „noch nie ein erfolgreicher Abruf – im Plugin Reiter Einstellungen Benutzername, Passwort und Steuer-PIN des BYD-Kontos eintragen, dann ‚Dienst starten‘“; V4 >= 3 „<v4> Abrufe in Folge gescheitert – das Plugin streckt den Takt; im Plugin Reiter Test ‚Selbsttest des Dienstes‘“; V2 = 0 „keine frischen Werte – letzter erfolgreicher Abruf vor <v3> s; im Plugin Reiter Test ‚Endpunkt jetzt messen‘“; ohne Bedingung „läuft – Werte <v3> s alt (Erreichbarkeit <v5>, Zustand <v6> als Kennzahlen)“; Visualisierung EIN | V1 = Ausgang E von #13, V2 = #1, V3 = #2, V4 = #3, V5 = #4, V6 = #5",
"BAUSTEIN.Z1_19": "Formel | Ladestand für Meldung (BYD) | IF(I1>0;I1;100) – ein nie gemeldeter Ladestand (0: Verbrenner oder vor dem ersten Abruf) zählt nicht als niedrig | I1 = #6",
"BAUSTEIN.Z1_20": "Schwellwertschalter | Ladestand niedrig (BYD) | Ein 20 / Aus 25 (%%; schaltet beim Unterschreiten von 20 %% ein, über 25 %% wieder aus) | Eingang = #19",
"BAUSTEIN.Z1_21": "Formel | Reichweite für Meldung (BYD) | IF(I1>0;I1;999) – eine nie gemeldete Reichweite (0) zählt nicht als gering | I1 = #7",
"BAUSTEIN.Z1_22": "Schwellwertschalter | Reichweite gering (BYD) | Ein 50 / Aus 70 (km; schaltet beim Unterschreiten von 50 km ein, über 70 km wieder aus) | Eingang = #21",
"BAUSTEIN.Z1_23": "ODER | Ladestand oder Reichweite knapp (BYD) | — | I1 = #20, I2 = #22",
"BAUSTEIN.Z1_24": "UND | Knapp und nicht angesteckt (BYD) | — (I2 negiert: in Config auf den Eingangspunkt klicken, es erscheint ein kleiner Kreis; am Ladekabel meldet nichts) | I1 = #23, I2 = #9 (negiert)",
"BAUSTEIN.Z1_25": "Einschaltverzögerung | Knapp bestätigt (BYD) | 600 s (schluckt den kurzen Impuls der Schwellwertschalter bei jeder Abfrage) | Eingang = #24",
"BAUSTEIN.Z1_26": "Benachrichtigung | Meldung Ladestand niedrig (BYD) | Text: BYD – Ladestand unter 20 %% oder Reichweite unter 50 km, und kein Ladekabel steckt. Bitte das Fahrzeug anstecken; Werte in der App unter „Ladestand und Reichweite (BYD)“ | Eingang = #25",
"BAUSTEIN.Z1_27": "Status | Ladestand und Reichweite (BYD) | Zeilen: V3 = 1 und V5 > 0 „lädt – <v1.0> %%, Reichweite <v2> km, fertig in etwa <v5> min“; V3 = 1 „lädt – <v1.0> %%, Reichweite <v2> km“; V7 = 1 „knapp – <v1.0> %%, nur noch <v2> km – bitte anstecken“; V4 = 1 „Kabel steckt, lädt nicht – <v1.0> %%, Reichweite <v2> km“; V6 = 1 „<v1.0> %%, Reichweite <v2> km – Fahrzeug zu Hause“; ohne Bedingung „<v1.0> %%, Reichweite <v2> km – unterwegs (ohne Heimatposition im Plugin steht hier immer ‚unterwegs‘)“; Visualisierung EIN | V1 = #6, V2 = #7, V3 = #8, V4 = #9, V5 = #10, V6 = #11, V7 = #25",
"BAUSTEIN.Z1_28": "Einschaltverzögerung | Lädt seit einer Minute (BYD) | 60 s (erst eine echte Ladung zählt; ein kurzer Ausreißer meldet kein Ladeende) | Eingang = #8",
"BAUSTEIN.Z1_29": "Flankenerkennung | Ladung endet (BYD) | Pd 1 s; benutzt wird der Ausgang Off (fallende Flanke) | Eingang = #28",
"BAUSTEIN.Z1_30": "Benachrichtigung | Meldung Ladung beendet (BYD) | Text: BYD – die Ladung ist beendet (voll, Kabel gezogen oder abgebrochen). Ladestand in der App unter „Ladestand und Reichweite (BYD)“ | Eingang = Ausgang Off von #29",
"BAUSTEIN.Z2_01": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_LAEDT | 1 = Fahrzeug lädt (weitere Instanz, auch auf Seite „BYD Autos“) | —",
"BAUSTEIN.Z2_02": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_KABEL | 1 = Ladekabel steckt (weitere Instanz) | —",
"BAUSTEIN.Z2_03": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_LADEZUST | Ladezustand als Kennzahl der Schnittstelle: 0 nicht verbunden, 1 lädt, 15 Stecker steckt (Tabelle des ioBroker-Adapters, am Fahrzeug nicht gemessen) | —",
"BAUSTEIN.Z2_04": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_LADEKWH | geladene Energie des letzten Ladevorgangs in kWh (gerechnet aus Ladestand und Kapazität; ohne Kapazität im Plugin kommt kein Wert) | —",
"BAUSTEIN.Z2_05": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_LADEEMPF | 1 = laden empfohlen (das Plugin hört einen Preis- oder Überschusswert im Broker mit), 0 = nicht; ohne eingeschaltete Ladeempfehlung im Plugin kommt kein Wert | —",
"BAUSTEIN.Z2_06": "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Spotpreis aWATTar) | spot_awattar_rank | Rang der laufenden Stunde in den nächsten 24 h, 1 = günstigste, -1 = kein Rang (weitere Instanz, auch auf „WaermepumpeCloud“, „Weissware PV-Start“, „Spotpreis aWATTar“); ohne Spotpreis-Plugin frei lassen (dann nie günstig) | —",
"BAUSTEIN.Z2_07": "Größer | Preisrang bekannt (BYD) | V2 = 0 (zweiten Eingang offen lassen) | I1 = #6",
"BAUSTEIN.Z2_08": "Kleiner oder gleich | Günstige Stunde zum Laden (BYD) | V2 = 4 (zweiten Eingang offen lassen; die vier günstigsten Stunden der nächsten 24 h) | I1 = #6",
"BAUSTEIN.Z2_09": "UND | Strom günstig zum Laden (BYD) | — | I1 = #7, I2 = #8",
"BAUSTEIN.Z2_10": "ODER | Laden empfohlen (BYD) | — (Empfehlung des Plugins oder günstige Stunde) | I1 = #5, I2 = #9",
"BAUSTEIN.Z2_11": "UND | Laden empfohlen und angesteckt (BYD) | — | I1 = #10, I2 = #2",
"BAUSTEIN.Z2_12": "Virtueller Eingang (Schalter) | Laden nach Empfehlung (BYD) | in der App; ab Werk aus | —",
"BAUSTEIN.Z2_13": "UND | Ladefreigabe (BYD) | — | I1 = #11, I2 = #12",
"BAUSTEIN.Z2_14": "Einschaltverzögerung | Ladefreigabe bestätigt (BYD) | 60 s (schluckt den Impuls der Vergleicher bei jeder Abfrage); Ausgang Q an die Freigabe der eigenen Wallbox (nicht Teil der Liste); mit EVCC entfällt die Zeile – dort regelt EVCC | Eingang = #13",
"BAUSTEIN.Z2_15": "Status | Laden (BYD) | Zeilen: V5 = 1 „Wallbox freigegeben – Empfehlung des Plugins oder günstige Stunde“; V1 = 1 „lädt (Kennzahl <v3>) – letzte Ladung <v4.1> kWh“; V6 = 1 und V7 = 0 „Laden empfohlen – Schalter ‚Laden nach Empfehlung (BYD)‘ ist aus“; V2 = 1 „Kabel steckt, lädt nicht (Kennzahl <v3>)“; ohne Bedingung „kein Ladekabel – letzte Ladung <v4.1> kWh“; Visualisierung EIN | V1 = #1, V2 = #2, V3 = #3, V4 = #4, V5 = #14, V6 = #10, V7 = #12",
"BAUSTEIN.Z2_16": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_INNENTEMP | Innenraumtemperatur in °C | —",
"BAUSTEIN.Z2_17": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_BATTHEIZ | Batterieheizung als Kennzahl der Schnittstelle (Rohwert) | —",
"BAUSTEIN.Z2_18": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_SITZHEIZ | Sitzheizung Fahrersitz als Kennzahl der Schnittstelle (Rohwert) | —",
"BAUSTEIN.Z2_19": "Virtueller Eingang (Schieberegler) | Zieltemperatur (BYD) | Min 16, Max 30, Schritt 0,5, Startwert 21 (°C; außerhalb der Grenzen im Plugin, ab Werk 16–30, weist das Plugin den Befehl ab) | —",
"BAUSTEIN.Z2_20": "Virtueller Eingang (Taste) | Klima jetzt (BYD) | in der App; startet die Klimatisierung mit der Zieltemperatur | —",
"BAUSTEIN.Z2_21": "Schaltuhr | Abfahrt vorklimatisieren (BYD) | EIN = vorklimatisieren: Montag bis Freitag 06:40–07:00 (20 Minuten vor der Abfahrt um 07:00; eigene Abfahrtszeiten eintragen) | —",
"BAUSTEIN.Z2_22": "Virtueller Eingang | Anwesenheit (eigene Quelle) | 1 = jemand zu Hause (weitere Instanz, derselbe Eingang wie auf „Saugroboter“, „Chromecast4lox“, „Abfahrtsassistent“); im eigenen Projekt aus der eigenen Anwesenheit speisen | —",
"BAUSTEIN.Z2_23": "UND | Vorklimatisieren nur bei Anwesenheit (BYD) | — (im Urlaub klimatisiert nichts) | I1 = Ausgang AQ von #21, I2 = #22",
"BAUSTEIN.Z2_24": "ODER | Klima anfordern (BYD) | — (Taste oder Schaltuhr) | I1 = #20, I2 = #23",
"BAUSTEIN.Z2_25": "Formel | Klima-Sollwert (BYD) | IF(I1>0;I2;-1) – solange angefordert die Zieltemperatur, sonst -1 (den Wert -1 weist das Plugin ohne Wirkung ab; kein Digitalimpuls auf den Analogbefehl) | I1 = #24, I2 = #19",
"BAUSTEIN.Z2_26": "Virtueller Ausgang Befehl (Vorlage „BYD 1 steuern“) | BYD_1_KLIMA | Befehl bei Analogwert <v.1>: startet die Klimatisierung mit dieser Temperatur; kein Aus-Befehl (Klima aus über den eigenen Befehl); schreibende Befehle und Steuer-PIN im Plugin nötig | Eingang = #25",
"BAUSTEIN.Z2_27": "Virtueller Eingang (Taste) | Klima aus (BYD) | in der App; hält die Klimatisierung an | —",
"BAUSTEIN.Z2_28": "Virtueller Ausgang Befehl (Vorlage „BYD 1 steuern“) | BYD_1_KLIMA_AUS | Befehl bei EIN: Klimatisierung anhalten | Eingang = #27",
"BAUSTEIN.Z2_29": "Status | Klima (BYD) | Zeilen: V2 > 0 „klimatisiert auf <v2.1> °C – innen <v1.1> °C“; ohne Bedingung „aus – innen <v1.1> °C (Batterieheizung <v3>, Sitzheizung <v4> als Kennzahlen)“; Visualisierung EIN | V1 = #16, V2 = #25, V3 = #17, V4 = #18",
"BAUSTEIN.Z2_30": "Virtueller Eingang (Schieberegler) | Sitzheizung Stufe (BYD) | Min 0, Max 3, Schritt 1, Startwert 0 (0 = aus; welche Stufen das Fahrzeug kennt, ist nicht dokumentiert – im Plugin Reiter Test ‚Schalten‘ mit Trockenlauf ansehen) | —",
"BAUSTEIN.Z2_31": "Virtueller Ausgang Befehl (Vorlage „BYD 1 steuern“) | BYD_1_SITZKLIMA | Befehl bei Analogwert <v.0> (Stufe), bei AUS Stufe 0; sendet die Stufe bei jeder Änderung | Eingang = #30",
"BAUSTEIN.Z2_32": "Virtueller Eingang (Schalter) | Batterieheizung (BYD) | in der App; Ein = Stufe 1, Aus = Stufe 0 | —",
"BAUSTEIN.Z2_33": "Virtueller Ausgang Befehl (Vorlage „BYD 1 steuern“) | BYD_1_BATTERIEHEIZUNG | Befehl bei Analogwert <v.0> (Stufe), bei AUS Stufe 0 (folgt dem Schalter) | Eingang = #32",
"BAUSTEIN.Z2_34": "Virtueller Eingang (Taste) | Jetzt abrufen (BYD) | in der App; jeder Abruf weckt das Fahrzeug – nicht im Takt auslösen | —",
"BAUSTEIN.Z2_35": "Virtueller Ausgang Befehl (Vorlage „BYD 1 steuern“) | BYD_1_ABRUF | holt sofort neue Werte statt auf den Takt zu warten; nur Einbefehl | Eingang = #34",
"BAUSTEIN.Z3_01": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_SCHLOSSVL | Türschloss vorne links (Fahrertür) als Kennzahl der Schnittstelle; am einzigen gemessenen Fahrzeug, geparkt: 2 | —",
"BAUSTEIN.Z3_02": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_SCHLOSSVR | Türschloss vorne rechts als Kennzahl | —",
"BAUSTEIN.Z3_03": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_SCHLOSSHL | Türschloss hinten links als Kennzahl | —",
"BAUSTEIN.Z3_04": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_SCHLOSSHR | Türschloss hinten rechts als Kennzahl | —",
"BAUSTEIN.Z3_05": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_TUERVL | Tür vorne links als Kennzahl; am gemessenen Fahrzeug, geparkt: 0 | —",
"BAUSTEIN.Z3_06": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_TUERVR | Tür vorne rechts als Kennzahl | —",
"BAUSTEIN.Z3_07": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_TUERHL | Tür hinten links als Kennzahl | —",
"BAUSTEIN.Z3_08": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_TUERHR | Tür hinten rechts als Kennzahl | —",
"BAUSTEIN.Z3_09": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_KOFFER | Heckklappe als Kennzahl; am gemessenen Fahrzeug, geparkt: 0 | —",
"BAUSTEIN.Z3_10": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_FENSTERVL | Fenster vorne links als Kennzahl; am gemessenen Fahrzeug, geparkt: 1 | —",
"BAUSTEIN.Z3_11": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_FENSTERVR | Fenster vorne rechts als Kennzahl | —",
"BAUSTEIN.Z3_12": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_FENSTERHL | Fenster hinten links als Kennzahl | —",
"BAUSTEIN.Z3_13": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_FENSTERHR | Fenster hinten rechts als Kennzahl | —",
"BAUSTEIN.Z3_14": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_DACHFENSTER | Schiebedach als Kennzahl; am gemessenen Fahrzeug, geparkt: 1 | —",
"BAUSTEIN.Z3_15": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_OK | 1 = Werte frisch (weitere Instanz) | —",
"BAUSTEIN.Z3_16": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_TEMPO | Geschwindigkeit in km/h (weitere Instanz, auch auf Seite „BYD Autos Werte“) | —",
"BAUSTEIN.Z3_17": "Virtueller Eingang (Schieberegler) | Schloss-Kennzahl verriegelt (BYD) | Min 0, Max 9, Schritt 1, Startwert 2 (der Wert, den das gemessene Fahrzeug geparkt meldete; einmal mit der BYD-App vergleichen und bei Bedarf hier umstellen) | —",
"BAUSTEIN.Z3_18": "Ungleich | Fahrertür nicht verriegelt (BYD) | — (Kennzahl weicht von „verriegelt“ ab) | I1 = #1, I2 = #17",
"BAUSTEIN.Z3_19": "Formel | Abgestellt und Daten frisch (BYD) | IF(I1<1;I2;0) – 1 nur, wenn das Fahrzeug steht (Geschwindigkeit 0) UND die Werte frisch sind | I1 = #16, I2 = #15",
"BAUSTEIN.Z3_20": "UND | Offen und abgestellt (BYD) | — (während der Fahrt ist das Auto oft nicht verriegelt – das zählt nicht) | I1 = #18, I2 = #19",
"BAUSTEIN.Z3_21": "Einschaltverzögerung | Offen seit 5 Minuten (BYD) | 300 s (beim Ein- und Ausladen keine Meldung) | Eingang = #20",
"BAUSTEIN.Z3_22": "Benachrichtigung | Meldung Fahrzeug offen (BYD) | Text: BYD – die Fahrertür des abgestellten Fahrzeugs ist seit 5 Minuten nicht verriegelt. Bitte abschließen; Kennzahlen in der App unter „Türen und Schlösser (BYD)“ | Eingang = #21",
"BAUSTEIN.Z3_23": "Virtueller Eingang (Taste) | Fenster schließen (BYD) | in der App | —",
"BAUSTEIN.Z3_24": "Virtueller Eingang (Schalter) | Regensensor (eigene Quelle) | 1 = es regnet (weitere Instanz, derselbe Platzhalter wie auf „Robonect Steuerung“); im eigenen Projekt die Leitung vom eigenen Regensensor statt dieses Schalters | —",
"BAUSTEIN.Z3_25": "ODER | Fenster schließen auslösen (BYD) | — (Taste oder Regen) | I1 = #23, I2 = #24",
"BAUSTEIN.Z3_26": "Virtueller Ausgang Befehl (Vorlage „BYD 1 steuern“) | BYD_1_FENSTER_ZU | schließt alle Fenster; nur Einbefehl | Eingang = #25",
"BAUSTEIN.Z3_27": "Status | Türen und Schlösser (BYD) | Zeilen: ohne Bedingung „Schlösser <v1> / <v2> / <v3> / <v4>, Türen <v5> / <v6> / <v7> / <v8> (vorne links / vorne rechts / hinten links / hinten rechts; Kennzahlen der Schnittstelle – am gemessenen, geparkten Fahrzeug Schlösser 2, Türen 0)“; Visualisierung EIN | V1 = #1, V2 = #2, V3 = #3, V4 = #4, V5 = #5, V6 = #6, V7 = #7, V8 = #8",
"BAUSTEIN.Z3_28": "Status | Fenster und Klappen (BYD) | Zeilen: V7 = 1 „Fahrertür seit über 5 Minuten nicht verriegelt – Fenster <v1> / <v2> / <v3> / <v4>, Schiebedach <v5>, Heckklappe <v6>“; ohne Bedingung „Fenster <v1> / <v2> / <v3> / <v4> (vorne links / vorne rechts / hinten links / hinten rechts), Schiebedach <v5>, Heckklappe <v6> (Kennzahlen – am gemessenen, geparkten Fahrzeug Fenster und Schiebedach 1, Heckklappe 0)“; Visualisierung EIN | V1 = #10, V2 = #11, V3 = #12, V4 = #13, V5 = #14, V6 = #9, V7 = #21",
"BAUSTEIN.Z4_01": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_REIFENVL | Reifendruck vorne links in bar | —",
"BAUSTEIN.Z4_02": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_REIFENVR | Reifendruck vorne rechts in bar | —",
"BAUSTEIN.Z4_03": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_REIFENHL | Reifendruck hinten links in bar | —",
"BAUSTEIN.Z4_04": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_REIFENHR | Reifendruck hinten rechts in bar | —",
"BAUSTEIN.Z4_05": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_KM | Kilometerstand in km; Statistik ein | —",
"BAUSTEIN.Z4_06": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_VERBRAUCH | Verbrauch der letzten abgeschlossenen Fahrt (ab 20 km) in kWh/100 km, vom Plugin gerechnet; ohne Kapazität im Plugin kommt kein Wert | —",
"BAUSTEIN.Z4_07": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_VERBR50 | Durchschnittsverbrauch der letzten 50 km laut Fahrzeug in kWh/100 km | —",
"BAUSTEIN.Z4_08": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_VERBRBYD | Durchschnittsverbrauch laut Fahrzeug über die ganze Laufleistung in kWh/100 km | —",
"BAUSTEIN.Z4_09": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_TEMPO | Geschwindigkeit in km/h | —",
"BAUSTEIN.Z4_10": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_FAHRSTUFE | Fahrstufe als Kennzahl der Schnittstelle (Rohwert) | —",
"BAUSTEIN.Z4_11": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_ZUENDUNG | Zündung als Kennzahl der Schnittstelle (Rohwert) | —",
"BAUSTEIN.Z4_12": "Virtueller HTTP-Eingang-Befehl (Vorlage „BYD 1“) | BYD_1_OK | 1 = Werte frisch (weitere Instanz) | —",
"BAUSTEIN.Z4_13": "Formel | Kleinster Reifendruck (BYD) | MIN(MIN(I1;I2);MIN(I3;I4)) | I1 = #1, I2 = #2, I3 = #3, I4 = #4",
"BAUSTEIN.Z4_14": "Schwellwertschalter | Reifendruck niedrig (BYD) | Ein 2,2 / Aus 2,4 (bar; schaltet beim Unterschreiten von 2,2 bar ein, über 2,4 bar wieder aus) | Eingang = #13",
"BAUSTEIN.Z4_15": "UND | Reifendruck niedrig, Werte frisch (BYD) | — (nach einem Neustart des Miniservers stehen die Drücke bis zum ersten Abruf auf 0) | I1 = #14, I2 = #12",
"BAUSTEIN.Z4_16": "Einschaltverzögerung | Reifendruck niedrig bestätigt (BYD) | 600 s (zwei Abrufe; schluckt den Impuls des Schwellwertschalters bei jeder Abfrage) | Eingang = #15",
"BAUSTEIN.Z4_17": "Benachrichtigung | Meldung Reifendruck niedrig (BYD) | Text: BYD – ein Reifen hat weniger als 2,2 bar. Drücke stehen in der App unter „Reifendruck (BYD)“; Reifen prüfen und aufpumpen | Eingang = #16",
"BAUSTEIN.Z4_18": "Status | Reifendruck (BYD) | Zeilen: V5 = 1 „Reifendruck niedrig – vorne <v1.1> / <v2.1> bar, hinten <v3.1> / <v4.1> bar; Reifen prüfen“; ohne Bedingung „vorne <v1.1> / <v2.1> bar, hinten <v3.1> / <v4.1> bar“; Visualisierung EIN | V1 = #1, V2 = #2, V3 = #3, V4 = #4, V5 = #15",
"BAUSTEIN.Z4_19": "Impuls um | Tagesbeginn 0:00 (BYD) | Zu bestimmter Uhrzeit, 00:00:00 | —",
"BAUSTEIN.Z4_20": "Analogspeicher | Kilometerstand um Mitternacht (BYD) | übernimmt um 0:00 den Kilometerstand; Rem ein (Vorgabe), damit der Stand einen Neustart übersteht | V = #5, Set = Ausgang Q von #19",
"BAUSTEIN.Z4_21": "Formel | Heute gefahren in km (BYD) | IF(I2>0;IF(I1>=I2;I1-I2;0);0) – Kilometerstand minus Stand um Mitternacht; nach einem Neustart des Miniservers bis Mitternacht 0 | I1 = #5, I2 = #20",
"BAUSTEIN.Z4_22": "Status | Fahrt und Verbrauch (BYD) | Zeilen: V6 > 0 „fährt <v6> km/h – heute <v2> km, Kilometerstand <v1> km“; ohne Bedingung „steht – heute <v2> km, Kilometerstand <v1> km; Verbrauch letzte Fahrt <v3.1>, letzte 50 km <v4.1>, gesamt <v5.1> kWh/100 km (Fahrstufe <v7>, Zündung <v8> als Kennzahlen)“; Visualisierung EIN | V1 = #5, V2 = #21, V3 = #6, V4 = #7, V5 = #8, V6 = #9, V7 = #10, V8 = #11",
"LOX.BILD_ALT": "Bausteine des Plugins in Loxone Config",
"LOX.BILD_UNTERSCHRIFT": "Seite „%s“ im LoxBerry-Plugins Musterprojekt. Config kürzt lange Bausteinnamen – Namen siehe Tabelle.",
"LOX.MUSTERPROJEKT": "Die ganze Projektdatei mit allen Plugin-Seiten und Vorlagen: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry-Plugins Musterprojekt</a>",
"LOX.VORLAGEN_FAHRZEUG": "Vorlagen für Fahrzeug %s",
"LOX.VORLAGE_VO_EINGRIFF": "Mit dem zweiten Haken stehen auch Verriegelung, Fahrzeug suchen und Blinken darin.",
"LOX.EINGRIFF": "nur mit dem zweiten Haken",
"EINST.L_GEFAHR_EIN": "Eingreifende Befehle zulassen (Verriegeln und Entriegeln, Fahrzeug suchen, Blinken)",
"EINST.H_GEFAHR_EIN": "Ab Werk aus. Diese Befehle wirken auf ein Fahrzeug, das im öffentlichen Raum steht: ein versehentliches Entriegeln lässt es offen stehen, ohne dass es jemand merkt, und die Hupe weckt die Nachbarschaft. Der Haken darüber genügt dafür nicht – dieser wirkt <b>zusätzlich</b>. Ohne ihn weist der Endpunkt die Befehle mit <span class='sm-mono'>GRUND=EINGRIFF_GESPERRT</span> ab, der Dienst ebenso, und die Vorlage der Steuerbefehle enthält sie nicht. An keinem Fahrzeug erprobt.",
"TEST.F_GEFAHR": "Sind eingreifende Befehle zugelassen?",
"TEST.A_GEFAHR_AUS": "nein – ab Werk gesperrt, das ist kein Fehler",
"TEST.A_GEFAHR_EIN": "ja – Verriegeln und Entriegeln, Fahrzeug suchen und Blinken sind freigegeben",
"TEST.SCHALTEN_EINGRIFF_GESPERRT": "Verriegeln, Entriegeln, Fahrzeug suchen und Blinken sind zusätzlich gesperrt, bis im Reiter Einstellungen der zweite Haken „Eingreifende Befehle zulassen“ gesetzt ist; der Trockenlauf nennt die Sperre.",

# DRIFT-ABGLEICH 06.11.2026: 134 Schluessel, die in der veroeffentlichten
# BYD Autos 0.9.36 (templates/lang/language_de.ini) standen, aber nicht hier -
# wortgleich von dort uebernommen, in der Reihenfolge der .ini.
"ALLG.KACHEL_MQTT_HILFE": "Veröffentlichung dieses Plugins; Autostart des Gateways: %s; Gateway-Fassung: %s",
"ALLG.NICHT_FESTSTELLBAR": "nicht feststellbar",
"EINST.L_HAUS_FAHRZEUG_EIN": "Sammelthemen haus/fahrzeug/… senden",
"EINST.H_HAUS_FAHRZEUG_EIN": "Ab Werk an. Ladestand, Reichweite, Kabel, lädt und zu Hause unter <span class='sm-mono'>haus/fahrzeug/&lt;name&gt;/…</span> (<span class='sm-mono'>soc</span>, <span class='sm-mono'>reichweite_km</span>, <span class='sm-mono'>kabel</span>, <span class='sm-mono'>laedt</span>, <span class='sm-mono'>zuhause</span> retained, ohne Aussage ein Strich; <span class='sm-mono'>zaehler</span> nie retained), damit andere Plugins und Loxone ein Fahrzeug lesen können, gleich welcher Marke. Unabhängig vom Haken darüber. Kein Standort, keine Fahrgestellnummer. Ausschalten räumt die Themen ab.",
"EINST.H_SAMMEL_KABEL": "Kabel vergessen",
"EINST.SAMMEL_KABEL_HILFE": "Meldet sich, wenn das Auto zu Hause steht, das Kabel nicht steckt und der Akku unter der Schwelle liegt: höchstens einmal je Standzeit und je Tag, nur mit einem Fahrzeugstand bis 12 Stunden. In der Nachtruhe wartet die Meldung. Unbekannte Werte (kein Heimatort, kein Kabelwert) warnen nie. Der Haken für die Ansage steht bei den Anlässen der Sprachausgabe.",
"EINST.L_KABEL_SOC": "Warnen unter Akku (%)",
"EINST.L_KABEL_UHR": "Warnen ab Uhrzeit",
"EINST.L_KABEL_ABFAHRT_MIN": "Auch warnen, wenn die Abfahrt in so vielen Minuten ansteht",
"EINST.H_KABEL_ABFAHRT_MIN": "0 = nicht. Wirkt nur mit eingeschalteter Vorklimatisierung, sie liefert die Abfahrtszeit.",
"EINST.L_SIGNAL_KABEL": "Kabel vergessen über SignalBot melden",
"EINST.L_ANSAGE_KABEL": "Das Auto steht zu Hause ohne Kabel, der Akku ist niedrig",
"EINST.L_VORKLIMA_MIN_SOC": "Vorklimatisierung nur ab Akku (%)",
"EINST.H_VORKLIMA_MIN_SOC": "0 = keine Grenze. Darunter wird nicht gesendet, kein Versuch wird verbraucht (Thema vorklima = 5). Ist der Akkustand unbekannt, klimatisiert das Plugin wie bisher.",
"EINST.L_VORKLIMA_NUR_KABEL": "Vorklimatisierung nur mit gestecktem Kabel",
"EINST.H_VORKLIMA_NUR_KABEL": "Ab Werk aus. Steckt das Kabel nicht, wird nicht gesendet (Thema vorklima = 6). Ist es unbekannt, klimatisiert das Plugin wie bisher.",
"EINST.F_HAUS_FAHRZEUG": "Sammelthemen haus/fahrzeug",
"EINST.A_HAUS_FAHRZEUG": "gesendet für: %s",
"EINST.A_HAUS_FAHRZEUG_NOCH": "eingeschaltet, noch nichts gesendet (der Dienst sendet, sobald er ein Fahrzeug kennt)",
"EINST.A_HAUS_FAHRZEUG_AUS": "ausgeschaltet",
"EINST.A_HAUS_FAHRZEUG_FREMD": "Unter haus/fahrzeug/%s sendet auch eine andere Linie (fremder Zähler). Bitte einem der Fahrzeuge einen anderen Namen geben: Bis dahin überschreiben sich die Werte, und dieses Plugin räumt die Themen dort nicht ab.",
"EINST.SICH_REGELN": "Die Regeln der Sprachausgabe in dieser Datei sind ungültig; sie bleiben, wie sie sind.",
"EINST.O_PREISEMPF_HAUS": "Haus-Thema haus/strompreis (Spotpreis-Plugin als Anbieter)",
"EINST.SICH_SPAET": "Nicht in der Sicherung, unverändert: %s (die Sicherung stammt aus einer früheren Fassung).",
"LADUNG.T_KOSTEN": "Kosten",
"LADUNG.T_PREIS": "Preis",
"BY_FELD.LADEKOSTEN": "Kosten der letzten Ladung zu Hause (EUR, -1 ohne Aussage)",
"BY_FELD.LADEPREIS": "Durchschnittspreis der letzten Ladung zu Hause (ct/kWh, -1 ohne Aussage)",
"BY_FELD.VORKLIMA": "Vorklimatisierung: 0 nichts fällig, 1 gesendet, 2 mild (nicht nötig), 3 wartet auf Wiederholung, 4 wartet auf Anwesenheit, 5 nicht gesendet (Akku unter der Grenze), 6 nicht gesendet (Kabel fehlt), -1 gescheitert",
"BY_MQTT.STATUS_BEFEHLE": "Lebenszeichen der Befehlsbrücke (1 läuft, 0 aus).",
"BY_MQTT.ZAEHLER": "Lebenszeichen: zählt je Durchgang 0…999 weiter, nie behalten – steht er länger als drei Takte, ist der Dienst ausgefallen.",
"BEFEHL.F_BRUECKE": "Befehlsbrücke",
"BEFEHL.F_PRUEFEN": "Befehlsbrücke: Einrichtung (--pruefen)",
"BEFEHL.H_ANNEHMEN": "Startet die Befehlsbrücke: Loxone sendet <span class='sm-mono'>publish byd/befehl/&lt;name&gt; &lt;wert&gt;</span> an den Ausgang „LoxBerry MQTT-Gateway“, die Antwort steht unter <span class='sm-mono'>…/quittung</span> („angenommen“ heißt: an den Dienst übergeben). Ab Werk aus.",
"BEFEHL.H_ENDPUNKT": "Die virtuellen HTTP-Eingänge und -Ausgänge mit Token. Neue Anlagen nehmen das MQTT-Gateway V2 und die Befehlsbrücke; ausgeschaltet antwortet der Endpunkt mit 403. Eine Anlage, die von einer Fassung vor 0.9.29 aktualisiert wurde, hat ihn an.",
"BEFEHL.H_STEUERN": "Ver-/Entriegeln, Suchen und Blinken über MQTT – nur zusammen mit <i>Eingreifende Befehle zulassen</i> (Reiter Einstellungen). Ab Werk aus.",
"BEFEHL.H_TITEL": "Befehle aus Loxone über MQTT",
"BEFEHL.K_AUFFRISCHEN": "Werte abfragen",
"BEFEHL.K_AUSSENTEMP": "Außentemperatur aus Loxone",
"BEFEHL.K_BATTHEIZ": "Batterieheizung (Stufe, 0 aus)",
"BEFEHL.K_BLINKEN": "Blinken",
"BEFEHL.K_ENTRIEGELN": "Entriegeln",
"BEFEHL.K_FENSTER_ZU": "Fenster schließen",
"BEFEHL.K_KLIMA_AN": "Klimatisierung ein (Grad)",
"BEFEHL.K_KLIMA_AUS": "Klimatisierung aus",
"BEFEHL.K_SITZKLIMA": "Sitzklima (Stufe, 0 aus)",
"BEFEHL.K_SUCHEN": "Fahrzeug suchen (Hupe und Licht)",
"BEFEHL.K_VERRIEGELN": "Verriegeln",
"BEFEHL.K_VORLAGE": "Vorlage Befehle über MQTT",
"BEFEHL.L_ANNEHMEN": "Befehle über MQTT annehmen",
"BEFEHL.L_ENDPUNKT": "HTTP-Endpunkt für Loxone (bisheriger Weg)",
"BEFEHL.L_STEUERN": "Eingreifende Befehle auch über MQTT annehmen",
"BEFEHL.M_SCHALTEN_FEHL": "Die Befehlsbrücke ließ sich nicht schalten (%s): %s",
"BEFEHL.T_ART": "Art",
"BEFEHL.T_AUS": "aus (Haken „Befehle über MQTT annehmen“ nicht gesetzt).",
"BEFEHL.T_DEFEKT": "Die Einrichtung der Brücke ist fehlerhaft: %s",
"BEFEHL.T_KEINER": "Noch kein Befehl.",
"BEFEHL.T_LAEUFT": "läuft (%d Prozess) – angenommen %d, abgelehnt %d.",
"BEFEHL.T_LETZTER": "Letzter Befehl %s: %s, vor %d s.",
"BEFEHL.T_NICHT_DA": "Die Befehlsbrücke (bin/befehlsbruecke.php) fehlt.",
"BEFEHL.T_PRUEFEN_OK": "in Ordnung (Zuordnung, mosquitto_sub/_pub, Optionsdatei).",
"BEFEHL.T_STEHT": "soll laufen, steht aber (%s) – der Wächter startet sie binnen einer Minute neu.",
"BEFEHL.T_TITEL": "Titel in Loxone",
"BEFEHL.UDP_HINWEIS": "Der UDP-Eingang des MQTT-Gateways (11884) nimmt im Heimnetz <b>ohne Anmeldung</b> an – jedes Gerät im WLAN kann einen Befehl schicken. Deshalb ist alles ab Werk aus, und schaltende Befehle wirken zusätzlich nur mit <i>Schreibende Befehle zulassen</i>. Eingreifende Befehle (Ver-/Entriegeln, Suchen, Blinken) brauchen den zweiten Haken unten <b>und</b> <i>Eingreifende Befehle zulassen</i>; Ver- und Entriegeln brauchen weiter die hinterlegte S-PIN. Jeder Befehl landet in derselben Warteschlange wie der HTTP-Weg; Entprellung und Stundenbremse des Dienstes gelten für alle Wege gemeinsam.",
"BY_ANSAGE.S_KABEL": "%s steht ohne Ladekabel zu Hause, der Akku steht bei %s Prozent.",
"G42.FEHLER_SAMMEL": "Dieser Wert passt nicht: %s.",
"G42.A_ENDPUNKT_AUS": "ausgeschaltet – jeder Aufruf außer ?selftest=1 bekommt 403 ENDPUNKT_AUS (Neuinstallation; einschalten im Reiter MQTT).",
"G42.A_ENDPUNKT_EIN": "eingeschaltet – die HTTP-Vorlagen werden beantwortet.",
"G42.FEHLER_ANKUNFT": "Wer kommt an: tag:NAME oder person:NAME (Buchstaben, Ziffern, _ und -), kommagetrennt, höchstens vier; jemand und zaehler sind keine Personen.",
"G42.FEHLER_KALT_HEISS": "Kalt unter und Heiß über müssen ganze Zahlen von -30 bis 45 sein, kalt kleiner als heiß.",
"G42.FEHLER_PRAEFIX": "Das Präfix des SignalBot-Plugins: 1 bis 40 Zeichen aus Buchstaben, Ziffern, _ und -.",
"G42.F_ENDPUNKT_EIN": "HTTP-Endpunkt (bisheriger Weg)",
"G42.H_ANKUNFT": "Wechselt ein gewählter Tag oder eine Person live von 0 auf 1, fragt das Plugin das Konto einmal ab – höchstens einmal je 30 Minuten und nur, wenn der Stand älter als 5 Minuten ist.",
"G42.H_SIGNAL": "Meldungen an SignalBot",
"G42.H_SIGNAL_TEXT": "Ladung beendet, keine Daten mehr und gescheiterte Vorklimatisierung als Signal-Nachricht (über das SignalBot-Plugin). Das Musterprojekt schickt dieselben Meldungen auch aus Loxone – nur einen Weg einschalten, sonst kommen sie doppelt.",
"G42.H_STROMPREIS": "Während einer Ladung zu Hause merkt der Dienst je Minute den Endpreis; nach dem Ladeende stehen Kosten und Durchschnittspreis im Reiter Ladungen. Die Energie ist Akkustand-Differenz × Kapazität (Reiter Einstellungen) – ohne Kapazität keine Kosten. Fehlt der Preis für mehr als 10 % der Ladung, bleiben die Kosten -1, nie geschätzt.",
"G42.H_TEXT": "Alles ab Werk aus. Die Werte kommen über die Dauerverbindung des Dienstes von den Haus-Themen anderer Plugins (Abfahrts-Assistent, BLE-Scanner, Spotpreis); ein Wert gilt nur, solange der Zähler seiner Quelle sich binnen 120 s live ändert. Nur eine Quelle nutzen: Schaltuhr in Loxone <b>oder</b> diese Haken – sonst kommen zwei Befehle.",
"G42.H_TITEL": "Hausform: Haus-Themen, Ladekosten, SignalBot",
"G42.H_V2": "Gateway V2: diese Datenpunkte anhaken",
"G42.H_VORKLIMA": "Ausgelöst wird bei 1 bis Vorlauf Minuten vor der Abfahrt, höchstens zweimal „Klima ein“ je Abfahrt (Senden – Abruf – Senden), erledigt erst, wenn BYD den Auftrag angenommen hat. Die Außentemperatur kommt aus Loxone (Brücke, Befehl <span class='sm-mono'>aussentemp</span>, 30 min gültig) – BYD meldet keine. Ohne Haus-Thema gilt in dieser Fassung noch das bisherige Abfahrtsthema (nur live empfangen).",
"G42.LOG_BRUECKE": "Befehlsbrücke (befehle_start.log)",
"G42.LOG_CRONERR": "Fehlerausgabe des Wächters (cron.err)",
"G42.LOX_AUS": "Der HTTP-Endpunkt ist zurzeit <b>ausgeschaltet</b> (Reiter MQTT) – diese Vorlagen bekommen 403.",
"G42.LOX_BISHER": "Die HTTP-Vorlagen unten sind der <b>bisherige Weg</b>. Neue Anlagen nehmen das MQTT-Gateway V2 (Reiter MQTT, Datenpunkte anhaken) und die Befehlsbrücke (Vorlage im Reiter MQTT).",
"G42.L_ANKUNFT": "Bei Ankunft einmal abrufen",
"G42.L_ANKUNFT_QUELLE": "Wer kommt an? (tag:NAME oder person:NAME, kommagetrennt, höchstens vier)",
"G42.L_ANWESEND": "Vorklimatisierung nur, wenn jemand zu Hause ist (haus/anwesenheit)",
"G42.L_EMPF_QUELLE": "Quelle der Ladeempfehlung aus einem Thema",
"G42.L_HAUS_ABFAHRT": "Minuten bis zur Abfahrt aus dem Haus-Thema (haus/abfahrt)",
"G42.L_HEISS": "Heiß über (°C)",
"G42.L_KALT": "Kalt unter (°C)",
"G42.L_SIGNAL": "Meldungen an SignalBot senden",
"G42.L_SIGNAL_PRAEFIX": "Präfix des SignalBot-Plugins",
"G42.L_SIG_AUSFALL": "Keine Daten mehr (drei Abrufe)",
"G42.L_SIG_FERTIG": "Ladung beendet",
"G42.L_SIG_VORKLIMA": "Vorklimatisierung gescheitert",
"G42.L_STROMPREIS": "Strompreis vom Spotpreis-Plugin für die Ladekosten (haus/strompreis)",
"G42.L_WETTER": "Vorklimatisierung nur bei Kälte oder Hitze",
"G42.O_HAUS": "haus/strompreis/aktuell (Endpreis jetzt)",
"G42.O_THEMA": "eigenes Thema (wie bisher)",
"G42.T_NAME": "Gateway-Name",
"G42.V2_NUR_V1": "Gateway V1: es gilt das Abo oben (Rückfall). Mit Gateway V2 steht hier die Liste der anzuhakenden Datenpunkte.",
"G42.V2_TEXT": "Das MQTT-Gateway V2 leitet nur angehakte Datenpunkte an den Miniserver weiter. In Loxone heißt der virtuelle Eingang wie die Spalte <i>Gateway-Name</i>. <i>Noncached</i> nur dort, wo es steht (Lebenszeichen) – die Ausfallerkennung hängt an <span class='sm-mono'>byd_zaehler</span>.",
"HAUS.FRISCH": "frisch (Zähler zuletzt vor %d s live gewechselt).",
"HAUS.NIE": "noch kein live gewechselter Zähler gesehen –",
"HAUS.RUECK_ABFAHRT": "es gilt das bisher eingetragene Abfahrtsthema (Rückfall).",
"HAUS.RUECK_ANWESENHEIT": "die Vorklimatisierung wartet nicht auf Anwesenheit, und eine Ankunft löst keinen Abruf aus.",
"HAUS.RUECK_STROMPREIS": "Ladekosten bleiben -1, die Ladeempfehlung aus haus/strompreis geht als 0 hinaus.",
"HAUS.SCHWEIGT": "schweigt seit %d min –",
"HAUS.VK_AUFGEGEBEN": "gescheitert (zwei Versuche)",
"HAUS.VK_ERFOLG": "angenommen",
"HAUS.VK_FRAGE": "Vorklimatisierung vor der Abfahrt",
"HAUS.VK_FZ_FEHLT": "Fahrzeug %s gibt es im Konto nicht – es wird nichts gesendet (Einstellung „Fahrzeug“).",
"HAUS.VK_MILD": "mild – nicht nötig",
"HAUS.VK_NICHTS": "Fahrzeug %s: noch keine Abfahrt im Vorlauf gesehen.",
"HAUS.VK_OFFEN": "läuft",
"HAUS.VK_STAND": "Fahrzeug %s, Abfahrt %s, %d Versuch(e): %s.",
"HAUS.ZEILE": "Haus-Quelle %s",
"PRUEF.V2_FEHLT": "Es fehlen: %s.",
"PRUEF.V2_FRAGE": "Gateway V2: sind alle Datenpunkte angehakt?",
"PRUEF.V2_LEER": "nicht feststellbar – die Themenliste des Dienstes (bin/byd.py) ist leer oder nicht lesbar.",
"PRUEF.V2_NC": "Noncached falsch: %s.",
"PRUEF.V2_NICHT_EINGERICHTET": "noch nicht eingerichtet – angehakt wird, sobald Werte kommen (erst Zugangsdaten eintragen).",
"PRUEF.V2_UNKLAR": "nicht feststellbar – die Gateway-Fassung oder die Subscriptions des Gateways lassen sich nicht lesen.",
"PRUEF.V2_V1": "trifft nicht zu (Gateway V1 – dort gilt das Abo im Reiter MQTT).",
"PRUEF.V2_ZAHL": "%d von %d Datenpunkten angehakt.",
"SIGNAL.H_TEST": "Testmeldung an SignalBot",
"SIGNAL.H_TEST_TEXT": "Schickt einen festen Satz an <span class='sm-mono'>&lt;Präfix&gt;/befehl/senden</span> und wartet bis 5 s auf die Quittung der SignalBot-Brücke. Wirkt nur, wenn <i>Meldungen an SignalBot</i> eingeschaltet ist.",
"SIGNAL.K_TEST": "Testmeldung an SignalBot",
"SIGNAL.T_ABGELEHNT": "SignalBot hat die Testmeldung abgelehnt: %s",
"SIGNAL.T_ANGENOMMEN": "SignalBot hat die Testmeldung angenommen.",
"SIGNAL.T_AUS": "Meldungen an SignalBot sind aus – es wurde nichts gesendet.",
"SIGNAL.T_KEINE_ANTWORT": "Keine Antwort binnen 5 s – SignalBot nicht installiert oder seine Befehlsbrücke aus.",
"SIGNAL.T_NICHT_MOEGLICH": "Testmeldung nicht möglich – Dienstprogramm, paho-mqtt oder Broker fehlen, oder das Präfix ist ungültig.",
}

# ---------------------------------------------------------------------------
# Englisch
# ---------------------------------------------------------------------------
EN = {
# ---- Speech output (Nr. 36 b) ----
"EINST.H_ANSAGE": "Speech output (announcements, on by default)",
"EINST.ANSAGE_ERKLAERUNG": "The plugin can announce single events – through the Loxone Music Server, MusicServer4Home, an own address template, Alexa-NG or Google speakers (Chromecast 4 Lox NG). The output is <b>on</b> by default. Only a change is announced, never a value on every poll; the same event is announced for the same vehicle at most once per the set blocking time, not during the night rest, and after a restart of the service the first poll never speaks. MQTT, Loxone and notifications are not affected. Address and template must be in the home network.",
"EINST.H_ANSAGE_ANLAESSE": "Events",
"EINST.L_ANSAGE_LADEN_FERTIG": "Charging finished (with battery level)",
"EINST.L_ANSAGE_AUSFALL": "No more data (three polls in a row failed)",
"EINST.H_ANSAGE_ANLAESSE_HILFE": "Each event can be deselected; it only takes effect once an output is chosen above. Doors, lock, lights and climatisation are not announced: BYD reports doors and lock only as device-specific raw values, lights and climatisation not at all. The test announcement is on the <i>Test</i> tab.",
"EINST.SICH_TTS_TOKEN": "The file carries a speech token (%s). A backup of this plugin never contains one – the file is rejected, the current token stays.",
"EINST.SICH_TTS": "Invalid value in the speech output (tts): %s",
"EINST.SICH_OHNE_ANSAGE": "The backup comes from a version before 0.9.23 and does not know the speech output yet – its settings stay as they are.",
"EINST.SICH_OHNE_SPRECHTOKEN": "The speech tokens of the speech output (Alexa-NG, Chromecast 4 Lox NG) are never in the backup; enter them again after restoring on a new system.",
"TEST.F_ANSAGE": "Speech output",
"TEST.A_ANSAGE_ANLAESSE": "Events switched on (%s): %s.",
"TEST.A_ANSAGE_KEINE": "none",
"TEST.H_ANSAGE": "Speech output",
"TEST.ANSAGE_TEST_TEXT": "Speaks the test sentence through the chosen output – independent of the events.",
"TEST.K_ANSAGE_TEST": "Test announcement",
"TEST.M_ANSAGE_TEST_OK": "Test announcement sent.",
"TEST.M_ANSAGE_TEST_NICHTS": "No test announcement: %s",
"TEST.M_ANSAGE_TEST_FEHL": "Test announcement not sent: %s",
"BY_ANSAGE.FAHRZEUG_NR": "Vehicle %s",
"BY_ANSAGE.S_LADEN_FERTIG": "%s: Charging has finished.",
"BY_ANSAGE.S_LADESTAND": "Battery at %s percent.",
"BY_ANSAGE.S_AUSFALL": "BYD: no data for three polls.",

# ---- Verbesserungsbau 30.09.2026 (vb_byd: BYD-b1, BYD-b2, X-2, X-3, Laden-1) ----
"LADUNG.K_CSV": "Download charging sessions (CSV)",
"LADUNG.H_CSV": "Downloads <b>all</b> recorded charging sessions as a table, oldest first: vehicle, start, end, duration in minutes, state of charge before and after, odometer, kWh charged. Separator semicolon, decimal point; an empty field means <i>not known</i>. Without any charging session the file contains only the header line. The button changes nothing.",
"EINST.SICH_KOPF_HINWEIS": "Backup of the settings of the BYD Autos plugin. Contains the action token and the user name, password, control PIN and country of the BYD account - treat it like a password. Restore on the Settings tab; keys starting with _ are skipped on restore.",
"EINST.SICH_ALTWERT": "<b>This backup could not be restored as it is.</b> The saved value of %s would be rejected on restore (the same check as there). The file is still delivered in full and says so in its header. Correct the value in the form above, save, and then back up again.",
"EINST.SICH_ALTWERT_KOPF": "This backup could not be restored as it is - rejected would be: %s. Correct the value in the interface, save and back up again.",
"EINST.EINGABEN_ZURUECK": "The fields of this form show what you entered - nothing was saved. The field with the red border was rejected; please correct it and save again. For security reasons password and control PIN are not filled in again: a password you just typed was not accepted and has to be entered once more.",
"EINST.H_PREISEMPF": "Charging recommendation from Spotpreis aWATTar or Tibber",
"EINST.PREISEMPF_ERKLAERUNG": "The plugin listens to the <b>rank of the current hour</b> from one of the two Spotpreis plugins (1 = cheapest of the next 24 hours) and sends <code>lade_empfehlung</code> via MQTT: 1 if the hour is among the configured cheapest hours, otherwise 0, plus <code>lade_empfehlung_grund</code>. If the source is silent or no rank is available, <code>-</code> is sent and the Test tab shows it in yellow. It <b>switches nothing</b> on the car. Prerequisite: the Spotpreis plugin publishes via MQTT (switched on in its MQTT tab). After the service starts, the first rank only arrives with the next full set of the source - for aWATTar within 30 minutes, for Tibber with the next hour.",
"EINST.L_PREISEMPF_EIN": "Send the charging recommendation based on the electricity price",
"EINST.L_PREISEMPF_QUELLE": "Price source",
"EINST.O_PREISEMPF_AWATTAR": "Spotpreis aWATTar",
"EINST.O_PREISEMPF_TIBBER": "Spotpreis Tibber",
"EINST.H_PREISEMPF_QUELLE": "Selection field: which Spotpreis plugin supplies the rank. Both have to be installed as a plugin on this LoxBerry; only their MQTT topics are read, never their files.",
"EINST.L_PREISEMPF_PRAEFIX": "MQTT prefix of the price source",
"EINST.H_PREISEMPF_PRAEFIX": "Leave empty as long as the Spotpreis plugin uses its default prefix (aWATTar <code>spot_awattar</code>, Tibber <code>tibber</code>). If you changed it in that plugin (MQTT tab), enter it here the same way. Read are <code>&lt;prefix&gt;/rank</code>, <code>/rankd</code> and the heartbeat <code>/status/…</code>.",
"EINST.L_PREISEMPF_STUNDEN": "Cheapest hours per 24 hours",
"EINST.H_PREISEMPF_STUNDEN": "From 1 to 12. The recommendation is 1 if the rank of the current hour is at most this number - that is, it lies among that many cheapest hours of the next 24 hours. If only a few hours are known (before the prices for tomorrow are published), the shorter ranking counts.",
"EINST.FEHLER_PREISEMPF_QUELLE": "Price source: allowed are Spotpreis aWATTar and Spotpreis Tibber. The previous choice is kept.",
"EINST.SICH_R_QUELLE": "the price source is awattar or tibber.",
"BY_MQTT.LADE_EMPFEHLUNG": "Only with the charging recommendation based on the price switched on: 1 = the current hour is among the configured cheapest hours, 0 = it is not, - = no statement (price source silent, no rank, service ended or the setting just switched off). Sent on every change and otherwise every 5 minutes.",
"BY_MQTT.LADE_EMPFEHLUNG_GRUND": "Keyword for the recommendation: GUENSTIG, TEUER, QUELLE_SCHWEIGT, QUELLE_OHNE_PREISE, KEIN_RANG, HORCHER (no connection to the broker), AUS, DIENST_AUS. Text, not a virtual input.",
"TEST.F_PREISEMPF": "Does the charging recommendation based on the price arrive?",
"TEST.A_PREISEMPF_AUS": "it is switched off - no topic is sent",
"TEST.A_PREISEMPF_KEIN_DIENST": "switched on, but the polling service is not running - it is only computed in the service. There is no recommendation.",
"TEST.A_PREISEMPF_NOCH_NICHTS": "switched on, but the service has not stored a state yet (it computes every 30 seconds). Reload the page in a minute.",
"TEST.A_PREISEMPF_OK": "yes: recommendation %d - rank %d of %d, limit %d (source %s, topics <code>%s/rank</code>)",
"TEST.A_PREISEMPF_OHNE": "no statement from %s (topics <code>%s/…</code>): %s <code>-</code> is sent - there is no recommendation, as without this setting.",
"TEST.A_PREISEMPF_OHNE_MQTT": "MQTT is switched off on the MQTT tab - it is computed, but not sent.",
"TEST.PREIS_G_HORCHER": "no connection to the broker (see the line on the foreign MQTT topics).",
"TEST.PREIS_G_QUELLE_SCHWEIGT": "no heartbeat for more than 5 minutes. Is the Spotpreis plugin installed, does it publish via MQTT, and is the prefix right?",
"TEST.PREIS_G_QUELLE_OHNE_PREISE": "the source is alive but reports status/ok = 0 - it has no prices for today.",
"TEST.PREIS_G_KEIN_RANG": "the source is alive, but no rank arrived for more than 65 minutes. After the service starts this is normal until the next full set of the source.",
"TEST.PREIS_G_ANLAUF": "just switched on, started or the source changed - the first heartbeat of the source is still pending (up to 2 minutes).",

"REITER.EINSTELLUNGEN": "Settings",
"REITER.LOXONE": "Loxone integration",
"REITER.TEST": "Test",
"REITER.LOG": "Log files",

"LEGENDE.LESEN": "View — reads only, changes nothing",
"LEGENDE.TECHNIK": "Technical information — for troubleshooting",
"LEGENDE.AKTION": "Triggers something — sends or changes",
"LEGENDE.AKTION_TOKEN": "Triggers something — a new token invalidates every address in the Miniserver",
"LEGENDE.AKTION_LOG": "Triggers something — the existing lines are gone afterwards",

"ALLG.BEANSTANDUNG": "Please correct the following:",
"ALLG.FEHLER_FORMTOKEN": "The form did not carry a valid marker for this session. Nothing was changed. Please reload the page and submit again. If no action token exists yet, it is created when this page is first opened — then a reload is enough.",
"ALLG.FEHLER_FORMULAR": "The form did not identify itself. Nothing was changed — guessing the wrong form would delete exactly what was meant to be kept.",
"ALLG.DIENST": "Polling service",
"ALLG.LAEUFT": "running",
"ALLG.GESTOPPT": "stopped",
"ALLG.KEINE_PID": "no process id",
"ALLG.LETZTER_ABRUF": "Last poll",
"ALLG.NIE": "never",
"ALLG.FAHRZEUGE": "Vehicles",
"ALLG.FAHRZEUG": "Vehicle",
"ALLG.LIB_FEHLT": "library missing",
"ALLG.SELBSTPRUEFUNG": "Self-check",
"ALLG.HINWEISE": "plus %d notes",
"ALLG.LETZTE_STOERUNG": "Last fault:",
"ALLG.OHNE_NAMEN": "no model given",
"ALLG.SOC": "State of charge",
"ALLG.REICHWEITE": "Range",
"ALLG.KM": "Odometer",
"ALLG.VERLAUF_HINWEIS": "State of charge for today. One data point every four minutes at most.",
"ALLG.OHNE_TREFFER": "Fields with no match:",
"ALLG.OHNE_TREFFER_HINWEIS": "These fields stay empty because the library response contained none of the stored names. The button <b>Suggest field mapping</b> on the Test tab shows what the fields are really called in this version.",
"ALLG.AUSFAELLE": "Requests this vehicle did not answer:",
"ALLG.EIGENSCHAFT": "Property",
"ALLG.WERT": "Value",
"ALLG.SEKUNDEN": "seconds",
"ALLG.SPEICHERN": "Save",
"ALLG.EIN": "on",
"ALLG.AUS": "off",
"ALLG.JA": "yes",
"ALLG.NEIN": "no",

"EINST.UNGEPRUEFT": "<b>This version is untested.</b> The plugin was built without a BYD account and without a vehicle. BYD publishes no interface documentation; the field names come from open sources and were never measured against a car. What the installed library really returns is shown on the Test tab. Write commands are therefore disabled by default.",
# Kopf wie alle Hausplugins (Entscheidung Nr. 43, 0.9.24): gruener Kasten oben im Reiter Einstellungen, roh ausgegeben (by_t ohne by_e).
"EINST.WAS_IST_DAS": "<b>BYD vehicles via the BYD account on the Loxone Miniserver.</b> A polling service fetches state of charge, range, doors, locks and windows, tyre pressures, location and further values from the BYD cloud through the pybyd library at the configured interval. The values reach the Miniserver over MQTT and over a token-protected HTTP endpoint. Locking, climatisation and seat and battery heating can be switched through the same endpoint – disabled by default, and every command can be checked as a dry run first.",
"EINST.H_DIENST": "Polling service",
"EINST.DIENST_ERKLAERUNG": "The service fetches the values at the configured interval and stores them in a cache. The web interface and the Miniserver only read that cache — which is why the endpoint answers in milliseconds rather than seconds.",
"EINST.K_START": "Start service",
"EINST.K_RESTART": "Restart service",
"EINST.K_STOP": "Stop service",
"EINST.DIENST_START": "The service was started.",
"EINST.DIENST_STOP": "The service was stopped.",
"EINST.DIENST_RESTART": "The service was restarted.",
"EINST.H_KONTO": "BYD account",
"EINST.KONTO_ERKLAERUNG": "These are the credentials of the BYD account from the BYD app, not those of a dealer portal. They are kept in a separate file with mode 0600 and are never displayed — only their length. Leaving the password field empty deletes nothing.",
"EINST.L_BENUTZER": "User name",
"EINST.H_BENUTZER": "The same name you use to sign in to the BYD app — an e-mail address or a phone number, depending on the account. Nothing is rewritten: what you type is what is sent.",
"EINST.L_PASSWORT": "Password",
"EINST.H_PASSWORT": "Leaving this empty keeps the stored password.",
"EINST.PW_GESETZT": "stored, %d characters",
"EINST.PW_LEER": "none stored yet",
"EINST.L_PIN": "Control PIN",
"EINST.H_PIN": "The PIN the BYD app uses to authorise write commands. Without it BYD rejects every command; it is not needed for reading. Four to eight digits.",
"EINST.PIN_GESETZT": "stored",
"EINST.PIN_LEER": "none stored yet",
"EINST.L_LAND": "Country code",
"EINST.H_LAND": "Two letters, e.g. DE or AT. Only needed if the library asks for it — whether it does is shown by the service self-test on the Test tab, in the line about the recognised configuration fields. Leave empty if unsure.",
"EINST.L_ZUGANG_LOESCHEN": "Delete user name, password and PIN completely",
"EINST.H_ZUGANG_LOESCHEN": "This also deletes the backup copy next to the configuration folder. Without this box it would remain and reappear on the next fresh install — a deletion that does not delete is worse than none.",
"EINST.H_TAKT": "Polling interval",
"EINST.TAKT_WARNUNG": "Every poll <b>wakes the car</b>: the interface asks the vehicle to report rather than reading a cloud cache. Too short an interval costs standby power and may hit a rate limit. The lower bound of 120 seconds is our own choice, not a figure from BYD.",
"EINST.L_INTERVALL": "Interval in seconds",
"EINST.H_INTERVALL": "120 to 3600. The default of 300 seconds matches the default of the ioBroker adapter for the same interface.",
"EINST.L_VERLAUF_TAGE": "Keep history (days)",
"EINST.H_VERLAUF_TAGE": "One small CSV file per day and vehicle in the data folder. Older ones are removed.",
"EINST.L_GPS_EIN": "Poll location as well",
"EINST.H_GPS_EIN": "The location is a separate request. If you do not need it, you save one call per cycle — and the position of the car never leaves it.",
"EINST.L_MQTT_BIBLIOTHEK": "Allow the library to use its own MQTT path",
"EINST.H_MQTT_BIBLIOTHEK": "This is <b>not</b> the LoxBerry MQTT gateway but BYD's own broker: the library uses it to await confirmation of a command instead of polling. Without this box a confirmation takes longer. The path to the Miniserver is unaffected.",
"EINST.H_STEUERUNG": "Write commands",
"EINST.STEUERUNG_ERKLAERUNG": "Disabled by default, on purpose: a default that switches something unasked on first run is a bug. With this box the Miniserver may run the climate control, set seat and battery heating and close the windows. <b>Lock, unlock, find vehicle and flash lights</b> additionally need the second box below since 0.9.26. Whether BYD accepts a command is a different question — the receipt is not the effect.",
"EINST.L_STEUERUNG_EIN": "Allow write commands",
"EINST.L_TEMP_MIN": "Target temperature, lowest allowed value",
"EINST.L_TEMP_MAX": "Target temperature, highest allowed value",
"EINST.H_TEMP": "Limits for the climate control. A value outside is <b>rejected</b> rather than silently clamped: a quietly changed setpoint leads to a car doing something other than what is displayed.",
"EINST.L_WARTEZEIT": "Wait for the answer (seconds)",
"EINST.H_WARTEZEIT": "How long the web interface waits for the service to answer before reporting „result unknown“. 0 means: queue it and do not wait.",
"EINST.H_ERKANNT": "Detected vehicles",
"EINST.KEINE_FAHRZEUGE": "No vehicle is known yet. That is normal until the first successful poll: enter the credentials, start the service, wait one cycle.",
"EINST.T_NR": "No.",
"EINST.T_MARKE": "Make",
"EINST.T_MODELL": "Model",
"EINST.T_NAME": "Name in account",
"EINST.T_KENNZEICHEN": "Licence plate",
"EINST.T_VIN": "VIN",
"EINST.T_ANTRIEB": "Drive type",
"EINST.T_TBOX": "Telematics unit",
"EINST.VIN_HINWEIS": "The sequence number is sorted by VIN and therefore stable. In the Loxone addresses you may use the VIN instead of the number — that is the more durable choice.",
"EINST.GESPEICHERT": "The settings were saved.",
"EINST.NICHT_GESPEICHERT": "Nothing was saved: %d entr(y/ies) were rejected - they are listed above. The fields show what you entered; please correct them and save again.",
"EINST.HINWEIS_BENUTZER_GESAEUBERT": "Characters that must not appear were removed from the user name (control characters, quotation marks). The cleaned version was saved – if your account name really contains such characters, the login will fail.",
"EINST.HINWEIS_LAND_GESAEUBERT": "Characters were removed from the country code: “%s” became “%s”. Two letters are allowed.",
"EINST.FEHLER_ZAHL": "%s: please enter a whole number.",
"EINST.FEHLER_BEREICH": "%s: the value must be between %d and %d.",
"EINST.FEHLER_TEMP_TAUSCH": "The lowest target temperature is greater than the highest. Please swap them.",
"EINST.FEHLER_PIN": "The control PIN was not accepted, the previously stored one remains: it consists of four to eight digits.",
"EINST.FEHLER_LAND": "The country code was not accepted, the previous one remains: it consists of exactly two letters, e.g. DE.",
"EINST.FEHLER_ZUGANG_SPEICHERN": "The credentials could not be saved. Check the permissions of the configuration folder.",
"EINST.FEHLER_ZUGANG_LOESCHEN": "The credentials could not be deleted completely.",
"EINST.ZUGANG_GELOESCHT": "User name, password and PIN were deleted, and so was the backup copy.",
"EINST.WARN_PW_OHNE_KONTO": "A password is stored but no user name. Sign-in cannot succeed this way.",
"EINST.HINWEIS_PIN_FEHLT": "Write commands are enabled but no control PIN is stored. BYD will reject every command.",
"EINST.FEHLER_SPEICHERN": "The configuration could not be written (%s).",
"EINST.FEHLER_TOPIC": "The topic path may only contain letters, digits, hyphen, underscore and slash.",
"EINST.L_MQTT_EIN": "Send values over MQTT",
"EINST.L_MQTT_TOPIC": "Topic path",
"EINST.H_MQTT_TOPIC": "Prefix of every topic. Changing it later renames <b>every</b> topic on an existing installation — the virtual inputs in Loxone and the values in the broker depend on it.",

"MQTT.GATEWAY_ERKLAERUNG": "Since LoxBerry 3 the MQTT gateway is <b>part of the system</b>, not a plugin. It is not installed separately but switched on under <span class='sm-mono'>System → MQTT Gateway</span>.",
"MQTT.H_ZUSTAND": "State of the gateway",
"MQTT.NICHT_GEFUNDEN": "No MQTT section could be found in the LoxBerry <span class='sm-mono'>general.json</span>. Without it nothing can be forwarded.",
"MQTT.AUTOSTART_AUS": "The MQTT gateway is not set to autostart (<span class='sm-mono'>System → MQTT Gateway</span>). Messages are sent, but probably nobody is listening.",
"MQTT.AUTOSTART_EIN": "The gateway is set to autostart. It comes up by itself after a LoxBerry restart.",
"MQTT.T_AUTOSTART": "Gateway autostart",
"MQTT.T_BROKER": "Broker",
"MQTT.T_UDP": "UDP input of the gateway",
"MQTT.T_PLUGIN": "This plugin sends over MQTT",
"MQTT.H_ABO": "The subscription in the MQTT gateway",
"MQTT.ABO_WARNUNG": "<b>MQTT gateway V1.</b> The plugin enters this subscription itself in the file <span class='sm-mono'>mqtt_subscriptions.cfg</span> in its configuration folder, and gateway V1 reads it (established in the gateway source code). A manual entry under <i>System → MQTT Gateway</i>, section <i>Subscriptions</i>, is therefore no longer needed; if one is already there, it does no harm. If nothing arrives all the same, the subscription is the first place to look.",
"MQTT.ABO_SCHRITTE": "The topic group of this plugin is:",
"MQTT.H_THEMEN": "Every topic this plugin publishes",
"MQTT.THEMEN_ERKLAERUNG": "This list is built from the same source as the status line of the endpoint. The MQTT path therefore carries the same values as the HTTP path — a plugin whose MQTT message contains less than its HTTP line makes migration impossible, and does so quietly: values do arrive, just not all of them. The Test tab verifies the match.",
"MQTT.T_THEMA": "Topic",
"MQTT.T_BEDEUTUNG": "Meaning",
"MQTT.T_RETAIN": "Retained",
"MQTT.RETAIN_ERKLAERUNG": "Only states are sent retained – ignition, lock or charging state, for example – so that Loxone has the current picture straight after a restart of the Miniserver or the gateway. Measurements with a time reference are sent without, so that no old value looks current after an outage. The timestamp ts and the two OK topics are never retained: they are the sign of life. Nor is FEHLFOLGE: the count of unsuccessful polls is a statement of the service about itself, and a retained “0” would stay in place after the service has ended. A state without a statement is sent retained as <b>-</b> (dash), never empty. If a vehicle is only silent for a while, its states stay in place and fahrzeugN/OK goes to 0 – a state only counts together with OK. A measurement without a statement is sent as <b>-1</b> (the interior temperature as <b>-999</b>); latitude and longitude are then not sent at all, because -1 would be a real location there. The HTTP status line still shows a dash for it.",
"MQTT.PLATZHALTER": "<span class='sm-mono'>N</span> stands for the sequence number of the vehicle, starting at 1.",
"MQTT.UMBENENNUNG": "Over MQTT the <b>timestamp</b> is sent, not the age: at the moment of sending the age is always zero. The receiving side computes it. In Loxone: <span class='sm-mono'>age = (Loxone time + 1230768000) − ts</span> — Loxone counts seconds since 1 January 2009.",

"LOX.H_TITEL": "Loxone integration",
"LOX.EINLEITUNG": "Two paths are available, equivalent, and they do not exclude each other. Over <b>MQTT</b> the gateway creates the virtual inputs itself; the <b>HTTP endpoint</b> delivers all values of a vehicle in one request, with ready-made templates – and it is the only path for write commands. The sample project and the four pages in step 8 use HTTP.",
"LOX.S1_TITEL": "Step 1: choose the path",
"LOX.S1_TEXT": "Both paths are equivalent. <b>HTTP</b> (step 3): one template per vehicle, one request for all values, the age of every value comes along, and the browser shows right away what arrives – this is how the sample project and the pages in step 8 work. <b>MQTT</b> (off by default): the gateway creates the input names itself and additionally delivers the charging recommendation by electricity price. Both paths at once give duplicate inputs.",
"LOX.S2_TITEL": "Step 2: the subscription in the MQTT gateway",
"LOX.S2_TEXT": "The topic group of this plugin is:",
"LOX.S3_TITEL": "Step 3: virtual inputs over HTTP",
"LOX.S3_TEXT": "One virtual HTTP input with this address fetches all values in a single call. One command recognition per value, using the search text from the table below.",
"LOX.S3_BEFEHLE": "<p>The title is for humans, the search text for the machine: the title may change without any existing installation noticing — what is searched for is still the text in the second column. The semicolon belongs <b>in the pattern</b>: Loxone searches literally and takes the first hit, and without the semicolon <span class='sm-mono'>KM=</span> would also occur inside a future <span class='sm-mono'>RESTKM=</span>.</p>",
"LOX.S3_STRICH": "A <b>dash</b> as a value means: this value is not available. No 0 is sent on purpose — a 0 would look like a measurement. Loxone then keeps the last valid value, and the ALTER field says how old it is.",
"LOX.S3_HERKUNFT": "The <b>Origin</b> column is meant seriously. <b>Documentation</b> means: the field name comes from an open source and was never measured against a car here. <b>Computed</b> means: the field does not come from the vehicle at all but arises here — if an ingredient is missing it stays empty. A field nobody measured must not look like one somebody did. The Test tab shows which fields the library actually matched on <b>your</b> vehicle.",
"LOX.T_ADRESSE": "Address",
"LOX.T_ZYKLUS": "Polling cycle",
"LOX.T_TITEL": "Title (suggestion)",
"LOX.T_BEFEHL": "Search text (command recognition)",
"LOX.T_EINHEIT": "Unit",
"LOX.T_BEDEUTUNG": "Meaning",
"LOX.T_HERKUNFT": "Origin",
"LOX.HERKUNFT_DOKU": "documentation",
"LOX.HERKUNFT_BESTAND": "measured",
"LOX.HERKUNFT_GERECHNET": "computed",
"LOX.HERKUNFT_UNBEKANNT": "unknown origin (%s)",
"LOX.MEHRERE_FAHRZEUGE": "Several vehicles: one address per vehicle",
"LOX.H_ALLES": "Create everything at once",
"LOX.ALLES_TEXT": "The two buttons produce ready-made import files for Loxone Config. Inputs are imported under <span class='sm-mono'>Virtual Inputs → Predefined HTTP devices → Import template…</span>, outputs under <span class='sm-mono'>Virtual Outputs → Predefined devices → Import template…</span> — note that the output button lacks the word HTTP.",
"LOX.K_VORLAGE": "Create template for Loxone Config",
"LOX.K_VORLAGE_VO": "Create template for the control commands",
"LOX.VORLAGE_ZWEIMAL": "Loxone Config <b>creates new objects on import and overwrites nothing</b>. Importing twice means duplicate blocks on the same address — and Config says nothing about it.",
"LOX.VORLAGE_HINWEIS": "Created by the LoxBerry plugin BYD Autos. Importing twice results in duplicate blocks.",
"LOX.VORLAGE_UNGEPRUEFT": "This vehicle has never answered - all fields are included. After the first successful poll, fetch the template again; it will then contain only the fields the car really delivers.",
"LOX.VORLAGE_VO_HINWEIS": "Control commands of the LoxBerry plugin BYD Autos. They only work if write commands are enabled on the Settings tab.",
"LOX.S4_TITEL": "Step 4: location",
"LOX.S4_TEXT": "The location is returned in a separate response so that the status line consists of whole numbers only. A latitude with a decimal point among integers would be a trap for a command recognition.",
"LOX.S5_TITEL": "Step 5: sending commands",
"LOX.S5_TEXT": "One virtual output per command. Use the host name of the LoxBerry as the address of the output and the path from the table as the command; the generated import file does exactly that. Air conditioning, seat and battery heating are <b>analogue</b> outputs there: the value comes from the block driving the output – the target temperature as <span class='sm-mono'>&lt;v.1&gt;</span>, the level as <span class='sm-mono'>&lt;v.0&gt;</span>. Since 0.9.26 <b>climate</b> has no off command any more; it is stopped via its own command <span class='sm-mono'>BYD_1_KLIMA_AUS</span>; seat and battery heating send level 0 when switched off. This has not been measured on the Miniserver. Lock, unlock, find vehicle and flash lights additionally need the second tick on the Settings tab.",
"LOX.S5_WARNUNG": "These addresses contain the token. If you create a new token you must update all of them — a virtual output does not evaluate the answer, so a failure would go unnoticed.",
"LOX.S5_KEIN_LADEN": "<b>Starting and stopping charging is not offered here.</b> The library used names no method for it. An output the manufacturer cannot serve is not offered at all: a block that only collects refusals is worse than none.",
"LOX.S6_TITEL": "Step 6: token and self-test",
"LOX.S6_TEXT": "The token protects the unauthenticated endpoint. The second address answers the question „is the token entered in Loxone still valid?“ <b>without triggering anything on the car</b> — no device contact, no write access. Without such a route there are only two bad options: either you really switch something, or you never find out.",
"LOX.T_TOKEN": "Token",
"LOX.T_SELBSTTEST": "Self-test (triggers nothing)",
"LOX.K_TOKEN_NEU": "Create a new token",
"LOX.TOKEN_NEU": "A new token was created. All previous addresses in the Miniserver are now invalid and must be updated.",
"LOX.S7_TITEL": "Step 7: failure detection",
"LOX.S7_TEXT": "<b>Virtual inputs keep their last value.</b> If the service fails, everything looks normal in the app. Three things are therefore wired up: <span class='sm-mono'>OK</span> (0 means this poll returned nothing, or the snapshot is older than three times the polling interval), <span class='sm-mono'>ALTER</span> (grows as long as nothing new arrives) and a <b>Value Validator</b> on ALTER: if the LoxBerry itself stands still, OK and ALTER freeze, and only the validator notices that ALTER no longer changes (page “BYD Autos” in step 8, Tmc three times the polling time). The special case <span class='sm-mono'>ALTER = −1</span> means “there has never been a successful poll” – so always evaluate OK as well.",
"LOX.S8_TITEL": "Step 8: four pages from the sample project to rebuild",
"LOX.S8_TEXT": "Four pages from the LoxBerry plugins sample project, built and connected there in Loxone Config. One block per row; Loxone Config lists them all in the block search (key F5). If you only want monitoring, take over the first page alone. The names apply to vehicle 1 as the templates create them; the template titles are fixed (BYD_1_…), also with an English interface. The sample project does not use intervening commands (lock, find, flash).",
"LOX.T_BAUSTEIN": "Block (type)",
"LOX.T_NAMENSVORSCHLAG": "Name (suggestion)",
"LOX.T_PARAMETER": "Parameters",
"LOX.T_EINGAENGE": "Connect inputs to",
"LOX.S9_TITEL": "Step 9: cross-check",
"LOX.S9_TEXT": "Call these four addresses once in a browser. The fourth is the most important: only a <b>refusal</b> for an invented action makes the three successes meaningful.",
"LOX.T_PRUEFUNG": "Call",
"LOX.T_ERWARTUNG": "Expected answer",


"TEST.H_SELBSTPRUEFUNG": "Self-check",
"TEST.EINLEITUNG": "These checks answer <b>without Loxone and without a BYD account</b> whether the setup will work. Anything that could only be checked with an actual car is named as such at the end of the page.",
"TEST.BILANZ": "%d of %d checks passed, plus %d notes.",
"TEST.T_FRAGE": "Question",
"TEST.T_BEFUND": "Finding",
"TEST.LEGENDE_PUNKT": "A grey dot is a <b>note</b>: the line does not apply here, or cannot be measured in this setup. A yellow dot means: switched on, but the ingredient from another plugin is missing (such as the price source of the charging recommendation). Neither counts as passed — a summary must not look better than its worst item.",
"TEST.H_LESEN": "View",
"TEST.K_STATUS": "Call the status line",
"TEST.K_POSITION": "Call the location",
"TEST.K_FAHRZEUGE": "Call the vehicle list",
"TEST.K_SELFTEST": "Endpoint self-test",
"TEST.H_TECHNIK": "Technical information",
"TEST.K_SELBSTTEST": "Service self-test",
"TEST.K_ENDPUNKT": "Measure the endpoint now",
"TEST.K_FELDER": "Suggest field mapping",
"TEST.K_JSON": "View mapped image as JSON",
"TEST.H_FELDER_ERKLAERUNG": "<b>Suggest field mapping</b> queries the vehicle and lists <b>every leaf of the response with its path</b> — together with the field that matched it. That way the device answers the question about the names, not a guess. The call needs credentials and network access and takes a few seconds.",
"TEST.H_SCHALTEN": "Switching",
"TEST.SCHALTEN_WARNUNG": "<b>These buttons act on the car immediately.</b> They are not a dry run. Whether BYD accepts a command is stated in the answer; whether the car carries it out is only shown by the next poll.",
"TEST.SCHALTEN_GESPERRT": "Write commands are disabled. The buttons will be refused until the box on the Settings tab is ticked.",
"TEST.L_FAHRZEUG": "Vehicle",
"TEST.H_FAHRZEUG": "The sequence number from the vehicle list.",
"TEST.L_TEMP": "Target temperature in degrees Celsius",
"TEST.H_TEMP": "Whole or half degrees. Values outside the configured limits are refused.",
"TEST.L_MINUTEN": "Duration in minutes (optional)",
"TEST.H_MINUTEN": "Only effective if the installed library knows a parameter for it. If it does not, the answer says so explicitly — a value that does not arrive is named rather than quietly dropped.",
"TEST.L_STUFE": "Level for seat and battery heating",
"TEST.H_STUFE": "Which levels this vehicle supports is undocumented. 0 switches off.",
"TEST.K_ABRUF": "Poll now",
"TEST.H_UNGEPRUEFT": "What cannot be checked here",
"TEST.UNGEPRUEFT": "Whether sign-in to the BYD interface succeeds, whether the field names in this table apply to this vehicle, and whether the write commands have the expected effect on the car — that is decided by the account and the car, not here. The field names come from open sources and were never measured against a car here.",
"TEST.UNBEKANNT": "Result unknown:",
"TEST.KEINE_MESSPUNKTE": "no data points for today",
"TEST.F_ENDPUNKT": "Does our own endpoint answer over HTTP?",
"TEST.A_ENDPUNKT_AUS_SPEICHER": "this answer comes from the cache and is %d s old",
"TEST.A_ENDPUNKT_UNKLAR": "cannot be determined — neither curl nor allow_url_fopen is available here, or the web server cannot call itself while rendering this page. This says nothing about the endpoint.",
"TEST.A_ENDPUNKT_OK": "yes, HTTP 200 with the expected marker (measurement %d s old)",
"TEST.A_ENDPUNKT_FEHL": "no: HTTP %d, answer: %s",
"TEST.A_LEER": "empty",
"TEST.F_VENV": "Does the Python virtual environment exist?",
"TEST.A_VENV_FEHLT": "no — reinstall the plugin, the installation creates it",
"TEST.F_PYTHON": "Is Python new enough (3.11 or newer)?",
"TEST.A_PYTHON_ZU_ALT": "too old for pybyd",
"TEST.A_PYTHON_UNBEKANNT": "cannot be determined",
"TEST.F_LIB": "Can the library be loaded, and in which version?",
"TEST.A_LIB_FEHLT": "no — without pybyd the service cannot work",
"TEST.F_DIENST": "Is the polling service running?",
"TEST.A_DIENST_LAEUFT": "yes, process id",
"TEST.A_DIENST_SOLL_TOT": "no — it should be running but is not. The reason is in the Log files tab.",
"TEST.A_DIENST_GESTOPPT": "no, deliberately stopped",
"TEST.F_KONTO": "Is a user name stored?",
"TEST.A_KONTO_FEHLT": "no — see the Settings tab",
"TEST.F_PASSWORT": "Is a password stored?",
"TEST.A_PASSWORT_DA": "yes, %d characters (the content is never displayed)",
"TEST.A_PASSWORT_FEHLT": "no — see the Settings tab",
"TEST.F_PIN": "Is the control PIN stored?",
"TEST.A_PIN_DA": "yes, %d digits",
"TEST.A_PIN_FEHLT": "no — BYD will reject every write command",
"TEST.A_PIN_UNNOETIG": "not needed for reading. It is only required once write commands are enabled.",
"TEST.F_RECHTE": "Is the credentials file protected from other users?",
"TEST.A_ZUGANGSDATEI_FEHLT": "the credentials file is missing",
"TEST.F_SICHERUNG": "Is there a backup copy of the configuration?",
"TEST.A_SICHERUNG_FEHLT": "none yet. It is created on the first save and lives <b>next to</b> the configuration folder — inside it, it would be deleted along with the folder on update.",
"TEST.F_FAHRZEUGE": "Have vehicles been detected?",
"TEST.A_FAHRZEUGE": "yes, %d",
"TEST.A_KEINE_FAHRZEUGE": "no — that is normal until the first successful poll",
"TEST.F_ZUORDNUNG": "Were the fields found in the response?",
"TEST.A_ZUORDNUNG_LEER": "no statement possible: there is no vehicle in the cache. A check over an empty set is not a tick.",
"TEST.A_ZUORDNUNG_UNBEKANNT": "no statement possible: this vehicle record carries no list of unresolved fields at all. That does not mean “nothing is open” – it means nothing is known about it.",
"TEST.F_ZUORDNUNG_N": "Were the fields found for vehicle %s?",
"TEST.A_ZUORDNUNG": "%d of %d fields resolved",
"TEST.F_HERKUNFT": "Where do the field names come from?",
"TEST.A_HERKUNFT": "%d measured, %d from documentation, %d computed here. The second figure is not a defect but a property of this version: BYD publishes no interface documentation. The third does not come from the vehicle.",
"TEST.A_HERKUNFT_UNBEKANNT": "there are fields with an origin the interface does not know: %s. They would be named in the origin column but assigned to none of the three classes.",
"TEST.F_ABRUF": "How fresh is the cache?",
"TEST.A_NIE_ABGERUFEN": "there has not been a successful poll yet",
"TEST.A_ABRUF_ALTER": "%d seconds old",
"TEST.F_LETZTER_FEHLER": "Last reported fault",
"TEST.F_MQTT": "State of the MQTT gateway",
"TEST.A_MQTT_UNBENUTZT": "this plugin does not send over MQTT — the state of the gateway is then irrelevant",
"TEST.A_MQTT_NICHT_GEFUNDEN": "no MQTT section can be found in general.json",
"TEST.A_MQTT_AUS": "the gateway is not set to autostart. Without it nothing arrives at the Miniserver.",
"TEST.F_VORGABEN": "Do service and web interface use the same defaults?",
"TEST.A_VORGABEN_UNKLAR": "the list in the service could not be read — the comparison was not made",
"TEST.A_VORGABEN_OK": "yes, all %d defaults of the service also appear in the web interface",
"TEST.A_VORGABEN_FEHLT": "no — only in the service: %s",
"TEST.F_REITER": "Do the tab list, the tab bar and the panes agree?",
"TEST.F_AKTIV": "Does every tab carry the condition that makes it visible?",
"TEST.A_AKTIV_OK": "%d anchors in the bar and %d panes, each with the condition for sm-active",
"TEST.A_AKTIV_FEHL": "only %d of %d places carry the condition. A pane without it stays hidden and cannot be reached from the bar.",
"TEST.A_AKTIV_KEINE": "no statement possible: no tab bar was found.",
"TEST.F_VOLLSTAENDIG": "Does the stored configuration carry every key?",
"TEST.A_VOLLSTAENDIG_OK": "%d keys, none missing",
"TEST.A_VOLLSTAENDIG_FEHLT": "missing from the file: %s. The interface shows the default for these — and whoever does not touch it does not save it either.",
"TEST.A_VOLLSTAENDIG_KEINE": "no statement possible: there is no configuration file yet, or it cannot be read.",
"TEST.F_LEGENDEN": "Does every tab with buttons carry exactly one legend, and does it name the right colours?",
"TEST.A_LEGENDEN_OK": "%d tabs with buttons, each with exactly one legend; the colours match in both directions",
"TEST.A_LEGENDEN_FEHL": "not exactly one legend: %s — colours do not match: %s",
"TEST.A_LEGENDEN_KEINE": "no statement possible: there is no tab with buttons.",
"TEST.F_FORMULARE": "Does every form carry its marker, and does the allow list know it?",
"TEST.A_FORMULARE_OK": "%d forms, each with a marker; the allow list holds %d names",
"TEST.A_FORMULARE_FEHL": "only %d of %d forms carry a marker; not in the allow list: %s",
"TEST.A_FORMULARE_UNKLAR": "no statement possible: the allow list could not be found in index.php. That is a finding about this check, not about the forms.",
"TEST.A_FORMULARE_KEINE": "no statement possible: the page carries no form at all.",
"TEST.A_REITER_UNKLAR": "the list could not be read — the comparison was not made",
"TEST.A_REITER_OK": "yes, all three places carry the same %d names",
"TEST.A_REITER_FEHL": "no: list %d, bar %d, panes %d. If a name is missing from the list, the page jumps back after every submit.",
"TEST.F_MUSTER": "Is every search text in the status line unambiguous?",
"TEST.A_MUSTER_OK": "yes, all %d search texts occur exactly once",
"TEST.A_MUSTER_FEHL": "no — ambiguous: %s. Loxone takes the first hit and would deliver the value of another field.",
"TEST.F_WEGE": "Does the MQTT path carry the same values as the HTTP path?",
"TEST.A_WEGE_OK": "yes: %d values in the status line, %d topics in the list, matching the service",
"TEST.A_WEGE_FEHL": "no — without a topic: %s; only the service sends: %s; only the list names: %s",
"TEST.F_TEXTE": "Does every field and every command have a text in this language?",
"TEST.A_TEXTE_OK": "yes, all %d",
"TEST.A_TEXTE_FEHL": "no — without text: %s. The table would then show the key name.",
"TEST.F_AUSWAHL": "Are the select fields recognisable as such?",
"TEST.A_AUSWAHL_KEINE": "this page has no select field",
"TEST.A_AUSWAHL": "%d of %d select fields carry the marker, own arrow present: %s",
"TEST.F_MASKE": "Is any text escaped twice?",
"TEST.A_MASKE_OK": "no, %d escaped texts checked",
"TEST.A_MASKE_FEHL": "yes — affected: %s. The browser would show the entity verbatim.",
"TEST.F_STEUERUNG": "Are write commands enabled?",
"TEST.A_STEUERUNG_EIN": "yes",
"TEST.A_STEUERUNG_AUS": "no — that is the default and thus correct as long as nothing is to be switched",
"TEST.M_FAHRZEUG_UNGUELTIG": "The vehicle number is not a number.",
"TEST.M_TEMP_UNGUELTIG": "The target temperature is not a whole or half number.",
"TEST.M_STUFE_UNGUELTIG": "The level is not a number.",
"TEST.M_UNBEKANNT": "Unknown check.",
"TEST.M_FELDER_STUMM": "The call produced no output at all. That is not a field list – nor an error message that would tell you anything.",

"LOG.H_TITEL": "Log files",
"LOG.ERKLAERUNG": "Newest line first. The log is truncated to the last 200 lines above 500 kB, and the same message appears at most once per hour — otherwise a persistent fault drowns out every other line. <b>It does not survive a reboot:</b> the folder is a ramdisk. Copy out anything you want to keep.",
"LOG.LEER": "The log is empty.",
"LOG.K_LEEREN": "Clear the log",
"LOG.GELEERT": "The log was cleared.",

"BY_FELD.OK": "Poll succeeded (1) or not (0)",
"BY_FELD.SOC": "State of charge of the traction battery",
"BY_FELD.KM": "Odometer",
"BY_FELD.REICHW": "Remaining range",
"BY_FELD.LAEDT": "Vehicle is charging (1) or not (0)",
"BY_FELD.KABEL": "Charging cable connected (1) or not (0)",
"BY_FELD.LADEZUST": "Charge state as reported by the interface",
"BY_FELD.RESTMIN": "Remaining charging time",
"BY_FELD.FEHLFOLGE": "Consecutive unsuccessful polls (0 = the last poll returned values)",
"BY_FELD.ZUHAUSE": "Vehicle within the radius of the home position (1) or not (0)",
"BY_FELD.VERBRAUCH": "Consumption of the last completed trip",
"BY_FELD.LADEEMPF": "Charging recommendation derived from the price (1 = charge now)",
"BY_FELD.LADEKWH": "Energy charged during the last charging session",
"BY_FELD.TEMPO": "Speed",
"BY_FELD.FAHRZUST": "Vehicle state as reported by the interface",
"BY_FELD.ONLINE": "Vehicle reachable as reported by the interface",
"BY_FELD.ZUENDUNG": "Ignition as reported by the interface",
"BY_FELD.SCHLOSSVL": "Door lock front left (driver door)",
"BY_FELD.BATTHEIZ": "Battery heating as reported by the interface",
"BY_FELD.SITZHEIZ": "Driver seat heating as reported by the interface",
"BY_FELD.ALTER": "Age of the cache",
"BY_FELD.BREITE": "Latitude of the location",
"BY_FELD.LAENGE": "Longitude of the location",
"BY_FELD.REIFENVL": "Tyre pressure front left",
"BY_FELD.REIFENVR": "Tyre pressure front right",
"BY_FELD.REIFENHL": "Tyre pressure rear left",
"BY_FELD.REIFENHR": "Tyre pressure rear right",
"BY_FELD.VERBRBYD": "Average consumption as reported by the vehicle, cumulative over the whole mileage",

# Neu 15.09.2026 (Issue #1). Die Kennzahlen heissen ausdruecklich "als Kennzahl
# der Schnittstelle": gemessen ist, WELCHE Zahl an einem Fahrzeug dastand,
# nicht, wofuer sie steht.
"BY_FELD.INNENTEMP": "Cabin temperature",
"BY_FELD.FAHRSTUFE": "Gear as reported by the interface",
"BY_FELD.SCHLOSSVR": "Door lock front right (passenger door)",
"BY_FELD.SCHLOSSHL": "Door lock rear left",
"BY_FELD.SCHLOSSHR": "Door lock rear right",
"BY_FELD.TUERVL": "Door front left (driver door) as reported by the interface",
"BY_FELD.TUERVR": "Door front right (passenger door) as reported by the interface",
"BY_FELD.TUERHL": "Door rear left as reported by the interface",
"BY_FELD.TUERHR": "Door rear right as reported by the interface",
"BY_FELD.KOFFER": "Tailgate as reported by the interface",
"BY_FELD.FENSTERVL": "Window front left as reported by the interface",
"BY_FELD.FENSTERVR": "Window front right as reported by the interface",
"BY_FELD.FENSTERHL": "Window rear left as reported by the interface",
"BY_FELD.FENSTERHR": "Window rear right as reported by the interface",
"BY_FELD.DACHFENSTER": "Sunroof as reported by the interface",
"BY_FELD.REIFENEH": "Unit code of the tyre pressures as reported by the interface: 1 = bar, 2 = psi, 3 = kPa; the plugin always converts the four pressures to bar (MQTT and aktion=json only)",
"BY_FELD.VERBR50": "Average consumption over the last 50 km as reported by the vehicle",

"BY_BEF.ABRUF": "Poll now",
"BY_BEF.VERRIEGELN": "Lock",
"BY_BEF.ENTRIEGELN": "Unlock",
"BY_BEF.KLIMA_START": "Start climate control",
"BY_BEF.KLIMA_STOP": "Stop climate control",
"BY_BEF.KLIMA_PLAN": "Schedule climate control",
"BY_BEF.SITZKLIMA": "Set seat heating",
"BY_BEF.BATTHEIZ": "Set battery heating",
"BY_BEF.SUCHEN": "Find the car (horn and lights)",
"BY_BEF.BLINKEN": "Flash the lights",
"BY_BEF.FENSTER_ZU": "Close the windows",

"BY_MQTT.OK": "1 if the last poll returned values, otherwise 0. Sent on every cycle, including during a fault.",
"BY_MQTT.TS": "Timestamp of the last successful measurement, in Unix seconds. The receiving side computes the age from it — over MQTT the age is always zero at the moment of sending.",
"BY_MQTT.FAHRZEUGE": "Number of detected vehicles",
# ---- Pre-conditioning driven by the departure assistant --------------------
"EINST.H_ABFAHRT": "Pre-conditioning via the departure assistant",
"EINST.ABFAHRT_ERKLAERUNG": "<b>Unverified.</b> The departure assistant publishes the minutes until departure (<code>ABFAHRT_IN</code>) and a release value (<code>OK</code>) below its topic path. This plugin <i>listens</i> and issues the climate command once the lead time is reached. All that has been measured so far is that the assistant carries these two topics — not that a BYD vehicle accepts the climate command. Leave this off until the dry run on the Test tab shows otherwise.",
"EINST.L_ABFAHRT_EIN": "Enable pre-conditioning",
"EINST.L_ABFAHRT_PRAEFIX": "Topic path of the departure assistant",
"EINST.H_ABFAHRT_PRAEFIX": "Without a slash at the start or end. Subscribed are <code>&lt;path&gt;/ABFAHRT_IN</code> and <code>&lt;path&gt;/OK</code>. Empty means: nothing is subscribed and nothing is switched.",
"EINST.L_ABFAHRT_VORLAUF": "Lead time before departure (minutes)",
"EINST.H_ABFAHRT_VORLAUF": "This many minutes before the announced departure the climate command is issued — once per departure, not repeatedly.",
"EINST.L_ABFAHRT_TEMP": "Target temperature for pre-conditioning (°C)",
"EINST.L_ABFAHRT_FAHRZEUG": "Vehicle used for pre-conditioning",
"EINST.H_ABFAHRT_FAHRZEUG": "The number from the Test tab. The departure assistant knows nothing about vehicles, so a fixed choice has to be made here.",
"EINST.L_ABFAHRT_ALTER": "Maximum age of the departure message (seconds)",
"EINST.H_ABFAHRT_ALTER": "Older messages count as expired and trigger nothing. A stale value left in the broker would otherwise claim the same departure every day.",
"EINST.FEHLER_ABFAHRT_TEMP": "The pre-conditioning target temperature (%d °C) is outside the limits for writing commands (%d to %d °C).",
"EINST.FEHLER_THEMA": "%s: letters, digits, hyphen, underscore and slash are allowed — no wildcards such as + or #.",

# ---- Charging recommendation ----------------------------------------------
"EINST.H_LADEEMPF": "Charging recommendation based on price",
"EINST.LADEEMPF_ERKLAERUNG": "The plugin listens to an existing price value in the broker and derives the field <code>LADEEMPF</code> from it (1 = charge now, 0 = do not). It <b>switches nothing</b>: the recommendation is a value for the Loxone logic, so that it stays visible there who triggers the charge. The price must come from another source — BYD supplies none.",
"EINST.L_LADEEMPF_EIN": "Compute the charging recommendation",
"EINST.L_LADEEMPF_THEMA": "MQTT topic carrying the price",
"EINST.H_LADEEMPF_THEMA": "The complete topic as it appears in the broker, without wildcards. Without a topic nothing is computed and nothing is sent.",
"EINST.L_LADEEMPF_GRENZE": "Threshold",
"EINST.H_LADEEMPF_GRENZE": "In the same unit as the value in the topic. Comma or dot, both are understood.",
"EINST.L_LADEEMPF_UNTER": "Recommend when the value is BELOW the threshold",
"EINST.H_LADEEMPF_UNTER": "Ticked for prices (cheap = charge), unticked for surplus (plenty = charge). Which direction is right depends solely on what the topic means — which is why it is not guessed.",
"EINST.L_LADEEMPF_ALTER": "Maximum age of the price value (seconds)",
"EINST.H_LADEEMPF_ALTER": "If the last price value is older, <code>LADEEMPF</code> is set to 0. A recommendation that falls silent must say 0 rather than say nothing: in Loxone a missing value reads like the last valid one.",
"EINST.FEHLER_LADEEMPF_OHNE_THEMA": "The charging recommendation is enabled but no MQTT topic is set. It would compute nothing.",
"EINST.FEHLER_DEZIMAL": "%s: please enter a number, using a comma or a dot as the separator.",
# B-Nachzug 01.10.2026 (vb_byd2, Nr. 19): access field as an array instead of text.
"EINST.FEHLER_KEIN_TEXT": "%s: the input did not arrive as a single text and was not accepted.",
# Follow-up 01.10.2026 (vb_byd2, no. 19/21): a slash at the edge is rejected.
"EINST.FEHLER_THEMA_RAND": "%s: enter it without a slash at the start or end – in the broker /home/byd is a different topic from home/byd.",

# ---- Computed values ------------------------------------------------------
"EINST.H_GERECHNET": "Computed values",
"EINST.GERECHNET_ERKLAERUNG": "These fields do not come from the vehicle, they are computed here. If an ingredient is missing the field stays empty — a 0 that looks like a measurement is never sent.",
"EINST.L_KAPAZITAET": "Usable battery capacity (kWh)",
"EINST.H_KAPAZITAET": "From the registration document or the data sheet. It is the ingredient for charged energy and for consumption; 0 means both stay empty. BYD does not supply this value.",
"EINST.L_HEIM_BREITE": "Home position: latitude",
"EINST.KARTE": "Open the map (mapatlas.eu): enter the address, copy the numbers under „Decimal degrees“",
"EINST.KARTE_ZUSAMMEN": "Both numbers may also be pasted here together (e.g. 50.123, 8.456); the plugin splits them when saving.",
"EINST.L_HEIM_LAENGE": "Home position: longitude",
"EINST.H_HEIM": "Decimal degrees, as in Loxone. Both values or none — no distance can be computed from half a position. This produces the field <code>ZUHAUSE</code>.",
"EINST.L_HEIM_RADIUS": "Radius (metres)",
"EINST.H_HEIM_RADIUS": "Within this radius the vehicle counts as being at home. Chosen too small the field flickers, because even a parked vehicle reports scattered positions.",
"EINST.FEHLER_HEIM_HALB": "The home position needs latitude AND longitude. With only one value no distance can be computed; the field stays empty.",

# ---- Charging sessions tab ------------------------------------------------
"REITER.LADUNGEN": "Charging sessions",
"LADUNG.H_TITEL": "Detected charging sessions",
"LADUNG.ERKLAERUNG": "A charging session is detected from a change of the field <code>LAEDT</code> — BYD does not report it. The list lives in <code>verlauf/ladungen.csv</code> in the data folder. <b>The installer wipes that folder on every update</b>; the plugin therefore carries the list across itself: <code>preupgrade.sh</code> puts it next to the configuration folder, <code>postinstall.sh</code> fetches it back. It does <b>not</b> survive an uninstall — that removes this backup copy as well. Copy the file out of the data folder beforehand if you want to keep it past that.",
"LADUNG.LEER": "No charging session recorded yet. An entry is only made once the service has seen a <i>change</i> from „charging“ to „not charging“ — a session already running at the first start therefore does not count.",
"LADUNG.K_ANZAHL": "Recorded",
"LADUNG.K_ANZAHL_H": "rows in the file",
"LADUNG.K_SUMME": "Energy charged",
"LADUNG.K_SUMME_H": "computed over %d of %d rows, only those with a capacity on file",
"LADUNG.T_START": "Start",
"LADUNG.T_ENDE": "End",
"LADUNG.T_DAUER": "Duration",
"LADUNG.T_SOC": "State of charge",
"LADUNG.T_KM": "Odometer",
"LADUNG.T_KWH": "kWh",
"LADUNG.GENAUIGKEIT": "<b>What these numbers are.</b> Start and end are the moments of the <i>polls</i> at which the change was noticed — they may be off by up to one polling interval. The kWh are computed from the change in state of charge and the capacity on file, not measured: charging losses are not in them, and a wrongly entered capacity distorts every row by the same factor.",

# ---- Dry run --------------------------------------------------------------
"TEST.L_PROBE": "Dry run: only show what would happen",
"TEST.H_PROBE": "When ticked the command takes the same path up to immediately before sending: the guards apply, the vehicle and the library function are looked up, the parameters are checked — only nothing is dispatched. The answer then starts with „PROBE“. This is the way to settle the field mapping and the command names on a real vehicle without moving it.",

# ---- Check rows of the new functions ---------------------------------------
"TEST.F_HORCHER": "Are the foreign MQTT topics subscribed?",
"TEST.A_HORCHER_UNNOETIG": "no function needs a foreign topic — pre-conditioning and charging recommendation are off",
"TEST.A_HORCHER_FEHLER": "no, the service reports: %s",
"TEST.A_HORCHER_KEIN_DIENST": "the service is not running — %d topics would have to be subscribed, nothing can be compared here",
"TEST.A_HORCHER_ABWEICHUNG": "no. Not subscribed: %s. Subscribed in addition: %s. As long as a topic is missing the corresponding function never triggers, and that looks like a silent counterpart.",
"TEST.A_HORCHER_OK": "yes, %d topics and the broker is connected: %s",
"TEST.A_HORCHER_GETRENNT": "the topic list agrees, but the service is not connected to the broker. Is the MQTT gateway running, and are user and password correct?",
"TEST.F_SELBSTBEZUG": "Does the plugin listen to itself?",
"TEST.A_SELBSTBEZUG_UNNOETIG": "no foreign topic is subscribed",
"TEST.A_SELBSTBEZUG_OK": "no, no subscribed topic lies below its own path (%s)",
"TEST.A_SELBSTBEZUG_FEHL": "yes: %s lies below the plugin's own topic path %s. The plugin would be its own supplier — the charging recommendation would compute from its own result, the pre-conditioning would wait for a departure nobody announces.",
"TEST.F_ABFAHRT": "Can the pre-conditioning switch at all?",
"TEST.A_ABFAHRT_AUS": "it is switched off",
"TEST.A_ABFAHRT_GESPERRT": "no: it is enabled, but writing commands are blocked. It would dispatch nothing at departure time — an enabled function that does nothing goes unnoticed.",
"TEST.A_ABFAHRT_TEMP": "no: the target temperature %d °C is outside the limits %d to %d °C, the command would be rejected",
"TEST.A_ABFAHRT_OK": "yes, %d minutes before departure to %d °C, vehicle %d. Whether BYD accepts the command is shown only by the dry run.",
"TEST.F_ZUTATEN": "Are the ingredients of the computed values present?",
"TEST.A_ZUTATEN_HALB": "no: the home position is only half filled in. No distance can be computed from a single value, the field ZUHAUSE stays empty — even though something is entered.",
"TEST.A_ZUTATEN_OK": "yes: %d kWh capacity and a home position with a %d m radius",
"TEST.A_ZUTATEN_OFFEN": "not complete, and that is allowed. Missing: %s. The fields depending on it stay empty instead of sending a 0.",
"TEST.Z_KAPAZITAET": "the battery capacity (VERBRAUCH and LADEKWH stay empty)",
"TEST.Z_HEIM": "the home position (ZUHAUSE stays empty)",
"TEST.F_LADUNGEN": "Can the list of charging sessions be read?",
"TEST.A_LADUNGEN_KEINE": "no file has been created yet — only a detected change from „charging“ to „not charging“ writes the first row",
"TEST.A_LADUNGEN_OK": "yes, %d of %d rows read",
"TEST.A_LADUNGEN_UNLESBAR": "no: the file has %d rows, but not one of them could be read. The tab would show an empty list and thereby claim that charging never happened.",

# NACHGEPFLEGT 31.08.2026. Diese 21 Schluessel standen in der
# ausgelieferten .ini und im PHP, aber nicht mehr hier - ein Lauf
# haette sie geloescht. Die Werte sind aus der .ini geholt und mit
# der umgekehrten Tabelle aus umlaute_umstellen.py in die
# Entitaetenform zurueckgerechnet.
"EINST.H_SICHERUNG": "Back up and restore settings",
"EINST.K_SICHERN": "Back up settings",
"EINST.K_ZURUECK": "Restore",
"EINST.H_ZURUECK": "Restore a backup",
"EINST.H_ZURUECK_TEXT": "Takes effect immediately: the file overwrites the stored settings. A partly valid file changes nothing at all — everything is checked first, then written. Every value is checked with the same rule as in the form, the credentials included; an empty token in the file means: the current one stays.",
"EINST.SICH_ABGELEHNT": "The file was <b>not</b> accepted — nothing has been changed:",
"EINST.SICH_ERKLAERUNG": "For <b>moving to a second LoxBerry</b>: the file contains all settings of this plugin and can be restored there.",
"EINST.SICH_FREMD": "Unknown setting in the file: %s",
"EINST.SICH_FEHLEND": "The file is missing %d settings: %s. An incomplete backup is not restored — otherwise the missing values would silently fall back to the factory defaults, with nothing on the page to show it.",
"EINST.SICH_WERT": "The value of %s is not usable as a setting — it is neither a number nor text, or too long, or it contains control characters.",
"EINST.SICH_BEREICH": "%s is outside the permitted range (%d to %d).",
"EINST.SICH_KEINE_DATEI": "No file was selected, or the upload failed.",
"EINST.SICH_KEIN_JSON": "The file is not a valid backup of this plugin.",
"EINST.SICH_LEER": "The file contains no known setting.",
"EINST.SICH_SCHREIBFEHLER": "The settings could not be written.",
"EINST.SICH_UEBERNOMMEN": "Settings restored: %d values taken over.",
"EINST.SICH_WARNUNG": "<b>The file contains your credentials.</b> Without them all fields would look right after restoring and the plugin still would not reach the installation. Treat the file like a password: do not post it in a forum and do not attach it to a bug report.",
"EINST.SICH_ZU_GROSS": "The file is larger than allowed — a backup of this plugin is a few kilobytes.",
"MQTT.ABO_GEMESSEN": "(measured: gateway&nbsp;V%d)",
"MQTT.ABO_UNBEKANNT": "The version of your MQTT gateway could not be determined. <b>Version&nbsp;1</b> reads the subscription file the plugin creates itself – no manual entry is needed. <b>Version&nbsp;2:</b> whether the topic group appears there by itself has not been measured on this installation.",
"MQTT.ABO_V2": "<b>MQTT gateway V2.</b> Only what is in the LoxBerry source code is established: under V2 the <i>Subscriptions</i> page has its own interface and its buttons are disabled. That the topic group appears there by itself and the data points are ticked has <b>not been measured</b> on this installation. The plugin creates its subscription file anyway; whether V2 reads it has not been measured either.",
"TEST.H_ROHDATEN": "Raw data from the BYD far end",
"TEST.K_ROH": "View raw data from the far end",
"TEST.ROHDATEN_LEER": "There is no raw data yet. Only after the first successful poll is there anything to see here.",
"TEST.ROHDATEN_STAND": "As of: %s",
"TEST.ROHDATEN_WARNUNG": "These are the <b>real field names</b> of your vehicle, exactly as the far end delivers them. That is what you need to check whether this plugin’s mapping fits: if a value stays empty, a wrongly guessed field name is more likely than a fault. The view exists only here in the authenticated area — the file carries permissions 0600, because vehicle identifier and position are in it.",

# ---- Marker of a running update (0.9.15) -----------------------------------
"UPGRADE.T_TITEL": "An update of this plugin is in progress.",
"UPGRADE.T_TEXT": "Until it has finished, this page shows no settings, saves nothing and does not start the service. Your credentials and the previous settings are restored at the end of the installation. Please reload the page in a minute.",
"TEST.F_MARKE": "Is there a marker „update in progress“?",
"TEST.A_MARKE_KEINE": "no — this plugin is not being updated right now",
"TEST.A_MARKE_GILT": "yes, for %d seconds. While it is valid the page saves nothing and the service is not started.",
"TEST.A_MARKE_ALT": "a marker from %d minutes ago is still lying there. It is no longer valid — after an hour it does not count, so that an aborted installation cannot shut the plugin down for good. It may be deleted: %s",
"TEST.A_MARKE_UNLESBAR": "a marker is lying there, but its content is not a Unix time. It is therefore not valid and blocks nothing; it may be deleted: %s",
# Nachgezogen 30.09.2026 aus dem Bau 0.9.19 (Durchgang)
"ALLG.ANMELDESPERRE": "Sign-in to BYD was rejected %d times within 24 hours. The plugin no longer signs in until new credentials are saved on the Settings tab – so BYD does not lock the account.",
"ALLG.VORGANG_GESCHEITERT": "The action did not succeed:",
"EINST.FEHLER_TOPIC_EBENE": "The topic path must not contain an empty level (two slashes in a row) – the service would otherwise publish under a different topic than this page shows.",
"EINST.SICH_OHNE_ZUGANG": "The file contains no credentials (backup of an older version) – the stored ones remain unchanged.",
"EINST.SICH_REGEL": "%s was not accepted: %s",
"EINST.SICH_R_BENUTZER": "the user name contains control characters or quotation marks.",
"EINST.SICH_R_DEZIMAL": "a number with a decimal point within the permitted range is expected.",
"EINST.SICH_R_LAND": "the country code consists of two capital letters or is empty.",
"EINST.SICH_R_PIN": "the control PIN consists of four to eight digits or is empty.",
"EINST.SICH_R_PRAEFIX": "the topic path follows the rule of the MQTT tab: letters, digits, hyphen, underscore and slash, no empty level, no slash at the edge.",
"EINST.SICH_R_SCHALTER": "a switch only knows 0 and 1.",
"EINST.SICH_R_THEMA": "the topic follows the rule of the form (letters, digits, hyphen, underscore, slash, no slash at the edge) or is empty.",
"EINST.SICH_R_TOKEN": "the action token consists of 1 to 64 characters (letters, digits, dot, hyphen, underscore) or is empty.",
"EINST.SICH_R_UNBEKANNT": "no rule is defined for this value.",
"EINST.SICH_R_ZUGANG": "the value is not text or contains control characters.",
"EINST.SICH_ZUGANG_UEBERNOMMEN": "The BYD account credentials from the file have been taken over; they apply from the next start of the service.",
"MQTT.ABGERAEUMT": "Retained topics under the previous prefix %s:",
"MQTT.ABODATEI_FEHLER": "The subscription file mqtt_subscriptions.cfg could not be written – please check the subscription in the MQTT gateway by hand.",
"MQTT.ABODATEI_NEU": "The subscription file of the MQTT gateway now reads %s.",
"LOX.S3_OK": "OK is 0 as soon as the snapshot is older than three times the polling interval (currently %d seconds); ALTER stays unchanged beside it. If there is no data at all yet, the endpoint answers with HTTP 503 and GRUND=KEINE_DATEN.",
"TEST.A_ABRUF_OHNE_DIENST": "the service is not running, freshness is not judged",
"TEST.A_MERKMAL_FEHL": "no — only %d of %d forms carry a token with a value; submitting the others is rejected.",
"TEST.A_MERKMAL_KEINE": "no statement possible: the page has no form.",
"TEST.A_MERKMAL_OK": "yes: %d of %d forms",
"TEST.A_WEGE_UNKLAR": "no statement possible: the topics of the service could not be read from bin/byd.py.",
"TEST.F_MERKMAL": "Does every form of the rendered page carry a token with a value?",
"LOG.BLEIBT": "Only byd.log was cleared; settings, credentials, charging sessions and the start file byd_start.log remain untouched.",
"LOG.H_BESTAETIGEN": "Without the tick nothing happens. Only byd.log is cleared – the previous lines are gone afterwards. Settings, credentials, charging sessions and the start file byd_start.log remain.",
"LOG.L_BESTAETIGEN": "Yes, clear the log",
"LOG.NICHT_BESTAETIGT": "The log was not cleared: the confirmation tick was missing.",
"LOG.NICHT_GELEERT": "The log could not be cleared: %s is not writable. It is unchanged.",
"BY_MQTT.FZ_OK": "1 if the last poll returned values for this vehicle, otherwise 0 – this is how a partial outage shows. Also sent during a fault, without credentials and when the service ends.",
"MELDUNG.DIENSTSKRIPT_FEHLT": "dienst.sh not found: %s",
"MELDUNG.DIENST_UNBEKANNT": "Unknown command.",
"MELDUNG.EXEC_DIENST": "exec() is disabled in this PHP set-up. The service cannot be controlled from here.",
"MELDUNG.EXEC_GESPERRT": "exec() is disabled in this PHP set-up - byd.py cannot be called from here.",
"MELDUNG.KEIN_DIENST": "The polling service is not running - nothing was queued. Settings tab, button Start service.",
"MELDUNG.KEIN_JSON": "The command could not be expressed as JSON (invalid UTF-8).",
"MELDUNG.NICHT_ABGELEGT": "The command could not be stored: %s",
"MELDUNG.OHNE_ANTWORT": "Queued, but the service did not answer within %d s. The result is therefore unknown - no success is reported that nobody has checked.",
"MELDUNG.ORDNER_FEHLT": "The folder for the queue could not be created: %s",
"MELDUNG.VENV_FEHLT": "The virtual Python environment or byd.py is missing. Expected: %s and %s. Remedy: reinstall the plugin; the installation creates both.",
"MELDUNG.VENV_FEHLT_KURZ": "The virtual Python environment or byd.py is missing - nothing was cleared.",

# ---- Welle Bild 17 (BYD Autos 0.9.26, 17.10.2026; Entwurf Welle 17 by, gemeinsame Form der fuenf Autos):
# vier Seiten aus dem LoxBerry-Plugins Musterprojekt - Kasten- und Hinweistitel, Kaesten BAUSTEIN.Sn_SCHRITTm,
# Hinweise BAUSTEIN.Sn_Hm, Tabellenzeilen BAUSTEIN.Zn_mm = "Typ | Name | Parameter | Eingaenge"
# (by_bausteinseiten() in htmlauth/index.php); LOX: Bild, Link, Vorlage-Knoepfe je Fahrzeug, zweiter Haken an
# Vorlage und Befehlstabelle; EINST/TEST: der zweite Haken (Hausherr 17.10.2026). ---------------------------
"BAUSTEIN.SCHRITTE_TITEL": "How to take over this page",
"BAUSTEIN.HINWEISE_TITEL": "Notes",
"BAUSTEIN.S1_SCHRITT1": "In the plugin tab “%s” enter user name, password and control PIN of the BYD account, press “%s” and wait one interval (5 minutes). If you want charged energy and consumption, enter the usable battery capacity; if you want “at home”, the home position. Tab “%s” → “%s”: a line BYD;OK=1;SOC=… comes back",
"BAUSTEIN.S1_SCHRITT2": "Tab “%s” → for “vehicle 1” the buttons “%s” and “%s”. In Loxone Config import the inputs: select “Virtual Inputs” in the tree, ribbon “Predefined HTTP devices → Import template…”; the control commands: in the tree “Virtual Outputs” → “Predefined devices → Import template…”. Import each file only ONCE (twice gives duplicate blocks). The two containers “BYD 1” and “BYD 1 steuern” serve all four pages.",
"BAUSTEIN.S1_SCHRITT3": "Create the page “BYD Autos”. Drag the 11 commands of the list from the container “BYD 1” (no. 1–11), plus the constant 1. Switch on “Statistics” in the properties window of BYD_1_SOC and BYD_1_REICHW.",
"BAUSTEIN.S1_SCHRITT4": "Create three notifications (Periphery → Messages → Notification): “Meldung Auto gestört (BYD)”, “Meldung Ladestand niedrig (BYD)” and “Meldung Ladung beendet (BYD)”, texts as in the list. Each gets exactly one connection.",
"BAUSTEIN.S1_SCHRITT5": "Place the remaining blocks via the block search (key F5), parameters as in the list, connect from top to bottom. On the Value Validator no. 13 remove the tick at ‘En’ in the properties window (Config creates En inverted; otherwise constant 1 arrives as 0). AND no. 24: negate input I2 – click its input point in Config; the input then shows a small circle. Status no. 18: click “+” twice first (V5, V6), status no. 27 three times (V5–V7); enter the rows in the given order, the one without condition last. Edge Detection no. 29: the connection to the notification leaves from output Off.",
"BAUSTEIN.S1_SCHRITT6": "Save and transfer. Check: “Zustand (BYD)” shows “läuft – Werte … s alt”; BYD_1_ALTER jumps back every 5 minutes.",
"BAUSTEIN.S1_H1": "The message “Auto gestört” only comes after 10 minutes of fault. If the LoxBerry itself stands still, the Value Validator notices it after 15 minutes; the message follows 10 minutes later.",
"BAUSTEIN.S1_H2": "On no. 13: if the LoxBerry stands still, all inputs keep their last value; only the frozen BYD_1_ALTER gives it away. Every poll wakes the vehicle – do not set the interval in the plugin below 300 s; if you raise it or the polling time on the container, set Tmc to three times the polling time.",
"BAUSTEIN.S1_H3": "On no. 19–25: a threshold switch behind a polled input gives a short pulse at every poll; the switch-on delay no. 25 swallows it. The formulas no. 19 and 21 make sure that a value never reported (0, for example after a restart of the Miniserver) does not count as low.",
"BAUSTEIN.S1_H4": "On no. 28–30: “Meldung Ladung beendet” comes at every end of charging after at least one minute of charging – also when the cable is pulled or the charge is aborted.",
"BAUSTEIN.S1_H5": "The announcements “Ladung beendet” and “Keine Daten mehr” are spoken by the plugin itself (tab Settings, voice output, on by default) – no block is needed for them.",
"BAUSTEIN.S1_H6": "Second vehicle: in the tab “Loxone integration” fetch the templates for vehicle 2 (container “BYD 2”, commands BYD_2_…) and create the pages a second time with these commands; lead the faults of both vehicles via a further OR before the switch-on delay – never two sources directly into one notification.",
"BAUSTEIN.S1_H7": "A dash from the plugin means “not available” – the input then keeps its last value. Once the vehicle has answered, the input template only contains the fields it delivers; before that all 42, as in the sample project.",
"BAUSTEIN.S2_SCHRITT1": "In the plugin tab “%s” set the tick “%s” (off by default) and enter the control PIN. If you want the charging recommendation of the plugin: switch on “%s” and enter the MQTT topic with price or surplus.",
"BAUSTEIN.S2_SCHRITT2": "The containers “BYD 1” and “BYD 1 steuern” come from the page “BYD Autos”, step 2 (do not import them again). Create the page “BYD Autos Laden und Klima”, drag the 8 commands from “BYD 1” (no. 1–5 and 16–18), plus spot_awattar_rank (create a virtual input named as in the name table on the tab “Loxone integration” of the plugin Spotpreis aWATTar, from 1.2.38 on; without the spot price plugin leave out no. 6–9 and leave input I2 of no. 10 free) and the five output commands BYD_1_KLIMA, BYD_1_KLIMA_AUS, BYD_1_SITZKLIMA, BYD_1_BATTERIEHEIZUNG and BYD_1_ABRUF from “BYD 1 steuern”.",
"BAUSTEIN.S2_SCHRITT3": "Create seven virtual inputs (switches no. 12 and 32, sliders no. 19 and 30, push buttons no. 20, 27 and 34; each with “Use in User Interface” on) and drag “Anwesenheit (eigene Quelle)” from the tree. Place the schedule no. 21 via the block search and enter ON Monday to Friday 06:40–07:00 in the schedule editor; its output AQ goes to the AND no. 23.",
"BAUSTEIN.S2_SCHRITT4": "Place the remaining blocks via the block search (key F5), parameters as in the list, connect them. Greater no. 7 and Less or Equal no. 8: enter the comparison value as parameter V2, leave the second input open. Status no. 15: click “+” three times first (V5–V7).",
"BAUSTEIN.S2_SCHRITT5": "Save and transfer. Check: press “Klima jetzt (BYD)” – the plugin tab “%s” shows the command klima_start at 21 °C; “Klima aus (BYD)” stops the climate control.",
"BAUSTEIN.S2_H1": "“Ladefreigabe bestätigt (BYD)” (no. 14) is the switching output for a wallbox without its own control. If you use EVCC, leave out no. 12–14: EVCC controls the wallbox itself. The vehicle cannot start or stop charging via BYD – the plugin offers no command for it.",
"BAUSTEIN.S2_H2": "On no. 7–9: spot_awattar_rank -1 means “no rank” and does not count as cheap; without the spot price plugin the input stays 0, so never cheap. The switch-on delay no. 14 swallows the pulse of the comparators at every poll.",
"BAUSTEIN.S2_H3": "On no. 25 and 26: the climate command is analogue and sends the target temperature (<v.1>). As long as nothing is requested, the formula delivers -1 – the plugin rejects this value without effect. Stopping only works via “Klima aus (BYD)” (no. 27 and 28).",
"BAUSTEIN.S2_H4": "The target temperature must lie between the limits in the plugin (16–30 °C by default), otherwise the plugin rejects the command and nothing happens. How long the vehicle runs the climate control is decided by BYD.",
"BAUSTEIN.S2_H5": "If you have switched on the preconditioning at the departure assistant in the plugin, leave the schedule no. 21 empty – otherwise there are two triggers for the same climate control. The schedule only preconditions when “Anwesenheit (eigene Quelle)” is 1 (nothing on holiday).",
"BAUSTEIN.S2_H6": "Seat and battery heating: level 0 switches off – the off command of the control template sends it (since 0.9.26). Which levels the vehicle knows is not documented; look at it in the plugin tab Test “Switching” with a dry run.",
"BAUSTEIN.S2_H7": "Every immediate poll (no. 34 and 35) wakes the vehicle – do not trigger the push button cyclically.",
"BAUSTEIN.S3_SCHRITT1": "The containers come from the page “BYD Autos”, step 2 (do not import them again). Create the page “BYD Autos Fahrzeug”, drag the 16 commands from “BYD 1” (no. 1–16), the output command BYD_1_FENSTER_ZU from “BYD 1 steuern” and “Regensensor (eigene Quelle)” from the tree.",
"BAUSTEIN.S3_SCHRITT2": "Create two virtual inputs: the slider no. 17 “Schloss-Kennzahl verriegelt (BYD)” (start value 2) and the push button no. 23 “Fenster schließen (BYD)” (each with “Use in User Interface” on). Create the notification “Meldung Fahrzeug offen (BYD)”, text as in the list.",
"BAUSTEIN.S3_SCHRITT3": "Place the remaining blocks via the block search (key F5), parameters as in the list, connect them. Status no. 27: click “+” four times first (V5–V8), status no. 28 three times (V5–V7).",
"BAUSTEIN.S3_SCHRITT4": "Compare once with the BYD app: lock the vehicle, read BYD_1_SCHLOSSVL after the next poll and set the slider “Schloss-Kennzahl verriegelt (BYD)” to this value (2 on the measured vehicle).",
"BAUSTEIN.S3_SCHRITT5": "Save and transfer. Check: press “Fenster schließen (BYD)” – the plugin tab “%s” shows the command fenster_zu.",
"BAUSTEIN.S3_H1": "BYD delivers locks, doors and windows only as codes; what 0, 1 or 2 means is not described by BYD. That is why no. 18 compares with the slider instead of a fixed value.",
"BAUSTEIN.S3_H2": "On no. 19–21: while driving the car is often not locked – a message only comes when it is standing (speed 0) and the values are fresh, and only after 5 minutes.",
"BAUSTEIN.S3_H3": "When it rains the Miniserver sends “close windows” once – even if the vehicle is parked elsewhere; that does no harm.",
"BAUSTEIN.S3_H4": "Locking, unlocking, find vehicle (horn and lights) and flashing are deliberately not on this page: they act on a vehicle in a public place. The plugin only offers them with a second tick (“%s”, off by default); without it the endpoint rejects them and the control template does not contain them.",
"BAUSTEIN.S4_SCHRITT1": "Create the page “BYD Autos Werte”, drag the 12 commands from “BYD 1” (no. 1–12); switch on “Statistics” in the properties window of BYD_1_KM.",
"BAUSTEIN.S4_SCHRITT2": "Create the notification “Meldung Reifendruck niedrig (BYD)”. Place the remaining blocks via the block search (key F5) and connect them: Pulse at no. 19 “At a specific time” 00:00:00; the Analog Memory no. 20 keeps Rem (default). Status no. 18: click “+” once first (V5), status no. 22 four times (V5–V8).",
"BAUSTEIN.S4_SCHRITT3": "Save and transfer. Check: compare “Reifendruck (BYD)” with the BYD app.",
"BAUSTEIN.S4_H1": "“Heute gefahren” shows 0 until midnight after a restart of the Miniserver.",
"BAUSTEIN.S4_H2": "The plugin only calculates the consumption of the last trip with an entered battery capacity (trips from 20 km); the vehicle reports the other two consumption values itself.",
"BAUSTEIN.S4_H3": "The tyre pressures always arrive in bar; the vehicle may report bar, psi or kPa (REIFENEH 1/2/3), the plugin converts. So 2.2 and 2.4 bar at no. 14 fit every vehicle. -1 means: implausible value (unknown unit) – no. 14 then reports as well; check the tyres and REIFENEH.",
"BAUSTEIN.S4_H4": "Gear position and ignition are codes of the interface without a described meaning; the status only shows them.",
"BAUSTEIN.Z1_01": "Virtual HTTP input command (template “BYD 1”) | BYD_1_OK | 1 = last poll brought values and they are at most three times as old as the poll interval (300 s by default), otherwise 0 | —",
"BAUSTEIN.Z1_02": "Virtual HTTP input command (template “BYD 1”) | BYD_1_ALTER | seconds since the last successful poll; -1 = never one so far – the sign of life: changes at every poll | —",
"BAUSTEIN.Z1_03": "Virtual HTTP input command (template “BYD 1”) | BYD_1_FEHLFOLGE | unsuccessful polls in a row; 0 = the last one brought values | —",
"BAUSTEIN.Z1_04": "Virtual HTTP input command (template “BYD 1”) | BYD_1_ONLINE | reachability of the vehicle as a code of the interface (raw value, meaning not documented) | —",
"BAUSTEIN.Z1_05": "Virtual HTTP input command (template “BYD 1”) | BYD_1_FAHRZUST | vehicle state as a code of the interface (raw value, meaning not documented) | —",
"BAUSTEIN.Z1_06": "Virtual HTTP input command (template “BYD 1”) | BYD_1_SOC | state of charge of the traction battery in %%; statistics on | —",
"BAUSTEIN.Z1_07": "Virtual HTTP input command (template “BYD 1”) | BYD_1_REICHW | remaining range in km; statistics on | —",
"BAUSTEIN.Z1_08": "Virtual HTTP input command (template “BYD 1”) | BYD_1_LAEDT | 1 = vehicle is charging, 0 = not charging | —",
"BAUSTEIN.Z1_09": "Virtual HTTP input command (template “BYD 1”) | BYD_1_KABEL | 1 = charging cable plugged in, 0 = not | —",
"BAUSTEIN.Z1_10": "Virtual HTTP input command (template “BYD 1”) | BYD_1_RESTMIN | remaining time of the charging process in min | —",
"BAUSTEIN.Z1_11": "Virtual HTTP input command (template “BYD 1”) | BYD_1_ZUHAUSE | 1 = vehicle within the radius of the home position (150 m by default), 0 = on the road; without a home position in the plugin no value comes | —",
"BAUSTEIN.Z1_12": "Constant | Konstante 1 | value 1 | —",
"BAUSTEIN.Z1_13": "Value Validator | Lebenszeichen fehlt (BYD) | Tmc 900 s (three times the polling time of 300 s), Min -1, Max 999999 – if the LoxBerry stands still, the age stays at its last value; remove the tick at ‘En’ in the properties window | V = #2, En = #12",
"BAUSTEIN.Z1_14": "NOT | Keine frischen Daten (BYD) | — | I = #1",
"BAUSTEIN.Z1_15": "OR | Störung (BYD) | — (no fresh data or sign of life missing) | I1 = #14, I2 = output E of #13",
"BAUSTEIN.Z1_16": "Switch-On Delay | Störung bestätigt (BYD) | 600 s (two polls; a restart and a single failed poll report nothing) | Input = #15",
"BAUSTEIN.Z1_17": "Notification | Meldung Auto gestört (BYD) | Text: BYD – no fresh vehicle values for 10 minutes, or the LoxBerry does not answer. Read the status “Zustand (BYD)” in the app | Input = #16",
"BAUSTEIN.Z1_18": "Status | Zustand (BYD) | rows: V1 = 1 “sign of life missing for at least 15 minutes – LoxBerry or plugin does not answer; open the LoxBerry in the browser, in the plugin tab Settings ‘Start service’”; V3 < 0 “never a successful poll so far – in the plugin tab Settings enter user name, password and control PIN of the BYD account, then ‘Start service’”; V4 >= 3 “<v4> polls failed in a row – the plugin stretches the interval; in the plugin tab Test ‘Self-test of the service’”; V2 = 0 “no fresh values – last successful poll <v3> s ago; in the plugin tab Test ‘Measure endpoint now’”; without condition “running – values <v3> s old (reachability <v5>, state <v6> as codes)”; visualisation ON | V1 = output E of #13, V2 = #1, V3 = #2, V4 = #3, V5 = #4, V6 = #5",
"BAUSTEIN.Z1_19": "Formula | Ladestand für Meldung (BYD) | IF(I1>0;I1;100) – a state of charge never reported (0: combustion car or before the first poll) does not count as low | I1 = #6",
"BAUSTEIN.Z1_20": "Threshold Switch | Ladestand niedrig (BYD) | On 20 / Off 25 (%%; switches on when falling below 20 %%, off again above 25 %%) | Input = #19",
"BAUSTEIN.Z1_21": "Formula | Reichweite für Meldung (BYD) | IF(I1>0;I1;999) – a range never reported (0) does not count as low | I1 = #7",
"BAUSTEIN.Z1_22": "Threshold Switch | Reichweite gering (BYD) | On 50 / Off 70 (km; switches on when falling below 50 km, off again above 70 km) | Input = #21",
"BAUSTEIN.Z1_23": "OR | Ladestand oder Reichweite knapp (BYD) | — | I1 = #20, I2 = #22",
"BAUSTEIN.Z1_24": "AND | Knapp und nicht angesteckt (BYD) | — (I2 negated: in Config click the input point, a small circle appears; with the charging cable plugged in nothing is reported) | I1 = #23, I2 = #9 (negated)",
"BAUSTEIN.Z1_25": "Switch-On Delay | Knapp bestätigt (BYD) | 600 s (swallows the short pulse of the threshold switches at every poll) | Input = #24",
"BAUSTEIN.Z1_26": "Notification | Meldung Ladestand niedrig (BYD) | Text: BYD – state of charge below 20 %% or range below 50 km, and no charging cable plugged in. Please plug in the vehicle; values in the app under “Ladestand und Reichweite (BYD)” | Input = #25",
"BAUSTEIN.Z1_27": "Status | Ladestand und Reichweite (BYD) | rows: V3 = 1 and V5 > 0 “charging – <v1.0> %%, range <v2> km, finished in about <v5> min”; V3 = 1 “charging – <v1.0> %%, range <v2> km”; V7 = 1 “low – <v1.0> %%, only <v2> km left – please plug in”; V4 = 1 “cable plugged in, not charging – <v1.0> %%, range <v2> km”; V6 = 1 “<v1.0> %%, range <v2> km – vehicle at home”; without condition “<v1.0> %%, range <v2> km – on the road (without a home position in the plugin this always says ‘on the road’)”; visualisation ON | V1 = #6, V2 = #7, V3 = #8, V4 = #9, V5 = #10, V6 = #11, V7 = #25",
"BAUSTEIN.Z1_28": "Switch-On Delay | Lädt seit einer Minute (BYD) | 60 s (only a real charge counts; a short outlier reports no end of charging) | Input = #8",
"BAUSTEIN.Z1_29": "Edge Detection | Ladung endet (BYD) | Pd 1 s; the output Off is used (falling edge) | Input = #28",
"BAUSTEIN.Z1_30": "Notification | Meldung Ladung beendet (BYD) | Text: BYD – charging has ended (full, cable pulled or aborted). State of charge in the app under “Ladestand und Reichweite (BYD)” | Input = output Off of #29",
"BAUSTEIN.Z2_01": "Virtual HTTP input command (template “BYD 1”) | BYD_1_LAEDT | 1 = vehicle is charging (further instance, also on page “BYD Autos”) | —",
"BAUSTEIN.Z2_02": "Virtual HTTP input command (template “BYD 1”) | BYD_1_KABEL | 1 = charging cable plugged in (further instance) | —",
"BAUSTEIN.Z2_03": "Virtual HTTP input command (template “BYD 1”) | BYD_1_LADEZUST | charging state as a code of the interface: 0 not connected, 1 charging, 15 plug inserted (table of the ioBroker adapter, not measured on the vehicle) | —",
"BAUSTEIN.Z2_04": "Virtual HTTP input command (template “BYD 1”) | BYD_1_LADEKWH | energy charged in the last charging process in kWh (calculated from state of charge and capacity; without a capacity in the plugin no value comes) | —",
"BAUSTEIN.Z2_05": "Virtual HTTP input command (template “BYD 1”) | BYD_1_LADEEMPF | 1 = charging recommended (the plugin listens to a price or surplus value in the broker), 0 = not; without the charging recommendation switched on in the plugin no value comes | —",
"BAUSTEIN.Z2_06": "Virtual input (name as the MQTT gateway assigns it, plugin Spotpreis aWATTar) | spot_awattar_rank | rank of the current hour in the next 24 h, 1 = cheapest, -1 = no rank (further instance, also on “WaermepumpeCloud”, “Weissware PV-Start”, “Spotpreis aWATTar”); without the spot price plugin leave it free (then never cheap) | —",
"BAUSTEIN.Z2_07": "Greater | Preisrang bekannt (BYD) | V2 = 0 (leave the second input open) | I1 = #6",
"BAUSTEIN.Z2_08": "Less or Equal | Günstige Stunde zum Laden (BYD) | V2 = 4 (leave the second input open; the four cheapest hours of the next 24 h) | I1 = #6",
"BAUSTEIN.Z2_09": "AND | Strom günstig zum Laden (BYD) | — | I1 = #7, I2 = #8",
"BAUSTEIN.Z2_10": "OR | Laden empfohlen (BYD) | — (recommendation of the plugin or cheap hour) | I1 = #5, I2 = #9",
"BAUSTEIN.Z2_11": "AND | Laden empfohlen und angesteckt (BYD) | — | I1 = #10, I2 = #2",
"BAUSTEIN.Z2_12": "Virtual input (switch) | Laden nach Empfehlung (BYD) | in the app; off by default | —",
"BAUSTEIN.Z2_13": "AND | Ladefreigabe (BYD) | — | I1 = #11, I2 = #12",
"BAUSTEIN.Z2_14": "Switch-On Delay | Ladefreigabe bestätigt (BYD) | 60 s (swallows the pulse of the comparators at every poll); output Q to the release of your own wallbox (not part of the list); with EVCC this row is dropped – EVCC controls it there | Input = #13",
"BAUSTEIN.Z2_15": "Status | Laden (BYD) | rows: V5 = 1 “wallbox released – recommendation of the plugin or cheap hour”; V1 = 1 “charging (code <v3>) – last charge <v4.1> kWh”; V6 = 1 and V7 = 0 “charging recommended – switch ‘Laden nach Empfehlung (BYD)’ is off”; V2 = 1 “cable plugged in, not charging (code <v3>)”; without condition “no charging cable – last charge <v4.1> kWh”; visualisation ON | V1 = #1, V2 = #2, V3 = #3, V4 = #4, V5 = #14, V6 = #10, V7 = #12",
"BAUSTEIN.Z2_16": "Virtual HTTP input command (template “BYD 1”) | BYD_1_INNENTEMP | interior temperature in °C | —",
"BAUSTEIN.Z2_17": "Virtual HTTP input command (template “BYD 1”) | BYD_1_BATTHEIZ | battery heating as a code of the interface (raw value) | —",
"BAUSTEIN.Z2_18": "Virtual HTTP input command (template “BYD 1”) | BYD_1_SITZHEIZ | seat heating driver seat as a code of the interface (raw value) | —",
"BAUSTEIN.Z2_19": "Virtual input (slider) | Zieltemperatur (BYD) | Min 16, Max 30, step 0.5, start value 21 (°C; outside the limits in the plugin, 16–30 by default, the plugin rejects the command) | —",
"BAUSTEIN.Z2_20": "Virtual input (push button) | Klima jetzt (BYD) | in the app; starts the climate control with the target temperature | —",
"BAUSTEIN.Z2_21": "Schedule | Abfahrt vorklimatisieren (BYD) | ON = precondition: Monday to Friday 06:40–07:00 (20 minutes before departure at 07:00; enter your own departure times) | —",
"BAUSTEIN.Z2_22": "Virtual input | Anwesenheit (eigene Quelle) | 1 = somebody at home (further instance, the same input as on “Saugroboter”, “Chromecast4lox”, “Abfahrtsassistent”); in your own project feed it from your own presence | —",
"BAUSTEIN.Z2_23": "AND | Vorklimatisieren nur bei Anwesenheit (BYD) | — (on holiday nothing preconditions) | I1 = output AQ of #21, I2 = #22",
"BAUSTEIN.Z2_24": "OR | Klima anfordern (BYD) | — (push button or schedule) | I1 = #20, I2 = #23",
"BAUSTEIN.Z2_25": "Formula | Klima-Sollwert (BYD) | IF(I1>0;I2;-1) – while requested the target temperature, otherwise -1 (the plugin rejects the value -1 without effect; no digital pulse on the analogue command) | I1 = #24, I2 = #19",
"BAUSTEIN.Z2_26": "Virtual output command (template “BYD 1 steuern”) | BYD_1_KLIMA | command at analogue value <v.1>: starts the climate control at this temperature; no off command (climate off via its own command); write commands and control PIN needed in the plugin | Input = #25",
"BAUSTEIN.Z2_27": "Virtual input (push button) | Klima aus (BYD) | in the app; stops the climate control | —",
"BAUSTEIN.Z2_28": "Virtual output command (template “BYD 1 steuern”) | BYD_1_KLIMA_AUS | command at ON: stop the climate control | Input = #27",
"BAUSTEIN.Z2_29": "Status | Klima (BYD) | rows: V2 > 0 “climate control at <v2.1> °C – inside <v1.1> °C”; without condition “off – inside <v1.1> °C (battery heating <v3>, seat heating <v4> as codes)”; visualisation ON | V1 = #16, V2 = #25, V3 = #17, V4 = #18",
"BAUSTEIN.Z2_30": "Virtual input (slider) | Sitzheizung Stufe (BYD) | Min 0, Max 3, step 1, start value 0 (0 = off; which levels the vehicle knows is not documented – look at it in the plugin tab Test ‘Switching’ with a dry run) | —",
"BAUSTEIN.Z2_31": "Virtual output command (template “BYD 1 steuern”) | BYD_1_SITZKLIMA | command at analogue value <v.0> (level), at OFF level 0; sends the level at every change | Input = #30",
"BAUSTEIN.Z2_32": "Virtual input (switch) | Batterieheizung (BYD) | in the app; on = level 1, off = level 0 | —",
"BAUSTEIN.Z2_33": "Virtual output command (template “BYD 1 steuern”) | BYD_1_BATTERIEHEIZUNG | command at analogue value <v.0> (level), at OFF level 0 (follows the switch) | Input = #32",
"BAUSTEIN.Z2_34": "Virtual input (push button) | Jetzt abrufen (BYD) | in the app; every poll wakes the vehicle – do not trigger it cyclically | —",
"BAUSTEIN.Z2_35": "Virtual output command (template “BYD 1 steuern”) | BYD_1_ABRUF | fetches new values immediately instead of waiting for the interval; on command only | Input = #34",
"BAUSTEIN.Z3_01": "Virtual HTTP input command (template “BYD 1”) | BYD_1_SCHLOSSVL | door lock front left (driver door) as a code of the interface; on the only measured vehicle, parked: 2 | —",
"BAUSTEIN.Z3_02": "Virtual HTTP input command (template “BYD 1”) | BYD_1_SCHLOSSVR | door lock front right as a code | —",
"BAUSTEIN.Z3_03": "Virtual HTTP input command (template “BYD 1”) | BYD_1_SCHLOSSHL | door lock rear left as a code | —",
"BAUSTEIN.Z3_04": "Virtual HTTP input command (template “BYD 1”) | BYD_1_SCHLOSSHR | door lock rear right as a code | —",
"BAUSTEIN.Z3_05": "Virtual HTTP input command (template “BYD 1”) | BYD_1_TUERVL | door front left as a code; on the measured vehicle, parked: 0 | —",
"BAUSTEIN.Z3_06": "Virtual HTTP input command (template “BYD 1”) | BYD_1_TUERVR | door front right as a code | —",
"BAUSTEIN.Z3_07": "Virtual HTTP input command (template “BYD 1”) | BYD_1_TUERHL | door rear left as a code | —",
"BAUSTEIN.Z3_08": "Virtual HTTP input command (template “BYD 1”) | BYD_1_TUERHR | door rear right as a code | —",
"BAUSTEIN.Z3_09": "Virtual HTTP input command (template “BYD 1”) | BYD_1_KOFFER | tailgate as a code; on the measured vehicle, parked: 0 | —",
"BAUSTEIN.Z3_10": "Virtual HTTP input command (template “BYD 1”) | BYD_1_FENSTERVL | window front left as a code; on the measured vehicle, parked: 1 | —",
"BAUSTEIN.Z3_11": "Virtual HTTP input command (template “BYD 1”) | BYD_1_FENSTERVR | window front right as a code | —",
"BAUSTEIN.Z3_12": "Virtual HTTP input command (template “BYD 1”) | BYD_1_FENSTERHL | window rear left as a code | —",
"BAUSTEIN.Z3_13": "Virtual HTTP input command (template “BYD 1”) | BYD_1_FENSTERHR | window rear right as a code | —",
"BAUSTEIN.Z3_14": "Virtual HTTP input command (template “BYD 1”) | BYD_1_DACHFENSTER | sunroof as a code; on the measured vehicle, parked: 1 | —",
"BAUSTEIN.Z3_15": "Virtual HTTP input command (template “BYD 1”) | BYD_1_OK | 1 = values fresh (further instance) | —",
"BAUSTEIN.Z3_16": "Virtual HTTP input command (template “BYD 1”) | BYD_1_TEMPO | speed in km/h (further instance, also on page “BYD Autos Werte”) | —",
"BAUSTEIN.Z3_17": "Virtual input (slider) | Schloss-Kennzahl verriegelt (BYD) | Min 0, Max 9, step 1, start value 2 (the value the measured vehicle reported when parked; compare once with the BYD app and change it here if needed) | —",
"BAUSTEIN.Z3_18": "Unequal | Fahrertür nicht verriegelt (BYD) | — (code differs from “locked”) | I1 = #1, I2 = #17",
"BAUSTEIN.Z3_19": "Formula | Abgestellt und Daten frisch (BYD) | IF(I1<1;I2;0) – 1 only if the vehicle is standing (speed 0) AND the values are fresh | I1 = #16, I2 = #15",
"BAUSTEIN.Z3_20": "AND | Offen und abgestellt (BYD) | — (while driving the car is often not locked – that does not count) | I1 = #18, I2 = #19",
"BAUSTEIN.Z3_21": "Switch-On Delay | Offen seit 5 Minuten (BYD) | 300 s (no message while loading and unloading) | Input = #20",
"BAUSTEIN.Z3_22": "Notification | Meldung Fahrzeug offen (BYD) | Text: BYD – the driver door of the parked vehicle has not been locked for 5 minutes. Please lock it; codes in the app under “Türen und Schlösser (BYD)” | Input = #21",
"BAUSTEIN.Z3_23": "Virtual input (push button) | Fenster schließen (BYD) | in the app | —",
"BAUSTEIN.Z3_24": "Virtual input (switch) | Regensensor (eigene Quelle) | 1 = it is raining (further instance, the same placeholder as on “Robonect Steuerung”); in your own project the connection from your own rain sensor instead of this switch | —",
"BAUSTEIN.Z3_25": "OR | Fenster schließen auslösen (BYD) | — (push button or rain) | I1 = #23, I2 = #24",
"BAUSTEIN.Z3_26": "Virtual output command (template “BYD 1 steuern”) | BYD_1_FENSTER_ZU | closes all windows; on command only | Input = #25",
"BAUSTEIN.Z3_27": "Status | Türen und Schlösser (BYD) | rows: without condition “locks <v1> / <v2> / <v3> / <v4>, doors <v5> / <v6> / <v7> / <v8> (front left / front right / rear left / rear right; codes of the interface – on the measured, parked vehicle locks 2, doors 0)”; visualisation ON | V1 = #1, V2 = #2, V3 = #3, V4 = #4, V5 = #5, V6 = #6, V7 = #7, V8 = #8",
"BAUSTEIN.Z3_28": "Status | Fenster und Klappen (BYD) | rows: V7 = 1 “driver door not locked for more than 5 minutes – windows <v1> / <v2> / <v3> / <v4>, sunroof <v5>, tailgate <v6>”; without condition “windows <v1> / <v2> / <v3> / <v4> (front left / front right / rear left / rear right), sunroof <v5>, tailgate <v6> (codes – on the measured, parked vehicle windows and sunroof 1, tailgate 0)”; visualisation ON | V1 = #10, V2 = #11, V3 = #12, V4 = #13, V5 = #14, V6 = #9, V7 = #21",
"BAUSTEIN.Z4_01": "Virtual HTTP input command (template “BYD 1”) | BYD_1_REIFENVL | tyre pressure front left in bar | —",
"BAUSTEIN.Z4_02": "Virtual HTTP input command (template “BYD 1”) | BYD_1_REIFENVR | tyre pressure front right in bar | —",
"BAUSTEIN.Z4_03": "Virtual HTTP input command (template “BYD 1”) | BYD_1_REIFENHL | tyre pressure rear left in bar | —",
"BAUSTEIN.Z4_04": "Virtual HTTP input command (template “BYD 1”) | BYD_1_REIFENHR | tyre pressure rear right in bar | —",
"BAUSTEIN.Z4_05": "Virtual HTTP input command (template “BYD 1”) | BYD_1_KM | mileage in km; statistics on | —",
"BAUSTEIN.Z4_06": "Virtual HTTP input command (template “BYD 1”) | BYD_1_VERBRAUCH | consumption of the last completed trip (from 20 km) in kWh/100 km, calculated by the plugin; without a capacity in the plugin no value comes | —",
"BAUSTEIN.Z4_07": "Virtual HTTP input command (template “BYD 1”) | BYD_1_VERBR50 | average consumption of the last 50 km according to the vehicle in kWh/100 km | —",
"BAUSTEIN.Z4_08": "Virtual HTTP input command (template “BYD 1”) | BYD_1_VERBRBYD | average consumption according to the vehicle over the whole mileage in kWh/100 km | —",
"BAUSTEIN.Z4_09": "Virtual HTTP input command (template “BYD 1”) | BYD_1_TEMPO | speed in km/h | —",
"BAUSTEIN.Z4_10": "Virtual HTTP input command (template “BYD 1”) | BYD_1_FAHRSTUFE | gear position as a code of the interface (raw value) | —",
"BAUSTEIN.Z4_11": "Virtual HTTP input command (template “BYD 1”) | BYD_1_ZUENDUNG | ignition as a code of the interface (raw value) | —",
"BAUSTEIN.Z4_12": "Virtual HTTP input command (template “BYD 1”) | BYD_1_OK | 1 = values fresh (further instance) | —",
"BAUSTEIN.Z4_13": "Formula | Kleinster Reifendruck (BYD) | MIN(MIN(I1;I2);MIN(I3;I4)) | I1 = #1, I2 = #2, I3 = #3, I4 = #4",
"BAUSTEIN.Z4_14": "Threshold Switch | Reifendruck niedrig (BYD) | On 2.2 / Off 2.4 (bar; switches on when falling below 2.2 bar, off again above 2.4 bar) | Input = #13",
"BAUSTEIN.Z4_15": "AND | Reifendruck niedrig, Werte frisch (BYD) | — (after a restart of the Miniserver the pressures are 0 until the first poll) | I1 = #14, I2 = #12",
"BAUSTEIN.Z4_16": "Switch-On Delay | Reifendruck niedrig bestätigt (BYD) | 600 s (two polls; swallows the pulse of the threshold switch at every poll) | Input = #15",
"BAUSTEIN.Z4_17": "Notification | Meldung Reifendruck niedrig (BYD) | Text: BYD – a tyre has less than 2.2 bar. Pressures in the app under “Reifendruck (BYD)”; check and inflate the tyres | Input = #16",
"BAUSTEIN.Z4_18": "Status | Reifendruck (BYD) | rows: V5 = 1 “tyre pressure low – front <v1.1> / <v2.1> bar, rear <v3.1> / <v4.1> bar; check the tyres”; without condition “front <v1.1> / <v2.1> bar, rear <v3.1> / <v4.1> bar”; visualisation ON | V1 = #1, V2 = #2, V3 = #3, V4 = #4, V5 = #15",
"BAUSTEIN.Z4_19": "Pulse at | Tagesbeginn 0:00 (BYD) | At a specific time, 00:00:00 | —",
"BAUSTEIN.Z4_20": "Analog Memory | Kilometerstand um Mitternacht (BYD) | takes over the mileage at 0:00; Rem on (default), so that the value survives a restart | V = #5, Set = output Q of #19",
"BAUSTEIN.Z4_21": "Formula | Heute gefahren in km (BYD) | IF(I2>0;IF(I1>=I2;I1-I2;0);0) – mileage minus the value at midnight; after a restart of the Miniserver 0 until midnight | I1 = #5, I2 = #20",
"BAUSTEIN.Z4_22": "Status | Fahrt und Verbrauch (BYD) | rows: V6 > 0 “driving <v6> km/h – today <v2> km, mileage <v1> km”; without condition “standing – today <v2> km, mileage <v1> km; consumption last trip <v3.1>, last 50 km <v4.1>, total <v5.1> kWh/100 km (gear position <v7>, ignition <v8> as codes)”; visualisation ON | V1 = #5, V2 = #21, V3 = #6, V4 = #7, V5 = #8, V6 = #9, V7 = #10, V8 = #11",
"LOX.BILD_ALT": "Plugin blocks in Loxone Config",
"LOX.BILD_UNTERSCHRIFT": "Page “%s” in the LoxBerry plugins sample project. Config shortens long block names – see the table for the full names.",
"LOX.MUSTERPROJEKT": "The complete project file with all plugin pages and templates: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry plugins sample project</a>",
"LOX.VORLAGEN_FAHRZEUG": "Templates for vehicle %s",
"LOX.VORLAGE_VO_EINGRIFF": "With the second tick, locking, find vehicle and flashing are included as well.",
"LOX.EINGRIFF": "only with the second tick",
"EINST.L_GEFAHR_EIN": "Allow intervening commands (lock and unlock, find vehicle, flash lights)",
"EINST.H_GEFAHR_EIN": "Off by default. These commands act on a vehicle standing in a public place: an accidental unlock leaves it open without anybody noticing, and the horn wakes the neighbourhood. The tick above is not enough for them – this one acts <b>in addition</b>. Without it the endpoint rejects the commands with <span class='sm-mono'>GRUND=EINGRIFF_GESPERRT</span>, the service does the same, and the template of the control commands does not contain them. Not tried on any vehicle.",
"TEST.F_GEFAHR": "Are intervening commands allowed?",
"TEST.A_GEFAHR_AUS": "no – blocked by default, that is not an error",
"TEST.A_GEFAHR_EIN": "yes – lock and unlock, find vehicle and flash lights are released",
"TEST.SCHALTEN_EINGRIFF_GESPERRT": "Lock, unlock, find vehicle and flash lights are blocked in addition until the second tick “Allow intervening commands” is set on the Settings tab; the dry run names the block.",

# DRIFT-ABGLEICH 06.11.2026: 134 Schluessel, die in der veroeffentlichten
# BYD Autos 0.9.36 (templates/lang/language_en.ini) standen, aber nicht hier -
# wortgleich von dort uebernommen, in der Reihenfolge der .ini.
"ALLG.KACHEL_MQTT_HILFE": "Publishing of this plugin; gateway autostart: %s; gateway version: %s",
"ALLG.NICHT_FESTSTELLBAR": "not determinable",
"EINST.L_HAUS_FAHRZEUG_EIN": "Send the collective topics haus/fahrzeug/…",
"EINST.H_HAUS_FAHRZEUG_EIN": "On by default. State of charge, range, cable, charging and at home under <span class='sm-mono'>haus/fahrzeug/&lt;name&gt;/…</span> (<span class='sm-mono'>soc</span>, <span class='sm-mono'>reichweite_km</span>, <span class='sm-mono'>kabel</span>, <span class='sm-mono'>laedt</span>, <span class='sm-mono'>zuhause</span> retained, a dash when there is no statement; <span class='sm-mono'>zaehler</span> never retained), so other plugins and Loxone can read a vehicle whatever its make. Independent of the tick above. No location, no VIN. Switching it off clears the topics.",
"EINST.H_SAMMEL_KABEL": "Cable forgotten",
"EINST.SAMMEL_KABEL_HILFE": "Reports when the car stands at home, the cable is not plugged in and the battery is below the threshold: at most once per stay and per day, only with vehicle data up to 12 hours old. During the night rest the message waits. Unknown values (no home location, no cable value) never warn. The tick for the announcement is among the occasions of the speech output.",
"EINST.L_KABEL_SOC": "Warn below battery (%)",
"EINST.L_KABEL_UHR": "Warn from this time",
"EINST.L_KABEL_ABFAHRT_MIN": "Also warn when departure is due within this many minutes",
"EINST.H_KABEL_ABFAHRT_MIN": "0 = no. Only works with pre-conditioning switched on, it supplies the departure time.",
"EINST.L_SIGNAL_KABEL": "Report a forgotten cable through SignalBot",
"EINST.L_ANSAGE_KABEL": "The car is at home without a cable and the battery is low",
"EINST.L_VORKLIMA_MIN_SOC": "Pre-conditioning only from battery (%)",
"EINST.H_VORKLIMA_MIN_SOC": "0 = no limit. Below it nothing is sent and no attempt is used up (topic vorklima = 5). If the battery level is unknown, the plugin pre-conditions as before.",
"EINST.L_VORKLIMA_NUR_KABEL": "Pre-conditioning only with the cable plugged in",
"EINST.H_VORKLIMA_NUR_KABEL": "Off by default. If the cable is not plugged in, nothing is sent (topic vorklima = 6). If it is unknown, the plugin pre-conditions as before.",
"EINST.F_HAUS_FAHRZEUG": "Collective topics haus/fahrzeug",
"EINST.A_HAUS_FAHRZEUG": "sent for: %s",
"EINST.A_HAUS_FAHRZEUG_NOCH": "switched on, nothing sent yet (the service sends as soon as it knows a vehicle)",
"EINST.A_HAUS_FAHRZEUG_AUS": "switched off",
"EINST.A_HAUS_FAHRZEUG_FREMD": "Under haus/fahrzeug/%s another plugin is sending too (foreign counter). Please give one of the vehicles a different name: until then the values overwrite each other, and this plugin does not clear the topics there.",
"EINST.SICH_REGELN": "The rules of the speech output in this file are invalid; they stay as they are.",
"EINST.O_PREISEMPF_HAUS": "House topic haus/strompreis (spot price plugin as provider)",
"EINST.SICH_SPAET": "Not in the backup, unchanged: %s (the backup comes from an earlier version).",
"LADUNG.T_KOSTEN": "Cost",
"LADUNG.T_PREIS": "Price",
"BY_FELD.LADEKOSTEN": "Cost of the last charge at home (EUR, -1 without a statement)",
"BY_FELD.LADEPREIS": "Average price of the last charge at home (ct/kWh, -1 without a statement)",
"BY_FELD.VORKLIMA": "Preconditioning: 0 nothing due, 1 sent, 2 mild (not needed), 3 waiting for retry, 4 waiting for presence, 5 not sent (battery below the limit), 6 not sent (cable missing), -1 failed",
"BY_MQTT.STATUS_BEFEHLE": "Sign of life of the command bridge (1 running, 0 off).",
"BY_MQTT.ZAEHLER": "Sign of life: counts 0…999 per run, never retained – if it stops for more than three cycles, the service has failed.",
"BEFEHL.F_BRUECKE": "Command bridge",
"BEFEHL.F_PRUEFEN": "Command bridge: set-up (--pruefen)",
"BEFEHL.H_ANNEHMEN": "Starts the command bridge: Loxone sends <span class='sm-mono'>publish byd/befehl/&lt;name&gt; &lt;value&gt;</span> to the output “LoxBerry MQTT-Gateway”, the answer is under <span class='sm-mono'>…/quittung</span> (“accepted” means: handed to the service). Off by default.",
"BEFEHL.H_ENDPUNKT": "The virtual HTTP inputs and outputs with token. New installations use the MQTT gateway V2 and the command bridge; when switched off the endpoint answers 403. An installation updated from a version before 0.9.29 has it on.",
"BEFEHL.H_STEUERN": "Lock/unlock, find and flash via MQTT – only together with <i>Allow intervening commands</i> (Settings tab). Off by default.",
"BEFEHL.H_TITEL": "Commands from Loxone via MQTT",
"BEFEHL.K_AUFFRISCHEN": "Query values",
"BEFEHL.K_AUSSENTEMP": "Outside temperature from Loxone",
"BEFEHL.K_BATTHEIZ": "Battery heating (level, 0 off)",
"BEFEHL.K_BLINKEN": "Flash lights",
"BEFEHL.K_ENTRIEGELN": "Unlock",
"BEFEHL.K_FENSTER_ZU": "Close windows",
"BEFEHL.K_KLIMA_AN": "Climate on (degrees)",
"BEFEHL.K_KLIMA_AUS": "Climate off",
"BEFEHL.K_SITZKLIMA": "Seat climate (level, 0 off)",
"BEFEHL.K_SUCHEN": "Find vehicle (horn and lights)",
"BEFEHL.K_VERRIEGELN": "Lock",
"BEFEHL.K_VORLAGE": "Template commands via MQTT",
"BEFEHL.L_ANNEHMEN": "Accept commands via MQTT",
"BEFEHL.L_ENDPUNKT": "HTTP endpoint for Loxone (previous path)",
"BEFEHL.L_STEUERN": "Also accept intervening commands via MQTT",
"BEFEHL.M_SCHALTEN_FEHL": "The command bridge could not be switched (%s): %s",
"BEFEHL.T_ART": "Type",
"BEFEHL.T_AUS": "off (tick “Accept commands via MQTT” not set).",
"BEFEHL.T_DEFEKT": "The bridge set-up is faulty: %s",
"BEFEHL.T_KEINER": "No command yet.",
"BEFEHL.T_LAEUFT": "running (%d process) – accepted %d, rejected %d.",
"BEFEHL.T_LETZTER": "Last command %s: %s, %d s ago.",
"BEFEHL.T_NICHT_DA": "The command bridge (bin/befehlsbruecke.php) is missing.",
"BEFEHL.T_PRUEFEN_OK": "in order (mapping, mosquitto_sub/_pub, options file).",
"BEFEHL.T_STEHT": "should run but stands still (%s) – the watchdog restarts it within a minute.",
"BEFEHL.T_TITEL": "Title in Loxone",
"BEFEHL.UDP_HINWEIS": "The UDP input of the MQTT gateway (11884) accepts messages on the home network <b>without authentication</b> – any device on the Wi-Fi can send a command. That is why everything is off by default, and switching commands additionally only work with <i>Allow write commands</i>. Intervening commands (lock/unlock, find, flash) need the second checkbox below <b>and</b> <i>Allow intervening commands</i>; lock and unlock still need the stored S-PIN. Every command lands in the same queue as the HTTP path; the service's debounce and hourly limit apply to all paths together.",
"BY_ANSAGE.S_KABEL": "%s is at home without a charging cable, the battery is at %s percent.",
"G42.FEHLER_SAMMEL": "This value does not fit: %s.",
"G42.A_ENDPUNKT_AUS": "switched off – every call except ?selftest=1 gets 403 ENDPUNKT_AUS (new installation; switch on in the MQTT tab).",
"G42.A_ENDPUNKT_EIN": "switched on – the HTTP templates are answered.",
"G42.FEHLER_ANKUNFT": "Who arrives: tag:NAME or person:NAME (letters, digits, _ and -), comma separated, at most four; jemand and zaehler are not persons.",
"G42.FEHLER_KALT_HEISS": "Cold below and hot above must be whole numbers from -30 to 45, cold lower than hot.",
"G42.FEHLER_PRAEFIX": "The prefix of the SignalBot plugin: 1 to 40 characters from letters, digits, _ and -.",
"G42.F_ENDPUNKT_EIN": "HTTP endpoint (previous way)",
"G42.H_ANKUNFT": "When a chosen tag or person changes live from 0 to 1, the plugin polls the account once – at most once per 30 minutes and only if the state is older than 5 minutes.",
"G42.H_SIGNAL": "Messages to SignalBot",
"G42.H_SIGNAL_TEXT": "Charge finished, no more data and failed preconditioning as a Signal message (through the SignalBot plugin). The sample project sends the same messages from Loxone as well – switch on only one way, otherwise they arrive twice.",
"G42.H_STROMPREIS": "During a charge at home the service notes the final price every minute; after the charge, cost and average price are shown in the Charges tab. Energy is state-of-charge difference × capacity (Settings tab) – no capacity, no cost. If the price is missing for more than 10 % of the charge, the cost stays -1, never estimated.",
"G42.H_TEXT": "Everything is off by default. The values come over the permanent connection of the service from the house topics of other plugins (departure assistant, BLE scanner, spot price); a value only counts while the counter of its source changes live within 120 s. Use only one source: a timer in Loxone <b>or</b> these ticks – otherwise two commands are sent.",
"G42.H_TITEL": "House form: house topics, charging cost, SignalBot",
"G42.H_V2": "Gateway V2: tick these data points",
"G42.H_VORKLIMA": "Triggered 1 to lead time minutes before departure, at most two “climate on” per departure (send – poll – send), done only once BYD accepted the order. The outside temperature comes from Loxone (bridge, command <span class='sm-mono'>aussentemp</span>, valid for 30 min) – BYD does not report one. Without the house topic this version still uses the previous departure topic (received live only).",
"G42.LOG_BRUECKE": "Command bridge (befehle_start.log)",
"G42.LOG_CRONERR": "Error output of the watchdog (cron.err)",
"G42.LOX_AUS": "The HTTP endpoint is currently <b>switched off</b> (MQTT tab) – these templates get 403.",
"G42.LOX_BISHER": "The HTTP templates below are the <b>previous way</b>. New installations use the MQTT gateway V2 (MQTT tab, tick data points) and the command bridge (template in the MQTT tab).",
"G42.L_ANKUNFT": "Poll once on arrival",
"G42.L_ANKUNFT_QUELLE": "Who arrives? (tag:NAME or person:NAME, comma separated, at most four)",
"G42.L_ANWESEND": "Precondition only when someone is at home (haus/anwesenheit)",
"G42.L_EMPF_QUELLE": "Source of the charging recommendation from a topic",
"G42.L_HAUS_ABFAHRT": "Minutes until departure from the house topic (haus/abfahrt)",
"G42.L_HEISS": "Hot above (°C)",
"G42.L_KALT": "Cold below (°C)",
"G42.L_SIGNAL": "Send messages to SignalBot",
"G42.L_SIGNAL_PRAEFIX": "Prefix of the SignalBot plugin",
"G42.L_SIG_AUSFALL": "No more data (three polls)",
"G42.L_SIG_FERTIG": "Charge finished",
"G42.L_SIG_VORKLIMA": "Preconditioning failed",
"G42.L_STROMPREIS": "Electricity price from the spot price plugin for the charging cost (haus/strompreis)",
"G42.L_WETTER": "Precondition only when it is cold or hot",
"G42.O_HAUS": "haus/strompreis/aktuell (final price now)",
"G42.O_THEMA": "own topic (as before)",
"G42.T_NAME": "Gateway name",
"G42.V2_NUR_V1": "Gateway V1: the subscription above applies (fallback). With gateway V2 this shows the list of data points to tick.",
"G42.V2_TEXT": "The MQTT gateway V2 only forwards ticked data points to the Miniserver. In Loxone the virtual input is named like the column <i>gateway name</i>. <i>Noncached</i> only where it says so (signs of life) – failure detection uses <span class='sm-mono'>byd_zaehler</span>.",
"HAUS.FRISCH": "fresh (counter last changed live %d s ago).",
"HAUS.NIE": "no live counter change seen yet –",
"HAUS.RUECK_ABFAHRT": "the departure topic entered so far applies (fallback).",
"HAUS.RUECK_ANWESENHEIT": "pre-conditioning does not wait for presence, and an arrival does not trigger a query.",
"HAUS.RUECK_STROMPREIS": "charging cost stays -1, the charging recommendation from haus/strompreis goes out as 0.",
"HAUS.SCHWEIGT": "silent for %d min –",
"HAUS.VK_AUFGEGEBEN": "failed (two attempts)",
"HAUS.VK_ERFOLG": "accepted",
"HAUS.VK_FRAGE": "Pre-conditioning before departure",
"HAUS.VK_FZ_FEHLT": "Vehicle %s does not exist in the account – nothing is sent (setting “Vehicle for pre-conditioning”).",
"HAUS.VK_MILD": "mild – not needed",
"HAUS.VK_NICHTS": "Vehicle %s: no departure within the lead time seen yet.",
"HAUS.VK_OFFEN": "running",
"HAUS.VK_STAND": "Vehicle %s, departure %s, %d attempt(s): %s.",
"HAUS.ZEILE": "House source %s",
"PRUEF.V2_FEHLT": "Missing: %s.",
"PRUEF.V2_FRAGE": "Gateway V2: are all data points ticked?",
"PRUEF.V2_LEER": "not determinable – the topic list of the service (bin/byd.py) is empty or unreadable.",
"PRUEF.V2_NC": "Noncached wrong: %s.",
"PRUEF.V2_NICHT_EINGERICHTET": "not set up yet – ticked once values arrive (enter the credentials first).",
"PRUEF.V2_UNKLAR": "not determinable – the gateway version or the gateway's subscriptions cannot be read.",
"PRUEF.V2_V1": "does not apply (gateway V1 – the subscription in the MQTT tab applies there).",
"PRUEF.V2_ZAHL": "%d of %d data points ticked.",
"SIGNAL.H_TEST": "Test message to SignalBot",
"SIGNAL.H_TEST_TEXT": "Sends a fixed sentence to <span class='sm-mono'>&lt;prefix&gt;/befehl/senden</span> and waits up to 5 s for the acknowledgement of the SignalBot bridge. Only works when <i>Messages to SignalBot</i> is switched on.",
"SIGNAL.K_TEST": "Test message to SignalBot",
"SIGNAL.T_ABGELEHNT": "SignalBot rejected the test message: %s",
"SIGNAL.T_ANGENOMMEN": "SignalBot accepted the test message.",
"SIGNAL.T_AUS": "Messages to SignalBot are off – nothing was sent.",
"SIGNAL.T_KEINE_ANTWORT": "No answer within 5 s – SignalBot not installed or its command bridge is off.",
"SIGNAL.T_NICHT_MOEGLICH": "Test message not possible – service program, paho-mqtt or broker missing, or the prefix is invalid.",
}


KOPF_DE = """; BYD Autos - Deutsch
;
; ERZEUGT von Werkzeuge/byd_sprache_erzeugen.py - nicht von Hand aendern.
; Wer hier etwas aendert, zieht den Erzeuger im selben Zug mit - sonst gibt es
; zwei Wahrheiten im selben Archiv, und die eine loescht die andere beim
; naechsten Lauf.
;
; Jeder Wert steht in doppelten Anfuehrungszeichen: bei parse_ini_file beginnt
; mit ';' ein Kommentar, und jede HTML-Entitaet endet auf ein Semikolon.
; Innerhalb eines Wertes darf KEIN doppeltes Anfuehrungszeichen stehen -
; HTML-Attribute deshalb einfach quoten: <span class='sm-mono'>. Sonst wird der
; Wert im Standardmodus abgeschnitten oder die ganze Datei abgewiesen, und mit
; INI_SCANNER_RAW faellt gar nichts auf.
;
; Schluessel, die im PHP durch by_e() laufen, enthalten KEINE Auszeichnung und
; KEINE Entitaeten: sie wuerden dort ein zweites Mal maskiert und als
; "pr&amp;uuml;fen" auf dem Bildschirm landen.
"""

KOPF_EN = """; BYD Autos - English
;
; GENERATED by Werkzeuge/byd_sprache_erzeugen.py - do not edit by hand.
;
; English is the fallback level: keys missing in another language are taken
; from here, so this file must always be complete.
; Quote every value - see the German file for the reason.
"""

REIHENFOLGE = ["REITER", "LEGENDE", "ALLG", "EINST", "MQTT", "LOX", "BAUSTEIN",
               "LADUNG", "TEST", "LOG", "BY_FELD", "BY_BEF", "BY_MQTT", "MELDUNG"]

# Schluessel, die zur Laufzeit zusammengesetzt werden und deshalb nicht als
# woertlicher by_t('X')-Aufruf im Quelltext stehen. Das ist etwas anderes als
# eine Ausnahme fuer ein Werkzeug, das nur schlecht sucht: hier gibt es den
# woertlichen Aufruf wirklich nicht.
ZUR_LAUFZEIT = {
    "EINST.DIENST_START", "EINST.DIENST_STOP", "EINST.DIENST_RESTART",
    "EINST.K_START", "EINST.K_STOP", "EINST.K_RESTART",
    "EINST.L_INTERVALL", "EINST.L_TEMP_MIN", "EINST.L_TEMP_MAX",
    "EINST.L_VERLAUF_TAGE", "EINST.L_WARTEZEIT",
}


# Namen, die im Quelltext wie ein Schluessel aussehen, aber keiner sind. Jeder
# Eintrag nennt die Stelle - eine namenlose Ausnahmeliste waechst, bis sie den
# Zweck der Pruefung aufhebt.
KEINE_SCHLUESSEL = {
    "ABSCHNITT.SCHLUESSEL",   # Beispiel im Kommentar von by_t(), by_lib.php
    "BEFEHL.K_X",             # Attrappe der Selbstpruefung in bin/befehlsbruecke.php ('kachel' => 'BEFEHL.K_X'),
                              # steht in keiner .ini und wird nie angezeigt (Drift-Abgleich 06.11.2026)
}


def php_dateien(wurzel: Path):
    # Die gemeinsame Sprachausgabe (sprachausgabe.php, Abschrift von Werkzeuge/gemeinsam/) ist nicht
    # Code dieser Linie: ihre Texte stehen im Abschnitt [ANSAGE], nicht in DE/EN (Nr. 36 b).
    return sorted(p for p in wurzel.rglob("*.php") if p.name != "sprachausgabe.php")


def maskierte_schluessel(wurzel: Path) -> set:
    """Welche Schluessel laufen im PHP durch by_e()?

    Beide Schachtelungen werden gesucht - by_e(sprintf(by_t(...))) UND
    sprintf(by_e(by_t(...))). Ein Muster, das nur eine davon kennt, uebersieht
    genau die Stellen, an denen ein Platzhalter im Spiel ist.
    """
    treffer = set()
    muster = (
        r"by_e\(\s*by_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)",
        r"by_e\(\s*sprintf\(\s*by_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)",
        r"sprintf\(\s*by_e\(\s*by_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)",
        r"by_e\(\s*by_klartext\(\s*by_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)",
    )
    for f in php_dateien(wurzel):
        t = f.read_text(encoding="utf-8")
        for m in muster[:3]:
            for x in re.finditer(m, t):
                treffer.add(x.group(1))
    return treffer


def benutzte_schluessel(wurzel: Path) -> set:
    """Alle im PHP vorkommenden Schluessel."""
    treffer = set()
    for f in php_dateien(wurzel):
        t = f.read_text(encoding="utf-8")
        for m in re.finditer(r"by_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t):
            treffer.add(m.group(1))
        # Schluessel, die nur als Zeichenkette in einer Tabelle stehen und
        # erst spaeter durch by_t() laufen. Bewusst OHNE Einschraenkung auf
        # bestimmte Abschnitte: die frueher hier stehende Liste (BY_* und
        # BAUSTEIN) hat drei Schluessel als "nie benutzt" gemeldet, die in
        # einer Zuordnungstabelle standen - und die naechste Tabelle in einem
        # neuen Abschnitt haette denselben Fehlalarm ausgeloest. Ein
        # Schluesselname, der woertlich im Quelltext steht, gilt als benutzt.
        # Ein Name, der auf '_' endet, ist der VORSATZ eines zur Laufzeit
        # zusammengesetzten Schluessels ('EINST.L_' . strtoupper($feld)) und
        # kein Schluessel. Und ein Platzhalter aus einem Kommentar ist keiner,
        # auch wenn er wie einer aussieht - er steht namentlich unten.
        for m in re.finditer(r"'([A-Z][A-Z0-9_]*\.[A-Z0-9_]*[A-Z0-9])'", t):
            if m.group(1) not in KEINE_SCHLUESSEL:
                treffer.add(m.group(1))
        # Jede Zeichenkette der Form ABSCHNITT.SCHLUESSEL zaehlt als
        # benutzt - unabhaengig davon, WIE sie in den Aufruf kommt.
        # Ergaenzt 31.08.2026: das Muster darueber verlangt die
        # schliessende Klammer unmittelbar hinter der Zeichenkette und
        # uebersieht deshalb den ternaeren Aufruf
        #     xx_t($f >= 2 ? 'MQTT.ABO_V2' : 'MQTT.ABO_WARNUNG')
        # Beide Schluessel wurden daraufhin als unbenutzt gemeldet.
        # NUR fuer Schluessel, die es in der Tabelle SCHON GIBT. Ein
        # loser Treffer darf einen vorhandenen Schluessel als benutzt
        # markieren, aber niemals einen neuen behaupten - sonst werden
        # Praefixe zusammengesetzter Aufrufe ('EINST.DIENST_' . $x) zu
        # angeblich fehlenden Schluesseln, und aus einer Abhilfe wird
        # ein zweiter Fehlalarm. Der Fehler geht so in die harmlose
        # Richtung: eine Meldung zu wenig statt einer Loeschung zu viel.
        for m in re.finditer(r"'([A-Z][A-Z0-9_]*\.[A-Z][A-Z0-9_]*)'", t):
            if m.group(1) in DE:
                treffer.add(m.group(1))
    return treffer | ZUR_LAUFZEIT


# ---------------------------------------------------------------------------
# Entitaeten aufloesen - IM ERZEUGER, nicht in einem Nachlauf
#
# Der Beschluss vom 14.08.2026 verlangt in den Sprachdateien direkte
# UTF-8-Zeichen: erst damit ist die Doppelmaskierung als FEHLERKLASSE
# beseitigt, denn htmlspecialchars darf dann folgenlos zweimal laufen.
#
# WARUM DAS HIER STEHT UND NICHT IN umlaute_umstellen.py. Am 03.09.2026
# gemessen: ein Lauf dieses Erzeugers gegen eine Kopie der veroeffentlichten
# 0.9.5 ergab 88 abweichende Zeilen in language_de.ini und 78 in
# language_en.ini - der Erzeuger haette 76x —, 11x &uuml;, 9x &auml;,
# 7x &rarr;, 4x &szlig;, 3x &ouml; und 2x &minus; ZURUECKGESCHRIEBEN. Nach
# Aufloesung der Entitaeten waren beide Dateien byteweise gleich; es ging also
# kein Schluessel und kein Wort verloren, nur die Schreibweise. Der
# ausgelieferte Stand war der richtige, der Erzeuger der falsche.
#
# Ein Nachlauf (umlaute_umstellen.py nach dem Erzeugen) waere die zweite
# Wahrheit: der naechste Erzeugerlauf holt die Entitaeten zurueck. Deshalb
# steht die Umsetzung hier - und die Wache unten weist ab, was sie nicht
# aufloesen kann.
#
# Was Entitaet BLEIBT und warum:
#   &nbsp; &shy;                 unsichtbare Zeichen. Als Zeichen im Quelltext
#                               waeren sie von einem Leerzeichen nicht zu
#                               unterscheiden - eine Wartungsfalle.
#   &#8209;                      dasselbe fuer den bindestrichfesten Trenner.
#   &amp; &lt; &gt; &quot; &apos; in HTML bedeutungstragend. Ein direktes '<'
#                               waere Auszeichnung statt Text.
SICHTBARE_ENTITAETEN = {
    "ä": "ä", "ö": "ö", "ü": "ü",
    "Ä": "Ä", "Ö": "Ö", "Ü": "Ü",
    "ß": "ß", "—": "—", "–": "–",
    "−": "−", "„": "„", "“": "“",
    "”": "”", "…": "…", "•": "•",
    "·": "·", "→": "→", "←": "←",
    "°": "°", "€": "€", "§": "§",
    "²": "²", "³": "³", "≤": "≤",
    "≥": "≥", "×": "×",
}
BLEIBEN_ENTITAET = ("&nbsp;", "&shy;", "&#8209;",
                    "&amp;", "&lt;", "&gt;", "&quot;", "&apos;")


def entitaeten_aufloesen(wert: str) -> str:
    """Sichtbare Entitaeten zum Zeichen machen; die uebrigen bleiben."""
    for ent, zeichen in SICHTBARE_ENTITAETEN.items():
        wert = wert.replace(ent, zeichen)
    return wert


def offene_entitaeten(wert: str) -> list:
    """Entitaeten, die nach der Aufloesung noch dastehen und NICHT bleiben duerfen."""
    rest = entitaeten_aufloesen(wert)
    for erlaubt in BLEIBEN_ENTITAET:
        rest = rest.replace(erlaubt, "")
    return re.findall(r"&[A-Za-z][A-Za-z0-9]{1,12};|&#[0-9]{1,6};", rest)


def ansage_abschnitt(sprache: str) -> str:
    """Der Abschnitt [ANSAGE] der gemeinsamen Sprachausgabe (Nr. 36 b) - EINE Quelle:
    Werkzeuge/gemeinsam_pruefen.py baut ihn aus Werkzeuge/gemeinsam/sprachausgabe_texte.json und
    haelt ihn spaeter gegen die .ini. Gesucht wird aufwaerts vom Ablageort dieses Erzeugers."""
    for d in [Path(__file__).resolve().parent] + list(Path(__file__).resolve().parents):
        for w in (d, d / "Werkzeuge"):
            if (w / "gemeinsam_pruefen.py").is_file() and (w / "gemeinsam" / "sprachausgabe_texte.json").is_file():
                sys.path.insert(0, str(w))
                import gemeinsam_pruefen
                return gemeinsam_pruefen.ini_abschnitt(sprache)
    raise SystemExit("Werkzeuge/gemeinsam_pruefen.py nicht gefunden - es wurde nichts geschrieben.")


def ini_schreiben(pfad: Path, kopf: str, texte: dict, sprache: str = "") -> None:
    abschnitte = {}
    for k, v in texte.items():
        a, s = k.split(".", 1)
        abschnitte.setdefault(a, {})[s] = v
    zeilen = [kopf]
    for a in REIHENFOLGE + [x for x in sorted(abschnitte) if x not in REIHENFOLGE]:
        if a not in abschnitte:
            continue
        zeilen.append("\n[" + a + "]")
        for s in sorted(abschnitte[a]):
            zeilen.append('%s = "%s"' % (s, entitaeten_aufloesen(abschnitte[a][s])))
    if sprache:
        zeilen.append("\n" + ansage_abschnitt(sprache).rstrip("\n"))
    pfad.parent.mkdir(parents=True, exist_ok=True)
    # BINAER geschrieben. Der Stil stand bis 13.09.2026 FEST auf CRLF;
    # seither gilt die Hausregel "alles wird auf LF gestellt". Die
    # Messung darunter ist der Stand von damals und bleibt als
    # Rueckblick stehen.
    #
    # BERICHTIGT am 03.09.2026, und die alte Begruendung war eine Zahl aus
    # einer Mustersuche, die etwas anderes gemessen hat als der Satz sagte.
    # Hier stand: "LF - das ist der Stil, den 140 von 146 Sprachdateien des
    # Bestands fuehren." Diese Zahl entsteht, wenn man ALLE .ini unter
    # templates/lang zusammenwirft. Getrennt gezaehlt (03.09.2026, ueber den
    # ganzen Arbeitsordner, byteweise, nur die jeweils hoechste Fassung je
    # Linie):
    #
    #     language_*.ini    CRLF 38, LF 11   von 49 Linien   -> CRLF
    #     help_*.ini        LF  216, CRLF 4  von 222 Dateien -> LF
    #
    # Die beiden Dateiarten haben also VERSCHIEDENE Hausformen, und die
    # gepoolte Zahl beschrieb keine von beiden. REGELN_2 nennt CRLF fuer
    # language_*.ini; das ist damit gemessen und nicht mehr nur behauptet.
    #
    # Diese Funktion schreibt ausschliesslich language_*.ini. Die help_*.ini
    # sind von Hand gepflegt und bleiben LF - wer sie hier aufnimmt, muss den
    # Stil mitentscheiden, statt ihn zu erben.
    text = "\n".join(zeilen) + "\n"
    pfad.write_bytes(text.encode("utf-8"))


def pruefen(wurzel: Path) -> int:
    fehler = []
    benutzt = benutzte_schluessel(wurzel)
    maskiert = maskierte_schluessel(wurzel)

    fehlend_de = sorted(benutzt - set(DE))
    fehlend_en = sorted(benutzt - set(EN))
    unbenutzt = sorted(set(DE) - benutzt)
    nur_de = sorted(set(DE) - set(EN))
    nur_en = sorted(set(EN) - set(DE))

    if fehlend_de:
        fehler.append("Im PHP benutzt, aber in DE nicht vorhanden: " + ", ".join(fehlend_de))
    if fehlend_en:
        fehler.append("Im PHP benutzt, aber in EN nicht vorhanden: " + ", ".join(fehlend_en))
    if unbenutzt:
        fehler.append("In DE vorhanden, aber im PHP nie benutzt: " + ", ".join(unbenutzt))
    if nur_de:
        fehler.append("Nur in DE: " + ", ".join(nur_de))
    if nur_en:
        fehler.append("Nur in EN: " + ", ".join(nur_en))

    # Maskierte Schluessel duerfen keine Auszeichnung und keine Entitaet tragen
    for name, tab in (("DE", DE), ("EN", EN)):
        for k in sorted(maskiert):
            w = tab.get(k, "")
            if "<" in w or "&" in w:
                fehler.append("%s %s laeuft durch by_e(), enthaelt aber Auszeichnung "
                              "oder eine Entitaet: %s" % (name, k, w))

    # Sichtbare Entitaeten: sie werden beim Schreiben aufgeloest. Was danach
    # noch als Entitaet dasteht und nicht ausdruecklich bleiben darf, ist ein
    # Befund - sonst wandert eine unbekannte Entitaet ungesehen in die Datei.
    #
    # Diese Wache gilt fuer JEDEN Wert, nicht nur fuer die maskierten. Bis
    # 0.9.5 pruefte der Erzeuger Entitaeten ausschliesslich in den Schluesseln,
    # die durch by_e() laufen - und genau deshalb ist ihm nicht aufgefallen,
    # dass er 166 Zeilen mit Entitaeten schreiben wollte, die roh ausgegeben
    # werden.
    for name, tab in (("DE", DE), ("EN", EN)):
        for k, w in sorted(tab.items()):
            offen = offene_entitaeten(w)
            if offen:
                fehler.append("%s %s traegt eine Entitaet, die weder aufgeloest "
                              "noch ausdruecklich erlaubt ist: %s"
                              % (name, k, ", ".join(sorted(set(offen)))))

    # Jeder Wert muss in eine INI-Zeile mit genau zwei Anfuehrungszeichen passen
    for name, tab in (("DE", DE), ("EN", EN)):
        for k, w in sorted(tab.items()):
            if '"' in w:
                fehler.append('%s %s enthaelt ein gerades Anfuehrungszeichen' % (name, k))
            if "\n" in w or "\r" in w:
                fehler.append("%s %s enthaelt einen Zeilenumbruch" % (name, k))
            if ";" in w and '"' not in w:
                pass    # ein Semikolon im quotierten Wert ist unbedenklich

    # Platzhalter muessen in beiden Sprachen gleich sein - ein sprintf, dem in
    # einer Sprache ein %s fehlt, gibt dort einen abgeschnittenen Satz aus.
    for k in sorted(set(DE) & set(EN)):
        pd = re.findall(r"%[sd]", DE[k])
        pe = re.findall(r"%[sd]", EN[k])
        if pd != pe:
            fehler.append("%s: Platzhalter unterschiedlich (DE %s, EN %s)" % (k, pd, pe))

    if fehler:
        for f in fehler:
            print("[FEHL]", f)
        return 1
    print("[OK]   %d Schluessel, DE und EN deckungsgleich, alle im PHP benutzt." % len(DE))
    print("[OK]   %d davon maskiert und frei von Auszeichnung." % len(maskiert))
    print("[OK]   Keine geraden Anfuehrungszeichen, Platzhalter passen zusammen.")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Aufruf: byd_sprache_erzeugen.py <pluginordner> [--pruefen]")
        return 2
    wurzel = Path(sys.argv[1])
    if not (wurzel / "webfrontend").is_dir():
        print("[FEHL] %s sieht nicht wie ein Plugin-Ordner aus (kein webfrontend/)."
              % wurzel)
        return 2
    code = pruefen(wurzel)
    if "--pruefen" in sys.argv:
        return code
    if code:
        print("Es wurde nichts geschrieben.")
        return code
    # Die Abschnitte [ANSAGE] VOR dem ersten Schreiben holen: fehlt die Quelle, wird nichts geschrieben.
    ansage_de, ansage_en = ansage_abschnitt("de"), ansage_abschnitt("en")
    ini_schreiben(wurzel / "templates/lang/language_de.ini", KOPF_DE, DE, "de" if ansage_de else "")
    ini_schreiben(wurzel / "templates/lang/language_en.ini", KOPF_EN, EN, "en" if ansage_en else "")
    print("Geschrieben: templates/lang/language_de.ini und language_en.ini")
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
    sys.exit(main())
