"""
Modul zur Verwaltung der Datenbankverbindungen.
"""

import pyodbc
import logging
from contextlib import contextmanager

from config.database import DATABASE_CONFIG

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_connection_string():
    """
    Erstellt einen Verbindungsstring für pyodbc basierend auf der Datenbankkonfiguration.

    Returns:
        str: Verbindungsstring für pyodbc
    """
    config = DATABASE_CONFIG
    conn_str = (
        f"DRIVER={config['driver']};"
        f"SERVER={config['server']};"
        f"DATABASE={config['database']};"
        f"UID={config['username']};"
        f"PWD={config['password']};"
        f"Trusted_Connection={config['trusted_connection']};"
        f"timeout={config['timeout']};"
    )
    logger.info(f"Verbindungsstring erstellt: SERVER={config['server']};DATABASE={config['database']}")
    return conn_str

def get_db_connection():
    """
    Stellt eine Verbindung zur Datenbank her.

    Returns:
        pyodbc.Connection: Datenbankverbindung

    Raises:
        Exception: Wenn die Verbindung fehlschlägt
    """
    try:
        conn_str = get_connection_string()
        logger.info("Versuche Verbindung zur Datenbank herzustellen...")
        conn = pyodbc.connect(conn_str)
        logger.info("Datenbankverbindung erfolgreich hergestellt")
        return conn
    except pyodbc.Error as e:
        logger.error(f"Fehler beim Verbindungsaufbau: {e}")
        raise Exception(f"Datenbankverbindung fehlgeschlagen: {e}")

def close_connection(conn):
    """
    Schließt eine Datenbankverbindung.

    Args:
        conn (pyodbc.Connection): Zu schließende Datenbankverbindung
    """
    if conn:
        try:
            conn.close()
            logger.info("Datenbankverbindung geschlossen")
        except pyodbc.Error as e:
            logger.error(f"Fehler beim Schließen der Verbindung: {e}")

@contextmanager
def db_connection():
    """
    Context Manager für die Datenbankverbindung.
    Verwendet with-Statement für automatisches Schließen der Verbindung.

    Yields:
        pyodbc.Connection: Datenbankverbindung
    """
    conn = None
    try:
        conn = get_db_connection()
        yield conn
    finally:
        if conn:
            close_connection(conn)

def test_connection():
    """
    Testet die Datenbankverbindung.

    Returns:
        bool: True, wenn die Verbindung erfolgreich ist, sonst False
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            logger.info("Verbindungstest erfolgreich")
            return True
    except Exception as e:
        logger.error(f"Verbindungstest fehlgeschlagen: {e}")
        return False