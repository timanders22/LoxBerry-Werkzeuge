<?php
/**
 * Hilfsprogramm zu tote_helfer.py: zerlegt eine PHP-Datei mit PHPS EIGENEM
 * Zerteiler und meldet, was Definition und was Benutzung ist.
 *
 * WARUM ES DIESE DATEI GIBT
 * -------------------------
 * tote_helfer.py hat bis 02.09.2026 jeden Namen gezaehlt, der irgendwo im
 * Text stand - auch in einem KOMMENTAR. Damit galt eine Funktion als
 * aufgerufen, sobald irgendwo ueber sie geredet wurde. Gemessen an
 * Spotpreis aWATTar: der Lauf meldete "alle aufgerufen", waehrend drei
 * Funktionen tot waren; ihre Namen standen in Erklaerkommentaren.
 *
 * Ein Zerteiler kennt den Unterschied. T_COMMENT und T_DOC_COMMENT werden
 * hier gar nicht erst betrachtet.
 *
 * Ein selbst geschriebener Zerteiler taugt dafuer nicht: der zweite Anlauf
 * dieses Werkzeugs hielt das "?>" in der Zeichenkette
 * '<?xml version="1.0" encoding="utf-8"?>' fuer das Ende des PHP-Bereichs
 * und war ab dort blind. Aufgefallen ist es nur, weil eine absichtlich
 * eingebaute tote Funktion NICHT gefunden wurde.
 *
 * AUSGABE, eine Zeile je Fund, mit senkrechtem Strich getrennt:
 *
 *     DEF|<name>|<zeile>     eine Definition
 *     USE|<name>|<zeile>     eine Benutzung
 *
 * Als Benutzung zaehlen:
 *   - ein Bezeichner, dem eine offene Klammer folgt und dem KEIN
 *     'function' vorausgeht (der gewoehnliche Aufruf),
 *   - ein Bezeichner ohne Klammer, der weder Definition noch Schluesselwort
 *     ist - das faengt Rueckrufe wie array_map('spot_x', ...) mit ab, wenn
 *     der Name ohne Anfuehrungszeichen dasteht,
 *   - eine ZEICHENKETTE, deren Inhalt genau ein Bezeichner ist. usort(),
 *     array_map() und register_shutdown_function() bekommen den Namen so.
 *
 * Aufruf: php tote_helfer_token.php <datei.php>
 */
if ($argc < 2) {
    fwrite(STDERR, "Aufruf: php tote_helfer_token.php <datei.php>\n");
    exit(2);
}
$roh = @file_get_contents($argv[1]);
if ($roh === false) {
    fwrite(STDERR, "nicht lesbar: " . $argv[1] . "\n");
    exit(2);
}
$tok = @token_get_all($roh);
if (!is_array($tok)) {
    fwrite(STDERR, "nicht zerlegbar: " . $argv[1] . "\n");
    exit(2);
}

/* Der Zerteiler liefert Kommentare und Leerraum als eigene Marken. Fuer die
 * Nachbarschaftsfragen ("steht davor ein 'function'?") stoeren sie, also
 * werden sie herausgenommen - NICHT ueberlesen, sondern verworfen: was in
 * einem Kommentar steht, ist keine Benutzung. */
$m = array();
foreach ($tok as $t) {
    if (is_array($t)) {
        if ($t[0] === T_WHITESPACE || $t[0] === T_COMMENT || $t[0] === T_DOC_COMMENT) {
            continue;
        }
        $m[] = array($t[0], $t[1], $t[2]);
    } else {
        $m[] = array(-1, $t, 0);
    }
}

$n = count($m);
for ($i = 0; $i < $n; $i++) {
    list($art, $text, $zeile) = $m[$i];

    if ($art === T_STRING) {
        $vorher = $i > 0 ? $m[$i - 1] : array(-1, '', 0);
        $nachher = $i + 1 < $n ? $m[$i + 1] : array(-1, '', 0);
        if ($vorher[0] === T_FUNCTION) {
            printf("DEF|%s|%d\n", $text, $zeile);
            continue;
        }
        /* Ein Pfeil oder zwei Doppelpunkte davor heisst: Methode eines
         * Objekts, nicht die gesuchte Funktion. Trotzdem als Benutzung
         * melden - der Name ist derselbe, und ein Werkzeug, das hier
         * unterscheidet, unterscheidet falsch, sobald jemand eine Klasse
         * einfuehrt. Lieber eine Benutzung zu viel als ein Fehlfund. */
        printf("USE|%s|%d\n", $text, $zeile);
        continue;
    }

    /* Zeichenketten: nur, wenn ihr Inhalt GENAU ein Bezeichner ist. Ein
     * Satz, in dem der Name vorkommt, ist keine Benutzung. */
    if ($art === T_CONSTANT_ENCAPSED_STRING) {
        $inhalt = substr($text, 1, -1);
        if (preg_match('/^[A-Za-z_][A-Za-z0-9_]*$/', $inhalt)) {
            printf("USE|%s|%d\n", $inhalt, $zeile);
        }
    }
}
