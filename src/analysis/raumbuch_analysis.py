"""
Modul zur Analyse und Verarbeitung von Raumbuch-Daten.
Mit verbesserter Behandlung von NULL-Werten.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import pdfkit
from jinja2 import Environment, FileSystemLoader
import logging

from config.settings import EXPORT_CONFIG, TEMPLATE_FOLDER

# Logging konfigurieren
logger = logging.getLogger(__name__)

def safe_number(value, default=0.0):
    """
    Konvertiert einen Wert sicher in eine Zahl und gibt einen Standardwert zurück, wenn nicht möglich.

    Args:
        value: Zu konvertierender Wert
        default (float): Standardwert, wenn Konvertierung nicht möglich ist

    Returns:
        float: Konvertierter Wert oder Standardwert
    """
    if value is None:
        return default

    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def calculate_summary(data):
    """
    Berechnet zusammenfassende Statistiken für die Raumbuch-Daten.

    Args:
        data (list): Liste von Raumbuch-Objekten

    Returns:
        dict: Dictionary mit zusammenfassenden Statistiken
    """
    if not data:
        return {}

    # Konvertieren zu DataFrame für einfachere Analyse
    df = pd.DataFrame(data)

    # Sicherstellen, dass numerische Spalten tatsächlich numerisch sind
    numeric_columns = ['qm', 'WertMonat', 'WertJahr', 'StundenMonat', 'qmMonat']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: safe_number(x))

    # Allgemeine Statistiken
    total_rooms = len(df)
    total_qm = df['qm'].sum() if 'qm' in df.columns else 0
    total_qm_monat = df['qmMonat'].sum() if 'qmMonat' in df.columns else 0
    total_wert_monat = df['WertMonat'].sum() if 'WertMonat' in df.columns else 0
    total_wert_jahr = df['WertJahr'].sum() if 'WertJahr' in df.columns else 0
    total_stunden_monat = df['StundenMonat'].sum() if 'StundenMonat' in df.columns else 0

    # Statistiken nach Bereichen
    bereich_stats = None
    if 'Bereich' in df.columns:
        bereich_stats = df.groupby('Bereich').agg({
            'qm': 'sum',
            'WertMonat': 'sum',
            'WertJahr': 'sum',
            'StundenMonat': 'sum'
        }).reset_index().to_dict('records')

    # Reinigungsgruppen-Statistiken
    rg_stats = None
    if 'RG' in df.columns:
        rg_stats = df.groupby('RG').agg({
            'qm': 'sum',
            'WertMonat': 'sum',
            'WertJahr': 'sum',
            'StundenMonat': 'sum'
        }).reset_index().to_dict('records')

    return {
        'total_rooms': total_rooms,
        'total_qm': total_qm,
        'total_qm_monat': total_qm_monat,
        'total_wert_monat': total_wert_monat,
        'total_wert_jahr': total_wert_jahr,
        'total_stunden_monat': total_stunden_monat,
        'bereich_stats': bereich_stats,
        'rg_stats': rg_stats
    }

def prepare_data_for_visualization(data):
    """
    Bereitet Daten für Visualisierungen auf.

    Args:
        data (list): Liste von Raumbuch-Objekten

    Returns:
        dict: Dictionary mit aufbereiteten Daten für verschiedene Visualisierungen
    """
    if not data:
        return {}

    try:
        # Konvertieren zu DataFrame für einfachere Analyse
        df = pd.DataFrame(data)

        # Sicherstellen, dass numerische Spalten tatsächlich numerisch sind
        numeric_columns = ['qm', 'WertMonat', 'StundenMonat']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: safe_number(x))

        # Daten für Kreisdiagramm der Bereiche
        bereich_data = None
        if 'Bereich' in df.columns and 'qm' in df.columns:
            bereich_data = df.groupby('Bereich')['qm'].sum().to_dict()

        # Daten für Balkendiagramm der Reinigungsgruppen
        rg_data = None
        if 'RG' in df.columns and 'WertMonat' in df.columns:
            rg_data = df.groupby('RG')['WertMonat'].sum().to_dict()

        # Daten für Stunden pro Etage
        etage_data = None
        if 'Etage' in df.columns and 'StundenMonat' in df.columns:
            etage_data = df.groupby('Etage')['StundenMonat'].sum().to_dict()

        return {
            'bereich_data': bereich_data,
            'rg_data': rg_data,
            'etage_data': etage_data
        }
    except Exception as e:
        logger.error(f"Fehler bei der Datenvorbereitung für Visualisierung: {e}")
        return {}

def export_to_excel(data, standort_name):
    """
    Exportiert Raumbuch-Daten nach Excel.

    Args:
        data (list): Liste von Raumbuch-Objekten
        standort_name (str): Name des Standorts

    Returns:
        str: Pfad zur erstellten Excel-Datei
    """
    if not data:
        return None

    try:
        # Erstelle DataFrame
        df = pd.DataFrame(data)

        # Sicherstellen, dass numerische Spalten tatsächlich numerisch sind
        numeric_columns = ['qm', 'qmMonat', 'WertMonat', 'WertJahr', 'StundenTag', 'StundenMonat', 'qmStunde']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: safe_number(x))

        # Erstelle Timestamp für Dateinamen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Raumbuch_Auswertung_{standort_name}_{timestamp}.xlsx"

        # Erstelle Export-Ordner, falls er nicht existiert
        export_folder = EXPORT_CONFIG['excel']['folder']
        os.makedirs(export_folder, exist_ok=True)

        # Erstelle Excel-Datei
        excel_path = os.path.join(export_folder, filename)

        # Erstelle Excel-Writer
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            # Haupttabelle
            df.to_excel(writer, sheet_name='Raumbuchdaten', index=False)

            # Erstelle Zusammenfassung
            summary = calculate_summary(data)

            # Erstellen des Summary-DataFrames
            summary_data = {
                'Metrik': ['Anzahl Räume', 'Gesamtfläche (qm)', 'Gesamtkosten pro Monat (€)',
                          'Gesamtkosten pro Jahr (€)', 'Gesamtstunden pro Monat'],
                'Wert': [summary['total_rooms'], summary['total_qm'], summary['total_wert_monat'],
                        summary['total_wert_jahr'], summary['total_stunden_monat']]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Zusammenfassung', index=False)

            # Bereichsstatistiken
            if summary['bereich_stats']:
                bereich_df = pd.DataFrame(summary['bereich_stats'])
                bereich_df.to_excel(writer, sheet_name='Nach Bereich', index=False)

            # Reinigungsgruppen-Statistiken
            if summary['rg_stats']:
                rg_df = pd.DataFrame(summary['rg_stats'])
                rg_df.to_excel(writer, sheet_name='Nach Reinigungsgruppe', index=False)

            # Formatierung
            workbook = writer.book
            format_header = workbook.add_format({'bold': True, 'bg_color': '#DDDDDD', 'border': 1})
            format_number = workbook.add_format({'num_format': '#,##0.00'})

            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, format_header)
                    if df[value].dtype in [float, int]:
                        worksheet.set_column(col_num, col_num, None, format_number)

        return excel_path
    except Exception as e:
        logger.error(f"Fehler beim Excel-Export: {e}")
        return None

def export_to_pdf(data, standort_name, charts_data=None):
    """
    Exportiert Raumbuch-Daten nach PDF.

    Args:
        data (list): Liste von Raumbuch-Objekten
        standort_name (str): Name des Standorts
        charts_data (dict, optional): Daten für Charts

    Returns:
        str: Pfad zur erstellten PDF-Datei
    """
    if not data:
        return None

    try:
        # Erstelle Timestamp für Dateinamen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Raumbuch_Auswertung_{standort_name}_{timestamp}.pdf"

        # Erstelle Export-Ordner, falls er nicht existiert
        export_folder = EXPORT_CONFIG['pdf']['folder']
        os.makedirs(export_folder, exist_ok=True)

        pdf_path = os.path.join(export_folder, filename)

        # Berechne Zusammenfassung
        summary = calculate_summary(data)

        # Erstelle Charts, falls nötig
        charts_folder = os.path.join(export_folder, 'charts')
        if not os.path.exists(charts_folder):
            os.makedirs(charts_folder)

        chart_paths = {}

        if charts_data:
            # Beispiel: Erstelle Balkendiagramm für Bereiche
            if charts_data.get('bereich_data'):
                bereiche = list(charts_data['bereich_data'].keys())
                qm_values = [safe_number(charts_data['bereich_data'][bereich]) for bereich in bereiche]

                plt.figure(figsize=(10, 6))
                plt.bar(bereiche, qm_values)
                plt.title('Quadratmeter nach Bereich')
                plt.xlabel('Bereich')
                plt.ylabel('Quadratmeter')
                plt.xticks(rotation=45)
                plt.tight_layout()

                bereich_chart_path = os.path.join(charts_folder, f'bereich_chart_{timestamp}.png')
                plt.savefig(bereich_chart_path)
                plt.close()

                chart_paths['bereich_chart'] = bereich_chart_path

        # Verwende Jinja2-Template für das PDF
        env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))
        template = env.get_template('report_pdf.html')

        # Render Template
        html_content = template.render(
            title=f"Raumbuch Auswertung - {standort_name}",
            timestamp=datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            data=data[:100],  # Begrenze auf 100 Einträge für das PDF
            summary=summary,
            charts=chart_paths,
            total_items=len(data)
        )

        # Erstelle PDF mit pdfkit
        pdfkit.from_string(html_content, pdf_path)

        # Lösche temporäre Charts
        for chart_path in chart_paths.values():
            if os.path.exists(chart_path):
                os.remove(chart_path)

        return pdf_path
    except Exception as e:
        logger.error(f"Fehler beim PDF-Export: {e}")
        return None