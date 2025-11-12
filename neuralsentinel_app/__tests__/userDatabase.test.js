jest.mock('electron', () => ({
  app: {
    getPath: () => __dirname
  }
}));

const path = require('path');
const { getUserByUsername } = require(
  path.join(__dirname, '..', 'python_backend', 'userDatabase', 'userDatabase.js')
);

describe('userDatabase', () => {
  it('returns an existing user with bcrypt-hashed password', done => {
    getUserByUsername('user1', (err, row) => {
      expect(err).toBeNull();
      expect(row).toBeDefined();
      expect(row.username).toBe('user1');
      expect(row.password).toMatch(/^\$2[aby]\$.{56}$/);
      done();
    });
  });

  it('returns undefined for non-existent user', done => {
    getUserByUsername('nonexistent', (err, row) => {
      expect(err).toBeNull();
      expect(row).toBeUndefined();
      done();
    });
  });
});