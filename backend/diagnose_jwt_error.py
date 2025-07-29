"""
Script de diagnóstico detallado para problemas con JWT
"""
import os
import sys
import logging
import json
import traceback
from datetime import datetime, timedelta

# Configurar logging para ver detalles
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler("jwt_diagnostico.log", mode="w"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("jwt_diagnose")

# Añadir directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_env_variables():
    """Verificar variables de entorno críticas para JWT"""
    jwt_secret = os.environ.get('JWT_SECRET_KEY')
    logger.info(f"JWT_SECRET_KEY presente: {jwt_secret is not None}")
    
    if jwt_secret is not None:
        # No mostrar la clave completa, solo los primeros caracteres
        logger.debug(f"JWT_SECRET_KEY (primeros 5 caracteres): {jwt_secret[:5]}***")
    
    # Verificar otras variables importantes
    logger.info(f"SECRET_KEY presente: {os.environ.get('SECRET_KEY') is not None}")
    logger.info(f"DATABASE_URL presente: {os.environ.get('DATABASE_URL') is not None}")

def test_jwt_directly():
    """Probar la funcionalidad JWT directamente fuera de Flask"""
    try:
        logger.info("=== TEST JWT DIRECTO ===")
        
        # Importar librería JWT
        import jwt
        
        # Obtener secreto
        secret = os.environ.get('JWT_SECRET_KEY', 'default-test-secret')
        
        # Crear payload de prueba
        payload = {
            'sub': '123',
            'username': 'test_user',
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        
        # Generar token
        logger.info("Generando token JWT directamente con librería 'jwt'")
        token = jwt.encode(payload, secret, algorithm='HS256')
        logger.info(f"Token generado: {token[:20]}...")
        
        # Decodificar token
        logger.info("Decodificando token JWT")
        decoded = jwt.decode(token, secret, algorithms=['HS256'])
        logger.info(f"Token decodificado correctamente: {json.dumps(decoded)}")
        
        logger.info("✅ Prueba directa de JWT exitosa")
    except Exception as e:
        logger.error(f"❌ Error en prueba directa de JWT: {str(e)}")
        logger.debug(traceback.format_exc())

def test_flask_jwt():
    """Probar la funcionalidad JWT dentro del contexto de Flask"""
    try:
        logger.info("\n=== TEST JWT CON FLASK ===")
        
        # Importar Flask y JWT
        from app import create_app
        from flask_jwt_extended import create_access_token, decode_token
        
        # Crear app y contexto
        app = create_app()
        
        with app.app_context():
            # Informar sobre configuración JWT
            logger.info(f"JWT_SECRET_KEY en app.config: {app.config.get('JWT_SECRET_KEY') is not None}")
            logger.info(f"JWT_ACCESS_TOKEN_EXPIRES: {app.config.get('JWT_ACCESS_TOKEN_EXPIRES')}")
            
            # Generar token
            logger.info("Generando token con create_access_token")
            token = create_access_token(identity="123")
            logger.info(f"Token generado: {token[:20]}...")
            
            # Decodificar token
            logger.info("Decodificando token con decode_token")
            decoded = decode_token(token)
            logger.info(f"Token decodificado correctamente: {json.dumps(decoded)}")
            
            logger.info("✅ Prueba Flask-JWT exitosa")
    except Exception as e:
        logger.error(f"❌ Error en prueba Flask-JWT: {str(e)}")
        logger.debug(traceback.format_exc())

def test_login_flow():
    """Simular el flujo de login directamente desde app/auth/routes.py"""
    try:
        logger.info("\n=== TEST FLUJO LOGIN ===")
        
        # Importar lo necesario
        from app import create_app
        from app.models import User
        
        # Crear app y contexto
        app = create_app()
        
        with app.app_context():
            # Buscar usuario de prueba
            user = User.query.filter_by(email="test@example.com").first()
            
            if not user:
                logger.error("Usuario de prueba no encontrado")
                return
            
            logger.info(f"Usuario encontrado: ID={user.id}, Username={user.username}")
            
            # Replicar el código de routes.py
            additional_claims = {
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'timestamp': datetime.utcnow().timestamp()
            }
            
            from flask_jwt_extended import create_access_token, decode_token
            
            # Intentar crear token
            logger.info("Generando token con identidad como string")
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims=additional_claims
            )
            logger.info(f"Access token generado: {access_token[:20]}...")
            
            # Intentar decodificar
            logger.info("Intentando decodificar token")
            decoded = decode_token(access_token)
            logger.info(f"Token decodificado correctamente: {json.dumps(decoded)}")
            
            logger.info("✅ Simulación de flujo de login exitosa")
    except Exception as e:
        logger.error(f"❌ Error en flujo de login: {str(e)}")
        logger.debug(traceback.format_exc())

if __name__ == "__main__":
    logger.info("=== DIAGNÓSTICO JWT DETALLADO ===")
    logger.info(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Directorio de trabajo: {os.getcwd()}")
    
    # Ejecutar pruebas
    check_env_variables()
    test_jwt_directly()
    test_flask_jwt()
    test_login_flow()
    
    logger.info("\n=== FIN DEL DIAGNÓSTICO ===")
    print("\n✅ Diagnóstico completo. Revisa el archivo 'jwt_diagnostico.log' para detalles.")
    print("   Este archivo te mostrará exactamente dónde ocurre el error.")
