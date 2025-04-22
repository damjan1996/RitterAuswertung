"""
Konfigurationsmodul für die RitterDigitalAuswertung-Anwendung.
Enthält Einstellungen für Datenbank und Anwendung.
"""

from config.database import DATABASE_CONFIG
from config.settings import APP_CONFIG

__all__ = ['DATABASE_CONFIG', 'APP_CONFIG']