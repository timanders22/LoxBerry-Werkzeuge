#!/usr/bin/env python3
"""Zeilenenden gegen den belegten Vorzustand halten - und in Plugin-Ordnern auf LF.

Aufruf:
    zeilenenden_vergleichen.py messen  <ordner>
    zeilenenden_vergleichen.py angleichen <alt> <neu> [--probe] [--crlf-erlaubt D[,D...]]

<alt> ist der belegte Vorzustand: entweder der Ordner der zuletzt
veroeffentlichten Fassung ODER - besser - ihr ZIP-Archiv. Das Archiv liegt
ohnehin im Arbeitsordner, ist unveraenderlich und kann nicht versehentlich
aufgeraeumt werden. Ein entpackter Zwilling daneben ist eine zweite Wahrheit,
die gepflegt werden muss und der niemand ansieht, dass ein Werkzeug sie
braucht.

--probe         misst und sagt, was es taete - schreibt nichts.
--crlf-erlaubt  nennt Dateien (Pfad oder Dateiname), die in einem
                Plugin-Ordner ihren bisherigen Stil behalten duerfen - die
                ehrliche Form von "noch nicht dran". Derselbe Schalter und
                dieselbe Auslegung wie in freigabe_pruefen.py.

Binaerdateien (Null-Byte im Inhalt) bleiben aussen vor: die PNG-Symbole
enthalten CR-Bytes als Bilddaten.

ZWEI ORDNUNGEN, UND WELCHE GILT
===============================

IN EINEM PLUGIN-ORDNER (erkannt an plugin.cfg an der Wurzel) fuehrt jede
Textdatei LF. Das ist seit 13.09.2026 eine Entscheidung des Hausherrn
(Regeln/01, Abschnitt 7: "In einem Plugin-Ordner fuehrt jede Textdatei LF;
CRLF ist ab 13.09.2026 ein Befund"). Der Vorzustand ist dort ein BELEG, kein
Befehl: das Werkzeug stellt nie von LF weg, und eine CRLF-Datei stellt es auf
LF - ausser sie steht in --crlf-erlaubt.

BERICHTIGT 16.09.2026. Bis dahin richtete sich jede Datei nach ihrem Stil im
Vorzustand, und damit drehte das Werkzeug jede erledigte Umstellung zurueck:
AWM-Abfuhr 1.4.9 hatte seine drei .cfg auf LF gestellt, dieses Werkzeug machte
daraus wieder CRLF, weil das Archiv von 1.4.8 CRLF trug - still, als
"3 Datei(en) angeglichen". Ueber den Bestand gemessen (neuester Ordner je
Linie gegen sein zuletzt veroeffentlichtes Archiv, auf Kopien): 67 Dateien in
29 von 49 Linien, ALLE von LF nach CRLF. Wer die Kette aus CLAUDE.md
Abschnitt 12 der Reihe nach abarbeitete, drehte damit seine eigene Umstellung
zurueck. packen.py und freigabe_pruefen.py melden eine solche Umstellung laut
und verlangen --zeilenenden-neu; dieses Werkzeug war das einzige, das still
zurueckschrieb.

Die Shebang-Regel vom 26.08.2026 (unten) war derselbe Gedanke fuer eine
einzige Dateiart; die LF-Regel ist ihre Verallgemeinerung auf den ganzen
Plugin-Ordner.

AUSSERHALB EINES PLUGIN-ORDNERS gilt weiter die alte Ordnung: eine Datei
behaelt den Stil, den sie im Vorzustand hat. Dort liegt Fremdgut, das CRLF
braucht - Projektstaende von Loxone Config (*.Loxone), die Vorlagen
VI_*/VO_*/VQU_*/VIU_*/MB_*.xml. Regeln/01 nennt die Liste ausdruecklich:
"Die alte Regel gilt damit noch fuer genau diese Ausnahmen." Gemessen am
16.09.2026: in keinem der 49 Plugin-Ordner liegt eine solche Datei - die
Unterscheidung an plugin.cfg trifft also keine davon.

Neue Dateien, die es in <alt> nicht gibt, bekommen in einem Plugin-Ordner LF;
ausserhalb den Stil ihrer Nachbarn im selben Verzeichnis, steht der nicht
fest, LF.

Wer mit diesem Werkzeug eine Datei auf LF stellt, die im veroeffentlichten
Archiv CRLF traegt, muss sie an packen.py und freigabe_pruefen.py mit
--zeilenenden-neu anmelden (Regeln/01). Das Werkzeug gibt die fertige Liste
dafuer am Ende aus.
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


def erlaubt(rel, liste):
    """Dieselbe Auslegung wie freigabe_pruefen.py: voller Pfad ODER Dateiname."""
    return rel in liste or rel.rsplit('/', 1)[-1] in liste


def angleichen(alt, neu, probe=False, crlf_erlaubt=()):
    alt, neu = Path(alt), Path(neu)
    # FAIL CLOSED: ohne Bezugsordner wird NICHT geraten.
    #
    # Am 19.08.2026 war der Bezugsordner verschwunden. Das Werkzeug hielt
    # daraufhin jede Datei fuer neu, nahm den Stil aus der Nachbarschaft - und
    # stellte sieben CRLF-Dateien auf LF. Ein Werkzeug, das seinen Bezugspunkt
    # verliert und trotzdem weiterarbeitet, ist gefaehrlicher als eines, das
    # gar nicht laeuft.
    #
    # Diese Wache bleibt auch unter der LF-Regel: der Bezug entscheidet dort
    # nicht mehr ueber den Stil, aber er belegt, dass das richtige Paar
    # uebergeben wurde - und er liefert die Liste fuer --zeilenenden-neu.
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

    plugin = (neu / 'plugin.cfg').is_file()
    if plugin:
        print('Ordnung: Plugin-Ordner (plugin.cfg vorhanden) - jede Textdatei LF'
              + (', ausgenommen: %s' % ', '.join(sorted(crlf_erlaubt)) if crlf_erlaubt else ''))
    else:
        print('Ordnung: KEIN Plugin-Ordner - jede Datei behaelt den Stil ihres Vorzustands')
        if crlf_erlaubt:
            print('HINWEIS: --crlf-erlaubt gilt nur in einem Plugin-Ordner und wird hier nicht gebraucht')
    if probe:
        print('PROBE: es wird nichts geschrieben')

    geaendert = 0
    neu_dateien = []
    anmelden = []           # im Bezug CRLF, danach LF -> --zeilenenden-neu
    for p in dateien(neu):
        rel = p.relative_to(neu)
        rel_s = rel.as_posix()
        d = p.read_bytes()
        if binaer(d):
            continue
        dv = bezug.get(rel_s)
        if dv is not None and binaer(dv):
            continue
        if dv is None:
            neu_dateien.append(rel_s)

        if plugin and not erlaubt(rel_s, crlf_erlaubt):
            soll = 'lf'
        elif dv is not None:
            cv, lv, rv = stil(dv)
            if cv and lv:
                print('WARNUNG: %s war schon gemischt - unangetastet' % rel_s)
                continue
            soll = 'crlf' if cv else 'lf'
        else:
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
        #
        # Auch fuer --crlf-erlaubt: eine Shebang-Datei bleibt LF.
        if d[:2] == b'#!' and soll == 'crlf':
            print('SHEBANG: %s faengt mit #! an - bleibt LF, auch wenn der '
                  'Bezug CRLF sagt' % rel_s)
            soll = 'lf'

        d2 = nach_crlf(d) if soll == 'crlf' else nach_lf(d)
        if dv is not None and soll == 'lf' and stil(dv)[0] and not stil(dv)[1]:
            anmelden.append(rel_s)
        if d2 != d:
            if not probe:
                p.write_bytes(d2)
            geaendert += 1
            print('%s auf %-4s : %s' % ('wuerde angleichen' if probe else 'angeglichen',
                                        soll, rel_s))
    print()
    if neu_dateien:
        print('Neue Dateien: ' + ', '.join(neu_dateien))
    print('%d Datei(en) %s, %d Dateien angesehen.'
          % (geaendert, 'waeren anzugleichen' if probe else 'angeglichen', len(dateien(neu))))

    # Die Anmeldeliste fuer die beiden Waechter. Wer das hier auf LF stellt,
    # muss es dort nennen - sonst bricht packen.py ab und das Tor wird rot,
    # und genau an dieser Stelle hat man sich bisher mit 'angleichen'
    # geholfen, das die Umstellung dann zuruecknahm.
    if anmelden:
        print()
        print('Im Bezug CRLF, jetzt LF - an packen.py und freigabe_pruefen.py anmelden:')
        print('    --zeilenenden-neu ' + ','.join(sorted(anmelden)))

    # Schlusskontrolle: keine gemischten Zeilenenden, kein einzelnes CR; in
    # einem Plugin-Ordner ausserdem kein CRLF ausser dem ausdruecklich
    # erlaubten. Unter --probe wird der Zustand NACH dem Angleichen
    # beurteilt, denn geschrieben wurde ja nichts.
    schlecht = 0
    for p in dateien(neu):
        d = p.read_bytes()
        if binaer(d):
            continue
        rel_s = p.relative_to(neu).as_posix()
        if probe:
            d = nach_lf(d) if (plugin and not erlaubt(rel_s, crlf_erlaubt)) else d
        c, l, r = stil(d)
        if c and l:
            print('BEFUND gemischt: %s (%d CRLF, %d LF)' % (rel_s, c, l))
            schlecht += 1
        if r:
            print('BEFUND einzelnes CR: %s (%d)' % (rel_s, r))
            schlecht += 1
        if plugin and c and not l and not erlaubt(rel_s, crlf_erlaubt):
            print('BEFUND CRLF im Plugin-Ordner: %s' % rel_s)
            schlecht += 1
    print('Schlusskontrolle: %d Befund(e) - gemischt, einzelnes CR%s.'
          % (schlecht, ', unerlaubtes CRLF' if plugin else ''))
    return 1 if schlecht else 0


def argumente(argv):
    probe = False
    erlaubt_liste = set()
    rest = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--probe':
            probe = True
        elif a == '--crlf-erlaubt':
            if i + 1 >= len(argv):
                sys.exit('ABBRUCH: --crlf-erlaubt braucht eine Liste von Dateien')
            erlaubt_liste.update(x.strip() for x in argv[i + 1].split(',') if x.strip())
            i += 1
        elif a.startswith('--'):
            sys.exit('ABBRUCH: unbekannter Schalter %s' % a)
        else:
            rest.append(a)
        i += 1
    return rest, probe, erlaubt_liste


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    if sys.argv[1] == 'messen':
        messen(sys.argv[2])
    elif sys.argv[1] == 'angleichen':
        rest, probe, erl = argumente(sys.argv[2:])
        if len(rest) != 2:
            sys.exit('ABBRUCH: angleichen braucht <alt> und <neu>')
        sys.exit(angleichen(rest[0], rest[1], probe, erl))
    else:
        sys.exit('ABBRUCH: unbekannte Betriebsart %s (messen | angleichen)' % sys.argv[1])
