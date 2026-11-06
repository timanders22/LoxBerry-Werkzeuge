#!/usr/bin/env python3
"""Zaehlt, wie oft ein Python-Pruefwerkzeug ins Netz will - und laesst es nicht.

Anlass (11.09.2026): au_neuerungstest.py gab nach "0 durchgefallen" den
Rueckgabewert 139 zurueck. Mit diesem Zaehler zeigte sich die Ursache:
13 Verbindungsversuche (Nominatim, Zeitserver), bei au_funktionstest.py 83,
darunter eine echte Anmeldung an identity.vwgroup.io. Behoben mit
netzsperre.py; dieser Zaehler ist die Gegenprobe - hinter einer eingebauten
Sperre sieht er 0 Versuche.

Aufruf:  python netz_zaehlen.py <werkzeug.py> [argumente ...]

Jede Verbindung und jede Namensaufloesung wird vermerkt und mit OSError
abgewiesen. Die Zeile "[netz_zaehlen] ..." steht am Ende auf stderr, noch
vor dem Abbau des Interpreters. Der Rueckgabewert ist der des Werkzeugs.
Rein lesend; kein PHP (dafuer hat rendern.py eine eigene Sperre).
"""
import os
import runpy
import socket
import sys

versuche = []


def _weg(adresse):
    versuche.append(adresse)
    raise OSError(101, "Netz im Pruefstand gesperrt (netz_zaehlen.py)")


def create_connection(adresse, *a, **k):
    return _weg(adresse)


def connect(self, adresse):
    return _weg(adresse)


def getaddrinfo(host, *a, **k):
    versuche.append(("dns", host))
    raise socket.gaierror(-2, "Namensaufloesung im Pruefstand gesperrt (netz_zaehlen.py)")


socket.create_connection = create_connection
socket.socket.connect = connect
socket.getaddrinfo = getaddrinfo

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(2)
werkzeug = sys.argv[1]
sys.argv = sys.argv[1:]
code = 0
try:
    runpy.run_path(werkzeug, run_name="__main__")
except SystemExit as e:
    code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
finally:
    ziele = sorted({str(v[1]) if isinstance(v, tuple) and v and v[0] == "dns" else str(v)
                    for v in versuche})
    sys.stderr.write("\n[netz_zaehlen] %s: %d Verbindungsversuche, Ziele: %s, Rueckgabe des "
                     "Werkzeugs: %s\n" % (os.path.basename(werkzeug), len(versuche), ziele[:6], code))
    sys.stderr.flush()
sys.exit(code)
