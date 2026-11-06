# Laeuft auf: Windows, Python 3. Prueft, ob die Abschriften gemeinsamer Dateien in einem
# Plugin-Ordner byte-gleich mit der Stammfassung unter Werkzeuge/gemeinsam/ sind
# (Octopus-c1, 30.09.2026: Octopus, aWATTar und Tibber tragen dieselbe planer.php; ein
# LoxBerry-Plugin kann keine Datei eines anderen Plugins laden, deshalb bleiben es drei
# Abschriften - aber aus EINER Quelle, und die Kette meldet jede Abweichung).
#
# Seit dem Sprachmodul (Nr. 36 b, 02.10.2026) auch sprachausgabe.php - je nach Linie unter
# webfrontend/html/ oder webfrontend/htmlauth/ (dort, wo die Bibliothek der Linie liegt).
# Traegt eine Linie die Abschrift, wird zusaetzlich der Abschnitt [ANSAGE] ihrer
# templates/lang/language_de.ini und language_en.ini gegen gemeinsam/sprachausgabe_texte.json
# gehalten: gleiche Schluessel, gleiche Werte. Fehlt der Abschnitt, fuehrt die Linie eigene
# Schluessel (Stufe 1 des Wanderwegs) - das ist "nicht geprueft", kein Befund. Ebenso ein Abschnitt
# [ANSAGE], der weniger als die Haelfte der Modulschluessel traegt: vier Linien fuehren einen eigenen
# dieses Namens, Weissware darin 15 Namen wie im Modul (sp1-wz, 02.10.2026, Fehlalarm an den Bauten
# vb_sp1_abf/oc/ww_bau gemessen). Ein Modulabschnitt muss alle Modulschluessel mit gleichen Werten
# tragen; linieneigene Schluessel daneben sind ein Hinweis.
#
# Aufruf: python gemeinsam_pruefen.py <plugin-ordner>      -> Befund je Datei, rc 1 bei Abweichung
#         python gemeinsam_pruefen.py --verteilen <ordner>  -> Stammfassung in den Ordner kopieren
#         python gemeinsam_pruefen.py --ini-abschnitt de|en -> Abschnitt [ANSAGE] fuer die .ini ausgeben
# Eine Abschrift wird nur geprueft, wenn der Ordner die Datei am selben relativen Pfad hat.
# --verteilen fasst keine .ini an; den Abschnitt schreibt der Spracherzeuger der Linie.
#
# Seit der Befehlsbruecke (Gruppe 1, 18.10.2026) auch bin/befehlsbruecke.php und bin/befehlsbruecke.sh
# (Stammfassung gemeinsam/befehlsbruecke.php/.sh; linieneigen bleibt bin/befehle_zuordnung.php).
# --stamm <ordner> nimmt die Stammfassungen aus einem anderen Ordner (Bauordner, Pruefung) - seit
# Pflegewelle 22 auch fuer --ini-abschnitt.
import hashlib, json, shutil, sys
from pathlib import Path

STAMM = Path(__file__).resolve().parent / "gemeinsam"
# relativer Pfad im Plugin -> Datei unter Werkzeuge/gemeinsam/
DATEIEN = {
    "webfrontend/html/planer.php": "planer.php",
    "webfrontend/html/sprachausgabe.php": "sprachausgabe.php",
    "webfrontend/htmlauth/sprachausgabe.php": "sprachausgabe.php",
    # 05.11.2026: Kodi-NG traegt seine Abschrift unter bin/; ohne diese Zeile blieb die Kette dort blind.
    "bin/sprachausgabe.php": "sprachausgabe.php",
    "bin/befehlsbruecke.php": "befehlsbruecke.php",
    "bin/befehlsbruecke.sh": "befehlsbruecke.sh",
    # Seit Gruppe 33 (27.10.2026): Xiaomi-Cloud-Anmeldung (BLE-Scanner, Saugroboter, Xiaomi Licht)
    "webfrontend/html/xiaomi_cloud.php": "xiaomi_cloud.php",
    "webfrontend/htmlauth/xiaomi_cloud.php": "xiaomi_cloud.php",
    # Gruppe 43 (29.10.2026): die Anbieterregel fuer haus/strompreis und haus/speicher (Spotpreis Tibber,
    # Zendure SolarFlow; danach aWATTar, Octopus, Marstek Venus E).
    "webfrontend/html/haus_anbieter.php": "haus_anbieter.php",
    "webfrontend/htmlauth/haus_anbieter.php": "haus_anbieter.php",
}
TEXTE = "sprachausgabe_texte.json"
ABSCHNITT = "ANSAGE"


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()[:16]


def ini_abschnitt(sprache):
    """Den Abschnitt [ANSAGE] fuer language_<sprache>.ini aus der Textdatei bauen (LF)."""
    d = json.loads((STAMM / TEXTE).read_bytes().decode("utf-8"))[sprache]
    z = ["[" + ABSCHNITT + "]"]
    for s, w in d.items():
        z.append('%s="%s"' % (s, w))
    return "\n".join(z) + "\n"


def abschnitt_lesen(datei):
    """Schluessel -> Wert (ohne die umschliessenden Anfuehrungszeichen) des Abschnitts [ANSAGE],
    oder None, wenn es ihn nicht gibt. Doppelte Schluessel kommen als Liste zurueck."""
    if not datei.is_file():
        return None
    aus, drin, doppelt = None, False, []
    for zeile in datei.read_bytes().decode("utf-8", "replace").splitlines():
        z = zeile.strip()
        if z.startswith("[") and z.endswith("]"):
            drin = z[1:-1] == ABSCHNITT
            if drin:
                aus = {} if aus is None else aus
            continue
        if not drin or not z or z.startswith(";") or "=" not in z:
            continue
        s, w = z.split("=", 1)
        s, w = s.strip(), w.strip()
        if len(w) >= 2 and w[0] == '"' and w[-1] == '"':
            w = w[1:-1]
        if s in aus:
            doppelt.append(s)
        aus[s] = w
    if aus is not None and doppelt:
        aus["__doppelt__"] = doppelt
    return aus


def texte_pruefen(ordner):
    """Befunde zum Abschnitt [ANSAGE] einer Linie mit sprachausgabe.php. Rueckgabe: Zahl der Befunde."""
    befund = 0
    quelle = STAMM / TEXTE
    if not quelle.is_file():
        print("  BEFUND Textdatei der Stammfassung fehlt (%s)" % quelle)
        return 1
    soll_alle = json.loads(quelle.read_bytes().decode("utf-8"))
    for sprache in ("de", "en"):
        rel = "templates/lang/language_%s.ini" % sprache
        ist = abschnitt_lesen(ordner / rel)
        if ist is None:
            print("  nicht geprueft %s: kein Abschnitt [%s] (die Linie fuehrt eigene Schluessel)" % (rel, ABSCHNITT))
            continue
        soll = soll_alle[sprache]
        if not soll:
            print("  BEFUND Textdatei: Sprache %s leer" % sprache)
            befund += 1
            continue
        # sp1-wz (02.10.2026): vier Linien fuehren schon einen EIGENEN Abschnitt [ANSAGE] (Abfahrt,
        # Octopus, aWATTar, Weissware). Traegt der Abschnitt keinen Schluessel des Moduls, ist es der
        # der Linie (Stufe 1) - "nicht geprueft", kein Befund. Traegt er Modulschluessel, muessen alle
        # da und gleich sein; linieneigene Schluessel daneben sind ein Hinweis.
        # Gleiche NAMEN allein machen ihn nicht zum Modulabschnitt: Weissware fuehrt in ihrem eigenen
        # [ANSAGE] 15 Schluessel mit Namen des Moduls (L_IP, O_MUSICSERVER, TESTTEXT ...) und eigenen
        # Werten (gemessen 02.10.2026). Als Modulabschnitt gilt er erst, wenn er mindestens die Haelfte
        # der Modulschluessel traegt; darunter ist es der Abschnitt der Linie, die Namensgleichen sind
        # ein Hinweis.
        eigene = sorted(set(ist) - set(soll) - {"__doppelt__"})
        gemeinsam = sorted(set(ist) & set(soll))
        if 2 * len(gemeinsam) < len(soll):
            print("  nicht geprueft %s: Abschnitt [%s] der Linie (%d eigene Schluessel%s)"
                  % (rel, ABSCHNITT, len(eigene),
                     (", Hinweis: %d mit Namen wie im Modul, z. B. %s" % (len(gemeinsam), ", ".join(gemeinsam[:3])))
                     if gemeinsam else ""))
            continue
        fehlt = sorted(set(soll) - set(ist))
        anders = sorted(s for s in soll if s in ist and ist[s] != soll[s])
        dop = ist.get("__doppelt__", [])
        if fehlt or anders or dop:
            befund += 1
            print("  BEFUND %s [%s]: %d fehlen, %d anders, %d doppelt - z. B. %s" % (
                rel, ABSCHNITT, len(fehlt), len(anders), len(dop), ", ".join((fehlt + anders + dop)[:5])))
        else:
            print("  gleich %s [%s] (%d Schluessel)%s" % (
                rel, ABSCHNITT, len(soll),
                ("; Hinweis: %d eigene Schluessel der Linie daneben (%s)" % (len(eigene), ", ".join(eigene[:3])))
                if eigene else ""))
    return befund


def main():
    args = sys.argv[1:]
    global STAMM
    # Pflegewelle 22 (25.10.2026): --stamm zuerst auswerten. Bis dahin las --ini-abschnitt immer
    # Werkzeuge/gemeinsam/ - auch mit --stamm (gemessen: FileNotFoundError ...\gemeinsam\sprachausgabe_texte.json).
    if "--stamm" in args:
        i = args.index("--stamm")
        if i + 1 >= len(args):
            print("Aufruf: gemeinsam_pruefen.py --stamm <ordner> <plugin-ordner>"); return 2
        STAMM = Path(args[i + 1]).resolve()
        del args[i:i + 2]
    if "--ini-abschnitt" in args:
        i = args.index("--ini-abschnitt")
        if i + 1 >= len(args) or args[i + 1] not in ("de", "en"):
            print("Aufruf: gemeinsam_pruefen.py --ini-abschnitt de|en"); return 2
        sys.stdout.buffer.write(ini_abschnitt(args[i + 1]).encode("utf-8"))
        return 0
    verteilen = "--verteilen" in args
    args = [a for a in args if a != "--verteilen"]
    if len(args) != 1:
        print(__doc__ or "Aufruf siehe Kopf"); return 2
    ordner = Path(args[0])
    befund = 0
    gesehen = 0
    sprachmodul = False
    for rel, stamm in DATEIEN.items():
        ziel = ordner / rel
        quelle = STAMM / stamm
        if not ziel.is_file():
            continue
        gesehen += 1
        if stamm == "sprachausgabe.php":
            sprachmodul = True
        if not quelle.is_file():
            print("  BEFUND %s: Stammfassung fehlt (%s)" % (rel, quelle)); befund += 1; continue
        if verteilen:
            shutil.copyfile(quelle, ziel)
            print("  verteilt %s (%s)" % (rel, md5(ziel))); continue
        if ziel.read_bytes() == quelle.read_bytes():
            print("  gleich %s (%s)" % (rel, md5(ziel)))
        else:
            print("  BEFUND %s weicht von Werkzeuge/gemeinsam/%s ab (%s gegen %s) - Aenderung in der "
                  "Stammfassung machen und mit --verteilen in alle Linien bringen" % (rel, stamm, md5(ziel), md5(quelle)))
            befund += 1
    if sprachmodul and not verteilen:
        befund += texte_pruefen(ordner)
    if gesehen == 0:
        print("  keine gemeinsame Datei in dieser Linie")
    return 1 if befund else 0


if __name__ == "__main__":
    sys.exit(main())
