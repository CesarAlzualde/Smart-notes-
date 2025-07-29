"""
Tareas asíncronas para procesamiento OCR.
"""

import logging
import os
import time
from celery import shared_task
from ..services.ocr_processor import process_ocr as process_ocr_service
from ..models.file import File
from app.extensions import db

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_ocr(file_id, engine='tesseract', extra_config=None):
    """Procesa un archivo para extraer texto con OCR. Ya no es una tarea Celery."""
    start_time = time.time()
    logger.info(f"Iniciando procesamiento OCR para archivo {file_id} con engine {engine}")

    file = File.query.get(file_id)
    if not file:
        logger.error(f"No se encontró el archivo con ID {file_id}")
        return

    try:
        file_path = file.filepath
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo no se encuentra en la ruta: {file_path}")

        is_whiteboard = extra_config.get('is_whiteboard', False) if extra_config else False
        
        logger.info(f"Delegando al servicio OCR: file={file_path}, engine={engine}, whiteboard={is_whiteboard}")
        
        # Llamar a la función de servicio unificada
        result = process_ocr_service(
            filepath=file_path,
            engine=engine,
            is_whiteboard=is_whiteboard
        )

        if not result.get('success'):
            error_message = result.get('error', 'Error desconocido en el servicio OCR')
            raise RuntimeError(error_message)

        extracted_text = result.get('text', '')
        engine_used = result.get('engine_used', engine)

        # Actualizar el archivo en la base de datos
        file.processed = True
        file.extract_text = extracted_text
        file.processing_status = 'SUCCESS'
        # Guardar metadatos relevantes en el campo JSON
        file.file_metadata = {
            'ocr_engine': engine_used,
            'processing_time_seconds': time.time() - start_time,
            'char_count': len(extracted_text)
        }
        db.session.commit()

        logger.info(f"OCR completado para archivo {file_id} con {engine}. Texto extraído: {len(extracted_text)} caracteres")
        return {'file_id': file_id, 'status': 'SUCCESS', 'text_length': len(extracted_text)}

    except Exception as e:
        logger.error(f"Error en la función OCR para el archivo {file_id}: {e}", exc_info=True)
        if file:
            file.processed = True # Marcar como procesado para no reintentar indefinidamente
            file.processing_status = f'ERROR: {str(e)}'
            db.session.commit()
        # Propagar la excepción para que el hilo que la llamó la pueda capturar y registrar
        raise e
