jest.mock('electron');

const path = require('path');
const { getAppIcon } = require('../main');

describe('getAppIcon()', () => {
  const originalPlatform = process.platform;

  afterEach(() => {
    Object.defineProperty(process, 'platform', {
      value: originalPlatform
    });
  });

  it('returns .ico path on Windows', () => {
    Object.defineProperty(process, 'platform', {
      value: 'win32'
    });
    expect(getAppIcon()).toMatch(/icono_Vicomtech\.ico$/);
  });

  it('returns .icns path on macOS', () => {
    Object.defineProperty(process, 'platform', {
      value: 'darwin'
    });
    expect(getAppIcon()).toMatch(/icono_Vicomtech\.icns$/);
  });

  it('returns .png path on other platforms', () => {
    Object.defineProperty(process, 'platform', {
      value: 'linux'
    });
    expect(getAppIcon()).toMatch(/icono_Vicomtech\.png$/);
  });
});