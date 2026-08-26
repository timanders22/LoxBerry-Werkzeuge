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

Aufruf:  byd_sprache_erzeugen.py <pluginordner> [--pruefen]

Geschrieben wird nur, wenn alle Pruefungen bestehen. Ein Erzeuger, der im
Zweifel die Haelfte schreibt, kostet die Sprachausgabe.
"""

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

# ---- Reiter und Legende ----------------------------------------------------
"REITER.EINSTELLUNGEN": "Einstellungen",
"REITER.LOXONE": "Einbindung in Loxone",
"REITER.TEST": "Test",
"REITER.LOG": "Logdateien",

"LEGENDE.LESEN": "Ansehen &mdash; fragt nur ab, verändert nichts",
"LEGENDE.TECHNIK": "Technische Auskunft &mdash; für die Fehlersuche",
"LEGENDE.AKTION": "Löst etwas aus &mdash; sendet oder verändert",
"LEGENDE.AKTION_TOKEN": "Löst etwas aus &mdash; ein neues Token macht alle Adressen im Miniserver ungültig",
"LEGENDE.AKTION_LOG": "Löst etwas aus &mdash; die bisherigen Zeilen sind danach fort",

# ---- Allgemein -------------------------------------------------------------
"ALLG.BEANSTANDUNG": "Bitte diese Punkte berichtigen:",
"ALLG.FEHLER_FORMTOKEN": "Das Formular trug kein gültiges Merkmal dieser Sitzung. Es wurde nichts geändert. Bitte die Seite neu laden und noch einmal absenden. Steht noch kein Aktionstoken in der Konfiguration, entsteht es beim ersten Aufruf dieser Seite &mdash; dann genügt ein Neuladen.",
"ALLG.FEHLER_FORMULAR": "Das Formular hat sich nicht zu erkennen gegeben. Es wurde nichts geändert &mdash; ein falsch geratenes Formular löscht sonst genau das, was behalten werden sollte.",
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
"EINST.H_DIENST": "Abrufdienst",
"EINST.DIENST_ERKLAERUNG": "Der Dienst holt die Werte im eingestellten Takt und legt sie als Zwischenspeicher ab. Oberfläche und Miniserver lesen nur diesen Zwischenspeicher &mdash; deshalb antwortet der Endpunkt in Millisekunden und nicht in Sekunden.",
"EINST.K_START": "Dienst starten",
"EINST.K_RESTART": "Dienst neu starten",
"EINST.K_STOP": "Dienst anhalten",
"EINST.DIENST_START": "Der Dienst wurde gestartet.",
"EINST.DIENST_STOP": "Der Dienst wurde angehalten.",
"EINST.DIENST_RESTART": "Der Dienst wurde neu gestartet.",
"EINST.H_KONTO": "BYD-Konto",
"EINST.KONTO_ERKLAERUNG": "Es sind die Zugangsdaten des BYD-Kontos aus der BYD-App, nicht die eines Händlerportals. Sie liegen in einer eigenen Datei mit den Rechten 0600 und werden nie angezeigt &mdash; nur ihre Länge. Ein leer gelassenes Passwortfeld löscht nichts.",
"EINST.L_BENUTZER": "Benutzername",
"EINST.H_BENUTZER": "Derselbe Name, mit dem Sie sich in der BYD-App anmelden &mdash; je nach Konto eine E-Mail-Adresse oder eine Telefonnummer. Es wird nichts umgeschrieben: was hier steht, geht so an die Schnittstelle.",
"EINST.L_PASSWORT": "Passwort",
"EINST.H_PASSWORT": "Leer lassen behält das gespeicherte Passwort.",
"EINST.PW_GESETZT": "gespeichert, %d Zeichen",
"EINST.PW_LEER": "noch keines gespeichert",
"EINST.L_PIN": "Steuer-PIN",
"EINST.H_PIN": "Die PIN, mit der die BYD-App schreibende Befehle freigibt. Ohne sie weist BYD jeden Schaltbefehl ab; für das reine Ablesen wird sie nicht gebraucht. Vier bis acht Ziffern.",
"EINST.PIN_GESETZT": "gespeichert",
"EINST.PIN_LEER": "noch keine gespeichert",
"EINST.L_LAND": "Länderkennung",
"EINST.H_LAND": "Zwei Buchstaben, etwa DE oder AT. Nur nötig, wenn die Bibliothek danach fragt &mdash; ob sie das tut, sagt der Selbsttest im Reiter Test in der Zeile über die erkannten Konfigurationsfelder. Leer lassen, wenn unklar.",
"EINST.L_ZUGANG_LOESCHEN": "Benutzername, Passwort und PIN vollständig löschen",
"EINST.H_ZUGANG_LOESCHEN": "Löscht auch die Zweitschrift neben dem Konfigurationsordner. Ohne diesen Haken bliebe sie liegen und wäre bei der nächsten Neuinstallation wieder da &mdash; ein Löschen, das nicht löscht, ist schlimmer als keines.",
"EINST.H_TAKT": "Abruftakt",
"EINST.TAKT_WARNUNG": "Jeder Abruf <b>weckt das Fahrzeug</b>: die Schnittstelle fordert das Auto zur Meldung auf, statt in einen Zwischenspeicher der Wolke zu sehen. Ein zu dichter Takt kostet Ruhestrom und kann in eine Sperre laufen. Die Untergrenze von 120 Sekunden ist eine eigene Wahl und keine Angabe von BYD.",
"EINST.L_INTERVALL": "Takt in Sekunden",
"EINST.H_INTERVALL": "120 bis 3600. Die Vorgabe von 300 Sekunden entspricht der Vorgabe des ioBroker-Adapters derselben Schnittstelle.",
"EINST.L_VERLAUF_TAGE": "Verlauf aufbewahren (Tage)",
"EINST.H_VERLAUF_TAGE": "Je Tag und Fahrzeug eine kleine CSV-Datei im Datenordner. Ältere werden entfernt.",
"EINST.L_GPS_EIN": "Standort mit abfragen",
"EINST.H_GPS_EIN": "Der Standort ist eine eigene Abfrage. Wer ihn nicht braucht, spart je Takt einen Aufruf &mdash; und die Position des Fahrzeugs verlässt dann den Wagen nicht.",
"EINST.L_MQTT_BIBLIOTHEK": "Die Bibliothek darf ihren eigenen MQTT-Weg benutzen",
"EINST.H_MQTT_BIBLIOTHEK": "Das ist <b>nicht</b> das MQTT-Gateway des LoxBerry, sondern der Broker von BYD: die Bibliothek wartet damit auf die Bestätigung eines Befehls, statt zu pollen. Ohne diesen Haken dauert eine Rückmeldung länger. Der Weg zum Miniserver bleibt davon unberührt.",
"EINST.H_STEUERUNG": "Schreibende Befehle",
"EINST.STEUERUNG_ERKLAERUNG": "Ab Werk gesperrt, und das ist Absicht: ein Vorgabewert, der beim ersten Lauf ungefragt schaltet, ist ein Fehler. Mit dem Haken darf der Miniserver ver- und entriegeln, klimatisieren, Sitz- und Batterieheizung stellen, das Auto suchen lassen, blinken und die Fenster schließen. Was BYD annimmt, ist damit noch nicht gesagt &mdash; die Quittung ist nicht die Wirkung.",
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
"EINST.VIN_HINWEIS": "Die laufende Nummer ist nach Fahrgestellnummer sortiert und bleibt damit stabil. In den Adressen für Loxone lässt sich statt der Nummer auch die Fahrgestellnummer angeben &mdash; das ist die haltbarere Angabe.",
"EINST.GESPEICHERT": "Die Einstellungen wurden gespeichert.",
"EINST.FEHLER_ZAHL": "%s: bitte eine ganze Zahl eintragen.",
"EINST.FEHLER_BEREICH": "%s: der Wert muss zwischen %d und %d liegen.",
"EINST.FEHLER_TEMP_TAUSCH": "Die kleinste Zieltemperatur ist größer als die größte. Bitte tauschen.",
"EINST.FEHLER_PIN": "Die Steuer-PIN besteht aus vier bis acht Ziffern.",
"EINST.FEHLER_LAND": "Die Länderkennung besteht aus genau zwei Buchstaben, etwa DE.",
"EINST.FEHLER_ZUGANG_SPEICHERN": "Die Zugangsdaten ließen sich nicht speichern. Rechte im Konfigurationsordner prüfen.",
"EINST.FEHLER_ZUGANG_LOESCHEN": "Die Zugangsdaten ließen sich nicht vollständig löschen.",
"EINST.ZUGANG_GELOESCHT": "Benutzername, Passwort und PIN wurden gelöscht, die Zweitschrift ebenfalls.",
"EINST.WARN_PW_OHNE_KONTO": "Es ist ein Passwort hinterlegt, aber kein Benutzername. So kann die Anmeldung nicht gelingen.",
"EINST.HINWEIS_PIN_FEHLT": "Schreibende Befehle sind zugelassen, es ist aber keine Steuer-PIN hinterlegt. BYD wird jeden Schaltbefehl abweisen.",
"EINST.FEHLER_SPEICHERN": "Die Konfiguration ließ sich nicht schreiben (%s).",
"EINST.FEHLER_TOPIC": "Der Themenpfad darf nur Buchstaben, Ziffern, Bindestrich, Unterstrich und Schrägstrich enthalten.",
"EINST.L_MQTT_EIN": "Werte über MQTT senden",
"EINST.L_MQTT_TOPIC": "Themenpfad",
"EINST.H_MQTT_TOPIC": "Vorsatz aller Themen. Ihn nachträglich zu ändern benennt auf einer bestehenden Anlage <b>sämtliche</b> Themen um &mdash; die virtuellen Eingänge in Loxone und die Werte im Broker hängen daran.",

# ---- MQTT ------------------------------------------------------------------
"MQTT.GATEWAY_ERKLAERUNG": "Das MQTT-Gateway ist seit LoxBerry 3 <b>Bestandteil des Systems</b> und kein Plugin. Es wird nicht nachinstalliert, sondern unter <span class='sm-mono'>System &rarr; MQTT Gateway</span> eingeschaltet.",
"MQTT.H_ZUSTAND": "Zustand des Gateways",
"MQTT.NICHT_GEFUNDEN": "In der <span class='sm-mono'>general.json</span> des LoxBerry ist kein MQTT-Abschnitt zu finden. Ohne ihn kann nichts weitergeleitet werden.",
"MQTT.AUTOSTART_AUS": "Das MQTT-Gateway steht nicht auf Autostart (<span class='sm-mono'>System &rarr; MQTT Gateway</span>). Es wird gesendet, aber vermutlich hört niemand zu.",
"MQTT.AUTOSTART_EIN": "Das Gateway steht auf Autostart. Es startet nach einem Neustart des LoxBerry von selbst.",
"MQTT.T_AUTOSTART": "Autostart des Gateways",
"MQTT.T_BROKER": "Broker",
"MQTT.T_UDP": "UDP-Eingang des Gateways",
"MQTT.T_PLUGIN": "Dieses Plugin sendet über MQTT",
"MQTT.H_ABO": "Das Abo im Gateway eintragen",
"MQTT.ABO_WARNUNG": "<b>Ohne diesen Eintrag kommt am Miniserver nichts an.</b> Das ist die häufigste Fehlerursache überhaupt.",
"MQTT.ABO_SCHRITTE": "Im LoxBerry unter <span class='sm-mono'>System &rarr; MQTT Gateway</span> in der Liste der Abos genau diese Zeile eintragen und speichern:",
"MQTT.H_THEMEN": "Alle Themen, die dieses Plugin veröffentlicht",
"MQTT.THEMEN_ERKLAERUNG": "Diese Liste entsteht aus derselben Quelle wie die Statuszeile des Endpunkts. Der MQTT-Weg trägt damit dieselben Werte wie der HTTP-Weg &mdash; ein Plugin, dessen MQTT-Meldung weniger enthält, macht die Umstellung unmöglich, und zwar unauffällig: es kommen ja Werte an, nur eben nicht alle. Der Reiter Test misst die Übereinstimmung nach.",
"MQTT.T_THEMA": "Thema",
"MQTT.T_BEDEUTUNG": "Bedeutung",
"MQTT.PLATZHALTER": "<span class='sm-mono'>N</span> steht für die laufende Nummer des Fahrzeugs, beginnend bei 1.",
"MQTT.UMBENENNUNG": "Über MQTT wird der <b>Zeitstempel</b> gesendet, nicht das Alter: beim Senden ist das Alter immer null. Die Gegenseite rechnet es aus. In Loxone gilt <span class='sm-mono'>Alter = (Loxone-Zeit + 1230768000) &minus; ts</span> &mdash; Loxone zählt Sekunden seit dem 01.01.2009.",

# ---- Einbindung in Loxone --------------------------------------------------
"LOX.H_TITEL": "Einbindung in Loxone",
"LOX.EINLEITUNG": "Zwei Wege stehen offen, und sie schließen sich nicht aus. <b>MQTT</b> ist der Regelweg: das Gateway legt die virtuellen Eingänge selbst an, und in Loxone genügt ein passend benannter Eingang. Der <b>HTTP-Endpunkt</b> ist der Weg für alles, was Loxone selbst holen soll &mdash; und der einzige für schreibende Befehle.",
"LOX.S1_TITEL": "Schritt 1: Weg festlegen",
"LOX.S1_TEXT": "MQTT ist dem HTTP-Abruf vorzuziehen: das Gateway erzeugt die Namen der Eingänge selbst, der HTTP-Weg verlangt je Wert eine eigene Befehlserkennung. Wer nur wenige Werte braucht oder ohne Broker arbeiten will, nimmt den Endpunkt aus Schritt 3.",
"LOX.S2_TITEL": "Schritt 2: Abo im MQTT-Gateway eintragen",
"LOX.S2_TEXT": "Im LoxBerry unter <span class='sm-mono'>System &rarr; MQTT Gateway</span> dieses Abo eintragen:",
"LOX.S2_WARNUNG": "<b>Ohne diesen Eintrag kommt am Miniserver nichts an.</b>",
"LOX.S3_TITEL": "Schritt 3: Virtuelle Eingänge über HTTP",
"LOX.S3_TEXT": "Ein virtueller HTTP-Eingang mit dieser Adresse holt alle Werte in einem Aufruf. Je Wert eine Befehlserkennung mit dem Suchtext aus der Tabelle darunter.",
"LOX.S3_BEFEHLE": "<p>Der Titel ist für Menschen, der Suchtext für die Maschine: der Titel darf sich ändern, ohne dass eine bestehende Anlage etwas merkt &mdash; gesucht wird weiter nach dem Text in der zweiten Spalte. Das Semikolon gehört <b>ins Muster</b>: Loxone sucht wörtlich und nimmt den ersten Treffer, und ohne das Semikolon steckte <span class='sm-mono'>KM=</span> auch in einem künftigen <span class='sm-mono'>RESTKM=</span>.</p>",
"LOX.S3_STRICH": "Ein <b>Strich</b> als Wert bedeutet: dieser Wert liegt nicht vor. Es wird bewusst keine 0 gesendet &mdash; eine 0 sähe aus wie ein Messwert. Loxone behält dann den letzten gültigen Wert, und dass er alt ist, sagt das Feld ALTER.",
"LOX.S3_HERKUNFT": "Die Spalte <b>Herkunft</b> ist ernst gemeint. <b>Dokumentation</b> heißt: der Feldname stammt aus einer offenen Quelle und ist an keinem Fahrzeug dieses Hauses gemessen. <b>Gerechnet</b> heißt: das Feld kommt gar nicht vom Fahrzeug, sondern entsteht hier &mdash; fehlt die Zutat, bleibt es leer. Ein Feld, das niemand gemessen hat, darf nicht aussehen wie eines, das jemand gemessen hat. Der Reiter Test zeigt, welche Felder die Bibliothek bei <b>Ihrem</b> Fahrzeug wirklich getroffen hat.",
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
"LOX.ALLES_TEXT": "Die beiden Knöpfe erzeugen fertige Importdateien für Loxone Config. Die Eingänge liest man unter <span class='sm-mono'>Virtuelle Eingänge &rarr; Vordefinierte HTTP-Geräte &rarr; Vorlage Importieren…</span> ein, die Ausgänge unter <span class='sm-mono'>Virtuelle Ausgänge &rarr; Vordefinierte Geräte &rarr; Vorlage Importieren…</span> &mdash; beim Ausgang fehlt im Knopfnamen der Zusatz HTTP.",
"LOX.K_VORLAGE": "Vorlage für Loxone Config erzeugen",
"LOX.K_VORLAGE_VO": "Vorlage der Steuerbefehle erzeugen",
"LOX.VORLAGE_ZWEIMAL": "Loxone Config <b>legt beim Import neu an und überschreibt nichts</b>. Zweimal eingelesen heißt doppelte Bausteine, beide auf derselben Adresse &mdash; und Config meldet dazu nichts.",
"LOX.VORLAGE_HINWEIS": "Erzeugt vom LoxBerry-Plugin BYD Autos. Zweimal eingelesen ergibt doppelte Bausteine.",
"LOX.VORLAGE_UNGEPRUEFT": "Dieses Fahrzeug hat noch nie geantwortet - es sind alle Felder enthalten. Nach dem ersten erfolgreichen Abruf die Vorlage erneut holen, dann stehen nur noch die Felder darin, die das Fahrzeug wirklich liefert.",
"LOX.VORLAGE_VO_HINWEIS": "Steuerbefehle des LoxBerry-Plugins BYD Autos. Sie wirken nur, wenn im Reiter Einstellungen schreibende Befehle zugelassen sind.",
"LOX.S4_TITEL": "Schritt 4: Standort",
"LOX.S4_TEXT": "Der Standort steht in einer eigenen Antwort, damit die Statuszeile aus reinen Ganzzahlen besteht. Ein Breitengrad mit Punkt zwischen Ganzzahlen wäre für eine Befehlserkennung eine Falle.",
"LOX.S5_TITEL": "Schritt 5: Befehle senden",
"LOX.S5_TEXT": "Je Befehl ein virtueller Ausgang. Als Adresse des Ausgangs trägt man den Rechnernamen des LoxBerry ein, als Befehl den Pfad aus der Tabelle. Ein Zustand gehört an <b>einen</b> Ausgang mit Ein- und Ausbefehl, nicht an zwei Ausgänge &mdash; die erzeugte Importdatei macht das so.",
"LOX.S5_WARNUNG": "Diese Adressen enthalten das Token. Wer ein neues Token erzeugt, muss sie alle nachziehen &mdash; ein virtueller Ausgang wertet die Antwort nicht aus, ein Ausfall bliebe also still.",
"LOX.S5_KEIN_LADEN": "<b>Laden starten und anhalten gibt es hier nicht.</b> Die verwendete Bibliothek nennt dafür keine Methode. Ein Ausgang, den der Hersteller nicht bedienen kann, wird gar nicht erst angeboten: ein Baustein, der nur Absagen erntet, ist schlimmer als keiner.",
"LOX.S6_TITEL": "Schritt 6: Token und Selbsttest",
"LOX.S6_TEXT": "Das Token schützt den unangemeldeten Endpunkt. Die zweite Adresse beantwortet die Frage „stimmt das in Loxone eingetragene Token noch?“ <b>ohne am Fahrzeug etwas auszulösen</b> &mdash; kein Gerätekontakt, kein Schreibzugriff. Ohne so einen Weg gibt es nur zwei schlechte Möglichkeiten: entweder man schaltet wirklich, oder man erfährt es nie.",
"LOX.T_TOKEN": "Token",
"LOX.T_SELBSTTEST": "Selbsttest (löst nichts aus)",
"LOX.K_TOKEN_NEU": "Neues Token erzeugen",
"LOX.TOKEN_NEU": "Es wurde ein neues Token erzeugt. Alle bisherigen Adressen im Miniserver sind damit ungültig und müssen nachgezogen werden.",
"LOX.S7_TITEL": "Schritt 7: Ausfallerkennung",
"LOX.S7_TEXT": "<b>Virtuelle Eingänge behalten ihren letzten Wert.</b> Fällt der Dienst aus, sieht in der App alles normal aus. Verdrahtet werden deshalb zwei Dinge: <span class='sm-mono'>OK</span> (0 heißt: dieser Abruf hat nichts gebracht) und <span class='sm-mono'>ALTER</span> (wächst, solange nichts Neues kommt). Die Schwelle für eine Meldung liegt deutlich über dem Abruftakt, damit ein einzelner verpasster Durchlauf keine Meldung auslöst. Und der Sonderfall gehört mitgedacht: <span class='sm-mono'>ALTER = &minus;1</span> heißt „es hat noch nie einen erfolgreichen Abruf gegeben“ &mdash; das sieht frischer aus als jeder echte Wert, weshalb OK immer mit auszuwerten ist.",
"LOX.S8_TITEL": "Schritt 8: Komplette Baustein-Liste zum Nachbauen",
"LOX.S8_TEXT": "Wer diese Tabelle von oben nach unten abarbeitet, hat die Funktion nachgebaut, ohne nachzudenken. Loxone Config führt alle Bausteine in der Baustein-Suche (F5). Optionale Zeilen sind als solche gekennzeichnet.",
"LOX.S8_ERLAEUTERUNG": "<p><b>Zu den UND- und ODER-Bausteinen:</b> sie haben in Loxone genau zwei Eingänge. Wo drei Bedingungen zusammenkommen, stehen zwei Bausteine hintereinander &mdash; eine Zeichnung mit vier Eingängen an einem ODER ist nicht nachbaubar.</p><p><b>Zum Benachrichtigungs-Baustein:</b> er sendet nur beim Wechsel von Aus auf Ein. Niemals mehrere Quellen direkt an seinen Eingang &mdash; erst über ODER zusammenführen, sonst verschluckt eine dauerhaft aktive Quelle alle übrigen.</p><p><b>Zur Loxone-Zeitrechnung:</b> Loxone zählt Sekunden seit dem 01.01.2009. Liefert ein Zeit-Baustein Unix-Zeit (Wert um 1,7 Milliarden), sind <span class='sm-mono'>1230768000</span> abzuziehen.</p>",
"LOX.T_BAUSTEIN": "Baustein (Typ)",
"LOX.T_NAMENSVORSCHLAG": "Name (Vorschlag)",
"LOX.T_PARAMETER": "Parameter",
"LOX.T_EINGAENGE": "Eingänge verbinden mit",
"LOX.S9_TITEL": "Schritt 9: Gegenprobe",
"LOX.S9_TEXT": "Diese vier Adressen einmal im Browser aufrufen. Die vierte ist die wichtigste: erst eine <b>Absage</b> auf eine erfundene Aktion macht die drei Erfolge aussagekräftig.",
"LOX.T_PRUEFUNG": "Aufruf",
"LOX.T_ERWARTUNG": "Erwartete Antwort",

# ---- Baustein-Liste --------------------------------------------------------
"BAUSTEIN.T_VE": "Virtueller Eingang",
"BAUSTEIN.T_VA": "Virtueller Ausgang Befehl",
"BAUSTEIN.T_NICHT": "NICHT",
"BAUSTEIN.T_ODER": "ODER",
"BAUSTEIN.T_UND": "UND",
"BAUSTEIN.T_SWS": "Schwellwertschalter",
"BAUSTEIN.T_EVZ": "Einschaltverzögerung",
"BAUSTEIN.T_BENACHR": "Benachrichtigung",
"BAUSTEIN.T_STATUS": "Statusbaustein",
"BAUSTEIN.T_WOCHE": "Wochenuhr",
"BAUSTEIN.T_TASTER": "Taster (Merker)",
"BAUSTEIN.N_NICHT": "BYD Abruf gestört",
"BAUSTEIN.N_ALT": "BYD Werte zu alt",
"BAUSTEIN.P_ALT": "Ein über 900, Aus unter 700",
"BAUSTEIN.N_STOER": "BYD Störung",
"BAUSTEIN.N_EVZ": "BYD Störung hält an",
"BAUSTEIN.P_EVZ": "Verzögerung 600 s",
"BAUSTEIN.N_MELD1": "BYD Meldung Störung",
"BAUSTEIN.P_MELD": "Text frei wählbar",
"BAUSTEIN.N_SOC": "BYD Akku niedrig",
"BAUSTEIN.P_SOC": "Ein unter 20, Aus über 30",
"BAUSTEIN.N_MELD2": "BYD Meldung Akku",
"BAUSTEIN.N_OFFEN": "BYD Fahrertür entriegelt",
"BAUSTEIN.P_OFFEN": "Ein unter 1, Aus über 1 &mdash; der Wert ist gerätespezifisch, erst am Fahrzeug ablesen",
"BAUSTEIN.N_UND": "BYD offen und niemand da",
"BAUSTEIN.N_MELD3": "BYD Meldung offen",
"BAUSTEIN.N_STATUS": "BYD Ladezustand als Text",
"BAUSTEIN.P_STATUS": "0 nicht verbunden, 1 lädt, 15 Stecker steckt",
"BAUSTEIN.N_WOCHE": "BYD Vorklimatisierung",
"BAUSTEIN.P_WOCHE": "Abfahrtszeiten je Wochentag",
"BAUSTEIN.N_TASTER": "BYD Klima jetzt",
"BAUSTEIN.P_TASTER": "aus der Visualisierung",
"BAUSTEIN.N_ODER2": "BYD Klima auslösen",
"BAUSTEIN.N_VA_KLIMA": "BYD Klima",
"BAUSTEIN.P_VA_KLIMA": "Ein- und Ausbefehl aus der Importdatei",
"BAUSTEIN.N_VA_VERR": "BYD Verriegelung",
"BAUSTEIN.P_VA_VERR": "Ein verriegelt, Aus entriegelt",
"BAUSTEIN.N_VA_ABRUF": "BYD Sofortabruf",
"BAUSTEIN.P_VA_ABRUF": "nur Einbefehl",
"BAUSTEIN.ANWESEND": "Anwesenheit (invertiert)",
"BAUSTEIN.MANUELL": "aus der Visualisierung",

# ---- Test ------------------------------------------------------------------
"TEST.H_SELBSTPRUEFUNG": "Selbstprüfung",
"TEST.EINLEITUNG": "Diese Prüfungen beantworten <b>ohne Loxone und ohne BYD-Konto</b>, ob die Einrichtung trägt. Was sich nur mit Fahrzeug prüfen ließe, steht am Ende der Seite als solches benannt.",
"TEST.BILANZ": "%d von %d Prüfungen bestanden, dazu %d Hinweise.",
"TEST.T_FRAGE": "Frage",
"TEST.T_BEFUND": "Befund",
"TEST.LEGENDE_PUNKT": "Ein grauer Punkt ist ein <b>Hinweis</b>: die Zeile trifft hier nicht zu oder lässt sich in diesem Aufbau nicht messen. Sie zählt bewusst nicht als bestanden &mdash; eine Zusammenfassung darf nicht besser aussehen als ihr schlechtester Punkt.",
"TEST.H_LESEN": "Ansehen",
"TEST.K_STATUS": "Statuszeile aufrufen",
"TEST.K_POSITION": "Standort aufrufen",
"TEST.K_FAHRZEUGE": "Fahrzeugliste aufrufen",
"TEST.K_SELFTEST": "Selbsttest des Endpunkts",
"TEST.H_TECHNIK": "Technische Auskunft",
"TEST.K_SELBSTTEST": "Selbsttest des Dienstes",
"TEST.K_ENDPUNKT": "Endpunkt jetzt messen",
"TEST.K_FELDER": "Feldzuordnung vorschlagen",
"TEST.K_JSON": "Rohdaten als JSON ansehen",
"TEST.H_FELDER_ERKLAERUNG": "<b>Feldzuordnung vorschlagen</b> fragt das Fahrzeug und listet <b>jedes Blatt der Antwort mit seinem Pfad</b> auf &mdash; samt der Angabe, welches Feld darauf getroffen hat. Damit beantwortet das Gerät die Frage nach den Namen, nicht eine Vermutung. Der Aufruf braucht Zugangsdaten und Netz und dauert einige Sekunden.",
"TEST.H_SCHALTEN": "Schalten",
"TEST.SCHALTEN_WARNUNG": "<b>Diese Knöpfe wirken sofort am Fahrzeug.</b> Sie sind kein Trockenlauf. Ob BYD einen Befehl annimmt, sagt die Antwort; ob das Fahrzeug ihn ausführt, zeigt erst der nächste Abruf.",
"TEST.SCHALTEN_GESPERRT": "Schreibende Befehle sind gesperrt. Die Knöpfe werden abgewiesen, bis der Haken im Reiter Einstellungen gesetzt ist.",
"TEST.L_FAHRZEUG": "Fahrzeug",
"TEST.H_FAHRZEUG": "Die laufende Nummer aus der Fahrzeugliste.",
"TEST.L_TEMP": "Zieltemperatur in Grad Celsius",
"TEST.H_TEMP": "Ganze oder halbe Grad. Außerhalb der eingestellten Grenzen wird abgewiesen.",
"TEST.L_MINUTEN": "Laufzeit in Minuten (freiwillig)",
"TEST.H_MINUTEN": "Nur wirksam, wenn die installierte Bibliothek dafür einen Parameter kennt. Kann sie es nicht, steht das ausdrücklich in der Antwort &mdash; eine Angabe, die nicht ankommt, wird genannt und nicht stillschweigend übergangen.",
"TEST.L_STUFE": "Stufe für Sitz- und Batterieheizung",
"TEST.H_STUFE": "Welche Stufen dieses Fahrzeug kennt, ist nicht dokumentiert. 0 schaltet aus.",
"TEST.K_ABRUF": "Sofort abrufen",
"TEST.H_UNGEPRUEFT": "Was hier nicht geprüft werden kann",
"TEST.UNGEPRUEFT": "Ob die Anmeldung an der BYD-Schnittstelle gelingt, ob die Feldnamen dieser Feldtabelle bei diesem Fahrzeug zutreffen und ob die schreibenden Befehle am Fahrzeug die erwartete Wirkung haben &mdash; das entscheidet sich am Konto und am Auto, nicht hier. Die Feldnamen stammen aus offenen Quellen und sind an keinem Fahrzeug dieses Hauses gemessen.",
"TEST.UNBEKANNT": "Ergebnis unbekannt:",
"TEST.KEINE_MESSPUNKTE": "keine Messpunkte für heute",
"TEST.F_ENDPUNKT": "Antwortet der eigene Endpunkt über HTTP?",
"TEST.A_ENDPUNKT_UNKLAR": "nicht feststellbar &mdash; es gibt hier weder curl noch allow_url_fopen, oder der Webserver kann sich während des Seitenaufbaus nicht selbst aufrufen. Das ist keine Aussage über den Endpunkt.",
"TEST.A_ENDPUNKT_OK": "ja, HTTP 200 mit der erwarteten Kennung (Messung %d s alt)",
"TEST.A_ENDPUNKT_FEHL": "nein: HTTP %d, Antwort: %s",
"TEST.A_LEER": "leer",
"TEST.F_VENV": "Ist die virtuelle Python-Umgebung vorhanden?",
"TEST.A_VENV_FEHLT": "nein &mdash; das Plugin neu installieren, die Installation legt sie an",
"TEST.F_PYTHON": "Ist das Python neu genug (3.11 oder neuer)?",
"TEST.A_PYTHON_ZU_ALT": "zu alt für pybyd",
"TEST.A_PYTHON_UNBEKANNT": "nicht feststellbar",
"TEST.F_LIB": "Lässt sich die Bibliothek laden, und in welcher Fassung?",
"TEST.A_LIB_FEHLT": "nein &mdash; ohne pybyd kann der Dienst nicht arbeiten",
"TEST.F_DIENST": "Läuft der Abrufdienst?",
"TEST.A_DIENST_LAEUFT": "ja, Prozessnummer",
"TEST.A_DIENST_SOLL_TOT": "nein &mdash; er soll laufen, tut es aber nicht. Der Grund steht im Reiter Logdateien.",
"TEST.A_DIENST_GESTOPPT": "nein, bewusst angehalten",
"TEST.F_KONTO": "Ist ein Benutzername hinterlegt?",
"TEST.A_KONTO_FEHLT": "nein &mdash; Reiter Einstellungen",
"TEST.F_PASSWORT": "Ist ein Passwort hinterlegt?",
"TEST.A_PASSWORT_DA": "ja, %d Zeichen (der Inhalt wird nicht angezeigt)",
"TEST.A_PASSWORT_FEHLT": "nein &mdash; Reiter Einstellungen",
"TEST.F_PIN": "Ist die Steuer-PIN hinterlegt?",
"TEST.A_PIN_DA": "ja, %d Ziffern",
"TEST.A_PIN_FEHLT": "nein &mdash; BYD wird jeden schreibenden Befehl abweisen",
"TEST.A_PIN_UNNOETIG": "für das reine Ablesen nicht nötig. Sie wird erst gebraucht, wenn schreibende Befehle zugelassen werden.",
"TEST.F_RECHTE": "Ist die Zugangsdatei vor fremden Blicken geschützt?",
"TEST.A_ZUGANGSDATEI_FEHLT": "die Zugangsdatei fehlt",
"TEST.F_SICHERUNG": "Gibt es eine Zweitschrift der Konfiguration?",
"TEST.A_SICHERUNG_FEHLT": "noch keine. Sie entsteht beim ersten Speichern und liegt <b>neben</b> dem Konfigurationsordner &mdash; darin würde sie beim Update mit gelöscht.",
"TEST.F_FAHRZEUGE": "Sind Fahrzeuge erkannt?",
"TEST.A_FAHRZEUGE": "ja, %d",
"TEST.A_KEINE_FAHRZEUGE": "nein &mdash; bis zum ersten erfolgreichen Abruf ist das normal",
"TEST.F_ZUORDNUNG": "Wurden die Felder in der Antwort gefunden?",
"TEST.A_ZUORDNUNG_LEER": "keine Aussage möglich: es ist kein Fahrzeug im Abbild. Eine Prüfung über eine leere Menge ist kein Haken.",
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
"TEST.A_MQTT_UNBENUTZT": "dieses Plugin sendet nicht über MQTT &mdash; der Zustand des Gateways ist dann ohne Belang",
"TEST.A_MQTT_NICHT_GEFUNDEN": "in der general.json ist kein MQTT-Abschnitt zu finden",
"TEST.A_MQTT_AUS": "das Gateway steht nicht auf Autostart. Ohne das kommt am Miniserver nichts an.",
"TEST.F_VORGABEN": "Führen Dienst und Oberfläche dieselben Vorgabewerte?",
"TEST.A_VORGABEN_UNKLAR": "die Liste im Dienst ließ sich nicht auslesen &mdash; der Vergleich wurde nicht gemacht",
"TEST.A_VORGABEN_OK": "ja, alle %d Vorgaben des Dienstes stehen auch in der Oberfläche",
"TEST.A_VORGABEN_FEHLT": "nein &mdash; nur im Dienst: %s",
"TEST.F_REITER": "Stimmen Reiterliste, Reiterleiste und Bereiche überein?",
"TEST.A_REITER_UNKLAR": "die Liste ließ sich nicht auslesen &mdash; der Vergleich wurde nicht gemacht",
"TEST.A_REITER_OK": "ja, alle drei Stellen führen dieselben %d Namen",
"TEST.A_REITER_FEHL": "nein: Liste %d, Leiste %d, Bereiche %d. Fehlt ein Name in der Liste, springt die Seite nach jedem Absenden zurück.",
"TEST.F_MUSTER": "Ist jeder Suchtext in der Statuszeile eindeutig?",
"TEST.A_MUSTER_OK": "ja, alle %d Suchtexte kommen genau einmal vor",
"TEST.A_MUSTER_FEHL": "nein &mdash; mehrdeutig: %s. Loxone nimmt den ersten Treffer und liefert damit den Wert eines anderen Feldes.",
"TEST.F_WEGE": "Trägt der MQTT-Weg dieselben Werte wie der HTTP-Weg?",
"TEST.A_WEGE_OK": "ja: %d Werte in der Statuszeile, %d Themen je Fahrzeug",
"TEST.A_WEGE_FEHL": "nein &mdash; über MQTT fehlen: %s",
"TEST.F_TEXTE": "Hat jedes Feld und jeder Befehl einen Text in dieser Sprache?",
"TEST.A_TEXTE_OK": "ja, alle %d",
"TEST.A_TEXTE_FEHL": "nein &mdash; ohne Text: %s. In der Tabelle stünde dann der Schlüsselname.",
"TEST.F_AUSWAHL": "Sind die Auswahlfelder als solche erkennbar?",
"TEST.A_AUSWAHL_KEINE": "diese Seite hat kein Auswahlfeld",
"TEST.A_AUSWAHL": "%d von %d Auswahlfeldern tragen das Merkmal, eigener Pfeil vorhanden: %s",
"TEST.F_MASKE": "Wird ein Text doppelt maskiert ausgegeben?",
"TEST.A_MASKE_OK": "nein, %d maskierte Texte geprüft",
"TEST.A_MASKE_FEHL": "ja &mdash; betroffen: %s. Im Browser stünde dort die Entität im Wortlaut.",
"TEST.F_STEUERUNG": "Sind schreibende Befehle zugelassen?",
"TEST.A_STEUERUNG_EIN": "ja",
"TEST.A_STEUERUNG_AUS": "nein &mdash; das ist die Vorgabe und damit richtig, solange nichts geschaltet werden soll",
"TEST.M_FAHRZEUG_UNGUELTIG": "Die Fahrzeugnummer ist keine Zahl.",
"TEST.M_TEMP_UNGUELTIG": "Die Zieltemperatur ist keine ganze oder halbe Zahl.",
"TEST.M_STUFE_UNGUELTIG": "Die Stufe ist keine Zahl.",
"TEST.M_UNBEKANNT": "Unbekannte Prüfung.",

# ---- Logdateien ------------------------------------------------------------
"LOG.H_TITEL": "Logdateien",
"LOG.ERKLAERUNG": "Neueste Zeile oben. Das Protokoll wird ab 500 kB auf die letzten 200 Zeilen gekappt, und dieselbe Meldung erscheint höchstens einmal je Stunde &mdash; sonst geht in einer Dauerstörung jede andere Zeile unter. <b>Es übersteht keinen Neustart:</b> der Ordner liegt auf einer Ramdisk. Wer eine Meldung aufheben will, kopiert sie vorher heraus.",
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
"BY_MQTT.TS": "Zeitstempel der letzten erfolgreichen Messung, in Unix-Sekunden. Daraus rechnet die Gegenseite das Alter &mdash; über MQTT ist das Alter beim Senden immer null.",
"BY_MQTT.FAHRZEUGE": "Anzahl der erkannten Fahrzeuge",
# ---- Vorklimatisierung am Abfahrtsassistenten ------------------------------
"EINST.H_ABFAHRT": "Vorklimatisierung am Abfahrtsassistenten",
"EINST.ABFAHRT_ERKLAERUNG": "<b>Ungeprüft.</b> Der Abfahrtsassistent sendet unter seinem Themenpfad die Minuten bis zur Abfahrt (<code>ABFAHRT_IN</code>) und einen Freigabewert (<code>OK</code>). Dieses Plugin <i>hört zu</i> und setzt den Klimabefehl ab, sobald der Vorlauf erreicht ist. Gemessen ist bisher nur, dass der Assistent diese beiden Themen führt &mdash; nicht, dass ein BYD-Fahrzeug den Klimabefehl annimmt. Erst ausschalten, bis der Trockenlauf im Reiter Test das Gegenteil zeigt.",
"EINST.L_ABFAHRT_EIN": "Vorklimatisierung einschalten",
"EINST.L_ABFAHRT_PRAEFIX": "Themenpfad des Abfahrtsassistenten",
"EINST.H_ABFAHRT_PRAEFIX": "Ohne Schrägstrich am Ende. Abonniert werden <code>&lt;Pfad&gt;/ABFAHRT_IN</code> und <code>&lt;Pfad&gt;/OK</code>. Leer heißt: es wird nichts abonniert und nichts geschaltet.",
"EINST.L_ABFAHRT_VORLAUF": "Vorlauf vor der Abfahrt (Minuten)",
"EINST.H_ABFAHRT_VORLAUF": "So viele Minuten vor der gemeldeten Abfahrt wird der Klimabefehl abgesetzt &mdash; und nur einmal je Abfahrt.",
"EINST.L_ABFAHRT_TEMP": "Zieltemperatur der Vorklimatisierung (°C)",
"EINST.L_ABFAHRT_FAHRZEUG": "Fahrzeug für die Vorklimatisierung",
"EINST.H_ABFAHRT_FAHRZEUG": "Die Nummer aus dem Reiter Test. Der Abfahrtsassistent kennt keine Fahrzeuge, also muss hier eine feste Wahl stehen.",
"EINST.L_ABFAHRT_ALTER": "Höchstalter der Abfahrtsmeldung (Sekunden)",
"EINST.H_ABFAHRT_ALTER": "Ältere Meldungen gelten als verfallen und lösen nichts aus. Ein stehengebliebener Wert im Broker würde sonst jeden Tag dieselbe Abfahrt behaupten.",
"EINST.FEHLER_ABFAHRT_TEMP": "Die Zieltemperatur der Vorklimatisierung (%d °C) liegt außerhalb der Grenzen für schreibende Befehle (%d bis %d °C).",
"EINST.FEHLER_THEMA": "%s: erlaubt sind Buchstaben, Ziffern, Bindestrich, Unterstrich und Schrägstrich &mdash; keine Platzhalter wie + oder #.",

# ---- Ladeempfehlung --------------------------------------------------------
"EINST.H_LADEEMPF": "Ladeempfehlung nach Strompreis",
"EINST.LADEEMPF_ERKLAERUNG": "Das Plugin hört einen vorhandenen Preiswert im Broker mit und sendet daraus das Feld <code>LADEEMPF</code> (1 = jetzt laden, 0 = nicht). Es <b>schaltet nichts</b>: die Empfehlung ist ein Wert für die Loxone-Logik, damit dort sichtbar bleibt, wer die Ladung auslöst. Der Preis muss von einer anderen Quelle kommen &mdash; BYD liefert keinen.",
"EINST.L_LADEEMPF_EIN": "Ladeempfehlung berechnen",
"EINST.L_LADEEMPF_THEMA": "MQTT-Thema mit dem Preis",
"EINST.H_LADEEMPF_THEMA": "Vollständiges Thema, so wie es im Broker steht, ohne Platzhalter. Ohne Thema wird nichts gerechnet und nichts gesendet.",
"EINST.L_LADEEMPF_GRENZE": "Grenzwert",
"EINST.H_LADEEMPF_GRENZE": "In derselben Einheit wie der Wert im Thema. Komma oder Punkt, beides wird verstanden.",
"EINST.L_LADEEMPF_UNTER": "Empfehlen, wenn der Wert UNTER dem Grenzwert liegt",
"EINST.H_LADEEMPF_UNTER": "Angehakt für Preise (billig = laden), abgehakt für Überschuss (viel = laden). Welche Richtung stimmt, entscheidet allein die Bedeutung des Themas &mdash; deshalb wird sie nicht geraten.",
"EINST.L_LADEEMPF_ALTER": "Höchstalter des Preiswertes (Sekunden)",
"EINST.H_LADEEMPF_ALTER": "Ist der letzte Preiswert älter, wird <code>LADEEMPF</code> auf 0 gesetzt. Eine Empfehlung, die verstummt, muss 0 sagen und nicht schweigen: ein fehlender Wert liest sich in Loxone wie der letzte gültige.",
"EINST.FEHLER_LADEEMPF_OHNE_THEMA": "Die Ladeempfehlung ist eingeschaltet, aber kein MQTT-Thema eingetragen. Sie würde nichts rechnen.",
"EINST.FEHLER_DEZIMAL": "%s: bitte eine Zahl eintragen, Komma oder Punkt als Trennzeichen.",

# ---- Gerechnete Groessen ---------------------------------------------------
"EINST.H_GERECHNET": "Gerechnete Größen",
"EINST.GERECHNET_ERKLAERUNG": "Diese Felder kommen nicht vom Fahrzeug, sondern werden hier gerechnet. Fehlt die Zutat, bleibt das Feld leer &mdash; es wird nie eine 0 gesendet, die wie eine Messung aussieht.",
"EINST.L_KAPAZITAET": "Nutzbare Batteriekapazität (kWh)",
"EINST.H_KAPAZITAET": "Aus dem Fahrzeugschein oder dem Datenblatt. Sie ist die Zutat für die geladene Energie und den Verbrauch; 0 heißt: beides bleibt leer. BYD liefert diesen Wert nicht mit.",
"EINST.L_HEIM_BREITE": "Heimatposition: Breite",
"EINST.L_HEIM_LAENGE": "Heimatposition: Länge",
"EINST.H_HEIM": "Dezimalgrad, wie in Loxone. Beide Werte oder keinen &mdash; aus einer halben Position lässt sich kein Abstand rechnen. Daraus entsteht das Feld <code>ZUHAUSE</code>.",
"EINST.L_HEIM_RADIUS": "Umkreis (Meter)",
"EINST.H_HEIM_RADIUS": "Innerhalb dieses Umkreises gilt das Fahrzeug als zuhause. Zu klein gewählt springt das Feld, weil auch ein stehendes Fahrzeug streuende Positionen meldet.",
"EINST.FEHLER_HEIM_HALB": "Die Heimatposition braucht Breite UND Länge. Mit nur einem Wert lässt sich kein Abstand rechnen; das Feld bleibt leer.",

# ---- Reiter Ladevorgaenge --------------------------------------------------
"REITER.LADUNGEN": "Ladevorgänge",
"LADUNG.H_TITEL": "Erkannte Ladevorgänge",
"LADUNG.ERKLAERUNG": "Ein Ladevorgang wird am Wechsel des Feldes <code>LAEDT</code> erkannt &mdash; nicht von BYD gemeldet. Die Liste steht in <code>verlauf/ladungen.csv</code> im Datenordner. Sie überlebt eine Aktualisierung des Plugins (der Installateur kopiert über den Datenordner, er räumt ihn nicht aus), aber <b>keine Deinstallation</b>: dabei wird <code>data/</code> entfernt. Wer sie darüber hinaus behalten will, sichert die Datei vorher.",
"LADUNG.LEER": "Noch kein Ladevorgang aufgezeichnet. Eingetragen wird erst, wenn der Dienst einen <i>Wechsel</i> von „lädt“ auf „lädt nicht“ gesehen hat &mdash; eine bereits laufende Ladung beim ersten Start zählt also nicht mit.",
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
"LADUNG.GENAUIGKEIT": "<b>Was diese Zahlen sind.</b> Beginn und Ende sind die Zeitpunkte der <i>Abrufe</i>, an denen der Wechsel auffiel &mdash; sie liegen bis zu einem Abrufabstand neben der Wirklichkeit. Die kWh sind aus der Änderung des Ladezustands und der eingetragenen Kapazität gerechnet, nicht gemessen: Ladeverluste stecken nicht darin, und ein falsch eingetragener Kapazitätswert verfälscht jede Zeile gleichmäßig.",

# ---- Trockenlauf -----------------------------------------------------------
"TEST.L_PROBE": "Trockenlauf: nur zeigen, was passieren würde",
"TEST.H_PROBE": "Angehakt geht der Befehl denselben Weg bis unmittelbar vor das Senden: die Wachen greifen, das Fahrzeug und die Bibliotheksfunktion werden gesucht, die Parameter werden geprüft &mdash; nur abgesetzt wird nichts. Die Antwort beginnt dann mit „PROBE“. Das ist der Weg, um die Feldzuordnung und die Befehlsnamen an einem echten Fahrzeug zu klären, ohne es zu bewegen.",

# ---- Pruefzeilen der neuen Funktionen --------------------------------------
"TEST.F_HORCHER": "Sind die fremden MQTT-Themen abonniert?",
"TEST.A_HORCHER_UNNOETIG": "keine Funktion braucht ein fremdes Thema &mdash; Vorklimatisierung und Ladeempfehlung sind aus",
"TEST.A_HORCHER_FEHLER": "nein, der Dienst meldet: %s",
"TEST.A_HORCHER_KEIN_DIENST": "der Dienst läuft nicht &mdash; %d Themen wären zu abonnieren, verglichen werden kann hier nichts",
"TEST.A_HORCHER_ABWEICHUNG": "nein. Nicht abonniert: %s. Zusätzlich abonniert: %s. Solange ein Thema fehlt, löst die zugehörige Funktion nie aus, und das sieht aus wie eine stille Gegenseite.",
"TEST.A_HORCHER_OK": "ja, %d Themen und der Broker ist verbunden: %s",
"TEST.A_HORCHER_GETRENNT": "die Themenliste stimmt, aber der Dienst ist nicht mit dem Broker verbunden. Läuft das MQTT-Gateway, und stimmen Benutzer und Passwort?",
"TEST.F_SELBSTBEZUG": "Hört das Plugin auf sich selbst?",
"TEST.A_SELBSTBEZUG_UNNOETIG": "es wird kein fremdes Thema abonniert",
"TEST.A_SELBSTBEZUG_OK": "nein, kein abonniertes Thema liegt unter dem eigenen Pfad (%s)",
"TEST.A_SELBSTBEZUG_FEHL": "ja: %s liegt unter dem eigenen Themenpfad %s. Das Plugin wäre sein eigener Zulieferer &mdash; die Ladeempfehlung rechnete mit ihrem eigenen Ergebnis, die Vorklimatisierung wartete auf eine Abfahrt, die niemand ankündigt.",
"TEST.F_ABFAHRT": "Kann die Vorklimatisierung schalten?",
"TEST.A_ABFAHRT_AUS": "sie ist ausgeschaltet",
"TEST.A_ABFAHRT_GESPERRT": "nein: sie ist eingeschaltet, aber schreibende Befehle sind gesperrt. Sie würde zur Abfahrtszeit nichts absetzen &mdash; eine eingeschaltete Funktion, die nichts tut, fällt niemandem auf.",
"TEST.A_ABFAHRT_TEMP": "nein: die Zieltemperatur %d °C liegt außerhalb der Grenzen %d bis %d °C, der Befehl würde abgewiesen",
"TEST.A_ABFAHRT_OK": "ja, %d Minuten vor der Abfahrt auf %d °C, Fahrzeug %d. Ob BYD den Befehl annimmt, zeigt erst der Trockenlauf.",
"TEST.F_ZUTATEN": "Sind die Zutaten der gerechneten Größen da?",
"TEST.A_ZUTATEN_HALB": "nein: die Heimatposition ist nur halb eingetragen. Aus einem einzelnen Wert lässt sich kein Abstand rechnen, das Feld ZUHAUSE bleibt leer &mdash; obwohl etwas eingetragen ist.",
"TEST.A_ZUTATEN_OK": "ja: %d kWh Kapazität und eine Heimatposition mit %d m Umkreis",
"TEST.A_ZUTATEN_OFFEN": "nicht vollständig, und das ist erlaubt. Es fehlt: %s. Die davon abhängigen Felder bleiben leer statt eine 0 zu senden.",
"TEST.Z_KAPAZITAET": "die Batteriekapazität (VERBRAUCH und LADEKWH bleiben leer)",
"TEST.Z_HEIM": "die Heimatposition (ZUHAUSE bleibt leer)",
"TEST.F_LADUNGEN": "Lässt sich die Liste der Ladevorgänge lesen?",
"TEST.A_LADUNGEN_KEINE": "es ist noch keine Datei angelegt &mdash; erst ein erkannter Wechsel von „lädt“ auf „lädt nicht“ schreibt die erste Zeile",
"TEST.A_LADUNGEN_OK": "ja, %d von %d Zeilen gelesen",
"TEST.A_LADUNGEN_UNLESBAR": "nein: die Datei hat %d Zeilen, aber keine davon ließ sich lesen. Der Reiter zeigte eine leere Liste und behauptete damit, es habe nie geladen.",
}

# ---------------------------------------------------------------------------
# Englisch
# ---------------------------------------------------------------------------
EN = {

"REITER.EINSTELLUNGEN": "Settings",
"REITER.LOXONE": "Loxone integration",
"REITER.TEST": "Test",
"REITER.LOG": "Log files",

"LEGENDE.LESEN": "View &mdash; reads only, changes nothing",
"LEGENDE.TECHNIK": "Technical information &mdash; for troubleshooting",
"LEGENDE.AKTION": "Triggers something &mdash; sends or changes",
"LEGENDE.AKTION_TOKEN": "Triggers something &mdash; a new token invalidates every address in the Miniserver",
"LEGENDE.AKTION_LOG": "Triggers something &mdash; the existing lines are gone afterwards",

"ALLG.BEANSTANDUNG": "Please correct the following:",
"ALLG.FEHLER_FORMTOKEN": "The form did not carry a valid marker for this session. Nothing was changed. Please reload the page and submit again. If no action token exists yet, it is created when this page is first opened &mdash; then a reload is enough.",
"ALLG.FEHLER_FORMULAR": "The form did not identify itself. Nothing was changed &mdash; guessing the wrong form would delete exactly what was meant to be kept.",
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
"EINST.H_DIENST": "Polling service",
"EINST.DIENST_ERKLAERUNG": "The service fetches the values at the configured interval and stores them in a cache. The web interface and the Miniserver only read that cache &mdash; which is why the endpoint answers in milliseconds rather than seconds.",
"EINST.K_START": "Start service",
"EINST.K_RESTART": "Restart service",
"EINST.K_STOP": "Stop service",
"EINST.DIENST_START": "The service was started.",
"EINST.DIENST_STOP": "The service was stopped.",
"EINST.DIENST_RESTART": "The service was restarted.",
"EINST.H_KONTO": "BYD account",
"EINST.KONTO_ERKLAERUNG": "These are the credentials of the BYD account from the BYD app, not those of a dealer portal. They are kept in a separate file with mode 0600 and are never displayed &mdash; only their length. Leaving the password field empty deletes nothing.",
"EINST.L_BENUTZER": "User name",
"EINST.H_BENUTZER": "The same name you use to sign in to the BYD app &mdash; an e-mail address or a phone number, depending on the account. Nothing is rewritten: what you type is what is sent.",
"EINST.L_PASSWORT": "Password",
"EINST.H_PASSWORT": "Leaving this empty keeps the stored password.",
"EINST.PW_GESETZT": "stored, %d characters",
"EINST.PW_LEER": "none stored yet",
"EINST.L_PIN": "Control PIN",
"EINST.H_PIN": "The PIN the BYD app uses to authorise write commands. Without it BYD rejects every command; it is not needed for reading. Four to eight digits.",
"EINST.PIN_GESETZT": "stored",
"EINST.PIN_LEER": "none stored yet",
"EINST.L_LAND": "Country code",
"EINST.H_LAND": "Two letters, e.g. DE or AT. Only needed if the library asks for it &mdash; whether it does is shown by the service self-test on the Test tab, in the line about the recognised configuration fields. Leave empty if unsure.",
"EINST.L_ZUGANG_LOESCHEN": "Delete user name, password and PIN completely",
"EINST.H_ZUGANG_LOESCHEN": "This also deletes the backup copy next to the configuration folder. Without this box it would remain and reappear on the next fresh install &mdash; a deletion that does not delete is worse than none.",
"EINST.H_TAKT": "Polling interval",
"EINST.TAKT_WARNUNG": "Every poll <b>wakes the car</b>: the interface asks the vehicle to report rather than reading a cloud cache. Too short an interval costs standby power and may hit a rate limit. The lower bound of 120 seconds is our own choice, not a figure from BYD.",
"EINST.L_INTERVALL": "Interval in seconds",
"EINST.H_INTERVALL": "120 to 3600. The default of 300 seconds matches the default of the ioBroker adapter for the same interface.",
"EINST.L_VERLAUF_TAGE": "Keep history (days)",
"EINST.H_VERLAUF_TAGE": "One small CSV file per day and vehicle in the data folder. Older ones are removed.",
"EINST.L_GPS_EIN": "Poll location as well",
"EINST.H_GPS_EIN": "The location is a separate request. If you do not need it, you save one call per cycle &mdash; and the position of the car never leaves it.",
"EINST.L_MQTT_BIBLIOTHEK": "Allow the library to use its own MQTT path",
"EINST.H_MQTT_BIBLIOTHEK": "This is <b>not</b> the LoxBerry MQTT gateway but BYD's own broker: the library uses it to await confirmation of a command instead of polling. Without this box a confirmation takes longer. The path to the Miniserver is unaffected.",
"EINST.H_STEUERUNG": "Write commands",
"EINST.STEUERUNG_ERKLAERUNG": "Disabled by default, on purpose: a default that switches something unasked on first run is a bug. With this box the Miniserver may lock and unlock, run the climate control, set seat and battery heating, make the car honk, flash the lights and close the windows. Whether BYD accepts a command is a different question &mdash; the receipt is not the effect.",
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
"EINST.VIN_HINWEIS": "The sequence number is sorted by VIN and therefore stable. In the Loxone addresses you may use the VIN instead of the number &mdash; that is the more durable choice.",
"EINST.GESPEICHERT": "The settings were saved.",
"EINST.FEHLER_ZAHL": "%s: please enter a whole number.",
"EINST.FEHLER_BEREICH": "%s: the value must be between %d and %d.",
"EINST.FEHLER_TEMP_TAUSCH": "The lowest target temperature is greater than the highest. Please swap them.",
"EINST.FEHLER_PIN": "The control PIN consists of four to eight digits.",
"EINST.FEHLER_LAND": "The country code consists of exactly two letters, e.g. DE.",
"EINST.FEHLER_ZUGANG_SPEICHERN": "The credentials could not be saved. Check the permissions of the configuration folder.",
"EINST.FEHLER_ZUGANG_LOESCHEN": "The credentials could not be deleted completely.",
"EINST.ZUGANG_GELOESCHT": "User name, password and PIN were deleted, and so was the backup copy.",
"EINST.WARN_PW_OHNE_KONTO": "A password is stored but no user name. Sign-in cannot succeed this way.",
"EINST.HINWEIS_PIN_FEHLT": "Write commands are enabled but no control PIN is stored. BYD will reject every command.",
"EINST.FEHLER_SPEICHERN": "The configuration could not be written (%s).",
"EINST.FEHLER_TOPIC": "The topic path may only contain letters, digits, hyphen, underscore and slash.",
"EINST.L_MQTT_EIN": "Send values over MQTT",
"EINST.L_MQTT_TOPIC": "Topic path",
"EINST.H_MQTT_TOPIC": "Prefix of every topic. Changing it later renames <b>every</b> topic on an existing installation &mdash; the virtual inputs in Loxone and the values in the broker depend on it.",

"MQTT.GATEWAY_ERKLAERUNG": "Since LoxBerry 3 the MQTT gateway is <b>part of the system</b>, not a plugin. It is not installed separately but switched on under <span class='sm-mono'>System &rarr; MQTT Gateway</span>.",
"MQTT.H_ZUSTAND": "State of the gateway",
"MQTT.NICHT_GEFUNDEN": "No MQTT section could be found in the LoxBerry <span class='sm-mono'>general.json</span>. Without it nothing can be forwarded.",
"MQTT.AUTOSTART_AUS": "The MQTT gateway is not set to autostart (<span class='sm-mono'>System &rarr; MQTT Gateway</span>). Messages are sent, but probably nobody is listening.",
"MQTT.AUTOSTART_EIN": "The gateway is set to autostart. It comes up by itself after a LoxBerry restart.",
"MQTT.T_AUTOSTART": "Gateway autostart",
"MQTT.T_BROKER": "Broker",
"MQTT.T_UDP": "UDP input of the gateway",
"MQTT.T_PLUGIN": "This plugin sends over MQTT",
"MQTT.H_ABO": "Add the subscription in the gateway",
"MQTT.ABO_WARNUNG": "<b>Without this entry nothing arrives at the Miniserver.</b> This is the single most common cause of failure.",
"MQTT.ABO_SCHRITTE": "In LoxBerry under <span class='sm-mono'>System &rarr; MQTT Gateway</span>, add exactly this line to the list of subscriptions and save:",
"MQTT.H_THEMEN": "Every topic this plugin publishes",
"MQTT.THEMEN_ERKLAERUNG": "This list is built from the same source as the status line of the endpoint. The MQTT path therefore carries the same values as the HTTP path &mdash; a plugin whose MQTT message contains less than its HTTP line makes migration impossible, and does so quietly: values do arrive, just not all of them. The Test tab verifies the match.",
"MQTT.T_THEMA": "Topic",
"MQTT.T_BEDEUTUNG": "Meaning",
"MQTT.PLATZHALTER": "<span class='sm-mono'>N</span> stands for the sequence number of the vehicle, starting at 1.",
"MQTT.UMBENENNUNG": "Over MQTT the <b>timestamp</b> is sent, not the age: at the moment of sending the age is always zero. The receiving side computes it. In Loxone: <span class='sm-mono'>age = (Loxone time + 1230768000) &minus; ts</span> &mdash; Loxone counts seconds since 1 January 2009.",

"LOX.H_TITEL": "Loxone integration",
"LOX.EINLEITUNG": "Two paths are available and they do not exclude each other. <b>MQTT</b> is the standard route: the gateway creates the virtual inputs itself, and in Loxone a suitably named input is enough. The <b>HTTP endpoint</b> is the route for anything Loxone should fetch itself &mdash; and the only one for write commands.",
"LOX.S1_TITEL": "Step 1: choose the path",
"LOX.S1_TEXT": "MQTT is preferable to HTTP polling: the gateway generates the input names itself, whereas the HTTP route needs a command recognition per value. If you only need a few values, or want to work without a broker, use the endpoint from step 3.",
"LOX.S2_TITEL": "Step 2: add the subscription in the MQTT gateway",
"LOX.S2_TEXT": "In LoxBerry under <span class='sm-mono'>System &rarr; MQTT Gateway</span> add this subscription:",
"LOX.S2_WARNUNG": "<b>Without this entry nothing arrives at the Miniserver.</b>",
"LOX.S3_TITEL": "Step 3: virtual inputs over HTTP",
"LOX.S3_TEXT": "One virtual HTTP input with this address fetches all values in a single call. One command recognition per value, using the search text from the table below.",
"LOX.S3_BEFEHLE": "<p>The title is for humans, the search text for the machine: the title may change without any existing installation noticing &mdash; what is searched for is still the text in the second column. The semicolon belongs <b>in the pattern</b>: Loxone searches literally and takes the first hit, and without the semicolon <span class='sm-mono'>KM=</span> would also occur inside a future <span class='sm-mono'>RESTKM=</span>.</p>",
"LOX.S3_STRICH": "A <b>dash</b> as a value means: this value is not available. No 0 is sent on purpose &mdash; a 0 would look like a measurement. Loxone then keeps the last valid value, and the ALTER field says how old it is.",
"LOX.S3_HERKUNFT": "The <b>Origin</b> column is meant seriously. <b>Documentation</b> means: the field name comes from an open source and was never measured against a car here. <b>Computed</b> means: the field does not come from the vehicle at all but arises here &mdash; if an ingredient is missing it stays empty. A field nobody measured must not look like one somebody did. The Test tab shows which fields the library actually matched on <b>your</b> vehicle.",
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
"LOX.ALLES_TEXT": "The two buttons produce ready-made import files for Loxone Config. Inputs are imported under <span class='sm-mono'>Virtual Inputs &rarr; Predefined HTTP devices &rarr; Import template…</span>, outputs under <span class='sm-mono'>Virtual Outputs &rarr; Predefined devices &rarr; Import template…</span> &mdash; note that the output button lacks the word HTTP.",
"LOX.K_VORLAGE": "Create template for Loxone Config",
"LOX.K_VORLAGE_VO": "Create template for the control commands",
"LOX.VORLAGE_ZWEIMAL": "Loxone Config <b>creates new objects on import and overwrites nothing</b>. Importing twice means duplicate blocks on the same address &mdash; and Config says nothing about it.",
"LOX.VORLAGE_HINWEIS": "Created by the LoxBerry plugin BYD Autos. Importing twice results in duplicate blocks.",
"LOX.VORLAGE_UNGEPRUEFT": "This vehicle has never answered - all fields are included. After the first successful poll, fetch the template again; it will then contain only the fields the car really delivers.",
"LOX.VORLAGE_VO_HINWEIS": "Control commands of the LoxBerry plugin BYD Autos. They only work if write commands are enabled on the Settings tab.",
"LOX.S4_TITEL": "Step 4: location",
"LOX.S4_TEXT": "The location is returned in a separate response so that the status line consists of whole numbers only. A latitude with a decimal point among integers would be a trap for a command recognition.",
"LOX.S5_TITEL": "Step 5: sending commands",
"LOX.S5_TEXT": "One virtual output per command. Use the host name of the LoxBerry as the address of the output and the path from the table as the command. A state belongs on <b>one</b> output with an on and an off command, not on two outputs &mdash; which is what the generated import file does.",
"LOX.S5_WARNUNG": "These addresses contain the token. If you create a new token you must update all of them &mdash; a virtual output does not evaluate the answer, so a failure would go unnoticed.",
"LOX.S5_KEIN_LADEN": "<b>Starting and stopping charging is not offered here.</b> The library used names no method for it. An output the manufacturer cannot serve is not offered at all: a block that only collects refusals is worse than none.",
"LOX.S6_TITEL": "Step 6: token and self-test",
"LOX.S6_TEXT": "The token protects the unauthenticated endpoint. The second address answers the question „is the token entered in Loxone still valid?“ <b>without triggering anything on the car</b> &mdash; no device contact, no write access. Without such a route there are only two bad options: either you really switch something, or you never find out.",
"LOX.T_TOKEN": "Token",
"LOX.T_SELBSTTEST": "Self-test (triggers nothing)",
"LOX.K_TOKEN_NEU": "Create a new token",
"LOX.TOKEN_NEU": "A new token was created. All previous addresses in the Miniserver are now invalid and must be updated.",
"LOX.S7_TITEL": "Step 7: failure detection",
"LOX.S7_TEXT": "<b>Virtual inputs keep their last value.</b> If the service fails, everything looks normal in the app. Two things are therefore wired up: <span class='sm-mono'>OK</span> (0 means this poll returned nothing) and <span class='sm-mono'>ALTER</span> (grows as long as nothing new arrives). Set the alarm threshold well above the polling interval so a single missed cycle raises nothing. And mind the special case: <span class='sm-mono'>ALTER = &minus;1</span> means „there has never been a successful poll“ &mdash; which looks fresher than any real value, so always evaluate OK as well.",
"LOX.S8_TITEL": "Step 8: complete block list for rebuilding",
"LOX.S8_TEXT": "Working through this table from top to bottom rebuilds the function without further thought. Loxone Config lists all blocks in the block search (F5). Optional rows are marked as such.",
"LOX.S8_ERLAEUTERUNG": "<p><b>On the AND and OR blocks:</b> in Loxone they have exactly two inputs. Where three conditions meet, two blocks are chained &mdash; a drawing with four inputs on an OR cannot be rebuilt.</p><p><b>On the notification block:</b> it only fires on a transition from off to on. Never wire several sources directly to its input &mdash; combine them with OR first, otherwise a permanently active source swallows all the others.</p><p><b>On Loxone time:</b> Loxone counts seconds since 1 January 2009. If a time block delivers Unix time (a value around 1.7 billion), subtract <span class='sm-mono'>1230768000</span>.</p>",
"LOX.T_BAUSTEIN": "Block (type)",
"LOX.T_NAMENSVORSCHLAG": "Name (suggestion)",
"LOX.T_PARAMETER": "Parameters",
"LOX.T_EINGAENGE": "Connect inputs to",
"LOX.S9_TITEL": "Step 9: cross-check",
"LOX.S9_TEXT": "Call these four addresses once in a browser. The fourth is the most important: only a <b>refusal</b> for an invented action makes the three successes meaningful.",
"LOX.T_PRUEFUNG": "Call",
"LOX.T_ERWARTUNG": "Expected answer",

"BAUSTEIN.T_VE": "Virtual input",
"BAUSTEIN.T_VA": "Virtual output command",
"BAUSTEIN.T_NICHT": "NOT",
"BAUSTEIN.T_ODER": "OR",
"BAUSTEIN.T_UND": "AND",
"BAUSTEIN.T_SWS": "Threshold switch",
"BAUSTEIN.T_EVZ": "Switch-on delay",
"BAUSTEIN.T_BENACHR": "Notification",
"BAUSTEIN.T_STATUS": "Status block",
"BAUSTEIN.T_WOCHE": "Weekly timer",
"BAUSTEIN.T_TASTER": "Push button (flag)",
"BAUSTEIN.N_NICHT": "BYD poll failed",
"BAUSTEIN.N_ALT": "BYD values too old",
"BAUSTEIN.P_ALT": "on above 900, off below 700",
"BAUSTEIN.N_STOER": "BYD fault",
"BAUSTEIN.N_EVZ": "BYD fault persists",
"BAUSTEIN.P_EVZ": "delay 600 s",
"BAUSTEIN.N_MELD1": "BYD notify fault",
"BAUSTEIN.P_MELD": "text of your choice",
"BAUSTEIN.N_SOC": "BYD battery low",
"BAUSTEIN.P_SOC": "on below 20, off above 30",
"BAUSTEIN.N_MELD2": "BYD notify battery",
"BAUSTEIN.N_OFFEN": "BYD driver door unlocked",
"BAUSTEIN.P_OFFEN": "on below 1, off above 1 &mdash; the value is device specific, read it off the car first",
"BAUSTEIN.N_UND": "BYD unlocked and nobody home",
"BAUSTEIN.N_MELD3": "BYD notify unlocked",
"BAUSTEIN.N_STATUS": "BYD charge state as text",
"BAUSTEIN.P_STATUS": "0 not connected, 1 charging, 15 plug connected",
"BAUSTEIN.N_WOCHE": "BYD pre-conditioning",
"BAUSTEIN.P_WOCHE": "departure times per weekday",
"BAUSTEIN.N_TASTER": "BYD climate now",
"BAUSTEIN.P_TASTER": "from the visualisation",
"BAUSTEIN.N_ODER2": "BYD trigger climate",
"BAUSTEIN.N_VA_KLIMA": "BYD climate",
"BAUSTEIN.P_VA_KLIMA": "on and off command from the import file",
"BAUSTEIN.N_VA_VERR": "BYD lock",
"BAUSTEIN.P_VA_VERR": "on locks, off unlocks",
"BAUSTEIN.N_VA_ABRUF": "BYD poll now",
"BAUSTEIN.P_VA_ABRUF": "on command only",
"BAUSTEIN.ANWESEND": "presence (inverted)",
"BAUSTEIN.MANUELL": "from the visualisation",

"TEST.H_SELBSTPRUEFUNG": "Self-check",
"TEST.EINLEITUNG": "These checks answer <b>without Loxone and without a BYD account</b> whether the setup will work. Anything that could only be checked with an actual car is named as such at the end of the page.",
"TEST.BILANZ": "%d of %d checks passed, plus %d notes.",
"TEST.T_FRAGE": "Question",
"TEST.T_BEFUND": "Finding",
"TEST.LEGENDE_PUNKT": "A grey dot is a <b>note</b>: the line does not apply here, or cannot be measured in this setup. It deliberately does not count as passed &mdash; a summary must not look better than its worst item.",
"TEST.H_LESEN": "View",
"TEST.K_STATUS": "Call the status line",
"TEST.K_POSITION": "Call the location",
"TEST.K_FAHRZEUGE": "Call the vehicle list",
"TEST.K_SELFTEST": "Endpoint self-test",
"TEST.H_TECHNIK": "Technical information",
"TEST.K_SELBSTTEST": "Service self-test",
"TEST.K_ENDPUNKT": "Measure the endpoint now",
"TEST.K_FELDER": "Suggest field mapping",
"TEST.K_JSON": "View raw data as JSON",
"TEST.H_FELDER_ERKLAERUNG": "<b>Suggest field mapping</b> queries the vehicle and lists <b>every leaf of the response with its path</b> &mdash; together with the field that matched it. That way the device answers the question about the names, not a guess. The call needs credentials and network access and takes a few seconds.",
"TEST.H_SCHALTEN": "Switching",
"TEST.SCHALTEN_WARNUNG": "<b>These buttons act on the car immediately.</b> They are not a dry run. Whether BYD accepts a command is stated in the answer; whether the car carries it out is only shown by the next poll.",
"TEST.SCHALTEN_GESPERRT": "Write commands are disabled. The buttons will be refused until the box on the Settings tab is ticked.",
"TEST.L_FAHRZEUG": "Vehicle",
"TEST.H_FAHRZEUG": "The sequence number from the vehicle list.",
"TEST.L_TEMP": "Target temperature in degrees Celsius",
"TEST.H_TEMP": "Whole or half degrees. Values outside the configured limits are refused.",
"TEST.L_MINUTEN": "Duration in minutes (optional)",
"TEST.H_MINUTEN": "Only effective if the installed library knows a parameter for it. If it does not, the answer says so explicitly &mdash; a value that does not arrive is named rather than quietly dropped.",
"TEST.L_STUFE": "Level for seat and battery heating",
"TEST.H_STUFE": "Which levels this vehicle supports is undocumented. 0 switches off.",
"TEST.K_ABRUF": "Poll now",
"TEST.H_UNGEPRUEFT": "What cannot be checked here",
"TEST.UNGEPRUEFT": "Whether sign-in to the BYD interface succeeds, whether the field names in this table apply to this vehicle, and whether the write commands have the expected effect on the car &mdash; that is decided by the account and the car, not here. The field names come from open sources and were never measured against a car here.",
"TEST.UNBEKANNT": "Result unknown:",
"TEST.KEINE_MESSPUNKTE": "no data points for today",
"TEST.F_ENDPUNKT": "Does our own endpoint answer over HTTP?",
"TEST.A_ENDPUNKT_UNKLAR": "cannot be determined &mdash; neither curl nor allow_url_fopen is available here, or the web server cannot call itself while rendering this page. This says nothing about the endpoint.",
"TEST.A_ENDPUNKT_OK": "yes, HTTP 200 with the expected marker (measurement %d s old)",
"TEST.A_ENDPUNKT_FEHL": "no: HTTP %d, answer: %s",
"TEST.A_LEER": "empty",
"TEST.F_VENV": "Does the Python virtual environment exist?",
"TEST.A_VENV_FEHLT": "no &mdash; reinstall the plugin, the installation creates it",
"TEST.F_PYTHON": "Is Python new enough (3.11 or newer)?",
"TEST.A_PYTHON_ZU_ALT": "too old for pybyd",
"TEST.A_PYTHON_UNBEKANNT": "cannot be determined",
"TEST.F_LIB": "Can the library be loaded, and in which version?",
"TEST.A_LIB_FEHLT": "no &mdash; without pybyd the service cannot work",
"TEST.F_DIENST": "Is the polling service running?",
"TEST.A_DIENST_LAEUFT": "yes, process id",
"TEST.A_DIENST_SOLL_TOT": "no &mdash; it should be running but is not. The reason is in the Log files tab.",
"TEST.A_DIENST_GESTOPPT": "no, deliberately stopped",
"TEST.F_KONTO": "Is a user name stored?",
"TEST.A_KONTO_FEHLT": "no &mdash; see the Settings tab",
"TEST.F_PASSWORT": "Is a password stored?",
"TEST.A_PASSWORT_DA": "yes, %d characters (the content is never displayed)",
"TEST.A_PASSWORT_FEHLT": "no &mdash; see the Settings tab",
"TEST.F_PIN": "Is the control PIN stored?",
"TEST.A_PIN_DA": "yes, %d digits",
"TEST.A_PIN_FEHLT": "no &mdash; BYD will reject every write command",
"TEST.A_PIN_UNNOETIG": "not needed for reading. It is only required once write commands are enabled.",
"TEST.F_RECHTE": "Is the credentials file protected from other users?",
"TEST.A_ZUGANGSDATEI_FEHLT": "the credentials file is missing",
"TEST.F_SICHERUNG": "Is there a backup copy of the configuration?",
"TEST.A_SICHERUNG_FEHLT": "none yet. It is created on the first save and lives <b>next to</b> the configuration folder &mdash; inside it, it would be deleted along with the folder on update.",
"TEST.F_FAHRZEUGE": "Have vehicles been detected?",
"TEST.A_FAHRZEUGE": "yes, %d",
"TEST.A_KEINE_FAHRZEUGE": "no &mdash; that is normal until the first successful poll",
"TEST.F_ZUORDNUNG": "Were the fields found in the response?",
"TEST.A_ZUORDNUNG_LEER": "no statement possible: there is no vehicle in the cache. A check over an empty set is not a tick.",
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
"TEST.A_MQTT_UNBENUTZT": "this plugin does not send over MQTT &mdash; the state of the gateway is then irrelevant",
"TEST.A_MQTT_NICHT_GEFUNDEN": "no MQTT section can be found in general.json",
"TEST.A_MQTT_AUS": "the gateway is not set to autostart. Without it nothing arrives at the Miniserver.",
"TEST.F_VORGABEN": "Do service and web interface use the same defaults?",
"TEST.A_VORGABEN_UNKLAR": "the list in the service could not be read &mdash; the comparison was not made",
"TEST.A_VORGABEN_OK": "yes, all %d defaults of the service also appear in the web interface",
"TEST.A_VORGABEN_FEHLT": "no &mdash; only in the service: %s",
"TEST.F_REITER": "Do the tab list, the tab bar and the panes agree?",
"TEST.A_REITER_UNKLAR": "the list could not be read &mdash; the comparison was not made",
"TEST.A_REITER_OK": "yes, all three places carry the same %d names",
"TEST.A_REITER_FEHL": "no: list %d, bar %d, panes %d. If a name is missing from the list, the page jumps back after every submit.",
"TEST.F_MUSTER": "Is every search text in the status line unambiguous?",
"TEST.A_MUSTER_OK": "yes, all %d search texts occur exactly once",
"TEST.A_MUSTER_FEHL": "no &mdash; ambiguous: %s. Loxone takes the first hit and would deliver the value of another field.",
"TEST.F_WEGE": "Does the MQTT path carry the same values as the HTTP path?",
"TEST.A_WEGE_OK": "yes: %d values in the status line, %d topics per vehicle",
"TEST.A_WEGE_FEHL": "no &mdash; missing over MQTT: %s",
"TEST.F_TEXTE": "Does every field and every command have a text in this language?",
"TEST.A_TEXTE_OK": "yes, all %d",
"TEST.A_TEXTE_FEHL": "no &mdash; without text: %s. The table would then show the key name.",
"TEST.F_AUSWAHL": "Are the select fields recognisable as such?",
"TEST.A_AUSWAHL_KEINE": "this page has no select field",
"TEST.A_AUSWAHL": "%d of %d select fields carry the marker, own arrow present: %s",
"TEST.F_MASKE": "Is any text escaped twice?",
"TEST.A_MASKE_OK": "no, %d escaped texts checked",
"TEST.A_MASKE_FEHL": "yes &mdash; affected: %s. The browser would show the entity verbatim.",
"TEST.F_STEUERUNG": "Are write commands enabled?",
"TEST.A_STEUERUNG_EIN": "yes",
"TEST.A_STEUERUNG_AUS": "no &mdash; that is the default and thus correct as long as nothing is to be switched",
"TEST.M_FAHRZEUG_UNGUELTIG": "The vehicle number is not a number.",
"TEST.M_TEMP_UNGUELTIG": "The target temperature is not a whole or half number.",
"TEST.M_STUFE_UNGUELTIG": "The level is not a number.",
"TEST.M_UNBEKANNT": "Unknown check.",

"LOG.H_TITEL": "Log files",
"LOG.ERKLAERUNG": "Newest line first. The log is truncated to the last 200 lines above 500 kB, and the same message appears at most once per hour &mdash; otherwise a persistent fault drowns out every other line. <b>It does not survive a reboot:</b> the folder is a ramdisk. Copy out anything you want to keep.",
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
"BY_MQTT.TS": "Timestamp of the last successful measurement, in Unix seconds. The receiving side computes the age from it &mdash; over MQTT the age is always zero at the moment of sending.",
"BY_MQTT.FAHRZEUGE": "Number of detected vehicles",
# ---- Pre-conditioning driven by the departure assistant --------------------
"EINST.H_ABFAHRT": "Pre-conditioning via the departure assistant",
"EINST.ABFAHRT_ERKLAERUNG": "<b>Unverified.</b> The departure assistant publishes the minutes until departure (<code>ABFAHRT_IN</code>) and a release value (<code>OK</code>) below its topic path. This plugin <i>listens</i> and issues the climate command once the lead time is reached. All that has been measured so far is that the assistant carries these two topics &mdash; not that a BYD vehicle accepts the climate command. Leave this off until the dry run on the Test tab shows otherwise.",
"EINST.L_ABFAHRT_EIN": "Enable pre-conditioning",
"EINST.L_ABFAHRT_PRAEFIX": "Topic path of the departure assistant",
"EINST.H_ABFAHRT_PRAEFIX": "Without a trailing slash. Subscribed are <code>&lt;path&gt;/ABFAHRT_IN</code> and <code>&lt;path&gt;/OK</code>. Empty means: nothing is subscribed and nothing is switched.",
"EINST.L_ABFAHRT_VORLAUF": "Lead time before departure (minutes)",
"EINST.H_ABFAHRT_VORLAUF": "This many minutes before the announced departure the climate command is issued &mdash; once per departure, not repeatedly.",
"EINST.L_ABFAHRT_TEMP": "Target temperature for pre-conditioning (°C)",
"EINST.L_ABFAHRT_FAHRZEUG": "Vehicle used for pre-conditioning",
"EINST.H_ABFAHRT_FAHRZEUG": "The number from the Test tab. The departure assistant knows nothing about vehicles, so a fixed choice has to be made here.",
"EINST.L_ABFAHRT_ALTER": "Maximum age of the departure message (seconds)",
"EINST.H_ABFAHRT_ALTER": "Older messages count as expired and trigger nothing. A stale value left in the broker would otherwise claim the same departure every day.",
"EINST.FEHLER_ABFAHRT_TEMP": "The pre-conditioning target temperature (%d °C) is outside the limits for writing commands (%d to %d °C).",
"EINST.FEHLER_THEMA": "%s: letters, digits, hyphen, underscore and slash are allowed &mdash; no wildcards such as + or #.",

# ---- Charging recommendation ----------------------------------------------
"EINST.H_LADEEMPF": "Charging recommendation based on price",
"EINST.LADEEMPF_ERKLAERUNG": "The plugin listens to an existing price value in the broker and derives the field <code>LADEEMPF</code> from it (1 = charge now, 0 = do not). It <b>switches nothing</b>: the recommendation is a value for the Loxone logic, so that it stays visible there who triggers the charge. The price must come from another source &mdash; BYD supplies none.",
"EINST.L_LADEEMPF_EIN": "Compute the charging recommendation",
"EINST.L_LADEEMPF_THEMA": "MQTT topic carrying the price",
"EINST.H_LADEEMPF_THEMA": "The complete topic as it appears in the broker, without wildcards. Without a topic nothing is computed and nothing is sent.",
"EINST.L_LADEEMPF_GRENZE": "Threshold",
"EINST.H_LADEEMPF_GRENZE": "In the same unit as the value in the topic. Comma or dot, both are understood.",
"EINST.L_LADEEMPF_UNTER": "Recommend when the value is BELOW the threshold",
"EINST.H_LADEEMPF_UNTER": "Ticked for prices (cheap = charge), unticked for surplus (plenty = charge). Which direction is right depends solely on what the topic means &mdash; which is why it is not guessed.",
"EINST.L_LADEEMPF_ALTER": "Maximum age of the price value (seconds)",
"EINST.H_LADEEMPF_ALTER": "If the last price value is older, <code>LADEEMPF</code> is set to 0. A recommendation that falls silent must say 0 rather than say nothing: in Loxone a missing value reads like the last valid one.",
"EINST.FEHLER_LADEEMPF_OHNE_THEMA": "The charging recommendation is enabled but no MQTT topic is set. It would compute nothing.",
"EINST.FEHLER_DEZIMAL": "%s: please enter a number, using a comma or a dot as the separator.",

# ---- Computed values ------------------------------------------------------
"EINST.H_GERECHNET": "Computed values",
"EINST.GERECHNET_ERKLAERUNG": "These fields do not come from the vehicle, they are computed here. If an ingredient is missing the field stays empty &mdash; a 0 that looks like a measurement is never sent.",
"EINST.L_KAPAZITAET": "Usable battery capacity (kWh)",
"EINST.H_KAPAZITAET": "From the registration document or the data sheet. It is the ingredient for charged energy and for consumption; 0 means both stay empty. BYD does not supply this value.",
"EINST.L_HEIM_BREITE": "Home position: latitude",
"EINST.L_HEIM_LAENGE": "Home position: longitude",
"EINST.H_HEIM": "Decimal degrees, as in Loxone. Both values or none &mdash; no distance can be computed from half a position. This produces the field <code>ZUHAUSE</code>.",
"EINST.L_HEIM_RADIUS": "Radius (metres)",
"EINST.H_HEIM_RADIUS": "Within this radius the vehicle counts as being at home. Chosen too small the field flickers, because even a parked vehicle reports scattered positions.",
"EINST.FEHLER_HEIM_HALB": "The home position needs latitude AND longitude. With only one value no distance can be computed; the field stays empty.",

# ---- Charging sessions tab ------------------------------------------------
"REITER.LADUNGEN": "Charging sessions",
"LADUNG.H_TITEL": "Detected charging sessions",
"LADUNG.ERKLAERUNG": "A charging session is detected from a change of the field <code>LAEDT</code> &mdash; BYD does not report it. The list lives in <code>verlauf/ladungen.csv</code> in the data folder. It survives an update of the plugin (the installer copies over the data folder, it does not clear it), but <b>not an uninstall</b>: that removes <code>data/</code>. Save the file beforehand if you want to keep it past that.",
"LADUNG.LEER": "No charging session recorded yet. An entry is only made once the service has seen a <i>change</i> from „charging“ to „not charging“ &mdash; a session already running at the first start therefore does not count.",
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
"LADUNG.GENAUIGKEIT": "<b>What these numbers are.</b> Start and end are the moments of the <i>polls</i> at which the change was noticed &mdash; they may be off by up to one polling interval. The kWh are computed from the change in state of charge and the capacity on file, not measured: charging losses are not in them, and a wrongly entered capacity distorts every row by the same factor.",

# ---- Dry run --------------------------------------------------------------
"TEST.L_PROBE": "Dry run: only show what would happen",
"TEST.H_PROBE": "When ticked the command takes the same path up to immediately before sending: the guards apply, the vehicle and the library function are looked up, the parameters are checked &mdash; only nothing is dispatched. The answer then starts with „PROBE“. This is the way to settle the field mapping and the command names on a real vehicle without moving it.",

# ---- Check rows of the new functions ---------------------------------------
"TEST.F_HORCHER": "Are the foreign MQTT topics subscribed?",
"TEST.A_HORCHER_UNNOETIG": "no function needs a foreign topic &mdash; pre-conditioning and charging recommendation are off",
"TEST.A_HORCHER_FEHLER": "no, the service reports: %s",
"TEST.A_HORCHER_KEIN_DIENST": "the service is not running &mdash; %d topics would have to be subscribed, nothing can be compared here",
"TEST.A_HORCHER_ABWEICHUNG": "no. Not subscribed: %s. Subscribed in addition: %s. As long as a topic is missing the corresponding function never triggers, and that looks like a silent counterpart.",
"TEST.A_HORCHER_OK": "yes, %d topics and the broker is connected: %s",
"TEST.A_HORCHER_GETRENNT": "the topic list agrees, but the service is not connected to the broker. Is the MQTT gateway running, and are user and password correct?",
"TEST.F_SELBSTBEZUG": "Does the plugin listen to itself?",
"TEST.A_SELBSTBEZUG_UNNOETIG": "no foreign topic is subscribed",
"TEST.A_SELBSTBEZUG_OK": "no, no subscribed topic lies below its own path (%s)",
"TEST.A_SELBSTBEZUG_FEHL": "yes: %s lies below the plugin's own topic path %s. The plugin would be its own supplier &mdash; the charging recommendation would compute from its own result, the pre-conditioning would wait for a departure nobody announces.",
"TEST.F_ABFAHRT": "Can the pre-conditioning switch at all?",
"TEST.A_ABFAHRT_AUS": "it is switched off",
"TEST.A_ABFAHRT_GESPERRT": "no: it is enabled, but writing commands are blocked. It would dispatch nothing at departure time &mdash; an enabled function that does nothing goes unnoticed.",
"TEST.A_ABFAHRT_TEMP": "no: the target temperature %d °C is outside the limits %d to %d °C, the command would be rejected",
"TEST.A_ABFAHRT_OK": "yes, %d minutes before departure to %d °C, vehicle %d. Whether BYD accepts the command is shown only by the dry run.",
"TEST.F_ZUTATEN": "Are the ingredients of the computed values present?",
"TEST.A_ZUTATEN_HALB": "no: the home position is only half filled in. No distance can be computed from a single value, the field ZUHAUSE stays empty &mdash; even though something is entered.",
"TEST.A_ZUTATEN_OK": "yes: %d kWh capacity and a home position with a %d m radius",
"TEST.A_ZUTATEN_OFFEN": "not complete, and that is allowed. Missing: %s. The fields depending on it stay empty instead of sending a 0.",
"TEST.Z_KAPAZITAET": "the battery capacity (VERBRAUCH and LADEKWH stay empty)",
"TEST.Z_HEIM": "the home position (ZUHAUSE stays empty)",
"TEST.F_LADUNGEN": "Can the list of charging sessions be read?",
"TEST.A_LADUNGEN_KEINE": "no file has been created yet &mdash; only a detected change from „charging“ to „not charging“ writes the first row",
"TEST.A_LADUNGEN_OK": "yes, %d of %d rows read",
"TEST.A_LADUNGEN_UNLESBAR": "no: the file has %d rows, but not one of them could be read. The tab would show an empty list and thereby claim that charging never happened.",
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
               "LADUNG", "TEST", "LOG", "BY_FELD", "BY_BEF", "BY_MQTT"]

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
}


def php_dateien(wurzel: Path):
    return sorted(wurzel.rglob("*.php"))


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
    return treffer | ZUR_LAUFZEIT


def ini_schreiben(pfad: Path, kopf: str, texte: dict) -> None:
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
            zeilen.append('%s = "%s"' % (s, abschnitte[a][s]))
    pfad.parent.mkdir(parents=True, exist_ok=True)
    # Absichtlich im Textmodus: unter Windows entstehen dabei CRLF, und das ist
    # der Stil, den die Sprachdateien dieser Reihe fuehren. Nach dem Schreiben
    # wird der Stil gegen die zuletzt veroeffentlichte Fassung gemessen
    # (Werkzeuge/zeilenenden_vergleichen.py) - eine Regel nach Dateiendung
    # waere geraten, nicht gemessen.
    pfad.write_text("\n".join(zeilen) + "\n", encoding="utf-8")


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
    ini_schreiben(wurzel / "templates/lang/language_de.ini", KOPF_DE, DE)
    ini_schreiben(wurzel / "templates/lang/language_en.ini", KOPF_EN, EN)
    print("Geschrieben: templates/lang/language_de.ini und language_en.ini")
    return 0


if __name__ == "__main__":
    sys.exit(main())
