#!/usr/bin/env python3
"""Baut eine einsprachige templates/help/help.html auf den vorgesehenen
LoxBerry-Mechanismus um.

Belegt an libs/phplib/loxberry_web.php: LBWeb::gethelp() sucht
templates/plugins/<ordner>/help/<name>.html, leitet daraus <name>.ini ab und
gibt den Namen an LBSystem::readlanguage(). Dieses sucht die Sprachdateien
NICHT neben der Hilfe, sondern unter templates/plugins/<ordner>/lang/ als
<name>_de.ini und <name>_en.ini.

Ergebnis je Plugin:
    templates/help/help.html          Geruest mit <TMPL_VAR HILFE.Knn>
    templates/lang/help_de.ini        die deutschen Texte
    templates/lang/help_en.ini        muss von Hand uebersetzt werden

    python3 hilfe_umbauen.py <Pluginordner> [...]        umbauen
    python3 hilfe_umbauen.py --schau <Pluginordner> [...] nur zeigen

Die Auszeichnung (<b>, <i>, <a href>) bleibt im Wert stehen - Hilfetexte
werden roh ausgegeben, nicht ueber xx_e(). Entitaeten wie &uuml; werden zu
echten UTF-8-Zeichen, weil die Hausregeln das fuer Sprachdateien verlangen.
Doppelte Anfuehrungszeichen verschwinden aus dem Wert: parse_ini_file wuerde
am zweiten abschneiden.
"""
import html
import re
import sys
from pathlib import Path

# Diese Entitaeten bleiben stehen - sie haben in HTML eine eigene Bedeutung
# oder sind als echtes Zeichen unsichtbar und damit in einer INI gefaehrlich.
BEHALTEN = {'amp', 'lt', 'gt', 'quot', 'apos', 'nbsp', 'shy'}

# Blockelemente, deren Inhalt ein eigener Sprachschluessel wird. Sie
# verschachteln sich nicht ineinander, deshalb genuegt ein einfaches Muster.
BLOECKE = ('h1', 'h2', 'h3', 'h4', 'p', 'li', 'dt', 'dd', 'caption', 'figcaption',
           'td', 'th')


def entitaeten_aufloesen(s):
    def ersetze(m):
        return m.group(0) if m.group(1) in BEHALTEN else html.unescape(m.group(0))
    return re.sub(r'&(\w+);', ersetze, s)


def anfuehrungszeichen(s):
    """Doppelte Anfuehrungszeichen aus dem Wert entfernen.

    In Attributen werden sie einfach, im Fliesstext typografisch. Sonst
    schneidet parse_ini_file den Wert am zweiten Anfuehrungszeichen ab -
    genau der Fehler, der in Smartmeter und VolkswagenID steckte.
    """
    s = re.sub(r'(\w+)="([^"]*)"', r"\1='\2'", s)
    stueck = s.split('"')
    if len(stueck) == 1:
        return s
    aus = stueck[0]
    for i, teil in enumerate(stueck[1:]):
        aus += ('„' if i % 2 == 0 else '“') + teil
    return aus


def wert(roh):
    # Im Quelltext umbrochene Bindestrich-Woerter wieder zusammenziehen.
    # "Loxone-\nEnergiemanager" wurde sonst zu "Loxone- Energiemanager" -
    # und zwar nicht erst hier: so stand es schon auf dem Bildschirm.
    s = re.sub(r'(?<=\w)-\s*\n\s*(?=\w)', '-', roh)
    s = re.sub(r'\s+', ' ', s).strip()
    s = entitaeten_aufloesen(s)
    return anfuehrungszeichen(s)


def zerlegen(text, ab=0):
    """Gibt (geruest, [(schluessel, wert), ...]) zurueck.

    'ab' erlaubt einen zweiten Durchgang ueber eine schon umgebaute Datei,
    ohne die vergebenen Schluessel noch einmal zu benutzen.
    """
    eintraege = []
    zaehler = [ab]

    def ersetze(m):
        tag, attr, inhalt = m.group(1), m.group(2) or '', m.group(3)
        if '<TMPL_VAR' in inhalt:
            return m.group(0)
        w = wert(inhalt)
        if not w or not re.search(r'\w', w):
            return m.group(0)
        zaehler[0] += 1
        s = 'K%02d' % zaehler[0]
        eintraege.append((s, w))
        return '<%s%s><TMPL_VAR HILFE.%s></%s>' % (tag, attr, s, tag)

    muster = re.compile(r'<(' + '|'.join(BLOECKE) + r')(\s[^>]*)?>(.*?)</\1>',
                        re.S | re.I)
    geruest = muster.sub(ersetze, text)
    return geruest, eintraege


def ini_schreiben(pfad, eintraege, sprache):
    kopf = (
        '; Hilfetexte, %s. Gehoert zu templates/help/help.html.\n'
        '; LBWeb::gethelp() leitet den Namen dieser Datei aus dem Namen der\n'
        '; Hilfedatei ab und sucht sie in templates/lang/ - nicht neben der\n'
        '; Hilfe. Jeder Wert steht in doppelten Anfuehrungszeichen und enthaelt\n'
        '; selbst keine; Auszeichnung bleibt roh, die Hilfe wird nicht\n'
        '; maskiert ausgegeben.\n\n[HILFE]\n' % sprache)
    zeilen = ''.join('%s = "%s"\n' % (s, w) for s, w in eintraege)
    Path(pfad).write_text(kopf + zeilen, encoding='utf-8')


def wurzel(p):
    p = Path(p)
    if (p / 'plugin.cfg').is_file():
        return p
    treffer = [d for d in sorted(p.iterdir()) if d.is_dir() and (d / 'plugin.cfg').is_file()]
    return treffer[0] if len(treffer) == 1 else p


def main():
    args = sys.argv[1:]
    nur_schauen = '--schau' in args
    args = [a for a in args if a != '--schau']
    if not args:
        print(__doc__)
        return 2
    for arg in args:
        w = wurzel(arg)
        hilfe = w / 'templates/help/help.html'
        if not hilfe.is_file():
            print('%-44s keine help.html' % Path(arg).name)
            continue
        text = hilfe.read_text(encoding='utf-8')
        ini = w / 'templates/lang/help_de.ini'
        alt = []
        if ini.is_file():
            for z in ini.read_text(encoding='utf-8').splitlines():
                m = re.match(r'^(K\d+)\s*=\s*"(.*)"\s*$', z)
                if m:
                    alt.append((m.group(1), m.group(2)))
        ab = max([int(s[1:]) for s, _ in alt], default=0)
        geruest, neue = zerlegen(text, ab)
        if not neue:
            print('%-44s nichts mehr zu tun (%d Schluessel)' % (Path(arg).name, len(alt)))
            continue
        print('=== %s  (%d neu, %d gesamt)' % (Path(arg).name, len(neue), len(alt) + len(neue)))
        for s, wt in neue:
            print('%s | %s' % (s, wt))
        if nur_schauen:
            continue
        (w / 'templates/lang').mkdir(parents=True, exist_ok=True)
        hilfe.write_text(geruest, encoding='utf-8')
        ini_schreiben(ini, alt + neue, 'deutsch')
    return 0


if __name__ == '__main__':
    sys.exit(main())
