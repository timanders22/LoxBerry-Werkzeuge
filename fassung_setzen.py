#!/usr/bin/env python3
"""Die Fassungsnummer an ALLEN Stellen setzen - oder an keiner.

Der Anlass: zweimal hintereinander sind release.cfg und prerelease.cfg eine
Fassung zurueckgeblieben, waehrend plugin.cfg und Ordner schon die neue
trugen. Beim ersten Mal (0.9.8) standen sie auf 0.9.7, beim zweiten (0.9.9)
auf 0.9.8. Beide Male fiel es einem Menschen auf, nicht einem Werkzeug.

Vier Stellen tragen die Nummer, und sie muessen zusammenpassen:

    plugin.cfg       VERSION
    release.cfg      VERSION, ARCHIVEURL, INFOURL
    prerelease.cfg   VERSION, ARCHIVEURL, INFOURL
    README.md        die Kopfzeile "Version X.Y.Z"

Warum die beiden .cfg trotzdem eine Sonderrolle haben: LoxBerry liest
release.cfg aus dem Zweig MASTER, zieht das Archiv aber aus dem TAG. Stehen
sie zu frueh auf der neuen Nummer, bieten sie eine Fassung an, die es als
Tag noch nicht gibt - jede Anlage sieht sie und keine kann sie laden.
Stehen sie zu lange auf der alten, wird die neue Fassung NIE angeboten.
Beides ist stumm.

Deshalb prueft dieses Werkzeug beim Anfassen der beiden .cfg, ob der Tag
schon antwortet, und weigert sich sonst.

Aufruf:
    python3 fassung_setzen.py ORDNER NUMMER
        plugin.cfg und README - immer unbedenklich (Vorbereitung)

    python3 fassung_setzen.py ORDNER NUMMER --auch-release
        zusaetzlich beide .cfg - nur wenn das Tag-Archiv mit 200 antwortet
        (Abschluss nach dem Anlegen des Tags)

    ... --auch-release --trotzdem
        setzt sie auch ohne Tag. Nur sinnvoll, wenn der Tag UNMITTELBAR
        nach dem Schieben angelegt wird; das Werkzeug sagt, was das kostet.

    ... --auch-release --repo KONTO/NAME
        erster Release eines NEUEN Repositories: ARCHIVEURL und INFOURL sind
        dort noch leer, also werden sie aus KONTO/NAME gebaut. Gemessen wird
        genauso - ohne HTTP 200 auf das Tag-Archiv schreibt das Werkzeug
        nichts.

    ... --probe        misst und schreibt nichts
"""
import os
import re
import sys
import urllib.request

# ACHTUNG bei den Mustern unten: diese Dateien sind CRLF. In einem regulaeren
# Ausdruck passt '.' AUCH auf \r, und '$' steht vor dem \n - also VOR dem \r
# nicht. Zwei Fallen daraus, beide am 19.08.2026 beim Bau dieses Werkzeugs
# aufgelaufen:
#   '^VERSION=.+$'   verschluckt das \r und macht die Datei gemischt
#   '\.zip$'          passt bei CRLF ueberhaupt nie - die Ersetzung tut still nichts
# Deshalb ueberall '[^\r\n]*' statt '.+$' und kein '$' am Zeilenende.

argv = sys.argv[1:]
PROBE = '--probe' in argv
AUCH = '--auch-release' in argv
TROTZDEM = '--trotzdem' in argv
# --repo KONTO/NAME: nur fuer den ERSTEN Release eines neuen Repositories.
# Dort ist ARCHIVEURL leer - das ist der von REGELN_4 verlangte Zustand einer
# vorbereiteten Fassung -, und ohne diesen Schalter gaebe es nichts, woraus
# die Tag-Adresse abzuleiten waere. Gemessen wird trotzdem: der Schalter sagt
# nur, WO gemessen wird, nicht DASS nicht gemessen wird.
REPO = None
for i, a in enumerate(argv):
    if a == '--repo' and i + 1 < len(argv):
        REPO = argv[i + 1].strip().strip('/')
    elif a.startswith('--repo='):
        REPO = a.split('=', 1)[1].strip().strip('/')
if REPO is not None:
    if REPO.count('/') != 1 or not all(REPO.split('/')):
        raise SystemExit('ABBRUCH: --repo erwartet KONTO/NAME, bekommen: %r' % REPO)
rest = [a for a in argv if not a.startswith('--')]
rest = [a for a in rest if a != REPO]
if len(rest) < 2:
    print(__doc__)
    sys.exit(1)
ORDNER, NUMMER = rest[0], rest[1]
if not re.match(r'^\d+\.\d+\.\d+$', NUMMER):
    raise SystemExit('ABBRUCH: %r sieht nicht wie X.Y.Z aus' % NUMMER)


def stil(b):
    crlf = b.count(b'\r\n')
    lf = b.count(b'\n') - crlf
    if b.count(b'\r') - crlf:
        return 'einzelne CR!'
    if crlf and lf:
        return 'gemischt!'
    return 'CRLF' if crlf else ('LF' if lf else 'ohne')


def lies(name):
    p = os.path.join(ORDNER, name)
    if not os.path.isfile(p):
        return None, None
    d = open(p, 'rb').read()
    return p, d


def schreibe(p, alt, neu_bytes):
    """Nur schreiben, wenn sich der Stil nicht aendert."""
    if stil(alt) != stil(neu_bytes):
        raise SystemExit('ABBRUCH %s: Zeilenenden %s -> %s'
                         % (os.path.basename(p), stil(alt), stil(neu_bytes)))
    if not PROBE:
        open(p, 'wb').write(neu_bytes)


# ---------- Die README-Kopfzeile ----------
#
# Sie steht nicht in einer festen Form. Gemessen am 25.08.2026 ueber den
# ganzen Bestand kommen drei Sorten vor:
#
#   Version 1.3.0                                  schlicht, Zeile 3
#   Version 0.9.10 . LoxBerry ab 3.0 . PHP 7.4     mit Zusatz
#   > **Version 0.9.15 - ohne Geraet gebaut.**     als Zitat  <- wurde verfehlt
#
# Das alte Muster verlangte "Version" am ZEILENANFANG und fand die dritte
# Sorte nicht. Es meldete dann `README.md ?` und schrieb stillschweigend
# nichts - genau die Klasse, vor der REGELN_4 warnt: eine Ersetzung, die
# nichts trifft, meldet nichts.
#
# ABER: ein einfach erweitertes Muster waere GEFAEHRLICH. Im Bestand stehen
# zwei weitere Sorten, die NICHT angefasst werden duerfen:
#
#   ## Version 3.0.9 - Stoercodes im Klartext      Abschnittsueberschrift
#   Version 0.2.31, Apache-Lizenz 2.0              Fassung eines FREMDEN Autors
#
# Die erste ist der teure Fall: WOLF-ISM-NG 3.0.9 traegt eine Ueberschrift
# mit GENAU der aktuellen Nummer. Ein gieriges Muster haette sie beim
# naechsten Hochsetzen umgeschrieben und damit die Geschichte gefaelscht.
#
# Drei Bedingungen, alle drei noetig:
#   1. im KOPFBEREICH (die ersten 20 Zeilen) - Abschnitte kommen spaeter
#   2. die Zeile beginnt NICHT mit '#' - keine Ueberschrift
#   3. sie steht als EIGENER ABSATZ, die Vorzeile ist leer
#   4. die Zeile nennt die ALTE Fassung aus der plugin.cfg - damit kann
#      kein Fremdverweis und keine andere Nummer getroffen werden
KOPFZEILEN = 20


def readme_kopfzeile(d, alte_fassung):
    """(Zeilennummer, Zeile) der Kopfzeile - oder (None, None).

    Gearbeitet wird auf Bytes, weil die Datei CRLF tragen kann und ein
    Muster ueber CRLF weder '$' noch '.' vertraegt (REGELN_4).
    """
    if not alte_fassung:
        return (None, None)
    ziel = alte_fassung.encode() if isinstance(alte_fassung, str) else alte_fassung
    zeilen = d.split(b'\n')[:KOPFZEILEN]
    muster = rb'(?<![0-9.])Version[ :]+' + re.escape(ziel) + rb'(?![0-9])'
    for i, z in enumerate(zeilen):
        nackt = z.lstrip(b' \t>*_')
        if nackt.startswith(b'#'):
            continue
        # Eine Kopfzeile steht als EIGENER ABSATZ. Bei Ultraschall 1.1.10
        # bricht ein Satz um, und die Folgezeile beginnt mit "Version 0.30
        # aus dem Jahr 2015" - der Fassung des Ursprungsplugins von Dietmar
        # Wimmer. "Beginnt mit Version" reicht also NICHT; die Vorzeile muss
        # leer sein. Gemessen an allen 13 Fassungszeilen des Bestands:
        # zwoelf stehen als Absatz, nur der Fremdverweis nicht.
        if i > 0 and zeilen[i - 1].strip() != b'':
            continue
        if re.search(muster, z):
            return (i + 1, z)
    return (None, None)


# ---------- Was steht jetzt da? ----------
print('== Vorher ==')
stand = {}
for name in ('plugin.cfg', 'release.cfg', 'prerelease.cfg'):
    p, d = lies(name)
    if d is None:
        print('  %-16s fehlt' % name)
        continue
    m = re.search(rb'^VERSION=([^\r\n]*)', d, re.M)
    stand[name] = (p, d, m.group(1).decode().strip() if m else None)
    print('  %-16s %-8s %s' % (name, stand[name][2] or '?', stil(d)))

# Die README erst NACH der plugin.cfg - ihre Kopfzeile wird an der alten
# Fassung erkannt, und die steht dort.
p, d = lies('README.md')
if d is None:
    print('  %-16s fehlt' % 'README.md')
else:
    alt_cfg = stand.get('plugin.cfg', (None, None, None))[2]
    nr, zeile = readme_kopfzeile(d, alt_cfg)
    stand['README.md'] = (p, d, alt_cfg if nr else None)
    if nr:
        print('  %-16s %-8s %s  (Kopfzeile, Zeile %d)'
              % ('README.md', alt_cfg, stil(d), nr))
    else:
        # Nennt die README ueberhaupt IRGENDEINE Fassung im Kopf? Wenn ja,
        # weicht sie von der plugin.cfg ab - das ist ein Befund, kein '?'.
        andere = None
        for i, z in enumerate(d.split(b'\n')[:KOPFZEILEN]):
            if z.lstrip(b' \t>*_').startswith(b'#'):
                continue
            m2 = re.search(rb'(?<![0-9.])Version[ :]+([0-9]+\.[0-9][0-9.]*)', z)
            if m2:
                andere = (i + 1, m2.group(1).decode())
                break
        if andere:
            # KEIN Automatismus daraus: die Zeile kann auch ein Verweis auf
            # eine FREMDE Fassung sein. Bei Ultraschall 1.1.10 steht im Kopf
            # "Version 0.30 aus dem Jahr 2015" - die Fassung des
            # Ursprungsplugins von Dietmar Wimmer. Deshalb wird hier
            # gemeldet und nicht geschrieben.
            print('  %-16s %-8s %s  <== ANSEHEN: Zeile %d nennt %s, plugin.cfg '
                  'nennt %s (Kopfzeile veraltet? oder Verweis auf eine fremde '
                  'Fassung?)'
                  % ('README.md', andere[1], stil(d), andere[0], andere[1], alt_cfg))
            stand['README.md'] = (p, d, None)
        else:
            print('  %-16s %-8s %s  (keine Fassungszeile im Kopf - nichts zu tun)'
                  % ('README.md', '--', stil(d)))
            stand['README.md'] = (p, d, False)

if 'plugin.cfg' not in stand:
    raise SystemExit('ABBRUCH: keine plugin.cfg in %s' % ORDNER)

# ---------- Das Tag pruefen, bevor die beiden .cfg angefasst werden ----------
tag_da = None
if AUCH:
    url = None
    if 'release.cfg' in stand:
        m = re.search(rb'^ARCHIVEURL=([^\r\n]*)', stand['release.cfg'][1], re.M)
        if m and m.group(1).strip():
            url = re.sub(r'v[0-9.]+\.zip$', 'v%s.zip' % NUMMER, m.group(1).decode().strip())
    if not url and REPO:
        # Erster Release: die Adresse steht noch nirgends, also wird sie
        # gebaut - und danach genauso gemessen wie jede andere.
        url = ('https://github.com/%s/archive/refs/tags/v%s.zip' % (REPO, NUMMER))
        print('\n  Adresse aus --repo gebaut (erster Release): %s' % url)
    print('\n== Gibt es den Tag schon? ==')
    if not url:
        print('  keine ARCHIVEURL gefunden - nicht pruefbar.')
        print('  Ist das der ERSTE Release eines neuen Repositories, fehlt')
        print('  --repo KONTO/NAME. Ohne Adresse wird nichts gemessen und')
        print('  nichts geschrieben - das ist die richtige Reihenfolge, nicht')
        print('  ein Fehler dieses Werkzeugs.')
    else:
        try:
            with urllib.request.urlopen(url, timeout=25) as a:
                tag_da = (a.getcode() == 200)
                laenge = len(a.read())
            print('  v%s  HTTP 200, %d Byte' % (NUMMER, laenge))
        except Exception as e:
            tag_da = False
            print('  v%s  %s' % (NUMMER, e))
    if not tag_da and not TROTZDEM:
        print('\nABBRUCH: release.cfg und prerelease.cfg werden NICHT gesetzt.')
        print('  Der Tag v%s antwortet nicht. Wuerden sie jetzt nach master' % NUMMER)
        print('  geschoben, boeten sie jeder Anlage eine Fassung an, die es')
        print('  nicht gibt - und zwar stumm.')
        print('  Erst den Tag anlegen, dann diesen Aufruf wiederholen.')
        print('  Wer Schieben und Taggen unmittelbar nacheinander macht,')
        print('  nimmt --trotzdem und traegt das kurze Fenster bewusst.')
        sys.exit(1)
    if not tag_da and TROTZDEM:
        print('\n  --trotzdem: die beiden .cfg werden gesetzt, OBWOHL der Tag fehlt.')
        print('  Ab dem Schieben nach master bietet LoxBerry v%s an und kann' % NUMMER)
        print('  es nicht laden, bis der Tag steht. Das Fenster gehoert in')
        print('  Sekunden gemessen, nicht in Minuten.')

# ---------- Setzen ----------
print('\n== %s ==' % ('Probe - es wird nichts geschrieben' if PROBE else 'Setzen'))
geaendert = []

p, d, alt = stand['plugin.cfg']
neu = re.sub(rb'^VERSION=[^\r\n]*', ('VERSION=%s' % NUMMER).encode(), d, count=1, flags=re.M)
if neu != d:
    schreibe(p, d, neu)
    geaendert.append('plugin.cfg  %s -> %s' % (alt, NUMMER))

if 'README.md' in stand and stand['README.md'][2]:
    p, d, alt = stand['README.md']
    nr, zeile = readme_kopfzeile(d, alt)
    if nr:
        # NUR diese eine Zeile anfassen, und darin nur die Nummer. Der Rest
        # der Zeile ("- ohne Geraet gebaut", "· LoxBerry ab 3.0") bleibt.
        neu_zeile = re.sub(rb'(Version[ :]+)' + re.escape(alt.encode()),
                           rb'\g<1>' + NUMMER.encode(), zeile, count=1)
        if neu_zeile != zeile:
            neu = d.replace(zeile, neu_zeile, 1)
            schreibe(p, d, neu)
            geaendert.append('README.md   %s -> %s  (Zeile %d)' % (alt, NUMMER, nr))
        elif alt != NUMMER:
            # Eine Ersetzung, die nichts trifft, meldet sonst nichts - ausser
            # wenn gar nichts zu tun war. Diesen Unterschied hat der erste
            # Anlauf nicht gemacht: er brach ab, wenn jemand dieselbe Nummer
            # noch einmal setzte. Nichts zu tun ist kein Fehler.
            raise SystemExit('ABBRUCH README.md: die Kopfzeile in Zeile %d liess '
                             'sich nicht von %s auf %s setzen' % (nr, alt, NUMMER))

if AUCH:
    for name in ('release.cfg', 'prerelease.cfg'):
        if name not in stand:
            continue
        p, d, alt = stand[name]
        neu = re.sub(rb'^VERSION=[^\r\n]*', ('VERSION=%s' % NUMMER).encode(), d, count=1, flags=re.M)
        neu = re.sub(rb'(^ARCHIVEURL=.*/tags/)v[0-9.]+\.zip',
                     lambda m: m.group(1) + ('v%s.zip' % NUMMER).encode(), neu, count=1, flags=re.M)
        neu = re.sub(rb'(^INFOURL=.*/tag/)v[0-9.]+',
                     lambda m: m.group(1) + ('v%s' % NUMMER).encode(), neu, count=1, flags=re.M)
        if REPO:
            # Beim ersten Release stehen die Felder LEER da. Gefuellt wird nur,
            # was leer ist - eine vorhandene Adresse gehoert einem anderen
            # Repository und wird nicht ueberschrieben, auch nicht "zur
            # Sicherheit".
            neu = re.sub(rb'^ARCHIVEURL=(?=[\r\n])',
                         ('ARCHIVEURL=https://github.com/%s/archive/refs/tags/v%s.zip'
                          % (REPO, NUMMER)).encode(), neu, count=1, flags=re.M)
            neu = re.sub(rb'^INFOURL=(?=[\r\n])',
                         ('INFOURL=https://github.com/%s/releases/tag/v%s'
                          % (REPO, NUMMER)).encode(), neu, count=1, flags=re.M)
        if neu != d:
            schreibe(p, d, neu)
            geaendert.append('%-12s %s -> %s  (mit beiden Adressen)' % (name, alt, NUMMER))

for g in geaendert:
    print('  ' + g)
if not geaendert:
    print('  nichts zu tun - alles steht schon auf %s' % NUMMER)

# ---------- Nachzaehlen ----------
if not PROBE and geaendert:
    print('\n== Nachher, gelesen ==')
    for name in ('plugin.cfg', 'release.cfg', 'prerelease.cfg', 'README.md'):
        p, d = lies(name)
        if d is None:
            continue
        if name == 'README.md':
            nr, _z = readme_kopfzeile(d, NUMMER)
            print('  %-16s %-8s %s%s'
                  % (name, NUMMER if nr else '--', stil(d),
                     '' if nr else '  (keine Fassungszeile im Kopf)'))
            continue
        m = re.search(rb'^VERSION=([^\r\n]*)', d, re.M)
        print('  %-16s %-8s %s' % (name, m.group(1).decode().strip() if m else '?', stil(d)))
    if AUCH:
        for name in ('release.cfg', 'prerelease.cfg'):
            p, d = lies(name)
            for feld in (b'ARCHIVEURL', b'INFOURL'):
                m = re.search(feld + rb'=([^\r\n]*)', d, re.M)
                if m and NUMMER.encode() not in m.group(1):
                    raise SystemExit('ABBRUCH %s: %s nennt nicht v%s'
                                     % (name, feld.decode(), NUMMER))
        print('  beide Adressen in beiden .cfg nennen v%s' % NUMMER)

if AUCH and not PROBE:
    print('\n  Gegenprobe empfohlen:  python3 Werkzeuge/fassungslage.py %s' % ORDNER)
