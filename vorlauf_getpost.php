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
