<?php
/**
 * Ein nachgebauter Miniserver - gegen das Original gebaut, nicht gegen den
 * eigenen Client.
 *
 * Raumnamen, Bausteinnamen, Kategorie und die WERTE sind am 29.08.2026 an
 * der echten Anlage abgelesen (ueber die Loxone-Schnittstelle), nicht
 * erfunden. Die Namen sind absichtlich so uneinheitlich wie dort:
 *   "01) Temperatur Kueche", "01) Temperatur OG Gelb",
 *   "01) Temperatur OG Schlafzimmer" (= Eltern), "01) Temperatur Blau"
 * Genau daran muss sich zeigen, dass ueber den RAUM zugeordnet wird.
 * Am 07.11.2026 wurden die Vornamen in drei Raum- und Kachelnamen durch
 * Farben ersetzt (Blau, Gelb, Gruen); Aufbau, Reihenfolge und die
 * Uneinheitlichkeit der Namen sind dieselben.
 *
 * Der UMSCHLAG von jdev/sps/io/<uuid>/all ist dokumentiert, aber von mir
 * nicht am Geraet gemessen. Er steht deshalb hier als Annahme - und der
 * Assistent liest den Pfad ohnehin aus der Antwort, statt ihn anzunehmen.
 * Die Attrappe kennt dafuer einen Schalter: mit ?form=fremd antwortet sie
 * in einer ANDEREN Form, und der Assistent muss auch die lesen.
 */
$pfad = isset($_SERVER['PATH_INFO']) ? $_SERVER['PATH_INFO'] : '';
if ($pfad === '') {
    $pfad = parse_url(isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : '',
                      PHP_URL_PATH);
}
$pfad = ltrim((string) $pfad, '/');
$form = isset($_GET['form']) ? $_GET['form'] : 'normal';
/* Die Antwortform laesst sich AUCH ueber die UUID waehlen. Das ist kein
 * Beiwerk: rk_ms_probe() baut den Pfad selbst und haengt kein ?form= an.
 * Waehlte die Attrappe die Form nur ueber die Abfrage, muesste der
 * Pruefstand die Auswertung nachbauen - und maesse dann seine eigene Kopie
 * statt der ausgelieferten Funktion. Am 29.08.2026 ist genau das passiert. */
$FORM_UUID = array(
    'ffff0001-fremd----ffff112233445566'    => 'fremd',
    'ffff0002-ohnezahl-ffff112233445566'    => 'ohnezahl',
    'ffff0003-textnurr-ffff112233445566'    => 'textnur',
    'ffff0004-nebenzah-ffff112233445566'    => 'nebenzahl',
);

/* Die Anmeldung wird verlangt - sonst misst der Pruefstand den 401-Fall nie. */
$kopf = isset($_SERVER['HTTP_AUTHORIZATION']) ? $_SERVER['HTTP_AUTHORIZATION'] : '';
$erwartet = 'Basic ' . base64_encode('admin:geheim123');
if (getenv('MS_VERLANGT_ANMELDUNG') === '1' && trim($kopf) !== $erwartet) {
    /* Es genuegt NICHT, dass irgendein Basic-Kopf mitkommt: der Pruefstand
     * schickt auch admin mit leerem Passwort, und das muss durchfallen. */
    header('HTTP/1.1 401 Unauthorized');
    echo '{"LL":{"Code":"401"}}';
    exit;
}

$RAEUME = array(
    'r01' => 'Dachboden',            'r02' => 'KG Technikraum',
    'r03' => 'KG Hauswirtschaft',    'r04' => 'EG Gast',
    'r05' => 'EG Küche',             'r06' => 'EG Wohnzimmer',
    'r07' => 'OG Schlafzimmer Gelb',     'r08' => 'OG Schlafzimmer Gruen',
    'r09' => 'OG Schlafzimmer Blau',     'r10' => 'OG Schlafzimmer Eltern',
    'r11' => 'OG Duschbad',          'r12' => 'OG Wannenbad',
    'r13' => 'EG Flur',              // Raum ganz ohne Fuehler
);
/* Absichtlich uneinheitliche Kachelnamen, wie an der echten Anlage. */
$KURZ = array('r01' => 'Dachboden', 'r02' => 'Technikraum', 'r03' => 'Hauswirtschaft',
              'r04' => 'Gast', 'r05' => 'Kueche', 'r06' => 'Wohnzimmer',
              'r07' => 'OG Gelb', 'r08' => 'OG Gruen', 'r09' => 'Blau',
              'r10' => 'OG Schlafzimmer', 'r11' => 'Duschbad', 'r12' => 'OG Wannenbad');

$WERT = array();
$controls = array();
$i = 0;
foreach ($KURZ as $ru => $kurz) {
    $i++;
    $ut = sprintf('1e26391b-008c-%04x-ffffa9a4bd817a6f', 0x9990 + $i * 2);
    $uf = sprintf('1e26391b-008c-%04x-ffffa9a4bd817a6f', 0x9991 + $i * 2);
    $controls[$ut] = array('name' => '01) Temperatur ' . $kurz, 'room' => $ru,
                           'cat' => 'c1', 'type' => 'TextState');
    $controls[$uf] = array('name' => '02) Luftfeuchtigkeit ' . $kurz, 'room' => $ru,
                           'cat' => 'c1', 'type' => 'TextState');
    $WERT[$ut] = sprintf('%.1f °C', 19.0 + $i * 0.7);
    $WERT[$uf] = sprintf('%d %% - gut', 44 + $i);
    /* Batterie, Volt, Netzteil, Funksignal - dieselbe Kategorie, duerfen
     * aber NICHT als Fuehler vorgeschlagen werden. */
    foreach (array('03) Batterie', '04) Volt', '05) Netzteil', '06) Funksignal') as $j => $bez) {
        $ux = sprintf('1e26391b-00ff-%04x-ffffa9a4bd817a6f', $i * 16 + $j);
        $controls[$ux] = array('name' => $bez . ' ' . $kurz, 'room' => $ru,
                               'cat' => 'c1', 'type' => 'TextState');
        $WERT[$ux] = '87 %';
    }
    /* Und die abgeleiteten Merker, die dieselben Woerter tragen. */
    $um = sprintf('c1ea0711-0242-%04x-ffff112233445566', $i);
    $controls[$um] = array('name' => 'Feuchte hoch (Schimmelgefahr)', 'room' => $ru,
                           'cat' => 'c1', 'type' => 'InfoOnlyDigital');
    $WERT[$um] = '0';
    $ul = sprintf('c1ea0711-0303-%04x-ffff112233445566', $i);
    $controls[$ul] = array('name' => 'Lüften sinnvoll (außen trockener)', 'room' => $ru,
                           'cat' => 'c1', 'type' => 'InfoOnlyDigital');
    $WERT[$ul] = '1';
}
/* Ein Raumregler mit einer SOLL-Temperatur in einer anderen Kategorie -
 * er darf nur dann stoeren, wenn nicht nach Kategorie gefiltert wird. */
$controls['124e8564-017c-cdef-ffff112233445566'] =
    array('name' => 'Temperatur Sollwert', 'room' => 'r05', 'cat' => 'c2',
          'type' => 'IRoomControllerV2');
$WERT['124e8564-017c-cdef-ffff112233445566'] = '21.0 °C';
/* Und noch einer, dessen NAME voellig unverdaechtig ist - nur die Kategorie
 * unterscheidet ihn. Ohne ihn misst der Kategoriefilter nichts: den
 * Sollwert oben wirft schon die Namensliste heraus. */
$controls['124e8564-017c-abcd-ffff112233445566'] =
    array('name' => 'Temperatur Regelung Kueche', 'room' => 'r05', 'cat' => 'c2',
          'type' => 'IRoomControllerV2');
$WERT['124e8564-017c-abcd-ffff112233445566'] = '21.4 °C';
/* Ein Taupunkt im Wohnzimmer - traegt kein Temperaturwort, aber steht in
 * der Ausschlussliste. Gegenstueck zu den Merkern. */
$controls['124e8564-017c-dead-ffff112233445566'] =
    array('name' => 'Taupunkt Wohnzimmer', 'room' => 'r06', 'cat' => 'c1',
          'type' => 'TextState');
$WERT['124e8564-017c-dead-ffff112233445566'] = '12.3 °C';
/* Ein Raum ganz ohne Fuehler, und ein Baustein ohne Raum. */
$controls['aaaa0000-0000-0000-ffff112233445566'] =
    array('name' => '01) Temperatur ohne Raum', 'room' => '', 'cat' => 'c1',
          'type' => 'TextState');

/* ======================================================================
 * ERGAENZT 30.08.2026 - die Luecken, die die Gegenpruefung des Pruefstands
 * gefunden hat. Alle vier kommen an der ECHTEN Anlage vor; die Attrappe
 * konnte sie bis dahin nicht zeigen, und deshalb blieben Verbiegungen an
 * genau diesen Stellen gruen.
 *
 * Sie haengen an einem Schalter: OHNE `MS_GROSSE_ANLAGE=1` antwortet die
 * Attrappe wie bisher. Die 45 bestehenden Pruefzeilen zaehlen Raeume und
 * Bausteine, und sie sollen weiter genau dieselben Zahlen messen - eine
 * Erweiterung, die die alten Zeilen umschreibt, misst danach etwas
 * anderes als vorher, ohne dass jemand es merkt.
 * ====================================================================== */
if (getenv('MS_GROSSE_ANLAGE') === '1') {
    /* 1. ZWEI Temperaturbausteine im selben Raum UND in DERSELBEN
     *    Kategorie. Bisher stand der zweite Bewerber immer in einer
     *    anderen Kategorie (c2) - deshalb konnte der Pruefstand behaupten,
     *    der Kategoriefilter raeume die Mehrdeutigkeit restlos ab. An der
     *    echten Anlage stehen im KG Technikraum NEUNZEHN Bewerber, und der
     *    erste ist `Temp. Relay 1`, die Gehaeusetemperatur eines
     *    Relaismoduls. */
    $controls['1e26391b-00aa-0001-ffffa9a4bd817a6f'] =
        array('name' => 'Temp. Relay 1', 'room' => 'r06', 'cat' => 'c1',
              'type' => 'InfoOnlyAnalog');
    $WERT['1e26391b-00aa-0001-ffffa9a4bd817a6f'] = '48.5 °C';

    /* 2. Ein Raum mit nur EINER Haelfte. An der echten Anlage sind das
     *    Garage (nur Temperatur) und Zentral. Bis 0.11.1 verschwand so ein
     *    Raum wortlos aus der Vorschau. */
    $RAEUME['r14'] = 'Garage';
    $controls['1e26391b-00bb-0001-ffffa9a4bd817a6f'] =
        array('name' => 'Temp. Extension 9', 'room' => 'r14', 'cat' => 'c1',
              'type' => 'InfoOnlyAnalog');
    $WERT['1e26391b-00bb-0001-ffffa9a4bd817a6f'] = '23.1 °C';

    /* 3. MEHR vollstaendige Raeume als Plaetze. RK_RAEUME ist 12, und die
     *    Attrappe hatte bis dahin genau zwoelf - der Ueberlauf war damit
     *    strukturell unsichtbar. Drei weitere reichen. Einer traegt ein ß,
     *    einer einen englischen Namen (`Humidity` steht in der Wortliste,
     *    wurde aber von keiner Zeile gemessen), einer Randleerzeichen. */
    $ZUSATZ = array(
        'r15' => array('Straße', '01) Temperatur Straße', '02) Luftfeuchtigkeit Straße'),
        'r16' => array('Attic', '01) Temperature Attic', '02) Humidity Attic'),
        /* Der Name beginnt mit AA, damit er unter den ersten zwoelf
         * landet. ksort() geht byteweise; ein 'Werkstatt ' am Ende der
         * Liste bekommt bei achtzehn Raeumen und zwoelf Plaetzen nie
         * einen - und die Pruefzeile auf das Trimmen maesse nichts. */
        'r17' => array('AA Werkstatt ', '01) Temperatur Werkstatt',
                       '02) Luftfeuchtigkeit Werkstatt'),
    );
    $k = 0;
    foreach ($ZUSATZ as $ru => $z) {
        $k++;
        $RAEUME[$ru] = $z[0];
        $ut = sprintf('1e26391b-00cc-%04x-ffffa9a4bd817a6f', $k * 2);
        $uf = sprintf('1e26391b-00cc-%04x-ffffa9a4bd817a6f', $k * 2 + 1);
        $controls[$ut] = array('name' => $z[1], 'room' => $ru, 'cat' => 'c1',
                               'type' => 'TextState');
        $controls[$uf] = array('name' => $z[2], 'room' => $ru, 'cat' => 'c1',
                               'type' => 'TextState');
        $WERT[$ut] = sprintf('%.1f °C', 20.0 + $k);
        $WERT[$uf] = sprintf('%d %% - gut', 50 + $k);
    }

    /* 4. Ein Feuchtebaustein ANDERER BAUART, der einen anderen Umschlag
     *    liefert. Bis 0.11.1 wurde der Feuchtepfad vom Temperaturbaustein
     *    abgeschrieben; dieser Raum ist der Fall, an dem das auffliegt. */
    $RAEUME['r18'] = 'Keller Nord';
    $controls['1e26391b-00dd-0001-ffffa9a4bd817a6f'] =
        array('name' => '01) Temperatur Keller Nord', 'room' => 'r18', 'cat' => 'c1',
              'type' => 'TextState');
    $WERT['1e26391b-00dd-0001-ffffa9a4bd817a6f'] = '14.2 °C';
    $controls['ffff0001-fremd----ffff112233445566'] =
        array('name' => '02) Luftfeuchtigkeit Keller Nord', 'room' => 'r18',
              'cat' => 'c1', 'type' => 'ShellyHT');
}

if ($pfad === 'data/LoxAPP3.json') {
    header('Content-Type: application/json');
    $r = array(); foreach ($RAEUME as $u => $n) { $r[$u] = array('name' => $n, 'uuid' => $u); }
    echo json_encode(array(
        'msInfo' => array('projectName' => 'Musterhaus', 'msName' => 'Loxone-Muster'),
        'rooms' => $r,
        'cats' => array('c1' => array('name' => 'Temperatur & Feuchte Shelly'),
                        'c2' => array('name' => 'Raumtemperatur')),
        'controls' => $controls,
    ));
    exit;
}
/* Die Sonderbausteine, die eine andere Antwortform ausloesen. Sie tragen
 * denselben Messwert wie der erste Fuehler - verschieden ist nur der
 * Umschlag. */
foreach ($FORM_UUID as $u => $f) { $WERT[$u] = '19.7 °C'; }

if (preg_match('#^jdev/sps/io/([^/]+)/all$#', $pfad, $m)) {
    $u = rawurldecode($m[1]);
    if (isset($FORM_UUID[$u])) { $form = $FORM_UUID[$u]; }
    header('Content-Type: application/json');
    if (!isset($WERT[$u])) {
        header('HTTP/1.1 404 Not Found');
        echo '{"LL":{"Code":"404"}}';
        exit;
    }
    if ($form === 'fremd') {
        /* Eine ANDERE Form - der Assistent darf sich nicht auf LL.value
         * festgelegt haben. */
        echo json_encode(array('daten' => array('zustand' => array(
            'aktuell' => $WERT[$u], 'code' => '200'))));
        exit;
    }
    if ($form === 'ohnezahl') {
        /* Der Wert traegt keine Zahl - aber Code schon. Wer irgendein Feld
         * mit einer Zahl nimmt, traegt hier 200 ein. */
        echo json_encode(array('LL' => array('control' => $u, 'value' => 'keine Verbindung',
                                             'Code' => '200')));
        exit;
    }
    if ($form === 'nebenzahl') {
        /* value ohne Zahl - aber NEBEN ihm steht eine, und zwar in einem
         * Feld, das nicht 'code' heisst. Wer nicht am value entscheidet,
         * traegt hier den Funkpegel als Raumtemperatur ein. */
        echo json_encode(array('LL' => array(
            'value' => 'keine Verbindung', 'signal' => '-67',
            'battery' => '87', 'Code' => '200')));
        exit;
    }
    if ($form === 'textnur') {
        /* Gar kein value-Feld, aber eine ablesbare Zahl an anderer Stelle -
         * das darf gefunden werden. */
        echo json_encode(array('LL' => array('Code' => '200',
                                             'messwert' => $WERT[$u])));
        exit;
    }
    echo json_encode(array('LL' => array('control' => 'dev/sps/io/' . $u . '/all',
                                         'value' => $WERT[$u], 'Code' => '200')));
    exit;
}
header('HTTP/1.1 404 Not Found');
echo '{"LL":{"Code":"404"}}';
