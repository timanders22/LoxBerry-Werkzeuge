#!/usr/bin/env python3
"""Den Midea2Lox-Dienst wirklich starten - ohne Klimageraet.

WAS DAS MISST UND WAS NICHT

msmart-ng und paho sind auf dem Entwicklungsrechner nicht installiert, und
ein Klimageraet gibt es nicht. Dieses Stueck schiebt deshalb ATTRAPPEN fuer
msmart, paho und requests in sys.modules und startet den Dienst damit
wirklich. Gemessen werden die Wege, die OHNE Geraet erreichbar sind:

  * bindet der Dienst seinen UDP-Port?
  * ueberlebt er ein Paket, das kein UTF-8 ist?          (Befund P1)
  * schreibt er ein Lebenszeichen?                        (V6)
  * laeuft der Abfragetakt an?                            (V5)
  * bricht er bei unvollstaendiger Konfiguration mit
    LESBARER Meldung und Rueckgabewert 1 ab?              (Befund P7)
  * stimmt der Hin- und Rueckweg der Luefterstufen?       (Befund P11)

NICHT gemessen wird alles, was ein echtes Geraet braucht: authenticate(),
refresh(), apply(), die Faehigkeitsabfrage und die tatsaechlichen Werte. Eine
Attrappe wird gegen das Geraet gebaut - diese hier ist es NICHT, sie bildet
nur so viel nach, dass der Dienst anlaeuft. Was daran gruen ist, sagt ueber
das Geraet nichts.

Aufruf: mi_dienstprobe.py <plugin-ordner> <arbeitsordner>
"""
import os
import socket
import subprocess
import sys
import textwrap
import time

P = os.path.abspath(sys.argv[1])
ARB = os.path.abspath(sys.argv[2])
befunde = []


def melde(bez, gut, text=''):
    print('  %-46s %-6s %s' % (bez, 'ok' if gut else 'BEFUND', text))
    if not gut:
        befunde.append(bez)


def baue_umgebung():
    """Die Platzhalter des Dienstes durch echte Pfade ersetzen."""
    for name in ('config', 'log', 'data', 'bin'):
        os.makedirs(os.path.join(ARB, name), exist_ok=True)
    quelle = open(os.path.join(P, 'data', 'midea2lox.py'), 'rb').read()
    for platz, wert in (
            (b'REPLACELBPCONFIGDIR', os.path.join(ARB, 'config').encode()),
            (b'REPLACELBPLOGDIR', os.path.join(ARB, 'log').encode()),
            (b'REPLACELBHOMEDIR', ARB.encode()),
            (b'REPLACELBPDATADIR', os.path.join(ARB, 'data').encode())):
        quelle = quelle.replace(platz, wert.replace(b'\\', b'/'))
    # Die Shebang-Zeile zeigt auf ein venv, das es hier nicht gibt.
    quelle = b'#!/usr/bin/env python3\n' + quelle.split(b'\n', 1)[1]
    ziel = os.path.join(ARB, 'data', 'midea2lox.py')
    open(ziel, 'wb').write(quelle)
    return ziel


ATTRAPPEN = textwrap.dedent('''
    """Attrappen fuer msmart, paho und requests - NUR so viel, dass der
    Dienst anlaeuft. Sie bilden KEIN Geraet nach."""
    import enum, sys, types

    def modul(name):
        m = types.ModuleType(name)
        sys.modules[name] = m
        return m

    msmart = modul('msmart'); msmart.__version__ = '0.0.0-attrappe'
    dev = modul('msmart.device')

    class _E(enum.Enum):
        pass

    class OperationalMode(enum.Enum):
        AUTO = 1; COOL = 2; HEAT = 3; DRY = 4; FAN_ONLY = 5

    class FanSpeed(enum.Enum):
        AUTO = 102; MAX = 100; HIGH = 80; MEDIUM = 60; LOW = 40; SILENT = 20

    class SwingMode(enum.Enum):
        OFF = 0; VERTICAL = 12; HORIZONTAL = 3; BOTH = 15

    class SwingAngle(enum.Enum):
        OFF = 0; POS_1 = 1; POS_2 = 2

    class AirConditioner:
        OperationalMode = OperationalMode
        FanSpeed = FanSpeed
        SwingMode = SwingMode
        SwingAngle = SwingAngle
        def __init__(self, ip=None, device_id=None, port=None):
            self.id = int(device_id or 0); self.ip = ip; self._online = False
        def set_max_connection_lifetime(self, n): pass
        async def authenticate(self, t, k): pass
        async def get_capabilities(self): pass
        async def refresh(self): self._online = False
        async def apply(self): self._online = False
        @property
        def online(self): return self._online
    dev.AirConditioner = AirConditioner

    disc = modul('msmart.discover')
    class Discover:
        @classmethod
        async def discover(cls, **kw): return []
    disc.Discover = Discover

    paho = modul('paho'); modul('paho.mqtt')
    mc = modul('paho.mqtt.client')
    class Client:
        def __init__(self, *a, **kw): pass
        def username_pw_set(self, *a): pass
        def will_set(self, *a, **kw): pass
        def connect(self, *a, **kw): raise OSError('kein Broker (Attrappe)')
        def loop_start(self): pass
    mc.Client = Client

    req = modul('requests')
    class _Ex(Exception): pass
    req.exceptions = types.SimpleNamespace(Timeout=_Ex, RequestException=_Ex)
    def _get(*a, **kw):
        raise req.exceptions.RequestException('kein Miniserver (Attrappe)')
    req.get = _get
''')


def starte(ziel, extra_pfad, dauer=6):
    vorlauf = os.path.join(ARB, 'attrappen.py')
    open(vorlauf, 'w', encoding='utf-8').write(ATTRAPPEN)
    umg = dict(os.environ)
    umg['PYTHONPATH'] = ARB + os.pathsep + umg.get('PYTHONPATH', '')
    umg['PYTHONDONTWRITEBYTECODE'] = '1'
    starter = os.path.join(ARB, 'starte.py')
    open(starter, 'w', encoding='utf-8').write(
        'import attrappen, runpy, sys\n'
        'sys.argv = ["midea2lox.py"]\n'
        'runpy.run_path(%r, run_name="__main__")\n' % ziel)
    p = subprocess.Popen([sys.executable, starter], env=umg, cwd=ARB,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p


def cfg_schreiben(zeilen):
    open(os.path.join(ARB, 'config', 'midea2lox.cfg'), 'w',
         encoding='utf-8').write(zeilen)


def general_cfg(ms='MINISERVER1'):
    os.makedirs(os.path.join(ARB, 'config', 'system'), exist_ok=True)
    open(os.path.join(ARB, 'config', 'system', 'general.cfg'), 'w',
         encoding='utf-8').write(
        '[%s]\nIPADDRESS=192.168.1.1\nPORT=80\nADMIN=admin\nPASS=geheim\n' % ms)


def log_lesen():
    p = os.path.join(ARB, 'log', 'midea2lox.log')
    return open(p, encoding='utf-8', errors='replace').read() if os.path.isfile(p) else ''


ziel = baue_umgebung()
general_cfg()

print('== Fall 1: unvollstaendige Konfiguration ==')
cfg_schreiben('[default]\nDEBUG=0\n')
if os.path.isfile(os.path.join(ARB, 'log', 'midea2lox.log')):
    os.remove(os.path.join(ARB, 'log', 'midea2lox.log'))
p = starte(ziel, ARB)
aus = p.communicate(timeout=30)[0].decode('utf-8', 'replace')
melde('bricht ab', p.returncode != 0, 'Rueckgabewert %s' % p.returncode)
melde('Rueckgabewert ist 1, nicht 0', p.returncode == 1, str(p.returncode))
melde('nennt den Grund im Klartext', 'unvollstaendig' in aus or 'unvollstaendig' in log_lesen(),
      aus.strip().splitlines()[-1] if aus.strip() else '(keine Ausgabe)')
melde('keine SystemExit-Spur im Protokoll', 'SystemExit' not in log_lesen())

print('\n== Fall 2: Miniserver fehlt in der general.cfg ==')
cfg_schreiben('[default]\nMINISERVER=MINISERVER9\nUDP_PORT=7013\nLoxberryIP=127.0.0.1\nDEBUG=0\n')
p = starte(ziel, ARB)
aus = p.communicate(timeout=30)[0].decode('utf-8', 'replace')
melde('bricht ab mit Rueckgabewert 1', p.returncode == 1, str(p.returncode))
melde('nennt den Miniserver', 'MINISERVER9' in aus or 'MINISERVER9' in log_lesen(),
      aus.strip().splitlines()[-1] if aus.strip() else '')

print('\n== Fall 3: Dienst laeuft, Herzschlag, kaputtes Paket ==')
port = 0
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]
cfg_schreiben('[default]\nMINISERVER=MINISERVER1\nUDP_PORT=%d\nLoxberryIP=127.0.0.1\n'
              'DEBUG=1\nmaxConnectionLifetime=90\nmqtt_praefix=Midea2Lox\n'
              'abfragetakt=30\nlox_timeout=5\n' % port)
leben = os.path.join(ARB, 'data', 'lebenszeichen.json')
if os.path.isfile(leben):
    os.remove(leben)
if os.path.isfile(os.path.join(ARB, 'log', 'midea2lox.log')):
    os.remove(os.path.join(ARB, 'log', 'midea2lox.log'))
p = starte(ziel, ARB)
try:
    zeit = time.time()
    gebunden = False
    while time.time() - zeit < 20:
        if 'Socket bind complete' in log_lesen():
            gebunden = True
            break
        time.sleep(0.3)
    melde('bindet den UDP-Port', gebunden, 'Port %d' % port)

    c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    c.sendto(b'123456789012 status', ('127.0.0.1', port))
    time.sleep(0.6)
    c.sendto(b'\xff\xfe kaputt', ('127.0.0.1', port))       # Befund P1
    time.sleep(0.6)
    c.sendto(b'123456789012 power.True', ('127.0.0.1', port))
    time.sleep(1.5)
    melde('lebt nach dem nicht-UTF-8-Paket noch', p.poll() is None,
          'Rueckgabewert %s' % p.poll())
    l = log_lesen()
    melde('meldet das verworfene Paket', 'kein UTF-8' in l)
    melde('verarbeitet das Paket DANACH weiter',
          l.count('Incomming Message from Loxone') >= 2,
          '%d Pakete angenommen' % l.count('Incomming Message from Loxone'))

    zeit = time.time()
    while time.time() - zeit < 20 and not os.path.isfile(leben):
        time.sleep(0.3)
    melde('schreibt ein Lebenszeichen', os.path.isfile(leben))
    if os.path.isfile(leben):
        import json
        d = json.load(open(leben, encoding='utf-8'))
        melde('Lebenszeichen traegt ts, zaehler, ok',
              all(k in d for k in ('ts', 'zaehler', 'ok')), str(d))
    melde('meldet den eingeschalteten Abfragetakt', 'Abfragetakt eingeschaltet' in l)
    melde('MQTT-Ausfall wird gemeldet, nicht verschwiegen',
          'MQTT nicht verfuegbar' in l)
finally:
    p.terminate()
    try:
        p.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        p.kill()

print('\n== Fall 4: Luefterstufen hin und zurueck ==')
umg = dict(os.environ); umg['PYTHONPATH'] = ARB; umg['PYTHONDONTWRITEBYTECODE'] = '1'
pruef = os.path.join(ARB, 'stufen.py')
open(pruef, 'w', encoding='utf-8').write(
    'import attrappen, runpy, sys\n'
    'sys.argv=["x"]\n'
    'g = runpy.run_path(%r)\n'
    'tab, rueck = g["mi_tabellen"](), g["mi_rueck"]\n'
    'fehl = 0\n'
    'for gruppe in ("operational_mode", "fan_speed", "swing_mode"):\n'
    '    for wort, name in tab[gruppe].items():\n'
    '        zurueck = rueck(gruppe).get(name)\n'
    '        erwartet = wort.rsplit(".", 1)[1]\n'
    '        if zurueck != erwartet:\n'
    '            print("   ABWEICHUNG %%s: %%s -> %%s -> %%s" %% (gruppe, wort, name, zurueck)); fehl += 1\n'
    'print("   %%d Zuordnungen geprueft, %%d Abweichung(en)" %% (\n'
    '    sum(len(tab[g2]) for g2 in tab), fehl))\n'
    'sys.exit(1 if fehl else 0)\n' % ziel)
r = subprocess.run([sys.executable, pruef], env=umg, cwd=ARB,
                   capture_output=True, text=True)
print(r.stdout.rstrip())
melde('Hin- und Rueckweg deckungsgleich', r.returncode == 0)

print('\n%s' % ('%d BEFUND(E): %s' % (len(befunde), ', '.join(befunde))
                if befunde else 'Alle Dienstproben bestanden.'))
sys.exit(1 if befunde else 0)
