<?php
/* Attrappe von loxberry_log.php */

class LBLog
{
    public $filename;
    public function __construct($p = array())
    {
        $dir = getenv('LBPLOGDIR') ?: (getenv('LBHOMEDIR') . '/log/plugins/pruefling');
        if (!is_dir($dir)) { @mkdir($dir, 0777, true); }
        $this->filename = isset($p['filename']) ? $p['filename'] : ($dir . '/pruefling.log');
    }
    public static function newLog($p = array()) { return new LBLog($p); }
    public function LOGSTART($m = '') { $this->schreib('START', $m); }
    public function LOGEND($m = '')   { $this->schreib('END', $m); }
    /* Im Original heisst sie LOGTITLE, nicht LOGTIT. Die Attrappe trug bis
     * zum 25.08.2026 den falschen Namen.
     *
     * LOGTIT ist ERSATZLOS weg, und das ist Absicht: ein Plugin, das
     * LOGTIT() ruft, stuerzt auf dem echten LoxBerry ab. Ein Verweis hier
     * wuerde genau diesen Fehler verdecken - die Attrappe ist dazu da,
     * ihn zu zeigen. Sie darf nachsichtiger sein als das Original, wo es
     * um die UMGEBUNG geht (kein Netz, kein Miniserver), nie dort, wo es
     * um die SCHNITTSTELLE geht. */
    public function LOGTITLE($m = '') { $this->schreib('TITLE', $m); }
    public function LOGOK($m = '')    { $this->schreib('OK', $m); }
    public function LOGINF($m = '')   { $this->schreib('INFO', $m); }
    public function LOGWARN($m = '')  { $this->schreib('WARN', $m); }
    public function LOGERR($m = '')   { $this->schreib('ERROR', $m); }
    public function LOGCRIT($m = '')  { $this->schreib('CRIT', $m); }
    public function LOGALERT($m = '') { $this->schreib('ALERT', $m); }
    public function LOGDEB($m = '')   { $this->schreib('DEBUG', $m); }
    public function LOGFILE($m = '')  { $this->schreib('FILE', $m); }
    public function close() { return true; }
    private function schreib($stufe, $m)
    {
        @file_put_contents($this->filename, date('c') . " <$stufe> $m\n", FILE_APPEND);
    }
}

$_lb_log = null;
function _lb_log() { global $_lb_log; if (!$_lb_log) { $_lb_log = new LBLog(); } return $_lb_log; }
function LOGSTART($m = '') { _lb_log()->LOGSTART($m); }
function LOGEND($m = '')   { _lb_log()->LOGEND($m); }
function LOGTITLE($m = '') { _lb_log()->LOGTITLE($m); }
function LOGOK($m = '')    { _lb_log()->LOGOK($m); }
function LOGINF($m = '')   { _lb_log()->LOGINF($m); }
function LOGWARN($m = '')  { _lb_log()->LOGWARN($m); }
function LOGERR($m = '')   { _lb_log()->LOGERR($m); }
function LOGCRIT($m = '')  { _lb_log()->LOGCRIT($m); }
function LOGALERT($m = '') { _lb_log()->LOGALERT($m); }
function LOGDEB($m = '')   { _lb_log()->LOGDEB($m); }

/* ------------------------------------------------------------------
 * Benachrichtigungen
 *
 * Beide fehlten in der Attrappe, obwohl sie von zahlreichen Plugins
 * gerufen werden - eine Oberflaeche, die notify_ext() aufruft, starb hier
 * mit "Call to undefined function". Gefunden am 25.08.2026 durch
 * attrappe_pruefen.py.
 *
 * Sie SENDEN nichts: der Pruefstand hat kein Benachrichtigungssystem. Sie
 * schreiben in eine Datei, damit eine Pruefung nachsehen kann, OB und
 * WOMIT gemeldet wurde - das ist der Teil, auf den es ankommt.
 * ------------------------------------------------------------------ */

function lbwebserverport() { return 80; }

function _lb_notify_datei()
{
    $dir = getenv('LBPLOGDIR') ?: (getenv('LBHOMEDIR') . '/log');
    if (!is_dir($dir)) { @mkdir($dir, 0777, true); }
    return $dir . '/notifications.jsonl';
}

/* Original: notify($package, $name, $message, $error = false) */
function notify($package, $name, $message, $error = false)
{
    return notify_ext(array(
        'PACKAGE' => $package, 'NAME' => $name, 'MESSAGE' => $message,
        'SEVERITY' => $error ? 3 : 6,
    ));
}

/* Original: notify_ext($fields) - verlangt PACKAGE, NAME und MESSAGE und
 * bricht sonst ab, ohne zu melden. Genau das bildet die Attrappe nach:
 * eine Pruefung soll den Fall finden, in dem ein Feld fehlt. */
function notify_ext($fields)
{
    if (!is_array($fields) || !isset($fields['PACKAGE'])
        || !isset($fields['NAME']) || !isset($fields['MESSAGE'])) {
        error_log("Notification: Missing parameters\n");
        return;
    }
    if (!isset($fields['SEVERITY'])) { $fields['SEVERITY'] = 6; }
    $fields['_ts'] = date('c');
    @file_put_contents(_lb_notify_datei(),
        json_encode($fields, JSON_UNESCAPED_UNICODE) . "\n", FILE_APPEND);
    return true;
}
