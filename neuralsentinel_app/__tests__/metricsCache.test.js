jest.mock('electron');

const fs = require('fs');
const path = require('path');
const { readMetricsCache, writeMetricsCache } = require('../main');

describe('Metrics Cache', () => {
  const tempDir = path.join(__dirname, 'temp-userdata');
  const uploadsDir = path.join(tempDir, 'uploads');
  const metricsPath = path.join(uploadsDir, 'metrics.json');

  beforeEach(() => {
    require('electron').app.getPath.mockImplementation((name) => {
      return name === 'userData' ? tempDir : `/tmp/${name}`;
    });

    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }
  });

  afterEach(() => {
    if (fs.existsSync(tempDir)) {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  });

  it('returns empty object when file does not exist', () => {
    expect(readMetricsCache()).toEqual({});
  });

  it('writes and reads back the same data', () => {
    if (!fs.existsSync(uploadsDir)) {
      fs.mkdirSync(uploadsDir, { recursive: true });
    }

    const testData = { metric1: 123, metric2: 'test' };
    writeMetricsCache(testData);
    expect(readMetricsCache()).toEqual(testData);
  });

  it('returns empty object when file contains invalid JSON', () => {
    if (!fs.existsSync(uploadsDir)) {
      fs.mkdirSync(uploadsDir, { recursive: true });
    }

    fs.writeFileSync(metricsPath, 'invalid json');
    expect(readMetricsCache()).toEqual({});
  });
});