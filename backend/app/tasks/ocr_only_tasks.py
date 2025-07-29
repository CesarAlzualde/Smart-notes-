"""
Tareas Celery específicas para OCR que no dependen de TensorFlow.
Este módulo está diseñado para funcionar incluso cuando hay conflictos con TensorFlow.
"""

import os
import time
import logging
from celery import shared_task
from ..extensions import db
from ..models import File
from ..services.ocr_processor import OCRProcessor
from ..services.ocr_summary_handler import OCRSummaryHandler
# Ya no necesitamos get_app_context ya que el worker tiene contexto global

logger = logging.getLogger(__name__)

def process_ocr_only(file_id, engine='tesseract', extra_config=None):
    """
    Tarea Celery para procesar OCR en segundo plano, sin dependencias de TensorFlow.
    Opcionalmente genera un resumen del texto extraído como un proceso separado.
    
    Args:
        file_id: ID del archivo a procesar
        engine: Motor OCR a utilizar ('tesseract' o 'google_vision')
        extra_config: Configuración adicional como {'is_whiteboard': True, 'generate_summary': True}
    
    Returns:
        dict: Resultado del procesamiento OCR con resumen si se habilitó
    """
    start_time = time.time()
    
    try:
        logger.info(f"Iniciando procesamiento OCR para archivo {file_id} con engine {engine}")
        

        
        # El contexto Flask ya está disponible globalmente en el worker
        file = File.query.get(file_id)
        if not file:
            raise ValueError(f"No se encontró el archivo con ID {file_id}")
    
        # Construir ruta completa (filepath ya contiene la ruta completa)
        file_path = file.filepath
        
        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No se encontró el archivo en: {file_path}")
        
        # Extraer opciones de config
        if not extra_config:
            extra_config = {}
            
        is_whiteboard = extra_config.get('is_whiteboard', False)
        generate_summary = extra_config.get('generate_summary', True)  # Por defecto generar resumen
        async_summary = extra_config.get('async_summary', True)  # Por defecto resumen asíncrono
        

        
        # Usar el nuevo handler que separa OCR y resumen
        handler = OCRSummaryHandler()
        
        # Ejecutar el pipeline de OCR y resumen como procesos separados
        result = handler.get_ocr_summary_pipeline(
            file_path=file_path,
            engine=engine,
            is_whiteboard=is_whiteboard,
            generate_summary=generate_summary,
            async_summary=async_summary
        )
        
        # Si el OCR fue exitoso, actualizar la base de datos
        if result.get('success', False):
            # El contexto Flask ya está disponible globalmente
            file.processed = True
            file.processing_status = 'SUCCESS'
            file.extract_text = result.get('text', '')
            
            # Guardar metadatos en el campo JSON
            file.file_metadata = {
                'ocr_engine': engine,
                'processing_time_seconds': time.time() - start_time,
                'char_count': len(result.get('text', '')),
                'is_whiteboard': is_whiteboard
            }
            
            # Si tenemos un resumen síncrono, añadirlo a los metadatos
            if generate_summary and not async_summary and 'summary' in result:
                if not file.file_metadata:
                    file.file_metadata = {}
                file.file_metadata['summary'] = result.get('summary', '')
                
            db.session.commit()
            logger.info(f"Archivo {file_id} actualizado en BD. Texto extraído: {len(result.get('text', ''))} caracteres")
        

        
        elapsed_time = time.time() - start_time
        result['total_processing_time'] = f"{elapsed_time:.2f}s"
        logger.info(f"Pipeline OCR-resumen completado para archivo {file_id} con {engine} en {elapsed_time:.2f}s")
    
        return result
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Error en procesamiento OCR para archivo {file_id}: {str(e)}")
        
        # Actualizar estado de error en la base de datos
        try:
            file = File.query.get(file_id)
            if file:
                file.processed = True
                file.processing_status = f'ERROR: {str(e)}'
                db.session.commit()
        except Exception as db_error:
            logger.error(f"Error actualizando estado en DB: {str(db_error)}")
        
        # Propagar la excepción para que el hilo que la llamó la pueda capturar
        raise e
