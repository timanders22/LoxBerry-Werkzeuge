#!/usr/bin/env python3
"""Rendert jede Plugin-Oberflaeche unter PHP 7.4 und 8.4 gegen die SDK-Attrappe.

Rein lesend fuer den Arbeitsordner: gearbeitet wird auf der Kopie unter stand/.

Aufruf:  rendern.py [<Verzeichnis mit Plugin-Ordnern> | <ein Plugin-Ordner>]
         ohne Argument: stand

SEIT 11.09.2026 (gemessen an AudiConnect 0.9.15):
  * Das Ergebnis steht in Werkzeuge/lb/render.json - nicht mehr im
    aktuellen Verzeichnis. Dort entstand es bis dahin neben jedem Aufruf:
    im Arbeitsordner (dort schon am 10.09. per Commit entfernt und wieder
    da), in Werkzeuge/, in Pruefordnern.
  * Am Ende steht immer eine Zeile mit der Zahl der gerenderten
    Oberflaechen und Laeufe. Bis dahin schwieg das Werkzeug bei sauberem
    Lauf - und genauso, wenn es gar nichts gefunden hatte.
  * Rueckgabewert: 0 ohne Befund, 1 mit Befund, 2 wenn nichts gerendert
    wurde. Vorher immer 0.
  * Ein einzelner Plugin-Ordner als Argument wird als EINE Linie mit ihrem
    Ordnernamen gerendert. Vorher hiess sie "webfrontend" - so stand es im
    Befund, und die Konfiguration landete unter config/plugins/webfrontend/.
  * Netzsperre: Plugin-Seiten, die beim Aufbau Daten holen, gehen nicht mehr
    nach aussen. file_get_contents & Co. faengt vorlauf.php ab (eigener
    Wrapper fuer http/https/ftp/ftps), curl ein Sperr-Proxy dieses Skripts
    (Umgebung http_proxy/https_proxy/all_proxy). Was abgewiesen wurde, steht
    in einem eigenen Block und zaehlt NICHT als Befund. Anlass: ein Lauf
    ueber den Bestand bekam von api.awattar.de "429 Too Many Requests".
    Nicht erfasst: rohe Sockets (fsockopen, stream_socket_client,
    socket_connect) - 25 Linien benutzen sie, meist fuer Geraete im Heimnetz.
    Wer mit gemessenem Netz rendern will, ruft lauf() ohne Sperre; die
    Werkzeuge, die lauf() einbinden, tun das bis heute.
"""
import os, re, subprocess, sys, json, socketserver, threading
from pathlib import Path
from urllib.parse import urlsplit

HIER = Path(__file__).resolve().parent
LB = HIER / 'lb'
VORLAUF = HIER / 'vorlauf.php'
PHPS = [('7.4', r'C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe'),
        ('8.4', r'C:\tmp\php-8.4.27-Win32-vs17-x64\php.exe')]


def oberflaechen(d):
    aus = []
    for name in ('index.php',):
        for f in d.rglob(name):
            if 'htmlauth' in str(f):
                aus.append(f)
    return aus


class Netzsperre:
    """Ein Proxy auf 127.0.0.1, der jede Anfrage mitschreibt und mit 403
    beantwortet. curl in PHP liest http_proxy/https_proxy/all_proxy aus der
    Umgebung - gemessen unter 7.4.33 und 8.4.24 am 11.09.2026 (mit gesetztem
    Proxy "over proxy 127.0.0.1", ohne ihn eine echte Verbindung zu
    example.com). Die Stroeme von file_get_contents & Co. faengt vorlauf.php
    ab; sie kommen ueber stderr zurueck und stehen danach in .stroeme."""

    def __init__(self):
        self.ziele = []
        self.stroeme = []
        sperre = self

        class Behandler(socketserver.BaseRequestHandler):
            def handle(self):
                try:
                    self.request.settimeout(5)
                    kopf = b''
                    while b'\r\n\r\n' not in kopf and len(kopf) < 65536:
                        teil = self.request.recv(4096)
                        if not teil:
                            break
                        kopf += teil
                    zeile = kopf.split(b'\r\n', 1)[0].decode('latin-1', 'replace')
                    teile = zeile.split()
                    sperre.ziele.append(teile[1] if len(teile) > 1 else zeile)
                    self.request.sendall(b'HTTP/1.1 403 Netz im Pruefstand gesperrt\r\n'
                                         b'Content-Length: 0\r\nConnection: close\r\n\r\n')
                except OSError:
                    pass

        socketserver.ThreadingTCPServer.daemon_threads = True
        self.server = socketserver.ThreadingTCPServer(('127.0.0.1', 0), Behandler)
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def umgebung(self, umg):
        # Unter Windows sind Umgebungsnamen gross/klein gleich - vorhandene
        # Schreibweisen erst entfernen, sonst stehen zwei im Block.
        for k in list(umg):
            if k.lower() in ('http_proxy', 'https_proxy', 'all_proxy', 'no_proxy'):
                del umg[k]
        adresse = 'http://127.0.0.1:%d' % self.port
        for k in ('http_proxy', 'https_proxy', 'all_proxy'):
            umg[k] = adresse
        umg['RENDERN_NETZSPERRE'] = '1'

    @staticmethod
    def wirt(ziel):
        if '://' in ziel:
            return urlsplit(ziel).hostname or ziel
        return ziel.rsplit(':', 1)[0]

    def ende(self):
        self.server.shutdown()
        self.server.server_close()


def attrappen_name(plugin):
    """Der Ordnername unter lb/{config,data,log,templates}/plugins/ - und LBPPLUGINDIR.

    SEIT 08.11.2026 nur noch a-z, 0-9, _ und -: alles andere wird _. Bis dahin
    stand hier plugin.lower(), und ein Direktaufruf auf den Arbeitsordner gab
    "loxberry-plugin-ankersolix-0.9.40" weiter. AnkerSolix nimmt nur
    [A-Za-z0-9_-]{1,64} an, arbeitete dann "nicht installiert" NEBEN sich und
    legte config/ankersolix.json im Pruefling an; der Wirkungstest verglich
    dabei eine leere Konfiguration in der Attrappe. Die Kette vergibt eigene
    Namen (KOPIENNAME, etwa "ankersolix") - fuer sie aendert sich nichts.
    """
    n = os.path.basename(str(plugin).replace('\\', '/').rstrip('/')).lower()
    return re.sub(r'[^a-z0-9_-]', '_', n)


def vorlagen_spiegel(datei, name):
    """templates/ des Pruefling nach lb/templates/plugins/<name> spiegeln - wie auf
    dem Geraet, wo LBPTEMPLATEDIR ein eigener Baum ist. Rueckgabe: der Spiegel.

    SEIT 08.11.2026. Vorher zeigte LBPTEMPLATEDIR in den Pruefling, und was ein
    Plugin dort ablegt, landete im Pruefling: Zigbee2MqttNG 4.2.12 seinen
    Twig-Zwischenspeicher (templates/cache/, zwei Dateien je Lauf). Der Spiegel
    wird bei jedem Lauf neu angelegt, damit er nie einen alten Stand zeigt.
    """
    import shutil
    quelle = (datei.parent.parent.parent / 'templates').resolve()
    ziel = LB / 'templates' / 'plugins' / name
    shutil.rmtree(ziel, ignore_errors=True)
    if ziel.exists():
        raise RuntimeError('Vorlagenspiegel nicht entfernbar: %s' % ziel)
    if quelle.is_dir():
        shutil.copytree(quelle, ziel)
    else:
        ziel.mkdir(parents=True, exist_ok=True)
    return ziel


def lauf(php, datei, plugin, sperre=None, unterdrueckt=None):
    """unterdrueckt: SEIT 25.09.2026. Eine Liste, in die lauf() die Meldungen
    legt, deren Stelle sie mit @ unterdrueckt hat - sie stehen dann NICHT
    unter den Befunden. Ohne Liste (Vorgabe, und so rufen gateway_wirkung.py,
    sicherung_wirkung.py und reiterlauf.py) zaehlt wie bisher jede Meldung als
    Befund. Anlass: Zendure 0.9.25/0.9.26, drei @fopen/@file_get_contents-
    Zeilen mit geprueftem Rueckgabewert, sieben Warnungen als Befund."""
    umg = dict(os.environ)
    umg.pop('RENDERN_UNTERDRUECKT', None)
    if unterdrueckt is not None:
        umg['RENDERN_UNTERDRUECKT'] = '1'
    # Kein __pycache__ im Prueflig: die Seite startet das Python des
    # Plugins, und dieses KIND schreibt sonst bin/__pycache__.
    # `python -B` vererbt sich nicht - nur die Umgebungsvariable tut es
    # (gemessen 13.09.2026 an Heimkino 1.3.9 und APC-UPS 1.2.8).
    umg['PYTHONDONTWRITEBYTECODE'] = '1'
    if sperre is not None:
        sperre.umgebung(umg)
    umg['LBHOMEDIR'] = str(LB)
    name = attrappen_name(plugin)
    umg['LBPPLUGINDIR'] = name
    umg['LBPCONFIGDIR'] = str(LB / 'config/plugins' / name)
    umg['LBPLOGDIR'] = str(LB / 'log/plugins' / name)
    umg['LBPDATADIR'] = str(LB / 'data/plugins' / name)
    umg['LBPHTMLAUTHDIR'] = str(datei.parent.resolve())
    umg['LBPHTMLDIR'] = str((datei.parent.parent / 'html').resolve())
    umg['LBPTEMPLATEDIR'] = str(vorlagen_spiegel(datei, name))
    umg['LBPBINDIR'] = str((datei.parent.parent.parent / 'bin').resolve())
    for k in ('LBPCONFIGDIR', 'LBPLOGDIR', 'LBPDATADIR'):
        Path(umg[k]).mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [php, '-n', '-d', 'include_path=.;' + str(LB / 'libs' / 'phplib'),
         '-d', 'auto_prepend_file=' + str(VORLAUF),
         '-d', 'display_errors=0', '-d', 'error_reporting=32767',
         '-d', 'date.timezone=Europe/Berlin',
         '-d', 'extension_dir=' + str(Path(php).parent / 'ext'),
         '-d', 'extension=curl', '-d', 'extension=openssl', '-d', 'extension=mbstring',
         '-d', 'extension=sockets', '-d', 'extension=fileinfo',
         str(datei.resolve())],
        capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=str(datei.parent.resolve()), env=umg, timeout=60)
    fehler = r.stderr
    # vorlauf.php schreibt ###UNTERDRUECKT### als letzten Block.
    if '###UNTERDRUECKT###' in fehler:
        fehler, u = fehler.split('###UNTERDRUECKT###', 1)
        if unterdrueckt is not None:
            unterdrueckt[:] = [z.strip() for z in u.strip().splitlines() if z.strip()]
    netz = []
    if '###NETZ###' in fehler:
        fehler, n = fehler.split('###NETZ###', 1)
        netz = [z.strip() for z in n.strip().splitlines() if z.strip()]
    if sperre is not None:
        sperre.stroeme = netz
    befunde = []
    if '###BEFUNDE###' in fehler:
        befunde = [z for z in fehler.split('###BEFUNDE###', 1)[1].strip().splitlines() if z.strip()]
    rest = fehler.split('###BEFUNDE###')[0].strip()
    return r.stdout, befunde, rest


if __name__ == '__main__':
    ziel = Path(sys.argv[1] if len(sys.argv) > 1 else 'stand')
    # Ein Plugin-Ordner selbst (er traegt webfrontend/) ist EINE Linie mit
    # seinem eigenen Namen; sonst ist jeder Unterordner eine.
    if (ziel / 'webfrontend').is_dir():
        ordner = [ziel.resolve()]
    else:
        ordner = [d for d in sorted(ziel.iterdir()) if d.is_dir()]
    ergebnis = {}
    netz = {}
    unterdrueckt = {}
    n_seiten = n_laeufe = n_netz = 0
    sperre = Netzsperre()
    for d in ordner:
        for datei in oberflaechen(d):
            n_seiten += 1
            for v, php in PHPS:
                if not Path(php).is_file():
                    continue
                n_laeufe += 1
                vorher = len(sperre.ziele)
                sperre.stroeme = []
                unt = []
                try:
                    out, bef, rest = lauf(php, datei, d.name, sperre, unt)
                    for z in unt:
                        unterdrueckt.setdefault(d.name, []).append((v, z))
                    abgewiesen = sperre.ziele[vorher:] + sperre.stroeme
                    if abgewiesen:
                        n_netz += len(abgewiesen)
                        netz.setdefault(d.name, set()).update(
                            Netzsperre.wirt(z) for z in abgewiesen)
                except subprocess.TimeoutExpired:
                    ergebnis.setdefault(d.name, []).append((v, 'ZEITUEBERSCHREITUNG', ''))
                    continue
                for b in bef:
                    ergebnis.setdefault(d.name, []).append((v, b, len(out)))
                if rest:
                    ergebnis.setdefault(d.name, []).append((v, 'STDERR|' + rest[:200], len(out)))
                if len(out) < 500:
                    ergebnis.setdefault(d.name, []).append((v, 'AUSGABE ZU KURZ (%d Zeichen)' % len(out), len(out)))
    ablage = LB / 'render.json'
    with open(ablage, 'w', encoding='utf-8') as f:
        json.dump({k: [list(map(str, x)) for x in v] for k, v in ergebnis.items()},
                  f, ensure_ascii=False, indent=1)
    for p in sorted(ergebnis):
        print('== ' + p)
        gesehen = set()
        for v, b, n in ergebnis[p]:
            k = (v, b)
            if k in gesehen:
                continue
            gesehen.add(k)
            print('   [%s] %s' % (v, b))
    sperre.ende()
    if netz:
        print('== Netzzugriffe beim Rendern - abgewiesen, nicht ausgefuehrt, kein Befund')
        for p in sorted(netz):
            print('   %s: %s' % (p, ', '.join(sorted(netz[p]))))
    # Seit 25.09.2026: Meldungen, die die Stelle selbst mit @ unterdrueckt,
    # stehen hier - nicht verschwiegen, aber kein Befund (Rueckgabewert und
    # "Linie(n) mit Befund" zaehlen sie nicht). Gezaehlt wie die Befunde:
    # je Linie jede Zeile einmal je PHP-Fassung.
    n_unt = 0
    if unterdrueckt:
        print('== Mit @ unterdrueckt - die Stelle unterdrueckt selbst, kein Befund')
        for p in sorted(unterdrueckt):
            zeilen = sorted(set(unterdrueckt[p]))
            n_unt += len(zeilen)
            print('   %s: unterdrueckt: %d' % (p, len(zeilen)))
            for v, b in zeilen:
                print('      [%s] %s' % (v, b))
    print('rendern.py: %d Oberflaeche(n) in %d Ordner(n), %d Laeufe, %d Linie(n) mit Befund, '
          '%d Linie(n) wollten ins Netz (%d Zugriffe abgewiesen), '
          'unterdrueckt: %d Meldung(en) in %d Linie(n) (kein Befund). Ergebnis: %s'
          % (n_seiten, len(ordner), n_laeufe, len(ergebnis), len(netz), n_netz,
             n_unt, len(unterdrueckt), ablage))
    if n_laeufe == 0:
        print('NICHTS GERENDERT - keine webfrontend/htmlauth/index.php gefunden oder kein PHP. '
              'Das ist kein sauberer Lauf.')
        sys.exit(2)
    sys.exit(1 if ergebnis else 0)
