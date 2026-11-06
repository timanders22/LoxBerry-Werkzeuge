"""Netzsperre fuer Pruefwerkzeuge, die mit ECHTEN Bibliotheksobjekten arbeiten.

Anlass (11.09.2026, gemessen mit gesperrtem Netz und Zaehler):
  au_neuerungstest.py wollte 13 Mal ins Netz (nominatim.openstreetmap.org,
  pool.ntp.org), au_funktionstest.py 83 Mal - darunter identity.vwgroup.io,
  also eine echte Anmeldung am Audi-/VW-Konto mit den Pruefdaten
  "a@b.de"/"x". Der Kommentar dort sagte "ohne Netz scheitert die Anmeldung"
  - er ging davon aus, dass es kein Netz gibt. Auf diesem Rechner gibt es
  eines.

  carconnectivity 0.11.10 legt bei JEDEM CarConnectivity() einen
  OSMLocationService an (carconnectivity.py, Zeile 338). Sobald ein Fahrzeug
  im Pruefstand "laedt" und eine Position hat, fragt die Bibliothek bei
  Nominatim nach der Ladesaeule - auch noch beim Aufraeumen am Prozessende,
  aus einem __del__ heraus. Diese Anfrage mitten im Abbau des Interpreters
  endete unter Python 3.14 mit einer Zugriffsverletzung: au_neuerungstest.py
  meldete "130 bestanden, 0 durchgefallen" und gab trotzdem 139 zurueck.
  Mit gesperrtem Netz: Rueckgabewert 0.

Ein Pruefwerkzeug geht nicht nach aussen. Wer ein Werkzeug baut, das es
muss, schaltet diese Sperre nicht ein und sagt es im Kopf.

Gebrauch, gleich nach den eigenen Einstellungen des Werkzeugs:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import netzsperre
    netzsperre.einschalten()
    ...
    print(netzsperre.bericht())
"""

import socket

ABGEWIESEN = []
_AN = False


def _vermerken(ziel):
    ABGEWIESEN.append(str(ziel))


def einschalten():
    """Jede ausgehende Verbindung und jede Namensaufloesung wird abgewiesen."""
    global _AN
    if _AN:
        return

    def create_connection(adresse, *a, **k):
        _vermerken(adresse[0] if isinstance(adresse, tuple) else adresse)
        raise OSError(101, "Netz im Pruefwerkzeug gesperrt (netzsperre.py)")

    def connect(self, adresse):
        _vermerken(adresse[0] if isinstance(adresse, tuple) else adresse)
        raise OSError(101, "Netz im Pruefwerkzeug gesperrt (netzsperre.py)")

    def connect_ex(self, adresse):
        _vermerken(adresse[0] if isinstance(adresse, tuple) else adresse)
        return 101

    def getaddrinfo(host, *a, **k):
        _vermerken(host)
        raise socket.gaierror(-2, "Namensaufloesung im Pruefwerkzeug gesperrt (netzsperre.py)")

    socket.create_connection = create_connection
    socket.socket.connect = connect
    socket.socket.connect_ex = connect_ex
    socket.getaddrinfo = getaddrinfo
    _AN = True


def bericht():
    """Eine Zeile fuer das Ende der Ausgabe: wie oft, wohin."""
    ziele = sorted(set(ABGEWIESEN))
    return "Netz gesperrt: %d Verbindungsversuch(e) abgewiesen%s" % (
        len(ABGEWIESEN), (" (" + ", ".join(ziele[:6]) + ")") if ziele else "")
