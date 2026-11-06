#!/usr/bin/env python3
"""Ein Plugin packen - und dabei Name, Ordner und plugin.cfg aneinander binden.

Der Anlass, 19.08.2026: das Archiv ist an einem Tag zweimal aus dem Tritt
geraten. Einmal lag ein 0.9.8.zip mit 434 690 Byte neben einem
veroeffentlichten 0.9.8 mit 432 578 - dieselbe Nummer, zwei Staende. Einmal
war das Archiv aelter als der Ordner, weil nach dem Packen noch etwas
geaendert wurde.

Beides kommt daher, dass Ordnername, Archivname und plugin.cfg drei
unabhaengige Angaben waren. Dieses Werkzeug macht daraus eine:

  * der Ordner MUSS auf die Fassung aus seiner plugin.cfg enden
  * das Archiv heisst wie der Ordner
  * nach dem Packen wird jede Datei BYTEWEISE zurueckverglichen

Zusaetzlich, wenn eine Grundlinie angegeben ist: jede Datei muss den
Zeilenendstil behalten, den sie in der zuletzt VEROEFFENTLICHTEN Fassung
hatte.

UND DIE DATEIRECHTE, seit dem 28.08.2026
----------------------------------------
Bis dahin entstand jeder Eintrag als blankes zipfile.ZipInfo. CPythons
writestr() stempelt darauf 0o600 - auf Dateien UND auf Verzeichnisse.
Ein Verzeichnis ohne x-Bit laesst sich nicht betreten; unzip legt es als
drw------- an. Und plugininstall.pl kopiert NICHT als root, sondern mit
"sudo -n -u loxberry cp -r -v" (Zeilen 939, 958, 1002, 1062, 1080, 1097).

Die Wirkung stand am 28.08.2026 im Installationsprotokoll einer Anlage:
jede Datei in einem Unterverzeichnis scheiterte mit
"cp: cannot stat ...: Permission denied", die oberste Ebene ging durch,
und am Ende meldete der Installer trotzdem "ALLES ERLEDIGT". Das Plugin
war danach nicht mehr auf dem Geraet - die alte Installation hatte der
Installer da schon entfernt.

Betroffen waren ALLE 25 Archive im Arbeitsordner. Die Archive der
GitHub-Tags nicht: sie tragen DOS-Attribute, und dann nimmt unzip die
umask.

Geeicht in beide Richtungen (drei Bauformen, entpackt unter Linux):
    blankes ZipInfo   drw-------   cp: Permission denied
    mit Rechten       drwxr-xr-x   cp: geht
    Zeichenkette      drwxrwxr-x   cp: geht

Aufruf:
    python3 packen.py PLUGINORDNER [--grundlinie VEROEFFENTLICHT.zip] [--probe]
                      [--zeilenenden-neu DATEI[,DATEI...]]

--zeilenenden-neu nennt Dateien, deren Zeilenendstil sich gegenueber der
Grundlinie AENDERN darf - namentlich, mit dem Pfad wie im Archiv. Alles
Uebrige bleibt geschuetzt, und die Ausnahme steht im Bericht. Ohne den
Schalter bricht jede Stilaenderung ab; das ist der Normalfall und hat
fuenfmal eine versehentliche Umstellung gefangen.
"""
import fnmatch
import hashlib
import os
import re
import sys
import zipfile

argv = sys.argv[1:]

# Ein unbekannter Schalter darf nicht ARBEITEN. Am 28.08.2026 wurde dieses
# Werkzeug mit --pruefen aufgerufen (es heisst --probe); es hat den Schalter
# stillschweigend uebergangen und gepackt, wo nur gemessen werden sollte.
BEKANNT = ('--probe', '--grundlinie', '--zeilenenden-neu')
unbekannt = [a for a in argv if a.startswith('--') and a not in BEKANNT]
if unbekannt:
    sys.stderr.write('ABBRUCH: unbekannte(r) Schalter %s - bekannt sind %s\n'
                     % (', '.join(unbekannt), ', '.join(BEKANNT)))
    sys.exit(2)

PROBE = '--probe' in argv


def wert(name):
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return argv[i + 1]
    return None


GRUND = wert('--grundlinie')
ZE_NEU = wert('--zeilenenden-neu')
ERLAUBT_STIL = set(t.strip().replace('\\', '/')
                   for t in (ZE_NEU or '').split(',') if t.strip())
rest = [a for a in argv if not a.startswith('--') and a not in (GRUND, ZE_NEU)]
if not rest:
    print(__doc__)
    sys.exit(1)
ORDNER = os.path.abspath(rest[0].rstrip('/\\'))


def stil(b):
    crlf = b.count(b'\r\n')
    lf = b.count(b'\n') - crlf
    if b.count(b'\r') - crlf:
        return 'einzelne CR'
    if crlf and lf:
        return 'gemischt'
    return 'CRLF' if crlf else ('LF' if lf else 'ohne')


# ---------- 1. Ordnername gegen plugin.cfg ----------
pc = os.path.join(ORDNER, 'plugin.cfg')
if not os.path.isfile(pc):
    raise SystemExit('ABBRUCH: keine plugin.cfg in %s' % ORDNER)
m = re.search(rb'^VERSION=([^\r\n]*)', open(pc, 'rb').read(), re.M)
if not m:
    raise SystemExit('ABBRUCH: kein VERSION in plugin.cfg')
fassung = m.group(1).decode().strip()
name = os.path.basename(ORDNER)
print('== %s ==' % name)
print('  plugin.cfg nennt %s' % fassung)
if not name.endswith(fassung):
    raise SystemExit(
        'ABBRUCH: der Ordner heisst %r, plugin.cfg nennt %r.\n'
        '  Ordnername und Fassung muessen zusammenpassen - sonst entsteht\n'
        '  genau die Verwechslung, gegen die dieses Werkzeug gebaut ist.'
        % (name, fassung))
print('  Ordnername passt dazu')

# ---------- 1b. Steckt eine Pruefstands-Attrappe im Prueling? ----------
#
# Mehrere Pruefstuecke im Haus bauen einen LoxBerry-Nachbau unter
# <sandkasten>/lb und nehmen den Sandkasten als ERSTES Argument - anders
# als jedes andere Werkzeug. Ein Griff daneben, und der Nachbau liegt im
# Plugin-Ordner. Am 14.09.2026 genau so passiert (ZendureSolarFlow
# 0.9.19): 77 Eintraege statt 42, und weder der byteweise Vergleich noch
# das Freigabetor haben etwas gesagt - der Ordner und das Archiv waren ja
# gleich, nur eben beide falsch.
#
# Ein Plugin fuehrt kein lb/ und kein webfrontend/html/plugins/ - diese
# Baeume legt der Installer auf der Anlage an.
ATTRAPPE = ('lb/config/system', 'lb/webfrontend', 'lb/data/system',
            'webfrontend/html/plugins', 'webfrontend/htmlauth/plugins')
_gefunden = [t for t in ATTRAPPE if os.path.isdir(os.path.join(ORDNER, *t.split('/')))]
if _gefunden:
    raise SystemExit(
        'ABBRUCH: im Plugin-Ordner steckt ein LoxBerry-Nachbau (%s).\n'
        '  Das legt kein Plugin an - das legt ein Pruefstueck an, dem man\n'
        '  den Plugin-Ordner statt eines Sandkastens gegeben hat.\n'
        '  Erst wegraeumen, dann packen: ohne diese Zeile ginge ein Archiv\n'
        '  mit einer zweiten general.json auf die Anlagen.'
        % ', '.join(_gefunden))
print('  kein Pruefstands-Nachbau im Ordner')
# Hinweis, kein Abbruch: ohne .gitattributes "* -text" darf git beim Erzeugen des Tag-Archivs
# normalisieren, und der Ordner ist dann nie byteweise gleich mit dem, was Anlagen laden
# (Regeln/03, Abschnitt 12; gemessen 05.09.2026: 12 von 142 Ordnern haben eine).
ga = os.path.join(ORDNER, '.gitattributes')
if not os.path.isfile(ga):
    print('  HINWEIS: keine .gitattributes im Ordner - beim naechsten Anfassen "* -text" hinein (Regeln/03, 12)')
elif b'-text' not in open(ga, 'rb').read():
    print('  HINWEIS: .gitattributes ohne "-text" - git darf normalisieren (Regeln/03, 12)')

ZIEL = os.path.join(os.path.dirname(ORDNER), name + '.zip')

# ---------- 1b. Pfade, an denen LoxBerry eine DATEI erwartet ----------
#
# plugininstall.pl oeffnet diese Pfade als Datei. Liegt dort ein Verzeichnis,
# scheitert das - und zwar STILL, mit einem Rueckfall auf eine leere Liste.
#
# Gemessen am 29.08.2026 an Raumklima 0.11.0, in einem echten
# Installationsprotokoll:
#
#   <INFO> Installing additional software packages.
#   <ERROR> Cannot open APT file.
#   ...
#   0 upgraded, 0 newly installed, 0 to remove
#   <OK> Packages  successfully installed        <- die Liste kam LEER an
#
# Das Plugin lieferte dpkg/apt/ als Ordner mit php-curl.list darin. Die
# Installation lief im uebrigen sauber durch, und die Zusammenfassung nannte
# genau EINE Zeile - php-curl wurde nie installiert. Die 28 uebrigen Linien
# des Bestands liefern dpkg/apt richtig als Datei; diese eine nicht, und kein
# Werkzeug hat es gesehen.
#
# Dieselbe Klasse steht mit cron/cron.XXmin schon in REGELN_2: LoxBerry
# fuehrt in den Cron-Ordnern nur Dateien aus, und ein ausgeliefertes
# Verzeichnis liess den Cron nie laufen.
DATEIPFADE = ('dpkg/apt', 'dpkg/dpkg')
verzeichnisse = []
for rp in DATEIPFADE:
    p = os.path.join(ORDNER, *rp.split('/'))
    if os.path.isdir(p):
        drin = sorted(os.listdir(p))
        verzeichnisse.append('%s (Ordner mit %s)'
                             % (rp, ', '.join(drin[:4]) or 'nichts darin'))
# cron/cron.NNmin ebenso - dort ist es seit dem Beschattungswaechter belegt.
cronordner = os.path.join(ORDNER, 'cron')
if os.path.isdir(cronordner):
    for e in sorted(os.listdir(cronordner)):
        if re.match(r'^cron\.\d+min$', e) and os.path.isdir(os.path.join(cronordner, e)):
            verzeichnisse.append('cron/%s (Ordner statt Datei)' % e)
if verzeichnisse:
    raise SystemExit(
        'ABBRUCH: LoxBerry erwartet an diesen Stellen eine DATEI, gefunden\n'
        '  wurde ein Verzeichnis:\n    %s\n'
        '  plugininstall.pl oeffnet sie als Datei; bei einem Verzeichnis\n'
        '  scheitert das STILL (Cannot open APT file / der Cron laeuft nie).'
        % '\n    '.join(verzeichnisse))
print('  Datei-Pfade (dpkg/apt, cron/cron.NNmin): keine Verzeichnisse')

# ---------- 2. Zeilenenden gegen die Grundlinie ----------
if GRUND:
    if not os.path.isfile(GRUND):
        raise SystemExit('ABBRUCH: Grundlinie %s fehlt' % GRUND)
    # BERICHTIGT 04.09.2026, gleiche Stelle wie in freigabe_pruefen.py: das
    # Abschneiden des ersten Pfadteils stand hier ohne Bedingung. Fuer ein
    # mit diesem Werkzeug gebautes Archiv (plugin.cfg an der Wurzel) wurde
    # damit aus "templates/lang/x.ini" ein "lang/x.ini"; der Schluessel traf
    # nicht, und jede Datei in einem Unterordner wurde stumm uebersprungen.
    # Gemessen ueber sieben Linien: 8 bis 12 statt 22 bis 47 Dateien.
    z = zipfile.ZipFile(GRUND)
    namen = [n for n in z.namelist() if not n.endswith('/')]
    erste = set(n.split('/')[0] for n in namen if '/' in n)
    kuerzen = len(erste) == 1 and all('/' in n for n in namen)
    basis = {}
    for n in namen:
        basis[n.split('/', 1)[1] if kuerzen else n] = z.read(n)
    z.close()
    abw = []
    gewollt = []
    verglichen = 0
    for w, _, ds in os.walk(ORDNER):
        for d in sorted(ds):
            p = os.path.join(w, d)
            rp = os.path.relpath(p, ORDNER).replace(os.sep, '/')
            b = open(p, 'rb').read()
            if b'\x00' in b or rp not in basis:
                continue
            verglichen += 1
            if stil(b) != stil(basis[rp]):
                if rp in ERLAUBT_STIL:
                    gewollt.append('%s (%s statt %s)' % (rp, stil(b), stil(basis[rp])))
                else:
                    abw.append('%s (%s statt %s)' % (rp, stil(b), stil(basis[rp])))
    if abw:
        raise SystemExit('ABBRUCH Zeilenenden: %s' % ', '.join(abw))
    # Eine genannte Datei, die sich gar nicht geaendert hat, ist ein Tippfehler
    # oder ein Rest - sie wird benannt, nicht stillschweigend hingenommen.
    ungenutzt = sorted(ERLAUBT_STIL - set(g.split(' ')[0] for g in gewollt))
    if ungenutzt:
        raise SystemExit('ABBRUCH: --zeilenenden-neu nennt %s - dort aendert sich '
                         'aber nichts. Tippfehler oder Rest?' % ', '.join(ungenutzt))
    # Eine leere Menge ist kein Bestehen.
    if not verglichen:
        raise SystemExit('ABBRUCH Zeilenenden: keine einzige Datei in %s '
                         'wiedergefunden - Grundlinie oder Ordner passt nicht'
                         % os.path.basename(GRUND))
    print('  Zeilenenden wie in %s: %d von %d Datei(en) verglichen, %s'
          % (os.path.basename(GRUND), verglichen, len(basis),
             'alle gehalten' if not gewollt
             else '%d gewollt umgestellt' % len(gewollt)))
    for g in gewollt:
        print('    GEWOLLT umgestellt: %s' % g)

# ---------- 3. Packen ----------
#
# Erzeugte Python-Zwischenstaende gehoeren nicht ins Archiv. Anlass,
# 26.08.2026: in LoxBerry-Plugin-Heimkino-1.3.2/bin/ lagen zwei .pyc aus
# einem Lauf auf dem Arbeitsrechner. Das Archiv hatte dadurch 39 statt 37
# Dateien - aufgefallen ist es nur, weil die Dateizahl mitgezaehlt wurde.
#
# WICHTIG: Weggelassenes wird NICHT verschwiegen. Dieses Werkzeug lebt von
# der Zusage "byteweise gegen den Ordner: gleich"; eine stille Ausnahme
# wuerde genau die Zusage aushoehlen. Darum steht jeder uebergangene
# Eintrag im Bericht, und der Rueckvergleich laesst genau diese aus -
# keinen weiteren.
os.chdir(ORDNER)


def uebergehen(pfad):
    """Erzeugter Python-Zwischenstand? Nur diese beiden Formen, sonst nichts.

    Geprueft wird der VOLLE Name eines Pfadteils, nicht ein Teilstueck:
    eine Datei 'mein_pycache.py' oder ein Ordner 'pycache' bleiben drin.
    """
    teile = pfad.split('/')
    if '__pycache__' in teile:
        return True
    return teile[-1].endswith(('.pyc', '.pyo'))


# ---------------------------------------------------------------------------
# ERGAENZT 05.09.2026: was der Zweig ignoriert, gehoert auch nicht ins Archiv.
#
# Anlass: LoxBerry-Plugin-AudiConnect-0.9.12 fuehrte ein log/ aus einem
# Prueflauf mit log/plugins/audiconnect/audi.log (0 Byte). Auf GitHub kam es
# nie an - die .gitignore des Zweigs fuehrt "*.log" -, ins ARCHIV aber schon,
# denn dieses Werkzeug kannte die .gitignore nicht. Archiv und Tag wichen
# damit um genau diese vier Eintraege voneinander ab, und das Archiv ist im
# Haus der belegte Vorzustand fuer die naechste Fassung.
#
# Umgesetzt ist eine BEWUSST KLEINE Teilmenge der git-Regeln: Kommentare und
# Leerzeilen, Verneinung mit '!', Verzeichnisse mit '/' am Ende, Verankerung
# mit '/' am Anfang, sonst Vergleich gegen den Basisnamen UND den ganzen
# Pfad. Was git sonst noch kann ('**', Zeichenklassen), ist hier nicht
# nachgebaut - und weil ein stilles Weglassen die Zusage "byteweise gegen den
# Ordner: gleich" aushoehlen wuerde, steht JEDER uebergangene Eintrag
# namentlich im Bericht.
# ERGAENZT 05.09.2026, unmittelbar nach der .gitignore-Lesung - denn die
# allein haette den Anlassfall NICHT gefangen: die .gitignore lebt im
# Repository, nicht im Arbeitsordner. Von den drei betroffenen Ordnern fuehrte
# KEINER eine (gemessen: 61 der 143 Ordner tun es, diese drei nicht). Eine
# Korrektur, die den Fall nicht faengt, wegen dem sie gebaut wurde, ist keine.
#
# Was ihn faengt, ist eine Aussage ueber das Plugin selbst: log/ an der WURZEL
# gehoert dem Installer. plugininstall.pl legt log/plugins/<ordner>/ an und
# setzt die Rechte; ein Plugin, das log/ mitliefert, liefert einen Prueflauf
# mit. Gemessen ueber alle Archive im Arbeitsordner: sieben fuehren log/, alle
# drei betroffenen Linien (AudiConnect, BatterieBMS, ZendureSolarFlow), stets
# leer bis auf eine 0-Byte-Datei. KEINE Linie braucht es.
def nicht_ins_plugin(pfad):
    """Legt der Installer das selbst an? Dann gehoert es nicht ins Archiv."""
    return pfad == 'log' or pfad.startswith('log/')


def gitignore_regeln(ordner):
    p = os.path.join(ordner, '.gitignore')
    if not os.path.isfile(p):
        return []
    regeln = []
    with open(p, 'r', encoding='utf-8', errors='replace') as fh:
        for zeile in fh:
            s = zeile.strip()
            if not s or s.startswith('#'):
                continue
            verneint = s.startswith('!')
            if verneint:
                s = s[1:].strip()
            nur_verz = s.endswith('/')
            s = s.rstrip('/')
            verankert = s.startswith('/')
            regeln.append((s.lstrip('/'), verneint, nur_verz, verankert))
    return regeln


def von_git_ignoriert(pfad, ist_verz, regeln):
    treffer = False
    for muster, verneint, nur_verz, verankert in regeln:
        if nur_verz and not ist_verz:
            continue
        if verankert:
            passt = fnmatch.fnmatch(pfad, muster)
        else:
            passt = (fnmatch.fnmatch(os.path.basename(pfad), muster)
                     or fnmatch.fnmatch(pfad, muster)
                     or any(fnmatch.fnmatch(t, muster) for t in pfad.split('/')))
        if passt:
            treffer = not verneint
    return treffer


# Welche Rechte ein Eintrag im Archiv traegt. Verzeichnisse BRAUCHEN das
# x-Bit, sonst laesst sich nicht hineinsehen. Ausfuehrbar sind genau die
# Dateien, die auch ausgefuehrt werden - der Installer setzt sie zwar
# ohnehin, aber dann entscheidet das Dateisystem darueber und nicht der
# Verfasser (Lehre aus der KODI-NG-Sitzung, 26.08.2026).
def rechte(pfad):
    """Rueckgabe: (Unix-Modus, DOS-Merker) fuer external_attr."""
    if pfad.endswith('/'):
        return 0o40755, 0x10
    teile = pfad.split('/')
    # Matter2Lox-k1 (08.10.2026): ein Python-Rad (.whl) ist ein Archiv, kein
    # Programm - auch unter bin/vendor/ 0644. Bis hierher bekam es ueber die
    # bin/-Regel 0755 (Matter2Lox 0.9.35, websockets-15.0.1-py3-none-any.whl).
    # Dieselbe Ausnahme steht in linie_veroeffentlichen.sh, soll_modus().
    if teile[-1].endswith('.whl'):
        return 0o100644, 0
    if teile[0] in ('bin', 'cron', 'daemon', 'sudoers') \
            or pfad == 'uninstall/uninstall' \
            or teile[-1].endswith(('.sh', '.pl', '.cgi')):
        return 0o100755, 0
    return 0o100644, 0


GITREGELN = gitignore_regeln('.')

eintraege = []
uebergangen = []
git_weg = []
inst_weg = []
for w, verz, ds in os.walk('.'):
    verz.sort()
    for v in list(verz):
        rp = os.path.relpath(os.path.join(w, v), '.').replace(os.sep, '/')
        if uebergehen(rp):
            uebergangen.append(rp + '/')
            verz.remove(v)          # gar nicht erst hineinsteigen
            continue
        if nicht_ins_plugin(rp):
            inst_weg.append(rp + '/')
            verz.remove(v)
            continue
        if von_git_ignoriert(rp, True, GITREGELN):
            git_weg.append(rp + '/')
            verz.remove(v)
            continue
        eintraege.append((rp + '/', None))
    for d in sorted(ds):
        p = os.path.relpath(os.path.join(w, d), '.').replace(os.sep, '/')
        if uebergehen(p):
            uebergangen.append(p)
            continue
        if nicht_ins_plugin(p):
            inst_weg.append(p)
            continue
        if von_git_ignoriert(p, False, GITREGELN):
            git_weg.append(p)
            continue
        eintraege.append((p, p))

if uebergangen:
    print('  uebergangen (erzeugte Python-Zwischenstaende), %d:' % len(uebergangen))
    for u in sorted(uebergangen):
        print('    %s' % u)
if inst_weg:
    print('  uebergangen (legt der Installer selbst an), %d:' % len(inst_weg))
    for u in sorted(inst_weg):
        print('    %s' % u)
if git_weg:
    print('  uebergangen (von der .gitignore des Ordners ignoriert), %d:' % len(git_weg))
    for u in sorted(git_weg):
        print('    %s' % u)
elif GITREGELN:
    print('  .gitignore gelesen (%d Regel(n)): nichts zu uebergehen' % len(GITREGELN))

if PROBE:
    print('  --probe: %d Eintraege waeren zu packen, nichts geschrieben' % len(eintraege))
    sys.exit(0)

ausfuehrbar = []
with zipfile.ZipFile(ZIEL, 'w', zipfile.ZIP_DEFLATED) as z:
    for eintrag, quelle in sorted(eintraege):
        zi = zipfile.ZipInfo(eintrag)
        modus, dos = rechte(eintrag)
        # create_system 3 = Unix. Ohne diese Angabe wertet unzip den Modus
        # gar nicht aus; unter Windows steht hier sonst 0 (DOS).
        zi.create_system = 3
        zi.external_attr = (modus << 16) | dos
        if quelle is not None and modus & 0o111:
            ausfuehrbar.append(eintrag)
        if quelle is None:
            z.writestr(zi, b'')
        else:
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, open(quelle, 'rb').read())

# ---------- 4. Zurueckvergleichen ----------
z = zipfile.ZipFile(ZIEL)
drin = [n for n in z.namelist() if not n.endswith('/')]
anders = [n for n in drin if open(n.replace('/', os.sep), 'rb').read() != z.read(n)]
auf_platte = {os.path.relpath(os.path.join(w, d), '.').replace(os.sep, '/')
              for w, _, ds in os.walk('.') for d in ds}
# Genau die uebergangenen Eintraege duerfen fehlen - kein einziger weiterer.
auf_platte = {p for p in auf_platte if not uebergehen(p)}
fehlt = sorted(auf_platte - set(drin))
tiefer = [n for n in drin if n.count('/') and n.endswith('plugin.cfg')]
# Die Rechte werden GEMESSEN, nicht angenommen: ein Verzeichnis ohne
# x-Bit ist der Befund vom 28.08.2026, und eine Zusage ohne Messung
# waere genau das, wogegen dieses Werkzeug gebaut ist.
ohne_x = [i.filename for i in z.infolist()
          if i.is_dir() and not (((i.external_attr >> 16) & 0o7777) & 0o111)]
z.close()


def abbruch(text):
    """Abbrechen UND das halbfertige Archiv wegraeumen.

    Ein Archiv, das nach einem Abbruch liegen bleibt, sieht aus wie ein
    gepacktes - und genau das laedt dann jemand hoch.
    """
    try:
        os.remove(ZIEL)
        text += '\n  Das halbfertige Archiv wurde entfernt.'
    except OSError as e:
        text += '\n  ACHTUNG: %s liess sich nicht entfernen (%s).' % (ZIEL, e)
    raise SystemExit(text)


if anders or fehlt or tiefer or 'plugin.cfg' not in drin:
    abbruch('ABBRUCH nach dem Packen: abweichend=%s fehlend=%s doppelt=%s'
            % (anders, fehlt, tiefer))
if ohne_x:
    abbruch('ABBRUCH: %d Verzeichnis(se) ohne x-Bit im Archiv - auf dem '
            'LoxBerry waere davon keine Datei kopierbar: %s'
            % (len(ohne_x), ', '.join(ohne_x[:5])))

h = hashlib.sha256(open(ZIEL, 'rb').read()).hexdigest()
print('\n  %s' % os.path.basename(ZIEL))
print('  %d Eintraege, %d Dateien, %d Byte' % (len(eintraege), len(drin), os.path.getsize(ZIEL)))
print('  SHA256 %s' % h)
print('  byteweise gegen den Ordner: gleich')
print('  Rechte: %d Verzeichnisse 0755, %d Dateien 0755, %d Dateien 0644'
      % (len(eintraege) - len(drin), len(ausfuehrbar), len(drin) - len(ausfuehrbar)))
if ausfuehrbar:
    print('    ausfuehrbar: %s' % ', '.join(sorted(ausfuehrbar)))
