#!/usr/bin/env python3
"""Gezielte Probe fuer den MQTT-Umbau.

Drei Fragen, die der allgemeine Wirkungstest nicht beantwortet:

  1. Speichert das MQTT-Formular ueberhaupt? (Thema aendern -> steht es drin?)
  2. Ueberlebt das geaenderte Thema ein Speichern der EINSTELLUNGEN?
  3. Ueberleben die Einstellungen ein Speichern des MQTT-Formulars?

Frage 2 ist die eigentliche: genau dort nullt ein Sammel-Handler per isset().

BERICHTIGT 23.08.2026 - zwei blinde Flecken in cfg_wert(), beide gemessen:

  1. Es verstand nur JSON. Eine Linie mit INI-Konfiguration (Config::Lite,
     so liest sie auch ein Python-Dienst) wurde nie gelesen; das Werkzeug
     meldete "MQTT-Formular speichert nicht" und meinte "ich kann die Datei
     nicht lesen". Ein Kreuz, das etwas anderes bedeutet als es sagt.

  2. Schwerer: es nahm den ERSTEN Treffer ueber ALLE Plugins des
     gemeinsamen Pruefstands. Gezaehlt ueber die 147 Konfigurationsdateien
     dort: 80 tragen mqtt_topic, 63 tragen mqtt_ein, 20 tragen
     mqtt_enabled. Fuer jede Linie ausser der zufaellig zuerst gelesenen
     wurde damit ein FREMDER Wert gemessen - und das Werkzeug hat es weder
     gemerkt noch gesagt.

Die eigene Datei wird jetzt nicht geraten, sondern GEMESSEN: es ist die,
die sich beim Speichern veraendert. Dieselbe Ueberlegung, die
konfig_abbild() schon fuer den Vergleich benutzt - und sie trifft auch die
Linien, deren Ordner anders heisst als die Linie (Heimkino -> heimkino,
Intercom -> htmlauth).

Veraendert das Formular GAR KEINE Datei, ist das die Antwort auf Frage 1
und kein Grund, anderswo weiterzusuchen.
"""
import json, sys
from pathlib import Path

import wirkungstest as W


def formulare(datei, plugin):
    html, _ = W.lauf(datei, plugin)
    p = W.Formulare()
    p.feed(html)
    aus = []
    for form in p.formulare:
        post = {}
        for name, wert in form['felder']:
            if name.endswith('[]'):
                post.setdefault(name[:-2], []).append(wert)
            else:
                post[name] = wert
        if form['marker']:
            post[form['marker'][0][0]] = form['marker'][0][1]
        if post and not any(W.AKTIONSFELD.match(k) for k in post):
            aus.append(post)
    return aus


def _werte(inhalt):
    """Schluessel und Werte einer Konfigurationsdatei - JSON ODER INI.

    JSON wie bisher: nur die oberste Ebene eines Objekts. INI dazu, im
    Format von Config::Lite - Abschnittskoepfe und Bemerkungen fallen weg,
    Anfuehrungszeichen um den Wert ebenfalls.
    """
    try:
        d = json.loads(inhalt)
        return d if isinstance(d, dict) else {}
    except ValueError:
        pass
    aus = {}
    for zeile in inhalt.splitlines():
        z = zeile.strip()
        if z == '' or z[0] in ';#[':
            continue
        if '=' not in z:
            continue
        k, v = z.split('=', 1)
        aus[k.strip()] = v.strip().strip('"').strip("'")
    return aus


def cfg_wert(plugin, schluessel, eigene=None):
    """Einen Wert aus der Konfiguration des Plugins lesen.

    'eigene' ist die Menge der Pfade, die dem Plugin nachweislich gehoeren -
    gemessen daran, dass es sie beim Speichern veraendert hat. Ohne diese
    Einschraenkung wuerde ueber ALLE Plugins des gemeinsamen Pruefstands
    gesucht, und 80 von 147 Dateien tragen mqtt_topic.

    Ist die Menge nicht bekannt, wird NICHT ersatzweise ueberall gesucht:
    ein fremder Wert ist schlimmer als kein Wert.
    """
    abbild = W.konfig_abbild(plugin)
    if eigene is None:
        return None
    for pfad in sorted(eigene):
        werte = _werte(abbild.get(pfad, ''))
        if schluessel in werte:
            return werte[schluessel]
    return None


def eigene_dateien(plugin, vorher, nachher):
    """Welche Dateien hat das Plugin veraendert oder angelegt?"""
    return set(p for p in nachher if nachher[p] != vorher.get(p))


def probe(plugin, verzeichnis='stand', topic_feld='mqtt_topic', ein_feld='mqtt_ein'):
    datei = Path(verzeichnis) / plugin / 'webfrontend/htmlauth/index.php'
    if not datei.is_file():
        return ['keine htmlauth/index.php']
    W.lauf(datei, plugin)
    W.lauf(datei, plugin)
    for f in formulare(datei, plugin):
        W.lauf(datei, plugin, f)

    fs = formulare(datei, plugin)
    mqttform = [f for f in fs if topic_feld in f or ein_feld in f]
    einstform = [f for f in fs if topic_feld not in f and ein_feld not in f
                 and any(k.startswith('speichern') or k.startswith('save') for k in f)]
    befunde = []
    if not mqttform:
        return ['kein Formular mit %s gefunden' % topic_feld]
    mq = dict(mqttform[0])
    if len(mqttform) > 1:
        befunde.append('MQTT-Felder stehen in %d Formularen - Dublette?' % len(mqttform))

    # 1) MQTT-Formular speichert?
    #
    # Dabei wird zugleich gemessen, WELCHE Dateien dem Plugin gehoeren:
    # die, die sich durch dieses Speichern veraendern. Ohne das suchte
    # cfg_wert() ueber alle Plugins des Pruefstands.
    mq[topic_feld] = 'probethema'
    mq[ein_feld] = '1'
    vor_eins = W.konfig_abbild(plugin)
    W.lauf(datei, plugin, mq)
    eigene = eigene_dateien(plugin, vor_eins, W.konfig_abbild(plugin))
    if not eigene:
        befunde.append('MQTT-Formular hat keine Datei veraendert - es speichert nicht.')
        return befunde
    ist = cfg_wert(plugin, topic_feld, eigene)
    if ist != 'probethema':
        befunde.append('MQTT-Formular speichert nicht: %s = %r (gemessen in %s)'
                       % (topic_feld, ist,
                          ', '.join(sorted(Path(p).name for p in eigene))))
        return befunde

    # 2) ueberlebt es das Speichern der Einstellungen?
    if not einstform:
        befunde.append('kein Einstellungsformular gefunden - Frage 2 offen')
    else:
        vorher_ein = cfg_wert(plugin, ein_feld, eigene)
        W.lauf(datei, plugin, einstform[0])
        n_topic = cfg_wert(plugin, topic_feld, eigene)
        n_ein = cfg_wert(plugin, ein_feld, eigene)
        if n_topic != 'probethema':
            befunde.append('Einstellungen-Speichern hat %s zerstoert: %r' % (topic_feld, n_topic))
        if str(n_ein) != str(vorher_ein):
            befunde.append('Einstellungen-Speichern hat %s veraendert: %r -> %r'
                           % (ein_feld, vorher_ein, n_ein))

    # 3) ueberleben die Einstellungen das MQTT-Speichern?
    vorher = W.konfig_abbild(plugin)
    W.lauf(datei, plugin, mqttform[0])
    for u in W.vergleiche(vorher, W.konfig_abbild(plugin)):
        if topic_feld in u or ein_feld in u:
            continue
        befunde.append('MQTT-Speichern hat etwas anderes veraendert: ' + u)
    return befunde


if __name__ == '__main__':
    verz = 'stand'
    namen = [a for a in sys.argv[1:] if not a.startswith('--')]
    schlecht = 0
    for n in namen:
        felder = ('mqtt_topic', 'mqtt_ein')
        if n in ('ACTiKamera', 'Octopus'):
            felder = ('mqtt_topic', 'mqtt_enabled')
        b = probe(n, verz, felder[0], felder[1])
        if b:
            schlecht += 1
            print('== ' + n)
            for x in b:
                print('   ' + x)
        else:
            print('%-22s ok  (MQTT speichert, ueberlebt Einstellungen, stoert nichts)' % n)
    print('\n%d von %d mit Befund.' % (schlecht, len(namen)))
