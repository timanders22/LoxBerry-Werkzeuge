"""HTTP-Pruefstand fuer die Oberflaeche des Abfahrts-Assistenten.

Baut einen Wegwerf-LoxBerry (Werkzeuge/lb_attrappe) in Installationslage,
startet php -S und misst an echten HTTP-Antworten. Schreibt nur in den
Wegwerfbaum. Jede Zeile nennt Erwartung und Messung.

Aufruf: python abf_httpprobe.py PLUGINORDNER PHP.EXE MARKE

Entstanden 16.09.2026 beim Umbau auf 1.6.10. Geeicht: 1.6.10 34/34 (PHP 7.4
und 8.4), veroeffentlichte 1.6.9 10 von 32; die zwei Sperrzeiten-Zeilen gegen
eine mutierte Kopie rot. Bauvorlage fuer andere Linien: PRG (303, Einmalmeldung,
F5 wiederholt nichts), Formularmerkmal, Zurueckspielen gueltig/halb/fremd,
beschaedigte Konfiguration mit Zweitschrift. Arbeitsbaum im Systemtemp.
"""
import http.client
import json
import os
import re
import shutil
import tempfile
import socket
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

# Werkzeugordner: LOXWERK/Werkzeuge, sonst der Ordner dieser Datei.
WERK = (Path(os.environ['LOXWERK'], 'Werkzeuge') if os.environ.get('LOXWERK')
        else Path(os.path.abspath(__file__)).parent)
PLUGIN = Path(sys.argv[1]).resolve()
PHP = sys.argv[2]
MARKE = sys.argv[3]
ORD = "abfahrtsassistent"
WURZEL = Path(tempfile.gettempdir()) / ("abf_http_" + MARKE)   # nie neben dem Skript: Werkzeuge/ bleibt sauber

GUT = {
    "provider": "tomtom", "api_key": "SCHLUESSEL-KARTENDIENST", "home_address": "Musterweg 1, Kassel",
    "buffer_min": 12, "arrival_min": 10, "lookahead_hours": 15,
    "calendars": [{"name": "Arbeit", "url": "https://example.invalid/a.ics"}],
    "aktionstoken": "MERKWORT-DER-ANLAGE",
}

ergebnisse = []


def zeile(ok, text, messung):
    ergebnisse.append(ok)
    print(("[OK]  " if ok else "[FEHL]") + " " + text + "  ->  " + str(messung))


def baue():
    if WURZEL.exists():
        shutil.rmtree(WURZEL)
    shutil.copytree(WERK / "lb_attrappe", WURZEL)
    for unter, quelle in (("webfrontend/html/plugins/" + ORD, "webfrontend/html"),
                          ("webfrontend/htmlauth/plugins/" + ORD, "webfrontend/htmlauth"),
                          ("templates/plugins/" + ORD, "templates"),
                          ("bin/plugins/" + ORD, "bin")):
        z = WURZEL / unter
        z.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(PLUGIN / quelle, z)
    for unter in ("config/plugins/" + ORD, "data/plugins/" + ORD, "log/plugins/" + ORD, "system/cron/cron.01min"):
        (WURZEL / unter).mkdir(parents=True, exist_ok=True)


def freier_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


CFG = lambda: WURZEL / "config/plugins" / ORD / "abfahrt.json"
BAK = lambda: WURZEL / "config/plugins" / (ORD + ".backup.json")


def lies_cfg():
    try:
        return json.loads(CFG().read_text(encoding="utf-8"))
    except Exception:
        return None


class Server:
    def __enter__(self):
        self.port = freier_port()
        umg = dict(os.environ)
        umg.update({"LBHOMEDIR": str(WURZEL), "LBPPLUGINDIR": ORD})
        tmp = WURZEL / "phptmp"; tmp.mkdir(exist_ok=True)
        wurzel = WURZEL / "webfrontend/htmlauth/plugins" / ORD
        self.p = subprocess.Popen(
            [PHP, "-n", "-S", f"127.0.0.1:{self.port}", "-t", str(wurzel),
             "-d", "include_path=.;" + str(WURZEL / "libs" / "phplib"),
             "-d", "display_errors=0", "-d", "date.timezone=Europe/Berlin",
             "-d", "sys_temp_dir=C:/tmp/abfprobe_" + MARKE,
             "-d", "upload_tmp_dir=C:/tmp/abfprobe_" + MARKE,
             "-d", "extension_dir=" + str(Path(PHP).parent / "ext"), "-d", "extension=curl"],
            cwd=str(wurzel), env=umg, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        Path("C:/tmp/abfprobe_" + MARKE).mkdir(parents=True, exist_ok=True)
        for _ in range(50):
            try:
                socket.create_connection(("127.0.0.1", self.port), 0.2).close(); break
            except OSError:
                time.sleep(0.1)
        return self

    def __exit__(self, *a):
        self.p.terminate(); self.p.wait(5)

    def anfrage(self, methode, pfad, felder=None, datei=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=30)
        kopf = {}
        rumpf = None
        if datei is not None:
            grenze = "----grenze1610"
            teile = []
            for k, v in (felder or {}).items():
                teile.append(f'--{grenze}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n')
            teile.append(f'--{grenze}\r\nContent-Disposition: form-data; name="abfahrt_sicherung"; filename="s.json"\r\nContent-Type: application/json\r\n\r\n')
            rumpf = "".join(teile).encode() + datei + f"\r\n--{grenze}--\r\n".encode()
            kopf["Content-Type"] = "multipart/form-data; boundary=" + grenze
        elif felder is not None:
            rumpf = urllib.parse.urlencode(felder, doseq=True).encode()
            kopf["Content-Type"] = "application/x-www-form-urlencoded"
        t0 = time.time()
        c.request(methode, pfad, body=rumpf, headers=kopf)
        r = c.getresponse()
        b = r.read().decode("utf-8", "replace")
        return r.status, dict(r.getheaders()), b, time.time() - t0


def formtoken(html):
    m = re.search(r'name="formtoken" value="([0-9a-f]+)"', html)
    return m.group(1) if m else ""


def main():
    baue()
    CFG().write_text(json.dumps(GUT, indent=2), encoding="utf-8")
    BAK().write_text(json.dumps(GUT, indent=2), encoding="utf-8")
    with Server() as s:
        st, kopf, html, dauer = s.anfrage("GET", "/index.php")
        zeile(st == 200 and len(html) > 20000, "GET liefert die Seite", f"HTTP {st}, {len(html)} Zeichen, {dauer:.2f} s")
        n_aktiv = len(re.findall(r'class="sm-seite sm-active"', html))
        zeile(n_aktiv == 1, "genau ein Reiterbereich serverseitig aktiv", n_aktiv)
        n_ziel = len(re.findall(r'data-ziel="tab-', html)); n_id = len(re.findall(r'<div class="sm-seite[^"]*" id="tab-', html))
        zeile(n_ziel == 5 and n_id == 5, "5 Reiter in Leiste und Bereichen", (n_ziel, n_id))
        zeile("sm-b-aktion sm-speichern" in html, "Speichern traegt die Aktionsfarbe", "sm-b-aktion sm-speichern" in html)
        fehlende = sorted(set(re.findall(r"\b(?:SEITE|TEXT|MELDUNG|TEST|LOX|MQTT|FELDKURZ|FELDNAME)\.[A-Z0-9_]+\b", html)))
        zeile(not fehlende, "keine unaufgeloesten Sprachschluessel in der Seite", fehlende[:8])
        zeile("&amp;bdquo;" not in html and "&amp;mdash;" not in html, "keine doppelt maskierten Entitaeten", html.count("&amp;mdash;"))
        n_such = html.count("\\i;")
        zeile(html.count("\\i;ALTER=\\i\\v") == 1 and html.count("\\i;ANKUNFT=\\i\\v") == 1, "Befehlserkennung fuehrt ALTER und ANKUNFT", n_such)
        zeile("abfahrt_ABFAHRT_IN" in html and "Abfahrt ABFAHRT_IN" not in html, "Eingangsname wie vom Gateway vergeben", "abfahrt_ABFAHRT_IN" in html)
        ft = formtoken(html)
        zeile(len(ft) == 64, "Formularmerkmal vorhanden", len(ft))

        # --- Formularschutz
        st, kopf, b, _ = s.anfrage("POST", "/index.php", {"token_neu": "1", "activetab": "tab-test", "formtoken": "falsch"})
        zeile(st == 303, "POST mit falschem Merkmal wird umgeleitet", (st, kopf.get("Location")))
        zeile(lies_cfg()["aktionstoken"] == GUT["aktionstoken"], "falsches Merkmal aendert nichts", lies_cfg()["aktionstoken"][:12])
        st, _, html, _ = s.anfrage("GET", "/index.php?form=test")
        zeile("Einmalmerkmal" in html or "one-time" in html, "GET zeigt die Abweisung", st)

        # --- Merkwort neu: PRG, einmalige Meldung, F5 wiederholt nichts
        st, _, html, _ = s.anfrage("GET", "/index.php"); ft = formtoken(html)
        st, kopf, b, _ = s.anfrage("POST", "/index.php", {"token_neu": "1", "activetab": "tab-test", "formtoken": ft})
        tok1 = lies_cfg()["aktionstoken"]
        zeile(st == 303 and kopf.get("Location", "").endswith("form=test") and b == "",
              "token_neu: 303 auf form=test, leerer Rumpf", (st, kopf.get("Location"), len(b)))
        zeile(tok1 != GUT["aktionstoken"], "token_neu hat ein neues Merkwort geschrieben", tok1[:12])
        zeile(json.loads(BAK().read_text())["aktionstoken"] == tok1, "Zweitschrift traegt das neue Merkwort", "gleich")
        st, _, html, _ = s.anfrage("GET", "/index.php?form=test")
        zeile("Neues Merkwort erzeugt" in html, "erstes GET zeigt die Meldung", st)
        st, _, html2, _ = s.anfrage("GET", "/index.php?form=test")
        zeile("Neues Merkwort erzeugt" not in html2, "zweites GET zeigt sie nicht mehr (Einmalmeldung)", "Neues Merkwort erzeugt" in html2)
        zeile(lies_cfg()["aktionstoken"] == tok1, "Neuladen wuerfelt kein zweites Merkwort", lies_cfg()["aktionstoken"][:12])

        # --- Speichern mit ungueltigem Wert: abgewiesen, gemeldet, alter Wert bleibt
        ft = formtoken(html2)
        felder = {"save": "1", "activetab": "tab-settings", "formtoken": ft,
                  "cal_name[]": ["Arbeit"] + [""] * 9, "cal_url[]": ["https://example.invalid/a.ics"] + [""] * 9,
                  "provider": "tomtom", "api_key": "SCHLUESSEL-KARTENDIENST", "home_address": "Musterweg 1, Kassel",
                  "buffer_min": "abc", "arrival_min": "10", "lookahead_hours": "15", "ignore_locations": "online",
                  "tts_mode": "custom", "tts_ip": "", "tts_port": "7091", "tts_zones": "1", "tts_volume": "8",
                  "tts_lang": "de", "tts_template": "http://fremd.example/x?t={text}", "ansage_vorlage": "", "ganztags_zeit": "08:00"}
        for d in range(1, 11):
            felder[f"quiet_from[{d}]"] = "20:00"; felder[f"quiet_to[{d}]"] = "07:00"
        st, kopf, _, _ = s.anfrage("POST", "/index.php", felder)
        c = lies_cfg()
        zeile(st == 303, "Speichern leitet um", st)
        zeile(c["buffer_min"] == 12, "buffer_min=abc abgewiesen, alter Wert 12 bleibt", c["buffer_min"])
        zeile(c.get("tts", {}).get("template", "") == "", "fremde tts-Vorlage abgewiesen", c.get("tts", {}).get("template"))
        zeile(c["aktionstoken"] == tok1, "Speichern behaelt das Merkwort", c["aktionstoken"][:12])
        st, _, html, _ = s.anfrage("GET", "/index.php")
        zeile("wurde nicht übernommen" in html, "GET meldet die abgewiesenen Felder", html.count("wurde nicht übernommen"))

        # --- Sperrzeiten: geleertes Feld behaelt den alten Wert, falsche Zeit wird abgewiesen
        for d in range(1, 11):
            felder[f"quiet_from[{d}]"] = "21:15"; felder[f"quiet_to[{d}]"] = "06:45"
        felder.update({"buffer_min": "12", "tts_template": "", "formtoken": formtoken(html)})
        s.anfrage("POST", "/index.php", felder)
        st, _, html, _ = s.anfrage("GET", "/index.php")
        felder.update({"quiet_from[3]": "", "quiet_on[3]": "on", "formtoken": formtoken(html)})
        s.anfrage("POST", "/index.php", felder)
        c = lies_cfg(); st, _, html, _ = s.anfrage("GET", "/index.php")
        q3 = c.get("quiet", {}).get("3", {})
        zeile(q3.get("from") == "21:15" and q3.get("on") == 1 and "Sperrzeiten" not in html.split("nicht übernommen")[0][-200:] and "wurde nicht übernommen" not in html,
              "leeres Zeitfeld behaelt den alten Wert, Tabelle uebernommen", (q3, "wurde nicht übernommen" in html))
        felder.update({"quiet_from[3]": "25:00", "quiet_on[3]": "", "formtoken": formtoken(html)})
        del felder["quiet_on[3]"]
        s.anfrage("POST", "/index.php", felder)
        c = lies_cfg(); st, _, html, _ = s.anfrage("GET", "/index.php")
        zeile(c.get("quiet", {}).get("3", {}).get("on") == 1 and "wurde nicht übernommen" in html,
              "Zeit 25:00 weist die Tabelle ab, alter Stand bleibt", c.get("quiet", {}).get("3"))

        # --- Zurueckspielen: gueltig, halb gueltig, fremd
        for name, inhalt, erwartung in (
            ("fremd", {"_plugin": "abfahrtsassistent", "unbekannt": 1, "buffer_min": 20}, "abgelehnt"),
            ("halb", {"_plugin": "abfahrtsassistent", "buffer_min": 30, "quiet": {"1": {"on": 1, "from": "XX", "to": "YY"}}}, "abgelehnt"),
            ("gueltig", {"_plugin": "abfahrtsassistent", "buffer_min": 25, "arrival_min": 5}, "uebernommen"),
        ):
            vorher = CFG().read_bytes()
            st, _, html, _ = s.anfrage("GET", "/index.php"); ft = formtoken(html)
            st, kopf, _, _ = s.anfrage("POST", "/index.php", {"abfahrt_zurueck": "1", "activetab": "tab-settings", "formtoken": ft},
                                       datei=json.dumps(inhalt).encode())
            nachher = CFG().read_bytes()
            st2, _, html, _ = s.anfrage("GET", "/index.php")
            if erwartung == "abgelehnt":
                zeile(st == 303 and vorher == nachher and "NICHT übernommen" in html,
                      f"Zurueckspielen {name}: nichts geaendert, gemeldet", (st, vorher == nachher))
            else:
                c = lies_cfg()
                zeile(st == 303 and c["buffer_min"] == 25 and c["api_key"] == GUT["api_key"] and "nachgezogen" in html,
                      f"Zurueckspielen {name}: uebernommen, Rest behalten, Dienst nachgezogen", (c["buffer_min"], c["api_key"][:9]))

    # --- beschaedigte Konfiguration (G1), neuer Server-Lauf
    CFG().write_bytes(b'{"api_key":"SCHLUESSEL-KARTENDIENST","aktion')
    gut_zweit = json.loads(BAK().read_text())
    with Server() as s:
        st, _, html, _ = s.anfrage("GET", "/index.php")
    c = lies_cfg()
    kaputt = list((WURZEL / "config/plugins" / ORD).glob("abfahrt.json.kaputt-*"))
    zeile(c is not None and c.get("aktionstoken") == gut_zweit["aktionstoken"], "beschaedigte Datei: Merkwort aus der Zweitschrift", (c or {}).get("aktionstoken", "")[:12])
    zeile(c is not None and c.get("api_key") == GUT["api_key"], "beschaedigte Datei: Schluessel erhalten", (c or {}).get("api_key"))
    zeile(json.loads(BAK().read_text())["aktionstoken"] == gut_zweit["aktionstoken"], "Zweitschrift nicht ueberschrieben", "gleich")
    zeile(len(kaputt) == 1, "beschaedigte Datei beiseitegelegt", [p.name for p in kaputt])
    log = (WURZEL / "log/plugins" / ORD / "abfahrt.log")
    lt = log.read_text(encoding="utf-8") if log.is_file() else ""
    zeile("nicht lesen" in lt and "Zweitschrift" in lt, "Protokoll nennt beides", lt.count("Konfiguration:"))
    zeile("ließ sich nicht lesen" in html, "Seite meldet es", st)

    print(f"== {sum(ergebnisse)} von {len(ergebnisse)} Zeilen erfuellt ==")
    return 0 if all(ergebnisse) else 1


if __name__ == "__main__":
    sys.exit(main())
