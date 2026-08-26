<?php
/* Attrappe von loxberry_io.php - MQTT-Gateway-Zugangsdaten. */

function mqtt_connectiondetails()
{
    return array(
        'brokerhost' => '127.0.0.1',
        'brokerport' => 1883,
        'brokeruser' => 'loxberry',
        'brokerpass' => 'geheim',
        'udpinport'  => 11883,
    );
}

if (!function_exists('get_miniservers')) {
    function get_miniservers() { if (class_exists('LBSystem')) { return LBSystem::get_miniservers(); } return array(); }
}
function get_miniserver_by_ip($ip) { return null; }
/* Die Argumentlisten sind die des Originals (4.0.0.15). Bis zum
 * 25.08.2026 verlangte die Attrappe bei mshttp_send drei Argumente, das
 * Original nur zwei - ein Aufruf mit zwei waere hier abgestuerzt und auf
 * dem echten LoxBerry durchgelaufen. Eine Attrappe, die STRENGER ist als
 * das Original, meldet Fehler, die es nicht gibt; eine, die lockerer ist,
 * verschweigt welche. */
function mshttp_send($msnr, $inputs, $value = null) { return true; }
function mshttp_send_mem($msnr, $params, $value = null) { return true; }
function mqtt_get($topic) { return null; }
function mqtt_set($topic, $content, $retain = false) { return true; }
