"""
Tareas asíncronas para procesamiento de notas.
"""

import logging
import time
from celery import shared_task
from ..extensions import db
from ..models.note import Note
from ..models.file import File



# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_note(note_id):
    """
    Tarea Celery para procesar una nota en segundo plano
    Genera resumen y clasifica tópicos
    
    Args:
        note_id: ID de la nota a procesar
    
    Returns:
        dict: Resultado del procesamiento
    """
    start_time = time.time()
    
    try:

        
        note = Note.query.get(note_id)
        if not note:
            raise ValueError(f"No se encontró la nota con ID {note_id}")
        
        # Inicializar servicios de IA con importación diferida
        from ..services.text_summarizer import TextSummarizer
        from ..services.topic_classifier import NlpAnalyser
        summarizer = TextSummarizer()
        classifier = NlpAnalyser()
        

        
        # Procesar la nota con IA
        note.process_with_ai(summarizer, classifier)
        
        db.session.commit()
        

        
        # Calcular tiempo de procesamiento
        elapsed_time = time.time() - start_time
        
        logger.info(f"Procesamiento de nota {note_id} completado en {elapsed_time:.2f}s")
        
        return {
            'success': True,
            'note_id': note_id,
            'summary_length': len(note.summary) if note.summary else 0,
            'main_topic': note.main_topic,
            'main_topic_score': note.main_topic_score,
            'processing_time': f"{elapsed_time:.2f}s"
        }
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Error en procesamiento de nota {note_id}: {str(e)}")
        
        # Propagar la excepción para que el hilo la capture
        raise e


def bulk_process_notes(note_ids):
    """
    Tarea Celery para procesar múltiples notas en lote
    
    Args:
        note_ids: Lista de IDs de notas a procesar
    
    Returns:
        dict: Resultados del procesamiento
    """
    total_notes = len(note_ids)
    processed_count = 0
    failed_count = 0
    results_details = []

    for note_id in note_ids:
        try:
            # Llamar a la función de procesamiento directamente
            process_note(note_id)
            results_details.append({
                'note_id': note_id,
                'success': True
            })
            processed_count += 1
        except Exception as e:
            failed_count += 1
            results_details.append({
                'note_id': note_id,
                'success': False,
                'error': str(e)
            })
            logger.error(f"Error procesando la nota {note_id} en lote: {e}")

    summary = {
        'total': total_notes,
        'processed': processed_count,
        'failed': failed_count,
        'details': results_details
    }
    
    logger.info(f"Procesamiento en lote completado: {processed_count}/{total_notes} notas procesadas con éxito")
    return summary
