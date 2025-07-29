@echo off
cd /d "%~dp0"
echo ========================================================
echo    EMPAQUETADO FINAL CON DEPENDENCIAS COMPLETAS
echo ========================================================
echo.

cd backend

echo [1/5] Limpiando compilaciones anteriores...
if exist "dist" rmdir /S /Q dist
if exist "build" rmdir /S /Q build
if exist "ApuntesBackend.spec" del /Q ApuntesBackend.spec
echo Limpieza completada.

echo [2/5] Configurando base de datos persistente...
mkdir "%USERPROFILE%\AppData\Local\Apuntes2.0\database" 2>nul
mkdir "%USERPROFILE%\AppData\Local\Apuntes2.0\uploads" 2>nul
mkdir "%USERPROFILE%\AppData\Local\Apuntes2.0\models" 2>nul

echo { "database_url": "sqlite:///%USERPROFILE:\=/%/AppData/Local/Apuntes2.0/database/app.db" } > config\db_config.json

echo [3/5] Creando hooks personalizados para dependencias...

echo Creando hook para cmudict...
if not exist "hooks" mkdir hooks
echo from PyInstaller.utils.hooks import collect_all > hooks\hook-cmudict.py
echo datas, binaries, hiddenimports = collect_all('cmudict') >> hooks\hook-cmudict.py

echo Creando hook para textstat...
echo from PyInstaller.utils.hooks import collect_all > hooks\hook-textstat.py
echo datas, binaries, hiddenimports = collect_all('textstat') >> hooks\hook-textstat.py

echo [4/5] Empaquetando con PyInstaller y hooks adicionales...
python -m PyInstaller --name ApuntesBackend ^
  --clean ^
  --hidden-import=flask_cors ^
  --hidden-import=pyarrow ^
  --hidden-import=unidecode ^
  --hidden-import=nltk ^
  --hidden-import=transformers ^
  --hidden-import=sentence_transformers ^
  --hidden-import=sqlalchemy ^
  --hidden-import=cmudict ^
  --hidden-import=textstat ^
  --add-data "config;config" ^
  --add-data "config\google-vision-key.json;config" ^
  --add-data "static;static" ^
  --additional-hooks-dir=hooks ^
  --onefile ^
  --noconfirm ^
  run.py

echo [5/5] Creando scripts de inicio y verificando...
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

echo @echo off > dist-apuntes\diagnostico.bat
echo echo =============================================== >> dist-apuntes\diagnostico.bat
echo echo    DIAGNOSTICO DE BACKEND APUNTES 2.0 >> dist-apuntes\diagnostico.bat
echo echo =============================================== >> dist-apuntes\diagnostico.bat
echo echo. >> dist-apuntes\diagnostico.bat
echo echo Iniciando backend con modo de diagnostico... >> dist-apuntes\diagnostico.bat
echo echo. >> dist-apuntes\diagnostico.bat
echo echo La ventana permanecera abierta para mostrar errores >> dist-apuntes\diagnostico.bat
echo echo. >> dist-apuntes\diagnostico.bat
echo cd /d "%%~dp0" >> dist-apuntes\diagnostico.bat
echo ApuntesBackend.exe >> dist-apuntes\diagnostico.bat
echo echo. >> dist-apuntes\diagnostico.bat
echo echo =============================================== >> dist-apuntes\diagnostico.bat
echo echo    FIN DE LA EJECUCION >> dist-apuntes\diagnostico.bat
echo echo =============================================== >> dist-apuntes\diagnostico.bat
echo echo. >> dist-apuntes\diagnostico.bat
echo echo Si el programa termino inmediatamente, revise los errores arriba. >> dist-apuntes\diagnostico.bat
echo echo. >> dist-apuntes\diagnostico.bat
echo pause >> dist-apuntes\diagnostico.bat

echo.
echo ========================================================
echo    EMPAQUETADO COMPLETADO EXITOSAMENTE
echo ========================================================
echo.
echo El ejecutable esta en: dist-apuntes\ApuntesBackend.exe
echo.
echo Para iniciar el backend, ejecuta: dist-apuntes\iniciar-backend.bat
echo Para diagnosticar problemas: dist-apuntes\diagnostico.bat
echo.
echo Los datos se almacenan en: %USERPROFILE%\AppData\Local\Apuntes2.0
echo.
pause
