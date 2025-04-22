"""
Allgemeine Anwendungseinstellungen für die RitterDigitalAuswertung-Anwendung.
"""

import os

# Anwendungskonfiguration
APP_CONFIG = {
    'title': 'Ritter Digital Raumbuch Auswertung',
    'description': 'Auswertungstool für das Raumbuch-System',
    'version': '1.0.0',
    'debug': True,
    'host': '0.0.0.0',
    'port': 5000,
    'secret_key': os.environ.get('SECRET_KEY', 'geheim_sicher_aendern_in_produktion'),
}

# Pfade
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STATIC_FOLDER = os.path.join(BASE_DIR, 'src', 'web', 'static')
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'src', 'web', 'templates')

# Export-Einstellungen
EXPORT_CONFIG = {
    'excel': {
        'enabled': True,
        'folder': os.path.join(BASE_DIR, 'exports'),
    },
    'pdf': {
        'enabled': True,
        'folder': os.path.join(BASE_DIR, 'exports'),
    }
}

# Erstellen des Export-Ordners, falls er nicht existiert
if not os.path.exists(EXPORT_CONFIG['excel']['folder']):
    os.makedirs(EXPORT_CONFIG['excel']['folder'])