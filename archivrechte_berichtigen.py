#!/usr/bin/env python3
"""Einem fertigen Archiv die Rechte gerade ziehen - ohne den Inhalt anzufassen.

Anlass, 28.08.2026: bis zu dieser Berichtigung legte packen.py jeden Eintrag
als blankes zipfile.ZipInfo an. writestr() stempelt darauf 0o600 - fuer
Dateien UND fuer Verzeichnisse. Ein Verzeichnis ohne x-Bit laesst sich nicht
betreten, und plugininstall.pl kopiert nicht als root, sondern

    sudo -n -u loxberry cp -r -v ...

Ergebnis auf dem Geraet: alles im Unterverzeichnis scheitert, alles auf der
obersten Ebene gelingt.

packen.py ist berichtigt. Archive, deren Ordner es nicht mehr gibt, lassen
sich aber nicht neu packen - sie werden hier an Ort und Stelle berichtigt:
Verzeichnisse 0755, ausfuehrbare Dateien 0755, alle uebrigen 0644.

DER INHALT WIRD NICHT ANGEFASST. Vorher und nachher wird jeder Eintrag
byteweise verglichen; stimmt einer nicht, bleibt das alte Archiv stehen.

Aufruf:  archivrechte_berichtigen.py ARCHIV.zip [...] [--probe]
"""
import os, shutil, sys, tempfile, zipfile


def rechte(pfad):
    if pfad.endswith('/'):
        return 0o40755, 0x10
    teile = pfad.split('/')
    if teile[0] in ('bin', 'cron', 'daemon', 'sudoers') \
            or pfad == 'uninstall/uninstall' \
            or teile[-1].endswith(('.sh', '.pl', '.cgi')):
        return 0o100755, 0
    return 0o100644, 0


def berichtige(pfad, probe=False):
    alt = zipfile.ZipFile(pfad)
    eintraege = alt.infolist()
    ohne_x = [i.filename for i in eintraege
              if i.is_dir() and not (((i.external_attr >> 16) & 0o7777) & 0o111)]
    if not ohne_x:
        alt.close()
        return 'in Ordnung, nichts zu tun'
    inhalt = {i.filename: alt.read(i.filename) for i in eintraege if not i.is_dir()}
    if probe:
        alt.close()
        return '%d Verzeichnis(se) ohne x-Bit - waeren zu berichtigen' % len(ohne_x)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.zip',
                                      dir=os.path.dirname(pfad) or '.')
    tmp.close()
    with zipfile.ZipFile(tmp.name, 'w', zipfile.ZIP_DEFLATED) as neu:
        for i in eintraege:
            zi = zipfile.ZipInfo(i.filename, date_time=i.date_time)
            m, dos = rechte(i.filename)
            zi.create_system = 3
            zi.external_attr = (m << 16) | dos
            if i.is_dir():
                neu.writestr(zi, b'')
            else:
                zi.compress_type = zipfile.ZIP_DEFLATED
                neu.writestr(zi, inhalt[i.filename])
    alt.close()

    # Gegenprobe: jeder Eintrag byteweise gleich, kein Verzeichnis ohne x-Bit
    p = zipfile.ZipFile(tmp.name)
    schlecht = [n for n, b in inhalt.items() if p.read(n) != b]
    fehlt = sorted(set(inhalt) - set(p.namelist()))
    rest = [i.filename for i in p.infolist()
            if i.is_dir() and not (((i.external_attr >> 16) & 0o7777) & 0o111)]
    p.close()
    if schlecht or fehlt or rest:
        os.remove(tmp.name)
        return ('ABBRUCH: abweichend=%s fehlend=%s ohne_x=%s - das alte Archiv '
                'bleibt stehen' % (schlecht[:3], fehlt[:3], rest[:3]))
    shutil.move(tmp.name, pfad)
    return 'berichtigt: %d Verzeichnisse, %d Dateien byteweise gleich' % (
        len(ohne_x), len(inhalt))


if __name__ == '__main__':
    probe = '--probe' in sys.argv
    for f in [a for a in sys.argv[1:] if a != '--probe']:
        print('%-54s %s' % (os.path.basename(f), berichtige(f, probe)))
