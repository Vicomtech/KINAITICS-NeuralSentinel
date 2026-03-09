const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

// Python backend configuration
const PYTHON_PORT = 5000;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        title: 'NeuralSentinel',
        minWidth: 1200,
        minHeight: 700,
        backgroundColor: '#f3f4f6',
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: path.join(__dirname, 'assets', 'icon.png')
    });

    mainWindow.loadFile('index.html');

    // Open DevTools in development mode
    // if (process.argv.includes('--dev')) {
    //     mainWindow.webContents.openDevTools();
    // }

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

function startPythonBackend() {
    // In development, assume Python backend runs separately
    // In production, spawn bundled Python executable
    const isDev = process.argv.includes('--dev');

    if (isDev) {
        console.log('Development mode: Python backend should be started manually');
        console.log('Run: cd backend && python app.py');
        return;
    }

    // Production: spawn bundled Python backend
    const pythonPath = path.join(
        process.resourcesPath,
        'backend',
        process.platform === 'win32' ? 'app.exe' : 'app'
    );

    pythonProcess = spawn(pythonPath, [], {
        stdio: 'inherit'
    });

    pythonProcess.on('error', (err) => {
        console.error('Failed to start Python backend:', err);
    });

    pythonProcess.on('exit', (code) => {
        console.log(`Python backend exited with code ${code}`);
    });
}

function stopPythonBackend() {
    if (pythonProcess) {
        pythonProcess.kill();
        pythonProcess = null;
    }
}

// App lifecycle
app.whenReady().then(() => {
    startPythonBackend();

    // Give backend time to start
    setTimeout(() => {
        createWindow();
    }, 2000);

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        stopPythonBackend();
        app.quit();
    }
});

app.on('will-quit', () => {
    stopPythonBackend();
});

// IPC handlers
ipcMain.handle('get-backend-url', () => {
    return `http://localhost:${PYTHON_PORT}`;
});

ipcMain.handle('app-version', () => {
    return app.getVersion();
});
