"""
Routen für die RitterDigitalAuswertung-Webanwendung.
"""

import logging
import os
from flask import render_template, request, jsonify, flash, redirect, url_for, send_file
from werkzeug.exceptions import NotFound
import traceback

from src.database import get_raumbuch_data, get_standorte, get_standort_by_id
from src.models.raumbuch import convert_db_results_to_entries
from src.analysis.raumbuch_analysis import (
    calculate_summary,
    prepare_data_for_visualization,
    export_to_excel,
    export_to_pdf,
    safe_number  # importiere die safe_number Funktion
)

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def preprocess_data(data):
    """
    Vorverarbeitung der Daten, um NULL-Werte zu behandeln.

    Args:
        data (list): Liste von Raumbuch-Daten

    Returns:
        list: Vorverarbeitete Daten
    """
    if not data:
        return []

    processed_data = []

    # Numerische Felder, die vorverarbeitet werden müssen
    numeric_fields = [
        'qm', 'Anzahl', 'RgJahr', 'RgMonat', 'qmMonat',
        'WertMonat', 'StundenTag', 'StundenMonat', 'WertJahr', 'qmStunde'
    ]

    for item in data:
        processed_item = dict(item)  # Kopie erstellen

        # Numerische Felder als Zahlen konvertieren oder 0 setzen
        for field in numeric_fields:
            if field in processed_item:
                processed_item[field] = safe_number(processed_item[field], 0.0)

        processed_data.append(processed_item)

    return processed_data

def register_routes(app):
    """
    Registriert die Routen für die Flask-Anwendung.

    Args:
        app (Flask): Flask-Anwendung
    """

    @app.route('/')
    def index():
        """
        Startseite mit Standortauswahl und einfacher Zusammenfassung.

        Returns:
            str: Gerenderte Index-Template
        """
        standorte = get_standorte()

        # Prüfen, ob ein Standort ausgewählt wurde
        standort_id = request.args.get('standort_id')
        data = None
        summary = None
        viz_data = None
        selected_standort = None

        if standort_id:
            try:
                standort_id = int(standort_id)
                selected_standort = get_standort_by_id(standort_id)

                if selected_standort:
                    # Daten abrufen
                    data = get_raumbuch_data(standort_id)

                    # Daten vorverarbeiten
                    data = preprocess_data(data)

                    # Zusammenfassung berechnen
                    summary = calculate_summary(data)

                    # Visualisierungsdaten vorbereiten
                    viz_data = prepare_data_for_visualization(data)
                else:
                    flash('Der ausgewählte Standort wurde nicht gefunden.', 'warning')
            except ValueError:
                flash('Ungültige Standort-ID.', 'danger')
            except Exception as e:
                logger.error(f"Fehler beim Laden der Daten: {e}")
                logger.error(traceback.format_exc())
                flash(f'Fehler beim Laden der Daten: {str(e)}', 'danger')

        return render_template(
            'index.html',
            standorte=standorte,
            data=data,
            summary=summary,
            viz_data=viz_data,
            selected_standort=selected_standort
        )

    @app.route('/report')
    def report():
        """
        Detaillierte Auswertungsseite mit Tabelle und Filtern.

        Returns:
            str: Gerenderte Report-Template
        """
        standorte = get_standorte()

        # Prüfen, ob ein Standort ausgewählt wurde
        standort_id = request.args.get('standort_id')
        data = None
        summary = None
        viz_data = None
        selected_standort = None
        filter_options = {}

        if standort_id:
            try:
                standort_id = int(standort_id)
                selected_standort = get_standort_by_id(standort_id)

                if selected_standort:
                    # Daten abrufen
                    data = get_raumbuch_data(standort_id)

                    # Daten vorverarbeiten
                    data = preprocess_data(data)

                    # Filter anwenden
                    data = apply_filters(data, request.args)

                    # Zusammenfassung berechnen
                    summary = calculate_summary(data)

                    # Visualisierungsdaten vorbereiten
                    viz_data = prepare_data_for_visualization(data)

                    # Filteroptionen erstellen
                    filter_options = create_filter_options(data)
                else:
                    flash('Der ausgewählte Standort wurde nicht gefunden.', 'warning')
            except ValueError:
                flash('Ungültige Standort-ID.', 'danger')
            except Exception as e:
                logger.error(f"Fehler beim Laden der Daten: {e}")
                logger.error(traceback.format_exc())  # Detaillierte Fehlerausgabe
                flash(f'Fehler beim Laden der Daten: {str(e)}', 'danger')

        return render_template(
            'report.html',
            standorte=standorte,
            data=data,
            summary=summary or {},  # Leeres Dict falls None
            viz_data=viz_data or {},  # Leeres Dict falls None
            selected_standort=selected_standort,
            filter_options=filter_options
        )

    @app.route('/api/standorte')
    def api_standorte():
        """
        API-Endpunkt für das Abrufen der Standorte.

        Returns:
            Response: JSON-Response mit Standortdaten
        """
        try:
            standorte = get_standorte()
            return jsonify(standorte)
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Standorte: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/export/excel/<int:standort_id>')
    def export_excel(standort_id):
        """
        Exportiert die Raumbuch-Daten als Excel-Datei.

        Args:
            standort_id (int): ID des Standorts

        Returns:
            Response: Excel-Datei zum Download
        """
        try:
            # Standort abrufen
            standort = get_standort_by_id(standort_id)
            if not standort:
                flash('Der ausgewählte Standort wurde nicht gefunden.', 'warning')
                return redirect(url_for('index'))

            # Daten abrufen
            data = get_raumbuch_data(standort_id)

            # Daten vorverarbeiten
            data = preprocess_data(data)

            # Filter anwenden
            data = apply_filters(data, request.args)

            # Nach Excel exportieren
            excel_path = export_to_excel(data, standort['Bezeichnung'])

            if excel_path and os.path.exists(excel_path):
                # Datei zum Download anbieten
                return send_file(
                    excel_path,
                    as_attachment=True,
                    download_name=os.path.basename(excel_path),
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                flash('Fehler beim Erstellen der Excel-Datei.', 'danger')
                return redirect(url_for('report', standort_id=standort_id))
        except Exception as e:
            logger.error(f"Fehler beim Excel-Export: {e}")
            logger.error(traceback.format_exc())
            flash(f'Fehler beim Excel-Export: {str(e)}', 'danger')
            return redirect(url_for('report', standort_id=standort_id))

    @app.route('/export/pdf/<int:standort_id>')
    def export_pdf(standort_id):
        """
        Exportiert die Raumbuch-Daten als PDF-Datei.

        Args:
            standort_id (int): ID des Standorts

        Returns:
            Response: PDF-Datei zum Download
        """
        try:
            # Standort abrufen
            standort = get_standort_by_id(standort_id)
            if not standort:
                flash('Der ausgewählte Standort wurde nicht gefunden.', 'warning')
                return redirect(url_for('index'))

            # Daten abrufen
            data = get_raumbuch_data(standort_id)

            # Daten vorverarbeiten
            data = preprocess_data(data)

            # Filter anwenden
            data = apply_filters(data, request.args)

            # Visualisierungsdaten für Charts vorbereiten
            viz_data = prepare_data_for_visualization(data)

            # Nach PDF exportieren
            pdf_path = export_to_pdf(data, standort['Bezeichnung'], viz_data)

            if pdf_path and os.path.exists(pdf_path):
                # Datei zum Download anbieten
                return send_file(
                    pdf_path,
                    as_attachment=True,
                    download_name=os.path.basename(pdf_path),
                    mimetype='application/pdf'
                )
            else:
                flash('Fehler beim Erstellen der PDF-Datei.', 'danger')
                return redirect(url_for('report', standort_id=standort_id))
        except Exception as e:
            logger.error(f"Fehler beim PDF-Export: {e}")
            logger.error(traceback.format_exc())
            flash(f'Fehler beim PDF-Export: {str(e)}', 'danger')
            return redirect(url_for('report', standort_id=standort_id))

def apply_filters(data, args):
    """
    Wendet Filter auf die Raumbuch-Daten an.

    Args:
        data (list): Liste der Raumbuch-Daten
        args (ImmutableMultiDict): Filter-Parameter

    Returns:
        list: Gefilterte Raumbuch-Daten
    """
    # Wenn keine Filter übergeben wurden, gib die ursprünglichen Daten zurück
    if not args or len(args) <= 1:  # standort_id ist immer vorhanden
        return data

    # Möglicherweise vorhandene Filter
    bereich = args.get('bereich')
    gebaeudeteil = args.get('gebaeudeteil')
    etage = args.get('etage')
    rg = args.get('rg')

    # Filtern
    filtered_data = data

    if bereich:
        filtered_data = [item for item in filtered_data if item.get('Bereich') == bereich]

    if gebaeudeteil:
        filtered_data = [item for item in filtered_data if item.get('Gebaeudeteil') == gebaeudeteil]

    if etage:
        filtered_data = [item for item in filtered_data if item.get('Etage') == etage]

    if rg:
        filtered_data = [item for item in filtered_data if item.get('RG') == rg]

    return filtered_data

def create_filter_options(data):
    """
    Erstellt Filteroptionen aus den Raumbuch-Daten.

    Args:
        data (list): Liste der Raumbuch-Daten

    Returns:
        dict: Dictionary mit Filteroptionen
    """
    bereiche = set()
    gebaeudeteil = set()
    etage = set()
    rg = set()

    for item in data:
        if 'Bereich' in item and item['Bereich']:
            bereiche.add(item['Bereich'])
        if 'Gebaeudeteil' in item and item['Gebaeudeteil']:
            gebaeudeteil.add(item['Gebaeudeteil'])
        if 'Etage' in item and item['Etage']:
            etage.add(item['Etage'])
        if 'RG' in item and item['RG']:
            rg.add(item['RG'])

    return {
        'bereiche': sorted(list(bereiche)),
        'gebaeudeteil': sorted(list(gebaeudeteil)),
        'etage': sorted(list(etage)),
        'rg': sorted(list(rg))
    }