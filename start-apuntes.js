#!/usr/bin/env node

/**
 * Apuntes 2.0 - Launcher Node.js
 * Inicia backend PyInstaller + Frontend Vite + Electron
 */

import { spawn, exec } from 'child_process';
import { join, resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

// ES modules compatibility
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Configuración
const config = {
    backendPath: resolve(__dirname, 'backend/dist/ApuntesBackend/ApuntesBackend.exe'),
    frontendDir: resolve(__dirname, 'auth-frontend'),
    backendUrl: 'http://localhost:5000',
    frontendUrl: 'http://localhost:5174',
    waitTime: 5000
};

let backendProcess = null;
let frontendProcess = null;
let electronProcess = null;

// Función para logging con colores
function log(level, message) {
    const timestamp = new Date().toLocaleTimeString();
    const colors = {
        info: '\x1b[36m',    // Cyan
        success: '\x1b[32m', // Green
        warning: '\x1b[33m', // Yellow
        error: '\x1b[31m',   // Red
        reset: '\x1b[0m'     // Reset
    };
    
    console.log(`${colors[level]}[${timestamp}] ${message}${colors.reset}`);
}

// Función para verificar si un puerto está disponible
function checkUrl(url) {
    return new Promise((resolve) => {
        exec(`curl -s ${url} --max-time 2`, (error) => {
            resolve(!error);
        });
    });
}

// Función para iniciar el backend
function startBackend() {
    return new Promise((resolve, reject) => {
        log('info', '🚀 Iniciando backend Flask...');
        
        if (!fs.existsSync(config.backendPath)) {
            return reject(`❌ Backend no encontrado: ${config.backendPath}`);
        }
        
        backendProcess = spawn(config.backendPath, [], {
            cwd: dirname(config.backendPath),
            stdio: 'pipe'
        });
        
        backendProcess.stdout.on('data', (data) => {
            log('info', `Backend: ${data.toString().trim()}`);
        });
        
        backendProcess.stderr.on('data', (data) => {
            log('warning', `Backend stderr: ${data.toString().trim()}`);
        });
        
        backendProcess.on('error', (err) => {
            log('error', `❌ Error backend: ${err.message}`);
            reject(err);
        });
        
        backendProcess.on('close', (code) => {
            log('info', `Backend cerrado con código: ${code}`);
            backendProcess = null;
        });
        
        // Esperar a que el backend responda
        setTimeout(async () => {
            const isReady = await checkUrl(config.backendUrl);
            if (isReady) {
                log('success', '✅ Backend listo y respondiendo');
                resolve();
            } else {
                log('warning', '⚠️ Backend podría no estar listo, continuando...');
                resolve(); // Continuar de todos modos
            }
        }, config.waitTime);
    });
}

// Función para iniciar el frontend
function startFrontend() {
    return new Promise((resolve, reject) => {
        log('info', '🌐 Iniciando frontend Vite...');
        
        frontendProcess = spawn('npm', ['run', 'dev'], {
            cwd: config.frontendDir,
            stdio: 'pipe',
            shell: true
        });
        
        frontendProcess.stdout.on('data', (data) => {
            const output = data.toString();
            if (output.includes('Local:') || output.includes('5174')) {
                log('success', '✅ Frontend listo en puerto 5174');
                resolve();
            }
            log('info', `Frontend: ${output.trim()}`);
        });
        
        frontendProcess.stderr.on('data', (data) => {
            log('warning', `Frontend stderr: ${data.toString().trim()}`);
        });
        
        frontendProcess.on('error', (err) => {
            log('error', `❌ Error frontend: ${err.message}`);
            reject(err);
        });
        
        frontendProcess.on('close', (code) => {
            log('info', `Frontend cerrado con código: ${code}`);
            frontendProcess = null;
        });
        
        // Timeout para resolverse
        setTimeout(() => {
            log('info', '⏱️ Continuando con Electron...');
            resolve();
        }, 8000);
    });
}

// Función para iniciar Electron
function startElectron() {
    return new Promise((resolve, reject) => {
        log('info', '🖥️ Iniciando Electron...');
        
        electronProcess = spawn('npm', ['run', 'electron'], {
            cwd: config.frontendDir,
            stdio: 'inherit',
            shell: true
        });
        
        electronProcess.on('error', (err) => {
            log('error', `❌ Error Electron: ${err.message}`);
            reject(err);
        });
        
        electronProcess.on('close', (code) => {
            log('info', `Electron cerrado con código: ${code}`);
            electronProcess = null;
            // Cuando Electron se cierra, cerrar todo
            cleanup();
        });
        
        resolve();
    });
}

// Función de limpieza
function cleanup() {
    log('info', '🧹 Cerrando aplicación...');
    
    if (electronProcess && !electronProcess.killed) {
        electronProcess.kill('SIGTERM');
    }
    
    if (frontendProcess && !frontendProcess.killed) {
        frontendProcess.kill('SIGTERM');
    }
    
    if (backendProcess && !backendProcess.killed) {
        backendProcess.kill('SIGTERM');
    }
    
    setTimeout(() => {
        log('success', '✅ Aplicación cerrada exitosamente');
        process.exit(0);
    }, 2000);
}

// Manejo de señales de salida
['SIGINT', 'SIGTERM', 'SIGHUP'].forEach(signal => {
    process.on(signal, cleanup);
});

// Función principal
async function main() {
    try {
        log('info', '🎯 Iniciando Apuntes 2.0...');
        
        // Paso 1: Backend
        await startBackend();
        
        // Paso 2: Frontend
        await startFrontend();
        
        // Paso 3: Electron
        await startElectron();
        
        log('success', '🎉 Apuntes 2.0 iniciado exitosamente!');
        
    } catch (error) {
        log('error', `❌ Error: ${error}`);
        cleanup();
        process.exit(1);
    }
}

// Iniciar aplicación
main();
