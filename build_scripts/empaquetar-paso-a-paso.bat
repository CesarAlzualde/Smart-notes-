@echo off
chcp 65001 >nul
title Empaquetado Paso a Paso - Apuntes 2.0
color 0B

REM Definición de directorios
set BASE_DIR=%~dp0
set BACKEND_DIR=%BASE_DIR%backend
set FRONTEND_DIR=%BASE_DIR%auth-frontend
set DIST_DIR=%BASE_DIR%dist-apuntes

echo ================================================================
echo               EMPAQUETADO PASO A PASO - APUNTES 2.0
echo ================================================================
echo.
echo Este script empaqueta el backend y prepara los archivos necesarios
echo para una distribución completa del sistema.
echo.
echo OPCIONES:
echo [1] Empaquetar solo el backend (PyInstaller)
echo [2] Generar archivos de configuración y scripts de inicio
echo [3] Proceso completo (1 + 2)
echo [4] Salir
echo.
choice /C 1234 /N /M "Seleccione una opción (1-4): "

if errorlevel 4 goto :EOF
if errorlevel 3 goto :COMPLETO
if errorlevel 2 goto :CONFIGURACION
if errorlevel 1 goto :BACKEND

:COMPLETO
call :BACKEND
call :CONFIGURACION
goto :EOF

:BACKEND
echo.
echo ================================================================
echo                    EMPAQUETANDO BACKEND
echo ================================================================
echo.

REM Crear directorio de distribución si no existe
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
pyinstaller --name ApuntesBackend ^
  --hidden-import=pytesseract ^
  --hidden-import=flask_cors ^
  --hidden-import=transformers ^
  --hidden-import=sentence_transformers ^
  --hidden-import=pyarrow ^
  --hidden-import=unidecode ^
  --hidden-import=nltk ^
  --hidden-import=tensorflow ^
  --hidden-import=numpy ^
  --add-data "config;config" ^
  --additional-hooks-dir=hooks ^
  --noconfirm ^
  --console ^
  run.py

echo [4/4] Copiando archivos al directorio de distribución...
xcopy /E /I /Y dist\ApuntesBackend "%DIST_DIR%\backend"
echo.
echo Backend empaquetado correctamente en %DIST_DIR%\backend
echo.
goto :EOF

:CONFIGURACION
echo.
echo ================================================================
echo           GENERANDO ARCHIVOS DE CONFIGURACIÓN
echo ================================================================
echo.

echo [1/4] Creando archivos de configuración necesarios...

REM Crear db_config.json en múltiples ubicaciones
echo { "database_url": "sqlite:///instance/app.db" } > "%DIST_DIR%\db_config.json"
echo { "database_url": "sqlite:///instance/app.db" } > "%DIST_DIR%\backend\db_config.json"
mkdir "%DIST_DIR%\backend\config" 2>nul
echo { "database_url": "sqlite:///instance/app.db" } > "%DIST_DIR%\backend\config\db_config.json"

REM Crear configuración falsa para Google Vision
echo { "type": "service_account" } > "%DIST_DIR%\backend\config\google-vision-key.json"

echo [2/4] Generando script de inicio del backend...
(
  echo @echo off
  echo title Backend Apuntes 2.0
  echo echo Iniciando backend Flask...
  echo cd /d "%%~dp0backend"
  echo start ApuntesBackend.exe
  echo echo.
  echo echo Backend iniciado en http://localhost:5000
  echo echo Para verificar, abre: http://localhost:5000/api/health
  echo echo.
  echo echo Presiona CTRL+C en la ventana del backend para detenerlo
  echo echo.
  echo pause
) > "%DIST_DIR%\iniciar-backend.bat"

echo [3/4] Generando script de primera ejecución...
(
  echo @echo off
  echo title Primera ejecución - Apuntes 2.0
  echo.
  echo echo ===== CONFIGURACIÓN INICIAL DE APUNTES 2.0 =====
  echo echo.
  echo echo [1/2] Configurando archivos necesarios...
  echo.
  echo echo { "database_url": "sqlite:///instance/app.db" } ^> db_config.json
  echo echo { "database_url": "sqlite:///instance/app.db" } ^> backend\db_config.json
  echo echo { "database_url": "sqlite:///instance/app.db" } ^> backend\config\db_config.json
  echo echo { "type": "service_account" } ^> backend\config\google-vision-key.json
  echo echo.
  echo echo [2/2] Configuración completa
  echo echo.
  echo echo Para iniciar Apuntes 2.0:
  echo echo  1. Ejecuta iniciar-backend.bat
  echo echo  2. [Opcional] Inicia Neo4j si necesitas mapas conceptuales
  echo echo.
  echo echo NOTA: Para OCR avanzado, coloca tus credenciales de Google Vision en:
  echo echo       backend\config\google-vision-key.json
  echo echo.
  echo pause
) > "%DIST_DIR%\configurar-primera-ejecucion.bat"

echo [4/4] Generando documentación...
(
  echo # Apuntes 2.0 - Guía de Usuario
  echo.
  echo ## Instalación
  echo.
  echo 1. Copia toda la carpeta de distribución a la ubicación deseada
  echo 2. Ejecuta `configurar-primera-ejecucion.bat` para inicializar el sistema
  echo.
  echo ## Inicio del Sistema
  echo.
  echo 1. Ejecuta `iniciar-backend.bat` para iniciar el backend Flask
  echo 2. Accede a la interfaz web a través de http://localhost:5000
  echo.
  echo ## Funcionalidades
  echo.
  echo ### OCR y Reconocimiento de Texto
  echo - La aplicación utiliza Tesseract OCR para reconocer texto en imágenes
  echo - Para usar Google Vision OCR, necesitas configurar las credenciales adecuadas
  echo.
  echo ### Análisis de Texto con IA
  echo - Utiliza el botón "Generar Análisis IA" para resumir y analizar textos
  echo - Los modelos utilizados están optimizados para el español
  echo.
  echo ### Mapas Conceptuales
  echo - **Requiere Neo4j**: Para usar mapas conceptuales, debes instalar y ejecutar Neo4j manualmente
  echo - Descarga Neo4j Desktop desde [neo4j.com/download](https://neo4j.com/download/)
  echo - Crea una base de datos con usuario "neo4j" y contraseña "password"
  echo.
  echo ## Solución de Problemas
  echo.
  echo ### Error de db_config.json
  echo - Ejecuta `configurar-primera-ejecucion.bat` para regenerar los archivos de configuración
  echo.
  echo ### Advertencias de Neo4j
  echo - Son normales si no tienes Neo4j ejecutándose
  echo - No afectan a las demás funcionalidades de la aplicación
) > "%DIST_DIR%\README.md"

echo.
echo Archivos de configuración y scripts generados en %DIST_DIR%
echo.
goto :EOF

:EOF
echo.
echo ================================================================
echo             PROCESO DE EMPAQUETADO COMPLETADO
echo ================================================================
echo.
echo Distribución disponible en: %DIST_DIR%
echo.
echo Próximos pasos:
echo  1. Ejecuta configurar-primera-ejecucion.bat en la carpeta de distribución
echo  2. Inicia el backend con iniciar-backend.bat
echo  3. Accede a la interfaz a través de http://localhost:5000
echo.
pause
