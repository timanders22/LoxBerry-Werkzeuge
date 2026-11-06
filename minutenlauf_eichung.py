#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Eichung von minutenlauf_pruefen.py in beide Richtungen. Laeuft auf: Windows, Python 3, WSL.

    python Werkzeuge/minutenlauf_eichung.py <arbeitsordner, neu>

Rot muss sein:  LoxBerry-Plugin-MGiSmart-1.1.31_Probe_zum_Hochladen_alt4.zip (d6a22bab), am Geraet in jedem Minutenlauf abgestuerzt: Quelltext, WSL und 7.4 je ein BEFUND.
Gruen muss sein: die aktuelle LoxBerry-Plugin-MGiSmart-1.1.31_Probe_zum_Hochladen.zip (die Summe wird genannt, sie aendert sich mit jedem Neubau; gemessen auch gegen 880bfe05).
Die Summe der roten Probe steht fest: sie ist die Eichgrundlage. Rueckgabe 1, wenn eine Richtung nicht stimmt. Packt in den Arbeitsordner aus, loescht nichts."""
import hashlib
import os
import re
import subprocess
import sys
import zipfile

HIER = os.path.dirname(os.path.abspath(__file__))
B = os.path.dirname(HIER)
ROT = ("LoxBerry-Plugin-MGiSmart-1.1.31_Probe_zum_Hochladen_alt4.zip", "d6a22bab")
GRUEN = ("LoxBerry-Plugin-MGiSmart-1.1.31_Probe_zum_Hochladen.zip", None)


def auspacken(name, summe, ziel):
    p = os.path.join(B, name)
    if not os.path.isfile(p):
        sys.exit("ABBRUCH: %s fehlt" % name)
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()[:8]
    print("%s: SHA256 %s" % (name, h))
    if summe is not None and h != summe:
        sys.exit("ABBRUCH: %s hat %s statt %s" % (name, h, summe))
    with zipfile.ZipFile(p) as z:
        z.extractall(ziel)
    return ziel


def lauf(ordner):
    env = dict(os.environ); env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([sys.executable, "-B", os.path.join(HIER, "minutenlauf_pruefen.py"), ordner], capture_output=True, env=env)
    return r.returncode, r.stdout.decode("utf-8", "replace")


def kinder():
    """Dritter Fall (seit 03.11.2026): SignalBot weckt im Minutenlauf einen Dienst mit Endlosschleife. Der Lauf muss ihn nennen und darf ihn nicht hinterlassen.
    Rueckgabe None, wenn die Linie nicht daliegt: dann ist der Fall nicht gemessen, das steht in der Ausgabe."""
    da = [n for n in os.listdir(B) if re.match(r"LoxBerry-Plugin-SignalBot-[0-9.]+$", n) and os.path.isdir(os.path.join(B, n))]
    if not da:
        print("kinder: NICHT gemessen, kein Ordner LoxBerry-Plugin-SignalBot-* da")
        return None
    linie = os.path.join(B, max(da, key=lambda n: [int(x) for x in n.rsplit("-", 1)[1].split(".")]))
    env = dict(os.environ); env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([sys.executable, "-B", os.path.join(HIER, "minutenlauf_pruefen.py"), linie, "--nur", "74"], capture_output=True, env=env)
    aus = r.stdout.decode("utf-8", "replace")
    ps = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", "@(Get-CimInstance Win32_Process -Filter \"Name='php.exe'\" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains('C:/tmp/ml74/fest_signalbot/') }).Count"], capture_output=True)
    rest = ps.stdout.decode("ascii", "replace").strip()
    ok = "Prozess(e) des Laufs" in aus and rest == "0"
    print("kinder %s: %s, danach php %s" % (os.path.basename(linie), "genannt und beendet" if ok else "NICHT wie erwartet:\n" + aus[:500], rest))
    return ok


def main():
    if len(sys.argv) != 2 or os.path.exists(sys.argv[1]):
        sys.exit("Aufruf: minutenlauf_eichung.py <arbeitsordner, neu>")
    w = sys.argv[1]
    os.makedirs(w)
    gut = True
    rc, aus = lauf(auspacken(ROT[0], ROT[1], os.path.join(w, "rot")))
    soll = ["BEFUND globales $cfg", "BEFUND Minutenlauf gegen das echte SDK rot (WSL)", "BEFUND Minutenlauf unter PHP 7.4 rot", "Cannot use object of type stdClass"]
    fehlt = [s for s in soll if s not in aus]
    print("rot  %s: rc %d, %s" % (ROT[1], rc, "alle drei Teile rot" if not fehlt and rc == 1 else "FEHLT: %s" % fehlt))
    gut = gut and not fehlt and rc == 1
    rc, aus = lauf(auspacken(GRUEN[0], GRUEN[1], os.path.join(w, "gruen")))
    ok = rc == 0 and "BEFUND" not in aus and "[WSL] ERGEBNIS GRUEN" in aus and "[7.4] ERGEBNIS GRUEN" in aus
    print("gruen: rc %d, %s" % (rc, "alle Teile gruen" if ok else "NICHT GRUEN:\n" + aus[:800]))
    gut = gut and ok
    gut = gut and kinder() is not False
    print("Eichung " + ("bestanden" if gut else "NICHT bestanden"))
    return 0 if gut else 1


if __name__ == "__main__":
    sys.exit(main())
