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
"""
import hashlib
import os
import re
import sys
import zipfile

argv = sys.argv[1:]

# Ein unbekannter Schalter darf nicht ARBEITEN. Am 28.08.2026 wurde dieses
# Werkzeug mit --pruefen aufgerufen (es heisst --probe); es hat den Schalter
# stillschweigend uebergangen und gepackt, wo nur gemessen werden sollte.
BEKANNT = ('--probe', '--grundlinie')
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
rest = [a for a in argv if not a.startswith('--') and a != GRUND]
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

ZIEL = os.path.join(os.path.dirname(ORDNER), name + '.zip')

# ---------- 2. Zeilenenden gegen die Grundlinie ----------
if GRUND:
    if not os.path.isfile(GRUND):
        raise SystemExit('ABBRUCH: Grundlinie %s fehlt' % GRUND)
    z = zipfile.ZipFile(GRUND)
    basis = {}
    for n in z.namelist():
        if not n.endswith('/'):
            basis[n.split('/', 1)[1] if '/' in n else n] = z.read(n)
    z.close()
    abw = []
    for w, _, ds in os.walk(ORDNER):
        for d in sorted(ds):
            p = os.path.join(w, d)
            rp = os.path.relpath(p, ORDNER).replace(os.sep, '/')
            b = open(p, 'rb').read()
            if b'\x00' in b or rp not in basis:
                continue
            if stil(b) != stil(basis[rp]):
                abw.append('%s (%s statt %s)' % (rp, stil(b), stil(basis[rp])))
    if abw:
        raise SystemExit('ABBRUCH Zeilenenden: %s' % ', '.join(abw))
    print('  Zeilenenden wie in %s: alle gehalten' % os.path.basename(GRUND))

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
    if teile[0] in ('bin', 'cron', 'daemon', 'sudoers') \
            or pfad == 'uninstall/uninstall' \
            or teile[-1].endswith(('.sh', '.pl', '.cgi')):
        return 0o100755, 0
    return 0o100644, 0


eintraege = []
uebergangen = []
for w, verz, ds in os.walk('.'):
    verz.sort()
    for v in list(verz):
        rp = os.path.relpath(os.path.join(w, v), '.').replace(os.sep, '/')
        if uebergehen(rp):
            uebergangen.append(rp + '/')
            verz.remove(v)          # gar nicht erst hineinsteigen
            continue
        eintraege.append((rp + '/', None))
    for d in sorted(ds):
        p = os.path.relpath(os.path.join(w, d), '.').replace(os.sep, '/')
        if uebergehen(p):
            uebergangen.append(p)
            continue
        eintraege.append((p, p))

if uebergangen:
    print('  uebergangen (erzeugte Python-Zwischenstaende), %d:' % len(uebergangen))
    for u in sorted(uebergangen):
        print('    %s' % u)

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
