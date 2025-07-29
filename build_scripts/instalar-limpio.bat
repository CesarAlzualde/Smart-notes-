@echo off
echo.
echo ===== INSTALADOR LIMPIO APUNTES 2.0 =====
echo.

REM Verificar Node.js
echo [1/5] Verificando Node.js...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js no esta instalado
    pause
    exit /b 1
)
echo OK: Node.js encontrado

REM Ir al directorio frontend
echo [2/5] Preparando frontend...
cd auth-frontend
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se encuentra directorio frontend
    pause
    exit /b 1
)

REM Eliminar node_modules y reinstalar todo desde cero
echo [3/5] Limpiando instalación anterior...
rmdir /s /q node_modules
del /q package-lock.json
echo Instalación anterior eliminada

REM Instalar dependencias sin aplicar parches
echo [4/5] Instalando dependencias (sin parches)...
set npm_config_loglevel=error
set ADBLOCK=1
set npm_config_no_update_notifier=1
call npm install --no-audit --no-fund --no-optional --no-scripts
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Fallo la instalacion de dependencias
    pause
    exit /b 1
)
echo Dependencias instaladas correctamente

REM Crear instalador con configuracion minima
echo [5/5] Creando instalador...
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
