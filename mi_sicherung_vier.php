<?php
/**
 * Der Pruefstand fuer Sichern und Zurueckspielen - VIER Faelle.
 *
 * Die drei aus REGELN_2 (gueltig, halb gueltig, fremd) und der vierte, den
 * man vergisst, weil er so selbstverstaendlich aussieht: die EIGENE frisch
 * erzeugte Sicherung wieder einspielen. Genau dort hat das WiFi-Scanner-
 * Plugin seine eigene Datei abgelehnt.
 *
 * Gemessen wird nicht nur der Rueckgabewert, sondern die WIRKUNG: was steht
 * nach dem Versuch in midea2lox.cfg und in devices.cfg?
 */
require_once getenv('MI_LIB');

$fehler = 0;

function zeige($bez, $erwartet, $ist, $zusatz = '')
{
    global $fehler;
    $gut = ($erwartet === $ist);
    if (!$gut) { $fehler++; }
    printf("  %-52s %-12s %s%s\n", $bez, $ist, $gut ? 'wie erwartet' : 'ABWEICHUNG, erwartet ' . $erwartet,
           $zusatz !== '' ? '  ' . $zusatz : '');
}

function lage()
{
    $c = mi_config_read();
    $d = mi_devices();
    $ids = array();
    foreach ($d as $g) { $ids[] = $g['id'] . ($g['token'] !== '' ? '(V3)' : '(V2)'); }
    return $c['UDP_PORT'] . '/' . $c['region'] . '/' . $c['MideaUser']
         . ' | ' . (count($d) ? implode(',', $ids) : 'keine Geraete');
}

$T = str_repeat('a1', 64);   // 128 Hexziffern
$K = str_repeat('b2', 32);   // 64 Hexziffern

echo "AUSGANGSLAGE: " . lage() . "\n\n";

/* ---- Fall 4 zuerst: die EIGENE Sicherung erzeugen und wieder einspielen ---- */
echo "Fall 4 - die eigene Sicherung zurueckspielen (der vergessene Fall)\n";
$eigen = json_encode(mi_sicherung_bauen(), JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
echo "  Kopfzeilen der Datei: ";
$k = json_decode($eigen, true);
echo implode(', ', array_filter(array_keys($k), function ($x) { return $x[0] === '_'; })), "\n";
list($neu, $mangel, $n, $ng) = mi_sicherung_lesen($eigen);
zeige('eigene Sicherung wieder eingelesen', 'uebernommen',
      $neu === null ? 'abgewiesen' : 'uebernommen',
      $neu === null ? implode(' | ', array_map('strip_tags', $mangel)) : "$n Werte, $ng Geraete");

/* ---- Fall 1: gueltig, mit Geraeten ---- */
echo "\nFall 1 - gueltige Sicherung mit zwei Geraeten\n";
$gut = json_encode(array(
    '_hinweis' => 'Sicherung', '_plugin' => 'Midea2Lox', '_stand' => '2026-08-28 01:00',
    'einstellungen' => array('MINISERVER' => 'MINISERVER2', 'UDP_PORT' => '7014',
        'DEBUG' => '0', 'LoxberryIP' => '192.168.1.9', 'maxConnectionLifetime' => '120',
        'region' => 'AT', 'MideaUser' => 'neu@example.com', 'MideaPassword' => 'geheim',
        'mqtt_praefix' => 'Klima', 'abfragetakt' => '300', 'lox_timeout' => '7'),
    'geraete' => array(
        array('id' => '111122223333', 'typ' => 'AC', 'ip' => '192.168.1.60',
              'port' => '6444', 'bezeichnung' => 'Schlafzimmer', 'token' => $T, 'key' => $K),
        array('id' => '444455556666', 'typ' => 'AC', 'ip' => '192.168.1.61',
              'port' => '6444', 'bezeichnung' => '', 'token' => '', 'key' => ''),
    )));
list($neu, $mangel, $n, $ng) = mi_sicherung_lesen($gut);
zeige('Ergebnis', 'uebernommen', $neu === null ? 'abgewiesen' : 'uebernommen',
      $neu === null ? implode(' | ', array_map('strip_tags', $mangel)) : "$n Werte, $ng Geraete");
if ($neu !== null) {
    mi_config_write($neu[0]);
    mi_devices_write($neu[1]);
    echo "  Lage danach: " . lage() . "\n";
    zeige('Praefix uebernommen', 'Klima', mi_mqtt_topic());
    zeige('Abfragetakt uebernommen', '300', mi_config_read()['abfragetakt']);
}

/* ---- Fall 2: halb gueltig - EIN Geraet mit kaputtem Token ---- */
echo "\nFall 2 - halb gueltig: Einstellungen richtig, ein Token zu kurz\n";
$vorher = lage();
$halb = json_encode(array(
    '_plugin' => 'Midea2Lox',
    'einstellungen' => array('UDP_PORT' => '7099', 'region' => 'DE'),
    'geraete' => array(
        array('id' => '777788889999', 'ip' => '192.168.1.70', 'port' => '6444',
              'token' => 'zukurz', 'key' => $K),
    )));
list($neu, $mangel, $n, $ng) = mi_sicherung_lesen($halb);
zeige('Ergebnis', 'abgewiesen', $neu === null ? 'abgewiesen' : 'uebernommen',
      $neu === null ? implode(' | ', array_map('strip_tags', $mangel)) : '');
zeige('Lage UNVERAENDERT', $vorher, lage());

/* ---- Fall 2b: ein Wert ausserhalb der Positivliste ---- */
echo "\nFall 2b - halb gueltig: UDP_PORT 99999999\n";
$vorher = lage();
list($neu, $mangel) = mi_sicherung_lesen('{"UDP_PORT":"99999999","region":"DE"}');
zeige('Ergebnis', 'abgewiesen', $neu === null ? 'abgewiesen' : 'uebernommen',
      $neu === null ? implode(' | ', array_map('strip_tags', $mangel)) : '');
zeige('Lage UNVERAENDERT', $vorher, lage());

/* ---- Fall 2c: ein Feld statt einer Zeichenkette ---- */
echo "\nFall 2c - halb gueltig: UDP_PORT ist ein Feld\n";
$vorher = lage();
list($neu, $mangel) = mi_sicherung_lesen('{"UDP_PORT":["7014","x"]}');
zeige('Ergebnis', 'abgewiesen', $neu === null ? 'abgewiesen' : 'uebernommen',
      $neu === null ? implode(' | ', array_map('strip_tags', $mangel)) : '');
zeige('Lage UNVERAENDERT', $vorher, lage());

/* ---- Fall 3: fremde Sicherung ---- */
echo "\nFall 3 - Sicherung eines anderen Plugins\n";
$vorher = lage();
list($neu, $mangel) = mi_sicherung_lesen('{"_plugin":"WiFi-Scanner-NG","einstellungen":{"BASE.PORT":"7007"}}');
zeige('Ergebnis', 'abgewiesen', $neu === null ? 'abgewiesen' : 'uebernommen',
      $neu === null ? implode(' | ', array_map('strip_tags', $mangel)) : '');
zeige('Lage UNVERAENDERT', $vorher, lage());

/* ---- Fall 3b: alte flache Form aus 4.2.x ---- */
echo "\nFall 3b - alte flache Sicherung aus 4.2.x (muss weiter gehen)\n";
list($neu, $mangel, $n, $ng) = mi_sicherung_lesen(
  '{"MINISERVER":"MINISERVER1","UDP_PORT":"7013","DEBUG":"0","LoxberryIP":"","maxConnectionLifetime":"90","region":"DE","MideaUser":"a@b.de","MideaPassword":"x"}');
zeige('Ergebnis', 'uebernommen', $neu === null ? 'abgewiesen' : 'uebernommen',
      $neu === null ? implode(' | ', array_map('strip_tags', $mangel)) : "$n Werte, $ng Geraete");
if ($neu !== null) {
    $vorher_geraete = count(mi_devices());
    mi_devices_write($neu[1]);
    zeige('Geraete bleiben erhalten', (string) $vorher_geraete, (string) count(mi_devices()),
          'eine alte Sicherung kennt den Abschnitt nicht - sie darf nichts loeschen');
}

echo "\n" . ($fehler ? "$fehler ABWEICHUNG(EN)" : "Alle Faelle wie erwartet.") . "\n";
exit($fehler ? 1 : 0);
