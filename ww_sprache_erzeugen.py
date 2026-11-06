#!/usr/bin/env python3
"""Erzeugt die Sprachdateien des Weissware-Plugins.

Seit der Sprachausgabe Stufe 2 (Weissware 0.9.39, Nr. 36 b): der linieneigene Abschnitt
heisst [WW_ANSAGE]; den Abschnitt [ANSAGE] schreibt dieser Erzeuger NICHT aus seiner
Tabelle, sondern holt ihn bei jedem Lauf aus Werkzeuge/gemeinsam_pruefen.py
(ini_abschnitt(), Quelle gemeinsam/sprachausgabe_texte.json) - eine Quelle fuer alle
Linien mit der gemeinsamen Sprachausgabe.

Warum erzeugt und nicht von Hand gepflegt: Beim Anker-SOLIX-Plugin sind so
zwei Fehlerklassen aufgefallen, die beim Handpflegen unsichtbar bleiben.

1. Doppelte Maskierung. Ein Text, der durch ww_e() laeuft und selbst eine
   HTML-Entitaet enthaelt, erscheint als "pr&amp;uuml;fen" auf dem Bildschirm.
   Dieses Skript kennt aus dem PHP, welche Schluessel maskiert ausgegeben
   werden, und laesst dort keine Auszeichnung und keine Entitaet zu.
2. Abgeschnittene Werte. Bei parse_ini_file beginnt mit ';' ein Kommentar.
   Jeder Wert steht deshalb in doppelten Anfuehrungszeichen, und im Wert darf
   kein weiteres doppeltes Anfuehrungszeichen stehen (HTML-Attribute einfach
   quoten).

STAND (vb_x10_ww, 09.10.2026, Welle X-10 / Sprachmodul 1.1.2): WW_ANSAGE.ART_HINWEIS und
WW_ANSAGE.O_AUS entfallen - die Werksart-Saetze bringt Modul 1.1.2 ueber den Kontext
'werk' => 'musicserver' selbst mit (ART_HINWEIS_WERK, O_AUS_SCHLICHT, O_WERK in [ANSAGE]).
[ANSAGE] wie immer aus gemeinsam_pruefen.ini_abschnitt() (157 Schluessel).

STAND (vb_bild_ww16, 17.10.2026, Welle Bild 16 / Musterprojekt, Vollausstattung): Reiter "Einbindung in
Loxone" auf drei Seiten aus dem Musterprojekt (Entwurf Welle 16 ww, E10/E12): die alte Liste [BAUSTEIN]
(80 Schluessel) und LOX.S8_ERLAEUTERUNG entfallen, [WW_NAME] (24) entfaellt mit E11 (Befehlstitel fest
deutsch in ww_titel()); neu 118 BAUSTEIN.* (Kasten- und Hinweistitel, Kaesten, Hinweise, 82 Tabellenzeilen
Z1_01..Z3_20), 7 LOX.* (Bild, Link, Vorlage "Weissware Dienst" E4, Kommentare VA_START/VA_STOP E3) und
5 WW_DFELD.* (Kommentare der Dienst-Werte); neu gefasst LOX.EINLEITUNG, S1_TEXT (B8), S5_TEXT (E3),
S7_TEXT (B5), S8_TITEL, S8_TEXT.

STAND (vb_g1_tz_ww, 18.10.2026, Gruppe 1 / Textnachzug): BAUSTEIN.Z2_10 (Seite "Weissware PV-Start" #10) neu
gefasst - Typ Virtueller Eingang (Gateway-Name), Name spot_awattar_rank (Spotpreis aWATTar liefert die Werte jetzt ueber
MQTT); dazu Kasten/Hinweise S2_SCHRITT3 mit den neuen
Namen und der Herkunft der Vorlage (ab Spotpreis aWATTar 1.2.38). Sonst unveraendert.

STAND (Erzeuger-Nachzug 01.11.2026): erzeugt Weissware 0.9.45 byteweise gleich. Grundlage
vb_g44_ww_bau_skripte/ww_sprache_erzeugen_nf.py (Gruppe 44: WW_MQTT.ZAEHLER/AUTO_WARTET/AUTO_GRUND,
LOX.VORLAGEN_MQTT, E6 gestrichen; Mehrfachziele Los C: EINST.SICH_SPAET; Nachfassung nf2:
EINST.ERNEUERUNG_SCHEITERT/HC_ERSETZT). Inhalt war damit schon gleich; nachgezogen ist die
Reihenfolge (Abschnittsfolge und NACHGESTELLT), damit ein Neubau die .ini nicht umsortiert.

STAND (Drift-Abgleich, 06.11.2026): angeglichen an Weissware 0.9.51, 0 Schluessel neu, 2 Werte
geaendert (WW_ANSAGE.H_EIN de und en "Vorgabe: an"; BAUSTEIN.S1_H8 nur de "ab Werk an"), 0
entfernt. Neu UNBENUTZT_IN_DER_AUSLIEFERUNG: WW_ANSAGE.FEHLER_ZEIT, H_RUHE, L_RUHE_BIS,
L_RUHE_VON stehen in der .ini, werden im Plugin aber nirgends benutzt (Befund am Plugin).

Aufruf:  ww_sprache_erzeugen.py <pluginordner> [--pruefen]
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gemeinsam_pruefen  # noqa: E402  (Werkzeuge/gemeinsam_pruefen.py: Abschnitt [ANSAGE])

# ---------------------------------------------------------------------------
# Deutsch
# ---------------------------------------------------------------------------
DE = {

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
"ALLG.BEANSTANDUNG": "Es wurde nichts gespeichert. Bitte diese Punkte berichtigen:",
"ALLG.MISSLUNGEN": "Der Vorgang ist nicht gelungen:",
"ALLG.DIENST": "Abrufdienst",
"ALLG.LAEUFT": "läuft",
"ALLG.GESTOPPT": "gestoppt",
"ALLG.KEINE_PID": "keine Prozessnummer",
"ALLG.LETZTER_ABRUF": "Letzter Abruf",
"ALLG.NIE": "noch nie",
"ALLG.KACHEL_MQTT_HILFE": "Veröffentlichung dieses Plugins; Autostart des Gateways: %s",
"ALLG.NICHT_FESTSTELLBAR": "nicht feststellbar",
"ALLG.EIN": "ein",
"ALLG.AUS": "aus",
"ALLG.JA": "ja",
"ALLG.NEIN": "nein",
"ALLG.OHNE_NAMEN": "ohne Namen",
"ALLG.LETZTE_STOERUNG": "Letzte Störung:",
"ALLG.AUSFAELLE": "Anbieter, die nicht geantwortet haben:",
"ALLG.EIGENSCHAFT": "Eigenschaft",
"ALLG.WERT": "Wert",
"ALLG.SEKUNDEN": "Sekunden",
"ALLG.SPEICHERN": "Speichern",

# ---- Einstellungen ---------------------------------------------------------
# Kopf wie alle Hausplugins (Entscheidung Nr. 43, 0.9.40): gruener Kasten oben im
# Reiter Einstellungen, roh ausgegeben (ww_t ohne ww_e).
"EINST.WAS_IST_DAS": "<b>Bindet vernetzte Hausgeräte dreier Ökosysteme an Loxone an und bringt sie auf ein gemeinsames Modell</b> – Home Connect (Bosch, Siemens, Neff, Gaggenau, Constructa), Miele und Samsung SmartThings. Ein Abrufdienst auf dem LoxBerry holt die Werte im eingestellten Takt aus den Clouds der Anbieter und legt sie ab; der Miniserver liest sie über MQTT oder den HTTP-Endpunkt des Plugins. Schreibende Befehle an die Geräte sind ab Werk gesperrt. Auf Wunsch sagt das Plugin über die gemeinsame Sprachausgabe an, wenn ein Gerät fertig ist (ab Werk aus).",
"EINST.H_DIENST": "Abrufdienst",
"EINST.DIENST_ERKLAERUNG": "Der Dienst holt die Werte im eingestellten Takt bei den eingeschalteten Anbietern und legt sie ab. Oberfläche und Miniserver lesen nur das Abgelegte — sie sprechen nie selbst mit dem Anbieter.",
"EINST.K_START": "Dienst starten",
"EINST.K_NEUSTART": "Dienst neu starten",
"EINST.K_STOPP": "Dienst anhalten",
"EINST.K_SITZUNG": "Anmeldung neu erzwingen",
"EINST.DIENST_START": "Dienst gestartet:",
"EINST.DIENST_STOP": "Dienst angehalten:",
"EINST.DIENST_RESTART": "Dienst neu gestartet:",
"EINST.SITZUNG_VERWORFEN": "Die Anmeldemarken von Home Connect und Miele wurden gelöscht. Der Dienst meldet sich NICHT von selbst neu an: melden Sie sich unten im Abschnitt „Anmeldung“ neu an – Home Connect über den Code im Browser (Device Flow), Miele über die Anmeldeadresse und den Code aus der Adresszeile. Zugangsdaten und Einstellungen bleiben unverändert.",
"EINST.SITZUNG_KEINE": "Es waren keine Anmeldemarken gespeichert.",
"EINST.PYTHON_ZU_ALT": "<b>Der Dienst kann nicht laufen.</b> Die virtuelle Python-Umgebung dieses Plugins nutzt ein Python älter als 3.9; die Bibliothek requests verlangt 3.9 oder neuer. Das sollte auf keinem heutigen LoxBerry vorkommen (Debian 12 liefert 3.11) — wenn doch, ist die virtuelle Umgebung kaputt. Abhilfe: Plugin neu installieren.",


"EINST.H_TAKT": "Abholtakt",

"EINST.H_STEUERUNG": "Schreibende Befehle",
"EINST.STEUERUNG_ERKLAERUNG": "Ab Werk <b>gesperrt</b>. Schreibende Befehle starten und stoppen echte Maschinen in einem leeren Haus. Ein versehentlich gestartetes Waschprogramm läuft, ohne dass jemand Wäsche eingefüllt hat; ein abgebrochenes bleibt nass in der Trommel. Erst freigeben, wenn die Lesewerte im Reiter Test stimmen. <b>Zwei Sicherungen bleiben ohnehin:</b> Das Gerät muss die Fernstart-Freigabe haben — die gibt man am Gerät selbst, und sie erlischt meist nach dem Programm —, und ein Programm muss dort gewählt sein.",
"EINST.L_STEUERUNG_EIN": "Schreibende Befehle zulassen",
"EINST.L_WARTEZEIT": "Wartezeit auf die Antwort (Sekunden)",
"EINST.H_WARTEZEIT": "So lange wartet die Oberfläche, bis der Dienst einen Befehl beantwortet hat. Danach meldet sie <span class='sm-mono'>OK=2</span> — eingereiht, Ergebnis unbekannt. Es wird bewusst kein Erfolg gemeldet, den niemand geprüft hat.",

"EINST.L_MQTT_EIN": "Werte über MQTT veröffentlichen",
"EINST.L_MQTT_TOPIC": "Themenpräfix",
"EINST.H_MQTT_TOPIC": "Erlaubt sind Buchstaben, Ziffern, Bindestrich und Unterstrich, Ebenen getrennt durch einen Schrägstrich. Aus dem Präfix ergeben sich alle Themen, siehe Reiter MQTT. Ein bisheriges Präfix wird beim Wechsel vorgemerkt: der Dienst räumt die dort zurückbehaltenen Themen ab, die Deinstallation leert es mit.",

"EINST.GESPEICHERT": "Die Einstellungen wurden gespeichert.",
"EINST.FEHLER_ZAHL": "%s: bitte eine ganze Zahl eintragen.",
"EINST.FEHLER_BEREICH": "%s: der Wert muss zwischen %d und %d liegen.",
"EINST.FEHLER_TOPIC": "Das Themenpräfix ist unzulässig. Erlaubt sind Buchstaben, Ziffern, Bindestrich und Unterstrich, die Ebenen getrennt durch je einen Schrägstrich – nicht am Anfang, nicht am Ende, nicht doppelt –, höchstens 64 Zeichen. Es wurde nichts verändert.",
"EINST.FEHLER_ZUGANG_SPEICHERN": "Die Zugangsdatei ließ sich nicht schreiben. Rechte des Konfigurationsordners prüfen.",
"EINST.FEHLER_SPEICHERN": "Die Konfiguration ließ sich nicht schreiben: %s",

"EINST.H_ERKANNT": "Erkannte Geräte",
"EINST.T_NR": "Nr.",

# ---- MQTT ------------------------------------------------------------------
"MQTT.H_ZUSTAND": "Zustand des MQTT-Gateways",
"MQTT.GATEWAY_ERKLAERUNG": "Der MQTT-Gateway ist seit LoxBerry 3 <b>Bestandteil des Systems</b> und kein Plugin. Er wird nicht nachinstalliert, sondern unter <i>System → MQTT Gateway</i> eingeschaltet.",
"MQTT.NICHT_GEFUNDEN": "In der <span class='sm-mono'>general.json</span> des LoxBerry ist kein MQTT-Abschnitt zu finden. Ohne den kann nichts gesendet werden.",
"MQTT.AUTOSTART_AUS": "Der Gateway ist <b>nicht</b> auf Autostart gestellt. Der Broker-Eintrag allein genügt nicht — er ist ab Werk gesetzt und sagt nichts darüber aus, ob Nachrichten ankommen können. Maßgeblich ist der Autostart unter <i>System → MQTT Gateway</i>.",
"MQTT.AUTOSTART_EIN": "Der Gateway ist auf Autostart gestellt. Nachrichten dieses Plugins können also ankommen.",
"MQTT.T_AUTOSTART": "Autostart des Gateways",
"MQTT.T_BROKER": "Broker",
"MQTT.T_UDP": "UDP-Eingangsport",
"MQTT.T_PLUGIN": "Veröffentlichen durch dieses Plugin",
"MQTT.H_ABO": "Das Abo im MQTT-Gateway",
"MQTT.ABO_WARNUNG": "<b>Ohne diesen Eintrag kommt am Miniserver nichts an.</b> Das ist die häufigste Fehlerursache überhaupt. Die Zeile gehört unter <i>System → MQTT Gateway</i> in den Abschnitt <i>Subscriptions</i>; danach speichern.",
"MQTT.ABO_SCHRITTE": "Die Themengruppe dieses Plugins lautet:",
"MQTT.H_THEMEN": "Alle veröffentlichten Themen",
"MQTT.THEMEN_ERKLAERUNG": "Ein Thema, dessen Wert dieses Gerät nicht liefert, wird gar nicht erst gesendet — es entsteht also kein Thema mit einer erfundenen Null.",
"MQTT.T_THEMA": "Thema",
"MQTT.T_BEDEUTUNG": "Bedeutung",
"MQTT.T_RETAIN": "Retain",
"MQTT.RETAIN_JA": "ja",
"MQTT.RETAIN_NEIN": "nein",
"MQTT.PLATZHALTER": "<b>N</b> steht für die laufende Nummer des Geräts, also 1 für das erste.",
    "MQTT.RETAIN_ERKLAERUNG": "<b>Retain</b> heißt: der Broker behält den letzten Wert und gibt ihn jedem neuen Abonnenten sofort. Nach einem Neustart des Miniservers oder des Gateways stehen die so gesendeten Werte also sofort wieder da. Zustände der Geräte werden zurückbehalten, Messwerte mit Zeitbezug nicht, Aussagen über den Dienst selbst (Lebenszeichen, ok, Fehlversuche, Ausfälle) nie — sonst stünde nach einem Neustart ein toter Dienst als gesund da — eine Restzeit von 60 Minuten, eine Woche lang aufbewahrt, wäre eine stille Falschaussage. Ein leerer Wert geht nie zurückbehalten hinaus, denn eine leere Nutzlast löscht das Thema im Broker.",

# ---- Loxone ----------------------------------------------------------------
"LOX.H_TITEL": "Einbindung in Loxone",
"LOX.EINLEITUNG": "Neun Schritte. Wer sie von oben nach unten abarbeitet, hat am Ende eine funktionierende Einbindung — einschließlich der drei Seiten aus dem Musterprojekt in Schritt 8.",
"LOX.S1_TITEL": "Schritt 1: Weg festlegen",
"LOX.S1_TEXT": "Es gibt zwei Wege. <b>Das Musterprojekt und die Seiten in Schritt 8 nutzen HTTP</b>: die Vorlagen, das Alter der Werte und die Befehle gibt es nur dort, und man sieht im Browser sofort, was ankommt. MQTT ist der zweite Weg (ab Werk aus): der Gateway erzeugt die Namen der virtuellen Eingänge selbst und liefert auch Programmname und Zustandstext, aber kein Alter. Beide Wege gleichzeitig ergeben doppelte Eingänge.",
"LOX.S2_TITEL": "Schritt 2: Das Abo im MQTT-Gateway",
"LOX.S2_TEXT": "Nur nötig, wenn Sie den MQTT-Weg gehen. Die Themengruppe dieses Plugins lautet:",
"LOX.S3_TITEL": "Schritt 3: Virtuellen HTTP-Eingang für die Hauptwerte anlegen",
"LOX.S3_TEXT": "In Loxone Config: <i>Virtueller Eingang → Virtueller HTTP-Eingang</i>. Adresse und Zyklus:",
"LOX.S3_BEFEHLE": "Darunter je Wert eine <i>Befehlserkennung</i>. Die Vorlage unten legt alle auf einmal an — das ist weniger mühsam und weniger fehleranfällig als das Abtippen.",
"LOX.S3_STRICH": "<b>Ein Strich statt einer Zahl bedeutet: dieser Wert liegt nicht vor.</b> Es wird bewusst keine 0 gesendet — eine 0 wäre eine stille Falschaussage. Loxone behält in diesem Fall den letzten gültigen Wert. Genau deshalb braucht es die Ausfallerkennung aus Schritt 7.",
"LOX.FEHLER_VORLAGE": "Die angeforderte Vorlage gibt es nicht. Es wurde nichts erzeugt.",
"LOX.VORLAGEN_FUER": "Vorlagen für Gerät %s",
"LOX.VORLAGEN_MQTT": "Vorlage für den MQTT-Weg",
"LOX.VORLAGEN_HINWEIS": "So werden sie in Loxone Config eingespielt: im Baum links <b>Virtuelle Eingänge</b> wählen, dann im Menüband auf <b>Vordefinierte HTTP-Geräte → Vorlage Importieren…</b>. Die Befehlsdatei (VQ_…) geht denselben Weg unter <b>Virtuelle Ausgänge → Vordefinierte Geräte → Vorlage Importieren…</b> — dort heißt der Knopf ohne den Zusatz HTTP. Loxone legt dabei <b>neu an</b> und überschreibt nichts — zweimal eingelesen ergibt doppelte Bausteine. Angelegt werden nur Felder, die das Gerät beim letzten Abruf wirklich geliefert hat; was deshalb fehlt, steht als Anmerkung in der Datei.",
"LOX.K_VORLAGE_STATUS": "Status-Eingänge als Vorlage",
"LOX.K_VORLAGE_VERBRAUCH": "Verbrauchs-Eingänge als Vorlage",
"LOX.K_VORLAGE_BEFEHLE": "Befehle als virtuelle Ausgänge",
"LOX.K_VORLAGE_MQTT": "MQTT-Eingänge als Vorlage",
"LOX.VA_PROGRAMM": "Ein startet das am Gerät gewählte Programm, Aus bricht es ab. Der Start wird abgewiesen, solange am Gerät keine Fernstart-Freigabe gegeben ist.",
"LOX.VA_PAUSE": "Ein hält das laufende Programm an, Aus setzt es fort.",
"LOX.VA_NETZ": "Ein schaltet das Gerät ein, Aus schaltet es aus.",
"LOX.VA_ABRUF": "Löst einen sofortigen Abruf aus, statt auf den Takt zu warten. Kein Ausbefehl.",
"LOX.MQTT_VORLAGE_HINWEIS": "Diese Datei legt nur die Eingänge an; die Werte kommen danach vom MQTT-Gateway, nicht über die eingetragene Adresse. Ohne das Abo im Gateway kommt am Miniserver nichts an.",
"LOX.T_ADRESSE": "Adresse",
"LOX.T_ZYKLUS": "Abfragezyklus",
"LOX.T_TITEL": "Bezeichnung",
"LOX.T_BEFEHL": "Befehlserkennung",
"LOX.T_EINHEIT": "Einheit",
"LOX.T_BEDEUTUNG": "Bedeutung",

"LOX.S4_TITEL": "Schritt 4: Eingang für Verbrauch und Programmwerte",
"LOX.S4_TEXT": "Ein weiterer virtueller HTTP-Eingang nach demselben Muster wie Schritt 3, mit der Aktion <span class='sm-mono'>verbrauch</span>. Ein Zyklus von 300 Sekunden genügt.",

"LOX.S5_TITEL": "Schritt 5: Befehle senden (virtueller Ausgang)",
"LOX.S5_TEXT": "Nur nötig, wenn Loxone etwas auslösen soll. In Loxone Config einen <i>Virtuellen Ausgang</i> mit der unten stehenden Adresse anlegen und darunter je Befehl einen <i>Virtuellen Ausgang Befehl</i>. Im Befehlstext steht <span class='sm-mono'>&lt;v&gt;</span> für den übergebenen Wert. Für Automatik und App-Tasten die beiden Impulsbefehle „WW 1 Start (Befehl)“ und „WW 1 Abbrechen (Befehl)“ der Vorlage nehmen – „WW 1 Programm (Befehl)“ sendet beim Abfallen „stop“ und bricht ein eben gestartetes Programm wieder ab.",
"LOX.T_VA_ADRESSE": "Adresse des virtuellen Ausgangs",
"LOX.T_VA_ABRUF": "Sofortabruf auslösen",
"LOX.S5_WARNUNG": "Drei Dinge, die man vorher wissen sollte. <b>Erstens:</b> Schreibende Befehle sind ab Werk gesperrt und müssen im Reiter Einstellungen erst freigegeben werden. <b>Zweitens:</b> Eine Antwort mit <span class='sm-mono'>OK=1</span> heißt, dass der Anbieter die Anfrage angenommen hat. Ob das Gerät anläuft, zeigt erst der nächste Abruf — wer sicher sein will, wertet <span class='sm-mono'>LAEUFT</span> aus und nicht die Antwort auf den Befehl. <b>Drittens:</b> Jeder schaltende Befehl außer <span class='sm-mono'>abruf</span> verlangt <span class='sm-mono'>geraet=</span> — ohne antwortet das Plugin mit <span class='sm-mono'>GRUND=GERAET_FEHLT</span> und schaltet nichts. <span class='sm-mono'>ein</span> und <span class='sm-mono'>aus</span> mit demselben Wert binnen 60 Sekunden werden nicht noch einmal gesendet; die Antwort trägt dann <span class='sm-mono'>UNVERAENDERT=1</span>.",

"LOX.S6_TITEL": "Schritt 6: Das Token",
"LOX.T_TOKEN": "Token dieses Plugins",
"LOX.S6_TEXT": "Der Endpunkt liegt im unangemeldeten Bereich, damit Loxone ihn ohne Zugangsdaten erreicht. Geschützt ist er durch dieses Token. Es steckt in jeder Adresse, die Sie im Miniserver eintragen — <b>ein neues Token macht alle diese Adressen auf einen Schlag ungültig</b> und muss überall nachgetragen werden. Würfeln Sie es also nur neu, wenn es tatsächlich in falsche Hände geraten ist.",

"LOX.S7_TITEL": "Schritt 7: Ausfallerkennung",
"LOX.S7_TEXT": "Schweigt ein Anbieter, behalten die virtuellen Eingänge ihren letzten Wert. In der App sieht dann alles normal aus, obwohl seit Stunden nichts mehr angekommen ist. Deshalb wird der Wert <span class='sm-mono'>ALTER</span> mitgeführt: er sagt, wie alt das Abbild in Sekunden ist. <span class='sm-mono'>OK</span> geht nach dreimal dem Ruhetakt (15 Minuten) auf 0; steht der LoxBerry selbst, frieren auch OK und ALTER ein – das erkennt nur eine Analogwertvalidierung auf ALTER (Seite „Weissware“ in Schritt 8).",

"LOX.S8_TITEL": "Schritt 8: Drei Seiten aus dem Musterprojekt zum Nachbauen",
"LOX.S8_TEXT": "Drei Seiten aus dem LoxBerry-Plugins Musterprojekt, dort in Loxone Config gebaut und verbunden. Jede Zeile ein Baustein; Loxone Config führt alle in der Baustein-Suche (Taste F5). Wer nur überwachen will, übernimmt die erste Seite allein; „Weissware PV-Start“ ist der Fall, um den es den meisten geht: <b>waschen, wenn die Sonne scheint</b>. Die Namen gelten für Gerät 1 so, wie die Vorlagen sie anlegen; die Titel der Vorlagen sind fest deutsch, auch bei englischer Oberfläche.",

"LOX.S9_TITEL": "Schritt 9: Gegenprobe",
"LOX.S9_TEXT": "Diese drei Adressen im Browser aufrufen. Die erste muss Werte liefern, die beiden anderen müssen <b>abgewiesen</b> werden — wenn nicht, ist etwas an der Absicherung falsch.",
"LOX.T_PRUEFUNG": "Aufruf",
"LOX.T_ERWARTUNG": "Erwartete Antwort",
"LOX.T_BAUSTEIN": "Baustein (Typ)",
"LOX.T_NAMENSVORSCHLAG": "Name (Vorschlag)",
"LOX.T_PARAMETER": "Parameter",
"LOX.T_EINGAENGE": "Eingänge verbinden mit",
"LOX.K_TOKEN_NEU": "Neues Token würfeln",
"LOX.TOKEN_NEU": "Es wurde ein neues Token erzeugt. Alle bisher im Miniserver eingetragenen Adressen sind damit ungültig und müssen nachgetragen werden.",

# ---- Bausteine: seit Weissware 0.9.42 im Block "Welle Bild 16" am Ende von DE und EN; hier folgt [TEST] ---

"TEST.H_SELBSTPRUEFUNG": "Selbstprüfung",
"TEST.EINLEITUNG": "Diese Prüfung beantwortet <b>ohne Loxone</b>, ob die Einrichtung trägt. Jede Zeile ist eine Frage; ein Kreuz bedeutet, dass hier etwas fehlt. Was sich nur mit einem angemeldeten Gerät prüfen ließe, steht unten ausdrücklich als ungeprüft.",
"TEST.T_FRAGE": "Frage",
"TEST.T_BEFUND": "Befund",
"TEST.F_VENV": "Ist die virtuelle Python-Umgebung vorhanden?",
"TEST.A_VENV_FEHLT": "nein — Plugin neu installieren",
"TEST.F_PYTHON": "Ist das Python neu genug (3.9 oder neuer)?",
"TEST.A_PYTHON_ZU_ALT": "zu alt für requests",
"TEST.A_PYTHON_UNBEKANNT": "nicht feststellbar — die virtuelle Umgebung fehlt",
"TEST.F_LIB": "Ist requests geladen, und in welcher Fassung?",
"TEST.A_LIB_FEHLT": "nein — siehe Ausgabe der Installation",
"TEST.F_DIENST": "Läuft der Abrufdienst?",
"TEST.A_DIENST_LAEUFT": "ja, PID",
"TEST.A_DIENST_SOLL_TOT": "nein — er soll laufen, tut es aber nicht. Logdatei ansehen.",
"TEST.A_DIENST_GESTOPPT": "nein — bewusst angehalten",
"TEST.F_RECHTE": "Ist die Zugangsdatei vor fremden Blicken geschützt?",
"TEST.A_ZUGANGSDATEI_FEHLT": "die Datei fehlt",
"TEST.F_AUSFAELLE": "Haben alle Anbieter geantwortet?",
"TEST.A_KEINE_AUSFAELLE": "ja, alle",
"TEST.F_ABRUF": "Wie frisch ist das Abbild?",
"TEST.A_ABRUF_ALTER": "%d Sekunden alt",
"TEST.A_NIE_ABGERUFEN": "es hat noch kein Abruf stattgefunden",
"TEST.F_LETZTER_FEHLER": "Letzte gemeldete Störung",
"TEST.F_MQTT": "Steht das MQTT-Gateway von LoxBerry bereit?",
"TEST.F_MQTT_EIN": "Ist die MQTT-Veröffentlichung dieses Plugins eingeschaltet?",
"TEST.A_MQTT_EIN_JA": "Ja. Der Dienst schickt seine Themen an den UDP-Eingang des Gateways.",
"TEST.A_MQTT_EIN_NEIN": "Nein — es geht nichts an den Broker und damit nichts an Loxone. Reiter MQTT.",
"TEST.A_MQTT_NICHT_GEFUNDEN": "kein MQTT-Abschnitt in der general.json",
"TEST.A_MQTT_AUS": "nicht auf Autostart — System, MQTT Gateway",
"TEST.F_STEUERUNG": "Sind schreibende Befehle zugelassen?",
"TEST.A_STEUERUNG_EIN": "ja",
"TEST.A_STEUERUNG_AUS": "nein — ab Werk gesperrt, das ist kein Fehler",

"TEST.H_LESEN": "Ansehen",
"TEST.K_STATUS": "Status abrufen",
"TEST.H_TECHNIK": "Technische Auskunft",
"TEST.K_SELBSTTEST": "Selbsttest des Dienstes",
"TEST.F_REITER": "Führen Reiterleiste, Bereiche und Positivliste dieselben Namen?",
"TEST.A_REITER_UNLESBAR": "index.php ist nicht lesbar - nicht feststellbar",
"TEST.A_REITER_OK": "%d Reiter, alle drei Stellen deckungsgleich",
"TEST.A_REITER_AB": "Leiste %d, Bereiche %d, Positivliste %d - sie passen nicht zusammen",
"WW_MQTT.GEWAEHLT": "Das am Gerät gewählte Programm, solange keines läuft (nur Home Connect)",
"WW_ANSAGE.EIN_GERAET": "Ein Haushaltsgerät",
"WW_ANSAGE.T_FERTIG": "Hallo! %s ist fertig.",
"WW_ANSAGE.T_STOERUNG": "Achtung! %s meldet eine Störung.",
"WW_ANSAGE.HAUSFORM": "Gesprochen wird über die gemeinsame Sprachausgabe der Plugins dieses Hauses: Loxone Music Server, MusicServer4Home, eine eigene Adressvorlage, den originalen Audioserver (über Loxone Config), Alexa-NG oder Google-Lautsprecher (Chromecast 4 Lox NG). Adresse und Vorlage müssen im Heimnetz liegen. Ins Protokoll kommt vom Text nur die Länge.",
"WW_ANSAGE.TEST_GESENDET": "Testansage gesendet: %s",
"WW_ANSAGE.TEST_NICHT": "Testansage nicht gesendet: %s",
"WW_ANSAGE.TEST_NICHTS": "Keine Testansage: %s",
"WW_ANSAGE.TEST_WAS": "%d Zeichen, HTTP %d.",
"TEST.F_ANSAGE": "Sprachausgabe: eingerichtet, und wie ging die letzte Ansage aus?",
"WW_ANSAGE.T_FERNSTART": "Hinweis: bei %s ist die Fernstart-Freigabe erloschen.",
"WW_ANSAGE.L_STOERUNG": "Auch bei einer Störung sprechen",
"WW_ANSAGE.L_FERNSTART": "Auch sprechen, wenn die Fernstart-Freigabe erlischt",
"WW_ANSAGE.H_FERNSTART": "Die Freigabe wird am Gerät gegeben und erlischt meist mit dem Programmende. Danach weist das Plugin jeden Startbefehl ab — ohne diese Ansage merkt man es erst, wenn die Sonne umsonst geschienen hat.",
"WW_ANSAGE.L_RUHE_VON": "Ruhezeit von",
"WW_ANSAGE.L_RUHE_BIS": "Ruhezeit bis",
"WW_ANSAGE.H_RUHE": "In diesem Fenster wird nicht gesprochen. Der Stand wird trotzdem fortgeschrieben, damit um sieben Uhr nicht die halbe Nacht nachgeholt wird. Gleiche Zeiten heißen: keine Ruhezeit.",
"WW_ANSAGE.FEHLER_ZEIT": "%s: bitte eine Uhrzeit in der Form 22:00 eintragen.",
"LAUF.H": "Beendete Programmläufe",
"LAUF.ERKLAERUNG": "Festgehalten im Augenblick, in dem ein Gerät auf <i>fertig</i> wechselt — danach sind Energie und Wasser beim Anbieter fort. Ein Strich heißt: dieser Wert lag nicht vor. Home Connect liefert weder Energie noch Wasser, SmartThings kein Wasser.",
"LAUF.LEER": "Noch kein Lauf beendet worden, seit das Plugin mitschreibt.",
"LAUF.T_ENDE": "Ende",
"LAUF.T_PROGRAMM": "Programm",
"LAUF.T_DAUER": "Dauer (min)",
"LAUF.T_ENERGIE": "Energie (kWh)",
"LAUF.T_WASSER": "Wasser (l)",
"TEST.F_ENDPUNKT": "Antwortet der eigene Endpunkt über HTTP?",
"TEST.A_EP_UNMESSBAR": "nicht feststellbar: weder curl noch allow_url_fopen stehen zur Verfügung",
"TEST.A_EP_KEINE_ANTWORT": "nicht feststellbar: keine Antwort (HTTP %d). Ein Webserver, der nur eine Anfrage zugleich bearbeitet, kann sich während des Seitenaufbaus nicht selbst aufrufen.",
"TEST.A_EP_FALSCH": "HTTP %d, und die Antwort beginnt nicht mit der erwarteten Kennung: %s",
"TEST.A_EP_ALTER": "vor %d s gemessen",
"TEST.F_VORGABEN": "Führen Oberfläche und Dienst dieselben Vorgabewerte?",
"TEST.A_VORGABEN_UNLESBAR": "bin/weissware.py ist nicht lesbar - nicht feststellbar",
"TEST.A_VORGABEN_FEHLEN": "der Oberfläche fehlen: %s",
"TEST.A_VORGABEN_OK": "alle %d Schlüssel des Dienstes sind auch der Oberfläche bekannt",
"TEST.F_THEMEN": "Stimmt die Themenliste mit dem Sendecode überein?",
"TEST.A_THEMEN_UNLESBAR": "bin/weissware.py ist nicht lesbar - nicht feststellbar",
"TEST.A_THEMEN_AB": "Abweichung: %s",
"TEST.A_THEMEN_OK": "%d Themen je Gerät, Liste und Sendecode deckungsgleich",
"TEST.F_RETAIN": "Stimmen die beiden Retain-Tabellen überein?",
"TEST.A_RETAIN_OK": "%d von %d Themenstämmen zurückbehalten; Oberfläche, Dienst und Themenliste deckungsgleich",
"TEST.A_RETAIN_AB": "die Tabellen weichen ab: %s",
"TEST.A_RETAIN_UNLESBAR": "die Tabelle in bin/weissware.py ist nicht lesbar - nicht feststellbar",
"TEST.F_MITSCHNITT": "Läuft ein Mitschnitt?",
"TEST.A_MITSCHNITT_LAEUFT": "ja, noch %d Sekunden. Er endet von selbst.",
"TEST.K_TROCKEN": "Trockenlauf: was würde geschehen?",
"TEST.H_TROCKEN": "Zeigt für <i>Start</i>, welche Sperre greift und welche Anfrage an den Anbieter hinausginge — und <b>sendet nichts</b>. Er braucht keinen laufenden Dienst; gerade dann will man es wissen.",
"TEST.K_MITSCHNITT_EIN": "Mitschnitt 5 Minuten einschalten",
"TEST.K_MITSCHNITT_AUS": "Mitschnitt jetzt beenden",
"TEST.H_MITSCHNITT": "Schreibt Anfragen und Antworten der Anbieter mit — das einzige Mittel, wenn ein Wert leer bleibt und niemand weiß, ob der Anbieter nichts liefert oder die Zuordnung den Schlüssel verfehlt. Ab Werk aus, endet von selbst, die Datei ist auf 500 kB begrenzt. Zugangsdaten und Token werden vor dem Schreiben entfernt.",
"TEST.M_MITSCHNITT_EIN": "Der Mitschnitt läuft %d Sekunden und endet dann von selbst.",
"TEST.M_MITSCHNITT_AUS": "Der Mitschnitt ist beendet.",
"TEST.K_ROH": "Rohdaten als JSON ansehen",
"TEST.H_SCHALTEN": "Schalten",
"TEST.SCHALTEN_WARNUNG": "<b>Diese Knöpfe wirken sofort und am echten Gerät.</b> Ein gestartetes Waschprogramm läuft durch, auch wenn niemand Wäsche eingefüllt hat. Ohne Fernstart-Freigabe am Gerät weist der Anbieter den Start ab — das ist keine Störung, sondern die Sicherung, die dafür gedacht ist.",
"TEST.SCHALTEN_GESPERRT": "Schreibende Befehle sind zurzeit gesperrt. Die Knöpfe geben deshalb eine Ablehnung zurück — das ist kein Fehler. Freigeben im Reiter Einstellungen.",
"TEST.K_ABRUF": "Sofort abrufen",
"TEST.M_UNBEKANNT": "Unbekannte Testaktion.",
"TEST.M_DIENST_AUS": "Der Abrufdienst läuft nicht – es wurde nichts eingereiht. Erst im Reiter Einstellungen den Dienst starten.",
"TEST.H_UNGEPRUEFT": "Was in dieser Fassung ungeprüft ist",
"TEST.UNGEPRUEFT": "Dieses Plugin wurde <b>ohne Entwicklerkonten und ohne Geräte</b> gebaut. Ungeprüft ist deshalb: ob die Anmeldung bei den drei Anbietern gelingt, ob die Feldnamen der Antworten zu der Zuordnung hier passen und ob die schreibenden Befehle am Gerät die erwartete Wirkung haben. Endpunkte und Datenformen stammen aus den Entwicklerdokumentationen, nicht aus einer Messung. Geprüft ist alles übrige: Oberfläche, Endpunkt, Absicherung, Warteschlange, Sprachdateien und die Zuordnung selbst — letztere gegen nachgebaute Antworten in der dokumentierten Form. Deshalb bleibt diese Linie in der Nummernreihe 0.9.x und nicht bei 1.0.0. Wenn etwas leer bleibt, hilft der Knopf <i>Rohdaten als JSON ansehen</i>: dort steht, was der Dienst tatsächlich bekommen hat.",

# ---- Logdateien ------------------------------------------------------------
"LOG.H_TITEL": "Logdateien",
"LOG.ERKLAERUNG": "Der Abrufdienst schreibt ausschließlich in diese eine Datei. Unten stehen die letzten 400 Zeilen, die neueste zuerst.",
"LOG.LEER": "Die Logdatei ist leer oder noch nicht angelegt.",
"LOG.K_LEEREN": "Logdatei leeren",
"LOG.GELEERT": "Logdatei geleert",

# ---- Feldbedeutungen (Status) ---------------------------------------------
"WW_FELD.ALTER": "Alter des Abbilds — für die Ausfallerkennung",
"WW_FELD.OK": "1 = der letzte Abruf war erfolgreich und liegt höchstens dreimal den Ruhetakt zurück; bei mehreren Anbietern zusätzlich: der Anbieter dieses Geräts hat geantwortet (sonst 0, die Werte sind die zuletzt gemessenen)",

# ---- Feldbedeutungen (Laden) ----------------------------------------------
"WW_VFELD.OK": "1 = der letzte Abruf war erfolgreich und liegt höchstens dreimal den Ruhetakt zurück; bei mehreren Anbietern zusätzlich: der Anbieter dieses Geräts hat geantwortet",

# ---- Feldbedeutungen (Wartung) --------------------------------------------

# ---- MQTT-Themen -----------------------------------------------------------
"WW_MQTT.OK": "1 = der letzte Abruf war erfolgreich",
"TEST.A_MARKE_FEHLT": "noch nicht angelegt — entsteht beim ersten Abruf",
"TEST.F_MARKE": "Sind die Anmeldemarken vor fremden Blicken geschützt?",
"WW_FELD.ZUSTAND": "0 aus, 1 bereit, 2 läuft, 3 pausiert, 4 fertig, 5 Störung",
"WW_MQTT.FERTIG": "1 = Programm beendet",
"WW_MQTT.ZUSTAND": "0 aus, 1 bereit, 2 läuft, 3 pausiert, 4 fertig, 5 Störung",
"ALLG.GERAET": "Gerät",
"ALLG.GERAETE": "Geräte",
"ALLG.IN_BETRIEB": "in Betrieb",
"ALLG.KEIN_FERNSTART": "keine Fernstart-Freigabe",
"ALLG.RESTZEIT": "Restzeit",
"ALLG.ZUSTAND": "Zustand",
"EINST.ANBIETER_ERKLAERUNG": "Drei Ökosysteme, ein gemeinsames Modell. Eingeschaltet wird nur, was Sie wirklich haben — jeder eingeschaltete Anbieter kostet Anfragen, auch wenn kein Gerät da ist. Bei Home Connect und Miele brauchen Sie ein <b>kostenloses Entwicklerkonto</b>, weil beide nur registrierten Anwendungen antworten; SmartThings kommt mit einem Token aus.",
"EINST.ANGEMELDET": "angemeldet",
"EINST.ANMELDUNG_ERKLAERUNG": "Erst speichern, dann anmelden. Die Anmeldung legt einen Erneuerungsschlüssel ab, mit dem sich der Dienst von selbst weiter anmeldet — Sie müssen das also nur einmal tun. Ausnahme ist SmartThings, siehe oben.",
"EINST.FEHLER_MIELE_CODE": "Der eingegebene Wert sieht nicht wie ein Anmeldecode aus. Er wurde nicht eingelöst.",
"EINST.FEHLER_SPRACHE": "Die Sprache muss die Form de-DE haben.",
"EINST.FEHLER_TAKT_TAUSCH": "Der Takt in Ruhe ist kleiner als der im Betrieb. Das ist verkehrt herum — bitte die beiden Werte tauschen.",
"EINST.GESETZT": "gespeichert (%d Zeichen) – leer lassen, um es zu behalten",
"EINST.HC_ADRESSE": "Adresse",
"EINST.HC_ADRESSE_DIREKT": "Adresse mit Code",
"EINST.HC_BEGONNEN": "Die Anmeldung wurde begonnen. Code und Adresse stehen unten — Sie haben fünf Minuten.",
"EINST.HC_CODE": "Code",
"EINST.HC_FERTIG": "Home Connect ist angemeldet.",
"EINST.HC_GUELTIG": "gültig noch",
"EINST.HC_NOCH_NICHT": "Noch nicht bestätigt. Code im Browser eingeben, Zugriff erlauben und dann erneut auf „Anmeldung abschließen“ drücken.",
"EINST.HC_SCHRITT1": "Auf <i>Anmeldung beginnen</i> drücken. Danach erscheinen hier ein Code und eine Adresse; die Adresse in einem beliebigen Browser öffnen, den Code eingeben und den Zugriff erlauben. Zum Schluss auf <i>Anmeldung abschließen</i> drücken.",
"EINST.HC_SCHRITT2": "Die Anmeldung läuft. Öffnen Sie die Adresse in einem Browser, geben Sie den Code ein, erlauben Sie den Zugriff — und drücken Sie dann hier auf <i>Anmeldung abschließen</i>.",
"EINST.H_ANBIETER": "Anbieter",
"EINST.H_ANMELDUNG": "Anmeldung",
"EINST.H_HC_ID": "Aus dem Entwicklerportal von Home Connect, Abschnitt <i>Applications</i>. Legen Sie dort eine Anwendung mit dem Anmeldeverfahren <b>Device Flow</b> an — das ist das einzige, das ohne Bildschirm am Gerät auskommt.",
"EINST.H_HC_SECRET": "Nur für das Erneuern des Zugriffstokens nötig. Bleibt das Feld leer, bleibt das gespeicherte Geheimnis unverändert.",
"EINST.H_HC_SIMULATOR": "Home Connect stellt simulierte Geräte bereit. Damit lässt sich alles einrichten und in Loxone nachbauen, bevor eine echte Maschine angeschlossen ist. <b>Achtung:</b> Simulator und echte Geräte brauchen verschiedene Client-IDs.",
"EINST.H_MIELE_CODE": "Die ganze Adresse geht auch — der Code wird daraus herausgesucht. Der Code ist nur wenige Minuten gültig und lässt sich genau einmal einlösen.",
"EINST.H_MIELE_ID": "Aus dem Miele-Entwicklerportal, Abschnitt <i>Get involved</i>. Als Weiterleitungsadresse tragen Sie dort <span class='sm-mono'>http://localhost</span> ein — die Adresse muss nicht erreichbar sein, der Code wird von Hand zurückkopiert.",
"EINST.H_SPRACHE": "In dieser Sprache liefern die Anbieter die Programmnamen und Zustandstexte. Auf die Sprache dieser Oberfläche hat das keinen Einfluss.",
"EINST.H_ST_TOKEN": "Aus dem SmartThings-Entwicklerportal. Bleibt das Feld leer, bleibt das gespeicherte Token unverändert.",
"EINST.H_TAKT_BETRIEB": "Abstand, sobald mindestens ein Gerät arbeitet. Untergrenze 60 Sekunden: Home Connect nennt häufiges Abfragen in seinen Best Practices ausdrücklich als häufigste Ursache für HTTP 429.",
"EINST.H_TAKT_RUHE": "Abstand, solange kein Gerät läuft. Fünf Minuten sind reichlich — eine Waschmaschine, die aus ist, wird nicht in einer Minute fertig.",
"EINST.KEINE_GERAETE": "Noch kein Gerät erkannt. Bis zum ersten erfolgreichen Abruf ist das normal: Anbieter einschalten, Zugangsdaten eintragen, speichern, anmelden, Dienst starten und eine Taktlänge abwarten. Bleibt die Liste danach leer, steht der Grund im Reiter <i>Test</i> und in der Logdatei.",
"EINST.KENNUNG_HINWEIS": "In allen Adressen kann statt der Nummer auch die Kennung stehen — <span class='sm-mono'>geraet=SIEMENS-HCS03WCH1-…</span>. Die Nummer bleibt einem Gerät seit 0.9.7 dauerhaft zugeordnet — auch wenn ein Anbieter ausfällt oder ein Gerät dazukommt; sie steht in <span class='sm-mono'>data/plugins/weissware/geraetenummern.json</span>. Die Kennung ist trotzdem die deutlichere Adresse, weil man ihr ansieht, welches Gerät gemeint ist.",
"EINST.K_HC_FERTIG": "Anmeldung abschließen",
"EINST.K_HC_START": "Anmeldung beginnen",
"EINST.K_MIELE_CODE": "Code einlösen",
"EINST.LEER": "noch nichts gespeichert",
"EINST.L_HC_EIN": "Home Connect abfragen",
"EINST.L_HC_ID": "Client-ID",
"EINST.L_HC_SECRET": "Client Secret",
"EINST.L_HC_SIMULATOR": "Simulator statt echter Geräte verwenden",
"EINST.L_MIELE_CODE": "Code aus der Adresszeile",
"EINST.L_MIELE_EIN": "Miele abfragen",
"EINST.L_MIELE_ID": "Client-ID",
"EINST.L_MIELE_SECRET": "Client Secret",
"EINST.L_SPRACHE": "Sprache der Anbieterantworten",
"EINST.L_ST_EIN": "SmartThings abfragen",
"EINST.L_ST_TOKEN": "Personal Access Token",
"EINST.L_TAKT_BETRIEB": "Takt im Betrieb (Sekunden)",
"EINST.L_TAKT_RUHE": "Takt in Ruhe (Sekunden)",
"EINST.MIELE_FERTIG": "Miele ist angemeldet.",
"EINST.MIELE_OHNE_ID": "Erst die Client-ID oben eintragen und speichern — ohne sie lässt sich keine Anmeldeadresse bilden.",
"EINST.MIELE_SCHRITTE": "Miele bietet <b>kein</b> Verfahren für Geräte ohne Bildschirm an. Deshalb von Hand: die Adresse unten in einen Browser kopieren, mit dem Miele-Konto anmelden, die Geräte auswählen, die freigegeben werden sollen. Danach landen Sie auf einer Seite, die nicht lädt — das ist richtig so. Aus deren <b>Adresszeile</b> den Teil hinter <span class='sm-mono'>code=</span> kopieren (oder die ganze Adresse) und hier einfügen.",
"EINST.ST_SCHRITTE": "SmartThings braucht keine Anmeldung — das Token oben genügt. Es läuft allerdings nach 24 Stunden ab; dann tragen Sie hier ein neues ein und speichern.",
"EINST.ST_WARNUNG": "<b>Vorbehalt.</b> Samsung hat die Lebensdauer neu ausgestellter Personal Access Tokens am 30.12.2024 auf <b>24 Stunden</b> verkürzt und die Ratengrenzen gesenkt. Für Dauerbetrieb verlangt Samsung eine registrierte Anwendung mit einem von außen erreichbaren Webhook — das kann ein LoxBerry hinter einem Router nicht ohne Weiteres. Praktisch heißt das: <b>Sie müssen das Token täglich erneuern.</b> Wer damit nicht leben will, lässt SmartThings aus. Wer ein älteres Token von vor dem 30.12.2024 hat, ist nicht betroffen.",
"EINST.TAKT_ERKLAERUNG": "<b>Der eigentliche Grund für dieses Plugin.</b> Ein starrer Abfragezyklus ist entweder zu langsam für eine brauchbare Restzeit oder zu schnell für die Ratengrenzen des Anbieters. Hier gibt es zwei Takte: einen weiten, solange nichts läuft, und einen engen, sobald mindestens ein Gerät arbeitet. Umgeschaltet wird von selbst.",
"EINST.T_ANBIETER": "Anbieter",
"EINST.T_FERNSTART": "Fernstart",
"EINST.T_KENNUNG": "Kennung",
"EINST.T_MARKE": "Marke",
"EINST.T_NAME": "Name",
"EINST.T_TYP": "Art",
"EINST.T_ZUSTAND": "Zustand",
"EINST.WARN_HC_OHNE_ID": "Home Connect ist eingeschaltet, aber es ist keine Client-ID hinterlegt. So schlägt jeder Abruf fehl.",
"EINST.WARN_MIELE_OHNE_ID": "Miele ist eingeschaltet, aber es ist keine Client-ID hinterlegt. So schlägt jeder Abruf fehl.",
"EINST.WARN_ST_OHNE_TOKEN": "SmartThings ist eingeschaltet, aber es ist kein Token hinterlegt. So schlägt jeder Abruf fehl.",
"LOX.MEHRERE_GERAETE": "Mehrere Geräte — je Gerät ein eigener virtueller Eingang:",
"LOX.S4_LEER": "<b>Nicht jeder Anbieter liefert jeden Wert.</b> Home Connect meldet weder Energie- noch Wasserverbrauch; SmartThings meldet keinen Fortschritt in Prozent; Miele liefert beides, aber nur bei Geräten mit EcoFeedback. Was fehlt, ist ein Strich — keine 0.",
"LOX.T_VA_AUS": "Gerät ausschalten",
"LOX.T_VA_EIN": "Gerät einschalten",
"LOX.T_VA_FORTSETZEN": "Programm fortsetzen",
"LOX.T_VA_PAUSE": "Programm anhalten",
"LOX.T_VA_START": "Programm starten (das am Gerät gewählte)",
"LOX.T_VA_START_PROG": "Bestimmtes Programm starten (nur Home Connect)",
"LOX.T_VA_STOP": "Programm abbrechen",
"TEST.A_ANBIETER": "ja, %d",
"TEST.A_ANGEMELDET": "ja, der Dienst erneuert sich selbst",
"TEST.A_GERAETE": "ja, %d",
"TEST.A_KEINE_GERAETE": "nein — bis zum ersten erfolgreichen Abruf normal",
"TEST.A_KEIN_ANBIETER": "nein — Reiter Einstellungen",
"TEST.A_NICHT_ANGEMELDET": "nein — Reiter Einstellungen, Abschnitt Anmeldung",
"TEST.A_ST_TOKEN": "entfällt — SmartThings braucht nur das Token (24 Stunden gültig)",
"TEST.A_ZUGANG_DA": "ja",
"TEST.A_ZUGANG_FEHLT": "nein",
"TEST.F_ANBIETER": "Ist mindestens ein Anbieter eingeschaltet?",
"TEST.F_ANGEMELDET": "%s: ist die Anmeldung abgeschlossen?",
"TEST.F_AUSFALL": "Hat %s geantwortet?",
"TEST.F_GERAETE": "Sind Geräte erkannt?",
"TEST.F_ZUGANG": "%s: sind Zugangsdaten hinterlegt?",
"TEST.H_PROGRAMM": "Leer lassen, um das am Gerät gewählte Programm zu starten — das ist der Regelfall. Ein Programmschlüssel wirkt <b>nur bei Home Connect</b> und sieht dort aus wie <span class='sm-mono'>LaundryCare.Washer.Program.Cotton</span>; bei Miele und SmartThings wird ein Start mit Schlüssel abgewiesen. Sichtbar wird der Schlüssel, sobald ein Programm läuft: dann führt ihn der Knopf <i>Rohdaten als JSON ansehen</i>.",
"TEST.K_AUS": "Gerät aus",
"TEST.K_EIN": "Gerät ein",
"TEST.K_FORTSETZEN": "Fortsetzen",
"TEST.K_GERAETE": "Geräte auflisten",
"TEST.K_PAUSE": "Anhalten",
"TEST.K_START": "Programm starten",
"TEST.K_STOP": "Programm abbrechen",
"TEST.K_VERBRAUCH": "Verbrauch abrufen",
"TEST.L_GERAET": "Gerät (laufende Nummer)",
"TEST.L_PROGRAMM": "Programm (freiwillig)",
"TEST.M_GERAET_UNGUELTIG": "Die Gerätenummer ist keine Zahl zwischen 1 und 999.",
"TEST.M_PROGRAMM_UNGUELTIG": "Der Programmschlüssel enthält Zeichen, die dort nicht vorkommen. Er wurde nicht gesendet.",
"WW_FELD.FERNBED": "1 = Fernbedienung ist erlaubt",
"WW_FELD.FERNSTART": "1 = am Gerät ist der Fernstart freigegeben",
"WW_FELD.FERTIG": "1 = Programm beendet, noch nicht quittiert",
"WW_FELD.FORTSCHR": "Fortschritt des laufenden Programms",
"WW_FELD.LAEUFT": "1 = ein Programm läuft gerade",
"WW_FELD.LAUFMIN": "Bisherige Laufzeit des Programms",
"WW_FELD.NETZ": "1 = Gerät eingeschaltet",
"WW_FELD.RESTMIN": "Restzeit bis zum Programmende",
"WW_FELD.STARTMIN": "Zeit bis zum Start bei Startvorwahl",
"WW_FELD.TUER": "1 = Tür offen",
"WW_FELD.VERBUNDEN": "1 = das Gerät ist für den Anbieter erreichbar",
"WW_MQTT.ANBIETER": "homeconnect, miele oder smartthings",
"WW_MQTT.ENERGIE": "Energieverbrauch in kWh",
"WW_MQTT.FERNBED": "1 = Fernbedienung erlaubt",
"WW_MQTT.FERNSTART": "1 = Fernstart am Gerät freigegeben",
"WW_MQTT.FORTSCHRITT": "Fortschritt in Prozent",
"WW_MQTT.GERAETE": "Anzahl der erkannten Geräte",
"WW_MQTT.LAEUFT": "1 = ein Programm läuft gerade",
"WW_MQTT.LAUFZEIT": "Bisherige Laufzeit in Minuten",
"WW_MQTT.NAME": "Name des Geräts",
"WW_MQTT.NETZ": "1 = Gerät eingeschaltet",
"WW_MQTT.PROGRAMM": "Laufendes Programm im Klartext",
"WW_FELD.FERTIGUM": "Voraussichtlicher Fertigzeitpunkt als Unixzeit. Loxone rechnet in Sekunden seit dem 01.01.2009, dort also den Wert minus 1230768000. Ein Strich heißt: keine Restzeit bekannt.",
"WW_MQTT.TS": "Zeitpunkt des letzten <b>erfolgreichen</b> Abrufs als Unixzeit. Über MQTT gibt es kein Alter - beim Senden ist es immer null; der Miniserver rechnet es aus: (Loxone-Zeit + 1230768000) - ts.",
"WW_MQTT.FEHLER_FOLGE": "Fehlgeschlagene Abrufe in Folge. 0 heißt: der letzte saß. Trennt einen kurzen Aussetzer von einer Dauerstörung.",
"WW_MQTT.FERTIGUM": "Voraussichtlicher Fertigzeitpunkt als Unixzeit",
"WW_MQTT.RESTZEIT": "Restzeit in Minuten",
"WW_MQTT.SCHLEUDER": "Eingestellte Schleuderdrehzahl",
"WW_MQTT.STARTZEIT": "Zeit bis zum Start in Minuten",
"WW_MQTT.TEMPERATUR": "Eingestellte Temperatur in Grad Celsius",
"WW_MQTT.TUER": "1 = Tür offen",
"WW_MQTT.VERBUNDEN": "1 = für den Anbieter erreichbar",
"WW_MQTT.WASSER": "Wasserverbrauch in Litern",
"WW_MQTT.ZUSTAND_TEXT": "Zustand im Klartext, wie der Anbieter ihn nennt",
"WW_VFELD.ENERGIE": "Energieverbrauch des laufenden Programms",
"WW_VFELD.SCHLEUDER": "Eingestellte Schleuderdrehzahl",
"WW_VFELD.TEMP": "Eingestellte Temperatur",
"WW_VFELD.WASSER": "Wasserverbrauch des laufenden Programms",
"WW_ANSAGE.H": "Sprachausgabe (Ansage, wenn ein Gerät fertig ist)",
"WW_ANSAGE.H_EIN": "Gesprochen wird beim Wechsel eines Geräts auf <i>fertig</i> – einmal je Programmlauf, nie beim Neustart des LoxBerry. Vorgabe: an.",
"WW_ANSAGE.H_TEST": "Ansage",
"WW_ANSAGE.H_TEST_TEXT": "Spricht sofort in die konfigurierten Zonen – unabhängig davon, ob die Ansage eingeschaltet ist.",
"WW_ANSAGE.K_TEST": "Testansage jetzt sprechen",
"WW_ANSAGE.L_EIN": "Ansage einschalten",
"WW_ANSAGE.TESTTEXT": "Hallo! Dies ist eine Testansage des Weissware-Plugins.",
"TEST.A_FELDER_AB": "Abweichung: %s",
"TEST.A_FELDER_OK": "%d Felder, Vorlage und Zeile deckungsgleich",
"TEST.A_FELDER_UNLESBAR": "die Statuszeile ist nicht lesbar - nicht feststellbar",
"TEST.A_MUSTER_AB": "nicht eindeutig: %s - Loxone nimmt den ersten Treffer und liefert den falschen Wert",
"TEST.A_MUSTER_OK": "%d Feldnamen, keiner steckt in einem anderen",
"TEST.A_ZWEITSCHRIFT_DA": "ja: %s, neben dem Konfigordner",
"TEST.A_ZWEITSCHRIFT_FEHLT": "noch keine - sie entsteht beim ersten Speichern",
"TEST.F_FELDER": "Führen Vorlage und Statuszeile dieselben Feldnamen?",
"TEST.F_MUSTER": "Ist jedes Suchmuster der Statuszeile eindeutig?",
"TEST.F_ZWEITSCHRIFT": "Gibt es eine Zweitschrift der Konfiguration?",
"WW_MQTT.AUSFAELLE": "Anzahl der Anbieter, die beim letzten Abruf nicht geantwortet haben",
"WW_MQTT.AUSFALL_HC": "1 = Home Connect hat beim letzten Abruf nicht geantwortet",
"WW_MQTT.AUSFALL_MIELE": "1 = Miele hat beim letzten Abruf nicht geantwortet",
"WW_MQTT.AUSFALL_ST": "1 = SmartThings hat beim letzten Abruf nicht geantwortet",
"ALLG.STOERUNG_ALTER": "(vor %d s festgestellt)",
"EINST.FEHLER_KEIN_ANBIETER": "Es ist kein Anbieter eingeschaltet - der Dienst würde sofort wieder aufhören. Setzen Sie oben den Haken bei dem Anbieter, den Sie haben, und speichern Sie. Angemeldet sein genügt nicht: Anmeldung und Haken sind zwei verschiedene Dinge.",
"EINST.MIELE_SCHON_ANGEMELDET": "Der Dienst hält sich selbst angemeldet. Die Schritte unten brauchen Sie nur, wenn Sie sich neu anmelden wollen.",
"TEST.A_ANGEMELDET_AUS": "ja: %s. Angemeldet, aber der Haken im Reiter Einstellungen fehlt - dieser Anbieter wird nicht abgefragt.",
"TEST.F_ANGEMELDET_AUS": "Ist ein angemeldeter Anbieter ausgeschaltet?",
"LOX.VA_KURZ": "Weissware Befehle - schreibende Befehle müssen im Reiter Einstellungen freigegeben sein",

# NACHGEPFLEGT 31.08.2026. Diese 18 Schluessel standen in der
# ausgelieferten .ini und im PHP, aber nicht mehr hier - ein Lauf
# haette sie geloescht, und der Erzeuger hat sich deshalb bisher
# geweigert zu schreiben. Die Werte sind aus der .ini geholt.
"EINST.H_SICHERUNG": "Einstellungen sichern und zurückspielen",
"EINST.K_SICHERN": "Einstellungen sichern",
"EINST.K_ZURUECK": "Zurückspielen",
"EINST.SICH_ABGELEHNT": "Die Datei wurde <b>nicht</b> übernommen — es ist nichts geändert worden:",
"EINST.SICH_ERKLAERUNG": "Für den <b>Umzug auf einen zweiten LoxBerry</b>: die Datei enthält alle Einstellungen dieses Plugins samt Aktionstoken und Zugangsdaten und lässt sich dort wieder einspielen. Nicht enthalten sind die Anmeldemarken der Anbieter — nach dem Zurückspielen ist einmal neu anzumelden.",
"EINST.SICH_FREMD": "Unbekannte Einstellung in der Datei: %s",
"EINST.SICH_KEINE_DATEI": "Es wurde keine Datei ausgewählt oder der Upload ist fehlgeschlagen.",
"EINST.SICH_KEIN_JSON": "Die Datei ist keine gültige Sicherung dieses Plugins.",
"EINST.SICH_LEER": "Die Datei enthält keine bekannte Einstellung.",
"EINST.SICH_SCHREIBFEHLER": "Die Einstellungen ließen sich nicht schreiben.",
"EINST.SICH_UEBERNOMMEN": "Einstellungen zurückgespielt: %d Werte übernommen.",
"EINST.SICH_WARNUNG": "<b>Die Datei enthält Ihre Zugangsdaten.</b> Ohne sie stünden nach dem Zurückspielen alle Felder richtig, und das Plugin käme trotzdem nicht an die Anlage. Behandeln Sie die Datei wie ein Passwort: nicht in ein Forum hängen und nicht an einen Fehlerbericht heften.",
"EINST.SICH_DIENST_AUS": "Der Dienst lief nicht; es wurde nichts nachgezogen.",
"EINST.SICH_DIENST_NEU": "Der Dienst wurde mit den neuen Einstellungen neu gestartet.",
"EINST.SICH_DIENST_FEHL": "Der Dienst ließ sich nicht neu starten – bitte im Reiter Einstellungen von Hand starten.",
"EINST.SICH_OHNE_TOKEN": "In der Datei fehlt das Aktionstoken. Ohne es wären alle Adressen ungültig, die im Miniserver eingetragen sind – deshalb wird gar nichts übernommen.",
"EINST.SICH_WERT": "Unzulässiger Wert für: %s",
"EINST.SICH_ZUGANG_FEHL": "Die Einstellungen wurden übernommen, die Zugangsdaten aus der Datei ließen sich aber nicht schreiben.",
"EINST.SICH_ZU_GROSS": "Die Datei ist größer als erlaubt — eine Sicherung dieses Plugins ist wenige Kilobyte groß.",
"MQTT.ABO_GEMESSEN": "(gemessen: Gateway&nbsp;V%d)",
"MQTT.ABO_UNBEKANNT": "Welche Fassung Ihr MQTT&#8209;Gateway hat, ließ sich nicht feststellen. <b>Fassung&nbsp;1:</b> ohne diesen Eintrag kommt am Miniserver nichts an. <b>Fassung&nbsp;2 und neuer:</b> die Themengruppe erscheint von selbst in den Subscriptions, einzutragen ist nichts.",
"MQTT.ABO_V2": "<b>MQTT&#8209;Gateway V2 erkennt die Themengruppe von selbst</b> — einzutragen ist hier nichts. In den <i>Subscriptions</i> erscheint die Gruppe; dort werden die gewünschten Datenpunkte einzeln angehakt. Erscheint sie nicht, hat noch nichts veröffentlicht.",
"WACHE.FALSCH": "Das Formularmerkmal war ungültig - vermutlich ist die Sitzung abgelaufen. Bitte die Seite neu laden.",
"WACHE.FEHLT": "Die Anfrage trug kein Formularmerkmal und wurde abgewiesen. Bitte die Seite neu laden und den Vorgang wiederholen.",
    # ---- Nachgetragen 19.09.2026 aus der ausgelieferten language_de.ini --------
    # Diese Schluessel standen nur dort; der Erzeuger verweigerte deshalb das
    # Schreiben (Rueckgabe 1). Die Ausgabe sortiert je Abschnitt selbst, die
    # Stelle im Quelltext ist also ohne Wirkung auf die .ini.
    "TEST.A_KONFIG_AUS_ZWEITSCHRIFT": "sie war leer und wurde aus der Zweitschrift zurückgeholt. Beim Update ist das der Regelfall.",
    "TEST.A_KONFIG_KAPUTT_GEHEILT": "nein — sie war unlesbar und wurde aus der Zweitschrift wiederhergestellt. Der vorherige Inhalt liegt als %s daneben. Bitte die Einstellungen durchsehen: die Zweitschrift kann älter sein.",
    "TEST.A_KONFIG_KAPUTT_OHNE": "nein — sie ist unlesbar, und es liegt keine brauchbare Zweitschrift daneben. Der bisherige Inhalt liegt als %s. Das Aktionstoken lässt sich nicht zurückrechnen.",
    "TEST.A_KONFIG_LEER": "sie ist leer. Das ist nach einer Neuinstallation normal.",
    "TEST.A_KONFIG_NEU": "sie gibt es noch nicht — beim ersten Speichern entsteht sie.",
    "TEST.A_KONFIG_OK": "ja, lesbar und mit Aktionstoken",
    "TEST.A_KONFIG_UNBEKANNT": "nicht feststellbar — in diesem Seitenaufbau wurde die Konfiguration nicht gelesen",
    "TEST.A_LEBENSZEICHEN_AB": "nein — eine Aussage über den Dienst geht zurückbehalten hinaus: %s",
    "TEST.A_LEBENSZEICHEN_OK": "ja — %s: als publish, nie als retain",
    "TEST.A_UPGRADE_ALT": "nein — es liegt aber noch die Marke einer früheren Aktualisierung, und sie gilt nicht mehr. Wahrscheinlich ist eine Installation abgebrochen. Der Dienst ist dadurch nicht gesperrt; die Datei data/plugins/%s kann gelöscht werden.",
    "TEST.A_UPGRADE_KEINE": "nein. Der Dienst lässt sich starten.",
    "TEST.A_UPGRADE_LAEUFT": "ja, seit %d Sekunden. Solange sie läuft, wird kein Dienst gestartet — auch nicht über die Knöpfe im Reiter Einstellungen. Die Installation startet ihn danach selbst, falls er vorher lief.",
    "TEST.F_KONFIG": "War die Konfiguration heil, als diese Seite aufgebaut wurde?",
    "TEST.F_LEBENSZEICHEN": "Gehen Lebenszeichen und Dienstzustand nie zurückbehalten hinaus?",
    "TEST.F_UPGRADE_MARKE": "Läuft gerade eine Aktualisierung dieses Plugins?",
    "WACHE.KEIN_TOKEN": "Die Konfigurationsdatei ist unlesbar, und die Zweitschrift daneben trägt noch das bisherige Aktionstoken. Es wird deshalb kein neues Aktionstoken erzeugt — das alte ließe sich nicht zurückrechnen, und alle Adressen im Miniserver wären ungültig. Bitte den Reiter Logdateien ansehen und die Konfiguration wiederherstellen; danach wirkt auch der Knopf für ein neues Token wieder.",
# ---- Durchgangsbau 02.10.2026 (weissware_BAULISTE.md, vb_ww): PRG, X-2, Nr. 19,
# Ausgabearten Alexa-NG und Google-Lautsprecher, MQTT-Praefixe, Geraete-ok ----
"ALLG.EINMAL_FEHLER": "Die Rückmeldung ließ sich nicht im Datenordner ablegen (%s) – sie steht deshalb nur auf dieser Seite, und ein Neuladen würde die Aktion wiederholen.",
"EINST.N_HC_ID": "Home Connect: Client-ID",
"EINST.N_HC_SECRET": "Home Connect: Client Secret",
"EINST.N_MIELE_ID": "Miele: Client-ID",
"EINST.N_MIELE_SECRET": "Miele: Client Secret",
"EINST.N_ST_TOKEN": "SmartThings: Personal Access Token",
"EINST.FEHLER_ZEICHEN": "%s enthält Steuerzeichen, ist kein gültiges UTF-8 oder ist länger als 512 Zeichen. Bitte so eintragen, wie das Entwicklerportal es anzeigt; es wurde nichts herausgeschnitten und nichts gespeichert.",
"EINST.FEHLER_MIELE_ABLAGE": "Der Miele-Code ließ sich nicht im Datenordner ablegen (%s) – er wird nie über die Befehlszeile gereicht, deshalb wurde nicht angemeldet.",
"EINST.L_SITZUNG_OK": "Ja, Anmeldemarken löschen",
"EINST.SITZUNG_ERKLAERUNG": "<i>Anmeldung neu erzwingen</i> löscht die Anmeldemarken von Home Connect und Miele – nur mit dem Haken darunter. Danach meldet sich der Dienst nicht von selbst an: die Anmeldung geschieht wieder im Browser, Abschnitt <i>Anmeldung</i> weiter unten. Zugangsdaten und Einstellungen bleiben.",
"EINST.SITZUNG_OHNE_HAKEN": "Die Anmeldemarken wurden nicht gelöscht: bitte vorher den Haken „Ja, Anmeldemarken löschen“ setzen.",
"EINST.SITZUNG_FEHLER": "Die Anmeldemarken ließen sich nicht löschen (%s) – Schreibrecht im Datenordner prüfen.",
"EINST.SICH_SPRECHTOKEN": "Die Datei enthält ein Sprechtoken (%s). Sicherungen tragen es nie – die Datei wird nicht übernommen. Das Token tragen Sie im Reiter Einstellungen ein.",
"EINST.SICH_TOKEN_LEER": "Die Datei trägt ein leeres Aktionstoken – das geltende Token bleibt, die Adressen im Miniserver gelten weiter.",
"EINST.SICH_WARN_STAND": "Diese gespeicherten Werte würden beim Zurückspielen abgewiesen: %s. Die Sicherung enthält sie trotzdem vollständig und nennt sie unter _warnung – bitte vorher in den Einstellungen berichtigen und speichern.",
"MQTT.PRAEFIX_VORGEMERKT": "Das bisherige Präfix %s ist vorgemerkt: der Dienst räumt die dort zurückbehaltenen Themen ab (mit Nachlesen beim Broker), und die Deinstallation leert es mit.",
"MQTT.AUS_RAEUMEN": "MQTT ist aus: der Dienst räumt die zurückbehaltenen Themen unter %s einmal ab, sobald er läuft (mit Nachlesen beim Broker).",
"MQTT.ALT_LISTE": "Vorgemerkte frühere Präfixe (werden abgeräumt): %s",
"LOG.LEEREN_FEHLER": "Die Logdatei ließ sich nicht leeren: %s",
"WW_MQTT.GERAET_OK": "1 = der Anbieter dieses Geräts hat im letzten Lauf geantwortet; 0 = er schweigt, die Zustände sind die zuletzt gemessenen. Nie zurückbehalten.",
"WW_MQTT.GERAET_TS": "Zeitpunkt, zu dem dieses Gerät zuletzt gelesen wurde (Unixzeit). Nie zurückbehalten.",

# ---- Welle Bild 16 (Weissware 0.9.42, 17.10.2026; Entwurf Welle 16 ww, E3/E4/E10-E12): drei Seiten aus
# dem LoxBerry-Plugins Musterprojekt - Kasten- und Hinweistitel, Kaesten BAUSTEIN.Sn_SCHRITTm, Hinweise
# BAUSTEIN.Sn_Hm, Tabellenzeilen BAUSTEIN.Zn_mm = "Typ | Name | Parameter | Eingaenge" (ww_bausteinseiten()
# in htmlauth/index.php); LOX: Bild, Link, Vorlage "Weissware Dienst", Kommentare der Impulsbefehle
# (ww_vorlage_ausgang()); WW_DFELD: Kommentare der Dienst-Werte (ww_dienst_felder()). -----------------
"BAUSTEIN.SCHRITTE_TITEL": "So übernehmen Sie diese Seite",
"BAUSTEIN.HINWEISE_TITEL": "Hinweise",
"BAUSTEIN.S1_SCHRITT1": "Im Plugin Reiter „%s“ den Hersteller anmelden (Home Connect, Miele oder SmartThings), Dienst starten und warten, bis unter „%s“ das Gerät steht. Reiter „%s“ → „%s“: es kommt eine Zeile WEISSWARE;OK=1;ZUSTAND=…",
"BAUSTEIN.S1_SCHRITT2": "Reiter „%s“ → bei „Vorlagen für Gerät 1“ den Knopf „%s“. In Loxone Config: im Baum „Virtuelle Eingänge“ wählen, Menüband „Vordefinierte HTTP-Geräte → Vorlage importieren…“. Nur EINMAL einlesen (zweimal ergibt doppelte Eingänge). Erst holen, wenn das Gerät einmal geantwortet hat – dann enthält die Datei nur, was es wirklich liefert.",
"BAUSTEIN.S1_SCHRITT3": "Seite „Weissware“ anlegen, aus dem Behälter „Weissware 1 Status“ alle Befehle ziehen (Nr. 1–15), dazu die Konstante 1.",
"BAUSTEIN.S1_SCHRITT4": "Vier Benachrichtigungen anlegen (Peripherie → Mitteilungen → Benachrichtigung), Texte wie in der Liste, auf die Seite ziehen. Jede bekommt genau eine Leitung.",
"BAUSTEIN.S1_SCHRITT5": "Übrige Bausteine über die Baustein-Suche (Taste F5) setzen, Parameter wie in der Liste, von oben nach unten verbinden. An der Analogwertvalidierung Nr. 17 den Haken bei ‚En‘ im Eigenschaftsfenster entfernen (Config legt En negiert an; sonst kommt die Konstante 1 als 0 an). Status „WW 1 Gerät“: vorher viermal „+“ klicken (V5–V8); die Zeilen der Status-Bausteine in der angegebenen Reihenfolge eintragen, die ohne Bedingung zuletzt. „In Visualisierung verwenden“ an Nr. 1, 2, 3, 7 und an beiden Status.",
"BAUSTEIN.S1_SCHRITT6": "Speichern und übertragen. Probe: „Weissware-Zustand“ zeigt „läuft – Werte … s alt“, „WW 1 Gerät“ den Zustand der Maschine.",
"BAUSTEIN.S1_H1": "Die Störungsmeldung kommt frühestens nach 5 Minuten; „Abruf steht“ (LoxBerry aus) nach 10 Minuten plus 5.",
"BAUSTEIN.S1_H2": "Zu Nr. 17: steht der LoxBerry, behalten alle Eingänge ihren letzten Wert; nur das stehende ALTER verrät es. Wer die Abfragezeit am Behälter verlängert, setzt Tmc auf das Zehnfache.",
"BAUSTEIN.S1_H3": "Zu Nr. 18, 25 und 27: digitale Eingänge gehen ohne Schwellwertschalter weiter – ein Schwellwertschalter hinter einem abgefragten Eingang gibt bei jeder Abfrage einen kurzen Impuls, eine Benachrichtigung dahinter meldet dann jede Minute.",
"BAUSTEIN.S1_H4": "Mehrere Geräte: je Gerät eine eigene Status-Vorlage („Weissware 2 Status“ …) und dieselben Bausteine; die Störungen über weitere ODER (je zwei Eingänge) vor Nr. 20 führen – nie mehrere Quellen direkt an eine Benachrichtigung.",
"BAUSTEIN.S1_H5": "„Fertig“ bleibt stehen, bis das Gerät ausgeräumt (Tür geöffnet) ist; deshalb kommt nach einer Stunde die Erinnerung.",
"BAUSTEIN.S1_H6": "Ein Strich vom Plugin heißt „liefert der Hersteller nicht“ – der Eingang behält dann seinen letzten Wert.",
"BAUSTEIN.S1_H7": "Nr. 11 (Fernbedienung) und Nr. 15 (Fertig um) stehen nur als Eingänge da: nicht jeder Hersteller liefert die Fernbedienung, und ein Status zeigt „Fertig um“ nicht als Uhrzeit. Programmname und Zustandstext gibt es nur über MQTT.",
"BAUSTEIN.S1_H8": "Die Ansage „… ist fertig“ über Lautsprecher macht das Plugin selbst (Reiter Einstellungen, ab Werk an) – kein Baustein.",
"BAUSTEIN.S2_SCHRITT1": "Im Plugin Reiter „%s“ den Haken „%s“ setzen und speichern.",
"BAUSTEIN.S2_SCHRITT2": "Reiter „%s“ → „%s“. In Loxone Config: Baum „Virtuelle Ausgänge“ → „Vordefinierte Geräte → Vorlage importieren…“. Nur einmal einlesen; die Vorlage trägt auch die Befehle der Seite „Weissware Steuerung und Verbrauch“.",
"BAUSTEIN.S2_SCHRITT3": "Die eigenen Messwerte bereitstellen: „Netzleistung (eigene Quelle)“ aus dem eigenen Stromzähler (plus = Bezug, minus = Einspeisung), mit Hausakku „Ladeleistung Speicher 1 (eigene Quelle)“ und „Ladezustand Speicher 1 (Proz) (eigene Quelle)“; mit dynamischem Tarif spot_awattar_rank – Virtuellen Eingang mit dem Namen aus der Namenstabelle im Reiter ‚Einbindung in Loxone‘ des Plugins Spotpreis aWATTar (ab 1.2.38) anlegen. Was es nicht gibt, bleibt frei – der Grund fällt dann einfach weg.",
"BAUSTEIN.S2_SCHRITT4": "Seite „Weissware PV-Start“ anlegen, die Bausteine der Liste ziehen bzw. über die Baustein-Suche (Taste F5) setzen und verbinden; jedes UND und ODER hat zwei Eingänge. Neu anlegen: die Schalter Nr. 14 und 21 und die Taste Nr. 23 als Virtuelle Eingänge (je „In Visualisierung verwenden“ an) und die Benachrichtigung „Meldung Weissware gestartet“. Schaltuhr Nr. 19: täglich 08:00–20:00 EIN eintragen. UND Nr. 26: den Eingang I2 negieren – in Config auf seinen Eingangspunkt klicken, danach zeigt er einen kleinen Kreis. Status „Weissware-Automatik jetzt“: vorher viermal „+“ klicken (V5–V8).",
"BAUSTEIN.S2_SCHRITT5": "Speichern, übertragen, in der App „Weissware-Automatik“ einschalten (und, wenn gewünscht, „Günstigen Strom zum Waschen nutzen“).",
"BAUSTEIN.S2_SCHRITT6": "So wird gewaschen: Maschine füllen, Programm wählen, am Gerät „Fernstart“ drücken, gehen. Die Seite startet, sobald 10 Minuten lang genug Überschuss da ist (oder der Hausakku über 60 Prozent steht oder eine der vier günstigsten Stunden läuft) – nur zwischen 8 und 20 Uhr.",
"BAUSTEIN.S2_H1": "Ohne Fernstart-Freigabe am Gerät startet nichts; die Freigabe erlischt meist mit dem Programm und muss jedes Mal neu gegeben werden. Deshalb startet die Automatik nach dem Programmende kein zweites Mal.",
"BAUSTEIN.S2_H2": "Zu Nr. 28 und 29: ein Impuls je Freigabe. „WW 1 Start (Befehl)“ hat nur einen Einbefehl – „WW 1 Programm (Befehl)“ sendet beim Abfallen „stop“ und bräche das eben gestartete Programm wieder ab.",
"BAUSTEIN.S2_H3": "„Weissware jetzt starten“ (Taste) startet sofort, auch ohne Automatik – aber ebenfalls nur mit Fernstart-Freigabe.",
"BAUSTEIN.S2_H4": "Zu Nr. 6: Überschuss = Einspeisung plus Ladeleistung des Hausakkus. Schwelle 2000 W an die eigene Maschine anpassen (Nr. 7); bezieht das Haus Strom, ist der Überschuss 0.",
"BAUSTEIN.S2_H5": "Ein voller Hausakku ist ein weiterer Grund zu starten – die Maschine läuft dann aus dem Akku. Mit Spotpreis Octopus oder Tibber kommt Nr. 10 vom Rang-Befehl jener Vorlage.",
"BAUSTEIN.S2_H6": "Nr. 1 bis 3 sind digitale Eingänge und gehen ohne Schwellwertschalter in die UND-Kette.",
"BAUSTEIN.S2_H7": "Ob das Gerät wirklich anläuft, zeigt „WW 1 Läuft“ nach dem nächsten Abruf, nicht die Antwort auf den Befehl.",
"BAUSTEIN.S3_SCHRITT1": "Die Befehlsvorlage kommt von der Seite „Weissware PV-Start“, Schritt 2 (nicht erneut einlesen). Reiter „%s“ → „%s“ und „%s“ holen und in Loxone Config einlesen: im Baum „Virtuelle Eingänge“ wählen, Menüband „Vordefinierte HTTP-Geräte → Vorlage importieren…“. Die Dienst-Werte gelten für alle Geräte zusammen und werden nur einmal eingelesen.",
"BAUSTEIN.S3_SCHRITT2": "Seite „Weissware Steuerung und Verbrauch“ anlegen, die vier Befehle (Nr. 2, 4, 6, 8) und die Eingänge ziehen, die vier App-Knöpfe als Virtuelle Eingänge anlegen (Taste oder Schalter wie in der Liste, je „In Visualisierung verwenden“ an), verbinden. An beiden Status vorher einmal „+“ klicken (V5).",
"BAUSTEIN.S3_SCHRITT3": "Speichern und übertragen. Probe: „Weissware sofort abrufen“ drücken – „WW 1 Alter“ fällt nach der nächsten Abfrage.",
"BAUSTEIN.S3_H1": "„Anhalten“ und „Ein/Aus“ verlangen am Gerät meist die Fernbedienungs-Freigabe; ohne sie weist die Hersteller-Cloud ab.",
"BAUSTEIN.S3_H2": "Der Schalter merkt sich nicht, was am Gerät von Hand gedrückt wurde – er zeigt den letzten Wunsch aus Loxone.",
"BAUSTEIN.S3_H3": "Home Connect liefert weder Energie noch Wasser, SmartThings kein Wasser; Miele beides nur bei Geräten mit EcoFeedback.",
"BAUSTEIN.S3_H4": "„WW Dienst OK“ und „WW Dienst Alter“ aus der Vorlage „Weissware Dienst“ bleiben im Baum; die Seite „Weissware“ überwacht den Abruf schon je Gerät.",
"BAUSTEIN.Z1_01": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 Zustand | 0 aus, 1 bereit, 2 läuft, 3 angehalten, 4 fertig (noch nicht ausgeräumt), 5 Störung | —",
"BAUSTEIN.Z1_02": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 Läuft | 1 = ein Programm läuft | —",
"BAUSTEIN.Z1_03": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 Fertig | 1 = Programm beendet, Gerät noch nicht ausgeräumt | —",
"BAUSTEIN.Z1_04": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 Verbunden | 1 = Gerät für die Hersteller-Cloud erreichbar | —",
"BAUSTEIN.Z1_05": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 Tür | 1 = Tür offen | —",
"BAUSTEIN.Z1_06": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 Fortschritt | Fortschritt des Programms in % (SmartThings liefert keinen) | —",
"BAUSTEIN.Z1_07": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 Restzeit | Restzeit bis Programmende in min | —",
"BAUSTEIN.Z1_08": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 Startvorwahl | Minuten bis zum Start, wenn am Gerät eine Startvorwahl läuft | —",
"BAUSTEIN.Z1_09": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 Laufzeit | bisherige Laufzeit des Programms in min | —",
"BAUSTEIN.Z1_10": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 Fernstart | 1 = am Gerät ist der Fernstart freigegeben (erlischt meist mit dem Programmende) | —",
"BAUSTEIN.Z1_11": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 Fernbedienung | 1 = Fernbedienung erlaubt (nur Anzeige; nicht jeder Hersteller liefert den Wert) | —",
"BAUSTEIN.Z1_12": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 Netz | 1 = Gerät eingeschaltet | —",
"BAUSTEIN.Z1_13": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 Alter | Sekunden seit dem letzten erfolgreichen Abruf | —",
"BAUSTEIN.Z1_14": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 OK | 1 = letzter Abruf gelungen und höchstens 15 Minuten alt; 0 auch, wenn die Hersteller-Cloud dieses Geräts schweigt | —",
"BAUSTEIN.Z1_15": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 Fertig um | voraussichtliches Programmende als Unixzeit, nur während eines Laufs; für eigene Logik (minus 1230768000 = Loxone-Zeit) | —",
"BAUSTEIN.Z1_16": "Konstante | Konstante 1 | Wert 1 | —",
"BAUSTEIN.Z1_17": "Analogwertvalidierung | Abruf steht | Tmc 600 s (zehn Abfragen à 60 s), Min -1, Max 2147483647; Haken bei ‚En‘ im Eigenschaftsfenster entfernen | V = #13, En = #16",
"BAUSTEIN.Z1_18": "NICHT | Weissware ohne frische Werte | — | I = #14",
"BAUSTEIN.Z1_19": "ODER | Störung Weissware | — (keine frischen Werte oder Abruf steht) | I1 = #18, I2 = Ausgang E von #17",
"BAUSTEIN.Z1_20": "Einschaltverzögerung | Störung Weissware bestätigt | 300 s | Eingang = #19",
"BAUSTEIN.Z1_21": "Benachrichtigung | Meldung Weissware Störung | Text: Weissware – seit 5 Minuten keine frischen Werte vom Hausgerät (LoxBerry, Plugin oder Hersteller-Cloud antwortet nicht). In der App den Status „Weissware-Zustand“ lesen | Eingang = #20",
"BAUSTEIN.Z1_22": "Gleich | Gerät meldet Störung | V2 = 5 (zweiten Eingang offen lassen) | I1 = #1",
"BAUSTEIN.Z1_23": "Einschaltverzögerung | Gerätestörung bestätigt | 120 s (zwei Abfragen) | Eingang = #22",
"BAUSTEIN.Z1_24": "Benachrichtigung | Meldung Weissware Gerätestörung | Text: Weissware – das Hausgerät meldet eine Störung. Am Gerät oder in der Hersteller-App nachsehen | Eingang = #23",
"BAUSTEIN.Z1_25": "Einschaltverzögerung | Fertig bestätigt | 60 s (eine Abfrage) | Eingang = #3",
"BAUSTEIN.Z1_26": "Benachrichtigung | Meldung Weissware fertig | Text: Weissware – das Programm ist fertig, bitte ausräumen | Eingang = #25",
"BAUSTEIN.Z1_27": "Einschaltverzögerung | Fertig, noch nicht ausgeräumt | 3600 s | Eingang = #3",
"BAUSTEIN.Z1_28": "Benachrichtigung | Erinnerung Weissware ausräumen | Text: Weissware – das Programm ist seit einer Stunde fertig und das Gerät noch nicht ausgeräumt | Eingang = #27",
"BAUSTEIN.Z1_29": "Status | Weissware-Zustand | Zeilen: V3 = 1 „Abruf steht seit mindestens 10 Minuten – LoxBerry oder Plugin antwortet nicht; LoxBerry im Browser öffnen, im Plugin Reiter Test ‚Status abrufen‘“; V1 = 0 „keine frischen Werte, letzter erfolgreicher Abruf vor <v2> s – im Plugin Reiter Einstellungen Anmeldung und Abrufdienst prüfen, Reiter Test ‚Selbsttest des Dienstes‘“; V4 = 0 „Gerät für die Hersteller-Cloud nicht erreichbar – Gerät einschalten, WLAN des Geräts in der Hersteller-App prüfen“; ohne Bedingung „läuft – Werte <v2> s alt“; Visualisierung EIN | V1 = #14, V2 = #13, V3 = Ausgang E von #17, V4 = #4",
"BAUSTEIN.Z1_30": "Status | WW 1 Gerät | Zeilen: V1 = 5 „Störung – am Gerät oder in der Hersteller-App nachsehen“; V1 = 2 „läuft – noch <v3> min, <v2> % (seit <v5> min)“; V1 = 3 „angehalten – noch <v3> min“; V1 = 4 „fertig – bitte ausräumen“; V1 = 1 und V4 > 0 „Startvorwahl – startet in <v4> min“; V6 = 1 „Tür offen“; V1 = 1 und V7 = 1 „bereit – Fernstart freigegeben, Loxone darf starten“; V1 = 1 „bereit – für einen Start aus Loxone am Gerät Programm wählen und ‚Fernstart‘ drücken“; V1 = 0 und V8 = 1 „eingeschaltet, kein Programm“; V1 = 0 „aus“; ohne Bedingung „kein Zustand bekannt“; Visualisierung EIN | V1 = #1, V2 = #6, V3 = #7, V4 = #8, V5 = #9, V6 = #5, V7 = #10, V8 = #12",
"BAUSTEIN.Z2_01": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 Läuft | 1 = ein Programm läuft (weitere Instanz, auch auf Seite „Weissware“) | —",
"BAUSTEIN.Z2_02": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 Fernstart | 1 = Fernstart am Gerät freigegeben (weitere Instanz) | —",
"BAUSTEIN.Z2_03": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Status“) | WW 1 OK | 1 = Werte frisch (weitere Instanz) | —",
"BAUSTEIN.Z2_04": "Virtueller Eingang | Netzleistung (eigene Quelle) | Leistung am eigenen Stromzähler in W, plus = Bezug, minus = Einspeisung; derselbe Eingang wie auf „AnkerSolix Steuerung“ | —",
"BAUSTEIN.Z2_05": "Virtueller Eingang | Ladeleistung Speicher 1 (eigene Quelle) | Ladeleistung in W, plus = lädt, minus = entlädt; derselbe Eingang wie auf „Einspeisebremse Speicher“; ohne Speicher frei lassen | —",
"BAUSTEIN.Z2_06": "Formel | PV-Überschuss (W) | MAX(0;MAX(0;I2)-I1) – Einspeisung plus das, was der Hausakku gerade lädt; 0 bei Netzbezug | I1 = #4, I2 = #5",
"BAUSTEIN.Z2_07": "Schwellwertschalter | PV-Überschuss reicht | Ein 2000 / Aus 1500 (W; Waschmaschine etwa 2000 W, Geschirrspüler etwa 2200 W beim Aufheizen – an die eigene Maschine anpassen) | Eingang = #6",
"BAUSTEIN.Z2_08": "Virtueller Eingang | Ladezustand Speicher 1 (Proz) (eigene Quelle) | Ladezustand in %; derselbe Eingang wie auf „Einspeisebremse Speicher“; ohne Speicher frei lassen (bleibt 0, zählt nie als voll) | —",
"BAUSTEIN.Z2_09": "Schwellwertschalter | Hausakku voll genug | Ein 60 / Aus 40 (%) | Eingang = #8",
"BAUSTEIN.Z2_10": "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Spotpreis aWATTar) | spot_awattar_rank | Rang der aktuellen Stunde in den nächsten 24 h, 1 = günstigste, -1 = kein Rang (weitere Instanz aus dem Plugin Spotpreis aWATTar); ohne Spotpreis-Plugin frei lassen (dann nie günstig) | —",
"BAUSTEIN.Z2_11": "Größer | Preisrang bekannt | V2 = 0 (zweiten Eingang offen lassen) | I1 = #10",
"BAUSTEIN.Z2_12": "Kleiner oder gleich | Günstige Stunde zum Waschen | V2 = 4 (zweiten Eingang offen lassen; die vier günstigsten Stunden der nächsten 24 h) | I1 = #10",
"BAUSTEIN.Z2_13": "UND | Strom günstig zum Waschen | — | I1 = #11, I2 = #12",
"BAUSTEIN.Z2_14": "Virtueller Eingang (Schalter) | Günstigen Strom zum Waschen nutzen | in der App; ab Werk aus | —",
"BAUSTEIN.Z2_15": "UND | Günstig waschen gewünscht | — | I1 = #13, I2 = #14",
"BAUSTEIN.Z2_16": "ODER | Akku oder günstiger Strom | — | I1 = #9, I2 = #15",
"BAUSTEIN.Z2_17": "ODER | Waschen jetzt sinnvoll | — (Überschuss, voller Akku oder günstiger Strom) | I1 = #7, I2 = #16",
"BAUSTEIN.Z2_18": "Einschaltverzögerung | Grund hält an | 600 s (eine vorbeiziehende Wolke startet kein Programm) | Eingang = #17",
"BAUSTEIN.Z2_19": "Schaltuhr | Startfenster Weissware | EIN = Start erlaubt: täglich 08:00–20:00, in allen Betriebsarten (nachts nicht schleudern) | —",
"BAUSTEIN.Z2_20": "UND | Grund im Startfenster | — | I1 = #18, I2 = Ausgang AQ von #19",
"BAUSTEIN.Z2_21": "Virtueller Eingang (Schalter) | Weissware-Automatik | in der App; ab Werk aus | —",
"BAUSTEIN.Z2_22": "UND | Automatik will starten | — | I1 = #20, I2 = #21",
"BAUSTEIN.Z2_23": "Virtueller Eingang (Taste) | Weissware jetzt starten | in der App; startet das am Gerät gewählte Programm sofort (auch ohne Automatik) | —",
"BAUSTEIN.Z2_24": "ODER | Startwunsch | — (Automatik oder Taste) | I1 = #22, I2 = #23",
"BAUSTEIN.Z2_25": "UND | Fernstart frei | — (ohne Freigabe weist die Hersteller-Cloud jeden Start ab) | I1 = #24, I2 = #2",
"BAUSTEIN.Z2_26": "UND | Gerät steht still | — | I1 = #25, I2 = #1 (negiert)",
"BAUSTEIN.Z2_27": "UND | Start freigegeben | — (nur mit frischen Werten) | I1 = #26, I2 = #3",
"BAUSTEIN.Z2_28": "Flankenerkennung | Startimpuls | Pd 1 s; einmal je Freigabe, kein Wiederholen im Takt | Eingang = #27",
"BAUSTEIN.Z2_29": "Virtueller Ausgang Befehl (Vorlage „Weissware 1 Befehle“) | WW 1 Start (Befehl) | startet das am Gerät gewählte Programm; nur Einbefehl; schreibende Befehle im Plugin freigeben | Eingang = Ausgang On von #28",
"BAUSTEIN.Z2_30": "UND | Läuft mit Automatik | — | I1 = #1, I2 = #21",
"BAUSTEIN.Z2_31": "Benachrichtigung | Meldung Weissware gestartet | Text: Weissware – das Gerät läuft; die Automatik ist an (Sonnenstrom, voller Hausakku oder günstiger Strom) | Eingang = #30",
"BAUSTEIN.Z2_32": "Status | Weissware-Automatik jetzt | Zeilen: V6 = 1 „läuft“; V1 = 0 „Automatik aus – Überschuss jetzt <v7> W, Preisrang <v8>“; V2 = 1 „Startbefehl gesendet – ob das Gerät anläuft, zeigt der nächste Abruf“; V3 = 1 und V4 = 0 „Grund da (Überschuss, Akku oder günstiger Strom), aber außerhalb des Startfensters 8–20 Uhr“; V3 = 1 und V5 = 0 „Grund da, aber keine Fernstart-Freigabe – am Gerät Programm wählen und ‚Fernstart‘ drücken“; V5 = 0 „wartet – am Gerät ist noch kein Fernstart freigegeben; Überschuss <v7> W“; ohne Bedingung „wartet auf Überschuss (jetzt <v7> W, nötig 2000 W für 10 Minuten), vollen Hausakku oder günstigen Strom (Rang <v8>)“; Visualisierung EIN | V1 = #21, V2 = #27, V3 = #18, V4 = Ausgang AQ von #19, V5 = #2, V6 = #1, V7 = #6, V8 = #10",
"BAUSTEIN.Z3_01": "Virtueller Eingang (Taste) | Weissware abbrechen | in der App | —",
"BAUSTEIN.Z3_02": "Virtueller Ausgang Befehl (Vorlage „Weissware 1 Befehle“) | WW 1 Abbrechen (Befehl) | bricht das laufende Programm ab; nur Einbefehl | Eingang = #1",
"BAUSTEIN.Z3_03": "Virtueller Eingang (Schalter) | Weissware anhalten | in der App; Ein = anhalten, Aus = fortsetzen; ab Werk aus | —",
"BAUSTEIN.Z3_04": "Virtueller Ausgang Befehl (Vorlage „Weissware 1 Befehle“) | WW 1 Pause (Befehl) | Ein = anhalten, Aus = fortsetzen (folgt dem Schalter) | Eingang = #3",
"BAUSTEIN.Z3_05": "Virtueller Eingang (Schalter) | Weissware Strom | in der App; Ein = Gerät einschalten, Aus = ausschalten | —",
"BAUSTEIN.Z3_06": "Virtueller Ausgang Befehl (Vorlage „Weissware 1 Befehle“) | WW 1 Ein/Aus (Befehl) | Ein = einschalten, Aus = ausschalten; gleicher Befehl binnen 60 s wird nicht wiederholt | Eingang = #5",
"BAUSTEIN.Z3_07": "Virtueller Eingang (Taste) | Weissware sofort abrufen | in der App | —",
"BAUSTEIN.Z3_08": "Virtueller Ausgang Befehl (Vorlage „Weissware 1 Befehle“) | WW Sofort abrufen (Befehl) | holt sofort neue Werte statt auf den Takt zu warten; gilt für alle Geräte | Eingang = #7",
"BAUSTEIN.Z3_09": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Verbrauch“) | WW 1 Energie | Energieverbrauch des laufenden Programms in kWh (Home Connect liefert keinen) | —",
"BAUSTEIN.Z3_10": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Verbrauch“) | WW 1 Wasser | Wasserverbrauch des laufenden Programms in l (Home Connect und SmartThings liefern keinen) | —",
"BAUSTEIN.Z3_11": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Verbrauch“) | WW 1 Temperatur | eingestellte Temperatur in °C | —",
"BAUSTEIN.Z3_12": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Verbrauch“) | WW 1 Schleuderdrehzahl | eingestellte Schleuderdrehzahl in U/min | —",
"BAUSTEIN.Z3_13": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware 1 Verbrauch“) | WW 1 OK (Verbrauch) | 1 = Verbrauchswerte frisch | —",
"BAUSTEIN.Z3_14": "Status | WW 1 Programm und Verbrauch | Zeilen: V5 = 0 „keine frischen Verbrauchswerte – Status ‚Weissware-Zustand‘ lesen“; ohne Bedingung „<v3> °C, <v4> U/min; bisher <v1.2> kWh und <v2> l (was die Hersteller-Cloud nicht liefert, bleibt stehen)“; Visualisierung EIN | V1 = #9, V2 = #10, V3 = #11, V4 = #12, V5 = #13",
"BAUSTEIN.Z3_15": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware Dienst“) | WW Geräte | Zahl der erkannten Geräte | —",
"BAUSTEIN.Z3_16": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware Dienst“) | WW Geräte laufen | Zahl der Geräte, in denen ein Programm läuft | —",
"BAUSTEIN.Z3_17": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware Dienst“) | WW Geräte fertig | Zahl der Geräte, die fertig sind und noch nicht ausgeräumt | —",
"BAUSTEIN.Z3_18": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware Dienst“) | WW Fehlversuche | fehlgeschlagene Abrufe in Folge; 0 = der letzte saß | —",
"BAUSTEIN.Z3_19": "Virtueller HTTP-Eingang-Befehl (Vorlage „Weissware Dienst“) | WW Anbieter still | Zahl der Hersteller-Clouds, die beim letzten Abruf nicht geantwortet haben | —",
"BAUSTEIN.Z3_20": "Status | Weissware-Dienst | Zeilen: V4 >= 5 „<v4> Abrufe in Folge gescheitert – das Plugin bremst; im Plugin Reiter Logdateien lesen“; V5 > 0 „<v5> Hersteller-Cloud(s) antworten nicht – im Plugin Reiter Einstellungen die Anmeldung prüfen“; V4 > 0 „letzter Abruf gescheitert (<v4>-mal in Folge)“; V2 > 0 „<v2> von <v1> Geräten laufen, <v3> fertig“; ohne Bedingung „<v1> Geräte, keines läuft, <v3> fertig“; Visualisierung EIN | V1 = #15, V2 = #16, V3 = #17, V4 = #18, V5 = #19",
"LOX.BILD_ALT": "Bausteine des Plugins in Loxone Config",
"LOX.BILD_UNTERSCHRIFT": "Seite „%s“ im LoxBerry-Plugins Musterprojekt. Config kürzt lange Bausteinnamen – Namen siehe Tabelle.",
"LOX.MUSTERPROJEKT": "Die ganze Projektdatei mit allen Plugin-Seiten und Vorlagen: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry-Plugins Musterprojekt</a>",
"LOX.VORLAGEN_DIENST": "Vorlage für die Sammelwerte des Dienstes (alle Geräte zusammen)",
"LOX.K_VORLAGE_DIENST": "Dienst-Werte als Vorlage",
"LOX.VA_START": "Startet das am Gerät gewählte Programm. Abgewiesen, solange am Gerät kein Fernstart freigegeben ist.",
"LOX.VA_STOP": "Bricht das laufende Programm ab.",
"WW_DFELD.LAEUFT": "Anzahl der Geräte, in denen ein Programm läuft",
"WW_DFELD.FERTIG": "Anzahl der Geräte, die fertig und noch nicht ausgeräumt sind",
"WW_DFELD.FEHLERFOLGE": "Fehlgeschlagene Abrufe in Folge. 0 heißt: der letzte saß.",
"WW_DFELD.AUSFAELLE": "Zahl der Hersteller-Clouds, die beim letzten Abruf nicht geantwortet haben",
"WW_DFELD.ALTER": "Alter des Abbilds",
}

# ---------------------------------------------------------------------------
# Englisch - Rueckfallebene, muss vollstaendig sein
# ---------------------------------------------------------------------------
EN = {

"REITER.EINSTELLUNGEN": "Settings",
"REITER.LOXONE": "Loxone integration",
"REITER.TEST": "Test",
"REITER.LOG": "Log files",

"LEGENDE.LESEN": "View — reads only, changes nothing",
"LEGENDE.TECHNIK": "Technical information — for troubleshooting",
"LEGENDE.AKTION": "Triggers something — sends or changes",
"LEGENDE.AKTION_TOKEN": "Triggers something — a new token invalidates every address in the Miniserver",
"LEGENDE.AKTION_LOG": "Triggers something — the existing lines will be gone",

"ALLG.BEANSTANDUNG": "Nothing was saved. Please correct these points:",
"ALLG.MISSLUNGEN": "The action did not succeed:",
"ALLG.DIENST": "Polling service",
"ALLG.LAEUFT": "running",
"ALLG.GESTOPPT": "stopped",
"ALLG.KEINE_PID": "no process id",
"ALLG.LETZTER_ABRUF": "Last poll",
"ALLG.NIE": "never",
"ALLG.KACHEL_MQTT_HILFE": "Publishing by this plugin; gateway autostart: %s",
"ALLG.NICHT_FESTSTELLBAR": "not determinable",
"ALLG.EIN": "on",
"ALLG.AUS": "off",
"ALLG.JA": "yes",
"ALLG.NEIN": "no",
"ALLG.OHNE_NAMEN": "unnamed",
"ALLG.LETZTE_STOERUNG": "Last fault:",
"ALLG.AUSFAELLE": "Providers that did not answer:",
"ALLG.EIGENSCHAFT": "Property",
"ALLG.WERT": "Value",
"ALLG.SEKUNDEN": "seconds",
"ALLG.SPEICHERN": "Save",

# Kopf wie alle Hausplugins (Entscheidung Nr. 43, 0.9.40): gruener Kasten oben im
# Reiter Einstellungen, roh ausgegeben (ww_t ohne ww_e).
"EINST.WAS_IST_DAS": "<b>Connects networked home appliances of three ecosystems to Loxone and brings them onto one common model</b> – Home Connect (Bosch, Siemens, Neff, Gaggenau, Constructa), Miele and Samsung SmartThings. A polling service on the LoxBerry fetches the values from the vendor clouds at the configured interval and stores them; the Miniserver reads them over MQTT or the HTTP endpoint of the plugin. Write commands to the appliances are blocked by default. On request the plugin announces through the shared speech output when an appliance has finished (off by default).",
"EINST.H_DIENST": "Polling service",
"EINST.DIENST_ERKLAERUNG": "The service fetches values from the enabled providers at the configured interval and stores them. The user interface and the Miniserver only read what has been stored — they never talk to the provider themselves.",
"EINST.K_START": "Start service",
"EINST.K_NEUSTART": "Restart service",
"EINST.K_STOPP": "Stop service",
"EINST.K_SITZUNG": "Force a new login",
"EINST.DIENST_START": "Service started:",
"EINST.DIENST_STOP": "Service stopped:",
"EINST.DIENST_RESTART": "Service restarted:",
"EINST.SITZUNG_VERWORFEN": "The sign-in tokens of Home Connect and Miele were deleted. The service does NOT sign in again by itself: sign in again in the “Sign-in” section below – Home Connect with the code in the browser (device flow), Miele with the sign-in address and the code from the address bar. Credentials and settings are unchanged.",
"EINST.SITZUNG_KEINE": "No authentication tokens were stored.",
"EINST.PYTHON_ZU_ALT": "<b>The service cannot run.</b> This plugin's Python virtual environment uses a Python older than 3.9, but the requests library requires 3.9 or newer. This should not happen on any current LoxBerry (Debian 12 ships 3.11) — if it does, the virtual environment is broken. Remedy: reinstall the plugin.",


"EINST.H_TAKT": "Polling interval",

"EINST.H_STEUERUNG": "Write commands",
"EINST.STEUERUNG_ERKLAERUNG": "<b>Disabled by default.</b> Write commands start and stop real machines in an empty house. A wash programme started by accident runs without anyone having loaded laundry; an aborted one leaves it wet in the drum. Only enable this once the read values in the Test tab look right. <b>Two safeguards remain anyway:</b> the appliance must have the remote start release — given on the appliance itself, and usually cleared after the programme — and a programme must be selected there.",
"EINST.L_STEUERUNG_EIN": "Allow write commands",
"EINST.L_WARTEZEIT": "Wait for the answer (seconds)",
"EINST.H_WARTEZEIT": "How long the interface waits for the service to answer a command. After that it reports <span class='sm-mono'>OK=2</span> — queued, outcome unknown. No success is reported that nobody has verified.",

"EINST.L_MQTT_EIN": "Publish values via MQTT",
"EINST.L_MQTT_TOPIC": "Topic prefix",
"EINST.H_MQTT_TOPIC": "Letters, digits, hyphen and underscore are allowed, levels separated by a slash. All topics derive from this prefix, see the MQTT tab. A previous prefix is noted when you change it: the service clears the retained topics below it, and the uninstall clears it as well.",

"EINST.GESPEICHERT": "The settings were saved.",
"EINST.FEHLER_ZAHL": "%s: please enter a whole number.",
"EINST.FEHLER_BEREICH": "%s: the value must be between %d and %d.",
"EINST.FEHLER_TOPIC": "The topic prefix is not allowed. Use letters, digits, hyphen and underscore, levels separated by a single slash – not at the start, not at the end, not doubled –, at most 64 characters. Nothing was changed.",
"EINST.FEHLER_ZUGANG_SPEICHERN": "The credentials file could not be written. Check the permissions of the configuration folder.",
"EINST.FEHLER_SPEICHERN": "The configuration could not be written: %s",

"EINST.H_ERKANNT": "Detected appliances",
"EINST.T_NR": "No.",

"MQTT.H_ZUSTAND": "State of the MQTT gateway",
"MQTT.GATEWAY_ERKLAERUNG": "Since LoxBerry 3 the MQTT gateway is <b>part of the system</b>, not a plugin. It is not installed separately but switched on under <i>System → MQTT Gateway</i>.",
"MQTT.NICHT_GEFUNDEN": "No MQTT section was found in the LoxBerry <span class='sm-mono'>general.json</span>. Nothing can be sent without it.",
"MQTT.AUTOSTART_AUS": "The gateway is <b>not</b> set to autostart. The broker entry alone is not enough — it is set out of the box and says nothing about whether messages can arrive. What matters is autostart under <i>System → MQTT Gateway</i>.",
"MQTT.AUTOSTART_EIN": "The gateway is set to autostart, so messages from this plugin can arrive.",
"MQTT.T_AUTOSTART": "Gateway autostart",
"MQTT.T_BROKER": "Broker",
"MQTT.T_UDP": "UDP input port",
"MQTT.T_PLUGIN": "Publishing by this plugin",
"MQTT.H_ABO": "The subscription in the MQTT gateway",
"MQTT.ABO_WARNUNG": "<b>Without this entry nothing arrives at the Miniserver.</b> This is by far the most common cause of failure. The line belongs under <i>System → MQTT Gateway</i> in the <i>Subscriptions</i> section; save afterwards.",
"MQTT.ABO_SCHRITTE": "The topic group of this plugin is:",
"MQTT.H_THEMEN": "All published topics",
"MQTT.THEMEN_ERKLAERUNG": "A topic whose value this appliance does not supply is not sent at all — so no topic is created carrying an invented zero.",
"MQTT.T_THEMA": "Topic",
"MQTT.T_BEDEUTUNG": "Meaning",
"MQTT.T_RETAIN": "Retain",
"MQTT.RETAIN_JA": "yes",
"MQTT.RETAIN_NEIN": "no",
"MQTT.PLATZHALTER": "<b>N</b> is the appliance number, so 1 for the first one.",
    "MQTT.RETAIN_ERKLAERUNG": "<b>Retain</b> means the broker keeps the last value and hands it to every new subscriber at once. After a restart of the Miniserver or the gateway those values are therefore back immediately. Device states are retained, measurements tied to a point in time are not, statements about the service itself (sign of life, ok, failed attempts, outages) never — otherwise a dead service would look healthy after a restart — a remaining time of 60 minutes, kept for a week, would be a quiet false statement. An empty value is never retained, because an empty payload deletes the topic in the broker.",

"LOX.H_TITEL": "Loxone integration",
"LOX.EINLEITUNG": "Nine steps. Work through them from top to bottom and you end up with a working integration — including the three pages from the sample project in step 8.",
"LOX.S1_TITEL": "Step 1: choose the path",
"LOX.S1_TEXT": "There are two paths. <b>The sample project and the pages in step 8 use HTTP</b>: the templates, the age of the values and the commands only exist there, and you can see in the browser right away what arrives. MQTT is the second path (off by default): the gateway creates the names of the virtual inputs itself and also delivers programme name and state text, but no age. Both paths at once give duplicate inputs.",
"LOX.S2_TITEL": "Step 2: The subscription in the MQTT gateway",
"LOX.S2_TEXT": "Only needed for the MQTT path. The topic group of this plugin is:",
"LOX.S3_TITEL": "Step 3: create a virtual HTTP input for the main values",
"LOX.S3_TEXT": "In Loxone Config: <i>Virtual input → Virtual HTTP input</i>. Address and polling cycle:",
"LOX.S3_BEFEHLE": "Below it one <i>command recognition</i> per value. The template below creates them all at once — less tedious and less error-prone than typing them.",
"LOX.S3_STRICH": "<b>A dash instead of a number means: this value is not available.</b> No zero is sent on purpose — a zero would be a silent false statement. Loxone keeps the last valid value in that case. That is exactly why the failure detection in step 7 is needed.",
"LOX.FEHLER_VORLAGE": "There is no such template. Nothing was generated.",
"LOX.VORLAGEN_FUER": "Templates for appliance %s",
"LOX.VORLAGEN_MQTT": "Template for the MQTT path",
"LOX.VORLAGEN_HINWEIS": "This is how to import them in Loxone Config: pick <b>Virtual inputs</b> in the tree on the left, then in the ribbon <b>Predefined HTTP devices → Import template…</b>. The command file (VQ_…) takes the same route under <b>Virtual outputs → Predefined devices → Import template…</b> — there the button has no HTTP in its name. Loxone <b>creates new blocks</b> and overwrites nothing — importing twice gives you duplicates. Only fields the appliance actually delivered on the last poll are created; whatever is missing for that reason is noted inside the file.",
"LOX.K_VORLAGE_STATUS": "Status inputs as a template",
"LOX.K_VORLAGE_VERBRAUCH": "Consumption inputs as a template",
"LOX.K_VORLAGE_BEFEHLE": "Commands as virtual outputs",
"LOX.K_VORLAGE_MQTT": "MQTT inputs as a template",
"LOX.VA_PROGRAMM": "On starts the programme selected on the appliance, Off aborts it. The start is rejected as long as no remote start release has been given on the appliance.",
"LOX.VA_PAUSE": "On pauses the running programme, Off resumes it.",
"LOX.VA_NETZ": "On switches the appliance on, Off switches it off.",
"LOX.VA_ABRUF": "Triggers an immediate poll instead of waiting for the interval. No off command.",
"LOX.MQTT_VORLAGE_HINWEIS": "This file only creates the inputs; the values then come from the MQTT gateway, not over the address entered. Without the subscription in the gateway nothing arrives at the Miniserver.",
"LOX.T_ADRESSE": "Address",
"LOX.T_ZYKLUS": "Polling cycle",
"LOX.T_TITEL": "Name",
"LOX.T_BEFEHL": "Command recognition",
"LOX.T_EINHEIT": "Unit",
"LOX.T_BEDEUTUNG": "Meaning",

"LOX.S4_TITEL": "Step 4: input for consumption and programme values",
"LOX.S4_TEXT": "One more virtual HTTP input built like step 3, using the action <span class='sm-mono'>verbrauch</span>. A cycle of 300 seconds is enough.",

"LOX.S5_TITEL": "Step 5: sending commands (virtual output)",
"LOX.S5_TEXT": "Only needed if Loxone should trigger something. In Loxone Config create a <i>virtual output</i> with the address below and one <i>virtual output command</i> per command. In the command text <span class='sm-mono'>&lt;v&gt;</span> stands for the value passed. For automatics and app buttons use the two pulse commands “WW 1 Start (Befehl)” and “WW 1 Abbrechen (Befehl)” of the template – “WW 1 Programm (Befehl)” sends “stop” when it drops and aborts a programme that has just started.",
"LOX.T_VA_ADRESSE": "Address of the virtual output",
"LOX.T_VA_ABRUF": "Trigger an immediate poll",
"LOX.S5_WARNUNG": "Three things to know beforehand. <b>First:</b> write commands are disabled by default and must be enabled in the Settings tab. <b>Second:</b> an answer of <span class='sm-mono'>OK=1</span> means the provider accepted the request. Whether the appliance actually starts only shows on the next poll — if you need certainty, evaluate <span class='sm-mono'>LAEUFT</span>, not the answer to the command. <b>Third:</b> every switching command except <span class='sm-mono'>abruf</span> needs <span class='sm-mono'>geraet=</span> — without it the plugin answers <span class='sm-mono'>GRUND=GERAET_FEHLT</span> and switches nothing. <span class='sm-mono'>ein</span> and <span class='sm-mono'>aus</span> with the same value within 60 seconds are not sent again; the answer then carries <span class='sm-mono'>UNVERAENDERT=1</span>.",

"LOX.S6_TITEL": "Step 6: the token",
"LOX.T_TOKEN": "Token of this plugin",
"LOX.S6_TEXT": "The endpoint sits in the unauthenticated area so Loxone can reach it without credentials. It is protected by this token. The token is part of every address you enter in the Miniserver — <b>a new token invalidates all of them at once</b> and has to be updated everywhere. So only roll a new one if it has actually leaked.",

"LOX.S7_TITEL": "Step 7: failure detection",
"LOX.S7_TEXT": "If a provider goes silent, the virtual inputs keep their last value. Everything looks normal in the app although nothing has arrived for hours. That is why the value <span class='sm-mono'>ALTER</span> is carried along: it states the age of the snapshot in seconds. <span class='sm-mono'>OK</span> drops to 0 after three times the idle interval (15 minutes); if the LoxBerry itself stands still, OK and ALTER freeze as well – only a Value Validator on ALTER notices that (page “Weissware” in step 8).",

"LOX.S8_TITEL": "Step 8: three pages from the sample project to rebuild",
"LOX.S8_TEXT": "Three pages from the LoxBerry plugins sample project, built and connected there in Loxone Config. One block per row; Loxone Config lists them all in the block search (key F5). If you only want monitoring, take over the first page alone; “Weissware PV-Start” is the case most people are after: <b>wash when the sun is shining</b>. The names apply to appliance 1 as the templates create them; the template titles are fixed German, also with an English interface.",

"LOX.S9_TITEL": "Step 9: cross-check",
"LOX.S9_TEXT": "Open these three addresses in a browser. The first must return values, the other two must be <b>rejected</b> — if they are not, something is wrong with the protection.",
"LOX.T_PRUEFUNG": "Request",
"LOX.T_ERWARTUNG": "Expected answer",
"LOX.T_BAUSTEIN": "Block (type)",
"LOX.T_NAMENSVORSCHLAG": "Name (suggestion)",
"LOX.T_PARAMETER": "Parameters",
"LOX.T_EINGAENGE": "Connect inputs to",
"LOX.K_TOKEN_NEU": "Roll a new token",
"LOX.TOKEN_NEU": "A new token was created. All addresses entered in the Miniserver so far are invalid now and have to be updated.",


"TEST.H_SELBSTPRUEFUNG": "Self-check",
"TEST.EINLEITUNG": "This check answers <b>without Loxone</b> whether the setup holds. Each row is a question; a cross means something is missing. What could only be checked with a signed-in appliance is listed as unverified below.",
"TEST.T_FRAGE": "Question",
"TEST.T_BEFUND": "Finding",
"TEST.F_VENV": "Is the Python virtual environment present?",
"TEST.A_VENV_FEHLT": "no — reinstall the plugin",
"TEST.F_PYTHON": "Is Python new enough (3.9 or newer)?",
"TEST.A_PYTHON_ZU_ALT": "too old for requests",
"TEST.A_PYTHON_UNBEKANNT": "cannot be determined — the virtual environment is missing",
"TEST.F_LIB": "Is requests loaded, and in which version?",
"TEST.A_LIB_FEHLT": "no — see the installation output",
"TEST.F_DIENST": "Is the polling service running?",
"TEST.A_DIENST_LAEUFT": "yes, PID",
"TEST.A_DIENST_SOLL_TOT": "no — it should be running but is not. Check the log file.",
"TEST.A_DIENST_GESTOPPT": "no — deliberately stopped",
"TEST.F_RECHTE": "Is the credentials file protected from other users?",
"TEST.A_ZUGANGSDATEI_FEHLT": "the file is missing",
"TEST.F_AUSFAELLE": "Did all providers answer?",
"TEST.A_KEINE_AUSFAELLE": "yes, all of them",
"TEST.F_ABRUF": "How fresh is the snapshot?",
"TEST.A_ABRUF_ALTER": "%d seconds old",
"TEST.A_NIE_ABGERUFEN": "no poll has taken place yet",
"TEST.F_LETZTER_FEHLER": "Last reported fault",
"TEST.F_MQTT": "Is the LoxBerry MQTT gateway ready?",
"TEST.F_MQTT_EIN": "Is this plugin's MQTT publishing switched on?",
"TEST.A_MQTT_EIN_JA": "Yes. The service sends its topics to the gateway's UDP input.",
"TEST.A_MQTT_EIN_NEIN": "No — nothing reaches the broker and therefore nothing reaches Loxone. Tab MQTT.",
"TEST.A_MQTT_NICHT_GEFUNDEN": "no MQTT section in general.json",
"TEST.A_MQTT_AUS": "not set to autostart — System, MQTT Gateway",
"TEST.F_STEUERUNG": "Are write commands allowed?",
"TEST.A_STEUERUNG_EIN": "yes",
"TEST.A_STEUERUNG_AUS": "no — disabled by default, this is not an error",

"TEST.H_LESEN": "View",
"TEST.K_STATUS": "Fetch status",
"TEST.H_TECHNIK": "Technical information",
"TEST.K_SELBSTTEST": "Self-test of the service",
"TEST.F_REITER": "Do the tab bar, the panes and the allow list carry the same names?",
"TEST.A_REITER_UNLESBAR": "index.php cannot be read - not determinable",
"TEST.A_REITER_OK": "%d tabs, all three places agree",
"TEST.A_REITER_AB": "bar %d, panes %d, allow list %d - they do not match",
"WW_MQTT.GEWAEHLT": "The programme selected on the appliance while none is running (Home Connect only)",
"WW_ANSAGE.EIN_GERAET": "An appliance",
"WW_ANSAGE.T_FERTIG": "Hello! %s has finished.",
"WW_ANSAGE.T_STOERUNG": "Attention! %s reports a fault.",
"WW_ANSAGE.HAUSFORM": "Announcements go through the shared speech output of the plugins of this house: Loxone Music Server, MusicServer4Home, an own address template, the original Audioserver (via Loxone Config), Alexa-NG or Google speakers (Chromecast 4 Lox NG). Address and template must be in the home network. Only the length of the text goes into the log.",
"WW_ANSAGE.TEST_GESENDET": "Test announcement sent: %s",
"WW_ANSAGE.TEST_NICHT": "Test announcement not sent: %s",
"WW_ANSAGE.TEST_NICHTS": "No test announcement: %s",
"WW_ANSAGE.TEST_WAS": "%d characters, HTTP %d.",
"TEST.F_ANSAGE": "Speech output: set up, and how did the last announcement go?",
"WW_ANSAGE.T_FERNSTART": "Note: the remote start release for %s has expired.",
"WW_ANSAGE.L_STOERUNG": "Also speak on a fault",
"WW_ANSAGE.L_FERNSTART": "Also speak when the remote start release expires",
"WW_ANSAGE.H_FERNSTART": "The release is given on the appliance and usually expires with the programme. After that the plugin rejects every start command — without this announcement you only notice once the sun has shone for nothing.",
"WW_ANSAGE.L_RUHE_VON": "Quiet time from",
"WW_ANSAGE.L_RUHE_BIS": "Quiet time until",
"WW_ANSAGE.H_RUHE": "Nothing is spoken inside this window. The state is still tracked, so that half the night is not caught up at seven in the morning. Equal times mean: no quiet time.",
"WW_ANSAGE.FEHLER_ZEIT": "%s: please enter a time of day in the form 22:00.",
"LAUF.H": "Completed programme runs",
"LAUF.ERKLAERUNG": "Recorded at the moment an appliance switches to <i>finished</i> — after that energy and water are gone at the provider. A dash means the value was not available. Home Connect delivers neither energy nor water, SmartThings no water.",
"LAUF.LEER": "No run has finished since the plugin started recording.",
"LAUF.T_ENDE": "End",
"LAUF.T_PROGRAMM": "Programme",
"LAUF.T_DAUER": "Duration (min)",
"LAUF.T_ENERGIE": "Energy (kWh)",
"LAUF.T_WASSER": "Water (l)",
"TEST.F_ENDPUNKT": "Does our own endpoint answer over HTTP?",
"TEST.A_EP_UNMESSBAR": "not determinable: neither curl nor allow_url_fopen is available",
"TEST.A_EP_KEINE_ANTWORT": "not determinable: no answer (HTTP %d). A web server handling only one request at a time cannot call itself while building this page.",
"TEST.A_EP_FALSCH": "HTTP %d, and the answer does not start with the expected marker: %s",
"TEST.A_EP_ALTER": "measured %d s ago",
"TEST.F_VORGABEN": "Do the interface and the service carry the same defaults?",
"TEST.A_VORGABEN_UNLESBAR": "bin/weissware.py cannot be read - not determinable",
"TEST.A_VORGABEN_FEHLEN": "missing in the interface: %s",
"TEST.A_VORGABEN_OK": "all %d keys of the service are known to the interface as well",
"TEST.F_THEMEN": "Does the topic list match the sending code?",
"TEST.A_THEMEN_UNLESBAR": "bin/weissware.py cannot be read - not determinable",
"TEST.A_THEMEN_AB": "difference: %s",
"TEST.A_THEMEN_OK": "%d topics per appliance, list and sending code agree",
"TEST.F_RETAIN": "Do both retain tables agree?",
"TEST.A_RETAIN_OK": "%d of %d topic stems retained; interface, service and topic list agree",
"TEST.A_RETAIN_AB": "the tables differ: %s",
"TEST.A_RETAIN_UNLESBAR": "the table in bin/weissware.py cannot be read - not determinable",
"TEST.F_MITSCHNITT": "Is a traffic capture running?",
"TEST.A_MITSCHNITT_LAEUFT": "yes, %d seconds left. It ends by itself.",
"TEST.K_TROCKEN": "Dry run: what would happen?",
"TEST.H_TROCKEN": "Shows for <i>Start</i> which lock applies and which request would go out to the provider — and <b>sends nothing</b>. It needs no running service; that is exactly when you want to know.",
"TEST.K_MITSCHNITT_EIN": "Start a 5 minute capture",
"TEST.K_MITSCHNITT_AUS": "Stop the capture now",
"TEST.H_MITSCHNITT": "Records the providers' requests and answers — the only means when a value stays empty and nobody knows whether the provider delivers nothing or the mapping misses the key. Off by default, ends by itself, the file is capped at 500 kB. Credentials and tokens are removed before writing.",
"TEST.M_MITSCHNITT_EIN": "The capture runs for %d seconds and then ends by itself.",
"TEST.M_MITSCHNITT_AUS": "The capture has ended.",
"TEST.K_ROH": "View raw data as JSON",
"TEST.H_SCHALTEN": "Switching",
"TEST.SCHALTEN_WARNUNG": "<b>These buttons act immediately and on the real appliance.</b> A wash programme that has been started runs through even if nobody has loaded laundry. Without the remote start release on the appliance the provider rejects the start — that is not a fault, it is the safeguard doing its job.",
"TEST.SCHALTEN_GESPERRT": "Write commands are currently disabled. The buttons will therefore return a rejection — that is not an error. Enable them in the Settings tab.",
"TEST.K_ABRUF": "Poll now",
"TEST.M_UNBEKANNT": "Unknown test action.",
"TEST.M_DIENST_AUS": "The polling service is not running – nothing was queued. Start the service on the Settings tab first.",
"TEST.H_UNGEPRUEFT": "What is unverified in this version",
"TEST.UNGEPRUEFT": "This plugin was built <b>without developer accounts and without appliances</b>. Unverified is therefore: whether signing in with the three providers succeeds, whether the field names of the responses match the mapping here, and whether the write commands have the expected effect. Endpoints and data shapes come from the developer documentation, not from a measurement. Everything else has been verified: user interface, endpoint, protection, queue, language files and the mapping itself — the latter against rebuilt responses in the documented shape. That is why this line stays in the 0.9.x number range and not at 1.0.0. If something stays empty, the button <i>View raw data as JSON</i> helps: it shows what the service actually received.",

"LOG.H_TITEL": "Log files",
"LOG.ERKLAERUNG": "The polling service writes to this one file only. Below are the last 400 lines, newest first.",
"LOG.LEER": "The log file is empty or has not been created yet.",
"LOG.K_LEEREN": "Clear log file",
"LOG.GELEERT": "Log file cleared",

"WW_FELD.ALTER": "Age of the snapshot — for failure detection",
"WW_FELD.OK": "1 = the last poll succeeded and is at most three times the idle interval old; with several providers also: the provider of this appliance answered (otherwise 0, the values are the last measured ones)",

"WW_VFELD.OK": "1 = the last poll succeeded and is at most three times the idle interval old; with several providers also: the provider of this appliance answered",


"WW_MQTT.OK": "1 = the last poll succeeded",
"TEST.A_MARKE_FEHLT": "not created yet — appears on the first poll",
"TEST.F_MARKE": "Are the authentication tokens protected from other users?",
"WW_FELD.ZUSTAND": "0 off, 1 ready, 2 running, 3 paused, 4 finished, 5 fault",
"WW_MQTT.FERTIG": "1 = programme finished",
"WW_MQTT.ZUSTAND": "0 off, 1 ready, 2 running, 3 paused, 4 finished, 5 fault",
"ALLG.GERAET": "Appliance",
"ALLG.GERAETE": "Appliances",
"ALLG.IN_BETRIEB": "running",
"ALLG.KEIN_FERNSTART": "no remote start release",
"ALLG.RESTZEIT": "Time left",
"ALLG.ZUSTAND": "State",
"EINST.ANBIETER_ERKLAERUNG": "Three ecosystems, one common model. Only switch on what you actually own — every enabled provider costs requests even if it has no appliances. Home Connect and Miele need a <b>free developer account</b> because both only answer registered applications; SmartThings gets by with a token.",
"EINST.ANGEMELDET": "signed in",
"EINST.ANMELDUNG_ERKLAERUNG": "Save first, then sign in. Signing in stores a refresh key the service uses to keep itself signed in — so you only have to do this once. SmartThings is the exception, see above.",
"EINST.FEHLER_MIELE_CODE": "The value entered does not look like a sign-in code. It was not redeemed.",
"EINST.FEHLER_SPRACHE": "The language must have the form de-DE.",
"EINST.FEHLER_TAKT_TAUSCH": "The idle interval is smaller than the running one. That is the wrong way round — please swap the two values.",
"EINST.GESETZT": "stored (%d characters) – leave empty to keep it",
"EINST.HC_ADRESSE": "Address",
"EINST.HC_ADRESSE_DIREKT": "Address with code",
"EINST.HC_BEGONNEN": "Sign-in has begun. The code and address are below — you have five minutes.",
"EINST.HC_CODE": "Code",
"EINST.HC_FERTIG": "Home Connect is signed in.",
"EINST.HC_GUELTIG": "valid for another",
"EINST.HC_NOCH_NICHT": "Not confirmed yet. Enter the code in the browser, grant access and then press 'Complete sign-in' again.",
"EINST.HC_SCHRITT1": "Press <i>Begin sign-in</i>. A code and an address will appear here; open the address in any browser, enter the code and grant access. Finally press <i>Complete sign-in</i>.",
"EINST.HC_SCHRITT2": "Sign-in is in progress. Open the address in a browser, enter the code, grant access — then press <i>Complete sign-in</i> here.",
"EINST.H_ANBIETER": "Providers",
"EINST.H_ANMELDUNG": "Sign-in",
"EINST.H_HC_ID": "From the Home Connect developer portal, section <i>Applications</i>. Create an application using the <b>Device Flow</b> — the only method that works without a screen on the device.",
"EINST.H_HC_SECRET": "Only needed to refresh the access token. Leaving the field empty keeps the stored secret.",
"EINST.H_HC_SIMULATOR": "Home Connect provides simulated appliances. That lets you set everything up and rebuild it in Loxone before a real machine is connected. <b>Note:</b> the simulator and real appliances need different client IDs.",
"EINST.H_MIELE_CODE": "The whole address works too — the code is extracted from it. The code is valid for a few minutes and can be redeemed exactly once.",
"EINST.H_MIELE_ID": "From the Miele developer portal, section <i>Get involved</i>. Enter <span class='sm-mono'>http://localhost</span> as the redirect address — it does not have to be reachable, the code is copied back by hand.",
"EINST.H_SPRACHE": "The providers return programme names and state texts in this language. It has no effect on the language of this user interface.",
"EINST.H_ST_TOKEN": "From the SmartThings developer portal. Leaving the field empty keeps the stored token.",
"EINST.H_TAKT_BETRIEB": "Interval as soon as at least one appliance is working. Lower limit 60 seconds: Home Connect explicitly names frequent polling in its best practices as the most common cause of HTTP 429.",
"EINST.H_TAKT_RUHE": "Interval while no appliance is running. Five minutes is plenty — a washing machine that is off will not finish within a minute.",
"EINST.KEINE_GERAETE": "No appliance detected yet. That is normal until the first successful poll: enable a provider, enter the credentials, save, sign in, start the service and wait one interval. If the list is still empty afterwards, the reason is in the <i>Test</i> tab and in the log file.",
"EINST.KENNUNG_HINWEIS": "Every address also accepts the identifier instead of the number — <span class='sm-mono'>geraet=SIEMENS-HCS03WCH1-…</span>. Since 0.9.7 a number stays with its appliance for good — even if a provider fails or an appliance is added; it is kept in <span class='sm-mono'>data/plugins/weissware/geraetenummern.json</span>. The identifier is still the clearer address, because you can see from it which appliance is meant.",
"EINST.K_HC_FERTIG": "Complete sign-in",
"EINST.K_HC_START": "Begin sign-in",
"EINST.K_MIELE_CODE": "Redeem code",
"EINST.LEER": "nothing stored yet",
"EINST.L_HC_EIN": "Poll Home Connect",
"EINST.L_HC_ID": "Client ID",
"EINST.L_HC_SECRET": "Client secret",
"EINST.L_HC_SIMULATOR": "Use the simulator instead of real appliances",
"EINST.L_MIELE_CODE": "Code from the address bar",
"EINST.L_MIELE_EIN": "Poll Miele",
"EINST.L_MIELE_ID": "Client ID",
"EINST.L_MIELE_SECRET": "Client secret",
"EINST.L_SPRACHE": "Language of the provider responses",
"EINST.L_ST_EIN": "Poll SmartThings",
"EINST.L_ST_TOKEN": "Personal access token",
"EINST.L_TAKT_BETRIEB": "Interval when running (seconds)",
"EINST.L_TAKT_RUHE": "Interval when idle (seconds)",
"EINST.MIELE_FERTIG": "Miele is signed in.",
"EINST.MIELE_OHNE_ID": "Enter and save the client ID above first — without it no sign-in address can be built.",
"EINST.MIELE_SCHRITTE": "Miele offers <b>no</b> flow for devices without a screen. So by hand: copy the address below into a browser, sign in with your Miele account and pick the appliances to release. You will then land on a page that does not load — that is expected. Copy the part after <span class='sm-mono'>code=</span> from its <b>address bar</b> (or the whole address) and paste it here.",
"EINST.ST_SCHRITTE": "SmartThings needs no sign-in — the token above is enough. It does expire after 24 hours; enter a new one here and save.",
"EINST.ST_WARNUNG": "<b>Reservation.</b> On 30 December 2024 Samsung cut the lifetime of newly issued personal access tokens to <b>24 hours</b> and lowered the rate limits. For continuous operation Samsung requires a registered application with a publicly reachable webhook — which a LoxBerry behind a router cannot easily provide. In practice: <b>you have to renew the token every day.</b> If you do not want to live with that, leave SmartThings switched off. Tokens issued before 30 December 2024 are not affected.",
"EINST.TAKT_ERKLAERUNG": "<b>The actual reason for this plugin.</b> A fixed polling cycle is either too slow for a useful remaining time or too fast for the provider's rate limits. Here there are two intervals: a wide one while nothing is running and a tight one as soon as at least one appliance is working. Switching happens automatically.",
"EINST.T_ANBIETER": "Provider",
"EINST.T_FERNSTART": "Remote start",
"EINST.T_KENNUNG": "Identifier",
"EINST.T_MARKE": "Brand",
"EINST.T_NAME": "Name",
"EINST.T_TYP": "Type",
"EINST.T_ZUSTAND": "State",
"EINST.WARN_HC_OHNE_ID": "Home Connect is enabled but no client ID is stored. Every poll will fail.",
"EINST.WARN_MIELE_OHNE_ID": "Miele is enabled but no client ID is stored. Every poll will fail.",
"EINST.WARN_ST_OHNE_TOKEN": "SmartThings is enabled but no token is stored. Every poll will fail.",
"LOX.MEHRERE_GERAETE": "Several appliances — one virtual input per appliance:",
"LOX.S4_LEER": "<b>Not every provider supplies every value.</b> Home Connect reports neither energy nor water consumption; SmartThings reports no progress in percent; Miele supplies both, but only for appliances with EcoFeedback. What is missing is a dash — not a zero.",
"LOX.T_VA_AUS": "Switch appliance off",
"LOX.T_VA_EIN": "Switch appliance on",
"LOX.T_VA_FORTSETZEN": "Resume programme",
"LOX.T_VA_PAUSE": "Pause programme",
"LOX.T_VA_START": "Start programme (the one selected on the appliance)",
"LOX.T_VA_START_PROG": "Start a specific programme (Home Connect only)",
"LOX.T_VA_STOP": "Abort programme",
"TEST.A_ANBIETER": "yes, %d",
"TEST.A_ANGEMELDET": "yes, the service refreshes itself",
"TEST.A_GERAETE": "yes, %d",
"TEST.A_KEINE_GERAETE": "no — normal until the first successful poll",
"TEST.A_KEIN_ANBIETER": "no — Settings tab",
"TEST.A_NICHT_ANGEMELDET": "no — Settings tab, Sign-in section",
"TEST.A_ST_TOKEN": "not applicable — SmartThings only needs the token (valid 24 hours)",
"TEST.A_ZUGANG_DA": "yes",
"TEST.A_ZUGANG_FEHLT": "no",
"TEST.F_ANBIETER": "Is at least one provider enabled?",
"TEST.F_ANGEMELDET": "%s: is sign-in complete?",
"TEST.F_AUSFALL": "Did %s answer?",
"TEST.F_GERAETE": "Have appliances been detected?",
"TEST.F_ZUGANG": "%s: are credentials stored?",
"TEST.H_PROGRAMM": "Leave empty to start the programme selected on the appliance — that is the normal case. A programme key works <b>with Home Connect only</b> and looks like <span class='sm-mono'>LaundryCare.Washer.Program.Cotton</span>; with Miele and SmartThings a start with a key is rejected. The key becomes visible once a programme is running: the button <i>View raw data as JSON</i> then carries it.",
"TEST.K_AUS": "Appliance off",
"TEST.K_EIN": "Appliance on",
"TEST.K_FORTSETZEN": "Resume",
"TEST.K_GERAETE": "List appliances",
"TEST.K_PAUSE": "Pause",
"TEST.K_START": "Start programme",
"TEST.K_STOP": "Abort programme",
"TEST.K_VERBRAUCH": "Fetch consumption",
"TEST.L_GERAET": "Appliance (running number)",
"TEST.L_PROGRAMM": "Programme (optional)",
"TEST.M_GERAET_UNGUELTIG": "The appliance number is not a number between 1 and 999.",
"TEST.M_PROGRAMM_UNGUELTIG": "The programme key contains characters that do not occur there. It was not sent.",
"WW_FELD.FERNBED": "1 = remote control is allowed",
"WW_FELD.FERNSTART": "1 = remote start is released on the appliance",
"WW_FELD.FERTIG": "1 = programme finished, not yet acknowledged",
"WW_FELD.FORTSCHR": "Progress of the running programme",
"WW_FELD.LAEUFT": "1 = a programme is running",
"WW_FELD.LAUFMIN": "Elapsed time of the programme",
"WW_FELD.NETZ": "1 = appliance switched on",
"WW_FELD.RESTMIN": "Time left until the programme ends",
"WW_FELD.STARTMIN": "Time until start when a delayed start is set",
"WW_FELD.TUER": "1 = door open",
"WW_FELD.VERBUNDEN": "1 = the appliance is reachable for the provider",
"WW_MQTT.ANBIETER": "homeconnect, miele or smartthings",
"WW_MQTT.ENERGIE": "Energy used in kWh",
"WW_MQTT.FERNBED": "1 = remote control allowed",
"WW_MQTT.FERNSTART": "1 = remote start released on the appliance",
"WW_MQTT.FORTSCHRITT": "Progress in percent",
"WW_MQTT.GERAETE": "Number of detected appliances",
"WW_MQTT.LAEUFT": "1 = a programme is running",
"WW_MQTT.LAUFZEIT": "Elapsed time in minutes",
"WW_MQTT.NAME": "Name of the appliance",
"WW_MQTT.NETZ": "1 = appliance switched on",
"WW_MQTT.PROGRAMM": "Running programme in plain text",
"WW_FELD.FERTIGUM": "Expected finishing time as Unix time. Loxone counts seconds since 1 Jan 2009, so subtract 1230768000 there. A dash means no time left is known.",
"WW_MQTT.TS": "Time of the last <b>successful</b> poll as Unix time. There is no age over MQTT - it is always zero at sending time; the Miniserver computes it: (Loxone time + 1230768000) - ts.",
"WW_MQTT.FEHLER_FOLGE": "Failed polls in a row. 0 means the last one succeeded. Tells a brief hiccup from a lasting fault.",
"WW_MQTT.FERTIGUM": "Expected finishing time as Unix time",
"WW_MQTT.RESTZEIT": "Time left in minutes",
"WW_MQTT.SCHLEUDER": "Configured spin speed",
"WW_MQTT.STARTZEIT": "Time until start in minutes",
"WW_MQTT.TEMPERATUR": "Configured temperature in degrees Celsius",
"WW_MQTT.TUER": "1 = door open",
"WW_MQTT.VERBUNDEN": "1 = reachable for the provider",
"WW_MQTT.WASSER": "Water used in litres",
"WW_MQTT.ZUSTAND_TEXT": "State in plain text, as the provider names it",
"WW_VFELD.ENERGIE": "Energy used by the running programme",
"WW_VFELD.SCHLEUDER": "Configured spin speed",
"WW_VFELD.TEMP": "Configured temperature",
"WW_VFELD.WASSER": "Water used by the running programme",
"WW_ANSAGE.H": "Voice announcement (when an appliance finishes)",
"WW_ANSAGE.H_EIN": "Spoken when an appliance changes to <i>finished</i> – once per programme run, never on LoxBerry restart. Default: on.",
"WW_ANSAGE.H_TEST": "Announcement",
"WW_ANSAGE.H_TEST_TEXT": "Speaks immediately into the configured zones – regardless of whether the announcement is enabled.",
"WW_ANSAGE.K_TEST": "Speak test announcement now",
"WW_ANSAGE.L_EIN": "Enable announcement",
"WW_ANSAGE.TESTTEXT": "Hello! This is a test announcement of the Weissware plugin.",
"TEST.A_FELDER_AB": "difference: %s",
"TEST.A_FELDER_OK": "%d fields, template and line agree",
"TEST.A_FELDER_UNLESBAR": "the status line cannot be read - not determinable",
"TEST.A_MUSTER_AB": "ambiguous: %s - Loxone takes the first match and delivers the wrong value",
"TEST.A_MUSTER_OK": "%d field names, none is contained in another",
"TEST.A_ZWEITSCHRIFT_DA": "yes: %s, next to the config folder",
"TEST.A_ZWEITSCHRIFT_FEHLT": "none yet - it is created on the first save",
"TEST.F_FELDER": "Do the template and the status line carry the same field names?",
"TEST.F_MUSTER": "Is every search pattern of the status line unambiguous?",
"TEST.F_ZWEITSCHRIFT": "Is there a second copy of the configuration?",
"WW_MQTT.AUSFAELLE": "Number of providers that did not answer on the last poll",
"WW_MQTT.AUSFALL_HC": "1 = Home Connect did not answer on the last poll",
"WW_MQTT.AUSFALL_MIELE": "1 = Miele did not answer on the last poll",
"WW_MQTT.AUSFALL_ST": "1 = SmartThings did not answer on the last poll",
"ALLG.STOERUNG_ALTER": "(observed %d s ago)",
"EINST.FEHLER_KEIN_ANBIETER": "No provider is switched on - the service would stop again immediately. Tick the provider you own above and save. Being signed in is not enough: signing in and ticking are two different things.",
"EINST.MIELE_SCHON_ANGEMELDET": "The service keeps itself signed in. You only need the steps below if you want to sign in again.",
"TEST.A_ANGEMELDET_AUS": "yes: %s. Signed in, but the tick in the Settings tab is missing - this provider is not polled.",
"TEST.F_ANGEMELDET_AUS": "Is a signed-in provider switched off?",
"LOX.VA_KURZ": "Weissware commands - write commands must be enabled in the Settings tab",

# NACHGEPFLEGT 31.08.2026. Diese 18 Schluessel standen in der
# ausgelieferten .ini und im PHP, aber nicht mehr hier - ein Lauf
# haette sie geloescht, und der Erzeuger hat sich deshalb bisher
# geweigert zu schreiben. Die Werte sind aus der .ini geholt.
"EINST.H_SICHERUNG": "Back up and restore settings",
"EINST.K_SICHERN": "Back up settings",
"EINST.K_ZURUECK": "Restore",
"EINST.SICH_ABGELEHNT": "The file was <b>not</b> accepted — nothing has been changed:",
"EINST.SICH_ERKLAERUNG": "For <b>moving to a second LoxBerry</b>: the file contains all settings of this plugin including the action token and the credentials, and can be restored there. It does not contain the providers' sign-in tokens — after restoring you have to sign in once.",
"EINST.SICH_FREMD": "Unknown setting in the file: %s",
"EINST.SICH_KEINE_DATEI": "No file was selected, or the upload failed.",
"EINST.SICH_KEIN_JSON": "The file is not a valid backup of this plugin.",
"EINST.SICH_LEER": "The file contains no known setting.",
"EINST.SICH_SCHREIBFEHLER": "The settings could not be written.",
"EINST.SICH_UEBERNOMMEN": "Settings restored: %d values taken over.",
"EINST.SICH_WARNUNG": "<b>The file contains your credentials.</b> Without them all fields would look right after restoring and the plugin still would not reach the installation. Treat the file like a password: do not post it in a forum and do not attach it to a bug report.",
"EINST.SICH_DIENST_AUS": "The service was not running; nothing was pulled along.",
"EINST.SICH_DIENST_NEU": "The service was restarted with the new settings.",
"EINST.SICH_DIENST_FEHL": "The service could not be restarted - please start it by hand in the Settings tab.",
"EINST.SICH_OHNE_TOKEN": "The action token is missing from the file. Without it every address entered in the Miniserver would be invalid - so nothing is taken over at all.",
"EINST.SICH_WERT": "Invalid value for: %s",
"EINST.SICH_ZUGANG_FEHL": "The settings were taken over, but the credentials from the file could not be written.",
"EINST.SICH_ZU_GROSS": "The file is larger than allowed — a backup of this plugin is a few kilobytes.",
"MQTT.ABO_GEMESSEN": "(measured: gateway&nbsp;V%d)",
"MQTT.ABO_UNBEKANNT": "The version of your MQTT gateway could not be determined. <b>Version&nbsp;1:</b> without this entry nothing arrives at the Miniserver. <b>Version&nbsp;2 and newer:</b> the topic group appears by itself under Subscriptions, nothing needs to be entered.",
"MQTT.ABO_V2": "<b>MQTT gateway V2 detects the topic group by itself</b> — nothing needs to be entered here. The group appears under <i>Subscriptions</i>; tick the data points you want there. If it does not appear, nothing has been published yet.",
"WACHE.FALSCH": "The form token was invalid - the session has probably expired. Please reload the page.",
"WACHE.FEHLT": "The request carried no form token and was rejected. Please reload the page and try again.",
    # ---- Nachgetragen 19.09.2026 aus der ausgelieferten language_en.ini --------
    # Diese Schluessel standen nur dort; der Erzeuger verweigerte deshalb das
    # Schreiben (Rueckgabe 1). Die Ausgabe sortiert je Abschnitt selbst, die
    # Stelle im Quelltext ist also ohne Wirkung auf die .ini.
    "TEST.A_KONFIG_AUS_ZWEITSCHRIFT": "it was empty and was restored from the second copy. After an update this is the normal case.",
    "TEST.A_KONFIG_KAPUTT_GEHEILT": "no — it was unreadable and was restored from the second copy. The previous content is kept as %s. Please review the settings: the second copy may be older.",
    "TEST.A_KONFIG_KAPUTT_OHNE": "no — it is unreadable and there is no usable second copy beside it. The previous content is kept as %s. The action token cannot be recomputed.",
    "TEST.A_KONFIG_LEER": "it is empty. After a fresh installation this is normal.",
    "TEST.A_KONFIG_NEU": "it does not exist yet — it is created on the first save.",
    "TEST.A_KONFIG_OK": "yes, readable and carrying an action token",
    "TEST.A_KONFIG_UNBEKANNT": "cannot be determined — the configuration was not read during this page build",
    "TEST.A_LEBENSZEICHEN_AB": "no — a statement about the service is sent retained: %s",
    "TEST.A_LEBENSZEICHEN_OK": "yes — %s: sent with publish, never with retain",
    "TEST.A_UPGRADE_ALT": "no — but the marker of an earlier update is still there, and it is no longer valid. An installation was probably aborted. The service is not blocked by it; the file data/plugins/%s can be deleted.",
    "TEST.A_UPGRADE_KEINE": "no. The service can be started.",
    "TEST.A_UPGRADE_LAEUFT": "yes, for %d seconds. While it runs, no service is started — not even through the buttons on the Settings tab. The installation starts it afterwards if it was running before.",
    "TEST.F_KONFIG": "Was the configuration intact when this page was built?",
    "TEST.F_LEBENSZEICHEN": "Are the sign of life and the service state never sent retained?",
    "TEST.F_UPGRADE_MARKE": "Is an update of this plugin running right now?",
    "WACHE.KEIN_TOKEN": "The configuration file is unreadable, and the second copy beside it still carries the existing action token. No new action token is created — the old one cannot be recomputed, and every address in the Miniserver would become invalid. Please look at the Log files tab and restore the configuration; the button for a new token will work again afterwards.",
# ---- Durchgangsbau 02.10.2026 (weissware_BAULISTE.md, vb_ww): PRG, X-2, Nr. 19,
# Ausgabearten Alexa-NG und Google-Lautsprecher, MQTT-Praefixe, Geraete-ok ----
"ALLG.EINMAL_FEHLER": "The result could not be stored in the data folder (%s) – it is therefore shown on this page only, and reloading would repeat the action.",
"EINST.N_HC_ID": "Home Connect: client ID",
"EINST.N_HC_SECRET": "Home Connect: client secret",
"EINST.N_MIELE_ID": "Miele: client ID",
"EINST.N_MIELE_SECRET": "Miele: client secret",
"EINST.N_ST_TOKEN": "SmartThings: personal access token",
"EINST.FEHLER_ZEICHEN": "%s contains control characters, is not valid UTF-8 or is longer than 512 characters. Please enter it as the developer portal shows it; nothing was cut out and nothing was saved.",
"EINST.FEHLER_MIELE_ABLAGE": "The Miele code could not be stored in the data folder (%s) – it is never passed on the command line, so no sign-in took place.",
"EINST.L_SITZUNG_OK": "Yes, delete the sign-in tokens",
"EINST.SITZUNG_ERKLAERUNG": "<i>Force a new login</i> deletes the sign-in tokens of Home Connect and Miele – only with the tick box below it. After that the service does not sign in by itself: the sign-in happens again in the browser, section <i>Sign-in</i> further down. Credentials and settings stay.",
"EINST.SITZUNG_OHNE_HAKEN": "The sign-in tokens were not deleted: please tick “Yes, delete the sign-in tokens” first.",
"EINST.SITZUNG_FEHLER": "The sign-in tokens could not be deleted (%s) – check the write permission of the data folder.",
"EINST.SICH_SPRECHTOKEN": "The file contains a speech token (%s). Backups never carry it – the file is not accepted. Enter the token on the Settings tab.",
"EINST.SICH_TOKEN_LEER": "The file carries an empty action token – the current token stays, the addresses in the Miniserver remain valid.",
"EINST.SICH_WARN_STAND": "These stored values would be rejected when restoring: %s. The backup still contains them in full and names them under _warnung – please correct and save them in the settings first.",
"MQTT.PRAEFIX_VORGEMERKT": "The previous prefix %s has been noted: the service clears the retained topics below it (checking back with the broker), and the uninstall clears it as well.",
"MQTT.AUS_RAEUMEN": "MQTT is off: the service clears the retained topics below %s once as soon as it runs (checking back with the broker).",
"MQTT.ALT_LISTE": "Previous prefixes noted for clearing: %s",
"LOG.LEEREN_FEHLER": "The log file could not be cleared: %s",
"WW_MQTT.GERAET_OK": "1 = the provider of this appliance answered in the last run; 0 = it is silent, the states are the last measured ones. Never retained.",
"WW_MQTT.GERAET_TS": "Time this appliance was last read (Unix time). Never retained.",

# ---- Welle Bild 16 (Weissware 0.9.42, 17.10.2026; Entwurf Welle 16 ww, E3/E4/E10-E12): drei Seiten aus
# dem LoxBerry-Plugins Musterprojekt - Kasten- und Hinweistitel, Kaesten BAUSTEIN.Sn_SCHRITTm, Hinweise
# BAUSTEIN.Sn_Hm, Tabellenzeilen BAUSTEIN.Zn_mm = "Typ | Name | Parameter | Eingaenge" (ww_bausteinseiten()
# in htmlauth/index.php); LOX: Bild, Link, Vorlage "Weissware Dienst", Kommentare der Impulsbefehle
# (ww_vorlage_ausgang()); WW_DFELD: Kommentare der Dienst-Werte (ww_dienst_felder()). -----------------
"BAUSTEIN.SCHRITTE_TITEL": "How to take over this page",
"BAUSTEIN.HINWEISE_TITEL": "Notes",
"BAUSTEIN.S1_SCHRITT1": "In the plugin tab “%s” log in to the manufacturer (Home Connect, Miele or SmartThings), start the service and wait until the appliance is listed under “%s”. Tab “%s” → “%s”: a line WEISSWARE;OK=1;ZUSTAND=… comes back",
"BAUSTEIN.S1_SCHRITT2": "Tab “%s” → under “Templates for appliance 1” the button “%s”. In Loxone Config: select “Virtual Inputs” in the tree, ribbon “Predefined HTTP devices → Import template…”. Import only ONCE (twice gives duplicate inputs). Fetch it only after the appliance has answered once – then the file only contains what it really delivers.",
"BAUSTEIN.S1_SCHRITT3": "Create the page “Weissware”, drag all commands from the container “Weissware 1 Status” (no. 1–15), plus the constant 1.",
"BAUSTEIN.S1_SCHRITT4": "Create four notifications (Periphery → Messages → Notification), texts as in the list, drag them onto the page. Each gets exactly one connection.",
"BAUSTEIN.S1_SCHRITT5": "Place the remaining blocks via the block search (key F5), parameters as in the list, connect from top to bottom. On the Value Validator no. 17 remove the tick at ‘En’ in the properties window (Config creates En inverted; otherwise constant 1 arrives as 0). Status “WW 1 Gerät”: click “+” four times first (V5–V8); enter the rows of the status blocks in the given order, the one without condition last. “Use in User Interface” on no. 1, 2, 3, 7 and on both status blocks.",
"BAUSTEIN.S1_SCHRITT6": "Save and transfer. Check: “Weissware-Zustand” shows “läuft – Werte … s alt”, “WW 1 Gerät” the state of the machine.",
"BAUSTEIN.S1_H1": "The fault message comes after 5 minutes at the earliest; “Abruf steht” (LoxBerry off) after 10 minutes plus 5.",
"BAUSTEIN.S1_H2": "On no. 17: if the LoxBerry stands still, all inputs keep their last value; only the frozen ALTER gives it away. If you lengthen the polling time on the container, set Tmc to ten times its value.",
"BAUSTEIN.S1_H3": "On no. 18, 25 and 27: digital inputs go on without a threshold switch – a threshold switch behind a polled input gives a short pulse at every poll, and a notification behind it then reports every minute.",
"BAUSTEIN.S1_H4": "Several appliances: one status template per appliance (“Weissware 2 Status” …) and the same blocks; lead the faults via further ORs (two inputs each) before no. 20 – never several sources directly into one notification.",
"BAUSTEIN.S1_H5": "“Fertig” stays until the appliance has been unloaded (door opened); that is why the reminder comes after one hour.",
"BAUSTEIN.S1_H6": "A dash from the plugin means “the manufacturer does not deliver this” – the input then keeps its last value.",
"BAUSTEIN.S1_H7": "No. 11 (Fernbedienung) and no. 15 (Fertig um) are there as inputs only: not every manufacturer delivers the remote control value, and a status does not show “Fertig um” as a time of day. Programme name and state text only exist over MQTT.",
"BAUSTEIN.S1_H8": "The announcement “… ist fertig” over a speaker is made by the plugin itself (tab Settings, off by default) – no block.",
"BAUSTEIN.S2_SCHRITT1": "In the plugin tab “%s” set the tick “%s” and save.",
"BAUSTEIN.S2_SCHRITT2": "Tab “%s” → “%s”. In Loxone Config: tree “Virtual Outputs” → “Predefined devices → Import template…”. Import only once; the template also carries the commands of the page “Weissware Steuerung und Verbrauch”.",
"BAUSTEIN.S2_SCHRITT3": "Provide your own measurements: “Netzleistung (eigene Quelle)” from your own electricity meter (plus = import, minus = feed-in), with a home battery “Ladeleistung Speicher 1 (eigene Quelle)” and “Ladezustand Speicher 1 (Proz) (eigene Quelle)”; with a dynamic tariff spot_awattar_rank – create a virtual input named as in the name table on the tab “Loxone integration” of the plugin Spotpreis aWATTar (from 1.2.38 on). Whatever you do not have stays free – that reason then simply drops out.",
"BAUSTEIN.S2_SCHRITT4": "Create the page “Weissware PV-Start”, drag the blocks of the list or place them via the block search (key F5) and connect them; every AND and OR has two inputs. Create new: the switches no. 14 and 21 and the push button no. 23 as virtual inputs (each with “Use in User Interface” on) and the notification “Meldung Weissware gestartet”. Schedule no. 19: enter ON daily 08:00–20:00. AND no. 26: negate input I2 – click its input point in Config; it then shows a small circle. Status “Weissware-Automatik jetzt”: click “+” four times first (V5–V8).",
"BAUSTEIN.S2_SCHRITT5": "Save, transfer, switch on “Weissware-Automatik” in the app (and, if wanted, “Günstigen Strom zum Waschen nutzen”).",
"BAUSTEIN.S2_SCHRITT6": "This is how washing works: fill the machine, select a programme, press “Remote start” on the appliance, leave. The page starts as soon as there has been enough surplus for 10 minutes (or the home battery is above 60 percent or one of the four cheapest hours is running) – only between 8 and 20 h.",
"BAUSTEIN.S2_H1": "Without a remote start release on the appliance nothing starts; the release usually expires with the programme and has to be given anew every time. That is why the automatic does not start a second time after the end of the programme.",
"BAUSTEIN.S2_H2": "On no. 28 and 29: one pulse per release. “WW 1 Start (Befehl)” has an on command only – “WW 1 Programm (Befehl)” sends “stop” when it drops and would abort the programme that has just started.",
"BAUSTEIN.S2_H3": "“Weissware jetzt starten” (push button) starts immediately, also without the automatic – but likewise only with a remote start release.",
"BAUSTEIN.S2_H4": "On no. 6: surplus = feed-in plus the charging power of the home battery. Adapt the threshold of 2000 W to your own machine (no. 7); if the house imports electricity, the surplus is 0.",
"BAUSTEIN.S2_H5": "A full home battery is a further reason to start – the machine then runs from the battery. With Spotpreis Octopus or Tibber, no. 10 comes from the rank command of that template.",
"BAUSTEIN.S2_H6": "No. 1 to 3 are digital inputs and go into the AND chain without a threshold switch.",
"BAUSTEIN.S2_H7": "Whether the appliance really starts is shown by “WW 1 Läuft” after the next poll, not by the answer to the command.",
"BAUSTEIN.S3_SCHRITT1": "The command template comes from the page “Weissware PV-Start”, step 2 (do not import it again). Tab “%s” → fetch “%s” and “%s” and import them in Loxone Config: select “Virtual Inputs” in the tree, ribbon “Predefined HTTP devices → Import template…”. The service values apply to all appliances together and are imported only once.",
"BAUSTEIN.S3_SCHRITT2": "Create the page “Weissware Steuerung und Verbrauch”, drag the four commands (no. 2, 4, 6, 8) and the inputs, create the four app buttons as virtual inputs (push button or switch as in the list, each with “Use in User Interface” on), connect them. Click “+” once on both status blocks first (V5).",
"BAUSTEIN.S3_SCHRITT3": "Save and transfer. Check: press “Weissware sofort abrufen” – “WW 1 Alter” drops after the next poll.",
"BAUSTEIN.S3_H1": "“Anhalten” and “Ein/Aus” usually need the remote control release on the appliance; without it the manufacturer cloud rejects them.",
"BAUSTEIN.S3_H2": "The switch does not remember what was pressed on the appliance by hand – it shows the last request from Loxone.",
"BAUSTEIN.S3_H3": "Home Connect delivers neither energy nor water, SmartThings no water; Miele both only with appliances with EcoFeedback.",
"BAUSTEIN.S3_H4": "“WW Dienst OK” and “WW Dienst Alter” from the template “Weissware Dienst” stay in the tree; the page “Weissware” already watches the polling per appliance.",
"BAUSTEIN.Z1_01": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 Zustand | 0 off, 1 ready, 2 running, 3 paused, 4 finished (not yet unloaded), 5 fault | —",
"BAUSTEIN.Z1_02": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 Läuft | 1 = a programme is running | —",
"BAUSTEIN.Z1_03": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 Fertig | 1 = programme finished, appliance not yet unloaded | —",
"BAUSTEIN.Z1_04": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 Verbunden | 1 = appliance reachable for the manufacturer cloud | —",
"BAUSTEIN.Z1_05": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 Tür | 1 = door open | —",
"BAUSTEIN.Z1_06": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 Fortschritt | programme progress in % (SmartThings delivers none) | —",
"BAUSTEIN.Z1_07": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 Restzeit | time left until the end of the programme in min | —",
"BAUSTEIN.Z1_08": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 Startvorwahl | minutes until the start when a delayed start is running on the appliance | —",
"BAUSTEIN.Z1_09": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 Laufzeit | runtime of the programme so far in min | —",
"BAUSTEIN.Z1_10": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 Fernstart | 1 = remote start is released on the appliance (usually expires with the end of the programme) | —",
"BAUSTEIN.Z1_11": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 Fernbedienung | 1 = remote control allowed (display only; not every manufacturer delivers the value) | —",
"BAUSTEIN.Z1_12": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 Netz | 1 = appliance switched on | —",
"BAUSTEIN.Z1_13": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 Alter | seconds since the last successful poll | —",
"BAUSTEIN.Z1_14": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 OK | 1 = last poll succeeded and is at most 15 minutes old; also 0 when the manufacturer cloud of this appliance is silent | —",
"BAUSTEIN.Z1_15": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 Fertig um | expected end of the programme as Unix time, only during a run; for your own logic (minus 1230768000 = Loxone time) | —",
"BAUSTEIN.Z1_16": "Constant | Konstante 1 | value 1 | —",
"BAUSTEIN.Z1_17": "Value Validator | Abruf steht | Tmc 600 s (ten polls of 60 s), Min -1, Max 2147483647; remove the tick at ‘En’ in the properties window | V = #13, En = #16",
"BAUSTEIN.Z1_18": "NOT | Weissware ohne frische Werte | — | I = #14",
"BAUSTEIN.Z1_19": "OR | Störung Weissware | — (no fresh values or polling stands still) | I1 = #18, I2 = output E of #17",
"BAUSTEIN.Z1_20": "Switch-On Delay | Störung Weissware bestätigt | 300 s | Input = #19",
"BAUSTEIN.Z1_21": "Notification | Meldung Weissware Störung | Text: Weissware – no fresh values from the appliance for 5 minutes (LoxBerry, plugin or manufacturer cloud does not answer). Read the status “Weissware-Zustand” in the app | Input = #20",
"BAUSTEIN.Z1_22": "Equal | Gerät meldet Störung | V2 = 5 (leave the second input open) | I1 = #1",
"BAUSTEIN.Z1_23": "Switch-On Delay | Gerätestörung bestätigt | 120 s (two polls) | Input = #22",
"BAUSTEIN.Z1_24": "Notification | Meldung Weissware Gerätestörung | Text: Weissware – the appliance reports a fault. Check on the appliance or in the manufacturer app | Input = #23",
"BAUSTEIN.Z1_25": "Switch-On Delay | Fertig bestätigt | 60 s (one poll) | Input = #3",
"BAUSTEIN.Z1_26": "Notification | Meldung Weissware fertig | Text: Weissware – the programme has finished, please unload | Input = #25",
"BAUSTEIN.Z1_27": "Switch-On Delay | Fertig, noch nicht ausgeräumt | 3600 s | Input = #3",
"BAUSTEIN.Z1_28": "Notification | Erinnerung Weissware ausräumen | Text: Weissware – the programme finished an hour ago and the appliance has not been unloaded yet | Input = #27",
"BAUSTEIN.Z1_29": "Status | Weissware-Zustand | rows: V3 = 1 “polling has stood still for at least 10 minutes – LoxBerry or plugin does not answer; open the LoxBerry in the browser, in the plugin tab Test ‘Fetch status’”; V1 = 0 “no fresh values, last successful poll <v2> s ago – in the plugin tab Settings check the login and the polling service, tab Test ‘Self-test of the service’”; V4 = 0 “appliance not reachable for the manufacturer cloud – switch the appliance on, check the Wi-Fi of the appliance in the manufacturer app”; without condition “running – values <v2> s old”; visualisation ON | V1 = #14, V2 = #13, V3 = output E of #17, V4 = #4",
"BAUSTEIN.Z1_30": "Status | WW 1 Gerät | rows: V1 = 5 “fault – check on the appliance or in the manufacturer app”; V1 = 2 “running – <v3> min left, <v2> % (for <v5> min)”; V1 = 3 “paused – <v3> min left”; V1 = 4 “finished – please unload”; V1 = 1 and V4 > 0 “delayed start – starts in <v4> min”; V6 = 1 “door open”; V1 = 1 and V7 = 1 “ready – remote start released, Loxone may start”; V1 = 1 “ready – to start from Loxone, select a programme on the appliance and press ‘Remote start’”; V1 = 0 and V8 = 1 “switched on, no programme”; V1 = 0 “off”; without condition “no state known”; visualisation ON | V1 = #1, V2 = #6, V3 = #7, V4 = #8, V5 = #9, V6 = #5, V7 = #10, V8 = #12",
"BAUSTEIN.Z2_01": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 Läuft | 1 = a programme is running (further instance, also on page “Weissware”) | —",
"BAUSTEIN.Z2_02": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 Fernstart | 1 = remote start released on the appliance (further instance) | —",
"BAUSTEIN.Z2_03": "Virtual HTTP input command (template “Weissware 1 Status”) | WW 1 OK | 1 = values fresh (further instance) | —",
"BAUSTEIN.Z2_04": "Virtual input | Netzleistung (eigene Quelle) | power at your own electricity meter in W, plus = import, minus = feed-in; the same input as on “AnkerSolix Steuerung” | —",
"BAUSTEIN.Z2_05": "Virtual input | Ladeleistung Speicher 1 (eigene Quelle) | charging power in W, plus = charging, minus = discharging; the same input as on “Einspeisebremse Speicher”; leave free without a battery | —",
"BAUSTEIN.Z2_06": "Formula | PV-Überschuss (W) | MAX(0;MAX(0;I2)-I1) – feed-in plus what the home battery is charging right now; 0 when importing from the grid | I1 = #4, I2 = #5",
"BAUSTEIN.Z2_07": "Threshold Switch | PV-Überschuss reicht | On 2000 / Off 1500 (W; washing machine about 2000 W, dishwasher about 2200 W while heating – adapt to your own machine) | Input = #6",
"BAUSTEIN.Z2_08": "Virtual input | Ladezustand Speicher 1 (Proz) (eigene Quelle) | state of charge in %; the same input as on “Einspeisebremse Speicher”; leave free without a battery (stays 0, never counts as full) | —",
"BAUSTEIN.Z2_09": "Threshold Switch | Hausakku voll genug | On 60 / Off 40 (%) | Input = #8",
"BAUSTEIN.Z2_10": "Virtual input (name as the MQTT gateway assigns it, plugin Spotpreis aWATTar) | spot_awattar_rank | rank of the current hour within the next 24 h, 1 = cheapest, -1 = no rank (further instance from the plugin Spotpreis aWATTar); leave free without a spot price plugin (then never cheap) | —",
"BAUSTEIN.Z2_11": "Greater | Preisrang bekannt | V2 = 0 (leave the second input open) | I1 = #10",
"BAUSTEIN.Z2_12": "Less or Equal | Günstige Stunde zum Waschen | V2 = 4 (leave the second input open; the four cheapest hours of the next 24 h) | I1 = #10",
"BAUSTEIN.Z2_13": "AND | Strom günstig zum Waschen | — | I1 = #11, I2 = #12",
"BAUSTEIN.Z2_14": "Virtual input (switch) | Günstigen Strom zum Waschen nutzen | in the app; off by default | —",
"BAUSTEIN.Z2_15": "AND | Günstig waschen gewünscht | — | I1 = #13, I2 = #14",
"BAUSTEIN.Z2_16": "OR | Akku oder günstiger Strom | — | I1 = #9, I2 = #15",
"BAUSTEIN.Z2_17": "OR | Waschen jetzt sinnvoll | — (surplus, full battery or cheap electricity) | I1 = #7, I2 = #16",
"BAUSTEIN.Z2_18": "Switch-On Delay | Grund hält an | 600 s (a passing cloud does not start a programme) | Input = #17",
"BAUSTEIN.Z2_19": "Schedule | Startfenster Weissware | ON = start allowed: daily 08:00–20:00, in all operating modes (no spinning at night) | —",
"BAUSTEIN.Z2_20": "AND | Grund im Startfenster | — | I1 = #18, I2 = output AQ of #19",
"BAUSTEIN.Z2_21": "Virtual input (switch) | Weissware-Automatik | in the app; off by default | —",
"BAUSTEIN.Z2_22": "AND | Automatik will starten | — | I1 = #20, I2 = #21",
"BAUSTEIN.Z2_23": "Virtual input (push button) | Weissware jetzt starten | in the app; starts the programme selected on the appliance immediately (also without the automatic) | —",
"BAUSTEIN.Z2_24": "OR | Startwunsch | — (automatic or push button) | I1 = #22, I2 = #23",
"BAUSTEIN.Z2_25": "AND | Fernstart frei | — (without the release the manufacturer cloud rejects every start) | I1 = #24, I2 = #2",
"BAUSTEIN.Z2_26": "AND | Gerät steht still | — | I1 = #25, I2 = #1 (negated)",
"BAUSTEIN.Z2_27": "AND | Start freigegeben | — (only with fresh values) | I1 = #26, I2 = #3",
"BAUSTEIN.Z2_28": "Edge Detection | Startimpuls | Pd 1 s; once per release, no repetition at every poll | Input = #27",
"BAUSTEIN.Z2_29": "Virtual output command (template “Weissware 1 Befehle”) | WW 1 Start (Befehl) | starts the programme selected on the appliance; on command only; enable write commands in the plugin | Input = output On of #28",
"BAUSTEIN.Z2_30": "AND | Läuft mit Automatik | — | I1 = #1, I2 = #21",
"BAUSTEIN.Z2_31": "Notification | Meldung Weissware gestartet | Text: Weissware – the appliance is running; the automatic is on (solar power, full home battery or cheap electricity) | Input = #30",
"BAUSTEIN.Z2_32": "Status | Weissware-Automatik jetzt | rows: V6 = 1 “running”; V1 = 0 “automatic off – surplus now <v7> W, price rank <v8>”; V2 = 1 “start command sent – the next poll shows whether the appliance starts”; V3 = 1 and V4 = 0 “reason present (surplus, battery or cheap electricity), but outside the start window 8–20 h”; V3 = 1 and V5 = 0 “reason present, but no remote start release – select a programme on the appliance and press ‘Remote start’”; V5 = 0 “waiting – no remote start released on the appliance yet; surplus <v7> W”; without condition “waiting for surplus (now <v7> W, 2000 W needed for 10 minutes), a full home battery or cheap electricity (rank <v8>)”; visualisation ON | V1 = #21, V2 = #27, V3 = #18, V4 = output AQ of #19, V5 = #2, V6 = #1, V7 = #6, V8 = #10",
"BAUSTEIN.Z3_01": "Virtual input (push button) | Weissware abbrechen | in the app | —",
"BAUSTEIN.Z3_02": "Virtual output command (template “Weissware 1 Befehle”) | WW 1 Abbrechen (Befehl) | aborts the running programme; on command only | Input = #1",
"BAUSTEIN.Z3_03": "Virtual input (switch) | Weissware anhalten | in the app; on = pause, off = resume; off by default | —",
"BAUSTEIN.Z3_04": "Virtual output command (template “Weissware 1 Befehle”) | WW 1 Pause (Befehl) | on = pause, off = resume (follows the switch) | Input = #3",
"BAUSTEIN.Z3_05": "Virtual input (switch) | Weissware Strom | in the app; on = switch the appliance on, off = switch it off | —",
"BAUSTEIN.Z3_06": "Virtual output command (template “Weissware 1 Befehle”) | WW 1 Ein/Aus (Befehl) | on = switch on, off = switch off; the same command within 60 s is not repeated | Input = #5",
"BAUSTEIN.Z3_07": "Virtual input (push button) | Weissware sofort abrufen | in the app | —",
"BAUSTEIN.Z3_08": "Virtual output command (template “Weissware 1 Befehle”) | WW Sofort abrufen (Befehl) | fetches new values immediately instead of waiting for the interval; applies to all appliances | Input = #7",
"BAUSTEIN.Z3_09": "Virtual HTTP input command (template “Weissware 1 Verbrauch”) | WW 1 Energie | energy consumption of the running programme in kWh (Home Connect delivers none) | —",
"BAUSTEIN.Z3_10": "Virtual HTTP input command (template “Weissware 1 Verbrauch”) | WW 1 Wasser | water consumption of the running programme in l (Home Connect and SmartThings deliver none) | —",
"BAUSTEIN.Z3_11": "Virtual HTTP input command (template “Weissware 1 Verbrauch”) | WW 1 Temperatur | set temperature in °C | —",
"BAUSTEIN.Z3_12": "Virtual HTTP input command (template “Weissware 1 Verbrauch”) | WW 1 Schleuderdrehzahl | set spin speed in rpm | —",
"BAUSTEIN.Z3_13": "Virtual HTTP input command (template “Weissware 1 Verbrauch”) | WW 1 OK (Verbrauch) | 1 = consumption values fresh | —",
"BAUSTEIN.Z3_14": "Status | WW 1 Programm und Verbrauch | rows: V5 = 0 “no fresh consumption values – read the status ‘Weissware-Zustand’”; without condition “<v3> °C, <v4> rpm; so far <v1.2> kWh and <v2> l (whatever the manufacturer cloud does not deliver stays as it is)”; visualisation ON | V1 = #9, V2 = #10, V3 = #11, V4 = #12, V5 = #13",
"BAUSTEIN.Z3_15": "Virtual HTTP input command (template “Weissware Dienst”) | WW Geräte | number of detected appliances | —",
"BAUSTEIN.Z3_16": "Virtual HTTP input command (template “Weissware Dienst”) | WW Geräte laufen | number of appliances in which a programme is running | —",
"BAUSTEIN.Z3_17": "Virtual HTTP input command (template “Weissware Dienst”) | WW Geräte fertig | number of appliances that have finished and are not yet unloaded | —",
"BAUSTEIN.Z3_18": "Virtual HTTP input command (template “Weissware Dienst”) | WW Fehlversuche | failed polls in a row; 0 = the last one succeeded | —",
"BAUSTEIN.Z3_19": "Virtual HTTP input command (template “Weissware Dienst”) | WW Anbieter still | number of manufacturer clouds that did not answer at the last poll | —",
"BAUSTEIN.Z3_20": "Status | Weissware-Dienst | rows: V4 >= 5 “<v4> polls failed in a row – the plugin slows down; in the plugin read the tab Log files”; V5 > 0 “<v5> manufacturer cloud(s) do not answer – in the plugin tab Settings check the login”; V4 > 0 “last poll failed (<v4> times in a row)”; V2 > 0 “<v2> of <v1> appliances running, <v3> finished”; without condition “<v1> appliances, none running, <v3> finished”; visualisation ON | V1 = #15, V2 = #16, V3 = #17, V4 = #18, V5 = #19",
"LOX.BILD_ALT": "Plugin blocks in Loxone Config",
"LOX.BILD_UNTERSCHRIFT": "Page “%s” in the LoxBerry plugins sample project. Config shortens long block names – see the table for the full names.",
"LOX.MUSTERPROJEKT": "The complete project file with all plugin pages and templates: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry plugins sample project</a>",
"LOX.VORLAGEN_DIENST": "Template for the summary values of the service (all appliances together)",
"LOX.K_VORLAGE_DIENST": "Service values as a template",
"LOX.VA_START": "Starts the programme selected on the appliance. Rejected as long as no remote start is released on the appliance.",
"LOX.VA_STOP": "Aborts the running programme.",
"WW_DFELD.LAEUFT": "Number of appliances in which a programme is running",
"WW_DFELD.FERTIG": "Number of appliances that have finished and are not yet unloaded",
"WW_DFELD.FEHLERFOLGE": "Failed polls in a row. 0 means: the last one succeeded.",
"WW_DFELD.AUSFAELLE": "Number of manufacturer clouds that did not answer at the last poll",
"WW_DFELD.ALTER": "Age of the snapshot",
}

# ---- Welle Mehrfach-Ziele Los C (30.10.2026): Spaetliste beim Zurueckspielen, aus mz_sprache_gegenprobe.py ----
DE.update({'EINST.SICH_SPAET': 'Nicht in der Sicherung, unverändert: %s (die Sicherung stammt aus einer früheren Fassung).'})
EN.update({'EINST.SICH_SPAET': 'Not in the backup, unchanged: %s (the backup comes from an earlier version).'})

# ---- Nachfassung 30.10.2026 nf2 (Abschnitt Anmeldung), aus nf_sprache_gegenprobe.py ----
DE.update({'EINST.ERNEUERUNG_SCHEITERT': 'angemeldet, aber Erneuerung scheitert – bitte neu anmelden', 'EINST.HC_ERSETZT': 'Es ist noch eine frühere Anmeldung gespeichert. Sie wird ersetzt, sobald Sie diese neue Anmeldung abschließen.'})
EN.update({'EINST.ERNEUERUNG_SCHEITERT': 'signed in, but renewal is failing – please sign in again', 'EINST.HC_ERSETZT': 'An earlier sign-in is still stored. It will be replaced as soon as you complete this new sign-in.'})

KOPF_DE = """; Weissware Cloud - Deutsch
;
; ERZEUGT von Werkzeuge/ww_sprache_erzeugen.py - nicht von Hand aendern,
; sonst geht die Aenderung beim naechsten Lauf verloren.
;
; Jeder Wert steht in doppelten Anfuehrungszeichen: bei parse_ini_file beginnt
; mit ';' ein Kommentar, und jede HTML-Entitaet endet auf ein Semikolon.
; Innerhalb eines Wertes darf kein doppeltes Anfuehrungszeichen stehen -
; HTML-Attribute deshalb einfach quoten: <span class='sm-mono'>.
;
; Schluessel, die im PHP durch ww_e() laufen, enthalten KEINE Auszeichnung und
; KEINE Entitaeten: sie wuerden dort ein zweites Mal maskiert und als
; "pr&amp;uuml;fen" auf dem Bildschirm landen.
"""

KOPF_EN = """; Weissware Cloud - English
;
; GENERATED by Werkzeuge/ww_sprache_erzeugen.py - do not edit by hand.
;
; English is the fallback level: keys missing in another language are taken
; from here, so this file must always be complete.
; Quote every value - see the German file for the reason.
"""


# Beschluss 14.08.2026: in den Sprachdateien steht "Lautstaerke" als Zeichen,
# nicht als Entitaet. Der Grund ist keine Geschmacksfrage, sondern eine
# Fehlerklasse: die Doppelmaskierung ww_e(ww_t('KEY')) zeigt den
# Entitaetentext woertlich an - der Benutzer liest "Pumpenw&auml;chter". Mit
# direkten Zeichen darf htmlspecialchars folgenlos zweimal laufen.
#
# NICHT umgesetzt werden:
#   &nbsp; und &shy; - ein unsichtbares Zeichen im Quelltext ist eine
#   Wartungsfalle, es sieht aus wie ein normales Leerzeichen.
#   &amp; &lt; &gt; &quot; &apos; - in HTML bedeutungstragend.
ZEICHEN = {
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


def entitaeten_aufloesen(text: str) -> str:
    for ent, zeichen in ZEICHEN.items():
        text = text.replace(ent, zeichen)
    return text


def php_dateien(wurzel: Path):
    return sorted(wurzel.rglob("*.php"))


def maskierte_schluessel(wurzel: Path) -> set:
    """Welche Schluessel laufen im PHP durch ww_e()?"""
    treffer = set()
    for f in php_dateien(wurzel):
        t = f.read_text(encoding="utf-8")
        for m in re.finditer(r"ww_e\(\s*ww_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t):
            treffer.add(m.group(1))
        # sprintf(ww_t('X'), ...) innerhalb von ww_e(): der Text selbst wird
        # dann ebenfalls maskiert.
        for m in re.finditer(r"ww_e\(\s*sprintf\(\s*ww_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t):
            treffer.add(m.group(1))
    return treffer


# Schluessel, die in der veroeffentlichten .ini stehen, aber im ganzen Plugin-Ordner
# (html, htmlauth, templates, bin; PHP, Python, Shell, JavaScript) nirgends benutzt werden.
# Gemessen an Weissware 0.9.51 am 06.11.2026 mit grep -r in beiden Schreibweisen
# (ruhe/Ruhe/RUHE, FEHLER_ZEIT): einzige Treffer sind die beiden language_*.ini. Es sind die
# Felder einer eigenen Ruhezeit der Ansage; die Nachtruhe regelt seither die gemeinsame
# Sprachausgabe (sprachausgabe.php, ansage_nachtruhe). Sie bleiben hier, damit die Ausgabe
# gleich der Auslieferung ist (Richtung ini -> Erzeuger) - streichen ist Sache des Plugins,
# im selben Zug mit diesem Eintrag. Ein Eintrag, der nicht mehr in DE steht, ist ein Fehler.
UNBENUTZT_IN_DER_AUSLIEFERUNG = {
    "WW_ANSAGE.FEHLER_ZEIT", "WW_ANSAGE.H_RUHE", "WW_ANSAGE.L_RUHE_BIS", "WW_ANSAGE.L_RUHE_VON",
}


def benutzte_schluessel(wurzel: Path) -> set:
    """Alle im PHP vorkommenden Schluessel, direkt oder als Zeichenkette."""
    treffer = set()
    for f in php_dateien(wurzel):
        t = f.read_text(encoding="utf-8")
        for m in re.finditer(r"ww_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t):
            treffer.add(m.group(1))
        for m in re.finditer(r"'(WW_[A-Z]+\.[A-Z0-9_]+|BAUSTEIN\.[A-Z0-9_]+)'", t):
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
    # Schluessel, die zur Laufzeit zusammengesetzt werden
    treffer |= {"EINST.DIENST_START", "EINST.DIENST_STOP", "EINST.DIENST_RESTART"}
    for feld in ("TAKT_RUHE", "TAKT_BETRIEB", "WARTEZEIT"):
        treffer.add("EINST.L_" + feld)
    # Bis Weissware 0.9.41 setzte ww_titel() den Schluessel WW_NAME.<FELD> zur
    # Laufzeit zusammen; seit 0.9.42 (Welle Bild 16, E11) traegt ww_titel() die
    # Befehlstitel fest deutsch im Code - [WW_NAME] gibt es nicht mehr.
    return treffer


# Schluessel, die in der ausgelieferten .ini NICHT alphabetisch stehen (dort von den
# Bauskripten der Gruppe 44 / Nachfassung nf2 eingefuegt). Damit der Erzeuger die Datei
# byteweise gleich erzeugt, stehen sie hier fest: (Abschnitt) -> (nach Schluessel | None
# = ans Ende, [Schluessel in dieser Folge]). Alles andere alphabetisch wie bisher.
NACHGESTELLT = {
    "EINST": ("ANGEMELDET", ["ERNEUERUNG_SCHEITERT", "HC_ERSETZT"]),
    "WW_MQTT": (None, ["ZAEHLER", "AUTO_WARTET", "AUTO_GRUND"]),
}


def schluessel_reihe(abschnitt: str, werte: dict) -> list:
    reihe = sorted(werte)
    if abschnitt not in NACHGESTELLT:
        return reihe
    nach, feste = NACHGESTELLT[abschnitt]
    feste = [s for s in feste if s in werte]
    reihe = [s for s in reihe if s not in feste]
    if nach is not None and nach in reihe:
        i = reihe.index(nach) + 1
        return reihe[:i] + feste + reihe[i:]
    return reihe + feste


def ini_schreiben(pfad: Path, kopf: str, texte: dict, sprache: str) -> None:
    abschnitte = {}
    for k, v in texte.items():
        a, s = k.split(".", 1)
        abschnitte.setdefault(a, {})[s] = v
    # Reihenfolge wie in der veroeffentlichten .ini (Weissware 0.9.45, Nachzug 01.11.2026):
    # LAUF..WW_DFELD standen frueher alphabetisch hinter WW_MQTT, BEFEHL/PRUEF/AUTO/G44
    # sind in Gruppe 44 hinten angefuegt worden. Neue Abschnitte weiter alphabetisch dahinter.
    reihenfolge = ["REITER", "LEGENDE", "ALLG", "EINST", "MQTT", "LOX", "BAUSTEIN",
                   "TEST", "LOG", "WW_FELD", "WW_VFELD", "WW_XFELD", "WW_MQTT",
                   "LAUF", "WACHE", "WW_ANSAGE", "WW_DFELD", "BEFEHL", "PRUEF", "AUTO", "G44"]
    zeilen = [kopf]
    for a in reihenfolge + [x for x in sorted(abschnitte) if x not in reihenfolge]:
        if a not in abschnitte:
            continue
        zeilen.append("\n[" + a + "]")
        for s in schluessel_reihe(a, abschnitte[a]):
            zeilen.append('%s = "%s"' % (s, entitaeten_aufloesen(abschnitte[a][s])))
    pfad.parent.mkdir(parents=True, exist_ok=True)
    # BINAER, und im Stil der ZIELDATEI. write_text uebersetzt unter Windows
    # jedes \n zu \r\n und unter Linux nicht - die Zeilenendenart einer
    # ausgelieferten Datei haetten damit das Betriebssystem des Erzeugers
    # bestimmt, nicht die Datei selbst. Gelesen wird der Stil deshalb aus der
    # vorhandenen Datei; gibt es sie noch nicht, gilt LF (140 von 146
    # Sprachdateien des Bestands fuehren LF).
    # Der Abschnitt [ANSAGE] der gemeinsamen Sprachausgabe kommt aus EINER Quelle.
    text = "\n".join(zeilen) + "\n" + "\n" + gemeinsam_pruefen.ini_abschnitt(sprache)
    ze = "\n"
    if pfad.is_file() and pfad.read_bytes().count(b"\r\n"):
        ze = "\r\n"
    pfad.write_bytes(text.replace("\n", ze).encode("utf-8"))


def pruefen(wurzel: Path) -> int:
    fehler = []
    benutzt = benutzte_schluessel(wurzel)
    maskiert = maskierte_schluessel(wurzel)

    fehlend_de = sorted(benutzt - set(DE))
    fehlend_en = sorted(benutzt - set(EN))
    unbenutzt = sorted(set(DE) - benutzt - UNBENUTZT_IN_DER_AUSLIEFERUNG)
    for k in sorted(UNBENUTZT_IN_DER_AUSLIEFERUNG - set(DE)):
        fehler.append("UNBENUTZT_IN_DER_AUSLIEFERUNG nennt %s, das in DE nicht mehr steht" % k)
    nur_de = sorted(set(DE) - set(EN))
    nur_en = sorted(set(EN) - set(DE))

    for k in sorted(set(DE) | set(EN)):
        if k.startswith("ANSAGE."):
            fehler.append("%s steht in der Tabelle - der Abschnitt [ANSAGE] kommt aus "
                          "gemeinsam_pruefen.py" % k)
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
                fehler.append("%s %s laeuft durch ww_e(), enthaelt aber Auszeichnung "
                              "oder eine Entitaet: %s" % (name, k, w))

    # Jeder Wert muss in eine INI-Zeile mit genau zwei Anfuehrungszeichen passen
    for name, tab in (("DE", DE), ("EN", EN)):
        for k, w in sorted(tab.items()):
            if '"' in w:
                fehler.append('%s %s enthaelt ein doppeltes Anfuehrungszeichen' % (name, k))
            if "\n" in w:
                fehler.append("%s %s enthaelt einen Zeilenumbruch" % (name, k))

    # Platzhalter muessen in beiden Sprachen gleich sein
    for k in sorted(set(DE) & set(EN)):
        pd = re.findall(r"%[sd]", DE[k])
        pe = re.findall(r"%[sd]", EN[k])
        if pd != pe:
            fehler.append("%s: Platzhalter unterschiedlich (DE %s, EN %s)" % (k, pd, pe))

    if fehler:
        for f in fehler:
            print("[FEHL]", f)
        return 1
    print("[OK]   %d Schluessel, DE und EN deckungsgleich, alle im PHP benutzt"
          " ausser %d aus UNBENUTZT_IN_DER_AUSLIEFERUNG (%s),"
          % (len(DE), len(UNBENUTZT_IN_DER_AUSLIEFERUNG), ", ".join(sorted(UNBENUTZT_IN_DER_AUSLIEFERUNG))))
    print("[OK]   %d davon maskiert und frei von Auszeichnung," % len(maskiert))
    print("[OK]   keine doppelten Anfuehrungszeichen, Platzhalter passen zusammen.")
    return 0


# ---- Gruppe 44 (Weissware 0.9.44): neue Schluessel, E6 gestrichen (sprache_g44.py) ----
DE.update({'WW_MQTT.ZAEHLER': 'Lebenszeichen 0…999, je Durchgang eins weiter (Gateway V2: Noncached anhaken; Ausfallerkennung in Loxone)', 'WW_MQTT.AUTO_WARTET': '1 = die Startlogik wartet auf ihre Stunde (Freigabe da, Startfenster offen)', 'WW_MQTT.AUTO_GRUND': 'Lage der Startlogik als Kennzahl: 0 aus, 1 keine Freigabe, 2 vor dem Startfenster, 3 günstigere Stunde kommt, 4 Speicher zu leer oder entlädt, 5 Quelle schweigt, 6 gestartet, 7 an der Frist gestartet, 8 Frist verstrichen, 9 erledigt, 10 Steuerung aus, 11 abgelehnt, 12 Gerät antwortet nicht', 'BEFEHL.F_BRUECKE': 'Befehlsbrücke', 'BEFEHL.F_PRUEFEN': 'Befehlsbrücke: Einrichtung (--pruefen)', 'BEFEHL.T_PRUEFEN_OK': 'in Ordnung (Zuordnung, mosquitto_sub/_pub, Optionsdatei).', 'BEFEHL.H_ANNEHMEN': "Startet die Befehlsbrücke: Loxone sendet <span class='sm-mono'>publish weissware/befehl/&lt;name&gt; &lt;wert&gt;</span> an den Ausgang „LoxBerry MQTT-Gateway“, die Antwort steht unter <span class='sm-mono'>…/quittung</span> („angenommen“ heißt: an den Dienst übergeben). Schaltende Befehle wirken nur mit <i>Schreibende Befehle zulassen</i>, ein Start nur mit der Fernstart-Freigabe am Gerät. Wirkt nur mit eingeschaltetem MQTT. Ab Werk aus.", 'BEFEHL.H_ENDPUNKT': 'Die virtuellen HTTP-Eingänge und -Ausgänge mit Token. Neue Anlagen nehmen das MQTT-Gateway V2 und die Befehlsbrücke; ausgeschaltet antwortet der Endpunkt mit 403. Eine Anlage, die von einer Fassung vor 0.9.44 aktualisiert wurde, hat ihn an.', 'BEFEHL.H_GERAETE': "Gerät 1 unter <span class='sm-mono'>…/befehl/&lt;name&gt;</span>, Gerät 2 bis 9 unter <span class='sm-mono'>…/befehl/&lt;n&gt;/&lt;name&gt;</span>; ein Gerät ab Nummer 10 nur über HTTP. Ein Programmschlüssel (nur Home Connect) bleibt dem HTTP-Weg vorbehalten.", 'BEFEHL.H_TITEL': 'Befehle aus Loxone über MQTT', 'BEFEHL.K_AUFFRISCHEN': 'Werte abfragen', 'BEFEHL.K_FORTSETZEN': 'Programm fortsetzen', 'BEFEHL.K_NETZ': 'Gerät ein (1) oder aus (0)', 'BEFEHL.K_PAUSE': 'Programm anhalten', 'BEFEHL.K_START': 'Gewähltes Programm starten', 'BEFEHL.K_STOP': 'Programm abbrechen', 'BEFEHL.K_VORLAGE': 'Vorlage Befehle über MQTT', 'BEFEHL.L_ANNEHMEN': 'Befehle über MQTT annehmen', 'BEFEHL.L_ENDPUNKT': 'HTTP-Endpunkt für Loxone (bisheriger Weg)', 'BEFEHL.M_SCHALTEN_FEHL': 'Die Befehlsbrücke ließ sich nicht schalten (%s): %s', 'BEFEHL.STATUS_BEFEHLE': 'Lebenszeichen der Befehlsbrücke', 'BEFEHL.T_ART': 'Art', 'BEFEHL.T_AUS': 'aus (Haken „Befehle über MQTT annehmen“ nicht gesetzt).', 'BEFEHL.T_DEFEKT': 'Die Einrichtung der Brücke ist fehlerhaft: %s', 'BEFEHL.T_ENDPUNKT_AUS': 'ausgeschaltet (Haken „HTTP-Endpunkt für Loxone“ im Reiter MQTT) – nicht aufgerufen.', 'BEFEHL.T_KEINER': 'Noch kein Befehl.', 'BEFEHL.T_LAEUFT': 'läuft (%d Prozess) – angenommen %d, abgelehnt %d.', 'BEFEHL.T_LETZTER': 'Letzter Befehl %s: %s, vor %d s.', 'BEFEHL.T_NICHT_DA': 'Die Befehlsbrücke (bin/befehlsbruecke.php) fehlt.', 'BEFEHL.T_STEHT': 'soll laufen, steht aber (%s) – der Wächter startet sie binnen einer Minute neu.', 'BEFEHL.T_TITEL': 'Titel in Loxone', 'BEFEHL.UDP_HINWEIS': 'Der UDP-Eingang des MQTT-Gateways (11884) nimmt im Heimnetz <b>ohne Anmeldung</b> an – jedes Gerät im WLAN kann einen Befehl schicken. Deshalb ist alles ab Werk aus, schaltende Befehle wirken zusätzlich nur mit <i>Schreibende Befehle zulassen</i>, und ein Start braucht die Fernstart-Freigabe am Gerät selbst.', 'PRUEF.V2_FEHLT': 'Es fehlen: %s.', 'PRUEF.V2_FRAGE': 'Gateway V2: sind alle Datenpunkte angehakt?', 'PRUEF.V2_LEER': 'nicht feststellbar – die Themenliste des Dienstes (bin/weissware.py) ist leer oder nicht lesbar.', 'PRUEF.V2_NC': 'Noncached falsch: %s.', 'PRUEF.V2_NICHT_EINGERICHTET': 'noch nicht eingerichtet – angehakt wird, sobald Werte kommen (erst einen Anbieter einschalten und anmelden).', 'PRUEF.V2_UNKLAR': 'nicht feststellbar – die Gateway-Fassung oder die Subscriptions des Gateways lassen sich nicht lesen.', 'PRUEF.V2_V1': 'trifft nicht zu (Gateway V1 – dort gilt das Abo im Reiter MQTT).', 'PRUEF.V2_ZAHL': '%d von %d Datenpunkten angehakt.', 'AUTO.ERKLAERUNG': "Das Plugin startet ein angehaktes Gerät selbst – nur, wenn am Gerät die <b>Fernstart-Freigabe</b> gegeben ist, <b>einmal je Freigabe</b> und nur im Startfenster. Quelle <b>Strompreis</b> (Vorgabe): Start, sobald die laufende Stunde zu den günstigsten Stunden bis zur Frist gehört (Werte vom Spotpreis-Plugin über <span class='sm-mono'>haus/strompreis</span>). Quelle <b>Speicher</b>: Start, sobald der Hausspeicher voll genug ist und nicht entlädt (<span class='sm-mono'>haus/speicher</span>). Schweigt die Quelle oder passt bis zur Frist nichts, startet das Gerät an der Frist. Wirkt nur mit <i>Schreibende Befehle zulassen</i>. Ab Werk ist kein Gerät angehakt.", 'AUTO.F_GERAET': 'Startlogik Gerät %s', 'AUTO.F_QUELLE': 'Startlogik: Quelle', 'AUTO.FEHLER_WERTE': 'Die Startlogik wurde nicht gespeichert: bitte die markierten Felder prüfen (Fensterbeginn vor der Frist, Stunden 1–24, Speicher 1–100 %).', 'AUTO.G0': 'aus', 'AUTO.G1': 'wartet auf die Fernstart-Freigabe am Gerät', 'AUTO.G2': 'wartet: Startfenster noch nicht offen', 'AUTO.G3': 'wartet: eine günstigere Stunde kommt noch', 'AUTO.G4': 'wartet: Speicher zu leer oder er entlädt', 'AUTO.G5': 'wartet: Quelle schweigt – an der Frist wird gestartet', 'AUTO.G6': 'gestartet', 'AUTO.G7': 'an der Frist gestartet', 'AUTO.G8': 'Frist verstrichen – nicht gestartet', 'AUTO.G9': 'erledigt (Gerät läuft bzw. Freigabe verbraucht)', 'AUTO.G10': 'Schreibende Befehle sind nicht zugelassen', 'AUTO.G11': 'Start vom Anbieter abgelehnt', 'AUTO.G12': 'der Anbieter des Geräts antwortet nicht', 'AUTO.H_FENSTER': 'Volle Stunden. Gestartet wird frühestens zum Fensterbeginn und spätestens zur Frist; eine Freigabe nach der Frist gilt bis zur Frist des nächsten Tages.', 'AUTO.H_FRIST_START': 'Schweigt die Quelle oder passt bis zur Frist nichts, wird an der Frist gestartet (höchstens eine Stunde danach), damit die Wäsche nicht liegen bleibt.', 'AUTO.H_QUELLE': 'Die Quelle gilt nur, solange ihr Anbieter lebt (Lebenszeichen binnen 120 s). Den PV-Überschuss kennt nur Loxone – dafür bleibt die Seite „PV-Start“.', 'AUTO.H_TITEL': 'Startlogik (Automatik)', 'AUTO.HINWEIS_STEUERUNG': 'Gespeichert. Die Startlogik wirkt erst mit „Schreibende Befehle zulassen“.', 'AUTO.KEINE_GERAETE': 'Noch kein Gerät erkannt – die Geräte erscheinen nach dem ersten erfolgreichen Abruf.', 'AUTO.L_FRIST': 'Frist (Uhr)', 'AUTO.L_FRIST_START': 'An der Frist auf jeden Fall starten', 'AUTO.L_QUELLE': 'Quelle', 'AUTO.L_SOC': 'Speicher mindestens (%)', 'AUTO.L_STUNDEN': 'Eine der günstigsten … Stunden', 'AUTO.L_VON': 'Startfenster ab (Uhr)', 'AUTO.NOCH_KEIN_LAUF': 'noch kein Lauf des Dienstes mit Startlogik', 'AUTO.PV_START': "Je Gerät entweder diese Startlogik <b>oder</b> die Loxone-Seite „PV-Start“ – nie beides, sonst kommen zwei Starts. Der Stand steht unter <span class='sm-mono'>geraetN/auto_wartet</span> und <span class='sm-mono'>geraetN/auto_grund</span> auch in Loxone.", 'AUTO.Q_ANBIETER': 'Anbieter: %s.', 'AUTO.Q_AUS': 'aus (kein Gerät angehakt)', 'AUTO.Q_FRISCH': '%s lebt (Lebenszeichen vor %d s).', 'AUTO.Q_KEIN_DIENST': 'nicht feststellbar – der Dienst läuft nicht.', 'AUTO.Q_KEINE_VERBINDUNG': 'keine Verbindung zum MQTT-Broker (%s).', 'AUTO.Q_NIE': '%s: noch kein Lebenszeichen live gesehen.', 'AUTO.Q_SCHWEIGT': '%s schweigt seit %d s – es gilt die Frist.', 'AUTO.Q_SPEICHER': 'Hausspeicher (haus/speicher)', 'AUTO.Q_STROMPREIS': 'Strompreis (haus/strompreis)', 'AUTO.T_AUTO': 'Automatik', 'AUTO.T_LAGE': 'Lage', 'G44.A_ENDPUNKT_AN': 'eingeschaltet – die HTTP-Vorlagen arbeiten.', 'G44.A_ENDPUNKT_AUS': 'ausgeschaltet – neue Anlagen nehmen das MQTT-Gateway V2 und die Befehlsbrücke.', 'G44.F_ENDPUNKT_HAKEN': 'HTTP-Endpunkt für Loxone', 'G44.H_V2': 'Gateway V2: diese Datenpunkte anhaken', 'G44.KACHEL_FASSUNG': 'Gateway-Fassung: %s', 'G44.LOG_BRUECKE': 'Befehlsbrücke (befehle_start.log)', 'G44.LOG_CRONERR': 'Fehlerausgabe des Wächters (cron.err)', 'G44.LOX_AUS': 'Dieser Weg ist ausgeschaltet (Reiter MQTT, Haken „HTTP-Endpunkt für Loxone“).', 'G44.LOX_BISHER': 'Die HTTP-Vorlagen unten sind der bisherige Weg. Neue Anlagen nehmen das MQTT-Gateway V2 (Datenpunkte im Reiter MQTT anhaken) und für Befehle die Befehlsbrücke (Vorlage im Reiter MQTT).', 'G44.LOX_MQTT_WEG': 'Die Eingänge legt das MQTT-Gateway V2 selbst an, sobald Werte kommen: die Datenpunkte im Reiter MQTT anhaken (Tabelle „Gateway V2: diese Datenpunkte anhaken“) und in Loxone je Wert einen Virtuellen Eingang mit dem Namen aus der Tabelle anlegen. Die frühere Vorlage mit Scheinadresse gibt es nicht mehr.', 'G44.T_NAME': 'Name im Gateway (Virtueller Eingang)', 'G44.V2_NUR_V1': 'Das MQTT-Gateway läuft in Fassung 1 – dort gilt das Abo oben. Mit Gateway V2 steht hier die Liste der anzuhakenden Datenpunkte.', 'G44.V2_TEXT': 'Unter System → MQTT Gateway → Subscriptions genau diese Datenpunkte anhaken, die mit „Noncached ja“ zusätzlich als Noncached (Lebenszeichen, damit die Ausfallerkennung in Loxone jeden Wert sieht). Textthemen und Zeitstempel stehen bewusst nicht darin. Ein Messwert ohne Aussage kommt als −1 an (Temperatur −999), ein Zustand ohne Aussage als Strich.'})
EN.update({'WW_MQTT.ZAEHLER': 'Sign of life 0…999, one step per run (Gateway V2: tick as noncached; failure detection in Loxone)', 'WW_MQTT.AUTO_WARTET': '1 = the start logic is waiting for its hour (permission given, start window open)', 'WW_MQTT.AUTO_GRUND': 'State of the start logic as a code: 0 off, 1 no permission, 2 before the start window, 3 a cheaper hour is coming, 4 storage too low or discharging, 5 source silent, 6 started, 7 started at the deadline, 8 deadline passed, 9 done, 10 control off, 11 rejected, 12 appliance not answering', 'BEFEHL.F_BRUECKE': 'Command bridge', 'BEFEHL.F_PRUEFEN': 'Command bridge: setup (--pruefen)', 'BEFEHL.T_PRUEFEN_OK': 'fine (mapping, mosquitto_sub/_pub, options file).', 'BEFEHL.H_ANNEHMEN': "Starts the command bridge: Loxone sends <span class='sm-mono'>publish weissware/befehl/&lt;name&gt; &lt;value&gt;</span> to the output “LoxBerry MQTT-Gateway”, the answer is under <span class='sm-mono'>…/quittung</span> (“accepted” means: handed to the service). Switching commands only work with <i>Allow write commands</i>, a start only with remote start enabled on the appliance. Works only with MQTT switched on. Off by default.", 'BEFEHL.H_ENDPUNKT': 'The virtual HTTP inputs and outputs with token. New installations use the MQTT gateway V2 and the command bridge; switched off, the endpoint answers 403. An installation updated from a version before 0.9.44 has it on.', 'BEFEHL.H_GERAETE': "Appliance 1 under <span class='sm-mono'>…/befehl/&lt;name&gt;</span>, appliances 2 to 9 under <span class='sm-mono'>…/befehl/&lt;n&gt;/&lt;name&gt;</span>; an appliance from number 10 only via HTTP. A program key (Home Connect only) stays with the HTTP path.", 'BEFEHL.H_TITEL': 'Commands from Loxone via MQTT', 'BEFEHL.K_AUFFRISCHEN': 'Poll values', 'BEFEHL.K_FORTSETZEN': 'Resume program', 'BEFEHL.K_NETZ': 'Appliance on (1) or off (0)', 'BEFEHL.K_PAUSE': 'Pause program', 'BEFEHL.K_START': 'Start the selected program', 'BEFEHL.K_STOP': 'Abort program', 'BEFEHL.K_VORLAGE': 'Template commands via MQTT', 'BEFEHL.L_ANNEHMEN': 'Accept commands via MQTT', 'BEFEHL.L_ENDPUNKT': 'HTTP endpoint for Loxone (previous path)', 'BEFEHL.M_SCHALTEN_FEHL': 'The command bridge could not be switched (%s): %s', 'BEFEHL.STATUS_BEFEHLE': 'Sign of life of the command bridge', 'BEFEHL.T_ART': 'Type', 'BEFEHL.T_AUS': 'off (“Accept commands via MQTT” not ticked).', 'BEFEHL.T_DEFEKT': 'The bridge setup is faulty: %s', 'BEFEHL.T_ENDPUNKT_AUS': 'switched off (“HTTP endpoint for Loxone” on the MQTT tab) – not called.', 'BEFEHL.T_KEINER': 'No command yet.', 'BEFEHL.T_LAEUFT': 'running (%d process) – accepted %d, rejected %d.', 'BEFEHL.T_LETZTER': 'Last command %s: %s, %d s ago.', 'BEFEHL.T_NICHT_DA': 'The command bridge (bin/befehlsbruecke.php) is missing.', 'BEFEHL.T_STEHT': 'should run but is stopped (%s) – the watchdog restarts it within a minute.', 'BEFEHL.T_TITEL': 'Title in Loxone', 'BEFEHL.UDP_HINWEIS': 'The UDP input of the MQTT gateway (11884) accepts messages in the home network <b>without login</b> – any device on the Wi-Fi can send a command. That is why everything is off by default, switching commands additionally need <i>Allow write commands</i>, and a start needs remote start enabled on the appliance itself.', 'PRUEF.V2_FEHLT': 'Missing: %s.', 'PRUEF.V2_FRAGE': 'Gateway V2: are all data points ticked?', 'PRUEF.V2_LEER': 'cannot be determined – the topic list of the service (bin/weissware.py) is empty or unreadable.', 'PRUEF.V2_NC': 'Noncached wrong: %s.', 'PRUEF.V2_NICHT_EINGERICHTET': 'not set up yet – tick them as soon as values arrive (first switch on and sign in to a provider).', 'PRUEF.V2_UNKLAR': 'cannot be determined – the gateway version or the gateway subscriptions cannot be read.', 'PRUEF.V2_V1': 'not applicable (gateway V1 – the subscription on the MQTT tab applies there).', 'PRUEF.V2_ZAHL': '%d of %d data points ticked.', 'AUTO.ERKLAERUNG': "The plugin starts a ticked appliance by itself – only when <b>remote start</b> is enabled on the appliance, <b>once per enabling</b> and only within the start window. Source <b>electricity price</b> (default): start as soon as the current hour is among the cheapest hours until the deadline (values from the spot price plugin via <span class='sm-mono'>haus/strompreis</span>). Source <b>storage</b>: start as soon as the home battery is full enough and not discharging (<span class='sm-mono'>haus/speicher</span>). If the source is silent or nothing fits until the deadline, the appliance starts at the deadline. Works only with <i>Allow write commands</i>. No appliance is ticked by default.", 'AUTO.F_GERAET': 'Start logic appliance %s', 'AUTO.F_QUELLE': 'Start logic: source', 'AUTO.FEHLER_WERTE': 'The start logic was not saved: please check the marked fields (window start before the deadline, hours 1–24, storage 1–100 %).', 'AUTO.G0': 'off', 'AUTO.G1': 'waiting for remote start to be enabled on the appliance', 'AUTO.G2': 'waiting: start window not open yet', 'AUTO.G3': 'waiting: a cheaper hour is still coming', 'AUTO.G4': 'waiting: storage too low or discharging', 'AUTO.G5': 'waiting: source silent – will start at the deadline', 'AUTO.G6': 'started', 'AUTO.G7': 'started at the deadline', 'AUTO.G8': 'deadline passed – not started', 'AUTO.G9': 'done (appliance running or permission used)', 'AUTO.G10': 'write commands are not allowed', 'AUTO.G11': 'start rejected by the provider', 'AUTO.G12': "the appliance's provider is not answering", 'AUTO.H_FENSTER': "Full hours. The start happens at the earliest at the window start and at the latest at the deadline; an enabling after the deadline counts until the next day's deadline.", 'AUTO.H_FRIST_START': 'If the source is silent or nothing fits until the deadline, the appliance starts at the deadline (at most one hour after it) so the laundry does not stay in the machine.', 'AUTO.H_QUELLE': 'The source only counts while its provider is alive (sign of life within 120 s). Only Loxone knows the PV surplus – the “PV start” page stays for that.', 'AUTO.H_TITEL': 'Start logic (automatic)', 'AUTO.HINWEIS_STEUERUNG': 'Saved. The start logic only works with “Allow write commands”.', 'AUTO.KEINE_GERAETE': 'No appliance detected yet – appliances appear after the first successful poll.', 'AUTO.L_FRIST': "Deadline (o'clock)", 'AUTO.L_FRIST_START': 'Start at the deadline in any case', 'AUTO.L_QUELLE': 'Source', 'AUTO.L_SOC': 'Storage at least (%)', 'AUTO.L_STUNDEN': 'One of the cheapest … hours', 'AUTO.L_VON': "Start window from (o'clock)", 'AUTO.NOCH_KEIN_LAUF': 'no service run with start logic yet', 'AUTO.PV_START': "Per appliance either this start logic <b>or</b> the Loxone page “PV start” – never both, otherwise two starts arrive. The state is also available in Loxone under <span class='sm-mono'>geraetN/auto_wartet</span> and <span class='sm-mono'>geraetN/auto_grund</span>.", 'AUTO.Q_ANBIETER': 'Provider: %s.', 'AUTO.Q_AUS': 'off (no appliance ticked)', 'AUTO.Q_FRISCH': '%s is alive (sign of life %d s ago).', 'AUTO.Q_KEIN_DIENST': 'cannot be determined – the service is not running.', 'AUTO.Q_KEINE_VERBINDUNG': 'no connection to the MQTT broker (%s).', 'AUTO.Q_NIE': '%s: no live sign of life seen yet.', 'AUTO.Q_SCHWEIGT': '%s silent for %d s – the deadline applies.', 'AUTO.Q_SPEICHER': 'Home battery (haus/speicher)', 'AUTO.Q_STROMPREIS': 'Electricity price (haus/strompreis)', 'AUTO.T_AUTO': 'Automatic', 'AUTO.T_LAGE': 'State', 'G44.A_ENDPUNKT_AN': 'switched on – the HTTP templates work.', 'G44.A_ENDPUNKT_AUS': 'switched off – new installations use the MQTT gateway V2 and the command bridge.', 'G44.F_ENDPUNKT_HAKEN': 'HTTP endpoint for Loxone', 'G44.H_V2': 'Gateway V2: tick these data points', 'G44.KACHEL_FASSUNG': 'gateway version: %s', 'G44.LOG_BRUECKE': 'Command bridge (befehle_start.log)', 'G44.LOG_CRONERR': 'Error output of the watchdog (cron.err)', 'G44.LOX_AUS': 'This path is switched off (MQTT tab, “HTTP endpoint for Loxone”).', 'G44.LOX_BISHER': 'The HTTP templates below are the previous path. New installations use the MQTT gateway V2 (tick the data points on the MQTT tab) and the command bridge for commands (template on the MQTT tab).', 'G44.LOX_MQTT_WEG': 'The MQTT gateway V2 creates the inputs itself as soon as values arrive: tick the data points on the MQTT tab (table “Gateway V2: tick these data points”) and create one virtual input per value in Loxone with the name from the table. The former template with a dummy address no longer exists.', 'G44.T_NAME': 'Name in the gateway (virtual input)', 'G44.V2_NUR_V1': 'The MQTT gateway runs version 1 – the subscription above applies. With gateway V2 the list of data points to tick appears here.', 'G44.V2_TEXT': 'Under System → MQTT Gateway → Subscriptions tick exactly these data points, those with “Noncached yes” additionally as noncached (signs of life, so the failure detection in Loxone sees every value). Text topics and time stamps are left out on purpose. A measurement without a value arrives as −1 (temperature −999), a state without a value as a dash.'})
for _d in (DE, EN):
    _d.pop('LOX.K_VORLAGE_MQTT', None)
    _d.pop('LOX.MQTT_VORLAGE_HINWEIS', None)
DE['LOX.VORLAGEN_MQTT'] = 'Der MQTT-Weg (Gateway V2)'
EN['LOX.VORLAGEN_MQTT'] = 'The MQTT path (gateway V2)'


def main() -> int:
    wurzel = Path(sys.argv[1])
    code = pruefen(wurzel)
    if "--pruefen" in sys.argv:
        return code
    if code:
        print("Es wurde nichts geschrieben.")
        return code
    ini_schreiben(wurzel / "templates/lang/language_de.ini", KOPF_DE, DE, "de")
    ini_schreiben(wurzel / "templates/lang/language_en.ini", KOPF_EN, EN, "en")
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
