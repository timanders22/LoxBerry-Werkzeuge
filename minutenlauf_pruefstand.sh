#!/bin/bash
# Laeuft in: WSL (Ubuntu), aufgerufen von Werkzeuge/minutenlauf_pruefen.py. Nicht unter Git Bash.
#
# Anlass (01.11.2026): MGiSmart 1.1.31 stuerzte am Geraet in jedem Minutenlauf ab, weil das echte SDK ein globales $cfg
# ueberschrieb. Die Attrappe Werkzeuge/lb hat das nicht, Kette und Tor sahen es nie. Dieser Stand fuehrt den ECHTEN
# Cron-Einstieg einer Linie unter dem Interpreter seiner Shebang (dash/bash) in der INSTALLIERTEN Lage gegen die ECHTE
# libs/phplib (Werkzeuge/minutenlauf_sdk, Herkunft dort in HERKUNFT.txt) aus. Muster: vb_s1c_mg_skripte/s1c_pruefstand.sh.
#
# Aufruf: minutenlauf_pruefstand.sh <linie> <sdk-ordner> <angaben.json> <cron-datei> ...
#   <linie>        Plugin-Ordner (bau, Folgeordner, ausgepacktes Archiv), nur gelesen
#   <angaben.json> von minutenlauf_pruefen.py: {"ordner","cron","konfig":{datei:text},"sub":[zeilen],"sub_rc","pruefpfade":[...]}
#
# Namensraum (unshare): kein Netz; /opt, /tmp, /run/shm und /dev/shm sind tmpfs, /opt/loxberry ist der Baum; eigene PIDs. Mit dem
# Stand enden jeder liegengebliebene Dienst und jede Datei, ohne dass etwas zu loeschen waere, und feste Pfade der Linie
# richten nichts an. Benutzer im Lauf ist die eigene Kennung, nicht root (sonst waere eine 0444-Datei kein Hindernis und der
# su-Zweig liefe). Broker und Fahrzeug sind Attrappen (mosquitto_sub/_pub im Suchpfad), ein Netz gibt es nicht.
#
# PHP 8.3: das Geraet faehrt 7.4, und libs/phplib/phpMQTT/phpMQTT.php liest $x{0}, was ab 8.0 ein Fatal ist. Fuer DIESEN Teil steht in der Kopie
# unter /opt/loxberry darum $x[0]; loxberry_system.php bleibt unberuehrt. Der 7.4-Teil (minutenlauf_pruefstand74.sh) nimmt die Datei unveraendert.
#
# Ausgabe, je eine Zeile: "LAUF <datei> <n>: rc=<rc> php=<aufrufe> err=<byte>", "SDK ...", "FEHL ...", am Ende "ERGEBNIS ...".
set -u
Q="${1:?linie}"; SDK="${2:?sdk}"; ANG="${3:?angaben}"
shift 3
W=/opt/ml

if [ "${ML_INNEN:-}" != 1 ]; then
    # 1. Ebene: Einhaengen als root im Benutzernamensraum. 2. Ebene: zurueck auf die eigene Kennung.
    exec env ML_INNEN=1 ML_UID="$(id -u)" unshare -r -n -m -p -f --kill-child --mount-proc bash "$0" "$Q" "$SDK" "$ANG" "$@"
fi
if [ "${ML_STUFE:-}" != 2 ]; then
    mount -t tmpfs tmpfs /opt 2>/dev/null || { echo "ABBRUCH: /opt nicht einhaengbar"; exit 2; }
    mkdir -p /opt/loxberry "$W/heim" "$W/fake" "$W/ini" "$W/aus" || exit 2
    mount -t tmpfs tmpfs /tmp || { echo "ABBRUCH: /tmp nicht einhaengbar"; exit 2; }
    mount -t tmpfs tmpfs /dev/shm 2>/dev/null
    [ -d /run/shm ] && mount -t tmpfs tmpfs /run/shm 2>/dev/null
    # Manche Linien suchen mosquitto_* nur unter festen Pfaden (rn_programm: /usr/bin, /usr/local/bin, /bin): dort muss die Attrappe auch liegen.
    mount -t tmpfs -o mode=1777 tmpfs /usr/local/bin || { echo "ABBRUCH: /usr/local/bin nicht einhaengbar"; exit 2; }
    # Im Lauf heisst die eigene Kennung loxberry wie am Geraet: Linien pruefen "id -un" und brechen sonst ab (Chromecast: "weder loxberry noch root").
    NAME_ICH="$(getent passwd "$ML_UID" | cut -d: -f1)"
    sed -e "s/^$NAME_ICH:/loxberry:/" /etc/passwd > "$W/passwd" && sed -e "s/^$NAME_ICH:/loxberry:/" /etc/group > "$W/group"
    mount --bind "$W/passwd" /etc/passwd && mount --bind "$W/group" /etc/group || { echo "ABBRUCH: passwd nicht einhaengbar"; exit 2; }
    ip link set lo up 2>/dev/null || { echo "ABBRUCH: lo nicht hochzubringen"; exit 2; }
    # Broker- und Web-Attrappe hier, nicht spaeter: Port 80 braucht die Rechte dieser Stufe. Sie enden mit dem Namensraum.
    python3 "$(dirname "$0")/minutenlauf_broker.py" "$W/aus/broker.log" > /dev/null 2>&1 &
    sleep 0.3
    exec env ML_STUFE=2 unshare -U --map-user="$ML_UID" --map-group="$ML_UID" bash "$0" "$Q" "$SDK" "$ANG" "$@"
fi

# ---- ab hier eigene Kennung, /opt/loxberry ist der Baum ----
L=/opt/loxberry
wert() { python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get(sys.argv[2],''))" "$ANG" "$1"; }
O="$(wert ordner)"
[ -n "$O" ] || { echo "ABBRUCH: kein Ordnername"; exit 2; }
mkdir -p "$L/bin/plugins/$O" "$L/webfrontend/html/plugins/$O" "$L/webfrontend/htmlauth/plugins/$O" "$L/templates/plugins/$O" \
         "$L/config/plugins/$O" "$L/data/plugins/$O" "$L/log/plugins/$O" "$L/config/system" "$L/data/system" "$L/libs/phplib" \
         "$L/system/cron" "$L/log/system_tmpfs" "$L/log/system"
for p in "bin:bin/plugins/$O" "webfrontend/html:webfrontend/html/plugins/$O" "webfrontend/htmlauth:webfrontend/htmlauth/plugins/$O" \
         "templates:templates/plugins/$O" "config:config/plugins/$O" "data:data/plugins/$O"; do
    [ -d "$Q/${p%%:*}" ] && cp -r "$Q/${p%%:*}/." "$L/${p##*:}/"
done
cp "$Q/plugin.cfg" "$L/config/plugins/$O/plugin.cfg" 2>/dev/null
cp -r "$SDK/." "$L/libs/phplib/"
sed -i -E 's/\$([a-z_]+)\{(\$?[a-z0-9_]+)\}/$\1[\2]/g' "$L/libs/phplib/phpMQTT/phpMQTT.php"
# Wie der Installer: die Platzhalter in allen Textdateien, bin/ ausfuehrbar.
ersetzen() {
    sed -i -e "s#REPLACELBPHTMLAUTHDIR#$L/webfrontend/htmlauth/plugins/$O#g" -e "s#REPLACELBPHTMLDIR#$L/webfrontend/html/plugins/$O#g" \
           -e "s#REPLACELBPTEMPLATEDIR#$L/templates/plugins/$O#g" -e "s#REPLACELBPDATADIR#$L/data/plugins/$O#g" \
           -e "s#REPLACELBPLOGDIR#$L/log/plugins/$O#g" -e "s#REPLACELBPCONFIGDIR#$L/config/plugins/$O#g" \
           -e "s#REPLACELBPBINDIR#$L/bin/plugins/$O#g" -e "s#REPLACELBPPLUGINDIR#$O#g" -e "s#REPLACEFOLDERNAME#$O#g" \
           -e "s#REPLACELBHOMEDIR#$L#g" "$1"
}
grep -rlIE 'REPLACE(LB|FOLDER)' "$L/bin/plugins/$O" "$L/webfrontend/html/plugins/$O" "$L/webfrontend/htmlauth/plugins/$O" \
     "$L/templates/plugins/$O" "$L/config/plugins/$O" "$L/data/plugins/$O" 2>/dev/null | while IFS= read -r f; do ersetzen "$f"; done
find "$L/bin/plugins/$O" -type f -exec chmod a+x {} + 2>/dev/null
cat > "$L/config/system/general.json" <<'EOF'
{"Base":{"Clouddnsuri":"dns.example.org","Country":"de","Lang":"de","Version":"4.0.0.15","Sendstatistic":"0","Systemloglevel":"6","Theme":"classic"},"Timeserver":{"Timezone":"Europe/Berlin"},
 "Network":{"Friendlyname":"probe"},"Webserver":{"Port":"80","Sslport":"443","Sslenabled":"0"},"Miniserver":{},"Binaries":{},
 "Mqtt":{"Gatewayversion":"2","Gatewayautostart":"1","Brokerhost":"127.0.0.1","Brokerport":"1883","Brokeruser":"lb","Brokerpass":"Geheim1","Finderdisabled":"1","Loglevel":"6","Udpinport":"11884","Uselocalbroker":"1","Websocketport":"9001"}}
EOF
FASS="$(sed -n 's/^VERSION=//p' "$Q/plugin.cfg" | tr -d '\r"' | head -1)"
printf '{"plugins":{"probe":{"author_name":"Probe","author_email":"probe@example.org","version":"%s","name":"%s","folder":"%s","title":"Probe","loglevel":"6","directories":{}}}}\n' \
    "$FASS" "$O" "$O" > "$L/data/system/plugindatabase.json"
# Angaben der Linie: Konfigurationsdateien (Pfad relativ zur Wurzel), Antwort der mosquitto_sub-Attrappe
python3 - "$ANG" "$L" "$O" "$W/fake/sub.txt" <<'PY'
import json, os, sys
d = json.load(open(sys.argv[1])); L, O = sys.argv[2], sys.argv[3]
for pfad, text in d.get("konfig", {}).items():
    z = os.path.join(L, pfad.replace("<O>", O))
    os.makedirs(os.path.dirname(z), exist_ok=True)
    open(z, "w", encoding="utf-8", newline="").write(text)
open(sys.argv[4], "w", encoding="utf-8", newline="").write("".join(z + chr(10) for z in d.get("sub", [])))
PY
SUBRC="$(wert sub_rc)"; [ -n "$SUBRC" ] || SUBRC=27
printf '#!/bin/sh\ncat "%s/fake/sub.txt"\nexit %s\n' "$W" "$SUBRC" > "$W/fake/mosquitto_sub"
printf '#!/bin/sh\necho "$*" >> "%s/aus/pub.log"\n' "$W" > "$W/fake/mosquitto_pub"
chmod +x "$W/fake/mosquitto_sub" "$W/fake/mosquitto_pub"
cp "$W/fake/mosquitto_sub" "$W/fake/mosquitto_pub" /usr/local/bin/
# Sonde (auto_prepend_file, liegt im bin-Ordner der Linie, damit das SDK am ersten Skript denselben Plugin-Ordner erkennt):
# zaehlt php-Laeufe ueber jeden Aufrufweg (Shebang, /usr/bin/php, Kinder) und haelt fest, ob das SDK im Lauf ueberhaupt
# beruehrt wurde. Eine Linie, die php nie ruft, ist "nicht gemessen", nicht gruen.
VOR="$(wert vorlauf)"; VORZ=""
if [ -n "$VOR" ]; then
    cp "$(dirname "$0")/minutenlauf_attrappen/$VOR" "$W/vorlauf.php" || { echo "ABBRUCH: Fahrzeug-Attrappe fehlt"; exit 2; }
    VORZ="putenv('RN_ATT=$W/aus'); require_once '$W/vorlauf.php';"
fi
cat > "$L/bin/plugins/$O/_ml_sonde.php" <<EOF
<?php
$VORZ
register_shutdown_function(function () {
    \$z = array('s' => basename((string) (isset(\$_SERVER['SCRIPT_FILENAME']) ? \$_SERVER['SCRIPT_FILENAME'] : '')),
        'sdk' => class_exists('LBSystem', false) ? 1 : 0, 'gelesen' => isset(\$GLOBALS['cfgwasread']) ? 1 : 0);
    @file_put_contents('$W/aus/php_aufrufe.log', json_encode(\$z) . "\n", FILE_APPEND);
});
EOF
# Wie am Geraet (gemessen 01.11., 20-loxberry-cli.ini): include_path mit libs/phplib, Fehler auf stderr, error_reporting=22527.
# Ohne den include_path scheitert schon require_once 'loxberry_web.php' (Renault), das waere ein Scheinbefund.
printf 'include_path=".:%s/libs/phplib"\ndisplay_errors=stderr\nlog_errors=Off\nerror_reporting=22527\nhtml_errors=0\nauto_prepend_file="%s"\n' "$L" "$L/bin/plugins/$O/_ml_sonde.php" > "$W/ini/95-ml.ini"
SCAN="$(/usr/bin/php --ini | sed -n 's/^Scan for additional .ini files in: *//p')"
UMGEBUNG=(env -i "PATH=$W/fake:/usr/local/bin:/usr/bin:/bin" "HOME=$W/heim" "LANG=C" "LC_ALL=C" "PHP_INI_SCAN_DIR=$SCAN:$W/ini"
    "LBHOMEDIR=$L" "LBPHTMLAUTH=$L/webfrontend/htmlauth/plugins" "LBPHTML=$L/webfrontend/html/plugins" "LBPTEMPL=$L/templates/plugins" "LBPDATA=$L/data/plugins"
    "LBPLOG=$L/log/plugins" "LBPCONFIG=$L/config/plugins" "LBPBIN=$L/bin/plugins" "LBSHTMLAUTH=$L/webfrontend/htmlauth/system" "LBSHTML=$L/webfrontend/html/system"
    "LBSTEMPL=$L/templates/system" "LBSDATA=$L/data/system" "LBSLOG=$L/log/system" "LBSTMPFSLOG=$L/log/system_tmpfs" "LBSCONFIG=$L/config/system" "LBSBIN=$L/bin" "LBSSBIN=$L/sbin")
[ $# -gt 0 ] || { echo "ABBRUCH: keine Cron-Datei"; exit 2; }
ERLAUBT=" 0 $(wert rc_erlaubt) "
FRIST="$(wert frist)"
BEFUND=0; PHPS=0
for CF in "$@"; do
    NAME="$(basename "$CF")"
    Z="$W/$NAME.lauf"
    cp "$Q/cron/$NAME" "$Z" || { echo "FEHL $NAME fehlt"; BEFUND=1; continue; }
    ersetzen "$Z"
    IN="$(head -c 256 "$Z" | sed -n '1s/^#! *//p' | tr -d '\r' | cut -d' ' -f1)"; [ -n "$IN" ] || IN=/bin/sh
    case "$IN" in */env) IN="$(head -1 "$Z" | tr -d '\r' | sed 's/^#! *//' | cut -d' ' -f2)";; esac
    echo "Interpreter $NAME: $IN ($(readlink -f "$(command -v "$IN")" 2>/dev/null))"
    for i in 1 2; do
        : >> "$W/aus/php_aufrufe.log"
        A=$(wc -l < "$W/aus/php_aufrufe.log")
        ( cd / && "${UMGEBUNG[@]}" timeout -k 2 "${FRIST:-60}" "$IN" "$Z" ) > "$W/aus/lauf_${NAME}_$i.txt" 2>&1 < /dev/null
        RC=$?
        B=$(wc -l < "$W/aus/php_aufrufe.log")
        PHPS=$((PHPS + B - A))
        ERRZ=0
        for e in "$L/log/plugins/$O"/*.err "$L/log/plugins/$O"/cron_fehler.log; do [ -f "$e" ] && ERRZ=$((ERRZ + $(stat -c %s "$e"))); done
        echo "LAUF $NAME $i: rc=$RC php=$((B - A)) err=$ERRZ Byte"
        case "$ERLAUBT" in *" $RC "*) ;; *) echo "FEHL $NAME Lauf $i: rc=$RC"; BEFUND=1;; esac
        sleep "${ML_NACHLAUF:-1}"
    done
done
sleep "${ML_NACHLAUF:-1}"
# cron.err und alle Protokolle der Linie: Inhalt nur als Zeilenzahl und gekuerzt, Werte der Attrappe sind erfunden.
for e in "$L/log/plugins/$O"/*.err "$L/log/plugins/$O"/cron_fehler.log; do
    [ -s "$e" ] || continue
    echo "FEHL $(basename "$e") nicht leer: $(wc -l < "$e") Zeilen"
    sed -e 's/^/  | /' "$e" | sed -e "s#/opt/loxberry/##g" | cut -c1-190 | head -6
    BEFUND=1
done
TREFFER="$(grep -rlE 'Uncaught|PHP Fatal|Fatal error|PHP Parse|Parse error' "$L/log/plugins/$O" "$W/aus" /tmp 2>/dev/null)"
if [ -n "$TREFFER" ]; then
    BEFUND=1
    printf '%s\n' "$TREFFER" | while IFS= read -r t; do
        echo "FEHL Absturz in ${t#/opt/loxberry/}: $(grep -E 'Uncaught|PHP Fatal|Fatal error|PHP Parse|Parse error' "$t" | head -1 | sed -e 's#/opt/loxberry/##g' | cut -c1-200)"
    done
fi
PV="$(/usr/bin/php -n -r 'echo PHP_VERSION;')"
[ -f "$W/aus/aufrufe.log" ] && echo "Fahrzeug-Attrappe: $(wc -l < "$W/aus/aufrufe.log") Aufrufe"
echo "Broker-Attrappe: $(wc -l < "$W/aus/broker.log" 2>/dev/null || echo 0) Veroeffentlichungen, mosquitto_pub: $(wc -l < "$W/aus/pub.log" 2>/dev/null || echo 0)"
echo "SDK: php-Laeufe $(wc -l < "$W/aus/php_aufrufe.log"), davon SDK geladen $(grep -c '"sdk":1' "$W/aus/php_aufrufe.log"), general.json gelesen $(grep -c '"gelesen":1' "$W/aus/php_aufrufe.log")"
if [ "$PHPS" = 0 ]; then
    echo "ERGEBNIS NICHT_GEMESSEN php=$PV: die Cron-Datei rief php nicht auf"
    [ "$BEFUND" = 0 ] && exit 3
fi
[ "$BEFUND" = 0 ] && { echo "ERGEBNIS GRUEN php=$PV: $PHPS php-Aufrufe"; exit 0; }
echo "ERGEBNIS ROT php=$PV"; exit 1
