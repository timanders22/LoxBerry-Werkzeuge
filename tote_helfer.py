#!/usr/bin/env python3
"""Findet PHP-Funktionen, die ein Plugin definiert und nie aufruft.

Der Anlass, 20.08.2026 am Anker-SOLIX-Plugin: `ak_cache()` stand seit 0.9.0
in der Bibliothek und wurde von keiner einzigen Zeile aufgerufen. Die Hilfe
und die README versprachen aber genau das, was diese Funktion geliefert
haette - die Rohdaten der Cloud mit den ECHTEN Feldnamen. Der Knopf
"Rohdaten als JSON ansehen" zeigte statt dessen das bereits umgesetzte
Abbild. Fuer eine Fassung, deren erklaerter Zweck das Nachmessen der
Feldnamen ist, war das die teuerste Luecke - und keine der acht
Pruefwerkzeuge hat sie gesehen, weil keines nach toten Helfern sucht.

Ein toter Helfer ist selten nur ueberfluessig. Er ist meistens der Rest
einer Absicht, die nie zu Ende gebaut wurde - und irgendwo steht ein Text,
der sie trotzdem verspricht.

Rein lesend. Aufruf:

    python3 tote_helfer.py PLUGINORDNER [PLUGINORDNER ...]
    python3 tote_helfer.py --alle          alle Plugins neben diesem Ordner

Ausgabe je Plugin eine Zeile; mit Fund dahinter die Namen.
Rueckgabewert 1, sobald irgendwo ein toter Helfer steckt.

GRENZEN - ausdruecklich, damit niemand mehr hineinliest, als drinsteht:

  * Gesucht wird in den .php-Dateien UND in den Skripten des Plugins
    (.sh .bash .pl .py .cgi .pm, dazu alles unter cron/ und jede
    endungslose Datei mit Shebang). In den Skripten zaehlt nur die Form
    `name(` - ein blosser Name in Prosa oder in einer README gilt NICHT
    als Aufruf, sonst wuerde eine erwaehnte Funktion nie mehr auffallen.

    NACHGETRAGEN am 20.08.2026, und zwar nach Schaden: der Lauf ueber
    Weissware 0.9.10 meldete `ww_wache_grenze()` als tot. Sie wurde
    daraufhin in 0.9.11 entfernt - aufgerufen wurde sie aber, naemlich in
    bin/dienst.sh ueber `php -r "... echo ww_wache_grenze();"`. Genau der
    Fall, den dieser Abschnitt vorher als Grenze BENANNTE. Ein Vorbehalt
    im Kopf einer Datei haelt niemanden auf; die Pruefung muss es tun.
  * Ein Aufruf ueber einen variablen Namen ($f = 'ak_cache'; $f();) oder
    ueber call_user_func() faellt durch. Beides ist in dieser Linie
    unueblich, aber es kommt vor.
  * Funktionen, die eine Attrappe oder ein Prueflauf aufruft, gelten hier
    als tot - das ist gewollt: sie gehoeren nicht ins ausgelieferte Plugin.
  * Ein Fund ist kein Fehler, sondern eine FRAGE: wird der Helfer gebraucht
    und fehlt der Aufruf, oder ist er ueberfluessig? Das entscheidet ein
    Mensch, nicht dieses Werkzeug.
"""
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
WURZEL = HIER.parent

# Diese Namen ruft nicht das Plugin, sondern LoxBerry oder PHP selbst auf.
FREMDAUFRUF = {
    # Rueckruffunktionen und Einstiegspunkte
    'main',
}
# Praefixe, die auf einen Einstiegspunkt deuten (kein Helfer).
EINSTIEG = ('__',)


SKRIPT_ENDUNGEN = ('.sh', '.bash', '.pl', '.py', '.cgi', '.pm')


def php_dateien(ordner):
    return sorted(f for f in ordner.rglob('*.php') if f.is_file())


def skript_dateien(ordner):
    """Alles, was ein PHP-Schnipsel ueber `php -r` aufrufen koennte.

    Ausdruecklich NICHT dabei: .md, .html, .txt, .json. Dort steht Prosa,
    und ein erwaehnter Name ist kein Aufruf.
    """
    raus = []
    for f in sorted(ordner.rglob('*')):
        if not f.is_file():
            continue
        if f.suffix.lower() in SKRIPT_ENDUNGEN or 'cron' in [t.lower() for t in f.parts]:
            raus.append(f)
            continue
        if not f.suffix:                      # endungslos: nur mit Shebang
            try:
                if f.open('rb').read(2) == b'#!':
                    raus.append(f)
            except OSError:
                pass
    return raus


def untersuchen(ordner):
    """Rueckgabe: (definiert, tot, fremd) - Mengen von Funktionsnamen.

    `fremd` sind die, die in PHP niemand ruft, wohl aber ein Skript.
    """
    quellen = {}
    for f in php_dateien(ordner):
        quellen[f] = f.read_text(encoding='utf-8', errors='replace')

    skripte = []
    for f in skript_dateien(ordner):
        try:
            skripte.append(f.read_text(encoding='utf-8', errors='replace'))
        except OSError:
            pass
    skripttext = '\n'.join(skripte)

    definiert = {}
    for f, s in quellen.items():
        for m in re.finditer(r'^\s*function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', s, re.M):
            definiert.setdefault(m.group(1), f)

    gesamt = '\n'.join(quellen.values())
    tot = []
    fremd = []
    for name, wo in sorted(definiert.items()):
        if name in FREMDAUFRUF or name.startswith(EINSTIEG):
            continue
        # Aufruf heisst: der Name taucht auf, OHNE dass 'function' davorsteht.
        # Auch ein Verweis als Zeichenkette zaehlt - array('ak_x') etwa geht
        # an usort() und ist ein Aufruf, nur ein spaeterer.
        treffer = 0
        # KORRIGIERT beim ersten Lauf, 20.08.2026: der Ausschluss enthielt '>'
        # und warf damit jeden Methodenaufruf ueber $this->name() weg. Folge
        # waren Fehlfunde in jeder Datei mit einer Klasse - im Smartmeter-
        # Plugin stand sml_crc16 als tot da, obwohl es zweimal gerufen wird.
        # Ein Werkzeug, das Fehlfunde liefert, wird beim dritten Mal nicht
        # mehr angesehen.
        for m in re.finditer(r'(?<![A-Za-z0-9_$])' + re.escape(name) + r'(?![A-Za-z0-9_])', gesamt):
            davor = gesamt[max(0, m.start() - 40):m.start()]
            if re.search(r'function\s+$', davor):
                continue
            treffer += 1
        if treffer == 0:
            # Zweite Runde: ruft ein Skript sie ueber `php -r`? Dort zaehlt
            # nur die Form name( - siehe GRENZEN im Kopf.
            if re.search(r'(?<![A-Za-z0-9_$])' + re.escape(name) + r'\s*\(', skripttext):
                fremd.append((name, wo))
            else:
                tot.append((name, wo))
    return definiert, tot, fremd


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--alle' in sys.argv:
        args = [str(p) for p in sorted(WURZEL.glob('LoxBerry-Plugin-*')) if p.is_dir()]
    if not args:
        print(__doc__.strip().splitlines()[0])
        print('Aufruf: python3 tote_helfer.py PLUGINORDNER [...] | --alle')
        return 2

    schlecht = 0
    for a in args:
        p = Path(a)
        if not p.is_dir():
            print('%-46s kein Ordner' % a)
            continue
        definiert, tot, fremd = untersuchen(p)
        if not definiert:
            print('%-46s keine PHP-Funktionen' % p.name)
            continue
        if tot:
            schlecht = 1
            print('%-46s %3d Funktionen, %d ohne Aufruf:' % (p.name, len(definiert), len(tot)))
            for name, wo in tot:
                print('%-46s     %s  (%s)' % ('', name, wo.relative_to(p)))
        else:
            print('%-46s %3d Funktionen, alle aufgerufen' % (p.name, len(definiert)))
        # Diese Zeile ist die Lehre aus ww_wache_grenze: aus PHP ruft sie
        # niemand, aus einem Skript schon. Wer sie entfernt, bricht den Aufruf.
        for name, wo in fremd:
            print('%-46s     %s  (%s) - kein PHP-Aufruf, ABER aus einem Skript gerufen: NICHT entfernen'
                  % ('', name, wo.relative_to(p)))
    print()
    print('Ein Fund ist eine Frage, kein Urteil: wird der Helfer gebraucht und')
    print('fehlt der Aufruf, oder ist er ueberfluessig? Und vor allem - steht')
    print('irgendwo ein Text, der verspricht, was er geliefert haette?')
    return schlecht


if __name__ == '__main__':
    sys.exit(main())
