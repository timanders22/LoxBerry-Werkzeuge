"""Pruefstand fuer Bibliothek, Dienst und Endpunkte des Abfahrts-Assistenten.

Wegwerf-LoxBerry in Installationslage, eigene general.json mit einem
UDP-Eingang, an dem dieser Pruefstand selbst horcht. Jede Zeile nennt die
Erwartung. Aufruf: python abf_kernprobe.py PLUGINORDNER PHP.EXE MARKE

Entstanden 16.09.2026 beim Umbau auf 1.6.10. Geeicht in beide Richtungen:
1.6.10 47/47 (PHP 7.4 und 8.4), veroeffentlichte 1.6.9 18/47. Arbeitsbaum im
Systemtemp (abf_kern_<MARKE>), dazu C:/tmp/abfkern_<MARKE> und C:/tmp/abfahrtsassistent.
Die Pruefzeilen sind fuer andere Linien eine Bauvorlage: Datumspruefung,
Wertpruefung mit Kontrollfaellen, Dienst gegen einen eigenen UDP-Horcher
(Retain je Feld, Lebenszeichen nie retained, Marke nur bei Erfolg).

16.10.2026 (Welle Bild 13 Nachzug): Zeile "Retain je Feld" auf Regeln/07 umgestellt -
seit 1.6.13 geht kein Feld retained hinaus (abfahrt_felder(), Element [4] = 0;
Entscheidungen 18./19./24.09.2026). Bis dahin erwartete die Zeile OK und FEHLER
retained (Eichstand 1.6.10) und meldete ab 1.6.13 46/47. Neu geeicht (PHP 7.4/8.4/8.5):
1.6.28 und Bau 1.6.28 (Nachzug) 47/47; Gegenprobe 1.6.12, PHP 8.4 (OK/FEHLER noch retained) 46/47 an dieser Zeile.
"""
import json
import os
import re
import shutil
import tempfile
import socket
import subprocess
import sys
import threading
import time
import xml.dom.minidom
from pathlib import Path

# Werkzeugordner: LOXWERK/Werkzeuge, sonst der Ordner dieser Datei.
WERK = (Path(os.environ['LOXWERK'], 'Werkzeuge') if os.environ.get('LOXWERK')
        else Path(os.path.abspath(__file__)).parent)
PLUGIN = Path(sys.argv[1]).resolve()
PHP = sys.argv[2]
MARKE = sys.argv[3]
ORD = "abfahrtsassistent"
W = Path(tempfile.gettempdir()) / ("abf_kern_" + MARKE)   # nie neben dem Skript: Werkzeuge/ bleibt sauber
TMPW = Path("C:/tmp/abfkern_" + MARKE)
erg = []


def zeile(ok, text, messung):
    erg.append(ok)
    print(("[OK]  " if ok else "[FEHL]") + " " + text + "  ->  " + str(messung)[:160])


def baue(udpport):
    if W.exists():
        shutil.rmtree(W)
    shutil.copytree(WERK / "lb_attrappe", W)
    for unter, q in (("webfrontend/html/plugins/" + ORD, "webfrontend/html"),
                     ("webfrontend/htmlauth/plugins/" + ORD, "webfrontend/htmlauth"),
                     ("templates/plugins/" + ORD, "templates"), ("bin/plugins/" + ORD, "bin")):
        (W / unter).parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(PLUGIN / q, W / unter)
    for u in ("config/plugins/" + ORD, "data/plugins/" + ORD, "log/plugins/" + ORD):
        (W / u).mkdir(parents=True, exist_ok=True)
    g = W / "config/system/general.json"
    d = json.loads(g.read_text(encoding="utf-8")) if g.is_file() else {}
    d.setdefault("Mqtt", {})
    d["Mqtt"].update({"Udpinport": str(udpport), "Gatewayautostart": 1, "Gatewayversion": 1})
    g.parent.mkdir(parents=True, exist_ok=True)
    g.write_text(json.dumps(d), encoding="utf-8")
    cfg = {"provider": "tomtom", "api_key": "K", "home_address": "Musterweg 1, Kassel",
           "calendars": [{"name": "A", "url": "https://example.invalid/a.ics"}],
           "aktionstoken": "MERKWORT", "mqtt_ein": 1, "mqtt_topic": "abfahrt", "mqtt_vollsend_min": 15}
    (W / "config/plugins" / ORD / "abfahrt.json").write_text(json.dumps(cfg), encoding="utf-8")
    if TMPW.exists():
        shutil.rmtree(TMPW)
    TMPW.mkdir(parents=True)


def php(args, umg_extra=None, eingabe=None):
    umg = dict(os.environ)
    umg.update({"LBHOMEDIR": str(W), "LBPPLUGINDIR": ORD})
    if umg_extra:
        umg.update(umg_extra)
    r = subprocess.run([PHP, "-n", "-d", "include_path=.;" + str(W / "libs/phplib"),
                        "-d", "display_errors=1", "-d", "error_reporting=32767",
                        "-d", "date.timezone=Europe/Berlin", "-d", "sys_temp_dir=" + str(TMPW).replace("\\", "/"),
                        "-d", "extension_dir=" + str(Path(PHP).parent / "ext"), "-d", "extension=curl",
                        "-d", "extension=sockets"] + args,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=umg, timeout=120,
                       cwd=str(W))
    return r.returncode, r.stdout, r.stderr


class Horcher:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(("127.0.0.1", 0))
        self.port = self.s.getsockname()[1]
        self.s.settimeout(0.3)
        self.zeilen = []
        self.an = True
        self.t = threading.Thread(target=self.lauf, daemon=True)
        self.t.start()

    def lauf(self):
        while self.an:
            try:
                d, _ = self.s.recvfrom(65535)
                self.zeilen += d.decode("utf-8", "replace").splitlines()
            except socket.timeout:
                pass

    def nimm(self, warten=1.5):
        time.sleep(warten)
        z, self.zeilen = self.zeilen, []
        return z


def schreibe_php(name, code):
    p = W / name
    p.write_text(code, encoding="utf-8")
    return str(p)


LIB = lambda: str(W / "webfrontend/html/plugins" / ORD / "abfahrt_lib.php").replace("\\", "/")
DIENST = lambda: str(W / "bin/plugins" / ORD / "abfahrt_dienst.php")


def main():
    h = Horcher()
    baue(h.port)
    tmpdir = Path("/tmp/" + ORD)  # unter Windows loest PHP /tmp zu C:\tmp auf
    wtmp = Path("C:/tmp/" + ORD)
    if wtmp.exists():
        shutil.rmtree(wtmp)

    # ---------------- Datumspruefung (G3)
    code = "<?php require '" + LIB() + "';\n" + r"""
foreach (['20261301T000000','20260230T100000','20260931T100000','20261301T000000Z','20260230T100000Z','20260906T100000','20260906T100000Z'] as $r) {
  $t = abfahrt_dt2ts($r, 'Europe/Berlin'); echo $r, '=', $t === null ? 'null' : date('Y-m-d H:i', $t), "\n"; }
$t = abfahrt_dt2ts('20261301', 'Europe/Berlin', '08:00'); echo 'GANZTAG13=', $t === null ? 'null' : date('Y-m-d H:i', $t), "\n";
$t = abfahrt_dt2ts('20260906', 'Europe/Berlin', '08:00'); echo 'GANZTAG_OK=', $t === null ? 'null' : date('Y-m-d H:i', $t), "\n";
"""
    rc, out, err = php([schreibe_php("p_datum.php", code)])
    werte = dict(l.split("=", 1) for l in out.strip().splitlines() if "=" in l)
    for k in ("20261301T000000", "20260230T100000", "20260931T100000", "20261301T000000Z", "20260230T100000Z", "GANZTAG13"):
        zeile(werte.get(k) == "null", f"unmoegliches Datum {k} verworfen", werte.get(k))
    zeile(werte.get("20260906T100000") == "2026-09-06 10:00", "gueltiges Datum (Kontrollfall)", werte.get("20260906T100000"))
    zeile(werte.get("20260906T100000Z", "null") != "null", "gueltiges Datum mit Z (Kontrollfall)", werte.get("20260906T100000Z"))
    zeile(werte.get("GANZTAG_OK") == "2026-09-06 08:00", "Ganztag gueltig (Kontrollfall)", werte.get("GANZTAG_OK"))

    # ---------------- Wertpruefung (G2), Token als Feld (G22)
    code = "<?php require '" + LIB() + "';\n" + r"""
$f = [
 ['quiet', [1 => ['on'=>1,'from'=>'XX','to'=>'YY']]],
 ['tts', ['mode'=>'custom','template'=>'http://fremd.example/x?t={text}']],
 ['tts', ['mode'=>'custom','template'=>'file:///etc/passwd?{text}']],
 ['tts', ['port'=>999999]],
 ['tts', ['ip'=>'8.8.8.8']],
 ['notify', ['audio'=>1,'boese'=>1]],
 ['ortsbuch', [['muster'=>'Buero','adresse'=>'']]],
 ['arrival_min', -999],
 ['tts', ['mode'=>'musicserver','ip'=>'192.168.1.11','port'=>7091,'zones'=>'1,2,3,4,5,6','volume'=>8,'lang'=>'de','template'=>'']],
 ['quiet', [1 => ['on'=>1,'from'=>'20:00','to'=>'07:00'], '10' => ['on'=>0,'from'=>'20:00','to'=>'09:00']]],
 ['tts', ['mode'=>'ms4h','template'=>'http://{ip}:{port}/tts?text={text}']],
 ['notify', ['audio'=>1,'push'=>0]],
];
foreach ($f as $i => $x) { $g=''; $w = abfahrt_wert_pruefen($x[0], $x[1], $g); echo $i, '=', $w === null ? 'ABGEWIESEN' : 'ANGENOMMEN', "\n"; }
$_GET['token'] = ['x']; $c = abfahrt_vorgaben(); $c['aktionstoken'] = 'ABC';
echo 'TOKENFELD=', var_export(abfahrt_token_ok($c), true), "\n";
$_GET['token'] = 'ABC'; echo 'TOKENGUT=', var_export(abfahrt_token_ok($c), true), "\n";
echo 'HTTPFILE=', var_export(abfahrt_http_get('file:///C:/Windows/win.ini'), true), "\n";
"""
    rc, out, err = php([schreibe_php("p_wert.php", code)])
    w = dict(l.split("=", 1) for l in out.strip().splitlines() if "=" in l)
    namen = ["quiet XX-YY", "tts fremder Rechner", "tts file://", "tts port 999999", "tts ip 8.8.8.8",
             "notify unbekannter Eintrag", "ortsbuch halbe Zeile", "arrival_min -999"]
    for i, n in enumerate(namen):
        zeile(w.get(str(i)) == "ABGEWIESEN", "abgewiesen: " + n, w.get(str(i)))
    for i, n in ((8, "tts wie am Geraet"), (9, "quiet gueltig"), (10, "tts ms4h-Vorlage mit {ip}"), (11, "notify gueltig")):
        zeile(w.get(str(i)) == "ANGENOMMEN", "angenommen (Kontrollfall): " + n, w.get(str(i)))
    zeile(w.get("TOKENFELD") == "false" and "Array to string" not in out + err, "token[]=x: false, keine Warnung", (w.get("TOKENFELD"), "Array to string" in out + err))
    zeile(w.get("TOKENGUT") == "true", "richtiges Merkwort (Kontrollfall)", w.get("TOKENGUT"))
    zeile(w.get("HTTPFILE") == "false", "file:// wird nicht abgerufen", w.get("HTTPFILE"))

    # ---------------- Endpunkt: Antwortform, nichts anlegen (G10, G18)
    endp = str(W / "webfrontend/html/plugins" / ORD / "termin.php")
    if wtmp.exists():
        shutil.rmtree(wtmp)
    vor = sorted(p.name for p in TMPW.iterdir())
    rc, out, err = php([endp], {"REQUEST_METHOD": "GET"})
    nach = sorted(p.name for p in TMPW.iterdir())
    zeile(out.strip().startswith("TERMIN;OK="), "termin.php liefert die Statuszeile", out.strip()[:60])
    zeile(vor == nach and not wtmp.exists(), "anonymer GET legt nichts an (Systemtemp und Zwischenordner)", (vor, nach, wtmp.exists()))
    code = "<?php $_GET = ['debug'=>'1','token'=>'falsch']; $_SERVER['REMOTE_ADDR']='192.168.1.9'; require '" + endp.replace("\\", "/") + "';"
    rc, out, err = php([schreibe_php("p_abw.php", code)])
    zeile("ERR=TOKEN" in out and "GRUND=TOKEN" in out, "Abweisung traegt ERR= und GRUND=", out.strip()[:60])

    # ---------------- Dienst: Selbsttest, Lebenszeichen, ALTER nicht ueber MQTT, Retain
    rc, out, err = php([DIENST(), "--selbsttest"])
    zeile("[OK]   PHP" in out, "Selbsttest laeuft", out.count("[OK]"))
    h.nimm(0.2)
    rc, out, err = php([DIENST(), "jetzt"])
    z = h.nimm(2.5)
    zeile(rc == 0, "Dienst jetzt rc=0", (rc, err.strip()[:80]))
    themen = [l.split(" ")[:2] for l in z]
    befehle = {t[1]: t[0] for t in themen if len(t) == 2}
    zeile(all(k in befehle for k in ("abfahrt/status/ts", "abfahrt/status/zaehler", "abfahrt/status/ok")), "Lebenszeichen: drei Themen gesendet", sorted(k for k in befehle if "status" in k))
    zeile(all(befehle.get(k) == "publish" for k in befehle if "status" in k), "Lebenszeichen nie retained", {k: v for k, v in befehle.items() if "status" in k})
    zeile("abfahrt/ALTER" not in befehle, "ALTER geht nicht ueber MQTT", "abfahrt/ALTER" in befehle)
    # Regeln/07 (seit 1.6.13): kein Feld retained - OK/FEHLER/AUDIO/PUSH sind Dienst- bzw. Zeitbezug-Aussagen.
    felder = {k: v for k, v in befehle.items() if "status" not in k}
    zeile(all(befehle.get(k) == "publish" for k in ("abfahrt/OK", "abfahrt/FEHLER", "abfahrt/MINSTART"))
          and all(v == "publish" for v in felder.values()),
          "Retain je Feld: kein Feld retained (Regeln/07)", {k: befehle.get(k) for k in ("abfahrt/OK", "abfahrt/FEHLER", "abfahrt/MINSTART")})
    zeile(len([k for k in befehle if "status" not in k]) == 8, "Vollversand beim ersten Lauf: 8 Felder", len([k for k in befehle if "status" not in k]))
    # zweiter Lauf: nur Lebenszeichen
    rc, out, err = php([DIENST(), "jetzt"])
    z2 = h.nimm(2.0)
    t2 = sorted(l.split(" ")[1] for l in z2 if len(l.split(" ")) > 1)
    zeile(t2 == ["abfahrt/status/ok", "abfahrt/status/ts", "abfahrt/status/zaehler"], "zweiter Lauf ohne Aenderung: nur das Lebenszeichen", t2)
    # Takt nicht faellig: Lebenszeichen trotzdem
    rc, out, err = php([DIENST()])
    z3 = h.nimm(2.0)
    zeile(len(z3) == 3, "Lauf ohne Rechnen sendet trotzdem das Lebenszeichen", len(z3))
    # Stand: FEHLER=8 (Kalender nicht lesbar - example.invalid)
    st = json.loads((wtmp / "stand.json").read_text(encoding="utf-8")) if (wtmp / "stand.json").is_file() else {}
    zeile(st.get("fehler") == 8 and st.get("ok") == 0, "kein Kalender lesbar -> FEHLER=8, OK=0", (st.get("fehler"), st.get("ok")))
    # MQTT nicht erreichbar -> Merker bleibt
    merk = wtmp / "mqtt_letzte.json"
    m_vor = merk.read_bytes() if merk.is_file() else b""
    g = W / "config/system/general.json"
    gd = json.loads(g.read_text()); gd["Mqtt"]["Udpinport"] = "0"; g.write_text(json.dumps(gd))
    (wtmp / "stand.json").unlink()
    (wtmp / "mqtt_voll.stamp").unlink() if (wtmp / "mqtt_voll.stamp").exists() else None
    rc, out, err = php([DIENST(), "jetzt"])
    m_nach = merk.read_bytes() if merk.is_file() else b""
    zeile(not (wtmp / "mqtt_voll.stamp").exists(), "ohne UDP-Eingang: Vollversand-Marke NICHT gesetzt", (wtmp / "mqtt_voll.stamp").exists())
    gd["Mqtt"]["Udpinport"] = str(h.port); g.write_text(json.dumps(gd))
    # cron.err-Frage gehoert zum Cron-Skript: Inhalt pruefen
    cron = (PLUGIN / "cron/cron.01min").read_text(encoding="utf-8")
    zeile('touch "REPLACELBPLOGDIR/cron.err"' in cron and all("REPLACELB" not in l for l in cron.splitlines() if l.startswith("#")) and cron.count("REPLACELB") == 4, "Cron fasst cron.err an; REPLACELB nur in Befehlszeilen", cron.count("REPLACELB"))

    # ---------------- termin_say: keine Ansage ohne gueltigen Termin
    say = str(W / "webfrontend/html/plugins" / ORD / "termin_say.php").replace("\\", "/")
    code = "<?php $_GET = ['token'=>'MERKWORT']; require '" + say + "';"
    rc, out, err = php([schreibe_php("p_say.php", code)])
    zeile(out.startswith("SKIP: kein gueltiger Termin"), "termin_say ohne gueltigen Termin: SKIP", out.strip()[:60])

    # ---------------- Vorlage
    code = "<?php require '" + LIB() + "'; $v = abfahrt_vorlage('loxberry'); file_put_contents('" + str(W / "vorlage.xml").replace("\\", "/") + "', $v[1]); echo 'OK';"
    rc, out, err = php([schreibe_php("p_vorlage.php", code)])
    x = (W / "vorlage.xml").read_bytes()
    try:
        dom = xml.dom.minidom.parseString(x); wohl = True
    except Exception as e:
        wohl = False
    zeile(wohl, "Vorlage wohlgeformt", len(x))
    txt = x.decode("utf-8")
    cmds = re.findall(r"<VirtualInHttpCmd ([^>]*)/>", txt)
    zeile(len(cmds) == 9, "9 Befehle", len(cmds))
    zeile(txt.startswith('<?xml version="1.0" encoding="utf-8"?>\r\n<VirtualInHttp HintText=""') and '\t<Info templateType="2" minVersion="17010727"/>\r\n' in txt,
          "HintText als erstes Wurzelattribut, Info als erstes Kind", txt[:80])
    ohne_unit = [c for c in cmds if "Unit=" not in c]
    zeile(not ohne_unit, "jeder Befehl traegt Unit", len(ohne_unit))
    lang = [re.search(r'Comment="([^"]*)"', c).group(1) for c in cmds]
    zeile(max(len(xml.dom.minidom.parseString('<a x="%s"/>' % l).documentElement.getAttribute('x')) for l in lang) <= 40, "Kachelnamen hoechstens 40 Zeichen", max(len(l) for l in lang))
    zeile(txt.count("\r\n") == txt.count("\n") and "ueberschreibt" not in txt, "CRLF durchgehend, keine Umschrift", (txt.count("\r\n"), txt.count("\n")))
    zeile('DefVal="9999"' in txt and 'Unit="&lt;v.0&gt; min"' in txt, "Fehlwert als DefVal, Einheit min", 'DefVal="9999"' in txt)

    h.an = False
    print(f"== {sum(erg)} von {len(erg)} Zeilen erfuellt ==")
    return 0 if all(erg) else 1


if __name__ == "__main__":
    sys.exit(main())
