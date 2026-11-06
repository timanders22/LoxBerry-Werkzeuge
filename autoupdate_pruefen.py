#!/usr/bin/env python3
"""Steht das Auto-Update an - und darf es?

Anlass, 28.08.2026: die LoxBerry-Pluginverwaltung meldete fuer
Beschattungswaechter 0.9.9 "No AutoUpdate". Der Grund stand seit dem ersten
Tag in der plugin.cfg:

    # Bewusst AUS, solange es das Repository noch nicht gibt.
    AUTOMATIC_UPDATES=false

Das war richtig - am 23./25.08., als es die Repositorien noch nicht gab.
Danach hat es niemand zurueckgedreht, weil nichts danach gefragt hat. Eine
Bedingung, die niemand nachprueft, bleibt fuer immer wahr.

DAS WERKZEUG PRUEFT VIER DINGE JE LINIE

  1. Steht AUTOMATIC_UPDATES auf true?
  2. Zeigen RELEASECFG und PRERELEASECFG auf das EIGENE Repositorium?
     Ein fremdes waere schlimmer als keines: LoxBerry vergleicht Fassungen
     als Zahl, und ein fremdes 2021.05.14 ist groesser als 0.9.0 - daraus
     wuerde ein stilles Downgrade auf ein voellig anderes Plugin.
  3. ABRUF: antworten BEIDE Adressen mit HTTP 200? Das ist die Wirkung -
     genau diesen Abruf macht pluginsupdate.pl. (Nur mit --fern.)
  4. Gibt es den Zweig, auf den die Adressen zeigen? (Nur mit --fern.)
     Das ist eine NEBENAUSKUNFT, kein Urteil - siehe unten.

Es aendert nichts.

Aufruf:  autoupdate_pruefen.py [--fern] [ORDNER ...]

GEAENDERT 08.09.2026 - zwei Maengel, beide bei Pumpenwacht 1.0.0 aufgefallen

(a) Es mass den ZWEIG, nicht den ABRUF. Pumpenwachts Adressen nannten seit
    dem ersten Tag ".../master/release.cfg", das Repositorium fuehrt aber nur
    "main" - das Werkzeug meldete FEHLT. Gemessen wurde daraufhin die
    Wirkung: die master-Adresse antwortet HTTP 200. GitHub leitet den alten
    Zweignamen nach einer Umbenennung weiter. Gegenprobe in beide Richtungen:
    ein erfundener Zweigname antwortet 404, und Bewaesserung/main (dort heisst
    der Zweig master, ohne Umbenennung) ebenfalls 404 - es gibt also keinen
    stillen Rueckfall auf den Vorgabezweig, die 200 ist echt.
    Das Werkzeug haette "kaputt" gesagt, wo nichts kaputt war. Deshalb
    entscheidet jetzt der Abruf; der Zweig steht daneben und heisst, wenn er
    fehlt und der Abruf trotzdem 200 gibt, "umgeleitet".

(b) Die Schlusszeile sagte "0 Linie(n) ohne Auto-Update, 0 mit fragwuerdigen
    Adressen" - waehrend eine Zeile darueber FEHLT stand. Der Rueckgabewert
    war 0. Eine Zusammenfassung darf nicht besser aussehen als ihr
    schlechtester Punkt (CLAUDE.md, Abschnitt 6). Jetzt wird jeder Ausgang
    gezaehlt und im Rueckgabewert getragen.

DREI AUSGAENGE, NICHT ZWEI

"Geprueft und in Ordnung" und "konnte nicht pruefen" sind verschieden. Ein
Abruf, der weder 200 noch 404 ergibt (Proxy, kein Netz, Zeitueberschreitung),
zaehlt als NICHT GEMESSEN und faerbt die Schlusszeile - nicht als gruen und
nicht als Befund.

  Rueckgabewert 0  alles geprueft, nichts zu beanstanden
                1  mindestens ein Befund
                2  kein Befund, aber etwas liess sich nicht messen
"""
import glob, os, re, subprocess, sys, urllib.error, urllib.request

fern = '--fern' in sys.argv
argv = [a for a in sys.argv[1:] if a != '--fern']


def aktuelle():
    st = {}
    for d in sorted(glob.glob('LoxBerry-Plugin-*')):
        if not os.path.isdir(d):
            continue
        m = re.match(r'(LoxBerry-Plugin-.+?)-(\d[\d.]*)$', d)
        if not m:
            continue
        k = tuple(int(x) for x in m.group(2).split('.'))
        if m.group(1) not in st or k > st[m.group(1)][0]:
            st[m.group(1)] = (k, d)
    return [v[1] for v in st.values()]


def abrufen(adresse):
    """Was antwortet die Adresse? Rueckgabe: 200, 404, oder None = nicht messbar.

    Gemessen wird der Abruf, den pluginsupdate.pl macht - nicht die Erreich-
    barkeit des Servers. Jede Antwort ausser 200 und 404 ist hier NICHT
    messbar: ein Proxy, der alles mit 403 beantwortet, ist kein Befund am
    Plugin.
    """
    bitte = urllib.request.Request(adresse, method='GET',
                                   headers={'User-Agent': 'autoupdate_pruefen'})
    try:
        with urllib.request.urlopen(bitte, timeout=20) as a:
            return a.status
    except urllib.error.HTTPError as f:
        return f.code if f.code == 404 else None
    except Exception:
        return None


kopf = '%-42s %-6s %-8s %-9s %s'
print(kopf % ('Plugin', 'Auto', 'Adressen', 'Abruf', 'Zweig'))
print('-' * 84)
n_aus = n_fremd = n_abruf = n_unklar = n_umgeleitet = n_linien = 0
for d in sorted(argv or aktuelle()):
    p = os.path.join(d, 'plugin.cfg')
    if not os.path.isfile(p):
        continue
    n_linien += 1
    t = open(p, encoding='utf-8', errors='replace').read().replace('\r\n', '\n')
    t = '\n'.join(z for z in t.split('\n') if not z.lstrip().startswith('#'))
    auto = (re.search(r'^AUTOMATIC_UPDATES=(\w+)', t, re.M) or [None, '?'])[1]
    eigen = re.sub(r'-\d[\d.]*$', '', os.path.basename(d))
    adr = re.findall(r'^(?:PRE)?RELEASECFG=(\S+)', t, re.M)
    passend = all(('/timanders22/%s/' % eigen) in a for a in adr) and len(adr) == 2
    zweig = abruf = '-'
    if fern and adr:
        # Punkt 3: der Abruf. BEIDE Adressen, nicht nur die erste - die
        # prerelease.cfg wird von pluginsupdate.pl genauso geholt, und sie
        # kann einzeln fehlen.
        st = [abrufen(a) for a in adr]
        if all(s == 200 for s in st):
            abruf = '200'
        elif None in st:
            abruf = '?'
            n_unklar += 1
        else:
            abruf = '/'.join('?' if s is None else str(s) for s in st)
            n_abruf += 1
        # Punkt 4: der Zweig - Nebenauskunft, siehe Kopf dieser Datei.
        m = re.search(r'/timanders22/([^/]+)/([^/]+)/', adr[0])
        if m:
            r = subprocess.run(['git', 'ls-remote',
                                'https://github.com/timanders22/%s.git' % m.group(1),
                                m.group(2)], capture_output=True, text=True)
            if r.stdout.strip():
                zweig = 'da'
            else:
                # Eine leere Antwort heisst zweierlei: den ZWEIG gibt es
                # nicht, oder das REPOSITORIUM gibt es nicht. Das bei der
                # Eichung am 08.09.2026 aufgefallen - der Fall "fremde
                # Adresse" bekam "umgeleitet" angeschrieben, obwohl dort gar
                # kein Repositorium steht. Deshalb eine zweite, nur hier
                # noetige Frage.
                r2 = subprocess.run(
                    ['git', 'ls-remote', '--symref',
                     'https://github.com/timanders22/%s.git' % m.group(1),
                     'HEAD'], capture_output=True, text=True)
                if not r2.stdout.strip():
                    zweig = 'Repo?'
                elif abruf == '200':
                    zweig = 'umgeleitet'
                    n_umgeleitet += 1
                else:
                    zweig = 'fehlt'
    if auto != 'true':
        n_aus += 1
    if not passend:
        n_fremd += 1
    print(kopf % (os.path.basename(d)[16:58], auto,
                  'eigen' if passend else 'PRUEFEN', abruf, zweig))
print('-' * 84)
print('%d Linie(n) geprueft: %d ohne Auto-Update, %d mit fragwuerdigen Adressen, '
      '%d mit fehlgehendem Abruf.' % (n_linien, n_aus, n_fremd, n_abruf))
if n_unklar:
    print('%d Linie(n) NICHT GEMESSEN - der Abruf kam weder mit 200 noch mit 404 '
          'zurueck (Proxy, kein Netz). Das ist kein gruenes Ergebnis.' % n_unklar)
if n_umgeleitet:
    print('%d Linie(n) antworten mit 200, obwohl es den genannten Zweig nicht '
          'gibt: GitHub leitet einen umbenannten Zweignamen weiter. Es wirkt, '
          'haengt aber an der Weiterleitung statt am Zweig.' % n_umgeleitet)
if not fern:
    print('Abruf und Zweig NICHT geprueft - dafuer --fern angeben.')
if n_aus:
    print('Ein "false" ist nur so lange richtig, wie seine Bedingung gilt.')
sys.exit(1 if (n_aus or n_fremd or n_abruf) else (2 if n_unklar else 0))
