"""
Erweiterte Tests für die Web-Routen der RitterDigitalAuswertung-Anwendung.
Fokus auf bisher nicht getestete Funktionen.
"""

import unittest
from unittest.mock import patch, MagicMock, ANY
import json
import io

from src.web.app import create_app
from src.web.routes import apply_filters, create_filter_options, preprocess_data

class TestWebRoutesExtended(unittest.TestCase):
    """Erweiterte Testklasse für die Web-Routen."""

    def setUp(self):
        """Testumgebung einrichten."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Test-Daten
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
                'qmStunde': 187.0
            },
            {
                'ID': 2,
                'Raumnummer': '102',
                'Bereich': 'Büro',
                'Gebaeudeteil': 'Nebengebäude',
                'Etage': '1. OG',
                'Bezeichnung': 'Büro',
                'RG': 'B',
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
                'qmStunde': 191.0
            }
        ]

    def test_preprocess_data(self):
        """Test der preprocess_data-Funktion."""
        # Testdaten mit NULL-Werten
        data_with_nulls = [
            {
                'ID': 3,
                'Raumnummer': '103',
                'Bereich': 'Flur',
                'Gebaeudeteil': None,
                'Etage': 'EG',
                'RG': 'A',
                'qm': None,
                'WertMonat': None,
                'StundenTag': 'ungültig'  # Ungültiger Wert (nicht numerisch)
            }
        ]

        # Vorverarbeitung ausführen
        result = preprocess_data(data_with_nulls)

        # Überprüfen, ob NULL-Werte korrekt behandelt wurden
        self.assertEqual(result[0]['ID'], 3)
        self.assertEqual(result[0]['qm'], 0.0)  # NULL zu 0.0 konvertiert
        self.assertEqual(result[0]['WertMonat'], 0.0)  # NULL zu 0.0 konvertiert
        self.assertEqual(result[0]['StundenTag'], 0.0)  # Ungültiger Wert zu 0.0 konvertiert
        self.assertIsNone(result[0]['Gebaeudeteil'])  # Textfeld bleibt None

    def test_apply_filters_without_filters(self):
        """Test von apply_filters ohne aktive Filter."""
        # ImmutableMultiDict simulieren
        class MockArgs:
            def __init__(self, args_dict):
                self._dict = args_dict

            def get(self, key):
                return self._dict.get(key)

            def __len__(self):
                return len(self._dict)

        # Keine Filter (nur standort_id)
        args = MockArgs({'standort_id': '1'})
        result = apply_filters(self.test_raumbuch_data, args)

        # Sollte die ursprünglichen Daten unverändert zurückgeben
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['ID'], 1)
        self.assertEqual(result[1]['ID'], 2)

    def test_apply_filters_with_filters(self):
        """Test von apply_filters mit verschiedenen Filtern."""
        # ImmutableMultiDict simulieren
        class MockArgs:
            def __init__(self, args_dict):
                self._dict = args_dict

            def get(self, key):
                return self._dict.get(key)

            def __len__(self):
                return len(self._dict)

        # Filter nach Bereich
        args_bereich = MockArgs({'standort_id': '1', 'bereich': 'Küche'})
        result_bereich = apply_filters(self.test_raumbuch_data, args_bereich)
        self.assertEqual(len(result_bereich), 1)
        self.assertEqual(result_bereich[0]['ID'], 1)

        # Filter nach Gebäudeteil
        args_gebaeudeteil = MockArgs({'standort_id': '1', 'gebaeudeteil': 'Nebengebäude'})
        result_gebaeudeteil = apply_filters(self.test_raumbuch_data, args_gebaeudeteil)
        self.assertEqual(len(result_gebaeudeteil), 1)
        self.assertEqual(result_gebaeudeteil[0]['ID'], 2)

        # Filter nach Etage
        args_etage = MockArgs({'standort_id': '1', 'etage': '1. OG'})
        result_etage = apply_filters(self.test_raumbuch_data, args_etage)
        self.assertEqual(len(result_etage), 1)
        self.assertEqual(result_etage[0]['ID'], 2)

        # Filter nach Reinigungsgruppe
        args_rg = MockArgs({'standort_id': '1', 'rg': 'C'})
        result_rg = apply_filters(self.test_raumbuch_data, args_rg)
        self.assertEqual(len(result_rg), 1)
        self.assertEqual(result_rg[0]['ID'], 1)

        # Kombinierte Filter
        args_combined = MockArgs({
            'standort_id': '1',
            'bereich': 'Büro',
            'etage': '1. OG',
            'rg': 'B'
        })
        result_combined = apply_filters(self.test_raumbuch_data, args_combined)
        self.assertEqual(len(result_combined), 1)
        self.assertEqual(result_combined[0]['ID'], 2)

        # Filter ohne Ergebnis
        args_no_match = MockArgs({'standort_id': '1', 'bereich': 'Nicht existierend'})
        result_no_match = apply_filters(self.test_raumbuch_data, args_no_match)
        self.assertEqual(len(result_no_match), 0)

    def test_create_filter_options(self):
        """Test der create_filter_options-Funktion."""
        # Funktion testen
        filter_options = create_filter_options(self.test_raumbuch_data)

        # Prüfen, ob alle erwarteten Optionen vorhanden sind
        self.assertIn('bereiche', filter_options)
        self.assertIn('gebaeudeteil', filter_options)
        self.assertIn('etage', filter_options)
        self.assertIn('rg', filter_options)

        # Prüfen, ob die Werte korrekt sind
        self.assertEqual(sorted(filter_options['bereiche']), ['Büro', 'Küche'])
        self.assertEqual(sorted(filter_options['gebaeudeteil']), ['Hauptgebäude', 'Nebengebäude'])
        self.assertEqual(sorted(filter_options['etage']), ['1. OG', 'EG'])
        self.assertEqual(sorted(filter_options['rg']), ['B', 'C'])

    def test_export_excel_errors(self):
        """Test der Excel-Export-Route mit Fehlerbedingungen."""
        # Standort nicht gefunden
        with patch('src.web.routes.get_standort_by_id', return_value=None):
            response = self.client.get('/export/excel/999')
            self.assertEqual(response.status_code, 302)  # Redirect

        # Export-Fehler
        with patch('src.web.routes.get_standort_by_id', return_value={'ID': 1, 'Bezeichnung': 'Test'}), \
             patch('src.web.routes.get_raumbuch_data', return_value=[]), \
             patch('src.web.routes.export_to_excel', return_value=None):
            response = self.client.get('/export/excel/1')
            self.assertEqual(response.status_code, 302)  # Redirect

    def test_export_pdf_errors(self):
        """Test der PDF-Export-Route mit Fehlerbedingungen."""
        # Standort nicht gefunden
        with patch('src.web.routes.get_standort_by_id', return_value=None):
            response = self.client.get('/export/pdf/999')
            self.assertEqual(response.status_code, 302)  # Redirect

        # Export-Fehler
        with patch('src.web.routes.get_standort_by_id', return_value={'ID': 1, 'Bezeichnung': 'Test'}), \
             patch('src.web.routes.get_raumbuch_data', return_value=[]), \
             patch('src.web.routes.export_to_pdf', return_value=None):
            response = self.client.get('/export/pdf/1')
            self.assertEqual(response.status_code, 302)  # Redirect

    def test_index_with_data(self):
        """Test der Startseite mit ausgewähltem Standort und Daten."""
        # Vollständigeres Mock-Objekt für summary erstellen
        mock_summary = {
            'total_rooms': 2,
            'total_qm': 35.8,
            'total_qm_monat': 155.02,
            'total_wert_monat': 17.15,
            'total_wert_jahr': 205.8,
            'total_stunden_monat': 0.82,
            'bereich_stats': [
                {'Bereich': 'Küche', 'qm': 20.5, 'WertMonat': 9.82, 'WertJahr': 117.84},
                {'Bereich': 'Büro', 'qm': 15.3, 'WertMonat': 7.33, 'WertJahr': 87.96}
            ],
            'rg_stats': [
                {'RG': 'C', 'qm': 20.5, 'WertMonat': 9.82},
                {'RG': 'B', 'qm': 15.3, 'WertMonat': 7.33}
            ]
        }

        # Visualisierungsdaten für das Template
        viz_data = {
            'bereich_data': {'Küche': 20.5, 'Büro': 15.3},
            'rg_data': {'C': 9.82, 'B': 7.33},
            'etage_data': {'EG': 0.47, '1. OG': 0.35}
        }

        with patch('src.web.routes.get_standorte', return_value=[{'ID': 1, 'Bezeichnung': 'Test'}]), \
             patch('src.web.routes.get_standort_by_id', return_value={'ID': 1, 'Bezeichnung': 'Test'}), \
             patch('src.web.routes.get_raumbuch_data', return_value=self.test_raumbuch_data), \
             patch('src.web.routes.preprocess_data', return_value=self.test_raumbuch_data), \
             patch('src.web.routes.calculate_summary', return_value=mock_summary), \
             patch('src.web.routes.prepare_data_for_visualization', return_value=viz_data):

            response = self.client.get('/?standort_id=1')

            # Erfolgreicher Request
            self.assertEqual(response.status_code, 200)
            # Überprüfen, ob die Zusammenfassung angezeigt wird
            self.assertIn(b'Zusammenfassung', response.data)

    def test_index_with_error(self):
        """Test der Startseite mit einem Fehler während der Datenverarbeitung."""
        with patch('src.web.routes.get_standorte', return_value=[{'ID': 1, 'Bezeichnung': 'Test'}]), \
             patch('src.web.routes.get_standort_by_id', return_value={'ID': 1, 'Bezeichnung': 'Test'}), \
             patch('src.web.routes.get_raumbuch_data', side_effect=Exception("Testfehler")):

            response = self.client.get('/?standort_id=1')

            # Erfolgreicher Request trotz Fehler
            self.assertEqual(response.status_code, 200)
            # Flash-Nachricht mit Fehler sollte gezeigt werden
            self.assertIn(b'Fehler beim Laden der Daten', response.data)

if __name__ == '__main__':
    unittest.main()