@echo off
echo Creando icono temporal para Apuntes 2.0...
echo.
echo NOTA: Para un icono profesional, reemplaza icon.ico con tu diseño personalizado
echo.

REM Crear un icono básico usando recursos del sistema
copy "%SystemRoot%\System32\shell32.dll" temp_shell32.dll >nul 2>&1
if exist temp_shell32.dll (
    echo Icono temporal creado exitosamente
    ren temp_shell32.dll icon.ico
) else (
    echo No se pudo crear icono automáticamente
    echo Por favor, agrega manualmente un archivo icon.ico en esta carpeta
)

echo.
echo ¡Listo para continuar con el empaquetado!
pause
