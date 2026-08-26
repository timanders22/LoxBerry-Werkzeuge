<?php
/**
 * anhaengen.php - Text an eine Datei haengen, ohne ihre Zeilenenden zu
 * verderben.
 *
 * Der Anlass: viermal in Folge sind in diesem Projekt beim Nachtragen
 * CRLF in reine LF-Dateien gerutscht oder umgekehrt. Jedes Mal fiel es
 * erst hinterher auf, und jedes Mal war die Berichtigung teurer als die
 * Messung gewesen waere. Die Regel dagegen steht laengst in den REGELN -
 * gefehlt hat das Werkzeug, das sie einhaelt, ohne dass jemand daran
 * denken muss.
 *
 * Was es tut:
 *   1. Es MISST die Zeilenenden der Zieldatei, bevor es sie oeffnet.
 *   2. Es setzt den neuen Text auf genau diesen Stil um.
 *   3. Es zaehlt hinterher nach und sagt beides an.
 *
 * Was es NICHT tut: raten. Eine Datei mit gemischten Zeilenenden wird
 * abgewiesen, nicht "vereinheitlicht" - das waere eine Aenderung an
 * Zeilen, die niemand angefasst hat, versteckt in einem Nachtrag.
 * Ebenso wird eine Datei mit einzelnen CR (alter Mac-Stil oder Binaeres)
 * abgewiesen.
 *
 * Aufruf:
 *   php anhaengen.php ZIEL --von TEXT.md
 *   php anhaengen.php ZIEL < text.md
 *   cat text.md | php anhaengen.php ZIEL
 *   php anhaengen.php ZIEL --von TEXT.md --probe     (nur messen, nichts schreiben)
 *   php anhaengen.php ZIEL --von TEXT.md --stil=lf   (nur fuer NEUE Dateien)
 *
 * Rueckgabewert: 0 wenn angehaengt oder geprobt, 1 bei jedem Abbruch.
 * Damit laesst es sich in eine Kette haengen, ohne dass ein Fehlschlag
 * unbemerkt durchrutscht.
 *
 * Kompatibel mit PHP 7.4 und PHP 8.x.
 */

function ah_stil($roh)
{
    $crlf = substr_count($roh, "\r\n");
    $lf = substr_count($roh, "\n") - $crlf;
    $cr = substr_count($roh, "\r") - $crlf;
    if ($cr > 0) { return array('einzelne_cr', $crlf, $lf, $cr); }
    if ($crlf > 0 && $lf > 0) { return array('gemischt', $crlf, $lf, $cr); }
    if ($crlf > 0) { return array('crlf', $crlf, $lf, $cr); }
    if ($lf > 0) { return array('lf', $crlf, $lf, $cr); }
    return array('ohne', $crlf, $lf, $cr);
}

/** Auf einen Stil umsetzen - erst alles auf LF, dann gezielt zurueck. */
function ah_umsetzen($text, $stil)
{
    $lf = str_replace(array("\r\n", "\r"), "\n", $text);
    return ($stil === 'crlf') ? str_replace("\n", "\r\n", $lf) : $lf;
}

function ah_fehler($satz)
{
    fwrite(STDERR, "anhaengen: " . $satz . "\n");
    exit(1);
}

/* ---- Aufruf zerlegen ---- */
$ziel = '';
$von = '';
$probe = false;
$stil_wunsch = '';
foreach (array_slice($argv, 1) as $arg) {
    if ($arg === '--probe') { $probe = true; }
    elseif (strpos($arg, '--von=') === 0) { $von = substr($arg, 6); }
    elseif ($arg === '--von') { $von = '@naechstes'; }
    elseif (strpos($arg, '--stil=') === 0) { $stil_wunsch = strtolower(substr($arg, 7)); }
    elseif ($von === '@naechstes') { $von = $arg; }
    elseif ($ziel === '') { $ziel = $arg; }
    else { ah_fehler('zu viele Angaben: ' . $arg); }
}
if ($von === '@naechstes') { ah_fehler('--von ohne Dateinamen'); }
if ($ziel === '') {
    fwrite(STDERR, "Aufruf: php anhaengen.php ZIEL [--von TEXT] [--probe] [--stil=lf|crlf]\n");
    exit(1);
}
if ($stil_wunsch !== '' && !in_array($stil_wunsch, array('lf', 'crlf'), true)) {
    ah_fehler('--stil kennt nur lf und crlf');
}

/* ---- Den anzuhaengenden Text holen ---- */
if ($von !== '') {
    if (!is_file($von)) { ah_fehler('Textdatei nicht gefunden: ' . $von); }
    $neu = file_get_contents($von);
    if ($neu === false) { ah_fehler('Textdatei nicht lesbar: ' . $von); }
} else {
    $neu = stream_get_contents(STDIN);
    if ($neu === false) { $neu = ''; }
}
if ($neu === '') { ah_fehler('es gibt nichts anzuhaengen'); }

/* ---- MESSEN, bevor irgendetwas geschrieben wird ---- */
$neu_da = is_file($ziel);
if ($neu_da) {
    $alt = file_get_contents($ziel);
    if ($alt === false) { ah_fehler('Zieldatei nicht lesbar: ' . $ziel); }
    list($stil, $crlf, $lf, $cr) = ah_stil($alt);
    printf("Ziel      %s\n", $ziel);
    printf("  vorher  %-12s CRLF %-6d reine LF %-6d einzelne CR %-4d %d Byte\n",
           $stil, $crlf, $lf, $cr, strlen($alt));
    if ($stil === 'einzelne_cr') {
        ah_fehler('die Datei enthaelt einzelne CR. Das ist alter Mac-Stil oder '
                . 'gar kein Text - hier wird nichts angehaengt.');
    }
    if ($stil === 'gemischt') {
        ah_fehler('die Datei hat GEMISCHTE Zeilenenden (' . $crlf . ' CRLF, ' . $lf
                . ' LF). Ein Nachtrag wuerde die Mischung fortschreiben, und ein '
                . 'stilles Vereinheitlichen waere eine Aenderung an Zeilen, die '
                . 'niemand angefasst hat. Bitte erst von Hand entscheiden.');
    }
    if ($stil === 'ohne') {
        /* Eine einzige Zeile ohne Abschluss. Woran soll man sich halten? */
        if ($stil_wunsch === '') {
            ah_fehler('die Datei hat ueberhaupt kein Zeilenende - der Stil laesst '
                    . 'sich nicht messen. Mit --stil=lf oder --stil=crlf bestimmen.');
        }
        $stil = $stil_wunsch;
        printf("  Stil    aus --stil uebernommen: %s\n", strtoupper($stil));
    } elseif ($stil_wunsch !== '' && $stil_wunsch !== $stil) {
        ah_fehler('die Datei ist ' . strtoupper($stil) . ', --stil verlangt '
                . strtoupper($stil_wunsch) . '. Das Werkzeug setzt sich nicht ueber '
                . 'die Messung hinweg; --stil gilt nur fuer neue Dateien.');
    }
} else {
    $alt = '';
    $stil = ($stil_wunsch !== '') ? $stil_wunsch : 'lf';
    printf("Ziel      %s\n", $ziel);
    printf("  vorher  NEUE DATEI, Stil %s%s\n", strtoupper($stil),
           $stil_wunsch === '' ? ' (Vorgabe, mit --stil aenderbar)' : '');
}

/* ---- Den neuen Text auf den gemessenen Stil bringen ---- */
$fertig = ah_umsetzen($neu, $stil);
$zeilenende = ($stil === 'crlf') ? "\r\n" : "\n";
/* Die vorhandene Datei soll auf einem Zeilenende enden, sonst klebte der
 * Nachtrag an die letzte Zeile an. Angefasst wird dafuer nichts Altes -
 * es kommt nur ein Abschluss davor. */
$fuge = '';
if ($alt !== '' && substr($alt, -strlen($zeilenende)) !== $zeilenende) {
    $fuge = $zeilenende;
    printf("  Fuge    die Datei endete ohne Zeilenende - eines wird vorangestellt\n");
}
if (substr($fertig, -strlen($zeilenende)) !== $zeilenende) {
    $fertig .= $zeilenende;
}

list($nstil, $ncrlf, $nlf, $ncr) = ah_stil($fertig);
printf("  Nachtrag %-12s CRLF %-6d reine LF %-6d %d Byte\n", $nstil, $ncrlf, $nlf, strlen($fertig));
if ($ncr > 0) { ah_fehler('im Nachtrag stecken einzelne CR - das wird nicht geschrieben.'); }

if ($probe) {
    printf("  --probe: es wurde NICHTS geschrieben.\n");
    exit(0);
}

/* ---- Schreiben ---- */
$fp = @fopen($ziel, 'ab');
if (!$fp) { ah_fehler('Zieldatei nicht zum Anhaengen zu oeffnen: ' . $ziel); }
if (!flock($fp, LOCK_EX)) { fclose($fp); ah_fehler('Datei laesst sich nicht sperren'); }
$geschrieben = fwrite($fp, $fuge . $fertig);
fflush($fp);
flock($fp, LOCK_UN);
fclose($fp);
if ($geschrieben === false || $geschrieben !== strlen($fuge . $fertig)) {
    ah_fehler('unvollstaendig geschrieben - die Datei bitte pruefen.');
}

/* ---- NACHZAEHLEN. Ein Werkzeug, das seine eigene Behauptung nicht
 *      pruefen kann, ist so gut wie keines. ---- */
clearstatcache(true, $ziel);
$hinterher = file_get_contents($ziel);
list($hstil, $hcrlf, $hlf, $hcr) = ah_stil($hinterher);
printf("  nachher %-12s CRLF %-6d reine LF %-6d einzelne CR %-4d %d Byte\n",
       $hstil, $hcrlf, $hlf, $hcr, strlen($hinterher));
if ($hstil !== $stil || $hcr > 0) {
    ah_fehler('der Stil hat sich beim Schreiben veraendert (' . $stil . ' -> '
            . $hstil . '). Die Datei bitte ansehen.');
}
printf("  in Ordnung: %s gehalten, %d Byte angehaengt.\n",
       strtoupper($stil), strlen($fuge . $fertig));
exit(0);
