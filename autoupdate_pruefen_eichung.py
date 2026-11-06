#!/usr/bin/env python3
"""Eichung fuer autoupdate_pruefen.py - in beide Richtungen.

Aufruf:  python3 autoupdate_pruefen_eichung.py [PFAD_AUF_autoupdate_pruefen.py]

Geeicht wird das ECHTE Werkzeug, nicht eine Abschrift: die Faelle werden als
Plugin-Ordner mit einer plugin.cfg gebaut und das Werkzeug darauf losgelassen.
Die Erwartung steht in FAELLE, also VOR dem Lauf.

Der Abruf zeigt auf einen kleinen Server im eigenen Rechner. Grund:
raw.githubusercontent.com ist aus der Arbeitsumgebung nicht immer erreichbar,
und ein Werkzeug, das dort nur schweigt, haette nichts gemessen. Der Zweigteil
geht weiterhin an das ECHTE Repositorium - deshalb tragen die Adressen einen
echten Repositoriumsnamen.

Sieben Faelle, letzter ohne Server: "nicht messbar" muss weder gruen (0) noch
Befund (1) heissen, sondern 2.

Anlass 08.09.2026: Pumpenwaechter 1.0.0. Der erste Lauf ergab 4 von 7 - alle
drei Abweichungen waren falsche ERWARTUNGEN, nicht Fehler des Werkzeugs. Eine
davon war ein echter Fund: eine leere Antwort von ls-remote heisst "Zweig
fehlt" ODER "Repositorium fehlt". Seither fragt das Werkzeug in diesem Zweig
ein zweites Mal nach und unterscheidet 'fehlt' von 'Repo?'.
"""
import http.server
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading

HIER = os.path.dirname(os.path.abspath(__file__))
WERK = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HIER, 'autoupdate_pruefen.py')
BAU = os.path.join(tempfile.gettempdir(), 'eichung_autoupdate')

VORLAGE = """[AUTHOR]
NAME=Eichung
EMAIL=eichung@users.noreply.github.com

[PLUGIN]
VERSION=%(v)s
NAME=eichung
FOLDER=eichung
TITLE=Eichung

[AUTOUPDATE]
AUTOMATIC_UPDATES=%(auto)s
RELEASECFG=%(rel)s
PRERELEASECFG=%(pre)s

[SYSTEM]
INTERFACE=2.0
"""

# Name, Ordner, auto, Pfad release, Pfad prerelease, Erwartung (Abruf, Zweig, Code)
FAELLE = [
    ('gut',        'LoxBerry-Plugin-Pumpenwacht-9.9.1', 'true',
     '/timanders22/LoxBerry-Plugin-Pumpenwacht/main/release.cfg',
     '/timanders22/LoxBerry-Plugin-Pumpenwacht/main/prerelease.cfg',
     ('200', 'da', 0)),
    ('eine404',    'LoxBerry-Plugin-Pumpenwacht-9.9.2', 'true',
     '/timanders22/LoxBerry-Plugin-Pumpenwacht/main/release.cfg',
     '/timanders22/LoxBerry-Plugin-Pumpenwacht/main/fehlt.cfg',
     ('200/404', 'da', 1)),
    ('beide404',   'LoxBerry-Plugin-Pumpenwacht-9.9.3', 'true',
     '/timanders22/LoxBerry-Plugin-Pumpenwacht/main/fehlt.cfg',
     '/timanders22/LoxBerry-Plugin-Pumpenwacht/main/fehlt2.cfg',
     ('404/404', 'da', 1)),
    ('umgeleitet', 'LoxBerry-Plugin-Pumpenwacht-9.9.4', 'true',
     '/timanders22/LoxBerry-Plugin-Pumpenwacht/master/release.cfg',
     '/timanders22/LoxBerry-Plugin-Pumpenwacht/master/prerelease.cfg',
     ('200', 'umgeleitet', 0)),
    ('autoaus',    'LoxBerry-Plugin-Pumpenwacht-9.9.5', 'false',
     '/timanders22/LoxBerry-Plugin-Pumpenwacht/main/release.cfg',
     '/timanders22/LoxBerry-Plugin-Pumpenwacht/main/prerelease.cfg',
     ('200', 'da', 1)),
    ('fremd',      'LoxBerry-Plugin-Pumpenwacht-9.9.6', 'true',
     '/timanders22/LoxBerry-Plugin-Fremd/main/release.cfg',
     '/timanders22/LoxBerry-Plugin-Fremd/main/prerelease.cfg',
     ('200', 'Repo?', 1)),
]

DA = ('/timanders22/LoxBerry-Plugin-Pumpenwacht/main/release.cfg',
      '/timanders22/LoxBerry-Plugin-Pumpenwacht/main/prerelease.cfg',
      '/timanders22/LoxBerry-Plugin-Pumpenwacht/master/release.cfg',
      '/timanders22/LoxBerry-Plugin-Pumpenwacht/master/prerelease.cfg',
      '/timanders22/LoxBerry-Plugin-Fremd/main/release.cfg',
      '/timanders22/LoxBerry-Plugin-Fremd/main/prerelease.cfg')


class Hand(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in DA:
            leib = b'[AUTOUPDATE]\nVERSION=9.9.9\n'
            self.send_response(200)
            self.send_header('Content-Length', str(len(leib)))
            self.end_headers()
            self.wfile.write(leib)
        else:
            self.send_response(404)
            self.send_header('Content-Length', '0')
            self.end_headers()

    def log_message(self, *a):
        pass


def frei():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    p = s.getsockname()[1]
    s.close()
    return p


def bauen(port):
    shutil.rmtree(BAU, ignore_errors=True)
    os.makedirs(BAU)
    for name, ordner, auto, rel, pre, _ in FAELLE:
        os.makedirs(os.path.join(BAU, ordner))
        werte = {'v': ordner.rsplit('-', 1)[1], 'auto': auto,
                 'rel': 'http://127.0.0.1:%d%s' % (port, rel),
                 'pre': 'http://127.0.0.1:%d%s' % (port, pre)}
        with open(os.path.join(BAU, ordner, 'plugin.cfg'), 'w',
                  encoding='utf-8') as f:
            f.write(VORLAGE % werte)


def lauf(ordner):
    r = subprocess.run([sys.executable, WERK, '--fern', ordner],
                       cwd=BAU, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    return r.returncode, r.stdout or ''


def spalten(aus):
    zeile = [z for z in aus.split('\n') if z.startswith('Pumpenwacht')]
    teile = zeile[0].split() if zeile else ['?', '?', '?', '?', '?']
    return teile[-2], teile[-1]


port = frei()
srv = http.server.HTTPServer(('127.0.0.1', port), Hand)
threading.Thread(target=srv.serve_forever, daemon=True).start()
bauen(port)

print('%-12s %-24s %-24s %s' % ('Fall', 'erwartet', 'gemessen', 'Urteil'))
print('-' * 78)
schlecht = 0
for name, ordner, auto, rel, pre, (e_ab, e_zw, e_c) in FAELLE:
    code, aus = lauf(ordner)
    g_ab, g_zw = spalten(aus)
    ok = (g_ab, g_zw, code) == (e_ab, e_zw, e_c)
    schlecht += 0 if ok else 1
    print('%-12s %-24s %-24s %s'
          % (name, '%s %s rc=%d' % (e_ab, e_zw, e_c),
             '%s %s rc=%d' % (g_ab, g_zw, code), 'gut' if ok else 'ABWEICHUNG'))

# Siebter Fall: der Server ist aus.
srv.shutdown()
code, aus = lauf(FAELLE[0][1])
g_ab, _ = spalten(aus)
ok = (g_ab, code) == ('?', 2)
schlecht += 0 if ok else 1
print('%-12s %-24s %-24s %s' % ('kein Netz', '? rc=2', '%s rc=%d' % (g_ab, code),
                                'gut' if ok else 'ABWEICHUNG'))
print('-' * 78)
print('%d von %d Faellen wie erwartet, %d Abweichungen.'
      % (len(FAELLE) + 1 - schlecht, len(FAELLE) + 1, schlecht))
shutil.rmtree(BAU, ignore_errors=True)
sys.exit(1 if schlecht else 0)
