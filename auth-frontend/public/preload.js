const { contextBridge, ipcRenderer } = require('electron');

// Exponer APIs seguras al renderer process
contextBridge.exposeInMainWorld('electronAPI', {
    // Obtener estado del backend
    getBackendStatus: () => ipcRenderer.invoke('get-backend-status'),
    
    // Versión de la aplicación
    getVersion: () => process.env.npm_package_version || '1.0.0',
    
    // Plataforma
    getPlatform: () => process.platform
});

// Logging seguro
contextBridge.exposeInMainWorld('console', {
    log: (message) => console.log(message),
    error: (message) => console.error(message),
    warn: (message) => console.warn(message)
});
