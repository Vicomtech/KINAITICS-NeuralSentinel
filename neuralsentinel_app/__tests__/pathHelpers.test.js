jest.mock('electron');

const path = require('path');
const {
  getRunPluginsScriptPath,
  getH5VisualizerScriptPath,
  getNpyNpzVisualizerScriptPath
} = require('../main');

describe('Path Helpers', () => {
  beforeEach(() => {
    require('electron').app.isPackaged = false;
    process.resourcesPath = '/fake/resources';
  });

  describe('Development mode', () => {
    it('returns correct path for run_plugins.py', () => {
      const expected = path.join(__dirname, '..', 'python_backend', 'run_plugins.py');
      expect(getRunPluginsScriptPath()).toBe(expected);
    });

    it('returns correct path for h5_visualizer.py', () => {
      const expected = path.join(__dirname, '..', 'python_backend', 'h5_visualizer.py');
      expect(getH5VisualizerScriptPath()).toBe(expected);
    });

    it('returns correct path for npy_npz_visualizer.py', () => {
      const expected = path.join(__dirname, '..', 'python_backend', 'npy_npz_visualizer.py');
      expect(getNpyNpzVisualizerScriptPath()).toBe(expected);
    });
  });

  describe('Packaged mode', () => {
    beforeEach(() => {
      require('electron').app.isPackaged = true;
    });

    it('returns correct packaged path for run_plugins.py', () => {
      const expected = path.join('/fake/resources', 'python_backend', 'run_plugins.py');
      expect(getRunPluginsScriptPath()).toBe(expected);
    });

    it('returns correct packaged path for h5_visualizer.py', () => {
      const expected = path.join('/fake/resources', 'python_backend', 'h5_visualizer.py');
      expect(getH5VisualizerScriptPath()).toBe(expected);
    });

    it('returns correct packaged path for npy_npz_visualizer.py', () => {
      const expected = path.join('/fake/resources', 'python_backend', 'npy_npz_visualizer.py');
      expect(getNpyNpzVisualizerScriptPath()).toBe(expected);
    });
  });
});