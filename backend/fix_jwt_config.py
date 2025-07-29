"""
Script para actualizar la configuración JWT y asegurar su correcto funcionamiento.
Este script configura correctamente la app.py para usar JWT_SECRET_KEY de manera consistente.
"""
import os
import sys

# Obtener la ruta actual
current_dir = os.path.dirname(os.path.abspath(__file__))

# Verificar la existencia del archivo app/__init__.py
init_file = os.path.join(current_dir, 'app', '__init__.py')
if not os.path.exists(init_file):
    print(f"❌ No se encontró el archivo {init_file}")
    sys.exit(1)

# Leer el contenido actual
with open(init_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Configurar correctamente JWT
updated_content = content

# Asegurarse de que se importan correctamente los módulos necesarios
if 'from flask_jwt_extended import JWTManager' not in content:
    import_line = 'from flask import Flask\n'
    replacement = 'from flask import Flask, jsonify\nfrom flask_jwt_extended import JWTManager\n'
    updated_content = updated_content.replace(import_line, replacement)

# Asegurar que se usa correctamente la configuración de JWT
jwt_config_exists = 'jwt = JWTManager(app)' in content
jwt_secret_config_exists = "app.config['JWT_SECRET_KEY']" in content

if not jwt_config_exists or not jwt_secret_config_exists:
    # Ubicar donde termina la función create_app
    create_app_def = 'def create_app('
    create_app_end_idx = updated_content.find('return app', updated_content.find(create_app_def))
    
    if create_app_end_idx != -1:
        # Código a insertar antes de "return app"
        jwt_config = """
    # Configuración de JWT
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'default-super-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    jwt = JWTManager(app)
    
    # Manejadores de errores JWT
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token expirado',
            'message': 'El token ha expirado'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Token inválido',
            'message': str(error)
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Token no proporcionado',
            'message': str(error)
        }), 401
        
"""
        # Verificar si necesitamos importar timedelta
        if 'from datetime import timedelta' not in updated_content:
            # Añadir import de timedelta junto con otros imports
            updated_content = updated_content.replace(
                'import os', 
                'import os\nfrom datetime import timedelta'
            )
        
        # Insertar la configuración antes de "return app"
        updated_content = (
            updated_content[:create_app_end_idx] + 
            jwt_config + 
            updated_content[create_app_end_idx:]
        )

# Guardar el archivo modificado
with open(init_file, 'w', encoding='utf-8') as f:
    f.write(updated_content)

print("✅ Configuración JWT actualizada en app/__init__.py")

# Verificar y crear un archivo .env adecuado si no existe
env_file = os.path.join(current_dir, '.env')
if not os.path.exists(env_file):
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write("""# Variables de entorno para el proyecto
JWT_SECRET_KEY=clave-secreta-jwt-para-proyecto-apuntes
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/apuntes
SECRET_KEY=clave-secreta-flask-para-proyecto-apuntes
UPLOAD_FOLDER=./uploads
""")
    print("✅ Archivo .env creado con valores predeterminados")
else:
    # Verificar que el archivo .env tenga JWT_SECRET_KEY
    with open(env_file, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    if 'JWT_SECRET_KEY' not in env_content:
        with open(env_file, 'a', encoding='utf-8') as f:
            f.write("\nJWT_SECRET_KEY=clave-secreta-jwt-para-proyecto-apuntes\n")
        print("✅ JWT_SECRET_KEY añadida al archivo .env existente")
    else:
        print("✅ JWT_SECRET_KEY ya existe en el archivo .env")

print("\n🔐 Configuración de JWT completada. El sistema debería funcionar correctamente ahora.")
print("Recuerda ejecutar 'python -m flask run' para iniciar el servidor.")
