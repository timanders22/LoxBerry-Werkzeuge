<?php
/* Gehilfe von vorlagen_pruefen.py - erzeugt die Loxone-Importvorlagen EINER
 * Linie und legt sie im Ordner ZIEL ab.
 *
 * Warum ueberhaupt erzeugen und nicht den Quelltext lesen: die Plugins
 * liefern keine XML-Datei mit, sie bauen sie beim Knopfdruck zusammen. Was
 * der Anwender in Loxone Config sieht, steht nirgends als Zeichenkette in
 * einer Datei - es entsteht erst im Lauf.
 *
 * Warum nicht die Oberflaeche mit POST aufrufen: gemessen am 05.09.2026 an
 * Robonect - jede Linie weist ein Formular ohne gueltiges Sicherungsmerkmal
 * ab, der Download-Zweig wird nie erreicht. Der Weg misst den Pruefstand,
 * nicht das Plugin.
 *
 * Deshalb: die Bibliothek der Linie laden und ueber ReflectionFunction jede
 * Funktion aufrufen, deren Name 'vorlage' enthaelt und die ohne
 * Pflichtargument auskommt. Rueckgaben koennen sein: eine Zeichenkette,
 * array(dateiname, xml) oder eine Liste davon - alle drei Formen kommen im
 * Bestand vor. Was kein <Virtual...> enthaelt, wird verworfen.
 *
 * Aufruf:  php vorlagen_treiber.php <libdatei> [<libdatei> ...]
 * Umgebung: ZIEL (Ausgabeordner), LINIE (Name), dazu die LBP*DIR wie bei
 *           rendern.py.
 *
 * MUSTERWERTE=1 (seit 01.10.2026, X-4): zweiter, eigener Lauf. Er ruft die
 * Vorlagenfunktionen noch einmal auf, diesmal
 *   - mit jeder Art, die die Funktion selbst kennt (Parameter art, satz,
 *     zeitraum, typ, zeile, weg): die Werte stehen im Rumpf als Vergleich,
 *     in_array-Liste, case-Marke oder Schluessel einer mit [$art] befragten
 *     Tabelle, oder eine Funktion <kuerzel>_*arten() liefert sie;
 *   - mit Musterwerten fuer Pflichtargumente, deren NAME bekannt ist
 *     (cfg/c/config -> die eigene Konfigurationsfunktion der Linie, host,
 *     token, geraete, tags, nummer/nr/dev).
 * Anlass: AnkerSolix 0.9.24 - gemessen wurde nur die Statusvorlage
 * (ak_vorlage('status')), 'energie' und 'geraet' nie; 13 Linien lieferten
 * ohne Pflichtargument gar nichts. Ein eigener Prozess, weil eine Funktion,
 * die mit Musterwerten exit() erreicht, den Grundlauf nicht mitreissen darf.
 * Dateinamen: <LINIE>__<fn>__m-<argumente>.xml - der Grundlauf behaelt seine
 * Namen, damit Vorher/Nachher vergleichbar bleibt.
 */

error_reporting(E_ALL);
ini_set('display_errors', '0');

$ziel  = (string) getenv('ZIEL');
$linie = (string) getenv('LINIE');
if ($ziel === '' || !is_dir($ziel)) {
    fwrite(STDERR, "ABBRUCH: ZIEL fehlt oder ist kein Ordner\n");
    exit(2);
}

$vorher = get_defined_functions()['user'];
foreach (array_slice($argv, 1) as $lib) {
    try {
        require_once $lib;
    } catch (Throwable $e) {
        fwrite(STDERR, 'LADEFEHLER ' . basename($lib) . ': ' . $e->getMessage() . "\n");
    }
}
$neu = array_diff(get_defined_functions()['user'], $vorher);

/* Ablegen - und zwar nur, was wirklich eine Vorlage ist. */
function vt_ablegen($ziel, $linie, $fn, $nr, $xml)
{
    if (!is_string($xml) || strpos($xml, '<Virtual') === false) {
        return 0;
    }
    $name = sprintf('%s__%s%s.xml', $linie, $fn, $nr ? '_' . $nr : '');
    /* Der Dateiname wird gebaut, nicht uebernommen: die Funktionen liefern
     * teils eigene Namen mit Leerzeichen und Umlauten. */
    $name = preg_replace('/[^A-Za-z0-9_.-]/', '_', $name);
    file_put_contents($ziel . DIRECTORY_SEPARATOR . $name, $xml);
    return 1;
}

/* Rueckgabe einer Vorlagenfunktion ablegen - alle drei Formen. */
function vt_rueckgabe($ziel, $linie, $fn, $wert)
{
    $zahl = 0;
    if (is_string($wert)) {
        $zahl += vt_ablegen($ziel, $linie, $fn, 0, $wert);
    } elseif (is_array($wert)) {
        $i = 0;
        foreach ($wert as $teil) {
            $i++;
            if (is_string($teil)) {
                $zahl += vt_ablegen($ziel, $linie, $fn, $i, $teil);
            } elseif (is_array($teil)) {
                foreach ($teil as $t2) {
                    if (is_string($t2)) {
                        $zahl += vt_ablegen($ziel, $linie, $fn, $i, $t2);
                    }
                }
            }
        }
    }
    return $zahl;
}

/* ------------------------------------------------ Musterwerte (X-4) */

/* Die Arten, die eine Funktion fuer ihren Parameter $name selbst kennt. */
function vt_arten(ReflectionFunction $r, $name, $neu)
{
    $q = @file($r->getFileName());
    if (!$q) { return array(); }
    $rumpf = implode('', array_slice($q, $r->getStartLine() - 1,
                                     $r->getEndLine() - $r->getStartLine() + 1));
    $v = preg_quote('$' . $name, '/');
    $w = array();
    $lit = "'([a-z][a-z0-9_]{0,29})'";
    if (preg_match_all('/' . $v . '\s*[!=]==?\s*' . $lit . '/', $rumpf, $m)) { $w = array_merge($w, $m[1]); }
    if (preg_match_all('/' . $lit . '\s*[!=]==?\s*' . $v . '\b/', $rumpf, $m)) { $w = array_merge($w, $m[1]); }
    if (preg_match_all('/in_array\(\s*' . $v . '\s*,\s*(?:array\(|\[)([^\)\]]*)/', $rumpf, $m)) {
        foreach ($m[1] as $liste) {
            if (preg_match_all('/' . $lit . '/', $liste, $m2)) { $w = array_merge($w, $m2[1]); }
        }
    }
    if (preg_match('/switch\s*\(\s*' . $v . '\s*\)/', $rumpf)
            && preg_match_all('/case\s+' . $lit . '\s*:/', $rumpf, $m)) {
        $w = array_merge($w, $m[1]);
    }
    /* isset($tabelle[$art]) / $tabelle[$art]: die Schluessel der Tabelle */
    if (preg_match_all('/\$(\w+)\[\s*' . $v . '\s*\]/', $rumpf, $m)) {
        foreach (array_unique($m[1]) as $tab) {
            if (preg_match('/\$' . $tab . '\s*=\s*(?:array\(|\[)(.*?);/s', $rumpf, $m2)
                    && preg_match_all('/' . $lit . '\s*=>/', $m2[1], $m3)) {
                $w = array_merge($w, $m3[1]);
            }
        }
    }
    /* <kuerzel>_*arten(): eine Funktion, die die Arten der Linie nennt */
    if ($name === 'art') {
        $kurz = strtolower(strtok($r->getName(), '_'));
        foreach ($neu as $fn) {
            if (strpos($fn, $kurz . '_') === 0 && substr($fn, -5) === 'arten') {
                try {
                    $ra = new ReflectionFunction($fn);
                    if ($ra->getNumberOfRequiredParameters() > 0) { continue; }
                    $liste = $ra->invoke();
                } catch (Throwable $e) { continue; }
                if (is_array($liste)) {
                    foreach ($liste as $k => $x) {
                        $s = is_string($k) ? $k : (is_string($x) ? $x : '');
                        if (preg_match('/^[a-z][a-z0-9_]{0,29}$/', $s)) { $w[] = $s; }
                    }
                }
            }
        }
    }
    return array_values(array_unique($w));
}

/* Ein Wert aus einer eigenen, argumentlosen Funktion der Linie. */
function vt_eigen($kurz, $namen, $sonst)
{
    foreach ($namen as $n) {
        $fn = $kurz . '_' . $n;
        if (!function_exists($fn)) { continue; }
        try {
            $r = new ReflectionFunction($fn);
            if ($r->getNumberOfRequiredParameters() > 0) { continue; }
            ob_start();
            $x = $r->invoke();
            ob_end_clean();
            if ($x !== null && $x !== false) { return $x; }
        } catch (Throwable $e) {
            while (ob_get_level() > 0) { ob_end_clean(); }
        }
    }
    return $sonst;
}

/* Die Argumentlisten fuer eine Funktion, oder null (nicht aufrufbar). */
function vt_argumentlisten(ReflectionFunction $r, $neu)
{
    $kurz = strtolower(strtok($r->getName(), '_'));
    $listen = array(array());
    $anders = false;
    foreach ($r->getParameters() as $p) {
        $n = strtolower($p->getName());
        $opt = $p->isOptional();
        $std = $opt && $p->isDefaultValueAvailable() ? $p->getDefaultValue() : null;
        if (in_array($n, array('art', 'satz', 'zeitraum', 'typ', 'zeile', 'weg'), true)) {
            $werte = vt_arten($r, $p->getName(), $neu);
            if ($opt) {
                $werte = array_values(array_unique(array_merge(array($std), $werte)));
            } elseif ($werte) {
                /* Pflicht-Art: '' fuer den Zweig "alles andere" - APC-UPS,
                 * Beschattungswaechter, Ultraschall bauen dort ihre
                 * Eingangsvorlage (gemessen 01.10.2026). */
                $werte[] = '';
            }
            if (!$werte) { return null; }
            if (count($werte) > 1 || !$opt) { $anders = true; }
        } elseif (in_array($n, array('nummer', 'nr', 'dev', 'n'), true)) {
            $werte = array($opt ? $std : 1);
            if (!$opt) { $anders = true; }
        } elseif ($opt) {
            $werte = array($std);
        } elseif (in_array($n, array('cfg', 'c', 'config', 'konfig'), true)) {
            $werte = array(vt_eigen($kurz, array('config', 'config_read', 'config_lesen',
                                                 'config_laden', 'cfg', 'konfig'), array()));
            $anders = true;
        } elseif ($n === 'host') {
            $werte = array(vt_eigen($kurz, array('host', 'eigene_ip'), 'loxberry'));
            $anders = true;
        } elseif ($n === 'token') {
            $werte = array('MUSTERTOKEN0123456789abcdef');
            $anders = true;
        } elseif ($n === 'geraete') {
            $werte = array(vt_eigen($kurz, array('geraete', 'geraete_lesen'), array()));
            $anders = true;
        } elseif ($n === 'tags') {
            $werte = array(array());
            $anders = true;
        } else {
            return null;
        }
        $neu_l = array();
        foreach ($listen as $l) {
            foreach ($werte as $x) {
                $l2 = $l;
                $l2[] = $x;
                $neu_l[] = $l2;
            }
        }
        $listen = array_slice($neu_l, 0, 20);
    }
    return $anders ? $listen : null;
}

function vt_signatur($args)
{
    $t = array();
    foreach ($args as $a) {
        $t[] = is_scalar($a) ? (string) $a : (is_array($a) ? 'feld' : 'x');
    }
    return 'm-' . implode('-', $t);
}

if (getenv('MUSTERWERTE') === '1') {
    $zahl = 0;
    foreach ($neu as $fn) {
        if (stripos($fn, 'vorlage') === false
                || preg_match('/pruef|probe|ausliefern|merken/i', $fn)) {
            continue;
        }
        $r = new ReflectionFunction($fn);
        $listen = vt_argumentlisten($r, $neu);
        if ($listen === null) { continue; }
        foreach ($listen as $args) {
            try {
                ob_start();
                $wert = $r->invokeArgs($args);
                ob_end_clean();
            } catch (Throwable $e) {
                while (ob_get_level() > 0) { ob_end_clean(); }
                fwrite(STDERR, 'AUFRUFFEHLER ' . $fn . ': ' . $e->getMessage() . "\n");
                continue;
            }
            $zahl += vt_rueckgabe($ziel, $linie, $fn . '__' . vt_signatur($args), $wert);
        }
    }
    echo $zahl;
    exit(0);
}

$zahl = 0;
foreach ($neu as $fn) {
    if (stripos($fn, 'vorlage') === false) {
        continue;
    }
    try {
        $r = new ReflectionFunction($fn);
        if ($r->getNumberOfRequiredParameters() > 0) {
            continue;
        }
        /* Eigene Ausgabe der Funktion abfangen: manche Linien echo'en den
         * Kopf und geben nur den Rumpf zurueck. Was sie ausgeben, gehoert
         * nicht in die Messung - gemessen wird der Rueckgabewert. */
        ob_start();
        $wert = $r->invoke();
        ob_end_clean();
    } catch (Throwable $e) {
        while (ob_get_level() > 0) { ob_end_clean(); }
        fwrite(STDERR, 'AUFRUFFEHLER ' . $fn . ': ' . $e->getMessage() . "\n");
        continue;
    }
    if (is_string($wert)) {
        $zahl += vt_ablegen($ziel, $linie, $fn, 0, $wert);
    } elseif (is_array($wert)) {
        $i = 0;
        foreach ($wert as $teil) {
            $i++;
            if (is_string($teil)) {
                $zahl += vt_ablegen($ziel, $linie, $fn, $i, $teil);
            } elseif (is_array($teil)) {
                foreach ($teil as $t2) {
                    if (is_string($t2)) {
                        $zahl += vt_ablegen($ziel, $linie, $fn, $i, $t2);
                    }
                }
            }
        }
    }
}
echo $zahl;
