"""
Tests für die Web-App-Funktionen der RitterDigitalAuswertung-Anwendung.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import flask

from src.web.app import create_app, render_error_page


class TestWebApp(unittest.TestCase):
    """Testklasse für die Web-App-Funktionen."""

    def setUp(self):
        """Testumgebung einrichten."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_create_app(self):
        """Test der create_app-Funktion."""
        app = create_app()

        # Überprüfen, ob eine Flask-Anwendung erstellt wurde
        self.assertIsInstance(app, flask.Flask)

        # Überprüfen, ob die Konfiguration korrekt ist
        self.assertIn('SECRET_KEY', app.config)
        self.assertIn('DEBUG', app.config)

    def test_context_processor(self):
        """Test des Kontext-Prozessors für Templates."""
        with self.app.test_request_context():
            # Zugriff auf die globalen Template-Variablen
            context = {}
            for processor in self.app.template_context_processors[None]:
                context.update(processor())

            # Überprüfen, ob die erwarteten Variablen vorhanden sind
            self.assertIn('current_year', context)
            self.assertIn('app_title', context)
            self.assertIn('app_version', context)

    def test_error_handlers(self):
        """Test der Fehlerbehandlung mit Error-Handlern."""
        # Test für 404-Fehler
        response = self.client.get('/nicht_existierende_seite')
        self.assertEqual(response.status_code, 404)

        # Test für unbewältigte Ausnahmen
        with self.app.test_request_context():
            with patch('flask.render_template') as mock_render:
                mock_render.return_value = "Fehlerseite"
                # render_error_page direkt aufrufen
                response, status = render_error_page('Testfehler', 500)

                # Überprüfen, ob render_template aufgerufen wurde
                mock_render.assert_called_once_with('error.html', message='Testfehler')

                # Überprüfen des Status-Codes
                self.assertEqual(status, 500)

    def test_page_not_found_handler(self):
        """Test des 404-Fehlerhandlers."""
        with self.app.test_request_context():
            # Eine 404-Exception manuell auslösen
            try:
                flask.abort(404)
            except Exception as e:
                # Den Fehlerhandler manuell aufrufen
                with patch('src.web.app.render_error_page') as mock_render:
                    mock_render.return_value = ("Fehlerseite", 404)
                    # page_not_found über die Exception aufrufen
                    for handler in self.app.error_handler_spec[None][404]:
                        handler(e)

                    # Überprüfen, ob render_error_page aufgerufen wurde
                    mock_render.assert_called_once()

    def test_server_error_handler(self):
        """Test des 500-Fehlerhandlers."""
        with self.app.test_request_context():
            # Eine 500-Exception manuell auslösen
            try:
                flask.abort(500)
            except Exception as e:
                # Den Fehlerhandler manuell aufrufen
                with patch('src.web.app.render_error_page') as mock_render:
                    mock_render.return_value = ("Fehlerseite", 500)
                    # server_error über die Exception aufrufen
                    for handler in self.app.error_handler_spec[None][500]:
                        handler(e)

                    # Überprüfen, ob render_error_page aufgerufen wurde
                    mock_render.assert_called_once()

    def test_handle_exception_handler(self):
        """Test des allgemeinen Exception-Handlers."""
        with self.app.test_request_context():
            # Eine Ausnahme erstellen
            test_exception = Exception("Testausnahme")

            # Den Fehlerhandler manuell aufrufen
            with patch('src.web.app.render_error_page') as mock_render:
                mock_render.return_value = ("Fehlerseite", 500)
                # Alle Exception-Handler durchgehen
                for code, handlers in self.app.error_handler_spec[None].items():
                    if code is None:  # Exception handler
                        for handler in handlers:
                            handler(test_exception)

                # Überprüfen, ob render_error_page aufgerufen wurde
                mock_render.assert_called_once()


if __name__ == '__main__':
    unittest.main()