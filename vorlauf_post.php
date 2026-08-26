<?php
/* Wie vorlauf.php, zusaetzlich: fuellt $_POST aus einer JSON-Datei.
 *
 * Damit laesst sich ein abgeschicktes Formular nachstellen, ohne einen
 * Webserver zu brauchen - die Voraussetzung fuer den Wirkungstest
 * "ueberlebt der eine Formularzweig die Werte des anderen?".
 */

$GLOBALS['_BEFUNDE'] = array();

set_error_handler(function ($stufe, $text, $datei, $zeile) {
    $namen = array(
        E_WARNING => 'WARNUNG', E_NOTICE => 'HINWEIS', E_DEPRECATED => 'VERFALL',
        E_USER_WARNING => 'WARNUNG', E_USER_NOTICE => 'HINWEIS',
        E_USER_DEPRECATED => 'VERFALL', E_STRICT => 'STRENG',
        E_RECOVERABLE_ERROR => 'FEHLER',
    );
    $n = isset($namen[$stufe]) ? $namen[$stufe] : ('STUFE' . $stufe);
    $GLOBALS['_BEFUNDE'][] = $n . '|' . $text . '|' . basename($datei) . ':' . $zeile;
    return true;
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

$_SERVER['SCRIPT_NAME'] = '/admin/plugins/pruefling/index.php';
$_SERVER['REQUEST_URI']  = '/admin/plugins/pruefling/index.php';
$_SERVER['HTTP_HOST']    = 'loxberry';
$_SERVER['SERVER_NAME']  = 'loxberry';
$_SERVER['REMOTE_ADDR']  = '192.168.1.99';
$_SERVER['HTTPS']        = '';

$_postdatei = getenv('PRUEF_POST');
if ($_postdatei && is_file($_postdatei)) {
    $_daten = json_decode((string) file_get_contents($_postdatei), true);
    if (is_array($_daten)) {
        $_POST = $_daten;
        $_REQUEST = array_merge($_REQUEST, $_daten);
        $_SERVER['REQUEST_METHOD'] = 'POST';
        $_SERVER['CONTENT_TYPE'] = 'application/x-www-form-urlencoded';
    }
} else {
    $_SERVER['REQUEST_METHOD'] = 'GET';
}
