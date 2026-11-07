# Leitungen aus der Baustein-Liste setzen – Anleitung

Das Werkzeug ist `leitungen_setzen.py` (Fassung 1.3.0, Python 3, keine Zusatzpakete). Es gehört zu Nr. 36 und ersetzt die Handzuordnung in `../verbinden.py`.

## Ablauf

1. **Bausteine in Loxone Config setzen.** Lege jeden Baustein der Baustein-Liste auf die Programmseite.
   - Gib ihm den **Namen aus der Spalte „Name“**, genau so geschrieben. Groß- und Kleinschreibung ist egal.
   - Setze die Parameter.
   - Die virtuellen Eingänge und Ausgänge ziehst du aus dem Baum auf die Seite. Ihr Titel muss dem Namen in der Liste entsprechen. `abfahrt_OK` in der Liste passt zu `ABFAHRT_OK` in Config.
   - Leitungen ziehst du nicht. Hat Config beim Ablegen schon selbst eine gezogen, siehe `--gleiche-lassen` unten.
2. **Speichern** und das Projekt in Config **schließen**.
3. **Trockenlauf.** Er zeigt die geplanten Leitungen als Tabelle und schreibt nichts:

   ```
   set PYTHONDONTWRITEBYTECODE=1
   python leitungen_setzen.py MeinDemo.Loxone --liste baustein_listen.txt --abschnitt Abfahrtsassistent --seite Abfahrtsassistent --ohne 10 --weg HTTP
   ```

   Lies die Tabelle und die Zeilen „Hinweis:“. Ein Hinweis nennt eine Zelle, aus der sich keine Leitung ableiten lässt, zum Beispiel „Ihr Taster“ oder „Bedienung in der App“. Diese Eingänge bleiben frei.
4. **Schreiblauf.** Dazu kommt `--schreiben MeinDemo_verbunden.Loxone`.
   - Es entsteht immer eine **neue** Datei. Die Eingabedatei wird nie überschrieben.
   - Eine schon bestehende Zieldatei wird nur mit `--ueberschreiben` ersetzt.
   - BOM und CRLF bleiben erhalten. Außer den neuen Leitungen bleibt die Datei byte-gleich.
5. **Weitere Seiten:** Hat das Projekt mehrere Seiten oder Listen, rufst du das Werkzeug je Abschnitt einmal auf. Dabei ist die Ausgabe des einen Laufs die Eingabe des nächsten.
6. **Gegenprobe in Config:** Öffne die neue Datei in Loxone Config. Config muss sie ohne Meldung öffnen und die Leitungen zeichnen. Erst dann gilt die Datei (Hausregel „wohlgeformt ≠ lauffähig“).

## Schalter

| Schalter | Wirkung |
|---|---|
| `--liste DATEI` | Baustein-Liste. Möglich sind zwei Formen. **Textform** wie `baustein_listen.txt`: `Nr \| Typ \| Name \| Parameter \| Eingänge verbinden mit`, Abschnitte beginnen mit `===== Name`. **Gerendertes HTML** des Reiters „Einbindung in Loxone“: Jede Tabelle mit der Kopfzelle „… verbinden mit“ ist ein Abschnitt, benannt nach der Überschrift davor. |
| `--abschnitt NAME` | Abschnitt der Liste. Pflicht, wenn die Liste mehrere Abschnitte hat. |
| `--seite TITEL` | Programmseite in Config. Ohne Angabe sucht das Werkzeug auf allen Seiten. Gib die Seite an; sonst werden Namen und Ketten leicht mehrdeutig. |
| `--weg HTTP\|MQTT` | Gilt für Zellen wie „HTTP-Weg: Eingang ALTER. MQTT-Weg: …“. Ohne Angabe bricht das Werkzeug ab. |
| `--ohne NR` | Die Listenzeile ist bewusst nicht gebaut, etwa der feste Wert #10 im Pilot, der als Vorgabe 5 an I2 steht. Leitungen von und zu dieser Zeile entfallen. Der Schalter ist mehrfach möglich. Seit 1.2 auch mit Buchstaben (`--ohne 18a`). Fehlt ein Vorlagen-Eingang in der Projektdatei, weil die Vorlage nicht importiert ist, nimmst du die Zeile, die ihn nennt, mit `--ohne` heraus. |
| `--ziel NR=TITEL` | Gilt für Ketten wie „UND → Virtueller Ausgang“ und legt fest, welcher Baustein am Ausgang hängt. Ohne Angabe nimmt das Werkzeug den einzigen Baustein dieses Typs auf der Seite, der keine eigene Listenzeile hat. Bei „→ Ausgangsbefehl play“ (seit 1.2) sucht es ohne Angabe den Befehl mit genau diesem Titel. Ist er mehrdeutig, legst du mit `--ziel 6.1=play` den Baustein auf der Seite fest (6 = Zeile, 1 = erste Folgestufe). |
| `--gleiche-lassen` | Ein Eingang, der schon mit genau dem geplanten Ausgang verbunden ist, bleibt stehen. Das ist gedacht für Leitungen, die Config beim Ablegen selbst gezogen hat. Ist der Eingang mit etwas anderem verbunden, bricht das Werkzeug trotzdem ab. |
| `--schreiben ZIEL`, `--ueberschreiben` | Siehe oben. |

Rückgabe: **0** heißt in Ordnung, **2** heißt Abbruch. Bei einem Abbruch steht eine Meldung `ABBRUCH: …` auf stderr, und es wird nichts geschrieben.

## Was die Spalte „Eingänge verbinden mit“ verstehen muss

| Schreibweise in der Liste | Leitung |
|---|---|
| `Ausgang von #11`, `#13` | Standardausgang von Zeile 11 bzw. 13 auf den ersten Eingang |
| `I1 = #13, I2 = #14` / `V1 = ABFAHRT_IN, …` | An die Eingänge I1/I2 … bzw. Input1 … (beim Status V1 → I1). Kleinschreibung `v1` gilt seit 1.1 genauso. |
| `V = #1`, `Gpwr = #3`, `Soc = #5`, `Off = #9` (seit 1.1) | An den Anschluss mit genau diesem Namen. Der Name muss am Baustein in der Projektdatei als Anschluss stehen (`<Co K="Gpwr" …>`), Groß- und Kleinschreibung egal. Sonst Abbruch mit der Liste der vorhandenen Anschlüsse. Namen von Ausgängen (Q, AQ, TQ, alles, was mit Q/AQ/TQ beginnt, API) werden abgelehnt. Achtung: Config zeigt manche Anschlüsse unter einem anderen Namen als die Datei. Der Bewässerungsbaustein hat in der Datei kein `Off` (dort: A, AIv, Rf, Ra, Reset …). Dann bricht das Werkzeug ab und nennt die Namen der Datei. |
| `AI1 = #7, AI2 = #2` (seit 1.1) | So beschriftet Config die Analogeingänge etwa von „Größer oder gleich“. Hat der Baustein keinen Anschluss `AI1`, nimmt das Werkzeug `Input1`, so heißen sie in der Datei (gemessen an Greater/GreaterEqual/Equal/Less einer von Config gespeicherten Datei). Ein Hinweis nennt die Umsetzung. Hat er auch kein `Input1`, bricht das Werkzeug ab. **Seit 1.2** gilt am Status (`State`) `AI1 … AI8` wie `V1 … V8`: Anschluss `I1 … I8`, mit Hinweis. |
| `V = #6`, `En = Konstante 1`, `Ausgang E von #7` an der Analogwertvalidierung (seit 1.2) | Der Baustein heißt in der Datei `Validator`. Seine Anschlüsse heißen dort `inval`, `enable`, …, `outval`, `error`. Die Config-Beschriftungen `V`, `En` und `E` setzt das Werkzeug an diesem Baustein auf `inval`, `enable` und `error` um, ein Hinweis nennt das. Der Standardausgang (`Ausgang von #7`, Kette „Analogwertvalidierung → Benachrichtigung“) ist `error`. **Seit 1.3 in Config gegengeprüft** (Musterprojekt, siehe „Config-Beschriftung und Name in der Datei“). Config legt `enable` negiert an (`Inv="true"`). **Seit 1.3.3** trägt das Werkzeug eine nicht negierte Leitung an `enable` ohne `Inv` ein und bricht ab, wenn sie schon vorhanden und negiert ist: Eine Konstante 1 an einem negierten `enable` kommt als 0 an, und die Validierung prüft Tmc nicht (Loxone-Beschreibung „Value Validator“; bis 16.10.2026 betraf das alle 22 Validierungen des Musterprojekts). |
| `V = Ausgang von pumpe_sperre (#1)` am Schwellwertschalter (seit 1.3) | Config beschriftet den Eingang mit `V`, in der Datei heißt er `Input`. Das Werkzeug setzt `V` nur an diesem Baustein (`AnalogThresholdTrigger`) auf `Input` um, ein Hinweis nennt das. Ohne Namen (`Ausgang von #1`) ist `Input` ohnehin der Standardeingang. |
| `FW_KRANK`, `I1 = FW_KRANK`, `V1 = …` am Analogkomparator; `Ausgang De von #2` (seit 1.3) | Typ „Analogwert-Vergleicher“ oder „Analogkomparator“ = `AnalogComparator` (Anschlüsse `Input1`, `Input2`, `On`, `Off`, `Q`). Standardeingang ist `Input1`, darum geht auch der bloße Name. `I1`/`I2` und `V1`/`V2` gehen auf `Input1`/`Input2`. Standardausgang ist `Q`: `I1 = #2` genügt, `Ausgang Q von #2` ist nicht mehr nötig. Den Ausgang beschriftet Config mit `De`; `Ausgang De von #2` wird `Q`. |
| `Ausgang Val von #3` am Status (seit 1.3) | Config beschriftet den Ausgang des Status mit `Val`, in der Datei heißt er `AQ`. Ohne Angabe gilt wie bisher AQ (TQ, wenn das Ziel ein Textausgang ist). |
| Typ `Flankenerkennung (steigend)` / `(fallend)` (seit 1.2) | Der Baustein heißt in der Datei `EdgeDetection` (Eingang `Input`). Als Quelle nimmt das Werkzeug `RisingEdge` bei „steigend“ und `FallingEdge` bei „fallend“. Steht keine Richtung im Typ, bricht es ab, außer der Ausgang ist ausdrücklich genannt (`Ausgang Edge von #N`). |
| `I2 = #10 (negiert)` (seit 1.1) | Es entsteht die Leitung, und der Eingang wird negiert. In der Datei steht dann `<Co K="I2" Inv="true" Nc="1" U="…">`, so wie Config es speichert. Ein Hinweis nennt jeden negierten Eingang. Mit `--gleiche-lassen` bricht das Werkzeug ab, wenn ein vorhandener Eingang verbunden, aber nicht negiert ist. Geht auch bei `Eingang X (negiert)` und `Ausgang von #N (negiert)`, das Wort muss am Ende stehen. |
| `Eingang = #5` (seit 1.1) | Standardeingang wie bei `Ausgang von #5` ohne Namen |
| `En = Konstante 1` (seit 1.1) | Keine Leitung, nur ein Hinweis. Der Anschlussname wird trotzdem geprüft. Den Wert setzt du in Config von Hand. Soll das Werkzeug verbinden, führe die Konstante als eigene Listenzeile (Typ „Konstante“, auf der Seite liegt sie als Eingangsbaustein) und schreibe `En = #N`. |
| `Ausgang von MOWER_BATT (#2)` (seit 1.1) | Ist #2 eine Zeile „Virtueller HTTP-Eingang …“ oder „Virtueller UDP-Eingang …“ (Gerät oder Sammelzeile „…-Befehl“), ist `MOWER_BATT` der **Titel des Befehls**. Das Werkzeug sucht ihn in der Projektdatei (HTTP: `VirtualHttpInCmd`, UDP: `VirtualUdpInCmd`) und nimmt den Eingangsbaustein auf der Seite, der auf diesen Befehl verweist. Bei jeder anderen Zeile bleibt der Text zwischen „von“ und „(#N)“ wie bisher ohne Bedeutung. |
| `Eingang MOWER_BATT` (seit 1.1 auch ohne eigene Zeile) | Führt die Liste keinen Eingang dieses Namens, aber **genau eine** HTTP-/UDP-Zeile (Sammelzeilen „…-Befehl“ gehen vor), gilt `MOWER_BATT` als Befehl dieser Zeile. Bei mehreren solchen Zeilen bricht das Werkzeug ab; dann `Ausgang von MOWER_BATT (#N)` schreiben. |
| `Eingang MINSTART` oder nur `MINSTART` | Virtueller Eingang aus der Liste, dessen Name so heißt oder auf `_MINSTART` endet |
| `FW_OK`, `V1 = FW_OK`, `Gpwr = EVCC_NETZ_KW`, `Eingang FW_OK` **ohne Listenzeile** (seit 1.2) | Vorlagen-Eingang: Führt die Liste den Namen nicht, sucht das Werkzeug ihn in der Projektdatei, siehe „Vorlagen-Eingänge“ unten. Für einen bloßen Namen gilt das nur mit Unterstrich (`FW_OK`, `pumpe_status_zaehler`). Ein bloßes Wort wie „Lebenszeichen“ bleibt Freitext. |
| `Ausgang AQ der Radiotasten (#11)` | Ausdrücklich genannter Ausgang (AQ) |
| `Ausgang des Statusbausteins (#5)` | Standardausgang, beim Status TQ, wenn das Ziel ein Textausgang ist, sonst AQ |
| `#18a`, `Ausgang von #18b` (seit 1.2) | Zeilennummer mit kleinem Buchstaben. Die Zeile `18a \| ODER \| …` wird gelesen und ist eine eigene Zeile neben 18 und 18b. Eine Nummer `18 (optional)`, `18 optional` oder `18 *optional*` ist die Zeile 18. |
| Typ `UND → Virtueller Ausgang` | Zusätzlich: Ausgang Q des UND an den Folgebaustein |
| Typ `Flankenerkennung (steigend) → Ausgangsbefehl play` (seit 1.2) | Folgebaustein ist der Baustein auf der Seite zum Ausgangsbefehl mit genau dem Titel `play`, siehe „Ausgangsbefehle“ unten |
| Typ `Virtueller Ausgang samt Befehlen` (Mehrzahl „Befehle“/„Befehlen“), Zelle `beamer-wol, xbox-an ← #9; beamer-aus, xbox-aus ← #10` (seit 1.2) | Jeder genannte Befehl dieses virtuellen Ausgangs (Titel des Geräts = Name der Zeile) bekommt die Leitung vom Standardausgang der Zeile hinter dem Pfeil. So hängen mehrere Folgebausteine nebeneinander an einer Quelle. Bei der Einzahl („Virtueller Ausgang (Befehl)“) bleibt `I ← #34` wie bisher Freitext. |
| Zwischenbaustein ohne eigene Zeile („LP1_LAEDT über eine negierte Flanke“, „über einen Schwellwertschalter“) | Keine Leitung. Der Hinweis nennt den Zwischenbaustein. Setze ihn in Config von Hand, oder nimm ihn als eigene Zeile in die Liste auf. |
| Alles andere („Ihr Taster“, „wie #7 bis #9“, „—“, `#2 (MW1_PUSH)`) | Keine Leitung, nur ein Hinweis |

UND/ODER/NICHT nach Nr. 39 werden erkannt, die ältere Schreibweise Und/Oder/Nicht ebenso.

### Typnamen der Liste (seit 1.3 ergänzt)

Ein Zusatz in Klammern wie „(optional)“ zählt nie mit: „Schwellwertschalter (optional)“ ist ein Schwellwertschalter. Kennt das Werkzeug den Typ nicht, sucht es den Baustein nur nach dem Namen (Hinweis „Typ … unbekannt“).

| Typ in der Liste | Baustein in der Datei | Beleg |
|---|---|---|
| „Statusbaustein“ (wie „Status“) | `State` | Musterprojekt, von Config gespeichert |
| „Analogwert-Vergleicher“, „Analogkomparator“ | `AnalogComparator` | Musterprojekt, von Config gespeichert |
| „Treppenlichtschalter“, „Alarmanlage“, „Bewässerung“, „Energiemanager“ / „Energiemanager 2“ | `StairwayLS`, `Alarm`, `Irrigation`, `EnergyManager2` | Diesen Titel vergibt Config beim Ablegen (`Leer.Loxone`, von Config 17.1 gespeichert). Nie mit dem Werkzeug verbunden in Config geöffnet. |

Die neuen Namen gelten nur allein. „Statusbaustein oder Vergleicher“ und „Statusbaustein oder Formel“ bleiben unbekannt (Namenssuche), weil die Liste dort zwei Bausteine zur Wahl stellt.

**Bewusst nicht aufgenommen**, weil keine von Config gespeicherte Datei den deutschen Namen belegt oder der Name mehrdeutig ist: „Vergleicher“ (Größer, Gleich … oder Analogkomparator), „Analogwert-Vergleich“, „Merker“ (Config titelt ihn „M1“), „Analogspeicher“, „Taster“ (`PButtonT` heißt in Config „Taster“, die Listen meinen oft einen virtuellen Eingang), „Zähler“ (Config titelt den Zähler-Baustein `MeterAbsUni` „Zähler“, der Zähler `Counter` heißt „O…“), „Analoger Schwellwertschalter“, „Lichtsteuerung“.

### Standardanschlüsse ohne Typnamen (seit 1.3)

Wird ein Baustein nur über den Namen gefunden, nimmt das Werkzeug für `Ausgang von #N` bzw. eine Zelle ohne Anschlussnamen diese Anschlüsse. Grundlage sind die Anschlusslisten in `Referenz_Bausteine.Loxone` und `Leer.Loxone` (beide von Config gespeichert): als Eingang der erste Eingang, als Ausgang nur der einzige Ausgang des Bausteins.

| Baustein in der Datei | Standardeingang | Standardausgang |
|---|---|---|
| `AnalogComparator` (Musterprojekt) | `Input1` | `Q` |
| `Greater`, `GreaterEqual`, `Less`, `LessEqual`, `Equal`, `NotEqual` | `Input1` | `Q` |
| `Monoflop`, `OnOffDelay` | `InputTrigger` | `Q` |
| `AMemory` (Analogspeicher) | `Input` | `AQ` |
| `Memory` (Merker) | `Input` | – (hat `AQ` und `Q`: „Ausgang AQ von #N“ schreiben) |
| `StairwayLS` (Treppenlichtschalter) | `InputTrigger` | `Q` |

Andere Eingänge gehen mit dem Namen der Datei (`Trigger = #10` am Analogspeicher). Diese Standardanschlüsse sind nur an einer Attrappe belegt, nicht in Config verbunden geöffnet.

### Config-Beschriftung und Name in der Datei (seit 1.3)

Config zeigt manche Anschlüsse anders, als die Datei sie nennt. Am Musterprojekt (`Musterprojekt/LoxBerry-Plugins_Musterprojekt.Loxone`, von Config gespeichert, 09.10.2026) sind diese abgelesen und als gezogene Leitungen gefunden:

| Baustein (Datei) | Config zeigt | Datei | Werkzeug |
|---|---|---|---|
| Schwellwertschalter (`AnalogThresholdTrigger`) | `V` | `Input` | setzt um, mit Hinweis |
| Analogkomparator (`AnalogComparator`) | `V1`/`V2` bzw. `I1`/`I2`, Ausgang `De` | `Input1`/`Input2`, `Q` | setzt um (De mit Hinweis) |
| Status (`State`) | Ausgang `Val` (Eingänge `I1 … I8`) | `AQ` | setzt um, mit Hinweis |
| Analogwertvalidierung (`Validator`) | `V`, `En`, Ausgang `E` | `inval`, `enable`, `error` | setzt um, mit Hinweis |

Die Umsetzung gilt nur am genannten Baustein. `V` am ODER, `De` am Status oder `E` am Analogkomparator brechen ab.

### HTTP- und UDP-Befehle (seit 1.1)

So steht ein Befehl in einer von Config gespeicherten Datei (gemessen an `Demo_Abfahrt_Alexa.Loxone`):

- Im Baum unter „Virtuelle Eingänge“ liegt `<C Type="VirtualHttpIn" Title="Abfahrts-Assistent">`. Darin steht je Befehl `<C Type="VirtualHttpInCmd" Title="ABFAHRT_OK">` mit den Ausgängen AQ und Q.
- Ziehst du den Befehl auf die Seite, legt Config dort einen `InputRef` mit demselben Titel an. Sein `Ref` zeigt auf den Befehl. Von diesem Baustein geht die Leitung aus, und zwar von AQ.
- Die Vorlagen-XML der Plugins schreibt anders (`VirtualInHttp`/`VirtualInHttpCmd`). Diese Form kommt in der Projektdatei nicht vor.

Abbruch gibt es in diesen Fällen, damit nie geraten wird:

- Den Befehl gibt es nicht. Die Meldung nennt ähnliche Titel.
- Es gibt den Befehl unter mehreren Geräten.
- Der Befehl liegt nicht auf der Seite, oder er liegt mehrmals dort.
- Die Liste nennt eine UDP-Zeile, der Befehl ist aber ein HTTP-Befehl, oder umgekehrt.

**UDP ist nicht an einem Demo-Projekt geeicht.** Die Typnamen `VirtualUdpIn`/`VirtualUdpInCmd` und der Verweis über `InputRef Ref=` sind an einer von Config gespeicherten Hausdatei gezählt. Nur gezählt, nicht verbunden.

### Vorlagen-Eingänge (seit 1.2)

Viele Linien legen ihre Eingänge über eine Vorlage an (Funkwacht `FW_OK`, Fensterbilanz `FB_OK`, Einspeisebremse `EB_EIN`). Die Baustein-Liste hat dafür keine eigene Zeile. Das Werkzeug sucht einen solchen Namen so:

1. Steht er in der Liste (Name gleich oder endet auf `_NAME`), gilt die Zeile, wie bisher.
2. Bei `Eingang NAME` und einer HTTP-/UDP-Zeile in der Liste gilt der Weg von 1.1 (Befehl dieser Zeile).
3. Sonst sucht es in der Projektdatei einen virtuellen Eingang (`VirtualIn`) oder einen HTTP-/UDP-Befehl mit **genau diesem Titel**. Groß- und Kleinschreibung zählt nur, wenn es beide Schreibweisen gibt. Quelle ist der Eingangsbaustein auf der Seite, der auf ihn verweist (`InputRef`, Ausgang AQ). Ein Hinweis nennt jeden so gefundenen Eingang.

Abbruch gibt es in diesen Fällen, damit nie geraten wird:

- Den Titel gibt es nicht. Die Meldung nennt ähnliche Titel und `--ohne`.
- Es gibt ihn mehrmals.
- Er liegt nicht auf der Seite, oder er liegt mehrmals dort.
- Es ist ein Texteingang (`VirtualTextIn`). Als Quelle ist er nicht geeicht.

Ohne Projektdatei, etwa im Prüfer `baustein_grammatik_pruefen.py` ab 1.1.0, zählt die Zelle als Leitung mit Hinweis. Gefunden wird der Eingang erst am Projekt.

**Seit 1.3 für HTTP-Befehle an einem Config-Projekt geeicht:** Im Musterprojekt hat Config die Funkwacht-Eingänge `FW_OK`, `FW_KRANK`, `FW_ALTER`, `FW_ALARM` (`VirtualHttpInCmd` aus der Vorlage) so verbunden gespeichert, wie das Werkzeug sie setzt (`InputRef`, Ausgang AQ). Für `VirtualIn` gilt weiter nur die Zählung an der von Config gespeicherten Hausdatei vom 03.07.2026: 49 von 49 `InputRef` auf einen `VirtualIn` tragen dessen Titel. Alle 25 genutzten Ausgänge solcher Bausteine sind AQ, auch bei digitalen Eingängen.

### Ausgangsbefehle (seit 1.2)

Ein Ausgangsbefehl steht im Baum als `<C Type="VirtualOutCmd" Title="play">` unter seinem virtuellen Ausgang. Auf der Seite liegt dazu ein `OutputRef` mit demselben Titel, und sein `Ref` zeigt auf den Befehl. Die Leitung geht an dessen Eingang `AI`. Diese Form stammt aus `Demo_Abfahrt_Alexa.Loxone`, wo Config zwei solche Leitungen gespeichert hat; in der Hausdatei tragen 15 von 15 diesen Titel. Abbruch gibt es, wenn der Befehl fehlt (mit ähnlichen Titeln), wenn er mehrdeutig ist oder wenn er nicht genau einmal auf der Seite liegt.

### Am Musterprojekt in Config gegengeprüft (1.3)

Die Seiten Zigbee2MqttNG, Pumpenwacht und Funkwacht des Musterprojekts (24 Leitungen) setzt 1.3 aus den Zellen der Plugin-Listen genau so, wie Config sie gespeichert hat: Nach dem Entfernen aller Leitungen (`entverbinden.py`) und drei Läufen ist der Text jeder der drei Seiten byte-gleich der von Config gespeicherten Datei. Damit sind belegt: Analogwertvalidierung (V/En/E, Standardausgang `error`, Kette zur Benachrichtigung), Schwellwertschalter `V`, Analogkomparator (bloßer Name, Standardein- und -ausgang), Status als Quelle (AQ), Vorlagen-Eingänge über HTTP-Befehle, „Ausgang der einzigen Quelle (#6)“, Einschaltverzögerung, NICHT, ODER, Konstante als Listenzeile. Die Beschriftungen De und Val sind in Config abgelesen; an einer Leitung belegt sind sie nur an der Attrappe (`Ausgang De`/`Ausgang Val` ergeben dieselben Leitungen wie die Zellen ohne Angabe).

### Was nicht in Config gegengeprüft ist (Stand 1.3)

- **Flankenerkennung:** Typ `EdgeDetection` und die Anschlüsse stammen aus der Referenzdatei. Dass „steigend“ `RisingEdge` ist, folgt aus dem Namen. In Config ist das nicht nachgesehen.
- **Vorlagen-Eingänge über `VirtualIn`** (nicht HTTP-Befehl): nur gezählt, siehe oben.
- **AI1 am Status → I1:** Die Hausdatei hat am `State` nur `I1 … I8`. Was Config dort anzeigt, ist nicht nachgesehen.
- **Standardanschlüsse** für Größer/Kleiner/Gleich, Monoflop, Ein-/Ausschaltverzögerung, Analogspeicher, Merker und Treppenlichtschalter sowie die Typnamen Treppenlichtschalter, Alarmanlage, Bewässerung, Energiemanager: aus von Config gespeicherten Dateien abgeleitet, aber keine solche Leitung in Config geöffnet.

## Beleg erneut ausführen

```
set PYTHONDONTWRITEBYTECODE=1
python beleg.py
```

Der Beleg schreibt nur nach `beleg/`. Das Protokoll liegt danach in `beleg/BELEG_AUSGABE.txt`. Die Rückgabe ist 0, wenn jede Erwartung eingetroffen ist.

Die Formen von 1.1 belegt `attrappen.py` an einer Attrappe (Kopie des Demo-Projekts mit UDP-Gerät, InputRef auf HTTP- und UDP-Befehle, Energiezähler, Energiemanager, Vergleicher, Bewässerung). Es schreibt nur nach `attrappen/`, das Protokoll liegt in `attrappen/AUSGABE.txt`. Die Attrappe ist nicht in Config geöffnet worden.

Die Formen von 1.2 belegt `Pruefung-Durchgang-2026-09-29/wz_leitungen12/lauf/attrappen.py`. Die Attrappe enthält virtuelle Eingänge aus einer Vorlage, zwei virtuelle Ausgänge mit Befehlen, Flankenerkennungen, Analogwertvalidierungen, einen Status mit `AI1/AI2` und die Zeilen 18a, 18b und „19 (optional)“. Auch sie ist nicht in Config geöffnet worden.

Die Formen von 1.3 belegen `Pruefung-Durchgang-2026-09-29/wz_leitungen13/lauf/muster_lauf.py` (Musterprojekt: Kopie ohne Leitungen, drei Seiten, Vergleich mit der von Config gespeicherten Datei) und `…/wz_leitungen13/lauf/attrappen.py` (Musterkopie mit sechs Bausteinen aus `Leer.Loxone`, positive Fälle und Abbrüche; die Zusatzbausteine sind nicht in Config geöffnet worden).
