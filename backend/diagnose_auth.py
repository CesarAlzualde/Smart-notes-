"""
Script de diagnóstico completo para el sistema de autenticación.
Escribe los resultados a un archivo de log para evitar problemas de visualización.
"""
import os
import sys
import json
import datetime
import traceback
import logging

# Configurar logging a archivo
logging.basicConfig(
    filename='auth_diagnosis.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_section(title):
    """Registra un título de sección en el log"""
    logging.info("="*50)
    logging.info(title)
    logging.info("="*50)

def diagnose_environment():
    """Diagnostica variables de entorno relacionadas con autenticación"""
    log_section("VARIABLES DE ENTORNO")
    
    critical_vars = ['JWT_SECRET_KEY', 'DATABASE_URL', 'SECRET_KEY']
    for var in critical_vars:
        value = os.environ.get(var)
        if value:
            # No mostrar el valor completo por seguridad
            logging.info(f"{var}: ✅ Configurado")
        else:
            logging.info(f"{var}: ❌ No configurado")

def diagnose_jwt():
    """Diagnostica la funcionalidad JWT"""
    log_section("FUNCIONALIDAD JWT")
    
    try:
        # Intentar importar flask_jwt_extended
        from flask_jwt_extended import create_access_token, decode_token
        logging.info("Módulo flask_jwt_extended: ✅ Importado correctamente")
        
        # Crear un token de prueba
        test_secret = os.environ.get('JWT_SECRET_KEY') or 'clave-prueba-jwt'
        test_payload = {'user_id': 123, 'username': 'test_user', 'role': 'user'}
        
        token = create_access_token(
            identity=test_payload,
            expires_delta=datetime.timedelta(hours=1)
        )
        logging.info(f"Generación de token: ✅ Exitosa")
        logging.info(f"Token: {token[:30]}...")
        
        # Intentar decodificar el token
        decoded = decode_token(token)
        logging.info(f"Decodificación de token: ✅ Exitosa")
        logging.info(f"Payload: {decoded['sub']}")
        logging.info(f"Expiración: {datetime.datetime.fromtimestamp(decoded['exp']).strftime('%Y-%m-%d %H:%M:%S')}")
        
        logging.info("RESULTADO JWT: ✅ La configuración JWT funciona correctamente")
        
    except Exception as e:
        logging.error(f"Error en diagnóstico JWT: {str(e)}")
        logging.error(traceback.format_exc())
        logging.error("RESULTADO JWT: ❌ Hay problemas con la configuración JWT")

def diagnose_database_connection():
    """Diagnostica la conexión a la base de datos"""
    log_section("CONEXIÓN A BASE DE DATOS")
    
    try:
        # Importar modelos y base de datos
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app.models import db, User
        from app import create_app
        
        logging.info("Módulos de la aplicación: ✅ Importados correctamente")
        
        # Crear aplicación de prueba con sqlite en memoria
        app = create_app(test_config=True)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            # Probar conexión
            db.create_all()
            logging.info("Conexión a base de datos: ✅ Exitosa (sqlite en memoria)")
            
            # Verificar modelo User
            user = User(
                username='diagnose_user',
                email='diagnose@example.com',
                name='Diagnose User',
                role='user'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Verificar si se creó el usuario
            found_user = User.query.filter_by(email='diagnose@example.com').first()
            if found_user:
                logging.info("Modelo User: ✅ Funciona correctamente")
                logging.info(f"Usuario creado: {found_user.email} (ID: {found_user.id})")
            else:
                logging.error("Modelo User: ❌ No se pudo crear/recuperar usuario")
        
    except Exception as e:
        logging.error(f"Error en diagnóstico de base de datos: {str(e)}")
        logging.error(traceback.format_exc())
        logging.error("RESULTADO DB: ❌ Hay problemas con la conexión a la base de datos")

def diagnose_auth_routes():
    """Diagnostica las rutas de autenticación"""
    log_section("RUTAS DE AUTENTICACIÓN")
    
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app import create_app
        
        app = create_app(test_config=True)
        
        # Obtener todas las rutas registradas
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'path': str(rule)
            })
        
        # Filtrar rutas de autenticación
        auth_routes = [r for r in routes if 'auth' in r['endpoint']]
        
        if auth_routes:
            logging.info(f"Se encontraron {len(auth_routes)} rutas de autenticación:")
            for route in auth_routes:
                logging.info(f"- {route['path']} [{', '.join(route['methods'])}] -> {route['endpoint']}")
        else:
            logging.warning("No se encontraron rutas de autenticación")
        
    except Exception as e:
        logging.error(f"Error en diagnóstico de rutas: {str(e)}")
        logging.error(traceback.format_exc())

if __name__ == "__main__":
    print("Iniciando diagnóstico del sistema de autenticación...")
    print("Los resultados se escribirán en el archivo 'auth_diagnosis.log'")
    
    diagnose_environment()
    diagnose_jwt()
    diagnose_database_connection()
    diagnose_auth_routes()
    
    print("Diagnóstico completado. Revisa el archivo 'auth_diagnosis.log' para ver los resultados detallados.")
