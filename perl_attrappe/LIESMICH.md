# Perl-Attrappe — damit `perl -c` überhaupt urteilen kann

`perl -c` prüft die **Syntax**, muss dafür aber jedes `use`-Modul laden. Im
Arbeitsbereich fehlen die LoxBerry-Module und einige aus CPAN; ohne sie
bricht die Prüfung mit `Can't locate …` ab, **bevor** sie eine einzige Zeile
des Skripts beurteilt hat.

Das ist kein Befund, sondern ein Nichtbefund — und genau so wurde es am
23.08.2026 für KODI-NG und WiFi-Scanner-NG aufgeschrieben: „nicht prüfbar".

Diese Attrappen schließen die Lücke. Aufruf:

    perl -I Werkzeuge/perl_attrappe -c PLUGINORDNER/bin/skript.pl

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
