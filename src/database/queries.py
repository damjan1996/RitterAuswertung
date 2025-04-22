"""
Modul mit Datenbankabfragen für die RitterDigitalAuswertung-Anwendung.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple

from config.database import RAUMBUCH_QUERY, STANDORTE_QUERY, DEFAULT_STANDORT_ID
from src.database.connection import db_connection

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def row_to_dict(cursor, row):
    """
    Konvertiert eine Zeile aus dem Cursor in ein Dictionary.

    Args:
        cursor: Der Cursor mit Spaltennamen
        row: Die zu konvertierende Zeile

    Returns:
        dict: Dictionary mit Spaltennamen als Schlüssel und Zeilenwerten
    """
    return {column[0]: value for column, value in zip(cursor.description, row)}


def get_raumbuch_data(standort_id: int = DEFAULT_STANDORT_ID) -> List[Dict[str, Any]]:
    """
    Ruft die Raumbuch-Daten für einen Standort ab.

    Args:
        standort_id (int): ID des Standorts, für den die Daten abgerufen werden sollen

    Returns:
        List[Dict[str, Any]]: Liste der Raumbuch-Daten als Dictionaries
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(RAUMBUCH_QUERY, (standort_id,))

            # Ergebnisse in Liste von Dictionaries konvertieren
            results = []
            for row in cursor.fetchall():
                results.append(row_to_dict(cursor, row))

            logger.info(f"Raumbuch-Daten für Standort {standort_id} erfolgreich abgerufen: {len(results)} Einträge")
            return results
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Raumbuch-Daten: {e}")
        return []


def get_standorte() -> List[Dict[str, Any]]:
    """
    Ruft alle verfügbaren Standorte ab.

    Returns:
        List[Dict[str, Any]]: Liste der Standorte als Dictionaries
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(STANDORTE_QUERY)

            # Ergebnisse in Liste von Dictionaries konvertieren
            results = []
            for row in cursor.fetchall():
                results.append(row_to_dict(cursor, row))

            logger.info(f"Standorte erfolgreich abgerufen: {len(results)} Einträge")
            return results
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Standorte: {e}")
        return []


def get_standort_by_id(standort_id: int) -> Optional[Dict[str, Any]]:
    """
    Ruft einen Standort anhand seiner ID ab.

    Args:
        standort_id (int): ID des Standorts

    Returns:
        Optional[Dict[str, Any]]: Standortinformationen oder None, falls nicht gefunden
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ID, Bezeichnung FROM BIRD.Standort WHERE ID = ?", (standort_id,))

            row = cursor.fetchone()
            if row:
                return row_to_dict(cursor, row)

            logger.warning(f"Standort mit ID {standort_id} nicht gefunden")
            return None
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Standorts: {e}")
        return None