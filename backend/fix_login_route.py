"""
Script para corregir específicamente la ruta de login en app/auth/routes.py
"""
import os
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_login_route():
    """Corrige la ruta de login para usar str(user.id) como identity"""
    try:
        # Ruta al archivo de rutas de autenticación
        auth_routes_path = Path('app/auth/routes.py')
        
        if not auth_routes_path.exists():
            logger.error(f"El archivo {auth_routes_path} no existe")
            return False
            
        # Leer el contenido actual
        with open(auth_routes_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Buscar el patrón específico de la creación de access_token
        if "identity=user.id" in content:
            # Reemplazar con la versión que usa str()
            logger.info("Reemplazando 'identity=user.id' con 'identity=str(user.id)'")
            updated_content = content.replace(
                "identity=user.id",
                "identity=str(user.id)"
            )
            
            # Guardar el archivo actualizado
            with open(auth_routes_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
                
            logger.info(f"✅ Archivo {auth_routes_path} actualizado correctamente")
            return True
        elif "identity=user" in content:
            # Si está usando el objeto user completo (otro tipo de error)
            logger.info("Reemplazando 'identity=user' con 'identity=str(user.id)'")
            updated_content = content.replace(
                "identity=user",
                "identity=str(user.id)"
            )
            
            # Guardar el archivo actualizado
            with open(auth_routes_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
                
            logger.info(f"✅ Archivo {auth_routes_path} actualizado correctamente")
            return True
        else:
            logger.warning("No se encontró el patrón esperado en el archivo")
            
            # Buscar la línea que crea el access_token en el contexto del login
            login_fn = content.find("def login():")
            if login_fn != -1:
                # Encontrar la línea de create_access_token dentro de la función login
                start_of_fn = content.find("access_token = create_access_token(", login_fn)
                if start_of_fn != -1:
                    # Encontrar el final de la declaración create_access_token
                    end_of_stmt = content.find(")", start_of_fn)
                    
                    if end_of_stmt != -1:
                        # Extraer y mostrar el contexto para diagnóstico
                        context = content[start_of_fn:end_of_stmt+1]
                        logger.info(f"Contexto encontrado: {context}")
                        
                        # Intentar una corrección más general
                        try:
                            print("Se intentará una corrección manual del código de login...")
                            # Mostrar el código actual para diagnóstico
                            print("CÓDIGO ACTUAL:")
                            print(context)
                            
                            # Intentar modificar manualmente la ruta de login
                            with open('app/auth/routes.py.bak', 'w', encoding='utf-8') as backup:
                                backup.write(content)
                            logger.info("Se ha creado una copia de seguridad en app/auth/routes.py.bak")
                            
                            return False
                        except Exception as e:
                            logger.error(f"Error al intentar corrección manual: {e}")
                            return False
            
            logger.error("No se pudo identificar claramente el patrón a corregir")
            return False
            
    except Exception as e:
        logger.error(f"Error al procesar el archivo: {e}")
        return False

if __name__ == "__main__":
    print("=== Corrigiendo ruta de login para tokens JWT ===")
    
    success = fix_login_route()
    
    if success:
        print("""
✅ La ruta de login ha sido corregida exitosamente.

IMPORTANTE:
1. Reinicia el servidor Flask con:
   python -m flask run --debug

2. Prueba la autenticación con:
   $loginData = @{
       email = "test@example.com"
       password = "password123"
   } | ConvertTo-Json
   
   Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method Post -Body $loginData -ContentType "application/json"
""")
    else:
        print("""
⚠️ No se pudo corregir automáticamente la ruta de login.

CORRECCIÓN MANUAL:
1. Abre el archivo: app/auth/routes.py
2. Encuentra la función login()
3. Busca la línea: access_token = create_access_token(identity=user.id, ...)
4. Asegúrate de usar str(user.id) como identity, debería quedar: 
   access_token = create_access_token(identity=str(user.id), ...)
5. Guarda el archivo y reinicia el servidor Flask
""")
