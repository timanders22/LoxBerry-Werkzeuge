#!/bin/bash
# Laeuft auf: Windows, Git Bash. Fuehrt EINEN Befehl unter der Kettensperre aus.
#
# Werkzeug-L1 (02.10.2026): Alle Ketten (kette_linie.sh) teilen die Attrappe
# Werkzeuge/lb und nehmen deshalb die Sperre Pruefung-Durchgang-2026-09-29/.kette_sperre.
# Proben, die ebenfalls in Werkzeuge/lb schreiben (rendern.py, wirkungstest.py,
# eigene Vorher/Nachher-Laeufe), liefen bisher ohne sie und verfaelschten parallel
# laufende Ketten (ACTiKamera-Lauf im G4-Bau 02.10., wiederholt). Dieses Skript nimmt
# dieselbe Sperre auf dieselbe Weise wie kette_linie.sh und x8_lauf.sh: mkdir ist
# atomar, die Sperre traegt die PID, eine verwaiste (Halter lebt nicht mehr) wird
# uebernommen; freigegeben wird beim Ende, auch bei Abbruch (trap EXIT).
#
# Aufruf:  bash Werkzeuge/unter_kettensperre.sh <befehl> [<argumente> ...]
# Beispiel: bash Werkzeuge/unter_kettensperre.sh python Werkzeuge/rendern.py "$ORDNER"
# Rueckgabe: die des Befehls; 2 bei falschem Aufruf.
# KETTE_SPERRE=<pfad> nur fuer die Eichung (eigene Sperre im Kratzordner); der Name muss
# auf .kette_sperre enden.
set -u
[ $# -ge 1 ] || { echo "Aufruf: unter_kettensperre.sh <befehl> [<argumente> ...]" >&2; exit 2; }
# Arbeitsordner: der Elternordner von Werkzeuge/, uebersteuerbar mit LOXWERK.
B="${LOXWERK:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
S="${KETTE_SPERRE:-$B/Pruefung-Durchgang-2026-09-29/.kette_sperre}"
case "$S" in */.kette_sperre) ;; *) echo "Sperrpfad muss auf .kette_sperre enden: $S" >&2; exit 2 ;; esac
[ -d "$(dirname "$S")" ] || { echo "Ordner der Sperre fehlt: $(dirname "$S")" >&2; exit 2; }
WARTET=""
while ! mkdir "$S" 2>/dev/null; do
    h=$(cat "$S/pid" 2>/dev/null)
    if [ -n "$h" ] && ! kill -0 "$h" 2>/dev/null; then
        echo "Sperre von PID $h verwaist - uebernommen" >&2; rm -f "$S/pid"; rmdir "$S" 2>/dev/null; continue
    fi
    [ -z "$WARTET" ] && { echo "Warte auf laufende Kette (PID ${h:-?}) ..." >&2; WARTET=1; }
    sleep "${KETTE_TAKT:-10}"
done
echo $$ > "$S/pid"
trap 'rm -f "$S/pid"; rmdir "$S" 2>/dev/null' EXIT
"$@"
