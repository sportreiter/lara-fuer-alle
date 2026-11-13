# Rezeptentwurf: Privates, nachvollziehbares Memory

**Status: Konzept. Keine Veröffentlichung privater Implementierung oder Datenbank.**

Ein Assistent kann hilfreiche Fakten, Entscheidungen, Annahmen und offene Fragen in einer privaten Datenbank verwalten. Die eigentliche KI wird dadurch **nicht automatisch neu trainiert**.

**Bausteine:** lokale/private Speicherung; Herkunft und Aktualisierungsdatum jeder Information; bewusste Korrektur/Verwerfen veralteter Annahmen; Vollständigkeitscheck; eine lesende Suchschnittstelle; Backup und getestete Wiederherstellung.

**Beispiel mit erfundenen Daten:** „Ein Beispielprojekt nutzt seit Oktober ein NAS; die frühere Annahme lokaler Laptop-Speicherung ist historisch.“ Der Assistent muss die neuere bestätigte Entscheidung berücksichtigen, statt alte Fakten zu vermischen.

**Sicherheit:** keine automatische Synchronisierung an fremde Assistenten; keine Memory-Daten in öffentliche Issues, RSS oder Codebeispiele; kontrollierte Berechtigungen und Datenlöschung.
