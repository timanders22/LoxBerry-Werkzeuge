<?php
/* Wird per auto_prepend_file eingehaengt.
 *
 * Zweck: einen eigenen Fehler-Aufnehmer setzen. set_error_handler() wird
 * unabhaengig von error_reporting() gerufen - deshalb sieht der Lauf auch die
 * Verfallswarnungen, die die Plugins selbst mit
 * "error_reporting(E_ALL & ~E_DEPRECATED & ~E_NOTICE)" stilllegen.
 */

$GLOBALS['_BEFUNDE'] = array();
$GLOBALS['_UNTERDRUECKT'] = array();
$GLOBALS['_UNTERDRUECKT_AN'] = (getenv('RENDERN_UNTERDRUECKT') === '1');

/* Netzsperre fuer rendern.py - SEIT 11.09.2026, und NUR wenn rendern.py
 * RENDERN_NETZSPERRE=1 setzt. Andere Werkzeuge, die diese Datei einhaengen,
 * bleiben unberuehrt.
 *
 * Anlass: ein Lauf ueber den ganzen Arbeitsordner schickte Anfragen an
 * api.awattar.de und bekam "429 Too Many Requests" - das Rendern
 * verbrauchte das Kontingent eines fremden Dienstes, und die Warnung stand
 * dann als Befund im Lauf. Die Wrapper fuer http, https, ftp und ftps werden
 * durch einen ersetzt, der nur mitschreibt und scheitert; curl lenkt
 * rendern.py ueber einen Sperr-Proxy. Die Warnung, die das Scheitern selbst
 * ausloest, ist KEIN Befund des Plugins und wird nicht aufgenommen - was
 * das Plugin danach aus dem Fehlschlag macht, schon.
 * Nicht erfasst: rohe Sockets (fsockopen, stream_socket_client,
 * socket_connect) - PHP laesst keine eigenen Transporte zu. */
$GLOBALS['_NETZ'] = array();
if (getenv('RENDERN_NETZSPERRE') === '1') {
    class RendernNetzsperre
    {
        public $context;

        public function stream_open($pfad, $modus, $optionen, &$geoeffnet)
        {
            $GLOBALS['_NETZ'][] = $pfad;
            return false;
        }

        public function url_stat($pfad, $flags)
        {
            $GLOBALS['_NETZ'][] = $pfad;
            return false;
        }
    }
    foreach (array('http', 'https', 'ftp', 'ftps') as $_w) {
        if (in_array($_w, stream_get_wrappers(), true)) {
            stream_wrapper_unregister($_w);
            stream_wrapper_register($_w, 'RendernNetzsperre', STREAM_IS_URL);
        }
    }
    unset($_w);
}

set_error_handler(function ($stufe, $text, $datei, $zeile) {
    if (strpos($text, 'RendernNetzsperre') !== false) {
        return true;    // das Scheitern der Sperre selbst - kein Befund
    }
    $namen = array(
        E_WARNING => 'WARNUNG', E_NOTICE => 'HINWEIS', E_DEPRECATED => 'VERFALL',
        E_USER_WARNING => 'WARNUNG', E_USER_NOTICE => 'HINWEIS',
        E_USER_DEPRECATED => 'VERFALL', E_STRICT => 'STRENG', E_RECOVERABLE_ERROR => 'FEHLER',
    );
    $n = isset($namen[$stufe]) ? $namen[$stufe] : ('STUFE' . $stufe);
    /* Mit @ unterdrueckt - SEIT 25.09.2026, und NUR wenn rendern.py
     * RENDERN_UNTERDRUECKT=1 setzt (sonst wie bisher: alles ist Befund, die
     * anderen Werkzeuge, die diese Datei einhaengen, messen unveraendert).
     * Anlass: Zendure 0.9.25/0.9.26, drei Zeilen @fopen/@file_get_contents mit
     * geprueftem Rueckgabewert, sieben Warnungen als Befund gezaehlt.
     * Erkennung, gemessen unter 7.4.33 und 8.4.24: unter @ liefert
     * error_reporting() 0 (7.4) bzw. hoechstens 4437 (8.x), ini_get() behaelt
     * den erklaerten Wert. Nur wenn BEIDES zutrifft - der Typ fehlt im
     * wirksamen Wert UND der wirksame Wert weicht vom erklaerten ab -, war es
     * @. Ein Plugin, das selbst error_reporting(E_ALL & ~E_DEPRECATED ...)
     * setzt, aendert beide gleich: seine Verfallsmeldungen bleiben Befund
     * (Kopf dieser Datei). Unterdrueckt wird nicht verschwiegen: eigener
     * Block ###UNTERDRUECKT###, als letzter geschrieben. */
    if ($GLOBALS['_UNTERDRUECKT_AN']) {
        $wirksam = error_reporting();
        if (($wirksam & $stufe) === 0 && $wirksam !== (int) ini_get('error_reporting')) {
            $GLOBALS['_UNTERDRUECKT'][] = $n . '|' . $text . '|' . basename($datei) . ':' . $zeile;
            return true;
        }
    }
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
    // Nach den Befunden, damit rendern.py beide Abschnitte sauber trennt.
    if ($GLOBALS['_NETZ']) {
        file_put_contents('php://stderr', "\n###NETZ###\n"
            . implode("\n", array_values(array_unique($GLOBALS['_NETZ']))) . "\n");
    }
    // Als letzter Block: rendern.lauf() trennt ihn zuerst ab.
    if ($GLOBALS['_UNTERDRUECKT']) {
        file_put_contents('php://stderr', "\n###UNTERDRUECKT###\n"
            . implode("\n", array_values(array_unique($GLOBALS['_UNTERDRUECKT']))) . "\n");
    }
});

$_SERVER['REQUEST_METHOD'] = isset($_SERVER['REQUEST_METHOD']) ? $_SERVER['REQUEST_METHOD'] : 'GET';
$_SERVER['SCRIPT_NAME'] = '/admin/plugins/pruefling/index.php';
$_SERVER['REQUEST_URI']  = '/admin/plugins/pruefling/index.php';
$_SERVER['HTTP_HOST']    = 'loxberry';
$_SERVER['SERVER_NAME']  = 'loxberry';
$_SERVER['REMOTE_ADDR']  = '192.168.1.99';
$_SERVER['HTTPS']        = '';
