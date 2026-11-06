#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deckt die Pruefung der Sprachausgabe wirklich, was sie behauptet?

Laeuft auf: Windows, Python 3 + php.exe 8.5.11 (und fuer zwei Faelle 7.4.33).

Bauform wie mutation_planer.py: je eine absichtliche VERFAELSCHUNG kommt in eine Kopie von
gemeinsam/sprachausgabe.php. Danach laeuft entweder der eingebaute Selbsttest
(php sprachausgabe.php --selbsttest) oder - fuer den echten Transport, den der Selbsttest
mit seiner Attrappe nicht sieht - Werkzeuge/sprachausgabe_probe.py gegen die Kopie. Bleibt
die Pruefung gruen, hat die Mutation UEBERLEBT: dann prueft nichts diese Stelle.

    python mutation_sprachausgabe.py [<Pfad zu sprachausgabe.php>] [--nur NAME,NAME]

Ohne Pfad: gemeinsam/sprachausgabe.php neben diesem Werkzeug. Vor den Mutationen muss die
UNVERAENDERTE Datei beide Pruefungen bestehen, sonst Abbruch (eine rote Pruefung erkennt
jede Mutation und misst nichts). Jeder Anker muss genau einmal treffen.
Rueckgabe 1, wenn eine Mutation ueberlebt oder ein Anker nicht genau einmal trifft.

Anker auf Fassung 1.1.1 (08.10.2026): die 1.0.2-Anker, die 1.1.0 umgebaut hat (Erfolgsmerkmal,
Vorlagenpruefung, Webport, Statuszeile des Datenstroms), sind nachgezogen; neu sind die
Mutationen fuer die Neuerungen aus 1.1.0 (IPv4 nur streng dezimal, Zahl ist kein Name, IPv6,
Benutzerangabe, Lautstaerke 0, Zonen, Umleitung) und 1.1.1 (.intern, Huellen fuer 1.0.3-Aufrufe,
leere Zonenliste, Fehlertext bei Netzfehlern). Die Datei muss LF tragen: mit CRLF trifft ein
mehrzeiliger Anker 0-mal (das Werkzeug bricht dann ab, statt "nicht eindeutig" zu zaehlen).

Fassung 1.1.2 (09.10.2026, Kopie in Pruefung-Durchgang-2026-09-29/sprachmodul_112/neu/): der Anker
webport_grossschreibung ist auf die neue Form von ansage_webport_aus() nachgezogen (dieselbe
Verfaelschung: ohne $weit nur noch 'Webserver'); neu sind die Mutationen s112_* fuer 1.1.2 (Saetze
K_TTS_EINTRAG/K_KEIN_FELD, $weit, Werk-Kontext, M_-Meldung ohne doppelten Feldnamen, Zeichen bei
ungueltigem UTF-8). Pruefart 'selbst_mb' laesst den Selbsttest mit geladenem mbstring laufen (nur so
ist der Zweig mb_strlen zu treffen; 'selbst' laeuft mit -n, also ohne mbstring).
    --php PFAD   php.exe fuer 'selbst' und 'selbst_mb' (ab Werk 8.5.11); die Probe-Laeufe waehlen ihre
                 PHP-Fassung selbst (74/84/85 im Namen).

Fassung 1.1.4 (25.10.2026, Pflegewelle 22, Kopie in Pruefung-Durchgang-2026-09-29/stamm_pw22/werkzeug_nachher/):
alle Anker der 1.1.3 treffen unveraendert; neu sind die Mutationen s114_* fuer SonoX (GET, Pfadsegmente,
Erfolg nur mit status=success, Fehlerkennungen ohne Text, Port nur aus settings.json, Punkt-Texte,
Pruefzeile mit /zones nur bei offenem Reiter), ansage_plugin_da(), die berichtigte Pruefzeile sonos4lox
(Installation, Zonenschluessel, Vorschlag) und das Formular (nur geschickte Felder, Block nur mit 'sonox'
in der Modusliste). Eine Probe-Kopie mit der neuen Textdatei kommt ueber SPRACHAUSGABE_PROBE.

Fassung 1.2.0 (27.10.2026, Vorschlag in Pruefung-Durchgang-2026-09-29/sm120_bau/werkzeug/, Ordner TMP *_120):
neu sind die Mutationen s120_* fuer mehrere Ausgabeziele (die zehn aus probe_mutation120.txt des Entwurfs, dazu
Doppel in Wertpruefung/Formular, Hoechstzahl, Spaetliste, Testknopf-Nummer und -Klasse, Formular ohne Opt-in,
kuerzen im Zielpruefer, abgebrochener Rumpf in ansage_http_zerlegen()); nachgezogen s113_kuerzen_573,
curl_proxy (Optionen jetzt in ansage_curl_optionen()) und datenstrom_laenge (je ein Zwilling im neuen Code).
Nachbesserung 27.10.2026 (Befund am Geraet, Echo mit Sprache rot): neu s120n_* (Sprache bei Echo/Google/Sonos4Lox
verwerfen und als Hinweis nennen, Feld gesperrt ohne Wert, Platzhalter SonoX, Hilfesaetze Tabelle und Ziel 1).

Fassung 1.2.1 (29.10.2026, Vorschlag in Pruefung-Durchgang-2026-09-29/stamm_sprachmodul_121/werkzeug_nachher/):
$k['frist'] gilt in jedem Weg (ansage_frist(), Kappung in ansage_anfrage(), Zahl in den Zeit-Kennungen). Anker
s114_zeile_mit_rumpf nachgezogen (die Zeile nennt jetzt ansage_frist(ANSAGE_TMO_SONOX, $k)); neu s121_* (sechs,
alle ueber den Selbsttest). Die Zeile im Mehrziel-Weg ($anf['tmo'] = min(..., $k['frist'])) ist seit 1.2.1
doppelt gesichert - eine Mutation dort ueberlebte und steht deshalb nicht in der Liste.

Messfalle: nie zwei Laeufe gleichzeitig - beide raeumen denselben Ordner C:\\tmp\\sprachmodul_mutation.

WAS ES NICHT KANN: Es misst, ob eine Stelle ANGEFASST wird, nicht ob sie richtig ist. Die
Verbindungsfrist von 3 s (curl) bleibt ungemessen - dafuer braeuchte es ein Ziel, das
Verbindungen verschluckt, und das gibt es auf 127.0.0.1 nicht. Die Benutzerangabe ist in
ansage_url_grund() dreifach gesichert (@ in der Autoritaet, user/pass aus parse_url, Muster der
Autoritaet); das Entfernen EINER dieser Stellen aendert nichts und waere als Mutation immer
"ueberlebt" - gemessen wird deshalb die Kennung (benutzer_kennung).
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HIER = Path(__file__).resolve().parent
PHP85 = Path(r'C:\tmp\php-8.5.12-Win32-vs17-x64\php.exe')
PHP = PHP85
TMP = Path(r'C:\tmp\sprachmodul_mutation_120')
# Die Probe liegt neben diesem Werkzeug (Werkzeuge/) - oder, solange es im Arbeitsordner einer
# Pruefung liegt, unter Werkzeuge/ der Werkstatt.
PROBE = HIER / 'sprachausgabe_probe.py'
if not PROBE.is_file():
    PROBE = HIER.parents[1] / 'Werkzeuge' / 'sprachausgabe_probe.py'
# Eine Messkopie der Probe (etwa mit einer vorgeschlagenen Textdatei) ueber die Umgebung.
if os.environ.get('SPRACHAUSGABE_PROBE'):
    PROBE = Path(os.environ['SPRACHAUSGABE_PROBE']).resolve()

# (Name, Anker, Ersatz, Pruefung) - Pruefung 'selbst' oder 'probe:<laeufe>'
MUTATIONEN = [
    ('token_muster', r"preg_match('/^[A-Za-z0-9_\-]{8,128}\z/', $t)", r"preg_match('/^[A-Za-z0-9_\-]{0,128}\z/', $t)", 'selbst'),
    ('erfolg_nur_200', "if ($a['code'] === 200 && preg_match('/^' . preg_quote($praefix, '/') . ';OK=1",
     "if ($a['code'] >= 200 && preg_match('/^' . preg_quote($praefix, '/') . ';OK=1", 'selbst'),
    ('token_ersetzen', "$erste = str_replace($felder['token'], '***', $erste);", "$erste = $erste;", 'selbst'),
    ('text_steuerzeichen', r"if (preg_match('/[\x00-\x1F\x7F]/', $text)) { return array(0, 'TEXT_STEUERZEICHEN'); }", "", 'selbst'),
    ('text_hoechstlaenge', "if (ansage_zeichen($text) > ANSAGE_TEXT_MAX)", "if (ansage_zeichen($text) > 10 * ANSAGE_TEXT_MAX)", 'selbst'),
    ('text_spitze_klammern', "strpbrk($text, '<>') !== false", "false", 'selbst'),
    # 1.1.2: Anker nachgezogen (ansage_webport_aus() mit $weit), Verfaelschung unveraendert
    ('webport_grossschreibung', ": array('Webserver', 'WEBSERVER');", ": array('Webserver');", 'selbst'),
    ('heimnetz_172', "if ($o[0] === 172 && $o[1] >= 16 && $o[1] <= 31) { return true; }", "if ($o[0] === 172) { return true; }", 'selbst'),
    ('vorlage_heimnetz', "$ug = ansage_url_grund($muster);", "$ug = '';", 'selbst'),
    ('vor_dem_senden_pruefen', "if (ansage_wert_pruefen($pruef, $grund) === null) {", "if (false) {", 'selbst'),
    ('sicherung_token_als_liste', "if (array_key_exists($s, $tts) && $tts[$s] !== '') { $namen[] = 'tts.' . $s; }",
     "if (!empty($tts[$s]) && is_string($tts[$s])) { $namen[] = 'tts.' . $s; }", 'selbst'),
    ('sicherung_ohne_token', "foreach (ansage_geheim() as $s) { unset($tts[$s]); }", "", 'selbst'),
    ('sicherung_token_behalten', "$neu[$s] = (is_array($jetzt) && isset($jetzt[$s]) && is_string($jetzt[$s])) ? $jetzt[$s] : '';",
     "$neu[$s] = isset($jetzt[$s]) ? $jetzt[$s] : '';", 'selbst'),
    ('form_widerspruch', "            if ($t !== '') {\n                $melden('M_' . $art_k . '_LOESCHEN_WIDERSPRUCH'",
     "            if (false) {\n                $melden('M_' . $art_k . '_LOESCHEN_WIDERSPRUCH'", 'selbst'),
    ('form_ohne_token', "if (empty($opt['token_vor_ort']) && $neu['mode'] === $gew && $tok === ''", "if (false && $tok === ''", 'selbst'),
    ('html_token_in_seite', "sprintf($t('P_TOKEN_DA'), strlen($gesp))", "sprintf($t('P_TOKEN_DA'), strlen($gesp)) . $gesp", 'selbst'),
    ('weiterleitung_ist_erfolg', "    if ($status >= 300) { return 'HTTP_WEITERLEITUNG|' . $status; }\n", "", 'selbst'),
    # 1.1.4: Anker auf den NG-Zweig verengt (der SonoX-Zweig hat ein zweites "if (!$offen) {", s114_pz_sonox_fragt_zu)
    ('pruefzeile_bei_zu', "    if (!$offen) {\n        return array(-2, $e(ansage_t('T_' . $art_k . '_ZU', $k)));", "    if (false) {\n        return array(-2, $e(ansage_t('T_' . $art_k . '_ZU', $k)));", 'selbst'),
    ('fehlt_404', "    if ($a['code'] === 404) {\n        return $art_k . '_FEHLT|'", "    if (false) {\n        return $art_k . '_FEHLT|'", 'selbst'),
    ('cli_rueckgabe', "return array($r['stand'] === 1 ? 0 : ($r['stand'] === -1 ? 3 : 1), $z);",
     "return array($r['stand'] === 1 ? 0 : 1, $z);", 'selbst'),
    ('verbindungsfrist_beschrieben', "'verbinden' => min(ANSAGE_TMO_VERBINDEN, $tmo),", "'verbinden' => $tmo,", 'selbst'),
    ('umleitung_beschrieben', "'umleitung' => false,", "'umleitung' => true,", 'selbst'),
    # --- Neuerungen 1.1.0 ---
    ('ipv4_streng', r"if (!preg_match('/^(0|[1-9]\d{0,2})(\.(0|[1-9]\d{0,2})){3}\z/', $h)) { return false; }",
     r"if (!preg_match('/^(\d{1,3})(\.(\d{1,3})){3}\z/', $h)) { return false; }", 'selbst'),
    ('zahl_ist_kein_name', r"if (preg_match('/^[0-9.]+\z/', $h) || strpos($h, '0x') === 0) {",
     r"if (strpos($h, '.') !== false && preg_match('/^[0-9.]+\z/', $h)) {", 'selbst'),
    ('ipv6_nur_heimnetz', "if (($o[0] & 0xFE) === 0xFC) { return true; }", "if (true) { return true; }", 'selbst'),
    ('benutzer_kennung', "if (strpos($m[2], '@') !== false) { return 'TTS_VORLAGE_BENUTZER'; }",
     "if (strpos($m[2], '@') !== false) { return 'TTS_VORLAGE_HTTP'; }", 'selbst'),
    ('fertige_adresse_pruefen', "$ug = ansage_url_grund($url);", "$ug = '';", 'selbst'),
    ('laut_null', "if ($i === 0) { $grund = 'AUSSERHALB|1|100'; return null; }", "", 'selbst'),
    ('erfolg_genau', r"';OK=1(?:;|\z)/'", "';OK=1/'", 'selbst'),
    ('zonen_lautstaerke', "if ((int) $v < 1 || (int) $v > 100) { return false; }", "", 'selbst'),
    ('umleitung_fremdes_ziel', "if (strtolower($nach['scheme']) !== 'https' || !in_array(strtolower($nach['host']), $loop, true)",
     "if (strtolower($nach['scheme']) !== 'https'", 'selbst'),
    # --- Neuerungen 1.1.1 (vertraeglich mit 1.0.3) ---
    ('intern_endung', r"|internal|intranet|intern)\z/", r"|internal|intranet)\z/", 'selbst'),
    ('zonen_leer', "if (is_string($z) && preg_match('/^ *\\z/', $z)) { return true; }", "", 'selbst'),
    ('netz_fehlertext', "return 'HTTP_NETZ|' . $errno . ($f !== '' ? '|' . $f : '');", "return 'HTTP_NETZ|' . $errno;", 'selbst'),
    ('netz_fehlertext_ng', "$gid = ansage_http_grund_id($a['errno'] === 0 ? -1 : $a['errno'], 0, $a['fehler']);",
     "$gid = ansage_http_grund_id($a['errno'] === 0 ? -1 : $a['errno'], 0);", 'selbst'),
    ('netz_fehlertext_sonos', "$a['code'],\n                                                 $a['fehler']);",
     "$a['code']);", 'selbst'),
    ('netz_fehlertext_klassisch', "$a['errno']), $a['code'], $a['fehler']);\n    $r['kennung'] = $gid;",
     "$a['errno']), $a['code']);\n    $r['kennung'] = $gid;", 'selbst'),
    ('huelle_url_heimnetz', "return ansage_url_grund($url) === '';", "return true;", 'selbst'),
    ('huelle_vorlage_platzhalter', r"if (preg_match('/\{(?!ip\}|port\})/', $m[1])) { return 'TTS_VORLAGE_HEIMNETZ'; }", "", 'selbst'),
    ('huelle_vorlage_benutzer', "($g === 'TTS_VORLAGE_HEIMNETZ' || $g === 'TTS_VORLAGE_BENUTZER') ? 'TTS_VORLAGE_HEIMNETZ'",
     "($g === 'TTS_VORLAGE_HEIMNETZ') ? 'TTS_VORLAGE_HEIMNETZ'", 'selbst'),
    # --- Neuerungen 1.1.2 ---
    ('s112_saetze_im_schluessel', "// seit 1.1.2\n               'K_TTS_EINTRAG', 'K_KEIN_FELD', ", "// seit 1.1.2\n               ", 'selbst'),
    ('s112_weit_abschnitt', "array('Webserver', 'WEBSERVER', 'webserver') : ", "array('Webserver', 'WEBSERVER') : ", 'selbst'),
    ('s112_weit_schluessel', "$namen = $weit ? array('Port', 'port', 'PORT') : array('Port');",
     "$namen = $weit ? array('Port', 'port') : array('Port');", 'selbst'),
    ('s112_weit_nur_true', "$weit = ($weit === true);", "$weit = (bool) $weit;", 'selbst'),
    ('s112_weit_ohne_weit_gleich', ": array('Port');\n", ": array('Port', 'port');\n", 'selbst'),
    ('s112_weit_durchreichen', "return ansage_webport_aus($roh === false ? '' : $roh, $weit === true);",
     "return ansage_webport_aus($roh === false ? '' : $roh);", 'selbst'),
    ('s112_werk_hinweis', "if ($w === 'aus' || isset($k['schluessel']['ART_HINWEIS'])) { return ansage_t('ART_HINWEIS', $k); }",
     "return ansage_t('ART_HINWEIS', $k);", 'selbst'),
    ('s112_werk_umlenkung', "if ($w === 'aus' || isset($k['schluessel']['ART_HINWEIS']))", "if ($w === 'aus')", 'selbst'),
    ('s112_werk_aus_schlicht', "return isset($k['schluessel']['O_AUS']) ? $name : ansage_t('O_AUS_SCHLICHT', $k);",
     "return $name;", 'selbst'),
    ('s112_werk_markiert', "return $modus === $w ? sprintf(ansage_t('O_WERK', $k), $name) : $name;", "return $name;", 'selbst'),
    ('s112_werk_vorgabe', "if ($w === 'aus') { return $name; }", "", 'selbst'),
    ('s112_werk_pruefen', "return (is_string($w) && in_array($w, ansage_modi(), true)) ? $w : 'aus';",
     "return is_string($w) ? $w : 'aus';", 'selbst'),
    ('s112_werk_im_formular', "$e(ansage_art_hinweis($k))", "$e($t('ART_HINWEIS'))", 'selbst'),
    ('s112_werk_wahl_im_formular', "$e(ansage_wahl_text($mo, $k))", "$e($t('O_' . strtoupper($mo)))", 'selbst'),
    ('s112_M_einmal', "if (count($teile) >= 3 && $teile[0] === 'UNTER') { $teile = array_slice($teile, 2); }", "", 'selbst'),
    ('s112_zeichen_muster', "    $n = @preg_match_all('/[\\x00-\\x7F]|", "    $n = false && @preg_match_all('/[\\x00-\\x7F]|", 'selbst'),
    ('s112_zeichen_mb', "$m = @mb_strlen($text, 'UTF-8');", "$m = strlen($text);", 'selbst_mb'),
    # --- Neuerungen 1.1.3 (S3, S4, S5) ---
    ('s113_kuerzen_aus', "    for ($i = 1; $i <= 3 && strlen($b) > 0; $i++) {", "    for ($i = 1; $i <= 0; $i++) {", 'selbst'),
    # 1.2.0: Anker auf ansage_wert_pruefen() verengt (ansage_ziel_pruefen() traegt dieselbe Zeile, s120_kuerzen_ziel)
    ('s113_kuerzen_573', "                $aus['ziele'] = $zl;\n                break;\n            default:\n                $grund = 'TTS_EINTRAG|' . str_replace('|', '/', ansage_kuerzen((string) $s, 40));",
     "                $aus['ziele'] = $zl;\n                break;\n            default:\n                $grund = 'TTS_EINTRAG|' . str_replace('|', '/', substr((string) $s, 0, 40));", 'selbst'),
    ('s120_kuerzen_ziel', "$aus['ein'] = ($w === 1 || $w === '1' || $w === true) ? 1 : 0;\n                break;\n            default:\n                $grund = 'TTS_EINTRAG|' . str_replace('|', '/', ansage_kuerzen((string) $s, 40));",
     "$aus['ein'] = ($w === 1 || $w === '1' || $w === true) ? 1 : 0;\n                break;\n            default:\n                $grund = 'TTS_EINTRAG|' . str_replace('|', '/', substr((string) $s, 0, 40));", 'selbst'),
    ('s113_kuerzen_zeile', "'zeile' => ansage_kuerzen($erste, 200),", "'zeile' => substr($erste, 0, 200),", 'selbst'),
    ('s113_letzte_substitute', "'zeile' => (string) $r['zeile']), JSON_INVALID_UTF8_SUBSTITUTE);", "'zeile' => (string) $r['zeile']));", 'selbst'),
    ('s113_absender_muster', r"&& preg_match('/^[a-z0-9_\-]{1,32}\z/', $k['absender'])) {", r"&& preg_match('/^.*\z/s', $k['absender'])) {", 'selbst'),
    ('s113_absender_nur_ng', "if ($modus === 'alexang' && isset($k['absender'])", "if (isset($k['absender'])", 'selbst'),
    ('s113_cli_dringend', "$r = ansage_sprechen($d['text'], $tts, $k, $opt);", "$r = ansage_sprechen($d['text'], $tts, $k);", 'selbst'),
    # --- 1.1.4 (Pflegewelle 22): SonoX, ansage_plugin_da(), Pruefzeile sonos4lox berichtigt ---
    ('s114_modus_fehlt', "'sonos4lox', 'sonox', 'tafel', 'homepod4lox');", "'sonos4lox', 'tafel', 'homepod4lox');", 'selbst'),
    ('s114_post_statt_get', "ansage_anfrage('GET', $url, null, ANSAGE_TMO_SONOX, $k)", "ansage_anfrage('POST', $url, null, ANSAGE_TMO_SONOX, $k)", 'selbst'),
    ('s114_erfolg_ohne_status', "isset($j['status']) && $j['status'] === 'success') ? '' : 'SONOX_UNERWARTET|200';", "true) ? '' : 'SONOX_UNERWARTET|200';", 'selbst'),
    ('s114_urlencode', "    return rawurlencode((string) $s);\n}", "    return urlencode((string) $s);\n}", 'selbst'),
    ('s114_raum_unbekannt', "if (preg_match(\"/^action '.*' not found\\\\z/s\", $f)) { return 'SONOX_RAUM_UNBEKANNT'; }", "", 'selbst'),
    ('s114_keine_anlage', "if (strpos($f, 'No system has yet been discovered') !== false) { return 'SONOX_KEINE_ANLAGE'; }", "", 'selbst'),
    ('s114_fehler_mit_text', "        return 'SONOX_FEHLER|500';", "        return 'SONOX_FEHLER|500|' . str_replace('|', '/', $f);", 'selbst'),
    ('s114_dienst_aus', "if ((int) $a['errno'] === 7) { return 'SONOX_DIENST_AUS|' . $basis; }", "", 'selbst'),
    ('s114_zeit_unklar', "if ((int) $a['errno'] === 28 && (int) $tmo > 0) {", "if (false) {", 'selbst'),
    ('s114_port_fest', "            if ($i >= 1 && $i <= 65535) { return $i; }\n        }\n    }\n    return 5005;", "        }\n    }\n    return 5005;", 'selbst'),
    ('s114_port_bereich', "            if ($i >= 1 && $i <= 65535) { return $i; }\n        }\n    }\n    return 5005;", "            return $i;\n        }\n    }\n    return 5005;", 'selbst'),
    ('s114_port_aus_wurzel', "    $f = $h . '/data/plugins/' . ansage_plugin_ordner('sonox', $home) . '/settings.json';", "    $f = $h . '/config/plugins/sonox/settings.json';", 'selbst'),
    ('s114_laut_ungeprueft', "        $laut = ansage_tts_laut($tts, 'sonox_laut', $grund);", "        $laut = (int) $tts['sonox_laut'];", 'selbst'),
    ('s114_sprache_weg', "             . ansage_sonox_segment($sprache) . ($laut >= 1 ? '/' . $laut : '');", "             . ($laut >= 1 ? '/' . $laut : '');", 'selbst'),
    ('s114_dringend_gesendet', "             . ansage_sonox_segment($sprache) . ($laut >= 1 ? '/' . $laut : '');", "             . ansage_sonox_segment($sprache) . ($laut >= 1 ? '/' . $laut : '') . (empty($opt['dringend']) ? '' : '?urgent=1');", 'selbst'),
    ('s114_text_punkte', "        if ($text === '.' || $text === '..') {", "        if (false) {", 'selbst'),
    # 1.2.1: Anker nachgezogen (Kennung nennt die gekappte Frist), Verfaelschung unveraendert
    ('s114_zeile_mit_rumpf', "        $r['kennung'] = ansage_sonox_grund($a, $basis, ansage_frist(ANSAGE_TMO_SONOX, $k));", "        $r['kennung'] = ansage_sonox_grund($a, $basis, ansage_frist(ANSAGE_TMO_SONOX, $k));\n        $r['zeile'] = substr((string) $a['rumpf'], 0, 200);", 'selbst'),
    ('s114_raum_punkte', "if (!ansage_geraet_ok($w) || preg_match('/^\\.+\\z/', $w)) { $grund = 'TTS_SONOX_RAUM'; return null; }", "if (!ansage_geraet_ok($w)) { $grund = 'TTS_SONOX_RAUM'; return null; }", 'selbst'),
    ('s114_sprache_muster', "!preg_match('/^[a-z]{2}(-[a-z]{2})?\\z/', $w)) { $grund = 'TTS_SONOX_SPRACHE'; return null; }", "!preg_match('/^[A-Za-z_\\-]{2,6}\\z/', $w)) { $grund = 'TTS_SONOX_SPRACHE'; return null; }", 'selbst'),
    ('s114_letzte_datei', "$art === 'sonos' || $art === 'sonox' || $art === 'tafel' || $art === 'homepod')", "$art === 'sonos' || $art === 'tafel' || $art === 'homepod')", 'selbst'),
    ('s114_tafel', "        'sonox' => array(array('sonox'), 'sonox'),\n", "", 'selbst'),
    ('s114_da_immer', "    return ansage_plugin_ordner_aus($json, $namen, \"\\0\") !== \"\\0\";", "    return true;", 'selbst'),
    ('s114_pz_sonos_installation', "        if ($da === false) {\n            return ansage_mit_letzter(array(0, $e(ansage_kennung_text('SONOS_NICHT_INSTALLIERT', $k))), $l, $k);", "        if (false) {\n            return ansage_mit_letzter(array(0, $e(ansage_kennung_text('SONOS_NICHT_INSTALLIERT', $k))), $l, $k);", 'selbst'),
    ('s114_pz_sonos_zone', "            if (in_array($zone, $zonen, true)) {", "            if (true) {", 'selbst'),
    ('s114_pz_sonos_vorschlag', "if ($v !== $zone && in_array($v, $zonen, true)) { $satz .=", "if (false) { $satz .=", 'selbst'),
    ('s114_zonen_ganze_datei', "    return array_map('strval', array_keys($d['sonoszonen']));", "    return array_map('strval', array_keys($d));", 'selbst'),
    ('s114_pz_sonox_fragt_zu', "        if (!$offen) {\n            return array(-2, $e(ansage_t('T_SONOX_ZU', $k)));", "        if (false) {\n            return array(-2, $e(ansage_t('T_SONOX_ZU', $k)));", 'selbst'),
    ('s114_pz_sonox_fehlt', "        if (ansage_plugin_da('sonox', ansage_k_home($k)) === false) {", "        if (false) {", 'selbst'),
    ('s114_pz_sonox_gross', "                if (ansage_klein($rn) === $kl) {", "                if ($rn === $raum) {", 'selbst'),
    ('s114_klein_ohne_umlaut', "    $s = strtr($s, array(\"\\xC3\\x84\" => \"\\xC3\\xA4\", \"\\xC3\\x96\" => \"\\xC3\\xB6\", \"\\xC3\\x9C\" => \"\\xC3\\xBC\"));\n    return strtr($s, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz');", "    return strtr($s, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz');", 'selbst'),
    ('s114_klein_mb', "    if (function_exists('mb_strtolower')) { return mb_strtolower($s, 'UTF-8'); }", "    if (function_exists('mb_strtolower')) { return strtolower($s); }", 'selbst_mb'),
    ('s114_form_nur_geschickte', "    if (isset($post[$n['sonox_sprache']])) {", "    if (true) {", 'selbst'),
    ('s114_form_ohne_raum', "    if ($neu['mode'] === 'sonox' && $neu['sonox_raum'] === '' && !in_array($n['sonox_raum'], $bean, true)) {", "    if (false) {", 'selbst'),
    ('s114_html_immer', "    $mit_sonox = in_array('sonox', $modi, true);", "    $mit_sonox = true;", 'selbst'),
    ('s114_html_laut_leer', " || $id === 'sonox_laut') && (int) $wert < 0) { $wert = ''; }", ") && (int) $wert < 0) { $wert = ''; }", 'selbst'),
    ('s114_x3_sprache', "            case 'sonox_sprache':\n", "            case 'sonox_sprache_x':\n", 'selbst'),
    # 1.2.0 (27.10.2026, Bau sm120): mehrere Ausgabeziele - die zehn Fehler aus probe_mutation120.txt des Entwurfs
    # (m1..m10) und vier weitere (Hoechstzahl, Spaetliste, Testknopf-Nummer, Formular ohne Opt-in).
    ('s120_mindestens_eins', "    if ($ok > 0) {", "    if ($ok === $n) {", 'selbst'),
    ('s120_doppel_ziel1', "        if (isset($gesehen[$s])) {\n            $liste[] = array('nr' => $nr,", "        if (false) {\n            $liste[] = array('nr' => $nr,", 'selbst'),
    ('s120_doppel_wertpruefung', "        if (isset($gesehen[$s])) { $grund = 'UNTER|ziel'", "        if (false) { $grund = 'UNTER|ziel'", 'selbst'),
    ('s120_doppel_formular', "        if (isset($gesehen[$s])) { $melden('M_ZIEL_DOPPELT|'", "        if (false) { $melden('M_ZIEL_DOPPELT|'", 'selbst'),
    ('s120_weiche_sprechen', "    if (array_key_exists('ziele', $tts) && $tts['ziele'] !== array()) {\n        return ansage_sprechen_ziele(",
     "    if (false) {\n        return ansage_sprechen_ziele(", 'selbst'),
    ('s120_sprache_bei_ng', "    } elseif ($aus['sprache'] !== '') {", "    } elseif (false) {", 'selbst'),
    ('s120_wiedergabe_reihenfolge', "        if ($pos < count($antworten)) { return $antworten[$pos++]; }",
     "        if ($pos < count($antworten)) { return $antworten[0]; }", 'selbst'),
    ('s120_ziel1_aus', "    if ($an && isset($neu['mode']) && $neu['mode'] === 'aus' && empty($opt['aus_gewinnt'])) { $melden('M_ZIEL1_AUS', 'mode'); }",
     "    if ($an && isset($neu['mode']) && $neu['mode'] === 'aus') {  }", 'selbst'),
    ('s120_kurz_ohne_ziele', "    if (isset($r['ziele'])) { $s .= ' ' . ansage_ziele_kurz($r); }      // seit 1.2.0\n", "", 'selbst'),
    ('s120_restzeit', "            if ($rest < 1) {", "            if ($rest < 100) {", 'selbst'),
    ('s120_token_im_html', "            $o[] = '<div id=\"ansage_' . $art . '_zugang\">';",
     "            $o[] = '<div id=\"ansage_' . $art . '_zugang\">' . $tts[$art . '_token'];", 'selbst'),
    ('s120_cli_ziele', "        $z .= ';ZIELE=' . $ok . '/' . count($r['ziele']);", "        ", 'selbst'),
    ('s120_ziele_zahl', "    if (count($liste) > ANSAGE_ZIELE_MAX - 1) {", "    if (count($liste) > ANSAGE_ZIELE_MAX + 4) {", 'selbst'),
    ('s120_spaetliste', "        $neu['ziele'] = $jetzt['ziele'];\n        $behalten[] = 'tts.ziele';", "        $behalten[] = 'tts.ziele';", 'selbst'),
    ('s120_test_ziel_grenze', "    return $n <= ANSAGE_ZIELE_MAX ? $n : 0;", "    return $n;", 'selbst'),
    ('s120_knopf_klasse_ungeprueft', "preg_match('/^[a-z][a-z0-9 _-]{0,60}\\z/', $h['klasse'])", "true", 'selbst'),
    ('s120_knopf_ohne_data_role', "<button data-role=\"none\" type=\"submit\" class=\"' . $e($kl) . '\"", "<button type=\"submit\" class=\"' . $e($kl) . '\"", 'selbst'),
    ('s120_form_ohne_optin',"    if (!empty($opt['ziele']) && isset($post[$nz['ziel_art']])) {", "    if (isset($post[$nz['ziel_art']])) {", 'selbst'),
    # 1.2.0, Nachbesserung 27.10.2026: Sprache bei Echo/Google/Sonos4Lox verwerfen und nennen, Feld gesperrt, Kuerzel genannt
    ('s120n_verwerfen_aus', "in_array($art, $arten, true) && !ansage_ziel_hat_sprache($art)) {", "in_array($art, $arten, true) && false) {", 'selbst'),
    ('s120n_nicht_verworfen', "            $sp = '';\n        }\n        if ($sp === null", "        }\n        if ($sp === null", 'selbst'),
    ('s120n_kein_hinweis', "            if (is_callable($hinweis)) { call_user_func($hinweis, $nr, $art); }\n", "", 'selbst'),
    ('s120n_hinweis_text', "'text' => sprintf(ansage_t('K_ZIEL_SPRACHE_GERAET', $k), $nr, ansage_t('O_' . strtoupper($art), $k))", "'text' => ''", 'selbst'),
    ('s120n_hat_sprache_sonox', "    return ansage_ziel_ist_zonenart($art) || $art === 'sonox';", "    return ansage_ziel_ist_zonenart($art);", 'selbst'),
    ('s120n_html_nicht_gesperrt', "        if (in_array($za, $arten, true) && !ansage_ziel_hat_sprache($za)) {", "        if (false) {", 'selbst'),
    ('s120n_wert_im_gesperrten', "'\" value=\"\" disabled placeholder=\"'", "'\" value=\"' . $e((string) $z['sprache']) . '\" disabled placeholder=\"'", 'selbst'),
    ('s120n_platzhalter_sonox', "$ph = ($za === 'sonox') ?", "$ph = false ?", 'selbst'),
    ('s120n_hilfesatz', "    $o[] = '    <div class=\"sm-hilfe\">' . $e($t('ZIEL_SPRACHE_HINWEIS')) . '</div>';\n", "", 'selbst'),
    ('s120n_ziel1_hinweis', "' maxlength=\"2\" placeholder=\"de\"', 'SPRACHE_HINWEIS'", "' maxlength=\"2\"', ''", 'selbst'),
    # --- echter Transport (Probe) ---
    ('curl_folgt', "CURLOPT_FOLLOWLOCATION => false,", "CURLOPT_FOLLOWLOCATION => true,", 'probe:85c'),
    ('datenstrom_folgt', "'follow_location' => 0,\n        'max_redirects' => 1,", "'follow_location' => 1,\n        'max_redirects' => 5,", 'probe:85'),
    # 1.2.0: die curl-Optionen stehen in ansage_curl_optionen() (eine Ebene weniger eingerueckt)
    ('curl_proxy', "        CURLOPT_PROXY => '',\n        CURLOPT_NOPROXY => '*',\n", "", 'probe:85cp'),
    ('curl_zeitgrenze', "CURLOPT_TIMEOUT => $anf['tmo'],", "CURLOPT_TIMEOUT => 3 * $anf['tmo'],", 'probe:85c'),
    ('datenstrom_zeitgrenze', "        'timeout' => $anf['tmo'],\n        'follow_location' => 0,",
     "        'timeout' => 3 * $anf['tmo'],\n        'follow_location' => 0,", 'probe:85'),
    ('datenstrom_status', "$code = (int) $m[1]; $laenge = -1; $ort = ''; }", "$code = 200; $laenge = -1; $ort = ''; }", 'probe:85'),
    ('datenstrom_stockt', "if ($zeit || microtime(true) - $t0 > $anf['tmo'] + 0.5) {", "if (false) {", 'probe:74'),
    ('kein_endpunkt', "if (isset($ansage_einstieg[0]) && realpath($ansage_einstieg[0]) === realpath(__FILE__)) {", "if (false) {", 'probe:85'),
    ('doppelt_laden', "if (!defined('ANSAGE_FASSUNG')) {", "if (true) {", 'probe:85'),
    # 1.2.0: Anker auf den Einzelweg verengt (ansage_http_zerlegen() traegt dieselbe Bedingung, s120_zerlegen_laenge)
    ('datenstrom_laenge', "if ($laenge >= 0 && $laenge <= ANSAGE_RUMPF_MAX && strlen($rumpf) < $laenge) {\n        return array('code' => 0, 'rumpf' => '', 'errno' => -1, 'fehler' => 'Rumpf abgebrochen');",
     "if (false) {\n        return array('code' => 0, 'rumpf' => '', 'errno' => -1, 'fehler' => 'Rumpf abgebrochen');", 'probe:85'),
    ('s120_zerlegen_laenge', "if ($laenge >= 0 && $laenge <= ANSAGE_RUMPF_MAX && strlen($rumpf) < $laenge) {\n        return array('code' => 0, 'rumpf' => '', 'errno' => -1, 'fehler' => 'Rumpf abgebrochen', 'ort' => '');",
     "if (false) {\n        return array('code' => 0, 'rumpf' => '', 'errno' => -1, 'fehler' => 'Rumpf abgebrochen', 'ort' => '');", 'selbst'),
    # 1.2.1: $k['frist'] in jedem Weg
    ('s121_anfrage_ohne_frist', "$tmo = ansage_frist(max(1, (int) $tmo), $k);", "$tmo = max(1, (int) $tmo);", 'selbst'),
    ('s121_frist_hebt', "{ $tmo = min($tmo, (int) $k['frist']); }", "{ $tmo = max($tmo, (int) $k['frist']); }", 'selbst'),
    ('s121_frist_grenze', "if (isset($k['frist']) && (int) $k['frist'] >= 1) { $tmo = min(", "if (isset($k['frist'])) { $tmo = min(", 'selbst'),
    ('s121_sonos_kennung', "'|' . ansage_frist(ANSAGE_TMO_SONOS, $k);", "'|' . ANSAGE_TMO_SONOS;", 'selbst'),
    ('s121_sonox_kennung', "ansage_sonox_grund($a, $basis, ansage_frist(ANSAGE_TMO_SONOX, $k));", "ansage_sonox_grund($a, $basis, ANSAGE_TMO_SONOX);", 'selbst'),
    ('s121_ng_kennung', "'tmo' => ansage_frist($tmo, $k));", "'tmo' => (int) $tmo);", 'selbst'),
    # 1.3.0 (S0, 01.11.2026): wann gesprochen wird
    ('s130_nacht_grenze_von', "return $v < $b ? ($n >= $v && $n < $b) : ($n >= $v || $n < $b);", "return $v < $b ? ($n > $v && $n < $b) : ($n > $v || $n < $b);", 'selbst'),
    ('s130_nacht_grenze_bis', "return $v < $b ? ($n >= $v && $n < $b) : ($n >= $v || $n < $b);", "return $v < $b ? ($n >= $v && $n <= $b) : ($n >= $v || $n <= $b);", 'selbst'),
    ('s130_nacht_ohne_mitternacht', "return $v < $b ? ($n >= $v && $n < $b) : ($n >= $v || $n < $b);", "return $n >= $v && $n < $b;", 'selbst'),
    ('s130_nacht_haken', "if (empty($regeln['nachtruhe'])) { return false; }", "", 'selbst'),
    ('s130_dringend_nachts', "if (empty($e['dringend']) && ansage_nachtruhe($regeln, $jetzt)) { return 'NACHTRUHE'; }", "if (ansage_nachtruhe($regeln, $jetzt)) { return 'NACHTRUHE'; }", 'selbst'),
    ('s130_sperre_grenze', "if ($d >= 0 && $d < $min * 60) { return 'SPERRE'; }", "if ($d >= 0 && $d <= $min * 60) { return 'SPERRE'; }", 'selbst'),
    ('s130_sperre_uhr', "if ($d >= 0 && $d < $min * 60) { return 'SPERRE'; }", "if ($d < $min * 60) { return 'SPERRE'; }", 'selbst'),
    ('s130_nur_nach', "if (isset($e['nur_nach']) && empty($stand['g'][$e['nur_nach']])) { return 'NUR_NACH'; }", "", 'selbst'),
    ('s130_nur_nach_quittung', "if (isset($e['nur_nach'])) { unset($stand['g'][$e['nur_nach']]); }", "", 'selbst'),
    ('s130_schalter_wirkt', "if ($vorab[0] && ansage_schalter_lesen($k) === '1') {", "if (false) {", 'selbst'),
    ('s130_schalter_immer_fragen', "if ($vorab[0] && ansage_schalter_lesen($k) === '1') {", "if (ansage_schalter_lesen($k) === '1' && $vorab[0]) {", 'selbst'),
    ('s130_schalter_wert', "return ($w === '1' || $w === '0') ? $w : '';", "return $w;", 'selbst'),
    ('s130_kein_ziel', "if ($block === null) {\n        $aus['regel'] = 'KEIN_ZIEL';", "if (false) {\n        $aus['regel'] = 'KEIN_ZIEL';", 'selbst'),
    ('s130_aus_bleibt', "if ($modus === 'aus' || $modus === 'audioserver' || !in_array($modus, ansage_modi(), true)) {\n        $aus['regel'] = 'AUS';", "if ($modus === 'audioserver' || !in_array($modus, ansage_modi(), true)) {\n        $aus['regel'] = 'AUS';", 'selbst'),
    ('s130_kaputt_gilt_aus', "if ($p === null) { $p = array('mode' => 'aus'); }", "if ($p === null) { $p = ansage_werk_block(); }", 'selbst'),
    ('s130_stand_kaputt_spricht', "if ($erg === null) {\n        foreach ($gueltig as $e) { $aus['einzeln'][$e['schluessel']] = 'STAND'; }", "if (false) {\n        foreach ($gueltig as $e) { $aus['einzeln'][$e['schluessel']] = 'STAND'; }", 'selbst'),
    ('s130_token_in_ergebnis', "$aus = array('regel' => '', 'einzeln' => array(), 'offen' => array(), 'r' => null);", "$aus = array('regel' => '', 'einzeln' => array(), 'offen' => array(), 'r' => null, 'x' => ansage_tts_vor_ort($tts, $k));", 'selbst'),
    ('s130_vor_ort_aus', "if ($n['token'] !== '' && $n['ein'] !== false) { $tts[$s] = $n['token']; }", "", 'selbst'),
    ('s130_sprechen_aus', "if ($n['ein'] === false) { return 'SPRECHEN_AUS'; }", "", 'selbst'),
    ('s130_kein_geraet', "&& $n['standard'] === false) { return 'KEIN_GERAET'; }", "&& false) { return 'KEIN_GERAET'; }", 'selbst'),
    ('s130_ms_ohne_adresse', "return ($u === '' || $u === null) ? 'KEINE_ADRESSE' : '';", "return '';", 'selbst'),
    ('s130_ein_satz', "$aus['r'] = ansage_sprechen(implode(' ', $text), $block, $k, array('dringend' => $dringend));", "$aus['r'] = ansage_sprechen($text[0], $block, $k, array('dringend' => $dringend));", 'selbst'),
    ('s130_dringend_weiter', "$aus['r'] = ansage_sprechen(implode(' ', $text), $block, $k, array('dringend' => $dringend));", "$aus['r'] = ansage_sprechen(implode(' ', $text), $block, $k, array());", 'selbst'),
    ('s130_merken_erst', "$stand['z'][$s] = $jetzt;\n", "\n", 'selbst'),
    ('s130_werk_ohne_alexa', "array('art' => 'alexang', 'wo' => '', 'laut' => -1, 'sprache' => '', 'ein' => 1),\n", "\n", 'selbst'),
    ('s130_token_mangel', "if (empty($opt['token_vor_ort']) && $neu['mode'] === $gew && $tok === ''", "if ($neu['mode'] === $gew && $tok === ''", 'selbst'),
    ('s130_aus_gewinnt', "$neu['mode'] === 'aus' && empty($opt['aus_gewinnt'])) {", "$neu['mode'] === 'aus') {", 'selbst'),
    ('s130_aus_gewinnt_immer', "$neu['mode'] === 'aus' && empty($opt['aus_gewinnt'])) {", "false) {", 'selbst'),
    ('s130_formular_gleich', "if ($neu['von'] === $neu['bis'] && !in_array", "if (false && !in_array", 'selbst'),
    ('s130_formular_haken', "$neu['nachtruhe'] = !empty($post['ansage_ruhe_ein']) ? 1 : 0;", "", 'selbst'),
    ('s130_mqtt_laenge', "$mal *= 128;", "$mal *= 1;", 'selbst'),
    ('s130_mqtt_halb', "if ($n < $i + $len) { return null; }", "", 'selbst'),
    # 1.3.1: das Sprechtoken dauerhaft
    ('s131_vor_ort_sperre', "if ($n['token'] !== '' && $n['ein'] !== false) { $tts[$s] = $n['token']; }", "if ($n['token'] !== '') { $tts[$s] = $n['token']; }", 'selbst'),
    ('s131_von_hand', "if ($alt !== '' && empty($herkunft[$s])) { continue; }", "", 'selbst'),
    ('s131_sperre', "$n = ansage_nachbar($m, $k);\n        if ($n['ein'] === false) { continue; }", "$n = ansage_nachbar($m, $k);", 'selbst'),
    ('s131_immer_geaendert', "if ($n['token'] !== $alt) {", "if (true) {", 'selbst'),
    ('s131_kein_vermerk', "$herkunft[$s] = 'nachbar';", "", 'selbst'),
    ('s131_geloescht_bleibt', "} elseif ($n['ein'] === true && $alt !== '') {", "} elseif (false) {", 'selbst'),
    ('s131_unlesbar_leert', "} elseif ($n['ein'] === true && $alt !== '') {", "} elseif ($alt !== '') {", 'selbst'),
    ('s131_aus_liest', "if ($modus === 'aus' || $modus === 'audioserver') { return array($tts, $herkunft, array()); }", "", 'selbst'),
    ('s131_nur_aktive', "if ($z['block'] !== null && isset($felder[$z['art']])) { $aktiv[$z['art']] = true; }", "if ($z['block'] !== null && isset($felder[$z['art']])) { $aktiv[$z['art']] = true; }\n        $aktiv['alexang'] = true; $aktiv['cc4lox'] = true;", 'selbst'),
    ('s131_lauf_sperre', "if (!empty($herkunft[$s]) && ansage_nachbar($m, $k)['ein'] === false) { $tts[$s] = ''; }", "", 'selbst'),
    ('s131_lauf_hand', "if (!empty($herkunft[$s]) && ansage_nachbar($m, $k)['ein'] === false) { $tts[$s] = ''; }", "if (ansage_nachbar($m, $k)['ein'] === false) { $tts[$s] = ''; }", 'selbst'),
    ('s131_form_eingetippt', "if ($eingetippt || !empty($post[$n[$s . '_loeschen']])) { unset($herkunft[$s]); }", "if (!empty($post[$n[$s . '_loeschen']])) { unset($herkunft[$s]); }", 'selbst'),
    ('s131_form_loeschen', "if ($eingetippt || !empty($post[$n[$s . '_loeschen']])) { unset($herkunft[$s]); }", "if ($eingetippt) { unset($herkunft[$s]); }", 'selbst'),
    ('s131_form_leerzeichen', "&& trim($post[$n[$s]]) !== '';", "&& $post[$n[$s]] !== '';", 'selbst'),
    ('s131_reihenfolge', "if ($n['ein'] === false) { return 'SPRECHEN_AUS'; }\n        if (!isset($b[$art . '_token'])", "if (!isset($b[$art . '_token']) || !ansage_token_ok($b[$art . '_token'])) { return 'KEIN_TOKEN'; }\n        if ($n['ein'] === false) { return 'SPRECHEN_AUS'; }\n        if (!isset($b[$art . '_token'])", 'selbst'),
    # 1.3.2: das SDK und die Globalen der Linie
    ('s132_webport_laedt', "    if (function_exists('lbwebserverport')) {\n        ob_start();", "    $lib132 = dirname($pfad, 3) . '/libs/phplib/loxberry_system.php';\n    if (is_file($lib132)) { require_once $lib132; }\n    if (function_exists('lbwebserverport')) {\n        ob_start();", 'selbst'),
    ('s132_kein_zurueck', "if (array_key_exists($g, $alt)) { $GLOBALS[$g] = $alt[$g]; } else { unset($GLOBALS[$g]); }", "", 'selbst'),
    ('s132_fehlendes_bleibt', "if (array_key_exists($g, $alt)) { $GLOBALS[$g] = $alt[$g]; } else { unset($GLOBALS[$g]); }", "if (array_key_exists($g, $alt)) { $GLOBALS[$g] = $alt[$g]; }", 'selbst'),
    ('s132_ohne_cfg', "    return array('cfg', 'cfgwasread', 'miniservers',", "    return array('cfgwasread', 'miniservers',", 'selbst'),
    # 1.4.0 (03.11.2026): das Ziel Tafel
    ('s140_nie_gesetzt_aus', "'sperre_min' => 30, 'tafel' => 1, 'tafel_namen' => '', 'homepod' => 1, 'homepod_geraet' => '');", "'sperre_min' => 30, 'tafel' => 0, 'tafel_namen' => '', 'homepod' => 1, 'homepod_geraet' => '');", 'selbst'),
    ('s140_hp_nie_gesetzt', "'sperre_min' => 30, 'tafel' => 1, 'tafel_namen' => '', 'homepod' => 1, 'homepod_geraet' => '');", "'sperre_min' => 30, 'tafel' => 1, 'tafel_namen' => '', 'homepod' => 0, 'homepod_geraet' => '');", 'selbst'),
    ('s140_hp_ohne_plugin', "if ($da || $m === 'homepod4lox' || !ansage_homepod_da($k)) { return $tts; }", "if ($da || $m === 'homepod4lox') { return $tts; }", 'selbst'),
    ('s140_hp_doppelt', "if ($da || $m === 'homepod4lox' || !ansage_homepod_da($k)) { return $tts; }", "if ($m === 'homepod4lox' || !ansage_homepod_da($k)) { return $tts; }", 'selbst'),
    ('s140_hp_aus', "if (empty($r['homepod'])) { unset($liste[$i]); } else { $da = true; }", "$da = true;", 'selbst'),
    ('s140_hp_aus2', "if (empty($r['homepod'])) {\n        if (isset($tts['ziele']))", "if (false) {\n        if (isset($tts['ziele']))", 'selbst'),
    ('s140_hp_html', "if (ansage_homepod_da($k)) {", "if (true) {", 'selbst'),
    ('s140_hp_bereit', "if ($nur_bereit && ansage_ziel_eingerichtet(ansage_ziel_block($tts, $z), $k) !== '') { return $tts; }\n    $liste[] = $z;\n    $tts['ziele'] = $liste;\n    return $tts;\n}\n\n/** Die Tafel", "$liste[] = $z;\n    $tts['ziele'] = $liste;\n    return $tts;\n}\n\n/** Die Tafel", 'selbst'),
    ('s140_hp_token', "$tts['homepod_token'] = ($n['ein'] !== false) ? $n['token'] : '';", "", 'selbst'),
    ('s140_regel_aus_wirkt_nicht', "if (empty($r['tafel'])) {\n        if (isset($tts['ziele']))", "if (false) {\n        if (isset($tts['ziele']))", 'selbst'),
    ('s140_regel_aus_laesst_zeile', "if (empty($r['tafel'])) { unset($liste[$i]); } else { $da = true; }", "$da = true;", 'selbst'),
    ('s140_doppelt', "if ($da || $m === 'tafel') { return $tts; }", "if ($m === 'tafel') { return $tts; }", 'selbst'),
    ('s140_ziel1_doppelt', "if ($da || $m === 'tafel') { return $tts; }", "if ($da) { return $tts; }", 'selbst'),
    ('s140_linie_aus_spricht', "if ($m === 'aus' || $m === 'audioserver' || !in_array($m, ansage_modi(), true)) { return $tts; }", "if ($m === 'audioserver' || !in_array($m, ansage_modi(), true)) { return $tts; }", 'selbst'),
    ('s140_audioserver_zeile', "if ($m === 'aus' || $m === 'audioserver' || !in_array($m, ansage_modi(), true)) { return $tts; }", "if ($m === 'aus' || !in_array($m, ansage_modi(), true)) { return $tts; }", 'selbst'),
    ('s140_kaputte_liste', "if (array_key_exists('ziele', $tts) && !is_array($tts['ziele'])) { return $tts; }", "", 'selbst'),
    ('s140_nur_bereit', "if ($nur_bereit && ansage_ziel_eingerichtet(ansage_ziel_block($tts, $z), $k) !== '') { return $tts; }\n    $liste[] = $z;\n    $tts['ziele'] = $liste;\n    return $tts;\n}\n\n/* ---", "$liste[] = $z;\n    $tts['ziele'] = $liste;\n    return $tts;\n}\n\n/* ---", 'selbst'),
    ('s140_namen_nicht_aus_regeln', "$z = array('art' => 'tafel', 'wo' => $r['tafel_namen'],", "$z = array('art' => 'tafel', 'wo' => '',", 'selbst'),
    ('s140_regelweg_ohne_tafel', "$roh = ansage_tafel_einreihen(ansage_tts_vor_ort($tts, $k), $regeln, $k);", "$roh = ansage_tts_vor_ort($tts, $k);", 'selbst'),
    ('s140_lage_ohne_tafel', "ansage_ziele_bereit(ansage_tafel_einreihen(ansage_tts_vor_ort($tts, $k), $regeln, $k), $k);", "ansage_ziele_bereit(ansage_tts_vor_ort($tts, $k), $k);", 'selbst'),
    ('s140_grenze_zaehlt_tafel', "if (is_array($z) && isset($z['art']) && ($z['art'] === 'tafel' || $z['art'] === 'homepod4lox')) { $grenze++; }", "", 'selbst'),
    ('s140_grenze_offen', "count($roh) > $grenze) {", "false) {", 'selbst'),
    ('s140_fassung_egal', "if (version_compare($f, ANSAGE_TAFEL_MIN, '<')) { return 'ZU_ALT'; }", "", 'selbst'),
    ('s140_fassung_textvergleich', "if (version_compare($f, ANSAGE_TAFEL_MIN, '<')) { return 'ZU_ALT'; }", "if ($f < ANSAGE_TAFEL_MIN) { return 'ZU_ALT'; }", 'selbst'),
    ('s140_ohne_dashboard', "if ($f === '') { return 'PLUGIN_FEHLT'; }", "", 'selbst'),
    ('s140_dort_aus', "if (false === $n['ein']) { return 'SPRECHEN_AUS'; }\n    if (!ansage_token_ok($n['token'])) { return 'KEIN_TOKEN'; }", "if (!ansage_token_ok($n['token'])) { return 'KEIN_TOKEN'; }", 'selbst'),
    ('s140_kein_token', "if (false === $n['ein']) { return 'SPRECHEN_AUS'; }\n    if (!ansage_token_ok($n['token'])) { return 'KEIN_TOKEN'; }", "if (false === $n['ein']) { return 'SPRECHEN_AUS'; }", 'selbst'),
    ('s140_keine_tafel', "isset($b['tafel_namen']) ? $b['tafel_namen'] : '', $k) < 1) { return 'KEINE_TAFEL'; }", "isset($b['tafel_namen']) ? $b['tafel_namen'] : '', $k) < 0) { return 'KEINE_TAFEL'; }", 'selbst'),
    ('s140_still_grenze', "(int) $jetzt - (int) $e['ts'] <= ANSAGE_TAFEL_STILL_S) { $n++; }", "(int) $jetzt - (int) $e['ts'] < ANSAGE_TAFEL_STILL_S) { $n++; }", 'selbst'),
    ('s140_still_egal', "(int) $jetzt - (int) $e['ts'] <= ANSAGE_TAFEL_STILL_S) { $n++; }", "true) { $n++; }", 'selbst'),
    ('s140_name_egal', "if ($wahl !== null && !in_array((string) $name, $wahl, true)) { continue; }", "", 'selbst'),
    ('s140_unbenannt_bei_name', "if ($art === 'unbenannt' && $wahl !== null) { continue; }", "", 'selbst'),
    ('s140_nie_gesetzt_dort', "$aus['ein'] = !(array_key_exists('ansage_ein', $d) && (int) $d['ansage_ein'] === 0);", "$aus['ein'] = !empty($d['ansage_ein']);", 'selbst'),
    ('s140_dort_immer_an', "$aus['ein'] = !(array_key_exists('ansage_ein', $d) && (int) $d['ansage_ein'] === 0);", "$aus['ein'] = true;", 'selbst'),
    ('s140_token_ungeprueft', "if (isset($d['aktionstoken']) && ansage_token_ok($d['aktionstoken'])) { $aus['token'] = $d['aktionstoken']; }", "if (isset($d['aktionstoken'])) { $aus['token'] = $d['aktionstoken']; }", 'selbst'),
    ('s140_sprechen_dort_aus', "if ($n['ein'] === false) {\n            $r['stand'] = -1;\n            $r['kennung'] = 'TAFEL_AUS';", "if (false) {\n            $r['stand'] = -1;\n            $r['kennung'] = 'TAFEL_AUS';", 'selbst'),
    ('s140_sprechen_ohne_token', "if (!ansage_token_ok($n['token'])) {\n            $r['kennung'] = 'TAFEL_KEIN_TOKEN';", "if (false) {\n            $r['kennung'] = 'TAFEL_KEIN_TOKEN';", 'selbst'),
    ('s140_sprechen_namen', "if (!ansage_tafel_namen_ok($namen)) {\n            $r['kennung'] = 'EINSTELLUNG|TTS_TAFEL_NAMEN';", "if (false) {\n            $r['kennung'] = 'EINSTELLUNG|TTS_TAFEL_NAMEN';", 'selbst'),
    ('s140_dringend_weg', "if ($dringend) { $f['dringend'] = '1'; }\n        if (!empty($opt['signal']))", "if (!empty($opt['signal']))", 'selbst'),
    ('s140_signal_weg', "if (!empty($opt['signal'])) { $f['art'] = 'gong'; }", "", 'selbst'),
    ('s140_namen_weg', "if ($namen !== '') { $f['tafel'] = $namen; }", "", 'selbst'),
    ('s140_laut_weg', "if ($laut >= 1) { $f['laut'] = $laut; }\n        if ($dringend) { $f['dringend'] = '1'; }\n        if (!empty($opt['signal']))", "if ($dringend) { $f['dringend'] = '1'; }\n        if (!empty($opt['signal']))", 'selbst'),
    ('s140_falsche_adresse', "$modus === 'cc4lox' || $modus === 'sonos4lox' || $modus === 'tafel' || $modus === 'homepod4lox' ? $modus : 'alexang'", "$modus === 'cc4lox' || $modus === 'sonos4lox' ? $modus : 'alexang'", 'selbst'),
    ('s140_namen_muster', "if (!ansage_tafel_namen_ok($aus['wo'])) { $grund = 'TTS_ZIEL_WO'; return null; }", "", 'selbst'),
    ('s140_ziel_sprache', "if ($aus['sprache'] !== '') { $grund = 'TTS_ZIEL_SPRACHE'; return null; }\n    } elseif ($aus['art'] === 'sonox') {", "} elseif ($aus['art'] === 'sonox') {", 'selbst'),
    ('s140_block_namen', "$b['tafel_namen'] = $wo;\n", "\n", 'selbst'),
    ('s140_block_laut', "$b['tafel_laut'] = $l;\n", "\n", 'selbst'),
    ('s140_formular_ohne_merkmal', "if (!empty($post['ansage_tafel_da'])) {", "if (true) {", 'selbst'),
    ('s140_formular_haken', "$neu['tafel'] = !empty($post['ansage_tafel_ein']) ? 1 : 0;", "", 'selbst'),
    ('s140_formular_namen', "if (ansage_tafel_namen_ok($w)) {\n            $neu['tafel_namen'] = $w;", "if (true) {\n            $neu['tafel_namen'] = $w;", 'selbst'),
    ('s140_html_merkmal', "$o[] = '    <input data-role=\"none\" type=\"hidden\" name=\"ansage_tafel_da\" value=\"1\">';", "", 'selbst'),
    ('s140_html_haken', "(call_user_func($c, 'ansage_tafel_ein', !empty($r['tafel'])) ? ' checked' : '')", "' checked'", 'selbst'),
    ('s140_regel_wert', "if ($w !== 0 && $w !== 1 && $w !== '0' && $w !== '1') { $grund = 'M_R_BLOCK'; return null; }", "", 'selbst'),
    ('s140_online_0', "if ($s['online'] === 0) { $z[0] = -1;", "if (false) { $z[0] = -1;", 'selbst'),
    ('s140_online_liste', "if ($s['online'] === -1) { $z[0] = -1;", "if (false) { $z[0] = -1;", 'selbst'),
    ('s140_online_lesen', "{ $aus['online'] = (int) $on[1]; }", "{ }", 'selbst'),
    ('s140_nacht_hinweis', "(isset($h['nacht_hinweis']) && is_string($h['nacht_hinweis'])) ? $h['nacht_hinweis'] : $t('R_NACHT_HINWEIS')", "$t('R_NACHT_HINWEIS')", 'selbst'),
    ('s140_nacht_lage', "(isset($k['nacht_lage']) && is_string($k['nacht_lage'])) ? $k['nacht_lage'] : $t('T_R_NACHT')", "$t('T_R_NACHT')", 'selbst'),
    ('s140_pruefzeile_rot', "return array(-1, $e(sprintf(ansage_t('T_TAFEL_OFFEN', $k), ansage_t('T_R_G_' . $g, $k))));", "return array(0, $e(sprintf(ansage_t('T_TAFEL_OFFEN', $k), ansage_t('T_R_G_' . $g, $k))));", 'selbst'),
    # 1.4.1 (05.11.2026): Tafel und HomePod fuehren das Eingetippte
    ('s141_name_ohne_w', "$e((string) call_user_func($w, 'ansage_tafel_namen', $r['tafel_namen']))", "$e((string) $r['tafel_namen'])", 'selbst'),
    ('s141_geraet_ohne_w', "$e((string) call_user_func($w, 'ansage_homepod_geraet', $r['homepod_geraet']))", "$e((string) $r['homepod_geraet'])", 'selbst'),
    ('s141_tafel_ohne_c', "call_user_func($c, 'ansage_tafel_ein', !empty($r['tafel']))", "!empty($r['tafel'])", 'selbst'),
    ('s141_homepod_ohne_c', "call_user_func($c, 'ansage_homepod_ein', !empty($r['homepod']))", "!empty($r['homepod'])", 'selbst'),
    ('s141_name_roh', "$e((string) call_user_func($w, 'ansage_tafel_namen', $r['tafel_namen']))", "(string) call_user_func($w, 'ansage_tafel_namen', $r['tafel_namen'])", 'selbst'),
    ('s141_geraet_roh', "$e((string) call_user_func($w, 'ansage_homepod_geraet', $r['homepod_geraet']))", "(string) call_user_func($w, 'ansage_homepod_geraet', $r['homepod_geraet'])", 'selbst'),
]


def pruefen(datei, art):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
    if art in ('selbst', 'selbst_mb'):
        mb = ['-d', 'extension_dir=' + str(PHP.parent / 'ext'), '-d', 'extension=mbstring'] if art == 'selbst_mb' else []
        r = subprocess.run([str(PHP), '-n', '-d', 'error_reporting=-1'] + mb + [str(datei), '--selbsttest'],
                           capture_output=True, timeout=120)
        letzte = r.stdout.decode('utf-8', 'replace').strip().splitlines()[-1:] or ['(keine Ausgabe)']
        return r.returncode, letzte[0]
    laeufe = art.split(':', 1)[1]
    r = subprocess.run([sys.executable, str(PROBE), '--modul', str(datei), '--nur', laeufe],
                       capture_output=True, timeout=600, env=env)
    letzte = r.stdout.decode('utf-8', 'replace').strip().splitlines()[-1:] or ['(keine Ausgabe)']
    return r.returncode, letzte[0]


def main():
    global PHP
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--php' in sys.argv:
        PHP = Path(sys.argv[sys.argv.index('--php') + 1])
        args = [a for a in args if a != sys.argv[sys.argv.index('--php') + 1]]
    nur = None
    if '--nur' in sys.argv:
        nur = sys.argv[sys.argv.index('--nur') + 1].split(',')
        args = [a for a in args if a != sys.argv[sys.argv.index('--nur') + 1]]
    quelle = Path(args[0]).resolve() if args else HIER / 'gemeinsam' / 'sprachausgabe.php'
    roh = quelle.read_bytes()
    if b'\r\n' in roh:
        sys.exit('ABBRUCH: %s traegt CRLF - mehrzeilige Anker traefen 0-mal (erst auf LF bringen)' % quelle)
    text = roh.decode('utf-8')
    if TMP.exists():
        if not str(TMP).startswith('C:\\tmp\\sprachmodul_'):
            sys.exit('ABBRUCH: Pfad unerwartet')
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    liste = [m for m in MUTATIONEN if not nur or m[0] in nur]
    if not liste:
        sys.exit('ABBRUCH: keine Mutation ausgewaehlt (leere Menge)')
    print('Quelle: %s' % quelle)
    print('Probe:  %s' % PROBE)
    print('PHP:    %s (selbst, selbst_mb)' % PHP)
    # Grundlinie: die unveraenderte Datei muss jede benutzte Pruefung bestehen.
    grund = TMP / 'grundlinie.php'
    grund.write_bytes(text.encode('utf-8'))
    for art in sorted(set(m[3] for m in liste)):
        rc, z = pruefen(grund, art)
        print('Grundlinie %-12s rc=%d  %s' % (art, rc, z))
        if rc != 0:
            sys.exit('ABBRUCH: die unveraenderte Datei besteht %s nicht' % art)
    ueberlebt = 0
    anker = 0
    for name, alt, neu, art in liste:
        n = text.count(alt)
        if n != 1:
            print('%-30s ANKER %d-mal - nicht geprueft' % (name, n))
            anker += 1
            continue
        mut = TMP / ('m_' + name + '.php')
        mut.write_bytes(text.replace(alt, neu).encode('utf-8'))
        rc, z = pruefen(mut, art)
        if rc == 0:
            ueberlebt += 1
        print('%-30s %-12s %s  (%s)' % (name, art, 'erkannt' if rc != 0 else 'UEBERLEBT', z[:90]))
    shutil.rmtree(TMP)
    print('%d Mutationen, %d erkannt, %d ueberlebt, %d Anker nicht eindeutig' % (
        len(liste), len(liste) - ueberlebt - anker, ueberlebt, anker))
    return 1 if ueberlebt or anker else 0


if __name__ == '__main__':
    sys.exit(main())
