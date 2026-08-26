#!/usr/bin/env python3
"""Stellt die Sprachdateien vom Entitaeten- auf den UTF-8-Hausstandard um.

Beschluss vom 14.08.2026. Der Grund ist nicht Geschmack, sondern eine
Fehlerklasse: die Doppelmaskierung xx_e(xx_t('KEY')) zeigt den Entitaetentext
woertlich an ("Pumpenw&auml;chter"). Sie ist NUR moeglich, solange der Wert
Entitaeten enthaelt. Mit direkten Zeichen darf htmlspecialchars folgenlos
zweimal laufen.

Regel:
  - Jede Entitaet, die ein SICHTBARES Zeichen darstellt, wird zum Zeichen.
  - &nbsp; und &shy; bleiben Entitaet: ein unsichtbares Zeichen im Quelltext
    ist eine Wartungsfalle - es sieht aus wie ein normales Leerzeichen.
  - &amp; &lt; &gt; &quot; &apos; bleiben Entitaet: sie sind in HTML
    bedeutungstragend, ein direktes < wuerde Markup erzeugen.
"""
import re, sys
from pathlib import Path

ERSETZUNG = {
    # Umlaute und Eszett
    '&auml;': 'ä', '&ouml;': 'ö', '&uuml;': 'ü',
    '&Auml;': 'Ä', '&Ouml;': 'Ö', '&Uuml;': 'Ü',
    '&szlig;': 'ß', '&#246;': 'ö',
    # Striche, Anfuehrungszeichen, Aufzaehlung
    '&mdash;': '—', '&ndash;': '–', '&minus;': '−',
    '&bdquo;': '„', '&ldquo;': '“', '&rdquo;': '”',
    '&hellip;': '…', '&bull;': '•', '&middot;': '·',
    # Pfeile
    '&rarr;': '→', '&larr;': '←',
    # Einheiten und Zeichen
    '&deg;': '°', '&euro;': '€', '&sect;': '§',
    '&sup2;': '²', '&sup3;': '³', '&#8322;': '₂',
    '&le;': '≤', '&ge;': '≥', '&times;': '×',
}
BLEIBT = {'&nbsp;', '&shy;', '&amp;', '&lt;', '&gt;', '&quot;', '&apos;'}


def umstellen(text):
    for k, v in ERSETZUNG.items():
        text = text.replace(k, v)
    return text


if __name__ == '__main__':
    wurzel = Path(sys.argv[1] if len(sys.argv) > 1 else 'stand')
    trocken = '--schreiben' not in sys.argv
    gesamt = 0
    linien = 0
    rest = {}
    for d in sorted(wurzel.iterdir()):
        if not d.is_dir():
            continue
        n = 0
        for f in sorted(d.rglob('language_*.ini')):
            t = f.read_text(encoding='utf-8')
            neu = umstellen(t)
            if neu != t:
                n += sum(t.count(k) for k in ERSETZUNG)
                if not trocken:
                    f.write_text(neu, encoding='utf-8')
            # Was bleibt an Entitaeten uebrig?
            for m in set(re.findall(r'&#?\w+;', neu)):
                if m not in BLEIBT:
                    rest.setdefault(d.name, set()).add(m)
        if n:
            linien += 1
            gesamt += n
            print('%-24s %5d Entitaeten umgestellt' % (d.name, n))
    print('-' * 50)
    print('%d Entitaeten in %d Linien%s' % (gesamt, linien, '' if not trocken else '  (Probelauf)'))
    if rest:
        print('\nNicht umgestellt (bitte ansehen):')
        for k, v in rest.items():
            print('  %-24s %s' % (k, ' '.join(sorted(v))))
