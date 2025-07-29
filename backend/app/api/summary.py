"""
API endpoints para manejar resúmenes de texto.
Permite consultar el estado de resúmenes generados de manera asíncrona.
"""

import os
import json
import logging
from ..extensions import db
from ..models.note import Note
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..services.ocr_summary_handler import OCRSummaryHandler
from ..services.summary_status_helper import patch_ocr_handler, get_summary_status

# Aplicar el patch para añadir get_summary_status si no existe
patch_ocr_handler()

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint para los endpoints relacionados con resúmenes
summary_bp = Blueprint('summary', __name__, url_prefix='/api/summary')

@summary_bp.route('/check/<summary_id>', methods=['GET'])
@jwt_required()
def check_summary_status(summary_id):
    """Verifica el estado de un resumen asíncrono mediante su ID."""
    if not summary_id:
        return jsonify({'status': 'error', 'error': 'ID de resumen no proporcionado'}), 400
    
    try:
        # Usar directamente get_summary_status del helper o de la clase OCRSummaryHandler si está disponible
        try:
            handler = OCRSummaryHandler()
            # Si el patch se aplicó correctamente, este método existirá
            result = handler.get_summary_status(summary_id)
        except AttributeError:
            # Si el método no existe en la clase, usar la versión del helper
            logging.info(f"Usando helper para consultar estado del resumen {summary_id}")
            result = get_summary_status(summary_id)
            
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error al verificar estado del resumen {summary_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': f"Error al verificar estado: {str(e)}"
        }), 500

@summary_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_summary():
    """
    Genera un resumen de texto de manera asíncrona o síncrona según parámetros.
    
    Request:
        - text: Texto a resumir
        - async_mode: Booleano indicando si el resumen debe ser asíncrono
        
    Returns:
        Resumen generado o ID para consultar el estado si es asíncrono
    """
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'status': 'error',
                'message': 'El texto a resumir es requerido'
            }), 400
        
        text = data.get('text')
        async_mode = data.get('async_mode', False)
        
        # Inicializar el manejador OCR-Resumen
        ocr_handler = OCRSummaryHandler()
        
        # Generar resumen
        summary, metadata = ocr_handler.generate_summary(
            text=text, 
            async_mode=async_mode,
            file_id=data.get('file_id')
        )
        
        if async_mode:
            return jsonify({
                'status': 'processing',
                'summary_id': metadata.get('summary_id', ''),
                'message': 'El resumen se está generando de manera asíncrona'
            }), 202
        else:
            return jsonify({
                'status': 'completed',
                'summary': summary,
                'metadata': metadata
            }), 200
            
    except Exception as e:
        logger.error(f"Error al generar resumen: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error al generar el resumen: {str(e)}'
        }), 500
