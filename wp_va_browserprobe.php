<?php
/* Prüfstand 0.9.22 Browser-Anmeldung am Gerät. Keine Zugangsdaten, kein echter
 * Code. Ausgegeben werden nur Gründe, HTTP-Codes und Feldnamen. */
$teil = isset($argv[1]) ? $argv[1] : 'fluss';
putenv('LBHOMEDIR=' . (getenv('WP_HOME') ?: '/opt/loxberry'));
putenv('LBPPLUGINDIR=' . ($teil === 'jwt' ? 'wp_sandkasten_jwt' : 'waermepumpe'));
require getenv('WPLIB') ?: '/tmp/wp22/wp_lib.php';
echo 'Realm: ', wp_va_realm(wp_config()['marke'], wp_config()['land']), "
";

if ($teil === 'fluss') {
    $vorher = wp_geheim();
    $refresh_vorher = md5($vorher['va_refresh']);
    echo "0 ohne offene Adresse: ", implode(' ', wp_va_browser_einloesen('enduservaillant.page.link://login?state=x&code=abcdefghijk')), "\n";
    $adr = wp_va_browser_starten();
    $l = wp_va_browser_lage();
    echo "1 Adresse erzeugt, Host: ", parse_url($adr, PHP_URL_HOST), " state-Laenge ", strlen($l['state']),
         " Rechte ", substr(sprintf('%o', fileperms(wp_va_browser_datei())), -4), "\n";
    $ch = curl_init($adr);
    curl_setopt_array($ch, array(CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 20, CURLOPT_HTTPHEADER => array('User-Agent: Mozilla/5.0')));
    $t = (string) curl_exec($ch);
    echo "2 Adresse im Abruf: HTTP ", curl_getinfo($ch, CURLINFO_HTTP_CODE), ", Formular ",
         preg_match('#login-actions/authenticate#', $t) ? 'ja' : 'nein', ", altcha ", substr_count(strtolower($t), 'altcha'), "\n";
    echo "3 fremder state: ", implode(' ', wp_va_browser_einloesen('enduservaillant.page.link://login?state=falsch&code=abcdefghijk')), "\n";
    echo "4 Muell ohne Code: ", implode(' ', wp_va_browser_einloesen('hallo welt')), "\n";
    echo "5 richtiger state, erfundener Code: ", implode(' ', wp_va_browser_einloesen(
        'enduservaillant.page.link://login?state=' . $l['state'] . '&session_state=x&code=erfunden-0000-1111')), "\n";
    echo "6 nackter erfundener Code: ", implode(' ', wp_va_browser_einloesen('erfunden-0000-2222')), "\n";
    echo "7 Adresse noch offen nach Fehlschlag: ", wp_va_browser_lage() ? 'ja' : 'nein', "\n";
    echo "8 va_refresh unveraendert: ", md5(wp_geheim()['va_refresh']) === $refresh_vorher ? 'ja' : 'NEIN', "\n";
    @unlink(wp_va_browser_datei());
    echo "9 aufgeraeumt: ", is_file(wp_va_browser_datei()) ? 'NEIN' : 'ja', "\n";
}

if ($teil === 'jwt') {
    // Erfundenes JWT mit typ/exp - prüft nur das Auslesen, kein echtes Merkmal.
    $b64 = function ($s) { return rtrim(strtr(base64_encode($s), '+/', '-_'), '='); };
    $jwt = $b64('{"alg":"HS512"}') . '.' . $b64('{"exp":1893456000,"typ":"Offline","x":"??>>"}') . '.sig';
    wp_va_erneuerung_merken($jwt, array('refresh_expires_in' => 0));
    $l = wp_va_erneuerung_lage();
    echo "J1 typ=", $l['typ'], " bis=", date('Y-m-d', $l['bis']), " sekunden=", $l['sekunden'], " angemeldet>0=", $l['angemeldet'] > 0 ? 'ja' : 'nein', "\n";
    echo "J2 Merkmal nicht in Datei: ", strpos((string) file_get_contents(wp_datadir() . '/va_erneuerung.json'), 'sig') === false ? 'ja' : 'NEIN', "\n";
    wp_va_erneuerung_merken('kein.jwt', array());
    $l = wp_va_erneuerung_lage();
    echo "J3 kaputtes Merkmal: typ='", $l['typ'], "' bis=", $l['bis'], " sekunden=", $l['sekunden'], "\n";
    $p = wp_paths();
    exec('rm -rf ' . escapeshellarg($p['datadir']) . ' ' . escapeshellarg($p['configdir']) . ' ' . escapeshellarg($p['logdir']));
    echo "J4 Sandkasten entfernt: ", is_dir($p['datadir']) ? 'NEIN' : 'ja', "\n";
}
