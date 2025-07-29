"""
Script para arreglar el problema de identidad JWT en la aplicación
"""
import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Añadir el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_login_route():
    """
    Corrige la ruta de autenticación para manejar correctamente la identidad JWT
    """
    auth_file_path = Path('app/api/auth.py')
    
    if not auth_file_path.exists():
        logger.error(f"Archivo de autenticación no encontrado en {auth_file_path}")
        return False
    
    # Leer el contenido actual
    with open(auth_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Buscar y corregir la parte que genera tokens
    if "create_access_token(identity=user)" in content:
        logger.info("Encontrada la llamada a create_access_token con objeto usuario completo")
        
        # Reemplazar con la versión corregida que usa str(user.id) como identidad
        updated_content = content.replace(
            "create_access_token(identity=user)",
            "create_access_token(identity=str(user.id))"
        )
        
        # Actualizar también jwt_refresh_token_required si existe
        if "jwt_refresh_token_required" in updated_content:
            updated_content = updated_content.replace(
                "jwt_refresh_token_required", 
                "jwt_required(refresh=True)"
            )
        
        # Actualizar get_jwt_identity() si es necesario para manejar IDs como strings
        if "current_user = User.query.filter_by(id=get_jwt_identity()).first()" in updated_content:
            # Ya está correcto, no es necesario cambiar
            pass
        elif "current_user = get_jwt_identity()" in updated_content:
            updated_content = updated_content.replace(
                "current_user = get_jwt_identity()",
                "user_id = get_jwt_identity()\n    current_user = User.query.filter_by(id=int(user_id)).first()"
            )
        
        # Guardar el archivo actualizado
        with open(auth_file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        
        logger.info(f"✅ Ruta de autenticación JWT corregida en {auth_file_path}")
        return True
    else:
        logger.warning("No se encontró el patrón exacto para corregir en la ruta de autenticación")
        # Intentar realizar una corrección manual más avanzada
        return False

if __name__ == "__main__":
    print("=== Corrección de identidad JWT ===")
    
    if fix_login_route():
        print("✅ Corrección completada. La aplicación ahora debería generar tokens JWT correctamente.")
        print("   Reinicia el servidor Flask para aplicar los cambios.")
    else:
        print("❌ No se pudo corregir automáticamente. Por favor revisa manualmente el archivo app/api/auth.py")
        print("   Asegúrate que create_access_token reciba un ID de usuario como string: create_access_token(identity=str(user.id))")
