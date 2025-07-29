@echo off
echo ===== SOLUCIONANDO ERRORES DE APUNTES 2.0 =====
echo.

set DIST_DIR=dist-apuntes
set BACKEND_DIR=%DIST_DIR%\backend
set CONFIG_DIR=%DIST_DIR%\config

echo [1/4] Solucionando error de db_config.json...
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

REM Crear db_config.json en todas las ubicaciones posibles donde el backend podría buscarlo
echo { "database_url": "sqlite:///instance/app.db" } > "%BACKEND_DIR%\db_config.json"
echo { "database_url": "sqlite:///instance/app.db" } > "%DIST_DIR%\db_config.json"
echo { "database_url": "sqlite:///instance/app.db" } > "%CONFIG_DIR%\db_config.json"

echo Archivos db_config.json creados en múltiples ubicaciones
echo.

echo [2/4] Creando archivo de configuración para Google Vision...
echo {
echo   "type": "service_account",
echo   "project_id": "apuntes-ocr",
echo   "private_key_id": "placeholder",
echo   "private_key": "-----BEGIN PRIVATE KEY-----\nMIIE...placeholder...==\n-----END PRIVATE KEY-----\n",
echo   "client_email": "vision-ocr@apuntes-ocr.iam.gserviceaccount.com",
echo   "client_id": "placeholder",
echo   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
echo   "token_uri": "https://oauth2.googleapis.com/token",
echo   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
echo   "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/vision-ocr%%40apuntes-ocr.iam.gserviceaccount.com",
echo   "universe_domain": "googleapis.com"
echo } > "%CONFIG_DIR%\google-vision-key.json"
copy "%CONFIG_DIR%\google-vision-key.json" "%BACKEND_DIR%\" /Y
echo.

echo [3/4] Creando script para omitir errores de Google Vision...
echo # Este archivo parchea el código para que funcione sin Google Vision > "%DIST_DIR%\disable_google_vision.py"
echo import os >> "%DIST_DIR%\disable_google_vision.py"
echo import sys >> "%DIST_DIR%\disable_google_vision.py"
echo import shutil >> "%DIST_DIR%\disable_google_vision.py"
echo. >> "%DIST_DIR%\disable_google_vision.py"
echo backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend") >> "%DIST_DIR%\disable_google_vision.py"
echo. >> "%DIST_DIR%\disable_google_vision.py"
echo # Crear archivo dummy para Google Vision >> "%DIST_DIR%\disable_google_vision.py"
echo with open(os.path.join(backend_dir, "google-vision-key.json"), "w") as f: >> "%DIST_DIR%\disable_google_vision.py"
echo     f.write('{"type": "service_account", "project_id": "dummy"}') >> "%DIST_DIR%\disable_google_vision.py"
echo. >> "%DIST_DIR%\disable_google_vision.py"
echo # Copiar db_config.json a todas las ubicaciones posibles >> "%DIST_DIR%\disable_google_vision.py"
echo db_config = '{"database_url": "sqlite:///instance/app.db"}' >> "%DIST_DIR%\disable_google_vision.py"
echo with open(os.path.join(backend_dir, "db_config.json"), "w") as f: >> "%DIST_DIR%\disable_google_vision.py"
echo     f.write(db_config) >> "%DIST_DIR%\disable_google_vision.py"
echo with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_config.json"), "w") as f: >> "%DIST_DIR%\disable_google_vision.py"
echo     f.write(db_config) >> "%DIST_DIR%\disable_google_vision.py"
echo config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config") >> "%DIST_DIR%\disable_google_vision.py"
echo os.makedirs(config_dir, exist_ok=True) >> "%DIST_DIR%\disable_google_vision.py"
echo with open(os.path.join(config_dir, "db_config.json"), "w") as f: >> "%DIST_DIR%\disable_google_vision.py"
echo     f.write(db_config) >> "%DIST_DIR%\disable_google_vision.py"
echo. >> "%DIST_DIR%\disable_google_vision.py"
echo print("¡Configuración completada con éxito!") >> "%DIST_DIR%\disable_google_vision.py"
echo.

echo [4/4] Creando script de inicio definitivo...
echo @echo off > "%DIST_DIR%\iniciar-definitivo.bat"
echo echo ===== INICIANDO APUNTES 2.0 (CONFIGURACION OPTIMIZADA) ===== >> "%DIST_DIR%\iniciar-definitivo.bat"
echo echo. >> "%DIST_DIR%\iniciar-definitivo.bat"
echo echo [1/5] Configurando entorno... >> "%DIST_DIR%\iniciar-definitivo.bat"
echo cd "%%~dp0" >> "%DIST_DIR%\iniciar-definitivo.bat"
echo python disable_google_vision.py >> "%DIST_DIR%\iniciar-definitivo.bat"
echo. >> "%DIST_DIR%\iniciar-definitivo.bat"
echo echo [2/5] Cerrando instancias previas... >> "%DIST_DIR%\iniciar-definitivo.bat"
echo taskkill /F /IM ApuntesBackend.exe 2^>nul >> "%DIST_DIR%\iniciar-definitivo.bat"
echo if %%ERRORLEVEL%% EQU 0 ( >> "%DIST_DIR%\iniciar-definitivo.bat"
echo     echo Procesos anteriores terminados >> "%DIST_DIR%\iniciar-definitivo.bat"
echo     timeout /t 2 /nobreak ^> nul >> "%DIST_DIR%\iniciar-definitivo.bat"
echo ) >> "%DIST_DIR%\iniciar-definitivo.bat"
echo. >> "%DIST_DIR%\iniciar-definitivo.bat"
echo echo [3/5] Preparando backend... >> "%DIST_DIR%\iniciar-definitivo.bat"
echo copy "config\db_config.json" "backend\" /Y ^> nul >> "%DIST_DIR%\iniciar-definitivo.bat"
echo copy "config\google-vision-key.json" "backend\" /Y ^> nul >> "%DIST_DIR%\iniciar-definitivo.bat"
echo copy "config\db_config.json" . /Y ^> nul >> "%DIST_DIR%\iniciar-definitivo.bat"
echo. >> "%DIST_DIR%\iniciar-definitivo.bat"
echo echo [4/5] Iniciando backend... >> "%DIST_DIR%\iniciar-definitivo.bat"
echo cd "%%~dp0" >> "%DIST_DIR%\iniciar-definitivo.bat"
echo start "Backend Apuntes 2.0" /min cmd /c "cd backend && ApuntesBackend.exe" >> "%DIST_DIR%\iniciar-definitivo.bat"
echo echo Esperando 5 segundos para inicialización del backend... >> "%DIST_DIR%\iniciar-definitivo.bat"
echo timeout /t 5 /nobreak ^> nul >> "%DIST_DIR%\iniciar-definitivo.bat"
echo. >> "%DIST_DIR%\iniciar-definitivo.bat"
echo echo [5/5] Iniciando aplicación principal... >> "%DIST_DIR%\iniciar-definitivo.bat"
echo cd "%%~dp0" >> "%DIST_DIR%\iniciar-definitivo.bat"
echo start "" "Apuntes 2.0 - Sistema de Notas con IA.exe" >> "%DIST_DIR%\iniciar-definitivo.bat"
echo. >> "%DIST_DIR%\iniciar-definitivo.bat"
echo echo ===== APLICACION INICIADA ===== >> "%DIST_DIR%\iniciar-definitivo.bat"
echo echo. >> "%DIST_DIR%\iniciar-definitivo.bat"
echo echo NOTA: Para usar los mapas conceptuales, debe iniciar Neo4j manualmente. >> "%DIST_DIR%\iniciar-definitivo.bat"
echo echo Las advertencias sobre Neo4j son normales si no está ejecutándose. >> "%DIST_DIR%\iniciar-definitivo.bat"
echo echo. >> "%DIST_DIR%\iniciar-definitivo.bat"
echo.

echo ===== CREANDO GUÍA DE USO =====
echo # Guía de Uso - Apuntes 2.0 > "%DIST_DIR%\LEEME.md"
echo. >> "%DIST_DIR%\LEEME.md"
echo ## Iniciar la aplicación >> "%DIST_DIR%\LEEME.md"
echo. >> "%DIST_DIR%\LEEME.md"
echo Para iniciar la aplicación correctamente, utiliza el script `iniciar-definitivo.bat`. >> "%DIST_DIR%\LEEME.md"
echo Este script: >> "%DIST_DIR%\LEEME.md"
echo. >> "%DIST_DIR%\LEEME.md"
echo 1. Configura todos los archivos necesarios >> "%DIST_DIR%\LEEME.md"
echo 2. Inicia el backend en segundo plano >> "%DIST_DIR%\LEEME.md"
echo 3. Inicia la interfaz principal >> "%DIST_DIR%\LEEME.md"
echo. >> "%DIST_DIR%\LEEME.md"
echo ## Solución de problemas >> "%DIST_DIR%\LEEME.md"
echo. >> "%DIST_DIR%\LEEME.md"
echo ### Pantalla en blanco >> "%DIST_DIR%\LEEME.md"
echo. >> "%DIST_DIR%\LEEME.md"
echo Si la aplicación muestra una pantalla en blanco: >> "%DIST_DIR%\LEEME.md"
echo. >> "%DIST_DIR%\LEEME.md"
echo 1. Cierra todas las ventanas de la aplicación >> "%DIST_DIR%\LEEME.md"
echo 2. Ejecuta nuevamente `iniciar-definitivo.bat` >> "%DIST_DIR%\LEEME.md"
echo. >> "%DIST_DIR%\LEEME.md"
echo ### Botón "Generar Análisis IA" no aparece >> "%DIST_DIR%\LEEME.md"
echo. >> "%DIST_DIR%\LEEME.md"
echo Si el botón no aparece: >> "%DIST_DIR%\LEEME.md"
echo. >> "%DIST_DIR%\LEEME.md"
echo 1. Asegúrate de que el backend está ejecutándose correctamente >> "%DIST_DIR%\LEEME.md"
echo 2. Reinicia completamente la aplicación >> "%DIST_DIR%\LEEME.md"
echo. >> "%DIST_DIR%\LEEME.md"
echo ### Mapas conceptuales >> "%DIST_DIR%\LEEME.md"
echo. >> "%DIST_DIR%\LEEME.md"
echo Para utilizar los mapas conceptuales: >> "%DIST_DIR%\LEEME.md"
echo. >> "%DIST_DIR%\LEEME.md"
echo 1. Instala Neo4j Desktop >> "%DIST_DIR%\LEEME.md"
echo 2. Crea una base de datos con contraseña >> "%DIST_DIR%\LEEME.md"
echo 3. Inicia la base de datos antes de usar la funcionalidad de mapas >> "%DIST_DIR%\LEEME.md"
echo. >> "%DIST_DIR%\LEEME.md"
echo ### OCR y análisis de texto >> "%DIST_DIR%\LEEME.md"
echo. >> "%DIST_DIR%\LEEME.md"
echo - El OCR utilizará Tesseract por defecto >> "%DIST_DIR%\LEEME.md"
echo - La funcionalidad de Google Vision OCR está deshabilitada >> "%DIST_DIR%\LEEME.md"
echo - Para habilitar Google Vision OCR, crea un archivo `google-vision-key.json` válido en la carpeta `config` >> "%DIST_DIR%\LEEME.md"
echo. >> "%DIST_DIR%\LEEME.md"
echo.

echo ===== INSTALACIÓN COMPLETADA =====
echo.
echo Se han creado los siguientes archivos:
echo 1. Archivos de configuración en múltiples ubicaciones
echo 2. Script de inicio mejorado: iniciar-definitivo.bat
echo 3. Guía de uso: LEEME.md
echo.
echo Por favor, utiliza el script 'iniciar-definitivo.bat' para iniciar la aplicación.
echo.
echo Presiona cualquier tecla para copiar estos archivos a la carpeta de distribución...
pause

echo.
echo Copiando archivos a carpeta de distribución...

if exist "%DIST_DIR%" (
    copy "arreglar-errores-ejecucion.bat" "%DIST_DIR%\" /Y > nul
) else (
    echo ERROR: La carpeta %DIST_DIR% no existe.
    echo Ejecuta primero el script distribucion-sencilla.bat para crear la carpeta.
)

echo.
echo Proceso completado.
echo.

pause
