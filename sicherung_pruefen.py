#!/usr/bin/env python3
"""Hat jedes Plugin die Sicherung der Einstellungen - und taugt sie?

Der Hausstandard verlangt sie seit dem 25.08.2026 in JEDEM Plugin (Muster:
WOLF ISM NG 3.0.8). Zweck ist der UMZUG auf einen zweiten LoxBerry, nicht
die Sicherung gegen Verlust - deshalb zwei Knoepfe und eine Datei, die der
Anwender in die Hand bekommt.

Geprueft wird, was sich am Quelltext messen laesst:

  1. ZWEI Formulare - Sichern schickt einen Download und ruft exit auf,
     Zurueckspielen braucht enctype="multipart/form-data". Wer beides in ein
     Formular legt, bekommt entweder keinen Upload oder einen Download, der
     das Speichern verschluckt.
  2. is_uploaded_file() - sonst laesst sich jede Datei des Servers
     unterschieben.
  3. eine Obergrenze fuer die Groesse.
  4. DER AKTIONSTOKEN IN DER DATEI. Enthaelt die Konfiguration einen Zugangs-
     oder Aktionstoken, muss er MITGESICHERT werden - ohne ihn stehen nach
     dem Zurueckspielen alle Felder richtig, und das Plugin kommt trotzdem
     nicht an die Anlage. Die Datei waere wertlos.

Was dieses Werkzeug NICHT kann: beurteilen, ob die Verarbeitung die sieben
Punkte aus REGELN_2 einhaelt. Es sagt, wo nachzusehen ist.

    python3 sicherung_pruefen.py [<Pluginordner> ...]

Rueckgabe 0, wenn kein Plugin etwas vermissen laesst.
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HIER = os.path.dirname(os.path.abspath(__file__))
ARBEIT = os.path.dirname(HIER)

# Woran ein Aktions- oder Zugangstoken zu erkennen ist. Bewusst breit: ein
# uebersehener Token ist teurer als eine Zeile, die man ansieht.
TOKEN = re.compile(r"'(\w*(?:token|apikey|api_key|secret|passwor|kennwort|"
                   r"schluessel|refresh|zugang|credential)\w*)'", re.I)
# Der FORMULARtoken - der gehoert NICHT in die Datei.
FORMTOKEN = re.compile(r'(?:fmt|formtoken|form_token|csrf)', re.I)


def dateien(o):
    for wurzel in ('webfrontend', 'bin'):
        for w, _, ds in os.walk(os.path.join(o, wurzel)):
            if os.sep + '.git' in w:
                continue
            for d in sorted(ds):
                if d.endswith('.php'):
                    yield os.path.join(w, d)


def pruefe(o):
    text = {}
    for p in dateien(o):
        try:
            text[p] = io.open(p, encoding='utf-8', errors='replace').read()
        except Exception:
            pass
    ganz = '\n'.join(text.values())

    hat_download = bool(re.search(r'Content-Disposition:\s*attachment', ganz, re.I))
    hat_upload = bool(re.search(r'enctype\s*=\s*["\']multipart/form-data', ganz, re.I))
    if not (hat_download or hat_upload):
        return ('fehlt', ['keine Sicherung gefunden'], [])

    maengel, hinweise = [], []
    if not hat_download:
        maengel.append('kein Download (Content-Disposition fehlt)')
    if not hat_upload:
        maengel.append('kein Upload (enctype multipart fehlt)')

    # --- Zwei GETRENNTE Formulare? ---
    for t in text.values():
        for m in re.finditer(r'<form\b[^>]*multipart[^>]*>', t, re.I):
            ende = t.find('</form>', m.end())
            block = t[m.end():ende if ende > 0 else m.end() + 800]
            sichern = re.search(r'name=["\']\w*(?:sichern|export|backup|_aus)\w*["\']',
                                block, re.I)
            laden = re.search(r'name=["\']\w*(?:laden|import|restore|_ein)\w*["\']',
                              block, re.I)
            if sichern and laden:
                maengel.append('Sichern und Zurueckspielen im SELBEN Formular')

    if 'is_uploaded_file' not in ganz:
        maengel.append('is_uploaded_file() fehlt')
    if not re.search(r"\['size'\]\s*>|MAX_FILE_SIZE|filesize\s*\(", ganz):
        hinweise.append('keine Obergrenze fuer die Dateigroesse erkennbar')

    # --- Der Aktionstoken: gibt es einen? Steckt er in der Sicherung? ---
    m = re.search(r'function\s+\w+_vorgaben\s*\(\).*?\n\}', ganz, re.S)
    vorgaben = m.group(0) if m else ''
    kandidaten = sorted(set(k for k in TOKEN.findall(vorgaben)
                            if not FORMTOKEN.search(k)))
    if kandidaten:
        m2 = re.search(r'function\s+\w+_(?:konfig_ausfuhr|sicherung\w*|export\w*|'
                       r'backup\w*|ausfuhr\w*)\s*\(.*?\n\}', ganz, re.S)
        ausfuhr = m2.group(0) if m2 else ''
        if ausfuhr:
            # Baut sie auf der GANZEN Konfiguration auf? Dann ist der Token drin.
            if not re.search(r'_vorgaben\(\)|_config\(\)|\$cfg\b|_konfig\(\)', ausfuhr):
                maengel.append('die Sicherung baut nicht auf der vollen Konfiguration auf')
            if FORMTOKEN.search(ausfuhr):
                maengel.append('der FORMULARtoken steht in der Sicherung')
        else:
            hinweise.append('Ausfuhrfunktion nicht eindeutig - von Hand ansehen')
        hinweise.append('Token: ' + ', '.join(kandidaten[:4]))
    return ('da', maengel, hinweise)


def main():
    ordner = [a for a in sys.argv[1:] if not a.startswith('--')]
    ausfuehrlich = '--alles' in sys.argv
    if not ordner:
        ordner = [e for e in sorted(os.listdir(ARBEIT))
                  if e.startswith('LoxBerry-Plugin-')
                  and os.path.isdir(os.path.join(ARBEIT, e))]
    print('%-32s %-7s %s' % ('Plugin', 'Stand', 'Befund'))
    print('-' * 92)
    fehlt, mangelhaft, gut = [], [], []
    for e in ordner:
        o = e if os.path.isdir(e) else os.path.join(ARBEIT, e)
        if not os.path.isdir(o):
            continue
        stand, maengel, hinweise = pruefe(o)
        name = os.path.basename(o)[16:]
        if stand == 'fehlt':
            fehlt.append(name)
            print('%-32s %-7s %s' % (name[:31], 'FEHLT', maengel[0]))
        elif maengel:
            mangelhaft.append(name)
            print('%-32s %-7s %s' % (name[:31], 'MANGEL', '; '.join(maengel)[:50]))
        else:
            gut.append(name)
            if ausfuehrlich:
                print('%-32s %-7s %s' % (name[:31], 'ok', '; '.join(hinweise)[:50]))
    print('-' * 92)
    print('%d Plugins: %d in Ordnung, %d mit Mangel, %d ohne Sicherung'
          % (len(gut) + len(mangelhaft) + len(fehlt), len(gut), len(mangelhaft), len(fehlt)))
    if fehlt:
        print('\nOhne Sicherung: %s' % ', '.join(fehlt))
    return 1 if (fehlt or mangelhaft) else 0


if __name__ == '__main__':
    sys.exit(main())
