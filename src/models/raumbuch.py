"""
Enthält Datenmodelle für die Raumbuch-Anwendung.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class RaumbuchEntry:
    """
    Datenklasse für einen Raumbuch-Eintrag.
    """
    id: int
    raumnummer: Optional[str] = None
    bereich: Optional[str] = None
    gebaeudeteil: Optional[str] = None
    etage: Optional[str] = None
    bezeichnung: Optional[str] = None
    rg: Optional[str] = None
    qm: float = 0.0
    anzahl: int = 0
    intervall: Optional[str] = None
    rg_jahr: float = 0.0
    rg_monat: float = 0.0
    qm_monat: float = 0.0
    wert_monat: float = 0.0
    stunden_tag: float = 0.0
    stunden_monat: float = 0.0
    wert_jahr: float = 0.0
    qm_stunde: float = 0.0
    reinigungstage: Optional[str] = None
    bemerkung: Optional[str] = None
    reduzierung: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RaumbuchEntry':
        """
        Erstellt ein RaumbuchEntry-Objekt aus einem Dictionary.

        Args:
            data (Dict[str, Any]): Dictionary mit Raumbuch-Daten

        Returns:
            RaumbuchEntry: Erstelltes RaumbuchEntry-Objekt
        """
        # Spaltennamen aus der Datenbank zu Klassenattributen zuordnen
        field_mapping = {
            'ID': 'id',
            'Raumnummer': 'raumnummer',
            'Bereich': 'bereich',
            'Gebaeudeteil': 'gebaeudeteil',
            'Etage': 'etage',
            'Bezeichnung': 'bezeichnung',
            'RG': 'rg',
            'qm': 'qm',
            'Anzahl': 'anzahl',
            'Intervall': 'intervall',
            'RgJahr': 'rg_jahr',
            'RgMonat': 'rg_monat',
            'qmMonat': 'qm_monat',
            'WertMonat': 'wert_monat',
            'StundenTag': 'stunden_tag',
            'StundenMonat': 'stunden_monat',
            'WertJahr': 'wert_jahr',
            'qmStunde': 'qm_stunde',
            'Reinigungstage': 'reinigungstage',
            'Bemerkung': 'bemerkung',
            'Reduzierung': 'reduzierung',
        }

        # Dictionary mit Attributnamen als Schlüssel erstellen
        kwargs = {}
        for db_field, class_field in field_mapping.items():
            if db_field in data:
                kwargs[class_field] = data[db_field]

        return cls(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert das RaumbuchEntry-Objekt in ein Dictionary.

        Returns:
            Dict[str, Any]: Dictionary-Repräsentation des Objekts
        """
        return {
            'id': self.id,
            'raumnummer': self.raumnummer,
            'bereich': self.bereich,
            'gebaeudeteil': self.gebaeudeteil,
            'etage': self.etage,
            'bezeichnung': self.bezeichnung,
            'rg': self.rg,
            'qm': self.qm,
            'anzahl': self.anzahl,
            'intervall': self.intervall,
            'rg_jahr': self.rg_jahr,
            'rg_monat': self.rg_monat,
            'qm_monat': self.qm_monat,
            'wert_monat': self.wert_monat,
            'stunden_tag': self.stunden_tag,
            'stunden_monat': self.stunden_monat,
            'wert_jahr': self.wert_jahr,
            'qm_stunde': self.qm_stunde,
            'reinigungstage': self.reinigungstage,
            'bemerkung': self.bemerkung,
            'reduzierung': self.reduzierung,
        }


def convert_db_results_to_entries(results: List[Dict[str, Any]]) -> List[RaumbuchEntry]:
    """
    Konvertiert eine Liste von Datenbankeinträgen in RaumbuchEntry-Objekte.

    Args:
        results (List[Dict[str, Any]]): Liste von Datenbank-Dictionaries

    Returns:
        List[RaumbuchEntry]: Liste von RaumbuchEntry-Objekten
    """
    entries = []
    for result in results:
        entry = RaumbuchEntry.from_dict(result)
        entries.append(entry)
    return entries


def validate_raumbuch_entries(entries: List[RaumbuchEntry]) -> List[str]:
    """
    Validiert eine Liste von RaumbuchEntry-Objekten.

    Args:
        entries (List[RaumbuchEntry]): Liste von RaumbuchEntry-Objekten

    Returns:
        List[str]: Liste von Validierungsfehlern, leer wenn keine Fehler
    """
    errors = []

    for i, entry in enumerate(entries):
        # Numerische Felder sollten positiv sein
        if entry.qm < 0:
            errors.append(f"Eintrag {i + 1}: qm darf nicht negativ sein")

        # Weitere Validierungsregeln können hier hinzugefügt werden

    return errors