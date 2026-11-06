# -*- coding: utf-8 -*-
"""Prueft die Morgensperre unabhaengig aus der fertigen Datei.

Die entscheidende Eigenschaft ist die PAARUNG: der Speicher, der die
Sonnenstandsautomatik eines Rollladens sperrt, muss von genau der
Schaltuhr-Gruppe zurueckgesetzt werden, die diesen Rollladen oeffnet.
Sitzt da ein Versatz, sperrt ein Rollladen bis zur Oeffnung eines anderen.

Aufruf:  morgensperre_pruefen.py DATEI.Loxone
Rueckgabe: 0 in Ordnung, 1 Befund, 2 Fehler
"""
import re
import sys

try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass


def lies(pfad):
    roh = open(pfad, "rb").read()
    if roh[:3] != b"\xef\xbb\xbf":
        raise SystemExit("BOM fehlt")
    return roh.decode("utf-8-sig").split("\r\n")


def bausteine(z):
    stapel, out = [], []
    for i, x in enumerate(z):
        s = x.strip()
        if s.startswith("<C "):
            stapel.append(i)
        elif s == "</C>" and stapel:
            out.append((stapel.pop(), i))
    return sorted(out)


def kons(z, a, e):
    out, k = {}, None
    for j in range(a + 1, e):
        s = z[j].strip()
        m = re.match(r'<Co K="(\w+)"', s)
        if m:
            k = m.group(1)
            uu = re.search(r'\bU="([^"]*)"', z[j])
            out.setdefault(k, {"u": uu.group(1) if uu else None, "in": []})
        elif s.startswith("<In Input=") and k:
            out[k]["in"].append(re.search(r'Input="([^"]*)"', s).group(1))
    return out


def pruefe(pfad):
    z = lies(pfad)
    gr = bausteine(z)
    befunde = []

    def titel(a):
        m = re.search(r'Title="([^"]*)"', z[a])
        return m.group(1) if m else "?"

    def typ(a):
        return re.search(r'Type="([^"]*)"', z[a]).group(1)

    # --- die drei globalen Bausteine finden ------------------------------
    def eins(bed, name):
        tr = [(a, e) for a, e in gr if bed(a)]
        if len(tr) != 1:
            befunde.append("%s: %d Treffer statt 1" % (name, len(tr)))
            return None
        return tr[0]

    schalter = eins(lambda a: titel(a) == "Beschattung erst nach der Morgenoeffnung",
                    "Freigabeschalter")
    impuls = eins(lambda a: titel(a) == "Impuls 00:30 Morgensperre setzen", "Impuls")
    undb = eins(lambda a: titel(a) == "UND Morgensperre setzen", "UND")
    if not (schalter and impuls and undb):
        return befunde

    ks = kons(z, *schalter)
    ki = kons(z, *impuls)
    ku = kons(z, *undb)

    # --- 1. Schalter ab Werk aus, ohne Remanenz --------------------------
    if 'Def="1"' in z[schalter[0]]:
        befunde.append("Freigabeschalter steht ab Werk AN")
    if 'Inv="true"' not in [x.strip() for x in [""]] and \
       'K="Remanence" Inv="true"' not in "\r\n".join(z[schalter[0]:schalter[1]]):
        befunde.append("Freigabeschalter: Remanenz nicht abgewaehlt")

    # --- 2. Impuls: Uhrzeit ----------------------------------------------
    sec = re.search(r'\bSec="(\d+)"', z[impuls[0]])
    if not sec:
        befunde.append("Impuls: kein Sec")
    else:
        s = int(sec.group(1))
        if s != 1800:
            befunde.append("Impuls steht auf %02d:%02d, erwartet 00:30" % (s // 3600, s % 3600 // 60))
        # frueheste Beschattungsperiode im Jahr: 05:44 Ortszeit
        if s >= 5 * 3600 + 44 * 60:
            befunde.append("Impuls liegt nach dem fruehesten Periodenstart 05:44")

    # --- 3. UND: genau eine Quelle je Eingang, die richtigen -------------
    for k, soll in (("I1", ki["Q"]["u"]), ("I2", ks["Q"]["u"])):
        if len(ku[k]["in"]) != 1:
            befunde.append("UND.%s hat %d Quellen, Hausregel ist genau eine"
                           % (k, len(ku[k]["in"])))
        elif ku[k]["in"][0] != soll:
            befunde.append("UND.%s haengt an der falschen Quelle" % k)

    # --- 4. die Monoflop-Gruppen unabhaengig neu bilden ------------------
    besitzer = {}
    for a, e in gr:
        for k, v in kons(z, a, e).items():
            if v["u"]:
                besitzer[v["u"]] = (a, k)
    gruppe_von_rollladen = {}
    for a, e in gr:
        if titel(a) != "Impuls Rollladen AUF (EndUp)":
            continue
        q = kons(z, a, e)["Q"]["u"]
        for b, c in gr:
            if typ(b) != "AutoJalousie":
                continue
            kb = kons(z, b, c)
            if q in kb.get("EndUp", {"in": []})["in"]:
                gruppe_von_rollladen[titel(b)] = q

    # --- 5. Paarung Speicher <-> Rollladen -------------------------------
    # Nur die Speicher selbst. Die Nachlauf-Bausteine heissen ebenfalls
    # "Morgensperre nachlaufen ...", sind aber OffDelay und haben kein On.
    sperren = [(a, e) for a, e in gr
               if typ(a) == "PushButton" and titel(a).startswith("Morgensperre ")]
    if len(sperren) != 15:
        befunde.append("Morgensperren: %d statt 15" % len(sperren))
    sperre_von_q = {}
    for a, e in sperren:
        k = kons(z, a, e)
        # On genau einmal vom UND
        if k["On"]["in"] != [ku["Q"]["u"]]:
            befunde.append("%s: On haengt nicht am UND" % titel(a)[:40])
        # Reset: Gruppenimpuls + Schalter-Qoff
        rs = set(k["Reset"]["in"])
        if ks["Qoff"]["u"] not in rs:
            befunde.append("%s: Reset ohne Schalter-Qoff" % titel(a)[:40])
        gruppen_q = [x for x in rs if x != ks["Qoff"]["u"]]
        if len(gruppen_q) != 1:
            befunde.append("%s: %d Gruppenimpulse am Reset" % (titel(a)[:40], len(gruppen_q)))
            continue
        sperre_von_q[k["Q"]["u"]] = gruppen_q[0]

    # --- 5b. Nachlauf: OffDelay zwischen Speicher und EnAutoShade --------
    # Ohne ihn faellt die Sperre im Augenblick des Oeffnungsimpulses, und die
    # Automatik gibt die Beschattungsposition vor, bevor der Rollladen oben
    # ist (gemessen 10.09.2026). Der Nachlauf muss ueber der laengsten
    # Oeffnungsdauer aller Rolllaeden liegen.
    laengste_auffahrt = 0
    for a, e in gr:
        if typ(a) != "AutoJalousie":
            continue
        for j in range(a + 1, e):
            m = re.match(r'<Co K="TimeEnd"[^>]*\bDef="([0-9.,]+)"', z[j].strip())
            if m:
                laengste_auffahrt = max(laengste_auffahrt,
                                        float(m.group(1).replace(",", ".")))
    nachlauf_q = {}
    for a, e in gr:
        if typ(a) != "OffDelay":
            continue
        k = kons(z, a, e)
        quelle = k.get("InputTrigger", {"in": []})["in"]
        if len(quelle) != 1 or quelle[0] not in sperre_von_q:
            continue
        t = None
        for j in range(a + 1, e):
            m = re.match(r'<Co K="Time"[^>]*\bDef="([0-9.,]+)"', z[j].strip())
            if m:
                t = float(m.group(1).replace(",", "."))
        if t is None:
            befunde.append("%s: kein Time am Nachlauf" % titel(a)[:40])
        elif t <= laengste_auffahrt:
            befunde.append("%s: Nachlauf %gs liegt nicht ueber der laengsten "
                           "Auffahrt %gs" % (titel(a)[:40], t, laengste_auffahrt))
        nachlauf_q[k["Q"]["u"]] = quelle[0]
    if len(nachlauf_q) != 15:
        befunde.append("Nachlauf-OffDelay: %d statt 15" % len(nachlauf_q))
    # jeder Speicherausgang darf NUR an seinen Nachlauf gehen
    for q in sperre_von_q:
        n = sum(1 for x in z if x.strip() == '<In Input="%s"/>' % q)
        if n != 1:
            befunde.append("Speicherausgang mit %d Abnehmern statt 1 (nur der "
                           "Nachlauf gehoert dorthin)" % n)
    # und jeder Nachlauf nur an eine Stelle weiter
    for q in nachlauf_q:
        n = sum(1 for x in z if x.strip() == '<In Input="%s"/>' % q)
        if n != 1:
            befunde.append("Nachlaufausgang mit %d Abnehmern statt 1" % n)

    # --- 5c. Strahlungssperre: ODER zwischen Nachlauf und EnAutoShade ----
    # Gibt es sie nicht, haengt EnAutoShade direkt am Nachlauf - das ist der
    # Stand vor dem 10.09.2026 und hier kein Befund, sondern eine Lage.
    strahl_und = None
    for a, e in gr:
        if typ(a) == "And" and titel(a) == "UND keine Strahlung + freigegeben":
            strahl_und = (a, e)
    oder_q = {}
    for a, e in gr:
        if typ(a) != "Or" or not titel(a).startswith("Beschattungssperre "):
            continue
        k = kons(z, a, e)
        for kk in ("I1", "I2"):
            if len(k.get(kk, {"in": []})["in"]) != 1:
                befunde.append("%s.%s hat nicht genau eine Quelle" % (titel(a)[:36], kk))
        i1 = (k.get("I1", {"in": []})["in"] or [None])[0]
        i2 = (k.get("I2", {"in": []})["in"] or [None])[0]
        if i1 not in nachlauf_q:
            befunde.append("%s: I1 haengt nicht an einem Nachlauf" % titel(a)[:36])
        if strahl_und and i2 != kons(z, *strahl_und)["Q"]["u"]:
            befunde.append("%s: I2 haengt nicht am Strahlungs-UND" % titel(a)[:36])
        oder_q[k["Q"]["u"]] = i1
    if oder_q and len(oder_q) != 15:
        befunde.append("Beschattungssperre-ODER: %d statt 15" % len(oder_q))
    if oder_q and not strahl_und:
        befunde.append("ODER vorhanden, aber kein 'UND keine Strahlung + freigegeben'")
    if strahl_und:
        ka = kons(z, *strahl_und)
        # I1 muss INVERTIERT sein und an der entprellten Freigabe haengen
        inv = False
        for j in range(strahl_und[0] + 1, strahl_und[1]):
            s = z[j].strip()
            if s.startswith('<Co K="I1"'):
                inv = 'Inv="true"' in s
                break
        if not inv:
            befunde.append("Strahlungs-UND: I1 ist NICHT invertiert - die Sperre "
                           "wirkte dann genau verkehrt herum")
        tr = [(a, e) for a, e in gr if titel(a) == "ODER Beschattungsfreigabe entprellt"]
        if len(tr) == 1:
            soll = kons(z, *tr[0])["Q"]["u"]
            if ka.get("I1", {"in": []})["in"] != [soll]:
                befunde.append("Strahlungs-UND: I1 haengt nicht an der entprellten Freigabe")
        schalter2 = [(a, e) for a, e in gr
                     if typ(a) == "PushButton"
                     and titel(a) == "Beschattung nur bei Fassadenstrahlung"]
        if len(schalter2) != 1:
            befunde.append("Schalter 'Beschattung nur bei Fassadenstrahlung': "
                           "%d Treffer statt 1" % len(schalter2))
        else:
            k2 = kons(z, *schalter2[0])
            if ka.get("I2", {"in": []})["in"] != [k2["Q"]["u"]]:
                befunde.append("Strahlungs-UND: I2 haengt nicht am Schalter")
            if 'K="Remanence" Inv="true"' not in "\r\n".join(
                    z[schalter2[0][0]:schalter2[0][1]]):
                befunde.append("Strahlungsschalter: Remanenz nicht abgewaehlt")

    # --- 6. der eigentliche Punkt: sperrt jeder den richtigen? -----------
    beschaltet = 0
    for a, e in gr:
        if typ(a) != "AutoJalousie":
            continue
        k = kons(z, a, e)
        en = k.get("EnAutoShade", {"in": []})["in"]
        if not en:
            if titel(a) != "Beamerleinwand":
                befunde.append("%s: EnAutoShade unbeschaltet" % titel(a)[:40])
            continue
        beschaltet += 1
        if len(en) != 1:
            befunde.append("%s: %d Quellen am EnAutoShade" % (titel(a)[:40], len(en)))
            continue
        # Kette: EnAutoShade <- [ODER Strahlungssperre <-] Nachlauf <- Speicher
        q = en[0]
        if oder_q:
            if q not in oder_q:
                befunde.append("%s: EnAutoShade haengt nicht an einer "
                               "Beschattungssperre" % titel(a)[:40])
                continue
            q = oder_q[q]
        if q not in nachlauf_q:
            befunde.append("%s: EnAutoShade haengt nicht an einem Nachlauf" % titel(a)[:40])
            continue
        soll = gruppe_von_rollladen.get(titel(a))
        ist = sperre_von_q[nachlauf_q[q]]
        if soll is None:
            befunde.append("%s: keine Schaltuhr-Gruppe gefunden" % titel(a)[:40])
        elif soll != ist:
            befunde.append("VERSATZ %s: sperrt bis zur Oeffnung einer FREMDEN Gruppe"
                           % titel(a)[:40])
    if beschaltet != 24:
        befunde.append("EnAutoShade beschaltet: %d statt 24" % beschaltet)
    return befunde


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(2)
    b = pruefe(sys.argv[1])
    if b:
        print("%d Befund(e):" % len(b))
        for x in b:
            print("   " + x)
        sys.exit(1)
    print("Morgensperre in Ordnung: 15 Speicher, 24 Rolllaeden, Paarung stimmt,")
    print("Schalter ab Werk aus, Impuls 00:30 vor dem fruehesten Periodenstart.")
    sys.exit(0)
