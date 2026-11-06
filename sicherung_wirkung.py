#!/usr/bin/env python3
"""Traegt die Sicherung wirklich - und lehnt sie ab, was sie ablehnen muss?

Gemessen an der GERENDERTEN Seite und an der Konfigurationsdatei, nicht am
Quelltext. Fuenf Faelle je Plugin:

    1. der Sicherungsknopf und das Rueckspielformular stehen auf der Seite
    2. eine gueltige Sicherung wird UEBERNOMMEN
    3. eine Datei mit einem unbekannten Schluessel wird ABGELEHNT - und
       zwar VOLLSTAENDIG: die Konfiguration bleibt Byte fuer Byte, wie sie
       war. Das ist der Punkt, an dem es haengt.
    4. eine Datei, die kein JSON ist, wird abgelehnt
    5. eine gueltige Datei, der ein Schluessel FEHLT, wird abgelehnt
       oder wenigstens beanstandet - nicht still auf Werk gesetzt

Der fuenfte Fall kam am 07.09.2026 dazu. Er fehlte, und deshalb meldeten
31 Linien "gueltig:ok fremd:ok kaputt:ok", waehrend sie eine halbe
Konfiguration stillschweigend mit Werkswerten auffuellten. Ein Pruefstand,
der eine Fehlerklasse nicht kennt, bescheinigt ihre Abwesenheit.

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
        # Die WERTE kommen aus der Vorgabenfunktion, wenn es eine gibt -
        # auch dann, wenn eine Schluesselliste die AUSWAHL bestimmt.
        # 'x' fuer alles war die Ursache des Fehlalarms an Intercom 2.2.8
        # (07.09.2026): 18 von 31 Werten wurden zu Recht beanstandet, und
        # eine Linie, die richtig arbeitet, bekam gueltig:ROT.
        "$basis = array();\n"
        "foreach (array('_vorgaben', '_defaults') as $e3) {\n"
        "    if (function_exists($GLOBALS['pp'] . $e3)) {\n"
        "        $b = call_user_func($GLOBALS['pp'] . $e3);\n"
        "        if (is_array($b)) { $basis = $b; }\n"
        "        break;\n"
        "    }\n"
        "}\n"
        "if ($liste !== '') {\n"
        # Zwei Proben, und es gilt die bessere. Der Ersatzwert fuer
        # Schluessel ohne Vorgabe wird abgetastet, nicht angenommen:
        # Intercom fuehrt 'stationen' in der Liste, aber nicht in den
        # Vorgaben, und dort verlangt der Wertpruefer ein Feld.
        "    $bau = function ($ersatz) use ($liste, $basis) {\n"
        "        $g = array();\n"
        "        foreach ($liste() as $lk) {\n"
        "            $g[$lk] = array_key_exists($lk, $basis) ? $basis[$lk] : $ersatz;\n"
        "        }\n"
        "        return json_encode($g);\n"
        "    };\n"
        "    $pA = $bau(''); $pB = $bau(array());\n"
        "    $nA = $fn($pA); $nB = $fn($pB);\n"
        "    $cA = (is_array($nA) && isset($nA[1]) && is_array($nA[1])) ? count($nA[1]) : 99;\n"
        "    $cB = (is_array($nB) && isset($nB[1]) && is_array($nB[1])) ? count($nB[1]) : 99;\n"
        "    $gut = ($cB < $cA) ? $pB : $pA;\n"
        "} else {\n"
        "    $gut = json_encode(" + vorg + "());\n"
        "}\n"

        # Die FORM feststellen, bevor geurteilt wird. WOLF liefert nur zwei
        # Werte statt dreien und liest Textzeilen ("schluessel wert") statt
        # JSON - die native Sicherungsform des ISM-Geraets. Mit JSON gefuettert
        # lehnt es zu Recht ab; das als roten Befund zu melden waere ein Fehler
        # des Pruefstands, nicht des Plugins.
        # DREI ODER MEHR, nicht genau drei.
        #
        # Hier stand "count($r) !== 3". Das wies eine Linie ab, die einen
        # VIERTEN Wert zurueckgibt - Octopus 1.1.0 reicht die Zugangsdaten
        # gesondert heraus, weil sie in eine eigene Datei mit Rechten 0600
        # gehoeren und nicht in die Konfiguration. Das ist dieselbe Bauart
        # mit einem Anhang, keine andere; gemeldet wurde trotzdem
        # "andere Bauart - von Hand ansehen", und damit hat das Werkzeug
        # NICHT gemessen, statt etwas zu finden. Ein Werkzeug, das den
        # Pruefling stillschweigend ueberspringt, entlastet nicht.
        #
        # Die Untergrenze bleibt: die Zwei-Werte-Form (WOLF, Zendure,
        # Funkwacht) wird weiterhin erkannt und ausgenommen, denn fuer sie
        # bedeutet $r[0] etwas anderes.
        "$r = $fn($gut);\n"
        "if (!is_array($r) || count($r) < 3) { echo 'ANDERE_BAUART'; exit; }\n"
        "$form = (is_array($r[0]) || $r[0] === null) && is_array($r[1]) ? 'neu' : 'alt';\n"
        "if ($form === 'alt') { echo 'ANDERE_BAUART'; exit; }\n"
        "list($a, $m1, $n1) = $r;\n"
        "$d = json_decode($gut, true); $d['gibtesnicht'] = 1;\n"
        "list($b, $m2, $n2) = $fn(json_encode($d));\n"
        "list($c, $m3, $n3) = $fn('kein json');\n"
        # Der fuenfte Fall: EIN Schluessel fehlt. Nicht die Haelfte - einer.
        # Das ist zugleich der wahrscheinlichste Fall im Feld: eine Sicherung
        # aus einer aelteren Fassung des Plugins, die einen spaeter
        # hinzugekommenen Schluessel noch nicht kennt.
        #
        # Verglichen wird gegen die Maengelliste des GUELTIGEN Laufs, nicht
        # gegen die leere Liste: manche Linien melden auch bei einer
        # einwandfreien Datei einen Hinweis, und der ist kein Fund.
        "$dl = json_decode($gut, true);\n"
        "$schl = is_array($dl) ? array_keys($dl) : array();\n"
        "$vier = 'NICHTMESSBAR';\n"
        "if (count($schl) >= 2) {\n"
        "    unset($dl[$schl[0]]);\n"
        "    $rv = $fn(json_encode($dl));\n"
        "    if (is_array($rv) && count($rv) >= 3) {\n"
        "        $e = $rv[0]; $m4 = $rv[1];\n"
        "        $z1 = is_array($m1) ? count($m1) : 0;\n"
        "        $z4 = is_array($m4) ? count($m4) : 0;\n"
        "        $vier = ($e === null) ? 'ABGELEHNT'\n"
        "                              : (($z4 > $z1) ? 'GEMELDET' : 'STILL');\n"
        "    }\n"
        "}\n"
        # Die Rueckgabe ist nicht ueberall gleich gebaut: die neuen Funktionen
        # liefern array(Konfiguration|null, Maengel, Anzahl), Zendure und
        # Funkwacht array(ok, Meldung). Wer nur die erste Form kennt, meldet
        # fuer die zweite ein rotes Kreuz, das nichts bedeutet - und genau
        # davor warnt REGELN_4. Deshalb wird die FORM erst festgestellt.
        # Wurde die GUELTIGE Probe beanstandet, taugt die Probe nicht -
        # das ist keine Aussage ueber das Plugin. Die Zahl wird
        # mitgegeben, damit man sieht, wie weit es daneben lag.
        "$z1x = is_array($m1) ? count($m1) : 0;\n"
        "printf(\"%s|%s|%s|%s|%d\", $a === null ? 'ABGELEHNT' : 'UEBERNOMMEN',\n"
        "       $b === null ? 'ABGELEHNT' : 'UEBERNOMMEN',\n"
        "       $c === null ? 'ABGELEHNT' : 'UEBERNOMMEN', $vier, $z1x);\n")
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
    if len(aus) != 5:
        urteile.append('-- nicht messbar (%s)' % (r.stdout or r.stderr or '').replace(chr(10),' ')[:150])
        return urteile
    gut, fremd, kaputt, luecke, z1 = aus
    teile = []
    if gut != 'UEBERNOMMEN' and z1.isdigit() and int(z1) > 0:
        # Die Probe wurde beanstandet, nicht das Plugin ertappt. Intercom
        # 2.2.8 prueft jeden Wert und arbeitet fail closed; mit einer
        # unplausiblen Probe lehnt es zu Recht ab.
        teile.append('gueltig:probe-untauglich (%s)' % z1)
    else:
        teile.append('gueltig:' + ('ok' if gut == 'UEBERNOMMEN' else 'ROT'))
    teile.append('fremd:' + ('ok' if fremd == 'ABGELEHNT' else 'ROT'))
    teile.append('kaputt:' + ('ok' if kaputt == 'ABGELEHNT' else 'ROT'))
    # Der fuenfte Fall. NICHTMESSBAR ist KEIN Haken: es heisst, die Probe
    # hatte weniger als zwei Schluessel, es wurde also nichts angesehen.
    #
    # ZWEI BAUARTEN. Wer als Grundlage die WERKSVORGABE ansetzt, muss eine
    # unvollstaendige Datei beanstanden - sonst faellt jeder fehlende Wert
    # still auf Werk. Wer den LAUFENDEN Stand ansetzt (Midea2Lox mit
    # mi_config_read(), Pumpenwacht mit pw_config()), hat denselben Schaden
    # schon abgewendet: dort bleibt ein fehlender Schluessel einfach stehen.
    # Fuer diese Bauart gilt der strenge Massstab nicht, und ein rotes Kreuz
    # dafuer waere ein Fehlalarm - einer, an den man sich gewoehnt.
    streng = bool(re.search(r'_(?:vorgaben|defaults)$', vorg))
    if luecke == 'STILL' and not streng:
        teile.append('luecke:andere-grundlage (%s)' % vorg)
    else:
        teile.append('luecke:' + {'ABGELEHNT': 'ok', 'GEMELDET': 'ok',
                                  'STILL': 'ROT'}.get(luecke, '--'))
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
