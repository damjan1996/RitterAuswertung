import os
import subprocess
import sys


def create_directory(path):
    """Erstellt ein Verzeichnis, falls es nicht existiert."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Verzeichnis erstellt: {path}")


def create_empty_file(path):
    """Erstellt eine leere Datei, falls sie nicht existiert."""
    if not os.path.exists(path):
        with open(path, 'w') as f:
            pass
        print(f"Leere Datei erstellt: {path}")


def setup_project():
    # Basisverzeichnis
    base_dir = r"C:\Development\RitterDigitalAuswertung"
    create_directory(base_dir)

    # Wechseln ins Basisverzeichnis
    os.chdir(base_dir)

    # Verzeichnisse erstellen
    directories = [
        "config",
        "src",
        "src/database",
        "src/models",
        "src/analysis",
        "src/web",
        "src/web/static",
        "src/web/static/css",
        "src/web/static/js",
        "src/web/templates",
        "tests",
        "scripts"
    ]

    for directory in directories:
        create_directory(os.path.join(base_dir, directory))

    # Leere Dateien erstellen
    files = [
        "README.md",
        "requirements.txt",
        ".gitignore",
        "setup.py",
        "config/__init__.py",
        "config/database.py",
        "config/settings.py",
        "src/__init__.py",
        "src/database/__init__.py",
        "src/database/connection.py",
        "src/database/queries.py",
        "src/models/__init__.py",
        "src/models/raumbuch.py",
        "src/analysis/__init__.py",
        "src/analysis/raumbuch_analysis.py",
        "src/web/__init__.py",
        "src/web/app.py",
        "src/web/routes.py",
        "src/web/static/css/style.css",
        "src/web/static/js/main.js",
        "src/web/templates/base.html",
        "src/web/templates/index.html",
        "src/web/templates/report.html",
        "tests/__init__.py",
        "tests/test_database.py",
        "tests/test_analysis.py",
        "scripts/run_app.py"
    ]

    for file in files:
        create_empty_file(os.path.join(base_dir, file))

    # Git-Repository initialisieren
    try:
        subprocess.run(["git", "init"], check=True)
        print("Git-Repository initialisiert")

        # Remote hinzufügen
        subprocess.run(["git", "remote", "add", "origin", "https://github.com/damjan1996/RitterAuswertung.git"],
                       check=True)
        print("Remote-Repository hinzugefügt")

    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Ausführen des Git-Befehls: {e}")

    print("\nProjektstruktur-Setup abgeschlossen!")
    print(f"Projekt erstellt unter: {base_dir}")
    print("Nächste Schritte:")
    print("1. Navigiere zum Projektverzeichnis: cd " + base_dir)
    print("2. Beginne mit der Implementierung der Anwendung")


if __name__ == "__main__":
    setup_project()