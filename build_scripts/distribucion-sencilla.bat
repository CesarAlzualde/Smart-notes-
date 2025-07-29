@echo off
echo ===== CREANDO DISTRIBUCION APUNTES 2.0 =====
echo.

REM Crear estructura base
echo [1/4] Preparando estructura...
if exist "Apuntes2.0-Distribucion" rmdir /s /q "Apuntes2.0-Distribucion"
mkdir "Apuntes2.0-Distribucion"
mkdir "Apuntes2.0-Distribucion\frontend"
mkdir "Apuntes2.0-Distribucion\backend"
echo Estructura creada correctamente

REM Copiar frontend
echo [2/4] Copiando frontend...
robocopy "auth-frontend\dist-electron\win-unpacked" "Apuntes2.0-Distribucion\frontend" /E
echo Frontend copiado correctamente

REM Copiar backend
echo [3/4] Copiando backend...
robocopy "backend\dist\ApuntesBackend" "Apuntes2.0-Distribucion\backend" /E
echo Backend copiado correctamente

REM Crear script de inicio
echo [4/4] Creando script de inicio...
(
echo @echo off
echo echo ===== INICIANDO APUNTES 2.0 =====
echo echo.
echo echo [1/2] Iniciando backend...
echo start "" "%%~dp0backend\ApuntesBackend.exe"
echo echo Esperando 3 segundos para que el backend se inicialice...
echo timeout /t 3 /nobreak ^> nul
echo echo [2/2] Iniciando frontend...
echo cd "%%~dp0frontend"
echo start "" "%%~dp0frontend\Apuntes 2.0 - Sistema de Notas con IA.exe"
echo echo.
echo echo NOTA: Para utilizar mapas conceptuales, recuerde iniciar Neo4j manualmente.
) > "Apuntes2.0-Distribucion\iniciar-apuntes.bat"
echo Script de inicio creado correctamente

echo.
echo ===== DISTRIBUCIÓN COMPLETADA =====
echo.
echo La aplicación está lista en la carpeta 'Apuntes2.0-Distribucion'
echo Para iniciar la aplicación, ejecute 'iniciar-apuntes.bat'
echo.
echo NOTA: Esta distribución incluye todas las funcionalidades:
echo - OCR avanzado con Google Vision API
echo - Análisis de texto con IA (botón "Generar Análisis IA")
echo - Corrección gramatical y extracción de entidades
echo - Mapas conceptuales (requiere iniciar Neo4j manualmente)
echo.

pause
