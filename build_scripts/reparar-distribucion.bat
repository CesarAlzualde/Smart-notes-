@echo off
echo ===== REPARACION DE APUNTES 2.0 =====
echo.

set DIST_DIR=dist-apuntes
set CONFIG_DIR=%DIST_DIR%\config

echo [1/5] Corrigiendo archivos de configuracion...
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

echo Copiando db_config.json...
copy "backend\config\db_config.json" "%CONFIG_DIR%\" /Y
if not exist "%CONFIG_DIR%\db_config.json" (
    echo { "database_url": "sqlite:///instance/app.db" } > "%CONFIG_DIR%\db_config.json"
    echo Creado db_config.json predeterminado
)

echo Copiando ai_config.json...
copy "backend\config\ai_config.json" "%CONFIG_DIR%\" /Y
if not exist "%CONFIG_DIR%\ai_config.json" (
    echo Creando ai_config.json predeterminado...
    echo { "summarization_models": ["josmunpen/mt5-small-spanish-summarization"], "correction_models": ["JasperLS/T5-Grammar-Checker-Spanish", "google/mt5-small"] } > "%CONFIG_DIR%\ai_config.json"
)

echo Copiando archivo .env...
copy "backend\.env" "%DIST_DIR%\" /Y
if not exist "%DIST_DIR%\.env" (
    echo JWT_SECRET_KEY=apuntes2_dev_key_please_change_in_production > "%DIST_DIR%\.env"
    echo DATABASE_URL=sqlite:///instance/app.db >> "%DIST_DIR%\.env"
    echo UPLOAD_FOLDER=uploads >> "%DIST_DIR%\.env"
    echo SECRET_KEY=dev_secret_key_change_in_production >> "%DIST_DIR%\.env"
    echo Creado .env predeterminado
)

echo.
echo [2/5] Verificando estructura de archivos...
if not exist "%DIST_DIR%\backend" (
    echo ERROR: No se encontro la carpeta del backend
    echo Asegurese de que el backend exista en %DIST_DIR%\backend
) else (
    echo Estructura del backend OK
)

echo.
echo [3/5] Mejorando script de inicio...
echo @echo off > "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo echo ===== INICIANDO APUNTES 2.0 ===== >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo echo. >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo echo [1/3] Verificando archivos de configuracion... >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo if not exist "config\db_config.json" ( >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo   echo ERROR: Falta archivo db_config.json >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo   echo Ejecute primero reparar-distribucion.bat >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo   pause >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo   exit /b 1 >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo ) >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo echo Archivos de configuracion OK >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo echo. >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo echo [2/3] Iniciando el backend PyInstaller... >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo cd "%%~dp0" >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo copy config\db_config.json . >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat" 
echo start "" "%%~dp0backend\ApuntesBackend.exe" >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo echo Esperando 5 segundos para inicializacion del backend... >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo timeout /t 5 /nobreak ^> nul >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo echo [3/3] Iniciando la aplicacion principal... >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo cd "%%~dp0" >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo start "" "%%~dp0Apuntes 2.0 - Sistema de Notas con IA.exe" >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo echo. >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo echo NOTA: >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo echo - Para utilizar los mapas conceptuales, asegurese de iniciar Neo4j manualmente. >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo echo - Si el boton "Generar Analisis IA" no aparece, reinicie la aplicacion. >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo echo. >> "%DIST_DIR%\iniciar-apuntes-mejorado.bat"
echo.
echo Script de inicio mejorado creado

echo.
echo [4/5] Creando archivo solucionar-problemas.txt...
echo ===== GUÍA DE SOLUCIÓN DE PROBLEMAS ===== > "%DIST_DIR%\solucionar-problemas.txt"
echo. >> "%DIST_DIR%\solucionar-problemas.txt"
echo Si encuentras alguno de estos problemas, aquí tienes las soluciones: >> "%DIST_DIR%\solucionar-problemas.txt"
echo. >> "%DIST_DIR%\solucionar-problemas.txt"
echo 1. PROBLEMA: Pantalla en blanco en la aplicación >> "%DIST_DIR%\solucionar-problemas.txt"
echo    SOLUCIÓN: Asegúrate de que el backend esté funcionando correctamente. >> "%DIST_DIR%\solucionar-problemas.txt"
echo    - Verifica que no haya errores en la consola del backend >> "%DIST_DIR%\solucionar-problemas.txt"
echo    - Usa iniciar-apuntes-mejorado.bat en lugar de iniciar-apuntes.bat >> "%DIST_DIR%\solucionar-problemas.txt"
echo. >> "%DIST_DIR%\solucionar-problemas.txt"
echo 2. PROBLEMA: Error "db_config.json no encontrado" >> "%DIST_DIR%\solucionar-problemas.txt"
echo    SOLUCIÓN: El archivo db_config.json debe estar tanto en la carpeta principal como en /config/ >> "%DIST_DIR%\solucionar-problemas.txt"
echo    - Copia manualmente config/db_config.json a la carpeta principal >> "%DIST_DIR%\solucionar-problemas.txt"
echo. >> "%DIST_DIR%\solucionar-problemas.txt"
echo 3. PROBLEMA: Botón "Generar Análisis IA" no aparece >> "%DIST_DIR%\solucionar-problemas.txt"
echo    SOLUCIÓN: Reinicia completamente la aplicación >> "%DIST_DIR%\solucionar-problemas.txt"
echo    - Cierra todas las ventanas de la aplicación >> "%DIST_DIR%\solucionar-problemas.txt"
echo    - Ejecuta nuevamente iniciar-apuntes-mejorado.bat >> "%DIST_DIR%\solucionar-problemas.txt"
echo. >> "%DIST_DIR%\solucionar-problemas.txt"
echo 4. PROBLEMA: Errores de Google Vision OCR >> "%DIST_DIR%\solucionar-problemas.txt"
echo    SOLUCIÓN: El OCR funcionará con Tesseract aunque Google Vision no esté disponible >> "%DIST_DIR%\solucionar-problemas.txt"
echo    - Si necesitas específicamente Google Vision, asegúrate que google-vision-key.json está en la carpeta config/ >> "%DIST_DIR%\solucionar-problemas.txt"
echo.
echo Guía de solución de problemas creada

echo.
echo [5/5] Copiando frontend a carpeta principal...
robocopy "%DIST_DIR%\frontend" "%DIST_DIR%" "Apuntes 2.0 - Sistema de Notas con IA.exe" /NFL /NDL /NJH /NJS /nc /ns /np
echo Frontend copiado a carpeta principal

echo.
echo ===== REPARACIÓN COMPLETADA =====
echo.
echo La aplicación ha sido reparada en la carpeta '%DIST_DIR%'
echo Por favor, use 'iniciar-apuntes-mejorado.bat' para iniciar la aplicación
echo.
echo NOTAS IMPORTANTES:
echo 1. El botón "Generar Análisis IA" debería estar disponible ahora
echo 2. Todos los archivos de configuración necesarios han sido creados
echo 3. Si encuentras algún problema, consulta solucionar-problemas.txt
echo.

pause
