#!/usr/bin/env python
"""
Skript zum Ausführen aller Tests mit Coverage-Bericht.
"""

import os
import sys
import subprocess
import webbrowser
import json


def run_tests_with_coverage():
    """
    Führt alle Tests mit pytest und generiert einen Coverage-Bericht.
    """
    print("Ausführen der Tests mit Coverage-Analyse...")

    # Basisverzeichnis ermitteln
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Coverage-Ordner erstellen, falls er nicht existiert
    coverage_dir = os.path.join(base_dir, 'htmlcov')
    if not os.path.exists(coverage_dir):
        os.makedirs(coverage_dir)

    # Tests mit Coverage ausführen
    cmd = [
        sys.executable, '-m', 'pytest',
        '--cov=src',  # Coverage für das src-Verzeichnis messen
        '--cov-report=term-missing',  # Fehlende Zeilen in der Konsole anzeigen
        '--cov-report=html:' + coverage_dir,  # HTML-Bericht generieren
        '--cov-report=json:' + os.path.join(coverage_dir, 'coverage.json'),  # JSON-Bericht für Analyse
        os.path.join(base_dir, 'tests')  # Tests-Verzeichnis
    ]

    result = subprocess.run(cmd, cwd=base_dir)

    if result.returncode == 0:
        print("\nTests erfolgreich abgeschlossen!")
    else:
        print("\nEinige Tests sind fehlgeschlagen.")

    # HTML-Bericht öffnen
    html_report = os.path.join(coverage_dir, 'index.html')
    if os.path.exists(html_report):
        print(f"\nHTML-Coverage-Bericht generiert: {html_report}")
        print("Öffne Bericht im Standardbrowser...")
        webbrowser.open('file://' + html_report)
    else:
        print("\nFehler: HTML-Bericht wurde nicht generiert.")

    # Ergebnisse analysieren und fehlende Bereiche identifizieren
    analyze_coverage(coverage_dir)

    return result.returncode


def analyze_coverage(coverage_dir):
    """
    Analysiert den Coverage-Bericht und identifiziert fehlende Testbereiche.
    """
    try:
        # JSON-Bericht lesen
        coverage_json = os.path.join(coverage_dir, 'coverage.json')
        if not os.path.exists(coverage_json):
            print("\nKein JSON-Coverage-Bericht gefunden. Überspringe Analyse.")
            return

        with open(coverage_json, 'r') as f:
            data = json.load(f)

        if not data or 'files' not in data:
            print("\nKeine Daten im Coverage-Bericht gefunden. Überspringe Analyse.")
            return

        # Module mit niedriger Abdeckung identifizieren
        low_coverage_modules = []
        for file_path, file_data in data['files'].items():
            if file_data['summary']['percent_covered'] < 80:
                low_coverage_modules.append({
                    'path': file_path,
                    'coverage': file_data['summary']['percent_covered'],
                    'missing_lines': len(file_data['missing_lines'])
                })

        # Nach Abdeckung sortieren
        low_coverage_modules.sort(key=lambda x: x['coverage'])

        if low_coverage_modules:
            print("\nModule mit niedriger Testabdeckung (unter 80%):")
            for module in low_coverage_modules:
                print(
                    f"  - {module['path']}: {module['coverage']:.1f}% abgedeckt ({module['missing_lines']} fehlende Zeilen)")
        else:
            print("\nAlle Module haben eine Testabdeckung von mindestens 80%. Gut gemacht!")

        # Gesamtabdeckung berechnen
        if 'totals' in data and 'percent_covered' in data['totals']:
            total_coverage = data['totals']['percent_covered']
            print(f"\nGesamtabdeckung: {total_coverage:.1f}%")

            if total_coverage < 70:
                print("⚠️ Die Gesamtabdeckung ist unter 70%. Es wird empfohlen, mehr Tests hinzuzufügen.")
            elif total_coverage < 80:
                print("⚠️ Die Gesamtabdeckung ist unter 80%. Überlegen Sie, weitere Tests hinzuzufügen.")
            elif total_coverage < 90:
                print("✓ Gute Abdeckung, aber es gibt noch Raum für Verbesserungen.")
            else:
                print("✓✓ Ausgezeichnete Testabdeckung!")

    except Exception as e:
        print(f"\nFehler bei der Analyse des Coverage-Berichts: {e}")

    # Empfehlungen für Verbesserungen
    print("\nEmpfehlungen zur Verbesserung der Testabdeckung:")
    print("1. Fügen Sie Tests für die Web-Routen hinzu (z.B. mit dem aktualisierten test_web_routes.py)")
    print("2. Testen Sie alle Fehlerbedingungen und Edge Cases in den Datenbankfunktionen")
    print("3. Erweitern Sie die Tests für die raumbuch.py-Modelle")
    print("4. Testen Sie die Exportfunktionen mit temporären Dateien")
    print("5. Fügen Sie Tests für die Filterlogik in routes.py hinzu")


if __name__ == "__main__":
    sys.exit(run_tests_with_coverage())