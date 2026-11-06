# -*- coding: utf-8 -*-
"""Probe der Stammfassung sprachausgabe.php gegen Attrappen - der ECHTE Transport.

Laeuft auf: Windows, Python 3 + php.exe 7.4.33 / 8.4.24 / 8.5.11, je ohne und mit curl
(-d extension=curl). Kein Netz: alle Ziele sind 127.0.0.1 (Attrappe in diesem Prozess,
ein geschlossener Port fuer "abgewiesen"). Kein Geraet.

  python Werkzeuge/sprachausgabe_probe.py [--modul PFAD] [--nur 85,85c,...] [--ausgabe ORDNER]

  --modul    eine andere Datei als Werkzeuge/gemeinsam/sprachausgabe.php (Abschrift einer
             Linie, Mutante aus mutation_sprachausgabe.py)
  --nur      nur diese Laeufe: 74 84 85 (Datenstrom), 74c 84c 85c (curl), 74cp 85cp (curl
             mit Proxy in der Umgebung)
  --ausgabe  je Lauf eine Datei probe_<lauf>.txt und probe_zusammenfassung.txt dorthin;
             ohne: nur die Zusammenfassung auf stdout

Die Attrappe spielt Alexa-NG (/plugins/alexang/index.php), Chromecast 4 Lox NG
(/plugins/chromecast-4lox-ng/index.php), einen Music Server (/audio/grouped/tts/...),
MusicServer4Home (/tts?...) und eine eigene Vorlage (/eigen/...). Den Fall waehlt die
Anfrage selbst: bei Alexa/Google das Feld geraet, beim Music Server die Sprache (lang),
bei Vorlagen der Pfad. Die Attrappe speichert vom Sprechtoken nur RICHTIG/FALSCH und vom
Text nur die Laenge und ob er in der Adresse stand - nie Token oder Text.

Geprueft je Lauf: jede Erwartung (Stand, Kennung, Dauer), dass Token und Ansagetext in
keiner Ausgabe, in keiner Datei <art>_letzte.json und in keiner Adresse an Alexa/Google
stehen, dass keiner Weiterleitung gefolgt wurde, und dass PHP keine Meldung ausgab
(error_reporting=-1). Mit curl zusaetzlich: ein Proxy aus der Umgebung wird nicht benutzt.
Rueckgabe 1, wenn eine Erwartung verfehlt ist.
"""
import http.server
import json
import os
import shutil
import socket
import socketserver
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8')
HIER = Path(__file__).resolve().parent
MODUL = HIER / 'gemeinsam' / 'sprachausgabe.php'
TEXTE = HIER / 'gemeinsam' / 'sprachausgabe_texte.json'
TREIBER = HIER / 'sprachausgabe_probe_treiber.php'
PHPS = {'74': Path(r'C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe'),
        '84': Path(r'C:\tmp\php-8.4.27-Win32-vs17-x64\php.exe'),
        '85': Path(r'C:\tmp\php-8.5.12-Win32-vs17-x64\php.exe')}
TMP = Path(r'C:\tmp\sprachmodul_probe')
A_TOK = 'ProbeAlexa0123456789abcd'
G_TOK = '0f1e2d3c4b5a69788796a5b4c3d2e1f0'
FALSCH = 'FalschesToken987654321zz'
TEXT = 'Probesatz Zitrone: morgen ist Feiertag.'
GEHEIM = (A_TOK, G_TOK, FALSCH, 'Zitrone', 'Zitrone'.encode('utf-8').hex())

args = sys.argv[1:]
if '--modul' in args:
    MODUL = Path(args[args.index('--modul') + 1]).resolve()
NUR = args[args.index('--nur') + 1].split(',') if '--nur' in args else None
AUSGABE = Path(args[args.index('--ausgabe') + 1]).resolve() if '--ausgabe' in args else None

ANFRAGEN = {}           # Lauf -> Liste der Aufzeichnungen
SPERRE = threading.Lock()


def frei():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    p = s.getsockname()[1]
    s.close()
    return p


class Attrappe(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'

    def log_message(self, *a):
        pass

    def merken(self, **w):
        lauf = (self.headers.get('User-Agent') or '').rpartition(' ')[2]
        w['pfad'] = urllib.parse.urlsplit(self.path).path
        w['token_in_adresse'] = any(g in self.path for g in (A_TOK, G_TOK, FALSCH))
        w['text_in_adresse'] = 'Zitrone' in urllib.parse.unquote(self.path)
        with SPERRE:
            ANFRAGEN.setdefault(lauf, []).append(w)

    def senden(self, code, rumpf, kopf=None, stocken=0, fehlt=0):
        b = rumpf.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        for k, v in (kopf or {}).items():
            self.send_header(k, v)
        self.send_header('Content-Length', str(len(b) + (100 if stocken else 0) + fehlt))
        self.end_headers()
        self.wfile.write(b)
        self.wfile.flush()
        if stocken:
            time.sleep(stocken)

    def do_GET(self):
        u = urllib.parse.urlsplit(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path.startswith('/audio/grouped/tts/'):
            teile = u.path.split('/')
            lang = urllib.parse.unquote(teile[-1]).split('|')[0] if len(teile) > 5 else ''
            self.merken(art='musicserver', fall=lang, zonen=teile[4] if len(teile) > 4 else '')
            fall = {'ok': (200, '{"ok":1}'), 'zu': (401, 'nein'), 'nf': (404, 'nicht da'), 'fe': (500, 'kaputt'),
                    'um': (302, '')}.get(lang)
            if lang == 'la':
                time.sleep(12)
                return self.senden(200, 'spaet')
            if lang == 'um':
                return self.senden(302, '', {'Location': '/ziel'})
            return self.senden(*(fall or (400, 'unbekannt')))
        if u.path == '/tts':
            self.merken(art='ms4h', fall='ok', zonen=(q.get('zone') or [''])[0], vol=(q.get('vol') or [''])[0])
            return self.senden(200, 'OK')
        if u.path.startswith('/eigen/'):
            fall = u.path[len('/eigen/'):]
            self.merken(art='custom', fall=fall)
            return self.senden(204 if fall == 'ok' else 404, '')
        if u.path == '/ziel':
            self.merken(art='ziel', fall='')
            return self.senden(200, 'SPRECHEN;OK=1;GRUND=ZIEL')
        self.merken(art='?', fall='')
        return self.senden(404, '<html>nicht da</html>')

    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0)
        f = urllib.parse.parse_qs(self.rfile.read(n).decode('utf-8', 'replace'), keep_blank_values=True)
        w = {k: v[0] for k, v in f.items()}
        u = urllib.parse.urlsplit(self.path)
        if u.path == '/plugins/alexang/index.php':
            art, soll, kopf = 'alexa', A_TOK, 'SPRECHEN'
        elif u.path == '/plugins/chromecast-4lox-ng/index.php':
            art, soll, kopf = 'google', G_TOK, 'SPRECHEN'
        elif u.path.endswith('/ziel'):
            self.merken(art='ziel', fall='')
            return self.senden(200, 'SPRECHEN;OK=1;GRUND=ZIEL')
        else:
            self.merken(art='?', fall='')
            return self.senden(404, '<html>nicht da</html>')
        tok = w.get('token')
        richtig = 'fehlt' if tok is None else ('RICHTIG' if tok == soll else 'FALSCH')
        fall = w.get('geraet', '(standard)')
        self.merken(art=art, fall=fall, felder=sorted(w), token=richtig, textlaenge=len(w.get('text', '')),
                    laut=w.get('laut', ''), selftest=w.get('selftest', ''))
        if w.get('selftest') == '1':
            if richtig != 'RICHTIG':
                return self.senden(403, 'SELFTEST;OK=0;GRUND=TOKEN')
            return self.senden(200, 'SELFTEST;OK=1;TOKEN=OK;SPRECHEN=1;DIENST=1;GRUND=-')
        if richtig != 'RICHTIG':
            return self.senden(403, kopf + ';OK=0;GRUND=TOKEN')
        if fall == '404ohne':
            return self.senden(404, '<html><body>Not Found</body></html>')
        if fall == '404mit':
            return self.senden(404, kopf + ';OK=0;GRUND=GERAET_UNBEKANNT;NAME=Bad')
        if fall == 'kaputt':
            return self.senden(200, '<html>\x07kaputt</html>')
        if fall == '503':
            return self.senden(503, kopf + ';OK=0;GRUND=DIENST_LAEUFT_NICHT')
        if fall == 'echo':
            return self.senden(403, kopf + ';OK=0;GRUND=TOKEN;ECHO=' + tok)
        if fall == 'umleitung':
            return self.senden(302, '', {'Location': u.path.rsplit('/', 1)[0] + '/ziel'})
        if fall == 'langsam':
            time.sleep(12)
            return self.senden(200, kopf + ';OK=1;GRUND=SPAET')
        if fall == 'stockt':
            return self.senden(200, kopf + ';OK=1;GRUND=STOCKT', stocken=12)
        if fall == 'kurz':
            return self.senden(200, kopf + ';OK=1;GRUND=KURZ', fehlt=100)
        return self.senden(200, kopf + ';OK=1;GERAETE=1;UNVERAENDERT=0;GRUND=EINGEREIHT')


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def handle_error(self, request, client_address):
        # Ein Aufrufer, der nach seiner Zeitgrenze auflegt, ist in den Faellen langsam/stockt gewollt.
        if not isinstance(sys.exc_info()[1], (ConnectionAbortedError, ConnectionResetError, BrokenPipeError)):
            super().handle_error(request, client_address)


def faelle(port, zu, ordner, texte):
    A = {'mode': 'alexang', 'alexa_token': A_TOK, 'alexa_laut': 30}
    G = {'mode': 'cc4lox', 'google_token': G_TOK, 'google_laut': -1}
    M = {'mode': 'musicserver', 'ip': '127.0.0.1', 'port': port, 'zones': '1', 'volume': 8}
    adr_a = 'http://127.0.0.1:%d/plugins/alexang/index.php' % port
    adr_g = 'http://127.0.0.1:%d/plugins/chromecast-4lox-ng/index.php' % port
    L = []

    def f(name, fn, tts, soll, text=TEXT, p=port, **x):
        d = {'name': name, 'fn': fn, 'tts': tts, 'text': text, 'port': p, 'ordner': ordner, 'soll': soll}
        d.update(x)
        L.append(d)

    f('a_ok', 'sprechen', dict(A, alexa_geraet='ok'), {'stand': 1, 'kennung': '', 'http': 200})
    f('a_falsch', 'sprechen', dict(A, alexa_geraet='ok', alexa_token=FALSCH), {'stand': 0, 'kennung': 'ALEXA_ANTWORT|403|TOKEN'})
    f('a_404ohne', 'sprechen', dict(A, alexa_geraet='404ohne'), {'stand': 0, 'kennung': 'ALEXA_FEHLT|%s|404' % adr_a})
    f('a_404mit', 'sprechen', dict(A, alexa_geraet='404mit'), {'stand': 0, 'kennung': 'ALEXA_ANTWORT|404|GERAET_UNBEKANNT'})
    f('a_kaputt', 'sprechen', dict(A, alexa_geraet='kaputt'), {'stand': 0, 'kennung': 'ALEXA_UNERWARTET|200|htmlkaputthtml'})
    f('a_503', 'sprechen', dict(A, alexa_geraet='503'), {'stand': 0, 'kennung': 'ALEXA_ANTWORT|503|DIENST_LAEUFT_NICHT'})
    f('a_echo', 'sprechen', dict(A, alexa_geraet='echo'), {'stand': 0, 'zeile': 'SPRECHEN;OK=0;GRUND=TOKEN;ECHO=***'})
    f('a_umleitung', 'sprechen', dict(A, alexa_geraet='umleitung'), {'stand': 0, 'kennung': 'ALEXA_UNERWARTET|302|-'})
    f('a_langsam', 'sprechen', dict(A, alexa_geraet='langsam'),
      {'stand': 0, 'kennung': 'ALEXA_KEINE_ANTWORT|%s|10|HTTP_ZEIT' % adr_a, 'ms': (9000, 11800)})
    f('a_stockt', 'sprechen', dict(A, alexa_geraet='stockt'),
      {'stand': 0, 'kennung': 'ALEXA_KEINE_ANTWORT|%s|10|HTTP_ZEIT' % adr_a, 'ms': (9000, 11800)})
    f('a_kurz', 'sprechen', dict(A, alexa_geraet='kurz'),
      {'stand': 0, 'kennung_beginnt': 'ALEXA_KEINE_ANTWORT|%s|10|' % adr_a, 'ms': (0, 4000)})
    f('a_abgewiesen', 'sprechen', dict(A, alexa_geraet='ok'),
      {'stand': 0, 'kennung': 'ALEXA_KEINE_ANTWORT|http://127.0.0.1:%d/plugins/alexang/index.php|10|HTTP_ABGEWIESEN' % zu,
       'ms': (0, 4000)}, p=zu)
    f('a_satz', 'sprechen', dict(A, alexa_geraet='503'),
      {'satz': 'Alexa-NG hat abgewiesen: HTTP 503, GRUND=DIENST_LAEUFT_NICHT'}, texte=texte)
    f('g_ok', 'sprechen', dict(G, google_geraet='ok'), {'stand': 1, 'kennung': '', 'http': 200})
    f('g_falsch', 'sprechen', dict(G, google_geraet='ok', google_token=FALSCH), {'stand': 0, 'kennung': 'GOOGLE_ANTWORT|403|TOKEN|GOOGLE_G_TOKEN'}, texte=texte)
    f('g_404ohne', 'sprechen', dict(G, google_geraet='404ohne'), {'stand': 0, 'kennung': 'GOOGLE_FEHLT|%s|404' % adr_g})
    f('g_ohne_token', 'sprechen', dict(G, google_token=''), {'stand': 0, 'kennung': 'GOOGLE_KEIN_TOKEN', 'anfragen': 0})
    f('g_selbsttest', 'selbsttest', dict(G), {'stand': 1, 'kennung': ''})
    f('g_selbsttest_falsch', 'selbsttest', dict(G, google_token=FALSCH), {'stand': 0, 'kennung': 'GOOGLE_ANTWORT|403|TOKEN'})
    f('g_cli', 'cli', dict(G, google_geraet='ok'), {'cli': [0, 'ANSAGE;STAND=1;ART=cc4lox;KENNUNG=-;HTTP=200;ZEICHEN=39']})
    # nach einer gelungenen Ansage (g_cli): Haken, und die letzte Ansage steht dabei
    f('g_pruefzeile', 'pruefzeile', dict(G), {'r0': 1, 'r1_beginnt': 'Chromecast 4 Lox NG antwortet unter %s' % adr_g}, texte=texte)
    f('g_rufen_2s', 'rufen', dict(G, google_geraet='langsam'), {'code': 0, 'grund_id': 'HTTP_ZEIT', 'ms': (1500, 3800)},
      text=TEXT, tmo=2)
    f('t_leer', 'sprechen', dict(A, alexa_geraet='ok'), {'stand': -1, 'kennung': 'TEXT_LEER', 'anfragen': 0}, text=' ')
    f('t_zu_lang', 'sprechen', dict(A, alexa_geraet='ok'), {'stand': 0, 'kennung': 'TEXT_ZU_LANG|1000', 'anfragen': 0},
      text='Zitrone ' * 130)
    f('t_steuer', 'sprechen', dict(A, alexa_geraet='ok'), {'stand': 0, 'kennung': 'TEXT_STEUERZEICHEN', 'anfragen': 0},
      text='Zitrone\nzwei')
    f('m_ok', 'sprechen', dict(M, lang='ok'), {'stand': 1, 'kennung': '', 'http': 200})
    f('m_401', 'sprechen', dict(M, lang='zu'), {'stand': 0, 'kennung': 'HTTP_ZUGANG|401'})
    f('m_404', 'sprechen', dict(M, lang='nf'), {'stand': 0, 'kennung': 'HTTP_404'})
    f('m_500', 'sprechen', dict(M, lang='fe'), {'stand': 0, 'kennung': 'HTTP_GEGENSEITE|500'})
    f('m_302', 'sprechen', dict(M, lang='um'), {'stand': 0, 'kennung': 'HTTP_WEITERLEITUNG|302'})
    f('m_langsam', 'sprechen', dict(M, lang='la'), {'stand': 0, 'kennung': 'HTTP_ZEIT', 'ms': (9000, 11800)})
    f('m_abgewiesen', 'sprechen', dict(M, lang='ok', port=zu), {'stand': 0, 'kennung': 'HTTP_ABGEWIESEN', 'ms': (0, 4000)})
    f('m_ms4h', 'sprechen', dict(M, mode='ms4h', zones='2, 3'), {'stand': 1, 'kennung': ''})
    f('m_eigen_ok', 'sprechen', dict(M, mode='custom', template='http://127.0.0.1:%d/eigen/ok?t={text}' % port),
      {'stand': 1, 'kennung': '', 'http': 204})
    f('m_eigen_404', 'sprechen', dict(M, mode='custom', template='http://127.0.0.1:%d/eigen/nf?t={text}' % port),
      {'stand': 0, 'kennung': 'HTTP_404'})
    f('m_extern', 'sprechen', dict(M, ip='8.8.8.8', lang='ok'), {'stand': 0, 'kennung': 'EINSTELLUNG|TTS_IP', 'anfragen': 0})
    f('schluessel', 'schluessel', {}, {'schluessel': sorted(texte)})
    return L


def pruefen(fall, zeile, anfr):
    """Liste der verfehlten Erwartungen eines Falls."""
    s = fall['soll']
    r = zeile.get('r')
    aus = []
    if fall['fn'] == 'schluessel':
        if sorted(r) != s['schluessel']:
            aus.append('Schluessel Modul %d gegen Textdatei %d, verschieden: %s' % (
                len(r), len(s['schluessel']), sorted(set(r) ^ set(s['schluessel']))[:5]))
        return aus
    if fall['fn'] == 'cli':
        if r != s['cli']:
            aus.append('cli %r' % (r,))
        return aus
    if fall['fn'] == 'pruefzeile':
        if r[0] != s['r0'] or not r[1].startswith(s['r1_beginnt']):
            aus.append('pruefzeile %r' % (r,))
        return aus
    for k in ('stand', 'kennung', 'http', 'zeile', 'satz', 'code', 'grund_id'):
        if k in s and r.get(k) != s[k]:
            aus.append('%s ist %r, soll %r' % (k, r.get(k), s[k]))
    if 'kennung_beginnt' in s and not str(r.get('kennung')).startswith(s['kennung_beginnt']):
        aus.append('kennung %r beginnt nicht mit %r' % (r.get('kennung'), s['kennung_beginnt']))
    if 'ms' in s and not (s['ms'][0] <= zeile['ms'] <= s['ms'][1]):
        aus.append('Dauer %d ms ausserhalb %r' % (zeile['ms'], s['ms']))
    if 'anfragen' in s and len(anfr) != s['anfragen']:
        aus.append('%d Anfragen, soll %d' % (len(anfr), s['anfragen']))
    return aus


def lauf(pv, curl, port, zu, texte, proxy=False):
    name = pv + ('c' if curl else '') + ('p' if proxy else '')
    ordner = TMP / ('letzte_' + name)
    ordner.mkdir(parents=True)
    php = PHPS[pv]
    cmd = [str(php), '-n', '-d', 'error_reporting=-1', '-d', 'display_errors=stderr', '-d', 'log_errors=0',
           '-d', 'default_socket_timeout=60']
    if curl:
        cmd += ['-d', 'extension_dir=' + str(php.parent / 'ext'), '-d', 'extension=curl']
    cmd += [str(TREIBER), str(MODUL)]
    env = {'SYSTEMROOT': os.environ.get('SYSTEMROOT', r'C:\Windows'), 'PATH': str(php.parent) + ';' + r'C:\Windows\system32'}
    if proxy:
        for k in ('http_proxy', 'HTTP_PROXY', 'all_proxy', 'ALL_PROXY'):
            env[k] = 'http://127.0.0.1:%d' % zu
    fl = faelle(port, zu, str(ordner), texte)
    if proxy:
        fl = [x for x in fl if x['name'] in ('a_ok', 'g_ok', 'm_ok')]
    for x in fl:
        # Lauf und Fall im User-Agent: die Attrappe ordnet jede Anfrage damit genau einem Fall zu
        x['ua'] = name + '_' + x['name']
    t0 = time.time()
    ergebnisse = []
    for x in fl:
        env1 = dict(env)
        p = subprocess.run(cmd, input=json.dumps([{k: v for k, v in x.items() if k != 'soll'}]).encode('utf-8'),
                           capture_output=True, env=env1, timeout=120)
        ergebnisse.append((x, p))
    return name, ordner, ergebnisse, time.time() - t0


def kein_endpunkt(pv):
    """php -S mit einer Abschrift im Dokumentenordner: direkter Aufruf -> 403, eingebunden -> 200."""
    d = TMP / ('web_' + pv)
    d.mkdir(parents=True)
    shutil.copy2(MODUL, d / 'sprachausgabe.php')
    (d / 'nachbar.php').write_text("<?php\nrequire __DIR__ . '/sprachausgabe.php';\n"
                                   "echo 'EINGEBUNDEN;FASSUNG=', ANSAGE_FASSUNG, \"\\n\";\n", encoding='utf-8')
    port = frei()
    pr = subprocess.Popen([str(PHPS[pv]), '-n', '-d', 'error_reporting=-1', '-d', 'display_errors=1',
                           '-S', '127.0.0.1:%d' % port, '-t', str(d)],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                socket.create_connection(('127.0.0.1', port), timeout=0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        erg = []
        for pfad in ('/sprachausgabe.php', '/sprachausgabe.php?aktion=x', '/nachbar.php'):
            try:
                r = urllib.request.urlopen('http://127.0.0.1:%d%s' % (port, pfad), timeout=10)
                erg.append((pfad, r.status, r.read().decode('utf-8', 'replace').strip()))
            except urllib.error.HTTPError as f:
                erg.append((pfad, f.code, f.read().decode('utf-8', 'replace').strip()))
    finally:
        pr.kill()           # nur der eigene, gemerkte Prozess
        pr.wait(timeout=10)
    soll = [('/sprachausgabe.php', 403, 'ANSAGE;OK=0;GRUND=KEIN_ENDPUNKT'),
            ('/sprachausgabe.php?aktion=x', 403, 'ANSAGE;OK=0;GRUND=KEIN_ENDPUNKT')]
    ok = erg[:2] == soll and erg[2][1] == 200 and erg[2][2].startswith('EINGEBUNDEN;FASSUNG=')
    return ok, erg


def doppelt(pv):
    """Zwei Abschriften im selben Prozess, wie Abfahrts-Assistent (eigene Abschrift) + ferien_lib.php
    (Abschrift von Ferien): erwartet rc 0 und die zuerst geladene gilt."""
    d = TMP / ('doppelt_' + pv)
    for u in ('a', 'b'):
        (d / u).mkdir(parents=True)
        shutil.copy2(MODUL, d / u / 'sprachausgabe.php')
    (d / 'b' / 'ferien_lib.php').write_text("<?php\nrequire_once __DIR__ . '/sprachausgabe.php';\n", encoding='utf-8')
    (d / 'a' / 'einstieg.php').write_text(
        "<?php\nrequire_once __DIR__ . '/sprachausgabe.php';\nrequire_once dirname(__DIR__) . '/b/ferien_lib.php';\n"
        "$r = new ReflectionFunction('ansage_sprechen');\necho 'GELADEN;AUS=', basename(dirname($r->getFileName())), \"\\n\";\n",
        encoding='utf-8')
    r = subprocess.run([str(PHPS[pv]), '-n', '-d', 'error_reporting=-1', '-d', 'display_errors=1', str(d / 'a' / 'einstieg.php')],
                       capture_output=True, timeout=60)
    o = (r.stdout + r.stderr).decode('utf-8', 'replace').strip()
    return r.returncode == 0 and o == 'GELADEN;AUS=a', 'rc %d %s' % (r.returncode, o.replace(str(d), '<tmp>')[:160])


def main():
    if TMP.exists():
        if not str(TMP).startswith('C:\\tmp\\sprachmodul_'):
            sys.exit('ABBRUCH: Pfad unerwartet')
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    texte = json.loads(TEXTE.read_bytes().decode('utf-8'))['de']
    zu = frei()     # geschlossener Port fuer "Verbindung abgewiesen" und den Proxy
    srv = Server(('127.0.0.1', 0), Attrappe)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    laeufe = [(pv, c, False) for pv in ('74', '84', '85') for c in (False, True)] + [('85', True, True), ('74', True, True)]
    if NUR:
        laeufe = [l for l in laeufe if (l[0] + ('c' if l[1] else '') + ('p' if l[2] else '')) in NUR]
    gesamt_fehl = 0
    zusammen = ['# Probe sprachausgabe.php gegen Attrappen (Modul %s, md5 %s)' % (
        MODUL.name, __import__('hashlib').md5(MODUL.read_bytes()).hexdigest())]
    faden = []
    ergebnis = {}

    def los(l):
        ergebnis[l] = lauf(l[0], l[1], port, zu, texte, l[2])

    for l in laeufe:
        t = threading.Thread(target=los, args=(l,))
        t.start()
        faden.append(t)
    for t in faden:
        t.join()
    for l in laeufe:
        name, ordner, erg, dauer = ergebnis[l]
        aus = ['== Lauf %s (PHP %s, %s%s), %.1f s' % (name, l[0], 'curl' if l[1] else 'Datenstrom',
                                                       ', Proxy aus der Umgebung gesetzt' if l[2] else '', dauer)]
        fehl = 0
        alle = []
        meldungen = 0
        geheim = 0
        weg = '?'
        for x, p in erg:
            out = p.stdout.decode('utf-8', 'replace')
            err = p.stderr.decode('utf-8', 'replace')
            meldungen += len([z for z in err.splitlines() if z.strip()])
            if any(g in out or g in err for g in GEHEIM):
                geheim += 1
                aus.append('  !! %s: Token oder Text in der Ausgabe' % x['name'])
            zeilen = [json.loads(z) for z in out.splitlines() if z.startswith('{')]
            z = [y for y in zeilen if y.get('name') == x['name']]
            w = [y for y in zeilen if y.get('name') == '_weg']
            if w:
                weg = w[0]['r']
            if not z:
                fehl += 1
                aus.append('  FEHL %s: keine Ausgabe (rc %d, stderr %r)' % (x['name'], p.returncode, err[:200]))
                continue
            z = z[0]
            # Anfragen dieses Falls: Lauf + Fall ueber die Ausgabe nicht trennbar, daher je Fall
            # ein eigener Prozess und die Aufzeichnung wird hier abgeholt und geleert.
            with SPERRE:
                anfr = ANFRAGEN.pop(name + '_' + x['name'], [])
            alle.extend(anfr)
            v = pruefen(x, z, anfr)
            r = z['r']
            kurz = r.get('kurz') if isinstance(r, dict) else None
            aus.append('  %-20s %s  %5d ms  %s' % (x['name'], 'ok  ' if not v else 'FEHL',
                                                  z['ms'], kurz or json.dumps(r, ensure_ascii=False)[:150]))
            for e in v:
                aus.append('      -> ' + e)
            fehl += 1 if v else 0
        # Anfragen an der Attrappe (alle Faelle dieses Laufs)
        tia = sum(1 for a in alle if a.get('token_in_adresse'))
        ziel = sum(1 for a in alle if a.get('art') == 'ziel')
        ng_text = sum(1 for a in alle if a.get('art') in ('alexa', 'google') and a.get('text_in_adresse'))
        ms_text = sum(1 for a in alle if a.get('art') == 'musicserver' and a.get('text_in_adresse'))
        aus.append('  Attrappe: %d Anfragen; Token in einer Adresse: %d; Text in einer Adresse an Alexa/Google: %d; '
                   'Music Server mit Text in der Adresse (gewollt): %d; Weiterleitung gefolgt: %d' % (
                       len(alle), tia, ng_text, ms_text, ziel))
        felder = sorted(set(tuple(a.get('felder', [])) for a in alle if a.get('art') in ('alexa', 'google')))
        aus.append('  Felder an Alexa/Google: %s' % felder)
        if tia or ng_text or ziel:
            fehl += 1
        letzte = sorted(ordner.iterdir())
        lt = [f.name for f in letzte]
        lg = sum(1 for f in letzte if any(g in f.read_bytes().decode('utf-8', 'replace') for g in GEHEIM))
        aus.append('  <art>_letzte.json: %s; mit Token oder Text: %d' % (lt, lg))
        if not lt or lg:
            fehl += 1
        aus.append('  Transportweg: %s (soll %s); PHP-Meldungen: %d; Ausgaben mit Token/Text: %d' % (
            weg, 'curl' if l[1] else 'datenstrom', meldungen, geheim))
        if weg != ('curl' if l[1] else 'datenstrom') or meldungen or geheim:
            fehl += 1
        aus.append('  Ergebnis Lauf %s: %s' % (name, 'alle Erwartungen erfuellt' if not fehl else '%d verfehlt' % fehl))
        gesamt_fehl += fehl
        if AUSGABE:
            (AUSGABE / ('probe_%s.txt' % name)).write_bytes(('\n'.join(aus) + '\n').encode('utf-8'))
        zusammen.append(aus[0] + ' -> ' + aus[-1].split(': ', 1)[1])
    srv.shutdown()
    srv.server_close()
    for pv in sorted(set(l[0] for l in laeufe)):
        ok, erg = kein_endpunkt(pv)
        zusammen.append('== PHP %s, php -S: %s -> %s' % (pv, '; '.join('%s %d %s' % e for e in erg),
                                                       'kein Endpunkt, wie erwartet' if ok else 'NICHT WIE ERWARTET'))
        gesamt_fehl += 0 if ok else 1
        ok, z = doppelt(pv)
        zusammen.append('== PHP %s, zwei Abschriften in einem Prozess: %s -> %s' % (pv, z, 'wie erwartet' if ok else 'NICHT WIE ERWARTET'))
        gesamt_fehl += 0 if ok else 1
    shutil.rmtree(TMP)
    zusammen.append('Gesamt: %d Laeufe, %d verfehlte Erwartungen' % (len(laeufe), gesamt_fehl))
    print('\n'.join(zusammen))
    if AUSGABE:
        (AUSGABE / 'probe_zusammenfassung.txt').write_bytes(('\n'.join(zusammen) + '\n').encode('utf-8'))
    return 1 if gesamt_fehl or not laeufe else 0


sys.exit(main())
