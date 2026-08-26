#!/usr/bin/env python3
"""Den lbheader()-Block hinter die Handler ziehen - woertlich, ohne Inhaltsaenderung.

Anlass: MGiSmart 1.1.2 (26.08.2026). Standen die Download-Handler hinter
LBWeb::lbheader(), war der Seitenkopf schon geschrieben, und
header('Content-Type: ...') kam zu spaet - der Knopf lieferte eine Seite
statt einer Datei.

WAS DIESES WERKZEUG TUT
Es bewegt GENAU EINEN Block: den lbheader()-Aufruf samt seiner Umhuellung
(if (...) { ... } und einem etwaigen else { ... }). Er wandert von seiner
Stelle an das Ende des PHP-Abschnitts, unmittelbar vor das '?>', hinter dem
die Ausgabe beginnt. Kein Zeichen des Blocks wird veraendert; die Handler
selbst werden nicht angefasst.

DAS IST DIE RICHTUNG, DIE DER VERFASSER GEWAEHLT HAT. Nachgemessen an
MGiSmart v1.1.1 -> 1.1.2: dort ist der Kopf nach unten gewandert, nicht die
Handler nach oben.

WORAN ES SICH WEIGERT - jede dieser Lagen bricht ab, ohne zu schreiben:
  * kein lbheader() gefunden, oder mehr als eines
  * die Umhuellung laesst sich nicht eindeutig klammern
  * zwischen dem Block und dem '?>' steht eine AUSGABE, die nicht in einem
    Zweig steht, der mit exit endet - dann aendert der Umzug die Reihenfolge
  * nach dem Umbau steht der Block nicht genau einmal da, oder die Datei hat
    eine andere Zeichenzahl als vorher plus/minus dem Block

Aufruf:  python3 kopfzeilen_umbauen.py DATEI.php [--probe]
"""
import re, sys, os

def ohne_kommentare(text):
    aus = []; i = 0; n = len(text)
    while i < n:
        z = text[i]
        if z == '/' and i + 1 < n and text[i+1] == '*':
            j = text.find('*/', i + 2); j = n if j < 0 else j + 2
            aus.append(''.join(c if c == '\n' else ' ' for c in text[i:j])); i = j
        elif (z == '/' and i + 1 < n and text[i+1] == '/') or z == '#':
            j = text.find('\n', i); j = n if j < 0 else j
            aus.append(' ' * (j - i)); i = j
        elif z in '"\'':
            j = i + 1
            while j < n and text[j] != z:
                j += 2 if text[j] == '\\' else 1
            j = min(j + 1, n)
            aus.append(''.join(c if c == '\n' else ' ' for c in text[i:j])); i = j
        else:
            aus.append(z); i += 1
    return ''.join(aus)

LB      = re.compile(r'\blbheader\s*\(')
AUSGABE = re.compile(r'^\s*(echo|print|printf|readfile|var_dump)\b')
EXIT    = re.compile(r'^\s*(exit|die)\b')

def umbauen(pfad, probe=False):
    # BYTEWEISE lesen und das Zeilenende merken. Am 26.08.2026 hat die erste
    # Fassung dieses Werkzeugs eine CRLF-Datei als LF zurueckgeschrieben - der
    # Diff zeigte dann 1523 geaenderte Zeilen statt drei. Textmodus-Lesen
    # macht CRLF zu \n, und newline='' schreibt genau das zurueck.
    rohb = open(pfad, 'rb').read()
    crlf = rohb.count(b'\r\n')
    lf   = rohb.count(b'\n') - crlf
    if crlf and lf:
        return 'ABBRUCH: gemischte Zeilenenden (CRLF %d, LF %d)' % (crlf, lf)
    ende  = '\r\n' if crlf else '\n'
    roh   = rohb.decode('utf-8', 'replace').replace('\r\n', '\n')
    blank = ohne_kommentare(roh)
    zr, zb = roh.split('\n'), blank.split('\n')

    treffer = [i for i, z in enumerate(zb, 1) if LB.search(z)]
    if len(treffer) == 1:
        # Gibt es ueberhaupt etwas zu beheben? Ein Kopf ohne spaeteres
        # header('Content-...') ist in Ordnung - dann wird nichts bewegt.
        spaet = [i for i, z in enumerate(zb, 1)
                 if i > treffer[0] and re.search(r'\bheader\s*\(', z)
                 and re.search(r'Content-(Type|Disposition)\s*:', zr[i-1], re.I)]
        if not spaet:
            return 'nichts zu tun: kein Content-Header hinter lbheader()' 
    if len(treffer) != 1:
        return 'ABBRUCH: %d lbheader()-Aufrufe (erwartet genau 1)' % len(treffer)
    kopf = treffer[0]

    # Klammertiefe je Zeile, kumuliert vom Dateianfang - keine Heuristik.
    tiefe = [0] * (len(zb) + 1)
    for i, z in enumerate(zb, 1):
        tiefe[i] = tiefe[i-1] + z.count('{') - z.count('}')

    # Blockanfang: die letzte Zeile vor dem Aufruf, vor der die Tiefe 0 war
    # und die selbst etwas enthaelt.
    a = kopf
    while a > 1 and not (tiefe[a-1] == 0 and zb[a-1].strip() != ''):
        a -= 1
    if tiefe[a-1] != 0:
        return 'ABBRUCH: Blockanfang nicht auf Klammertiefe 0'

    # Blockende: geschweifte UND runde Klammern muessen ausgeglichen sein, und
    # die Zeile muss die Anweisung abschliessen. Ein anschliessendes
    # else/elseif gehoert dazu.
    #
    # Die runden Klammern sind am 27.08.2026 dazugekommen: Midea2Lox 4.2.11
    # ruft lbheader() OHNE umschliessendes if und ueber ZWEI Zeilen auf. Ohne
    # diese Bedingung riss der Umzug die Anweisung mitten entzwei - PHP meldete
    # "syntax error, unexpected ','". Die Datei ist wiederhergestellt worden.
    e = a
    runde = 0
    while e <= len(zb):
        runde += zb[e-1].count('(') - zb[e-1].count(')')
        schluss = zb[e-1].rstrip().endswith((';', '}', '{'))
        if e >= kopf and tiefe[e] == 0 and runde == 0 and schluss:
            rest = zb[e-1].split('}')[-1].strip()
            nach = zb[e].strip() if e < len(zb) else ''
            if rest.startswith(('else', 'elseif')) or nach.startswith(('else', 'elseif')):
                e += 1
                continue
            if zb[e-1].rstrip().endswith('{'):     # Block erst geoeffnet
                e += 1
                continue
            break
        e += 1
    if e > len(zb):
        return 'ABBRUCH: Blockende nicht gefunden'

    # Einfuegestelle: das '?>' nach dem Block
    ziel = next((i for i in range(e + 1, len(zb) + 1) if '?>' in zb[i-1]), None)
    if ziel is None:
        return 'ABBRUCH: kein "?>" hinter dem Block'

    # Steht dazwischen eine Ausgabe, die NICHT mit exit endet?
    # Zeilen, die in einem Funktionsrumpf liegen, laufen hier nicht - eine
    # Ausgabe darin ist kein Hindernis. (AudiConnect 0.9.9: au_formfelder()
    # gibt zwei versteckte Felder aus, aber erst wenn sie gerufen wird.)
    in_funktion = [False] * (len(zb) + 2)
    i = 1
    while i <= len(zb):
        if re.search(r'^\s*(abstract\s+|final\s+|public\s+|private\s+|protected\s+|static\s+)*function\b', zb[i-1]):
            j = i
            while j <= len(zb) and '{' not in zb[j-1]:
                j += 1
            k = j
            while k <= len(zb) and tiefe[k] > tiefe[i-1]:
                k += 1
            for m in range(i, min(k + 1, len(zb) + 1)):
                in_funktion[m] = True
            i = k + 1
            continue
        i += 1

    ungedeckt = []
    for i in range(e + 1, ziel):
        if not AUSGABE.search(zb[i-1]) or in_funktion[i]:
            continue
        if not any(EXIT.search(zb[j-1]) for j in range(i + 1, min(i + 6, ziel))):
            ungedeckt.append(i)
    if ungedeckt:
        return 'ABBRUCH: Ausgabe ohne exit dazwischen, Zeile(n) %s' % ungedeckt

    block = zr[a-1:e]
    while block and block[-1].strip() == '':
        block.pop(); e -= 1
    neu = zr[:a-1] + zr[e:ziel-1] + [''] + block + [''] + zr[ziel-1:]

    # Gegenrechnung: nichts verloren, nichts doppelt
    if len(neu) != len(zr) + 2:
        return 'ABBRUCH: Zeilenzahl %d statt %d' % (len(neu), len(zr) + 2)
    if sorted(x.strip() for x in neu if x.strip()) != sorted(x.strip() for x in zr if x.strip()):
        return 'ABBRUCH: der Inhalt hat sich veraendert, nicht nur die Reihenfolge'

    if not probe:
        aus = ende.join(neu).encode('utf-8')
        # Gegenrechnung: dasselbe Zeilenende wie vorher, dieselbe Zeichenzahl
        # ohne Leerraum.
        assert (aus.count(b'\r\n') > 0) == bool(crlf), 'Zeilenende veraendert'
        # Verglichen werden die Zeilen als MENGE, nicht als Zeichenfolge - der
        # Zeichenstrom aendert sich ja gerade, das ist der Zweck. (Die erste
        # Fassung dieser Zusicherung verglich den Strom und schlug deshalb
        # immer fehl.) Erlaubt sind genau zwei zusaetzliche Leerzeilen.
        eb = ende.encode('utf-8')
        va, vb = sorted(rohb.split(eb)), sorted(aus.split(eb))
        assert [x for x in vb if x.strip()] == [x for x in va if x.strip()], \
            'Zeilen veraendert, nicht nur umgestellt'
        assert len(vb) - len(va) == 2, 'Zeilenzahl: %d statt %d' % (len(vb), len(va) + 2)
        open(pfad, 'wb').write(aus)
    return 'umgebaut: Block Zeile %d-%d vor Zeile %d gezogen (%d Zeilen)' % (a, e, ziel, len(block))

if __name__ == '__main__':
    argv = [x for x in sys.argv[1:] if x != '--probe']
    probe = '--probe' in sys.argv
    for p in argv:
        print('%-70s %s' % (os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(p)))), umbauen(p, probe)))
