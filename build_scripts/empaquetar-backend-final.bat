@echo off
rem Navega al directorio donde se encuentra el script
cd /d "%~dp0"

chcp 65001 > nul
echo ===== EMPAQUETADO FINAL DEL BACKEND FLASK =====
echo.

rem --- Limpieza ---
echo [1/5] Limpiando compilaciones anteriores...
if exist "backend\dist" rmdir /S /Q backend\dist
if exist "backend\build" rmdir /S /Q backend\build
if exist "backend\*.spec" del /Q backend\*.spec
if exist "backend\run_prod.py" del /Q backend\run_prod.py
if exist "backend\app\__production_config.py" del /Q backend\app\__production_config.py
echo Limpieza completada.

rem --- Preparación del Entorno de Producción ---
echo [2/5] Preparando entorno de produccion...

rem Crear el directorio de datos persistentes
set "DATA_DIR=%USERPROFILE%\AppData\Local\Apuntes2.0"
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"
if not exist "%DATA_DIR%\database" mkdir "%DATA_DIR%\database"
if not exist "%DATA_DIR%\uploads" mkdir "%DATA_DIR%\uploads"

rem Crear el archivo de configuración de producción en el código
( 
    echo import os
    echo import sys
    echo.
    echo # Determinar la ruta base, tanto para desarrollo como para PyInstaller
    echo if getattr(sys, 'frozen', False):
    echo     # Estamos en un entorno empaquetado
    echo     BASE_DIR = sys._MEIPASS
    echo else:
    echo     # Estamos en un entorno de desarrollo
    echo     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    echo.
    echo # Configurar directorio de datos persistentes
    echo DATA_DIR = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Apuntes2.0')
    echo os.environ['DATA_DIR'] = DATA_DIR
    echo.
    echo # Configurar URL de la base de datos
    echo db_path = os.path.join(DATA_DIR, 'database', 'app.db')
    echo os.environ['DATABASE_URL'] = f'sqlite:///{db_path.replace('\\', '/')}'
    echo.
    echo # Crear directorios si no existen
    echo os.makedirs(os.path.join(DATA_DIR, 'database'), exist_ok=True)
    echo os.makedirs(os.path.join(DATA_DIR, 'uploads'), exist_ok=True)
) > backend\app\__production_config.py

rem Crear el punto de entrada para producción
( 
    echo # Este script carga la configuracion de produccion antes de iniciar la app.
    echo import app.__production_config
    echo from app import create_app
    echo.
    echo app = create_app()
    echo.
    echo if __name__ == '__main__':
    echo     app.run(host='0.0.0.0', port=5000)
) > backend\run_prod.py


echo [3/5] Empaquetando la aplicacion con PyInstaller...
cd backend

pyinstaller --name ApuntesBackend ^
  --noconfirm ^
  --console ^
  --add-data "config;config" ^
  --add-data "app/static;app/static" ^
  --add-data "app/templates;app/templates" ^
  run_prod.py

if %errorlevel% neq 0 (
    echo.
    echo ***** ERROR: PyInstaller fallo. Abortando. *****
    cd ..
    pause
    exit /b
)

cd ..

echo [4/5] Preparando directorio de distribucion final...
if exist "dist-apuntes" rmdir /S /Q dist-apuntes
mkdir dist-apuntes
mkdir dist-apuntes\backend
xcopy /E /Y /I backend\dist\ApuntesBackend dist-apuntes\backend

echo [5/5] Creando scripts de inicio...
( 
    echo @echo off
    echo title Apuntes 2.0 - Backend
    echo echo Iniciando backend de Apuntes 2.0...
    echo cd /d "%~dp0\backend"
    echo ApuntesBackend.exe
) > dist-apuntes\iniciar-backend.bat


echo.
echo ====================================================
echo      BACKEND EMPAQUETADO EXITOSAMENTE
echo ====================================================
echo.
echo El backend empaquetado se encuentra en:
echo   %cd%\dist-apuntes
echo.
echo Para iniciar, ejecuta el siguiente archivo:
echo   dist-apuntes\iniciar-backend.bat
echo.
echo La base de datos y los archivos se guardaran en:
echo   %USERPROFILE%\AppData\Local\Apuntes2.0
echo.
pause
