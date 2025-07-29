"""
Script para crear usuarios de prueba en la base de datos.

Ejemplo de uso:
    python create_test_user.py --username admin --email admin@example.com --password admin123 --role admin
    python create_test_user.py --username estudiante --role student
    python create_test_user.py  # Crea usuario por defecto
"""

import sys
import os
import logging
import argparse

# Añadir el directorio actual al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar solo create_app desde app
from app import create_app
# Luego importar db desde extensions y User desde models
from app.extensions import db
from app.models.user import User

# Configurar logging de manera más visible
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Asegurar que los mensajes vayan a la consola
    ]
)
logger = logging.getLogger(__name__)

def create_test_user(username="testuser", email="test@example.com", password="password123", name="Usuario de Prueba", role="student"):
    """Crear un usuario de prueba en la base de datos.
    
    Args:
        username (str): Nombre de usuario único
        email (str): Correo electrónico único
        password (str): Contraseña
        name (str): Nombre completo del usuario
        role (str): Rol del usuario ('admin', 'student', 'teacher', 'user')
    
    Returns:
        User: Objeto de usuario creado o actualizado
        None: Si ocurre algún error
    """
    try:
        # Crear la aplicación con configuración de prueba
        app = create_app()
        
        # Validar el rol proporcionado
        valid_roles = ['admin', 'student', 'teacher', 'user']
        if role not in valid_roles:
            logger.warning(f"Rol '{role}' no válido. Opciones válidas: {', '.join(valid_roles)}")
            logger.warning(f"Usando rol por defecto: 'student'")
            role = 'student'
        
        # Usar el contexto de la aplicación
        with app.app_context():
            # Verificar si el usuario ya existe (por email o username)
            existing_user = User.query.filter(
                (User.email == email) | (User.username == username)
            ).first()
            
            if existing_user:
                logger.info(f"El usuario {existing_user.username} ({existing_user.email}) ya existe.")
                
                # Actualizar información
                existing_user.name = name
                existing_user.role = role
                existing_user.set_password(password)
                
                db.session.commit()
                logger.info(f"Información actualizada para {existing_user.username}")
                return existing_user
            
            # Crear nuevo usuario
            user = User(
                username=username,
                email=email,
                name=name,
                is_active=True,
                role=role
            )
            
            # Establecer contraseña
            user.set_password(password)
            
            # Guardar en la base de datos
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"Usuario creado exitosamente: {username} ({email})")
            logger.info(f"Rol: {role}")
            logger.info(f"Contraseña: {password}")
            return user
    
    except Exception as e:
        logger.error(f"Error al crear usuario de prueba: {e}")
        return None

if __name__ == "__main__":
    # Configurar parser de argumentos para línea de comandos
    parser = argparse.ArgumentParser(description="Crear usuarios de prueba en la base de datos")
    parser.add_argument("--username", type=str, default="testuser", help="Nombre de usuario")
    parser.add_argument("--email", type=str, default="test@example.com", help="Correo electrónico")
    parser.add_argument("--password", type=str, default="password123", help="Contraseña")
    parser.add_argument("--name", type=str, default="Usuario de Prueba", help="Nombre completo")
    parser.add_argument("--role", type=str, default="student", 
                       choices=["admin", "student", "teacher", "user"],
                       help="Rol del usuario")
    
    # Analizar argumentos
    args = parser.parse_args()
    
    logger.info("Creando usuario de prueba...")
    create_test_user(
        username=args.username,
        email=args.email,
        password=args.password,
        name=args.name,
        role=args.role
    )
    logger.info("Proceso completado.")
