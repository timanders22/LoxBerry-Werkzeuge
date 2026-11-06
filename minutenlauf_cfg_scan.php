<?php
/**
 * minutenlauf_cfg_scan.php <Linienordner>: gibt je Treffer "datei:zeile" aus, wo $cfg im globalen Bereich einer PHP-Datei steht.
 * Das LoxBerry-SDK (loxberry_system.php) macht beim ersten Lesen von general.json "global $cfg; $cfg = json_decode(..., FALSE)" und beim Laden
 * im globalen Bereich $cfg=NULL. Tokenizer: Kommentare und Funktionsrumpfe zaehlen nicht. Der eingebaute Stamm sprachausgabe.php zaehlt nicht.
 * Eichung: siehe minutenlauf_eichung.py. Laeuft auf: php -n (8.4, Tokenizer eingebaut).
 */
$b = rtrim($argv[1], '/\\');
$it = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($b, FilesystemIterator::SKIP_DOTS));
$raus = array('png','svg','jpg','gif','zip','py','js','css','ini','json','md','txt','html','cfg','xml','pl','pm','sh','gz','ico','woff','woff2','ttf');
foreach ($it as $f) {
    $s = str_replace('\\', '/', (string) $f);
    if (preg_match('~/(icons|dpkg|venv|node_modules|__pycache__|\.git)/~', $s) || !is_file($s) || filesize($s) > 3000000) { continue; }
    if (in_array(strtolower(pathinfo($s, PATHINFO_EXTENSION)), $raus, true) || basename($s) === 'sprachausgabe.php') { continue; }
    $k = (string) file_get_contents($s);
    if (strpos($k, '<?php') === false || strpos($k, '$cfg') === false) { continue; }
    $t = @token_get_all($k);
    $tiefe = 0; $fn = array(); $wartet = false; $z = array();
    $c = count($t);
    for ($i = 0; $i < $c; $i++) {
        $x = $t[$i];
        if (is_array($x)) {
            if ($x[0] === T_CURLY_OPEN || $x[0] === T_DOLLAR_OPEN_CURLY_BRACES) { $tiefe++; }
            if ($x[0] === T_FUNCTION || $x[0] === T_CLASS || $x[0] === T_TRAIT || $x[0] === T_INTERFACE) {
                $j = $i - 1; while ($j >= 0 && is_array($t[$j]) && $t[$j][0] === T_WHITESPACE) { $j--; }
                if (!($j >= 0 && is_array($t[$j]) && $t[$j][0] === T_DOUBLE_COLON)) { $wartet = true; }
            }
            if (!$fn && !$wartet && $x[0] === T_VARIABLE && $x[1] === '$cfg') { $z[] = $x[2]; }
        } elseif ($x === '{') {
            $tiefe++; if ($wartet) { $fn[] = $tiefe; $wartet = false; }
        } elseif ($x === '}') {
            if ($fn && end($fn) === $tiefe) { array_pop($fn); }
            $tiefe--;
        } elseif ($x === ';') {
            $wartet = false;
        }
    }
    if ($z) { echo substr($s, strlen(str_replace('\\', '/', $b)) + 1), ':', implode(',', array_slice($z, 0, 5)), count($z) > 5 ? ' ...' : '', "\n"; }
}
