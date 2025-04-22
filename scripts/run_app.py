#!/usr/bin/env python
"""
Skript zum Starten der RitterDigitalAuswertung Web-Anwendung.
"""

import os
import sys

# Füge das Hauptverzeichnis dem Python-Pfad hinzu, um Imports zu ermöglichen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import APP_CONFIG
from src.web.app import create_app


def main():
    """Startet die Flask-Webanwendung mit den konfigurierten Einstellungen."""
    app = create_app()

    # Starte die App
    app.run(
        host=APP_CONFIG['host'],
        port=APP_CONFIG['port'],
        debug=APP_CONFIG['debug']
    )

    print(f"Server läuft auf http://{APP_CONFIG['host']}:{APP_CONFIG['port']}")


if __name__ == "__main__":
    main()