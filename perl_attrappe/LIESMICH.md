# Perl-Attrappe — damit `perl -c` überhaupt urteilen kann

`perl -c` prüft die **Syntax**, muss dafür aber jedes `use`-Modul laden. Im
Arbeitsbereich fehlen die LoxBerry-Module und einige aus CPAN; ohne sie
bricht die Prüfung mit `Can't locate …` ab, **bevor** sie eine einzige Zeile
des Skripts beurteilt hat.

Das ist kein Befund, sondern ein Nichtbefund — und genau so wurde es am
23.08.2026 für KODI-NG und WiFi-Scanner-NG aufgeschrieben: „nicht prüfbar".

Diese Attrappen schließen die Lücke. Aufruf:

    perl -I Werkzeuge/perl_attrappe -c PLUGINORDNER/bin/skript.pl

## Und warum sie an der Schnittstelle nicht NACHSICHTIG sein dürfen

Der Abschnitt oben zeigt die eine Richtung: eine zu magere Attrappe erfindet
Beanstandungen. Am **07.09.2026** kam die andere Richtung dazu — eine zu
nachsichtige **verdeckt** sie.

`fetch_vzlogger.pl` (Smartmeter classic) gab am Gerät bei **jedem** Lauf aus:

    Prototype mismatch: sub main::decode_json ($) vs none
    at /usr/lib/.../Exporter.pm line 63.

Im Cron-Lauf ging das ins Systemprotokoll, bei `--themen` und `--roh` mitten
in die Antwort. Acht Fassungen lang. Gegen die Attrappe kam die Meldung nie.

Der Mechanismus, an der Anlage gelesen: `LoxBerry/JSON.pm` hat in **Zeile 2**
ein `use JSON;`, während `package LoxBerry::JSON;` erst in Zeile 6 kommt. Zum
Zeitpunkt des Imports ist das laufende Paket also noch `main` — `JSON.pm`
(gemessen: 4.10) setzt `encode_json` und `decode_json` mit dem Prototyp `($)`
unmittelbar in den Namensraum des **Aufrufers**. Ein Plugin, das danach noch
`use JSON::PP qw(decode_json)` einbindet, importiert dieselben Namen ohne
Prototyp, und Exporter meldet.

Die Attrappe hatte weder das `use JSON;` an dieser Stelle noch die
Prototypen. Beides ist jetzt nachgetragen und **in beide Richtungen geeicht**:
Smartmeter classic 2.7.2 meldet, 2.8.0 schweigt; über den ganzen Bestand
gemessen ging die Zahl der meldenden Dateien von 0 auf 7, und alle sieben
sind die älteren Ordner derselben Linie. Am Übersetzen änderte sich in keiner
einzigen Datei etwas.

**Die Regel:** nachsichtiger als das Original darf eine Attrappe bei der
**Umgebung** sein, nie bei der **Schnittstelle**. Ein Prototyp, eine
Exportliste und die Stelle, an der ein Modul importiert, gehören zur
Schnittstelle.

Seit demselben Tag ruft `freigabe_pruefen.py` selbst `perl -c` gegen diese
Attrappe (Prüfung *Perl-Syntax*) — und liest dabei die **Ausgabe**, nicht den
Rückgabewert: `perl -c` endet mit 0, obwohl es warnt.

## Warum die Attrappen nicht leer sein dürfen

Ein `package X; 1;` reicht **nicht**. `LoxBerry::Log` exportiert `LOGSTART`,
`LOGINF` und Geschwister mit Prototyp — ohne Deklaration liest Perl
`LOGSTART "text"` als Zeichenkette hinter einem Bareword und meldet einen
*Syntaxfehler, den es nicht gibt*:

    String found where operator expected … (Do you need to predeclare LOGSTART?)

Dasselbe bei `LoxBerry::System`: `$lbplogdir` und Geschwister sind
exportierte Paketvariablen; fehlen sie, meldet `use strict` „Global symbol
requires explicit package name".

Am 25.08.2026 an `wolf_ism8i.pl` gemessen: mit leeren Attrappen elf
Beanstandungen, alle unecht. Mit diesen hier: `syntax OK`.

## Die Grenze, ausdrücklich

Geprüft wird **nur die Syntax**. Ob eine Funktion existiert, ob sie richtig
heißt, ob die Argumente stimmen — davon sieht `perl -c` nichts, und die
Attrappen erst recht nicht. Wer hier `syntax OK` liest, weiß, dass die Datei
sich einlesen lässt. Mehr nicht.

## Beidseitig geeicht

    # muss "syntax OK" sagen
    perl -I Werkzeuge/perl_attrappe -c <plugin>/bin/wolf_ism8i.pl

    # muss den Fehler finden
    sed 's/^use strict;/use strict; my $x = ;/' <datei> > /tmp/kaputt.pl
    perl -I Werkzeuge/perl_attrappe -c /tmp/kaputt.pl

Die zweite Zeile ist die wichtigere: eine Prüfung, die nur „ok" sagen kann,
sagt nichts.

## Nachtrag 26.08.2026: sieben weitere Attrappen

Beim Durchgang über 42 Linien fehlten nacheinander sieben Module. Jedes
Fehlen sah aus wie ein Fehler des Plugins und war keiner — `perl -c` meldet
in beiden Fällen `BEGIN failed--compilation aborted`.

| Modul | aufgefallen bei |
|---|---|
| `CGI` | `KODI-NG/bin/elevatedhelper.pl` |
| `XML::Simple` | `WiFi-Scanner-NG/bin/check.pl` |
| `Config::Simple` | `WiFi-Scanner-NG/bin/mqtt_listener.pl` |
| `JSON` | `WiFi-Scanner-NG/bin/check.pl` |
| `File::HomeDir` | dieselbe Datei, eine Zeile später |
| `Data::Validate::IP` | dieselbe Datei |
| `Capture::Tiny` | dieselbe Datei, Zeile 77 |

**Lehre:** eine Datei gibt ihre fehlenden Module *einzeln* preis — immer nur
das erste. Wer eine Attrappe nachlegt und wieder prüft, bekommt das nächste
Fehlen. Schneller geht es mit

    grep -oE '^\s*use\s+([A-Za-z0-9_:]+)' DATEI | awk '{print $2}' | sort -u \
      | while read -r m; do perl -I Werkzeuge/perl_attrappe -M"$m" -e1 \
          >/dev/null 2>&1 || echo "fehlt: $m"; done

Das nennt **alle** fehlenden auf einmal.

**Nach jeder neuen Attrappe zweimal eichen** — sonst wächst hier eine
Sammlung, die nur noch „ok" sagen kann:

1. ein echter Syntaxfehler muss weiterhin durchschlagen,
2. ein **unbekanntes** Modul muss weiterhin auffallen.

Am 26.08. wurde beides nach jeder Ergänzung geprüft. Beide Zusagen halten.

## Nachtrag 02.10.2026: `LWP::UserAgent` (Werkzeug-P1)

Es kommt darauf an, **welche** Perl prüft. Git-Perl auf dem Arbeitsplatz
bringt libwww mit (`/usr/share/perl5/vendor_perl/LWP/UserAgent.pm`), die Perl
in WSL nicht. Unter WSL brach `perl -c WiFi-Scanner-NG/bin/check.pl` deshalb
mit `Can't locate LWP/UserAgent.pm` ab, und die Prüfung sagte zu der Datei
nichts. Die Attrappe `LWP/UserAgent.pm` exportiert nichts und hat keine
Prototypen (wie das Original); da `-I` sie vor die Systempfade stellt, gilt
sie auch dort, wo libwww installiert ist.

Gemessen über die acht Perl-Dateien des Bestands (je höchste Fassung), unter
Git-Perl und WSL-Perl, alte gegen neue Attrappe: Git-Perl unverändert 8 von 8
ohne Beanstandung; WSL-Perl ändert sich genau eine Zeile (`check.pl`:
`Can't locate LWP/UserAgent.pm` → `syntax OK`). Beide Eichungen gelten unter
beiden Perl: ein eingebauter Syntaxfehler schlägt durch, ein unbekanntes
Modul fällt auf.

## Nachtrag 02.10.2026: `HTML::Entities` (Werkzeug-P2)

Dieselbe Lage bei `WOLF-ISM-NG/bin/wolf_ism8i.pl`: unter WSL-Perl fehlt
HTML::Parser, `perl -c` brach mit `Can't locate HTML/Entities.pm` ab. Die
Attrappe `HTML/Entities.pm` hat die Exportlisten des Originals (gemessen an
Git-Perl, HTML::Entities 3.86): `@EXPORT` = `encode_entities`,
`decode_entities`, `_decode_entities`; `@EXPORT_OK` =
`encode_entities_numeric`, `%entity2char`, `%char2entity`; keine Prototypen.

Gemessen über die acht Perl-Dateien des Bestands (WOLF jetzt 3.1.7): Git-Perl
unverändert ohne Beanstandung; WSL-Perl ändert sich genau eine Zeile
(`wolf_ism8i.pl` → `syntax OK`), danach 0 Beanstandungen. Eichung unter
beiden Perl: Syntaxfehler und unbekanntes Modul schlagen durch; ohne die
neue Datei (Rückbau) ist `wolf_ism8i.pl` unter WSL wieder rot.
