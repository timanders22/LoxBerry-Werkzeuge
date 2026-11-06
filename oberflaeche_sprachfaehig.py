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
import os
import re
import subprocess
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


# Was wie Programmtext aussieht, ist keiner zum Uebersetzen.
#
# ERGAENZT 31.08.2026, nach einem gemessenen Schaden. Das Werkzeug hat PHP-CODE
# fuer einen deutschen Textknoten gehalten und ihn durch einen Sprachschluessel
# ersetzt:
#
#     if ($alter > $grenze && $wert < 5) {
#              wurde zu
#     if ($alter ><?= $L['UI.K002'] ?>< 5) {
#
# php -l danach: "Parse error: syntax error, unexpected token <". In der INI
# stand K002 = "$grenze && $wert". Der Grund steht in bereiche_ohne_code().
CODEZEICHEN = re.compile(r'[${};]|&&|\|\||->|::|=>|\$\w')


def uebersetzbar(s):
    s = s.strip()
    if len(s) < 3 or TECHNIK.match(s):
        return False
    if CODEZEICHEN.search(s):
        return False
    # Mindestens drei Buchstaben am Stueck - sonst ist es Auszeichnung.
    ohne = re.sub(r'&[a-zA-Z]+;', 'x', s)
    return bool(re.search(r'[A-Za-zÄÖÜäöüß]{3}', ohne))


def bereiche_ohne_code(t):
    """Spannen (Anfang, Ende) des HTML-Bereichs liefern.

    BERICHTIGT 31.08.2026: ein NICHT GESCHLOSSENER PHP-Block gehoert ganz zum
    Code, nicht zum HTML.

    Der Hausstandard laesst die letzte `?>` weg - das ist verbreitet und
    richtig. Das alte Muster `<\\?.*?\\?>` findet dann gar keinen Treffer mehr,
    `pos` bleibt stehen, und ALLES ab diesem `<?php` galt als HTML. Der Sucher
    `>([^<>]+)<` greift darin jedes Stueck zwischen einem `>` und einem `<` ab
    - also mitten aus einem Vergleich heraus.

    Gemessen am 31.08.2026: `if ($alter > $grenze && $wert < 5)` ergab den
    "Textknoten" ` $grenze && $wert `, und die Datei war nach dem Schreiben
    syntaktisch kaputt.
    """
    aus, pos = [], 0
    muster = re.compile(r'<\?.*?\?>|<style\b.*?</style>|<script\b.*?</script>',
                        re.S | re.I)
    for m in muster.finditer(t):
        if m.start() > pos:
            aus.append((pos, m.start()))
        pos = m.end()
    # Ein offener Block ab pos: alles Weitere ist Code.
    offen = t.find('<?', pos)
    ende = len(t) if offen < 0 else offen
    if pos < ende:
        aus.append((pos, ende))
    return aus


def php_binaer():
    """Ein PHP, das antwortet - oder None.

    Eigene Funktion, damit der Zweig "kein PHP" ueberhaupt eichbar ist. Unter
    Windows sucht CreateProcess die ausfuehrbare Datei im PATH des ELTERN-
    prozesses; ein Pruefstand kann ein systemweit eingetragenes php also gar
    nicht verstecken (am 31.08.2026 dreimal versucht und dreimal gemessen,
    dass es trotzdem gefunden wird). Der Zweig wird deshalb unmittelbar
    geeicht, nicht ueber die Umgebung.
    """
    for k in (os.environ.get('PHP84'), os.environ.get('PHP74'),
              r'C:\tmp\php-8.4.27-Win32-vs17-x64\php.exe',
              r'C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe', 'php'):
        if not k:
            continue
        try:
            if subprocess.run([k, '-v'], capture_output=True,
                              timeout=20).returncode == 0:
                return k
        except (OSError, subprocess.SubprocessError):
            continue
    return None


def main():
    args = sys.argv[1:]
    schau = '--schau' in args
    args = [a for a in args if a != '--schau']
    if not args:
        print(__doc__)
        return 2
    quelle = Path(args[0])
    abschnitt = args[2] if len(args) > 2 else 'UI'

    # DIES IST EIN UMBAUWERKZEUG, KEIN PRUEFER. Ohne --schau schreibt es in
    # beide angegebene Dateien. Wer es versehentlich mit zwei .php-Dateien
    # aufruft, bekommt eine umgebaute Oberflaeche und eine .php mit einem
    # angehaengten [UI]-Block - genau so geschehen am 28.08.2026.
    if not schau:
        if len(args) < 2:
            print('Ohne --schau werden ZWEI Pfade gebraucht: '
                  '<index.php> <language_de.ini>')
            return 2
        if not Path(args[1]).name.startswith('language_') \
                or not args[1].endswith('.ini'):
            print('ABGEWIESEN: der zweite Pfad muss eine language_*.ini sein, '
                  'nicht %r.\n'
                  'Dieses Werkzeug SCHREIBT in beide Dateien. Zum blossen '
                  'Ansehen: --schau' % args[1])
            return 2

    t = quelle.read_text(encoding='utf-8')
    # Die Zeilenenden der Quelle merken: write_text macht unter Windows aus
    # jedem \n ein \r\n und wuerde eine LF-Datei stumm umstellen.
    roh = quelle.read_bytes()
    crlf = roh.count(b'\r\n') > roh.count(b'\n') // 2

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

    # NICHTS ZU TUN HEISST NICHTS SCHREIBEN.
    #
    # Gefunden in der eigenen Eichung am 31.08.2026: ein zweiter Lauf ueber
    # eine bereits umgestellte Oberflaeche fand 0 Textknoten - und haengte
    # trotzdem einen LEEREN Abschnitt an die Sprachdatei. Die Oberflaeche blieb
    # byteweise gleich, die INI nicht. Beim dritten Lauf stuende der Abschnitt
    # zweimal da, und parse_ini_file nimmt den letzten.
    #
    # Das ist genau der Vorwurf, unter dem dieses Werkzeug im STAND steht:
    # es schreibt ohne Not.
    if not eintraege:
        print('Nichts zu tun - kein uebersetzbarer Textknoten gefunden. '
              'Es wurde NICHTS geschrieben.')
        return 0

    def ablegen(pfad, text, mit_crlf):
        b = text.encode('utf-8').replace(b'\r\n', b'\n')
        if mit_crlf:
            b = b.replace(b'\n', b'\r\n')
        pfad.write_bytes(b)

    # ------------------------------------------------------------------
    # DREI WACHEN VOR DEM SCHREIBEN - alle drei aus einem gemessenen Schaden.
    #
    # Bis zum 31.08.2026 hat dieses Werkzeug geschrieben und danach gehofft.
    # Es hat dabei PHP-Code durch einen Sprachschluessel ersetzt und die Datei
    # syntaktisch zerstoert (siehe bereiche_ohne_code). Ein Umbauwerkzeug, das
    # sein Ergebnis nicht misst, ist ein Zufallsgenerator mit Schreibrecht.
    # ------------------------------------------------------------------
    ini = Path(args[1])

    # 1. Ein Abschnitt, den es schon gibt, wird NICHT ein zweites Mal
    #    angehaengt. parse_ini_file nimmt bei einem doppelten Schluessel
    #    stillschweigend den LETZTEN - eine zweite [UI]-Sektion ueberschreibt
    #    die erste, ohne dass irgendetwas meldet.
    if ini.is_file():
        vorhanden = ini.read_text(encoding='utf-8', errors='replace')
        if re.search(r'(?m)^\s*\[' + re.escape(abschnitt) + r'\]\s*$', vorhanden):
            print('ABGEWIESEN: der Abschnitt [%s] steht in %s bereits.\n'
                  'Ein zweiter Abschnitt gleichen Namens ueberschreibt den '
                  'ersten stillschweigend (parse_ini_file nimmt den letzten).\n'
                  'Einen anderen Abschnittsnamen angeben oder den vorhandenen '
                  'von Hand zusammenfuehren.' % (abschnitt, ini.name))
            return 2

    # 2. Das ERGEBNIS wird gemessen, bevor es die Quelle ersetzt: erst in eine
    #    Nebendatei schreiben, php -l darueber, und nur bei sauberer Syntax
    #    umbenennen. Ohne PHP wird NICHT geschrieben - lieber gar nichts tun
    #    als ungeprueft eine Oberflaeche umbauen.
    php = php_binaer()
    if php is None:
        print('ABGEWIESEN: kein PHP gefunden. Dieses Werkzeug schreibt nur, '
              'wenn es das Ergebnis mit php -l nachmessen kann.\n'
              'Ueber PHP84=<pfad> einen Interpreter angeben - oder --schau '
              'benutzen.')
        return 2

    tmp = quelle.with_suffix(quelle.suffix + '.pruef.%d' % os.getpid())
    ablegen(tmp, neu, crlf)
    r = subprocess.run([php, '-l', str(tmp)], capture_output=True, text=True,
                       encoding='utf-8', errors='replace', timeout=60)
    if r.returncode != 0:
        meldung = ((r.stdout or '') + (r.stderr or '')).strip().splitlines()
        tmp.unlink()
        print('ABGEWIESEN: das Ergebnis ist syntaktisch KAPUTT - es wurde '
              'nichts geschrieben.\n   ' + '\n   '.join(meldung[:3]))
        print('Das heisst fast immer: ein Stueck PHP wurde fuer einen '
              'Textknoten gehalten. Mit --schau ansehen, welcher.')
        return 1

    # 3. Erst jetzt die Quelle ersetzen - und die INI danach.
    tmp.replace(quelle)
    iroh = ini.read_bytes() if ini.is_file() else b''
    icrlf = iroh.count(b'\r\n') > iroh.count(b'\n') // 2
    alt = ini.read_text(encoding='utf-8').rstrip('\n') if ini.is_file() else ''
    zeilen = '\n'.join('%s = "%s"' % (k, w.replace('"', "'")) for k, w in eintraege)
    ablegen(ini, alt + '\n\n[%s]\n' % abschnitt + zeilen + '\n', icrlf)
    print('\nGeschrieben: %s (Syntax mit php -l nachgemessen) und %s.'
          % (quelle.name, ini.name))
    print('NICHT geschrieben: die englische Sprachdatei. Der Hausstandard '
          'verlangt in beiden Dateien\ndieselbe Schluesselmenge - die %d neuen '
          'Schluessel fehlen dort jetzt und muessen\nnachgetragen werden.'
          % len(eintraege))
    return 0


if __name__ == '__main__':
    sys.exit(main())
