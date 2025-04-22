"""
Tests für die Web-Routen der RitterDigitalAuswertung-Anwendung.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
import tempfile

from src.web.app import create_app

class TestWebRoutes(unittest.TestCase):
    """Testklasse für die Web-Routen."""

    def setUp(self):
        """Testumgebung einrichten."""
        # Test-Konfiguration
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Test-Daten
        self.test_standorte = [
            {'ID': 1, 'Bezeichnung': 'Standort 1'},
            {'ID': 2, 'Bezeichnung': 'Standort 2'},
            {'ID': 3, 'Bezeichnung': 'Standort 3'}
        ]

        self.test_raumbuch_data = [
            {
                'ID': 1,
                'Raumnummer': '101',
                'Bereich': 'Küche',
                'Gebaeudeteil': 'Hauptgebäude',
                'Etage': 'EG',
                'Bezeichnung': 'Besprechungsraum',
                'RG': 'C',
                'qm': 20.5,
                'Anzahl': 1,
                'Intervall': 'Woche',
                'RgJahr': 52.0,
                'RgMonat': 4.33,
                'qmMonat': 88.77,
                'WertMonat': 9.82,
                'StundenTag': 0.11,
                'StundenMonat': 0.47,
                'WertJahr': 117.84,
                'qmStunde': 187.0,
                'Reinigungstage': None,
                'Bemerkung': None,
                'Reduzierung': None
            },
            {
                'ID': 2,
                'Raumnummer': '102',
                'Bereich': 'Büro',
                'Gebaeudeteil': 'Hauptgebäude',
                'Etage': 'EG',
                'Bezeichnung': 'Büro',
                'RG': 'C',
                'qm': 15.3,
                'Anzahl': 1,
                'Intervall': 'Woche',
                'RgJahr': 52.0,
                'RgMonat': 4.33,
                'qmMonat': 66.25,
                'WertMonat': 7.33,
                'StundenTag': 0.08,
                'StundenMonat': 0.35,
                'WertJahr': 87.96,
                'qmStunde': 191.0,
                'Reinigungstage': None,
                'Bemerkung': None,
                'Reduzierung': None
            }
        ]

    def test_index_route(self):
        """Test der Startseiten-Route."""
        with patch('src.web.routes.get_standorte', return_value=self.test_standorte):
            response = self.client.get('/')

            # Überprüfen des HTTP-Status
            self.assertEqual(response.status_code, 200)

            # Überprüfen, ob der Titel auf der Seite erscheint
            self.assertIn(b'Ritter Digital Raumbuch Auswertung', response.data)

    def test_report_route_without_standort(self):
        """Test der Report-Route ohne ausgewählten Standort."""
        with patch('src.web.routes.get_standorte', return_value=self.test_standorte):
            response = self.client.get('/report')

            # Überprüfen des HTTP-Status
            self.assertEqual(response.status_code, 200)

            # Überprüfen, ob die Info-Meldung erscheint
            self.assertIn(b'Bitte w\xc3\xa4hlen Sie einen Standort aus', response.data)

    def test_report_route_with_standort(self):
        """Test der Report-Route mit ausgewähltem Standort."""
        with patch('src.web.routes.get_standorte', return_value=self.test_standorte), \
             patch('src.web.routes.get_standort_by_id', return_value=self.test_standorte[0]), \
             patch('src.web.routes.get_raumbuch_data', return_value=self.test_raumbuch_data), \
             patch('src.web.routes.preprocess_data', return_value=self.test_raumbuch_data), \
             patch('src.web.routes.apply_filters', return_value=self.test_raumbuch_data), \
             patch('src.web.routes.calculate_summary') as mock_summary, \
             patch('src.web.routes.prepare_data_for_visualization') as mock_viz, \
             patch('src.web.routes.create_filter_options') as mock_filter:

            # Mocks für die Summary- und Visualisierungsdaten
            mock_summary.return_value = {
                'total_rooms': 2,
                'total_qm': 35.8,
                'total_wert_monat': 17.15,
                'total_wert_jahr': 205.8,
                'total_stunden_monat': 0.82
            }
            mock_viz.return_value = {
                'bereich_data': {'Küche': 20.5, 'Büro': 15.3},
                'rg_data': {'C': 17.15},
                'etage_data': {'EG': 0.82}
            }
            mock_filter.return_value = {
                'bereiche': ['Büro', 'Küche'],
                'gebaeudeteil': ['Hauptgebäude'],
                'etage': ['EG'],
                'rg': ['C']
            }

            response = self.client.get('/report?standort_id=1')

            # Überprüfen des HTTP-Status
            self.assertEqual(response.status_code, 200)

            # Überprüfen, ob die Daten korrekt angezeigt werden
            self.assertIn(b'Raumbuch Auswertung', response.data)

            # Aufrufe überprüfen
            mock_summary.assert_called_once()
            mock_viz.assert_called_once()
            mock_filter.assert_called_once()

    def test_api_standorte(self):
        """Test der API-Route für Standorte."""
        with patch('src.web.routes.get_standorte', return_value=self.test_standorte):
            response = self.client.get('/api/standorte')

            # Überprüfen des HTTP-Status
            self.assertEqual(response.status_code, 200)

            # Überprüfen des Inhalts (JSON-Format)
            data = json.loads(response.data)
            self.assertEqual(len(data), 3)
            self.assertEqual(data[0]['ID'], 1)
            self.assertEqual(data[0]['Bezeichnung'], 'Standort 1')

    def test_export_excel(self):
        """Test der Excel-Export-Route."""
        # Temporäre Excel-Datei für den Test (Windows-kompatibel)
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            test_excel_path = temp_file.name

        try:
            with patch('src.web.routes.get_standort_by_id', return_value=self.test_standorte[0]), \
                 patch('src.web.routes.get_raumbuch_data', return_value=self.test_raumbuch_data), \
                 patch('src.web.routes.preprocess_data', return_value=self.test_raumbuch_data), \
                 patch('src.web.routes.apply_filters', return_value=self.test_raumbuch_data), \
                 patch('src.web.routes.export_to_excel', return_value=test_excel_path), \
                 patch('src.web.routes.send_file', return_value=MagicMock()) as mock_send_file, \
                 patch('src.web.routes.os.path.exists', return_value=True):

                # Excel-Export aufrufen
                response = self.client.get('/export/excel/1')

                # Überprüfen, ob die Funktion aufgerufen wurde
                mock_send_file.assert_called_once()
        finally:
            # Aufräumen
            if os.path.exists(test_excel_path):
                os.unlink(test_excel_path)

    def test_export_pdf(self):
        """Test der PDF-Export-Route."""
        # Temporäre PDF-Datei für den Test (Windows-kompatibel)
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            test_pdf_path = temp_file.name

        try:
            with patch('src.web.routes.get_standort_by_id', return_value=self.test_standorte[0]), \
                 patch('src.web.routes.get_raumbuch_data', return_value=self.test_raumbuch_data), \
                 patch('src.web.routes.preprocess_data', return_value=self.test_raumbuch_data), \
                 patch('src.web.routes.apply_filters', return_value=self.test_raumbuch_data), \
                 patch('src.web.routes.prepare_data_for_visualization', return_value={}), \
                 patch('src.web.routes.export_to_pdf', return_value=test_pdf_path), \
                 patch('src.web.routes.send_file', return_value=MagicMock()) as mock_send_file, \
                 patch('src.web.routes.os.path.exists', return_value=True):

                # PDF-Export aufrufen
                response = self.client.get('/export/pdf/1')

                # Überprüfen, ob die Funktion aufgerufen wurde
                mock_send_file.assert_called_once()
        finally:
            # Aufräumen
            if os.path.exists(test_pdf_path):
                os.unlink(test_pdf_path)

    def test_standort_not_found(self):
        """Test für den Fall, dass ein Standort nicht gefunden wird."""
        with patch('src.web.routes.get_standorte', return_value=self.test_standorte), \
             patch('src.web.routes.get_standort_by_id', return_value=None):

            response = self.client.get('/report?standort_id=999')

            # Überprüfen des HTTP-Status
            self.assertEqual(response.status_code, 200)

            # Es sollte eine Fehlermeldung angezeigt werden
            self.assertIn(b'Bitte w\xc3\xa4hlen Sie einen Standort aus', response.data)

    def test_invalid_standort_id(self):
        """Test für den Fall einer ungültigen Standort-ID."""
        with patch('src.web.routes.get_standorte', return_value=self.test_standorte):
            response = self.client.get('/report?standort_id=abc')  # Keine Zahl

            # Überprüfen des HTTP-Status
            self.assertEqual(response.status_code, 200)

            # Es sollte eine Fehlermeldung angezeigt werden
            self.assertIn(b'Bitte w\xc3\xa4hlen Sie einen Standort aus', response.data)

if __name__ == '__main__':
    unittest.main()