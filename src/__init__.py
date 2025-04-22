"""
Hauptmodul für die RitterDigitalAuswertung-Anwendung.
Enthält Untermodule für Datenbank, Modelle, Analyse und Web.
"""

from src.database import (
    get_db_connection,
    close_connection,
    get_raumbuch_data,
    get_standorte,
    get_standort_by_id
)

from src.models import RaumbuchEntry

from src.analysis import (
    calculate_summary,
    prepare_data_for_visualization,
    export_to_excel,
    export_to_pdf
)

from src.web import create_app

__all__ = [
    'get_db_connection',
    'close_connection',
    'get_raumbuch_data',
    'get_standorte',
    'get_standort_by_id',
    'RaumbuchEntry',
    'calculate_summary',
    'prepare_data_for_visualization',
    'export_to_excel',
    'export_to_pdf',
    'create_app'
]