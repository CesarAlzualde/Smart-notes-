@echo off
cd /d "%~dp0"
echo ========================================================
echo    EMPAQUETADO LIMPIO DE BACKEND APUNTES 2.0
echo ========================================================
echo.

cd backend

echo [1/4] Limpiando compilaciones anteriores...
if exist "dist" rmdir /S /Q dist
if exist "build" rmdir /S /Q build
if exist "ApuntesBackend.spec" del /Q ApuntesBackend.spec
echo Limpieza completada.

echo [2/4] Configurando base de datos persistente...
mkdir "%USERPROFILE%\AppData\Local\Apuntes2.0\database" 2>nul
mkdir "%USERPROFILE%\AppData\Local\Apuntes2.0\uploads" 2>nul
mkdir "%USERPROFILE%\AppData\Local\Apuntes2.0\models" 2>nul

echo { "database_url": "sqlite:///%USERPROFILE:\=/%/AppData/Local/Apuntes2.0/database/app.db" } > config\db_config.json

echo [3/4] Empaquetando con PyInstaller...
python -m PyInstaller --name ApuntesBackend ^
  --hidden-import=flask_cors ^
  --hidden-import=pyarrow ^
  --hidden-import=unidecode ^
  --hidden-import=nltk ^
  --hidden-import=transformers ^
  --hidden-import=sentence_transformers ^
  --hidden-import=sqlalchemy ^
  --add-data "config;config" ^
  --add-data "static;static" ^
  --onefile ^
  --noconfirm ^
  run.py

echo [4/4] Creando scripts de inicio...
cd ..
if not exist "dist-apuntes" mkdir dist-apuntes
xcopy /Y backend\dist\ApuntesBackend.exe dist-apuntes\ >nul

echo @echo off > dist-apuntes\iniciar-backend.bat
echo title Backend Apuntes 2.0 >> dist-apuntes\iniciar-backend.bat
echo echo Iniciando backend Flask... >> dist-apuntes\iniciar-backend.bat
echo echo. >> dist-apuntes\iniciar-backend.bat
echo cd /d "%%~dp0" >> dist-apuntes\iniciar-backend.bat
echo start ApuntesBackend.exe >> dist-apuntes\iniciar-backend.bat
echo echo Backend iniciado en http://localhost:5000 >> dist-apuntes\iniciar-backend.bat
echo echo Para verificar, abre: http://localhost:5000/api/health >> dist-apuntes\iniciar-backend.bat
echo echo. >> dist-apuntes\iniciar-backend.bat
echo echo NOTA: Los datos se almacenan en: %USERPROFILE%\AppData\Local\Apuntes2.0 >> dist-apuntes\iniciar-backend.bat

echo.
echo ========================================================
echo    EMPAQUETADO COMPLETADO EXITOSAMENTE
echo ========================================================
echo.
echo El ejecutable esta en: dist-apuntes\ApuntesBackend.exe
echo.
echo Para iniciar el backend, ejecuta: dist-apuntes\iniciar-backend.bat
echo.
echo Los datos se almacenan en: %USERPROFILE%\AppData\Local\Apuntes2.0
echo.
pause
