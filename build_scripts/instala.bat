@echo off
echo.
echo ===== INSTALADOR SIMPLE APUNTES 2.0 =====
echo.

REM Verificar Node.js
echo [1/4] Verificando Node.js...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js no esta instalado
    pause
    exit /b 1
)
echo OK: Node.js encontrado

REM Ir al directorio frontend
echo [2/4] Preparando frontend...
cd auth-frontend
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se encuentra directorio frontend
    pause
    exit /b 1
)

REM Instalar dependencias rapido
echo [3/4] Instalando dependencias (modo rapido)...
call npm install --no-audit --no-fund
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Fallo la instalacion de dependencias
    pause
    exit /b 1
)

REM Crear instalador con configuracion minima
echo [4/4] Creando instalador...
set ELECTRON_BUILDER_ALLOW_UNRESOLVED_DEPENDENCIES=true
call npx electron-builder --win --x64 --publish=never
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Fallo al crear instalador
    pause
    exit /b 1
)

echo.
echo ===== INSTALADOR CREADO EXITOSAMENTE =====
echo Ubicacion: auth-frontend\dist-electron\
echo.
pause
