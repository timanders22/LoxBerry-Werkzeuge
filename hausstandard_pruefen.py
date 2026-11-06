#!/usr/bin/env python3
"""Prueft ein Plugin gegen die strukturellen Punkte von PLUGIN_HAUSREGELN.md.

Rein lesend. Meldet je Plugin eine Zeile mit Kuerzeln:

    sm      CSS-Klassen heissen ueberall sm-
    tabs    Reiterleiste, Bereiche und activetab-Positivliste passen zusammen
    leg     unter jeder Knopfreihe steht eine Legende
    act     jedes Formular sendet an index.php
    lbmin   LB_MINIMUM >= 3.0.0
    help    templates/help/help.html vorhanden
    lang    beide Sprachdateien vorhanden
    sauber  kein __pycache__, keine *.pyc, keine Sicherungsdateien

Dazu die drei Fehlerbilder aus der Docker-NG-Meldung vom 10.08.2026
(siehe PLUGIN_HAUSREGELN.md, Abschnitt "Regeln aus der Docker-NG-Meldung"):

    pfad    der Bibliothekspfad trifft AUCH den installierten Zustand
    mask    kein xx_e(xx_t(...)) auf einen Wert mit HTML-Entitaet
    log     wer ein Protokoll anzeigt, schreibt es auch

Dazu der Kopf jeder Oberflaeche nach Entscheidung Nr. 43 (08.10.2026,
Vorbild Dashboard, index.php?form=settings):

    kpf     ueber der Reiterleiste steht eine Statusuebersicht
    kas     erstes Element im ersten Reiter ist ein sm-hinweis-Kasten

Eine LoxBerry-Navigationsleiste ($navbar[...]) ist seit Nr. 43 ein Befund in
der Spalte tab - und weil es dann keine Reiterleiste gibt, auch in kpf/kas.

Grossbuchstabe = erfuellt, Kleinbuchstabe = offen, "-" = trifft nicht zu.
"""
import re, sys
from pathlib import Path


def php_dateien(p):
    return [f for f in p.rglob('*') if f.is_file() and f.suffix in ('.php', '.cgi', '.html')]


def gemeinsame_abschriften(p):
    """Dateien des Plugins, die byte-gleich mit einer Stammfassung unter Werkzeuge/gemeinsam/ sind
    (sp1-uebergabe3, 02.10.2026). Eine abweichende Abschrift gehoert nicht dazu."""
    stamm = Path(__file__).resolve().parent / 'gemeinsam'
    aus = set()
    if not stamm.is_dir():
        return aus
    vorlagen = {}
    for s in stamm.iterdir():
        if s.is_file():
            vorlagen.setdefault(s.name, []).append(s.read_bytes())
    for f in Path(p).rglob('*'):
        if f.is_file() and f.name in vorlagen:
            try:
                if f.read_bytes() in vorlagen[f.name]:
                    aus.add(f.resolve())
            except OSError:
                pass
    return aus


def plugin_wurzel(p):
    """Die Ebene finden, auf der plugin.cfg liegt.

    Viele Arbeitsordner heissen <Plugin>-<Fassung>/ und enthalten das Plugin
    noch einmal als Unterordner. Die Pruefungen, die feste Pfade benutzen
    (plugin.cfg, templates/help, templates/lang), sahen dort ins Leere und
    meldeten 34 Plugins als "Hilfe fehlt / Sprachdatei fehlt", obwohl beides
    da war. Aufgefallen am 10.08.2026.
    """
    if (p / 'plugin.cfg').is_file():
        return p
    treffer = [d for d in sorted(p.iterdir()) if d.is_dir() and (d / 'plugin.cfg').is_file()]
    return treffer[0] if len(treffer) == 1 else p


def _leeren(t, muster, flags=re.S):
    """Treffer durch Leerzeichen gleicher Laenge ersetzen - Positionen und
    Zeilennummern bleiben gueltig, Zeilenumbrueche bleiben stehen."""
    return re.sub(muster, lambda m: re.sub(r'[^\n]', ' ', m.group(0)), t, flags=flags)


def _php_code(seg):
    """PHP-Stueck ohne Kommentare und Zeichenketten - nur fuer Klammerzaehlung
    und die Frage "gibt das etwas aus?"."""
    seg = re.sub(r'/\*.*?\*/', ' ', seg, flags=re.S)
    seg = re.sub(r'(?m)//[^\n]*|#[^\n]*', ' ', seg)
    seg = re.sub(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"", "''", seg, flags=re.S)
    return seg


def _in_if(t, von, bis):
    """Steht Position bis innerhalb eines if/else-Blocks, der zwischen von und
    bis geoeffnet wurde? foreach/while zaehlen nicht als Bedingung."""
    stapel = []
    for m in re.finditer(r'<\?(?:php)?(.*?)(?:\?>|\Z)', t[von:bis], re.S):
        code = _php_code(m.group(1))
        cs = code.strip()
        # Alternative Schreibweise "if (...):" … "endif;" - nur als ganzes
        # Stueck erkannt; ein ":" mitten im Code ist meist ein ?:-Ausdruck.
        a = re.fullmatch(r'(if|elseif|foreach|for|while)\s*\(.*\)\s*:', cs, re.S)
        if a:
            if a.group(1) == 'elseif' and stapel:
                stapel.pop()
            stapel.append(a.group(1) in ('if', 'elseif'))
            continue
        if re.fullmatch(r'else\s*:', cs):
            if stapel:
                stapel.pop()
            stapel.append(True)
            continue
        if re.fullmatch(r'(?:endif|endforeach|endfor|endwhile)\s*;?', cs):
            if stapel:
                stapel.pop()
            continue
        for k in re.finditer(r'[{}]', code):
            if k.group(0) == '}':
                if stapel:
                    stapel.pop()
                continue
            davor = re.split(r'[;{}]', code[:k.start()])[-1]
            stapel.append(bool(re.match(r'\s*(?:if|elseif|else\s*if|else)\b', davor)))
    return any(stapel)


def _eltern_div(t, pos):
    """Anfang des <div>, das Position pos umschliesst (None, wenn keines).

    RUECKWAERTS gezaehlt, von pos aus. Vorwaerts vom Dateianfang her kippt
    die Zaehlung an jedem unpaarigen <div> in einem PHP- oder JS-String weit
    oben (Intercom oeffnet im Upgrade-Zweig ein smw per echo und schliesst es
    nie); rueckwaerts zaehlt nur, was zwischen Behaelter und Leiste steht."""
    tiefe = 0
    for m in reversed(list(re.finditer(r'<div\b|</div\s*>', t[:pos]))):
        if m.group(0).startswith('</'):
            tiefe += 1
        elif tiefe:
            tiefe -= 1
        else:
            return m.start()
    return None


def _div_ende(t, start):
    tiefe = 0
    for tok in re.finditer(r'<div\b|</div\s*>', t[start:]):
        tiefe += 1 if tok.group(0) == '<div' else -1
        if tiefe == 0:
            return start + tok.end()
    return len(t)


# Zaehlen Statuskacheln (sm-kacheln) als Statusuebersicht? Nr. 43 nennt als
# Form die Tabelle Eigenschaft/Wert wie im Dashboard. Gemessen 08.10.2026 ueber
# die 51 neuesten Ordner: 20 Linien haben ueber den Reitern einen Status,
# davon 2 als Tabelle (Dashboard, Bewaesserung) und 18 als Kacheln - meist mit
# "Dienst laeuft/gestoppt". True misst die Wirkung (es gibt eine Uebersicht),
# False die Form. Offen bis zur Entscheidung des Hausherrn; True ist die
# Empfehlung (siehe wz_kopf/BERICHT.md).
KOPF_KACHELN_ZAEHLEN = True


def _php_kommentare_leeren(t):
    """Kommentare INNERHALB von PHP-Bloecken durch Leerzeichen gleicher Laenge
    ersetzen (Zeilenumbrueche bleiben) - Werkzeug-HS2, 09.10.2026.

    Bis dahin wurden nur Bloecke geleert, die AUSSCHLIESSLICH Kommentar sind.
    aWATTar 1.2.35 erklaert in einem Block mit Code (/* ... */ vor
    $sp_beschriftung = ...) die alte Leiste als '<div class="sm-tab" ...>'
    und 'keine <div>'; _eltern_div() zaehlte diese Erwaehnungen als offene
    div und hielt sie fuer den Behaelter der Reiterleiste - kpf wurde klein,
    obwohl die Statustabelle davor stand.

    Ein kleiner Zeichenleser statt eines regulaeren Ausdrucks, weil '//' und
    '#' in Zeichenketten ('http://', "#fff") kein Kommentar sind. Die
    Zeichenketten selbst bleiben stehen: was ein echo ausgibt, ist echtes
    Markup (Intercom oeffnet einen Behaelter per echo). Ein '//'- oder
    '#'-Kommentar endet wie in PHP am Zeilenende oder am '?>'.
    """
    a = list(t)
    n = len(t)
    i = 0
    while i < n:
        j = t.find('<?', i)
        if j < 0:
            break
        i = j + 2
        if t.startswith('php', i):
            i += 3
        elif t.startswith('=', i):
            i += 1
        while i < n:
            c = t[i]
            if t.startswith('?>', i):
                i += 2
                break
            hd = re.match(r'<<<[ \t]*(["\']?)([A-Za-z_]\w*)\1\r?\n', t[i:i + 80])
            if hd:
                # Heredoc/Nowdoc: bis zur Zeile mit dem Schlusswort ueberspringen.
                e = re.compile(r'\n[ \t]*' + hd.group(2) + r'\b').search(t, i + hd.end() - 1)
                i = n if not e else e.end()
                continue
            if c in ('"', "'"):
                k = i + 1
                while k < n and t[k] != c:
                    k += 2 if t[k] == '\\' else 1
                i = k + 1
                continue
            if t.startswith('/*', i):
                e = t.find('*/', i + 2)
                e = n if e < 0 else e + 2
                for k in range(i, e):
                    if a[k] != '\n':
                        a[k] = ' '
                i = e
                continue
            if t.startswith('//', i) or (c == '#' and not t.startswith('#[', i)):
                k = i
                while k < n and t[k] != '\n' and not t.startswith('?>', k):
                    a[k] = ' '
                    k += 1
                i = k
                continue
            i += 1
    return ''.join(a)


def kopf_pruefen(t, pre):
    """Kopf nach Entscheidung Nr. 43 (08.10.2026). Gibt (kpf, kpf_detail,
    kas, kas_detail) zurueck, oder None, wenn die Seite keine Reiterleiste hat.

    kpf: zwischen dem Behaelter der Reiterleiste (sm-wrap, bei Intercom smw,
    bei ACTiKamera acw - der Name ist eine Formfrage, gesucht wird deshalb das
    ELTERN-div der Leiste) und der Leiste selbst steht eine Statusuebersicht:
    eine <table> oder Statuskacheln (sm-kachel/sm-kacheln; abschaltbar ueber
    KOPF_KACHELN_ZAEHLEN). Die Form schreibt
    Nr. 43 als Tabelle Eigenschaft/Wert vor; das Werkzeug misst die WIRKUNG
    (gibt es eine Zustandsuebersicht?), wie bei den Auswahlfeldern (e).
    Nicht als Status zaehlen:
      - alles in einem Meldungskasten (sm-hinweis/-fehler/-alert/-warnung …);
      - alles in einem if-Block. Ein Status, der nur erscheint, wenn der
        Abruf gelang (Spotpreis-Octopus: Kacheln in if ($oc_st['ok'])), fehlt
        genau dann, wenn man ihn braucht. Eine Schleife (AWM-Abfuhr: Kacheln
        je Kalender in foreach) ist kein Bedingungsblock und zaehlt.
    kas: das erste inhaltliche Element im ersten Bereich (sm-seite/sm-pane)
    ist ein <div class="sm-hinweis">. Uebersprungen werden Leerraum,
    HTML-Kommentare und PHP-Bloecke, die nichts ausgeben und keinen Block
    oeffnen (Kommentar, Zuweisung). Eine Ueberschrift, eine Legende oder ein
    if davor macht ihn offen - so steht es in Nr. 43: "oben im ersten Reiter".
    """
    # Kommentare leeren, sonst trifft die Suche Beispiel-Markup in
    # Begruendungen (Saugroboter, aWATTar, WOLF und Ultraschall erklaeren
    # die Leiste mit '<div class="sm-tab" data-pane="...">' im Kommentar).
    s = _leeren(t, r'<!--.*?-->')
    # Nur Bloecke, die AUSSCHLIESSLICH Kommentar sind. Ein .*? liefe ueber
    # das erste '*/' hinweg bis zum naechsten '*/ ?>' und leerte echten Code.
    s = _leeren(s, r'<\?php\s*/\*(?:(?!\*/).)*\*/\s*\?>')
    # Und Kommentare in Bloecken MIT Code (Werkzeug-HS2, aWATTar 1.2.35).
    s = _php_kommentare_leeren(s)
    zeile_von = lambda pos: s.count('\n', 0, pos) + 1
    seite = re.search(r'<div class="' + pre + r'-(?:seite|pane)[^"]*"[^>]*id="tab-', s)
    if not seite:
        return None
    reiter = None
    # Das Tag darf PHP enthalten (class="sm-tab<?= … ?>") - ein [^>]* bliebe
    # am '?>' haengen und faende in 50 von 51 Linien keine Leiste.
    # 08.10.2026 (Kopf-Welle 1, BatterieBMS): <\?.*?\?> wuchs ueber das erste ?>
    # hinaus und hielt einen Tageslink fuer den ersten Reiter - jetzt endet
    # der PHP-Block am ersten ?>.
    for m in re.finditer(r'<(?:a|button|li)\b(?:<\?(?:(?!\?>).)*\?>|[^>])*?\bdata-(?:ziel|pane|tab)="',
                         s[:seite.start()], re.S):
        reiter = m
        break
    if not reiter:
        return None
    leiste = _eltern_div(s, reiter.start())
    if leiste is None:
        return None
    behaelter = _eltern_div(s, leiste)
    von = behaelter if behaelter is not None else 0

    # -- kpf
    bereich = s[von:leiste]
    meld = []
    for m in re.finditer(r'<div class="(?:[^"]*\s)?' + pre
                         + r'-(?:hinweis|fehler|alert|warnung|warn|info|ok|err|demo)\b', bereich):
        meld.append((m.start(), _div_ende(bereich, m.start())))
    kpf, bedingt = False, []
    muster = r'<table\b|<div class="(?:[^"]*\s)?' + pre + r'-status\b'
    if KOPF_KACHELN_ZAEHLEN:
        muster += r'|class="(?:[^"]*\s)?' + pre + r'-kacheln?\b'
    for m in re.finditer(muster, bereich):
        if any(a <= m.start() < b for a, b in meld):
            continue
        if _in_if(s, von, von + m.start()):
            bedingt.append(zeile_von(von + m.start()))
            continue
        kpf = True
        kpf_detail = 'Status Zeile %d' % zeile_von(von + m.start())
        break
    if not kpf:
        kpf_detail = ('Status nur bedingt (if-Block, Zeile %s)' % ', '.join(map(str, bedingt[:3]))
                      if bedingt else
                      'kein Status zwischen Zeile %d und der Reiterleiste (Zeile %d)'
                      % (zeile_von(von), zeile_von(leiste)))

    # -- kas
    pos = s.index('>', seite.end()) + 1
    while True:
        rest = s[pos:]
        lr = len(rest) - len(rest.lstrip())
        pos += lr
        if s.startswith('<?php', pos):
            ende = s.find('?>', pos)
            ende = len(s) if ende < 0 else ende + 2
            code = _php_code(s[pos + 5:ende - 2])
            # Ein ':' allein heisst nichts (SignalBot: $a = $b ? x() : array();
            # gibt nichts aus); die alternative Schreibweise "if (...):"
            # faengt das Schluesselwort.
            if not re.search(r'[{}]|\b(?:echo|print|printf|vprintf|include|require'
                             r'|include_once|require_once|readfile|passthru'
                             r'|if|else|elseif|foreach|for|while|switch)\b', code):
                pos = ende
                continue
        break
    erstes = s[pos:pos + 120].split('\n')[0].strip()
    m = re.match(r'<div class="([^"]*)"', s[pos:])
    klassen = m.group(1).split() if m else []
    kas = (pre + '-hinweis' in klassen
           and not any(re.fullmatch(pre + r'-(?:warn|warnung|fehler|err|alert)', k) for k in klassen))
    kas_detail = ('Kasten Zeile %d' % zeile_von(pos) if kas else
                  'erstes Element im ersten Reiter (Zeile %d): %s' % (zeile_von(pos), erstes[:50]))
    return kpf, kpf_detail, kas, kas_detail


def pruefe(p):
    p = plugin_wurzel(p)
    e = {}
    texte = {}
    for f in php_dateien(p):
        try:
            texte[f] = f.read_text(encoding='utf-8', errors='replace')
        except Exception:
            pass
    alles = '\n'.join(texte.values())

    # -- eigenes CSS-Kuerzel statt sm- ?
    # Nur Kuerzel zaehlen, die auch als eigene Regel im <style> stehen -
    # sonst werden Fremdklassen wie "form-..." von jQuery Mobile mitgezaehlt.
    kand = {}
    for k in set(re.findall(r'class="(?:[^"]*\s)?([a-z]{2,4})-[a-z0-9-]+', alles)):
        if k in ('sm', 'ui', 'fa', 'lb'):
            continue
        if re.search(r'(?m)^\s*\.' + k + r'-[a-z0-9-]+\s*[{,]', alles):
            kand[k] = len(re.findall(r'class="(?:[^"]*\s)?' + k + r'-', alles))
    e['sm'] = not kand
    e['sm_detail'] = sorted(kand, key=kand.get, reverse=True)
    # Kuerzel, mit dem die weiteren Pruefungen arbeiten
    pre = e['sm_detail'][0] if e['sm_detail'] else 'sm'

    # -- Reiter / Bereiche / Positivliste
    # Nur die Bedienoberflaeche unter htmlauth/ zaehlt. webfrontend/html/
    # enthaelt oft ein zweites index.php als Endpunkt fuer den Miniserver -
    # das hat keine Reiter und wuerde die Pruefung verfaelschen.
    haupt = None
    for f, t in texte.items():
        if f.name in ('index.php', 'index.cgi') and 'htmlauth' in str(f):
            haupt = (f, t)
            break
    if not haupt:
        e['tabs'] = None
    else:
        t = haupt[1]
        # Die Reiterleiste heisst je nach Plugin data-ziel oder data-pane.
        ziele = re.findall(r'data-(?:ziel|pane|tab)="(tab-[a-z0-9]+)"', t)
        # Der Bereichsbehaelter heisst in VORLAGE_hausstandard.css.html
        # sm-seite; aeltere Plugins nennen ihn sm-pane. Beides zaehlt, sonst
        # meldet die Pruefung "0 Bereiche" und wirft faelschlich einen Befund
        # aus (aufgefallen am 05.08.2026 an AnkerSolix und Skoda Connect).
        # Das Klassenattribut darf mehr enthalten als nur den Bereichsnamen:
        # manche Plugins setzen den aktiven Reiter serverseitig und schreiben
        # class="sm-seite<?= … ' sm-active' … ?>". Ein Muster, das direkt hinter
        # 'seite' das Anfuehrungszeichen erwartet, findet die Bereiche dann
        # NICHT und meldet faelschlich "0 Bereiche" (aufgefallen am 07.08.2026
        # an Docker NG, das genau so gebaut ist - und zwar richtig: so bleibt
        # die Seite ohne JavaScript bedienbar).
        panes = re.findall(r'class="' + pre + r'-(?:pane|seite)[^"]*"[^>]*id="(tab-[a-z0-9]+)"', t)
        # Die Positivliste darf zweierlei Gestalt haben. Manche Plugins
        # schreiben sie als regulaeren Ausdruck ^tab-(settings|mqtt|...),
        # andere als array('tab-settings', 'tab-mqtt', ...) und pruefen mit
        # in_array(..., true). Beides ist eine Positivliste und beides ist
        # richtig; bis zum 10.08.2026 kannte die Pruefung nur die erste Form
        # und meldete BLE-Scanner und Chromecast4lox faelschlich als "Liste 0".
        m = re.search(r"\^tab-\(([a-z0-9|]+)\)", t)
        liste = set('tab-' + x for x in m.group(1).split('|')) if m else set()
        for arr in re.finditer(r"(?:array\s*\(|\[)((?:\s*'tab-[a-z0-9]+'\s*,?)+)\s*[)\]]", t):
            liste |= set(re.findall(r"'(tab-[a-z0-9]+)'", arr.group(1)))
        # Dritte Gestalt: eine ZUORDNUNG Reitername -> Sprachschluessel, aus
        # deren Schluesseln das Muster gebaut wird. Renault NG fuehrt sie so -
        # und das ist die beste der drei Gestalten, weil sie nur einmal
        # dasteht. Das Werkzeug meldete dafuer bis 20.08.2026 "Liste 0", also
        # einen Befund ohne Sache.
        if not liste:
            for nm in re.finditer(r"\^tab-\('.{0,400}?array_keys\(\$([A-Za-z_][A-Za-z0-9_]*)\)",
                                  t, re.S):
                a = re.search(r"\$" + nm.group(1) + r"\s*=\s*array\s*\((.*?)\n\);",
                              t, re.S)
                if a:
                    liste |= set('tab-' + k for k in
                                 re.findall(r"'([a-z0-9]+)'\s*=>", a.group(1)))
        # Vierte Gestalt der Liste: ein FLACHES Array, dessen Namen ueber
        # implode in das Muster gehen. Volkswagen ID fuehrt sie so.
        if not liste:
            for nm in re.finditer(
                    r"\^tab-\('.{0,400}?implode\('\|',\s*\$([A-Za-z_][A-Za-z0-9_]*)\)",
                    t, re.S):
                a = re.search(r"\$" + nm.group(1) + r"\s*=\s*array\s*\((.*?)\);",
                              t, re.S)
                if a:
                    liste |= set('tab-' + k for k in
                                 re.findall(r"'([a-z0-9]+)'", a.group(1)))
        # Die ERZEUGTE Leiste. Steht dort data-ziel="tab-<? , entstehen die
        # Namen der Leiste aus der Liste und koennen nicht abweichen -
        # verglichen wird dann Liste gegen Bereiche. Der Beitext sagt es,
        # damit niemand glaubt, die Leiste sei nachgesehen worden.
        # Das "tab-" muss nicht IM Markup stehen. ZendureSolarFlow setzt
        # es in der Schleife zusammen ($zd_id = 'tab-' . $zd_k) und schreibt
        # data-ziel="<?= zd_e($zd_id) ?>". Das alte Muster verlangte
        # data-ziel="tab-<? und traf dort nicht - die Linie bekam einen
        # Strich, der wie ein Haken aussieht: 5 Bereiche, und nachgesehen
        # wurde nichts. Gemessen am 07.09.2026 ueber alle 49 Linien.
        erzeugt = bool(re.search(r'data-(?:ziel|pane|tab)="(?:tab-)?<\?', t))
        if not ziele and erzeugt and liste:
            e['tabs'] = (liste == set(panes))
            e['tabs_detail'] = ('Leiste erzeugt, %d Bereiche, Liste %d'
                                % (len(panes), len(liste)))
        elif not ziele:
            e['tabs'] = None
        else:
            e['tabs'] = (set(ziele) == set(panes) and set(ziele) <= liste)
            e['tabs_detail'] = ('%d Reiter, %d Bereiche, Liste %d'
                                % (len(ziele), len(panes), len(liste)))

    # -- LoxBerry-Navigationsleiste statt gruener Reiter (Nr. 43, 08.10.2026)
    # Bis hierher bekam eine Linie mit $navbar[...] und mehreren Einzelseiten
    # in der Spalte tab einen Strich: index.php hat keine data-ziel, also
    # "trifft nicht zu". Zigbee2MqttNG 4.1.0 stand so in der Liste, und die
    # Schlusszeile sagte "0 von 51 offen" - ein Strich, der wie ein Haken
    # aussieht. Nr. 43: gruene sm-tabs, KEINE Navigationsleiste. Das gilt auch
    # neben vorhandenen Reitern (Intercom fuehrt beides: Reiter auf index.php
    # und eine Navigationsleiste zu live.php/archive.php/videoarchive.php).
    # Gesucht wird die Zuweisung an ein Element, nicht das Wort: Zigbee
    # schreibt in bin/defines.php '$navbar = array();' - das leert nur.
    nav = []
    seiten = []
    for f, t2 in sorted(texte.items()):
        if re.search(r'\$navbar\s*(?:\[|\{)', t2):
            nav.append(f.name)
            seiten += re.findall(r"\[['\"]URL['\"]\]\s*=\s*['\"]([^'\"]+)['\"]", t2)
    for f in sorted(p.rglob('*.pl')):
        try:
            if re.search(r'\$navbar\s*\{', f.read_text(encoding='utf-8', errors='replace')):
                nav.append(f.name)
        except OSError:
            pass
    if nav:
        alt = e.get('tabs_detail')
        e['tabs'] = False
        e['tabs_detail'] = ('LoxBerry-Navigationsleiste ($navbar in %s%s) statt sm-tabs'
                            % (', '.join(nav),
                               ('; Seiten: ' + ', '.join(sorted(set(seiten)))) if seiten else ''))
        if alt:
            e['tabs_detail'] += '; daneben ' + alt

    # -- Kopf: Status ueber den Reitern, Kasten oben im ersten Reiter (Nr. 43)
    kopf = kopf_pruefen(haupt[1], pre) if haupt else None
    if kopf is None:
        if nav:
            # Ohne Reiterleiste gibt es weder "ueber den Reitern" noch einen
            # ersten Reiter - offen, nicht "trifft nicht zu".
            e['kpf'] = e['kas'] = False
            e['kpf_detail'] = e['kas_detail'] = 'keine Reiterleiste (Navigationsleiste)'
        else:
            e['kpf'] = e['kas'] = None
    else:
        e['kpf'], e['kpf_detail'], e['kas'], e['kas_detail'] = kopf

    # -- Legende: jeder Reiter mit Knopfreihen braucht eine gesammelte
    #    Legende (Beschluss 01.08.2026), nicht eine je Reihe.
    reihen = len(re.findall(r'class="' + pre + r'-knopfreihe', alles))
    if reihen == 0:
        e['leg'] = None
    else:
        ohne = []
        quelle = haupt[1] if haupt else alles
        # Das Klassenattribut darf mehr enthalten als den Bereichsnamen -
        # dasselbe Muster wie oben bei den Bereichen. Ein Muster, das direkt
        # hinter 'seite' das Anfuehrungszeichen erwartet, findet bei
        # serverseitig gesetztem aktiven Reiter GAR KEINEN Bereich, prueft
        # dann nichts und meldet Erfolg. So blieben am 10.08.2026 26 Reiter
        # mit unpassender Legende unbemerkt (Docker NG, AWM-Abfuhr u.a.).
        for m in re.finditer(r'<div class="' + pre + r'-(?:pane|seite)[^"]*"[^>]*id="(tab-[a-z0-9]+)"', quelle):
            rest = quelle[m.start():]
            tiefe, pos = 0, 0
            for tok in re.finditer(r'</?div', rest):
                tiefe += 1 if tok.group(0) == '<div' else -1
                if tiefe == 0:
                    pos = tok.end()
                    break
            inhalt = rest[:pos] if pos else rest
            # Nicht nur "gibt es ueberhaupt eine Legende", sondern: nennt sie
            # genau die Farben, die in diesem Reiter als Knopf vorkommen?
            # Eine Legende, die Gruen erklaert, wo es keinen gruenen Knopf
            # gibt, ist genauso irrefuehrend wie eine fehlende.
            knopf = set(re.findall(r'class="[^"]*' + pre + r'-btn[^"]*' + pre + r'-b-([a-z]+)', inhalt))
            leg = set(re.findall(pre + r'-punkt ' + pre + r'-b-([a-z]+)', inhalt))
            if knopf and knopf != leg:
                fehlt = sorted(knopf - leg)
                zuviel = sorted(leg - knopf)
                txt = m.group(1)
                if fehlt:
                    txt += ' ohne ' + '/'.join(fehlt)
                if zuviel:
                    txt += ' zuviel ' + '/'.join(zuviel)
                ohne.append(txt)
        e['leg'] = not ohne
        e['leg_detail'] = ('Legende passt nicht: ' + '; '.join(ohne)) if ohne else ''

    # -- Formularziel
    # Die alte Perl-Struktur sendet an index.cgi - das ist dort richtig.
    forms = len(re.findall(r'<form[^>]*method="post"', alles))
    acts = len(re.findall(r'action="\.?/?index(?:\.php|\.cgi)"', alles))
    e['act'] = None if forms == 0 else (forms == acts)
    e['act_detail'] = '%d Formulare / %d mit action' % (forms, acts)

    # -- plugin.cfg
    cfg = p / 'plugin.cfg'
    if cfg.is_file():
        c = cfg.read_text(encoding='utf-8', errors='replace')
        m = re.search(r'^LB_MINIMUM=(.+)$', c, re.M)
        v = (m.group(1).strip() if m else '')
        try:
            e['lbmin'] = tuple(int(x) for x in (v.split('.') + ['0', '0'])[:3]) >= (3, 0, 0)
        except ValueError:
            e['lbmin'] = False
        e['lbmin_detail'] = v or 'fehlt'
    else:
        e['lbmin'] = None

    e['help'] = (p / 'templates/help/help.html').is_file()
    e['lang'] = ((p / 'templates/lang/language_de.ini').is_file()
                 and (p / 'templates/lang/language_en.ini').is_file())

    # '.backup' im Namen seit 17.09.2026: CLAUDE.md §9 verbietet ".backup" im
    # Plugin, die Liste kannte es aber nicht. Zendure 0.9.15 bis 0.9.19 lieferten
    # config/zendure.backup.json mit, der Installer legte sie IN den
    # Konfigordner, und das Freigabetor war jedes Mal gruen. Gemessen vor der
    # Aenderung: in 301 Ordnern und 357 Archiven traf die Suche nur diese fuenf.
    muell = [f for f in p.rglob('*')
             if '__pycache__' in str(f) or f.suffix == '.pyc'
             or f.name.endswith(('.vor-sm', '.vor-hausregeln', '.bak', '.orig'))
             or '.backup' in f.name.lower()]
    e['sauber'] = not muell
    e['muell'] = len(muell)

    # ---- pfad: Bibliothekspfad aus htmlauth heraus ------------------
    # Im Archiv liegen htmlauth/ und html/ nebeneinander, installiert unter
    # je einer eigenen plugins/-Ebene. Ein fester __DIR__/../html/-Pfad
    # trifft nur den Archivfall - installiert gibt es HTTP 500.
    # Gefunden am 10.08.2026 an Docker NG, gemeldet von einem Mitleser.
    naiv = []
    for f, t in texte.items():
        if 'htmlauth' not in str(f) or f.suffix != '.php':
            continue
        if re.search(r"(?:require|include)(?:_once)?\s+__DIR__\s*\.\s*'/\.\./html/", t):
            # Eine Kandidatenliste daneben macht es wieder richtig.
            if not (re.search(r'foreach\s*\(\s*array\(', t) and 'html/plugins/' in t):
                naiv.append(f.name)
    e['pfad'] = not naiv if any('htmlauth' in str(f) for f in texte) else None
    e['pfad_detail'] = ', '.join(naiv)

    # ---- mask: doppelte Maskierung -----------------------------------
    # xx_e(xx_t(KEY)) auf einen Wert, der eine HTML-Entitaet enthaelt,
    # zeigt im Browser woertlich 'l&auml;uft'. Am 10.08.2026 an 40 Stellen
    # in 13 Plugins gefunden.
    werte = {}
    for ini in p.rglob('language_de.ini'):
        abschnitt = None
        try:
            zeilen = ini.read_text(encoding='utf-8', errors='replace').splitlines()
        except OSError:
            continue
        for z in zeilen:
            s = z.strip()
            if s.startswith(';'):
                continue
            m = re.match(r'^\[([A-Z_]+)\]$', s)
            if m:
                abschnitt = m.group(1)
                continue
            m = re.match(r'^([A-Za-z0-9_]+)\s*=\s*"?(.*?)"?\s*$', s)
            if m and abschnitt:
                werte['%s.%s' % (abschnitt, m.group(1))] = m.group(2)
    treffer = []
    for f, t in texte.items():
        if f.suffix != '.php':
            continue
        for m in re.finditer(r"\b([a-z]{2,6})_e\(\s*\1_t\(\s*'([A-Z_]+\.[A-Za-z0-9_]+)'\s*\)\s*\)", t):
            v = werte.get(m.group(2))
            if v and re.search(r'&[a-zA-Z]{2,8};|&#\d+;', v):
                treffer.append(m.group(2))
    e['mask'] = not treffer if werte else None
    e['mask_detail'] = ('%d Stellen: %s' % (len(treffer), ', '.join(sorted(set(treffer))[:4]))
                        if treffer else '')

    # ---- log: wer anzeigt, muss auch schreiben ------------------------
    # Docker NG hatte dk_log_lesen() und keine schreibende Gegenstelle.
    # Der Reiter blieb dauerhaft leer, ohne dass ein Fehler sichtbar wurde.
    quellen = {f: t for f, t in texte.items() if f.suffix in ('.php', '.cgi')}
    for zusatz in ('*.py', '*.pl', '*.sh'):
        for f in p.rglob(zusatz):
            if f.is_file():
                try:
                    quellen[f] = f.read_text(encoding='utf-8', errors='replace')
                except OSError:
                    pass
    ganz = ''.join(quellen.values())
    zeigt = bool(re.search(r'_log_lesen\s*\(|logdatei|loglist_html', ganz, re.I))
    schreibt = bool(re.search(
        r'file_put_contents\s*\([^;]{0,120}log'      # eigene Textdatei
        r'|_log\s*\(\s*[\'"]'                        # xx_log('...')
        r'|LOGSTART|LoxBerry::Log|logging\.|logger\.', ganz))
    e['log'] = schreibt if zeigt else None
    e['log_detail'] = '' if (schreibt or not zeigt) else 'zeigt ein Protokoll, schreibt aber keines'
    return e


def zusatzpruefungen(p):
    """Vier Pruefungen aus der Sitzung vom 13.08.2026 (siehe
    PLUGIN_PRUEFUNG_2026-08-13.md). Rein lesend; gibt eine Liste von
    Beanstandungen zurueck, leer = nichts gefunden.

    a) zusammengesetzte sm-Klassen (sm-b-<?= ...) - das Werkzeug kann sie
       nicht sehen, deshalb werden sie GEMELDET statt falsch beurteilt
       (Fehlalarm WaermepumpeCloud).
    b) falscher Schluessel Mqtt.Autostart - den gibt es nicht, richtig ist
       Gatewayautostart. Vier Funde dieser Klasse (ACTiKamera, Midea 4.0.0,
       Abfahrtsassistent, WaermepumpeCloud).
    c) Gleichstand plugin.cfg / release.cfg / prerelease.cfg - die
       prerelease.cfg hinkte am 13.08. in 19 Plugins hinterher.
    d) benutzte sm-Klassen ohne Definition - sm-hinweis stand in acht
       Plugins rahmenlos da.
    e) <select> ohne Pfeil - die Rahmen-CSS nimmt ihn weg, und das Feld
       sieht dann aus wie ein Textfeld (05.09.2026; 22 von 43 Linien).
    f) cron/crontab statt cron.NNmin - eine Aenderung daran erreicht eine
       bestehende Anlage nie (am Geraet gemessen, 06.09.2026).
    """
    p = plugin_wurzel(p)
    aus = []          # Liste von (marke, text); marke ist 'BEFUND' oder 'Hinweis'
    texte = {}
    for f in php_dateien(p):
        try:
            texte[f] = f.read_text(encoding='utf-8', errors='replace')
        except Exception:
            pass
    alles = '\n'.join(texte.values())

    # a) zusammengesetzte Klassen
    # sorted(): set() laeuft je Prozess in anderer Reihenfolge (Python
    # streut Zeichenketten-Hashes). Ohne sorted() sind zwei Laeufe
    # desselben Skripts verschieden, und jeder Diff - etwa der Nachweis,
    # dass eine Werkzeugaenderung keine fremde Linie beruehrt - misst die
    # Streuung statt der Aenderung. Am 06.09.2026 hineingetreten:
    # 94 von 180 Ordnern meldeten scheinbar Neues, keiner zu Recht.
    for m in sorted(set(re.findall(r'class="[^"]*sm-[a-z]*-?<\?', alles))):
        # HINWEIS, kein Befund: genau diese Form zeigt
        # VORLAGE_hausstandard.css.html selbst (Zeile 192,
        # class="sm-seite<?= $tab === ... ' sm-active' : '' ?>"). Ueber den
        # Bestand gemessen (04.09.2026): 258 von 293 Zusatzzeilen sind diese.
        # Ein Tor, das dabei rot wird, ist ein abgeschaltetes Tor.
        aus.append(('Hinweis', 'zusammengesetzte CSS-Klasse (nicht pruefbar): ' + m[:60]))

    # b) falscher Autostart-Schluessel
    for f, t2 in texte.items():
        for nr, zl in enumerate(t2.splitlines(), 1):
            if re.search(r"\[['\"]Mqtt['\"]\]\[['\"]Autostart['\"]\]", zl):
                aus.append(('BEFUND',
                            'falscher Schluessel Mqtt.Autostart (richtig: Gatewayautostart): '
                            + f.name + ':' + str(nr)))

    # c) Versionsgleichstand
    def version_aus(name):
        d = p / name
        if not d.is_file():
            return None
        m = re.search(r'^VERSION=(.+)$', d.read_text(encoding='utf-8', errors='replace'), re.M)
        return m.group(1).strip() if m else None
    v_p, v_r, v_pre = version_aus('plugin.cfg'), version_aus('release.cfg'), version_aus('prerelease.cfg')
    if v_p and v_r and v_p != v_r:
        # HINWEIS: das ist der Sollzustand jeder vorbereiteten, noch nicht
        # veroeffentlichten Fassung - der Ordner traegt die hoehere Nummer.
        # Ob er richtig ist, beantwortet fassungslage.py mit Netz.
        aus.append(('Hinweis',
                    'plugin.cfg (%s) und release.cfg (%s) weichen ab' % (v_p, v_r)))
    if v_r and v_pre and v_r != v_pre:
        aus.append(('BEFUND',
                    'prerelease.cfg (%s) hinkt hinter release.cfg (%s) her'
                    % (v_pre, v_r)))

    # d) benutzte sm-Klassen ohne Definition (nur eigene sm-Praefixe)
    #
    # sp1-uebergabe3 (02.10.2026): Klassen, die NUR in einer unveraenderten Abschrift einer gemeinsamen
    # Datei (byte-gleich mit Werkzeuge/gemeinsam/<name>) stehen, sind ein Hinweis: die Datei bringt ihre
    # Klassen mit, die Linie braucht sie erst, wenn sie den Baustein benutzt (Anlass: AWM-Bau mit
    # sprachausgabe.php, .sm-alert/.sm-info/.sm-small). Eine abweichende Abschrift zaehlt wie Code der Linie.
    gem = gemeinsame_abschriften(p)
    eigen = '\n'.join(t2 for f, t2 in texte.items() if f.resolve() not in gem)
    nur_gem = '\n'.join(t2 for f, t2 in texte.items() if f.resolve() in gem)

    def klassen(text):
        b = set()
        for m in re.findall(r'class="([^"]*)"', text):
            for k in m.split():
                if re.fullmatch(r'sm-[a-z0-9\-]+', k):
                    b.add(k)
        return b
    benutzt = klassen(eigen)
    benutzt_gem = klassen(nur_gem)
    definiert = set(re.findall(r'\.(sm-[a-z0-9\-]+)', alles))
    # Zustandsklassen, die das Skript setzt, sind definiert genug
    definiert |= {'sm-active'}
    for k in sorted(benutzt - definiert):
        # BEFUND: ein Tippfehler in einem CSS-Namen erzeugt keine
        # Fehlermeldung, sondern gar nichts. Genau so ging die tote Klasse
        # .sm-warnung durch ein gruenes Freigabetor hinaus - der Satz "Die
        # Datei enthaelt Ihre Zugangsdaten" stand rahmenlos da.
        aus.append(('BEFUND', 'CSS-Klasse benutzt, aber nirgends definiert: .' + k))
    for k in sorted(benutzt_gem - benutzt - definiert):
        aus.append(('Hinweis', 'CSS-Klasse .%s aus gemeinsamer Datei (unveraenderte Abschrift), '
                               'erst bei Benutzung noetig' % k))

    # e) Ist ein <select> als Auswahlfeld erkennbar?
    #
    # Die LoxBerry-Rahmen-CSS (jQuery Mobile) nimmt dem Auswahlfeld den
    # Pfeil; data-role="none" haelt nur deren Umbauten fern, nicht deren
    # Stilregeln. Ohne Pfeil sieht das Feld aus wie ein Textfeld - acht
    # Vorlagen standen dahinter, und der Anwender fand sie nicht
    # (Bewaesserung 18.08.2026; von einem Menschen gefunden, nicht von der
    # Kette).
    #
    # Gemessen wird die WIRKUNG, nicht ein Klassenname. Der Selektor heisst
    # je Linie anders - .sm-wrap select, .sm-feld select, .sm-row select,
    # .smw select -; ihn vorzuschreiben waere eine Formfrage. Gesucht wird
    # deshalb ein Regelblock, der ein <select> trifft und darin appearance
    # UND background-image setzt.
    #
    # HINWEIS und nicht BEFUND: ueber den Bestand gemessen (05.09.2026)
    # zeichnen 22 von 43 Linien keinen Pfeil, zusammen 102 Auswahlfelder.
    # Ein Freigabetor, das bei der Haelfte des Bestands rot wird, wird
    # abgeschaltet. Sobald die Zahl klein ist, gehoert daraus ein BEFUND -
    # dafuer ist nur die Marke unten zu tauschen.
    auswahl = re.findall(r'<select\b[^>]*>', alles, re.I)
    if auswahl:                  # ueber eine leere Menge wird nicht geurteilt
        css = '\n'.join(re.findall(r'<style\b[^>]*>(.*?)</style>', alles, re.S | re.I))
        zeichnet = False
        for sel, rumpf in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
            sl = sel.lower()
            if not re.search(r'(^|[\s,>.])select\b', sl) and 'sm-auswahl' not in sl:
                continue
            r = rumpf.lower()
            if 'appearance' in r and 'background-image' in r:
                zeichnet = True
                break
        if not zeichnet:
            aus.append(('Hinweis',
                        'Auswahlfeld ohne Pfeil: %d <select>, aber keine Regel mit '
                        'appearance und background-image - das Feld sieht aus wie '
                        'ein Textfeld' % len(auswahl)))

    # f) Ein Cron-Eintrag als cron/crontab kommt genau EINMAL an.
    #
    # plugininstall.pl:977
    #     if (-e "$tempfolder/cron/crontab"
    #         && !-e "$lbhomedir/system/cron/cron.d/$pname") {
    # kopiert nur, wenn die Datei noch nicht da ist, und purge_installation
    # entfernt sie ausdruecklich nur beim Deinstallieren ("only on
    # uninstall"). Jede spaetere Aenderung bleibt auf jeder bestehenden
    # Anlage wirkungslos - fuer immer.
    #
    # Am Geraet gemessen (06.09.2026): Intercom 2.2.6, Dateien vom
    # 05.09.2026, cron.d-Eintrag vom 10.08.2026 mit ">/dev/null 2>&1",
    # waehrend das Archiv seit 2.2.4 "| logger -t ..." mitbringt. Dieselbe
    # Lage bei smartmeter-classic.
    #
    # BEFUND und nicht Hinweis - anders als bei (a) und (e) ist die Menge
    # klein: im Bestand tragen 9 von 180 Ordnern ein cron/crontab, und das
    # sind die Fassungen von genau ZWEI Linien. Die uebrigen 165 mit
    # cron/-Ordner gehen ueber cron.NNmin und bleiben still.
    if (p / 'cron' / 'crontab').is_file():
        aus.append(('BEFUND',
                    'cron/crontab wird nur bei der ERSTEN Installation '
                    'geschrieben (plugininstall.pl:977) - jede Aenderung daran '
                    'erreicht eine bestehende Anlage nie; nach cron/cron.NNmin/ '
                    'umstellen'))
    return aus


def zeile(name, e):
    def z(k, buchstabe):
        if e.get(k) is None:
            return ' -   '
        return (buchstabe.upper() if e[k] else buchstabe.lower()) + '   '
    s = (z('sm', 'sm') + z('tabs', 'tab') + z('leg', 'leg') + z('act', 'act')
         + z('lbmin', 'min') + z('help', 'hlp') + z('lang', 'lng')
         + z('sauber', 'clr') + z('pfad', 'pfd') + z('mask', 'msk') + z('log', 'log')
         # Kopf nach Entscheidung Nr. 43 (08.10.2026)
         + z('kpf', 'kpf') + z('kas', 'kas'))
    return '%-34s %s' % (name[:34], s)


if __name__ == '__main__':
    print('%-34s %s' % ('Plugin',
                        'sm    tab   leg   act   min   hlp   lng   clr   pfd   msk   log   kpf   kas'))
    print('-' * 100)
    offen = 0
    for arg in sys.argv[1:]:
        p = Path(arg)
        e = pruefe(p)
        print(zeile(p.name if p.name else str(p), e))
        for k, txt in (('sm_detail', 'fremdes Kuerzel'), ('tabs_detail', 'Reiter'),
                       ('leg_detail', 'Knoepfe'), ('act_detail', 'Formulare'),
                       ('lbmin_detail', 'LB_MINIMUM'), ('pfad_detail', 'Bibliothekspfad'),
                       ('mask_detail', 'doppelt maskiert'), ('log_detail', 'Protokoll'),
                       ('kpf_detail', 'Kopf-Status'), ('kas_detail', 'Kasten oben')):
            if k in e and e[k]:
                merk = {'sm_detail': 'sm', 'tabs_detail': 'tabs', 'leg_detail': 'leg',
                        'act_detail': 'act', 'lbmin_detail': 'lbmin',
                        'pfad_detail': 'pfad', 'mask_detail': 'mask', 'log_detail': 'log',
                        'kpf_detail': 'kpf', 'kas_detail': 'kas'}[k]
                if e.get(merk) is False:
                    print('      %-18s %s' % (txt + ':', e[k]))
        if e.get('muell'):
            print('      %-18s %d Dateien' % ('Muell:', e['muell']))
        offen_zusatz = False
        for marke, b in zusatzpruefungen(p):
            print('      %-18s %s' % ('Zusatz-' + marke + ':', b))
            if marke == 'BEFUND':
                offen_zusatz = True
        if any(e.get(k) is False for k in
               ('sm', 'tabs', 'leg', 'act', 'lbmin', 'help', 'lang',
                'sauber', 'pfad', 'mask', 'log', 'kpf', 'kas')) or offen_zusatz:
            offen += 1
    if len(sys.argv) > 2:
        print('-' * 100)
        print('%d von %d Plugins mit mindestens einem offenen Punkt.'
              % (offen, len(sys.argv) - 1))
    # Rueckgabewert, damit sich die Pruefung in eine Kette haengen laesst.
    sys.exit(1 if offen else 0)
