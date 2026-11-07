<?php
/**
 * Der Einrichtungs-Assistent gegen einen nachgebauten Miniserver.
 *
 * Gemessen wird die WIRKUNG der AUSGELIEFERTEN Funktionen - der Pruefstand
 * baut die Auswertung nicht nach. (Die erste Fassung tat das und mass
 * dadurch ihre eigene Kopie; der Fehler in rk_ms_probe() blieb unsichtbar.)
 * Zu jedem Fall gehoert der Gegenfall.
 */
require_once getenv('RK_LIB');

$MS  = array('nr' => '1', 'name' => 'Attrappe', 'adresse' => '127.0.0.1',
             'port' => (int) getenv('MS_PORT'), 'user' => 'admin', 'pass' => 'geheim123');
$MSA = $MS; $MSA['port'] = (int) getenv('MS_PORT_AUTH');   /* verlangt Anmeldung */

$gruen = 0; $rot = 0;
function fall($was, $ist, $soll)
{
    global $gruen, $rot;
    $ok = ($ist === $soll);
    if ($ok) { $gruen++; } else { $rot++; }
    printf("  [%s] %-52s ist=%-28s soll=%s\n", $ok ? 'ok' : 'ROT', $was,
           var_export($ist, true), var_export($soll, true));
}

echo "== 1. Struktur holen ==\n";
list($ok, $meld, $raeume, $bausteine) = rk_struktur_holen($MS);
fall('Struktur gelesen', $ok, 1);
fall('Meldung leer', $meld, '');
fall('Raeume (12 mit Fuehler + EG Flur ohne)', count($raeume), 13);
fall('Bausteine (12*8 + 3 Sonderfaelle + ohne Raum)', count($bausteine), 100);

echo "\n== 2. Vorschlag OHNE Kategoriefilter ==\n";
$v = rk_fuehler_vorschlag($bausteine, '');
$voll = 0; $namen = array();
foreach ($v as $e) {
    if ($e['t'] !== null && $e['rf'] !== null) { $voll++; }
    $namen[$e['raum']] = $e;
    printf("      %-26s T=%-32s RF=%-34s%s\n", $e['raum'],
        $e['t'] ? $e['t']['name'] : '-', $e['rf'] ? $e['rf']['name'] : '-',
        $e['t_mehr'] ? '  (' . ($e['t_mehr'] + 1) . ' T-Bewerber)' : '');
}
fall('Raeume im Vorschlag (EG Flur faellt heraus)', count($v), 12);
fall('davon vollstaendig', $voll, 12);
/* Der Kern: zugeordnet wird ueber den RAUM, nicht ueber den Namen. */
fall('Eltern bekommt "01) Temperatur OG Schlafzimmer"',
     $namen['OG Schlafzimmer Eltern']['t']['name'], '01) Temperatur OG Schlafzimmer');
fall('Blau bekommt "01) Temperatur Blau"',
     $namen['OG Schlafzimmer Blau']['t']['name'], '01) Temperatur Blau');
fall('Gelb bekommt NICHT die Kachel von Gruen',
     $namen['OG Schlafzimmer Gelb']['t']['name'], '01) Temperatur OG Gelb');
/* Batterie/Volt/Netzteil/Funksignal stehen in derselben Kategorie ... */
$stoerer = 0;
foreach ($v as $e) {
    foreach (array('t', 'rf') as $s) {
        if ($e[$s] === null) { continue; }
        if (preg_match('/Batterie|Volt|Netzteil|Funksignal|Schimmel|L.ften|Taupunkt|Soll/u',
                       $e[$s]['name'])) { $stoerer++; }
    }
}
fall('kein Batterie-/Volt-/Merker-/Taupunkt-/Sollbaustein vorgeschlagen', $stoerer, 0);
fall('Kueche hat einen zweiten T-Bewerber (Regelung, andere Kategorie)',
     $namen['EG Küche']['t_mehr'], 1);
fall('Wohnzimmer hat nur einen', $namen['EG Wohnzimmer']['t_mehr'], 0);

echo "\n== 3. Vorschlag MIT Kategoriefilter ==\n";
$v2 = rk_fuehler_vorschlag($bausteine, 'Feuchte');
$mehr = 0; $voll2 = 0;
foreach ($v2 as $e) {
    if ($e['t_mehr'] > 0) { $mehr++; }
    if ($e['t'] !== null && $e['rf'] !== null) { $voll2++; }
}
fall('Raeume unveraendert', count($v2), 12);
fall('immer noch alle vollstaendig', $voll2, 12);
fall('kein Raum mehr mit mehreren T-Bewerbern', $mehr, 0);
/* GEGENFALL zum Filter: ein Filter, auf den nichts passt, findet nichts. */
$v3 = rk_fuehler_vorschlag($bausteine, 'Rollladen');
fall('Filter ohne Treffer liefert nichts', count($v3), 0);

echo "\n== 4. Die Probe - der Pfad wird ABGELESEN, nicht angenommen ==\n";
$u_norm = ''; foreach ($bausteine as $b) {
    if ($b['name'] === '01) Temperatur Wohnzimmer') { $u_norm = $b['uuid']; } }
$faelle = array(
    'normale Form'   => array($u_norm, 1, 'LL.value', 19.0 + 6 * 0.7),
    'fremde Form'    => array('ffff0001-fremd----ffff112233445566', 1,
                              'daten.zustand.aktuell', 19.7),
    'nur ein Textfeld' => array('ffff0003-textnurr-ffff112233445566', 1,
                              'LL.messwert', 19.7),
);
foreach ($faelle as $bez => $e) {
    list($uu, $sok, $spfad, $szahl) = $e;
    list($pok, $pmeld, $pfad, $prohw, $pzahl) = rk_ms_probe($MS, $uu);
    fall($bez . ': gelesen', $pok, $sok);
    fall($bez . ': Pfad', $pfad, $spfad);
    fall($bez . ': Zahl', round((float) $pzahl, 2), round($szahl, 2));
}

echo "\n== 5. GEGENFAELLE der Probe ==\n";
/* Der Fund vom 29.08.2026: value ohne Zahl, aber Code=200 daneben. */
list($pok, $pmeld, $pfad, $prohw, $pzahl) = rk_ms_probe($MS,
    'ffff0002-ohnezahl-ffff112233445566');
fall('value ohne Zahl: abgewiesen', $pok, 0);
fall('value ohne Zahl: Meldung', $pmeld, 'MELD.MS_KEINE_ZAHL');
fall('value ohne Zahl: NICHT der Statuscode genommen', $pfad, '');
fall('value ohne Zahl: keine Zahl geliefert', $pzahl, null);

/* Der schaerfere Gegenfall: value ohne Zahl, daneben aber Funkpegel und
 * Batterie - beides Zahlen, beides keine Raumtemperatur. */
list($nok, $nmeld, $npfad, $nroh, $nzahl) = rk_ms_probe($MS,
    'ffff0004-nebenzah-ffff112233445566');
fall('Zahl daneben: trotzdem abgewiesen', $nok, 0);
fall('Zahl daneben: Meldung', $nmeld, 'MELD.MS_KEINE_ZAHL');
fall('Zahl daneben: NICHT den Funkpegel genommen', $npfad, '');
fall('Zahl daneben: keine Zahl geliefert', $nzahl, null);

list($pok2, $pmeld2) = rk_ms_probe($MS, 'gibt-es-nicht');
fall('unbekannter Baustein: abgewiesen', $pok2, 0);
fall('unbekannter Baustein: Meldung', $pmeld2, 'MELD.MS_HTTP');

list($ok4, $meld4) = rk_struktur_holen(array('nr' => '1', 'name' => 'x',
    'adresse' => '127.0.0.1', 'port' => 1, 'user' => 'a', 'pass' => 'b'), 3);
fall('falscher Port: abgewiesen', $ok4, 0);
fall('falscher Port: Meldung', $meld4, 'MELD.MS_STUMM');

echo "\n== 6. Anmeldung ==\n";
list($a1, $m1, $r1) = rk_struktur_holen($MSA);
fall('mit richtigem Passwort gelesen', $a1, 1);
fall('mit richtigem Passwort: Raeume', count($r1), 13);
$MSF = $MSA; $MSF['pass'] = '';
list($a2, $m2) = rk_struktur_holen($MSF);
fall('ohne Passwort: abgewiesen', $a2, 0);
fall('ohne Passwort: Meldung', $m2, 'MELD.MS_401');

echo "\n== 7. Kein Miniserver in LoxBerry ==\n";
$leer = rk_miniserver_gewaehlt(array('ms_nr' => ''), array());
fall('leere Liste liefert nichts', $leer, null);
$eins = rk_miniserver_gewaehlt(array('ms_nr' => ''), array('1' => $MS));
fall('ohne Wahl wird der einzige genommen', $eins === null ? '-' : $eins['name'],
     'Attrappe');
$zwei = rk_miniserver_gewaehlt(array('ms_nr' => '2'),
     array('1' => $MS, '2' => array('nr' => '2', 'name' => 'Zweiter')));
fall('die Wahl gilt', $zwei === null ? '-' : $zwei['name'], 'Zweiter');
$weg  = rk_miniserver_gewaehlt(array('ms_nr' => '9'), array('1' => $MS));
fall('gewaehlte Nummer gibt es nicht mehr -> erster', $weg === null ? '-' : $weg['name'],
     'Attrappe');

/* ======================================================================
 * ERGAENZT 30.08.2026.
 *
 * Abschnitt 8 misst gegen die GROSSE Attrappe (MS_GROSSE_ANLAGE=1, eigener
 * Port in MS_PORT_GROSS). Ohne sie war dreierlei strukturell unsichtbar:
 * ein zweiter Temperaturbewerber in DERSELBEN Kategorie, ein Raum mit nur
 * einer Haelfte, und mehr vollstaendige Raeume als Plaetze.
 *
 * Abschnitt 9 misst die Funktionen, die 0.11.2 neu hat. Sie brauchen keinen
 * Miniserver - aber sie brauchen eine Zeile, sonst bleibt jede Verbiegung
 * an ihnen gruen. Genau das hat die Eichung am 30.08.2026 gezeigt.
 * ====================================================================== */
$port_gross = (int) getenv('MS_PORT_GROSS');
if ($port_gross > 0) {
    echo "\n== 8. Die grosse Anlage: 18 Raeume auf 12 Plaetze ==\n";
    $MSG = $MS; $MSG['port'] = $port_gross;
    list($g_ok, $g_meld, $g_raeume, $g_bau) = rk_struktur_holen($MSG);
    fall('grosse Anlage gelesen', $g_ok, 1);
    fall('Raeume', count($g_raeume), 18);

    $gv = rk_fuehler_vorschlag($g_bau, '');
    $gn = array();
    foreach ($gv as $e) { $gn[$e['raum']] = $e; }

    /* 8a. Der zweite Bewerber in DERSELBEN Kategorie. */
    fall('Wohnzimmer hat jetzt zwei T-Bewerber', $gn['EG Wohnzimmer']['t_mehr'], 1);
    $gv_f = rk_fuehler_vorschlag($g_bau, 'Feuchte');
    $gnf = array();
    foreach ($gv_f as $e) { $gnf[$e['raum']] = $e; }
    /* DAS ist der Punkt: der Kategoriefilter raeumt diese Mehrdeutigkeit
     * NICHT ab - beide stehen in c1. Bis 30.08.2026 behauptete Abschnitt 3
     * "kein Raum mehr mit mehreren T-Bewerbern", und das galt nur, weil die
     * Attrappe den zweiten Bewerber stets in eine andere Kategorie legte. */
    fall('der Kategoriefilter raeumt DIESE Mehrdeutigkeit nicht ab',
         $gnf['EG Wohnzimmer']['t_mehr'], 1);

    /* 8b. Ein Raum mit nur einer Haelfte bleibt im Vorschlag stehen -
     *     er soll GEZEIGT und nicht angelegt werden. */
    fall('Garage steht im Vorschlag', isset($gn['Garage']), true);
    fall('  mit Temperatur', $gn['Garage']['t'] !== null, true);
    fall('  ohne Feuchte', $gn['Garage']['rf'], null);

    /* 8c. Namen mit ß und englische Namen. */
    fall('ein Raumname mit ss wird gefunden',
         isset($gn["Stra\xc3\x9fe"]) && $gn["Stra\xc3\x9fe"]['rf'] !== null, true);
    fall('"Humidity" gilt als Feuchtewort',
         isset($gn['Attic']) && $gn['Attic']['rf'] !== null, true);
    fall('  und "Temperature" als Temperaturwort',
         isset($gn['Attic']) && $gn['Attic']['t'] !== null, true);

    /* 8d. Randleerzeichen im Loxone-Raumnamen. */
    fall('Raumname mit Randleerzeichen kommt roh an',
         isset($gn['AA Werkstatt ']), true);
    fall('  und rk_raum_gleich() erkennt ihn wieder',
         rk_raum_gleich('AA Werkstatt', 'AA Werkstatt '), true);

    /* 8e. MEHR vollstaendige Raeume als Plaetze. */
    $g_voll = array();
    foreach ($gv as $e) {
        if ($e['t'] !== null && $e['rf'] !== null) { $g_voll[] = $e; }
    }
    fall('vollstaendige Raeume ueberschreiten RK_RAEUME',
         count($g_voll) > RK_RAEUME, true);

    /* 8f. Je Bauart eine Probe - und der Feuchtepfad wird EIGENS gemessen.
     *     Keller Nord traegt einen Feuchtebaustein der Bauart ShellyHT mit
     *     einem anderen Umschlag. Bis 0.11.1 wurde sein Pfad vom
     *     Temperaturbaustein abgeschrieben und war damit falsch. */
    $proben = rk_ms_proben($MSG, $g_voll);
    $t_typen = array_keys($proben['t']);
    $rf_typen = array_keys($proben['rf']);
    fall('je Bauart eine T-Probe, nicht je Raum', count($t_typen) <= 3, true);
    fall('ShellyHT hat eine EIGENE Feuchteprobe',
         isset($proben['rf']['ShellyHT']), true);
    fall('  und sie liest einen ANDEREN Pfad als die Temperatur',
         isset($proben['rf']['ShellyHT']) ? $proben['rf']['ShellyHT']['pfad'] : '-',
         'daten.zustand.aktuell');
    fall('  waehrend TextState bei LL.value bleibt',
         isset($proben['t']['TextState']) ? $proben['t']['TextState']['pfad'] : '-',
         'LL.value');
} else {
    echo "\n== 8. Die grosse Anlage: MS_PORT_GROSS nicht gesetzt - NICHT gemessen ==\n";
    echo "   (ohne sie bleiben Mehrdeutigkeit, halbe Raeume und der Ueberlauf ungeprueft)\n";
}

echo "\n== 9. Die Funktionen, die 0.11.2 neu hat ==\n";
$vorg = rk_raum_vorgabe();
fall('unberuehrter Platz ist frei', rk_platz_frei($vorg), true);
foreach (array('name', 'quelle', 'quelle_rf', 'pfad_t', 'pfad_rf',
               'pfad_co2', 'pfad_fenster', 'pfad_zuluft') as $feld) {
    $b = $vorg; $b[$feld] = 'x';
    fall('  ' . $feld . ' belegt den Platz', rk_platz_frei($b), false);
}
fall('Randleerzeichen: derselbe Raum', rk_raum_gleich('Bad ', 'Bad'), true);
fall('Grossschreibung: derselbe Raum', rk_raum_gleich('BAD', 'bad'), true);
fall('leerer Name: nie derselbe Raum', rk_raum_gleich('  ', 'Bad'), false);
fall('verschiedene Raeume bleiben verschieden', rk_raum_gleich('Bad', 'Bad OG'), false);

$zcfg = array('raeume' => array(array('quelle' => 'http://192.168.1.66/rpc/x',
                                      'quelle_rf' => '')),
              'quelle' => '', 'ms_nr' => '');
fall('Zugang an den Wirt der Raumquelle',
     rk_zugang_erlaubt('http://192.168.1.66/status', $zcfg), true);
fall('  aber nicht an eine fremde Adresse',
     rk_zugang_erlaubt('http://fremd.example/wetter', $zcfg), false);

fall('ohne HTTPS: http und einfacher Port',
     rk_ms_url(array('adresse' => '10.0.0.5', 'port' => 80, 'https' => 0), 'a'),
     'http://10.0.0.5:80/a');
fall('mit Preferhttps: https und TLS-Port',
     rk_ms_url(array('adresse' => '10.0.0.5', 'port' => 443, 'https' => 1), 'a'),
     'https://10.0.0.5:443/a');

printf("\n== Ergebnis: %d gruen, %d ROT ==\n", $gruen, $rot);
exit($rot > 0 ? 1 : 0);
