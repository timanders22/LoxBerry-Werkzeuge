<?php
/* Wird per auto_prepend_file eingehaengt.
 *
 * Wie vorlauf.php - dazu fuellt es $_GET aus QUERY_STRING und $_POST aus
 * der Umgebungsvariablen PRUEF_POST (JSON).
 *
 * WARUM ES DAS BRAUCHT: PHP fuellt unter der Kommandozeile $_GET NICHT aus
 * QUERY_STRING - weder mit variables_order=EGPCS noch mit
 * register_argc_argv=0; beides am 20.08.2026 gemessen, beide Male blieb
 * $_GET leer. Ein Prueflauf gegen eine Oberflaeche mit ?form=<reiter> misst
 * ohne diesen Vorlauf also IMMER den Vorgabereiter und sieht dabei aus, als
 * habe er alle fuenf geprueft. Das ist die Klasse "ein Pruefstand, der nicht
 * dem Geraet entspricht, misst den Pruefstand".
 *
 * Es wird ausdruecklich NICHTS zurechtgebogen: Werte kommen so an, wie sie
 * in der Adresse stehen. parse_str() macht dieselbe Zerlegung wie der
 * Webserver.
 *
 * NACHTRAG 13.09.2026: dazu der Vorgabewert fuer $_SERVER['REQUEST_METHOD']
 * am Dateiende. Er fehlte hier, waehrend vorlauf.php ihn seit je setzt - und
 * ohne ihn meldete JEDE Seite, die REQUEST_METHOD ohne isset() liest, unter
 * PHP 7.4 einen HINWEIS und unter 8.4 eine WARNUNG, auf jedem Reiter neu.
 * Gemessen an APC-UPS 1.2.8: zehn Scheinbefunde in einem Lauf. Auf dem Geraet
 * kann das nicht auftreten, die Webserver-SAPI setzt REQUEST_METHOD immer -
 * es war also ein Befund am Pruefstand, keiner am Plugin. Ueber den ganzen
 * Bestand nachgemessen (256 Linien mit Oberflaeche, je unter 7.4 und 8.4):
 * 111 Linien verlieren mit diesem Nachtrag 1026 Scheinbefunde, 513 je
 * PHP-Fassung; keine Linie bekommt etwas dazu.
 */

$GLOBALS['_BEFUNDE'] = array();

set_error_handler(function ($stufe, $text, $datei, $zeile) {
    $namen = array(
        E_WARNING => 'WARNUNG', E_NOTICE => 'HINWEIS', E_DEPRECATED => 'VERFALL',
        E_USER_WARNING => 'WARNUNG', E_USER_NOTICE => 'HINWEIS',
        E_USER_DEPRECATED => 'VERFALL', E_RECOVERABLE_ERROR => 'FEHLER',
    );
    $n = isset($namen[$stufe]) ? $namen[$stufe] : ('STUFE' . $stufe);
    $GLOBALS['_BEFUNDE'][] = $n . '|' . $text . '|' . basename($datei) . ':' . $zeile;
    return true;    // PHP-eigene Ausgabe unterdruecken
});

register_shutdown_function(function () {
    $letzt = error_get_last();
    if ($letzt && in_array($letzt['type'], array(E_ERROR, E_PARSE, E_CORE_ERROR, E_COMPILE_ERROR), true)) {
        $GLOBALS['_BEFUNDE'][] = 'FATAL|' . $letzt['message'] . '|' . basename($letzt['file']) . ':' . $letzt['line'];
    }
    $einmalig = array_values(array_unique($GLOBALS['_BEFUNDE']));
    if ($einmalig) {
        file_put_contents('php://stderr', "\n###BEFUNDE###\n" . implode("\n", $einmalig) . "\n");
    }
});

$qs = getenv('QUERY_STRING');
if ($qs !== false && $qs !== '') {
    $g = array();
    parse_str($qs, $g);
    $_GET = $g;
    $_REQUEST = array_merge($_REQUEST, $g);
}

$pj = getenv('PRUEF_POST');
if ($pj !== false && $pj !== '') {
    $p = json_decode($pj, true);
    if (is_array($p)) {
        $_POST = $p;
        $_REQUEST = array_merge($_REQUEST, $p);
        if (getenv('REQUEST_METHOD') === false) {
            $_SERVER['REQUEST_METHOD'] = 'POST';
        }
    }
}

/* Der Vorgabewert - NACH dem POST-Zweig, damit ein POST-Lauf 'POST' behaelt.
 * Wortgleich mit vorlauf.php: gesetzt wird nur, was nicht schon dasteht. */
if (!isset($_SERVER['REQUEST_METHOD'])) {
    $_SERVER['REQUEST_METHOD'] = 'GET';
}
