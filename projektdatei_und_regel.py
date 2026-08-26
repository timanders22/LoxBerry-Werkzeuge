# -*- coding: utf-8 -*-
# Hausregel: an einem UND-Baustein traegt JEDER Eingang genau eine Quelle.
import re, sys
TAB = chr(9); CRLF = chr(13) + chr(10)
L = open(sys.argv[1], "rb").read().decode("utf-8-sig").split(CRLF)
befunde = 0; angesehen = 0
i = 0
while i < len(L):
    t = L[i].strip()
    if t.startswith('<C Type="And"'):
        ti = re.search('Title="([^"]*)"', t)
        titel = ti.group(1) if ti else "?"
        d = 1; j = i + 1; cur = None; zahl = {}
        while j < len(L):
            v = L[j].strip()
            if v.startswith("<C ") and not v.endswith("/>"): d += 1
            elif v.startswith("</C>"):
                d -= 1
                if d == 0: break
            elif d == 1 and v.startswith("<Co "):
                k = re.search('K="([^"]*)"', v).group(1)
                cur = k if k in ("I1", "I2") else None
                if cur: zahl[cur] = 0
            elif d == 1 and v.startswith("<In ") and cur:
                zahl[cur] = zahl.get(cur, 0) + 1
            j += 1
        angesehen += 1
        for k in ("I1", "I2"):
            if zahl.get(k, 0) != 1:
                print("[BEFUND] Z%-6d %-46s %s traegt %d Quellen" % (i + 1, titel[:46], k, zahl.get(k, 0)))
                befunde += 1
        i = j
    i += 1
print("angesehene UND-Bausteine: %d, Befunde: %d" % (angesehen, befunde))
sys.exit(1 if befunde else 0)
