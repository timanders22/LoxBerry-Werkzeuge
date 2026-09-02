#!/bin/bash
# Eine Linie veroeffentlichen, in der Reihenfolge aus REGELN_4.
#
#   Schritt 1  Inhalt schieben, .cfg bleiben auf der ALTEN Nummer
#   Schritt 2  Tag anlegen und schieben
#   Schritt 3  Tag NACHWEISEN (ls-remote; das Archiv ist von hier nicht messbar)
#   Schritt 4  .cfg auf die neue Nummer, Adressen auf den neuen Tag, schieben
#
# Der Zugangsschluessel kommt aus der Umgebung ($PAT_EIN) und wird NIE in eine
# Datei geschrieben; nach jedem Schub wird .git/config gegengeprueft.
#
# Aufruf:  PAT_EIN=... linie_veroeffentlichen.sh NAME NEUE_FASSUNG MELDUNGSDATEI
set -u
# Arbeitsordner: der Elternordner von Werkzeuge/, uebersteuerbar mit LOXWERK.
B="${LOXWERK:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PAT="$PAT_EIN"; n="$1"; soll="$2"; meldung="${3:-}"
o=$(cd "$B" && ls -d LoxBerry-Plugin-"$n"-*/ 2>/dev/null | sed 's|/$||' | sort -V | tail -1)
[ -n "$o" ] || { echo "$n ABBRUCH: kein Ordner"; exit 1; }
o="$B/$o"
R="https://github.com/timanders22/LoxBerry-Plugin-$n.git"
# MIT Zugangsschluessel abfragen, nicht anonym. GitHub drosselt unangemeldete
# Abfragen, und die Drosselung sieht hier aus wie ein fehlendes Repository:
# "could not read Username" -> leere Ausgabe -> "Zweig nicht messbar".
# Am 02.09.2026 hat das eine Veroeffentlichung angehalten, obwohl mit
# Schluessel alles erreichbar war. Ein Abbruch, der wie ein Befund aussieht
# und keiner ist, kostet mehr als die zwei Zeichen hier.
RA="https://x-access-token:$PAT@github.com/timanders22/LoxBerry-Plugin-$n.git"
zweig=$(git ls-remote --symref "$RA" HEAD 2>/dev/null | sed -n 's|^ref: refs/heads/\(\S*\).*|\1|p')
[ -n "$zweig" ] || { echo "$n ABBRUCH: Zweig nicht messbar"; exit 1; }
w=/tmp/v_$n; rm -rf "$w"
git clone -q "https://x-access-token:$PAT@github.com/timanders22/LoxBerry-Plugin-$n.git" "$w" || { echo "$n ABBRUCH: clone"; exit 1; }
cd "$w"
alt=$(tr -d '\r' <release.cfg | grep -m1 '^VERSION=' | cut -d= -f2)
rsync -rt --delete --no-perms --no-owner --no-group --exclude=.git --exclude=.gitignore \
  --exclude=.gitattributes --exclude='*.zip' --exclude='STAND_IN_ARBEIT.md' --exclude='FREIGABE_*' "$o/" ./
git checkout -- release.cfg prerelease.cfg 2>/dev/null
# Dateimodi: verfolgte Dateien wie im Zweig, neue auf 644 - sonst traegt der
# Mount sein 700 in den Baum (siehe REGELN_1, Kapitel 26).
git ls-tree -r HEAD | while read -r m t h f; do
  [ -e "$f" ] || continue
  [ "$m" = "100755" ] && chmod 755 "$f" || chmod 644 "$f"
done
git status --short --untracked-files=all | grep '^??' | cut -c4- | while IFS= read -r f; do [ -f "$f" ] && chmod 644 "$f"; done
git add -A
stat=$(git diff --cached --shortstat | sed 's/^ *//')
[ -n "$stat" ] || { echo "$n ABBRUCH: keine Aenderung"; exit 2; }
if [ -n "$meldung" ] && [ -f "$meldung" ]; then
  sed -e "s/{NAME}/$n/g" -e "s/{NEU}/$soll/g" -e "s/{ALT}/$alt/g" -e "s/{STAT}/$stat/g" "$meldung" > /tmp/m_$n.txt
else
  printf '%s %s\n\nGeaendert gegenueber v%s: %s.\n' "$n" "$soll" "$alt" "$stat" > /tmp/m_$n.txt
fi
git -c user.name='timanders22' -c user.email='timanders22@users.noreply.github.com' commit -q -F /tmp/m_$n.txt || { echo "$n ABBRUCH: commit"; exit 1; }
git -c user.name='timanders22' -c user.email='timanders22@users.noreply.github.com' tag -a "v$soll" -m "$n $soll"
git push --quiet "https://x-access-token:$PAT@github.com/timanders22/LoxBerry-Plugin-$n.git" "$zweig" "v$soll" || { echo "$n ABBRUCH: push"; exit 1; }
git remote set-url origin "$R"
c1=$(git rev-parse --short HEAD)
# Schritt 3: Tag nachweisen, BEVOR die Nummer in den Zweig geht
tsha=$(git ls-remote "$RA" "refs/tags/v$soll^{}" | awk '{print $1}')
[ -n "$tsha" ] || { echo "$n ABBRUCH: Tag v$soll nicht fern"; exit 1; }
[ "${tsha:0:7}" = "$c1" ] || { echo "$n ABBRUCH: Tag ${tsha:0:7} != Zweig $c1"; exit 1; }
# Schritt 4
out=$(cd "$B" && python3 Werkzeuge/fassung_setzen.py "$(basename "$o")" "$soll" --auch-release --trotzdem 2>&1)
echo "$out" | grep -q "beide Adressen in beiden .cfg nennen v$soll" || { echo "$n ABBRUCH fassung_setzen: $(echo "$out"|tail -3)"; exit 1; }
cp "$o/release.cfg" "$o/prerelease.cfg" .
git add -A
git -c user.name='timanders22' -c user.email='timanders22@users.noreply.github.com' commit -q -m "Schritt 4: release.cfg und prerelease.cfg auf $soll, Adressen auf v$soll

Tag v$soll steht (Tag-Commit = Zweig-Commit $c1)."
git push --quiet "https://x-access-token:$PAT@github.com/timanders22/LoxBerry-Plugin-$n.git" "$zweig" || { echo "$n ABBRUCH: push Schritt 4"; exit 1; }
git remote set-url origin "$R"
printf '%-28s %-7s %-8s -> %-8s  %-38s Tag %s  Zweig %s  PAT %s\n' \
  "$n" "$zweig" "$alt" "$soll" "$stat" "$c1" "$(git rev-parse --short HEAD)" "$(grep -c github_pat .git/config)"
