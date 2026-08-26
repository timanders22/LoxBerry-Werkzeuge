#!/usr/bin/env python3
"""Sucht die Zweideutigkeit im Loxone-Suchtext: \\iNAME= statt \\i;NAME=.

DER BEFUND, der dieses Werkzeug ausgeloest hat (20.08.2026, Volkswagen ID und
Skoda Connect): der virtuelle Eingang fuer KM trug den Suchtext \\iKM=\\i\\v.
Die Antwort des Wartungs-Abrufs lautet

    WARTUNG;OK=1;INSPTAGE=..;INSPKM=15000;OELTAGE=..;OELKM=..;KM=48210;ALTER=..

Loxone nimmt die ERSTE Fundstelle - und das ist INSPKM=. Der Kilometerstand las
damit die Inspektionsvorgabe: 15000 statt 48210. Beide Zahlen sehen aus wie ein
Kilometerstand; der Fehler meldet sich nie.

WAS DIESES WERKZEUG MISST

Nicht "fehlt das Semikolon" - das allein ist harmlos, solange kein Feldname
Endstueck eines anderen ist. Gemessen wird die WIRKUNG:

 1. Welche Suchtexte nennt das Plugin?  (\\i NAME = \\i \\v, mit oder ohne
    Trennzeichen davor)
 2. Welche Antwortzeilen gibt der Endpunkt aus?  Gesucht werden
    Zeichenkettenliterale, in denen mindestens zwei Felder der Form NAME=
    durch Semikolon getrennt stehen - das ist die Gestalt jeder Antwortzeile
    dieser Reihe.
 3. Fuer jeden Suchtext OHNE Trennzeichen: kommt der Name in einer dieser
    Zeilen als ENDSTUECK eines anderen Namens vor? Dann trifft der Suchtext
    dort zuerst das falsche Feld.

Vier Befundstufen, und sie werden auseinandergehalten:

    TRIFFT FALSCH   ein Suchtext ohne Trennzeichen, und in derselben
                    Antwortzeile steht ein laengerer Name, der auf ihn endet.
                    Das ist der Fehler - er wirkt heute.
    ABSCHRIFT       der Quelltext baut den Suchtext MIT Trennzeichen, aber
    WEICHT AB       eine Sprach- oder Vorlagendatei zeigt ihn ohne. Der
                    Anwender liest die Abschrift, nicht den Quelltext.
    RISIKO          Suchtexte ohne Trennzeichen, aber heute kein Namenspaar,
                    das kollidiert. Faellt beim naechsten neuen Feld an.
    IN ORDNUNG      alle Suchtexte tragen ein Trennzeichen.

Eine Warnung, die zwischen "wirkt heute" und "koennte einmal" nicht
unterscheidet, wird nach dem dritten Mal nicht mehr gelesen.

WO GESUCHT WIRD - und warum genau dort

    *.php                      der Quelltext, der den Suchtext BAUT
    templates/lang/*.ini       die Sprachdateien, die ihn ZEIGEN
    templates/**/*.html        die Hilfe und die Vorlagen, die ihn ZEIGEN

ERWEITERT am 20.08.2026, nach Befund an FerienFeiertage 1.2.1: dort baute
fer_check() den Suchtext seit der Umstellung mit Trennzeichen - in
language_de.ini und language_en.ini standen aber weiterhin 54 Schluessel der
Form ISCHULTAG_I_V = "\\iSCHULTAG=\\i\\v", also die alte Gestalt. Das Werkzeug
las nur .php und meldete "alle 1 Suchtexte tragen das Trennzeichen".

Ueber den ganzen Bestand gemessen: 54 .ini-Dateien in 26 Linien tragen
Suchtexte. Das war keine Eigenheit einer Linie, sondern ein blinder Fleck.

NICHT gesucht wird in *.md. Dort steht die BESCHREIBUNG - und wer eine
Umstellung erklaert, schreibt die alte Gestalt zwangslaeufig hin ("bis 1.2.0
lautete er \\iNAME=\\i\\v"). Ein Sucher, der das als Fund meldet, bestraft
genau die Sorgfalt, die er befoerdern soll.

GRENZEN, und sie gehoeren zum Ergebnis

 * Gelesen wird der QUELLTEXT, nicht eine erzeugte Antwort. Ein Feld, das
   erst zur Laufzeit in die Zeile kommt, ist hier nicht zu sehen.
 * Nur Antwortzeilen in der Gestalt "A=..;B=.." werden erkannt. Ein Plugin,
   das seine Werte anders ausgibt (JSON, MQTT, eine Zeile je Feld), erscheint
   mit "keine Antwortzeile gefunden" - das ist KEIN Freispruch, sondern die
   Aussage, dass hier nichts zu messen war.
 * Fundstellen in KOMMENTAREN werden erkannt und getrennt gezaehlt, aber
   nicht als Befund gewertet. Eine Zeile gilt als Kommentar, wenn sie mit
   *, /*, // oder # beginnt (in .ini auch ; und #). Ein Suchtext, der hinter
   Code auf derselben Zeile im Kommentar steht, faellt durch diese Regel.
 * Rein lesend.

Aufruf:
    suchmuster_pruefen.py                  alle LoxBerry-Plugin-* im Ordner
    suchmuster_pruefen.py PLUGINORDNER     einer
    suchmuster_pruefen.py --nur-befunde    nur Linien mit Befund
    suchmuster_pruefen.py --roh            jede Fundstelle einzeln auflisten
"""
import re
import sys
from pathlib import Path

# Der Suchtext, wie ihn diese Reihe baut: \i  NAME  =  \i \v  - entweder
# woertlich oder mit dem Namen aus einer Variablen.
#
# BERICHTIGT am 20.08.2026: hier stand (.?) - "das Zeichen vor dem Namen,
# was immer es ist". Ohne Trennzeichen frass diese Gruppe den ERSTEN
# BUCHSTABEN des Namens: aus \iKM=\i\v wurde Trenner='K', Name='M', aus
# \iSCHULTAG=\i\v wurde Name='CHULTAG'. Damit stand in namen_ohne nie der
# wirkliche Feldname, und die Kollisionspruefung konnte nur ueber den
# Umweg 'variabel' anschlagen. Der Trenner ist ein Semikolon oder er ist
# nicht da - also (;?).
MUSTER_WOERTLICH = re.compile(r"\\i(;?)([A-Z][A-Z0-9_]{0,19})=\\i\\v")
MUSTER_VARIABEL = re.compile(
    r"'\\i(;?)'\s*\.\s*\$[A-Za-z_][A-Za-z0-9_]*\s*\.\s*'=\\i\\v'")
# Dasselbe in der Oberflaeche, wo der Name aus PHP kommt:
#   \i<?= xx_e($feld) ?>=\i\v
MUSTER_VORLAGE = re.compile(r"\\i(;?)<\?=[^?]*\?>=\\i\\v")

# Eine Antwortzeile: mindestens zwei Felder NAME=, durch Semikolon getrennt.
# Gesucht wird in Zeichenkettenliteralen - printf-Vorlagen eingeschlossen.
MUSTER_ZEILE = re.compile(r"[A-Z][A-Z0-9_]*=[^\"';]*;[A-Z][A-Z0-9_]*=")
MUSTER_FELD_IN_ZEILE = re.compile(r"(?:^|[;\"'])([A-Z][A-Z0-9_]{0,19})=")

TRENNER = ';'

# Welche Dateien gelesen werden - und unter welcher Herkunft sie zaehlen.
# 'baut'  = der Quelltext erzeugt den Suchtext
# 'zeigt' = eine Datei stellt ihn dem Anwender zum Abschreiben hin
HERKUNFT = (
    ('**/*.php', 'baut'),
    ('templates/lang/*.ini', 'zeigt'),
    ('templates/**/*.html', 'zeigt'),
)

KOMMENTAR_PHP = re.compile(r'^\s*(\*|/\*|//|#)')
KOMMENTAR_INI = re.compile(r'^\s*(;|#)')


def dateien(ordner: Path):
    """Rueckgabe: Liste von (Pfad, Herkunft). Ohne Dubletten."""
    aus, gesehen = [], set()
    for muster, herkunft in HERKUNFT:
        for p in sorted(ordner.glob(muster)):
            if p.is_file() and p not in gesehen:
                gesehen.add(p)
                aus.append((p, herkunft))
    return aus


def ist_kommentar(pfad: Path, zeile: str) -> bool:
    if pfad.suffix.lower() == '.ini':
        return bool(KOMMENTAR_INI.match(zeile))
    if pfad.suffix.lower() == '.php':
        return bool(KOMMENTAR_PHP.match(zeile))
    return False


def suchtexte(ordner: Path):
    """Rueckgabe: Liste von Fundstellen als dict."""
    aus = []
    for f, herkunft in dateien(ordner):
        try:
            text = f.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        for nr, zeile in enumerate(text.splitlines(), 1):
            komm = ist_kommentar(f, zeile)
            treffer = []
            for m in MUSTER_VARIABEL.finditer(zeile):
                treffer.append((m.group(1), 'variabel'))
            for m in MUSTER_VORLAGE.finditer(zeile):
                treffer.append((m.group(1), 'vorlage'))
            for m in MUSTER_WOERTLICH.finditer(zeile):
                treffer.append((m.group(1), m.group(2)))
            for trenner, name in treffer:
                aus.append({'datei': f, 'nr': nr, 'trenner': trenner,
                            'name': name, 'herkunft': herkunft,
                            'kommentar': komm})
    return aus


def antwortzeilen(ordner: Path):
    """Rueckgabe: Liste von (datei, zeilennummer, [Feldnamen]).

    Nur aus .php - die Antwortzeile entsteht im Quelltext.
    """
    aus = []
    for f in sorted(ordner.rglob('*.php')):
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        for nr, zeile in enumerate(text.splitlines(), 1):
            if not MUSTER_ZEILE.search(zeile):
                continue
            felder = MUSTER_FELD_IN_ZEILE.findall(zeile)
            if len(felder) >= 2:
                aus.append((f, nr, felder))
    return aus


def zusammenhaengen(zeilen):
    """Antwortzeilen ueber mehrere Quellzeilen zusammenfassen.

    Eine printf-Vorlage steht oft ueber zwei oder drei Quellzeilen, mit '.'
    verbunden. Zeilen, die in derselben Datei direkt aufeinander folgen,
    gehoeren deshalb zu EINER Antwort - und nur innerhalb einer Antwort ist
    eine Verwechslung moeglich.
    """
    aus = []
    for f, nr, felder in zeilen:
        if aus and aus[-1][0] == f and nr - aus[-1][1] <= 2:
            aus[-1] = (f, nr, aus[-1][2] + felder)
        else:
            aus.append((f, nr, list(felder)))
    return aus


def pruefen(ordner: Path):
    alle = suchtexte(ordner)
    if not alle:
        return None
    muster = [m for m in alle if not m['kommentar']]
    kommentare = [m for m in alle if m['kommentar']]
    ohne = [m for m in muster if m['trenner'] != TRENNER]
    zeilen = zusammenhaengen(antwortzeilen(ordner))

    # Die Kollision: ein Name, der Endstueck eines LAENGEREN Namens in
    # DERSELBEN Antwortzeile ist - und der laengere steht davor.
    treffer = []
    for f, nr, felder in zeilen:
        for kurz in sorted(set(felder)):
            for lang in felder:
                if lang != kurz and lang.endswith(kurz):
                    # Reihenfolge zaehlt: Loxone nimmt die erste Fundstelle.
                    zuerst = felder.index(lang) < felder.index(kurz)
                    treffer.append((f, nr, kurz, lang, zuerst))
    return {
        'muster': muster,
        'kommentare': kommentare,
        'ohne_trenner': ohne,
        'zeilen': zeilen,
        'kollisionen': treffer,
    }


def kurz(pfad: Path, ordner: Path) -> str:
    try:
        return pfad.relative_to(ordner).as_posix()
    except ValueError:
        return pfad.name


def bericht(ordner: Path, nur_befunde: bool, roh: bool) -> int:
    e = pruefen(ordner)
    if e is None:
        if not nur_befunde:
            print('%-46s kein Suchtext dieser Gestalt - entfaellt' % ordner.name)
        return 0

    ohne = e['ohne_trenner']
    if roh:
        for m in e['muster'] + e['kommentare']:
            print('        %-7s %-5s %-9s %s:%d  %s'
                  % (m['herkunft'], 'komm' if m['kommentar'] else '',
                     m['name'], kurz(m['datei'], ordner), m['nr'],
                     'mit ;' if m['trenner'] == TRENNER else 'OHNE ;'))

    zusatz = (''
              if not e['kommentare']
              else '  (+%d in Kommentaren, nicht gewertet)' % len(e['kommentare']))

    if not ohne:
        if not nur_befunde:
            print('%-46s [ok  ] alle %d Suchtexte tragen das Trennzeichen%s'
                  % (ordner.name, len(e['muster']), zusatz))
        return 0

    # Nur Kollisionen, deren kurzer Name auch WIRKLICH als Suchtext ohne
    # Trennzeichen gebaut wird. Alles andere ist Theorie.
    namen_ohne = set(m['name'] for m in ohne
                     if m['name'] not in ('variabel', 'vorlage'))
    variabel = any(m['name'] in ('variabel', 'vorlage') for m in ohne)
    echt = [k for k in e['kollisionen']
            if k[4] and (variabel or k[2] in namen_ohne)]

    if echt:
        print('%-46s [FEHL] TRIFFT FALSCH' % ordner.name)
        gesehen = set()
        for f, nr, k, lang, _ in echt:
            if (k, lang) in gesehen:
                continue
            gesehen.add((k, lang))
            print('        %s trifft zuerst %s (%s:%d)'
                  % (k, lang, kurz(f, ordner), nr))
        print('        %d Suchtexte ohne Trennzeichen, %d Antwortzeilen gelesen%s'
              % (len(ohne), len(e['zeilen']), zusatz))
        return 1

    # Weicht die Abschrift vom Quelltext ab? Das ist der FerienFeiertage-Fall:
    # der Quelltext ist umgestellt, die Sprachdatei nicht. Wer die Oberflaeche
    # abschreibt, traegt den alten Suchtext ein.
    baut_mit = [m for m in e['muster']
                if m['herkunft'] == 'baut' and m['trenner'] == TRENNER]
    zeigt_ohne = [m for m in ohne if m['herkunft'] == 'zeigt']
    baut_ohne = [m for m in ohne if m['herkunft'] == 'baut']
    if baut_mit and zeigt_ohne and not baut_ohne:
        print('%-46s [ABW ] ABSCHRIFT WEICHT AB: der Quelltext stellt %d mal '
              'mit Trennzeichen her,' % (ordner.name, len(baut_mit)))
        dateien_ = sorted(set(kurz(m['datei'], ordner) for m in zeigt_ohne))
        print('        %d Fundstellen ohne Trennzeichen zeigen ihn aber an: %s'
              % (len(zeigt_ohne), ', '.join(dateien_)))
        print('        Wer die Oberflaeche abschreibt, traegt den alten '
              'Suchtext ein.%s' % zusatz)
        return 1

    if not nur_befunde:
        woher = ''
        if zeigt_ohne and baut_ohne:
            woher = ' (%d im Quelltext, %d in Text- und Sprachdateien)' % (
                len(baut_ohne), len(zeigt_ohne))
        elif zeigt_ohne:
            woher = ' (alle in Text- und Sprachdateien)'
        print('%-46s [hinw] RISIKO: %d Suchtexte ohne Trennzeichen%s, heute '
              'kein Namenspaar, das kollidiert%s%s'
              % (ordner.name, len(ohne), woher,
                 '' if e['zeilen'] else ' (keine Antwortzeile gefunden - hier war nichts zu messen)',
                 zusatz))
    return 0


def main() -> int:
    argv = [a for a in sys.argv[1:] if not a.startswith('--')]
    nur_befunde = '--nur-befunde' in sys.argv
    roh = '--roh' in sys.argv
    if argv:
        ziele = [Path(a).resolve() for a in argv]
    else:
        ziele = sorted(p for p in Path('.').iterdir()
                       if p.is_dir() and p.name.startswith('LoxBerry-Plugin-'))
    if not ziele:
        print(__doc__)
        return 2

    fehl = 0
    for z in ziele:
        if not (z / 'webfrontend').is_dir():
            print('%-46s kein webfrontend/ - uebersprungen' % z.name)
            continue
        fehl += bericht(z, nur_befunde, roh)
    print('')
    print('%d von %d Linien mit einem Befund (TRIFFT FALSCH oder ABSCHRIFT '
          'WEICHT AB).' % (fehl, len(ziele)))
    print('Gemessen am Quelltext, an den Sprachdateien und an den Vorlagen -')
    print('nicht an einer erzeugten Antwort. Die Grenzen stehen im Kopf')
    print('dieser Datei.')
    return 1 if fehl else 0


if __name__ == '__main__':
    sys.exit(main())
