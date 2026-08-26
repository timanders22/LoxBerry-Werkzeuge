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
| `freigabepruefung.py` | Steht ein Geheimnis, eine MAC, eine Netzadresse im Paket? |
| `zeilenenden_vergleichen.py` | Hat eine Datei ihren Zeilenendstil verloren? |
| `linie_veroeffentlichen.sh` | Die vorgeschriebene Reihenfolge in einem Aufruf |

## Attrappen

`perl_attrappe/` enthält Stellvertreter für Module, die `perl -c` laden
möchte (`LoxBerry::System`, `CGI`, `Net::MQTT::Simple`, …). Sie bilden **kein**
Verhalten nach — sie sorgen nur dafür, dass die Syntaxprüfung nicht an einem
fehlenden Modul scheitert und dabei aussieht wie ein Fehler des Plugins.
Näheres in `perl_attrappe/LIESMICH.md`.

`lb_attrappe/` und `lb_leer/` sind zwei winzige LoxBerry-Bäume für den
Prüfstand. Ihre Zugangsdaten sind Attrappen (`geheim123`).

## Was hier **nicht** liegt

`lb/` und `lb_mqtt/` sind Prüfstände mit der Konfiguration einer **laufenden**
Anlage — Aktionstoken, WLAN-Kennwörter, Broker-Zugänge, Fahrzeugnummern. Sie
sind von `.gitignore` gedeckt und gehören auf keinen fremden Rechner. Wer die
Werkzeuge nachbaut, legt sich eigene an.

Ebenso `anonymisierung_woerter.txt`: die Liste der Wörter, die in keiner
Veröffentlichung stehen dürfen. Eine solche Liste im Quelltext trüge genau den
Namen in jede Veröffentlichung, vor dem sie schützen soll. Vorlage:
`anonymisierung_woerter.beispiel.txt`.

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
