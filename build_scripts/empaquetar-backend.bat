@echo off
echo ===== EMPAQUETADO DEL BACKEND FLASK =====
echo.

cd backend

echo [1/5] Limpiando compilaciones anteriores...
rmdir /S /Q dist build 2>nul
del /Q *.spec 2>nul
echo Limpieza completada

echo [2/5] Creando hooks para PyInstaller...
mkdir hooks 2>nul

echo import sys > hooks\hook-tensorflow.py
echo import tensorflow as tf >> hooks\hook-tensorflow.py
echo from PyInstaller.utils.hooks import collect_all >> hooks\hook-tensorflow.py
echo datas, binaries, hiddenimports = collect_all('tensorflow') >> hooks\hook-tensorflow.py

echo import os > hooks\hook-nltk.py
echo import nltk >> hooks\hook-nltk.py
echo from PyInstaller.utils.hooks import collect_data_files >> hooks\hook-nltk.py
echo datas = collect_data_files('nltk') >> hooks\hook-nltk.py
echo nltk_data_path = os.path.join(os.path.expanduser('~'), 'nltk_data') >> hooks\hook-nltk.py
echo datas += [(nltk_data_path, 'nltk_data')] >> hooks\hook-nltk.py

echo [3/5] Generando archivo .spec...
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
  --add-data "config;config" ^
  --add-data "app/static;app/static" ^
  --add-data "app/templates;app/templates" ^
  --add-binary "%USERPROFILE%\nltk_data;nltk_data" ^
  --additional-hooks-dir=hooks ^
  --noconfirm ^
  --console ^
  run.py
  
echo [4/5] Asegurando archivos de configuración...
mkdir dist\ApuntesBackend\config 2>nul
copy config\db_config.json dist\ApuntesBackend\config\ /Y
copy config\ai_config.json dist\ApuntesBackend\config\ /Y
echo. > dist\ApuntesBackend\config\google-vision-key.json
echo { "database_url": "sqlite:///instance/app.db" } > dist\ApuntesBackend\db_config.json

echo [5/5] Creando script de prueba...
echo @echo off > dist\ApuntesBackend\probar-backend.bat
echo echo Iniciando backend Flask... >> dist\ApuntesBackend\probar-backend.bat
echo start ApuntesBackend.exe >> dist\ApuntesBackend\probar-backend.bat
echo echo Backend iniciado en http://localhost:5000 >> dist\ApuntesBackend\probar-backend.bat
echo echo Para probar, abre: http://localhost:5000/api/health >> dist\ApuntesBackend\probar-backend.bat

echo.
echo ===== BACKEND EMPAQUETADO EXITOSAMENTE =====
echo Backend disponible en: backend\dist\ApuntesBackend\ApuntesBackend.exe
echo.
echo Puedes probar el backend ejecutando backend\dist\ApuntesBackend\probar-backend.bat
echo.
pause
