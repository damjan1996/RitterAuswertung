"""
Korrekturen für die Fehlerbehandlungs-Tests.
Diese verbesserte Version testet die Fehlerbehandlung über die API statt interne Flask-Strukturen.
"""

import unittest
from unittest.mock import patch, MagicMock
from werkzeug.exceptions import NotFound, InternalServerError

from src.web.app import create_app, render_error_page


class TestAppErrorHandling(unittest.TestCase):
    """Überarbeitete Testklasse für die Fehlerbehandlung in der App."""

    def setUp(self):
        """Testumgebung einrichten."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_render_error_page_with_different_messages(self):
        """Test der render_error_page-Funktion mit verschiedenen Nachrichten."""
        with self.app.test_request_context():
            # 404-Fehler
            with patch('flask.render_template') as mock_render:
                mock_render.return_value = "404 Seite"
                response, status = render_error_page('Seite nicht gefunden', 404)
                mock_render.assert_called_once_with('error.html', message='Seite nicht gefunden')
                self.assertEqual(status, 404)

            # 500-Fehler
            with patch('flask.render_template') as mock_render:
                mock_render.return_value = "500 Seite"
                response, status = render_error_page('Serverfehler', 500)
                mock_render.assert_called_once_with('error.html', message='Serverfehler')
                self.assertEqual(status, 500)

    def test_error_page_rendering(self):
        """Test, ob die Fehlerseite korrekt gerendert wird."""
        # Die nicht existierende Route aufrufen (erzeugt 404)
        response = self.client.get('/test-error-nicht-existierend')

        # Prüfen des Status-Codes und Inhalts - auf Deutsch statt Englisch prüfen
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'fehler', response.data.lower())
        self.assertIn(b'nicht gefunden', response.data.lower())

    def test_server_error_logging(self):
        """Test, ob Serverfehler korrekt protokolliert werden."""
        # Definieren einer neuen Route, die direkt einen 500-Fehler auslöst
        @self.app.route('/trigger-server-error')
        def trigger_server_error():
            # Absichtlich einen Fehler auslösen
            raise Exception("Manuell ausgelöster Serverfehler für Tests")

        # Mock für den Logger erstellen
        with patch('src.web.app.logger') as mock_logger:
            # Die Route aufrufen
            response = self.client.get('/trigger-server-error')

            # Prüfen, ob der Logger aufgerufen wurde (mit irgendeinem Fehler)
            mock_logger.error.assert_called()
            self.assertEqual(response.status_code, 500)

    def test_unhandled_exception_logging(self):
        """Test, ob unbehandelte Ausnahmen korrekt protokolliert werden."""
        # Eine Route definieren, die eine Exception auslöst
        @self.app.route('/unhandled-exception')
        def unhandled_exception():
            # Absichtlich eine Exception auslösen
            1/0  # ZeroDivisionError
            return "Diese Zeile wird nie erreicht"

        # Mock für den Logger erstellen
        with patch('src.web.app.logger') as mock_logger:
            # Die Route aufrufen
            response = self.client.get('/unhandled-exception')

            # Prüfen, ob der Logger aufgerufen wurde
            mock_logger.error.assert_called()
            # Prüfen, ob die Antwort einen 500 Server-Fehler enthält
            self.assertEqual(response.status_code, 500)

if __name__ == '__main__':
    unittest.main()