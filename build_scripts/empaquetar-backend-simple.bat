@echo off
cd /d "%~dp0"
echo ===== EMPAQUETADO SIMPLIFICADO DEL BACKEND =====
echo.

rem --- Configuracion inicial ---
echo [1/5] Configurando directorios de datos...
set DATA_DIR=%USERPROFILE%\AppData\Local\Apuntes2.0
mkdir "%DATA_DIR%\database" 2>nul
mkdir "%DATA_DIR%\uploads" 2>nul
echo. > "%DATA_DIR%\database\app.db"

rem --- Crear archivo de configuracion ---
echo [2/5] Creando archivo de configuracion...
echo { > backend\config\db_config.json
echo   "database_url": "sqlite:///%USERPROFILE%/AppData/Local/Apuntes2.0/database/app.db" >> backend\config\db_config.json
echo } >> backend\config\db_config.json

rem --- Limpieza ---
echo [3/5] Limpiando compilaciones anteriores...
if exist "backend\dist" rmdir /S /Q backend\dist
if exist "backend\build" rmdir /S /Q backend\build
if exist "backend\*.spec" del /Q backend\*.spec
echo Limpieza completada.

rem --- Empaquetar con PyInstaller ---
echo [4/5] Empaquetando la aplicacion...
cd backend
pyinstaller --name ApuntesBackend ^
  --hidden-import=flask_cors ^
  --hidden-import=pytesseract ^
  --hidden-import=transformers ^
  --hidden-import=sqlalchemy ^
  --add-data "config;config" ^
  --noconfirm ^
  --console ^
  run.py
cd ..

rem --- Crear directorio final ---
echo [5/5] Preparando distribucion final...
if not exist "dist-apuntes" mkdir dist-apuntes
if not exist "dist-apuntes\backend" mkdir dist-apuntes\backend
xcopy /E /Y backend\dist\ApuntesBackend\* dist-apuntes\backend\

echo @echo off > dist-apuntes\iniciar-backend.bat
echo cd /d "%%~dp0\backend" >> dist-apuntes\iniciar-backend.bat
echo echo Iniciando backend de Apuntes 2.0... >> dist-apuntes\iniciar-backend.bat
echo start ApuntesBackend.exe >> dist-apuntes\iniciar-backend.bat
echo echo Backend iniciado en http://localhost:5000 >> dist-apuntes\iniciar-backend.bat
echo echo Para verificar, abre: http://localhost:5000/api/health >> dist-apuntes\iniciar-backend.bat
echo echo. >> dist-apuntes\iniciar-backend.bat
echo echo NOTA: La base de datos se encuentra en %DATA_DIR%\database\app.db >> dist-apuntes\iniciar-backend.bat

echo.
echo ====================================================
echo      BACKEND EMPAQUETADO EXITOSAMENTE
echo ====================================================
echo.
echo El backend empaquetado se encuentra en:
echo   %cd%\dist-apuntes\backend
echo.
echo La base de datos se encuentra en:
echo   %DATA_DIR%\database\app.db
echo.
echo Para probar, ejecuta:
echo   dist-apuntes\iniciar-backend.bat
echo.
pause
