"""
Tests für die Datenbankfunktionen der RitterDigitalAuswertung-Anwendung.
"""

import unittest
from unittest.mock import patch, MagicMock

from src.database.connection import (
    get_connection_string,
    get_db_connection,
    close_connection,
    test_connection
)
from src.database.queries import (
    get_raumbuch_data,
    get_standorte,
    get_standort_by_id
)
from config.database import DATABASE_CONFIG


class TestDatabaseConnection(unittest.TestCase):
    """Testklasse für die Datenbankverbindung."""

    def test_get_connection_string(self):
        """Test der get_connection_string-Funktion."""
        conn_str = get_connection_string()

        # Überprüfen, ob die wichtigen Bestandteile im Verbindungsstring enthalten sind
        self.assertIn(DATABASE_CONFIG['server'], conn_str)
        self.assertIn(DATABASE_CONFIG['database'], conn_str)
        self.assertIn(DATABASE_CONFIG['username'], conn_str)
        self.assertIn(DATABASE_CONFIG['password'], conn_str)
        self.assertIn(DATABASE_CONFIG['driver'], conn_str)

    @patch('pyodbc.connect')
    def test_get_db_connection(self, mock_connect):
        """Test der get_db_connection-Funktion."""
        # Mock für pyodbc.connect
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # Funktion testen
        conn = get_db_connection()

        # Überprüfen, ob pyodbc.connect aufgerufen wurde
        mock_connect.assert_called_once()

        # Überprüfen, ob die Funktion die Verbindung zurückgibt
        self.assertEqual(conn, mock_conn)

    @patch('pyodbc.connect')
    def test_close_connection(self, mock_connect):
        """Test der close_connection-Funktion."""
        # Mock für pyodbc.connect
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # Verbindung erstellen und schließen
        conn = get_db_connection()
        close_connection(conn)

        # Überprüfen, ob close aufgerufen wurde
        conn.close.assert_called_once()

    @patch('src.database.connection.db_connection')
    def test_test_connection(self, mock_db_connection):
        """Test der test_connection-Funktion."""
        # Mock für db_connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_connection.return_value.__enter__.return_value = mock_conn

        # Funktion testen
        result = test_connection()

        # Überprüfen, ob die Funktion True zurückgibt
        self.assertTrue(result)

        # Überprüfen, ob die notwendigen Funktionen aufgerufen wurden
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("SELECT 1")
        mock_cursor.fetchone.assert_called_once()

    @patch('src.database.connection.db_connection')
    def test_test_connection_error(self, mock_db_connection):
        """Test der test_connection-Funktion bei einem Fehler."""
        # Mock für db_connection mit Fehler
        mock_db_connection.side_effect = Exception("Test error")

        # Funktion testen
        result = test_connection()

        # Überprüfen, ob die Funktion False zurückgibt
        self.assertFalse(result)


class TestDatabaseQueries(unittest.TestCase):
    """Testklasse für die Datenbankabfragen."""

    @patch('src.database.queries.db_connection')
    def test_get_raumbuch_data(self, mock_db_connection):
        """Test der get_raumbuch_data-Funktion."""
        # Mock für db_connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_connection.return_value.__enter__.return_value = mock_conn

        # Mock für Cursor-Ergebnisse
        mock_cursor.description = [('ID',), ('Raumnummer',), ('Bereich',)]
        mock_cursor.fetchall.return_value = [(1, '101', 'Küche'), (2, '102', 'Büro')]

        # Funktion testen
        result = get_raumbuch_data(standort_id=1)

        # Überprüfen, ob die Funktion die erwarteten Ergebnisse zurückgibt
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['ID'], 1)
        self.assertEqual(result[0]['Raumnummer'], '101')
        self.assertEqual(result[0]['Bereich'], 'Küche')
        self.assertEqual(result[1]['ID'], 2)
        self.assertEqual(result[1]['Raumnummer'], '102')
        self.assertEqual(result[1]['Bereich'], 'Büro')

        # Überprüfen, ob die notwendigen Funktionen aufgerufen wurden
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_called_once()

    @patch('src.database.queries.db_connection')
    def test_get_standorte(self, mock_db_connection):
        """Test der get_standorte-Funktion."""
        # Mock für db_connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_connection.return_value.__enter__.return_value = mock_conn

        # Mock für Cursor-Ergebnisse
        mock_cursor.description = [('ID',), ('Bezeichnung',)]
        mock_cursor.fetchall.return_value = [(1, 'Standort 1'), (2, 'Standort 2')]

        # Funktion testen
        result = get_standorte()

        # Überprüfen, ob die Funktion die erwarteten Ergebnisse zurückgibt
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['ID'], 1)
        self.assertEqual(result[0]['Bezeichnung'], 'Standort 1')
        self.assertEqual(result[1]['ID'], 2)
        self.assertEqual(result[1]['Bezeichnung'], 'Standort 2')

        # Überprüfen, ob die notwendigen Funktionen aufgerufen wurden
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_called_once()

    @patch('src.database.queries.db_connection')
    def test_get_standort_by_id(self, mock_db_connection):
        """Test der get_standort_by_id-Funktion."""
        # Mock für db_connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_connection.return_value.__enter__.return_value = mock_conn

        # Mock für Cursor-Ergebnisse
        mock_cursor.description = [('ID',), ('Bezeichnung',)]
        mock_cursor.fetchone.return_value = (1, 'Standort 1')

        # Funktion testen
        result = get_standort_by_id(1)

        # Überprüfen, ob die Funktion die erwarteten Ergebnisse zurückgibt
        self.assertEqual(result['ID'], 1)
        self.assertEqual(result['Bezeichnung'], 'Standort 1')

        # Überprüfen, ob die notwendigen Funktionen aufgerufen wurden
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()

    @patch('src.database.queries.db_connection')
    def test_get_standort_by_id_not_found(self, mock_db_connection):
        """Test der get_standort_by_id-Funktion, wenn der Standort nicht gefunden wird."""
        # Mock für db_connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_connection.return_value.__enter__.return_value = mock_conn

        # Mock für Cursor-Ergebnisse (Standort nicht gefunden)
        mock_cursor.fetchone.return_value = None

        # Funktion testen
        result = get_standort_by_id(999)

        # Überprüfen, ob die Funktion None zurückgibt
        self.assertIsNone(result)

        # Überprüfen, ob die notwendigen Funktionen aufgerufen wurden
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()

if __name__ == '__main__':
    unittest.main()