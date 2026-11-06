#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Legt die Release-Seite zu einem bestehenden Tag an (Schritt 9 aus Regeln/11).

WARUM ES DIESES WERKZEUG GIBT
-----------------------------
`linie_veroeffentlichen.sh` macht die Schritte 1 bis 4 (Inhalt schieben, Tag,
Tagnachweis, die beiden .cfg). Schritt 9 - die Release-Seite - blieb Handarbeit
und wurde deshalb jedes Mal neu zusammengebaut. `gh` gibt es auf diesem Rechner
nicht; der Weg ist `POST /repos/<konto>/<name>/releases`.

**Nachweis ist HTTP 201 und die zurueckgegebene html_url, nicht der
Rueckgabewert des Aufrufs** (Regeln/11, Abschnitt 5). Am 10.08.2026 galten
sechs Seiten als angelegt, und keine einzige war es.

ZWEI VORSICHTSMASSNAHMEN
------------------------
1. Vorher wird `GET /releases/tags/<tag>` gefragt. GitHub duldet nur ein
   Release je Tag; ein zweiter POST antwortet 422 und legt nichts an - der
   Lauf saehe dann aus wie ein Fehlschlag, obwohl alles in Ordnung ist.
   Liegt die Seite schon, wird ihre Adresse gemeldet und nichts getan.
2. Ohne `--anlegen` wird NICHTS geschrieben. Der Probelauf sagt, was er taete,
   und zaehlt die Zeichen der Beschreibung.

Die Beschreibung kommt aus derselben Meldungsdatei, die auch
`linie_veroeffentlichen.sh` fuer den Commit benutzt; die Marken {NAME}, {NEU},
{ALT} und {STAT} werden gleich ersetzt. Bleibt eine Marke stehen, bricht das
Werkzeug ab - eine Release-Seite mit einem rohen {STAT} darin ist peinlicher
als ein Abbruch.

DER SCHLUESSEL kommt aus der Umgebung ($PAT_EIN) und wird nirgends ausgegeben.
Zum Schieben taugen nur die beiden klassischen Schluessel (ghp_, 40 Zeichen);
der feinkoernige antwortet 403 (Regeln/11).

Aufruf:
  PAT_EIN=... python3 Werkzeuge/release_seite.py <repo> <tag> <meldungsdatei> \\
                      <neu> <alt> <stat> [--anlegen]

  <repo>  Name OHNE "LoxBerry-Plugin-", also z. B. "Weissware"
  <tag>   mit v, also "v0.9.23"

DER TITEL der Seite ist die erste Zeile der Meldungsdatei, wenn sie eine H1
ist ("# Spotpreis Tibber 0.9.15"); sie steht dann nicht mehr im Rumpf. Fehlt
die H1, bricht das Werkzeug seit 24.09.2026 ab, auch im Probelauf; einen
Titel ohne H1 gibt es nur ausdruecklich mit --titel "Name X.Y.Z". Bis
15.09.2026 hiess die Seite IMMER wie der Tag, bis 24.09.2026 ohne H1 still
wie der Tag - siehe die Begruendung an der Stelle selbst.

EINE FREIGABENOTIZ IST KEINE MELDUNGSDATEI. Die `FREIGABE_*.md` im
Arbeitsordner tragen H1 wie "Freigabenotiz BLE-Scanner NG 1.3.13" oder "Text
fuer die Release-Seite v1.1.9"; als Titel waere das schlechter als der Tag.
Das Werkzeug kann die Gattung nicht erkennen und raet deshalb nicht - es
MELDET den gewaehlten Titel, im Probelauf wie nach dem Anlegen. Wer ihn dort
nicht liest, merkt es erst auf der Seite.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

KONTO = "timanders22"


def ruf(weg, daten=None):
    pat = os.environ.get("PAT_EIN", "")
    if not pat:
        print("ABBRUCH: $PAT_EIN ist nicht gesetzt.")
        raise SystemExit(2)
    a = urllib.request.Request(
        "https://api.github.com/repos/%s/%s" % (KONTO, weg),
        data=None if daten is None else json.dumps(daten).encode("utf-8"),
        headers={"Authorization": "Bearer " + pat,
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "loxberry-haus",
                 "X-GitHub-Api-Version": "2022-11-28"},
        method="GET" if daten is None else "POST")
    try:
        with urllib.request.urlopen(a, timeout=60) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:300]


def main() -> int:
    if len(sys.argv) < 7:
        print(__doc__)
        return 2
    repo, tag, datei, neu, alt, stat = sys.argv[1:7]
    anlegen = "--anlegen" in sys.argv
    name = "LoxBerry-Plugin-" + repo

    try:
        text = open(datei, encoding="utf-8").read()
    except OSError as err:
        print("ABBRUCH: Meldungsdatei nicht lesbar: %s" % err)
        return 2
    for marke, wert in (("{NAME}", repo), ("{NEU}", neu),
                        ("{ALT}", alt), ("{STAT}", stat)):
        text = text.replace(marke, wert)
    rest = [w for w in text.split()
            if w.startswith("{") and w.endswith("}") and len(w) > 2]
    if rest:
        print("ABBRUCH: nicht ersetzte Marke(n): %s" % ", ".join(sorted(set(rest))))
        return 1

    # DER TITEL KOMMT AUS DER UEBERSCHRIFT, NICHT AUS DEM TAG.
    #
    # Bis zum 15.09.2026 stand unten schlicht "name": tag. Jede so angelegte
    # Seite hiess dann "v0.9.15", waehrend die von Hand gemachten Vorgaenger
    # DERSELBEN Linie "Spotpreis Tibber 0.9.14" heissen - eine Drift, die nur
    # auffaellt, wenn man die Releaseliste einer Linie untereinander sieht.
    # Gemessen am 15.09.2026 ueber den ganzen Bestand: von 842 Release-Seiten
    # tragen 39 den Tag als Titel; die drei jungen darunter (Matter2Lox
    # v0.9.23, Weissware v0.9.22 und v0.9.23) sind mit diesem Werkzeug
    # angelegt, die uebrigen 36 stammen aus der Zeit davor.
    #
    # Die Hausform ist an VIER Seiten gemessen, nicht an einer: Spotpreis
    # Tibber 0.9.14, Zendure SolarFlow 0.9.19, Beschattungswaechter 0.9.18 und
    # Ultraschall 1.2.6. Bei allen vier gilt dasselbe - die erste Zeile der
    # Meldungsdatei ist eine H1, sie wird der TITEL, und sie steht danach NICHT
    # mehr im Rumpf ("Rumpf == Datei ohne die H1", viermal wahr). Sonst stuende
    # dieselbe Ueberschrift zweimal auf der Seite: einmal als Titel, einmal als
    # erste Zeile.
    #
    # Fehlt die H1, bleibt es beim Tag. Es gibt Meldungsdateien, die mit "##"
    # oder mit einem ganzen Satz anfangen (Midea2Lox 4.5.0, WiFi-Scanner-NG
    # 3.2.4); deren erste Zeile ist keine Ueberschrift, und ein Titel aus
    # einem halben Satz waere schlechter als der Tag.
    # Das ﻿ ist kein Zierrat: eine Meldungsdatei mit Byte-Reihenfolgemarke
    # haette sonst "﻿# Titel" in der ersten Zeile, die H1 waere nicht mehr
    # zu erkennen, und die Seite hiesse still wie der Tag - genau der Zustand,
    # gegen den diese Stelle steht.
    titel = tag
    zeilen = text.lstrip("﻿\n").split("\n")
    kopf = re.match(r"^#[ \t]+(\S.*?)[ \t]*$", zeilen[0]) if zeilen else None
    if kopf:
        titel = kopf.group(1)
        text = "\n".join(zeilen[1:]).lstrip("\n")
    # OHNE H1 WIRD ABGEBROCHEN - GEAENDERT 24.09.2026.
    #
    # Bis dahin hiess die Seite dann still wie der Tag. Am 24.09.2026 standen
    # so wieder 59 von 992 Seiten mit "v0.9.25" als Titel da, neun Tage nach
    # dem Durchgang, der alle 39 berichtigt hatte: andere Sitzungen gaben dem
    # Werkzeug die Commit-Meldung (ohne H1) statt der Datei fuer die Seite.
    # Der Probelauf meldete zwar "(Tag - die Datei hat keine H1)", gelesen
    # hat es niemand. Wer eine Meldung ohne H1 benutzen will (siehe oben:
    # "##" oder ein ganzer Satz), setzt den Titel ausdruecklich mit
    # --titel "Name X.Y.Z".
    if "--titel" in sys.argv:
        i = sys.argv.index("--titel")
        if i + 1 >= len(sys.argv) or not sys.argv[i + 1].strip():
            print("ABBRUCH: --titel ohne Text.")
            return 2
        titel = sys.argv[i + 1].strip()
    elif not kopf:
        print("ABBRUCH: die Meldungsdatei hat keine H1 - die Seite hiesse %r." % tag)
        print("    Die Datei fuer die Seite beginnt mit '# <Anzeigename> %s' (nicht die"
              " Commit-Meldung); oder --titel \"<Anzeigename> %s\" angeben." % (neu, neu))
        return 1

    code, antwort = ruf("%s/releases/tags/%s" % (name, tag))
    if code == 200:
        print("%-16s %-9s liegt schon: %s" % (repo, tag, antwort.get("html_url")))
        return 0
    if code != 404:
        print("%-16s %-9s Vorabfrage HTTP %s: %s" % (repo, tag, code, antwort))
        return 1
    print("%-16s %-9s Vorabfrage HTTP 404 - noch keine Seite" % (repo, tag))
    if not anlegen:
        print("    Probe - nichts angelegt (%d Zeichen Beschreibung)." % len(text))
        print("    Titel waere: %r %s" % (titel, "(aus --titel)" if "--titel" in sys.argv
                                          else "(aus der H1)"))
        print("    Mit --anlegen ausfuehren.")
        return 0

    code, antwort = ruf("%s/releases" % name,
                        {"tag_name": tag, "name": titel, "body": text,
                         "draft": False, "prerelease": False})
    if code != 201:
        print("    ABBRUCH: POST antwortete HTTP %s: %s" % (code, antwort))
        return 1
    # Der Titel wird MITGEMELDET. Er kommt jetzt aus der Datei, nicht mehr aus
    # dem Tag - also muss man sehen koennen, was daraus geworden ist, ohne die
    # Seite aufzurufen. Eine Meldungsdatei der falschen Gattung (eine
    # Freigabenotiz etwa, deren H1 "Freigabenotiz BLE-Scanner NG 1.3.13"
    # lautet) faellt nur hier auf.
    print("    HTTP 201  %s" % antwort.get("html_url"))
    print("    Titel: %r %s" % (titel, "(aus --titel)" if "--titel" in sys.argv
                                else "(aus der H1)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
