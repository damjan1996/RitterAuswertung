"""
Datenbankmodul für die RitterDigitalAuswertung-Anwendung.
Stellt Funktionen für die Datenbankverbindung und -abfragen bereit.
"""

from src.database.connection import get_db_connection, close_connection
from src.database.queries import (
    get_raumbuch_data,
    get_standorte,
    get_standort_by_id
)

__all__ = [
    'get_db_connection',
    'close_connection',
    'get_raumbuch_data',
    'get_standorte',
    'get_standort_by_id'
]