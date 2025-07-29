"""
Script para diagnosticar problemas con la ruta de login.
Este script analiza específicamente por qué la ruta de login se queda colgada.
"""

import os
import sys
import logging
import json
import requests
from flask import Flask, jsonify
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

def test_login_http_request():
    """Prueba el endpoint de login usando requests directamente."""
    try:
        logger.info("=== Prueba de login directa con requests (timeout: 5s) ===")
        credentials = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        logger.info(f"Enviando solicitud POST a http://localhost:5000/api/auth/login")
        response = requests.post(
            "http://localhost:5000/api/auth/login", 
            json=credentials,
            timeout=5  # Timeout de 5 segundos para evitar esperar indefinidamente
        )
        
        logger.info(f"Status code: {response.status_code}")
        if response.status_code == 200:
            logger.info("Login exitoso!")
            # Mostrar solo los primeros 50 caracteres del token para evitar log excesivo
            token = response.json().get('access_token', '')
            logger.info(f"Token recibido (primeros 50 chars): {token[:50]}...")
            return token
        else:
            logger.error(f"Error en login: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error("TIMEOUT: La solicitud de login excedió el tiempo límite de 5 segundos!")
        logger.error("Esto sugiere un bloqueo en la ruta de login del servidor.")
        return None
        
    except Exception as e:
        logger.error(f"Error inesperado en prueba HTTP: {e}")
        return None

def verify_user_in_database():
    """Verifica si el usuario de prueba existe en la base de datos."""
    try:
        # Importar modelos dentro de la función para evitar problemas de importación
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app.models import User
        
        logger.info("Buscando usuario de prueba en la base de datos...")
        user = User.query.filter_by(email="test@example.com").first()
        
        if user:
            logger.info(f"Usuario encontrado: ID={user.id}, Username={user.username}, Activo={user.is_active}")
            # Verificar si el usuario tiene contraseña
            if user.password_hash:
                logger.info("El usuario tiene un hash de contraseña almacenado.")
            else:
                logger.error("El usuario NO tiene un hash de contraseña!")
        else:
            logger.error("No se encontró el usuario con email test@example.com en la base de datos!")
            logger.info("Debes crear primero el usuario de prueba con python create_test_user.py")
        
        return user
    except Exception as e:
        logger.error(f"Error al verificar usuario en base de datos: {e}")
        return None

def diagnose_login_issues():
    """Función principal de diagnóstico."""
    logger.info("Iniciando diagnóstico de problemas de login...")
    
    # 1. Verificar que existe el usuario de prueba
    user = verify_user_in_database()
    
    if user:
        # 2. Probar el endpoint de login
        token = test_login_http_request()
        
        if token:
            logger.info("La ruta de login parece estar funcionando correctamente.")
            
            # 3. Guardar el token para referencia
            with open("token_diagnostico.txt", "w") as f:
                f.write(token)
            logger.info("Token guardado en 'token_diagnostico.txt'")
            
            # 4. Probar acceso a un endpoint protegido
            try:
                logger.info("Probando acceso a endpoint protegido con el token...")
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(
                    "http://localhost:5000/api/users/profile",
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    logger.info("✅ Acceso a endpoint protegido exitoso!")
                else:
                    logger.error(f"❌ Error al acceder a endpoint protegido: {response.text}")
            except Exception as e:
                logger.error(f"Error al probar endpoint protegido: {e}")
        else:
            logger.error("No se pudo obtener un token. La ruta de login parece bloquearse.")
            logger.info("Recomendaciones:")
            logger.info("1. Revisa si hay operaciones bloqueantes en la ruta de login")
            logger.info("2. Verifica que el método User.check_password() funcione correctamente")
            logger.info("3. Inspecciona los logs del servidor Flask para más detalles")
    
    logger.info("Diagnóstico completado.")

if __name__ == "__main__":
    diagnose_login_issues()
