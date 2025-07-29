@echo off
rem Este script debe ejecutarse con CMD, no PowerShell
cd /d "%~dp0"

echo ===== EMPAQUETADO FINAL DEL BACKEND FLASK =====
echo.

rem --- Limpieza ---
echo [1/5] Limpiando compilaciones anteriores...
if exist "backend\dist" rmdir /S /Q backend\dist
if exist "backend\build" rmdir /S /Q backend\build
if exist "backend\*.spec" del /Q backend\*.spec
echo Limpieza completada.

rem --- Crear directorio de datos ---
echo [2/5] Configurando directorios de datos...
set DATA_DIR=%USERPROFILE%\AppData\Local\Apuntes2.0
mkdir "%DATA_DIR%\database" 2>nul
mkdir "%DATA_DIR%\uploads" 2>nul

rem --- Configurar la aplicación para usar rutas absolutas ---
echo [3/5] Empaquetando la aplicacion con PyInstaller...

echo { > backend\config\db_config.json
echo   "database_url": "sqlite:///%USERPROFILE%/AppData/Local/Apuntes2.0/database/app.db" >> backend\config\db_config.json
echo } >> backend\config\db_config.json

cd backend
pyinstaller --name ApuntesBackend ^
  --hidden-import=flask_cors ^
  --hidden-import=pytesseract ^
  --add-data "config;config" ^
  --add-data "app/static;app/static" ^
  --add-data "app/templates;app/templates" ^
  --noconfirm ^
  --console ^
  run.py
cd ..

rem --- Preparar directorio final ---
echo [4/5] Preparando directorio final...
if not exist "dist-apuntes" mkdir dist-apuntes
if not exist "dist-apuntes\backend" mkdir dist-apuntes\backend
xcopy /E /Y backend\dist\ApuntesBackend\* dist-apuntes\backend\

rem --- Crear script de inicio ---
echo [5/5] Creando scripts de inicio...
echo @echo off > dist-apuntes\iniciar-backend.bat
echo cd /d "%%~dp0\backend" >> dist-apuntes\iniciar-backend.bat
echo echo Iniciando backend de Apuntes 2.0... >> dist-apuntes\iniciar-backend.bat
echo start ApuntesBackend.exe >> dist-apuntes\iniciar-backend.bat
echo echo Backend iniciado en http://localhost:5000 >> dist-apuntes\iniciar-backend.bat
echo echo Para verificar, abre: http://localhost:5000/api/health >> dist-apuntes\iniciar-backend.bat

echo.
echo ====================================================
echo      BACKEND EMPAQUETADO EXITOSAMENTE
echo ====================================================
echo.
echo El backend empaquetado se encuentra en:
echo   %cd%\dist-apuntes
echo.
echo La base de datos y los archivos se guardaran en:
echo   %USERPROFILE%\AppData\Local\Apuntes2.0
echo.
pause
