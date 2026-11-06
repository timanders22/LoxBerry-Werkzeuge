#!/usr/bin/env python3
"""Erzeugt language_de.ini und language_en.ini der Sprachsteuerung.

WARUM EIN ERZEUGER: die beiden Dateien fuehren zusammen rund 450 Schluessel.
Von Hand gepflegt laufen sie auseinander - und der haeufigste Befund der
Pruefreihe ist ein Schluessel, den nur eine der beiden kennt. Hier steht jeder
Text EINMAL, deutsch und englisch nebeneinander; fehlt eine Haelfte, bricht
dieses Skript ab, statt eine halbe Datei zu schreiben.

Regeln des Hausstandards, die hier eingehalten werden:
  - JEDER Wert steht in doppelten Anfuehrungszeichen. Bei parse_ini_file
    beginnt mit ';' ein Kommentar; ein unquotierter Wert wuerde dort
    abgeschnitten - und das trifft jede HTML-Entitaet.
  - Innerhalb eines Wertes steht KEIN weiteres doppeltes Anfuehrungszeichen.
    HTML-Attribute deshalb einfach quoten: <span class='sm-mono'>.
  - Werte, die im PHP durch sp_e() laufen, tragen echte Umlaute statt
    Entitaeten - sonst stuende 'pr&uuml;fen' auf dem Bildschirm.

STAND (vb_bild_ss18, 17.10.2026, Welle Bild 18 / Musterprojekt, Vollausstattung): Reiter "Einbindung in
Loxone" mit drei Seiten aus dem Musterprojekt (Entwurf Welle 18 ss, E10): die alte Liste [BAUSTEIN]
(43 Schluessel) und LOX.S6_* entfallen; neu 98 BAUSTEIN.* (62 Tabellenzeilen Z1_01..Z3_22, Kaesten,
Hinweise), 18 LOX.* (Kasten-/Hinweistitel, Bild, Link, Schritt 3, Kommentare der Ausgangsvorlage) und
SP_FELD.ZAEHLER/DIENSTE_GESAMT (E3); neu gefasst:
LOX.EINLEITUNG, LOX.S1_TEXT, LOX.S3_TEXT, LOX.S4_TITEL, LOX.S4_TEXT, LOX.S5_TITEL, LOX.T_NAMENSVORSCHLAG,
MQTT.B_ZIELTHEMA, MQTT.EMPFEHLUNG, UI013.VORLAGE_NONCACHED.

Aufruf:
    python3 Werkzeuge/sp_sprache_erzeugen.py <Pluginordner>

STAND (vb_st2_sp, 08.10.2026, NACHGEZOGEN): Sprachsteuerung 0.12.2 - zwei Saetze fuer die
Heimnetz-Pflicht beim Speichern (UI013.FEHLER_TTS_IP_HEIMNETZ, UI013.FEHLER_TTS_VORLAGE_HEIMNETZ),
hinten an UI013 (Nachtrag-Reihenfolge, siehe N).

STAND (17.10.2026): Sprachsteuerung 0.12.6 - BAUSTEIN.SEITE3_H4 neu gefasst: die Stilllegung aus
Loxone (ruhe.json) uebersteht seit 0.12.6 ein Update (preupgrade.sh/postinstall.sh).
"""
import sys
from pathlib import Path

# (Abschnitt, Schluessel): (deutsch, englisch)
T = {}


def s(abschnitt, **paare):
    for schluessel, wert in paare.items():
        T[(abschnitt, schluessel)] = wert


s("ALLG",
  AUS=("aus", "off"),
  BEANSTANDUNG=("Bitte prüfen:", "Please check:"),
  CONT_EXTERN=("läuft extern", "running externally"),
  CONT_EXTERN_WEG=("extern, antwortet nicht", "external, not responding"),
  CONT_FEHLT=("fehlt", "missing"),
  CONT_FREMD=("fremder Container", "foreign container"),
  CONT_GESTOPPT=("gestoppt", "stopped"),
  CONT_UNBEKANNT=("nicht feststellbar", "not determinable"),
  CONT_KEIN_DOCKER=("kein Docker", "no Docker"),
  CONT_LAEUFT=("läuft", "running"),
  DIENST=("Sprachdienst", "Voice service"),
  EIGENER_WERT=("eigener Wert (Feld darunter)", "custom value (field below)"),
  EIGENER_WERT_H=("oder hier einen eigenen Wert eintragen",
                  "or enter a custom value here"),
  EIGENSCHAFT=("Eigenschaft", "Property"),
  EIN=("ein", "on"),
  KACHEL_MQTT_HILFE=("Veröffentlichung dieses Plugins; Autostart des Gateways: %s",
                     "Publishing by this plugin; gateway autostart: %s"),
  NICHT_FESTSTELLBAR=("nicht feststellbar", "not determinable"),
  GESTOPPT=("gestoppt", "stopped"),
  HINWEIS=("Zur Kenntnis:", "For information:"),
  JA=("ja", "yes"),
  KEINE_PID=("keine Prozessnummer", "no process id"),
  LAEUFT=("läuft", "running"),
  MIKROFONE=("Mikrofone", "Microphones"),
  NEIN=("nein", "no"),
  RUHE=("Ansagen", "Announcements"),
  RUHE_AUS=("keine Ruhezeit eingestellt", "no quiet hours configured"),
  SAETZE=("Satzmuster", "Sentence patterns"),
  SPEICHERN=("Speichern", "Save"),
  SPRICHT=("frei", "allowed"),
  STILL=("still", "muted"),
  VERBUNDEN=("verbunden", "connected"),
  WERT=("Wert", "Value"),
  ZIELE=("Ziele", "targets"),
  ZULETZT=("Zuletzt gehört:", "Last heard:"),
  )

s("FEHLER",
  CSRF=("Das Formular trug kein gültiges Merkmal und wurde abgewiesen. "
        "Harmlose Ursache: die Seite lag lange offen, während das Token neu "
        "gewürfelt wurde - dann genügt ein Neuladen.",
        "The form carried no valid marker and was rejected. Harmless cause: "
        "the page was open while the token was regenerated - simply reload."),
  CSRF_KEIN_TOKEN=("Es gibt noch kein Aktionstoken, deshalb kann kein Merkmal "
                   "gegen fremde Formulare gebildet werden. Die Seite einmal neu laden.",
                   "There is no action token yet, so no marker against foreign "
                   "forms can be derived. Reload the page once."),
  )

s("LEGENDE",
  AKTION=("Löst etwas aus — wirkt sofort", "Triggers something — takes effect at once"),
  AKTION_LOG=("Löst etwas aus — löscht den Inhalt der Logdatei",
              "Triggers something — clears the log file"),
  AKTION_TOKEN=("Löst etwas aus — ändert bestehende Loxone-Adressen",
                "Triggers something — invalidates existing Loxone addresses"),
  LESEN=("Ansehen — fragt nur ab, verändert nichts",
         "Read only — queries, changes nothing"),
  LESEN_START=("Startet — umkehrbar und harmlos", "Starts — reversible and harmless"),
  TECHNIK=("Technische Auskunft — für die Fehlersuche",
           "Technical information — for troubleshooting"),
  )

s("REITER",
  DIENSTE=("Dienste", "Services"),
  EINSTELLUNGEN=("Einstellungen", "Settings"),
  MQTT=("MQTT", "MQTT"),
  LOG=("Logdateien", "Log files"),
  LOXONE=("Einbindung in Loxone", "Loxone integration"),
  MIKROFONE=("Mikrofone", "Microphones"),
  SAETZE=("Sätze", "Sentences"),
  TEST=("Test", "Test"),
  )

s("SP_FELD",
  OK=("1 = der Sprachdienst läuft", "1 = the voice service is running"),
  MIKROFONE=("Anzahl der eingetragenen Mikrofone", "Number of configured microphones"),
  BEREIT=("Anzahl der gerade verbundenen Mikrofone",
          "Number of microphones currently connected"),
  DIENSTE=("Anzahl der erreichbaren Sprachdienste (Whisper, Piper, Sprachmodell)",
           "Number of reachable voice services (Whisper, Piper, language model)"),
  REGELN=("Anzahl der geladenen Satzmuster - 0 heißt: die Satzdatei ist weg",
          "Number of loaded sentence patterns - 0 means the sentence file is gone"),
  ZIELE=("Anzahl der eingetragenen Ziele", "Number of configured targets"),
  RUHE=("1 = es wird gerade nichts angesagt (Ruhezeit)",
        "1 = announcements are currently suppressed (quiet hours)"),
  LETZTER=("Sekunden seit dem letzten verstandenen Satz, -1 = noch keiner",
           "Seconds since the last understood sentence, -1 = none yet"),
  ALTER=("Alter der Werte in Sekunden, -1 = noch keine",
         "Age of the values in seconds, -1 = none yet"),
  ZAEHLER=("Lebenszeichen: 0 bis 999, ändert sich mindestens alle 15 s, -1 = noch nie",
    "Sign of life: 0 to 999, changes at least every 15 s, -1 = never"),
  DIENSTE_GESAMT=("Anzahl der geprüften Sprachdienste",
    "Number of voice services checked"),
  )

s("STUFE",
  GROSS=("Reichlich Speicher: hier ist auch ein größeres Sprachmodell sinnvoll.",
         "Plenty of memory: a larger language model makes sense here."),
  KLEIN=("Knapp, aber tragfähig. Das Sprachmodell läuft, wird aber spürbar Zeit brauchen.",
         "Tight but workable. The language model runs, but will take noticeable time."),
  MITTEL=("Genug Speicher für ein mittleres Sprachmodell neben der Spracherkennung.",
          "Enough memory for a medium language model alongside speech recognition."),
  WINZIG=("Wenig Speicher: Spracherkennung und Sprachausgabe ja, Sprachmodell nein.",
          "Little memory: speech recognition and synthesis yes, language model no."),
  )

s("DIENST",
  WHISPER=("Wandelt das Gesprochene in Text um. Läuft ganz im Haus.",
           "Turns speech into text. Runs entirely in the house."),
  PIPER=("Spricht die Antwort aus. Läuft ganz im Haus.",
         "Speaks the answer. Runs entirely in the house."),
  WAKEWORD=("Hört auf das Weckwort, damit nicht jedes Wort verarbeitet wird.",
            "Listens for the wake word so not every word gets processed."),
  LLM=("Versteht freie Formulierungen - nur als Rückfallebene, wenn kein Satzmuster passt.",
       "Understands free wording - only as a fallback when no pattern matches."),
  AUSGELAGERT=("<b>Dieser Dienst ist ausgelagert.</b> Er läuft auf %s, nicht auf diesem "
               "LoxBerry. Anlegen, Starten und Anhalten gehören deshalb auf jenen Rechner - "
               "dieses Plugin fasst ihn bewusst nicht an, sonst träfe der Befehl den falschen "
               "Rechner. Die Zeile darunter ist der passende Aufruf zum Mitnehmen: sie bindet "
               "den Port ans Netz (statt nur an 127.0.0.1), damit der LoxBerry herankommt.",
               "<b>This service is remote.</b> It runs on %s, not on this LoxBerry. Creating, "
               "starting and stopping therefore belong on that machine - this plugin "
               "deliberately keeps its hands off, otherwise the command would hit the wrong "
               "machine. The line below is the matching call to take along: it binds the port "
               "to the network instead of just 127.0.0.1."),
  CONTAINER_FEHL=("%s: %s fehlgeschlagen.", "%s: %s failed."),
  CONTAINER_OK=("%s: %s erledigt.", "%s: %s done."),
  FEHLER_BEFEHL=("Unbekannter Containerbefehl.", "Unknown container command."),
  FEHLER_MODELL=("%s: darin stehen unerlaubte Zeichen.", "%s: contains illegal characters."),
  ERST_OEFFNEN=("Dieser Reiter startet die Hardwareerkennung und fragt Docker nach vier "
                "Containern. Das läuft erst, wenn der Reiter wirklich geöffnet wird.",
                "This tab starts hardware detection and asks Docker about four containers. "
                "That only runs when the tab is actually opened."),
  K_JETZT_LADEN=("Jetzt laden", "Load now"),
  FREI=("frei", "free"),
  GESPEICHERT=("Die Modellauswahl wurde gespeichert. Sie wirkt erst, wenn der Container "
               "NEU ANGELEGT wird.",
               "The model selection was saved. It only takes effect once the container is "
               "RE-CREATED."),
  H_CONTAINER=("Die vier Container", "The four containers"),
  H_HARDWARE=("Diese Maschine", "This machine"),
  H_LLM_MODELL=("Angabe im HuggingFace-Format, etwa "
                "<span class='sm-mono'>Qwen/Qwen2.5-1.5B-Instruct-GGUF</span>. llama.cpp "
                "lädt es beim ersten Start selbst herunter - das dauert und braucht Platz.",
                "HuggingFace format, e.g. "
                "<span class='sm-mono'>Qwen/Qwen2.5-1.5B-Instruct-GGUF</span>. llama.cpp "
                "downloads it on first start - that takes time and disk space."),
  H_MESSEN=("Messen statt raten", "Measure instead of guessing"),
  H_MESSVERLAUF=("Frühere Messungen", "Earlier measurements"),
  H_MODELLE=("Modelle", "Models"),
  KC_ANLEGEN=("Anlegen", "Create"),
  KC_ENTFERNEN=("Entfernen", "Remove"),
  KC_HOLEN=("Abbild holen", "Pull image"),
  KC_LOG=("Protokoll", "Log"),
  KC_RESTART=("Neu starten", "Restart"),
  KC_START=("Starten", "Start"),
  KC_STOP=("Anhalten", "Stop"),
  KEINE_GPU=("keine erkannt", "none detected"),
  KEINE_HARDWARE=("Die Hardwareerkennung ließ sich nicht ausführen. Läuft bin/hardware.py?",
                  "Hardware detection could not be run. Is bin/hardware.py in place?"),
  KEINE_ZEITEN=("<b>Hier stehen bewusst keine Sekundenangaben.</b> Wie schnell das auf Ihrer "
                "Maschine ist, hängt an Takt, Kühlung und Speicherbandbreite - jede Zahl in "
                "einer Anleitung wäre geraten. Der Knopf <i>Jetzt messen</i> weiter unten "
                "misst es statt dessen.",
                "<b>No timings are given here on purpose.</b> How fast this is on your machine "
                "depends on clock, cooling and memory bandwidth - any number in a manual would "
                "be a guess. The <i>Measure now</i> button below measures it instead."),
  KEIN_BEFEHL=("Für diesen Dienst ist kein Modell eingestellt - erst oben eintragen.",
               "No model configured for this service - set one above first."),
  # Seit 0.11.11 (Bauliste Einrichtung E7): Docker NG statt des eingestellten
  # Plugins "Docker"; der Gruppenbefehl steht nur noch als letzter Hinweis in
  # DOCKER_ANTWORTET_NICHT.
  KEIN_DOCKER=("<b>Docker ist auf diesem LoxBerry nicht installiert.</b> Ohne Docker kann das "
               "Plugin die Sprachdienste nicht selbst betreiben. Zwei Wege: das LoxBerry-Plugin "
               "<a href='https://github.com/timanders22/LoxBerry-Plugin-Docker-NG' "
               "target='_blank'>Docker NG</a> installieren und den LoxBerry danach einmal neu "
               "starten, oder die Dienste auf einem anderen Rechner betreiben und in den "
               "Einstellungen nur deren Adressen eintragen.",
               "<b>Docker is not installed on this LoxBerry.</b> Without Docker this plugin "
               "cannot run the voice services itself. Two ways: install the LoxBerry plugin "
               "<a href='https://github.com/timanders22/LoxBerry-Plugin-Docker-NG' "
               "target='_blank'>Docker NG</a> and restart the LoxBerry once afterwards, or run "
               "the services on another machine and only enter their addresses in the settings."),
  DOCKER_ANTWORTET_NICHT=("Nach der Installation von "
                          "<a href='https://github.com/timanders22/LoxBerry-Plugin-Docker-NG' "
                          "target='_blank'>Docker NG</a> genügt meist <b>ein Neustart des "
                          "LoxBerry</b>: erst danach darf die Plugin-Oberfläche mit Docker "
                          "sprechen. Nur wenn auch der Neustart nicht hilft, der Befehl für den "
                          "Fachmann (als root): <span class='sm-mono'>usermod -aG docker "
                          "loxberry</span>, danach den LoxBerry neu starten.",
                          "After installing "
                          "<a href='https://github.com/timanders22/LoxBerry-Plugin-Docker-NG' "
                          "target='_blank'>Docker NG</a>, <b>restarting the LoxBerry</b> is "
                          "usually enough: only then may the plugin page talk to Docker. Only if "
                          "the restart does not help either, the command for the expert (as "
                          "root): <span class='sm-mono'>usermod -aG docker loxberry</span>, then "
                          "restart the LoxBerry."),
  KEIN_LLM=("keines - diese Maschine ist dafür zu klein",
            "none - this machine is too small for one"),
  KERNE=("Kerne", "cores"),
  K_MESSEN=("Jetzt messen", "Measure now"),
  L_LLM_MODELL=("Sprachmodell", "Language model"),
  L_PIPER_STIMME=("Piper-Stimme", "Piper voice"),
  L_WHISPER_MODELL=("Whisper-Modell", "Whisper model"),
  MESSEN_ERKLAERUNG=("Der Knopf schickt einen Prüfton fester Länge durch die Spracherkennung, "
                     "lässt einen Satz aussprechen, fragt den Wortwecker und stellt dem "
                     "Sprachmodell eine Frage - und misst dabei die Zeit. Das ist die einzige "
                     "belastbare Aussage darüber, ob diese Maschine schnell genug ist. "
                     "<b>Als Anhaltspunkt:</b> Wer länger als etwa drei Sekunden auf das Licht "
                     "wartet, greift beim nächsten Mal wieder zum Schalter.",
                     "The button sends a test tone of fixed length through speech recognition, "
                     "has a sentence spoken, queries the wake word service and asks the "
                     "language model a question - measuring the time. This is the only solid "
                     "statement about whether this machine is fast enough. <b>As a rule of "
                     "thumb:</b> whoever waits longer than about three seconds for the light "
                     "will reach for the switch next time."),
  MESSVERLAUF_ERKLAERUNG=("Die letzten Messungen bleiben erhalten. Erst damit lässt sich "
                          "sagen, ob ein Modellwechsel wirklich schneller war - eine einzelne "
                          "Zahl beantwortet das nicht.",
                          "The last measurements are kept. Only then can you tell whether a "
                          "model change really was faster - a single number cannot answer that."),
  MODELLE_ERKLAERUNG=("Die Liste kommt aus der Empfehlungstabelle des Plugins. Wer ein Modell "
                      "benutzt, das nicht darin steht, trägt es unten als eigenen Wert ein - "
                      "ein Vertipper fiel früher erst auf, wenn der Container nicht startete.",
                      "The list comes from the plugin's recommendation table. To use a model "
                      "not listed, enter it below as a custom value - a typo used to surface "
                      "only when the container failed to start."),
  MODELLE_LEER=("Bleibt ein Feld leer, gilt der Vorschlag von oben.",
                "If a field is left empty, the suggestion above applies."),
  MODELL_WARNUNG=("<b>Der Modellordner wird nie mitgelöscht.</b> <i>Container entfernen</i> "
                  "entfernt nur den Container; die heruntergeladenen Modelle bleiben liegen "
                  "und sind nach <i>Container anlegen</i> sofort wieder da. Das ist Absicht: "
                  "es geht um Gigabyte. Erst beim Deinstallieren des Plugins entfernt "
                  "LoxBerry den Datenordner und mit ihm die Modelle; die eigenen Container "
                  "entfernt die Deinstallation vorher.",
                  "<b>The model folder is never deleted.</b> <i>Remove container</i> only "
                  "removes the container; the downloaded models stay and are back immediately "
                  "after <i>Create container</i>. This is deliberate: gigabytes are involved. "
                  "Only when the plugin is uninstalled does LoxBerry remove the data folder and "
                  "the models with it; the uninstall removes the plugin's own containers "
                  "before that."),
  NICHT64=("nicht 64 Bit, die Container laufen so nicht",
           "not 64 bit, the containers will not run"),
  T_ARCH=("Architektur", "Architecture"),
  T_CPU=("Prozessor", "Processor"),
  T_GPU=("Grafik", "Graphics"),
  T_GROESSE=("Dateigröße", "File size"),
  T_MODELL=("Modell", "Model"),
  T_SPEICHER=("Arbeitsspeicher", "Memory"),
  T_TEIL=("Teil", "Part"),
  T_VORSCHLAG=("Vorschlag", "Suggestion"),
  VORSCHLAG=("Vorschlag für diese Maschine: Stufe %s.",
             "Suggestion for this machine: level %s."),
  VORSCHLAG_NEHMEN=("Vorschlag von oben nehmen", "use the suggestion above"),
  )

# Seit 0.11.11 (Bauliste Einrichtung, 30.09.2026): Container auf Knopfdruck.
# Alle Werte ausser EINRICHTEN_ERKLAERUNG und EINZELN_ERKLAERUNG laufen
# durch sp_e() und tragen deshalb keine Auszeichnung und keine Entitaet.
s("CT",
  AMPEL_WARTET=("Die Ampel wird gemessen, sobald der Vorgang fertig ist.",
                "The status lights are measured once the process has finished."),
  AMPEL_ZEIT=("Gemessen am %s.", "Measured on %s."),
  A_AUSGESCHALTET=("ausgeschaltet - das Sprachmodell ist in den Einstellungen aus",
                   "switched off - the language model is off in the settings"),
  A_NICHT_VORGESEHEN=("nicht vorgesehen - kein Sprachmodell eingestellt oder empfohlen",
                      "not planned - no language model configured or recommended"),
  ANGELEGT=("Container %s angelegt und gestartet (Kennung %s).",
            "Container %s created and started (id %s)."),
  ANGELEGT_STEHT=("Container %s angelegt (Kennung %s), läuft aber nicht (Zustand %s). Das Protokoll unter Einzeln verwalten zeigt, warum.",
                  "Container %s created (id %s) but not running (state %s). The log under Manage individually shows why."),
  DOCKER_DIENST_AUS=("Der Docker-Dienst läuft nicht.", "The Docker service is not running."),
  DOCKER_FEHLER=("Docker antwortete mit Fehler %d: %s", "Docker answered with error %d: %s"),
  DOCKER_FEHLT=("Docker ist auf diesem LoxBerry nicht installiert.",
                "Docker is not installed on this LoxBerry."),
  DOCKER_HAENGT=("Docker antwortete nicht innerhalb von %d Sekunden.",
                 "Docker did not answer within %d seconds."),
  DOCKER_KEIN_ZUGRIFF=("Docker ist installiert, verweigert der Plugin-Oberfläche aber den Zugriff.",
                       "Docker is installed but refuses access to the plugin page."),
  DOCKER_OK=("Docker antwortet (Fassung %s).", "Docker answers (version %s)."),
  EINRICHTEN_ERKLAERUNG=("Der Knopf holt die Abbilder, legt die Container an und startet sie - "
                         "mit den Modellen, die oben eingestellt sind, sonst mit dem Vorschlag "
                         "für diese Maschine. Das läuft im Hintergrund; die Seite zeigt den "
                         "Fortschritt und lädt sich dabei selbst neu. Das erste Holen kann je "
                         "nach Leitung viele Minuten dauern. <b>Vorhandene eigene Container "
                         "bleiben stehen</b> und werden nur gestartet, wenn sie angehalten "
                         "sind. Ausgelagerte Dienste fasst der Knopf nicht an. Vorgesehen ist:",
                         "The button pulls the images, creates the containers and starts them - "
                         "with the models set above, otherwise with the suggestion for this "
                         "machine. It runs in the background; the page shows the progress and "
                         "reloads itself meanwhile. The first pull can take many minutes "
                         "depending on the line. <b>Existing own containers are kept</b> and "
                         "only started if they are stopped. Remote services are left alone. "
                         "Planned:"),
  EINZELN_ERKLAERUNG=("Für Fortgeschrittene: jeder Container einzeln. <i>Abbild holen</i> und "
                      "<i>Anlegen</i> laufen ebenfalls im Hintergrund. Angefasst wird nur ein "
                      "Container, der zu diesem Plugin gehört - er trägt dessen Label, oder er "
                      "heißt genau wie hier angegeben und stammt aus dem vorgesehenen Abbild.",
                      "For advanced users: each container on its own. <i>Pull image</i> and "
                      "<i>Create</i> also run in the background. Only a container belonging to "
                      "this plugin is touched - it carries the plugin's label, or it has exactly "
                      "the name given here and comes from the intended image."),
  FREMD_ABBILD=("Der Container %s stammt aus dem Abbild %s, vorgesehen ist %s. Er gehört "
                "vermutlich nicht zu diesem Plugin und bleibt deshalb unberührt.",
                "Container %s comes from image %s, expected is %s. It probably does not belong "
                "to this plugin and is therefore left alone."),
  FREMD_LABEL=("Der Container %s trägt die Labels folder=%s und name=%s, dieses Plugin ist %s. "
               "Er gehört zu einer anderen Installation und bleibt unberührt.",
               "Container %s carries the labels folder=%s and name=%s, this plugin is %s. It "
               "belongs to another installation and is left alone."),
  FREMD_NAME=("Der Container heißt %s, erwartet ist %s - er bleibt unberührt.",
              "The container is named %s, expected is %s - it is left alone."),
  G_ABBILD_FEHLT=("%s: Abbild nicht geholt", "%s: image not pulled"),
  G_ANGEHALTEN=("%s: Container angehalten", "%s: container stopped"),
  G_AUS_ANTWORTET=("%s auf %s (antwortet)", "%s on %s (responding)"),
  G_AUS_STUMM=("%s auf %s (antwortet nicht)", "%s on %s (not responding)"),
  G_AUSGESCHALTET=("Ausgeschaltet und nicht eingerichtet: %s.", "Switched off and not set up: %s."),
  G_AUSGELAGERT=("Ausgelagert, hier nicht verwaltet: %s.", "Remote, not managed here: %s."),
  G_BEREIT=("Bereit: %s laufen und antworten.", "Ready: %s are running and responding."),
  G_FEHLT=("Noch nicht bereit. Es fehlt: %s.", "Not ready yet. Missing: %s."),
  G_FREMD=("%s: der Name ist durch einen fremden Container belegt",
           "%s: the name is taken by a foreign container"),
  G_KEIN_LOKALER=("Auf diesem LoxBerry ist kein Sprachdienst vorgesehen - es gibt nichts einzurichten.",
                  "No voice service is planned on this LoxBerry - there is nothing to set up."),
  G_NICHT_ANGELEGT=("%s: Container nicht angelegt", "%s: container not created"),
  G_NUR_PORTS=("Alle Ports antworten, aber Docker ist nicht zu fragen (%s) - ob es die eigenen Container sind, ist nicht feststellbar.",
               "All ports respond, but Docker cannot be asked (%s) - whether these are the plugin's own containers cannot be determined."),
  G_PORT_STUMM=("%s: Port %d antwortet nicht", "%s: port %d not responding"),
  G_UNBEKANNT=("%s: Zustand nicht feststellbar", "%s: state not determinable"),
  GEHOLT=("Abbild %s geholt.", "Image %s pulled."),
  GESAMT=("Gesamt:", "Overall:"),
  GESCHALTET_ENTFERNEN=("Container %s (Kennung %s) entfernt. Der Modellordner bleibt.",
                        "Container %s (id %s) removed. The model folder stays."),
  GESCHALTET_RESTART=("Container %s (Kennung %s) neu gestartet, er läuft.",
                      "Container %s (id %s) restarted, it is running."),
  GESCHALTET_START=("Container %s (Kennung %s) gestartet, er läuft.",
                    "Container %s (id %s) started, it is running."),
  GESCHALTET_STOP=("Container %s (Kennung %s) angehalten.", "Container %s (id %s) stopped."),
  H_AMPEL=("Ampel", "Status lights"),
  H_EINRICHTEN=("Sprachdienste einrichten", "Set up voice services"),
  H_EINZELN=("Einzeln verwalten", "Manage individually"),
  K_EINRICHTEN=("Sprachdienste einrichten", "Set up voice services"),
  KEIN_ABBILD=("%s: in templates/modelle.json steht kein Abbild.",
               "%s: templates/modelle.json names no image."),
  LAEUFT_SCHON=("Container %s läuft bereits (Kennung %s) und bleibt, wie er ist.",
                "Container %s is already running (id %s) and is left as it is."),
  NICHT_ANGEFASST=("Nicht angefasst: %s", "Not touched: %s"),
  NICHT_DA=("Einen Container %s gibt es nicht.", "There is no container %s."),
  NUR_HINTERGRUND=("Abbild holen und Anlegen laufen nur im Hintergrund.",
                   "Pull image and Create only run in the background."),
  OHNE_WIRKUNG=("%s an %s blieb ohne Wirkung (Rückgabewert %d): %s",
                "%s on %s had no effect (return code %d): %s"),
  P_AUSGELAGERT=("%s ist auf %s ausgelagert und wird hier nicht angefasst.",
                 "%s is remote on %s and is not touched here."),
  P_AUSGESCHALTET=("%s ist in den Einstellungen ausgeschaltet und wird nicht angelegt (von Hand unter Einzeln verwalten weiter möglich).",
                   "%s is switched off in the settings and is not created (still possible by hand under Manage individually)."),
  P_EINRICHTEN=("%s mit %s (Abbild %s)", "%s with %s (image %s)"),
  P_KEIN_MODELL=("%s: kein Modell eingestellt oder empfohlen - wird übersprungen.",
                 "%s: no model configured or recommended - skipped."),
  PULL_FEHLER=("Abbild %s ließ sich nicht holen (Rückgabewert %d): %s",
               "Image %s could not be pulled (return code %d): %s"),
  PULL_NICHT_DA=("docker pull meldete Erfolg, aber das Abbild %s liegt nicht da.",
                 "docker pull reported success, but image %s is not present."),
  PULL_ZEITABLAUF=("Abbild %s: das Holen wurde nach %d Minuten abgebrochen - die Leitung ist "
                   "zu langsam oder unterbrochen. Ein erneuter Druck auf den Knopf versucht es "
                   "noch einmal.",
                   "Image %s: pulling was stopped after %d minutes - the line is too slow or "
                   "interrupted. Pressing the button again tries once more."),
  RUN_FEHLER=("Container %s ließ sich nicht anlegen (Rückgabewert %d): %s",
              "Container %s could not be created (return code %d): %s"),
  RUN_ZEITABLAUF=("Container %s: docker run antwortete nicht innerhalb von %d Sekunden.",
                  "Container %s: docker run did not answer within %d seconds."),
  S_ANLEGEN=("Container anlegen", "create container"),
  S_HOLEN=("Abbild holen", "pull image"),
  S_PLAN=("Planen", "planning"),
  S_STARTEN=("Container starten", "start container"),
  SCHON_DA=("Es gibt bereits einen Container %s. Erst entfernen, dann neu anlegen.",
            "Container %s already exists. Remove it first, then create it anew."),
  T_ABBILD=("Abbild da", "Image present"),
  T_DIENST=("Dienst", "Service"),
  T_HINWEIS=("Zustand", "State"),
  T_LAEUFT=("Container läuft", "Container running"),
  T_PORT=("Port antwortet", "Port responding"),
  U_BLEIBT=("Container %s (Kennung %s) ist noch da: %s", "Container %s (id %s) is still there: %s"),
  U_ENTFERNT=("Container %s (Kennung %s) entfernt.", "Container %s (id %s) removed."),
  U_KEINER=("Einen Container %s gibt es nicht.", "There is no container %s."),
  U_NICHTS=("Es wurde kein Container entfernt. Von Hand nachsehen: docker ps -a --filter label=de.loxberry.plugin.folder=%s",
            "No container was removed. Check by hand: docker ps -a --filter label=de.loxberry.plugin.folder=%s"),
  V_ABGEBROCHEN=("Der letzte Vorgang wurde abgebrochen (bei Schritt %d von %d: %s, %s) - der "
                 "Prozess lebt nicht mehr. Ein erneuter Druck auf den Knopf setzt fort.",
                 "The last process was aborted (at step %d of %d: %s, %s) - the process is no "
                 "longer alive. Pressing the button again continues."),
  V_ABGEBROCHEN_PLAN=("Der letzte Vorgang wurde abgebrochen, bevor er einen Schritt getan hatte "
                      "- der Prozess lebt nicht mehr. Ein erneuter Druck auf den Knopf fängt von "
                      "vorn an.",
                      "The last process was aborted before it had taken a step - the process is "
                      "no longer alive. Pressing the button again starts over."),
  V_FEHLER=("Der Vorgang vom %s ist nicht vollständig gelungen.", "The process of %s did not fully succeed."),
  V_FERTIG=("Der Vorgang vom %s ist fertig.", "The process of %s has finished."),
  V_GESTARTET=("Der Vorgang wird gestartet ... seit %d s.", "The process is starting ... for %d s."),
  V_LAEUFT=("Wird eingerichtet ... Schritt %d von %d: %s, %s - seit %d s.",
            "Setting up ... step %d of %d: %s, %s - for %d s."),
  V_NEU_LADEN=("Die Seite lädt sich alle 5 Sekunden neu, solange der Vorgang läuft.",
               "The page reloads every 5 seconds while the process is running."),
  V_PLANT=("Wird eingerichtet ... Docker wird gefragt, was zu tun ist - seit %d s.",
           "Setting up ... asking Docker what needs doing - for %d s."),
  VORGANG_AUSNAHME=("Der Vorgang brach mit einer Ausnahme ab: %s", "The process stopped with an exception: %s"),
  VORGANG_DATEI=("Die Zustandsdatei des Vorgangs ließ sich nicht schreiben.",
                 "The state file of the process could not be written."),
  VORGANG_FEHLT=("Das Programm des Vorgangs fehlt: %s - Plugin neu installieren.",
                 "The process program is missing: %s - reinstall the plugin."),
  VORGANG_GESTARTET=("Der Vorgang läuft im Hintergrund.", "The process is running in the background."),
  VORGANG_LAEUFT_SCHON=("Es läuft bereits ein Vorgang - erst dessen Ende abwarten.",
                        "A process is already running - wait for it to finish first."),
  VORGANG_NOCH_NICHT=("Der Vorgang wurde abgezweigt, hat sich aber noch nicht gemeldet. Die Seite zeigt, ob er anläuft.",
                      "The process was forked but has not reported yet. The page shows whether it starts."),
  VORGANG_START=("Der Hintergrundvorgang ließ sich nicht starten.", "The background process could not be started."),
  ZEITABLAUF=("%s antwortete nicht innerhalb von %d Sekunden.", "%s did not answer within %d seconds."),
  )

s("EINST",
  DIENSTE_ERKLAERUNG=("Ab Werk auf demselben Rechner. Wer einen kräftigeren Rechner im Haus "
                      "hat, lässt Whisper und das Sprachmodell dort laufen und trägt hier nur "
                      "dessen Adresse ein - das ist bei einem Raspberry Pi oft der "
                      "entscheidende Unterschied.",
                      "By default on the same machine. If you have a more powerful machine in "
                      "the house, run Whisper and the language model there and only enter its "
                      "address here - on a Raspberry Pi that is often the decisive difference."),
  DIENST_ERKLAERUNG=("Der Dienst hält die Verbindung zu den Mikrofonen offen und führt jede "
                     "Aufnahme durch die Kette. Ein minütlicher Wächter startet ihn neu, wenn "
                     "er abstürzt; ein von Hand angehaltener Dienst bleibt angehalten.",
                     "The service keeps the connections to the microphones open and runs every "
                     "recording through the chain. A watchdog restarts it every minute if it "
                     "crashes; a manually stopped service stays stopped."),
  DIENST_RESTART=("Dienst neu gestartet.", "Service restarted."),
  DIENST_START=("Dienst gestartet.", "Service started."),
  DIENST_STOP=("Dienst angehalten.", "Service stopped."),
  ERGAENZT=("Die Konfiguration wurde um %d fehlende Angaben ergänzt: %s",
            "The configuration was completed with %d missing entries: %s"),
  FEHLER_ANTWORTWEG=("Der Antwortweg muss Satellit, Loxone oder beides sein.",
                     "The answer path must be satellite, Loxone or both."),
  FEHLER_BEREICH=("%s: der Wert muss zwischen %d und %d liegen.",
                  "%s: the value must be between %d and %d."),
  FEHLER_HOST=("%s: das ist keine gültige Adresse.", "%s: that is not a valid address."),
  FEHLER_PORT=("%s: der Port muss eine Zahl von 1 bis 65535 sein.",
               "%s: the port must be a number from 1 to 65535."),
  FEHLER_RUHEZEIT=("Die Ruhezeit wird als Uhrzeit eingetragen, zum Beispiel 22:00.",
                   "Quiet hours are entered as a time of day, for example 22:00."),
  FEHLER_SPEICHERN=("Die Konfiguration ließ sich nicht schreiben: %s",
                    "The configuration could not be written: %s"),
  FEHLER_SPRACHE=("Die Sprache muss aus genau zwei Buchstaben bestehen, zum Beispiel de.",
                  "The language must be exactly two letters, for example de."),
  FEHLER_TOPIC=("Das Themen-Präfix darf nur Buchstaben, Ziffern, Bindestrich, Unterstrich und "
                "Schrägstrich enthalten und nicht leer sein.",
                "The topic prefix may only contain letters, digits, hyphen, underscore and "
                "slash, and must not be empty."),
  FEHLER_TTS_FEHLT=("Der Antwortweg führt über Loxone, aber es ist keine Adresse für die "
                    "Audioausgabe eingetragen.",
                    "The answer path goes through Loxone, but no address for the audio output "
                    "is configured."),
  FEHLER_TTS_IP=("Loxone-Audioausgabe: die Adresse ist keine gültige IP und kein gültiger "
                 "Rechnername.",
                 "Loxone audio output: the address is neither a valid IP nor a valid host name."),
  FEHLER_TTS_MODUS=("Loxone-Audioausgabe: unbekannte Art der Ausgabe.",
                    "Loxone audio output: unknown output type."),
  FEHLER_TTS_VORLAGE=("Loxone-Audioausgabe: die Vorlage muss mit http:// oder https:// beginnen.",
                      "Loxone audio output: the template must start with http:// or https://."),
  FEHLER_TTS_ZONEN=("Loxone-Audioausgabe: Zonen bestehen aus Ziffern, Komma und der Tilde, zum "
                    "Beispiel <span class='sm-mono'>2,4</span> oder "
                    "<span class='sm-mono'>2~15,4</span>.",
                    "Loxone audio output: zones consist of digits, commas and the tilde, for "
                    "example <span class='sm-mono'>2,4</span> or "
                    "<span class='sm-mono'>2~15,4</span>."),
  FEHLER_URL=("Die Adresse muss mit http:// oder https:// beginnen.",
              "The address must start with http:// or https://."),
  FEHLER_WAKEWORD=("Das Weckwort darf nur Kleinbuchstaben, Ziffern, Bindestrich und "
                   "Unterstrich enthalten.",
                   "The wake word may only contain lowercase letters, digits, hyphen and "
                   "underscore."),
  FEHLER_ZAHL=("%s: bitte eine ganze Zahl eintragen.", "%s: please enter a whole number."),
  GESPEICHERT=("Die Einstellungen wurden gespeichert, samt Sicherungskopie für Updates.",
               "The settings were saved, including a backup copy for updates."),
  K_PROBE=("Stimme probehören", "Preview the voice"),
  K_PROBE_HOLEN=("Probe herunterladen (WAV)", "Download sample (WAV)"),
  L_PROBE_TEXT=("Text für die Probe", "Text for the sample"),
  H_PROBE=("Erzeugt eine WAV-Datei mit der oben eingetragenen Stimme, ohne einen Container "
           "anzulegen. So lässt sich hören, wie eine Stimme klingt, bevor man sie einrichtet. "
           "Piper muss dafür laufen.",
           "Creates a WAV file with the voice entered above, without creating a container. That "
           "lets you hear how a voice sounds before setting it up. Piper must be running."),
  PROBE_FERTIG=("Die Probe steht unten zum Herunterladen bereit.",
                "The sample is available for download below."),
  PROBE_FEHLT=("Es liegt keine Probe vor - erst erzeugen lassen.",
               "There is no sample yet - create one first."),
  H_ANSAGE_ABSTAND_S=("Mindestabstand zwischen zwei Ansagen. Ein Loxone-Baustein, der in einer "
                      "Schleife hängt, erzeugt sonst beliebig viele hintereinander. 0 schaltet "
                      "die Bremse ab.",
                      "Minimum gap between two announcements. Otherwise a Loxone block stuck in "
                      "a loop produces any number in a row. 0 disables the limit."),
  H_ANSAGE_JE_TAG=("Höchstzahl der Ansagen in 24 Stunden. 0 heißt: unbegrenzt.",
                   "Maximum number of announcements within 24 hours. 0 means unlimited."),
  H_ANTWORTWEG=("Antwort zurück nach Loxone", "Answer back to Loxone"),
  H_ANTWORTWEG_FELD=("Der Text im Thema <span class='sm-mono'>/antwort</span> geht in jedem "
                     "Fall an Loxone - diese Auswahl betrifft nur die gesprochene Ansage.",
                     "The text on topic <span class='sm-mono'>/antwort</span> always goes to "
                     "Loxone - this selection only concerns the spoken announcement."),
  H_ANTWORTWEG_TEXT=("Piper spricht die Antwort in den Lautsprecher des Mikrofons, das die "
                     "Frage gehört hat. Wer im Nebenzimmer steht, hört nichts. Hier wird "
                     "eingestellt, dass der fertige Satz zusätzlich nach Loxone geht: als Text "
                     "im MQTT-Thema <span class='sm-mono'>/antwort</span> für einen virtuellen "
                     "Texteingang, und als Ansage über Music Server oder Audioserver. Die "
                     "Felder sind dieselben wie im Abfuhrkalender und im Abfahrtsassistenten.",
                     "Piper speaks the answer into the loudspeaker of the microphone that heard "
                     "the question. Anyone in the next room hears nothing. Here you configure "
                     "that the finished sentence additionally goes to Loxone: as text on MQTT "
                     "topic <span class='sm-mono'>/antwort</span> for a virtual text input, and "
                     "as an announcement via Music Server or Audioserver. The fields are the "
                     "same as in the waste calendar and the departure assistant plugins."),
  H_BESTAETIGUNG_S=("Wie lange die Anlage auf ein 'ja' wartet, nachdem sie bei einem heiklen "
                    "Ziel zurückgefragt hat. 0 schaltet die Rückfrage ab - dann wird sofort "
                    "geschaltet.",
                    "How long the system waits for a 'yes' after asking back about a sensitive "
                    "target. 0 disables the question - it then switches immediately."),
  H_DIENST=("Sprachdienst", "Voice service"),
  H_DIENSTE=("Wo die Sprachdienste laufen", "Where the voice services run"),
  H_KONTEXT_S=("Wie lange ein genanntes Ziel für Folgesätze gilt. Damit wird aus einer "
               "Befehlsliste ein Gespräch: 'Licht im Wohnzimmer an' - 'heller' - 'aus'. "
               "0 schaltet den Kontext ab.",
               "How long a mentioned target remains valid for follow-up sentences. This turns a "
               "list of commands into a conversation: 'living room light on' - 'brighter' - "
               "'off'. 0 disables context."),
  H_LLM_EIN=("Nur was kein Satzmuster trifft, geht an das Modell. Ist es abgeschaltet, "
             "antwortet die Anlage auf Unbekanntes mit 'Das habe ich nicht verstanden' - "
             "ehrlicher als eine geratene Handlung.",
             "Only what no pattern matches goes to the model. If it is off, the system answers "
             "unknown input with 'I did not understand that' - more honest than a guessed "
             "action."),
  H_LOXONE=("Weg nach Loxone", "Path to Loxone"),
  H_RUHE=("Ruhezeit und Wiederholungsbremse", "Quiet hours and repeat limit"),
  H_RUHE_TEXT=("<b>Ohne Ruhezeit kann jeder Loxone-Baustein um drei Uhr nachts das Haus reden "
               "lassen.</b> Das Ansageverfahren dieses Plugins stammt aus dem Abfuhrkalender - "
               "die Wache davor gab es dort seit jeher, hier bis 0.9.11 nicht. Innerhalb der "
               "Ruhezeit bleibt auch der Lautsprecher des Mikrofons still. Ein Alarm kann sie "
               "übergehen: dafür trägt der virtuelle Ausgang "
               "<span class='sm-mono'>&amp;dringend=1</span>.",
               "<b>Without quiet hours any Loxone block can make the house talk at three in the "
               "morning.</b> This plugin's announcement mechanism comes from the waste calendar "
               "plugin - the guard in front of it existed there from the start, here it did not "
               "until 0.9.11. During quiet hours the microphone loudspeaker stays silent too. "
               "An alarm can override it: the virtual output carries "
               "<span class='sm-mono'>&amp;dringend=1</span> for that."),
  H_TTS_MODE=("<b>aus</b> (ab Werk): es sprechen nur die Lautsprecher der Sprachgeräte. <b>Music Server</b> ist der Regelfall für Loxone. <b>MusicServer4Home</b> und <b>eigene Vorlage</b> benutzen das Vorlagenfeld unten. Beim <b>originalen Loxone Audioserver</b> gibt es keinen Aufruf über das Netz - dort wird die Ansage in Loxone Config gebaut (Textgenerator am TTS-Eingang), und das Plugin liefert den Text im MQTT-Thema <span class='sm-mono'>/ansage</span>. <b>Chromecast4lox</b> (über MQTT), <b>Alexa-NG</b> und <b>Google-Lautsprecher (Chromecast 4 Lox NG)</b> (über dessen Sprech-Endpunkt) sind Plugins auf diesem LoxBerry (Felder weiter unten). Alexa selbst ist nicht eingebaut: dafür gibt es keine offizielle lokale Schnittstelle.",
    "<b>off</b> (default): only the speakers of the voice devices speak. <b>Music Server</b> is the standard case for Loxone. <b>MusicServer4Home</b> and <b>custom template</b> use the template field below. The <b>original Loxone Audioserver</b> has no network call - there the announcement is built in Loxone Config (text generator at the TTS input), and the plugin delivers the text on MQTT topic <span class='sm-mono'>/ansage</span>. <b>Chromecast4lox</b> (via MQTT), <b>Alexa-NG</b> and <b>Google speakers (Chromecast 4 Lox NG)</b> (via its speech endpoint) are plugins on this LoxBerry (fields further down). Alexa itself is not built in: there is no official local interface for it."),
  H_TTS_STIMME=("Wahlweise eine andere Piper-Stimme für die Ansagen als die, mit der der "
                "Container gestartet wurde. Bleibt das Feld leer, gilt die des Containers.",
                "Optionally a different Piper voice for announcements than the one the "
                "container was started with. If empty, the container's voice applies."),
  H_TTS_TEMPLATE=("Nur für MusicServer4Home und eigene Vorlage. Ersetzt werden "
                  "<span class='sm-mono'>{ip}</span>, <span class='sm-mono'>{port}</span>, "
                  "<span class='sm-mono'>{zones}</span>, <span class='sm-mono'>{vol}</span>, "
                  "<span class='sm-mono'>{lang}</span> und <span class='sm-mono'>{text}</span>. "
                  "Bleibt das Feld leer, gilt die Standardvorlage von MusicServer4Home.",
                  "Only for MusicServer4Home and custom template. Replaced are "
                  "<span class='sm-mono'>{ip}</span>, <span class='sm-mono'>{port}</span>, "
                  "<span class='sm-mono'>{zones}</span>, <span class='sm-mono'>{vol}</span>, "
                  "<span class='sm-mono'>{lang}</span> and <span class='sm-mono'>{text}</span>. "
                  "If empty, the MusicServer4Home default template applies."),
  H_TTS_ZONES=("Eine oder mehrere Zonen, durch Komma getrennt: "
               "<span class='sm-mono'>2,4</span>. Eine eigene Lautstärke je Zone geht mit der "
               "Tilde: <span class='sm-mono'>2~15,4</span> - sie hat Vorrang vor dem Feld "
               "darunter. Ein Mikrofon kann eine eigene Zone tragen; dann kommt die Antwort in "
               "dem Raum an, in dem gefragt wurde.",
               "One or more zones, comma separated: <span class='sm-mono'>2,4</span>. A "
               "per-zone volume works with the tilde: <span class='sm-mono'>2~15,4</span> - it "
               "takes precedence over the field below. A microphone can carry its own zone; the "
               "answer then arrives in the room where the question was asked."),
  H_URL=("Wahlweise. Der Regelweg ist MQTT - dafür braucht das Plugin keine Zugangsdaten des "
         "Miniservers. Wer den unmittelbaren Aufruf will, trägt hier eine Adresse ein; "
         "<span class='sm-mono'>{ziel}</span>, <span class='sm-mono'>{aktion}</span> und "
         "<span class='sm-mono'>{wert}</span> werden ersetzt. <b>Zugangsdaten werden hier "
         "maskiert angezeigt</b> - wer sie ändern will, trägt die ganze Adresse neu ein.",
         "Optional. The standard path is MQTT - for that the plugin needs no Miniserver "
         "credentials. For a direct call enter an address here; "
         "<span class='sm-mono'>{ziel}</span>, <span class='sm-mono'>{aktion}</span> and "
         "<span class='sm-mono'>{wert}</span> are replaced. <b>Credentials are shown masked "
         "here</b> - to change them, enter the whole address again."),
  H_VERSTEHEN=("Wie verstanden wird", "How understanding works"),
  H_WAKEWORD=("Das Weckwort muss der Wortwecker kennen. Welche er wirklich geladen hat, sagt "
              "der Knopf <i>Dienste befragen</i> im Reiter Test - was das Modell nicht kennt, "
              "weckt nicht.",
              "The wake word service must know the wake word. Which ones it has actually loaded "
              "is shown by the <i>Query services</i> button on the Test tab - what the model "
              "does not know will not wake anything."),
  H_WARTEZEIT=("Wie lange die Oberfläche und der Miniserver auf die Antwort des Dienstes "
               "warten. Mehr als 12 Sekunden nimmt ein Webserver ohnehin nicht an; der Dienst "
               "arbeitet den Befehl trotzdem zu Ende.",
               "How long the interface and the Miniserver wait for the service to answer. A web "
               "server will not accept more than 12 seconds anyway; the service finishes the "
               "command regardless."),
  K_RESTART=("Dienst neu starten", "Restart service"),
  K_START=("Dienst starten", "Start service"),
  K_STOP=("Dienst anhalten", "Stop service"),
  L_ANSAGE_ABSTAND_S=("Mindestabstand zwischen Ansagen (Sekunden)",
                      "Minimum gap between announcements (seconds)"),
  L_ANSAGE_JE_TAG=("Höchstzahl Ansagen je Tag", "Maximum announcements per day"),
  L_ANTWORT=("Antwort über den Lautsprecher sprechen", "Speak the answer via the loudspeaker"),
  L_ANTWORTWEG=("Gesprochene Antwort", "Spoken answer"),
  L_BESTAETIGUNG_S=("Rückfrage bei heiklen Zielen (Sekunden)",
                    "Confirmation for sensitive targets (seconds)"),
  L_KONTEXT_S=("Kontext für Folgesätze (Sekunden)", "Context for follow-up sentences (seconds)"),
  L_LLM=("Sprachmodell", "Language model"),
  L_LLM_EIN=("Sprachmodell als Rückfallebene benutzen", "Use the language model as a fallback"),
  L_MQTT_EIN=("Erkannte Absicht per MQTT veröffentlichen", "Publish recognised intent via MQTT"),
  L_MQTT_TOPIC=("Themen-Präfix", "Topic prefix"),
  L_PIPER=("Sprachausgabe (Piper)", "Speech synthesis (Piper)"),
  L_RUHE_BIS=("Ruhezeit bis", "Quiet hours until"),
  L_RUHE_EIN=("Ruhezeit einschalten", "Enable quiet hours"),
  L_RUHE_VON=("Ruhezeit von", "Quiet hours from"),
  L_SPRACHE=("Sprache", "Language"),
  L_TTS_IP=("Adresse des Music Servers", "Music Server address"),
  L_TTS_LANG=("Sprache der Ansage", "Announcement language"),
  L_TTS_MODE=("Art der Audioausgabe", "Type of audio output"),
  L_TTS_PORT=("Port des Music Servers", "Music Server port"),
  L_TTS_STIMME=("Stimme der Ansage", "Announcement voice"),
  L_TTS_TEMPLATE=("Eigene Vorlage", "Custom template"),
  L_TTS_VOLUME=("Lautstärke (1-100)", "Volume (1-100)"),
  L_TTS_ZONES=("Zonen", "Zones"),
  L_URL=("Adresse für den unmittelbaren Miniserver-Aufruf",
         "Address for the direct Miniserver call"),
  L_URL_LOESCHEN=("Diese Adresse löschen", "Delete this address"),
  L_VERLAUF_ZEILEN=("Verlauf aufbewahren (Zeilen)", "Keep history (lines)"),
  L_WAKE=("Wortwecker (openWakeWord)", "Wake word (openWakeWord)"),
  L_WAKEWORD=("Weckwort", "Wake word"),
  L_WARTEZEIT=("Wartezeit auf die Antwort des Dienstes (Sekunden)",
               "Wait for the service to answer (seconds)"),
  L_WHISPER=("Spracherkennung (Whisper)", "Speech recognition (Whisper)"),
  TTS_AUDIOSERVER=("Originaler Loxone Audioserver (über Loxone Config)",
                   "Original Loxone Audioserver (via Loxone Config)"),
  TTS_CUSTOM=("Eigene Vorlage", "Custom template"),
  TTS_MS4H=("MusicServer4Home / Audioserver4Home", "MusicServer4Home / Audioserver4Home"),
  TTS_MUSICSERVER=("Loxone Music Server (klassisch)", "Loxone Music Server (classic)"),
  T_ADRESSE=("Adresse", "Address"),
  T_DIENST=("Dienst", "Service"),
  T_PORT=("Port", "Port"),
  VERSTEHEN_ERKLAERUNG=("<b>Erst Satzmuster, dann Sprachmodell.</b> Das ist keine "
                        "Sparmaßnahme, sondern die bessere Reihenfolge: Ein Mustervergleich "
                        "braucht Millisekunden und kann sich nicht irren - er trifft oder er "
                        "trifft nicht. Ein Sprachmodell braucht auf einem kleinen Rechner "
                        "Sekunden und kann danebenliegen. Für 'Licht an' will man das erste. "
                        "Für 'mach es hier drin ein bisschen gemütlicher' das zweite.",
                        "<b>Patterns first, language model second.</b> This is not a cost "
                        "saving but the better order: a pattern match takes milliseconds and "
                        "cannot be wrong - it matches or it does not. A language model takes "
                        "seconds on a small machine and can be off. For 'lights on' you want "
                        "the first. For 'make it a bit cosier in here' the second."),
  WAS_IST_DAS=("<b>Alles bleibt im Haus.</b> Kein Wort verlässt das Heimnetz: das Mikrofon "
               "schickt sein Audio an den LoxBerry, dort erkennt Whisper den Text, Satzmuster "
               "machen daraus eine Absicht, und der Miniserver schaltet. Die Antwort spricht "
               "Piper - ebenfalls hier. Es gibt keinen Anbieter, der mithören könnte, weil es "
               "keinen Anbieter gibt.",
               "<b>Everything stays in the house.</b> Not a word leaves the home network: the "
               "microphone sends its audio to the LoxBerry, Whisper turns it into text, "
               "patterns turn that into an intent, and the Miniserver switches. Piper speaks "
               "the answer - here as well. There is no provider that could listen in, because "
               "there is no provider."),
  WEG_BEIDE=("Mikrofon und Loxone", "Microphone and Loxone"),
  WEG_LOXONE=("nur Loxone (Music Server / Audioserver)", "Loxone only (Music Server)"),
  WEG_SATELLIT=("nur das Mikrofon (Piper)", "microphone only (Piper)"),
  )

s("LOXIMP",
  H_TITEL=("Ziele aus Loxone übernehmen", "Adopt targets from Loxone"),
  ERKLAERUNG=("Der Miniserver kennt Ihre Geräteliste bereits - jeden Baustein mit Raum und "
              "Anzeigenamen. Statt sie abzutippen, lässt sie sich einmal holen und dann "
              "anhaken. <b>Drei Dinge dazu:</b> Es bleibt ein <i>Vorschlag</i> - übernommen "
              "wird nur, was Sie anhaken. Die Zugangsdaten werden <b>einmal benutzt und nicht "
              "gespeichert</b>; abgelegt wird nur die Vorschlagsliste, und darin stehen Namen, "
              "keine Kennwörter. Und die Satzmuster bleiben unberührt - es kommen nur Ziele "
              "dazu.",
              "The Miniserver already knows your device list - every block with its room and "
              "display name. Instead of typing it out, it can be fetched once and then ticked. "
              "<b>Three notes:</b> it stays a <i>suggestion</i> - only what you tick is "
              "adopted. The credentials are <b>used once and not stored</b>; only the "
              "suggestion list is kept, and it contains names, not passwords. And the sentence "
              "patterns are left untouched - only targets are added."),
  L_HOST=("Adresse des Miniservers", "Miniserver address"),
  L_BENUTZER=("Benutzer", "User"),
  L_KENNWORT=("Kennwort", "Password"),
  H_KENNWORT=("Wird nur für diesen einen Abruf benutzt und nirgends gespeichert.",
              "Used only for this single fetch and stored nowhere."),
  K_HOLEN=("Vorschläge holen", "Fetch suggestions"),
  K_UEBERNEHMEN=("Angehakte übernehmen", "Adopt ticked entries"),
  K_VERWERFEN=("Vorschläge verwerfen", "Discard suggestions"),
  T_ART=("Art", "Type"),
  SCHON_DA=("schon eingetragen", "already present"),
  PRUEFEN=("<b>Bitte durchsehen, bevor Sie übernehmen.</b> Der Miniserver führt oft mehr "
           "Bausteine, als man ansprechen will. Was hier nicht angehakt ist, kommt auch nicht "
           "in die Zielliste; die Namen lassen sich danach in der Tabelle oben noch ändern.",
           "<b>Please review before adopting.</b> The Miniserver often carries more blocks than "
           "you want to address. What is not ticked here does not enter the target list; the "
           "names can still be changed in the table above afterwards."),
  GEFUNDEN=("%d brauchbare Ziele aus %d Bausteinen der Strukturdatei.",
            "%d usable targets out of %d blocks in the structure file."),
  NICHTS=("In der Strukturdatei stand kein Baustein, der sich als Ziel eignet.",
          "The structure file contained no block usable as a target."),
  NICHTS_GEWAEHLT=("Es war nichts angehakt - es wurde nichts übernommen.",
                   "Nothing was ticked - nothing was adopted."),
  UEBERNOMMEN=("%d Ziele übernommen, %d waren schon eingetragen. Die Satzmuster sind "
               "unberührt geblieben.",
               "%d targets adopted, %d were already present. The sentence patterns were left "
               "untouched."),
  VERWORFEN=("Die Vorschläge wurden verworfen.", "The suggestions were discarded."),
  FEHLER_HOST=("Das ist keine gültige Adresse für den Miniserver.",
               "That is not a valid Miniserver address."),
  FEHLER_STUMM=("%s hat nicht geantwortet. Adresse und Netz prüfen.",
                "%s did not answer. Check address and network."),
  FEHLER_401=("Der Miniserver hat die Zugangsdaten abgelehnt (401).",
              "The Miniserver rejected the credentials (401)."),
  FEHLER_HTTP=("Der Miniserver antwortete mit HTTP %d.",
               "The Miniserver answered with HTTP %d."),
  FEHLER_FORM=("Die Antwort war keine Strukturdatei - es fehlt die Liste der Bausteine.",
               "The answer was not a structure file - the list of blocks is missing."),
  )

s("MQTT",
  EINLEITUNG=("Hier steht alles, was MQTT betrifft: der Zustand des Gateways, das einzutragende "
              "Abo, die vollständige Themenliste und die Einstellungen. MQTT ist der Regelweg "
              "zum Miniserver - dafür braucht das Plugin keine Zugangsdaten.",
              "Everything concerning MQTT is here: the gateway state, the subscription to "
              "enter, the full topic list and the settings. MQTT is the standard path to the "
              "Miniserver - the plugin needs no credentials for it."),
  H_ZUSTAND=("Zustand des Gateways", "Gateway state"),
  H_ABO=("Das Abo", "The subscription"),
  H_THEMEN=("Was veröffentlicht wird", "What is published"),
  H_EINSTELLEN=("Einstellungen", "Settings"),
  # Die Themenzeile steht VOR der Verzweigung und gilt in beiden Faellen -
  # sie ist eine Auskunft, keine Aufforderung.
  ABO_EINLEITUNG=("Die Themengruppe dieses Plugins lautet:",
                  "The topic group of this plugin is:"),
  ABO_V1_TITEL=("Gateway V1: Abo eintragen", "Gateway V1: enter the subscription"),
  ABO_V1=("Diese Zeile in <i>System → MQTT Gateway</i> unter <i>Subscriptions</i> eintragen und speichern.",
          "Enter that line in <i>System → MQTT Gateway</i> under <i>Subscriptions</i> and save."),
  ABO_V1_WARNUNG=("<b>Ohne diesen Eintrag kommt am Miniserver nichts an.</b> Das ist die "
                  "häufigste Fehlerursache überhaupt.",
                  "<b>Without this entry nothing reaches the Miniserver.</b> This is the most "
                  "common cause of failure of all."),
  ABO_V2_TITEL=("Gateway V2: nichts einzutragen", "Gateway V2: nothing to enter"),
  ABO_V2=("<b>MQTT-Gateway V2 erkennt die Themengruppe von selbst</b> — einzutragen ist "
          "hier nichts. In den <i>Subscriptions</i> erscheint die Gruppe, sobald das "
          "Plugin zum ersten Mal etwas gesendet hat; dort werden die gewünschten "
          "Datenpunkte einzeln angehakt.",
          "<b>MQTT gateway V2 detects the topic group by itself</b> — there is nothing to "
          "enter here. The group appears under <i>Subscriptions</i> once the plugin has "
          "published for the first time; the desired data points are ticked there "
          "individually."),
  ABO_UNBEKANNT=("Die Fassung des Gateways ließ sich nicht lesen. Deshalb stehen oben beide "
                 "Wege - welcher gilt, sieht man in <i>System → MQTT Gateway</i>: gibt es dort "
                 "ein Eingabefeld für Abos, ist es V1.",
                 "The gateway version could not be read. Both ways are therefore shown above - "
                 "which one applies is visible in <i>System → MQTT Gateway</i>: if there is an "
                 "input field for subscriptions, it is V1."),
  THEMEN_ERKLAERUNG=("Bei jedem verstandenen Satz und - falls der Herzschlag eingeschaltet ist "
                     "- regelmäßig auch ohne Anlass.",
                     "On every understood sentence and - if the heartbeat is enabled - "
                     "regularly without any trigger."),
  EMPFEHLUNG=("<b>Der bequemste Weg</b> ist die Zeile mit dem Zielthema: je Ziel ein eigenes Thema. Ein virtueller Eingang hängt dann genau an <span class='sm-mono'>wohnzimmer/licht/aktion</span> und braucht keine Fallunterscheidung im Miniserver. Schritt 3 im Reiter <i>Einbindung in Loxone</i> nennt die Namen dieser Eingänge für jedes Ziel.",
    "<b>The most convenient way</b> is the row with the target topic: one topic per target. A virtual input then hangs on exactly <span class='sm-mono'>wohnzimmer/licht/aktion</span> and needs no case distinction in the Miniserver. Step 3 on the <i>Loxone integration</i> tab lists the names of these inputs for every target."),
  L_HERZSCHLAG=("Herzschlag alle (Sekunden)", "Heartbeat every (seconds)"),
  H_HERZSCHLAG=("Ohne Herzschlag geht über MQTT nur etwas hinaus, wenn jemand spricht - ein "
                "toter Dienst ist dann von einem stillen Haus nicht zu unterscheiden. 0 "
                "schaltet ihn ab.",
                "Without a heartbeat, MQTT only carries something when someone speaks - a dead "
                "service is then indistinguishable from a quiet house. 0 disables it."),
  A_NICHT_GEFUNDEN=("kein MQTT-Abschnitt in der general.json",
                    "no MQTT section in general.json"),
  A_AUTOSTART_AUS=("aus - unter System, MQTT Gateway einschalten",
                   "off - enable under System, MQTT Gateway"),
  A_FASSUNG_UNBEKANNT=("nicht lesbar", "not readable"),
  T_GEFUNDEN=("Gateway gefunden", "Gateway found"),
  T_AUTOSTART=("Autostart", "Autostart"),
  T_BROKER=("Broker", "Broker"),
  T_UDP=("UDP-Eingang", "UDP input"),
  T_FASSUNG=("Fassung", "Version"),
  T_THEMA=("Thema", "Topic"),
  T_BEDEUTUNG=("Bedeutung", "Meaning"),
  T_RETAIN=("zurückbehalten", "retained"),
  B_SATZ=("Der gehörte Satz, Leerzeichen als Unterstrich",
          "The sentence heard, spaces as underscores"),
  B_ABSICHT=("Was gemeint war: schalten, dimmen, frage",
             "What was meant: switch, dim, question"),
  B_AKTION=("Was zu tun ist: ein, aus, wert", "What to do: on, off, value"),
  B_ZIEL=("Der Schlüssel des Geräts aus der Zielliste",
          "The key of the device from the target list"),
  B_WERT=("Die genannte Zahl, falls eine fiel", "The number mentioned, if any"),
  B_EINHEIT=("Die Einheit dazu, etwa Prozent oder Grad",
             "The matching unit, e.g. percent or degrees"),
  B_QUELLE=("muster oder llm - woher die Deutung kam",
            "pattern or llm - where the interpretation came from"),
  B_MIKROFON=("Welches Mikrofon zugehört hat - damit weiß Loxone, aus welchem Raum der Befehl "
              "kam", "Which microphone listened - so Loxone knows which room the command came "
              "from"),
  B_ZEIT=("Zeitstempel des Satzes", "Timestamp of the sentence"),
  RETAIN_ERKLAERUNG=("<b>Zurückbehalten</b> heißt: der Broker hebt den letzten Wert auf und "
                     "gibt ihn jedem neuen Abonnenten sofort. Nach einem Neustart des "
                     "Miniservers oder des Gateways steht der Zustand damit sofort wieder da, "
                     "ohne auf den nächsten Herzschlag zu warten. Zustände werden "
                     "zurückbehalten, Messwerte mit Zeitbezug nicht - sonst sähe ein Wert von "
                     "gestern wie einer von jetzt aus. Das Lebenszeichen "
                     "(<span class='sm-mono'>online</span>, <span class='sm-mono'>ts</span>) "
                     "wird nie zurückbehalten: es stünde für immer auf 'lebt'. Ebenso nie "
                     "zurückbehalten werden Aussagen des Dienstes über sich selbst - das "
                     "Ergebnis des letzten Satzes (<span class='sm-mono'>ok</span>, "
                     "<span class='sm-mono'>grund</span>, <span class='sm-mono'>antwort</span>) "
                     "und seine Verbindungen (<span class='sm-mono'>bereit</span>, "
                     "<span class='sm-mono'>dienste_ok</span>) - und "
                     "<span class='sm-mono'>ruhe</span>, weil die Ruhezeit allein mit der Uhr "
                     "wechselt. Die Befehle an die Ziele (<span class='sm-mono'>thema/aktion</span>, "
                     "<span class='sm-mono'>thema/wert</span>) gehen ebenfalls flüchtig: nach "
                     "einem Neustart von Broker oder Gateway sollen sie nicht noch einmal ankommen. "
                     "Seit 0.11.10; der alte Wert wird gelöscht, bis der Broker bestätigt, dass "
                     "keiner mehr dasteht.",
                     "<b>Retained</b> means the broker keeps the last value and hands it to "
                     "every new subscriber straight away. After a restart of the Miniserver or "
                     "the gateway the state is there again immediately, without waiting for the "
                     "next heartbeat. States are retained, time-related readings are not - "
                     "otherwise yesterday's value would look like a current one. The heartbeat "
                     "(<span class='sm-mono'>online</span>, <span class='sm-mono'>ts</span>) is "
                     "never retained: it would read 'alive' forever. Likewise never retained "
                     "are statements of the service about itself - the result of the last "
                     "sentence (<span class='sm-mono'>ok</span>, "
                     "<span class='sm-mono'>grund</span>, <span class='sm-mono'>antwort</span>) "
                     "and its connections (<span class='sm-mono'>bereit</span>, "
                     "<span class='sm-mono'>dienste_ok</span>) - and "
                     "<span class='sm-mono'>ruhe</span>, because quiet hours change with the "
                     "clock alone. The commands to the targets (<span class='sm-mono'>thema/aktion</span>, "
                     "<span class='sm-mono'>thema/wert</span>) are transient as well: after a "
                     "restart of the broker or the gateway they must not arrive a second time. "
                     "Since 0.11.10; the old value is deleted until the broker confirms that "
                     "none is left."),
  RETAIN_GEMESSEN=("<b>Am Gerät gemessen (13.09.2026):</b> der UDP-Eingang des Gateways nimmt "
                   "das Befehlswort <span class='sm-mono'>retain</span> an; die so gesendeten "
                   "Themen lagen danach zurückbehalten im Broker, die mit "
                   "<span class='sm-mono'>publish</span> gesendeten nicht. Bis 0.11.4 ging "
                   "alles flüchtig hinaus. Im Haus läuft Gateway <b>Version 1</b>. Ein leerer "
                   "Wert geht immer flüchtig - eine leere Nutzlast löscht ein zurückbehaltenes "
                   "Thema.",
                   "<b>Measured on the device (13 Sep 2026):</b> the gateway UDP inlet accepts "
                   "the command word <span class='sm-mono'>retain</span>; topics sent that way "
                   "were then held in the broker, those sent with "
                   "<span class='sm-mono'>publish</span> were not. Up to 0.11.4 everything was "
                   "sent transiently. This house runs gateway <b>version 1</b>. An empty value "
                   "is always sent transiently - an empty payload deletes a retained topic."),
  B_ZIELWERT=("Der Zahlenwert unter dem Thema des Ziels - nur wenn der Satz einen nennt",
              "The numeric value under the target topic - only when the sentence names one"),
  B_ZIELTHEMA=("Dasselbe noch einmal unter dem Thema des Ziels - der bequemste Weg in Loxone. Seit 0.12.5 geht es 2 Sekunden später auf „-“ zurück, so wirkt derselbe Befehl auch zweimal hintereinander",
    "The same again under the target's own topic - the most convenient way in Loxone. Since 0.12.5 it returns to “-” 2 seconds later, so the same command also works twice in a row"),
  B_ANTWORT=("Der fertige Antwortsatz als Text - für einen virtuellen Texteingang in der Visu",
             "The finished answer as text - for a virtual text input in the visualisation"),
  B_OK=("1 verstanden und ausgeführt, 0 nicht verstanden",
        "1 understood and executed, 0 not understood"),
  B_GRUND=("Woran es lag, wenn nicht: kein_muster, ziel_unbekannt, ziel_fehlt, llm_fehler",
           "What went wrong if not: no pattern, unknown target, missing target, model error"),
  B_ANSAGE=("Der Text für den Textgenerator - nur im Modus 'Originaler Loxone Audioserver'",
            "The text for the text generator - only in mode 'original Loxone Audioserver'"),
  B_ONLINE=("1, solange der Dienst lebt; 0 beim geordneten Anhalten",
            "1 while the service is alive; 0 on an orderly stop"),
  B_TS=("Zeitstempel des Herzschlags - läuft weiter, solange der Dienst lebt",
        "Heartbeat timestamp - keeps running as long as the service is alive"),
  B_BEREIT=("Anzahl der verbundenen Mikrofone", "Number of connected microphones"),
  B_MIKROFONE=("Anzahl der eingetragenen Mikrofone - 0 heißt: keines eingerichtet",
               "Number of configured microphones - 0 means none set up"),
  B_DIENSTE_GESAMT=("Anzahl der geprüften Sprachdienste - der Nenner zu dienste_ok",
                    "Number of voice services checked - the denominator of dienste_ok"),
  B_DIENSTE_OK=("Anzahl der erreichbaren Sprachdienste",
                "Number of reachable voice services"),
  B_REGELN=("Anzahl der Satzmuster - 0 heißt: die Satzdatei ist weg",
            "Number of sentence patterns - 0 means the sentence file is gone"),
  B_ZIELE=("Anzahl der Ziele", "Number of targets"),
  B_RUHE=("1 = es wird gerade nichts angesagt", "1 = announcements are currently suppressed"),
  B_LETZTER=("Sekunden seit dem letzten verstandenen Satz",
             "Seconds since the last understood sentence"),
  )

s("MIKRO",
  ERKLAERUNG=("Zwei Familien, beide vollständig lokal:<br><b>Wyoming</b> - jeder Linux-Rechner "
              "mit Mikrofon, auf dem <span class='sm-mono'>wyoming-satellite</span> läuft. Ein "
              "Raspberry Pi Zero 2 W mit USB-Mikrofon kostet unter 30 Euro und genügt "
              "vollauf.<br><b>ESPHome</b> - die fertig kaufbaren Kleingeräte: M5Stack Atom "
              "Echo, Home Assistant Voice Preview Edition, ESP32-S3-BOX. Sie brauchen den "
              "Noise-Schlüssel aus ihrer ESPHome-Einrichtung.",
              "Two families, both entirely local:<br><b>Wyoming</b> - any Linux machine with a "
              "microphone running <span class='sm-mono'>wyoming-satellite</span>. A Raspberry "
              "Pi Zero 2 W with a USB microphone costs under 30 euros and is entirely "
              "sufficient.<br><b>ESPHome</b> - the ready-made small devices: M5Stack Atom Echo, "
              "Home Assistant Voice Preview Edition, ESP32-S3-BOX. They need the noise key from "
              "their ESPHome setup."),
  RAUM_ERKLAERUNG=("<b>Raum und Zone sind neu und lohnen sich.</b> Im Feld <i>Raum</i> steht "
                   "ein Ziel aus der Zielliste - es gilt, wenn der Satz selbst keines nennt. "
                   "Damit wird aus 'mach das Licht im Wohnzimmer an' schlicht 'mach an', "
                   "gesprochen im Wohnzimmer. Im Feld <i>Zone</i> steht die Music-Server-Zone "
                   "dieses Raums; die Antwort kommt dann dort an und nicht im ganzen Haus.",
                   "<b>Room and zone are new and worth setting.</b> The <i>Room</i> field holds "
                   "a target from the target list - it applies when the sentence names none. "
                   "That turns 'switch on the living room light' into simply 'switch on', "
                   "spoken in the living room. The <i>Zone</i> field holds the Music Server "
                   "zone of that room; the answer then arrives there and not throughout the "
                   "house."),
  ESPHOME_WARNUNG=("<b>Ehrliche Einordnung:</b> Bis 0.9.11 gab es diesen Weg gar nicht - das "
                   "Gerät wurde verbunden, danach geschah nichts. Von 0.10.0 bis 0.10.2 waren "
                   "die Rückrufe zwar eingetragen, aber unbrauchbar: die Bibliothek verlangt "
                   "Koroutinen, es waren gewöhnliche Funktionen, und einer nahm ein Argument "
                   "zu wenig. Es kam nie ein Ton an, und es ging kein einziges Ereignis zurück "
                   "- das Gerät hielt sich für dauerhaft mitten in einer Anfrage. Seit 0.11.0 "
                   "ist der Weg gegen das Originalpaket aioesphomeapi gebaut, seit 0.11.1 dazu gegen die ESPHome-<b>Firmware</b> selbst: sie liest aus jedem Ereignis bestimmte Werte und steigt bei leerem Wert aus - ohne Text im TTS_START startet sie den Lautsprecher nie, ohne Adresse im TTS_END wechselt sie nie in den Zustand, in dem der Puffer geleert wird. Das Audio wird außerdem getaktet, weil ihr Lautsprecherpuffer nur eine halbe Sekunde faßt. <b>Am Gerät gemessen ist der Weg weiterhin nicht</b> - hier steht keines. Ein Fehler dort reißt die Wyoming-Mikrofone nicht mit; jedes läuft für sich.",
                   "<b>An honest assessment:</b> until 0.9.11 this path did not exist - the "
                   "device connected and then nothing happened. From 0.10.0 to 0.10.2 the "
                   "callbacks were registered but unusable: the library requires coroutines, "
                   "these were plain functions, and one took an argument too few. No audio "
                   "ever arrived, and not a single event went back - the device believed it "
                   "was permanently mid-request. Since 0.11.0 the path is built and measured "
                   "against the original aioesphomeapi package, and since 0.11.1 against the ESPHome <b>firmware</b> itself: it reads specific values out of each event and bails out on an empty one - without text in TTS_START it never starts the speaker, without a url in TTS_END it never enters the state in which the buffer is drained. The audio is also paced, because its speaker buffer holds only half a second. <b>It is still not measured on a device</b> - there is none here. A fault there does not drag the Wyoming microphones down; each runs on its own."),
  ANTWORTET=("antwortet", "responding"),
  FEHLER_HOST=("Zeile %d: Das ist keine gültige Adresse.", "Row %d: that is not a valid address."),
  FEHLER_HOST_FEHLT=("Zeile %d: Ein Mikrofon braucht eine Adresse.",
                     "Row %d: a microphone needs an address."),
  FEHLER_PORT=("Zeile %d: Der Port muss eine Zahl von 1 bis 65535 sein.",
               "Row %d: the port must be a number from 1 to 65535."),
  FEHLER_ZONE=("Zeile %d: Eine Zone besteht aus Ziffern, Komma und der Tilde.",
               "Row %d: a zone consists of digits, commas and the tilde."),
  GESPEICHERT=("Die Mikrofone wurden gespeichert. Der Dienst übernimmt sie ohne Neustart.",
               "The microphones were saved. The service picks them up without a restart."),
  G_ATOM=("Klein und billig, aber nur ein Mikrofon und ein leiser Lautsprecher.",
          "Small and cheap, but only one microphone and a quiet loudspeaker."),
  G_BOX=("Mit Bildschirm. Braucht eine passende ESPHome-Einrichtung.",
         "With a screen. Needs a matching ESPHome setup."),
  G_LINUX=("Wer ein Mikrofon am LoxBerry hat, braucht kein zweites Gerät.",
           "With a microphone on the LoxBerry itself no second device is needed."),
  G_LINUX_NAME=("Beliebiger Linux-Rechner (auch der LoxBerry selbst)",
                "Any Linux machine (including the LoxBerry itself)"),
  G_PI=("Günstigster Einstieg. wyoming-satellite installieren, fertig.",
        "Cheapest entry. Install wyoming-satellite, done."),
  G_RESPEAKER=("Mehrere Mikrofone, deutlich besser bei Nebengeräuschen.",
               "Several microphones, much better with background noise."),
  G_VOICEPE=("Fertiggerät mit Weckwort im Gerät, Lautsprecher und Drehknopf.",
             "Ready-made device with on-device wake word, loudspeaker and dial."),
  HILFE=("Vorgabeports: Wyoming <span class='sm-mono'>10700</span>, ESPHome "
         "<span class='sm-mono'>6053</span>. Eine leere Zeile wird übergangen; wer ein Mikrofon "
         "löschen will, leert Name und Adresse.",
         "Default ports: Wyoming <span class='sm-mono'>10700</span>, ESPHome "
         "<span class='sm-mono'>6053</span>. An empty row is skipped; to delete a microphone, "
         "clear name and address."),
  H_PRUEFEN=("Einzeln prüfen", "Check individually"),
  H_TITEL=("Mikrofone", "Microphones"),
  H_WELCHE=("Welche Geräte gehen", "Which devices work"),
  K_PRUEFEN=("%s prüfen", "Check %s"),
  PRUEFEN_ERKLAERUNG=("Fragt nur nach, ob unter der eingetragenen Adresse jemand antwortet. Es "
                      "wird nichts geschaltet und nichts aufgenommen.",
                      "Only asks whether anything responds at the configured address. Nothing "
                      "is switched and nothing is recorded."),
  SCHLUESSEL_DA=("gespeichert - leer lassen zum Beibehalten",
                 "stored - leave empty to keep"),
  SCHLUESSEL_LEER=("nur für ESPHome", "ESPHome only"),
  T_ART=("Art", "Type"),
  T_GERAET=("Gerät", "Device"),
  T_HINWEIS=("Hinweis", "Note"),
  T_HOST=("Adresse", "Address"),
  T_NAME=("Name", "Name"),
  T_PORT=("Port", "Port"),
  T_RAUM=("Raum (Vorgabeziel)", "Room (default target)"),
  T_SCHLUESSEL=("Noise-Schlüssel", "Noise key"),
  T_ZONE=("Zone", "Zone"),
  T_ZUSTAND=("Zustand", "State"),
  )

s("SATZ",
  H_ZIELE=("Ziele", "Targets"),
  ZIELE_ERKLAERUNG=("Ein Ziel ist ein Gerät, das angesprochen werden kann. <b>Schlüssel</b> ist "
                    "der interne Name (Buchstaben, Ziffern, Unterstrich), <b>Name</b> der, den "
                    "die Anlage ausspricht, <b>Aliasse</b> sind alle Bezeichnungen, unter denen "
                    "man es sonst noch nennt - durch Komma getrennt. <b>Thema</b> ist das "
                    "MQTT-Thema in Loxone. <b>Lesen</b> ist eine Adresse, unter der sich der "
                    "Ist-Wert abrufen lässt; nur damit kann die Anlage Fragen beantworten "
                    "(Platzhalter <span class='sm-mono'>{istwert}</span> im Antworttext).",
                    "A target is a device that can be addressed. <b>Key</b> is the internal name "
                    "(letters, digits, underscore), <b>Name</b> the one the system speaks, "
                    "<b>Aliases</b> are all other ways of naming it - comma separated. "
                    "<b>Topic</b> is the MQTT topic in Loxone. <b>Read</b> is an address the "
                    "current value can be fetched from; only with it can the system answer "
                    "questions (placeholder <span class='sm-mono'>{istwert}</span> in the "
                    "answer text)."),
  ZIELE_HILFE=("Eine neue Zeile ohne Schlüssel und ohne Namen wird übergangen; ein gespeichertes "
               "Ziel löscht der Haken <i>Löschen</i> seiner Zeile. Der Haken <i>Rückfrage</i> lässt die Anlage bei "
               "diesem Ziel erst nachfragen, statt sofort zu schalten - gedacht für Tore, "
               "Schlösser und alles, was man nicht versehentlich auslösen will.",
               "A new row without key and name is skipped; a saved target is deleted with the "
               "<i>Delete</i> checkbox in its row. "
               "The <i>Confirm</i> checkbox makes the system ask back for this target instead "
               "of switching at once - meant for gates, locks and anything you do not want to "
               "trigger by accident."),
  K_ZIELE_SPEICHERN=("Ziele speichern", "Save targets"),
  ZIELE_GESPEICHERT=("Die Ziele wurden gespeichert. Die Satzmuster sind unberührt geblieben.",
                     "The targets were saved. The sentence patterns were left untouched."),
  FEHLER_SCHLUESSEL=("Zeile %d: ein Ziel braucht einen Schlüssel (Buchstaben, Ziffern, "
                     "Unterstrich).",
                     "Row %d: a target needs a key (letters, digits, underscore)."),
  FEHLER_DOPPELT=("Den Schlüssel '%s' gibt es zweimal.", "The key '%s' exists twice."),
  FEHLER_THEMA=("Ziel '%s': das Thema darf nur Buchstaben, Ziffern, Bindestrich, Unterstrich "
                "und Schrägstrich enthalten.",
                "Target '%s': the topic may only contain letters, digits, hyphen, underscore "
                "and slash."),
  FEHLER_LESEN=("Ziel '%s': die Leseadresse muss mit http:// oder https:// beginnen.",
                "Target '%s': the read address must start with http:// or https://."),
  BEARBEITEN_WARNUNG=("Hier steht die Datei so, wie sie ist. Beim Speichern wird geprüft, ob es "
                      "gültiges JSON ist und ob jede Regel ein Muster hat - <b>kaputtes JSON "
                      "wird abgewiesen und NICHT gespeichert</b>, damit eine laufende Anlage "
                      "nicht durch einen Tippfehler verstummt. Ein Kommaproblem ist ärgerlich, "
                      "eine stumme Anlage ärgerlicher.",
                      "This is the file as it is. On saving it is checked whether it is valid "
                      "JSON and whether every rule has a pattern - <b>broken JSON is rejected "
                      "and NOT saved</b>, so a running system is not silenced by a typo. A "
                      "misplaced comma is annoying, a silent system more so."),
  REIHENFOLGE_WARNUNG=("<b>Die Reihenfolge entscheidet.</b> Es gilt die ERSTE Regel, die passt. "
                       "Genauere Muster gehören deshalb nach oben: "
                       "<span class='sm-mono'>[schalte|mach] {ziel} [aus|ab]</span> passt auch "
                       "auf 'mach das Wohnzimmer in 10 Minuten aus' - der Befehl wäre dann "
                       "sofort ausgeführt statt vorgemerkt. Der Selbsttest prüft das und nennt "
                       "die verdeckte Regel beim Namen.",
                       "<b>Order matters.</b> The FIRST matching rule wins. More specific "
                       "patterns therefore belong at the top: "
                       "<span class='sm-mono'>[turn|switch] {ziel} off</span> also matches "
                       "'switch the living room off in 10 minutes' - the command would then be "
                       "executed at once instead of scheduled. The self-test checks this and "
                       "names the shadowed rule."),
  B_ALT=("Eine der Alternativen", "One of the alternatives"),
  B_DAUER=("Eine Zeitangabe - der Befehl wird vorgemerkt und später ausgeführt",
           "A time span - the command is scheduled and executed later"),
  B_ISTWERT=("Der gelesene Ist-Wert des Ziels (braucht 'Lesen' am Ziel)",
             "The target's current value (requires 'Read' on the target)"),
  B_LEER=("Eine leere Alternative heißt: darf auch fehlen",
          "An empty alternative means: may also be absent"),
  B_REST=("Beliebiger Text - steht im Antworttext zur Verfügung",
          "Arbitrary text - available in the answer text"),
  B_WERT=("Eine Zahl - als Ziffern oder als Wort ('fünfzig')",
          "A number - as digits or as a word"),
  B_ZIEL=("Ein Gerät aus der Zielliste. Darf fehlen: dann gilt der Raum des Mikrofons",
          "A device from the target list. May be absent: the microphone's room then applies"),
  ERKLAERUNG=("Ein Satzmuster ist eine Schablone. Passt der gesprochene Satz darauf, steht "
              "sofort fest, was zu tun ist - ohne Raten. Beim Vergleich werden Groß- und "
              "Kleinschreibung, Umlaute und Zeichensetzung eingeebnet: "
              "<span class='sm-mono'>Küche</span> und <span class='sm-mono'>kueche</span> sind "
              "dasselbe.",
              "A sentence pattern is a template. If the spoken sentence matches it, what to do "
              "is immediately clear - no guessing. Case, umlauts and punctuation are normalised "
              "for the comparison: <span class='sm-mono'>Küche</span> and "
              "<span class='sm-mono'>kueche</span> are the same."),
  FEHLER_JSON=("Das ist kein gültiges JSON - es wurde NICHTS gespeichert.",
               "That is not valid JSON - NOTHING was saved."),
  FEHLER_MUSTER=("Regel %d hat kein Muster.", "Rule %d has no pattern."),
  FEHLER_REGELN=("Es fehlt die Liste 'regeln'.", "The list 'regeln' is missing."),
  FEHLER_ZIELE=("Es fehlt die Liste 'ziele'.", "The list 'ziele' is missing."),
  FEHLER_ZIEL_FORM=("Das Ziel '%s' hat weder einen Block noch ein Thema als Text.",
                    "Target '%s' has neither a block nor a topic as text."),
  GESPEICHERT=("Die Sätze wurden gespeichert.", "The sentences were saved."),
  H_BEARBEITEN=("Datei bearbeiten", "Edit the file"),
  H_TITEL=("Satzmuster", "Sentence patterns"),
  NEU_LADEN=("Der Dienst liest die Datei von selbst neu, sobald sie sich ändert - ein Neustart "
             "ist nicht nötig.",
             "The service reloads the file by itself as soon as it changes - no restart needed."),
  T_ALIAS=("Wie man es sonst noch nennt", "Other names for it"),
  T_BEDEUTUNG=("Bedeutung", "Meaning"),
  T_BEISPIEL=("Beispiel", "Example"),
  T_BESTAETIGEN=("Rückfrage", "Confirm"),
  T_EINHEIT=("Einheit", "Unit"),
  T_LESEN=("Lesen (Adresse für den Ist-Wert)", "Read (address for the current value)"),
  T_NAME=("Name", "Name"),
  T_SCHLUESSEL=("Schlüssel", "Key"),
  T_THEMA=("Thema in Loxone", "Topic in Loxone"),
  T_ZEICHEN=("Zeichen", "Symbol"),
  )

s("SICHER",
  H_TITEL=("Sichern und zurückspielen", "Backup and restore"),
  ERKLAERUNG=("Die Satzdatei ist der eigentliche Wert dieses Plugins - Regeln, Ziele, "
              "Aliasnamen, Themen. <b>Aktionstoken, Miniserver-Adresse und die Schlüssel der "
              "ESPHome-Mikrofone gehen absichtlich NICHT mit:</b> in ihnen stecken "
              "Zugangsdaten, und eine Sicherungsdatei liegt am Ende im Download-Ordner eines "
              "Rechners, der nicht der LoxBerry ist. Beim Zurückspielen bleiben sie ebenfalls "
              "unangetastet - die Adressen im Miniserver behalten also ihre Gültigkeit.",
              "The sentence file is the real value of this plugin - rules, targets, aliases, "
              "topics. <b>The action token, the Miniserver address and the ESPHome noise keys "
              "are deliberately NOT included:</b> they contain credentials, and a backup file "
              "ends up in the download folder of a machine that is not the LoxBerry. On restore "
              "they are left untouched as well - so the addresses in the Miniserver stay valid."),
  K_HOLEN=("Sicherung herunterladen", "Download backup"),
  K_EINSPIELEN=("Sicherung einspielen", "Restore backup"),
  L_DATEI=("Sicherungsdatei auswählen", "Select backup file"),
  FEHLER_KEINE_DATEI=("Es wurde keine Datei hochgeladen.", "No file was uploaded."),
  )

s("LOX",
  EINLEITUNG=("Die Sprachsteuerung sagt Loxone, WAS gemeint war. Was daraus wird, entscheidet der Miniserver - so bleibt die Logik dort, wo sie hingehört. Sechs Schritte; in den Schritten 2 bis 4 steht je eine fertig verbundene Seite aus dem LoxBerry-Plugins Musterprojekt mit Anleitung, Tabelle und Bild.",
    "The voice control tells Loxone WHAT was meant. What comes of it is decided by the Miniserver - so the logic stays where it belongs. Six steps; steps 2 to 4 each carry a fully connected page from the LoxBerry plugins sample project with instructions, table and picture."),
  H_TITEL=("Einbindung in Loxone, Schritt für Schritt", "Loxone integration, step by step"),
  IMPORT_WARNUNG=("<b>Loxone Config legt beim Import neu an und überschreibt nichts.</b> "
                  "Zweimal importiert heißt doppelte Objekte. Und die Adresse im Kopf der "
                  "Datei ist ein <b>Vorschlag</b>: sie stammt aus dem Namen, unter dem Sie "
                  "diese Seite gerade aufgerufen haben, und muss nicht der sein, unter dem der "
                  "Miniserver den LoxBerry erreicht. Nach dem Import einmal nachsehen.",
                  "<b>Loxone Config creates new objects on import and overwrites nothing.</b> "
                  "Importing twice means duplicate objects. And the address in the file header "
                  "is a <b>suggestion</b>: it comes from the name you used to open this page, "
                  "which need not be the one the Miniserver uses to reach the LoxBerry. Check "
                  "it after importing."),
  KEINE_ZIELE_VORLAGE=("Es ist kein Ziel eingetragen - für die Zielvorlage gibt es nichts zu "
                       "bauen.",
                       "No targets are configured - there is nothing to build for the target "
                       "template."),
  K_TOKEN_NEU=("Neues Token erzeugen", "Generate new token"),
  K_VORLAGE=("Vorlage: Zustand (Eingang)", "Template: status (input)"),
  K_VORLAGE_ZIELE=("Vorlage: je Ziel ein Eingang", "Template: one input per target"),
  K_VORLAGE_AUSGANG=("Vorlage: Befehle (Ausgang)", "Template: commands (output)"),
  S1_TITEL=("Schritt 1: MQTT einrichten", "Step 1: set up MQTT"),
  S1_TEXT=("Alles, was MQTT betrifft, steht im Reiter <i>MQTT</i>: der Zustand des Gateways, das einzutragende Abo und die vollständige Themenliste. Ohne diesen Schritt kommen keine Sprachbefehle am Miniserver an (Schritt 3); der Zustand (Schritt 2) und die Ansagen (Schritt 4) gehen über HTTP.",
    "Everything concerning MQTT is on the <i>MQTT</i> tab: the gateway state, the subscription to enter and the full topic list. Without this step no voice commands reach the Miniserver (step 3); the state (step 2) and the announcements (step 4) go via HTTP."),
  S3_TITEL=("Schritt 2: Zustand der Anlage überwachen", "Step 2: monitor the system state"),
  S3_TEXT=("Ein virtueller HTTP-Eingang, der den Zustand holt. Wichtig sind vor allem <span class='sm-mono'>BEREIT</span> - wie viele Mikrofone gerade wirklich verbunden sind - und <span class='sm-mono'>DIENSTE</span>: ein toter Whisper-Container sieht sonst genauso aus wie eine gesunde Anlage. Ein Mikrofon, das seit Tagen nicht antwortet, fällt niemandem auf, bis man davor steht und redet. Steht der LoxBerry selbst, behalten alle Eingänge ihren letzten Wert; nur das Lebenszeichen <span class='sm-mono'>ZAEHLER</span> verrät es (seit 0.12.5, mit <span class='sm-mono'>DIENSTE_GESAMT</span>).",
    "A virtual HTTP input that fetches the state. The important ones are <span class='sm-mono'>BEREIT</span> - how many microphones are really connected - and <span class='sm-mono'>DIENSTE</span>: otherwise a dead Whisper container looks exactly like a healthy system. A microphone that has not answered for days goes unnoticed until you stand in front of it and speak. If the LoxBerry itself stops, all inputs keep their last value; only the sign of life <span class='sm-mono'>ZAEHLER</span> gives it away (since 0.12.5, with <span class='sm-mono'>DIENSTE_GESAMT</span>)."),
  S4_TITEL=("Schritt 4: Loxone spricht",
    "Step 4: Loxone speaks"),
  S4_TEXT=("Es geht auch andersherum: Loxone kann die Anlage etwas sagen lassen, ihr einen Satz unterschieben, als hätte ihn jemand gesprochen, oder die Ansagen stilllegen. Ein <i>Virtueller Ausgang</i> mit der Adresse des LoxBerry genügt - oder gleich die fertige Vorlage (Knopf unten).",
    "It also works the other way round: Loxone can have the system say something, feed it a sentence as if someone had spoken it, or mute announcements. A <i>virtual output</i> with the LoxBerry address is enough - or simply the ready-made template (button below)."),
  S4_ANSAGE=("<b>Das ist mehr wert, als es klingt.</b> Eine Ansage 'Das Garagentor steht seit "
             "einer Stunde offen' im richtigen Raum erreicht mehr als jede Meldung auf einem "
             "Bildschirm, den niemand ansieht. Und der Satzweg macht die Sprachlogik auch für "
             "Taster nutzbar.",
             "<b>This is worth more than it sounds.</b> An announcement 'the garage door has "
             "been open for an hour' in the right room achieves more than any message on a "
             "screen nobody looks at. And the sentence path makes the voice logic usable from "
             "push buttons too."),
  S5_TITEL=("Schritt 5: Das Token",
    "Step 5: the token"),
  S5_TEXT=("Der Endpunkt liegt im unangemeldeten Bereich, damit Loxone ihn ohne Zugangsdaten "
           "erreicht, und ist deshalb durch ein Token geschützt. Mit "
           "<span class='sm-mono'>?selftest=1</span> lässt sich prüfen, ob es noch stimmt, "
           "<b>ohne dass etwas passiert</b> - die Alternative wäre, das Haus zum Reden zu "
           "bringen. Ein neues Token macht alle bereits eingetragenen Adressen ungültig.",
           "The endpoint lives in the unauthenticated area so Loxone can reach it without "
           "credentials, and is therefore protected by a token. With "
           "<span class='sm-mono'>?selftest=1</span> you can check whether it is still correct "
           "<b>without anything happening</b> - the alternative would be to make the house "
           "talk. A new token invalidates all addresses already entered."),
  S7_TITEL=("Schritt 6: Gegenprobe", "Step 6: cross-check"),
  S7_TEXT=("Diese Adressen im Browser aufrufen. Der erste sagt, ob das Token stimmt, ohne dass "
           "etwas passiert.",
           "Call these addresses in a browser. The first one says whether the token is correct "
           "without anything happening."),
  A_DIAG=("Klartextbefund samt Handgriffen", "plain-text findings with next steps"),
  TOKEN_NEU=("Es wurde ein neues Token erzeugt. <b>Die Adressen in Loxone müssen angepasst "
             "werden.</b>",
             "A new token was generated. <b>The addresses in Loxone must be updated.</b>"),
  T_ADRESSE=("Adresse", "Address"),
  T_BAUSTEIN=("Baustein (Typ)", "Block (type)"),
  T_BEDEUTUNG=("Bedeutung", "Meaning"),
  T_BEFEHL=("Befehlserkennung", "Command recognition"),
  T_EINGAENGE=("Eingänge verbinden mit", "Connect inputs to"),
  T_ERWARTUNG=("Erwartete Antwort", "Expected answer"),
  T_GRENZEN=("Grenzen", "Limits"),
  T_NAMENSVORSCHLAG=("Name",
    "Name"),
  T_PARAMETER=("Parameter", "Parameter"),
  T_PRUEFUNG=("Aufruf", "Call"),
  T_SELFTEST=("Token prüfen, ohne etwas auszulösen",
              "Check the token without triggering anything"),
  T_TITEL=("Titel (Vorschlag)", "Title (suggestion)"),
  T_TOKEN=("Aktuelles Token", "Current token"),
  T_VA_ADRESSE=("Adresse des virtuellen Ausgangs", "Virtual output address"),
  T_VA_ANSAGE=("Befehl bei EIN: etwas ansagen", "Command on ON: make an announcement"),
  T_VA_ZONE=("Ansage in einer bestimmten Zone", "Announcement in a specific zone"),
  T_VA_DRINGEND=("Ansage trotz Ruhezeit (Alarm)", "Announcement despite quiet hours (alarm)"),
  T_VA_SATZ=("Befehl bei EIN: einen Satz verarbeiten lassen",
             "Command on ON: process a sentence"),
  T_VA_RUHE=("Ansagen stilllegen (wert=0 gibt sie wieder frei)",
             "Mute announcements (wert=0 releases them again)"),
  SCHRITTE_TITEL=("So übernehmen Sie diese Seite",
    "How to take over this page"),
  HINWEISE_TITEL=("Hinweise",
    "Notes"),
  BILD_ALT=("Bausteine der Seite „%s“ in Loxone Config",
    "Blocks of the page “%s” in Loxone Config"),
  BILD_UNTERSCHRIFT=("Seite „%s“ im LoxBerry-Plugins Musterprojekt. Config kürzt lange Bausteinnamen – Namen siehe Tabelle.",
    "Page “%s” in the LoxBerry plugins sample project. Config shortens long block names – see the table for the full names."),
  MUSTERPROJEKT=("Die ganze Projektdatei mit allen Plugin-Seiten und Vorlagen: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry-Plugins Musterprojekt</a>",
    "The complete project file with all plugin pages and templates: <a href='https://github.com/timanders22/LoxBerry-Plugins-Musterprojekt' target='_blank' rel='noopener'>LoxBerry plugins sample project</a>"),
  SB_TITEL=("Schritt 3: Sprachbefehle in Loxone",
    "Step 3: voice commands in Loxone"),
  SB_TEXT=("Ein verstandener Befehl kommt über das MQTT-Gateway in Loxone an: je Ziel ein <i>Virtueller Texteingang</i> für die Aktion (<span class='sm-mono'>ein</span>, <span class='sm-mono'>aus</span>, <span class='sm-mono'>wert</span>) und ein <i>Virtueller Eingang</i> für die Zahl. Das Gateway vergibt die Namen selbst – Präfix und Thema mit „_“ statt „/“. Die Tabelle nennt sie für jedes eingetragene Ziel; seit 0.12.5 geht die Aktion 2 Sekunden nach jedem Befehl auf „-“ zurück.",
    "An understood command reaches Loxone via the MQTT gateway: per target a <i>Virtual Text Input</i> for the action (<span class='sm-mono'>ein</span>, <span class='sm-mono'>aus</span>, <span class='sm-mono'>wert</span>) and a <i>Virtual Input</i> for the number. The gateway assigns the names itself – prefix and topic with “_” instead of “/”. The table lists them for every configured target; since 0.12.5 the action returns to “-” 2 seconds after each command."),
  SB_KEINE_ZIELE=("Es ist noch kein Ziel eingetragen (Reiter Sätze) – die Namen entstehen aus dem Thema des Ziels.",
    "No target is configured yet (Sentences tab) – the names are formed from the topic of the target."),
  T_ZIEL=("Ziel",
    "Target"),
  T_GW_AKTION=("Virtueller Texteingang (Aktion)",
    "Virtual Text Input (action)"),
  T_GW_WERT=("Virtueller Eingang (Zahl)",
    "Virtual Input (number)"),
  SB_UDP=("Die Vorlage „je Ziel ein Eingang“ wirkt nur, wenn das Gateway UDP sendet – im Haus läuft es über HTTP, dort bekäme sie nie einen Wert (ungeprüft). Ohne Gateway, mit Zugang zum Miniserver, geht auch der Direktaufruf je Ziel (Spalte „Adresse (eigener Miniserver)“ der Ziele im Reiter Sätze).",
    "The template “one input per target” only works if the gateway sends via UDP – in the house it runs via HTTP, where it would never get a value (not tested). Without the gateway, with access to the Miniserver, the direct call per target also works (column “Address (own Miniserver)” of the targets in the Sentences tab)."),
  VORLAGE_KOMMENTAR=("Erzeugt vom LoxBerry-Plugin Sprachsteuerung lokal (%s)",
    "Generated by the LoxBerry plugin Sprachsteuerung lokal (%s)"),
  VQ_ANSAGE=("Ein: sagt den festen Text an. Den Text hinter text= anpassen; Leerzeichen als %20 schreiben.",
    "On: announces the fixed text. Adjust the text after text=; write spaces as %20."),
  VQ_TUERKLINGEL=("Ein: sagt „Es hat an der Haustür geklingelt“ an; in der Ruhezeit still.",
    "On: announces “Es hat an der Haustür geklingelt” (the doorbell rang); silent during quiet hours."),
  VQ_ALARM=("Ein: sagt den Text dringend an – auch in der Ruhezeit und wenn Loxone stillgelegt hat.",
    "On: announces the text urgently – also during quiet hours and when Loxone has muted announcements."),
  VQ_SATZ=("Ein: schickt einen Satz durch dieselbe Kette wie ein gesprochener. Damit lässt sich die Sprachlogik auch von einem Taster aus benutzen.",
    "On: sends a sentence through the same chain as a spoken one. This makes the voice logic usable from a push button too."),
  VQ_RUHE=("Ein schaltet die Ruhezeit ein (keine Ansagen), Aus wieder ab. Damit lässt sich die Nachtruhe aus Loxone steuern.",
    "On switches quiet hours on (no announcements), Off switches them off again. This lets Loxone control the night-time quiet."),
  )

s("BAUSTEIN",
  # ---- Welle Bild 18 (Sprachsteuerung 0.12.5, 17.10.2026; Entwurf Welle 18 ss, E1-E13): drei Seiten aus
  # dem LoxBerry-Plugins Musterprojekt - Tabellenzeilen Zn_mm = "Typ | Name | Parameter | Eingaenge" (Zeilen
  # mit Prozentzeichen doppelt, ueber sprintf), Kaesten SEITEn_SCHRITTm (Klartext), Hinweise SEITEn_Hm (HTML);
  # sp_bausteinliste() in htmlauth/index.php. Die alte Liste (43 Schluessel, sp_bausteine()) ist entfallen.
  Z1_01=("Virtueller HTTP-Eingang-Befehl (Vorlage „Sprachsteuerung lokal“) | SPRACHSTEUERUNG_OK | 1 = der Sprachdienst läuft, 0 = gestoppt (wird bei jeder Abfrage neu geprüft) | —",
    "Virtual HTTP Input Command (template “Sprachsteuerung lokal”) | SPRACHSTEUERUNG_OK | 1 = the voice service is running, 0 = stopped (checked anew on every poll) | —"),
  Z1_02=("Virtueller HTTP-Eingang-Befehl (Vorlage „Sprachsteuerung lokal“) | SPRACHSTEUERUNG_MIKROFONE | Anzahl der eingetragenen Mikrofone | —",
    "Virtual HTTP Input Command (template “Sprachsteuerung lokal”) | SPRACHSTEUERUNG_MIKROFONE | Number of configured microphones | —"),
  Z1_03=("Virtueller HTTP-Eingang-Befehl (Vorlage „Sprachsteuerung lokal“) | SPRACHSTEUERUNG_BEREIT | Anzahl der gerade verbundenen Mikrofone | —",
    "Virtual HTTP Input Command (template “Sprachsteuerung lokal”) | SPRACHSTEUERUNG_BEREIT | Number of microphones currently connected | —"),
  Z1_04=("Virtueller HTTP-Eingang-Befehl (Vorlage „Sprachsteuerung lokal“) | SPRACHSTEUERUNG_DIENSTE | Anzahl der erreichbaren Sprachdienste (Whisper, Piper und – wenn im Plugin eingeschaltet – Sprachmodell) | —",
    "Virtual HTTP Input Command (template “Sprachsteuerung lokal”) | SPRACHSTEUERUNG_DIENSTE | Number of reachable voice services (Whisper, Piper and – if switched on in the plugin – language model) | —"),
  Z1_05=("Virtueller HTTP-Eingang-Befehl (Vorlage „Sprachsteuerung lokal“) | SPRACHSTEUERUNG_REGELN | Anzahl der geladenen Satzmuster; 0 = die Satzdatei fehlt | —",
    "Virtual HTTP Input Command (template “Sprachsteuerung lokal”) | SPRACHSTEUERUNG_REGELN | Number of loaded sentence patterns; 0 = the sentence file is missing | —"),
  Z1_06=("Virtueller HTTP-Eingang-Befehl (Vorlage „Sprachsteuerung lokal“) | SPRACHSTEUERUNG_ZIELE | Anzahl der eingetragenen Ziele (Geräte, die man per Sprache schalten kann) | —",
    "Virtual HTTP Input Command (template “Sprachsteuerung lokal”) | SPRACHSTEUERUNG_ZIELE | Number of configured targets (devices that can be switched by voice) | —"),
  Z1_07=("Virtueller HTTP-Eingang-Befehl (Vorlage „Sprachsteuerung lokal“) | SPRACHSTEUERUNG_RUHE | 1 = es wird gerade nichts angesagt (Ruhezeit im Plugin oder von Loxone stillgelegt) | —",
    "Virtual HTTP Input Command (template “Sprachsteuerung lokal”) | SPRACHSTEUERUNG_RUHE | 1 = nothing is announced at the moment (quiet hours in the plugin or muted by Loxone) | —"),
  Z1_08=("Virtueller HTTP-Eingang-Befehl (Vorlage „Sprachsteuerung lokal“) | SPRACHSTEUERUNG_LETZTER | Sekunden seit dem letzten verstandenen Satz; -1 = noch keiner | —",
    "Virtual HTTP Input Command (template “Sprachsteuerung lokal”) | SPRACHSTEUERUNG_LETZTER | Seconds since the last understood sentence; -1 = none yet | —"),
  Z1_09=("Virtueller HTTP-Eingang-Befehl (Vorlage „Sprachsteuerung lokal“) | SPRACHSTEUERUNG_ALTER | Sekunden, seit der Dienst seinen Zustand zuletzt geschrieben hat (läuft er, höchstens etwa 15); -1 = noch nie | —",
    "Virtual HTTP Input Command (template “Sprachsteuerung lokal”) | SPRACHSTEUERUNG_ALTER | Seconds since the service last wrote its state (at most about 15 while it runs); -1 = never | —"),
  Z1_10=("Virtueller HTTP-Eingang-Befehl (Vorlage „Sprachsteuerung lokal“) | SPRACHSTEUERUNG_ZAEHLER | Lebenszeichen: 0 bis 999, läuft um und ändert sich mindestens alle 15 Sekunden, solange der Dienst arbeitet; -1 = noch nie | —",
    "Virtual HTTP Input Command (template “Sprachsteuerung lokal”) | SPRACHSTEUERUNG_ZAEHLER | Sign of life: 0 to 999, wraps around and changes at least every 15 seconds while the service works; -1 = never | —"),
  Z1_11=("Virtueller HTTP-Eingang-Befehl (Vorlage „Sprachsteuerung lokal“) | SPRACHSTEUERUNG_DIENSTE_GESAMT | Anzahl der geprüften Sprachdienste (der Nenner zu DIENSTE; ein abgeschaltetes Sprachmodell zählt nicht mit) | —",
    "Virtual HTTP Input Command (template “Sprachsteuerung lokal”) | SPRACHSTEUERUNG_DIENSTE_GESAMT | Number of voice services checked (the denominator of DIENSTE; a switched-off language model does not count) | —"),
  Z1_12=("Konstante | Konstante 1 | Wert 1 | —",
    "Constant | Konstante 1 | Value 1 | —"),
  Z1_13=("Analogwertvalidierung | Lebenszeichen fehlt (Sprachsteuerung) | Tmc 180 s (drei Abfragen à 60 s ohne neues Lebenszeichen), Min -1, Max 999 – steht der LoxBerry, bleiben alle Werte stehen und nur der stehende Zähler verrät es; Haken bei ‚En‘ im Eigenschaftsfenster entfernen | V = #10, En = #12",
    "Value Validator | Lebenszeichen fehlt (Sprachsteuerung) | Tmc 180 s (three polls of 60 s without a new sign of life), Min -1, Max 999 – if the LoxBerry stops, all values stay as they are and only the stopped counter gives it away; remove the tick at ‘En’ in the properties window | V = #10, En = #12"),
  Z1_14=("NICHT | Keine frischen Daten (Sprachsteuerung) | — (Sprachdienst gestoppt) | I = #1",
    "NOT | Keine frischen Daten (Sprachsteuerung) | — (voice service stopped) | I = #1"),
  Z1_15=("Formel | Sprachdienste ausgefallen (Sprachsteuerung) | I1-I2 (geprüfte minus erreichbare Sprachdienste; 0 = alle antworten) | I1 = #11, I2 = #4",
    "Formula | Sprachdienste ausgefallen (Sprachsteuerung) | I1-I2 (checked minus reachable voice services; 0 = all respond) | I1 = #11, I2 = #4"),
  Z1_16=("Schwellwertschalter | Sprachdienst fehlt (Sprachsteuerung) | Ein 0,5 / Aus 0,25 (ab einem ausgefallenen Dienst ein; Zahlenwert, kein 0/1-Feld) | Eingang = #15",
    "Threshold Switch | Sprachdienst fehlt (Sprachsteuerung) | On 0.5 / Off 0.25 (on from one failed service; numeric value, not a 0/1 field) | Input = #15"),
  Z1_17=("ODER | Dienst gestoppt oder Sprachdienst fehlt (Sprachsteuerung) | — (linieneigener Zwischenschritt; die 600 s danach schlucken den Impuls des Schwellwertschalters) | I1 = #14, I2 = #16",
    "OR | Dienst gestoppt oder Sprachdienst fehlt (Sprachsteuerung) | — (step specific to this line; the 600 s afterwards swallow the pulse of the threshold switch) | I1 = #14, I2 = #16"),
  Z1_18=("ODER | Störung (Sprachsteuerung) | — (keine frischen Daten oder Lebenszeichen fehlt) | I1 = #17, I2 = Ausgang E von #13",
    "OR | Störung (Sprachsteuerung) | — (no fresh data or sign of life missing) | I1 = #17, I2 = output E of #13"),
  Z1_19=("Einschaltverzögerung | Störung bestätigt (Sprachsteuerung) | 600 s (zehn Abfragen; ein Neustart, ein Update und eine einzelne Fehlabfrage melden nichts) | Eingang = #18",
    "Switch-On Delay | Störung bestätigt (Sprachsteuerung) | 600 s (ten polls; a restart, an update and a single failed poll report nothing) | Input = #18"),
  Z1_20=("Benachrichtigung | Meldung Plugin gestört (Sprachsteuerung) | Text: Sprachsteuerung – seit 10 Minuten läuft der Sprachdienst nicht, Whisper, Piper oder das Sprachmodell antworten nicht, oder der LoxBerry antwortet nicht. Sprachbefehle und Ansagen gehen dann nicht. In der App den Status „Zustand (Sprachsteuerung)“ lesen | Eingang = #19",
    "Notification | Meldung Plugin gestört (Sprachsteuerung) | Text: Sprachsteuerung – for 10 minutes the voice service has not been running, Whisper, Piper or the language model do not respond, or the LoxBerry does not respond. Voice commands and announcements do not work then. Read the status “Zustand (Sprachsteuerung)” in the app | Input = #19"),
  Z1_21=("Status | Zustand (Sprachsteuerung) | Zeilen: V1 = 1 „Lebenszeichen fehlt seit mindestens 3 Minuten – LoxBerry oder Plugin antwortet nicht; LoxBerry im Browser öffnen, im Plugin Reiter Einstellungen ‚Dienst starten‘“; V2 = 0 „Sprachdienst gestoppt – im Plugin Reiter Einstellungen ‚Dienst starten‘“; V3 = 0 „keine Satzmuster geladen – im Plugin Reiter Sätze eine Sicherung einspielen oder Muster eintragen“; V7 = 0 „kein Sprachdienst erreichbar – im Plugin Reiter Dienste die Container starten“; V8 > 0 „<v8> Sprachdienst(e) antworten nicht – im Plugin Reiter Dienste nachsehen“; V4 = 0 „läuft – kein Mikrofon eingetragen; Sätze kommen nur über Loxone und den Reiter Test (im Plugin Reiter Mikrofone eines hinzufügen)“; V6 > 0 „<v6> von <v4> Mikrofonen getrennt – Strom und WLAN prüfen, im Plugin Reiter Mikrofone nachsehen“; ohne Bedingung „läuft – <v5> von <v4> Mikrofonen verbunden, <v7> Sprachdienste erreichbar“; Visualisierung EIN | V1 = Ausgang E von #13, V2 = #1, V3 = #5, V4 = #2, V5 = #3, V6 = #22, V7 = #4, V8 = #15",
    "Status | Zustand (Sprachsteuerung) | Rows: V1 = 1 “sign of life missing for at least 3 minutes – LoxBerry or plugin does not answer; open the LoxBerry in the browser, in the plugin tab Settings ‘Start service’”; V2 = 0 “voice service stopped – in the plugin tab Settings ‘Start service’”; V3 = 0 “no sentence patterns loaded – in the plugin tab Sentences restore a backup or enter patterns”; V7 = 0 “no voice service reachable – start the containers in the plugin tab Services”; V8 > 0 “<v8> voice service(s) do not respond – look at the plugin tab Services”; V4 = 0 “running – no microphone configured; sentences only arrive via Loxone and the Test tab (add one in the plugin tab Microphones)”; V6 > 0 “<v6> of <v4> microphones disconnected – check power and Wi-Fi, look at the plugin tab Microphones”; without condition “running – <v5> of <v4> microphones connected, <v7> voice services reachable”; visualisation ON | V1 = output E of #13, V2 = #1, V3 = #5, V4 = #2, V5 = #3, V6 = #22, V7 = #4, V8 = #15"),
  Z1_22=("Formel | Mikrofone getrennt (Sprachsteuerung) | I1-I2 (eingetragene minus verbundene Mikrofone) | I1 = #2, I2 = #3",
    "Formula | Mikrofone getrennt (Sprachsteuerung) | I1-I2 (configured minus connected microphones) | I1 = #2, I2 = #3"),
  Z1_23=("Schwellwertschalter | Mikrofon getrennt (Sprachsteuerung) | Ein 0,5 / Aus 0,25 (ab einem getrennten Mikrofon ein) | Eingang = #22",
    "Threshold Switch | Mikrofon getrennt (Sprachsteuerung) | On 0.5 / Off 0.25 (on from one disconnected microphone) | Input = #22"),
  Z1_24=("Einschaltverzögerung | Mikrofon seit einer Stunde getrennt (Sprachsteuerung) | 3600 s (ein Mikrofon, das nach Stromausfall oder WLAN-Wechsel neu startet, meldet nichts) | Eingang = #23",
    "Switch-On Delay | Mikrofon seit einer Stunde getrennt (Sprachsteuerung) | 3600 s (a microphone that restarts after a power cut or a Wi-Fi change reports nothing) | Input = #23"),
  Z1_25=("Benachrichtigung | Meldung Mikrofon getrennt (Sprachsteuerung) | Text: Sprachsteuerung – ein Mikrofon ist seit einer Stunde nicht verbunden; in diesem Raum hört niemand zu. Strom und WLAN des Geräts prüfen, im Plugin Reiter Mikrofone nachsehen; in der App den Status „Zustand (Sprachsteuerung)“ lesen | Eingang = #24",
    "Notification | Meldung Mikrofon getrennt (Sprachsteuerung) | Text: Sprachsteuerung – a microphone has not been connected for an hour; nobody is listening in this room. Check the power and Wi-Fi of the device, look at the plugin tab Microphones; read the status “Zustand (Sprachsteuerung)” in the app | Input = #24"),
  Z1_26=("Status | Sprachbetrieb (Sprachsteuerung) | Zeilen: V4 > 60 „der Dienst hat seinen Zustand seit <v4> s nicht geschrieben – hängt er? Im Plugin Reiter Einstellungen ‚Dienst neu starten‘“; V3 = 0 „keine Ziele eingetragen – im Plugin Reiter Sätze Ziele eintragen oder ‚Ziele aus Loxone übernehmen‘“; V1 < 0 „noch kein Satz verstanden – <v3> Ziele eingetragen; im Plugin Reiter Test einen Satz durchschicken“; V2 = 1 „Ansagen still (Ruhezeit oder von Loxone stillgelegt) – letzter verstandener Satz vor <v1> s“; ohne Bedingung „letzter verstandener Satz vor <v1> s – <v3> Ziele, Ansagen frei“; Visualisierung EIN | V1 = #8, V2 = #7, V3 = #6, V4 = #9",
    "Status | Sprachbetrieb (Sprachsteuerung) | Rows: V4 > 60 “the service has not written its state for <v4> s – is it hanging? In the plugin tab Settings ‘Restart service’”; V3 = 0 “no targets configured – in the plugin tab Sentences enter targets or ‘Adopt targets from Loxone’”; V1 < 0 “no sentence understood yet – <v3> targets configured; send a sentence through in the plugin tab Test”; V2 = 1 “announcements muted (quiet hours or muted by Loxone) – last understood sentence <v1> s ago”; without condition “last understood sentence <v1> s ago – <v3> targets, announcements allowed”; visualisation ON | V1 = #8, V2 = #7, V3 = #6, V4 = #9"),
  Z2_01=("Virtueller Texteingang | sprachsteuerung_wohnzimmer_licht_aktion | von Hand anlegen, Name genau so (Name, den das MQTT-Gateway vergibt); was der letzte Satz für das Ziel „Licht im Wohnzimmer“ wollte: ein, aus oder wert (dimmen); 2 Sekunden später setzt das Plugin ihn auf „-“ zurück – so wirkt auch derselbe Befehl zweimal hintereinander | —",
    "Virtual Text Input | sprachsteuerung_wohnzimmer_licht_aktion | create by hand, name exactly like this (the name the MQTT gateway assigns); what the last sentence wanted for the target “Licht im Wohnzimmer”: ein, aus or wert (dim); 2 seconds later the plugin resets it to “-” – so the same command also works twice in a row | —"),
  Z2_02=("Virtueller Eingang (MQTT-Gateway) | sprachsteuerung_wohnzimmer_licht_wert | Analog ein; Anzeigename „Helligkeit per Sprache (Sprachsteuerung)“; die genannte Zahl in %% (0–100), nur wenn der Satz eine nennt („dimme das wohnzimmer auf 40“); Ausgang an den Helligkeitseingang des eigenen Dimmers (nicht Teil der Liste) | —",
    "Virtual Input (MQTT gateway) | sprachsteuerung_wohnzimmer_licht_wert | Analog on; display name “Helligkeit per Sprache (Sprachsteuerung)”; the number given in %% (0–100), only if the sentence names one (“dimme das wohnzimmer auf 40”); output to the brightness input of your own dimmer (not part of the list) | —"),
  Z2_03=("Status | Wohnzimmerlicht ein per Sprache (Sprachsteuerung) | Zeilen: V1 == „ein“ „per Sprache eingeschaltet“, Statuswert 1; ohne Bedingung „–“, Statuswert 0; Visualisierung AUS (nur Logik) | V1 = #1",
    "Status | Wohnzimmerlicht ein per Sprache (Sprachsteuerung) | Rows: V1 == “ein” “per Sprache eingeschaltet” (switched on by voice), status value 1; without condition “–”, status value 0; visualisation OFF (logic only) | V1 = #1"),
  Z2_04=("Status | Wohnzimmerlicht aus per Sprache (Sprachsteuerung) | Zeilen: V1 == „aus“ „per Sprache ausgeschaltet“, Statuswert 1; ohne Bedingung „–“, Statuswert 0; Visualisierung AUS (nur Logik) | V1 = #1",
    "Status | Wohnzimmerlicht aus per Sprache (Sprachsteuerung) | Rows: V1 == “aus” “per Sprache ausgeschaltet” (switched off by voice), status value 1; without condition “–”, status value 0; visualisation OFF (logic only) | V1 = #1"),
  Z2_05=("Flankenerkennung | Impuls Wohnzimmerlicht ein (Sprachsteuerung) | Pd 0,1 s; benutzt wird der Ausgang On (steigende Flanke); an den Einschalt-Eingang des eigenen Licht- oder Schaltbausteins (nicht Teil der Liste) | Eingang = Ausgang AQ von #3",
    "Edge Detection | Impuls Wohnzimmerlicht ein (Sprachsteuerung) | Pd 0.1 s; the output On (rising edge) is used; to the switch-on input of your own lighting or switching block (not part of the list) | Input = output AQ of #3"),
  Z2_06=("Flankenerkennung | Impuls Wohnzimmerlicht aus (Sprachsteuerung) | Pd 0,1 s; benutzt wird der Ausgang On; an den Aus-Eingang des eigenen Bausteins (nicht Teil der Liste) – an „Off“ einer Lichtsteuerung sperrt ein Impuls über 200 ms den Baustein, deshalb 0,1 s | Eingang = Ausgang AQ von #4",
    "Edge Detection | Impuls Wohnzimmerlicht aus (Sprachsteuerung) | Pd 0.1 s; the output On is used; to the off input of your own block (not part of the list) – at “Off” of a lighting controller a pulse longer than 200 ms locks the block, hence 0.1 s | Input = output AQ of #4"),
  Z2_07=("Virtueller Eingang (MQTT-Gateway) | sprachsteuerung_wohnzimmer_heizung_wert | Analog ein; Anzeigename „Solltemperatur per Sprache (Sprachsteuerung)“; genannte Temperatur in °C (das Ziel erlaubt 5–30), nur wenn der Satz eine nennt („stelle die heizung auf 21 grad“); Ausgang an den eigenen Sollwert, z. B. einen Analogspeicher vor dem Raumregler (nicht Teil der Liste) | —",
    "Virtual Input (MQTT gateway) | sprachsteuerung_wohnzimmer_heizung_wert | Analog on; display name “Solltemperatur per Sprache (Sprachsteuerung)”; temperature given in °C (the target allows 5–30), only if the sentence names one (“stelle die heizung auf 21 grad”); output to your own setpoint, e.g. an analog memory in front of the room controller (not part of the list) | —"),
  Z2_08=("Virtueller Eingang (MQTT-Gateway) | sprachsteuerung_ok | Analog ein; Anzeigename „Satz ausgeführt (Sprachsteuerung)“; 1 = verstanden und ausgeführt, 0 = nicht | —",
    "Virtual Input (MQTT gateway) | sprachsteuerung_ok | Analog on; display name “Satz ausgeführt (Sprachsteuerung)”; 1 = understood and executed, 0 = not | —"),
  Z2_09=("Virtueller Texteingang | sprachsteuerung_satz | Titel genau so (Name, den das MQTT-Gateway vergibt), „In Visualisierung verwenden“ an; der gehörte Satz, Leerzeichen als Unterstrich („schalte_das_licht_im_wohnzimmer_aus“) | —",
    "Virtual Text Input | sprachsteuerung_satz | title exactly like this (the name the MQTT gateway assigns), “Use in visualisation” on; the sentence heard, spaces as underscores (“schalte_das_licht_im_wohnzimmer_aus”) | —"),
  Z2_10=("Virtueller Texteingang | sprachsteuerung_grund | Titel genau so; warum ein Satz nicht ausgeführt wurde: kein_muster, ziel_unbekannt, ziel_fehlt, llm_fehler, rueckfrage …; „-“ = nichts zu melden | —",
    "Virtual Text Input | sprachsteuerung_grund | title exactly like this; why a sentence was not executed: kein_muster, ziel_unbekannt, ziel_fehlt, llm_fehler, rueckfrage …; “-” = nothing to report | —"),
  Z2_11=("Virtueller Texteingang | sprachsteuerung_antwort | Titel genau so, „In Visualisierung verwenden“ an; der Antwortsatz der Anlage | —",
    "Virtual Text Input | sprachsteuerung_antwort | title exactly like this, “Use in visualisation” on; the reply sentence of the system | —"),
  Z2_12=("Virtueller Texteingang | sprachsteuerung_mikrofon | Titel genau so; welches Mikrofon zugehört hat – damit weiß Loxone, aus welchem Raum der Befehl kam; „-“ ohne Mikrofon (Satz aus Loxone oder dem Reiter Test) | —",
    "Virtual Text Input | sprachsteuerung_mikrofon | title exactly like this; which microphone was listening – so Loxone knows which room the command came from; “-” without microphone (sentence from Loxone or from the Test tab) | —"),
  Z2_13=("Virtueller Texteingang | sprachsteuerung_ziel | Titel genau so; Schlüssel des Geräts aus der Zielliste, z. B. wohnzimmer_licht | —",
    "Virtual Text Input | sprachsteuerung_ziel | title exactly like this; key of the device from the target list, e.g. wohnzimmer_licht | —"),
  Z2_14=("Status | Letzter Sprachbefehl (Sprachsteuerung) | Zeilen: V1 = 1 und V3 == „vorgemerkt“ „vorgemerkt (<v4>): <v2> – <v5>“; V1 = 1 „ausgeführt (<v4>): <v2> → <v6> – <v5>“; V3 == „kein_muster“ „nicht verstanden (<v4>): <v2> – im Plugin Reiter Sätze ein Satzmuster ergänzen“; V3 == „ziel_unbekannt“ „Gerät nicht gefunden (<v4>): <v2> – im Plugin Reiter Sätze am Ziel einen Alias ergänzen“; V3 == „ziel_fehlt“ „kein Gerät genannt (<v4>): <v2> – das Gerät nennen oder im Plugin Reiter Mikrofone dem Mikrofon einen Raum geben“; V3 := „llm_“ „Sprachmodell antwortet nicht oder falsch – im Plugin Reiter Dienste nachsehen“; V3 == „rueckfrage“ „Rückfrage: <v5>“; V3 == „“ „seit dem Neustart noch kein Satz“; ohne Bedingung „nicht ausgeführt (<v3>): <v2> – <v5>“; Visualisierung EIN | V1 = #8, V2 = #9, V3 = #10, V4 = #12, V5 = #11, V6 = #13",
    "Status | Letzter Sprachbefehl (Sprachsteuerung) | Rows: V1 = 1 and V3 == “vorgemerkt” “vorgemerkt (<v4>): <v2> – <v5>” (scheduled); V1 = 1 “ausgeführt (<v4>): <v2> → <v6> – <v5>” (executed); V3 == “kein_muster” “nicht verstanden (<v4>): <v2> – im Plugin Reiter Sätze ein Satzmuster ergänzen” (not understood – add a sentence pattern in the plugin tab Sentences); V3 == “ziel_unbekannt” “Gerät nicht gefunden (<v4>): <v2> – im Plugin Reiter Sätze am Ziel einen Alias ergänzen” (device not found – add an alias at the target); V3 == “ziel_fehlt” “kein Gerät genannt (<v4>): <v2> – das Gerät nennen oder im Plugin Reiter Mikrofone dem Mikrofon einen Raum geben” (no device named – name it or give the microphone a room); V3 := “llm_” “Sprachmodell antwortet nicht oder falsch – im Plugin Reiter Dienste nachsehen” (language model does not answer); V3 == “rueckfrage” “Rückfrage: <v5>” (question back); V3 == “” “seit dem Neustart noch kein Satz” (no sentence since the restart); without condition “nicht ausgeführt (<v3>): <v2> – <v5>” (not executed); visualisation ON | V1 = #8, V2 = #9, V3 = #10, V4 = #12, V5 = #11, V6 = #13"),
  Z3_01=("Virtueller HTTP-Eingang-Befehl (Vorlage „Sprachsteuerung lokal“) | SPRACHSTEUERUNG_RUHE | 1 = es wird gerade nichts angesagt (weitere Instanz, derselbe Befehl wie auf Seite „Sprachsteuerung“) | —",
    "Virtual HTTP Input Command (template “Sprachsteuerung lokal”) | SPRACHSTEUERUNG_RUHE | 1 = nothing is announced at the moment (further instance, the same command as on page “Sprachsteuerung”) | —"),
  Z3_02=("Virtueller Eingang (Taste) | Türklingel (eigene Quelle) | 1 = es klingelt (weitere Instanz, derselbe Platzhalter wie auf „Dashboard Steuerung“, „Heimkino Steuerung“ und „Kodi-NG Wiedergabe“); im eigenen Projekt die Leitung vom eigenen Klingeltaster bzw. vom Klingelausgang des Bausteins Türsteuerung statt dieser Taste an Nr. 3 legen | —",
    "Virtual Input (Push Button) | Türklingel (eigene Quelle) | 1 = it rings (further instance, the same placeholder as on “Dashboard Steuerung”, “Heimkino Steuerung” and “Kodi-NG Wiedergabe”); in your own project connect your own bell push button or the bell output of the Door Controller block to no. 3 instead of this button | —"),
  Z3_03=("Virtueller Ausgang Befehl (Vorlage „Sprachsteuerung lokal - Befehle“) | Sprachsteuerung Ansage Türklingel | Befehl bei EIN: spricht „Es hat an der Haustür geklingelt“; in der Ruhezeit still; Wie und wo gesprochen wird, stellt man im Plugin ein (gemeinsames Sprachmodul, Reiter Einstellungen) – Loxone löst nur aus | Eingang = #2",
    "Virtual Output Command (template “Sprachsteuerung lokal - Befehle”) | Sprachsteuerung Ansage Türklingel | Command on ON: says “Es hat an der Haustür geklingelt” (someone rang at the front door); silent during quiet hours; How and where announcements are spoken is set in the plugin (shared voice module, Settings tab) – Loxone only triggers | Input = #2"),
  Z3_04=("Virtueller Eingang (Schalter) | Garagentor offen (eigene Quelle) | 1 = Tor offen; im eigenen Projekt die Leitung vom eigenen Torkontakt (Digitaleingang, Torantrieb) statt dieses Schalters an Nr. 5 legen | —",
    "Virtual Input (Switch) | Garagentor offen (eigene Quelle) | 1 = gate open; in your own project connect your own gate contact (digital input, gate drive) to no. 5 instead of this switch | —"),
  Z3_05=("Einschaltverzögerung | Garagentor seit einer Stunde offen (Sprachsteuerung) | 3600 s | Eingang = #4",
    "Switch-On Delay | Garagentor seit einer Stunde offen (Sprachsteuerung) | 3600 s | Input = #4"),
  Z3_06=("Virtueller Eingang (Taste) | Taste Testansage (Sprachsteuerung) | in der App; spricht die Garagentor-Ansage einmal zum Ausprobieren | —",
    "Virtual Input (Push Button) | Taste Testansage (Sprachsteuerung) | in the app; speaks the garage gate announcement once for trying it out | —"),
  Z3_07=("ODER | Ansage Garagentor auslösen (Sprachsteuerung) | — (Tor eine Stunde offen oder Taste) | I1 = #5, I2 = #6",
    "OR | Ansage Garagentor auslösen (Sprachsteuerung) | — (gate open for an hour or button) | I1 = #5, I2 = #6"),
  Z3_08=("Virtueller Ausgang Befehl (Vorlage „Sprachsteuerung lokal - Befehle“) | Sprachsteuerung Ansage | Befehl bei EIN: spricht „Das Garagentor steht seit einer Stunde offen“ (eigenen Text im Befehl eintragen; wahlweise nur in einer Zone oder an einem Lautsprecher, Adresszusatz im Plugin Reiter Einbindung); Wie und wo gesprochen wird, stellt man im Plugin ein (gemeinsames Sprachmodul, Reiter Einstellungen) – Loxone löst nur aus | Eingang = #7",
    "Virtual Output Command (template “Sprachsteuerung lokal - Befehle”) | Sprachsteuerung Ansage | Command on ON: says “Das Garagentor steht seit einer Stunde offen” (the garage gate has been open for an hour) (enter your own text in the command; optionally only in one zone or on one loudspeaker, address suffix in the plugin tab Integration); How and where announcements are spoken is set in the plugin (shared voice module, Settings tab) – Loxone only triggers | Input = #7"),
  Z3_09=("Virtueller Eingang (Schalter) | Wassermelder (eigene Quelle) | 1 = Wasser erkannt; im eigenen Projekt die Leitung vom eigenen Wassermelder statt dieses Schalters an Nr. 10 legen | —",
    "Virtual Input (Switch) | Wassermelder (eigene Quelle) | 1 = water detected; in your own project connect your own water detector to no. 10 instead of this switch | —"),
  Z3_10=("Virtueller Ausgang Befehl (Vorlage „Sprachsteuerung lokal - Befehle“) | Sprachsteuerung Alarm | Befehl bei EIN: spricht dringend „Wasseralarm im Keller“ – auch in der Ruhezeit und wenn Loxone stillgelegt hat; Wie und wo gesprochen wird, stellt man im Plugin ein (gemeinsames Sprachmodul, Reiter Einstellungen) – Loxone löst nur aus | Eingang = #9",
    "Virtual Output Command (template “Sprachsteuerung lokal - Befehle”) | Sprachsteuerung Alarm | Command on ON: says “Wasseralarm im Keller” urgently (water alarm in the basement) – also during quiet hours and when Loxone has muted announcements; How and where announcements are spoken is set in the plugin (shared voice module, Settings tab) – Loxone only triggers | Input = #9"),
  Z3_11=("Virtueller Eingang (Taste) | Taste Licht aus per Satz (Sprachsteuerung) | in der App oder an einem Taster; schickt den Satz „schalte das licht im wohnzimmer aus“ durch die Sprachlogik – das Ergebnis kommt wie ein gesprochener Befehl auf Seite „Sprachsteuerung Befehle“ an | —",
    "Virtual Input (Push Button) | Taste Licht aus per Satz (Sprachsteuerung) | in the app or on a push button; sends the sentence “schalte das licht im wohnzimmer aus” through the voice logic – the result arrives on page “Sprachsteuerung Befehle” like a spoken command | —"),
  Z3_12=("Virtueller Ausgang Befehl (Vorlage „Sprachsteuerung lokal - Befehle“) | Sprachsteuerung Satz | Befehl bei EIN: schickt „schalte das licht im wohnzimmer aus“ durch die Sprachlogik (eigenen Satz im Befehl eintragen, wie man ihn sprechen würde) | Eingang = #11",
    "Virtual Output Command (template “Sprachsteuerung lokal - Befehle”) | Sprachsteuerung Satz | Command on ON: sends “schalte das licht im wohnzimmer aus” through the voice logic (enter your own sentence in the command, the way you would say it) | Input = #11"),
  Z3_13=("Schaltuhr | Nachtruhe Ansagen (Sprachsteuerung) | EIN = keine Ansagen: täglich 22:00–07:00, in allen Betriebsarten (eigene Zeiten eintragen) | —",
    "Schedule | Nachtruhe Ansagen (Sprachsteuerung) | ON = no announcements: daily 22:00–07:00, in all operating modes (enter your own times) | —"),
  Z3_14=("Virtueller Eingang (Schalter) | Ansagen stilllegen (Sprachsteuerung) | in der App; Ein = keine Ansagen (Alarmansagen kommen trotzdem) | —",
    "Virtual Input (Switch) | Ansagen stilllegen (Sprachsteuerung) | in the app; On = no announcements (alarm announcements still come) | —"),
  Z3_15=("Virtueller Eingang (Schalter) | Niemand zu Hause (eigene Quelle) | 1 = alle sind weg (weitere Instanz, derselbe Platzhalter wie auf „Alexa NG“ und „Kodi-NG Wiedergabe“); im eigenen Projekt die Leitung von der eigenen Anwesenheit statt dieses Schalters an Nr. 17 legen | —",
    "Virtual Input (Switch) | Niemand zu Hause (eigene Quelle) | 1 = everybody is away (further instance, the same placeholder as on “Alexa NG” and “Kodi-NG Wiedergabe”); in your own project connect your own presence to no. 17 instead of this switch | —"),
  Z3_16=("ODER | Ansagen stilllegen, Teil 1 (Sprachsteuerung) | — (Nachtruhe oder Schalter) | I1 = #13, I2 = #14",
    "OR | Ansagen stilllegen, Teil 1 (Sprachsteuerung) | — (night quiet or switch) | I1 = #13, I2 = #14"),
  Z3_17=("ODER | Ansagen stilllegen gesamt (Sprachsteuerung) | — (dazu: niemand zu Hause) | I1 = #16, I2 = #15",
    "OR | Ansagen stilllegen gesamt (Sprachsteuerung) | — (plus: nobody at home) | I1 = #16, I2 = #15"),
  Z3_18=("Virtueller Ausgang Befehl (Vorlage „Sprachsteuerung lokal - Befehle“) | Sprachsteuerung Ruhe | Befehl bei EIN: Ansagen im Plugin stilllegen; Befehl bei AUS: wieder frei. Gilt auch für Ansagen, die andere Plugins über die Sprachsteuerung sprechen lassen (z. B. Intercom beim Klingeln); die Ruhezeit im Plugin dann ausgeschaltet lassen | Eingang = #17",
    "Virtual Output Command (template “Sprachsteuerung lokal - Befehle”) | Sprachsteuerung Ruhe | Command on ON: mute announcements in the plugin; command on OFF: allowed again. Also applies to announcements that other plugins have the voice control speak (e.g. Intercom when the bell rings); then leave the quiet hours in the plugin switched off | Input = #17"),
  Z3_19=("Virtueller Eingang (MQTT-Gateway) | sprachsteuerung_ansage_ok | Analog ein; Anzeigename „Letzte Ansage angekommen (Sprachsteuerung)“; 1 = angekommen, 0 = nicht, -1 = gesendet, Ausgang unklar; kommt nur mit „Dauerhafte Verbindung zum Broker“ (Plugin Reiter MQTT, ab Werk aus) – ohne sie bleibt 0 stehen; nur Anzeige, keine Meldung daran | —",
    "Virtual Input (MQTT gateway) | sprachsteuerung_ansage_ok | Analog on; display name “Letzte Ansage angekommen (Sprachsteuerung)”; 1 = arrived, 0 = not, -1 = sent, outcome unclear; only comes with “Permanent connection to the broker” (plugin tab MQTT, off by default) – without it 0 stays; display only, no message on it | —"),
  Z3_20=("Virtueller Texteingang | sprachsteuerung_ansage_grund | Titel genau so (Name, den das MQTT-Gateway vergibt); Grund, wenn die letzte Ansage nicht ankam; „-“ bei Erfolg; nur mit Dauerverbindung | —",
    "Virtual Text Input | sprachsteuerung_ansage_grund | title exactly like this (the name the MQTT gateway assigns); reason if the last announcement did not arrive; “-” on success; only with the permanent connection | —"),
  Z3_21=("Virtueller Texteingang | sprachsteuerung_ansage | Titel genau so; nur bei Ausgabeart „Original Loxone Audioserver“ (sonst spricht das Plugin selbst – dann weglassen): der Ansagetext, Ausgang an den TTS-Eingang des eigenen Audioserver-Bausteins (nicht Teil der Liste) | —",
    "Virtual Text Input | sprachsteuerung_ansage | title exactly like this; only with output type “Original Loxone Audioserver” (otherwise the plugin speaks itself – then leave it out): the announcement text, output to the TTS input of your own Audioserver block (not part of the list) | —"),
  Z3_22=("Status | Ansagen (Sprachsteuerung) | Zeilen: V2 = 1 und V1 = 1 „still – von Loxone stillgelegt (Nachtruhe, Schalter oder niemand zu Hause); Alarmansagen kommen trotzdem“; V2 = 1 „Loxone legt still – das Plugin bestätigt es beim nächsten Abruf; bleibt es so, läuft der Sprachdienst nicht (Status ‚Zustand (Sprachsteuerung)‘)“; V1 = 1 „still – Ruhezeit im Plugin (Reiter Einstellungen); Alarmansagen kommen trotzdem“; V3 = -1 „bereit – letzte Ansage gesendet, ob sie ankam, ist unklar“; V3 = 0 und V4 != „“ und V4 != „-“ „bereit – letzte Ansage kam nicht an: <v4>; im Plugin Reiter Einstellungen die Ausgabe prüfen“; V3 = 1 „bereit – letzte Ansage ist angekommen“; ohne Bedingung „bereit (ob eine Ansage ankam, meldet das Plugin nur mit dauerhafter Broker-Verbindung, Reiter MQTT)“; Visualisierung EIN | V1 = #1, V2 = #17, V3 = #19, V4 = #20",
    "Status | Ansagen (Sprachsteuerung) | Rows: V2 = 1 and V1 = 1 “still – von Loxone stillgelegt (Nachtruhe, Schalter oder niemand zu Hause); Alarmansagen kommen trotzdem” (muted by Loxone; alarms still come); V2 = 1 “Loxone legt still – das Plugin bestätigt es beim nächsten Abruf; bleibt es so, läuft der Sprachdienst nicht (Status ‚Zustand (Sprachsteuerung)‘)” (Loxone mutes – the plugin confirms it with the next poll); V1 = 1 “still – Ruhezeit im Plugin (Reiter Einstellungen); Alarmansagen kommen trotzdem” (quiet hours in the plugin); V3 = -1 “bereit – letzte Ansage gesendet, ob sie ankam, ist unklar” (sent, outcome unclear); V3 = 0 and V4 != “” and V4 != “-” “bereit – letzte Ansage kam nicht an: <v4>; im Plugin Reiter Einstellungen die Ausgabe prüfen” (did not arrive); V3 = 1 “bereit – letzte Ansage ist angekommen” (arrived); without condition “bereit (ob eine Ansage ankam, meldet das Plugin nur mit dauerhafter Broker-Verbindung, Reiter MQTT)” (ready); visualisation ON | V1 = #1, V2 = #17, V3 = #19, V4 = #20"),
  SEITE1_SCHRITT1=("Im Plugin Reiter „Einstellungen“ den Dienst starten, im Reiter „Dienste“ Whisper und Piper starten, im Reiter „Mikrofone“ die Mikrofone eintragen. Probe: im Reiter „Test“ ist die Selbstprüfung grün.",
    "In the plugin tab “Settings” start the service, in the tab “Services” start Whisper and Piper, in the tab “Microphones” enter the microphones. Check: in the tab “Test” the self-check is green."),
  SEITE1_SCHRITT2=("In Schritt 2 dieses Reiters Knopf „Vorlage: Zustand (Eingang)“. In Loxone Config: Virtuelle Eingänge anwählen → Vordefinierte HTTP-Geräte → Vorlage importieren. Die Datei nur EINMAL einlesen (zweimal ergibt doppelte Eingänge). Die Adresse im Kopf prüfen: so muss der Miniserver den LoxBerry erreichen.",
    "In step 2 of this tab button “Template: status (input)”. In Loxone Config: select Virtual Inputs → Predefined HTTP devices → import template. Import the file only ONCE (twice gives duplicate inputs). Check the address in the header: this is how the Miniserver must reach the LoxBerry."),
  SEITE1_SCHRITT3=("Seite „Sprachsteuerung“ anlegen. Aus dem Behälter „Sprachsteuerung lokal“ die 11 Befehle ziehen (Nr. 1–11), dazu die Konstante „Konstante 1“ (Nr. 12, Wert 1; im Musterprojekt schon vorhanden).",
    "Create the page “Sprachsteuerung”. Drag the 11 commands from the container “Sprachsteuerung lokal” (no. 1–11), plus the constant “Konstante 1” (no. 12, value 1; already present in the sample project)."),
  SEITE1_SCHRITT4=("Zwei Benachrichtigungen anlegen (Peripherie → Mitteilungen → Benachrichtigung): „Meldung Plugin gestört (Sprachsteuerung)“ und „Meldung Mikrofon getrennt (Sprachsteuerung)“, Text aus der Tabelle, auf die Seite ziehen.",
    "Create two notifications (Periphery → Messages → Notification): “Meldung Plugin gestört (Sprachsteuerung)” and “Meldung Mikrofon getrennt (Sprachsteuerung)”, text from the table, drag them onto the page."),
  SEITE1_SCHRITT5=("Übrige Bausteine über die Baustein-Suche (F5) setzen, Parameter wie in der Tabelle, von oben nach unten verbinden; ODER haben je zwei Eingänge. Analogwertvalidierung Nr. 13: Haken bei ‚En‘ im Eigenschaftsfenster entfernen (Config legt En negiert an; sonst kommt die Konstante 1 als 0 an, und die Ausfallmeldung löst nie aus). Status Nr. 21: vorher viermal „+“ (V5–V8). Statuszeilen und Mitteilungstexte stehen in der Tabelle und werden von Hand eingetragen, die Zeile ohne Bedingung zuletzt.",
    "Place the other blocks with the block search (F5), parameters as in the table, connect from top to bottom; OR blocks have two inputs each. Value Validator no. 13: remove the tick at ‘En’ in the properties window (Config creates En inverted; otherwise the constant 1 arrives as 0 and the failure message never triggers). Status no. 21: click “+” four times first (V5–V8). The status rows and message texts are in the table and are entered by hand, the row without condition last."),
  SEITE1_SCHRITT6=("Speichern und in den Miniserver übertragen. Probe: „Zustand (Sprachsteuerung)“ zeigt „läuft – … Mikrofonen verbunden“, und SPRACHSTEUERUNG_ZAEHLER ändert sich bei jeder Abfrage. Gegenprobe: im Plugin den Dienst anhalten – nach 10 Minuten kommt „Meldung Plugin gestört (Sprachsteuerung)“.",
    "Save and send to the Miniserver. Check: “Zustand (Sprachsteuerung)” shows “läuft – … Mikrofonen verbunden” (running – … microphones connected), and SPRACHSTEUERUNG_ZAEHLER changes on every poll. Cross-check: stop the service in the plugin – after 10 minutes “Meldung Plugin gestört (Sprachsteuerung)” arrives."),
  SEITE1_H1=("<b>Zu Nr. 13:</b> steht der LoxBerry, behalten alle Eingänge ihren letzten Wert (OK bleibt 1, ALTER klein) – nur der stehende Zähler verrät es. Kommt innerhalb Tmc (180 s) kein neuer Wert, meldet die Analogwertvalidierung an ihrem Ausgang E. SPRACHSTEUERUNG_ZAEHLER an V, die Konstante 1 an En – und den Haken bei ‚En‘ im Eigenschaftsfenster entfernen.",
    "<b>On no. 13:</b> if the LoxBerry stops, all inputs keep their last value (OK stays 1, ALTER small) – only the stopped counter gives it away. If no new value arrives within Tmc (180 s), the value validator reports at its output E. SPRACHSTEUERUNG_ZAEHLER to V, the constant 1 to En – and remove the tick at ‘En’ in the properties window."),
  SEITE1_H2=("<b>Zu Nr. 14 bis 20:</b> „Dienst gestoppt“, „Sprachdienst fehlt“ und „Lebenszeichen fehlt“ laufen über zwei ODER in eine Benachrichtigung – ein Benachrichtigungsbaustein bekommt nur eine Quelle. Die Meldung kommt erst nach 10 Minuten Störung (ein Neustart oder ein Update bleibt still); „LoxBerry aus“ frühestens nach 13 Minuten (3 Minuten Lebenszeichen und 10 Minuten).",
    "<b>On no. 14 to 20:</b> “service stopped”, “voice service missing” and “sign of life missing” go through two OR blocks into one notification – a notification block gets only one source. The message only comes after 10 minutes of fault (a restart or an update stays quiet); “LoxBerry off” at the earliest after 13 minutes (3 minutes sign of life plus 10 minutes)."),
  SEITE1_H3=("<b>Zu Nr. 16 und 23:</b> ein Schwellwertschalter hinter einem abgefragten Eingang gibt bei jeder Abfrage einen kurzen Impuls; die Einschaltverzögerung dahinter (Nr. 19 bzw. 24) schluckt ihn.",
    "<b>On no. 16 and 23:</b> a threshold switch behind a polled input gives a short pulse on every poll; the switch-on delay behind it (no. 19 or 24) swallows it."),
  SEITE1_H4=("<b>Zu Nr. 10 und 11:</b> beide Werte gibt es seit 0.12.5. Wer die Vorlage früher importiert hat, ergänzt die zwei Befehle von Hand (Befehlserkennung aus der Tabelle in Schritt 2) oder importiert die Vorlage neu – dann aber alle Leitungen neu ziehen.",
    "<b>On no. 10 and 11:</b> both values exist since 0.12.5. If you imported the template earlier, add the two commands by hand (command recognition from the table in step 2) or import the template again – but then draw all connections anew."),
  SEITE1_H5=("Nach „Neues Token erzeugen“ (Schritt 5) die Adresse am Behälter „Sprachsteuerung lokal“ erneuern.",
    "After “Generate new token” (step 5) renew the address at the container “Sprachsteuerung lokal”."),
  SEITE1_H6=("Wer nur über MQTT arbeitet: dasselbe Lebenszeichen liefert der Herzschlag (Thema <span class='sm-mono'>ts</span> unter dem Präfix aus dem Reiter MQTT, alle 60 s); die Tabelle nimmt den HTTP-Weg.",
    "If you work only via MQTT: the heartbeat delivers the same sign of life (topic <span class='sm-mono'>ts</span> under the prefix from the MQTT tab, every 60 s); the table uses the HTTP path."),
  SEITE2_SCHRITT1=("Im Plugin Reiter „MQTT“ prüfen: das Gateway steht auf Autostart, das Abo für die Themen dieses Plugins steht (bei Gateway V2: die Datenpunkte anhaken). Im Reiter „Sätze“ haben die Ziele ein Thema (Werksziel „Licht im Wohnzimmer“ = wohnzimmer/licht).",
    "In the plugin tab “MQTT” check: the gateway is set to autostart, the subscription for the topics of this plugin is in place (with gateway V2: tick the data points). In the tab “Sentences” the targets have a topic (factory target “Licht im Wohnzimmer” = wohnzimmer/licht)."),
  SEITE2_SCHRITT2=("In Loxone Config die Eingänge der Tabelle VON HAND anlegen (Virtuelle Eingänge anwählen → Virtueller Texteingang bzw. Virtueller Eingang), Name GENAU wie in der Tabelle – so heißen sie beim Gateway: Präfix und Thema mit „_“ statt „/“. Texte (Nr. 1, 9–13) als „Virtueller Texteingang“, Zahlen (Nr. 2, 7, 8) als „Virtueller Eingang“, Anzeigenamen wie in der Tabelle. Ein verschönerter Name ergibt beim ersten Satz einen zweiten Eingang, und der Baustein der Tabelle bleibt leer.",
    "In Loxone Config create the inputs of the table BY HAND (select Virtual Inputs → Virtual Text Input or Virtual Input), name EXACTLY as in the table – this is what the gateway calls them: prefix and topic with “_” instead of “/”. Texts (no. 1, 9–13) as “Virtual Text Input”, numbers (no. 2, 7, 8) as “Virtual Input”, display names as in the table. A prettified name creates a second input with the first sentence, and the block of the table stays empty."),
  SEITE2_SCHRITT3=("Seite „Sprachsteuerung Befehle“ anlegen, die Eingänge ziehen, Status und Flankenerkennungen über die Baustein-Suche (F5) setzen. An den beiden Flankenerkennungen Nr. 5 und 6 Pd auf 0,1 s stellen (Config legt 1 s an). Status „Letzter Sprachbefehl (Sprachsteuerung)“ Nr. 14: vorher zweimal „+“ (V5, V6).",
    "Create the page “Sprachsteuerung Befehle”, drag the inputs, place the status blocks and edge detections with the block search (F5). At the two edge detections no. 5 and 6 set Pd to 0.1 s (Config creates 1 s). Status “Letzter Sprachbefehl (Sprachsteuerung)” no. 14: click “+” twice first (V5, V6)."),
  SEITE2_SCHRITT4=("Die Ausgänge On von Nr. 5 und 6 an den eigenen Licht- oder Schaltbaustein legen (Ein bzw. Aus), Nr. 2 an den eigenen Dimmer, Nr. 7 an den eigenen Sollwert.",
    "Connect the outputs On of no. 5 and 6 to your own lighting or switching block (on and off), no. 2 to your own dimmer, no. 7 to your own setpoint."),
  SEITE2_SCHRITT5=("Speichern und übertragen. Probe: „schalte das licht im wohnzimmer an“ sagen (oder im Plugin Reiter „Test“ eintippen) – „Letzter Sprachbefehl (Sprachsteuerung)“ zeigt „ausgeführt …“, und die Flankenerkennung Nr. 5 gibt einen kurzen Impuls.",
    "Save and send. Check: say “schalte das licht im wohnzimmer an” (or type it in the plugin tab “Test”) – “Letzter Sprachbefehl (Sprachsteuerung)” shows “ausgeführt …” (executed), and the edge detection no. 5 gives a short pulse."),
  SEITE2_H1=("<b>Zu Nr. 1 bis 13:</b> Name genau wie das Gateway ihn vergibt (Präfix aus dem Reiter MQTT); ein verschönerter Name ergibt einen zweiten Eingang. Die Namen aller eingetragenen Ziele stehen oben in diesem Schritt.",
    "<b>On no. 1 to 13:</b> name exactly as the gateway assigns it (prefix from the MQTT tab); a prettified name creates a second input. The names of all configured targets are listed above in this step."),
  SEITE2_H2=("<b>Zu Nr. 1:</b> seit 0.12.5 setzt das Plugin den Befehl 2 Sekunden nach jedem Satz auf „-“ zurück. So wirkt derselbe Befehl auch zweimal hintereinander („Licht an“, dazwischen von Hand aus) – das Gateway schickt nur Änderungen, und Loxone sähe denselben Text sonst nicht als neu.",
    "<b>On no. 1:</b> since 0.12.5 the plugin resets the command to “-” 2 seconds after each sentence. So the same command also works twice in a row (“light on”, switched off by hand in between) – the gateway only sends changes, and Loxone would otherwise not see the same text as new."),
  SEITE2_H3=("<b>Zu Nr. 3 und 4:</b> den Text vergleicht der Status (== „ein“); sein Statuswert kommt am Ausgang AQ heraus.",
    "<b>On no. 3 and 4:</b> the status block compares the text (== “ein”); its status value comes out at output AQ."),
  SEITE2_H4=("<b>Zu Nr. 6:</b> an „Off“ einer Lichtsteuerung nur Impulse unter 200 ms – ein längerer sperrt den Baustein, deshalb Pd 0,1 s.",
    "<b>On no. 6:</b> at “Off” of a lighting controller only pulses shorter than 200 ms – a longer one locks the block, hence Pd 0.1 s."),
  SEITE2_H5=("<b>Zu Nr. 2 und 7:</b> dieselbe Zahl zweimal („dimme auf 40“) ändert den Eingang nicht – der Dimmer bekommt nichts Neues.",
    "<b>On no. 2 and 7:</b> the same number twice (“dimme auf 40”) does not change the input – the dimmer gets nothing new."),
  SEITE2_H6=("Je weiteres Ziel dieselben Zeilen mit seinem Thema (Werksziele: kueche/licht, alle/licht, wohnzimmer/heizung). Nach einem Neustart von Gateway oder Miniserver stehen die Befehlseingänge leer; das ist gewollt – es schaltet nichts nach.",
    "For every further target the same rows with its topic (factory targets: kueche/licht, alle/licht, wohnzimmer/heizung). After a restart of the gateway or the Miniserver the command inputs are empty; that is intended – nothing is switched again."),
  SEITE2_H7=("Wer das Gateway auf UDP umstellt, kann statt der Texteingänge die Vorlage „je Ziel ein Eingang“ nehmen – im Haus ungeprüft.",
    "If you switch the gateway to UDP, you can use the template “one input per target” instead of the text inputs – not tested in the house."),
  SEITE3_SCHRITT1=("Im Plugin Reiter „Einstellungen“ die Ausgabe wählen (ab Werk „aus“: es sprechen nur die Lautsprecher der Sprachgeräte; sonst z. B. Music Server, Chromecast, Alexa-NG, Sonos oder Audioserver über das gemeinsame Sprachmodul). Die Ruhezeit im Plugin ausgeschaltet lassen, wenn Loxone stilllegt (Nr. 18).",
    "In the plugin tab “Settings” choose the output (factory setting “off”: only the loudspeakers of the voice devices speak; otherwise e.g. Music Server, Chromecast, Alexa-NG, Sonos or Audioserver via the shared voice module). Leave the quiet hours in the plugin switched off if Loxone mutes (no. 18)."),
  SEITE3_SCHRITT2=("In Schritt 4 dieses Reiters Knopf „Vorlage: Befehle (Ausgang)“. In Loxone Config: Virtuelle Ausgänge anwählen → Vordefinierte Geräte → Vorlage importieren (nur einmal). Der Behälter „Sprachsteuerung lokal - Befehle“ trägt fünf Befehle; die Datei enthält das Token – nicht weitergeben.",
    "In step 4 of this tab button “Template: commands (output)”. In Loxone Config: select Virtual Outputs → Predefined devices → import template (only once). The container “Sprachsteuerung lokal - Befehle” carries five commands; the file contains the token – do not pass it on."),
  SEITE3_SCHRITT3=("Seite „Sprachsteuerung Ansagen“ anlegen. Die fünf Befehle, SPRACHSTEUERUNG_RUHE (weitere Instanz), „Türklingel (eigene Quelle)“ und „Niemand zu Hause (eigene Quelle)“ ziehen (im Musterprojekt schon vorhanden); die Platzhalter „Garagentor offen (eigene Quelle)“ und „Wassermelder (eigene Quelle)“, die zwei Tasten und den Schalter „Ansagen stilllegen (Sprachsteuerung)“ anlegen; die Eingänge Nr. 19, 20 und 21 von Hand anlegen, Name genau so.",
    "Create the page “Sprachsteuerung Ansagen”. Drag the five commands, SPRACHSTEUERUNG_RUHE (further instance), “Türklingel (eigene Quelle)” and “Niemand zu Hause (eigene Quelle)” (already present in the sample project); create the placeholders “Garagentor offen (eigene Quelle)” and “Wassermelder (eigene Quelle)”, the two buttons and the switch “Ansagen stilllegen (Sprachsteuerung)”; create the inputs no. 19, 20 and 21 by hand, name exactly like this."),
  SEITE3_SCHRITT4=("Übrige Bausteine über die Baustein-Suche (F5) setzen und verbinden. An der Schaltuhr Nr. 13 täglich 22:00–07:00 EIN eintragen, in allen Betriebsarten.",
    "Place the other blocks with the block search (F5) and connect them. At the schedule no. 13 enter ON daily 22:00–07:00, in all operating modes."),
  SEITE3_SCHRITT5=("Speichern und übertragen. Probe: „Taste Testansage (Sprachsteuerung)“ drücken – die Anlage sagt „Das Garagentor steht seit einer Stunde offen“. Schalter „Ansagen stilllegen (Sprachsteuerung)“ ein, Taste noch einmal: es bleibt still, und „Ansagen (Sprachsteuerung)“ zeigt „still – von Loxone stillgelegt“.",
    "Save and send. Check: press “Taste Testansage (Sprachsteuerung)” – the system says “Das Garagentor steht seit einer Stunde offen”. Switch “Ansagen stilllegen (Sprachsteuerung)” on, press the button again: it stays silent, and “Ansagen (Sprachsteuerung)” shows “still – von Loxone stillgelegt” (muted by Loxone)."),
  SEITE3_H1=("Den Text einer Ansage ändert man im Befehl hinter <span class='sm-mono'>text=</span> (Leerzeichen als <span class='sm-mono'>%20</span>, Umlaute wie in der Vorlage); höchstens 400 Zeichen. Nur in einer Zone oder an einem Lautsprecher: <span class='sm-mono'>&amp;zone=4</span> bzw. <span class='sm-mono'>&amp;mikrofon=…</span> anhängen (Tabelle in diesem Schritt).",
    "To change the text of an announcement, edit the command after <span class='sm-mono'>text=</span> (spaces as <span class='sm-mono'>%20</span>, umlauts as in the template); at most 400 characters. Only in one zone or on one loudspeaker: append <span class='sm-mono'>&amp;zone=4</span> or <span class='sm-mono'>&amp;mikrofon=…</span> (table in this step)."),
  SEITE3_H2=("Eine Ansage geht nur, wenn der Sprachdienst läuft – sonst verfällt sie (sie wird nicht nachgeholt). Zwei Ansagen binnen 10 Sekunden: die zweite schluckt das Plugin (Wiederholungsbremse, Reiter Einstellungen).",
    "An announcement only goes out while the voice service is running – otherwise it lapses (it is not repeated later). Two announcements within 10 seconds: the plugin swallows the second one (repeat brake, Settings tab)."),
  SEITE3_H3=("<b>Zu Nr. 10:</b> „dringend“ übergeht jede Ruhe – auch nachts und stillgelegt; nur für echte Alarme benutzen.",
    "<b>On no. 10:</b> “dringend” (urgent) overrides every quiet – also at night and when muted; use it only for real alarms."),
  SEITE3_H4=("<b>Zu Nr. 13 bis 18:</b> Loxone legt über den Befehl „Sprachsteuerung Ruhe“ still – das gilt auch für Ansagen, die andere Plugins über die Sprachsteuerung sprechen lassen. Die Stilllegung aus Loxone übersteht ein Plugin-Update (seit 0.12.6).",
    "<b>On no. 13 to 18:</b> Loxone mutes via the command “Sprachsteuerung Ruhe” – this also applies to announcements that other plugins have the voice control speak. The muting from Loxone survives a plugin update (since 0.12.6)."),
  SEITE3_H5=("<b>Zu Nr. 19 und 20:</b> ohne „Dauerhafte Verbindung zum Broker“ (Reiter MQTT) steht Nr. 19 auf 0 – keine Meldung daran hängen.",
    "<b>On no. 19 and 20:</b> without “Permanent connection to the broker” (MQTT tab) no. 19 stays at 0 – do not hang a message on it."),
  SEITE3_H6=("<b>Zu Nr. 2:</b> im eigenen Haus nur einen Weg für die Klingel wählen – entweder die Klingel-Meldungen im Intercom-Plugin oder diese Bausteine.",
    "<b>On no. 2:</b> choose only one path for the doorbell in your own house – either the bell messages in the Intercom plugin or these blocks."),
  SEITE3_H7=("Wie und wo gesprochen wird, stellt man im Plugin ein (gemeinsames Sprachmodul); Loxone löst nur aus. Nur bei „Original Loxone Audioserver“ liefert das Plugin den Text für den TTS-Eingang (Nr. 21).",
    "How and where announcements are spoken is set in the plugin (shared voice module); Loxone only triggers. Only with “Original Loxone Audioserver” does the plugin deliver the text for the TTS input (no. 21)."),
  )

s("TEST",
  EINLEITUNG=("Diese Prüfung beantwortet ohne Loxone und ohne Mikrofon, ob die Einrichtung "
              "trägt. Jedes Kreuz nennt die Abhilfe mit.",
              "This check answers - without Loxone and without a microphone - whether the setup "
              "holds. Every cross names the remedy."),
  ERST_OEFFNEN=("Diese Prüfung fragt vier Ports ab und ruft den eigenen Endpunkt auf. Sie läuft "
                "deshalb erst, wenn der Reiter wirklich geöffnet wird - sonst würde sie bei "
                "jedem Seitenaufbau mitlaufen.",
                "This check queries four ports and calls our own endpoint. It therefore only "
                "runs when the tab is actually opened - otherwise it would run on every page "
                "load."),
  K_JETZT_PRUEFEN=("Jetzt prüfen", "Check now"),
  F_ENDPUNKT=("Antwortet der eigene Endpunkt - und weist er ein falsches Token ab?",
              "Does our own endpoint answer - and does it reject a wrong token?"),
  A_ENDPUNKT_OK=("ja, und ein falsches Token wird mit 403 abgewiesen",
                 "yes, and a wrong token is rejected with 403"),
  A_ENDPUNKT_FEHL=("HTTP %d, Anfang der Antwort: %s", "HTTP %d, start of the answer: %s"),
  A_ENDPUNKT_OFFEN=("Der Endpunkt antwortet, aber ein FALSCHES Token bekommt HTTP %d statt 403. "
                    "Ein Endpunkt, der jedem antwortet, ist schlimmer als einer, der schweigt.",
                    "The endpoint answers, but a WRONG token gets HTTP %d instead of 403. An "
                    "endpoint that answers everyone is worse than one that stays silent."),
  A_ENDPUNKT_STUMM=("keine Antwort - das kann daran liegen, dass der Webserver nur eine Anfrage "
                    "zugleich bearbeitet und sich deshalb nicht selbst aufrufen kann. Die "
                    "Adresse einmal von Hand im Browser prüfen.",
                    "no answer - this can be because the web server handles only one request at "
                    "a time and therefore cannot call itself. Check the address manually in a "
                    "browser."),
  F_DIENST=("Läuft der Sprachdienst?", "Is the voice service running?"),
  F_VENV=("Ist die virtuelle Python-Umgebung da?", "Is the Python virtual environment present?"),
  A_VENV_FEHLT=("Nein - erwartet unter %s. Das Plugin neu installieren.",
                "No - expected at %s. Reinstall the plugin."),
  F_LLM=("Antwortet das Sprachmodell?", "Is the language model responding?"),
  F_CT_EINGERICHTET=("Sprachdienste eingerichtet?", "Voice services set up?"),
  F_MIKROFONE=("Sind Mikrofone eingetragen?", "Are microphones configured?"),
  # Diese vier standen bis 13.09.2026 nur in den .ini-Dateien der
  # veroeffentlichten 0.11.4 und nicht hier; der Erzeuger haette sie beim
  # naechsten Lauf weggeworfen. Seine Wache hat das gemeldet, statt es zu tun.
  F_MQTT=("Steht das MQTT-Gateway von LoxBerry bereit?",
          "Is the LoxBerry MQTT gateway ready?"),
  F_MQTT_EIN=("Ist die MQTT-Veröffentlichung dieses Plugins eingeschaltet?",
              "Is this plugin's MQTT publishing switched on?"),
  F_PIPER=("Antwortet die Sprachausgabe?", "Is speech synthesis responding?"),
  F_SAETZE=("Sind Satzmuster und Ziele da?", "Are patterns and targets present?"),
  F_WAKE=("Antwortet der Wortwecker?", "Is the wake word service responding?"),
  F_WHISPER=("Antwortet die Spracherkennung?", "Is speech recognition responding?"),
  F_RUHE=("Ruhezeit", "Quiet hours"),
  F_VORGABEN=("Ist die Konfiguration vollständig?", "Is the configuration complete?"),
  F_ZWEITSCHRIFT=("Gibt es eine Zweitschrift?", "Is there a backup copy?"),
  F_MUSTER=("Ist jedes Suchmuster der Statuszeile eindeutig?",
            "Is every search pattern of the status line unambiguous?"),
  F_VORLAGE=("Ist die erzeugte Loxone-Vorlage wohlgeformt?",
             "Is the generated Loxone template well-formed?"),
  F_SMACTIVE=("Setzt der Server den aktiven Reiter selbst?",
              "Does the server set the active tab itself?"),
  F_FORMULAR=("Trägt jedes Formular das Merkmal gegen fremde Absender?",
              "Does every form carry the marker against foreign senders?"),
  A_DIENST_GESTOPPT=("Nein - im Reiter Einstellungen starten.",
                     "No - start it on the Settings tab."),
  A_DIENST_LAEUFT=("Ja, PID", "Yes, PID"),
  A_DIENST_SOLL_TOT=("Nein, obwohl er laufen soll. Die Logdatei sagt, woran es scheitert.",
                     "No, although it should be running. The log file says why."),
  A_DIENST_STUMM=("%s antwortet nicht (%s). Reiter Dienste, Container starten.",
                  "%s is not responding (%s). Services tab, start the container."),
  A_ESPHOME_UNGEPRUEFT=("der Port ist offen; ob der Audioweg trägt, ist damit NICHT gesagt",
                        "the port is open; whether the audio path works is NOT implied"),
  A_KEINE_MIKROFONE=("Keines. Sätze lassen sich hier trotzdem durchschicken.",
                     "None. Sentences can still be sent through here."),
  A_KEINE_MODELLE=("antwortet, nennt aber kein Modell",
                   "responds, but names no model"),
  A_KEINE_SAETZE=("Nein - ohne Regeln oder ohne Ziele wird nichts erkannt.",
                  "No - without rules or targets nothing is recognised."),
  A_LLM_AUS=("Abgeschaltet - es gelten nur die Satzmuster.",
             "Disabled - only the patterns apply."),
  A_MIKRO_STUMM=("%s antwortet nicht (%s).", "%s is not responding (%s)."),
  A_MQTT_AUS=("Nicht auf Autostart - unter System, MQTT Gateway einschalten.",
              "Autostart is off - enable it under System, MQTT Gateway."),
  A_MQTT_EIN_JA=("Ja. Der Dienst schickt seine Themen an den UDP-Eingang des Gateways.",
                 "Yes. The service sends its topics to the gateway's UDP input."),
  A_MQTT_EIN_NEIN=("Nein — es geht nichts an den Broker und damit nichts an Loxone. Reiter MQTT.",
                   "No — nothing reaches the broker and therefore nothing reaches Loxone. "
                   "Tab MQTT."),
  A_MQTT_FASSUNG=("Fassung %s", "version %s"),
  A_MQTT_UNBEKANNT=("unbekannt", "unknown"),
  A_MQTT_NICHT_GEFUNDEN=("Kein MQTT-Abschnitt in der general.json gefunden.",
                         "No MQTT section found in general.json."),
  A_RAUM_UNBEKANNT=("der eingetragene Raum %s steht nicht in der Zielliste, 'mach an' geht dort "
                    "ins Leere",
                    "the configured room %s is not in the target list, 'switch on' goes nowhere "
                    "there"),
  A_RUHE_AUS=("Keine eingestellt - eine Ansage kann zu jeder Tages- und Nachtzeit kommen.",
              "None configured - an announcement can come at any time of day or night."),
  A_RUHE_EIN=("%s bis %s, gerade nicht aktiv", "%s to %s, not currently active"),
  A_RUHE_LOXONE=("von Loxone stillgelegt - es wird nichts angesagt, unabhängig von der Uhrzeit",
                 "muted by Loxone - nothing is announced, regardless of the time"),
  A_RUHE_AKTIV=("%s bis %s - AKTIV, es wird nichts angesagt",
                "%s to %s - ACTIVE, nothing is announced"),
  A_SAETZE=("%d Regeln, %d Ziele", "%d rules, %d targets"),
  A_VORGABEN_FEHLT=("templates/vorgaben.json wurde nicht gefunden - ohne sie kennt weder die "
                    "Oberfläche noch der Dienst die Vorgabewerte.",
                    "templates/vorgaben.json was not found - without it neither the interface "
                    "nor the service knows the default values."),
  A_VORGABEN_LUECKE=("nein, %d von %d Schlüsseln - es fehlen: %s (gelesen wird die Vorgabe; "
                     "einmal Speichern ergänzt sie)",
                     "no, %d of %d keys - missing: %s (the default is used; saving once "
                     "completes them)"),
  A_VORGABEN_OK=("ja, %d von %d Schlüsseln", "yes, %d of %d keys"),
  A_ZWEIT_FEHLT=("nein, nur %d von 2 - ein Update oder eine Neuinstallation kann Einstellungen "
                 "kosten",
                 "no, only %d of 2 - an update or reinstall may cost settings"),
  A_MUSTER_DOPPELT=("nein - diese Namen kommen in der Statuszeile nicht genau einmal vor: %s",
                    "no - these names do not appear exactly once in the status line: %s"),
  A_MUSTER_OK=("ja, alle %d Namen genau einmal", "yes, all %d names exactly once"),
  A_VORLAGE_OK=("ja, %d von %d Vorlagen sind wohlgeformt und tragen CRLF - eine leere Vorlage (etwa ohne Ziele) wird nicht gezählt",
                "yes, %d of %d templates are well-formed and use CRLF - an empty template (for example without targets) is not counted"),
  A_SMACTIVE_OK=("ja, an Leiste und Bereichen (%d Reiter)", "yes, on bar and panes (%d tabs)"),
  A_SMACTIVE_FEHL=("Nein - Leiste %d (mindestens 1 nötig), Bereiche %d von %d. Ohne JavaScript wäre die Seite leer.",
                   "No - bar %d (at least 1 required), panes %d of %d. Without JavaScript the page would be empty."),
  A_SMACTIVE_NICHTS=("die Oberflächendatei ließ sich nicht lesen - die Prüfung greift ins Leere",
                     "the interface file could not be read - the check has nothing to look at"),
  A_FORM_KEINS=("kein Formular gefunden - die Prüfung greift ins Leere",
                "no form found - the check has nothing to look at"),
  A_FORM_OHNE=("nein - %d von %d ohne Merkmal", "no - %d of %d without the marker"),
  A_FORM_HUELLE=("die Hülle $sp_hidden gibt kein name='fmt' mehr aus - dann trägt kein einziges Formular das Merkmal",
                 "the $sp_hidden helper no longer emits name='fmt' - then no form carries the marker at all"),
  A_FORM_OK=("ja, alle %d Formulare", "yes, all %d forms"),
  H_LESEN=("Ansehen", "Read"),
  H_NICHT_VERSTANDEN=("Was regelmäßig nicht verstanden wird",
                      "What regularly goes unrecognised"),
  NICHT_VERSTANDEN_ERKLAERUNG=("Aus dem Verlauf gezählt. Steht dort mehrfach dieselbe "
                               "Bezeichnung, fehlt in aller Regel nur ein Alias - der Knopf "
                               "trägt ihn beim gewählten Ziel nach.",
                               "Counted from the history. If the same wording appears several "
                               "times, usually only an alias is missing - the button adds it to "
                               "the selected target."),
  H_RAUM=("Wie der Raum am Mikrofon. Bleibt das Feld leer, muss der Satz das Ziel selbst nennen.",
          "Like the room on the microphone. If empty, the sentence must name the target itself."),
  H_SATZ=("Genau so, wie es die Spracherkennung liefern würde - ohne Weckwort.",
          "Exactly as speech recognition would deliver it - without the wake word."),
  H_SCHALTEN=("Ausprobieren", "Try it out"),
  H_SELBSTPRUEFUNG=("Selbstprüfung", "Self-check"),
  H_TECHNIK=("Technische Auskunft", "Technical information"),
  H_TROCKEN=("Trockenlauf - deuten, ohne zu schalten",
             "Dry run - interpret without switching"),
  TROCKEN_ERKLAERUNG=("Der Trockenlauf schickt den Satz durch dieselbe Kette wie der Dienst und "
                      "sendet NICHTS: kein MQTT, kein Miniserver-Aufruf, keine Ansage. Er "
                      "zeigt, welche Regel greifen würde, welches Ziel getroffen wäre und "
                      "welche MQTT-Themen geschrieben würden. Er braucht dafür keinen laufenden "
                      "Dienst - gerade dann will man es wissen.",
                      "The dry run sends the sentence through the same chain as the service and "
                      "publishes NOTHING: no MQTT, no Miniserver call, no announcement. It "
                      "shows which rule would match, which target would be hit and which MQTT "
                      "topics would be written. It needs no running service - which is exactly "
                      "when you want to know."),
  H_UNGEPRUEFT=("Was hier nicht geprüft werden kann", "What cannot be checked here"),
  H_VERLAUF=("Was zuletzt verstanden wurde", "What was understood recently"),
  KEIN_VERLAUF=("Noch nichts gehört.", "Nothing heard yet."),
  K_ALIAS=("übernehmen", "adopt"),
  K_CSV=("Verlauf als CSV holen", "Download history as CSV"),
  K_DIAG=("Diagnose abrufen", "Fetch diagnostics"),
  K_DIENSTE=("Dienste befragen", "Query services"),
  K_NEU_LADEN=("Satzdatei neu lesen", "Reload sentence file"),
  K_ROH=("Rohdaten als JSON ansehen", "View raw data as JSON"),
  K_SATZ=("Satz wirklich verarbeiten", "Really process the sentence"),
  K_SELBSTTEST=("Selbsttest des Dienstes ausführen", "Run the service self-test"),
  K_SPRECHEN=("Aussprechen lassen", "Have it spoken"),
  K_STATUS=("Zustand abrufen", "Fetch status"),
  K_TROCKEN=("Nur deuten, nicht schalten", "Interpret only, do not switch"),
  K_VERLAUF=("Verlauf abrufen", "Fetch history"),
  L_ANSAGE=("Text zum Aussprechen", "Text to be spoken"),
  L_RAUM=("Raum (wie am Mikrofon)", "Room (as on the microphone)"),
  L_SATZ=("Satz, als hätte ihn jemand gesprochen", "Sentence, as if someone had spoken it"),
  L_ZONE=("Zone für die Ansage (leer = eingestellte Zonen)",
          "Zone for the announcement (empty = configured zones)"),
  M_ALIAS_FEHL=("Der Alias ließ sich nicht übernehmen - gibt es das Ziel noch?",
                "The alias could not be adopted - does the target still exist?"),
  M_ALIAS_OK=("'%s' wurde als weitere Bezeichnung für '%s' eingetragen.",
              "'%s' was added as another name for '%s'."),
  M_ANSAGE_LEER=("Es wurde kein Text eingegeben.", "No text was entered."),
  M_SATZ_LEER=("Es wurde kein Satz eingegeben.", "No sentence was entered."),
  M_TROCKEN=("Trockenlauf: %s — Antwort wäre: '%s'. Es wären %d MQTT-Themen geschrieben "
             "worden, gesendet wurde nichts.",
             "Dry run: %s — the answer would be: '%s'. %d MQTT topics would have been "
             "written, nothing was sent."),
  M_UNBEKANNT=("Unbekannte Aktion.", "Unknown action."),
  SCHALTEN_WARNUNG=("<b>Diese Knöpfe wirken sofort.</b> Ein Satz geht durch dieselbe Kette wie "
                    "ein gesprochener - das Licht geht wirklich an. Wer nur sehen will, welche "
                    "Regel greift, nimmt den Trockenlauf darüber.",
                    "<b>These buttons take effect at once.</b> A sentence goes through the same "
                    "chain as a spoken one - the light really comes on. To only see which rule "
                    "matches, use the dry run above."),
  T_ABSICHT=("Gedeutet als", "Interpreted as"),
  T_ANTWORT=("Antwort", "Answer"),
  T_ANZAHL=("Anzahl", "Count"),
  T_BEFUND=("Befund", "Finding"),
  T_FRAGE=("Frage", "Question"),
  T_GRUND=("Grund", "Reason"),
  T_MIKROFON=("Mikrofon", "Microphone"),
  T_QUELLE=("Quelle", "Source"),
  T_SATZ=("Satz", "Sentence"),
  T_UEBERNEHMEN=("Als Alias übernehmen bei", "Adopt as alias for"),
  T_VERSTANDEN=("Gehört", "Heard"),
  T_ZEIT=("Zeit", "Time"),
  UNGEPRUEFT=("Ob ein Mikrofon Audio liefert, das Whisper versteht; ob das Weckwort in Ihrem "
              "Raum zuverlässig anspricht; ob ESPHome-Mikrofone den Audioweg tragen - das lässt "
              "sich nur mit echter Hardware feststellen. Das Plugin wurde ohne gebaut; geprüft "
              "wurde die ganze Kette gegen Attrappen, die das Originalpaket des "
              "Wyoming-Protokolls benutzen. Was danach kommt - Raumakustik, Nachhall, "
              "Nebengeräusche - entscheidet sich erst bei Ihnen. Ebenfalls ungemessen: ob das MQTT-Gateway die Werte behält (retain), und ob ein anderer Teilnehmer am Broker mithören kann. Und: fünf Netzabrufe des Dienstes sind synchron; ein einzelner Satz kann die Verarbeitung rechnerisch bis zu rund 161 Sekunden anhalten, in denen kein anderes Mikrofon bedient wird - am Gerät nachzumessen an der Lücke zwischen zwei Herzschlägen.",
              "Whether a microphone delivers audio Whisper understands; whether the wake word "
              "reliably triggers in your room; whether ESPHome microphones carry the audio path "
              "- only real hardware can establish that. The plugin was built without any; the "
              "whole chain was tested against stubs using the original Wyoming protocol "
              "package. What comes after - room acoustics, reverberation, background noise - is "
              "decided at your place. Also unmeasured: whether the MQTT gateway retains the values, and whether another client on the broker can listen in. And: five of the service's network calls are synchronous; a single sentence can stall processing for up to roughly 161 seconds, during which no other microphone is served - to be measured on the device from the gap between two heartbeats."),
  VERLAUF_ERKLAERUNG=("Der wichtigste Anhaltspunkt bei 'sie versteht mich nicht'. Hier steht, "
                      "was die Spracherkennung GEHÖRT hat - oft ist der Fehler dort und nicht "
                      "im Satzmuster.",
                      "The most important clue when 'it does not understand me'. This shows what "
                      "speech recognition HEARD - often the fault is there and not in the "
                      "pattern."),
  )

s("LOG",
  ERKLAERUNG=("Protokolliert werden Start und Ende, Störungen und jeder verstandene Satz mit "
              "seinem Ergebnis.",
              "Logged are start and stop, faults, and every understood sentence with its result."),
  GELEERT=("Logdatei geleert (Bedienoberfläche).", "Log file cleared (from the interface)."),
  H_TITEL=("Logdateien", "Log files"),
  H_MITSCHNITT=("Mitschnitt", "Trace"),
  MITSCHNITT_ERKLAERUNG=("Bei diesem Plugin laufen fünf Gegenstellen: Mikrofon, "
                         "Spracherkennung, Sprachausgabe, Sprachmodell und der MQTT-Gateway. "
                         "Geht ein Satz unterwegs verloren, zeigt das Protokoll nur das "
                         "Ergebnis, nicht den Weg. Der Mitschnitt zeigt den Weg - <b>als "
                         "Frist, nicht als Schalter</b>: er hört von selbst wieder auf. Ein "
                         "vergessener Mitschnitt schriebe sonst die Ramdisk voll, auf der diese "
                         "Protokolle liegen.",
                         "This plugin talks to five counterparts: microphone, speech "
                         "recognition, speech synthesis, language model and the MQTT gateway. "
                         "If a sentence is lost on the way, the log only shows the result, not "
                         "the path. The trace shows the path - <b>as a deadline, not a "
                         "switch</b>: it stops by itself. A forgotten trace would otherwise "
                         "fill the RAM disk these logs live on."),
  MITSCHNITT_AN=("Der Mitschnitt läuft für %d Sekunden und schaltet sich dann selbst ab.",
                 "The trace runs for %d seconds and then switches itself off."),
  MITSCHNITT_AUS=("Der Mitschnitt wurde abgeschaltet.", "The trace was switched off."),
  MITSCHNITT_LAEUFT=("Der Mitschnitt läuft noch %d Sekunden.",
                     "The trace is still running for %d seconds."),
  K_MITSCHNITT_5=("Mitschnitt 5 Minuten", "Trace for 5 minutes"),
  K_MITSCHNITT_15=("Mitschnitt 15 Minuten", "Trace for 15 minutes"),
  K_MITSCHNITT_AUS=("Mitschnitt abschalten", "Switch trace off"),
  K_LEEREN=("Logdatei leeren", "Clear log file"),
  LEER=("Es gibt noch keine Log-Einträge.", "There are no log entries yet."),
  )


# Verbesserungsbau Welle 3 (01.10.2026): Ansage-1 (zusaetzliche Ansage ueber
# Chromecast4lox / Alexa-NG), Nr. 19 (leeres Feld), PRG/X-2 und X-3.
# Quelle: Pruefung-Durchgang-2026-09-29/vb_sp_bau_skripte/texte_daten.py.
s("EINST",
  TTS_AUS=("aus (ab Werk) - nur die Lautsprecher der Sprachgeräte",
    "off (default) - only the speakers of the voice devices"),
  TTS_CHROMECAST=("Chromecast4lox (über MQTT)",
    "Chromecast4lox (via MQTT)"),
  TTS_ALEXANG=("Alexa-NG (eigenes Plugin)",
    "Alexa-NG (own plugin)"),
  H_ZUSATZ=("Chromecast4lox und Alexa-NG",
    "Chromecast4lox and Alexa-NG"),
  H_ZUSATZ_TEXT=("Nur für die Art der Audioausgabe <b>Chromecast4lox</b> bzw. <b>Alexa-NG</b>. Das jeweilige Plugin muss auf diesem LoxBerry laufen. Nimmt es die Ansage nicht an (Plugin fehlt, Lautsprecher unbekannt, keine Rückmeldung binnen 10 s), sprechen wie bisher die Lautsprecher der Sprachgeräte - auch beim Antwortweg <i>nur Loxone</i>. Der Reiter Test sagt, was gilt.",
    "Only for the audio output types <b>Chromecast4lox</b> and <b>Alexa-NG</b>. The respective plugin must run on this LoxBerry. If it does not accept the announcement (plugin missing, speaker unknown, no feedback within 10 s), the speakers of the voice devices speak as before - also with the answer path <i>Loxone only</i>. The Test tab says what applies."),
  L_CC_PRAEFIX=("Chromecast4lox: Themenpräfix",
    "Chromecast4lox: topic prefix"),
  H_CC_PRAEFIX=("Die Einstellung <i>MQTT-Thema</i> in Chromecast4lox, ab Werk <span class='sm-mono'>chromecast4lox</span>. Die Ansage geht an <span class='sm-mono'>&lt;präfix&gt;/&lt;lautsprecher&gt;/cmd/tts</span> (QoS 1, nicht zurückbehalten). Ob Chromecast4lox da ist, sagt <span class='sm-mono'>&lt;präfix&gt;/server/online</span>.",
    "The setting <i>MQTT topic</i> in Chromecast4lox, default <span class='sm-mono'>chromecast4lox</span>. The announcement goes to <span class='sm-mono'>&lt;prefix&gt;/&lt;speaker&gt;/cmd/tts</span> (QoS 1, not retained). Whether Chromecast4lox is there is told by <span class='sm-mono'>&lt;prefix&gt;/server/online</span>."),
  L_CC_ZIEL=("Chromecast4lox: Ziel-Lautsprecher",
    "Chromecast4lox: target speaker"),
  H_CC_ZIEL=("Name des Lautsprechers wie in Chromecast4lox (Umlaute und Leerzeichen werden wie dort umgeschrieben) oder <span class='sm-mono'>alle</span> für jeden Lautsprecher. Die Lautstärke der Ansage stellt Chromecast4lox ein (Ansagelautstärke).",
    "Name of the speaker as in Chromecast4lox (umlauts and spaces are rewritten as there) or <span class='sm-mono'>alle</span> for every speaker. The announcement volume is set in Chromecast4lox."),
  L_ALEXA_GERAET=("Alexa-NG: Gerät",
    "Alexa-NG: device"),
  H_ALEXA_GERAET=("Ein oder mehrere Geräte (durch Komma getrennt), <span class='sm-mono'>gruppe:&lt;name&gt;</span> oder <span class='sm-mono'>alle</span> - so, wie Alexa-NG sie nennt. Leer: das Standardgerät aus Alexa-NG.",
    "One or more devices (comma separated), <span class='sm-mono'>gruppe:&lt;name&gt;</span> or <span class='sm-mono'>alle</span> - as Alexa-NG names them. Empty: the default device of Alexa-NG."),
  L_ALEXA_TOKEN=("Alexa-NG: Sprechtoken",
    "Alexa-NG: speech token"),
  H_ALEXA_TOKEN=("Aus dem Reiter <i>Einbindung in Loxone</i> von Alexa-NG. Es wird wie ein Kennwort behandelt: nie angezeigt, nicht in der Sicherung, nie in einer Adresse (der Aufruf geht per POST an <span class='sm-mono'>127.0.0.1</span>). Leer lassen behält das gespeicherte.",
    "From the tab <i>Loxone integration</i> of Alexa-NG. It is treated like a password: never shown, not in the backup, never in an address (the call goes by POST to <span class='sm-mono'>127.0.0.1</span>). Leave empty to keep the stored one."),
  L_ALEXA_TOKEN_LOESCHEN=("Gespeichertes Sprechtoken löschen",
    "Delete the stored speech token"),
  P_ALEXA_TOKEN_GESETZT=("gespeichert (%d Zeichen) - leer lassen, um es zu behalten",
    "stored (%d characters) - leave empty to keep it"),
  P_ALEXA_TOKEN_LEER=("noch keins gespeichert",
    "none stored yet"),
  L_ALEXA_LAUT=("Alexa-NG: Lautstärke der Ansage (1-100)",
    "Alexa-NG: announcement volume (1-100)"),
  H_ALEXA_LAUT=("Leer: die Lautstärke des Geräts bleibt. Sonst stellt Alexa-NG sie für die Ansage ein und danach zurück.",
    "Empty: the device volume stays. Otherwise Alexa-NG sets it for the announcement and back afterwards."),
  FEHLER_CC_PRAEFIX=("Chromecast4lox: das Themenpräfix besteht aus Buchstaben, Ziffern, _ und -, höchstens vier Ebenen mit /, ohne + und #.",
    "Chromecast4lox: the topic prefix consists of letters, digits, _ and -, at most four levels with /, without + and #."),
  FEHLER_CC_ZIEL=("Chromecast4lox: der Ziel-Lautsprecher braucht 1 bis 60 Zeichen, ohne /, + und # (für alle Lautsprecher: alle).",
    "Chromecast4lox: the target speaker needs 1 to 60 characters, without /, + and # (for all speakers: alle)."),
  FEHLER_ALEXA_GERAET=("Alexa-NG: das Gerät darf höchstens 200 Zeichen und keine Steuerzeichen haben.",
    "Alexa-NG: the device may have at most 200 characters and no control characters."),
  FEHLER_ALEXA_TOKEN=("Alexa-NG: das Sprechtoken besteht aus 8 bis 128 Buchstaben, Ziffern, _ und -.",
    "Alexa-NG: the speech token consists of 8 to 128 letters, digits, _ and -."),
  HINWEIS_ALEXA_OHNE_TOKEN=("Alexa-NG ist gewählt, aber es ist kein Sprechtoken gespeichert - bis dahin sprechen die Lautsprecher der Sprachgeräte.",
    "Alexa-NG is selected, but no speech token is stored - until then the speakers of the voice devices speak."),
  FEHLER_LEER=("%s: das Feld ist leer. Ein leeres Feld behält den alten Wert nicht mehr - bitte einen Wert eintragen.",
    "%s: the field is empty. An empty field no longer keeps the old value - please enter a value."),
  NICHTS_GESPEICHERT=("Es wurde nichts gespeichert. Die eingetippten Werte stehen wieder im Formular, beanstandete Felder sind rot umrandet.",
    "Nothing was saved. The values you typed are back in the form, rejected fields have a red frame."),
  )
s("MIKRO",
  FEHLER_ZEICHEN=("Zeile %d: Adresse, Port oder Zone enthält Anführungs- oder Steuerzeichen.",
    "Line %d: address, port or zone contains quotes or control characters."),
  )
s("SICHER",
  WARN_RUECKSPIEL=("Achtung: Diese Sicherung würde beim Zurückspielen abgewiesen (%s). Sie wird trotzdem vollständig geliefert.",
    "Caution: this backup would be rejected on restore (%s). It is delivered in full anyway."),
  WARN_KOPF=("Diese Sicherung würde beim Zurückspielen abgewiesen: %s",
    "This backup would be rejected on restore: %s"),
  )
s("TEST",
  F_ANSAGE=("Zusätzliche Ansage",
    "Additional announcement"),
  A_ANSAGE_AUS=("aus (ab Werk) - Ansagen sprechen die Lautsprecher der Sprachgeräte.",
    "off (default) - announcements are spoken by the speakers of the voice devices."),
  A_ANSAGE_SATELLIT=("eingestellt, aber der Antwortweg ist <i>nur das Mikrofon</i> - sie wird nicht benutzt.",
    "configured, but the answer path is <i>microphone only</i> - it is not used."),
  A_RUECKFALL=("Bis das behoben ist, sprechen die Lautsprecher der Sprachgeräte (bisheriger Weg).",
    "Until this is fixed, the speakers of the voice devices speak (previous path)."),
  A_CC_EINSTELLUNG=("Chromecast4lox: kein Ziel-Lautsprecher eingestellt.",
    "Chromecast4lox: no target speaker configured."),
  A_CC_BROKER=("Chromecast4lox: am Broker nicht zu fragen (%s).",
    "Chromecast4lox: the broker cannot be asked (%s)."),
  A_CC_FEHLT=("Chromecast4lox meldet sich nicht (<span class='sm-mono'>%s/server/online</span> ist %s).",
    "Chromecast4lox does not report (<span class='sm-mono'>%s/server/online</span> is %s)."),
  A_CC_GERAET=("Chromecast4lox läuft, kennt aber keinen Lautsprecher '%s' (bekannt: %s).",
    "Chromecast4lox is running but knows no speaker '%s' (known: %s)."),
  A_CC_OK=("Chromecast4lox läuft (<span class='sm-mono'>%s/server/online</span> = 1), Ziel '%s'; Lautsprecher: %s.",
    "Chromecast4lox is running (<span class='sm-mono'>%s/server/online</span> = 1), target '%s'; speakers: %s."),
  A_ALEXA_TOKEN=("Alexa-NG: kein Sprechtoken gespeichert.",
    "Alexa-NG: no speech token stored."),
  A_ALEXA_OK=("Alexa-NG antwortet, das Sprechtoken passt.",
    "Alexa-NG responds, the speech token matches."),
  A_ALEXA_ABGEWIESEN=("Alexa-NG weist das Sprechtoken ab (%s).",
    "Alexa-NG rejects the speech token (%s)."),
  A_ALEXA_FEHLT=("Alexa-NG ist nicht installiert oder antwortet nicht (%s).",
    "Alexa-NG is not installed or does not respond (%s)."),
  A_LETZTE_OK=("Letzte Ansage vor %d s: angekommen.",
    "Last announcement %d s ago: delivered."),
  A_LETZTE_FEHL=("Letzte Ansage vor %d s: NICHT angekommen - %s",
    "Last announcement %d s ago: NOT delivered - %s"),
  )

# Ansage-3 (01.10.2026): Ausgabeart "Google-Lautsprecher (Chromecast 4 Lox NG)".
# Quelle: Pruefung-Durchgang-2026-09-29/vb_gs_sp_bau_skripte/texte_daten.py.
s("EINST",
  TTS_CC4LOX=("Google-Lautsprecher (Chromecast 4 Lox NG)",
    "Google speakers (Chromecast 4 Lox NG)"),
  H_GOOGLE=("Google-Lautsprecher (Chromecast 4 Lox NG)",
    "Google speakers (Chromecast 4 Lox NG)"),
  H_GOOGLE_TEXT=("Nur für die Art der Audioausgabe <b>Google-Lautsprecher (Chromecast 4 Lox NG)</b>. Die Ansage geht per POST an den Sprech-Endpunkt des Chromecast-Plugins auf diesem LoxBerry (<span class='sm-mono'>127.0.0.1/plugins/chromecast-4lox-ng/index.php</span>, ab dessen Fassung 1.3.15). Dort einrichten: Reiter <i>Einstellungen</i>, Abschnitt <i>Sprachausgabe für andere Plugins</i> - Haken setzen, Sprechtoken festlegen, wahlweise ein Standardgerät. Ruhezeit, Lautstärke-Obergrenze und Gong des Chromecast-Plugins gelten auch hier. Anders als <i>Chromecast4lox (über MQTT)</i> braucht dieser Weg keinen Broker. Nimmt das Chromecast-Plugin die Ansage nicht an, sprechen wie bisher die Lautsprecher der Sprachgeräte; auf einen anderen Google-Lautsprecher wird nie ausgewichen. Der Reiter Test sagt, was gilt.",
    "Only for the audio output type <b>Google speakers (Chromecast 4 Lox NG)</b>. The announcement goes by POST to the speech endpoint of the Chromecast plugin on this LoxBerry (<span class='sm-mono'>127.0.0.1/plugins/chromecast-4lox-ng/index.php</span>, from its version 1.3.15). Set up there: tab <i>Settings</i>, section <i>Speech output for other plugins</i> - tick the box, set a speech token, optionally a default device. Quiet time, volume limit and chime of the Chromecast plugin apply here as well. Unlike <i>Chromecast4lox (via MQTT)</i> this path needs no broker. If the Chromecast plugin does not accept the announcement, the speakers of the voice devices speak as before; it never switches to another Google speaker. The Test tab says what applies."),
  L_GOOGLE_GERAET=("Google: Gerät",
    "Google: device"),
  H_GOOGLE_GERAET=("Leer: das Standardgerät von Chromecast 4 Lox NG. Sonst ein Name aus dessen Geräteliste, genau wie dort geschrieben (z. B. <span class='sm-mono'>Küche Box</span>), mehrere durch Komma getrennt, <span class='sm-mono'>gruppe:&lt;Name&gt;</span> oder <span class='sm-mono'>alle</span>. Einen unbekannten Namen weist Chromecast 4 Lox NG ab - nie wird daraus <i>alle</i>.",
    "Empty: the default device of Chromecast 4 Lox NG. Otherwise a name from its device list, exactly as written there (e.g. <span class='sm-mono'>Küche Box</span>), several separated by commas, <span class='sm-mono'>gruppe:&lt;Name&gt;</span> or <span class='sm-mono'>alle</span>. Chromecast 4 Lox NG rejects an unknown name - it never becomes <i>alle</i>."),
  L_GOOGLE_TOKEN=("Google: Sprechtoken",
    "Google: speech token"),
  H_GOOGLE_TOKEN=("Das Sprechtoken aus Chromecast 4 Lox NG (Reiter <i>Einstellungen</i>, Abschnitt <i>Sprachausgabe für andere Plugins</i>) - ein anderes als das von Alexa-NG. Es wird wie ein Kennwort behandelt: nie angezeigt, nicht in der Sicherung, nie in einer Adresse (der Aufruf geht per POST an <span class='sm-mono'>127.0.0.1</span>). Leer lassen behält das gespeicherte.",
    "The speech token from Chromecast 4 Lox NG (tab <i>Settings</i>, section <i>Speech output for other plugins</i>) - a different one from Alexa-NG's. It is treated like a password: never shown, not in the backup, never in an address (the call goes by POST to <span class='sm-mono'>127.0.0.1</span>). Leave empty to keep the stored one."),
  L_GOOGLE_TOKEN_LOESCHEN=("Gespeichertes Google-Sprechtoken löschen",
    "Delete the stored Google speech token"),
  L_GOOGLE_LAUT=("Google: Lautstärke der Ansage (1-100)",
    "Google: announcement volume (1-100)"),
  H_GOOGLE_LAUT=("Leer: die Ansagelautstärke von Chromecast 4 Lox NG. Sonst gilt der Wert nur für diese Ansage, gedeckelt durch dessen Lautstärke-Obergrenze und Ruhezeit; danach stellt es die vorige Lautstärke wieder her.",
    "Empty: the announcement volume of Chromecast 4 Lox NG. Otherwise the value applies to this announcement only, capped by its volume limit and quiet time; afterwards it restores the previous volume."),
  FEHLER_GOOGLE_GERAET=("Google: das Gerät darf höchstens 200 Zeichen und keine Steuerzeichen haben.",
    "Google: the device may have at most 200 characters and no control characters."),
  FEHLER_GOOGLE_TOKEN=("Google: das Sprechtoken besteht aus 8 bis 128 Buchstaben, Ziffern, _ und -.",
    "Google: the speech token consists of 8 to 128 letters, digits, _ and -."),
  HINWEIS_GOOGLE_OHNE_TOKEN=("Google-Lautsprecher (Chromecast 4 Lox NG) ist gewählt, aber es ist kein Sprechtoken gespeichert - bis dahin sprechen die Lautsprecher der Sprachgeräte.",
    "Google speakers (Chromecast 4 Lox NG) is selected, but no speech token is stored - until then the speakers of the voice devices speak."),
  )
s("SICHER",
  WARN_GESPEICHERT=("Ein gespeicherter Wert ist ungültig (%s); er gilt als leer, und die Sicherung trägt den geltenden Wert. Bitte im Reiter Einstellungen prüfen und speichern.",
    "A stored value is invalid (%s); it counts as empty, and the backup carries the value in effect. Please check and save in the Settings tab."),
  )
s("TEST",
  A_GOOGLE_TOKEN=("Chromecast 4 Lox NG: kein Sprechtoken gespeichert.",
    "Chromecast 4 Lox NG: no speech token stored."),
  A_GOOGLE_OK=("Chromecast 4 Lox NG antwortet, das Sprechtoken passt.",
    "Chromecast 4 Lox NG responds, the speech token matches."),
  A_GOOGLE_OK_ABER=("Chromecast 4 Lox NG antwortet und das Sprechtoken passt, aber: %s",
    "Chromecast 4 Lox NG responds and the speech token matches, but: %s"),
  A_GOOGLE_SPRECHEN_AUS=("die Sprachausgabe für andere Plugins ist dort aus.",
    "speech output for other plugins is switched off there."),
  A_GOOGLE_DIENST_AUS=("der Dienst von Chromecast 4 Lox NG läuft nicht.",
    "the service of Chromecast 4 Lox NG is not running."),
  A_GOOGLE_ABGEWIESEN=("Chromecast 4 Lox NG weist das Sprechtoken ab (%s).",
    "Chromecast 4 Lox NG rejects the speech token (%s)."),
  A_GOOGLE_ANTWORT=("Chromecast 4 Lox NG antwortet nicht wie erwartet (%s).",
    "Chromecast 4 Lox NG does not answer as expected (%s)."),
  A_GOOGLE_FEHLT=("Chromecast 4 Lox NG fehlt, ist älter als 1.3.15 oder antwortet nicht (%s).",
    "Chromecast 4 Lox NG is missing, older than 1.3.15 or does not respond (%s)."),
  A_GOOGLE_OHNE_GRUND=("Antwort ohne GRUND",
    "answer without GRUND"),
  )

# NACHTRAG 0.12.0 - von Hand angehaengte Abschnitte, Reihenfolge wie geliefert.
#
# Die Oberflaeche 0.12.0 (Cloud-Lauf des Hausherrn) hat ihre neuen Texte als
# eigene Abschnitte HINTER [TEST] an beide Sprachdateien angehaengt: mit einem
# Kommentar davor, die Abschnitte nicht alphabetisch (UI012, LIB012, UI013)
# und die Schluessel darin in Bearbeitungsreihenfolge. Damit der Erzeuger die
# ausgelieferten Dateien byte-gleich wiederherstellt, stehen diese Abschnitte
# hier getrennt von T und werden in GENAU dieser Reihenfolge (Abschnitte wie
# Schluessel) nach dem sortierten Teil geschrieben. Ein Abschnitt darf nicht
# zugleich in T stehen - sonst stuende er zweimal in der Datei.
# Wer hier neue Texte ergaenzt, haengt sie hinten an den passenden Abschnitt;
# wer die Reihenfolge einmal angleichen will, zieht die Abschnitte nach T um
# (dann aendern sich die Dateien, aber kein Schluessel).
N = {}


def n(abschnitt, **paare):
    for schluessel, wert in paare.items():
        if schluessel in N.get(abschnitt, {}):
            raise SystemExit("Schluessel %s.%s doppelt." % (abschnitt, schluessel))
        N.setdefault(abschnitt, {})[schluessel] = wert


NACHTRAG_KOPF = (
    "; Oberflaeche 0.12.0 (Bearbeiter ui): neue Texte. Werte, die durch sp_e()\n"
    "; laufen, tragen echte Umlaute und keine Entitaeten.",
    "; User interface 0.12.0 (editor ui): new texts. Values that pass through\n"
    "; sp_e() carry real characters, no entities.")

n("UI012",
  CC_GEFUNDEN=("Die Auswahl kennt %d Lautsprecher, die Chromecast4lox am Broker meldet.",
    "The list knows %d speakers reported by Chromecast4lox at the broker."),
  CT_ABWEICHUNG=("%s: der laufende Container weicht von dem ab, was das Plugin heute anlegen würde.",
    "%s: the running container differs from what the plugin would create today."),
  CT_OHNE_SKRIPT=("Ohne JavaScript lädt sich die Seite nicht selbst neu - bitte den Link benutzen.",
    "Without JavaScript the page does not reload itself - please use the link."),
  FASSUNG=("Fassung %s",
    "Version %s"),
  FEHLER_BLOCK=("Der Block %s ist kein Block mit Feldern.",
    "The block %s is not a block of fields."),
  FEHLER_LAUT=("%s: leer lassen (unverändert) oder 1 bis 100 eintragen. 0 wäre stumm und gälte trotzdem als gesendet.",
    "%s: leave empty (unchanged) or enter 1 to 100. 0 would be silent and still count as sent."),
  FEHLER_MIKRO_ACHT=("Es sind höchstens 8 Mikrofone möglich, eingetragen sind %d. Bitte überzählige Zeilen leeren.",
    "At most 8 microphones are possible, %d are entered. Please clear the surplus rows."),
  FEHLER_MIKRO_ART=("Zeile %d: die Art muss Wyoming oder ESPHome sein.",
    "Row %d: the type must be Wyoming or ESPHome."),
  FEHLER_MIKRO_DOPPELT=("Zeile %d: den Namen '%s' trägt schon Zeile %d (ohne Namen zählt die Adresse als Name).",
    "Row %d: the name '%s' is already used by row %d (without a name the address counts as the name)."),
  FEHLER_MIKRO_EINTRAG=("Zeile %d: das ist kein brauchbarer Mikrofon-Eintrag.",
    "Row %d: this is not a usable microphone entry."),
  FEHLER_MIKRO_LISTE=("Die Mikrofone stehen nicht als Liste in der Datei.",
    "The microphones are not stored as a list in the file."),
  FEHLER_MIKRO_TEXT=("Zeile %d: Name oder Raum ist kein Text, ist länger als 200 Zeichen oder enthält Steuerzeichen.",
    "Row %d: name or room is not text, is longer than 200 characters or contains control characters."),
  FEHLER_NR=("Fehler %d",
    "Error %d"),
  FEHLER_RUHEZEIT=("Die Ruhezeit wird als Uhrzeit von 0:00 bis 23:59 eingetragen, zum Beispiel 22:00.",
    "Quiet hours are entered as a time of day from 0:00 to 23:59, for example 22:00."),
  FEHLER_SCHALTER=("%s: erlaubt sind nur 0 und 1.",
    "%s: only 0 and 1 are allowed."),
  FEHLER_SPRACHE_LISTE=("Die Sprache muss eine dieser sein: %s.",
    "The language must be one of these: %s."),
  FILTER_ALLE=("alle",
    "all"),
  FILTER_OHNE_RAUM=("(ohne Raum)",
    "(no room)"),
  H_FREITEXT_GEWINNT=("Steht im Freitextfeld etwas, gilt es - sonst die Auswahl.",
    "If the free text field holds something, it applies - otherwise the selection."),
  H_LOX_HAND=("Oder von Hand: Adresse und Zugangsdaten",
    "Or by hand: address and credentials"),
  H_LOX_MS=("Die Zugangsdaten stehen in der LoxBerry-Einstellung des Miniservers und kommen nicht in diese Seite.",
    "The credentials are taken from the LoxBerry settings of the Miniserver and never enter this page."),
  H_PROBE_OHNE_SPEICHERN=("Die Probe speichert nichts - zum Übernehmen danach auf Speichern drücken.",
    "The preview saves nothing - press Save afterwards to keep the settings."),
  H_STAENDE=("Frühere Stände der Satzdatei",
    "Earlier versions of the sentence file"),
  JSON_FEHLER=("Das ist kein gültiges JSON - es wurde nichts abgeschickt:",
    "This is not valid JSON - nothing was sent:"),
  JSON_STELLE=("(Zeile {zeile}, Spalte {spalte})",
    "(line {zeile}, column {spalte})"),
  K_ALLE_AB=("Alle abwählen",
    "Deselect all"),
  K_ALLE_AN=("Alle anwählen",
    "Select all"),
  K_LOG_HOLEN=("Protokoll herunterladen",
    "Download log"),
  K_MITSCHNITT_HOLEN=("Mitschnitt herunterladen",
    "Download trace"),
  K_NEU_ANLEGEN=("Neu anlegen",
    "Recreate"),
  K_ZURUECKHOLEN=("Zurückholen",
    "Restore"),
  LOG_FEHLT=("Diese Datei gibt es (noch) nicht.",
    "This file does not exist (yet)."),
  LOX_ADRESSE=("Die Adressen auf dieser Seite nennen den LoxBerry als %s.",
    "The addresses on this page name the LoxBerry as %s."),
  LOX_ADRESSE_BROWSER=("Das ist die Adresse aus der Adresszeile Ihres Browsers - erreicht der Miniserver den LoxBerry unter einer anderen, dort diese eintragen.",
    "This is the address from your browser's address bar - if the Miniserver reaches the LoxBerry under a different one, enter that one in Loxone."),
  LOX_ADRESSE_LB=("Sie stammt aus der Netzwerkeinstellung des LoxBerry.",
    "It comes from the network settings of the LoxBerry."),
  LOX_MS_FEHLT=("Dieser Miniserver ist in der LoxBerry-Einstellung nicht zu finden.",
    "This Miniserver cannot be found in the LoxBerry settings."),
  L_FILTER_ART=("Art:",
    "Type:"),
  L_FILTER_RAUM=("Raum:",
    "Room:"),
  L_LOX_MS=("Miniserver aus der LoxBerry-Einstellung",
    "Miniserver from the LoxBerry settings"),
  L_SCHLUESSEL_LOESCHEN=("Schlüssel löschen",
    "Delete key"),
  MIKRO_MEHR_ALS_ACHT=("In der Konfiguration stehen %d Mikrofone, möglich sind 8. Alle Zeilen werden angezeigt; gespeichert wird erst, wenn höchstens 8 übrig sind.",
    "The configuration holds %d microphones, 8 are possible. All rows are shown; saving works once at most 8 are left."),
  MIKRO_SCHLUESSEL_VERWORFEN=("Zeile %d: neue Adresse - der gespeicherte ESPHome-Schlüssel gehört zum vorigen Gerät und wurde nicht übernommen.",
    "Row %d: new address - the stored ESPHome key belongs to the previous device and was not carried over."),
  PLUGIN_DA=("%s ist installiert, Fassung %s.",
    "%s is installed, version %s."),
  PLUGIN_EINSTELLUNGEN=("Einstellungen öffnen",
    "Open settings"),
  PLUGIN_FEHLT=("%s ist auf diesem LoxBerry nicht installiert.",
    "%s is not installed on this LoxBerry."),
  PLUGIN_ZU_ALT=("%s nimmt Ansagen erst ab Fassung %s an.",
    "%s accepts announcements only from version %s on."),
  PROBE_NICHT_GESPEICHERT=("Die Probe hat nichts gespeichert. Die Eingaben stehen wieder im Formular; übernommen werden sie erst mit Speichern.",
    "The preview saved nothing. The inputs are back in the form; they are only kept after Save."),
  PROBE_TEXT=("Die Sprachsteuerung ist bereit.",
    "The voice control is ready."),
  P_ALEXA_GERAET=("kueche",
    "kitchen"),
  P_GOOGLE_GERAET=("Küche Box",
    "Kitchen speaker"),
  P_RAUM=("wohnzimmer",
    "living room"),
  ROHTEXT_ZURUECK=("Der eingegebene Text steht wieder im Feld.",
    "The text you entered is back in the field."),
  SPRACHE_DE=("Deutsch (de)",
    "German (de)"),
  SPRACHE_EN=("Englisch (en)",
    "English (en)"),
  STAENDE_ERKLAERUNG=("Vor jedem Speichern der Satzdatei aus dieser Oberfläche bleibt der bisherige Stand erhalten, die letzten %d. Zurückholen legt den jetzigen Stand ebenfalls hier ab.",
    "Before every save of the sentence file from this interface the previous version is kept, the last %d. Restoring also stores the current version here."),
  STAENDE_KEINE=("Noch kein früherer Stand - er entsteht beim nächsten Speichern.",
    "No earlier version yet - it is created on the next save."),
  STAND_FEHLT=("Diesen Stand gibt es nicht mehr.",
    "This version no longer exists."),
  STAND_KAPUTT=("Dieser Stand ist keine brauchbare Satzdatei (es fehlen regeln oder ziele).",
    "This version is not a usable sentence file (regeln or ziele is missing)."),
  STAND_ZURUECK=("Der Stand vom %s ist zurückgeholt: %d Regeln, %d Ziele.",
    "The version from %s has been restored: %d rules, %d targets."),
  TEST_SATZ=("schalte das Licht im Wohnzimmer ein",
    "turn on the light in the living room"),
  T_LOESCHEN=("Löschen",
    "Delete"),
  T_MAX=("max",
    "max"),
  T_MIN=("min",
    "min"),
  T_REGELN=("Regeln",
    "Rules"),
  T_URL=("Adresse (eigener Miniserver)",
    "Address (own Miniserver)"),
  ZIELE_HILFE=("Adresse und Lesen dürfen Zugangsdaten tragen; sie stehen hier maskiert und bleiben gespeichert, solange das Feld nicht geändert wird. Leeren entfernt sie. Was ein Ziel sonst noch trägt (etwa aus dem Rohtext), bleibt beim Speichern erhalten.",
    "Address and Read may carry credentials; they are shown masked and stay stored as long as the field is not changed. Clearing removes them. Anything else a target carries (for instance from the raw text) is kept on save."),
  ZIEL_ALIAS_DOPPELT=("Den Namen '%s' tragen die Ziele '%s' und '%s' - es gewinnt der längste passende Name, bei gleicher Länge das erste Ziel.",
    "The name '%s' is used by the targets '%s' and '%s' - the longest matching name wins, with equal length the first target."),
  ZIEL_SCHLUESSEL_LEER=("Zeile %d: der Schlüssel ist leer. Zum Löschen den Haken <i>Löschen</i> setzen.",
    "Row %d: the key is empty. To delete the target, tick <i>Delete</i>."),
  ZIEL_SCHLUESSEL_VORSCHLAG=("Zeile %d: im Schlüssel '%s' stehen Zeichen, die als MQTT-Thema nicht taugen (erlaubt: Buchstaben ohne Umlaute, Ziffern, _ und -). Vorschlag: <span class='sm-mono'>%s</span>",
    "Row %d: the key '%s' contains characters that do not work as an MQTT topic (allowed: letters without umlauts, digits, _ and -). Suggestion: <span class='sm-mono'>%s</span>"),
  ZIEL_URL_FALSCH=("Ziel '%s': die Adresse muss mit http:// oder https:// beginnen.",
    "Target '%s': the address must start with http:// or https://."),
  ZIEL_ZAHL_FALSCH=("Ziel '%s': min und max sind Zahlen (oder leer).",
    "Target '%s': min and max are numbers (or empty)."),
  BSP_ALT=("[schalte|mach] {ziel} [an|ein]",
    "[turn|switch] on {ziel}"),
  BSP_ANSAGE=("Das Garagentor steht offen",
    "The garage door is open"),
  BSP_DAUER=("mach {ziel} in {dauer} aus",
    "turn off {ziel} in {dauer}"),
  BSP_DRINGEND=("Wasseralarm im Keller",
    "Water alarm in the basement"),
  BSP_ISTWERT=("Es sind {istwert} Grad",
    "It is {istwert} degrees"),
  BSP_LEER=("{ziel} auf {wert} [prozent|]",
    "{ziel} to {wert} [percent|]"),
  BSP_REST=("sag mir {rest}",
    "tell me {rest}"),
  BSP_SATZ=("schalte das licht im wohnzimmer aus",
    "turn off the light in the living room"),
  BSP_WERT=("dimme {ziel} auf {wert}",
    "dim {ziel} to {wert}"),
  BSP_ZIEL=("schalte {ziel} ein",
    "turn on {ziel}"),
  BSP_ZONE=("Guten Morgen",
    "Good morning"),
  G_PI_NAME=("Raspberry Pi Zero 2 W, Pi 3/4/5 mit USB-Mikrofon",
    "Raspberry Pi Zero 2 W, Pi 3/4/5 with USB microphone"),
  )

n("LIB012",
  ABW_ABBILD=("Abbild %s statt %s",
    "image %s instead of %s"),
  ABW_MODELL=("Modell %s statt %s",
    "model %s instead of %s"),
  ABW_PORT=("Port %s statt %d auf dem LoxBerry",
    "port %s instead of %d on the LoxBerry"),
  ABW_SPRACHE=("Sprache %s statt %s",
    "language %s instead of %s"),
  ARCHIV=("Diese Oberfläche liegt nicht in einer LoxBerry-Installation - ausgepacktes Archiv oder Prüfordner. Es wurde nichts geschaltet.",
    "This interface is not part of a LoxBerry installation - unpacked archive or test folder. Nothing was switched."),
  ARCHIV_WURZEL=("Diese Oberfläche liegt nicht in einer LoxBerry-Installation (die Wurzel %s wurde gefunden, diese Datei liegt aber nicht darin) - ausgepacktes Archiv oder Prüfordner. Es wurde nichts geschaltet.",
    "This interface is not part of a LoxBerry installation (the root %s was found, but this file is not inside it) - unpacked archive or test folder. Nothing was switched."),
  BEFEHL_ABLEGEN=("Der Befehl ließ sich nicht ablegen: %s",
    "The command could not be stored: %s"),
  BEFEHL_DIENST_AUS=("Der Dienst läuft nicht - der Befehl wurde nicht eingereiht. Im Reiter Einstellungen starten.",
    "The service is not running - the command was not queued. Start it in the Settings tab."),
  BEFEHL_JSON=("Der Befehl ließ sich nicht als JSON darstellen (ungültiges UTF-8).",
    "The command could not be encoded as JSON (invalid UTF-8)."),
  BEFEHL_OHNE_ANTWORT=("Eingereiht, aber der Dienst hat innerhalb von %d s nicht geantwortet. Er arbeitet den Befehl zu Ende - das Ergebnis steht im Protokoll.",
    "Queued, but the service did not answer within %d s. It will finish the command - the result is in the log."),
  BEFEHL_ORDNER=("Der Ordner für die Warteschlange ließ sich nicht anlegen: %s",
    "The queue folder could not be created: %s"),
  CT_NICHT64=("%s: wird nicht eingerichtet - das System läuft mit 32-Bit-Programmen, die Abbilder gibt es nur für 64 Bit (amd64, arm64).",
    "%s: not set up - the system runs 32-bit programs, the images exist only for 64 bit (amd64, arm64)."),
  CT_NICHT64_SPERRE=("Die Sprachdienste lassen sich hier nicht einrichten: das System läuft mit 32-Bit-Programmen (auch wenn der Kern 64 Bit hat), und die Abbilder gibt es nur für amd64 und arm64. Abhilfe: ein 64-Bit-Betriebssystem (Raspberry Pi OS 64 Bit) oder die Dienste auf einem anderen Rechner betreiben und dessen Adresse in den Einstellungen eintragen.",
    "The speech services cannot be set up here: the system runs 32-bit programs (even if the kernel is 64-bit), and the images exist only for amd64 and arm64. Remedy: a 64-bit operating system (Raspberry Pi OS 64-bit), or run the services on another computer and enter its address in the settings."),
  CT_PORT_BELEGT=("%s: Port %d ist auf dem LoxBerry schon belegt - dort antwortet ein anderer Dienst (etwa Zigbee2MQTT auf 8080). Den Port in den Einstellungen ändern und erneut einrichten. Es wurde nichts angelegt.",
    "%s: port %d is already in use on the LoxBerry - another service answers there (e.g. Zigbee2MQTT on 8080). Change the port in the settings and set up again. Nothing was created."),
  DIENST_BEFEHL=("Unbekannter Befehl für den Dienst.",
    "Unknown command for the service."),
  DIENST_SH_FEHLT=("dienst.sh nicht gefunden: %s",
    "dienst.sh not found: %s"),
  ERKENNEN_ANDERER_WYOMING=("auf Port %d antwortet ein anderer Wyoming-Dienst",
    "a different Wyoming service answers on port %d"),
  ERKENNEN_FREMD=("auf Port %d antwortet ein anderer Dienst",
    "a different service answers on port %d"),
  ERKENNEN_LAEDT=("das Sprachmodell wird noch geladen",
    "the language model is still loading"),
  LOG_AUSGELAGERT=("Dieser Dienst läuft auf %s. Sein Protokoll steht dort - hier gibt es keinen Container dazu.",
    "This service runs on %s. Its log is there - there is no container for it here."),
  LOX_MS_FEHLT=("In LoxBerry ist kein Miniserver Nr. %d eingetragen (System, Miniserver).",
    "No Miniserver no. %d is configured in LoxBerry (System, Miniserver)."),
  LOX_WEITERLEITUNG=("Der Miniserver leitet weiter (HTTP %d), aber nicht von http nach https auf denselben Rechner. Der Weiterleitung wurde nicht gefolgt - die Anmeldung ginge sonst an ein fremdes Ziel.",
    "The Miniserver redirects (HTTP %d), but not from http to https on the same host. The redirect was not followed - the credentials would otherwise go to a foreign target."),
  NICHT_GESPEICHERT=("Nicht gespeichert.",
    "Not saved."),
  RUHEZEIT=("Ruhezeit %s bis %s",
    "Quiet time %s to %s"),
  SICH_CONFIG_SCHREIBEN=("Die Konfiguration ließ sich nicht schreiben.",
    "The configuration could not be written."),
  SICH_EINGESPIELT=("Sicherung eingespielt: %d Regeln, %d Ziele. Token und Miniserver-Adresse sind unverändert geblieben.",
    "Backup restored: %d rules, %d targets. Token and Miniserver address are unchanged."),
  SICH_FELDER=("Die Sicherung trägt Werte, die das Formular abweist: %s. Es wurde nichts eingespielt.",
    "The backup carries values the form rejects: %s. Nothing was restored."),
  SICH_GROSS=("Die Datei ist größer als 2 MB - das ist keine Sicherung dieses Plugins.",
    "The file is larger than 2 MB - this is not a backup of this plugin."),
  SICH_KEIN_JSON=("Das ist kein gültiges JSON: %s",
    "This is not valid JSON: %s"),
  SICH_KENNZEICHEN=("Das ist keine Sicherung dieses Plugins (Kennzeichen fehlt).",
    "This is not a backup of this plugin (marker missing)."),
  SICH_LEER=("Die Datei ist leer.",
    "The file is empty."),
  SICH_LISTEN=("Die Satzdatei in der Sicherung hat keine Listen regeln und ziele.",
    "The sentence file in the backup has no lists regeln and ziele."),
  SICH_SAETZE_SCHREIBEN=("Die Satzdatei ließ sich nicht schreiben.",
    "The sentence file could not be written."),
  SICH_TEILE=("In der Sicherung fehlt die Konfiguration oder die Satzdatei.",
    "The backup lacks the configuration or the sentence file."),
  SICH_TOKEN=("Die Sicherung trägt ein Sprechtoken (%s) - eine Sicherung dieses Plugins trägt nie eines. Es wurde nichts eingespielt.",
    "The backup carries a speech token (%s) - a backup of this plugin never does. Nothing was restored."),
  SICH_WERTE=("Die Sicherung trägt unbrauchbare Werte (%s). Es wurde nichts eingespielt.",
    "The backup carries unusable values (%s). Nothing was restored."),
  TROCKEN_FEHLT=("sprachsteuerung_dienst.py fehlt.",
    "sprachsteuerung_dienst.py is missing."),
  TROCKEN_UNVERWERTBAR=("Der Trockenlauf lieferte keine verwertbare Antwort: %s",
    "The dry run returned no usable answer: %s"),
  VORLAGE_ZIELE_KOPF=("Erzeugt vom LoxBerry-Plugin Sprachsteuerung lokal. Versorgt vom MQTT-Gateway von LoxBerry über UDP an Port %d (im Gateway: UDP einschalten; Gateway V2: Thema %s/# abonnieren). Das Gateway sendet nur GEÄNDERTE Werte: damit dieselbe Aktion zweimal hintereinander ankommt, die Aktions-Themen im Gateway als nicht zwischengespeichert (Noncached) markieren. Über HTTP liefert das Gateway stattdessen an virtuelle Texteingänge mit diesen Namen: %s",
    "Created by the LoxBerry plugin Sprachsteuerung lokal. Fed by the LoxBerry MQTT gateway via UDP on port %d (in the gateway: enable UDP; gateway V2: subscribe to topic %s/#). The gateway only sends CHANGED values: for the same action to arrive twice in a row, mark the action topics as non-cached (Noncached) in the gateway. Via HTTP the gateway instead delivers to virtual text inputs with these names: %s"),
  VORLAGE_ZIEL_AKTION=("%s: spricht an, wenn die Aktion '%s' ankommt (MQTT-Thema %s). Über HTTP: virtueller Texteingang %s",
    "%s: fires when the action '%s' arrives (MQTT topic %s). Via HTTP: virtual text input %s"),
  VORLAGE_ZIEL_WERT=("%s: Zahlenwert (MQTT-Thema %s). Über HTTP: virtueller Eingang %s",
    "%s: numeric value (MQTT topic %s). Via HTTP: virtual input %s"),
  ZEICHEN=("%d Zeichen",
    "%d characters"),
  ZEITABLAUF=("%s hat nach %d s nicht geantwortet und wurde abgebrochen.",
    "%s did not answer within %d s and was aborted."),
  )

n("UI013",
  ABO_DATEI_ANDERS=("Die Datei trägt etwas anderes als %s - sie wird beim nächsten Speichern der MQTT-Einstellungen ersetzt.",
    "The file contains something other than %s - it is replaced the next time the MQTT settings are saved."),
  ABO_DATEI_FEHLER=("Die Abo-Datei ließ sich nicht schreiben: %s",
    "The subscription file could not be written: %s"),
  ABO_DATEI_GESCHRIEBEN=("Abo-Datei für das MQTT-Gateway geschrieben: %s",
    "Subscription file for the MQTT gateway written: %s"),
  ABO_DATEI_PASST=("Sie trägt das Abo %s.",
    "It contains the subscription %s."),
  ABO_DATEI_V1=("Das MQTT-Gateway V1 liest diese Datei von selbst und bemerkt Änderungen ohne Neustart - der Eintrag von Hand unter Subscriptions ist damit nicht mehr nötig.",
    "MQTT gateway V1 reads this file by itself and notices changes without a restart - a manual entry under Subscriptions is no longer needed."),
  ABO_DATEI_V2=("Das MQTT-Gateway V2 liest diese Datei nicht (es findet die Themengruppe von selbst); sie schadet dort nicht.",
    "MQTT gateway V2 does not read this file (it finds the topic group by itself); it does no harm there."),
  ABO_KEINE_UMWANDLUNG=("Umwandlungen (mqtt_conversions.cfg, etwa ein=1) schreibt das Plugin bewusst nicht: das Gateway wendet sie auf die Themen aller Plugins an.",
    "The plugin deliberately writes no conversions (mqtt_conversions.cfg, e.g. ein=1): the gateway would apply them to the topics of all plugins."),
  A_LETZTE_ANSAGE_FEHL=("zuletzt NICHT angekommen (%s): %s",
    "last one did NOT arrive (%s): %s"),
  A_LETZTE_ANSAGE_OK=("zuletzt angekommen (%s)",
    "last one arrived (%s)"),
  A_LETZTE_ANSAGE_UNKLAR=("gesendet, Ausgang unklar (%s) - kein Beleg, dass gesprochen wurde; kein Rückfall",
    "sent, outcome unclear (%s) - no proof it was spoken; no fallback"),
  A_LETZTE_UNKLAR=("letzte Ansage vor %d s gesendet, Ausgang unklar (kein Beleg, dass gesprochen wurde)",
    "last announcement %d s ago sent, outcome unclear (no proof it was spoken)"),
  A_LETZTE_ANSAGE_UNBEKANNT=("Der Dienst meldet im Abbild kein Ergebnis einer Ansage (ältere Dienstfassung, noch keine Ansage oder Dienst gestoppt).",
    "The service reports no announcement result in its snapshot (older service version, no announcement yet, or service stopped)."),
  A_MQTT_DAUER_AUS=("ausgeschaltet (Reiter MQTT) - der Dienst verbindet sich nur zum Senden.",
    "switched off (MQTT tab) - the service connects only to send."),
  A_MQTT_DAUER_JA=("verbunden",
    "connected"),
  A_MQTT_DAUER_NEIN=("NICHT verbunden: %s",
    "NOT connected: %s"),
  A_MQTT_DAUER_SEIT=("verbunden seit %s",
    "connected since %s"),
  A_MQTT_DAUER_UNBEKANNT=("eingeschaltet, aber der Dienst meldet keinen Zustand (ältere Dienstfassung oder Dienst gestoppt).",
    "switched on, but the service reports no state (older service version or service stopped)."),
  A_TIMER=("%d laufen: %s",
    "%d running: %s"),
  A_TIMER_KEINE=("keine (oder der Dienst meldet sie nicht)",
    "none (or the service does not report them)"),
  BSP_DRINGEND_MIKRO=("Dringend, nur an einem Mikrofon",
    "Urgent, one microphone only"),
  BSP_DRINGEND_VOLL=("Ansage trotz Ruhezeit (ganze Adresse)",
    "Announcement despite quiet hours (full address)"),
  BSP_KOPF=("Token im Kopf X-Token (Skript, anderes Plugin)",
    "Token in the X-Token header (script, other plugin)"),
  BSP_MIKROFON=("Küche",
    "Kitchen"),
  BSP_POST=("Token als POST-Feld token",
    "Token as POST field token"),
  B_ANSAGE_GRUND=("Grund, wenn die letzte Ansage nicht ankam (leer bei Erfolg)",
    "Reason if the last announcement did not arrive (empty on success)"),
  B_ANSAGE_OK=("1, wenn die letzte Ansage angekommen ist, sonst 0",
    "1 if the last announcement arrived, otherwise 0"),
  B_CMD_RUHE=("0 oder 1 - Ansagen stilllegen bzw. freigeben (wie aktion=ruhe)",
    "0 or 1 - mute or release announcements (like aktion=ruhe)"),
  B_CMD_SATZ=("Nutzlast = ein Satz, verarbeitet, als hätte ihn jemand gesprochen (wie aktion=satz)",
    "Payload = a sentence, processed as if someone had spoken it (like aktion=satz)"),
  B_CMD_SPRECHEN=("Nutzlast = Text, der angesagt wird (wie aktion=sprechen)",
    "Payload = text to announce (like aktion=sprechen)"),
  B_MIKRO_ZUSTAND=("Zustand je Mikrofon (etwa verbunden, hört, getrennt)",
    "State per microphone (e.g. connected, listening, disconnected)"),
  B_ONLINE_LW=("1, solange der Dienst verbunden ist; 0 setzt der Broker als Letzten Willen, wenn die Verbindung abreißt",
    "1 while the service is connected; the broker sets 0 as last will when the connection drops"),
  CT_FREMD_PORT=("fremder Dienst auf Port %d: %s",
    "foreign service on port %d: %s"),
  FEHLER_RAUMAUSGABE=("Zeile %d: Ausgabe dieses Raums - %s ist unbrauchbar (es gilt dieselbe Regel wie für das gleichnamige Feld unter Einstellungen).",
    "Row %d: output of this room - %s is unusable (the same rule applies as for the field of the same name in Settings)."),
  FEHLER_RAUMAUSGABE_BLOCK=("Zeile %d: die Ausgabe dieses Raums ist ein Block mit höchstens den Feldern alexa_geraet, google_geraet, cc_ziel und sonos_zone",
    "Row %d: the output of this room is a block with at most the fields alexa_geraet, google_geraet, cc_ziel and sonos_zone"),
  FEHLER_RUHE_BIS=("Das Ende der Ruhezeit wird als Uhrzeit von 0:00 bis 24:00 eingetragen, zum Beispiel 07:00 (24:00 = Mitternacht).",
    "The end of the quiet hours is entered as a time from 0:00 to 24:00, e.g. 07:00 (24:00 = midnight)."),
  FEHLER_URL_MS=("Die Adresse muss mit http://, https:// oder ms://Nr/ (Miniserver 1 bis 99 aus der LoxBerry-Einstellung) beginnen.",
    "The address must start with http://, https:// or ms://no/ (Miniserver 1 to 99 from the LoxBerry settings)."),
  F_LETZTE_ANSAGE=("Letzte Ansage",
    "Last announcement"),
  F_MQTT_DAUER=("Dauerverbindung zum Broker",
    "Permanent broker connection"),
  F_TIMER=("Laufende Timer",
    "Running timers"),
  HINWEIS_MQTT_LESEN=("Ein Ziel liest seinen Wert über mqtt:Thema. Das geht nur mit der Dauerverbindung zum Broker - einschalten im Reiter MQTT.",
    "A target reads its value via mqtt:topic. This only works with the permanent broker connection - switch it on in the MQTT tab."),
  HINWEIS_MUSIK_OHNE_MS=("Musik leiser stellen und Musik steuern wirken nur mit dem Loxone Music Server als Art der Audioausgabe (MusicServer4Home kennt diese Schnittstelle nicht).",
    "Lowering and controlling music only work with the Loxone Music Server as audio output type (MusicServer4Home does not offer this interface)."),
  HINWEIS_TOKEN_POST=("Der Endpunkt nimmt das Token auch im Kopf X-Token oder als POST-Feld token an - dann steht es nicht im Zugriffsprotokoll des Webservers. Aktion und Text bleiben in der Adresse. Ein virtueller Ausgang in Loxone kann meist nur GET und bleibt bei ?token=.",
    "The endpoint also accepts the token in the X-Token header or as POST field token - then it does not appear in the web server access log. Action and text stay in the address. A virtual output in Loxone can usually only do GET and stays with ?token=."),
  HINWEIS_WAECHTER=("Nach einem Neustart des Webservers startet der Wächter den Dienst binnen einer Minute neu.",
    "After a restart of the web server, the watchdog restarts the service within one minute."),
  H_ABO_DATEI=("Abo-Datei für das Gateway:",
    "Subscription file for the gateway:"),
  H_AUSFALL=("Nach einem Ausfall",
    "After a failure"),
  H_DOCKER_NEUSTART=("Gilt nur für Container auf diesem LoxBerry, die das Plugin selbst angelegt hat. Ab Werk aus: ein Neustart unterbricht auch einen Satz, der gerade verarbeitet wird.",
    "Applies only to containers on this LoxBerry that the plugin created itself. Off by default: a restart also interrupts a sentence being processed."),
  H_MQTT_DAUER=("Ohne sie verbindet sich der Dienst nur kurz zum Senden. Mit ihr hört er auf Befehle über MQTT, meldet den Zustand je Mikrofon und das Ergebnis jeder Ansage und kann Werte aus MQTT-Themen lesen. Die Themen:",
    "Without it the service connects only briefly to send. With it, it listens for commands via MQTT, reports the state of each microphone and the result of every announcement, and can read values from MQTT topics. The topics:"),
  H_MQTT_DAUER_LESEN=("Werte lesen: im Reiter Sätze darf im Feld Lesen eines Ziels mqtt:Thema stehen (ohne # und +) - der Dienst nimmt den zuletzt dort gesehenen Wert.",
    "Reading values: in the Sentences tab, the Read field of a target may contain mqtt:topic (without # and +) - the service uses the value last seen there."),
  H_MUSIK=("Musik",
    "Music"),
  H_MUSIK_DUCKEN_LAUT=("0 bis 100. 0 schaltet die Musik während der Ansage ganz leise.",
    "0 to 100. 0 silences the music completely during the announcement."),
  H_MUSIK_STEUERN=("Sätze wie „lauter“, „leiser“, „Pause“, „weiter“ oder „nächster Titel“ (ohne Ziel) gehen dann an die Zone des Mikrofons am Music Server.",
    "Sentences like “louder”, “quieter”, “pause”, “resume” or “next track” (without a target) then go to the microphone's zone on the Music Server."),
  H_MUSIK_TEXT=("Beides nur mit dem Loxone Music Server als Art der Audioausgabe und einer Zone am Mikrofon; ab Werk aus.",
    "Both only with the Loxone Music Server as audio output type and a zone on the microphone; off by default."),
  H_NICHT64=("Einrichten gesperrt",
    "Setup blocked"),
  H_RAUMAUSGABE=("Ausgabe dieses Raums",
    "Output of this room"),
  H_RUHE_BIS=("24:00 heißt bis Mitternacht.",
    "24:00 means until midnight."),
  H_SONOS=("Sonos über Sonos4Lox (ab Werk nicht gewählt)",
    "Sonos via Sonos4Lox (not selected by default)"),
  H_SONOS_LAUT=("Leer = die Lautstärke von Sonos4Lox, sonst 1 bis 100.",
    "Empty = the volume of Sonos4Lox, otherwise 1 to 100."),
  H_SONOS_TEXT=("Die Ansage geht an das Plugin Sonos4Lox auf diesem LoxBerry (action=say). Sonos4Lox hat keinen Selbsttest: der Reiter Test prüft nur Zone und Installation, eine Probe würde sprechen.",
    "The announcement goes to the Sonos4Lox plugin on this LoxBerry (action=say). Sonos4Lox has no self-test: the Test tab only checks zone and installation, a probe would speak."),
  H_SONOS_ZONE=("Der Name der Zone, wie er in Sonos4Lox steht. Ohne Zone spricht Sonos4Lox nicht.",
    "The zone name as it appears in Sonos4Lox. Without a zone, Sonos4Lox does not speak."),
  L_DOCKER_NEUSTART=("Lokalen Container nach drei Fehlschlägen neu starten (höchstens alle 10 Minuten)",
    "Restart the local container after three failures (at most every 10 minutes)"),
  L_MQTT_DAUER=("Dauerhafte Verbindung zum Broker (Befehle über MQTT, Zustand je Mikrofon, Ansage-Ergebnis, Werte lesen)",
    "Permanent connection to the broker (commands via MQTT, state per microphone, announcement result, reading values)"),
  L_MUSIK_DUCKEN=("Musik leiser stellen, solange das Mikrofon zuhört und antwortet",
    "Lower the music while the microphone listens and answers"),
  L_MUSIK_DUCKEN_LAUT=("Lautstärke der Musik während der Ansage",
    "Music volume during the announcement"),
  L_MUSIK_STEUERN=("Musik per Sprache steuern",
    "Control music by voice"),
  L_RA_ALEXA_GERAET=("Alexa-Gerät",
    "Alexa device"),
  L_RA_CC_ZIEL=("Chromecast4lox-Lautsprecher",
    "Chromecast4lox speaker"),
  L_RA_GOOGLE_GERAET=("Google-Lautsprecher",
    "Google speaker"),
  L_RA_SONOS_ZONE=("Sonos-Zone",
    "Sonos zone"),
  L_SONOS_LAUT=("Lautstärke für Sonos",
    "Volume for Sonos"),
  L_SONOS_ZONE=("Sonos-Zone",
    "Sonos zone"),
  M_SONOS_LAUT=("Lautstärke für Sonos: leer lassen oder 1 bis 100 eintragen.",
    "Volume for Sonos: leave empty or enter 1 to 100."),
  M_SONOS_OHNE_ZONE=("Sonos4Lox ist gewählt, aber keine Zone eingetragen - ohne Zone spricht Sonos4Lox nicht.",
    "Sonos4Lox is selected, but no zone is entered - without a zone Sonos4Lox does not speak."),
  M_SONOS_ZONE=("Sonos-Zone: höchstens 200 Zeichen, ohne Steuerzeichen und ohne Leerraum am Rand.",
    "Sonos zone: at most 200 characters, no control characters, no leading or trailing spaces."),
  P_SONOS_ZONE=("Kueche",
    "Kitchen"),
  RAUMAUSGABE_HILFE=("Leer = wie unter Einstellungen. Ein Eintrag gilt nur für Antworten und Ansagen dieses Mikrofons und nur bei der passenden Art der Audioausgabe.",
    "Empty = as in Settings. An entry applies only to answers and announcements of this microphone and only with the matching audio output type."),
  R_AUS=("Dienst sendet",
    "service sends"),
  R_EIN=("an den Dienst",
    "to the service"),
  TTS_SONOS4LOX=("Sonos (Sonos4Lox)",
    "Sonos (Sonos4Lox)"),
  T_BEISPIEL=("Beispiel",
    "Example"),
  T_RICHTUNG=("Richtung",
    "Direction"),
  T_SCHRITT=("Schritt",
    "Step"),
  T_SONOS=("Sonos4Lox: Zone %s über %s (nicht abgefragt - eine Probe würde sprechen).",
    "Sonos4Lox: zone %s via %s (not queried - a probe would speak)."),
  VORLAGE_NONCACHED=("Das MQTT-Gateway sendet nur GEÄNDERTE Werte. Seit 0.12.5 setzt das Plugin die Aktions-Themen %s/Thema/aktion 2 Sekunden nach jedem Befehl auf „-“ zurück - dieselbe Aktion kommt so auch zweimal hintereinander an (zweimal Licht an); Noncached im Gateway ist dafür nicht mehr nötig.",
    "The MQTT gateway only sends CHANGED values. Since 0.12.5 the plugin resets the action topics %s/topic/aktion to “-” 2 seconds after each command - so the same action also arrives twice in a row (two times light on); Noncached in the gateway is no longer needed for that."),
  VORLAGE_ZIELE=("Die Vorlage je Ziel heißt %s: ein virtueller UDP-Eingang (VirtualInUdp), den das MQTT-Gateway über UDP an Port %d beliefert - im Gateway muss UDP eingeschaltet sein.",
    "The per-target template is called %s: a virtual UDP input (VirtualInUdp) fed by the MQTT gateway via UDP on port %d - UDP must be enabled in the gateway."),
  ZIEL_LESEN_FALSCH=("Ziel '%s': die Leseadresse muss mit http://, https://, ms://Nr/ oder mqtt:Thema (ohne # und +) beginnen.",
    "Target '%s': the read address must start with http://, https://, ms://no/ or mqtt:topic (without # and +)."),
  ZIEL_SCHRITT_FALSCH=("Ziel '%s': der Schritt ist eine Zahl größer als 0 (oder leer).",
    "Target '%s': the step is a number greater than 0 (or empty)."),
  ZIEL_URL_FALSCH=("Ziel '%s': die Adresse muss mit http://, https:// oder ms://Nr/ beginnen.",
    "Target '%s': the address must start with http://, https:// or ms://no/."),
  # ---- vb_st2_sp (08.10.2026): Heimnetz-Pflicht beim Speichern (0.12.2) ----
  FEHLER_TTS_IP_HEIMNETZ=("Adresse des Music Servers: der Rechner liegt nicht im Heimnetz. Erlaubt sind private Adressen (192.168.x.x, 10.x.x.x, 172.16.x.x bis 172.31.x.x), Namen ohne Punkt und Namen auf .local, .lan, .home, .fritz.box, .home.arpa, .internal, .intranet oder .intern.",
    "Music Server address: the host is not in the home network. Allowed are private addresses (192.168.x.x, 10.x.x.x, 172.16.x.x to 172.31.x.x), names without a dot and names ending in .local, .lan, .home, .fritz.box, .home.arpa, .internal, .intranet or .intern."),
  FEHLER_TTS_VORLAGE_HEIMNETZ=("Loxone-Audioausgabe: die Vorlage führt zu einem Rechner außerhalb des Heimnetzes oder trägt Benutzerdaten vor dem Rechner. Vor dem ersten / stehen nur {ip}, {port} oder ein Rechner im Heimnetz.",
    "Loxone audio output: the template leads to a host outside the home network or carries user data before the host. Before the first / only {ip}, {port} or a host in the home network may stand."),
  )

KOPF_DE = """; Sprachsteuerung lokal - Sprachdatei Deutsch
;
; ERZEUGT von Werkzeuge/sp_sprache_erzeugen.py - NICHT von Hand pflegen.
; Wer einen Text aendert, aendert ihn im Erzeuger und laesst beide Dateien
; neu schreiben. Sonst kennt eine der beiden Sprachen einen Schluessel nicht.
;
; Regeln (Hausstandard):
;   - JEDER Wert steht in doppelten Anfuehrungszeichen. Bei parse_ini_file
;     beginnt mit ';' ein Kommentar - ein unquotierter Wert wuerde dort
;     abgeschnitten. Das trifft ausgerechnet jede HTML-Entitaet.
;   - Innerhalb eines Wertes steht KEIN weiteres doppeltes Anfuehrungszeichen.
;     HTML-Attribute deshalb einfach quoten: <span class='sm-mono'>.
;   - Werte, die im PHP durch sp_e() laufen, tragen echte Umlaute statt
;     Entitaeten - sonst stuende 'pr&uuml;fen' auf dem Bildschirm.
;   - Jeder im PHP benutzte Schluessel steht in BEIDEN Sprachdateien.
"""

KOPF_EN = KOPF_DE.replace("Sprachdatei Deutsch", "Language file English")


def schreiben(pfad: Path, kopf: str, index: int) -> int:
    abschnitte = {}
    for (ab, sch), wert in T.items():
        if not isinstance(wert, tuple) or len(wert) != 2:
            raise SystemExit("Schluessel %s.%s hat kein Paar (de, en)." % (ab, sch))
        text = wert[index]
        if '"' in text:
            raise SystemExit("Schluessel %s.%s enthaelt ein doppeltes "
                             "Anfuehrungszeichen." % (ab, sch))
        abschnitte.setdefault(ab, {})[sch] = text
    zeilen = [kopf]
    for ab in sorted(abschnitte):
        zeilen.append("\n[%s]" % ab)
        for sch in sorted(abschnitte[ab]):
            zeilen.append('%s = "%s"' % (sch, abschnitte[ab][sch]))
    # Nachtrag (siehe N): Leerzeile, Kommentar, dann die Abschnitte in
    # Einfuegereihenfolge, ohne zu sortieren.
    anzahl = sum(len(v) for v in abschnitte.values())
    if N:
        zeilen.append("")
        zeilen.append(NACHTRAG_KOPF[index])
        for nr, (ab, paare) in enumerate(N.items()):
            if ab in abschnitte:
                raise SystemExit("Abschnitt [%s] steht in T und im Nachtrag." % ab)
            zeilen.append(("[%s]" if nr == 0 else "\n[%s]") % ab)
            for sch, wert in paare.items():
                if not isinstance(wert, tuple) or len(wert) != 2:
                    raise SystemExit("Schluessel %s.%s hat kein Paar (de, en)." % (ab, sch))
                if '"' in wert[index]:
                    raise SystemExit("Schluessel %s.%s enthaelt ein doppeltes "
                                     "Anfuehrungszeichen." % (ab, sch))
                zeilen.append('%s = "%s"' % (sch, wert[index]))
                anzahl += 1
    # newline='' UND \n: die Datei landet auf einem Linux-System. Ohne das
    # schreibt Python unter Windows CRLF, und die Sprachdateien waeren als
    # einzige Dateien des Pakets anders als der Rest.
    with pfad.open("w", encoding="utf-8", newline="") as f:
        f.write("\n".join(zeilen) + "\n")
    return anzahl


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    ordner = Path(sys.argv[1])
    ziel = ordner / "templates" / "lang"
    if not ziel.is_dir():
        print("Nicht gefunden: %s" % ziel)
        return 2
    n = schreiben(ziel / "language_de.ini", KOPF_DE, 0)
    m = schreiben(ziel / "language_en.ini", KOPF_EN, 1)
    print("geschrieben: %d Schluessel deutsch, %d englisch" % (n, m))
    return 0 if n == m else 1


# ---------------------------------------------------------------------------
# STAND (vb_g11_sp, 24.10.2026, Gruppe 11 / MQTT): Sprachsteuerung 0.12.7 - Werte ueber das MQTT-Gateway, Befehle
# ueber die gemeinsame Befehlsbruecke (Entwurf Musterprojekt/entwurf_gruppe11_sp.txt, Entscheidungen Gruppe 11).
# Neu [BEFEHL]; LOX.* fuer den Reiter Einbindung (HTTP-Endpunkt und alter Befehlsweg zugeklappt), BAUSTEIN.* wortgleich
# zu Musterprojekt/baustein_listen.txt (Nachzug 24.10., md5 5c26b2fd...; Seite "Sprachsteuerung" 25 statt 26 Zeilen,
# Z1_26 entfaellt), Korrekturen S16 (EINST.H_PROBE), S21/S22 (LIB012.VORLAGE_ZIELE_KOPF), S23 (TEST.UNGEPRUEFT), E2
# (LOXIMP.H_SPERRE), S6 (LIB012.DIENST_BELEGT), S14/S15 (TEST.A_WAKE_UNNOETIG, TEST.A_DIENST_FREMD), Endpunkt aus
# (TEST.A_ENDPUNKT_AUS). Ein Wert mit %1$s/%2$s (BAUSTEIN.Z3_03/08/10/12/18) bekommt Praefix und doppeltes
# Anfuehrungszeichen ueber sprintf() - in einer Sprachdatei darf keines stehen.
# ---------------------------------------------------------------------------
_GW = "Virtueller Eingang (Name wie das MQTT-Gateway ihn vergibt, Plugin Sprachsteuerung)"
_GW_EN = "Virtual Input (name as the MQTT gateway assigns it, plugin Sprachsteuerung)"
_VQ = "Virtueller Ausgang Befehl (Vorlage „LoxBerry MQTT-Gateway“, MQTT)"
_VQ_EN = "Virtual Output Command (template “LoxBerry MQTT-Gateway”, MQTT)"

s("BEFEHL",
  H=("Befehle über MQTT", "Commands via MQTT"),
  TEXT=("Loxone schickt Ansagen, Sätze und die Stilllegung über das MQTT-Gateway an das Plugin (Themen unter %s, die Liste steht im Reiter Einbindung in Loxone, Schritt 4). Die Befehlsbrücke des Plugins reicht jeden an den Sprachdienst weiter - dieselbe Prüfung und dieselbe Warteschlange wie der HTTP-Endpunkt - und quittiert ihn. Ohne den ersten Haken nimmt sie keinen an.",
        "Loxone sends announcements, sentences and muting to the plugin via the MQTT gateway (topics below %s; the list is on the tab Integration into Loxone, step 4). The plugin's command bridge passes each one to the voice service - the same check and the same queue as the HTTP endpoint - and acknowledges it. Without the first tick it accepts none."),
  L_EIN=("Befehle über MQTT annehmen", "Accept commands via MQTT"),
  H_EIN=("Ab Werk aus. Allein genügt der Haken für „ruhe“ (Ansagen stilllegen und freigeben). Speichern startet bzw. hält die Befehlsbrücke sofort; sonst tut es der Wächter binnen einer Minute.",
         "Off by default. On its own the tick covers “ruhe” (mute and unmute announcements). Saving starts or stops the command bridge right away; otherwise the watchdog does it within a minute."),
  L_STEUERN=("Ansagen und Sätze über MQTT zulassen (sprechen, alarm, satz)", "Allow announcements and sentences via MQTT (sprechen, alarm, satz)"),
  H_STEUERN=("Ab Werk aus. Ansagen erzeugen Ton im Haus, „alarm“ übergeht dabei Ruhezeit und Stilllegung, und ein Satz kann über die Ziele schalten, Timer anlegen und Musik steuern. Derselbe Ansagetext wird innerhalb von 10 s nur einmal angenommen.",
             "Off by default. Announcements make sound in the house, “alarm” overrides quiet hours and muting, and a sentence can switch via the targets, create timers and control music. The same announcement text is accepted only once within 10 s."),
  HEIMNETZ=("Jeder im Heimnetz kann über den UDP-Eingang des MQTT-Gateways Befehle senden – deshalb sind beide Haken ab Werk aus.",
            "Anyone on the home network can send commands via the UDP input of the MQTT gateway – that is why both ticks are off by default."),
  QUITTUNG=("Das Plugin quittiert jeden Befehl unter %s – „angenommen“ oder „abgelehnt“ mit Grund, nie zurückbehalten; etwa „abgelehnt: DIENST_LAEUFT_NICHT“. Das Musterprojekt liest die Quittung nicht; die Wirkung zeigen ok und grund (Satz), ansage_ok (Ansage, nur mit Dauerverbindung) und ruhe (Stilllegung, mit dem nächsten Herzschlag).",
            "The plugin acknowledges every command under %s – “angenommen” (accepted) or “abgelehnt” (rejected) with a reason, never retained; for example “abgelehnt: DIENST_LAEUFT_NICHT”. The sample project does not read the acknowledgement; the effect shows in ok and grund (sentence), ansage_ok (announcement, only with the permanent connection) and ruhe (muting, with the next heartbeat)."),
  M_PRAEFIX=("Für Befehle über MQTT darf das Präfix je Ebene nur Buchstaben, Ziffern, Unterstrich und Bindestrich tragen (höchstens 5 Ebenen, keine leere): „%s“. Entweder das Präfix ändern oder den Haken „Befehle über MQTT annehmen“ weglassen.",
             "For commands via MQTT the prefix may carry only letters, digits, underscore and hyphen per level (at most 5 levels, none empty): “%s”. Either change the prefix or leave the tick “Accept commands via MQTT” off."),
  M_GESTARTET=("Befehlsbrücke gestartet: %s", "Command bridge started: %s"),
  M_ANGEHALTEN=("Befehlsbrücke angehalten: %s", "Command bridge stopped: %s"),
  M_START_FEHL=("Die Befehlsbrücke ließ sich nicht starten: %s – der Wächter versucht es im Minutentakt erneut (höchstens alle 10 Minuten); im Reiter Test die Zeile „Läuft die Befehlsbrücke?“ lesen.",
                "The command bridge could not be started: %s – the watchdog tries again every minute (at most every 10 minutes); read the row “Is the command bridge running?” on the Test tab."),
  M_STOP_FEHL=("Die Befehlsbrücke ließ sich nicht anhalten: %s", "The command bridge could not be stopped: %s"),
  L_CMD_EIN=("Alten Befehlsweg <Präfix>/cmd/… annehmen (nur mit der dauerhaften Verbindung)",
             "Accept the old command path <prefix>/cmd/… (only with the permanent connection)"),
  H_CMD_EIN=("Bis 0.12.6 der einzige Befehlsweg über MQTT, ohne Quittung (%s/cmd/sprechen, satz, ruhe). Beim Update behält ihn, wer die dauerhafte Verbindung eingeschaltet hatte; neu installiert ist er aus. Neue Anlagen nehmen die Befehlsbrücke oben.",
             "Up to 0.12.6 the only command path via MQTT, without acknowledgement (%s/cmd/sprechen, satz, ruhe). On update it stays for anyone who had the permanent connection switched on; on a new installation it is off. New setups use the command bridge above."),
  K_SPRECHEN=("Ansage", "Announcement"),
  K_ALARM=("Alarmansage", "Alarm announcement"),
  K_SATZ=("Satz", "Sentence"),
  K_RUHE=("Ansagen stilllegen", "Mute announcements"),
  B_STATUS_ZAEHLER=("Lebenszeichen: zählt mit jedem Herzschlag eins weiter (0 bis 999, läuft um); nie zurückbehalten. Bleibt es stehen, hängt der Dienst oder der LoxBerry.",
                    "Sign of life: counts up by one with every heartbeat (0 to 999, wraps around); never retained. If it stops, the service or the LoxBerry hangs."),
  B_STATUS_BEFEHLE=("Lebenszeichen der Befehlsbrücke (1 läuft, 0 angehalten); nie zurückbehalten.",
                    "Sign of life of the command bridge (1 running, 0 stopped); never retained."),
  T_NAME=("Name in Loxone (Gateway)", "Name in Loxone (gateway)"),
  T_ART=("Art", "Type"),
  T_V2=("Gateway Fassung 2", "Gateway version 2"),
  T_MUSTER=("im Musterprojekt", "in the sample project"),
  A_TEXT=("Virtueller Texteingang", "Virtual Text Input"),
  A_ZAHL=("Virtueller Eingang", "Virtual Input"),
  A_HAKEN=("Haken", "tick"),
  A_HAKEN_N=("Haken und Noncached", "tick and Noncached"),
  NAMEN_HINWEIS=("Die Tabelle nennt jedes Thema dieses Plugins mit dem Namen, den das Gateway vergibt (Präfix und Thema, „/“ und Leerzeichen als „_“). Ein anderes Präfix im Reiter MQTT ergibt andere Namen. Beim Gateway Fassung 2 die Themen der Spalte „im Musterprojekt“ in den Subscriptions anhaken, „Noncached“ wo genannt; Fassung 1 liest die Abo-Datei, die das Plugin selbst anlegt. Nach einem Neustart des Miniservers holt der zentrale „reconnect“ auf der Seite „LoxBerry MQTT-Gateway“ die zurückbehaltenen Werte.",
                 "The table lists every topic of this plugin with the name the gateway assigns (prefix and topic, “/” and spaces as “_”). Another prefix on the MQTT tab gives other names. With gateway version 2 tick the topics of the column “in the sample project” in the subscriptions, “Noncached” where stated; version 1 reads the subscription file the plugin writes itself. After a Miniserver restart the central “reconnect” on the page “LoxBerry MQTT-Gateway” fetches the retained values."),
  T_TITEL=("Befehl (Titel in Loxone Config)", "Command (title in Loxone Config)"),
  T_THEMA=("Befehl bei EIN", "Command on ON"),
  T_BEI_AUS=("Befehl bei AUS", "Command on OFF"),
  T_EINGREIFEND=("eingreifend", "intervening"),
  T_JA_ZWEITER=("ja – braucht zusätzlich „Ansagen und Sätze über MQTT zulassen“", "yes – also needs “Allow announcements and sentences via MQTT”"),
  T_NEIN=("nein – „Befehle über MQTT annehmen“ genügt", "no – “Accept commands via MQTT” is enough"),
  T_ADRESSE=("Virtueller Ausgang mit der Adresse /dev/udp/%s/%d (UDP-Eingang des MQTT-Gateways), „Nach dem Senden schließen“ an; jeder Befehl „publish …“, nie „retain“.",
             "Virtual output with the address /dev/udp/%s/%d (UDP input of the MQTT gateway), “close after send” on; every command “publish …”, never “retain”."),
  GATEWAY_NICHTS=("Für Befehle ist unter Gateway V1 und V2 nichts einzutragen. Unter V1 kommen über die Abo-Datei auch <präfix>/befehl/… und die Quittungen als Gateway-Namen an – harmlos, kein Befehlstitel heißt wie sie.",
                  "For commands nothing needs to be entered in gateway V1 or V2. Under V1 the subscription file also brings <prefix>/befehl/… and the acknowledgements as gateway names – harmless, no command title equals them."),
  UMLAUTE=("Ansagetexte möglichst ohne Umlaute schreiben (ae, oe, ue, ss), bis am Gerät gemessen ist, wie Loxone sie über UDP sendet.",
           "Write announcement texts without umlauts where possible (ae, oe, ue, ss) until it has been measured on the device how Loxone sends them via UDP."),
  F_BRUECKE=("Läuft die Befehlsbrücke?", "Is the command bridge running?"),
  F_EINRICHTUNG=("Ist die Befehlsbrücke eingerichtet (mosquitto-clients)?", "Is the command bridge set up (mosquitto-clients)?"),
  F_PRAEFIX=("Taugt das Präfix für Befehle?", "Does the prefix suit commands?"),
  F_NAMENSFILTER=("Liegt in der Warteschlange nur, was hingehört?", "Does the queue hold only what belongs there?"),
  F_HERZ=("Zählt das Lebenszeichen?", "Does the sign of life count?"),
  F_NAMEN=("Stimmen die Namen der Gateway-Eingänge?", "Are the gateway input names right?"),
  F_ABO=("Steht die Abo-Datei für das Gateway V1?", "Is the subscription file for gateway V1 in place?"),
  F_VORLAGE=("Taugt die Vorlage MQTT-Befehle?", "Is the MQTT command template valid?"),
  T_FEHLT=("bin/befehlsbruecke.php fehlt - das Plugin neu installieren.", "bin/befehlsbruecke.php is missing - reinstall the plugin."),
  T_DEFEKT=("Die Zuordnung der Befehlsbrücke taugt nicht: %s", "The command bridge mapping is not valid: %s"),
  T_AUS=("aus (Haken „Befehle über MQTT annehmen“ im Reiter MQTT nicht gesetzt)", "off (tick “Accept commands via MQTT” on the MQTT tab not set)"),
  T_ARCHIV=("nicht feststellbar (kein LoxBerry oder ausgepacktes Archiv)", "not determinable (no LoxBerry or unpacked archive)"),
  T_STEHT=("steht - der Wächter startet sie binnen einer Minute (höchstens alle 10 Minuten neu); Protokoll lesen", "stopped - the watchdog starts it within a minute (restarts at most every 10 minutes); read the log"),
  T_HAENGT=("hängt - ihr Zustand ist %d s alt", "hangs - its state is %d s old"),
  T_OHNE_ABO=("läuft, aber ohne Abo am Broker: %s", "running, but without a subscription at the broker: %s"),
  T_LAEUFT=("läuft seit %s; angenommen %d, abgelehnt %d; zuletzt %s", "running since %s; accepted %d, rejected %d; last %s"),
  T_UNKLAR=("--pruefen gab nichts aus", "--pruefen printed nothing"),
  T_EINRICHTUNG=("(Paket mosquitto-clients installieren bzw. das Plugin neu installieren)", "(install the package mosquitto-clients or reinstall the plugin)"),
  T_PRAEFIX_OK=("„%s“ – passt in die Grenze der Befehlsbrücke", "“%s” – fits the command bridge limits"),
  T_PRAEFIX=("„%s“ – für Befehle über MQTT je Ebene nur Buchstaben, Ziffern, _ und -", "“%s” – for commands via MQTT only letters, digits, _ and - per level"),
  T_WS_LEER=("leer", "empty"),
  T_WS_FREMD=("fremde Dateien im Ordner befehle/: %s", "foreign files in the folder befehle/: %s"),
  T_WS_ZAHL=("%d Befehl(e) warten, der älteste seit %d s", "%d command(s) waiting, the oldest for %d s"),
  T_HERZ_AUS=("kein Herzschlag (MQTT oder Herzschlag im Reiter MQTT aus) - das Musterprojekt meldet dann nach 3 Minuten", "no heartbeat (MQTT or heartbeat off on the MQTT tab) - the sample project then reports after 3 minutes"),
  T_HERZ_NIE=("der Dienst hat noch kein Lebenszeichen gezählt", "the service has not counted a sign of life yet"),
  T_HERZ=("status/zaehler = %d (vorher %s), vor %d s", "status/zaehler = %d (before %s), %d s ago"),
  T_NAMEN_FEHL=("passt nicht zu einem gesendeten Thema: %s", "does not match a sent topic: %s"),
  T_NAMEN_OK=("%d Namen, davon %d im Musterprojekt", "%d names, %d of them in the sample project"),
  T_ABO_OK=("steht: %s", "in place: %s"),
  T_ABO_FALSCH=("Abo-Datei: %s, erwartet „%s“ (legen postinstall und der Dienststart an; Reiter MQTT speichern schreibt sie neu)", "subscription file: %s, expected “%s” (written by postinstall and the service start; saving the MQTT tab rewrites it)"),
  T_VORLAGE_UNKLAR=("nicht prüfbar - PHP ohne simplexml", "not checkable - PHP without simplexml"),
  T_VORLAGE_KAPUTT=("die Vorlage MQTT-Befehle ist kein gültiges XML", "the MQTT command template is not valid XML"),
  T_VORLAGE_NAME=("ein Befehlstitel heißt wie ein Gateway-Eingang: %s", "a command title equals a gateway input name: %s"),
  T_VORLAGE_OK=("%d Befehle, kein Titel heißt wie ein Gateway-Eingang", "%d commands, no title equals a gateway input name"),
)

s("LOX",
  EINLEITUNG=("Die Sprachsteuerung sagt Loxone, WAS gemeint war. Was daraus wird, entscheidet der Miniserver - so bleibt die Logik dort, wo sie hingehört. Seit 0.12.7 holt das Musterprojekt die Werte über MQTT und sendet Ansagen, Sätze und die Stilllegung über MQTT an das Plugin. Der HTTP-Endpunkt steht unten für bestehende Anlagen (Haken „HTTP-Endpunkt für Loxone annehmen“). In den Schritten 2 bis 4 steht je eine fertig verbundene Seite aus dem LoxBerry-Plugins Musterprojekt mit Anleitung, Tabelle und Bild.",
              "The voice control tells Loxone WHAT was meant. What happens next is decided by the Miniserver - so the logic stays where it belongs. Since 0.12.7 the sample project fetches the values via MQTT and sends announcements, sentences and muting to the plugin via MQTT. The HTTP endpoint is below for existing setups (tick “Accept the HTTP endpoint for Loxone”). Steps 2 to 4 each contain a fully wired page from the LoxBerry plugins sample project with instructions, table and picture."),
  S1_TEXT=("Alles, was MQTT betrifft, steht im Reiter <i>MQTT</i>: „MQTT“ und den Herzschlag (60 s) an lassen (beides ab Werk an), der Zustand des Gateways und die vollständige Themenliste. Beim MQTT-Gateway Fassung 1 legt das Plugin die Abo-Datei selbst an; bei Fassung 2 die Themen der Namenstabelle (Schritt 2) in den Subscriptions anhaken, „Noncached“ wo genannt. Nach einem Neustart des Miniservers holt der zentrale „reconnect“ auf der Seite „LoxBerry MQTT-Gateway“ die zurückbehaltenen Werte. Für die Befehle (Schritt 4) dort die Haken „Befehle über MQTT annehmen“ und „Ansagen und Sätze über MQTT zulassen“ setzen.",
           "Everything about MQTT is on the <i>MQTT</i> tab: leave “MQTT” and the heartbeat (60 s) on (both on by default), the gateway state and the complete topic list. With MQTT gateway version 1 the plugin writes the subscription file itself; with version 2 tick the topics of the name table (step 2) in the subscriptions, “Noncached” where stated. After a Miniserver restart the central “reconnect” on the page “LoxBerry MQTT-Gateway” fetches the retained values. For the commands (step 4) set the ticks “Accept commands via MQTT” and “Allow announcements and sentences via MQTT” there."),
  S3_TEXT=("Der Zustand der Anlage kommt mit dem Herzschlag jede Minute über das MQTT-Gateway: je Wert ein <i>Virtueller Eingang</i>, dessen Namen das Gateway vergibt (Tabelle). Wichtig sind vor allem <span class='sm-mono'>bereit</span> - wie viele Mikrofone gerade wirklich verbunden sind - und <span class='sm-mono'>dienste_ok</span>: ein toter Whisper-Container sieht sonst genauso aus wie eine gesunde Anlage. Hängt der Dienst oder steht der LoxBerry, kommt kein Herzschlag mehr; das Lebenszeichen <span class='sm-mono'>status/zaehler</span> verrät es (seit 0.12.7).",
           "The state of the system arrives with the heartbeat every minute via the MQTT gateway: one <i>Virtual Input</i> per value, named by the gateway (table). Most important are <span class='sm-mono'>bereit</span> - how many microphones are really connected right now - and <span class='sm-mono'>dienste_ok</span>: otherwise a dead Whisper container looks just like a healthy system. If the service hangs or the LoxBerry stops, no heartbeat arrives; the sign of life <span class='sm-mono'>status/zaehler</span> gives it away (since 0.12.7)."),
  S4_TEXT=("Es geht auch andersherum: Loxone kann die Anlage etwas sagen lassen, ihr einen Satz unterschieben, als hätte ihn jemand gesprochen, oder die Ansagen stilllegen - über MQTT an die Befehlsbrücke des Plugins. Ein <i>Virtueller Ausgang</i> an den UDP-Eingang des MQTT-Gateways genügt - oder gleich die fertige Vorlage (Knopf unten).",
           "It also works the other way round: Loxone can make the system say something, pass it a sentence as if someone had spoken it, or mute the announcements - via MQTT to the plugin's command bridge. A <i>Virtual Output</i> to the UDP input of the MQTT gateway is enough - or the ready-made template (button below)."),
  S5_TITEL=("Das Token", "The token"),
  S7_TITEL=("Gegenprobe", "Cross-check"),
  K_VORLAGE_MQTT=("Vorlage: MQTT-Befehle", "Template: MQTT commands"),
  H_HTTP=("Bestehende Anlagen: HTTP-Endpunkt", "Existing setups: HTTP endpoint"),
  HTTP_TEXT=("Bis 0.12.6 holte ein Virtueller HTTP-Eingang „Sprachsteuerung lokal“ den Zustand mit dem Token ab, und ein Virtueller Ausgang „Sprachsteuerung lokal - Befehle“ schickte die Befehle über HTTP. Der Weg bleibt für bestehende Anlagen, steht aber seit 0.12.7 hinter einem Haken: ohne ihn antwortet der ganze Endpunkt mit 403 (ENDPUNKT_AUS). Beim Update ist er an, wenn ein Token gesetzt war.",
             "Up to 0.12.6 a Virtual HTTP Input “Sprachsteuerung lokal” fetched the state with the token, and a Virtual Output “Sprachsteuerung lokal - Befehle” sent the commands via HTTP. The path remains for existing setups, but since 0.12.7 it is behind a tick: without it the whole endpoint answers 403 (ENDPUNKT_AUS). On update it is on if a token was set."),
  L_ENDPUNKT_EIN=("HTTP-Endpunkt für Loxone annehmen", "Accept the HTTP endpoint for Loxone"),
  H_ENDPUNKT_EIN=("Ab Werk aus. Gilt für den ganzen Endpunkt, auch für status, diag und den Selbsttest des Tokens.",
                  "Off by default. Applies to the whole endpoint, including status, diag and the token self-test."),
  ERST_HAKEN=("Erst den Haken „HTTP-Endpunkt für Loxone annehmen“ setzen - ohne ihn antwortet jede Adresse der HTTP-Vorlagen mit 403.",
              "Set the tick “Accept the HTTP endpoint for Loxone” first - without it every address of the HTTP templates answers 403."),
  H_HTTP_ZUSTAND=("Zustand über HTTP (Vorlage „Sprachsteuerung lokal“)", "State via HTTP (template “Sprachsteuerung lokal”)"),
  H_HTTP_AUSGANG=("Befehle über HTTP (Vorlage „Sprachsteuerung lokal - Befehle“)", "Commands via HTTP (template “Sprachsteuerung lokal - Befehle”)"),
  H_CMD=("Alter Befehlsweg %s/cmd/…", "Old command path %s/cmd/…"),
  CMD_TEXT=("Bis 0.12.6 nahm der Dienst mit der dauerhaften Broker-Verbindung Befehle auf cmd/sprechen, cmd/satz und cmd/ruhe an - ohne Quittung. Seit 0.12.7 steht der Weg hinter einem eigenen Haken im Reiter MQTT; neue Anlagen nehmen die Befehlsbrücke (Schritt 4). Der Weg fällt weg, sobald ihn niemand mehr braucht.",
            "Up to 0.12.6 the service accepted commands on cmd/sprechen, cmd/satz and cmd/ruhe with the permanent broker connection - without acknowledgement. Since 0.12.7 the path is behind its own tick on the MQTT tab; new setups use the command bridge (step 4). The path will be dropped once nobody needs it."),
  CMD_AN=("Der alte Befehlsweg ist an.", "The old command path is on."),
  CMD_AUS=("Der alte Befehlsweg ist aus.", "The old command path is off."),
  CMD_ZULETZT=("Zuletzt benutzt: %s.", "Last used: %s."),
  CMD_NIE=("Seit dem Start des Dienstes kam dort nichts an.", "Nothing has arrived there since the service started."),
)

s("LOXIMP",
  H_SPERRE=("Nach mehreren falschen Anmeldungen sperrt der Miniserver den Zugang vorübergehend (Close Code 4003) – Benutzer und Kennwort vorher prüfen.",
            "After several failed logins the Miniserver blocks access temporarily (close code 4003) – check user and password first."),
)

s("TEST",
  A_ENDPUNKT_AUS=("aus (gewollt) - Haken „HTTP-Endpunkt für Loxone annehmen“ im Reiter Einbindung nicht gesetzt; das Musterprojekt nimmt MQTT",
                  "off (intended) - tick “Accept the HTTP endpoint for Loxone” on the Integration tab not set; the sample project uses MQTT"),
  A_DIENST_FREMD=("%s: %s – im Reiter Dienste Adresse und Port prüfen", "%s: %s – check address and port on the Services tab"),
  A_WAKE_UNNOETIG=("antwortet nicht auf %s. Kein eingetragenes Mikrofon braucht ihn (nur Wyoming-Mikrofone ohne eigenes Weckwort tun das).",
                   "does not answer on %s. No configured microphone needs it (only Wyoming microphones without their own wake word do)."),
  UNGEPRUEFT=("Ob ein Mikrofon Audio liefert, das Whisper versteht; ob das Weckwort in Ihrem "
              "Raum zuverlässig anspricht; ob ESPHome-Mikrofone den Audioweg tragen - das lässt "
              "sich nur mit echter Hardware feststellen. Das Plugin wurde ohne gebaut; geprüft "
              "wurde die ganze Kette gegen Attrappen, die das Originalpaket des "
              "Wyoming-Protokolls benutzen. Was danach kommt - Raumakustik, Nachhall, "
              "Nebengeräusche - entscheidet sich erst bei Ihnen. Ob das MQTT-Gateway die Werte behält (retain), ist am 13.09.2026 mit dem Gateway V1 gemessen (Reiter MQTT). Sätze werden nacheinander verarbeitet; ein Satz kann den nächsten bis rund 33 s warten lassen (aus den Fristen, am Gerät ungemessen) - die Mikrofone werden in der Zeit weiter bedient.",
              "Whether a microphone delivers audio Whisper understands; whether the wake word "
              "reliably triggers in your room; whether ESPHome microphones carry the audio path "
              "- only real hardware can establish that. The plugin was built without any; the "
              "whole chain was tested against stubs using the original Wyoming protocol "
              "package. What comes after - room acoustics, reverberation, background noise - is "
              "decided at your place. Whether the MQTT gateway retains the values was measured on 13.09.2026 with gateway V1 (MQTT tab). Sentences are processed one after another; one sentence can make the next wait for up to roughly 33 s (from the time limits, unmeasured on the device) - the microphones keep being served meanwhile."),
)

s("EINST",
  H_PROBE=("Erzeugt eine WAV-Datei mit der oben eingetragenen Stimme über die gespeicherte Piper-Adresse, ohne einen Container "
           "anzulegen. So lässt sich hören, wie eine Stimme klingt, bevor man sie einrichtet. "
           "Piper muss dafür laufen.",
           "Creates a WAV file with the voice entered above via the saved Piper address, without creating a container. That "
           "lets you hear how a voice sounds before setting it up. Piper must be running."),
)

N["LIB012"]["VORLAGE_ZIELE_KOPF"] = (
    "Erzeugt vom LoxBerry-Plugin Sprachsteuerung lokal. Versorgt vom MQTT-Gateway von LoxBerry über UDP an Port %d (im Gateway: UDP einschalten). Gateway V2: es liest keine Abo-Datei, sondern findet die Themengruppe %s selbst - dort die Datenpunkte in den Subscriptions anhaken. Seit 0.12.5 setzt das Plugin die Aktions-Themen 2 Sekunden nach jedem Befehl auf „-“ zurück; dieselbe Aktion kommt so auch zweimal hintereinander an, Noncached ist dafür nicht nötig. Über HTTP liefert das Gateway stattdessen an virtuelle Texteingänge mit diesen Namen: %s",
    "Created by the LoxBerry plugin Sprachsteuerung lokal. Fed by the LoxBerry MQTT gateway via UDP on port %d (in the gateway: switch on UDP). Gateway V2: it reads no subscription file but finds the topic group %s itself - tick the data points in its subscriptions there. Since 0.12.5 the plugin resets the action topics to “-” 2 seconds after each command; the same action thus also arrives twice in a row, Noncached is not needed for that. Via HTTP the gateway instead delivers to virtual text inputs with these names: %s")
n("LIB012",
  DIENST_BELEGT=("Ein anderer Start dieses Plugins läuft gerade – in einer Minute erneut versuchen.",
                 "Another start of this plugin is running right now – try again in a minute."),
)

# BAUSTEIN - wortgleich zu Musterprojekt/baustein_listen.txt (Nachzug 24.10.2026), Seite "Sprachsteuerung" 25 Zeilen.
T.pop(("BAUSTEIN", "Z1_26"))
_Z1 = [
    ("sprachsteuerung_online", "1 = der Sprachdienst läuft (kommt mit dem Herzschlag jede Minute), 0 = geordnet angehalten; MQTT-Gateway Fassung 2: Haken und „Noncached“",
     "1 = the voice service is running (comes with the heartbeat every minute), 0 = stopped in an orderly way; MQTT gateway version 2: tick and “Noncached”"),
    ("sprachsteuerung_mikrofone", "Anzahl der eingetragenen Mikrofone (retained)", "Number of configured microphones (retained)"),
    ("sprachsteuerung_bereit", "Anzahl der gerade verbundenen Mikrofone; jede Minute; Fassung 2: Haken und „Noncached“",
     "Number of microphones connected right now; every minute; version 2: tick and “Noncached”"),
    ("sprachsteuerung_dienste_ok", "Anzahl der erreichbaren Sprachdienste (Whisper, Piper und – wenn im Plugin eingeschaltet – Sprachmodell); jede Minute; Fassung 2: Haken und „Noncached“",
     "Number of reachable voice services (Whisper, Piper and – if switched on in the plugin – language model); every minute; version 2: tick and “Noncached”"),
    ("sprachsteuerung_regeln", "Anzahl der geladenen Satzmuster; 0 = die Satzdatei fehlt (retained)", "Number of loaded sentence patterns; 0 = the sentence file is missing (retained)"),
    ("sprachsteuerung_ziele", "Anzahl der eingetragenen Ziele (Geräte, die man per Sprache schalten kann; retained)",
     "Number of configured targets (devices that can be switched by voice; retained)"),
    ("sprachsteuerung_ruhe", "1 = es wird gerade nichts angesagt (Ruhezeit im Plugin oder von Loxone stillgelegt); jede Minute; Fassung 2: Haken und „Noncached“",
     "1 = nothing is announced at the moment (quiet hours in the plugin or muted by Loxone); every minute; version 2: tick and “Noncached”"),
    ("sprachsteuerung_letzter_satz_alter", "Sekunden seit dem letzten verstandenen Satz, Stand des letzten Herzschlags; -1 = noch keiner; Fassung 2: Haken und „Noncached“",
     "Seconds since the last understood sentence, as of the last heartbeat; -1 = none yet; version 2: tick and “Noncached”"),
    ("sprachsteuerung_status_zaehler", "Lebenszeichen: zählt mit jedem Herzschlag eins weiter (jede Minute), 0 bis 999, läuft um (nie retained); kommt nur mit „MQTT“ und Herzschlag an (Plugin Reiter MQTT, ab Werk an)",
     "Sign of life: counts up by one with every heartbeat (every minute), 0 to 999, wraps around (never retained); only arrives with “MQTT” and heartbeat (plugin tab MQTT, on by default)"),
    ("sprachsteuerung_dienste_gesamt", "Anzahl der geprüften Sprachdienste (der Nenner zu Nr. 4; ein abgeschaltetes Sprachmodell zählt nicht mit; retained)",
     "Number of checked voice services (the denominator of no. 4; a switched-off language model does not count; retained)"),
]
for _i, (_n, _de, _en) in enumerate(_Z1, 1):
    T[("BAUSTEIN", "Z1_%02d" % _i)] = ("%s | %s | %s | —" % (_GW, _n, _de), "%s | %s | %s | —" % (_GW_EN, _n, _en))
s("BAUSTEIN",
  Z1_11=("Konstante | Konstante 1 | Wert 1 | —", "Constant | Konstante 1 | value 1 | —"),
  Z1_12=("Analogwertvalidierung | Lebenszeichen fehlt (Sprachsteuerung) | Tmc 180 s (drei Herzschläge ohne neues Lebenszeichen; auch ein hängender Dienst sendet keins), Min 0, Max 999; Haken bei ‚En‘ im Eigenschaftsfenster entfernen | V = #9, En = #11",
         "Value Validator | Lebenszeichen fehlt (Sprachsteuerung) | Tmc 180 s (three heartbeats without a new sign of life; a hanging service sends none either), Min 0, Max 999; remove the tick at ‘En’ in the properties window | V = #9, En = #11"),
  Z1_13=("NICHT | Keine frischen Daten (Sprachsteuerung) | — (Sprachdienst angehalten) | I = #1",
         "NOT | Keine frischen Daten (Sprachsteuerung) | — (voice service stopped) | I = #1"),
  Z1_14=("Formel | Sprachdienste ausgefallen (Sprachsteuerung) | I1-I2 (geprüfte minus erreichbare Sprachdienste; 0 = alle antworten) | I1 = #10, I2 = #4",
         "Formula | Sprachdienste ausgefallen (Sprachsteuerung) | I1-I2 (checked minus reachable voice services; 0 = all answer) | I1 = #10, I2 = #4"),
  Z1_15=("Schwellwertschalter | Sprachdienst fehlt (Sprachsteuerung) | Ein 0,5 / Aus 0,25 (ab einem ausgefallenen Dienst ein; Zahlenwert, kein 0/1-Feld) | Eingang = #14",
         "Threshold Switch | Sprachdienst fehlt (Sprachsteuerung) | On 0.5 / Off 0.25 (on from one failed service; a number, not a 0/1 field) | Input = #14"),
  Z1_16=("ODER | Dienst gestoppt oder Sprachdienst fehlt (Sprachsteuerung) | — (linieneigener Zwischenschritt; die 600 s danach schlucken den Impuls des Schwellwertschalters) | I1 = #13, I2 = #15",
         "OR | Dienst gestoppt oder Sprachdienst fehlt (Sprachsteuerung) | — (intermediate step of this line; the 600 s after it swallow the pulse of the threshold switch) | I1 = #13, I2 = #15"),
  Z1_17=("ODER | Störung (Sprachsteuerung) | — (Dienst angehalten, Sprachdienst fehlt oder Lebenszeichen fehlt) | I1 = #16, I2 = Ausgang E von #12",
         "OR | Störung (Sprachsteuerung) | — (service stopped, voice service missing or sign of life missing) | I1 = #16, I2 = output E of #12"),
  Z1_18=("Einschaltverzögerung | Störung bestätigt (Sprachsteuerung) | 600 s (zehn Herzschläge; ein Neustart, ein Update und ein verspäteter Herzschlag melden nichts) | Eingang = #17",
         "On-Delay | Störung bestätigt (Sprachsteuerung) | 600 s (ten heartbeats; a restart, an update and a late heartbeat report nothing) | Input = #17"),
  Z1_19=("Benachrichtigung | Meldung Plugin gestört (Sprachsteuerung) | Text: Sprachsteuerung – seit 10 Minuten läuft der Sprachdienst nicht, Whisper, Piper oder das Sprachmodell antworten nicht, oder vom Plugin kommt kein Lebenszeichen. Sprachbefehle und Ansagen gehen dann nicht. In der App den Status „Zustand (Sprachsteuerung)“ lesen | Eingang = #18",
         "Notification | Meldung Plugin gestört (Sprachsteuerung) | Text: Sprachsteuerung – seit 10 Minuten läuft der Sprachdienst nicht, Whisper, Piper oder das Sprachmodell antworten nicht, oder vom Plugin kommt kein Lebenszeichen. Sprachbefehle und Ansagen gehen dann nicht. In der App den Status „Zustand (Sprachsteuerung)“ lesen (for 10 minutes the voice service has not been running, a voice service does not answer or no sign of life comes from the plugin) | Input = #18"),
  Z1_20=("Status | Zustand (Sprachsteuerung) | Zeilen: V2 = 0 „Sprachdienst gestoppt – im Plugin Reiter Einstellungen ‚Dienst starten‘“; V1 = 1 „Lebenszeichen fehlt seit mindestens 3 Minuten – LoxBerry oder Plugin antwortet nicht; LoxBerry im Browser öffnen, im Plugin Reiter MQTT ‚MQTT‘ und ‚Herzschlag‘ prüfen, unter MQTT-Gateway Fassung 2 die Haken“; V3 = 0 „keine Satzmuster geladen – im Plugin Reiter Sätze eine Sicherung einspielen oder Muster eintragen“; V7 = 0 „kein Sprachdienst erreichbar – im Plugin Reiter Dienste die Container starten“; V8 > 0 „<v8> Sprachdienst(e) antworten nicht – im Plugin Reiter Dienste nachsehen“; V4 = 0 „läuft – kein Mikrofon eingetragen; Sätze kommen nur über Loxone und den Reiter Test (im Plugin Reiter Mikrofone eines hinzufügen)“; V6 > 0 „<v6> von <v4> Mikrofonen getrennt – Strom und WLAN prüfen, im Plugin Reiter Mikrofone nachsehen“; ohne Bedingung „läuft – <v5> von <v4> Mikrofonen verbunden, <v7> Sprachdienste erreichbar“; Visualisierung EIN | V1 = Ausgang E von #12, V2 = #1, V3 = #5, V4 = #2, V5 = #3, V6 = #21, V7 = #4, V8 = #14",
         "Status | Zustand (Sprachsteuerung) | Rows: V2 = 0 “Sprachdienst gestoppt – im Plugin Reiter Einstellungen ‚Dienst starten‘” (service stopped); V1 = 1 “Lebenszeichen fehlt seit mindestens 3 Minuten – LoxBerry oder Plugin antwortet nicht; LoxBerry im Browser öffnen, im Plugin Reiter MQTT ‚MQTT‘ und ‚Herzschlag‘ prüfen, unter MQTT-Gateway Fassung 2 die Haken” (sign of life missing); V3 = 0 “keine Satzmuster geladen – im Plugin Reiter Sätze eine Sicherung einspielen oder Muster eintragen” (no patterns); V7 = 0 “kein Sprachdienst erreichbar – im Plugin Reiter Dienste die Container starten” (no voice service); V8 > 0 “<v8> Sprachdienst(e) antworten nicht – im Plugin Reiter Dienste nachsehen” (services not answering); V4 = 0 “läuft – kein Mikrofon eingetragen; Sätze kommen nur über Loxone und den Reiter Test (im Plugin Reiter Mikrofone eines hinzufügen)” (no microphone); V6 > 0 “<v6> von <v4> Mikrofonen getrennt – Strom und WLAN prüfen, im Plugin Reiter Mikrofone nachsehen” (microphones disconnected); without condition “läuft – <v5> von <v4> Mikrofonen verbunden, <v7> Sprachdienste erreichbar” (running); visualisation ON | V1 = output E of #12, V2 = #1, V3 = #5, V4 = #2, V5 = #3, V6 = #21, V7 = #4, V8 = #14"),
  Z1_21=("Formel | Mikrofone getrennt (Sprachsteuerung) | I1-I2 (eingetragene minus verbundene Mikrofone) | I1 = #2, I2 = #3",
         "Formula | Mikrofone getrennt (Sprachsteuerung) | I1-I2 (configured minus connected microphones) | I1 = #2, I2 = #3"),
  Z1_22=("Schwellwertschalter | Mikrofon getrennt (Sprachsteuerung) | Ein 0,5 / Aus 0,25 (ab einem getrennten Mikrofon ein) | Eingang = #21",
         "Threshold Switch | Mikrofon getrennt (Sprachsteuerung) | On 0.5 / Off 0.25 (on from one disconnected microphone) | Input = #21"),
  Z1_23=("Einschaltverzögerung | Mikrofon seit einer Stunde getrennt (Sprachsteuerung) | 3600 s (ein Mikrofon, das nach Stromausfall oder WLAN-Wechsel neu startet, meldet nichts) | Eingang = #22",
         "On-Delay | Mikrofon seit einer Stunde getrennt (Sprachsteuerung) | 3600 s (a microphone restarting after a power cut or WLAN change reports nothing) | Input = #22"),
  Z1_24=("Benachrichtigung | Meldung Mikrofon getrennt (Sprachsteuerung) | Text: Sprachsteuerung – ein Mikrofon ist seit einer Stunde nicht verbunden; in diesem Raum hört niemand zu. Strom und WLAN des Geräts prüfen, im Plugin Reiter Mikrofone nachsehen; in der App den Status „Zustand (Sprachsteuerung)“ lesen | Eingang = #23",
         "Notification | Meldung Mikrofon getrennt (Sprachsteuerung) | Text: Sprachsteuerung – ein Mikrofon ist seit einer Stunde nicht verbunden; in diesem Raum hört niemand zu. Strom und WLAN des Geräts prüfen, im Plugin Reiter Mikrofone nachsehen; in der App den Status „Zustand (Sprachsteuerung)“ lesen (a microphone has been disconnected for an hour) | Input = #23"),
  Z1_25=("Status | Sprachbetrieb (Sprachsteuerung) | Zeilen: V4 = 1 „kein Lebenszeichen seit 3 Minuten – hängt der Dienst? Im Plugin Reiter Einstellungen ‚Dienst neu starten‘“; V3 = 0 „keine Ziele eingetragen – im Plugin Reiter Sätze Ziele eintragen oder ‚Ziele aus Loxone übernehmen‘“; V1 < 0 „noch kein Satz verstanden – <v3> Ziele eingetragen; im Plugin Reiter Test einen Satz durchschicken“; V2 = 1 „Ansagen still (Ruhezeit oder von Loxone stillgelegt) – letzter verstandener Satz vor etwa <v1> s“; ohne Bedingung „letzter verstandener Satz vor etwa <v1> s – <v3> Ziele, Ansagen frei“; Visualisierung EIN | V1 = #8, V2 = #7, V3 = #6, V4 = Ausgang E von #12",
         "Status | Sprachbetrieb (Sprachsteuerung) | Rows: V4 = 1 “kein Lebenszeichen seit 3 Minuten – hängt der Dienst? Im Plugin Reiter Einstellungen ‚Dienst neu starten‘” (no sign of life); V3 = 0 “keine Ziele eingetragen – im Plugin Reiter Sätze Ziele eintragen oder ‚Ziele aus Loxone übernehmen‘” (no targets); V1 < 0 “noch kein Satz verstanden – <v3> Ziele eingetragen; im Plugin Reiter Test einen Satz durchschicken” (no sentence yet); V2 = 1 “Ansagen still (Ruhezeit oder von Loxone stillgelegt) – letzter verstandener Satz vor etwa <v1> s” (announcements muted); without condition “letzter verstandener Satz vor etwa <v1> s – <v3> Ziele, Ansagen frei” (last sentence); visualisation ON | V1 = #8, V2 = #7, V3 = #6, V4 = output E of #12"),
  # Seite "Sprachsteuerung Befehle": geaendert #1, #2, #7, #8, #12
  Z2_01=("Virtueller Texteingang | sprachsteuerung_wohnzimmer_licht_aktion | von Hand anlegen, Name genau so (Name, den das MQTT-Gateway vergibt); was der letzte Satz für das Ziel „Licht im Wohnzimmer“ wollte: ein, aus oder wert (dimmen); 2 Sekunden später setzt das Plugin ihn auf „-“ zurück – so wirkt auch derselbe Befehl zweimal hintereinander; MQTT-Gateway Fassung 2: Haken (kein „Noncached“ nötig) | —",
         "Virtual Text Input | sprachsteuerung_wohnzimmer_licht_aktion | create by hand, name exactly like this (the name the MQTT gateway assigns); what the last sentence wanted for the target “Licht im Wohnzimmer”: ein, aus or wert (dim); 2 seconds later the plugin resets it to “-” – so the same command also works twice in a row; MQTT gateway version 2: tick (no “Noncached” needed) | —"),
  Z2_02=(_GW + " | sprachsteuerung_wohnzimmer_licht_wert | Analog ein; Anzeigename „Helligkeit per Sprache (Sprachsteuerung)“; die genannte Zahl in %% (0–100), nur wenn der Satz eine nennt („dimme das wohnzimmer auf 40“); Ausgang an den Helligkeitseingang des eigenen Dimmers (nicht Teil der Liste) | —",
         _GW_EN + " | sprachsteuerung_wohnzimmer_licht_wert | Analog on; display name “Helligkeit per Sprache (Sprachsteuerung)”; the number given in %% (0–100), only if the sentence names one (“dimme das wohnzimmer auf 40”); output to the brightness input of your own dimmer (not part of the list) | —"),
  Z2_07=(_GW + " | sprachsteuerung_wohnzimmer_heizung_wert | Analog ein; Anzeigename „Solltemperatur per Sprache (Sprachsteuerung)“; genannte Temperatur in °C (das Ziel erlaubt 5–30), nur wenn der Satz eine nennt („stelle die heizung auf 21 grad“); Ausgang an den eigenen Sollwert, z. B. einen Analogspeicher vor dem Raumregler (nicht Teil der Liste) | —",
         _GW_EN + " | sprachsteuerung_wohnzimmer_heizung_wert | Analog on; display name “Solltemperatur per Sprache (Sprachsteuerung)”; temperature given in °C (the target allows 5–30), only if the sentence names one (“stelle die heizung auf 21 grad”); output to your own setpoint, e.g. an analogue memory in front of the room controller (not part of the list) | —"),
  Z2_08=(_GW + " | sprachsteuerung_ok | Analog ein; Anzeigename „Satz ausgeführt (Sprachsteuerung)“; 1 = verstanden und ausgeführt, 0 = nicht (gilt für gesprochene Sätze und für „Sprachsteuerung: Satz schicken“) | —",
         _GW_EN + " | sprachsteuerung_ok | Analog on; display name “Satz ausgeführt (Sprachsteuerung)”; 1 = understood and carried out, 0 = not (applies to spoken sentences and to “Sprachsteuerung: Satz schicken”) | —"),
  Z2_12=("Virtueller Texteingang | sprachsteuerung_mikrofon | Titel genau so; welches Mikrofon zugehört hat – damit weiß Loxone, aus welchem Raum der Befehl kam; „-“ ohne Mikrofon (Satz aus Loxone über MQTT oder aus dem Reiter Test) | —",
         "Virtual Text Input | sprachsteuerung_mikrofon | title exactly like this; which microphone listened – so Loxone knows from which room the command came; “-” without microphone (sentence from Loxone via MQTT or from the Test tab) | —"),
  # Seite "Sprachsteuerung Ansagen": geaendert #1, #3, #8, #10, #12, #18, #19, #22
  Z3_01=(_GW + " | sprachsteuerung_ruhe | 1 = es wird gerade nichts angesagt (weitere Instanz, derselbe Eingang wie auf Seite „Sprachsteuerung“) | —",
         _GW_EN + " | sprachsteuerung_ruhe | 1 = nothing is announced at the moment (further instance, the same input as on page “Sprachsteuerung”) | —"),
  Z3_03=(_VQ + " | Sprachsteuerung: Ansage Türklingel | Befehl bei EIN: publish %1$s/befehl/sprechen Es hat an der Haustuer geklingelt (nie retain; Text ohne Umlaute); in der Ruhezeit still; derselbe Text binnen 10 s wird nur einmal gesprochen; wie und wo gesprochen wird, stellt man im Plugin ein (gemeinsames Sprachmodul, Reiter Einstellungen) – Loxone löst nur aus; wirkt nur mit den Haken „Befehle über MQTT annehmen“ und „Ansagen und Sätze über MQTT zulassen“ (Plugin Reiter MQTT) | Eingang = #2",
         _VQ_EN + " | Sprachsteuerung: Ansage Türklingel | Command on ON: publish %1$s/befehl/sprechen Es hat an der Haustuer geklingelt (never retain; text without umlauts); silent during quiet hours; the same text within 10 s is spoken only once; how and where it is spoken is set in the plugin (shared voice module, Settings tab) – Loxone only triggers; works only with the ticks “Accept commands via MQTT” and “Allow announcements and sentences via MQTT” (plugin tab MQTT) | Input = #2"),
  Z3_08=(_VQ + " | Sprachsteuerung: Ansage | Befehl bei EIN: publish %1$s/befehl/sprechen Das Garagentor steht seit einer Stunde offen (eigenen Text hinter „sprechen “ eintragen, höchstens 400 Zeichen; nur in einer Zone oder an einem Lautsprecher: publish %1$s/befehl/sprechen {%2$stext%2$s:%2$s…%2$s,%2$szone%2$s:%2$s2%2$s} bzw. {%2$stext%2$s:%2$s…%2$s,%2$smikrofon%2$s:%2$sKueche%2$s}); Haken wie Nr. 3 | Eingang = #7",
         _VQ_EN + " | Sprachsteuerung: Ansage | Command on ON: publish %1$s/befehl/sprechen Das Garagentor steht seit einer Stunde offen (enter your own text after “sprechen ”, at most 400 characters; only in one zone or on one speaker: publish %1$s/befehl/sprechen {%2$stext%2$s:%2$s…%2$s,%2$szone%2$s:%2$s2%2$s} or {%2$stext%2$s:%2$s…%2$s,%2$smikrofon%2$s:%2$sKueche%2$s}); ticks as no. 3 | Input = #7"),
  Z3_10=(_VQ + " | Sprachsteuerung: Alarmansage | Befehl bei EIN: publish %1$s/befehl/alarm Wasseralarm im Keller (nie retain); spricht dringend – auch in der Ruhezeit und wenn Loxone stillgelegt hat; Haken wie Nr. 3 | Eingang = #9",
         _VQ_EN + " | Sprachsteuerung: Alarmansage | Command on ON: publish %1$s/befehl/alarm Wasseralarm im Keller (never retain); speaks urgently – also during quiet hours and when Loxone has muted; ticks as no. 3 | Input = #9"),
  Z3_12=(_VQ + " | Sprachsteuerung: Satz schicken | Befehl bei EIN: publish %1$s/befehl/satz schalte das licht im wohnzimmer aus (eigenen Satz eintragen, wie man ihn sprechen würde); jeder Druck zählt; Haken wie Nr. 3 | Eingang = #11",
         _VQ_EN + " | Sprachsteuerung: Satz schicken | Command on ON: publish %1$s/befehl/satz schalte das licht im wohnzimmer aus (enter your own sentence as you would speak it); every press counts; ticks as no. 3 | Input = #11"),
  Z3_18=(_VQ + " | Sprachsteuerung: Ansagen stilllegen | Befehl bei EIN: publish %1$s/befehl/ruhe 1; Befehl bei AUS: publish %1$s/befehl/ruhe 0 (nie retain). Gilt auch für Ansagen, die andere Plugins über die Sprachsteuerung sprechen lassen (z. B. Intercom beim Klingeln); die Ruhezeit im Plugin dann ausgeschaltet lassen; wirkt mit dem Haken „Befehle über MQTT annehmen“ allein | Eingang = #17",
         _VQ_EN + " | Sprachsteuerung: Ansagen stilllegen | Command on ON: publish %1$s/befehl/ruhe 1; command on OFF: publish %1$s/befehl/ruhe 0 (never retain). Also applies to announcements other plugins make via the voice control (e.g. Intercom when the bell rings); then leave the quiet hours in the plugin switched off; works with the tick “Accept commands via MQTT” alone | Input = #17"),
  Z3_19=(_GW + " | sprachsteuerung_ansage_ok | Analog ein; Anzeigename „Letzte Ansage angekommen (Sprachsteuerung)“; 1 = angekommen, 0 = nicht, -1 = gesendet, Ausgang unklar; kommt nur mit „Dauerhafte Verbindung zum Broker“ (Plugin Reiter MQTT, ab Werk aus) – ohne sie bleibt 0 stehen; nur Anzeige, keine Meldung daran | —",
         _GW_EN + " | sprachsteuerung_ansage_ok | Analog on; display name “Letzte Ansage angekommen (Sprachsteuerung)”; 1 = arrived, 0 = not, -1 = sent, outcome unclear; only comes with “Permanent connection to the broker” (plugin tab MQTT, off by default) – without it 0 stays; display only, no message on it | —"),
  Z3_22=("Status | Ansagen (Sprachsteuerung) | Zeilen: V2 = 1 und V1 = 1 „still – von Loxone stillgelegt (Nachtruhe, Schalter oder niemand zu Hause); Alarmansagen kommen trotzdem“; V2 = 1 „Loxone legt still – das Plugin bestätigt es mit dem nächsten Herzschlag (höchstens eine Minute); bleibt es so, Haken ‚Befehle über MQTT annehmen‘ und Status ‚Zustand (Sprachsteuerung)‘ prüfen“; V1 = 1 „still – Ruhezeit im Plugin (Reiter Einstellungen); Alarmansagen kommen trotzdem“; V3 = -1 „bereit – letzte Ansage gesendet, ob sie ankam, ist unklar“; V3 = 0 und V4 != „“ und V4 != „-“ „bereit – letzte Ansage kam nicht an: <v4>; im Plugin Reiter Einstellungen die Ausgabe prüfen“; V3 = 1 „bereit – letzte Ansage ist angekommen“; ohne Bedingung „bereit (ob eine Ansage ankam, meldet das Plugin nur mit dauerhafter Broker-Verbindung, Reiter MQTT)“; Visualisierung EIN | V1 = #1, V2 = #17, V3 = #19, V4 = #20",
         "Status | Ansagen (Sprachsteuerung) | Rows: V2 = 1 and V1 = 1 “still – von Loxone stillgelegt (Nachtruhe, Schalter oder niemand zu Hause); Alarmansagen kommen trotzdem” (muted by Loxone; alarms still come); V2 = 1 “Loxone legt still – das Plugin bestätigt es mit dem nächsten Herzschlag (höchstens eine Minute); bleibt es so, Haken ‚Befehle über MQTT annehmen‘ und Status ‚Zustand (Sprachsteuerung)‘ prüfen” (Loxone mutes – the plugin confirms it with the next heartbeat); V1 = 1 “still – Ruhezeit im Plugin (Reiter Einstellungen); Alarmansagen kommen trotzdem” (quiet hours in the plugin); V3 = -1 “bereit – letzte Ansage gesendet, ob sie ankam, ist unklar” (sent, outcome unclear); V3 = 0 and V4 != “” and V4 != “-” “bereit – letzte Ansage kam nicht an: <v4>; im Plugin Reiter Einstellungen die Ausgabe prüfen” (did not arrive); V3 = 1 “bereit – letzte Ansage ist angekommen” (arrived); without condition “bereit (ob eine Ansage ankam, meldet das Plugin nur mit dauerhafter Broker-Verbindung, Reiter MQTT)” (ready); visualisation ON | V1 = #1, V2 = #17, V3 = #19, V4 = #20"),
  # Kaesten und Hinweise der Seiten 1 und 3 (Seite 2 bleibt bis auf Schritt 1)
  SEITE1_SCHRITT1=("Im Plugin Reiter „Einstellungen“ den Dienst starten, im Reiter „Dienste“ Whisper und Piper starten, im Reiter „Mikrofone“ die Mikrofone eintragen. Im Reiter „MQTT“ „MQTT“ und den Herzschlag (60 s) an lassen (ab Werk an). Probe: im Reiter „Test“ ist die Selbstprüfung grün.",
                   "In the plugin, start the service on the “Settings” tab, start Whisper and Piper on the “Services” tab, enter the microphones on the “Microphones” tab. On the “MQTT” tab leave “MQTT” and the heartbeat (60 s) on (on by default). Check: the self-test on the “Test” tab is green."),
  SEITE1_SCHRITT2=("Beim MQTT-Gateway Fassung 2 die zehn Themen der Nr. 1–10 in den Subscriptions anhaken, bei online, bereit, dienste_ok, ruhe und letzter_satz_alter zusätzlich „Noncached“ (Namenstabelle oben). Fassung 1 liest die Abo-Datei, die das Plugin selbst anlegt.",
                   "With MQTT gateway version 2 tick the ten topics of nos. 1–10 in the subscriptions, for online, bereit, dienste_ok, ruhe and letzter_satz_alter additionally “Noncached” (name table above). Version 1 reads the subscription file the plugin writes itself."),
  SEITE1_SCHRITT3=("Seite „Sprachsteuerung“ anlegen. Die zehn Eingänge Nr. 1–10 VON HAND anlegen (Virtuelle Eingänge anwählen → Virtueller Eingang), Name GENAU wie in der Tabelle – so heißen sie beim Gateway; „Als Digitaleingang“ nicht anhaken. Dazu die Konstante „Konstante 1“ (Nr. 11, Wert 1; im Musterprojekt schon vorhanden).",
                   "Create the page “Sprachsteuerung”. Create the ten inputs nos. 1–10 BY HAND (select Virtual Inputs → Virtual Input), name EXACTLY as in the table – that is what they are called at the gateway; do not tick “Use as digital input”. Add the constant “Konstante 1” (no. 11, value 1; already present in the sample project)."),
  SEITE1_SCHRITT4=("Zwei Benachrichtigungen anlegen (Peripherie → Mitteilungen → Benachrichtigung): „Meldung Plugin gestört (Sprachsteuerung)“ und „Meldung Mikrofon getrennt (Sprachsteuerung)“, Text aus der Tabelle, auf die Seite ziehen.",
                   "Create two notifications (Periphery → Messages → Notification): “Meldung Plugin gestört (Sprachsteuerung)” and “Meldung Mikrofon getrennt (Sprachsteuerung)”, text from the table, drag them onto the page."),
  SEITE1_SCHRITT5=("Übrige Bausteine über die Baustein-Suche (F5) setzen, Parameter wie in der Tabelle, von oben nach unten verbinden; ODER haben je zwei Eingänge. Analogwertvalidierung Nr. 12: Haken bei ‚En‘ im Eigenschaftsfenster entfernen (Config legt En negiert an; sonst kommt die Konstante 1 als 0 an, und die Ausfallmeldung löst nie aus). Status Nr. 20: vorher viermal „+“ (V5–V8). Statuszeilen und Mitteilungstexte stehen in der Tabelle und werden von Hand eingetragen, die Zeile ohne Bedingung zuletzt.",
                   "Place the remaining blocks via the block search (F5), parameters as in the table, wire from top to bottom; ORs have two inputs each. Value validator no. 12: remove the tick at ‘En’ in the properties window (Config creates En negated; otherwise the constant 1 arrives as 0 and the failure message never triggers). Status no. 20: press “+” four times first (V5–V8). Status rows and message texts are in the table and entered by hand, the row without condition last."),
  SEITE1_SCHRITT6=("Speichern und in den Miniserver übertragen. Probe: „Zustand (Sprachsteuerung)“ zeigt „läuft – … Mikrofonen verbunden“, und sprachsteuerung_status_zaehler zählt jede Minute eins weiter. Gegenprobe: im Plugin den Dienst anhalten – „Zustand“ zeigt „Sprachdienst gestoppt“, nach 10 Minuten kommt „Meldung Plugin gestört (Sprachsteuerung)“.",
                   "Save and transfer to the Miniserver. Check: “Zustand (Sprachsteuerung)” shows “läuft – … Mikrofonen verbunden”, and sprachsteuerung_status_zaehler counts up by one every minute. Cross-check: stop the service in the plugin – “Zustand” shows “Sprachdienst gestoppt”, after 10 minutes “Meldung Plugin gestört (Sprachsteuerung)” arrives."),
  SEITE1_H1=("<b>Zu Nr. 12:</b> hängt der Dienst oder steht der LoxBerry, kommt kein Herzschlag mehr – die übrigen Eingänge behalten ihren letzten Wert, nur das Lebenszeichen bleibt stehen. Kommt innerhalb Tmc (180 s) kein neuer Wert, meldet die Analogwertvalidierung an ihrem Ausgang E. sprachsteuerung_status_zaehler an V, die Konstante 1 an En – und den Haken bei ‚En‘ im Eigenschaftsfenster entfernen.",
             "<b>On no. 12:</b> if the service hangs or the LoxBerry stops, no heartbeat arrives – the other inputs keep their last value, only the sign of life stands still. If no new value arrives within Tmc (180 s), the value validator reports at its output E. sprachsteuerung_status_zaehler to V, the constant 1 to En – and remove the tick at ‘En’ in the properties window."),
  SEITE1_H2=("<b>Zu Nr. 13 bis 19:</b> „Dienst gestoppt“, „Sprachdienst fehlt“ und „Lebenszeichen fehlt“ laufen über zwei ODER in eine Benachrichtigung – ein Benachrichtigungsbaustein bekommt nur eine Quelle. Die Meldung kommt erst nach 10 Minuten Störung (ein Neustart oder ein Update bleibt still); „LoxBerry aus“ frühestens nach 13 Minuten (3 Minuten Lebenszeichen und 10 Minuten).",
             "<b>On nos. 13 to 19:</b> “service stopped”, “voice service missing” and “sign of life missing” run through two ORs into one notification – a notification block only gets one source. The message only comes after 10 minutes of fault (a restart or an update stays silent); “LoxBerry off” after 13 minutes at the earliest (3 minutes sign of life and 10 minutes)."),
  SEITE1_H3=("<b>Zu Nr. 15 und 22:</b> ein Schwellwertschalter hinter einem Eingang, der jede Minute neu kommt, gibt kurze Impulse; die Einschaltverzögerung dahinter (Nr. 18 bzw. 23) schluckt sie.",
             "<b>On nos. 15 and 22:</b> a threshold switch behind an input that arrives anew every minute gives short pulses; the on-delay behind it (no. 18 or 23) swallows them."),
  SEITE1_H4=("<b>Zu Nr. 1, 3, 4, 7 und 8:</b> diese Werte kommen jede Minute, oft mit gleichem Wert; beim Gateway Fassung 2 deshalb „Noncached“ setzen – sonst bleibt ein Eingang nach einem Neustart des Miniservers auf 0 stehen (etwa „Sprachdienst gestoppt“). Die übrigen sind zurückbehalten oder ändern sich immer.",
             "<b>On nos. 1, 3, 4, 7 and 8:</b> these values arrive every minute, often with the same value; with gateway version 2 therefore set “Noncached” – otherwise an input stays at 0 after a Miniserver restart (e.g. “service stopped”). The others are retained or always change."),
  SEITE1_H5=("Ein anderes Präfix im Reiter MQTT ergibt andere Namen – dann alle Eingänge neu benennen. Der LoxBerry-Benutzer im Miniserver braucht das Recht, virtuelle Eingänge zu beschreiben.",
             "Another prefix on the MQTT tab gives other names – then rename all inputs. The LoxBerry user in the Miniserver needs the right to write virtual inputs."),
  SEITE1_H6=("Bis 0.12.6 holte ein Virtueller HTTP-Eingang „Sprachsteuerung lokal“ diese Werte mit dem Token; der Weg steht unten unter „Bestehende Anlagen“ und braucht seit 0.12.7 den Haken „HTTP-Endpunkt für Loxone annehmen“. ALTER gibt es über MQTT nicht – das Lebenszeichen deckt den hängenden Dienst mit ab.",
             "Up to 0.12.6 a Virtual HTTP Input “Sprachsteuerung lokal” fetched these values with the token; that path is below under “Existing setups” and since 0.12.7 needs the tick “Accept the HTTP endpoint for Loxone”. ALTER does not exist via MQTT – the sign of life also covers a hanging service."),
  SEITE2_SCHRITT1=("Im Plugin Reiter „MQTT“ prüfen: das Gateway steht auf Autostart; bei Gateway Fassung 2 die Datenpunkte der Namenstabelle (Schritt 2) anhaken. Im Reiter „Sätze“ haben die Ziele ein Thema (Werksziel „Licht im Wohnzimmer“ = wohnzimmer/licht).",
                   "Check on the plugin's “MQTT” tab: the gateway is on autostart; with gateway version 2 tick the data points of the name table (step 2). On the “Sentences” tab the targets have a topic (factory target “Licht im Wohnzimmer” = wohnzimmer/licht)."),
  SEITE3_SCHRITT2=("In Schritt 4 dieses Reiters Knopf „Vorlage: MQTT-Befehle“. In Loxone Config: Virtuelle Ausgänge anwählen → Vordefinierte Geräte → Vorlage importieren (nur einmal). Der Behälter „Sprachsteuerung Befehle (MQTT)“ trägt fünf Befehle an den UDP-Eingang des MQTT-Gateways. Im Musterprojekt stehen sie am gemeinsamen Ausgang „LoxBerry MQTT-Gateway“ – dort die fünf Befehle mit Titel und Befehl aus der Tabelle anlegen.",
                   "In step 4 of this tab, button “Template: MQTT commands”. In Loxone Config: select Virtual Outputs → Predefined devices → import template (only once). The container “Sprachsteuerung Befehle (MQTT)” carries five commands to the UDP input of the MQTT gateway. In the sample project they are on the shared output “LoxBerry MQTT-Gateway” – create the five commands with title and command from the table there."),
  SEITE3_SCHRITT3=("Seite „Sprachsteuerung Ansagen“ anlegen. Die fünf Befehle, sprachsteuerung_ruhe (weitere Instanz), „Türklingel (eigene Quelle)“ und „Niemand zu Hause (eigene Quelle)“ ziehen (im Musterprojekt schon vorhanden); die Platzhalter „Garagentor offen (eigene Quelle)“ und „Wassermelder (eigene Quelle)“, die zwei Tasten und den Schalter „Ansagen stilllegen (Sprachsteuerung)“ anlegen; die Eingänge Nr. 19, 20 und 21 von Hand anlegen, Name genau so.",
                   "Create the page “Sprachsteuerung Ansagen”. Drag the five commands, sprachsteuerung_ruhe (further instance), “Türklingel (eigene Quelle)” and “Niemand zu Hause (eigene Quelle)” (already present in the sample project); create the placeholders “Garagentor offen (eigene Quelle)” and “Wassermelder (eigene Quelle)”, the two buttons and the switch “Ansagen stilllegen (Sprachsteuerung)”; create inputs nos. 19, 20 and 21 by hand, name exactly like this."),
  SEITE3_SCHRITT5=("Im Plugin Reiter „MQTT“ die Haken „Befehle über MQTT annehmen“ und „Ansagen und Sätze über MQTT zulassen“ setzen. Speichern und übertragen. Probe: „Taste Testansage (Sprachsteuerung)“ drücken – die Anlage sagt „Das Garagentor steht seit einer Stunde offen“. Schalter „Ansagen stilllegen (Sprachsteuerung)“ ein, Taste noch einmal: es bleibt still, und „Ansagen (Sprachsteuerung)“ zeigt „still – von Loxone stillgelegt“.",
                   "On the plugin's “MQTT” tab set the ticks “Accept commands via MQTT” and “Allow announcements and sentences via MQTT”. Save and transfer. Check: press “Taste Testansage (Sprachsteuerung)” – the system says “Das Garagentor steht seit einer Stunde offen”. Switch “Ansagen stilllegen (Sprachsteuerung)” on, press the button again: it stays silent, and “Ansagen (Sprachsteuerung)” shows “still – von Loxone stillgelegt”."),
  SEITE3_H1=("Den Text einer Ansage ändert man im Befehl hinter <span class='sm-mono'>sprechen </span> (Leerzeichen bleiben Leerzeichen); höchstens 400 Zeichen; vorerst ohne Umlaute (ae, oe, ue, ss), bis gemessen ist, wie Loxone sie über UDP sendet. Nur in einer Zone oder an einem Lautsprecher: JSON statt Text (Nr. 8).",
             "You change the text of an announcement in the command after <span class='sm-mono'>sprechen </span> (spaces stay spaces); at most 400 characters; for now without umlauts (ae, oe, ue, ss) until it has been measured how Loxone sends them via UDP. Only in one zone or on one speaker: JSON instead of text (no. 8)."),
  SEITE3_H2=("Eine Ansage geht nur, wenn der Sprachdienst läuft – sonst quittiert das Plugin „abgelehnt: DIENST_LAEUFT_NICHT“, sie wird nicht nachgeholt. Derselbe Text binnen 10 Sekunden wird nur einmal angenommen (Bremse der Befehlsbrücke); danach greift die Wiederholungsbremse des Plugins (Reiter Einstellungen).",
             "An announcement only works if the voice service is running – otherwise the plugin acknowledges “abgelehnt: DIENST_LAEUFT_NICHT”, it is not made up later. The same text within 10 seconds is accepted only once (command bridge brake); after that the plugin's repetition brake applies (Settings tab)."),
  SEITE3_H3=("<b>Zu Nr. 10:</b> „alarm“ übergeht jede Ruhe – auch nachts und stillgelegt; nur für echte Alarme benutzen.",
             "<b>On no. 10:</b> “alarm” overrides any quiet – also at night and when muted; only use it for real alarms."),
  SEITE3_H4=("<b>Zu Nr. 13 bis 18:</b> Loxone legt über den Befehl „Sprachsteuerung: Ansagen stilllegen“ still – das gilt auch für Ansagen, die andere Plugins über die Sprachsteuerung sprechen lassen. Die Stilllegung aus Loxone übersteht ein Plugin-Update (seit 0.12.6).",
             "<b>On nos. 13 to 18:</b> Loxone mutes via the command “Sprachsteuerung: Ansagen stilllegen” – this also applies to announcements other plugins make via the voice control. Muting from Loxone survives a plugin update (since 0.12.6)."),
  SEITE3_H8=("Jeder im Heimnetz kann über den UDP-Eingang des MQTT-Gateways Befehle senden – deshalb sind beide Haken ab Werk aus. Bis 0.12.6 gingen die Befehle über HTTP mit Token (Vorlage „Sprachsteuerung lokal - Befehle“); der Weg steht unten unter „Bestehende Anlagen“.",
             "Anyone on the home network can send commands via the UDP input of the MQTT gateway – that is why both ticks are off by default. Up to 0.12.6 the commands went via HTTP with token (template “Sprachsteuerung lokal - Befehle”); that path is below under “Existing setups”."),
)


# ---------------------------------------------------------------------------
# STAND (vb_g20_sp, 25.10.2026, Gruppe 20): Sprachsteuerung 0.12.8 - V3 Kalenderfragen (Abnehmer haus/kalender/*,
# Entwurf Musterprojekt/entwurf_gruppe20_sp.txt 2.5/2.6) und Pflegewelle 22 (Sprachmodul 1.1.4, SonoX).
# Neu [UI020] (Haken und Thementabelle im Reiter MQTT, Pruefzeile im Reiter Test) und [SONOX] (E-E5: statt [ANSAGE]
# genau die Modul-IDs, die ansage_pruefzeile() fuer sonos4lox/sonox ausgibt, dazu die SonoX-Formulartexte). Die
# [SONOX]-Werte liest dieser Erzeuger byte-gleich aus Werkzeuge/gemeinsam/sprachausgabe_texte.json (fehlt die Datei,
# bricht er ab, ohne zu schreiben). BAUSTEIN.Z2_14/Z3_16 wortgleich zu Musterprojekt/baustein_listen.txt (Nachzug
# 25.10., md5 29b291d3...). UI013.T_SONOS entfaellt (die Sonos4Lox-Zeile kommt jetzt aus dem Modul, E-E7).
# ---------------------------------------------------------------------------
import json as _json_g20
import os as _os_g20


def _sonox_texte_g20():
    kandidaten = [Path(__file__).resolve().parent / "gemeinsam" / "sprachausgabe_texte.json"]
    if _os_g20.environ.get("SP_TEXTE_JSON"):
        kandidaten.insert(0, Path(_os_g20.environ["SP_TEXTE_JSON"]))
    for k in kandidaten:
        if k.is_file():
            return _json_g20.loads(k.read_text(encoding="utf-8"))
    raise SystemExit("sprachausgabe_texte.json nicht gefunden (Werkzeuge/gemeinsam/ oder SP_TEXTE_JSON) - "
                     "es wurde NICHTS geschrieben.")


_SONOX_IDS_G20 = (
    # Pruefzeile sonos4lox (Sprachausgabe 1.1.4, ansage_pruefzeile())
    "T_SONOS", "T_SONOS_ZONE_OK", "T_SONOS_ZONEN", "T_SONOS_ZONE_VORSCHLAG",
    "K_SONOS_KEINE_ZONE", "K_SONOS_NICHT_INSTALLIERT", "K_SONOS_ZONE_UNBEKANNT",
    # Pruefzeile sonox (GET /zones; ansage_sonox_grund() mit Frist 0 und ansage_http_grund_id())
    "T_SONOX_OK", "T_SONOX_ZU", "T_SONOX_FEHL", "T_SONOX_RAEUME",
    "K_SONOX_KEIN_RAUM", "K_SONOX_FEHLT", "K_SONOX_RAUM_UNBEKANNT", "K_SONOX_KEINE_ANLAGE", "K_SONOX_FEHLER",
    "K_SONOX_UNERWARTET", "K_SONOX_DIENST_AUS",
    "K_HTTP_ZEIT", "K_HTTP_OHNE_ANTWORT", "K_HTTP_NETZ", "K_HTTP_NAME", "K_HTTP_ZUGANG", "K_HTTP_404",
    "K_HTTP_429", "K_HTTP_GEGENSEITE", "K_HTTP_STATUS", "K_HTTP_WEITERLEITUNG",
    # Formular (index.php) und Sicherungspruefung (sp_pruefen.php)
    "O_SONOX", "SONOX_HINWEIS", "L_SONOX_RAUM", "SONOX_RAUM_HINWEIS", "L_SONOX_LAUT", "SONOX_LAUT_HINWEIS",
    "L_SONOX_SPRACHE", "SONOX_SPRACHE_HINWEIS", "M_SONOX_RAUM", "M_SONOX_LAUT", "M_SONOX_SPRACHE", "M_SONOX_OHNE_RAUM",
)
_TX_G20 = _sonox_texte_g20()
for _id in _SONOX_IDS_G20:
    if _id not in _TX_G20.get("de", {}) or _id not in _TX_G20.get("en", {}):
        raise SystemExit("sprachausgabe_texte.json: %s fehlt in de oder en - es wurde NICHTS geschrieben." % _id)
    s("SONOX", **{_id: (_TX_G20["de"][_id], _TX_G20["en"][_id])})

N["UI013"].pop("T_SONOS", None)

s("UI020",
  L_KALENDER=("Kalenderfragen beantworten („Ist morgen schulfrei?“)", "Answer calendar questions (“Is there school tomorrow?”)"),
  H_KALENDER=("Ab Werk aus. Antwortet auf Fragen nach Schule, Ferien und Feiertagen („Ist morgen schulfrei?“, „Wann sind die nächsten Ferien?“, „Wie lange dauern die Ferien noch?“, „Wann ist der nächste Feiertag?“) aus den Zahlen, die das Plugin „Ferien und Feiertage“ unter haus/kalender/… veröffentlicht – dort im Reiter MQTT „Kalendertage an andere Plugins geben“ anhaken. Nie Namen, kein Urlaub. Öffnet eine eigene Verbindung zum Broker, die nur liest (ohne Letzten Willen, ohne online). Schweigt das Ferien-Plugin länger als zwei Minuten oder sind die Daten nicht von heute, lautet die Antwort „keine Kalenderdaten“.",
              "Off by default. Answers questions about school, school holidays and public holidays (“Is there school tomorrow?”, “When are the next school holidays?”, “How long do the holidays last?”, “When is the next public holiday?”) from the numbers the plugin “Ferien und Feiertage” publishes below haus/kalender/… – tick “Kalendertage an andere Plugins geben” on its MQTT tab. Never names, no vacation. Opens its own read-only connection to the broker (no last will, no online). If the holidays plugin is silent for more than two minutes or the data is not from today, the answer is “no calendar data”."),
  T_KALENDER_THEMEN=("(9 Themen: datum, heute/frei, heute/feiertag, morgen/frei, morgen/feiertag, ferien_in, ferien_rest, feiertag_in, zaehler)",
                     "(9 topics: datum, heute/frei, heute/feiertag, morgen/frei, morgen/feiertag, ferien_in, ferien_rest, feiertag_in, zaehler)"),
  B_KALENDER=("Kalenderzahlen des Ferien-Plugins, nur mit Kalenderfragen; nie ruhetag, nie urlaub",
              "Calendar numbers of the holidays plugin, only with calendar questions; never ruhetag, never urlaub"),
  F_KALENDER=("Kalenderfragen (haus/kalender)", "Calendar questions (haus/kalender)"),
  A_KALENDER_AUS=("aus (Reiter MQTT, „Kalenderfragen beantworten“)", "off (MQTT tab, “Answer calendar questions”)"),
  A_KALENDER_FRISCH=("frisch – Daten vom %s, Lebenszeichen vor %s s; heute schulfrei: %s, morgen: %s, Ferien in %s Tagen, Feiertag in %s Tagen",
                     "fresh – data from %s, sign of life %s s ago; no school today: %s, tomorrow: %s, school holidays in %s days, public holiday in %s days"),
  A_KALENDER_WARTET=("wartet auf das erste Lebenszeichen des Ferien-Plugins (höchstens 2 Minuten nach dem Start)",
                     "waiting for the first sign of life of the holidays plugin (at most 2 minutes after the start)"),
  A_KALENDER_SCHWEIGT=("das Ferien-Plugin schweigt seit %s s (haus/kalender/zaehler).",
                       "the holidays plugin has been silent for %s s (haus/kalender/zaehler)."),
  A_KALENDER_SCHWEIGT_NIE=("seit dem Verbinden kein Lebenszeichen des Ferien-Plugins (haus/kalender/zaehler).",
                           "no sign of life of the holidays plugin since connecting (haus/kalender/zaehler)."),
  A_KALENDER_VERALTET=("Daten nicht von heute (%s).", "data not from today (%s)."),
  A_KALENDER_GETRENNT=("Verbindung zum Broker steht nicht: %s.", "connection to the broker is down: %s."),
  A_KALENDER_HILFE=("Fragen werden mit „keine Kalenderdaten“ beantwortet. Im Plugin „Ferien und Feiertage“ Reiter MQTT „Kalendertage an andere Plugins geben“ prüfen.",
                    "Questions are answered with “no calendar data”. Check “Kalendertage an andere Plugins geben” on the MQTT tab of the plugin “Ferien und Feiertage”."),
  A_KALENDER_UNBEKANNT=("der laufende Dienst meldet noch keinen Kalenderstand (läuft er, und ist der Haken gespeichert?)",
                        "the running service reports no calendar state yet (is it running, and is the tick saved?)"),
)

s("BAUSTEIN",
  Z2_14=("Status | Letzter Sprachbefehl (Sprachsteuerung) | Zeilen: V3 := „kalender“ „Kalenderfrage (<v4>): <v5>“; V1 = 1 und V3 == „vorgemerkt“ „vorgemerkt (<v4>): <v2> – <v5>“; V1 = 1 „ausgeführt (<v4>): <v2> → <v6> – <v5>“; V3 == „kein_muster“ „nicht verstanden (<v4>): <v2> – im Plugin Reiter Sätze ein Satzmuster ergänzen“; V3 == „ziel_unbekannt“ „Gerät nicht gefunden (<v4>): <v2> – im Plugin Reiter Sätze am Ziel einen Alias ergänzen“; V3 == „ziel_fehlt“ „kein Gerät genannt (<v4>): <v2> – das Gerät nennen oder im Plugin Reiter Mikrofone dem Mikrofon einen Raum geben“; V3 := „llm_“ „Sprachmodell antwortet nicht oder falsch – im Plugin Reiter Dienste nachsehen“; V3 == „rueckfrage“ „Rückfrage: <v5>“; V3 == „“ „seit dem Neustart noch kein Satz“; ohne Bedingung „nicht ausgeführt (<v3>): <v2> – <v5>“; Visualisierung EIN | V1 = #8, V2 = #9, V3 = #10, V4 = #12, V5 = #11, V6 = #13",
         "Status | Letzter Sprachbefehl (Sprachsteuerung) | Rows: V3 := “kalender” “Kalenderfrage (<v4>): <v5>” (calendar question; := means begins with); V1 = 1 and V3 == “vorgemerkt” “vorgemerkt (<v4>): <v2> – <v5>” (scheduled); V1 = 1 “ausgeführt (<v4>): <v2> → <v6> – <v5>” (executed); V3 == “kein_muster” “nicht verstanden (<v4>): <v2> – im Plugin Reiter Sätze ein Satzmuster ergänzen” (not understood – add a sentence pattern in the plugin tab Sentences); V3 == “ziel_unbekannt” “Gerät nicht gefunden (<v4>): <v2> – im Plugin Reiter Sätze am Ziel einen Alias ergänzen” (device not found – add an alias at the target); V3 == “ziel_fehlt” “kein Gerät genannt (<v4>): <v2> – das Gerät nennen oder im Plugin Reiter Mikrofone dem Mikrofon einen Raum geben” (no device named – name it or give the microphone a room); V3 := “llm_” “Sprachmodell antwortet nicht oder falsch – im Plugin Reiter Dienste nachsehen” (language model does not answer); V3 == “rueckfrage” “Rückfrage: <v5>” (question back); V3 == “” “seit dem Neustart noch kein Satz” (no sentence since the restart); without condition “nicht ausgeführt (<v3>): <v2> – <v5>” (not executed); visualisation ON | V1 = #8, V2 = #9, V3 = #10, V4 = #12, V5 = #11, V6 = #13"),
  Z3_16=("ODER | Ansagen stilllegen, Teil 1 (Sprachsteuerung) | — (Nachtruhe oder Schalter) | I1 = Ausgang AQ von #13, I2 = #14",
         "OR | Ansagen stilllegen, Teil 1 (Sprachsteuerung) | — (night quiet or switch) | I1 = output AQ of #13, I2 = #14"),
)


# ---------------------------------------------------------------------------
# STAND (vb_ss013, 05.11.2026): Sprachsteuerung 0.12.13 - Wetterfragen (Abnehmer haus/wetter/* von Weatherdata 0.9.8,
# Rueckfall weatherdata/*). Neu [UI021]: Haken und Thementabelle im Reiter MQTT, Pruefzeile im Reiter Test.
# Die gesprochenen Antworten stehen als SPRECHTEXTE im Dienst, nicht hier.
# ---------------------------------------------------------------------------
s("UI021",
  L_WETTER=('Wetterfragen beantworten („Wie warm ist es draußen?“)', 'Answer weather questions (“How warm is it outside?”)'),
  H_WETTER=('Ab Werk aus. Dafür muss das Plugin Weatherdata installiert sein. So geht es: 1. In Weatherdata im Reiter MQTT „Wetter an andere Plugins geben“ anhaken und speichern. 2. Hier anhaken und speichern. 3. Nach höchstens zwei Minuten fragen. Es geht zum Beispiel: „Wie warm ist es draußen?“, „Wie ist das Wetter?“, „Wie wird das Wetter morgen?“, „Regnet es heute noch?“, „Brauche ich einen Schirm?“, „Gibt es eine Wetterwarnung?“, „Wie ist der Pollenflug?“, „Wie windig ist es?“ – auch auf Englisch. Ohne den Haken in Weatherdata liest die Sprachsteuerung ersatzweise dessen eigene Werte; dann fehlen die Regenmenge für morgen und der Name der Warnung. Hat sie keine frischen Wetterdaten, sagt sie „Wetterdaten sind nicht verfügbar“ – sie rät nie. Eine eigene Regel im Reiter Sätze geht vor.', "Off by default. The Weatherdata plugin must be installed. How to: 1. In Weatherdata, tick “Share the weather with other plugins” on its MQTT tab and save. 2. Tick this box and save. 3. Ask after at most two minutes. For example: “How warm is it outside?”, “What's the weather like?”, “What will the weather be like tomorrow?”, “Will it rain today?”, “Do I need an umbrella?”, “Is there a weather warning?”, “What's the pollen count?”, “How windy is it?” – also in German. Without the tick in Weatherdata, the voice control reads its own values instead; then tomorrow's rain amount and the name of the warning are missing. Without fresh weather data it says “Weather data is not available” – it never guesses. Your own rule on the Sentences tab takes precedence."),
  T_WETTER_THEMEN=('(28 Themen von Weatherdata; ersatzweise weatherdata/…)', '(28 topics from Weatherdata; as a fallback weatherdata/…)'),
  B_WETTER=('Wetter von Weatherdata, nur mit Wetterfragen; nie ein Standort', 'Weather from Weatherdata, only with weather questions; never a location'),
  F_WETTER=('Wetterfragen (haus/wetter)', 'Weather questions (haus/wetter)'),
  A_WETTER_AUS=('aus (Reiter MQTT, „Wetterfragen beantworten“)', 'off (MQTT tab, “Answer weather questions”)'),
  A_WETTER_HAUS=('bereit – Weatherdata liefert die Wetterübersicht; draußen %s °C, Warnstufe %s', 'ready – Weatherdata delivers the weather summary; outside %s °C, warning level %s'),
  A_WETTER_LINIE=('bereit über den Ersatzweg – Weatherdata sendet, aber nicht die Wetterübersicht für andere Plugins (dort im Reiter MQTT „Wetter an andere Plugins geben“ anhaken); draußen %s °C', 'ready via the fallback – Weatherdata sends, but not the weather summary for other plugins (tick “Share the weather with other plugins” on its MQTT tab); outside %s °C'),
  A_WETTER_WARTET=('wartet auf Weatherdata (höchstens zwei Minuten nach dem Start)', 'waiting for Weatherdata (at most two minutes after the start)'),
  A_WETTER_KEINE=('keine frischen Wetterdaten – Fragen werden mit „Wetterdaten sind nicht verfügbar“ beantwortet. Ist Weatherdata installiert, dort „Werte über MQTT senden“ an und „Wetter an andere Plugins geben“ angehakt?', 'no fresh weather data – questions are answered with “Weather data is not available”. Is Weatherdata installed, with “Send values via MQTT” on and “Share the weather with other plugins” ticked?'),
  A_WETTER_GETRENNT=('Verbindung zum Broker steht nicht: %s.', 'connection to the broker is down: %s.'),
  A_WETTER_UNBEKANNT=('der laufende Dienst meldet noch keinen Wetterstand (läuft er, und ist der Haken gespeichert?)', 'the running service reports no weather state yet (is it running, and is the tick saved?)'),
)


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
