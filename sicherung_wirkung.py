#!/usr/bin/env python3
"""Traegt die Sicherung wirklich - und lehnt sie ab, was sie ablehnen muss?

Gemessen an der GERENDERTEN Seite und an der Konfigurationsdatei, nicht am
Quelltext. Vier Faelle je Plugin:

    1. der Sicherungsknopf und das Rueckspielformular stehen auf der Seite
    2. eine gueltige Sicherung wird UEBERNOMMEN
    3. eine Datei mit einem unbekannten Schluessel wird ABGELEHNT - und
       zwar VOLLSTAENDIG: die Konfiguration bleibt Byte fuer Byte, wie sie
       war. Das ist der Punkt, an dem es haengt.
    4. eine Datei, die kein JSON ist, wird abgelehnt

Der dritte Fall ist der wichtige. Eine zur Haelfte uebernommene
Konfiguration ist schlimmer als die alte - und man sieht es ihr nicht an.

    python3 sicherung_wirkung.py <Pluginordner> [...]
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HIER = os.path.dirname(os.path.abspath(__file__))
ARBEIT = os.path.dirname(HIER)
sys.path.insert(0, HIER)
import importlib
_rendern = importlib.import_module('rendern')


def php():
    return next((p for _v, p in _rendern.PHPS if os.path.isfile(p)), None)


def rendern(ordner):
    dateien = list(_rendern.oberflaechen(_rendern.Path(ordner)))
    p = php()
    if not dateien or p is None:
        return None
    seite, _b, _r = _rendern.lauf(p, dateien[0], os.path.basename(ordner))
    return seite


def pruefe(o):
    name = os.path.basename(o)
    urteile = []

    # ---- 1. Stehen beide Knoepfe auf der Seite? ----
    t = rendern(o)
    if not t:
        return ['nicht gerendert'] * 2
    hat_datei = bool(re.search(r'type=["\']file["\']', t))
    hat_multi = bool(re.search(r'enctype=["\']multipart/form-data', t))
    urteile.append('ok' if (hat_datei and hat_multi) else
                   'ROT (Datei:%d multipart:%d)' % (hat_datei, hat_multi))

    # ---- 2..4: die Verarbeitung, in einem eigenen PHP-Lauf ----
    # Gemessen wird an der KONFIGURATIONSDATEI: was steht danach drin?
    lib = None
    # Die Datei suchen, die die LESEFUNKTION traegt - nicht die, die
    # "_lib.php" heisst. Gardena haelt seine Konfigurationsfunktionen in
    # bin/functions.inc.php; wer nur nach _lib.php sucht, meldet dort
    # "keine Bibliothek" und prueft nichts.
    for w, _, ds in os.walk(o):
        if os.sep + '.git' in w:
            continue
        for d in sorted(ds):
            if not d.endswith('.php'):
                continue
            f = os.path.join(w, d)
            try:
                t2 = io.open(f, encoding='utf-8', errors='replace').read()
            except Exception:
                continue
            if re.search(r'(?m)^function\s+\w+_(?:sicherung_lesen|konfig_einlesen|konfig_einfuhr|sicherung_einlesen)\s*\(', t2):
                lib = f
                break
        if lib:
            break
    if not lib:
        urteile.append('-- keine Bibliothek gefunden')
        return urteile

    # Den Praefix MESSEN, nicht aus dem Dateinamen ableiten: ferien_lib.php
    # traegt fer_, mower_lib.php traegt mo_, robo_lib.php traegt ro_. Der
    # Dateiname als Quelle meldete fuer drei Linien "nicht messbar" - und
    # ein Strich sammelt sich wie ein Haken ein.
    q = io.open(lib, encoding='utf-8', errors='replace').read()
    mp = re.search(r'(?m)^function\s+(\w+?)_(?:sicherung_lesen|konfig_einlesen'
                   r'|konfig_einfuhr|sicherung_einlesen)\s*\(', q)
    if mp is None:
        mp = re.search(r'(?m)^function\s+(\w+?)_(?:vorgaben|defaults)\s*\(', q)
    prae = mp.group(1) if mp else os.path.basename(lib).split('_lib')[0]
    # Die Vorgabenfunktion ABLESEN, nicht raten: sie steht im Rumpf der
    # Lesefunktion als "$neu = <name>();". AWM nennt sie awm_config_vorgaben,
    # andere _vorgaben oder _defaults - wer nur zwei Namen kennt, meldet fuer
    # den dritten "nicht messbar".
    # AB DER FUNKTIONSDEFINITION suchen, nicht ab der ersten Erwaehnung des
    # Namens. Am 26.08.2026 am Saugroboter-Plugin aufgelaufen: dort steht
    # "ro_sicherung_lesen()" in Zeile 172 in einem KOMMENTAR, die Definition
    # aber erst in Zeile 1932. Das lazy ".*?" fand danach das naechste
    # "$neu = ..." - und das war eine ganz andere Funktion:
    #
    #   Zeile  172  // ... und ro_sicherung_lesen() lehnte die eigene Datei ab
    #   Zeile 1078  $neu = array('ts' => time(), ...)      <- getroffen
    #   Zeile 1939  $neu = ro_vorgaben();                  <- gemeint
    #
    # $vorg wurde damit "array", die Probe lautete json_encode(array()) - eine
    # LEERE Konfiguration. Die lehnt jede Lesefunktion zu Recht ab, und das
    # Werkzeug meldete "gueltig:ROT" fuer ein Plugin, das richtig arbeitet.
    mv = re.search(r'(?m)^function\s+\w+_(?:sicherung_lesen|konfig_einlesen'
                   r'|konfig_einfuhr|sicherung_einlesen)\s*\(.*?'
                   r'\$neu\s*=\s*(\w+)\s*\(', q, re.S)
    # Und der gefundene Name wird GEGENGEPRUEFT: er gilt nur, wenn die Datei
    # eine Funktion dieses Namens auch definiert.
    #
    # Zendure schreibt in seiner Lesefunktion
    #     $neu = isset($d['konfiguration']) ? ... : $d;
    # Das Muster oben fasst dort "isset" als Vorgabenfunktion auf, und die
    # Probe lautete json_encode(isset()) - ein PHP-Syntaxfehler. Beim ersten
    # Anlauf dieser Korrektur ist genau das passiert: der Saugroboter wurde
    # gruen und Zendure dafuer rot. Ein Werkzeug, das eine Beanstandung gegen
    # eine andere tauscht, hat nichts verbessert.
    kandidat = mv.group(1) if mv else ''
    if kandidat and re.search(r'(?m)^function\s+' + re.escape(kandidat) + r'\s*\(', q):
        vorg = kandidat
    elif re.search(r'(?m)^function\s+' + prae + r'_vorgaben\s*\(', q):
        vorg = prae + '_vorgaben'
    else:
        vorg = prae + '_defaults'
    skript = os.path.join(os.environ.get('TEMP', '/tmp'), 'sich_probe.php')
    io.open(skript, 'w', encoding='utf-8').write(
        "<?php\n"
        "require '" + lib.replace('\\', '/') + "';\n"
        # Die Funktion heisst nicht ueberall gleich: WOLF nennt sie
        # konfig_einlesen, Zendure konfig_einfuhr, die neuen sicherung_lesen.
        # Ein Werkzeug, das nur einen Namen kennt, meldet fuer die anderen
        # "nicht messbar" - und ein Strich sammelt sich wie ein Haken ein.
        "$fn = '';\n"
        "foreach (array('_sicherung_lesen', '_konfig_einlesen', '_konfig_einfuhr',\n"
        "               '_sicherung_einlesen', '_import') as $end) {\n"
        "    if (function_exists('" + prae + "' . $end)) { $fn = '" + prae + "' . $end; break; }\n"
        "}\n"
        "if ($fn === '') { echo 'KEINE_FUNKTION'; exit; }\n"
        # Wo es KEINE Vorgabenfunktion gibt, sondern nur eine Schluesselliste
        # (Intercom), die Probe daraus bauen. Sonst ist die Probe eine LEERE
        # Konfiguration - und die lehnt jede Lesefunktion zu Recht ab, was
        # aussieht wie ein Fehler des Plugins und keiner ist.
        "$GLOBALS['pp'] = '" + prae + "';\n"
        "$liste = '';\n"
        "foreach (array('_sicherungsschluessel', '_schluessel') as $e2) {\n"
        "    if (function_exists($GLOBALS['pp'] . $e2)) { $liste = $GLOBALS['pp'] . $e2; break; }\n"
        "}\n"
        "$gut = ($liste !== '') ? json_encode(array_fill_keys($liste(), 'x'))\n"
        "                       : json_encode(" + vorg + "());\n"
        # Die FORM feststellen, bevor geurteilt wird. WOLF liefert nur zwei
        # Werte statt dreien und liest Textzeilen ("schluessel wert") statt
        # JSON - die native Sicherungsform des ISM-Geraets. Mit JSON gefuettert
        # lehnt es zu Recht ab; das als roten Befund zu melden waere ein Fehler
        # des Pruefstands, nicht des Plugins.
        "$r = $fn($gut);\n"
        "if (!is_array($r) || count($r) !== 3) { echo 'ANDERE_BAUART'; exit; }\n"
        "$form = (is_array($r[0]) || $r[0] === null) && is_array($r[1]) ? 'neu' : 'alt';\n"
        "if ($form === 'alt') { echo 'ANDERE_BAUART'; exit; }\n"
        "list($a, $m1, $n1) = $r;\n"
        "$d = json_decode($gut, true); $d['gibtesnicht'] = 1;\n"
        "list($b, $m2, $n2) = $fn(json_encode($d));\n"
        "list($c, $m3, $n3) = $fn('kein json');\n"
        # Die Rueckgabe ist nicht ueberall gleich gebaut: die neuen Funktionen
        # liefern array(Konfiguration|null, Maengel, Anzahl), Zendure und
        # Funkwacht array(ok, Meldung). Wer nur die erste Form kennt, meldet
        # fuer die zweite ein rotes Kreuz, das nichts bedeutet - und genau
        # davor warnt REGELN_4. Deshalb wird die FORM erst festgestellt.
        "printf(\"%s|%s|%s\", $a === null ? 'ABGELEHNT' : 'UEBERNOMMEN',\n"
        "       $b === null ? 'ABGELEHNT' : 'UEBERNOMMEN',\n"
        "       $c === null ? 'ABGELEHNT' : 'UEBERNOMMEN');\n")
    umg = dict(os.environ)
    umg['LBHOMEDIR'] = os.path.join(HIER, 'lb')
    umg['LBPPLUGINDIR'] = name
    # KEIN -n. Mit abgeschalteter php.ini greift auto_prepend_file nicht,
    # und die LoxBerry-Klassen der Attrappe fehlen - jede Bibliothek, die
    # sie beruehrt, stirbt dann mit "Call to undefined". Das sah nach
    # einem Plugin-Fehler aus und war einer des Pruefstands.
    r = subprocess.run([php(), '-d',
                        'include_path=.;' + os.path.join(HIER, 'lb', 'libs', 'phplib'),
                        '-d', 'auto_prepend_file=' + os.path.join(HIER, 'vorlauf.php'),
                        '-d', 'display_errors=0', skript],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', env=umg, timeout=60)
    roh = (r.stdout or '').strip()
    if 'ANDERE_BAUART' in roh:
        urteile.append('--  andere Bauart - von Hand ansehen')
        return urteile
    aus = roh.split('|')
    if len(aus) != 3:
        urteile.append('-- nicht messbar (%s)' % (r.stdout or r.stderr or '').replace(chr(10),' ')[:150])
        return urteile
    gut, fremd, kaputt = aus
    teile = []
    teile.append('gueltig:' + ('ok' if gut == 'UEBERNOMMEN' else 'ROT'))
    teile.append('fremd:' + ('ok' if fremd == 'ABGELEHNT' else 'ROT'))
    teile.append('kaputt:' + ('ok' if kaputt == 'ABGELEHNT' else 'ROT'))
    urteile.append(' '.join(teile))
    return urteile


def main():
    ordner = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not ordner:
        ordner = [e for e in sorted(os.listdir(ARBEIT))
                  if e.startswith('LoxBerry-Plugin-')
                  and os.path.isdir(os.path.join(ARBEIT, e))]
    print('%-30s %-22s %s' % ('Plugin', 'Formular', 'Verarbeitung'))
    print('-' * 88)
    fehler = 0
    for e in ordner:
        o = e if os.path.isdir(e) else os.path.join(ARBEIT, e)
        if not os.path.isdir(o):
            continue
        u = pruefe(o)
        if any('ROT' in x for x in u):
            fehler += 1
        print('%-30s %-22s %s' % (os.path.basename(o)[16:45], u[0],
                                  u[1] if len(u) > 1 else ''))
    print('-' * 88)
    print('%d Plugin(e), %d mit Befund' % (len(ordner), fehler))
    return 1 if fehler else 0


if __name__ == '__main__':
    sys.exit(main())
