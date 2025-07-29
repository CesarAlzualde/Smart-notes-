"""
Funciones auxiliares para autenticación y autorización.
"""

import functools
from flask import jsonify, current_app
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from ..models import User

def admin_required(fn):
    """
    Decorador que verifica que el usuario autenticado sea un administrador.
    Se debe usar junto con @jwt_required().
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return jsonify({"error": "Se requieren privilegios de administrador"}), 403
            
        return fn(*args, **kwargs)
        
    return wrapper


def role_required(roles):
    """
    Decorador que verifica que el usuario autenticado tenga uno de los roles especificados.
    Se debe usar junto con @jwt_required().
    
    Args:
        roles: Lista de roles permitidos (ej. ['admin', 'teacher'])
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or user.role not in roles:
                allowed_roles = ", ".join(roles)
                return jsonify({
                    "error": f"Acceso restringido. Se requiere uno de los siguientes roles: {allowed_roles}"
                }), 403
                
            return fn(*args, **kwargs)
            
        return wrapper
        
    return decorator


def generate_recovery_code():
    """
    Genera un código aleatorio de 6 caracteres para recuperación de contraseña.
    
    Returns:
        str: Código de recuperación
    """
    import random
    import string
    
    # Generar código alfanumérico de 6 caracteres
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(6))
