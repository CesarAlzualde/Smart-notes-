@echo off
chcp 65001 > nul
title Generador de Instalador - Apuntes 2.0
color 0B

echo ================================================================
echo          GENERADOR DE INSTALADOR PARA APUNTES 2.0
echo ================================================================
echo.
echo Este script generará un instalador completo que incluirá:
echo  - Frontend (Electron/React)
echo  - Backend empaquetado (PyInstaller/Flask)
echo  - Archivos de configuración necesarios
echo.

rem Verificar que Node.js esté instalado
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js no está instalado o no está en el PATH.
    echo Por favor, instala Node.js desde https://nodejs.org/
    pause
    exit /b 1
)

echo [1/6] Verificando estructura del proyecto...

set BASE_DIR=%~dp0
set DIST_APUNTES=%BASE_DIR%dist-apuntes
set FRONTEND_DIR=%BASE_DIR%auth-frontend

if not exist "%DIST_APUNTES%\backend\ApuntesBackend.exe" (
    echo ERROR: No se encontró el backend empaquetado.
    echo Ejecuta primero el script empaquetar.bat para generar el backend.
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%" (
    echo ERROR: No se encontró el directorio del frontend.
    pause
    exit /b 1
)

echo [2/6] Instalando dependencias del frontend...
cd /d "%FRONTEND_DIR%"

echo Ejecutando npm install...
call npm install --force
if %errorlevel% neq 0 (
    echo ERROR: Falló la instalación de dependencias del frontend.
    pause
    exit /b 1
)

echo [3/6] Preparando el directorio de recursos...
if not exist "%FRONTEND_DIR%\resources" mkdir "%FRONTEND_DIR%\resources"
if not exist "%FRONTEND_DIR%\resources\backend" mkdir "%FRONTEND_DIR%\resources\backend"

echo Copiando archivos del backend a los recursos de Electron...
xcopy /E /I /Y "%DIST_APUNTES%\backend" "%FRONTEND_DIR%\resources\backend"
if %errorlevel% neq 0 (
    echo ERROR: Falló la copia de archivos del backend a recursos.
    pause
    exit /b 1
)

echo [4/6] Configurando archivos de distribución...
copy /Y "%BASE_DIR%\dist-apuntes\MANUAL_USUARIO.md" "%FRONTEND_DIR%\README.md"

echo [5/6] Generando build de producción...
call npm run build
if %errorlevel% neq 0 (
    echo ERROR: Falló la generación del build.
    pause
    exit /b 1
)

echo [6/6] Creando instalador con electron-builder...
call npm run make
if %errorlevel% neq 0 (
    echo ERROR: Falló la generación del instalador.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo        INSTALADOR GENERADO CORRECTAMENTE
echo ================================================================
echo.
echo El instalador se encuentra en: %FRONTEND_DIR%\out\make\squirrel.windows\x64\
echo.
echo Para distribuir la aplicación, comparte el archivo .exe de esta carpeta.
echo.
pause
