"""
Flask-Anwendung für die RitterDigitalAuswertung.
"""

import logging
import os
from datetime import datetime
from flask import Flask

from config.settings import APP_CONFIG, STATIC_FOLDER, TEMPLATE_FOLDER
from src.web.routes import register_routes

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    """
    Erstellt und konfiguriert die Flask-Anwendung.

    Returns:
        Flask: Konfigurierte Flask-Anwendung
    """
    app = Flask(
        __name__,
        static_folder=STATIC_FOLDER,
        template_folder=TEMPLATE_FOLDER
    )

    # Konfiguration
    app.config.update(
        SECRET_KEY=APP_CONFIG['secret_key'],
        DEBUG=APP_CONFIG['debug']
    )

    # Kontextprozessoren
    @app.context_processor
    def inject_globals():
        """
        Injiziert globale Variablen in die Templates.

        Returns:
            dict: Dictionary mit globalen Variablen
        """
        return {
            'current_year': datetime.now().year,
            'app_title': APP_CONFIG['title'],
            'app_version': APP_CONFIG['version']
        }

    # Fehlerbehandlung
    @app.errorhandler(404)
    def page_not_found(e):
        """
        Behandelt 404-Fehler.

        Args:
            e: Fehler-Objekt

        Returns:
            tuple: Fehler-Template und Statuscode
        """
        return render_error_page('Die angeforderte Seite wurde nicht gefunden.', 404)

    @app.errorhandler(500)
    def server_error(e):
        """
        Behandelt 500-Fehler.

        Args:
            e: Fehler-Objekt

        Returns:
            tuple: Fehler-Template und Statuscode
        """
        logger.error(f"Serverfehler: {e}")
        return render_error_page('Ein interner Serverfehler ist aufgetreten.', 500)

    @app.errorhandler(Exception)
    def handle_exception(e):
        """
        Behandelt unerwartete Ausnahmen.

        Args:
            e: Exception-Objekt

        Returns:
            tuple: Fehler-Template und Statuscode
        """
        logger.error(f"Unerwartete Ausnahme: {e}")
        return render_error_page('Ein unerwarteter Fehler ist aufgetreten.', 500)

    # Routen registrieren
    register_routes(app)

    logger.info(f"Flask-Anwendung erstellt. Debug-Modus: {app.config['DEBUG']}")
    return app


def render_error_page(message, status_code):
    """
    Rendert eine Fehlerseite mit einer Nachricht und einem Statuscode.

    Args:
        message (str): Fehlermeldung
        status_code (int): HTTP-Statuscode

    Returns:
        tuple: Fehler-Template und Statuscode
    """
    from flask import render_template
    return render_template('error.html', message=message), status_code