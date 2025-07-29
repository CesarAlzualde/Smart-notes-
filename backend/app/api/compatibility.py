"""
Endpoints de compatibilidad para asegurar que las versiones antiguas del frontend 
sigan funcionando con los nuevos cambios del backend.
"""

import logging
from flask import Blueprint, request, jsonify, url_for, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import File
from ..services.ocr_processor import OCRProcessor
from ..services.ocr_summary_handler import OCRSummaryHandler

from datetime import datetime
import os

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint para rutas de compatibilidad
compat_bp = Blueprint('compatibility', __name__)


@compat_bp.route('/files/<file_id>/extract-text', methods=['POST'])
@jwt_required()
def process_file_ocr_compat(file_id):
    """
    Endpoint de compatibilidad para mantener funcionando el frontend actual.
    Este endpoint traduce las llamadas antiguas al nuevo sistema.
    """
    try:
        logger.info(f"Llamada a endpoint de compatibilidad para OCR: /files/{file_id}/extract-text")
        
        data = request.json or {}
        engine = data.get('engine', 'auto')
        is_whiteboard = data.get('isWhiteboard', False)
        # Manejar posible errata en el nombre del campo 'language' desde el frontend
        lang = data.get('language', data.get('Languag e', 'spa'))

        if engine == 'google':
            engine = 'google_vision'
        elif engine == 'auto' or not engine:
            engine = 'tesseract'
            
        file = File.query.get(file_id)
        if not file:
            logger.error(f"Archivo con ID {file_id} no encontrado.")
            return jsonify({"error": "Archivo no encontrado"}), 404

        user_id = get_jwt_identity()
        if file.user_id != int(user_id):
            logger.warning(f"Acceso denegado para usuario {user_id} al archivo {file_id}.")
            return jsonify({"error": "No tienes permiso para acceder a este archivo"}), 403
            
        file_path = file.filepath
        
        if not os.path.exists(file_path):
            logger.error(f"El archivo {file_path} para el ID {file_id} no existe en el disco.")
            return jsonify({"error": "No se encuentra el archivo en el servidor"}), 404
            
        if engine == 'google_vision':
            ocr_processor = OCRProcessor()
            if not ocr_processor.is_google_vision_available():
                logger.warning("Se solicitó Google Vision, pero no está disponible.")
                return jsonify({"error": "Google Vision API no está disponible"}), 503
    
        ocr_handler = OCRSummaryHandler()
        
        result = ocr_handler.get_ocr_summary_pipeline(
            file_path=file_path,
            engine=engine, 
            is_whiteboard=is_whiteboard,
            generate_summary=True,
            async_summary=False,
            lang=lang
        )
        
        if not result.get('success', False):
            error_msg = result.get('error', 'Error desconocido')
            logger.error(f"Error procesando OCR para archivo {file_id}: {error_msg}")
            return jsonify({"error": f"Error procesando OCR: {error_msg}"}), 500
            
        extracted_text = result.get('text', '')
        engine_used = result.get('engine', engine)
        summary = result.get('summary', '')
        
        file.processed = True
        file.processing_status = 'completed'
        file.extract_text = extracted_text
        
        import json
        metadata = file.file_metadata or {}
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except json.JSONDecodeError:
                metadata = {}
        
        metadata.update({
            'summary': summary,
            'engine': engine_used,
            'processed_at': datetime.utcnow().isoformat()
        })
        file.file_metadata = json.dumps(metadata)
            
        db.session.commit()
        
        logger.info(f"Procesamiento OCR completado para file_id: {file_id}.")
        
        return jsonify({
            "message": "Archivo procesado correctamente",
            "engine": engine_used,
            "extracted_text": extracted_text,
            "summary": summary,
            "text_length": len(extracted_text),
            "file_id": file_id,
            "success": True
        }), 200
        
    except Exception as e:
        logger.error(f"Error fatal en endpoint de compatibilidad process_file_ocr_compat: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor: " + str(e)}), 500
