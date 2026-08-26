<?php
/* Wird per auto_prepend_file eingehaengt.
 *
 * Zweck: einen eigenen Fehler-Aufnehmer setzen. set_error_handler() wird
 * unabhaengig von error_reporting() gerufen - deshalb sieht der Lauf auch die
 * Verfallswarnungen, die die Plugins selbst mit
 * "error_reporting(E_ALL & ~E_DEPRECATED & ~E_NOTICE)" stilllegen.
 */

$GLOBALS['_BEFUNDE'] = array();

set_error_handler(function ($stufe, $text, $datei, $zeile) {
    $namen = array(
        E_WARNING => 'WARNUNG', E_NOTICE => 'HINWEIS', E_DEPRECATED => 'VERFALL',
        E_USER_WARNING => 'WARNUNG', E_USER_NOTICE => 'HINWEIS',
        E_USER_DEPRECATED => 'VERFALL', E_STRICT => 'STRENG', E_RECOVERABLE_ERROR => 'FEHLER',
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

$_SERVER['REQUEST_METHOD'] = isset($_SERVER['REQUEST_METHOD']) ? $_SERVER['REQUEST_METHOD'] : 'GET';
$_SERVER['SCRIPT_NAME'] = '/admin/plugins/pruefling/index.php';
$_SERVER['REQUEST_URI']  = '/admin/plugins/pruefling/index.php';
$_SERVER['HTTP_HOST']    = 'loxberry';
$_SERVER['SERVER_NAME']  = 'loxberry';
$_SERVER['REMOTE_ADDR']  = '192.168.1.99';
$_SERVER['HTTPS']        = '';
