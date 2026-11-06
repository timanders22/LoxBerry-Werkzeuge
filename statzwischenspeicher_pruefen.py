#!/usr/bin/env python3
"""Protokollkappungen finden, die den stat()-Zwischenspeicher nicht leeren.

DIE KLASSE, nicht jedes filesize():

PHP merkt sich die Antworten von stat(). Innerhalb EINES Prozesses sieht
filesize() die erste Groesse und danach nie wieder eine neue -
file_put_contents(..., FILE_APPEND) macht den Eintrag nicht ungueltig. Eine
Protokollkappung, die an filesize() haengt, faellt in einem langlebigen
Prozess (Dienst, Zuhoerer, Minutentakt mit Schleife) still aus.

Gemeint ist deshalb NUR: ein filesize() als KAPPUNGSTOR, also in einem Block,
der danach kuerzt oder umbenennt - und in einer Funktion, die je Zeile erneut
aufgerufen wird. Ein filesize(), das dem Menschen eine Groesse ANZEIGT, oder
eines in einem Pruefstand, braucht die Zeile nicht: dort laeuft der Prozess
einmal.

Ohne diese Einengung meldet das Werkzeug 44 Fundstellen, von denen die
meisten keine sind - und ein Werkzeug, das mehr Fehlmeldungen als Befunde
gibt, wird nach dem dritten Mal nicht mehr gelesen.

NUR PHP. Das Werkzeug liest ausschliesslich .php-Dateien, denn nur PHP
haelt einen stat()-Zwischenspeicher. In Python liefert os.path.getsize()
nach einem Anhaengen sofort die neue Groesse - gemessen am 03.09.2026:
100 Byte, angehaengt, 1000 Byte. Eine Kappung in Python hat das Problem
also nicht.

DAHER GILT: "0 Kappung(en)" heisst "keine PHP-Kappung", NICHT "keine
Kappung". Ultraschall 1.2.2 kappt sein Protokoll in bin/ultraschall.py
(log_kappen); dieses Werkzeug meldet dort 0 und hat trotzdem recht. Wer aus
der Null auf eine fehlende Kappung schliesst, misst das Werkzeug, nicht den
Prueflaufling.

Aufruf:  statzwischenspeicher_pruefen.py [ORDNER ...]
"""
import re, sys, pathlib

# Was hinter dem filesize() stehen muss, damit es ein Kappungstor ist.
KAPPT = re.compile(r'array_slice|file\s*\(|rename\s*\(|unlink\s*\(|ftruncate|'
                   r'file_put_contents\s*\([^,]+,\s*implode', re.I)
# Woran ein Pruefstand erkannt wird - dort laeuft der Prozess einmal.
PRUEFSTAND = re.compile(r'_test\.php$|/t_[^/]+\.php$|_probe\.php$')

# NACHGESCHAERFT 04.09.2026 - der dritte Fehlalarm derselben Bauart.
#
# KAPPT allein zaehlt 'unlink(' und 'file(' in der Naehe eines filesize() mit.
# Damit schlug das Werkzeug dreimal auf ARCHIVBEREINIGUNGEN an, die keine
# Kappungen sind:
#
#   BYD-Autos    by_zugang_loeschen()  filesize() sagt, wie viele Nullen zu
#                                      schreiben sind - einmal je Klick
#   ACTiKamera   cam_cleanup()         summiert Byte und loescht die
#                                      aeltesten Dateien
#   Intercom     ic_aufraeumen()       dasselbe, nach Alter, Anzahl und Platz
#
# Allen dreien fehlt das Merkmal einer Kappung: Ein Kappungstor VERGLEICHT die
# Groesse EINER Datei mit einer Schranke und kuerzt DIESE Datei. Die drei oben
# lesen die Groesse fremder Dateien, um zu summieren oder zu melden - und die
# gelesene Datei wird danach geloescht, nicht fortgeschrieben. Der
# stat()-Zwischenspeicher kann dort nicht schaden: zwischen den zwei Lesungen
# desselben Pfades schreibt niemand.
#
# Erkannt wird der Vergleich in zwei Formen:
#   direkt    if (filesize($f) > 512000)        - auch mit @ und (int)
#   indirekt  $n = filesize($f); if ($n > 100)  - Zuweisung, dann Vergleich
#
# GRENZE, ausdruecklich: eine Kappung, die die Schranke ueber zwei Funktionen
# verteilt, findet dieses Werkzeug nicht. Lieber eine enge Pruefung, der man
# glaubt, als eine breite, die nach dem dritten Fehlalarm niemand mehr liest.
# Ein Vergleich gegen 0 ist KEINE Schranke, sondern die Frage "ist die Datei
# leer?". Anlass 04.09.2026: BYD-Autos by_zugang_loeschen() ueberschreibt die
# Zugangsdatei mit Nullen und loescht sie danach -
#     $laenge = (int) @filesize($f);
#     if ($laenge > 0) { @file_put_contents($f, str_repeat('0', $laenge)); }
# Das ist eine Leerheitswache. Eine Kappung vergleicht gegen eine GROESSE.
VERGLEICH_DIREKT = re.compile(
    r'filesize\s*\([^;()]{0,120}?\)\s*\)?\s*(?:[<>]=?|[!=]==?)\s*(?!0\b)[\'"$\w(]')
VERGLEICH_ZUWEISUNG = re.compile(r'(\$\w+)\s*=[^;=]{0,40}?filesize\s*\(')


def vergleicht_groesse(text):
    """Wird die gelesene Groesse mit einer SCHRANKE verglichen?

    Nicht gezaehlt wird der Vergleich gegen 0 - der fragt, ob die Datei leer
    ist, und steht in Loeschfunktionen.
    """
    if VERGLEICH_DIREKT.search(text):
        return True
    for var in set(VERGLEICH_ZUWEISUNG.findall(text)):
        # dieselbe Variable spaeter in einem Vergleich, aber nicht gegen 0
        if re.search(re.escape(var) + r'\s*(?:[<>]=?|[!=]==?)\s*(?!0\b)[\'"$\w(]',
                     text):
            return True
    return False


def bloecke(text):
    """(Startzeile, Name, Rumpf) je Funktion - grob, aber ausreichend."""
    z = text.split('\n')
    for i, s in enumerate(z):
        m = re.match(r'\s*function\s+([A-Za-z_]\w*)\s*\(', s)
        if not m:
            continue
        tiefe = 0; gesehen = False; ende = i
        for j in range(i, min(len(z), i + 400)):
            tiefe += z[j].count('{') - z[j].count('}')
            if '{' in z[j]:
                gesehen = True
            if gesehen and tiefe <= 0:
                ende = j
                break
        yield i, m.group(1), z[i:ende + 1]


def pruefe(datei):
    t = pathlib.Path(datei).read_text(encoding='utf-8', errors='replace')
    if PRUEFSTAND.search(str(datei).replace('\\', '/')):
        return []
    fund = []
    for start, name, rumpf in bloecke(t):
        roh = '\n'.join(rumpf)
        # Nur echte Anweisungen, keine Kommentarzeilen
        anw = [z for z in rumpf if not z.strip().startswith(('*', '//', '#'))]
        roh_anw = '\n'.join(anw)
        if not re.search(r'filesize\s*\(', roh_anw):
            continue
        if not KAPPT.search(roh_anw):
            continue          # kein Kappungstor - nur eine Anzeige
        if not vergleicht_groesse(roh_anw):
            continue          # liest fremde Groessen, kappt aber nichts
        hat = 'clearstatcache' in roh_anw
        fund.append((name, start + 1, hat))
    return fund


def main(argv):
    ziele = argv or sorted(str(p) for p in pathlib.Path('.').glob('LoxBerry-Plugin-*/'))
    ok = fehl = 0
    for o in ziele:
        p = pathlib.Path(o)
        zeilen = []
        for f in sorted(p.rglob('*.php')):
            for name, nr, hat in pruefe(f):
                zeilen.append((str(f.relative_to(p)), name, nr, hat))
        if not zeilen:
            continue
        offen = [z for z in zeilen if not z[3]]
        ok += len(zeilen) - len(offen); fehl += len(offen)
        marke = 'ok' if not offen else 'OFFEN: ' + ', '.join(
            '%s() in %s:%d' % (n, d, r) for d, n, r, _ in offen[:3])
        print('   %-48s %d Kappung(en)  %s' % (p.name[:48], len(zeilen), marke))
    print('   ' + '-' * 76)
    print('   %d Kappung(en) mit clearstatcache, %d ohne' % (ok, fehl))
    return 1 if fehl else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
