#!/usr/bin/env python3
"""Eine Linie an die Hausform angleichen (REGELN_2, "Die innere Form").

Vier Handgriffe, jeder einzeln an- und abwaehlbar, jeder mit Gegenrechnung:

  --escape       <p>_e() von index.php in die Bibliothek verschieben
  --pfade        <p>_pfade() nach <p>_paths() umbenennen
  --meldename ALT NEU     $ALT -> $NEU (die Meldeliste heisst 'fehler')
  --meldeliste VAR        $VAR von Zeichenkette auf Liste umstellen

DER VIERTE IST KEIN SCHOENHEITSGRIFF. Gemessen am 28.08.2026 in
Beschattungswaechter 0.9.6 und Ecowitt-Weiche 0.9.5:

    $bw_fehler = '';        // Zeichenkette
    ...
    $bw_fehler[] = bw_t('TEXT.SICH_KEINE_DATEI');   // fuenfmal

'[] operator not supported for strings' ist in PHP 7.4 wie in PHP 8 ein
FATALER Fehler. Jeder Fehlerweg des Sicherungsknopfes riss die Seite ab -
weisse Seite, kein Text. Der Umbau auf eine Liste behebt das.

Geschrieben wird erst, wenn alle gewaehlten Handgriffe gerechnet sind.
Zeilenenden bleiben, wie sie waren.

Aufruf:  hausform_angleichen.py ORDNER PRAEFIX [Handgriffe ...] [--probe]
"""
import glob, os, re, sys


def lies(p):
    b = open(p, 'rb').read()
    crlf, lf = b.count(b'\r\n'), b.count(b'\n') - b.count(b'\r\n')
    if crlf and lf:
        raise SystemExit('ABBRUCH %s: gemischte Zeilenenden' % p)
    return b.decode('utf-8'), ('\r\n' if crlf else '\n')


def schreib(p, text, ende):
    aus = ende.join(text.replace('\r\n', '\n').split('\n')).encode('utf-8')
    c = aus.count(b'\r\n'); l = aus.count(b'\n') - c
    assert not (c and l), 'gemischte Zeilenenden entstanden'
    assert (c > 0) == (ende == '\r\n'), 'Zeilenende veraendert'
    open(p, 'wb').write(aus)


def angleichen(ordner, p, tun, probe=False):
    idx = os.path.join(ordner, 'webfrontend', 'htmlauth', 'index.php')
    libs = (glob.glob(os.path.join(ordner, 'webfrontend', 'html', '*_lib.php'))
            + glob.glob(os.path.join(ordner, 'webfrontend', 'htmlauth', '*_lib.php')))
    if not os.path.isfile(idx) or not libs:
        return 'ABBRUCH: index.php oder Bibliothek fehlt'
    lib = libs[0]
    t_idx, e_idx = lies(idx)
    t_lib, e_lib = lies(lib)
    bericht = []

    # --- 1. Escape-Helfer in die Bibliothek ---------------------------------
    if 'escape' in tun:
        if re.search(r'function\s+%s_e\s*\(' % p, t_lib):
            return 'ABBRUCH: %s_e() steht schon in der Bibliothek' % p
        # Den Block ueber die KLAMMERBILANZ schneiden, nicht ueber einen
        # regulaeren Ausdruck.
        #
        # Die erste Fassung nahm r'\{.*?\n\}' mit re.S - nicht gierig, aber
        # eben bis zur ERSTEN Zeile, die mit '}' beginnt, irgendwo spaeter in
        # der Datei. Bei einzeiligen Definitionen verschlang sie damit alles
        # dazwischen: in MGiSmart 1.1.4 den kompletten Wachposten (32 Zeilen),
        # in Robonect 24, in ACTiKamera 22, in AWM-Abfuhr 16. Gemessen am
        # 28.08.2026, gefunden an der Zeilenzahl - nicht am Ergebnis, denn
        # PHP-Syntax und Hausform waren danach tadellos.
        zeilen = t_idx.replace('\r\n', '\n').split('\n')
        anf = next((i for i, z in enumerate(zeilen)
                    if re.match(r'^function\s+%s_e\s*\(' % p, z)), None)
        if anf is None:
            return 'ABBRUCH: %s_e() nicht in index.php gefunden' % p
        # Erst wenn die erste oeffnende Klammer gesehen ist, zaehlt die
        # Rueckkehr auf null. Ohne dieses Merkmal endet die mehrzeilige Form
        #     function bw_e($s)
        #     {
        # nie, weil die erste Zeile keine Klammer traegt (Beschattungswaechter,
        # 28.08.2026 - der Abbruch bei '131 Zeilen' kam von hier).
        tiefe, gesehen, ende_i = 0, False, None
        for i in range(anf, len(zeilen)):
            if '{' in zeilen[i]:
                gesehen = True
            tiefe += zeilen[i].count('{') - zeilen[i].count('}')
            if gesehen and tiefe == 0:
                ende_i = i
                break
        if ende_i is None:
            return 'ABBRUCH: das Ende von %s_e() ist nicht zu finden' % p
        block = '\n'.join(zeilen[anf:ende_i + 1])
        if 'htmlspecialchars' not in block:
            return 'ABBRUCH: der Block enthaelt kein htmlspecialchars - falsch geschnitten'
        if ende_i - anf > 8:
            return 'ABBRUCH: %d Zeilen fuer %s_e() - das ist zu viel' % (ende_i - anf + 1, p)
        vorher_n = len(zeilen)
        del zeilen[anf:ende_i + 1]
        if vorher_n - len(zeilen) != ende_i - anf + 1:
            return 'ABBRUCH: Zeilenzahl stimmt nach dem Schnitt nicht'
        t_idx = '\n'.join(zeilen)
        t_idx = re.sub(r'\n{4,}', '\n\n\n', t_idx)
        kopf = ('\n\n/* Der Escape-Helfer gehoert in die Bibliothek, nicht in\n'
                ' * index.php: sonst steht er dem Endpunkt und jedem weiteren\n'
                ' * Aufrufer nicht zur Verfuegung (Hausform, REGELN_2). */\n')
        t_lib = t_lib.rstrip('\n') + kopf + block + '\n'
        bericht.append('escape verschoben')

    # --- 2. _pfade -> _paths ------------------------------------------------
    umbenannt = {}
    if 'pfade' in tun:
        alt, neu = '%s_pfade' % p, '%s_paths' % p
        if re.search(r'\b%s\b' % neu, t_idx + t_lib):
            return 'ABBRUCH: %s gibt es schon' % neu
        n = 0
        for f in sorted(glob.glob(os.path.join(ordner, '**', '*.php'), recursive=True)):
            t, e = lies(f)
            t2, k = re.subn(r'\b%s\b' % alt, neu, t)
            if k:
                umbenannt[f] = (t2, e); n += k
        if not n:
            return 'ABBRUCH: %s kommt nicht vor' % alt
        bericht.append('%s -> %s an %d Stellen' % (alt, neu, n))

    # --- 3. Meldeziel umbenennen -------------------------------------------
    for alt, neu in tun.get('meldename', []):
        if re.search(r'\$%s\b' % neu, t_idx):
            return 'ABBRUCH: $%s gibt es schon' % neu
        t_idx, k = re.subn(r'\$%s\b' % alt, '$' + neu, t_idx)
        if not k:
            return 'ABBRUCH: $%s kommt nicht vor' % alt
        bericht.append('$%s -> $%s (%d)' % (alt, neu, k))

    # --- 4. Zeichenkette -> Liste ------------------------------------------
    for var in tun.get('meldeliste', []):
        # ZEILENWEISE, und die Anlage zuerst. Die erste Fassung stellte erst
        # alle Zuweisungen um und wollte die Anlage danach zurueckbauen - dabei
        # blieb "$var[] =  array();" stehen, mit zwei Leerzeichen. Ein
        # Rueckbau, der auf genaue Abstaende angewiesen ist, ist kein Rueckbau.
        zeilen = t_idx.replace('\r\n', '\n').split('\n')
        anlage = umgestellt = 0
        for i, z in enumerate(zeilen):
            if re.match(r"^\s*\$%s\s*=\s*''\s*;\s*$" % var, z):
                zeilen[i] = re.sub(r"=\s*''\s*;", '= array();', z)
                anlage += 1
                continue
            if re.search(r'\$%s\s*\[\s*\]\s*=' % var, z):
                continue                      # schon eine Liste
            z2, k = re.subn(r'\$%s\s*=\s*' % var, '$%s[] = ' % var, z)
            if k:
                zeilen[i] = z2; umgestellt += k
        if anlage != 1:
            return 'ABBRUCH: die Anlage von $%s wurde %dmal gefunden' % (var, anlage)
        t_idx = '\n'.join(zeilen)

        t_idx, k3 = re.subn(
            r"if\s*\(\s*\$%s\s*!==\s*''\s*\)\s*\{\s*\?>(.*?)<\?php\s*\}" % var,
            lambda m: ("foreach ($%s as $%s_m) { ?>" % (var, var)
                       + re.sub(r'\$%s\b' % var, '$%s_m' % var, m.group(1))
                       + '<?php }'),
            t_idx, flags=re.S)
        if k3 != 1:
            return 'ABBRUCH: die Ausgabestelle von $%s wurde %dmal gefunden' % (var, k3)

        # Gegenrechnung: genau eine Anlage, keine verunglueckte Zeile
        if len(re.findall(r'^\s*\$%s = array\(\);\s*$' % var, t_idx, re.M)) != 1:
            return 'ABBRUCH: nach dem Umbau steht die Anlage von $%s nicht genau einmal da' % var
        if re.search(r'\$%s\[\]\s*=\s*array\(' % var, t_idx):
            return 'ABBRUCH: die Anlage von $%s wurde mit umgestellt' % var
        bericht.append('$%s auf Liste (%d Zuweisungen, 1 Ausgabe)' % (var, umgestellt))

    if not probe:
        for f, (t, e) in umbenannt.items():
            if f not in (idx, lib):
                schreib(f, t, e)
        if idx in umbenannt:
            t_idx = re.sub(r'\b%s_pfade\b' % p, '%s_paths' % p, t_idx)
        if lib in umbenannt:
            t_lib = re.sub(r'\b%s_pfade\b' % p, '%s_paths' % p, t_lib)
        schreib(idx, t_idx, e_idx)
        schreib(lib, t_lib, e_lib)
    return 'angeglichen: ' + '; '.join(bericht)


if __name__ == '__main__':
    a = sys.argv[1:]
    probe = '--probe' in a
    a = [x for x in a if x != '--probe']
    ordner, p = a[0], a[1]
    tun = {'meldename': [], 'meldeliste': []}
    i = 2
    while i < len(a):
        if a[i] == '--escape':
            tun['escape'] = True; i += 1
        elif a[i] == '--pfade':
            tun['pfade'] = True; i += 1
        elif a[i] == '--meldename':
            tun['meldename'].append((a[i+1], a[i+2])); i += 3
        elif a[i] == '--meldeliste':
            tun['meldeliste'].append(a[i+1]); i += 2
        else:
            raise SystemExit('unbekannt: %s' % a[i])
    print(angleichen(ordner, p, tun, probe))
