"""
Módulo para diagnóstico de problemas con JWT
"""
import logging
from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint para pruebas JWT
jwt_test_bp = Blueprint('jwt_test', __name__, url_prefix='/api/test-jwt')

@jwt_test_bp.route('', methods=['GET'])
@jwt_required()
def test_jwt():
    """Endpoint de diagnóstico para probar la autenticación JWT."""
    try:
        # Obtener identidad y claims completos
        current_user_id = get_jwt_identity()
        jwt_data = get_jwt()
        
        # Información detallada de logging
        logger.info(f"JWT válido - Usuario ID: {current_user_id}")
        logger.info(f"JWT claims completos: {jwt_data}")
        
        # Verificar si el usuario existe en la base de datos
        from ..models.user import User
        from ..models import db
        
        user = User.query.get(current_user_id)
        user_exists = user is not None
        
        logger.info(f"Usuario encontrado en BD: {user_exists}")
        
        return jsonify({
            'status': 'ok',
            'message': 'JWT válido y validado',
            'user_id': current_user_id,
            'user_exists': user_exists,
            'jwt_claims': jwt_data,
            'user_data': user.to_dict() if user else None
        })
    except Exception as e:
        error_msg = f"Error en validación JWT: {e}"
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        
        # Responder con detalles técnicos para facilitar depuración
        return jsonify({
            'status': 'error',
            'message': error_msg,
            'error_type': str(type(e).__name__),
            'error_details': str(e)
        }), 500

def register_blueprint(app):
    """Registra el blueprint en la aplicación Flask."""
    app.register_blueprint(jwt_test_bp)
