"""
Script principal para ejecutar la aplicación Flask.
"""

import os
import sys
import traceback
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("Iniciando script run.py")

# Añadir la carpeta 'backend' al path de Python para que 'app' sea un paquete de nivel superior
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ahora importamos directamente desde 'app'
from app import create_app
from app.extensions import db

# Crear la aplicación usando la función factory
app = create_app()

# La inicialización de la base de datos ahora se maneja mediante el endpoint /api/health/init-db
# Ver app/api/health.py para el código

if __name__ == '__main__':
    try:
        # Obtener configuración del host y puerto de las variables de entorno, con valores por defecto
        host = os.environ.get('FLASK_HOST', '0.0.0.0')
        port = int(os.environ.get('FLASK_PORT', 5000))
        # FLASK_DEBUG=True/False, por defecto True para desarrollo
        debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 't']

        logger.info(f"Iniciando servidor Flask en http://{host}:{port} (Debug: {debug})")
        
        # use_reloader=False es importante en algunos entornos para evitar que se ejecute dos veces
        app.run(host=host, port=port, debug=debug, use_reloader=False)

    except Exception as e:
        logger.error(f"Error fatal al intentar iniciar el servidor: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1) # Salir con un código de error
