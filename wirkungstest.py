#!/usr/bin/env python3
"""Wirkungstest: ueberlebt die Konfiguration das Absenden eines Formulars?

Der Test macht genau das, was ein Benutzer macht, der nichts aendert:

  1. Seite einmal aufrufen (das Plugin legt Konfiguration und Merkwort an).
  2. Abbild der Konfiguration nehmen.
  3. Seite rendern, JEDES Formular so einsammeln, wie ein Browser es
     abschicken wuerde (alle Felder mit ihren angezeigten Werten).
  4. Formular unveraendert absenden.
  5. Konfiguration erneut lesen und mit dem Abbild vergleichen.

Jeder Unterschied ist ein Befund: ein Formular hat einen Wert veraendert,
den es gar nicht anzeigt. Genau so gingen am 13.08. bei MarstekVenus,
Robonect und Saugroboter die Aktionstoken verloren.
"""
import difflib, json, os, re, subprocess, sys
from html.parser import HTMLParser
from pathlib import Path

HIER = Path(__file__).resolve().parent
LB = HIER / 'lb'
VORLAUF = HIER / 'vorlauf_post.php'
# Ueber die Umgebung uebersteuerbar - sonst laeuft das Werkzeug nur auf genau
# diesem Rechner, und auf jedem anderen bricht es mit einem Traceback ab.
# Ein Traceback endet mit Rueckgabewert 1, und 1 heisst in diesem Werkzeug
# "mit Befund": ein fehlender Interpreter saehe aus wie ein kaputtes Plugin.
PHP84 = os.environ.get('PHP84') or r'C:\tmp\php-8.4.27-Win32-vs17-x64\php.exe'

# Knopfnamen, die im Test NICHT gedrueckt werden: sie sollen etwas aendern.
# Feldnamen, die ein Formular als AKTIONS-Formular ausweisen (Dienst starten,
# Token erneuern, Test ausloesen). Solche Formulare sollen etwas aendern -
# sie werden im Test gar nicht erst abgeschickt.
AKTIONSFELD = re.compile(r'^(testaktion|aktion|dienst|befehl|action|cmd|task)$', re.I)

# Schluessel, deren Aenderung kein Verlust ist: Zeitstempel und Zaehler, die
# bei jedem Schreiben ohnehin neu gesetzt werden.
EGAL = re.compile(r'/(geaendert|ts|zeit|timestamp|updated|mtime|stand_zeit|letzte?_?\w*zeit)$', re.I)

def epochenpaar(a, b):
    """Sehen ALTER und NEUER Wert beide wie ein Unix-Zeitstempel aus?

    EGAL trifft nur Schluessel, die auf ts/zeit/geaendert enden. Steht ein
    Zeitstempel als Element einer Messreihe (.../punkte/3/0), heisst der
    Blattname eine Ziffer - das Werkzeug meldete dann eine Aenderung, die
    keine ist. Gemessen an Raumklima 0.11.2: zwoelf Zeilen aus verlauf.json,
    alle nur Zeitstempel.

    Die Regel ist bewusst eng: sie greift nur, wenn BEIDE Seiten Zahlen im
    Fenster 2017 bis 2049 sind. Ueber den ganzen Bestand der Attrappe
    gemessen (05.09.2026): 39.105 Blattwerte, davon 377 epochenaehnlich -
    und jeder einzelne davon ist ein Zeitstempel. Blattnamen: eine Ziffer
    296-mal, ts 47, zeit 12, geaendert 7, TS 3, dazu bis, erzeugt,
    wartung_ts, sperre_bis, letzter_versuch, klima_fertig_um,
    laden_fertig_um, platz_zeit, lauf_ts. Keine Einstellung faellt in
    dieses Fenster; eine Zahl, die eine Einstellung waere, muesste ueber
    1,5 Milliarden liegen.
    """
    for w in (a, b):
        if isinstance(w, bool) or not isinstance(w, (int, float)):
            return False
        if not (1500000000 <= w <= 2500000000):
            return False
    return True


# `^mitschnitt$` seit 25.09.2026 - der GANZE Name, nicht das Wort. Ein Knopf
# name="mitschnitt" startet oder beendet einen befristeten Mitschnitt (Wert =
# Sekunden bzw. ein/aus); das ist eine Aktion, kein Speichern. Gedrueckt
# wurde er trotzdem, und seine gewollte Wirkung stand als Befund da -
# Bestandslauf 25.09.2026: "/mitschnitt_bis <Zeit> -> 0" bei Weissware 0.9.32
# (Knopf "jetzt beenden", index.php:1542), "0 -> <Zeit>" und "<Zeit> -> 0"
# bei Sprachsteuerung 0.11.10 (index.php:2077/2085) und BatterieBMS 0.9.28
# (index.php:1612/1617) - fuenf Zeilen, alle weg mit dieser Regel. Reichweite,
# gezaehlt am 25.09.2026 ueber alle Plugin-Ordner: name="mitschnitt" steht
# nur an Knoepfen von BatterieBMS, MarstekVenus (mv_test.php, wird hier nicht
# gerendert), Sprachsteuerung und Weissware; das einzige andere Feld mit dem
# Wort ist Govees Einstellung "test_mitschnitt" (Zahlenfeld, von dieser
# Liste ohnehin nicht erfasst). Ein Feld wie "mitschnitt_dauer" in einem
# Speichern-Formular bleibt gemessen.
VERBOTEN = re.compile(
    r'token|test|neu|reset|del|l(oe|ö)sch|leer|refresh|download|quittier'
    r'|start|stop|install|abruf|erneuer|holen|import|export|clear|purge'
    r'|^mitschnitt$',
    re.I)


class Formulare(HTMLParser):
    """Sammelt je Formular die Felder, die ein Browser mitschicken wuerde."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.formulare = []
        self.aktuell = None
        self.select = None
        self.option_offen = None
        self.textarea = None
        self.text = ''

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'form':
            self.aktuell = {'felder': [], 'marker': [], 'versteckt': [],
                            'sichtbar': 0}
        elif self.aktuell is None:
            return
        elif tag == 'input':
            name, typ = a.get('name'), (a.get('type') or 'text').lower()
            if not name or typ in ('submit', 'button', 'reset', 'file'):
                return
            if typ == 'hidden':
                self.aktuell['versteckt'].append(name)
            else:
                self.aktuell['sichtbar'] += 1
            if typ in ('checkbox', 'radio'):
                if 'checked' in a:
                    self.aktuell['felder'].append((name, a.get('value', 'on')))
            else:
                self.aktuell['felder'].append((name, a.get('value', '')))
        elif tag == 'select':
            self.select = a.get('name')
            if self.select:
                self.aktuell['sichtbar'] += 1
        elif tag == 'option' and self.select:
            if 'selected' in a:
                self.option_offen = None
                self.aktuell['felder'].append((self.select, a.get('value', '')))
        elif tag == 'textarea':
            self.textarea = a.get('name')
            self.text = ''
            if self.textarea:
                self.aktuell['sichtbar'] += 1
        elif tag == 'button':
            # Ein Knopf mit name/value wird nur mitgeschickt, wenn er
            # gedrueckt wird - das merken wir uns getrennt.
            #
            # Gedrueckt wird im Test NUR ein Speichern-Knopf. Knoepfe wie
            # "neues Token erzeugen", "Testansage", "Protokoll leeren" oder
            # "Dienst neu starten" AENDERN etwas - das ist ihr Zweck, kein
            # Befund. Wer sie mitdrueckt, misst Absicht als Fehler.
            if a.get('name') and not VERBOTEN.search(a['name']):
                self.aktuell['marker'].append((a['name'], a.get('value', '')))

    def handle_endtag(self, tag):
        if tag == 'form' and self.aktuell is not None:
            self.formulare.append(self.aktuell)
            self.aktuell = None
        elif tag == 'select':
            self.select = None
        elif tag == 'textarea' and self.textarea and self.aktuell is not None:
            self.aktuell['felder'].append((self.textarea, self.text))
            self.textarea = None

    def handle_data(self, d):
        if self.textarea is not None:
            self.text += d


def umgebung(datei, plugin):
    u = dict(os.environ)
    # Kein __pycache__ im Prueflig: die Seite startet das Python des
    # Plugins, und dieses KIND schreibt sonst bin/__pycache__.
    # `python -B` vererbt sich nicht - nur die Umgebungsvariable tut es
    # (gemessen 13.09.2026 an Heimkino 1.3.9 und APC-UPS 1.2.8).
    u['PYTHONDONTWRITEBYTECODE'] = '1'
    u['LBHOMEDIR'] = str(LB)
    # Nur der ORDNERNAME, nicht der ganze Pfad. main() laesst ausdruecklich zu,
    # dass ein Plugin-Ordner unmittelbar als Argument uebergeben wird - dann
    # stand hier bisher der absolute Pfad, und LBPCONFIGDIR fiel unter Windows
    # auf den Plugin-Pfad selbst zurueck. Gemessen am 17.08.2026: Matter2Lox
    # legte seine Konfiguration unter config/plugins/html/ ab, und die Adressen
    # in den erzeugten XML-Vorlagen lauteten http://loxberry/plugins/html/...
    # statt .../plugins/<ordner>/... Der Wirkungstest hat trotzdem gemessen,
    # weil er den ganzen Baum abbildet - jede Pruefung, die den PFAD auswertet,
    # war aber verfaelscht.
    name = pruefling_ordner(plugin)
    u['LBPPLUGINDIR'] = name
    u['LBPCONFIGDIR'] = str(LB / 'config/plugins' / name)
    u['LBPLOGDIR'] = str(LB / 'log/plugins' / name)
    u['LBPDATADIR'] = str(LB / 'data/plugins' / name)
    u['LBPHTMLAUTHDIR'] = str(datei.parent.resolve())
    u['LBPHTMLDIR'] = str((datei.parent.parent / 'html').resolve())
    u['LBPTEMPLATEDIR'] = str((datei.parent.parent.parent / 'templates').resolve())
    u['LBPBINDIR'] = str((datei.parent.parent.parent / 'bin').resolve())
    for k in ('LBPCONFIGDIR', 'LBPLOGDIR', 'LBPDATADIR'):
        Path(u[k]).mkdir(parents=True, exist_ok=True)
    return u


def lauf(datei, plugin, post=None):
    """Rueckgabe: (Ausgabe, Befunde des Vorlaufs, Rueckgabewert).

    DER RUECKGABEWERT WAR BIS ZUM 31.08.2026 VERWORFEN - und das ist dieselbe
    Fehlerklasse, die installationslage_pruefen.py am 16.08.2026 blind gemacht
    hat. Eine Oberflaeche mit Parsefehler liefert 0 Byte und endet mit 255;
    ohne den Rueckgabewert sieht das aus wie eine Seite ohne Formulare, und
    "keine Formulare" hiess in diesem Werkzeug "nichts verloren", also "ok".

    Gemessen am 31.08.2026: eine index.php mit einer zusaetzlichen oeffnenden
    Klammer am Ende (php -l meldet den Parsefehler) ergab
    "1 Linien geprueft, 0 mit Befund", Rueckgabewert 0.
    """
    u = umgebung(datei, plugin)
    if post is None:
        u.pop('PRUEF_POST', None)
    else:
        # Die Nebendatei traegt die PROZESSNUMMER. Ein fester Name im
        # gemeinsamen Werkzeugordner heisst: zwei Laeufe nebeneinander
        # ueberschreiben einander die POST-Daten, und der zweite misst dann
        # das Formular des ersten. Dieselbe Regel wie beim atomaren Schreiben
        # im Hausstandard.
        pd = HIER / ('post.%d.json' % os.getpid())
        pd.write_text(json.dumps(post), encoding='utf-8')
        u['PRUEF_POST'] = str(pd)
    r = subprocess.run(
        # os.pathsep statt eines harten ';' - unter Linux trennt der
        # Doppelpunkt, und ein ';' machte aus beiden Pfaden EINEN. Die
        # phplib waere dort nie gefunden worden, und JEDE Linie haette
        # gleich ausgesehen. Vier gleiche Ergebnisse sind ein Hinweis,
        # kein Beleg.
        [PHP84, '-n', '-d', 'include_path=.' + os.pathsep + str(LB / 'libs' / 'phplib'),
         '-d', 'auto_prepend_file=' + str(VORLAUF), '-d', 'display_errors=0',
         '-d', 'error_reporting=32767', '-d', 'date.timezone=Europe/Berlin',
         '-d', 'extension_dir=' + str(Path(PHP84).parent / 'ext'),
         '-d', 'extension=curl', '-d', 'extension=openssl', '-d', 'extension=mbstring',
         '-d', 'extension=sockets', '-d', 'extension=fileinfo',
         str(datei.resolve())],
        capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=str(datei.parent.resolve()),
        env=u, timeout=90)
    bef = []
    if '###BEFUNDE###' in r.stderr:
        bef = [z for z in r.stderr.split('###BEFUNDE###', 1)[1].strip().splitlines() if z.strip()]
    return r.stdout, bef, r.returncode


# Dateien, die sich bei jedem Schreiben aendern DUERFEN: Zweitschriften,
# Nebendateien, Sperren, Protokolle. Wer sie mitnimmt, meldet Absicht als
# Befund.
#
# Seit 17.09.2026 auch die EINMALMELDUNG der Umleitung nach einem POST
# (Regeln/04, Hausstandard seit 06.09.2026): jeder Knopf schreibt sie, das
# naechste GET liest und loescht sie. Ohne die Ausnahme meldete das Werkzeug
# an jeder Linie mit Umleitung "1 mit Befund", und zwar nur wegen dieser
# Datei - gemessen an Docker NG 1.3.8 (11 von 12 Zeilen) und Raumklima 0.11.8
# (12 von 12). Namentlich, nach Rolle: genau meldung.json und
# einmalmeldung.json, die zwei Namen im Bestand (Reichweite 17.09.2026:
# Abfahrtsassistent 1.6.10, Docker NG 1.3.8, Raumklima 0.11.8). Geeicht an
# einer Kopie von Raumklima, deren MQTT-Speichern den Takt hochzaehlt: die
# Zeile /takt bleibt vorher wie nachher stehen.
FLUECHTIG = re.compile(r'backup|sicherung|\.tmp(\.|$)|\.lock$|\.pid$'
                       r'|\.log(\.\d+)?$|\.wdh$|~$'
                       r'|^(einmal)?meldung\.json$', re.I)


def pruefling_ordner(plugin):
    """Der Ordnername, unter dem die Attrappe den Pruefling erwartet."""
    return os.path.basename(str(plugin).replace('\\', '/').rstrip('/')).lower()


def plugin_ordner(pfad):
    """Der Ordner unmittelbar unter config/plugins bzw. data/plugins.

    Leere Zeichenkette, wenn der Pfad nicht so gebaut ist - dann wird auch
    nichts gekennzeichnet. Lieber keine Angabe als eine falsche.
    """
    t = Path(pfad).parts
    for i, s in enumerate(t):
        if s.lower() == 'plugins' and i + 1 < len(t):
            return t[i + 1].lower()
    return ''


def konfig_abbild(plugin):
    """Alle Konfigurationsdateien als {Pfad: Inhalt}.

    ZWEI BLINDE FLECKEN, BEIDE AM 17.08.2026 GEMESSEN UND BEHOBEN

    Diese Funktion hatte zwei Filter, und jeder liess ganze Linien lautlos
    durchfallen. Bei acht geprueften Linien bekamen VIER ein leeres Abbild -
    das Werkzeug meldete fuer sie "ok", ohne etwas verglichen zu haben.

    1. Der ENDUNGSFILTER liess nur .json/.cfg/.ini/.conf durch. Ein Plugin
       mit config.php (Renault) bekam ein Abbild aus null Dateien. Gegenprobe
       an einer absichtlich kaputten Kopie, die beim Speichern das
       Aktionstoken verliert: das Werkzeug meldete weiterhin "ok".

    2. Der NAMENSFILTER verlangte, dass der Linienname im Pfad vorkommt. Ein
       Plugin bestimmt seinen Ordner aber aus plugin.cfg FOLDER oder aus
       basename(__DIR__) - Heimkino schreibt nach config/plugins/heimkino/,
       Intercom nach config/plugins/htmlauth/. Der Ordner heisst also gerade
       NICHT wie die Linie, und beide fielen durch.

    Beide Filter sind fort. Der Namensfilter wird nicht gebraucht: verglichen
    wird ein Abbild VOR und NACH einem einzelnen Absenden. Was andere Linien
    frueher im Baum hinterlassen haben, steht in beiden Abbildern gleich und
    faellt beim Vergleich heraus.

    Der Endungsfilter bleibt fuer data/plugins bestehen - dort liegen
    Sitzungen, Zwischenspeicher und Aufzeichnungen, die sich bei jedem
    Seitenaufruf aendern DUERFEN. Unter config/plugins wird dagegen alles
    genommen, was nicht ausdruecklich fluechtig ist.
    """
    aus = {}
    for wurzel, alles in ((LB / 'config/plugins', True),
                          (LB / 'data/plugins', False)):
        for f in wurzel.rglob('*'):
            if not f.is_file():
                continue
            if FLUECHTIG.search(f.name):
                continue
            if not alles and f.suffix.lower() not in ('.json', '.cfg', '.ini', '.conf'):
                continue
            try:
                aus[str(f)] = f.read_text(encoding='utf-8', errors='replace')
            except OSError:
                pass
    return aus


def vergleiche(vorher, nachher, eigen=None):
    """Unterschiede je Schluessel melden - JSON tief, sonst zeilenweise.

    `eigen` ist der Ordnername des Prueflings. Ist er gesetzt, bekommt jeder
    Unterschied, der in einem ANDEREN Plugin-Ordner liegt, einen Zusatz.

    Das ist eine KENNZEICHNUNG, kein Filter. Der Namensfilter, den es hier
    frueher gab, ist am 17.08.2026 aus gutem Grund entfernt worden (siehe
    konfig_abbild) und kommt nicht zurueck: ein Plugin schreibt nicht
    zwingend in einen Ordner, der wie es selbst heisst, und ein Formular, das
    eine FREMDE Konfiguration beschaedigt, ist der schwerste Fall ueberhaupt.
    Falsch war nie die Breite der Messung, sondern allein die Zuschreibung -
    am 14.09.2026 las sich ein Rueckstand der gemeinsamen Attrappe
    (`wifi_scanner.cfg`) wie ein Befund von APC-UPS. Gemeldet wird also
    weiterhin alles; es steht nur dabei, wo es liegt.

    Der Zusatz sagt AUSDRUECKLICH nicht "gehoert einer anderen Linie" - das
    waere nicht messbar. Er sagt "liegt nicht im erwarteten Ordner", und das
    ist es. Der Unterschied ist keine Wortklauberei: beim Eichen am
    15.09.2026 stellte sich heraus, dass BatterieBMS seine eigene
    Konfiguration nach `config/plugins/html/` schreibt. Die erste Fassung
    dieses Zusatzes behauptete dort "NICHT im Pruefling" - und log. Wer den
    Zusatz liest, weiss jetzt, wo er nachsehen muss, und entscheidet selbst.
    """
    aus = []
    for pfad in sorted(set(vorher) | set(nachher)):
        wo = plugin_ordner(pfad)
        marke = ('' if (not eigen or not wo or wo == eigen)
                 else '   [liegt in %s, nicht im erwarteten Ordner %s]'
                      % (wo, eigen))

        def melde(text, _m=marke):
            aus.append(text + _m)

        a, b = vorher.get(pfad), nachher.get(pfad)
        if a == b:
            continue
        if a is None:
            melde('NEU angelegt: ' + Path(pfad).name)
            continue
        if b is None:
            melde('VERSCHWUNDEN: ' + Path(pfad).name)
            continue
        try:
            ja, jb = json.loads(a), json.loads(b)
        except ValueError:
            # Kein JSON (config.php, .cfg, .ini): zeilenweise vergleichen.
            # "geaendert (kein JSON)" allein ist kein brauchbarer Befund - man
            # weiss dann, DASS etwas anders ist, und muss trotzdem von Hand
            # nachsehen, WAS. Ein verlorenes Aktionstoken haette so niemand
            # erkannt.
            weg = [z for z in difflib.unified_diff(
                a.splitlines(), b.splitlines(), n=0, lineterm='')
                if z[:1] in ('-', '+') and not z.startswith(('---', '+++'))]
            if not weg:
                melde('%s geaendert (nur Zeilenenden oder Leerraum)'
                      % Path(pfad).name)
            for z in weg[:12]:
                melde('%s: %s' % (Path(pfad).name, z.strip()))
            continue
        def flach(d, p=''):
            f = {}
            if isinstance(d, dict):
                for k, v in d.items():
                    f.update(flach(v, p + '/' + str(k)))
            elif isinstance(d, list):
                for i, v in enumerate(d):
                    f.update(flach(v, p + '/' + str(i)))
            else:
                f[p] = d
            return f
        fa, fb = flach(ja), flach(jb)
        for k in sorted(set(fa) | set(fb)):
            if (fa.get(k) != fb.get(k) and not EGAL.search(k)
                    and not epochenpaar(fa.get(k), fb.get(k))):
                melde('%s: %s   %r -> %r' % (Path(pfad).name, k, fa.get(k), fb.get(k)))
    return aus


def teste(plugin, verzeichnis='stand'):
    """Rueckgabe: (Befunde, Zahl der ABSENDUNGEN, Grund). None heisst: keine
    Oberflaeche.

    "keine htmlauth/index.php" war bis 17.08.2026 ein BEFUND - und damit ein
    rotes Kreuz an der ersten Stelle, das nichts bedeutet: ein Plugin ohne
    Weboberflaeche hat schlicht kein Formular, das etwas verlieren koennte,
    und ein falsch angegebenes Verzeichnis ist ein Fehler des Aufrufs, nicht
    des Plugins. Beides wird jetzt getrennt gemeldet und nicht mitgezaehlt.

    DRITTER AUSGANG, ERGAENZT 31.08.2026: "nicht messbar".
    Bis dahin gab es nur "ok" und "Befund". Rendert die Seite gar nicht -
    Parsefehler, fataler Abbruch, fehlende Bibliothek -, findet der Leser null
    Formulare, die Schleife laeuft nicht, die Befundliste bleibt leer, und die
    Zeile lautete "ok".

    Gemessen am 31.08.2026 an einer index.php mit einer zusaetzlichen
    oeffnenden Klammer (php -l meldet den Parsefehler): "1 Linien geprueft,
    0 mit Befund", Rueckgabewert 0. Das ist die Klasse "eine Pruefung ohne
    Fundstellen ist kein Nachweis, sondern ein blinder Fleck" - und sie sass
    in einem Werkzeug der Freigabekette.
    """
    d = Path(verzeichnis) / plugin if not Path(plugin).is_absolute() else Path(plugin)
    datei = d / 'webfrontend/htmlauth/index.php'
    if not datei.is_file():
        return None
    # Seite aufrufen, damit Konfiguration und Merkwort ueberhaupt entstehen.
    lauf(datei, plugin)
    html0, _b0, rc0 = lauf(datei, plugin)

    # Erst pruefen, ob ueberhaupt etwas zu messen ist. Ein Aufruf, der mit
    # einem Fehler endet oder nichts ausgibt, macht jede folgende Aussage
    # gegenstandslos.
    if rc0 != 0:
        return ([], 0, 'die Oberflaeche bricht mit Rueckgabewert %d ab' % rc0)
    if len(html0.strip()) < 200:
        return ([], 0, 'die Oberflaeche liefert nur %d Zeichen - zu wenig fuer '
                       'eine Seite' % len(html0.strip()))

    def formulare_lesen():
        html, _, _rc = lauf(datei, plugin)
        p = Formulare()
        p.feed(html)
        # Ein Aktionsmarker steht an GENAU EINEM Formular. Felder, die in
        # mehreren Formularen derselben Seite auftauchen, sind Infrastruktur -
        # `activetab`, ein CSRF-Feld, ein Reitername. Ohne diese
        # Unterscheidung liest die Markererkennung `formtoken` als Marker (es
        # enthaelt "token") und ueberspringt beim Abfahrts-Assistenten vier
        # Formulare, die geprueft gehoeren. Gemessen am 17.08.2026.
        haeufig = {}
        for form in p.formulare:
            for n in set(form['versteckt']):
                haeufig[n] = haeufig.get(n, 0) + 1
        aus = []
        for form in p.formulare:
            if not form['felder'] and not form['marker']:
                continue
            post = {}
            for name, wert in form['felder']:
                if name.endswith('[]'):
                    post.setdefault(name[:-2], []).append(wert)
                else:
                    post[name] = wert
            # Ein Formular OHNE sichtbares Bedienelement, dessen versteckte
            # Felder einen Aktionsnamen tragen, ist ein Aktionsformular - es
            # SOLL etwas aendern. Bis 17.08.2026 wurde nur der Name eines
            # <button> darauf geprueft; ein Plugin, das denselben Marker als
            # <input type="hidden"> mitschickt, wurde deshalb abgeschickt und
            # als Befund gemeldet. Gemessen an Intercom 2.1.13 (verstecktes
            # token_neu) gegen Renault 2.1.0 (gleichnamiger Knopf): dasselbe
            # Formular, zweierlei Ergebnis. Ein Werkzeug, das dieselbe Absicht
            # je nach Schreibweise einmal duldet und einmal meldet, ist keins.
            #
            # Die Bedingung ist bewusst eng: NUR wenn das Formular gar kein
            # sichtbares Feld hat. Ein Einstellungsformular mit einem Feld
            # namens 'start_zeit' oder 'install_pfad' faellt sonst mit heraus -
            # und der blinde Fleck waere nur verschoben.
            nur_marker = (form['sichtbar'] == 0
                          and any(VERBOTEN.search(n) and haeufig.get(n, 0) == 1
                                  for n in form['versteckt']))
            if not post or nur_marker or any(AKTIONSFELD.match(k) for k in post):
                continue
            # JEDEN zulaessigen Knopf einzeln druecken - ein Browser schickt
            # auch genau einen mit.
            #
            # Bis 17.08.2026 wurde nur der ERSTE genommen. Heisst der
            # "ms4h_suchen" oder "geraete_suchen", springt der Speicherzweig
            # gar nicht erst an: das Werkzeug meldet "ok", obwohl das
            # Speichern das Aktionstoken verliert. Gemessen an einem gebauten
            # Fall (erster Knopf "geraete_suchen", zweiter "speichern") -
            # gruen, obwohl der Verlust nachweisbar eintrat.
            #
            # Die Antwort darauf ist NICHT, die Verbotsliste um "suchen" zu
            # erweitern. Eine Liste, die man nach jedem neuen Plugin
            # nachziehen muss, ist genau die Sorte Regel, die irgendwann
            # jemand vergisst. Wer alle Knoepfe einzeln drueckt, braucht sie
            # fuer diesen Zweck nicht mehr.
            if form['marker']:
                for name, wert in form['marker']:
                    p2 = dict(post)
                    p2[name] = wert
                    aus.append((p2, name))
            else:
                aus.append((post, ''))
        return aus

    # Einlauf: jedes Formular einmal abschicken. Manche Plugins legen ihre
    # Konfigurationsdatei erst beim ersten Speichern an - das ist Erstanlage,
    # kein Verlust, und darf den eigentlichen Vergleich nicht verfaelschen.
    for post, _knopf in formulare_lesen():
        lauf(datei, plugin, post)

    befunde = []
    liste = formulare_lesen()
    if not liste:
        # Die Seite rendert, traegt aber kein einziges pruefbares Formular.
        # Das ist keine Entlastung - es ist die Abwesenheit einer Messung.
        return ([], 0, 'die Seite rendert, enthaelt aber kein pruefbares '
                       'Formular (alle uebersprungen oder keines vorhanden)')
    for nr, (post, knopf) in enumerate(liste, 1):
        vorher = konfig_abbild(plugin)
        lauf(datei, plugin, post)
        nachher = konfig_abbild(plugin)
        # Der gedrueckte Knopf gehoert in den Befund: bei mehreren Knoepfen
        # an einem Formular sagt die Feldliste allein nicht, welcher Zweig
        # gelaufen ist.
        wer = ('Knopf %s' % knopf) if knopf else ', '.join(sorted(post)[:4])
        for u in vergleiche(vorher, nachher, pruefling_ordner(plugin)):
            befunde.append('Formular %d (%s): %s' % (nr, wer, u))
    return (befunde, len(liste), '')


def main():
    """Aufruf:

        python3 wirkungstest.py                     alles unter stand/
        python3 wirkungstest.py <linie> [...]       einzelne Linien unter stand/
        python3 wirkungstest.py --verz=<pfad> ...   anderes Grundverzeichnis
        python3 wirkungstest.py <pfad-zum-plugin>   ein Ordner irgendwo

    Ein fehlendes oder leeres Grundverzeichnis ist ein ABBRUCH mit
    Rueckgabewert 2 - nicht "0 von 0 Linien". Bis 17.08.2026 brach der Lauf
    bei fehlendem stand/ mit einem Traceback ab und lieferte trotzdem
    Rueckgabewert 0; ein aufrufendes Skript hielt das fuer Erfolg.
    """
    verz = 'stand'
    namen = []
    for a in sys.argv[1:]:
        if a.startswith('--verz='):
            verz = a.split('=', 1)[1]
        elif not a.startswith('--'):
            namen.append(a)

    # Ein Argument, das selbst ein Plugin-Ordner ist, wird unmittelbar
    # genommen - dann braucht es gar kein Grundverzeichnis.
    einzeln = [n for n in namen
               if (Path(n) / 'webfrontend/htmlauth/index.php').is_file()]
    if einzeln and len(einzeln) == len(namen):
        auftrag = [(str(Path(n).resolve()), Path(n).name) for n in namen]
    else:
        wurzel = Path(verz)
        if not wurzel.is_dir():
            print('Grundverzeichnis %r gibt es nicht. Entweder die Linien '
                  'dorthin legen oder --verz=<pfad> angeben, oder einen '
                  'Plugin-Ordner unmittelbar als Argument uebergeben.' % verz)
            return 2
        if not namen:
            namen = [x.name for x in sorted(wurzel.iterdir()) if x.is_dir()]
        if not namen:
            print('Grundverzeichnis %r ist leer - es wurde nichts geprueft.' % verz)
            return 2
        auftrag = [(n, n) for n in namen]

    if not Path(PHP84).is_file() and '/' not in PHP84 and '\\' not in PHP84:
        pass          # ein blosser Name wird ueber den Suchpfad gefunden
    elif not Path(PHP84).is_file():
        print('Der Interpreter %r ist nicht da. Ueber PHP84=<pfad> einen '
              'angeben.\nOhne ihn misst dieses Werkzeug NICHTS - und ein '
              'Traceback saehe aus wie ein Befund.' % PHP84)
        return 2

    schlecht = 0
    ohne = 0
    geprueft = 0
    unmessbar = 0
    absendungen_gesamt = 0
    for pfad, anzeige in auftrag:
        e = teste(pfad, verz)
        if e is None:
            ohne += 1
            print('%-40s uebersprungen (keine htmlauth/index.php)' % anzeige)
            continue
        b, anzahl, grund = e
        if grund:
            # Der dritte Ausgang. Ein Strich zaehlt weder als bestanden noch
            # als Befund - und er sagt, WARUM nicht gemessen werden konnte.
            unmessbar += 1
            print('%-40s NICHT MESSBAR - %s' % (anzeige, grund))
            continue
        geprueft += 1
        absendungen_gesamt += anzahl
        if b:
            schlecht += 1
            print('== %s   (%d Absendungen geprueft)' % (anzeige, anzahl))
            for x in b[:12]:
                print('   ' + x)
        else:
            # Die ZAHL gehoert in die gruene Zeile. "ok" allein sagt nicht,
            # ob ueberhaupt etwas angesehen wurde.
            print('%-40s ok (%d Absendungen geprueft)' % (anzeige, anzahl))

    print('\n%d Linien geprueft (%d Absendungen), %d mit Befund, %d nicht messbar, '
          '%d ohne Oberflaeche uebersprungen.'
          % (geprueft, absendungen_gesamt, schlecht, unmessbar, ohne))
    if geprueft == 0:
        print('ACHTUNG: es wurde keine einzige Oberflaeche geprueft.')
        return 2
    if unmessbar:
        print('ACHTUNG: %d Linie(n) konnten nicht gemessen werden. Ein Strich '
              'ist kein Haken.' % unmessbar)

    # Die eigene Nebendatei wieder wegraeumen - und nur die eigene. Ein
    # Werkzeug, das Spuren im gemeinsamen Werkzeugordner hinterlaesst, laesst
    # den naechsten raten, wo sie herkommen. Fremde post*.json bleiben liegen;
    # sie gehoeren jemand anderem.
    eigen = HIER / ('post.%d.json' % os.getpid())
    try:
        eigen.unlink()
    except OSError:
        pass
    return 1 if schlecht else 0


if __name__ == '__main__':
    sys.exit(main())
