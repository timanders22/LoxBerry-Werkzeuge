#!/usr/bin/env python3
"""Erzeugt die Sprachdateien des Weissware-Plugins.

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

Aufruf:  ww_sprache_erzeugen.py <pluginordner> [--pruefen]
"""

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Deutsch
# ---------------------------------------------------------------------------
DE = {

# ---- Reiter und Legende ----------------------------------------------------
"REITER.EINSTELLUNGEN": "Einstellungen",
"REITER.LOXONE": "Einbindung in Loxone",
"REITER.TEST": "Test",
"REITER.LOG": "Logdateien",

"LEGENDE.LESEN": "Ansehen &mdash; fragt nur ab, ver&auml;ndert nichts",
"LEGENDE.TECHNIK": "Technische Auskunft &mdash; f&uuml;r die Fehlersuche",
"LEGENDE.AKTION": "L&ouml;st etwas aus &mdash; sendet oder ver&auml;ndert",
"LEGENDE.AKTION_TOKEN": "L&ouml;st etwas aus &mdash; ein neues Token macht alle Adressen im Miniserver ung&uuml;ltig",
"LEGENDE.AKTION_LOG": "L&ouml;st etwas aus &mdash; die bisherigen Zeilen sind danach fort",

# ---- Allgemein -------------------------------------------------------------
"ALLG.BEANSTANDUNG": "Es wurde nichts gespeichert. Bitte diese Punkte berichtigen:",
"ALLG.DIENST": "Abrufdienst",
"ALLG.LAEUFT": "läuft",
"ALLG.GESTOPPT": "gestoppt",
"ALLG.KEINE_PID": "keine Prozessnummer",
"ALLG.LETZTER_ABRUF": "Letzter Abruf",
"ALLG.NIE": "noch nie",
"ALLG.GATEWAY": "Gateway des LoxBerry",
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
"EINST.H_DIENST": "Abrufdienst",
"EINST.DIENST_ERKLAERUNG": "Der Dienst holt die Werte im eingestellten Takt bei den eingeschalteten Anbietern und legt sie ab. Oberfl&auml;che und Miniserver lesen nur das Abgelegte &mdash; sie sprechen nie selbst mit dem Anbieter.",
"EINST.K_START": "Dienst starten",
"EINST.K_NEUSTART": "Dienst neu starten",
"EINST.K_STOPP": "Dienst anhalten",
"EINST.K_SITZUNG": "Anmeldung neu erzwingen",
"EINST.DIENST_START": "Dienst gestartet:",
"EINST.DIENST_STOP": "Dienst angehalten:",
"EINST.DIENST_RESTART": "Dienst neu gestartet:",
"EINST.SITZUNG_VERWORFEN": "Die Anmeldemarken wurden gelöscht. Beim nächsten Abruf meldet sich der Dienst mit Benutzername und Passwort neu an.",
"EINST.SITZUNG_KEINE": "Es waren keine Anmeldemarken gespeichert.",
"EINST.PYTHON_ZU_ALT": "<b>Der Dienst kann nicht laufen.</b> Die virtuelle Python-Umgebung dieses Plugins nutzt ein Python &auml;lter als 3.9; die Bibliothek carconnectivity verlangt 3.9 oder neuer. Das sollte auf keinem heutigen LoxBerry vorkommen (Debian 12 liefert 3.11) &mdash; wenn doch, ist die virtuelle Umgebung kaputt. Abhilfe: Plugin neu installieren.",


"EINST.H_TAKT": "Abholtakt",

"EINST.H_STEUERUNG": "Schreibende Befehle",
"EINST.STEUERUNG_ERKLAERUNG": "Ab Werk <b>gesperrt</b>. Schreibende Befehle starten und stoppen echte Maschinen in einem leeren Haus. Ein versehentlich gestartetes Waschprogramm l&auml;uft, ohne dass jemand W&auml;sche eingef&uuml;llt hat; ein abgebrochenes bleibt nass in der Trommel. Erst freigeben, wenn die Lesewerte im Reiter Test stimmen. <b>Zwei Sicherungen bleiben ohnehin:</b> Das Ger&auml;t muss die Fernstart-Freigabe haben &mdash; die gibt man am Ger&auml;t selbst, und sie erlischt meist nach dem Programm &mdash;, und ein Programm muss dort gew&auml;hlt sein.",
"EINST.L_STEUERUNG_EIN": "Schreibende Befehle zulassen",
"EINST.L_WARTEZEIT": "Wartezeit auf die Antwort (Sekunden)",
"EINST.H_WARTEZEIT": "So lange wartet die Oberfl&auml;che, bis der Dienst einen Befehl beantwortet hat. Danach meldet sie <span class='sm-mono'>OK=2</span> &mdash; eingereiht, Ergebnis unbekannt. Es wird bewusst kein Erfolg gemeldet, den niemand gepr&uuml;ft hat.",

"EINST.L_MQTT_EIN": "Werte über MQTT veröffentlichen",
"EINST.L_MQTT_TOPIC": "Themenpräfix",
"EINST.H_MQTT_TOPIC": "Erlaubt sind Buchstaben, Ziffern, Bindestrich, Unterstrich und Schr&auml;gstrich. Aus dem Pr&auml;fix ergeben sich alle Themen, siehe Reiter MQTT.",

"EINST.GESPEICHERT": "Die Einstellungen wurden gespeichert.",
"EINST.FEHLER_ZAHL": "%s: bitte eine ganze Zahl eintragen.",
"EINST.FEHLER_BEREICH": "%s: der Wert muss zwischen %d und %d liegen.",
"EINST.FEHLER_TOPIC": "Das Themenpräfix enthält unerlaubte Zeichen. Erlaubt sind Buchstaben, Ziffern, Bindestrich, Unterstrich und Schrägstrich.",
"EINST.FEHLER_ZUGANG_SPEICHERN": "Die Zugangsdatei ließ sich nicht schreiben. Rechte des Konfigurationsordners prüfen.",
"EINST.FEHLER_SPEICHERN": "Die Konfiguration ließ sich nicht schreiben: %s",

"EINST.H_ERKANNT": "Erkannte Geräte",
"EINST.T_NR": "Nr.",

# ---- MQTT ------------------------------------------------------------------
"MQTT.H_ZUSTAND": "Zustand des MQTT-Gateways",
"MQTT.GATEWAY_ERKLAERUNG": "Der MQTT-Gateway ist seit LoxBerry 3 <b>Bestandteil des Systems</b> und kein Plugin. Er wird nicht nachinstalliert, sondern unter <i>System &rarr; MQTT Gateway</i> eingeschaltet.",
"MQTT.NICHT_GEFUNDEN": "In der <span class='sm-mono'>general.json</span> des LoxBerry ist kein MQTT-Abschnitt zu finden. Ohne den kann nichts gesendet werden.",
"MQTT.AUTOSTART_AUS": "Der Gateway ist <b>nicht</b> auf Autostart gestellt. Der Broker-Eintrag allein gen&uuml;gt nicht &mdash; er ist ab Werk gesetzt und sagt nichts dar&uuml;ber aus, ob Nachrichten ankommen k&ouml;nnen. Ma&szlig;geblich ist der Autostart unter <i>System &rarr; MQTT Gateway</i>.",
"MQTT.AUTOSTART_EIN": "Der Gateway ist auf Autostart gestellt. Nachrichten dieses Plugins k&ouml;nnen also ankommen.",
"MQTT.T_AUTOSTART": "Autostart des Gateways",
"MQTT.T_BROKER": "Broker",
"MQTT.T_UDP": "UDP-Eingangsport",
"MQTT.T_PLUGIN": "Veröffentlichen durch dieses Plugin",
"MQTT.H_ABO": "Das einzutragende Abo",
"MQTT.ABO_WARNUNG": "<b>Ohne diesen Eintrag kommt am Miniserver nichts an.</b> Das ist die h&auml;ufigste Fehlerursache &uuml;berhaupt.",
"MQTT.ABO_SCHRITTE": "<i>System &rarr; MQTT Gateway</i> &rarr; Abschnitt <i>Subscriptions</i> &rarr; folgende Zeile eintragen und speichern:",
"MQTT.H_THEMEN": "Alle veröffentlichten Themen",
"MQTT.THEMEN_ERKLAERUNG": "Ein Thema, dessen Wert dieses Ger&auml;t nicht liefert, wird gar nicht erst gesendet &mdash; es entsteht also kein Thema mit einer erfundenen Null.",
"MQTT.T_THEMA": "Thema",
"MQTT.T_BEDEUTUNG": "Bedeutung",
"MQTT.PLATZHALTER": "<b>N</b> steht f&uuml;r die laufende Nummer des Ger&auml;ts, also 1 f&uuml;r das erste.",

# ---- Loxone ----------------------------------------------------------------
"LOX.H_TITEL": "Einbindung in Loxone",
"LOX.EINLEITUNG": "Neun Schritte. Wer sie von oben nach unten abarbeitet, hat am Ende eine funktionierende Einbindung &mdash; einschlie&szlig;lich der kompletten Baustein-Liste in Schritt 8.",
"LOX.S1_TITEL": "Schritt 1: Weg festlegen",
"LOX.S1_TEXT": "Es gibt zwei Wege, und <b>MQTT ist der Regelweg</b>. Der Gateway erzeugt die Namen der virtuellen Eing&auml;nge selbst; in Loxone gen&uuml;gt dann ein passend benannter virtueller Eingang. Der Weg &uuml;ber HTTP verlangt je Wert eine eigene Befehlserkennung, daf&uuml;r kommt alles in <b>einem</b> Abruf und man sieht im Browser sofort, was ankommt. Wer neu anf&auml;ngt, nimmt MQTT; wer nur wenige Werte braucht, f&auml;hrt mit HTTP schneller ans Ziel. Beides gleichzeitig geht auch.",
"LOX.S2_TITEL": "Schritt 2: Abo im MQTT-Gateway eintragen",
"LOX.S2_TEXT": "Nur n&ouml;tig, wenn Sie den MQTT-Weg gehen. Unter <i>System &rarr; MQTT Gateway</i> im Abschnitt <i>Subscriptions</i> eintragen:",
"LOX.S2_WARNUNG": "<b>Ohne diesen Eintrag kommt am Miniserver nichts an.</b> Das ist die h&auml;ufigste Fehlerursache &uuml;berhaupt &mdash; das Plugin sendet, aber niemand h&ouml;rt zu.",
"LOX.S3_TITEL": "Schritt 3: Virtuellen HTTP-Eingang für die Hauptwerte anlegen",
"LOX.S3_TEXT": "In Loxone Config: <i>Virtueller Eingang &rarr; Virtueller HTTP-Eingang</i>. Adresse und Zyklus:",
"LOX.S3_BEFEHLE": "Darunter je Wert eine <i>Befehlserkennung</i>. Die Vorlage unten legt alle auf einmal an &mdash; das ist weniger m&uuml;hsam und weniger fehleranf&auml;llig als das Abtippen.",
"LOX.S3_STRICH": "<b>Ein Strich statt einer Zahl bedeutet: dieser Wert liegt nicht vor.</b> Es wird bewusst keine 0 gesendet &mdash; eine 0 w&auml;re eine stille Falschaussage. Loxone beh&auml;lt in diesem Fall den letzten g&uuml;ltigen Wert. Genau deshalb braucht es die Ausfallerkennung aus Schritt 7.",
"LOX.FEHLER_VORLAGE": "Die angeforderte Vorlage gibt es nicht. Es wurde nichts erzeugt.",
"LOX.VORLAGEN_FUER": "Vorlagen für Gerät %s",
"LOX.VORLAGEN_MQTT": "Vorlage für den MQTT-Weg",
"LOX.VORLAGEN_HINWEIS": "So werden sie in Loxone Config eingespielt: im Baum links <b>Virtuelle Eingänge</b> wählen, dann im Menüband auf <b>Vordefinierte HTTP-Geräte &rarr; Vorlage Importieren&hellip;</b>. Die Befehlsdatei (VQ_&hellip;) geht denselben Weg unter <b>Virtuelle Ausgänge &rarr; Vordefinierte Geräte &rarr; Vorlage Importieren&hellip;</b> &mdash; dort heißt der Knopf ohne den Zusatz HTTP. Loxone legt dabei <b>neu an</b> und überschreibt nichts &mdash; zweimal eingelesen ergibt doppelte Bausteine. Angelegt werden nur Felder, die das Gerät beim letzten Abruf wirklich geliefert hat; was deshalb fehlt, steht als Anmerkung in der Datei.",
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
"LOX.S4_TEXT": "Ein weiterer virtueller HTTP-Eingang nach demselben Muster wie Schritt 3, mit der Aktion <span class='sm-mono'>verbrauch</span>. Ein Zyklus von 300 Sekunden gen&uuml;gt.",

"LOX.S5_TITEL": "Schritt 5: Befehle senden (virtueller Ausgang)",
"LOX.S5_TEXT": "Nur n&ouml;tig, wenn Loxone etwas ausl&ouml;sen soll. In Loxone Config einen <i>Virtuellen Ausgang</i> mit der unten stehenden Adresse anlegen und darunter je Befehl einen <i>Virtuellen Ausgang Befehl</i>. Im Befehlstext steht <span class='sm-mono'>&lt;v&gt;</span> f&uuml;r den &uuml;bergebenen Wert.",
"LOX.T_VA_ADRESSE": "Adresse des virtuellen Ausgangs",
"LOX.T_VA_ABRUF": "Sofortabruf auslösen",
"LOX.S5_WARNUNG": "Zwei Dinge, die man vorher wissen sollte. <b>Erstens:</b> Schreibende Befehle sind ab Werk gesperrt und m&uuml;ssen im Reiter Einstellungen erst freigegeben werden. <b>Zweitens:</b> Eine Antwort mit <span class='sm-mono'>OK=1</span> hei&szlig;t, dass der Anbieter die Anfrage angenommen hat. Ob das Ger&auml;t anl&auml;uft, zeigt erst der n&auml;chste Abruf &mdash; wer sicher sein will, wertet <span class='sm-mono'>LAEUFT</span> aus und nicht die Antwort auf den Befehl.",

"LOX.S6_TITEL": "Schritt 6: Das Token",
"LOX.T_TOKEN": "Token dieses Plugins",
"LOX.S6_TEXT": "Der Endpunkt liegt im unangemeldeten Bereich, damit Loxone ihn ohne Zugangsdaten erreicht. Gesch&uuml;tzt ist er durch dieses Token. Es steckt in jeder Adresse, die Sie im Miniserver eintragen &mdash; <b>ein neues Token macht alle diese Adressen auf einen Schlag ung&uuml;ltig</b> und muss &uuml;berall nachgetragen werden. W&uuml;rfeln Sie es also nur neu, wenn es tats&auml;chlich in falsche H&auml;nde geraten ist.",

"LOX.S7_TITEL": "Schritt 7: Ausfallerkennung",
"LOX.S7_TEXT": "Schweigt ein Anbieter, behalten die virtuellen Eing&auml;nge ihren letzten Wert. In der App sieht dann alles normal aus, obwohl seit Stunden nichts mehr angekommen ist. Deshalb wird der Wert <span class='sm-mono'>ALTER</span> mitgef&uuml;hrt: er sagt, wie alt das Abbild in Sekunden ist. Die Schwelle daf&uuml;r geh&ouml;rt <b>deutlich &uuml;ber den Ruhetakt</b> &mdash; bei 300 Sekunden sind 1200 Sekunden ein brauchbarer Wert.",

"LOX.S8_TITEL": "Schritt 8: Komplette Baustein-Liste zum 1:1-Nachbauen",
"LOX.S8_TEXT": "Jede Zeile ein Baustein. Loxone Config f&uuml;hrt alle in der Baustein-Suche (Taste F5). Die Zeilen 1 bis 12 sind die virtuellen Eing&auml;nge aus Schritt 3 und 4. Nachgebaut wird der Fall, um den es den meisten geht: <b>Waschen, wenn die Sonne scheint</b> &mdash; und eine Meldung, wenn das Programm fertig ist.",
"LOX.S8_ERLAEUTERUNG": "<p><b>Zu #13 bis #16 &mdash; der eigentliche Zweck:</b> Der Schwellwertschalter #13 vergleicht den PV-&Uuml;berschuss mit dem, was die Maschine zieht (Waschmaschine etwa 2000 W, Geschirrsp&uuml;ler etwa 2200 W in der Aufheizphase). Die UND-Verkn&uuml;pfung #14 l&auml;sst den Start nur zu, wenn zugleich die Fernstart-Freigabe vorliegt und das Ger&auml;t nicht schon l&auml;uft. Die Einschaltverz&ouml;gerung #15 von zehn Minuten verhindert, dass eine vorbeiziehende Wolke ein Waschprogramm ausl&ouml;st.</p><p><b>Zu #17 und #18:</b> Beide freiwillig. Wer einen Hausakku hat, will nicht waschen, solange der leer ist; wer einen dynamischen Tarif hat, will notfalls auch ohne Sonne waschen, wenn der Strom billig ist. Beide Bausteine kommen aus anderen Plugins &mdash; dieses liefert sie nicht.</p><p><b>Zu #21 und #22:</b> Der Benachrichtigungs-Baustein sendet nur beim Wechsel von Aus auf Ein &mdash; genau richtig f&uuml;r &bdquo;Geschirrsp&uuml;ler ist fertig&ldquo;. Niemals mehrere Ger&auml;te direkt an seinen Eingang: eine dauerhaft aktive Quelle verschluckt alle &uuml;brigen. Erst &uuml;ber ODER zusammenf&uuml;hren.</p><p><b>Zu #25:</b> Die Schwelle liegt beim Vierfachen des Ruhetakts. Wer sie knapper setzt, bekommt bei jedem einzelnen verpassten Durchlauf eine Meldung.</p><p><b>Zu #30:</b> Ohne Fernstart-Freigabe weist der Anbieter jeden Start ab. Der Befehl gar nicht erst zu senden spart eine Fehlermeldung und eine Anfrage. <b>Loxone-Zeitrechnung:</b> Sekunden seit dem 01.01.2009. Liefert ein Zeit-Baustein Unix-Zeit (Werte um 1,23 Milliarden), sind 1230768000 abzuziehen.</p>",

"LOX.S9_TITEL": "Schritt 9: Gegenprobe",
"LOX.S9_TEXT": "Diese drei Adressen im Browser aufrufen. Die erste muss Werte liefern, die beiden anderen m&uuml;ssen <b>abgewiesen</b> werden &mdash; wenn nicht, ist etwas an der Absicherung falsch.",
"LOX.T_PRUEFUNG": "Aufruf",
"LOX.T_ERWARTUNG": "Erwartete Antwort",
"LOX.T_BAUSTEIN": "Baustein (Typ)",
"LOX.T_NAMENSVORSCHLAG": "Name (Vorschlag)",
"LOX.T_PARAMETER": "Parameter",
"LOX.T_EINGAENGE": "Eingänge verbinden mit",
"LOX.K_TOKEN_NEU": "Neues Token würfeln",
"LOX.TOKEN_NEU": "Es wurde ein neues Token erzeugt. Alle bisher im Miniserver eingetragenen Adressen sind damit ungültig und müssen nachgetragen werden.",

# ---- Bausteine -------------------------------------------------------------
"BAUSTEIN.T_VE": "Virtueller Eingang",
"BAUSTEIN.T_ODER": "ODER",
"BAUSTEIN.T_UND": "UND",
"BAUSTEIN.T_EVZ": "Einschaltverzögerung",
"BAUSTEIN.T_BENACHR": "Benachrichtigung",
"BAUSTEIN.T_SWS": "Schwellwertschalter",
"BAUSTEIN.T_STATUS": "Status",
"BAUSTEIN.T_WOCHE": "Wochenuhr",
"BAUSTEIN.T_TASTER": "Taster",
"BAUSTEIN.T_IMPULS": "Impulsgeber",
"BAUSTEIN.T_VA": "Virtueller Ausgang Befehl",
"BAUSTEIN.MANUELL": "von Hand oder aus einer Szene",

"BAUSTEIN.N01": "WW 1 Zustand",
"BAUSTEIN.P01": "0 aus, 1 bereit, 2 läuft, 3 pausiert, 4 fertig, 5 Störung",
"BAUSTEIN.N02": "WW 1 Läuft",
"BAUSTEIN.P02": "1 = Programm läuft",
"BAUSTEIN.N03": "WW 1 Restzeit",
"BAUSTEIN.P03": "Einheit min, Restzeit",
"BAUSTEIN.N04": "WW 1 Fortschritt",
"BAUSTEIN.P04": "Einheit %, Fortschritt",
"BAUSTEIN.N05": "WW 1 Fertig",
"BAUSTEIN.P05": "1 = Programm beendet",
"BAUSTEIN.N06": "WW 1 Fernstart",
"BAUSTEIN.P06": "1 = Fernstart am Gerät freigegeben",
"BAUSTEIN.N07": "WW 1 Tür",
"BAUSTEIN.P07": "1 = Tür offen",
"BAUSTEIN.N08": "WW 1 Verbunden",
"BAUSTEIN.P08": "1 = Gerät erreichbar",
"BAUSTEIN.N09": "WW 1 Netz",
"BAUSTEIN.P09": "1 = Gerät eingeschaltet",
"BAUSTEIN.N10": "WW 1 Energie",
"BAUSTEIN.P10": "Einheit kWh, aus dem Verbrauchs-Eingang",
"BAUSTEIN.N11": "WW 1 Alter",
"BAUSTEIN.P11": "Einheit s, Alter des Abbilds",
"BAUSTEIN.N12": "WW 1 Startvorwahl",
"BAUSTEIN.P12": "Einheit min, Startvorwahl",
"BAUSTEIN.N13": "PV-Überschuss ausreichend",
"BAUSTEIN.P13": "Ein > 2000, Aus < 1500 (Watt Überschuss)",
"BAUSTEIN.N14": "Ladezustand hoch genug",
"BAUSTEIN.P14": "Ein > 60, Aus < 40 (Hausakku in %, freiwillig)",
"BAUSTEIN.N15": "Strompreis niedrig",
"BAUSTEIN.P15": "Ein < 15, Aus > 20 (ct/kWh, freiwillig)",
"BAUSTEIN.N16": "Günstig waschen",
"BAUSTEIN.N17": "Waschen jetzt sinnvoll",
"BAUSTEIN.N18": "Überschuss muss anhalten",
"BAUSTEIN.P18": "Einschaltverzögerung 600 s",
"BAUSTEIN.N19": "Frühester Startzeitpunkt",
"BAUSTEIN.P19": "Wochenuhr, z. B. ab 9 Uhr — nicht nachts waschen",
"BAUSTEIN.N20": "Weißware Programm starten",
"BAUSTEIN.P20": "zwei Eingänge — für eine dritte Bedingung einen zweiten UND-Baustein dahinterhängen",
"BAUSTEIN.N21": "Jetzt starten",
"BAUSTEIN.P21": "Taster als Impuls",
"BAUSTEIN.N22": "Startbefehl anfordern",
"BAUSTEIN.N23": "Nur wenn Fernstart frei",
"BAUSTEIN.P23": "verhindert Befehle, die der Anbieter ohnehin abweist",
"BAUSTEIN.N24": "Einmal auslösen",
"BAUSTEIN.P24": "Impulsgeber, damit der Befehl nicht im Takt wiederholt wird",
"BAUSTEIN.N25": "Weißware Start",
"BAUSTEIN.P25": "Befehl bei EIN, Adresse aus Schritt 5",
"BAUSTEIN.N26": "Weißware Abbrechen",
"BAUSTEIN.P26": "optional, Befehl bei EIN",
"BAUSTEIN.N27": "Programm ist fertig",
"BAUSTEIN.P27": "Ein > 0,5, Aus < 0,5",
"BAUSTEIN.N28": "Meldung: Geschirrspüler ist fertig",
"BAUSTEIN.P28": "Betreff frei wählbar",
"BAUSTEIN.N29": "Tür steht offen",
"BAUSTEIN.P29": "Ein > 0,5, Aus < 0,5",
"BAUSTEIN.N30": "Meldung: Tür offen",
"BAUSTEIN.P30": "Betreff frei wählbar",
"BAUSTEIN.N31": "Abruf ausgefallen",
"BAUSTEIN.P31": "Ein > 1200, Aus < 900 (bei 300 s Ruhetakt)",
"BAUSTEIN.N32": "Meldung: Kein Kontakt zum Anbieter",
"BAUSTEIN.P32": "Betreff frei wählbar",
"BAUSTEIN.N33": "Geräteübersicht",
"BAUSTEIN.P33": "Statusbaustein für die App-Kachel",
"BAUSTEIN.N34": "Meldung: Waschmaschine gestartet",
"BAUSTEIN.P34": "Betreff frei wählbar",
"TEST.H_SELBSTPRUEFUNG": "Selbstprüfung",
"TEST.EINLEITUNG": "Diese Pr&uuml;fung beantwortet <b>ohne Loxone</b>, ob die Einrichtung tr&auml;gt. Jede Zeile ist eine Frage; ein Kreuz bedeutet, dass hier etwas fehlt. Was sich nur mit Fahrzeug pr&uuml;fen lie&szlig;e, steht unten ausdr&uuml;cklich als ungepr&uuml;ft.",
"TEST.T_FRAGE": "Frage",
"TEST.T_BEFUND": "Befund",
"TEST.F_VENV": "Ist die virtuelle Python-Umgebung vorhanden?",
"TEST.A_VENV_FEHLT": "nein — Plugin neu installieren",
"TEST.F_PYTHON": "Ist das Python neu genug (3.9 oder neuer)?",
"TEST.A_PYTHON_ZU_ALT": "zu alt für carconnectivity",
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
"TEST.F_MQTT": "Zustand des MQTT-Gateways",
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
"ANSAGE.EIN_GERAET": "Ein Haushaltsgerät",
"ANSAGE.T_FERTIG": "Hallo! %s ist fertig.",
"ANSAGE.T_STOERUNG": "Achtung! %s meldet eine Störung.",
"ANSAGE.T_FERNSTART": "Hinweis: bei %s ist die Fernstart-Freigabe erloschen.",
"ANSAGE.L_STOERUNG": "Auch bei einer Störung sprechen",
"ANSAGE.L_FERNSTART": "Auch sprechen, wenn die Fernstart-Freigabe erlischt",
"ANSAGE.H_FERNSTART": "Die Freigabe wird am Gerät gegeben und erlischt meist mit dem Programmende. Danach weist das Plugin jeden Startbefehl ab &mdash; ohne diese Ansage merkt man es erst, wenn die Sonne umsonst geschienen hat.",
"ANSAGE.L_RUHE_VON": "Ruhezeit von",
"ANSAGE.L_RUHE_BIS": "Ruhezeit bis",
"ANSAGE.H_RUHE": "In diesem Fenster wird nicht gesprochen. Der Stand wird trotzdem fortgeschrieben, damit um sieben Uhr nicht die halbe Nacht nachgeholt wird. Gleiche Zeiten heißen: keine Ruhezeit.",
"ANSAGE.FEHLER_ZEIT": "%s: bitte eine Uhrzeit in der Form 22:00 eintragen.",
"LAUF.H": "Beendete Programmläufe",
"LAUF.ERKLAERUNG": "Festgehalten im Augenblick, in dem ein Gerät auf <i>fertig</i> wechselt &mdash; danach sind Energie und Wasser beim Anbieter fort. Ein Strich heißt: dieser Wert lag nicht vor. Home Connect liefert weder Energie noch Wasser, SmartThings kein Wasser.",
"LAUF.LEER": "Noch kein Lauf beendet worden, seit das Plugin mitschreibt.",
"LAUF.T_ENDE": "Ende",
"LAUF.T_PROGRAMM": "Programm",
"LAUF.T_DAUER": "Dauer (min)",
"LAUF.T_ENERGIE": "Energie (kWh)",
"LAUF.T_WASSER": "Wasser (l)",
"TEST.F_ENDPUNKT": "Antwortet der eigene Endpunkt ueber HTTP?",
"TEST.A_EP_UNMESSBAR": "nicht feststellbar: weder curl noch allow_url_fopen stehen zur Verfuegung",
"TEST.A_EP_KEINE_ANTWORT": "nicht feststellbar: keine Antwort (HTTP %d). Ein Webserver, der nur eine Anfrage zugleich bearbeitet, kann sich waehrend des Seitenaufbaus nicht selbst aufrufen.",
"TEST.A_EP_FALSCH": "HTTP %d, und die Antwort beginnt nicht mit der erwarteten Kennung: %s",
"TEST.A_EP_ALTER": "vor %d s gemessen",
"TEST.F_VORGABEN": "Fuehren Oberflaeche und Dienst dieselben Vorgabewerte?",
"TEST.A_VORGABEN_UNLESBAR": "bin/weissware.py ist nicht lesbar - nicht feststellbar",
"TEST.A_VORGABEN_FEHLEN": "der Oberflaeche fehlen: %s",
"TEST.A_VORGABEN_OK": "alle %d Schluessel des Dienstes sind auch der Oberflaeche bekannt",
"TEST.F_THEMEN": "Stimmt die Themenliste mit dem Sendecode ueberein?",
"TEST.A_THEMEN_UNLESBAR": "bin/weissware.py ist nicht lesbar - nicht feststellbar",
"TEST.A_THEMEN_AB": "Abweichung: %s",
"TEST.A_THEMEN_OK": "%d Themen je Geraet, Liste und Sendecode deckungsgleich",
"TEST.F_MITSCHNITT": "Laeuft ein Mitschnitt?",
"TEST.A_MITSCHNITT_LAEUFT": "ja, noch %d Sekunden. Er endet von selbst.",
"TEST.K_TROCKEN": "Trockenlauf: was wuerde geschehen?",
"TEST.H_TROCKEN": "Zeigt fuer <i>Start</i>, welche Sperre greift und welche Anfrage an den Anbieter hinausginge &mdash; und <b>sendet nichts</b>. Er braucht keinen laufenden Dienst; gerade dann will man es wissen.",
"TEST.K_MITSCHNITT_EIN": "Mitschnitt 5 Minuten einschalten",
"TEST.K_MITSCHNITT_AUS": "Mitschnitt jetzt beenden",
"TEST.H_MITSCHNITT": "Schreibt Anfragen und Antworten der Anbieter mit &mdash; das einzige Mittel, wenn ein Wert leer bleibt und niemand weiss, ob der Anbieter nichts liefert oder die Zuordnung den Schluessel verfehlt. Ab Werk aus, endet von selbst, die Datei ist auf 500 kB begrenzt. Zugangsdaten und Token werden vor dem Schreiben entfernt.",
"TEST.M_MITSCHNITT_EIN": "Der Mitschnitt laeuft %d Sekunden und endet dann von selbst.",
"TEST.M_MITSCHNITT_AUS": "Der Mitschnitt ist beendet.",
"TEST.K_ROH": "Rohdaten als JSON ansehen",
"TEST.H_SCHALTEN": "Schalten",
"TEST.SCHALTEN_WARNUNG": "<b>Diese Kn&ouml;pfe wirken sofort und am echten Ger&auml;t.</b> Ein gestartetes Waschprogramm l&auml;uft durch, auch wenn niemand W&auml;sche eingef&uuml;llt hat. Ohne Fernstart-Freigabe am Ger&auml;t weist der Anbieter den Start ab &mdash; das ist keine St&ouml;rung, sondern die Sicherung, die daf&uuml;r gedacht ist.",
"TEST.SCHALTEN_GESPERRT": "Schreibende Befehle sind zurzeit gesperrt. Die Kn&ouml;pfe geben deshalb eine Ablehnung zur&uuml;ck &mdash; das ist kein Fehler. Freigeben im Reiter Einstellungen.",
"TEST.K_ABRUF": "Sofort abrufen",
"TEST.M_UNBEKANNT": "Unbekannte Testaktion.",
"TEST.H_UNGEPRUEFT": "Was in dieser Fassung ungeprüft ist",
"TEST.UNGEPRUEFT": "Dieses Plugin wurde <b>ohne Entwicklerkonten und ohne Ger&auml;te</b> gebaut. Ungepr&uuml;ft ist deshalb: ob die Anmeldung bei den drei Anbietern gelingt, ob die Feldnamen der Antworten zu der Zuordnung hier passen und ob die schreibenden Befehle am Ger&auml;t die erwartete Wirkung haben. Endpunkte und Datenformen stammen aus den Entwicklerdokumentationen, nicht aus einer Messung. Gepr&uuml;ft ist alles &uuml;brige: Oberfl&auml;che, Endpunkt, Absicherung, Warteschlange, Sprachdateien und die Zuordnung selbst &mdash; letztere gegen nachgebaute Antworten in der dokumentierten Form. Deshalb tr&auml;gt diese Fassung die Nummer 0.9.0 und nicht 1.0.0. Wenn etwas leer bleibt, hilft der Knopf <i>Rohdaten als JSON ansehen</i>: dort steht, was der Dienst tats&auml;chlich bekommen hat.",

# ---- Logdateien ------------------------------------------------------------
"LOG.H_TITEL": "Logdateien",
"LOG.ERKLAERUNG": "Der Abrufdienst schreibt ausschlie&szlig;lich in diese eine Datei. Unten stehen die letzten 400 Zeilen, die neueste zuerst.",
"LOG.LEER": "Die Logdatei ist leer oder noch nicht angelegt.",
"LOG.K_LEEREN": "Logdatei leeren",
"LOG.GELEERT": "Logdatei geleert",

# ---- Feldbedeutungen (Status) ---------------------------------------------
"WW_FELD.ALTER": "Alter des Abbilds — für die Ausfallerkennung",
"WW_FELD.OK": "1 = der letzte Abruf war erfolgreich",

# ---- Feldbedeutungen (Laden) ----------------------------------------------
"WW_VFELD.OK": "1 = der letzte Abruf war erfolgreich",

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
"EINST.ANBIETER_ERKLAERUNG": "Drei &Ouml;kosysteme, ein gemeinsames Modell. Eingeschaltet wird nur, was Sie wirklich haben &mdash; jeder eingeschaltete Anbieter kostet Anfragen, auch wenn kein Ger&auml;t da ist. Bei Home Connect und Miele brauchen Sie ein <b>kostenloses Entwicklerkonto</b>, weil beide nur registrierten Anwendungen antworten; SmartThings kommt mit einem Token aus.",
"EINST.ANGEMELDET": "angemeldet",
"EINST.ANMELDUNG_ERKLAERUNG": "Erst speichern, dann anmelden. Die Anmeldung legt einen Erneuerungsschl&uuml;ssel ab, mit dem sich der Dienst von selbst weiter anmeldet &mdash; Sie m&uuml;ssen das also nur einmal tun. Ausnahme ist SmartThings, siehe oben.",
"EINST.FEHLER_MIELE_CODE": "Der eingegebene Wert sieht nicht wie ein Anmeldecode aus. Er wurde nicht eingelöst.",
"EINST.FEHLER_SPRACHE": "Die Sprache muss die Form de-DE haben.",
"EINST.FEHLER_TAKT_TAUSCH": "Der Takt in Ruhe ist kleiner als der im Betrieb. Das ist verkehrt herum — bitte die beiden Werte tauschen.",
"EINST.GESETZT": "gespeichert (%d Zeichen) – leer lassen, um es zu behalten",
"EINST.HC_ADRESSE": "Adresse",
"EINST.HC_BEGONNEN": "Die Anmeldung wurde begonnen. Code und Adresse stehen unten — Sie haben fünf Minuten.",
"EINST.HC_CODE": "Code",
"EINST.HC_FERTIG": "Home Connect ist angemeldet.",
"EINST.HC_GUELTIG": "gültig noch",
"EINST.HC_NOCH_NICHT": "Noch nicht bestätigt. Code im Browser eingeben, Zugriff erlauben und dann erneut auf „Anmeldung abschließen“ drücken.",
"EINST.HC_SCHRITT1": "Auf <i>Anmeldung beginnen</i> dr&uuml;cken. Danach erscheinen hier ein Code und eine Adresse; die Adresse in einem beliebigen Browser &ouml;ffnen, den Code eingeben und den Zugriff erlauben. Zum Schluss auf <i>Anmeldung abschlie&szlig;en</i> dr&uuml;cken.",
"EINST.HC_SCHRITT2": "Die Anmeldung l&auml;uft. &Ouml;ffnen Sie die Adresse in einem Browser, geben Sie den Code ein, erlauben Sie den Zugriff &mdash; und dr&uuml;cken Sie dann hier auf <i>Anmeldung abschlie&szlig;en</i>.",
"EINST.H_ANBIETER": "Anbieter",
"EINST.H_ANMELDUNG": "Anmeldung",
"EINST.H_HC_ID": "Aus dem Entwicklerportal von Home Connect, Abschnitt <i>Applications</i>. Legen Sie dort eine Anwendung mit dem Anmeldeverfahren <b>Device Flow</b> an &mdash; das ist das einzige, das ohne Bildschirm am Ger&auml;t auskommt.",
"EINST.H_HC_SECRET": "Nur f&uuml;r das Erneuern des Zugriffstokens n&ouml;tig. Bleibt das Feld leer, bleibt das gespeicherte Geheimnis unver&auml;ndert.",
"EINST.H_HC_SIMULATOR": "Home Connect stellt simulierte Ger&auml;te bereit. Damit l&auml;sst sich alles einrichten und in Loxone nachbauen, bevor eine echte Maschine angeschlossen ist. <b>Achtung:</b> Simulator und echte Ger&auml;te brauchen verschiedene Client-IDs.",
"EINST.H_MIELE_CODE": "Die ganze Adresse geht auch &mdash; der Code wird daraus herausgesucht. Der Code ist nur wenige Minuten g&uuml;ltig und l&auml;sst sich genau einmal einl&ouml;sen.",
"EINST.H_MIELE_ID": "Aus dem Miele-Entwicklerportal, Abschnitt <i>Get involved</i>. Als Weiterleitungsadresse tragen Sie dort <span class='sm-mono'>http://localhost</span> ein &mdash; die Adresse muss nicht erreichbar sein, der Code wird von Hand zur&uuml;ckkopiert.",
"EINST.H_SPRACHE": "In dieser Sprache liefern die Anbieter die Programmnamen und Zustandstexte. Auf die Sprache dieser Oberfl&auml;che hat das keinen Einfluss.",
"EINST.H_ST_TOKEN": "Aus dem SmartThings-Entwicklerportal. Bleibt das Feld leer, bleibt das gespeicherte Token unver&auml;ndert.",
"EINST.H_TAKT_BETRIEB": "Abstand, sobald mindestens ein Ger&auml;t arbeitet. Untergrenze 60 Sekunden: Home Connect nennt h&auml;ufiges Abfragen in seinen Best Practices ausdr&uuml;cklich als h&auml;ufigste Ursache f&uuml;r HTTP 429.",
"EINST.H_TAKT_RUHE": "Abstand, solange kein Ger&auml;t l&auml;uft. F&uuml;nf Minuten sind reichlich &mdash; eine Waschmaschine, die aus ist, wird nicht in einer Minute fertig.",
"EINST.KEINE_GERAETE": "Noch kein Ger&auml;t erkannt. Bis zum ersten erfolgreichen Abruf ist das normal: Anbieter einschalten, Zugangsdaten eintragen, speichern, anmelden, Dienst starten und eine Taktl&auml;nge abwarten. Bleibt die Liste danach leer, steht der Grund im Reiter <i>Test</i> und in der Logdatei.",
"EINST.KENNUNG_HINWEIS": "In allen Adressen kann statt der Nummer auch die Kennung stehen &mdash; <span class='sm-mono'>geraet=SIEMENS-HCS03WCH1-…</span>. Die Nummer bleibt einem Ger&auml;t seit 0.9.7 dauerhaft zugeordnet &mdash; auch wenn ein Anbieter ausf&auml;llt oder ein Ger&auml;t dazukommt; sie steht in <span class='sm-mono'>data/plugins/weissware/geraetenummern.json</span>. Die Kennung ist trotzdem die deutlichere Adresse, weil man ihr ansieht, welches Ger&auml;t gemeint ist.",
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
"EINST.MIELE_SCHRITTE": "Miele bietet <b>kein</b> Verfahren f&uuml;r Ger&auml;te ohne Bildschirm an. Deshalb von Hand: die Adresse unten in einen Browser kopieren, mit dem Miele-Konto anmelden, die Ger&auml;te ausw&auml;hlen, die freigegeben werden sollen. Danach landen Sie auf einer Seite, die nicht l&auml;dt &mdash; das ist richtig so. Aus deren <b>Adresszeile</b> den Teil hinter <span class='sm-mono'>code=</span> kopieren (oder die ganze Adresse) und hier einf&uuml;gen.",
"EINST.ST_SCHRITTE": "SmartThings braucht keine Anmeldung &mdash; das Token oben gen&uuml;gt. Es l&auml;uft allerdings nach 24 Stunden ab; dann tragen Sie hier ein neues ein und speichern.",
"EINST.ST_WARNUNG": "<b>Vorbehalt.</b> Samsung hat die Lebensdauer neu ausgestellter Personal Access Tokens am 30.12.2024 auf <b>24 Stunden</b> verk&uuml;rzt und die Ratengrenzen gesenkt. F&uuml;r Dauerbetrieb verlangt Samsung eine registrierte Anwendung mit einem von au&szlig;en erreichbaren Webhook &mdash; das kann ein LoxBerry hinter einem Router nicht ohne Weiteres. Praktisch hei&szlig;t das: <b>Sie m&uuml;ssen das Token t&auml;glich erneuern.</b> Wer damit nicht leben will, l&auml;sst SmartThings aus. Wer ein &auml;lteres Token von vor dem 30.12.2024 hat, ist nicht betroffen.",
"EINST.TAKT_ERKLAERUNG": "<b>Der eigentliche Grund f&uuml;r dieses Plugin.</b> Ein starrer Abfragezyklus ist entweder zu langsam f&uuml;r eine brauchbare Restzeit oder zu schnell f&uuml;r die Ratengrenzen des Anbieters. Hier gibt es zwei Takte: einen weiten, solange nichts l&auml;uft, und einen engen, sobald mindestens ein Ger&auml;t arbeitet. Umgeschaltet wird von selbst.",
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
"LOX.S4_LEER": "<b>Nicht jeder Anbieter liefert jeden Wert.</b> Home Connect meldet weder Energie- noch Wasserverbrauch; SmartThings meldet keinen Fortschritt in Prozent; Miele liefert beides, aber nur bei Ger&auml;ten mit EcoFeedback. Was fehlt, ist ein Strich &mdash; keine 0.",
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
"WW_FELD.FERTIGUM": "Voraussichtlicher Fertigzeitpunkt als Unixzeit. Loxone rechnet in Sekunden seit dem 01.01.2009, dort also den Wert minus 1230768000. Ein Strich heisst: keine Restzeit bekannt.",
"WW_MQTT.TS": "Zeitpunkt des letzten <b>erfolgreichen</b> Abrufs als Unixzeit. Ueber MQTT gibt es kein Alter - beim Senden ist es immer null; der Miniserver rechnet es aus: (Loxone-Zeit + 1230768000) - ts.",
"WW_MQTT.FEHLER_FOLGE": "Fehlgeschlagene Abrufe in Folge. 0 heisst: der letzte sass. Trennt einen kurzen Aussetzer von einer Dauerstoerung.",
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
"BAUSTEIN.HAUSAKKU": "Ladezustand des Hausakkus",
"BAUSTEIN.PVUEBERSCHUSS": "PV-Überschuss in Watt",
"BAUSTEIN.SPOTPREIS": "Strompreis aus dem Spotpreis-Plugin",
"ANSAGE.H": "Sprachausgabe (Ansage, wenn ein Gerät fertig ist)",
"ANSAGE.H_AUDIOSERVER": "Der originale Loxone Audioserver bietet <b>keine HTTP-TTS-Schnittstelle</b>. In diesem Modus spricht das Plugin nicht selbst; die Ansage erfolgt in Loxone Config über einen Textgenerator am TTS-Eingang des Audioplayer-Bausteins (MQTT-Wert <span class='sm-mono'>geraetN/fertig</span> als Auslöser).",
"ANSAGE.H_EIN": "Gesprochen wird beim Wechsel eines Geräts auf <i>fertig</i> – einmal je Programmlauf, nie beim Neustart des LoxBerry. Vorgabe: aus.",
"ANSAGE.H_TEST": "Ansage",
"ANSAGE.H_TEST_TEXT": "Spricht sofort in die konfigurierten Zonen – unabhängig davon, ob die Ansage eingeschaltet ist.",
"ANSAGE.H_VORLAGE": "Platzhalter: <span class='sm-mono'>{ip} {port} {zones} {vol} {lang} {text}</span>. Leer = Standard-Vorlage MusicServer4Home.",
"ANSAGE.H_ZONEN": "Zonennummern mit Komma (z.&nbsp;B. <span class='sm-mono'>2,4,6</span>) — die Lautstärke kommt aus dem Feld daneben. Optional je Zone eigene Lautstärke: <span class='sm-mono'>Zone~Lautstärke</span> (z.&nbsp;B. <span class='sm-mono'>2~25,4~40</span>). Leerzeichen nach dem Komma sind erlaubt — <span class='sm-mono'>2,4,6</span> und <span class='sm-mono'>2, 4, 6</span> funktionieren beide.",
"ANSAGE.K_TEST": "Testansage jetzt sprechen",
"ANSAGE.L_AUSGABE": "Audio-Ausgabe",
"ANSAGE.L_EIN": "Ansage einschalten",
"ANSAGE.L_IP": "IP des Audio-Servers",
"ANSAGE.L_LAUTSTAERKE": "Lautstärke",
"ANSAGE.L_PORT": "Port",
"ANSAGE.L_SPRACHE": "Sprache",
"ANSAGE.L_VORLAGE": "URL-Vorlage für Audioserver4Home/MS4H oder eigene Systeme",
"ANSAGE.L_ZONEN": "Zonen",
"ANSAGE.O_AUDIOSERVER": "Original Loxone Audioserver (via Loxone Config)",
"ANSAGE.O_CUSTOM": "Eigene URL-Vorlage",
"ANSAGE.O_MS4H": "Audioserver4Home / MusicServer4Home",
"ANSAGE.O_MUSICSERVER": "Loxone Music Server (klassisch)",
"ANSAGE.TESTTEXT": "Hallo! Dies ist eine Testansage des Weissware-Plugins.",
"ANSAGE.TEST_FEHLER": "Testansage fehlgeschlagen – Einstellungen und ansage.log prüfen.",
"ANSAGE.TEST_OK": "Testansage abgesetzt – das Protokoll der Ansage-Strecke steht in ansage.log.",
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
"WW_NAME.ALTER": "Alter",
"WW_NAME.CMD_ABRUF": "Sofort abrufen (Befehl)",
"WW_NAME.CMD_NETZ": "Ein/Aus (Befehl)",
"WW_NAME.CMD_PAUSE": "Pause (Befehl)",
"WW_NAME.CMD_PROGRAMM": "Programm (Befehl)",
"WW_NAME.ENERGIE": "Energie",
"WW_NAME.FERNBED": "Fernbedienung",
"WW_NAME.FERNSTART": "Fernstart",
"WW_NAME.FERTIG": "Fertig",
"WW_NAME.FERTIGUM": "Fertig um",
"WW_NAME.FORTSCHR": "Fortschritt",
"WW_NAME.LAEUFT": "Läuft",
"WW_NAME.LAUFMIN": "Laufzeit",
"WW_NAME.NETZ": "Netz",
"WW_NAME.OK": "OK",
"WW_NAME.RESTMIN": "Restzeit",
"WW_NAME.SCHLEUDER": "Schleuderdrehzahl",
"WW_NAME.STARTMIN": "Startvorwahl",
"WW_NAME.TEMP": "Temperatur",
"WW_NAME.TUER": "Tür",
"WW_NAME.VERBUNDEN": "Verbunden",
"WW_NAME.VOK": "OK (Verbrauch)",
"WW_NAME.WASSER": "Wasser",
"WW_NAME.ZUSTAND": "Zustand",
}

# ---------------------------------------------------------------------------
# Englisch - Rueckfallebene, muss vollstaendig sein
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
"LEGENDE.AKTION_LOG": "Triggers something &mdash; the existing lines will be gone",

"ALLG.BEANSTANDUNG": "Nothing was saved. Please correct these points:",
"ALLG.DIENST": "Polling service",
"ALLG.LAEUFT": "running",
"ALLG.GESTOPPT": "stopped",
"ALLG.KEINE_PID": "no process id",
"ALLG.LETZTER_ABRUF": "Last poll",
"ALLG.NIE": "never",
"ALLG.GATEWAY": "LoxBerry gateway",
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

"EINST.H_DIENST": "Polling service",
"EINST.DIENST_ERKLAERUNG": "The service fetches values from the enabled providers at the configured interval and stores them. The user interface and the Miniserver only read what has been stored &mdash; they never talk to the provider themselves.",
"EINST.K_START": "Start service",
"EINST.K_NEUSTART": "Restart service",
"EINST.K_STOPP": "Stop service",
"EINST.K_SITZUNG": "Force a new login",
"EINST.DIENST_START": "Service started:",
"EINST.DIENST_STOP": "Service stopped:",
"EINST.DIENST_RESTART": "Service restarted:",
"EINST.SITZUNG_VERWORFEN": "The authentication tokens were deleted. On the next poll the service will sign in again with username and password.",
"EINST.SITZUNG_KEINE": "No authentication tokens were stored.",
"EINST.PYTHON_ZU_ALT": "<b>The service cannot run.</b> This plugin's Python virtual environment uses a Python older than 3.9, but the carconnectivity library requires 3.9 or newer. This should not happen on any current LoxBerry (Debian 12 ships 3.11) &mdash; if it does, the virtual environment is broken. Remedy: reinstall the plugin.",


"EINST.H_TAKT": "Polling interval",

"EINST.H_STEUERUNG": "Write commands",
"EINST.STEUERUNG_ERKLAERUNG": "<b>Disabled by default.</b> Write commands start and stop real machines in an empty house. A wash programme started by accident runs without anyone having loaded laundry; an aborted one leaves it wet in the drum. Only enable this once the read values in the Test tab look right. <b>Two safeguards remain anyway:</b> the appliance must have the remote start release &mdash; given on the appliance itself, and usually cleared after the programme &mdash; and a programme must be selected there.",
"EINST.L_STEUERUNG_EIN": "Allow write commands",
"EINST.L_WARTEZEIT": "Wait for the answer (seconds)",
"EINST.H_WARTEZEIT": "How long the interface waits for the service to answer a command. After that it reports <span class='sm-mono'>OK=2</span> &mdash; queued, outcome unknown. No success is reported that nobody has verified.",

"EINST.L_MQTT_EIN": "Publish values via MQTT",
"EINST.L_MQTT_TOPIC": "Topic prefix",
"EINST.H_MQTT_TOPIC": "Letters, digits, hyphen, underscore and slash are allowed. All topics derive from this prefix, see the MQTT tab.",

"EINST.GESPEICHERT": "The settings were saved.",
"EINST.FEHLER_ZAHL": "%s: please enter a whole number.",
"EINST.FEHLER_BEREICH": "%s: the value must be between %d and %d.",
"EINST.FEHLER_TOPIC": "The topic prefix contains characters that are not allowed. Use letters, digits, hyphen, underscore and slash.",
"EINST.FEHLER_ZUGANG_SPEICHERN": "The credentials file could not be written. Check the permissions of the configuration folder.",
"EINST.FEHLER_SPEICHERN": "The configuration could not be written: %s",

"EINST.H_ERKANNT": "Detected appliances",
"EINST.T_NR": "No.",

"MQTT.H_ZUSTAND": "State of the MQTT gateway",
"MQTT.GATEWAY_ERKLAERUNG": "Since LoxBerry 3 the MQTT gateway is <b>part of the system</b>, not a plugin. It is not installed separately but switched on under <i>System &rarr; MQTT Gateway</i>.",
"MQTT.NICHT_GEFUNDEN": "No MQTT section was found in the LoxBerry <span class='sm-mono'>general.json</span>. Nothing can be sent without it.",
"MQTT.AUTOSTART_AUS": "The gateway is <b>not</b> set to autostart. The broker entry alone is not enough &mdash; it is set out of the box and says nothing about whether messages can arrive. What matters is autostart under <i>System &rarr; MQTT Gateway</i>.",
"MQTT.AUTOSTART_EIN": "The gateway is set to autostart, so messages from this plugin can arrive.",
"MQTT.T_AUTOSTART": "Gateway autostart",
"MQTT.T_BROKER": "Broker",
"MQTT.T_UDP": "UDP input port",
"MQTT.T_PLUGIN": "Publishing by this plugin",
"MQTT.H_ABO": "The subscription to enter",
"MQTT.ABO_WARNUNG": "<b>Without this entry nothing arrives at the Miniserver.</b> This is by far the most common cause of failure.",
"MQTT.ABO_SCHRITTE": "<i>System &rarr; MQTT Gateway</i> &rarr; section <i>Subscriptions</i> &rarr; add the following line and save:",
"MQTT.H_THEMEN": "All published topics",
"MQTT.THEMEN_ERKLAERUNG": "A topic whose value this appliance does not supply is not sent at all &mdash; so no topic is created carrying an invented zero.",
"MQTT.T_THEMA": "Topic",
"MQTT.T_BEDEUTUNG": "Meaning",
"MQTT.PLATZHALTER": "<b>N</b> is the appliance number, so 1 for the first one.",

"LOX.H_TITEL": "Loxone integration",
"LOX.EINLEITUNG": "Nine steps. Work through them from top to bottom and you end up with a working integration &mdash; including the complete block list in step 8.",
"LOX.S1_TITEL": "Step 1: choose the path",
"LOX.S1_TEXT": "There are two paths, and <b>MQTT is the standard one</b>. The gateway creates the names of the virtual inputs itself; in Loxone a matching virtual input is all you need. The HTTP path requires a command recognition per value, but everything arrives in <b>one</b> request and you can see in the browser what comes back. Start with MQTT; if you only need a few values, HTTP gets you there faster. Both at once works too.",
"LOX.S2_TITEL": "Step 2: add the subscription in the MQTT gateway",
"LOX.S2_TEXT": "Only needed for the MQTT path. Under <i>System &rarr; MQTT Gateway</i>, section <i>Subscriptions</i>, add:",
"LOX.S2_WARNUNG": "<b>Without this entry nothing arrives at the Miniserver.</b> This is by far the most common cause of failure &mdash; the plugin sends, but nobody listens.",
"LOX.S3_TITEL": "Step 3: create a virtual HTTP input for the main values",
"LOX.S3_TEXT": "In Loxone Config: <i>Virtual input &rarr; Virtual HTTP input</i>. Address and polling cycle:",
"LOX.S3_BEFEHLE": "Below it one <i>command recognition</i> per value. The template below creates them all at once &mdash; less tedious and less error-prone than typing them.",
"LOX.S3_STRICH": "<b>A dash instead of a number means: this value is not available.</b> No zero is sent on purpose &mdash; a zero would be a silent false statement. Loxone keeps the last valid value in that case. That is exactly why the failure detection in step 7 is needed.",
"LOX.FEHLER_VORLAGE": "There is no such template. Nothing was generated.",
"LOX.VORLAGEN_FUER": "Templates for appliance %s",
"LOX.VORLAGEN_MQTT": "Template for the MQTT path",
"LOX.VORLAGEN_HINWEIS": "This is how to import them in Loxone Config: pick <b>Virtual inputs</b> in the tree on the left, then in the ribbon <b>Predefined HTTP devices &rarr; Import template&hellip;</b>. The command file (VQ_&hellip;) takes the same route under <b>Virtual outputs &rarr; Predefined devices &rarr; Import template&hellip;</b> &mdash; there the button has no HTTP in its name. Loxone <b>creates new blocks</b> and overwrites nothing &mdash; importing twice gives you duplicates. Only fields the appliance actually delivered on the last poll are created; whatever is missing for that reason is noted inside the file.",
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
"LOX.S5_TEXT": "Only needed if Loxone should trigger something. In Loxone Config create a <i>virtual output</i> with the address below and one <i>virtual output command</i> per command. In the command text <span class='sm-mono'>&lt;v&gt;</span> stands for the value passed.",
"LOX.T_VA_ADRESSE": "Address of the virtual output",
"LOX.T_VA_ABRUF": "Trigger an immediate poll",
"LOX.S5_WARNUNG": "Two things to know beforehand. <b>First:</b> write commands are disabled by default and must be enabled in the Settings tab. <b>Second:</b> an answer of <span class='sm-mono'>OK=1</span> means the provider accepted the request. Whether the appliance actually starts only shows on the next poll &mdash; if you need certainty, evaluate <span class='sm-mono'>LAEUFT</span>, not the answer to the command.",

"LOX.S6_TITEL": "Step 6: the token",
"LOX.T_TOKEN": "Token of this plugin",
"LOX.S6_TEXT": "The endpoint sits in the unauthenticated area so Loxone can reach it without credentials. It is protected by this token. The token is part of every address you enter in the Miniserver &mdash; <b>a new token invalidates all of them at once</b> and has to be updated everywhere. So only roll a new one if it has actually leaked.",

"LOX.S7_TITEL": "Step 7: failure detection",
"LOX.S7_TEXT": "If a provider goes silent, the virtual inputs keep their last value. Everything looks normal in the app although nothing has arrived for hours. That is why the value <span class='sm-mono'>ALTER</span> is carried along: it states the age of the snapshot in seconds. Set the threshold <b>well above the idle interval</b> &mdash; with 300 seconds, 1200 works well.",

"LOX.S8_TITEL": "Step 8: complete block list for rebuilding one to one",
"LOX.S8_TEXT": "One block per row. Loxone Config lists them all in the block search (key F5). Rows 1 to 12 are the virtual inputs from steps 3 and 4. What is rebuilt is the case most people are after: <b>wash when the sun is shining</b> &mdash; plus a message when the programme has finished.",
"LOX.S8_ERLAEUTERUNG": "<p><b>On #13 to #16 &mdash; the actual purpose:</b> threshold switch #13 compares the PV surplus with what the machine draws (washing machine about 2000 W, dishwasher about 2200 W while heating). The AND at #14 only allows the start if the remote start release is present and the appliance is not already running. The ten minute on-delay at #15 prevents a passing cloud from triggering a wash programme.</p><p><b>On #17 and #18:</b> both optional. With a house battery you do not want to wash while it is empty; with a dynamic tariff you may want to wash without sun when electricity is cheap. Both blocks come from other plugins &mdash; this one does not supply them.</p><p><b>On #21 and #22:</b> the notification block only fires on a change from off to on &mdash; exactly right for 'the dishwasher has finished'. Never wire several appliances straight to its input: one permanently active source swallows all the others. Combine them with an OR first.</p><p><b>On #25:</b> the threshold is four times the idle interval. Set it tighter and every single missed cycle raises an alarm.</p><p><b>On #30:</b> without the remote start release the provider rejects every start. Not sending the command at all saves an error message and a request. <b>Loxone time base:</b> seconds since 1 January 2009. If a time block supplies Unix time (values around 1.23 billion), subtract 1230768000.</p>",

"LOX.S9_TITEL": "Step 9: cross-check",
"LOX.S9_TEXT": "Open these three addresses in a browser. The first must return values, the other two must be <b>rejected</b> &mdash; if they are not, something is wrong with the protection.",
"LOX.T_PRUEFUNG": "Request",
"LOX.T_ERWARTUNG": "Expected answer",
"LOX.T_BAUSTEIN": "Block (type)",
"LOX.T_NAMENSVORSCHLAG": "Name (suggestion)",
"LOX.T_PARAMETER": "Parameters",
"LOX.T_EINGAENGE": "Connect inputs to",
"LOX.K_TOKEN_NEU": "Roll a new token",
"LOX.TOKEN_NEU": "A new token was created. All addresses entered in the Miniserver so far are invalid now and have to be updated.",

"BAUSTEIN.T_VE": "Virtual input",
"BAUSTEIN.T_ODER": "OR",
"BAUSTEIN.T_UND": "AND",
"BAUSTEIN.T_EVZ": "On-delay",
"BAUSTEIN.T_BENACHR": "Notification",
"BAUSTEIN.T_SWS": "Threshold switch",
"BAUSTEIN.T_STATUS": "Status",
"BAUSTEIN.T_WOCHE": "Weekly timer",
"BAUSTEIN.T_TASTER": "Push-button",
"BAUSTEIN.T_IMPULS": "Pulse generator",
"BAUSTEIN.T_VA": "Virtual output command",
"BAUSTEIN.MANUELL": "by hand or from a scene",

"BAUSTEIN.N01": "WW 1 State",
"BAUSTEIN.P01": "0 off, 1 ready, 2 running, 3 paused, 4 finished, 5 fault",
"BAUSTEIN.N02": "WW 1 Running",
"BAUSTEIN.P02": "1 = programme running",
"BAUSTEIN.N03": "WW 1 Time left",
"BAUSTEIN.P03": "unit min, time left",
"BAUSTEIN.N04": "WW 1 Progress",
"BAUSTEIN.P04": "unit %, progress",
"BAUSTEIN.N05": "WW 1 Finished",
"BAUSTEIN.P05": "1 = programme finished",
"BAUSTEIN.N06": "WW 1 Remote start",
"BAUSTEIN.P06": "1 = remote start released on the appliance",
"BAUSTEIN.N07": "WW 1 Door",
"BAUSTEIN.P07": "1 = door open",
"BAUSTEIN.N08": "WW 1 Connected",
"BAUSTEIN.P08": "1 = appliance reachable",
"BAUSTEIN.N09": "WW 1 Power",
"BAUSTEIN.P09": "1 = appliance switched on",
"BAUSTEIN.N10": "WW 1 Energy",
"BAUSTEIN.P10": "unit kWh, from the consumption input",
"BAUSTEIN.N11": "WW 1 Age",
"BAUSTEIN.P11": "unit s, age of the snapshot",
"BAUSTEIN.N12": "WW 1 Start delay",
"BAUSTEIN.P12": "unit min, delayed start",
"BAUSTEIN.N13": "PV surplus sufficient",
"BAUSTEIN.P13": "on > 2000, off < 1500 (watts of surplus)",
"BAUSTEIN.N14": "Battery high enough",
"BAUSTEIN.P14": "on > 60, off < 40 (house battery in %, optional)",
"BAUSTEIN.N15": "Electricity price low",
"BAUSTEIN.P15": "on < 15, off > 20 (ct/kWh, optional)",
"BAUSTEIN.N16": "Wash cheaply",
"BAUSTEIN.N17": "Washing sensible now",
"BAUSTEIN.N18": "Surplus must persist",
"BAUSTEIN.P18": "on-delay 600 s",
"BAUSTEIN.N19": "Earliest start time",
"BAUSTEIN.P19": "weekly timer, e.g. from 9 a.m. — do not wash at night",
"BAUSTEIN.N20": "Start appliance programme",
"BAUSTEIN.P20": "two inputs — for a third condition chain a second AND block behind it",
"BAUSTEIN.N21": "Start now",
"BAUSTEIN.P21": "push-button as a pulse",
"BAUSTEIN.N22": "Request start command",
"BAUSTEIN.N23": "Only if remote start is free",
"BAUSTEIN.P23": "prevents commands the provider would reject anyway",
"BAUSTEIN.N24": "Fire once",
"BAUSTEIN.P24": "pulse generator, so the command is not repeated every cycle",
"BAUSTEIN.N25": "Appliance start",
"BAUSTEIN.P25": "command on ON, address from step 5",
"BAUSTEIN.N26": "Appliance abort",
"BAUSTEIN.P26": "optional, command on ON",
"BAUSTEIN.N27": "Programme has finished",
"BAUSTEIN.P27": "on > 0.5, off < 0.5",
"BAUSTEIN.N28": "Message: dishwasher has finished",
"BAUSTEIN.P28": "subject freely chosen",
"BAUSTEIN.N29": "Door is open",
"BAUSTEIN.P29": "on > 0.5, off < 0.5",
"BAUSTEIN.N30": "Message: door open",
"BAUSTEIN.P30": "subject freely chosen",
"BAUSTEIN.N31": "Poll has failed",
"BAUSTEIN.P31": "on > 1200, off < 900 (at a 300 s idle interval)",
"BAUSTEIN.N32": "Message: no contact with the provider",
"BAUSTEIN.P32": "subject freely chosen",
"BAUSTEIN.N33": "Appliance overview",
"BAUSTEIN.P33": "status block for the app tile",
"BAUSTEIN.N34": "Message: washing machine started",
"BAUSTEIN.P34": "subject freely chosen",
"TEST.H_SELBSTPRUEFUNG": "Self-check",
"TEST.EINLEITUNG": "This check answers <b>without Loxone</b> whether the setup holds. Each row is a question; a cross means something is missing. What could only be checked with a car present is listed as unverified below.",
"TEST.T_FRAGE": "Question",
"TEST.T_BEFUND": "Finding",
"TEST.F_VENV": "Is the Python virtual environment present?",
"TEST.A_VENV_FEHLT": "no — reinstall the plugin",
"TEST.F_PYTHON": "Is Python new enough (3.9 or newer)?",
"TEST.A_PYTHON_ZU_ALT": "too old for carconnectivity",
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
"TEST.F_MQTT": "State of the MQTT gateway",
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
"ANSAGE.EIN_GERAET": "An appliance",
"ANSAGE.T_FERTIG": "Hello! %s has finished.",
"ANSAGE.T_STOERUNG": "Attention! %s reports a fault.",
"ANSAGE.T_FERNSTART": "Note: the remote start release for %s has expired.",
"ANSAGE.L_STOERUNG": "Also speak on a fault",
"ANSAGE.L_FERNSTART": "Also speak when the remote start release expires",
"ANSAGE.H_FERNSTART": "The release is given on the appliance and usually expires with the programme. After that the plugin rejects every start command &mdash; without this announcement you only notice once the sun has shone for nothing.",
"ANSAGE.L_RUHE_VON": "Quiet time from",
"ANSAGE.L_RUHE_BIS": "Quiet time until",
"ANSAGE.H_RUHE": "Nothing is spoken inside this window. The state is still tracked, so that half the night is not caught up at seven in the morning. Equal times mean: no quiet time.",
"ANSAGE.FEHLER_ZEIT": "%s: please enter a time of day in the form 22:00.",
"LAUF.H": "Completed programme runs",
"LAUF.ERKLAERUNG": "Recorded at the moment an appliance switches to <i>finished</i> &mdash; after that energy and water are gone at the provider. A dash means the value was not available. Home Connect delivers neither energy nor water, SmartThings no water.",
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
"TEST.F_MITSCHNITT": "Is a traffic capture running?",
"TEST.A_MITSCHNITT_LAEUFT": "yes, %d seconds left. It ends by itself.",
"TEST.K_TROCKEN": "Dry run: what would happen?",
"TEST.H_TROCKEN": "Shows for <i>Start</i> which lock applies and which request would go out to the provider &mdash; and <b>sends nothing</b>. It needs no running service; that is exactly when you want to know.",
"TEST.K_MITSCHNITT_EIN": "Start a 5 minute capture",
"TEST.K_MITSCHNITT_AUS": "Stop the capture now",
"TEST.H_MITSCHNITT": "Records the providers' requests and answers &mdash; the only means when a value stays empty and nobody knows whether the provider delivers nothing or the mapping misses the key. Off by default, ends by itself, the file is capped at 500 kB. Credentials and tokens are removed before writing.",
"TEST.M_MITSCHNITT_EIN": "The capture runs for %d seconds and then ends by itself.",
"TEST.M_MITSCHNITT_AUS": "The capture has ended.",
"TEST.K_ROH": "View raw data as JSON",
"TEST.H_SCHALTEN": "Switching",
"TEST.SCHALTEN_WARNUNG": "<b>These buttons act immediately and on the real appliance.</b> A wash programme that has been started runs through even if nobody has loaded laundry. Without the remote start release on the appliance the provider rejects the start &mdash; that is not a fault, it is the safeguard doing its job.",
"TEST.SCHALTEN_GESPERRT": "Write commands are currently disabled. The buttons will therefore return a rejection &mdash; that is not an error. Enable them in the Settings tab.",
"TEST.K_ABRUF": "Poll now",
"TEST.M_UNBEKANNT": "Unknown test action.",
"TEST.H_UNGEPRUEFT": "What is unverified in this version",
"TEST.UNGEPRUEFT": "This plugin was built <b>without developer accounts and without appliances</b>. Unverified is therefore: whether signing in with the three providers succeeds, whether the field names of the responses match the mapping here, and whether the write commands have the expected effect. Endpoints and data shapes come from the developer documentation, not from a measurement. Everything else has been verified: user interface, endpoint, protection, queue, language files and the mapping itself &mdash; the latter against rebuilt responses in the documented shape. That is why this version is numbered 0.9.0 and not 1.0.0. If something stays empty, the button <i>View raw data as JSON</i> helps: it shows what the service actually received.",

"LOG.H_TITEL": "Log files",
"LOG.ERKLAERUNG": "The polling service writes to this one file only. Below are the last 400 lines, newest first.",
"LOG.LEER": "The log file is empty or has not been created yet.",
"LOG.K_LEEREN": "Clear log file",
"LOG.GELEERT": "Log file cleared",

"WW_FELD.ALTER": "Age of the snapshot — for failure detection",
"WW_FELD.OK": "1 = the last poll succeeded",

"WW_VFELD.OK": "1 = the last poll succeeded",


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
"EINST.ANBIETER_ERKLAERUNG": "Three ecosystems, one common model. Only switch on what you actually own &mdash; every enabled provider costs requests even if it has no appliances. Home Connect and Miele need a <b>free developer account</b> because both only answer registered applications; SmartThings gets by with a token.",
"EINST.ANGEMELDET": "signed in",
"EINST.ANMELDUNG_ERKLAERUNG": "Save first, then sign in. Signing in stores a refresh key the service uses to keep itself signed in &mdash; so you only have to do this once. SmartThings is the exception, see above.",
"EINST.FEHLER_MIELE_CODE": "The value entered does not look like a sign-in code. It was not redeemed.",
"EINST.FEHLER_SPRACHE": "The language must have the form de-DE.",
"EINST.FEHLER_TAKT_TAUSCH": "The idle interval is smaller than the running one. That is the wrong way round — please swap the two values.",
"EINST.GESETZT": "stored (%d characters) – leave empty to keep it",
"EINST.HC_ADRESSE": "Address",
"EINST.HC_BEGONNEN": "Sign-in has begun. The code and address are below — you have five minutes.",
"EINST.HC_CODE": "Code",
"EINST.HC_FERTIG": "Home Connect is signed in.",
"EINST.HC_GUELTIG": "valid for another",
"EINST.HC_NOCH_NICHT": "Not confirmed yet. Enter the code in the browser, grant access and then press 'Complete sign-in' again.",
"EINST.HC_SCHRITT1": "Press <i>Begin sign-in</i>. A code and an address will appear here; open the address in any browser, enter the code and grant access. Finally press <i>Complete sign-in</i>.",
"EINST.HC_SCHRITT2": "Sign-in is in progress. Open the address in a browser, enter the code, grant access &mdash; then press <i>Complete sign-in</i> here.",
"EINST.H_ANBIETER": "Providers",
"EINST.H_ANMELDUNG": "Sign-in",
"EINST.H_HC_ID": "From the Home Connect developer portal, section <i>Applications</i>. Create an application using the <b>Device Flow</b> &mdash; the only method that works without a screen on the device.",
"EINST.H_HC_SECRET": "Only needed to refresh the access token. Leaving the field empty keeps the stored secret.",
"EINST.H_HC_SIMULATOR": "Home Connect provides simulated appliances. That lets you set everything up and rebuild it in Loxone before a real machine is connected. <b>Note:</b> the simulator and real appliances need different client IDs.",
"EINST.H_MIELE_CODE": "The whole address works too &mdash; the code is extracted from it. The code is valid for a few minutes and can be redeemed exactly once.",
"EINST.H_MIELE_ID": "From the Miele developer portal, section <i>Get involved</i>. Enter <span class='sm-mono'>http://localhost</span> as the redirect address &mdash; it does not have to be reachable, the code is copied back by hand.",
"EINST.H_SPRACHE": "The providers return programme names and state texts in this language. It has no effect on the language of this user interface.",
"EINST.H_ST_TOKEN": "From the SmartThings developer portal. Leaving the field empty keeps the stored token.",
"EINST.H_TAKT_BETRIEB": "Interval as soon as at least one appliance is working. Lower limit 60 seconds: Home Connect explicitly names frequent polling in its best practices as the most common cause of HTTP 429.",
"EINST.H_TAKT_RUHE": "Interval while no appliance is running. Five minutes is plenty &mdash; a washing machine that is off will not finish within a minute.",
"EINST.KEINE_GERAETE": "No appliance detected yet. That is normal until the first successful poll: enable a provider, enter the credentials, save, sign in, start the service and wait one interval. If the list is still empty afterwards, the reason is in the <i>Test</i> tab and in the log file.",
"EINST.KENNUNG_HINWEIS": "Every address also accepts the identifier instead of the number &mdash; <span class='sm-mono'>geraet=SIEMENS-HCS03WCH1-…</span>. Since 0.9.7 a number stays with its appliance for good — even if a provider fails or an appliance is added; it is kept in <span class='sm-mono'>data/plugins/weissware/geraetenummern.json</span>. The identifier is still the clearer address, because you can see from it which appliance is meant.",
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
"EINST.MIELE_SCHRITTE": "Miele offers <b>no</b> flow for devices without a screen. So by hand: copy the address below into a browser, sign in with your Miele account and pick the appliances to release. You will then land on a page that does not load &mdash; that is expected. Copy the part after <span class='sm-mono'>code=</span> from its <b>address bar</b> (or the whole address) and paste it here.",
"EINST.ST_SCHRITTE": "SmartThings needs no sign-in &mdash; the token above is enough. It does expire after 24 hours; enter a new one here and save.",
"EINST.ST_WARNUNG": "<b>Reservation.</b> On 30 December 2024 Samsung cut the lifetime of newly issued personal access tokens to <b>24 hours</b> and lowered the rate limits. For continuous operation Samsung requires a registered application with a publicly reachable webhook &mdash; which a LoxBerry behind a router cannot easily provide. In practice: <b>you have to renew the token every day.</b> If you do not want to live with that, leave SmartThings switched off. Tokens issued before 30 December 2024 are not affected.",
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
"LOX.S4_LEER": "<b>Not every provider supplies every value.</b> Home Connect reports neither energy nor water consumption; SmartThings reports no progress in percent; Miele supplies both, but only for appliances with EcoFeedback. What is missing is a dash &mdash; not a zero.",
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
"BAUSTEIN.HAUSAKKU": "house battery state of charge",
"BAUSTEIN.PVUEBERSCHUSS": "PV surplus in watts",
"BAUSTEIN.SPOTPREIS": "electricity price from the spot price plugin",
"ANSAGE.H": "Voice announcement (when an appliance finishes)",
"ANSAGE.H_AUDIOSERVER": "The original Loxone Audioserver has <b>no HTTP TTS interface</b>. In this mode the plugin does not speak itself; trigger the announcement in Loxone Config via a text generator at the TTS input of the audio player block (MQTT value <span class='sm-mono'>geraetN/fertig</span> as trigger).",
"ANSAGE.H_EIN": "Spoken when an appliance changes to <i>finished</i> – once per programme run, never on LoxBerry restart. Default: off.",
"ANSAGE.H_TEST": "Announcement",
"ANSAGE.H_TEST_TEXT": "Speaks immediately into the configured zones – regardless of whether the announcement is enabled.",
"ANSAGE.H_VORLAGE": "Placeholders: <span class='sm-mono'>{ip} {port} {zones} {vol} {lang} {text}</span>. Empty = MusicServer4Home default template.",
"ANSAGE.H_ZONEN": "Zone numbers separated by commas (e.g. <span class='sm-mono'>2,4,6</span>) — the volume comes from the field next to it. Optionally a separate volume per zone: <span class='sm-mono'>zone~volume</span> (e.g. <span class='sm-mono'>2~25,4~40</span>). Spaces after the comma are allowed — <span class='sm-mono'>2,4,6</span> and <span class='sm-mono'>2, 4, 6</span> both work.",
"ANSAGE.K_TEST": "Speak test announcement now",
"ANSAGE.L_AUSGABE": "Audio output",
"ANSAGE.L_EIN": "Enable announcement",
"ANSAGE.L_IP": "IP of the audio server",
"ANSAGE.L_LAUTSTAERKE": "Volume",
"ANSAGE.L_PORT": "Port",
"ANSAGE.L_SPRACHE": "Language",
"ANSAGE.L_VORLAGE": "URL template for Audioserver4Home/MS4H or custom systems",
"ANSAGE.L_ZONEN": "Zones",
"ANSAGE.O_AUDIOSERVER": "Original Loxone Audioserver (via Loxone Config)",
"ANSAGE.O_CUSTOM": "Custom URL template",
"ANSAGE.O_MS4H": "Audioserver4Home / MusicServer4Home",
"ANSAGE.O_MUSICSERVER": "Loxone Music Server (classic)",
"ANSAGE.TESTTEXT": "Hello! This is a test announcement of the Weissware plugin.",
"ANSAGE.TEST_FEHLER": "Test announcement failed – check the settings and ansage.log.",
"ANSAGE.TEST_OK": "Test announcement sent – the announcement log is in ansage.log.",
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
"WW_NAME.ALTER": "Age",
"WW_NAME.CMD_ABRUF": "Poll now (command)",
"WW_NAME.CMD_NETZ": "On/Off (command)",
"WW_NAME.CMD_PAUSE": "Pause (command)",
"WW_NAME.CMD_PROGRAMM": "Programme (command)",
"WW_NAME.ENERGIE": "Energy",
"WW_NAME.FERNBED": "Remote control",
"WW_NAME.FERNSTART": "Remote start",
"WW_NAME.FERTIG": "Finished",
"WW_NAME.FERTIGUM": "Finished at",
"WW_NAME.FORTSCHR": "Progress",
"WW_NAME.LAEUFT": "Running",
"WW_NAME.LAUFMIN": "Runtime",
"WW_NAME.NETZ": "Power",
"WW_NAME.OK": "OK",
"WW_NAME.RESTMIN": "Time left",
"WW_NAME.SCHLEUDER": "Spin speed",
"WW_NAME.STARTMIN": "Start delay",
"WW_NAME.TEMP": "Temperature",
"WW_NAME.TUER": "Door",
"WW_NAME.VERBUNDEN": "Connected",
"WW_NAME.VOK": "OK (consumption)",
"WW_NAME.WASSER": "Water",
"WW_NAME.ZUSTAND": "State",
}

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
    "&auml;": "ä", "&ouml;": "ö", "&uuml;": "ü",
    "&Auml;": "Ä", "&Ouml;": "Ö", "&Uuml;": "Ü",
    "&szlig;": "ß", "&mdash;": "—", "&ndash;": "–",
    "&minus;": "−", "&bdquo;": "„", "&ldquo;": "“",
    "&rdquo;": "”", "&hellip;": "…", "&bull;": "•",
    "&middot;": "·", "&rarr;": "→", "&larr;": "←",
    "&deg;": "°", "&euro;": "€", "&sect;": "§",
    "&sup2;": "²", "&sup3;": "³", "&le;": "≤",
    "&ge;": "≥", "&times;": "×",
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


def benutzte_schluessel(wurzel: Path) -> set:
    """Alle im PHP vorkommenden Schluessel, direkt oder als Zeichenkette."""
    treffer = set()
    for f in php_dateien(wurzel):
        t = f.read_text(encoding="utf-8")
        for m in re.finditer(r"ww_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t):
            treffer.add(m.group(1))
        for m in re.finditer(r"'(WW_[A-Z]+\.[A-Z0-9_]+|BAUSTEIN\.[A-Z0-9_]+)'", t):
            treffer.add(m.group(1))
    # Schluessel, die zur Laufzeit zusammengesetzt werden
    treffer |= {"EINST.DIENST_START", "EINST.DIENST_STOP", "EINST.DIENST_RESTART"}
    for feld in ("TAKT_RUHE", "TAKT_BETRIEB", "WARTEZEIT"):
        treffer.add("EINST.L_" + feld)
    # ww_titel() setzt den Schluessel zur Laufzeit zusammen: WW_NAME.<FELD>.
    # Diese Namen stehen in den Feldtabellen, nicht als woertlicher Aufruf -
    # der Scanner findet sie sonst nicht und meldet sie als unbenutzt.
    for feld in ("ZUSTAND", "LAEUFT", "FERTIG", "VERBUNDEN", "TUER", "FORTSCHR",
                 "RESTMIN", "STARTMIN", "LAUFMIN", "FERNSTART", "FERNBED", "NETZ",
                 "ALTER", "OK", "FERTIGUM", "ENERGIE", "WASSER", "TEMP",
                 "SCHLEUDER", "VOK", "CMD_PROGRAMM", "CMD_PAUSE", "CMD_NETZ",
                 "CMD_ABRUF"):
        treffer.add("WW_NAME." + feld)
    return treffer


def ini_schreiben(pfad: Path, kopf: str, texte: dict) -> None:
    abschnitte = {}
    for k, v in texte.items():
        a, s = k.split(".", 1)
        abschnitte.setdefault(a, {})[s] = v
    reihenfolge = ["REITER", "LEGENDE", "ALLG", "EINST", "MQTT", "LOX", "BAUSTEIN",
                   "TEST", "LOG", "WW_FELD", "WW_VFELD", "WW_XFELD", "WW_MQTT"]
    zeilen = [kopf]
    for a in reihenfolge + [x for x in sorted(abschnitte) if x not in reihenfolge]:
        if a not in abschnitte:
            continue
        zeilen.append("\n[" + a + "]")
        for s in sorted(abschnitte[a]):
            zeilen.append('%s = "%s"' % (s, entitaeten_aufloesen(abschnitte[a][s])))
    pfad.parent.mkdir(parents=True, exist_ok=True)
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
    print("[OK]   %d Schluessel, DE und EN deckungsgleich, alle im PHP benutzt,"
          % len(DE))
    print("[OK]   %d davon maskiert und frei von Auszeichnung," % len(maskiert))
    print("[OK]   keine doppelten Anfuehrungszeichen, Platzhalter passen zusammen.")
    return 0


def main() -> int:
    wurzel = Path(sys.argv[1])
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
