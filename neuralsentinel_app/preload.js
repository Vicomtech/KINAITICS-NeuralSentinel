const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer process
contextBridge.exposeInMainWorld('electronAPI', {
    getBackendUrl: () => ipcRenderer.invoke('get-backend-url'),
    getAppVersion: () => ipcRenderer.invoke('app-version')
});
