module.exports = {
  app: {
    isPackaged: false,
    whenReady: jest.fn(() => Promise.resolve()),
    getPath: jest.fn((name) => {
      if (name === 'userData') return '/tmp/userData';
      return `/tmp/${name}`;
    }),
    on: jest.fn(),
    resourcesPath: '/fake/resources',
    quit: jest.fn(),
    exit: jest.fn()
  },
  BrowserWindow: jest.fn().mockImplementation(() => ({
    loadURL: jest.fn(),
    webContents: {
      on: jest.fn(),
      setWindowOpenHandler: jest.fn(),
      getURL: jest.fn(() => 'app://-/'),
      session: {
        webRequest: {
          onHeadersReceived: jest.fn()
        }
      }
    },
    on: jest.fn(),
    close: jest.fn(),
    destroy: jest.fn(),
    isDestroyed: jest.fn(() => false)
  })),
  ipcMain: {
    on: jest.fn(),
    handle: jest.fn(),
    removeHandler: jest.fn()
  },
  dialog: {
    showSaveDialog: jest.fn(),
    showMessageBox: jest.fn(),
    showErrorBox: jest.fn()
  },
  session: {
    defaultSession: {
      setPermissionRequestHandler: jest.fn(),
      webRequest: {
        onHeadersReceived: jest.fn()
      }
    }
  },
  shell: {
    openExternal: jest.fn()
  },
  protocol: {
    registerSchemesAsPrivileged: jest.fn(),
    registerFileProtocol: jest.fn(),
    interceptFileProtocol: jest.fn()
  },
  net: {
    request: jest.fn()
  }
};