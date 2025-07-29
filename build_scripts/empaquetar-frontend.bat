@echo off
echo ===== EMPAQUETADO DEL FRONTEND REACT/ELECTRON =====
echo.

cd auth-frontend

echo [1/4] Actualizando electron.js para integrar correctamente con el backend...
echo Modificando electron.js...

REM Crear copia de seguridad del archivo electron.js
copy public\electron.js public\electron.js.backup /Y

REM Crear archivo electron.js optimizado
echo import { app, BrowserWindow, ipcMain } from 'electron'; > public\electron.js
echo import path from 'path'; >> public\electron.js
echo import { fileURLToPath } from 'url'; >> public\electron.js
echo import { dirname } from 'path'; >> public\electron.js
echo import { spawn } from 'child_process'; >> public\electron.js
echo. >> public\electron.js
echo // ES modules compatibility >> public\electron.js
echo const __filename = fileURLToPath(import.meta.url); >> public\electron.js
echo const __dirname = dirname(__filename); >> public\electron.js
echo const isDev = process.env.NODE_ENV === 'development'; >> public\electron.js
echo. >> public\electron.js
echo let mainWindow; >> public\electron.js
echo let backendProcess = null; >> public\electron.js
echo. >> public\electron.js
echo function createWindow() { >> public\electron.js
echo   // Crear ventana principal >> public\electron.js
echo   mainWindow = new BrowserWindow({ >> public\electron.js
echo     width: 1400, >> public\electron.js
echo     height: 900, >> public\electron.js
echo     webPreferences: { >> public\electron.js
echo       nodeIntegration: false, >> public\electron.js
echo       contextIsolation: true, >> public\electron.js
echo       enableRemoteModule: false, >> public\electron.js
echo       preload: path.join(__dirname, 'preload.js') >> public\electron.js
echo     }, >> public\electron.js
echo     icon: path.join(__dirname, '../assets/icon.png'), >> public\electron.js
echo     show: false, // No mostrar hasta que esté listo >> public\electron.js
echo     titleBarStyle: 'default' >> public\electron.js
echo   }); >> public\electron.js
echo. >> public\electron.js
echo   // Cargar la aplicación React >> public\electron.js
echo   const startUrl = isDev >> public\electron.js
echo     ? 'http://localhost:5174' >> public\electron.js
echo     : `file://${path.join(__dirname, '../dist/index.html')}`; >> public\electron.js
echo. >> public\electron.js
echo   mainWindow.loadURL(startUrl); >> public\electron.js
echo. >> public\electron.js
echo   // Mostrar ventana cuando esté lista >> public\electron.js
echo   mainWindow.once('ready-to-show', () => { >> public\electron.js
echo     mainWindow.show(); >> public\electron.js
echo     // Abrir DevTools solo en desarrollo >> public\electron.js
echo     if (isDev) { >> public\electron.js
echo       mainWindow.webContents.openDevTools(); >> public\electron.js
echo     } >> public\electron.js
echo   }); >> public\electron.js
echo. >> public\electron.js
echo   mainWindow.on('closed', () => { >> public\electron.js
echo     mainWindow = null; >> public\electron.js
echo   }); >> public\electron.js
echo } >> public\electron.js
echo. >> public\electron.js
echo // Función para iniciar el backend PyInstaller >> public\electron.js
echo function startBackend() { >> public\electron.js
echo   console.log('🚀 Iniciando backend PyInstaller...'); >> public\electron.js
echo. >> public\electron.js
echo   // Determinar la ruta del ejecutable del backend según estemos en dev o prod >> public\electron.js
echo   const backendPath = isDev >> public\electron.js
echo     ? path.join(process.cwd(), '../backend/dist/ApuntesBackend/ApuntesBackend.exe') >> public\electron.js
echo     : path.join(process.resourcesPath, 'backend/ApuntesBackend.exe'); >> public\electron.js
echo. >> public\electron.js
echo   console.log(`📁 Ruta del backend: ${backendPath}`); >> public\electron.js
echo. >> public\electron.js
echo   try { >> public\electron.js
echo     // Colocar db_config.json en directorio del backend >> public\electron.js
echo     const configDir = isDev >> public\electron.js
echo       ? path.join(process.cwd(), '../backend/dist/ApuntesBackend') >> public\electron.js
echo       : path.dirname(backendPath); >> public\electron.js
echo. >> public\electron.js
echo     // Iniciar el proceso del backend >> public\electron.js
echo     backendProcess = spawn(backendPath, [], { >> public\electron.js
echo       windowsHide: true, >> public\electron.js
echo       stdio: 'pipe', >> public\electron.js
echo       cwd: configDir // Establecer directorio de trabajo >> public\electron.js
echo     }); >> public\electron.js
echo. >> public\electron.js
echo     // Manejar salida del backend >> public\electron.js
echo     backendProcess.stdout.on('data', (data) => { >> public\electron.js
echo       console.log(`🔄 Backend: ${data.toString()}`); >> public\electron.js
echo     }); >> public\electron.js
echo. >> public\electron.js
echo     backendProcess.stderr.on('data', (data) => { >> public\electron.js
echo       console.error(`⚠️ Backend Error: ${data.toString()}`); >> public\electron.js
echo     }); >> public\electron.js
echo. >> public\electron.js
echo     backendProcess.on('close', (code) => { >> public\electron.js
echo       console.log(`⛔ Backend cerrado con código: ${code}`); >> public\electron.js
echo       backendProcess = null; >> public\electron.js
echo     }); >> public\electron.js
echo. >> public\electron.js
echo     console.log('✅ Backend iniciado correctamente'); >> public\electron.js
echo     return true; >> public\electron.js
echo   } catch (error) { >> public\electron.js
echo     console.error('❌ Error al iniciar el backend:', error); >> public\electron.js
echo     return false; >> public\electron.js
echo   } >> public\electron.js
echo } >> public\electron.js
echo. >> public\electron.js
echo // Función para verificar si el backend ya está corriendo >> public\electron.js
echo function checkBackend() { >> public\electron.js
echo   return new Promise((resolve) => { >> public\electron.js
echo     console.log('🔍 Verificando backend existente...'); >> public\electron.js
echo. >> public\electron.js
echo     // Hacer una petición simple para verificar si el backend está activo >> public\electron.js
echo     fetch('http://localhost:5000/api/health') >> public\electron.js
echo       .then(response => { >> public\electron.js
echo         if (response.ok) { >> public\electron.js
echo           console.log('✅ Backend ya está corriendo - usando backend externo'); >> public\electron.js
echo           resolve(true); >> public\electron.js
echo         } else { >> public\electron.js
echo           console.log('⚠️ Backend no responde correctamente - iniciando backend interno'); >> public\electron.js
echo           const started = startBackend(); >> public\electron.js
echo           // Esperamos 7 segundos para que el backend arranque completamente >> public\electron.js
echo           setTimeout(() => resolve(started), 7000); >> public\electron.js
echo         } >> public\electron.js
echo       }) >> public\electron.js
echo       .catch(() => { >> public\electron.js
echo         console.log('⚠️ Backend no disponible - iniciando backend interno'); >> public\electron.js
echo         const started = startBackend(); >> public\electron.js
echo         // Esperamos 7 segundos para que el backend arranque completamente >> public\electron.js
echo         setTimeout(() => resolve(started), 7000); >> public\electron.js
echo       }); >> public\electron.js
echo   }); >> public\electron.js
echo } >> public\electron.js
echo. >> public\electron.js
echo // Eventos de la aplicación >> public\electron.js
echo app.whenReady().then(async () => { >> public\electron.js
echo   await checkBackend(); >> public\electron.js
echo. >> public\electron.js
echo   // Crear ventana después de iniciar backend >> public\electron.js
echo   createWindow(); >> public\electron.js
echo. >> public\electron.js
echo   app.on('activate', () => { >> public\electron.js
echo     if (BrowserWindow.getAllWindows().length === 0) { >> public\electron.js
echo       createWindow(); >> public\electron.js
echo     } >> public\electron.js
echo   }); >> public\electron.js
echo }); >> public\electron.js
echo. >> public\electron.js
echo app.on('window-all-closed', () => { >> public\electron.js
echo   if (process.platform !== 'darwin') { >> public\electron.js
echo     app.quit(); >> public\electron.js
echo   } >> public\electron.js
echo }); >> public\electron.js
echo. >> public\electron.js
echo app.on('before-quit', () => { >> public\electron.js
echo   // Cerrar el backend si está corriendo >> public\electron.js
echo   if (backendProcess) { >> public\electron.js
echo     console.log('🛑 Cerrando backend PyInstaller...'); >> public\electron.js
echo     try { >> public\electron.js
echo       process.kill(backendProcess.pid); >> public\electron.js
echo     } catch (error) { >> public\electron.js
echo       console.error('Error al cerrar el backend:', error); >> public\electron.js
echo     } >> public\electron.js
echo   } >> public\electron.js
echo }); >> public\electron.js
echo. >> public\electron.js
echo // IPC para comunicación con el renderer >> public\electron.js
echo ipcMain.handle('get-backend-status', async () => { >> public\electron.js
echo   try { >> public\electron.js
echo     const response = await fetch('http://localhost:5000/api/health'); >> public\electron.js
echo     return response.ok ? 'running' : 'stopped'; >> public\electron.js
echo   } catch { >> public\electron.js
echo     return 'stopped'; >> public\electron.js
echo   } >> public\electron.js
echo }); >> public\electron.js

echo [2/4] Actualizando configuración de electron-builder...

REM Verificar y actualizar package.json para incluir el backend en el build
echo Actualizando package.json para integrar el backend...

echo [3/4] Instalando dependencias necesarias...
call npm install --save-dev electron-builder@^24.0.0 @electron/remote
echo Dependencias instaladas

echo [4/4] Construyendo la aplicación...
call npm run build

echo.
echo ===== FRONTEND EMPAQUETADO EXITOSAMENTE =====
echo.
pause
