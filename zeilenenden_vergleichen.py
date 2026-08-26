#!/usr/bin/env python3
"""Zeilenenden gegen den belegten Vorzustand halten - keine Regel nach Endung.

Aufruf:
    zeilenenden_vergleichen.py messen  <ordner>
    zeilenenden_vergleichen.py angleichen <alt> <neu>

<alt> ist der belegte Vorzustand: entweder der Ordner der zuletzt
veroeffentlichten Fassung ODER - besser - ihr ZIP-Archiv. Das Archiv liegt
ohnehin im Arbeitsordner, ist unveraenderlich und kann nicht versehentlich
aufgeraeumt werden. Ein entpackter Zwilling daneben ist eine zweite Wahrheit,
die gepflegt werden muss und der niemand ansieht, dass ein Werkzeug sie
braucht.

Binaerdateien (Null-Byte im Inhalt) bleiben aussen vor: die PNG-Symbole
enthalten CR-Bytes als Bilddaten.

Neue Dateien, die es in <alt> nicht gibt, bekommen den Stil ihrer
Nachbarn im selben Verzeichnis; steht der nicht fest, LF.
"""
import sys
from pathlib import Path


def binaer(d):
    return b'\x00' in d


def stil(d):
    crlf = d.count(b'\r\n')
    lf = d.count(b'\n') - crlf
    cr = d.count(b'\r') - crlf
    return crlf, lf, cr


def nach_lf(d):
    return d.replace(b'\r\n', b'\n')


def nach_crlf(d):
    return nach_lf(d).replace(b'\n', b'\r\n')


def dateien(w):
    return sorted(p for p in Path(w).rglob('*') if p.is_file())


def bezug_lesen(alt):
    """Den Vorzustand als {relativer Pfad: Inhalt} - aus Ordner ODER ZIP."""
    alt = Path(alt)
    aus = {}
    if alt.is_file() and alt.suffix.lower() == '.zip':
        import zipfile
        with zipfile.ZipFile(str(alt)) as z:
            namen = [n.replace('\\', '/') for n in z.namelist()
                     if not n.endswith('/')]
            # Ein von GitHub erzeugtes Archiv haengt alles unter EINEN
            # obersten Ordner ("<repo>-<tag>/"); ein lokal gepacktes nicht.
            # Ohne das Abschneiden findet der Vergleich keine einzige Datei
            # wieder, meldet alles als neu und sieht dabei bestanden aus.
            # Abgeschnitten wird NUR, wenn wirklich ALLE Eintraege denselben
            # ersten Pfadteil haben - sonst waere es geraten.
            erste = set(n.split('/')[0] for n in namen if '/' in n)
            alle_tief = all('/' in n for n in namen)
            kuerzen = len(erste) == 1 and alle_tief
            for name in namen:
                schluessel = name.split('/', 1)[1] if kuerzen else name
                aus[schluessel] = z.read(
                    name if '\\' not in name else name.replace('/', '\\'))
        return aus, ('Archiv ' + alt.name
                     + (' (oberster Ordner abgeschnitten)' if kuerzen else ''))
    if alt.is_dir():
        for p in dateien(alt):
            aus[p.relative_to(alt).as_posix()] = p.read_bytes()
        return aus, 'Ordner ' + alt.name
    return {}, str(alt)


def messen(w):
    print('%-46s %6s %6s %6s' % ('Datei', 'CRLF', 'LF', 'CR'))
    for p in dateien(w):
        d = p.read_bytes()
        rel = str(p.relative_to(w)).replace('\\', '/')
        if binaer(d):
            print('%-46s %6s' % (rel, 'binaer'))
            continue
        c, l, r = stil(d)
        print('%-46s %6d %6d %6d' % (rel, c, l, r))


def angleichen(alt, neu):
    alt, neu = Path(alt), Path(neu)
    # FAIL CLOSED: ohne Bezugsordner wird NICHT geraten.
    #
    # Am 19.08.2026 war der Bezugsordner verschwunden. Das Werkzeug hielt
    # daraufhin jede Datei fuer neu, nahm den Stil aus der Nachbarschaft - und
    # stellte sieben CRLF-Dateien auf LF. Ein Werkzeug, das seinen Bezugspunkt
    # verliert und trotzdem weiterarbeitet, ist gefaehrlicher als eines, das
    # gar nicht laeuft.
    bezug, woher = bezug_lesen(alt)
    if len(bezug) == 0:
        print('ABBRUCH: der Bezug %s fehlt oder ist leer.' % alt)
        print('Ohne ihn gibt es keinen belegten Vorzustand - es wird nichts geraten.')
        return 2
    print('Bezug: %s, %d Dateien' % (woher, len(bezug)))

    # ZWEITE WACHE: ein Bezug kann voll sein und trotzdem nicht passen.
    # Die erste Wache oben faengt nur den LEEREN Bezug. Am 20.08.2026 wurde
    # ein GitHub-Archiv uebergeben, dessen Eintraege alle unter einem
    # obersten Ordner lagen: 35 Dateien im Bezug, 35 im Ordner, und KEINE
    # EINZIGE wiedergefunden. Gemeldet wurde "0 angeglichen" - das sah aus
    # wie ein bestandener Vergleich.
    ziel = [p for p in dateien(neu) if not binaer(p.read_bytes())]
    treffer = sum(1 for p in ziel
                  if p.relative_to(neu).as_posix() in bezug)
    if ziel and treffer == 0:
        print('ABBRUCH: der Bezug enthaelt %d Dateien, aber KEINE davon kommt'
              % len(bezug))
        print('im Zielordner vor. Er passt nicht - es wird nichts angeglichen.')
        return 2
    if ziel and treffer < len(ziel) // 2:
        print('ACHTUNG: nur %d von %d Textdateien im Bezug wiedergefunden.'
              % (treffer, len(ziel)))

    geaendert = 0
    neu_dateien = []
    for p in dateien(neu):
        rel = p.relative_to(neu)
        d = p.read_bytes()
        if binaer(d):
            continue
        dv = bezug.get(rel.as_posix())
        if dv is not None:
            if binaer(dv):
                continue
            cv, lv, rv = stil(dv)
            if cv and lv:
                print('WARNUNG: %s war schon gemischt - unangetastet' % rel)
                continue
            soll = 'crlf' if cv else 'lf'
        else:
            neu_dateien.append(rel.as_posix())
            # Nachbarn im selben Verzeichnis des BEZUGS befragen
            ordner = rel.parent.as_posix()
            crlf_n = lf_n = 0
            for name, dq in bezug.items():
                if name.rsplit('/', 1)[0] != ordner and not (ordner == '.' and '/' not in name):
                    continue
                if binaer(dq):
                    continue
                c2, l2, r2 = stil(dq)
                if c2 and not l2:
                    crlf_n += 1
                elif l2 and not c2:
                    lf_n += 1
            soll = 'crlf' if crlf_n > lf_n else 'lf'

        # ERGAENZT 26.08.2026. Der Vorzustand ist ein BELEG, kein Befehl -
        # und in genau einem Fall belegt er einen Fehler.
        #
        # Eine Datei, die mit #! beginnt, startet der Kernel ueber diese
        # Zeile. Steht dort ein CR, sucht er einen Interpreter namens
        # "php\r" und findet ihn nicht: "bad interpreter". Fuer eine solche
        # Datei gibt es keinen Fall, in dem CRLF richtig waere.
        #
        # Anlass: bin/fetch.php in Smartmeter classic war im
        # veroeffentlichten Archiv CRLF - der Cron-Eintrag des klassischen
        # Lesers konnte nie anlaufen. Nach dem Berichtigen auf LF hat dieses
        # Werkzeug die Datei brav wieder auf CRLF gestellt, weil der Beleg
        # es so sagte. Es hat den Fehler also nicht uebersehen, es hat ihn
        # wiederhergestellt.
        if d[:2] == b'#!' and soll == 'crlf':
            print('SHEBANG: %s faengt mit #! an - bleibt LF, auch wenn der '
                  'Bezug CRLF sagt' % str(rel).replace('\\', '/'))
            soll = 'lf'

        d2 = nach_crlf(d) if soll == 'crlf' else nach_lf(d)
        if d2 != d:
            p.write_bytes(d2)
            geaendert += 1
            print('angeglichen auf %-4s : %s' % (soll, str(rel).replace('\\', '/')))
    print()
    if neu_dateien:
        print('Neue Dateien (Stil aus der Nachbarschaft): ' + ', '.join(neu_dateien))
    print('%d Datei(en) angeglichen, %d Dateien angesehen.' % (geaendert, len(dateien(neu))))

    # Schlusskontrolle: keine gemischten Zeilenenden
    schlecht = 0
    for p in dateien(neu):
        d = p.read_bytes()
        if binaer(d):
            continue
        c, l, r = stil(d)
        if c and l:
            print('BEFUND gemischt: %s (%d CRLF, %d LF)' % (p.relative_to(neu), c, l))
            schlecht += 1
        if r:
            print('BEFUND einzelnes CR: %s (%d)' % (p.relative_to(neu), r))
            schlecht += 1
    print('Schlusskontrolle: %d Datei(en) mit gemischten Zeilenenden.' % schlecht)
    return 1 if schlecht else 0


if __name__ == '__main__':
    if sys.argv[1] == 'messen':
        messen(sys.argv[2])
    else:
        sys.exit(angleichen(sys.argv[2], sys.argv[3]))
