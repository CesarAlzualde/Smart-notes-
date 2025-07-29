"""
API para gestión de etiquetas.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from ..extensions import db
from ..models.tag import Tag
from ..models.note import Note

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# El blueprint ya se creó en __init__.py, así que usamos el de allí
from . import api_bp

@api_bp.route('/tags', methods=['GET'])
@jwt_required()
def get_tags():
    """Obtiene todas las etiquetas disponibles para el usuario."""
    try:
        user_id = get_jwt_identity()
        
        # Obtenemos etiquetas que estén asociadas con notas del usuario
        # Necesitamos hacer un join entre Tag, note_tag y Note
        tags = Tag.query.join(Tag.notes).filter(Note.user_id == user_id).distinct().all()
        
        # Preparar respuesta
        tag_list = [tag.to_dict() for tag in tags]
        
        return jsonify(tag_list), 200
        
    except Exception as e:
        logging.error(f"Error al obtener etiquetas: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/tags/<int:tag_id>', methods=['GET'])
@jwt_required()
def get_tag(tag_id):
    """Obtiene una etiqueta específica y sus notas asociadas."""
    try:
        user_id = get_jwt_identity()
        tag = Tag.query.get(tag_id)
        
        if not tag:
            return jsonify({"error": "Etiqueta no encontrada"}), 404
            
        # Filtrar notas para mostrar solo las del usuario actual
        user_notes = [note.to_dict() for note in tag.notes if note.user_id == user_id]
        
        tag_data = tag.to_dict()
        tag_data['notes'] = user_notes
        
        return jsonify(tag_data), 200
        
    except Exception as e:
        logging.error(f"Error al obtener etiqueta {tag_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/tags', methods=['POST'])
@jwt_required()
def create_tag():
    """Crea una nueva etiqueta."""
    try:
        # Verificar que request.json existe y es un diccionario
        if not request.is_json:
            return jsonify({"error": "Se esperaba contenido JSON"}), 400
        
        data = request.json
        
        # Verificar que data es un diccionario
        if not isinstance(data, dict):
            return jsonify({"error": "Formato de datos inválido"}), 422
        
        # Verificar que el campo name existe y es válido
        if not data.get('name'):
            return jsonify({"error": "Se requiere el nombre de la etiqueta"}), 400
        
        # Validar formato del nombre (eliminar espacios extra, caracteres inválidos, etc)
        tag_name = data['name'].strip()
        if not tag_name or len(tag_name) > 50:  # Nombre no vacío y longitud máxima
            return jsonify({"error": "El nombre de la etiqueta no puede estar vacío ni exceder 50 caracteres"}), 422
            
        # Verificar si ya existe la etiqueta
        existing_tag = Tag.query.filter_by(name=tag_name).first()
        if existing_tag:
            return jsonify({"message": "La etiqueta ya existe", "tag": existing_tag.to_dict()}), 200
            
        # Crear etiqueta
        tag = Tag(name=tag_name)
        db.session.add(tag)
        db.session.commit()
        
        return jsonify(tag.to_dict()), 201
        
    except ValueError as e:
        db.session.rollback()
        logging.error(f"Error de validación al crear etiqueta: {e}")
        return jsonify({"error": "Error en el formato de los datos"}), 422
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al crear etiqueta: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@api_bp.route('/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    """Elimina una etiqueta (solo si no tiene notas asociadas o es el propietario de todas)."""
    try:
        user_id = get_jwt_identity()
        tag = Tag.query.get(tag_id)
        
        if not tag:
            return jsonify({"error": "Etiqueta no encontrada"}), 404
            
        # Verificar si el usuario es propietario de todas las notas que usan esta etiqueta
        for note in tag.notes:
            if note.user_id != user_id:
                return jsonify({
                    "error": "No puedes eliminar esta etiqueta porque está siendo usada por notas de otros usuarios"
                }), 403
                
        # Eliminar etiqueta
        db.session.delete(tag)
        db.session.commit()
        
        return jsonify({"message": "Etiqueta eliminada correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al eliminar etiqueta {tag_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/tags/statistics', methods=['GET'])
@jwt_required()
def get_tag_statistics():
    """Obtiene estadísticas sobre las etiquetas del usuario."""
    try:
        user_id = get_jwt_identity()
        
        # Obtener todas las etiquetas asociadas con notas del usuario
        tags = Tag.query.join(Tag.notes).filter(Note.user_id == user_id).distinct().all()
        
        # Contar notas por etiqueta
        tag_stats = []
        for tag in tags:
            # Contar solo las notas del usuario actual
            note_count = sum(1 for note in tag.notes if note.user_id == user_id)
            tag_stats.append({
                'id': tag.id,
                'name': tag.name,
                'note_count': note_count
            })
        
        # Ordenar por cantidad de notas (descendente)
        tag_stats.sort(key=lambda x: x['note_count'], reverse=True)
        
        # Estadísticas generales
        total_tags = len(tags)
        most_used = tag_stats[0] if tag_stats else None
        
        return jsonify({
            'total_tags': total_tags,
            'most_used': most_used,
            'tag_stats': tag_stats
        }), 200
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logging.error(f"Error al obtener estadísticas de etiquetas: {e}\n{error_traceback}")
        return jsonify({
            "error": f"Error al obtener estadísticas de etiquetas: {str(e)}",
            "traceback": error_traceback
        }), 500


@api_bp.route('/tags/popular', methods=['GET'])
@jwt_required()
def get_popular_tags():
    """Obtiene las etiquetas más populares del usuario."""
    try:
        user_id = get_jwt_identity()
        
        # Validar el parámetro limit
        try:
            limit = request.args.get('limit', 10, type=int)
            # Asegurar que limit sea un número positivo y no muy grande
            limit = max(1, min(limit, 50))  # Entre 1 y 50
        except (ValueError, TypeError):
            limit = 10  # Valor por defecto si hay error
            
        # Obtener todas las etiquetas asociadas con notas del usuario
        # y contar sus ocurrencias
        from sqlalchemy import func
        tag_counts = db.session.query(
            Tag.id,
            Tag.name,
            func.count(Note.id).label('count')
        ).join(Tag.notes).filter(
            Note.user_id == user_id
        ).group_by(Tag.id, Tag.name).order_by(
            func.count(Note.id).desc()
        ).limit(limit).all()
        
        # Formatear respuesta
        result = [
            {
                'id': tag_id,
                'name': name,
                'count': count
            } for tag_id, name, count in tag_counts
        ]
        
        return jsonify(result), 200
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logging.error(f"Error al obtener etiquetas populares: {e}\n{error_traceback}")
        return jsonify({
            "error": f"Error al obtener etiquetas populares: {str(e)}",
            "success": False,
            "data": [] # Siempre incluir una estructura de datos vacía compatible
        }), 200  # Devolvemos 200 pero con error para que la UI pueda recuperarse
