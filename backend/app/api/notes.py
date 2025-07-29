"""
API para gestión de notas.
Proporciona endpoints para crear, leer, actualizar y eliminar notas.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import logging
import threading
from flask import current_app
from datetime import datetime
from sqlalchemy import desc, func
from ..extensions import db
from ..models.note import Note, note_tag
from ..models.tag import Tag
from ..models.topic import Topic
from ..models.file import File
from ..utils.helpers import save_file, allowed_file
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# El blueprint ya se creó en __init__.py, así que usamos el de allí
from . import api_bp

# Inicializar modelos de IA con carga perezosa (lazy loading)
summarizer = None
classifier = None

def get_summarizer():
    global summarizer
    if summarizer is None:
        from app.services.text_summarizer import TextSummarizer
        summarizer = TextSummarizer()
    return summarizer

def get_classifier():
    global classifier
    if classifier is None:
        from ..services.topic_classifier import NlpAnalyser
        classifier = NlpAnalyser()
    return classifier

@api_bp.route('/notes', methods=['GET'])
@jwt_required()
def get_notes():
    """Obtiene todas las notas del usuario actual."""
    try:
        user_id = get_jwt_identity()
        
        # Log de filtros recibidos para debug
        logger.info(f"🔍 Filtros recibidos: {dict(request.args)}")
        
        # Parámetros de consulta con validación
        page = max(1, request.args.get('page', 1, type=int))  # Asegurar que page sea al menos 1
        per_page = min(max(1, request.args.get('per_page', 10, type=int)), 100)  # Entre 1 y 100
        
        # Filtros de búsqueda y clasificación
        search = request.args.get('search')
        tag = request.args.get('tag')
        topic = request.args.get('topic')
        topic_id = request.args.get('topic_id')
        date_filter = request.args.get('date_filter')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        source_types = request.args.getlist('source_types')  # Para múltiples valores
        sort_param = request.args.get('sort', 'created_at')
        
        # Mapear el parámetro 'sort' del frontend a sort_by y sort_dir
        sort_mapping = {
            'created_at': ('created_at', 'desc'),
            'updated_at': ('updated_at', 'desc'),
            'title': ('title', 'asc'),
            'topic': ('main_topic', 'asc'),
            'relevance': ('created_at', 'desc'),  # Por defecto para relevancia
            'newest': ('created_at', 'desc'),     # Más recientes
            'oldest': ('created_at', 'asc')       # Más antiguas
        }
        
        sort_by, sort_dir = sort_mapping.get(sort_param, ('created_at', 'desc'))
        
        # Validar sort_by para asegurar que es un atributo válido del modelo Note
        valid_sort_fields = ['id', 'title', 'created_at', 'updated_at', 'main_topic']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'  # Valor por defecto si no es válido
        
        # Construir consulta base
        query = Note.query.filter_by(user_id=user_id)
        
        # Filtrar por etiqueta si se especifica
        if tag:
            query = query.join(Note.tags).filter(Tag.name == tag)
            
        # Filtrar por tema si se especifica (topic o topic_id)
        if topic:
            query = query.filter(Note.main_topic == topic)
        elif topic_id:
            # Si topic_id es numérico, buscar por ID en la tabla de topics
            try:
                topic_id_int = int(topic_id)
                # Buscar el nombre del tema por ID
                topic_result = db.session.query(Note.main_topic)\
                    .filter(Note.user_id == user_id, Note.main_topic != None, Note.main_topic != '')\
                    .distinct()\
                    .order_by(Note.main_topic)\
                    .offset(topic_id_int - 1)\
                    .limit(1)\
                    .first()
                if topic_result:
                    query = query.filter(Note.main_topic == topic_result[0])
            except (ValueError, TypeError):
                # Si no es numérico, tratarlo como nombre de tema
                query = query.filter(Note.main_topic == topic_id)
        
        # Filtrar por tipo de fuente
        if source_types:
            logger.info(f"🗄 Filtrando por tipos de fuente: {source_types}")
            source_conditions = []
            for source_type in source_types:
                if source_type.lower() == 'texto':
                    source_conditions.append(Note.source_type == 'text')
                elif source_type.lower() == 'ocr':
                    source_conditions.append(Note.source_type == 'ocr')
                elif source_type.lower() == 'pdf':
                    source_conditions.append(Note.source_type == 'pdf')
                else:
                    source_conditions.append(Note.source_type == source_type)
            
            if source_conditions:
                query = query.filter(db.or_(*source_conditions))
        
        # Filtrar por fecha
        if date_filter:
            from datetime import datetime, timedelta
            now = datetime.now()
            
            if date_filter == 'today':
                start_date = datetime(now.year, now.month, now.day)
                query = query.filter(Note.created_at >= start_date)
            elif date_filter == 'yesterday':
                yesterday = now - timedelta(days=1)
                start_date = datetime(yesterday.year, yesterday.month, yesterday.day)
                end_date = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
                query = query.filter(Note.created_at >= start_date, Note.created_at <= end_date)
            elif date_filter == 'last_7_days':
                start_date = now - timedelta(days=7)
                start_date = datetime(start_date.year, start_date.month, start_date.day)
                query = query.filter(Note.created_at >= start_date)
            elif date_filter == 'last_30_days':
                start_date = now - timedelta(days=30)
                start_date = datetime(start_date.year, start_date.month, start_date.day)
                query = query.filter(Note.created_at >= start_date)
            elif date_filter == 'this_week':
                start_date = now - timedelta(days=now.weekday())
                start_date = datetime(start_date.year, start_date.month, start_date.day)
                query = query.filter(Note.created_at >= start_date)
            elif date_filter == 'this_month':
                start_date = datetime(now.year, now.month, 1)
                query = query.filter(Note.created_at >= start_date)
            elif date_filter == 'this_year':
                start_date = datetime(now.year, 1, 1)
                query = query.filter(Note.created_at >= start_date)
            elif date_filter == 'custom' and (date_from or date_to):
                if date_from:
                    try:
                        from_date = datetime.strptime(date_from, '%Y-%m-%d')
                        query = query.filter(Note.created_at >= from_date)
                    except ValueError:
                        logger.warning(f"Formato de fecha inválido para date_from: {date_from}")
                if date_to:
                    try:
                        to_date = datetime.strptime(date_to, '%Y-%m-%d')
                        # Añadir 23:59:59 para incluir todo el día
                        to_date = to_date.replace(hour=23, minute=59, second=59)
                        query = query.filter(Note.created_at <= to_date)
                    except ValueError:
                        logger.warning(f"Formato de fecha inválido para date_to: {date_to}")
        
        # Buscar en título y contenido
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Note.title.ilike(search_term),
                    Note.content.ilike(search_term)
                )
            )
            
        # Ordenar resultados con manejo de excepciones
        try:
            if sort_dir == 'desc':
                query = query.order_by(desc(getattr(Note, sort_by)))
            else:
                query = query.order_by(getattr(Note, sort_by))
        except Exception as e:
            logging.warning(f"Error al ordenar por {sort_by}: {e}, usando created_at por defecto")
            query = query.order_by(desc(Note.created_at))  # Fallback a ordenación por defecto
            
        # Paginar resultados con manejo de errores
        try:
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            # Preparar respuesta con validación
            notes = [note.to_dict() for note in pagination.items]
            
            return jsonify({
                'notes': notes,
                'total': pagination.total if hasattr(pagination, 'total') else 0,
                'pages': pagination.pages if hasattr(pagination, 'pages') else 0,
                'page': page,
                'per_page': per_page
            }), 200
        except Exception as e:
            logging.error(f"Error en la paginación: {e}")
            # Respuesta de fallback sin paginación
            notes = [note.to_dict() for note in query.limit(per_page).all()]
            return jsonify({
                'notes': notes,
                'total': len(notes),
                'pages': 1,
                'page': 1,
                'per_page': per_page,
                'error': 'Error en la paginación, mostrando resultados limitados'
            }), 200
        
    except Exception as e:
        logging.error(f"Error al obtener notas: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/notes/<int:note_id>', methods=['GET'])
@jwt_required()
def get_note(note_id):
    """Obtiene una nota específica por ID."""
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        
        if not note:
            return jsonify({"error": "Nota no encontrada"}), 404
            
        return jsonify(note.to_dict()), 200
        
    except Exception as e:
        logging.error(f"Error al obtener nota {note_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/notes/recent', methods=['GET'])
@jwt_required()
def get_recent_notes():
    """Obtiene las notas más recientes del usuario."""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 5, type=int)
        
        notes = Note.query.filter_by(user_id=user_id) \
                .order_by(Note.created_at.desc()) \
                .limit(limit) \
                .all()
                
        return jsonify([note.to_dict() for note in notes]), 200
        
    except Exception as e:
        logging.error(f"Error al obtener notas recientes: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/notes', methods=['POST'])
@jwt_required()
def create_note():
    """Crea una nueva nota."""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        # Validar datos mínimos
        if not data.get('title') or not data.get('content'):
            return jsonify({"error": "Se requiere título y contenido"}), 400
            
        # Crear nota
        note = Note(
            title=data['title'],
            content=data['content'],
            summary=data.get('summary'),
            user_id=user_id,
            source_type="text"
        )
        
        # Procesar con IA si se solicita explícitamente
        if data.get('process_ai', False) and len(data['content']) > 50:
            note.process_with_ai(get_summarizer(), get_classifier())
            
        # Agregar etiquetas si se proporcionan
        if 'tags' in data and isinstance(data['tags'], list):
            for tag_name in data['tags']:
                tag = Tag.get_or_create(tag_name)
                note.tags.append(tag)
                
        # Guardar en la base de datos
        db.session.add(note)
        db.session.commit()


        
        return jsonify(note.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al crear nota: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/notes/from-file', methods=['POST'])
@jwt_required()
def create_note_from_file():
    """Crea una nueva nota a partir de un archivo procesado por OCR, incluyendo etiquetas."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Cuerpo de la petición JSON inválido"}), 400

        file_id = data.get('file_id')
        title = data.get('title')
        tags_data = data.get('tags', [])
        current_user_id = get_jwt_identity()

        if not file_id:
            return jsonify({"error": "El campo 'file_id' es requerido"}), 400

        file = File.query.filter_by(id=file_id, user_id=current_user_id).first()
        if not file:
            return jsonify({"error": "Archivo no encontrado o no autorizado"}), 404

        final_title = title if title and title.strip() else file.filename

        new_note = Note(
            title=final_title,
            content=file.extract_text or "",
            user_id=current_user_id,
            file_id=file.id,
            source_type='ocr'
        )
        db.session.add(new_note)

        if tags_data and isinstance(tags_data, list):
            for tag_name in tags_data:
                if not isinstance(tag_name, str) or not tag_name.strip():
                    continue
                tag = Tag.get_or_create(tag_name.strip())
                new_note.tags.append(tag)
        
        db.session.commit()

        return jsonify(new_note.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al crear nota desde archivo: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/notes/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    """Actualiza una nota existente de forma segura, evitando la sobreescritura con datos vacíos."""
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()

        if not note:
            return jsonify({"error": "Nota no encontrada"}), 404

        data = request.json
        if not data:
            return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400

        if 'title' in data:
            if data['title'] or not note.title:
                note.title = data['title']
        
        if 'content' in data:
            if data['content'] or not note.content:
                note.content = data['content']

        if 'summary' in data:
            note.summary = data.get('summary')

        if 'main_topic' in data:
            note.main_topic = data.get('main_topic')

        if 'tags' in data and isinstance(data['tags'], list):
            new_tags = []
            for tag_name in data['tags']:
                if isinstance(tag_name, str) and tag_name.strip():
                    tag = Tag.get_or_create(tag_name.strip())
                    new_tags.append(tag)
            note.tags = new_tags

        if 'topics' in data and isinstance(data['topics'], list):
            new_topics = []
            for topic_name in data['topics']:
                if isinstance(topic_name, str) and topic_name.strip():
                    topic = Topic.get_or_create(topic_name.strip())
                    new_topics.append(topic)
            note.topics = new_topics

        note.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify(note.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al actualizar nota {note_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/notes/<int:note_id>/semantically-related', methods=['GET'])
@jwt_required(optional=True)
def get_semantically_related_notes(note_id):
    logger.debug(f"Buscando notas relacionadas para la nota ID: {note_id}")
    try:
        current_user_id = get_jwt_identity()
        
        if not current_user_id:
            logger.info(f"Acceso no autenticado a notas relacionadas para la nota {note_id}. Devolviendo lista vacía.")
            return jsonify({"related_notes": [], "message": "Authentication is required to view related notes."}), 200

        logger.info(f"Petición autenticada por el usuario ID: {current_user_id}")

        main_note = Note.query.filter_by(id=note_id, user_id=current_user_id).first()

        if not main_note:
            logger.warning(f"Nota principal {note_id} no encontrada para el usuario {current_user_id}")
            return jsonify({"related_notes": [], "message": "Main note not found or access denied."}), 404

        if not main_note.embedding:
            logger.info(f"La nota principal {note_id} no tiene embedding. No se pueden buscar relacionadas.")
            return jsonify({"related_notes": [], "message": "No embedding available for the main note."}), 200
        
        # Normalizar embedding de la nota principal
        try:
            # Intentar convertir a numpy array, asegurando que es una lista
            if isinstance(main_note.embedding, list):
                main_embedding_data = main_note.embedding
            elif hasattr(main_note.embedding, 'tolist'):
                main_embedding_data = main_note.embedding.tolist()
            else:
                main_embedding_data = list(main_note.embedding)
                
            logger.info(f"Nota principal {note_id} tiene embedding de tamaño: {len(main_embedding_data)}")
            main_embedding = np.array(main_embedding_data).reshape(1, -1)
            main_embedding_dim = main_embedding.shape[1]  # Dimensión esperada
        except Exception as e:
            logger.error(f"Error procesando embedding de nota principal {note_id}: {e}")
            return jsonify({"related_notes": [], "error": "Error processing main note embedding."}), 500

        # Obtener otras notas con embeddings
        other_notes = Note.query.filter(
            Note.id != note_id, 
            Note.user_id == current_user_id, 
            Note.embedding.isnot(None)
        ).all()

        if not other_notes:
            logger.info(f"No se encontraron otras notas con embeddings para el usuario {current_user_id}")
            return jsonify({"related_notes": []})
        
        logger.info(f"Encontradas {len(other_notes)} otras notas con embeddings para comparar")
        
        # Filtrar y normalizar embeddings para asegurar compatibilidad
        valid_notes = []
        valid_embeddings = []
        
        for note in other_notes:
            try:
                # Normalizar embedding para que sea una lista
                if isinstance(note.embedding, list):
                    embedding_data = note.embedding
                elif hasattr(note.embedding, 'tolist'):
                    embedding_data = note.embedding.tolist()
                else:
                    embedding_data = list(note.embedding)
                    
                # Convertir a numpy array
                embedding_array = np.array(embedding_data)
                
                # Verificar que la dimensión coincida con el embedding principal
                if embedding_array.size == main_embedding_dim:
                    valid_notes.append(note)
                    valid_embeddings.append(embedding_array)
                else:
                    logger.warning(f"Nota {note.id} tiene embedding con dimensión incompatible: {embedding_array.size} vs {main_embedding_dim}")
            except Exception as e:
                logger.warning(f"Error procesando embedding de nota {note.id}: {e}")
                continue
        
        if not valid_notes:
            logger.info(f"No hay notas con embeddings válidos para comparar")
            return jsonify({"related_notes": []})
            
        # Crear matrices para cálculo de similitud
        other_embeddings = np.vstack(valid_embeddings)
        note_ids = [note.id for note in valid_notes]
        note_titles = [note.title for note in valid_notes]

        # Calcular similitud coseno
        similarities = cosine_similarity(main_embedding, other_embeddings)[0]
        
        # Obtener los índices de las notas más similares (hasta 5)
        top_indices = np.argsort(similarities)[::-1][:5]
        
        logger.info(f"Top {len(top_indices)} índices: {top_indices}")
        
        # Filtrar notas con similitud > 0.2
        related_notes = [
            {"id": note_ids[i], "title": note_titles[i], "similarity": float(similarities[i])}
            for i in top_indices if similarities[i] > 0.2
        ]
        logger.info(f"Encontradas {len(related_notes)} notas relacionadas para la nota {note_id} (umbral: 0.2)")
        return jsonify({"related_notes": related_notes})
    
    except Exception as e:
        logger.error(f"Error crítico obteniendo notas relacionadas para {note_id}: {e}", exc_info=True)
        return jsonify({"related_notes": [], "error": "An internal error occurred."}), 500


def run_note_processing(app, note_id):
    with app.app_context():
        from ..tasks.note_tasks import process_note
        try:
            logging.info(f"[Thread] Iniciando procesamiento para la nota {note_id}")
            process_note(note_id)
            logging.info(f"[Thread] Procesamiento para la nota {note_id} completado.")
        except Exception as e:
            logging.error(f"[Thread] Error en el procesamiento de la nota {note_id}: {e}")


@api_bp.route('/notes/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    """Elimina una nota."""
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        
        if not note:
            return jsonify({"error": "Nota no encontrada"}), 404
            
        # Eliminar nota
        db.session.delete(note)
        db.session.commit()
        
        return jsonify({"message": "Nota eliminada correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al eliminar nota {note_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/notes/statistics', methods=['GET'])
@jwt_required()
def get_note_stats():
    """Obtiene estadísticas sobre las notas del usuario."""
    try:
        user_id = get_jwt_identity()
        
        # Estadísticas básicas
        total_notes = Note.query.filter_by(user_id=user_id).count()
        
        # Notas por tema
        topic_stats = db.session.query(
            Note.main_topic, 
            func.count(Note.id).label('count')
        ).filter_by(user_id=user_id).group_by(Note.main_topic).all()
        
        # Filtrar None y crear diccionario
        topic_dict = {(topic or 'Sin clasificar'): count for topic, count in topic_stats if topic is not None}
        
        # Notas por tipo de fuente
        source_stats = db.session.query(
            Note.source_type, 
            func.count(Note.id).label('count')
        ).filter_by(user_id=user_id).group_by(Note.source_type).all()
        
        # Filtrar None y crear diccionario
        source_dict = {(source or 'Sin tipo'): count for source, count in source_stats if source is not None}
        
        # Estadísticas por mes - usando to_char para PostgreSQL en lugar de date_format (MySQL)
        try:
            # Para PostgreSQL
            month_stats = db.session.query(
                func.to_char(Note.created_at, 'YYYY-MM').label('month'),
                func.count(Note.id).label('count')
            ).filter_by(user_id=user_id).group_by('month').order_by('month').all()
        except Exception as e:
            logging.error(f"Error con func.to_char: {e}")
            # Si falla, usar una forma alternativa compatible
            from sqlalchemy.sql.expression import extract
            month_stats = db.session.query(
                (extract('year', Note.created_at).cast(String) + '-' + 
                 extract('month', Note.created_at).cast(String).concat('00').substr(1,2)
                ).label('month'),
                func.count(Note.id).label('count')
            ).filter_by(user_id=user_id).group_by('month').order_by('month').all()
        
        monthly_list = [{'month': month, 'count': count} for month, count in month_stats]
        
        return jsonify({
            'total': total_notes,
            'by_topic': topic_dict,
            'by_source': source_dict,
            'monthly': monthly_list
        }), 200
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logging.error(f"Error al obtener estadísticas: {e}\n{error_traceback}")
        return jsonify({
            "error": f"Error al obtener estadísticas: {str(e)}",
            "traceback": error_traceback
        }), 500


@api_bp.route('/notes/topics', methods=['GET'])
@jwt_required()
def get_topics():
    """Obtiene todos los temas únicos de las notas del usuario."""
    try:
        user_id = get_jwt_identity()
        
        # Consultar temas únicos
        topics = db.session.query(Note.main_topic)\
            .filter(Note.user_id == user_id, Note.main_topic != None, Note.main_topic != '')\
            .distinct()\
            .order_by(Note.main_topic)\
            .all()
        
        # Convertir a lista de objetos con id y name para compatibilidad con el frontend
        topic_list = []
        for index, topic_tuple in enumerate(topics):
            topic_name = topic_tuple[0]
            if topic_name:  # Solo incluir temas no vacíos
                # Contar notas con este tema principal
                note_count = Note.query.filter_by(
                    user_id=user_id, 
                    main_topic=topic_name
                ).count()
                
                # Agregar tema como objeto con ID
                topic_list.append({
                    'id': index + 1,  # ID secuencial para garantizar unicidad
                    'name': topic_name,
                    'note_count': note_count
                })
        
        # Si no hay temas, proporcionar temas predeterminados
        if not topic_list:
            logging.warning("No se encontraron temas en /api/notes/topics. Proporcionando predeterminados.")
            default_topics = [
                {'id': 1, 'name': 'Arquitectura', 'note_count': 0},
                {'id': 2, 'name': 'Derecho y Leyes', 'note_count': 0},
                {'id': 3, 'name': 'Gestión de Proyectos', 'note_count': 0},
                {'id': 4, 'name': 'Diseño Gráfico', 'note_count': 0},
                {'id': 5, 'name': 'Educación', 'note_count': 0},
                {'id': 6, 'name': 'Desarrollo Personal', 'note_count': 0},
                {'id': 7, 'name': 'Emprendimiento', 'note_count': 0},
                {'id': 8, 'name': 'General', 'note_count': 0},
            ]
            topic_list = default_topics
        
        # Ordenar por cantidad de notas (descendente)
        topic_list.sort(key=lambda x: x.get('note_count', 0), reverse=True)
        
        logging.info(f"Devolviendo {len(topic_list)} temas para el usuario {user_id} en /api/notes/topics")
        return jsonify(topic_list), 200
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logging.error(f"Error al obtener temas: {e}\n{error_traceback}")
        return jsonify({
            "error": f"Error al obtener temas: {str(e)}",
            "traceback": error_traceback
        }), 500


@api_bp.route('/notes/<int:note_id>/process-ai', methods=['POST'])
@jwt_required()
def process_note_with_ai(note_id):
    """Procesa una nota existente con IA para generar resumen y clasificación."""
    try:
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        
        if not note:
            return jsonify({"error": "Nota no encontrada"}), 404
        
        # Verificar que hay contenido suficiente
        if not note.content or len(note.content) < 50:
            return jsonify({"error": "La nota no tiene contenido suficiente para procesar"}), 400
        
        # Obtener el parámetro async del body (opcional)
        data = request.get_json() or {}
        is_async = data.get('async', True)  # Por defecto asíncrono
        
        if is_async:
            # Procesamiento asíncrono usando la tarea de Celery o hilos
            try:
                from ..tasks.note_tasks import process_note
                from threading import Thread
                from flask import current_app
                
                # Usar hilo para procesar en background
                thread = Thread(target=run_note_processing, args=(current_app._get_current_object(), note_id))
                thread.daemon = True
                thread.start()
                
                return jsonify({
                    "message": "Procesamiento iniciado en segundo plano",
                    "note_id": note_id,
                    "async": True
                }), 200
                
            except Exception as e:
                logging.error(f"Error iniciando procesamiento asíncrono: {e}")
                # Si falla el async, intentar síncrono
                is_async = False
        
        if not is_async:
            # Procesamiento síncrono
            try:
                summarizer = get_summarizer()
                classifier = get_classifier()
                
                # Procesar con IA
                note.process_with_ai(summarizer, classifier)
                
                # Guardar cambios
                note.updated_at = datetime.utcnow()
                db.session.commit()
                
                return jsonify({
                    "message": "Nota procesada correctamente",
                    "note": note.to_dict(),
                    "async": False
                }), 200
                
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error en procesamiento síncrono: {e}")
                return jsonify({"error": f"Error procesando nota: {str(e)}"}), 500
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error en endpoint process_note_with_ai: {e}")
        return jsonify({"error": str(e)}), 500
