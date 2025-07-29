@echo off
echo.
echo ===== LIMPIEZA DE INSTALACION APUNTES 2.0 =====
echo.

cd auth-frontend
echo [1/3] Usando comando de Windows para eliminar node_modules...
rmdir /s /q node_modules 2>nul
if exist node_modules (
    echo Usando metodo alternativo para eliminar node_modules...
    powershell -Command "Remove-Item -Path 'node_modules' -Recurse -Force"
)
echo [2/3] Eliminando package-lock.json...
del /q package-lock.json 2>nul

echo [3/3] Limpiando cache npm...
call npm cache clean --force

echo.
echo ===== LIMPIEZA COMPLETA =====
echo.
echo Ahora ejecuta:
echo cd auth-frontend
echo npm install --no-audit --no-fund --no-optional
echo.
pause
