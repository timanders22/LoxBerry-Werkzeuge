#!/usr/bin/env python3
"""Den Schluessel des Datenverzeichnisses von 'data' auf 'datadir' umziehen.

Anlass, 28.08.2026: dieselbe Sache heisst in 25 Linien 'datadir' und in 16
'data'. Das kostet bei jeder Aenderung, die mehrere Linien betrifft (siehe
REGELN_2, "Die innere Form eines Plugins").

WARUM DAS KEIN SUCHEN-UND-ERSETZEN IST

  'data' ist ein Allerweltswort. Gemessen ueber die 16 Linien:

      76 Lesestellen  gehoeren zum Pfad-Array      -> umziehen
      13 Lesestellen  sind die ANTWORT einer API   -> stehen lassen

  $d['data']['obtainKrakenToken']['token']   (Spotpreis-Octopus)
  foreach ($d['data'] as $row)               (Spotpreis-aWATTar, MarstekVenus)

  Ein blindes Ersetzen haette in drei Linien den Preisabruf zerlegt - und
  zwar still: die Oberflaeche haette weiter Zahlen gezeigt, die alten.

WIE ENTSCHIEDEN WIRD

  Umgezogen wird NUR, wenn der Zugriff nachweislich am Pfad-Array haengt:
      <pfadfn>()['data']        der Aufruf selbst
      $p['data'] $pfade['data'] und <praefix>_p / <praefix>_pfade
  Jeder andere Zugriff bleibt unberuehrt. Die Zahl der Umzuege wird gegen
  eine ERWARTUNG gehalten, die vorher gemessen wurde - stimmt sie nicht,
  wird nichts geschrieben.

Aufruf:
    datenschluessel_umziehen.py ORDNER PFADFUNKTION ERWARTETE_ANZAHL [--probe]
"""
import glob, os, re, sys

ERLAUBT = r"(?:\$p|\$pfade|\$[a-z]+_p|\$[a-z]+_pfade|%s\(\))"


def lies(p):
    b = open(p, 'rb').read()
    crlf, lf = b.count(b'\r\n'), b.count(b'\n') - b.count(b'\r\n')
    if crlf and lf:
        raise SystemExit('ABBRUCH %s: gemischte Zeilenenden' % p)
    return b.decode('utf-8'), ('\r\n' if crlf else '\n')


def umziehen(ordner, pfadfn, erwartet, probe=False):
    dateien = sorted(glob.glob(os.path.join(ordner, '**', '*.php'), recursive=True))
    if not dateien:
        return 'ABBRUCH: keine PHP-Dateien'

    lese = re.compile(ERLAUBT % re.escape(pfadfn) + r"\['data'\]")
    # Die Zeile, die den Schluessel ANLEGT - nur innerhalb der Pfadfunktion.
    n_def = n_lese = 0
    neu = {}
    for f in dateien:
        t, ende = lies(f)
        o = t

        m = re.search(r'function\s+%s\s*\(' % re.escape(pfadfn), t)
        if m:
            rest = t[m.end():]
            w = re.search(r'\nfunction\s+\w+\s*\(', rest)
            rumpf = rest[:w.start()] if w else rest
            neu_rumpf, k = re.subn(r"'data'(\s*=>)", r"'datadir'\1", rumpf)
            if k:
                t = t[:m.end()] + neu_rumpf + (rest[w.start():] if w else '')
                n_def += k

        t, k = lese.subn(lambda x: x.group(0).replace("['data']", "['datadir']"), t)
        n_lese += k
        if t != o:
            neu[f] = (t, ende)

    gesamt = n_def + n_lese
    if gesamt != erwartet:
        return ('ABBRUCH: %d Stellen (%d Anlage + %d Lesen), erwartet %d - '
                'nichts geschrieben' % (gesamt, n_def, n_lese, erwartet))
    # Zwei Anlagen sind die Regel, nicht die Ausnahme: die Pfadfunktion
    # liefert das Array in zwei Zweigen - installiert und aus dem Paket
    # heraus. Die erste Fassung dieser Zusicherung verlangte genau eine und
    # brach damit bei elf von sechzehn Linien ab. Nicht der Bestand war
    # falsch, sondern die Erwartung.
    if not 1 <= n_def <= 2:
        return 'ABBRUCH: die Anlage des Schluessels wurde %dmal gefunden' % n_def

    if not probe:
        for f, (t, ende) in neu.items():
            aus = ende.join(t.replace('\r\n', '\n').split('\n')).encode('utf-8')
            c = aus.count(b'\r\n'); l = aus.count(b'\n') - c
            assert not (c and l), 'gemischte Zeilenenden entstanden'
            assert (c > 0) == (ende == '\r\n'), 'Zeilenende veraendert'
            open(f, 'wb').write(aus)
    # Was bleibt stehen?
    rest = sum(len(re.findall(r"\['data'\]", lies(f)[0])) for f in dateien) if not probe else -1
    return ('umgezogen: %d Anlage(n) + %d Lesestellen in %d Datei(en); '
            "%s uebrig" % (n_def, n_lese, len(neu),
                           ("%d fremde ['data']" % rest) if rest >= 0 else 'Probe'))


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if x != '--probe']
    if len(a) != 3:
        print(__doc__)
        raise SystemExit(1)
    print(umziehen(a[0], a[1], int(a[2]), '--probe' in sys.argv))
