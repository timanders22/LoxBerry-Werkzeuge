#!/usr/bin/env python3
"""Ist der Unterschied zweier release.cfg genau der, den das Veroeffentlichen macht?

Eine Frage, ein Modul - damit `fassungslage.py` sie stellt und
`cfg_abweichung_eichung.py` sie in BEIDE Richtungen misst, ohne dass dafuer
ein Werkzeug mit Netzzugriff laufen muss.

DER ANLASS (01.09.2026)
-----------------------
REGELN_4 schreibt die Reihenfolge vor: Inhalt mit den ALTEN `.cfg` schieben,
dann taggen, dann die `.cfg` heben. Das Tag-Archiv kann den Stand, der es
nennt, deshalb nie enthalten - in `release.cfg` und `prerelease.cfg` steht
dort fuer immer die vorige Nummer.

Fuer diesen Fall gibt es in `fassungslage.py` seit dem 29.08.2026 eine
Ausnahme. Sie ist eng: sie ersetzt im Tag die alte Nummer durch die neue und
verlangt, dass Zeichen fuer Zeichen die Datei des Ordners herauskommt. Das
traegt, solange sich an den beiden Dateien NUR die Nummer aendert.

Am 31.08.2026 hat es nicht getragen: Beschattungswaechter 0.9.13 hat in beiden
`.cfg` einen KOMMENTAR ergaenzt (die Pflegeanweisung nannte sich selbst
nicht). Damit war die Datei nicht mehr durch blosses Ersetzen der Nummer aus
der alten zu erzeugen, und das Werkzeug meldete "DIESELBE NUMMER,
VERSCHIEDENER INHALT. Nummer erhoehen" - fuer eine Fassung, die frisch und
richtig veroeffentlicht war.

WAS DIESES MODUL ANDERS MACHT
-----------------------------
Es vergleicht die WIRKSAMEN Zeilen, nicht die Bytes: Abschnittskopf und
`SCHLUESSEL=WERT`. Kommentare und Leerzeilen zaehlen nicht - sie stehen in
keiner Auswertung, weder bei LoxBerry noch hier.

Streng bleibt alles andere:

  * dieselben Abschnittskoepfe in derselben Reihenfolge,
  * dieselben Schluessel in derselben Reihenfolge,
  * die Nummer im Ordner ist HOEHER als die im Tag,
  * und jeder Wert, der sich unterscheidet, muss aus dem alten entstehen,
    indem man die alte Nummer durch die neue ersetzt.

Damit faellt weiterhin durch: eine Adresse, die auf ein anderes Repository
zeigt; ein neuer oder fehlender Schluessel; ein Wert, der sich sonstwie
aendert; dieselbe Nummer bei verschiedenem Inhalt.

Diese Dateien wirken ohnehin nur IM REPOSITORY: LoxBerry liest die angebotene
Fassung aus `master` und die installierte aus `plugin.cfg`. Ein Unterschied
zwischen Tag-Archiv und Ordner ist hier also nie eine Frage dessen, was auf
der Anlage laeuft - sondern nur eine der Ordnung.
"""
import re

_ZEILE = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$')
_KOPF = re.compile(r'^\[([^\]]+)\]\s*$')


def _wirksam(rohbytes):
    """Abschnittskoepfe und Schluessel=Wert in der Reihenfolge der Datei.

    Rueckgabe: Liste aus ('kopf', name) und ('paar', schluessel, wert).
    Kommentare (# oder ;) und Leerzeilen fallen weg.
    """
    text = rohbytes.decode('utf-8', 'replace').replace('\r\n', '\n').replace('\r', '\n')
    aus = []
    for zeile in text.split('\n'):
        z = zeile.strip()
        if z == '' or z.startswith('#') or z.startswith(';'):
            continue
        m = _KOPF.match(z)
        if m:
            aus.append(('kopf', m.group(1)))
            continue
        m = _ZEILE.match(z)
        if m:
            aus.append(('paar', m.group(1), m.group(2).strip()))
            continue
        # Keine Zeile dieser Form. Sie zaehlt als wirksam und unbekannt -
        # was nicht erkannt wird, wird nicht wegerklaert.
        aus.append(('roh', z))
    return aus


def _zahlen(v):
    try:
        return tuple(int(x) for x in v.strip().split('.'))
    except (ValueError, AttributeError):
        return None


def erklaerbar(alt_bytes, neu_bytes):
    """Ist der Unterschied genau der des Veroeffentlichens?

    alt_bytes  die Datei aus dem TAG-Archiv (die vorige Nummer)
    neu_bytes  die Datei aus dem Arbeitsordner (die neue Nummer)

    Rueckgabe: (True, Grund) oder (False, Grund). Der Grund ist immer ein
    Satz, den man in einen Bericht schreiben kann - "False, ''" waere eine
    Meldung, die zum Nachsehen zwingt.
    """
    a, n = _wirksam(alt_bytes), _wirksam(neu_bytes)
    if len(a) != len(n):
        return False, 'verschieden viele wirksame Zeilen (%d gegen %d)' % (len(a), len(n))

    a_paare = {e[1]: e[2] for e in a if e[0] == 'paar'}
    n_paare = {e[1]: e[2] for e in n if e[0] == 'paar'}
    a_v, n_v = a_paare.get('VERSION'), n_paare.get('VERSION')
    if a_v is None or n_v is None:
        return False, 'keine VERSION-Zeile'
    a_z, n_z = _zahlen(a_v), _zahlen(n_v)
    if a_z is None or n_z is None:
        return False, 'VERSION ist keine Nummer (%r / %r)' % (a_v, n_v)
    if not n_z > a_z:
        return False, 'der Ordner traegt keine hoehere Nummer (%s gegen %s)' % (n_v, a_v)

    for e_a, e_n in zip(a, n):
        if e_a[0] != e_n[0]:
            return False, 'Aufbau weicht ab (%s gegen %s)' % (e_a[0], e_n[0])
        if e_a[0] == 'kopf':
            if e_a[1] != e_n[1]:
                return False, 'anderer Abschnitt: [%s] gegen [%s]' % (e_a[1], e_n[1])
            continue
        if e_a[0] == 'roh':
            if e_a[1] != e_n[1]:
                return False, 'unbekannte Zeile geaendert: %s' % e_n[1][:60]
            continue
        if e_a[1] != e_n[1]:
            return False, 'anderer Schluessel: %s gegen %s' % (e_a[1], e_n[1])
        if e_a[2] == e_n[2]:
            continue
        if e_a[2].replace(a_v, n_v) != e_n[2]:
            return False, '%s aendert sich nicht nur um die Nummer' % e_a[1]
    return True, 'nur Fassungsnummer und Kommentare (%s -> %s)' % (a_v, n_v)
