"""
Implementación del endpoint /classify para análisis de texto.
Este archivo es temporal y su contenido debe integrarse en backend/app/api/analysis.py
"""

from flask import request, jsonify
import logging
import os
from werkzeug.utils import secure_filename

def classify_text_endpoint():
    """
    Endpoint para clasificar y resumir texto.
    Acepta texto directo o un archivo para OCR.
    Devuelve el resumen, tema principal y temas secundarios.
    
    Este endpoint migra la funcionalidad que antes estaba en /classify en app.py.
    """
    try:
        # Verificar si se envía texto o archivo
        if 'text' in request.form:
            # Usar texto proporcionado directamente
            text = request.form.get('text', '')
            source = "input_directo"
        elif 'file' in request.files:
            # Extraer texto de archivo (imagen/PDF)
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({"error": "No se seleccionó ningún archivo"}), 400
                
            if not allowed_file(file.filename):
                return jsonify({"error": f"Tipo de archivo no permitido. Use: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
            
            # Guardar archivo temporalmente
            filename = secure_filename(file.filename)
            upload_folder = get_upload_folder()
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            # Obtener parámetros OCR
            ocr_engine = request.form.get('ocr_engine', 'tesseract')
            is_whiteboard = request.form.get('is_whiteboard', 'false').lower() == 'true'
            
            # Extraer texto con OCR usando la nueva interfaz unificada
            try:
                from ..services.ocr_processor import process_ocr
                
                # Usar la nueva función unificada de OCR
                ocr_result = process_ocr(
                    filepath=filepath,
                    engine=ocr_engine,
                    is_whiteboard=is_whiteboard,
                    lang='es'
                )
                
                if ocr_result['success']:
                    text = ocr_result['text']
                    source = f"ocr_{ocr_result['engine_used']}"
                else:
                    return jsonify({"error": f"Error en OCR: {ocr_result['error']}"}), 400
                
                # Eliminar archivo temporal
                os.remove(filepath)
            except Exception as e:
                # Limpiar si hay error
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({"error": f"Error en OCR: {str(e)}"}), 400
        else:
            return jsonify({"error": "No se proporcionó texto ni archivo"}), 400
            
        # Verificar longitud del texto
        if not text or len(text.strip()) < 10:
            return jsonify({"error": "Texto insuficiente para procesar"}), 400
            
        # Obtener parámetros opcionales
        compression_ratio = float(request.form.get('compression_ratio', '0.3'))
        top_n_topics = int(request.form.get('top_n_topics', '3'))
        
        # Procesar texto en paralelo (resumen y clasificación)
        logger.info(f"Procesando texto de {len(text)} caracteres")
        
        # Generar resumen con manejo de errores
        try:
            summary_result = summarizer.generate_summary(
                text, 
                compression_ratio=compression_ratio
            )
        except Exception as e:
            logger.error(f"Error al generar resumen: {e}")
            return jsonify({"error": f"Error al generar resumen: {str(e)}"}), 500
        
        # Clasificar temas con manejo de errores
        try:
            topics = classifier.classify_text(text, top_n=top_n_topics)
        except Exception as e:
            logger.error(f"Error al clasificar texto: {e}")
            # Proporcionar un tema genérico en caso de error
            topics = [("General", 1.0)]
        
        # Formatear resultados
        main_topic, main_score = topics[0]
        
        # Resultado final
        result = {
            "text": text[:1000] + "..." if len(text) > 1000 else text,  # Truncar texto largo
            "summary": summary_result["summary"],
            "main_topic": main_topic,
            "main_topic_score": float(main_score),
            "topics": [{"name": t, "score": float(s)} for t, s in topics],
            "metadata": {
                "source": source,
                "chars": len(text),
                "summary_chars": len(summary_result["summary"]),
                "compression_ratio": float(summary_result["real_compression"]),
                "processing_time": float(summary_result["generation_time"])
            }
        }
        
        # Almacenar en Neo4j (opcional) - si está configurado
        try:
            # En la versión reestructurada, podría ser parte de un servicio separado
            # Sólo intentamos si existe la función en el ámbito
            if 'store_in_neo4j' in globals():
                entities = [(main_topic, "TOPIC")] + [(t, "TOPIC") for t, _ in topics[1:]]
                store_in_neo4j(text, summary_result["summary"], entities)
        except Exception as e:
            logger.error(f"Error al almacenar en Neo4j: {e}")
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error en classify_text_endpoint: {e}")
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

# Para integrarse en analysis.py, agregar:
# @api_bp.route('/classify', methods=['POST'])
# def classify_text_endpoint():
#    ... todo el código de la función ...
