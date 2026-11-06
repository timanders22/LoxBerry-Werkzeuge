#!/usr/bin/env python3
"""Eicht die Netzsperre von rendern.py (seit 11.09.2026).

Baut im Temp-Verzeichnis eine Probeseite, die auf vier Wegen nach aussen
fragt: file_get_contents mit https, mit http und eigenem Kontext, einmal
ohne "@" (waere eine Warnung), und curl. Dann rendern.lauf() MIT Sperre je
PHP-Fassung. Erwartet: alle vier scheitern, der Proxy sah den curl-Aufruf,
der Wrapper die drei Stroeme, und es entsteht KEIN Befund.

Die Gegenrichtung (ohne Sperre geht die Seite wirklich hinaus) laeuft nur
mit --gegenprobe: sie fragt example.com/.org/.net (RFC 2606) - ein
Pruefwerkzeug geht nicht ungefragt nach aussen. Gemessen am 11.09.2026 mit
Gegenprobe: ohne Sperre 559 Byte von example.com und 2 Befunde.

Aufruf:  rendern_netzsperre_eichung.py [--gegenprobe]
Rueckgabewert: 0 wie erwartet, 1 sonst.
"""
import shutil
import sys
import tempfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
sys.dont_write_bytecode = True
import rendern  # noqa: E402

SEITE = r"""<?php
$e = array();
$r = @file_get_contents('https://example.com/');
$e[] = 'fgc_https=' . ($r === false ? 'false' : strlen($r));
$ctx = stream_context_create(array('http' => array('timeout' => 5)));
$r = @file_get_contents('http://example.com/', false, $ctx);
$e[] = 'fgc_http_kontext=' . ($r === false ? 'false' : strlen($r));
$r = file_get_contents('https://example.org/ohne-at');
$e[] = 'fgc_ohne_at=' . ($r === false ? 'false' : strlen($r));
if (function_exists('curl_init')) {
    $c = curl_init('https://example.net/');
    curl_setopt($c, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($c, CURLOPT_TIMEOUT, 8);
    $r = curl_exec($c);
    $e[] = 'curl_https=' . ($r === false ? 'false' : strlen($r));
} else {
    $e[] = 'curl_https=fehlt';
}
echo '<html><body><pre>PROBE ' . implode(' | ', $e) . '</pre>'
   . str_repeat('<!-- Fuellung -->', 40) . '</body></html>';
"""

OK = FAIL = 0


def pruefe(name, ist, soll):
    global OK, FAIL
    gut = ist == soll
    OK += gut
    FAIL += not gut
    print("   [%s] %-48s ist=%r soll=%r" % ("ok " if gut else "FEHL", name, ist, soll))


def main():
    gegen = "--gegenprobe" in sys.argv
    tmp = Path(tempfile.mkdtemp(prefix="netzsperre_"))
    datei = tmp / "Netzprobe" / "webfrontend" / "htmlauth" / "index.php"
    datei.parent.mkdir(parents=True)
    datei.write_text(SEITE, encoding="utf-8")
    try:
        for v, php in rendern.PHPS:
            if not Path(php).is_file():
                print("== PHP %s fehlt - uebersprungen" % v)
                continue
            sperre = rendern.Netzsperre()
            out, bef, rest = rendern.lauf(php, datei, "netzprobe", sperre)
            sperre.ende()
            probe = next((z for z in out.splitlines() if "PROBE" in z), "")
            print("== PHP %s mit Sperre: %s" % (v, probe[probe.find("PROBE"):probe.find("</pre>")]))
            for teil in ("fgc_https=false", "fgc_http_kontext=false", "fgc_ohne_at=false"):
                pruefe(teil.split("=")[0] + " gescheitert", teil in probe, True)
            if "curl_https=fehlt" not in probe:
                pruefe("curl gescheitert", "curl_https=false" in probe, True)
                pruefe("Proxy sah den curl-Aufruf", sperre.ziele, ["example.net:443"])
            pruefe("Wrapper sah drei Stroeme", len(sperre.stroeme), 3)
            pruefe("kein Befund aus der Sperre", bef, [])
            if gegen:
                out2, bef2, _ = rendern.lauf(php, datei, "netzprobe", None)
                probe2 = next((z for z in out2.splitlines() if "PROBE" in z), "")
                print("== PHP %s OHNE Sperre (Gegenprobe): %s"
                      % (v, probe2[probe2.find("PROBE"):probe2.find("</pre>")]))
                pruefe("ohne Sperre geht die Seite hinaus",
                       "fgc_https=false" not in probe2 or bool(bef2), True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        for teil in ("config", "data", "log"):
            shutil.rmtree(rendern.LB / teil / "plugins" / "netzprobe", ignore_errors=True)
    print("%d wie erwartet, %d nicht" % (OK, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
