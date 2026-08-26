#!/usr/bin/env python3
"""Stellt das plugin-eigene CSS-Kuerzel auf den Hausstandard sm- um.

Ersetzt wird der Token <kuerzel>- ueberall dort, wo davor KEIN Bezeichnerzeichen
steht. Damit sind erfasst: .hk-x  "hk-x"  'hk-x'  a.hk-x  .sm-tab.hk-x  >hk-x
Nicht erfasst und damit sicher: PHP-Funktionen hk_paths(), Dateiname hk_lib.php
(dort steht ein Unterstrich).
"""
import re, sys, shutil
from pathlib import Path

def kuerzel_finden(dateien):
    z = {}
    for _, t in dateien:
        for k in re.findall(r'class="([a-z]{2,4})-[a-z0-9-]+"', t): z[k] = z.get(k,0)+1
        for k in re.findall(r'\.([a-z]{2,4})-[a-z0-9-]+\s*[{,:]', t): z[k] = z.get(k,0)+1
    z.pop('ui', None); z.pop('sm', None)
    return (max(z, key=z.get) if z else None), z

def main(ordner, schreiben=False):
    p = Path(ordner)
    ziele = [f for f in p.rglob('*') if f.is_file()
             and f.suffix.lower() in ('.php','.html','.css','.js','.cgi')]
    dateien = []
    for f in ziele:
        try: dateien.append((f, f.read_text(encoding='utf-8')))
        except Exception: pass
    k, alle = kuerzel_finden(dateien)
    if not k:
        print(f"  {p.name}: kein eigenes Kuerzel ({alle})"); return 0
    print(f"  Kuerzel '{k}-'  Vorkommen: {alle}")
    muster = re.compile(r'(?<![A-Za-z0-9_])' + k + r'-(?=[a-z0-9])')
    gesamt = 0
    for f, t in dateien:
        neu, n = muster.subn('sm-', t)
        if n:
            gesamt += n
            if schreiben:
                shutil.copy2(f, str(f) + '.vor-sm')
                f.write_text(neu, encoding='utf-8')
            print(f"    {f.relative_to(p)}: {n}")
        rest = re.findall(r'(?<![A-Za-z0-9_])' + k + r'-[a-z0-9-]+', neu)
        if rest: print(f"    !! Rest in {f.relative_to(p)}: {sorted(set(rest))}")
    print(f"  Summe: {gesamt}")
    return gesamt

if __name__ == '__main__':
    main(sys.argv[1], '--schreiben' in sys.argv)
