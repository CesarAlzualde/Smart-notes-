"""
Script para corregir la autenticación JWT que está fallando
"""
import os
import sys
import logging
from pathlib import Path
import traceback

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_jwt_identity_in_init():
    """Corrige la configuración de JWTManager en app/__init__.py"""
    try:
        init_file = Path('app/__init__.py')
        
        if not init_file.exists():
            logger.error(f"Archivo __init__.py no encontrado en {init_file.absolute()}")
            return False
        
        with open(init_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Verificar si hay un problema con la configuración de JWT
        if "@jwt.user_identity_loader" not in content:
            logger.info("Añadiendo user_identity_loader para convertir ID a string")
            
            # Buscar donde se configura el JWTManager
            jwt_manager_pos = content.find("jwt = JWTManager(app)")
            
            if jwt_manager_pos != -1:
                # Encontrar el final de la línea para insertar después
                end_of_line = content.find('\n', jwt_manager_pos)
                
                # Código a insertar
                jwt_identity_code = """
    # Asegurar que la identidad sea siempre un string para evitar errores
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        if user is None:
            return None
        return str(user)
"""
                
                # Insertar el código después de la línea que configura JWTManager
                updated_content = content[:end_of_line+1] + jwt_identity_code + content[end_of_line+1:]
                
                # Guardar el archivo actualizado
                with open(init_file, 'w', encoding='utf-8') as file:
                    file.write(updated_content)
                
                logger.info("✅ Se ha añadido user_identity_loader a app/__init__.py")
                return True
            else:
                logger.error("No se encontró JWTManager en app/__init__.py")
                return False
        else:
            logger.info("user_identity_loader ya existe en app/__init__.py")
            return True
    
    except Exception as e:
        logger.error(f"Error al corregir app/__init__.py: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Corrección de JWT Auth ===")
    
    success = fix_jwt_identity_in_init()
    
    if success:
        print("✅ Configuración JWT corregida.")
        print("   Por favor reinicia el servidor Flask para que los cambios surtan efecto.")
    else:
        print("❌ No se pudo corregir automáticamente la configuración JWT.")
        print("   Por favor revisa manualmente los archivos de configuración y rutas de autenticación.")
