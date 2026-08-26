#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft, ob die Sprachdateien eines Plugins mit JEDEM INI-Zerlegermodus lesbar sind.

Aufruf:
    sprachdatei_lesbar.py <Plugin-Ordner>      eine Linie
    sprachdatei_lesbar.py <Verzeichnis>        alle LoxBerry-Plugin-* darin
    sprachdatei_lesbar.py                      alle im Arbeitsverzeichnis

WARUM ES DIESES WERKZEUG GIBT (19.08.2026, Intercom 2.1.13)
-----------------------------------------------------------
Vier unquotierte Werte mit Klammern, Fragezeichen und Anfuehrungszeichen
haben zwei Sprachdateien mit je 160 Schluesseln vollstaendig unlesbar
gemacht: parse_ini_file($p, true) - der VORGABEMODUS - gibt fuer die ganze
Datei false zurueck, nicht etwa nur fuer die betroffene Zeile. Steht in der
aufrufenden Fassung kein INI_SCANNER_RAW, ist $L leer und die Oberflaeche
hat keinen einzigen Text mehr, einschliesslich der Navigationsleiste.

Ob das durchschlaegt, haengt an einer Zeile in einer fremden Bibliothek. Die
Frage laesst sich vermeiden: eine Datei, die in ALLEN DREI Modi laedt, ist
unabhaengig davon in Ordnung.

Gemessen wird mit PHP selbst - eine Nachbildung des Zerlegers waere eine
zweite Wahrheit. Geprueft wird gegen die PHP-Fassungen, die auf diesem
Rechner liegen; gefunden werden sie wie in installationslage_pruefen.py.

Rein lesend. Rueckgabewert: 0 in Ordnung, 1 Befund, 2 nichts angesehen.
"""
import glob
import json
import os
import subprocess
import sys

PHP_KANDIDATEN = [
    r'C:\tmp\php-8.4.24-Win32-vs17-x64\php.exe',
    r'C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe',
    '/usr/bin/php', 'php',
]

PRUEFER = r'''<?php
$aus = array();
foreach (array_slice($argv, 1) as $datei) {
    $z = array('datei' => $datei);
    foreach (array('NORMAL' => INI_SCANNER_NORMAL,
                   'TYPED' => INI_SCANNER_TYPED,
                   'RAW' => INI_SCANNER_RAW) as $name => $modus) {
        $r = @parse_ini_file($datei, true, $modus);
        if ($r === false) {
            $z[$name] = -1;
        } else {
            $n = 0;
            foreach ($r as $paare) { $n += is_array($paare) ? count($paare) : 1; }
            $z[$name] = $n;
        }
    }
    /* DIE STILLE HAELFTE: ein Wert, den der Vorgabemodus zwar liest, aber
     * KUERZER liefert als der RAW-Modus. Das passiert bei einem geraden
     * Anfuehrungszeichen im Wert, wenn der Rest der Zeile zufaellig kein
     * reserviertes Zeichen enthaelt - dann gibt es keinen Fehler, sondern
     * einen Satz, der mitten im Wort aufhoert. Gemessen an Einspeisebremse
     * 0.9.9: 780 von 1448 Zeichen, ohne jede Meldung. */
    $z['kurz'] = array();
    $roh = @parse_ini_file($datei, true, INI_SCANNER_RAW);
    $vorgabe = @parse_ini_file($datei, true, INI_SCANNER_NORMAL);
    if (is_array($roh) && is_array($vorgabe)) {
        foreach ($roh as $sek => $paare) {
            if (!is_array($paare)) { continue; }
            foreach ($paare as $k => $v) {
                if (!is_string($v)) { continue; }
                $ist = isset($vorgabe[$sek][$k]) && is_string($vorgabe[$sek][$k])
                     ? $vorgabe[$sek][$k] : '';
                /* Verglichen wird gegen den RAW-Wert OHNE seine geraden
                 * Anfuehrungszeichen.
                 *
                 * Der Vorgabemodus entfernt sie naemlich, ohne den Wert zu
                 * kuerzen: aus class="sm-mono" wird class=sm-mono, zwei
                 * Zeichen weniger und derselbe Sinn. Wer nur die Laengen
                 * vergleicht, meldet das als Befund - beim ersten Lauf dieses
                 * Werkzeugs waren 14 von 14 Treffern genau das, also
                 * ausnahmslos Fehlalarme. Ein Befund ist erst, was auch nach
                 * dieser Bereinigung noch fehlt: dann ist der Wert wirklich
                 * abgeschnitten. */
                /* Zwei Umsetzungen, die der Vorgabemodus vornimmt und die
                 * KEINE Kuerzung sind:
                 *   "  faellt weg      class="x" wird class=x
                 *   \ wird zu \       \n im Text wird zu 

                 * Beim zweiten Anlauf dieses Werkzeugs waren zwei von vier
                 * Treffern im Bestand genau das - ein Wert, der um ein
                 * einziges Zeichen kuerzer ist, weil der Autor \n schreiben
                 * musste, damit 
 ankommt. */
                $sollte = str_replace(array('"', '\\\\'), array('', '\\'), $v);
                if (strlen($ist) < strlen($sollte)) {
                    $z['kurz'][] = $sek . '.' . $k . ': ' . strlen($ist)
                                 . ' statt ' . strlen($sollte) . ' Zeichen';
                }
            }
        }
    }

    /* Die Zeilen, die der Vorgabemodus einzeln nicht annimmt - damit der
     * Befund eine Fundstelle hat und nicht nur ein Urteil. */
    $z['zeilen'] = array();
    $inhalt = @file($datei, FILE_IGNORE_NEW_LINES);
    if (is_array($inhalt)) {
        foreach ($inhalt as $i => $zeile) {
            $t = trim($zeile);
            if ($t === '' || $t[0] === ';' || $t[0] === '[' || $t[0] === '#') { continue; }
            if (@parse_ini_string($zeile, false, INI_SCANNER_NORMAL) === false) {
                $z['zeilen'][] = ($i + 1) . ': ' . substr($t, 0, 60);
            }
        }
    }
    $aus[] = $z;
}
echo json_encode($aus);
'''


def php_finden():
    # Je Fassung EINER. 'php' aus dem Pfad ist haeufig dieselbe Datei wie ein
    # Kandidat davor; zweimal dieselbe Fassung zu messen verdoppelt nur die
    # Zeilen und suggeriert eine Abdeckung, die es nicht gibt.
    gefunden = []
    gesehen = set()
    for k in PHP_KANDIDATEN:
        try:
            r = subprocess.run([k, '-n', '-r', 'echo PHP_VERSION;'],
                               capture_output=True, text=True, timeout=20)
        except Exception:
            continue
        v = r.stdout.strip()
        if r.returncode == 0 and v and v not in gesehen:
            gesehen.add(v)
            gefunden.append((v, k))
    return gefunden


def sprachdateien(ordner):
    treffer = []
    for muster in ('templates/lang/*.ini', 'templates/*.ini'):
        treffer += sorted(glob.glob(os.path.join(ordner, muster)))
    return [t for t in treffer if os.path.isfile(t)]


def plugin_wurzel(p):
    if os.path.isfile(os.path.join(p, 'plugin.cfg')):
        return p
    unter = [os.path.join(p, d) for d in sorted(os.listdir(p))
             if os.path.isdir(os.path.join(p, d))
             and os.path.isfile(os.path.join(p, d, 'plugin.cfg'))]
    return unter[0] if len(unter) == 1 else p


def main():
    ziele = sys.argv[1:]
    if not ziele:
        ziele = sorted(glob.glob('LoxBerry-Plugin-*'))
    elif len(ziele) == 1 and os.path.isdir(ziele[0]) \
            and not os.path.isfile(os.path.join(ziele[0], 'plugin.cfg')) \
            and glob.glob(os.path.join(ziele[0], 'LoxBerry-Plugin-*')):
        ziele = sorted(glob.glob(os.path.join(ziele[0], 'LoxBerry-Plugin-*')))
    ziele = [z for z in ziele if os.path.isdir(z)]

    phps = php_finden()
    if not phps:
        print('ACHTUNG: kein PHP gefunden - es wurde NICHTS geprueft.')
        return 2
    print('Interpreter: ' + ', '.join(v for v, _ in phps))

    hier = os.path.dirname(os.path.abspath(__file__))
    pruefer = os.path.join(hier, '.sprachdatei_lesbar_probe.php')
    with open(pruefer, 'w', encoding='utf-8') as f:
        f.write(PRUEFER)

    dateien_gesamt = 0
    befunde = 0
    linien = 0
    try:
        for ziel in ziele:
            wurzel = plugin_wurzel(ziel)
            dateien = sprachdateien(wurzel)
            if not dateien:
                continue
            linien += 1
            name = os.path.basename(os.path.abspath(ziel))
            zeilen_aus = []
            schlecht = 0
            for version, php in phps:
                r = subprocess.run([php, '-n', pruefer] + dateien,
                                   capture_output=True, text=True, timeout=120)
                try:
                    daten = json.loads(r.stdout)
                except Exception:
                    zeilen_aus.append('   PHP %s: keine auswertbare Antwort (%s)'
                                      % (version, (r.stdout + r.stderr)[:80]))
                    schlecht += 1
                    continue
                for z in daten:
                    dateien_gesamt += 1
                    if z['NORMAL'] == -1 or z['TYPED'] == -1:
                        schlecht += 1
                        zeilen_aus.append(
                            '   %-22s PHP %-7s NORMAL=%s TYPED=%s RAW=%s'
                            % (os.path.basename(z['datei']), version,
                               'FALSE' if z['NORMAL'] == -1 else z['NORMAL'],
                               'FALSE' if z['TYPED'] == -1 else z['TYPED'],
                               'FALSE' if z['RAW'] == -1 else z['RAW']))
                        for zeile in z['zeilen'][:5]:
                            zeilen_aus.append('      Zeile ' + zeile)
                        if len(z['zeilen']) > 5:
                            zeilen_aus.append('      ... und %d weitere'
                                              % (len(z['zeilen']) - 5))
                    elif z.get('kurz'):
                        # Der stille Fall: gelesen, aber verkuerzt.
                        schlecht += 1
                        zeilen_aus.append(
                            '   %-22s PHP %-7s liest, liefert aber %d Wert(e) VERKUERZT'
                            % (os.path.basename(z['datei']), version, len(z['kurz'])))
                        for k in z['kurz'][:5]:
                            zeilen_aus.append('      ' + k)
                        if len(z['kurz']) > 5:
                            zeilen_aus.append('      ... und %d weitere'
                                              % (len(z['kurz']) - 5))
            if schlecht:
                befunde += 1
                print('[FEHL] %-42s %d Datei(en), %d Befund(e)'
                      % (name, len(dateien), schlecht))
                for z in zeilen_aus:
                    print(z)
            else:
                print('[OK]   %-42s %d Datei(en) in allen drei Modi lesbar'
                      % (name, len(dateien)))
    finally:
        try:
            os.unlink(pruefer)
        except Exception:
            pass

    print()
    if linien == 0:
        print('ACHTUNG: es wurde keine einzige Sprachdatei angesehen.')
        return 2
    print('%d Linie(n) geprueft, %d Dateilaeufe, %d Linie(n) mit Befund.'
          % (linien, dateien_gesamt, befunde))
    print('Zwei Wirkungen derselben Ursache, beide gemessen:')
    print('  laut  - ein unquotierter Wert mit ( ) ? oder ein gerades')
    print('          Anfuehrungszeichen bringt den Vorgabemodus zu Fall, und')
    print('          zwar die GANZE Datei, nicht die Zeile.')
    print('  still - derselbe Wert wird gelesen und dabei am ersten inneren')
    print('          Anfuehrungszeichen ABGESCHNITTEN. Kein Fehler, keine')
    print('          Warnung, nur ein Satz, der mitten im Wort aufhoert.')
    print('Abhilfe fuer beides: Attribute in der Auszeichnung einfach quotieren')
    print("(class='sm-mono'), und im Text keine geraden Anfuehrungszeichen.")
    return 1 if befunde else 0


if __name__ == '__main__':
    sys.exit(main())
