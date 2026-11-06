#!/bin/bash
# Laeuft auf: Windows, Git Bash, aufgerufen von Werkzeuge/minutenlauf_pruefen.py. Zweiter Teil des Kettenschritts "Minutenlauf".
#
# Warum es den Teil gibt: am LoxBerry ist php die 7.4.33 (am Geraet gemessen 01.11.2026). In WSL gibt es nur 8.3, und ein Linux-PHP 7.4
# liegt auf diesem Rechner nicht vor (das Geraet ist aarch64, die Fassung dort laeuft hier nicht). 7.4.33 gibt es nur als Windows-Programm.
# Dieser Teil fuehrt deshalb dieselbe Cron-Datei unter dash (MSYS) mit php.exe 7.4 aus. Er beantwortet EINE Frage: stuerzt der Lauf unter 7.4 ab?
# Er ersetzt NICHT den Teil in WSL: Rechte, Signale, flock, /proc und Zeilenenden der Schale misst nur der. Darum zaehlen hier nur
# Absturzzeilen und der Rueckgabewert; eine volle cron.err kann auch vom Windows-Umfeld kommen und wird nur genannt.
#
# Abweichungen vom Geraet, alle hier und nirgends sonst:
#  * loxberry_system.php: eine Zeile mehr, damit das SDK den Plugin-Ordner auch mit Rueckstrichen erkennt (Windows liefert sie in get_included_files()).
#    Sonst die Datei vom Geraet; die Prueffsumme vor der Aenderung wird verglichen.
#  * posix_*-Ersatz in der Sonde (unter Windows fehlt die Erweiterung), flock- und nohup-Attrappe, kein Dienststart.
#  * /tmp/<ordner> der Linie ist C:\tmp\<ordner>. Der Ordnername ist je Linie fest (<ordner>_ml), siehe unten zum alten Stand.
#  * Netz: unter Windows gibt es keinen Namensraum. Darum schalten disable_functions und allow_url_fopen=0 jeden Weg von PHP nach aussen ab, auch
#    die Prozessstarter (unter 7.4 ist das eine Warnung mit Rueckgabe null, kein Absturz), und curl, wget, ping, ssh, docker, python sind Attrappen.
#
# Aufruf: minutenlauf_pruefstand74.sh <linie> <sdk-ordner> <angaben.json> <arbeit, neu, ohne Leerzeichen> <php.exe> <cron-datei> ...
# Ausgabe wie der WSL-Teil, Zeilen "LAUF", "FEHL", "HINWEIS", am Ende "ERGEBNIS". Nichts wird geloescht.
# Seit 01.11.2026 EIN fester Arbeitsordner je Linie statt eines neuen je Lauf (C:/tmp/ml74 wuchs auf 231 MB). Er traegt die Marke .ml74_fest. Vor dem Lauf werden die Dateien der
# Linie darueberkopiert und alle Zustandsdateien des letzten Laufs (data, log, aus, /tmp/<ordner>_ml) auf 0 Byte gesetzt, nicht entfernt. Grenze: eine Datei, die nur der letzte Lauf
# angelegt hat, ist damit leer da, nicht weg; config/ bleibt ueberschrieben, nicht geleert. Wer einen wirklich frischen Stand will, nennt den Ordner um.
set -u
Q="${1:?linie}"; SDK="${2:?sdk}"; ANG="${3:?angaben}"; W="${4:?arbeit}"; PHP74="${5:?php}"
shift 5
if [ -e "$W" ] && [ ! -f "$W/.ml74_fest" ]; then echo "ABBRUCH: $W gibt es schon und traegt die Marke dieses Werkzeugs nicht"; exit 2; fi
case "$W" in *" "*) echo "ABBRUCH: Leerzeichen im Arbeitsordner"; exit 2;; esac
wert() { python -B -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); print(d.get(sys.argv[2],''))" "$ANG" "$1"; }
O0="$(wert ordner)"; O="${O0}_ml"
case "$O0" in ""|*[!A-Za-z0-9_-]*) echo "ABBRUCH: Ordnername der Linie unbrauchbar"; exit 2;; esac
mkdir -p "$W" && : > "$W/.ml74_fest" || { echo "ABBRUCH: $W nicht anlegbar"; exit 2; }
# Zustand des letzten Laufs dieser Linie auf 0 Byte: sonst spielten Merker, Sperren und Protokolle mit.
for r in "$W/aus" "$W/lb/data/plugins/$O" "$W/lb/log/plugins/$O" "/c/tmp/$O" "/tmp/$O"; do
    [ -d "$r" ] || continue
    find "$r" -type f | while IFS= read -r f; do : > "$f"; done
done
L="$W/lb"
mkdir -p "$W/fake" "$W/aus" "$W/heim" "$L/bin/plugins/$O" "$L/webfrontend/html/plugins/$O" "$L/webfrontend/htmlauth/plugins/$O" "$L/templates/plugins/$O" \
         "$L/config/plugins/$O" "$L/data/plugins/$O" "$L/log/plugins/$O" "$L/config/system" "$L/data/system" "$L/libs/phplib" || exit 2
for p in "bin:bin/plugins/$O" "webfrontend/html:webfrontend/html/plugins/$O" "webfrontend/htmlauth:webfrontend/htmlauth/plugins/$O" \
         "templates:templates/plugins/$O" "config:config/plugins/$O" "data:data/plugins/$O"; do
    [ -d "$Q/${p%%:*}" ] && cp -r "$Q/${p%%:*}/." "$L/${p##*:}/"
done
cp "$Q/plugin.cfg" "$L/config/plugins/$O/plugin.cfg" 2>/dev/null
cp -r "$SDK/." "$L/libs/phplib/"
LW="$(cygpath -m "$L")"
# Die Aenderung am SDK, geprueft: Ausgangssumme aus HERKUNFT.txt, Trefferzahl genau 1.
python -B - "$L/libs/phplib/loxberry_system.php" "$SDK/HERKUNFT.txt" <<'PY' || { echo "ABBRUCH: SDK-Kopie nicht wie erwartet"; exit 2; }
import hashlib, re, sys
d = open(sys.argv[1], "rb").read()
soll = re.search(r"md5 ([0-9a-f]{32})", open(sys.argv[2], encoding="utf-8").read()).group(1)
assert hashlib.md5(d).hexdigest() == soll
a = b"list($scriptPath) = get_included_files();"
assert d.count(a) == 1
open(sys.argv[1], "wb").write(d.replace(a, a + b" $scriptPath = str_replace(chr(92), '/', $scriptPath);"))
PY
# Wie der Installer, dazu: #!/usr/bin/php gibt es unter MSYS nicht.
ersetzen() {
    sed -i -e "s#REPLACELBPHTMLAUTHDIR#$LW/webfrontend/htmlauth/plugins/$O#g" -e "s#REPLACELBPHTMLDIR#$LW/webfrontend/html/plugins/$O#g" \
           -e "s#REPLACELBPTEMPLATEDIR#$LW/templates/plugins/$O#g" -e "s#REPLACELBPDATADIR#$LW/data/plugins/$O#g" \
           -e "s#REPLACELBPLOGDIR#$LW/log/plugins/$O#g" -e "s#REPLACELBPCONFIGDIR#$LW/config/plugins/$O#g" \
           -e "s#REPLACELBPBINDIR#$LW/bin/plugins/$O#g" -e "s#REPLACELBPPLUGINDIR#$O#g" -e "s#REPLACEFOLDERNAME#$O#g" \
           -e "s#REPLACELBHOMEDIR#$LW#g" -e '1s,^#! */usr/bin/php,#!/usr/bin/env php,' "$1"
}
grep -rlIE 'REPLACE(LB|FOLDER)|^#! */usr/bin/php' "$L/bin/plugins/$O" "$L/webfrontend/html/plugins/$O" "$L/webfrontend/htmlauth/plugins/$O" \
     "$L/templates/plugins/$O" "$L/config/plugins/$O" "$L/data/plugins/$O" 2>/dev/null | while IFS= read -r f; do ersetzen "$f"; done
cat > "$L/config/system/general.json" <<'EOF'
{"Base":{"Clouddnsuri":"dns.example.org","Country":"de","Lang":"de","Version":"4.0.0.15","Sendstatistic":"0","Systemloglevel":"6","Theme":"classic"},"Timeserver":{"Timezone":"Europe/Berlin"},
 "Network":{"Friendlyname":"probe"},"Webserver":{"Port":"80","Sslport":"443","Sslenabled":"0"},"Miniserver":{},"Binaries":{},
 "Mqtt":{"Gatewayversion":"2","Gatewayautostart":"1","Brokerhost":"127.0.0.1","Brokerport":"1","Brokeruser":"lb","Brokerpass":"Geheim1","Finderdisabled":"1","Loglevel":"6","Udpinport":"11884","Uselocalbroker":"1","Websocketport":"9001"}}
EOF
FASS="$(sed -n 's/^VERSION=//p' "$Q/plugin.cfg" | tr -d '\r"' | head -1)"
printf '{"plugins":{"probe":{"version":"%s","name":"%s","folder":"%s","title":"Probe","loglevel":"6"}}}\n' "$FASS" "$O" "$O" > "$L/data/system/plugindatabase.json"
python -B - "$ANG" "$L" "$O" "$W/fake/sub.txt" "$W/fake/mosquitto_sub.cmd" <<'PY'
import json, os, sys
d = json.load(open(sys.argv[1], encoding="utf-8")); L, O = sys.argv[2], sys.argv[3]
for pfad, text in d.get("konfig", {}).items():
    z = os.path.join(L, pfad.replace("<O>", O))
    os.makedirs(os.path.dirname(z), exist_ok=True)
    open(z, "w", encoding="utf-8", newline="").write(text)
zeilen = d.get("sub", [])
open(sys.argv[4], "w", encoding="utf-8", newline="").write("".join(z + chr(10) for z in zeilen))
open(sys.argv[5], "w", encoding="utf-8", newline="").write("@echo off" + chr(13) + chr(10) + "".join("echo " + z + chr(13) + chr(10) for z in zeilen) + "exit /b 27" + chr(13) + chr(10))
PY
printf '#!/bin/sh\ncat "%s/fake/sub.txt"\nexit 27\n' "$W" > "$W/fake/mosquitto_sub"
printf '#!/bin/sh\necho "$*" >> "%s/aus/pub.log"\n' "$W" > "$W/fake/mosquitto_pub"
printf '@echo off\r\nexit /b 0\r\n' > "$W/fake/mosquitto_pub.cmd"
printf '#!/bin/sh\necho "$*" >> "%s/aus/nohup.log"\n' "$W" > "$W/fake/nohup"
printf '#!/bin/sh\nexit 0\n' > "$W/fake/flock"
for x in curl wget ping nc ssh docker python python3 su sudo; do printf '#!/bin/sh\nexit 1\n' > "$W/fake/$x"; done
# Sonde: zaehlt die Laeufe und ersetzt, was es unter Windows nicht gibt. Pfade ohne Tilde (Gedaechtnis: php -d und der Kurzpfad).
SONDE="$L/bin/plugins/$O/_ml_sonde.php"
AUSW="$(cygpath -m "$W/aus")"
VOR="$(wert vorlauf)"; VORZ=""
if [ -n "$VOR" ]; then
    cp "$(dirname "$0")/minutenlauf_attrappen/$VOR" "$W/vorlauf.php" || { echo "ABBRUCH: Fahrzeug-Attrappe fehlt"; exit 2; }
    VORZ="putenv('RN_ATT=$AUSW'); require_once '$(cygpath -m "$W/vorlauf.php")';"
fi
cat > "$SONDE" <<EOF
<?php
$VORZ
foreach (array('posix_getuid' => 1000, 'posix_geteuid' => 1000, 'posix_getgid' => 1000, 'posix_getegid' => 1000, 'posix_getpid' => 1, 'posix_isatty' => false, 'posix_kill' => false) as \$ml_f => \$ml_w) {
    if (!function_exists(\$ml_f)) { eval('function ' . \$ml_f . '() { return ' . var_export(\$ml_w, true) . '; }'); }
}
if (!function_exists('posix_getpwuid')) { function posix_getpwuid(\$u) { return array('name' => 'loxberry', 'dir' => (string) getenv('LBHOMEDIR')); } }
if (!function_exists('posix_getpwnam')) { function posix_getpwnam(\$u) { return array('name' => 'loxberry', 'uid' => 1000, 'dir' => (string) getenv('LBHOMEDIR')); } }
register_shutdown_function(function () {
    \$z = array('s' => basename((string) (isset(\$_SERVER['SCRIPT_FILENAME']) ? \$_SERVER['SCRIPT_FILENAME'] : '')),
        'sdk' => class_exists('LBSystem', false) ? 1 : 0, 'gelesen' => isset(\$GLOBALS['cfgwasread']) ? 1 : 0);
    @file_put_contents('$AUSW/php_aufrufe.log', json_encode(\$z) . "\n", FILE_APPEND);
});
EOF
EXT="$(dirname "$(cygpath -m "$PHP74")")/ext"
cat > "$W/fake/php" <<EOF
#!/bin/sh
exec "$PHP74" -n -d extension_dir="$EXT" -d extension=mbstring -d extension=openssl -d extension=curl -d extension=sockets -d allow_url_fopen=0 -d disable_functions=curl_exec,curl_multi_exec,fsockopen,pfsockopen,stream_socket_client,socket_connect,gethostbyname,gethostbynamel,dns_get_record,mail,exec,shell_exec,system,passthru,proc_open,popen -d include_path=".;$LW/libs/phplib" -d display_errors=stderr -d log_errors=0 -d error_reporting=22527 -d html_errors=0 -d auto_prepend_file="$(cygpath -m "$SONDE")" "\$@"
EOF
chmod +x "$W/fake/"* 2>/dev/null
[ $# -gt 0 ] || { echo "ABBRUCH: keine Cron-Datei"; exit 2; }
FRIST="$(wert frist)"
ABSTURZ='Uncaught|PHP Fatal|Fatal error|PHP Parse|Parse error'
BEFUND=0; PHPS=0
for CF in "$@"; do
    NAME="$(basename "$CF")"
    Z="$W/$NAME.lauf"
    cp "$Q/cron/$NAME" "$Z" || { echo "FEHL $NAME fehlt"; BEFUND=1; continue; }
    ersetzen "$Z"
    sed -i -e 's#/usr/bin/php#php#g' "$Z"
    # Ein Lauf: Fragen zum Zustand ueber zwei Laeufe beantwortet der WSL-Teil, und manche Linien warten absichtlich (Abfahrt: 5 bis 40 s).
    for i in 1; do
        : >> "$W/aus/php_aufrufe.log"; A=$(wc -l < "$W/aus/php_aufrufe.log")
        T0=$(date +%s)
        ( cd "$W" && env PATH="$W/fake:/usr/bin:/bin:$PATH" LBHOMEDIR="$LW" LBPPLUGINDIR="$O" HOME="$W/heim" timeout --foreground -k 2 "${FRIST:-60}" /usr/bin/dash "$Z" ) > "$W/aus/lauf_${NAME}_$i.txt" 2>&1 < /dev/null
        RC=$?
        B=$(wc -l < "$W/aus/php_aufrufe.log"); PHPS=$((PHPS + B - A))
        echo "LAUF $NAME $i: rc=$RC php=$((B - A)) $(( $(date +%s) - T0 )) s"
        case "$RC" in 0) ;; 124|137) if [ -n "$FRIST" ]; then echo "HINWEIS $NAME: Frist $FRIST s erreicht (Angabe der Linie)"; else echo "FEHL $NAME Lauf $i: rc=$RC"; BEFUND=1; fi;; 255) echo "FEHL $NAME Lauf $i: rc=$RC"; BEFUND=1;; *) echo "HINWEIS $NAME Lauf $i: rc=$RC (unter Windows nicht gewertet, der WSL-Teil wertet ihn)";; esac
    done
done
PLATTFORM="undefined function (posix|pcntl)_|Call to undefined function (posix|pcntl)"
grep -rlE "$ABSTURZ" "$L/log/plugins/$O" "$W/aus" 2>/dev/null | while IFS= read -r t; do
    grep -E "$ABSTURZ" "$t" | head -1 | sed -e "s#$LW/##g" -e 's#\\#/#g' | cut -c1-200
done > "$W/treffer.txt"
if grep -qvE "$PLATTFORM" "$W/treffer.txt" 2>/dev/null; then
    BEFUND=1
    grep -vE "$PLATTFORM" "$W/treffer.txt" | head -3 | sed -e 's/^/FEHL Absturz unter 7.4: /'
fi
grep -E "$PLATTFORM" "$W/treffer.txt" 2>/dev/null | head -2 | sed -e 's/^/HINWEIS unter Windows nicht messbar: /'
for e in "$L/log/plugins/$O"/*.err "$L/log/plugins/$O"/cron_fehler.log; do
    [ -s "$e" ] && echo "HINWEIS $(basename "$e"): $(wc -l < "$e") Zeilen (Windows-Umfeld moeglich, nicht gewertet): $(head -1 "$e" | sed -e "s#$LW/##g" | cut -c1-120)"
done
PV="$("$PHP74" -n -r 'echo PHP_VERSION;' 2>/dev/null)"
[ -f "$W/aus/aufrufe.log" ] && echo "Fahrzeug-Attrappe: $(wc -l < "$W/aus/aufrufe.log") Aufrufe"
echo "SDK: php-Laeufe $(wc -l < "$W/aus/php_aufrufe.log"), davon SDK geladen $(grep -c '"sdk":1' "$W/aus/php_aufrufe.log"), general.json gelesen $(grep -c '"gelesen":1' "$W/aus/php_aufrufe.log")"
if [ "$BEFUND" != 0 ]; then echo "ERGEBNIS ROT php=$PV"; exit 1; fi
if [ "$PHPS" = 0 ]; then echo "ERGEBNIS NICHT_GEMESSEN php=$PV: kein php-Lauf"; exit 3; fi
echo "ERGEBNIS GRUEN php=$PV: $PHPS php-Aufrufe"; exit 0
