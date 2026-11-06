# Banken fuer die Pruefwerkzeuge

Hier liegen Abbilder (`loxone.json` und Verwandte), die ein Pruefwerkzeug vor
dem Lauf nach `lb/data/plugins/<ordner>/` kopiert.

**Warum nicht gleich dort?** Weil `wachposten_wirkung.py` genau diese drei
Baeume vor jedem seiner vier Faelle mit `rmtree` leert - zu Recht, es braucht
einen sauberen Stand. Eine Bank, die dort liegt, ueberlebt den naechsten Lauf
eines anderen Werkzeugs nicht. Am 31.08.2026 ist das zweimal passiert, und
beim ersten Mal meldete `au_reitertest.py` daraufhin "10 Laeufe, 0
Beanstandungen" - aus einer leeren Bank.

**Namensform:** `<FOLDER aus plugin.cfg>.<dateiname>.json`

**Was ein Abbild enthalten soll:** einen VOLLSTAENDIGEN Datensatz und einen
UNVOLLSTAENDIGEN. Der zweite ist der wichtigere - er stellt den Zustand nach
einer abgewiesenen Abfrage nach (bei Skoda: HTTP 429 auf den Endpunkt `info`,
danach fehlen modell, kennzeichen, motorart und software). Genau daran sind
sechs ungeschuetzte Feldzugriffe der Oberflaeche aufgefallen.
