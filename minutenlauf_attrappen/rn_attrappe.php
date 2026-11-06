<?php
/* Laeuft auf: WSL (PHP 8.3), eingebunden mit -d auto_prepend_file. Gruppe 40 (Renault NG 2.1.20): Renault-Attrappe.
 * Definiert rn_http_senden() VOR dem Laden der Bibliothek (Bauvorschrift 1.0) und antwortet aus Tabellen - KEIN
 * Netzaufruf an Renault, Gigya, OpenWeatherMap oder ABRP. Ordner aus RN_ATT (Umgebung):
 *   <RN_ATT>/aufrufe.log    eine Zeile je Aufruf: "<Zeit> <METHODE> <Kurzname>"
 *   <RN_ATT>/ctl.json       Steuerung je Kurzname: {"battery-status": {"code": 403}, "actions": {"code": 500},
 *                           "accounts.login": {"code": 200, "body": {...}}, "*": {"delay": 20}, ...}
 *   <RN_ATT>/stand.json     Fahrzeugstand {"soc":80,"plug":1,"charging":0,"ts":"2026-10-27T17:02:00Z","kwh":20.5,
 *                           "lat":"48.0005","lon":"11.0","gps_ts":"...","hvac":"off","ext":8,"person":"P1","konto":"KONTO_A"}
 * Kurznamen: accounts.login, accounts.getJWT, persons, battery-status, cockpit, charge-mode, location, details,
 * hvac-status, soc-levels, vehicles, charges, actions (hvac-start, charging-start, charge-mode, pause-resume), abrp, wetter.
 * Zeitschranke: "delay" wartet; ist sie groesser als die Zeitschranke des Aufrufs (gesamt), endet der Aufruf nach der
 * Schranke mit Code 0 wie curl (Zeitueberschreitung). */
if (!function_exists('rn_http_senden')) {
    function rn_att_dir() { $d = (string) getenv('RN_ATT'); return $d !== '' ? $d : '/tmp/rn_att'; }
    function rn_att_json($f) { $d = @json_decode((string) @file_get_contents(rn_att_dir() . '/' . $f), true); return is_array($d) ? $d : array(); }
    function rn_att_kurz($url) {
        $p = (string) parse_url($url, PHP_URL_PATH);
        $h = (string) parse_url($url, PHP_URL_HOST);
        if (strpos($h, 'gigya') !== false) { return basename($p); }
        if (strpos($h, 'iternio') !== false) { return 'abrp'; }
        if (strpos($h, 'openweathermap') !== false) { return 'wetter'; }
        if (preg_match('#/persons/#', $p)) { return 'persons'; }
        if (preg_match('#/actions/([a-z-]+)$#', $p, $m)) { return 'actions:' . $m[1]; }
        if (preg_match('#/charge/pause-resume$#', $p)) { return 'actions:pause-resume'; }
        if (preg_match('#/ev/soc-levels$#', $p)) { return 'soc-levels'; }
        if (preg_match('#/vehicles/[^/]+/details$#', $p)) { return 'details'; }
        if (preg_match('#/vehicles$#', $p)) { return 'vehicles'; }
        if (preg_match('#/charges$#', $p)) { return 'charges'; }
        return basename($p);
    }
    function rn_http_senden($methode, $url, array $kopf, $rumpf, $zeit)
    {
        $kurz = rn_att_kurz($url);
        $art = (strpos($kurz, 'actions:') === 0) ? 'actions' : $kurz;
        $ctl = rn_att_json('ctl.json');
        $st = rn_att_json('stand.json') + array('soc' => 80, 'plug' => 1, 'charging' => 0, 'ts' => gmdate('Y-m-d\TH:i:s\Z', time() - 120),
            'kwh' => 20.5, 'range' => 250, 'km' => 12345, 'lat' => '48.0005', 'lon' => '11.0000',
            'gps_ts' => gmdate('Y-m-d\TH:i:s\Z', time() - 600), 'hvac' => 'off', 'ext' => 8, 'int' => 19, 'person' => 'P1',
            'konto' => 'KONTO_A', 'jwt' => 'JWT_A_0', 'mode' => 'always_charging', 'zeit_s' => 0);
        $c = isset($ctl[$kurz]) ? $ctl[$kurz] : (isset($ctl[$art]) ? $ctl[$art] : array());
        $alle = isset($ctl['*']) ? $ctl['*'] : array();
        $mit = '';
        if (is_array($rumpf)) { $mit = isset($rumpf['loginId']) ? ' login=' . $rumpf['loginId'] : ''; }
        elseif (is_string($rumpf) && $rumpf !== '' && preg_match('/"action":"([a-z_]+)"/', $rumpf, $mm)) { $mit = ' ' . $mm[1]; }
        $proz = getenv('RN_ATT_WER') ? ' [' . getenv('RN_ATT_WER') . ']' : '';
        file_put_contents(rn_att_dir() . '/aufrufe.log', date('H:i:s') . ' ' . strtoupper($methode) . ' ' . $kurz . $mit . $proz . "\n", FILE_APPEND | LOCK_EX);
        $delay = isset($c['delay']) ? (float) $c['delay'] : (isset($alle['delay']) ? (float) $alle['delay'] : 0.0);
        $gesamt = is_array($zeit) ? (float) $zeit[1] : (float) $zeit;
        if ($delay > 0) {
            if ($delay > $gesamt) { usleep((int) ($gesamt * 1000000)); return array(0, false, 'Operation timed out after ' . (int) $gesamt . ' seconds', $gesamt); }
            usleep((int) ($delay * 1000000));
        }
        $code = isset($c['code']) ? (int) $c['code'] : 200;
        if (isset($c['body'])) { return array($code, is_string($c['body']) ? $c['body'] : json_encode($c['body']), '', $delay); }
        if ($code >= 400) { return array($code, '{"errors":[{"errorCode":"err.func.' . $code . '","errorMessage":"Attrappe"}]}', '', $delay); }
        switch ($art) {
            case 'accounts.login':
                return array(200, json_encode(array('errorCode' => 0, 'sessionInfo' => array('cookieValue' => 'COOKIE_ATT'),
                    'data' => array('personId' => $st['person']))), '', 0);
            case 'accounts.getJWT':
                return array(200, json_encode(array('errorCode' => 0, 'id_token' => $st['jwt'])), '', 0);
            case 'persons':
                return array(200, json_encode(array('accounts' => array(array('accountId' => $st['konto'], 'accountType' => 'MYRENAULT',
                    'accountStatus' => 'ACTIVE')))), '', 0);
            case 'battery-status':
                $a = array('timestamp' => $st['ts'], 'batteryLevel' => $st['soc'], 'batteryAutonomy' => $st['range'],
                           'plugStatus' => $st['plug'], 'chargingStatus' => $st['charging']);
                if ($st['kwh'] !== null) { $a['batteryAvailableEnergy'] = $st['kwh']; }
                if ((float) $st['charging'] == 1) { $a['chargingRemainingTime'] = 45; $a['chargingInstantaneousPower'] = 7.4; }
                return array(200, json_encode(array('data' => array('type' => 'Car', 'attributes' => $a))), '', 0);
            case 'cockpit':
                return array(200, json_encode(array('data' => array('attributes' => array('totalMileage' => $st['km'])))), '', 0);
            case 'charge-mode':
                return array(200, json_encode(array('data' => array('attributes' => array('chargeMode' => $st['mode'])))), '', 0);
            case 'location':
                return array(200, json_encode(array('data' => array('attributes' => array('gpsLatitude' => $st['lat'],
                    'gpsLongitude' => $st['lon'], 'lastUpdateTime' => $st['gps_ts'])))), '', 0);
            case 'hvac-status':
                return array(200, json_encode(array('data' => array('attributes' => array('hvacStatus' => $st['hvac'],
                    'externalTemperature' => $st['ext'], 'internalTemperature' => $st['int'])))), '', 0);
            case 'details':
                return array(200, json_encode(array('data' => array('attributes' => array('modelCode' => 'X10')))), '', 0);
            case 'charges':
                return array(200, json_encode(array('data' => array('attributes' => array('charges' => array())))), '', 0);
            case 'actions':
                return array(200, '{"data":{"type":"Action","id":"att"}}', '', 0);
            case 'abrp':
                return array(200, '{"status":"ok"}', '', 0);
            case 'wetter':
                return array(200, '{"current":{"temp":7,"weather":[{"description":"klar"}]}}', '', 0);
        }
        return array(404, '{"errors":[{"errorCode":"notFound"}]}', '', 0);
    }
}
