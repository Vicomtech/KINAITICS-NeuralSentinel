jest.mock('electron');
jest.mock('python-shell');
jest.mock('child_process', () => ({
  spawn: jest.fn()
}));

const fs = require('fs');
const path = require('path');
const { spawnLocalPython } = require('../main');

describe('spawnLocalPython()', () => {
  const fakeExe = path.join(__dirname, '..', 'python_backend', 'python_embedded', 'python.exe');
  const fakeScript = path.join(__dirname, 'fake-script.py');

  beforeEach(() => {
    jest.spyOn(fs, 'existsSync').mockImplementation(p => {
      return p === fakeExe || p === fakeScript;
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('throws if python executable not found', () => {
    fs.existsSync.mockImplementation(() => false);
    expect(() => spawnLocalPython(fakeScript))
      .toThrow(`Python executable not found at: ${fakeExe}`);
  });

  it('throws if script path not found', () => {
    fs.existsSync.mockImplementation(p => p === fakeExe);
    expect(() => spawnLocalPython(fakeScript))
      .toThrow(`Script path not found: ${fakeScript}`);
  });

  it('returns a ChildProcess when both exist', () => {
    const fakeProc = { on: jest.fn(), unref: jest.fn() };
    require('child_process').spawn.mockReturnValue(fakeProc);

    const proc = spawnLocalPython(fakeScript, ['arg1'], { stdio: ['ignore'] });
    expect(proc).toBe(fakeProc);
    expect(require('child_process').spawn).toHaveBeenCalledWith(
      fakeExe,
      [fakeScript, 'arg1'],
      expect.objectContaining({ stdio: ['ignore'] })
    );
  });
});