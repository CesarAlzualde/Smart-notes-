@echo off
chcp 65001 >nul
title 📦 Crear Instalador Profesional - Apuntes 2.0

echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║              📦 CREADOR DE INSTALADOR PROFESIONAL                     ║
echo ║                        Apuntes 2.0 v1.0                             ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

REM Verificar que Node.js esté instalado
echo [1/6] 🔍 Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Node.js no está instalado
    echo    Descarga e instala Node.js desde: https://nodejs.org
    pause
    exit /b 1
)
echo ✅ Node.js detectado

REM Cambiar al directorio del proyecto
cd /d "%~dp0"

REM Verificar estructura del proyecto
echo.
echo [2/6] 📁 Verificando estructura del proyecto...
if not exist "auth-frontend\package.json" (
    echo ❌ ERROR: No se encuentra el frontend
    pause
    exit /b 1
)
if not exist "backend\dist\ApuntesBackend.exe" (
    echo ❌ ERROR: Backend no empaquetado
    echo    Ejecuta primero el empaquetado del backend con PyInstaller
    pause
    exit /b 1
)
echo ✅ Estructura del proyecto verificada

REM Crear icono temporal si no existe
echo.
echo [3/6] 🎨 Preparando recursos...
cd auth-frontend
if not exist "assets\icon.ico" (
    echo 🔄 Creando icono temporal...
    REM Crear un icono simple usando PowerShell
    powershell -Command "Add-Type -AssemblyName System.Drawing; $bitmap = New-Object System.Drawing.Bitmap(32,32); $graphics = [System.Drawing.Graphics]::FromImage($bitmap); $graphics.Clear([System.Drawing.Color]::Blue); $graphics.FillEllipse([System.Drawing.Brushes]::White, 8, 8, 16, 16); $bitmap.Save('assets\icon.ico', [System.Drawing.Imaging.ImageFormat]::Icon); $graphics.Dispose(); $bitmap.Dispose()" 2>nul
    if not exist "assets\icon.ico" (
        echo ⚠️  No se pudo crear icono automáticamente
        echo    Usando icono por defecto del sistema
        echo. > assets\icon.ico
    )
)
echo ✅ Recursos preparados

REM Instalar dependencias del frontend
echo.
echo [4/6] 📦 Instalando dependencias...
echo 🔄 npm install...
call npm install --silent
if errorlevel 1 (
    echo ❌ ERROR: Falló la instalación de dependencias
    pause
    exit /b 1
)
echo ✅ Dependencias instaladas

REM Construir el frontend para producción
echo.
echo [5/6] 🏗️  Construyendo aplicación...
echo 🔄 Generando build de producción...
call npm run build
if errorlevel 1 (
    echo ❌ ERROR: Falló la construcción del frontend
    pause
    exit /b 1
)
echo ✅ Build de producción generado

REM Crear el instalador con electron-builder
echo.
echo [6/6] 🚀 Creando instalador...
echo 🔄 Empaquetando con Electron Builder...
call npm run dist
if errorlevel 1 (
    echo ❌ ERROR: Falló la creación del instalador
    echo    Revisa los logs arriba para más detalles
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║                  🎉 ¡INSTALADOR CREADO EXITOSAMENTE! 🎉              ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo 📍 Ubicación del instalador:
echo    📂 %CD%\dist-electron\
echo.
echo 📋 Archivos generados:
for %%f in (dist-electron\*.exe) do (
    echo    📄 %%f
)
echo.
echo 🔥 El instalador incluye:
echo    ✅ Frontend React empaquetado
echo    ✅ Backend Flask ejecutable
echo    ✅ Todas las dependencias
echo    ✅ Configuración automática
echo    ✅ Accesos directos
echo.
echo 💡 Para distribuir: Comparte el archivo .exe generado
echo    Los usuarios solo necesitan ejecutarlo para instalar todo
echo.

REM Abrir carpeta del instalador
echo ¿Deseas abrir la carpeta con el instalador? (S/N)
set /p choice="> "
if /i "%choice%"=="S" (
    start "" "dist-electron"
)

echo.
echo ¡Gracias por usar Apuntes 2.0!
pause
