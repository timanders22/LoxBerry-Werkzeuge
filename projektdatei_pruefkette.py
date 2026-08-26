# -*- coding: utf-8 -*-
# Zehnteilige Pruefkette aus REGELN_3 A2, lesend.
# Punkt 10 kam am 20.08.2026 dazu (A5c): einen von Config verworfenen
# Baustein erkennt man an der Null-UUID. Punkt 5 findet ihn NICHT - die
# Null-UUID ist formal gueltig, und solange es nur eine gibt, ist sie auch
# keine Dublette.
import re, sys, collections
import xml.etree.ElementTree as ET
CRLF = chr(13) + chr(10)
p = sys.argv[1]
b = open(p, "rb").read()
s = b.decode("utf-8-sig")
L = s.split(CRLF)
ok = True
def sag(nr, txt, gut):
    global ok
    print(("[OK]  " if gut else "[FEHL]") + " %d. %s" % (nr, txt))
    if not gut: ok = False
sag(1, "BOM=%s CRLF=%d einzelne LF=%d" % (b[:3] == bytes([0xEF,0xBB,0xBF]), b.count(CRLF.encode()), b.count(bytes([10])) - b.count(CRLF.encode())),
    b[:3] == bytes([0xEF,0xBB,0xBF]))
for tag in ("C", "Co", "In", "IoData"):
    auf = len(re.findall("<" + tag + "[ >]", s))
    selbst = len(re.findall("<" + tag + " [^>]*/>", s))
    zu = len(re.findall("</" + tag + ">", s))
    sag(2, "Tag %-7s auf=%-6d selbstschliessend=%-6d zu=%-6d" % (tag, auf, selbst, zu), auf - selbst == zu)
d = 0; unter = 0
for l in L:
    t = l.strip()
    if t.startswith("<C ") and not t.endswith("/>"): d += 1
    elif t.startswith("</C>"): d -= 1; unter = min(unter, d)
sag(3, "Verschachtelungstiefe Ende=%d Unterlauf=%d" % (d, unter), d == 0 and unter == 0)
def entdoppeln(zeile):
    st = [m.start() for m in re.finditer(' Title="', zeile)]
    if len(st) < 2: return zeile
    for anf in reversed(st[1:]):
        ende = zeile.index('"', zeile.index('"', anf + 8) + 1) + 1 if False else zeile.index('"', anf + 8) + 1
        zeile = zeile[:anf] + zeile[ende:]
    return zeile
ber = CRLF.join([entdoppeln(x) if 'Type="ApiActor"' in x else x for x in L])
try:
    ET.fromstring(ber); sag(4, "XML wohlgeformt", True)
except Exception as e:
    sag(4, "XML: %s" % e, False)
uu = re.findall(' U="([^"]*)"', s)
form = re.compile("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{16}$")
dop = [u for u, c in collections.Counter(uu).items() if c > 1]
schlecht = [u for u in uu if not form.match(u)]
sag(5, "UUIDs %d, verschieden %d, Dubletten %d, Formfehler %d" % (len(uu), len(set(uu)), len(dop), len(schlecht)),
    not dop and not schlecht)
alle = set(uu)
tot = [i for i in re.findall('<In Input="([^"]*)"', s) if i not in alle]
sag(6, "tote <In>: %d" % len(tot), not tot)
ncf = 0; niof = 0
i = 0
while i < len(L):
    t = L[i].strip()
    if t.startswith("<Co "):
        m = re.search('Nc="([0-9]+)"', t); n = 0
        if not t.endswith("/>"):
            j = i + 1
            while j < len(L) and not L[j].strip().startswith("</Co>"):
                if L[j].strip().startswith("<In "): n += 1
                j += 1
        if (int(m.group(1)) if m else 0) != n: ncf += 1
    elif t.startswith("<C ") and not t.endswith("/>"):
        m = re.search('Nio="([0-9]+)"', t)
        dd = 1; j = i + 1; c = 0
        while j < len(L) and dd > 0:
            u = L[j].strip()
            if u.startswith("<C ") and not u.endswith("/>"): dd += 1
            elif u.startswith("</C>"): dd -= 1
            elif u.startswith("<Co ") and dd == 1: c += 1
            j += 1
        if m and int(m.group(1)) != c: niof += 1
    i += 1
sag(7, "Nc-Abweichungen=%d  Nio-Abweichungen=%d" % (ncf, niof), ncf == 0 and niof == 0)
sag(8, "Dateiende %r" % s[-18:], s.rstrip(CRLF).endswith("</ControlList>"))
refs = set(re.findall(' Ref="([^"]*)"', s))
ohne = [r for r in refs if r not in alle]
sag(9, "Ref ohne Ziel: %d" % len(ohne), not ohne)
# Nur U= an <C> und <Co> zaehlt. Icon="00000000-..." heisst "kein Symbol"
# und steht in dieser Anlage 473mal voellig zu Recht.
NULL = ' U="00000000-0000-0000-0000000000000000"'
verworfen = [i + 1 for i, l in enumerate(L)
             if (l.strip().startswith("<C ") or l.strip().startswith("<Co ")) and NULL in l]
sag(10, "verworfene Bausteine (Null-UUID): %d%s" % (
        len(verworfen), (" in Zeile " + ", ".join(map(str, verworfen[:5]))) if verworfen else ""),
    not verworfen)
print()
print("ERGEBNIS:", "alle zehn Punkte bestanden" if ok else "NICHT BESTANDEN")
sys.exit(0 if ok else 1)
