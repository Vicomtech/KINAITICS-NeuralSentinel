jest.mock('electron');
jest.mock('python-shell');
jest.mock('child_process', () => ({
  spawn: jest.fn()
}));

const fs = require('fs');
const childProcess = require('child_process');
const path = require('path');
const { runPythonScript } = require('../main');

describe('runPythonScript()', () => {
  const fakeExe = path.join(__dirname, '..', 'python_backend', 'python_embedded', 'python.exe');
  const fakeScript = path.join(__dirname, 'fake-script.py');

  beforeEach(() => {
    jest.spyOn(require('../main'), 'getEmbeddedPythonExe').mockReturnValue(fakeExe);
    jest.spyOn(fs, 'existsSync').mockImplementation(p => {
      return p === fakeExe || p === fakeScript;
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('resolves with parsed JSON on success', async () => {
    const fakeProc = {
      stdout: { on: jest.fn((evt, cb) => evt === 'data' && cb(Buffer.from('{"ok":true}'))) },
      stderr: { on: jest.fn() },
      on: jest.fn((evt, cb) => evt === 'close' && cb(0))
    };
    childProcess.spawn.mockReturnValue(fakeProc);

    await expect(runPythonScript(fakeScript)).resolves.toEqual({ ok: true });
  });

  it('rejects with stderr on non-zero exit', async () => {
    const fakeProc = {
      stdout: { on: jest.fn() },
      stderr: { on: jest.fn((evt, cb) => evt === 'data' && cb(Buffer.from('error!'))) },
      on: jest.fn((evt, cb) => evt === 'close' && cb(1))
    };
    childProcess.spawn.mockReturnValue(fakeProc);

    await expect(runPythonScript(fakeScript)).rejects.toThrow('error!');
  });

  it('rejects if JSON parsing fails', async () => {
    const fakeProc = {
      stdout: { on: jest.fn((evt, cb) => evt === 'data' && cb(Buffer.from('invalid json'))) },
      stderr: { on: jest.fn() },
      on: jest.fn((evt, cb) => evt === 'close' && cb(0))
    };
    childProcess.spawn.mockReturnValue(fakeProc);

    await expect(runPythonScript(fakeScript)).rejects.toThrow('Failed to parse JSON output');
  });
});