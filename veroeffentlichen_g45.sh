#!/bin/bash
# G45 (30.10.2026): eine Linie veroeffentlichen, Bauordner als Argument (nie parallel, keine Kette daneben).
# Aufruf: veroeffentlichen_g45.sh <bauordner> <repo> <neu> <alt> <LBPPLUGINDIR> <probe-sha256-anfang> "Commit-Text" "Release-Titel"
# Vor dem Abschluss: Probe-Zip-SHA256 muss passen und ihr Inhalt byteweise dem Bauordner gleichen; kein C2PA im Bau.
# 05.11.2026: aus dem Sitzungs-Notizblock hierher (der Notizblock verlor welle12).
# Arbeitsordner: der Elternordner von Werkzeuge/, uebersteuerbar mit LOXWERK.
cd "${LOXWERK:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}" || exit 1
P=Pruefung-Durchgang-2026-09-29
# Nachholweg (30.10.2026, Netzaussetzer nach Tag-Schub): nur der Schluss von linie_abschluss.sh -
# plugin.cfg im Tag pruefen, Release-Seite anlegen, Folgeordner. Aufruf: --nachholen <repo> <neu> <alt>
if [ "${1:-}" = "--nachholen" ]; then
  [ $# -eq 4 ] || { echo "ABBRUCH: --nachholen repo neu alt"; exit 2; }
  REPO=$2; NEU=$3; ALT=$4; T="$P/abschluss"; L="LoxBerry-Plugin-$REPO-$NEU"; R="timanders22/LoxBerry-Plugin-$REPO"
  F='s/ghp_[A-Za-z0-9]+/ghp_***/g; s/github_pat_[A-Za-z0-9_]+/github_pat_***/g; s/x-access-token:[^@]*@/x-access-token:***@/g'
  [ -f "$T/${REPO}_${NEU}_Release.md" ] || { echo "ABBRUCH: Releasetext fehlt"; exit 1; }
  PAT_EIN="$(sed -n '1p' /c/tmp_skripte/gh-token.txt | tr -d ' \r\n')"
  PV=$(printf 'Authorization: token %s\n' "$PAT_EIN" | curl -s -H @- -H 'Accept: application/vnd.github.raw' "https://api.github.com/repos/$R/contents/plugin.cfg?ref=v$NEU" | tr -d '\r' | grep -m1 '^VERSION=')
  echo "  plugin.cfg im Tag v$NEU: ${PV:-nicht lesbar}"
  [ "$PV" = "VERSION=$NEU" ] || { echo "ABBRUCH: plugin.cfg im Tag passt nicht"; exit 1; }
  N=$(grep -o "[0-9]* files changed" "$T/veroeffentlichen_${REPO}_${NEU}.txt" | head -1 | cut -d' ' -f1)
  PAT_EIN="$PAT_EIN" python Werkzeuge/release_seite.py "$REPO" "v$NEU" "$(cygpath -w "$T/${REPO}_${NEU}_Release.md")" "$NEU" "$ALT" "${N:-?} Dateien" --anlegen 2>&1 | sed -E "$F" > "$T/release_${REPO}_${NEU}.txt"
  rc=${PIPESTATUS[0]}; unset PAT_EIN
  grep -E "HTTP|Titel" "$T/release_${REPO}_${NEU}.txt" | sed 's/^/ /'
  if [ "$rc" != 0 ] || ! grep -qE "HTTP 201|liegt schon" "$T/release_${REPO}_${NEU}.txt"; then echo "ABBRUCH: Release-Seite nicht angelegt"; exit 1; fi
  NN=$(python -c "import sys;v=sys.argv[1].split('.');v[-1]=str(int(v[-1])+1);print('.'.join(v))" "$NEU")
  if [ -e "LoxBerry-Plugin-$REPO-$NN" ]; then echo "  Ordner $NN liegt schon"; else
    cp -r "$L" "LoxBerry-Plugin-$REPO-$NN" && python Werkzeuge/fassung_setzen.py "LoxBerry-Plugin-$REPO-$NN" "$NN" 2>&1 | tail -1 | sed 's/^/  /'
    python Werkzeuge/packen.py "LoxBerry-Plugin-$REPO-$NN" --grundlinie "$L.zip" 2>&1 | grep byteweise | sed 's/^/ /'
  fi
  echo "FERTIG (nachgeholt) $REPO $NEU"; exit 0
fi
[ $# -eq 8 ] || { echo "ABBRUCH: 8 Argumente noetig, $# erhalten"; exit 2; }
bau=$1; repo=$2; neu=$3; alt=$4; dir=$5; sha=$6; t1=$7; t2=$8
case "$bau" in vb_*_bau) ;; *) echo "ABBRUCH: Bauordner '$bau' ist kein vb_*_bau"; exit 2 ;; esac
[ -d "$P/$bau" ] || { echo "ABBRUCH: $P/$bau fehlt"; exit 2; }
echo "=== $bau $repo $neu (alt $alt, $dir) $(date +%H:%M:%S)"
z="LoxBerry-Plugin-$repo-${neu}_Probe_zum_Hochladen.zip"
python -I -c "
import hashlib,os,sys,zipfile
z,b,s=sys.argv[1:4]
h=hashlib.sha256(open(z,'rb').read()).hexdigest()
if not h.startswith(s): sys.exit('ABBRUCH: Probe-Zip SHA256 %s statt %s' % (h[:8], s))
zf=zipfile.ZipFile(z); zi={i.filename:hashlib.md5(zf.read(i)).hexdigest() for i in zf.infolist() if not i.is_dir()}
oi={}
for dp,dn,fn in os.walk(b):
    for f in fn:
        p=os.path.join(dp,f); oi[os.path.relpath(p,b).replace(os.sep,'/')]=hashlib.md5(open(p,'rb').read()).hexdigest()
if oi!=zi: sys.exit('ABBRUCH: Bau weicht von der Probe-Zip ab (%d Dateien)' % len(set(oi.items())^set(zi.items())))
c=[k for k in oi if k.lower().endswith(('.png','.svg','.jpg','.jpeg','.gif','.webp','.ico')) and any(m in open(os.path.join(b,k),'rb').read() for m in (b'c2pa',b'caBX',b'jumb'))]
if c: sys.exit('ABBRUCH: C2PA im Bau: %s' % c)
print('  Probe %s = Bau (%d Dateien), kein C2PA' % (h[:8], len(oi)))
" "$z" "$P/$bau" "$sha" || exit 3
bash $P/linie_abschluss.sh $P/$bau $repo $neu $alt "$t1" "$t2" --veroeffentlichen LBPPLUGINDIR=$dir \
  > $P/${bau}_abschluss_g45.txt 2>&1 < /dev/null
rc=$?
echo "rc=$rc"
grep -E 'GLEICH|ABBRUCH|HALT|Pruefungen|release.cfg|plugin.cfg im Tag|HTTP|Titel|Tag-Archiv|files changed|FERTIG|Fehl' $P/${bau}_abschluss_g45.txt | sed -E 's/(ghp_|github_pat_)[A-Za-z0-9_]+/***/g' | tail -14
# 07.11.2026: Liegen die Einbindungsbilder dieser Linie im Musterprojekt-Repository? Nur ein Hinweis, blockiert nichts.
# Anlass: Weatherdata-Seiten vom 05.11. kamen nie ins Repository LoxBerry-Plugins-Musterprojekt (7 Bilder aus 4 Linien).
# Vorher den lokalen Klon auf origin/main bringen, sonst misst die Pruefung einen alten Stand.
if [ "$rc" = 0 ]; then
  MPK="LoxBerry-Plugins-Musterprojekt"
  git -C "$MPK" -c core.autocrlf=false pull -q --ff-only origin main >/dev/null 2>&1 || echo "  HINWEIS Musterprojekt: lokaler Klon nicht nachziehbar - Pruefung misst evtl. alten Stand"
  mpb=$(PYTHONDONTWRITEBYTECODE=1 python Werkzeuge/musterprojekt_bilder_pruefen.py "LoxBerry-Plugin-$repo-$neu" 2>&1); mprc=$?
  if [ "$mprc" = 0 ]; then echo "  Musterprojekt: Einbindungsbilder vorhanden"
  else echo "$mpb" | grep -E "FEHLT|NICHT PRUEFBAR" | sed 's/^/  HINWEIS /'; echo "  HINWEIS Musterprojekt: Seiten und Bilder ins Repository LoxBerry-Plugins-Musterprojekt nachziehen (Regeln/11)"; fi
fi
echo "=== fertig $(date +%H:%M:%S)"
exit $rc
