#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Erzeugt language_de.ini und language_en.ini fuer das Robonect-Plugin.

EINE Quelle fuer beide Dateien. Zwei getrennt gepflegte Sprachdateien laufen
auseinander, und der Fehler faellt erst am Bildschirm auf.

Regeln, die hier eingebaut sind (REGELN_2, "Sprachdateien"):

  * Jeder Wert steht in doppelten Anfuehrungszeichen. Bei parse_ini_file
    beginnt mit ';' ein Kommentar - ein unquotierter Wert wird dort
    abgeschnitten, und JEDE HTML-Entitaet endet auf ein Semikolon.
  * Innerhalb eines Wertes darf KEIN doppeltes Anfuehrungszeichen stehen.
    HTML-Attribute deshalb einfach quoten: <span class='sm-mono'>.
  * Werte, die durch mw_e() laufen, tragen ECHTE UTF-8-Zeichen und KEINE
    Entitaeten - sonst steht im Browser woertlich 'l&auml;uft'.
  * Ein Wert, der durch sprintf geht, schreibt ein literales Prozentzeichen
    als '%%'.

STAND (Werkzeug-S1, 02.10.2026): nachgezogen auf Robonect 1.1.15 (mit den
Schluesseln der Ausgabeart Google-Lautsprecher) - erzeugt language_de.ini und
language_en.ini des Archivs LoxBerry-Plugin-Robonect-1.1.15.zip byteweise
gleich (107 Schluessel neu, 3 entfallen, 4 Werte neu gefasst). Die help_*.ini
schreibt dieser Erzeuger nicht.

STAND (vb_st2_ro, 08.10.2026, NACHGEZOGEN - Werkzeuge/ unveraendert): Robonect 1.1.18 mit der
Sprachausgabe Stufe 2 - Abschnitt [ANSAGE] der gemeinsamen Sprachausgabe am Ende der Datei, aus
Werkzeuge/gemeinsam_pruefen.ini_abschnitt() (EINE Quelle: Werkzeuge/gemeinsam/sprachausgabe_texte.json),
dazu PRUEF.ANSAGE und fuenf TEXT-Schluessel.

STAND (G4/X-8, 02.10.2026): nachgezogen auf den Bau vb_g4_rbn_bau (Robonect 1.1.16
mit der Baustein-Liste in der einheitlichen Form): neuer Abschnitt [BAUSTEIN]
(89 Schluessel) hinter [TEXT], 54 TEXT-Schluessel der alten Teiltabellen entfallen.
Erzeugt die language_*.ini dieses Baus byteweise gleich.

STAND (vb_x10_ro, 09.10.2026, Welle X-10 / Sprachmodul 1.1.2): Baustein-Liste [BAUSTEIN] in der
Grammatik von Werkzeuge/leitungen_setzen.py (19 VERB-Zellen: "Ausgang von {F:..} ({B2})", "V1 = ...",
"Ausgang von {Bn}"); TEXT.SICH_TTS_EINTRAG entfaellt (Satz K_TTS_EINTRAG kommt mit Modul 1.1.2).
[ANSAGE] wie immer aus Werkzeuge/gemeinsam/sprachausgabe_texte.json (157 Schluessel).

STAND (vb_bild_ro, 11.10.2026, Welle Bild 8 / Musterprojekt): [BAUSTEIN] ganz ersetzt durch die
Liste aus Musterprojekt/baustein_listen.txt, Abschnitt Robonect (19 Zeilen, eine Zeile = ein
Baustein); Hinweise H_AWV, H_ODER, H_PUSH, H_HEIM, H_SPERREN; TEXT und ERLAEUTERUNG neu gefasst.
[TEXT] +BILD_ALT, BILD_UNTERSCHRIFT, MUSTERPROJEKT (Bild unter der Liste).

STAND (vb_bild_ro, 12.10.2026, Welle Bild 10 VOLL / Musterprojekt): [BAUSTEIN] ganz ersetzt durch
zwei Listen aus Musterprojekt/baustein_listen.txt (Robonect 42 Zeilen B1..B42, Robonect Steuerung
34 Zeilen S1..S34), je Seite Ueberschrift, Kasten "So uebernehmen Sie diese Seite" und Hinweise.
[TEXT] SCHRITT_6_BAUSTEINE (Mehrzahl), BILD_ALT und BILD_UNTERSCHRIFT (je Seite, %s).

STAND (vb_bild_ro14, 16.10.2026, Welle Bild 14): BAUSTEIN.H_AWV um den Hinweis ergaenzt, dass
Config den Eingang En der Analogwertvalidierung negiert anlegt (Haken entfernen); "prueft nur mit
der Konstante 1 an En" ersetzt durch "bekommt an En die Konstante 1" (unbeschaltet steht En auf EIN).

STAND (vb_g2_rb, 19.10.2026, Gruppe 2 / MQTT, Robonect 1.1.24): [BAUSTEIN] ganz neu aus
Musterprojekt/baustein_listen.txt (Robonect 44, Robonect Steuerung 52 Zeilen; Typ "Virtueller Eingang (Name
wie das MQTT-Gateway ihn vergibt ...)", Befehle am Ausgang "LoxBerry MQTT-Gateway"; Platzhalter {Bn}/{Sn},
{L:..}, {N:thema} = Gateway-Name, {P} = Themenpraefix); [TEXT] Nachtrag fuer den Reiter "Einbindung in
Loxone" ueber MQTT (Namenstabelle, Hakenliste, Ausfallerkennung am Lebenszeichen status/zaehler, Befehle) und
den zugeklappten Weg ueber HTTP, die Alters-Formel aus TS ist entfallen; [PRUEF] NAMEN, V2_HAKEN, BRUECKE;
neuer Abschnitt [BEFEHL] der Befehlsbruecke (Werkzeuge/gemeinsam/befehlsbruecke.php).

STAND (Drift-Abgleich, 06.11.2026): angeglichen an Robonect 1.1.32, 1 Schluessel neu, 1 Wert
geaendert, 0 entfernt (TEXT.SICH_SPAET neu; TEXT.ANSAGE_SCHALTER "ab Werk an"/"on by default").

Aufruf:
    python3 Werkzeuge/mo_sprache_erzeugen.py <Plugin-Ordner>
"""

import os
import sys

# ---------------------------------------------------------------- Texte
# Aufbau: SCHLUESSEL -> (deutsch, englisch)
# Die Abschnitte entsprechen denen der .ini.

REITER = {
    "EINSTELLUNGEN": ("Einstellungen", "Settings"),
    "MQTT":          ("MQTT", "MQTT"),
    "LOXONE":        ("Einbindung in Loxone", "Loxone integration"),
    "TEST":          ("Test", "Test"),
    "LOG":           ("Logdateien", "Log files"),
}

LEGENDE = {
    "LESEN":   ("Ansehen — fragt nur ab, verändert nichts",
                "View — only queries, changes nothing"),
    "TECHNIK": ("Technische Auskunft — für die Fehlersuche",
                "Technical information — for troubleshooting"),
    "AKTION":  ("Löst etwas aus — sendet oder verändert",
                "Triggers something — sends or changes"),
}

# Die Beschriftungen der Pruefzeilen im Reiter Test.
PRUEF = {
    "CFG_HEIL":   ("Ist die Konfiguration heil?", "Is the configuration intact?"),
    "CFG_VOLL":   ("Ist die Konfiguration vollständig?", "Is the configuration complete?"),
    "MAEHER":     ("Antwortet jeder eingerichtete Mäher?", "Does every configured mower respond?"),
    "CRON":       ("Arbeitet der Cron-Lauf noch?", "Is the cron run still working?"),
    "TOKEN":      ("Ist das Aktionstoken eingerichtet?", "Is the action token set up?"),
    "ENDPUNKT":   ("Antwortet der eigene Endpunkt?", "Does our own endpoint respond?"),
    "GATEWAY":    ("Zustand des MQTT-Gateways", "State of the MQTT gateway"),
    "THEMEN":     ("Stimmt die Themenliste mit dem Sendecode überein?",
                   "Does the topic list match the sending code?"),
    "REITER":     ("Passen Reiterleiste, Bereiche und Positivliste zusammen?",
                   "Do tab bar, panes and allow list agree?"),
    "FORMULARE":  ("Tragen alle Formulare das Merkmal gegen fremde Absender?",
                   "Do all forms carry the anti-forgery marker?"),
    "DOWNLOAD":   ("Steht der Sicherungs-Download vor dem Seitenkopf?",
                   "Is the backup download placed before the page header?"),
    "VORLAGEN":   ("Sind die Loxone-Vorlagen wohlgeformt?", "Are the Loxone templates well-formed?"),

    # --- Nachgezogen 07.09.2026: stand bis dahin nur von Hand in der
    # .ini und waere beim naechsten Erzeugerlauf verschwunden.
    "RETAIN": ("Ist für jedes MQTT-Thema entschieden, ob es zurückbehalten "
               "wird?",
               "Is every MQTT topic decided on retain?"),
    "SIGNATUR": ("Merkt die Änderungssignatur jeden Wert, der über MQTT "
                 "hinausgeht?",
                 "Does the change signature notice every value that goes out "
                 "over MQTT?"),
    "SMACTIVE": ("Öffnet sich ein Reiter auch ohne JavaScript?",
                 "Does a tab open without JavaScript?"),
    # ---- Werkzeug-S1 (02.10.2026): nachgezogen auf Robonect 1.1.15 ----
    "ALEXA": ("Antwortet Alexa-NG, passt das Sprechtoken?", "Does Alexa-NG respond, is the speech token valid?"),
    "GOOGLE": ("Antwortet Chromecast 4 Lox NG, passt das Sprechtoken?", "Does Chromecast 4 Lox NG respond, is the speech token valid?"),
    "MQTT_EIN": ("Ist die MQTT-Veröffentlichung dieses Plugins eingeschaltet?", "Is MQTT publishing of this plugin switched on?"),
    # ---- vb_st2_ro (08.10.2026): Sprachausgabe Stufe 2 ----
    "ANSAGE": ("Ist die Sprachausgabe eingerichtet?", "Is speech output set up?"),
}

# ---------------------------------------------------------------- TEXT
# Alles, was aus 1.0.13 weiterlebt, steht hier unveraendert; die toten
# Schluessel sind entfallen, die neuen kommen dazu.
TEXT = {
    # ---- vb_st2_ro (08.10.2026): Sprachausgabe Stufe 2 ----
    "ANSAGE_SCHALTER": ("Angesagt wird nur, wenn oben unter „Meldungen“ der Haken „Audioausgabe aktiv“ gesetzt ist (ab Werk an). Adresse und Vorlage müssen im Heimnetz liegen.",
        "Announcements are only spoken when “Audio output active” is ticked under “Notifications” above (on by default). Address and template must be on the home network."),
    "PRUEF_ANSAGE_AUS": ("Ansagen sind aus (Haken „Audioausgabe aktiv“ unter Meldungen). Eingestellt:",
        "Announcements are off (tick “Audio output active” under Notifications). Set up:"),
    "SICH_TTS": ("Sprachausgabe: unzulässiger Wert – %s",
        "Speech output: invalid value – %s"),
    "TESTANSAGE_NICHTS": ("Keine Testansage: %s",
        "No test announcement: %s"),
    # --- Ueberschriften und Reiterinhalte
    "H_MAEHER":            ("Mäher (bis zu %d)", "Mowers (up to %d)"),
    "H_STATISTIK":         ("Einsatzstatistik", "Usage statistics"),
    "H_SICHERUNG":         ("Einstellungen sichern und zurückspielen",
                            "Back up and restore settings"),
    "H_ABO":               ("Das Abo im MQTT-Gateway", "The subscription in the MQTT gateway"),
    "H_THEMEN":            ("Alle veröffentlichten Themen", "All published topics"),
    "H_VORLAGE":           ("Alles auf einmal anlegen", "Create everything at once"),
    "H_TOKEN":             ("Aktionstoken", "Action token"),
    "H_SELBSTPRUEFUNG":    ("Selbstprüfung", "Self-check"),
    "H_ROHBEFEHL":         ("Rohe Antwort des Moduls", "Raw response from the module"),
    "H_FEHLERHISTORIE":    ("Zuletzt vermerkte Fehler", "Recently recorded faults"),
    "EINBINDUNG_IN_LOXONE_SCHRITT_FR_SC": ("Einbindung in Loxone — Schritt für Schritt",
                            "Loxone integration — step by step"),
    "STATUSCODES_IM_UUML_BERBLICK": ("Statuscodes im Überblick", "Status codes at a glance"),
    "MELDUNGEN":           ("Meldungen", "Notifications"),
    "SPRACHAUSGABE":       ("Sprachausgabe", "Speech output"),
    "MQTT_OPTIONAL":       ("MQTT (optional)", "MQTT (optional)"),

    # --- Schritte im Reiter Loxone
    "SCHRITT_1_VIRTUELLER_HTTP_EINGANG_": ("Schritt 1: Virtueller HTTP-Eingang „Rasenmäher“",
                            "Step 1: Virtual HTTP input “lawn mower”"),
    "SCHRITT_2_ABO":       ("Schritt 2: Das Abo im MQTT-Gateway",
                            "Step 2: The subscription in the MQTT gateway"),
    "SCHRITT_2_ABO_TEXT":  ("Nur nötig, wenn die Werte über MQTT laufen sollen. Über den "
                            "virtuellen HTTP-Eingang aus Schritt 1 kommen sie auch ohne "
                            "MQTT an — beide Wege tragen dieselben Werte.",
                            "Only needed if the values are to travel via MQTT. They also "
                            "arrive through the virtual HTTP input from step 1 — both "
                            "paths carry the same values."),
    "SCHRITT_3_BEFEHLSERKENNUNGEN": ("Schritt 3: Befehlserkennungen",
                            "Step 3: Command recognitions"),
    "SCHRITT_4_STEUERUNG": ("Schritt 4: Steuerung über einen Virtuellen Ausgang",
                            "Step 4: Control via a virtual output"),
    "SCHRITT_5_AUSFALL":   ("Schritt 5: Ausfallerkennung", "Step 5: Failure detection"),
    "SCHRITT_6_BAUSTEINE": ("Schritt 6: Komplette Baustein-Listen zum 1:1-Nachbauen",
        "Step 6: Complete block lists for a 1:1 rebuild"),
    "SCHRITT_7_GEGENPROBE": ("Schritt 7: Gegenprobe", "Step 7: Verification"),

    "AUSFALL_TEXT":        ("Ein virtueller Eingang <b>behält seinen letzten Wert</b>, wenn "
                            "nichts mehr kommt — in der App sieht dann alles normal aus. "
                            "Deshalb liefert das Plugin <span class='sm-mono'>TS</span> "
                            "(Zeitstempel des letzten Laufs) und <span class='sm-mono'>ZAEHLER</span> "
                            "(läuft 0…999 um). Alter in Sekunden = (Loxone-Zeit + 1230768000) − TS. "
                            "Eine Überwachung auf ein Alter über 300 s meldet einen stehenden "
                            "Cron-Lauf; steht zusätzlich der Zähler still, ist es kein Uhrenproblem. "
                            "<span class='sm-mono'>OK</span> beantwortet etwas anderes: ob der "
                            "Mäher beim letzten Messen erreichbar war.",
                            "A virtual input <b>keeps its last value</b> when nothing arrives "
                            "any more — everything then looks normal in the app. That is why "
                            "the plugin supplies <span class='sm-mono'>TS</span> (timestamp of "
                            "the last run) and <span class='sm-mono'>ZAEHLER</span> (wraps "
                            "0…999). Age in seconds = (Loxone time + 1230768000) − TS. Monitor "
                            "for an age above 300 s to detect a stalled cron run; if the counter "
                            "is stuck as well, it is not a clock problem. "
                            "<span class='sm-mono'>OK</span> answers something else: whether the "
                            "mower was reachable during the last measurement."),
    "GEGENPROBE_TEXT":     ("Alle Werte auch als JSON — dort steht neben dem Zustand das Feld "
                            "<span class='sm-mono'>werte</span> mit genau den Namen, die die "
                            "Befehlserkennungen suchen:",
                            "All values are also available as JSON — next to the state it "
                            "contains the field <span class='sm-mono'>werte</span> with exactly "
                            "the names the command recognitions look for:"),
    "CHECK_HILFE":         ("Diese Texte stehen genauso in der Importdatei aus dem Knopf weiter "
                            "unten. Wer sie abtippt, achtet auf das <b>führende Semikolon</b> — "
                            "ohne das trifft eine Erkennung unter Umständen die falsche Stelle "
                            "der Zeile.",
                            "These texts appear identically in the import file produced by the "
                            "button below. If you type them by hand, watch the <b>leading "
                            "semicolon</b> — without it a recognition may match the wrong part "
                            "of the line."),
    "TOKEN_NOETIG":        ("<b>Token nötig:</b> Der Endpunkt liegt unangemeldet und ist deshalb "
                            "mit einem Token abgesichert — ohne passendes "
                            "<span class='sm-mono'>&amp;token=…</span> antwortet er mit HTTP 403. "
                            "Wird das Token neu erzeugt, müssen alle Adressen oben in Loxone "
                            "nachgezogen werden.",
                            "<b>Token required:</b> the endpoint is unauthenticated and therefore "
                            "protected by a token — without a matching "
                            "<span class='sm-mono'>&amp;token=…</span> it answers with HTTP 403. "
                            "If the token is regenerated, all addresses above must be updated in "
                            "Loxone."),
    "AKTUELLES_TOKEN":     ("Aktuelles Token", "Current token"),
    "TOKEN_NEU_OK":        ("Neues Token erzeugt. <b>Die Adressen in Loxone müssen angepasst "
                            "werden</b> — die alten funktionieren nicht mehr.",
                            "New token created. <b>The addresses in Loxone must be updated</b> — "
                            "the old ones no longer work."),

    # --- Befehle
    "B_AUTO":              ("Automatikbetrieb (Zeitsteuerung des Mähers)",
                            "Automatic mode (mower’s own schedule)"),
    "B_HOME":              ("zurück zur Ladestation und dort bleiben",
                            "return to the charging station and stay there"),
    "B_MAN":               ("Handbetrieb", "Manual mode"),
    "B_EOD":               ("bis Feierabend mähen (End of Day)", "mow until end of day"),
    "B_START":             ("sofort starten", "start immediately"),
    "B_STOP":              ("sofort anhalten", "stop immediately"),
    "B_BLADE":             ("Messerwechsel quittieren (z. B. über einen Taster in der App)",
                            "acknowledge blade change (e.g. via a button in the app)"),

    # --- Kacheln
    "K_ZUSTAND":           ("Zustand", "State"),
    "K_AKKU":              ("Akku", "Battery"),
    "K_MODUS":             ("Betriebsart", "Mode"),
    "K_STUNDEN":           ("Betriebsstunden", "Operating hours"),
    "K_MESSER":            ("bis Messerwechsel", "until blade change"),
    "K_TEMP":              ("Temperatur", "Temperature"),
    "K_WLAN":              ("WLAN", "Wi-Fi"),
    "K_FEHLER":            ("Fehler %d:", "Fault %d:"),
    "K_MESSER_FAELLIG":    ("Der Messerwechsel ist fällig. Nach dem Wechsel unten quittieren — "
                            "das setzt den Nullpunkt neu.",
                            "The blade change is due. Acknowledge below after changing — this "
                            "resets the zero point."),
    "K_EINS_HEUTE":        ("Einsätze heute", "Runs today"),
    "K_MIN_HEUTE":         ("Mähdauer heute", "Mowing time today"),
    "K_EINS_WOCHE":        ("Einsätze diese Woche", "Runs this week"),
    "K_MIN_WOCHE":         ("Mähdauer diese Woche", "Mowing time this week"),

    # --- Knoepfe
    "SPEICHERN":           ("Speichern", "Save"),
    "K_SICHERN":           ("Einstellungen sichern", "Back up settings"),
    "K_ZURUECK":           ("Zurückspielen", "Restore"),
    "K_TOKEN_NEU":         ("Neues Token erzeugen", "Create new token"),
    "K_VORLAGE":           ("Vorlage für Loxone Config erzeugen", "Create template for Loxone Config"),
    "K_VORLAGE_VO":        ("Vorlage der Steuerbefehle erzeugen", "Create template for control commands"),
    "K_SELFTEST":          ("Token prüfen (löst nichts aus)", "Check token (triggers nothing)"),
    "K_TROCKEN":           ("Trockenlauf „Automatik“", "Dry run “automatic”"),
    "K_ROH_VERSION":       ("Rohe Antwort: version", "Raw response: version"),
    "K_ROH_STATUS":        ("Rohe Antwort: status", "Raw response: status"),
    "K_ROH_HEALTH":        ("Rohe Antwort: health", "Raw response: health"),
    "MESSERWECHSEL_QUITTIEREN": ("Messerwechsel quittieren", "Acknowledge blade change"),
    "PROTOKOLL_LEEREN":    ("Protokoll leeren", "Clear log"),
    "LOXONE_ZEILE_ABRUFEN": ("Loxone-Zeile abrufen", "Fetch Loxone line"),
    "JSON_ANSICHT":        ("JSON-Ansicht", "JSON view"),
    "DEBUG":               ("Debug", "Debug"),
    "TEST_PUSHNACHRICHT":  ("Test-Pushnachricht", "Test push message"),
    "AUTOMATIK":           ("Automatik", "Automatic"),
    "NACH_HAUSE":          ("Nach Hause", "Go home"),
    "STOPP":               ("Stopp", "Stop"),
    "ANSEHEN":             ("Ansehen", "View"),
    "TECHNISCHE_AUSKUNFT": ("Technische Auskunft", "Technical information"),
    "LST_ETWAS_AUS":       ("Löst etwas aus", "Triggers something"),

    # --- Tabellenkoepfe und kleine Beschriftungen
    "NAME":                ("Name", "Name"),
    "NAME_FREI":           ("Name (frei)", "Name (free)"),
    "ADRESSE":             ("Adresse", "Address"),
    "BENUTZER":            ("Benutzer", "User"),
    "PASSWORT":            ("Passwort", "Password"),
    "LOESCHEN":            ("Löschen", "Delete"),
    "EIGENSCHAFT":         ("Eigenschaft", "Property"),
    "WERT":                ("Wert", "Value"),
    "BEDEUTUNG":           ("Bedeutung", "Meaning"),
    "BEFEHLSERKENNUNG":    ("Befehlserkennung", "Command recognition"),
    "BEFEHL_BEI_EIN":      ("Befehl bei EIN", "Command on ON"),
    "WIRKUNG":             ("Wirkung", "Effect"),
    "THEMA":               ("Thema", "Topic"),
    "ZEITPUNKT":           ("Zeitpunkt", "Time"),
    "CODE_2":              ("Code", "Code"),
    "ABFRAGEZYKLUS":       ("Abfragezyklus", "Polling interval"),
    "ADRESSE_VIRTUELLER_AUSGANG": ("Adresse (Virtueller Ausgang)", "Address (virtual output)"),
    "OHNE":                ("ohne", "without"),
    "BENUTZER_UND_PASSWORT": ("Benutzer und Passwort!", "user and password!"),
    "EINE":                ("eine", "one"),
    "PORT":                ("Port", "Port"),
    "ZONEN":               ("Zonen", "Zones"),
    "LAUTSTRKE":           ("Lautstärke (%)", "Volume (%)"),
    "SPRACHE":             ("Sprache", "Language"),
    "AUDIO_AUSGABE":       ("Audio-Ausgabe", "Audio output"),
    "IP_DES_AUDIO_SERVERS": ("IP des Audio-Servers", "IP of the audio server"),
    "PLATZHALTER":         ("Platzhalter:", "Placeholders:"),
    "TOPIC_PRFIX":         ("Topic-Präfix", "Topic prefix"),
    "STATUS_CACHE_SEKUNDEN": ("Status-Cache (Sekunden)", "Status cache (seconds)"),
    "MESSERWECHSEL_INTERVALL_BETRIEBSST": ("Messerwechsel-Intervall (Betriebsstunden)",
                            "Blade change interval (operating hours)"),
    "NULLPUNKT_STUNDEN_BEIM_LETZTEN_WEC": ("Nullpunkt: Stunden beim letzten Wechsel",
                            "Zero point: hours at the last change"),
    "DATEI":               ("Datei:", "File:"),
    "FEHLER_4":            ("Fehler", "Error"),
    "KEINE_VERBINDUNG":    ("keine Verbindung", "no connection"),
    "KONFIGURATION_GESPEICHERT": ("Konfiguration gespeichert", "Configuration saved"),
    "ZUGANGSDATEN_MIT_DATEIRECHTEN_0600": ("(Zugangsdaten mit Dateirechten 0600, "
                            "inklusive Zweitschrift für Updates).",
                            "(credentials with file permissions 0600, including a second copy "
                            "for updates)."),
    "MESSER_QUITTIERT":    ("Messerwechsel quittiert — die Restlaufzeit startet neu.",
                            "Blade change acknowledged — the remaining runtime starts over."),

    # --- Platzhaltertexte
    "PH_NAME":             ("z. B. Rasenmäher", "e.g. lawn mower"),
    "PH_IP":               ("z. B. 192.168.1.34", "e.g. 192.168.1.34"),
    "PH_GESPEICHERT":      ("(gespeichert)", "(saved)"),
    "PH_TTS_IP":           ("z. B. 192.168.1.50", "e.g. 192.168.1.50"),

    # --- Ankreuzfelder. Das schliessende > des <input> steht im HTML, NICHT
    #     hier. Bis 1.0.13 trugen elf Werte es am Anfang - wer den Text
    #     uebersetzte und das Zeichen wegnahm, zerlegte das Formular.
    "AUDIOAUSGABE_AKTIV":  ("Audioausgabe aktiv", "Audio output active"),
    "PUSH_NACHRICHT_AKTIV": ("Push-Nachricht aktiv", "Push message active"),
    "STRUNG_SCHLEIFENSIGNAL_VERLOREN": ("Störung / Schleifensignal verloren",
                            "Fault / loop signal lost"),
    "MHEN_BEENDET":        ("Mähen beendet", "Mowing finished"),
    "MESSERWECHSEL_FLLIG": ("Messerwechsel fällig", "Blade change due"),
    "AKKU_UNTER_20_AUERHALB_DER_STATION": ("Akku unter 20 % außerhalb der Station",
                            "Battery below 20 % outside the station"),
    "ZUSTAND_PER_MQTT_VERFFENTLICHEN": ("Zustand per MQTT veröffentlichen",
                            "Publish state via MQTT"),
    "STAT_EIN":            ("Einsätze und Mähdauer mitzählen",
                            "Count runs and mowing time"),
    "LOXONE_MUSIC_SERVER_KLASSISCH": ("Loxone Music Server (klassisch)",
                            "Loxone Music Server (classic)"),
    "AUDIOSERVER4HOME_MUSICSERVER4HOME": ("Audioserver4Home / MusicServer4Home",
                            "Audioserver4Home / MusicServer4Home"),
    "ORIGINAL_LOXONE_AUDIOSERVER_VIA_LO": ("Original Loxone Audioserver (via Loxone Config)",
                            "Original Loxone Audioserver (via Loxone Config)"),
    "EIGENE_URL_VORLAGE":  ("Eigene URL-Vorlage", "Custom URL template"),

    # --- Hilfetexte
    "LOESCHEN_HILFE":      ("Gelöscht wird über den Haken, nie durch Leeren eines Feldes: "
                            "wer nur den Namen berichtigen will und ihn dabei kurz leert, "
                            "soll nicht die Zugangsdaten verlieren. Die unterste, leere Zeile "
                            "legt einen weiteren Mäher an.",
                            "Deletion happens via the checkbox, never by clearing a field: "
                            "someone who only wants to correct the name should not lose the "
                            "credentials while the field is briefly empty. The bottom, empty "
                            "row adds another mower."),
    "PASSWORT_HINWEIS":    ("Das Passwort wird <b>nie angezeigt</b> und beim Speichern behalten, "
                            "wenn das Feld leer bleibt. Es liegt ausschließlich in der "
                            "Plugin-Konfiguration (Dateirechte 0600) und wird per HTTP-Basic-Auth "
                            "übertragen — <b>in der Loxone-Projektdatei steht damit kein Passwort "
                            "mehr</b>. Genau dafür gibt es dieses Plugin.",
                            "The password is <b>never displayed</b> and is kept on save if the "
                            "field is left empty. It resides solely in the plugin configuration "
                            "(file permissions 0600) and is transmitted via HTTP basic auth — "
                            "<b>so no password appears in the Loxone project file</b>. That is "
                            "exactly what this plugin is for."),
    "STAT_HILFE":          ("Zählt abgeschlossene Mäheinsätze und die Mähdauer je Tag und Woche. "
                            "Die Dauer wird zwischen dem ersten und dem letzten Durchlauf mit "
                            "Zustand „mäht“ gemessen, nicht vom Mäher übernommen. Ab Werk aus — "
                            "eingeschaltet kommen vier weitere Werte in Vorlage, MQTT und "
                            "Antwortzeile dazu.",
                            "Counts completed mowing runs and mowing time per day and week. The "
                            "duration is measured between the first and last cycle in state "
                            "“mowing”, not taken from the mower. Off by default — when enabled, "
                            "four more values are added to template, MQTT and response line."),
    "ZONEN_HILFE":         ("Zonennummern mit Komma (z.&nbsp;B. <span class='sm-mono'>2,4,6</span>) "
                            "— die Lautstärke kommt aus dem Feld daneben. Optional je Zone eigene "
                            "Lautstärke: <span class='sm-mono'>2~25,4~40</span>. Leerzeichen nach "
                            "dem Komma sind erlaubt.",
                            "Zone numbers separated by commas (e.g. "
                            "<span class='sm-mono'>2,4,6</span>) — the volume comes from the "
                            "field next to it. Optionally a separate volume per zone: "
                            "<span class='sm-mono'>2~25,4~40</span>. Spaces after the comma are "
                            "allowed."),
    "THEMEN_HILFE":        ("Diese Liste entsteht aus derselben Quelle wie der Sendecode — sie "
                            "kann also nicht veralten. Die drei Themen unter "
                            "<span class='sm-mono'>status/</span> gelten für die ganze Anlage, "
                            "nicht je Mäher.",
                            "This list is generated from the same source as the sending code — so "
                            "it cannot become stale. The three topics under "
                            "<span class='sm-mono'>status/</span> apply to the whole installation, "
                            "not per mower."),
    "THEMEN_MEHRERE":      ("Bei mehreren Mähern trägt jeder weitere seine Nummer im Thema: "
                            "<span class='sm-mono'>&lt;präfix&gt;/2/…</span> bis "
                            "<span class='sm-mono'>&lt;präfix&gt;/%d/…</span>. Der erste Mäher "
                            "bleibt ohne Nummer, damit bestehende Anlagen nichts ändern müssen.",
                            "With several mowers each additional one carries its number in the "
                            "topic: <span class='sm-mono'>&lt;prefix&gt;/2/…</span> up to "
                            "<span class='sm-mono'>&lt;prefix&gt;/%d/…</span>. The first mower "
                            "stays without a number so existing installations need no changes."),
    "SELBST_HILFE":        ("Diese Prüfung beantwortet <b>ohne Loxone</b>, ob die Einrichtung "
                            "trägt. Der Aufruf des eigenen Endpunkts wird 300 Sekunden lang "
                            "zwischengespeichert — sonst riefe sich der Webserver bei jedem Klick "
                            "selbst auf.",
                            "This check answers <b>without Loxone</b> whether the setup works. "
                            "The call to our own endpoint is cached for 300 seconds — otherwise "
                            "the web server would call itself on every click."),
    "SELBST_STRICH":       ("Ein Strich ist <b>kein Haken</b>: er heißt „ließ sich nicht "
                            "feststellen“ und ist etwas anderes als „in Ordnung“.",
                            "A dash is <b>not a check mark</b>: it means “could not be "
                            "determined” and is different from “fine”."),
    "ROHBEFEHL_HILFE":     ("Welche Lesebefehle Ihr Robonect-Modul kennt, ist <b>nicht "
                            "gemessen</b> — es hängt von Modell und Firmware ab. Diese Knöpfe "
                            "zeigen die rohe Antwort, damit die Anlage die Frage selbst "
                            "beantwortet. Kommt <span class='sm-mono'>BEFEHL_UNBEKANNT</span>, "
                            "kennt das Plugin ihn nicht; kommt eine leere oder fehlerhafte "
                            "Antwort, kennt ihn das Modul nicht.",
                            "Which read commands your Robonect module supports has <b>not been "
                            "measured</b> — it depends on model and firmware. These buttons show "
                            "the raw response so the installation answers the question itself. "
                            "If <span class='sm-mono'>BEFEHL_UNBEKANNT</span> appears the plugin "
                            "does not know it; an empty or faulty response means the module does "
                            "not."),
    "SCHALTEN_HINWEIS":    ("Diese Knöpfe wirken <b>sofort</b> auf den Mäher. Der Trockenlauf (grau, unter „Technische Auskunft“) läuft durch dieselbe Funktion und sagt nur, was gesendet <i>würde</i> — er sendet nicht. „Testansage sprechen“ nimmt die gespeicherte Sprachausgabe.",
                            "These buttons act on the mower <b>immediately</b>. The dry run (grey, under “Technical information”) goes through the same function and only reports what <i>would</i> be sent — it does not send. “Speak test announcement” uses the saved speech output."),
    "HERSTELLERANGABE_OFT_150250_H": ("Herstellerangabe, oft 150–250 h.",
                            "Manufacturer’s figure, often 150–250 h."),
    "WIRD_BEIM_QUITTIEREN_AUTOMATISCH_G": ("Wird beim Quittieren automatisch gesetzt (Knopf unten "
                            "oder", "Set automatically when acknowledging (button below or"),
    "DIE_ANSAGE_SPRICHT_DAS_PLUGIN_SELB": ("Die Ansage spricht das Plugin selbst; den Push "
                            "verschickt der Miniserver über",
                            "The plugin speaks the announcement itself; the push is sent by the "
                            "Miniserver via"),
    "DER_ORIGINALE_LOXONE_AUDIOSERVER_B": ("Der originale Loxone Audioserver bietet keine "
                            "HTTP-TTS-Schnittstelle. In diesem Modus spricht das Plugin nicht "
                            "selbst; die Ausgabe baut man in Loxone Config über Textgenerator und",
                            "The original Loxone Audioserver offers no HTTP TTS interface. In this "
                            "mode the plugin does not speak itself; build the output in Loxone "
                            "Config using the text generator and"),
    "URL_VORLAGE_FR_AUDIOSERVER4HOME_MS": ("URL-Vorlage (für Audioserver4Home/MS4H bzw. eigene "
                            "Ausgabe)", "URL template (for Audioserver4Home/MS4H or custom output)"),
    "IP_PORT_ZONES_VOL_LANG_TEXT": ("{ip} {port} {zones} {vol} {lang} {text}",
                            "{ip} {port} {zones} {vol} {lang} {text}"),
    "LEER_STANDARD_VORLAGE": (". Leer = Standard-Vorlage.", ". Empty = default template."),
    "NOCH_KEIN_MHER_EINGERICHTET": ("Noch kein Mäher eingerichtet.", "No mower configured yet."),
    "BITTE_UNTEN_ADRESSE_BENUTZER_UND_P": ("Bitte unten Adresse, Benutzer und Passwort des "
                            "Robonect-Moduls eintragen.",
                            "Please enter address, user and password of the Robonect module below."),
    "ADRESSE_UND_ZUGANGSDATEN_PRFEN_ROB": ("Adresse und Zugangsdaten prüfen (Robonect-Oberfläche "
                            "im Browser erreichbar?).",
                            "Check address and credentials (is the Robonect interface reachable in "
                            "a browser?)."),
    "DER_MINISERVER_FRAGT": ("Der Miniserver fragt", "The Miniserver polls"),
    "ADRESSE_OHNE_ZUGANGSDATEN_AB_UND_B": ("Adresse ohne Zugangsdaten ab und bekommt fertige "
                            "Zahlenwerte. Die Steuerung läuft über ebenso einfache Adressen — das "
                            "Passwort bleibt im LoxBerry.",
                            "address without credentials and receives ready-made numeric values. "
                            "Control works through equally simple addresses — the password stays "
                            "on the LoxBerry."),
    "DER_BISHERIGE_EINGANG_MIT": ("Der bisherige Eingang mit", "The previous input using"),
    "KANN_DANACH_GELSCHT_WERDEN": ("kann danach gelöscht werden.", "can be deleted afterwards."),
    "H_VORLAGE_TEXT":      ("Statt jeden Wert von Hand als virtuellen Eingang anzulegen: diese "
                            "Datei enthält alle Werte samt Einheit, Grenzen und Kommentar. "
                            "<b>Achtung:</b> Loxone Config legt beim Import neu an und "
                            "überschreibt nichts — zweimal eingelesen ergibt doppelte Bausteine.",
                            "Instead of creating every value by hand as a virtual input: this file "
                            "contains all values including unit, limits and comment. "
                            "<b>Caution:</b> Loxone Config creates new objects on import and "
                            "overwrites nothing — importing twice yields duplicate blocks."),
    "PROTOKOLLIERT_WERDEN_STATUSNDERUNG": ("Protokolliert werden Statusänderungen, Meldungen und "
                            "Steuerbefehle. Passwörter werden vor dem Schreiben maskiert. Neueste "
                            "Einträge oben (max. 300).",
                            "Logged are status changes, notifications and control commands. "
                            "Passwords are masked before writing. Newest entries at the top "
                            "(max. 300)."),
    "NOCH_KEINE_PROTOKOLL_EINTRGE_VORHA": ("Noch keine Protokoll-Einträge vorhanden.",
                            "No log entries yet."),
    "NACH_HAUSE_IST_DER_UNGEFHRLICHSTE_": ("„Nach Hause“ ist der ungefährlichste Test: Der Mäher "
                            "fährt zur Ladestation und bleibt dort, bis wieder auf Automatik "
                            "gestellt wird.",
                            "“Go home” is the least risky test: the mower drives to the charging "
                            "station and stays there until automatic mode is set again."),

    # --- Statuscodes
    "STATUS_WIRD_ERMITTELT": ("Status wird ermittelt", "Determining status"),
    "PARKT":               ("parkt", "parked"),
    "MHT":                 ("mäht", "mowing"),
    "SUCHT_DIE_LADESTATION": ("sucht die Ladestation", "searching for the charging station"),
    "LDT":                 ("lädt", "charging"),
    "SUCHT":               ("sucht", "searching"),
    "SCHLEIFENSIGNAL_VERLOREN": ("Schleifensignal verloren", "loop signal lost"),
    "ABGESCHALTET":        ("abgeschaltet", "switched off"),
    "SCHLFT":              ("schläft", "sleeping"),
    "WIRD_GEWARTET":       ("wird gewartet", "being serviced"),

    # --- MQTT-Themen ohne eigenes Feld
    # Nachlese 25.09.2026 (Robonect 1.1.12): status traegt bei nicht
    # erreichbarem Maeher die Aussage des Plugins ueber den eigenen Abruf und
    # geht deshalb nicht mehr zurueckbehalten; der Geraeteteil steht als
    # maeherstatus daneben (Regeln/07 Abschnitt 3).
    "TH_STATUS":           ("Zustand als Klartext (nur über MQTT), nicht zurückbehalten — "
                            "antwortet der Mäher nicht, steht hier, warum",
                            "State as plain text (MQTT only), not retained — if the mower does "
                            "not answer, this says why"),
    "TH_MAEHERSTATUS":     ("Zustand als Klartext, wie der Mäher ihn meldet (nur über MQTT), "
                            "zurückbehalten — geht nur hinaus, wenn der Mäher geantwortet hat",
                            "State as plain text as reported by the mower (MQTT only), retained — "
                            "only sent when the mower answered"),
    # A9: ein Thema, zu dem die Zuordnung kein Feld kennt, wird GENANNT.
    # Bis 1.1.3 blieb die Zelle leer - vier von 55 Zeilen, und stumm.
    "TH_OHNE":             ("(zu diesem Thema kennt das Plugin kein Feld: %s)",
                            "(no field known for this topic: %s)"),
    "TH_TS":               ("Zeitstempel des letzten Cron-Laufs, Unix-Sekunden",
                            "Timestamp of the last cron run, Unix seconds"),
    "TH_ZAEHLER":          ("Laufzähler, läuft 0…999 um", "Run counter, wraps 0…999"),
    "TH_OK":               ("1 = der letzte Lauf hat wirklich gemessen",
                            "1 = the last run actually measured"),
    "ABO_TITEL":           ("Das Abo im MQTT-Gateway",
                            "The subscription in the MQTT gateway"),
    "ABO_PFLICHT":         ("<b>Ohne diesen Eintrag kommt am Miniserver nichts an.</b> "
                            "System → MQTT Gateway → Subscriptions.",
                            "<b>Without this entry nothing arrives at the Miniserver.</b> "
                            "System → MQTT Gateway → Subscriptions."),
    "ABO_V2":              ("<b>MQTT-Gateway V2 erkennt die Themengruppe von selbst</b> — "
                            "einzutragen ist hier nichts. In den <i>Subscriptions</i> erscheint "
                            "die Gruppe; dort werden die gewünschten Datenpunkte einzeln "
                            "angehakt. Erscheint sie nicht, hat noch nichts veröffentlicht.",
                            "<b>MQTT gateway V2 detects the topic group by itself</b> — "
                            "nothing needs to be entered here. The group appears under "
                            "<i>Subscriptions</i>; tick the desired data points there. If it does "
                            "not appear, nothing has been published yet."),
    "ABO_UNBEKANNT":       ("Welche Fassung Ihr MQTT-Gateway hat, ließ sich nicht feststellen. "
                            "<b>Fassung&nbsp;1:</b> ohne diesen Eintrag kommt am Miniserver nichts "
                            "an. <b>Fassung&nbsp;2 und neuer:</b> die Themengruppe erscheint von "
                            "selbst in den Subscriptions, einzutragen ist nichts.",
                            "The version of your MQTT gateway could not be determined. "
                            "<b>Version&nbsp;1:</b> without this entry nothing arrives at the "
                            "Miniserver. <b>Version&nbsp;2 and newer:</b> the topic group appears "
                            "by itself under Subscriptions, nothing needs to be entered."),
    "ABO_GEMESSEN":        ("(gemessen: Gateway&nbsp;V%d)", "(measured: gateway&nbsp;V%d)"),
    "W_AUTOSTART":         ("Das MQTT-Gateway steht nicht auf Autostart (System → MQTT "
                            "Gateway). Es wird gesendet, aber vermutlich hört niemand zu.",
                            "The MQTT gateway is not set to autostart (System → MQTT "
                            "Gateway). Data is sent, but probably nobody is listening."),

    # --- Meldungen der Sicherung
    "SICH_ERKLAERUNG":     ("Für den <b>Umzug auf einen zweiten LoxBerry</b>: die Datei enthält "
                            "alle Einstellungen dieses Plugins und lässt sich dort wieder "
                            "einspielen.",
                            "For <b>moving to a second LoxBerry</b>: the file contains all "
                            "settings of this plugin and can be imported there."),
    "SICH_WARNUNG":        ("<b>Die Datei enthält Ihre Zugangsdaten.</b> Ohne sie stünden nach dem "
                            "Zurückspielen alle Felder richtig, und das Plugin käme trotzdem nicht "
                            "an die Anlage. Behandeln Sie die Datei wie ein Passwort: nicht in ein "
                            "Forum hängen und nicht an einen Fehlerbericht heften.",
                            "<b>The file contains your credentials.</b> Without them all fields "
                            "would look right after restoring and the plugin still would not reach "
                            "the installation. Treat the file like a password: do not post it in a "
                            "forum and do not attach it to a bug report."),
    "SICH_ABGELEHNT":      ("Die Datei wurde <b>nicht</b> übernommen — es ist nichts geändert "
                            "worden:",
                            "The file was <b>not</b> imported — nothing has been changed:"),
    # Fehlende Schluessel sind eine Beanstandung (Umbau ro_sicherung_lesen,
    # 07.09.2026). Der Schluessel stand bis dahin nur von Hand in der .ini
    # und haette beim naechsten Erzeugerlauf gefehlt.
    "SICH_FEHLEND":        ("In der Datei fehlen %d Einstellungen: %s. Eine unvollständige "
                            "Sicherung wird nicht zurückgespielt — sonst fielen die "
                            "fehlenden Werte stillschweigend auf die Werkseinstellung zurück, "
                            "ohne dass an der Oberfläche etwas davon zu sehen wäre.",
                            "The file is missing %d settings: %s. An incomplete backup is not "
                            "restored — otherwise the missing values would silently fall "
                            "back to the factory defaults, with nothing on the page to show it."),
    "SICH_FREMD":          ("Unbekannte Einstellung in der Datei: %s",
                            "Unknown setting in the file: %s"),
    "SICH_WERT":           ("Unzulässiger Wert für %s.", "Invalid value for %s."),
    "SICH_BEREICH":        ("Der Wert für %s liegt außerhalb von %d bis %d.",
                            "The value for %s is outside the range %d to %d."),
    "SICH_MAEHER_FORM":    ("Mäher %d: die Angaben haben nicht die erwartete Form.",
                            "Mower %d: the entries do not have the expected form."),
    # Messerwechsel je Maeher (1.1.4). Ein leeres Feld heisst "wie die
    # Vorgabe weiter unten" - das ist der Zustand jeder bestehenden Anlage
    # und darf sich nicht still aendern.
    "MESSER_IV_KURZ":      ("Messer: Intervall (h)", "Blade: interval (h)"),
    "MESSER_NP_KURZ":      ("Messer: Nullpunkt (h)", "Blade: zero point (h)"),
    "MESSER_JE_MAEHER":    ("Intervall und Nullpunkt gelten <b>je Mäher</b>. Bleibt ein Feld leer, "
                            "gilt die Vorgabe weiter unten — so verhält sich jeder Mäher wie bisher, "
                            "bis Sie hier etwas eintragen.",
                            "Interval and zero point apply <b>per mower</b>. If a field is left empty, "
                            "the default further down applies — so every mower behaves as before "
                            "until you enter something here."),
    "MESSER_VORGABE":      ("Vorgabe für Mäher ohne eigenen Wert",
                            "Default for mowers without their own value"),
    "QUITTIEREN_FUER":     ("Messerwechsel quittieren für", "Acknowledge blade change for"),
    "SICH_MAEHER_BLADE":   ("Mäher %d: %s muss eine ganze Zahl von %d bis %d sein (%s).",
                            "Mower %d: %s must be a whole number from %d to %d (%s)."),
    "SICH_MAEHER_IP":      ("Mäher %d: ungültige Adresse (%s).", "Mower %d: invalid address (%s)."),
    # A19: ein geleertes Adressfeld hat die Zeile bis 1.1.3 samt Benutzer und
    # Kennwort still verworfen - während der Hilfetext daneben zusagte,
    # gelöscht werde nur über den Haken.
    "MAEHER_ADRESSE_LEER": ("Mäher %d: die Adresse fehlt. Zum Entfernen bitte den Haken "
                            "„Löschen“ setzen — ein leeres Feld löscht nichts.",
                            "Mower %d: the address is missing. To remove the mower, tick "
                            "“Delete” — an empty field deletes nothing."),
    "SICH_ZU_VIELE":       ("Mehr als %d Mäher werden nicht geführt.",
                            "More than %d mowers are not supported."),
    "SICH_KEINE_DATEI":    ("Es wurde keine Datei ausgewählt oder der Upload ist fehlgeschlagen.",
                            "No file was selected or the upload failed."),
    "SICH_KEIN_JSON":      ("Die Datei ist keine gültige Sicherung dieses Plugins.",
                            "The file is not a valid backup of this plugin."),
    "SICH_LEER":           ("Die Datei enthält keine bekannte Einstellung.",
                            "The file contains no known setting."),
    "SICH_SCHREIBFEHLER":  ("Die Einstellungen ließen sich nicht schreiben.",
                            "The settings could not be written."),
    "SICH_UEBERNOMMEN":    ("Einstellungen zurückgespielt: %d Werte übernommen. Der "
                            "Zwischenspeicher wurde verworfen; die Werte gelten ab dem nächsten "
                            "Cron-Lauf.",
                            "Settings restored: %d values imported. The cache was discarded; the "
                            "values take effect with the next cron run."),
    "SICH_ZU_GROSS":       ("Die Datei ist größer als erlaubt — eine Sicherung dieses Plugins ist "
                            "wenige Kilobyte groß.",
                            "The file is larger than allowed — a backup of this plugin is a few "
                            "kilobytes in size."),

    # --- Fehler und Wachposten
    "FEHLER_SCHREIBEN":    ("Konfiguration konnte nicht geschrieben werden: %s",
                            "Configuration could not be written: %s"),
    "CSRF":                ("Das Formular trug kein gültiges Merkmal und wurde abgewiesen — es "
                            "ist nichts geändert worden. Harmlose Ursache: die Seite lag lange "
                            "offen, während das Aktionstoken neu erzeugt wurde. Dann genügt ein "
                            "Neuladen.",
                            "The form did not carry a valid marker and was rejected — nothing has "
                            "been changed. Harmless cause: the page was open for a long time while "
                            "the action token was regenerated. Reloading is then enough."),
    "CSRF_KEIN_TOKEN":     ("Es ist kein Aktionstoken eingerichtet, deshalb lässt sich kein "
                            "Formular prüfen — und ohne Prüfung wird nichts geändert. Bitte die "
                            "Seite neu laden; das Token wird dabei erzeugt.",
                            "No action token is set up, so no form can be verified — and without "
                            "verification nothing is changed. Please reload the page; the token is "
                            "created in the process."),

    # --- Meldungen der Selbstpruefung
    "PRUEF_CFG_OK":        ("in Ordnung", "fine"),
    "PRUEF_CFG_LEER":      ("noch leer — es ist nichts eingerichtet", "still empty — nothing set up"),
    "PRUEF_CFG_ZWEIT":     ("Sie wurde aus der Zweitschrift wiederhergestellt.",
                            "It was restored from the second copy."),
    "PRUEF_CFG_KAPUTT":    ("Die Datei war kein gültiges JSON. Sie liegt als "
                            "<span class='sm-mono'>mower.json.kaputt</span> daneben; gearbeitet "
                            "wird mit der Zweitschrift.",
                            "The file was not valid JSON. It is kept as "
                            "<span class='sm-mono'>mower.json.kaputt</span>; the second copy is "
                            "being used."),
    "PRUEF_CFG_KAPUTT_OHNE": ("Die Datei war kein gültiges JSON, und es gibt keine Zweitschrift. "
                            "Es gelten die Werkseinstellungen.",
                            "The file was not valid JSON and there is no second copy. Factory "
                            "settings apply."),
    "PRUEF_CFG_VOLL":      ("ja, alle %d Einstellungen stehen in der Datei",
                            "yes, all %d settings are present in the file"),
    "PRUEF_CFG_FEHLT":     ("nein, es fehlen %d von %d: %s (im Betrieb greifen die Vorgaben)",
                            "no, %d of %d are missing: %s (defaults apply at runtime)"),
    "PRUEF_CFG_FREMD":     ("In der Datei stehen Einstellungen, die es nicht gibt: %s — sie wirken "
                            "nicht.", "The file contains settings that do not exist: %s — they have "
                            "no effect."),
    "PRUEF_MAEHER_JA":     ("ja, alle %d", "yes, all %d"),
    "PRUEF_MAEHER_NEIN":   ("%d von %d — nicht erreichbar: %s", "%d of %d — unreachable: %s"),
    "PRUEF_MAEHER_KEINER": ("Es ist kein Mäher eingerichtet.", "No mower is configured."),
    "PRUEF_CRON_JA":       ("ja, letzter Lauf vor %d s, Zähler %d", "yes, last run %d s ago, counter %d"),
    "PRUEF_CRON_ALT":      ("Der letzte Lauf ist %d s her — er sollte jede Minute kommen. Läuft der "
                            "Cron-Dienst?",
                            "The last run was %d s ago — it should occur every minute. Is the cron "
                            "service running?"),
    "PRUEF_CRON_NIE":      ("Es hat noch kein Cron-Lauf stattgefunden. Nach der Installation dauert "
                            "das bis zu einer Minute.",
                            "No cron run has happened yet. After installation this takes up to one "
                            "minute."),
    "PRUEF_TOKEN_JA":      ("ja", "yes"),
    "PRUEF_TOKEN_NEIN":    ("nein — ohne Token weist der Endpunkt jeden Aufruf ab.",
                            "no — without a token the endpoint rejects every call."),
    "PRUEF_EP_JA":         ("ja, HTTP %d und die Antwort ist plausibel",
                            "yes, HTTP %d and the response is plausible"),
    "PRUEF_EP_NEIN":       ("Der Endpunkt antwortete mit HTTP %d: %s",
                            "The endpoint answered with HTTP %d: %s"),
    "PRUEF_EP_UNKLAR":     ("nicht feststellbar — der Aufruf auf 127.0.0.1 kam nicht zustande. "
                            "Das ist kein Befund: er sagt nur, dass hier nicht gemessen werden "
                            "konnte.",
                            "not determinable — the call to 127.0.0.1 did not go through. This is "
                            "not a finding: it only says that nothing could be measured here."),
    "PRUEF_EP_KEIN_TOKEN": ("Ohne eingerichtetes Token lässt sich der Endpunkt nicht prüfen.",
                            "Without a token in place the endpoint cannot be checked."),
    "PRUEF_GW_JA":         ("Autostart ist an, Gateway-Fassung %s.",
                            "Autostart is on, gateway version %s."),
    "PRUEF_GW_NEIN":       ("Autostart ist AUS (System → MQTT Gateway), Gateway-Fassung %s. "
                            "Es wird gesendet, aber vermutlich hört niemand zu.",
                            "Autostart is OFF (System → MQTT Gateway), gateway version %s. "
                            "Data is sent, but probably nobody is listening."),
    "PRUEF_GW_UNKLAR":     ("nicht feststellbar — <span class='sm-mono'>general.json</span> war "
                            "nicht lesbar.",
                            "not determinable — <span class='sm-mono'>general.json</span> was not "
                            "readable."),
    "PRUEF_GW_UNBEKANNT":  ("unbekannt", "unknown"),
    "PRUEF_THEMEN":        ("ja — %d Themen je Mäher, %d für die Anlage, %d Felder in der Vorlage. "
                            "Jedes Thema ist einem Feld zugeordnet.",
                            "yes — %d topics per mower, %d for the installation, %d fields in the "
                            "template. Every topic maps to a field."),
    # Bis 1.1.3 stand das ok dieser Zeile als feste 1 im Quelltext: sie
    # zählte drei Zahlen und verglich nichts. Jetzt gibt es beide Ausgänge.
    "PRUEF_THEMEN_NEIN":   ("nein — zu diesen Themen gibt es kein Feld: %s",
                            "no — no field exists for these topics: %s"),
    "PRUEF_REITER_JA":     ("ja, alle %d Reiter", "yes, all %d tabs"),
    "PRUEF_REITER_LEER":   ("Es wurde kein einziger Reiter gefunden — die Prüfung greift ins Leere.",
                            "Not a single tab was found — the check has nothing to measure."),
    "PRUEF_REITER_FEHLT":  ("Zu diesen Reitern gibt es keinen Bereich: %s",
                            "There is no pane for these tabs: %s"),
    "PRUEF_REITER_UEBER":  ("Unerreichbare Bereiche: %s", "Unreachable panes: %s"),
    "PRUEF_REITER_LEISTE": ("Diese Reiter fehlen in der Leiste: %s",
                            "These tabs are missing from the bar: %s"),
    "PRUEF_FORM_JA":       ("ja, alle %d Formulare", "yes, all %d forms"),
    "PRUEF_FORM_NEIN":     ("nein — %d von %d ohne Merkmal", "no — %d of %d without the marker"),
    "PRUEF_FORM_LEER":     ("Es wurde kein Formular gefunden — die Prüfung greift ins Leere.",
                            "No form was found — the check has nothing to measure."),
    "PRUEF_DL_JA":         ("ja — er kann eine Datei ausliefern.",
                            "yes — it can deliver a file."),
    "PRUEF_DL_NEIN":       ("NEIN — der Zweig steht hinter dem Seitenkopf. Der Knopf liefert dann "
                            "keine Datei, sondern die Konfiguration als sichtbaren Text.",
                            "NO — the branch sits behind the page header. The button then delivers "
                            "no file but the configuration as visible text."),
    "PRUEF_DL_UNKLAR":     ("nicht feststellbar — die erwarteten Stellen wurden nicht gefunden.",
                            "not determinable — the expected places were not found."),
    "PRUEF_XML_JA":        ("ja, alle %d wohlgeformt", "yes, all %d well-formed"),
    "PRUEF_XML_NEIN":      ("Die Vorlage %s ist nicht wohlgeformt.",
                            "The template %s is not well-formed."),
    "PRUEF_DATEI_LEER":    ("nicht feststellbar — %s war nicht lesbar.",
                            "not determinable — %s was not readable."),

    # --- Nachgezogen 07.09.2026: stand bis dahin nur von Hand in der
    # .ini und waere beim naechsten Erzeugerlauf verschwunden.
    "ABFRAGE_ALLE_S": ("(Abfrage alle %d s)",
                       "(polled every %d s)"),
    "EMPFEHLUNG_20_EINE_LOXONE_ABFRAGE_": ("Empfehlung 20 — eine Loxone-Abfrage alle %d s reicht völlig.",
                                           "Recommendation 20 — one Loxone poll every %d s is plenty."),
    "LOG_RAMDISK": ("Das Protokoll liegt auf einer Ramdisk und übersteht keinen "
                    "Neustart. Wer eine Meldung aufheben will, kopiert sie vorher "
                    "heraus.",
                    "The log lives on a RAM disk and does not survive a reboot. "
                    "Copy a message out before restarting if you want to keep it."),
    "NR": ("Nr.",
           "No."),
    "PRUEF_RETAIN_JA": ("ja, alle %d Themen entschieden (%d davon zurückbehalten)",
                        "yes, all %d topics decided (%d of them retained)"),
    "PRUEF_RETAIN_LEER": ("Es gibt keine Themenliste — hier wurde nichts gemessen.",
                          "There is no topic list — nothing was measured here."),
    "PRUEF_RETAIN_NEIN": ("Ohne Entscheidung, gehen deshalb flüchtig hinaus: %s",
                          "Undecided, therefore sent volatile: %s"),
    "PRUEF_SIGNATUR_JA": ("ja — gleicher Zustand mit anderem Wortlaut ergibt dieselbe "
                          "Signatur, ein anderer Grund eine andere (%d Felder verglichen)",
                          "yes — the same state with different wording gives the same "
                          "signature, a different reason gives a different one (%d "
                          "fields compared)"),
    "PRUEF_SIGNATUR_LAUT": ("Nein — zwei Wortlaute desselben Zustands ergeben verschiedene "
                            "Signaturen (%s). Der volle Wertsatz ginge jede Minute hinaus.",
                            "No — two wordings of the same state give different signatures "
                            "(%s). The full value set would go out every minute."),
    "PRUEF_SIGNATUR_LEER": ("Hier wurde nichts gemessen: die Signaturquelle ist leer.",
                            "Nothing was measured here: the signature source is empty."),
    "PRUEF_SIGNATUR_STUMPF": ("Nein — ein Wechsel des Grundes ohne Änderung einer Zahl ändert die Signatur nicht. Das Thema status (flüchtig) ginge mit dem alten Wortlaut nicht neu hinaus.",
                              "No — a change of reason without a change in numbers does not change the signature. The topic status (not retained) would not be sent again with the new wording."),
    "PRUEF_SIGNATUR_UNKLAR": ("Hier wurde nichts gemessen: zwischen den beiden Läufen hat "
                              "sich %s bewegt.",
                              "Nothing was measured here: %s moved between the two runs."),
    "PRUEF_SMACTIVE_JA": ("ja, an Leiste und Bereichen (%d Reiter)",
                          "yes, on the bar and the panes (%d tabs)"),
    "PRUEF_SMACTIVE_NEIN": ("Nein — Leiste %d, Bereiche %d von %d. Ohne JavaScript wäre "
                            "die Seite leer.",
                            "No — bar %d, panes %d of %d. Without JavaScript the page "
                            "would be empty."),
    "SEKUNDEN_N": ("%d Sekunden",
                   "%d seconds"),
    # ---- Werkzeug-S1 (02.10.2026): nachgezogen auf Robonect 1.1.15 ----
    "ABO_DATEI": ("<b>Das Plugin bringt das Abo selbst mit</b> (Abodatei <span class='sm-mono'>mqtt_subscriptions.cfg</span>, folgt dem Präfix). Das MQTT-Gateway liest sie; einzutragen ist nichts.", "<b>The plugin brings the subscription itself</b> (subscription file <span class='sm-mono'>mqtt_subscriptions.cfg</span>, follows the prefix). The MQTT gateway reads it; nothing to enter."),
    "ALEXA_ANTWORT": ("Alexa-NG lehnt ab: HTTP %d, GRUND=%s.", "Alexa-NG refuses: HTTP %d, GRUND=%s."),
    "ALEXA_FEHLT": ("Alexa-NG ist unter %s nicht zu finden (HTTP 404) – ist das Plugin installiert?", "Alexa-NG cannot be found at %s (HTTP 404) – is the plugin installed?"),
    "ALEXA_GERAET": ("Echo-Gerät oder Gruppe", "Echo device or group"),
    "ALEXA_GERAET_PH": ("leer = Standardgerät von Alexa-NG", "empty = default device of Alexa-NG"),
    "ALEXA_HINWEIS": ("Ausgabe über das Plugin <a href='https://github.com/timanders22/LoxBerry-Plugin-Alexa-NG' target='_blank' rel='noopener'>Alexa-NG</a> auf diesem LoxBerry. Das Sprechtoken steht dort im Reiter Einbindung; es wird hier wie ein Kennwort behandelt: nie angezeigt, nicht in der Sicherung, leer lassen behält es.", "Output via the plugin <a href='https://github.com/timanders22/LoxBerry-Plugin-Alexa-NG' target='_blank' rel='noopener'>Alexa-NG</a> on this LoxBerry. The speech token is shown there in the tab Integration; here it is treated like a password: never shown, not in the backup, leaving it empty keeps it."),
    "ALEXA_KEINE_ANTWORT": ("Alexa-NG antwortet nicht unter %s (Wartezeit %d s, %s).", "Alexa-NG does not respond at %s (timeout %d s, %s)."),
    "ALEXA_KEIN_TOKEN": ("Für Alexa-NG ist kein Sprechtoken eingetragen (Reiter Einstellungen, Sprachausgabe).", "No speech token is set for Alexa-NG (tab Settings, speech output)."),
    "ALEXA_LAUT": ("Lautstärke der Ansage (0–100)", "Announcement volume (0–100)"),
    "ALEXA_LAUT_PH": ("leer = bleibt", "empty = unchanged"),
    "ALEXA_NG_AUSGABE": ("Alexa-NG (Echo-Geräte)", "Alexa-NG (Echo devices)"),
    "ALEXA_OHNE_TOKEN": ("Für die Ausgabe über Alexa-NG fehlt das Sprechtoken.", "The speech token is missing for output via Alexa-NG."),
    "ALEXA_TOKEN": ("Sprechtoken", "Speech token"),
    "ALEXA_TOKEN_GESPEICHERT": ("gespeichert (%d Zeichen) – leer lassen behält es", "stored (%d characters) – leave empty to keep it"),
    "ALEXA_TOKEN_LOESCHEN": ("Sprechtoken löschen", "Delete speech token"),
    "ALEXA_TOKEN_WIDERSPRUCH": ("Sprechtoken: ein neues Token und der Haken „löschen“ zugleich — bitte eines von beiden.", "Speech token: a new token and the box “delete” at the same time — please only one of them."),
    "ALEXA_UNERWARTET": ("Unerwartete Antwort von Alexa-NG: HTTP %d, %s.", "Unexpected answer from Alexa-NG: HTTP %d, %s."),
    "AN": ("an", "on"),
    "ANSAGE_AUDIOSERVER": ("Ausgabeart Loxone Audioserver: das Plugin spricht nicht selbst, die Ansage baut Loxone Config.", "Output type Loxone Audioserver: the plugin does not speak itself, Loxone Config builds the announcement."),
    "ANSAGE_FEHLER": ("Der Audio-Server hat die Ansage nicht angenommen (keine Antwort oder Fehler).", "The audio server did not accept the announcement (no answer or error)."),
    "ANSAGE_KEINE_IP": ("Es ist keine IP des Audio-Servers eingetragen.", "No IP of the audio server is set."),
    "AUS": ("aus", "off"),
    "BEFEHLE_FUER": ("Mäher %d: %s", "Mower %d: %s"),
    "GLEICHWERT_HILFE": ("<b>Gleichwert-Sperre:</b> derselbe Modus (<span class='sm-mono'>auto</span>, <span class='sm-mono'>man</span>, <span class='sm-mono'>home</span>, <span class='sm-mono'>eod</span>, <span class='sm-mono'>job</span>) innerhalb von 60 s geht nicht noch einmal an den Mäher; die Antwort sagt <span class='sm-mono'>UNVERAENDERT=1</span>. <span class='sm-mono'>start</span> und <span class='sm-mono'>stop</span> gehen immer hinaus. Scheitert ein Befehl, nennt die Antwort den <span class='sm-mono'>GRUND</span> (z. B. <span class='sm-mono'>anmeldung</span>, <span class='sm-mono'>keine_antwort</span>).", "<b>Same-value lock:</b> the same mode (<span class='sm-mono'>auto</span>, <span class='sm-mono'>man</span>, <span class='sm-mono'>home</span>, <span class='sm-mono'>eod</span>, <span class='sm-mono'>job</span>) within 60 s is not sent to the mower again; the answer says <span class='sm-mono'>UNVERAENDERT=1</span>. <span class='sm-mono'>start</span> and <span class='sm-mono'>stop</span> are always sent. If a command fails, the answer names the <span class='sm-mono'>GRUND</span> (e.g. <span class='sm-mono'>anmeldung</span>, <span class='sm-mono'>keine_antwort</span>)."),
    "GOOGLE_ANTWORT": ("Chromecast 4 Lox NG lehnt ab: HTTP %d, GRUND=%s.", "Chromecast 4 Lox NG refuses: HTTP %d, GRUND=%s."),
    "GOOGLE_AUSGABE": ("Google-Lautsprecher (Chromecast 4 Lox NG)", "Google speakers (Chromecast 4 Lox NG)"),
    "GOOGLE_FEHLT": ("Chromecast 4 Lox NG fehlt oder ist zu alt (Sprachausgabe für andere Plugins ab 1.3.15): %s antwortet mit HTTP 404 ohne GRUND.", "Chromecast 4 Lox NG is missing or too old (speech output for other plugins from 1.3.15): %s answers HTTP 404 without GRUND."),
    "GOOGLE_GERAET": ("Lautsprecher, Gruppe oder alle", "Speaker, group or all"),
    "GOOGLE_GERAET_PH": ("leer = Standardgerät von Chromecast 4 Lox NG", "empty = default device of Chromecast 4 Lox NG"),
    "GOOGLE_G_DIENST_ANTWORTET_NICHT": ("Der Dienst von Chromecast 4 Lox NG nahm die Ansage nicht rechtzeitig an; sie wurde zurückgezogen.", "The service of Chromecast 4 Lox NG did not accept the announcement in time; it was withdrawn."),
    "GOOGLE_G_DIENST_LAEUFT_NICHT": ("Der Dienst von Chromecast 4 Lox NG läuft nicht.", "The service of Chromecast 4 Lox NG is not running."),
    "GOOGLE_G_FEHLER": ("Interner Fehler in Chromecast 4 Lox NG.", "Internal error in Chromecast 4 Lox NG."),
    "GOOGLE_G_GERAETE_OFFLINE": ("Kein Ziel-Lautsprecher ist mit Chromecast 4 Lox NG verbunden.", "No target speaker is connected to Chromecast 4 Lox NG."),
    "GOOGLE_G_GERAET_UNBEKANNT": ("Diesen Lautsprecher kennt Chromecast 4 Lox NG nicht – Name wie in dessen Geräteliste eintragen.", "Chromecast 4 Lox NG does not know this speaker – enter the name as in its device list."),
    "GOOGLE_G_GRUPPE_UNBEKANNT": ("Diese Gruppe kennt Chromecast 4 Lox NG nicht.", "Chromecast 4 Lox NG does not know this group."),
    "GOOGLE_G_KEINE_GERAETE": ("In Chromecast 4 Lox NG ist kein Lautsprecher eingerichtet.", "No speaker is set up in Chromecast 4 Lox NG."),
    "GOOGLE_G_KEIN_GERAET": ("Kein Lautsprecher angegeben und in Chromecast 4 Lox NG kein Standardgerät gewählt.", "No speaker given and no default device chosen in Chromecast 4 Lox NG."),
    "GOOGLE_G_KEIN_TOKEN_EINGERICHTET": ("In Chromecast 4 Lox NG ist kein Sprechtoken festgelegt.", "No speech token is set in Chromecast 4 Lox NG."),
    "GOOGLE_G_NUR_LOKAL": ("Chromecast 4 Lox NG nimmt nur Aufrufe von diesem LoxBerry (127.0.0.1) an.", "Chromecast 4 Lox NG only accepts calls from this LoxBerry (127.0.0.1)."),
    "GOOGLE_G_SPRECHEN_AUS": ("Die Sprachausgabe für andere Plugins ist in Chromecast 4 Lox NG ausgeschaltet.", "Speech output for other plugins is switched off in Chromecast 4 Lox NG."),
    "GOOGLE_G_STUNDENGRENZE": ("Chromecast 4 Lox NG hat in der letzten Stunde schon so viele Ansagen angenommen, wie dort erlaubt sind.", "Chromecast 4 Lox NG has already accepted as many announcements in the last hour as allowed there."),
    "GOOGLE_G_TOKEN": ("Das Sprechtoken passt nicht zu dem in Chromecast 4 Lox NG.", "The speech token does not match the one in Chromecast 4 Lox NG."),
    "GOOGLE_G_TTS_MODUS": ("In Chromecast 4 Lox NG ist der Ansagemodus „audioserver“ eingestellt.", "Chromecast 4 Lox NG is set to announcement mode “audioserver”."),
    "GOOGLE_HINWEIS": ("Ausgabe über das Plugin <a href='https://github.com/timanders22/LoxBerry-Plugin-Chromecast4lox' target='_blank' rel='noopener'>Chromecast 4 Lox NG</a> (ab 1.3.15) auf diesem LoxBerry an Chromecast- und Nest-Lautsprecher. Dort im Reiter Einstellungen, Abschnitt „Sprachausgabe für andere Plugins“, die Sprachausgabe einschalten und das Sprechtoken festlegen – es ist ein anderes als das von Alexa-NG. Hier wird es wie ein Kennwort behandelt: nie angezeigt, nicht in der Sicherung, leer lassen behält es. IP, Port, Zonen, Lautstärke und Sprache oben gelten für diese Ausgabeart nicht. Fällt Chromecast 4 Lox NG aus, entfällt die Ansage – kein Wiederholen, kein Wechsel auf einen anderen Lautsprecher.", "Output via the plugin <a href='https://github.com/timanders22/LoxBerry-Plugin-Chromecast4lox' target='_blank' rel='noopener'>Chromecast 4 Lox NG</a> (1.3.15 or later) on this LoxBerry to Chromecast and Nest speakers. There, in the tab Settings, section “Speech output for other plugins”, switch speech output on and set the speech token – it is a different one from the Alexa-NG token. Here it is treated like a password: never shown, not in the backup, leaving it empty keeps it. IP, port, zones, volume and language above do not apply to this output type. If Chromecast 4 Lox NG fails, the announcement is dropped – no retry, no switch to another speaker."),
    "GOOGLE_KEINE_ANTWORT": ("Chromecast 4 Lox NG antwortet nicht unter %s (Wartezeit %d s, %s).", "Chromecast 4 Lox NG does not respond at %s (timeout %d s, %s)."),
    "GOOGLE_KEIN_TOKEN": ("Für Google-Lautsprecher (Chromecast 4 Lox NG) ist kein Sprechtoken eingetragen (Reiter Einstellungen, Sprachausgabe).", "No speech token is set for Google speakers (Chromecast 4 Lox NG) (tab Settings, speech output)."),
    "GOOGLE_LAUT": ("Lautstärke der Ansage auf Google-Lautsprechern (0–100)", "Announcement volume on Google speakers (0–100)"),
    "GOOGLE_LAUT_PH": ("leer = Ansagelautstärke von Chromecast 4 Lox NG", "empty = announcement volume of Chromecast 4 Lox NG"),
    "GOOGLE_OHNE_TOKEN": ("Für die Ausgabe über Google-Lautsprecher (Chromecast 4 Lox NG) fehlt das Sprechtoken.", "The speech token is missing for output via Google speakers (Chromecast 4 Lox NG)."),
    "GOOGLE_TOKEN": ("Sprechtoken (Chromecast 4 Lox NG)", "Speech token (Chromecast 4 Lox NG)"),
    "GOOGLE_TOKEN_LOESCHEN": ("Sprechtoken für Google-Lautsprecher löschen", "Delete speech token for Google speakers"),
    "GOOGLE_TOKEN_WIDERSPRUCH": ("Sprechtoken für Google-Lautsprecher: ein neues Token und der Haken „löschen“ zugleich — bitte eines von beiden.", "Speech token for Google speakers: a new token and the box “delete” at the same time — please only one of them."),
    "GOOGLE_UNERWARTET": ("Unerwartete Antwort von Chromecast 4 Lox NG: HTTP %d, %s.", "Unexpected answer from Chromecast 4 Lox NG: HTTP %d, %s."),
    "HTTP_ABGEWIESEN": ("Verbindung abgewiesen", "connection refused"),
    "HTTP_FEHLER": ("Verbindungsfehler", "connection error"),
    "HTTP_ZEIT": ("Zeitüberschreitung", "timeout"),
    "JA": ("ja", "yes"),
    "K_TESTANSAGE": ("Testansage sprechen", "Speak test announcement"),
    "LOG_GELEERT": ("Protokoll geleert.", "Log cleared."),
    "LOG_LEER_LAUF": ("Letzter Lauf des Plugins: %s, Zähler %d.", "Last run of the plugin: %s, counter %d."),
    "LOG_LEER_WARTUNG": ("Protokolliert wird nur bei Wechseln (Zustand, Meldungen, Befehle); die Protokollwartung von LoxBerry räumt die Datei nach einem Neustart oder einer Stunde ab. Ein leerer Reiter ist deshalb kein Fehler.", "Only changes are logged (state, messages, commands); the LoxBerry log maintenance removes the file after a restart or an hour. An empty tab is therefore not an error."),
    "LOG_NICHT_GELEERT": ("Das Protokoll ließ sich nicht leeren: %s", "The log could not be cleared: %s"),
    "MAEHER_ADRESSE_FEHLT": ("Mäher %d: es fehlt die Adresse — ohne sie wird die Zeile nicht angelegt.", "Mower %d: the address is missing — without it the row is not created."),
    "MESSER_NICHT_EINGERICHTET": ("Messerwechsel nicht quittiert: Mäher %s ist nicht eingerichtet.", "Blade change not confirmed: mower %s is not configured."),
    "MESSER_NICHT_ERREICHBAR": ("Messerwechsel nicht quittiert: der Mäher antwortet nicht (%s). Der Nullpunkt bleibt unverändert.", "Blade change not confirmed: the mower does not respond (%s). The zero point is unchanged."),
    "MQTT_RAEUMEN_KEIN_EINGANG": ("MQTT: die zurückbehaltenen Themen unter %s/ ließen sich nicht abräumen — der UDP-Eingang des Gateways ist nicht eingetragen oder nicht erreichbar. Die Deinstallation leert das Präfix mit.", "MQTT: the retained topics under %s/ could not be removed — the UDP input of the gateway is not configured or not reachable. Uninstalling clears the prefix as well."),
    "MQTT_RAEUMEN_OFFEN": ("MQTT: %d Themen unter %s/ stehen noch zurückbehalten im Broker (%s). Die Deinstallation leert sie mit; von Hand: mosquitto_pub -r -n -t &lt;thema&gt;.", "MQTT: %d topics under %s/ are still retained at the broker (%s). Uninstalling clears them as well; manually: mosquitto_pub -r -n -t &lt;topic&gt;."),
    "MQTT_RAEUMEN_OK": ("MQTT: unter %s/ steht beim Broker nichts mehr zurückbehalten (nachgelesen).", "MQTT: nothing is retained any more under %s/ at the broker (checked)."),
    "MQTT_RAEUMEN_UNGEPRUEFT": ("MQTT: die Themen unter %s/ wurden zum Löschen gesendet, der Broker ließ sich aber nicht befragen (Brokerhost, Zugangsdaten in general.json) — nicht nachgelesen. Die Deinstallation leert das Präfix mit.", "MQTT: the topics under %s/ were sent for deletion, but the broker could not be queried (broker host, credentials in general.json) — not verified. Uninstalling clears the prefix as well."),
    "MQTT_WECHSEL_HILFE": ("Beim Ausschalten und bei einem Präfixwechsel räumt das Plugin die zurückbehaltenen Themen unter dem bisherigen Präfix ab und liest beim Broker nach; danach geht der volle Satz hinaus.", "When switched off or when the prefix changes, the plugin removes the retained topics under the previous prefix and checks with the broker; then the full set is sent."),
    "NEIN": ("nein", "no"),
    "NENN_MAEHER": ("Mäher", "Mowers"),
    "NICHTS_GESPEICHERT": ("<b>Es wurde nichts gespeichert.</b> Bitte die markierten Felder berichtigen — die Eingaben stehen wieder im Formular.", "<b>Nothing was saved.</b> Please correct the marked fields — your input is back in the form."),
    "PRUEF_ALEXA_FEHL": ("nein — %s", "no — %s"),
    "PRUEF_ALEXA_JA": ("ja, %s antwortet, das Sprechtoken passt.", "yes, %s responds, the speech token is valid."),
    "PRUEF_ALEXA_LETZTE_FEHL": ("Letzte Ansage vor %s gescheitert: %s", "Last announcement %s ago failed: %s"),
    "PRUEF_ALEXA_LETZTE_OK": ("Letzte Ansage vor %s: gesprochen.", "Last announcement %s ago: spoken."),
    "PRUEF_ALEXA_ZU": ("nur bei geöffnetem Reiter Test geprüft — die Seite mit dem Reiter Test neu laden.", "checked only with the tab Test open — reload the page with the tab Test."),
    "PRUEF_GOOGLE_DIENST_AUS": ("Aber: der Dienst von Chromecast 4 Lox NG läuft nicht – es wird nichts gesprochen.", "But: the service of Chromecast 4 Lox NG is not running – nothing will be spoken."),
    "PRUEF_GOOGLE_FEHL": ("nein — %s", "no — %s"),
    "PRUEF_GOOGLE_JA": ("ja, %s antwortet, das Sprechtoken passt.", "yes, %s responds, the speech token is valid."),
    "PRUEF_GOOGLE_LETZTE_FEHL": ("Letzte Ansage vor %s gescheitert: %s", "Last announcement %s ago failed: %s"),
    "PRUEF_GOOGLE_LETZTE_OK": ("Letzte Ansage vor %s: gesendet (bei Chromecast 4 Lox NG eingereiht).", "Last announcement %s ago: sent (queued at Chromecast 4 Lox NG)."),
    "PRUEF_GOOGLE_SPRECHEN_AUS": ("Aber: die Sprachausgabe für andere Plugins ist dort ausgeschaltet – es wird nichts gesprochen.", "But: speech output for other plugins is switched off there – nothing will be spoken."),
    "PRUEF_GOOGLE_ZU": ("nur bei geöffnetem Reiter Test geprüft — die Seite mit dem Reiter Test neu laden.", "checked only with the tab Test open — reload the page with the tab Test."),
    "PRUEF_GW_AUS": ("Dieses Plugin sendet nicht (MQTT aus). Autostart des Gateways: %s, Gateway-Fassung %s.", "This plugin does not send (MQTT off). Gateway autostart: %s, gateway version %s."),
    "PRUEF_MQTT_EIN_AUS": ("nein — ausgeschaltet; dieses Plugin sendet nichts über MQTT (Reiter MQTT).", "no — switched off; this plugin sends nothing via MQTT (tab MQTT)."),
    "PRUEF_MQTT_EIN_JA": ("ja", "yes"),
    "PRUEF_THEMEN_SENDECODE": ("nein — Themenliste und Sendecode weichen ab. Nur gesendet: %s; nur in der Liste: %s", "no — topic list and sending code differ. Only sent: %s; only listed: %s"),
    "RETAINED": ("retained", "retained"),
    "SICH_ALEXA_TOKEN_DATEI": ("Die Datei trägt ein Sprechtoken für Alexa-NG — das gehört nicht in eine Sicherung. Nichts übernommen; das geltende Token bleibt.", "The file carries a speech token for Alexa-NG — it does not belong in a backup. Nothing applied; the current token stays."),
    "SICH_GANZZAHL": ("%s muss eine ganze Zahl von %d bis %d sein.", "%s must be a whole number from %d to %d."),
    "SICH_GOOGLE_TOKEN_DATEI": ("Die Datei trägt ein Sprechtoken für Google-Lautsprecher (Chromecast 4 Lox NG) — das gehört nicht in eine Sicherung. Nichts übernommen; das geltende Token bleibt.", "The file carries a speech token for Google speakers (Chromecast 4 Lox NG) — it does not belong in a backup. Nothing applied; the current token stays."),
    "SICH_LEER_FELD": ("%s darf nicht leer sein.", "%s must not be empty."),
    "SICH_MAEHER_FELD": ("Mäher %d: %s enthält unzulässige Zeichen oder hat nicht die erwartete Form.", "Mower %d: %s contains invalid characters or does not have the expected form."),
    "SICH_SPAET": ("Nicht in der Sicherung, unverändert: %s (die Sicherung stammt aus einer früheren Fassung).", "Not in the backup, unchanged: %s (the backup comes from an earlier version)."),
    "SICH_THEMA_RAND": ("%s darf nicht mit / beginnen oder enden.", "%s must not start or end with /."),
    "SICH_TOKEN_BLIEB": ("Die Datei trug kein Aktionstoken — das bisherige Token bleibt, die Adressen in Loxone gelten weiter.", "The file carried no action token — the previous token stays, the addresses in Loxone remain valid."),
    "SICH_X3_WARNUNG": ("<b>Achtung:</b> Diese Sicherung würde beim Zurückspielen abgewiesen — beanstandet würden: %s. Sie wird trotzdem vollständig geliefert; bitte vorher in der Oberfläche berichtigen.", "<b>Caution:</b> this backup would be rejected when restored — objections: %s. It is still delivered in full; please correct the settings first."),
    "TESTANSAGE_ANTWORT": ("Antwort von Chromecast 4 Lox NG: %s", "Answer from Chromecast 4 Lox NG: %s"),
    "TESTANSAGE_FEHL": ("Testansage nicht gesprochen: %s", "Test announcement not spoken: %s"),
    "TESTANSAGE_OK": ("Testansage gesendet (Ausgabeart %s).", "Test announcement sent (output type %s)."),
    "TESTANSAGE_TEXT": ("Hallo! Das ist eine Testansage des Rasenmäher-Plugins.", "Hello! This is a test announcement of the lawn mower plugin."),
    "VORLAGE_DEV_FALSCH": ("Für Mäher %s gibt es keine Vorlage — es sind weniger Mäher eingerichtet.", "There is no template for mower %s — fewer mowers are configured."),
    # Kopf wie alle Hausplugins (Entscheidung Nr. 43, 1.1.19): Statusuebersicht ueber den
    # Reitern und gruener Kasten oben im Reiter Einstellungen (WAS_IST_DAS roh, mo_t ohne mw_e).
    "KOPF_ABRUF": ("Abruf", "Polling"),
    "KOPF_OHNE_DIENST": ("ohne Dienst – Cron jede Minute", "no service – cron every minute"),
    "KOPF_LETZTER_LAUF": ("Letzter Lauf", "Last run"),
    "KOPF_NOCH_KEIN_LAUF": ("noch kein Lauf", "no run yet"),
    "KOPF_VOR_S": ("(vor %d s)", "(%d s ago)"),
    "KOPF_MAEHER_ZAHL": ("%d eingerichtet, %d erreichbar", "%d configured, %d reachable"),
    "KOPF_MQTT": ("MQTT", "MQTT"),
    "KOPF_EIN": ("ein", "on"),
    "WAS_IST_DAS": ("<b>Mähroboter mit Robonect-Modul (HX/Hx+) am Loxone Miniserver – ohne Passwort in der Projektdatei.</b> Das Plugin hält die Zugangsdaten zum Mäher auf dem LoxBerry und fragt jede Minute (Cron, ohne eigenen Dienst) Zustand, Akku, Betriebsart, Betriebsstunden, Messer, Temperatur und WLAN ab. Die Werte gehen über einen HTTP-Endpunkt an den Miniserver, auf Wunsch auch per MQTT; Befehle wie Start, Stopp oder Betriebsart nimmt derselbe Endpunkt entgegen, geschützt durch ein Aktionstoken. Fehler, Mähende und fälliger Messerwechsel gehen als Meldung an Loxone, auf Wunsch auch als Ansage.", "<b>Robotic mower with Robonect module (HX/Hx+) on the Loxone Miniserver – without a password in the project file.</b> The plugin keeps the mower credentials on the LoxBerry and polls state, battery, mode, operating hours, blades, temperature and Wi-Fi every minute (cron, no service of its own). The values reach the Miniserver through an HTTP endpoint, and over MQTT on request; commands such as start, stop or mode go through the same endpoint, protected by an action token. Faults, end of mowing and a due blade change are reported to Loxone, and announced on request."),
    "VORLAGE_FUER": ("Vorlage für", "Template for"),
    # Welle Bild 8 (1.1.21): Bild der Bausteine aus dem LoxBerry-Plugins Musterprojekt.
    "BILD_ALT": ("Bausteine des Plugins in Loxone Config – %s",
        "Plugin blocks in Loxone Config – %s"),
    "BILD_UNTERSCHRIFT": ("Seite „%s“ im LoxBerry-Plugins Musterprojekt. Config kürzt lange Bausteinnamen – Namen siehe Tabelle.",
        "Page “%s” in the LoxBerry plugins sample project. Config shortens long block names – see the table for the full names."),
    "MUSTERPROJEKT": ("Die ganze Projektdatei mit allen Plugin-Seiten und Vorlagen: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry-Plugins Musterprojekt</a>",
        "The complete project file with all plugin pages and templates: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry plugins sample project</a>"),
}

# ---- vb_g2_rb (19.10.2026, Gruppe 2 / MQTT, Robonect 1.1.24): Reiter "Einbindung in Loxone" ueber MQTT
# (Entwurf gruppe2_rb 2.4), Weg ueber HTTP zugeklappt; neu gefasst und neu - Liste vb_g2_rb_bau_skripte/g2_daten.py.
_G2_TEXT = {
    "WAS_IST_DAS": ("<b>Mähroboter mit Robonect-Modul (HX/Hx+) am Loxone Miniserver – ohne Passwort in der Projektdatei.</b> Das Plugin hält die Zugangsdaten zum Mäher auf dem LoxBerry und fragt jede Minute (Cron, ohne eigenen Dienst) Zustand, Akku, Betriebsart, Betriebsstunden, Messer, Temperatur und WLAN ab. Die Werte gehen über MQTT an das MQTT-Gateway und von dort an Virtuelle Eingänge im Miniserver; Befehle wie Start, Stopp oder Betriebsart nimmt die Befehlsbrücke über MQTT entgegen (zwei Haken im Reiter MQTT, ab Werk aus). Der Weg über HTTP mit Aktionstoken bleibt für bestehende Anlagen. Fehler, Mähende und fälliger Messerwechsel gehen als Meldung an Loxone, auf Wunsch auch als Ansage.",
        "<b>Robotic mower with Robonect module (HX/Hx+) on the Loxone Miniserver – without a password in the project file.</b> The plugin keeps the mower credentials on the LoxBerry and polls state, battery, mode, operating hours, blades, temperature and Wi-Fi every minute (cron, no service of its own). The values go over MQTT to the MQTT gateway and from there to virtual inputs on the Miniserver; commands such as start, stop or mode are taken over MQTT by the command bridge (two ticks in the MQTT tab, off by default). The HTTP path with action token stays for existing installations. Faults, end of mowing and a due blade change are reported to Loxone, and announced on request."),
    "MQTT_OPTIONAL": ("MQTT – Werte und Befehle",
        "MQTT – values and commands"),
    "TH_BEFEHLE": ("Befehlsdienst: 1 läuft, 0 aus (Haken), -1 gestört; sendet der Befehlsdienst jede Minute, nie zurückbehalten",
        "Command service: 1 running, 0 off (tick), -1 faulty; sent by the command service every minute, never retained"),
    "THEMEN_HILFE": ("Diese Liste entsteht aus derselben Quelle wie der Sendecode — sie kann also nicht veralten. Die Themen unter <span class='sm-mono'>status/</span> gelten für die ganze Anlage, nicht je Mäher; <span class='sm-mono'>status/befehle</span> sendet der Befehlsdienst.",
        "This list comes from the same source as the sending code — it cannot go stale. The topics under <span class='sm-mono'>status/</span> apply to the whole system, not per mower; <span class='sm-mono'>status/befehle</span> is sent by the command service."),
    "EINBINDUNG_IN_LOXONE_SCHRITT_FR_SC": ("Einbindung in Loxone über MQTT — Schritt für Schritt",
        "Loxone integration via MQTT — step by step"),
    "EB_S1": ("Schritt 1: MQTT einschalten",
        "Step 1: switch on MQTT"),
    "EB_S1_TEXT": ("Das LoxBerry-Plugins Musterprojekt holt Werte und Befehle über MQTT: das Plugin sendet an das MQTT-Gateway des LoxBerry, das Gateway gibt die Werte an den Miniserver weiter. Der Haken steht im Reiter „MQTT“ (bei neuen Installationen ab Werk an).",
        "The LoxBerry plugins sample project gets values and commands via MQTT: the plugin sends to the MQTT gateway of the LoxBerry, the gateway passes the values on to the Miniserver. The tick is in the tab “MQTT” (on by default for new installations)."),
    "EB_S1_EIN": ("MQTT ist eingeschaltet – die Werte gehen unter dem Präfix %s hinaus.",
        "MQTT is switched on – the values go out under the prefix %s."),
    "EB_S1_AUS": ("<b>MQTT ist aus</b> – über MQTT kommt am Miniserver nichts an. Im Reiter „MQTT“ den Haken setzen. Bestehende Anlagen können beim Weg über HTTP bleiben (ganz unten).",
        "<b>MQTT is off</b> – nothing arrives at the Miniserver via MQTT. Set the tick in the tab “MQTT”. Existing installations can stay with the HTTP path (at the bottom)."),
    "EB_S2": ("Schritt 2: Das MQTT-Gateway",
        "Step 2: the MQTT gateway"),
    "EB_S2_V2": ("<b>Gateway V2:</b> Unter System → MQTT Gateway → Subscriptions erscheint die Gruppe des Präfixes. Die Datenpunkte der Liste anhaken; die mit [Noncached] markierten zusätzlich als „Noncached“. Kein Datenpunkt braucht „Zurücksetzen nach Senden“.",
        "<b>Gateway V2:</b> Under System → MQTT Gateway → Subscriptions the group of the prefix appears. Tick the data points of the list; the ones marked [Noncached] also as “Noncached”. No data point needs “Reset after send”."),
    "EB_HAKEN_AUF": ("Hakenliste für Gateway V2 (%d Datenpunkte, davon %d Noncached)",
        "Tick list for gateway V2 (%d data points, %d of them noncached)"),
    "EB_NONCACHED": ("[Noncached]",
        "[Noncached]"),
    "EB_NEUSTART": ("Nach einem Neustart des Miniservers fordert die Musterseite „LoxBerry MQTT-Gateway“ einmal alles neu an.",
        "After a restart of the Miniserver the sample page “LoxBerry MQTT-Gateway” requests everything once again."),
    "EB_WEITERE": ("Jeder weitere Mäher sendet unter seiner Nummer: %d Datenpunkte mehr je Mäher, Namen mit der Nummer nach dem Präfix.",
        "Each further mower sends under its number: %d more data points per mower, names with the number after the prefix."),
    "EB_S3": ("Schritt 3: Virtuelle Eingänge anlegen",
        "Step 3: create virtual inputs"),
    "EB_S3_TEXT": ("Je Wert in Loxone Config einen <b>Virtuellen Eingang</b> anlegen (Peripherie → Virtuelle Eingänge), für Text einen <b>Virtuellen Texteingang</b>. Der Name muss genau so heißen, wie das MQTT-Gateway ihn vergibt – den Knopf „Kopieren“ benutzen. Für die Werte gibt es keine Importvorlage.",
        "Create one <b>virtual input</b> per value in Loxone Config (Periphery → Virtual inputs), a <b>virtual text input</b> for text. The name must be exactly the one the MQTT gateway assigns – use the button “Copy”. There is no import template for the values."),
    "EB_T_NAME": ("Name in Loxone",
        "Name in Loxone"),
    "EB_T_THEMA": ("Thema",
        "Topic"),
    "EB_T_BEDEUTUNG": ("Bedeutung",
        "Meaning"),
    "EB_T_BEREICH": ("Bereich / Einheit",
        "Range / unit"),
    "EB_T_ART": ("Art",
        "Kind"),
    "EB_T_MUSTER": ("im Musterprojekt",
        "in the sample project"),
    "EB_ART_ZAHL": ("Zahl (Virtueller Eingang)",
        "Number (virtual input)"),
    "EB_ART_TEXT": ("Text (Virtueller Texteingang)",
        "Text (virtual text input)"),
    "EB_KOPIEREN": ("Kopieren",
        "Copy"),
    "EB_KOPIERT": ("kopiert",
        "copied"),
    "EB_S3_DIGITAL": ("„Als Digitaleingang verwenden“ nicht aktivieren – -1 heißt „nicht bekannt“ und würde sonst zu EIN.",
        "Do not activate “Use as digital input” – -1 means “unknown” and would otherwise become ON."),
    "EB_S3_RECHTE": ("Der LoxBerry-Benutzer am Miniserver braucht Rechte auf diese Eingänge, sonst schreibt das MQTT-Gateway nichts hinein.",
        "The LoxBerry user on the Miniserver needs rights on these inputs, otherwise the MQTT gateway writes nothing into them."),
    "EB_S3_MUSTER": ("Wer die Seiten „Robonect“ und „Robonect Steuerung“ aus dem Musterprojekt kopiert, bekommt die Eingänge mit. „nein“ in der letzten Spalte: das Plugin sendet den Wert, die Musterseiten brauchen ihn nicht.",
        "Whoever copies the pages “Robonect” and “Robonect Steuerung” from the sample project gets the inputs with them. “no” in the last column: the plugin sends the value, the sample pages do not need it."),
    "EB_S4": ("Schritt 4: Ausfallerkennung",
        "Step 4: failure detection"),
    "EB_S4_TEXT": ("Ein Virtueller Eingang <b>behält seinen letzten Wert</b>, wenn nichts mehr kommt — in der App sieht dann alles normal aus. Deshalb sendet das Plugin jede Minute das Lebenszeichen %s (zählt 0 bis 999 um). Diesen Eingang an eine Analogwertvalidierung legen: Tmc 600 s, Min 0, Max 999, an En die Konstante 1, und im Eigenschaftsfenster den Haken bei ‚En‘ entfernen. Steht der LoxBerry, der Minutenlauf oder das MQTT-Gateway, meldet ihr Ausgang E. %s an einem NICHT meldet, wenn der Mäher nicht antwortet. Ein Alter aus einem Zeitstempel braucht es nicht.",
        "A virtual input <b>keeps its last value</b> when nothing arrives any more — in the app everything looks normal then. That is why the plugin sends the sign of life %s every minute (counts 0 to 999 and wraps). Connect this input to an analog value validation: Tmc 600 s, Min 0, Max 999, constant 1 at En, and remove the tick at ‘En’ in the properties. If the LoxBerry, the minute run or the MQTT gateway stands still, its output E reports. %s on a NOT reports when the mower does not answer. An age computed from a timestamp is not needed."),
    "EB_S5": ("Schritt 5: Befehle",
        "Step 5: commands"),
    "EB_S5_TEXT": ("Befehle gehen als <span class='sm-mono'>publish</span> an den UDP-Eingang des MQTT-Gateways; der Befehlsdienst des Plugins führt sie aus und quittiert auf <span class='sm-mono'>…/quittung</span>. Sie wirken nur mit dem Haken „Befehle über MQTT annehmen“ im Reiter „MQTT“; Fahrbefehle brauchen zusätzlich „Mäher über MQTT steuern“. Unter Gateway V1 und V2 ist für Befehle nichts einzutragen.",
        "Commands go as <span class='sm-mono'>publish</span> to the UDP input of the MQTT gateway; the command service of the plugin executes them and acknowledges on <span class='sm-mono'>…/quittung</span>. They only work with the tick “Accept commands via MQTT” in the tab “MQTT”; driving commands also need “Control the mower via MQTT”. Nothing needs to be entered for commands under gateway V1 and V2."),
    "EB_S5_KEINE": ("Die Befehlsbrücke fehlt oder ihre Tabelle ist defekt – Reiter Test.",
        "The command bridge is missing or its table is broken – Test tab."),
    "EB_S5_ANTWORT": ("„abgelehnt: KEINE_ANTWORT“ heißt: der Mäher hat binnen 5 s nicht geantwortet – der Befehl kann trotzdem gewirkt haben.",
        "“abgelehnt: KEINE_ANTWORT” means: the mower did not answer within 5 s – the command may have worked anyway."),
    "EB_S5_MEHR": ("Weitere Mäher: %s (n = 2 bis 9).",
        "Further mowers: %s (n = 2 to 9)."),
    "EB_S5_VORLAGE": ("Die Vorlage legt einen eigenen Virtuellen Ausgang „Rasenmäher MQTT-Befehle“ an (UDP an das Gateway). Das Musterprojekt nutzt statt dessen den gemeinsamen Ausgang „LoxBerry MQTT-Gateway“ mit den Befehlen „Robonect: …“ – beides wirkt gleich; je Befehl nur einen von beiden einfügen.",
        "The template creates its own virtual output “Rasenmäher MQTT-Befehle” (UDP to the gateway). The sample project uses the shared output “LoxBerry MQTT-Gateway” with the commands “Robonect: …” instead – both work the same; add only one of the two per command."),
    "SCHRITT_6_BAUSTEINE": ("Schritt 6: Baustein-Listen der Musterseiten zum 1:1-Nachbauen",
        "Step 6: block lists of the sample pages for a 1:1 rebuild"),
    "EB_HTTP_TITEL": ("Bestehende Anlagen: Weg über HTTP (Virtueller HTTP-Eingang und Ausgang mit Aktionstoken)",
        "Existing installations: path via HTTP (virtual HTTP input and output with action token)"),
    "EB_HTTP_TEXT": ("Bis 1.1.23 war das der Weg dieser Seite. Er bleibt für bestehende Anlagen unverändert; neue Anlagen nehmen MQTT (oben).",
        "Up to 1.1.23 this was the path of this page. It stays unchanged for existing installations; new installations use MQTT (above)."),
    "SCHRITT_1_VIRTUELLER_HTTP_EINGANG_": ("HTTP 1: Virtueller HTTP-Eingang „Rasenmäher“",
        "HTTP 1: virtual HTTP input “Rasenmäher”"),
    "SCHRITT_3_BEFEHLSERKENNUNGEN": ("HTTP 2: Befehlserkennungen",
        "HTTP 2: command recognitions"),
    "SCHRITT_4_STEUERUNG": ("HTTP 3: Steuerung über einen Virtuellen Ausgang mit Aktionstoken",
        "HTTP 3: control via a virtual output with action token"),
    "SCHRITT_5_AUSFALL": ("HTTP 4: Ausfallerkennung",
        "HTTP 4: failure detection"),
    "SCHRITT_7_GEGENPROBE": ("HTTP 5: Gegenprobe",
        "HTTP 5: cross-check"),
    "AUSFALL_TEXT": ("Ein virtueller Eingang <b>behält seinen letzten Wert</b>, wenn nichts mehr kommt — in der App sieht dann alles normal aus. Deshalb liefert das Plugin <span class='sm-mono'>ZAEHLER</span> (zählt bei jedem Minutenlauf eins weiter, 0…999). An eine Analogwertvalidierung gelegt (Tmc 600 s, Min 0, Max 999, an En die Konstante 1, Haken bei ‚En‘ entfernen), meldet ihr Ausgang E einen stehenden Cron-Lauf – unabhängig von jeder Uhr. <span class='sm-mono'>TS</span> ist nur zur Anzeige. <span class='sm-mono'>OK</span> beantwortet etwas anderes: ob der Mäher beim letzten Messen erreichbar war.",
        "A virtual input <b>keeps its last value</b> when nothing arrives any more — in the app everything looks normal then. That is why the plugin delivers <span class='sm-mono'>ZAEHLER</span> (counts up by one on every minute run, 0…999). Connected to an analog value validation (Tmc 600 s, Min 0, Max 999, constant 1 at En, remove the tick at ‘En’), its output E reports a stopped cron run – independent of any clock. <span class='sm-mono'>TS</span> is for display only. <span class='sm-mono'>OK</span> answers something else: whether the mower was reachable at the last measurement."),
    "H_VORLAGE": ("HTTP 6: Alles auf einmal anlegen (Vorlagen für den Weg über HTTP)",
        "HTTP 6: create everything at once (templates for the HTTP path)"),
    "H_VORLAGE_TEXT": ("Für bestehende Anlagen auf dem Weg über HTTP: diese Dateien enthalten alle Werte samt Einheit, Grenzen und Kommentar bzw. die Steuerbefehle mit Aktionstoken. Neue Anlagen brauchen sie nicht. <b>Achtung:</b> Loxone Config legt beim Import neu an und überschreibt nichts — zweimal eingelesen ergibt doppelte Bausteine.",
        "For existing installations on the HTTP path: these files contain all values with unit, limits and comment, or the control commands with action token. New installations do not need them. <b>Caution:</b> Loxone Config creates new objects on import and overwrites nothing — importing twice gives duplicate blocks."),
    "MESSER_STUNDEN_FEHLT": ("Messerwechsel nicht quittiert: der Mäher meldet keine Betriebsstunden. Der Nullpunkt bleibt unverändert.",
        "Blade change not acknowledged: the mower reports no operating hours. The zero point stays unchanged."),
    "PRUEF_NAMEN_JA": ("%d Namen – jeder ist ein Name, unter dem das MQTT-Gateway sendet, und jedes gesendete Thema der Musterseiten steht in der Tabelle.",
        "%d names – each is a name under which the MQTT gateway sends, and every sent topic of the sample pages is in the table."),
    "PRUEF_NAMEN_NEIN": ("Namenstabelle und Sendecode weichen ab – nur in der Tabelle: %s; gesendet, aber nicht in der Tabelle: %s.",
        "Name table and sending code differ – only in the table: %s; sent, but not in the table: %s."),
    "PRUEF_V2_UNKLAR": ("Gateway-Fassung oder subscriptions.json nicht lesbar – nicht feststellbar.",
        "Gateway version or subscriptions.json not readable – cannot be determined."),
    "PRUEF_V2_V1": ("Gateway V1 – es gibt keine Haken; das Abo bringt das Plugin selbst mit.",
        "Gateway V1 – there are no ticks; the plugin brings the subscription itself."),
    "PRUEF_V2_OK": ("Alle %d Datenpunkte der Hakenliste sind angehakt, %d davon Noncached.",
        "All %d data points of the tick list are ticked, %d of them noncached."),
    "PRUEF_V2_FEHLT": ("Nicht angehakt: %s; ohne „Noncached“: %s.",
        "Not ticked: %s; without “Noncached”: %s."),
}
TEXT.update(_G2_TEXT)
# gestrichen (im Bau nirgends mehr gelesen; der Weg ueber HTTP braucht kein Abo im MQTT-Gateway):
for _k in ("SCHRITT_2_ABO", "SCHRITT_2_ABO_TEXT"):
    del TEXT[_k]
_G2_PRUEF = {
    "NAMEN": ("Passt die Namenstabelle zu den gesendeten Themen?",
        "Does the name table match the sent topics?"),
    "V2_HAKEN": ("Sind unter Gateway V2 alle Datenpunkte angehakt?",
        "Are all data points ticked under gateway V2?"),
    "BRUECKE": ("Läuft die Befehlsbrücke?",
        "Is the command bridge running?"),
}
PRUEF.update(_G2_PRUEF)



# Die Baustein-Liste im Reiter Einbindung in Loxone (X-8, Bau vb_g4_rbn, 02.10.2026).
# Die Werte gehen durch vsprintf bzw. werden mit {Bn} nummeriert - kein woertliches
# Prozentzeichen, keine Entitaeten in Werten, die durch mw_e() laufen.
BAUSTEIN = {
    "T_VI_GW": ("Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Rasenmäher (Robonect))",
        "Virtual input (name as assigned by the MQTT gateway, plugin Rasenmäher (Robonect))"),
    "T_VQ_GW": ("Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“)",
        "Virtual output command (template “LoxBerry MQTT-Gateway”)"),
    "T_TEXTEIN": ("Virtueller Texteingang",
        "Virtual text input"),
    "T_VI": ("Virtueller Eingang",
        "Virtual input"),
    "T_TASTER": ("Virtueller Eingang (Taste)",
        "Virtual input (push button)"),
    "T_SCHALTER": ("Virtueller Eingang (Schalter)",
        "Virtual input (switch)"),
    "T_REGLER": ("Virtueller Eingang (Schieberegler)",
        "Virtual input (slider)"),
    "T_KONST": ("Konstante",
        "Constant"),
    "T_STATUS": ("Status",
        "Status"),
    "T_UND": ("UND",
        "AND"),
    "T_ODER": ("ODER",
        "OR"),
    "T_NICHT": ("NICHT",
        "NOT"),
    "T_BENACH": ("Benachrichtigung",
        "Notification"),
    "T_AWV": ("Analogwertvalidierung",
        "Analog value validation"),
    "T_EINVERZ": ("Einschaltverzögerung",
        "On-delay"),
    "T_AUSVERZ": ("Ausschaltverzögerung",
        "Off-delay"),
    "T_GLEICH": ("Gleich",
        "Equal"),
    "T_SCHWELL": ("Schwellwertschalter",
        "Threshold switch"),
    "T_SCHALTUHR": ("Schaltuhr",
        "Schedule"),
    "T_FLANKE": ("Flankenerkennung",
        "Edge detection"),
    "T_FORMEL": ("Formel",
        "Formula"),
    "T_RS": ("RS-Impulsschalter",
        "RS Flipflop"),
    "T_IMPULS": ("Impuls um",
        "Pulse at"),
    "B1_PARAM": ("Zustand: 1 parkt, 2 mäht, 3 sucht die Ladestation, 4 lädt, 7 Fehler; -1 = keine Verbindung oder kein Zustand in der Antwort des Mähers",
        "State: 1 parked, 2 mowing, 3 searching for the charging station, 4 charging, 7 fault; -1 = no connection or no state in the answer of the mower"),
    "B2_PARAM": ("Akku in %; -1 = nicht bekannt",
        "Battery in %; -1 = unknown"),
    "B3_PARAM": ("Fehlercode, 0 = kein Fehler",
        "Fault code, 0 = no fault"),
    "B4_PARAM": ("1 = Meldefenster aktiv (10 Minuten)",
        "1 = notification window active (10 minutes)"),
    "B5_PARAM": ("1 = Push für diese Meldung freigegeben",
        "1 = push enabled for this notification"),
    "B6_PARAM": ("1 = der Mäher hat beim letzten Abruf geantwortet (kommt jede Minute)",
        "1 = the mower answered the last poll (arrives every minute)"),
    "B7_PARAM": ("Lebenszeichen 0 bis 999, zählt bei jedem Minutenlauf des Plugins eins weiter (kommt jede Minute, nie retained)",
        "Sign of life 0 to 999, counts up by one on every minute run of the plugin (arrives every minute, never retained)"),
    "B8_NAME": ("Konstante 1",
        "Konstante 1"),
    "B8_PARAM": ("Wert 1",
        "value 1"),
    "B9_NAME": ("Mäher-Zustand",
        "Mäher-Zustand"),
    "B9_PARAM": ("Zeilen: V1 = -1 und V3 = 1 „antwortet, meldet aber keinen Zustand – Reiter Protokoll im Plugin“; V1 = -1 „keine Verbindung“; V1 = 0 „Status wird ermittelt“; V1 = 1 „parkt, Akku &lt;v2&gt; %“; V1 = 2 „mäht, Akku &lt;v2&gt; %“; V1 = 3 „sucht die Ladestation, Akku &lt;v2&gt; %“; V1 = 4 „lädt, Akku &lt;v2&gt; %“; V1 = 5 „sucht“; V1 = 6 „Abschluss der Bearbeitung“; V1 = 7 „Fehler“; V1 = 8 „Schleifensignal verloren“; V1 = 16 „abgeschaltet“; V1 = 17 „schläft“; V1 = 18 „wird gewartet“; ohne Bedingung „Zustand &lt;v1&gt;“",
        "Lines: V1 = -1 and V3 = 1 “answers, but reports no state – log tab in the plugin”; V1 = -1 “no connection”; V1 = 0 “status being determined”; V1 = 1 “parked, battery &lt;v2&gt; %”; V1 = 2 “mowing, battery &lt;v2&gt; %”; V1 = 3 “searching for the charging station, battery &lt;v2&gt; %”; V1 = 4 “charging, battery &lt;v2&gt; %”; V1 = 5 “searching”; V1 = 6 “finishing the job”; V1 = 7 “fault”; V1 = 8 “loop signal lost”; V1 = 16 “switched off”; V1 = 17 “sleeping”; V1 = 18 “under maintenance”; without condition “state &lt;v1&gt;”"),
    "B9_VERB": ("V1 = {B1}, V2 = {B2}, V3 = {B6}",
        "V1 = {B1}, V2 = {B2}, V3 = {B6}"),
    "B10_NAME": ("Push freigegeben",
        "Push freigegeben"),
    "B10_VERB": ("I1 = {B4}, I2 = {B5}",
        "I1 = {B4}, I2 = {B5}"),
    "B11_NAME": ("Push Rasenmäher",
        "Push Rasenmäher"),
    "B11_VERB": ("Eingang = {B10}",
        "Input = {B10}"),
    "B12_NAME": ("Kein frischer Lauf",
        "Kein frischer Lauf"),
    "B12_VERB": ("I = {B6}",
        "I = {B6}"),
    "B13_NAME": ("Abruf steht",
        "Abruf steht"),
    "B13_PARAM": ("Tmc 600 s (zehn Minutenläufe; einzelne verlorene Meldungen des Gateways melden nichts), Min 0, Max 999 – steht der LoxBerry, der Minutenlauf oder das MQTT-Gateway, bleibt der Zähler stehen; Haken bei ‚En‘ im Eigenschaftsfenster entfernen",
        "Tmc 600 s (ten minute runs; single lost messages of the gateway report nothing), Min 0, Max 999 – if the LoxBerry, the minute run or the MQTT gateway stands still, the counter stops; remove the tick at ‘En’ in the properties"),
    "B13_VERB": ("V = {B7}, En = {B8}",
        "V = {B7}, En = {B8}"),
    "B14_NAME": ("Plugin gestört",
        "Plugin gestört"),
    "B14_VERB": ("I1 = {B12}, I2 = Ausgang E von {B13}",
        "I1 = {B12}, I2 = output E of {B13}"),
    "B15_NAME": ("Mäher-Störung",
        "Mäher-Störung"),
    "B15_VERB": ("I1 = {B3}, I2 = {B14}",
        "I1 = {B3}, I2 = {B14}"),
    "B16_NAME": ("Störung hält an",
        "Störung hält an"),
    "B16_PARAM": ("300 s",
        "300 s"),
    "B16_VERB": ("Eingang = {B15}",
        "Input = {B15}"),
    "B17_NAME": ("Rasenmäher gestört",
        "Rasenmäher gestört"),
    "B17_VERB": ("Eingang = {B16}",
        "Input = {B16}"),
    "B18_NAME": ("Mäher heim",
        "Mäher heim"),
    "B19_NAME": ("Robonect: zur Ladestation",
        "Robonect: zur Ladestation"),
    "B19_PARAM": ("Befehl bei EIN: publish {P}/befehl/heim 1 (nie retain); Betriebsart „Zuhause“ – der Mäher fährt in die Station und bleibt dort, bis „Automatik“ kommt; wirkt nur mit den Haken „Befehle über MQTT annehmen“ und „Mäher über MQTT steuern“ im Plugin (Reiter MQTT)",
        "Command on ON: publish {P}/befehl/heim 1 (never retain); mode “home” – the mower drives into the station and stays there until “Automatik” comes; only works with the ticks “Accept commands via MQTT” and “Control the mower via MQTT” in the plugin (MQTT tab)"),
    "B19_VERB": ("Eingang = {B18}",
        "Input = {B18}"),
    "B20_PARAM": ("1 = mäht gerade; -1 = nicht bekannt (weitere Instanz auf Seite „Robonect Steuerung“)",
        "1 = mowing right now; -1 = unknown (further instance on the page “Robonect Steuerung”)"),
    "B21_PARAM": ("Betriebsstunden gesamt in h; -1 = nicht bekannt",
        "Total operating hours in h; -1 = unknown"),
    "B22_PARAM": ("Reststunden bis zum Messerwechsel in h, -1 = unbekannt",
        "Hours left until the blade change in h, -1 = unknown"),
    "B23_PARAM": ("1 = Messerwechsel fällig; -1 = nicht bekannt",
        "1 = blade change due; -1 = unknown"),
    "B24_NAME": ("Messer",
        "Messer"),
    "B24_PARAM": ("Zeilen: V3 = 1 „Messerwechsel fällig – nach dem Wechsel Taste ‚Messer gewechselt‘“; V2 = -1 „Reststunden unbekannt, &lt;v1&gt; Betriebsstunden gesamt“; ohne Bedingung „Messer noch &lt;v2&gt; h, &lt;v1&gt; Betriebsstunden gesamt“",
        "Lines: V3 = 1 “blade change due – after the change press ‘Messer gewechselt’”; V2 = -1 “hours left unknown, &lt;v1&gt; operating hours in total”; without condition “blades &lt;v2&gt; h left, &lt;v1&gt; operating hours in total”"),
    "B24_VERB": ("V1 = {B21}, V2 = {B22}, V3 = {B23}",
        "V1 = {B21}, V2 = {B22}, V3 = {B23}"),
    "B25_NAME": ("Messerwechsel fällig",
        "Messerwechsel fällig"),
    "B25_PARAM": ("Text: Rasenmäher – Messerwechsel fällig (alle 200 Betriebsstunden); danach in der App „Messer gewechselt“ drücken",
        "Text: lawn mower – blade change due (every 200 operating hours); afterwards press “Messer gewechselt” in the app"),
    "B25_VERB": ("Eingang = {B23}",
        "Input = {B23}"),
    "B26_NAME": ("Messer gewechselt",
        "Messer gewechselt"),
    "B26_PARAM": ("in der App; erst nach dem Wechsel drücken",
        "in the app; press only after the change"),
    "B27_NAME": ("Robonect: Messerwechsel quittieren",
        "Robonect: Messerwechsel quittieren"),
    "B27_PARAM": ("Befehl bei EIN: publish {P}/befehl/messer_gewechselt 1; setzt die Reststunden wieder auf das Intervall (ab Werk 200 h); der Mäher muss dabei erreichbar sein; wirkt mit dem Haken „Befehle über MQTT annehmen“ im Plugin",
        "Command on ON: publish {P}/befehl/messer_gewechselt 1; sets the hours left back to the interval (200 h by default); the mower must be reachable; works with the tick “Accept commands via MQTT” in the plugin"),
    "B27_VERB": ("Eingang = {B26}",
        "Input = {B26}"),
    "B28_PARAM": ("Temperatur am Mäher in °C, -999 = unbekannt",
        "Temperature at the mower in °C, -999 = unknown"),
    "B29_PARAM": ("Luftfeuchte am Mäher in %, -1 = unbekannt",
        "Humidity at the mower in %, -1 = unknown"),
    "B30_PARAM": ("WLAN-Signal in dBm, -999 = unbekannt",
        "Wi-Fi signal in dBm, -999 = unknown"),
    "B31_NAME": ("Mäher-Umgebung",
        "Mäher-Umgebung"),
    "B31_PARAM": ("Zeilen: V1 = -999 und V3 = -999 „keine Klimawerte, kein WLAN-Wert“; V1 = -999 „Klimawerte unbekannt, WLAN &lt;v3&gt; dBm“; V3 = -999 „&lt;v1.1&gt; °C, &lt;v2.0&gt; % Feuchte, WLAN unbekannt“; ohne Bedingung „&lt;v1.1&gt; °C, &lt;v2.0&gt; % Feuchte, WLAN &lt;v3&gt; dBm“",
        "Lines: V1 = -999 and V3 = -999 “no climate values, no Wi-Fi value”; V1 = -999 “climate values unknown, Wi-Fi &lt;v3&gt; dBm”; V3 = -999 “&lt;v1.1&gt; °C, &lt;v2.0&gt; % humidity, Wi-Fi unknown”; without condition “&lt;v1.1&gt; °C, &lt;v2.0&gt; % humidity, Wi-Fi &lt;v3&gt; dBm”"),
    "B31_VERB": ("V1 = {B28}, V2 = {B29}, V3 = {B30}",
        "V1 = {B28}, V2 = {B29}, V3 = {B30}"),
    "B32_PARAM": ("Stunden seit dem letzten Fehler, -1 = keiner",
        "Hours since the last fault, -1 = none"),
    "B33_NAME": ("Letzter Fehler",
        "Letzter Fehler"),
    "B33_PARAM": ("Zeilen: V2 &gt; 0 „Fehler &lt;v2&gt; steht an – Reiter Protokoll im Plugin“; V1 = -1 „kein Fehler vermerkt“; ohne Bedingung „letzter Fehler vor &lt;v1&gt; h“",
        "Lines: V2 &gt; 0 “fault &lt;v2&gt; pending – log tab in the plugin”; V1 = -1 “no fault recorded”; without condition “last fault &lt;v1&gt; h ago”"),
    "B33_VERB": ("V1 = {B32}, V2 = {B3}",
        "V1 = {B32}, V2 = {B3}"),
    "B34_NAME": ("Schleifensignal verloren",
        "Schleifensignal verloren"),
    "B34_PARAM": ("V2 = 8 (offen lassen)",
        "V2 = 8 (leave open)"),
    "B34_VERB": ("V1 = {B1}",
        "V1 = {B1}"),
    "B35_NAME": ("Rasenmäher Schleifensignal",
        "Rasenmäher Schleifensignal"),
    "B35_PARAM": ("Text: Rasenmäher hat das Schleifensignal verloren – Begrenzungsdraht und Ladestation prüfen",
        "Text: lawn mower lost the loop signal – check the boundary wire and the charging station"),
    "B35_VERB": ("Eingang = {B43}",
        "Input = {B43}"),
    "B36_NAME": ("Akku schwach",
        "Akku schwach"),
    "B36_PARAM": ("Ein 19 / Aus 25 (%; schaltet beim Unterschreiten; wie die Plugin-Meldung „Akku unter 20 %“)",
        "On 19 / Off 25 (%; switches when falling below; like the plugin message “battery below 20 %”)"),
    "B36_VERB": ("Eingang = {B2}",
        "Input = {B2}"),
    "B37_NAME": ("Akku schwach beim Mähen",
        "Akku schwach beim Mähen"),
    "B37_PARAM": ("— (nur während der Mäher mäht; beim Heimfahren und Laden still)",
        "— (only while the mower is mowing; silent while returning home and charging)"),
    "B37_VERB": ("I1 = {B36}, I2 = {B20}",
        "I1 = {B36}, I2 = {B20}"),
    "B38_NAME": ("Rasenmäher Akku schwach",
        "Rasenmäher Akku schwach"),
    "B38_PARAM": ("Text: Rasenmäher mäht mit weniger als 20 % Akku",
        "Text: lawn mower is mowing with less than 20 % battery"),
    "B38_VERB": ("Eingang = {B37}",
        "Input = {B37}"),
    "B39_PARAM": ("1 = Test-Push ausgelöst (5 min lang)",
        "1 = test push triggered (for 5 min)"),
    "B40_NAME": ("Test-Push Rasenmäher",
        "Test-Push Rasenmäher"),
    "B40_PARAM": ("Text: Test vom Rasenmäher-Plugin – der Push-Weg funktioniert",
        "Text: test from the lawn mower plugin – the push path works"),
    "B40_VERB": ("Eingang = {B39}",
        "Input = {B39}"),
    "B41_PARAM": ("1 = Ansage im Plugin eingeschaltet",
        "1 = announcement switched on in the plugin"),
    "B42_NAME": ("Meldewege",
        "Meldewege"),
    "B42_PARAM": ("Zeilen: V3 = 0 „Mäher antwortet nicht: &lt;v5&gt; – letzter Plugin-Lauf &lt;v4.t&gt;“; V1 = 1 und V2 = 1 „Push und Ansage an, Plugin-Lauf &lt;v4.t&gt;“; V1 = 1 „Push an, Ansage aus, Plugin-Lauf &lt;v4.t&gt;“; V2 = 1 „Ansage an, Push aus, Plugin-Lauf &lt;v4.t&gt;“; ohne Bedingung „Push und Ansage aus – im Plugin Reiter Einstellungen einschalten“",
        "Lines: V3 = 0 “mower does not answer: &lt;v5&gt; – last plugin run &lt;v4.t&gt;”; V1 = 1 and V2 = 1 “push and announcement on, plugin run &lt;v4.t&gt;”; V1 = 1 “push on, announcement off, plugin run &lt;v4.t&gt;”; V2 = 1 “announcement on, push off, plugin run &lt;v4.t&gt;”; without condition “push and announcement off – switch them on in the plugin, Settings tab”"),
    "B42_VERB": ("V1 = {B5}, V2 = {B41}, V3 = {B6}, V4 = {B7}, V5 = {B44}",
        "V1 = {B5}, V2 = {B41}, V3 = {B6}, V4 = {B7}, V5 = {B44}"),
    "B43_NAME": ("Schleifensignal weg bestätigt",
        "Schleifensignal weg bestätigt"),
    "B43_PARAM": ("120 s (ein kurzer Aussetzer beim Andocken meldet nicht)",
        "120 s (a short dropout while docking does not report)"),
    "B43_VERB": ("Eingang = {B34}",
        "Input = {B34}"),
    "B44_PARAM": ("von Hand anlegen, Name genau so (Name, den das MQTT-Gateway vergibt), „In Visualisierung verwenden“ an; Klartext des Plugins: Zustand des Mähers oder warum er nicht antwortet, z. B. „antwortet gerade nicht“ oder „Benutzer oder Passwort stimmen nicht (HTTP 401)“",
        "create by hand, name exactly like this (the name the MQTT gateway assigns), “Use in visualisation” on; plain text of the plugin: state of the mower or why it does not answer, e.g. “antwortet gerade nicht” or “Benutzer oder Passwort stimmen nicht (HTTP 401)”"),
    "S1_PARAM": ("Betriebsart: 0 Automatik, 1 Manuell, 2 Zuhause, 3 Demo, 4 Auftrag, -1 unbekannt",
        "Mode: 0 automatic, 1 manual, 2 home, 3 demo, 4 job, -1 unknown"),
    "S2_PARAM": ("1 = Timer des Mähers aktiv; -1 = nicht bekannt",
        "1 = mower timer active; -1 = unknown"),
    "S3_NAME": ("Betriebsart",
        "Betriebsart"),
    "S3_PARAM": ("Zeilen: V1 = -1 „Betriebsart unbekannt (keine Verbindung)“; V1 = 0 und V2 = 1 „Automatik, Timer aktiv“; V1 = 0 und V2 = -1 „Automatik, Timer unbekannt“; V1 = 0 „Automatik, kein Timer aktiv“; V1 = 1 „Handbetrieb“; V1 = 2 „Zuhause – bleibt in der Station“; V1 = 3 „Demo“; V1 = 4 „Auftrag“; ohne Bedingung „Betriebsart &lt;v1&gt;“",
        "Lines: V1 = -1 “mode unknown (no connection)”; V1 = 0 and V2 = 1 “automatic, timer active”; V1 = 0 and V2 = -1 “automatic, timer unknown”; V1 = 0 “automatic, no timer active”; V1 = 1 “manual mode”; V1 = 2 “home – stays in the station”; V1 = 3 “demo”; V1 = 4 “job”; without condition “mode &lt;v1&gt;”"),
    "S3_VERB": ("V1 = {S1}, V2 = {S2}",
        "V1 = {S1}, V2 = {S2}"),
    "S4_PARAM": ("1 = mäht gerade (zweite Instanz, auch auf Seite „Robonect“)",
        "1 = mowing right now (second instance, also on the page “Robonect”)"),
    "S5_PARAM": ("1 = lädt gerade; -1 = nicht bekannt",
        "1 = charging right now; -1 = unknown"),
    "S6_PARAM": ("Dauer des laufenden Einsatzes in min; -1 = nicht bekannt",
        "Duration of the current run in min; -1 = unknown"),
    "S7_NAME": ("Einsatz jetzt",
        "Einsatz jetzt"),
    "S7_PARAM": ("Zeilen: V1 = 1 „mäht seit &lt;v2&gt; min“; V3 = 1 „lädt in der Station“; ohne Bedingung „mäht gerade nicht“",
        "Lines: V1 = 1 “mowing for &lt;v2&gt; min”; V3 = 1 “charging in the station”; without condition “not mowing right now”"),
    "S7_VERB": ("V1 = {S4}, V2 = {S6}, V3 = {S5}",
        "V1 = {S4}, V2 = {S6}, V3 = {S5}"),
    "S8_PARAM": ("abgeschlossene Mäheinsätze heute; -1 = Statistik im Plugin aus (Haken „Einsätze und Mähdauer mitzählen“ im Reiter Einstellungen, ab Werk aus)",
        "completed mowing runs today; -1 = statistics off in the plugin (tick “Count runs and mowing time” in the Settings tab, off by default)"),
    "S9_PARAM": ("Mähdauer heute in min; -1 = Statistik aus (gleicher Haken)",
        "mowing time today in min; -1 = statistics off (same tick)"),
    "S10_PARAM": ("abgeschlossene Mäheinsätze diese Woche; -1 = Statistik aus (gleicher Haken)",
        "completed mowing runs this week; -1 = statistics off (same tick)"),
    "S11_PARAM": ("Mähdauer diese Woche in min; -1 = Statistik aus (gleicher Haken)",
        "mowing time this week in min; -1 = statistics off (same tick)"),
    "S12_NAME": ("Mähstatistik",
        "Mähstatistik"),
    "S12_PARAM": ("Zeilen: V1 = -1 „Einsatzstatistik im Plugin aus – Reiter Einstellungen ‚Einsätze und Mähdauer mitzählen‘ anhaken“; ohne Bedingung „heute &lt;v1&gt; Einsätze, &lt;v2&gt; min – diese Woche &lt;v3&gt; Einsätze, &lt;v4&gt; min“",
        "Lines: V1 = -1 “usage statistics off in the plugin – tick ‘Einsätze und Mähdauer mitzählen’ in the Settings tab”; without condition “today &lt;v1&gt; runs, &lt;v2&gt; min – this week &lt;v3&gt; runs, &lt;v4&gt; min”"),
    "S12_VERB": ("V1 = {S8}, V2 = {S9}, V3 = {S10}, V4 = {S11}",
        "V1 = {S8}, V2 = {S9}, V3 = {S10}, V4 = {S11}"),
    "S13_NAME": ("Mähen starten",
        "Mähen starten"),
    "S14_NAME": ("Robonect: Mähen starten",
        "Robonect: Mähen starten"),
    "S14_PARAM": ("Befehl bei EIN: publish {P}/befehl/starten 1 (nie retain); startet sofort einen Mähauftrag; wirkt nur mit den Haken „Befehle über MQTT annehmen“ und „Mäher über MQTT steuern“ im Plugin",
        "Command on ON: publish {P}/befehl/starten 1 (never retain); starts a mowing job at once; only works with the ticks “Accept commands via MQTT” and “Control the mower via MQTT” in the plugin"),
    "S14_VERB": ("Eingang = {S13}",
        "Input = {S13}"),
    "S15_NAME": ("Mähen anhalten",
        "Mähen anhalten"),
    "S15_PARAM": ("in der App; der Mäher bleibt stehen, wo er ist",
        "in the app; the mower stops where it is"),
    "S16_NAME": ("Robonect: Mähen anhalten",
        "Robonect: Mähen anhalten"),
    "S16_PARAM": ("Befehl bei EIN: publish {P}/befehl/anhalten 1; der Mäher bleibt stehen, wo er ist; wirkt nur mit beiden Haken im Plugin",
        "Command on ON: publish {P}/befehl/anhalten 1; the mower stops where it is; only works with both ticks in the plugin"),
    "S16_VERB": ("Eingang = {S15}",
        "Input = {S15}"),
    "S17_NAME": ("Handbetrieb",
        "Handbetrieb"),
    "S18_NAME": ("Robonect: Handbetrieb",
        "Robonect: Handbetrieb"),
    "S18_PARAM": ("Befehl bei EIN: publish {P}/befehl/handbetrieb 1; Betriebsart Manuell – der Mäher mäht nur auf Befehl; wirkt nur mit beiden Haken im Plugin",
        "Command on ON: publish {P}/befehl/handbetrieb 1; mode manual – the mower only mows on command; only works with both ticks in the plugin"),
    "S18_VERB": ("Eingang = {S17}",
        "Input = {S17}"),
    "S19_NAME": ("Regensensor (eigene Quelle)",
        "Regensensor (eigene Quelle)"),
    "S19_PARAM": ("1 = es regnet; im eigenen Projekt die Leitung vom eigenen Regensensor statt dieses Schalters an Nr. 20 legen",
        "1 = it is raining; in your own project connect the line from your own rain sensor to no. 20 instead of this switch"),
    "S20_NAME": ("Rasen nass",
        "Rasen nass"),
    "S20_PARAM": ("Zeit kommt von Nr. 42 (Trocknungszeit aus der App, 0 = 2 Stunden)",
        "Time comes from no. 42 (drying time from the app, 0 = 2 hours)"),
    "S20_VERB": ("Eingang = {S19}, Doff = {S42}",
        "Input = {S19}, Doff = {S42}"),
    "S21_NAME": ("Ruhezeiten Mähen",
        "Ruhezeiten Mähen"),
    "S21_PARAM": ("EIN = nicht mähen: Montag bis Samstag 00:00–07:00 und 20:00–24:00, Sonntag und Feiertag 00:00–24:00",
        "ON = do not mow: Monday to Saturday 00:00–07:00 and 20:00–24:00, Sunday and public holiday 00:00–24:00"),
    "S22_NAME": ("Mähen sperren (von Hand)",
        "Mähen sperren (von Hand)"),
    "S22_PARAM": ("in der App, z. B. bei Gartenfest oder spielenden Kindern",
        "in the app, e.g. for a garden party or children playing"),
    "S23_NAME": ("Sperrgrund",
        "Sperrgrund"),
    "S23_VERB": ("I1 = {S20}, I2 = Ausgang AQ von {S21}",
        "I1 = {S20}, I2 = output AQ of {S21}"),
    "S24_NAME": ("Sperr-Automatik ein",
        "Sperr-Automatik ein"),
    "S24_PARAM": ("in der App; ab Werk aus; im Winter ausschalten",
        "in the app; off by default; switch off in winter"),
    "S25_NAME": ("Mähen gesperrt",
        "Mähen gesperrt"),
    "S25_VERB": ("I1 = {S40}, I2 = {S24}",
        "I1 = {S40}, I2 = {S24}"),
    "S26_NAME": ("Sperre Wechsel",
        "Sperre Wechsel"),
    "S26_PARAM": ("Pd 1 s",
        "Pd 1 s"),
    "S26_VERB": ("Eingang = {S25}",
        "Input = {S25}"),
    "S27_NAME": ("Feierabend",
        "Feierabend"),
    "S27_PARAM": ("in der App; Mäher fährt heim und mäht heute nicht mehr",
        "in the app; the mower goes home and does not mow any more today"),
    "S28_NAME": ("Ende des Tages senden",
        "Ende des Tages senden"),
    "S28_PARAM": ("— (Sperre beginnt oder Taste)",
        "— (lock begins or button)"),
    "S28_VERB": ("I1 = Ausgang On von {S26}, I2 = {S27}",
        "I1 = output On of {S26}, I2 = {S27}"),
    "S29_NAME": ("Robonect: Ende des Tages",
        "Robonect: Ende des Tages"),
    "S29_PARAM": ("Befehl bei EIN: publish {P}/befehl/feierabend 1; der Mäher fährt heim und mäht heute nicht mehr; wirkt nur mit beiden Haken im Plugin",
        "Command on ON: publish {P}/befehl/feierabend 1; the mower goes home and does not mow any more today; only works with both ticks in the plugin"),
    "S29_VERB": ("Eingang = {S48}",
        "Input = {S48}"),
    "S30_NAME": ("Automatik",
        "Automatik"),
    "S30_PARAM": ("in der App; Mäher mäht wieder nach seinem Timer",
        "in the app; the mower mows by its timer again"),
    "S31_NAME": ("Automatik senden",
        "Automatik senden"),
    "S31_PARAM": ("— (Sperre endet und sie hatte heimgeschickt, oder Taste)",
        "— (lock ends and it had sent the mower home, or button)"),
    "S31_VERB": ("I1 = {S45}, I2 = {S30}",
        "I1 = {S45}, I2 = {S30}"),
    "S32_NAME": ("Robonect: Automatik",
        "Robonect: Automatik"),
    "S32_PARAM": ("Befehl bei EIN: publish {P}/befehl/automatik 1; der Mäher mäht wieder nach seinem Timer; wirkt nur mit beiden Haken im Plugin",
        "Command on ON: publish {P}/befehl/automatik 1; the mower mows by its timer again; only works with both ticks in the plugin"),
    "S32_VERB": ("Eingang = {S31}",
        "Input = {S31}"),
    "S33_NAME": ("Sperre jetzt",
        "Sperre jetzt"),
    "S33_PARAM": ("Zeilen: V1 = 0 „Sperr-Automatik aus – der Mäher folgt nur seinem Timer“; V2 = 1 „gesperrt: es regnet“; V3 = 1 „gesperrt: Rasen trocknet nach dem Regen (Trocknungszeit in der App)“; V6 = 1 „gesperrt: Frost (Außentemperatur &lt;v8.1&gt; °C)“; V7 = 1 „gesperrt: Rasen nass nach der Bewässerung (30 Minuten)“; V4 = 1 „gesperrt: Ruhezeit“; V5 = 1 „gesperrt von Hand“; ohne Bedingung „frei – der Mäher mäht nach seinem Timer“",
        "Lines: V1 = 0 “lock automation off – the mower only follows its timer”; V2 = 1 “locked: it is raining”; V3 = 1 “locked: lawn drying after the rain (drying time in the app)”; V6 = 1 “locked: frost (outdoor temperature &lt;v8.1&gt; °C)”; V7 = 1 “locked: lawn wet after the irrigation (30 minutes)”; V4 = 1 “locked: quiet time”; V5 = 1 “locked by hand”; without condition “free – the mower mows by its timer”"),
    "S33_VERB": ("V1 = {S24}, V2 = {S19}, V3 = {S20}, V4 = Ausgang AQ von {S21}, V5 = {S22}, V6 = {S52}, V7 = {S38}, V8 = {S35}",
        "V1 = {S24}, V2 = {S19}, V3 = {S20}, V4 = output AQ of {S21}, V5 = {S22}, V6 = {S52}, V7 = {S38}, V8 = {S35}"),
    "S34_NAME": ("Sperrgrund 2",
        "Sperrgrund 2"),
    "S34_PARAM": ("— (Sperrgrund oder Handsperre; ein ODER hat nur zwei Eingänge)",
        "— (lock reason or manual lock; an OR has only two inputs)"),
    "S34_VERB": ("I1 = {S23}, I2 = {S22}",
        "I1 = {S23}, I2 = {S22}"),
    "S35_NAME": ("Außentemperatur (eigene Quelle)",
        "Außentemperatur (eigene Quelle)"),
    "S35_PARAM": ("Außentemperatur in °C; im eigenen Projekt die Leitung von der eigenen Wetterstation oder dem Außenfühler statt dieses Eingangs an Nr. 36 legen; ohne Quelle steht er auf 0 °C – deshalb sperrt Frost erst mit dem Schalter „Frostsperre an“ (Nr. 51, ab Werk aus)",
        "Outdoor temperature in °C; in your own project connect the line from your own weather station or outdoor sensor to no. 36 instead of this input; without a source it stays at 0 °C – that is why frost only locks with the switch “Frostsperre an” (no. 51, off by default)"),
    "S36_NAME": ("Frost (Mähen)",
        "Frost (Mähen)"),
    "S36_PARAM": ("Ein 5 / Aus 6 (°C; schaltet beim Unterschreiten)",
        "On 5 / Off 6 (°C; switches when falling below)"),
    "S36_VERB": ("Eingang = {S35}",
        "Input = {S35}"),
    "S37_NAME": ("Bewässerung läuft (eigene Quelle)",
        "Bewässerung läuft (eigene Quelle)"),
    "S37_PARAM": ("1 = Bewässerung läuft; im eigenen Projekt den Ausgang „Bewässerung läuft“ bzw. der Pumpe des eigenen Bewässerungsbausteins statt dieses Schalters an Nr. 38 legen",
        "1 = irrigation running; in your own project connect the output “Bewässerung läuft” or the pump of your own irrigation block to no. 38 instead of this switch"),
    "S38_NAME": ("Rasen nass nach Bewässerung (Mähen)",
        "Rasen nass nach Bewässerung (Mähen)"),
    "S38_PARAM": ("1800 s (30 Minuten Abtrocknung)",
        "1800 s (30 minutes drying)"),
    "S38_VERB": ("Eingang = {S37}",
        "Input = {S37}"),
    "S39_NAME": ("Sperrgrund 3 (Mähen)",
        "Sperrgrund 3 (Mähen)"),
    "S39_PARAM": ("— (Sperrgrund 2 oder Frost bei eingeschalteter Frostsperre)",
        "— (lock reason 2 or frost with the frost lock switched on)"),
    "S39_VERB": ("I1 = {S34}, I2 = {S52}",
        "I1 = {S34}, I2 = {S52}"),
    "S40_NAME": ("Sperrgrund 4 (Mähen)",
        "Sperrgrund 4 (Mähen)"),
    "S40_PARAM": ("— (dazu Bewässerung)",
        "— (plus irrigation)"),
    "S40_VERB": ("I1 = {S39}, I2 = {S38}",
        "I1 = {S39}, I2 = {S38}"),
    "S41_NAME": ("Trocknungszeit nach Regen (min)",
        "Trocknungszeit nach Regen (min)"),
    "S41_PARAM": ("Min 0, Max 480, Schritt 10; in der App; 0 = Vorgabe 2 Stunden",
        "Min 0, Max 480, step 10; in the app; 0 = default 2 hours"),
    "S42_NAME": ("Trocknungszeit (s)",
        "Trocknungszeit (s)"),
    "S42_PARAM": ("IF(I1&gt;0;I1*60;7200) – 0 oder kein Wert ergibt 2 Stunden",
        "IF(I1&gt;0;I1*60;7200) – 0 or no value gives 2 hours"),
    "S42_VERB": ("I1 = {S41}",
        "I1 = {S41}"),
    "S43_NAME": ("Hand übernimmt (Mähen)",
        "Hand übernimmt (Mähen)"),
    "S43_PARAM": ("— (Feierabend oder Anhalten von Hand)",
        "— (Feierabend or stopping by hand)"),
    "S43_VERB": ("I1 = {S27}, I2 = {S15}",
        "I1 = {S27}, I2 = {S15}"),
    "S44_NAME": ("Sperre hat heimgeschickt (Mähen)",
        "Sperre hat heimgeschickt (Mähen)"),
    "S44_PARAM": ("Rem EIN; setzt bei Sperrbeginn, löscht bei Feierabend oder Anhalten von Hand (Rücksetzen gewinnt)",
        "Rem ON; sets when a lock begins, clears on Feierabend or stopping by hand (reset wins)"),
    "S44_VERB": ("S = Ausgang On von {S26}, R = {S43}",
        "S = output On of {S26}, R = {S43}"),
    "S45_NAME": ("Automatik nach Sperre (Mähen)",
        "Automatik nach Sperre (Mähen)"),
    "S45_PARAM": ("— (Sperre endet, und sie hatte den Mäher heimgeschickt)",
        "— (lock ends, and it had sent the mower home)"),
    "S45_VERB": ("I1 = Ausgang Off von {S26}, I2 = {S44}",
        "I1 = output Off of {S26}, I2 = {S44}"),
    "S46_NAME": ("Tagesbeginn (Mähen)",
        "Tagesbeginn (Mähen)"),
    "S46_PARAM": ("Zu bestimmter Uhrzeit, 00:05:00",
        "At a certain time, 00:05:00"),
    "S47_NAME": ("Sperre besteht über Mitternacht (Mähen)",
        "Sperre besteht über Mitternacht (Mähen)"),
    "S47_PARAM": ("— (beim Tagesbeginn ist noch gesperrt)",
        "— (the lock still holds at the start of the day)"),
    "S47_VERB": ("I1 = Ausgang Q von {S46}, I2 = {S25}",
        "I1 = output Q of {S46}, I2 = {S25}"),
    "S48_NAME": ("Ende des Tages senden 2 (Mähen)",
        "Ende des Tages senden 2 (Mähen)"),
    "S48_PARAM": ("— (Sperre beginnt, Taste oder Sperre besteht über Mitternacht)",
        "— (lock begins, button or lock holds over midnight)"),
    "S48_VERB": ("I1 = {S28}, I2 = {S47}",
        "I1 = {S28}, I2 = {S47}"),
    "S49_PARAM": ("1 = der Befehlsdienst des Plugins läuft und nimmt {P}/befehl/… an; 0 = „Befehle über MQTT annehmen“ ist im Plugin aus; -1 = soll laufen und steht",
        "1 = the command service of the plugin runs and accepts {P}/befehl/…; 0 = “Accept commands via MQTT” is off in the plugin; -1 = should run and stands still"),
    "S50_NAME": ("Befehlsweg (Mähen)",
        "Befehlsweg (Mähen)"),
    "S50_PARAM": ("Zeilen: V1 = -1 „Befehlsdienst des Plugins steht – im Plugin Reiter Test nachsehen“; V1 = 0 „Befehle über MQTT sind im Plugin aus – Reiter MQTT ‚Befehle über MQTT annehmen‘ und ‚Mäher über MQTT steuern‘ anhaken“; ohne Bedingung „Befehle über MQTT werden angenommen; Fahrbefehle nur mit dem Haken ‚Mäher über MQTT steuern‘“; Visualisierung EIN",
        "Lines: V1 = -1 “command service of the plugin stands still – look at the Test tab in the plugin”; V1 = 0 “commands via MQTT are off in the plugin – tick ‘Befehle über MQTT annehmen’ and ‘Mäher über MQTT steuern’ in the MQTT tab”; without condition “commands via MQTT are accepted; driving commands only with the tick ‘Mäher über MQTT steuern’”; visualisation ON"),
    "S50_VERB": ("V1 = {S49}",
        "V1 = {S49}"),
    "S51_NAME": ("Frostsperre an",
        "Frostsperre an"),
    "S51_PARAM": ("in der App; ab Werk aus; 1 = bei Frost (Nr. 36) nicht mähen – erst einschalten, wenn an Nr. 35 die eigene Außentemperatur angeschlossen ist",
        "in the app; off by default; 1 = do not mow in frost (no. 36) – only switch on once your own outdoor temperature is connected to no. 35"),
    "S52_NAME": ("Frost sperrt (Mähen)",
        "Frost sperrt (Mähen)"),
    "S52_PARAM": ("— (Frost und Frostsperre an)",
        "— (frost and frost lock on)"),
    "S52_VERB": ("I1 = {S36}, I2 = {S51}",
        "I1 = {S36}, I2 = {S51}"),
    "T_TYP": ("Baustein (Typ)",
        "Block (type)"),
    "T_NAME": ("Name",
        "Name"),
    "T_PARAM": ("Parameter",
        "Parameters"),
    "T_VERB": ("Eingänge verbinden mit",
        "Connect inputs to"),
    "P_KEINE": ("—",
        "—"),
    "V_KEINE": ("—",
        "—"),
    "P_FREI": ("Betreff und Text frei",
        "Subject and text as you like"),
    "P_APP": ("in der App",
        "in the app"),
    "UE_WERTE": ("Werte, Meldungen und Messer",
        "Values, notifications and blades"),
    "UE_STEUERUNG": ("Steuerung, Sperren und Befehlsweg",
        "Control, locks and command path"),
    "SO_TITEL": ("So übernehmen Sie diese Seite",
        "How to take over this page"),
    "H_TITEL": ("Hinweise",
        "Notes"),
    "TEXT": ("Von oben nach unten abarbeiten, dann ist die Funktion nachgebaut – eine Zeile ist ein Baustein, so wie auf den Seiten „Robonect“ und „Robonect Steuerung“ im LoxBerry-Plugins Musterprojekt gebaut und verbunden. Die Eingänge {P}_… legt man nach Schritt 3 oben an, die Befehle am Virtuellen Ausgang „LoxBerry MQTT-Gateway“; die übrigen Bausteine findet Loxone Config über die Baustein-Suche (<b>F5</b>). Jede Seite hat ihre eigene Nummerierung.",
        "Work through it from top to bottom and the function is rebuilt – one row is one block, built and connected exactly like this on the pages “Robonect” and “Robonect Steuerung” of the LoxBerry plugins sample project. Create the inputs {P}_… as in step 3 above and the commands at the virtual output “LoxBerry MQTT-Gateway”; Loxone Config finds the other blocks via the block search (<b>F5</b>). Each page has its own numbering."),
    "A_S1": ("Im Plugin Reiter „{L:REITER.EINSTELLUNGEN}“ den Mäher eintragen und speichern. Im Reiter „{L:REITER.MQTT}“ muss „{L:TEXT.ZUSTAND_PER_MQTT_VERFFENTLICHEN}“ angehakt sein (bei neuen Installationen ab Werk an).",
        "In the plugin, enter the mower in the tab “{L:REITER.EINSTELLUNGEN}” and save. In the tab “{L:REITER.MQTT}” “{L:TEXT.ZUSTAND_PER_MQTT_VERFFENTLICHEN}” must be ticked (on by default for new installations)."),
    "A_S2": ("Für die Befehle Nr. 19 und Nr. 27 im Reiter „{L:REITER.MQTT}“ den Haken „{L:BEFEHL.HAKEN_EIN}“ setzen, für Nr. 19 zusätzlich „{L:BEFEHL.HAKEN_STEUERN}“, und speichern – der Befehlsdienst startet sofort.",
        "For the commands no. 19 and no. 27 tick “{L:BEFEHL.HAKEN_EIN}” in the tab “{L:REITER.MQTT}”, for no. 19 also “{L:BEFEHL.HAKEN_STEUERN}”, and save – the command service starts at once."),
    "A_S3": ("In Loxone Config die Eingänge aus Schritt 3 oben anlegen (Peripherie → Virtuelle Eingänge → Virtueller Eingang, Nr. 44 als Virtueller Texteingang), Namen genau wie in der Tabelle – Knopf „{L:TEXT.EB_KOPIEREN}“. „Als Digitaleingang verwenden“ nicht anhaken. Eine Importvorlage gibt es für die Werte nicht; wer die Seite aus dem Musterprojekt kopiert, bekommt die Eingänge mit.",
        "In Loxone Config create the inputs from step 3 above (Periphery → Virtual inputs → Virtual input, no. 44 as virtual text input), names exactly as in the table – button “{L:TEXT.EB_KOPIEREN}”. Do not tick “Use as digital input”. There is no import template for the values; whoever copies the page from the sample project gets the inputs with it."),
    "A_S4": ("Neue Seite „Robonect“ anlegen und die Eingänge Nr. 1–7, 20–23, 28–30, 32, 39, 41 und den Texteingang Nr. 44 aus dem Baum auf die Seite ziehen.",
        "Create a new page “Robonect” and drag the inputs no. 1–7, 20–23, 28–30, 32, 39, 41 and the text input no. 44 from the tree onto the page."),
    "A_S5": ("Die Befehle Nr. 19 und Nr. 27 am Virtuellen Ausgang „LoxBerry MQTT-Gateway“ des Musterprojekts anlegen (Virtueller Ausgang Befehl, Name und Befehl bei EIN wie in der Tabelle, kein Befehl bei AUS). Wer den Ausgang nicht hat, liest statt dessen die Vorlage „{L:BEFEHL.K_VORLAGE}“ aus Schritt 5 ein – dann heißen die Befehle „Rasenmäher … (MQTT)“.",
        "Create the commands no. 19 and no. 27 at the virtual output “LoxBerry MQTT-Gateway” of the sample project (virtual output command, name and command on ON as in the table, no command on OFF). If you do not have this output, import the template “{L:BEFEHL.K_VORLAGE}” from step 5 instead – the commands are then called “Rasenmäher … (MQTT)”."),
    "A_S6": ("Zwei Tasten anlegen (Peripherie → Virtuelle Eingänge → Virtueller Eingang, Eingabeart Taster, „In Visualisierung verwenden“ an): Nr. 18 „Mäher heim“ und Nr. 26 „Messer gewechselt“.",
        "Create two buttons (Periphery → Virtual inputs → Virtual input, input type push button, “Use in visualisation” on): no. 18 “Mäher heim” and no. 26 “Messer gewechselt”."),
    "A_S7": ("Sechs Benachrichtigungen anlegen (Peripherie → Mitteilungen → Benachrichtigung): Nr. 11, 17, 25, 35, 38 und 40, Texte wie in der Tabelle, und auf die Seite ziehen. Jede bekommt genau eine Leitung.",
        "Create six notifications (Periphery → Messages → Notification): no. 11, 17, 25, 35, 38 and 40, texts as in the table, and drag them onto the page. Each one gets exactly one line."),
    "A_S8": ("Die übrigen Bausteine über die Baustein-Suche (F5) setzen, Parameter wie in der Tabelle eintragen und von oben nach unten verbinden. Status-Bausteine: Zeilen in der angegebenen Reihenfolge, die Zeile ohne Bedingung zuletzt; am Status Nr. 42 erscheint der Eingang V5 erst nach einem Klick auf das „+“.",
        "Place the other blocks via the block search (F5), enter the parameters as in the table and connect from top to bottom. Status blocks: lines in the order given, the line without condition last; on the status no. 42 the input V5 only appears after a click on the “+”."),
    "A_S9": ("Im Plugin Reiter „{L:REITER.EINSTELLUNGEN}“ den Haken „{L:TEXT.PUSH_NACHRICHT_AKTIV}“ setzen (für Nr. 11). Dann Reiter „{L:REITER.TEST}“ → Knopf „{L:TEXT.TEST_PUSHNACHRICHT}“: innerhalb von 5 Minuten muss „Test-Push Rasenmäher“ auf dem Handy ankommen.",
        "In the plugin tab “{L:REITER.EINSTELLUNGEN}” tick “{L:TEXT.PUSH_NACHRICHT_AKTIV}” (for no. 11). Then tab “{L:REITER.TEST}” → button “{L:TEXT.TEST_PUSHNACHRICHT}”: within 5 minutes “Test-Push Rasenmäher” must arrive on the phone."),
    "A_S10": ("In Config speichern und in den Miniserver übertragen.",
        "Save in Config and transfer to the Miniserver."),
    "H_AWV": ("Die Analogwertvalidierung bekommt an En die Konstante 1; steht das Lebenszeichen {N:status/zaehler} länger als Tmc, meldet ihr Ausgang E. Config legt den Eingang En negiert an (Haken bei ‚En‘ im Eigenschaftsfenster unter Parameter). Diesen Haken entfernen, sonst kommt die Konstante 1 als 0 an und die Ausfallmeldung löst nie aus.",
        "The analog value validation gets the constant 1 at En; if the sign of life {N:status/zaehler} stands still for longer than Tmc, its output E reports. Config creates input En inverted (tick at ‘En’ in the properties under Parameters). Remove this tick, otherwise constant 1 arrives as 0 and the failure message never triggers."),
    "H_ODER": ("Alle Störungen laufen über ODER in eine Benachrichtigung; ein Benachrichtigungsbaustein bekommt nur eine Quelle.",
        "All faults go through OR into one notification; a notification block gets only one source."),
    "H_PUSH": ("Push Rasenmäher sendet nur, wenn das Meldefenster aktiv UND der Push freigegeben ist (beides stellt das Plugin ein).",
        "Push Rasenmäher only sends when the notification window is active AND the push is enabled (the plugin sets both)."),
    "H_HEIM": ("Mäher heim ist ein Taster in der App und schickt den Befehl „Robonect: zur Ladestation“.",
        "Mäher heim is a push button in the app and sends the command “Robonect: zur Ladestation”."),
    "H_MESSER": ("„Messer gewechselt“ erst nach dem Wechsel drücken – der Befehl setzt die Reststunden wieder auf das Intervall (ab Werk 200 h, im Plugin Reiter „{L:REITER.EINSTELLUNGEN}“ änderbar). Der Mäher muss dabei erreichbar sein und seine Betriebsstunden melden.",
        "Press “Messer gewechselt” only after the change – the command sets the hours left back to the interval (200 h by default, can be changed in the plugin tab “{L:REITER.EINSTELLUNGEN}”). The mower must be reachable and report its operating hours."),
    "H_DOPPELT": ("Doppelte Meldungen vermeiden: Wer Nr. 25 und Nr. 38 nutzt, nimmt im Plugin die Haken „{L:TEXT.MESSERWECHSEL_FLLIG}“ und „{L:TEXT.AKKU_UNTER_20_AUERHALB_DER_STATION}“ heraus; „Push Rasenmäher“ (Nr. 11) meldet dann noch Störung und „{L:TEXT.MHEN_BEENDET}“.",
        "Avoid duplicate notifications: if you use no. 25 and no. 38, untick “{L:TEXT.MESSERWECHSEL_FLLIG}” and “{L:TEXT.AKKU_UNTER_20_AUERHALB_DER_STATION}” in the plugin; “Push Rasenmäher” (no. 11) then still reports faults and “{L:TEXT.MHEN_BEENDET}”."),
    "H_ANZEIGE": ("Temperatur und WLAN sind nur Anzeige – das Plugin kennt dafür keine Warnschwelle. Unbekannt ist dort -999, weil -1 °C und -1 dBm gültige Messwerte wären.",
        "Temperature and Wi-Fi are for display only – the plugin has no warning threshold for them. Unknown is -999 there, because -1 °C and -1 dBm would be valid readings."),
    "H_MINUS1": ("-1 heißt „nicht bekannt“: der Mäher antwortet nicht oder hat das Feld nicht geliefert. Die Eingänge deshalb analog lassen.",
        "-1 means “unknown”: the mower does not answer or did not deliver the field. Therefore leave the inputs analog."),
    "H_SCHLEIFE": ("Die Schleifensignal-Meldung (Nr. 35) kommt erst, wenn der Zustand 8 länger als 120 s ansteht (Nr. 43) – ein kurzer Aussetzer beim Andocken meldet nicht.",
        "The loop signal notification (no. 35) only comes when state 8 lasts longer than 120 s (no. 43) – a short dropout while docking does not report."),
    "ERLAEUTERUNG": ("<b>Zu den Eingängen und Befehlen:</b> Die Namen stehen hier so, wie das MQTT-Gateway sie für Mäher 1 vergibt (Präfix aus dem Reiter „{L:REITER.MQTT}“). Für einen weiteren Mäher steht seine Nummer nach dem Präfix (z. B. {N:2/code}); seine Befehle heißen {P}/befehl/2/… .",
        "<b>On the inputs and commands:</b> The names appear here exactly as the MQTT gateway assigns them for mower 1 (prefix from the tab “{L:REITER.MQTT}”). For a further mower its number follows the prefix (e.g. {N:2/code}); its commands are called {P}/befehl/2/… ."),
    "B_S1": ("Eingänge wie auf Seite „Robonect“ (Schritt 3 oben). Die Werte Nr. 8–11 zählt das Plugin nur mit dem Haken „{L:TEXT.STAT_EIN}“ im Reiter „{L:REITER.EINSTELLUNGEN}“ (ab Werk aus); ohne ihn senden sie -1, und der Status Nr. 12 sagt es.",
        "Inputs as on the page “Robonect” (step 3 above). The plugin only counts the values no. 8–11 with the tick “{L:TEXT.STAT_EIN}” in the tab “{L:REITER.EINSTELLUNGEN}” (off by default); without it they send -1, and the status no. 12 says so."),
    "B_S2": ("Neue Seite „Robonect Steuerung“ anlegen. Die Eingänge Nr. 1, 2, 4–6, 8–11 und 49 ziehen (Nr. 4 {N:maeht} ein zweites Mal – er steht auch auf Seite „Robonect“). Am Ausgang „LoxBerry MQTT-Gateway“ die Befehle Nr. 14, 16, 18, 29 und 32 anlegen (Name und Befehl wie in der Tabelle); jeder Befehl steht nur einmal im Projekt.",
        "Create a new page “Robonect Steuerung”. Drag the inputs no. 1, 2, 4–6, 8–11 and 49 ({N:maeht} a second time – it is also on the page “Robonect”). At the output “LoxBerry MQTT-Gateway” create the commands no. 14, 16, 18, 29 and 32 (name and command as in the table); each command appears only once in the project."),
    "B_S3": ("Virtuelle Eingänge anlegen (Peripherie → Virtuelle Eingänge, „In Visualisierung verwenden“ an): Tasten (Eingabeart Taster) Nr. 13, 15, 17, 27 und 30; Schalter (Eingabeart Schalter) Nr. 19, 22, 24, 37 und 51; Nr. 35 als Virtueller Eingang (analog); Nr. 41 als Schieberegler (Min 0, Max 480, Schritt 10). Ein Virtueller Eingang hat keinen Startwert – deshalb rechnet die Formel Nr. 42 „0 oder kein Wert“ als 2 Stunden.",
        "Create virtual inputs (Periphery → Virtual inputs, “Use in visualisation” on): push buttons (input type push button) no. 13, 15, 17, 27 and 30; switches (input type switch) no. 19, 22, 24, 37 and 51; no. 35 as virtual input (analog); no. 41 as slider (Min 0, Max 480, step 10). A virtual input has no start value – that is why the formula no. 42 counts “0 or no value” as 2 hours."),
    "B_S4": ("Eigene Quellen: Regensensor (Loxone Wetterstation, Regensensor an einem Digitaleingang, Ecowitt über die Ecowitt-Weiche mit Schwellwertschalter auf die Regenrate) an Nr. 20 und an Nr. 33 V2 legen und den Schalter Nr. 19 löschen; ohne Regensensor bleibt Nr. 19 als Handschalter „es regnet“. Außentemperatur an Nr. 36 und Nr. 33 V8 statt Nr. 35, „Bewässerung läuft“ an Nr. 38 statt Nr. 37. Erst mit eigener Außentemperatur „Frostsperre an“ (Nr. 51) einschalten – ohne Quelle steht Nr. 35 auf 0 °C. Schaltuhr Nr. 21: Doppelklick, EIN-Zeiten wie in der Tabelle; die Feiertage kommen aus dem Loxone-Kalender (Betriebsarten).",
        "Own sources: connect your rain sensor (Loxone weather station, rain sensor on a digital input, Ecowitt via the Ecowitt-Weiche with a threshold switch on the rain rate) to no. 20 and to no. 33 V2 and delete the switch no. 19; without a rain sensor no. 19 stays as a manual “it is raining” switch. Outdoor temperature to no. 36 and no. 33 V8 instead of no. 35, “irrigation running” to no. 38 instead of no. 37. Only switch on “Frostsperre an” (no. 51) with your own outdoor temperature – without a source no. 35 stays at 0 °C. Schedule no. 21: double-click, ON times as in the table; the holidays come from the Loxone calendar (operating modes)."),
    "B_S5": ("Übrige Bausteine setzen (F5) und von oben nach unten verbinden: Ausschaltverzögerung Nr. 20 (Zeit von Nr. 42 an Doff) und Nr. 38 (1800 s), Schwellwertschalter Nr. 36, Formel Nr. 42, acht ODER, vier UND, Flankenerkennung Nr. 26 (Pd 1 s), RS-Impulsschalter Nr. 44 (Remanenz an), Impuls um Nr. 46 (00:05), Status-Zeilen wie angegeben. Ein ODER hat nur zwei Eingänge: die Sperrgründe laufen über Nr. 23, 34, 39 und 40. Den Ausgang AQ der Schaltuhr Nr. 21 an Nr. 23 I2 und an Nr. 33 V4 legen. Am Status Nr. 33 erscheinen die Eingänge ab V5 erst nach einem Klick auf das „+“.",
        "Place the other blocks (F5) and connect from top to bottom: off-delay no. 20 (time from no. 42 at Doff) and no. 38 (1800 s), threshold switch no. 36, formula no. 42, eight OR, four AND, edge detection no. 26 (Pd 1 s), RS flipflop no. 44 (remanence on), pulse at no. 46 (00:05), status lines as given. An OR has only two inputs: the lock reasons run through no. 23, 34, 39 and 40. Connect output AQ of the schedule no. 21 to no. 23 I2 and to no. 33 V4. On the status no. 33 the inputs from V5 only appear after a click on the “+”."),
    "B_S6": ("In Config speichern und übertragen. In der App „Sperr-Automatik ein“ einschalten.",
        "Save in Config and transfer. Switch on “Sperr-Automatik ein” in the app."),
    "B_S7": ("Probe: in der App „Regensensor (eigene Quelle)“ ein → der Mäher bekommt „Ende des Tages“ und fährt heim, „Sperre jetzt“ zeigt „gesperrt: es regnet“. Wieder aus → „Rasen trocknet“, nach der Trocknungszeit (ab Werk 2 h) „Automatik“. Im Plugin Reiter „{L:REITER.LOG}“ stehen beide Befehle („über MQTT“).",
        "Check: switch on “Regensensor (eigene Quelle)” in the app → the mower gets “Ende des Tages” and goes home, “Sperre jetzt” shows “locked: it is raining”. Off again → “lawn drying”, after the drying time (2 h by default) “Automatik”. Both commands appear in the plugin tab “{L:REITER.LOG}” (“über MQTT”)."),
    "H_SPERREN": ("Jede Sperre (Regen und Trocknungszeit danach, Ruhezeit, Bewässerung und 30 Minuten danach, Frost mit „Frostsperre an“, von Hand) schickt bei ihrem Beginn einmal „Ende des Tages“. Am Ende kommt „Automatik“ nur, wenn die Sperre den Mäher heimgeschickt hat und seitdem niemand „Feierabend“ oder „Mähen anhalten“ gedrückt hat (Nr. 43–45). „Automatik“ oder „Mähen starten“ von Hand während einer Sperre bleibt erlaubt – Hand geht vor.",
        "Each lock (rain and the drying time afterwards, quiet time, irrigation and 30 minutes afterwards, frost with “Frostsperre an”, by hand) sends “Ende des Tages” once when it begins. At its end “Automatik” only comes if the lock had sent the mower home and nobody has pressed “Feierabend” or “Mähen anhalten” since (no. 43–45). “Automatik” or “Mähen starten” by hand during a lock stays allowed – hand comes first."),
    "H_MITTERNACHT": ("„Ende des Tages“ gilt nur bis Mitternacht. Besteht die Sperre um 00:05 noch (Ruhezeit am Sonntag, Regen in der Nacht), geht es noch einmal hinaus (Nr. 46–48).",
        "“Ende des Tages” only holds until midnight. If the lock still holds at 00:05 (quiet time on Sunday, rain at night), it goes out once more (no. 46–48)."),
    "H_FROST": ("Frost sperrt nur mit dem Schalter „Frostsperre an“ (Nr. 51, ab Werk aus): ohne eigene Außentemperatur an Nr. 35 stünde dort 0 °C, und die Sperre griffe dauernd.",
        "Frost only locks with the switch “Frostsperre an” (no. 51, off by default): without your own outdoor temperature at no. 35 it would read 0 °C, and the lock would hold all the time."),
    "H_WINTER": ("Im Winter „Sperr-Automatik ein“ ausschalten – sonst weckt das „Automatik“ um 7 Uhr den eingewinterten Mäher, wenn die Sperre ihn heimgeschickt hatte.",
        "In winter switch off “Sperr-Automatik ein” – otherwise the “Automatik” at 7 am wakes the mower in its winter storage if the lock had sent it home."),
    "H_ZEITEN": ("Trocknungszeit (Nr. 41, in der App; 0 = 2 Stunden), Abtrocknung nach der Bewässerung (Nr. 38) und Ruhezeiten (Nr. 21) sind Vorschläge – nach eigener Erfahrung und Ortssatzung ändern. Die Zeiten der Schaltuhr sind die gängige Regel für Wohngebiete, kein Rechtsrat.",
        "Drying time (no. 41, in the app; 0 = 2 hours), drying after the irrigation (no. 38) and quiet times (no. 21) are suggestions – change them to your own experience and local bylaws. The schedule times are the usual rule for residential areas, not legal advice."),
    "H_ANHALTEN": ("„Mähen anhalten“ lässt den Mäher stehen, wo er ist; heim schickt ihn „Feierabend“ oder „Mäher heim“ (Seite „Robonect“).",
        "“Mähen anhalten” leaves the mower where it is; “Feierabend” or “Mäher heim” (page “Robonect”) sends it home."),
    "H_STATISTIK": ("Die Mähstatistik zeigt „Einsatzstatistik im Plugin aus“, solange im Plugin der Haken „{L:TEXT.STAT_EIN}“ fehlt – die vier Werte sind dann -1.",
        "The mowing statistics show “usage statistics off”, as long as the tick “{L:TEXT.STAT_EIN}” is missing in the plugin – the four values are -1 then."),
    "H_BEFEHLE": ("Befehle wirken nur mit dem Haken „{L:BEFEHL.HAKEN_EIN}“, Fahrbefehle zusätzlich mit „{L:BEFEHL.HAKEN_STEUERN}“ (Reiter „{L:REITER.MQTT}“). Der Status Nr. 50 zeigt, ob der Befehlsdienst läuft. Denselben Fahrbefehl nimmt das Plugin nicht sofort noch einmal an: Starten und Anhalten 10 s, Betriebsarten 60 s.",
        "Commands only work with the tick “{L:BEFEHL.HAKEN_EIN}”, driving commands also with “{L:BEFEHL.HAKEN_STEUERN}” (tab “{L:REITER.MQTT}”). The status no. 50 shows whether the command service runs. The plugin does not accept the same driving command again at once: start and stop 10 s, modes 60 s."),
}


# vb_g2_rb (19.10.2026, Gruppe 2 / MQTT): Abschnitt [BEFEHL] der Befehlsbruecke - Haken, Meldungen, Kacheln
# (bin/befehle_zuordnung.php "kachel"), Befehlstabelle im Reiter Einbindung, Abschnitt im Reiter Test.
BEFEHL = {
    "H_BEFEHLE": ("Befehle aus Loxone über MQTT",
        "Commands from Loxone via MQTT"),
    "HAKEN_EIN": ("Befehle über MQTT annehmen",
        "Accept commands via MQTT"),
    "HAKEN_STEUERN": ("Mäher über MQTT steuern (Starten, Anhalten, Betriebsart)",
        "Control the mower via MQTT (start, stop, mode)"),
    "HAKEN_HILFE": ("Jeder im Heimnetz kann über den UDP-Eingang des MQTT-Gateways Befehle senden. Fahrbefehle brauchen zusätzlich „Mäher über MQTT steuern“. Ab Werk ist beides aus; der Befehlsdienst startet beim Speichern.",
        "Anyone on the home network can send commands via the UDP input of the MQTT gateway. Driving commands also need “Control the mower via MQTT”. Both are off by default; the command service starts when you save."),
    "HAKEN_MQTT_AUS": ("Befehle über MQTT brauchen „Zustand per MQTT veröffentlichen“ – ohne MQTT nimmt der Befehlsdienst nichts an.",
        "Commands via MQTT need “Publish state via MQTT” – without MQTT the command service accepts nothing."),
    "M_EIN": ("Befehlsdienst gestartet.",
        "Command service started."),
    "M_AUS": ("Befehlsdienst angehalten.",
        "Command service stopped."),
    "M_START_FEHL": ("Der Befehlsdienst ließ sich nicht starten: %s – der Minutenlauf versucht es erneut.",
        "The command service could not be started: %s – the minute run tries again."),
    "M_STOP_FEHL": ("Der Befehlsdienst ließ sich nicht anhalten: %s",
        "The command service could not be stopped: %s"),
    "K_STARTEN": ("Mähen starten",
        "Start mowing"),
    "K_ANHALTEN": ("Mähen anhalten",
        "Stop mowing"),
    "K_AUTOMATIK": ("Automatik",
        "Automatic"),
    "K_HEIM": ("zur Ladestation",
        "to the charging station"),
    "K_FEIERABEND": ("Ende des Tages",
        "End of day"),
    "K_HANDBETRIEB": ("Handbetrieb",
        "Manual mode"),
    "K_MESSER": ("Messerwechsel quittieren",
        "Acknowledge blade change"),
    "K_VORLAGE": ("Vorlage MQTT-Befehle",
        "Template MQTT commands"),
    "T_BEDEUTUNG": ("Bedeutung",
        "Meaning"),
    "T_TITEL": ("Titel in der Vorlage",
        "Title in the template"),
    "T_THEMA": ("Thema",
        "Topic"),
    "T_LOXONE": ("Befehl bei EIN",
        "Command on ON"),
    "T_EINGREIFEND": ("Fahrbefehl",
        "Driving command"),
    "T_SPERRE": ("Sperrzeit",
        "Lock time"),
    "T_QUITTUNG": ("Quittung",
        "Acknowledgement"),
    "Q_AUSGEFUEHRT": ("angenommen = der Mäher hat den Befehl bestätigt",
        "angenommen = the mower confirmed the command"),
    "H_TEST": ("Befehlsbrücke",
        "Command bridge"),
    "H_PRUEFEN": ("Einrichtungsprüfung (befehlsbruecke.php --pruefen)",
        "Setup check (befehlsbruecke.php --pruefen)"),
    "P_FEHLT": ("Die Befehlsbrücke fehlt (bin/befehlsbruecke.php).",
        "The command bridge is missing (bin/befehlsbruecke.php)."),
    "P_DEFEKT": ("Tabelle der Befehlsbrücke defekt: %s",
        "Table of the command bridge broken: %s"),
    "P_AUS": ("aus – Haken „Befehle über MQTT annehmen“ im Reiter MQTT.",
        "off – tick “Accept commands via MQTT” in the MQTT tab."),
    "P_MQTT_AUS": ("aus – MQTT ist ausgeschaltet.",
        "off – MQTT is switched off."),
    "P_STEHT": ("soll laufen und steht – der Minutenlauf startet sie neu (höchstens alle 10 Minuten).",
        "should run and stands still – the minute run restarts it (at most every 10 minutes)."),
    "P_HAENGT": ("läuft, hat aber seit %d s nichts geschrieben.",
        "runs, but has written nothing for %d s."),
    "P_OHNE_ABO": ("läuft ohne Abo beim Broker: %s",
        "runs without subscription at the broker: %s"),
    "P_LAEUFT": ("läuft seit %s; angenommen %d, abgelehnt %d, verworfen %d.",
        "running since %s; accepted %d, rejected %d, discarded %d."),
    "P_LETZTER": ("Zuletzt: %s – %s (vor %d s).",
        "Last: %s – %s (%d s ago)."),
    "P_VERWORFEN": ("Verworfen werden zurückbehaltene Befehle: in Loxone „retain“ durch „publish“ ersetzen.",
        "Retained commands are discarded: replace “retain” by “publish” in Loxone."),
}

def ansage_abschnitt(sprache):
    """Der Abschnitt [ANSAGE] der gemeinsamen Sprachausgabe (Nr. 36 b) - EINE Quelle:
    Werkzeuge/gemeinsam_pruefen.py baut ihn aus Werkzeuge/gemeinsam/sprachausgabe_texte.json und
    haelt ihn spaeter gegen die .ini. Gesucht wird aufwaerts vom Ablageort dieses Erzeugers."""
    hier = os.path.dirname(os.path.abspath(__file__))
    while True:
        for w in (hier, os.path.join(hier, "Werkzeuge")):
            if os.path.isfile(os.path.join(w, "gemeinsam_pruefen.py")) and \
                    os.path.isfile(os.path.join(w, "gemeinsam", "sprachausgabe_texte.json")):
                sys.path.insert(0, w)
                import gemeinsam_pruefen
                return gemeinsam_pruefen.ini_abschnitt(sprache)
        oben = os.path.dirname(hier)
        if oben == hier:
            raise SystemExit("Werkzeuge/gemeinsam_pruefen.py nicht gefunden - es wurde nichts geschrieben.")
        hier = oben


def zeilen(abschnitt, tabelle, index):
    out = ["[%s]" % abschnitt]
    for schluessel in sorted(tabelle):
        wert = tabelle[schluessel][index]
        if '"' in wert:
            raise SystemExit("ABBRUCH: doppeltes Anfuehrungszeichen in %s.%s - "
                             "HTML-Attribute einfach quoten." % (abschnitt, schluessel))
        out.append('%s = "%s"' % (schluessel, wert))
    out.append("")
    return out


def bauen(index, sprache):
    kopf = [
        "; Robonect - %s" % ("Deutsch" if index == 0 else "English"),
        ";",
        "; ERZEUGT von Werkzeuge/mo_sprache_erzeugen.py - nicht von Hand aendern.",
        "; Beide Sprachdateien kommen aus EINER Quelle; getrennt gepflegt laufen",
        "; sie auseinander, und der Fehler faellt erst am Bildschirm auf.",
        ";",
        "; Jeder Wert steht in doppelten Anfuehrungszeichen: bei parse_ini_file",
        "; beginnt mit ; ein Kommentar, und jede HTML-Entitaet endet auf ein",
        "; Semikolon. Innerhalb eines Wertes darf kein doppeltes",
        "; Anfuehrungszeichen stehen - HTML-Attribute deshalb einfach quoten:",
        "; <span class='sm-mono'>.",
        "",
    ]
    teile = kopf
    teile += zeilen("REITER", REITER, index)
    teile += zeilen("LEGENDE", LEGENDE, index)
    teile += ["[ALLGEMEIN]", ""]
    teile += zeilen("PRUEF", PRUEF, index)
    teile += zeilen("TEXT", TEXT, index)
    teile += zeilen("BAUSTEIN", BAUSTEIN, index)
    # vb_g2_rb (19.10.2026): Abschnitt der Befehlsbruecke.
    teile += zeilen("BEFEHL", BEFEHL, index)
    # vb_st2_ro: der Abschnitt der gemeinsamen Sprachausgabe, wortgleich aus der Quelle.
    teile += ansage_abschnitt("de" if index == 0 else "en").rstrip("\n").split("\n")
    # LF seit der Hausregel vom 13.09.2026; bis dahin CRLF.
    return "\n".join(teile) + "\n"


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Aufruf: mo_sprache_erzeugen.py <Plugin-Ordner>")
    ordner = os.path.join(sys.argv[1], "templates", "lang")
    if not os.path.isdir(ordner):
        raise SystemExit("Nicht gefunden: " + ordner)
    # Werkzeug-S4 (02.10.2026): erst BEIDE Dateien bauen und pruefen, dann
    # schreiben. Bis dahin stand language_de.ini schon auf der Platte, wenn
    # zeilen() beim Englischen an einem geraden Anfuehrungszeichen abbrach,
    # und die CRLF-Wache schlug erst NACH dem Schreiben an.
    fertig = []
    for index, name in ((0, "language_de.ini"), (1, "language_en.ini")):
        inhalt = bauen(index, name).encode("utf-8")
        # Die Wache ist mitgedreht: sie schlug frueher bei reinen LF an,
        # jetzt bei CRLF. Eine Wache, die nach der Umstellung noch das
        # alte Ziel bewacht, haelt den eigenen Erzeuger an.
        if inhalt.count(b"\r\n"):
            raise SystemExit("ABBRUCH: CRLF in " + name)
        fertig.append((name, inhalt))
    # Die Sprachwache prueft je Datei erst beim Schreiben - vorab ueber beide,
    # damit ein Abbruch bei der zweiten die erste nicht schon ersetzt hat (die
    # Meldung "werden neu gefasst" kann dadurch zweimal erscheinen).
    for name, inhalt in fertig:
        sprachwache.pruefen(os.path.join(ordner, name), inhalt.decode("utf-8"))
    for name, inhalt in fertig:
        pfad = os.path.join(ordner, name)
        alt = open(pfad, "rb").read() if os.path.isfile(pfad) else b""
        # BINAER schreiben: open(p, "w") uebersetzt unter Windows still jedes
        # \n zu \r\n und macht aus CRLF ein CRCRLF.
        with open(pfad, "wb") as fh:
            fh.write(inhalt)
        crlf = inhalt.count(b"\r\n")
        lf = inhalt.count(b"\n") - crlf
        print("  %-18s %6d Byte  (vorher %6d)  CRLF=%d LF=%d  Schluessel=%d"
              % (name, len(inhalt), len(alt), crlf, lf,
                 len(REITER) + len(LEGENDE) + len(PRUEF) + len(TEXT)
                 + len(BAUSTEIN) + len(BEFEHL)))


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
    main()
