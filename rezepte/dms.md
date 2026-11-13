# Rezeptentwurf: Persönliches Dokumentenmanagement (DMS)

**Status: Architektur- und Testskizze, keine fertige Installationsanleitung.**

Ziel: Rechnungen und andere Dokumente privat ablegen, durchsuchbar machen und Fristen zuverlässig erkennen – ohne sensible Unterlagen an fremde KI-Dienste zu übergeben.

**Bausteine:** gesicherter Importordner → Dateitypprüfung → lokale PDF-Textextraktion / bei Bedarf OCR → nachvollziehbare Metadaten → Archivablage mit stabiler Dokument-ID → lokale Suche → getrennte Fristen-/Zahlungsstatus.

**Wichtige Sicherheitsregeln:** Original unverändert behalten; Dubletten erkennen; widersprüchliche Datumsfelder als unklar markieren; OCR-Ergebnis nicht als bestätigte Zahlungsfrist ausgeben; kein automatisches Bezahlen oder Versicherungs-Einreichen; Protokolle und Backups prüfen.

**Synthetischer Test:** Beispielrechnung A nennt zwei unterschiedliche Zahlungsfristen. Erwartung: Manuelle Prüfung statt stiller Auswahl eines Datums. Testdokumente enthalten keine echten Namen oder Rechnungsnummern.

**Voraussetzungen:** privater Speicher, Backup, je nach Dokumentenart lokale OCR-Software. Ein NAS ist optional.
