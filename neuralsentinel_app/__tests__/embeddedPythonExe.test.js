jest.mock('electron');

const fs = require('fs');
const path = require('path');
const { getEmbeddedPythonExe } = require('../main');

describe('getEmbeddedPythonExe()', () => {
  const relPath = path.join('python_backend', 'python_embedded', 'python.exe');
  const devPath = path.join(__dirname, '..', relPath);
  const packagedPath = path.join(process.resourcesPath || '/fake/resources', relPath);
  let mockExistsSync;

  beforeEach(() => {
    mockExistsSync = jest.spyOn(fs, 'existsSync').mockReturnValue(true);
    require('electron').app.isPackaged = false;
    process.resourcesPath = '/fake/resources';
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('returns correct path in development mode', () => {
    require('electron').app.isPackaged = false;
    expect(getEmbeddedPythonExe()).toBe(devPath);
  });

  it('returns correct path in packaged mode', () => {
    require('electron').app.isPackaged = true;
    expect(getEmbeddedPythonExe()).toBe(packagedPath);
  });

  it('throws if python.exe not found', () => {
    require('electron').app.isPackaged = true;
    mockExistsSync.mockImplementation((p) => {
      return p === devPath;
    });
    
    expect(() => getEmbeddedPythonExe()).toThrow(/python\.exe no encontrado en/);
  });
});