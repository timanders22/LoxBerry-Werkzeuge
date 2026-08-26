#!/usr/bin/env python3
"""Erzeugt die Sprachdateien des Volkswagen-ID-Plugins.

Warum erzeugt und nicht von Hand gepflegt: Beim Anker-SOLIX-Plugin sind so
zwei Fehlerklassen aufgefallen, die beim Handpflegen unsichtbar bleiben.

1. Doppelte Maskierung. Ein Text, der durch vw_e() laeuft und selbst eine
   HTML-Entitaet enthaelt, erscheint als "pr&amp;uuml;fen" auf dem Bildschirm.
   Dieses Skript kennt aus dem PHP, welche Schluessel maskiert ausgegeben
   werden, und laesst dort keine Auszeichnung und keine Entitaet zu.
2. Abgeschnittene Werte. Bei parse_ini_file beginnt mit ';' ein Kommentar.
   Jeder Wert steht deshalb in doppelten Anfuehrungszeichen, und im Wert darf
   kein weiteres doppeltes Anfuehrungszeichen stehen (HTML-Attribute einfach
   quoten).

Aufruf:  vw_sprache_erzeugen.py <pluginordner> [--pruefen]
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
"ALLG.FAHRZEUGE": "Fahrzeuge",
"ALLG.FAHRZEUG": "Fahrzeug",
"ALLG.LIB_FEHLT": "Bibliothek fehlt",
"ALLG.GATEWAY": "Gateway des LoxBerry",
"ALLG.EIN": "ein",
"ALLG.AUS": "aus",
"ALLG.JA": "ja",
"ALLG.NEIN": "nein",
"ALLG.SOC": "Ladezustand",
"ALLG.KM": "Kilometerstand",
"ALLG.REICHWEITE": "Reichweite",
"ALLG.VERRIEGELT": "verriegelt",
"ALLG.OHNE_NAMEN": "ohne Modellangabe",
"ALLG.LETZTE_STOERUNG": "Letzte Störung:",
"ALLG.AUSFAELLE": "Abrufe, die dieses Fahrzeug nicht beantwortet hat:",
"ALLG.VERLAUF_HINWEIS": "Ladezustand beziehungsweise Tankfüllstand des heutigen Tages. Ein Messpunkt höchstens alle vier Minuten.",
"ALLG.EIGENSCHAFT": "Eigenschaft",
"ALLG.WERT": "Wert",
"ALLG.SEKUNDEN": "Sekunden",
"ALLG.SPEICHERN": "Speichern",

# ---- Einstellungen ---------------------------------------------------------
"EINST.H_DIENST": "Abrufdienst",
"EINST.DIENST_ERKLAERUNG": "Der Dienst holt die Werte im eingestellten Takt aus der Volkswagen-Schnittstelle und legt sie ab. Oberfl&auml;che und Miniserver lesen nur das Abgelegte &mdash; sie sprechen nie selbst mit dem Anbieter.",
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

"EINST.H_KONTO": "Zugang zum Volkswagen-Konto",
"EINST.KONTO_ERKLAERUNG": "Es sind die Zugangsdaten des <b>Volkswagen-Kontos</b> &mdash; dieselben, mit denen Sie sich in der App <i>Volkswagen</i> beziehungsweise <i>We Connect ID</i> anmelden. Nicht die eines H&auml;ndlerportals. Sie werden in einer eigenen Datei mit den Rechten 0600 abgelegt, nicht in der Konfiguration, die diese Seite anzeigt. <b>Zwei Hinweise:</b> Der Connector arbeitet mit <b>europ&auml;ischen</b> Fahrzeugen &mdash; f&uuml;r Nordamerika gibt es einen eigenen, hier nicht eingebauten. Und einzelne Konten verlangen eine Zwei-Faktor-Best&auml;tigung; die l&auml;sst sich nicht automatisieren. Wer davon betroffen ist, meldet sich einmal im Browser auf diesem Ger&auml;t an.",
"EINST.L_EMAIL": "Benutzername (E-Mail-Adresse)",
"EINST.H_EMAIL": "Die E-Mail-Adresse, mit der das Volkswagen-Konto angelegt wurde.",
"EINST.L_PASSWORT": "Passwort",
"EINST.H_PASSWORT": "Bleibt das Feld leer, bleibt das gespeicherte Passwort unver&auml;ndert. Es wird nie angezeigt &mdash; im Reiter Test steht nur seine L&auml;nge.",
"EINST.PW_GESETZT": "gespeichert (%d Zeichen) – leer lassen, um es zu behalten",
"EINST.PW_LEER": "noch kein Passwort gespeichert",
"EINST.L_SPIN": "S-PIN (vier Ziffern, freiwillig)",
"EINST.H_SPIN": "Die vierstellige S-PIN aus der Volkswagen-App. Dieses Plugin bietet <b>kein</b> Ver- oder Entriegeln und keine Hupe an und braucht sie deshalb nicht; das Feld ist f&uuml;r eine sp&auml;tere Fassung vorbereitet. Wer sie nicht braucht, l&auml;sst es leer.",
"EINST.SPIN_GESETZT": "gespeichert – leer lassen, um sie zu behalten",
"EINST.SPIN_LEER": "keine S-PIN gespeichert",

"EINST.H_TAKT": "Abholtakt",
"EINST.TAKT_WARNUNG": "<b>Untergrenze 180 Sekunden.</b> Der Volkswagen-Connector nimmt darunter gar nichts an &mdash; er wirft beim Anlegen einen Fehler. Und auch dar&uuml;ber gilt: zu h&auml;ufige Anfragen weist Volkswagen mit HTTP 429 ab, und ein st&auml;ndig geweckter Wagen kostet Ruhestrom. F&uuml;nf Minuten sind ein guter Anfang. Wird ein Wert sofort gebraucht, ist der Abruf-Befehl der richtige Weg, nicht ein k&uuml;rzerer Takt.",
"EINST.L_INTERVALL": "Takt in Sekunden",
"EINST.H_INTERVALL": "Abstand zwischen zwei Abrufen. Zul&auml;ssig sind 180 bis 3600 Sekunden &mdash; 180 ist die Untergrenze der Bibliothek, nicht eine Vorsichtsma&szlig;nahme dieses Plugins.",
"EINST.L_TAKT_WARTUNG": "Wartungswerte alle … Takte",
"EINST.H_TAKT_WARTUNG": "Inspektion und &Ouml;lservice &auml;ndern sich in Tagen, nicht in Minuten. Bei einem Takt von 300 Sekunden bedeutet 12 also: einmal je Stunde.",
"EINST.L_VERLAUF_TAGE": "Verlauf aufbewahren (Tage)",
"EINST.H_VERLAUF_TAGE": "Wie lange die Messpunkte f&uuml;r die kleine Tagesgrafik aufgehoben werden.",

"EINST.H_STEUERUNG": "Schreibende Befehle",
"EINST.STEUERUNG_ERKLAERUNG": "Ab Werk <b>gesperrt</b>. Schreibende Befehle greifen in ein Fahrzeug ein, das irgendwo steht &mdash; ein versehentlich gestarteter Standklimaanlagenlauf entl&auml;dt die Batterie, und ein angehaltener Ladevorgang f&auml;llt erst am n&auml;chsten Morgen auf. Erst freigeben, wenn die Lesewerte im Reiter Test stimmen. <b>Ver- und Entriegeln bietet dieses Plugin nicht an.</b>",
"EINST.L_STEUERUNG_EIN": "Schreibende Befehle zulassen",
"EINST.L_TEMP_MIN": "Kleinste erlaubte Zieltemperatur (Grad Celsius)",
"EINST.L_TEMP_MAX": "Größte erlaubte Zieltemperatur (Grad Celsius)",
"EINST.H_TEMP": "Grenzen f&uuml;r die Klimatisierung. Ein Wert au&szlig;erhalb wird <b>abgewiesen</b>, nicht auf die Grenze gekappt: ein still ver&auml;nderter Sollwert f&uuml;hrt zu einem Fahrzeug, das etwas anderes tut als angezeigt.",
"EINST.L_WARTEZEIT": "Wartezeit auf die Antwort (Sekunden)",
"EINST.H_WARTEZEIT": "So lange wartet die Oberfl&auml;che, bis der Dienst einen Befehl beantwortet hat. Danach meldet sie <span class='sm-mono'>OK=2</span> &mdash; eingereiht, Ergebnis unbekannt. Es wird bewusst kein Erfolg gemeldet, den niemand gepr&uuml;ft hat.",

"EINST.L_MQTT_EIN": "Werte über MQTT veröffentlichen",
"EINST.L_MQTT_TOPIC": "Themenpräfix",
"EINST.H_MQTT_TOPIC": "Erlaubt sind Buchstaben, Ziffern, Bindestrich, Unterstrich und Schr&auml;gstrich. Aus dem Pr&auml;fix ergeben sich alle Themen, siehe Reiter MQTT.",

"EINST.GESPEICHERT": "Die Einstellungen wurden gespeichert.",
"EINST.FEHLER_ZAHL": "%s: bitte eine ganze Zahl eintragen.",
"EINST.FEHLER_BEREICH": "%s: der Wert muss zwischen %d und %d liegen.",
"EINST.FEHLER_TEMP_TAUSCH": "Die kleinste Zieltemperatur ist größer als die größte. Bitte die beiden Werte tauschen.",
"EINST.FEHLER_TOPIC": "Das Themenpräfix enthält unerlaubte Zeichen. Erlaubt sind Buchstaben, Ziffern, Bindestrich, Unterstrich und Schrägstrich.",
"EINST.FEHLER_EMAIL": "Der Benutzername sieht nicht wie eine E-Mail-Adresse aus.",
"EINST.FEHLER_SPIN": "Die S-PIN besteht aus genau vier Ziffern. Der eingegebene Wert passt nicht in dieses Muster und wurde nicht gespeichert.",
"EINST.FEHLER_ZUGANG_SPEICHERN": "Die Zugangsdatei ließ sich nicht schreiben. Rechte des Konfigurationsordners prüfen.",
"EINST.FEHLER_SPEICHERN": "Die Konfiguration ließ sich nicht schreiben: %s",
"EINST.WARN_PW_OHNE_KONTO": "Es ist ein Passwort gespeichert, aber kein Benutzername. So schlägt jede Anmeldung fehl, ohne dass man den Grund sieht.",

"EINST.H_ERKANNT": "Erkannte Fahrzeuge",
"EINST.KEINE_FAHRZEUGE": "Noch kein Fahrzeug erkannt. Das ist bis zum ersten erfolgreichen Abruf normal: Zugangsdaten eintragen, speichern, Dienst starten und eine Taktl&auml;nge abwarten. Bleibt die Liste danach leer, steht der Grund im Reiter Test und in der Logdatei.",
"EINST.T_NR": "Nr.",
"EINST.T_MODELL": "Modell",
"EINST.T_KENNZEICHEN": "Kennzeichen",
"EINST.T_VIN": "Fahrgestellnummer",
"EINST.T_ANTRIEB": "Antrieb",
"EINST.T_BATTERIE": "Batterie",
"EINST.T_SOFTWARE": "Softwarestand",
"EINST.VIN_HINWEIS": "In allen Adressen kann statt der Nummer auch die Fahrgestellnummer stehen &mdash; <span class='sm-mono'>fahrzeug=WVW…</span>. Das ist stabiler, wenn sp&auml;ter ein zweites Fahrzeug ins Konto kommt und sich die Reihenfolge verschiebt.",

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
"MQTT.THEMEN_ERKLAERUNG": "Ein Thema, das dieses Fahrzeug nicht beantwortet, wird gar nicht erst gesendet &mdash; es entsteht also kein Thema mit einer erfundenen Null.",
"MQTT.T_THEMA": "Thema",
"MQTT.T_BEDEUTUNG": "Bedeutung",
"MQTT.PLATZHALTER": "<b>N</b> steht f&uuml;r die laufende Nummer des Fahrzeugs, also 1 f&uuml;r das erste.",

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
"LOX.MEHRERE_FAHRZEUGE": "Mehrere Fahrzeuge im Konto — je Fahrzeug ein eigener virtueller Eingang:",
"LOX.K_VORLAGE": "Vorlage für Loxone Config herunterladen",
"LOX.T_ADRESSE": "Adresse",
"LOX.T_ZYKLUS": "Abfragezyklus",
"LOX.T_TITEL": "Bezeichnung",
"LOX.T_BEFEHL": "Befehlserkennung",
"LOX.T_EINHEIT": "Einheit",
"LOX.T_BEDEUTUNG": "Bedeutung",

"LOX.S4_TITEL": "Schritt 4: Weitere Eingänge für Laden, Wartung und Standort",
"LOX.S4_TEXT": "Drei weitere virtuelle HTTP-Eing&auml;nge, jeder nach demselben Muster wie Schritt 3. Der Lade-Eingang bleibt bei einem reinen Verbrenner leer &mdash; dort stehen dann &uuml;berall Striche, und das ist richtig so.",
"LOX.S4_WARTUNG": "<b>Wartung</b> &mdash; ein eigener Eingang mit der Aktion <span class='sm-mono'>wartung</span>. Ein Zyklus von 3600 Sekunden gen&uuml;gt; die Werte &auml;ndern sich in Tagen.",
"LOX.S4_POSITION": "<b>Standort</b> &mdash; ein eigener Eingang mit der Aktion <span class='sm-mono'>position</span>. Die Anschrift steht in einer zweiten Zeile und ist f&uuml;r Loxone nicht gedacht; die erste Zeile besteht bewusst nur aus Zahlen.",

"LOX.S5_TITEL": "Schritt 5: Befehle senden (virtueller Ausgang)",
"LOX.S5_TEXT": "Nur n&ouml;tig, wenn Loxone etwas ausl&ouml;sen soll. In Loxone Config einen <i>Virtuellen Ausgang</i> mit der unten stehenden Adresse anlegen und darunter je Befehl einen <i>Virtuellen Ausgang Befehl</i>. Im Befehlstext steht <span class='sm-mono'>&lt;v&gt;</span> f&uuml;r den &uuml;bergebenen Wert.",
"LOX.T_VA_ADRESSE": "Adresse des virtuellen Ausgangs",
"LOX.T_VA_KLIMA_EIN": "Klimatisierung ein (21 Grad)",
"LOX.T_VA_KLIMA_AUS": "Klimatisierung aus",
"LOX.T_VA_LADEN_EIN": "Laden starten",
"LOX.T_VA_LADEN_AUS": "Laden anhalten",
"LOX.T_VA_LADEGRENZE": "Ladegrenze setzen",
"LOX.T_VA_SCHEIBE": "Scheibenheizung ein",
"LOX.T_VA_ABRUF": "Sofortabruf auslösen",
"LOX.S5_WARNUNG": "Zwei Dinge, die man vorher wissen sollte. <b>Erstens:</b> Schreibende Befehle sind ab Werk gesperrt und m&uuml;ssen im Reiter Einstellungen erst freigegeben werden. <b>Zweitens:</b> Eine Antwort mit <span class='sm-mono'>OK=1</span> hei&szlig;t, dass der Volkswagen-Server den Auftrag mit HTTP 200 entgegengenommen hat. Ob das Fahrzeug ihn ausf&uuml;hrt, zeigt erst der n&auml;chste Abruf &mdash; wer sicher sein will, wertet den zur&uuml;ckgelesenen Zustand aus und nicht die Antwort auf den Befehl.",

"LOX.S6_TITEL": "Schritt 6: Das Token",
"LOX.T_TOKEN": "Token dieses Plugins",
"LOX.S6_TEXT": "Der Endpunkt liegt im unangemeldeten Bereich, damit Loxone ihn ohne Zugangsdaten erreicht. Gesch&uuml;tzt ist er durch dieses Token. Es steckt in jeder Adresse, die Sie im Miniserver eintragen &mdash; <b>ein neues Token macht alle diese Adressen auf einen Schlag ung&uuml;ltig</b> und muss &uuml;berall nachgetragen werden. W&uuml;rfeln Sie es also nur neu, wenn es tats&auml;chlich in falsche H&auml;nde geraten ist.",

"LOX.S7_TITEL": "Schritt 7: Ausfallerkennung",
"LOX.S7_TEXT": "Schweigt die Cloud, behalten die virtuellen Eing&auml;nge ihren letzten Wert. In der App sieht dann alles normal aus, obwohl seit Stunden nichts mehr angekommen ist. Deshalb wird der Wert <span class='sm-mono'>ALTER</span> mitgef&uuml;hrt: er sagt, wie alt das Abbild in Sekunden ist. Die Schwelle daf&uuml;r geh&ouml;rt <b>deutlich &uuml;ber den Abholtakt</b> &mdash; bei 300 Sekunden Takt sind 900 Sekunden ein brauchbarer Wert, dann l&ouml;st ein einzelner verpasster Durchlauf noch keine Meldung aus.",

"LOX.S8_TITEL": "Schritt 8: Komplette Baustein-Liste zum 1:1-Nachbauen",
"LOX.S8_TEXT": "Jede Zeile ein Baustein. Loxone Config f&uuml;hrt alle in der Baustein-Suche (Taste F5). Die Zeilen 1 bis 12 sind die virtuellen Eing&auml;nge aus Schritt 3 und 4 &mdash; wer die Vorlage geladen hat, findet sie bereits im Baum.",
"LOX.S8_ERLAEUTERUNG": "<p><b>Zu #13 bis #16:</b> Die Meldung &bdquo;Fahrzeug offen oder Licht an&ldquo; l&auml;uft &uuml;ber ein ODER und eine Einschaltverz&ouml;gerung. Beides ist Absicht. Der Benachrichtigungs-Baustein sendet nur beim Wechsel von Aus auf Ein; h&auml;ngt man mehrere Quellen direkt an seinen Eingang, verschluckt eine dauerhaft aktive Quelle alle &uuml;brigen. Die Verz&ouml;gerung von f&uuml;nf Minuten verhindert eine Meldung, w&auml;hrend man gerade einl&auml;dt.</p><p><b>Zu #17 und #18:</b> Zwei getrennte Schwellwertschalter, weil ein Fahrzeug entweder einen Ladezustand oder einen Tankf&uuml;llstand liefert &mdash; bei einem Hybrid beides. Der jeweils nicht gelieferte Wert bleibt ein Strich; der zugeh&ouml;rige Schalter beh&auml;lt dann seinen letzten Zustand und schaltet nicht.</p><p><b>Zu #21 und #22:</b> Der Benachrichtigungs-Baustein sendet nur beim Wechsel von Aus auf Ein &mdash; genau deshalb ist er hier richtig: Sie bekommen eine Meldung, wenn das Ladekabel eingesteckt wird, und nicht dauernd, solange es steckt. Wer lieber die umgekehrte Meldung will (&bdquo;Kabel wurde gezogen&ldquo;), setzt ein NICHT davor.</p><p><b>Zu #23:</b> Die Inspektionsmeldung braucht den Eingang aus dem Wartungs-Abruf (Schritt 4), nicht den aus dem Status-Abruf.</p><p><b>Zu #25:</b> Die Schwelle f&uuml;r die Ausfallerkennung liegt bewusst beim Dreifachen des Abholtakts. Wer sie knapper setzt, bekommt bei jedem einzelnen verpassten Durchlauf eine Meldung.</p><p><b>Zu #28 bis #33:</b> Die Vorheizung ist optional. Die Wochenuhr gibt die gew&uuml;nschte Abfahrtszeit vor, die UND-Verkn&uuml;pfung mit der Anwesenheit verhindert das Heizen, w&auml;hrend Sie im Urlaub sind, und der Impulsgeber sorgt daf&uuml;r, dass der Befehl einmal ausgel&ouml;st und nicht dauerhaft gesendet wird. <b>Loxone-Zeitrechnung:</b> Sekunden seit dem 01.01.2009. Liefert ein Zeit-Baustein Unix-Zeit (Werte um 1,23 Milliarden), sind 1230768000 abzuziehen.</p><p><b>Zu #34:</b> Optional, aber n&uuml;tzlich: ein Befehl, der die Klimatisierung von Hand wieder ausschaltet. Ohne ihn l&auml;uft sie bis zum eigenen Zeitablauf weiter.</p><p><b>Zu #14 &mdash; warum dort vier Quellen an zwei Eing&auml;ngen h&auml;ngen:</b> Bei UND und ODER ist die Zahl der Eing&auml;nge eine Eigenschaft des Bausteins, die Loxone Config selbst setzt. Zieht man einen dritten Eingang auf, &ouml;ffnet Config die Datei beim n&auml;chsten Mal ohne jede Meldung, entfernt den Eingang wieder &mdash; und l&ouml;scht dabei alle Verbindungen, die daran hingen. Erlaubt ist dagegen, an <i>einen</i> Eingang mehrere Quellen zu h&auml;ngen; sie werden ODER-verkn&uuml;pft. An einem ODER ist das dasselbe Ergebnis mit zwei Eing&auml;ngen. <b>An einem UND w&auml;re es falsch</b>: dort werden mehrere Quellen an einem Eingang ebenfalls ODER-verkn&uuml;pft, und damit wird aus dem UND ein ODER, ohne dass es irgendetwas meldet. Bei #30 h&auml;ngt deshalb an jedem Eingang genau eine Quelle.</p>",

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
"BAUSTEIN.T_NICHT": "NICHT",
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
"BAUSTEIN.ANWESEND": "Anwesenheitsmelder",
"BAUSTEIN.MANUELL": "von Hand oder aus einer Szene",

"BAUSTEIN.N01": "VW_1_SOC",
"BAUSTEIN.P01": "Einheit %, aus dem Status-Eingang",
"BAUSTEIN.N02": "VW_1_TANK",
"BAUSTEIN.P02": "Einheit %, aus dem Status-Eingang",
"BAUSTEIN.N03": "VW_1_REICHW",
"BAUSTEIN.P03": "Einheit km, aus dem Status-Eingang",
"BAUSTEIN.N04": "VW_1_KM",
"BAUSTEIN.P04": "Einheit km, aus dem Status-Eingang",
"BAUSTEIN.N05": "VW_1_VERR",
"BAUSTEIN.P05": "1 = verriegelt, 0 = offen",
"BAUSTEIN.N06": "VW_1_TUEREN",
"BAUSTEIN.P06": "1 = mindestens eine Tür offen",
"BAUSTEIN.N07": "VW_1_FENSTER",
"BAUSTEIN.P07": "1 = mindestens ein Fenster offen",
"BAUSTEIN.N08": "VW_1_LICHT",
"BAUSTEIN.P08": "1 = Licht an",
"BAUSTEIN.N09": "VW_1_KLIMA",
"BAUSTEIN.P09": "1 = Klimatisierung läuft",
"BAUSTEIN.N10": "VW_1_KABEL",
"BAUSTEIN.P10": "1 = Ladekabel steckt, aus dem Lade-Eingang",
"BAUSTEIN.N11": "VW_1_ALTER",
"BAUSTEIN.P11": "Einheit s, Alter des Abbilds",
"BAUSTEIN.N12": "VW_1_INSPTAGE",
"BAUSTEIN.P12": "Einheit d, aus dem Wartungs-Eingang",
"BAUSTEIN.N13": "Fahrzeug nicht verriegelt",
"BAUSTEIN.N14": "Fahrzeug offen oder Licht an",
"BAUSTEIN.N15": "Verzögerung Offen-Meldung",
"BAUSTEIN.P15": "Einschaltverzögerung 300 s",
"BAUSTEIN.N16": "Meldung: Fahrzeug ist offen",
"BAUSTEIN.P16": "Betreff frei wählbar, Empfänger in den Benutzereinstellungen",
"BAUSTEIN.N17": "Ladezustand niedrig",
"BAUSTEIN.P17": "Ein < 20, Aus > 25 (Hysterese, sonst flattert es)",
"BAUSTEIN.N18": "Tankfüllstand niedrig",
"BAUSTEIN.P18": "Ein < 15, Aus > 20",
"BAUSTEIN.N19": "Reichweite gering",
"BAUSTEIN.N20": "Meldung: Reichweite gering",
"BAUSTEIN.P20": "Betreff frei wählbar",
"BAUSTEIN.N21": "Ladekabel steckt",
"BAUSTEIN.P21": "Ein > 0,5, Aus < 0,5",
"BAUSTEIN.N22": "Meldung: Ladekabel eingesteckt",
"BAUSTEIN.P22": "Betreff frei wählbar",
"BAUSTEIN.N23": "Inspektion fällig",
"BAUSTEIN.P23": "Ein < 14, Aus > 21 (Tage)",
"BAUSTEIN.N24": "Meldung: Inspektion fällig",
"BAUSTEIN.P24": "Betreff frei wählbar",
"BAUSTEIN.N25": "Abruf ausgefallen",
"BAUSTEIN.P25": "Ein > 900, Aus < 600 (bei 300 s Takt)",
"BAUSTEIN.N26": "Meldung: Keine Daten mehr vom Fahrzeug",
"BAUSTEIN.P26": "Betreff frei wählbar",
"BAUSTEIN.N27": "Fahrzeugübersicht",
"BAUSTEIN.P27": "Statusbaustein für die App-Kachel",
"BAUSTEIN.N28": "Abfahrtszeit",
"BAUSTEIN.P28": "Wochenuhr, Einschaltpunkt 30 Minuten vor der Abfahrt",
"BAUSTEIN.N29": "Klima jetzt",
"BAUSTEIN.P29": "Taster als Impuls",
"BAUSTEIN.N30": "Vorheizen nur bei Anwesenheit",
"BAUSTEIN.P30": "verhindert Vorheizen im Urlaub",
"BAUSTEIN.N31": "Klimatisierung anfordern",
"BAUSTEIN.N32": "Einmal auslösen",
"BAUSTEIN.P32": "Impulsgeber, damit der Befehl nicht im Takt wiederholt wird",
"BAUSTEIN.N33": "Volkswagen Klima ein",
"BAUSTEIN.P33": "Befehl bei EIN, Adresse aus Schritt 5",
"BAUSTEIN.N34": "Volkswagen Klima aus",
"BAUSTEIN.P34": "optional, Befehl bei EIN",

# ---- Test ------------------------------------------------------------------
"TEST.H_SELBSTPRUEFUNG": "Selbstprüfung",
"TEST.EINLEITUNG": "Diese Pr&uuml;fung beantwortet <b>ohne Loxone</b>, ob die Einrichtung tr&auml;gt. Jede Zeile ist eine Frage; ein Kreuz bedeutet, dass hier etwas fehlt. Was sich nur mit Fahrzeug pr&uuml;fen lie&szlig;e, steht unten ausdr&uuml;cklich als ungepr&uuml;ft.",
"TEST.T_FRAGE": "Frage",
"TEST.T_BEFUND": "Befund",
"TEST.F_VENV": "Ist die virtuelle Python-Umgebung vorhanden?",
"TEST.A_VENV_FEHLT": "nein — Plugin neu installieren",
"TEST.F_PYTHON": "Ist das Python neu genug (3.9 oder neuer)?",
"TEST.A_PYTHON_ZU_ALT": "zu alt für carconnectivity",
"TEST.A_PYTHON_UNBEKANNT": "nicht feststellbar — die virtuelle Umgebung fehlt",
"TEST.F_LIB": "Ist der Kern der Bibliothek geladen, und in welcher Fassung?",
"TEST.A_LIB_FEHLT": "nein — siehe Ausgabe der Installation",
"TEST.F_DIENST": "Läuft der Abrufdienst?",
"TEST.A_DIENST_LAEUFT": "ja, PID",
"TEST.A_DIENST_SOLL_TOT": "nein — er soll laufen, tut es aber nicht. Logdatei ansehen.",
"TEST.A_DIENST_GESTOPPT": "nein — bewusst angehalten",
"TEST.F_KONTO": "Ist ein Benutzername hinterlegt?",
"TEST.A_KONTO_FEHLT": "nein",
"TEST.F_PASSWORT": "Ist ein Passwort hinterlegt?",
"TEST.A_PASSWORT_DA": "ja, %d Zeichen (der Inhalt wird nicht angezeigt)",
"TEST.A_PASSWORT_FEHLT": "nein",
"TEST.F_RECHTE": "Ist die Zugangsdatei vor fremden Blicken geschützt?",
"TEST.A_ZUGANGSDATEI_FEHLT": "die Datei fehlt",
"TEST.F_FAHRZEUGE": "Sind Fahrzeuge erkannt?",
"TEST.A_FAHRZEUGE": "ja, %d",
"TEST.A_KEINE_FAHRZEUGE": "nein — bis zum ersten erfolgreichen Abruf normal",
"TEST.F_AUSFAELLE": "Beantwortet das Fahrzeug alle Abrufe?",
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
"TEST.KEINE_MESSPUNKTE": "noch keine Messpunkte für heute",

"TEST.H_LESEN": "Ansehen",
"TEST.K_STATUS": "Status abrufen",
"TEST.K_LADEN": "Ladewerte abrufen",
"TEST.K_WARTUNG": "Wartungswerte abrufen",
"TEST.K_FAHRZEUGE": "Fahrzeuge auflisten",
"TEST.H_TECHNIK": "Technische Auskunft",
"TEST.K_SELBSTTEST": "Selbsttest des Dienstes",
"TEST.K_ROH": "Rohdaten als JSON ansehen",
"TEST.H_SCHALTEN": "Schalten",
"TEST.SCHALTEN_WARNUNG": "<b>Diese Kn&ouml;pfe wirken sofort und am echten Fahrzeug.</b> Eine Klimatisierung entl&auml;dt die Batterie, ein angehaltener Ladevorgang f&auml;llt erst am n&auml;chsten Morgen auf, und ein Weckruf holt das Fahrzeug aus dem Ruhezustand &mdash; das kostet Strom.",
"TEST.SCHALTEN_GESPERRT": "Schreibende Befehle sind zurzeit gesperrt. Die Kn&ouml;pfe geben deshalb eine Ablehnung zur&uuml;ck &mdash; das ist kein Fehler. Freigeben im Reiter Einstellungen.",
"TEST.L_FAHRZEUG": "Fahrzeug (laufende Nummer)",
"TEST.L_TEMP": "Zieltemperatur in Grad Celsius",
"TEST.H_TEMP": "Halbe Grad sind erlaubt, etwa <span class='sm-mono'>21.5</span>. Werte au&szlig;erhalb der eingestellten Grenzen werden abgewiesen und nicht gekappt.",
"TEST.L_PROZENT": "Ladegrenze in Prozent",
"TEST.H_PROZENT": "Zul&auml;ssig sind 10 bis 100. Volkswagen rundet auf die Stufen, die das Fahrzeug kennt &mdash; meist Zehnerschritte.",
"TEST.K_ABRUF": "Sofort abrufen",
"TEST.K_KLIMA_EIN": "Klimatisierung ein",
"TEST.K_KLIMA_AUS": "Klimatisierung aus",
"TEST.K_LADEN_EIN": "Laden starten",
"TEST.K_LADEN_AUS": "Laden anhalten",
"TEST.K_LADEGRENZE": "Ladegrenze setzen",
"TEST.K_SCHEIBE_EIN": "Scheibenheizung ein",
"TEST.K_SCHEIBE_AUS": "Scheibenheizung aus",
"TEST.K_WECKEN": "Fahrzeug wecken",
"TEST.M_FAHRZEUG_UNGUELTIG": "Die Fahrzeugnummer ist keine Zahl zwischen 1 und 99.",
"TEST.M_TEMP_UNGUELTIG": "Die Zieltemperatur muss eine Zahl sein, halbe Grad erlaubt (etwa 21 oder 21.5).",
"TEST.M_PROZENT_UNGUELTIG": "Die Ladegrenze muss eine ganze Zahl sein.",
"TEST.M_UNBEKANNT": "Unbekannte Testaktion.",
"TEST.H_UNGEPRUEFT": "Was in dieser Fassung ungeprüft ist",
"TEST.UNGEPRUEFT": "Dieses Plugin wurde <b>ohne Volkswagen-Konto und ohne Fahrzeug</b> gebaut. Ungepr&uuml;ft ist deshalb: ob die Anmeldung gelingt, ob dieses Fahrzeug die abgefragten Werte liefert und ob die schreibenden Befehle die erwartete Wirkung haben. Alles &uuml;brige ist gepr&uuml;ft &mdash; und zwar nicht gegen Attrappen: die Zuordnung der Werte und die Schreibbefehle sind gegen <b>echte Objekte der Bibliothek</b> gemessen worden. Deshalb tr&auml;gt diese Fassung die Nummer 0.9.0 und nicht 1.0.0. Wenn etwas leer bleibt, hilft der Knopf <i>Rohdaten als JSON ansehen</i>: dort steht, was der Dienst tats&auml;chlich bekommen hat.",

# ---- Logdateien ------------------------------------------------------------
"LOG.H_TITEL": "Logdateien",
"LOG.ERKLAERUNG": "Der Abrufdienst schreibt ausschlie&szlig;lich in diese eine Datei. Unten stehen die letzten 400 Zeilen, die neueste zuerst.",
"LOG.LEER": "Die Logdatei ist leer oder noch nicht angelegt.",
"LOG.K_LEEREN": "Logdatei leeren",
"LOG.GELEERT": "Logdatei geleert",

# ---- Feldbedeutungen (Status) ---------------------------------------------
"VW_FELD.SOC": "Ladezustand der Antriebsbatterie",
"VW_FELD.TANK": "Tankfüllstand",
"VW_FELD.REICHW": "Gesamtreichweite",
"VW_FELD.KM": "Kilometerstand",
"VW_FELD.VERR": "1 = verriegelt, 0 = nicht verriegelt",
"VW_FELD.TUEREN": "1 = mindestens eine Tür offen",
"VW_FELD.FENSTER": "1 = mindestens ein Fenster offen",
"VW_FELD.LICHT": "1 = Licht an",
"VW_FELD.KLIMA": "1 = Klimatisierung läuft (auch Lüften und Zusatzheizen)",
"VW_FELD.ZIELTEMP": "Eingestellte Zieltemperatur der Klimatisierung",
"VW_FELD.AUSSEN": "Außentemperatur, vom Fahrzeug gemessen",
"VW_FELD.ERREICH": "1 = das Fahrzeug ist für die Cloud erreichbar",
"VW_FELD.ALTER": "Alter des Abbilds — für die Ausfallerkennung",
"VW_FELD.OK": "1 = der letzte Abruf war erfolgreich",

# ---- Feldbedeutungen (Laden) ----------------------------------------------
"VW_LFELD.SOC": "Ladezustand der Antriebsbatterie",
"VW_LFELD.LAEDT": "1 = wird gerade geladen",
"VW_LFELD.LADEKW": "Aktuelle Ladeleistung",
"VW_LFELD.TEMPO": "Zugewinn an Reichweite je Stunde",
"VW_LFELD.LADEGR": "Eingestellte Ladegrenze",
"VW_LFELD.KABEL": "1 = Ladekabel steckt",
"VW_LFELD.REICHWBAT": "Reichweite allein aus der Batterie",
"VW_LFELD.OK": "1 = der letzte Abruf war erfolgreich",

# ---- Feldbedeutungen (Wartung) --------------------------------------------
"VW_WFELD.INSPTAGE": "Tage bis zur nächsten Inspektion",
"VW_WFELD.INSPKM": "Kilometer bis zur nächsten Inspektion",
"VW_WFELD.OELTAGE": "Tage bis zum nächsten Ölservice",
"VW_WFELD.OELKM": "Kilometer bis zum nächsten Ölservice",
"VW_WFELD.KM": "Kilometerstand",
"VW_WFELD.OK": "1 = der letzte Abruf war erfolgreich",

# ---- MQTT-Themen -----------------------------------------------------------
"VW_MQTT.OK": "1 = der letzte Abruf war erfolgreich",
"VW_MQTT.FAHRZEUGE": "Anzahl der Fahrzeuge im Konto",
"VW_MQTT.SOC": "Ladezustand der Antriebsbatterie in Prozent",
"VW_MQTT.REICHWEITE": "Gesamtreichweite in km",
"VW_MQTT.TANK": "Tankfüllstand in Prozent",
"VW_MQTT.KM": "Kilometerstand",
"VW_MQTT.VERRIEGELT": "1 = verriegelt",
"VW_MQTT.TUEREN": "1 = mindestens eine Tür offen",
"VW_MQTT.FENSTER": "1 = mindestens ein Fenster offen",
"VW_MQTT.LICHT": "1 = Licht an",
"VW_MQTT.KLIMA": "1 = Klimatisierung läuft",
"VW_MQTT.ZIELTEMP": "Zieltemperatur in Grad Celsius",
"VW_MQTT.AUSSEN": "Außentemperatur in Grad Celsius",
"VW_MQTT.LAEDT": "1 = wird gerade geladen",
"VW_MQTT.LADEKW": "Ladeleistung in kW",
"VW_MQTT.LADEGRENZE": "Eingestellte Ladegrenze in Prozent",
"VW_MQTT.KABEL": "1 = Ladekabel steckt",
"VW_MQTT.BREITE": "Breitengrad des Standorts",
"VW_MQTT.LAENGE": "Längengrad des Standorts",
"VW_MQTT.INSP_TAGE": "Tage bis zur Inspektion",
"VW_MQTT.INSP_KM": "Kilometer bis zur Inspektion",
"VW_MQTT.OEL_TAGE": "Tage bis zum Ölservice",
"VW_MQTT.OEL_KM": "Kilometer bis zum Ölservice",
"VW_MQTT.ERREICHBAR": "1 = für die Cloud erreichbar",
"EINST.H_ZUGRIFF_ERZWINGEN": "Manche Fahrzeuge melden die F&auml;higkeit <span class='sm-mono'>ACCESS</span> nicht, liefern Verriegelung und T&uuml;rzustand aber sehr wohl. Der Connector bietet daf&uuml;r einen Schalter an. Nur einschalten, wenn diese Felder sonst leer bleiben &mdash; sonst fragt das Plugin etwas ab, das es nicht gibt.",
"EINST.L_ZUGRIFF_ERZWINGEN": "Türzustand erzwingen (nur wenn Türen und Verriegelung leer bleiben)",
"EINST.SITZUNG_ERKLAERUNG": "Nach der ersten Anmeldung legt die Bibliothek Anmeldemarken in einer eigenen Datei mit den Rechten 0600 ab und meldet sich damit an, statt jedes Mal das Passwort zu senden. Das schont die Anmeldeseite von Volkswagen, die wiederholte Anmeldungen drosselt. Nach einem Passwortwechsel sind die Marken wertlos &mdash; dann hilft der Knopf <i>Anmeldung neu erzwingen</i> oben.",
"LOX.T_VA_LADESTROM": "Ladestrom setzen (Ampere)",
"TEST.A_CONNECTOR_FEHLT": "nein — siehe Ausgabe der Installation",
"TEST.A_MARKE_FEHLT": "noch nicht angelegt — entsteht beim ersten Abruf",
"TEST.F_CONNECTOR": "Ist der Volkswagen-Connector geladen?",
"TEST.F_MARKE": "Sind die Anmeldemarken vor fremden Blicken geschützt?",
"TEST.H_AMPERE": "Welche Stufen Ihr Fahrzeug kennt, h&auml;ngt vom Modell ab: manche f&uuml;hren den Strom in Ampere (5, 10, 13, 32), die &uuml;brigen kennen nur reduziert (6) und maximal (16). Eine unbekannte Stufe weist Volkswagen ab &mdash; die Ablehnung steht dann in der Meldung.",
"TEST.K_LADESTROM": "Ladestrom setzen",
"TEST.L_AMPERE": "Ladestrom",
"TEST.M_AMPERE_UNGUELTIG": "Der Ladestrom muss eine ganze Zahl sein.",
"VW_FELD.HANDBR": "1 = Handbremse angezogen",
"VW_FELD.SCHEIBE": "1 = Scheibenheizung an",
"VW_FELD.ZUSTAND": "0 = offline, 1 = geparkt, 2 = Zündung an, 3 = fährt",
"VW_LFELD.FERTIGMIN": "Minuten bis zum voraussichtlichen Ladeende",
"VW_LFELD.LADESTROM": "Eingestellter maximaler Ladestrom",
"VW_LFELD.STECKER": "1 = Stecker im Fahrzeug verriegelt",
"VW_MQTT.FERTIG": "Voraussichtliches Ladeende als Unix-Zeit",
"VW_MQTT.HANDBREMSE": "1 = Handbremse angezogen",
"VW_MQTT.LADESTROM": "Eingestellter maximaler Ladestrom in Ampere",
"VW_MQTT.SCHEIBE": "1 = Scheibenheizung an",
"VW_MQTT.STECKER": "1 = Stecker im Fahrzeug verriegelt",
"VW_MQTT.TEMPO": "Zugewinn an Reichweite je Stunde in km/h",
"VW_MQTT.ZUSTAND": "0 = offline, 1 = geparkt, 2 = Zündung an, 3 = fährt",

# Aus der ausgelieferten ini nachgetragen (20.08.2026): der Erzeuger
# kannte sie nicht, das Sprachpaket schon. Ohne den Nachtrag haette ein
# Lauf des Erzeugers diese Texte geloescht.
"EINST.FEHLER_ZUGANG_LOESCHEN": "Die Zugangsdaten ließen sich nicht löschen. Rechte der Dateien prüfen.",
"EINST.H_ZUGANG_LOESCHEN": "Entfernt E-Mail, Passwort und S-PIN restlos — einschließlich der Sicherungskopie und der gespeicherten Anmeldemarken (<span class='sm-mono'>token.json</span>), denn die sind auch ohne Passwort ein gültiger Zugang zum Konto. Ein leeres Passwortfeld allein löscht nichts; das wäre zu leicht aus Versehen passiert. Was im selben Vorgang eingetippt wurde, wird verworfen.",
"EINST.L_ZUGANG_LOESCHEN": "Gespeicherte Zugangsdaten löschen",
"EINST.ZUGANG_GELOESCHT": "E-Mail, Passwort, S-PIN und die Anmeldemarken wurden gelöscht. Der Dienst kann sich nicht mehr anmelden, bis neue Zugangsdaten eingetragen sind.",
# ---- Reiterpruefung (nachgezogen 20.08.2026) --------------------------------
"TEST.F_REITER": "Stimmen Reiterliste, Beschriftungen und Fl&auml;chen &uuml;berein?",
"TEST.A_REITER_UNKLAR": "die Liste oder die Fl&auml;chen liessen sich nicht auslesen &mdash; der Vergleich wurde nicht gemacht. Das ist kein Haken: eine Pr&uuml;fung, die nichts messen konnte, sagt es.",
"TEST.A_REITER_OK": "ja, alle %d Namen stehen in der Liste, in den Beschriftungen und als Fl&auml;che. Die Leiste entsteht in einer Schleife aus derselben Liste und kann deshalb nicht abweichen.",
"TEST.A_REITER_FEHL": "nein. %s",
"TEST.A_REITER_OHNE_BEREICH": "In der Liste, aber ohne Fl&auml;che: <b>%s</b>. Der Reiter erscheint in der Leiste, l&auml;sst sich anklicken und bleibt leer.",
"TEST.A_REITER_OHNE_LISTE": "Als Fl&auml;che vorhanden, aber nicht in der Liste: <b>%s</b>. Der Reiter fehlt in der Leiste, und das Muster weist ihn ab &mdash; er ist unerreichbar, und nach jedem Absenden springt die Seite auf Einstellungen zur&uuml;ck.",
"TEST.A_REITER_OHNE_TEXT": "In der Liste, aber ohne Beschriftung: <b>%s</b>. Die Leiste greift dann auf einen Schl&uuml;ssel zu, den es nicht gibt.",
"TEST.A_REITER_LEISTE_FEST": "Fest in der Leiste, aber nicht in der Liste: <b>%s</b>. Wer die Schleife aufl&ouml;st, muss die Namen wieder von Hand gleich halten.",
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
"ALLG.FAHRZEUGE": "Vehicles",
"ALLG.FAHRZEUG": "Vehicle",
"ALLG.LIB_FEHLT": "library missing",
"ALLG.GATEWAY": "LoxBerry gateway",
"ALLG.EIN": "on",
"ALLG.AUS": "off",
"ALLG.JA": "yes",
"ALLG.NEIN": "no",
"ALLG.SOC": "State of charge",
"ALLG.KM": "Odometer",
"ALLG.REICHWEITE": "Range",
"ALLG.VERRIEGELT": "locked",
"ALLG.OHNE_NAMEN": "no model name",
"ALLG.LETZTE_STOERUNG": "Last fault:",
"ALLG.AUSFAELLE": "Endpoints this vehicle did not answer:",
"ALLG.VERLAUF_HINWEIS": "State of charge or fuel level for today. One reading every four minutes at most.",
"ALLG.EIGENSCHAFT": "Property",
"ALLG.WERT": "Value",
"ALLG.SEKUNDEN": "seconds",
"ALLG.SPEICHERN": "Save",

"EINST.H_DIENST": "Polling service",
"EINST.DIENST_ERKLAERUNG": "The service fetches values from the Volkswagen cloud at the configured interval and stores them. The user interface and the Miniserver only read what has been stored &mdash; they never talk to the provider themselves.",
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

"EINST.H_KONTO": "Volkswagen account access",
"EINST.KONTO_ERKLAERUNG": "These are the credentials of your <b>Volkswagen account</b> &mdash; the same ones you use in the <i>Volkswagen</i> or <i>We Connect ID</i> app. Not those of a dealer portal. They are stored in a separate file with mode 0600, not in the configuration this page displays. <b>Two notes:</b> the connector works with <b>European</b> vehicles &mdash; there is a separate one for North America which is not included here. And some accounts ask for two-factor confirmation, which cannot be automated; if that affects you, sign in once in a browser on this machine.",
"EINST.L_EMAIL": "Username (e-mail address)",
"EINST.H_EMAIL": "The e-mail address the Volkswagen account was created with.",
"EINST.L_PASSWORT": "Password",
"EINST.H_PASSWORT": "Leaving the field empty keeps the stored password. It is never displayed &mdash; the Test tab only shows its length.",
"EINST.PW_GESETZT": "stored (%d characters) – leave empty to keep it",
"EINST.PW_LEER": "no password stored yet",
"EINST.L_SPIN": "S-PIN (four digits, optional)",
"EINST.H_SPIN": "The four-digit S-PIN from the Volkswagen app. This plugin offers <b>no</b> locking, unlocking or horn and therefore does not need it; the field is prepared for a later version. Leave it empty if you do not need it.",
"EINST.SPIN_GESETZT": "stored – leave empty to keep it",
"EINST.SPIN_LEER": "no S-PIN stored",

"EINST.H_TAKT": "Polling interval",
"EINST.TAKT_WARNUNG": "<b>Lower limit 180 seconds.</b> The Volkswagen connector refuses anything below that &mdash; it raises an error on creation. And above it the same applies: Volkswagen rejects frequent requests with HTTP 429, and a car that is woken constantly draws standby current. Five minutes is a good start. If you need a value right now, use the poll command, not a shorter interval.",
"EINST.L_INTERVALL": "Interval in seconds",
"EINST.H_INTERVALL": "Time between two polls. Allowed: 180 to 3600 seconds &mdash; 180 is the library's lower limit, not a precaution added by this plugin.",
"EINST.L_TAKT_WARTUNG": "Service data every … cycles",
"EINST.H_TAKT_WARTUNG": "Inspection and oil service change in days, not minutes. With a 300 second interval, 12 means once per hour.",
"EINST.L_VERLAUF_TAGE": "Keep history (days)",
"EINST.H_VERLAUF_TAGE": "How long the readings for the small daily chart are kept.",

"EINST.H_STEUERUNG": "Write commands",
"EINST.STEUERUNG_ERKLAERUNG": "<b>Disabled by default.</b> Write commands act on a car parked somewhere else &mdash; an air conditioning run started by accident drains the battery, and a stopped charge is only noticed the next morning. Enable this only once the read values in the Test tab look right. <b>This plugin does not offer locking or unlocking.</b>",
"EINST.L_STEUERUNG_EIN": "Allow write commands",
"EINST.L_TEMP_MIN": "Lowest allowed target temperature (degrees Celsius)",
"EINST.L_TEMP_MAX": "Highest allowed target temperature (degrees Celsius)",
"EINST.H_TEMP": "Limits for the air conditioning. A value outside them is <b>rejected</b>, not clamped: a silently altered setpoint leads to a car doing something other than what is displayed.",
"EINST.L_WARTEZEIT": "Wait for the answer (seconds)",
"EINST.H_WARTEZEIT": "How long the interface waits for the service to answer a command. After that it reports <span class='sm-mono'>OK=2</span> &mdash; queued, outcome unknown. No success is reported that nobody has verified.",

"EINST.L_MQTT_EIN": "Publish values via MQTT",
"EINST.L_MQTT_TOPIC": "Topic prefix",
"EINST.H_MQTT_TOPIC": "Letters, digits, hyphen, underscore and slash are allowed. All topics derive from this prefix, see the MQTT tab.",

"EINST.GESPEICHERT": "The settings were saved.",
"EINST.FEHLER_ZAHL": "%s: please enter a whole number.",
"EINST.FEHLER_BEREICH": "%s: the value must be between %d and %d.",
"EINST.FEHLER_TEMP_TAUSCH": "The lowest target temperature is higher than the highest. Please swap the two values.",
"EINST.FEHLER_TOPIC": "The topic prefix contains characters that are not allowed. Use letters, digits, hyphen, underscore and slash.",
"EINST.FEHLER_EMAIL": "The username does not look like an e-mail address.",
"EINST.FEHLER_SPIN": "The S-PIN consists of exactly four digits. The value entered does not match that pattern and was not saved.",
"EINST.FEHLER_ZUGANG_SPEICHERN": "The credentials file could not be written. Check the permissions of the configuration folder.",
"EINST.FEHLER_SPEICHERN": "The configuration could not be written: %s",
"EINST.WARN_PW_OHNE_KONTO": "A password is stored but no username. Every login will fail without showing why.",

"EINST.H_ERKANNT": "Detected vehicles",
"EINST.KEINE_FAHRZEUGE": "No vehicle detected yet. That is normal until the first successful poll: enter the credentials, save, start the service and wait one interval. If the list is still empty afterwards, the reason is in the Test tab and in the log file.",
"EINST.T_NR": "No.",
"EINST.T_MODELL": "Model",
"EINST.T_KENNZEICHEN": "Licence plate",
"EINST.T_VIN": "VIN",
"EINST.T_ANTRIEB": "Drivetrain",
"EINST.T_BATTERIE": "Battery",
"EINST.T_SOFTWARE": "Software version",
"EINST.VIN_HINWEIS": "Every address also accepts the VIN instead of the number &mdash; <span class='sm-mono'>fahrzeug=WVW…</span>. That is more robust if a second vehicle is added to the account later and the order shifts.",

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
"MQTT.THEMEN_ERKLAERUNG": "A topic this vehicle does not answer is not sent at all &mdash; so no topic is created carrying an invented zero.",
"MQTT.T_THEMA": "Topic",
"MQTT.T_BEDEUTUNG": "Meaning",
"MQTT.PLATZHALTER": "<b>N</b> is the vehicle number, so 1 for the first one.",

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
"LOX.MEHRERE_FAHRZEUGE": "Several vehicles in the account — one virtual input per vehicle:",
"LOX.K_VORLAGE": "Download template for Loxone Config",
"LOX.T_ADRESSE": "Address",
"LOX.T_ZYKLUS": "Polling cycle",
"LOX.T_TITEL": "Name",
"LOX.T_BEFEHL": "Command recognition",
"LOX.T_EINHEIT": "Unit",
"LOX.T_BEDEUTUNG": "Meaning",

"LOX.S4_TITEL": "Step 4: further inputs for charging, servicing and location",
"LOX.S4_TEXT": "Three more virtual HTTP inputs, each built like step 3. The charging input stays empty on a pure combustion car &mdash; you will see dashes there, and that is correct.",
"LOX.S4_WARTUNG": "<b>Servicing</b> &mdash; a separate input using the action <span class='sm-mono'>wartung</span>. A cycle of 3600 seconds is plenty; these values change in days.",
"LOX.S4_POSITION": "<b>Location</b> &mdash; a separate input using the action <span class='sm-mono'>position</span>. The postal address is on a second line and is not meant for Loxone; the first line deliberately contains numbers only.",

"LOX.S5_TITEL": "Step 5: sending commands (virtual output)",
"LOX.S5_TEXT": "Only needed if Loxone should trigger something. In Loxone Config create a <i>virtual output</i> with the address below and one <i>virtual output command</i> per command. In the command text <span class='sm-mono'>&lt;v&gt;</span> stands for the value passed.",
"LOX.T_VA_ADRESSE": "Address of the virtual output",
"LOX.T_VA_KLIMA_EIN": "Air conditioning on (21 degrees)",
"LOX.T_VA_KLIMA_AUS": "Air conditioning off",
"LOX.T_VA_LADEN_EIN": "Start charging",
"LOX.T_VA_LADEN_AUS": "Stop charging",
"LOX.T_VA_LADEGRENZE": "Set charge limit",
"LOX.T_VA_SCHEIBE": "Window heating on",
"LOX.T_VA_ABRUF": "Trigger an immediate poll",
"LOX.S5_WARNUNG": "Two things to know beforehand. <b>First:</b> write commands are disabled by default and must be enabled in the Settings tab. <b>Second:</b> an answer of <span class='sm-mono'>OK=1</span> means the Volkswagen server accepted the request with HTTP 200. Whether the car carries it out only shows on the next poll &mdash; if you need certainty, evaluate the state read back, not the answer to the command.",

"LOX.S6_TITEL": "Step 6: the token",
"LOX.T_TOKEN": "Token of this plugin",
"LOX.S6_TEXT": "The endpoint sits in the unauthenticated area so Loxone can reach it without credentials. It is protected by this token. The token is part of every address you enter in the Miniserver &mdash; <b>a new token invalidates all of them at once</b> and has to be updated everywhere. So only roll a new one if it has actually leaked.",

"LOX.S7_TITEL": "Step 7: failure detection",
"LOX.S7_TEXT": "If the cloud goes silent, the virtual inputs keep their last value. Everything looks normal in the app although nothing has arrived for hours. That is why the value <span class='sm-mono'>ALTER</span> is carried along: it states the age of the snapshot in seconds. Set the threshold <b>well above the polling interval</b> &mdash; with a 300 second interval, 900 seconds works well, so a single missed cycle does not raise an alarm.",

"LOX.S8_TITEL": "Step 8: complete block list for rebuilding one to one",
"LOX.S8_TEXT": "One block per row. Loxone Config lists them all in the block search (key F5). Rows 1 to 12 are the virtual inputs from steps 3 and 4 &mdash; if you loaded the template, they are already in the tree.",
"LOX.S8_ERLAEUTERUNG": "<p><b>On #13 to #16:</b> the 'vehicle open or lights on' message goes through an OR and an on-delay. Both are deliberate. The notification block only fires on a change from off to on; if several sources are wired straight to its input, one permanently active source swallows all the others. The five minute delay prevents a message while you are still loading the boot.</p><p><b>On #17 and #18:</b> two separate threshold switches, because a car supplies either a state of charge or a fuel level &mdash; a hybrid supplies both. The value not supplied stays a dash; the corresponding switch then keeps its last state and does not fire.</p><p><b>On #21 and #22:</b> the notification block only fires on a change from off to on &mdash; which is exactly why it fits here: you get a message when the cable is plugged in, not continuously while it stays plugged in. If you prefer the opposite message ('cable unplugged'), put a NOT in front.</p><p><b>On #23:</b> the inspection message needs the input from the servicing request (step 4), not the one from the status request.</p><p><b>On #25:</b> the failure detection threshold is deliberately set to three times the polling interval. Set it tighter and every single missed cycle raises an alarm.</p><p><b>On #28 to #33:</b> preheating is optional. The weekly timer defines the intended departure time, the AND with presence prevents heating while you are away, and the pulse generator makes sure the command fires once rather than being sent on every cycle. <b>Loxone time base:</b> seconds since 1 January 2009. If a time block supplies Unix time (values around 1.23 billion), subtract 1230768000.</p><p><b>On #34:</b> optional but useful: a command that switches the air conditioning off again by hand. Without it, it runs until its own timeout.</p><p><b>On #14 &mdash; why four sources hang on two inputs there:</b> for AND and OR the number of inputs is a property of the block that Loxone Config sets itself. Add a third input and the next time Config opens the file it removes that input again without a word &mdash; deleting every connection that hung on it. What is allowed is hanging several sources on <i>one</i> input; they are OR-combined. On an OR that gives the same result with two inputs. <b>On an AND it would be wrong</b>: there, several sources on one input are OR-combined as well, which turns the AND into an OR without anything reporting it. That is why #30 carries exactly one source per input.</p>",

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
"BAUSTEIN.T_NICHT": "NOT",
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
"BAUSTEIN.ANWESEND": "presence detector",
"BAUSTEIN.MANUELL": "by hand or from a scene",

"BAUSTEIN.N01": "VW_1_SOC",
"BAUSTEIN.P01": "unit %, from the status input",
"BAUSTEIN.N02": "VW_1_TANK",
"BAUSTEIN.P02": "unit %, from the status input",
"BAUSTEIN.N03": "VW_1_REICHW",
"BAUSTEIN.P03": "unit km, from the status input",
"BAUSTEIN.N04": "VW_1_KM",
"BAUSTEIN.P04": "unit km, from the status input",
"BAUSTEIN.N05": "VW_1_VERR",
"BAUSTEIN.P05": "1 = locked, 0 = open",
"BAUSTEIN.N06": "VW_1_TUEREN",
"BAUSTEIN.P06": "1 = at least one door open",
"BAUSTEIN.N07": "VW_1_FENSTER",
"BAUSTEIN.P07": "1 = at least one window open",
"BAUSTEIN.N08": "VW_1_LICHT",
"BAUSTEIN.P08": "1 = lights on",
"BAUSTEIN.N09": "VW_1_KLIMA",
"BAUSTEIN.P09": "1 = air conditioning running",
"BAUSTEIN.N10": "VW_1_KABEL",
"BAUSTEIN.P10": "1 = charging cable plugged in, from the charging input",
"BAUSTEIN.N11": "VW_1_ALTER",
"BAUSTEIN.P11": "unit s, age of the snapshot",
"BAUSTEIN.N12": "VW_1_INSPTAGE",
"BAUSTEIN.P12": "unit d, from the servicing input",
"BAUSTEIN.N13": "Vehicle not locked",
"BAUSTEIN.N14": "Vehicle open or lights on",
"BAUSTEIN.N15": "Delay for the open message",
"BAUSTEIN.P15": "on-delay 300 s",
"BAUSTEIN.N16": "Message: vehicle is open",
"BAUSTEIN.P16": "subject freely chosen, recipients in the user settings",
"BAUSTEIN.N17": "State of charge low",
"BAUSTEIN.P17": "on < 20, off > 25 (hysteresis, otherwise it chatters)",
"BAUSTEIN.N18": "Fuel level low",
"BAUSTEIN.P18": "on < 15, off > 20",
"BAUSTEIN.N19": "Range low",
"BAUSTEIN.N20": "Message: range low",
"BAUSTEIN.P20": "subject freely chosen",
"BAUSTEIN.N21": "Charging cable plugged in",
"BAUSTEIN.P21": "on > 0.5, off < 0.5",
"BAUSTEIN.N22": "Message: charging cable plugged in",
"BAUSTEIN.P22": "subject freely chosen",
"BAUSTEIN.N23": "Inspection due",
"BAUSTEIN.P23": "on < 14, off > 21 (days)",
"BAUSTEIN.N24": "Message: inspection due",
"BAUSTEIN.P24": "subject freely chosen",
"BAUSTEIN.N25": "Poll has failed",
"BAUSTEIN.P25": "on > 900, off < 600 (at a 300 s interval)",
"BAUSTEIN.N26": "Message: no more data from the vehicle",
"BAUSTEIN.P26": "subject freely chosen",
"BAUSTEIN.N27": "Vehicle overview",
"BAUSTEIN.P27": "status block for the app tile",
"BAUSTEIN.N28": "Departure time",
"BAUSTEIN.P28": "weekly timer, switching on 30 minutes before departure",
"BAUSTEIN.N29": "Air conditioning now",
"BAUSTEIN.P29": "push-button as a pulse",
"BAUSTEIN.N30": "Preheat only when present",
"BAUSTEIN.P30": "prevents preheating while you are away",
"BAUSTEIN.N31": "Request air conditioning",
"BAUSTEIN.N32": "Fire once",
"BAUSTEIN.P32": "pulse generator, so the command is not repeated every cycle",
"BAUSTEIN.N33": "Volkswagen air conditioning on",
"BAUSTEIN.P33": "command on ON, address from step 5",
"BAUSTEIN.N34": "Volkswagen air conditioning off",
"BAUSTEIN.P34": "optional, command on ON",

"TEST.H_SELBSTPRUEFUNG": "Self-check",
"TEST.EINLEITUNG": "This check answers <b>without Loxone</b> whether the setup holds. Each row is a question; a cross means something is missing. What could only be checked with a car present is listed as unverified below.",
"TEST.T_FRAGE": "Question",
"TEST.T_BEFUND": "Finding",
"TEST.F_VENV": "Is the Python virtual environment present?",
"TEST.A_VENV_FEHLT": "no — reinstall the plugin",
"TEST.F_PYTHON": "Is Python new enough (3.9 or newer)?",
"TEST.A_PYTHON_ZU_ALT": "too old for carconnectivity",
"TEST.A_PYTHON_UNBEKANNT": "cannot be determined — the virtual environment is missing",
"TEST.F_LIB": "Is the library core loaded, and in which version?",
"TEST.A_LIB_FEHLT": "no — see the installation output",
"TEST.F_DIENST": "Is the polling service running?",
"TEST.A_DIENST_LAEUFT": "yes, PID",
"TEST.A_DIENST_SOLL_TOT": "no — it should be running but is not. Check the log file.",
"TEST.A_DIENST_GESTOPPT": "no — deliberately stopped",
"TEST.F_KONTO": "Is a username stored?",
"TEST.A_KONTO_FEHLT": "no",
"TEST.F_PASSWORT": "Is a password stored?",
"TEST.A_PASSWORT_DA": "yes, %d characters (the content is never displayed)",
"TEST.A_PASSWORT_FEHLT": "no",
"TEST.F_RECHTE": "Is the credentials file protected from other users?",
"TEST.A_ZUGANGSDATEI_FEHLT": "the file is missing",
"TEST.F_FAHRZEUGE": "Have vehicles been detected?",
"TEST.A_FAHRZEUGE": "yes, %d",
"TEST.A_KEINE_FAHRZEUGE": "no — normal until the first successful poll",
"TEST.F_AUSFAELLE": "Does the vehicle answer every request?",
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
"TEST.KEINE_MESSPUNKTE": "no readings for today yet",

"TEST.H_LESEN": "View",
"TEST.K_STATUS": "Fetch status",
"TEST.K_LADEN": "Fetch charging values",
"TEST.K_WARTUNG": "Fetch servicing values",
"TEST.K_FAHRZEUGE": "List vehicles",
"TEST.H_TECHNIK": "Technical information",
"TEST.K_SELBSTTEST": "Self-test of the service",
"TEST.K_ROH": "View raw data as JSON",
"TEST.H_SCHALTEN": "Switching",
"TEST.SCHALTEN_WARNUNG": "<b>These buttons act immediately and on the real car.</b> Air conditioning drains the battery, a stopped charge is only noticed the next morning, and a wake-up call pulls the car out of sleep, which costs power.",
"TEST.SCHALTEN_GESPERRT": "Write commands are currently disabled. The buttons will therefore return a rejection &mdash; that is not an error. Enable them in the Settings tab.",
"TEST.L_FAHRZEUG": "Vehicle (running number)",
"TEST.L_TEMP": "Target temperature in degrees Celsius",
"TEST.H_TEMP": "Half degrees are allowed, e.g. <span class='sm-mono'>21.5</span>. Values outside the configured limits are rejected, not clamped.",
"TEST.L_PROZENT": "Charge limit in percent",
"TEST.H_PROZENT": "Allowed: 10 to 100. Volkswagen rounds to the steps the car supports &mdash; usually multiples of ten.",
"TEST.K_ABRUF": "Poll now",
"TEST.K_KLIMA_EIN": "Air conditioning on",
"TEST.K_KLIMA_AUS": "Air conditioning off",
"TEST.K_LADEN_EIN": "Start charging",
"TEST.K_LADEN_AUS": "Stop charging",
"TEST.K_LADEGRENZE": "Set charge limit",
"TEST.K_SCHEIBE_EIN": "Window heating on",
"TEST.K_SCHEIBE_AUS": "Window heating off",
"TEST.K_WECKEN": "Wake the vehicle",
"TEST.M_FAHRZEUG_UNGUELTIG": "The vehicle number is not a number between 1 and 99.",
"TEST.M_TEMP_UNGUELTIG": "The target temperature must be a number, half degrees allowed (e.g. 21 or 21.5).",
"TEST.M_PROZENT_UNGUELTIG": "The charge limit must be a whole number.",
"TEST.M_UNBEKANNT": "Unknown test action.",
"TEST.H_UNGEPRUEFT": "What is unverified in this version",
"TEST.UNGEPRUEFT": "This plugin was built <b>without a Volkswagen account and without a car</b>. Unverified is therefore: whether signing in succeeds, whether this vehicle supplies the requested values, and whether the write commands have the expected effect. Everything else has been verified &mdash; and not against mock objects: the value mapping and the write commands were measured against <b>real library objects</b>. That is why this version is numbered 0.9.0 and not 1.0.0. If something stays empty, the button <i>View raw data as JSON</i> helps: it shows what the service actually received.",

"LOG.H_TITEL": "Log files",
"LOG.ERKLAERUNG": "The polling service writes to this one file only. Below are the last 400 lines, newest first.",
"LOG.LEER": "The log file is empty or has not been created yet.",
"LOG.K_LEEREN": "Clear log file",
"LOG.GELEERT": "Log file cleared",

"VW_FELD.SOC": "State of charge of the traction battery",
"VW_FELD.TANK": "Fuel level",
"VW_FELD.REICHW": "Total range",
"VW_FELD.KM": "Odometer",
"VW_FELD.VERR": "1 = locked, 0 = not locked",
"VW_FELD.TUEREN": "1 = at least one door open",
"VW_FELD.FENSTER": "1 = at least one window open",
"VW_FELD.LICHT": "1 = lights on",
"VW_FELD.KLIMA": "1 = air conditioning running (including ventilation and auxiliary heating)",
"VW_FELD.ZIELTEMP": "Configured target temperature of the air conditioning",
"VW_FELD.AUSSEN": "Outside temperature as measured by the car",
"VW_FELD.ERREICH": "1 = the car is reachable for the cloud",
"VW_FELD.ALTER": "Age of the snapshot — for failure detection",
"VW_FELD.OK": "1 = the last poll succeeded",

"VW_LFELD.SOC": "State of charge of the traction battery",
"VW_LFELD.LAEDT": "1 = charging right now",
"VW_LFELD.LADEKW": "Current charging power",
"VW_LFELD.TEMPO": "Range gained per hour",
"VW_LFELD.LADEGR": "Configured charge limit",
"VW_LFELD.KABEL": "1 = charging cable plugged in",
"VW_LFELD.REICHWBAT": "Range from the battery alone",
"VW_LFELD.OK": "1 = the last poll succeeded",

"VW_WFELD.INSPTAGE": "Days until the next inspection",
"VW_WFELD.INSPKM": "Kilometres until the next inspection",
"VW_WFELD.OELTAGE": "Days until the next oil service",
"VW_WFELD.OELKM": "Kilometres until the next oil service",
"VW_WFELD.KM": "Odometer",
"VW_WFELD.OK": "1 = the last poll succeeded",

"VW_MQTT.OK": "1 = the last poll succeeded",
"VW_MQTT.FAHRZEUGE": "Number of vehicles in the account",
"VW_MQTT.SOC": "State of charge of the traction battery in percent",
"VW_MQTT.REICHWEITE": "Total range in km",
"VW_MQTT.TANK": "Fuel level in percent",
"VW_MQTT.KM": "Odometer",
"VW_MQTT.VERRIEGELT": "1 = locked",
"VW_MQTT.TUEREN": "1 = at least one door open",
"VW_MQTT.FENSTER": "1 = at least one window open",
"VW_MQTT.LICHT": "1 = lights on",
"VW_MQTT.KLIMA": "1 = air conditioning running",
"VW_MQTT.ZIELTEMP": "Target temperature in degrees Celsius",
"VW_MQTT.AUSSEN": "Outside temperature in degrees Celsius",
"VW_MQTT.LAEDT": "1 = charging right now",
"VW_MQTT.LADEKW": "Charging power in kW",
"VW_MQTT.LADEGRENZE": "Configured charge limit in percent",
"VW_MQTT.KABEL": "1 = charging cable plugged in",
"VW_MQTT.BREITE": "Latitude of the location",
"VW_MQTT.LAENGE": "Longitude of the location",
"VW_MQTT.INSP_TAGE": "Days until the inspection",
"VW_MQTT.INSP_KM": "Kilometres until the inspection",
"VW_MQTT.OEL_TAGE": "Days until the oil service",
"VW_MQTT.OEL_KM": "Kilometres until the oil service",
"VW_MQTT.ERREICHBAR": "1 = reachable for the cloud",
"EINST.H_ZUGRIFF_ERZWINGEN": "Some cars do not announce the <span class='sm-mono'>ACCESS</span> capability although they do report locking and door status. The connector offers a switch for this. Only enable it if those fields stay empty otherwise &mdash; else the plugin asks for something that does not exist.",
"EINST.L_ZUGRIFF_ERZWINGEN": "Force door status (only if doors and locking stay empty)",
"EINST.SITZUNG_ERKLAERUNG": "After the first login the library stores authentication tokens in a separate file with mode 0600 and uses them instead of sending the password every time. This spares the Volkswagen login page, which throttles repeated sign-ins. After a password change the tokens are worthless &mdash; then use the <i>Force a new login</i> button above.",
"LOX.T_VA_LADESTROM": "Set charging current (amperes)",
"TEST.A_CONNECTOR_FEHLT": "no — see the installation output",
"TEST.A_MARKE_FEHLT": "not created yet — appears on the first poll",
"TEST.F_CONNECTOR": "Is the Volkswagen connector loaded?",
"TEST.F_MARKE": "Are the authentication tokens protected from other users?",
"TEST.H_AMPERE": "Which steps your car supports depends on the model: some handle the current in amperes (5, 10, 13, 32), the rest only know reduced (6) and maximum (16). Volkswagen rejects an unknown step &mdash; the rejection then appears in the message.",
"TEST.K_LADESTROM": "Set charging current",
"TEST.L_AMPERE": "Charging current",
"TEST.M_AMPERE_UNGUELTIG": "The charging current must be a whole number.",
"VW_FELD.HANDBR": "1 = parking brake engaged",
"VW_FELD.SCHEIBE": "1 = window heating on",
"VW_FELD.ZUSTAND": "0 = offline, 1 = parked, 2 = ignition on, 3 = driving",
"VW_LFELD.FERTIGMIN": "Minutes until charging is expected to finish",
"VW_LFELD.LADESTROM": "Configured maximum charging current",
"VW_LFELD.STECKER": "1 = plug locked in the vehicle",
"VW_MQTT.FERTIG": "Expected end of charging as Unix time",
"VW_MQTT.HANDBREMSE": "1 = parking brake engaged",
"VW_MQTT.LADESTROM": "Configured maximum charging current in amperes",
"VW_MQTT.SCHEIBE": "1 = window heating on",
"VW_MQTT.STECKER": "1 = plug locked in the vehicle",
"VW_MQTT.TEMPO": "Range gained per hour in km/h",
"VW_MQTT.ZUSTAND": "0 = offline, 1 = parked, 2 = ignition on, 3 = driving",

# Aus der ausgelieferten ini nachgetragen (20.08.2026): der Erzeuger
# kannte sie nicht, das Sprachpaket schon. Ohne den Nachtrag haette ein
# Lauf des Erzeugers diese Texte geloescht.
"EINST.FEHLER_ZUGANG_LOESCHEN": "The credentials could not be deleted. Please check the file permissions.",
"EINST.H_ZUGANG_LOESCHEN": "Removes e-mail, password and S-PIN completely — including the backup copy and the stored login tokens (<span class='sm-mono'>token.json</span>), which grant access to the account even without the password. An empty password field on its own deletes nothing; that would happen by accident far too easily. Anything typed in the same step is discarded.",
"EINST.L_ZUGANG_LOESCHEN": "Delete stored credentials",
"EINST.ZUGANG_GELOESCHT": "E-mail, password, S-PIN and the login tokens have been deleted. The service can no longer sign in until new credentials are entered.",
# ---- Tab check (added 20.08.2026) -------------------------------------------
"TEST.F_REITER": "Do the tab list, the labels and the panes agree?",
"TEST.A_REITER_UNKLAR": "the list or the panes could not be read &mdash; the comparison was not made. That is not a tick: a check that could measure nothing says so.",
"TEST.A_REITER_OK": "yes, all %d names appear in the list, in the labels and as a pane. The bar is built in a loop from that same list and therefore cannot diverge.",
"TEST.A_REITER_FEHL": "no. %s",
"TEST.A_REITER_OHNE_BEREICH": "In the list but without a pane: <b>%s</b>. The tab appears in the bar, can be clicked and stays empty.",
"TEST.A_REITER_OHNE_LISTE": "Present as a pane but not in the list: <b>%s</b>. The tab is missing from the bar and the pattern rejects it &mdash; it is unreachable, and after every submit the page jumps back to Settings.",
"TEST.A_REITER_OHNE_TEXT": "In the list but without a label: <b>%s</b>. The bar then reads a key that does not exist.",
"TEST.A_REITER_LEISTE_FEST": "Hard-coded in the bar but not in the list: <b>%s</b>. Whoever unrolls the loop has to keep the names equal by hand again.",
}

KOPF_DE = """; Volkswagen ID - Deutsch
;
; ERZEUGT von Werkzeuge/vw_sprache_erzeugen.py - nicht von Hand aendern,
; sonst geht die Aenderung beim naechsten Lauf verloren.
;
; Jeder Wert steht in doppelten Anfuehrungszeichen: bei parse_ini_file beginnt
; mit ';' ein Kommentar, und jede HTML-Entitaet endet auf ein Semikolon.
; Innerhalb eines Wertes darf kein doppeltes Anfuehrungszeichen stehen -
; HTML-Attribute deshalb einfach quoten: <span class='sm-mono'>.
;
; Schluessel, die im PHP durch vw_e() laufen, enthalten KEINE Auszeichnung und
; KEINE Entitaeten: sie wuerden dort ein zweites Mal maskiert und als
; "pr&amp;uuml;fen" auf dem Bildschirm landen.
"""

KOPF_EN = """; Volkswagen ID - English
;
; GENERATED by Werkzeuge/vw_sprache_erzeugen.py - do not edit by hand.
;
; English is the fallback level: keys missing in another language are taken
; from here, so this file must always be complete.
; Quote every value - see the German file for the reason.
"""


def php_dateien(wurzel: Path):
    return sorted(wurzel.rglob("*.php"))


def maskierte_schluessel(wurzel: Path) -> set:
    """Welche Schluessel laufen im PHP durch vw_e()?"""
    treffer = set()
    for f in php_dateien(wurzel):
        t = f.read_text(encoding="utf-8")
        for m in re.finditer(r"vw_e\(\s*vw_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t):
            treffer.add(m.group(1))
        # sprintf(vw_t('X'), ...) innerhalb von vw_e(): der Text selbst wird
        # dann ebenfalls maskiert.
        for m in re.finditer(r"vw_e\(\s*sprintf\(\s*vw_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t):
            treffer.add(m.group(1))
    return treffer


# Namen, die im Quelltext wie ein Schluessel aussehen, aber keiner sind.
# Jeder Eintrag nennt die Stelle - eine namenlose Ausnahmeliste waechst,
# bis sie den Zweck der Pruefung aufhebt.
KEINE_SCHLUESSEL = {
    "ABSCHNITT.SCHLUESSEL",   # Beispiel im Kommentar der Textfunktion
}


def benutzte_schluessel(wurzel: Path) -> set:
    """Alle im PHP vorkommenden Schluessel, direkt oder als Zeichenkette."""
    treffer = set()
    for f in php_dateien(wurzel):
        t = f.read_text(encoding="utf-8")
        for m in re.finditer(r"vw_t\('([A-Z0-9_]+\.[A-Z0-9_]+)'\)", t):
            treffer.add(m.group(1))
        # Schluessel, die nur als Zeichenkette in einer Tabelle stehen
        # und erst spaeter durch die Textfunktion laufen. Bewusst OHNE
        # Einschraenkung auf bestimmte Abschnitte: die frueher hier
        # stehende Liste (VW_ und BAUSTEIN) hat die vier
        # REITER-Schluessel als "nie benutzt" gemeldet, weil sie in
        # einer Zuordnungstabelle stehen. Ein Name, der auf "_" endet,
        # ist der Vorsatz eines zusammengesetzten Schluessels und
        # zaehlt nicht mit.
        for m in re.finditer(r"'([A-Z][A-Z0-9_]*\.[A-Z0-9_]*[A-Z0-9])'", t):
            if m.group(1) not in KEINE_SCHLUESSEL:
                treffer.add(m.group(1))
    # Schluessel, die zur Laufzeit zusammengesetzt werden
    treffer |= {"EINST.DIENST_START", "EINST.DIENST_STOP", "EINST.DIENST_RESTART"}
    for feld in ("INTERVALL", "TAKT_WARTUNG", "TEMP_MIN", "TEMP_MAX",
                 "VERLAUF_TAGE", "WARTEZEIT"):
        treffer.add("EINST.L_" + feld)
    return treffer


def ini_schreiben(pfad: Path, kopf: str, texte: dict) -> None:
    abschnitte = {}
    for k, v in texte.items():
        a, s = k.split(".", 1)
        abschnitte.setdefault(a, {})[s] = v
    reihenfolge = ["REITER", "LEGENDE", "ALLG", "EINST", "MQTT", "LOX", "BAUSTEIN",
                   "TEST", "LOG", "VW_FELD", "VW_LFELD", "VW_WFELD", "VW_MQTT"]
    zeilen = [kopf]
    for a in reihenfolge + [x for x in sorted(abschnitte) if x not in reihenfolge]:
        if a not in abschnitte:
            continue
        zeilen.append("\n[" + a + "]")
        for s in sorted(abschnitte[a]):
            zeilen.append('%s = "%s"' % (s, abschnitte[a][s]))
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
                fehler.append("%s %s laeuft durch vw_e(), enthaelt aber Auszeichnung "
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
