import os
import sys
import shutil
import subprocess

# Directorio del proyecto
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("Directorio actual:", os.getcwd())

# Limpieza previa
print("Limpiando compilaciones anteriores...")
if os.path.exists("backend/dist"):
    shutil.rmtree("backend/dist")
if os.path.exists("backend/build"):
    shutil.rmtree("backend/build")
for file in os.listdir("backend"):
    if file.endswith(".spec"):
        os.remove(os.path.join("backend", file))

# Directorios persistentes
print("Configurando directorios persistentes...")
data_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Apuntes2.0")
os.makedirs(data_dir, exist_ok=True)
os.makedirs(os.path.join(data_dir, "database"), exist_ok=True)
os.makedirs(os.path.join(data_dir, "uploads"), exist_ok=True)
os.makedirs(os.path.join(data_dir, "models"), exist_ok=True)

# Configuración de producción
print("Creando configuración de producción...")
config_dir = os.path.join("backend", "app")
config_file = os.path.join(config_dir, "__production_config.py")

with open(config_file, "w") as f:
    f.write("""import os
import sys

# Configurar entorno de producción
os.environ['FLASK_ENV'] = 'production'

# Determinar directorio base
if getattr(sys, 'frozen', False):
    # Estamos en PyInstaller
    BASE_DIR = sys._MEIPASS
else:
    # Estamos en desarrollo
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Definir directorio de datos persistente
DATA_DIR = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Apuntes2.0')
os.environ['DATA_DIR'] = DATA_DIR

# Crear directorios necesarios
for subdir in ['database', 'uploads', 'models']:
    os.makedirs(os.path.join(DATA_DIR, subdir), exist_ok=True)

# Configurar ruta de base de datos
db_path = os.path.join(DATA_DIR, 'database', 'app.db').replace('\\\\', '/')
os.environ['DATABASE_URL'] = f"sqlite:///{db_path}"

# Configurar carpeta de uploads
os.environ['UPLOAD_FOLDER'] = os.path.join(DATA_DIR, 'uploads')

print(f"Configuración de producción cargada:")
print(f"DATA_DIR: {DATA_DIR}")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
print(f"UPLOAD_FOLDER: {os.environ.get('UPLOAD_FOLDER')}")
""")

# Script de entrada para producción
print("Creando script de entrada para producción...")
with open(os.path.join("backend", "run_prod.py"), "w") as f:
    f.write('''"""Punto de entrada para producción"""
import os
import sys

# Cargar configuración de producción primero
from app.__production_config import *

# Importar app después de cargar configuración
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
''')

# Ejecutar PyInstaller
print("Ejecutando PyInstaller...")
os.chdir("backend")
pyinstaller_cmd = [
    "python", "-m", "PyInstaller",
    "--name", "ApuntesBackend",
    "--hidden-import=pytesseract",
    "--hidden-import=flask_cors",
    "--hidden-import=transformers",
    "--hidden-import=sentence_transformers",
    "--hidden-import=pyarrow",
    "--hidden-import=unidecode",
    "--hidden-import=nltk",
    "--hidden-import=tensorflow",
    "--hidden-import=numpy",
    "--hidden-import=sqlalchemy",
    "--add-data", "config;config",
    "--add-data", "app/static;app/static",
    "--add-data", "app/templates;app/templates",
    "--noconfirm",
    "--console",
    "run_prod.py"
]

try:
    subprocess.run(pyinstaller_cmd, check=True)
    print("PyInstaller ejecutado exitosamente")
except Exception as e:
    print(f"Error al ejecutar PyInstaller: {e}")

# Crear distribución final
print("Preparando distribución final...")
os.chdir("..")
dist_dir = "dist-apuntes"
os.makedirs(os.path.join(dist_dir, "backend"), exist_ok=True)

# Copiar archivos
source_dir = "backend/dist/ApuntesBackend"
if os.path.exists(source_dir):
    for item in os.listdir(source_dir):
        s = os.path.join(source_dir, item)
        d = os.path.join(dist_dir, "backend", item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

# Crear script de inicio
with open(os.path.join(dist_dir, "iniciar-backend.bat"), "w") as f:
    f.write(f'''@echo off
title Backend Apuntes 2.0
cd /d "%~dp0\\backend"
echo Iniciando backend Flask...
echo.
start ApuntesBackend.exe
echo Backend iniciado en http://localhost:5000
echo Para verificar, abre: http://localhost:5000/api/health
echo.
echo NOTA: Los datos se almacenan en: {data_dir}
''')

print("\nEmpaquetado completado exitosamente.")
print(f"El backend está disponible en: {os.path.abspath(dist_dir)}/backend")
print(f"La base de datos y archivos se guardarán en: {data_dir}")
print("Para iniciar el backend, ejecuta: dist-apuntes/iniciar-backend.bat")
