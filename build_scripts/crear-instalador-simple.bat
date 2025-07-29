@echo off
chcp 65001 > nul
echo.
echo ===== INSTALADOR SIMPLE APUNTES 2.0 =====
echo.

rem Verificar Node.js
echo [1/4] Verificando Node.js...
node --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js no esta instalado
    pause
    exit /b 1
)
echo OK: Node.js encontrado

rem Ir al directorio frontend
echo [2/4] Preparando frontend...
cd auth-frontend
if errorlevel 1 (
    echo ERROR: No se encuentra directorio frontend
    pause
    exit /b 1
)

rem Instalar dependencias rápido
echo [3/4] Instalando dependencias (modo rápido)...
npm install --no-audit --no-fund --silent

rem Crear instalador con configuración mínima
echo [4/4] Creando instalador...
set ELECTRON_BUILDER_ALLOW_UNRESOLVED_DEPENDENCIES=true
npx electron-builder --win --x64 --publish=never

if errorlevel 1 (
    echo ERROR: Fallo al crear instalador
    pause
    exit /b 1
)

echo.
echo ===== INSTALADOR CREADO EXITOSAMENTE =====
echo Ubicacion: auth-frontend\dist-electron\
echo.
pause
