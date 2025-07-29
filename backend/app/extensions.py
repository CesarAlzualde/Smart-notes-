"""
Archivo central para instanciar extensiones de Flask y evitar importaciones circulares.
"""
import logging
from functools import wraps
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)

# --- Instancia de SQLAlchemy ---
db = SQLAlchemy()


# --- Instancia de la Caché ---
try:
    from flask_caching import Cache
    
    # Configuración para usar una caché simple en memoria a través de Flask-Caching.
    cache = Cache(config={
        'CACHE_TYPE': 'SimpleCache'
    })
    logger.info("Flask-Caching configurado para usar SimpleCache (en memoria).")

except ImportError:
    logger.warning("ADVERTENCIA: No se pudo importar flask_caching. La caché no funcionará.")
    
    # Implementación de un objeto de caché 'dummy' que no hace nada si la librería no está instalada.
    # Esto evita que la aplicación se rompa si flask_caching no está presente.
    class DummyCache:
        def __init__(self, *args, **kwargs): pass
        def init_app(self, app): pass
        def get(self, *args, **kwargs): return None
        def set(self, *args, **kwargs): pass
        def delete(self, *args, **kwargs): pass
        def cached(self, *args, **kwargs):
            def decorator(f):
                @wraps(f)
                def decorated_function(*args, **kwargs):
                    return f(*args, **kwargs)
                return decorated_function
            return decorator
    
    cache = DummyCache()
