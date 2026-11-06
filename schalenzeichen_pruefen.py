#!/usr/bin/env python3
"""Findet Steuerzeichen-Fallen in erzeugten Kommandozeilen.

Der Anlass, 27.08.2026: MG iSmart baute die Zeile

    $cmd = 'while IFS="\\t" read -r t v; do ' . … ;

In einem EINFACH angefuehrten PHP-String ist \\t kein Tabulator, sondern
Backslash und t. An die Schale ging woertlich IFS="\\t" - das Trennzeichen war
damit der Buchstabe t. Gemessen mit dash ueber 68 Themen: 0 kamen richtig an,
26 davon mit leerer Nutzlast, und leer plus -r loescht ein behaltenes Thema.
Der Fehler war drei Fassungen lang veroeffentlicht.

Die Fehlerklasse ist nicht auf IFS beschraenkt und nicht auf PHP. Sie lautet:
EIN ZEICHEN, DAS WIE EIN STEUERZEICHEN AUSSIEHT, IST AN DER STELLE, AN DER ES
ANKOMMT, KEINES - oder es ist eines, wo keines hingehoert.

Rein lesend. Aufruf:

    python3 schalenzeichen_pruefen.py PLUGINORDNER [...]
    python3 schalenzeichen_pruefen.py --alle
    python3 schalenzeichen_pruefen.py --alle --lang     auch die Hinweise

Rueckgabewert 1, wenn ein BEFUND gefunden wurde - fuer die Pruefkette.

WAS ALS BEFUND GILT (die Schale loest es NICHT auf):

  A  Eine Zuweisung an eine Schalenvariable mit rohem Backslash:
     IFS="\\t", SEP='\\n'. Die Schale legt zwei Zeichen ab, nicht eines.
  B  Ein Programm, das ein EINZELNES Zeichen erwartet, bekommt zwei:
     cut -d, sort -t, join -t, read -d. (awk -F und tr loesen selbst auf -
     die stehen deshalb nicht hier.)
  C  Ein ECHTES Steuerzeichen mitten in der Kommandozeile: ein Zeilenumbruch
     beendet dort den Befehl, ein Tabulator trennt Argumente.

WAS ALS HINWEIS GILT: jede andere Backslash-Folge, die eine Schale erreicht.
Oft richtig - printf, awk, sed und tr loesen sie selbst auf -, aber es ist die
Stelle, an der man einmal hinsehen sollte. Mit --lang werden sie gezeigt.

DIE GRENZEN, damit niemand mehr erwartet als da ist:

  * Was in escapeshellarg( … ) steht, wird UEBERSPRUNGEN - es wird ein
    einziges, angefuehrtes Argument, und ein Steuerzeichen darin ist Nutzlast.
    Drei Plugins uebergeben so ein mehrzeiliges Python-Schnipsel an
    "python -c"; das war beim ersten Anlauf ein Fehlalarm.
    ABER: wer eine ganze Kommandozeile in escapeshellarg steckt und sie an
    "sh -c" gibt, versteckt sie damit vor diesem Werkzeug. Am 27.08.2026 tut
    das im Bestand niemand (nachgesehen); wer es einfuehrt, sagt es dazu.
  * Gelesen werden nur STRINGLITERALE. Was aus einer Variablen, einer
    Konfiguration oder einer Datei kommt, sieht das Werkzeug nicht.
  * Verfolgt wird eine Variable nur innerhalb DERSELBEN Datei und ohne
    Rueckhalt auf den Ablauf - jede Zuweisung an sie wird geprueft, auch eine,
    die den Aufruf nie erreicht. Lieber ein Blick zu viel als einer zu wenig.
  * Perl: qx{ … } und Backticks sind selbst der Befehl, system(...) bekommt
    einen Ausdruck. Beides wird verschieden gelesen. Python-Aufrufe ohne
    shell=True gehen gar nicht durch eine Schale - dort ist ein Tabulator im
    Argument voellig in Ordnung, das Werkzeug meldet ihn trotzdem.
"""
import os
import re
import sys

# Programme, die ein Argument als EINZELNES Zeichen nehmen und Backslash-Folgen
# NICHT aufloesen. Gemessen an den Handbuchseiten von coreutils und dash.
EINZELZEICHEN = (
    (re.compile(r'\bcut\b[^|;&]*?\s-d\s*(["\']?)\\[tnr0]'), 'cut -d'),
    (re.compile(r'\bsort\b[^|;&]*?\s-t\s*(["\']?)\\[tnr0]'), 'sort -t'),
    (re.compile(r'\bjoin\b[^|;&]*?\s-t\s*(["\']?)\\[tnr0]'), 'join -t'),
    (re.compile(r'\bread\b[^|;&]*?\s-d\s*(["\']?)\\[tnr0]'), 'read -d'),
)

# Zuweisung an eine Schalenvariable, deren Wert mit einem Backslash beginnt.
ZUWEISUNG = re.compile(r'(?<![\w-])([A-Za-z_][A-Za-z0-9_]*)=("|\')?\\([tnr0e])')

# Aufrufe, die eine Schale starten.
PHP_AUFRUF = re.compile(
    r'(?<![\w$>])(exec|shell_exec|system|passthru|popen|proc_open)\s*\(')
PERL_AUFRUF = re.compile(r'(?<![\w$])(system|qx)\s*(?=[({\[/|!\'"])')
PY_AUFRUF = re.compile(r'(subprocess\.(?:run|call|check_output|Popen)|os\.popen)\s*\(')

# Backslash-Folgen, die eine Schale erreichen duerfen, weil das empfangende
# Programm sie selbst aufloest.
LOEST_SELBST = re.compile(r'\b(printf|awk|gawk|mawk|sed|tr|perl|python3?|echo\s+-e)\b')


def in_anfuehrung(text):
    """Nur die Teile zurueckgeben, die in der Schale angefuehrt stehen."""
    aus = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c in '\'"':
            j = i + 1
            while j < n and text[j] != c:
                j += 1
            aus.append(text[i + 1:j])
            i = j + 1
            continue
        i += 1
    return ''.join(aus)


def ohne_escapeshellarg(ausdruck):
    """escapeshellarg( … ) durch einen Platzhalter ersetzen.

    Was dort hineingeht, wird EIN angefuehrtes Argument - ein Zeilenumbruch
    darin ist Nutzlast, kein Bruch der Kommandozeile. Drei Plugins uebergeben
    so ein mehrzeiliges Python-Schnipsel an "python -c"; das ist richtig.
    """
    aus = []
    i = 0
    n = len(ausdruck)
    while i < n:
        m = re.compile(r'escapeshellarg\s*\(').search(ausdruck, i)
        if not m:
            aus.append(ausdruck[i:])
            break
        aus.append(ausdruck[i:m.start()])
        aus.append("'\x01'")
        # bis zur schliessenden Klammer, Literale uebersprungen
        tiefe = 1
        j = m.end()
        while j < n and tiefe:
            c = ausdruck[j]
            if c in '\'"':
                j = ende_literal(ausdruck, j)
                continue
            if c == '(':
                tiefe += 1
            elif c == ')':
                tiefe -= 1
            j += 1
        i = j
    return ''.join(aus)


# Perl: qx{…}, qx(…), qx[…], `…`, system(…). Der PHP-Extraktor zaehlt runde
# Klammern und lief bei qx{ … } ueber das Ende hinaus - drei falsche Treffer.
PERL_PAARE = {'{': '}', '(': ')', '[': ']', '<': '>'}


def perl_argument(quelle, ab):
    """Den Rumpf eines qx- oder system-Aufrufs holen, Trennzeichen beachtet."""
    i = ab
    n = len(quelle)
    while i < n and quelle[i] in ' \t':
        i += 1
    if i >= n:
        return ''
    auf = quelle[i]
    zu = PERL_PAARE.get(auf, auf)
    tiefe = 1
    j = i + 1
    while j < n:
        if quelle[j] == '\\':
            j += 2
            continue
        if auf != zu and quelle[j] == auf:
            tiefe += 1
        elif quelle[j] == zu:
            tiefe -= 1
            if tiefe == 0:
                return quelle[i + 1:j]
        j += 1
    return quelle[i + 1:n]


def php_argument(quelle, ab):
    """Den Ausdruck bis zur schliessenden Klammer holen (Klammern gezaehlt)."""
    tiefe = 0
    i = ab
    n = len(quelle)
    while i < n:
        c = quelle[i]
        if c in '\'"':
            i = ende_literal(quelle, i)
            continue
        if c == '(':
            tiefe += 1
        elif c == ')':
            if tiefe == 0:
                return quelle[ab:i]
            tiefe -= 1
        elif c == ',' and tiefe == 0:
            return quelle[ab:i]
        i += 1
    return quelle[ab:i]


def ende_literal(quelle, i):
    """Index HINTER dem schliessenden Anfuehrungszeichen."""
    q = quelle[i]
    i += 1
    while i < len(quelle):
        if quelle[i] == '\\':
            i += 2
            continue
        if quelle[i] == q:
            return i + 1
        i += 1
    return i


def php_aufloesen(literal):
    """Ein PHP-Stringliteral in das aufloesen, was die Schale wirklich sieht."""
    q = literal[0]
    inhalt = literal[1:-1]
    aus = []
    i = 0
    while i < len(inhalt):
        c = inhalt[i]
        if c != '\\':
            aus.append(c)
            i += 1
            continue
        n = inhalt[i + 1] if i + 1 < len(inhalt) else ''
        if q == "'":
            # Einfach angefuehrt: NUR \\ und \' sind Sonderfaelle.
            if n in ("\\", "'"):
                aus.append(n)
                i += 2
            else:
                aus.append('\\')
                i += 1
            continue
        # Doppelt angefuehrt: PHP loest auf.
        ersatz = {'n': '\n', 't': '\t', 'r': '\r', 'v': '\v', 'e': '\x1b',
                  'f': '\f', '\\': '\\', '$': '$', '"': '"'}
        if n in ersatz:
            aus.append(ersatz[n])
            i += 2
        elif n == 'x' and re.match(r'[0-9A-Fa-f]{1,2}', inhalt[i + 2:i + 4]):
            m = re.match(r'[0-9A-Fa-f]{1,2}', inhalt[i + 2:i + 4])
            aus.append(chr(int(m.group(0), 16)))
            i += 2 + len(m.group(0))
        elif re.match(r'[0-7]{1,3}', n + inhalt[i + 2:i + 4]):
            m = re.match(r'[0-7]{1,3}', inhalt[i + 1:i + 4])
            aus.append(chr(int(m.group(0), 8) & 0xFF))
            i += 1 + len(m.group(0))
        else:
            aus.append('\\')
            i += 1
    return ''.join(aus)


def schalentext(ausdruck):
    """Aus einem PHP-Ausdruck den Text bilden, den die Schale zu sehen bekommt.

    Alles, was keine Zeichenkette ist (Variablen, Funktionsaufrufe), wird zu
    einem Platzhalter - es ist zur Pruefzeit unbekannt und darf keine falschen
    Treffer erzeugen.
    """
    aus = []
    i = 0
    n = len(ausdruck)
    while i < n:
        c = ausdruck[i]
        if c in '\'"':
            j = ende_literal(ausdruck, i)
            aus.append(php_aufloesen(ausdruck[i:j]))
            i = j
            continue
        if c in ' \t\r\n.':
            i += 1
            continue
        # Ein Nicht-Literal: bis zum naechsten Punkt oder Anfuehrungszeichen.
        j = i
        while j < n and ausdruck[j] not in '\'".':
            j += 1
        aus.append('\x01')          # Platzhalter, taucht in keinem Quelltext auf
        i = j if j > i else i + 1
    return ''.join(aus)


def pruefe_text(text):
    """Befunde und Hinweise zu einem Schalentext."""
    befunde = []
    hinweise = []

    for name, anf, zeichen in ZUWEISUNG.findall(text):
        befunde.append('A  Zuweisung %s=%s\\%s - die Schale legt Backslash und '
                       '%s ab, kein Steuerzeichen'
                       % (name, anf or '', zeichen, zeichen))

    for muster, wie in EINZELZEICHEN:
        if muster.search(text):
            befunde.append('B  %s bekommt zwei Zeichen statt einem' % wie)

    # Tabulator und Wagenruecklauf gehoeren nicht MITTEN in eine Zeile - dort
    # trennen sie Argumente. Am Zeilenanfang sind sie Einrueckung eines
    # mehrzeiligen Schalenskripts und voellig ueblich.
    kern = '\n'.join(z.lstrip(' \t') for z in text.split('\n'))
    for zeichen, bez in (('\t', 'Tabulator'), ('\r', 'Wagenruecklauf')):
        if zeichen in kern:
            befunde.append('C  ECHTER %s mitten in der Kommandozeile' % bez)
    # Ein Zeilenumbruch AUSSERHALB von Anfuehrungszeichen ist ein mehrzeiliges
    # Schalenskript - voellig ueblich. Innerhalb war ein Steuerzeichen als
    # DATEN gemeint, und dann ist die Frage berechtigt, ob es dort ankommt.
    if '\n' in in_anfuehrung(text):
        befunde.append('C  ECHTER Zeilenumbruch INNERHALB von Anfuehrungszeichen')

    if not befunde:
        for m in re.finditer(r'\\([a-zA-Z0-9])', text):
            hinweise.append('\\' + m.group(1))
    return befunde, sorted(set(hinweise))


NUR_VARIABLE = re.compile(r'^\s*\$([A-Za-z_]\w*)\s*$')


def anweisung_ab(quelle, i):
    """Vom Zuweisungszeichen bis zum Strichpunkt - Literale uebersprungen."""
    n = len(quelle)
    while i < n:
        c = quelle[i]
        if c in '\'"':
            i = ende_literal(quelle, i)
            continue
        if c == ';':
            return i
        i += 1
    return n


def zuweisungen(quelle, name):
    """Alle Rumpfe von  $name = …;  und  $name .= …;  in dieser Datei.

    DAS HAEUFIGSTE MUSTER UEBERHAUPT - und der Grund, warum dieses Werkzeug
    beim ersten Anlauf blind war: der Befund von MG iSmart stand nicht in der
    Klammer von exec(), sondern zwei Zeilen darueber in $cmd.
    """
    aus = []
    for m in re.finditer(r'\$' + re.escape(name) + r'\s*\.?=\s*(?![=>])', quelle):
        ende = anweisung_ab(quelle, m.end())
        aus.append((m.start(), quelle[m.end():ende]))
    return aus


def datei_pruefen(pfad):
    """Rueckgabe: Liste (zeile, aufruf, befunde, hinweise, ausschnitt)."""
    try:
        quelle = open(pfad, 'r', encoding='utf-8', errors='replace').read()
    except OSError:
        return []
    endung = os.path.splitext(pfad)[1].lower()
    if endung in ('.php', '.cgi', '.html'):
        muster = PHP_AUFRUF
    elif endung in ('.pl', '.pm'):
        muster = PERL_AUFRUF
    elif endung == '.py':
        muster = PY_AUFRUF
    else:
        return []

    perl = endung in ('.pl', '.pm')
    aus = []
    gesehen = set()
    for m in muster.finditer(quelle):
        # qx{ … } und Backticks SIND der Befehl. system(...) bekommt einen
        # Ausdruck mit Stringliteralen - der wird gelesen wie in PHP, sonst
        # zaehlt die Einrueckung des Quelltextes als Kommandozeile mit.
        roh_perl = perl and m.group(1) == 'qx'
        if perl:
            ausdruck = perl_argument(quelle, m.end())
        else:
            ausdruck = ohne_escapeshellarg(php_argument(quelle, m.end()))
        # Steht in der Klammer nur eine Variable, wird die Zeichenkette
        # woanders gebaut. Dann werden ihre Zuweisungen geprueft.
        stellen = []
        v = NUR_VARIABLE.match(ausdruck)
        if v:
            for pos, rumpf in zuweisungen(quelle, v.group(1)):
                stellen.append((pos, rumpf, '$' + v.group(1)))
            if not stellen:
                continue
        else:
            stellen.append((m.start(), ausdruck, ''))

        for pos, rumpf, ueber in stellen:
            if (pfad, pos) in gesehen:
                continue
            gesehen.add((pfad, pos))
            if not perl:
                rumpf = ohne_escapeshellarg(rumpf)
            if len(rumpf) > 4000:
                rumpf = rumpf[:4000]
            text = rumpf if roh_perl else schalentext(rumpf)
            befunde, hinweise = pruefe_text(text)
            if not befunde and not hinweise:
                continue
            if hinweise and LOEST_SELBST.search(text):
                hinweise = [h + ' (Empfaenger loest selbst auf)' for h in hinweise]
            zeile = quelle.count('\n', 0, pos) + 1
            kurz = re.sub(r'\s+', ' ', rumpf.strip())[:110]
            aufruf = m.group(1) + (' ueber ' + ueber if ueber else '')
            aus.append((zeile, aufruf, befunde, hinweise, kurz))
    return aus


def plugin_pruefen(ordner, lang=False):
    befunde_gesamt = 0
    hinweise_gesamt = 0
    zeilen = []
    for wurzel, verz, dateien in os.walk(ordner):
        verz[:] = [v for v in verz if v not in ('__pycache__', '.git')]
        for d in sorted(dateien):
            pfad = os.path.join(wurzel, d)
            for zeile, aufruf, befunde, hinweise, kurz in datei_pruefen(pfad):
                rel = os.path.relpath(pfad, ordner).replace('\\', '/')
                if befunde:
                    befunde_gesamt += len(befunde)
                    zeilen.append('    BEFUND  %s:%d  (%s)' % (rel, zeile, aufruf))
                    for b in befunde:
                        zeilen.append('            ' + b)
                    zeilen.append('            ' + kurz)
                elif hinweise:
                    hinweise_gesamt += len(hinweise)
                    if lang:
                        zeilen.append('    hinweis %s:%d  %s'
                                      % (rel, zeile, ', '.join(hinweise)))
                        zeilen.append('            ' + kurz)
    return befunde_gesamt, hinweise_gesamt, zeilen


def main():
    argv = sys.argv[1:]
    lang = '--lang' in argv
    argv = [a for a in argv if a != '--lang']
    hier = os.path.dirname(os.path.abspath(__file__))
    if '--alle' in argv:
        eltern = os.path.dirname(hier)
        ordner = sorted(os.path.join(eltern, d) for d in os.listdir(eltern)
                        if os.path.isfile(os.path.join(eltern, d, 'plugin.cfg')))
    else:
        ordner = [os.path.abspath(a) for a in argv]
    if not ordner:
        print(__doc__)
        return 2

    schlimm = 0
    print('%-48s %8s %9s' % ('Plugin', 'Befunde', 'Hinweise'))
    print('-' * 70)
    for o in ordner:
        b, h, zeilen = plugin_pruefen(o, lang)
        if b:
            schlimm += 1
        print('%-48s %8s %9d' % (os.path.basename(o), b if b else 'keine', h))
        for z in zeilen:
            print(z)
    print('-' * 70)
    print('%d Linien geprueft, %d mit BEFUND.' % (len(ordner), schlimm))
    if not lang:
        print('Die Hinweise zeigt --lang. Sie sind meistens richtig - '
              'printf, awk, sed und tr loesen selbst auf.')
    return 1 if schlimm else 0


if __name__ == '__main__':
    sys.exit(main())
