@echo off
title Apuntes 2.0 - Iniciando...
color 0B

echo.
echo =============================================
echo       APUNTES 2.0 - INICIANDO SISTEMA
echo =============================================
echo.

REM Verificar si existe el backend
if not exist "backend\dist\ApuntesBackend\ApuntesBackend.exe" (
    echo ERROR: Backend no encontrado. Por favor ejecuta PyInstaller primero.
    pause
    exit /b 1
)

REM Iniciar backend en segundo plano
echo [1/3] Iniciando backend Flask...
start /min "Apuntes Backend" "backend\dist\ApuntesBackend\ApuntesBackend.exe"

REM Esperar a que el backend se inicie
echo [2/3] Esperando a que el backend se inicie...
timeout /t 5 /nobreak >nul

REM Verificar que el backend responda
echo [3/3] Verificando conexion con backend...
curl -s http://localhost:5000 >nul 2>&1
if errorlevel 1 (
    echo ADVERTENCIA: Backend podria no estar listo aun
    echo Continuando de todos modos...
) else (
    echo ✅ Backend listo y respondiendo
)

echo.
echo =============================================
echo        SISTEMA INICIADO EXITOSAMENTE
echo =============================================
echo.
echo 🌐 Frontend: http://localhost:5174
echo 🔧 Backend: http://localhost:5000
echo.
echo ⚠️  IMPORTANTE: NO cierres esta ventana
echo.

REM Abrir frontend en navegador
start http://localhost:5174

REM Mantener ventana abierta
echo Presiona cualquier tecla para cerrar la aplicacion...
pause >nul

REM Cerrar backend al salir
taskkill /im "ApuntesBackend.exe" /f >nul 2>&1
echo Sistema cerrado exitosamente.
