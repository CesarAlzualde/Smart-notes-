"""
Módulo auxiliar para manejar el estado de resúmenes asíncronos.
Este módulo extiende la funcionalidad del OCRSummaryHandler sin modificar
directamente el archivo original.
"""

import os
import json
import logging
from typing import Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_temp_file_path(summary_id: str, prefix: str = "summary_result") -> str:
    """
    Obtiene la ruta de archivo temporal para un ID de resumen.
    Esta función duplica la lógica interna de OCRSummaryHandler para mantener compatibilidad.
    
    Args:
        summary_id: ID del resumen
        prefix: Prefijo del nombre de archivo (default: summary_result)
        
    Returns:
        Ruta completa al archivo temporal
    """
    # Obtener una instancia de OCRSummaryHandler para usar su método get_temp_file_path
    from .ocr_summary_handler import OCRSummaryHandler
    handler = OCRSummaryHandler()
    
    # Usar el método original para garantizar que la ruta sea consistente
    return handler.get_temp_file_path(summary_id, prefix)

def get_summary_status(summary_id: str) -> Dict[str, Any]:
    """
    Recupera el estado de un resumen asíncrono.
    
    Args:
        summary_id: ID del resumen asíncrono
        
    Returns:
        Estado actual del resumen, incluyendo el resumen si está completo
    """
    temp_file = get_temp_file_path(summary_id)
    
    if not os.path.exists(temp_file):
        logger.warning(f"No se encontró archivo de resumen para ID: {summary_id}")
        return {
            'status': 'not_found',
            'error': f"No se encontró información para el resumen {summary_id}"
        }
        
    try:
        with open(temp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Resumen encontrado para ID {summary_id}: {data.get('status', 'unknown')}")
        return data
    except Exception as e:
        logger.error(f"Error leyendo estado del resumen: {e}")
        return {
            'status': 'error',
            'error': f"Error al leer estado: {str(e)}"
        }
        
def patch_ocr_handler():
    """
    Aplica un monkey patch al OCRSummaryHandler para añadir la funcionalidad
    de get_summary_status si no existe.
    
    Esta función se debe llamar durante el inicio de la aplicación.
    """
    from .ocr_summary_handler import OCRSummaryHandler
    
    # Solo añadir el método si no existe
    if not hasattr(OCRSummaryHandler, 'get_summary_status'):
        logger.info("Aplicando patch a OCRSummaryHandler para añadir método get_summary_status")
        
        def get_summary_status_method(self, summary_id: str) -> Dict[str, Any]:
            """
            Recupera el estado de un resumen asíncrono.
            Método añadido dinámicamente por patch.
            """
            return get_summary_status(summary_id)
        
        # Añadir el método a la clase
        setattr(OCRSummaryHandler, 'get_summary_status', get_summary_status_method)
        
        logger.info("Patch aplicado correctamente")
    else:
        logger.info("OCRSummaryHandler ya tiene el método get_summary_status, no se requiere patch")
