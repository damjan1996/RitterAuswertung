"""
Tests für die Datenmodelle der RitterDigitalAuswertung-Anwendung.
"""

import unittest
from src.models.raumbuch import (
    RaumbuchEntry,
    convert_db_results_to_entries,
    validate_raumbuch_entries
)

class TestRaumbuchModel(unittest.TestCase):
    """Testklasse für das Raumbuch-Datenmodell."""

    def setUp(self):
        """Testdaten vorbereiten."""
        self.test_data_dict = {
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
        }

        self.test_data_dict_with_nulls = {
            'ID': 2,
            'Raumnummer': '102',
            'Bereich': 'Büro',
            'Gebaeudeteil': None,  # NULL
            'Etage': 'EG',
            'Bezeichnung': 'Büro',
            'RG': 'C',
            'qm': None,  # NULL
            'Anzahl': 1,
            'Intervall': 'Woche',
            'RgJahr': 52.0,
            'RgMonat': None,  # NULL
            'qmMonat': None,  # NULL
            'WertMonat': 7.33,
            'StundenTag': None,  # NULL
            'StundenMonat': 0.35,
            'WertJahr': 87.96,
            'qmStunde': 191.0,
            'Reinigungstage': None,
            'Bemerkung': None,
            'Reduzierung': None
        }

        self.test_db_results = [
            self.test_data_dict,
            self.test_data_dict_with_nulls
        ]

    def test_create_raumbuch_entry(self):
        """Test der Erstellung eines RaumbuchEntry-Objekts."""
        entry = RaumbuchEntry(id=1, raumnummer='101', bereich='Küche')

        self.assertEqual(entry.id, 1)
        self.assertEqual(entry.raumnummer, '101')
        self.assertEqual(entry.bereich, 'Küche')
        self.assertEqual(entry.qm, 0.0)  # Standardwert

    def test_from_dict(self):
        """Test der from_dict-Methode."""
        entry = RaumbuchEntry.from_dict(self.test_data_dict)

        self.assertEqual(entry.id, 1)
        self.assertEqual(entry.raumnummer, '101')
        self.assertEqual(entry.bereich, 'Küche')
        self.assertEqual(entry.gebaeudeteil, 'Hauptgebäude')
        self.assertEqual(entry.etage, 'EG')
        self.assertEqual(entry.bezeichnung, 'Besprechungsraum')
        self.assertEqual(entry.rg, 'C')
        self.assertEqual(entry.qm, 20.5)
        self.assertEqual(entry.anzahl, 1)
        self.assertEqual(entry.intervall, 'Woche')
        self.assertEqual(entry.rg_jahr, 52.0)
        self.assertEqual(entry.rg_monat, 4.33)
        self.assertEqual(entry.qm_monat, 88.77)
        self.assertEqual(entry.wert_monat, 9.82)
        self.assertEqual(entry.stunden_tag, 0.11)
        self.assertEqual(entry.stunden_monat, 0.47)
        self.assertEqual(entry.wert_jahr, 117.84)
        self.assertEqual(entry.qm_stunde, 187.0)
        self.assertIsNone(entry.reinigungstage)
        self.assertIsNone(entry.bemerkung)
        self.assertIsNone(entry.reduzierung)

    def test_from_dict_with_nulls(self):
        """Test der from_dict-Methode mit NULL-Werten."""
        entry = RaumbuchEntry.from_dict(self.test_data_dict_with_nulls)

        self.assertEqual(entry.id, 2)
        self.assertEqual(entry.raumnummer, '102')
        self.assertEqual(entry.bereich, 'Büro')
        self.assertIsNone(entry.gebaeudeteil)  # NULL-Wert
        self.assertEqual(entry.etage, 'EG')
        self.assertEqual(entry.bezeichnung, 'Büro')
        self.assertEqual(entry.rg, 'C')
        self.assertIsNone(entry.qm)  # NULL-Wert
        self.assertEqual(entry.anzahl, 1)
        self.assertEqual(entry.intervall, 'Woche')
        self.assertEqual(entry.rg_jahr, 52.0)
        self.assertIsNone(entry.rg_monat)  # NULL-Wert
        self.assertIsNone(entry.qm_monat)  # NULL-Wert
        self.assertEqual(entry.wert_monat, 7.33)
        self.assertIsNone(entry.stunden_tag)  # NULL-Wert
        self.assertEqual(entry.stunden_monat, 0.35)
        self.assertEqual(entry.wert_jahr, 87.96)
        self.assertEqual(entry.qm_stunde, 191.0)
        self.assertIsNone(entry.reinigungstage)
        self.assertIsNone(entry.bemerkung)
        self.assertIsNone(entry.reduzierung)

    def test_to_dict(self):
        """Test der to_dict-Methode."""
        entry = RaumbuchEntry.from_dict(self.test_data_dict)
        result_dict = entry.to_dict()

        # Überprüfen, ob alle Attribute im Dictionary vorhanden sind
        self.assertIn('id', result_dict)
        self.assertIn('raumnummer', result_dict)
        self.assertIn('bereich', result_dict)
        self.assertIn('gebaeudeteil', result_dict)
        self.assertIn('etage', result_dict)
        self.assertIn('qm', result_dict)
        self.assertIn('rg_jahr', result_dict)  # Snake-Case statt RgJahr

        # Überprüfen der Werte
        self.assertEqual(result_dict['id'], 1)
        self.assertEqual(result_dict['raumnummer'], '101')
        self.assertEqual(result_dict['bereich'], 'Küche')
        self.assertEqual(result_dict['gebaeudeteil'], 'Hauptgebäude')
        self.assertEqual(result_dict['qm'], 20.5)
        self.assertEqual(result_dict['rg_jahr'], 52.0)

    def test_convert_db_results_to_entries(self):
        """Test der convert_db_results_to_entries-Funktion."""
        entries = convert_db_results_to_entries(self.test_db_results)

        # Überprüfen der Anzahl der Einträge
        self.assertEqual(len(entries), 2)

        # Überprüfen des Typs
        self.assertIsInstance(entries[0], RaumbuchEntry)
        self.assertIsInstance(entries[1], RaumbuchEntry)

        # Überprüfen der Werte
        self.assertEqual(entries[0].id, 1)
        self.assertEqual(entries[0].raumnummer, '101')
        self.assertEqual(entries[1].id, 2)
        self.assertEqual(entries[1].raumnummer, '102')

    def test_validate_raumbuch_entries(self):
        """Test der validate_raumbuch_entries-Funktion."""
        # Gültige Einträge
        valid_entries = [
            RaumbuchEntry(id=1, raumnummer='101', bereich='Küche', qm=20.5),
            RaumbuchEntry(id=2, raumnummer='102', bereich='Büro', qm=15.3)
        ]

        # Ungültige Einträge (negative qm)
        invalid_entries = [
            RaumbuchEntry(id=3, raumnummer='103', bereich='Flur', qm=-5.0),
            RaumbuchEntry(id=4, raumnummer='104', bereich='Lager', qm=10.0)
        ]

        # Validierung testen
        valid_errors = validate_raumbuch_entries(valid_entries)
        invalid_errors = validate_raumbuch_entries(invalid_entries)

        # Überprüfen der Ergebnisse
        self.assertEqual(len(valid_errors), 0)  # Keine Fehler bei gültigen Einträgen
        self.assertGreater(len(invalid_errors), 0)  # Fehler bei ungültigen Einträgen
        self.assertIn('qm darf nicht negativ sein', invalid_errors[0])

if __name__ == '__main__':
    unittest.main()