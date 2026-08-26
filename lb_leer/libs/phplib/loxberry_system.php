<?php
/* Attrappe des LoxBerry-PHP-SDK, nur so weit, wie die Plugins es benutzen. */

$lbhomedir   = getenv('LBHOMEDIR');
$lbsdir      = $lbhomedir;
$lbpplugindir = getenv('LBPPLUGINDIR') ?: 'pruefling';
$lbpconfigdir = $lbhomedir . '/config/plugins/' . $lbpplugindir;
$lbplogdir    = $lbhomedir . '/log/plugins/' . $lbpplugindir;
$lbpdatadir   = $lbhomedir . '/data/plugins/' . $lbpplugindir;
$lbpbindir    = getenv('LBPBINDIR') ?: ($lbhomedir . '/bin/plugins/' . $lbpplugindir);
$lbphtmlauthdir = getenv('LBPHTMLAUTHDIR') ?: '';
$lbphtmldir     = getenv('LBPHTMLDIR') ?: '';
$lbptemplatedir = getenv('LBPTEMPLATEDIR') ?: '';

if (!defined('LBHOMEDIR'))      define('LBHOMEDIR', $lbhomedir);
if (!defined('LBPCONFIGDIR'))   define('LBPCONFIGDIR', $lbpconfigdir);
if (!defined('LBPLOGDIR'))      define('LBPLOGDIR', $lbplogdir);
if (!defined('LBPDATADIR'))     define('LBPDATADIR', $lbpdatadir);
if (!defined('LBPPLUGINDIR'))   define('LBPPLUGINDIR', $lbpplugindir);
if (!defined('LBPBINDIR'))      define('LBPBINDIR', $lbpbindir);
if (!defined('LBPHTMLAUTHDIR')) define('LBPHTMLAUTHDIR', $lbphtmlauthdir);
if (!defined('LBPHTMLDIR'))     define('LBPHTMLDIR', $lbphtmldir);
if (!defined('LBPTEMPLATEDIR')) define('LBPTEMPLATEDIR', $lbptemplatedir);
if (!defined('LBLANG'))         define('LBLANG', 'de');

foreach (array($lbpconfigdir, $lbplogdir, $lbpdatadir) as $d) {
    if (!is_dir($d)) { @mkdir($d, 0777, true); }
}

class LBSystem
{
    public static function lblanguage() { return 'de'; }
    public static function get_localip() { return '192.168.1.50'; }
    public static function lbhostname() { return 'loxberry'; }
    public static function lbfriendlyname() { return 'LoxBerry Pruefstand'; }
    public static function lbversion() { return '4.0.0.15'; }   /* Stand 25.08.2026, gemessen an den Releases */
    public static function pluginversion($queryname = "") { return '9.9.9'; }
    public static function pluginloglevel($queryname = "") { return 7; }
    public static function plugindata($x = null)
    {
        return array('PLUGINDB_TITLE' => 'Pruefling', 'PLUGINDB_VERSION' => '9.9.9',
                     'PLUGINDB_FOLDER' => getenv('LBPPLUGINDIR') ?: 'pruefling',
                     'PLUGINDB_LOGLEVEL' => 7);
    }
    public static function get_miniservers()
    {
        return array(1 => array(
            'Name' => 'Miniserver', 'IPAddress' => '192.168.1.10', 'Port' => 80,
            'Admin' => 'admin', 'Pass' => 'geheim123',
            'Admin_RAW' => 'admin', 'Pass_RAW' => 'geheim123',
            'Credentials' => 'admin:geheim123', 'Credentials_RAW' => 'admin:geheim123',
            'PreferHttps' => 0, 'PortHttps' => 443, 'UseCloudDNS' => 0,
        ));
    }
    public static function get_miniserver_by_name($n) { $m = self::get_miniservers(); return $m[1]; }
    public static function readlanguage($tmpl = null, $file = null, $return = false)
    {
        // Liest die Sprachdatei des Pruefling-Plugins wie das Original.
        $dir = getenv('LBPTEMPLATEDIR');
        $lang = 'de';
        $cand = array();
        if ($file) { $cand[] = $dir . '/lang/' . str_replace('_de.ini', '_' . $lang . '.ini', $file); }
        $cand[] = $dir . '/lang/language_' . $lang . '.ini';
        foreach ($cand as $p) {
            if (is_file($p)) {
                $ini = parse_ini_file($p, true, INI_SCANNER_RAW);
                if ($ini === false) { return array(); }
                $flach = array();
                foreach ($ini as $sec => $paare) {
                    if (is_array($paare)) { foreach ($paare as $k => $v) { $flach[$sec . '.' . $k] = $v; } }
                    else { $flach[$sec] = $paare; }
                }
                return $flach;
            }
        }
        return array();
    }
    public static function is_enabled($v) { $v = strtolower(trim((string) $v)); return in_array($v, array('true','yes','on','1','enabled','check','checked','select','selected'), true); }
    public static function is_disabled($v) { return !self::is_enabled($v); }
    public static function reboot_required($t = null) { return false; }
    public static function systemloglevel() { return 7; }
    public static function get_ftpport($msnr = 1) { return 21; }
    /* lbsystemversion() stand hier bis zum 25.08.2026 und gibt es im
     * Original NICHT - sie war erfunden. Ersatzlos entfernt: ein Plugin,
     * das sie ruft, soll hier abstuerzen, weil es auf dem echten LoxBerry
     * genauso abstuerzt. Die richtige Funktion heisst lbversion(). */
}

foreach (array('lblanguage', 'readlanguage', 'is_enabled', 'is_disabled',
               'get_localip', 'get_miniservers') as $_f) {
    if (function_exists($_f)) { continue; }
    switch ($_f) {
        case 'lblanguage':      eval('function lblanguage() { return LBSystem::lblanguage(); }'); break;
        case 'readlanguage':    eval('function readlanguage($t = null, $f = null, $r = false) { return LBSystem::readlanguage($t, $f, $r); }'); break;
        case 'is_enabled':      eval('function is_enabled($v) { return LBSystem::is_enabled($v); }'); break;
        case 'is_disabled':     eval('function is_disabled($v) { return LBSystem::is_disabled($v); }'); break;
        case 'get_localip':     eval('function get_localip() { return LBSystem::get_localip(); }'); break;
        case 'get_miniservers': eval('function get_miniservers() { return LBSystem::get_miniservers(); }'); break;
    }
}
if (!function_exists('trim_all')) { function trim_all($v) { return trim((string) $v); } }

/* ==========================================================================
 * ABSICHTLICHER FLURSCHADEN - bitte nicht "aufraeumen"
 *
 * Die echte loxberry_system.php hinterlaesst im einbindenden
 * Gueltigkeitsbereich globale Variablen. require_once bindet im GLEICHEN
 * Bereich ein: was hier steht, ersetzt das, was der Aufrufer unter demselben
 * Namen hatte.
 *
 * Bis zum 17.08.2026 tat diese Attrappe das NICHT - und hat deshalb einen
 * Fehler durchgelassen, an dem die Oberflaeche eines Plugins auf dem Geraet
 * mit HTTP 500 endete, waehrend rendern.py in allen sechs Reitern und unter
 * beiden PHP-Fassungen gruen war. Eine Attrappe wird gegen das Geraet gebaut,
 * sonst prueft man die Attrappe.
 *
 * $p ist AM GERAET GEMESSEN (LoxBerry 4.0.0.14, 17.08.2026):
 *
 *     php -r '$p = array("home"=>"/opt/loxberry");
 *             require_once "/opt/loxberry/libs/phplib/loxberry_system.php";
 *             var_dump($p);'
 *     nachher: array(4) { [0]=> ""  [1]=> "libs"
 *                         [2]=> "phplib"  [3]=> "loxberry_system.php" }
 *
 * Die uebrigen Namen stammen aus dem Abschnitt "Variables to store" des
 * Originals (Zweig master, abgerufen 17.08.2026) - belegt, aber nicht am
 * Geraet nachgemessen. Sie stehen hier, weil ein Plugin, das eine davon im
 * Hauptteil benutzt, denselben Fehler hat wie das mit $p.
 *
 * WAS EIN PLUGIN DARAUS ZU LERNEN HAT: jede Variable im Hauptteil traegt das
 * Plugin-Kuerzel ($xx_p, $xx_cfg), und Werte, die nach dem Einbinden noch
 * gebraucht werden, werden VORHER in eine eigene Variable gerettet.
 * ========================================================================== */

$p = explode('/', '/libs/phplib/loxberry_system.php');

$cfg = null;
$binaries = null;
$pluginversion = null;
$lbfriendlyname = null;
$lbsysversion = null;
$miniservercount = null;
$plugins = null;
$lblang = null;
$lbcountry = null;
$cfgwasread = null;
$plugindb_timestamp = 0;
$plugindb_lastchecked = 0;
$plugindb_timestamp_last = 0;
