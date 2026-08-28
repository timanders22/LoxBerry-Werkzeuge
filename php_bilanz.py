#!/usr/bin/env python3
"""Ersatz fuer 'php -l', solange kein PHP-Aufruf zur Verfuegung steht.

Die Hausregel sagt: eine fehlende PHP-Syntaxpruefung ist KEIN Grund, sie zu
ueberspringen. Ersatzweise werden Klammer-, Zeichenketten- und
<?php/?>-Bilanz gezaehlt und das Ergebnis offengelegt.

Der Zaehler kennt einfache und doppelte Zeichenketten, Heredoc und Nowdoc,
//-, #- und /* */-Kommentare sowie den HTML-Bereich ausserhalb von <?php.

Was er NICHT kann: fehlende Semikolons, falsche Argumentzahlen, unbekannte
Funktionen. Er ersetzt 'php -l' nicht, er verkleinert nur die Luecke.

    python3 php_bilanz.py <datei.php> [...]
    python3 php_bilanz.py --plugin <Pluginordner>

Zusaetzlich mit --plugin: undefinierte Aufrufe eigener Funktionen, doppelte
Definitionen und Funktionen, die niemand aufruft.
"""
import re
import sys
from pathlib import Path


def bilanz(pfad):
    s = Path(pfad).read_text(encoding='utf-8', errors='replace')
    i, n = 0, len(s)
    in_php = False
    stapel = []
    fehler = []
    zeile = 1
    offen = 0
    while i < n:
        c = s[i]
        if c == '\n':
            zeile += 1
            i += 1
            continue
        if not in_php:
            if s.startswith('<?php', i) or s.startswith('<?=', i):
                in_php = True
                offen += 1
                i += 5 if s.startswith('<?php', i) else 3
                continue
            i += 1
            continue
        if s.startswith('?>', i):
            in_php = False
            offen -= 1
            i += 2
            continue
        if s.startswith('//', i) or c == '#':
            j = s.find('\n', i)
            k = s.find('?>', i)
            if k != -1 and (j == -1 or k < j):
                i = k
                continue
            if j == -1:
                break
            i = j
            continue
        if s.startswith('/*', i):
            j = s.find('*/', i + 2)
            if j == -1:
                fehler.append(f'{pfad}:{zeile}: Blockkommentar wird nicht geschlossen')
                break
            zeile += s.count('\n', i, j)
            i = j + 2
            continue
        if c in '\'"':
            j = i + 1
            while j < n:
                if s[j] == '\\':
                    j += 2
                    continue
                if s[j] == c:
                    break
                j += 1
            if j >= n:
                art = 'einfache' if c == "'" else 'doppelte'
                fehler.append(f'{pfad}:{zeile}: {art} Zeichenkette wird nicht geschlossen')
                break
            zeile += s.count('\n', i, j)
            i = j + 1
            continue
        m = re.match(r"<<<[ \t]*(['\"]?)([A-Za-z_]\w*)\1\r?\n", s[i:])
        if m:
            marke = m.group(2)
            ende = re.search(r'^[ \t]*' + marke + r'\b', s[i + m.end():], re.M)
            if not ende:
                fehler.append(f'{pfad}:{zeile}: Heredoc {marke} wird nicht geschlossen')
                break
            j = i + m.end() + ende.end()
            zeile += s.count('\n', i, j)
            i = j
            continue
        if c in '([{':
            stapel.append((c, zeile))
            i += 1
            continue
        if c in ')]}':
            paar = {')': '(', ']': '[', '}': '{'}[c]
            if not stapel:
                fehler.append(f'{pfad}:{zeile}: schliessendes {c} ohne oeffnendes {paar}')
            elif stapel[-1][0] != paar:
                o, z = stapel.pop()
                fehler.append(f'{pfad}:{zeile}: {c} passt nicht zu {o} aus Zeile {z}')
            else:
                stapel.pop()
            i += 1
            continue
        i += 1
    for o, z in stapel:
        fehler.append(f'{pfad}:{z}: {o} wird nie geschlossen')
    if offen not in (0, 1):
        fehler.append(f'{pfad}: <?php/?>-Bilanz ist {offen}, erwartet 0 oder 1')
    return fehler


SCHLUESSELWOERTER = {
    'if', 'for', 'foreach', 'while', 'switch', 'function', 'array', 'list',
    'isset', 'unset', 'empty', 'echo', 'print', 'return', 'catch', 'elseif',
    'use', 'fn', 'match', 'and', 'or', 'new', 'do', 'exit', 'die', 'require',
    'include', 'require_once', 'include_once', 'declare', 'global', 'static',
}


def nur_code(s):
    """Kommentare und Zeichenketten durch Leerzeichen ersetzen, Laenge erhalten.

    Ohne das findet die Aufrufsuche Funktionsnamen in Kommentaren
    ("Bis 0.9.0 standen hier db_mqtt_senden() …") und meldet sie als
    undefiniert. Am 10.08.2026 waren vier von fuenf Befunden genau das.
    """
    aus = []
    i, n = 0, len(s)
    in_php = False
    while i < n:
        c = s[i]
        if not in_php:
            if s.startswith('<?php', i) or s.startswith('<?=', i):
                in_php = True
                k = 5 if s.startswith('<?php', i) else 3
                aus.append(s[i:i + k])
                i += k
                continue
            aus.append(' ' if c != '\n' else '\n')
            i += 1
            continue
        if s.startswith('?>', i):
            in_php = False
            aus.append('  ')
            i += 2
            continue
        if s.startswith('//', i) or c == '#' or s.startswith('/*', i):
            if s.startswith('/*', i):
                j = s.find('*/', i + 2)
                j = n if j == -1 else j + 2
            else:
                j = s.find('\n', i)
                k = s.find('?>', i)
                if k != -1 and (j == -1 or k < j):
                    j = k
                elif j == -1:
                    j = n
            aus.append(''.join('\n' if ch == '\n' else ' ' for ch in s[i:j]))
            i = j
            continue
        if c in '\'"':
            j = i + 1
            while j < n:
                if s[j] == '\\':
                    j += 2
                    continue
                if s[j] == c:
                    break
                j += 1
            j = min(j + 1, n)
            aus.append(''.join('\n' if ch == '\n' else ' ' for ch in s[i:j]))
            i = j
            continue
        m = re.match(r"<<<[ \t]*(['\"]?)([A-Za-z_]\w*)\1\r?\n", s[i:])
        if m:
            marke = m.group(2)
            ende = re.search(r'^[ \t]*' + marke + r'\b', s[i + m.end():], re.M)
            j = n if not ende else i + m.end() + ende.end()
            aus.append(''.join('\n' if ch == '\n' else ' ' for ch in s[i:j]))
            i = j
            continue
        aus.append(c)
        i += 1
    return ''.join(aus)


# Eingebaute PHP-Funktionen, die zufaellig wie ein Plugin-Kuerzel aussehen.
# parse_ini_file wurde gemeldet, weil irgendein Plugin eine Funktion mit dem
# Praefix 'parse' definiert - damit galt 'parse' als eigenes Kuerzel.
EINGEBAUT = {
    'parse_ini_file', 'parse_ini_string', 'parse_url', 'parse_str',
    'array_map', 'array_filter', 'array_merge', 'str_replace', 'str_repeat',
    'file_get_contents', 'file_put_contents', 'is_array', 'in_array',
    # mt_* wurde an Matter2Lox gemeldet: dessen Kuerzel ist 'mt', und damit
    # galt der Zufallszahlengeber von PHP als eigene, nie definierte Funktion.
    'mt_rand', 'mt_srand', 'mt_getrandmax',
    # Weitere Kuerzel, die im Hause vorkommen und mit PHP kollidieren.
    'str_pad', 'str_split', 'str_contains', 'str_starts_with', 'str_ends_with',
    'is_string', 'is_numeric', 'is_file', 'is_dir', 'is_null', 'is_int',
    'array_key_exists', 'array_keys', 'array_values', 'array_slice',
}


def funktionen(dateien):
    defs, aufrufe, alle = set(), {}, []
    unbewacht = set()   # Namen, die MINDESTENS EINMAL ohne Wache stehen
    for f in dateien:
        roh = Path(f).read_text(encoding='utf-8', errors='replace')
        # DEFINITIONEN UND AUFRUFE MUESSEN DENSELBEN TEXT LESEN.
        #
        # Bis zum 28.08.2026 wurden die Definitionen im ROHTEXT gesucht, die
        # Aufrufe dagegen in nur_code(). Damit galt jede JavaScript-Funktion
        # im <script>-Bereich als PHP-Funktion, die niemand aufruft: 'zeige'
        # in den meisten Linien, 'activate' und 'mwTtsMode' in Robonect.
        t = nur_code(roh)
        # 'function &name()' gibt eine Referenz zurueck - das & gehoert zur
        # Definition, nicht zum Namen. Ohne das optionale & galt eine solche
        # Funktion als nie definiert (gefunden am 10.08.2026 an BatterieBMS).
        #
        # \bfunction\b statt \bfunction: ohne die zweite Wortgrenze griff das
        # Muster auch in function_exists( - nach "function" steht dort ein
        # Unterstrich, und der ist ein Wortzeichen. Jedes Plugin im Hause
        # benutzt function_exists, jedes bekam '_exists' als doppelt
        # definierte, nie aufgerufene Funktion gemeldet - und weil "doppelt
        # definiert" den Rueckgabewert auf 1 setzt, war dieses Werkzeug ueber
        # den ganzen Bestand rot.
        for m in re.finditer(r'\bfunction\b\s*&?\s*([a-zA-Z_]\w*)\s*\(', t):
            nm = m.group(1)
            defs.add(nm)
            # EINE BEWACHTE DEFINITION IST KEINE DOPPELDEFINITION.
            #
            # if (!function_exists('x')) { function x() ... } ist das
            # Hausmuster fuer Funktionen, die in webfrontend/html UND in
            # webfrontend/htmlauth stehen muessen: auf dem installierten
            # System sind das getrennte Baeume, ein require ueber die Grenze
            # gibt es nicht. Die Wache verhindert das "cannot redeclare" im
            # entpackten Archiv, wo beide Dateien zusammenkommen.
            #
            # Ohne diese Ausnahme meldete das Werkzeug Raumklima rot wegen
            # rk_e - einer Stelle, die genau richtig gebaut ist. Zwei
            # UNBEWACHTE Definitionen bleiben ein Befund.
            # Gesucht wird im ROHTEXT, nicht in t: nur_code() entfernt die
            # Zeichenketten, und damit auch den Namen im function_exists('x').
            # Die Stellen laufen zwischen beiden Texten auseinander, deshalb
            # wird die Wache in der ganzen Datei gesucht - wer den Namen dort
            # ueberhaupt nennt, hat die Doppelung bedacht.
            alle.append(nm)
            if not re.search(r"function_exists\s*\(\s*['\"]" + re.escape(nm)
                             + r"['\"]\s*\)", roh):
                unbewacht.add(nm)
        for m in re.finditer(r'(?<![\$>:\w])([a-z_]\w*)\s*\(', t):
            nm = m.group(1)
            if nm in SCHLUESSELWOERTER or nm in EINGEBAUT:
                continue
            aufrufe.setdefault(nm, []).append((f, t[:m.start()].count('\n') + 1))
    # Kuerzel des Plugins aus den Definitionen ableiten
    kuerzel = {d.split('_')[0] for d in defs if '_' in d}
    eigen = {a for a in aufrufe if a.split('_')[0] in kuerzel and '_' in a}
    # Doppelt ist erst ein Befund, wenn MINDESTENS EINE der Stellen ohne
    # Wache steht. Zwei bewachte sind das Hausmuster fuer die getrennten
    # Baeume; eine bewachte PLUS eine ungedeckte ist dagegen genau der
    # Fall, der im entpackten Archiv "cannot redeclare" wirft - und der
    # rutschte bis zur Eichung am 28.08.2026 durch.
    doppelt = sorted({x for x in alle if alle.count(x) > 1 and x in unbewacht})
    return sorted(eigen - defs), doppelt, sorted(d for d in defs if d not in aufrufe), aufrufe


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    if args[0] == '--plugin':
        wurzel = Path(args[1])
        dateien = sorted(str(f) for f in wurzel.rglob('*.php'))
    else:
        # Ein Ordner als Argument ist der naheliegende Aufruf und war bis zum
        # 29.08.2026 ein Absturz mit IsADirectoryError - mitten in der
        # Pruefkette, also genau dort, wo eine Ausnahme wie ein Befund
        # aussieht. Ein Ordner wird jetzt aufgeloest wie bei --plugin.
        dateien = []
        for a in args:
            p = Path(a)
            if p.is_dir():
                dateien += sorted(str(f) for f in p.rglob('*.php'))
            else:
                dateien.append(a)
    if not dateien:
        # Ein Plugin OHNE PHP ist kein Fehlerfall - LoxoneIcons ist eine reine
        # Symbolsammlung. Bis zum 28.08.2026 gab das Werkzeug hier 2 zurueck
        # und stand damit in jeder Kette rot. Ein nicht vorhandener Ordner
        # bleibt dagegen ein Aufrufproblem.
        if args[0] == '--plugin' and Path(args[1]).is_dir():
            print('Keine PHP-Dateien in %s - entfaellt.' % args[1])
            return 0
        print('Keine PHP-Dateien gefunden.')
        return 2

    alles = []
    for f in dateien:
        alles += bilanz(f)
    if alles:
        for f in alles:
            print('   ', f)
        print(f'{len(alles)} Beanstandungen in der Bilanz')
    else:
        print(f'Klammer-, Zeichenketten- und Tag-Bilanz: fehlerfrei in {len(dateien)} Dateien')

    fehlend, doppelt, ungenutzt, _ = funktionen(dateien)
    print('  undefinierte Aufrufe eigener Funktionen:', fehlend or 'keine')
    print('  doppelt definiert:', doppelt or 'keine')
    print('  definiert, aber nirgends aufgerufen:', ungenutzt or 'keine')
    return 1 if (alles or fehlend or doppelt) else 0


if __name__ == '__main__':
    sys.exit(main())
