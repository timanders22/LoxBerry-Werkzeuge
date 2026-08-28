#!/usr/bin/env python3
"""Einen Wachposten gegen fremde Formulare in ein Plugin einbauen.

Vorbild sind Midea2Lox 4.3.0 und Skoda Connect 0.9.13, wo derselbe Posten
von Hand entstanden und gemessen worden ist.

WAS EINGEBAUT WIRD
  1. in die Bibliothek:  <p>_merkwort(), <p>_formtoken(), <p>_fmt(),
     <p>_wachposten()
  2. in htmlauth/index.php: der Aufruf, unmittelbar HINTER der Zeile, die
     die Meldeliste anlegt - und damit vor jedem Handler
  3. in jedes <form> derselben Datei: das versteckte Feld
  4. in beide Sprachdateien: die Sektion [WACHE] mit FEHLT und FALSCH

WAS ES NICHT TUT
  * Es raet nichts. Praefix, Bibliothek, Uebersetzer, Pfadfunktion,
    Datenschluessel, Meldeziel und Ankerzeile kommen als Argumente. Eine
    Namensliste kennt nur, woran jemand gedacht hat - dieselbe Lehre wie bei
    wachposten_pruefen.py am 27.08.2026.
  * <p>_fmt() ruft KEINEN Escape-Helfer des Plugins. Bei drei Linien steht
    der in index.php und waere aus der Bibliothek heraus nicht da. Der Wert
    ist ohnehin hexadezimal; htmlspecialchars() genuegt und haengt an nichts.

WORAN ES SICH WEIGERT
  * Die Bibliothek fehlt, oder es steht schon ein hash_equals darin.
  * Die Ankerzeile passt nicht auf das erwartete Muster.
  * Die Datei hat gemischte Zeilenenden.
  * Nach dem Einbau traegt nicht JEDES Formular ein Merkmal.

Aufruf:
    wachposten_einbauen.py ORDNER PRAEFIX LIBPFAD T_FN PFAD_FN DATENSCHLUESSEL
                           liste|skalar MELDEVAR ANKERZEILE
"""
import io, os, re, sys


def lies(p):
    b = open(p, 'rb').read()
    crlf, lf = b.count(b'\r\n'), b.count(b'\n') - b.count(b'\r\n')
    if crlf and lf:
        raise SystemExit('ABBRUCH %s: gemischte Zeilenenden (CRLF %d, LF %d)' % (p, crlf, lf))
    return b.decode('utf-8'), ('\r\n' if crlf else '\n')


def schreib(p, text, ende, vorher):
    aus = ende.join(text.replace('\r\n', '\n').split('\n')).encode('utf-8')
    c = aus.count(b'\r\n'); l = aus.count(b'\n') - c
    assert not (c and l), 'gemischte Zeilenenden entstanden'
    assert (c > 0) == (vorher == '\r\n'), 'Zeilenende veraendert'
    open(p, 'wb').write(aus)


BAUSTEIN = '''

/* ==================================================================
 * WACHPOSTEN GEGEN FREMDE FORMULARE
 * ==================================================================
 *
 * htmlauth/ schuetzt gegen den UNANGEMELDETEN Aufruf. Es schuetzt nicht
 * dagegen, dass der Browser eines angemeldeten Bedieners ein Formular
 * abschickt, das auf einer fremden Seite steht - die Anmeldung schickt er
 * automatisch mit.
 *
 * Gemessen an Schwesterlinien (Skoda Connect 0.9.12, Midea 4.2.12, beide
 * am 27.08.2026): ein einziger fremder POST genuegte, um das Aktionstoken
 * neu zu wuerfeln. Danach beantwortet der Endpunkt jeden Virtuellen Eingang
 * mit 403 - und ein Virtueller Eingang wertet die Antwort NICHT aus. Der
 * Ausfall bleibt still.
 *
 * Der leere Fall wird eigens abgefangen: hash_equals('', '') ist in PHP
 * TRUE. Wer das Feld nicht vor dem Vergleich auf leer prueft, hat einen
 * Posten gebaut, den jeder passiert, der das Feld leer laesst.
 *
 * Das Merkmal wird aus $_POST und $_GET gelesen, nie aus $_REQUEST:
 * $_REQUEST enthaelt je nach variables_order auch Cookies.
 * ================================================================== */

function {p}_merkwort()
{{
    static $wort = null;
    if ($wort !== null) {{
        return $wort;
    }}
    $pfade = {pfad}();
    $verz  = isset($pfade['{key}']) ? $pfade['{key}'] : '';
    if ($verz === '') {{
        return '';
    }}
    $datei = $verz . '/formmerkwort';
    if (is_readable($datei)) {{
        $roh = trim((string) @file_get_contents($datei));
        if (preg_match('/^[0-9a-f]{{32,64}}$/', $roh)) {{
            $wort = $roh;
            return $wort;
        }}
    }}
    if (function_exists('random_bytes')) {{
        $neu = bin2hex(random_bytes(24));
    }} else {{
        $neu = substr(hash('sha256', uniqid((string) mt_rand(), true) . microtime(true)), 0, 48);
    }}
    if (!is_dir($verz)) {{
        @mkdir($verz, 0775, true);
    }}
    /* Rechte VOR dem Inhalt: zwischen Anlegen und chmod laege sonst ein
     * Fenster, in dem das Merkwort fuer alle lesbar ist. */
    $tmp = $datei . '.tmp';
    if (@file_put_contents($tmp, $neu) !== false) {{
        @chmod($tmp, 0600);
        if (@rename($tmp, $datei)) {{
            @chmod($datei, 0600);
        }} else {{
            @unlink($tmp);
        }}
    }}
    $wort = $neu;
    return $wort;
}}

function {p}_formtoken()
{{
    $grund = {p}_merkwort();
    return $grund === '' ? '' : hash_hmac('sha256', 'formular-v1', $grund);
}}

/* Das versteckte Feld. Bewusst OHNE den Escape-Helfer des Plugins: der
 * steht bei einigen Linien in index.php und waere von hier aus nicht da.
 * Der Wert ist hexadezimal. */
function {p}_fmt()
{{
    return '<input data-role="none" type="hidden" name="fmt" value="'
         . htmlspecialchars({p}_formtoken(), ENT_QUOTES, 'UTF-8') . '">';
}}

/** Rueckgabe: '' wenn die Anfrage durchgelassen wird, sonst der Grund. */
function {p}_wachposten()
{{
    if (!isset($_SERVER['REQUEST_METHOD']) || $_SERVER['REQUEST_METHOD'] !== 'POST') {{
        return '';
    }}
    $soll = {p}_formtoken();
    $ist = isset($_POST['fmt']) ? $_POST['fmt']
         : (isset($_GET['fmt']) ? $_GET['fmt'] : null);
    if (!is_string($ist) || $ist === '' || $soll === '') {{
        return {t}('WACHE.FEHLT');
    }}
    if (!hash_equals($soll, $ist)) {{
        return {t}('WACHE.FALSCH');
    }}
    return '';
}}
'''

AUFRUF = '''
/* ---------------------------------------------------------------- *
 * Der Wachposten - EIN Posten, vor allen Handlern.
 * Abgewiesen heisst gemeldet, und es wird NICHTS ausgefuehrt: $_POST
 * wird geleert, nur der aktive Reiter bleibt stehen, damit der Bediener
 * nach der Abweisung dort steht, wo er war.
 * ---------------------------------------------------------------- */
${p}_wache = {p}_wachposten();
if (${p}_wache !== '') {{
    ${p}_reiter_merk = isset($_POST['activetab']) && is_string($_POST['activetab'])
        ? (string) $_POST['activetab'] : null;
    $_POST = array();
    if (${p}_reiter_merk !== null) {{
        $_POST['activetab'] = ${p}_reiter_merk;
    }}
    {melde}
}}
'''

DE = ('\n[WACHE]\n'
      'FEHLT = "Die Anfrage trug kein Formularmerkmal und wurde abgewiesen. '
      'Bitte die Seite neu laden und den Vorgang wiederholen."\n'
      'FALSCH = "Das Formularmerkmal war ungültig - vermutlich ist die Sitzung '
      'abgelaufen. Bitte die Seite neu laden."\n')
EN = ('\n[WACHE]\n'
      'FEHLT = "The request carried no form token and was rejected. '
      'Please reload the page and try again."\n'
      'FALSCH = "The form token was invalid - the session has probably expired. '
      'Please reload the page."\n')


def baue(ordner, p, libpfad, tfn, pfadfn, key, art, meldevar, anker):
    lib = os.path.join(ordner, 'webfrontend', libpfad)
    idx = os.path.join(ordner, 'webfrontend', 'htmlauth', 'index.php')
    for f in (lib, idx):
        if not os.path.isfile(f):
            return 'ABBRUCH: %s fehlt' % f
    t_lib, e_lib = lies(lib)
    # Gesucht wird ein FORMULAR-Posten, nicht irgendein hash_equals.
    #
    # Die erste Fassung wies jede Bibliothek ab, die hash_equals enthielt -
    # und traf damit Dashboard und SignalBot, wo der Vergleich einer PIN
    # bzw. einer Rufnummernliste gilt und mit Formularen nichts zu tun hat.
    # Ein Vergleich ist noch kein Posten.
    if ('%s_wachposten' % p) in t_lib or ('%s_fmt(' % p) in t_lib:
        return 'ABBRUCH: die Bibliothek traegt schon einen Formular-Posten'

    # ERST RECHNEN, DANN SCHREIBEN.
    #
    # Die erste Fassung schrieb die Bibliothek sofort und pruefte den Anker
    # danach. Bei einer falschen Ankerzeile blieb das Plugin halb umgebaut
    # zurueck - gemessen am 27.08.2026 in der Gegenprobe. Ein Werkzeug, das
    # auf halbem Weg abbricht, hinterlaesst einen Zustand, den niemand
    # erwartet. Alle vier Aenderungen entstehen jetzt im Speicher; geschrieben
    # wird erst, wenn jede von ihnen steht.
    zu_schreiben = []

    # 1. Bibliothek
    baustein = BAUSTEIN.format(p=p, t=tfn, pfad=pfadfn, key=key)
    neu_lib = t_lib.rstrip('\n')
    if neu_lib.endswith('?>'):
        neu_lib = neu_lib[:-2].rstrip('\n') + '\n' + baustein + '\n?>\n'
    else:
        neu_lib = neu_lib + '\n' + baustein
    zu_schreiben.append((lib, neu_lib, e_lib))

    # 2. Aufruf hinter die Ankerzeile
    t_idx, e_idx = lies(idx)
    z = t_idx.replace('\r\n', '\n').split('\n')
    if anker < 1 or anker > len(z):
        return 'ABBRUCH: Ankerzeile %d gibt es nicht' % anker
    if ('$%s' % meldevar) not in z[anker - 1]:
        return 'ABBRUCH: Zeile %d nennt $%s nicht: %r' % (anker, meldevar, z[anker - 1][:60])
    melde = ('$%s[] = $%s_wache;' % (meldevar, p)) if art == 'liste' \
        else ('$%s = $%s_wache;' % (meldevar, p))
    z[anker - 1:anker] = [z[anker - 1]] + AUFRUF.format(p=p, melde=melde).split('\n')

    # 3. Merkmal in jedes Formular
    # Ein <form>-Anfang kann ueber mehrere Zeilen laufen (EVCC 0.9.22,
    # Zeile 862). Das Merkmal gehoert hinter das schliessende '>', nicht
    # hinter die Zeile mit dem '<form'. Die erste Fassung zaehlte 16
    # Formulare und setzte 15 Merkmale - und brach zu Recht ab.
    n_form = 0
    aus = []
    offen = None          # Einzug des begonnenen, noch nicht geschlossenen Tags
    for zeile in z:
        aus.append(zeile)
        if offen is not None:
            if '>' in zeile:
                aus.append('%s  <?php echo %s_fmt(); ?>' % (offen, p))
                n_form += 1
                offen = None
            continue
        anf = list(re.finditer(r'<form\b', zeile))
        if not anf:
            continue
        geschlossen = len(re.findall(r'<form\b[^>]*>', zeile))
        einzug = re.match(r'\s*', zeile).group(0)
        for _ in range(geschlossen):
            aus.append('%s  <?php echo %s_fmt(); ?>' % (einzug, p))
            n_form += 1
        if len(anf) > geschlossen:
            offen = einzug
    zu_schreiben.append((idx, '\n'.join(aus), e_idx))

    # 4. Sprachdateien
    for datei, text in (('language_de.ini', DE), ('language_en.ini', EN)):
        pfad = os.path.join(ordner, 'templates', 'lang', datei)
        if not os.path.isfile(pfad):
            return 'ABBRUCH: %s fehlt' % pfad
        t_ini, e_ini = lies(pfad)
        if '[WACHE]' in t_ini:
            continue
        zu_schreiben.append((pfad, t_ini.rstrip('\n') + '\n' + text, e_ini))

    # 5. Gegenrechnung VOR dem Schreiben, am gerechneten Stand
    t_neu = dict((a, b) for a, b, _ in zu_schreiben)[idx]
    formulare = len(re.findall(r'<form\b', t_neu))
    merkmale = t_neu.count('%s_fmt()' % p)
    if formulare != merkmale:
        return 'ABBRUCH vor dem Schreiben: %d Formulare, aber %d Merkmale' % (formulare, merkmale)

    for pfad, inhalt, ende in zu_schreiben:
        schreib(pfad, inhalt, ende, ende)

    t_neu, _ = lies(idx)
    formulare = len(re.findall(r'<form\b', t_neu))
    merkmale = t_neu.count('%s_fmt()' % p)
    if formulare != merkmale:
        return 'ABBRUCH nach dem Einbau: %d Formulare, aber %d Merkmale' % (formulare, merkmale)
    return 'eingebaut: %d Formulare, %d Merkmale, Aufruf hinter Zeile %d' % (formulare, merkmale, anker)


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) != 9:
        print(__doc__)
        raise SystemExit(1)
    print(baue(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], int(a[8])))
