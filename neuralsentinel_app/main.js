const { app, BrowserWindow, ipcMain, dialog, session, shell, protocol } = require('electron');
const path = require('path');
const fs = require('fs');
const fsp = fs.promises;
const { spawn } = require('child_process');
const XLSX = require('xlsx');
const yaml = require('js-yaml');
const { PythonShell } = require('python-shell');
const { URL } = require('url');

const bcrypt = require('bcryptjs');


// Carga del módulo que vive DENTRO del ASAR
const { getUserByUsername } = require(
  path.join(__dirname, 'python_backend', 'userDatabase', 'userDatabase.js')
);

process.on('uncaughtException', (err) => {
  console.error('UNCAUGHT EXCEPTION:', err);
});



// --------------------Utility functions--------------------
/**
 * Escapes HTML special characters to prevent XSS attacks
 * @param {string} str - Input string to escape
 * @returns {string} Escaped HTML string
 */
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// Register custom protocol before app ready
protocol.registerSchemesAsPrivileged([{
  scheme: 'app',
  privileges: { secure: true, standard: true }
}]);

// --------------------Logger setup--------------------
/**
 * Creates a file-based logger with timestamped log files
 * @returns {Function} Log function that writes to file and console
 */
function createLogger() {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const logFilePath = path.join(app.getPath('userData'), 'logs', `${timestamp}.log`);
  const logDir = path.dirname(logFilePath);

  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }

  const logStream = fs.createWriteStream(logFilePath, { flags: 'a' });

  return function log(message) {
    const logMessage = `[${new Date().toISOString()}] ${message}\n`;
    logStream.write(logMessage);
    console.log(message);
  };
}

const log = createLogger();

// --------------------Python process management--------------------
let activePythonProcesses = [];
const pyExe = getEmbeddedPythonExe();
const embedDir = path.dirname(pyExe);

// Verify Python executable exists
//log(`[DEBUG] fs.existsSync(pyExe)= ${fs.existsSync(pyExe)}`);
if (!fs.existsSync(embedDir)) {
  log(`[DEBUG] embedDir DOES NOT EXIST: ${embedDir}`);
}

/**
 * Spawns a Python process with the given script and arguments
 * @param {string} scriptPath - Path to Python script to execute
 * @param {Array} args - Arguments to pass to the script
 * @param {Object} options - Additional spawn options
 * @returns {ChildProcess} The spawned Python process
 */
function spawnLocalPython(scriptPath, args = [], options = {}) {
  const pythonExe = getEmbeddedPythonExe();
  if (!pythonExe || !fs.existsSync(pythonExe)) {
    log(`[ERROR] Python executable not found at: ${pythonExe}`);
    throw new Error(`Python executable not found at: ${pythonExe}`);
  }

  if (!fs.existsSync(scriptPath)) {
    log(`[ERROR] Script path not found: ${scriptPath}`);
    throw new Error(`Script path not found: ${scriptPath}`);
  }

  // Use provided stdio or default to ignoring output
  const stdio = options.stdio || ['ignore', 'ignore', 'ignore'];

  const proc = spawn(pythonExe, [scriptPath, ...args], {
    env: { 
      ...process.env,
      PYTHONPATH: [
        path.join(__dirname, 'python_backend', 'core'),
        path.join(__dirname, 'python_backend', 'python_embedded', 'site-packages')
      ].join(path.delimiter)
    },
    detached: true,
    stdio
  });

  activePythonProcesses.push(proc);

  proc.on('error', err => {
    log(`[ERROR] Python process error: ${err.message}`);
  });

  proc.on('close', code => {
    log(`[DEBUG] Python process exited with code: ${code}`);
    activePythonProcesses = activePythonProcesses.filter(p => p !== proc);
  });

  return proc;
}

// --------------------Window management--------------------
let mainWindow;

/**
 * Gets platform-specific application icon path
 * @returns {string} Path to icon file
 */
function getAppIcon() {
  if (process.platform === 'win32') {
    return path.join(__dirname, 'renderer', 'assets', 'icono_Vicomtech.ico');
  } else if (process.platform === 'darwin') {
    return path.join(__dirname, 'renderer', 'assets', 'icono_Vicomtech.icns');
  }
  return path.join(__dirname, 'renderer', 'assets', 'icono_Vicomtech.png');
}

/**
 * Creates the main application window with security settings
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200, 
    height: 800,
    icon: getAppIcon(),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      sandbox: true
    }
  });

  // Load login page using custom protocol
  mainWindow.loadURL('app://-/views/login.html');
  log('Main window created');

  mainWindow.webContents.on('did-navigate', (event, url) => {
    const rel = url.replace(/^.*app:\/\/-\/views\//, '');
    log(`[USER] entered screen: ${rel}`);
  });

  // Security: Limit navigation to app:// and file:// protocols
  mainWindow.webContents.on('will-navigate', (event, navigationUrl) => {
    const parsed = new URL(navigationUrl);
    if (parsed.protocol !== 'file:' && parsed.protocol !== 'app:') {
      event.preventDefault();
      log(`[SECURITY] Blocked navigation to: ${navigationUrl}`);
    }
  }); 

  // Security: Control window.open behavior
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    const parsed = new URL(url);
    if (parsed.protocol === 'https:' && parsed.host === 'misitio.com') {
      shell.openExternal(url);
    } else {
      log(`[SECURITY] Blocked new-window to: ${url}`);
    }
    return { action: 'deny' };
  });

  mainWindow.on('closed', () => mainWindow = null);
}

// --------------------Application lifecycle--------------------
app.whenReady().then(() => {
  // Set up permission request handler
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
    const origin = new URL(webContents.getURL());
    if (permission === 'notifications') {
      return callback(origin.protocol === 'https:' && origin.host === 'pulpo.com');
    }
    callback(false);
  });

  // Register custom app:// protocol handler
  protocol.registerFileProtocol('app', (request, callback) => {
    const url = new URL(request.url);
    const relPath = url.pathname.replace(/^\/+/, '');
    const filePath = path.join(__dirname, 'renderer', relPath);
    callback({ path: filePath });
  });

  createWindow();
});

// Additional security handlers for all web contents
app.on('web-contents-created', (event, contents) => {
  // Validate webview attachments
  contents.on('will-attach-webview', (event, webPreferences, params) => {
    delete webPreferences.preload;
    webPreferences.nodeIntegration = false;
    webPreferences.contextIsolation = true;
    const allowed = ['file://', 'app://-/', 'https://tudominio.com/'];
    if (!allowed.some(o => params.src.startsWith(o))) {
      event.preventDefault();
      log(`[SECURITY] Blocked will-attach-webview src=${params.src}`);
    }
  });

  // Limit navigation in all web contents
  contents.on('will-navigate', (ev, navigationUrl) => {
    const parsed = new URL(navigationUrl);
    if (parsed.protocol !== 'file:' && parsed.protocol !== 'app:') {
      ev.preventDefault();
      log(`[SECURITY] Blocked navigation to ${navigationUrl}`);
    }
  });

  // Control popup windows
  contents.setWindowOpenHandler(({ url }) => {
    const parsed = new URL(url);
    if (parsed.protocol === 'https:' && parsed.host === 'misitio.com') {
      shell.openExternal(url);
    } else {
      log(`[SECURITY] Blocked new-window to: ${url}`);
    }
    return { action: 'deny' };
  });
});

// Clean up on window close
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    activePythonProcesses.forEach(proc => {
      try { proc.kill(); } 
      catch (e) { log(`[WARN] Could not kill Python process: ${e.message}`); }
    });
    activePythonProcesses = [];
    app.quit();
  }
});

// Recreate window on macOS when dock icon is clicked
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

// --------------------Metrics cache management--------------------
/**
 * Gets path to metrics cache file
 * @returns {string} Path to metrics.json
 */
function getMetricsJsonPath() {
  return path.join(app.getPath('userData'), 'uploads', 'metrics.json');
}

/**
 * Reads metrics cache from file
 * @returns {Object} Cached metrics data
 */
function readMetricsCache() {
  const metricsPath = getMetricsJsonPath();
  if (!fs.existsSync(metricsPath)) return {};

  try {
    return JSON.parse(fs.readFileSync(metricsPath, 'utf-8'));
  } catch (err) {
    log('Error reading metrics.json: ' + err);
    return {};
  }
}

/**
 * Writes metrics to cache file
 * @param {Object} cache - Metrics data to cache
 */
function writeMetricsCache(cache) {
  fs.writeFileSync(getMetricsJsonPath(), JSON.stringify(cache, null, 2), 'utf-8');
}

// --------------------Python script path helpers--------------------
/**
 * Gets path to run_plugins.py script
 * @returns {string} Path to script
 */
function getRunPluginsScriptPath() {
  if (!app.isPackaged) {
    return path.join(__dirname, 'python_backend', 'run_plugins.py');
  }
  return path.join(process.resourcesPath, 'python_backend', 'run_plugins.py');
}

/**
 * Gets path to h5_visualizer.py script
 * @returns {string} Path to script
 */
function getH5VisualizerScriptPath() {
  if (!app.isPackaged) {
    return path.join(__dirname, 'python_backend', 'h5_visualizer.py');
  }
  return path.join(process.resourcesPath, 'python_backend', 'h5_visualizer.py');
}

/**
 * Gets path to npy_npz_visualizer.py script
 * @returns {string} Path to script
 */
function getNpyNpzVisualizerScriptPath() {
  if (!app.isPackaged) {
    return path.join(__dirname, 'python_backend', 'npy_npz_visualizer.py');
  }
  return path.join(process.resourcesPath, 'python_backend', 'npy_npz_visualizer.py');
}

// --------------------Python script execution--------------------
/**
 * Runs a Python script and returns its output
 * @param {string} scriptPath - Path to Python script
 * @param {Array} args - Arguments to pass to script
 * @returns {Promise} Resolves with script output or rejects with error
 */
function runPythonScript(scriptPath, args = []) {
  return new Promise((resolve, reject) => {
    const pythonExe = getEmbeddedPythonExe();
    if (!pythonExe || !fs.existsSync(pythonExe)) {
      return reject(new Error(`Embedded Python exe not found at ${pythonExe}`));
    }

    if (!fs.existsSync(scriptPath)) {
      return reject(new Error(`Script path not found: ${scriptPath}`));
    }

    const pythonProcess = spawn(pythonExe, [scriptPath, ...args]);
    let stdoutData = "";
    let stderrData = "";

    pythonProcess.stdout.on('data', (data) => {
      stdoutData += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      stderrData += data.toString();
      console.error(`[PYTHON STDERR] ${data.toString()}`); 
    });

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        try {
          resolve(JSON.parse(stdoutData));
        } catch (err) {
          reject(new Error('Failed to parse JSON output'));
        }
      } else {
        reject(new Error(stderrData || 'Python script failed with no stderr'));
      }
    });
  });
}

// --------------------IPC handlers--------------------
// Log message from renderer
ipcMain.on('log', (event, message) => {
  log(message);
});

// Start authentication process
ipcMain.on('start-authenticator', (event, userName) => {
  const frameUrl = event.senderFrame?.url || '';
  if (!frameUrl.startsWith('app://-/')) return log('[SECURITY] blocked');
  if (!mainWindow) return log('[ERROR] mainWindow null');

  const scriptsRoot = app.isPackaged
    ? path.join(process.resourcesPath, 'python_backend', 'continuous_authentication')
    : path.join(__dirname, 'python_backend', 'continuous_authentication');
  const collectorPath     = path.join(scriptsRoot, 'data_collector.py');
  const authenticatorPath = path.join(scriptsRoot, 'continuous_authenticator.py');

  // Get window bounds for collector
  const { x, y, width, height } = mainWindow.getContentBounds();

  // Launch data collector
  const dcArgs = [
    '--user',     userName,
    '--width',    width.toString(),
    '--height',   height.toString(),
    '--offset_x', x.toString(),
    '--offset_y', y.toString()
  ];

  try {
    spawnLocalPython(collectorPath, dcArgs).unref();
    log(`data_collector launched for user: ${userName}`);
  } catch (e) {
    log('[ERROR] start collector: ' + e.message);
  }

  // Launch authenticator
  const modelDir = path.join(app.getPath('userData'), 'user_behavior');
  const authArgs = [
    'run',
    '--user',      userName,
    '--load_prefix', 'user_auth',
    '--model_dir',   modelDir,
    '--interval',    '5'
  ];

  try {
    const proc = spawnLocalPython(authenticatorPath, authArgs, {
      stdio: ['ignore', 'pipe', 'ignore']
    });
    proc.stdout.on('data', chunk => {
      if (chunk.toString().trim() === 'ANOMALY_DETECTED') {
        const ts = new Date().toLocaleString('es-ES', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        hour12: false
      });
    log(`ANOMALY DETECTED AT [${ts}]`);
        dialog.showMessageBox(mainWindow, {
          type:    'warning',
          title:   'Authentication Alert',
          message: 'Anomalous behavior detected'
        });
      }
    });
    log('continuous_authenticator launched for user: ' + userName);
  } catch (e) {
    log('[ERROR] start authenticator: ' + e.message);
  }
});

// Show save dialog
ipcMain.handle('show-save-dialog', async (event, options) => {
  const frameUrl = event.senderFrame?.url || '';
  if (!frameUrl.startsWith('app://-/')) {
    log(`[SECURITY] show-save-dialog blocked from ${frameUrl}`);
    return { canceled: true };
  }
  return await dialog.showSaveDialog(mainWindow, options);
});

// Get model summary information
ipcMain.handle('get-h5-visualizer', async (event, modelFilePath) => {
  const frameUrl = event.senderFrame?.url || '';
  if (!frameUrl.startsWith('app://-/')) {
    log(`[SECURITY] get-h5-visualizer blocked from ${frameUrl}`);
    return { success: false, error: 'Forbidden' };
  }
  try {
    const result = await runPythonScript(getH5VisualizerScriptPath(), [modelFilePath]);
    if (result.error) {
      return { success: false, error: result.error };
    }
    if (result.summary) {
      return { success: true, summary: result.summary };
    }
    if (result.structure) {
      return { success: true, summary: JSON.stringify(result.structure, null, 2) };
    }
    return { success: false, error: 'No summary or structure found.' };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

// Get plugin metadata from YAML config
ipcMain.handle('get-plugin-meta', async (event) => {
  const frameUrl = event.senderFrame?.url || '';
  if (!frameUrl.startsWith('app://-/')) {
    log(`[SECURITY] get-plugin-meta blocked from ${frameUrl}`);
    return [];
  }

  const configPath = app.isPackaged
    ? path.join(process.resourcesPath, 'python_backend', 'plugin_config.yaml')
    : path.join(__dirname, 'python_backend', 'plugin_config.yaml');

  if (!fs.existsSync(configPath)) {
    log(`[DEBUG] plugin_config.yaml not found at ${configPath}`);
    return [];
  }

  try {
    const config = yaml.load(fs.readFileSync(configPath, 'utf8'));
    return config.plugins
      .filter(p => p.enabled)
      .map(p => ({ name: p.name,  displayName: p.display_name || p.name, functions: p.functions || [] }));
  } catch (err) {
    log('[ERROR] Reading plugin config: ' + err);
    return [];
  }
});

// Get column headers from CSV file
ipcMain.handle('get-dataset-columns', async (event, datasetFile) => {
  const frameUrl = event.senderFrame?.url || '';
  if (!frameUrl.startsWith('app://-/')) {
    log(`[SECURITY] get-dataset-columns blocked from ${frameUrl}`);
    return { success: false, error: 'Forbidden' };
  }
  try {
    const filePath = path.join(app.getPath('userData'), 'uploads', 'datasets', datasetFile);
    if (path.extname(filePath).toLowerCase() !== '.csv') {
      return { success: false, error: 'Only CSV files supported' };
    }
    const [headerLine] = fs.readFileSync(filePath, 'utf-8').split('\n');
    const columns = headerLine.split(',').map(h => h.trim());
    return { success: true, columns };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

// Handle file upload and metrics calculation
ipcMain.handle('upload-and-calc', async (event, { subfolder, fileType }) => {
  const frameUrl = event.senderFrame?.url || '';
  if (!frameUrl.startsWith('app://-/')) {
    log(`[SECURITY] upload-and-calc blocked from ${frameUrl}`);
    return { success: false, error: 'Forbidden' };
  }
  const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
    title: `Select file (${fileType})`,
    properties: ['openFile']
  });
  if (canceled || !filePaths[0]) {
    return { success: false, error: 'File selection canceled.' };
  }
  try {
    const sourcePath = filePaths[0];
    const fileName = path.basename(sourcePath);
    const destDir = path.join(app.getPath('userData'), 'uploads', subfolder);
    if (!fs.existsSync(destDir)) fs.mkdirSync(destDir, { recursive: true });
    fs.copyFileSync(sourcePath, path.join(destDir, fileName));
    const cache = readMetricsCache();
    if (fileType === 'model') {
      cache[fileName] = cache[fileName] || {};
      cache[fileName]['__DUMMY__'] = {};
    } else {
      Object.keys(cache).forEach(model => {
        cache[model][fileName] = cache[model][fileName] || {};
      });
    }
    writeMetricsCache(cache);
    return { success: true, fileName, fileType };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

// Get list of uploaded files
ipcMain.handle('get-uploaded-files', (event) => {
  const frameUrl = event.senderFrame?.url || '';
  if (!frameUrl.startsWith('app://-/')) {
    log(`[SECURITY] get-uploaded-files blocked from ${frameUrl}`);
    return { datasets: [], models: [] };
  }
  const base = path.join(app.getPath('userData'), 'uploads');
  //log(`[DEBUG] Listing uploads at ${base}`);
  if (!fs.existsSync(base)) log('[DEBUG] uploads folder does not exist');
  
  function listFiles(sub) {
    const dir = path.join(base, sub);
    //log(`[DEBUG] Checking ${dir}`);
    if (!fs.existsSync(dir)) {
      log(`[DEBUG]   ${sub} folder missing`);
      return [];
    }
    return fs.readdirSync(dir, { withFileTypes: true })
             .filter(d => d.isFile())
             .map(d => d.name);
  }
  
  return {
    datasets: listFiles('datasets'),
    models: listFiles('models'),
  };
});

// Delete uploaded file
ipcMain.handle('delete-file', async (event, { fileName, fileType }) => {
  const frameUrl = event.senderFrame?.url || '';
  if (!frameUrl.startsWith('app://-/')) {
    log(`[SECURITY] delete-file blocked from ${frameUrl}`);
    return { success: false, error: 'Forbidden' };
  }
  try {
    const targetDir = path.join(app.getPath('userData'), 'uploads',
      fileType === 'dataset' ? 'datasets' : 'models');
    const filePath = path.join(targetDir, fileName);
    if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
    const metricsCache = readMetricsCache();
    if (fileType === 'dataset') {
      Object.keys(metricsCache).forEach(model => {
        delete metricsCache[model][fileName];
      });
    } else {
      delete metricsCache[fileName];
    }
    writeMetricsCache(metricsCache);
    log(`[USER] deleted file: ${fileName} (type: ${fileType})`);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Get stored metrics for model/dataset combination
ipcMain.handle('get-stored-metrics', (event, { modelFile, datasetFile }) => {
  const frameUrl = event.senderFrame?.url || '';
  if (!frameUrl.startsWith('app://-/')) {
    log(`[SECURITY] get-stored-metrics blocked from ${frameUrl}`);
    return { success: false, error: 'Forbidden' };
  }
  const metricsCache = readMetricsCache();
  const metrics = metricsCache[modelFile]?.[datasetFile] || {};
  return { success: true, metrics };
});

// Get full path to uploaded file
ipcMain.handle('get-file-path', (event, fileName, fileType) => {
  const frameUrl = event.senderFrame?.url || '';
  if (!frameUrl.startsWith('app://-/')) {
    log(`[SECURITY] get-file-path blocked from ${frameUrl}`);
    return { success: false, error: 'Forbidden' };
  }
  try {
    const dir = path.join(app.getPath('userData'), 'uploads',
      fileType === 'dataset' ? 'datasets' : 'models');
    const filePath = path.join(dir, fileName);
    return fs.existsSync(filePath)
      ? { success: true, filePath }
      : { success: false, error: 'File not found' };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Read file content
ipcMain.handle('read-file-content', async (event, filePath) => {
  const frameUrl = event.senderFrame?.url || '';
  if (!frameUrl.startsWith('app://-/')) {
    log(`[SECURITY] read-file-content blocked from ${frameUrl}`);
    return { success: false, error: 'Forbidden' };
  }
  try {
    const content = await fsp.readFile(filePath, 'utf-8');
    return { success: true, fileContent: content };
  } catch (err) {
    log(`[ERROR] read-file-content: ${err.message}`);
    return { success: false, error: err.message };
  }
});

// -------------------- Export metrics to Excel --------------------
ipcMain.handle('export-metrics', async (event, args) => {
  const { modelFile, datasetFile } = args;
  log(`[DEBUG] export-metrics called with args: ${JSON.stringify(args)}`);

  const frameUrl = event.senderFrame?.url || '';
  if (!frameUrl.startsWith('app://-/')) {
    log(`[SECURITY] export-metrics blocked from ${frameUrl}`);
    return { success: false, error: 'Forbidden' };
  }

  try {
    const cache = readMetricsCache();
    const modelCache = cache[modelFile] || {};
    const metricsObj = modelCache[datasetFile];
    if (!metricsObj) {
      return { success: false, error: 'No metrics found for that model/dataset' };
    }

    // If the cache is wrapped in the plugin key (like neuralstrength_lite_evaluator), we step down one level:
    const pluginKey = Object.keys(metricsObj).find(k => k === 'neuralstrength_lite_evaluator');
    const payload = pluginKey ? metricsObj[pluginKey] : metricsObj;

    // We build rows: one entry per engine
    const rows = [];
    for (const [engineName, pd] of Object.entries(payload)) {
      if (pd.metrics) {
        rows.push({ Engine: engineName, ...pd.metrics });
      }
    }
    if (rows.length === 0) {
      return { success: false, error: 'No engine-level metrics to export' };
    }

    // Creating the Excel file
    const workbook = XLSX.utils.book_new();
    const ws = XLSX.utils.json_to_sheet(rows);
    XLSX.utils.book_append_sheet(workbook, ws, 'Metrics');

    const { canceled, filePath } = await dialog.showSaveDialog(mainWindow, {
      title: 'Save Metrics as Excel',
      defaultPath: `${modelFile}-${datasetFile}-metrics.xlsx`,
      filters: [{ name: 'Excel Files', extensions: ['xlsx'] }]
    });
    if (canceled || !filePath) {
      return { success: false, error: 'Save canceled', filePath: null };
    }

    XLSX.writeFile(workbook, filePath);
    return { success: true, filePath };
  } catch (error) {
    log(`[ERROR] export-metrics: ${error.message}`);
    return { success: false, error: error.message };
  }
});

// -------------------- Export metrics to CSV --------------------
ipcMain.handle('export-csv', async (event, args) => {
  const { modelFile, datasetFile } = args;
  log(`[DEBUG] export-csv called with args: ${JSON.stringify(args)}`);

  const frameUrl = event.senderFrame?.url || '';
  if (!frameUrl.startsWith('app://-/')) {
    log(`[SECURITY] export-csv blocked from ${frameUrl}`);
    return { success: false, error: 'Forbidden' };
  }

  try {
    const cache = readMetricsCache();
    const modelCache = cache[modelFile] || {};
    const metricsObj = modelCache[datasetFile];
    if (!metricsObj) {
      return { success: false, error: 'No metrics found for that model/dataset' };
    }

    // Same: we step down one level if it is wrapped by the plugin name
    const pluginKey = Object.keys(metricsObj).find(k => k === 'neuralstrength_lite_evaluator');
    const payload = pluginKey ? metricsObj[pluginKey] : metricsObj;

    const rows = [];
    for (const [engineName, pd] of Object.entries(payload)) {
      if (pd.metrics) {
        rows.push({ Engine: engineName, ...pd.metrics });
      }
    }
    if (rows.length === 0) {
      return { success: false, error: 'No engine-level metrics to export' };
    }

    const ws = XLSX.utils.json_to_sheet(rows);
    const csv = XLSX.utils.sheet_to_csv(ws);

    const { canceled, filePath } = await dialog.showSaveDialog(mainWindow, {
      title: 'Save Metrics as CSV',
      defaultPath: `${modelFile}-${datasetFile}-metrics.csv`,
      filters: [{ name: 'CSV Files', extensions: ['csv'] }]
    });
    if (canceled || !filePath) {
      return { success: false, error: 'Save canceled', filePath: null };
    }

    await fsp.writeFile(filePath, csv, 'utf-8');
    return { success: true, filePath };
  } catch (error) {
    log(`[ERROR] export-csv: ${error.message}`);
    return { success: false, error: error.message };
  }
});


// Get preview of NPY file contents
ipcMain.handle('get-npy-npz-visualizer', async (event, filePath) => {
  const frameUrl = event.senderFrame?.url || '';
  if (!frameUrl.startsWith('app://-/')) {
    log(`[SECURITY] get-npy-npz-visualizer blocked from ${frameUrl}`);
    return { success: false, error: 'Forbidden' };
  }
  try {
    const result = await runPythonScript(getNpyNpzVisualizerScriptPath(), [filePath]);
    if (result.error) return { success: false, error: result.error };
    return { success: true, htmlPreview: result.html || 'No preview generated.' };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

// Compute metrics for model/dataset combination, with cache support
ipcMain.handle('compute-combo-metrics', async (event, {
  modelFile,
  datasetFile,
  labelColumn,
  protectedColumn
}) => {
  const frameUrl = event.senderFrame?.url || '';
  if (!frameUrl.startsWith('app://-/')) {
    log(`[SECURITY] compute-combo-metrics blocked from ${frameUrl}`);
    return { success: false, error: 'Forbidden' };
  }

  try {
    // 1) Read cache
    const cache = readMetricsCache();
    const modelCache = cache[modelFile] || {};

    // 2) Only use cache if it's non-empty AND not a dummy-model run
    if (modelFile !== '__DUMMY__') {
      const cached = modelCache[datasetFile];
      if (cached && Object.keys(cached).length > 0) {
        log(`[DEBUG] Using cached metrics for ${modelFile} + ${datasetFile}`);
        return { success: true, metrics: cached };
      }
    }

    // 3) Build Python arguments
    const args = [
      '--model',
      path.join(app.getPath('userData'), 'uploads', 'models', modelFile)
    ];
    if (datasetFile === '__DUMMY__') {
      args.push('--use-dummy');
    } else {
      args.push(
        '--dataset',
        path.join(app.getPath('userData'), 'uploads', 'datasets', datasetFile)
      );
    }
    if (labelColumn)     args.push('--label-column', labelColumn);
    if (protectedColumn) args.push('--protected-column', protectedColumn);

    // 4) Run Python plugins
    const output = await runPythonScript(getRunPluginsScriptPath(), args);
    const metrics = typeof output === 'string' ? JSON.parse(output) : output;

    // 5) Store in cache
    cache[modelFile] = modelCache;
    cache[modelFile][datasetFile] = metrics;
    writeMetricsCache(cache);

    return { success: true, metrics };

  } catch (err) {
    log(`[ERROR] compute-combo-metrics: ${err.message}`);
    return { success: false, error: err.message };
  }
});


// --------------------Embedded python helper--------------------
/**
 * Locates the embedded Python executable
 * @returns {string} Path to Python executable
 * @throws {Error} If Python executable not found
 */
function getEmbeddedPythonExe() {
  const rel = path.join('python_backend', 'python_embedded', 'python.exe');

  if (!app.isPackaged) {
    return path.join(__dirname, rel);
  }

  const exePath = path.join(process.resourcesPath, rel);
  if (!fs.existsSync(exePath)) {
    log(`[ERROR] python.exe no encontrado en: ${exePath}`);
    throw new Error(`python.exe no encontrado en: ${exePath}`);
  }
  return exePath;
}

// --------------------Plugin visualization handler--------------------
ipcMain.handle('get-tab-html', async (event, pluginName, metrics) => {
  const frameUrl = event.senderFrame?.url || '';
  if (!frameUrl.startsWith('app://-/')) {
    log(`[SECURITY] get-tab-html blocked from ${frameUrl}`);
    return '<div class="alert alert-danger">Forbidden</div>';
  }

  try {
    const relViz = path.join('python_backend', 'plugins', pluginName, 'visualizer.py');
    const visualizer = path.join(
    app.isPackaged ? process.resourcesPath : __dirname,
    relViz
   );
    const pyExe = getEmbeddedPythonExe();
    //log(`[${pluginName}] lanzando visualizer: ${pyExe} ${visualizer}`);

    const cwd = path.dirname(pyExe);

    return await new Promise(resolve => {
      const child = spawn(pyExe, [visualizer, JSON.stringify(metrics || {})], {
        cwd,
        env: { ...process.env, PYTHONUNBUFFERED: '1' }
      });

      let stdout = '', stderr = '';
      child.stdout.on('data', data => { stdout += data.toString(); });
      child.stderr.on('data', data => { stderr += data.toString(); });

      child.on('close', code => {
        if (code === 0) {
          resolve(stdout || '<div>No output</div>');
        } else {
          log(`[${pluginName}] visualizer exited ${code} with stderr:\n${stderr}`);
          resolve(`<div class="alert alert-danger">${escapeHtml(stderr || 'Error del visualizador')}</div>`);
        }
      });

      child.on('error', err => {
        log(`[${pluginName}] error al lanzar el visualizer: ${err.message}`);
        resolve(`<div class="alert alert-danger">Error al lanzar el visualizador: ${escapeHtml(err.message)}</div>`);
      });
    });
  } catch (e) {
    log(`[${pluginName}] EXCEPCIÓN: ${e.message}`);
    return `<div class="alert alert-danger">Visualizer error: ${escapeHtml(e.message)}</div>`;
  }
});

// Get preview of CSV file contents
ipcMain.handle('get-csv-preview', async (event, filePath) => {
  const frameUrl = event.senderFrame?.url || '';
  if (!frameUrl.startsWith('app://-/')) {
    log(`[SECURITY] get-csv-preview blocked from ${frameUrl}`);
    return { success: false, error: 'Forbidden' };
  }
  try {
    const raw = await fsp.readFile(filePath, 'utf-8');
    const lines = raw.split(/\r?\n/).slice(0, 100);
    return { success: true, preview: lines.join('\n') };
  } catch (err) {
    log(`[ERROR] get-csv-preview: ${err.message}`);
    return { success: false, error: err.message };
  }
});

// Validate credentials against SQLite
ipcMain.handle('validate-user', async (event, { username, password }) => {
  return new Promise(resolve => {
    getUserByUsername(username, (err, row) => {
      if (err || !row) return resolve(false);
      resolve(bcrypt.compareSync(password, row.password));
    });
  });
});

// Start second-factor authenticator
ipcMain.on('start-auth', (event, username) => {
  console.log(`Starting authenticator for ${username}`);
});


// main.js (append this at the end of the file)
module.exports = {
  // Utility
  escapeHtml,
  createLogger,

  // Python process
  spawnLocalPython,
  runPythonScript,

  // Path helpers
  getRunPluginsScriptPath,
  getH5VisualizerScriptPath,
  getNpyNpzVisualizerScriptPath,
  getEmbeddedPythonExe,

  // App helpers
  getAppIcon,

  // Metrics cache
  getMetricsJsonPath,
  readMetricsCache,
  writeMetricsCache,
};