@echo off
setlocal enabledelayedexpansion

echo ===== PREPARANDO DISTRIBUCION DE APUNTES 2.0 =====
echo.

REM Crear carpeta de distribución
echo [1/5] Creando estructura de carpetas...
if exist "dist-apuntes" rmdir /s /q "dist-apuntes"
mkdir "dist-apuntes"
mkdir "dist-apuntes\backend"
mkdir "dist-apuntes\config"
echo Estructura de carpetas creada

REM Copiar frontend
echo [2/5] Copiando frontend...
xcopy /E /I /H "auth-frontend\dist-electron\win-unpacked\*.*" "dist-apuntes\"
if errorlevel 1 (
    echo ERROR: No se pudo copiar el frontend
    pause
    exit /b 1
)
echo Frontend copiado correctamente

REM Copiar backend
echo [3/5] Copiando backend...
xcopy /E /I /H "backend\dist\ApuntesBackend\*.*" "dist-apuntes\backend\"
if errorlevel 1 (
    echo ERROR: No se pudo copiar el backend
    pause
    exit /b 1
)
echo Backend copiado correctamente

REM Copiar archivos de configuración
echo [4/5] Copiando configuraciones...
xcopy /E /I /H "backend\config\*.*" "dist-apuntes\config\"
if errorlevel 1 (
    echo ADVERTENCIA: No se copiaron todos los archivos de configuración
)
if exist "backend\.env" copy "backend\.env" "dist-apuntes\.env"
echo Configuración copiada correctamente

REM Crear script de inicio
echo [5/5] Creando script de inicio...
(
echo @echo off
echo echo ===== INICIANDO APUNTES 2.0 =====
echo echo.
echo echo [1/2] Iniciando el backend PyInstaller...
echo start "" "%%~dp0backend\ApuntesBackend.exe"
echo echo Esperando 3 segundos para inicialización del backend...
echo timeout /t 3 /nobreak ^> nul
echo echo [2/2] Iniciando la aplicación principal...
echo start "" "%%~dp0Apuntes 2.0 - Sistema de Notas con IA.exe"
echo echo.
echo echo NOTA: Para utilizar los mapas conceptuales, asegúrese de iniciar Neo4j manualmente.
echo echo.
) > "dist-apuntes\iniciar-apuntes.bat"
echo Script de inicio creado

echo.
echo ===== DISTRIBUCIÓN COMPLETADA =====
echo La aplicación completa está lista en la carpeta 'dist-apuntes'
echo Para ejecutar la aplicación, use el archivo 'iniciar-apuntes.bat'
echo.

pause
