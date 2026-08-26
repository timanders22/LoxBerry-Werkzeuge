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

Aufruf:
    python3 Werkzeuge/sp_sprache_erzeugen.py <Pluginordner>
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
  CONT_GESTOPPT=("gestoppt", "stopped"),
  CONT_KEIN_DOCKER=("kein Docker", "no Docker"),
  CONT_LAEUFT=("läuft", "running"),
  DIENST=("Sprachdienst", "Voice service"),
  EIGENER_WERT=("eigener Wert (Feld darunter)", "custom value (field below)"),
  EIGENER_WERT_H=("oder hier einen eigenen Wert eintragen",
                  "or enter a custom value here"),
  EIGENSCHAFT=("Eigenschaft", "Property"),
  EIN=("ein", "on"),
  GATEWAY=("MQTT-Gateway des LoxBerry", "LoxBerry MQTT gateway"),
  GESTOPPT=("gestoppt", "stopped"),
  JA=("ja", "yes"),
  KEINE_PID=("keine Prozessnummer", "no process id"),
  LAEUFT=("läuft", "running"),
  MIKROFONE=("Mikrofone", "Microphones"),
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
  KEIN_DOCKER=("<b>Docker ist nicht installiert oder antwortet nicht.</b> Ohne Docker kann das "
               "Plugin die Sprachdienste nicht selbst betreiben. Zwei Wege: das "
               "LoxBerry-Plugin <i>Docker</i> installieren, oder die Dienste auf einem anderen "
               "Rechner betreiben und oben nur deren Adressen eintragen. Antwortet Docker "
               "nicht, obwohl es installiert ist, fehlt meist die Gruppe: "
               "<span class='sm-mono'>sudo usermod -aG docker loxberry</span>",
               "<b>Docker is not installed or not responding.</b> Without Docker this plugin "
               "cannot run the voice services itself. Two ways: install the LoxBerry "
               "<i>Docker</i> plugin, or run the services on another machine and only enter "
               "their addresses above. If Docker is installed but silent, the group is usually "
               "missing: <span class='sm-mono'>sudo usermod -aG docker loxberry</span>"),
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
                  "es geht um Gigabyte.",
                  "<b>The model folder is never deleted.</b> <i>Remove container</i> only "
                  "removes the container; the downloaded models stay and are back immediately "
                  "after <i>Create container</i>. This is deliberate: gigabytes are involved."),
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
  H_TTS_MODE=("<b>Music Server</b> ist der Regelfall. <b>MusicServer4Home</b> und <b>eigene "
              "Vorlage</b> benutzen das Vorlagenfeld unten. Beim <b>originalen Loxone "
              "Audioserver</b> gibt es keinen Aufruf über das Netz - dort wird die Ansage in "
              "Loxone Config gebaut (Textgenerator am TTS-Eingang), und das Plugin liefert den "
              "Text im MQTT-Thema <span class='sm-mono'>/ansage</span>.",
              "<b>Music Server</b> is the standard case. <b>MusicServer4Home</b> and <b>custom "
              "template</b> use the template field below. The <b>original Loxone "
              "Audioserver</b> has no network call - there the announcement is built in Loxone "
              "Config (text generator at the TTS input), and the plugin delivers the text on "
              "MQTT topic <span class='sm-mono'>/ansage</span>."),
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
  L_SPRACHE=("Sprache (zwei Buchstaben)", "Language (two letters)"),
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
  ABO_V1_TITEL=("Gateway V1: Abo eintragen", "Gateway V1: enter the subscription"),
  ABO_V1=("In <i>System → MQTT Gateway</i> unter <i>Subscriptions</i> eintragen und speichern:",
          "In <i>System → MQTT Gateway</i> under <i>Subscriptions</i> enter and save:"),
  ABO_V1_WARNUNG=("<b>Ohne diesen Eintrag kommt am Miniserver nichts an.</b> Das ist die "
                  "häufigste Fehlerursache überhaupt.",
                  "<b>Without this entry nothing reaches the Miniserver.</b> This is the most "
                  "common cause of failure of all."),
  ABO_V2_TITEL=("Gateway V2: nichts einzutragen", "Gateway V2: nothing to enter"),
  ABO_V2=("Unter Gateway V2 gibt es das Eingabefeld für Abos nicht mehr. Die Datenpunkte "
          "erscheinen von selbst, sobald das Plugin zum ersten Mal etwas gesendet hat, und "
          "werden in den <i>Abonnements</i> angehakt.",
          "Under gateway V2 there is no subscription input field any more. The data points "
          "appear by themselves once the plugin has published for the first time, and are "
          "ticked in the <i>Subscriptions</i> list."),
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
  EMPFEHLUNG=("<b>Der bequemste Weg</b> ist die Zeile mit dem Zielthema: je Ziel ein eigenes "
              "Thema. Ein virtueller Eingang hängt dann genau an "
              "<span class='sm-mono'>wohnzimmer/licht/aktion</span> und braucht keine "
              "Fallunterscheidung im Miniserver. Die Vorlage im Reiter <i>Einbindung in "
              "Loxone</i> baut diese Eingänge fertig.",
              "<b>The most convenient way</b> is the row with the target topic: one topic per "
              "target. A virtual input then hangs on exactly "
              "<span class='sm-mono'>wohnzimmer/licht/aktion</span> and needs no case "
              "distinction in the Miniserver. The template on the <i>Loxone integration</i> tab "
              "builds these inputs ready to import."),
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
  B_ZIELTHEMA=("Dasselbe noch einmal unter dem Thema des Ziels - der bequemste Weg in Loxone",
               "The same again under the target's own topic - the most convenient way in Loxone"),
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
  ESPHOME_WARNUNG=("<b>Ehrliche Einordnung:</b> Der ESPHome-Weg ist der am wenigsten geprüfte "
                   "Teil dieses Plugins. Bis 0.9.11 war er überhaupt nicht vorhanden - das "
                   "Gerät wurde verbunden und danach geschah nichts. Seit 0.10.0 werden die "
                   "Rückrufe der Sprachschnittstelle bedient; ob der Audioweg an einem echten "
                   "Gerät trägt, ist mangels Gerät NICHT gemessen. Ein Fehler dort reißt die "
                   "Wyoming-Mikrofone nicht mit - jedes läuft für sich. Wer sicher gehen will, "
                   "fängt mit einem Wyoming-Satelliten an.",
                   "<b>An honest assessment:</b> the ESPHome path is the least tested part of "
                   "this plugin. Until 0.9.11 it did not exist at all - the device connected and "
                   "then nothing happened. Since 0.10.0 the voice assistant callbacks are "
                   "served; whether the audio path works on a real device has NOT been measured "
                   "for lack of one. A fault there does not drag the Wyoming microphones down - "
                   "each runs on its own. To be safe, start with a Wyoming satellite."),
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
  ZIELE_HILFE=("Eine Zeile ohne Schlüssel und ohne Namen wird übergangen; wer ein Ziel löschen "
               "will, leert beide Felder. Der Haken <i>Rückfrage</i> lässt die Anlage bei "
               "diesem Ziel erst nachfragen, statt sofort zu schalten - gedacht für Tore, "
               "Schlösser und alles, was man nicht versehentlich auslösen will.",
               "A row without key and name is skipped; to delete a target, clear both fields. "
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
                       "<span class='sm-mono'>[schalte|mach] {ziel} [aus|ab]</span> also matches "
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
  EINLEITUNG=("Die Sprachsteuerung sagt Loxone, WAS gemeint war. Was daraus wird, entscheidet "
              "der Miniserver - so bleibt die Logik dort, wo sie hingehört.",
              "The voice control tells Loxone WHAT was meant. What comes of it is decided by "
              "the Miniserver - so the logic stays where it belongs."),
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
  S1_TEXT=("Alles, was MQTT betrifft, steht im Reiter <i>MQTT</i>: der Zustand des Gateways, "
           "das einzutragende Abo und die vollständige Themenliste. Ohne diesen Schritt kommt "
           "am Miniserver nichts an.",
           "Everything concerning MQTT is on the <i>MQTT</i> tab: the gateway state, the "
           "subscription to enter and the full topic list. Without this step nothing reaches "
           "the Miniserver."),
  S3_TITEL=("Schritt 2: Zustand der Anlage überwachen", "Step 2: monitor the system state"),
  S3_TEXT=("Ein virtueller HTTP-Eingang, der den Zustand holt. Wichtig sind vor allem "
           "<span class='sm-mono'>BEREIT</span> - wie viele Mikrofone gerade wirklich verbunden "
           "sind - und <span class='sm-mono'>DIENSTE</span>: ein toter Whisper-Container sieht "
           "sonst genauso aus wie eine gesunde Anlage. Ein Mikrofon, das seit Tagen nicht "
           "antwortet, fällt niemandem auf, bis man davor steht und redet.",
           "A virtual HTTP input that fetches the state. The important ones are "
           "<span class='sm-mono'>BEREIT</span> - how many microphones are really connected - "
           "and <span class='sm-mono'>DIENSTE</span>: otherwise a dead Whisper container looks "
           "exactly like a healthy system. A microphone that has not answered for days goes "
           "unnoticed until you stand in front of it and speak."),
  S4_TITEL=("Schritt 3: Loxone spricht", "Step 3: Loxone speaks"),
  S4_TEXT=("Es geht auch andersherum: Loxone kann die Anlage etwas sagen lassen, ihr einen Satz "
           "unterschieben, als hätte ihn jemand gesprochen, oder die Ansagen stilllegen. Ein "
           "<i>Virtueller Ausgang</i> mit der Adresse des LoxBerry genügt - oder gleich die "
           "fertige Vorlage von oben.",
           "It also works the other way round: Loxone can have the system say something, feed "
           "it a sentence as if someone had spoken it, or mute announcements. A <i>virtual "
           "output</i> with the LoxBerry address is enough - or simply the ready-made template "
           "above."),
  S4_ANSAGE=("<b>Das ist mehr wert, als es klingt.</b> Eine Ansage 'Das Garagentor steht seit "
             "einer Stunde offen' im richtigen Raum erreicht mehr als jede Meldung auf einem "
             "Bildschirm, den niemand ansieht. Und der Satzweg macht die Sprachlogik auch für "
             "Taster nutzbar.",
             "<b>This is worth more than it sounds.</b> An announcement 'the garage door has "
             "been open for an hour' in the right room achieves more than any message on a "
             "screen nobody looks at. And the sentence path makes the voice logic usable from "
             "push buttons too."),
  S5_TITEL=("Schritt 4: Das Token", "Step 4: the token"),
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
  S6_TITEL=("Schritt 5: Komplette Baustein-Liste zum 1:1-Nachbauen",
            "Step 5: complete block list to rebuild 1:1"),
  S6_TEXT=("Nachgebaut wird: ein gesprochener Befehl schaltet eine Lichtgruppe, der Ausfall der "
           "Sprachkette wird gemeldet, und nachts schaltet Loxone die Ansagen still. Loxone "
           "Config führt alle Bausteine in der Baustein-Suche (F5).",
           "What is rebuilt: a spoken command switches a light group, a failure of the voice "
           "chain is reported, and at night Loxone mutes the announcements. Loxone Config lists "
           "all blocks in the block search (F5)."),
  S6_ERLAEUTERUNG=("<b>Zu #3, #4 und #5:</b> Diese drei sind virtuelle Eingänge für TEXT, keine "
                   "Zahlen. In Loxone Config ist das der Haken 'Als Text verwenden' - ohne ihn "
                   "kommt bei <span class='sm-mono'>ein</span> eine 0 an.<br><b>Zu #8 und "
                   "#9:</b> Erst die UND-Verknüpfung mit dem Ziel macht den Befehl eindeutig. "
                   "Ohne sie schaltet 'Licht aus' in der Küche auch das Wohnzimmer.<br><b>Zu "
                   "#11:</b> Die Schwelle liegt bewusst hoch. Wer eine halbe Stunde nichts "
                   "sagt, hat keine Störung - er hat nur nichts gesagt. Gemeint ist das ALTER "
                   "des Abbilds, nicht die Zeit seit dem letzten Satz.<br><b>Zu #13 und "
                   "#15:</b> Der Benachrichtigungs-Baustein sendet nur beim Wechsel von Aus auf "
                   "Ein. Niemals mehrere Quellen direkt an seinen Eingang legen, sondern erst "
                   "über ein ODER zusammenführen.<br><b>Zu #16 und #17:</b> Der Rückweg. Damit "
                   "sagt die Anlage von sich aus Bescheid - und hält nachts den Mund.",
                   "<b>On #3, #4 and #5:</b> these three are virtual inputs for TEXT, not "
                   "numbers. In Loxone Config that is the 'use as text' checkbox - without it "
                   "<span class='sm-mono'>ein</span> arrives as 0.<br><b>On #8 and #9:</b> only "
                   "the AND with the target makes the command unambiguous. Without it 'lights "
                   "off' in the kitchen also switches the living room.<br><b>On #11:</b> the "
                   "threshold is deliberately high. Someone who says nothing for half an hour "
                   "has no fault - they simply said nothing. What is meant is the AGE of the "
                   "snapshot, not the time since the last sentence.<br><b>On #13 and #15:</b> "
                   "the notification block only fires on a change from off to on. Never wire "
                   "several sources directly to its input, combine them with an OR "
                   "first.<br><b>On #16 and #17:</b> the way back. This lets the system speak "
                   "up by itself - and keep quiet at night."),
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
  T_NAMENSVORSCHLAG=("Name (Vorschlag)", "Name (suggestion)"),
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
  )

s("BAUSTEIN",
  EREIGNIS=("dem Ereignis, das angesagt werden soll", "the event to be announced"),
  NACHTS=("dem Nachtmerker der Anlage", "the house night flag"),
  N01=("SPRACHSTEUERUNG_OK", "SPRACHSTEUERUNG_OK"),
  N02=("SPRACHSTEUERUNG_ALTER", "SPRACHSTEUERUNG_ALTER"),
  N03=("Sprachsteuerung Aktion", "Voice control action"),
  N04=("Sprachsteuerung Ziel", "Voice control target"),
  N05=("Sprachsteuerung Grund", "Voice control reason"),
  N06=("Befehl war ein", "Command was on"),
  N07=("Befehl war aus", "Command was off"),
  N08=("Wohnzimmer einschalten", "Switch living room on"),
  N09=("Wohnzimmer ausschalten", "Switch living room off"),
  N10=("Licht Wohnzimmer", "Living room light"),
  N11=("Sprachkette veraltet", "Voice chain stale"),
  N12=("Sprachdienst antwortet nicht", "Voice service not responding"),
  N13=("Sprachsteuerung Störung gesammelt", "Voice control fault collected"),
  N14=("Sprachsteuerung Störung bestätigt", "Voice control fault confirmed"),
  N15=("Meldung Sprachsteuerung gestört", "Notification voice control faulty"),
  N16=("Ansage über den Lautsprecher", "Announcement via loudspeaker"),
  N17=("Ansagen nachts stilllegen", "Mute announcements at night"),
  P01=("Befehlserkennung <span class='sm-mono'>\\i;OK=\\i\\v</span>",
       "Command recognition <span class='sm-mono'>\\i;OK=\\i\\v</span>"),
  P02=("Befehlserkennung <span class='sm-mono'>\\i;ALTER=\\i\\v</span>",
       "Command recognition <span class='sm-mono'>\\i;ALTER=\\i\\v</span>"),
  P03=("MQTT-Thema <span class='sm-mono'>sprachsteuerung/aktion</span>, ALS TEXT",
       "MQTT topic <span class='sm-mono'>sprachsteuerung/aktion</span>, AS TEXT"),
  P04=("MQTT-Thema <span class='sm-mono'>sprachsteuerung/ziel</span>, ALS TEXT",
       "MQTT topic <span class='sm-mono'>sprachsteuerung/ziel</span>, AS TEXT"),
  P05=("MQTT-Thema <span class='sm-mono'>sprachsteuerung/grund</span>, ALS TEXT",
       "MQTT topic <span class='sm-mono'>sprachsteuerung/grund</span>, AS TEXT"),
  P06=("Vergleichstext <span class='sm-mono'>ein</span>",
       "Comparison text <span class='sm-mono'>ein</span>"),
  P07=("Vergleichstext <span class='sm-mono'>aus</span>",
       "Comparison text <span class='sm-mono'>aus</span>"),
  P10=("Dimmen zulassen", "Allow dimming"),
  P11=("Ein bei 1800, Aus bei 900", "On at 1800, off at 900"),
  P14=("300 s", "300 s"),
  P15=("Push-Nachricht oder Mail", "Push message or mail"),
  P16=("Adresse aus Schritt 3, Aktion sprechen", "Address from step 3, action sprechen"),
  P17=("Adresse aus Schritt 3, Aktion ruhe - EIN legt still, AUS gibt frei",
       "Address from step 3, action ruhe - ON mutes, OFF releases"),
  T_BENACHR=("Benachrichtigungs-Baustein", "Notification block"),
  T_EVZ=("Einschaltverzögerung", "On-delay"),
  T_LICHT=("Beleuchtungssteuerung", "Lighting controller"),
  T_NICHT=("NICHT", "NOT"),
  T_ODER=("ODER", "OR"),
  T_SWS=("Schwellwertschalter", "Threshold switch"),
  T_UND=("UND", "AND"),
  T_VA=("Virtueller Ausgang Befehl", "Virtual output command"),
  T_VE=("Virtueller Eingang (analog)", "Virtual input (analogue)"),
  T_VERGL=("Vergleicher (Text)", "Comparator (text)"),
  T_VET=("Virtueller Eingang (Text)", "Virtual input (text)"),
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
  F_MIKROFONE=("Sind Mikrofone eingetragen?", "Are microphones configured?"),
  F_MQTT=("Zustand des MQTT-Gateways", "State of the MQTT gateway"),
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
  A_VORLAGE_OK=("ja, alle drei Vorlagen sind wohlgeformt und tragen CRLF",
                "yes, all three templates are well-formed and use CRLF"),
  A_SMACTIVE_OK=("ja, an Leiste und Bereichen (%d Reiter)", "yes, on bar and panes (%d tabs)"),
  A_SMACTIVE_FEHL=("Nein - Leiste %d, Bereiche %d von %d. Ohne JavaScript wäre die Seite leer.",
                   "No - bar %d, panes %d of %d. Without JavaScript the page would be empty."),
  A_SMACTIVE_NICHTS=("die Oberflächendatei ließ sich nicht lesen - die Prüfung greift ins Leere",
                     "the interface file could not be read - the check has nothing to look at"),
  A_FORM_KEINS=("kein Formular gefunden - die Prüfung greift ins Leere",
                "no form found - the check has nothing to look at"),
  A_FORM_OHNE=("nein - %d von %d ohne Merkmal", "no - %d of %d without the marker"),
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
  M_TROCKEN=("Trockenlauf: %s &mdash; Antwort wäre: '%s'. Es wären %d MQTT-Themen geschrieben "
             "worden, gesendet wurde nichts.",
             "Dry run: %s &mdash; the answer would be: '%s'. %d MQTT topics would have been "
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
              "Nebengeräusche - entscheidet sich erst bei Ihnen.",
              "Whether a microphone delivers audio Whisper understands; whether the wake word "
              "reliably triggers in your room; whether ESPHome microphones carry the audio path "
              "- only real hardware can establish that. The plugin was built without any; the "
              "whole chain was tested against stubs using the original Wyoming protocol "
              "package. What comes after - room acoustics, reverberation, background noise - is "
              "decided at your place."),
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
    # newline='' UND \n: die Datei landet auf einem Linux-System. Ohne das
    # schreibt Python unter Windows CRLF, und die Sprachdateien waeren als
    # einzige Dateien des Pakets anders als der Rest.
    with pfad.open("w", encoding="utf-8", newline="") as f:
        f.write("\n".join(zeilen) + "\n")
    return sum(len(v) for v in abschnitte.values())


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


if __name__ == "__main__":
    sys.exit(main())
