"""
Rutas para autenticación de usuarios.
Proporciona endpoints para login, registro, recuperación de contraseña, etc.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, decode_token
)
import logging
from datetime import datetime, timedelta
from ..extensions import db
from ..models.user import User
from .helpers import generate_recovery_code

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# El blueprint ya se creó en __init__.py, así que usamos el de allí
from . import auth_bp

@auth_bp.route('/login', methods=['POST'])
def login():
    """Inicia sesión de usuario y devuelve tokens JWT."""
    try:
        # Obtener datos del JSON
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Falta email o contraseña"}), 400
            
        # Buscar usuario
        user = User.query.filter_by(email=email).first()
        
        if not user:
            logger.warning(f"Login fallido: Usuario no encontrado para email {email}")
            return jsonify({"error": "Credenciales inválidas"}), 401
            
        # Verificar contraseña
        if not user.verify_password(password):
            logger.warning(f"Login fallido: Contraseña incorrecta para {user.email}")
            return jsonify({"error": "Credenciales inválidas"}), 401
            
        if not user.is_active:
            logger.warning(f"Login fallido: Usuario {user.email} está desactivado")
            return jsonify({"error": "Usuario desactivado"}), 403
        
        # Crear un diccionario con claims adicionales del usuario
        # Esto garantiza que el token tenga la información correcta del usuario
        additional_claims = {
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'timestamp': datetime.utcnow().timestamp()
        }
        
        logger.info(f"Generando token JWT para usuario ID: {user.id} con claims adicionales")
        
        # Crear access_token con la configuración global (1 hora) y claims adicionales
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=additional_claims
        )
        
        # Log para diagnóstico
        logger.info(f"Token JWT generado: {access_token[:20]}...")
        
        # Crear refresh_token con la configuración global (30 días)
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # Actualizar último inicio de sesión
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Log de éxito
        logger.info(f"Login exitoso para usuario {user.username} (ID: {user.id})") 
        
        # Devolver respuesta exitosa
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }), 200
            
    except Exception as e:
        # Log detallado del error con traceback completo
        import traceback
        logger.error(f"Error en login: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Respuesta de error genérica pero segura
        return jsonify({"error": "Error durante la autenticación"}), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    """Registra un nuevo usuario."""
    try:
        data = request.json
        
        # Validar datos requeridos
        if not data or not data.get('username') or not data.get('name') or not data.get('email') or not data.get('password'):
            return jsonify({
                "error": "Se requieren nombre de usuario, nombre, email y contraseña"
            }), 400
            
        # Verificar si el email ya está en uso
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({"error": "El email ya está registrado"}), 400
            
        # Verificar si el username ya está en uso
        existing_username = User.query.filter_by(username=data['username']).first()
        if existing_username:
            return jsonify({"error": "El nombre de usuario ya está en uso"}), 400
            
        # Crear nuevo usuario
        user = User(
            username=data['username'],
            name=data['name'],
            email=data['email'],
            is_active=True,
            role='student'  # Rol por defecto
        )
        
        # Establecer contraseña (el método set_password realiza el hash)
        user.set_password(data['password'])
        
        # Guardar pregunta y respuesta de seguridad si se proporcionan
        if data.get('security_question') and data.get('security_answer'):
            user.security_question = data['security_question']
            user.set_security_answer(data['security_answer'])
            
        # Guardar en la base de datos
        db.session.add(user)
        db.session.commit()
        
        # Crear tokens
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=1)
        )
        
        refresh_token = create_refresh_token(
            identity=str(user.id),
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            "message": "Usuario registrado correctamente",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error en registro: {e}")
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Renueva el token de acceso usando el refresh token."""
    try:
        # Obtener la identidad del usuario desde el token
        user_id = get_jwt_identity()
        logger.info(f"Intento de refresh token para usuario ID: {user_id}")
        
        # Buscar el usuario en la base de datos
        user = User.query.get(user_id)
        
        if not user:
            logger.warning(f"Refresh token fallido: Usuario no encontrado para ID {user_id}")
            return jsonify({"error": "Usuario no encontrado"}), 401
            
        if not user.is_active:
            logger.warning(f"Refresh token fallido: Usuario {user.email} está desactivado")
            return jsonify({"error": "Usuario desactivado"}), 401
            
        # Crear un diccionario con claims adicionales del usuario
        additional_claims = {
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'timestamp': datetime.utcnow().timestamp()
        }
        
        # Crear nuevo token de acceso con claims adicionales
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=additional_claims
        )
        
        logger.info(f"Refresh token exitoso para usuario {user.username} (ID: {user.id})")
        
        return jsonify({
            "access_token": access_token,
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        import traceback
        logger.error(f"Error en refresh token: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Error al renovar el token: " + str(e)}), 500


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Inicia el proceso de recuperación de contraseña."""
    try:
        data = request.json
        
        if not data or not data.get('email'):
            return jsonify({"error": "Se requiere email"}), 400
            
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            # Por seguridad, no revelamos que el email no existe
            return jsonify({
                "message": "Si el email está registrado, se enviará un código de recuperación"
            }), 200
            
        # Generar código de recuperación
        recovery_code = generate_recovery_code()
        user.recovery_code = recovery_code
        from datetime import datetime, timedelta
        user.recovery_code_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        
        # En producción, enviar email con el código
        # Para desarrollo, simplemente devolvemos el código
        
        # Si hay pregunta de seguridad, devolverla para que el usuario responda
        security_question = user.security_question if user.security_question else None
        
        return jsonify({
            "message": "Se ha enviado un código de recuperación al email",
            "security_question": security_question,
            "recovery_code": recovery_code,  # Solo para desarrollo, eliminar en producción
            "email": data['email']
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error en recuperación de contraseña: {e}")
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/check-security-answer', methods=['POST'])
def check_security_answer():
    """Verifica la respuesta a la pregunta de seguridad."""
    try:
        data = request.json
        
        if not data or not data.get('email') or not data.get('security_answer'):
            return jsonify({"error": "Se requiere email y respuesta de seguridad"}), 400
            
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        if not user.security_question or not user.security_answer_hash:
            return jsonify({"error": "Este usuario no tiene pregunta de seguridad configurada"}), 400
            
        # Verificar respuesta
        if not user.check_security_answer(data['security_answer']):
            return jsonify({"error": "Respuesta de seguridad incorrecta"}), 401
            
        # Si la respuesta es correcta, generar un código de recuperación
        recovery_code = generate_recovery_code()
        user.recovery_code = recovery_code
        from datetime import datetime, timedelta
        user.recovery_code_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        
        return jsonify({
            "message": "Respuesta correcta",
            "recovery_code": recovery_code,  # Solo para desarrollo
            "email": data['email']
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al verificar respuesta de seguridad: {e}")
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Restablece la contraseña usando el código de recuperación."""
    try:
        data = request.json
        
        if not data or not data.get('email') or not data.get('recovery_code') or not data.get('new_password'):
            return jsonify({
                "error": "Se requiere email, código de recuperación y nueva contraseña"
            }), 400
            
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        # Verificar código de recuperación
        if not user.recovery_code or user.recovery_code != data['recovery_code']:
            return jsonify({"error": "Código de recuperación inválido"}), 401
            
        # Verificar que el código no haya expirado
        from datetime import datetime
        if not user.recovery_code_expires or user.recovery_code_expires < datetime.utcnow():
            return jsonify({"error": "El código de recuperación ha expirado"}), 401
            
        # Actualizar contraseña
        user.set_password(data['new_password'])
        
        # Limpiar código de recuperación
        user.recovery_code = None
        user.recovery_code_expires = None
        db.session.commit()
        
        return jsonify({
            "message": "Contraseña restablecida correctamente"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al restablecer contraseña: {e}")
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Cierra la sesión del usuario.
    
    Nota: En JWT, el logout es manejado principalmente por el cliente
    eliminando los tokens. Este endpoint es más para consistencia y
    para posibles mejoras futuras (como lista negra de tokens).
    """
    try:
        # Actualmente solo devuelve un mensaje de éxito
        # En una implementación más completa, aquí se agregaría el token a una lista negra
        
        return jsonify({
            "message": "Sesión cerrada correctamente"
        }), 200
        
    except Exception as e:
        logging.error(f"Error en logout: {e}")
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_info():
    """Obtiene información del usuario autenticado."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        logging.error(f"Error al obtener información de usuario: {e}")
        return jsonify({"error": str(e)}), 500
