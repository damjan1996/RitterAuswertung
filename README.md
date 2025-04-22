# Ritter Digital Raumbuch Auswertung

Eine Web-Anwendung zur Analyse und Visualisierung von Raumbuch-Daten aus dem RdRaumbuch-System.

## Übersicht

Diese Anwendung ermöglicht:

- Anzeigen der Raumbuch-Daten für einen ausgewählten Standort
- Filtern und Sortieren der Daten nach verschiedenen Kriterien
- Berechnung von Statistiken und Zusammenfassungen
- Visualisierung der Daten mit Diagrammen
- Export der Daten als Excel oder PDF

## Installation

### Voraussetzungen

- Python 3.8 oder höher
- SQL Server ODBC-Treiber
- Zugriff auf die RdRaumbuch-Datenbank

### Schritte

1. Repository klonen:
   ```
   git clone https://github.com/damjan1996/RitterAuswertung.git
   cd RitterAuswertung
   ```

2. Virtuelle Umgebung erstellen und aktivieren:
   ```
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/macOS
   python -m venv venv
   source venv/bin/activate
   ```

3. Abhängigkeiten installieren:
   ```
   pip install -r requirements.txt
   ```

4. Anwendung installieren:
   ```
   pip install -e .
   ```

5. Konfiguration anpassen:
   - `config/database.py`: Datenbankverbindungsparameter
   - `config/settings.py`: Anwendungseinstellungen

## Verwendung

### Anwendung starten

```
# Mit dem Startskript
python scripts/run_app.py

# Alternativ mit Python direkt
python -m src.web.app
```

Die Anwendung ist dann unter http://localhost:5000 erreichbar.

### Funktionen

1. **Standort auswählen**: Auf der Startseite einen Standort aus der Dropdown-Liste auswählen.
2. **Raumbuch-Daten anzeigen**: Nach der Auswahl werden die Daten als Tabelle angezeigt.
3. **Daten filtern**: Verwenden Sie die Filter über der Tabelle, um bestimmte Bereiche, Gebäudeteile, Etagen oder Reinigungsgruppen zu filtern.
4. **Zusammenfassung anzeigen**: Oben auf der Seite werden Zusammenfassungen wie Gesamtfläche, monatliche/jährliche Kosten und Arbeitsstunden angezeigt.
5. **Daten visualisieren**: Verschiedene Diagramme zeigen die Verteilung nach Bereichen, Reinigungsgruppen und Etagen.
6. **Daten exportieren**: Verwenden Sie die Export-Buttons, um die Daten als Excel- oder PDF-Datei zu exportieren.

## Projektstruktur

```
RitterDigitalAuswertung/
├── config/                  # Konfigurationsdateien
├── src/                     # Quellcode
│   ├── database/            # Datenbankbezogener Code
│   ├── models/              # Datenmodelle
│   ├── analysis/            # Datenanalyse-Code
│   └── web/                 # Web-Interface
│       ├── static/          # Statische Dateien (CSS, JS)
│       └── templates/       # HTML-Vorlagen
├── tests/                   # Testcode
└── scripts/                 # Hilfsskripte
```

## Tests

Tests können mit unittest ausgeführt werden:

```
python -m unittest discover tests
```

## Fehlerbehebung

### Datenbankverbindungsprobleme

- Stellen Sie sicher, dass die SQL Server-Verbindungsparameter in `config/database.py` korrekt sind.
- Überprüfen Sie, ob der ODBC-Treiber für SQL Server installiert ist.
- Testen Sie die Verbindung mit einem einfachen Skript:
  ```python
  from src.database.connection import test_connection
  print(test_connection())  # Sollte True zurückgeben, wenn die Verbindung erfolgreich ist
  ```

### Fehlende Abhängigkeiten

Wenn Fehler bezüglich fehlender Module auftreten, stellen Sie sicher, dass alle Abhängigkeiten installiert sind:

```
pip install -r requirements.txt
```

## Lizenz

Dieses Projekt ist proprietär und nur für die interne Verwendung bei Ritter Digital bestimmt.

## Kontakt

Bei Fragen oder Problemen wenden Sie sich an:
- Damjan Petrovic - [petrovic@ritter-digital.de](mailto:petrovic@ritter-digital.de)