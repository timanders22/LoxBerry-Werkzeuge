#!/bin/bash
# Schritt 4 nachholen, wenn der Schub daran gescheitert ist (Proxy, Netz).
# Setzt voraus: Inhalt und Tag stehen schon, die .cfg im Ordner sind gesetzt.
set -u
# Arbeitsordner: der Elternordner von Werkzeuge/, uebersteuerbar mit LOXWERK.
B="${LOXWERK:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PAT="$PAT_EIN"; n="$1"; soll="$2"
o=$(cd "$B" && ls -d LoxBerry-Plugin-"$n"-*/ 2>/dev/null | sed 's|/$||' | sort -V | tail -1); o="$B/$o"
R="https://github.com/timanders22/LoxBerry-Plugin-$n.git"
zweig=$(git ls-remote --symref "$R" HEAD | sed -n 's|^ref: refs/heads/\(\S*\).*|\1|p')
tsha=$(git ls-remote "$R" "refs/tags/v$soll^{}" | awk '{print $1}')
[ -n "$tsha" ] || { echo "$n ABBRUCH: Tag v$soll fehlt fern"; exit 1; }
w=/tmp/n_$n; rm -rf "$w"
git clone -q "https://x-access-token:$PAT@github.com/timanders22/LoxBerry-Plugin-$n.git" "$w" || exit 1
cd "$w"
[ "$(git rev-parse HEAD)" = "$tsha" ] || { echo "$n ABBRUCH: Zweig $(git rev-parse --short HEAD) != Tag ${tsha:0:7}"; exit 1; }
cp "$o/release.cfg" "$o/prerelease.cfg" .
git add -A
[ -n "$(git diff --cached --name-only)" ] || { echo "$n: nichts nachzuholen"; exit 0; }
git -c user.name='timanders22' -c user.email='timanders22@users.noreply.github.com' commit -q -m "Schritt 4: release.cfg und prerelease.cfg auf $soll, Adressen auf v$soll

Tag v$soll steht (Tag-Commit = Zweig-Commit ${tsha:0:7})."
git push --quiet "https://x-access-token:$PAT@github.com/timanders22/LoxBerry-Plugin-$n.git" "$zweig" || { echo "$n ABBRUCH: push"; exit 1; }
git remote set-url origin "$R"
printf '%-28s Schritt 4 nachgeholt: %s   PAT %s\n' "$n" "$(git rev-parse --short HEAD)" "$(grep -c github_pat .git/config)"
