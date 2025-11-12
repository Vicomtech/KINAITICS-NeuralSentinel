jest.mock('electron');

const fs = require('fs');
const path = require('path');
const { createLogger } = require('../main');

describe('createLogger()', () => {
  const tempDir = path.join(__dirname, 'temp-userdata-test');
  const logsDir = path.join(tempDir, 'logs');
  let logStreamWrite;

  beforeAll(() => {
    // Guardar referencia original
    logStreamWrite = fs.WriteStream.prototype.write;
  });

  beforeEach(() => {
    // Configurar mocks
    require('electron').app.getPath.mockImplementation((name) => {
      return name === 'userData' ? tempDir : `/tmp/${name}`;
    });

    // Limpiar directorio completamente
    if (fs.existsSync(tempDir)) {
      fs.rmSync(tempDir, { recursive: true, force: true, maxRetries: 3, retryDelay: 100 });
    }
    fs.mkdirSync(tempDir, { recursive: true });

    // Mockear console.log
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(async () => {
    // Cerrar todos los streams de archivo
    await new Promise(resolve => setTimeout(resolve, 50));
    
    // Limpiar directorio con más tolerancia a errores
    try {
      if (fs.existsSync(tempDir)) {
        fs.rmSync(tempDir, { recursive: true, force: true, maxRetries: 3, retryDelay: 100 });
      }
    } catch (err) {
      console.warn('Cleanup warning:', err.message);
    }
    
    jest.restoreAllMocks();
  });

  afterAll(() => {
    // Restaurar implementación original
    fs.WriteStream.prototype.write = logStreamWrite;
  });

  it('creates log file and writes to console', (done) => {
    // Monkey patch para detectar cuando se ha escrito
    fs.WriteStream.prototype.write = function(chunk, encoding, callback) {
      logStreamWrite.call(this, chunk, encoding, () => {
        try {
          const logFiles = fs.readdirSync(logsDir);
          expect(logFiles.length).toBe(1);
          
          const logContent = fs.readFileSync(
            path.join(logsDir, logFiles[0]), 
            'utf8'
          );
          expect(logContent).toContain('test message');
          expect(console.log).toHaveBeenCalledWith('test message');
          done();
        } catch (err) {
          done(err);
        } finally {
          fs.WriteStream.prototype.write = logStreamWrite;
        }
      });
    };

    const log = createLogger();
    log('test message');
  });
});