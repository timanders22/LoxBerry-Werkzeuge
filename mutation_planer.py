#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deckt der Selbsttest des Fahrplaners wirklich, was er behauptet?

EINE ZAHL IST KEINE DECKUNG.

planer.php meldete am Stand 1.0.0 "53 Faelle geprueft, 0 Fehlschlaege" -
und der Kommentar daneben sprach von dreissig. Beides beruhigt, keines
sagt etwas darueber, ob die Faelle die Rechnung ueberhaupt anfassen.

Dieses Werkzeug baut je eine absichtliche VERFAELSCHUNG in eine Kopie der
Datei ein und laesst den Selbsttest darauf laufen. Bleibt er gruen, hat
die Mutation UEBERLEBT - dann prueft kein Fall diese Stelle.

Was es an planer.php gefunden hat, in zwei Runden:

    1.0.0    28 Mutationen, 11 ueberlebt.  Ungeprueft waren unter anderem
             die Regelarten 'stunden' und 'mittel', jedes Zeitfenster, der
             Vergangenheitsfilter und die beiden Sommerzeit-Umstellungstage
             - genau dort sass ein Fehler, der ein Jahr lang mitlief.

    1.1.0    nach 48 neuen Faellen erneut gemessen: 18 Mutationen,
             5 ueberlebt - und alle fuenf sassen auf einem "genau gleich".
             Gleichstaende entstehen beim Pruefen nie von selbst; wer eine
             Reihe hinschreibt, waehlt unwillkuerlich Zahlen, die sich
             unterscheiden. Man muss sie bauen.

    danach   18 von 18 erkannt.

WAS ES NICHT KANN

Es misst, ob eine Stelle ANGEFASST wird - nicht, ob sie richtig ist. Eine
Mutation, die niemand erkennt, ist ein sicherer Befund; eine, die alle
erkennen, ist noch kein Freispruch fuer die Rechnung dahinter.

Und es misst nur die achtzehn Stellen, die unten stehen. Wer die Rechnung
erweitert, traegt seine Mutation hier ein - sonst waechst die Datei und
die Deckung nicht mit.

    python mutation_planer.py [<Pfad zu planer.php>]

Ohne Argument wird die Datei im neuesten Spotpreis-Octopus-Ordner genommen.
Rueckgabe 1, wenn eine Mutation ueberlebt.
"""

import io
import os
import shutil
import subprocess
import sys
import tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
ARBEIT = os.path.dirname(HIER)


def neueste_quelle():
    """Die planer.php im neuesten Spotpreis-Octopus-Ordner."""
    kand = sorted(e for e in os.listdir(ARBEIT)
                  if e.startswith('LoxBerry-Plugin-Spotpreis-Octopus-')
                  and os.path.isdir(os.path.join(ARBEIT, e)))
    for e in reversed(kand):
        p = os.path.join(ARBEIT, e, 'webfrontend', 'html', 'planer.php')
        if os.path.isfile(p):
            return p
    return None


QUELLE = sys.argv[1] if len(sys.argv) > 1 else neueste_quelle()
if not QUELLE or not os.path.isfile(QUELLE):
    print('planer.php nicht gefunden - Pfad als Argument angeben.')
    sys.exit(2)
print('Gemessen wird: %s' % QUELLE)
PHPS = [('7.4', r'C:\tmp\php-7.4.33-Win32-vc15-x64\php.exe'),
        ('8.4', r'C:\tmp\php-8.4.27-Win32-vs17-x64\php.exe')]

# (Name, Suchtext, Ersatztext).  Der Suchtext muss GENAU EINMAL vorkommen -
# sonst trifft die Mutation etwas anderes als gemeint, und das Ergebnis
# waere wertlos.
MUTATIONEN = [
 # --- die elf, die am Stand 1.0.0 ueberlebt haben ---
 ('Vergangenheitsfilter entfernt',
  "if ($ts < $jetzt || $ts >= $ende) { continue; }",
  "if ($ts >= $ende) { continue; }"),
 ('Zeitfenster ignoriert',
  "if (!plan_in_zeitfenster($stunde, $von, $bis)) { continue; }",
  "if (false) { continue; }"),
 ('Budgetgrenze > wird >=',
  "if ($budget > 0 && plan_runde($schon + $leistung, 4) > plan_runde($budget, 4)) { continue; }",
  "if ($budget > 0 && plan_runde($schon + $leistung, 4) >= plan_runde($budget, 4)) { continue; }"),
 ('Lueckenpruefung entfernt',
  "if ($ks[$i + $len - 1] - $ks[$i] !== ($len - 1) * $slotlen) { continue; }",
  "if (false) { continue; }"),
 ('angebrochene Stunden zaehlen mit',
  # Seit Planerfassung 1.1.2 wird gerundet - sonst greift der
  # Zweitschluessel bei gleichem Stundenmittel nie.
  "if ($v[1] === $pro) { $mittelwerte[$h] = plan_runde($v[0] / $pro, 6); }",
  "$mittelwerte[$h] = $v[0] / max(1, $v[1]);"),
 ('Schwelle <= wird <',
  "if ($ct <= $grenze) { $treffer[] = $ts; }",
  "if ($ct < $grenze) { $treffer[] = $ts; }"),
 ('pv_sperre >= wird >',
  "&& (float) $umwelt['pv_summe'] >= $pvs) {",
  "&& (float) $umwelt['pv_summe'] > $pvs) {"),
 ('soc_min < wird <=',
  "if ($min > 0 && (float) $soc < $min) { return 'soc_min'; }",
  "if ($min > 0 && (float) $soc <= $min) { return 'soc_min'; }"),
 ('Rang-Gleichstand nicht mehr stabil',
  "return $a['i'] < $b['i'] ? -1 : ($a['i'] > $b['i'] ? 1 : 0);",
  "return 0;"),
 ('ct aus Effektivpreis statt Boersenpreis',
  "foreach ($treffer as $ts) { $summe += isset($preise[$ts]) ? (float) $preise[$ts] : 0.0; }",
  "foreach ($treffer as $ts) { $summe += isset($eff[$ts]) ? (float) $eff[$ts] : 0.0; }"),
 ('Belegung ohne Summierung',
  "$out[$ts] = plan_runde($out[$ts] + (float) $e['leistung'], 4);",
  "$out[$ts] = plan_runde((float) $e['leistung'], 4);"),
 # --- sieben fuer das, was 1.1.0 neu koennen soll ---
 ('Frist rechnet wieder mit + Stunde * 3600',
  "$ziel = (int) strtotime(sprintf('%s %02d:00:00', $tag, $frist));",
  "$ziel = (int) strtotime($tag . ' 00:00:00') + $frist * 3600;"),
 ('Einheit nicht mehr klein geschrieben',
  "$einheit = strtolower(trim((string) $einheit));",
  "$einheit = (string) $einheit;"),
 ('mittel wieder als Faktor statt Betrag',
  "$grenze = plan_runde($m - abs($m) * $prozent / 100, 3);",
  "$grenze = plan_runde($m * (1 - $prozent / 100), 3);"),
 ('Negativpreis fuellt slots nicht mehr',
  "                if (!in_array($jetzt, $e['slots'], true)) {",
  "                if (false) {"),
 ('Taktschutz abgeschaltet',
  "        $treffer = plan_takt($treffer, $mit, $slotlen,",
  "        $treffer = $treffer ?: plan_takt($treffer, $mit, $slotlen,"),
 ('Hysterese haelt nichts mehr fest',
  "        if ($bis > $jetzt) {",
  "        if (false) {"),
 ('zweites Budget wirkungslos',
  "            if ($b2kw > 0 && plan_in_zeitfenster($stunde, $b2von, $b2bis)",
  "            if (false && plan_in_zeitfenster($stunde, $b2von, $b2bis)"),

 # --- Rangfolge, nachgetragen am 27.08.2026 ---
 #
 # WARUM SIE GEFEHLT HABEN: plan_rang_vergleich() und plan_reihenfolge()
 # sind mit der 89 564-Byte-Fassung dazugekommen, die Mutationsliste nicht.
 # Nachgemessen: alle achtzehn Anker von damals standen schon in der
 # veroeffentlichten 1.2.13 - der Lauf meldete "18 von 18 erkannt" und
 # ruehrte den neuen Code mit keiner einzigen Mutation an. Eine Liste, die
 # nicht mitwaechst, wird mit jeder Erweiterung beruhigender und
 # aussageaermer.
 ('Rangfolge: Gleichstand nicht mehr nach Nummer aufgeloest',
  "    return $a['i'] < $b['i'] ? -1 : ($a['i'] > $b['i'] ? 1 : 0);",
  "    return 0;"),
 ('Rangfolge: kleinerer Rang verliert statt zu gewinnen',
  "    if ($a['rang'] !== $b['rang']) { return $a['rang'] < $b['rang'] ? -1 : 1; }",
  "    if ($a['rang'] !== $b['rang']) { return $a['rang'] > $b['rang'] ? -1 : 1; }"),
 ('Rangfolge gar nicht sortieren',
  "    usort($reihe, 'plan_rang_vergleich');",
  "    /* usort entfernt */"),

 # --- die Luecken der Deckungsmessung vom 27.08.2026 ---
 #
 # Gefunden nicht durch Nachdenken, sondern durch zwei Messungen: welche
 # Rueckgabefelder der Selbsttest nie prueft (rest und startmin von
 # achtzehn), und welche Bedingung sich auf true oder false zwingen laesst,
 # ohne dass ein Fall rot wird (45 von 176). Die achtzehn neuen Faelle im
 # Selbsttest schliessen sie; diese fuenf Mutationen halten sie zu.
 ('rest wird nicht mehr gerechnet',
  "            if ($e['aktiv']) {\n                $rest = 0;",
  "            if (false) {\n                $rest = 0;"),
 ('startmin wird nicht mehr gesetzt',
  "                    $e['startmin'] = (int) date('i', $ts);",
  "                    $e['startmin'] = 0;"),
 ('grund wartet faellt weg',
  "            $e['grund'] = $e['aktiv'] ? $art : 'wartet';",
  "            $e['grund'] = $art;"),
 ('Einheit w wird wie wh behandelt',
  "    if ($einheit === 'w')  { return $w * $std; }",
  "    /* Einheit w entfernt */"),
 # --- sechs fuer die Befunde der Planerfassung 1.1.3 ---
 #
 # Die ersten beiden sind FASSUNGSABHAENGIG: unter 7.4 antwortet die alte
 # Rechnung genauso wie die neue, der Selbsttest bleibt dort also zu Recht
 # gruen. Deshalb tragen sie die vierte Spalte.
 ('Rundung wieder ueber die eingebaute Funktion',
  """function plan_runde($x, $stellen = 0)
{
    $x = (float) $x;""",
  """function plan_runde($x, $stellen = 0)
{
    return round($x, (int) $stellen);
    $x = (float) $x;""", ('8.4',)),
 ('Frist wieder ueber die Zeitfunktion',
  "    $ziel = (int) strtotime(sprintf('%s %02d:00:00', $tag, $frist));",
  "    $ziel = (int) mktime($frist, 0, 0, (int) date('n', $jetzt),"
  " (int) date('j', $jetzt), (int) date('Y', $jetzt));", ('8.4',)),
 # Die uebrigen vier wirken in jeder Fassung.
 ('Runden trifft die Haelfte nicht mehr',
  "    if ($z[$k] >= '5') {",
  "    if ($z[$k] > '5') {"),
 ('Frist kennt kein Morgen mehr',
  "        $ziel = (int) strtotime(sprintf('%s %02d:00:00 +1 day', $tag, $frist));",
  "        $ziel = (int) strtotime(sprintf('%s %02d:00:00', $tag, $frist));"),
 ('Luecken werden nur einmal zugemacht',
  """        $treffer = plan_luecken_zu($treffer, $kand, $slotlen, $min_pause);
    }

    return $treffer;""",
  """    }

    return $treffer;"""),
 ('Fenstermittel wieder ungerundet',
  """            $m = plan_runde($s / $len, 6);
            if ($best === null || $m < $best[1]) { $best = array($i, $m); }""",
  """            $m = $s / $len;
            if ($best === null || $m < $best[1]) { $best = array($i, $m); }"""),
 ('Kennzahlen nach dem Negativpreis nicht neu',
  """                $e = plan_kennzahlen($e, $r, $preise, $jetzt, $slotlen, $noetig);
                $e['grund'] = 'negativ';""",
  """                $e['grund'] = 'negativ';"""),
 ('Hysterese nimmt wieder jeden Preis',
  "                if (isset($mit[$ts])) { $vorhanden[$ts] = 1; }",
  "                if (isset($preise[$ts])) { $vorhanden[$ts] = 1; }"),
 ('plan_pfad gibt bei fehlendem Schritt den Rest zurueck',
  "        if (!is_array($daten) || !isset($daten[$teil])) { return null; }",
  "        if (!is_array($daten)) { return null; }\n"
  "        if (!isset($daten[$teil])) { return $daten; }"),
]

roh = io.open(QUELLE, encoding='utf-8', newline='').read()
arbeit = tempfile.mkdtemp(prefix='mutation_')
treiber = os.path.join(arbeit, 'treiber.php')
io.open(treiber, 'w', encoding='utf-8').write(
    "<?php date_default_timezone_set('Europe/Berlin');\n"
    "require_once getenv('PLANER');\n"
    "list($n, $f, $t) = plan_selbsttest();\n"
    "echo $n . '|' . $f;\n")


def selbsttest(pfad, php):
    umg = dict(os.environ, PLANER=pfad)
    r = subprocess.run([php, '-n', '-d', 'date.timezone=Europe/Berlin',
                        '-d', 'display_errors=0', treiber],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', env=umg, timeout=180)
    aus = (r.stdout or '').strip()
    if '|' not in aus:
        return None, None
    a, b = aus.split('|', 1)
    return int(a), int(b)


print('Grundlage: der unveraenderte Stand')
for v, php in PHPS:
    if not os.path.isfile(php):
        continue
    n, f = selbsttest(QUELLE, php)
    print('  PHP %s: %s Faelle, %s Fehlschlaege' % (v, n, f))
    if f != 0:
        print('  ABBRUCH: der Selbsttest ist schon ohne Mutation nicht gruen.')
        sys.exit(2)

print()
print('%-42s %-9s %s' % ('Mutation', 'Treffer', 'Urteil'))
print('-' * 74)
ueberlebt = []
for eintrag in MUTATIONEN:
    # Vierter Eintrag optional: welche PHP-Fassungen die Mutation erkennen
    # MUESSEN. Fehlt er, gilt wie bisher: alle.
    if len(eintrag) == 4:
        name, alt, neu, noetig = eintrag
    else:
        name, alt, neu = eintrag
        noetig = None
    anzahl = roh.count(alt)
    if anzahl != 1:
        print('%-42s %-9s WERKZEUGFEHLER: Suchtext kommt %dx vor'
              % (name[:42], '-', anzahl))
        ueberlebt.append(name + ' (nicht einbaubar)')
        continue
    ziel = os.path.join(arbeit, 'planer.php')
    io.open(ziel, 'w', encoding='utf-8', newline='').write(roh.replace(alt, neu))
    urteile = []
    for v, php in PHPS:
        if not os.path.isfile(php):
            continue
        n, f = selbsttest(ziel, php)
        if n is None:
            urteile.append('%s:Absturz' % v)      # zaehlt als erkannt
        else:
            urteile.append('%s:%d' % (v, f))
    zaehlt = [u for u in urteile
              if noetig is None or u.split(':')[0] in noetig]
    erkannt = bool(zaehlt) and all(
        u.endswith('Absturz') or int(u.split(':')[1]) > 0 for u in zaehlt)
    print('%-42s %-9s %s%s' % (name[:42], ' '.join(urteile),
                               'erkannt' if erkannt else 'UEBERLEBT',
                               '' if noetig is None else '  (nur ' + ','.join(noetig) + ')'))
    if not erkannt:
        ueberlebt.append(name)

print('-' * 74)
print('%d Mutationen, %d erkannt, %d ueberlebt.'
      % (len(MUTATIONEN), len(MUTATIONEN) - len(ueberlebt), len(ueberlebt)))
for u in ueberlebt:
    print('  UEBERLEBT: ' + u)
shutil.rmtree(arbeit, ignore_errors=True)
sys.exit(1 if ueberlebt else 0)
