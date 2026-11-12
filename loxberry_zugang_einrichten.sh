#!/bin/bash
# Richtet auf dem LoxBerry den Benutzer "claude" ein: eigener Benutzer, knappe Rechte,
# Anmeldung nur mit Schluessel. Einmal als root laufen lassen. Auf dem LoxBerry im Haus geht das NUR
# ueber `su -` (Root-Kennwort): der Benutzer loxberry hat dort kein sudo mit Kennwort (gemessen 05.09.2026).
#
# Aufruf vom Windows-Rechner (PowerShell), nachdem der Schluessel erzeugt ist (siehe
# Werkzeuge/LIESMICH_LoxBerry-Zugang.md):
#
#   Im LoxBerry-Terminal (Admin -> Terminal, Benutzer loxberry):
#     su -                       (Root-Kennwort tippt der Hausherr selbst)
#     bash /tmp/zugang.sh 'ssh-ed25519 AAAA... claude-code'
#     rm -f /tmp/zugang.sh; exit
#   Die Datei /tmp/zugang.sh kommt dorthin ueber den Dateimanager (Upload nach /tmp) oder per
#   Einfuegen im Terminal:  cat > /tmp/zugang.sh   (Inhalt einfuegen, Strg-D).
#
# Was das Skript tut - und nur das:
#   1. Benutzer claude anlegen (kein Kennwort, Shell bash, Heimat /home/claude). KEINE Gruppe
#      loxberry: gemessen am 05.09.2026 ist config/system/general.json mit 644 ohnehin fuer jeden
#      lesbar (Miniserver- und Broker-Zugangsdaten im Klartext) - mehr Gruppenrechte braucht es nicht,
#      Plugin-Code (755/664) und Plugin-Logs (664) sind fuer "andere" lesbar; Konfigurationen mit
#      0600/0700 bleiben verborgen, und das ist richtig so.
#   2. Den uebergebenen oeffentlichen Schluessel als einzige Anmeldung eintragen.
#   3. sudo NUR fuer drei Dinge, ohne Kennwort:
#        systemctl status ...            (laeuft ein Dienst?)
#        journalctl ...                  (was sagt das Protokoll?)
#        sudo -u loxberry php|perl /opt/loxberry/bin/plugins/...   (einen Cron-Dienst einmal von Hand
#                                        starten und den Rueckgabewert ansehen - Regeln/01, Abschnitt 4)
#      Kein anderes sudo. Kein Schreiben ausserhalb von /home/claude.
#   4. Nachmessen und ausgeben: id, sudo -l, Schluesseldatei, sshd-Einstellung fuer Schluessel.
#
# Idempotent: ein zweiter Lauf aendert nichts, ausser dass ein neuer Schluessel ergaenzt wird.
# Rueckbau steht am Ende dieser Datei.
#
# Anlass: Regeln/01 verlangt Messungen am installierten Zustand; bisher stand nirgends, wie Claude
# aufs Geraet kommt. Entscheidung des Hausherrn 05.09.2026.

set -u
KEY="${1:-}"
if [ "$(id -u)" -ne 0 ]; then echo "FEHL: als root laufen lassen (su -)"; exit 2; fi
if [ -z "$KEY" ] || ! echo "$KEY" | grep -qE '^(ssh-ed25519|ssh-rsa|ecdsa-sha2-nistp256) [A-Za-z0-9+/=]+'; then
  echo "FEHL: erstes Argument muss der oeffentliche Schluessel sein (Inhalt von loxberry_claude.pub)"; exit 2
fi

echo "== 1. Benutzer"
if id claude >/dev/null 2>&1; then
  echo "   claude gibt es schon"
else
  useradd --create-home --shell /bin/bash --comment "Claude Code, Schluessel-Zugang" claude && echo "   claude angelegt"
fi
passwd -l claude >/dev/null 2>&1 && echo "   Kennwort-Anmeldung gesperrt (nur Schluessel)"

echo "== 2. Schluessel"
install -d -m 700 -o claude -g claude /home/claude/.ssh
touch /home/claude/.ssh/authorized_keys
if grep -qF "$KEY" /home/claude/.ssh/authorized_keys; then
  echo "   Schluessel war schon eingetragen"
else
  echo "$KEY" >> /home/claude/.ssh/authorized_keys && echo "   Schluessel eingetragen"
fi
chown claude:claude /home/claude/.ssh/authorized_keys; chmod 600 /home/claude/.ssh/authorized_keys

echo "== 3. sudo, eng"
cat > /etc/sudoers.d/claude <<'EOF'
# Claude Code auf dem LoxBerry: nur lesen, Dienste ansehen, einen Plugin-Dienst von Hand starten.
# Angelegt von Werkzeuge/loxberry_zugang_einrichten.sh.
Defaults:claude !requiretty
claude ALL=(root) NOPASSWD: /usr/bin/systemctl status *, /bin/systemctl status *
claude ALL=(root) NOPASSWD: /usr/bin/journalctl *, /bin/journalctl *
claude ALL=(loxberry) NOPASSWD: /usr/bin/php /opt/loxberry/bin/plugins/*, /usr/bin/perl /opt/loxberry/bin/plugins/*
EOF
chmod 440 /etc/sudoers.d/claude
if visudo -cf /etc/sudoers.d/claude >/dev/null; then echo "   /etc/sudoers.d/claude gueltig"; else echo "FEHL: sudoers ungueltig - entfernt"; rm -f /etc/sudoers.d/claude; exit 2; fi

echo "== 4. sshd"
if sshd -T 2>/dev/null | grep -qi '^pubkeyauthentication yes'; then
  echo "   PubkeyAuthentication yes"
else
  echo "   ACHTUNG: sshd meldet keine Schluessel-Anmeldung - /etc/ssh/sshd_config pruefen (PubkeyAuthentication yes)"
fi

echo "== Nachmessung"
id claude
sudo -l -U claude | sed 's/^/   /'
ls -la /home/claude/.ssh/authorized_keys
echo "   Schluessel in Datei: $(wc -l < /home/claude/.ssh/authorized_keys)"
echo
echo "Fertig. Vom Windows-Rechner pruefen:  ssh loxberry-claude 'id; cat /etc/os-release | head -2'"
echo
echo "Rueckbau (als root):  userdel -r claude; rm -f /etc/sudoers.d/claude"
