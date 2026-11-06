#!/usr/bin/env python3
"""Zeigt die Oberflaeche wirklich den richtigen Gateway-Text?

Gemessen an der GERENDERTEN Seite, nicht am Quelltext. Ein Quelltext mit
einer Verzweigung beweist nicht, dass sie greift - dazwischen liegen noch
die Sprachdateien und die Frage, ob die Fassung ueberhaupt ankommt.

Drei Laeufe je Plugin, mit verstellter `Mqtt.Gatewayversion` in der
general.json der Attrappe:

    Gatewayversion 1      -> der V1-Satz, und NUR er
    Gatewayversion 2      -> der V2-Satz, und der V1-Satz NICHT mehr
    Schluessel fehlt      -> beide Faelle genannt, keiner behauptet

Der zweite Lauf ist der eigentliche Punkt: eine Seite, die beide Texte
untereinander zeigt, waere sonst gruen.

    python3 gateway_wirkung.py <Pluginordner> [...]

Rueckgabe 0, wenn alle geprueften Plugins alle drei Faelle bestehen.
"""
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HIER = os.path.dirname(os.path.abspath(__file__))
ARBEIT = os.path.dirname(HIER)
LB = os.path.join(HIER, 'lb')
GEN = os.path.join(LB, 'config', 'system', 'general.json')

V1 = re.compile(r'ohne\s+(diesen|den)\s+eintrag\s+kommt\s+am\s+miniserver'
                r'|without\s+th(is|e)\s+entry\s+nothing\s+arrives', re.I)
# ERWEITERT 31.08.2026. Das Muster kannte nur EINE Formulierung -
# 'erkennt die Themengruppe von selbst'. Zendure SolarFlow sagt dasselbe
# mit anderen Worten ('Dort gibt es die Abo-Seite nicht mehr, das Gateway
# leitet von sich aus weiter') und wurde deshalb als 'kein Text - nicht
# messbar' gefuehrt. Das ist kein Strich, sondern ein blinder Fleck: die
# Zelle sah unverfaenglich aus, und dahinter stand eine voellig richtige
# Seite. Bei sieben anderen Linien stand dahinter ein echter Befund - man
# sieht der Zelle nicht an, welcher Fall vorliegt, und genau deshalb darf
# das Muster nicht am Wortlaut EINER Linie haengen.
#
# Aufgenommen werden nur Wendungen, die eine V2-AUSSAGE sind und in
# keinem V1-Text vorkommen koennen.
V2 = re.compile(r'erkennt\s+die\s+themengruppe\s+von\s+selbst'
                r'|detects\s+the\s+topic\s+group\s+by\s+itself'
                r'|abo.{0,3}seite\s+nicht\s+mehr'
                r'|leitet\s+von\s+sich\s+aus\s+weiter'
                r'|subscription\s+page\s+(?:no\s+longer|is\s+gone)'
                r'|forwards\s+(?:it|them|the\s+data)\s+by\s+itself', re.I)
UNBEKANNT = re.compile(r'lie(ß|ss)\s+sich\s+nicht\s+feststellen'
                       r'|could\s+not\s+be\s+determined', re.I)

# Die AUFFORDERUNG, ein Abo einzutragen - in jeder Gestalt, die im Bestand
# vorkommt: Ueberschrift, Schritttitel, Anleitungssatz.
#
# ERGAENZT 31.08.2026, und der Anlass steht in Skoda-Connect-NG 0.9.13. Dieses
# Werkzeug zaehlte nur die drei SAETZE und meldete das Plugin dreimal gruen.
# Gerendert mit Gatewayversion 2 stand auf der Seite:
#
#     "Das einzutragende Abo"                          <- Ueberschrift
#     "... einzutragen ist hier nichts."               <- der V2-Satz
#     "-> folgende Zeile eintragen und speichern:"     <- Anleitung
#     "Schritt 2: Abo im MQTT-Gateway eintragen"       <- Schritttitel
#
# Vier Aufforderungen gegen eine Verneinung. Der V2-Satz war richtig
# umgeschaltet, und die Seite war trotzdem falsch - weil alles um ihn herum
# unbedingt ausgegeben wird. Ein Werkzeug, das nur den Satz misst, den der
# Umbau angefasst hat, bestaetigt den Umbau statt die Seite.
AUFFORDERUNG = re.compile(
    r'einzutragende'
    r'|eintragen\s+und\s+speichern'
    r'|Abo\s+im\s+MQTT.Gateway\s+eintragen'
    r'|folgende\s+Zeile\s+eintragen'
    r'|enter\s+the\s+(?:following|subscription)'
    r'|add\s+the\s+subscription', re.I)


def hat_abo_abschnitt(text):
    """Zeigt diese Seite ueberhaupt einen MQTT-Abo-Abschnitt?

    Gemessen wird am gerenderten Text ohne Auszeichnung, nicht am Quelltext:
    ein Abschnitt, der hinter einer Bedingung steht und nicht erscheint, ist
    fuer den Anwender nicht da.

    Zwei Woerter genuegen und keines davon ist ein Satz aus der Musterliste -
    diese Wache darf nicht an dem haengen, was sie ermoeglichen soll.
    """
    klar = re.sub(r'<[^>]+>', ' ', text)
    return bool(re.search(r'Subscription', klar, re.I)
                or re.search(r'MQTT[\s-]?Gateway', klar, re.I))


def aufforderungen(text):
    """Aufforderungen zum Eintragen - aber nur rund um den Abo-Abschnitt.

    Zwei Wachen gegen Fehlalarme, beide noetig:

    1. Der V2-Satz und der Unbekannt-Satz werden VORHER herausgeschnitten.
       Sie enthalten selbst das Wort "einzutragen" ("einzutragen ist hier
       nichts") - wer sie mitliest, meldet jede richtig umgebaute Seite rot.
    2. Gesucht wird nur im Umkreis von 600 Zeichen um eine Fundstelle von
       "Subscription". So faellt "die Adresse in Loxone Config eintragen"
       nicht darunter: das ist eine Aufforderung, aber nicht diese.
    """
    rein = V2.sub(' ', UNBEKANNT.sub(' ', text))
    treffer = []
    for m in re.finditer(r'Subscription', rein, re.I):
        a, b = max(0, m.start() - 600), m.end() + 600
        for f in AUFFORDERUNG.finditer(rein[a:b]):
            s = ' '.join(f.group(0).split())
            if s not in treffer:
                treffer.append(s)
    return treffer


def abo_bereich(text):
    """Der Teil der Seite, in dem der Abo-Hinweis steht.

    Genommen wird der Umkreis von 900 Zeichen um jede Fundstelle von
    "Subscription" - das Wort, mit dem der Kern seinen Abschnitt benennt und
    das in jedem Abo-Text des Bestands vorkommt.

    Findet sich keins, gilt die GANZE Seite. Das ist Absicht: lieber einmal zu
    weit gesucht als eine Linie stillschweigend nicht gemessen. Der Aufrufer
    sieht am Ergebnis "kein Text - nicht messbar", wenn wirklich nichts da ist.
    """
    stellen = [m.start() for m in re.finditer(r'Subscription', text, re.I)]
    # Drei Anker, nicht einer. Intercom 2.2.4 formuliert seinen Abo-Hinweis
    # ohne das Wort "Subscription"; der Rueckfall auf die ganze Seite hat dort
    # eine maskierte Auszeichnung im Abschnitt "Einstellungen sichern"
    # getroffen und als Gateway-Befund gemeldet.
    #
    # NICHT UNBEKANNT als Anker. Das waere zirkulaer: wer die Fundstelle
    # eines Musters zum Bereich macht, findet das Muster darin
    # zwangslaeufig wieder. Und ausgerechnet dieser Satz ist der
    # unspezifischste - "liess sich nicht feststellen" steht bei
    # Robonect auch im Reiter Test ueber einen Strich in der
    # Selbstpruefung. Mit UNBEKANNT als Anker war Robonect 1.1.3 im
    # V1-Fall wieder rot, obwohl es zehn Minuten zuvor gruen gemessen
    # hatte - derselbe Fehlalarm wie am Morgen, nur durch eine andere
    # Tuer. V1 und V2 sind woertlich genug, um als Anker zu taugen.
    for muster in (V1, V2):
        stellen += [m.start() for m in muster.finditer(text)]
    if not stellen:
        return text
    stuecke = []
    for i in stellen:
        stuecke.append(text[max(0, i - 900):i + 900])
    return '\n'.join(stuecke)


SICHER = GEN + '.vor-gateway_wirkung'


def sicherung_anlegen():
    """Die Rohbytes VOR der ersten Aenderung auf die Platte legen.

    Bis zum 30.08.2026 gab es nur ein `finally`. Das ueberlebt keinen harten
    Abbruch - kein Taskkill, keine Zeitueberschreitung, kein Einsammeln eines
    Hintergrundprozesses. Und der Zustand, in dem das Werkzeug dabei stehen
    bleibt, ist ausgerechnet der schaedlichste: `Gatewayversion` entfernt.
    Genau so ist `Werkzeuge/lb/config/system/general.json` am 28.08.2026
    liegengeblieben, und jedes Werkzeug, das danach gegen diese Bank
    renderte, las "Gateway liess sich nicht feststellen" - ein Befund des
    Pruefstands, der wie ein Befund des Pruflings aussah.

    Eine Datei auf der Platte ueberlebt, was ein `finally` nicht ueberlebt.
    """
    if os.path.isfile(SICHER):
        return          # ein frueherer Lauf ist abgebrochen - die gilt
    if os.path.isfile(GEN):
        schreiben_atomar(SICHER, io.open(GEN, 'rb').read())


def sicherung_zurueck():
    """Zuruecklegen und die Sicherung entfernen. Auch beim naechsten Start."""
    if not os.path.isfile(SICHER):
        return False
    schreiben_atomar(GEN, io.open(SICHER, 'rb').read())
    os.remove(SICHER)
    return True


def schreiben_atomar(ziel, bytes_):
    """Erst daneben, dann umbenennen.

    `json.dump` schrieb bisher unmittelbar in die Zieldatei. Ein Abbruch
    mitten im Schreiben hinterliess dort halbes JSON - und die naechste
    Messung haette an einer unlesbaren general.json gemessen, ohne es zu
    merken."""
    tmp = '%s.%d.tmp' % (ziel, os.getpid())
    with io.open(tmp, 'wb') as f:
        f.write(bytes_)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, ziel)


def fassung_setzen(wert):
    """Nur den EINEN Wert anfassen - den Abschnitt nie anlegen.

    `d.setdefault('Mqtt', {})` legte den Abschnitt an, wenn es ihn nicht gab.
    Damit fuegte das Werkzeug einen Fremdkoerper in eine Bank ein, statt
    einen vorhandenen Wert zu aendern - `lb_attrappe` und `lb_leer` fuehren
    bewusst gar keinen Mqtt-Abschnitt. Wer dort misst, misst danach eine
    andere Bank als die, die er aufgesetzt hat.
    """
    if not os.path.isfile(GEN):
        raise SystemExit('general.json fehlt: %s - hier ist nichts zu messen.'
                         % GEN)
    d = json.load(io.open(GEN, encoding='utf-8'))
    hatte_abschnitt = isinstance(d.get('Mqtt'), dict)
    if not hatte_abschnitt and wert is None:
        return          # nichts zu tun: kein Abschnitt = keine Angabe
    d.setdefault('Mqtt', {})
    d['Mqtt'].pop('Gatewayversion', None)
    if wert is not None:
        d['Mqtt']['Gatewayversion'] = wert
    elif not hatte_abschnitt:
        d.pop('Mqtt', None)
    schreiben_atomar(GEN, json.dumps(d, ensure_ascii=False).encode('utf-8'))


# Gerendert wird ueber rendern.py - NICHT ueber einen eigenen php-Aufruf.
# Der erste Anlauf rief schlicht `php index.php` und bekam fuer JEDES Plugin
# eine leere Seite, auch fuer MGiSmart, das nachweislich richtig gebaut ist.
# rendern.py setzt acht Umgebungsvariablen, einen include_path, einen
# auto_prepend_file und fuenf Erweiterungen; das nachzubauen hiesse, eine
# zweite Wahrheit zu pflegen.
sys.path.insert(0, HIER)
import importlib

# Warum eine Seite nicht gerendert werden konnte - von rendern() gesetzt.
grund = ''
_rendern = importlib.import_module('rendern')


def rendern(ordner):
    """Die htmlauth-Oberflaeche einmal ausfuehren und den Text zurueckgeben.

    Rueckgabe None heisst "nicht gerendert" - und WARUM das so ist, gehoert in
    die Meldung. Bis zum 31.08.2026 sahen beide Gruende gleich aus:
    LoxoneIcons 2.0.4 hat eine Perl-index.cgi statt einer PHP-Oberflaeche und
    ueberhaupt kein MQTT; dort ist nichts zu messen. Ein fehlendes PHP auf dem
    Rechner waere dagegen ein Mangel des PRUEFSTANDS. Der Grund steht in
    rendern.grund.
    """
    global grund
    dateien = list(_rendern.oberflaechen(_rendern.Path(ordner)))
    if not dateien:
        grund = 'keine PHP-Oberflaeche (htmlauth/index.php)'
        return None
    php = next((p for _v, p in _rendern.PHPS if os.path.isfile(p)), None)
    if php is None:
        grund = 'auf diesem Rechner ist kein PHP gefunden worden'
        return None
    grund = ''
    seite, _befunde, _rest = _rendern.lauf(php, dateien[0],
                                           os.path.basename(ordner))
    return seite


def main():
    ordner = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not ordner:
        ordner = [e for e in sorted(os.listdir(ARBEIT))
                  if e.startswith('LoxBerry-Plugin-')
                  and os.path.isdir(os.path.join(ARBEIT, e))]
    if not os.path.isfile(GEN):
        print('general.json fehlt: %s' % GEN)
        print('Hier ist nichts zu messen - und eine angelegte Datei waere')
        print('eine Bank, die niemand aufgesetzt hat.')
        return 1

    # Lag von einem abgebrochenen Lauf noch eine Sicherung da, gilt SIE - und
    # zwar bevor irgendetwas gemessen wird. Sonst misst dieser Lauf gegen die
    # Truemmer des vorigen.
    if sicherung_zurueck():
        print('Hinweis: eine Sicherung eines abgebrochenen Laufs lag noch da')
        print('         und wurde zurueckgelegt, bevor gemessen wurde.')
        print()
    sicherung_anlegen()
    alt = io.open(GEN, 'rb').read()

    print('%-32s %-14s %-14s %s' % ('Plugin', 'V1 gesetzt', 'V2 gesetzt', 'ohne Angabe'))
    print('-' * 82)
    fehler = 0
    try:
        for e in ordner:
            # Der Name wird GESAEUBERT, bevor er verworfen wird: kommt die
            # Liste aus einer Datei, die Windows im Textmodus geschrieben hat,
            # traegt jeder Eintrag ein \r - und der Ordner ist dann "nicht
            # vorhanden", obwohl er dasteht.
            e = e.strip().strip('"').rstrip('/').rstrip('\\')
            o = e if os.path.isdir(e) else os.path.join(ARBEIT, e)
            if not os.path.isdir(o):
                # KEIN stilles continue. Am 31.08.2026 hat genau diese Zeile
                # 49 Ordner uebersprungen und "0 mit Befund" gemeldet.
                print('%-32s %s' % (os.path.basename(e)[:32],
                                    'BEFUND: Ordner nicht gefunden - hier wurde '
                                    'NICHTS gemessen'))
                fehler += 1
                continue
            urteile = []
            # Erst alle drei Seiten holen, dann urteilen. Der Vergleich
            # zwischen der V1- und der V2-Seite braucht beide gleichzeitig.
            seiten = {}
            for wert, name in ((1, 'v1'), (2, 'v2'), (None, 'unbekannt')):
                fassung_setzen(wert)
                seiten[name] = rendern(o)
            for erwartet in ('v1', 'v2', 'unbekannt'):
                t = seiten[erwartet]
                if t is None:
                    urteile.append('--  (%s)' % (grund or 'nicht gerendert'))
                    continue
                # Gesucht wird im ABO-ABSCHNITT, nicht auf der ganzen
                # Seite. Robonect 1.1.2 wurde sonst fuer einen Satz im Reiter
                # Test rot gemeldet, der zufaellig dieselben Woerter traegt.
                bereich = abo_bereich(t)
                hat_v1, hat_v2 = bool(V1.search(bereich)), bool(V2.search(bereich))
                hat_un = bool(UNBEKANNT.search(bereich))
                # Steht das HTML des Hinweises MASKIERT auf der Seite? Dann
                # liest der Anwender die spitzen Klammern. Fuenf Stellen in
                # drei Plugins standen am 25.08.2026 in einem xx_e(...) -
                # der Text erschien, und die Pruefung meldete gruen. Ein
                # Ergebnis, das nur "der Text ist da" misst, misst zu wenig.
                # Auch diese Pruefung im BEREICH, nicht auf der ganzen
                # Seite - sonst meldet sie fremde Abschnitte als
                # Gateway-Befund (Intercom 2.2.4, 31.08.2026).
                if re.search(r'&lt;(b|span|i)[ &]', bereich):
                    urteile.append('ROT (HTML maskiert)')
                    continue
                # Kommt ueberhaupt einer der drei Texte vor? Wenn keiner, hat
                # die Seite den Abschnitt gar nicht gezeigt - etwa weil das
                # Plugin seine Sprachdatei am INSTALLIERTEN Ort sucht, den
                # die Attrappe nicht hat (Midea2Lox). Das ist ein Strich,
                # kein Befund: hier ist nichts zu messen, und ein rotes Kreuz
                # an dieser Stelle wuerde beim naechsten Mal ueberlesen.
                if not (hat_v1 or hat_v2 or hat_un):
                    # KEIN blosser Strich mehr. Kennt das Werkzeug den
                    # Wortlaut nicht, misst es statt dessen das VERHALTEN:
                    # unterscheiden sich die Seite mit Fassung 1 und die mit
                    # Fassung 2 ueberhaupt?
                    a, b = seiten.get('v1'), seiten.get('v2')
                    if a is None or b is None:
                        urteile.append('--  (nicht gerendert)')
                    elif not hat_abo_abschnitt(t):
                        # Ohne Abo-Abschnitt ist "beide Seiten gleich" trivial
                        # wahr. Ein Plugin, das gar kein MQTT-Abo anbietet,
                        # darf hier nicht als defekt erscheinen.
                        urteile.append('--  (kein Abo-Abschnitt auf der Seite)')
                    elif a == b:
                        # Gleiche Seite bei verschiedener Fassung: das Plugin
                        # liest Mqtt.Gatewayversion nicht. Das ist ein Befund
                        # ohne jede Kenntnis des Wortlauts.
                        urteile.append('ROT (verzweigt nicht - Seite bei V1 '
                                       'und V2 zeichengleich)')
                    else:
                        # Es verzweigt, nur mit unbekannten Worten. Die
                        # Aufforderungspruefung greift trotzdem.
                        auf = aufforderungen(t) if erwartet == 'v2' else []
                        if auf:
                            urteile.append('ROT (Aufforderung bleibt: %s)'
                                           % '; '.join(auf[:2]))
                        else:
                            urteile.append('ok  (verzweigt, Wortlaut unbekannt)')
                    continue
                # Der UNBEKANNT-Text enthaelt den V1-Satz - er nennt ja beide
                # Faelle. Ohne "und nicht der Unbekannt-Text" sah ein Plugin,
                # das die Fassung gar nicht liest (immer 0 -> unbekannt), bei
                # gesetztem V1 richtig aus. Genau das ist am 25.08.2026
                # passiert und hat mehrere kaputte Umbauten gruen gemeldet.
                if erwartet == 'v1':
                    gut = hat_v1 and not hat_v2 and not hat_un
                elif erwartet == 'v2':
                    gut = hat_v2 and not hat_v1
                    # Der Satz allein genuegt nicht: steht rundherum weiter
                    # eine Aufforderung zum Eintragen, widerspricht sich die
                    # Seite - und der Anwender folgt eher der Ueberschrift
                    # als dem Fliesstext.
                    auf = aufforderungen(t)
                    if gut and auf:
                        urteile.append('ROT (Aufforderung bleibt: %s)'
                                       % '; '.join(auf[:2]))
                        continue
                else:
                    gut = hat_un or (hat_v1 and hat_v2)
                urteile.append(('ok' if gut else 'ROT') +
                               ' (V1:%d V2:%d U:%d)' % (hat_v1, hat_v2, hat_un))
            if any(u.startswith('ROT') for u in urteile):
                fehler += 1
            print('%-32s %-14s %-14s %s' % (e[16:47], *urteile))
    finally:
        schreiben_atomar(GEN, alt)
        if os.path.isfile(SICHER):
            os.remove(SICHER)

    print('-' * 82)
    print('%d Plugin(e), %d mit Befund' % (len(ordner), fehler))
    return 1 if fehler else 0


if __name__ == '__main__':
    sys.exit(main())
