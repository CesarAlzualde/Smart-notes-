"""
Script simple para probar la autenticación usando Python y requests
"""
import requests
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_login():
    """Prueba el endpoint de login"""
    logger.info("Probando login...")
    
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/auth/login",
            json=login_data,
            timeout=10  # timeout de 10 segundos
        )
        
        logger.info(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("Login exitoso!")
            data = response.json()
            token = data.get('access_token')
            
            # Guardar token en un archivo
            with open("token_python.txt", "w") as f:
                f.write(token)
            logger.info(f"Token guardado en token_python.txt (primeros 30 caracteres): {token[:30]}...")
            
            # Probar endpoint protegido
            logger.info("Probando acceso a endpoint protegido...")
            headers = {"Authorization": f"Bearer {token}"}
            
            profile_response = requests.get(
                "http://localhost:5000/api/users/profile",
                headers=headers,
                timeout=10
            )
            
            if profile_response.status_code == 200:
                logger.info("Acceso exitoso al endpoint protegido!")
                logger.info(f"Datos del perfil: {json.dumps(profile_response.json(), indent=2)}")
                return True
            else:
                logger.error(f"Error al acceder al endpoint protegido: {profile_response.status_code}")
                logger.error(profile_response.text)
                return False
        else:
            logger.error(f"Error en login: {response.status_code}")
            logger.error(response.text)
            return False
            
    except requests.exceptions.Timeout:
        logger.error("TIMEOUT: La solicitud excedió el tiempo límite!")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("ERROR DE CONEXIÓN: No se pudo conectar al servidor!")
        logger.error("Verifica que el servidor Flask esté ejecutándose en localhost:5000")
        return False
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return False

if __name__ == "__main__":
    test_login()
