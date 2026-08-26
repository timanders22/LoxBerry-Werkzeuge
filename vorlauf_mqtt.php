<?php
/* Wie vorlauf.php, zusaetzlich wird die Abfragezeichenkette aus der
 * Umgebungsvariablen TEST_QUERY nach $_GET uebernommen - PHP im
 * Kommandozeilenbetrieb tut das von sich aus nicht. */
require_once getenv('TEST_VORLAUF');
$tq = (string) getenv('TEST_QUERY');
if ($tq !== '') {
    parse_str($tq, $_GET);
    $_SERVER['QUERY_STRING'] = $tq;
}
