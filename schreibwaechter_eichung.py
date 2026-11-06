# -*- coding: utf-8 -*-
"""Eichung des Schreibwaechters in beide Richtungen.

Aufruf: python schreibwaechter_eichung.py
Baut einen Wegwerf-Arbeitsordner unter dem Temp-Verzeichnis, legt dort Dateien an und
ruft schreibwaechter.py mit CLAUDE_PROJECT_DIR darauf. Schreibt NICHTS in den echten
Arbeitsordner. Rueckgabewert 0 = alle Faelle wie erwartet, 1 = mindestens einer nicht.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

HIER = os.path.dirname(os.path.abspath(__file__))
WAECHTER = os.path.join(HIER, "schreibwaechter.py")


def lauf(projekt, aufruf):
    umg = dict(os.environ)
    umg["CLAUDE_PROJECT_DIR"] = projekt
    p = subprocess.run([sys.executable, WAECHTER], input=json.dumps(aufruf).encode("utf-8"),
                       capture_output=True, env=umg, cwd=projekt)
    return p.returncode, p.stderr.decode("utf-8", "replace").strip()


def main():
    wurzel = tempfile.mkdtemp(prefix="waechter_eichung_")
    os.makedirs(os.path.join(wurzel, "Archiv", "Regeln-Rohfassung"))
    os.makedirs(os.path.join(wurzel, "Stand-Protokolle"))
    os.makedirs(os.path.join(wurzel, "Regeln"))
    gross = "x" * 10000
    open(os.path.join(wurzel, "Regeln", "01_test.md"), "w").write(gross)
    open(os.path.join(wurzel, "Archiv", "Regeln-Rohfassung", "REGELN_1_Arbeitsweise.md"), "w").write(gross)
    open(os.path.join(wurzel, "alt.Loxone"), "w").write(gross)
    os.utime(os.path.join(wurzel, "alt.Loxone"), (time.time() - 7200, time.time() - 7200))
    open(os.path.join(wurzel, "frisch.Loxone"), "w").write(gross)
    open(os.path.join(wurzel, "Plugin.zip"), "w").write("zip")
    open(os.path.join(wurzel, "Stand-Protokolle", "alt.md"), "w").write(gross)

    faelle = [
        # (Name, Aufruf, erwarteter Rueckgabewert)
        ("Write: neue Datei anlegen", {"tool_name": "Write", "tool_input": {"file_path": "Regeln/neu.md", "content": "hallo"}}, 0),
        ("Write: Datei gleich gross ueberschreiben", {"tool_name": "Write", "tool_input": {"file_path": "Regeln/01_test.md", "content": gross}}, 0),
        ("Write: Datei um 10 % kuerzen (unter Schwelle)", {"tool_name": "Write", "tool_input": {"file_path": "Regeln/01_test.md", "content": "x" * 9000}}, 0),
        ("Write: Datei um 40 % kuerzen", {"tool_name": "Write", "tool_input": {"file_path": "Regeln/01_test.md", "content": "x" * 6000}}, 2),
        ("Edit: kleine Aenderung", {"tool_name": "Edit", "tool_input": {"file_path": "Regeln/01_test.md", "old_string": "xxxx", "new_string": "yy"}}, 0),
        ("Edit: grossen Block entfernen", {"tool_name": "Edit", "tool_input": {"file_path": "Regeln/01_test.md", "old_string": "x" * 5000, "new_string": ""}}, 2),
        ("Write unter Archiv/", {"tool_name": "Write", "tool_input": {"file_path": "Archiv/Regeln-Rohfassung/REGELN_1_Arbeitsweise.md", "content": gross}}, 2),
        ("Write NEUE Datei in Stand-Protokolle/", {"tool_name": "Write", "tool_input": {"file_path": "Stand-Protokolle/neu.md", "content": "a"}}, 0),
        ("Write BESTEHENDE Datei in Stand-Protokolle/", {"tool_name": "Write", "tool_input": {"file_path": "Stand-Protokolle/alt.md", "content": gross}}, 2),
        ("Bash: rm in Stand-Protokolle/", {"tool_name": "Bash", "tool_input": {"command": "rm Stand-Protokolle/alt.md"}}, 2),
        ("Write alte .Loxone", {"tool_name": "Write", "tool_input": {"file_path": "alt.Loxone", "content": gross}}, 2),
        ("Write frische .Loxone", {"tool_name": "Write", "tool_input": {"file_path": "frisch.Loxone", "content": gross}}, 0),
        ("Bash: lesen aus Archiv", {"tool_name": "Bash", "tool_input": {"command": "grep -n Titel Archiv/Regeln-Rohfassung/REGELN_1_Arbeitsweise.md | head"}}, 0),
        ("Bash: Umleitung in REGELN", {"tool_name": "Bash", "tool_input": {"command": "echo neu >> Archiv/Regeln-Rohfassung/REGELN_1_Arbeitsweise.md"}}, 2),
        ("Bash: rm im Archiv", {"tool_name": "Bash", "tool_input": {"command": "rm Archiv/Regeln-Rohfassung/REGELN_1_Arbeitsweise.md"}}, 2),
        ("Bash: mv eines Zip", {"tool_name": "Bash", "tool_input": {"command": "mv Plugin.zip /tmp/"}}, 2),
        ("Bash: sed -i auf Regeln/ (erlaubt)", {"tool_name": "Bash", "tool_input": {"command": "sed -i 's/a/b/' Regeln/01_test.md"}}, 0),
        ("Bash: python-Aufruf ohne Umleitung", {"tool_name": "Bash", "tool_input": {"command": "python Werkzeuge/fassungslage.py LoxBerry-Plugin-Govee-0.9.12"}}, 0),
        ("Unlesbarer Aufruf", None, 2),
    ]
    fehler = 0
    for name, aufruf, erwartet in faelle:
        if aufruf is None:
            umg = dict(os.environ); umg["CLAUDE_PROJECT_DIR"] = wurzel
            p = subprocess.run([sys.executable, WAECHTER], input=b"{kaputt", capture_output=True, env=umg, cwd=wurzel)
            rc, err = p.returncode, p.stderr.decode("utf-8", "replace").strip()
        else:
            rc, err = lauf(wurzel, aufruf)
        ok = rc == erwartet
        fehler += 0 if ok else 1
        print("[%s] %-42s erwartet %d, bekommen %d%s" % ("OK " if ok else "FEHL", name, erwartet, rc,
                                                        ("  -> " + err.splitlines()[0][:110]) if err and not ok else ""))
    # Mit Marke: Kuerzen erlaubt
    open(os.path.join(wurzel, ".kuerzen-erlaubt"), "w").close()
    rc, err = lauf(wurzel, {"tool_name": "Write", "tool_input": {"file_path": "Regeln/01_test.md", "content": "x" * 6000}})
    ok = rc == 0
    fehler += 0 if ok else 1
    print("[%s] %-42s erwartet 0, bekommen %d" % ("OK " if ok else "FEHL", "Write: 40 % kuerzen MIT Marke", rc))
    # Marke schuetzt Archiv NICHT
    rc, err = lauf(wurzel, {"tool_name": "Write", "tool_input": {"file_path": "Archiv/Regeln-Rohfassung/REGELN_1_Arbeitsweise.md", "content": gross}})
    ok = rc == 2
    fehler += 0 if ok else 1
    print("[%s] %-42s erwartet 2, bekommen %d" % ("OK " if ok else "FEHL", "Write unter Archiv/ trotz Marke", rc))
    print("\n%d Faelle, %d abweichend. Wegwerfordner: %s" % (len(faelle) + 2, fehler, wurzel))
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
