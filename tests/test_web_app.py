"""
Tests für die Web-App-Funktionen der RitterDigitalAuswertung-Anwendung.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
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

    def test_404_response(self):
        """Test, ob 404-Fehler korrekt behandelt werden."""
        # Nicht existierende Route aufrufen
        response = self.client.get('/nicht-existierende-route')
        self.assertEqual(response.status_code, 404)
        # Auf Deutsch statt Englisch prüfen
        self.assertIn(b'fehler', response.data.lower())
        self.assertIn(b'nicht gefunden', response.data.lower())

    def test_error_route(self):
        """Test, ob eine Route, die einen Fehler auslöst, korrekt behandelt wird."""
        # Definiere eine Test-Route, die einen Fehler auslöst
        @self.app.route('/test-error-route')
        def test_error_route():
            # Einen Fehler auslösen
            raise Exception("Test Exception")

        # Route aufrufen
        response = self.client.get('/test-error-route')

        # Überprüfen des Status-Codes
        self.assertEqual(response.status_code, 500)
        # Auf Deutsch statt Englisch prüfen
        self.assertIn(b'fehler', response.data.lower())
        self.assertIn(b'aufgetreten', response.data.lower())

    def test_custom_error_in_route(self):
        """Test, ob benutzerdefinierte Fehler in Routen korrekt behandelt werden."""
        # Eine spezielle Testroute hinzufügen, die die render_error_page-Funktion direkt aufruft
        @self.app.route('/custom-error')
        def custom_error():
            return render_error_page("Benutzerdefinierter Testfehler", 418)

        # Die Route aufrufen
        response = self.client.get('/custom-error')

        # Der Status-Code sollte der angeforderte sein
        self.assertEqual(response.status_code, 418)
        # Die Seite sollte den Fehlertext enthalten
        self.assertIn(b'Benutzerdefinierter Testfehler', response.data)


if __name__ == '__main__':
    unittest.main()