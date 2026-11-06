<?php
/* Treiber fuer Werkzeuge/sprachausgabe_probe.py. Laeuft auf: Windows, php.exe (7.4/8.4/8.5), mit
 * oder ohne curl. Nicht selbst aufrufen.
 *
 *   php sprachausgabe_probe_treiber.php <pfad zu sprachausgabe.php> < faelle.json
 *
 * Liest eine Liste von Faellen (JSON) von der Standardeingabe und gibt je Fall eine Zeile
 * JSON aus: Name, Ergebnis der Modulfunktion, Dauer in ms. Am Ende eine Zeile mit dem
 * benutzten Transportweg. Gibt NIE Text oder Token aus - das prueft der Aufrufer zusaetzlich.
 */
error_reporting(-1);
ini_set('display_errors', 'stderr');
require $argv[1];

$faelle = json_decode((string) stream_get_contents(STDIN), true);
if (!is_array($faelle)) { fwrite(STDERR, "keine Faelle\n"); exit(2); }

foreach ($faelle as $f) {
    $k = array('port' => (int) $f['port'], 'kopf' => array('User-Agent: Sprachmodul-Probe ' . (isset($f['ua']) ? $f['ua'] : '-')),
               'ordner' => isset($f['ordner']) ? (string) $f['ordner'] : '');
    if (isset($f['texte']) && is_array($f['texte'])) {
        $tx = $f['texte'];
        $k['t'] = function ($s) use ($tx) {
            $id = substr($s, strlen('ANSAGE.'));
            return (strpos($s, 'ANSAGE.') === 0 && isset($tx[$id])) ? $tx[$id] : $s;
        };
    }
    $tts = $f['tts'] + ansage_vorgaben();
    $t0 = microtime(true);
    switch ($f['fn']) {
        case 'sprechen':
            $r = ansage_sprechen($f['text'], $tts, $k);
            $r['kurz'] = ansage_kurz($r);
            if (isset($k['t'])) { $r['satz'] = ansage_kennung_text($r['kennung'], $k); }
            break;
        case 'selbsttest':
            $r = ansage_ng_selbsttest($tts, $tts['mode'], $k);
            break;
        case 'pruefzeile':
            $r = ansage_pruefzeile($tts, true, $k);
            break;
        case 'cli':
            $r = ansage_cli(json_encode(array('text' => $f['text'])), $tts, $k);
            break;
        case 'rufen':
            $url = ansage_adresse($tts['mode'], $k['port']);
            $r = ansage_ng_rufen($url, array('aktion' => 'sprechen', 'token' => $tts['google_token'], 'geraet' => $tts['google_geraet'], 'text' => $f['text']),
                                 (int) $f['tmo'], $k);
            unset($r['roh']);
            break;
        case 'schluessel':
            $r = ansage_sprachschluessel();
            break;
        default:
            $r = 'unbekannte Funktion';
    }
    $ms = (int) round((microtime(true) - $t0) * 1000);
    echo json_encode(array('name' => $f['name'], 'r' => $r, 'ms' => $ms), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES), "\n";
}
echo json_encode(array('name' => '_weg', 'r' => function_exists('curl_init') ? 'curl' : 'datenstrom',
                       'php' => PHP_VERSION)), "\n";
