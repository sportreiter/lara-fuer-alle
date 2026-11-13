# Rezeptentwurf: KI-Assistent sicher mit eigenem VPS verbinden

**Status: Architekturidee, nicht als Ein-Klick-Installation freigegeben.**

Der Nutzer betreibt auf seinem VPS definierte Werkzeuge. Ein autorisierter Connector oder eine sichere Ausführungsumgebung stellt dem Assistenten **nur ausgewählte Funktionen** zur Verfügung, nicht zwingend eine freie Root-Shell.

**Minimaler Aufbau:** Chat-Assistent → autorisiertes Werkzeug/Connector → abgesicherter VPS-Dienst → eng begrenzte Fachfunktionen → protokolliertes Ergebnis.

**Grundsätze:** verschlüsselte Verbindung; getrennte Dienstbenutzer; kurzlebige Zugangsdaten; minimaler Funktionsumfang; Leseoperationen zuerst; mutierende Aktionen erst nach Nutzerfreigabe; Fehler- und Wiederherstellungsweg. Keine Tokens in Git oder öffentlichen Prompts.

**Testidee:** Ein synthetisches Statuswerkzeug liefert Dienstzustand und Version ohne private Daten. Erst wenn der Zugriff nachvollziehbar, widerrufbar und protokolliert ist, folgt eine weitere Funktion.

**Wichtig:** Die konkrete Installation hängt vom gewählten Assistenten, dessen Connector-/Computerzugang und dem Hosting ab. Chat-Abonnements liefern nicht automatisch eine universelle VPS-Verbindung.
