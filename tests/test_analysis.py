"""
Tests für die Analysefunktionen der RitterDigitalAuswertung-Anwendung.
"""

import unittest
from unittest.mock import patch, MagicMock, ANY
import os
import tempfile

from src.analysis.raumbuch_analysis import (
    calculate_summary,
    prepare_data_for_visualization,
    export_to_excel,
    export_to_pdf,
    safe_number
)

class TestAnalysis(unittest.TestCase):
    """Testklasse für die Analysefunktionen."""

    def setUp(self):
        """Testdaten für die Tests erstellen."""
        self.test_data = [
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

        # Testdaten mit NULL-Werten
        self.test_data_with_nulls = [
            {
                'ID': 3,
                'Raumnummer': '103',
                'Bereich': 'Flur',
                'Gebaeudeteil': 'Hauptgebäude',
                'Etage': 'EG',
                'Bezeichnung': 'Flur',
                'RG': 'C',
                'qm': None,  # NULL-Wert
                'Anzahl': 1,
                'Intervall': 'Woche',
                'RgJahr': 52.0,
                'RgMonat': None,  # NULL-Wert
                'qmMonat': None,  # NULL-Wert
                'WertMonat': 5.0,
                'StundenTag': None,  # NULL-Wert
                'StundenMonat': 0.2,
                'WertJahr': 60.0,
                'qmStunde': None,  # NULL-Wert
                'Reinigungstage': None,
                'Bemerkung': None,
                'Reduzierung': None
            }
        ]

    def test_calculate_summary(self):
        """Test der calculate_summary-Funktion."""
        summary = calculate_summary(self.test_data)

        # Überprüfen, ob die Schlüssel im Summary-Dictionary vorhanden sind
        self.assertIn('total_rooms', summary)
        self.assertIn('total_qm', summary)
        self.assertIn('total_wert_monat', summary)
        self.assertIn('total_wert_jahr', summary)
        self.assertIn('total_stunden_monat', summary)

        # Überprüfen der berechneten Werte
        self.assertEqual(summary['total_rooms'], 2)
        self.assertAlmostEqual(summary['total_qm'], 35.8, places=1)
        self.assertAlmostEqual(summary['total_wert_monat'], 17.15, places=2)
        self.assertAlmostEqual(summary['total_wert_jahr'], 205.8, places=1)
        self.assertAlmostEqual(summary['total_stunden_monat'], 0.82, places=2)

    def test_calculate_summary_with_nulls(self):
        """Test der calculate_summary-Funktion mit NULL-Werten."""
        # Kombinierte Daten mit NULL-Werten
        combined_data = self.test_data + self.test_data_with_nulls

        # Test ausführen
        summary = calculate_summary(combined_data)

        # Überprüfen, dass NULL-Werte korrekt behandelt werden
        self.assertEqual(summary['total_rooms'], 3)
        self.assertAlmostEqual(summary['total_qm'], 35.8, places=1)  # Nur die nicht-NULL-Werte werden summiert
        self.assertAlmostEqual(summary['total_wert_monat'], 22.15, places=2)  # 17.15 + 5.0
        self.assertAlmostEqual(summary['total_wert_jahr'], 265.8, places=1)  # 205.8 + 60.0
        self.assertAlmostEqual(summary['total_stunden_monat'], 1.02, places=2)  # 0.82 + 0.2

    def test_prepare_data_for_visualization(self):
        """Test der prepare_data_for_visualization-Funktion."""
        viz_data = prepare_data_for_visualization(self.test_data)

        # Überprüfen, ob die Schlüssel im Viz-Data-Dictionary vorhanden sind
        self.assertIn('bereich_data', viz_data)
        self.assertIn('rg_data', viz_data)
        self.assertIn('etage_data', viz_data)

        # Überprüfen der berechneten Werte
        self.assertEqual(len(viz_data['bereich_data']), 2)
        self.assertEqual(len(viz_data['rg_data']), 1)
        self.assertEqual(len(viz_data['etage_data']), 1)

        self.assertAlmostEqual(viz_data['bereich_data']['Küche'], 20.5, places=1)
        self.assertAlmostEqual(viz_data['bereich_data']['Büro'], 15.3, places=1)
        self.assertAlmostEqual(viz_data['rg_data']['C'], 17.15, places=2)
        self.assertAlmostEqual(viz_data['etage_data']['EG'], 0.82, places=2)

    def test_safe_number(self):
        """Test der safe_number-Funktion."""
        # Test mit gültigen Zahlen
        self.assertEqual(safe_number(10), 10.0)
        self.assertEqual(safe_number(3.14), 3.14)
        self.assertEqual(safe_number("5.5"), 5.5)

        # Test mit NULL-Werten und ungültigen Werten
        self.assertEqual(safe_number(None), 0.0)
        self.assertEqual(safe_number(None, 1.0), 1.0)  # Eigener Default-Wert
        self.assertEqual(safe_number("nicht_numerisch"), 0.0)
        self.assertEqual(safe_number(""), 0.0)

    @patch('pandas.DataFrame')
    @patch('pandas.ExcelWriter')
    @patch('os.path.dirname')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('os.path.join')
    def test_export_to_excel(self, mock_join, mock_exists, mock_makedirs, mock_dirname, mock_writer_class, mock_dataframe):
        """Test der export_to_excel-Funktion mit umfangreicheren Mocks."""
        # Erstellen von Mock-Objekten
        mock_writer = MagicMock()
        mock_writer_instance = MagicMock()
        mock_writer_class.return_value.__enter__.return_value = mock_writer_instance
        mock_dirname.return_value = '/fake/path'
        mock_exists.return_value = True

        # Mock für os.path.join
        def fake_join(*args):
            # Für Excel-Pfad einen gültigen String zurückgeben
            return '/fake/path/excel_file.xlsx'
        mock_join.side_effect = fake_join

        # Mock für DataFrame
        mock_df_instance = MagicMock()
        mock_dataframe.return_value = mock_df_instance

        # Mock für ExcelWriter
        mock_book = MagicMock()
        mock_writer_instance.book = mock_book
        mock_writer_instance.sheets = {'sheet1': MagicMock()}

        # Zeitstempel und Dateinamen simulieren
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = '20250422_123456'

            # Spezifischen EXPORT_CONFIG patchen
            with patch('src.analysis.raumbuch_analysis.EXPORT_CONFIG',
                      {'excel': {'folder': '/fake/path'}}):

                # Exportfunktion aufrufen
                result = export_to_excel(self.test_data, 'Teststandort')

        # Prüfen, ob das Ergebnis der erwartete Pfad ist
        self.assertEqual(result, '/fake/path/excel_file.xlsx')

        # Überprüfen, ob die grundlegenden Funktionen aufgerufen wurden
        mock_makedirs.assert_called_once_with('/fake/path', exist_ok=True)
        mock_writer_class.assert_called_once()
        mock_dataframe.assert_called()  # DataFrame wurde erstellt

    @patch('pdfkit.from_string')
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('os.path.join')
    def test_export_to_pdf(self, mock_join, mock_makedirs, mock_exists, mock_pdfkit):
        """Test der export_to_pdf-Funktion mit verbesserten Mocks."""
        # Mocks konfigurieren
        mock_exists.return_value = True

        # Mock für os.path.join
        def fake_join(*args):
            # Einen gültigen Pfad zurückgeben
            if 'charts' in args:
                return '/fake/path/charts/chart.png'
            return '/fake/path/pdf_file.pdf'
        mock_join.side_effect = fake_join

        # Mock für das Template
        with patch('jinja2.Environment.get_template') as mock_get_template:
            mock_template = MagicMock()
            mock_template.render.return_value = '<html>Test</html>'
            mock_get_template.return_value = mock_template

            # Zeitstempel simulieren
            with patch('datetime.datetime') as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = '20250422_123456'

                # Exportfunktion aufrufen
                with patch('src.analysis.raumbuch_analysis.EXPORT_CONFIG',
                          {'pdf': {'folder': '/fake/path'}}):
                    result = export_to_pdf(self.test_data, 'Teststandort')

        # Prüfen, ob das Ergebnis der erwartete Pfad ist
        self.assertEqual(result, '/fake/path/pdf_file.pdf')

        # Überprüfen, ob die grundlegenden Funktionen aufgerufen wurden
        mock_makedirs.assert_called()
        mock_pdfkit.assert_called_once()
        mock_template.render.assert_called_once()

if __name__ == '__main__':
    unittest.main()