#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Broker-Attrappe fuer Werkzeuge/minutenlauf_pruefstand.sh (nur im Netz-Namensraum des Stands, 127.0.0.1:1883, reines MQTT 3.1.1 ohne Speicher).
Dazu 127.0.0.1:80 (siehe web()). CONNECT -> CONNACK, SUBSCRIBE -> SUBACK, PINGREQ -> PINGRESP, QoS-1-PUBLISH -> PUBACK, alles andere wird geschluckt. Liefert nie Werte.
Damit laufen Linien, die selbst per TCP mit dem Broker sprechen (phpMQTT, eigener Client), bis zum Senden, statt an "Network is unreachable" zu enden.
Die Themen schreibt sie mit, wenn ein Pfad angegeben ist: minutenlauf_broker.py [<mitschrift>]"""
import socket
import sys
import threading

MITSCHRIFT = sys.argv[1] if len(sys.argv) > 1 else None


def laenge(k, puffer):
    n, f, i = 0, 1, 0
    while True:
        while len(puffer) <= i:
            d = k.recv(65536)
            if not d:
                return None, None, puffer
            puffer += d
        b = puffer[i]
        n += (b & 127) * f
        f *= 128
        i += 1
        if not b & 128:
            return n, i, puffer


def dienst(k):
    puffer = b""
    try:
        while True:
            while len(puffer) < 2:
                d = k.recv(65536)
                if not d:
                    return
                puffer += d
            kopf = puffer[0]
            n, s, rest = laenge(k, puffer[1:])
            if n is None:
                return
            puffer = rest
            while len(puffer) < s + n:
                d = k.recv(65536)
                if not d:
                    return
                puffer += d
            nutz = puffer[s:s + n]
            puffer = puffer[s + n:]
            art = kopf >> 4
            if art == 1:
                k.sendall(bytes([0x20, 2, 0, 0]))
            elif art == 8:
                anzahl = 0
                i = 2
                while i + 2 <= len(nutz):
                    i += 3 + int.from_bytes(nutz[i:i + 2], "big")
                    anzahl += 1
                k.sendall(bytes([0x90, 2 + anzahl]) + nutz[:2] + bytes(anzahl))
            elif art == 12:
                k.sendall(bytes([0xD0, 0]))
            elif art == 3:
                tl = int.from_bytes(nutz[:2], "big")
                if MITSCHRIFT:
                    with open(MITSCHRIFT, "a", encoding="utf-8", errors="replace") as f:
                        f.write(nutz[2:2 + tl].decode("utf-8", "replace") + chr(10))
                if (kopf >> 1) & 3:
                    k.sendall(bytes([0x40, 2]) + nutz[2 + tl:4 + tl])
            elif art == 14:
                return
    except OSError:
        return
    finally:
        k.close()


def web(k):
    """Der lighttpd/Apache des LoxBerry: das SDK meldet Notifys per http://localhost:80/admin/system/ajax/ajax-notification-handler.cgi. Antwortet nur 200."""
    try:
        k.settimeout(2)
        k.recv(65536)
        k.sendall(b"HTTP/1.0 200 OK" + bytes([13, 10]) + b"Content-Type: application/json" + bytes([13, 10, 13, 10]) + b"{}")
    except OSError:
        pass
    finally:
        k.close()


def web_dienst():
    w = socket.socket()
    w.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    w.bind(("127.0.0.1", 80))
    w.listen(16)
    while True:
        v, _ = w.accept()
        threading.Thread(target=web, args=(v,), daemon=True).start()


threading.Thread(target=web_dienst, daemon=True).start()
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", 1883))
s.listen(16)
while True:
    v, _ = s.accept()
    threading.Thread(target=dienst, args=(v,), daemon=True).start()
