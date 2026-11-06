<?php
/**
 * php74_pruefen.php - sucht Sprachmittel, die PHP 7.4 NICHT kennt.
 *
 * WOFUER: wenn kein PHP 7.4 zur Hand ist, beantwortet dieses Werkzeug die
 * Frage, an der ein 7.4 scheitern WUERDE: benutzt der Quelltext etwas, das
 * erst ab PHP 8.0 geparst werden kann?
 *
 * WAS ES NICHT IST: kein Ersatz fuer "php7.4 -l". Es findet keine Fehler,
 * die auch 8.x meldet (dafuer ist php -l da), und es kennt nicht jedes
 * 8er-Sprachmittel - benannte Argumente, Erstklass-Rueckrufe (...) und
 * neue-in-Vorgabewerten fehlen. Ein Fund ist verlaesslich, ein Nicht-Fund
 * ist ein starkes Indiz, kein Beweis.
 *
 * GEEICHT in beide Richtungen (13.09.2026): eine Datei mit acht 8er-Mitteln
 * ergibt acht Funde, eine bewusst 7.4-taugliche Datei ergibt keinen. Der
 * Dreiweg-Ausdruck "? x : false" ist ausdruecklich KEIN Rueckgabetyp - das
 * war beim ersten Wurf ein Fehlalarm in bl_lib.php Zeile 292.
 *
 * AUFRUF:
 *   php php74_pruefen.php <datei.php> [weitere.php ...]
 *   php php74_pruefen.php $(find ORDNER -name '*.php')
 *
 * Findet: match, ?->, #[Attribut], enum, readonly, Rueckgabetypen
 * mixed/never/false/true, Konstruktor-Eigenschaftsfoerderung,
 * Vereinigungstypen a|b.
 */
$dateien = array_slice($argv, 1);
$treffer = [];
foreach ($dateien as $datei) {
    $q = file_get_contents($datei);
    $tk = token_get_all($q);
    $n  = count($tk);
    for ($i = 0; $i < $n; $i++) {
        $t = $tk[$i];
        if (!is_array($t)) {
            // Attribut #[...] taucht als T_ATTRIBUTE auf, nicht als Zeichen
            continue;
        }
        $name = token_name($t[0]);
        $text = $t[1];
        $z    = $t[2];
        $melde = function ($was, $ab) use (&$treffer, $datei, $z, $text) {
            $treffer[] = [$datei, $z, $was, $ab, trim(substr($text, 0, 40))];
        };
        switch ($name) {
            case 'T_MATCH':            $melde('match-Ausdruck', '8.0'); break;
            case 'T_NULLSAFE_OBJECT_OPERATOR': $melde('Nullsafe ?->', '8.0'); break;
            case 'T_ATTRIBUTE':        $melde('Attribut #[...]', '8.0'); break;
            case 'T_ENUM':             $melde('enum', '8.1'); break;
            case 'T_READONLY':         $melde('readonly', '8.1'); break;
            case 'T_NAME_QUALIFIED':
            case 'T_NAME_FULLY_QUALIFIED':
            case 'T_NAME_RELATIVE':    break; // nur Namensraeume, 7.4 kennt sie anders, aber gleichwertig
        }
        // Typen, die es vor 8.0 nicht gab, nur wenn sie als Typangabe stehen
        if ($name === 'T_STRING' && in_array(strtolower($text), ['mixed','never','false','true','null'], true)) {
            // Vorzeichen: steht ein ':' oder '|' unmittelbar davor?
            for ($j = $i - 1; $j >= 0 && is_array($tk[$j]) && $tk[$j][0] === T_WHITESPACE; $j--);
            $vor = $j >= 0 ? (is_array($tk[$j]) ? $tk[$j][1] : $tk[$j]) : '';
            // Ein Rueckgabetyp steht hinter ':' und DAS steht hinter ')'.
            // Ohne diese Zusatzbedingung faengt man jeden Dreiweg-Ausdruck
            // "... ? x : false" mit - gemessen an bl_lib.php Zeile 292.
            $vor2 = '';
            if ($vor === ':') {
                for ($m = $j - 1; $m >= 0 && is_array($tk[$m]) && $tk[$m][0] === T_WHITESPACE; $m--);
                $vor2 = $m >= 0 ? (is_array($tk[$m]) ? $tk[$m][1] : $tk[$m]) : '';
            }
            if ($vor === ':' && $vor2 === ')' && in_array(strtolower($text), ['mixed','never','false','true'], true)) {
                $melde('Rueckgabetyp ' . strtolower($text), strtolower($text) === 'mixed' ? '8.0' : '8.1');
            }
        }
    }

    // Konstruktor-Eigenschaftsfoerderung: __construct(public int $x)
    // und Vereinigungstypen (int|string) - beides erst ab 8.0.
    for ($i = 0; $i < $n; $i++) {
        if (is_array($tk[$i]) && $tk[$i][0] === T_FUNCTION) {
            for ($j = $i + 1; $j < $n && $j < $i + 6; $j++) {
                if (is_array($tk[$j]) && strtolower($tk[$j][1] ?? '') === '__construct') {
                    $tiefe = 0;
                    for ($k = $j; $k < $n; $k++) {
                        $z = is_array($tk[$k]) ? $tk[$k][1] : $tk[$k];
                        if ($z === '(') $tiefe++;
                        elseif ($z === ')') { if (--$tiefe === 0) break; }
                        elseif ($tiefe === 1 && is_array($tk[$k])
                                && in_array($tk[$k][0], [T_PUBLIC, T_PROTECTED, T_PRIVATE], true)) {
                            $treffer[] = [$datei, $tk[$k][2], 'Konstruktor-Eigenschaftsfoerderung', '8.0', $tk[$k][1]];
                            break;
                        }
                    }
                    break;
                }
            }
        }
        // Vereinigungstyp: Bezeichner '|' Bezeichner in einer Signatur
        if ($tk[$i] === '|' && $i > 0 && $i + 1 < $n) {
            $v = $tk[$i-1]; $h = $tk[$i+1];
            $vs = is_array($v) ? $v[0] : null; $hs = is_array($h) ? $h[0] : null;
            if (in_array($vs, [T_STRING, T_ARRAY, T_CALLABLE], true)
                && in_array($hs, [T_STRING, T_ARRAY, T_CALLABLE, T_WHITESPACE], true)) {
                // nur zaehlen, wenn davor ein ':' oder eine Typposition steht
                for ($j = $i - 2; $j >= 0 && is_array($tk[$j]) && $tk[$j][0] === T_WHITESPACE; $j--);
                $vor = $j >= 0 ? (is_array($tk[$j]) ? $tk[$j][1] : $tk[$j]) : '';
                if ($vor === ':' || $vor === '(' || $vor === ',') {
                    $treffer[] = [$datei, is_array($v) ? $v[2] : 0, 'Vereinigungstyp a|b', '8.0', ''];
                }
            }
        }
    }
}
if (!$treffer) {
    printf("%d Datei(en) geprueft - kein Sprachmittel gefunden, das PHP 7.4 nicht kennt.\n", count($dateien));
} else {
    printf("%d Datei(en) geprueft - %d Fundstelle(n):\n", count($dateien), count($treffer));
    foreach ($treffer as $t) {
        printf("  %s Zeile %d: %s (erst ab PHP %s)  %s\n", $t[0], $t[1], $t[2], $t[3], $t[4]);
    }
}
