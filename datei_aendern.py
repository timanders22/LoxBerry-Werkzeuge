#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sicheres Aendern von Plugin-Dateien.

Drei Dinge, die in dieser Umgebung schon dreimal schiefgegangen sind und
deshalb hier ein fuer alle Mal geregelt werden:

  1. Gelesen und geschrieben wird BINAER. 'open(p, "w")' uebersetzt unter
     Windows still jedes \n zu \r\n, und Path.read_text(newline='') erhaelt
     die Zeilenenden auch nicht.
  2. Jeder Anker wird GEZAEHLT, bevor ersetzt wird. Kommt er nicht genau so
     oft vor wie erwartet, bricht der Lauf ab, BEVOR etwas geschrieben ist.
  3. Nach dem Schreiben wird die Zeilenendenart gegen den Zustand VORHER
     geprueft. Eine Mischung bricht ab und stellt den alten Inhalt wieder her.
"""

from pathlib import Path


def art(b):
    crlf = b.count(b"\r\n")
    lf = b.count(b"\n") - crlf
    if crlf and lf:
        return "GEMISCHT"
    if crlf:
        return "CRLF"
    if lf:
        return "LF"
    return "-"


class Datei:
    def __init__(self, pfad):
        self.pfad = Path(pfad)
        self.roh = self.pfad.read_bytes()
        self.neu = self.roh
        self.art_vorher = art(self.roh)
        self.schritte = []

    def _kod(self, s):
        if isinstance(s, bytes):
            return s
        # Zeilenenden des Bausteins an die Datei anpassen.
        t = s.replace("\r\n", "\n")
        if self.art_vorher == "CRLF":
            t = t.replace("\n", "\r\n")
        return t.encode("utf-8")

    def ersetze(self, alt, neu, anzahl=1, name=""):
        a, n = self._kod(alt), self._kod(neu)
        ist = self.neu.count(a)
        if ist != anzahl:
            raise SystemExit("ABBRUCH %s: Anker %r kommt %d mal vor, erwartet %d"
                             % (name or self.pfad.name, alt[:70], ist, anzahl))
        self.neu = self.neu.replace(a, n)
        self.schritte.append("ersetzt: %s" % (name or alt[:50]))
        return self

    def davor(self, anker, block, name=""):
        """Block VOR den Anker setzen.

        Die Wache dazu: enthaelt der Block den Anker selbst, stuende die
        Zeile hinterher zweimal da. Zweimal an einem Tag passiert (18.08.2026),
        beide Male mit einer offenen Klammer als Ergebnis, gemeldet ueber
        tausend Zeilen weiter. Gefunden hat es nur 'php -l'.
        """
        if anker.strip() and anker in block:
            raise SystemExit(
                "ABBRUCH %s: der Block enthaelt den Anker %r selbst - "
                "die Zeile stuende danach zweimal da."
                % (name or self.pfad.name, anker[:60]))
        return self.ersetze(anker, block + anker, 1, name)

    def danach(self, anker, block, name=""):
        """Block HINTER den Anker setzen - mit derselben Wache."""
        if anker.strip() and anker in block:
            raise SystemExit(
                "ABBRUCH %s: der Block enthaelt den Anker %r selbst."
                % (name or self.pfad.name, anker[:60]))
        return self.ersetze(anker, anker + block, 1, name)

    def anhaengen(self, block, name="", stil=None):
        """Block ans ENDE haengen - mit dem Zeilenende der Datei.

        Die Luecke, die am 19.08.2026 auffiel: ersetze/davor/danach brauchen
        alle einen Anker. Fuer einen Nachtrag ans Dateiende gibt es keinen,
        und genau dort sind in diesem Projekt viermal in Folge Zeilenenden
        verrutscht.

        Endet die Datei nicht auf einem Zeilenende, wird eines
        vorangestellt - sonst klebte der Nachtrag an der letzten Zeile.
        Angefasst wird dabei nichts Bestehendes.

        Gemischte Zeilenenden werden abgewiesen, nicht vereinheitlicht: ein
        stilles Vereinheitlichen waere eine Aenderung an Zeilen, die niemand
        angefasst hat.
        """
        if self.art_vorher == "GEMISCHT":
            raise SystemExit("ABBRUCH %s: gemischte Zeilenenden - ein Nachtrag "
                             "wuerde die Mischung fortschreiben."
                             % (name or self.pfad.name))
        if self.art_vorher == "-":
            # Leere Datei oder eine einzige Zeile ohne Abschluss: es gibt
            # nichts zu messen. Dann MUSS der Aufrufer den Stil nennen -
            # geraten wird hier nicht. 'art_vorher' wird mitgezogen, sonst
            # meldete schreiben() einen Stilwechsel, den der Nachtrag
            # zwangslaeufig herbeifuehrt.
            if stil not in ("LF", "CRLF"):
                raise SystemExit(
                    "ABBRUCH %s: die Datei hat kein Zeilenende, der Stil laesst "
                    "sich nicht messen. anhaengen(..., stil='LF') oder 'CRLF'."
                    % (name or self.pfad.name))
            self.art_vorher = stil
        elif stil is not None and stil != self.art_vorher:
            raise SystemExit(
                "ABBRUCH %s: die Datei ist %s, verlangt wurde %s. Die Messung "
                "sticht den Wunsch." % (name or self.pfad.name, self.art_vorher, stil))
        ze = b"\r\n" if self.art_vorher == "CRLF" else b"\n"
        b = self._kod(block)
        if self.neu and not self.neu.endswith(ze):
            self.neu += ze
        if not b.endswith(ze):
            b += ze
        self.neu += b
        self.schritte.append("angehaengt: %d Byte" % len(b))
        return self

    def muss_fehlen(self, muster, name=""):
        """Pruefen, dass etwas NOCH NICHT da ist - gegen doppeltes Einfuegen.

        Geprueft wird die kennzeichnende Zeile, nicht ein blosses Wort: ein
        Wort steht auch im erklaerenden Kommentar (belegt an 'socket_create').
        """
        if self._kod(muster) in self.neu:
            raise SystemExit("ABBRUCH %s: %r steht schon da - schon eingebaut?"
                             % (name or self.pfad.name, muster[:70]))
        return self

    def schreiben(self):
        nachher = art(self.neu)
        if nachher != self.art_vorher:
            raise SystemExit("ABBRUCH %s: Zeilenenden %s -> %s"
                             % (self.pfad.name, self.art_vorher, nachher))
        self.pfad.write_bytes(self.neu)
        print("  %-34s %s, %d Schritte, %d -> %d Byte"
              % (self.pfad.name, nachher, len(self.schritte),
                 len(self.roh), len(self.neu)))
