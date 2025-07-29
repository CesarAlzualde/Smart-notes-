@echo off
chcp 65001 >nul
title Empaquetado Completo Apuntes 2.0
color 0B

echo ================================================================
echo                  EMPAQUETADO COMPLETO APUNTES 2.0
echo                 Backend (PyInstaller) + Frontend (Electron)
echo ================================================================
echo.

REM Configuración de variables
set BACKEND_DIR=%~dp0backend
set FRONTEND_DIR=%~dp0auth-frontend
set DIST_DIR=%~dp0dist-apuntes
set RESOURCES_DIR=%FRONTEND_DIR%\resources

REM Verificar herramientas necesarias
echo [1/7] Verificando requisitos...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js no está instalado
    echo    Descarga e instala Node.js desde: https://nodejs.org
    pause
    exit /b 1
)

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no está instalado
    echo    Descarga e instala Python desde: https://www.python.org
    pause
    exit /b 1
)

where pip >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Pip no está instalado
    echo    Instala pip con: python -m ensurepip
    pause
    exit /b 1
)

echo ✓ Node.js detectado
echo ✓ Python detectado
echo ✓ Pip detectado

REM Crear directorios necesarios
echo.
echo [2/7] Preparando directorios...
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"
if not exist "%RESOURCES_DIR%" mkdir "%RESOURCES_DIR%"
if not exist "%RESOURCES_DIR%\backend" mkdir "%RESOURCES_DIR%\backend"
echo ✓ Directorios creados

REM Empaquetar el backend con PyInstaller
echo.
echo [3/7] Empaquetando backend con PyInstaller...
cd "%BACKEND_DIR%"

echo  - Limpiando compilaciones anteriores...
rmdir /S /Q dist build 2>nul
del /Q *.spec 2>nul

echo  - Creando archivos de configuración...
if not exist hooks mkdir hooks

REM Crear hook para TensorFlow
echo import sys > hooks\hook-tensorflow.py
echo import tensorflow as tf >> hooks\hook-tensorflow.py
echo from PyInstaller.utils.hooks import collect_all >> hooks\hook-tensorflow.py
echo datas, binaries, hiddenimports = collect_all('tensorflow') >> hooks\hook-tensorflow.py

REM Crear hook para NLTK
echo import os > hooks\hook-nltk.py
echo import nltk >> hooks\hook-nltk.py
echo from PyInstaller.utils.hooks import collect_data_files >> hooks\hook-nltk.py
echo datas = collect_data_files('nltk') >> hooks\hook-nltk.py
echo nltk_data_path = os.path.join(os.path.expanduser('~'), 'nltk_data') >> hooks\hook-nltk.py
echo datas += [(nltk_data_path, 'nltk_data')] >> hooks\hook-nltk.py

echo  - Ejecutando PyInstaller...
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

echo  - Creando archivos de configuración...
mkdir dist\ApuntesBackend\config 2>nul
copy config\db_config.json dist\ApuntesBackend\config\ /Y
copy config\ai_config.json dist\ApuntesBackend\config\ /Y
echo { "type": "service_account" } > dist\ApuntesBackend\config\google-vision-key.json
echo { "database_url": "sqlite:///instance/app.db" } > dist\ApuntesBackend\db_config.json
echo { "database_url": "sqlite:///instance/app.db" } > dist\ApuntesBackend\config\db_config.json

echo ✓ Backend empaquetado correctamente

REM Copiar backend al directorio de recursos de Electron
echo.
echo [4/7] Copiando backend a recursos de Electron...
xcopy /E /I /Y "%BACKEND_DIR%\dist\ApuntesBackend" "%RESOURCES_DIR%\backend"
echo ✓ Backend copiado a recursos de Electron

REM Configurar y empaquetar el frontend
echo.
echo [5/7] Configurando frontend Electron...
cd "%FRONTEND_DIR%"

echo  - Actualizando package.json para incluir recursos...
(
    echo {
    echo   "name": "apuntes2-desktop",
    echo   "version": "1.0.0",
    echo   "private": true,
    echo   "type": "module",
    echo   "scripts": {
    echo     "dev": "vite",
    echo     "build": "tsc && vite build",
    echo     "preview": "vite preview",
    echo     "electron": "electron .",
    echo     "start": "electron .",
    echo     "dist": "electron-builder"
    echo   },
    echo   "main": "dist/electron.js",
    echo   "build": {
    echo     "appId": "com.apuntes2.app",
    echo     "productName": "Apuntes 2.0",
    echo     "directories": {
    echo       "output": "dist-electron"
    echo     },
    echo     "files": [
    echo       "dist/**/*"
    echo     ],
    echo     "extraResources": [
    echo       {
    echo         "from": "resources/backend",
    echo         "to": "backend",
    echo         "filter": ["**/*"]
    echo       }
    echo     ],
    echo     "win": {
    echo       "target": ["nsis"],
    echo       "icon": "assets/icon.ico"
    echo     },
    echo     "nsis": {
    echo       "oneClick": false,
    echo       "perMachine": false,
    echo       "allowToChangeInstallationDirectory": true,
    echo       "createDesktopShortcut": true,
    echo       "createStartMenuShortcut": true
    echo     }
    echo   },
    echo   "dependencies": {
    echo     "electron-is-dev": "^2.0.0"
    echo   },
    echo   "devDependencies": {}
    echo }
) > package.json.new
move /Y package.json.new package.json

echo  - Instalando dependencias...
call npm install --save-dev electron electron-builder@^24.0.0
call npm install --save electron-is-dev
echo ✓ Dependencias instaladas

REM Configurar archivo electron.js optimizado
echo.
echo [6/7] Construyendo aplicación Electron...
echo  - Compilando frontend React...
call npm run build

echo  - Preparando archivo electron.js...
mkdir dist 2>nul
(
    echo // electron.js - Archivo principal de Electron
    echo import { app, BrowserWindow, ipcMain } from 'electron';
    echo import path from 'path';
    echo import { fileURLToPath } from 'url';
    echo import { dirname } from 'path';
    echo import { spawn } from 'child_process';
    echo import fs from 'fs';
    echo import isDev from 'electron-is-dev';
    echo.
    echo // ES modules compatibility
    echo const __filename = fileURLToPath^(import.meta.url^);
    echo const __dirname = dirname^(__filename^);
    echo.
    echo let mainWindow;
    echo let backendProcess = null;
    echo.
    echo // Función para crear la ventana principal
    echo function createWindow^(^) {
    echo   mainWindow = new BrowserWindow^({
    echo     width: 1400,
    echo     height: 900,
    echo     webPreferences: {
    echo       nodeIntegration: true,
    echo       contextIsolation: false
    echo     },
    echo     show: false
    echo   }^);
    echo.
    echo   // Cargar la aplicación React
    echo   const startUrl = isDev
    echo     ? 'http://localhost:5173'
    echo     : `file://${path.join^(__dirname, 'index.html')}`;
    echo.
    echo   console.log^(`Cargando URL: ${startUrl}`^);
    echo   mainWindow.loadURL^(startUrl^);
    echo.
    echo   // Mostrar ventana cuando esté lista
    echo   mainWindow.once^('ready-to-show', ^(^) =^> {
    echo     mainWindow.show^(^);
    echo     if ^(isDev^) {
    echo       mainWindow.webContents.openDevTools^(^);
    echo     }
    echo   }^);
    echo.
    echo   mainWindow.on^('closed', ^(^) =^> {
    echo     mainWindow = null;
    echo   }^);
    echo }
    echo.
    echo // Función para iniciar el backend PyInstaller
    echo function startBackend^(^) {
    echo   console.log^('🚀 Iniciando backend PyInstaller...'^);
    echo.
    echo   // Determinar la ruta del ejecutable del backend
    echo   const backendPath = isDev
    echo     ? path.join^(process.cwd^(^), '../backend/dist/ApuntesBackend/ApuntesBackend.exe'^)
    echo     : path.join^(process.resourcesPath, 'backend/ApuntesBackend.exe'^);
    echo.
    echo   console.log^(`📁 Ruta del backend: ${backendPath}`^);
    echo.
    echo   try {
    echo     // Asegurar que db_config.json existe en la ubicación correcta
    echo     const configDir = path.dirname^(backendPath^);
    echo     const dbConfigPath = path.join^(configDir, 'db_config.json'^);
    echo.
    echo     if ^(!fs.existsSync^(dbConfigPath^)^) {
    echo       console.log^('⚠️ Creando db_config.json...'^);
    echo       fs.writeFileSync^(
    echo         dbConfigPath,
    echo         JSON.stringify^({ database_url: "sqlite:///instance/app.db" }^),
    echo         'utf8'
    echo       ^);
    echo     }
    echo.
    echo     // Iniciar el proceso del backend
    echo     backendProcess = spawn^(backendPath, [], {
    echo       windowsHide: true,
    echo       stdio: 'pipe',
    echo       cwd: configDir  // Establecer directorio de trabajo
    echo     }^);
    echo.
    echo     // Manejar salida del backend
    echo     backendProcess.stdout.on^('data', ^(data^) =^> {
    echo       console.log^(`🔄 Backend: ${data.toString^(^)}`^);
    echo     }^);
    echo.
    echo     backendProcess.stderr.on^('data', ^(data^) =^> {
    echo       console.error^(`⚠️ Backend Error: ${data.toString^(^)}`^);
    echo     }^);
    echo.
    echo     backendProcess.on^('close', ^(code^) =^> {
    echo       console.log^(`⛔ Backend cerrado con código: ${code}`^);
    echo       backendProcess = null;
    echo     }^);
    echo.
    echo     // Esperar 5 segundos para asegurarse de que el backend inicie completamente
    echo     setTimeout^(^(^) =^> {
    echo       console.log^('✅ Backend debería estar iniciado ahora'^);
    echo     }, 5000^);
    echo.
    echo     return true;
    echo   } catch ^(error^) {
    echo     console.error^('❌ Error al iniciar el backend:', error^);
    echo     return false;
    echo   }
    echo }
    echo.
    echo // Función para verificar si el backend ya está corriendo
    echo function checkBackend^(^) {
    echo   return new Promise^(^(resolve^) =^> {
    echo     console.log^('🔍 Verificando backend existente...'^);
    echo.
    echo     // Hacer una petición simple para verificar si el backend está activo
    echo     fetch^('http://localhost:5000/api/health'^)
    echo       .then^(response =^> {
    echo         if ^(response.ok^) {
    echo           console.log^('✅ Backend ya está corriendo - usando backend externo'^);
    echo           resolve^(true^);
    echo         } else {
    echo           console.log^('⚠️ Backend no responde correctamente - iniciando backend interno'^);
    echo           const started = startBackend^(^);
    echo           setTimeout^(^(^) =^> resolve^(started^), 7000^);
    echo         }
    echo       }^)
    echo       .catch^(^(^) =^> {
    echo         console.log^('⚠️ Backend no disponible - iniciando backend interno'^);
    echo         const started = startBackend^(^);
    echo         setTimeout^(^(^) =^> resolve^(started^), 7000^);
    echo       }^);
    echo   }^);
    echo }
    echo.
    echo // Eventos de la aplicación
    echo app.whenReady^(^).then^(async ^(^) =^> {
    echo   await checkBackend^(^);
    echo.
    echo   // Crear ventana después de iniciar backend
    echo   createWindow^(^);
    echo.
    echo   app.on^('activate', ^(^) =^> {
    echo     if ^(BrowserWindow.getAllWindows^(^).length === 0^) {
    echo       createWindow^(^);
    echo     }
    echo   }^);
    echo }^);
    echo.
    echo app.on^('window-all-closed', ^(^) =^> {
    echo   if ^(process.platform !== 'darwin'^) {
    echo     app.quit^(^);
    echo   }
    echo }^);
    echo.
    echo app.on^('before-quit', ^(^) =^> {
    echo   // Cerrar el backend si está corriendo
    echo   if ^(backendProcess^) {
    echo     console.log^('🛑 Cerrando backend PyInstaller...'^);
    echo     try {
    echo       process.kill^(backendProcess.pid^);
    echo     } catch ^(error^) {
    echo       console.error^('Error al cerrar el backend:', error^);
    echo     }
    echo   }
    echo }^);
    echo.
    echo // IPC para comunicación con el renderer
    echo ipcMain.handle^('get-backend-status', async ^(^) =^> {
    echo   try {
    echo     const response = await fetch^('http://localhost:5000/api/health'^);
    echo     return response.ok ? 'running' : 'stopped';
    echo   } catch {
    echo     return 'stopped';
    echo   }
    echo }^);
) > dist\electron.js

echo ✓ Frontend configurado y construido

REM Crear instalador con electron-builder
echo.
echo [7/7] Creando instalador...
call npm run dist

REM Copiar instalador al directorio de distribución principal
copy "%FRONTEND_DIR%\dist-electron\*.exe" "%DIST_DIR%\" /Y

cd "%~dp0"

REM Crear script de configuración para la primera ejecución
echo.
echo [+] Creando scripts y documentación adicionales...
(
    echo @echo off
    echo echo ===== PRIMERA EJECUCIÓN - CONFIGURACIÓN APUNTES 2.0 =====
    echo echo.
    echo echo Configurando archivos necesarios...
    echo.
    echo REM Crear config para Neo4j
    echo echo { "database_url": "sqlite:///instance/app.db" } ^> db_config.json
    echo echo.
    echo echo Configuración completa
    echo echo.
    echo echo Para iniciar la aplicación, ejecuta Apuntes2.exe
    echo echo.
    echo echo NOTA: Para utilizar mapas conceptuales, debes iniciar Neo4j manualmente
    echo echo.
    echo pause
) > "%DIST_DIR%\configurar-primera-ejecucion.bat"

REM Crear documentación con instrucciones
(
    echo # Apuntes 2.0 - Guía de Usuario
    echo.
    echo ## Instalación
    echo.
    echo 1. Ejecuta el instalador y sigue las instrucciones en pantalla
    echo 2. Al finalizar, se creará un acceso directo en el escritorio y menú inicio
    echo.
    echo ## Primer inicio
    echo.
    echo Antes de usar la aplicación por primera vez:
    echo.
    echo 1. Ejecuta `configurar-primera-ejecucion.bat` en la carpeta de instalación
    echo 2. Inicia la aplicación desde el acceso directo creado
    echo.
    echo ## Funcionalidades
    echo.
    echo ### OCR y Reconocimiento de Texto
    echo - La aplicación utiliza Tesseract OCR para reconocer texto en imágenes
    echo - La función Google Vision está desactivada por defecto, requiere configuración adicional
    echo.
    echo ### Análisis de Texto con IA
    echo - Utiliza el botón "Generar Análisis IA" para resumir y corregir textos
    echo - Modelos utilizados:
    echo   - Summarization: josmunpen/mt5-small-spanish-summarization
    echo   - Grammar correction: JasperLS/T5-Grammar-Checker-Spanish
    echo.
    echo ### Mapas Conceptuales
    echo - **Requiere Neo4j**: Para usar mapas conceptuales, debes instalar y ejecutar Neo4j manualmente
    echo - Descarga Neo4j Desktop desde [neo4j.com/download](https://neo4j.com/download/)
    echo - Crea una base de datos con usuario "neo4j" y contraseña "password"
    echo.
    echo ## Solución de Problemas
    echo.
    echo ### Pantalla en blanco
    echo - Cierra la aplicación y reiníciala
    echo - Verifica que no haya otra instancia ejecutándose
    echo.
    echo ### Error de db_config.json
    echo - Ejecuta `configurar-primera-ejecucion.bat` en la carpeta de instalación
    echo.
    echo ### Advertencias de Neo4j
    echo - Son normales si no tienes Neo4j ejecutándose
    echo - No afectan a las demás funcionalidades de la aplicación
) > "%DIST_DIR%\LEEME.md"

REM Finalización
echo.
echo ================================================================
echo              PROCESO DE EMPAQUETADO COMPLETADO
echo ================================================================
echo.
echo INSTALADOR DISPONIBLE EN:
echo    %DIST_DIR%
echo.
echo INSTRUCCIONES DE USO:
echo    1. Ejecutar el instalador
echo    2. Al iniciar la aplicación, usar "configurar-primera-ejecucion.bat"
echo    3. Seguir las instrucciones del archivo LEEME.md
echo.
echo NOTAS IMPORTANTES:
echo    - El OCR utilizará Tesseract por defecto
echo    - Para usar los mapas conceptuales, se requiere Neo4j
echo.
pause
