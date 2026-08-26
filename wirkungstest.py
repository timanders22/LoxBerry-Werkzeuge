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
PHP84 = r'C:\tmp\php-8.4.24-Win32-vs17-x64\php.exe'

# Knopfnamen, die im Test NICHT gedrueckt werden: sie sollen etwas aendern.
# Feldnamen, die ein Formular als AKTIONS-Formular ausweisen (Dienst starten,
# Token erneuern, Test ausloesen). Solche Formulare sollen etwas aendern -
# sie werden im Test gar nicht erst abgeschickt.
AKTIONSFELD = re.compile(r'^(testaktion|aktion|dienst|befehl|action|cmd|task)$', re.I)

# Schluessel, deren Aenderung kein Verlust ist: Zeitstempel und Zaehler, die
# bei jedem Schreiben ohnehin neu gesetzt werden.
EGAL = re.compile(r'/(geaendert|ts|zeit|timestamp|updated|mtime|stand_zeit|letzte?_?\w*zeit)$', re.I)

VERBOTEN = re.compile(
    r'token|test|neu|reset|del|l(oe|ö)sch|leer|refresh|download|quittier'
    r'|start|stop|install|abruf|erneuer|holen|import|export|clear|purge',
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
    name = os.path.basename(str(plugin).replace('\\', '/').rstrip('/')).lower()
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
    u = umgebung(datei, plugin)
    if post is None:
        u.pop('PRUEF_POST', None)
    else:
        pd = HIER / 'post.json'
        pd.write_text(json.dumps(post), encoding='utf-8')
        u['PRUEF_POST'] = str(pd)
    r = subprocess.run(
        [PHP84, '-n', '-d', 'include_path=.;' + str(LB / 'libs' / 'phplib'),
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
    return r.stdout, bef


# Dateien, die sich bei jedem Schreiben aendern DUERFEN: Zweitschriften,
# Nebendateien, Sperren, Protokolle. Wer sie mitnimmt, meldet Absicht als
# Befund.
FLUECHTIG = re.compile(r'backup|sicherung|\.tmp(\.|$)|\.lock$|\.pid$'
                       r'|\.log(\.\d+)?$|\.wdh$|~$', re.I)


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


def vergleiche(vorher, nachher):
    """Unterschiede je Schluessel melden - JSON tief, sonst zeilenweise."""
    aus = []
    for pfad in sorted(set(vorher) | set(nachher)):
        a, b = vorher.get(pfad), nachher.get(pfad)
        if a == b:
            continue
        if a is None:
            aus.append('NEU angelegt: ' + Path(pfad).name)
            continue
        if b is None:
            aus.append('VERSCHWUNDEN: ' + Path(pfad).name)
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
                aus.append('%s geaendert (nur Zeilenenden oder Leerraum)'
                           % Path(pfad).name)
            for z in weg[:12]:
                aus.append('%s: %s' % (Path(pfad).name, z.strip()))
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
            if fa.get(k) != fb.get(k) and not EGAL.search(k):
                aus.append('%s: %s   %r -> %r' % (Path(pfad).name, k, fa.get(k), fb.get(k)))
    return aus


def teste(plugin, verzeichnis='stand'):
    """Rueckgabe: Liste der Befunde. None heisst: hat keine Oberflaeche.

    "keine htmlauth/index.php" war bis 17.08.2026 ein BEFUND - und damit ein
    rotes Kreuz an der ersten Stelle, das nichts bedeutet: ein Plugin ohne
    Weboberflaeche hat schlicht kein Formular, das etwas verlieren koennte,
    und ein falsch angegebenes Verzeichnis ist ein Fehler des Aufrufs, nicht
    des Plugins. Beides wird jetzt getrennt gemeldet und nicht mitgezaehlt.
    """
    d = Path(verzeichnis) / plugin if not Path(plugin).is_absolute() else Path(plugin)
    datei = d / 'webfrontend/htmlauth/index.php'
    if not datei.is_file():
        return None
    # Seite aufrufen, damit Konfiguration und Merkwort ueberhaupt entstehen.
    lauf(datei, plugin)
    lauf(datei, plugin)

    def formulare_lesen():
        html, _ = lauf(datei, plugin)
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
    for nr, (post, knopf) in enumerate(formulare_lesen(), 1):
        vorher = konfig_abbild(plugin)
        lauf(datei, plugin, post)
        nachher = konfig_abbild(plugin)
        # Der gedrueckte Knopf gehoert in den Befund: bei mehreren Knoepfen
        # an einem Formular sagt die Feldliste allein nicht, welcher Zweig
        # gelaufen ist.
        wer = ('Knopf %s' % knopf) if knopf else ', '.join(sorted(post)[:4])
        for u in vergleiche(vorher, nachher):
            befunde.append('Formular %d (%s): %s' % (nr, wer, u))
    return befunde


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

    schlecht = 0
    ohne = 0
    geprueft = 0
    for pfad, anzeige in auftrag:
        b = teste(pfad, verz)
        if b is None:
            ohne += 1
            print('%-40s uebersprungen (keine htmlauth/index.php)' % anzeige)
            continue
        geprueft += 1
        if b:
            schlecht += 1
            print('== ' + anzeige)
            for x in b[:12]:
                print('   ' + x)
        else:
            print('%-40s ok' % anzeige)

    print('\n%d Linien geprueft, %d mit Befund, %d ohne Oberflaeche uebersprungen.'
          % (geprueft, schlecht, ohne))
    if geprueft == 0:
        print('ACHTUNG: es wurde keine einzige Oberflaeche geprueft.')
        return 2
    return 1 if schlecht else 0


if __name__ == '__main__':
    sys.exit(main())
