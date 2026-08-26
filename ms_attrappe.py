#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Attrappe eines Loxone Miniservers - streng nach dem Dokument gebaut.

Sie wurde AUS DEM DOKUMENT geschrieben, nicht aus dem Client. Damit prueft der
Lauf, ob Client und Dokument zusammenpassen, und nicht, ob der Client zu sich
selbst passt.

  [K] "Communicating with the Miniserver" 16.0, 03.06.2025

Was nachgebildet ist:
  - HTTP: jdev/cfg/api, jdev/sys/getPublicKey, jdev/sys/getkey, jdev/sps/io/.../state
  - WebSocket /ws/rfc6455, Unterprotokoll "remotecontrol"
  - jdev/sys/keyexchange, getkey2, enc-Befehle, getjwt, authwithtoken
  - jdev/sps/enablebinstatusupdate mit Werte- und Text-Ereignistabellen
  - data/LoxAPP3.json als Textnachricht
  - Nachrichtenkopf 0x03 vor JEDER Nachricht

Was die Attrappe absichtlich NICHT kann: TLS und Statistiken.

WICHTIG: Sie ist so streng wie das Geraet, nicht so nachsichtig wie ein
Client. Wo das Dokument eine Schreibweise vorschreibt, wird jede andere
abgewiesen - sonst prueft der Lauf den Nachbau gegen sich selbst. Am
16.08.2026 hat genau das einen Fehler ueber eine ganze Pruefreihe verdeckt
(keyexchange, siehe dort).
"""
import asyncio, base64, hashlib, hmac, json, os, struct, sys, threading
import urllib.parse

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import websockets

BENUTZER = "admin"
PASSWORT = "geheim123"
USER_SALT = "5a3f"
HASH_ALG = "SHA256"
GETKEY2_KEY = "4141424243434444"       # hex, wie vom Miniserver geliefert
GETKEY_KEY = "3132333435363738"
TOKEN = "eyJhbGciOiJIUzI1NiJ9.pruefstand.xxxx"

_priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_pub_pem = _priv.public_key().public_bytes(
    serialization.Encoding.PEM,
    serialization.PublicFormat.SubjectPublicKeyInfo).decode("ascii")
# Loxone liefert den Schluessel mit CERTIFICATE-Rahmen - genau das bildet die
# Attrappe nach, damit die Aufbereitung im Client wirklich geprueft wird.
_pub_lox = ("-----BEGIN CERTIFICATE-----"
            + "".join(_pub_pem.strip().splitlines()[1:-1])
            + "-----END CERTIFICATE-----")

STRUKTUR = {
    "lastModified": "2026-08-06 01:00:00",
    "msInfo": {"serialNr": "504F94A00000", "msName": "Pruefstand",
               "projectName": "Attrappe", "localUrl": "pruefstand.local"},
    "rooms": {
        "0af17bf3-0125-02a1-ffff112233445566": {"name": "EG Wohnzimmer", "defaultRating": 10,
                                                "uuid": "0af17bf3-0125-02a1-ffff112233445566"},
        "0af17bf3-0125-029b-ffff112233445566": {"name": "KG Vorrat Ost", "defaultRating": 3,
                                                "uuid": "0af17bf3-0125-029b-ffff112233445566"},
    },
    "cats": {
        "0af17bf3-0115-025e-ffff112233445566": {"name": "Beleuchtung", "defaultRating": 10,
                                                "type": "lights"},
        "0af17bf3-0115-0260-ffff112233445566": {"name": "Beschattung", "defaultRating": 8,
                                                "type": "shading"},
    },
    "controls": {
        "aaaa0001-0000-0000-ffff000000000001": {
            "name": "Deckenlicht", "type": "Switch",
            "uuidAction": "aaaa0001-0000-0000-ffff000000000001",
            "room": "0af17bf3-0125-02a1-ffff112233445566",
            "cat": "0af17bf3-0115-025e-ffff112233445566",
            "defaultRating": 5, "isSecured": False, "isFavorite": True,
            "states": {"active": "bbbb0001-0000-0000-ffff000000000001"},
        },
        "aaaa0002-0000-0000-ffff000000000002": {
            "name": "Rollo Sued", "type": "Jalousie",
            "uuidAction": "aaaa0002-0000-0000-ffff000000000002",
            "room": "0af17bf3-0125-02a1-ffff112233445566",
            "cat": "0af17bf3-0115-0260-ffff112233445566",
            "defaultRating": 4, "isSecured": False,
            "states": {"position": "bbbb0002-0000-0000-ffff000000000002",
                       "shadePosition": "bbbb0002-0000-0000-ffff000000000003",
                       "up": "bbbb0002-0000-0000-ffff000000000004",
                       "down": "bbbb0002-0000-0000-ffff000000000005",
                       "autoActive": "bbbb0002-0000-0000-ffff000000000006",
                       "infoText": "bbbb0002-0000-0000-ffff000000000007"},
        },
        "aaaa0003-0000-0000-ffff000000000003": {
            "name": "Aussentemperatur", "type": "InfoOnlyAnalog",
            "uuidAction": "aaaa0003-0000-0000-ffff000000000003",
            "room": "0af17bf3-0125-029b-ffff112233445566",
            "defaultRating": 2, "isSecured": False,
            "details": {"format": "%.1f&deg;"},
            "states": {"value": "bbbb0003-0000-0000-ffff000000000001"},
        },
        "aaaa0004-0000-0000-ffff000000000004": {
            "name": "Was es nicht gibt", "type": "PhantasieBaustein",
            "uuidAction": "aaaa0004-0000-0000-ffff000000000004",
            "room": "0af17bf3-0125-029b-ffff112233445566",
            "defaultRating": 0, "isSecured": False,
            "states": {"irgendwas": "bbbb0004-0000-0000-ffff000000000001"},
        },
        "aaaa0005-0000-0000-ffff000000000005": {
            "name": "Nicht anzeigen", "type": "",
            "uuidAction": "aaaa0005-0000-0000-ffff000000000005",
            "defaultRating": 0, "isSecured": False, "states": {},
        },
        "aaaa0006-0000-0000-ffff000000000006": {
            "name": "Alarmanlage", "type": "Alarm",
            "uuidAction": "aaaa0006-0000-0000-ffff000000000006",
            "room": "0af17bf3-0125-02a1-ffff112233445566",
            "defaultRating": 9, "isSecured": True,
            "states": {"armed": "bbbb0006-0000-0000-ffff000000000001",
                       "level": "bbbb0006-0000-0000-ffff000000000002"},
        },
    },
    "globalStates": {},
}

WERTE = {
    "bbbb0001-0000-0000-ffff000000000001": 1.0,
    "bbbb0002-0000-0000-ffff000000000002": 0.35,
    "bbbb0002-0000-0000-ffff000000000003": 0.0,
    "bbbb0002-0000-0000-ffff000000000004": 0.0,
    "bbbb0002-0000-0000-ffff000000000005": 0.0,
    "bbbb0002-0000-0000-ffff000000000006": 1.0,
    "bbbb0003-0000-0000-ffff000000000001": 21.4,
    "bbbb0004-0000-0000-ffff000000000001": 7.0,
    "bbbb0006-0000-0000-ffff000000000001": 0.0,
    "bbbb0006-0000-0000-ffff000000000002": 0.0,
}
TEXTE = {"bbbb0002-0000-0000-ffff000000000007": "Automatik aktiv"}

PROTOKOLL = []


def ll(wert, code="200"):
    return json.dumps({"LL": {"control": "x", "value": wert, "Code": code}})


def uuid_bytes(s):
    a, b, c, rest = s.split("-")
    return struct.pack("<IHH", int(a, 16), int(b, 16), int(c, 16)) + bytes.fromhex(rest)


def kopf(kennung, laenge):
    return bytes([0x03, kennung, 0x00, 0x00]) + struct.pack("<I", laenge)


class WSTeil:
    def __init__(self, ws):
        self.ws = ws
        self.key = None
        self.iv = None
        self.salt = None
        self.angemeldet = False

    async def senden_text(self, text):
        b = text.encode("utf-8")
        await self.ws.send(kopf(0, len(b)))
        await self.ws.send(text)

    async def senden_werte(self, paare):
        roh = b"".join(uuid_bytes(u) + struct.pack("<d", float(v)) for u, v in paare)
        await self.ws.send(kopf(2, len(roh)))
        await self.ws.send(roh)

    async def senden_texte(self, paare):
        roh = b""
        for u, t in paare:
            b = t.encode("utf-8")
            roh += uuid_bytes(u) + b"\x00" * 16 + struct.pack("<I", len(b)) + b
            roh += b"\x00" * ((-len(b)) % 4)
        await self.ws.send(kopf(3, len(roh)))
        await self.ws.send(roh)

    def entschluesseln(self, enc):
        roh = base64.b64decode(urllib.parse.unquote(enc))
        d = Cipher(algorithms.AES(self.key), modes.CBC(self.iv)).decryptor()
        klar = (d.update(roh) + d.finalize()).rstrip(b"\x00").decode("utf-8")
        teile = klar.split("/", 2)
        if teile[0] != "salt":
            raise ValueError("kein Salt vorangestellt")
        if self.salt is not None and teile[1] == self.salt:
            PROTOKOLL.append("WARNUNG Salt wurde nicht gewechselt")
        self.salt = teile[1]
        return teile[2]

    async def behandeln(self, cmd, verschluesselt=False):
        PROTOKOLL.append(("ENC " if verschluesselt else "WS  ") + cmd.split("?")[0][:70])

        if cmd.startswith("jdev/sys/keyexchange/"):
            # STRENG, und das ist der Sinn dieser Attrappe.
            #
            # Bis zum 16.08.2026 stand hier urllib.parse.unquote(). Damit nahm
            # die Attrappe den Sitzungsschluessel in beiden Schreibweisen an -
            # ein echter Miniserver (Fassung 17.1.7.27, gemessen) nimmt ihn
            # NUR roh und antwortet auf die URI-kodierte Form mit 401. Der
            # Fehler steckte ueber die ganze Pruefreihe im Client und blieb
            # unsichtbar, weil die Attrappe dem CLIENT nachgebaut war statt
            # dem GERAET.
            #
            # [K, Step-by-step Guide] Schritt 7 nennt fuer keyexchange keine
            # Kodierung; kodiert werden nur der Sitzungsschluessel im
            # HTTP-Abfrageteil (Schritt 11) und der Chiffretext bei
            # jdev/sys/enc (dort ausdruecklich).
            teil = cmd.split("/", 3)[3]
            if "%" in teil:
                PROTOKOLL.append("FEHLSCHLAG keyexchange: URI-kodiert statt roh")
                await self.senden_text(ll("", "401"))
                return
            roh = base64.b64decode(teil)
            klar = _priv.decrypt(roh, padding.PKCS1v15()).decode("ascii")
            k, i = klar.split(":")
            self.key, self.iv = bytes.fromhex(k), bytes.fromhex(i)
            await self.senden_text(ll("keyexchange ok"))
            return

        if cmd.startswith("jdev/sys/enc/"):
            innen = self.entschluesseln(cmd.split("/", 3)[3])
            await self.behandeln(innen, True)
            return

        if cmd.startswith("jdev/sys/getkey2/"):
            await self.senden_text(ll({"key": GETKEY2_KEY, "salt": USER_SALT,
                                       "hashAlg": HASH_ALG}))
            return

        if cmd.startswith("jdev/sys/getjwt/"):
            if not verschluesselt:
                # [K, Seite 30]: unverschluesselt wird mit 400 abgewiesen.
                await self.senden_text(ll("", "400")); return
            t = cmd.split("/")
            h, user = t[3], t[4]
            pw = hashlib.sha256(("%s:%s" % (PASSWORT, USER_SALT)).encode()).hexdigest().upper()
            soll = hmac.new(bytes.fromhex(GETKEY2_KEY),
                            ("%s:%s" % (BENUTZER, pw)).encode(), hashlib.sha256).hexdigest()
            if h != soll or urllib.parse.unquote(user) != BENUTZER:
                PROTOKOLL.append("FEHLSCHLAG getjwt: Hash stimmt nicht")
                await self.senden_text(ll("", "401")); return
            self.angemeldet = True
            await self.senden_text(ll({"token": TOKEN, "validUntil": 555000000,
                                       "tokenRights": 4, "unsecurePass": False,
                                       "key": GETKEY_KEY}))
            return

        if cmd.startswith("authwithtoken/"):
            h = cmd.split("/")[1]
            soll = hmac.new(bytes.fromhex(GETKEY_KEY), TOKEN.encode(),
                            hashlib.sha256).hexdigest()
            if h != soll:
                await self.senden_text(ll("", "401")); return
            self.angemeldet = True
            await self.senden_text(ll({"validUntil": 555000000, "tokenRights": 4}))
            return

        if cmd == "jdev/sys/getkey":
            await self.senden_text(ll(GETKEY_KEY)); return

        if not self.angemeldet:
            # [K, Seite 9]: andere Befehle vor der Anmeldung -> 400
            await self.senden_text(ll("", "400")); return

        if cmd == "jdev/sps/LoxAPPversion3":
            # [K, Seite 25]: liefert den lastModified-Zeitstempel der Struktur.
            await self.senden_text(ll(STRUKTUR["lastModified"])); return

        if cmd == "data/LoxAPP3.json":
            await self.senden_text(json.dumps(STRUKTUR)); return

        if cmd == "jdev/sps/enablebinstatusupdate":
            await self.senden_text(ll("1"))
            await self.senden_werte(list(WERTE.items()))
            await self.senden_texte(list(TEXTE.items()))
            return

        if cmd == "keepalive":
            await self.ws.send(kopf(6, 0)); return

        if cmd.startswith("jdev/sps/io/"):
            t = cmd.split("/")
            uuid, befehl = t[3], "/".join(t[4:])
            if uuid not in STRUKTUR["controls"]:
                await self.senden_text(ll("", "404")); return
            await self.senden_text(ll(befehl))
            # Wirkung nachbilden: Schalter kippt, Jalousie faehrt
            if uuid == "aaaa0001-0000-0000-ffff000000000001":
                neu = 1.0 if befehl == "on" else 0.0
                WERTE["bbbb0001-0000-0000-ffff000000000001"] = neu
                await self.senden_werte([("bbbb0001-0000-0000-ffff000000000001", neu)])
            if uuid == "aaaa0002-0000-0000-ffff000000000002" and befehl.startswith("manualPosition/"):
                neu = float(befehl.split("/")[1]) / 100.0
                WERTE["bbbb0002-0000-0000-ffff000000000002"] = neu
                await self.senden_werte([("bbbb0002-0000-0000-ffff000000000002", neu)])
            return

        await self.senden_text(ll("", "400"))


async def ws_handler(ws):
    if ws.request.path != "/ws/rfc6455":
        await ws.close(); return
    teil = WSTeil(ws)
    async for n in ws:
        if isinstance(n, bytes):
            continue
        await teil.behandeln(n)


def http_antwort(verbindung, anfrage):
    """Der echte Miniserver bedient HTTP und WebSocket auf DEMSELBEN Port.

    websockets ruft diesen Haken vor dem Handshake auf; wer keine
    WebSocket-Anfrage stellt, bekommt hier die HTTP-Antwort.
    """
    pfad = urllib.parse.urlparse(anfrage.path).path.lstrip("/")
    if pfad == "ws/rfc6455":
        return None
    frage = urllib.parse.parse_qs(urllib.parse.urlparse(anfrage.path).query)
    PROTOKOLL.append("HTTP " + pfad)
    if pfad == "jdev/cfg/api":
        koerper = ll('{"snr":"504F94A00000","version":"16.0.1.1","key":"x",'
                     '"httpsStatus":0,"local":true,"hasEventSlots":true}')
    elif pfad == "jdev/sys/getPublicKey":
        koerper = ll(_pub_lox)
    elif pfad == "jdev/sys/getkey":
        koerper = ll(GETKEY_KEY)
    elif pfad.startswith("jdev/sps/io/"):
        soll = hmac.new(bytes.fromhex(GETKEY_KEY), TOKEN.encode(), hashlib.sha256).hexdigest()
        if frage.get("autht", [""])[0] != soll or frage.get("user", [""])[0] != BENUTZER:
            return verbindung.respond(401, ll("", "401"))
        uuid = pfad.split("/")[3]
        zustand = STRUKTUR["controls"].get(uuid, {}).get("states", {})
        erst = next(iter(zustand.values()), None)
        koerper = ll(WERTE.get(erst, 0))
    else:
        return verbindung.respond(404, ll("", "404"))
    return verbindung.respond(200, koerper)


def protokoll_zeigen():
    print("--- Protokoll der Attrappe ---")
    for z in PROTOKOLL: print("   ", z)


async def main(port):
    print("ATTRAPPE: HTTP und WebSocket auf %d" % port, flush=True)
    async with websockets.serve(ws_handler, "127.0.0.1", port,
                                subprotocols=["remotecontrol"],
                                process_request=http_antwort):
        try:
            await asyncio.Future()
        finally:
            protokoll_zeigen()


if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 18080
    try:
        asyncio.run(main(p))
    except KeyboardInterrupt:
        pass
