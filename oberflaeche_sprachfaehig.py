#!/usr/bin/env python3
"""Holt die deutschen Textknoten einer PHP-Oberflaeche in Sprachschluessel.

Gedacht fuer Altbestand, dessen Oberflaeche ihre Texte unmittelbar im
Quelltext traegt. Ersetzt jeden uebersetzbaren Textknoten durch
<?= $L['ABSCHNITT.Knnn'] ?> und schreibt die deutschen Werte in eine INI.

    python3 oberflaeche_sprachfaehig.py --schau <index.php>
    python3 oberflaeche_sprachfaehig.py <index.php> <language_de.ini> [ABSCHNITT]

Angefasst wird nur der HTML-Bereich ausserhalb von <?php … ?>, <style> und
<script>. Uebersprungen wird alles, was nicht nach Sprache aussieht: Pfade,
Adressen, MQTT-Themen, Dateinamen, reine Zahlen und Zeichen.
"""
import re
import sys
from pathlib import Path

# Was kein uebersetzbarer Text ist, sondern Technik.
TECHNIK = re.compile(r'''^(
      [/.]                    # Pfade und Dateinamen
    | https?://
    | \w+\.(php|jpg|xml|json|ini|log|txt|html)\b
    | [\w-]+/[\w/{}<>-]*$     # MQTT-Themen wie intercom/trigger/NAME
    | \?\w+=
    | &\w+;?
    | [\d\s.,:%-]+$
)''', re.X)


def uebersetzbar(s):
    s = s.strip()
    if len(s) < 3 or TECHNIK.match(s):
        return False
    # Mindestens drei Buchstaben am Stueck - sonst ist es Auszeichnung.
    ohne = re.sub(r'&[a-zA-Z]+;', 'x', s)
    return bool(re.search(r'[A-Za-zÄÖÜäöüß]{3}', ohne))


def bereiche_ohne_code(t):
    """Spannen (Anfang, Ende) des HTML-Bereichs liefern."""
    aus, pos = [], 0
    muster = re.compile(r'<\?.*?\?>|<style\b.*?</style>|<script\b.*?</script>', re.S | re.I)
    for m in muster.finditer(t):
        if m.start() > pos:
            aus.append((pos, m.start()))
        pos = m.end()
    if pos < len(t):
        aus.append((pos, len(t)))
    return aus


def main():
    args = sys.argv[1:]
    schau = '--schau' in args
    args = [a for a in args if a != '--schau']
    if not args:
        print(__doc__)
        return 2
    quelle = Path(args[0])
    abschnitt = args[2] if len(args) > 2 else 'UI'
    t = quelle.read_text(encoding='utf-8')

    treffer = []
    for a, b in bereiche_ohne_code(t):
        for m in re.finditer(r'>([^<>]+)<', t[a:b]):
            if uebersetzbar(m.group(1)):
                treffer.append((a + m.start(1), a + m.end(1), m.group(1)))

    treffer.sort()
    eintraege, neu = [], t
    for i, (s, e, text) in enumerate(reversed(treffer), 1):
        nr = len(treffer) - i + 1
        key = 'K%03d' % nr
        eintraege.append((key, ' '.join(text.split())))
        neu = neu[:s] + "<?= $L['%s.%s'] ?>" % (abschnitt, key) + neu[e:]
    eintraege.reverse()

    for key, wert in eintraege:
        print('%s | %s' % (key, wert))
    print('--- %d Textknoten' % len(eintraege))
    if schau:
        return 0

    quelle.write_text(neu, encoding='utf-8')
    ini = Path(args[1])
    alt = ini.read_text(encoding='utf-8').rstrip('\n') if ini.is_file() else ''
    zeilen = '\n'.join('%s = "%s"' % (k, w.replace('"', "'")) for k, w in eintraege)
    ini.write_text(alt + '\n\n[%s]\n' % abschnitt + zeilen + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
