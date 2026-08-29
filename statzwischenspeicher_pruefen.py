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

Aufruf:  statzwischenspeicher_pruefen.py [ORDNER ...]
"""
import re, sys, pathlib

# Was hinter dem filesize() stehen muss, damit es ein Kappungstor ist.
KAPPT = re.compile(r'array_slice|file\s*\(|rename\s*\(|unlink\s*\(|ftruncate|'
                   r'file_put_contents\s*\([^,]+,\s*implode', re.I)
# Woran ein Pruefstand erkannt wird - dort laeuft der Prozess einmal.
PRUEFSTAND = re.compile(r'_test\.php$|/t_[^/]+\.php$|_probe\.php$')


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
