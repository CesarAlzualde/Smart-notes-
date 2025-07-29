@echo off
cd /d "%~dp0"
echo Empaquetando backend con estructura de directorios correcta...

cd backend

echo Configurando base de datos persistente...
mkdir "%USERPROFILE%\AppData\Local\Apuntes2.0\database" 2>nul
mkdir "%USERPROFILE%\AppData\Local\Apuntes2.0\uploads" 2>nul

echo { "database_url": "sqlite:///%USERPROFILE:\=/%/AppData/Local/Apuntes2.0/database/app.db" } > config\db_config.json

echo Empaquetando con PyInstaller...
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
  --add-data "templates;templates" ^
  --onefile ^
  --noconfirm ^
  run.py

echo.
echo Si el empaquetado fue exitoso, el ejecutable esta en:
echo %CD%\dist\ApuntesBackend.exe
echo.
pause
