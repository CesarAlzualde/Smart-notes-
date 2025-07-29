const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const axios = require('axios');

class AppLauncher {
    constructor() {
        this.backendProcess = null;
        this.backendReady = false;
        this.backendPort = 5000;
        this.maxRetries = 30; // 30 segundos de espera máxima
    }

    // Iniciar el backend Flask empaquetado
    async startBackend() {
        return new Promise((resolve, reject) => {
            console.log('🚀 Iniciando backend Flask...');
            
            const backendPath = path.join(__dirname, 'backend', 'dist', 'ApuntesBackend', 'ApuntesBackend.exe');
            
            if (!fs.existsSync(backendPath)) {
                return reject(new Error(`Backend no encontrado en: ${backendPath}`));
            }

            this.backendProcess = spawn(backendPath, [], {
                cwd: path.dirname(backendPath),
                stdio: ['pipe', 'pipe', 'pipe']
            });

            this.backendProcess.stdout.on('data', (data) => {
                console.log(`[Backend] ${data.toString()}`);
                if (data.toString().includes('Running on')) {
                    this.backendReady = true;
                }
            });

            this.backendProcess.stderr.on('data', (data) => {
                console.error(`[Backend Error] ${data.toString()}`);
            });

            this.backendProcess.on('close', (code) => {
                console.log(`Backend cerrado con código: ${code}`);
                this.backendReady = false;
            });

            // Esperar a que el backend esté listo
            this.waitForBackend().then(resolve).catch(reject);
        });
    }

    // Verificar si el backend está listo
    async waitForBackend() {
        let retries = 0;
        
        while (retries < this.maxRetries) {
            try {
                await axios.get(`http://localhost:${this.backendPort}/health`, { timeout: 1000 });
                console.log('✅ Backend listo y respondiendo');
                return true;
            } catch (error) {
                retries++;
                console.log(`⏳ Esperando backend... (${retries}/${this.maxRetries})`);
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
        
        throw new Error('Backend no respondió en el tiempo esperado');
    }

    // Iniciar Electron con el frontend
    async startElectron() {
        const { app, BrowserWindow } = require('electron');
        
        await app.whenReady();
        
        const mainWindow = new BrowserWindow({
            width: 1200,
            height: 800,
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                enableRemoteModule: false
            },
            icon: path.join(__dirname, 'assets', 'icon.png') // Opcional: agregar icono
        });

        // Cargar el frontend React (construido)
        const frontendPath = path.join(__dirname, 'auth-frontend', 'build', 'index.html');
        
        if (fs.existsSync(frontendPath)) {
            await mainWindow.loadFile(frontendPath);
        } else {
            // Fallback: cargar desde servidor de desarrollo
            await mainWindow.loadURL('http://localhost:3000');
        }

        // Configurar el menú y eventos
        this.setupElectronEvents(app, mainWindow);

        console.log('✅ Electron iniciado exitosamente');
    }

    // Configurar eventos de Electron
    setupElectronEvents(app, mainWindow) {
        app.on('window-all-closed', () => {
            if (process.platform !== 'darwin') {
                this.shutdown();
            }
        });

        app.on('before-quit', () => {
            this.shutdown();
        });

        mainWindow.on('closed', () => {
            this.shutdown();
        });
    }

    // Cerrar todos los procesos
    shutdown() {
        console.log('🔄 Cerrando aplicación...');
        
        if (this.backendProcess && !this.backendProcess.killed) {
            console.log('🛑 Cerrando backend...');
            this.backendProcess.kill('SIGTERM');
        }
        
        const { app } = require('electron');
        if (app) {
            app.quit();
        }
    }

    // Iniciar aplicación completa
    async launch() {
        try {
            console.log('🌟 Iniciando Apuntes 2.0...');
            
            // 1. Iniciar backend
            await this.startBackend();
            
            // 2. Iniciar Electron
            await this.startElectron();
            
            console.log('🎉 Aplicación iniciada exitosamente');
            
        } catch (error) {
            console.error('❌ Error al iniciar aplicación:', error.message);
            this.shutdown();
            process.exit(1);
        }
    }
}

// Iniciar aplicación si este archivo se ejecuta directamente
if (require.main === module) {
    const launcher = new AppLauncher();
    launcher.launch();
}

module.exports = AppLauncher;
