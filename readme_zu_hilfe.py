#!/usr/bin/env python3
"""Erzeugt templates/help/help.html aus der README.md eines Plugins.

Der Hilfetext hinter dem Fragezeichen ist fuer Anwender gedacht. Deshalb
fliegen Abschnitte raus, die nur Entwickler angehen (Lizenz, Mitwirken,
Changelog, Installation aus dem Quelltext).

Aufruf:  readme_zu_hilfe.py <pluginordner> [--schreiben]
"""
import html
import re
import sys
from pathlib import Path

RAUS = re.compile(r'^(lizenz|license|mitwirken|contributing|changelog|'
                  r'.*nderungen|installation aus|entwicklung|danksagung|credits)',
                  re.I)


def inline(s):
    """Markdown-Auszeichnung innerhalb einer Zeile."""
    s = html.escape(s, quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*([^*]+)\*(?![\w*])', r'<i>\1</i>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', s)
    s = s.replace('&quot;', '"')
    return s


def wandeln(md):
    zeilen = md.split('\n')
    aus, i = [], 0
    titel = ''
    ueberspringen = False
    while i < len(zeilen):
        z = zeilen[i].rstrip()

        # Ueberschriften
        m = re.match(r'^(#{1,6})\s+(.*)$', z)
        if m:
            stufe, text = len(m.group(1)), m.group(2).strip()
            text = re.sub(r'^LoxBerry-Plugin:\s*', '', text)
            if stufe == 1 and not titel:
                titel = text
                aus.append('<h2>%s</h2>' % inline(text))
                ueberspringen = False
                i += 1
                continue
            ueberspringen = bool(RAUS.match(text))
            if not ueberspringen:
                aus.append('<h%d>%s</h%d>' % (min(stufe + 1, 4), inline(text),
                                              min(stufe + 1, 4)))
            i += 1
            continue
        if ueberspringen:
            i += 1
            continue

        # Codeblock
        if z.startswith('```'):
            i += 1
            block = []
            while i < len(zeilen) and not zeilen[i].startswith('```'):
                block.append(html.escape(zeilen[i], quote=False))
                i += 1
            i += 1
            aus.append('<pre><code>' + '\n'.join(block) + '</code></pre>')
            continue

        # Tabelle
        if z.startswith('|') and i + 1 < len(zeilen) and re.match(r'^\|[\s:|-]+\|?$', zeilen[i + 1].strip()):
            kopf = [c.strip() for c in z.strip('|').split('|')]
            i += 2
            reihen = []
            while i < len(zeilen) and zeilen[i].strip().startswith('|'):
                reihen.append([c.strip() for c in zeilen[i].strip().strip('|').split('|')])
                i += 1
            t = ['<table class="sm-tbl">', '<tr>'
                 + ''.join('<th>%s</th>' % inline(c) for c in kopf) + '</tr>']
            for r in reihen:
                t.append('<tr>' + ''.join('<td>%s</td>' % inline(c) for c in r) + '</tr>')
            t.append('</table>')
            aus.append('\n'.join(t))
            continue

        # Liste
        if re.match(r'^\s*[-*]\s+', z) or re.match(r'^\s*\d+\.\s+', z):
            geordnet = bool(re.match(r'^\s*\d+\.', z))
            punkte = []
            while i < len(zeilen):
                y = zeilen[i].rstrip()
                m2 = re.match(r'^\s*(?:[-*]|\d+\.)\s+(.*)$', y)
                if m2:
                    punkte.append(m2.group(1))
                elif y.strip() and y.startswith(('  ', '\t')) and punkte:
                    punkte[-1] += ' ' + y.strip()
                else:
                    break
                i += 1
            tag = 'ol' if geordnet else 'ul'
            aus.append('<%s>' % tag
                       + ''.join('<li>%s</li>' % inline(p) for p in punkte)
                       + '</%s>' % tag)
            continue

        # Absatz
        if z.strip():
            absatz = []
            while i < len(zeilen) and zeilen[i].strip() \
                    and not re.match(r'^(#{1,6}\s|\s*[-*]\s|\s*\d+\.\s|\||```)', zeilen[i]):
                absatz.append(zeilen[i].strip())
                i += 1
            if absatz:
                aus.append('<p>' + inline(' '.join(absatz)) + '</p>')
            continue
        i += 1
    return titel, '\n\n'.join(aus) + '\n'


if __name__ == '__main__':
    p = Path(sys.argv[1])
    schreiben = '--schreiben' in sys.argv
    rd = p / 'README.md'
    if not rd.is_file():
        print('  keine README.md in', p)
        sys.exit(1)
    titel, htm = wandeln(rd.read_text(encoding='utf-8'))
    ziel = p / 'templates/help/help.html'
    print('  %-38s %-34s %5d Zeichen' % (p.name[:38], titel[:34], len(htm)))
    if schreiben:
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(htm, encoding='utf-8')
