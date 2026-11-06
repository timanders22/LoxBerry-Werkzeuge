<?php
/* Attrappe von loxberry_web.php. lbheader() setzt bewusst SDK-Globale -
 * genau das ist der Grund fuer die Praefix-Regel der Hausregeln, also bildet
 * die Attrappe es nach. */

if (!class_exists('LBSystem')) { require_once __DIR__ . '/loxberry_system.php'; }

class LBWeb
{
    public static function lbheader($pagetitle = '', $helpurl = '', $helptemplate = '', $nojqm = false)
    {
        // Die echte Funktion legt diese Globalen an. Wer im Plugin gleich
        // benannte Variablen benutzt, verliert sie hier.
        global $cfg, $lang, $template_title, $helplink, $L;
        $cfg = json_decode(json_encode(array(
            'BASE' => array('VERSION' => '4.0.0', 'LANG' => 'de'),
            'NETWORK' => array('FRIENDLYNAME' => 'LoxBerry Pruefstand'),
        )));
        $template_title = $pagetitle;
        $helplink = $helpurl;
        echo "<!-- lbheader: " . htmlspecialchars((string) $pagetitle) . " -->\n";
        return true;
    }
    public static function lbfooter() { echo "<!-- lbfooter -->\n"; return true; }
    public static function head($t = '') { echo "<!-- head -->\n"; }
    public static function pagestart($pagetitle = "", $helpurl = "", $helptemplate = "", $page = "main1") { echo "<!-- pagestart -->\n"; }
    public static function pageend() { echo "<!-- pageend -->\n"; }
    public static function foot() { echo "<!-- foot -->\n"; }
    public static function gethelp($file = '', $key = '') { return '<p>Hilfe-Attrappe</p>'; }
    /* ==================================================================
     * loglist_html() kann jetzt auch NICHTS liefern - gehaertet 29.08.2026
     * ==================================================================
     *
     * Bis dahin lieferte die Attrappe IMMER eine Zeichenkette. Damit war der
     * Fall, der auf dem Geraet der haeufigere ist, nicht pruefbar: die
     * Funktion listet die ueber LoxBerry::Log ANGEMELDETEN Protokolle. Ein
     * Plugin, dessen Dienst seine Datei selbst schreibt - etwa mit einem
     * RotatingFileHandler aus Python -, meldet nichts an, und LoxBerry
     * liefert voellig korrekt eine leere Liste.
     *
     * Aufgefallen an Midea2Lox 4.3.1: der Reiter "Logdateien" zeigte auf dem
     * Geraet ausser der Ueberschrift NICHTS, waehrend jeder Prueflauf ihn
     * gefuellt sah. Das Plugin hatte ein Entweder-oder gebaut - gibt es
     * loglist_html(), wird nur die benutzt - und die Attrappe hat den Fehler
     * zugedeckt.
     *
     * LB_ATTRAPPE_LOGLIST=leer stellt den Fall her. Ohne die Variable
     * aendert sich nichts; kein vorhandener Prueflauf wird anders.
     *
     * Wer diesen Lauf ansetzt und einen leeren Reiter findet, hat einen
     * echten Befund - keinen Fehler der Attrappe.
     * ================================================================== */
    public static function loglist_html($p = array())
    {
        if (getenv('LB_ATTRAPPE_LOGLIST') === 'leer') {
            return '';
        }
        return '<div class="loglist">Protokoll-Attrappe</div>';
    }
    public static function logfile_button_html($p = array()) { return '<a href="#">Protokoll</a>'; }
    public static function mslist_select_html($p = array()) { return '<select><option value="1">Miniserver</option></select>'; }
}

function lbheader($t = '', $h = '', $ht = '') { return LBWeb::lbheader($t, $h, $ht); }
function lbfooter() { return LBWeb::lbfooter(); }
function loglist_html($p = array()) { return LBWeb::loglist_html($p); }
