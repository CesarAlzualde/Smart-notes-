"""
API para análisis de texto, OCR, y procesamiento de contenido.
"""

from flask import Blueprint, request, jsonify, current_app, url_for, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
import os
import re
from bs4 import BeautifulSoup
import json
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models import Note, User, Topic
from ..models.file import File  # Importando directamente del módulo específico
from PIL import Image
import textstat
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import concurrent.futures
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración para tipos de archivos permitidos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'bmp', 'tiff', 'webp'}

# Funciones auxiliares
def allowed_file(filename):
    """Verifica si la extensión del archivo está permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_thumbnail(image_path, size=(200, 200)):
    """
    Genera una miniatura para una imagen.
    
    Args:
        image_path (str): Ruta a la imagen
        size (tuple): Tamaño de la miniatura (ancho, alto)
        
    Returns:
        str: Ruta a la miniatura generada o None si falla
    """
    try:
        # Crear nombre para miniatura
        filename = os.path.basename(image_path)
        directory = os.path.dirname(image_path)
        name, ext = os.path.splitext(filename)
        thumb_filename = f"{name}_thumb{ext}"
        thumbnail_path = os.path.join(directory, thumb_filename)
        
        # Generar miniatura
        with Image.open(image_path) as img:
            img.thumbnail(size)
            img.save(thumbnail_path, quality=85, optimize=True)
            
        return thumbnail_path
        
    except Exception as e:
        logger.error(f"Error al generar miniatura: {e}")
        return None
        
def _clean_text_for_ai(text: str) -> str:
    """
    Preprocesa y limpia el texto de forma más inteligente, especialmente el de OCR,
    preservando la estructura de párrafos para mejorar la calidad del análisis de IA.
    """
    # 1. Eliminar etiquetas HTML para obtener texto plano.
    # Esto es crucial para evitar que los modelos de IA procesen código HTML.
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text(separator='\n')

    # 2. Normalizar saltos de línea y eliminar retornos de carro
    text = text.replace('\r', '')

    # 3. Unir palabras cortadas por un guion al final de la línea.
    # Ejemplo: "inteligente-\nmente" -> "inteligentemente"
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    # 4. Preservar párrafos. Se identifican por dos o más saltos de línea.
    # Se usa un marcador temporal para no perder esta estructura.
    text = re.sub(r'\n{2,}', '<<PARAGRAPH_BREAK>>', text)

    # 5. Reemplazar los saltos de línea simples restantes con un espacio.
    # Estos suelen ser cortes de línea dentro de un mismo párrafo.
    text = text.replace('\n', ' ')

    # 6. Restaurar los saltos de párrafo para mantener la estructura del texto.
    text = text.replace('<<PARAGRAPH_BREAK>>', '\n\n')

    # 7. Normalizar múltiples espacios/tabulaciones a un solo espacio.
    text = re.sub(r'[ \t]+', ' ', text)

    # 8. Corregir espaciado alrededor de la puntuación para mayor coherencia.
    text = re.sub(r'\s+([.,;!?])', r'\1', text)  # Elimina espacio ANTES de la puntuación.
    text = re.sub(r'([.,;!?])([^\s])', r'\1 \2', text) # Asegura espacio DESPUÉS de la puntuación.
    
    # 9. Se elimina la eliminación agresiva de caracteres y la capitalización forzada.
    # Esto es para evitar destruir información valiosa (símbolos, etc.) y para
    # delegar la corrección gramatical y de estilo a los modelos de IA dedicados,
    # que pueden hacerlo con un mejor contexto.

    return text.strip()

# El blueprint ya se creó en __init__.py, así que usamos el de allí
from . import api_bp

# Verificar disponibilidad de Google Vision OCR
try:
    from ..services.ocr_processor import is_google_vision_available
    google_vision_status = is_google_vision_available()
    logger.info(f"Google Vision OCR disponible: {google_vision_status}")
except ImportError:
    google_vision_status = False
    logger.warning("No se pudo importar el comprobador de Google Vision OCR")

# Helper functions for lazy initialization of services
_summarizer = None
_analyser = None
_ocr_processor = None

def get_summarizer():
    global _summarizer
    if _summarizer is None:
        from ..services.text_summarizer import TextSummarizer
        _summarizer = TextSummarizer()
    return _summarizer

def get_analyser():
    global _analyser
    if _analyser is None:
        from ..services.topic_classifier import NlpAnalyser
        _analyser = NlpAnalyser()
    return _analyser

def get_ocr_processor():
    global _ocr_processor
    if _ocr_processor is None:
        from ..services.ocr_processor import OCRProcessor
        _ocr_processor = OCRProcessor()
    return _ocr_processor

# Configurar rutas de almacenamiento
def get_upload_folder():
    """Obtiene la ruta de la carpeta de uploads desde la configuración."""
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    if not upload_folder:
        # Si no está definida, usar una ruta por defecto relativa al backend
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "static", "uploads")
        
    # Asegurar que existe la carpeta
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder

# Endpoints para compatibilidad con el frontend
@api_bp.route('/analysis/text', methods=['POST'])
@jwt_required()
def analyze_text():
    """Endpoint unificado para análisis de texto que responde a las expectativas del frontend."""
    try:
        # Obtener usuario actual
        current_user = get_jwt_identity()
        
        # Obtener nota a analizar
        data = request.json
        note_id = data.get('note_id')
        text = data.get('text', '')
        
        if not note_id or not text:
            return jsonify({'error': 'Se requiere ID de nota y texto'}), 400
            
        # Limpiar texto para análisis
        original_length = len(text)
        clean_text = _clean_text_for_ai(text)
        logger.info(f"Texto original ({original_length} chars) -> Texto limpio ({len(clean_text)} chars) para la nota {note_id}")
        
        # Verificar longitud para procesamiento adecuado
        if len(clean_text) < 50:  # Umbral mínimo para análisis significativo
            return jsonify({
                'error': 'Texto demasiado corto para analizar',
                'min_chars': 50,
                'provided_chars': len(clean_text)
            }), 400
        
        # --- FASE 1: Corrección gramatical del texto ---
        # NOTA: La corrección gramatical se deshabilita temporalmente por defecto para evitar timeouts en el frontend.
        # Es un proceso muy lento que debe moverse a una tarea en segundo plano (ej. Celery) para reactivarse.
        logger.info("FASE 1: Corrección gramatical (temporalmente deshabilitada por rendimiento).")
        
        text_for_analysis = clean_text
        corrected_text = clean_text
        grammar_result = {'corrected_text': clean_text, 'corrections': []}

        # El siguiente bloque es el código original que se puede reactivar con una tarea asíncrona.
        # skip_grammar = data.get('skip_grammar_correction', True) # Forzar a True para deshabilitar
        # if skip_grammar:
        #     logger.info("Corrección gramatical omitida por solicitud explícita")
        #     text_for_analysis = clean_text
        #     corrected_text = clean_text
        #     grammar_result = {'corrected_text': clean_text, 'corrections': []}
        # else:
        #     try:
        #         logger.info("Iniciando corrección gramatical...")
        #         grammar_result = summarizer.correct_grammar(clean_text)
        #         corrected_text = grammar_result.get('corrected_text', clean_text)
        #         
        #         if corrected_text and len(corrected_text) > 10 and corrected_text != clean_text:
        #             text_for_analysis = corrected_text
        #             logger.info("Corrección gramatical aplicada correctamente")
        #         else:
        #             text_for_analysis = clean_text
        #             logger.info("No fue necesaria la corrección gramatical o no hay modelo disponible")
        #     except Exception as e:
        #         logger.warning(f"No se pudo realizar la corrección gramatical: {e}", exc_info=True)
        #         text_for_analysis = clean_text
        #         corrected_text = clean_text
        #         grammar_result = {'corrected_text': clean_text, 'corrections': []}
        
        # --- FASE 2: Estadísticas y Legibilidad con textstat ---
        try:
            textstat.set_lang('es_ES')
            words = textstat.lexicon_count(text_for_analysis)
            sentences = textstat.sentence_count(text_for_analysis)
            reading_time = max(1, round(words / 200)) # 200 palabras por minuto aprox.
            
            readability_score = textstat.flesch_reading_ease(text_for_analysis)
            
            if readability_score > 80:
                readability_label = "Muy fácil"
            elif readability_score > 60:
                readability_label = "Fácil"
            elif readability_score > 40:
                readability_label = "Moderado"
            elif readability_score > 20:
                readability_label = "Difícil"
            else:
                readability_label = "Muy difícil"
        except Exception as e:
            logger.warning(f"No se pudo calcular la legibilidad con textstat: {e}")
            words, sentences, reading_time, readability_score, readability_label = 0, 0, 0, 0, "No disponible"

        paragraphs = len([p for p in text_for_analysis.split('\n\n') if p.strip()])

        stats_data = {
            'words': int(words),
            'paragraphs': int(paragraphs),
            'sentences': int(sentences),
            'reading_time': int(reading_time),
            'readability': float(readability_score),
            'readability_label': str(readability_label)
        }

        # --- FASE 3: Análisis IA con paralelismo para mayor eficiencia ---
        summarizer = get_summarizer()
        analyser = get_analyser()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_summary = executor.submit(summarizer.generate_summary, text_for_analysis, compression_ratio=0.50)
            future_topics = executor.submit(analyser.classify_text, text_for_analysis, top_n=8)
            future_keywords = executor.submit(summarizer.keywords, text_for_analysis, max_keywords=15)
            future_entities = executor.submit(summarizer.extract_entities, text_for_analysis)
            future_sentiment = executor.submit(summarizer.analyze_sentiment, text_for_analysis)

            # --- FASE 4: Recoger resultados y guardar en DB ---
            
            # 1. Resumen
            try:
                summary_result = future_summary.result(timeout=120)
                summary = summary_result.get('summary', 'No se pudo generar un resumen.')
            except Exception as e:
                logger.error(f"Error al generar resumen: {e}")
                summary = "Error al generar el resumen."

            # 2. Tópicos y guardado en DB
            try:
                topics = future_topics.result(timeout=60)
                main_topic = topics[0][0] if topics else 'General'
                main_score = topics[0][1] if topics else 1.0
                main_score = topics[0][1] if topics else 0.0
                
                # Procesar topics para el frontend
                topics_distribution = []
                suggested_topics = []
                
                if topics:
                    for topic, score in topics:
                        topic_info = {
                            'topic': topic,
                            'weight': float(score)
                        }
                        topics_distribution.append(topic_info)
                        suggested_topics.append(topic)
                else:
                    # Fallback si no hay topics
                    topics_distribution = [{'topic': 'General', 'weight': 1.0}]
                    suggested_topics = ['General']
                
                # Guardar el tema principal en la nota
                note = Note.query.get(note_id)
                if note:
                    # Generar y guardar el embedding semántico
                    try:
                        text_to_embed = note.content
                        if text_to_embed:
                            embedding = analyser.generate_embedding(text_to_embed)
                            if embedding is not None:
                                note.embedding = embedding  # generate_embedding ya devuelve una lista
                                logger.info(f"Embedding generado y asignado para la nota {note_id}")
                            else:
                                logger.warning(f"La generación de embedding no devolvió resultados para la nota {note_id}")
                    except Exception as e:
                        logger.error(f"Error generando embedding para la nota {note_id}: {e}")

                    note.main_topic = main_topic
                    # Guardar cambios en la base de datos
                    db.session.commit()
                    logger.info(f"Análisis y embedding guardados correctamente para la nota {note_id}")
            except Exception as e:
                logger.error(f"Error al clasificar tópicos o guardar en DB: {e}")
                topics = []
                main_topic = 'General'
                main_score = 0.0
                topics_distribution = [{'topic': 'General', 'weight': 1.0}]
                suggested_topics = ['General']

            # 3. Palabras clave
            try:
                keywords = future_keywords.result(timeout=60)
                logger.info(f"Keywords extraídas: {keywords} (tipo: {type(keywords)})")
            except Exception as e:
                logger.error(f"Error al extraer palabras clave: {e}")
                keywords = []

            # 4. Entidades
            try:
                entities = future_entities.result(timeout=60)
                logger.info(f"Entidades extraídas: {entities} (tipo: {type(entities)})")
            except Exception as e:
                logger.error(f"Error al extraer entidades: {e}")
                entities = []

            # 5. Sentimiento
            try:
                sentiment = future_sentiment.result(timeout=60)
            except Exception as e:
                logger.error(f"Error al analizar sentimiento: {e}")
                sentiment = {'label': 'unknown', 'score': 0.0}

            # --- FASE 5: Construir respuesta final ---
            # Preparar datos en el formato esperado por el frontend
            main_topic = topics[0][0] if topics else 'General'
            main_score = topics[0][1] if topics else 1.0
            
            # Convertir a formato esperado por el frontend
            topics_distribution = [{'topic': topic, 'weight': float(score)} for topic, score in topics] if topics else [{'topic': "General", 'weight': 1.0}]
            suggested_topics = [topic for topic, _ in topics] if topics else ["General"]
            concepts_list = keywords if keywords else ["No se encontraron palabras clave"]
            
            # Formatear entidades para que coincida con la estructura de la captura de pantalla
            # El frontend espera un diccionario donde cada clave es un tipo de entidad
            entities_result = {}
            if entities and isinstance(entities, dict):
                for entity_type, entity_items in entities.items():
                    # Asegurarse de que el tipo de entidad es un string y no está vacío
                    if not isinstance(entity_type, str) or not entity_type.strip():
                        continue
                    
                    # Crear una lista de strings para cada tipo de entidad
                    # El frontend espera una lista de strings, no de objetos
                    entities_result[entity_type] = [str(item) for item in entity_items]
            
            # Si no se encontraron entidades, devolver un diccionario vacío
            if not entities_result:
                entities_result = {}
            
            logger.info(f"Entities_result final: {entities_result}")
            logger.info(f"Keywords final (concepts_list): {concepts_list}")
            
            # Formatear sentimiento para frontend
            if sentiment and isinstance(sentiment, dict) and 'label' in sentiment and 'score' in sentiment:
                sentiment_label = sentiment['label']
                sentiment_score = float(sentiment['score'])  # El score ya está en formato porcentual
                sentiment_result = {
                    "label": sentiment_label,
                    "score": sentiment_score,
                    "displayText": f"{sentiment_label}({sentiment_score:.1f}%)"
                }
            else:
                sentiment_result = {
                    "label": "Neutral",
                    "score": 50.0,
                    "displayText": "Neutral(50.0%)"
                }
            
            # Formatear legibilidad para frontend
            # El frontend espera un texto con esta estructura exacta
            readability_display = f"{readability_label}"
            
            # Estructurar resultados como el frontend espera
            response_data = {
                'stats': stats_data,
                'summary': str(summary),
                'sentiment': sentiment_result, # Ya está formateado y casteado
                'readability': {
                    'score': float(readability_score),
                    'grade': str(readability_label),
                    'displayText': str(readability_display)
                },
                'corrected_text': str(grammar_result.get('corrected_text', text_for_analysis)),
                'main_topic': str(main_topic),
                'main_topic_confidence': float(main_score),
                'topics_distribution': topics_distribution, # Ya está formateado y casteado
                'suggested_topics': [str(topic) for topic in suggested_topics],
                'keywords': [str(keyword) for keyword in concepts_list],
                'entities': entities_result, # Ya está formateado y casteado
            }
            
            # Guardar los resultados del análisis en la base de datos
            try:
                # Obtener la nota de la base de datos
                note = Note.query.get(note_id)
                
                if note:
                    # Actualizar campos de la nota con los resultados del análisis
                    note.summary = summary
                    note.main_topic = main_topic
                    note.main_topic_score = float(main_score)
                    
                    # Generar y guardar embedding para búsqueda semántica
                    try:
                        # El método correcto es generate_embedding (singular) y ya devuelve una lista
                        embedding_list = analyser.generate_embedding(text_for_analysis)
                        if embedding_list:
                            note.embedding = embedding_list
                            logger.info(f"Embedding generado y asignado para la nota {note_id}")
                        else:
                            logger.warning(f"La generación de embedding no devolvió resultados para la nota {note_id}")
                    except Exception as e:
                        logger.error(f"Error generando embedding para la nota {note_id}: {e}")
                    
                    # Actualizar topics sugeridos
                    if suggested_topics and len(suggested_topics) > 0:
                        # Añadir tópicos a la nota
                        try:
                            # Buscar o crear topics en la base de datos
                            for topic_name in suggested_topics[:3]:  # Limitar a los 3 primeros
                                if not topic_name or topic_name == "General":
                                    continue
                                
                                # Buscar topic existente o crear uno nuevo
                                topic = Topic.query.filter_by(name=topic_name).first()
                                if not topic:
                                    topic = Topic(name=topic_name)
                                    db.session.add(topic)
                                
                                # Añadir a la nota si no existe ya
                                if topic not in note.topics:
                                    note.topics.append(topic)
                        except Exception as e:
                            logger.error(f"Error al añadir topics a la nota: {e}")
                    
                    note.topics_distribution = response_data.get('topics_distribution')
                    
                    # NUEVO: Guardar keywords y entidades en analysis_cache para mapas conceptuales
                    from datetime import datetime
                    analysis_cache_data = {
                        'keywords': concepts_list,  # Lista de palabras clave
                        'entities': entities_result,  # Diccionario de entidades por tipo
                        'summary': summary,
                        'main_topic': main_topic,
                        'sentiment': sentiment_result,
                        'readability': {
                            'score': float(readability_score),
                            'label': str(readability_label)
                        },
                        'analyzed_at': datetime.utcnow().isoformat(),
                        'stats': stats_data
                    }
                    note.analysis_cache = analysis_cache_data
                    logger.info(f"Keywords y entidades guardadas en analysis_cache para la nota {note_id}")

                    db.session.commit()
                    logger.info(f"Análisis y embedding guardados correctamente para la nota {note_id}")
                else:
                    logger.warning(f"No se encontró la nota con ID {note_id} para guardar el análisis")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error al guardar el análisis en la base de datos: {e}")
            
            # Log de la respuesta antes de enviar para diagnosticar
            logger.info(f"Enviando respuesta al frontend con {len(response_data)} campos")
            logger.debug(f"Resumen enviado: {response_data.get('summary', 'Sin resumen')[:100]}...")
            logger.debug(f"Tema principal: {response_data.get('main_topic', 'Sin tema')}")
            
            # Devolver resultados al frontend en el formato esperado
            return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Error fatal en el endpoint de análisis: {e}", exc_info=True)
        return jsonify({'error': 'Ocurrió un error inesperado durante el análisis.'}), 500

@api_bp.route('/analysis/summarize', methods=['POST'])
@jwt_required()
def summarize_text():
    """Genera un resumen de texto proporcionado."""
    try:
        data = request.json
        
        if not data or not data.get('text'):
            return jsonify({"error": "Se requiere texto para resumir"}), 400
            
        text = data['text']
        max_length = data.get('max_length', 150)  # Longitud máxima del resumen
        
        # Verificar longitud mínima
        if len(text.split()) < 30:  # Menos de 30 palabras
            return jsonify({
                "summary": text,
                "message": "El texto es demasiado corto para resumir"
            }), 200
            
        # Procesar texto
        summarizer = get_summarizer()
        summary = summarizer.summarize(text, max_length)
        
        return jsonify({
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary)
        }), 200
        
    except Exception as e:
        logging.error(f"Error al resumir texto: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/analysis/grammar', methods=['POST'])
@jwt_required()
def correct_grammar():
    """Endpoint específico para corrección gramatical por demanda."""
    try:
        data = request.json
        
        if not data or not data.get('text'):
            return jsonify({"error": "Se requiere texto para corregir"}), 400
            
        text = data['text']
        note_id = data.get('note_id')  # Opcional
        
        # Verificar longitud mínima
        if len(text.split()) < 10:  # Menos de 10 palabras
            return jsonify({
                "corrected_text": text,
                "message": "El texto es demasiado corto para corregir"
            }), 200
        
        # Limpiar texto para análisis
        original_length = len(text)
        clean_text = _clean_text_for_ai(text)
        logger.info(f"Corrección gramatical: Texto original ({original_length} chars) -> Texto limpio ({len(clean_text)} chars)")
        
        # Aplicar corrección gramatical
        logger.info("Iniciando corrección gramatical independiente...")
        summarizer = get_summarizer()
        grammar_result = summarizer.correct_grammar(clean_text)
        corrected_text = grammar_result.get('corrected_text', clean_text)
        
        # Comprobar si hubo cambios significativos
        has_changes = corrected_text and len(corrected_text) > 10 and corrected_text != clean_text

        if has_changes:
            logger.info("Corrección gramatical aplicada correctamente")
            result = {
                "corrected_text": corrected_text,
                "original_text": text,
                "has_changes": True
            }
        else:
            logger.info("No fue necesaria la corrección gramatical o no hay modelo disponible")
            result = {
                "corrected_text": text,
                "original_text": text,
                "has_changes": False,
                "message": "No se detectaron cambios gramaticales necesarios"
            }

        # Si se proporciona note_id y hubo cambios, guardar en metadatos
        if note_id and has_changes:
            note = Note.query.get(note_id)
            current_user = get_jwt_identity()

            if note and str(note.user_id) == str(current_user):
                try:
                    current_metadata = json.loads(note.note_metadata or '{}')
                    current_metadata['grammar_correction'] = {
                        'corrected_text': corrected_text,
                        'timestamp': datetime.now().isoformat(),
                        'applied': False
                    }
                    note.note_metadata = json.dumps(current_metadata)
                    db.session.commit()
                    logger.info(f"Corrección gramatical guardada en metadatos para la nota ID: {note_id}")
                    result['saved'] = True
                except Exception as db_error:
                    db.session.rollback()
                    logger.error(f"Error al guardar la corrección en la BD para la nota {note_id}: {db_error}")
                    result['saved'] = False
                    result['save_error'] = str(db_error)
            elif note:
                # El usuario no es el propietario de la nota
                return jsonify({'error': 'No autorizado para modificar esta nota'}), 403

        return jsonify(result), 200
            

            
    except Exception as e:
        logger.error(f"Error general en endpoint de corrección: {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
        

@api_bp.route('/analysis/classify', methods=['POST'])
@jwt_required()
def classify_text():
    """Clasifica el texto en tópicos/temas."""
    try:
        data = request.json
        
        if not data or not data.get('text'):
            return jsonify({"error": "Se requiere texto para clasificar"}), 400
            
        text = data['text']
        
        # Verificar longitud mínima
        if len(text.split()) < 20:  # Menos de 20 palabras
            return jsonify({
                "topics": [],
                "main_topic": "",
                "message": "El texto es demasiado corto para clasificar"
            }), 200
            
        # Clasificar texto
        analyser = get_analyser()
        main_topic, topics = analyser.classify_text(text)
        
        return jsonify({
            "main_topic": main_topic,
            "topics": topics,
            "confidence": 0.85  # Placeholder para confianza del modelo
        }), 200
        
    except Exception as e:
        logging.error(f"Error al clasificar texto: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/analysis/extract-text', methods=['POST'])
@jwt_required()
def extract_text():
    """Extrae texto de un archivo (OCR para imágenes/PDF)."""
    try:
        user_id = get_jwt_identity()
        
        # Verificar si hay archivo adjunto
        if 'file' not in request.files:
            return jsonify({"error": "No se proporcionó ningún archivo"}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No se seleccionó ningún archivo"}), 400
            
        # Verificar tipo de archivo
        ocr_processor = get_ocr_processor()
        if not ocr_processor.is_supported_filetype(file.filename):
            return jsonify({
                "error": "Tipo de archivo no soportado. Por favor sube una imagen o PDF."
            }), 400
            
        # Guardar archivo temporalmente
        temp_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp')
        os.makedirs(temp_folder, exist_ok=True)
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(temp_folder, filename)
        file.save(filepath)
        
        # Procesar archivo con OCR
        extracted_text = ocr_processor.process_file(filepath)
        
        # Eliminar archivo temporal
        os.remove(filepath)
        
        if not extracted_text:
            return jsonify({
                "error": "No se pudo extraer texto del archivo. Verifica que el archivo tenga contenido textual."
            }), 400
            
        # Analizar el texto extraído
        summarizer = get_summarizer()
        summary = summarizer.summarize(extracted_text)
        analyser = get_analyser()
        main_topic, topics = analyser.classify_text(extracted_text)
        # Extraer palabras clave
        keywords = summarizer.keywords(extracted_text)
        
        # Construir la respuesta final
        response_data = {
            'extracted_text': extracted_text,
            'summary': summary,
            'main_topic': main_topic,
            'topics': topics,
            'ai_keywords': keywords, # Renombrado para coincidir con el frontend
            'text_length': len(extracted_text)
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logging.error(f"Error al extraer texto: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/notes/<int:note_id>/analyze', methods=['POST'])
@jwt_required()
def process_note(note_id):
    """Procesa una nota existente con IA (resumen y clasificación)."""
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        
        if not note:
            return jsonify({"error": "Nota no encontrada"}), 404
            
        if not note.content or len(note.content) < 50:
            return jsonify({"error": "El contenido de la nota es demasiado corto para procesar"}), 400
            
        # --- Realizar análisis completo en paralelo ---
        text_content = _clean_text_for_ai(note.content)
        
        summarizer = get_summarizer()
        analyser = get_analyser()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_summary = executor.submit(summarizer.generate_summary, text_content)
            future_topics = executor.submit(analyser.classify_text, text_content)
            future_embedding = executor.submit(analyser.generate_embedding, text_content)
            future_keywords = executor.submit(analyser.extract_keywords, text_content)
            future_entities = executor.submit(summarizer.extract_entities, text_content)

            summary_result = future_summary.result()
            topics = future_topics.result()
            embedding = future_embedding.result()
            keywords = future_keywords.result()
            entities = future_entities.result()

        # Consolidar todos los resultados del análisis
        analysis_data = {
            'summary': summary_result.get('summary'),
            'topics': topics,
            'keywords': keywords,
            'entities': entities,
            'metadata': summary_result.get('metadata', {})
        }

        # Actualizar la nota con los resultados del análisis
        note.summary = summary_result.get('summary') # Guardar resumen en el campo principal
        note.analysis_cache = analysis_data
        
        if embedding is not None:
            note.embedding = embedding
        
        db.session.commit()
        
        # Devolver el análisis completo junto con el mensaje
        return jsonify({
            "message": "Nota procesada correctamente",
            "analysis": analysis_data,
            "note_id": note.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al procesar nota {note_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/analysis/extract-concepts', methods=['POST'])
@jwt_required()
def extract_concepts():
    """Extrae conceptos y relaciones para mapas conceptuales."""
    try:
        data = request.json
        
        if not data or not data.get('text'):
            return jsonify({"error": "Se requiere texto para extraer conceptos"}), 400
            
        text = data['text']
        
        # Verificar longitud mínima
        if len(text.split()) < 50:  # Menos de 50 palabras
            return jsonify({
                "concepts": [],
                "relations": [],
                "message": "El texto es demasiado corto para extraer conceptos relevantes"
            }), 200
            
        # Esta función podría implementarse con NLP más avanzado
        # Por ahora es un placeholder
        concepts = [
            {"id": "1", "label": "Concepto 1", "weight": 0.9},
            {"id": "2", "label": "Concepto 2", "weight": 0.8},
            {"id": "3", "label": "Concepto 3", "weight": 0.7},
        ]
        
        relations = [
            {"source": "1", "target": "2", "label": "relación", "weight": 0.8},
            {"source": "1", "target": "3", "label": "deriva en", "weight": 0.6},
        ]
        
        return jsonify({
            "concepts": concepts,
            "relations": relations
        }), 200
        
    except Exception as e:
        logging.error(f"Error al extraer conceptos: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/upload', methods=['POST'])
@jwt_required()
def process_file_upload():
    """Endpoint para procesar archivos subidos mediante OCR, resumen y clasificación de temas.
    
    Este endpoint migra la funcionalidad que antes estaba en /api/upload en app.py.
    Procesa imágenes y PDFs utilizando OCR avanzado (Google Vision cuando está disponible),
    extrae texto, genera resúmenes, y clasifica el contenido en temas.
    
    Se puede usar tanto con autenticación como sin ella.
    """
    try:
        # Verificar si hay archivo adjunto
        if 'file' not in request.files:
            return jsonify({"error": "No se envió ningún archivo"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No se seleccionó ningún archivo"}), 400
            
        if not allowed_file(file.filename):
            return jsonify({"error": "Tipo de archivo no permitido"}), 400

        # Obtiene parámetros de la solicitud
        ocr_engine = request.form.get('ocr_engine', 'tesseract')  # tesseract o google_vision
        is_whiteboard = request.form.get('is_whiteboard', 'false').lower() == 'true'
        language = request.form.get('language', 'es')
        
        # Seguridad del nombre de archivo
        filename = secure_filename(file.filename)
        
        # Obtener carpeta de uploads y asegurar que exista
        upload_folder = get_upload_folder()
        
        # Define la ruta donde se guardará el archivo
        file_path = os.path.join(upload_folder, filename)
        
        # Guardar el archivo
        file.save(file_path)
        logger.debug(f"Archivo guardado en {file_path}")
        
        # Procesamiento de imagen con OCR
        try:
            # Preparar el método OCR según el motor seleccionado
            ocr_processor = get_ocr_processor()
            if ocr_engine == 'google_vision' and google_vision_status:
                # Usar Google Vision OCR
                logger.debug("Usando Google Vision OCR")
                if is_whiteboard:
                    text = extract_text_for_whiteboard(file_path)
                else:
                    text = google_vision_ocr(file_path, lang=language, is_whiteboard=is_whiteboard)
            else:
                # Usar Tesseract por defecto
                logger.debug("Usando Tesseract OCR")
                text = ocr_processor.process_file(file_path, is_whiteboard=is_whiteboard)
            
            logger.debug(f"Texto extraído: {text[:100]}...") if text else logger.debug("No se extrajo texto")
            
            # Generar vista previa de la imagen (thumbnail)
            thumbnail_url = None
            if file.content_type.startswith('image/'):
                try:
                    thumbnail_path = create_thumbnail(file_path)
                    if thumbnail_path:
                        # Generar URL relativa para la miniatura
                        thumbnail_url = f'/uploads/{os.path.basename(thumbnail_path)}'
                except Exception as e:
                    logger.error(f"Error creando miniatura: {e}")
            
            # Sumario del texto (solo si hay suficiente contenido)
            summary = None
            if text and len(text) > 100:
                try:
                    summarizer = get_summarizer()
                    summary = summarizer.summarize(text)
                except Exception as e:
                    logger.error(f"Error al resumir el texto: {e}")
            
            # Extraer entidades
            entities = None
            try:
                if text:
                    summarizer = get_summarizer()
                    entities = summarizer.extract_entities(text)
            except Exception as e:
                logger.error(f"Error al extraer entidades: {e}")
            
            # Clasificar por tópico
            topics = []
            confidence_scores = []
            try:
                if text and len(text) > 100:
                    # Utilizar el clasificador de tópicos
                    analyser = get_analyser()
                    topic_prediction = analyser.classify_text(text)
                    
                    # Ordenamos por puntuación descendente
                    sorted_topics = sorted(topic_prediction.items(), key=lambda x: x[1], reverse=True)
                    
                    # Tomamos los primeros 3 tópicos con puntuación > 0.1
                    for topic, score in sorted_topics:
                        if score > 0.1 and len(topics) < 3:
                            topics.append(topic)
                            confidence_scores.append(float(score))
            except Exception as e:
                logger.error(f"Error al clasificar tópicos: {e}")
            
            # Preparar respuesta
            response = {
                "text": text,
                "summary": summary,
                "entities": entities,
                "topics": topics,
                "topic_scores": confidence_scores,
                "thumbnail_url": thumbnail_url,
                "path": filename,
                "corrected_summary": summary  # Campo agregado
            }
            
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Error procesando archivo: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Error procesando archivo: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"Error general: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route('/classify', methods=['POST'])
@jwt_required()
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
            summarizer = get_summarizer()
            summary_result = summarizer.generate_summary(
                text, 
                compression_ratio=compression_ratio
            )
        except Exception as e:
            logger.error(f"Error al generar resumen: {e}")
            return jsonify({"error": f"Error al generar resumen: {str(e)}"}), 500
        
        # Clasificar temas con manejo de errores
        try:
            analyser = get_analyser()
            topics = analyser.classify_text(text, top_n=top_n_topics)
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
