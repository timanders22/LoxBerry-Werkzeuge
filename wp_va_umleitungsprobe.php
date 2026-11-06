<?php
/* Nur LESEN, keine Zugangsdaten: Welche redirect_uri nimmt der Client myvaillant
 * an, und wie ist das ALTCHA-Widget eingestellt (automatisch oder Klick)? */
$basis = 'https://identity.vaillant-group.com/auth/realms/vaillant-germany-b2c';
function hole($url) {
    $ch = curl_init($url);
    curl_setopt_array($ch, array(CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 20,
        CURLOPT_HTTPHEADER => array('User-Agent: Mozilla/5.0')));
    $t = (string) curl_exec($ch);
    return array(curl_getinfo($ch, CURLINFO_HTTP_CODE), $t);
}
$ch_ = rtrim(strtr(base64_encode(hash('sha256', 'x', true)), '+/', '-_'), '=');
foreach (array('enduservaillant.page.link://login', 'http://localhost/', 'https://my.vaillant.de/', 'urn:ietf:wg:oauth:2.0:oob') as $ru) {
    list($c, $t) = hole($basis . '/protocol/openid-connect/auth?' . http_build_query(array(
        'response_type' => 'code', 'client_id' => 'myvaillant', 'redirect_uri' => $ru,
        'code_challenge_method' => 'S256', 'code_challenge' => $ch_)));
    $form = preg_match('#login-actions/authenticate#', $t) ? 'Anmeldeformular' : 'kein Formular';
    $fehler = preg_match('/(Invalid parameter[^<]*|Ungültige[^<]*|redirect_uri[^<]{0,40})/i', $t, $m) ? trim($m[1]) : '';
    echo str_pad($ru, 36), " HTTP $c  $form  $fehler\n";
}
list($c, $t) = hole($basis . '/protocol/openid-connect/auth?' . http_build_query(array(
    'response_type' => 'code', 'client_id' => 'myvaillant', 'redirect_uri' => 'enduservaillant.page.link://login',
    'code_challenge_method' => 'S256', 'code_challenge' => $ch_)));
preg_match_all('#<altcha-widget[^>]*>#i', $t, $w);
echo "Widget: ", implode(' || ', $w[0]), "\n";
preg_match_all('#<script[^>]*src="([^"]*altcha[^"]*)"#i', $t, $s);
echo "Skripte: ", implode(', ', $s[1]), "\n";
