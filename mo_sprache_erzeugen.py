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
}

# ---------------------------------------------------------------- TEXT
# Alles, was aus 1.0.13 weiterlebt, steht hier unveraendert; die toten
# Schluessel sind entfallen, die neuen kommen dazu.
TEXT = {
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
    "SCHRITT_6_BAUSTEINE": ("Schritt 6: Komplette Baustein-Liste zum 1:1-Nachbauen",
                            "Step 6: Complete block list for a 1:1 rebuild"),
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
    "BAUSTEIN":            ("Baustein", "Block"),
    "EINSTELLUNG":         ("Einstellung", "Setting"),
    "EINGNGE":             ("Eingänge", "Inputs"),
    "BEDEUTUNG":           ("Bedeutung", "Meaning"),
    "BEFEHLSERKENNUNG":    ("Befehlserkennung", "Command recognition"),
    "BEFEHL_BEI_EIN":      ("Befehl bei EIN", "Command on ON"),
    "WIRKUNG":             ("Wirkung", "Effect"),
    "THEMA":               ("Thema", "Topic"),
    "ZEITPUNKT":           ("Zeitpunkt", "Time"),
    "CODE_2":              ("Code", "Code"),
    "ABFRAGEZYKLUS":       ("Abfragezyklus", "Polling interval"),
    "30_SEKUNDEN":         ("30 Sekunden", "30 seconds"),
    "ABFRAGE_ALLE_30_S":   ("(Abfrage alle 30 s)", "(polled every 30 s)"),
    "ADRESSE_VIRTUELLER_AUSGANG": ("Adresse (Virtueller Ausgang)", "Address (virtual output)"),
    "MHER_2":              ("(Mäher 2:", "(mower 2:"),
    "OHNE":                ("ohne", "without"),
    "BENUTZER_UND_PASSWORT": ("Benutzer und Passwort!", "user and password!"),
    "EINE":                ("eine", "one"),
    "PORT":                ("Port", "Port"),
    "ZONEN":               ("Zonen", "Zones"),
    "LAUTSTRKE":           ("Lautstärke (%%)", "Volume (%%)"),
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
    "AKKU_UNTER_20_AUERHALB_DER_STATION": ("Akku unter 20 %% außerhalb der Station",
                            "Battery below 20 %% outside the station"),
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
    "SCHALTEN_HINWEIS":    ("Diese Knöpfe wirken <b>sofort</b> auf den Mäher. Der Trockenlauf "
                            "läuft durch dieselbe Funktion und sagt nur, was gesendet <i>würde</i> "
                            "— er sendet nicht.",
                            "These buttons act on the mower <b>immediately</b>. The dry run goes "
                            "through the same function and only reports what <i>would</i> be sent "
                            "— it does not send."),
    "EMPFEHLUNG_20_EINE_LOXONE_ABFRAGE_": ("Empfehlung 20 — eine Loxone-Abfrage alle 30 s reicht "
                            "völlig.", "Recommendation 20 — one Loxone poll every 30 s is plenty."),
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
    "TH_STATUS":           ("Zustand als Klartext (nur über MQTT)",
                            "State as plain text (MQTT only)"),
    "TH_TS":               ("Zeitstempel des letzten Cron-Laufs, Unix-Sekunden",
                            "Timestamp of the last cron run, Unix seconds"),
    "TH_ZAEHLER":          ("Laufzähler, läuft 0…999 um", "Run counter, wraps 0…999"),
    "TH_OK":               ("1 = der letzte Lauf hat wirklich gemessen",
                            "1 = the last run actually measured"),
    "ABO_TITEL":           ("Dieses Abo im MQTT-Gateway eintragen",
                            "Enter this subscription in the MQTT gateway"),
    "ABO_PFLICHT":         ("<b>Ohne diesen Eintrag kommt am Miniserver nichts an.</b> "
                            "System &rarr; MQTT Gateway &rarr; Subscriptions.",
                            "<b>Without this entry nothing arrives at the Miniserver.</b> "
                            "System &rarr; MQTT Gateway &rarr; Subscriptions."),
    "ABO_V2":              ("<b>MQTT-Gateway V2 erkennt die Themengruppe von selbst</b> &mdash; "
                            "einzutragen ist hier nichts. In den <i>Subscriptions</i> erscheint "
                            "die Gruppe; dort werden die gewünschten Datenpunkte einzeln "
                            "angehakt. Erscheint sie nicht, hat noch nichts veröffentlicht.",
                            "<b>MQTT gateway V2 detects the topic group by itself</b> &mdash; "
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
    "W_AUTOSTART":         ("Das MQTT-Gateway steht nicht auf Autostart (System &rarr; MQTT "
                            "Gateway). Es wird gesendet, aber vermutlich hört niemand zu.",
                            "The MQTT gateway is not set to autostart (System &rarr; MQTT "
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
    "SICH_FREMD":          ("Unbekannte Einstellung in der Datei: %s",
                            "Unknown setting in the file: %s"),
    "SICH_WERT":           ("Unzulässiger Wert für %s.", "Invalid value for %s."),
    "SICH_BEREICH":        ("Der Wert für %s liegt außerhalb von %d bis %d.",
                            "The value for %s is outside the range %d to %d."),
    "SICH_MAEHER_FORM":    ("Mäher %d: die Angaben haben nicht die erwartete Form.",
                            "Mower %d: the entries do not have the expected form."),
    "SICH_MAEHER_IP":      ("Mäher %d: ungültige Adresse (%s).", "Mower %d: invalid address (%s)."),
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
    "PRUEF_GW_NEIN":       ("Autostart ist AUS (System &rarr; MQTT Gateway), Gateway-Fassung %s. "
                            "Es wird gesendet, aber vermutlich hört niemand zu.",
                            "Autostart is OFF (System &rarr; MQTT Gateway), gateway version %s. "
                            "Data is sent, but probably nobody is listening."),
    "PRUEF_GW_UNKLAR":     ("nicht feststellbar — <span class='sm-mono'>general.json</span> war "
                            "nicht lesbar.",
                            "not determinable — <span class='sm-mono'>general.json</span> was not "
                            "readable."),
    "PRUEF_GW_UNBEKANNT":  ("unbekannt", "unknown"),
    "PRUEF_THEMEN":        ("ja — %d Themen je Mäher, %d für die Anlage, %d Felder in der Vorlage. "
                            "Alle drei kommen aus einer Quelle.",
                            "yes — %d topics per mower, %d for the installation, %d fields in the "
                            "template. All three come from one source."),
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

    # --- Baustein-Liste
    "4A_KACHELN":          ("6a) Kacheln", "6a) Tiles"),
    "4B_MELDUNGEN":        ("6b) Meldungen", "6b) Notifications"),
    "4C_WETTER_UND_ZEITSPERREN_DER_EIGE": ("6c) Wetter- und Zeitsperren (der eigentliche Mehrwert "
                            "der Automatisierung)",
                            "6c) Weather and time locks (the real benefit of automation)"),
    "STATUSBAUSTEIN":      ("Statusbaustein", "Status block"),
    "MHER_ZUSTAND":        ("Mäher-Zustand", "Mower state"),
    "TEXTE_JE_WERT_1_PARKT_2_MHT_3_FHRT": ("Texte je Wert: 1 „parkt“, 2 „mäht“, 3 „fährt zur "
                            "Station“, 4 „lädt“, 7 „Störung“, 8 „Schleifensignal verloren“, "
                            "−1 „keine Verbindung“",
                            "Texts per value: 1 “parked”, 2 “mowing”, 3 “returning to station”, "
                            "4 “charging”, 7 “fault”, 8 “loop signal lost”, −1 “no connection”"),
    "I1_CODE":             ("I1 ← CODE", "I1 ← CODE"),
    "ANALOGANZEIGEN":      ("Analoganzeigen", "Analog displays"),
    "AKKU_BETRIEBSSTUNDEN_MESSER_RESTST": ("Akku / Betriebsstunden / Messer-Reststunden",
                            "Battery / operating hours / blade hours remaining"),
    "EINHEITEN":           ("Einheiten", "Units"),
    "BATT_STUNDEN_MESSER": ("← BATT, STUNDEN, MESSER", "← BATT, STUNDEN, MESSER"),
    "SCHWELLWERTSCHALTER_S1_S2": ("Schwellwertschalter S1 / S2", "Threshold switch S1 / S2"),
    "MELDEFENSTER_PUSH_FREIGEGEBEN": ("Meldefenster / Push freigegeben",
                            "Notification window / push enabled"),
    "JE_EIN_0_5_AUS_0_4":  ("je Ein 0,5 / Aus 0,4", "each on 0.5 / off 0.4"),
    "ANN_BZW_PUSH":        ("← ANN bzw. PUSH", "← ANN or PUSH"),
    "UND_U1_ODER_O1":      ("UND U1 + ODER O1", "AND U1 + OR O1"),
    "MHER_MELDUNG":        ("Mäher-Meldung", "Mower notification"),
    "O1_IST_DIE_EINZIGE_QUELLE_DES_BENA": ("O1 ist die einzige Quelle des Benachrichtigungs-"
                            "Bausteins", "O1 is the only source of the notification block"),
    "U1_S1_S2":            ("U1: S1 &amp; S2", "U1: S1 &amp; S2"),
    "BENACHRICHTIGUNGS_BAUSTEIN": ("Benachrichtigungs-Baustein", "Notification block"),
    "PUSH_RASENMHER":      ("Push „Rasenmäher“", "Push “lawn mower”"),
    "TEXT_Z_B_MELDUNG_VOM_RASENMHER_DET": ("Text z. B. „Meldung vom Rasenmäher — Details in der "
                            "App“", "Text e.g. “Message from the lawn mower — details in the app”"),
    "O1":                  ("← O1", "← O1"),
    "SCHWELLWERTSCHALTER_S3": ("Schwellwertschalter S3", "Threshold switch S3"),
    "STRUNG":              ("Störung", "Fault"),
    "EIN_0_5_AN_FEHLER_EIGENE_WARNKACHE": ("Ein 0,5 an FEHLER → eigene Warnkachel",
                            "On 0.5 at FEHLER → separate warning tile"),
    "FEHLER_3":            ("← FEHLER", "← FEHLER"),
    "BENACHRICHTIGUNGS_BAUSTEIN_2": ("Benachrichtigungs-Baustein 2", "Notification block 2"),
    "TEST_PUSH":           ("Test-Push", "Test push"),
    "EIGENER_BAUSTEIN_NUR_FR_DEN_TEST": ("eigener Baustein NUR für den Test",
                            "separate block ONLY for the test"),
    "SCHWELLWERTSCHALTER_AN_PTEST": ("← Schwellwertschalter an PTEST",
                            "← threshold switch on PTEST"),
    "B8_NAME":             ("Ausfall des Cron-Laufs", "Cron run failure"),
    "B8_EINST":            ("Statusbaustein oder Schwellwertschalter auf das Alter: "
                            "(Loxone-Zeit + 1230768000) − TS. Schwelle 300 s.",
                            "Status block or threshold switch on the age: "
                            "(Loxone time + 1230768000) − TS. Threshold 300 s."),
    "B8_EING":             ("← TS (und ZAEHLER zur Gegenprobe)",
                            "← TS (and ZAEHLER as a cross-check)"),
    "ZU_8":                ("Zu #8:", "Re #8:"),
    "ZU_8_TEXT":           ("Dieser Baustein ist der wichtigste der ganzen Liste. Ohne ihn steht "
                            "in Loxone bei einem stehenden Cron-Lauf weiter der letzte gemessene "
                            "Wert — und das sieht aus wie eine gültige Auskunft. Die Schwelle "
                            "liegt deutlich über dem Abholtakt von 60 s, damit ein einzelner "
                            "verpasster Durchlauf keine Meldung auslöst.",
                            "This block is the most important one in the whole list. Without it "
                            "Loxone keeps showing the last measured value when the cron run "
                            "stalls — and that looks like valid information. The threshold is well "
                            "above the 60 s polling cycle so a single missed run does not trigger "
                            "an alert."),
    "UND_U2":              ("UND U2", "AND U2"),
    "MHEN_SPERREN_BEI_REGEN": ("Mähen sperren bei Regen", "Block mowing when raining"),
    "AUF":                 ("→ auf", "→ to"),
    "FREIGABE_ERST_NACH_DER_TROCKNUNGSZ": ("; Freigabe erst nach der Trocknungszeit wieder auf",
                            "; release only after the drying time back to"),
    "REGENSENSOR_CODE_2":  ("Regensensor &amp; (CODE = 2)", "Rain sensor &amp; (CODE = 2)"),
    "UND_U3":              ("UND U3", "AND U3"),
    "RUHEZEITEN_EINHALTEN": ("Ruhezeiten einhalten", "Observe quiet hours"),
    "TEXT_2":              ("→", "→"),
    "ZU_ZEITEN_IN_DENEN_NICHT_GEMHT_WER": ("zu Zeiten, in denen nicht gemäht werden soll (Sonn- "
                            "und Feiertage!)", "at times when mowing is unwanted (Sundays and "
                            "public holidays!)"),
    "ZEITSCHALTUHR_GGF_SCHULFREI_FEIERT": ("Zeitschaltuhr &amp; ggf. SCHULFREI/FEIERTAG aus dem "
                            "Ferien-Plugin",
                            "Timer &amp; optionally SCHULFREI/FEIERTAG from the holiday plugin"),
    "SCHWELLWERTSCHALTER_S4_TASTER": ("Schwellwertschalter S4 + Taster",
                            "Threshold switch S4 + button"),
    "TASTER_IN_DER_APP_VIRTUELLER_AUSGA": ("Taster in der App → Virtueller Ausgang",
                            "Button in the app → virtual output"),
    "MESSERWARN_FR_DIE_WARNKACHEL": ("← MESSERWARN für die Warnkachel",
                            "← MESSERWARN for the warning tile"),
    "PRAXIS_ERFAHRUNG":    ("Praxis-Erfahrung:", "From practice:"),
    "DER_BENACHRICHTIGUNGS_BAUSTEIN_SEN": ("Der Benachrichtigungs-Baustein sendet nur bei einer "
                            "0→1-Flanke — niemals mehrere Quellen direkt an den Eingang legen, "
                            "immer erst im ODER sammeln. Für den Test einen eigenen Baustein "
                            "verwenden.",
                            "The notification block only sends on a 0→1 edge — never wire several "
                            "sources directly to the input, always collect them in an OR first. "
                            "Use a separate block for the test."),
}


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
    return "\r\n".join(teile) + "\r\n"


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Aufruf: mo_sprache_erzeugen.py <Plugin-Ordner>")
    ordner = os.path.join(sys.argv[1], "templates", "lang")
    if not os.path.isdir(ordner):
        raise SystemExit("Nicht gefunden: " + ordner)
    for index, name in ((0, "language_de.ini"), (1, "language_en.ini")):
        inhalt = bauen(index, name).encode("utf-8")
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
                 len(REITER) + len(LEGENDE) + len(PRUEF) + len(TEXT)))
        if lf:
            raise SystemExit("ABBRUCH: reine LF in " + name)


if __name__ == "__main__":
    main()
