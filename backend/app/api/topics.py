"""
API para gestión de tópicos/temas.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
import datetime
from ..extensions import db
from ..models.topic import Topic
from ..models.note import Note

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# El blueprint ya se creó en __init__.py, así que usamos el de allí
from . import api_bp

@api_bp.route('/topics', methods=['GET'], endpoint='get_all_topics')
@jwt_required()
def get_topics():
    """Obtiene todos los tópicos/temas disponibles para el usuario."""
    try:
        user_id = get_jwt_identity()
        
        # Primero intentamos obtener tópicos que estén asociados con notas del usuario
        # mediante la relación Topic.notes
        topics = Topic.query.join(Topic.notes).filter(Note.user_id == user_id).distinct().all()
        
        # También incluimos los temas principales (main_topic) de las notas del usuario
        # que pueden no estar en la tabla de tópicos pero son cruciales para el funcionamiento
        main_topics = db.session.query(Note.main_topic).filter(
            Note.user_id == user_id,
            Note.main_topic.isnot(None),
            Note.main_topic != ''
        ).distinct().all()
        
        main_topic_names = [t[0] for t in main_topics if t[0]]
        
        # Preparar respuesta
        topic_list = [topic.to_dict() for topic in topics]
        
        # Agregar temas principales que no están en la tabla de tópicos
        for topic_name in main_topic_names:
            if not any(t.get('name') == topic_name for t in topic_list):
                # Contar notas con este tema principal
                note_count = Note.query.filter_by(
                    user_id=user_id, 
                    main_topic=topic_name
                ).count()
                
                # Si no hay tópicos y estamos en la página de inicio, necesitamos crear objetos con ID
                # para que el frontend pueda usarlos en los filtros
                topic_list.append({
                    'id': -len(topic_list) - 1,  # ID negativo temporal para distinguirlo
                    'name': topic_name,
                    'description': 'Tema extraído automáticamente',
                    'created_at': datetime.datetime.utcnow().isoformat(),
                    'updated_at': datetime.datetime.utcnow().isoformat(),
                    'note_count': note_count
                })
        
        # Si después de todo esto la lista está vacía, proporcionamos temas predeterminados
        # para asegurar que siempre haya algo que mostrar
        if not topic_list:
            logger.warning("No se encontraron temas. Proporcionando temas predeterminados.")
            default_topics = [
                {'id': -1, 'name': 'Arquitectura', 'description': 'Tema predeterminado', 'note_count': 0},
                {'id': -2, 'name': 'Derecho y Leyes', 'description': 'Tema predeterminado', 'note_count': 0},
                {'id': -3, 'name': 'Gestión de Proyectos', 'description': 'Tema predeterminado', 'note_count': 0},
                {'id': -4, 'name': 'Diseño Gráfico', 'description': 'Tema predeterminado', 'note_count': 0},
                {'id': -5, 'name': 'Educación', 'description': 'Tema predeterminado', 'note_count': 0},
                {'id': -6, 'name': 'Desarrollo Personal', 'description': 'Tema predeterminado', 'note_count': 0},
                {'id': -7, 'name': 'Emprendimiento', 'description': 'Tema predeterminado', 'note_count': 0},
                {'id': -8, 'name': 'General', 'description': 'Tema predeterminado', 'note_count': 0},
            ]
            topic_list.extend(default_topics)
        
        # Ordenar por cantidad de notas (descendente)
        topic_list.sort(key=lambda x: x.get('note_count', 0), reverse=True)
        
        logger.info(f"Devolviendo {len(topic_list)} temas para el usuario {user_id}")
        return jsonify(topic_list), 200
        
    except Exception as e:
        logging.error(f"Error al obtener tópicos: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/topics/<int:topic_id>', methods=['GET'])
@jwt_required()
def get_topic(topic_id):
    """Obtiene un tópico específico y sus notas asociadas."""
    try:
        user_id = get_jwt_identity()
        topic = Topic.query.get(topic_id)
        
        if not topic:
            return jsonify({"error": "Tópico no encontrado"}), 404
            
        # Filtrar notas para mostrar solo las del usuario actual
        user_notes = [note.to_dict() for note in topic.notes if note.user_id == user_id]
        
        topic_data = topic.to_dict()
        topic_data['notes'] = user_notes
        
        return jsonify(topic_data), 200
        
    except Exception as e:
        logging.error(f"Error al obtener tópico {topic_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/topics/by-name/<topic_name>', methods=['GET'])
@jwt_required()
def get_topic_by_name(topic_name):
    """Obtiene un tópico específico por nombre y sus notas asociadas."""
    try:
        user_id = get_jwt_identity()
        
        # Intentar encontrar en tabla de tópicos
        topic = Topic.query.filter_by(name=topic_name).first()
        
        if topic:
            # Filtrar notas para mostrar solo las del usuario actual
            user_notes = [note.to_dict() for note in topic.notes if note.user_id == user_id]
            
            topic_data = topic.to_dict()
            topic_data['notes'] = user_notes
        else:
            # Buscar notas con este tema principal
            notes = Note.query.filter_by(user_id=user_id, main_topic=topic_name).all()
            
            if not notes:
                return jsonify({"error": "Tópico no encontrado"}), 404
                
            # Crear un tópico virtual
            topic_data = {
                'id': None,
                'name': topic_name,
                'description': None,
                'created_at': None,
                'updated_at': None,
                'note_count': len(notes),
                'notes': [note.to_dict() for note in notes]
            }
        
        return jsonify(topic_data), 200
        
    except Exception as e:
        logging.error(f"Error al obtener tópico por nombre {topic_name}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/topics', methods=['POST'])
@jwt_required()
def create_topic():
    """Crea un nuevo tópico."""
    try:
        data = request.json
        
        if not data.get('name'):
            return jsonify({"error": "Se requiere el nombre del tópico"}), 400
            
        # Verificar si ya existe el tópico
        existing_topic = Topic.query.filter_by(name=data['name']).first()
        if existing_topic:
            return jsonify({
                "message": "El tópico ya existe", 
                "topic": existing_topic.to_dict()
            }), 200
            
        # Crear tópico
        topic = Topic(
            name=data['name'],
            description=data.get('description')
        )
        db.session.add(topic)
        db.session.commit()
        
        return jsonify(topic.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al crear tópico: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/topics/<int:topic_id>', methods=['PUT'])
@jwt_required()
def update_topic(topic_id):
    """Actualiza un tópico existente."""
    try:
        topic = Topic.query.get(topic_id)
        
        if not topic:
            return jsonify({"error": "Tópico no encontrado"}), 404
            
        data = request.json
        
        # Actualizar campos
        if 'name' in data:
            # Verificar que el nombre no esté en uso
            existing = Topic.query.filter_by(name=data['name']).first()
            if existing and existing.id != topic_id:
                return jsonify({"error": "Ya existe un tópico con ese nombre"}), 400
                
            topic.name = data['name']
            
        if 'description' in data:
            topic.description = data['description']
            
        # Guardar cambios
        db.session.commit()
        
        return jsonify(topic.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al actualizar tópico {topic_id}: {e}")
        return jsonify({"error": str(e)}), 500
