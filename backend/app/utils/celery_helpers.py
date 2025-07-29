"""
Utilidades para trabajar con Celery y determinar su disponibilidad.
"""

import logging
from functools import wraps

logger = logging.getLogger(__name__)

def is_celery_worker_running():
    """
    Verifica si hay trabajadores de Celery ejecutándose y disponibles.
    
    Returns:
        bool: True si hay trabajadores de Celery disponibles, False en caso contrario.
    """
    try:
        # Importar aquí para evitar importaciones circulares
        from app.celery_app import celery, CELERY_AVAILABLE
        
        if not CELERY_AVAILABLE:
            logger.warning("Celery no está disponible (no importado correctamente)")
            return False
            
        # Intentar inspeccionar los trabajadores activos
        try:
            inspector = celery.control.inspect()
            stats = inspector.stats()
            if not stats:
                logger.warning("No se detectaron trabajadores de Celery activos")
                return False
            
            logger.info(f"Trabajadores de Celery activos detectados: {len(stats)}")
            return True
        except Exception as e:
            logger.warning(f"Error al inspeccionar trabajadores de Celery: {e}")
            return False
    except Exception as e:
        logger.error(f"Error al verificar disponibilidad de Celery: {e}")
        return False

def fallback_to_sync(async_param_name='async_mode'):
    """
    Decorador que hace que una función use automáticamente el modo síncrono
    si los trabajadores de Celery no están disponibles.
    
    Args:
        async_param_name (str): Nombre del parámetro que controla el modo asíncrono
    
    Returns:
        function: Función decorada
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Si se solicitó modo asíncrono, verificar disponibilidad
            if kwargs.get(async_param_name, True):
                if not is_celery_worker_running():
                    logger.warning(f"Celery no disponible. Cambiando función {func.__name__} a modo síncrono")
                    kwargs[async_param_name] = False
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
