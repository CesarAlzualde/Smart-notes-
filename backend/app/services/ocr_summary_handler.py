"""
Módulo que maneja la separación y coordinación entre extracción OCR y generación de resúmenes.
Permite que OCR funcione incluso cuando TensorFlow tiene problemas, y maneja la generación
de resúmenes en un proceso separado cuando sea necesario.
"""

import os
import time
import logging
import json
from typing import Dict, Any, Optional, Tuple
import threading
from flask import current_app

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRSummaryHandler:
    """
    Gestiona la separación de procesos OCR y resumen.
    Proporciona métodos para extraer texto y generar resúmenes de manera independiente.
    """
    
    def __init__(self):
        """Inicializa el gestor OCR-Resumen"""
        self.summary_error = None
        # Directorio para guardar resultados temporales
        self.temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                            'tmp', 'ocr_results')
        os.makedirs(self.temp_dir, exist_ok=True)
        
    def get_temp_file_path(self, file_id: str, prefix: str = "ocr_result") -> str:
        """
        Genera una ruta para almacenar resultados temporales de OCR.
        
        Args:
            file_id: ID del archivo
            prefix: Prefijo para el nombre del archivo temporal
            
        Returns:
            Ruta completa al archivo temporal
        """
        return os.path.join(self.temp_dir, f"{prefix}_{file_id}.json")
    
    def save_ocr_result(self, file_id: str, result: Dict[str, Any]) -> str:
        """
        Guarda el resultado OCR en un archivo temporal.
        
        Args:
            file_id: ID del archivo
            result: Resultado del OCR
            
        Returns:
            Ruta al archivo temporal donde se guardó el resultado
        """
        temp_file = self.get_temp_file_path(file_id)
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': time.time(),
                    'file_id': file_id,
                    'result': result
                }, f, ensure_ascii=False)
            logger.info(f"Resultado OCR guardado en {temp_file}")
            return temp_file
        except Exception as e:
            logger.error(f"Error guardando resultado OCR: {e}")
            return ""
    
    def load_ocr_result(self, file_id: str) -> Dict[str, Any]:
        """
        Carga un resultado OCR desde archivo temporal.
        
        Args:
            file_id: ID del archivo
            
        Returns:
            Datos del resultado OCR o diccionario vacío si no se encuentra
        """
        temp_file = self.get_temp_file_path(file_id)
        
        if not os.path.exists(temp_file):
            logger.warning(f"No se encontró resultado OCR para el archivo {file_id}")
            return {}
            
        try:
            with open(temp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('result', {})
        except Exception as e:
            logger.error(f"Error cargando resultado OCR: {e}")
            return {}
            
    def process_ocr(self, file_path: str, engine: str = 'tesseract', 
                  is_whiteboard: bool = False, lang: str = 'spa') -> Dict[str, Any]:
        """
        Procesa OCR sin dependencias de TensorFlow.
        
        Args:
            file_path: Ruta al archivo a procesar
            engine: Motor OCR ('tesseract' o 'google_vision')
            is_whiteboard: Si es una imagen de pizarra
            
        Returns:
            Resultado del procesamiento OCR
        """
        from ..services.ocr_processor import process_ocr as ocr_process_function
        
        start_time = time.time()
        
        try:
            # Usar la función process_ocr correcta del módulo ocr_processor
            result = ocr_process_function(
                filepath=file_path,
                engine=engine,
                is_whiteboard=is_whiteboard,
                lang=lang
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f"OCR completado con {engine} en {elapsed_time:.2f}s")
            
            # Incluir metadatos
            result['processing_time'] = f"{elapsed_time:.2f}s"
            result['engine'] = engine
            
            return result
            
        except Exception as e:
            logger.error(f"Error en procesamiento OCR: {e}")
            return {
                'success': False,
                'text': '',
                'error': str(e),
                'processing_time': f"{time.time() - start_time:.2f}s",
                'engine': engine
            }
    
    def generate_summary(self, text: str, async_mode: bool = False, file_id: str = None) -> Tuple[str, Dict[str, Any]]:
        """
        Genera un resumen del texto extraído.
        Si está en modo asíncrono, lo hace en un hilo separado.
        
        Args:
            text: Texto a resumir
            async_mode: Si se debe resumir asíncronamente
            file_id: Identificador opcional para asociar con el resumen
            
        Returns:
            Tupla con (resumen, metadatos)
        """
        if not text or len(text.strip()) < 50:
            return "", {"error": "Texto insuficiente para resumir"}
        
        # Si no hay ID, generar uno basado en hash del texto y timestamp
        if not file_id:
            text_hash = str(hash(text[:100]))  # Hash de los primeros 100 caracteres
            file_id = f"sum_{text_hash}_{int(time.time())}"
            
        if async_mode:
            # Crear archivo temporal con estado "procesando"
            temp_file = self.get_temp_file_path(file_id, prefix="summary_result")
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'timestamp': time.time(),
                        'file_id': file_id,
                        'status': 'processing'
                    }, f, ensure_ascii=False)
            except Exception as e:
                logger.warning(f"No se pudo crear archivo temporal para seguimiento de resumen: {e}")
            
            # Iniciar un hilo separado para el resumen
            summary_thread = threading.Thread(
                target=self._summarize_in_thread,
                args=(text, file_id)
            )
            summary_thread.daemon = True
            summary_thread.start()
            return "", {"status": "summarizing", "async": True, "summary_id": file_id}
        
        return self._summarize_direct(text)
    
    def _summarize_direct(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Ejecuta la generación de resumen directamente.
        
        Args:
            text: Texto a resumir
            
        Returns:
            Tupla con (resumen, metadatos)
        """
        try:
            from ..services.text_summarizer import TextSummarizer
            
            # Verificar si el resumen avanzado está disponible
            from ..services.text_summarizer import HF_AVAILABLE
            
            start_time = time.time()
            summarizer = TextSummarizer()
            
            # Generar resumen
            summary_data = summarizer.generate_summary(text, use_advanced=HF_AVAILABLE)
            summary = summary_data.get("summary", "")
            metadata = summary_data.get("metadata", {})
            
            # Extraer palabras clave
            keywords = summarizer.keywords(text, max_keywords=8)
            
            elapsed_time = time.time() - start_time
            
            # Actualizar metadatos
            metadata.update({
                "keywords": keywords,
                "processing_time": f"{elapsed_time:.2f}s",
                "advanced_mode": HF_AVAILABLE
            })
            
            return summary, metadata
            
        except Exception as e:
            logger.error(f"Error generando resumen: {e}")
            self.summary_error = str(e)
            return "", {"error": str(e)}
    
    def _summarize_in_thread(self, text: str, file_id: str = None):
        """
        Ejecuta resumen en un hilo separado y guarda el resultado.
        
        Args:
            text: Texto a resumir
            file_id: Identificador único del archivo/documento para guardar el resultado
        """
        try:
            # Generar un ID temporal si no se proporciona uno
            if not file_id:
                file_id = f"summary_{int(time.time())}"
                
            summary, metadata = self._summarize_direct(text)
            
            # Guardar el resultado en un archivo temporal
            temp_file = self.get_temp_file_path(file_id, prefix="summary_result")
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': time.time(),
                    'file_id': file_id,
                    'summary': summary,
                    'metadata': metadata,
                    'status': 'completed'
                }, f, ensure_ascii=False)
                
            logger.info(f"Resumen generado en hilo separado y guardado en {temp_file}")
            
        except Exception as e:
            logger.error(f"Error en hilo de resumen: {e}")
            self.summary_error = str(e)
            
            # Guardar el estado de error
            if file_id:
                temp_file = self.get_temp_file_path(file_id, prefix="summary_result")
                try:
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            'timestamp': time.time(),
                            'file_id': file_id,
                            'summary': '',
                            'metadata': {'error': str(e)},
                            'status': 'error'
                        }, f, ensure_ascii=False)
                except Exception as write_error:
                    logger.error(f"No se pudo guardar el error del resumen: {write_error}")
            
    def get_ocr_summary_pipeline(self, file_path: str, engine: str = 'tesseract',
                               is_whiteboard: bool = False, generate_summary: bool = True,
                               async_summary: bool = False, lang: str = 'spa') -> Dict[str, Any]:
        """
        Pipeline completo de OCR y resumen opcional.
        
        Args:
            file_path: Ruta al archivo
            engine: Motor OCR
            is_whiteboard: Si es una imagen de pizarra
            generate_summary: Si se debe generar resumen
            async_summary: Si el resumen debe ser asíncrono
            
        Returns:
            Resultado completo con OCR y resumen
        """
        # Paso 1: Procesar OCR (esto funciona sin TensorFlow)
        ocr_result = self.process_ocr(file_path, engine, is_whiteboard, lang=lang)
        
        # Verificar éxito del OCR
        if not ocr_result.get('success', False):
            return ocr_result
        
        extracted_text = ocr_result.get('text', '')
        
        # Generar un ID único para el documento
        file_id = os.path.basename(file_path)
        file_id = os.path.splitext(file_id)[0]  # Quitar extensión
        doc_id = f"{file_id}_{int(time.time())}"
        
        result = {
            'success': True,
            'text': extracted_text,
            'engine': engine,
            'ocr_processing_time': ocr_result.get('processing_time', ''),
            'doc_id': doc_id
        }
        
        # Paso 2: Generar resumen si se solicita
        if generate_summary and extracted_text:
            try:
                summary, summary_meta = self.generate_summary(
                    extracted_text, 
                    async_mode=async_summary,
                    file_id=doc_id
                )
                
                if not async_summary:
                    result['summary'] = summary
                    result['summary_metadata'] = summary_meta
                else:
                    result['summary_status'] = 'processing'
                    result['summary_id'] = doc_id
            except Exception as e:
                logger.error(f"Error en pipeline de resumen: {e}")
                result['summary_error'] = str(e)
        
        return result
