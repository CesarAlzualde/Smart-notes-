@echo off
chcp 65001 >nul
title 🚀 Apuntes 2.0 - Sistema de Notas con IA
color 0B

echo.
echo ████████████████████████████████████████████████████
echo █                APUNTES 2.0                      █
echo █          Sistema de Notas con IA                █  
echo █              ¡Iniciando!                       █
echo ████████████████████████████████████████████████████
echo.
echo 🔧 Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Node.js no está instalado
    echo Por favor instala Node.js desde https://nodejs.org
    pause
    exit /b 1
)

echo ✅ Node.js detectado
echo.
echo 🚀 Iniciando Apuntes 2.0...
echo ⏱️  Por favor espera mientras se cargan todos los servicios...
echo.

REM Cambiar al directorio del proyecto
cd /d "%~dp0"

REM Ejecutar launcher Node.js
node start-apuntes.js

if errorlevel 1 (
    echo.
    echo ❌ Error al iniciar la aplicación
    echo 📋 Revisa los logs anteriores para más detalles
    echo.
    pause
) else (
    echo.
    echo ✅ Aplicación cerrada correctamente
)
