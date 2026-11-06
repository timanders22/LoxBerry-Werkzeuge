#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kettenschritt "Minutenlauf gegen die echte SDK-Datei" (seit 01.11.2026, Anlass: Ausfall MGiSmart 1.1.31, globales $cfg).

Laeuft auf: Windows, Python 3, Git Bash und WSL. Nur lesend gegen die Linie; Arbeitsstand im Namensraum (WSL, tmpfs) bzw. unter C:/tmp/ml74.

    python Werkzeuge/minutenlauf_pruefen.py <Linienordner> [--nur wsl|74] [--cron cron.01min,...]

Drei Pruefungen, jede meldet "BEFUND ..." und das Werkzeug gibt dann rc 1:
  1. Quelltext: T_VARIABLE $cfg im globalen Bereich einer PHP-Datei. Das echte SDK ueberschreibt es beim ersten Lesen von general.json.
     Faengt auch die Wege, die ein Lauf nicht betritt (Monatsbericht, Formular, Endpunkt mit Token).
  2. WSL (minutenlauf_pruefstand.sh): echte Cron-Datei, Interpreter ihrer Shebang, installierte Lage /opt/loxberry, echte libs/phplib,
     PHP 8.3, kein Netz, Attrappen fuer Broker und Fahrzeug. Soll: rc 0, cron.err leer, keine Absturzzeile.
  3. PHP 7.4 (minutenlauf_pruefstand74.sh): dieselbe Cron-Datei, dash (MSYS), php.exe 7.4.33. Soll: keine Absturzzeile, rc nicht 255/124/137.
Fehlt WSL oder 7.4, ist das ein BEFUND, kein stilles Auslassen. Hat eine Cron-Datei keinen php-Lauf: "HINWEIS nicht gemessen".

Angaben je Linie in Werkzeuge/minutenlauf_linien.json (Schluessel = FOLDER aus plugin.cfg): Konfiguration und Antwort der mosquitto_sub-Attrappe.
Ohne Eintrag laeuft die Linie im Werkszustand, dann sagt der Lauf oft nur, dass der Einstieg heil bis "nicht eingerichtet" kommt; das steht in der Ausgabe.

Geeicht: rot gegen MGiSmart 1.1.31 Probe d6a22bab (_alt4), gruen gegen 880bfe05, beide Teile (minutenlauf_eichung.py). Nichts wird geloescht.
Arbeitsordner des 7.4-Teils: je Linie fest C:/tmp/ml74/fest_<ordner>, wiederverwendet (seit 01.11.2026, siehe minutenlauf_pruefstand74.sh).
Der 7.4-Teil laeuft in einem Windows-Job (seit 03.11.2026, lauf_mit_kindern()): hinterlaesst ein Lauf Prozesse, nennt die Ausgabe sie und sie enden mit ihm.
"""
import ctypes
import ctypes.wintypes
import json
import os
import re
import subprocess
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
BASH = r"C:\Program Files\Git\bin\bash.exe"
PHP74 = "/c/tmp/php-7.4.33-Win32-vc15-x64/php.exe"
PHP84 = r"C:\tmp\php-8.4.27-Win32-vs17-x64\php.exe"
RANG = ["01min", "03min", "05min", "10min", "15min", "30min", "hourly", "daily"]


def wsl_pfad(p):
    p = os.path.realpath(p).replace("\\", "/")
    return "/mnt/" + p[0].lower() + p[2:]


def msys_pfad(p):
    p = os.path.realpath(p).replace("\\", "/")
    return "/" + p[0].lower() + p[2:]


def cron_dateien(linie, angabe):
    if angabe.get("cron"):
        return list(angabe["cron"])
    d = os.path.join(linie, "cron")
    da = sorted(f for f in os.listdir(d) if f.startswith("cron.")) if os.path.isdir(d) else []
    for r in RANG:
        if "cron." + r in da:
            return ["cron." + r]
    return da[:1]


def quelltext(linie):
    r = subprocess.run([PHP84, "-n", os.path.join(HIER, "minutenlauf_cfg_scan.php"), linie], capture_output=True)
    aus = r.stdout.decode("utf-8", "replace").strip()
    if r.returncode != 0:
        return ["Quelltextsuche scheiterte: " + (aus + r.stderr.decode("utf-8", "replace"))[:200]]
    return [z for z in aus.split("\n") if z]


def lauf(befehl, umg=None, frist=300):
    try:
        r = subprocess.run(befehl, capture_output=True, timeout=frist, env=umg, stdin=subprocess.DEVNULL)
        return r.returncode, r.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "ERGEBNIS ROT Zeitgrenze des Werkzeugs (%d s)\n" % frist


def lauf_mit_kindern(befehl, frist=300):
    """Wie lauf(), aber in einem Windows-Job: was der Lauf hinterlaesst, endet mit ihm. Eine Cron-Datei, die einen Dienst weckt (Signalbot sg_bot.php: Endlosschleife, im
    Hintergrund gestartet), kehrt sofort zurueck, und unter MSYS erreicht kein Signal das php.exe dahinter: am 01.11.2026 liefen drei solche Prozesse zwei Tage weiter."""
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    nt = ctypes.WinDLL("ntdll")
    H = ctypes.wintypes.HANDLE
    k.CreateJobObjectW.restype = H
    k.CreateJobObjectW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
    k.SetInformationJobObject.argtypes = [H, ctypes.c_int, ctypes.c_void_p, ctypes.wintypes.DWORD]
    k.AssignProcessToJobObject.argtypes = [H, H]
    k.QueryInformationJobObject.argtypes = [H, ctypes.c_int, ctypes.c_void_p, ctypes.wintypes.DWORD, ctypes.c_void_p]
    k.TerminateJobObject.argtypes = [H, ctypes.c_uint]
    k.CloseHandle.argtypes = [H]
    nt.NtResumeProcess.argtypes = [H]
    job = k.CreateJobObjectW(None, None)
    if not job:
        return 125, "Job nicht anlegbar: %d\n" % ctypes.get_last_error()
    # JOBOBJECT_EXTENDED_LIMIT_INFORMATION (144 Byte unter x64), LimitFlags bei Versatz 16; 0x2000 = alle enden, wenn der Griff zugeht, auch wenn dieses Werkzeug abstuerzt
    grenzen = (ctypes.c_uint32 * 36)()
    grenzen[4] = 0x2000
    if not k.SetInformationJobObject(job, 9, grenzen, ctypes.sizeof(grenzen)):
        k.CloseHandle(job)
        return 125, "Job nicht einstellbar: %d\n" % ctypes.get_last_error()
    p = subprocess.Popen(befehl, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, creationflags=0x4)  # CREATE_SUSPENDED: nichts startet vor der Zuordnung
    try:
        if not k.AssignProcessToJobObject(job, int(p._handle)):
            p.kill()
            return 125, "Job nicht zuordenbar: %d\n" % ctypes.get_last_error()
        nt.NtResumeProcess(int(p._handle))
        try:
            aus = p.communicate(timeout=frist)[0]
            rc = p.returncode
            zusatz = ""
        except subprocess.TimeoutExpired:
            k.TerminateJobObject(job, 124)
            aus = p.communicate()[0]
            rc = 124
            zusatz = "ERGEBNIS ROT Zeitgrenze des Werkzeugs (%d s)\n" % frist
        # JOBOBJECT_BASIC_PROCESS_ID_LIST: Zugewiesen, Gelistet, Kennungen
        liste = (ctypes.c_uint32 * 130)()
        if k.QueryInformationJobObject(job, 3, liste, ctypes.sizeof(liste), None) and liste[0]:
            zusatz += "HINWEIS %d Prozess(e) des Laufs waren noch da und wurden beendet\n" % liste[0]
        return rc, aus.decode("utf-8", "replace") + zusatz
    finally:
        k.TerminateJobObject(job, 1)
        k.CloseHandle(job)


def main():
    args = sys.argv[1:]
    nur = ""
    cron = None
    if "--nur" in args:
        i = args.index("--nur"); nur = args[i + 1]; del args[i:i + 2]
    if "--cron" in args:
        i = args.index("--cron"); cron = args[i + 1].split(","); del args[i:i + 2]
    if len(args) != 1 or not os.path.isfile(os.path.join(args[0], "plugin.cfg")):
        sys.exit("Aufruf: minutenlauf_pruefen.py <Linienordner> [--nur wsl|74] [--cron a,b]")
    linie = os.path.abspath(args[0])
    pc = open(os.path.join(linie, "plugin.cfg"), "rb").read().decode("utf-8", "replace")
    m = re.search(r"^FOLDER=(\S+)", pc, re.M)
    ordner = m.group(1).strip('"') if m else ""
    if not ordner:
        print("  BEFUND plugin.cfg ohne FOLDER")
        return 1
    tab = json.load(open(os.path.join(HIER, "minutenlauf_linien.json"), encoding="utf-8"))
    tab = {k: v for k, v in tab.items() if not k.startswith("_")}
    angabe = dict(tab.get(ordner, {}))
    if cron:
        angabe["cron"] = cron
    angabe["ordner"] = ordner
    dateien = cron_dateien(linie, angabe)
    befund = 0
    print("  Linie %s, Angaben: %s, Cron: %s" % (ordner, "ja" if ordner in tab else "keine (Werkszustand)", ", ".join(dateien) or "keine"))
    treffer = quelltext(linie)
    for z in treffer:
        print("  BEFUND globales $cfg: " + z)
    befund += len(treffer)
    if not dateien:
        print("  HINWEIS nicht gemessen: die Linie hat keine Cron-Datei")
        return 1 if befund else 0
    sdk = os.path.join(HIER, "minutenlauf_sdk")
    t0 = time.time()
    ang = os.path.join(os.environ.get("TEMP", r"C:\tmp"), "minutenlauf_angaben_%s.json" % re.sub(r"[^A-Za-z0-9_]", "_", ordner))
    json.dump(angabe, open(ang, "w", encoding="utf-8"), ensure_ascii=False)
    # 2. WSL
    if nur != "74":
        umg = dict(os.environ); umg["MSYS_NO_PATHCONV"] = "1"
        rc, aus = lauf(["wsl", "-e", "bash", wsl_pfad(os.path.join(HIER, "minutenlauf_pruefstand.sh")), wsl_pfad(linie), wsl_pfad(sdk), wsl_pfad(ang)] + dateien, umg)
        ausgabe("WSL", aus)
        if "ERGEBNIS" not in aus:
            print("  BEFUND WSL-Teil lief nicht (rc %d): %s" % (rc, aus.strip()[:160]))
            befund += 1
        elif "ERGEBNIS ROT" in aus or rc not in (0, 3):
            print("  BEFUND Minutenlauf gegen das echte SDK rot (WSL), siehe oben")
            befund += 1
    # 3. PHP 7.4
    if nur != "wsl":
        php74 = "C:" + PHP74[2:]
        if not os.path.isfile(php74):
            print("  BEFUND PHP 7.4 fehlt (%s): der Minutenlauf ist unter der Fassung des Geraets nicht gemessen" % php74)
            befund += 1
        else:
            arbeit = "/c/tmp/ml74/fest_%s" % re.sub(r"[^A-Za-z0-9_]", "_", ordner)
            rc, aus = lauf_mit_kindern([BASH, msys_pfad(os.path.join(HIER, "minutenlauf_pruefstand74.sh")), msys_pfad(linie), msys_pfad(sdk), msys_pfad(ang), arbeit, PHP74] + dateien)
            ausgabe("7.4", aus)
            if "ERGEBNIS" not in aus:
                print("  BEFUND 7.4-Teil lief nicht (rc %d): %s" % (rc, aus.strip()[:160]))
                befund += 1
            elif "ERGEBNIS ROT" in aus:
                print("  BEFUND Minutenlauf unter PHP 7.4 rot, siehe oben")
                befund += 1
    print("  Dauer %.1f s" % (time.time() - t0))
    return 1 if befund else 0


def ausgabe(teil, aus):
    for z in aus.strip().split("\n"):
        if z.startswith(("LAUF", "Interpreter")) and "rc=0" in z:
            continue
        print("  [%s] %s" % (teil, z[:210]))


if __name__ == "__main__":
    sys.exit(main())
