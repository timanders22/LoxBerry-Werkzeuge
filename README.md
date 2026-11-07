# LoxBerry-Werkzeuge

Die Prüf- und Bauwerkzeuge hinter den LoxBerry-Plugins dieses Kontos. Python 3
und Bash, ohne Fremdpakete, entstanden beim Bauen von rund fünfzig Plugins.

Sie sind **nicht** als Bibliothek gedacht, sondern als Werkstatt: jedes
Werkzeug beantwortet eine Frage, die einmal teuer war.

---

## Der Grundsatz

**Die Wirkung prüfen, nicht den Rückgabewert.** Fast jedes Werkzeug hier ist
entstanden, weil etwas Erfolg gemeldet hat, das nicht geschehen war — ein Tag,
den GitHub bestätigte und nicht anlegte; ein Sicherungsknopf, den drei Prüfer
grün meldeten, der aber keine Datei lieferte; eine Konfiguration, die
„gespeichert" sagte und Felder verlor.

Daraus folgt das zweite: **jede Prüfung wird in beide Richtungen geeicht.**
Ein Werkzeug, das nur „ok" sagen kann, sagt nichts. Zu den meisten gibt es
deshalb eine `*_eichung.py`, die den Fehler absichtlich einbaut und nachweist,
dass er gefunden wird.

## Die wichtigsten

| Werkzeug | Frage |
|---|---|
| `packen.py` | Stimmen Ordnername, `plugin.cfg` und Archiv überein? Danach jede Datei **byteweise** zurückverglichen |
| `fassung_setzen.py` | Sind die sechs Stellen einer Fassung beisammen — und **steht der Tag schon**? |
| `fassungslage.py` | Was sagt der Ordner, was der Zweig, was der Tag? |
| `kopfzeilen_pruefen.py` | Steht ein Download-Handler hinter `lbheader()`? Dann liefert der Knopf eine Seite statt einer Datei |
| `kopfzeilen_umbauen.py` | Zieht genau diesen Block wörtlich an die richtige Stelle |
| `hausstandard_pruefen.py` | Hält die Oberfläche den Hausstandard? |
| `suchmuster_pruefen.py` | Trifft ein Loxone-Suchtext auch das falsche Feld? (`\iKM=` trifft `INSPKM=`) |
| `tote_helfer.py` | Funktionen ohne Aufruf — auch aus Skripten heraus gesucht, nicht nur aus PHP |
| `sprachschluessel_pruefen.py`, `ini_pruefen.py` | Sind Deutsch und Englisch gleichstaendig? |
| `wachposten_pruefen.py` | Ist jeder POST durch ein Formularmerkmal gedeckt? |
| `freigabe_pruefen.py` | Alles, was vor einer Veröffentlichung zu prüfen ist, in einem Aufruf — auch: steht ein Geheimnis, eine MAC, eine Netzadresse im Paket? |
| `zeilenenden_vergleichen.py` | Hat eine Datei ihren Zeilenendstil verloren? |
| `linie_veroeffentlichen.sh` | Die vorgeschriebene Reihenfolge in einem Aufruf |
| `projektdatei_vergleichen.py` | Was ist zwischen zwei `.Loxone`-Fassungen anders — in Bausteinen und Verbindungen, nicht in Zeilen? Findet, was Config beim Speichern still verwirft |
| `miniserver_abgleich.py` | Hat der Miniserver das geladen, was in der Datei steht? Projektdatei gegen `LoxAPP3.json` |
| `stand_sichern.py` | Lokaler Versionsstand des Arbeitsordners: sichern, Lage, Verlauf, Datei aus einem Stand daneben legen — nie überschreiben, kein Remote |
| `geraet_abbild.py` | Wie sieht der LoxBerry wirklich aus? Rechte, Pfade, Fassungen, Dienste über SSH — ohne Zugangsdaten |
| `geraetestand_vergleichen.py` | Trägt das Gerät wirklich den Inhalt seines Tags - oder nur dessen Nummer? Vergleicht die installierten Dateien byteweise mit dem Tag-Archiv der **installierten** Fassung. Zeilenenden und ersetzte Platzhalter zählen nicht als Befund, alles andere schon |
| `loxberry_zugang_einrichten.sh` | Einmalig auf dem LoxBerry: Benutzer `claude` mit Schlüssel und drei `sudo`-Rechten |
| `schreibwaechter.py` | Claude-Code-Hook: darf dieser Schreibvorgang überhaupt stattfinden? Lehnt Schreiben ins Archiv und stilles Kürzen ab |

## Attrappen

`perl_attrappe/` enthält Stellvertreter für Module, die `perl -c` laden
möchte (`LoxBerry::System`, `CGI`, `Net::MQTT::Simple`, …). Sie bilden **kein**
Verhalten nach — sie sorgen nur dafür, dass die Syntaxprüfung nicht an einem
fehlenden Modul scheitert und dabei aussieht wie ein Fehler des Plugins.
Näheres in `perl_attrappe/LIESMICH.md`.

Seit dem 07.09.2026 ruft `freigabe_pruefen.py` sie selbst auf (Prüfung
*Perl-Syntax*). Anlass: eine Attrappe, die **nachsichtiger** war als das
Original, hat einen echten Fehler acht Fassungen lang verdeckt — sie bildete
weder das `use JSON;` von `LoxBerry::JSON` noch die Prototypen `($)` nach.
Nachsichtig sein darf eine Attrappe bei der Umgebung, nie bei der
Schnittstelle.

`lb_attrappe/` und `lb_leer/` sind zwei winzige LoxBerry-Bäume für den
Prüfstand. Ihre Zugangsdaten sind Attrappen (`geheim123`).

## Seit September dazugekommen

**Gemeinsame Bausteine (`gemeinsam/`).** Ein LoxBerry-Plugin kann keine Datei
eines anderen Plugins laden. Was mehrere Plugins brauchen — die Sprachausgabe
(`sprachausgabe.php` mit `sprachausgabe_texte.json`), der Planer, die
Befehlsbrücke —, liegt deshalb als Stammfassung hier und als byteweise gleiche
Abschrift in jedem Plugin. `gemeinsam_pruefen.py` meldet jede Abschrift, die
von der Stammfassung abweicht; `mutation_sprachausgabe.py` und
`mutation_planer.py` bauen absichtlich Fehler ein und zeigen, dass die
Selbsttests sie finden.

**Sprachdateien.** Die `*_sprache_erzeugen.py` schreiben die Sprachdateien
(`de`/`en`) der Plugins aus einer Quelle; am 06.11.2026 wurden alle an die
veröffentlichten Sprachdateien angeglichen, `ap_sprache_erzeugen.py` und
`ap_hilfe_erzeugen.py` prüfen vor dem Schreiben. `sprachwache.py` passt auf,
dass ein Erzeuger keinen Schlüssel verliert, den die Datei schon führt;
`sprachabbild.py` hält das Schlüssel-Wert-Abbild einer Sprachablage fest und
vergleicht dagegen; `sprachplatzhalter_pruefen.py` zählt, ob Text und
Aufrufstelle dieselbe Zahl von Platzhaltern meinen.

**Minutenlauf.** `minutenlauf_pruefen.py` startet die Cron-Dienste der Plugins
gegen eine LoxBerry-Attrappe mit Broker-Attrappe (`minutenlauf_broker.py`)
und sieht nach, was sie veröffentlichen. Die Angaben je Plugin stehen in
`minutenlauf_linien.json`. Die Prüfstand-Skripte erwarten einen Ordner
`minutenlauf_sdk/` mit den PHP-Bibliotheken eines LoxBerry
(`libs/phplib`); er liegt hier nicht bei und wird von einem eigenen Gerät
kopiert.

**Seiten und Formulare.** `seitenvergleich.py` vergleicht die gerenderte
Oberfläche zweier Fassungen, `wachposten_wirkung.py` schickt Formulare mit
und ohne Formularmerkmal ab und sieht nach, ob der Wachposten wirkt.
`netzsperre.py` sperrt Prüfwerkzeugen, die mit echten Bibliotheken arbeiten,
den Weg ins Netz, damit kein Prüflauf eine Anmeldung bei einem Cloud-Dienst
auslöst.

**Gerät.** `geraet_abbild.py` und `geraetestand_vergleichen.py` lesen über
SSH; sie erwarten einen eingerichteten SSH-Zugang (Vorgabe: Host
`loxberry-claude`), den `loxberry_zugang_einrichten.sh` auf dem LoxBerry
anlegt.

## Was hier **nicht** liegt

`lb/` und `lb_mqtt/` sind Prüfstände mit der Konfiguration einer **laufenden**
Anlage — Aktionstoken, WLAN-Kennwörter, Broker-Zugänge, Fahrzeugnummern. Sie
sind von `.gitignore` gedeckt und gehören auf keinen fremden Rechner. Wer die
Werkzeuge nachbaut, legt sich eigene an.

Ebenso `anonymisierung_woerter.txt`: die Liste der Wörter, die in keiner
Veröffentlichung stehen dürfen. Eine solche Liste im Quelltext trüge genau den
Namen in jede Veröffentlichung, vor dem sie schützen soll. Vorlage:
`anonymisierung_woerter.beispiel.txt`.

Ebenso `hausdatei.txt`: der Kern des Namens der eigenen Projektdatei, den
`leitungen_setzen.py` und `woerterbuch_lernen.py` brauchen (eine Zeile, Form
`Projekt_Name`; ersatzweise in der Umgebungsvariablen `LOX_HAUSDATEI`). Und
`freigabetor_ausnahmen.json`, die eigenen Ausnahmen des Freigabetors; fehlt
sie, gilt keine. Vorlage: `freigabetor_ausnahmen.beispiel.json`.

Ebenso nicht: Werkzeuge, die an Zugang, Räume oder Netz eines bestimmten
Geräts gebunden sind, und fremde Bibliotheken.

## Aufruf

Die meisten Werkzeuge nehmen einen Plugin-Ordner:

```
python3 Werkzeuge/packen.py LoxBerry-Plugin-Beispiel-1.0.0
python3 Werkzeuge/kopfzeilen_pruefen.py LoxBerry-Plugin-Beispiel-1.0.0
```

Der Arbeitsordner ist der Elternordner von `Werkzeuge/`; mit `LOXWERK` lässt
er sich übersteuern. Zugangsschlüssel kommen aus der Umgebung und werden
nirgends in eine Datei geschrieben.

## Lizenz

MIT, siehe `LICENSE`.
