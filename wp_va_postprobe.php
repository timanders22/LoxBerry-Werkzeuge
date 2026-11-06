<?php
/* POST-Weg 0.9.22 im WSL-Sandkasten: ein Aufruf je Fall, weil index.php mit exit endet. */
$fall = $argv[1];
$html = getenv('WPHTML');
putenv('LBHOMEDIR=/tmp/lbwp2'); putenv('LBPPLUGINDIR=waermepumpe');
$_SERVER['REQUEST_METHOD'] = 'POST'; $_SERVER['SCRIPT_NAME'] = '/admin/plugins/waermepumpe/index.php';
require $html . '/wp_lib.php';
$cfg = wp_config(); $cfg['hersteller'] = 'vaillant'; wp_config_write($cfg);
$_POST['activetab'] = 'tab-settings';
if ($fall !== 'ohne_token') { $_POST['fmt'] = wp_formtoken(); }
if ($fall === 'start' || $fall === 'ohne_token') { $_POST['va_browser_start'] = '1'; }
if ($fall === 'falscher_state') { $_POST['va_browser_code'] = '1'; $_POST['va_code'] = 'enduservaillant.page.link://login?state=falsch&code=abcdefghijkl'; }
if ($fall === 'leer') { $_POST['va_browser_code'] = '1'; $_POST['va_code'] = '  '; }
register_shutdown_function(function () use ($fall) {
    $m = wp_einmalmeldung_lesen();
    echo $fall, ': Adresse offen=', wp_va_browser_lage() ? 'ja' : 'nein',
        ' | meldungen=', json_encode(isset($m['meldungen']) ? $m['meldungen'] : null, JSON_UNESCAPED_UNICODE),
        ' | fehler=', json_encode(isset($m['fehler']) ? $m['fehler'] : null, JSON_UNESCAPED_UNICODE),
        ' | header=', implode(';', headers_list()), "\n";
});
chdir($html);
ob_start();
include $html . '/index.php';
$rest = ob_get_clean();
echo $fall, ': ohne Umleitung beendet, ', strlen($rest), " Byte Ausgabe\n";
