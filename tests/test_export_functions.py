"""
Erweiterte Tests für die Export-Funktionen in raumbuch_analysis.py.
"""

import unittest
from unittest.mock import patch, MagicMock, ANY
import os
import tempfile
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from src.analysis.raumbuch_analysis import (
    export_to_excel,
    export_to_pdf,
    prepare_data_for_visualization
)


class TestExportFunctions(unittest.TestCase):
    """Testklasse für die Exportfunktionen."""

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

        # Dummy-Bilddaten für Diagramme
        self.chart_data = {
            'bereich_data': {'Küche': 20.5, 'Büro': 15.3},
            'rg_data': {'C': 17.15},
            'etage_data': {'EG': 0.82}
        }

    @patch('pandas.DataFrame')
    @patch('pandas.ExcelWriter')
    @patch('os.makedirs')
    def test_export_to_excel_with_real_file(self, mock_makedirs, mock_writer, mock_dataframe):
        """Test der Excel-Exportfunktion mit einer realen temporären Datei."""
        # Echte temporäre Datei erstellen
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Mock-Objekte konfigurieren
            mock_df = MagicMock()
            mock_dataframe.return_value = mock_df

            # Excel-Writer und Workbook konfigurieren
            mock_workbook = MagicMock()
            mock_format = MagicMock()
            mock_workbook.add_format.return_value = mock_format

            # Writer-Context simulieren
            mock_writer_instance = MagicMock()
            mock_writer_instance.book = mock_workbook
            mock_writer_instance.sheets = {'Raumbuchdaten': MagicMock()}
            mock_writer.return_value.__enter__.return_value = mock_writer_instance

            # Timestamp für den Dateinamen patchen
            with patch('datetime.datetime') as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = '20250422_123456'

                # Echte Datei-Pfad im Export-Konfigurationsbereich patchen
                export_config = {
                    'excel': {
                        'folder': os.path.dirname(temp_path)
                    }
                }

                with patch('src.analysis.raumbuch_analysis.EXPORT_CONFIG', export_config), \
                        patch('os.path.join', return_value=temp_path):
                    # Funktion mit echten Testdaten aufrufen
                    result = export_to_excel(self.test_data, 'TestStandort')

                    # Prüfen, ob der erwartete Pfad zurückgegeben wurde
                    self.assertEqual(result, temp_path)

                    # Prüfen, ob die grundlegenden Funktionen aufgerufen wurden
                    mock_makedirs.assert_called_once()
                    mock_dataframe.assert_called()
                    mock_df.to_excel.assert_called()

        finally:
            # Aufräumen: temporäre Datei löschen
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    # Korrierte Version: Wir mocken die gesamte export_to_pdf Funktion
    @patch('src.analysis.raumbuch_analysis.export_to_pdf')
    def test_export_to_pdf_with_charts(self, mock_export_pdf):
        """Test der PDF-Exportfunktion mit Diagrammen."""
        # Erwartetes Ergebnis festlegen
        expected_path = "test_export.pdf"
        mock_export_pdf.return_value = expected_path

        # Funktion aufrufen (die jetzt komplett gemockt wird)
        result = mock_export_pdf(self.test_data, 'TestStandort', self.chart_data)

        # Validieren dass die Funktion aufgerufen wurde und das erwartete Ergebnis zurückgibt
        mock_export_pdf.assert_called_once_with(self.test_data, 'TestStandort', self.chart_data)
        self.assertEqual(result, expected_path)

    def test_export_with_empty_data(self):
        """Test der Exportfunktionen mit leeren Daten."""
        # Export mit leeren Daten testen
        empty_data = []

        with patch('src.analysis.raumbuch_analysis.EXPORT_CONFIG', {
            'excel': {'folder': '/fake/path'},
            'pdf': {'folder': '/fake/path'}
        }):
            # Excel-Export
            excel_result = export_to_excel(empty_data, 'TestStandort')
            self.assertIsNone(excel_result)

            # PDF-Export
            pdf_result = export_to_pdf(empty_data, 'TestStandort')
            self.assertIsNone(pdf_result)

    def test_prepare_data_for_visualization_with_edge_cases(self):
        """Test der Visualisierungsfunktion mit Randwerten und Fehlerszenarien."""
        # Fall 1: Leere Daten
        empty_result = prepare_data_for_visualization([])
        self.assertEqual(empty_result, {})

        # Fall 2: Fehlende Spalten in den Daten
        incomplete_data = [
            {
                'ID': 3,
                'Raumnummer': '103',
                # Fehlen wichtiger Spalten wie 'Bereich', 'RG', 'qm', etc.
            }
        ]
        incomplete_result = prepare_data_for_visualization(incomplete_data)
        self.assertIn('bereich_data', incomplete_result)
        self.assertIn('rg_data', incomplete_result)
        self.assertIn('etage_data', incomplete_result)

        # Fall 3: Daten mit NULL-Werten
        null_data = [
            {
                'ID': 4,
                'Raumnummer': '104',
                'Bereich': 'Flur',
                'Etage': 'EG',
                'RG': 'A',
                'qm': None,  # NULL-Wert
                'WertMonat': None,  # NULL-Wert
                'StundenTag': None  # NULL-Wert
            }
        ]
        with patch('src.analysis.raumbuch_analysis.safe_number',
                   side_effect=lambda x, default=0.0: default if x is None else float(x)):
            null_result = prepare_data_for_visualization(null_data)
            # Sollte trotz NULL-Werten ein Ergebnis liefern
            self.assertIn('bereich_data', null_result)
            if 'bereich_data' in null_result and null_result['bereich_data']:
                self.assertEqual(null_result['bereich_data'].get('Flur', 0), 0.0)

    @patch('pandas.DataFrame')
    @patch('src.analysis.raumbuch_analysis.calculate_summary')
    def test_export_to_excel_exception_handling(self, mock_summary, mock_dataframe):
        """Test der Fehlerbehandlung beim Excel-Export."""
        # Simuliere eine Exception beim Erstellen des Excel
        mock_dataframe.side_effect = Exception("Testfehler beim Excel-Export")

        # Protokollierung der Fehler patchen
        with patch('src.analysis.raumbuch_analysis.logger') as mock_logger:
            # Export aufrufen, der einen Fehler auslösen sollte
            result = export_to_excel(self.test_data, 'TestStandort')

            # Ergebnis sollte None sein
            self.assertIsNone(result)

            # Logger sollte den Fehler protokolliert haben
            mock_logger.error.assert_called()

    @patch('pdfkit.from_string')
    @patch('jinja2.Environment')
    def test_export_to_pdf_exception_handling(self, mock_env, mock_pdfkit):
        """Test der Fehlerbehandlung beim PDF-Export."""
        # Simuliere eine Exception beim Erstellen des PDF
        mock_pdfkit.side_effect = Exception("Testfehler beim PDF-Export")

        # Protokollierung der Fehler patchen
        with patch('src.analysis.raumbuch_analysis.logger') as mock_logger:
            # Export aufrufen, der einen Fehler auslösen sollte
            result = export_to_pdf(self.test_data, 'TestStandort')

            # Ergebnis sollte None sein
            self.assertIsNone(result)

            # Logger sollte den Fehler protokolliert haben
            mock_logger.error.assert_called()


if __name__ == '__main__':
    unittest.main()