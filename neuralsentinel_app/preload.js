// preload.js
// Importing necessary modules from Electron 
const { contextBridge, ipcRenderer } = require('electron');

// Attempt to import the optional XLSX library for Excel support in the renderer process
let XLSX = null;
try {
  // Optional library for Excel functionality in renderer
  XLSX = require('xlsx');
} catch (err) {
  // If XLSX is not found, log a warning
  console.warn('Preload: failed to load xlsx, only CSV functionality will work:', err.message);
}

// Exposing the necessary API methods to the renderer process using contextBridge
contextBridge.exposeInMainWorld('electronAPI', {
  // Logging & Authenticator
  log:                 msg    => ipcRenderer.send('log', msg),
  startAuthenticator:  user   => ipcRenderer.send('start-authenticator', user),
  validateUser: (username, password) => ipcRenderer.invoke('validate-user', { username, password }),

  // File handling methods
  getUploadedFiles:    ()     => ipcRenderer.invoke('get-uploaded-files'),
  getPluginMeta:       ()     => ipcRenderer.invoke('get-plugin-meta'),
  uploadAndCalc:       opts   => ipcRenderer.invoke('upload-and-calc', opts),
  deleteFile:          args   => ipcRenderer.invoke('delete-file', args),

  // Path lookup & reading
  getFilePath:         (name, type) => ipcRenderer.invoke('get-file-path', name, type),
  readFileContent:     path        => ipcRenderer.invoke('read-file-content', path),
  getCsvPreview:       path        => ipcRenderer.invoke('get-csv-preview', path),
  getNpyNpzVisualizer: path        => ipcRenderer.invoke('get-npy-npz-visualizer', path),
  getH5Visualizer:     path        => ipcRenderer.invoke('get-h5-visualizer', path),
  getDatasetColumns:   d           => ipcRenderer.invoke('get-dataset-columns', d),

  // Metrics and visualization methods
  computeComboMetrics: args   => ipcRenderer.invoke('compute-combo-metrics', args),
  getTabHtml:          (plg, pay) => ipcRenderer.invoke('get-tab-html', plg, pay),
  getStoredMetrics:    args   => ipcRenderer.invoke('get-stored-metrics', args),

  // Export and saving methods
  showSaveDialog:      opts   => ipcRenderer.invoke('show-save-dialog', opts),
  writeFile:           (filePath, data) =>
                           ipcRenderer.invoke('write-file', { filePath, data }),
  exportMetrics:       args   => ipcRenderer.invoke('export-metrics', args),
  exportCsv:           args   => ipcRenderer.invoke('export-csv', args),

  // Exposing the XLSX library if available
  XLSX
});
