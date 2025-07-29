"""
Inicialización de la aplicación Flask principal.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .extensions import db, cache
from dotenv import load_dotenv
from .cli import register_commands
import os

def create_app(test_config=None):
    """
    Función de fábrica de la aplicación Flask
    Inicializa la aplicación con todas las extensiones necesarias
    """
    # Cargar variables de entorno (solo si no estamos en modo de prueba)
    if test_config is None:
        load_dotenv()
        
        # Verificar variables de entorno críticas (solo en modo normal)
        critical_vars = ['DATABASE_URL', 'JWT_SECRET_KEY', 'UPLOAD_FOLDER', 'SECRET_KEY']
        for var in critical_vars:
            value = os.environ.get(var)
            if value:
                print(f"Configuración: {var} está configurado")
            else:
                print(f"Advertencia: {var} no está configurado, usando valor por defecto")
    
    # Crear y configurar la app
    app = Flask(__name__, 
                static_folder='../static',
                template_folder='../static')
    
    # Configuración base por defecto
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key'),
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'apuntes-app-jwt-secret-key-fixed'),
        JWT_ACCESS_TOKEN_EXPIRES=3600,  # 1 hora
        JWT_REFRESH_TOKEN_EXPIRES=2592000,  # 30 días
        JWT_ERROR_MESSAGE_KEY='error',
        UPLOAD_FOLDER=os.environ.get('UPLOAD_FOLDER', '../uploads'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # Sobreescribir con configuración de prueba si se proporciona
    if test_config is not None:
        app.config.update(test_config)
    
    # Habilitar CORS con manejo de credenciales
    CORS(app, supports_credentials=True)
    
    # Configurar JWT con manejo de errores
    jwt = JWTManager(app)

    # --- Manejadores de errores de JWT ---
    # Estos manejadores aseguran que los errores de autenticación devuelvan JSON
    # en lugar de la página de error HTML por defecto de Flask.

    @jwt.invalid_token_loader
    def invalid_token_callback(error):  # error es un string con la razón
        return jsonify({
            'message': 'Token inválido o malformado.',
            'error': 'invalid_token'
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'message': 'El token ha expirado.',
            'error': 'token_expired'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'message': 'La solicitud no contiene un token de acceso.',
            'error': 'authorization_required'
        }), 401

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({
            'message': 'Se requiere un token fresco para esta operación.',
            'error': 'fresh_token_required'
        }), 401

    # Asegurar que la identidad sea siempre un string para evitar errores
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        if user is None:
            return None
        return str(user)
    
    # Manejadores de errores para JWT
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'El token ha expirado',
            'code': 'token_expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Token inválido',
            'details': str(error),
            'code': 'invalid_token'
        }), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({
            'error': 'Solicitud sin token de autorización',
            'code': 'authorization_required'
        }), 401
    
    # Manejadores de errores globales
    @app.errorhandler(400)
    def handle_bad_request(e):
        return jsonify({"error": "Solicitud incorrecta", "details": str(e)}), 400
        
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({"error": "Recurso no encontrado", "details": str(e)}), 404
        
    @app.errorhandler(500)
    def handle_server_error(e):
        print(f"Error 500: {str(e)}")
        return jsonify({"error": "Error interno del servidor", "details": str(e)}), 500
    
    # Importar e inicializar extensiones desde el archivo central
    from .extensions import db, cache
    from flask_migrate import Migrate

    db.init_app(app)
    cache.init_app(app)
    migrate = Migrate(app, db)
    
    # Inicialización de blueprints
    print("Inicializando blueprints de la aplicación")
    
    # Registrar todos los blueprints
    from .api import api_bp
    from .auth import auth_bp
    from .api.health import health_bp
    from .api.jwt_test import jwt_test_bp
    from .api.compatibility import compat_bp
    from .api.summary import summary_bp
    
    app.register_blueprint(compat_bp, url_prefix='/api')  # Endpoints de compatibilidad para versiones anteriores
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(jwt_test_bp)  # Endpoint de prueba para JWT
    app.register_blueprint(summary_bp)  # Endpoints para manejo de resúmenes
    
    # Ruta para servir la aplicación React
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react(path):
        from flask import send_from_directory, current_app
        import os
        
        # Si la ruta existe como un archivo estático, servirlo directamente
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
            
        # Para todas las demás rutas, servir el index.html de React
        return send_from_directory(app.static_folder, 'index.html')
    
    # Registrar comandos CLI
    register_commands(app)
    
    return app
