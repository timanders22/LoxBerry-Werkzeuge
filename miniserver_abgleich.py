# -*- coding: utf-8 -*-
"""Projektdatei gegen die Strukturdatei des laufenden Miniservers halten (LoxAPP3.json).

Aufruf:
    python miniserver_abgleich.py <DATEI.Loxone> <LoxAPP3.json> [--alle] [--markdown DATEI]
    python miniserver_abgleich.py <DATEI.Loxone> --holen http://<miniserver>  [--speichern LoxAPP3.json]

Rein lesend an der Projektdatei. Schreibt nur die mit --markdown / --speichern genannten Dateien.

Rueckgabewert: 0 = Strukturdatei und Projektdatei passen zusammen (kein Befund),
1 = Befunde, 2 = Fehler (Datei fehlt, JSON/XML nicht lesbar, Abruf gescheitert),
3 = die Strukturdatei gehoert erkennbar zu einem ANDEREN Stand (Projektname, Datum oder
    weniger als 90 % der Bausteine wiedergefunden) - dann sind die Einzelbefunde bedeutungslos.

Warum es dieses Werkzeug gibt (Regeln/08, "Die Projektdatei als Auskunftsquelle - und ihre
Grenze"; Regeln/07, Abschnitt 8): Die Datei sagt, was verdrahtet ist. Der Miniserver sagt,
was er wirklich geladen hat und was der Anwender sieht. Bisher wurde das von Hand am
Geraet nachgesehen; dieses Werkzeug macht daraus eine Messung, die in die Pruefkette passt.

Was verglichen wird:
  1. Kopf: msInfo.projectName gegen Document Title, lastModified gegen Document Date -
     passt das nicht, ist die Strukturdatei ein anderer Stand (Rueckgabewert 3).
  2. Jeder Baustein der Strukturdatei (controls, Schluessel = uuidAction) wird ueber seine
     UUID in der Projektdatei gesucht (<C U="...">). Nicht gefundene werden aufgefuehrt.
     Unterbausteine (subControls: Ausgaenge eines Lichtsteuerungs-Bausteins ".../AI1",
     Tastenfelder ".../1", Zeitschaltuhr eines Raumreglers) sind KEINE <C U> der Datei,
     sondern Teile ihres Bausteins; sie gelten als gefunden, wenn ihr Baustein in der
     Datei ist (gemessen 05.09.2026: alle 83 Unterbausteine am eigenen Miniserver).
  3. Jeder Baustein der Projektdatei mit <IoData Visu="true"> wird in der Strukturdatei
     gesucht. Nicht gefundene werden aufgefuehrt - getrennt nach VirtualIn (die dort laut
     Regeln/08 nie erscheinen) und allen anderen (das sind die Befunde).
  4. Raeume (Type="Place") und Kategorien (Type="Category") der Datei gegen rooms/cats.
  5. Namen: wo ein Baustein in beiden vorkommt, aber unter anderem Namen (Title/Desc in der
     Datei gegen name in der Strukturdatei) - das ist die Frage "was sieht der Anwender".
  6. isSecured am Miniserver gegen VisuPwd="true" in der IoData der Datei.

Was NICHT verglichen wird: Zustaende (Werte). Dafuer braucht es die WebSocket-Anmeldung
(Regeln/07, Abschnitt 9) - das ist ein eigenes Werkzeug.

Abruf mit --holen: HTTP-Basic gegen http://<miniserver>/data/LoxAPP3.json. Benutzer und
Kennwort kommen NUR aus den Umgebungsvariablen LOX_BENUTZER und LOX_KENNWORT
(Regeln/05: Zugangsdaten nie auf der Kommandozeile). Ein 401 heisst dort "Recht zur
Visualisierung fehlt" (Regeln/07, Abschnitt 9). Ob der Basic-Weg an einem Gen-2-Miniserver
mit Firmware 17 noch angenommen wird, ist NICHT gemessen - im Zweifel die Datei im
Browser holen (angemeldet http://<miniserver>/data/LoxAPP3.json aufrufen, speichern).

Eichung (02.09.2026):
  - Gegen eine aus der Projektdatei selbst gebaute Strukturdatei (alle Visu-Bausteine als
    controls, Raeume und Kategorien): 0 Befunde, Rueckgabewert 0.
  - Dieselbe mit drei entfernten und einem umbenannten Baustein: genau 3 "nur in der
    Datei" und 1 Namensabweichung, Rueckgabewert 1.
  - Dieselbe mit fremdem projectName: Rueckgabewert 3.
Eichung gegen die echte Strukturdatei (05.09.2026, Geraet/2026-09-05/LoxAPP3.json,
725 386 Byte, msName des eigenen Miniservers, 694 controls + 83 subControls, 27 rooms, 37 cats)
gegen die Hausdatei vom 05.09.2026, 17:14:
  - Die Annahme uuidAction == <C U> STIMMT: 694 von 694 Bausteinen der Strukturdatei
    stehen unter derselben UUID in der Projektdatei (100 %). Vor der Berichtigung wurden
    die 83 Unterbausteine mitgezaehlt und als "nur am Miniserver" gemeldet (Quote 89,4 %,
    Rueckgabewert 3 - ein Fehlalarm des Werkzeugs); seit 05.09.2026 werden sie ihrem
    Baustein zugerechnet.
  - lastModified der Strukturdatei (17:31:47) lag NACH dem Document Date der Projektdatei
    (17:14:14): der Miniserver traegt einen spaeteren Stand. Das Werkzeug meldet das im
    Kopf, wertet es aber nicht als fremden Stand, solange Projektname und Trefferquote
    passen.
  - 60 Bausteine mit Visu="true" in der Datei, aber nicht am Miniserver. GEMESSEN 19:33:
    einer davon (<IoData Visu="true"/> OHNE Pr und Cr) bekam in Config Raum und Kategorie
    "Nicht zugeordnet" und wurde hochgeladen - danach stand genau dieser eine Baustein
    zusaetzlich in der Strukturdatei (694 -> 695 controls, room/cat = "Nicht zugeordnet").
    Folge: ein Baustein ohne Raum UND Kategorie erscheint am Miniserver nicht, egal was
    Visu sagt. Seit 05.09.2026 fuehrt das Werkzeug solche Bausteine getrennt als
    "erwartungsgemaess nicht am Miniserver" (Hinweis, kein Befund); Befund bleibt, was
    Raum und Kategorie hat und trotzdem fehlt (am 05.09.: Devicemonitor, WeatherServer,
    zwei IntercomDevice - Typen, deren Erscheinen in der Strukturdatei ungemessen ist).
"""
import sys, io, json, os, re
import xml.etree.ElementTree as ET

CRLF = "\r\n"


def entdoppeln(zeile):
    st = [m.start() for m in re.finditer(' Title="', zeile)]
    if len(st) < 2:
        return zeile
    for anf in reversed(st[1:]):
        ende = zeile.index('"', anf + 8) + 1
        zeile = zeile[:anf] + zeile[ende:]
    return zeile


def projekt_lesen(pfad):
    s = open(pfad, "rb").read().decode("utf-8-sig")
    ber = CRLF.join([entdoppeln(z) if 'Type="ApiActor"' in z else z for z in s.split(CRLF)])
    wurzel = ET.fromstring(ber)
    dok = [c for c in wurzel if c.tag == "C" and c.get("Type") == "Document"]
    kopf = {"Title": dok[0].get("Title", "") if dok else "", "Date": dok[0].get("Date", "") if dok else ""}
    bausteine, orte, kategorien = {}, {}, {}

    def gehe(el):
        for c in el:
            if c.tag != "C":
                continue
            u, typ = c.get("U", ""), c.get("Type", "")
            io_ = [k for k in c if k.tag == "IoData"]
            visu = any(k.get("Visu") == "true" for k in io_)
            pwd = any(k.get("VisuPwd") == "true" for k in io_)
            pr = io_[0].get("Pr", "") if io_ else ""
            cr = io_[0].get("Cr", "") if io_ else ""
            bausteine[u] = {"Type": typ, "Title": c.get("Title", ""), "Desc": c.get("Desc", ""),
                            "Visu": visu, "VisuPwd": pwd, "Pr": pr, "Cr": cr}
            if typ == "Place":
                orte[u] = c.get("Title", "")
            elif typ == "Category":
                kategorien[u] = c.get("Title", "")
            gehe(c)
    gehe(wurzel)
    return kopf, bausteine, orte, kategorien


def struktur_lesen(pfad):
    with open(pfad, "rb") as f:
        roh = f.read()
    return json.loads(roh.decode("utf-8-sig"))


def holen(basis):
    import base64, urllib.request
    b, k = os.environ.get("LOX_BENUTZER"), os.environ.get("LOX_KENNWORT")
    if not b or not k:
        raise RuntimeError("LOX_BENUTZER und LOX_KENNWORT muessen als Umgebungsvariablen gesetzt sein")
    url = basis.rstrip("/") + "/data/LoxAPP3.json"
    req = urllib.request.Request(url)
    req.add_header("Authorization", "Basic " + base64.b64encode(("%s:%s" % (b, k)).encode()).decode())
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def abgleich(kopf, bausteine, orte, kategorien, st, alle):
    b = {"kopf": [], "stand_fremd": False, "ms_nicht_in_datei": [], "datei_nicht_am_ms": [],
         "virtualin_nicht_am_ms": 0, "ohne_raum": [], "namen": [], "orte": [], "kategorien": [],
         "gesichert": [], "zahlen": {}}
    info = st.get("msInfo", {})
    controls = st.get("controls", {})
    pn, ms = info.get("projectName", ""), info.get("msName", "")
    b["kopf"].append(("Projektname", kopf["Title"], pn))
    b["kopf"].append(("Miniserver", "-", ms))
    b["kopf"].append(("Document Date / lastModified", kopf["Date"], st.get("lastModified", "")))
    if pn and kopf["Title"] and pn != kopf["Title"]:
        b["stand_fremd"] = True

    # 2. Miniserver -> Datei
    alle_ms = {}
    unter_ms = {}
    for u, c in controls.items():
        alle_ms[u] = c
        for su, sc in (c.get("subControls") or {}).items():
            unter_ms[su] = (u, sc)
    treffer = 0
    for u, c in alle_ms.items():
        if u in bausteine:
            treffer += 1
            d = bausteine[u]
            name_datei = d["Desc"] or d["Title"]
            if c.get("name", "") not in (d["Title"], d["Desc"]) and c.get("name", ""):
                b["namen"].append((u, d["Type"], d["Title"], d["Desc"], c.get("name", "")))
            if bool(c.get("isSecured")) != d["VisuPwd"]:
                b["gesichert"].append((u, d["Title"], d["VisuPwd"], bool(c.get("isSecured"))))
        else:
            b["ms_nicht_in_datei"].append((u, c.get("name", ""), c.get("type", "")))
    # Unterbausteine: gefunden, wenn ihr Baustein in der Datei ist (Eichung 05.09.2026)
    unter_ok = 0
    for su, (u, sc) in unter_ms.items():
        if su in bausteine or u in bausteine:
            unter_ok += 1
        else:
            b["ms_nicht_in_datei"].append((su, sc.get("name", ""), sc.get("type", "") + ", Unterbaustein von " + u))
    quote = (100.0 * treffer / len(alle_ms)) if alle_ms else 0.0
    b["zahlen"].update({"ms": len(alle_ms), "treffer": treffer, "quote": quote,
                        "unter": len(unter_ms), "unter_ok": unter_ok})
    if alle_ms and quote < 90.0:
        b["stand_fremd"] = True

    # 3. Datei -> Miniserver
    visu = 0
    for u, d in bausteine.items():
        if not d["Visu"]:
            continue
        visu += 1
        if u in alle_ms or u in unter_ms:
            continue
        if d["Type"] == "VirtualIn" and not alle:
            b["virtualin_nicht_am_ms"] += 1
        elif not d["Pr"] and not d["Cr"]:
            # gemessen 05.09.2026: ohne Raum und Kategorie nimmt der Miniserver den Baustein nicht auf
            b["ohne_raum"].append((u, d["Type"], d["Title"]))
        else:
            b["datei_nicht_am_ms"].append((u, d["Type"], d["Title"], orte.get(d["Pr"], ""), kategorien.get(d["Cr"], "")))
    b["zahlen"]["visu"] = visu

    # 4. Raeume und Kategorien
    rooms, cats = st.get("rooms", {}), st.get("cats", {})
    for u, n in orte.items():
        if u not in rooms:
            b["orte"].append(("nur in Datei", u, n))
        elif rooms[u].get("name") != n:
            b["orte"].append(("Name", u, "%s -> %s" % (n, rooms[u].get("name"))))
    for u in rooms:
        if u not in orte:
            b["orte"].append(("nur am Miniserver", u, rooms[u].get("name", "")))
    for u, n in kategorien.items():
        if u not in cats:
            b["kategorien"].append(("nur in Datei", u, n))
        elif cats[u].get("name") != n:
            b["kategorien"].append(("Name", u, "%s -> %s" % (n, cats[u].get("name"))))
    for u in cats:
        if u not in kategorien:
            b["kategorien"].append(("nur am Miniserver", u, cats[u].get("name", "")))
    b["zahlen"].update({"orte_datei": len(orte), "orte_ms": len(rooms), "kat_datei": len(kategorien), "kat_ms": len(cats)})
    return b


def ausgeben(b, pfad_p, pfad_s, out):
    w = out.write
    z = b["zahlen"]
    w("# Abgleich Projektdatei gegen Strukturdatei des Miniservers\n\n")
    w("Projektdatei: %s\nStrukturdatei: %s\n\n" % (pfad_p, pfad_s))
    w("| Kopf | Datei | Miniserver |\n|---|---|---|\n")
    for k, a, m in b["kopf"]:
        w("| %s | %s | %s |\n" % (k, a, m))
    w("\n")
    w("Bausteine am Miniserver: %d, davon in der Datei wiedergefunden: %d (%.1f %%); dazu %d Unterbausteine, "
      "%d davon ihrem Baustein zugeordnet. Bausteine mit Visu=\"true\" in der Datei: %d.\n"
      % (z["ms"], z["treffer"], z["quote"], z.get("unter", 0), z.get("unter_ok", 0), z["visu"]))
    w("Raeume: Datei %d, Miniserver %d. Kategorien: Datei %d, Miniserver %d.\n\n"
      % (z["orte_datei"], z["orte_ms"], z["kat_datei"], z["kat_ms"]))
    if b["stand_fremd"]:
        w("**[FEHL] Die Strukturdatei gehoert erkennbar zu einem anderen Stand als die Projektdatei** "
          "(Projektname weicht ab oder Trefferquote unter 90 %%). Die Einzelbefunde unten sagen dann "
          "nur, dass es ein anderer Stand ist - nicht, was in der Anlage fehlt.\n\n")
    befunde = 0
    if b["ms_nicht_in_datei"]:
        befunde += len(b["ms_nicht_in_datei"])
        w("## Am Miniserver, aber nicht in der Datei (%d)\n\n" % len(b["ms_nicht_in_datei"]))
        for u, n, t in b["ms_nicht_in_datei"][:200]:
            w("- %s [%s]  `%s`\n" % (n, t, u))
        if len(b["ms_nicht_in_datei"]) > 200:
            w("- ... und %d weitere\n" % (len(b["ms_nicht_in_datei"]) - 200))
        w("\n")
    if b["datei_nicht_am_ms"]:
        befunde += len(b["datei_nicht_am_ms"])
        w("## In der Datei fuer die Visualisierung vorgesehen, am Miniserver nicht vorhanden (%d)\n\n" % len(b["datei_nicht_am_ms"]))
        w("| Baustein | Typ | Raum | Kategorie | UUID |\n|---|---|---|---|---|\n")
        for u, t, n, o, k in b["datei_nicht_am_ms"]:
            w("| %s | %s | %s | %s | `%s` |\n" % (n, t, o, k, u))
        w("\n")
    if b["virtualin_nicht_am_ms"]:
        w("Dazu %d VirtualIn mit Visu=\"true\", die am Miniserver nie erscheinen (Regeln/08) - kein Befund; mit --alle werden sie aufgefuehrt.\n\n" % b["virtualin_nicht_am_ms"])
    if b["ohne_raum"]:
        w("## Visu=\"true\" ohne Raum und Kategorie - erwartungsgemaess nicht am Miniserver (%d)\n\n" % len(b["ohne_raum"]))
        w("Gemessen 05.09.2026: ohne Raum und Kategorie nimmt der Miniserver einen Baustein nicht in die Strukturdatei auf. "
          "Kein Befund am Miniserver, aber ein Widerspruch in der Datei: Hilfsbaustein -> Raum und Kategorie Nicht zugeordnet setzen und das Visu-Attribut entfernen (Config setzt eine leere IoData auf Visu=an zurueck; Regeln/08).\n\n")
        for u, t, n in b["ohne_raum"][:100]:
            w("- %s [%s]  `%s`\n" % (n, t, u))
        if len(b["ohne_raum"]) > 100:
            w("- ... und %d weitere\n" % (len(b["ohne_raum"]) - 100))
        w("\n")
    if b["namen"]:
        befunde += len(b["namen"])
        w("## Anderer Name am Miniserver als in der Datei (%d) - das sieht der Anwender\n\n" % len(b["namen"]))
        w("| Typ | Title (Datei) | Desc (Datei) | name (Miniserver) | UUID |\n|---|---|---|---|---|\n")
        for u, t, ti, de, n in b["namen"]:
            w("| %s | %s | %s | %s | `%s` |\n" % (t, ti, de, n, u))
        w("\n")
    if b["gesichert"]:
        befunde += len(b["gesichert"])
        w("## Visualisierungspasswort: Datei und Miniserver uneins (%d)\n\n| Baustein | VisuPwd (Datei) | isSecured (Miniserver) | UUID |\n|---|---|---|---|\n" % len(b["gesichert"]))
        for u, n, a, m in b["gesichert"]:
            w("| %s | %s | %s | `%s` |\n" % (n, a, m, u))
        w("\n")
    for titel, liste in (("Raeume", b["orte"]), ("Kategorien", b["kategorien"])):
        if liste:
            befunde += len(liste)
            w("## %s (%d Abweichungen)\n\n" % (titel, len(liste)))
            for art, u, n in liste:
                w("- %s: %s  `%s`\n" % (art, n, u))
            w("\n")
    if b["stand_fremd"]:
        return 3
    if befunde == 0:
        w("Kein Befund: Strukturdatei und Projektdatei passen zusammen.\n")
        return 0
    w("Summe: %d Befunde.\n" % befunde)
    return 1


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    alle = "--alle" in argv
    md = argv[argv.index("--markdown") + 1] if "--markdown" in argv else None
    sp = argv[argv.index("--speichern") + 1] if "--speichern" in argv else None
    pfad_p = argv[0]
    try:
        kopf, bausteine, orte, kategorien = projekt_lesen(pfad_p)
    except Exception as e:
        print("[FEHL] Projektdatei nicht lesbar: %s" % e); return 2
    try:
        if "--holen" in argv:
            basis = argv[argv.index("--holen") + 1]
            roh = holen(basis)
            if sp:
                with open(sp, "wb") as f:
                    f.write(roh)
            st = json.loads(roh.decode("utf-8-sig"))
            pfad_s = basis + "/data/LoxAPP3.json"
        else:
            pfad_s = argv[1]
            st = struktur_lesen(pfad_s)
    except Exception as e:
        print("[FEHL] Strukturdatei nicht lesbar/abrufbar: %s" % e); return 2
    b = abgleich(kopf, bausteine, orte, kategorien, st, alle)
    buf = io.StringIO()
    rc = ausgeben(b, pfad_p, pfad_s, buf)
    sys.stdout.write(buf.getvalue())
    if md:
        with open(md, "w", encoding="utf-8", newline="\n") as f:
            f.write(buf.getvalue())
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
