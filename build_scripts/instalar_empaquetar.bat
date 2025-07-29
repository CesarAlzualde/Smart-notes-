@echo off
echo =========================================================
echo     INSTALACION Y EMPAQUETADO SIMPLIFICADO
echo =========================================================
echo.

cd /d "%~dp0"

echo Instalando PyInstaller...
pip install pyinstaller

echo.
echo Empaquetando backend...
cd backend

python -m PyInstaller --name ApuntesBackend^
 --hidden-import=pytesseract^
 --hidden-import=flask_cors^
 --hidden-import=transformers^
 --hidden-import=sentence_transformers^
 --hidden-import=pyarrow^
 --hidden-import=unidecode^
 --add-data "config;config"^
 --add-data "app/static;app/static"^
 --add-data "app/templates;app/templates"^
 --noconfirm^
 --onefile^
 run.py

echo.
echo Aplicando configuracion...
cd ..

if not exist "%USERPROFILE%\AppData\Local\Apuntes2.0\database" mkdir "%USERPROFILE%\AppData\Local\Apuntes2.0\database"
if not exist "%USERPROFILE%\AppData\Local\Apuntes2.0\uploads" mkdir "%USERPROFILE%\AppData\Local\Apuntes2.0\uploads"

echo { "database_url": "sqlite:///%USERPROFILE:\=/%/AppData/Local/Apuntes2.0/database/app.db" } > backend\config\db_config.json

echo.
echo =========================================================
echo     EMPAQUETADO COMPLETADO
echo =========================================================
echo.
echo El ejecutable esta en: backend\dist\ApuntesBackend.exe
echo.
echo Para ejecutar:
echo 1. Abrir una ventana de comandos
echo 2. Navegar a la carpeta backend\dist
echo 3. Ejecutar ApuntesBackend.exe
echo.
echo La base de datos se guardara en: %USERPROFILE%\AppData\Local\Apuntes2.0\database
echo.
pause
