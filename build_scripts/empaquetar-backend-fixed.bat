@echo off
chcp 850
echo ===== EMPAQUETADO MEJORADO DEL BACKEND FLASK =====
echo.

cd backend

echo [1/6] Limpiando compilaciones anteriores...
rmdir /S /Q dist build 2>nul
del /Q *.spec 2>nul
echo Limpieza completada

echo [2/6] Creando hooks para PyInstaller...
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
echo if os.path.exists(nltk_data_path): >> hooks\hook-nltk.py
echo     datas += [(nltk_data_path, 'nltk_data')] >> hooks\hook-nltk.py

echo [3/6] Modificando configuración para entorno de producción...
echo import os > app\__production_config.py
echo os.environ['FLASK_ENV'] = 'production' >> app\__production_config.py
echo os.environ['DATA_DIR'] = r'C:\ProgramData\Apuntes2.0' >> app\__production_config.py
echo # Asegurar que el directorio de datos existe >> app\__production_config.py
echo if not os.path.exists(os.environ['DATA_DIR']): >> app\__production_config.py
echo     try: >> app\__production_config.py
echo         os.makedirs(os.environ['DATA_DIR']) >> app\__production_config.py
echo         os.makedirs(os.path.join(os.environ['DATA_DIR'], 'database')) >> app\__production_config.py
echo         os.makedirs(os.path.join(os.environ['DATA_DIR'], 'uploads')) >> app\__production_config.py
echo     except: >> app\__production_config.py
echo         pass >> app\__production_config.py
echo # Configurar DB para producción >> app\__production_config.py
echo os.environ['DATABASE_URL'] = f"sqlite:///{os.environ['DATA_DIR']}/database/app.db" >> app\__production_config.py

echo # Modificar archivo run.py para cargar configuración de producción
echo import app.__production_config > run_prod.py
echo from run import app >> run_prod.py
echo if __name__ == '__main__': >> run_prod.py
echo     app.run(host='0.0.0.0', port=5000) >> run_prod.py

echo [4/6] Generando archivo .spec y empaquetando...
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
  --add-data "%USERPROFILE%\nltk_data;nltk_data" ^
  --additional-hooks-dir=hooks ^
  --noconfirm ^
  --console ^
  run_prod.py

echo [5/6] Preparando directorio de distribución...
mkdir ..\dist-apuntes 2>nul
mkdir ..\dist-apuntes\backend 2>nul
xcopy /E /Y dist\ApuntesBackend\* ..\dist-apuntes\backend\

echo [6/6] Creando scripts de inicio y configuración...

echo @echo off > ..\dist-apuntes\iniciar-backend.bat
echo echo Iniciando backend Flask... >> ..\dist-apuntes\iniciar-backend.bat
echo echo. >> ..\dist-apuntes\iniciar-backend.bat
echo cd backend >> ..\dist-apuntes\iniciar-backend.bat
echo start ApuntesBackend.exe >> ..\dist-apuntes\iniciar-backend.bat
echo echo Backend iniciado en http://localhost:5000 >> ..\dist-apuntes\iniciar-backend.bat
echo echo Para verificar, abre: http://localhost:5000/api/health >> ..\dist-apuntes\iniciar-backend.bat
echo echo. >> ..\dist-apuntes\iniciar-backend.bat
echo echo Presiona CTRL+C en la ventana del backend para detenerlo >> ..\dist-apuntes\iniciar-backend.bat

echo # Configuración de la base de datos > ..\dist-apuntes\backend\config\db_config.json
echo { >> ..\dist-apuntes\backend\config\db_config.json
echo   "database_url": "sqlite:///C:/ProgramData/Apuntes2.0/database/app.db" >> ..\dist-apuntes\backend\config\db_config.json
echo } >> ..\dist-apuntes\backend\config\db_config.json

echo # Google Vision API Key (placeholder) > ..\dist-apuntes\backend\config\google-vision-key.json
echo {} >> ..\dist-apuntes\backend\config\google-vision-key.json

mkdir C:\ProgramData\Apuntes2.0 2>nul
mkdir C:\ProgramData\Apuntes2.0\database 2>nul
mkdir C:\ProgramData\Apuntes2.0\uploads 2>nul
echo. > C:\ProgramData\Apuntes2.0\database\app.db

cd ..

echo.
echo ===== BACKEND EMPAQUETADO EXITOSAMENTE =====
echo Backend disponible en: dist-apuntes\backend\ApuntesBackend.exe
echo.
echo IMPORTANTE:
echo - La base de datos se almacena en: C:\ProgramData\Apuntes2.0\database\app.db
echo - Las imágenes subidas se guardarán en: C:\ProgramData\Apuntes2.0\uploads
echo.
echo Para iniciar el backend, ejecuta: dist-apuntes\iniciar-backend.bat
echo.
pause
