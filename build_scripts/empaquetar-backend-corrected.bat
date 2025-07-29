@echo off
cd /d "%~dp0"
chcp 65001 > nul
title Empaquetado Corregido de Apuntes 2.0
color 0A

echo =========================================================
echo     EMPAQUETADO CORREGIDO DEL BACKEND (APUNTES 2.0)
echo =========================================================
echo.

rem --- Limpieza previa ---
echo [1/5] Limpiando compilaciones anteriores...
if exist "backend\dist" rmdir /S /Q backend\dist
if exist "backend\build" rmdir /S /Q backend\build
if exist "backend\*.spec" del /Q backend\*.spec
echo Limpieza completada.

rem --- Directorios persistentes ---
echo [2/5] Configurando directorios persistentes...
set DATA_DIR=%USERPROFILE%\AppData\Local\Apuntes2.0
mkdir "%DATA_DIR%" 2>nul
mkdir "%DATA_DIR%\database" 2>nul
mkdir "%DATA_DIR%\uploads" 2>nul
mkdir "%DATA_DIR%\models" 2>nul
echo. > "%DATA_DIR%\database\app.db"

rem --- Hooks para PyInstaller (creados correctamente en archivos) ---
echo [3/5] Creando hooks para PyInstaller...
mkdir backend\hooks 2>nul

echo import sys > backend\hooks\hook-tensorflow.py
echo import tensorflow as tf >> backend\hooks\hook-tensorflow.py
echo from PyInstaller.utils.hooks import collect_all >> backend\hooks\hook-tensorflow.py
echo datas, binaries, hiddenimports = collect_all('tensorflow') >> backend\hooks\hook-tensorflow.py

echo import os > backend\hooks\hook-nltk.py
echo import nltk >> backend\hooks\hook-nltk.py
echo from PyInstaller.utils.hooks import collect_data_files >> backend\hooks\hook-nltk.py
echo datas = collect_data_files('nltk') >> backend\hooks\hook-nltk.py
echo nltk_data_path = os.path.join(os.path.expanduser('~'), 'nltk_data') >> backend\hooks\hook-nltk.py
echo if os.path.exists(nltk_data_path): >> backend\hooks\hook-nltk.py
echo     datas += [(nltk_data_path, 'nltk_data')] >> backend\hooks\hook-nltk.py

rem --- Crear script de configuración de producción ---
echo [3.5/5] Creando script de configuración de producción...
echo import os > backend\app\__production_config.py
echo import sys >> backend\app\__production_config.py
echo. >> backend\app\__production_config.py
echo # Configurar entorno de producción >> backend\app\__production_config.py
echo os.environ['FLASK_ENV'] = 'production' >> backend\app\__production_config.py
echo. >> backend\app\__production_config.py
echo # Determinar directorio base >> backend\app\__production_config.py
echo if getattr(sys, 'frozen', False): >> backend\app\__production_config.py
echo     # Estamos en PyInstaller >> backend\app\__production_config.py
echo     BASE_DIR = sys._MEIPASS >> backend\app\__production_config.py
echo else: >> backend\app\__production_config.py
echo     # Estamos en desarrollo >> backend\app\__production_config.py
echo     BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) >> backend\app\__production_config.py
echo. >> backend\app\__production_config.py
echo # Definir directorio de datos persistente >> backend\app\__production_config.py
echo DATA_DIR = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Apuntes2.0') >> backend\app\__production_config.py
echo os.environ['DATA_DIR'] = DATA_DIR >> backend\app\__production_config.py
echo. >> backend\app\__production_config.py
echo # Crear directorios necesarios >> backend\app\__production_config.py
echo for subdir in ['database', 'uploads', 'models']: >> backend\app\__production_config.py
echo     os.makedirs(os.path.join(DATA_DIR, subdir), exist_ok=True) >> backend\app\__production_config.py
echo. >> backend\app\__production_config.py
echo # Configurar ruta de base de datos >> backend\app\__production_config.py
echo db_path = os.path.join(DATA_DIR, 'database', 'app.db').replace('\\', '/') >> backend\app\__production_config.py
echo os.environ['DATABASE_URL'] = f"sqlite:///{db_path}" >> backend\app\__production_config.py
echo. >> backend\app\__production_config.py
echo # Configurar carpeta de uploads >> backend\app\__production_config.py
echo os.environ['UPLOAD_FOLDER'] = os.path.join(DATA_DIR, 'uploads') >> backend\app\__production_config.py
echo. >> backend\app\__production_config.py
echo print(f"Configuración de producción cargada:") >> backend\app\__production_config.py
echo print(f"DATA_DIR: {DATA_DIR}") >> backend\app\__production_config.py
echo print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}") >> backend\app\__production_config.py
echo print(f"UPLOAD_FOLDER: {os.environ.get('UPLOAD_FOLDER')}") >> backend\app\__production_config.py

rem --- Crear script de entrada para producción ---
echo [3.6/5] Creando script de entrada para producción...
echo """Punto de entrada para producción""" > backend\run_prod.py
echo import os, sys >> backend\run_prod.py
echo. >> backend\run_prod.py
echo # Cargar configuración de producción primero >> backend\run_prod.py
echo from app.__production_config import * >> backend\run_prod.py
echo. >> backend\run_prod.py
echo # Importar app después de cargar configuración >> backend\run_prod.py
echo from app import create_app >> backend\run_prod.py
echo. >> backend\run_prod.py
echo app = create_app() >> backend\run_prod.py
echo. >> backend\run_prod.py
echo if __name__ == '__main__': >> backend\run_prod.py
echo     app.run(host='0.0.0.0', port=5000) >> backend\run_prod.py

rem --- Empaquetado con PyInstaller ---
echo [4/5] Empaquetando con PyInstaller...
cd backend
python -m PyInstaller --name ApuntesBackend ^
  --hidden-import=pytesseract ^
  --hidden-import=flask_cors ^
  --hidden-import=transformers ^
  --hidden-import=sentence_transformers ^
  --hidden-import=pyarrow ^
  --hidden-import=unidecode ^
  --hidden-import=nltk ^
  --hidden-import=tensorflow ^
  --hidden-import=numpy ^
  --hidden-import=sqlalchemy ^
  --add-data "config;config" ^
  --add-data "app/static;app/static" ^
  --add-data "app/templates;app/templates" ^
  --additional-hooks-dir=hooks ^
  --noconfirm ^
  --console ^
  run_prod.py
cd ..

rem --- Preparar distribución final ---
echo [5/5] Preparando distribución final...
if not exist "dist-apuntes" mkdir dist-apuntes
if not exist "dist-apuntes\backend" mkdir dist-apuntes\backend
xcopy /E /Y backend\dist\ApuntesBackend\* dist-apuntes\backend\

echo @echo off > dist-apuntes\iniciar-backend.bat
echo title Backend Apuntes 2.0 >> dist-apuntes\iniciar-backend.bat
echo cd /d "%%~dp0\backend" >> dist-apuntes\iniciar-backend.bat
echo echo Iniciando backend Flask... >> dist-apuntes\iniciar-backend.bat
echo echo. >> dist-apuntes\iniciar-backend.bat
echo start ApuntesBackend.exe >> dist-apuntes\iniciar-backend.bat
echo echo Backend iniciado en http://localhost:5000 >> dist-apuntes\iniciar-backend.bat
echo echo Para verificar, abre: http://localhost:5000/api/health >> dist-apuntes\iniciar-backend.bat
echo echo. >> dist-apuntes\iniciar-backend.bat
echo echo NOTA: Los datos se almacenan en: %USERPROFILE%\AppData\Local\Apuntes2.0 >> dist-apuntes\iniciar-backend.bat

echo.
echo =========================================================
echo     EMPAQUETADO COMPLETADO EXITOSAMENTE
echo =========================================================
echo.
echo El backend está disponible en: 
echo   %cd%\dist-apuntes\backend
echo.
echo La base de datos y archivos se guardarán en:
echo   %USERPROFILE%\AppData\Local\Apuntes2.0
echo.
echo Para iniciar el backend, ejecuta:
echo   dist-apuntes\iniciar-backend.bat
echo.
pause
