@echo off
cd /d "%~dp0"
chcp 65001 > nul
title Empaquetado Mejorado de Apuntes 2.0
color 0A

echo =========================================================
echo     EMPAQUETADO MEJORADO DEL BACKEND (APUNTES 2.0)
echo =========================================================
echo.

rem --- Limpieza previa ---
echo [1/5] Limpiando compilaciones anteriores...
if exist "backend\dist" rmdir /S /Q backend\dist
if exist "backend\build" rmdir /S /Q backend\build
if exist "backend\*.spec" del /Q backend\*.spec
echo Limpieza completada.

rem --- Directorios persistentes ---
echo [2/5] Configurando directorios persistentes...
set DATA_DIR=%USERPROFILE%\AppData\Local\Apuntes2.0
mkdir "%DATA_DIR%" 2>nul
mkdir "%DATA_DIR%\database" 2>nul
mkdir "%DATA_DIR%\uploads" 2>nul
mkdir "%DATA_DIR%\models" 2>nul
echo. > "%DATA_DIR%\database\app.db"

rem --- Hooks para PyInstaller ---
echo [3/5] Creando hooks para PyInstaller...
mkdir backend\hooks 2>nul

echo import sys > backend\hooks\hook-tensorflow.py
echo import tensorflow as tf >> backend\hooks\hook-tensorflow.py
echo from PyInstaller.utils.hooks import collect_all >> backend\hooks\hook-tensorflow.py
echo datas, binaries, hiddenimports = collect_all('tensorflow') >> backend\hooks\hook-tensorflow.py

echo import os > backend\hooks\hook-nltk.py
echo import nltk >> backend\hooks\hook-nltk.py
echo from PyInstaller.utils.hooks import collect_data_files >> backend\hooks\hook-nltk.py
echo datas = collect_data_files('nltk') >> backend\hooks\hook-nltk.py
echo nltk_data_path = os.path.join(os.path.expanduser('~'), 'nltk_data') >> backend\hooks\hook-nltk.py
echo if os.path.exists(nltk_data_path): >> backend\hooks\hook-nltk.py
echo     datas += [(nltk_data_path, 'nltk_data')] >> backend\hooks\hook-nltk.py

echo import os > backend\hooks\hook-app.py
echo from PyInstaller.utils.hooks import collect_data_files >> backend\hooks\hook-app.py
echo datas = [] >> backend\hooks\hook-app.py
echo if os.path.exists('app/local_models'): >> backend\hooks\hook-app.py
echo     datas += [('app/local_models', 'app/local_models')] >> backend\hooks\hook-app.py

rem --- Empaquetado con PyInstaller ---
echo [4/5] Empaquetando con PyInstaller...
cd backend
pyinstaller --name ApuntesBackend ^
  --hidden-import=pytesseract ^
  --hidden-import=flask_cors ^
  --hidden-import=transformers ^
  --hidden-import=sentence_transformers ^
  --hidden-import=pyarrow ^
  --hidden-import=unidecode ^
  --hidden-import=nltk ^
  --hidden-import=tensorflow ^
  --hidden-import=numpy ^
  --hidden-import=sqlalchemy ^
  --add-data "config;config" ^
  --add-data "app/static;app/static" ^
  --add-data "app/templates;app/templates" ^
  --additional-hooks-dir=hooks ^
  --noconfirm ^
  --console ^
  run_packaged.py
cd ..

rem --- Preparar distribución final ---
echo [5/5] Preparando distribución final...
if not exist "dist-apuntes" mkdir dist-apuntes
if not exist "dist-apuntes\backend" mkdir dist-apuntes\backend
xcopy /E /Y backend\dist\ApuntesBackend\* dist-apuntes\backend\

echo @echo off > dist-apuntes\iniciar-backend.bat
echo title Backend Apuntes 2.0 >> dist-apuntes\iniciar-backend.bat
echo cd /d "%%~dp0\backend" >> dist-apuntes\iniciar-backend.bat
echo echo Iniciando backend Flask... >> dist-apuntes\iniciar-backend.bat
echo echo. >> dist-apuntes\iniciar-backend.bat
echo start ApuntesBackend.exe >> dist-apuntes\iniciar-backend.bat
echo echo Backend iniciado en http://localhost:5000 >> dist-apuntes\iniciar-backend.bat
echo echo Para verificar, abre: http://localhost:5000/api/health >> dist-apuntes\iniciar-backend.bat
echo echo. >> dist-apuntes\iniciar-backend.bat
echo echo NOTA: Los datos se almacenan en: %USERPROFILE%\AppData\Local\Apuntes2.0 >> dist-apuntes\iniciar-backend.bat

rem --- README con información ---
echo # Apuntes 2.0 - Backend empaquetado > dist-apuntes\README.md
echo >> dist-apuntes\README.md
echo ## Información importante >> dist-apuntes\README.md
echo >> dist-apuntes\README.md
echo - **Base de datos**: %USERPROFILE%\AppData\Local\Apuntes2.0\database\app.db >> dist-apuntes\README.md
echo - **Archivos subidos**: %USERPROFILE%\AppData\Local\Apuntes2.0\uploads >> dist-apuntes\README.md
echo - **Modelos IA**: %USERPROFILE%\AppData\Local\Apuntes2.0\models >> dist-apuntes\README.md
echo >> dist-apuntes\README.md
echo ## Neo4j (opcional) >> dist-apuntes\README.md
echo >> dist-apuntes\README.md
echo Para utilizar mapas conceptuales, debes tener Neo4j instalado y configurado con: >> dist-apuntes\README.md
echo - Usuario: neo4j >> dist-apuntes\README.md
echo - Contraseña: password >> dist-apuntes\README.md
echo >> dist-apuntes\README.md

echo.
echo =========================================================
echo     EMPAQUETADO COMPLETADO EXITOSAMENTE
echo =========================================================
echo.
echo El backend está disponible en: 
echo   %cd%\dist-apuntes\backend
echo.
echo La base de datos y archivos se guardarán en:
echo   %USERPROFILE%\AppData\Local\Apuntes2.0
echo.
echo Para iniciar el backend, ejecuta:
echo   dist-apuntes\iniciar-backend.bat
echo.
pause
