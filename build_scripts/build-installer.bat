@echo off
title Crear Instalador - Apuntes 2.0

echo.
echo ===== CREADOR DE INSTALADOR APUNTES 2.0 =====
echo.

echo [1/6] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js no instalado
    pause
    exit /b 1
)
echo OK: Node.js encontrado

echo.
echo [2/6] Verificando estructura...
if not exist "auth-frontend\package.json" (
    echo ERROR: Frontend no encontrado
    pause
    exit /b 1
)
if not exist "backend\dist\ApuntesBackend\ApuntesBackend.exe" (
    echo ERROR: Backend no empaquetado
    echo Ejecuta primero: cd backend ^&^& pyinstaller ApuntesBackend.spec
    pause
    exit /b 1
)
echo OK: Estructura verificada

echo.
echo [3/6] Preparando recursos...
cd auth-frontend
if not exist "assets\icon.ico" (
    echo Creando icono basico...
    echo temp > assets\icon.ico
)
echo OK: Recursos listos

echo.
echo [4/6] Instalando dependencias...
call npm install
if errorlevel 1 (
    echo ERROR: npm install fallo
    pause
    exit /b 1
)
echo OK: Dependencias instaladas

echo.
echo [5/6] Construyendo aplicacion...
call npm run build
if errorlevel 1 (
    echo ERROR: Build fallo
    pause
    exit /b 1
)
echo OK: Build completado

echo.
echo [6/6] Creando instalador...
call npm run dist
if errorlevel 1 (
    echo ERROR: Instalador fallo
    pause
    exit /b 1
)

echo.
echo ===== INSTALADOR CREADO EXITOSAMENTE =====
echo.
echo Ubicacion: %CD%\dist-electron\
echo.
dir dist-electron\*.exe
echo.
echo Abrir carpeta? (S/N)
set /p choice=
if /i "%choice%"=="S" start "" "dist-electron"

pause
