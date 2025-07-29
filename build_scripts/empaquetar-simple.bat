@echo off
chcp 65001 >nul
title Empaquetado Apuntes 2.0
color 0B

echo =======================================================
echo             EMPAQUETADO APUNTES 2.0
echo =======================================================

REM Definir directorios
set BACKEND_DIR=%~dp0backend
set FRONTEND_DIR=%~dp0auth-frontend
set DIST_DIR=%~dp0dist-apuntes

REM Verificar requisitos
echo [1/7] Verificando requisitos...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js no esta instalado
    echo    Descarga e instala Node.js desde: https://nodejs.org
    pause
    exit /b 1
)

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado
    echo    Descarga e instala Python desde: https://www.python.org
    pause
    exit /b 1
)

echo OK: Node.js y Python detectados

REM Crear directorios
echo [2/7] Preparando directorios...
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

REM Empaquetar backend con PyInstaller
echo [3/7] Empaquetando backend con PyInstaller...
cd "%BACKEND_DIR%"

echo - Limpiando compilaciones anteriores...
rmdir /S /Q dist build 2>nul
del /Q *.spec 2>nul

echo - Creando archivo spec...
pyinstaller --name ApuntesBackend ^
  --hidden-import pytesseract ^
  --hidden-import flask_cors ^
  --hidden-import transformers ^
  --hidden-import sentence_transformers ^
  --hidden-import pyarrow ^
  --hidden-import unidecode ^
  --hidden-import nltk ^
  --hidden-import tensorflow ^
  --hidden-import numpy ^
  --add-data "config;config" ^
  --add-data "app/static;app/static" ^
  --add-data "app/templates;app/templates" ^
  --noconfirm ^
  --console ^
  run.py

echo - Creando archivos de configuracion...
mkdir dist\ApuntesBackend\config 2>nul
copy config\db_config.json dist\ApuntesBackend\config\ /Y
copy config\ai_config.json dist\ApuntesBackend\config\ /Y
echo { "type": "service_account" } > dist\ApuntesBackend\config\google-vision-key.json
echo { "database_url": "sqlite:///instance/app.db" } > dist\ApuntesBackend\db_config.json
echo { "database_url": "sqlite:///instance/app.db" } > dist\ApuntesBackend\config\db_config.json

echo OK: Backend empaquetado correctamente

REM Configurar recursos para Electron
echo [4/7] Preparando recursos para Electron...
cd "%FRONTEND_DIR%"
if not exist "resources" mkdir resources
if not exist "resources\backend" mkdir resources\backend

echo - Copiando backend a recursos de Electron...
xcopy /E /I /Y "%BACKEND_DIR%\dist\ApuntesBackend" "resources\backend"

REM Actualizar electron.js
echo [5/7] Configurando electron.js...
cd "%FRONTEND_DIR%"
copy public\electron.js public\electron.js.backup /Y

REM Construir frontend
echo [6/7] Construyendo frontend...
call npm install --save-dev electron electron-builder
call npm run build

REM Crear instalador
echo [7/7] Creando instalador...
call npm run dist

REM Copiar instalador a directorio principal
echo Copiando instalador a directorio principal...
copy "dist-electron\*.exe" "%DIST_DIR%\" /Y

REM Crear scripts de ayuda
cd "%DIST_DIR%"
echo @echo off > configurar-primera-ejecucion.bat
echo echo ===== CONFIGURACION APUNTES 2.0 ===== >> configurar-primera-ejecucion.bat
echo echo. >> configurar-primera-ejecucion.bat
echo echo { "database_url": "sqlite:///instance/app.db" } ^> db_config.json >> configurar-primera-ejecucion.bat
echo echo Configuracion completa >> configurar-primera-ejecucion.bat
echo echo. >> configurar-primera-ejecucion.bat
echo pause >> configurar-primera-ejecucion.bat

echo =======================================================
echo          PROCESO DE EMPAQUETADO COMPLETADO
echo =======================================================
echo.
echo Instalador disponible en: %DIST_DIR%
echo.
echo Nota: Para un empaquetado completo con configuracion 
echo       optimizada, revisa los scripts individuales:
echo       - empaquetar-backend.bat
echo       - empaquetar-frontend.bat
echo.
pause
