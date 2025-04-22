"""
Webmodul für die RitterDigitalAuswertung-Anwendung.
Stellt die Flask-Webanwendung bereit.
"""

from src.web.app import create_app
from src.web.routes import register_routes

__all__ = ['create_app', 'register_routes']