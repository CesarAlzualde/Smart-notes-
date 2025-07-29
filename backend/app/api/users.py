"""
API para gestión de usuarios.
Proporciona endpoints para administrar usuarios.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime
from ..extensions import db
from ..models.user import User
from ..auth.helpers import admin_required

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# El blueprint ya se creó en __init__.py, así que usamos el de allí
from . import api_bp

@api_bp.route('/users/profile', methods=['GET'])
@api_bp.route('/users/me', methods=['GET'])  # Alias para compatibilidad con el frontend
@jwt_required()
def get_user_profile():
    """Obtiene el perfil del usuario autenticado."""
    try:
        user_id = get_jwt_identity()
        print(f"--- ID de usuario solicitado en perfil: {user_id} ---")
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        logging.error(f"Error al obtener perfil de usuario: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/users/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """Actualiza el perfil del usuario autenticado."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        data = request.json
        
        # Actualizar campos permitidos
        if 'name' in data:
            user.name = data['name']
            
        if 'email' in data and data['email'] != user.email:
            # Verificar que el email no esté en uso
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({"error": "El email ya está en uso"}), 400
                
            user.email = data['email']
            
        # Actualizar contraseña si se proporciona
        if 'password' in data and data['password']:
            user.set_password(data['password'])
            
        # Actualizar pregunta de seguridad si se proporciona
        if 'security_question' in data:
            user.security_question = data['security_question']
            
        if 'security_answer' in data and data['security_answer']:
            user.set_security_answer(data['security_answer'])
            
        # Guardar cambios
        db.session.commit()
        
        return jsonify({"message": "Perfil actualizado correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al actualizar perfil de usuario: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    """[Admin] Obtiene todos los usuarios del sistema."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)
        users = [user.to_dict() for user in pagination.items]
        
        return jsonify({
            'users': users,
            'total': pagination.total,
            'pages': pagination.pages,
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        logging.error(f"Error al obtener usuarios: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id):
    """[Admin] Obtiene un usuario específico por ID."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        logging.error(f"Error al obtener usuario {user_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    """[Admin] Actualiza un usuario específico."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        data = request.json
        
        # Actualizar campos
        if 'name' in data:
            user.name = data['name']
            
        if 'email' in data and data['email'] != user.email:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({"error": "El email ya está en uso"}), 400
                
            user.email = data['email']
            
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
            
        if 'role' in data and data['role'] in ['admin', 'teacher', 'student']:
            user.role = data['role']
            
        if 'password' in data and data['password']:
            user.set_password(data['password'])
            
        # Guardar cambios
        db.session.commit()
        
        return jsonify({"message": "Usuario actualizado correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al actualizar usuario {user_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """[Admin] Elimina un usuario."""
    try:
        # No permitir eliminar el propio usuario
        current_user_id = get_jwt_identity()
        if current_user_id == user_id:
            return jsonify({"error": "No puedes eliminar tu propio usuario"}), 400
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        # Eliminar usuario
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({"message": "Usuario eliminado correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al eliminar usuario {user_id}: {e}")
        return jsonify({"error": str(e)}), 500
