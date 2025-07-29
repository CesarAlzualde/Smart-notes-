"""
Script de entrada principal para la versión empaquetada con PyInstaller
Este script configura el entorno y luego inicia la aplicación Flask
"""
import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Determinar si estamos en modo empaquetado o desarrollo
if getattr(sys, 'frozen', False):
    # Estamos en PyInstaller
    logger.info("Ejecutando en modo empaquetado (PyInstaller)")
    base_dir = sys._MEIPASS
else:
    # Estamos en modo desarrollo
    logger.info("Ejecutando en modo desarrollo")
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Definir directorio de datos persistente
data_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Apuntes2.0')
os.environ['DATA_DIR'] = data_dir

# Crear directorios necesarios
for subdir in ['database', 'uploads', 'models']:
    os.makedirs(os.path.join(data_dir, subdir), exist_ok=True)

# Definir ruta de la base de datos (normalizada para Windows)
db_path = os.path.join(data_dir, 'database', 'app.db').replace('\\', '/')
os.environ['DATABASE_URL'] = f"sqlite:///{db_path}"

# Configurar otras variables de entorno críticas si no existen
if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = 'apuntes-desarrollo-local'
    
if 'JWT_SECRET_KEY' not in os.environ:
    os.environ['JWT_SECRET_KEY'] = 'jwt-secret-apuntes-local'

if 'UPLOAD_FOLDER' not in os.environ:
    os.environ['UPLOAD_FOLDER'] = os.path.join(data_dir, 'uploads')

# Mostrar configuración para depuración
logger.info(f"DATA_DIR: {os.environ.get('DATA_DIR')}")
logger.info(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
logger.info(f"UPLOAD_FOLDER: {os.environ.get('UPLOAD_FOLDER')}")

# Ahora importamos la app después de configurar el entorno
from app import create_app

app = create_app()

if __name__ == '__main__':
    logger.info("Iniciando servidor Flask...")
    app.run(host='0.0.0.0', port=5000)
