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

Aufruf:
    python3 packen.py PLUGINORDNER [--grundlinie VEROEFFENTLICHT.zip] [--probe]
"""
import hashlib
import os
import re
import sys
import zipfile

argv = sys.argv[1:]
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

with zipfile.ZipFile(ZIEL, 'w', zipfile.ZIP_DEFLATED) as z:
    for eintrag, quelle in sorted(eintraege):
        zi = zipfile.ZipInfo(eintrag)
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
z.close()
if anders or fehlt or tiefer or 'plugin.cfg' not in drin:
    raise SystemExit('ABBRUCH nach dem Packen: abweichend=%s fehlend=%s doppelt=%s'
                     % (anders, fehlt, tiefer))

h = hashlib.sha256(open(ZIEL, 'rb').read()).hexdigest()
print('\n  %s' % os.path.basename(ZIEL))
print('  %d Eintraege, %d Dateien, %d Byte' % (len(eintraege), len(drin), os.path.getsize(ZIEL)))
print('  SHA256 %s' % h)
print('  byteweise gegen den Ordner: gleich')
