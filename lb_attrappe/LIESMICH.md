# LoxBerry-Attrappe für die Prüfwerkzeuge

Nachbildung der Teile des LoxBerry-PHP-SDK, die die Plugins wirklich
benutzen. Damit lassen sich die Oberflächen **ausführen**, ohne einen
LoxBerry zu haben — und zwar unter PHP 7.4 *und* 8.x.

    libs/phplib/loxberry_system.php   LBSystem, Konstanten, readlanguage
    libs/phplib/loxberry_web.php      LBWeb (lbheader setzt bewusst SDK-Globale)
    libs/phplib/loxberry_log.php      LBLog und die LOG*-Funktionen
    libs/phplib/loxberry_io.php       mqtt_connectiondetails
    config/system/general.json        Miniserver, Netz, Fassung
    config/plugins/mqttgateway/       Broker-Zugangsdaten des Gateways

`loxberry_web.php` bildet ausdrücklich nach, dass `lbheader()` Globale wie
`$cfg` setzt — genau deshalb verlangen die Hausregeln überall ein
Plugin-Präfix. Wer die Attrappe „aufräumt" und das wegnimmt, verliert die
Prüfung auf diesen Fehler.

Benutzt wird sie von `rendern.py`, `wirkungstest.py`, `mqtt_probe.py` und
`formularpruefung.py` (jeweils eine Ebene höher).

## Sie altert — und wird deshalb gemessen

Die Nachbildung bleibt stehen, während das Original weitergeht. Stand
25.08.2026 ist sie gegen **LoxBerry 4.0.0.15** geprüft; dabei fehlte
`notify_ext()` (von acht Plugins gerufen), `LOGTIT()` hieß in Wahrheit
`LOGTITLE()`, `lbsystemversion()` war frei erfunden, und acht Signaturen
verlangten mehr Argumente als das Original.

    python3 ../attrappe_pruefen.py

Das Werkzeug liest die aktuelle Fassung aus den Releases, vergleicht die
Namen und Signaturen und prüft, dass **alle vier Stände** (`lb`,
`lb_attrappe`, `lb_leer`, `lb_mqtt`) dieselbe `phplib` tragen. Genau daran
hing es: drei der vier waren veraltet, und der gepflegte wurde von einem
einzigen Werkzeug gelesen.

**Die vier Ordner sind keine Kopien voneinander** — sie unterscheiden sich in
ihren Konfigurationen und sind verschiedene Prüfumgebungen (`lb` 267
Plugin-Konfigurationen, `lb_mqtt` 261 mit MQTT, `lb_attrappe` eine,
`lb_leer` ein LoxBerry ohne eingerichtete Plugins). Gemeinsam ist ihnen nur
`libs/phplib/`. Wer einen davon löscht, verliert eine Prüfumgebung, keine
Dublette.

**Die Attrappe darf nachsichtiger sein als das Original, wo es um die
UMGEBUNG geht — nie, wo es um die SCHNITTSTELLE geht.** Eine Funktion, die
es im Original nicht gibt, gehört hier ersatzlos weg: ein Plugin, das sie
ruft, soll in der Prüfung abstürzen, weil es auf dem echten LoxBerry
genauso abstürzt.
