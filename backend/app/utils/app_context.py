"""
Utilidad para manejar el contexto de la aplicación Flask en diferentes entornos.
"""
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def get_app_context():
    """
    Obtiene el contexto de la aplicación Flask actual o crea uno nuevo si no existe.
    Útil para operaciones que necesitan acceder a la base de datos u otras configuraciones
    de Flask fuera del contexto de una solicitud web.
    
    Returns:
        Un contexto de aplicación Flask que puede ser usado en un bloque 'with'
    """
    try:
        # Intentar obtener la app actual
        return current_app.app_context()
    except RuntimeError:
        # Si no hay contexto de app activo, crear uno
        logger.info("No hay contexto de aplicación activo, creando uno nuevo")
        from app import create_app
        app = create_app()
        return app.app_context()
