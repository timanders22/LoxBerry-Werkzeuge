#!/usr/bin/env python3
"""Baut den Zweisprachigkeits-Mechanismus in ein Plugin ein.

Legt an bzw. ergaenzt:
  webfrontend/htmlauth/<kuerzel>_lib.php   xx_sprache() und xx_t()
  templates/lang/language_de.ini            Geruest
  templates/lang/language_en.ini            Geruest

Die Sprachfunktionen sind bewusst eigenstaendig: sie berechnen den Pfad zu
den .ini-Dateien selbst und setzen kein xx_paths() voraus. So laesst sich
derselbe Block in jedes Plugin einsetzen, egal wie es sonst aufgebaut ist.

Aufruf:  sprache_einbauen.py <pluginordner> <kuerzel> [--schreiben]
"""
import re
import sys
from pathlib import Path

BLOCK = '''
/* ==================================================================
 * Sprache (Pflicht: Deutsch und Englisch)
 *
 * Englisch ist die Rueckfallebene, nicht Deutsch: wer eine dritte Sprache
 * eingestellt hat, versteht eher Englisch. Deshalb muss language_en.ini
 * immer vollstaendig sein.
 * ================================================================== */

function {p}_sprache()
{{
    $sprache = 'de';
    if (class_exists('LBSystem', false) && method_exists('LBSystem', 'lblanguage')) {{
        $sprache = LBSystem::lblanguage();
    }} elseif (getenv('LBLANG')) {{
        $sprache = getenv('LBLANG');
    }}
    $sprache = strtolower(substr((string) $sprache, 0, 2));
    return in_array($sprache, array('de', 'en'), true) ? $sprache : 'en';
}}

/**
 * Text zu einem Schluessel "ABSCHNITT.SCHLUESSEL".
 *
 * Ist der Schluessel unbekannt, wird er selbst zurueckgegeben - so faellt
 * beim Durchsehen sofort auf, was noch fehlt, statt dass die Seite leer
 * bleibt.
 */
function {p}_t($schluessel)
{{
    static $texte = null;
    if ($texte === null) {{
        // Installiert liegen die Dateien unter
        // <home>/templates/plugins/<ordner>/lang/ - der Ordnername ergibt
        // sich aus dem Ablageort dieser Datei.
        $home = getenv('LBHOMEDIR');
        if (!$home || !is_dir($home)) {{
            foreach (array('/opt/loxberry', '/home/loxberry/loxberry') as $k) {{
                if (is_dir($k)) {{ $home = $k; break; }}
            }}
        }}
        $ordner = basename(dirname(__FILE__));
        $pfad = $home . '/templates/plugins/' . $ordner . '/lang';
        if (!is_dir($pfad)) {{
            // Nicht installiert (Entwicklung): neben dem Plugin nachsehen.
            $pfad = dirname(dirname(dirname(__FILE__))) . '/templates/lang';
        }}
        $texte = @parse_ini_file($pfad . '/language_' . {p}_sprache() . '.ini',
                                 true, INI_SCANNER_RAW);
        if (!is_array($texte)) {{ $texte = array(); }}
        $rueck = @parse_ini_file($pfad . '/language_en.ini', true, INI_SCANNER_RAW);
        if (is_array($rueck)) {{ $texte = array_replace_recursive($rueck, $texte); }}
    }}
    list($a, $s) = array_pad(explode('.', $schluessel, 2), 2, '');
    return isset($texte[$a][$s]) ? $texte[$a][$s] : $schluessel;
}}
'''

INI_DE = '''; {name} - Deutsch
;
; Jeder hier benutzte Schluessel muss auch in language_en.ini stehen.
; Jeden Wert in doppelte Anfuehrungszeichen setzen: bei parse_ini_file
; beginnt mit ; ein Kommentar, und jede HTML-Entitaet endet auf ein
; Semikolon (&rarr; &ndash; &uuml;). Innerhalb eines Wertes darf kein
; doppeltes Anfuehrungszeichen stehen - HTML-Attribute deshalb einfach
; quoten: <span class='sm-mono'>.

[REITER]
EINSTELLUNGEN = "Einstellungen"
MQTT = "MQTT"
LOXONE = "Einbindung in Loxone"
TEST = "Test"
LOG = "Logdateien"

[LEGENDE]
LESEN = "Ansehen &mdash; fragt nur ab, ver&auml;ndert nichts"
TECHNIK = "Technische Auskunft &mdash; f&uuml;r die Fehlersuche"
AKTION = "L&ouml;st etwas aus &mdash; sendet oder ver&auml;ndert"

[ALLGEMEIN]
JA = "ja"
NEIN = "nein"
SPEICHERN = "Speichern"
'''

INI_EN = '''; {name} - English
;
; English is the fallback level: keys missing in another language are taken
; from here, so this file must always be complete.
; Quote every value - see the German file for the reason.

[REITER]
EINSTELLUNGEN = "Settings"
MQTT = "MQTT"
LOXONE = "Loxone integration"
TEST = "Test"
LOG = "Log files"

[LEGENDE]
LESEN = "View &mdash; reads only, changes nothing"
TECHNIK = "Technical information &mdash; for troubleshooting"
AKTION = "Triggers something &mdash; sends or changes"

[ALLGEMEIN]
JA = "yes"
NEIN = "no"
SPEICHERN = "Save"
'''


def main(ordner, kuerzel, schreiben=False):
    p = Path(ordner)
    ha = p / 'webfrontend/htmlauth'
    lib = ha / (kuerzel + '_lib.php')
    neu_angelegt = False

    if lib.is_file():
        t = lib.read_text(encoding='utf-8')
        if ('function ' + kuerzel + '_t(') in t:
            print('  %-38s Mechanismus schon vorhanden' % p.name[:38])
            return
        t = t.rstrip() + '\n' + BLOCK.format(p=kuerzel)
    else:
        neu_angelegt = True
        t = ('<?php\n/**\n * %s - gemeinsame Funktionen der Oberflaeche\n *\n'
             ' * Kompatibel mit PHP 7.4 und PHP 8.x (LoxBerry 3.x/4.x).\n */\n'
             % p.name) + BLOCK.format(p=kuerzel)

    name = p.name.replace('LoxBerry-Plugin-', '')
    lang = p / 'templates/lang'
    de = lang / 'language_de.ini'
    en = lang / 'language_en.ini'

    print('  %-38s %s%s%s' % (
        p.name[:38],
        ('lib NEU' if neu_angelegt else 'lib ergaenzt'),
        ('' if de.is_file() else ', de.ini'),
        ('' if en.is_file() else ', en.ini')))

    if not schreiben:
        return

    lib.write_text(t, encoding='utf-8')
    lang.mkdir(parents=True, exist_ok=True)
    if not de.is_file():
        de.write_text(INI_DE.format(name=name), encoding='utf-8')
    if not en.is_file():
        en.write_text(INI_EN.format(name=name), encoding='utf-8')

    # index.php muss die Bibliothek einbinden
    idx = ha / 'index.php'
    if idx.is_file():
        it = idx.read_text(encoding='utf-8')
        if (kuerzel + '_lib.php') not in it:
            it = re.sub(r"(require_once\s+'loxberry_web\.php';)",
                        r"\1\nrequire_once __DIR__ . '/" + kuerzel + "_lib.php';",
                        it, count=1)
            idx.write_text(it, encoding='utf-8')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], '--schreiben' in sys.argv)
