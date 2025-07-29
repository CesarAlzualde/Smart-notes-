@echo off
chcp 65001
title Empaquetado - Apuntes 2.0

set BASE_DIR=%~dp0
set BACKEND_DIR=%BASE_DIR%backend
set FRONTEND_DIR=%BASE_DIR%auth-frontend
set DIST_DIR=%BASE_DIR%dist-apuntes

echo ================================================================
echo               EMPAQUETADO - APUNTES 2.0
echo ================================================================
echo.
echo Empaquetando el backend y generando archivos de configuracion...
echo.

REM Crear directorio de distribucion si no existe
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"
if not exist "%DIST_DIR%\backend" mkdir "%DIST_DIR%\backend"

REM Empaquetar el backend con PyInstaller
cd "%BACKEND_DIR%"
echo [1/4] Limpiando compilaciones anteriores...
rmdir /S /Q dist build 2>nul
del /Q *.spec 2>nul

echo [2/4] Creando hooks para PyInstaller...
if not exist hooks mkdir hooks

echo import sys > hooks\hook-tensorflow.py
echo import tensorflow as tf >> hooks\hook-tensorflow.py
echo from PyInstaller.utils.hooks import collect_all >> hooks\hook-tensorflow.py
echo datas, binaries, hiddenimports = collect_all('tensorflow') >> hooks\hook-tensorflow.py

echo import os > hooks\hook-nltk.py
echo import nltk >> hooks\hook-nltk.py
echo from PyInstaller.utils.hooks import collect_data_files >> hooks\hook-nltk.py
echo datas = collect_data_files('nltk') >> hooks\hook-nltk.py
echo nltk_data_path = os.path.join(os.path.expanduser('~'), 'nltk_data') >> hooks\hook-nltk.py
echo if os.path.exists(nltk_data_path): >> hooks\hook-nltk.py
echo     datas += [(nltk_data_path, 'nltk_data')] >> hooks\hook-nltk.py

echo [3/4] Ejecutando PyInstaller...
pyinstaller --name ApuntesBackend --hidden-import=pytesseract --hidden-import=flask_cors --hidden-import=transformers --hidden-import=sentence_transformers --hidden-import=pyarrow --hidden-import=unidecode --hidden-import=nltk --hidden-import=tensorflow --hidden-import=numpy --add-data "config;config" --additional-hooks-dir=hooks --noconfirm --console run.py

echo [4/4] Copiando archivos al directorio de distribucion...
xcopy /E /I /Y dist\ApuntesBackend "%DIST_DIR%\backend"
echo.
echo Backend empaquetado correctamente en %DIST_DIR%\backend
echo.

echo ================================================================
echo           GENERANDO ARCHIVOS DE CONFIGURACION
echo ================================================================
echo.

echo [1/3] Creando archivos de configuracion necesarios...

REM Crear db_config.json en multiples ubicaciones
echo { "database_url": "sqlite:///instance/app.db" } > "%DIST_DIR%\db_config.json"
echo { "database_url": "sqlite:///instance/app.db" } > "%DIST_DIR%\backend\db_config.json"
mkdir "%DIST_DIR%\backend\config" 2>nul
echo { "database_url": "sqlite:///instance/app.db" } > "%DIST_DIR%\backend\config\db_config.json"

REM Crear configuracion falsa para Google Vision
echo { "type": "service_account" } > "%DIST_DIR%\backend\config\google-vision-key.json"

echo [2/3] Generando scripts de inicio...
echo @echo off > "%DIST_DIR%\iniciar-backend.bat"
echo title Backend Apuntes 2.0 >> "%DIST_DIR%\iniciar-backend.bat"
echo echo Iniciando backend Flask... >> "%DIST_DIR%\iniciar-backend.bat"
echo cd /d "%%~dp0backend" >> "%DIST_DIR%\iniciar-backend.bat"
echo start ApuntesBackend.exe >> "%DIST_DIR%\iniciar-backend.bat"
echo echo. >> "%DIST_DIR%\iniciar-backend.bat"
echo echo Backend iniciado en http://localhost:5000 >> "%DIST_DIR%\iniciar-backend.bat"
echo echo Para verificar, abre: http://localhost:5000/api/health >> "%DIST_DIR%\iniciar-backend.bat"
echo echo. >> "%DIST_DIR%\iniciar-backend.bat"
echo echo Presiona CTRL+C en la ventana del backend para detenerlo >> "%DIST_DIR%\iniciar-backend.bat"
echo echo. >> "%DIST_DIR%\iniciar-backend.bat"
echo pause >> "%DIST_DIR%\iniciar-backend.bat"

echo [3/3] Generando documentacion...
echo # Apuntes 2.0 - Guia de Usuario > "%DIST_DIR%\README.md"
echo. >> "%DIST_DIR%\README.md"
echo ## Instalacion >> "%DIST_DIR%\README.md"
echo. >> "%DIST_DIR%\README.md"
echo 1. Copia toda la carpeta de distribucion a la ubicacion deseada >> "%DIST_DIR%\README.md"
echo 2. Inicia el backend con iniciar-backend.bat >> "%DIST_DIR%\README.md"
echo. >> "%DIST_DIR%\README.md"
echo ## Funcionalidades >> "%DIST_DIR%\README.md"
echo. >> "%DIST_DIR%\README.md"
echo ### OCR y Reconocimiento de Texto >> "%DIST_DIR%\README.md"
echo - La aplicacion utiliza Tesseract OCR para reconocer texto en imagenes >> "%DIST_DIR%\README.md"
echo - Para usar Google Vision OCR, necesitas configurar las credenciales adecuadas >> "%DIST_DIR%\README.md"
echo. >> "%DIST_DIR%\README.md"
echo ### Analisis de Texto con IA >> "%DIST_DIR%\README.md"
echo - Utiliza el boton "Generar Analisis IA" para resumir y analizar textos >> "%DIST_DIR%\README.md"
echo - Los modelos utilizados estan optimizados para el espanol >> "%DIST_DIR%\README.md"
echo. >> "%DIST_DIR%\README.md"
echo ### Mapas Conceptuales >> "%DIST_DIR%\README.md"
echo - **Requiere Neo4j**: Para usar mapas conceptuales, debes instalar y ejecutar Neo4j manualmente >> "%DIST_DIR%\README.md"
echo - Descarga Neo4j Desktop desde [neo4j.com/download](https://neo4j.com/download/) >> "%DIST_DIR%\README.md"
echo - Crea una base de datos con usuario "neo4j" y contrasena "password" >> "%DIST_DIR%\README.md"
echo. >> "%DIST_DIR%\README.md"

echo.
echo ================================================================
echo             PROCESO DE EMPAQUETADO COMPLETADO
echo ================================================================
echo.
echo Distribucion disponible en: %DIST_DIR%
echo.
echo Proximos pasos:
echo  1. Inicia el backend con iniciar-backend.bat
echo  2. Accede a la interfaz a traves de http://localhost:5000
echo.
pause
