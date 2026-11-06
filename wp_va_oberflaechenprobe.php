<?php
/* Oberfläche 0.9.22 mit Hersteller vaillant rendern (WSL-Sandkasten).
 * Stufe A: ohne offene Adresse, Stufe B: mit offener Adresse, Stufe C: mit Anmeldung. */
$stufe = $argv[1];
$html = getenv('WPHTML');
putenv('LBHOMEDIR=/tmp/lbwr'); putenv('LBPPLUGINDIR=waermepumpe');
$_SERVER['REQUEST_METHOD'] = 'GET'; $_GET['form'] = 'settings'; $_SERVER['SCRIPT_NAME'] = '/admin/plugins/waermepumpe/index.php';
require $html . '/wp_lib.php';
$cfg = wp_config(); $cfg['hersteller'] = 'vaillant'; wp_config_write($cfg);
if ($stufe === 'B') { wp_va_browser_starten(); }
if ($stufe === 'C') {
    $g = wp_geheim(); $g['va_refresh'] = 'x.y.z'; wp_geheim_write($g);
    $b64 = function ($s) { return rtrim(strtr(base64_encode($s), '+/', '-_'), '='); };
    wp_va_erneuerung_merken($b64('{}') . '.' . $b64('{"exp":1893456000,"typ":"Offline"}') . '.s', array());
}
chdir($html);
ob_start();
include $html . '/index.php';
$out = ob_get_clean();
file_put_contents('/tmp/lbwr/seite_' . $stufe . '.html', $out);
