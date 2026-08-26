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

Grossbuchstabe = erfuellt, Kleinbuchstabe = offen, "-" = trifft nicht zu.
"""
import re, sys
from pathlib import Path


def php_dateien(p):
    return [f for f in p.rglob('*') if f.is_file() and f.suffix in ('.php', '.cgi', '.html')]


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
        erzeugt = bool(re.search(r'data-(?:ziel|pane|tab)="tab-<\?', t))
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

    muell = [f for f in p.rglob('*')
             if '__pycache__' in str(f) or f.suffix == '.pyc'
             or f.name.endswith(('.vor-sm', '.vor-hausregeln', '.bak', '.orig'))]
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
    """
    p = plugin_wurzel(p)
    aus = []
    texte = {}
    for f in php_dateien(p):
        try:
            texte[f] = f.read_text(encoding='utf-8', errors='replace')
        except Exception:
            pass
    alles = '\n'.join(texte.values())

    # a) zusammengesetzte Klassen
    for m in set(re.findall(r'class="[^"]*sm-[a-z]*-?<\?', alles)):
        aus.append('zusammengesetzte CSS-Klasse (nicht pruefbar): ' + m[:60])

    # b) falscher Autostart-Schluessel
    for f, t2 in texte.items():
        for nr, zl in enumerate(t2.splitlines(), 1):
            if re.search(r"\[['\"]Mqtt['\"]\]\[['\"]Autostart['\"]\]", zl):
                aus.append('falscher Schluessel Mqtt.Autostart (richtig: Gatewayautostart): '
                           + f.name + ':' + str(nr))

    # c) Versionsgleichstand
    def version_aus(name):
        d = p / name
        if not d.is_file():
            return None
        m = re.search(r'^VERSION=(.+)$', d.read_text(encoding='utf-8', errors='replace'), re.M)
        return m.group(1).strip() if m else None
    v_p, v_r, v_pre = version_aus('plugin.cfg'), version_aus('release.cfg'), version_aus('prerelease.cfg')
    if v_p and v_r and v_p != v_r:
        aus.append('plugin.cfg (%s) und release.cfg (%s) weichen ab' % (v_p, v_r))
    if v_r and v_pre and v_r != v_pre:
        aus.append('prerelease.cfg (%s) hinkt hinter release.cfg (%s) her' % (v_pre, v_r))

    # d) benutzte sm-Klassen ohne Definition (nur eigene sm-Praefixe)
    benutzt = set()
    for m in re.findall(r'class="([^"]*)"', alles):
        for k in m.split():
            if re.fullmatch(r'sm-[a-z0-9\-]+', k):
                benutzt.add(k)
    definiert = set(re.findall(r'\.(sm-[a-z0-9\-]+)', alles))
    # Zustandsklassen, die das Skript setzt, sind definiert genug
    definiert |= {'sm-active'}
    for k in sorted(benutzt - definiert):
        aus.append('CSS-Klasse benutzt, aber nirgends definiert: .' + k)
    return aus


def zeile(name, e):
    def z(k, buchstabe):
        if e.get(k) is None:
            return ' -   '
        return (buchstabe.upper() if e[k] else buchstabe.lower()) + '   '
    s = (z('sm', 'sm') + z('tabs', 'tab') + z('leg', 'leg') + z('act', 'act')
         + z('lbmin', 'min') + z('help', 'hlp') + z('lang', 'lng')
         + z('sauber', 'clr') + z('pfad', 'pfd') + z('mask', 'msk') + z('log', 'log'))
    return '%-34s %s' % (name[:34], s)


if __name__ == '__main__':
    print('%-34s %s' % ('Plugin',
                        'sm    tab   leg   act   min   hlp   lng   clr   pfd   msk   log'))
    print('-' * 100)
    offen = 0
    for arg in sys.argv[1:]:
        p = Path(arg)
        e = pruefe(p)
        print(zeile(p.name if p.name else str(p), e))
        for k, txt in (('sm_detail', 'fremdes Kuerzel'), ('tabs_detail', 'Reiter'),
                       ('leg_detail', 'Knoepfe'), ('act_detail', 'Formulare'),
                       ('lbmin_detail', 'LB_MINIMUM'), ('pfad_detail', 'Bibliothekspfad'),
                       ('mask_detail', 'doppelt maskiert'), ('log_detail', 'Protokoll')):
            if k in e and e[k]:
                merk = {'sm_detail': 'sm', 'tabs_detail': 'tabs', 'leg_detail': 'leg',
                        'act_detail': 'act', 'lbmin_detail': 'lbmin',
                        'pfad_detail': 'pfad', 'mask_detail': 'mask', 'log_detail': 'log'}[k]
                if e.get(merk) is False:
                    print('      %-18s %s' % (txt + ':', e[k]))
        if e.get('muell'):
            print('      %-18s %d Dateien' % ('Muell:', e['muell']))
        for b in zusatzpruefungen(p):
            print('      %-18s %s' % ('Zusatz:', b))
            offen_zusatz = True
        if any(e.get(k) is False for k in
               ('sm', 'tabs', 'leg', 'act', 'lbmin', 'help', 'lang',
                'sauber', 'pfad', 'mask', 'log')):
            offen += 1
    if len(sys.argv) > 2:
        print('-' * 100)
        print('%d von %d Plugins mit mindestens einem offenen Punkt.'
              % (offen, len(sys.argv) - 1))
    # Rueckgabewert, damit sich die Pruefung in eine Kette haengen laesst.
    sys.exit(1 if offen else 0)
