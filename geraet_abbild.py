# -*- coding: utf-8 -*-
"""Ist-Abbild des LoxBerry ziehen - ueber SSH als Benutzer claude, rein lesend, ohne Zugangsdaten.

Aufruf:
    python Werkzeuge/geraet_abbild.py                 schreibt nach Geraet/<JJJJ-MM-TT>/
    python Werkzeuge/geraet_abbild.py --host NAME     anderer SSH-Host (Vorgabe: loxberry-claude)
    python Werkzeuge/geraet_abbild.py --vergleich     zusaetzlich Unterschiede zum vorigen Abbild ausgeben

Voraussetzung: der SSH-Zugang aus Werkzeuge/LIESMICH_LoxBerry-Zugang.md (Host loxberry-claude in
~/.ssh/config, Schluessel loxberry_claude).

Was gezogen wird (je ein Textfile, Nummern wie beim ersten Abbild vom 05.09.2026):
  01 System (Kernel, Debian, Uptime)          02 Benutzer/Gruppen, sudoers.d soweit lesbar
  03 Sprachen (php -v/-m, python, perl, node) 04 Umgebung (LB*-Variablen aus /etc/environment)
  06 /opt/loxberry Tiefe 2 mit Rechten          07 Plugin-Baeume (bin, config, data, html, htmlauth, log, cron)
  08 plugininstall.pl (Kopie, fuer Zeilennummern in den Regeln)
  09 plugindatabase.json (Kopie)               10 general.json - NUR Schluessel und Gateway-Fassung
  11 Cron                                       12 laufende Dienste und Timer
  13 PHP/Apache-Konfiguration (php.ini-Zeilen, sites-enabled ohne Kommentare)

Was NIE gezogen wird: Werte aus config/system/general.json (Miniserver- und Broker-Zugangsdaten
stehen dort im Klartext, Datei ist 644), Plugin-Konfigurationen, .ssh, Logs mit Nutzlast.
Der Filter fuer general.json ersetzt jeden Zeichenkettenwert auf JEDER Tiefe durch "str"; belassen
werden nur Zahlen, Wahrheitswerte, null und die Schluessel Base.Version, Mqtt.Gatewayversion,
Mqtt.Gatewayautostart. Eichung: Werkzeuge/geraet_abbild_eichung.py prueft den Filter an einer
nachgebauten general.json (ein Kennwort auf Tiefe 3 muss verschwinden).

Anlass: Regeln/06 stuetzte sich bisher auf Vermutungen ueber Pfade und Rechte des Geraets. Das erste
Abbild (05.09.2026) hat u. a. gezeigt: PHP 7.4.33 auf Debian 13, general.json fuer jeden lesbar,
loxberry ohne kennwortfreies sudo fuer beliebige Befehle, zwei Gateway-Implementierungen in sbin.
"""
import datetime
import json
import os
import subprocess
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.dirname(HIER)

BEFEHLE = [
    ("01_system.txt", "uname -a; cat /etc/os-release; cat /etc/debian_version; uptime"),
    ("02_benutzer_rechte.txt", "id loxberry; id; getent group loxberry adm www-data docker; "
     "getent passwd | awk -F: '$3>=1000 || $1==\"www-data\" || $1==\"root\"'; "
     "for f in /etc/sudoers.d/*; do echo \"# $f\"; grep -v '^ *#' \"$f\" 2>&1 | grep -v '^$'; done"),
    ("03_sprachen.txt", "php -v; php -m; ls -la /usr/bin/php* /etc/php 2>&1; python3 --version; perl -v | head -2; node -v 2>&1; /usr/sbin/apache2 -v 2>&1"),
    ("04_env.txt", "grep -h 'LB\\|PERL5LIB' /etc/environment /etc/profile.d/loxberry.sh 2>/dev/null | sort -u"),
    ("06_baum_tiefe2.txt", "find /opt/loxberry -maxdepth 2 -not -path '*/.cache/*' -not -path '*/.npm/*' -printf '%M %u %g %8s %p\\n' | sort -k5"),
    ("07_pluginbaeume.txt", "find /opt/loxberry/bin/plugins /opt/loxberry/config/plugins /opt/loxberry/data/plugins "
     "/opt/loxberry/webfrontend/html/plugins /opt/loxberry/webfrontend/htmlauth/plugins /opt/loxberry/log/plugins "
     "/opt/loxberry/system/cron -maxdepth 2 -not -name '*.log' -printf '%M %u %g %8s %TY-%Tm-%Td %p\\n' 2>&1 | sort -k6"),
    ("08_plugininstall.pl", "cat /opt/loxberry/sbin/plugininstall.pl"),
    ("09_plugindatabase.json", "cat /opt/loxberry/data/system/plugindatabase.json"),
    ("10_general_schluessel.json", "cat /opt/loxberry/config/system/general.json"),
    ("11_cron.txt", "ls -la /etc/cron.d /opt/loxberry/system/cron/cron.d 2>&1; for f in /etc/cron.d/* /opt/loxberry/system/cron/cron.d/*; do echo \"# $f\"; grep -v '^ *#' \"$f\" 2>&1 | grep -v '^$'; done"),
    ("12_dienste.txt", "systemctl list-units --type=service --state=running --no-pager; systemctl list-timers --no-pager"),
    ("13_php_apache.txt", "grep -n 'auto_prepend\\|include_path\\|display_errors\\|error_log' /etc/php/*/apache2/php.ini /etc/php/*/cli/php.ini 2>/dev/null; "
     "ls /etc/apache2/sites-enabled; cat /etc/apache2/sites-enabled/* 2>/dev/null | grep -v '^ *#' | grep -v '^$'"),
]


def filtern_general(text):
    """general.json: alle Zeichenkettenwerte auf jeder Tiefe durch 'str' ersetzen, Ausnahmen s. o."""
    d = json.loads(text)
    BEHALTEN = {("Base", "Version"), ("Mqtt", "Gatewayversion"), ("Mqtt", "Gatewayautostart")}

    def geh(v, pfad):
        if isinstance(v, dict):
            return {k: geh(vv, pfad + (k,)) for k, vv in v.items()}
        if isinstance(v, list):
            return [geh(x, pfad) for x in v]
        if isinstance(v, str):
            return v if (v == "" or pfad[:2] in BEHALTEN) else "str"
        return v
    aus = geh(d, ())
    aus["_hinweis"] = "Werte durch 'str' ersetzt (geraet_abbild.py); Zugangsdaten stehen hier nicht."
    return json.dumps(aus, indent=1, sort_keys=True, ensure_ascii=False)


def ssh(host, befehl):
    p = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", host, befehl],
                       capture_output=True)
    return p.returncode, p.stdout, p.stderr


def main(argv):
    host = argv[argv.index("--host") + 1] if "--host" in argv else "loxberry-claude"
    heute = datetime.datetime.now().strftime("%Y-%m-%d")
    ziel = os.path.join(WURZEL, "Geraet", heute)
    rc, out, err = ssh(host, "id")
    if rc != 0:
        sys.stderr.write("Kein Zugang zu %s: %s\n" % (host, err.decode("utf-8", "replace").strip()))
        return 2
    os.makedirs(ziel, exist_ok=True)
    fehler = 0
    for name, befehl in BEFEHLE:
        rc, out, err = ssh(host, befehl)
        text = out.decode("utf-8", "replace")
        if name == "10_general_schluessel.json":
            try:
                text = filtern_general(text)
            except Exception as e:
                text = '{"_fehler": "general.json nicht lesbar oder kein JSON: %s"}' % e
        if rc != 0 and not text.strip():
            text = "# Befehl scheiterte (rc=%d): %s\n" % (rc, err.decode("utf-8", "replace").strip())
            fehler += 1
        with open(os.path.join(ziel, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text if text.endswith("\n") else text + "\n")
        print("%-28s %7d Byte%s" % (name, len(text.encode("utf-8")), "" if rc == 0 else "  (rc=%d)" % rc))
    # Befund: Verzeichnisse in den Cron-Ordnern laufen nie (lbdefaults ruft $f direkt auf;
    # plugininstall.pl raeumt sie beim Upgrade nicht ab, weil es rm -fv ohne -r nimmt)
    try:
        with open(os.path.join(ziel, "07_pluginbaeume.txt"), encoding="utf-8") as f:
            cron_verz = [z.split()[-1] for z in f
                         if z.startswith("d") and "/system/cron/cron." in z
                         and not z.rstrip().endswith(("/cron.d", "/cron.reboot", "/cron.01min", "/cron.03min",
                                                       "/cron.05min", "/cron.10min", "/cron.15min", "/cron.30min",
                                                       "/cron.hourly", "/cron.daily", "/cron.weekly",
                                                       "/cron.monthly", "/cron.yearly"))]
        if cron_verz:
            print("BEFUND - Verzeichnis im Cron-Ordner, wird nie ausgefuehrt: %s" % ", ".join(cron_verz))
    except OSError:
        pass
    # Gegenprobe: kein Kennwort im Abbild
    verdacht = []
    for name in os.listdir(ziel):
        b = open(os.path.join(ziel, name), "rb").read().lower()
        # LoxAPP3.json fuehrt das Benutzerrecht "changePassword" - kein Kennwort (gemessen 05.09.2026)
        b = b.replace(b'changepassword', b'')
        for muster in (b'"pass"', b'brokerpass', b'credentials"', b'password'):
            if muster in b and name != "08_plugininstall.pl":
                # in 10_ sind die Schluessel erlaubt, die Werte muessen 'str' sein
                if name == "10_general_schluessel.json":
                    continue
                verdacht.append((name, muster.decode()))
    if verdacht:
        print("ACHTUNG - Muster fuer Zugangsdaten gefunden, bitte ansehen: %s" % verdacht)
    print("Abbild unter %s (%d Dateien, %d Befehle gescheitert)" % (ziel, len(BEFEHLE), fehler))
    if "--vergleich" in argv:
        alle = sorted(d for d in os.listdir(os.path.join(WURZEL, "Geraet")) if d < heute)
        if alle:
            vorher = os.path.join(WURZEL, "Geraet", alle[-1])
            print("\nUnterschiede zu %s:" % alle[-1])
            for name, _ in BEFEHLE:
                a, b = os.path.join(vorher, name), os.path.join(ziel, name)
                if os.path.isfile(a) and open(a, "rb").read() != open(b, "rb").read():
                    print("  %s weicht ab" % name)
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
