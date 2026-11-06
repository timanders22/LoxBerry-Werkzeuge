#!/bin/bash
# Eine Linie veroeffentlichen, in der Reihenfolge aus REGELN_4.
#
#   Schritt 1  Inhalt schieben, .cfg bleiben auf der ALTEN Nummer
#   Schritt 2  Tag anlegen und schieben
#   Schritt 3  Tag NACHWEISEN (ls-remote; das Archiv ist von hier nicht messbar)
#   Schritt 4  .cfg auf die neue Nummer, Adressen auf den neuen Tag, schieben
#
# Der Zugangsschluessel kommt aus der Umgebung ($PAT_EIN) und wird NIE in eine
# Datei geschrieben und NIE als Argument uebergeben (git: git_gh, siehe unten);
# nach dem Klonen und am Ende wird .git/config gegengeprueft.
#
# Aufruf:  PAT_EIN=... linie_veroeffentlichen.sh NAME NEUE_FASSUNG MELDUNGSDATEI
#   Quelle ist GENAU der Ordner LoxBerry-Plugin-NAME-NEUE_FASSUNG (seit 08.10.2026).
#   Rueckgabe: 0 Erfolg, 2 keine Aenderung, 3 Schluessel abgelehnt, 1 sonst.
set -u
# Arbeitsordner: der Elternordner von Werkzeuge/, uebersteuerbar mit LOXWERK.
B="${LOXWERK:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PAT="${PAT_EIN:-}"; n="${1:-}"; soll="${2:-}"; meldung="${3:-}"
[ -n "$n" ] && [ -n "$soll" ] || { echo "ABBRUCH: Aufruf: PAT_EIN=... linie_veroeffentlichen.sh NAME NEUE_FASSUNG MELDUNGSDATEI"; exit 1; }
[ -n "$PAT" ] || { echo "$n ABBRUCH: \$PAT_EIN ist leer - nichts geschoben"; exit 1; }
# DER QUELLORDNER WIRD GENANNT, NICHT GERATEN - GEAENDERT 08.10.2026 (Werkzeug-P3).
#
# Bis dahin stand hier
#
#   o=$(cd "$B" && ls -d LoxBerry-Plugin-"$n"-*/ | sed 's|/$||' | sort -V | tail -1)
#
# - der Ordner mit der HOECHSTEN Nummer. Am 08.10.2026 war der Schluessel
# abgelaufen, linie_abschluss.sh meldete trotzdem FERTIG und legte den
# Folgeordner Sprachsteuerung-0.12.1 an. Der zweite Lauf ("0.12.0") nahm
# genau diesen Ordner: Tag v0.12.0 trug plugin.cfg 0.12.1. Der Fehllauf
# hinterlaesst also den Ordner, der beim naechsten Lauf gewinnt.
#
# Jetzt gilt: Argument 2 IST die neue Fassung, also ist der Ordner
# LoxBerry-Plugin-<NAME>-<NEUE_FASSUNG>, und seine plugin.cfg traegt genau eine
# Zeile VERSION=<NEUE_FASSUNG>. Liegt ein hoeherer Ordner daneben, bleibt er
# liegen. Gemessen am 08.10.2026: 663 von 664 Ordnern im Arbeitsordner tragen
# genau eine VERSION-Zeile mit der Nummer aus dem Ordnernamen; der eine ist
# Zigbee2MqttNG-4.1.0 (__VERSION__, eigener Workflow, nie ueber dieses Werkzeug).
o="$B/LoxBerry-Plugin-$n-$soll"
[ -d "$o" ] || { echo "$n ABBRUCH: kein Ordner LoxBerry-Plugin-$n-$soll"; exit 1; }
pv=$(tr -d '\r' < "$o/plugin.cfg" 2>/dev/null | grep '^VERSION=')
[ "$pv" = "VERSION=$soll" ] || { echo "$n ABBRUCH: plugin.cfg in LoxBerry-Plugin-$n-$soll nennt '$(echo $pv)' statt VERSION=$soll"; exit 1; }
# DER SCHLUESSEL WIRD VORAB GEFRAGT - GEAENDERT 08.10.2026 (Werkzeug-P3).
#
# Ein abgelaufener Schluessel zeigte sich bisher als "Zweig nicht messbar"
# (ls-remote antwortet leer) - ein Satz, der nach einem Befund am Repository
# klingt. GET /user sagt es eindeutig: 200 = Schluessel gilt, 401 = abgelaufen
# oder widerrufen. Der Kopf geht ueber die Standardeingabe (-H @-), damit der
# Schluessel nicht in der Prozessliste steht; ausgegeben wird nur der Code.
code=$(printf 'Authorization: token %s\n' "$PAT" | curl -s -o /dev/null -w '%{http_code}' --max-time 30 \
  -H @- -H 'User-Agent: loxberry-haus' https://api.github.com/user)
case "$code" in
  200) ;;
  401) echo "$n ABBRUCH: Zugangsschluessel abgelehnt (GET /user: HTTP 401 - abgelaufen oder widerrufen); nichts geschoben"; exit 3 ;;
  *)   echo "$n ABBRUCH: Schluesselpruefung GET /user antwortete HTTP ${code:-?} statt 200; nichts geschoben"; exit 3 ;;
esac
R="https://github.com/timanders22/LoxBerry-Plugin-$n.git"
# DER SCHLUESSEL GEHT NICHT MEHR UEBER DIE ADRESSE - GEAENDERT 09.10.2026 (Werkzeug-P5).
#
# Bis dahin stand hier RA="https://x-access-token:$PAT@github.com/...", und
# ls-remote, clone und beide push bekamen diese Adresse als Argument: der
# Schluessel stand in der Prozessliste (git und git-remote-https), und der
# Klon trug ihn in .git/config als remote.origin.url, bis "git remote set-url"
# ihn nach dem ersten Schub ueberschrieb - brach der Lauf vorher ab, blieb er
# in /tmp/v_<NAME>/.git/config liegen.
#
# Jetzt laeuft jeder git-Aufruf, der GitHub erreicht, ueber git_gh. Der
# Schluessel geht als Kopf "Authorization: Basic base64(x-access-token:PAT)"
# ueber GIT_CONFIG_COUNT/GIT_CONFIG_KEY_n/GIT_CONFIG_VALUE_n (git >= 2.31) -
# Umgebung, kein Argument, keine Datei; git schreibt diese Werte nicht in den
# Klon. Der Kopf gilt nur fuer https://github.com/ (http.<url>.extraheader).
# Gewaehlt statt GIT_ASKPASS: der Kopf geht beim ERSTEN Aufruf mit, es kommt
# also kein 401 und damit keine Rueckfrage an Zugangshelfer. Auf diesem Rechner
# steht credential.helper=manager (Git fuer Windows, systemweit); mit ASKPASS
# fragt git ZUERST den Helfer (der einen alten Schluessel liefern oder ein
# Fenster oeffnen kann) und legt den Schluessel nach Erfolg dort AB. Fuer den
# Fall, dass GitHub doch 401 sagt, wird der Helfer hier geleert und die
# Rueckfrage abgeschaltet: der Aufruf scheitert, statt zu warten.
# base64 liest den Schluessel ueber die Pipe (printf ist eingebaut).
# Ein schon gesetztes GIT_CONFIG_COUNT bleibt erhalten; angehaengt wird dahinter.
#
# MIT Zugangsschluessel abfragen, nicht anonym. GitHub drosselt unangemeldete
# Abfragen, und die Drosselung sieht hier aus wie ein fehlendes Repository:
# "could not read Username" -> leere Ausgabe -> "Zweig nicht messbar".
# Am 02.09.2026 hat das eine Veroeffentlichung angehalten, obwohl mit
# Schluessel alles erreichbar war. Ein Abbruch, der wie ein Befund aussieht
# und keiner ist, kostet mehr als die zwei Zeichen hier.
B64=$(printf 'x-access-token:%s' "$PAT" | base64 | tr -d '\r\n')
[ -n "$B64" ] || { echo "$n ABBRUCH: base64 lieferte nichts - nichts geschoben"; exit 1; }
git_gh() (
  i=${GIT_CONFIG_COUNT:-0}
  export "GIT_CONFIG_KEY_$i=http.https://github.com/.extraheader" "GIT_CONFIG_VALUE_$i=Authorization: Basic $B64"
  i=$((i+1))
  export "GIT_CONFIG_KEY_$i=credential.helper" "GIT_CONFIG_VALUE_$i="
  export GIT_CONFIG_COUNT=$((i+1)) GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never
  exec git "$@"
)
# Schluesselspur in .git/config des Klons: nur Bash-Bordmittel ($(<), case),
# damit der Schluessel auch hier in keinem Argument steht. 0 = keine Spur.
spur() {
  local cfg
  cfg=$(<.git/config) || { echo 1; return; }
  case "$cfg" in
    *"$PAT"*|*"$B64"*|*x-access-token*|*extraheader*|*github_pat_*) echo 1 ;;
    *) echo 0 ;;
  esac
}
zweig=$(git_gh ls-remote --symref "$R" HEAD 2>/dev/null | sed -n 's|^ref: refs/heads/\(\S*\).*|\1|p')
[ -n "$zweig" ] || { echo "$n ABBRUCH: Zweig nicht messbar"; exit 1; }
w=/tmp/v_$n; rm -rf "$w"
git_gh clone -q "$R" "$w" || { echo "$n ABBRUCH: clone"; exit 1; }
cd "$w"
[ "$(spur)" = 0 ] || { echo "$n ABBRUCH: Schluesselspur in .git/config des Klons - nichts geschoben"; exit 1; }
alt=$(tr -d '\r' <release.cfg | grep -m1 '^VERSION=' | cut -d= -f2)
# KEIN rsync AUF DIESEM RECHNER? DANN DER NACHBAU (seit 13.09.2026).
#
# Gemessen: `command -v rsync` ist hier leer. Dieses Skript hat kein
# `set -e` - das rsync scheiterte still, der Klon blieb beim alten
# Inhalt, `git add -A` fand nichts, und der Lauf endete mit
# "ABBRUCH: keine Aenderung". Das liest sich wie ein Befund an der Linie
# und ist einer am Rechner; betroffen waeren alle 49 Linien.
#
# Werkzeuge/spiegeln_ohne_rsync.py bildet die Zeile darunter nach, samt
# der Ausnahmen, die --delete NICHT anfassen darf. Mit vorhandenem rsync
# laeuft alles wie bisher; ohne wird gespiegelt - und ein Fehlschlag
# bricht ab, statt den Lauf leer weiterlaufen zu lassen.
if command -v rsync >/dev/null 2>&1; then
rsync -rt --delete --no-perms --no-owner --no-group --exclude=.git --exclude=.gitignore \
  --exclude=.gitattributes --exclude='*.zip' --exclude='STAND_IN_ARBEIT.md' --exclude='FREIGABE_*' "$o/" ./
else
  python3 "$B/Werkzeuge/spiegeln_ohne_rsync.py" "$o" . \
    || { echo "$n ABBRUCH: Spiegelung (kein rsync, Nachbau scheiterte)"; exit 1; }
fi
git checkout -- release.cfg prerelease.cfg 2>/dev/null
# .gitattributes wird NICHT uebertragen - Entscheidung des Hausherrn, zweimal.
#
# Das rsync nimmt sie von der Uebertragung aus, damit --delete eine
# repository-eigene (Fremd-Fork, z. B. Smartmeter-classic) nie loescht. Am
# 06.09.2026, 00:21 stand hier voruebergehend eine Kopierzeile, die eine im
# Arbeitsordner liegende .gitattributes in den Klon uebernahm - mit der
# Begruendung, eine neu angelegte komme sonst nie hinaus (gemessen an
# Bewaesserung 0.9.21).
#
# Der Hausherr hat die Frage am selben Abend zweimal entschieden, beide Male
# gegen die Uebertragung: bei Bewaesserung 0.9.21 ("nicht mituebertragen") und
# noch einmal, nachdem die Kopierzeile bei Abfahrtsassistent 1.6.8 gewirkt und
# die Datei in den Tag v1.6.8 gebracht hatte. Die Zeile ist deshalb wieder
# fort.
#
# Wer sie erneut einbauen will, aendert damit den Auslieferungsweg aller 49
# Linien - das gehoert entschieden, nicht nebenbei gemacht. Und wer dieses
# Werkzeug benutzt, liest es vorher: an diesem Ordner arbeitet mehr als ein
# Schreiber, und was gestern hier stand, muss heute nicht mehr stimmen.
# Dateimodi - GEAENDERT 05.09.2026.
#
# Bis dahin stand hier "verfolgte Dateien wie im Zweig, neue auf 644". Das
# hielt den Mount davon ab, sein 700 in den Baum zu tragen (REGELN_1,
# Kapitel 26) - und schrieb zugleich jeden FALSCHEN Modus des Zweiges fort.
# Anlass: dpkg/apt stand in der Linie MarstekVenus auf 100755. Der Installer
# LIEST die Datei; packen.py setzt sie im Archiv seit jeher auf 0644. Ohne
# einen Commit von Hand waere sie bei jeder weiteren Fassung 100755 geblieben,
# ohne dass irgendetwas rot geworden waere.
#
# Jetzt gilt dieselbe Aufteilung wie in packen.py (Funktion rechte()), damit
# Zweig, Tag und Archiv dasselbe sagen:
#
#   755  bin/ cron/ daemon/ sudoers/ , uninstall/uninstall , *.sh *.pl *.cgi
#   644  alles Uebrige
#
# Am 05.09.2026 ueber alle 49 Zweige gemessen: von 1496 Dateien wuerden 495
# den Modus wechseln - 305 hinauf (postinstall.sh, preupgrade.sh,
# uninstall/uninstall, cron.01min, daemon/daemon, sudoers/sudoers) und 190
# hinab (Symbole, Vorlagen, README, die drei .cfg, dpkg/apt). Beide
# Richtungen sind Berichtigungen; die Archive tragen die neuen Werte laengst.
# Wirksam wird es je Linie erst bei ihrer naechsten Veroeffentlichung.
#
# .gitignore und .gitattributes: das rsync nimmt sie von der UEBERTRAGUNG aus
# (--exclude), es loescht sie aber nicht aus dem Klon - sie liegen also da und
# bekommen die Regel wie alles andere, also 644. Beim Eichen am 06.09.2026
# ist genau das aufgefallen: die erste Erwartung lautete "wird uebersprungen",
# und der Lauf hat sie widerlegt. Sechs Zweige fuehren .gitignore auf 100755;
# 644 ist dort richtig, die Zeile bleibt also so - aber sie steht hier, damit
# niemand den Kommentar fuer eine Zusicherung haelt, die der Code nicht gibt.
soll_modus() {
  # Matter2Lox-k1 (08.10.2026): *.whl ist ein Archiv, kein Programm - auch unter
  # bin/vendor/ 644 (wie packen.py, rechte()). Muss vor bin/* stehen.
  case "$1" in
    *.whl)                                               echo 644 ;;
    bin/*|cron/*|daemon/*|sudoers/*|uninstall/uninstall) echo 755 ;;
    *.sh|*.pl|*.cgi)                                     echo 755 ;;
    *)                                                   echo 644 ;;
  esac
}
: > /tmp/modi_$n.txt
git ls-tree -r HEAD | while read -r m t h f; do
  [ -e "$f" ] || continue
  s=$(soll_modus "$f")
  chmod "$s" "$f"
  [ "$m" = "100$s" ] || echo "$f: 100$s statt $m" >> /tmp/modi_$n.txt
done
git status --short --untracked-files=all | grep '^??' | cut -c4- | while IFS= read -r f; do
  [ -f "$f" ] && chmod "$(soll_modus "$f")" "$f"
done
git add -A
# DER MODUS GEHT UEBER DEN INDEX - GEAENDERT 24.09.2026.
#
# Bis hierher stand nur das chmod oben, und die Meldung "Dateimodi
# berichtigt" kam, sobald ein Modus im Zweig vom Soll abwich. Gewirkt hat das
# auf diesem Rechner NIE: Git fuer Windows schreibt beim Klonen
# core.filemode=false in die .git/config des Klons, und dann sieht git kein
# chmod - auch nicht mit "-c core.fileMode=true" beim add (am Wegwerfklon
# gemessen). LoxoneIcons 2.0.9 meldete 5 Berichtigungen, der Tag trug alle 5
# weiter als 100644. Wirksam ist nur "git update-index --chmod". Gemeldet wird
# deshalb erst, was danach IM INDEX steht, und eine Abweichung, die bleibt,
# bricht ab. Nur 100644/100755 werden angefasst (kein Verweis, kein Submodul).
git ls-files -s | while read -r m h st f; do
  case "$m" in 100644|100755) ;; *) continue ;; esac
  s=$(soll_modus "$f")
  [ "$m" = "100$s" ] && continue
  if [ "$s" = 755 ]; then git update-index --chmod=+x -- "$f"; else git update-index --chmod=-x -- "$f"; fi
done
rest=$(git ls-files -s | while read -r m h st f; do
  case "$m" in 100644|100755) ;; *) continue ;; esac
  [ "$m" = "100$(soll_modus "$f")" ] || echo "$f"
done)
[ -z "$rest" ] || { echo "$n ABBRUCH: Dateimodi im Index weichen weiter ab: $(echo $rest)"; rm -f /tmp/modi_$n.txt; exit 1; }
# Ein stiller Moduswechsel waere derselbe Fehler in gruen: was sich aendert,
# wird benannt - jetzt NACH der Nachpruefung im Index.
if [ -s /tmp/modi_$n.txt ]; then
  echo "$n  Dateimodi berichtigt ($(wc -l < /tmp/modi_$n.txt)), im Index nachgeprueft:"
  sed 's/^/    /' /tmp/modi_$n.txt
fi
rm -f /tmp/modi_$n.txt
stat=$(git diff --cached --shortstat | sed 's/^ *//')
[ -n "$stat" ] || { echo "$n ABBRUCH: keine Aenderung"; exit 2; }
if [ -n "$meldung" ] && [ -f "$meldung" ]; then
  sed -e "s/{NAME}/$n/g" -e "s/{NEU}/$soll/g" -e "s/{ALT}/$alt/g" -e "s/{STAT}/$stat/g" "$meldung" > /tmp/m_$n.txt
else
  printf '%s %s\n\nGeaendert gegenueber v%s: %s.\n' "$n" "$soll" "$alt" "$stat" > /tmp/m_$n.txt
fi
git -c user.name='timanders22' -c user.email='timanders22@users.noreply.github.com' commit -q -F /tmp/m_$n.txt || { echo "$n ABBRUCH: commit"; exit 1; }
git -c user.name='timanders22' -c user.email='timanders22@users.noreply.github.com' tag -a "v$soll" -m "$n $soll"
git_gh push --quiet "$R" "$zweig" "v$soll" || { echo "$n ABBRUCH: push"; exit 1; }
c1=$(git rev-parse --short HEAD)
# Schritt 3: Tag nachweisen, BEVOR die Nummer in den Zweig geht
tsha=$(git_gh ls-remote "$R" "refs/tags/v$soll^{}" | awk '{print $1}')
[ -n "$tsha" ] || { echo "$n ABBRUCH: Tag v$soll nicht fern"; exit 1; }
[ "${tsha:0:7}" = "$c1" ] || { echo "$n ABBRUCH: Tag ${tsha:0:7} != Zweig $c1"; exit 1; }
# Schritt 4
#
# GEAENDERT 08.09.2026: hier stand
#
#   echo "$out" | grep -q "beide Adressen in beiden .cfg nennen v$soll" || ABBRUCH
#
# - ein Waechter auf den WORTLAUT der Ausgabe von fassung_setzen.py. Am
# 07.09.2026 hat er bei Dashboard 0.9.19 einen vollstaendig richtigen Lauf
# angehalten: fassung_setzen.py hatte die beiden .cfg im Ordner schon gesetzt
# und meldete deshalb "nichts zu tun" statt des erwarteten Satzes. Inhalt und
# Tag standen da bereits; liegen blieb ausgerechnet der Schub der beiden .cfg -
# das Auto-Update haette weiter die ALTE Nummer angeboten, und die neue Fassung
# waere nie angekommen. Nachgeholt werden musste es mit schritt4_nachholen.sh.
#
# Gemessen wird jetzt der ZUSTAND der beiden Dateien, nicht der Wortlaut:
# VERSION, ARCHIVEURL und INFOURL - je Datei genau einmal, und die beiden
# Adressen muessen v$soll nennen. Ueber alle Ordner gezaehlt tragen alle 456
# .cfg genau diese drei Schluessel.
#
# Gelesen werden nur ZEILENANFAENGE (sed '^KEY='). Die Dateien fuehren lange
# Kommentarkoepfe, in denen alte Nummern vorkommen ("bis 2.1.8", "Alt (bis
# 2.2.5)"); eine Suche ueber die ganze Datei traefe die und waere derselbe
# Fehler wie der alte Waechter, nur eine Ebene tiefer.
out=$(cd "$B" && python3 Werkzeuge/fassung_setzen.py "$(basename "$o")" "$soll" --auch-release --trotzdem 2>&1)
maengel=""
for c in release.cfg prerelease.cfg; do
  if [ ! -f "$o/$c" ]; then maengel="$maengel $c:fehlt"; continue; fi
  roh=$(tr -d '\r' < "$o/$c")
  for schl in VERSION ARCHIVEURL INFOURL; do
    anz=$(printf '%s\n' "$roh" | grep -c "^$schl=")
    if [ "$anz" != "1" ]; then maengel="$maengel $c:$schl x$anz"; continue; fi
    wert=$(printf '%s\n' "$roh" | sed -n "s/^$schl=//p")
    case "$schl" in
      VERSION) [ "$wert" = "$soll" ] || maengel="$maengel $c:VERSION=$wert" ;;
      *)       case "$wert" in *"v$soll"*) ;; *) maengel="$maengel $c:$schl->$wert" ;; esac ;;
    esac
  done
done
if [ -n "$maengel" ]; then
  echo "$n ABBRUCH fassung_setzen (Zustand der .cfg):$maengel"
  echo "$out" | tail -3
  exit 1
fi
cp "$o/release.cfg" "$o/prerelease.cfg" .
git add -A
git -c user.name='timanders22' -c user.email='timanders22@users.noreply.github.com' commit -q -m "Schritt 4: release.cfg und prerelease.cfg auf $soll, Adressen auf v$soll

Tag v$soll steht (Tag-Commit = Zweig-Commit $c1)."
git_gh push --quiet "$R" "$zweig" || { echo "$n ABBRUCH: push Schritt 4"; exit 1; }
# "git remote set-url origin $R" nach jedem Schub ist entfallen: origin ist seit
# dem Klonen $R, ohne Schluessel. Die Spalte PAT zaehlt jetzt mit spur().
printf '%-28s %-7s %-8s -> %-8s  %-38s Tag %s  Zweig %s  PAT %s\n' \
  "$n" "$zweig" "$alt" "$soll" "$stat" "$c1" "$(git rev-parse --short HEAD)" "$(spur)"
